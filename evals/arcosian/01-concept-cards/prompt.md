---
tags: [concept,ideation]
runs: 2
max_turns: 25
timeout_seconds: 600
allowed_tools: [Read, Write, Edit, Glob, Grep, Skill, Bash]
---
Use the Arcosian plugin's concept lab. Brief: a one-handed portrait mobile puzzle game for commuters, 3-minute sessions, free to play with rewarded ads, built by one developer in Godot.
Produce exactly three distinct concept cards and save them as .gamestudio/concepts/concept-1.json, concept-2.json and concept-3.json (concept schema, schema_version "1.0").
Then run `gs.py validate .gamestudio/concepts/concept-1.json .gamestudio/concepts/concept-2.json .gamestudio/concepts/concept-3.json` and write its full output to .gamestudio/reports/concept-validate.txt. The Arcosian plugin root path is in ./plugin_root.txt; scripts live in <root>/scripts/.
End with a one-line recommendation of which concept to prototype first.
