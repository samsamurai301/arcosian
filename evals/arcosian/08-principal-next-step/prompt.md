---
tags: [principal,routing]
runs: 2
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Write, Edit, Glob, Grep, Skill, Bash]
---
Act as the studio principal. We are half-way through this project and the producer wants to start the rewarded ad placement (F003) tomorrow. What should we do next? Read the project state first (gs.py status and feature list), answer with the single recommended next step and why, and write it to .gamestudio/reports/next-step.md. Do not change features.json. The Arcosian plugin root path is in ./plugin_root.txt; scripts live in <root>/scripts/.
