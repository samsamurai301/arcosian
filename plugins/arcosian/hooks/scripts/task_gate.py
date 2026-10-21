#!/usr/bin/env python3
"""TaskCompleted: refuse completion of a task that names a feature id which does not pass its gates."""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _common import gslib, project_root, run  # noqa: E402


def handle(payload: dict) -> None:
    root = project_root(payload)
    if root is None:
        return
    text = " ".join(str(payload.get(k) or "") for k in ("task_subject", "task_description", "task_title"))
    ids = sorted(set(m.upper() for m in re.findall(r"\bF\d{3,4}\b", text, re.I)))
    if not ids:
        return
    doc = gslib.load_json(gslib.state_path(root, "features"), default=None)
    msgs = []
    for fid in ids:
        feat = gslib.find_feature(doc, fid)
        if feat is None or (feat.get("passes") is True and gslib.check_feature_pass(feat, root)[0]):
            continue
        ok, problems = gslib.check_feature_pass(feat, root)
        msgs.append("%s does not pass its gates: %s" % (fid, "; ".join(problems[:5]) or "passes is false"))
    if msgs:
        sys.stderr.write("Task not complete.\n" + "\n".join(msgs) +
                         "\nRun the missing gates (gs.py feature gate ...) before completing this task.\n")
        sys.exit(2)


if __name__ == "__main__":
    run(handle)
