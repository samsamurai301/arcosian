#!/usr/bin/env bash
# Runs in the fresh run directory; $0 is evals/<case>/scaffold.sh, so the plugin root is two levels up.
set -euo pipefail
PLUGIN="$(cd "$(dirname "$0")/../../../plugins/arcosian" && pwd)"
python3 "$PLUGIN/scripts/gs.py" init --title "Compliance Eval" --engine godot --root . >/dev/null
echo "$PLUGIN" > plugin_root.txt
cat > project.godot <<'EOF'
[application]
config/name="Tiles"
config/features=PackedStringArray("4.5", "Mobile")
EOF
cat > export_presets.cfg <<'EOF'
[preset.0]
platform="Android"
[preset.0.options]
gradle_build/use_gradle_build=true
gradle_build/target_sdk="34"
package/unique_name="com.example.tiles"
EOF
