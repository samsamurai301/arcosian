# arcosian-levels

Adapter plugin for the `arcosian` core plugin. It adds a skill and a script for tile-based level work: choosing between Tiled, LDtk and engine-native editors, keeping editor files as the source of truth, importing them into Godot 4 and Unity, and checking levels automatically before anyone plays them.

Requires the core plugin `arcosian` (declared as a dependency).

## What you get

- Skill `level-editors`: editor decision table, file conventions, command-line recipes, a worked example (an LDtk platformer level, checked, then imported into Godot), checklists, failure modes and security notes. Four reference files cover Tiled, LDtk, engine import and the level checks.
- Script `scripts/level_import.py` (Python 3.9+, standard library only):
  - `convert <map.tmj|map.tmx|project.ldtk> --out level.json` normalises a map into one JSON file: grid and tile size, layers, a solid/walkable grid, entities with roles and cells, and metadata. Tiled CSV and base64 (none, zlib, gzip) data, finite and infinite maps; LDtk single-file and separate-level-file projects. `--audit-out` also writes a level-spec for the core `level_audit.py` and lists the fields it cannot derive.
  - `check level.json` tests reachability from spawn to every exit (top-down or approximate platformer jumps and falls), unreachable pickups and enemies, dead ends, softlock traps, path length and pacing. It prints a JSON report and exits 1 when an exit is unreachable.
  - `--selftest` runs offline with inline fixtures.
- No `.mcp.json`: no official Tiled or LDtk MCP server was found (October 2026), so the skill gives command-line recipes instead.

## Setup

1. Install the core plugin `arcosian`, then this plugin.
2. Install the editor you use: Tiled (https://www.mapeditor.org/) or LDtk (https://ldtk.io/). The script does not need either; it reads their files. Only the Tiled command-line export recipes need the Tiled program.
3. Engine importers are separate downloads, chosen in the skill: YATI or Tiled's Godot 4 exporter, a Godot LDtk importer, SuperTiled2Unity, LDtkToUnity. Install them from their official repositories at a pinned version.
4. Check the script: `python3 scripts/level_import.py --selftest`.

## What this plugin runs, sends and fetches

- **Runs:** `scripts/level_import.py` on files you name. It runs no other programs.
- **Sends:** nothing. There is no network access and no account or key.
- **Fetches:** nothing. The skill describes Tiled command-line recipes (`tiled --export-map ...`) that you or your build run yourself.
- **Writes:** the output paths you give (`--out`, `--audit-out`, `--out` of `check`).

## Security

- Treat maps from outside the team as untrusted. The script reads referenced tileset and level files relative to the map and only parses them as XML or JSON; compressed tile data is read with a size cap.
- Engine importers run code inside the engine editor. Install them from official repositories, pinned, and review release notes.
- Tiled project Commands and scripts can run programs; do not enable them from untrusted projects.

## Typical session

1. Ask for a level editor setup or load the `level-editors` skill; pick the editor from the decision table.
2. Write the conventions (collision layer, entity types) in the project README.
3. Designers build levels in the editor. An agent runs `convert` and `check` after each change.
4. Fix errors; note accepted warnings in the level's `notes`.
5. Run the core audit on the generated level-specs, then import into the engine and run the parity test.
6. Save reports as gate evidence; run the bot sweep for the playthrough gate.

## Verified and not verified

Verified in October 2026: Tiled command-line flags (read from the Tiled source, `src/tiledapp/main.cpp`), Tiled and LDtk file format details (official documentation and the LDtk JSON schema), versions and licences of the named importers (GitHub), and the script's behaviour (its self-test passes, and the audit output was run through the core `level_audit.py` and `validate_json.py`). Not verified: the importers inside a running Godot or Unity (no engine was run), the Tiled command-line export itself (Tiled was not installed), whether the Godot LDtk importer emits `TileMapLayer` nodes, and that the platformer movement model matches your game's controller (it is an approximation; the playthrough gate is the test of record). Thresholds in the check presets are starting values.

## Volatile facts (as of Oct 2026 - verify)

- Tiled 1.12.2 and its flags. Sources: https://github.com/mapeditor/tiled/releases and https://github.com/mapeditor/tiled/blob/master/src/tiledapp/main.cpp
- LDtk 1.5.3 and its JSON schema. Sources: https://github.com/deepnight/ldtk/releases and https://ldtk.io/files/JSON_SCHEMA.json
- YATI. Source: https://github.com/Kiamo2/YATI
- Godot LDtk importer. Source: https://github.com/heygleeson/godot-ldtk-importer
- LDtkToUnity. Source: https://github.com/Cammin/LDtkToUnity
- SuperTiled2Unity. Source: https://github.com/Seanba/SuperTiled2Unity
- No official Tiled or LDtk MCP server found. Source: search of the MCP ecosystem, October 2026.

## License

MIT.
