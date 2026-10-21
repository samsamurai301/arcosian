---
tags: [compliance,release]
runs: 2
max_turns: 25
timeout_seconds: 600
allowed_tools: [Read, Write, Edit, Glob, Grep, Skill, Bash]
---
We plan to ship this Godot project to Google Play next week. Run the store compliance pre-flight on it (compliance_preflight.py --project . --platform android --json) and save the JSON to .gamestudio/reports/preflight.json. Then write .gamestudio/reports/preflight-summary.md listing each blocker with its fix, and state clearly whether we can ship. The Arcosian plugin root path is in ./plugin_root.txt; scripts live in <root>/scripts/.
