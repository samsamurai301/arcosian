#!/usr/bin/env python3
"""perf_budget.py - frame-time statistics and perf-budget verdict.

--report accepts:
  * CSV of frame times in ms: one column, or a header with a frame-time column
    (frame_ms | frametime | frame_time | ms | dt_ms); otherwise the last numeric column is used.
  * perf-report JSON (perf-report.schema.json): uses "frames_ms" (list) if present to recompute
    statistics, else the reported fps / frame_ms / memory_mb / download_mb / cold_start_sec values.

Metrics: avg fps = 1000 / mean frame ms; 1% low = fps of the mean of the slowest 1% of frames;
p50/p95/p99 ms (linear interpolation); jank = frames slower than 2x the median frame time.

Budgets come from --contract (contract.technical.perf_budgets) or the report's own "budgets":
  fps_target       avg fps must be >= 0.95 x target (5% tolerance for capture noise)
  frame_ms_p95     p95 frame time must be <= budget
  memory_mb        peak memory must be <= budget      (needs memory in a JSON report)
  download_mb      download size must be <= budget    (needs download_mb in a JSON report)
  cold_start_sec   cold start must be <= budget       (needs cold_start_sec in a JSON report)
A budget with no matching measurement is reported as skipped, never as a pass.

Exit codes: 0 pass (or no budgets), 1 budget failed, 2 usage/input error.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from pathlib import Path

FPS_TOLERANCE = 0.95
CSV_COLS = ("frame_ms", "frametime", "frame_time", "frametime_ms", "ms", "dt_ms")


class InputError(Exception):
    pass


def percentile(sorted_vals: list[float], p: float) -> float:
    if not sorted_vals:
        return 0.0
    k = (len(sorted_vals) - 1) * p / 100.0
    lo = int(k)
    hi = min(lo + 1, len(sorted_vals) - 1)
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (k - lo)


def frame_stats(frames: list[float]) -> dict:
    fr = [f for f in frames if f > 0]
    if not fr:
        raise InputError("no positive frame times in report")
    s = sorted(fr)
    n = len(s)
    mean = sum(s) / n
    worst = s[-max(1, n // 100):]
    p50 = percentile(s, 50)
    return {"frames": n, "duration_sec": round(sum(s) / 1000.0, 3), "avg_fps": round(1000.0 / mean, 2),
            "p1_low_fps": round(1000.0 / (sum(worst) / len(worst)), 2), "p50_ms": round(p50, 3),
            "p95_ms": round(percentile(s, 95), 3), "p99_ms": round(percentile(s, 99), 3),
            "jank_count": sum(1 for f in fr if f > 2 * p50)}


def parse_csv(text: str) -> list[float]:
    rows = [r for r in csv.reader(io.StringIO(text)) if r and any(c.strip() for c in r)]
    if not rows:
        raise InputError("empty CSV")

    def num(s: str):
        try:
            return float(s)
        except ValueError:
            return None
    col = len(rows[0]) - 1
    start = 0
    if any(num(c) is None for c in rows[0]):  # header row
        start = 1
        names = [c.strip().lower() for c in rows[0]]
        for cand in CSV_COLS:
            if cand in names:
                col = names.index(cand)
                break
    vals = [num(r[col]) for r in rows[start:] if len(r) > col]
    vals = [v for v in vals if v is not None]
    if not vals:
        raise InputError("no numeric frame times found in CSV column %d" % col)
    return vals


def load_report(path: Path) -> tuple[dict, dict, dict]:
    """Return (stats, extras, embedded_budgets)."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        raise InputError("cannot read report: %s" % e)
    if path.suffix.lower() == ".json" or text.lstrip().startswith("{"):
        try:
            doc = json.loads(text)
        except ValueError as e:
            raise InputError("invalid JSON: %s" % e)
        extras = {"memory_mb": (doc.get("memory_mb") or {}).get("peak"), "download_mb": doc.get("download_mb"),
                  "cold_start_sec": doc.get("cold_start_sec")}
        frames = doc.get("frames_ms")
        if frames:
            return frame_stats([float(x) for x in frames]), extras, doc.get("budgets") or {}
        fps, fm = doc.get("fps") or {}, doc.get("frame_ms") or {}
        if not fps.get("avg") or not fm.get("p95"):
            raise InputError("JSON report needs frames_ms, or fps.avg and frame_ms.p95")
        stats = {"frames": None, "duration_sec": doc.get("duration_sec"), "avg_fps": fps["avg"],
                 "p1_low_fps": fps.get("p1_low"), "p50_ms": fm.get("p50"), "p95_ms": fm["p95"],
                 "p99_ms": fm.get("p99"), "jank_count": doc.get("jank_count")}
        return stats, extras, doc.get("budgets") or {}
    return frame_stats(parse_csv(text)), {}, {}


def evaluate(stats: dict, extras: dict, budgets: dict) -> list[dict]:
    res: list[dict] = []

    def add(key: str, label: str, measured, limit, ok_fn, unit: str) -> None:
        if key not in budgets or budgets[key] is None:
            return
        if measured is None:
            res.append({"budget": key, "status": "skipped", "message": "%s: no measurement in report" % label})
            return
        ok = ok_fn(measured, limit)
        res.append({"budget": key, "status": "pass" if ok else "fail", "measured": measured, "limit": limit,
                    "message": "%s: %s%s vs %s%s" % (label, measured, unit, limit, unit)})
    add("fps_target", "avg fps (>= %d%% of target)" % round(FPS_TOLERANCE * 100), stats["avg_fps"],
        budgets.get("fps_target"), lambda m, b: m >= b * FPS_TOLERANCE, " fps")
    add("frame_ms_p95", "p95 frame time", stats["p95_ms"], budgets.get("frame_ms_p95"), lambda m, b: m <= b, " ms")
    add("memory_mb", "peak memory", extras.get("memory_mb"), budgets.get("memory_mb"), lambda m, b: m <= b, " MB")
    add("download_mb", "download size", extras.get("download_mb"), budgets.get("download_mb"), lambda m, b: m <= b, " MB")
    add("cold_start_sec", "cold start", extras.get("cold_start_sec"), budgets.get("cold_start_sec"), lambda m, b: m <= b, " s")
    return res


def analyze(report: Path, contract: Path | None) -> dict:
    stats, extras, embedded = load_report(report)
    budgets = embedded
    source = "report" if embedded else "none"
    if contract is not None:
        try:
            c = json.loads(contract.read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            raise InputError("cannot read contract: %s" % e)
        budgets = (c.get("technical") or {}).get("perf_budgets") or {}
        source = "contract"
    checks = evaluate(stats, extras, budgets)
    failed = [c for c in checks if c["status"] == "fail"]
    verdict = "fail" if failed else ("pass" if any(c["status"] == "pass" for c in checks) else "no-budgets")
    return {"report": str(report), "stats": stats, "budget_source": source, "budgets": budgets,
            "checks": checks, "violations": [c["message"] for c in failed], "verdict": verdict}


def render(r: dict) -> str:
    s = r["stats"]
    out = ["Perf report: %s" % r["report"],
           "  frames %s  duration %ss  avg %.1f fps  1%% low %s fps" % (s["frames"], s["duration_sec"], s["avg_fps"], s["p1_low_fps"]),
           "  p50 %s ms  p95 %s ms  p99 %s ms  jank %s" % (s["p50_ms"], s["p95_ms"], s["p99_ms"], s["jank_count"]),
           "Budgets (%s):" % r["budget_source"]]
    out += ["  [%s] %s" % (c["status"].upper(), c["message"]) for c in r["checks"]] or ["  none"]
    out.append("Verdict: %s" % r["verdict"].upper())
    return "\n".join(out)


def selftest() -> int:
    import tempfile
    s = frame_stats([16.667] * 98 + [50.0, 60.0])
    assert abs(s["avg_fps"] - 1000 / ((16.667 * 98 + 110) / 100)) < 0.1 and s["jank_count"] == 2, s
    assert abs(s["p1_low_fps"] - 1000 / 60.0) < 0.1 and abs(s["p50_ms"] - 16.667) < 1e-6
    assert abs(percentile([1, 2, 3, 4], 50) - 2.5) < 1e-9
    assert parse_csv("frame,ms\n1,16.7\n2,16.9\n") == [16.7, 16.9]
    assert parse_csv("16.7\n17.1\n") == [16.7, 17.1]
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        (d / "good.csv").write_text("frame_ms\n" + "16.6\n" * 300, encoding="utf-8")
        (d / "bad.csv").write_text("frame_ms\n" + "33.3\n" * 300, encoding="utf-8")
        (d / "contract.json").write_text(json.dumps({"technical": {"perf_budgets": {"fps_target": 60, "frame_ms_p95": 20, "memory_mb": 500}}}), encoding="utf-8")
        (d / "rep.json").write_text(json.dumps({"fps": {"avg": 58, "p1_low": 40}, "frame_ms": {"p50": 16, "p95": 19, "p99": 25},
                                                  "memory_mb": {"peak": 620}, "budgets": {"memory_mb": 500, "fps_target": 60}}), encoding="utf-8")
        c = d / "contract.json"
        assert analyze(d / "good.csv", c)["verdict"] == "pass"
        r = analyze(d / "good.csv", c)
        assert [x["status"] for x in r["checks"]] == ["pass", "pass", "skipped"]
        assert analyze(d / "bad.csv", c)["verdict"] == "fail"
        r = analyze(d / "rep.json", None)
        assert r["verdict"] == "fail" and r["violations"] and "memory" in r["violations"][0], r
        assert analyze(d / "good.csv", None)["verdict"] == "no-budgets"
        try:
            (d / "e.csv").write_text("", encoding="utf-8")
            analyze(d / "e.csv", None)
            raise SystemExit("expected InputError")
        except InputError:
            pass
    print("selftest ok")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Frame-time statistics and perf-budget verdict.")
    ap.add_argument("--report", help="perf-report JSON or CSV of frame times (ms)")
    ap.add_argument("--contract", help="contract.json with technical.perf_budgets")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    try:
        a = ap.parse_args(argv)
    except SystemExit as e:
        return 2 if e.code else 0
    if a.selftest:
        return selftest()
    if not a.report:
        print("error: --report is required", file=sys.stderr)
        return 2
    try:
        r = analyze(Path(a.report), Path(a.contract) if a.contract else None)
    except InputError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    print(json.dumps(r, indent=2) if a.json else render(r))
    return 1 if r["verdict"] == "fail" else 0


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows pipes default to the ANSI code page; Claude Code reads UTF-8
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
