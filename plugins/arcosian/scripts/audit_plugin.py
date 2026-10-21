#!/usr/bin/env python3
"""Free structural audit of the arcosian plugin (no model calls).

Checks skill and agent frontmatter, reference/script bookkeeping in each SKILL.md, cross-references
(arcosian:<name>, /arcosian:<name>, ${CLAUDE_PLUGIN_ROOT}/<path>) and JSON validity, and can
write a Markdown knowledge map.

Usage: audit_plugin.py [--root PLUGIN_DIR] [--json] [--map OUT.md] [--selftest]
Exit codes: 0 ok (warnings allowed), 1 errors found, 2 usage error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SKILL_KEYS = {"name", "description", "when_to_use", "argument-hint", "allowed-tools", "disable-model-invocation",
              "user-invocable", "model", "effort", "context", "agent", "paths", "license", "metadata"}
AGENT_KEYS = {"name", "description", "tools", "model", "effort", "color", "skills"}
DESC_WARN, DESC_ERR, WHEN_MAX, AGENT_DESC_MAX, AGENT_SKILLS_MAX = 450, 1536, 200, 400, 4
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".godot", "templates"}
TEXT_SUFFIXES = {".md", ".js", ".mjs", ".json"}

PLACEHOLDER_CHARS = "<>*${}"
REL_REF_RE = re.compile(r"(?<![\w/.<>${}-])((?:references|scripts)/[^\s`'\"()\[\]|,;:]+)")
SLASH_RE = re.compile(r"(?<![\w])/arcosian:([a-z][a-z0-9-]*)")
PLAIN_RE = re.compile(r"(?<![\w/:-])arcosian:([a-z][a-z0-9-]*)")
ROOT_REF_RE = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([^\s`'\"\\()\[\]|,;]+)")
META_NAME_RE = re.compile(r"\bmeta\b[^{]*\{[^}]*?\bname\s*:\s*['\"]([^'\"]+)['\"]", re.S)


class Report:
    def __init__(self) -> None:
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.stats: Dict[str, int] = {}

    def err(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


# --------------------------------------------------------------------------
# Parsing helpers
# --------------------------------------------------------------------------

def _clean(val: str) -> str:
    val = val.strip()
    if len(val) >= 2 and val[0] == val[-1] and val[0] in "'\"":
        return val[1:-1]
    return val


def parse_frontmatter(text: str) -> Tuple[Optional[Dict[str, Any]], str]:
    """Minimal YAML-subset parser for `---` frontmatter. Returns (data, error)."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, "missing frontmatter (file must start with ---)"
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return None, "frontmatter is not closed with ---"
    data: Dict[str, Any] = {}
    key: Optional[str] = None
    for ln in lines[1:end]:
        if not ln.strip() or ln.lstrip().startswith("#"):
            continue
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", ln)
        if m and not ln[0].isspace():
            key, val = m.group(1), m.group(2).strip()
            if val in (">", "|", ">-", "|-", ">+", "|+"):
                val = ""
            if val.startswith("[") and val.endswith("]"):
                data[key] = [_clean(v) for v in val[1:-1].split(",") if v.strip()]
            else:
                data[key] = _clean(val)
            continue
        if key is None:
            return None, "unparseable frontmatter line: %r" % ln
        s = ln.strip()
        if s.startswith("- "):
            if not isinstance(data[key], list):
                if data[key]:
                    return None, "key %r mixes a scalar and a list" % key
                data[key] = []
            data[key].append(_clean(re.sub(r"\s+#.*$", "", s[2:])))
        elif isinstance(data[key], str):
            data[key] = (data[key] + " " + s).strip()
    return data, ""


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def walk_files(root: Path, suffixes: set) -> List[Path]:
    out = []
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.suffix in suffixes and not (set(p.relative_to(root).parts[:-1]) & SKIP_DIRS):
            out.append(p)
    return out


def clean_ref(raw: str) -> str:
    return raw.rstrip(".,:;)]}>'\"`*")


# --------------------------------------------------------------------------
# Checks
# --------------------------------------------------------------------------

def audit_skills(root: Path, rep: Report) -> Dict[str, Dict[str, Any]]:
    skills: Dict[str, Dict[str, Any]] = {}
    sdir = root / "skills"
    total_desc = refs = ref_lines = 0
    for d in sorted(p for p in sdir.iterdir() if p.is_dir()) if sdir.is_dir() else []:
        rel = "skills/%s" % d.name
        md = d / "SKILL.md"
        if not md.is_file():
            rep.err("%s: missing SKILL.md" % rel)
            continue
        text = read(md)
        fm, why = parse_frontmatter(text)
        if fm is None:
            rep.err("%s/SKILL.md: %s" % (rel, why))
            continue
        for k in sorted(set(fm) - SKILL_KEYS):
            rep.err("%s/SKILL.md: frontmatter key %r is not allowed" % (rel, k))
        if fm.get("name") != d.name:
            rep.err("%s/SKILL.md: name %r does not equal directory %r" % (rel, fm.get("name"), d.name))
        desc = fm.get("description")
        if not isinstance(desc, str) or not desc.strip():
            rep.err("%s/SKILL.md: description is missing or empty" % rel)
            desc = ""
        elif len(desc) > DESC_ERR:
            rep.err("%s/SKILL.md: description is %d chars (limit %d)" % (rel, len(desc), DESC_ERR))
        elif len(desc) > DESC_WARN:
            rep.warn("%s/SKILL.md: description is %d chars (target <= %d)" % (rel, len(desc), DESC_WARN))
        if isinstance(fm.get("when_to_use"), str) and len(fm["when_to_use"]) > WHEN_MAX:
            rep.err("%s/SKILL.md: when_to_use is %d chars (limit %d)" % (rel, len(fm["when_to_use"]), WHEN_MAX))
        total_desc += len(desc)
        files = [f for sub in ("references", "scripts") for f in sorted((d / sub).rglob("*"))
                 if f.is_file() and "__pycache__" not in f.parts] if d.is_dir() else []
        info = {"description": desc, "refs": [], "lines": len(text.splitlines())}
        mentioned = {clean_ref(m) for m in REL_REF_RE.findall(text)}
        for f in files:
            rp = f.relative_to(d).as_posix()
            if f.parent.name == "references" or rp.startswith("references/"):
                refs += 1
                n = len(read(f).splitlines())
                ref_lines += n
                info["refs"].append((rp, n, read(f)))
            if rp not in text:
                rep.err("%s/SKILL.md: %s exists but is not listed in SKILL.md" % (rel, rp))
        for m in sorted(mentioned):
            if any(c in m for c in PLACEHOLDER_CHARS):
                continue
            if not (d / m).exists():
                rep.err("%s/SKILL.md: references %s which does not exist" % (rel, m))
        skills[d.name] = info
    rep.stats.update(skills=len(skills), references=refs, reference_lines=ref_lines,
                     skill_description_chars=total_desc)
    return skills


def audit_agents(root: Path, skills: Dict[str, Any], rep: Report) -> List[str]:
    names = []
    adir = root / "agents"
    agent_chars = 0
    for f in sorted(adir.glob("*.md")) if adir.is_dir() else []:
        rel = "agents/%s" % f.name
        fm, why = parse_frontmatter(read(f))
        if fm is None:
            rep.err("%s: %s" % (rel, why))
            continue
        names.append(f.stem)
        for k in sorted(set(fm) - AGENT_KEYS):
            rep.err("%s: frontmatter key %r is not allowed" % (rel, k))
        if fm.get("name") != f.stem:
            rep.err("%s: name %r does not equal file name %r" % (rel, fm.get("name"), f.stem))
        desc = fm.get("description")
        if not isinstance(desc, str) or not desc.strip():
            rep.err("%s: description is missing or empty" % rel)
        elif len(desc) > AGENT_DESC_MAX:
            rep.err("%s: description is %d chars (limit %d)" % (rel, len(desc), AGENT_DESC_MAX))
        agent_chars += len(desc) if isinstance(desc, str) else 0
        pre = fm.get("skills") or []
        if not isinstance(pre, list):
            rep.err("%s: skills must be a list" % rel)
            pre = []
        if len(pre) > AGENT_SKILLS_MAX:
            rep.err("%s: preloads %d skills (max %d)" % (rel, len(pre), AGENT_SKILLS_MAX))
        for s in pre:
            if s not in skills:
                rep.err("%s: preloaded skill %r does not exist" % (rel, s))
    rep.stats["agents"] = len(names)
    rep.stats["agent_description_chars"] = agent_chars
    return names


def workflow_names(root: Path, rep: Report) -> List[str]:
    names = []
    for f in sorted((root / "workflows").glob("*.js")) if (root / "workflows").is_dir() else []:
        m = META_NAME_RE.search(read(f))
        if m:
            names.append(m.group(1))
        else:
            rep.warn("workflows/%s: no meta.name found" % f.name)
    rep.stats["workflows"] = len(list((root / "workflows").glob("*.js"))) if (root / "workflows").is_dir() else 0
    return names


def core_names(core: Path) -> Tuple[set, set, set]:
    """Skill, agent and workflow names of the core plugin, so an adapter's arcosian:<x> links resolve."""
    sk = {d.name for d in (core / "skills").iterdir() if (d / "SKILL.md").is_file()} if (core / "skills").is_dir() else set()
    ag = {f.stem for f in (core / "agents").glob("*.md")} if (core / "agents").is_dir() else set()
    wf = set()
    for f in (core / "workflows").glob("*.js") if (core / "workflows").is_dir() else []:
        m = META_NAME_RE.search(read(f))
        if m:
            wf.add(m.group(1))
    return sk, ag, wf


def audit_refs(root: Path, skills: Dict, agents: List[str], workflows: List[str], rep: Report,
               core: Optional[Path] = None) -> None:
    targets = set(skills) | set(agents)
    slash_targets = set(skills) | set(workflows)
    if core is not None:
        sk, ag, wf = core_names(core)
        targets |= sk | ag
        slash_targets |= sk | wf
    for f in walk_files(root, {".md", ".js", ".mjs", ".json"}):
        text = read(f)
        rel = f.relative_to(root).as_posix()
        for name in sorted(set(PLAIN_RE.findall(text))):
            if name not in targets:
                rep.err("%s: arcosian:%s is not an agent or skill" % (rel, name))
        for name in sorted(set(SLASH_RE.findall(text))):
            if name not in slash_targets:
                rep.err("%s: /arcosian:%s is not a skill or workflow" % (rel, name))
        for raw in sorted(set(ROOT_REF_RE.findall(text))):
            path = clean_ref(raw)
            if not path or any(c in path for c in PLACEHOLDER_CHARS):
                continue
            if not (root / path).exists():
                rep.err("%s: ${CLAUDE_PLUGIN_ROOT}/%s does not exist" % (rel, path))


def audit_json(root: Path, rep: Report) -> None:
    for f in walk_files(root, {".json"}):
        try:
            json.loads(f.read_text(encoding="utf-8"))
        except (ValueError, OSError) as exc:
            rep.err("%s: invalid JSON: %s" % (f.relative_to(root).as_posix(), exc))


def audit(root: Path, core: Optional[Path] = None, max_chars: Optional[int] = None) -> Tuple[Report, Dict[str, Dict[str, Any]]]:
    rep = Report()
    skills = audit_skills(root, rep)
    agents = audit_agents(root, skills, rep)
    workflows = workflow_names(root, rep)
    audit_refs(root, skills, agents, workflows, rep, core)
    audit_json(root, rep)
    scripts = [p for p in (root / "scripts").glob("*.py")] if (root / "scripts").is_dir() else []
    rep.stats["scripts"] = len(scripts)
    rep.stats["skill_md_lines"] = sum(s["lines"] for s in skills.values())
    rep.stats["lines"] = rep.stats["skill_md_lines"] + rep.stats["reference_lines"]
    # Skill and agent descriptions sit in every session's context, so they are the always-on cost.
    always = rep.stats.get("skill_description_chars", 0) + rep.stats.get("agent_description_chars", 0)
    rep.stats["always_on_chars"] = always
    rep.stats["always_on_tokens_est"] = int(round(always / 4.0))
    if max_chars is not None and always > max_chars:
        rep.err("always-on budget: skill and agent descriptions total %d chars (limit %d); shorten descriptions "
                "and keep detail in references" % (always, max_chars))
    return rep, skills


# --------------------------------------------------------------------------
# Knowledge map
# --------------------------------------------------------------------------

def first_line(text: str) -> str:
    body = text
    if text.startswith("---"):
        parts = text.split("---", 2)
        body = parts[2] if len(parts) == 3 else text
    for ln in body.splitlines():
        ln = ln.strip()
        if ln.startswith("#"):
            return ln.lstrip("#").strip()
    for ln in body.splitlines():
        if ln.strip():
            return re.split(r"(?<=[.!?])\s", ln.strip())[0][:160]
    return ""


def write_map(path: Path, skills: Dict[str, Dict[str, Any]], rep: Report) -> None:
    s = rep.stats
    out = ["# Knowledge map", "",
           "%d skills, %d reference files, %d lines (SKILL.md + references), %d agents, %d workflows, %d scripts."
           % (s["skills"], s["references"], s["lines"], s["agents"], s["workflows"], s["scripts"]),
           "Total skill description characters: %d." % s["skill_description_chars"], ""]
    for name, info in sorted(skills.items()):
        out += ["## %s" % name, "", info["description"] or "(no description)", ""]
        if info["refs"]:
            out += ["| Reference | Lines | Starts with |", "|---|---|---|"]
            for rp, n, text in info["refs"]:
                out.append("| `%s` | %d | %s |" % (rp, n, first_line(text).replace("|", "/")))
            out.append("")
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------
# Selftest
# --------------------------------------------------------------------------

def _w(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def selftest() -> int:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        _w(root / "skills/alpha/SKILL.md",
           "---\nname: alpha\ndescription: Alpha knowledge. Use when testing.\n---\n# Alpha\n"
           "See `references/a.md`, `scripts/tool.py` and `${CLAUDE_PLUGIN_ROOT}/scripts/gs.py`.\n"
           "Delegate to arcosian:boss, run /arcosian:alpha or /arcosian:flow.\n")
        _w(root / "skills/alpha/references/a.md", "# Alpha ref\nBody.\n")
        _w(root / "skills/alpha/scripts/tool.py", "print(1)\n")
        _w(root / "scripts/gs.py", "pass\n")
        _w(root / "agents/boss.md", "---\nname: boss\ndescription: Boss.\nmodel: opus\nskills:\n  - alpha  # preload\n---\nBody\n")
        _w(root / "workflows/flow.js", "export const meta = {\n  name: 'flow',\n  description: 'x',\n}\n")
        _w(root / "data.json", "{\"ok\": true}\n")
        _w(root / "hooks/hooks.json", '{"c": "python3 \\"${CLAUDE_PLUGIN_ROOT}/scripts/gs.py\\""}\n')
        rep, skills = audit(root)
        assert not rep.errors, rep.errors
        assert rep.stats["skills"] == 1 and rep.stats["references"] == 1 and rep.stats["agents"] == 1, rep.stats
        mp = root / "map.md"
        write_map(mp, skills, rep)
        assert "Alpha ref" in mp.read_text(encoding="utf-8")
        # Break things one at a time and expect the matching error.
        _w(root / "skills/alpha/references/extra.md", "# Extra\n")
        _w(root / "skills/beta/SKILL.md", "---\nname: wrong\ndescription: d\nbogus: 1\n---\n")
        _w(root / "skills/gamma/SKILL.md", "---\nname: gamma\ndescription: %s\n---\nsee references/missing.md\n" % ("x" * 1600))
        _w(root / "agents/bad.md", "---\nname: bad\ndescription: d\nhooks: x\nskills:\n  - nope\n---\n")
        _w(root / "notes.md", "arcosian:ghost /arcosian:phantom ${CLAUDE_PLUGIN_ROOT}/nope/file.md. ${CLAUDE_PLUGIN_ROOT}/<x>\n")
        _w(root / "broken.json", "{oops")
        rep, _ = audit(root)
        joined = "\n".join(rep.errors)
        for needle in ("extra.md exists but is not listed", "name 'wrong' does not equal", "key 'bogus' is not allowed",
                       "description is 1600 chars", "references/missing.md which does not exist",
                       "key 'hooks' is not allowed", "preloaded skill 'nope'", "arcosian:ghost",
                       "/arcosian:phantom", "nope/file.md does not exist", "broken.json: invalid JSON"):
            assert needle in joined, "expected error not reported: %s\n%s" % (needle, joined)
        assert "<x>" not in joined
        _w(root / "skills/delta/SKILL.md", "---\nname: delta\ndescription: %s\n---\n" % ("y" * 500))
        rep, _ = audit(root)
        assert any("skills/delta" in w and "500 chars" in w for w in rep.warnings), rep.warnings
        rep, _ = audit(root, max_chars=100)
        assert any("always-on budget" in e for e in rep.errors), rep.errors
        adapter = root / "adapter"
        _w(adapter / "skills/bridge/SKILL.md", "---\nname: bridge\ndescription: Bridge. Use when bridging.\n---\n"
           "Hand off to arcosian:boss and /arcosian:alpha.\n")
        rep, _ = audit(adapter)
        assert any("arcosian:boss" in e for e in rep.errors), rep.errors
        rep, _ = audit(adapter, core=root)
        assert not rep.errors, rep.errors
    print("audit_plugin selftest ok")
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Structural audit of the arcosian plugin.")
    ap.add_argument("--root", default=str(Path(__file__).resolve().parent.parent), help="plugin directory")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--map", metavar="OUT.md", help="write a Markdown knowledge map")
    ap.add_argument("--selftest", action="store_true", help="run built-in tests")
    ap.add_argument("--core", metavar="DIR", help="core plugin, so an adapter's arcosian:<x> links resolve")
    ap.add_argument("--max-description-chars", type=int, metavar="N",
                    help="fail when skill and agent descriptions (always in context) exceed N characters")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    root = Path(args.root).resolve()
    if not root.is_dir():
        sys.stderr.write("audit_plugin: --root %s is not a directory\n" % root)
        return 2
    rep, skills = audit(root, Path(args.core).resolve() if args.core else None, args.max_description_chars)
    if args.map:
        try:
            write_map(Path(args.map), skills, rep)
        except OSError as exc:
            sys.stderr.write("audit_plugin: cannot write map: %s\n" % exc)
            return 2
    if args.json:
        print(json.dumps({"ok": not rep.errors, "errors": rep.errors, "warnings": rep.warnings,
                          "stats": rep.stats}, indent=2))
    else:
        for e in rep.errors:
            print("ERROR   " + e)
        for w in rep.warnings:
            print("WARNING " + w)
        print("stats: " + ", ".join("%s=%s" % kv for kv in sorted(rep.stats.items())))
        print("result: %s (%d errors, %d warnings)" % ("FAIL" if rep.errors else "ok", len(rep.errors), len(rep.warnings)))
    return 1 if rep.errors else 0


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows pipes default to the ANSI code page; Claude Code reads UTF-8
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
