---
name: level-editors
description: Tiled and LDtk level editing for arcosian games - editor choice, file conventions, command-line export, Godot 4 and Unity import, and level_import.py, which converts maps to one JSON, writes a level-spec for the core audit, and checks reachability, dead ends and pacing. Use for "set up Tiled or LDtk", "import this map into Godot or Unity", "can the player reach the exit", "check this level".
when_to_use: Building, converting, importing or automatically checking tile-based levels made in Tiled or LDtk.
---

# Level editors: Tiled and LDtk

Levels made in a tile editor are data, and data can be checked before anyone plays it. This skill covers the two editors most 2D teams use, how to keep their files as the source of truth, how to get them into Godot or Unity, and a script that finds broken levels (unreachable exits, sealed rooms, impossible jumps) in seconds. It builds on the core `level-design` skill: that skill says what a good level is and audits a set; this one handles the editor files and per-level geometry.

## When to use

Use this skill when:

- the game has tile-based 2D levels (platformer, top-down action, RPG, roguelike rooms, puzzle grids) and a team needs to choose or set up an editor;
- a Tiled (`.tmx`, `.tmj`) or LDtk (`.ldtk`) file must be read, edited, exported or imported into Godot 4 or Unity;
- an agent must answer "is this level completable?" without playing it;
- level files must feed the core level audit or the playthrough gate.

Do not use it for match-3, sort or other non-spatial puzzle content (use `puzzle_solver.py` and `match3_sim.py` from the core plugin), for 3D levels, or for procedural maps with no editor file (the checker still works on a hand-written `level.json`; see `references/level-checks.md`).

## Editor choice

| Need | Tiled | LDtk | Engine-native editor |
|---|---|---|---|
| Typed entities with fields and tags (enemies, doors, spawns) | Objects with custom classes and properties; powerful but set up per project | First-class, with typed fields, enums and entity references | Prefabs or scenes; most flexible, no editor-independent data |
| Collision as clean data | Collision tile layer, tile property or shape layer | IntGrid layer with named values: the strongest model | TileSet physics layers; data lives in engine files |
| Auto-tiling art | Terrains, Wang sets, automapping rules | Auto-layer rules from IntGrid | Godot terrains, Unity rule tiles |
| Many levels in one world | Worlds file | World layouts, neighbours, GridVania | Scenes |
| Merge friendliness | TMJ with CSV data merges tolerably | Separate level files (`.ldtkl`) | Scene files; varies |
| Infinite or huge maps | Infinite maps with chunks | Fixed-size levels | Chunked loading by hand |
| Isometric or hex maps | Yes | No (orthogonal only) | Engine-dependent |
| Engine importers | Godot: YATI; Unity: SuperTiled2Unity | Godot: community importer; Unity: LDtkToUnity | None needed |
| Scripts and CLI | `tiled --export-map` and flags; scripting | Parse the JSON; no export CLI | Engine CLI |
| `level_import.py` support | TMJ, TMX (orthogonal; finite and infinite) | Single-file and external-level projects | Export a `level.json` yourself |

Defaults:

- **Platformer or top-down action with several enemy and trigger types:** LDtk. IntGrid collision and typed entities cut the setup work.
- **Isometric, hex, infinite worlds, existing Tiled assets, or a team that already knows Tiled:** Tiled.
- **A game whose levels are scenes with heavy scripting (physics puzzles, 3D-like layouts):** engine-native, plus a small exporter that writes `level.json` for checks.
- **Procedural levels:** generate `level.json` directly and skip the editor; use the check as a validator.

Pick one editor per project. Two editors double the conventions, importers and bugs.

## Procedures

### 1. Set up conventions (once per project)

1. Write the convention in the project's README, using the tables in `references/tiled.md` section 11 or `references/ldtk.md` section 9: collision layer name, entity types, required properties, level fields.
2. Collision is one layer (Tiled `Collision`; LDtk IntGrid `Collisions` with named values). Art layers never carry collision.
3. Entities are `PlayerStart`, `Exit`, `Enemy`, `Pickup` and `Hazard`, or tagged equivalents. Extra types get a `role` property or `--role TYPE=ROLE`.
4. Put the map and its tilesets inside the engine project, relative paths only.
5. Commit the editor files. Do not commit editor session files (`.tiled-session`).

### 2. Convert and check one level

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/level_import.py convert levels/stage1.ldtk --level Stage_1 --out build/stage1.json \
        --audit-out .gamestudio/levels/w1_l001.level.json
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/level_import.py check build/stage1.json --mode platformer --jump-height 3 --jump-distance 5
```

Read the summary `convert` prints: `solid_source` must name your collision layer, `warnings` must be empty, entity counts must match the editor. Then read the check report (`references/level-checks.md` section 5).

Top-down: `--mode topdown` (add `--diagonal` for 8-way movement). Puzzle connectivity: `--preset puzzle`.

### 3. Tiled command-line export (build step or CI)

Use it when a tool needs one flat JSON without external tilesets or unresolved classes, or when the editor's data is zstd:

```
tiled --project game.tiled-project --export-map json --embed-tilesets --detach-templates \
      --resolve-types-and-properties maps/stage1.tmx build/stage1.tmj
```

Flags were read from the Tiled source (Oct 2026); confirm with `tiled --help`. Linux CI needs `xvfb-run`. Details: `references/tiled.md` section 10.

### 4. Import into the engine

1. Pick editor import, runtime import or your own loader (`references/engine-import.md` section 1).
2. Godot 4: `TileMapLayer` nodes and a TileSet with a physics layer. Tiled maps: YATI addon or Tiled's Godot 4 exporter. LDtk: the community importer, then a post-import script for entities.
3. Unity: Tilemap with `Composite Collider 2D`. Tiled: SuperTiled2Unity. LDtk: LDtkToUnity with a prefab replacement table.
4. Set pixel snapping once (Nearest or Point filter, integer scale, PPU equal to tile size).
5. Run the parity test (`references/engine-import.md` section 6): the engine's collision must equal `solid.rows`.

### 5. Regenerate without losing work

Re-run `convert --audit-out` any time the editor file changes. The script keeps the existing spec's `solver`, `difficulty_target`, `teach`, limits, `mechanic_refs` and hand-written `notes`, and rewrites the layout. Add `--overwrite-audit` to start fresh. Never hand-edit a generated `level.json`; edit the editor file.

### 6. Run the set audit and record evidence

```
python3 <core>/skills/level-design/scripts/level_audit.py audit --dir .gamestudio/levels --strict
```

Save check reports under `.gamestudio/reports/levels/`, and the logs under the feature's evidence folder for the `static` gate. The `playthrough` gate still needs bot runs through the real build (`references/level-checks.md` section 9).

## Worked example: an LDtk platformer level, checked, then into Godot

Scenario: stage 1 of a platformer. Player kit: jump height 3 tiles, flat jump 5 tiles. The designer built `levels/stage1.ldtk` with one level `Stage_1`, a 40 by 15 grid at 16 px, an IntGrid layer `Collisions` (value 1 named `wall`) and an `Entities` layer with `PlayerStart`, `Exit`, three `Enemy` and four `Coin` entities.

Step 1, convert:

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/level_import.py convert levels/stage1.ldtk --level Stage_1 \
        --out build/stage1.json --audit-out .gamestudio/levels/w1_l001.level.json
```

Summary: grid 40 by 15, `solid_source` "layer Collisions (auto)", entities spawn 1, exit 1, enemy 3, pickup 4, no warnings; the audit spec lists `audit_not_derivable`: `mechanic_refs`, `moves_or_time_limit`, `obstacles`, `difficulty_target`, `solver`. The designer fills `mechanics` and `teach` as level fields in LDtk and re-runs, so those fields derive on the next conversion.

Step 2, check at full capability:

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/level_import.py check build/stage1.json --mode platformer --jump-height 3 --jump-distance 5
```

Result: exit reachable at 45 tiles; 48 of 54 standing cells reachable; one coin at (32, 3) unreachable (it needs about a 5-tile rise); no traps; 6 entities on the route, 2.67 per screen of 20 tiles; longest empty stretch 17 tiles; verdict `warn`, exit code 0.

Step 3, check an easy-tier margin (80 percent of capability):

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/level_import.py check build/stage1.json --mode platformer --jump-height 2.4 --jump-distance 4
```

Result: the exit is unreachable (verdict `fail`, exit code 1) because the 4-tile pit needs a 5-tile jump. Decision: this is stage 1, so the designer narrows the pit to 3 tiles in LDtk, saves, and re-runs both checks. The coin on the high platform stays as a deliberate secret; the designer notes it in the level's `notes`.

Step 4, import into Godot 4:

1. Install the LDtk importer addon and enable it; put `stage1.ldtk` and its tileset PNG under `res://levels/`.
2. In the Import dock, set the entity post-import script (it replaces `PlayerStart` with the player scene, `Enemy` with the enemy scenes by `kind`, `Coin` with the pickup scene, `Exit` with the exit scene).
3. In the TileSet, add a physics layer; give the wall tiles a full-tile polygon (or generate the collision from IntGrid in the post-import script).
4. Project Settings: default texture filter Nearest, stretch mode `canvas_items`, scale mode `integer`.
5. Run the parity script (`references/engine-import.md` section 6) and diff its rows against `solid.rows` in `build/stage1.json`. Fix any difference in the editor file or TileSet, never in the scene.
6. Save the check reports as `static` evidence; run the bot sweep for `playthrough`.

After the designer narrows the pit to 3 tiles, the 80 percent run passes (exit reachable, route 53 tiles): a 3-tile pit needs a flat jump of 4, which is 0.8 of 5, the top of the core skill's easy-tier gap band (60 to 80 percent of maximum).

## Checklists

Before converting:

- [ ] One collision layer, named to match the convention; no collision in art layers.
- [ ] Exactly one `PlayerStart`; at least one `Exit` (or a recorded reason).
- [ ] Tilesets and images inside the project, relative paths.
- [ ] Tiled: orthogonal; CSV or zlib/gzip data; templates and classes resolved if the importer needs them.
- [ ] LDtk: `--level` named if the project has several; separate level files committed with the project.

After converting:

- [ ] `solid_source` names the intended layer; `warnings` empty or explained.
- [ ] Entity counts per role match the editor.
- [ ] `check` run with the real jump values (platformer) and again at 80 percent for easy levels.
- [ ] Every error fixed; every warning fixed or noted in the level's `notes`.
- [ ] Audit spec regenerated; `level_audit.py audit --strict` run on the set.

Before shipping a level set:

- [ ] Parity test passes in the engine (collision and entity counts).
- [ ] Imported scenes have no hand edits (diff the re-import).
- [ ] Bot sweep run for the `playthrough` gate; traps reported by `check` are visited or respawn.
- [ ] Reports and logs saved as gate evidence.

## Failure modes

| Failure | Cause | Remedy |
|---|---|---|
| Every cell walkable | No recognised collision source | Name the layer, or pass `--solid-layer` / `--solid-property` / `--solid-values` |
| Exit unreachable but the level plays | Game has a mechanic the model lacks (double jump, ladder, one-way) | Model it in a check copy (`level-checks.md` section 11); record the exception |
| Exit reachable but unplayable | Jump values too generous, or enemies and doors block | Lower the values to the real controller; rely on the bot run |
| Entities one cell off | Anchor or pivot ignored | Use `convert`'s cells; in custom loaders use the centre |
| `zstd` error | Tiled tile data compressed with zstd | Set CSV or zlib in Tiled, or export with `tiled --export-map` |
| `project has N levels` | LDtk project with several levels | Pass `--level NAME` |
| No collision in the engine | TileSet has no physics layer, or importer maps the wrong layer | `engine-import.md` sections 3 to 4 |
| Re-import erases a fix | Hand edit in the generated scene | Move it to the editor file or a post-import script |
| Audit spec lost its notes | Used `--overwrite-audit` | Re-add from version control; default merges |
| Check takes long | Huge platformer map | `--max-nodes`; split the level |

## Security

- The script reads files and writes JSON. It runs no external programs and uses no network. Tileset and level references (`source`, `externalRelPath`) are read relative to the map file; treat maps from outside the team as untrusted and review them before converting, because a crafted path can make the script read a different local file (it only parses XML or JSON and reports errors).
- Compressed tile data is read with a size cap equal to the expected size, so a decompression bomb cannot exhaust memory.
- Engine importers are code that runs inside the editor. Install them from the official repositories at a pinned version, read the release notes, and never open a map from an unknown source in an editor with scripting enabled.
- Tiled can run external commands (the project's Commands) and scripts (`--evaluate`, extensions). Do not enable or run them from an untrusted project.
- No keys or accounts are needed. This plugin ships no MCP server because no official Tiled or LDtk MCP server was found in October 2026.

## Platform notes

- PC, web and console games use the same editor files. Check texture and atlas size limits for the weakest target (web and older mobile GPUs prefer atlases at or below 2048 by 2048 or 4096 by 4096; verify for your targets).
- Touch games: tile sizes, camera zoom and HUD safe areas decide the "screen width in tiles" that sets pacing (`--screen-tiles`); derive it from the real viewport.
- Console and web builds load levels from packaged files; prefer editor import (baked assets) over runtime import of raw JSON unless the game has user levels.

## Reference library

| File | What it contains | Read it when |
|---|---|---|
| `references/tiled.md` | TMX and TMJ formats, layers, GIDs and flip flags, tile data encodings, objects and properties, tilesets, infinite maps, terrains, automapping, projects, command-line export, gameplay conventions, pitfalls | Reading, editing or exporting Tiled files; setting Tiled conventions |
| `references/ldtk.md` | Project JSON, levels and worlds, IntGrid, AutoLayer, Tiles and Entities layers, entity fields, separate level files, export options, schema and version notes, conventions, pitfalls | Reading or editing LDtk projects; setting LDtk conventions |
| `references/engine-import.md` | Editor vs runtime import, source of truth, Godot 4 TileMapLayer and importers, Unity Tilemap and importers, collisions, draw order, pixel snapping, parity test, post-import hooks | Getting levels into Godot or Unity; fixing import problems |
| `references/level-checks.md` | The `level_import.py` data format and checks, movement models, report reading, genre thresholds, jump parameters, audit and gate integration, CI recipe, limits | Running or interpreting `check`; wiring results into the audit and gates |

Script: `${CLAUDE_PLUGIN_ROOT}/scripts/level_import.py` (`convert`, `check`, `--selftest`; Python 3.9+, standard library only).

## Volatile facts (as of Oct 2026 - verify)

- Tiled latest release 1.12.2 (2026-05-27); command-line flags `--export-map`, `--export-tileset`, `--export-formats`, `--embed-tilesets`, `--detach-templates`, `--resolve-types-and-properties`, `--export-version`, `--minimize`, `--project`, `--evaluate`. Sources: https://github.com/mapeditor/tiled/releases and https://github.com/mapeditor/tiled/blob/master/src/tiledapp/main.cpp
- Tiled map format notes (class vs type, compression, chunks). Source: https://doc.mapeditor.org/en/stable/reference/json-map-format/
- LDtk latest release 1.5.3 (2024-01-15); official schema "LDtk 1.5.3". Sources: https://github.com/deepnight/ldtk/releases and https://ldtk.io/files/JSON_SCHEMA.json
- YATI (Godot 4 Tiled importer): v2.2.10 (2026-10-05), Godot 4.3+. Source: https://github.com/Kiamo2/YATI
- Godot LDtk importer (heygleeson): release 2.0.1 (2024-09-19), README states Godot 4.1+ and LDtk 1.4.1; output node type (TileMap or TileMapLayer) not verified. Source: https://github.com/heygleeson/godot-ldtk-importer
- LDtkToUnity: 6.12.4 (2026-10-10), Unity 2019.3+. Source: https://github.com/Cammin/LDtkToUnity
- SuperTiled2Unity: latest commit 2026-05-25, tag v2.3.0; download via itch.io. Source: https://github.com/Seanba/SuperTiled2Unity
- Godot stable 4.7.2 (2026-08-18); `TileMapLayer` replaced `TileMap` in 4.3. Sources: https://github.com/godotengine/godot/releases and https://docs.godotengine.org/en/stable/classes/class_tilemaplayer.html
- No official Tiled or LDtk MCP server found (search of the MCP ecosystem, Oct 2026); unverified beyond that search.
- Thresholds in `check` presets are starting values (estimates), not published standards.

## Related skills

- `level-design` (core): level craft, the level-spec format, `level_audit.py`, the five gates for content.
- `engine-godot` and `engine-unity` (core): engine project setup, tile and scene conventions, build commands.
- `game-ontology` (core): where level specs and gate evidence live in the project state.
- `procedural-generation` (core): generating levels without an editor; the checker validates their `level.json`.
- `qa-testing` and `playtest` (core): bot runs and playthrough evidence.
- `game-feel` (core): jump forgiveness values that change how generous jump parameters should be.
- `art-direction` and `technical-art` (core): tile size, palette and atlas decisions that fix PPU and snapping.
