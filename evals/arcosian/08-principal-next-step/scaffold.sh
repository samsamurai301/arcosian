#!/usr/bin/env bash
# Runs in the fresh run directory; $0 is evals/<case>/scaffold.sh, so the plugin root is two levels up.
set -euo pipefail
PLUGIN="$(cd "$(dirname "$0")/../../../plugins/arcosian" && pwd)"
python3 "$PLUGIN/scripts/gs.py" init --title "Principal Eval" --engine godot --root . >/dev/null
echo "$PLUGIN" > plugin_root.txt
G() { python3 "$PLUGIN/scripts/gs.py" "$@"; }
G feature add --id F001 --title "Core merge loop" --area gameplay --priority P0 --accept "merge two tiles into one" >/dev/null
G feature add --id F002 --title "Energy and lives" --area meta --priority P1 --depends F001 >/dev/null
G feature add --id F003 --title "Rewarded ad placement" --area monetization --priority P1 --depends F002 >/dev/null
G feature start F001 >/dev/null
G evidence-dir F001 >/dev/null
echo "compile ok" > .gamestudio/evidence/F001/static.log
G feature gate F001 static pass --evidence .gamestudio/evidence/F001/static.log >/dev/null
G progress "F001 implemented; static gate passed; no tests or playthrough yet" >/dev/null
