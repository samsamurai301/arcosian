#!/usr/bin/env python3
"""SessionStart: inject the project summary, or hint at /arcosian:studio for a bare engine project.
Where Python 3 is not `python3` (typical on Windows), also tell Claude which command to use for the plugin's scripts."""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import emit, gslib, project_root, run  # noqa: E402


def handle(payload: dict) -> None:
    cwd = payload.get("cwd") or "."
    root = project_root(payload)
    text = ""
    if root is not None:
        text = gslib.summarize(root)
    else:
        engine, _ver, _rel = gslib.detect_engine(cwd)
        if engine:
            text = ("arcosian: a %s project was detected here without a .gamestudio/ directory. "
                    "Run /arcosian:studio to set up the design contract, feature list and gates."
                    % engine)
    python = os.environ.get("GS_PYTHON", "")  # set by run-python.mjs to the command that started this hook
    if python and python != "python3":
        note = ("arcosian: on this machine Python 3 runs as `%s`; use it wherever the skills and docs say `python3`."
                % python)
        text = text + "\n\n" + note if text else note
    if text:
        emit({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": text}})


if __name__ == "__main__":
    run(handle)
