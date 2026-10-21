#!/usr/bin/env python3
"""Connector catalog check: every MCP server a plugin registers must be in docs/connectors.json with a trust level,
pinned, free of literal secrets, and the rendered docs/CONNECTORS.md must be current.

  python3 tools/check_connectors.py            check (CI)
  python3 tools/check_connectors.py --write    regenerate docs/CONNECTORS.md
  python3 tools/check_connectors.py --selftest

Exit codes: 0 ok, 1 problems found, 2 usage error.
"""
import argparse
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Tuple

TRUST = ("first-party", "official", "community")
PINNED = (re.compile(r"@\d+\.\d+\.\d+"), re.compile(r"==\d+\.\d+\.\d+"))
LAUNCHERS = ("npx", "uvx", "bunx", "pnpm", "yarn")
SECRET_RE = re.compile(r"(ghp_|github_pat_|sk-|xox[bp]-|AKIA|AIza)[A-Za-z0-9_-]{8,}")
PLACEHOLDER_RE = re.compile(r"^\$\{[^}]+\}$|^Bearer \$\{[^}]+\}$")


def source_of(cfg: Dict[str, Any]) -> Tuple[str, str]:
    if cfg.get("url"):
        return cfg.get("type", "http"), cfg["url"]
    return "stdio", " ".join([cfg.get("command", "")] + [str(a) for a in cfg.get("args", [])]).strip()


def registered(repo: Path) -> List[Dict[str, Any]]:
    out = []
    for f in sorted(repo.glob("plugins/*/.mcp.json")):
        doc = json.loads(f.read_text(encoding="utf-8"))
        for name, cfg in (doc.get("mcpServers") or {}).items():
            transport, src = source_of(cfg)
            out.append({"plugin": f.parent.name, "server": name, "transport": transport, "source": src, "cfg": cfg})
    return out


def check(repo: Path) -> List[str]:
    problems: List[str] = []
    cat = json.loads((repo / "docs" / "connectors.json").read_text(encoding="utf-8"))
    entries = {(c["plugin"], c["server"]): c for c in cat.get("connectors", [])}
    regs = registered(repo)
    seen = set()
    for r in regs:
        key = (r["plugin"], r["server"])
        seen.add(key)
        c = entries.get(key)
        where = "%s/%s" % key
        if not c:
            problems.append("%s: registered in .mcp.json but missing from docs/connectors.json" % where)
            continue
        if c.get("trust") not in TRUST:
            problems.append("%s: trust must be one of %s" % (where, ", ".join(TRUST)))
        if c.get("transport") != r["transport"] or c.get("source") != r["source"]:
            problems.append("%s: catalog says %s %r, .mcp.json has %s %r" % (where, c.get("transport"), c.get("source"),
                                                                           r["transport"], r["source"]))
        cmd = r["cfg"].get("command", "")
        if cmd in LAUNCHERS and not any(p.search(r["source"]) for p in PINNED):
            problems.append("%s: %s launcher is not pinned to an exact version" % (where, cmd))
        if r["transport"] != "stdio" and not r["source"].startswith("https://"):
            problems.append("%s: remote servers must use https" % where)
        for k, v in list((r["cfg"].get("env") or {}).items()) + list((r["cfg"].get("headers") or {}).items()):
            if SECRET_RE.search(str(v)):
                problems.append("%s: %s looks like a literal secret" % (where, k))
            elif re.search(r"(?i)key|token|secret|authorization|password", k) and not PLACEHOLDER_RE.match(str(v)):
                problems.append("%s: %s must come from a ${...} placeholder (plugin option or environment)" % (where, k))
        for field in ("vendor", "auth", "verified"):
            if not c.get(field):
                problems.append("%s: catalog entry needs %s" % (where, field))
    for key in entries:
        if key not in seen:
            problems.append("%s/%s: in docs/connectors.json but no plugin registers it" % key)
    expected = render(cat)
    md = repo / "docs" / "CONNECTORS.md"
    # compare without line endings: a Windows checkout may convert LF to CRLF
    if not md.is_file() or md.read_text(encoding="utf-8").replace("\r\n", "\n") != expected:
        problems.append("docs/CONNECTORS.md is out of date: run python3 tools/check_connectors.py --write")
    return problems


def render(cat: Dict[str, Any]) -> str:
    lines = ["# Connector catalog", "",
             "Every MCP server that an Arcosian plugin registers, with where it comes from and how much to trust it. "
             "Generated from `docs/connectors.json` by `tools/check_connectors.py --write`; CI fails when the two differ "
             "or when a plugin registers a server that is not listed here.", "",
             "Trust levels:", ""]
    for k in TRUST:
        lines.append("- **%s**: %s" % (k, cat.get("trust_levels", {}).get(k, "")))
    lines += ["", "Servers that need an account do nothing until you sign in or add a key; nothing is sent before that.", "",
              "| Plugin | Server | Transport | Source | Vendor | Trust | Auth | Checked |", "|---|---|---|---|---|---|---|---|"]
    for c in sorted(cat.get("connectors", []), key=lambda c: (c["plugin"], c["server"])):
        lines.append("| `%s` | `%s` | %s | `%s` | %s | %s | %s | %s |" % (
            c["plugin"], c["server"], c["transport"], c["source"].replace("|", "\\|"), c["vendor"], c["trust"],
            c["auth"], c["verified"]))
    docs = cat.get("documented_only") or []
    if docs:
        lines += ["", "## Documented, not registered", "",
                  "These appear in the skills as options but are not started by any plugin.", "",
                  "| Plugin | Server | Source | Why not registered |", "|---|---|---|---|"]
        for d in docs:
            lines.append("| `%s` | %s | %s | %s |" % (d["plugin"], d["server"], d["source"], d["why"]))
    lines += ["", "## Proposing a connector", "",
              "Open a connector proposal issue with the vendor's documentation link, the exact package version or URL, "
              "what it can read and write, and how it authenticates. See [EXTENDING.md](EXTENDING.md).", ""]
    return "\n".join(lines)


def main(argv: List[str] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--repo", default=str(Path(__file__).resolve().parent.parent))
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    repo = Path(a.repo)
    if a.write:
        cat = json.loads((repo / "docs" / "connectors.json").read_text(encoding="utf-8"))
        (repo / "docs" / "CONNECTORS.md").write_text(render(cat), encoding="utf-8")
    problems = check(repo)
    for p in problems:
        print("PROBLEM " + p)
    print("connectors: %d registered, %d problem(s)" % (len(registered(repo)), len(problems)))
    return 1 if problems else 0


def selftest() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="conn-"))
    try:
        (tmp / "docs").mkdir()
        p = tmp / "plugins" / "demo"
        p.mkdir(parents=True)
        (p / ".mcp.json").write_text(json.dumps({"mcpServers": {
            "ok": {"command": "npx", "args": ["-y", "pkg@1.2.3"], "env": {"API_KEY": "${user_config.k}"}},
            "loose": {"command": "npx", "args": ["-y", "pkg"]},
            "leak": {"type": "http", "url": "https://x.example/mcp", "headers": {"Authorization": "Bearer ghp_abcdefghijklmnop"}}}}),
            encoding="utf-8")
        cat = {"connectors": [
            {"plugin": "demo", "server": "ok", "transport": "stdio", "source": "npx -y pkg@1.2.3", "vendor": "v", "trust": "official", "auth": "key", "verified": "x"},
            {"plugin": "demo", "server": "loose", "transport": "stdio", "source": "npx -y pkg", "vendor": "v", "trust": "community", "auth": "-", "verified": "x"},
            {"plugin": "demo", "server": "ghost", "transport": "http", "source": "https://g", "vendor": "v", "trust": "official", "auth": "-", "verified": "x"}]}
        (tmp / "docs" / "connectors.json").write_text(json.dumps(cat), encoding="utf-8")
        probs = "\n".join(check(tmp))
        for needle in ("demo/loose: npx launcher is not pinned", "demo/leak: registered in .mcp.json but missing",
                       "demo/ghost: in docs/connectors.json but no plugin", "CONNECTORS.md is out of date"):
            assert needle in probs, (needle, probs)
        assert "demo/ok" not in probs, probs
        cat["connectors"] = cat["connectors"][:1]
        (tmp / "docs" / "connectors.json").write_text(json.dumps(cat), encoding="utf-8")
        (p / ".mcp.json").write_text(json.dumps({"mcpServers": {"ok": {"command": "npx", "args": ["-y", "pkg@1.2.3"],
                                                                       "env": {"API_KEY": "${user_config.k}"}}}}), encoding="utf-8")
        (tmp / "docs" / "CONNECTORS.md").write_text(render(cat), encoding="utf-8")
        assert check(tmp) == [], check(tmp)
    finally:
        shutil.rmtree(str(tmp), ignore_errors=True)
    print("check_connectors selftest ok")
    return 0


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows pipes default to the ANSI code page; Claude Code reads UTF-8
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
