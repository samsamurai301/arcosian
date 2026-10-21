#!/usr/bin/env bash
# Runs in the fresh run directory; $0 is evals/<case>/scaffold.sh, so the plugin root is two levels up.
set -euo pipefail
PLUGIN="$(cd "$(dirname "$0")/../../../plugins/arcosian" && pwd)"
python3 "$PLUGIN/scripts/gs.py" init --platforms ios,android --title "Gateway Eval" --engine godot --root . >/dev/null
echo "$PLUGIN" > plugin_root.txt
