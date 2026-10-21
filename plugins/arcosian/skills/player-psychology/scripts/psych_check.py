#!/usr/bin/env python3
"""psych_check.py - player-psychology calculators and an ethics red-line checker.

Subcommands
  discovery  Usability problem-discovery maths: P(seen at least once) = 1-(1-p)^n,
             and participants needed for a target discovery probability.
  moe        Survey margin of error for a proportion, or the sample size needed
             for a target margin (optional finite-population correction).
  alpha      Cronbach's alpha (+ alpha-if-item-deleted, corrected item-total r)
             from a CSV of responses (rows = respondents, columns = items).
  redlines   Static audit of a design contract (.gamestudio/contract.json) against
             the machine-checkable studio red lines in
             skills/player-psychology/references/ethics-and-dark-patterns.md section 6.

Exit codes: 0 ok, 1 check failed, 2 usage/input error.
Stdlib only; Python 3.9+.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
import sys
from pathlib import Path
from statistics import NormalDist
from typing import Any, Dict, List, Optional, Sequence, Tuple


class InputError(ValueError):
    """Malformed user input (maps to exit code 2)."""


# --------------------------------------------------------------------------- discovery

def discovery_probability(p: float, n: int) -> float:
    """Probability that a problem affecting a share p of users is seen at least once in n sessions."""
    if not 0.0 < p < 1.0:
        raise InputError("--p must be strictly between 0 and 1")
    if n < 0:
        raise InputError("--n must be >= 0")
    return 1.0 - (1.0 - p) ** n


def participants_needed(p: float, target: float) -> int:
    """Smallest n with 1-(1-p)^n >= target."""
    if not 0.0 < p < 1.0:
        raise InputError("--p must be strictly between 0 and 1")
    if not 0.0 < target < 1.0:
        raise InputError("--target must be strictly between 0 and 1")
    return int(math.ceil(math.log(1.0 - target) / math.log(1.0 - p) - 1e-12))


# --------------------------------------------------------------------------- margin of error

def z_for(conf: float) -> float:
    if not 0.5 < conf < 1.0:
        raise InputError("--conf must be between 0.5 and 1 (e.g. 0.95)")
    return NormalDist().inv_cdf(1.0 - (1.0 - conf) / 2.0)


def margin_of_error(n: int, p: float = 0.5, conf: float = 0.95, population: Optional[int] = None) -> float:
    if n < 1:
        raise InputError("--n must be >= 1")
    if not 0.0 < p < 1.0:
        raise InputError("--p must be strictly between 0 and 1")
    e = z_for(conf) * math.sqrt(p * (1.0 - p) / n)
    if population:
        if population < n:
            raise InputError("--population must be >= --n")
        if population > 1:
            e *= math.sqrt((population - n) / (population - 1))
    return e


def sample_size(margin: float, p: float = 0.5, conf: float = 0.95, population: Optional[int] = None) -> int:
    if not 0.0 < margin < 1.0:
        raise InputError("--margin must be strictly between 0 and 1 (e.g. 0.05 for +/-5 points)")
    if not 0.0 < p < 1.0:
        raise InputError("--p must be strictly between 0 and 1")
    n0 = z_for(conf) ** 2 * p * (1.0 - p) / margin ** 2
    if population:
        if population < 1:
            raise InputError("--population must be >= 1")
        n0 = n0 / (1.0 + (n0 - 1.0) / population)
    return int(math.ceil(n0 - 1e-9))


# --------------------------------------------------------------------------- Cronbach's alpha

def _variance(xs: Sequence[float]) -> float:
    """Sample variance (n-1)."""
    n = len(xs)
    if n < 2:
        return 0.0
    m = sum(xs) / n
    return sum((x - m) ** 2 for x in xs) / (n - 1)


def _pearson(xs: Sequence[float], ys: Sequence[float]) -> Optional[float]:
    n = len(xs)
    if n < 3:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx <= 0 or syy <= 0:
        return None
    return sxy / math.sqrt(sxx * syy)


def cronbach_alpha(rows: List[List[float]]) -> Optional[float]:
    """rows: respondents x items. Returns None when undefined (k<2 or zero total variance)."""
    if not rows:
        return None
    k = len(rows[0])
    if k < 2:
        return None
    items = [[r[i] for r in rows] for i in range(k)]
    totals = [sum(r) for r in rows]
    var_total = _variance(totals)
    if var_total <= 0:
        return None
    sum_item_var = sum(_variance(col) for col in items)
    return (k / (k - 1.0)) * (1.0 - sum_item_var / var_total)


def parse_response_csv(text: str, reverse: Sequence[int], scale_min: float, scale_max: float
                       ) -> Tuple[List[str], List[List[float]], int]:
    """Parse CSV text. Returns (item names, complete rows after reverse-scoring, dropped row count).

    A non-numeric first row is treated as a header. Rows with blanks or non-numeric
    cells are dropped (listwise deletion). `reverse` holds 1-based item indices.
    """
    reader = csv.reader(io.StringIO(text))
    raw = [r for r in reader if any(c.strip() for c in r)]
    if not raw:
        raise InputError("CSV is empty")

    def numeric(cells: List[str]) -> bool:
        try:
            [float(c) for c in cells]
            return True
        except ValueError:
            return False

    header: List[str]
    if numeric([c.strip() for c in raw[0]]):
        header = ["item%d" % (i + 1) for i in range(len(raw[0]))]
        body = raw
    else:
        header = [c.strip() or "item%d" % (i + 1) for i, c in enumerate(raw[0])]
        body = raw[1:]
    k = len(header)
    if k < 2:
        raise InputError("need at least 2 item columns")
    for idx in reverse:
        if idx < 1 or idx > k:
            raise InputError("--reverse index %d out of range 1..%d" % (idx, k))
    if scale_max <= scale_min:
        raise InputError("--scale-max must be greater than --scale-min")
    rows: List[List[float]] = []
    dropped = 0
    for r in body:
        cells = [c.strip() for c in r]
        if len(cells) != k or any(c == "" for c in cells):
            dropped += 1
            continue
        try:
            vals = [float(c) for c in cells]
        except ValueError:
            dropped += 1
            continue
        if any(v < scale_min or v > scale_max for v in vals):
            raise InputError("value outside [%g, %g] in row %r" % (scale_min, scale_max, cells))
        for idx in reverse:
            vals[idx - 1] = scale_min + scale_max - vals[idx - 1]
        rows.append(vals)
    if len(rows) < 3:
        raise InputError("need at least 3 complete respondent rows (got %d)" % len(rows))
    return header, rows, dropped


def alpha_report(header: List[str], rows: List[List[float]]) -> Dict[str, Any]:
    k = len(header)
    alpha = cronbach_alpha(rows)
    items = []
    for i in range(k):
        rest_rows = [[v for j, v in enumerate(r) if j != i] for r in rows]
        col = [r[i] for r in rows]
        rest_total = [sum(rr) for rr in rest_rows]
        items.append({
            "item": header[i],
            "mean": round(sum(col) / len(col), 3),
            "sd": round(math.sqrt(_variance(col)), 3),
            "corrected_item_total_r": None if _pearson(col, rest_total) is None else round(_pearson(col, rest_total), 3),
            "alpha_if_deleted": None if (k - 1) < 2 or cronbach_alpha(rest_rows) is None else round(cronbach_alpha(rest_rows), 3),
        })
    totals = [sum(r) / k for r in rows]
    return {
        "n": len(rows),
        "k": k,
        "alpha": None if alpha is None else round(alpha, 4),
        "scale_mean": round(sum(totals) / len(totals), 3),
        "scale_sd": round(math.sqrt(_variance(totals)), 3),
        "items": items,
        "interpretation": interpret_alpha(alpha),
    }


def interpret_alpha(alpha: Optional[float]) -> str:
    if alpha is None:
        return "undefined (no variance or fewer than 2 items)"
    if alpha > 0.95:
        return "very high: items may be redundant"
    if alpha >= 0.8:
        return "good"
    if alpha >= 0.7:
        return "acceptable for research use"
    if alpha >= 0.6:
        return "questionable: inspect items"
    return "poor: items do not measure one construct, or reverse-coding is wrong"


# --------------------------------------------------------------------------- red lines

RANDOM_TERMS = ("loot", "gacha", "random", "mystery", "chest", "spin", "lucky", "box", "pull", "summon", "draw")
AGE_TERMS = ("minor", "under 18", "under-18", "18+", "adult", "age gate", "age-gate", "children", "child", "under 16", "teen")
ODDS_TERMS = ("odds", "probabilit", "drop rate", "drop-rate")
URGENCY_TERMS = ("urgency", "countdown", "timer", "scarcity", "limited")
FAILURE_TERMS = ("fail", "loss", "losing", "frustrat", "streak")
SPEND_DIFFICULTY_TERMS = ("difficulty", "matchmaking", "drop rate")
PURCHASE_TERMS = ("iap", "purchase", "buy", "store", "shop", "pack", "offer")


def _text(obj: Any) -> str:
    """Flatten any JSON value to lower-case text for keyword checks."""
    if obj is None:
        return ""
    if isinstance(obj, str):
        return obj.lower()
    try:
        return json.dumps(obj, ensure_ascii=False).lower()
    except (TypeError, ValueError):
        return str(obj).lower()


def _has_any(text: str, terms: Sequence[str]) -> bool:
    return any(t in text for t in terms)


def _price(value: Any) -> Optional[float]:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip().lstrip("$"))
        except ValueError:
            return None
    return None


def check_redlines(contract: Dict[str, Any]) -> List[Dict[str, str]]:
    """Return findings: dicts with id, rule, level (fail|warn), message."""
    findings: List[Dict[str, str]] = []

    def add(fid: str, rule: str, level: str, msg: str) -> None:
        findings.append({"id": fid, "rule": rule, "level": level, "message": msg})

    meta = contract.get("meta") or {}
    audience = meta.get("target_audience") or {}
    age_min = audience.get("age_min")
    model = (meta.get("monetization_model") or "").lower()
    mon = contract.get("monetization") or {}
    ethics_list = mon.get("ethics") or []
    if isinstance(ethics_list, str):
        ethics_list = [ethics_list]
    ethics_text = " | ".join(str(e) for e in ethics_list).lower()
    iaps = mon.get("iap") or []
    ads = mon.get("ads") or {}
    currencies = ((contract.get("economy") or {}).get("currencies")) or []
    ftue_steps = ((contract.get("ftue") or {}).get("steps")) or []

    monetized = model not in ("", "premium") or bool(iaps) or bool(ads)

    # C01 ethics list present
    if monetized and not ethics_list:
        add("C01", "doctrine-8", "fail", "monetization.ethics is empty; copy the applicable red lines (RL-xx) into it")

    # C02 age
    if age_min is None:
        add("C02", "RL-01/RL-17", "warn", "meta.target_audience.age_min is missing; minors' protections cannot be checked")

    # C03 paid random items
    paid_random = []
    for item in iaps if isinstance(iaps, list) else []:
        if not isinstance(item, dict):
            continue
        blob = _text({k: item.get(k) for k in ("id", "type", "contents")})
        price = _price(item.get("price_tier"))
        if _has_any(blob, RANDOM_TERMS) and (price is None or price > 0):
            paid_random.append(str(item.get("id")))
    if paid_random:
        if not _has_any(ethics_text, ODDS_TERMS):
            add("C03", "RL-02", "fail",
                "paid random item(s) %s but no ethics rule about odds disclosure" % ", ".join(paid_random))
        adult_only = isinstance(age_min, int) and age_min >= 18
        age_gated = _has_any(ethics_text, AGE_TERMS) and _has_any(ethics_text, RANDOM_TERMS + ODDS_TERMS)
        if not adult_only and not age_gated:
            add("C04", "RL-01", "fail",
                "paid random item(s) %s with age_min %r and no ethics rule disabling them for minors/unknown age"
                % (", ".join(paid_random), age_min))

    # C05 premium currencies
    premium = []
    for c in currencies if isinstance(currencies, list) else []:
        if isinstance(c, dict) and str(c.get("kind", "")).lower() in ("hard", "premium"):
            sources = _text(c.get("sources"))
            if not sources or _has_any(sources, PURCHASE_TERMS):
                premium.append(str(c.get("id")))
    if len(premium) > 1:
        add("C05", "RL-07", "fail", "more than one purchasable premium currency: %s" % ", ".join(premium))

    # C06/C07 interstitial pacing
    inter = ads.get("interstitial") if isinstance(ads, dict) else None
    if isinstance(inter, dict):
        first = inter.get("first_after_sec")
        interval = inter.get("min_interval_sec")
        ftue_sec = 0.0
        for s in ftue_steps if isinstance(ftue_steps, list) else []:
            if isinstance(s, dict) and isinstance(s.get("max_seconds"), (int, float)):
                ftue_sec += float(s["max_seconds"])
        floor = max(300.0, ftue_sec)
        if not isinstance(first, (int, float)):
            add("C06", "RL-14", "fail", "interstitials configured without first_after_sec (FTUE protection)")
        elif first < floor:
            add("C06", "RL-14", "fail",
                "interstitial first_after_sec=%g is below the floor %g s (max of 300 s and summed FTUE step limits)"
                % (first, floor))
        if not isinstance(interval, (int, float)):
            add("C07", "RL-14", "warn", "interstitial min_interval_sec missing")
        elif interval < 120:
            add("C07", "RL-14", "warn", "interstitial min_interval_sec=%g s is aggressive (< 120 s)" % interval)
        if isinstance(age_min, int) and age_min < 13:
            add("C08", "minors", "fail", "interstitial ads configured for an under-13 audience (protections matrix: off)")

    # C09 rewarded ads caps
    rewarded = ads.get("rewarded") if isinstance(ads, dict) else None
    for r in rewarded if isinstance(rewarded, list) else []:
        if isinstance(r, dict) and r.get("cap_per_day") is None:
            add("C09", "RL-14", "warn", "rewarded placement %r has no cap_per_day" % r.get("id"))

    # C10 topic coverage of the ethics list
    if monetized and ethics_list:
        coverage = [
            ("RL-04", URGENCY_TERMS, "fake urgency/scarcity"),
            ("RL-05", FAILURE_TERMS, "no offers triggered by failure or loss"),
            ("RL-09", SPEND_DIFFICULTY_TERMS, "difficulty/drop rates independent of spending"),
            ("RL-17", AGE_TERMS, "protections for minors"),
        ]
        for rule, terms, label in coverage:
            if not _has_any(ethics_text, terms):
                add("C10", rule, "warn", "ethics list does not mention: %s" % label)

    # C11 limited-time offers need a truthful-timer rule
    for item in iaps if isinstance(iaps, list) else []:
        if isinstance(item, dict) and _has_any(_text(item), ("limited", "countdown", "timer", "flash")):
            if not _has_any(ethics_text, URGENCY_TERMS):
                add("C11", "RL-04", "warn", "offer %r looks time-limited; add a truthful-timer rule" % item.get("id"))

    return findings


# --------------------------------------------------------------------------- output helpers

def emit(data: Dict[str, Any], as_json: bool, lines: List[str]) -> None:
    if as_json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print("\n".join(lines))


def _parse_index_list(text: Optional[str]) -> List[int]:
    if not text:
        return []
    try:
        return [int(x) for x in text.split(",") if x.strip()]
    except ValueError:
        raise InputError("--reverse expects comma-separated 1-based item indices, e.g. 3,5")


# --------------------------------------------------------------------------- commands

def cmd_discovery(a: argparse.Namespace) -> int:
    out: Dict[str, Any] = {"p": a.p}
    lines = []
    if a.n is not None:
        prob = discovery_probability(a.p, a.n)
        out.update({"n": a.n, "probability_seen": round(prob, 4)})
        lines.append("With n=%d and problem frequency p=%.3f: P(seen at least once) = %.1f%%" % (a.n, a.p, 100 * prob))
    target = a.target if a.target is not None else (0.85 if a.n is None else None)
    if target is not None:
        need = participants_needed(a.p, target)
        out.update({"target": target, "participants_needed": need})
        lines.append("Participants needed for %.0f%% chance to see a p=%.3f problem: %d" % (100 * target, a.p, need))
    lines.append("Rule: 5-8 per segment per round; run several rounds; report 'x of n', not percentages.")
    emit(out, a.json, lines)
    return 0


def cmd_moe(a: argparse.Namespace) -> int:
    if (a.n is None) == (a.margin is None):
        raise InputError("give exactly one of --n or --margin")
    out: Dict[str, Any] = {"p": a.p, "conf": a.conf, "population": a.population}
    if a.n is not None:
        e = margin_of_error(a.n, a.p, a.conf, a.population)
        out.update({"n": a.n, "margin": round(e, 4)})
        lines = ["n=%d -> margin of error +/- %.1f points at %.0f%% confidence (p=%.2f)%s"
                 % (a.n, 100 * e, 100 * a.conf, a.p, ", FPC applied" if a.population else "")]
    else:
        n = sample_size(a.margin, a.p, a.conf, a.population)
        out.update({"margin": a.margin, "n": n})
        lines = ["margin +/- %.1f points at %.0f%% confidence (p=%.2f) -> n = %d%s"
                 % (100 * a.margin, 100 * a.conf, a.p, n, " (FPC, N=%d)" % a.population if a.population else "")]
    lines.append("Margins apply per subgroup; non-response bias usually matters more than n.")
    emit(out, a.json, lines)
    return 0


def cmd_alpha(a: argparse.Namespace) -> int:
    path = Path(a.csv)
    if not path.is_file():
        raise InputError("CSV not found: %s" % path)
    header, rows, dropped = parse_response_csv(path.read_text(encoding="utf-8"), _parse_index_list(a.reverse),
                                               a.scale_min, a.scale_max)
    rep = alpha_report(header, rows)
    rep["dropped_rows"] = dropped
    lines = ["Cronbach's alpha = %s (%s); n=%d respondents, k=%d items, dropped %d incomplete rows"
             % ("n/a" if rep["alpha"] is None else "%.3f" % rep["alpha"], rep["interpretation"], rep["n"], rep["k"], dropped),
             "%-20s %7s %7s %10s %10s" % ("item", "mean", "sd", "item-tot r", "a-if-del")]
    for it in rep["items"]:
        lines.append("%-20s %7.2f %7.2f %10s %10s" % (it["item"][:20], it["mean"], it["sd"],
                                                     "-" if it["corrected_item_total_r"] is None else "%.2f" % it["corrected_item_total_r"],
                                                     "-" if it["alpha_if_deleted"] is None else "%.2f" % it["alpha_if_deleted"]))
    failed = a.fail_below is not None and (rep["alpha"] is None or rep["alpha"] < a.fail_below)
    rep["passed"] = not failed
    emit(rep, a.json, lines)
    return 1 if failed else 0


def cmd_redlines(a: argparse.Namespace) -> int:
    path = Path(a.contract)
    if not path.is_file():
        raise InputError("contract not found: %s" % path)
    try:
        contract = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise InputError("contract is not valid JSON: %s" % exc)
    if not isinstance(contract, dict):
        raise InputError("contract must be a JSON object")
    findings = check_redlines(contract)
    fails = [f for f in findings if f["level"] == "fail"]
    warns = [f for f in findings if f["level"] == "warn"]
    failed = bool(fails) or (a.strict and bool(warns))
    out = {"contract": str(path), "fails": len(fails), "warnings": len(warns), "findings": findings,
           "passed": not failed,
           "note": "Static checks only; the full review (ethics-and-dark-patterns.md section 11) still applies."}
    lines = ["red-line check: %s - %d fail, %d warn" % ("PASS" if not failed else "FAIL", len(fails), len(warns))]
    for f in findings:
        lines.append("  [%s] %s %s: %s" % (f["level"].upper(), f["id"], f["rule"], f["message"]))
    lines.append("Static checks only; run the full ethics review before sign-off.")
    emit(out, a.json, lines)
    return 1 if failed else 0


# --------------------------------------------------------------------------- selftest

def selftest() -> int:
    checks = [0]

    def ok(cond: bool, msg: str) -> None:
        checks[0] += 1
        if not cond:
            raise AssertionError(msg)

    # discovery
    ok(abs(discovery_probability(0.31, 5) - 0.8436) < 1e-3, "five users at p=0.31 ~ 84%")
    ok(participants_needed(0.31, 0.85) == 6, "p=.31 target .85 -> 6")
    ok(participants_needed(0.10, 0.85) == 19, "p=.10 target .85 -> 19")
    ok(participants_needed(0.05, 0.95) == 59, "p=.05 target .95 -> 59")
    # moe
    ok(sample_size(0.05) == 385, "n for +/-5 at 95% = 385")
    ok(sample_size(0.10) == 97, "n for +/-10 = 97")
    ok(sample_size(0.03) == 1068, "n for +/-3 = 1068")
    ok(sample_size(0.05, population=2000) == 323, "FPC 2000 -> 323")
    ok(abs(margin_of_error(100) - 0.098) < 1e-3, "moe n=100 ~ 9.8 points")
    # alpha: perfectly parallel items -> alpha 1; known small example
    rows = [[1, 1, 1], [2, 2, 2], [3, 3, 3], [4, 4, 4]]
    ok(abs((cronbach_alpha(rows) or 0) - 1.0) < 1e-9, "parallel items alpha=1")
    rows2 = [[3, 4, 3], [5, 5, 4], [2, 3, 2], [4, 4, 5], [1, 2, 1]]
    a2 = cronbach_alpha(rows2) or 0
    ok(abs(a2 - 0.95376) < 1e-4, "alpha example ~0.9538 (got %.4f)" % a2)
    csv_text = "q1,q2,q3\n3,4,3\n5,5,4\n2,3,2\n4,4,5\n1,2,1\n,3,3\n"
    header, prow, dropped = parse_response_csv(csv_text, [], 1, 5)
    ok(header == ["q1", "q2", "q3"] and len(prow) == 5 and dropped == 1, "csv header + listwise deletion")
    rev_text = "3,2,3\n5,1,4\n2,3,2\n4,2,5\n1,4,1\n"
    _, rrows, _ = parse_response_csv(rev_text, [2], 1, 5)
    ok(abs((cronbach_alpha(rrows) or 0) - a2) < 1e-9, "reverse-coding restores alpha")
    rep = alpha_report(header, prow)
    ok(rep["k"] == 3 and rep["items"][0]["alpha_if_deleted"] is not None, "alpha report fields")
    try:
        parse_response_csv("1,2\n2,3\n", [], 1, 5)
        ok(False, "too few rows should raise")
    except InputError:
        ok(True, "")

    # redlines: clean contract passes
    clean = {
        "meta": {"monetization_model": "hybrid", "target_audience": {"age_min": 13}},
        "economy": {"currencies": [{"id": "coins", "kind": "soft"}, {"id": "gems", "kind": "hard", "sources": ["IAP"]}]},
        "ftue": {"steps": [{"id": "a", "max_seconds": 30}, {"id": "b", "max_seconds": 90}]},
        "monetization": {
            "iap": [{"id": "gems_s", "type": "currency_pack", "price_tier": 4.99, "contents": {"gems": 300}}],
            "ads": {"rewarded": [{"id": "double", "cap_per_day": 10}],
                    "interstitial": {"min_interval_sec": 240, "first_after_sec": 1200}},
            "ethics": ["No fake countdowns or false scarcity", "No offers triggered by failure or loss",
                       "Difficulty never depends on spending", "Minors get no targeted offers"],
        },
    }
    f_clean = check_redlines(clean)
    ok(not any(f["level"] == "fail" for f in f_clean), "clean contract has no fails: %r" % f_clean)
    ok(not f_clean, "clean contract has no warnings either: %r" % f_clean)

    dirty = json.loads(json.dumps(clean))
    dirty["monetization"]["iap"].append({"id": "mystery_chest", "type": "offer", "price_tier": 2.99,
                                         "contents": "random hero chest"})
    dirty["monetization"]["ads"]["interstitial"]["first_after_sec"] = 60
    dirty["economy"]["currencies"].append({"id": "crystals", "kind": "premium", "sources": ["shop packs"]})
    ids = {f["id"] for f in check_redlines(dirty) if f["level"] == "fail"}
    ok({"C03", "C04", "C05", "C06"} <= ids, "dirty contract triggers C03-C06: %r" % ids)

    kids = json.loads(json.dumps(clean))
    kids["meta"]["target_audience"]["age_min"] = 8
    ok("C08" in {f["id"] for f in check_redlines(kids)}, "under-13 interstitials flagged")

    empty_eth = json.loads(json.dumps(clean))
    empty_eth["monetization"]["ethics"] = []
    ok("C01" in {f["id"] for f in check_redlines(empty_eth)}, "empty ethics flagged")

    adult_random = json.loads(json.dumps(dirty))
    adult_random["meta"]["target_audience"]["age_min"] = 18
    adult_random["monetization"]["ethics"].append("Odds shown before every paid draw")
    ids2 = {f["id"] for f in check_redlines(adult_random) if f["level"] == "fail"}
    ok("C03" not in ids2 and "C04" not in ids2, "adult game with odds rule passes C03/C04: %r" % ids2)

    # bundled example contract (if present): informational only, so another file's edits never break this selftest
    example = Path(__file__).resolve().parents[3] / "scripts" / "schemas" / "examples" / "example.design-contract.json"
    if example.is_file():
        try:
            ex = json.loads(example.read_text(encoding="utf-8"))
            ex_fails = [f for f in check_redlines(ex) if f["level"] == "fail"] if isinstance(ex, dict) else []
            print("note: example contract red-line fails: %d" % len(ex_fails))
        except (OSError, ValueError) as exc:
            print("note: example contract not checked (%s)" % exc)

    print("selftest ok (%d checks)" % checks[0])
    return 0


# --------------------------------------------------------------------------- CLI

def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--selftest", action="store_true", help="run built-in fixtures and exit")
    sub = ap.add_subparsers(dest="cmd")

    d = sub.add_parser("discovery", help="usability problem-discovery maths")
    d.add_argument("--p", type=float, required=True, help="share of users affected by the problem (0-1)")
    d.add_argument("--n", type=int, help="participants planned")
    d.add_argument("--target", type=float, help="target probability of seeing the problem (default 0.85 when --n absent)")
    d.add_argument("--json", action="store_true")

    m = sub.add_parser("moe", help="survey margin of error / sample size")
    m.add_argument("--n", type=int, help="sample size -> margin")
    m.add_argument("--margin", type=float, help="target margin (0.05 = +/-5 points) -> sample size")
    m.add_argument("--p", type=float, default=0.5, help="expected proportion (default 0.5, worst case)")
    m.add_argument("--conf", type=float, default=0.95, help="confidence level (default 0.95)")
    m.add_argument("--population", type=int, help="finite population size for correction")
    m.add_argument("--json", action="store_true")

    al = sub.add_parser("alpha", help="Cronbach's alpha from a CSV of item responses")
    al.add_argument("--csv", required=True, help="rows = respondents, columns = items; optional header row")
    al.add_argument("--reverse", help="comma-separated 1-based indices of reverse-scored items")
    al.add_argument("--scale-min", type=float, default=1.0)
    al.add_argument("--scale-max", type=float, default=7.0)
    al.add_argument("--fail-below", type=float, help="exit 1 if alpha is below this value (e.g. 0.7)")
    al.add_argument("--json", action="store_true")

    r = sub.add_parser("redlines", help="static red-line audit of a design contract")
    r.add_argument("--contract", required=True, help="path to .gamestudio/contract.json")
    r.add_argument("--strict", action="store_true", help="treat warnings as failures")
    r.add_argument("--json", action="store_true")
    return ap


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = build_parser()
    args = ap.parse_args(argv)
    if args.selftest:
        try:
            return selftest()
        except AssertionError as exc:
            print("selftest FAILED: %s" % exc, file=sys.stderr)
            return 1
    if not args.cmd:
        ap.print_help(sys.stderr)
        return 2
    try:
        return {"discovery": cmd_discovery, "moe": cmd_moe, "alpha": cmd_alpha, "redlines": cmd_redlines}[args.cmd](args)
    except InputError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows pipes default to the ANSI code page; Claude Code reads UTF-8
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
