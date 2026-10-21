#!/usr/bin/env python3
"""analogy_score.py - scoring helpers for the analogy-engine skill.

Subcommands
  fitness  Analogy Fitness Score (AFS) for a source -> target mapping, from
           either summary numbers (--rc --hc --sf ...) or a mapping JSON file
           (see references/analogy-method.md section 15.5).
             AFS = clamp(0, 100, 100*(0.35*RC + 0.35*HC + 0.30*SF) - 15*V - 20*L)
           Verdict: GO (>= 70), ADAPT (50-69.99), DROP (< 50 or any hard violation).
  concept  Weighted total for a concept card (concept.schema.json "scores"),
           with weight presets, optional custom weights, gates and an
           evidence cap on fun_potential. --write stores scores.weighted_total.
  rank     Rank several concept cards (files or a directory of *.json).

Exit codes: 0 ok; 1 check failed (fitness DROP, concept gate failure);
2 usage or input error. Stdlib only; Python 3.9+.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

CRITERIA = (
    "market",
    "novelty",
    "fun_potential",
    "feasibility",
    "monetization",
    "production_cost",
    "agent_buildability",
)

PRESETS: Dict[str, Dict[str, float]] = {
    # Matches the example concept card: fun x2, market x1.5, rest x1 (sum 8.5).
    "default": {"market": 1.5, "novelty": 1, "fun_potential": 2, "feasibility": 1,
                "monetization": 1, "production_cost": 1, "agent_buildability": 1},
    # Solo developer plus agents: buildability, cost and risk weigh more.
    "agent_first": {"market": 1, "novelty": 1, "fun_potential": 2, "feasibility": 1.5,
                    "monetization": 1, "production_cost": 1.5, "agent_buildability": 2},
    # UA-led hybrid-casual publisher: market, hook and revenue weigh more.
    "ua_led": {"market": 2, "novelty": 1.5, "fun_potential": 1.5, "feasibility": 1,
               "monetization": 1.5, "production_cost": 1, "agent_buildability": 1},
    # Premium indie: fun and novelty first, monetization least.
    "premium_indie": {"market": 1, "novelty": 2, "fun_potential": 2.5, "feasibility": 1,
                      "monetization": 0.5, "production_cost": 1.5, "agent_buildability": 1},
}

DEFAULT_GATES: Dict[str, float] = {"fun_potential": 5, "feasibility": 4}

# Evidence level -> maximum fun_potential score allowed (house rule).
EVIDENCE_CAPS: Dict[str, float] = {"none": 7, "paper": 8, "greybox": 9, "playtest": 10}

W_RC, W_HC, W_SF = 0.35, 0.35, 0.30
PEN_V, PEN_L = 15.0, 20.0


class InputError(ValueError):
    """Malformed user input (exit code 2)."""


# --------------------------------------------------------------------------- helpers

def _num(value: Any, name: str, lo: float, hi: float) -> float:
    try:
        x = float(value)
    except (TypeError, ValueError):
        raise InputError(f"{name} must be a number, got {value!r}")
    if x < lo or x > hi:
        raise InputError(f"{name} must be in [{lo}, {hi}], got {x}")
    return x


def parse_kv(text: Optional[str], name: str) -> Dict[str, float]:
    """Parse "a=1,b=2.5" into a dict of floats."""
    out: Dict[str, float] = {}
    if not text:
        return out
    for part in text.split(","):
        part = part.strip()
        if not part:
            continue
        if "=" not in part:
            raise InputError(f"{name}: expected key=value, got {part!r}")
        k, v = part.split("=", 1)
        k = k.strip()
        if k not in CRITERIA:
            raise InputError(f"{name}: unknown criterion {k!r}; valid: {', '.join(CRITERIA)}")
        try:
            out[k] = float(v)
        except ValueError:
            raise InputError(f"{name}: value for {k!r} is not a number: {v!r}")
    return out


def load_json(path: Path) -> Any:
    try:
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        raise InputError(f"file not found: {path}")
    except json.JSONDecodeError as exc:
        raise InputError(f"invalid JSON in {path}: {exc}")


def save_json_atomic(path: Path, data: Any) -> None:
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp_", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        os.replace(tmp, str(path))
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


# --------------------------------------------------------------------------- fitness

def afs(rc: float, hc: float, sf: float, violations: int = 0, leakage: float = 0.0,
        hard_violations: int = 0) -> Dict[str, Any]:
    rc = _num(rc, "rc", 0, 1)
    hc = _num(hc, "hc", 0, 1)
    sf = _num(sf, "sf", 0, 1)
    leakage = _num(leakage, "leakage", 0, 1)
    if violations < 0 or hard_violations < 0:
        raise InputError("violation counts must be >= 0")
    raw = 100.0 * (W_RC * rc + W_HC * hc + W_SF * sf) - PEN_V * violations - PEN_L * leakage
    score = max(0.0, min(100.0, raw))
    if hard_violations > 0:
        verdict = "DROP"
        reason = f"{hard_violations} hard violation(s) (ethics/legal/platform policy)"
    elif score >= 70:
        verdict, reason = "GO", "structure and fit sufficient; prototype or simulate"
    elif score >= 50:
        verdict, reason = "ADAPT", "repair missing relations or support, then re-score (max two cycles)"
    else:
        verdict, reason = "DROP", "choose another source or another relation"
    diagnosis: List[str] = []
    if rc >= 0.75 and hc < 0.5:
        diagnosis.append("high RC, low HC: parts transfer but not the reason they matter; rebuild the causal link")
    if hc >= 0.75 and sf < 0.5:
        diagnosis.append("high HC, low SF: sound idea, target cannot host it; change target structure")
    if leakage > 0.25:
        diagnosis.append("high surface leakage: theme carries the analogy; strip attribute rows and re-score")
    if violations >= 2:
        diagnosis.append("two or more constraint violations: run platform translation (OP10) first")
    return {
        "rc": round(rc, 4), "hc": round(hc, 4), "sf": round(sf, 4),
        "violations": violations, "hard_violations": hard_violations,
        "leakage": round(leakage, 4), "afs": round(score, 1),
        "verdict": verdict, "reason": reason, "diagnosis": diagnosis,
    }


def _status_value(status: Any, where: str) -> float:
    s = str(status).strip().lower()
    if s == "mapped":
        return 1.0
    if s == "partial":
        return 0.5
    if s == "unmapped":
        return 0.0
    raise InputError(f"{where}: status must be mapped|partial|unmapped, got {status!r}")


def _present_value(present: Any, where: str) -> float:
    if present is True:
        return 1.0
    if present is False:
        return 0.0
    if isinstance(present, str) and present.strip().lower() == "partial":
        return 0.5
    raise InputError(f"{where}: present must be true|false|\"partial\", got {present!r}")


def afs_from_mapping(doc: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(doc, dict):
        raise InputError("mapping must be a JSON object")
    rels = doc.get("relations")
    if not isinstance(rels, list) or not rels:
        raise InputError("mapping.relations must be a non-empty list")
    first_n = first_m = high_n = high_m = 0.0
    mapped_rows = surface_rows = 0
    for i, r in enumerate(rels):
        where = f"relations[{i}]"
        if not isinstance(r, dict):
            raise InputError(f"{where} must be an object")
        order = r.get("order", 1)
        if order not in (0, 1, 2):
            raise InputError(f"{where}.order must be 0 (attribute), 1 or 2")
        val = _status_value(r.get("status", "unmapped"), where)
        surface = bool(r.get("surface_only", False)) or order == 0
        if val > 0:
            mapped_rows += 1
            if surface:
                surface_rows += 1
        if surface or not r.get("essential", False):
            continue
        if order == 1:
            first_n += 1
            first_m += val
        elif order == 2:
            high_n += 1
            high_m += val
    if first_n == 0 and high_n == 0:
        raise InputError("mapping has no essential first- or higher-order relations")
    rc = first_m / first_n if first_n else 1.0
    hc = high_m / high_n if high_n else 1.0
    support = doc.get("support", [])
    if not isinstance(support, list):
        raise InputError("mapping.support must be a list")
    if support:
        sf = sum(_present_value(s.get("present"), f"support[{j}]") if isinstance(s, dict)
                 else _present_value(None, f"support[{j}]") for j, s in enumerate(support)) / len(support)
    else:
        sf = 1.0
    viol = doc.get("violations", [])
    if not isinstance(viol, list):
        raise InputError("mapping.violations must be a list")
    hard = sum(1 for v in viol if isinstance(v, dict) and v.get("hard") is True)
    soft = len(viol) - hard
    leakage = surface_rows / mapped_rows if mapped_rows else 0.0
    res = afs(rc, hc, sf, violations=soft, leakage=leakage, hard_violations=hard)
    res["source"] = doc.get("source")
    res["target"] = doc.get("target")
    res["counts"] = {
        "essential_first_order": first_n, "essential_higher_order": high_n,
        "support_items": len(support), "mapped_rows": mapped_rows, "surface_rows": surface_rows,
    }
    return res


# --------------------------------------------------------------------------- concept

def resolve_weights(preset: str, custom: Optional[str]) -> Dict[str, float]:
    if preset not in PRESETS:
        raise InputError(f"unknown preset {preset!r}; valid: {', '.join(PRESETS)}")
    w = dict(PRESETS[preset])
    w.update(parse_kv(custom, "--weights"))
    if any(v < 0 for v in w.values()):
        raise InputError("weights must be >= 0")
    if sum(w.values()) <= 0:
        raise InputError("weights must not all be zero")
    return w


def score_concept(scores: Dict[str, Any], weights: Dict[str, float],
                  gates: Optional[Dict[str, float]] = None,
                  evidence: Optional[str] = None) -> Dict[str, Any]:
    if not isinstance(scores, dict):
        raise InputError("scores must be an object")
    missing = [c for c in CRITERIA if c not in scores]
    if missing:
        raise InputError(f"scores missing: {', '.join(missing)}")
    vals: Dict[str, float] = {c: _num(scores[c], f"scores.{c}", 1, 10) for c in CRITERIA}
    notes: List[str] = []
    if evidence is not None:
        if evidence not in EVIDENCE_CAPS:
            raise InputError(f"unknown evidence level {evidence!r}; valid: {', '.join(EVIDENCE_CAPS)}")
        cap = EVIDENCE_CAPS[evidence]
        if vals["fun_potential"] > cap:
            notes.append(f"fun_potential capped {vals['fun_potential']} -> {cap} (evidence: {evidence})")
            vals["fun_potential"] = cap
    total_w = sum(weights.get(c, 0.0) for c in CRITERIA)
    weighted = sum(vals[c] * weights.get(c, 0.0) for c in CRITERIA) / total_w
    gates = DEFAULT_GATES if gates is None else gates
    failed = [f"{k} {vals[k]} < {v}" for k, v in gates.items() if vals[k] < v]
    return {
        "scores": vals, "weights": weights, "weighted_total": round(weighted, 2),
        "gates": gates, "gate_failures": failed, "passes_gates": not failed, "notes": notes,
    }


def concept_from_card(path: Path, preset: str, custom: Optional[str], gates_text: Optional[str],
                      evidence: Optional[str], write: bool) -> Dict[str, Any]:
    card = load_json(path)
    if not isinstance(card, dict):
        raise InputError(f"{path}: concept card must be a JSON object")
    scores = card.get("scores")
    if not isinstance(scores, dict):
        raise InputError(f"{path}: missing scores object")
    weights = resolve_weights(preset, custom)
    gates = dict(DEFAULT_GATES)
    gates.update(parse_kv(gates_text, "--gate"))
    res = score_concept(scores, weights, gates, evidence)
    res["id"] = card.get("id")
    res["title"] = card.get("title")
    res["preset"] = preset
    res["path"] = str(path)
    if write:
        card["scores"]["weighted_total"] = res["weighted_total"]
        save_json_atomic(path, card)
        res["written"] = True
    return res


def cards_in_dir(directory: Path) -> List[Path]:
    """Prefer *.concept.json; otherwise every *.json except *.mapping.json."""
    cards = sorted(directory.glob("*.concept.json"))
    if cards:
        return cards
    return sorted(p for p in directory.glob("*.json") if not p.name.endswith(".mapping.json"))


def rank_cards(paths: List[Path], preset: str, custom: Optional[str],
               evidence: Optional[str]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    weights = resolve_weights(preset, custom)
    for p in paths:
        try:
            card = load_json(p)
            res = score_concept(card.get("scores", {}) if isinstance(card, dict) else {},
                                weights, None, evidence)
            rows.append({"id": card.get("id"), "title": card.get("title"), "path": str(p),
                         "weighted_total": res["weighted_total"],
                         "passes_gates": res["passes_gates"],
                         "gate_failures": res["gate_failures"]})
        except InputError as exc:
            rows.append({"id": None, "title": None, "path": str(p), "error": str(exc)})
    ok = [r for r in rows if "error" not in r]
    bad = [r for r in rows if "error" in r]
    ok.sort(key=lambda r: (not r["passes_gates"], -r["weighted_total"]))
    return ok + bad


# --------------------------------------------------------------------------- output

def print_fitness(res: Dict[str, Any]) -> None:
    src = f"{res.get('source')} -> {res.get('target')}" if res.get("source") else "mapping"
    print(f"AFS {res['afs']}  verdict {res['verdict']}  ({src})")
    print(f"  RC {res['rc']}  HC {res['hc']}  SF {res['sf']}  V {res['violations']}  "
          f"hard {res['hard_violations']}  L {res['leakage']}")
    print(f"  {res['reason']}")
    for d in res["diagnosis"]:
        print(f"  - {d}")


def print_concept(res: Dict[str, Any]) -> None:
    label = res.get("title") or res.get("id") or "concept"
    print(f"{label}: weighted_total {res['weighted_total']} (preset {res.get('preset', 'custom')})")
    print("  " + "  ".join(f"{c}={res['scores'][c]:g}x{res['weights'][c]:g}" for c in CRITERIA))
    for n in res["notes"]:
        print(f"  note: {n}")
    if res["gate_failures"]:
        print("  GATE FAIL: " + "; ".join(res["gate_failures"]))
    else:
        print("  gates: pass")


# --------------------------------------------------------------------------- selftest

def selftest() -> int:
    checks: List[Tuple[str, bool]] = []

    a = afs(1.0, 2 / 3, 0.75)
    checks.append(("worked example A before adapt ~80.8 GO", abs(a["afs"] - 80.8) < 0.11 and a["verdict"] == "GO"))
    b = afs(1.0, 2.5 / 3, 0.875)
    checks.append(("worked example A after adapt ~90.4", abs(b["afs"] - 90.4) < 0.11))
    c = afs(0.5, 0.5, 0.5, violations=1)
    checks.append(("violation penalty 50 - 15 = 35 -> DROP", c["afs"] == 35.0 and c["verdict"] == "DROP"))
    d = afs(1, 1, 1, hard_violations=1)
    checks.append(("hard violation forces DROP", d["verdict"] == "DROP"))
    e = afs(0.2, 0.1, 0.2, violations=3, leakage=1.0)
    checks.append(("clamped at 0", e["afs"] == 0.0 and e["verdict"] == "DROP"))
    f = afs(0.7, 0.6, 0.6)
    checks.append(("ADAPT 50-70", f["verdict"] == "ADAPT" and 50 <= f["afs"] < 70))

    mapping = {
        "source": "Marvel Snap", "target": "async word duel",
        "relations": [
            {"id": "R1", "order": 1, "essential": True, "status": "mapped"},
            {"id": "R2", "order": 1, "essential": True, "status": "mapped"},
            {"id": "R3", "order": 1, "essential": True, "status": "mapped"},
            {"id": "R4", "order": 1, "essential": True, "status": "mapped"},
            {"id": "H1", "order": 2, "essential": True, "status": "mapped"},
            {"id": "H2", "order": 2, "essential": True, "status": "mapped"},
            {"id": "H3", "order": 2, "essential": True, "status": "unmapped"},
        ],
        "support": [{"id": "S1", "present": True}, {"id": "S2", "present": True},
                    {"id": "S3", "present": True}, {"id": "S4", "present": False}],
        "violations": [],
    }
    m = afs_from_mapping(mapping)
    checks.append(("mapping file equals summary numbers", abs(m["afs"] - a["afs"]) < 0.01))
    mapping2 = json.loads(json.dumps(mapping))
    mapping2["relations"].append({"id": "A1", "order": 0, "essential": False, "status": "mapped"})
    m2 = afs_from_mapping(mapping2)
    checks.append(("surface row adds leakage 1/7", abs(m2["leakage"] - 1 / 7) < 1e-3 and m2["afs"] < m["afs"]))
    mapping3 = json.loads(json.dumps(mapping))
    mapping3["violations"] = [{"id": "V1", "kind": "ethics", "hard": True}]
    checks.append(("mapping hard violation DROP", afs_from_mapping(mapping3)["verdict"] == "DROP"))
    try:
        afs_from_mapping({"relations": [{"id": "x", "order": 1, "essential": True, "status": "maybe"}]})
        checks.append(("bad status rejected", False))
    except InputError:
        checks.append(("bad status rejected", True))

    example = {"market": 7, "novelty": 6, "fun_potential": 8, "feasibility": 8,
               "monetization": 7, "production_cost": 7, "agent_buildability": 9}
    r = score_concept(example, PRESETS["default"])
    checks.append(("example concept default = 7.47", r["weighted_total"] == 7.47 and r["passes_gates"]))
    r2 = score_concept(example, PRESETS["default"], evidence="none")
    checks.append(("evidence cap lowers fun to 7", r2["scores"]["fun_potential"] == 7 and r2["weighted_total"] < 7.47))
    low = dict(example, fun_potential=4)
    checks.append(("gate failure on fun 4", not score_concept(low, PRESETS["default"])["passes_gates"]))
    try:
        score_concept(dict(example, market=11), PRESETS["default"])
        checks.append(("out-of-range rejected", False))
    except InputError:
        checks.append(("out-of-range rejected", True))
    w = resolve_weights("default", "market=3")
    checks.append(("custom weight override", w["market"] == 3 and w["fun_potential"] == 2))
    try:
        parse_kv("speed=2", "--weights")
        checks.append(("unknown criterion rejected", False))
    except InputError:
        checks.append(("unknown criterion rejected", True))

    # rank + write round trip in a temp dir
    with tempfile.TemporaryDirectory() as td:
        p1 = Path(td) / "a.json"
        p2 = Path(td) / "b.json"
        p1.write_text(json.dumps({"id": "a", "title": "A", "scores": example}), encoding="utf-8")
        p2.write_text(json.dumps({"id": "b", "title": "B", "scores": dict(example, fun_potential=10)}),
                      encoding="utf-8")
        ranked = rank_cards([p1, p2], "default", None, None)
        checks.append(("rank orders by total", [x["id"] for x in ranked] == ["b", "a"]))
        (Path(td) / "a.mapping.json").write_text(json.dumps(mapping), encoding="utf-8")
        checks.append(("dir scan skips mapping files", [p.name for p in cards_in_dir(Path(td))] == ["a.json", "b.json"]))
        res = concept_from_card(p1, "default", None, None, None, write=True)
        stored = json.loads(p1.read_text(encoding="utf-8"))["scores"].get("weighted_total")
        checks.append(("write stores weighted_total", res.get("written") and stored == 7.47))

    ok = True
    for name, passed in checks:
        print(f"[{'PASS' if passed else 'FAIL'}] {name}")
        ok = ok and passed
    print("selftest:", "ok" if ok else "FAILED")
    return 0 if ok else 1


# --------------------------------------------------------------------------- CLI

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Analogy Fitness Score and concept scoring (analogy-engine).")
    p.add_argument("--selftest", action="store_true", help="run built-in tests and exit")
    sub = p.add_subparsers(dest="cmd")

    f = sub.add_parser("fitness", help="Analogy Fitness Score for a mapping")
    f.add_argument("--mapping", type=Path, help="mapping JSON (analogy-method.md section 15.5)")
    f.add_argument("--rc", type=float, help="relational coverage 0-1")
    f.add_argument("--hc", type=float, help="higher-order coverage 0-1")
    f.add_argument("--sf", type=float, help="support fit 0-1")
    f.add_argument("--violations", type=int, default=0, help="soft constraint violations")
    f.add_argument("--hard-violations", type=int, default=0, help="ethics/legal/policy violations")
    f.add_argument("--leakage", type=float, default=0.0, help="surface leakage 0-1")
    f.add_argument("--json", action="store_true")

    c = sub.add_parser("concept", help="weighted total for one concept card or inline scores")
    src = c.add_mutually_exclusive_group(required=True)
    src.add_argument("--card", type=Path, help="concept card JSON (concept.schema.json)")
    src.add_argument("--scores", help='inline "market=7,novelty=6,..." (all seven criteria)')
    c.add_argument("--preset", default="default", choices=sorted(PRESETS))
    c.add_argument("--weights", help='override weights, e.g. "market=2,fun_potential=3"')
    c.add_argument("--gate", help='minimum scores, e.g. "fun_potential=6,feasibility=5"')
    c.add_argument("--evidence", choices=sorted(EVIDENCE_CAPS), help="cap fun_potential by evidence level")
    c.add_argument("--write", action="store_true", help="store scores.weighted_total in the card")
    c.add_argument("--json", action="store_true")

    r = sub.add_parser("rank", help="rank concept cards")
    r.add_argument("paths", nargs="*", type=Path, help="card files")
    r.add_argument("--dir", type=Path,
                   help="directory of concept cards (*.concept.json, else *.json minus *.mapping.json)")
    r.add_argument("--preset", default="default", choices=sorted(PRESETS))
    r.add_argument("--weights")
    r.add_argument("--evidence", choices=sorted(EVIDENCE_CAPS))
    r.add_argument("--json", action="store_true")
    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.cmd:
        parser.print_help()
        return 2
    try:
        if args.cmd == "fitness":
            if args.mapping:
                res = afs_from_mapping(load_json(args.mapping))
            else:
                if args.rc is None or args.hc is None or args.sf is None:
                    raise InputError("give --mapping, or all of --rc --hc --sf")
                res = afs(args.rc, args.hc, args.sf, args.violations, args.leakage, args.hard_violations)
            if args.json:
                print(json.dumps(res, indent=2))
            else:
                print_fitness(res)
            return 1 if res["verdict"] == "DROP" else 0
        if args.cmd == "concept":
            if args.card:
                res = concept_from_card(args.card, args.preset, args.weights, args.gate,
                                        args.evidence, args.write)
            else:
                if args.write:
                    raise InputError("--write needs --card")
                gates = dict(DEFAULT_GATES)
                gates.update(parse_kv(args.gate, "--gate"))
                res = score_concept(parse_kv(args.scores, "--scores"),
                                    resolve_weights(args.preset, args.weights), gates, args.evidence)
                res["preset"] = args.preset
            if args.json:
                print(json.dumps(res, indent=2))
            else:
                print_concept(res)
            return 0 if res["passes_gates"] else 1
        if args.cmd == "rank":
            paths = list(args.paths)
            if args.dir:
                if not args.dir.is_dir():
                    raise InputError(f"not a directory: {args.dir}")
                paths += cards_in_dir(args.dir)
            if not paths:
                raise InputError("no concept cards given")
            rows = rank_cards(paths, args.preset, args.weights, args.evidence)
            if not any("error" not in r for r in rows):
                raise InputError("no valid concept cards: " + "; ".join(r["error"] for r in rows))
            if args.json:
                print(json.dumps(rows, indent=2))
            else:
                for i, row in enumerate(rows, 1):
                    if "error" in row:
                        print(f"  -  {row['path']}: ERROR {row['error']}")
                    else:
                        flag = "" if row["passes_gates"] else "  [gate fail: " + "; ".join(row["gate_failures"]) + "]"
                        print(f"{i:>3}. {row['weighted_total']:>5.2f}  {row['title'] or row['id']}{flag}")
            return 0
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
