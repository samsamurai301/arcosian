# Level checks with level_import.py

`level_import.py convert` turns a Tiled or LDtk file into one normalised JSON; `level_import.py check` then asks structural questions the core level audit cannot: can the player reach every exit, are pickups and enemies reachable, where are the dead ends and softlock traps, how long is the shortest route and how are entities spread along it. This file explains the data format, the movement models and their limits, how to read the report, starting thresholds for top-down, platformer and puzzle levels, and where the results go in the core level audit and the five-gate playthrough evidence.

## Contents

1. Pipeline
2. The normalised file
3. What `check` measures
4. Movement models and their limits
5. Reading the report
6. Thresholds by genre
7. Choosing jump parameters
8. Feeding the core audit
9. Feeding the gates
10. CI recipe
11. Limits and false results
12. Worked numbers

## 1. Pipeline

```
editor file (.tmj .tmx .ldtk)
   |  level_import.py convert --out build/l1.json [--audit-out .gamestudio/levels/w1_l001.level.json]
   v
level.json (arcosian-level/1)         level-spec (grid layout)
   |  level_import.py check                |  level_audit.py audit --dir .gamestudio/levels
   v                                       v
report.json (verdict, findings)        set-level findings (mechanic order, difficulty, ...)
```

`convert` and `check` are separate on purpose. `convert` depends on the editor conventions (layer names, tags, roles). `check` depends only on the normalised file, so a level built any other way (a procedural generator, a hand-written grid) can be checked by writing the same JSON.

Exit codes: 0 pass or warnings, 1 check failed (an error finding, or any warning with `--strict`), 2 usage or input error (missing file, unsupported format, a layer name that does not exist).

## 2. The normalised file

Format name `arcosian-level/1`. Keys:

| Key | Content |
|---|---|
| `name`, `source` | Level name; `file`, `editor` (`tiled` or `ldtk`), `editor_version`, `level` |
| `grid` | `width`, `height` in tiles |
| `tile_size` | `[w, h]` in pixels |
| `origin` | `[x, y]` tile offset removed from an infinite Tiled map (else `[0, 0]`) |
| `layers` | One entry per layer: `name`, `kind` (`tiles`, `intgrid`, `objects`, `entities`), size, `tile_count`, `visible`, and `data` (flat, row-major, unless `--omit-layer-data`). Tiled tile data holds GIDs with flip flags removed; LDtk tile layers hold tile id + 1 (0 is empty); LDtk IntGrid holds the raw values |
| `solid` | `rows`: one string per row, `#` solid, `.` walkable; `source`: how it was derived |
| `entities` | `type`, `name`, `role`, `x`, `y`, `w`, `h` (tiles, top-left), `cell` (the centre's cell), `layer`, `properties`, `tags` (LDtk) |
| `metadata` | Map or level properties and editor details |
| `warnings` | Things `convert` could not do |

Roles: `spawn`, `exit`, `enemy`, `pickup`, `hazard`, `other`.

### How `solid` is chosen

Order of precedence in `convert`:

1. `--solid-layer NAME` (repeatable). Tiled: a tile layer (any non-empty tile is solid) or an object layer (rectangles, ellipses and polygons are rasterised onto cell centres; rotation is ignored with a warning). LDtk: an IntGrid layer (cells whose value is in `--solid-values`) or a Tiles or AutoLayer layer (any tile).
2. `--solid-property KEY`. Tiled: a boolean-like tile property in the tileset. LDtk: a tile enum tag.
3. Automatic: a layer named `collision`, `collisions`, `solid`, `solids`, `wall`, `walls`, `ground`, `blocking`, `blocked`, `collider` or `colliders`, or a Tiled layer property `solid` or `collision` set true; for Tiled then a tile property named `solid`, `collision`, `collides`, `blocked` or `blocks`; for LDtk the only IntGrid layer, if there is exactly one.
4. Nothing found: everything is walkable and `warnings` says so. Do not trust `check` on such a file.

`--solid-values` takes numbers or IntGrid value names (`1,wall`). With no option, LDtk values named `wall`, `solid`, `ground`, `block`, `blocked` or `collision` are solid, else value 1.

Anything the script reads as solid is solid for every check. One-way platforms, ladders, doors and water are not separate. Mark them walkable or solid on purpose (section 11).

## 3. What `check` measures

| Measure | Definition |
|---|---|
| Reachability | Cells the player can occupy, found by graph search from the first spawn (cost-ordered, so distances are shortest routes) |
| Exit reachability | An exit is reachable when any cell it covers is reachable. An exit sitting in a solid cell (a door tile) counts if a neighbour cell is reachable |
| Pickups, enemies | Same rule per entity. Unreachable ones are listed with their cells |
| Path length | Shortest route from the spawn to the nearest reachable exit, in tiles (Manhattan displacement along the route; top-down diagonals count 1.414) |
| Dead ends | Reachable cells with exactly one way in or out, that hold no entity and are not the spawn. Top-down: cells with one walkable neighbour. Platformer: standing cells with one connection to the rest |
| Traps (platformer) | Reachable standing cells from which no exit can be reached (a pit you can fall into but not leave). A softlock if the game does not respawn the player |
| Pacing | Entities of role enemy, pickup and hazard assigned to the shortest route: those within a radius (screen width / 4, at least 2 tiles) of the route count as "on route". Per-screen density; fullest and emptiest screen-wide window; longest stretch of route with none |
| Verdict | `fail` if any error finding; `warn` if only warnings; else `pass` |

Findings and severities:

| Code | Severity | Meaning |
|---|---|---|
| `no_spawn` | error | No entity with role spawn |
| `spawn_in_solid`, `spawn_out_of_bounds`, `spawn_falls` | error | The start is invalid |
| `exit_unreachable` | error | An exit cannot be reached. Exit code 1 |
| `no_exit` | warning | No exit entity; the level may end another way (a boss, a timer) |
| `pickup_unreachable` | warning (error with `--strict`) | A pickup cannot be reached |
| `enemy_unreachable` | warning | An enemy sits where the player cannot go. Fine for ranged or flying enemies; check each |
| `entity_in_solid`, `entity_out_of_bounds` | warning | Entity placed inside a wall, or outside the grid |
| `dead_ends` | warning | More dead ends than the preset allows |
| `softlock_traps` | warning | Trap cells exist (platformer) |
| `path_short` | warning | Route shorter than the minimum (spawn next to exit, or a test level) |
| `pacing_sparse`, `pacing_dense`, `empty_stretch` | warning | Entity density or gaps outside the preset |
| `multiple_spawns` | warning | Only the first spawn is checked |
| `search_truncated` | warning | `--max-nodes` reached; the result is partial |
| `jump_assumed` | info | Jump values were defaults |

## 4. Movement models and their limits

### Top-down (`--mode topdown`)

A body that moves between 4-neighbour walkable cells; `--diagonal` adds diagonal steps without cutting corners. A one-cell body is assumed. If your character is wider than one tile, widen corridors in the check by dilating the solid layer in the editor, or accept that narrow gaps read as passable.

### Platformer (`--mode platformer`)

A body of one cell tall and wide. Gravity is derived from the jump you give it, using units where a full jump lasts one time unit:

```
g  = 8 x H                    H = max jump height in tiles
v0 = 4 x sqrt(H x h)          launch speed for a jump of height h (h up to H)
vx = D x s                    D = flat jump distance in tiles; s in {1, 0.5}
```

A full jump at full speed rises H tiles (with a 1% margin, so a jump of N clears an N-tile ledge) and lands D tiles away on flat ground. The search tries, from each standing cell: walking left or right; stepping off an edge (falls with horizontal speed `D x s`); jumps straight up; jumps left and right at several heights (1, 2, up to H) and both speeds. Each trial is integrated in small steps (at most 0.3 tile per step). The body may hold a direction against a wall, so it can slide up and over a ledge. Side walls of the level stop it. Falling out of the bottom of the grid is death and not a route. Top of the grid is open air.

What it catches: gaps wider than the jump, ledges higher than the jump, rooms sealed by walls or pits, pits with no way out, and pickups that are out of reach.

What it does not model: double jumps, dashes, wall jumps, ladders, moving platforms, one-way platforms, springs, ice, doors and keys, enemies, a body taller than one tile, coyote time and jump buffering, and variable run speed beyond the two values. Those features change reachability. Work around them in the data (see section 11), or run the check with more generous parameters to model an upgraded character, as a separate "with double jump" pass.

The model is an approximation. Use it to find levels that are surely broken, and treat levels that pass as "not obviously broken", not as proof. The bot run in the playthrough gate is the test of record (section 9).

### Puzzle (`--preset puzzle`)

Uses the top-down model with pacing off and a high dead-end tolerance. For grid puzzles with rules (sliding, Sokoban, sort) use the core solvers instead (`puzzle_solver.py`), which understand the rules. This preset is for maze-like or room-connection puzzles where only connectivity matters.

## 5. Reading the report

Top-level keys of the JSON report:

| Key | Content |
|---|---|
| `mode`, `preset`, `jump` | What was run; `jump.assumed` is true if you did not pass both values |
| `thresholds` | The values in force (starting values; see section 6) |
| `spawn` | Cell of the spawn |
| `reachability` | Top-down: `walkable_cells`, `reachable_cells`, `reachable_fraction`. Platformer: `standable_cells`, `reachable_standable`, `touchable_cells` |
| `exits` | Per exit: `cell`, `reachable`, `distance_tiles` |
| `pickups`, `enemies` | `total` and the `unreachable` list |
| `path` | `nearest_exit_tiles`, `nodes` |
| `dead_ends`, `traps` | Counts and up to 20 example cells |
| `pacing` | `route_tiles`, `entities_on_route`, `entities_off_route`, `per_screen`, `emptiest_screen`, `fullest_screen`, `longest_empty_stretch_tiles` |
| `findings`, `verdict`, `fail` | The list, the verdict, and whether the exit code is 1 |

Read in this order:

1. `verdict` and `findings`. Fix every error first.
2. `reachability`. A low reachable fraction on a level that should be open means a wall in the wrong place or a missing collision layer. Compare `solid.source` in `level.json`.
3. `exits`, then `pickups` and `enemies`. The cells tell you which spot to open in the editor.
4. `path` and `pacing` against the design intent: a 45-tile route with 6 things on it is about 2.7 per screen at 20-tile screens.
5. `dead_ends` and `traps`: decide whether each is an intended secret, a reward nook or a mistake.

Entities that are off the route are not wrong: optional areas should have pickups. The `entities_off_route` count is information.

## 6. Thresholds by genre

These are starting values and estimates, not measured limits. They are the preset defaults, and each can be overridden with a flag. Tune per game with playtest data.

| Setting | Flag | Top-down | Platformer | Puzzle |
|---|---|---|---|---|
| Screen width (tiles) | `--screen-tiles` | 20 | 20 | n/a |
| Entities per screen, minimum | `--min-per-screen` | 0.5 | 1.0 | off |
| Entities per screen, maximum | `--max-per-screen` | 6 | 8 | off |
| Longest empty stretch (screens) | `--max-empty-screens` | 1.5 | 1.0 | off |
| Dead ends, share of reachable cells | `--max-dead-end-ratio` | 0.10 | 0.05 | 1.0 (off) |
| Shortest route (tiles) | `--min-path-tiles` | 10 | 10 | 4 |
| Pickups unreachable | n/a | warn | warn | warn |
| Traps allowed | n/a | n/a | 0 (warn) | n/a |

Why these shapes:

- **Top-down:** rooms and corridors have dead ends and rest areas, so the density band is wide and empty stretches may be longer. A top-down shooter or dungeon crawler tolerates more empty route than a platformer because movement itself is the activity.
- **Platformer:** the route is mostly traversal, so the player should meet something to jump, avoid or collect often. Under about one thing per screen reads as empty; over eight is crowded at typical enemy sizes. Empty stretches beyond about one screen are where players stop feeling pace.
- **Puzzle:** connectivity only. Pacing does not apply, and dead ends are part of the design.

Screen width in tiles is the viewport width in pixels divided by the tile size, in the game's own units: 320 / 16 = 20; 480 / 16 = 30; 1280 / 32 = 40. For vertical scrollers, use the viewport height instead and read "per screen" as per screen-height of route. A mobile portrait game that shows 12 tiles across and 20 tiles up uses `--screen-tiles 20` for a vertical route.

Match presets to design targets from the core skill: gaps and ledges on easy levels should stay at or under 60 to 80 percent of the player's maximum jump (`action-level-design.md`, gap and height tables). The check passes a gap at 100 percent of capability; the design rule is stricter. Run the check at your real capability, then run it again at 80 percent (for example `--jump-height 2.4 --jump-distance 4`) on easy levels: an easy level that fails at 80 percent has gaps or ledges that are too demanding for its tier.

## 7. Choosing jump parameters

Derive them from the controller, in tiles:

```
H  = v_jump^2 / (2 x g)                  jump height (tiles)
t  = 2 x v_jump / g                      air time (s), flat ground
D  = v_run x t                           flat jump distance (tiles)
```

The core skill's worked example: jump height 3 tiles, time to apex 0.42 s, run speed 6 tiles/s gives gravity about 34 tiles/s^2, launch speed about 14.3 tiles/s and a flat distance of about 5 tiles. Pass `--jump-height 3 --jump-distance 5`.

If the controller has stronger gravity on the way down, the real distance is shorter than the formula: recompute D from the actual descent. If you give the check a larger D than the game provides, it will pass gaps players cannot cross. When in doubt, use a smaller D.

If the game has a double jump or a dash, run twice: once for the base kit (to see where a player without upgrades is blocked, which is wanted in a gated area) and once with the combined reach.

## 8. Feeding the core audit

`convert --audit-out` writes a level-spec for `level_audit.py`:

| level-spec field | Source |
|---|---|
| `schema_version`, `$schema_name`, `level_id` | Constants; `--level-id` or the level name, sanitised to the id pattern |
| `layout` | `{"type": "grid", "rows": [...], "legend": {...}}` with `#` wall, `.` floor, `P` spawn, `E` exit, `e` enemy, `^` hazard, `$` pickup. Where two entities share a cell the higher priority wins (spawn, exit, enemy, hazard, pickup) |
| `goals` | `[{"type": "reach", "target": "exit", "count": 1}]` when an exit exists |
| `obstacles` | Hazard entities as `{"type": "hazard", "cells": [[x, y], ...]}` |
| `mechanic_refs` | Map or level property `mechanics` (comma-separated ids) |
| `moves_or_time_limit` | Properties `moves` (integer) and `time_sec` or `time_limit` (seconds) |
| `teach` | Property `teach` if one of teach, test, twist, reward |
| `difficulty_target` | Property `target_win_rate` (or `win_rate`) between 0 and 1 |
| `notes`, `source` | Import note and the source file name |

Fields it cannot derive, and which it reports in `audit_not_derivable`: `mechanic_refs` (the contract's mechanic ids are a design decision), `solver` (nothing has solved the level), `difficulty_target` (unless a property exists), `moves_or_time_limit`, `obstacles` (if there are no hazards), and `teach`. Tile art, other layers and entity properties are not carried over.

If the output file already exists, `convert` keeps its `solver`, `difficulty_target`, `teach`, limit, `mechanic_refs` and hand-written `notes` and reports them in `audit_preserved`. This follows the core adapter rule: merge, do not overwrite. Use `--overwrite-audit` to start fresh.

Then run the core audit on the directory:

```
python3 level_audit.py audit --dir .gamestudio/levels --strict
```

`level_audit.py` lives in the core plugin, under `skills/level-design/scripts/`; use the path your core `level-design` skill gives. The audit checks the set: one new mechanic per level, teach-test-twist order, difficulty sequence and duplicate layouts. `level_import.py check` checks one level's geometry. A level can pass one and fail the other.

The audit does not understand the platformer or top-down layout (it solves puzzle types only), so a grid layout from `convert` gets no `unverified` warning: only the fields above are checked. Write the check's verdict into `notes` or into the evidence folder instead, and keep the report file next to the level.

## 9. Feeding the gates

Level work passes the five gates like any feature (core skill `level-design`, section on the five gates):

| Gate | What this tool adds |
|---|---|
| `static` | Save `check` reports for every level (exit code 0) and the audit log under `.gamestudio/evidence/F0xx/static.log` |
| `unit` | A parity test that the engine's imported collision equals `solid.rows` (see `engine-import.md`); the script's `--selftest` |
| `playthrough` | The reachability result is a pre-screen, not evidence. The gate needs bot runs through the real build: win rates and zero softlocks. If `check` reports traps, the bot run must visit those cells or the game must respawn |
| `visual` | Screenshots of imported levels; the check says nothing about visuals |
| `perf` | Tile and entity counts from `layers[].tile_count` identify the heaviest level to profile |

Use the check to avoid wasting bot runs: a level whose exit is unreachable cannot win a playthrough, so fix it before the run. Use the bot run to catch what the model cannot: enemy blocking, timing, controls that differ from the assumed jump.

## 10. CI recipe

```
for f in levels/*.tmj levels/*.ldtk; do
  id=$(basename "${f%.*}")
  python3 level_import.py convert "$f" --out "build/$id.json" \
      --audit-out ".gamestudio/levels/$id.level.json" || exit 2
  python3 level_import.py check "build/$id.json" --mode platformer \
      --jump-height 3 --jump-distance 5 --out ".gamestudio/reports/levels/$id.check.json" || fail=1
done
python3 level_audit.py audit --dir .gamestudio/levels --strict
exit ${fail:-0}
```

For LDtk projects with many levels, pass `--level NAME` per level; `convert` refuses to guess. Keep the editor binaries out of CI: both tools read files directly. For Tiled maps in zstd, or maps that use unresolved templates or classes, run the Tiled export first (see `tiled.md`).

## 11. Limits and false results

| Situation | Effect | What to do |
|---|---|---|
| One-way platforms marked solid | Player appears unable to jump up through them | Do not mark them solid in the collision source; they then read as air, so the check lets the player pass through them and may over-report reach |
| Ladders and climbables | Not modelled; regions look unreachable | Treat the ladder cells as walkable and put a standing platform at the top and bottom for the check, or raise `--jump-height` for a ladder-only run |
| Doors, keys, switches | Locked doors read as walls or air | Convert the level twice: once with doors solid, once open; require that open passes and note the keys |
| Moving platforms, springs | Not modelled | Mark their travel cells as walkable in a copy used for the check |
| Wide or tall body | Narrow gaps and low ceilings pass | Use a smaller tolerance: dilate walls in the editor copy |
| Entity positions in mid-air | A pickup floating above a platform counts as reachable if the jump trajectory crosses its cell | Intended; pickups need only to be touched |
| Large platformer maps | The search grows with standing cells | Use `--max-nodes`; split the level; time is usually below a second for maps of a few thousand cells |
| Hazards | Not modelled as danger; spikes are walkable if they are not solid | Mark hazard tiles solid in a check copy if you want to treat them as walls |
| Multi-floor top-down maps with stairs | Two floors read as two disconnected areas | Check each floor, or connect them with a stair entity treated as walkable |
| Infinite Tiled maps | Bounding box only; large empty margins stay walkable | Use a collision layer with borders |

A level that fails the check may still be fine in the game, if the game has a mechanic the model lacks. A level that passes may still be broken, if the game has a rule the model lacks. Record known exceptions in the level's `notes` so the next reader of the report knows.

## 12. Worked numbers

A 40 by 15 platformer (tiles 16 px) with a spawn at (1, 13), an exit at (38, 13), three enemies and four coins, one of which sits on a 6-tile platform at row 4. Run with `--jump-height 3 --jump-distance 5`:

```
reachability   standable 54, reachable 48, touchable 309
exit           reachable, 45 tiles
pickups        1 of 4 unreachable (32, 3)
enemies        3 of 3 reachable
traps          0       dead ends 0
pacing         route 45 tiles, 6 entities on route, 1 off route
               2.67 per screen (20-tile screens), emptiest screen 2, fullest 4
               longest empty stretch 17 tiles
verdict        warn (exit code 0)
```

Reading it: the level is completable. The coin at (32, 3) needs a rise of about 5 tiles, above the 3-tile jump; it is either a secret that needs an upgrade (note it in the level's `notes`) or a mistake (add a stepping platform). The route has 2.67 things per screen, inside the platformer band of 1 to 8, and the longest empty stretch, 17 tiles, is under one screen (20 tiles). A second run with `--jump-height 2.4 --jump-distance 4` (80 percent of capability) fails: the exit becomes unreachable, because the 4-tile pit needs a jump of about 5 tiles to clear. So the level is fine for a normal tier but too demanding for an easy one; shrink the pit to 3 tiles if it is meant for early levels.
