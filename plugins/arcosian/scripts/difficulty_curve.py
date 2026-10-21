#!/usr/bin/env python3
"""Target win-rate curves and telemetry analysis for level difficulty.

  difficulty_curve.py generate --levels N --pattern linear|sawtooth|stepped --base WINRATE --floor WINRATE
                               [--period P] [--hard-every K] [--json]
  difficulty_curve.py analyze  --data CSV(level,attempts,wins,churned) [--json]
  difficulty_curve.py --selftest

Patterns (win rate of an average player on the first attempt of each level):
  linear    base falls straight to floor across all levels.
  sawtooth  each tooth of --period levels ramps from base to the midpoint of base and floor, then resets;
            a hard level every K (default: period) drops to floor (the "boss" at the end of a tooth).
  stepped   plateaus of --period levels, stepping from base to floor.
--hard-every also applies to linear and stepped when given. Every rate is clamped to [floor, 1].

analyze flags, per level, compared with the median of up to 3 neighbours on each side:
  win_rate_dip  win rate at least 0.15 below the neighbours;
  churn_spike   churn rate at least double the neighbours (and +0.03 or more);
and recommends a re-tune target. Levels with fewer than 30 attempts are noted but never flagged.
economy_sim.py imports gen_curve() from this file.

Exit codes: 0 ok / nothing flagged, 1 levels flagged, 2 usage or input error.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence

MIN_ATTEMPTS = 30
DIP = 0.15
CHURN_ABS = 0.03


class InputError(Exception):
    pass


def gen_curve(levels: int, pattern: str, base: float, floor: float, period: int = 10,
              hard_every: int = 0) -> List[float]:
    if levels < 1:
        raise InputError("levels must be >= 1")
    if not (0.0 < floor <= base <= 1.0):
        raise InputError("need 0 < floor <= base <= 1 (got base=%s floor=%s)" % (base, floor))
    if period < 1:
        raise InputError("period must be >= 1")
    if pattern not in ("linear", "sawtooth", "stepped"):
        raise InputError("unknown pattern %r" % pattern)
    if pattern == "sawtooth" and hard_every <= 0:
        hard_every = period
    mid = base - 0.5 * (base - floor)
    nsteps = int(math.ceil(levels / period))
    out = []  # type: List[float]
    for lv in range(1, levels + 1):
        if pattern == "linear":
            r = base - (base - floor) * ((lv - 1) / (levels - 1) if levels > 1 else 0.0)
        elif pattern == "sawtooth":
            i = (lv - 1) % period
            r = base - (base - mid) * (i / (period - 1) if period > 1 else 0.0)
        else:
            s = (lv - 1) // period
            r = base - (base - floor) * (s / (nsteps - 1) if nsteps > 1 else 0.0)
        if hard_every > 0 and lv % hard_every == 0:
            r = floor
        out.append(round(max(floor, min(1.0, r)), 4))
    return out


def median(vals: Sequence[float]) -> float:
    s = sorted(vals)
    n = len(s)
    return s[n // 2] if n % 2 else 0.5 * (s[n // 2 - 1] + s[n // 2])


def read_telemetry(path: str) -> List[Dict]:
    p = Path(path)
    if not p.is_file():
        raise InputError("data file not found: %s" % path)
    merged = {}  # type: Dict[int, Dict]
    with p.open(newline="", encoding="utf-8") as fh:
        rd = csv.DictReader(fh)
        cols = [c.strip().lower() for c in (rd.fieldnames or [])]
        missing = [c for c in ("level", "attempts", "wins", "churned") if c not in cols]
        if missing:
            raise InputError("CSV needs columns level,attempts,wins,churned (missing %s)" % ",".join(missing))
        for n, raw in enumerate(rd, start=2):
            row = {k.strip().lower(): (v or "").strip() for k, v in raw.items() if k}
            if not any(row.values()):
                continue
            try:
                lv, at, wi, ch = (int(float(row[c])) for c in ("level", "attempts", "wins", "churned"))
            except ValueError:
                raise InputError("line %d: non-numeric value" % n)
            if at < 0 or wi < 0 or ch < 0 or wi > at:
                raise InputError("line %d: need 0 <= wins <= attempts and churned >= 0" % n)
            m = merged.setdefault(lv, {"level": lv, "attempts": 0, "wins": 0, "churned": 0})
            m["attempts"] += at
            m["wins"] += wi
            m["churned"] += ch
    rows = [merged[k] for k in sorted(merged) if merged[k]["attempts"] > 0]
    if not rows:
        raise InputError("no usable rows in %s" % path)
    return rows


def analyze(rows: List[Dict]) -> Dict:
    for r in rows:
        r["win_rate"] = r["wins"] / r["attempts"]
        r["churn_rate"] = r["churned"] / r["attempts"]
    levels = []  # type: List[Dict]
    flags = []  # type: List[Dict]
    for i, r in enumerate(rows):
        nb = [rows[j] for j in range(max(0, i - 3), min(len(rows), i + 4)) if j != i]
        ref_w = median([x["win_rate"] for x in nb]) if len(nb) >= 2 else None
        ref_c = median([x["churn_rate"] for x in nb]) if len(nb) >= 2 else None
        issues = []  # type: List[str]
        if r["attempts"] < MIN_ATTEMPTS:
            issues.append("low_sample")
        elif ref_w is not None:
            if ref_w - r["win_rate"] >= DIP:
                issues.append("win_rate_dip")
            if r["churn_rate"] >= max(2 * ref_c, ref_c + CHURN_ABS) and r["churn_rate"] >= CHURN_ABS:
                issues.append("churn_spike")
        entry = {"level": r["level"], "attempts": r["attempts"], "win_rate": round(r["win_rate"], 4),
                 "churn_rate": round(r["churn_rate"], 4),
                 "neighbour_win_rate": None if ref_w is None else round(ref_w, 4),
                 "neighbour_churn_rate": None if ref_c is None else round(ref_c, 4), "issues": issues}
        real = [x for x in issues if x != "low_sample"]
        if real and ref_w is not None:
            w = r["win_rate"]
            target = max(w, ref_w - 0.05) if "win_rate_dip" in real else min(ref_w, w + 0.10)
            target = round(min(target, 0.95), 2)
            old = (1.0 / w) if w > 0 else float("inf")
            entry["recommendation"] = {
                "target_win_rate": target,
                "attempts_per_win": "%s -> %.1f" % ("inf" if w == 0 else "%.1f" % old, 1.0 / target),
                "action": "Re-tune toward %.2f win rate (ease obstacles, add moves/lives, or add an assist after "
                          "repeated losses). If this is a deliberate hard level, keep it but add a pity/assist after "
                          "3-5 fails and place a reward level right after it." % target}
            flags.append(entry)
        levels.append(entry)
    att = sum(r["attempts"] for r in rows)
    return {"levels": levels, "flagged": [f["level"] for f in flags],
            "summary": {"levels": len(rows), "attempts": att,
                        "win_rate": round(sum(r["wins"] for r in rows) / att, 4),
                        "churned": sum(r["churned"] for r in rows)},
            "ok": not flags}


def cmd_generate(a: argparse.Namespace) -> int:
    rates = gen_curve(a.levels, a.pattern, a.base, a.floor, a.period, a.hard_every)
    res = {"pattern": a.pattern, "levels": a.levels,
           "params": {"base": a.base, "floor": a.floor, "period": a.period, "hard_every": a.hard_every},
           "win_rates": rates, "expected_attempts": [round(1 / r, 2) for r in rates],
           "summary": {"mean": round(sum(rates) / len(rates), 4), "min": min(rates), "max": max(rates)}}
    if a.json:
        print(json.dumps(res, indent=2))
        return 0
    print("Target win-rate curve: %s, %d levels (base %.2f, floor %.2f, period %d, hard every %d)"
          % (a.pattern, a.levels, a.base, a.floor, a.period, a.hard_every))
    print("level  win%   attempts/win")
    for i, r in enumerate(rates, 1):
        print("%5d  %4.0f%%  %5.2f  %s" % (i, r * 100, 1 / r, "#" * int(round(r * 40))))
    print("mean %.3f  min %.3f  max %.3f" % (res["summary"]["mean"], res["summary"]["min"], res["summary"]["max"]))
    return 0


def cmd_analyze(a: argparse.Namespace) -> int:
    res = analyze(read_telemetry(a.data))
    if a.json:
        print(json.dumps(res, indent=2))
        return 0 if res["ok"] else 1
    s = res["summary"]
    print("Telemetry: %d levels, %d attempts, win rate %.1f%%, %d churned" %
          (s["levels"], s["attempts"], s["win_rate"] * 100, s["churned"]))
    print("level attempts  win%  churn%  neighbours(win%/churn%)  issues")
    for e in res["levels"]:
        nw = "-" if e["neighbour_win_rate"] is None else "%.0f/%.1f" % (e["neighbour_win_rate"] * 100,
                                                                      e["neighbour_churn_rate"] * 100)
        print("%5d %8d %5.1f %6.1f  %-22s  %s" % (e["level"], e["attempts"], e["win_rate"] * 100,
                                                   e["churn_rate"] * 100, nw, ",".join(e["issues"])))
    for e in res["levels"]:
        if "recommendation" in e:
            print("RE-TUNE level %d: %s (attempts/win %s)" % (e["level"], e["recommendation"]["action"],
                                                              e["recommendation"]["attempts_per_win"]))
    print("OK: no spikes" if res["ok"] else "FLAGGED levels: %s" % res["flagged"])
    return 0 if res["ok"] else 1


def selftest() -> int:
    import os
    import tempfile
    lin = gen_curve(10, "linear", 0.9, 0.5)
    assert lin[0] == 0.9 and lin[-1] == 0.5 and lin == sorted(lin, reverse=True), lin
    saw = gen_curve(30, "sawtooth", 0.85, 0.45, period=10, hard_every=10)
    assert saw[9] == saw[19] == saw[29] == 0.45 and saw[10] == 0.85 and saw[8] > 0.45, saw
    st = gen_curve(30, "stepped", 0.8, 0.5, period=10)
    assert st[0] == st[9] == 0.8 and st[10] == st[19] == 0.65 and st[29] == 0.5, st
    assert min(gen_curve(50, "linear", 0.9, 0.6, hard_every=7)) == 0.6
    try:
        gen_curve(5, "linear", 0.4, 0.6)
        raise AssertionError("expected InputError")
    except InputError:
        pass
    lines = ["level,attempts,wins,churned"]
    for lv in range(1, 21):
        wins, ch = (60, 2) if lv != 12 else (18, 25)
        lines.append("%d,100,%d,%d" % (lv, wins, ch))
    fd, path = tempfile.mkstemp(suffix=".csv")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))
        res = analyze(read_telemetry(path))
    finally:
        os.unlink(path)
    assert res["flagged"] == [12] and not res["ok"], res["flagged"]
    rec = [e for e in res["levels"] if e["level"] == 12][0]["recommendation"]
    assert 0.5 <= rec["target_win_rate"] <= 0.6, rec
    print("selftest ok")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Difficulty curve generator and telemetry analyzer.")
    p.add_argument("--selftest", action="store_true", help="run built-in checks and exit")
    sub = p.add_subparsers(dest="cmd")
    g = sub.add_parser("generate", help="generate a target win-rate curve")
    g.add_argument("--levels", type=int, required=True)
    g.add_argument("--pattern", choices=["linear", "sawtooth", "stepped"], required=True)
    g.add_argument("--base", type=float, required=True, help="starting win rate, 0-1")
    g.add_argument("--floor", type=float, required=True, help="lowest allowed win rate, 0-1")
    g.add_argument("--period", type=int, default=10, help="levels per tooth/step (default 10)")
    g.add_argument("--hard-every", type=int, default=0, help="every K-th level drops to floor")
    g.add_argument("--json", action="store_true")
    g.set_defaults(fn=cmd_generate)
    n = sub.add_parser("analyze", help="analyze telemetry CSV")
    n.add_argument("--data", required=True, help="CSV with level,attempts,wins,churned")
    n.add_argument("--json", action="store_true")
    n.set_defaults(fn=cmd_analyze)
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.cmd:
        print("error: choose generate or analyze (or --selftest)", file=sys.stderr)
        return 2
    try:
        return args.fn(args)
    except InputError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows pipes default to the ANSI code page; Claude Code reads UTF-8
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
