#!/usr/bin/env python3
"""PreToolUse guard.

Bash and PowerShell (Claude Code's shell on Windows): ask before store submission, deny reading signing secrets,
ask before recursively deleting project dirs.
Write/Edit/MultiEdit on .gamestudio/features.json: deny a done/passing feature that fails the gates.
"""
from __future__ import annotations

import json
import re
import shlex
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import emit, gslib, project_root, run, tool_path  # noqa: E402

STORE_RE = re.compile(
    r"\bfastlane\b[^;&|\n]*\b(deliver|upload_to_app_store|submit_for_review|upload_to_play_store|"
    r"promote_track|promote_track_to_track)\b"
    r"|\bfastlane\s+supply\b[^;&|\n]*(production|promote|rollout)"
    r"|\bxcrun\s+altool\b[^;&|\n]*--upload|\baltool\b[^;&|\n]*--upload"
    r"|\bnotarytool\s+(submit|store-credentials)\b"
    r"|\bTransporter\b[^;&|\n]*-m\s+upload|\bgradlew?\b[^;&|\n]*\bpublish\w*(Bundle|Apk|Release)\w*"
    r"|\bandroidpublisher\b", re.I)
KEYCHAIN_RE = re.compile(r"\bsecurity\s+(find-generic-password|find-internet-password|dump-keychain|"
                         r"export)\b|\bsecurity\s+cms\s+-D\b|\bGet-StoredCredential\b|\bvaultcmd(\.exe)?\s+/listcreds",
                         re.I)
READERS = {"cat", "less", "more", "head", "tail", "bat", "xxd", "hexdump", "od", "strings", "base64",
           "openssl", "grep", "rg", "awk", "sed", "source", ".", "nl", "tac", "cut", "sort", "uniq"}
# PowerShell cmdlets and aliases that print a file, plus the Windows tools commonly called from it.
PS_READERS = READERS | {"get-content", "gc", "type", "select-string", "sls", "format-hex", "fhx", "findstr",
                        "certutil", "get-pfxdata"}
PS_REMOVERS = {"remove-item", "rm", "ri", "del", "erase", "rd", "rmdir"}
IO_READ_RE = re.compile(r"\[(?:system\.)?io\.file\]::readall(?:text|bytes|lines)\s*\(([^)]*)\)", re.I)
SECRET_SUFFIXES = (".keystore", ".jks", ".p12", ".pfx", ".mobileprovision", ".p8")
PROTECTED_DIRS = {".gamestudio", "assets"}
DENY_SECRET = ("Reading or printing a signing secret (keystore, .p12, .mobileprovision, .p8 or .env) is blocked. "
               "Reference secrets by name and load them in CI.")
DENY_KEYCHAIN = "Reading keychain secrets is blocked. Signing credentials must come from CI secrets."
ASK_STORE = ("This command submits or promotes a build in a store. Confirm that release-manager pre-flight and the "
             "human release checkpoint are complete.")


def segments(command: str) -> List[List[str]]:
    """Split a shell command into simple commands and tokenise each (best effort)."""
    out = []
    for seg in re.split(r"&&|\|\||[;|&\n]", command):
        try:
            toks = shlex.split(seg)
        except ValueError:
            toks = seg.split()
        while toks and (re.match(r"^\w+=", toks[0]) or toks[0] in ("sudo", "command", "env", "time")):
            toks = toks[1:]
        if toks:
            out.append(toks)
    return out


def is_secret_file(token: str) -> bool:
    # Split on both separators so Windows paths are read the same on every host.
    name = token.split("=", 1)[-1].strip("'\"").replace("\\", "/").rstrip("/").rsplit("/", 1)[-1].lower()
    if name.endswith(SECRET_SUFFIXES):
        return True
    return (name == ".env" or name.startswith(".env.")) and not name.endswith(
        (".example", ".sample", ".template", ".dist"))


def ps_segments(command: str) -> List[List[str]]:
    """PowerShell flavour of segments(): backslashes are path separators, not escapes; `cmd /c` is unwrapped."""
    out = []
    for seg in re.split(r"&&|\|\||[;|\n]", command):
        try:
            toks = [t.strip("'\"") for t in shlex.split(seg, posix=False)]
        except ValueError:
            toks = seg.split()
        toks = [t for t in toks if t and t != "&"]  # the call operator
        while len(toks) > 2 and toks[0].lower() in ("cmd", "cmd.exe") and toks[1].lower() == "/c":
            toks = toks[2:]
        if toks:
            out.append(toks)
    return out


def ps_name(token: str) -> str:
    """Bare command name: no module prefix (Microsoft.PowerShell.Management\\Get-Content), path or .exe."""
    name = token.replace("\\", "/").rsplit("/", 1)[-1].lower()
    return name[:-4] if name.endswith(".exe") else name


def protected_target(t: str, cwd: Path, root: Path) -> bool:
    target = Path(t.replace("\\", "/")).expanduser()
    target = target if target.is_absolute() else cwd / target
    target = Path(re.sub(r"[\\/]\*$", "", str(target)))  # a trailing wildcard (dir/* or dir\*) targets dir
    try:
        resolved = target.resolve()
    except OSError:
        return False
    return resolved.name in PROTECTED_DIRS or resolved == root or resolved in root.parents


def ask_delete(t: str) -> Tuple[str, str]:
    return "ask", ("A recursive delete would remove %s, which holds project state or source assets. "
                   "Confirm this is intended." % t)


def guard_bash(payload: Dict[str, Any], root: Path) -> Optional[Tuple[str, str]]:
    command = str((payload.get("tool_input") or {}).get("command") or "")
    if KEYCHAIN_RE.search(command):
        return "deny", DENY_KEYCHAIN
    segs = segments(command)
    for toks in segs:
        cmd = Path(toks[0]).name
        if cmd in READERS and any(is_secret_file(t) for t in toks[1:]):
            return "deny", DENY_SECRET
    if STORE_RE.search(command):
        return "ask", ASK_STORE
    cwd = Path(payload.get("cwd") or ".")
    for toks in segs:
        if Path(toks[0]).name != "rm":
            continue
        flags = "".join(t for t in toks[1:] if t.startswith("-") and not t.startswith("--"))
        recursive = "r" in flags.lower() or "--recursive" in toks
        if not recursive:
            continue
        for t in toks[1:]:
            if not t.startswith("-") and protected_target(t, cwd, root):
                return ask_delete(t)
    return None


def guard_powershell(payload: Dict[str, Any], root: Path) -> Optional[Tuple[str, str]]:
    command = str((payload.get("tool_input") or {}).get("command") or "")
    if KEYCHAIN_RE.search(command):
        return "deny", DENY_KEYCHAIN
    for m in IO_READ_RE.finditer(command):
        if any(is_secret_file(arg.strip(" '\"")) for arg in m.group(1).split(",")):
            return "deny", DENY_SECRET
    segs = ps_segments(command)
    for toks in segs:
        if ps_name(toks[0]) in PS_READERS and any(is_secret_file(t) for t in toks[1:]):
            return "deny", DENY_SECRET
    if STORE_RE.search(command):
        return "ask", ASK_STORE
    cwd = Path(payload.get("cwd") or ".")
    for toks in segs:
        if ps_name(toks[0]) not in PS_REMOVERS:
            continue
        args = [t.lower() for t in toks[1:]]
        # -Recurse and its prefixes (-r, -rec), short clusters such as -rf, and cmd's rd /s.
        if not any(a.startswith("-r") or a == "/s" or (re.fullmatch(r"-[a-z]{2,3}", a) and "r" in a) for a in args):
            continue
        for t in toks[1:]:
            if not t.startswith("-") and not re.fullmatch(r"/[a-z?]", t, re.I) and protected_target(t, cwd, root):
                return ask_delete(t)
    return None


def apply_edits(payload: Dict[str, Any], path: Path) -> Optional[str]:
    """Reconstruct the file text after the tool call; None when it cannot be determined."""
    tool = payload.get("tool_name")
    ti = payload.get("tool_input") or {}
    if tool == "Write":
        return ti.get("content") if isinstance(ti.get("content"), str) else None
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    edits = ti.get("edits") if tool == "MultiEdit" else [ti]
    for e in edits or []:
        old, new = e.get("old_string"), e.get("new_string")
        if not isinstance(old, str) or not isinstance(new, str) or old not in text:
            return None
        text = text.replace(old, new) if e.get("replace_all") else text.replace(old, new, 1)
    return text


def guard_features(payload: Dict[str, Any], path: Path, root: Path) -> Optional[Tuple[str, str]]:
    text = apply_edits(payload, path)
    if text is None:
        return None
    try:
        new_doc = json.loads(text)
    except ValueError:
        return None  # invalid JSON is reported by the PostToolUse schema check
    old_doc = gslib.load_json(path, default=None)
    old = {str(f.get("id")): f for f in gslib.get_features(old_doc)}
    new = {str(f.get("id")): f for f in gslib.get_features(new_doc)}
    problems: List[str] = []
    for fid, f in new.items():
        if (f.get("passes") is True or f.get("status") == "done") and f != old.get(fid):
            ok, probs = gslib.check_feature_pass(f, root)
            if not ok:
                problems.append("%s cannot be marked done/passing: %s" % (fid, "; ".join(probs[:4])))
    for fid, f in old.items():
        if f.get("passes") is True and fid not in new:
            problems.append("%s is passing and cannot be deleted; set it to blocked or open a replacement." % fid)
    if problems:
        return "deny", ("Five-gate rule (BLUEPRINT section 6): " + " | ".join(problems[:5]) +
                        " Run the gates and record evidence with gs.py feature gate/pass instead of editing the JSON.")
    return None


def handle(payload: Dict[str, Any]) -> None:
    tool = payload.get("tool_name")
    result = None
    if tool in ("Bash", "PowerShell"):
        root = project_root(payload)
        guard = guard_bash if tool == "Bash" else guard_powershell
        result = guard(payload, root) if root else None
    elif tool in ("Write", "Edit", "MultiEdit"):
        path = tool_path(payload)
        if path is not None and path.name == "features.json" and path.parent.name == gslib.GS_DIRNAME:
            root = gslib.find_project_root(path.parent)
            result = guard_features(payload, path, root) if root else None
    if result:
        emit({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": result[0],
                                     "permissionDecisionReason": result[1]}})


if __name__ == "__main__":
    run(handle)
