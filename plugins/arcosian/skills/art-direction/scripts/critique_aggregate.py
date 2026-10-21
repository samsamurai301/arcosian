#!/usr/bin/env python3
"""critique_aggregate.py - combine several visual-critique passes into one gate verdict.

VLM reviewers produce false positives and drifting scores, so the visual gate
never trusts one pass. Run the rubric 3+ times (different samples, different
models, or different crops), then aggregate here:
  * per-criterion MEDIAN of 1-5 anchored scores (robust to one outlier),
  * weighted total (default weights: readability .30, consistency .25,
    technical .20, appeal .15, polish .10),
  * defect flags CONFIRMED only when at least --quorum of reviewers (default
    2/3, minimum 2) report the same flag id at the same location,
  * a pass/fail verdict from tier presets, plus a needs_human list
    (unconfirmed blockers, criteria where reviewers disagree by >= 2 points).

Input JSON:
  {"subject": "F012 battle screen", "tier": "slice",          # tier optional
   "weights": {"readability": 0.3, ...},                      # optional override
   "reviews": [{"reviewer": "vlm-a",
                "scores": {"readability": 4, "consistency": 3, "technical": 4, "appeal": 3, "polish": 3},
                "flags": [{"id": "text_clipping", "severity": "major", "where": "shop button",
                           "evidence": "shot_02.png", "note": "..."}]}]}
Severities: blocker > major > minor > polish.

Tier presets (override with --floor/--pass-score):
  prototype   floor 2, pass 2.5, confirmed blockers fail
  slice       floor 3, pass 3.5, confirmed blockers and majors fail
  soft_launch / global / live
              floor 3 (readability and technical 4), pass 4.0, blockers and majors fail

Usage: critique_aggregate.py --in reviews.json [--tier T] [--quorum 0.67] [--md OUT.md] [--json]
Exit codes: 0 pass, 1 fail, 2 usage/input error. Stdlib only; Python 3.9+.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

CRITERIA = ("readability", "consistency", "technical", "appeal", "polish")
DEFAULT_WEIGHTS = {"readability": 0.30, "consistency": 0.25, "technical": 0.20, "appeal": 0.15, "polish": 0.10}
SEVERITY_ORDER = {"polish": 0, "minor": 1, "major": 2, "blocker": 3}
TIERS = {
    "prototype": {"floor": 2.0, "pass": 2.5, "fail_sev": {"blocker"}, "floors": {}},
    "slice": {"floor": 3.0, "pass": 3.5, "fail_sev": {"blocker", "major"}, "floors": {}},
    "soft_launch": {"floor": 3.0, "pass": 4.0, "fail_sev": {"blocker", "major"},
                    "floors": {"readability": 4.0, "technical": 4.0}},
}
TIERS["global"] = TIERS["soft_launch"]
TIERS["live"] = TIERS["soft_launch"]


class InputError(ValueError):
    """Malformed input (exit code 2)."""


def _norm(s: object) -> str:
    return " ".join(str(s or "").lower().split())


def aggregate(doc: dict, tier: str = "slice", quorum: float = 2.0 / 3.0,
              floor: Optional[float] = None, pass_score: Optional[float] = None) -> Dict[str, object]:
    reviews = doc.get("reviews")
    if not isinstance(reviews, list) or not reviews:
        raise InputError("input needs a non-empty 'reviews' list")
    if tier not in TIERS:
        raise InputError("unknown tier %r (use %s)" % (tier, ", ".join(sorted(TIERS))))
    preset = TIERS[tier]
    weights = dict(DEFAULT_WEIGHTS)
    weights.update({k: float(v) for k, v in (doc.get("weights") or {}).items()})
    unknown = set(weights) - set(CRITERIA)
    if unknown:
        raise InputError("unknown criteria in weights: %s" % ", ".join(sorted(unknown)))
    n = len(reviews)
    per: Dict[str, List[float]] = defaultdict(list)
    flag_reports: Dict[Tuple[str, str], List[dict]] = defaultdict(list)
    for i, r in enumerate(reviews):
        scores = r.get("scores") or {}
        for c in CRITERIA:
            if c in scores:
                v = float(scores[c])
                if not 1.0 <= v <= 5.0:
                    raise InputError("review %d: %s score %s outside 1-5" % (i + 1, c, v))
                per[c].append(v)
        seen = set()
        for f in r.get("flags") or []:
            fid = _norm(f.get("id"))
            sev = _norm(f.get("severity") or "minor")
            if not fid:
                raise InputError("review %d: flag without id" % (i + 1))
            if sev not in SEVERITY_ORDER:
                raise InputError("review %d: severity %r not in %s" % (i + 1, sev, list(SEVERITY_ORDER)))
            key = (fid, _norm(f.get("where")))
            if key in seen:
                continue
            seen.add(key)
            flag_reports[key].append(dict(f, reviewer=r.get("reviewer", "r%d" % (i + 1)), severity=sev))
    criteria = {}
    needs_human: List[str] = []
    failures: List[str] = []
    total_w = 0.0
    total = 0.0
    floor_v = preset["floor"] if floor is None else floor
    pass_v = preset["pass"] if pass_score is None else pass_score
    for c in CRITERIA:
        vals = per.get(c, [])
        if not vals:
            needs_human.append("no reviewer scored %s" % c)
            continue
        med = statistics.median(vals)
        spread = max(vals) - min(vals)
        crit_floor = max(floor_v, preset["floors"].get(c, 0.0)) if floor is None else floor_v
        criteria[c] = {"median": med, "min": min(vals), "max": max(vals), "n": len(vals),
                       "floor": crit_floor, "ok": med >= crit_floor}
        if spread >= 2:
            needs_human.append("reviewers disagree on %s (scores %s)" % (c, sorted(vals)))
        if med < crit_floor:
            failures.append("%s median %.1f below floor %.1f" % (c, med, crit_floor))
        total += weights.get(c, 0.0) * med
        total_w += weights.get(c, 0.0)
    weighted = round(total / total_w, 2) if total_w else 0.0
    if total_w and weighted < pass_v:
        failures.append("weighted score %.2f below pass %.2f" % (weighted, pass_v))
    need = max(2, int(math.ceil(quorum * n - 1e-9))) if n >= 2 else 1
    confirmed, unconfirmed = [], []
    for (fid, where), reps in sorted(flag_reports.items()):
        sevs = sorted(SEVERITY_ORDER[x["severity"]] for x in reps)
        sev_name = [k for k, v in SEVERITY_ORDER.items() if v == sevs[(len(sevs) - 1) // 2]][0]
        row = {"id": fid, "where": where, "severity": sev_name, "reports": len(reps), "of": n,
               "evidence": sorted({str(x.get("evidence")) for x in reps if x.get("evidence")}),
               "reviewers": [x["reviewer"] for x in reps]}
        if len(reps) >= need:
            confirmed.append(row)
            if sev_name in preset["fail_sev"]:
                failures.append("confirmed %s flag: %s at %s (%d/%d)" % (sev_name, fid, where or "-", len(reps), n))
        else:
            unconfirmed.append(row)
            if max(sevs) >= SEVERITY_ORDER["major"]:
                needs_human.append("unconfirmed %s flag %s at %s (%d/%d) - check by eye" % (
                    [k for k, v in SEVERITY_ORDER.items() if v == max(sevs)][0], fid, where or "-", len(reps), n))
    warnings = []
    if n < 3:
        warnings.append("only %d review(s); use 3+ independent passes for majority voting" % n)
    return {
        "subject": doc.get("subject", ""), "tier": tier, "reviews": n, "quorum_needed": need,
        "weights": weights, "criteria": criteria, "weighted_score": weighted, "pass_score": pass_v,
        "confirmed_flags": confirmed, "unconfirmed_flags": unconfirmed,
        "failures": failures, "needs_human": needs_human, "warnings": warnings,
        "verdict": "fail" if failures else "pass",
    }


def to_markdown(r: Dict[str, object]) -> str:
    out = ["# Visual review: %s" % (r["subject"] or "(unnamed)"), "",
           "- Verdict: **%s** (tier `%s`, %d reviews, flag quorum %d)" % (
               str(r["verdict"]).upper(), r["tier"], r["reviews"], r["quorum_needed"]),
           "- Weighted score: %.2f / 5 (pass at %.2f)" % (r["weighted_score"], r["pass_score"]), "",
           "| Criterion | Median | Range | Floor | OK |", "|---|---|---|---|---|"]
    for c, v in r["criteria"].items():  # type: ignore[union-attr]
        out.append("| %s | %.1f | %.0f-%.0f | %.1f | %s |" % (c, v["median"], v["min"], v["max"], v["floor"],
                                                           "yes" if v["ok"] else "**no**"))
    for title, key in (("Confirmed flags", "confirmed_flags"), ("Unconfirmed flags (single reviewer)", "unconfirmed_flags")):
        rows = r[key]
        out += ["", "## " + title, ""]
        if not rows:
            out.append("None.")
        for f in rows:  # type: ignore[union-attr]
            out.append("- `%s` (%s) at %s: %d/%d reviewers%s" % (
                f["id"], f["severity"], f["where"] or "-", f["reports"], f["of"],
                (" - evidence " + ", ".join(f["evidence"])) if f["evidence"] else ""))
    for title, key in (("Failures", "failures"), ("Needs human eyes", "needs_human"), ("Warnings", "warnings")):
        if r[key]:
            out += ["", "## " + title, ""] + ["- " + str(x) for x in r[key]]  # type: ignore[union-attr]
    return "\n".join(out) + "\n"


def selftest() -> int:
    base = {"subject": "test", "reviews": [
        {"reviewer": "a", "scores": {"readability": 4, "consistency": 4, "technical": 4, "appeal": 3, "polish": 3},
         "flags": [{"id": "text_clipping", "severity": "major", "where": "Shop button"}]},
        {"reviewer": "b", "scores": {"readability": 4, "consistency": 3, "technical": 5, "appeal": 4, "polish": 3},
         "flags": [{"id": "text_clipping", "severity": "major", "where": "shop  button"},
                   {"id": "missing_texture", "severity": "blocker", "where": "golem t3"}]},
        {"reviewer": "c", "scores": {"readability": 5, "consistency": 4, "technical": 4, "appeal": 4, "polish": 2},
         "flags": []}]}
    checks = []
    r = aggregate(base, "slice")
    checks.append(("median readability = 4", r["criteria"]["readability"]["median"] == 4))
    checks.append(("clipping confirmed 2/3", any(f["id"] == "text_clipping" for f in r["confirmed_flags"])))
    checks.append(("single blocker unconfirmed", any(f["id"] == "missing_texture" for f in r["unconfirmed_flags"])))
    checks.append(("unconfirmed blocker -> human", any("missing_texture" in x for x in r["needs_human"])))
    checks.append(("confirmed major fails slice", r["verdict"] == "fail"))
    r2 = aggregate(base, "prototype")
    checks.append(("major does not fail prototype", r2["verdict"] == "pass"))
    checks.append(("weighted = 3.9", abs(r2["weighted_score"] - 3.9) < 0.01))
    r3 = aggregate(base, "global")
    checks.append(("global floor technical 4 ok", r3["criteria"]["technical"]["floor"] == 4.0))
    md = to_markdown(r)
    checks.append(("markdown has verdict", "Verdict: **FAIL**" in md))
    try:
        aggregate({"reviews": [{"scores": {"readability": 7}}]})
        checks.append(("rejects score 7", False))
    except InputError:
        checks.append(("rejects score 7", True))
    ok = True
    for name, passed in checks:
        print("%-36s %s" % (name, "ok" if passed else "FAIL"))
        ok = ok and passed
    print("selftest: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    p.add_argument("--in", dest="inp", help="reviews JSON")
    p.add_argument("--tier", default=None, help="prototype|slice|soft_launch|global|live (default: file or slice)")
    p.add_argument("--quorum", type=float, default=2.0 / 3.0, help="fraction of reviewers to confirm a flag")
    p.add_argument("--floor", type=float, default=None, help="override per-criterion floor")
    p.add_argument("--pass-score", type=float, default=None, help="override weighted pass score")
    p.add_argument("--md", help="also write a markdown report (e.g. evidence/F012/visual_review.md)")
    p.add_argument("--json", action="store_true")
    p.add_argument("--selftest", action="store_true")
    args = p.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.inp:
        print("error: --in is required", file=sys.stderr)
        return 2
    try:
        doc = json.loads(Path(args.inp).read_text(encoding="utf-8"))
        r = aggregate(doc, args.tier or doc.get("tier") or "slice", args.quorum, args.floor, args.pass_score)
    except (OSError, ValueError) as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    md = to_markdown(r)
    if args.md:
        Path(args.md).parent.mkdir(parents=True, exist_ok=True)
        Path(args.md).write_text(md, encoding="utf-8")
    print(json.dumps(r, indent=2) if args.json else md)
    return 0 if r["verdict"] == "pass" else 1


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows pipes default to the ANSI code page; Claude Code reads UTF-8
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
