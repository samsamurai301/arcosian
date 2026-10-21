#!/usr/bin/env python3
"""PostToolUse (Write/Edit/MultiEdit): GDScript parse check (valid scripts that only look broken because the
import caches are stale are re-checked after a cache refresh, never blocked), duplicate scene uids, schema check
of .gamestudio JSON, and a manifest reminder for new binary assets."""
from __future__ import annotations

import contextlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Set

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import emit, gslib, project_root, run, tool_path  # noqa: E402

SKIP_DIRS = {".godot", ".git", "node_modules", ".import", "Library", "Temp"}
BINARY_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".svg", ".ogg", ".wav", ".mp3", ".flac", ".glb", ".gltf",
               ".fbx", ".obj", ".ttf", ".otf", ".mp4", ".webm"}
UID_RE = re.compile(r'^\[gd_(?:scene|resource)\b[^\]]*\buid="(uid://[^"]+)"', re.M)

# `--check-only --script` runs the analyzer without the editor's caches. Two kinds of "Parse Error" are artefacts of a
# missing or stale import (the script is fine): a type from a `class_name` script that is not yet in
# .godot/global_script_class_cache.cfg, and a preload of an asset that has no `.import` sidecar yet. They are
# resolved by refreshing the caches (`--import`) and checking again; autoload names are not an issue for the
# analyzer (their "Compile Error: Identifier not found" is not a Parse Error and is not reported here).
CLASS_NAME_RE = re.compile(r"^\s*class_name\s+([A-Za-z_]\w*)", re.M)
UNRESOLVED_TYPE_RE = re.compile(r'(?:Could not find (?:type|base class)|Could not resolve class|Identifier) "([A-Za-z_]\w*)"')
NO_LOADER_RE = re.compile(r'Preload file "res://([^"]+)" has no resource loaders')
CASCADE_RE = re.compile(r"Cannot infer the type of \"[^\"]*\" variable because the value doesn't have a set type")
CHECK_BUDGET_SEC = 34.0  # hooks.json allows 40 s for this hook


def _adapter_option(key: str) -> Optional[str]:
    """An option of the arcosian-godot adapter. Its SessionStart hook saves them to its own plugin data folder,
    which sits next to this plugin's and is named after the adapter (arcosian-<suffix> -> arcosian-godot-<suffix>)."""
    data = Path(os.environ.get("CLAUDE_PLUGIN_DATA") or "")
    if not data.name.startswith("arcosian-"):
        return None
    try:
        value = json.loads((data.parent / ("arcosian-godot-" + data.name[len("arcosian-"):]) / "options.json")
                           .read_text(encoding="utf-8")).get(key)
    except (OSError, ValueError, AttributeError):
        return None
    return value if isinstance(value, str) else None


def _godot_path(cand: Optional[str]) -> Optional[str]:
    """A Godot path as users give it: the binary, a macOS .app, a folder holding Godot, or a Windows GUI .exe, which is
    swapped for its _console twin because only the console build's output can be read through a pipe."""
    if not cand:
        return None
    p = Path(cand).expanduser()
    if (p / "Contents" / "MacOS" / "Godot").is_file():
        p = p / "Contents" / "MacOS" / "Godot"
    elif p.is_dir():
        exes = sorted(c for c in p.iterdir() if c.name.lower().startswith("godot") and c.suffix.lower() == ".exe")
        plain = next((p / n for n in ("godot", "godot4", "Godot") if (p / n).is_file()), None)
        if not exes and plain is None:
            return None
        p = next((c for c in exes if c.stem.lower().endswith("_console")), exes[0]) if exes else plain
    if p.suffix.lower() == ".exe" and not p.stem.lower().endswith("_console"):
        twin = p.with_name(p.stem + "_console.exe")
        if twin.is_file():
            p = twin
    return str(p) if p.is_file() else None


def godot_binary() -> Optional[str]:
    """GODOT_BIN, the godot adapter's godot_bin option, godot/godot4 on PATH, a versioned Windows download on PATH
    (Godot_v4.7.2-stable_win64.exe keeps that name), then the default macOS install."""
    cands = [os.environ.get("GODOT_BIN"), _adapter_option("godot_bin"), shutil.which("godot"), shutil.which("godot4")]
    for d in os.environ.get("PATH", "").split(os.pathsep):
        try:
            names = sorted(n for n in os.listdir(d) if n.lower().startswith("godot") and n.lower().endswith(".exe")) if d else []
        except OSError:
            continue
        cands += [os.path.join(d, n) for n in names]
    if sys.platform == "darwin":
        cands.append("/Applications/Godot.app")
    for cand in cands:
        found = _godot_path(cand)
        if found:
            return found
    return None


def godot_project_dir(path: Path) -> Optional[Path]:
    for d in path.parents:
        if (d / "project.godot").is_file():
            return d
    return None


def parse_errors(binary: str, proj: Path, rel: str, timeout: float) -> Optional[List[str]]:
    """Parse errors reported by `godot --headless --check-only --script` (it exits 0, so scan output).
    None when Godot could not be run (missing, timed out): the hook then fails open."""
    try:
        r = subprocess.run([binary, "--headless", "--path", str(proj), "--check-only", "--script", "res://" + rel],
                           capture_output=True, text=True, timeout=max(timeout, 1.0), stdin=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError):
        return None
    lines = (r.stdout + "\n" + r.stderr).splitlines()
    errors = []
    for i, ln in enumerate(lines):
        if "Parse Error" in ln:
            where = lines[i + 1].strip() if i + 1 < len(lines) and lines[i + 1].strip().startswith("at:") else ""
            errors.append("%s %s" % (ln.replace("SCRIPT ERROR:", "").strip(), where))
    return errors


def project_class_names(proj: Path) -> Set[str]:
    """Every `class_name X` declared by a script in the project."""
    names: Set[str] = set()
    for dirpath, dirnames, files in os.walk(str(proj)):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in files:
            if fn.endswith(".gd"):
                try:
                    names.update(CLASS_NAME_RE.findall((Path(dirpath) / fn).read_text(encoding="utf-8", errors="replace")))
                except OSError:
                    continue
    return names


def stale_cache_errors(errors: List[str], proj: Path) -> List[str]:
    """The errors that only mean the import caches are stale or missing (see the comment on CLASS_NAME_RE)."""
    names: Optional[Set[str]] = None
    found = []
    for e in errors:
        m = UNRESOLVED_TYPE_RE.search(e)
        if m:
            names = project_class_names(proj) if names is None else names
            if m.group(1) in names:
                found.append(e)
                continue
        m = NO_LOADER_RE.search(e)
        if m and not (proj / (m.group(1) + ".import")).exists():
            found.append(e)
    return found


@contextlib.contextmanager
def import_lock(proj: Path, deadline: float) -> Iterator[bool]:
    """Serialise cache refreshes: parallel tool calls fire parallel hooks and two `--import` runs would race.
    Yields False when the lock could not be taken before `deadline` (gslib.try_lock: macOS, Linux and Windows)."""
    try:
        (proj / ".godot").mkdir(exist_ok=True)
        fh = open(str(proj / ".godot" / "arcosian-import.lock"), "a+", encoding="utf-8")
    except OSError:
        yield False
        return
    try:
        while not gslib.try_lock(fh):
            if time.monotonic() >= deadline:
                yield False
                return
            time.sleep(0.1)
        try:
            yield True
        finally:
            gslib.unlock(fh)
    finally:
        fh.close()


def refresh_import(binary: str, proj: Path, timeout: float) -> bool:
    """`godot --headless --path <proj> --import`: rebuilds the class-name cache and the import sidecars.
    Side effect: Godot 4.4+ also writes the `.gd.uid` files, which belong in version control anyway."""
    try:
        r = subprocess.run([binary, "--headless", "--path", str(proj), "--import"], capture_output=True, text=True,
                           timeout=max(timeout, 1.0), stdin=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError):
        return False
    return r.returncode == 0


def check_gdscript(path: Path) -> List[str]:
    """Parse errors of one script, without the false positives of a missing or stale import cache.

    Errors that only mean "types or assets not imported yet" trigger one `--import` and a second check, whose result
    is reported as is. If the refresh cannot run in time, those errors are dropped (fail open) rather than blocking
    a valid script; real syntax and type errors are reported either way."""
    binary, proj = godot_binary(), godot_project_dir(path)
    if not binary or not proj:
        return []
    rel = path.relative_to(proj).as_posix()
    deadline = time.monotonic() + CHECK_BUDGET_SEC
    errors = parse_errors(binary, proj, rel, min(15.0, deadline - time.monotonic()))
    if errors is None:
        return []
    if not stale_cache_errors(errors, proj):
        return errors[:10]
    with import_lock(proj, deadline) as locked:
        if locked:
            fresh = parse_errors(binary, proj, rel, deadline - time.monotonic())  # a parallel hook may have refreshed it
            if fresh is not None and not stale_cache_errors(fresh, proj):
                return fresh[:10]
            if refresh_import(binary, proj, deadline - time.monotonic() - 3.0):
                fresh = parse_errors(binary, proj, rel, deadline - time.monotonic())
                if fresh is not None:
                    return fresh[:10]
    stale = set(stale_cache_errors(errors, proj))
    return [e for e in errors if e not in stale and not CASCADE_RE.search(e)][:10]


def duplicate_uids(path: Path) -> List[str]:
    proj = godot_project_dir(path)
    if proj is None:
        return []
    seen: Dict[str, List[str]] = {}
    for dirpath, dirnames, files in os.walk(str(proj)):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in files:
            if fn.endswith((".tscn", ".tres")):
                fp = Path(dirpath) / fn
                try:
                    head = fp.read_text(encoding="utf-8", errors="replace")[:4000]
                except OSError:
                    continue
                m = UID_RE.search(head)
                if m:
                    seen.setdefault(m.group(1), []).append(fp.relative_to(proj).as_posix())
    me = path.relative_to(proj).as_posix()
    return ["%s is defined by %s" % (uid, ", ".join(fs)) for uid, fs in seen.items() if len(fs) > 1 and me in fs]


def check_gs_json(path: Path) -> List[str]:
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except ValueError as exc:
        return ["%s: invalid JSON: %s" % (path.name, exc)]
    except OSError:
        return []
    return gslib.validate_file(path)


def unlisted_asset(path: Path, root: Path) -> bool:
    if path.suffix.lower() not in BINARY_EXTS or not path.exists():
        return False
    rel = path.relative_to(root).as_posix() if root in path.parents else path.name
    if "assets" not in rel.split("/") and not rel.startswith("assets/"):
        return False
    manifest = gslib.load_json(gslib.state_path(root, "manifest"), default=None) or {}
    paths = [str(a.get("path", "")).lstrip("./") for a in manifest.get("assets", []) if isinstance(a, dict)]
    return not any(rel == p or rel.endswith("/" + p) or p.endswith("/" + rel) for p in paths if p)


def handle(payload: dict) -> None:
    path = tool_path(payload)
    if path is None:
        return
    root = gslib.find_project_root(path)
    if root is None:
        return
    reason = ""
    if path.suffix == ".gd":
        errs = check_gdscript(path)
        if errs:
            reason = "GDScript parse errors in %s:\n- %s" % (path.name, "\n- ".join(errs))
    elif path.suffix in (".tscn", ".tres"):
        errs = duplicate_uids(path)
        if errs:
            reason = "Duplicate Godot uid in %s (give the new file a fresh uid or delete the uid line):\n- %s" % (
                path.name, "\n- ".join(errs))
    elif path.suffix == ".json" and gslib.GS_DIRNAME in path.parts:
        errs = check_gs_json(path)
        if errs:
            reason = "%s fails schema validation:\n- %s" % (path.name, "\n- ".join(errs[:10]))
    if reason:
        emit({"decision": "block", "reason": reason})
    elif unlisted_asset(path, root):
        emit({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext":
              "Asset %s is not in .gamestudio/assets/manifest.json. Record provenance and licence "
              "as a manifest entry before relying on it." % path.name}})


if __name__ == "__main__":
    run(handle)
