#!/usr/bin/env python3
"""Retention curve fitting and LTV projection.

  retention_ltv.py fit --points "1:0.42,7:0.18,30:0.07" [--model power|exp] [--json]
  retention_ltv.py ltv --points "..." --arpdau A [--horizon 365] [--json]

power: r(t) = a * t^-b   (log-log least squares)
exp:   r(t) = a * exp(-b t)  (semi-log least squares)
Lifetime days = sum of r(t) for t = 0..horizon with r(0) = 1; LTV = ARPDAU x lifetime days.
Fit, parsing and curve evaluation reuse skills/player-analytics/scripts/analytics_calc.py.
Exit codes: 0 ok, 1 selftest failure, 2 usage/input error.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

HERE = Path(__file__).resolve().parent


def _load(rel: str, name: str):
    spec = importlib.util.spec_from_file_location(name, str(HERE.parent / rel))
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    sys.modules[name] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


_ac = _load("skills/player-analytics/scripts/analytics_calc.py", "analytics_calc_mod")
InputError, parse_points, fit_curve, curve_value = _ac.InputError, _ac.parse_points, _ac.fit_curve, _ac.curve_value

PROJECT_DAYS = (1, 3, 7, 14, 30, 60, 90, 180, 365)


def fit(points: str, model: str) -> Dict[str, Any]:
    pts = parse_points(points)
    a, b, r2 = fit_curve(pts, model)
    proj = {"D%d" % d: round(curve_value(a, b, model, d), 4) for d in PROJECT_DAYS}
    warn: List[str] = []
    if r2 < 0.9:
        warn.append("poor fit (R2 %.2f in log space): try the other model or add points" % r2)
    if len(pts) < 3:
        warn.append("only %d points: the fit is exact, not validated" % len(pts))
    if model == "power" and a > 1:
        warn.append("D1 projected above 100%: check inputs")
    return {"model": model, "a": round(a, 5), "b": round(b, 5), "r2_log": round(r2, 4),
            "points": [{"day": d, "retention": r, "fitted": round(curve_value(a, b, model, int(d)), 4)}
                       for d, r in pts],
            "projection": proj, "warnings": warn}


def ltv(points: str, arpdau: float, horizon: int, model: str) -> Dict[str, Any]:
    if arpdau < 0:
        raise InputError("arpdau must be >= 0")
    if not 1 <= horizon <= 3650:
        raise InputError("horizon must be 1..3650")
    res = fit(points, model)
    a, b, _ = fit_curve(parse_points(points), model)
    life = 0.0
    marks = {}
    for t in range(0, horizon + 1):
        life += curve_value(a, b, model, t)
        if t in (7, 30, 90, 180, 365):
            marks["D%d" % t] = {"lifetime_days": round(life, 3), "ltv": round(life * arpdau, 4)}
    res.update({"arpdau": arpdau, "horizon": horizon, "lifetime_days": round(life, 3),
                "ltv": round(life * arpdau, 4), "ltv_by_day": marks,
                "note": "assumes flat ARPDAU across player age and a smooth tail beyond the last observed day"})
    return res


def selftest() -> int:
    fails: List[str] = []
    # exact power law r = 0.5 * t^-0.5 -> recovered exactly
    pts = ",".join("%d:%.6f" % (t, 0.5 * t ** -0.5) for t in (1, 4, 16, 64))
    r = fit(pts, "power")
    if abs(r["a"] - 0.5) > 1e-4 or abs(r["b"] - 0.5) > 1e-4 or r["r2_log"] < 0.9999:
        fails.append("power fit %s" % r)
    pts = ",".join("%d:%.6f" % (t, 0.4 * math.exp(-0.1 * t)) for t in (1, 3, 7, 14))
    r = fit(pts, "exp")
    if abs(r["a"] - 0.4) > 1e-4 or abs(r["b"] - 0.1) > 1e-4:
        fails.append("exp fit %s" % r)
    # exp lifetime closed form: 1 + sum a e^{-b t}, t=1..H
    l = ltv(pts, 0.1, 365, "exp")
    want = 1 + sum(0.4 * math.exp(-0.1 * t) for t in range(1, 366))
    if abs(l["lifetime_days"] - want) > 0.01 or abs(l["ltv"] - 0.1 * want) > 0.001:
        fails.append("ltv lifetime %s vs %s" % (l["lifetime_days"], want))
    p = fit("1:0.42,7:0.18,30:0.07", "power")
    if not (0.4 < p["projection"]["D1"] < 0.5 and p["projection"]["D365"] < p["projection"]["D90"]):
        fails.append("projection shape %s" % p["projection"])
    try:
        parse_points("1:0.4")
        fails.append("single point accepted")
    except InputError:
        pass
    for f in fails:
        print("FAIL", f)
    print("retention_ltv selftest: %s" % ("FAILED" if fails else "ok"))
    return 1 if fails else 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--selftest", action="store_true")
    sub = p.add_subparsers(dest="cmd")
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--points", required=True, help='"day:rate,..." e.g. "1:0.42,7:0.18,30:0.07"')
    common.add_argument("--model", choices=("power", "exp"), default="power")
    common.add_argument("--json", action="store_true")
    sub.add_parser("fit", parents=[common], help="fit a curve and project D1..D365")
    lt = sub.add_parser("ltv", parents=[common], help="LTV = ARPDAU x lifetime days within horizon")
    lt.add_argument("--arpdau", type=float, required=True)
    lt.add_argument("--horizon", type=int, default=365)
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--selftest" in argv:
        return selftest()
    a = p.parse_args(argv)
    if not a.cmd:
        p.print_usage(sys.stderr)
        return 2
    try:
        res = fit(a.points, a.model) if a.cmd == "fit" else ltv(a.points, a.arpdau, a.horizon, a.model)
    except InputError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    if a.json:
        print(json.dumps(res, indent=2))
        return 0
    print("%s fit: a=%s b=%s R2(log)=%s" % (res["model"], res["a"], res["b"], res["r2_log"]))
    print("projection: " + "  ".join("%s=%.1f%%" % (k, v * 100) for k, v in res["projection"].items()))
    if a.cmd == "ltv":
        print("lifetime days (D0..D%d): %s   LTV = %s x %s = %s" % (
            res["horizon"], res["lifetime_days"], res["arpdau"], res["lifetime_days"], res["ltv"]))
    for w in res["warnings"]:
        print("warning:", w)
    return 0


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows pipes default to the ANSI code page; Claude Code reads UTF-8
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
