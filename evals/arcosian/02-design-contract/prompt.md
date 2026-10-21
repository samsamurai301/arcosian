---
tags: [contract,validation]
runs: 2
max_turns: 30
timeout_seconds: 600
allowed_tools: [Read, Write, Edit, Glob, Grep, Skill, Bash]
---
Fill .gamestudio/contract.json for this game: "Pebble Keep", a portrait mobile tower-defence-meets-merge game, hybrid monetization (rewarded ads plus IAP), target audience age 13+, Godot. Replace every TBD with real content: 3-5 pillars, verbs, at least two mechanics, a core loop, a FTUE with an aha moment under 60 seconds, perf budgets, scope tier, risks and kill criteria.
Run `python3 <root>/scripts/gs.py validate .gamestudio/contract.json` and write the complete command output to .gamestudio/reports/contract-validate.txt, then fix any errors and re-run until it reports 0 failed. The Arcosian plugin root path is in ./plugin_root.txt; scripts live in <root>/scripts/.
