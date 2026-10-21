---
tags: [economy,simulation]
runs: 2
max_turns: 35
timeout_seconds: 600
allowed_tools: [Read, Write, Edit, Glob, Grep, Skill, Bash]
---
Design a soft-currency economy for a casual puzzle game with energy-gated play and one starter IAP pack. Save the model as .gamestudio/economy/model.json (economy-model schema, schema_version "1.0", at least two archetypes, a source, a sink and a converter node, and one offer). Validate it, then run `python3 <root>/scripts/economy_sim.py --model .gamestudio/economy/model.json --runs 100 --json --out .gamestudio/economy/sim.json`.
Write .gamestudio/economy/findings.md with: the hoard risk (days of soft-currency stockpile), days to complete content versus the target, which archetype breaks first, and one concrete rebalance. The Arcosian plugin root path is in ./plugin_root.txt; scripts live in <root>/scripts/.
