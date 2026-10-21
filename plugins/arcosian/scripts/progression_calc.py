#!/usr/bin/env python3
"""XP / progression curve tables, cumulative XP and time-to-level.

  progression_calc.py curve --formula linear|poly|exp|logistic|piecewise --levels N
                            [--base B] [--growth G] [--exponent E] [--xp-per-min X] [--json]
  progression_calc.py time-to-level --table PATH --xp-per-min X [--json]
  progression_calc.py --selftest

xp_to_next(L) is the XP needed to go from level L to L+1 (L = 1..N). B = --base (default 100).
  linear     B + G*(L-1)            G = XP added per level      (default 50)
  poly       B * L^E                E = exponent                (default 1.5; G unused)
  exp        B * G^(L-1)            G = per-level multiplier    (default 1.15)
  logistic   B * (1 + 9*S(L))       S = sigmoid(G*(L - N/2)), G = steepness (default 0.25): cost rises ~10x
             through the middle of the game and flattens, an S-shaped curve
  piecewise  exp in three thirds of the game with per-level multiplier 1+(G-1)*w, w = 0.25 / 0.6 / 1.0
             (G default 1.15): gentle onboarding, steeper mid-game, full growth late
With --xp-per-min the table adds minutes to level and cumulative minutes/hours/days at the entered rate.

time-to-level --table reads a JSON file (the output of `curve --json`, a {"levels":[{"xp_to_next":..}]}
object, or a plain list of numbers) or a CSV with a level column and an xp / xp_to_next column.

Exit codes: 0 ok, 2 usage or input error (1 is unused: nothing here can fail a check).
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence

DEFAULT_GROWTH = {"linear": 50.0, "poly": 0.0, "exp": 1.15, "logistic": 0.25, "piecewise": 1.15}


class InputError(Exception):
    pass


def sigmoid(x: float) -> float:
    if x >= 0:
        return 1.0 / (1.0 + math.exp(-x))
    z = math.exp(x)
    return z / (1.0 + z)


def xp_curve(formula: str, levels: int, base: float = 100.0, growth: Optional[float] = None,
             exponent: float = 1.5) -> List[float]:
    """XP needed to go from level L to L+1, for L = 1..levels."""
    if formula not in DEFAULT_GROWTH:
        raise InputError("unknown formula %r" % formula)
    if levels < 1:
        raise InputError("levels must be >= 1")
    if base <= 0:
        raise InputError("base must be > 0")
    g = DEFAULT_GROWTH[formula] if growth is None else growth
    if formula in ("exp", "piecewise") and g <= 0:
        raise InputError("growth multiplier must be > 0")
    out = []  # type: List[float]
    for lv in range(1, levels + 1):
        if formula == "linear":
            x = base + g * (lv - 1)
        elif formula == "poly":
            x = base * lv ** exponent
        elif formula == "exp":
            x = base * g ** (lv - 1)
        elif formula == "logistic":
            x = base * (1.0 + 9.0 * sigmoid(g * (lv - levels / 2.0)))
        else:
            x = base
            for k in range(2, lv + 1):
                w = 0.25 if k <= levels / 3.0 else (0.6 if k <= 2.0 * levels / 3.0 else 1.0)
                x *= 1.0 + (g - 1.0) * w
        if x <= 0:
            raise InputError("curve goes non-positive at level %d (check base/growth)" % lv)
        out.append(x)
    return out


def build_table(xp: List[float], xp_per_min: Optional[float]) -> List[Dict]:
    rows = []  # type: List[Dict]
    cum = 0.0
    cum_min = 0.0
    for i, x in enumerate(xp, 1):
        cum += x
        row = {"level": i, "xp_to_next": round(x, 2), "cumulative_xp": round(cum, 2)}
        if xp_per_min:
            cum_min += x / xp_per_min
            row.update({"minutes_to_next": round(x / xp_per_min, 2), "cumulative_minutes": round(cum_min, 2),
                        "cumulative_hours": round(cum_min / 60.0, 2)})
        rows.append(row)
    return rows


def read_table(path: str) -> List[float]:
    p = Path(path)
    if not p.is_file():
        raise InputError("table not found: %s" % path)
    text = p.read_text(encoding="utf-8")
    try:
        data = json.loads(text)
    except ValueError:
        data = None
    try:
        if data is not None:
            rows = data.get("levels") if isinstance(data, dict) else data
            if not isinstance(rows, list) or not rows:
                raise InputError("JSON table needs a non-empty list or a 'levels' list")
            return [float(r["xp_to_next"] if isinstance(r, dict) else r) for r in rows]
        rd = csv.DictReader(text.splitlines())
        cols = [c.strip().lower() for c in (rd.fieldnames or [])]
        col = next((c for c in ("xp_to_next", "xp", "xp_required") if c in cols), None)
        if col is None:
            raise InputError("CSV needs an xp_to_next (or xp) column")
        vals = [float(r[col]) for r in ({k.strip().lower(): v for k, v in row.items()} for row in rd) if r.get(col)]
    except (KeyError, TypeError, ValueError) as e:
        raise InputError("bad table content: %s" % e)
    if not vals or any(v <= 0 for v in vals):
        raise InputError("table must contain positive XP values")
    return vals


def fmt_dur(minutes: float) -> str:
    if minutes < 90:
        return "%.1f min" % minutes
    if minutes < 48 * 60:
        return "%.1f h" % (minutes / 60.0)
    return "%.1f d" % (minutes / 1440.0)


def print_table(title: str, rows: List[Dict]) -> None:
    timed = "minutes_to_next" in rows[0]
    print(title)
    print("level  xp_to_next  cumulative_xp" + ("  time_to_next  cumulative_time" if timed else ""))
    for r in rows:
        line = "%5d  %10.0f  %13.0f" % (r["level"], r["xp_to_next"], r["cumulative_xp"])
        if timed:
            line += "  %12s  %15s" % (fmt_dur(r["minutes_to_next"]), fmt_dur(r["cumulative_minutes"]))
        print(line)


def cmd_curve(a: argparse.Namespace) -> int:
    if a.xp_per_min is not None and a.xp_per_min <= 0:
        raise InputError("--xp-per-min must be > 0")
    xp = xp_curve(a.formula, a.levels, a.base, a.growth, a.exponent)
    rows = build_table(xp, a.xp_per_min)
    params = {"base": a.base, "growth": DEFAULT_GROWTH[a.formula] if a.growth is None else a.growth,
              "exponent": a.exponent, "xp_per_min": a.xp_per_min}
    if a.json:
        print(json.dumps({"formula": a.formula, "levels": rows, "params": params,
                          "total_xp": rows[-1]["cumulative_xp"]}, indent=2))
    else:
        print_table("XP curve: %s, %d levels (%s)" % (a.formula, a.levels, params), rows)
    return 0


def cmd_time(a: argparse.Namespace) -> int:
    if a.xp_per_min <= 0:
        raise InputError("--xp-per-min must be > 0")
    rows = build_table(read_table(a.table), a.xp_per_min)
    if a.json:
        print(json.dumps({"levels": rows, "total_xp": rows[-1]["cumulative_xp"],
                          "total_hours": rows[-1]["cumulative_hours"]}, indent=2))
    else:
        print_table("Time to level at %.2f XP/min" % a.xp_per_min, rows)
        print("total: %.0f XP, %s" % (rows[-1]["cumulative_xp"], fmt_dur(rows[-1]["cumulative_minutes"])))
    return 0


def selftest() -> int:
    import os
    import tempfile
    lin = xp_curve("linear", 5, base=100, growth=50)
    assert lin == [100, 150, 200, 250, 300], lin
    assert xp_curve("poly", 3, base=10, exponent=2) == [10, 40, 90]
    ex = xp_curve("exp", 4, base=100, growth=2)
    assert ex == [100, 200, 400, 800], ex
    lg = xp_curve("logistic", 20, base=100)
    assert lg == sorted(lg) and 100 < lg[0] < 200 and 900 < lg[-1] <= 1000 and lg[9] < lg[10] < lg[11], lg
    pw = xp_curve("piecewise", 30, base=100, growth=1.2)
    ratios = [pw[i + 1] / pw[i] for i in range(29)]
    assert ratios[0] < ratios[14] < ratios[-1] and abs(ratios[-1] - 1.2) < 1e-9, ratios
    rows = build_table(lin, 10.0)
    assert rows[-1]["cumulative_xp"] == 1000 and rows[-1]["cumulative_minutes"] == 100.0, rows[-1]
    fd, path = tempfile.mkstemp(suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump({"levels": rows}, fh)
        assert read_table(path) == [100, 150, 200, 250, 300]
    finally:
        os.unlink(path)
    fd, path = tempfile.mkstemp(suffix=".csv")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write("level,xp\n1,50\n2,75\n")
        assert read_table(path) == [50, 75]
    finally:
        os.unlink(path)
    try:
        xp_curve("exp", 5, growth=-1)
        raise AssertionError("expected InputError")
    except InputError:
        pass
    print("selftest ok")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Progression curve tables and time-to-level.")
    p.add_argument("--selftest", action="store_true", help="run built-in checks and exit")
    sub = p.add_subparsers(dest="cmd")
    c = sub.add_parser("curve", help="XP curve table")
    c.add_argument("--formula", choices=sorted(DEFAULT_GROWTH), required=True)
    c.add_argument("--levels", type=int, required=True)
    c.add_argument("--base", type=float, default=100.0, help="XP for level 1 -> 2 (default 100)")
    c.add_argument("--growth", type=float, default=None, help="formula-specific growth (see --help header)")
    c.add_argument("--exponent", type=float, default=1.5, help="poly exponent (default 1.5)")
    c.add_argument("--xp-per-min", type=float, default=None, help="add time columns at this XP rate")
    c.add_argument("--json", action="store_true")
    c.set_defaults(fn=cmd_curve)
    t = sub.add_parser("time-to-level", help="time per level from a table")
    t.add_argument("--table", required=True, help="JSON (curve --json output) or CSV")
    t.add_argument("--xp-per-min", type=float, required=True)
    t.add_argument("--json", action="store_true")
    t.set_defaults(fn=cmd_time)
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.cmd:
        print("error: choose curve or time-to-level (or --selftest)", file=sys.stderr)
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
