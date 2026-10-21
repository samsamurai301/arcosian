#!/usr/bin/env python3
"""level_audit.py - audit an ordered set of level-spec files (level-design skill).

Single-level tools (puzzle_solver.py, match3_sim.py) say whether one level is
solvable and how hard a bot finds it. This tool checks what only the *set* can
show: mechanic introduction order (one new mechanic per level, introduced in a
teach level, tested before it is twisted), difficulty sequencing (hard streaks,
relief after spikes), move-limit slack against the solver optimum, bot results
against the designed target, run counts, duplicate layouts, and consistency of
win-rate and attempts targets. It also converts a per-attempt win rate into
attempt odds, and merges solver / simulator JSON output into a level's
`solver` block.

    level_audit.py audit --dir DIR [--order FILE] [--glob "*.level.json"]
                         [--tolerance 0.10] [--min-runs 200] [--hard-threshold 0.5]
                         [--max-hard-streak 2] [--slack-min 1.1] [--slack-max 3.0]
                         [--strict] [--json]
    level_audit.py odds  --win-rate P [--attempts K] [--json]
    level_audit.py merge --level PATH --result PATH [--dry-run] [--json]
    level_audit.py --selftest

Ordering: --order FILE (a JSON list of level ids, or one id per line), else
DIR/order.json if present, else natural sort of level ids. Files under a
directory named "archive" are skipped.

Exit codes: 0 ok (warnings allowed), 1 check failed (errors found / nothing
merged), 2 usage or input error. Stdlib only, Python 3.9+.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PUZZLE_TYPES = {"sliding", "sokoban", "sort", "lights_out"}
STOCHASTIC_TYPES = {"match3"}
ROLES = ("teach", "test", "twist", "reward")

Finding = Dict[str, Any]


# --------------------------------------------------------------------------- helpers

def natural_key(text: str) -> List[Any]:
    """Sort key that orders 'w1_l9' before 'w1_l10'."""
    return [int(tok) if tok.isdigit() else tok.lower() for tok in re.split(r"(\d+)", text)]


def finding(severity: str, code: str, level_id: Optional[str], message: str,
            file: Optional[str] = None) -> Finding:
    return {"severity": severity, "code": code, "level_id": level_id, "file": file, "message": message}


def layout_type(level: Dict[str, Any]) -> Optional[str]:
    layout = level.get("layout")
    if isinstance(layout, list):
        return "grid"
    if isinstance(layout, dict):
        t = layout.get("type")
        return t if isinstance(t, str) else None
    return None


def move_limit(level: Dict[str, Any]) -> Optional[int]:
    lim = level.get("moves_or_time_limit")
    if isinstance(lim, bool):
        return None
    if isinstance(lim, int):
        return lim
    if isinstance(lim, dict):
        m = lim.get("moves")
        if isinstance(m, int) and not isinstance(m, bool):
            return m
    return None


def _num(value: Any) -> Optional[float]:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def target_win_rate(level: Dict[str, Any]) -> Optional[float]:
    dt = level.get("difficulty_target")
    return _num(dt.get("win_rate")) if isinstance(dt, dict) else None


def target_bot_win_rate(level: Dict[str, Any]) -> Optional[float]:
    """Bot-space target (difficulty_target.bot_win_rate, from a bot-to-human calibration), if set."""
    dt = level.get("difficulty_target")
    return _num(dt.get("bot_win_rate")) if isinstance(dt, dict) else None


def target_attempts(level: Dict[str, Any]) -> Optional[float]:
    dt = level.get("difficulty_target")
    return _num(dt.get("attempts_p50")) if isinstance(dt, dict) else None


def solver_block(level: Dict[str, Any]) -> Dict[str, Any]:
    s = level.get("solver")
    return s if isinstance(s, dict) else {}


def mechanics(level: Dict[str, Any]) -> List[str]:
    refs = level.get("mechanic_refs")
    if not isinstance(refs, list):
        return []
    out: List[str] = []
    for r in refs:
        if isinstance(r, str) and r not in out:
            out.append(r)
    return out


def canonical_layout(layout: Any) -> Any:
    """Normalise a layout so cosmetic differences do not defeat duplicate detection."""
    if isinstance(layout, dict) and layout.get("type") == "sort":
        tubes = layout.get("tubes")
        if isinstance(tubes, list):
            canon_tubes = sorted((json.dumps(t, sort_keys=True) for t in tubes))
            return {"type": "sort", "capacity": layout.get("capacity"),
                    "pour": layout.get("pour", "max"), "tubes": canon_tubes}
    if isinstance(layout, dict) and layout.get("type") == "generator":
        return {"type": "generator", "generator": layout.get("generator"),
                "seed": layout.get("seed"), "params": layout.get("params")}
    return layout


def layout_hash(layout: Any) -> Optional[str]:
    if layout is None:
        return None
    blob = json.dumps(canonical_layout(layout), sort_keys=True, separators=(",", ":"))
    return hashlib.sha1(blob.encode("utf-8")).hexdigest()[:12]


def geometric_quantile(p: float, q: float) -> Optional[int]:
    """Smallest k with P(first win within k attempts) >= q, for per-attempt win rate p."""
    if p <= 0.0:
        return None
    if p >= 1.0:
        return 1
    k = math.log(1.0 - q) / math.log(1.0 - p)
    return max(1, int(math.ceil(k - 1e-9)))


def attempt_odds(p: float, attempts: int = 3) -> Dict[str, Any]:
    if not 0.0 <= p <= 1.0:
        raise ValueError("win rate must be between 0 and 1")
    return {
        "win_rate": p,
        "median_attempts": geometric_quantile(p, 0.5),
        "p90_attempts": geometric_quantile(p, 0.9),
        "expected_attempts": (None if p == 0 else round(1.0 / p, 3)),
        "attempts": attempts,
        "p_fail_streak": round((1.0 - p) ** attempts, 4),
        "p_win_within": round(1.0 - (1.0 - p) ** attempts, 4),
        "assumption": "independent attempts (players learn, so real attempts are usually lower)",
    }


# --------------------------------------------------------------------------- loading

def load_levels(directory: Path, pattern: str) -> Tuple[List[Dict[str, Any]], List[Finding]]:
    findings: List[Finding] = []
    levels: List[Dict[str, Any]] = []
    seen: Dict[str, str] = {}
    files = sorted(p for p in directory.rglob(pattern)
                   if p.is_file() and "archive" not in p.relative_to(directory).parts[:-1])
    for path in files:
        rel = str(path.relative_to(directory))
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            findings.append(finding("error", "parse", None, "cannot parse JSON: %s" % exc, rel))
            continue
        if not isinstance(doc, dict):
            findings.append(finding("error", "parse", None, "top level is not an object", rel))
            continue
        lid = doc.get("level_id")
        if not isinstance(lid, str) or not lid:
            findings.append(finding("error", "missing_id", None, "no level_id", rel))
            continue
        if lid in seen:
            findings.append(finding("error", "duplicate_id", lid,
                                    "level_id also used by %s" % seen[lid], rel))
            continue
        seen[lid] = rel
        doc["_file"] = rel
        levels.append(doc)
    return levels, findings


def read_order(path: Path) -> List[str]:
    text = path.read_text(encoding="utf-8")
    stripped = text.strip()
    if stripped.startswith("["):
        data = json.loads(stripped)
        if not isinstance(data, list) or not all(isinstance(x, str) for x in data):
            raise ValueError("order file must be a JSON list of level ids")
        return data
    return [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.strip().startswith("#")]


def order_levels(levels: List[Dict[str, Any]], order: Optional[List[str]]) -> Tuple[List[Dict[str, Any]], List[Finding]]:
    findings: List[Finding] = []
    by_id = {lv["level_id"]: lv for lv in levels}
    if not order:
        return sorted(levels, key=lambda lv: natural_key(lv["level_id"])), findings
    ordered: List[Dict[str, Any]] = []
    for lid in order:
        if lid in by_id:
            ordered.append(by_id.pop(lid))
        else:
            findings.append(finding("warning", "order_unknown_id", lid, "listed in the order file but no level file has this id"))
    for lv in sorted(by_id.values(), key=lambda x: natural_key(x["level_id"])):
        findings.append(finding("warning", "order_missing", lv["level_id"],
                                "not in the order file; appended at the end", lv["_file"]))
        ordered.append(lv)
    return ordered, findings


# --------------------------------------------------------------------------- audit

def audit(levels: List[Dict[str, Any]], opts: argparse.Namespace) -> Tuple[List[Finding], Dict[str, Any]]:
    out: List[Finding] = []
    tol = opts.tolerance
    thr = opts.hard_threshold

    def add(sev: str, code: str, lv: Dict[str, Any], msg: str) -> None:
        out.append(finding(sev, code, lv.get("level_id"), msg, lv.get("_file")))

    # ---- per-level checks
    for lv in levels:
        lt = layout_type(lv)
        sb = solver_block(lv)
        solvable = sb.get("solvable")
        min_moves = sb.get("min_moves")
        bot = _num(sb.get("bot_win_rate"))
        runs = sb.get("runs")
        limit = move_limit(lv)
        wr = target_win_rate(lv)
        role = lv.get("teach")

        if role is not None and role not in ROLES:
            add("error", "bad_role", lv, "teach must be one of %s, got %r" % (", ".join(ROLES), role))
        if solvable is False:
            add("error", "unsolvable", lv, "solver.solvable is false")
        elif lt in PUZZLE_TYPES and solvable is None:
            add("error" if opts.strict else "warning", "unverified", lv,
                "%s layout has no solver verdict (run puzzle_solver.py)" % lt)
        if lt in STOCHASTIC_TYPES and bot is None:
            add("error" if opts.strict else "warning", "unverified", lv,
                "match3 layout has no bot_win_rate (run match3_sim.py)")

        if isinstance(min_moves, int) and not isinstance(min_moves, bool) and limit is not None:
            if limit < min_moves:
                add("error", "limit_below_optimum", lv,
                    "move limit %d is below the solver optimum %d (unwinnable)" % (limit, min_moves))
            elif min_moves > 0 and lt in PUZZLE_TYPES:
                slack = limit / float(min_moves)
                # generous limits are intended on teach and reward levels, so only the lower bound applies there
                upper_applies = role not in ("teach", "reward")
                if slack < opts.slack_min or (upper_applies and slack > opts.slack_max):
                    add("warning", "slack_out_of_band", lv,
                        "slack %.2f (limit %d / optimum %d) outside [%.2f, %.2f]" %
                        (slack, limit, min_moves, opts.slack_min, opts.slack_max))

        bot_target = target_bot_win_rate(lv)
        cmp_target = bot_target if bot_target is not None else wr
        if bot is not None and cmp_target is not None:
            gap = abs(bot - cmp_target)
            if gap > tol:
                sev = "error" if gap > 2 * tol else "warning"
                add(sev, "bot_vs_target", lv,
                    "bot win rate %.2f vs %s %.2f (gap %.2f > tolerance %.2f)" %
                    (bot, "bot target" if bot_target is not None else "target", cmp_target, gap, tol))
        if bot is not None and isinstance(runs, int) and not isinstance(runs, bool) and runs < opts.min_runs:
            se = math.sqrt(max(bot * (1 - bot), 1e-9) / max(runs, 1))
            add("warning", "few_runs", lv,
                "only %d bot runs (standard error about %.3f); use at least %d" % (runs, se, opts.min_runs))

        att = target_attempts(lv)
        if wr is not None and att is not None and 0.0 < wr < 1.0:
            implied = geometric_quantile(wr, 0.5) or 1
            if att > 2 * implied or att * 2 < implied:
                add("warning", "attempts_inconsistent", lv,
                    "attempts_p50 %.1f vs %d implied by win rate %.2f (geometric median)" % (att, implied, wr))

    # ---- sequence checks
    seen: set = set()
    tested: set = set()
    intro_at: Dict[str, str] = {}
    streak = 0
    streak_flagged = False
    n = len(levels)
    for i, lv in enumerate(levels):
        refs = mechanics(lv)
        role = lv.get("teach")
        wr = target_win_rate(lv)
        hard = wr is not None and wr < thr
        new = [m for m in refs if m not in seen]
        if len(new) > 1:
            add("error", "multi_intro", lv, "%d mechanics first appear here: %s" % (len(new), ", ".join(new)))
        if new and role is not None and role != "teach":
            add("warning", "intro_not_teach", lv,
                "first appearance of %s in a '%s' level" % (", ".join(new), role))
        if new and hard:
            add("warning", "intro_on_spike", lv,
                "first appearance of %s in a hard level (target %.2f < %.2f)" % (", ".join(new), wr, thr))
        if role == "twist":
            untested = [m for m in refs if m in seen and m not in tested]
            if untested:
                add("warning", "twist_before_test", lv,
                    "twist uses %s before any test level" % ", ".join(untested))
        for m in new:
            intro_at[m] = lv["level_id"]
        seen.update(refs)
        if role == "test":
            tested.update(refs)

        if hard:
            streak += 1
            if streak > opts.max_hard_streak and not streak_flagged:
                add("warning", "hard_streak", lv,
                    "%d consecutive hard levels (max %d)" % (streak, opts.max_hard_streak))
                streak_flagged = True
        else:
            streak = 0
            streak_flagged = False

        next_hard = False
        if i + 1 < n:
            nwr = target_win_rate(levels[i + 1])
            next_hard = nwr is not None and nwr < thr
        if hard and not next_hard and i + 1 < n:
            window = levels[i + 1:i + 3]
            relief = False
            for nxt in window:
                nwr = target_win_rate(nxt)
                if nxt.get("teach") == "reward" or (nwr is not None and nwr >= thr + 0.15):
                    relief = True
                    break
            if not relief:
                add("warning", "no_relief", lv,
                    "no reward level or level with target >= %.2f in the next %d level(s)" % (thr + 0.15, len(window)))

    # ---- duplicates
    hashes: Dict[str, List[Dict[str, Any]]] = {}
    for lv in levels:
        h = layout_hash(lv.get("layout"))
        if h:
            hashes.setdefault(h, []).append(lv)
    for h, group in hashes.items():
        if len(group) > 1:
            ids = [g["level_id"] for g in group]
            for g in group[1:]:
                add("warning", "duplicate_layout", g, "same canonical layout as %s (hash %s)" % (ids[0], h))

    # ---- summary
    roles = {r: 0 for r in ROLES}
    verified = 0
    wrs: List[float] = []
    hard_count = 0
    for lv in levels:
        r = lv.get("teach")
        if r in roles:
            roles[r] += 1
        sb = solver_block(lv)
        if sb.get("solvable") is True or _num(sb.get("bot_win_rate")) is not None:
            verified += 1
        wr = target_win_rate(lv)
        if wr is not None:
            wrs.append(wr)
            if wr < thr:
                hard_count += 1
    summary = {
        "levels": len(levels),
        "verified": verified,
        "roles": roles,
        "hard_levels": hard_count,
        "mean_target_win_rate": round(sum(wrs) / len(wrs), 3) if wrs else None,
        "mechanic_intros": intro_at,
        "order": [lv["level_id"] for lv in levels],
    }
    return out, summary


# --------------------------------------------------------------------------- merge

EXTRA_KEYS = ("algo", "states_visited", "nodes_expanded", "max_nodes", "budget_exhausted",
              "bot", "seed", "median_moves", "moves_p50", "moves_left_p50", "solution_count")


def _pick_source(result: Any) -> Dict[str, Any]:
    if isinstance(result, dict):
        for key in ("solver", "result", "summary"):
            if isinstance(result.get(key), dict):
                merged = dict(result)
                merged.update(result[key])
                return merged
        return result
    return {}


def merge_result(level_doc: Dict[str, Any], result: Any) -> Tuple[Dict[str, Any], List[str]]:
    """Return (new solver block, list of mapped field names). Raises ValueError on bad values."""
    src = _pick_source(result)
    sb = dict(solver_block(level_doc))
    mapped: List[str] = []

    if "solvable" in src and (src["solvable"] is None or isinstance(src["solvable"], bool)):
        sb["solvable"] = src["solvable"]
        mapped.append("solvable")
    mm = None
    for key in ("min_moves", "solution_length", "moves"):
        v = src.get(key)
        if isinstance(v, int) and not isinstance(v, bool):
            mm = v
            break
    if mm is None and isinstance(src.get("solution"), list):
        mm = len(src["solution"])
    if mm is not None:
        if mm < 0:
            raise ValueError("min_moves must be >= 0")
        sb["min_moves"] = mm
        mapped.append("min_moves")
    for key in ("bot_win_rate", "win_rate"):
        v = _num(src.get(key))
        if v is not None:
            if not 0.0 <= v <= 1.0:
                raise ValueError("%s %.3f is not a ratio between 0 and 1" % (key, v))
            sb["bot_win_rate"] = round(v, 4)
            mapped.append("bot_win_rate")
            break
    for key in ("runs", "n_runs"):
        v = src.get(key)
        if isinstance(v, int) and not isinstance(v, bool) and v >= 0:
            sb["runs"] = v
            mapped.append("runs")
            break
    for key in EXTRA_KEYS:
        v = src.get(key)
        if isinstance(v, (str, int, float, bool)):
            sb[key] = v
            mapped.append(key)
    if src.get("budget_exhausted") is True and src.get("solvable") is not True:
        sb["solvable"] = None
    for key in ("solvable", "min_moves", "bot_win_rate", "runs"):
        sb.setdefault(key, None)
    return sb, mapped


def write_json_atomic(path: Path, data: Any) -> None:
    fd, tmp = tempfile.mkstemp(prefix=".tmp_", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        os.replace(tmp, str(path))
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


# --------------------------------------------------------------------------- commands

def cmd_audit(args: argparse.Namespace) -> int:
    directory = Path(args.dir)
    if not directory.is_dir():
        print("error: not a directory: %s" % directory, file=sys.stderr)
        return 2
    levels, findings = load_levels(directory, args.glob)
    order: Optional[List[str]] = None
    order_src = "natural sort of level ids"
    order_path = Path(args.order) if args.order else directory / "order.json"
    if args.order and not order_path.is_file():
        print("error: order file not found: %s" % order_path, file=sys.stderr)
        return 2
    if order_path.is_file():
        try:
            order = read_order(order_path)
            order_src = str(order_path)
        except (OSError, ValueError) as exc:
            print("error: bad order file %s: %s" % (order_path, exc), file=sys.stderr)
            return 2
    ordered, ofind = order_levels(levels, order)
    findings.extend(ofind)
    afind, summary = audit(ordered, args)
    findings.extend(afind)
    errors = sum(1 for f in findings if f["severity"] == "error")
    warnings = sum(1 for f in findings if f["severity"] == "warning")
    summary.update({"errors": errors, "warnings": warnings, "order_source": order_src})
    if args.json:
        print(json.dumps({"ok": errors == 0, "summary": summary, "findings": findings}, indent=2))
    else:
        print("level audit: %d level(s) in %s (order: %s)" % (summary["levels"], directory, order_src))
        width = max([12] + [len(str(f["level_id"] or f["file"] or "-")) for f in findings])
        for f in findings:
            print("%-5s  %-*s  %-22s %s" % ("ERROR" if f["severity"] == "error" else "WARN", width,
                                            f["level_id"] or f["file"] or "-", f["code"], f["message"]))
        r = summary["roles"]
        print("summary: %d error(s), %d warning(s); verified %d/%d; hard %d; mean target %s; roles teach %d test %d twist %d reward %d" % (
            errors, warnings, summary["verified"], summary["levels"], summary["hard_levels"],
            summary["mean_target_win_rate"], r["teach"], r["test"], r["twist"], r["reward"]))
        if summary["mechanic_intros"]:
            print("mechanic intros: " + ", ".join("%s@%s" % kv for kv in summary["mechanic_intros"].items()))
    return 0 if errors == 0 else 1


def cmd_odds(args: argparse.Namespace) -> int:
    if not 0.0 <= args.win_rate <= 1.0 or args.attempts < 1:
        print("error: --win-rate must be in [0, 1] and --attempts >= 1", file=sys.stderr)
        return 2
    res = attempt_odds(args.win_rate, args.attempts)
    if args.json:
        print(json.dumps(res, indent=2))
    else:
        print("per-attempt win rate %.3f" % res["win_rate"])
        print("  median attempts to first win: %s" % res["median_attempts"])
        print("  90th percentile attempts:     %s" % res["p90_attempts"])
        print("  expected attempts:            %s" % res["expected_attempts"])
        print("  P(fail %d in a row):           %.1f%%" % (res["attempts"], 100 * res["p_fail_streak"]))
        print("  P(win within %d attempts):     %.1f%%" % (res["attempts"], 100 * res["p_win_within"]))
        print("  assumes %s" % res["assumption"])
    return 0


def cmd_merge(args: argparse.Namespace) -> int:
    lpath, rpath = Path(args.level), Path(args.result)
    try:
        level_doc = json.loads(lpath.read_text(encoding="utf-8"))
        result = json.loads(rpath.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    if not isinstance(level_doc, dict):
        print("error: level file is not a JSON object", file=sys.stderr)
        return 2
    try:
        sb, mapped = merge_result(level_doc, result)
    except ValueError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    core = [m for m in mapped if m in ("solvable", "min_moves", "bot_win_rate", "runs")]
    if not core:
        msg = "nothing mappable in %s (expected solvable / min_moves / bot_win_rate / runs)" % rpath
        print(json.dumps({"ok": False, "error": msg}) if args.json else "check failed: " + msg)
        return 1
    level_doc["solver"] = sb
    if not args.dry_run:
        write_json_atomic(lpath, level_doc)
    if args.json:
        print(json.dumps({"ok": True, "level": str(lpath), "mapped": mapped, "solver": sb,
                          "written": not args.dry_run}, indent=2))
    else:
        print("%s %s: %s" % ("would update" if args.dry_run else "updated", lpath, ", ".join(mapped)))
    return 0


# --------------------------------------------------------------------------- selftest

def _lv(lid: str, role: Optional[str], mechs: List[str], wr: Optional[float], layout: Any = None,
        limit: Optional[int] = None, solver: Optional[Dict[str, Any]] = None,
        attempts: Optional[float] = None) -> Dict[str, Any]:
    doc: Dict[str, Any] = {"schema_version": "1.0", "level_id": lid, "mechanic_refs": mechs}
    if layout is not None:
        doc["layout"] = layout
    if limit is not None:
        doc["moves_or_time_limit"] = {"moves": limit}
    dt: Dict[str, Any] = {}
    if wr is not None:
        dt["win_rate"] = wr
    if attempts is not None:
        dt["attempts_p50"] = attempts
    if dt:
        doc["difficulty_target"] = dt
    doc["solver"] = solver if solver is not None else {"solvable": True, "min_moves": 10, "bot_win_rate": wr, "runs": 500}
    if role:
        doc["teach"] = role
    return doc


def _sort_layout(tubes: List[List[str]]) -> Dict[str, Any]:
    return {"type": "sort", "capacity": 4, "pour": "max", "tubes": tubes}


def selftest() -> int:
    failures: List[str] = []

    def check(cond: bool, label: str) -> None:
        if not cond:
            failures.append(label)

    # odds
    check(attempt_odds(0.5)["median_attempts"] == 1, "odds p=0.5 median")
    check(attempt_odds(0.5)["p90_attempts"] == 4, "odds p=0.5 p90")
    check(attempt_odds(0.25)["median_attempts"] == 3, "odds p=0.25 median")
    check(attempt_odds(0.25)["p90_attempts"] == 9, "odds p=0.25 p90")
    check(attempt_odds(0.35)["median_attempts"] == 2, "odds p=0.35 median")
    check(abs(attempt_odds(0.25, 3)["p_fail_streak"] - 0.4219) < 1e-4, "odds fail streak")
    check(attempt_odds(1.0)["median_attempts"] == 1 and attempt_odds(0.0)["median_attempts"] is None, "odds edges")
    check(natural_key("w1_l9") < natural_key("w1_l10"), "natural sort")
    a = _sort_layout([["r", "g", "r", "g"], ["g", "r", "g", "r"], []])
    b = _sort_layout([[], ["g", "r", "g", "r"], ["r", "g", "r", "g"]])
    check(layout_hash(a) == layout_hash(b), "sort canonical hash ignores tube order")

    ns = argparse.Namespace(tolerance=0.10, min_runs=200, hard_threshold=0.5, max_hard_streak=2,
                            slack_min=1.1, slack_max=3.0, strict=False, glob="*.level.json",
                            order=None, json=True)
    tubes1 = [["r", "g", "b", "r"], ["g", "b", "r", "g"], ["b", "r", "g", "b"], [], []]
    fixtures = [
        _lv("w1_l001", "teach", ["A"], 0.97, _sort_layout(tubes1), 12,
            {"solvable": True, "min_moves": 5, "bot_win_rate": 0.98, "runs": 200}),
        _lv("w1_l002", "test", ["A"], 0.80, _sort_layout([["r", "r", "g", "g"], ["g", "g", "r", "r"], []]), 14,
            {"solvable": True, "min_moves": 10, "bot_win_rate": 0.78, "runs": 500}),
        _lv("w1_l003", "teach", ["B", "C"], 0.95),                         # multi_intro
        _lv("w1_l004", "twist", ["B"], 0.40),                              # twist_before_test, hard 1
        _lv("w1_l005", "test", ["B"], 0.35),                               # hard 2
        _lv("w1_l006", "test", ["C"], 0.30),                               # hard 3 -> hard_streak
        _lv("w1_l007", "test", ["A"], 0.55),                               # not relief
        _lv("w1_l008", "test", ["A"], 0.60),                               # not relief -> no_relief on l006
        _lv("w1_l009", "test", ["A"], 0.70, _sort_layout(list(reversed(tubes1))), 15,
            {"solvable": True, "min_moves": 20, "bot_win_rate": 0.7, "runs": 500}),  # limit_below_optimum, duplicate_layout
        _lv("w1_l010", "test", ["A"], 0.70, None, None,
            {"solvable": False, "min_moves": None, "bot_win_rate": None, "runs": None}),  # unsolvable
        _lv("w1_l011", "reward", ["A"], 0.60, {"type": "match3", "width": 8, "height": 8, "colors": 5}, 25,
            {"solvable": None, "min_moves": None, "bot_win_rate": 0.90, "runs": 50}),  # bot_vs_target error, few_runs
        _lv("w1_l012", "reward", ["D"], 0.90, {"type": "sliding", "grid": [[1, 2], [0, 3]]}, None,
            {"solvable": None, "min_moves": None, "bot_win_rate": None, "runs": None}, attempts=5),  # unverified, attempts_inconsistent, intro_not_teach
        _lv("w1_l013", "test", ["A"], 0.75, _sort_layout([["r", "g", "r", "g"], ["g", "r", "g", "r"], []]), 40,
            {"solvable": True, "min_moves": 6, "bot_win_rate": 0.75, "runs": 500}),  # slack_out_of_band (6.7)
    ]
    expected = {"multi_intro", "twist_before_test", "hard_streak", "no_relief", "limit_below_optimum",
                "duplicate_layout", "unsolvable", "bot_vs_target", "few_runs", "unverified",
                "attempts_inconsistent", "intro_not_teach", "slack_out_of_band", "parse", "duplicate_id"}
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        for fx in reversed(fixtures):   # write in reverse to prove ordering is by id, not by write order
            (d / ("%s.level.json" % fx["level_id"])).write_text(json.dumps(fx), encoding="utf-8")
        (d / "broken.level.json").write_text("{not json", encoding="utf-8")
        (d / "zz_dupe.level.json").write_text(json.dumps(_lv("w1_l001", "test", ["A"], 0.8)), encoding="utf-8")
        (d / "archive").mkdir()
        (d / "archive" / "old.level.json").write_text("{also broken", encoding="utf-8")
        levels, lf = load_levels(d, "*.level.json")
        ordered, of = order_levels(levels, None)
        af, summary = audit(ordered, ns)
        codes = {f["code"] for f in lf + of + af}
        missing = expected - codes
        check(not missing, "missing finding codes: %s" % sorted(missing))
        check(summary["order"][0] == "w1_l001" and summary["order"][-1] == "w1_l013", "natural ordering of fixture set")
        check(summary["mechanic_intros"].get("D") == "w1_l012", "mechanic intro map")
        sev = {f["code"]: f["severity"] for f in af}
        check(sev.get("bot_vs_target") == "error", "bot gap beyond 2x tolerance is an error")
        check(sev.get("unverified") == "warning", "unverified is a warning without --strict")
        check(not any(f["code"] == "parse" and "archive" in (f["file"] or "") for f in lf), "archive dirs skipped")
        hs = [f for f in af if f["code"] == "hard_streak"]
        check(len(hs) == 1 and hs[0]["level_id"] == "w1_l006", "hard streak flagged once at the third hard level")
        nr = [f for f in af if f["code"] == "no_relief"]
        check(len(nr) == 1 and nr[0]["level_id"] == "w1_l006", "no_relief flagged at end of streak")

        # generous slack is fine on a teach level, flagged on a test level
        gen_teach = _lv("slk_001", "teach", ["A"], 0.97, _sort_layout(tubes1), 40,
                        {"solvable": True, "min_moves": 10, "bot_win_rate": 0.97, "runs": 500})
        afs, _ = audit([gen_teach], ns)
        check(not any(f["code"] == "slack_out_of_band" for f in afs), "teach level may have generous slack")
        check(any(f["code"] == "slack_out_of_band" and f["level_id"] == "w1_l013" for f in af), "test level slack upper bound")

        # a bot-space target overrides the human target for the bot comparison
        calibrated = _lv("cal_001", "test", ["A"], 0.55, None, None,
                         {"solvable": True, "min_moves": 18, "bot_win_rate": 0.34, "runs": 200})
        calibrated["difficulty_target"]["bot_win_rate"] = 0.35
        afc, _ = audit([calibrated], ns)
        check(not any(f["code"] == "bot_vs_target" for f in afc), "bot-space target honoured")
        del calibrated["difficulty_target"]["bot_win_rate"]
        afc, _ = audit([calibrated], ns)
        check(any(f["code"] == "bot_vs_target" for f in afc), "human target used without bot-space target")

        # strict mode turns unverified into an error
        ns_strict = argparse.Namespace(**dict(vars(ns), strict=True))
        af2, _ = audit(ordered, ns_strict)
        check(any(f["code"] == "unverified" and f["severity"] == "error" for f in af2), "strict unverified")

        # explicit order with an unknown id and a missing id
        ordered2, of2 = order_levels(levels, ["w1_l002", "w1_l001", "nope"])
        check(ordered2[0]["level_id"] == "w1_l002", "explicit order respected")
        check({f["code"] for f in of2} >= {"order_unknown_id", "order_missing"}, "order warnings")

    # clean set passes via the CLI path
    with tempfile.TemporaryDirectory() as tmp:
        d = Path(tmp)
        for fx in fixtures[:2]:
            (d / ("%s.level.json" % fx["level_id"])).write_text(json.dumps(fx), encoding="utf-8")
        (d / "order.json").write_text(json.dumps(["w1_l001", "w1_l002"]), encoding="utf-8")
        args = argparse.Namespace(**dict(vars(ns), dir=str(d), json=True))
        import contextlib
        import io
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = cmd_audit(args)
        out = json.loads(buf.getvalue())
        check(rc == 0 and out["ok"] and out["summary"]["errors"] == 0, "clean set exit 0")
        check(out["summary"]["order_source"].endswith("order.json"), "order.json picked up")

        # merge: puzzle solver style, simulator style, nothing mappable, bad ratio
        lpath = d / "w1_l002.level.json"
        rpath = d / "solve.json"
        rpath.write_text(json.dumps({"solvable": True, "min_moves": 13, "states_visited": 1012, "algo": "bfs"}), encoding="utf-8")
        margs = argparse.Namespace(level=str(lpath), result=str(rpath), dry_run=False, json=True)
        with contextlib.redirect_stdout(io.StringIO()):
            rc = cmd_merge(margs)
        doc = json.loads(lpath.read_text(encoding="utf-8"))
        check(rc == 0 and doc["solver"]["min_moves"] == 13 and doc["solver"]["states_visited"] == 1012, "merge solver output")
        check(doc["solver"]["bot_win_rate"] == 0.78, "merge keeps existing fields")
        rpath.write_text(json.dumps({"result": {"win_rate": 0.66, "runs": 1000, "bot": "greedy", "seed": 1}}), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            rc = cmd_merge(margs)
        doc = json.loads(lpath.read_text(encoding="utf-8"))
        check(rc == 0 and doc["solver"]["bot_win_rate"] == 0.66 and doc["solver"]["runs"] == 1000, "merge nested sim output")
        rpath.write_text(json.dumps({"foo": 1}), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            rc = cmd_merge(margs)
        check(rc == 1, "merge with nothing mappable returns 1")
        rpath.write_text(json.dumps({"win_rate": 66}), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            rc = cmd_merge(margs)
        check(rc == 2, "merge rejects a non-ratio win rate")
        rpath.write_text(json.dumps({"solvable": None, "budget_exhausted": True, "states_visited": 500000}), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            rc = cmd_merge(margs)
        doc = json.loads(lpath.read_text(encoding="utf-8"))
        check(rc == 0 and doc["solver"]["solvable"] is None, "budget exhaustion recorded as unknown")

    if failures:
        for f in failures:
            print("FAIL: " + f)
        print("selftest: %d failure(s)" % len(failures))
        return 1
    print("selftest: ok")
    return 0


# --------------------------------------------------------------------------- main

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Audit an ordered set of level-spec files; attempt odds; merge solver results.")
    p.add_argument("--selftest", action="store_true", help="run built-in tests and exit")
    sub = p.add_subparsers(dest="cmd")

    a = sub.add_parser("audit", help="audit a directory of *.level.json files in order")
    a.add_argument("--dir", required=True, help="levels directory (searched recursively; 'archive' dirs skipped)")
    a.add_argument("--order", help="order file: JSON list of level ids or one id per line (default DIR/order.json)")
    a.add_argument("--glob", default="*.level.json", help="file pattern (default *.level.json)")
    a.add_argument("--tolerance", type=float, default=0.10, help="allowed |bot_win_rate - target| (default 0.10)")
    a.add_argument("--min-runs", type=int, default=200, help="minimum bot runs (default 200)")
    a.add_argument("--hard-threshold", type=float, default=0.5, help="target win rate below which a level is hard (default 0.5)")
    a.add_argument("--max-hard-streak", type=int, default=2, help="maximum consecutive hard levels (default 2)")
    a.add_argument("--slack-min", type=float, default=1.1, help="minimum limit/min_moves for puzzles (default 1.1)")
    a.add_argument("--slack-max", type=float, default=3.0, help="maximum limit/min_moves for puzzles (default 3.0)")
    a.add_argument("--strict", action="store_true", help="treat unverified levels as errors")
    a.add_argument("--json", action="store_true", help="machine-readable output")

    o = sub.add_parser("odds", help="attempt odds for a per-attempt win rate (geometric model)")
    o.add_argument("--win-rate", type=float, required=True)
    o.add_argument("--attempts", type=int, default=3, help="streak length for fail/win odds (default 3)")
    o.add_argument("--json", action="store_true")

    m = sub.add_parser("merge", help="merge solver / simulator JSON output into a level's solver block")
    m.add_argument("--level", required=True)
    m.add_argument("--result", required=True)
    m.add_argument("--dry-run", action="store_true")
    m.add_argument("--json", action="store_true")
    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return 0 if exc.code == 0 else 2
    if args.selftest:
        return selftest()
    if args.cmd == "audit":
        if args.tolerance < 0 or args.min_runs < 0 or args.max_hard_streak < 0 or args.slack_min <= 0 or args.slack_max < args.slack_min:
            print("error: invalid threshold arguments", file=sys.stderr)
            return 2
        return cmd_audit(args)
    if args.cmd == "odds":
        return cmd_odds(args)
    if args.cmd == "merge":
        return cmd_merge(args)
    parser.print_help()
    return 2


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows pipes default to the ANSI code page; Claude Code reads UTF-8
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
