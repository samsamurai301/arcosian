#!/usr/bin/env python3
"""A/B test maths: sample size, proportion z-test, Welch t-test, group-sequential boundaries.

  ab_test.py size --baseline P --mde D [--alpha 0.05] [--power 0.8] [--two-sided]
  ab_test.py analyze --a-success X --a-n N --b-success Y --b-n M [--json]
  ab_test.py mean --a-mean --a-sd --a-n --b-mean --b-sd --b-n [--json]
  ab_test.py sequential --baseline P --mde D --looks K [--alpha 0.05] [--json]

--mde is an absolute difference (0.02 = +2 points). Tests are two-sided by default;
`--two-sided` is accepted for explicitness and `--one-sided` switches `size` to one-sided.
Normal-curve helpers are reused from skills/player-analytics/scripts/analytics_calc.py.
Exit codes: 0 ok (analyze/mean: also when not significant), 1 selftest failure, 2 usage error.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

HERE = Path(__file__).resolve().parent


def _load(rel: str, name: str):
    spec = importlib.util.spec_from_file_location(name, str(HERE.parent / rel))
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    sys.modules[name] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


_ac = _load("skills/player-analytics/scripts/analytics_calc.py", "analytics_calc_mod")
InputError = _ac.InputError
norm_cdf, norm_ppf = _ac.norm_cdf, _ac.norm_ppf


# ---------------------------------------------------------------- math

def _betacf(a: float, b: float, x: float) -> float:
    tiny = 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 300):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 3e-14:
            break
    return h


def betainc(a: float, b: float, x: float) -> float:
    """Regularized incomplete beta I_x(a, b)."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lbeta = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
    front = math.exp(lbeta + a * math.log(x) + b * math.log(1.0 - x))
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, x) / a
    return 1.0 - front * _betacf(b, a, 1.0 - x) / b


def t_cdf(t: float, df: float) -> float:
    x = df / (df + t * t)
    tail = 0.5 * betainc(df / 2.0, 0.5, x)
    return 1.0 - tail if t > 0 else tail


def t_ppf(p: float, df: float) -> float:
    lo, hi = -200.0, 200.0
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if t_cdf(mid, df) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def _check_p(name: str, v: float) -> None:
    if not 0.0 < v < 1.0:
        raise InputError("%s must be in (0, 1), got %s" % (name, v))


# ---------------------------------------------------------------- size / analyze / mean

def sample_size(baseline: float, mde: float, alpha: float, power: float, two_sided: bool) -> Dict[str, Any]:
    _check_p("baseline", baseline)
    _check_p("alpha", alpha)
    _check_p("power", power)
    p2 = baseline + mde
    if mde == 0 or not 0.0 < p2 < 1.0:
        raise InputError("baseline + mde must be in (0, 1) and mde non-zero")
    za = norm_ppf(1.0 - alpha / (2.0 if two_sided else 1.0))
    zb = norm_ppf(power)
    n = (za + zb) ** 2 * (baseline * (1 - baseline) + p2 * (1 - p2)) / (mde ** 2)
    n_arm = int(math.ceil(n))
    return {"baseline": baseline, "mde_abs": mde, "variant_rate": round(p2, 6),
            "relative_lift": round(mde / baseline, 6), "alpha": alpha, "power": power,
            "two_sided": two_sided, "n_per_arm": n_arm, "n_total": 2 * n_arm}


def analyze_props(xa: float, na: float, xb: float, nb: float, alpha: float = 0.05) -> Dict[str, Any]:
    if na <= 0 or nb <= 0 or not (0 <= xa <= na) or not (0 <= xb <= nb):
        raise InputError("need 0 <= success <= n and n > 0 for both arms")
    pa, pb = xa / na, xb / nb
    pool = (xa + xb) / (na + nb)
    se0 = math.sqrt(pool * (1 - pool) * (1 / na + 1 / nb))
    z = (pb - pa) / se0 if se0 > 0 else 0.0
    p = 2.0 * (1.0 - norm_cdf(abs(z)))
    se = math.sqrt(pa * (1 - pa) / na + pb * (1 - pb) / nb)
    zc = norm_ppf(1.0 - alpha / 2.0)
    diff = pb - pa
    out: Dict[str, Any] = {
        "a_rate": round(pa, 6), "b_rate": round(pb, 6), "abs_diff": round(diff, 6),
        "ci_abs": [round(diff - zc * se, 6), round(diff + zc * se, 6)],
        "z": round(z, 4), "p_value": round(p, 6), "alpha": alpha, "significant": p < alpha,
        "relative_lift": round(diff / pa, 6) if pa > 0 else None, "ci_relative": None,
    }
    if pa > 0:  # delta-method CI for the ratio on the log scale
        if xa > 0 and xb > 0:
            lr = math.log(pb / pa)
            s = math.sqrt((1 - pa) / xa + (1 - pb) / xb)
            out["ci_relative"] = [round(math.exp(lr - zc * s) - 1, 6), round(math.exp(lr + zc * s) - 1, 6)]
    out["verdict"] = ("B better" if diff > 0 else "B worse") if p < alpha else "no significant difference"
    return out


def welch(ma: float, sa: float, na: float, mb: float, sb: float, nb: float, alpha: float = 0.05) -> Dict[str, Any]:
    if na < 2 or nb < 2 or sa < 0 or sb < 0:
        raise InputError("need n >= 2 and sd >= 0 for both arms")
    va, vb = sa * sa / na, sb * sb / nb
    se = math.sqrt(va + vb)
    if se == 0:
        raise InputError("both standard deviations are zero")
    t = (mb - ma) / se
    df = (va + vb) ** 2 / (va * va / (na - 1) + vb * vb / (nb - 1))
    p = 2.0 * (1.0 - t_cdf(abs(t), df))
    tc = t_ppf(1.0 - alpha / 2.0, df)
    diff = mb - ma
    d = diff / math.sqrt(((na - 1) * sa * sa + (nb - 1) * sb * sb) / (na + nb - 2))
    return {"a_mean": ma, "b_mean": mb, "abs_diff": round(diff, 6),
            "ci_abs": [round(diff - tc * se, 6), round(diff + tc * se, 6)],
            "t": round(t, 4), "df": round(df, 3), "p_value": round(p, 6), "alpha": alpha,
            "significant": p < alpha, "relative_lift": round(diff / ma, 6) if ma else None,
            "cohens_d": round(d, 4)}


# ---------------------------------------------------------------- group sequential

_GRID = 140


def _cross_prob(bounds: Sequence[float], drift: float) -> float:
    """P(|Z_k| >= bounds[k] for some k) with equally spaced looks; Z_k = S_k / sqrt(k),
    S_k a random walk with N(drift, 1) steps. Midpoint-rule density recursion."""
    pts: List[float] = []
    dens: List[float] = []
    h_prev = 0.0
    surv = 1.0
    for k, b in enumerate(bounds, start=1):
        lim = b * math.sqrt(k)
        h = 2.0 * lim / _GRID
        xs = [-lim + (i + 0.5) * h for i in range(_GRID)]
        if k == 1:
            f = [math.exp(-0.5 * (x - drift) ** 2) / math.sqrt(2 * math.pi) for x in xs]
        else:
            f = []
            for x in xs:
                s = 0.0
                for xp, dp in zip(pts, dens):
                    s += dp * math.exp(-0.5 * (x - xp - drift) ** 2)
                f.append(s * h_prev / math.sqrt(2 * math.pi))
        pts, dens, h_prev = xs, f, h
        surv = sum(f) * h
    return 1.0 - surv


def _shape(method: str, k: int, looks: int) -> float:
    return 1.0 if method == "pocock" else math.sqrt(looks / k)


def _bounds(method: str, looks: int, c: float) -> List[float]:
    return [c * _shape(method, k, looks) for k in range(1, looks + 1)]


def _bisect(fn, lo: float, hi: float, target: float, increasing: bool, iters: int = 30) -> float:
    for _ in range(iters):
        mid = (lo + hi) / 2.0
        v = fn(mid)
        if (v < target) == increasing:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def sequential(baseline: float, mde: float, looks: int, alpha: float, power: float = 0.8,
               method: str = "obf") -> Dict[str, Any]:
    if looks < 1 or looks > 10:
        raise InputError("--looks must be 1..10")
    fixed = sample_size(baseline, mde, alpha, power, True)
    # c such that total two-sided type I error = alpha (cross prob decreases as c grows)
    c = _bisect(lambda c_: _cross_prob(_bounds(method, looks, c_), 0.0), 1.0, 5.0, alpha, increasing=False)
    bounds = _bounds(method, looks, c)
    # drift per look such that power matches; inflation relative to the fixed design
    za, zb = norm_ppf(1.0 - alpha / 2.0), norm_ppf(power)
    theta = _bisect(lambda d: _cross_prob(bounds, d), 0.0, 2.0 * (za + zb) / math.sqrt(looks), power,
                    increasing=True) * math.sqrt(looks)
    inflation = (theta / (za + zb)) ** 2
    n_max = int(math.ceil(fixed["n_per_arm"] * inflation))
    rows = []
    for k, b in enumerate(bounds, start=1):
        rows.append({"look": k, "info_fraction": round(k / looks, 4), "z_boundary": round(b, 4),
                     "nominal_p": round(2 * (1 - norm_cdf(b)), 6),
                     "n_per_arm": int(math.ceil(n_max * k / looks))})
    return {"method": method, "looks": looks, "alpha": alpha, "power": power, "baseline": baseline,
            "mde_abs": mde, "fixed_n_per_arm": fixed["n_per_arm"], "inflation": round(inflation, 4),
            "max_n_per_arm": n_max, "boundaries": rows,
            "note": "equally spaced looks, two-sided; stop for efficacy only when |z| >= boundary"}


# ---------------------------------------------------------------- CLI

def selftest() -> int:
    fails: List[str] = []

    def chk(name: str, got: float, want: float, tol: float) -> None:
        if abs(got - want) > tol:
            fails.append("%s: got %s want %s +- %s" % (name, got, want, tol))

    chk("ppf .975", norm_ppf(0.975), 1.959964, 1e-5)
    s = sample_size(0.5, 0.05, 0.05, 0.8, True)
    chk("size 0.5/0.55", s["n_per_arm"], 1562, 2)
    s1 = sample_size(0.5, 0.05, 0.05, 0.8, False)
    if s1["n_per_arm"] >= s["n_per_arm"]:
        fails.append("one-sided must need fewer samples")
    a = analyze_props(200, 1000, 240, 1000)
    chk("analyze z", a["z"], 2.159, 0.002)
    chk("analyze p", a["p_value"], 0.0309, 0.0005)
    chk("analyze lift", a["relative_lift"], 0.2, 1e-9)
    chk("t cdf df1", t_cdf(1.0, 1), 0.75, 1e-9)
    chk("t cdf df2", t_cdf(1.0, 2), 0.5 + 1 / (2 * math.sqrt(3)), 1e-9)
    chk("t ppf df10", t_ppf(0.975, 10), 2.228139, 1e-4)
    m = welch(10.0, 2.0, 25, 11.0, 2.0, 25)  # se = 0.5657, t = 1.7678, df = 48
    chk("welch t", m["t"], 1.7678, 1e-3)
    chk("welch df", m["df"], 48.0, 1e-6)
    chk("welch p", m["p_value"], 0.0835, 0.002)
    # Pocock two-sided alpha .05: K=2 -> 2.178, K=3 -> 2.289; OBF K=2 -> 1.977 * sqrt(2/k)
    for K, want in ((2, 2.178), (3, 2.289)):
        r = sequential(0.5, 0.05, K, 0.05, method="pocock")
        chk("pocock K=%d" % K, r["boundaries"][0]["z_boundary"], want, 0.012)
    r = sequential(0.5, 0.05, 2, 0.05, method="obf")
    chk("obf K=2 final", r["boundaries"][1]["z_boundary"], 1.977, 0.012)
    chk("obf K=2 first", r["boundaries"][0]["z_boundary"], 2.797, 0.02)
    chk("obf K=2 inflation", r["inflation"], 1.008, 0.015)
    for f in fails:
        print("FAIL", f)
    print("ab_test selftest: %s" % ("FAILED" if fails else "ok"))
    return 1 if fails else 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--selftest", action="store_true")
    sub = p.add_subparsers(dest="cmd")
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true")
    common.add_argument("--alpha", type=float, default=0.05)
    s = sub.add_parser("size", parents=[common], help="sample size per arm for two proportions")
    s.add_argument("--baseline", type=float, required=True)
    s.add_argument("--mde", type=float, required=True, help="absolute difference to detect")
    s.add_argument("--power", type=float, default=0.8)
    s.add_argument("--two-sided", action="store_true", help="default; accepted for explicitness")
    s.add_argument("--one-sided", action="store_true")
    a = sub.add_parser("analyze", parents=[common], help="two-proportion z-test")
    for f in ("a-success", "a-n", "b-success", "b-n"):
        a.add_argument("--" + f, type=float, required=True)
    m = sub.add_parser("mean", parents=[common], help="Welch t-test on means")
    for f in ("a-mean", "a-sd", "a-n", "b-mean", "b-sd", "b-n"):
        m.add_argument("--" + f, type=float, required=True)
    q = sub.add_parser("sequential", parents=[common], help="group-sequential boundaries")
    q.add_argument("--baseline", type=float, required=True)
    q.add_argument("--mde", type=float, required=True)
    q.add_argument("--looks", type=int, required=True)
    q.add_argument("--power", type=float, default=0.8)
    q.add_argument("--method", choices=("obf", "pocock"), default="obf")
    return p


def render(res: Dict[str, Any]) -> str:
    return "\n".join("%-18s %s" % (k, json.dumps(v) if isinstance(v, (list, dict)) else v)
                     for k, v in res.items())


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = build_parser()
    a = p.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.cmd:
        p.print_usage(sys.stderr)
        return 2
    try:
        _check_p("alpha", a.alpha)
        if a.cmd == "size":
            res = sample_size(a.baseline, a.mde, a.alpha, a.power, not a.one_sided)
        elif a.cmd == "analyze":
            res = analyze_props(a.a_success, a.a_n, a.b_success, a.b_n, a.alpha)
        elif a.cmd == "mean":
            res = welch(a.a_mean, a.a_sd, a.a_n, a.b_mean, a.b_sd, a.b_n, a.alpha)
        else:
            res = sequential(a.baseline, a.mde, a.looks, a.alpha, a.power, a.method)
    except InputError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    if a.json:
        print(json.dumps(res, indent=2))
    elif a.cmd == "sequential":
        print(render({k: v for k, v in res.items() if k != "boundaries"}))
        for r in res["boundaries"]:
            print("  look %(look)d  info %(info_fraction).2f  |z|>=%(z_boundary).3f  p<%(nominal_p).5f  n/arm=%(n_per_arm)d" % r)
    else:
        print(render(res))
    return 0


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows pipes default to the ANSI code page; Claude Code reads UTF-8
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
