#!/usr/bin/env python3
"""Stop / SubagentStop: block while a feature is marked done but fails the five-gate rule."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import emit, gslib, project_root, run  # noqa: E402


def handle(payload: dict) -> None:
    if payload.get("stop_hook_active"):
        return
    root = project_root(payload)
    if root is None:
        return
    doc = gslib.load_json(gslib.state_path(root, "features"), default=None)
    bad = [(fid, p) for fid, p in gslib.dod_violations(doc, root)]
    if not bad:
        return
    lines = ["Features are marked done but fail the five-gate definition of done:"]
    for fid, problems in bad[:8]:
        lines.append("- %s: %s" % (fid, "; ".join(problems[:4])))
    lines.append("Run the missing gates and record evidence (gs.py feature gate ...), or set the feature "
                 "back to in_progress, before stopping.")
    emit({"decision": "block", "reason": "\n".join(lines)})


if __name__ == "__main__":
    run(handle)
