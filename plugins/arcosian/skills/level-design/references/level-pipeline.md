# Level Pipeline: Specs, Editors, Solvers and Metrics

The machinery that turns level ideas into verified, shippable, measurable content: the `level-spec.schema.json` format field by field with an example for every layout type; file conventions; editors and data formats and how to adapt them to level-spec; the solver and simulation gates; how to drive `puzzle_solver.py`, `match3_sim.py`, `pcg.py` and this skill's `level_audit.py`; batch validation and CI; the playtest and live metrics that close the loop; how level work maps onto the five gates; and a step-by-step agent workflow. Design craft is in `principles.md` and the genre files; this file is about making that craft repeatable at volume.

## Contents

1. Pipeline overview
2. The level-spec format, field by field
3. Layout examples for every type
4. File and id conventions
5. Editors and data formats
6. The gates a level must pass
7. puzzle_solver.py
8. match3_sim.py
9. pcg.py
10. level_audit.py (this skill)
11. Batch validation and CI
12. Playtest and live metrics
13. Level work and the five gates
14. Live content operations
15. Agent workflow: producing a verified level set
16. Volatile facts

---

## 1. Pipeline overview

```
brief ──► design / generate ──► level-spec JSON ──► schema gate ──► solver / sim gate ──► set audit
  ▲                                                                                          │
  │                                                                                          ▼
recalibrate ◄── telemetry ◄── ship (remote-tunable) ◄── taste sign-off ◄── engine check ◄── playtest
```

Principles:
- **One canonical format.** Level-spec JSON in `.gamestudio/levels/` is the source of truth. Editors export to it; the engine and every tool read it (directly or through a build step). Never maintain two hand-edited copies.
- **Generate, then verify.** No level, handmade or generated, enters the set without a machine verdict from a solver or a bot. Hard levels get the most verification.
- **Deterministic by seed.** Generators, bots and the game's own RNG take seeds so any result can be reproduced.
- **Measure in production.** Bot predictions are hypotheses; live metrics are the verdict. Recalibrate bots against players regularly.

## 2. The level-spec format, field by field

Schema: `${CLAUDE_PLUGIN_ROOT}/scripts/schemas/level-spec.schema.json`. Example: `${CLAUDE_PLUGIN_ROOT}/scripts/schemas/examples/example.level-spec.json`. Only `schema_version` and `level_id` are required; extra properties are allowed at the top level and in `solver` and `difficulty_target`.

| Field | Type | Meaning and rules |
|---|---|---|
| `schema_version` | `"1.0"` | Always present |
| `level_id` | id string | Stable id such as `w1_l012` or `bonus_005`; also the `level_id` analytics parameter. Never reuse an id for a different level |
| `mechanic_refs` | list of ids | Contract mechanic ids used. A level should introduce at most one mechanic new to the player |
| `layout` | array or object | A bare grid (array of rows, strings or arrays) or a typed object with `type` in `grid`, `sliding`, `sokoban`, `sort`, `lights_out`, `match3`, `generator`, `custom` |
| `goals` | list | Strings or objects `{type, target, count}`; all must be met unless `notes` say otherwise. Common types: `sort_all`, `collect`, `clear`, `survive_waves`, `reach`, `score` |
| `moves_or_time_limit` | integer, object or null | Integer move limit, or `{"moves": n}` and/or `{"time_sec": s}`, or `null` for unlimited |
| `obstacles` | list | Codes or objects such as `{"type": "ice", "cells": [[2,3]], "hp": 2}` |
| `difficulty_target` | object | `win_rate` (designed first-try win rate of an average player, 0–1), `attempts_p50` (≥ 1); extras allowed: `bot_win_rate` (the same target converted into bot space by the bot-to-human calibration, section 12), `duration_sec` |
| `solver` | object | Written from tool output: `solvable` (bool or null), `min_moves` (int or null), `bot_win_rate` (0–1 or null), `runs` (int or null); extras allowed (`algo`, `states_visited`, `bot`, `seed`) |
| `teach` | enum | `teach`, `test`, `twist` or `reward` (`principles.md` section 2) |
| `notes` | string | Design intent, intended solution or path, known issues, live-change log |

Rules the schema cannot express (checked by `level_audit.py` and review):
- `solver` fields stay `null` until a tool has run; never type numbers in by hand.
- `moves_or_time_limit.moves` must be ≥ `solver.min_moves` for deterministic puzzles.
- `solver.bot_win_rate` should sit within a tolerance of the bot-space target: `difficulty_target.bot_win_rate` when present, else `difficulty_target.win_rate` (which assumes the bot plays like an average player).
- `runs` should be large enough for the tolerance (500+ for ±5 points; `casual-level-production.md` section 9).

## 3. Layout examples for every type

Every example below validates against the schema. Wrap each `layout` in a full document with `schema_version` and `level_id`.

**`sort`** (water, ball, nut sort; tubes listed bottom to top)
```json
{"type": "sort", "capacity": 4, "pour": "max", "colors": ["r", "g", "b"],
 "tubes": [["r","g","b","r"], ["g","b","r","g"], ["b","r","g","b"], [], []]}
```

**`sokoban`** (XSB notation: `#` wall, `@` player, `+` player on goal, `$` box, `*` box on goal, `.` goal, space/`-`/`_` floor; boxes = goals)
```json
{"type": "sokoban", "rows": ["#######", "#.@ $ #", "#  $  #", "# .   #", "#######"]}
```

**`sliding`** (0 is the blank; default goal is 1..N−1 in reading order with the blank last)
```json
{"type": "sliding", "grid": [[1, 2, 3], [4, 0, 6], [7, 5, 8]]}
```

**`lights_out`** (1 = lit; pressing toggles the cell and its orthogonal neighbours)
```json
{"type": "lights_out", "grid": [[0, 1, 0], [1, 1, 1], [0, 1, 0]]}
```

**`match3`** (`.` random tile, `#` hole, legend codes for blockers; `colors` = spawnable colour count)
```json
{"type": "match3", "colors": 5,
 "rows": ["#.......#", ".........", "..BB.BB..", ".........", "..IIIII..", ".........", "........."],
 "legend": {"B": "box (2 hp)", "I": "ice over random tile (1 hp)"}}
```

**`grid`** (generic tile grid with a legend: tower defense, board games, custom puzzles)
```json
{"type": "grid", "rows": ["S.....##", "#####.##", "##....##", "##.#####", "##....E#"],
 "legend": {"S": "spawn", "E": "exit", ".": "path", "#": "buildable"}}
```

**`generator`** (layout produced on demand; the seed makes it reproducible)
```json
{"type": "generator", "generator": "pcg.py cave", "seed": 1207, "params": {"w": 40, "h": 24}}
```

**`custom`** (anything else; tools that do not know the format skip it)
```json
{"type": "custom", "format": "runner_chunk_v1", "data": {"length_m": 40, "lanes": 3}}
```

A **bare grid** (array of row strings) is equivalent to `{"type": "grid", "grid": ...}` and is fine for quick prototypes; prefer the typed form so tools can dispatch on `type`.

## 4. File and id conventions

```
.gamestudio/levels/
├── order.json                 # ["w1_l001", "w1_l002", ...]  the shipping order (optional; else natural sort of ids)
├── legend.json                # shared cell codes for editor, sims and engine (casual games)
├── metrics.json               # capability metrics for action games (principles.md section 12)
├── elasticity.json            # measured lever effects (casual-level-production.md section 9)
├── w1_l001.level.json
├── w1_l002.level.json
└── ...
.gamestudio/reports/levels/    # solver and sim outputs, audit reports (not level files)
```

- File names end in `.level.json` so `validate_json.py --auto` and the post-write hook infer the schema.
- Ids: `w<world>_l<number>` with zero-padded numbers (`w1_l007`) so natural sort equals intended order; side content uses a prefix (`bonus_`, `event_<name>_`, `daily_`).
- **Ids are permanent.** A redesigned level in the same slot keeps its id only if analytics should treat it as the same level (record the change in `notes`); otherwise give it a new id and update `order.json`.
- Store tool outputs under `.gamestudio/reports/levels/`, not in `levels/`, so the levels directory contains only specs.
- Keep large worlds in subdirectories (`levels/w3/`) and point tools at the directory.

## 5. Editors and data formats

| Tool | Best for | Native format | Adapter to level-spec | Notes |
|---|---|---|---|---|
| Tiled | Tile maps, object layers, any 2D grid game | TMX (XML) and JSON | Read the tile layer into `rows` with a legend from tile ids; objects into `obstacles` | Mature, general-purpose, custom properties per tile and object |
| LDtk | 2D levels with typed entities and auto-tiling | JSON with a documented schema | Read IntGrid layers into `grid`; entities into `obstacles` or `data` | Strong typed-entity model; good for platformers and top-down |
| Ogmo Editor | Simple 2D levels | JSON | Same as above | Lightweight |
| PuzzleScript | Prototyping turn-based grid puzzles fast | Text rules and ASCII levels | Copy ASCII levels into `rows` (map the legend) | Excellent for finding the fun of a push or tile puzzle before engine work |
| Engine-native (Godot TileMapLayer, Unity Tilemap) | Final in-engine editing and visual polish | Engine scene or resource files | An editor script exports level-spec JSON | Never hand-write Unity scene YAML; generate via editor scripts (`engine-unity`) |
| Spreadsheet or CSV | Wave tables, encounter budgets, tuning sheets | CSV | A converter writes `waves` or `layout.data` | Designers tune numbers fastest in tables |
| Custom web editor | Casual grids (match-3, sort, screw) with live bot results | Level-spec JSON directly | None needed | A single HTML page can load, edit and save level-spec and call a local bot; agent-buildable |
| Text (direct JSON) | Agent-authored and generated levels | Level-spec JSON | None | Validate on every write (the hook does this) |

### Adapter rules
- Adapters are **one-way** (editor → level-spec) and deterministic. If designers must re-open levels in the editor, keep the editor file next to the spec and regenerate the spec from it; do not edit the spec by hand afterwards.
- Map editor tile ids to legend codes through `legend.json`; fail loudly on unknown ids.
- Preserve `solver`, `difficulty_target`, `teach` and `notes` when regenerating a spec from the editor (merge, do not overwrite).
- Put the editor source path in `notes` or an extra field such as `"source": "editor/w2_l014.tmj"`.

### Choosing
| Game | Recommended setup |
|---|---|
| Match-3, blast, sort, screw | Custom web editor or engine-native editor writing level-spec, plus `match3_sim.py` / `puzzle_solver.py` in the loop |
| Grid puzzle (Sokoban-like, rule puzzles) | PuzzleScript for prototyping, then text level-spec; solver in CI |
| Platformer, top-down action | LDtk or Tiled with an adapter; reachability checker |
| Runner | Chunks as level-spec `custom` files authored in engine or text; validator in CI |
| Survivor, tower defense | Spreadsheet wave tables plus generator or grid layouts |

## 6. The gates a level must pass

| Gate | Check | Tool | Pass condition | Blocking? |
|---|---|---|---|---|
| L1 Schema | Structure and types | `validate_json.py --auto` or `gs.py validate` | No errors | Yes |
| L2 Solvable | A solution exists within the limit | `puzzle_solver.py` (deterministic types); purpose-built solver; action validators | `solvable: true`; budget exhaustion = unknown, which blocks until resolved | Yes |
| L3 Limit sanity | Limit vs optimum | `level_audit.py` | `limit ≥ min_moves`; slack ratio inside the role's band | Error if impossible; warning if out of band |
| L4 Difficulty | Bot result vs target | `match3_sim.py`, solver bots, engine bots | `abs(bot_win_rate − target) ≤ tolerance` (after bot-to-human mapping) with enough runs | Yes for shipping |
| L5 Sequencing | Fits its neighbours | `level_audit.py` | ≤ 1 new mechanic; teach role on first appearance; relief after spikes; no long hard streaks | Errors block; warnings reviewed |
| L6 Uniqueness | Not a duplicate | `level_audit.py` (layout hash) | No duplicate layouts | Warning |
| L7 Readability | Mobile constraints | Review plus lint (columns ≤ 9 in portrait; colours ≤ 6) | Pass | Yes for shipping |
| L8 Engine | Loads and plays in the real game | Engine bot runner, screenshot capture | Loads without errors; bot result consistent with the Python sim | Yes for shipping |
| L9 Taste | Human sign-off per world | Human checkpoint | Approved | Yes (doctrine 10) |

## 7. puzzle_solver.py

CLI (binding, BLUEPRINT section 14):
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/puzzle_solver.py --level PATH [--algo bfs|astar] [--max-nodes N] [--json]
```

- Supports level-spec files whose `layout.type` is `sliding`, `sokoban`, `sort` or `lights_out`.
- `--algo bfs` finds a shortest solution and explores exhaustively up to the node budget; `--algo astar` uses a heuristic and typically scales further on sliding and Sokoban.
- `--max-nodes` caps the search. If the cap is hit, the honest result is "unknown", not "unsolvable"; raise the cap, switch to A*, or simplify the level.
- `--json` gives machine-readable output (solvability, shortest length, search statistics; check `--help` for exact field names). Copy the results into the `solver` block, or use `level_audit.py merge` (section 10).

Typical use:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/puzzle_solver.py --level .gamestudio/levels/w3_l007.level.json --algo bfs --max-nodes 500000 --json \
  > .gamestudio/reports/levels/w3_l007.solve.json
python3 ${CLAUDE_PLUGIN_ROOT}/skills/level-design/scripts/level_audit.py merge \
  --level .gamestudio/levels/w3_l007.level.json --result .gamestudio/reports/levels/w3_l007.solve.json
```

Interpreting for design (`puzzle-level-design.md` sections 6–8): `min_moves` sets the limit (slack bands); states visited is a rough complexity signal; a solution path lets you check that the intended key move is used.

## 8. match3_sim.py

CLI (binding):
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/match3_sim.py --level PATH [--runs N=500] [--bot greedy|random|cascade] [--seed S] [--json]
```

Input is a level-spec with `layout.type: match3`. Output gives the bot's win rate over the runs (plus whatever distribution data the script reports; check `--help`). Write the reference bot's results into `solver.bot_win_rate` and `solver.runs`, with the bot name and seed as extra fields. Recipes, sweeps and interpretation are in `casual-level-production.md` section 15.

## 9. pcg.py

CLI (binding):
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/pcg.py wfc|bsp|cave|noise|poisson|maze --w W --h H [--seed S] [--json] [--out PATH]
```

| Algorithm | Produces | Use for | Global guarantees? | Post-check |
|---|---|---|---|---|
| `wfc` (wave function collapse) | Grids that respect local tile-adjacency rules | Tilesets with local coherence: towns, decor, terrain transitions | No: connectivity and solvability are not guaranteed | Flood fill for connectivity; solver for puzzles; regenerate with a new seed on failure |
| `bsp` (binary space partition) | Rooms and corridors | Dungeons, roguelite floors, arenas linked by corridors | Connectivity by construction when corridors join sibling regions | Check room sizes against capability metrics |
| `cave` (cellular automata) | Organic caverns | Cave levels, survivor maps, natural arenas | No: can leave disconnected pockets | Keep the largest connected region or carve tunnels |
| `noise` | Continuous value fields | Terrain height, biome masks, resource density; threshold into holes for match-3 shapes | n/a | Threshold, then check reachability |
| `poisson` (Poisson-disc sampling) | Evenly spaced points with a minimum distance | Placing trees, pickups, spawn points, enemies without clumps | Spacing only | Check against paths and line of sight |
| `maze` | Perfect mazes (one route between any two cells) | Maze levels; corridor skeletons for other generators | Full connectivity, no loops | Add loops by removing a few walls if circulation is needed (`action-level-design.md` section 6) |

### Turning generator output into levels
1. Generate with a fixed seed: `pcg.py cave --w 40 --h 24 --seed 1207 --json --out .gamestudio/reports/levels/cave_1207.json`.
2. Post-process: keep the largest region, place start and goal at the farthest-apart reachable cells (two BFS passes), place pickups with `poisson`.
3. Store either the **result** (`layout.type: grid` with the produced rows, best for handcrafted curation) or the **recipe** (`layout.type: generator`, `generator: "pcg.py cave"`, `seed`, `params`, best for runtime generation; the engine must reproduce `pcg.py` exactly or use its own generator id).
4. Verify (reachability, solver or bot) and record results in `solver`.
5. Reject or repair failures; do not hand-patch a recipe-based level (the patch is lost on regeneration). Patch only stored results.

See `procedural-generation` for generator design in depth (grammars, constraint solving, seeds and runtime generation).

## 10. level_audit.py (this skill)

`${CLAUDE_PLUGIN_ROOT}/skills/level-design/scripts/level_audit.py` checks a **set** of levels in order: the things single-level tools cannot see. Stdlib only, Python 3.9+, `--json`, `--selftest`.

```bash
# audit a directory (order from order.json if present, else natural sort of level ids)
python3 ${CLAUDE_PLUGIN_ROOT}/skills/level-design/scripts/level_audit.py audit --dir .gamestudio/levels \
  [--order .gamestudio/levels/order.json] [--tolerance 0.10] [--min-runs 200] \
  [--hard-threshold 0.5] [--max-hard-streak 2] [--slack-min 1.1] [--slack-max 3.0] [--strict] [--json]

# geometric attempt odds for a per-attempt win rate
python3 ${CLAUDE_PLUGIN_ROOT}/skills/level-design/scripts/level_audit.py odds --win-rate 0.35 [--attempts 3] [--json]

# copy a solver / sim JSON result into a level's solver block
python3 ${CLAUDE_PLUGIN_ROOT}/skills/level-design/scripts/level_audit.py merge --level L.level.json --result R.json [--dry-run] [--json]
```

| Check | Severity | Rule |
|---|---|---|
| `parse` / `missing_id` / `duplicate_id` | error | Every file parses and has a unique `level_id` |
| `unsolvable` | error | `solver.solvable` is false |
| `unverified` | warning (error with `--strict`) | `solver.solvable` is null or missing on a puzzle layout, or no bot result on a match-3 layout |
| `limit_below_optimum` | error | Move limit < `solver.min_moves` |
| `slack_out_of_band` | warning | Limit / `min_moves` below `--slack-min` (any role) or above `--slack-max` (test and twist levels; teach and reward levels may be generous) |
| `bot_vs_target` | warning; error beyond 2× tolerance | `abs(solver.bot_win_rate − target) > tolerance`, where target is `difficulty_target.bot_win_rate` if set, else `difficulty_target.win_rate` |
| `few_runs` | warning | `solver.runs` < `--min-runs` |
| `multi_intro` | error | More than one mechanic first appears in the same level |
| `intro_not_teach` | warning | A first appearance in a level whose `teach` is not `teach` |
| `intro_on_spike` | warning | A first appearance in a level with target win rate below `--hard-threshold` |
| `twist_before_test` | warning | A `twist` level uses a mechanic that has had no `test` level yet |
| `hard_streak` | warning | More than `--max-hard-streak` consecutive hard levels |
| `no_relief` | warning | Neither of the 2 levels after a hard level is a reward or ≥ hard-threshold + 0.15 |
| `duplicate_layout` | warning | Two levels share a canonical layout hash |
| `attempts_inconsistent` | warning | `attempts_p50` differs by more than 2× from the geometric median implied by `win_rate` |

Exit codes: 0 no errors (warnings allowed), 1 errors found, 2 usage or input error.

## 11. Batch validation and CI

### Local batch
```bash
LEVELS=.gamestudio/levels
OUT=.gamestudio/reports/levels
mkdir -p "$OUT"

# L1 schema
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_json.py --auto "$LEVELS"

# L2/L4 solve or simulate each level by layout type
for f in "$LEVELS"/*.level.json; do
  id=$(basename "$f" .level.json)
  t=$(python3 -c 'import json,sys; l=json.load(open(sys.argv[1])).get("layout"); print(l.get("type") if isinstance(l, dict) else "grid")' "$f")
  case "$t" in
    sort|sokoban|sliding|lights_out)
      python3 ${CLAUDE_PLUGIN_ROOT}/scripts/puzzle_solver.py --level "$f" --algo bfs --max-nodes 500000 --json > "$OUT/$id.solve.json" ;;
    match3)
      python3 ${CLAUDE_PLUGIN_ROOT}/scripts/match3_sim.py --level "$f" --runs 500 --bot greedy --seed 1 --json > "$OUT/$id.sim.json" ;;
    *) continue ;;
  esac
  for r in "$OUT/$id".solve.json "$OUT/$id".sim.json; do
    [ -f "$r" ] && python3 ${CLAUDE_PLUGIN_ROOT}/skills/level-design/scripts/level_audit.py merge --level "$f" --result "$r"
  done
done

# L3/L5/L6 set audit
python3 ${CLAUDE_PLUGIN_ROOT}/skills/level-design/scripts/level_audit.py audit --dir "$LEVELS" --json > "$OUT/audit.json"
python3 ${CLAUDE_PLUGIN_ROOT}/skills/level-design/scripts/level_audit.py audit --dir "$LEVELS"
```

### Caching and speed
- Hash each level's `layout`, limits and goals; skip re-solving when the hash and tool version are unchanged (store the hash next to the result).
- Solving is embarrassingly parallel: use `xargs -P` or GNU parallel over files.
- Use fewer runs (100–200) while iterating, then the full count (500–1,000) before shipping.

### CI (GitHub Actions sketch)
```yaml
name: levels
on:
  pull_request:
    paths: [".gamestudio/levels/**"]
jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - name: Verify levels
        env: { GS: ./tools/arcosian }   # vendored copy or checkout of the plugin scripts
        run: |
          python3 $GS/scripts/validate_json.py --auto .gamestudio/levels
          python3 $GS/skills/level-design/scripts/level_audit.py audit --dir .gamestudio/levels --strict
```
Pin action versions to what your repository already uses; the snippet shows the shape, not required versions. Full CI templates live in `templates/ci/` (`store-release`, `qa-testing`).

## 12. Playtest and live metrics

### Event set for levels
Define these in the event taxonomy (`event-taxonomy.schema.json`, category `progression`; see `player-analytics`):

| Event | Key params |
|---|---|
| `level_start` | `level_id`, `attempt` (1-based per player per level), `boosters_pre` |
| `level_end` | `level_id`, `attempt`, `result` (`win`, `lose`, `quit`), `moves_used`, `moves_left`, `goal_remaining`, `duration_sec`, `boosters_used`, `continues` |
| `level_hint` | `level_id`, `attempt`, `hint_step` |
| `level_restart` | `level_id`, `attempt`, `moves_used` |

### Derived metrics
| Metric | Formula |
|---|---|
| First-try win rate | `count(level_end: win, attempt = 1) / count(level_start: attempt = 1)` |
| Per-attempt win rate | `wins / (wins + losses + quits)` (report quits separately as well) |
| Attempts to win p50 / p90 | Per player, the `attempt` of the first win; take percentiles over players who won |
| Level churn | Players whose last `level_start` (no activity for N days afterwards, e.g. 7) was this level, divided by players who started it |
| Pass-through | Players reaching L+1 within N days / players starting L |
| Near-miss loss share | Losses with `goal_remaining` ≤ 1 unit / losses |
| Assist share | Attempts with boosters, continues or hints / attempts |
| Duration p50 | Median `duration_sec` per attempt |

Export a per-level CSV with columns `level,attempts,wins,churned` and run:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/difficulty_curve.py analyze --data levels.csv --json
```
to spot spikes and churn outliers against the curve.

### Bot-to-human calibration
1. Join live first-try win rate with `solver.bot_win_rate` per level (≥ 30 levels; more is better).
2. Fit `logit(human) = a + b · logit(bot)` per bot type and mechanic family.
3. Convert design targets into bot targets with the inverse map and write them to each level's `difficulty_target.bot_win_rate`; store `a` and `b` with a date in the project (e.g. `.gamestudio/levels/calibration.json`).
4. Re-fit after major rule changes and at least monthly in live operation.

### Playtest protocol for levels
- Persona or human playtests: 5 players per round on 5–10 levels around a new mechanic; record traces (moves, time between moves, restarts).
- Look for: the intended insight moment, misreads (wrong taps on non-interactive elements), unintended solutions, and quits.
- Store results as playtest reports (`playtest-report.schema.json`) under `.gamestudio/playtests/`.

## 13. Level work and the five gates

A level-content feature (area `content` in `features.json`) passes the five gates like any other feature (BLUEPRINT section 6):

| Gate | Evidence for a level set |
|---|---|
| `static` | `validate_json.py --auto` log plus `level_audit.py audit --strict` log with no errors (`.gamestudio/evidence/F0xx/static.log`) |
| `unit` | Engine level-loader tests (every level in the set loads; goals and limits read correctly) and solver/sim tool selftests |
| `playthrough` | Bot runs over the set from the engine runner or Python sims, saved as a playtest report: win rates within tolerance, zero softlocks |
| `visual` | Screenshots of a sample of levels (every teach level plus every hard level) passing the visual rubric on the smallest supported screen |
| `perf` | Perf report for the heaviest level (most blockers, largest cascades, densest wave) on the low-tier device |

Commands: `gs.py evidence-dir F0xx`, then `gs.py feature gate F0xx static pass --evidence .gamestudio/evidence/F0xx/static.log`, and so on; `gs.py feature pass F0xx` once all gates pass.

## 14. Live content operations

- **Remote-tunable parameters:** move limits, goal counts, colour counts, spawn weights and wave multipliers, per level, with a version stamp. Changing them is a content change: log it in the level's `notes` and in `progress.md` (`gs.py progress "..."`).
- **Level replacement:** a replaced level that should be analysed separately gets a new id; keep the old spec file in an `archive/` folder for reproducibility.
- **Rollout:** ship difficulty changes to a percentage first, or as an A/B test (`casual-level-production.md` section 13).
- **Content drops:** new levels pass the full gate set before the build or remote bundle is cut; the drop's levels are audited together with the 10 levels before them so the curve stays continuous.
- **Regression check after client updates:** re-run the bot gate on a fixed sample of levels; a shift in bot win rate with unchanged level files means the game rules or the simulator changed.

## 15. Agent workflow: producing a verified level set

The `arcosian:level-designer` agent (or any agent loading this skill) follows this procedure for a request such as "make world 3: 20 levels introducing chains".

1. **Read the contract**: mechanics, `progression.difficulty`, `content.levels`, art and UX constraints (`gs.py status`, `.gamestudio/contract.json`).
2. **Plan the world**: list elements, write the role sequence and target curve (`difficulty_curve.py generate`), and a one-line brief per slot (`principles.md` section 1).
3. **Author or generate candidates**: archetypes and generators for casual games (`casual-level-production.md` section 11); design-backwards for puzzles (`puzzle-level-design.md` section 3); chunk and wave specs for action (`action-level-design.md`). Write `.level.json` files; the post-write hook validates the schema.
4. **Verify** with the batch in section 11 (solve or simulate, merge results).
5. **Slot and audit**: assign levels to slots, write `order.json`, run `level_audit.py audit`; fix errors, review warnings.
6. **Engine check**: load every level in the engine; run the engine bot runner on teach and hard levels; capture screenshots for the visual gate.
7. **Report**: a short report in `.gamestudio/reports/` with the curve, the audit summary, open warnings and the levels needing human taste review.
8. **Human checkpoint**: request sign-off on the world (taste, fun). Do not mark the content feature done until the gates pass (`gs.py feature gate ...`).
9. **After launch**: pull live metrics, recalibrate bots, flag problem levels, propose fixes as remote-config changes or A/B tests.

## 16. Volatile facts

As of Oct 2026 — verify before relying.

- Research on LLM-generated, difficulty-labelled Snake levels (validated with A* pathfinding) reported about 87% playability for easy levels and only about 36% for hard ones, which is why generated hard levels need the strictest verification. Source: [FedCSIS 2025, Annals of Computer Science and Information Systems vol. 43](https://annals-csis.org/Volume_43/drp/1909.html).
- Production evidence that bots can replace most human difficulty playtests for casual levels comes from King (Candy Crush); details and sources are in `casual-level-production.md` section 18. Source: [Gudmundsson et al., 2018 (King)](https://www.Gwern.net/doc/reinforcement-learning/imitation-learning/2018-gudmundsson.pdf).
- Epic describes Unreal Engine 5.7's PCG framework as production-ready; relevant only if a project uses Unreal (the studio's mobile default is Godot or Unity). Source: [Unreal Engine What's New](https://www.unrealengine.com/whats-new).
- Editors referenced in section 5 and their home pages (features and licences change; check before adopting): Tiled — [mapeditor.org](https://www.mapeditor.org/); LDtk — [ldtk.io](https://ldtk.io/); Ogmo Editor 3 — [ogmo-editor-3.github.io](https://ogmo-editor-3.github.io/); PuzzleScript — [puzzlescript.net](https://www.puzzlescript.net/); Godot's `TileMapLayer` node (which replaced the older single `TileMap` node in the Godot 4.3 era) — [Godot docs](https://docs.godotengine.org/en/stable/classes/class_tilemaplayer.html); Unity Tilemap — [Unity Manual](https://docs.unity3d.com/Manual/class-Tilemap.html).
