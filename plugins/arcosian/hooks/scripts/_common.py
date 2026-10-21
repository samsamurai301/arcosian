"""Shared plumbing for the arcosian hooks: gslib import, stdin/stdout JSON, fail-open runner."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Callable, Dict, Optional

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PLUGIN_ROOT / "scripts"))

import gslib  # noqa: E402  (path set above)


def read_input() -> Dict[str, Any]:
    """Parse the hook payload from stdin; an unreadable payload is an empty dict."""
    try:
        data = json.load(sys.stdin)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def emit(obj: Dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(obj))
    sys.stdout.write("\n")
    sys.stdout.flush()


def tool_path(payload: Dict[str, Any]) -> Optional[Path]:
    """Absolute path of tool_input.file_path (relative paths resolve against cwd), or None."""
    fp = (payload.get("tool_input") or {}).get("file_path")
    if not isinstance(fp, str) or not fp:
        return None
    p = Path(fp).expanduser()
    if not p.is_absolute():
        p = Path(payload.get("cwd") or ".") / p
    return p


def project_root(payload: Dict[str, Any], path: Optional[Path] = None) -> Optional[Path]:
    """Nearest `.gamestudio/` ancestor of `path` (when given) or of the session cwd."""
    return gslib.find_project_root(path if path is not None else (payload.get("cwd") or "."))


def run(handler: Callable[[Dict[str, Any]], None]) -> None:
    """Run a hook handler; any internal error fails open (exit 0, note on stderr)."""
    try:
        handler(read_input())
    except SystemExit:
        raise
    except Exception as exc:
        sys.stderr.write("arcosian hook %s failed open: %s: %s\n"
                         % (Path(sys.argv[0]).name, type(exc).__name__, exc))
    sys.exit(0)
