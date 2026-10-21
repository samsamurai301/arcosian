#!/usr/bin/env bash
# Runs in the fresh run directory; $0 is evals/<case>/scaffold.sh, so the plugin root is two levels up.
set -euo pipefail
PLUGIN="$(cd "$(dirname "$0")/../../../plugins/arcosian" && pwd)"
python3 "$PLUGIN/scripts/gs.py" init --title "Gate Eval" --engine godot --root . >/dev/null
echo "$PLUGIN" > plugin_root.txt
python3 "$PLUGIN/scripts/gs.py" feature add --id F001 --title "Core loop prototype" --area gameplay --priority P0 --accept "one full loop playable in under 60 s" >/dev/null
python3 "$PLUGIN/scripts/gs.py" feature start F001 >/dev/null
