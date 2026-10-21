---
tags: [deconstruct,research]
runs: 2
max_turns: 30
timeout_seconds: 600
allowed_tools: [Read, Write, Edit, Glob, Grep, Skill, Bash]
---
Deconstruct the mobile game Royal Match using the plugin's deconstruct skill. Work from what you know; do not browse the web. Save the result as .gamestudio/research/royal-match.deconstruction.json (deconstruction schema, schema_version "1.0"), flagging anything you are unsure of as unverified, then run `gs.py validate` on it and write the output to .gamestudio/reports/deconstruct-validate.txt. The Arcosian plugin root path is in ./plugin_root.txt; scripts live in <root>/scripts/.
Include core loop, meta loops, economy sinks and sources, monetization, retention hooks, psychology principles, weaknesses, and at least five concrete lessons and borrow_for_us items.
