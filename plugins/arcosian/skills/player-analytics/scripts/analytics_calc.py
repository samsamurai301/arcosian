#!/usr/bin/env python3
"""analytics_calc.py - player-analytics calculators (stdlib only, Python 3.9+).

Complements the plugin-level tools (ab_test.py, retention_ltv.py,
difficulty_curve.py, event_taxonomy.py) with the everyday analyst maths:

  kpis     derived KPIs from daily aggregates (stickiness, ARPDAU, ARPPU,
           conversion, ad ARPDAU, eCPM, CPI, K-factor, viral multiplier)
  ci       Wilson confidence interval for a rate (retention, conversion)
  funnel   step conversion, drop-off and the biggest leak
  cohort   classic or rolling retention triangle from a user-activity CSV
  economy  source/sink ratios, top faucets/drains, balance percentiles,
           hoarding (days of spending stored)
  rfm      recency/frequency/monetary scoring and segment labels
  payback  retention-curve fit -> cumulative ARPU, ROAS by day, payback day
  srm      sample-ratio-mismatch chi-square check for experiments

Exit codes: 0 ok, 1 check failed (srm mismatch, economy out of band with
--strict, no payback with --strict), 2 usage or input error.
Run with --selftest to exercise every calculator on built-in fixtures.
"""
from __future__ import annotations

import argparse
import csv
import datetime as _dt
import io
import json
import math
import sys
from typing import Callable, Dict, List, Optional, Sequence, Tuple


class InputError(Exception):
    """Bad user input (exit code 2)."""


# --------------------------------------------------------------------------
# statistics helpers
# --------------------------------------------------------------------------

def norm_cdf(z: float) -> float:
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def norm_ppf(p: float) -> float:
    """Inverse standard normal CDF by bisection (accurate to ~1e-10)."""
    if not 0.0 < p < 1.0:
        raise InputError("probability must be in (0, 1)")
    lo, hi = -40.0, 40.0
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if norm_cdf(mid) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def wilson(success: float, n: float, confidence: float = 0.95) -> Tuple[float, float, float]:
    """Wilson score interval. Returns (rate, low, high)."""
    if n <= 0:
        raise InputError("n must be > 0")
    if success < 0 or success > n:
        raise InputError("success must be between 0 and n")
    p = success / n
    z = norm_ppf(1.0 - (1.0 - confidence) / 2.0)
    z2 = z * z
    denom = 1.0 + z2 / n
    centre = (p + z2 / (2.0 * n)) / denom
    half = z * math.sqrt(p * (1.0 - p) / n + z2 / (4.0 * n * n)) / denom
    return p, max(0.0, centre - half), min(1.0, centre + half)


def _gammaln(x: float) -> float:
    return math.lgamma(x)


def _gamma_p_series(s: float, x: float) -> float:
    total = 1.0 / s
    term = total
    a = s
    for _ in range(1000):
        a += 1.0
        term *= x / a
        total += term
        if abs(term) < abs(total) * 1e-15:
            break
    return total * math.exp(-x + s * math.log(x) - _gammaln(s))


def _gamma_q_cf(s: float, x: float) -> float:
    # Lentz continued fraction for the upper regularized gamma
    tiny = 1e-300
    b = x + 1.0 - s
    c = 1.0 / tiny
    d = 1.0 / b
    h = d
    for i in range(1, 1000):
        an = -i * (i - s)
        b += 2.0
        d = an * d + b
        if abs(d) < tiny:
            d = tiny
        c = b + an / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-15:
            break
    return math.exp(-x + s * math.log(x) - _gammaln(s)) * h


def chi2_sf(x: float, df: int) -> float:
    """Survival function of the chi-square distribution."""
    if df < 1:
        raise InputError("df must be >= 1")
    if x <= 0:
        return 1.0
    s = df / 2.0
    hx = x / 2.0
    if hx < s + 1.0:
        return max(0.0, 1.0 - _gamma_p_series(s, hx))
    return min(1.0, _gamma_q_cf(s, hx))


def percentile(values: Sequence[float], q: float) -> float:
    """Linear-interpolated percentile, q in [0, 100]."""
    if not values:
        raise InputError("no values for percentile")
    xs = sorted(values)
    if len(xs) == 1:
        return float(xs[0])
    pos = (len(xs) - 1) * q / 100.0
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    frac = pos - lo
    return float(xs[lo] + (xs[hi] - xs[lo]) * frac)


# --------------------------------------------------------------------------
# parsing helpers
# --------------------------------------------------------------------------

def parse_points(text: str) -> List[Tuple[float, float]]:
    """'1:0.42,7:0.18,30:0.07' -> [(1, 0.42), ...]"""
    pts: List[Tuple[float, float]] = []
    for chunk in text.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if ":" not in chunk:
            raise InputError(f"bad point '{chunk}', expected day:rate")
        d, r = chunk.split(":", 1)
        try:
            day, rate = float(d), float(r)
        except ValueError:
            raise InputError(f"bad point '{chunk}'")
        if day <= 0 or not 0 < rate <= 1:
            raise InputError(f"point '{chunk}': day must be > 0 and 0 < rate <= 1")
        pts.append((day, rate))
    if len(pts) < 2:
        raise InputError("need at least two day:rate points")
    return sorted(pts)


def parse_steps(text: str) -> List[Tuple[str, float]]:
    steps: List[Tuple[str, float]] = []
    for chunk in text.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if ":" not in chunk:
            raise InputError(f"bad step '{chunk}', expected name:count")
        name, cnt = chunk.rsplit(":", 1)
        try:
            value = float(cnt)
        except ValueError:
            raise InputError(f"bad count in '{chunk}'")
        if value < 0:
            raise InputError("counts must be >= 0")
        steps.append((name.strip(), value))
    if len(steps) < 2:
        raise InputError("need at least two funnel steps")
    return steps


def read_csv_rows(path_or_text: str, required: Sequence[str], is_text: bool = False) -> List[Dict[str, str]]:
    try:
        if is_text:
            handle = io.StringIO(path_or_text)
        else:
            handle = open(path_or_text, newline="", encoding="utf-8")
    except OSError as exc:
        raise InputError(f"cannot open {path_or_text}: {exc}")
    with handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise InputError("empty CSV")
        fields = [f.strip() for f in reader.fieldnames]
        missing = [c for c in required if c not in fields]
        if missing:
            raise InputError(f"CSV missing columns: {', '.join(missing)} (has {', '.join(fields)})")
        rows = []
        for raw in reader:
            rows.append({(k or "").strip(): (v or "").strip() for k, v in raw.items()})
    if not rows:
        raise InputError("CSV has no data rows")
    return rows


def parse_date(text: str) -> _dt.date:
    try:
        return _dt.date.fromisoformat(text[:10])
    except ValueError:
        raise InputError(f"bad date '{text}', expected YYYY-MM-DD")


def fnum(text: str, field: str) -> float:
    try:
        return float(text)
    except ValueError:
        raise InputError(f"bad number '{text}' in column {field}")


# --------------------------------------------------------------------------
# calculators
# --------------------------------------------------------------------------

def calc_kpis(a: Dict[str, Optional[float]]) -> Dict[str, object]:
    out: Dict[str, object] = {}

    def g(key: str) -> Optional[float]:
        v = a.get(key)
        return None if v is None else float(v)

    dau, mau, wau = g("dau"), g("mau"), g("wau")
    iap, ads, revenue = g("iap_revenue"), g("ad_revenue"), g("revenue")
    if revenue is None and (iap is not None or ads is not None):
        revenue = (iap or 0.0) + (ads or 0.0)
    payers, installs, spend = g("payers"), g("installs"), g("spend")
    impressions, sessions, playtime = g("impressions"), g("sessions"), g("playtime_min")
    ipu, iconv = g("invites_per_user"), g("invite_conversion")

    def ratio(num: Optional[float], den: Optional[float]) -> Optional[float]:
        if num is None or den is None or den == 0:
            return None
        return num / den

    if dau is not None and mau is not None:
        if dau > mau:
            raise InputError("dau cannot exceed mau")
        out["stickiness_dau_mau"] = ratio(dau, mau)
    if dau is not None and wau is not None:
        out["stickiness_dau_wau"] = ratio(dau, wau)
    if revenue is not None:
        out["revenue"] = revenue
        out["arpdau"] = ratio(revenue, dau)
    if iap is not None:
        out["iap_arpdau"] = ratio(iap, dau)
    if ads is not None:
        out["ad_arpdau"] = ratio(ads, dau)
        out["ecpm"] = None if impressions in (None, 0) else ads / impressions * 1000.0
    if impressions is not None:
        out["impressions_per_dau"] = ratio(impressions, dau)
    if payers is not None:
        out["payer_conversion_daily"] = ratio(payers, dau)
        if iap is not None:
            out["arppu_iap"] = ratio(iap, payers)
        elif revenue is not None:
            out["arppu"] = ratio(revenue, payers)
    if sessions is not None:
        out["sessions_per_dau"] = ratio(sessions, dau)
        if playtime is not None:
            out["avg_session_min"] = ratio(playtime, sessions)
    if playtime is not None:
        out["playtime_min_per_dau"] = ratio(playtime, dau)
    if spend is not None:
        out["cpi"] = ratio(spend, installs)
    if ipu is not None and iconv is not None:
        k = ipu * iconv
        out["k_factor"] = k
        out["viral_multiplier"] = (1.0 / (1.0 - k)) if k < 1 else None
        out["viral_note"] = "k >= 1: exponential growth in theory; check for saturation" if k >= 1 else "total users per seeded user = 1/(1-k)"
    return {k: (round(v, 6) if isinstance(v, float) else v) for k, v in out.items()}


def calc_funnel(steps: List[Tuple[str, float]]) -> Dict[str, object]:
    start = steps[0][1]
    if start <= 0:
        raise InputError("first step count must be > 0")
    rows = []
    total_loss = max(0.0, start - steps[-1][1])
    warnings = []
    biggest = None
    for i, (name, cnt) in enumerate(steps):
        prev = steps[i - 1][1] if i else cnt
        drop = prev - cnt if i else 0.0
        if drop < 0:
            warnings.append(f"step '{name}' is larger than the previous step: open funnel or mismatched definitions")
        row = {
            "step": name,
            "count": cnt,
            "conv_from_prev": None if i == 0 else (cnt / prev if prev else None),
            "conv_from_start": cnt / start,
            "drop_abs": drop,
            "share_of_total_loss": (drop / total_loss) if (i and total_loss > 0 and drop > 0) else 0.0,
        }
        rows.append(row)
        if i and (biggest is None or drop > biggest["drop_abs"]):
            biggest = row
    for r in rows:
        for k in ("conv_from_prev", "conv_from_start", "share_of_total_loss"):
            if isinstance(r[k], float):
                r[k] = round(r[k], 4)
    return {"steps": rows, "overall_conversion": round(steps[-1][1] / start, 4),
            "biggest_leak": None if biggest is None else biggest["step"], "warnings": warnings}


def calc_cohort(rows: List[Dict[str, str]], days: List[int], mode: str,
                asof: Optional[_dt.date], confidence: float = 0.95) -> Dict[str, object]:
    if mode not in ("classic", "rolling"):
        raise InputError("mode must be classic or rolling")
    install: Dict[str, _dt.date] = {}
    active: Dict[str, set] = {}
    max_seen: Optional[_dt.date] = None
    for r in rows:
        uid = r["user_id"]
        if not uid:
            continue
        inst = parse_date(r["install_date"])
        act = parse_date(r["active_date"])
        if act < inst:
            raise InputError(f"user {uid}: active_date {act} before install_date {inst}")
        install[uid] = min(inst, install.get(uid, inst))
        active.setdefault(uid, set()).add(act)
        if max_seen is None or act > max_seen:
            max_seen = act
    if not install:
        raise InputError("no users found")
    asof = asof or max_seen
    cohorts: Dict[_dt.date, List[str]] = {}
    for uid, d in install.items():
        cohorts.setdefault(d, []).append(uid)
    table = []
    pooled = {d: [0, 0] for d in days}
    for cdate in sorted(cohorts):
        users = cohorts[cdate]
        row: Dict[str, object] = {"cohort": cdate.isoformat(), "installs": len(users)}
        for d in days:
            target = cdate + _dt.timedelta(days=d)
            if asof is not None and target > asof:
                row[f"d{d}"] = None
                continue
            if mode == "classic":
                ret = sum(1 for u in users if target in active[u])
            else:
                ret = sum(1 for u in users if any(x >= target for x in active[u]))
            row[f"d{d}"] = round(ret / len(users), 4)
            pooled[d][0] += ret
            pooled[d][1] += len(users)
        table.append(row)
    summary = {}
    for d in days:
        s, n = pooled[d]
        if n:
            p, lo, hi = wilson(s, n, confidence)
            summary[f"d{d}"] = {"rate": round(p, 4), "ci_low": round(lo, 4), "ci_high": round(hi, 4),
                               "users": n, "mature_cohorts": sum(1 for r in table if r.get(f"d{d}") is not None)}
        else:
            summary[f"d{d}"] = None
    diag = {}
    if summary.get("d1") and summary.get("d7") and summary["d1"]["rate"] > 0:
        diag["d7_over_d1"] = round(summary["d7"]["rate"] / summary["d1"]["rate"], 3)
    if summary.get("d7") and summary.get("d30") and summary["d7"]["rate"] > 0:
        diag["d30_over_d7"] = round(summary["d30"]["rate"] / summary["d7"]["rate"], 3)
    if mode == "rolling":
        diag["note"] = "rolling retention is right-censored: young cohorts are understated until they age"
    return {"mode": mode, "asof": asof.isoformat() if asof else None, "cohorts": table,
            "weighted": summary, "diagnostics": diag}


def calc_economy(flow_rows: List[Dict[str, str]], dau_days: Optional[float],
                 balance_rows: Optional[List[Dict[str, str]]], low: float, high: float,
                 max_hoard_days: Optional[float],
                 broke_below: Optional[Dict[str, float]] = None) -> Dict[str, object]:
    per: Dict[str, Dict[str, Dict[str, float]]] = {}
    for r in flow_rows:
        cur = r["currency"]
        flow = r["flow"].lower()
        if flow in ("earn", "source", "faucet"):
            flow = "source"
        elif flow in ("spend", "sink", "drain"):
            flow = "sink"
        else:
            raise InputError(f"flow must be source/sink (or earn/spend), got '{r['flow']}'")
        amt = fnum(r["amount"], "amount")
        if amt < 0:
            raise InputError("amounts must be >= 0; use flow to give direction")
        per.setdefault(cur, {"source": {}, "sink": {}})
        node = r.get("node") or "unknown"
        per[cur][flow][node] = per[cur][flow].get(node, 0.0) + amt
    balances: Dict[str, List[float]] = {}
    if balance_rows:
        for r in balance_rows:
            balances.setdefault(r["currency"], []).append(fnum(r["balance"], "balance"))
    out = {}
    flags_total = 0
    for cur, f in sorted(per.items()):
        src = sum(f["source"].values())
        snk = sum(f["sink"].values())
        res: Dict[str, object] = {
            "source_total": round(src, 4), "sink_total": round(snk, 4), "net": round(src - snk, 4),
            "sink_source_ratio": round(snk / src, 4) if src else None,
            "top_sources": [{"node": k, "share": round(v / src, 4)} for k, v in sorted(f["source"].items(), key=lambda kv: -kv[1])[:5]] if src else [],
            "top_sinks": [{"node": k, "share": round(v / snk, 4)} for k, v in sorted(f["sink"].items(), key=lambda kv: -kv[1])[:5]] if snk else [],
        }
        flags = []
        ratio = res["sink_source_ratio"]
        if ratio is None:
            flags.append("no sources recorded")
        elif ratio < low:
            flags.append(f"sink/source {ratio:.2f} < {low}: currency accumulates (inflation/hoarding risk) - add sinks or cut faucets")
        elif ratio > high:
            flags.append(f"sink/source {ratio:.2f} > {high}: balances draining - check broke rate and faucet reach")
        notes = []
        if src and max(f["source"].values()) / src > 0.6:
            notes.append("one source supplies > 60% of inflow (normal for IAP-fed hard currency; a risk for soft currency)")
        sink_per_dau = None
        if dau_days:
            res["source_per_dau_day"] = round(src / dau_days, 4)
            sink_per_dau = snk / dau_days
            res["sink_per_dau_day"] = round(sink_per_dau, 4)
            res["net_per_dau_day"] = round((src - snk) / dau_days, 4)
        if cur in balances:
            vals = balances[cur]
            pct = {f"p{q}": round(percentile(vals, q), 2) for q in (10, 50, 90, 99)}
            res["balance_percentiles"] = pct
            res["zero_balance_share"] = round(sum(1 for v in vals if v <= 0) / len(vals), 4)
            if broke_below and cur in broke_below:
                thr = broke_below[cur]
                res["broke_share"] = round(sum(1 for v in vals if v < thr) / len(vals), 4)
                res["broke_threshold"] = thr
            if sink_per_dau:
                hoard = {k: round(v / sink_per_dau, 1) for k, v in pct.items()}
                res["hoard_days"] = hoard
                if max_hoard_days is not None and hoard["p50"] > max_hoard_days:
                    flags.append(f"median player holds {hoard['p50']} days of spending > target {max_hoard_days}")
        res["flags"] = flags
        res["notes"] = notes
        flags_total += len(flags)
        out[cur] = res
    return {"currencies": out, "bands": {"low": low, "high": high}, "flag_count": flags_total}


RFM_RULES: List[Tuple[str, str, Callable[[int, int, int], bool]]] = [
    # (segment, readable rule, predicate on 1-5 scores r, f, m); first match wins.
    ("champions", "r>=4 and f>=4 and m>=4", lambda r, f, m: r >= 4 and f >= 4 and m >= 4),
    ("loyal", "r>=3 and f>=4", lambda r, f, m: r >= 3 and f >= 4),
    ("cant_lose", "r<=2 and f>=4 and m>=4", lambda r, f, m: r <= 2 and f >= 4 and m >= 4),
    ("at_risk", "r<=2 and f>=3", lambda r, f, m: r <= 2 and f >= 3),
    ("new_or_promising", "r>=4 and f<=2", lambda r, f, m: r >= 4 and f <= 2),
    ("potential_loyal", "r>=3 and f>=2", lambda r, f, m: r >= 3 and f >= 2),
    ("lost", "r==1 and f==1", lambda r, f, m: r == 1 and f == 1),
    ("hibernating", "r<=2", lambda r, f, m: r <= 2),
    ("needs_attention", "otherwise", lambda r, f, m: True),
]


def _quantile_scores(values: List[float], bins: int, reverse: bool) -> List[int]:
    n = len(values)
    order = sorted(range(n), key=lambda i: values[i])
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j + 1 < n and values[order[j + 1]] == values[order[i]]:
            j += 1
        avg = (i + j) / 2.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    scores = []
    for r in ranks:
        pct = (r + 0.5) / n
        s = min(bins, int(pct * bins) + 1)
        scores.append(bins + 1 - s if reverse else s)
    return scores


def calc_rfm(rows: List[Dict[str, str]], bins: int) -> Tuple[Dict[str, object], List[Dict[str, object]]]:
    if bins < 2 or bins > 10:
        raise InputError("bins must be 2-10")
    uids = [r["user_id"] for r in rows]
    rec = [fnum(r["recency_days"], "recency_days") for r in rows]
    frq = [fnum(r["frequency"], "frequency") for r in rows]
    mon = [fnum(r["monetary"], "monetary") for r in rows]
    rs = _quantile_scores(rec, bins, reverse=True)
    fs = _quantile_scores(frq, bins, reverse=False)
    # Most game players never pay: non-spenders get M=1 and spenders are
    # binned among themselves into 2..bins, so zero ties do not land mid-scale.
    spenders = [i for i, v in enumerate(mon) if v > 0]
    ms = [1] * len(mon)
    if spenders:
        sub = _quantile_scores([mon[i] for i in spenders], bins - 1, reverse=False)
        for idx, sc in zip(spenders, sub):
            ms[idx] = sc + 1

    def to5(s: int) -> int:
        return max(1, min(5, int(math.ceil(s * 5.0 / bins))))

    per_user = []
    seg_stats: Dict[str, List[float]] = {}
    for i, uid in enumerate(uids):
        r5, f5, m5 = to5(rs[i]), to5(fs[i]), to5(ms[i])
        seg = "needs_attention"
        for name, _rule, pred in RFM_RULES:
            if pred(r5, f5, m5):
                seg = name
                break
        per_user.append({"user_id": uid, "r": rs[i], "f": fs[i], "m": ms[i], "segment": seg})
        seg_stats.setdefault(seg, []).append(mon[i])
    n = len(uids)
    total_m = sum(mon) or 1.0
    segments = []
    for name, _rule, _pred in RFM_RULES:
        vals = seg_stats.get(name, [])
        if not vals:
            continue
        segments.append({"segment": name, "users": len(vals), "share": round(len(vals) / n, 4),
                         "avg_monetary": round(sum(vals) / len(vals), 4),
                         "monetary_share": round(sum(vals) / total_m, 4)})
    return {"bins": bins, "users": n, "segments": segments,
            "rules": [{"segment": name, "rule": rule} for name, rule, _ in RFM_RULES]}, per_user


def fit_curve(points: List[Tuple[float, float]], model: str) -> Tuple[float, float, float]:
    """Least squares fit. power: r = a*t^-b ; exp: r = a*exp(-b*t). Returns (a, b, r2 in log space)."""
    xs, ys = [], []
    for t, r in points:
        xs.append(math.log(t) if model == "power" else t)
        ys.append(math.log(r))
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        raise InputError("points need at least two distinct days")
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    slope = sxy / sxx
    icpt = my - slope * mx
    ss_tot = sum((y - my) ** 2 for y in ys)
    ss_res = sum((y - (icpt + slope * x)) ** 2 for x, y in zip(xs, ys))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0
    return math.exp(icpt), -slope, r2


def curve_value(a: float, b: float, model: str, t: int) -> float:
    if t <= 0:
        return 1.0
    v = a * (t ** (-b)) if model == "power" else a * math.exp(-b * t)
    return max(0.0, min(1.0, v))


def calc_payback(points: List[Tuple[float, float]], arpdau: float, cpi: float, net_share: float,
                 horizon: int, model: str) -> Dict[str, object]:
    if arpdau <= 0 or cpi <= 0:
        raise InputError("arpdau and cpi must be > 0")
    if not 0 < net_share <= 1:
        raise InputError("net-share must be in (0, 1]")
    if horizon < 1 or horizon > 3650:
        raise InputError("horizon must be 1..3650")
    a, b, r2 = fit_curve(points, model)
    cum_days = 0.0
    payback_day = None
    checkpoints = [d for d in (1, 3, 7, 14, 30, 60, 90, 180, 365, 730) if d <= horizon]
    if horizon not in checkpoints:
        checkpoints.append(horizon)
    rows = []
    for t in range(0, horizon + 1):
        cum_days += curve_value(a, b, model, t)
        cum_rev = cum_days * arpdau * net_share
        if payback_day is None and cum_rev >= cpi:
            payback_day = t
        if t in checkpoints:
            rows.append({"day": t, "retention": round(curve_value(a, b, model, t), 4),
                         "lifetime_days": round(cum_days, 3), "cum_arpu": round(cum_rev, 4),
                         "roas": round(cum_rev / cpi, 4)})
    lifetime = cum_days
    return {
        "model": model, "a": round(a, 5), "b": round(b, 5), "fit_r2_log": round(r2, 4),
        "arpdau": arpdau, "net_share": net_share, "basis": "gross" if net_share == 1 else "net",
        "cpi": cpi, "horizon": horizon, "lifetime_days": round(lifetime, 3),
        "ltv": round(lifetime * arpdau * net_share, 4), "checkpoints": rows,
        "payback_day": payback_day,
        "break_even_arpdau": round(cpi / (lifetime * net_share), 5),
        "note": "assumes constant ARPDAU across player age; older players usually monetize more, so treat as a floor for IAP-heavy games",
    }


def calc_srm(counts: List[float], weights: Optional[List[float]], alpha: float) -> Dict[str, object]:
    k = len(counts)
    if k < 2:
        raise InputError("need at least two arms")
    if any(c < 0 for c in counts):
        raise InputError("counts must be >= 0")
    if weights is None:
        weights = [1.0 / k] * k
    if len(weights) != k:
        raise InputError("weights must match counts")
    ws = sum(weights)
    if ws <= 0:
        raise InputError("weights must sum to > 0")
    weights = [w / ws for w in weights]
    total = sum(counts)
    if total <= 0:
        raise InputError("total count must be > 0")
    exp = [total * w for w in weights]
    chi2 = sum((o - e) ** 2 / e for o, e in zip(counts, exp) if e > 0)
    p = chi2_sf(chi2, k - 1)
    return {"counts": counts, "expected": [round(e, 2) for e in exp], "chi2": round(chi2, 4), "df": k - 1,
            "p_value": p, "alpha": alpha, "mismatch": p < alpha,
            "verdict": "SRM detected: do not read results; debug assignment/logging" if p < alpha else "no SRM at this alpha"}


# --------------------------------------------------------------------------
# output
# --------------------------------------------------------------------------

def emit(result: object, as_json: bool, text: str) -> None:
    if as_json:
        print(json.dumps(result, indent=2, default=str))
    else:
        print(text)


def fmt_pct(v: Optional[float]) -> str:
    return "  -  " if v is None else f"{v * 100:5.1f}%"


def text_cohort(res: Dict[str, object], days: List[int]) -> str:
    lines = [f"Retention triangle ({res['mode']}, as of {res['asof']})",
             "cohort      installs " + " ".join(f"{('D' + str(d)):>6}" for d in days)]
    for r in res["cohorts"]:
        lines.append(f"{r['cohort']}  {r['installs']:8d} " + " ".join(f"{fmt_pct(r.get('d' + str(d))):>6}" for d in days))
    lines.append("weighted (mature cohorts only, Wilson 95% CI):")
    for d in days:
        s = res["weighted"].get(f"d{d}")
        if s:
            lines.append(f"  D{d}: {s['rate'] * 100:.1f}% [{s['ci_low'] * 100:.1f}-{s['ci_high'] * 100:.1f}] n={s['users']}")
    for k, v in res["diagnostics"].items():
        lines.append(f"  {k} = {v}")
    return "\n".join(lines)


# --------------------------------------------------------------------------
# self-test
# --------------------------------------------------------------------------

def selftest() -> int:
    failures: List[str] = []

    def check(cond: bool, label: str) -> None:
        if not cond:
            failures.append(label)

    # stats
    check(abs(norm_ppf(0.975) - 1.959964) < 1e-4, "norm_ppf")
    p, lo, hi = wilson(40, 100)
    check(abs(lo - 0.3094) < 0.001 and abs(hi - 0.4980) < 0.001, f"wilson {lo:.4f} {hi:.4f}")
    check(abs(chi2_sf(3.841459, 1) - 0.05) < 1e-4, "chi2 df1")
    check(abs(chi2_sf(5.991465, 2) - 0.05) < 1e-4, "chi2 df2")
    check(abs(chi2_sf(30.0, 3) - 1.380e-6) < 1e-7, "chi2 df3 tail")
    # srm
    s1 = calc_srm([10000, 10400], None, 0.001)
    check(abs(s1["chi2"] - 7.8431) < 1e-3 and not s1["mismatch"], "srm no mismatch")
    s2 = calc_srm([10000, 10600], None, 0.001)
    check(s2["mismatch"], "srm mismatch")
    # kpis
    k = calc_kpis({"dau": 10000, "mau": 50000, "iap_revenue": 900.0, "ad_revenue": 300.0, "payers": 150,
                   "impressions": 40000, "sessions": 32000, "playtime_min": 224000, "spend": 5000, "installs": 2000,
                   "invites_per_user": 0.5, "invite_conversion": 0.2})
    check(k["stickiness_dau_mau"] == 0.2 and abs(k["arpdau"] - 0.12) < 1e-9, "kpis basic")
    check(abs(k["ecpm"] - 7.5) < 1e-9 and abs(k["arppu_iap"] - 6.0) < 1e-9, "kpis ads/arppu")
    check(abs(k["k_factor"] - 0.1) < 1e-9 and abs(k["viral_multiplier"] - 1.111111) < 1e-5, "kpis viral")
    check(abs(k["cpi"] - 2.5) < 1e-9 and abs(k["avg_session_min"] - 7.0) < 1e-9, "kpis cpi/session")
    # funnel
    f = calc_funnel(parse_steps("first_open:10000,tutorial_begin:9200,step_3:7800,tutorial_complete:7100,level_5:5600"))
    check(f["biggest_leak"] == "level_5" and abs(f["overall_conversion"] - 0.56) < 1e-9, "funnel")
    # cohort: 3 cohorts of 10 users with known activity
    lines = ["user_id,install_date,active_date"]
    base = _dt.date(2026, 10, 1)
    for c in range(3):
        inst = base + _dt.timedelta(days=c)
        for u in range(10):
            uid = f"c{c}u{u}"
            lines.append(f"{uid},{inst},{inst}")
            if u < 4:
                lines.append(f"{uid},{inst},{inst + _dt.timedelta(days=1)}")
            if u < 2:
                lines.append(f"{uid},{inst},{inst + _dt.timedelta(days=7)}")
            if u == 2:
                lines.append(f"{uid},{inst},{inst + _dt.timedelta(days=9)}")
    rows = read_csv_rows("\n".join(lines), ["user_id", "install_date", "active_date"], is_text=True)
    cr = calc_cohort(rows, [1, 7], "classic", _dt.date(2026, 10, 9))
    check(cr["weighted"]["d1"]["rate"] == 0.4 and cr["weighted"]["d7"]["rate"] == 0.2, f"cohort classic {cr['weighted']}")
    check(cr["cohorts"][2]["d7"] is None and cr["weighted"]["d7"]["mature_cohorts"] == 2, "cohort maturity")
    rr = calc_cohort(rows, [7], "rolling", _dt.date(2026, 10, 12))
    check(rr["weighted"]["d7"]["rate"] == 0.3, f"cohort rolling {rr['weighted']}")
    # economy
    flows = read_csv_rows("currency,flow,node,amount\ncoins,source,win_reward,7000\ncoins,source,daily_chest,1000\n"
                          "coins,sink,upgrade,4000\ncoins,sink,booster,800\ngems,earn,ads,60\ngems,earn,event,40\ngems,spend,revive,100\n",
                          ["currency", "flow", "amount"], is_text=True)
    bal = read_csv_rows("currency,balance\n" + "".join(f"coins,{v}\n" for v in (0, 100, 200, 400, 800, 1600, 3200, 6400)),
                        ["currency", "balance"], is_text=True)
    e = calc_economy(flows, 100.0, bal, 0.7, 1.05, 10.0, {"coins": 300})
    coins = e["currencies"]["coins"]
    check(abs(coins["sink_source_ratio"] - 0.6) < 1e-9 and coins["flags"], "economy ratio/flags")
    check(abs(coins["sink_per_dau_day"] - 48.0) < 1e-9 and coins["hoard_days"]["p50"] == 12.5, f"economy hoard {coins.get('hoard_days')}")
    check(not e["currencies"]["gems"]["flags"], "economy gems in band")
    check(coins["broke_share"] == 0.375, f"economy broke share {coins.get('broke_share')}")
    # rfm
    rfm_rows = read_csv_rows("user_id,recency_days,frequency,monetary\n" + "".join(
        f"u{i},{i},{20 - i},{(20 - i) * 2}\n" for i in range(20)), ["user_id", "recency_days", "frequency", "monetary"], is_text=True)
    summary, per_user = calc_rfm(rfm_rows, 5)
    segs = {s["segment"]: s for s in summary["segments"]}
    check(per_user[0]["segment"] == "champions" and per_user[-1]["segment"] in ("lost", "hibernating"), "rfm extremes")
    check(abs(sum(s["share"] for s in summary["segments"]) - 1.0) < 1e-6 and "champions" in segs, "rfm shares")
    zrows = read_csv_rows("user_id,recency_days,frequency,monetary\n" + "".join(
        f"z{i},1,10,{5 if i == 0 else 0}\n" for i in range(10)), ["user_id", "recency_days", "frequency", "monetary"], is_text=True)
    _, zu = calc_rfm(zrows, 5)
    check(zu[0]["m"] >= 2 and all(u["m"] == 1 for u in zu[1:]), "rfm zero spenders score 1")
    # payback: exact power-law data recovers parameters
    pts = [(t, 0.4 * t ** -0.5) for t in (1, 7, 30)]
    pb = calc_payback(pts, 0.10, 1.50, 1.0, 365, "power")
    check(abs(pb["a"] - 0.4) < 1e-4 and abs(pb["b"] - 0.5) < 1e-4, "payback fit")
    manual = 1.0 + sum(0.4 * t ** -0.5 for t in range(1, 366))
    check(abs(pb["lifetime_days"] - manual) < 1e-2, "payback lifetime")
    check(pb["payback_day"] is not None and pb["checkpoints"][-1]["day"] == 365, "payback day")
    ex = calc_payback([(1, 0.4), (7, 0.2)], 0.1, 100.0, 1.0, 90, "exp")
    check(ex["payback_day"] is None, "payback none")
    # input errors
    try:
        parse_points("1:0.4")
        failures.append("parse_points should reject one point")
    except InputError:
        pass
    if failures:
        print("SELFTEST FAILED:")
        for x in failures:
            print("  -", x)
        return 1
    print("selftest ok (stats, srm, kpis, funnel, cohort classic/rolling, economy, rfm, payback)")
    return 0


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true", help="machine-readable output")
    p = argparse.ArgumentParser(description="Player-analytics calculators (see module docstring).")
    p.add_argument("--selftest", action="store_true", help="run built-in tests and exit")
    sub = p.add_subparsers(dest="cmd")

    k = sub.add_parser("kpis", parents=[common], help="derived KPIs from daily aggregates")
    for name in ("dau", "wau", "mau", "revenue", "iap-revenue", "ad-revenue", "payers", "installs", "spend",
                 "impressions", "sessions", "playtime-min", "invites-per-user", "invite-conversion"):
        k.add_argument(f"--{name}", type=float)

    c = sub.add_parser("ci", parents=[common], help="Wilson interval for a rate")
    c.add_argument("--success", type=float, required=True)
    c.add_argument("--n", type=float, required=True)
    c.add_argument("--confidence", type=float, default=0.95)

    f = sub.add_parser("funnel", parents=[common], help="step conversion and biggest leak")
    f.add_argument("--steps", required=True, help='"name:count,name:count,..." in funnel order')

    co = sub.add_parser("cohort", parents=[common], help="retention triangle from user_id,install_date,active_date CSV")
    co.add_argument("--csv", required=True)
    co.add_argument("--days", default="1,3,7,14,30")
    co.add_argument("--mode", choices=["classic", "rolling"], default="classic")
    co.add_argument("--asof", help="YYYY-MM-DD last complete day (default: max active_date)")

    e = sub.add_parser("economy", parents=[common], help="source/sink health from currency,flow,node,amount CSV")
    e.add_argument("--csv", required=True)
    e.add_argument("--dau-days", type=float, help="sum of DAU over the window (normalizes per player-day)")
    e.add_argument("--balances", help="CSV currency,balance (one row per player snapshot)")
    e.add_argument("--low", type=float, default=0.7, help="flag sink/source below this (default 0.7)")
    e.add_argument("--high", type=float, default=1.05, help="flag sink/source above this (default 1.05)")
    e.add_argument("--max-hoard-days", type=float, help="flag if median balance covers more days of spending")
    e.add_argument("--broke-below", help='"coins:200,gems:10" share of players below the cheapest meaningful sink')
    e.add_argument("--strict", action="store_true", help="exit 1 if any flag is raised")

    r = sub.add_parser("rfm", parents=[common], help="RFM scores from user_id,recency_days,frequency,monetary CSV")
    r.add_argument("--csv", required=True)
    r.add_argument("--bins", type=int, default=5)
    r.add_argument("--out", help="write per-user scores CSV here")

    pb = sub.add_parser("payback", parents=[common], help="ROAS curve and payback day from retention points")
    pb.add_argument("--points", required=True, help='"1:0.40,7:0.18,30:0.08"')
    pb.add_argument("--arpdau", type=float, required=True)
    pb.add_argument("--cpi", type=float, required=True)
    pb.add_argument("--net-share", type=float, default=1.0, help="share of revenue kept (1.0 = gross)")
    pb.add_argument("--horizon", type=int, default=365)
    pb.add_argument("--model", choices=["power", "exp"], default="power")
    pb.add_argument("--strict", action="store_true", help="exit 1 if no payback within horizon")

    s = sub.add_parser("srm", parents=[common], help="sample ratio mismatch check")
    s.add_argument("--counts", required=True, help='"10000,10400" users per arm')
    s.add_argument("--weights", help='"0.5,0.5" intended split (default equal)')
    s.add_argument("--alpha", type=float, default=0.001)
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return 0 if exc.code == 0 else 2
    if args.selftest:
        return selftest()
    if not args.cmd:
        parser.print_help()
        return 2
    try:
        if args.cmd == "kpis":
            vals = {k: getattr(args, k) for k in ("dau", "wau", "mau", "revenue", "iap_revenue", "ad_revenue", "payers",
                                                  "installs", "spend", "impressions", "sessions", "playtime_min",
                                                  "invites_per_user", "invite_conversion")}
            res = calc_kpis(vals)
            if not res:
                raise InputError("give at least one combination, e.g. --dau and --mau")
            emit(res, args.json, "\n".join(f"{k:24s} {v}" for k, v in res.items()))
            return 0
        if args.cmd == "ci":
            p, lo, hi = wilson(args.success, args.n, args.confidence)
            res = {"rate": round(p, 5), "low": round(lo, 5), "high": round(hi, 5), "n": args.n,
                   "confidence": args.confidence, "half_width": round((hi - lo) / 2, 5)}
            emit(res, args.json, f"rate {p * 100:.2f}%  {int(args.confidence * 100)}% CI [{lo * 100:.2f}%, {hi * 100:.2f}%]  (+/-{(hi - lo) * 50:.2f} pp)")
            return 0
        if args.cmd == "funnel":
            res = calc_funnel(parse_steps(args.steps))
            lines = [f"{'step':24s} {'count':>10s} {'from prev':>9s} {'from start':>10s} {'loss share':>10s}"]
            for r in res["steps"]:
                lines.append(f"{r['step'][:24]:24s} {r['count']:10.0f} {fmt_pct(r['conv_from_prev']):>9s} {fmt_pct(r['conv_from_start']):>10s} {fmt_pct(r['share_of_total_loss']):>10s}")
            lines.append(f"overall {res['overall_conversion'] * 100:.1f}%  biggest leak: {res['biggest_leak']}")
            lines += [f"warning: {w}" for w in res["warnings"]]
            emit(res, args.json, "\n".join(lines))
            return 0
        if args.cmd == "cohort":
            try:
                days = sorted({int(x) for x in args.days.split(",") if x.strip()})
            except ValueError:
                raise InputError("--days must be integers like 1,7,30")
            if not days or days[0] < 1:
                raise InputError("--days must be >= 1")
            rows = read_csv_rows(args.csv, ["user_id", "install_date", "active_date"])
            res = calc_cohort(rows, days, args.mode, parse_date(args.asof) if args.asof else None)
            emit(res, args.json, text_cohort(res, days))
            return 0
        if args.cmd == "economy":
            flows = read_csv_rows(args.csv, ["currency", "flow", "amount"])
            bals = read_csv_rows(args.balances, ["currency", "balance"]) if args.balances else None
            broke = None
            if args.broke_below:
                broke = {}
                for chunk in args.broke_below.split(","):
                    if ":" not in chunk:
                        raise InputError("--broke-below expects currency:amount pairs")
                    cur_name, amt = chunk.split(":", 1)
                    broke[cur_name.strip()] = fnum(amt.strip(), "--broke-below")
            res = calc_economy(flows, args.dau_days, bals, args.low, args.high, args.max_hoard_days, broke)
            lines = []
            for cur, r in res["currencies"].items():
                lines.append(f"[{cur}] source {r['source_total']}  sink {r['sink_total']}  sink/source {r['sink_source_ratio']}")
                for key in ("source_per_dau_day", "sink_per_dau_day", "balance_percentiles", "hoard_days", "zero_balance_share", "broke_share"):
                    if key in r:
                        lines.append(f"   {key}: {r[key]}")
                lines.append("   top sources: " + ", ".join(f"{x['node']} {x['share'] * 100:.0f}%" for x in r["top_sources"]))
                lines.append("   top sinks:   " + ", ".join(f"{x['node']} {x['share'] * 100:.0f}%" for x in r["top_sinks"]))
                lines += [f"   FLAG: {x}" for x in r["flags"]]
                lines += [f"   note: {x}" for x in r["notes"]]
            emit(res, args.json, "\n".join(lines))
            return 1 if (args.strict and res["flag_count"]) else 0
        if args.cmd == "rfm":
            rows = read_csv_rows(args.csv, ["user_id", "recency_days", "frequency", "monetary"])
            res, per_user = calc_rfm(rows, args.bins)
            if args.out:
                with open(args.out, "w", newline="", encoding="utf-8") as fh:
                    w = csv.DictWriter(fh, fieldnames=["user_id", "r", "f", "m", "segment"])
                    w.writeheader()
                    w.writerows(per_user)
                res["per_user_csv"] = args.out
            lines = [f"{'segment':18s} {'users':>7s} {'share':>7s} {'avg M':>9s} {'M share':>8s}"]
            for s in res["segments"]:
                lines.append(f"{s['segment']:18s} {s['users']:7d} {fmt_pct(s['share']):>7s} {s['avg_monetary']:9.2f} {fmt_pct(s['monetary_share']):>8s}")
            emit(res, args.json, "\n".join(lines))
            return 0
        if args.cmd == "payback":
            res = calc_payback(parse_points(args.points), args.arpdau, args.cpi, args.net_share, args.horizon, args.model)
            lines = [f"fit {res['model']}: a={res['a']} b={res['b']} (log R^2 {res['fit_r2_log']})  basis={res['basis']}",
                     f"{'day':>5s} {'ret':>7s} {'life d':>8s} {'cum ARPU':>9s} {'ROAS':>7s}"]
            for r in res["checkpoints"]:
                lines.append(f"{r['day']:5d} {fmt_pct(r['retention']):>7s} {r['lifetime_days']:8.2f} {r['cum_arpu']:9.3f} {fmt_pct(r['roas']):>7s}")
            lines.append(f"LTV({res['horizon']}d) {res['ltv']}  payback day: {res['payback_day']}  break-even ARPDAU: {res['break_even_arpdau']}")
            lines.append("note: " + res["note"])
            emit(res, args.json, "\n".join(lines))
            return 1 if (args.strict and res["payback_day"] is None) else 0
        if args.cmd == "srm":
            try:
                counts = [float(x) for x in args.counts.split(",") if x.strip()]
                weights = [float(x) for x in args.weights.split(",")] if args.weights else None
            except ValueError:
                raise InputError("counts and weights must be numbers")
            res = calc_srm(counts, weights, args.alpha)
            emit(res, args.json, f"chi2={res['chi2']} df={res['df']} p={res['p_value']:.3g} -> {res['verdict']}")
            return 1 if res["mismatch"] else 0
    except InputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    parser.print_help()
    return 2


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows pipes default to the ANSI code page; Claude Code reads UTF-8
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
