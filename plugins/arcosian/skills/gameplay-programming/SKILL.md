---
name: gameplay-programming
description: 'Gameplay programming codex: vector math, easing, springs, kinematic controllers, jump arcs, cameras, grids and hexes, collision, pathfinding (BFS, A*, JPS, flow fields), PRNG, shuffle bags, pity, plus recipes for inventory, crafting, quests, timers, waves, match-3, merge, idle big numbers, block puzzles, runners. Use when implementing movement, feel, grids, search, randomness, or a game system.'
when_to_use: 'Implementing a mechanic or system in code; fixing movement, camera, collision or frame-rate bugs; choosing pathfinding or RNG approaches; making randomness feel fair.'
---

# Gameplay Programming

The code-level craft behind mechanics: the maths, algorithms and system recipes that turn a design card into rules that are correct, deterministic and pleasant to play on a phone. Everything here is written to live in the sim core described by `game-architecture`.

## What this skill gives you

- Formulas and snippets for vectors, frame-rate independent smoothing, easing, springs, Bezier curves, grids, hex coordinates, collision tests, kinematic controllers, jump arcs and cameras.
- Search toolkit: BFS, Dijkstra, A*, jump point search and flow fields, with a chooser and the mobile budget rules.
- Randomness toolkit: PRNG choice, seeding and streams, shuffle bags, pseudo-random distribution, alias tables, fairness perception.
- A systems cookbook: inventory, crafting, quests, achievements, timers and energy, spawners and waves, match-3, merge boards, idle big numbers and offline progress, block placement, runner chunks.
- Test and verification habits: invariants, golden seeds, fairness checks, bots.

## Core models

**1. Rates per second, integrations per step.** Every speed is per second and every update takes `dt`. Smoothing uses `1 - exp(-k*dt)`, never a fixed per-frame lerp factor. Clamp `dt` after hitches.

**2. Separate intent from physics.** Input becomes desired velocity; acceleration limits move velocity toward it; collisions resolve afterwards. Tune feel on accel, decel, gravity, coyote time and buffering, not on raw speed alone.

**3. Derive, do not guess.** From desired jump height `H` and apex time `T`: `g = 2H/T^2`, `v0 = 2H/T`. From an idle cost curve: closed-form geometric sums. Derived numbers survive tuning changes.

**4. Pick the cheapest algorithm that meets the budget.** BFS for unweighted maps and distance fields; A* for point-to-point; flow fields for crowds. Measure before adding JPS or hierarchy.

**5. Randomness is a design surface.** Pick the distribution on purpose: independent draws for surprise, bags for variety, pseudo-random distribution for proc rates, hard pity for guarantees. Store RNG state; use separate streams per concern.

**6. Perceived fairness beats mathematical fairness.** Players distrust streaks, discount stated odds and weigh losses heavily. Prefer input-side randomness, give mitigation, show odds, never skew against paying players.

**7. Atomic transactions.** Spending, crafting and claiming validate all costs first, mutate once, and are idempotent. Half-applied states are the root of duplication bugs.

**8. Time is data.** Timers use absolute timestamps for offline progress and tick counters for sim time. Clocks can be edited, so value-bearing time comes from a server.

## Decision procedures

### Implement a mechanic from a design card

1. Restate the verb, rule, parameters and feedback from the card (see `mechanics-codex`).
2. Write the rule as a pure function with data in and data out; list its tuning parameters and put them in data.
3. Pick the matching recipe in `references/systems-cookbook.md` or formulas in `references/math-and-movement.md`.
4. Add the action and events to the core; write three tests: a normal case, an edge case, a failure case.
5. Add a bot or playthrough step; run it with several seeds.
6. Hand the events to presentation for juice (`game-feel`).

### Choose a pathfinding approach

| Question | Answer |
|---|---|
| One agent, one target, moderate map | A* with `max_nodes` cap |
| Many agents, same target | Flow field |
| Need distances or reachable set | BFS or Dijkstra distance map |
| Big open uniform grid, many queries | JPS after profiling A* |
| Puzzle state search | BFS or A* over states (`puzzle_solver.py`) |
| 3D free movement | Engine navmesh |

Always: fixed neighbour order, ties by index, path cache keyed by map version, time budget per frame, partial path when unreachable.

### Make a random system feel fair

1. State the player experience: surprise, variety, reliability or guarantee.
2. Map to a tool: surprise (plain), variety (bag), reliability (PRD), guarantee (hard pity).
3. Put counters and bag contents in saved core state; give each concern its own stream.
4. Simulate a million draws; check average rate, longest drought, longest streak.
5. For paid randomness, run `gacha_calc.py`, disclose odds and pity, and have `compliance-officer` review.

### Debug a movement or physics bug

1. Reproduce with a fixed seed and a recorded input list.
2. Check frame-rate dependence: run the sim at 30 and 120 Hz and compare.
3. Check units and coordinate conventions (y-up versus y-down; radians versus degrees).
4. Check order of operations: input, velocity, gravity, collision, then state flags (`is_on_floor` read after move).
5. Check tunnelling (`v*dt` versus thickness) and corner snagging (resolve axes separately).
6. Add a regression test with the captured input list.

### Build an idle or offline progress loop

1. Choose number representation (double, mantissa and exponent, big integer).
2. Cost curve `base * growth^n`; "buy max" via closed form.
3. Offline: `elapsed = clamp(now - last_seen, 0, cap)`; closed form or coarse steps; one summary event.
4. Server time for anything valuable; clamp backwards clock jumps.
5. Test online versus offline equivalence within the efficiency factor.

## Mobile specifics

- Touch input replaces buttons: dynamic-origin virtual sticks, dead zones near 10 to 15 percent, drag with an offset above the finger, generous hit areas, and input buffering (see `mobile-ux`).
- Frame budget is shared with rendering and thermals: prefer 30 Hz sims for slow games, cap search per frame, stagger AI and path requests.
- Avoid per-frame allocations in movement, collision and pathfinding code; reuse arrays and stamp-reset scratch buffers.
- Safe areas and aspect ratios change layout and camera fit; recompute on rotation and resize.
- Interruptions and background kills: save timers as timestamps, regenerate energy lazily, handle resume with a clamp.
- Low-end devices: replace per-pixel or N-squared checks with grids; avoid heavy float transcendental calls in hot loops.
- Battery: avoid continuous polling; sleep sims when nothing can change.

## Anti-patterns

| Anti-pattern | Detect | Fix |
|---|---|---|
| `lerp(x, target, 0.1)` per frame | Smoothness differs between 30 and 60 fps | Exponential decay with `dt` |
| Random in rule code from global RNG | Replays diverge | Seeded RNG in state |
| Shuffle with `j` in `[0, n)` each step | Biased permutations | Fisher-Yates with `j` in `[0, i]` |
| Pathfind every frame per agent | Profiler spikes | Cache, throttle, flow field |
| Sorting a full open list each step | A* slow on large maps | Binary heap |
| Rewards from device clock | Players change time | Server time, clamp |
| Spending without pre-check | Negative balances, dupes | Validate all, then mutate |
| Float equality | Flaky tests and logic | Epsilon, integers |
| Hidden odds manipulation | Complaints, regulatory risk | Disclose and consistent rules |
| One huge update loop | Cannot test pieces | Pure functions per rule |
| Unwinnable random boards | Churn spikes | Solvability check or fair supply |
| Pixel-based tuning | Breaks on other resolutions | World units or tiles |

## Using the ontology

- Core verbs from the ontology become actions; mechanics become pure rule functions with named parameters; dynamics are what bots and simulations measure.
- Resource flows (sources, sinks, converters) become inventory, crafting and timer code here; model them first with `economy_sim.py`.
- Content units (levels, recipes, quests, waves) are data validated against schemas with `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_json.py`.
- Level solvers and simulators: `puzzle_solver.py --level PATH --algo bfs|astar`, `match3_sim.py --level PATH --bot greedy|random|cascade`, `gacha_calc.py` for pity maths, `pcg.py` for generators.
- Difficulty evidence feeds `difficulty_curve.py analyze` and the playtest bots from the engine template.
- Fairness findings go in the design contract's risk list for the `critic` to challenge.

## Reference library

| File | What it contains | When to read it |
|---|---|---|
| `references/math-and-movement.md` | Vectors, smoothing, easing, springs, Bezier, square and hex grids, collision primitives, kinematic controllers, jump arc derivation, cameras, aiming, numerical hygiene, formula sheet | Implementing movement, camera, feel or grid logic; debugging scale, sign or frame-rate issues |
| `references/systems-cookbook.md` | Inventory, crafting, quests, achievements, timers and energy, spawners and waves, match-3 logic, merge boards, idle big numbers and offline progress, block placement, runner chunks, testing | Building a concrete game system in GDScript or C# |
| `references/pathfinding-and-rng.md` | Search algorithm chooser, BFS, Dijkstra, A*, JPS, flow fields, practical rules; PRNG choice, seeding and streams, shuffle bags, pseudo-random distribution, alias tables, fairness perception, verification | Choosing a search or randomness approach; making randomness fair and testable |

## Related skills

- `game-architecture` — the sim-core structure, patterns and AI that host this code.
- `mechanics-codex` — the mechanic cards these recipes implement.
- `game-feel` — juice and feedback layered on the events these systems emit.
- `economy-design` — currency, price and drop-rate design behind inventory and pity.
- `progression-difficulty` — curves and win-rate targets for waves, levels and idle growth.
- `level-design` — level structure that solvers and chunk generators serve.
- `procedural-generation` — generators and fairness checks for random content.
- `mobile-ux` — touch input, hit areas and layout.
- `mobile-performance` — profiling and budgets for hot gameplay code.
- `qa-testing` — bots, deterministic playthroughs and fairness verification.
- `legal-ethics` — paid randomness disclosure and odds rules.
- `engine-godot` / `engine-unity` — engine APIs for character bodies, tweens and input.
