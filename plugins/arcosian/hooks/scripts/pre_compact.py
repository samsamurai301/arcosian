#!/usr/bin/env python3
"""PreCompact: snapshot the project summary to .gamestudio/snapshots/precompact-<timestamp>.md."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import gslib, project_root, run  # noqa: E402


def handle(payload: dict) -> None:
    root = project_root(payload)
    if root is None:
        return
    snap_dir = gslib.gs_dir(root) / "snapshots"
    snap_dir.mkdir(parents=True, exist_ok=True)
    stamp = gslib.now_stamp().replace(" ", "-").replace(":", "")
    body = "# Pre-compaction snapshot %s\n\ntrigger: %s\n\n%s\n" % (
        gslib.now_iso(), payload.get("trigger") or "unknown", gslib.summarize(root, max_chars=6000))
    (snap_dir / ("precompact-%s.md" % stamp)).write_text(body, encoding="utf-8")


if __name__ == "__main__":
    run(handle)
