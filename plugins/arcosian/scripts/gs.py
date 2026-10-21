#!/usr/bin/env python3
"""gs.py - project-state CLI for the arcosian plugin (stdlib only, Python 3.9+).

Owns the `.gamestudio/` directory of a game project: design contract,
feature list with the five-gate definition of done, progress log, budget
ledger, asset manifest, evidence folders, and a ranked search over the
plugin's codex skills.  All state logic lives in `gslib.py`; this file is the
command line on top of it (BLUEPRINT section 8).

    gs.py init --title "Name" --engine godot|unity|other [--genre G] [--root DIR] [--force]
    gs.py status [--json]
    gs.py validate [--all | PATH ...] [--schema NAME] [--cross]
    gs.py feature list [--status S] [--area A] [--priority P] [--json]
    gs.py feature add --id F001 --title T --area A [--priority P0] [--accept "..."]... [--depends F001,F002] [--desc TEXT]
    gs.py feature next [--json]
    gs.py feature start F001 [--reopen]
    gs.py feature gate F001 <static|unit|playthrough|visual|perf> <pass|fail|n/a|reset> [--evidence PATH]... [--note TEXT]
    gs.py feature pass F001
    gs.py feature block F001 --reason TEXT
    gs.py feature show F001
    gs.py evidence-dir F001
    gs.py progress "text"
    gs.py budget [--json]
    gs.py kb "query" [--skill NAME] [--limit N] [--json]
    gs.py summary [--max-chars N]

`validate --cross` adds the cross-document checks of gslib.cross_check (unique ids, feature dependencies, level
mechanic_refs, economy vs contract, manifest and evidence paths on disk); errors make it exit 1.

Every command accepts --root DIR (project root; default: the nearest
ancestor of the current directory that contains .gamestudio/, then
$GS_PROJECT_ROOT, then $CLAUDE_PROJECT_DIR) and --json.
Exit codes: 0 ok, 1 check failed (gate refused, validation errors, over
budget, already initialised), 2 usage or input error.
Run `python3 gs.py --selftest` to exercise the CLI end to end.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.dont_write_bytecode = True  # keep the installed plugin tree free of __pycache__
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
import gslib as G  # noqa: E402

__version__ = G.__version__
GS_CMD = 'python3 "%s"' % (_HERE / "gs.py")


class CliError(Exception):
    """User-facing error; `code` becomes the exit status (2 = usage/input)."""

    def __init__(self, message: str, code: int = 2) -> None:
        super().__init__(message)
        self.code = code


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def _emit(args: argparse.Namespace, data: Any, text: Optional[str]) -> None:
    if getattr(args, "json", False):
        print(json.dumps(data, indent=2, ensure_ascii=False, default=str))
    elif text:
        print(text)


def _note(msg: str) -> None:
    print("gs: %s" % msg, file=sys.stderr)


def _find_root(args: argparse.Namespace) -> Path:
    starts: List[str] = []
    if getattr(args, "root", None):
        starts.append(args.root)
    else:
        starts.append(os.getcwd())
        for env in ("GS_PROJECT_ROOT", "CLAUDE_PROJECT_DIR"):
            if os.environ.get(env):
                starts.append(os.environ[env])
    for s in starts:
        r = G.find_project_root(s)
        if r is not None:
            return r
    raise CliError("no %s/ directory found from %s; create one with: gs.py init --title \"Name\" "
                   "--engine godot --platforms <list>" % (G.GS_DIRNAME, starts[0]))


def _fid(value: str) -> str:
    try:
        return G.normalize_feature_id(value)
    except ValueError as exc:
        raise CliError(str(exc))


def _load_features(root: Path) -> Dict[str, Any]:
    path = G.state_path(root, "features")
    try:
        doc = G.load_json(path, None, strict=True)
    except ValueError as exc:
        raise CliError("%s; fix or restore it (backups live in .gamestudio/snapshots/) before changing "
                       "features" % exc)
    if doc is None:
        doc = G.empty_features()
    if not isinstance(doc, dict) or not isinstance(doc.get("features"), list):
        raise CliError("features.json must be an object with a 'features' array")
    return doc


def _save_features(root: Path, doc: Dict[str, Any]) -> None:
    G.save_json(G.state_path(root, "features"), doc)


def _get_feature(doc: Dict[str, Any], fid: str) -> Dict[str, Any]:
    f = G.find_feature(doc, _fid(fid))
    if f is None:
        raise CliError("unknown feature %s (see: gs.py feature list)" % _fid(fid))
    return f


def _split_ids(values: Optional[List[str]]) -> List[str]:
    out: List[str] = []
    for v in values or []:
        for part in str(v).replace(";", ",").split(","):
            if part.strip():
                out.append(_fid(part))
    return out


def _money(x: Any) -> str:
    try:
        return "$%.2f" % float(x)
    except (TypeError, ValueError):
        return "$?"


def _rel(path: Path, root: Path) -> str:
    return G.rel_to_root(path, root)


# --------------------------------------------------------------------------
# init
# --------------------------------------------------------------------------

def cmd_init(args: argparse.Namespace) -> int:
    root = Path(args.root or os.getcwd()).expanduser()
    root = root if root.is_absolute() else Path.cwd() / root
    try:
        root.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise CliError("cannot create project root %s: %s" % (root, exc))
    root = root.resolve()
    outer = G.find_project_root(root.parent) if root.parent != root else None
    platforms = [p for p in (args.platforms or "").split(",") if p.strip()]
    if not platforms:
        raise CliError("choose the target platforms with --platforms, any combination of %s. Ask the user: "
                       "platforms drive input, UI, performance budgets and release steps (skill "
                       "platform-targets)." % ", ".join(G.PLATFORMS))
    inputs = [i for i in (args.input or "").split(",") if i.strip()] or None
    try:
        res = G.init_project(
            root, args.title, args.engine, args.genre, force=args.force, slug=args.slug,
            engine_version=args.engine_version, platforms=platforms, orientation=args.orientation,
            input_methods=inputs,
            tier=args.tier, monetization_model=args.monetization, asset_usd_cap=args.budget,
            per_call_usd_cap=args.per_call_cap)
    except ValueError as exc:
        raise CliError(str(exc))
    except OSError as exc:
        raise CliError("cannot initialise %s: %s" % (root / G.GS_DIRNAME, exc))
    nothing = not res["created"] and not res["dirs_created"]
    res["already_initialized"] = nothing
    lines = []
    if nothing:
        lines.append("Project already initialised at %s - nothing overwritten." % res["gs_dir"])
        lines.append("Use --force to rewrite the skeleton documents (previous versions are backed up "
                     "to .gamestudio/snapshots/; progress.md is never truncated).")
    else:
        lines.append("Initialised %s (engine %s)." % (res["gs_dir"], res["engine"]))
        lines.append("  platforms:   %s | input: %s | orientation: %s" % (
            ", ".join(res["platforms"]), ", ".join(res["input"]), res["orientation"]))
        if res["created"]:
            lines.append("  created:     " + ", ".join(res["created"]))
        elif res["dirs_created"]:
            lines.append("  added missing directories: " + ", ".join(res["dirs_created"]))
        if res["overwritten"]:
            lines.append("  overwritten: " + ", ".join(res["overwritten"]) + "  (backup: %s)"
                         % _rel(Path(res["backup_dir"]), root))
        if res["skipped"]:
            lines.append("  kept:        " + ", ".join(res["skipped"]) + "  (use --force to overwrite)")
    if outer is not None:
        lines.append("Note: an enclosing project already exists at %s; commands run from this folder "
                     "will use %s." % (outer, root))
    tpl = G.PLUGIN_ROOT / "templates" / ("%s-starter" % res["engine"])
    lines += [
        "",
        "Next steps (gs.py = %s):" % GS_CMD,
        "  1. Fill the design contract: /arcosian:new-game, or edit .gamestudio/contract.json "
        "(TBD fields), then gs.py validate",
        "  2. Plan features: gs.py feature add --id F001 --title \"Core loop prototype\" --area gameplay "
        "--priority P0 --accept \"one full loop playable in under 60 s\"",
        "  3. Pick work: gs.py feature next ; gs.py feature start F001",
        "  4. Prove each gate: gs.py evidence-dir F001 ; gs.py feature gate F001 static pass "
        "--evidence .gamestudio/evidence/F001/static.log",
        "  5. Close it: gs.py feature pass F001 ; gs.py progress \"what changed, what was verified\"",
    ]
    if tpl.is_dir():
        lines.append("  Engine template: %s (copy it in if the game project is empty)." % tpl)
    _emit(args, res, "\n".join(lines))
    return 1 if nothing else 0


# --------------------------------------------------------------------------
# status / summary / budget
# --------------------------------------------------------------------------

def _status_data(root: Path) -> Dict[str, Any]:
    st = G.load_state(root)
    cfg = st["config"] if isinstance(st["config"], dict) else {}
    con = st["contract"] if isinstance(st["contract"], dict) else {}
    meta = con.get("meta") if isinstance(con.get("meta"), dict) else {}
    proj = cfg.get("project") if isinstance(cfg.get("project"), dict) else {}
    feats = st["features"]
    nf = G.next_feature(feats)
    return {
        "root": str(root),
        "title": meta.get("title") or proj.get("title") or root.name,
        "genre": meta.get("genre"),
        "engine": cfg.get("engine") or meta.get("engine"),
        "engine_version": cfg.get("engine_version"),
        "platforms": cfg.get("platforms") or meta.get("platforms") or [],
        "orientation": cfg.get("orientation") or meta.get("orientation"),
        "tier": cfg.get("tier") or (con["scope"].get("tier") if isinstance(con.get("scope"), dict) else None),
        "features_readable": feats is not None,
        "counts": G.feature_counts(feats),
        "next": {"id": nf.get("id"), "title": nf.get("title"), "priority": nf.get("priority"),
                 "area": nf.get("area")} if nf else None,
        "in_progress": [{"id": f.get("id"), "title": f.get("title"), "open_gates": G.open_gates(f)}
                        for f in G.get_features(feats) if f.get("status") == "in_progress"],
        "blocked": [{"id": f.get("id"), "title": f.get("title")}
                    for f in G.get_features(feats) if f.get("status") == "blocked"],
        "failing_gates": [{"id": fid, "gates": gates} for fid, gates in G.failing_gates(feats)],
        "dod_violations": [{"id": fid, "problems": probs} for fid, probs in G.dod_violations(feats, root)],
        "budget": G.budget_summary(st["budget"], cfg),
        "progress": G.read_progress_entries(root, 5),
    }


def cmd_status(args: argparse.Namespace) -> int:
    root = _find_root(args)
    d = _status_data(root)
    c = d["counts"]
    head = [str(x) for x in (d["engine"], d["engine_version"]) if x]
    plat = "/".join(d["platforms"]) if isinstance(d["platforms"], list) else str(d["platforms"])
    lines = ["%s  (%s | %s | %s | tier %s)" % (d["title"], " ".join(head) or "engine?", plat or "platforms?",
                                               d["orientation"] or "orientation?", d["tier"] or "?"),
             "root: %s" % d["root"]]
    if not d["features_readable"]:
        lines.append("Features     features.json missing or unreadable (run gs.py validate)")
    else:
        lines.append("Features     %d total | %d done | %d passing | %d in progress | %d blocked | %d todo"
                     % (c["total"], c["done"], c["passing"], c["in_progress"], c["blocked"], c["todo"]))
    for f in d["in_progress"][:5]:
        lines.append("In progress  %s %s  (open gates: %s)" % (f["id"], f["title"], ", ".join(f["open_gates"]) or "none"))
    if d["next"]:
        lines.append("Next         %s [%s] %s" % (d["next"]["id"], d["next"]["priority"], d["next"]["title"]))
    elif c["total"]:
        lines.append("Next         none ready (see gs.py feature next)")
    for f in d["blocked"][:5]:
        lines.append("Blocked      %s %s" % (f["id"], f["title"]))
    if d["failing_gates"]:
        lines.append("Failing      " + "; ".join("%s (%s)" % (x["id"], ", ".join(x["gates"])) for x in d["failing_gates"]))
    else:
        lines.append("Failing      none")
    for v in d["dod_violations"]:
        lines.append("DoD BROKEN   %s is marked done/passing but: %s" % (v["id"], "; ".join(v["problems"][:3])))
    b = d["budget"]
    pct = (" | %.1f%%" % b["pct_used"]) if b["pct_used"] is not None else ""
    lines.append("Budget       %s spent of %s cap | %s left%s" % (_money(b["spent_usd"]), _money(b["cap_usd"]),
                                                                _money(b["remaining_usd"]), pct))
    for w in b["warnings"]:
        lines.append("             warning: %s" % w)
    if d["progress"]:
        lines.append("Recent progress")
        lines += ["  " + e for e in d["progress"]]
    _emit(args, d, "\n".join(lines))
    return 0


def cmd_summary(args: argparse.Namespace) -> int:
    root = _find_root(args)
    text = G.summarize(root, args.max_chars)
    _emit(args, {"summary": text, "chars": len(text)}, text)
    return 0


# --------------------------------------------------------------------------
# understanding layer: project map, change impact, what-if, dashboard
# --------------------------------------------------------------------------

def cmd_map(args: argparse.Namespace) -> int:
    import project_map
    root = _find_root(args)
    doc = project_map.build(root)
    d = project_map.map_dir(root)
    data = dict(doc["stats"], engine=doc["engine"], summary=_rel(d / "MAP.md", root), graph=_rel(d / "map.json", root))
    _emit(args, data, "Mapped %d files (%d parsed, %d references, engine %s).\n  summary: %s\n  graph:   %s" % (
        data["files"], data["reparsed"], data["edges"], data["engine"], data["summary"], data["graph"]))
    return 0


def cmd_impact(args: argparse.Namespace) -> int:
    import project_map
    root = _find_root(args)
    res = project_map.impact(project_map.load(root, refresh=True), root, args.targets, max(1, args.depth))
    _emit(args, res, project_map.render_impact(res))
    return 1 if res["missing"] and not res["resolved"] else 0


def cmd_whatif(args: argparse.Namespace) -> int:
    import whatif
    root = _find_root(args)
    try:
        res = whatif.run(root, args.set, args.sim, args.runs, args.seeds, args.seed, args.bot, args.model,
                         args.level, args.label, args.tolerance, not args.no_save)
    except whatif.WhatIfError as exc:
        raise CliError(str(exc))
    _emit(args, res, whatif.render(res))
    return 1 if res["verdict"] == "reject" else 0


def cmd_dashboard(args: argparse.Namespace) -> int:
    import dashboard
    root = _find_root(args)
    path = dashboard.write(root, Path(args.out).resolve() if args.out else None, not args.no_map)
    _emit(args, {"path": str(path)}, "Dashboard written: %s\nOpen it in a browser; it works offline." % _rel(path, root))
    return 0


def cmd_budget(args: argparse.Namespace) -> int:
    root = _find_root(args)
    st = G.load_state(root)
    b = G.budget_summary(st["budget"], st["config"])
    lines = ["Asset budget  %s spent of %s cap  (%s left%s)" % (
        _money(b["spent_usd"]), _money(b["cap_usd"]), _money(b["remaining_usd"]),
        (", %.1f%%" % b["pct_used"]) if b["pct_used"] is not None else "")]
    if b["per_call_usd_cap"] is not None:
        lines.append("Per-call cap  %s" % _money(b["per_call_usd_cap"]))
    lines.append("Ledger        %d entr%s, total %s" % (b["ledger_entries"], "y" if b["ledger_entries"] == 1 else "ies",
                                                      _money(b["ledger_total_usd"])))
    if b["by_provider"]:
        lines.append("By provider   " + " | ".join("%s %s" % (k, _money(v)) for k, v in
                                                  sorted(b["by_provider"].items(), key=lambda kv: -kv[1])))
    if b["by_tool"]:
        lines.append("By tool       " + " | ".join("%s %s" % (k, _money(v)) for k, v in
                                                  sorted(b["by_tool"].items(), key=lambda kv: -kv[1])))
    if b["recent"]:
        lines.append("Recent")
        for e in b["recent"]:
            ids = e.get("asset_ids") or []
            lines.append("  %s  %s  %s/%s  %s%s%s" % (
                e.get("ts", "?"), e.get("tool", "?"), e.get("provider") or "-", e.get("model") or "-",
                _money(e.get("cost_usd")), ("  [%s]" % ", ".join(map(str, ids))) if ids else "",
                ("  " + str(e.get("note"))) if e.get("note") else ""))
    for w in b["warnings"]:
        lines.append("warning: %s" % w)
    _emit(args, b, "\n".join(lines))
    over = b["cap_usd"] > 0 and b["spent_usd"] > b["cap_usd"] + 1e-9
    return 1 if over else 0


# --------------------------------------------------------------------------
# validate
# --------------------------------------------------------------------------

def _resolve_schema_arg(value: str) -> Path:
    p = Path(value).expanduser()
    if p.is_file():
        return p.resolve()
    key = value[:-len(".schema.json")] if value.endswith(".schema.json") else value
    key = G._DECLARED_KEYS.get(key, key)
    found = G._find_schema(key) or (G.SCHEMAS_DIR / ("%s.schema.json" % value))
    if not Path(found).is_file():
        avail = sorted(x.name[:-len(".schema.json")] for x in G.SCHEMAS_DIR.glob("*.schema.json"))
        raise CliError("unknown schema %r; available: %s" % (value, ", ".join(avail) or "(none)"))
    return Path(found)


def cmd_validate(args: argparse.Namespace) -> int:
    try:
        root: Optional[Path] = _find_root(args)
    except CliError:
        root = None
    avail, verr = G.validator_available()
    targets: List[Path] = []
    whole_project = args.all or not args.paths
    if whole_project:
        if root is None:
            raise CliError("no %s/ project found; pass file paths or --root" % G.GS_DIRNAME)
        g = G.gs_dir(root)
        targets = sorted(p for p in g.rglob("*.json") if "snapshots" not in p.relative_to(g).parts)
    for raw in args.paths or []:
        p = Path(raw).expanduser()
        if not p.is_absolute():
            p = (Path.cwd() / p) if (Path.cwd() / p).exists() or root is None else (root / p)
        if p.is_dir():
            targets += sorted(x for x in p.rglob("*.json") if not x.name.endswith(".schema.json"))
        else:
            targets.append(p)
    forced = _resolve_schema_arg(args.schema) if args.schema else None
    mod = G._load_validator() if avail else None
    results = []
    n_fail = n_unchecked = 0
    for t in targets:
        disp = _rel(t, root) if root else str(t)
        entry: Dict[str, Any] = {"path": disp, "schema": None, "status": "ok", "errors": []}
        try:
            instance = json.loads(t.read_text(encoding="utf-8"))
        except FileNotFoundError:
            entry.update(status="fail", errors=["file not found"])
        except (ValueError, UnicodeDecodeError) as exc:
            entry.update(status="fail", errors=["invalid JSON: %s" % exc])
        except OSError as exc:
            entry.update(status="fail", errors=["cannot read: %s" % exc])
        if entry["status"] == "fail":
            n_fail += 1
            results.append(entry)
            continue
        sp = forced or G.schema_for(t)
        if sp is None:
            entry["status"] = "skip"
        else:
            entry["schema"] = Path(sp).name
            if mod is None:
                entry["status"] = "unchecked"
                n_unchecked += 1
            else:
                try:
                    schema = json.loads(Path(sp).read_text(encoding="utf-8"))
                    errs = [str(e) for e in (mod.validate(instance, schema, Path(sp).parent) or [])]
                except Exception as exc:  # validator or schema problem: report, do not crash
                    errs = ["validator error: %s: %s" % (type(exc).__name__, exc)]
                if errs:
                    entry.update(status="fail", errors=errs)
                    n_fail += 1
        results.append(entry)
    lint_errors: List[str] = []
    lint_warnings: List[str] = []
    fpath = G.state_path(root, "features") if root else None
    if root is not None and (whole_project or any(_abspath_eq(t, fpath) for t in targets)):
        fdoc = G.load_json(fpath, None)
        if fdoc is not None:
            lint_errors, lint_warnings = G.lint_features(fdoc, root)
        b = G.budget_summary(G.load_json(G.state_path(root, "budget"), None),
                             G.load_json(G.state_path(root, "config"), None))
        lint_warnings += ["budget: %s" % w for w in b["warnings"]]
    cross_errors: List[str] = []
    cross_warnings: List[str] = []
    if args.cross:
        if root is None:
            raise CliError("--cross needs a project: no %s/ directory found (use --root DIR)" % G.GS_DIRNAME)
        for severity, msg in G.cross_check(root):
            # features.json messages repeat what the features rules above already reported: show each once
            core = msg.split(": ", 1)[-1]
            if msg.startswith("features.json ") and any(core in e for e in lint_errors):
                continue
            (cross_errors if severity == "error" else cross_warnings).append(msg)
    data = {"files": results, "features_lint": {"errors": lint_errors, "warnings": lint_warnings},
            "validator_available": avail, "validator_error": verr,
            "summary": {"files": len(results), "failed": n_fail, "unchecked": n_unchecked,
                        "skipped": sum(1 for r in results if r["status"] == "skip"),
                        "lint_errors": len(lint_errors)}}
    if args.cross:
        data["cross"] = {"errors": cross_errors, "warnings": cross_warnings}
        data["summary"]["cross_errors"] = len(cross_errors)
    lines = []
    if not avail:
        lines.append("warning: schema validator unavailable (%s); JSON syntax and feature rules still checked"
                     % verr)
    for r in results:
        tag = {"ok": "OK  ", "fail": "FAIL", "skip": "SKIP", "unchecked": "????"}[r["status"]]
        extra = " (%s)" % r["schema"] if r["schema"] else (" (no schema)" if r["status"] == "skip" else "")
        lines.append("%s  %s%s" % (tag, r["path"], extra))
        for e in r["errors"][:25]:
            lines.append("      - %s" % e)
        if len(r["errors"]) > 25:
            lines.append("      ... %d more" % (len(r["errors"]) - 25))
    if lint_errors or lint_warnings:
        lines.append("features/budget rules: %d error(s), %d warning(s)" % (len(lint_errors), len(lint_warnings)))
        lines += ["  error: %s" % e for e in lint_errors]
        lines += ["  warning: %s" % w for w in lint_warnings]
    if args.cross:
        if cross_errors or cross_warnings:
            lines.append("cross-document checks: %d error(s), %d warning(s)" % (len(cross_errors), len(cross_warnings)))
            lines += ["  error: %s" % e for e in cross_errors]
            lines += ["  warning: %s" % w for w in cross_warnings]
        else:
            lines.append("cross-document checks: ok")
    s = data["summary"]
    lines.append("Summary: %d file(s), %d failed, %d skipped (no schema), %d unchecked, %d rule error(s)%s"
                 % (s["files"], s["failed"], s["skipped"], s["unchecked"], s["lint_errors"],
                    (", %d cross-document error(s)" % len(cross_errors)) if args.cross else ""))
    _emit(args, data, "\n".join(lines))
    if n_fail or lint_errors or cross_errors:
        return 1
    if n_unchecked:
        return 2
    return 0


def _abspath_eq(a: Path, b: Optional[Path]) -> bool:
    if b is None:
        return False
    try:
        return Path(a).resolve() == Path(b).resolve()
    except OSError:
        return False


# --------------------------------------------------------------------------
# feature commands
# --------------------------------------------------------------------------

def cmd_feature_list(args: argparse.Namespace) -> int:
    root = _find_root(args)
    doc = _load_features(root)
    feats = G.get_features(doc)
    if args.status:
        feats = [f for f in feats if (f.get("status") or "todo") == args.status]
    if args.area:
        feats = [f for f in feats if f.get("area") == args.area]
    if args.priority:
        feats = [f for f in feats if f.get("priority") == args.priority]
    data = {"features": feats, "counts": G.feature_counts(doc)}
    if not feats:
        _emit(args, data, "No features%s." % (" match the filter" if (args.status or args.area or args.priority)
                                              else " yet (gs.py feature add ...)"))
        return 0
    lines = ["%-6s %-3s %-12s %-5s %-4s %-12s %s" % ("ID", "P", "STATUS", "GATES", "PASS", "AREA", "TITLE")]
    for f in feats:
        deps = f.get("depends_on") or []
        lines.append("%-6s %-3s %-12s %-5s %-4s %-12s %s%s" % (
            f.get("id", "?"), f.get("priority", "?"), f.get("status", "todo"), G.gate_code(f),
            "yes" if f.get("passes") is True else "no", f.get("area", "?"), f.get("title", ""),
            ("  <- " + ",".join(map(str, deps))) if deps else ""))
    c = data["counts"]
    lines.append("GATES order: static unit playthrough visual perf  (P pass, X fail, n n/a, . not run)")
    lines.append("%d total | %d done | %d in progress | %d blocked | %d todo"
                 % (c["total"], c["done"], c["in_progress"], c["blocked"], c["todo"]))
    _emit(args, data, "\n".join(lines))
    return 0


def cmd_feature_add(args: argparse.Namespace) -> int:
    root = _find_root(args)
    doc = _load_features(root)
    fid = _fid(args.id) if args.id else G.next_feature_id(doc)
    if G.find_feature(doc, fid) is not None:
        raise CliError("feature %s already exists (ids are permanent; pick another id)" % fid)
    deps = _split_ids(args.depends)
    unknown = [d for d in deps if G.find_feature(doc, d) is None and d != fid]
    if unknown:
        raise CliError("unknown dependenc%s %s; add %s first" % ("y" if len(unknown) == 1 else "ies",
                                                               ", ".join(unknown), "it" if len(unknown) == 1 else "them"))
    try:
        f = G.new_feature(fid, args.title, args.area, priority=args.priority, acceptance=args.accept,
                          depends_on=deps, description=args.desc or "", owner=args.owner or "",
                          notes=args.notes or "")
    except ValueError as exc:
        raise CliError(str(exc))
    if getattr(args, "path", None):
        f["paths"] = [p.replace("\\", "/") for p in args.path]
    doc["features"].append(f)
    _save_features(root, doc)
    text = "Added %s [%s] %s: %s" % (f["id"], f["priority"], f["area"], f["title"])
    if deps:
        text += "  (depends on %s)" % ", ".join(deps)
    if not f["acceptance"]:
        text += "\nwarning: no acceptance criteria; add testable ones (--accept) so the playthrough gate has targets"
    _emit(args, f, text)
    return 0


def cmd_feature_next(args: argparse.Namespace) -> int:
    root = _find_root(args)
    doc = _load_features(root)
    nf = G.next_feature(doc)
    if args.json:
        print(json.dumps(nf, indent=2, ensure_ascii=False))
        if nf is None:
            _note(_why_no_next(doc))
        return 0
    if nf is None:
        print(_why_no_next(doc))
        return 0
    lines = ["%s [%s] %s - %s" % (nf["id"], nf.get("priority", "?"), nf.get("area", "?"), nf.get("title", ""))]
    if nf.get("description"):
        lines.append("  %s" % nf["description"])
    acc = nf.get("acceptance") or []
    lines.append("  acceptance:" if acc else "  acceptance: (none - define testable criteria first)")
    lines += ["   - %s" % a for a in acc]
    lines.append("  depends on: %s" % (", ".join(nf.get("depends_on") or []) or "nothing"))
    others = [f["id"] for f in G.ready_features(doc)[1:4]]
    if others:
        lines.append("  then: %s" % ", ".join(others))
    lines.append("  start: gs.py feature start %s" % nf["id"])
    print("\n".join(lines))
    return 0


def _why_no_next(doc: Dict[str, Any]) -> str:
    c = G.feature_counts(doc)
    if c["total"] == 0:
        return "No features yet - plan them with gs.py feature add."
    parts = ["No todo feature is ready."]
    waiting = G.waiting_features(doc)
    if waiting:
        parts.append("Waiting on dependencies: " + "; ".join(
            "%s needs %s" % (f.get("id"), ", ".join(u)) for f, u in waiting[:6]) + ".")
    prog = [f.get("id") for f in G.get_features(doc) if f.get("status") == "in_progress"]
    if prog:
        parts.append("In progress: %s." % ", ".join(map(str, prog)))
    blocked = [f.get("id") for f in G.get_features(doc) if f.get("status") == "blocked"]
    if blocked:
        parts.append("Blocked: %s." % ", ".join(map(str, blocked)))
    if c["done"] == c["total"]:
        parts = ["All %d features are done." % c["total"]]
    return " ".join(parts)


def cmd_feature_show(args: argparse.Namespace) -> int:
    root = _find_root(args)
    doc = _load_features(root)
    f = _get_feature(doc, args.id)
    ok, problems = G.check_feature_pass(f, root)
    data = {"feature": f, "five_gate_check": {"ok": ok, "problems": problems}}
    lines = ["%s [%s] %s - %s   status %s | passes %s" % (
        f.get("id"), f.get("priority"), f.get("area"), f.get("title"), f.get("status"),
        "yes" if f.get("passes") is True else "no")]
    if f.get("description"):
        lines.append("  %s" % f["description"])
    for a in f.get("acceptance") or []:
        lines.append("  accept: %s" % a)
    if f.get("depends_on"):
        lines.append("  depends on: %s" % ", ".join(f["depends_on"]))
    gates = f.get("gates") or {}
    ev = f.get("evidence") or {}
    notes = f.get("gate_notes") or {}
    for g in G.GATES:
        evs = ev.get(g)
        evs = ", ".join(evs) if isinstance(evs, list) else (evs or "")
        lines.append("  %-11s %-5s %s%s" % (g, gates.get(g) or "-", evs, ("  # " + notes[g]) if notes.get(g) else ""))
    if f.get("notes"):
        lines.append("  notes: %s" % str(f["notes"]).replace("\n", "\n         "))
    lines.append("  five-gate check: %s" % ("PASS" if ok else "not yet"))
    lines += ["    - %s" % p for p in problems]
    _emit(args, data, "\n".join(lines))
    return 0


def cmd_feature_start(args: argparse.Namespace) -> int:
    root = _find_root(args)
    doc = _load_features(root)
    f = _get_feature(doc, args.id)
    fid = f["id"]
    msgs = []
    if f.get("passes") is True or f.get("status") == "done":
        if not args.reopen:
            raise CliError("%s is done; use 'feature start %s --reopen' to rework it (resets passes and all "
                           "gates)" % (fid, fid))
        f["passes"] = False
        f["gates"] = {g: None for g in G.GATES}
        f["evidence"] = {g: None for g in G.GATES}
        f["gate_notes"] = {}
        msgs.append("reopened: passes=false, all gates reset")
        G.append_progress(root, "Reopened %s - %s." % (fid, f.get("title", "")))
    elif f.get("status") == "in_progress":
        _emit(args, f, "%s is already in progress (open gates: %s)." % (fid, ", ".join(G.open_gates(f)) or "none"))
        return 0
    unmet = G._deps_status(f, G._by_id(doc))
    if unmet:
        msgs.append("warning: dependencies do not pass yet: %s" % ", ".join(unmet))
    was_blocked = f.get("status") == "blocked"
    f["status"] = "in_progress"
    if was_blocked:
        f["notes"] = ((f.get("notes") or "") + "\n" if f.get("notes") else "") + "[unblocked %s]" % G.now_stamp()
    _save_features(root, doc)
    if not args.reopen:
        G.append_progress(root, "Started %s - %s." % (fid, f.get("title", "")))
    text = "%s in progress: %s" % (fid, f.get("title", ""))
    if msgs:
        text += "\n" + "\n".join(msgs)
    text += "\nevidence dir: gs.py evidence-dir %s" % fid
    _emit(args, f, text)
    return 0


def _ingest_evidence(root: Path, fid: str, raw_paths: List[str]) -> Tuple[List[str], List[str]]:
    """Normalise evidence paths; copy files from outside the project into the evidence dir.

    Returns (stored project-relative paths, notices).  Missing paths are an input error.
    """
    normed = G.normalize_evidence(raw_paths, root)
    missing = [n for n in normed if not n["exists"]]
    if missing:
        raise CliError("evidence not found: %s (produce it first, e.g. into $(gs.py evidence-dir %s))"
                       % (", ".join(n["stored"] for n in missing), fid))
    stored: List[str] = []
    notices: List[str] = []
    dest_dir = G.gs_dir(root) / "evidence" / fid
    for n in normed:
        if not Path(n["stored"]).is_absolute():
            stored.append(n["stored"])
            if not n["stored"].startswith(G.GS_DIRNAME + "/"):
                notices.append("evidence %s lives outside .gamestudio/; build or clean steps may delete it "
                               "(the Stop hook then flags %s) - prefer $(gs.py evidence-dir %s)"
                               % (n["stored"], fid, fid))
            continue
        src = Path(n["abs"])
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / src.name
        i = 1
        while dest.exists():
            dest = dest_dir / ("%s-%d%s" % (src.stem, i, src.suffix))
            i += 1
        if src.is_dir():
            shutil.copytree(str(src), str(dest))
        else:
            shutil.copy2(str(src), str(dest))
        rel = _rel(dest, root)
        stored.append(rel)
        notices.append("copied external evidence %s -> %s (evidence must live inside the project)" % (src, rel))
    return stored, notices


def cmd_feature_gate(args: argparse.Namespace) -> int:
    root = _find_root(args)
    doc = _load_features(root)
    f = _get_feature(doc, args.id)
    fid = f["id"]
    stored: List[str] = []
    notices: List[str] = []
    if args.evidence:
        if args.result == "reset":
            raise CliError("--evidence makes no sense with reset")
        stored, notices = _ingest_evidence(root, fid, args.evidence)
    was_passing = f.get("passes") is True
    try:
        warnings = G.set_gate(f, args.gate, args.result, evidence=stored or None, note=args.note, root=root)
    except ValueError as exc:
        raise CliError(str(exc))
    if f["gates"].get(args.gate) == "pass":
        for p in G._as_path_list(f["evidence"].get(args.gate)):
            if isinstance(p, str):
                why = G.evidence_contradiction(G.resolve_evidence(p, root))
                if why:
                    warnings.append("%s: evidence %s %s; 'feature pass' will refuse it" % (fid, p, why))
    _save_features(root, doc)
    if was_passing and f.get("passes") is not True:
        G.append_progress(root, "Regression: %s %s gate is now %s; feature demoted to in_progress."
                          % (fid, args.gate, f["gates"].get(args.gate) or "unset"))
    opened = G.open_gates(f)
    ev = f["evidence"].get(args.gate)
    data = {"id": fid, "gate": args.gate, "result": f["gates"].get(args.gate), "evidence": ev,
            "note": (f.get("gate_notes") or {}).get(args.gate), "open_gates": opened,
            "passes": f.get("passes"), "status": f.get("status"), "warnings": notices + warnings}
    lines = ["%s %s = %s" % (fid, args.gate, f["gates"].get(args.gate) or "unset (reset)")]
    if ev:
        lines.append("  evidence: %s" % (", ".join(ev) if isinstance(ev, list) else ev))
    if data["note"]:
        lines.append("  note: %s" % data["note"])
    lines += ["  %s" % m for m in notices]
    lines += ["  warning: %s" % w for w in warnings]
    if opened:
        lines.append("  open gates: %s" % ", ".join("%s(%s)" % (g, f["gates"].get(g) or "-") for g in opened))
    elif f.get("passes") is not True:
        lines.append("  all five gates are pass/n/a - close it with: gs.py feature pass %s" % fid)
    _emit(args, data, "\n".join(lines))
    return 0


def cmd_feature_pass(args: argparse.Namespace) -> int:
    root = _find_root(args)
    doc = _load_features(root)
    f = _get_feature(doc, args.id)
    fid = f["id"]
    was_passing = f.get("passes") is True
    ok, problems = G.mark_pass(f, root)
    if not ok:
        demoted = False
        if was_passing or f.get("status") == "done":
            f["passes"] = False
            f["status"] = "in_progress"
            _save_features(root, doc)
            G.append_progress(root, "%s failed re-verification of the five-gate rule; demoted to in_progress."
                              % fid)
            demoted = True
        data = {"id": fid, "passes": False, "status": f.get("status"), "problems": problems, "demoted": demoted}
        text = "REFUSED: %s does not satisfy the five-gate rule:\n%s" % (fid, "\n".join("  - " + p for p in problems))
        if demoted:
            text += "\n%s was marked done/passing and has been demoted to in_progress." % fid
        text += ("\nFix: run the missing checks, then gs.py feature gate %s <gate> pass --evidence PATH "
                 "(or n/a --note WHY)." % fid)
        _emit(args, data, text)
        return 1
    _save_features(root, doc)
    unmet = G._deps_status(f, G._by_id(doc))
    if not was_passing:
        G.append_progress(root, "%s passed all five gates: %s." % (fid, f.get("title", "")))
    nf = G.next_feature(doc)
    data = {"id": fid, "passes": True, "status": "done", "problems": [],
            "dependency_warnings": unmet, "next": nf.get("id") if nf else None}
    text = "%s passes: all five gates satisfied, status done." % fid if not was_passing else \
        "%s already passing; re-verified OK." % fid
    if unmet:
        text += "\nwarning: dependencies that do not pass yet: %s" % ", ".join(unmet)
    if nf:
        text += "\nnext: %s [%s] %s" % (nf["id"], nf.get("priority"), nf.get("title"))
    _emit(args, data, text)
    return 0


def cmd_feature_block(args: argparse.Namespace) -> int:
    root = _find_root(args)
    doc = _load_features(root)
    f = _get_feature(doc, args.id)
    fid = f["id"]
    reason = (args.reason or "").strip()
    if not reason:
        raise CliError("--reason must not be empty")
    if f.get("passes") is True or f.get("status") == "done":
        raise CliError("%s is done; reopen it with 'feature start %s --reopen' before blocking it" % (fid, fid))
    f["status"] = "blocked"
    line = "[blocked %s] %s" % (G.now_stamp(), reason)
    f["notes"] = (str(f.get("notes")) + "\n" + line) if f.get("notes") else line
    _save_features(root, doc)
    G.append_progress(root, "Blocked %s - %s: %s" % (fid, f.get("title", ""), reason))
    _emit(args, f, "%s blocked: %s" % (fid, reason))
    return 0


# --------------------------------------------------------------------------
# evidence-dir / progress / kb
# --------------------------------------------------------------------------

def cmd_evidence_dir(args: argparse.Namespace) -> int:
    root = _find_root(args)
    fid = _fid(args.id)
    d = G.gs_dir(root) / "evidence" / fid
    d.mkdir(parents=True, exist_ok=True)
    try:
        known = G.find_feature(G.load_json(G.state_path(root, "features"), None), fid) is not None
    except Exception:
        known = False
    if not known:
        _note("warning: %s is not in features.json yet" % fid)
    _emit(args, {"id": fid, "path": str(d), "relative": _rel(d, root)}, str(d))
    return 0


def cmd_progress(args: argparse.Namespace) -> int:
    root = _find_root(args)
    text = " ".join(args.text).strip()
    if not text or text == "-":
        text = sys.stdin.read().strip() if not sys.stdin.isatty() else ""
    if not text:
        raise CliError("progress text is empty")
    entry = G.append_progress(root, text)
    _emit(args, {"entry": entry, "file": str(G.state_path(root, "progress"))}, entry)
    return 0


def cmd_kb(args: argparse.Namespace) -> int:
    skills_root = Path(args.skills_dir) if args.skills_dir else G.PLUGIN_ROOT / "skills"
    res = G.kb_search(args.query, skills_root=skills_root, skill=args.skill, limit=args.limit,
                      per_file=args.per_file)
    if args.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
        return 0
    if not res["results"]:
        msg = "No matches for %r (%d files searched)." % (args.query, res["files_searched"])
        if res.get("note"):
            msg += " " + res["note"]
        print(msg)
        return 0
    lines = []
    for i, r in enumerate(res["results"], 1):
        lines.append("%d. %s:%d  [%s]  score %.2f" % (i, r["file"], r["line"], r["skill"] or "-", r["score"]))
        lines.append("   %s" % r["heading"])
        lines += ["   > %s" % ln for ln in r["excerpt"].splitlines()]
    lines.append("(%d files searched in %.0f ms; terms: %s)" % (res["files_searched"], res["elapsed_ms"],
                                                               ", ".join(res["terms"])))
    print("\n".join(lines))
    return 0


# --------------------------------------------------------------------------
# argument parser
# --------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--root", metavar="DIR",
                        help="project root (default: nearest ancestor of cwd containing .gamestudio/)")
    common.add_argument("--json", action="store_true", help="machine-readable JSON output")

    p = argparse.ArgumentParser(
        prog="gs.py", description="arcosian project-state CLI: contract, features and the five gates, "
        "progress, budget, evidence, codex search, project map, change impact, what-if predictions, dashboard.",
        epilog="Five-gate rule: a feature is done only when static, unit, playthrough, visual and perf are each "
        "'pass' (with evidence on disk) or 'n/a' (with a note). Exit codes: 0 ok, 1 check failed, 2 usage error.")
    p.add_argument("--selftest", action="store_true", help="run the built-in end-to-end self-test")
    p.add_argument("--version", action="version", version="gs.py %s" % __version__)
    sub = p.add_subparsers(dest="cmd", metavar="COMMAND")

    sp = sub.add_parser("init", parents=[common], help="create .gamestudio/ with skeleton documents")
    sp.add_argument("--title", required=True, help="game title")
    sp.add_argument("--engine", choices=G.ENGINES, help="engine (default: auto-detect, else other)")
    sp.add_argument("--genre", help="genre, e.g. puzzle, idle, roguelite")
    sp.add_argument("--engine-version", help="e.g. 4.7 or 6000.3.2f1 (default: detected or current line)")
    sp.add_argument("--platforms", help="required comma list, any of: " + ",".join(G.PLATFORMS))
    sp.add_argument("--input", help="comma list of %s (default: what the platforms expect)"
                    % ",".join(G.INPUTS))
    sp.add_argument("--orientation", choices=G.ORIENTATIONS,
                    help="default: portrait for phone-only games, landscape otherwise")
    sp.add_argument("--tier", choices=G.TIERS, default="prototype")
    sp.add_argument("--monetization", choices=G.MONETIZATION_MODELS, default="hybrid")
    sp.add_argument("--slug", help="kebab-case slug (default: from title)")
    sp.add_argument("--budget", type=float, default=G.DEFAULT_ASSET_USD_CAP, help="asset spend cap USD (default 50)")
    sp.add_argument("--per-call-cap", type=float, default=G.DEFAULT_PER_CALL_USD_CAP,
                    help="max USD per generation call (default 5)")
    sp.add_argument("--force", action="store_true", help="overwrite skeleton documents (backs them up first)")
    sp.set_defaults(func=cmd_init)

    sp = sub.add_parser("status", parents=[common], help="compact project summary")
    sp.set_defaults(func=cmd_status)

    sp = sub.add_parser("summary", parents=[common], help="the SessionStart summary text")
    sp.add_argument("--max-chars", type=int, default=2500)
    sp.set_defaults(func=cmd_summary)

    sp = sub.add_parser("validate", parents=[common], help="schema-validate project JSON + feature rules")
    sp.add_argument("--all", action="store_true", help="every JSON file under .gamestudio/ (default)")
    sp.add_argument("--schema", help="force a schema (name like level-spec, or a path)")
    sp.add_argument("--cross", action="store_true",
                    help="also check the documents against each other (unique ids, references, evidence and "
                         "manifest paths); needs a project")
    sp.add_argument("paths", nargs="*", metavar="PATH")
    sp.set_defaults(func=cmd_validate)

    fp = sub.add_parser("feature", help="feature list and five-gate workflow")
    fsub = fp.add_subparsers(dest="fcmd", metavar="ACTION")
    p.set_defaults(_feature_parser=fp)

    s = fsub.add_parser("list", parents=[common], help="list features")
    s.add_argument("--status", choices=G.STATUSES)
    s.add_argument("--area", choices=G.AREAS)
    s.add_argument("--priority", choices=G.PRIORITIES)
    s.set_defaults(func=cmd_feature_list)

    s = fsub.add_parser("add", parents=[common], help="add a feature")
    s.add_argument("--id", help="F001 style id (default: next free id)")
    s.add_argument("--title", required=True)
    s.add_argument("--area", required=True, choices=G.AREAS)
    s.add_argument("--priority", choices=G.PRIORITIES, default="P1")
    s.add_argument("--accept", action="append", default=[], metavar="TEXT", help="acceptance criterion (repeatable)")
    s.add_argument("--depends", action="append", default=[], metavar="IDS", help="comma list of feature ids")
    s.add_argument("--desc", help="description")
    s.add_argument("--owner", help="owning agent or person")
    s.add_argument("--path", action="append", default=[], metavar="GLOB",
                   help="code or content this feature owns, e.g. core/combat/* (repeatable; used by gs.py impact)")
    s.add_argument("--notes", help="free notes")
    s.set_defaults(func=cmd_feature_add)

    s = fsub.add_parser("next", parents=[common], help="highest-priority ready todo feature")
    s.set_defaults(func=cmd_feature_next)

    s = fsub.add_parser("show", parents=[common], help="one feature with its five-gate check")
    s.add_argument("id")
    s.set_defaults(func=cmd_feature_show)

    s = fsub.add_parser("start", parents=[common], help="mark a feature in progress")
    s.add_argument("id")
    s.add_argument("--reopen", action="store_true", help="rework a done feature (resets passes and gates)")
    s.set_defaults(func=cmd_feature_start)

    s = fsub.add_parser("gate", parents=[common], help="record a gate result with evidence")
    s.add_argument("id")
    s.add_argument("gate", choices=G.GATES)
    s.add_argument("result", choices=("pass", "fail", "n/a", "reset"))
    s.add_argument("--evidence", action="append", default=[], metavar="PATH",
                   help="evidence file or dir (repeatable; replaces the gate's previous evidence)")
    s.add_argument("--note", help="gate note (required for n/a)")
    s.set_defaults(func=cmd_feature_gate)

    s = fsub.add_parser("pass", parents=[common], help="mark done if the five-gate rule holds")
    s.add_argument("id")
    s.set_defaults(func=cmd_feature_pass)

    s = fsub.add_parser("block", parents=[common], help="mark a feature blocked")
    s.add_argument("id")
    s.add_argument("--reason", required=True)
    s.set_defaults(func=cmd_feature_block)

    sp = sub.add_parser("evidence-dir", parents=[common], help="create and print .gamestudio/evidence/<ID>/")
    sp.add_argument("id")
    sp.set_defaults(func=cmd_evidence_dir)

    sp = sub.add_parser("progress", parents=[common], help="append a dated entry to progress.md")
    sp.add_argument("text", nargs="*", help="entry text ('-' or nothing reads stdin)")
    sp.set_defaults(func=cmd_progress)

    sp = sub.add_parser("budget", parents=[common], help="asset/audio spend vs cap")
    sp.set_defaults(func=cmd_budget)

    sp = sub.add_parser("map", parents=[common], help="index scenes, scripts, classes, assets and tuning (.gamestudio/map/)")
    sp.set_defaults(func=cmd_map)

    sp = sub.add_parser("impact", parents=[common], help="what a change to a file, class, tuning key or feature touches")
    sp.add_argument("targets", nargs="+", metavar="TARGET")
    sp.add_argument("--depth", type=int, default=4, help="how many dependency hops to follow (default 4)")
    sp.set_defaults(func=cmd_impact)

    sp = sub.add_parser("whatif", parents=[common], help="predict a change with bots or simulators against the contract")
    sp.add_argument("--set", action="append", required=True, metavar="KEY=VALUE",
                    help="tuning key or model path = JSON value, *factor or +=delta (repeatable)")
    sp.add_argument("--sim", choices=("auto", "godot", "economy", "match3"), default="auto")
    sp.add_argument("--runs", type=int, default=100, help="runs per seed (default 100)")
    sp.add_argument("--seeds", type=int, default=5, help="independent seeds (default 5)")
    sp.add_argument("--seed", type=int, default=1)
    sp.add_argument("--bot", default="greedy")
    sp.add_argument("--model", help="economy-model JSON (economy simulator)")
    sp.add_argument("--level", help="match-3 level spec (match3 simulator)")
    sp.add_argument("--label")
    sp.add_argument("--tolerance", type=float, default=0.05, help="win-rate band half-width (default 0.05)")
    sp.add_argument("--no-save", action="store_true", help="do not write .gamestudio/whatif/")
    sp.set_defaults(func=cmd_whatif)

    sp = sub.add_parser("dashboard", parents=[common], help="write the offline project dashboard (HTML)")
    sp.add_argument("--out", help="output path (default .gamestudio/reports/dashboard.html)")
    sp.add_argument("--no-map", action="store_true", help="skip the dependency graph")
    sp.set_defaults(func=cmd_dashboard)

    sp = sub.add_parser("kb", parents=[common], help="ranked search across the plugin's skills")
    sp.add_argument("query")
    sp.add_argument("--skill", help="restrict to one skill directory")
    sp.add_argument("--limit", type=int, default=8)
    sp.add_argument("--per-file", type=int, default=2, help=argparse.SUPPRESS)
    sp.add_argument("--skills-dir", help=argparse.SUPPRESS)
    sp.set_defaults(func=cmd_kb)
    return p


_MUTATING = (cmd_feature_add, cmd_feature_start, cmd_feature_gate, cmd_feature_pass, cmd_feature_block)


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")  # type: ignore[attr-defined]
        except (AttributeError, ValueError):
            pass
    if "--selftest" in argv:
        return _selftest()
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "cmd", None):
        parser.print_help()
        return 2
    if getattr(args, "func", None) is None:      # e.g. "gs.py feature" without an action
        fp = getattr(args, "_feature_parser", None)
        (fp or parser).print_help()
        return 2
    try:
        if args.func in _MUTATING:
            with G.state_lock(_find_root(args)):
                return int(args.func(args) or 0)
        return int(args.func(args) or 0)
    except TimeoutError as exc:
        _note(str(exc))
        return 2
    except CliError as exc:
        if getattr(args, "json", False):
            print(json.dumps({"error": str(exc), "code": exc.code}))
        _note(str(exc))
        return exc.code
    except BrokenPipeError:  # e.g. piped into head
        return 0
    except KeyboardInterrupt:
        return 130


# --------------------------------------------------------------------------
# self-test (end to end through main())
# --------------------------------------------------------------------------

def _selftest() -> int:
    failures: List[str] = []
    passed = [0]

    def check(cond: Any, msg: str) -> None:
        if cond:
            passed[0] += 1
        else:
            failures.append(msg)
            print("FAIL: %s" % msg)

    def run(*argv: str) -> Tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = main(list(argv))
            except SystemExit as exc:  # argparse usage errors
                code = exc.code if isinstance(exc.code, int) else 2
        return code, out.getvalue(), err.getvalue()

    def jrun(*argv: str) -> Tuple[int, Any]:
        code, out, err = run(*argv, "--json")
        try:
            return code, json.loads(out) if out.strip() else None
        except ValueError:
            print("non-JSON output for %s:\n%s\n%s" % (argv, out, err))
            return code, None

    tmp = Path(tempfile.mkdtemp(prefix="gs-selftest-"))
    try:
        root = tmp / "game"
        R = str(root)
        # ---- init ----
        code, out, _ = run("init", "--platforms", "ios,android", "--title", "Selftest Merge", "--engine", "godot", "--genre", "puzzle", "--root", R)
        check(code == 0 and "Next steps" in out, "init exit 0 + next steps (%d)" % code)
        g = root.resolve() / G.GS_DIRNAME
        for rel in ("config.json", "contract.json", "features.json", "budget.json", "assets/manifest.json",
                    "progress.md", "evidence", "snapshots", "playtests", "reports", "levels", "economy",
                    "concepts", "research", "analytics", "design", "art", "audio"):
            check((g / rel).exists(), "init created %s" % rel)
        # a project initialised before design/art/audio existed gets them on re-init, nothing else touched
        for d in ("design", "art", "audio"):
            shutil.rmtree(str(g / d))
        before = (g / "config.json").read_text(encoding="utf-8")
        code, out, _ = run("init", "--platforms", "ios,android", "--title", "Again", "--engine", "godot", "--root", R)
        check(code == 0 and "added missing directories" in out and all((g / d).is_dir() for d in ("design", "art", "audio"))
              and (g / "config.json").read_text(encoding="utf-8") == before, "re-init adds missing directories only")
        cfg = json.loads((g / "config.json").read_text(encoding="utf-8"))
        check(cfg["budgets"]["asset_usd_cap"] == 50 and cfg["budgets"]["per_call_usd_cap"] == 5
              and cfg["platforms"] == ["ios", "android"] and cfg["orientation"] == "portrait"
              and cfg["input"] == ["touch"]
              and cfg["storefronts"] == ["US"] and cfg["tier"] == "prototype"
              and cfg["licence_allowlist"] == ["commercial-paid", "cc0", "cc-by", "mit", "apache-2.0"],
              "config defaults")
        code, out, _ = run("init", "--platforms", "ios,android", "--title", "Again", "--engine", "godot", "--root", R)
        check(code == 1 and "already" in out, "re-init without --force refuses (exit 1)")
        check(json.loads((g / "config.json").read_text(encoding="utf-8"))["project"]["title"] == "Selftest Merge",
              "re-init did not overwrite config")
        code, data = jrun("init", "--platforms", "ios,android", "--title", "Selftest Merge", "--engine", "godot", "--root", R, "--force")
        check(code == 0 and "config.json" in data["overwritten"] and data["backup_dir"], "init --force with backup")
        code, _, err = run("init", "--title", "Bad", "--engine", "godot", "--root", str(tmp / "bad"),
                           "--platforms", "ios,gameboy")
        check(code == 2 and "platforms" in err, "init rejects unknown platform (exit 2)")
        code, _, err = run("init", "--title", "Bad", "--engine", "godot", "--root", str(tmp / "bad2"))
        check(code == 2 and "choose the target platforms" in err, "init without --platforms asks for them (exit 2)")
        code, out, _ = run("init", "--title", "Desk", "--engine", "godot", "--root", str(tmp / "desk"),
                           "--platforms", "windows,linux,switch")
        dcfg = json.loads((tmp / "desk" / G.GS_DIRNAME / "config.json").read_text(encoding="utf-8"))
        check(code == 0 and dcfg["input"] == ["mouse_keyboard", "gamepad"] and dcfg["orientation"] == "landscape"
              and "input: mouse_keyboard, gamepad" in out, "desktop/console init: input and orientation defaults")

        # ---- understanding layer ----
        code, out, _ = run("map", "--root", R)
        check(code == 0 and (Path(R) / G.GS_DIRNAME / "map" / "MAP.md").is_file(), "map writes MAP.md")
        code, out, _ = run("impact", "no/such/file.gd", "--root", R)
        check(code == 1 and "not found" in out, "impact reports an unknown target (exit 1)")
        code, out, _ = run("dashboard", "--root", R)
        check(code == 0 and (Path(R) / G.GS_DIRNAME / "reports" / "dashboard.html").is_file(), "dashboard written")
        code, _, err = run("whatif", "--set", "x=1", "--root", R)
        check(code == 2 and "simulator" in err, "whatif without a simulator explains the options (exit 2)")
        check("No project map yet" not in G.summarize(Path(R), 2500), "summary points at the map once it exists")

        # ---- feature add ----
        check(run("feature", "add", "--id", "F001", "--title", "Merge rule", "--area", "gameplay", "--path", "core/*",
                  "--accept", "two equal tiles merge into their sum", "--root", R)[0] == 0, "add F001")
        check(run("feature", "add", "--id", "F002", "--title", "Merge VFX", "--area", "vfx", "--priority", "P0",
                  "--depends", "F001", "--accept", "burst on merge", "--root", R)[0] == 0, "add F002 (P0, dep F001)")
        check(run("feature", "add", "--id", "F003", "--title", "Board input", "--area", "gameplay",
                  "--priority", "P0", "--accept", "swipe moves tiles", "--root", R)[0] == 0, "add F003 (P0)")
        code, f4 = jrun("feature", "add", "--title", "Settings", "--area", "ui", "--priority", "P2", "--root", R)
        check(code == 0 and f4 and f4["id"] == "F004", "add without --id auto-numbers F004")
        check(run("feature", "add", "--id", "F001", "--title", "dup", "--area", "ui", "--root", R)[0] == 2,
              "duplicate id rejected")
        check(run("feature", "add", "--id", "X1", "--title", "bad", "--area", "ui", "--root", R)[0] == 2,
              "bad id rejected")
        check(run("feature", "add", "--id", "F009", "--title", "bad dep", "--area", "ui", "--depends", "F077",
                  "--root", R)[0] == 2, "unknown dependency rejected")
        check(run("feature", "add", "--id", "F010", "--title", "bad area", "--area", "nope", "--root", R)[0] == 2,
              "bad area rejected by argparse")

        # ---- next ordering ----
        code, nf = jrun("feature", "next", "--root", R)
        check(code == 0 and nf and nf["id"] == "F003", "next = F003 (ready P0; F002 waits on F001): %s" % (nf or {}).get("id"))
        code, out, _ = run("feature", "next", "--root", R)
        check("F003" in out and "then: F001, F004" in out, "next text shows queue")

        # ---- gates ----
        check(run("feature", "start", "F003", "--root", R)[0] == 0, "start F003")
        code, out, _ = run("evidence-dir", "F003", "--root", R)
        evd = Path(out.strip())
        check(code == 0 and evd.is_dir() and evd == g / "evidence" / "F003", "evidence-dir creates + prints path")
        (evd / "static.log").write_text("0 errors\n", encoding="utf-8")
        code, d = jrun("feature", "gate", "F003", "static", "pass", "--evidence", str(evd / "static.log"), "--root", R)
        check(code == 0 and d["evidence"] == ".gamestudio/evidence/F003/static.log",
              "absolute evidence stored project-relative: %s" % (d or {}).get("evidence"))
        code, d = jrun("feature", "gate", "F003", "unit", "pass", "--root", R)
        check(code == 0 and any("without evidence" in w for w in d["warnings"]), "gate pass w/o evidence warns")
        check(run("feature", "gate", "F003", "playthrough", "pass", "--evidence",
                  ".gamestudio/evidence/F003/nope.json", "--root", R)[0] == 2, "missing evidence file rejected")
        check(run("feature", "gate", "F003", "visual", "n/a", "--root", R)[0] == 2, "n/a without note rejected")
        check(run("feature", "gate", "F003", "visual", "n/a", "--note", "input only; F002 owns visuals",
                  "--root", R)[0] == 0, "n/a with note accepted")
        check(run("feature", "gate", "F003", "perf", "fail", "--note", "p95 21 ms low tier", "--root", R)[0] == 0,
              "gate fail recorded")
        code, d = jrun("feature", "pass", "F003", "--root", R)
        probs = "\n".join(d["problems"]) if d else ""
        check(code == 1 and d["passes"] is False and "'unit' is pass but has no evidence" in probs
              and "'perf' is fail" in probs and "'playthrough' has not been run" in probs,
              "pass refused with problems: %s" % probs)
        code, out, _ = run("feature", "pass", "F003", "--root", R)
        check(code == 1 and out.startswith("REFUSED"), "pass refusal text")
        outside = tmp / "outside"
        outside.mkdir()
        (outside / "unit.xml").write_text('<testsuites tests="4" failures="0" errors="0"></testsuites>',
                                          encoding="utf-8")
        code, d = jrun("feature", "gate", "F003", "unit", "pass", "--evidence", str(outside / "unit.xml"), "--root", R)
        check(code == 0 and d["evidence"] == ".gamestudio/evidence/F003/unit.xml"
              and (evd / "unit.xml").is_file() and any("copied external evidence" in w for w in d["warnings"]),
              "external evidence copied into evidence dir")
        (evd / "playthrough.json").write_text(json.dumps({"schema_version": "1.0", "mode": "deterministic_script",
                                                           "verdict": "fail"}),
                                              encoding="utf-8")
        code, d = jrun("feature", "gate", "F003", "playthrough", "pass", "--evidence",
                       ".gamestudio/evidence/F003/playthrough.json", "--root", R)
        check(code == 0 and any("verdict" in w for w in d["warnings"]), "contradicting evidence warned at gate time")
        (evd / "perf.json").write_text(json.dumps({"schema_version": "1.0", "verdict": "pass"}), encoding="utf-8")
        run("feature", "gate", "F003", "perf", "pass", "--evidence", ".gamestudio/evidence/F003/perf.json", "--root", R)
        code, d = jrun("feature", "pass", "F003", "--root", R)
        check(code == 1 and len(d["problems"]) == 1 and "verdict" in d["problems"][0],
              "pass refused on failing playthrough report")
        (evd / "playthrough.json").write_text(json.dumps({"schema_version": "1.0", "mode": "deterministic_script",
                                                           "verdict": "pass"}),
                                              encoding="utf-8")
        code, d = jrun("feature", "pass", "F003", "--root", R)
        check(code == 0 and d["passes"] is True and d["status"] == "done", "pass accepted with full evidence")
        fdoc = json.loads((g / "features.json").read_text(encoding="utf-8"))
        f3 = [f for f in fdoc["features"] if f["id"] == "F003"][0]
        check(f3["passes"] is True and f3["status"] == "done" and all(
            not str(v).startswith("/") for v in f3["evidence"].values() if v), "stored state is project-relative")

        # regression demotes, re-pass restores
        code, d = jrun("feature", "gate", "F003", "perf", "fail", "--root", R)
        check(d["passes"] is False and d["status"] == "in_progress", "regression demotes F003")
        run("feature", "gate", "F003", "perf", "pass", "--root", R)
        check(run("feature", "pass", "F003", "--root", R)[0] == 0, "re-pass after regression")
        check(run("feature", "start", "F003", "--root", R)[0] == 2, "start on done feature needs --reopen")

        # all n/a with notes -> F001 passes, then F002 (P0) is next over F004 (P2)
        for gate in G.GATES:
            run("feature", "gate", "F001", gate, "n/a", "--note", "rules spec; exercised by F003 tests", "--root", R)
        check(run("feature", "pass", "F001", "--root", R)[0] == 0, "all-n/a feature passes")
        code, nf = jrun("feature", "next", "--root", R)
        check(nf and nf["id"] == "F002", "next after deps pass = F002: %s" % (nf or {}).get("id"))

        # block / list / show
        check(run("feature", "block", "F004", "--reason", "waiting on UX spec", "--root", R)[0] == 0, "block F004")
        code, d = jrun("feature", "list", "--status", "blocked", "--root", R)
        check(code == 0 and [f["id"] for f in d["features"]] == ["F004"], "list --status blocked")
        code, out, _ = run("feature", "list", "--root", R)
        check("PPPnP" in out and "nnnnn" in out, "list shows gate codes")
        code, d = jrun("feature", "show", "F003", "--root", R)
        check(code == 0 and d["five_gate_check"]["ok"] is True, "show F003 passes check")
        check(run("feature", "show", "F404", "--root", R)[0] == 2, "unknown feature exit 2")
        check(run("feature", "block", "F003", "--reason", "x", "--root", R)[0] == 2, "cannot block a done feature")

        # ---- progress / status / budget ----
        code, d = jrun("progress", "Selftest", "entry", "--root", R)
        check(code == 0 and d["entry"].endswith("Selftest entry"), "progress appends")
        code, st = jrun("status", "--root", R)
        check(code == 0 and st["counts"]["done"] == 2 and st["counts"]["blocked"] == 1
              and st["next"]["id"] == "F002" and st["title"] == "Selftest Merge"
              and st["budget"]["cap_usd"] == 50 and len(st["progress"]) <= 5
              and st["progress"][-1].endswith("Selftest entry"), "status JSON")
        code, out, _ = run("status", "--root", R)
        check(code == 0 and "Selftest Merge" in out and "Next         F002" in out, "status text")
        code, b = jrun("budget", "--root", R)
        check(code == 0 and b["spent_usd"] == 0 and b["remaining_usd"] == 50, "budget JSON")

        # ---- validate ----
        avail, _ = G.validator_available()
        state_files = [".gamestudio/%s" % x for x in ("config.json", "contract.json", "features.json",
                                                      "budget.json", "assets/manifest.json")]
        code, v = jrun("validate", "--root", R, *[str(root / x) for x in state_files])
        if avail:
            bad = [f for f in v["files"] if f["status"] != "ok"] if v else ["no output"]
            check(code == 0 and not bad and not v["features_lint"]["errors"],
                  "state files validate against schemas: %s" % bad)
        else:
            check(code in (0, 2), "validate without validator exits 0/2")
        code, v = jrun("validate", "--all", "--root", R)
        fails = [(f["path"], f["errors"][:2]) for f in v["files"] if f["status"] == "fail"] if v else ["no output"]
        if avail:
            check(code == 0 and not fails, "validate --all clean (state + evidence reports): %s" % fails)
        else:
            check(code in (0, 2) and v is not None, "validate --all runs without validator")
        good_features = (g / "features.json").read_text(encoding="utf-8")
        (g / "features.json").write_text("{oops", encoding="utf-8")
        code, out, err = run("feature", "list", "--root", R)
        check(code == 2 and "not valid JSON" in err, "corrupt features.json refused, not overwritten")
        check((g / "features.json").read_text(encoding="utf-8") == "{oops", "corrupt file left untouched")
        code, v = jrun("validate", "--root", R, str(g / "features.json"))
        check(code == 1, "validate flags corrupt JSON")
        (g / "features.json").write_text(good_features, encoding="utf-8")

        # ---- validate --cross (separate project: the main one keeps its state for the checks below) ----
        xr = tmp / "xgame"
        XR = str(xr)
        run("init", "--platforms", "ios,android", "--title", "Cross", "--engine", "godot", "--root", XR)
        xg = xr.resolve() / G.GS_DIRNAME
        code, out, _ = run("validate", "--cross", "--root", XR)
        check(code == 0 and "cross-document checks: ok" in out, "validate --cross on a fresh project: ok (%d)" % code)
        code, d = jrun("validate", "--cross", "--root", XR)
        check(code == 0 and d["cross"] == {"errors": [], "warnings": []} and d["summary"]["cross_errors"] == 0,
              "validate --cross --json carries an empty cross section")
        code, d = jrun("validate", "--root", XR)
        check("cross" not in d, "validate without --cross has no cross section")
        # warnings alone do not fail the run
        model = json.loads((G.SCHEMAS_DIR / "examples" / "example.economy-model.json").read_text(encoding="utf-8"))
        model["offers"] = [{"id": "mystery_pack", "price_usd": 2}]       # no such contract monetization.iap id
        G.save_json(xg / "economy" / "model.economy.json", model)
        code, out, _ = run("validate", "--cross", "--root", XR)
        check(code == 0 and "warning: " in out and "mystery_pack" in out and "1 warning(s)" in out,
              "cross warnings keep exit 0: %d %s" % (code, out[-300:]))
        # errors fail it
        check(run("feature", "add", "--id", "F001", "--title", "Core", "--area", "gameplay", "--root", XR)[0] == 0, "xadd F001")
        check(run("feature", "add", "--id", "F002", "--title", "Juice", "--area", "vfx", "--root", XR)[0] == 0, "xadd F002")
        fx = json.loads((xg / "features.json").read_text(encoding="utf-8"))
        fx["features"][1]["depends_on"] = ["F077"]
        G.save_json(xg / "features.json", fx)
        con = json.loads((xg / "contract.json").read_text(encoding="utf-8"))
        con["mechanics"] = [{"id": "merge_two"}, {"id": "merge_two"}]
        G.save_json(xg / "contract.json", con)
        stray = tmp / "static_tmp.log"
        stray.write_text("0 errors\n", encoding="utf-8")
        check(run("feature", "gate", "F001", "static", "pass", "--evidence", str(stray), "--root", XR)[0] == 0, "xgate F001")
        (xg / "evidence" / "F001" / "static_tmp.log").unlink()          # evidence vanishes after the gate was recorded
        code, d = jrun("validate", "--cross", "--root", XR)
        cross_e = "\n".join(d["cross"]["errors"]) if d else ""
        check(code == 1 and "duplicate mechanic id 'merge_two'" in cross_e
              and "features.json F001: gate 'static' evidence not found on disk" in cross_e,
              "validate --cross fails on duplicate ids and missing evidence of a passing gate: %s" % cross_e)
        check(any("F077" in e for e in d["features_lint"]["errors"]) and "F077" not in cross_e,
              "a problem the feature rules already report is not repeated in the cross section")
        check(d["summary"]["cross_errors"] == len(d["cross"]["errors"]) >= 2, "cross_errors counted in the summary")
        code, out, _ = run("validate", "--cross", "--root", XR)
        check(code == 1 and "cross-document checks:" in out and "error: contract.json mechanics[1]" in out,
              "validate --cross text output lists the errors")
        check(run("validate", "--cross", str(stray), "--root", str(tmp / "nowhere"))[0] == 2, "--cross without a project: exit 2")

        # ---- kb ----
        skills = tmp / "plugin" / "skills"
        G._write_fake_skills(skills, filler=200)
        code, k = jrun("kb", "currency sinks", "--skills-dir", str(skills), "--limit", "3")
        check(code == 0 and k["results"] and
              k["results"][0]["file"] == "skills/economy-design/references/currency-architecture.md",
              "kb top hit via CLI")
        check(k["elapsed_ms"] < 3000, "kb fast (%s ms)" % k.get("elapsed_ms"))
        code, out, _ = run("kb", "screen shake", "--skill", "game-feel", "--skills-dir", str(skills))
        check(code == 0 and "skills/game-feel/SKILL.md" in out and "> " in out, "kb text output")

        # ---- summary ----
        for n in (2500, 500, 120):
            code, d = jrun("summary", "--root", R, "--max-chars", str(n))
            check(code == 0 and d["chars"] <= n, "summary <= %d chars" % n)
        code, d = jrun("summary", "--root", R)
        check("Five-gate rule" in d["summary"] and "F002" in d["summary"], "summary content")

        # ---- usage errors / discovery ----
        check(run("status", "--root", str(tmp / "nowhere"))[0] == 2, "no project -> exit 2")
        check(run("feature")[0] == 2, "feature without action prints help, exit 2")
        sub_dir = root / "src" / "deep"
        sub_dir.mkdir(parents=True)
        old = os.getcwd()
        try:
            os.chdir(str(sub_dir))
            code, st2 = jrun("status")
            check(code == 0 and st2["root"] == str(root.resolve()), "root discovered from nested cwd")
        finally:
            os.chdir(old)

        # ---- real subprocess (shebang/entry point) ----
        proc = subprocess.run([sys.executable, str(_HERE / "gs.py"), "feature", "next", "--json", "--root", R],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, timeout=60)
        check(proc.returncode == 0 and json.loads(proc.stdout)["id"] == "F002", "subprocess entry point")
    except Exception as exc:
        import traceback
        traceback.print_exc()
        failures.append("unexpected exception: %r" % exc)
    finally:
        shutil.rmtree(str(tmp), ignore_errors=True)
    if failures:
        print("gs selftest: %d passed, %d FAILED" % (passed[0], len(failures)))
        return 1
    print("gs selftest: OK (%d checks)" % passed[0])
    return 0


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows pipes default to the ANSI code page; Claude Code reads UTF-8
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
