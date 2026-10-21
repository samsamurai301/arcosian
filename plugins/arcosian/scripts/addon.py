#!/usr/bin/env python3
"""Arcosian add-ons: scaffold a new one, and check one before it is published.

  addon.py new --name arcosian-rpgmaker --kind genre|engine|tool --skill rpgmaker-bridge --description "..."
               [--author NAME] [--out DIR] [--with-script]
  addon.py check DIR [--core DIR] [--run-selftests] [--json]
  addon.py --selftest

`new` copies templates/addon/ into DIR (default ./<name>) and fills in the names; it never overwrites files.
`check` applies the house rules: manifest fields, the skill format (via audit_plugin.py), README disclosure
sections, licence, pinned MCP launchers, secrets only through placeholders, scripts with --selftest and UTF-8 output,
and the plugin directory's file rules. Exit codes: 0 ok, 1 problems found, 2 usage error.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

HERE = Path(__file__).resolve().parent
CORE = HERE.parent
TEMPLATE = CORE / "templates" / "addon"
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,62}$")
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")
DEVICE_NAMES = {"con", "prn", "aux", "nul"} | {"com%d" % i for i in range(1, 10)} | {"lpt%d" % i for i in range(1, 10)}
SECRET_RE = re.compile(r"(ghp_|github_pat_|sk-|xox[bp]-|AKIA|AIza)[A-Za-z0-9_-]{12,}")
LAUNCHERS = ("npx", "uvx", "bunx")
README_SECTIONS = ("What this plugin runs, sends and fetches", "Security")
TEXT_EXT = {".md", ".json", ".py", ".mjs", ".js", ".txt", ".yml", ".yaml", ".toml", ".cfg", ".gd", ".cs", ""}

sys.path.insert(0, str(HERE))


def _fill(text: str, values: Dict[str, str]) -> str:
    for k, v in values.items():
        text = text.replace("{{%s}}" % k, v)
    return text


def new(name: str, kind: str, skill: str, description: str, author: str, out: Path, with_script: bool) -> List[Path]:
    if not NAME_RE.match(name):
        raise ValueError("name must be lower-case letters, digits and hyphens, e.g. arcosian-rpgmaker")
    if not NAME_RE.match(skill):
        raise ValueError("skill must be lower-case letters, digits and hyphens, e.g. rpgmaker-bridge")
    if kind not in ("genre", "engine", "tool"):
        raise ValueError("kind must be genre, engine or tool")
    description = " ".join(description.split())
    if not description or len(description) > 300:
        raise ValueError("description is required, at most 300 characters (say what it gives and when to use it)")
    if out.exists() and any(out.iterdir()):
        raise ValueError("%s already exists and is not empty; nothing was written" % out)
    script = skill.replace("-", "_")
    values = {"name": name, "kind": kind, "skill": skill, "description": description, "author": author,
              "title": skill.replace("-", " ").capitalize(), "year": str(datetime.now().year),
              "month": datetime.now().strftime("%b %Y"), "script": script}
    plan = [("plugin.json.tmpl", ".claude-plugin/plugin.json"), ("README.md.tmpl", "README.md"), ("LICENSE.tmpl", "LICENSE"),
            ("codex-SKILL.md.tmpl" if kind == "genre" else "process-SKILL.md.tmpl", "skills/%s/SKILL.md" % skill),
            ("overview.md.tmpl", "skills/%s/references/overview.md" % skill)]
    if with_script:
        plan.append(("script.py.tmpl", "scripts/%s.py" % script))
    written = []
    for src, dst in plan:
        target = out / dst
        target.parent.mkdir(parents=True, exist_ok=True)
        raw = (TEMPLATE / src).read_text(encoding="utf-8")
        if dst.endswith("plugin.json"):  # JSON-escape the values so quotes in a description stay valid JSON
            text = json.dumps(json.loads(_fill(raw, {k: json.dumps(v)[1:-1] for k, v in values.items()})), indent=2) + "\n"
        else:
            text = _fill(raw, values)
        target.write_text(text, encoding="utf-8")
        written.append(target)
    icon = CORE / "icon.png"
    if icon.is_file():
        shutil.copy(str(icon), str(out / "icon.png"))
    return written


def check(root: Path, core: Optional[Path] = None, run_selftests: bool = False) -> Dict[str, List[str]]:
    errors: List[str] = []
    warnings: List[str] = []
    mf = root / ".claude-plugin" / "plugin.json"
    manifest: Dict[str, Any] = {}
    if not mf.is_file():
        errors.append(".claude-plugin/plugin.json is missing")
    else:
        try:
            manifest = json.loads(mf.read_text(encoding="utf-8"))
        except ValueError as exc:
            errors.append("plugin.json is not valid JSON: %s" % exc)
    if manifest:
        if not NAME_RE.match(str(manifest.get("name", ""))):
            errors.append("plugin.json name must be lower-case letters, digits and hyphens")
        if manifest.get("name") != root.name:
            warnings.append("folder name %r differs from the plugin name %r" % (root.name, manifest.get("name")))
        if not SEMVER_RE.match(str(manifest.get("version", ""))):
            errors.append("plugin.json version must be semantic (1.2.3); raise it on every release")
        if not manifest.get("description"):
            errors.append("plugin.json needs a description")
        if not (manifest.get("author") or {}).get("name"):
            errors.append("plugin.json needs author.name")
        if not manifest.get("license"):
            warnings.append("plugin.json has no license field")
        if "arcosian" not in (manifest.get("dependencies") or []):
            warnings.append("plugin.json does not depend on arcosian; say how users install the core instead")
    readme = root / "README.md"
    if not readme.is_file():
        errors.append("README.md is missing")
    else:
        text = readme.read_text(encoding="utf-8", errors="replace")
        for sec in README_SECTIONS:
            if sec.lower() not in text.lower():
                errors.append("README.md needs a %r section" % sec)
        if len(text.split()) < 40:
            errors.append("README.md has fewer than 40 words")
    if not any((root / n).is_file() for n in ("LICENSE", "LICENSE.md", "LICENSE.txt")):
        errors.append("LICENSE is missing")
    files = [p for p in root.rglob("*") if p.is_file() and ".git" not in p.parts]
    if len(files) > 512:
        warnings.append("%d files: more than 512 sends the plugin to manual review" % len(files))
    for p in files:
        rel = p.relative_to(root).as_posix()
        stem = p.name.split(".")[0].lower()
        if p.name == ".gitattributes":
            errors.append("%s: no .gitattributes inside a plugin (the directory validator rejects content filters)" % rel)
        if stem in DEVICE_NAMES or re.search(r"[:\\]", p.name) or p.name.endswith((".", " ")):
            errors.append("%s: file name is not portable" % rel)
        if p.stat().st_size > 256 * 1024:
            warnings.append("%s: larger than 256 KiB (manual review)" % rel)
        if p.suffix.lower() in TEXT_EXT and p.stat().st_size < 2_000_000:
            t = p.read_text(encoding="utf-8", errors="replace")
            if "{{" in t and "}}" in t and re.search(r"\{\{[a-z]+\}\}", t):
                errors.append("%s: unfilled template placeholder" % rel)
            if SECRET_RE.search(t):
                errors.append("%s: looks like it contains a secret" % rel)
    mcp = root / ".mcp.json"
    if mcp.is_file():
        try:
            servers = json.loads(mcp.read_text(encoding="utf-8")).get("mcpServers", {})
        except ValueError as exc:
            servers = {}
            errors.append(".mcp.json is not valid JSON: %s" % exc)
        options = (manifest.get("userConfig") or {}) if manifest else {}
        for name, cfg in servers.items():
            src = cfg.get("url") or " ".join([cfg.get("command", "")] + [str(a) for a in cfg.get("args", [])])
            if cfg.get("command") in LAUNCHERS and not re.search(r"@\d+\.\d+\.\d+|==\d+\.\d+\.\d+", src):
                errors.append(".mcp.json %s: %s launcher must pin an exact version" % (name, cfg.get("command")))
            if cfg.get("url") and not str(cfg["url"]).startswith("https://"):
                errors.append(".mcp.json %s: remote servers must use https" % name)
            for k, v in list((cfg.get("env") or {}).items()) + list((cfg.get("headers") or {}).items()):
                for ref in re.findall(r"\$\{user_config\.([\w-]+)\}", str(v)):
                    if ref not in options:
                        errors.append(".mcp.json %s: ${user_config.%s} is not declared in plugin.json userConfig" % (name, ref))
                    elif re.search(r"(?i)key|token|secret|password", ref) and not options[ref].get("sensitive"):
                        errors.append("plugin.json userConfig %s holds a secret: mark it sensitive" % ref)
                if re.search(r"(?i)key|token|secret|authorization|password", k) and "${" not in str(v):
                    errors.append(".mcp.json %s: %s must come from a ${...} placeholder" % (name, k))
    for py in sorted((root / "scripts").glob("*.py")) if (root / "scripts").is_dir() else []:
        t = py.read_text(encoding="utf-8", errors="replace")
        rel = py.relative_to(root).as_posix()
        if "--selftest" not in t:
            errors.append("%s: needs a --selftest" % rel)
        if 'reconfigure(encoding="utf-8"' not in t:
            warnings.append("%s: reconfigure stdout/stderr to UTF-8 for Windows (see the template)" % rel)
        if run_selftests:
            r = subprocess.run([sys.executable, str(py), "--selftest"], capture_output=True, text=True, timeout=600)
            if r.returncode != 0:
                errors.append("%s --selftest failed: %s" % (rel, (r.stdout + r.stderr).strip()[-300:]))
    try:
        import audit_plugin
        rep, _ = audit_plugin.audit(root, core or CORE)
        errors += ["skills: " + e for e in rep.errors]
        warnings += ["skills: " + w for w in rep.warnings]
    except Exception as exc:  # noqa: BLE001 - report instead of crashing
        errors.append("skill audit failed to run: %s" % exc)
    return {"errors": errors, "warnings": warnings}


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--selftest", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    n = sub.add_parser("new", help="scaffold an add-on")
    n.add_argument("--name", required=True)
    n.add_argument("--kind", required=True, choices=("genre", "engine", "tool"))
    n.add_argument("--skill", required=True)
    n.add_argument("--description", required=True)
    n.add_argument("--author", default="your-name")
    n.add_argument("--out")
    n.add_argument("--with-script", action="store_true", help="add a stdlib Python helper with --selftest")
    c = sub.add_parser("check", help="check an add-on against the house rules")
    c.add_argument("dir")
    c.add_argument("--core", help="core plugin directory (default: this plugin)")
    c.add_argument("--run-selftests", action="store_true")
    c.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.cmd == "new":
        out = Path(a.out or a.name).resolve()
        try:
            written = new(a.name, a.kind, a.skill, a.description, a.author, out, a.with_script)
        except ValueError as exc:
            print("addon: %s" % exc, file=sys.stderr)
            return 2
        print("Created %s (%d files). Next: write the skill, then run addon.py check %s" % (out, len(written), out))
        return 0
    if a.cmd == "check":
        root = Path(a.dir).resolve()
        if not root.is_dir():
            print("addon: %s is not a directory" % root, file=sys.stderr)
            return 2
        res = check(root, Path(a.core).resolve() if a.core else None, a.run_selftests)
        if a.json:
            print(json.dumps(res, indent=1))
        else:
            for e in res["errors"]:
                print("ERROR   " + e)
            for w in res["warnings"]:
                print("WARNING " + w)
            print("result: %s (%d errors, %d warnings)" % ("FAIL" if res["errors"] else "ok", len(res["errors"]), len(res["warnings"])))
        return 1 if res["errors"] else 0
    ap.print_help()
    return 2


def selftest() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="addon-"))
    try:
        out = tmp / "arcosian-demo"
        new("arcosian-demo", "tool", "demo-bridge", 'Bridges the "Demo" editor to Arcosian.', "tester", out, True)
        res = check(out, run_selftests=True)
        assert not res["errors"], res["errors"]
        assert json.loads((out / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["description"].startswith("Bridges")
        try:
            new("arcosian-demo", "tool", "demo-bridge", "x", "t", out, False)
            raise AssertionError("must refuse to overwrite")
        except ValueError:
            pass
        g = tmp / "arcosian-genre"
        new("arcosian-genre", "genre", "rhythm-roguelites", "Rhythm roguelite playbooks.", "t", g, False)
        assert "## Core models" in (g / "skills/rhythm-roguelites/SKILL.md").read_text(encoding="utf-8")
        assert not check(g)["errors"], check(g)["errors"]
        (out / ".mcp.json").write_text(json.dumps({"mcpServers": {
            "a": {"command": "npx", "args": ["-y", "pkg"]},
            "b": {"type": "http", "url": "http://x/mcp", "headers": {"Authorization": "Bearer ${user_config.tok}"}},
            "c": {"command": "x", "env": {"API_KEY": "plain"}}}}), encoding="utf-8")
        (out / "skills/demo-bridge/notes.txt").write_text("{{name}} sk-abcdefghijklmnopqrstuv", encoding="utf-8")
        (out / ".gitattributes").write_text("* text=auto\n", encoding="utf-8")
        errs = "\n".join(check(out)["errors"])
        for needle in ("a: npx launcher must pin", "b: remote servers must use https", "user_config.tok} is not declared",
                       "c: API_KEY must come from", "unfilled template placeholder", "contains a secret", ".gitattributes"):
            assert needle in errs, (needle, errs)
        try:
            new("Bad Name", "tool", "x-y", "d", "t", tmp / "bad", False)
            raise AssertionError("bad name accepted")
        except ValueError:
            pass
    finally:
        shutil.rmtree(str(tmp), ignore_errors=True)
    print("addon selftest ok")
    return 0


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows pipes default to the ANSI code page; Claude Code reads UTF-8
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
