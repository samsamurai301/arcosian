# LDtk

LDtk is a 2D level editor built around typed entities, IntGrid collision layers and auto-layer rules. A project is one JSON file (`.ldtk`), optionally with one extra file per level (`.ldtkl`). This file explains the project structure, the four layer types, entity fields, world layouts, the separate-levels option, the official JSON schema and its version notes, and a gameplay convention that `level_import.py` understands.

## Contents

1. Files and versions
2. Project structure
3. Levels and worlds
4. Layer types and layer instances
5. Entities and fields
6. Separate level files
7. Other export options
8. Reading the JSON safely
9. Gameplay conventions
10. Editing and automation
11. Pitfalls

## 1. Files and versions

| File | What it is |
|---|---|
| `project.ldtk` | JSON: settings, definitions (`defs`), and levels. With "Save levels separately" on, level contents move out |
| `project/Level_1.ldtkl` | One level (only with separate level files). Same data as an entry of `levels`, plus a file header |
| `project/png/`, `simplified/` | Optional image and "Super simple export" output |

Version facts, checked in October 2026:

- The official JSON schema at https://ldtk.io/files/JSON_SCHEMA.json is titled "LDtk 1.5.3 JSON schema".
- The latest GitHub release of `deepnight/ldtk` is 1.5.3 (15 January 2024). LDtk is stable rather than fast-moving; the schema and the importers below may therefore trail or lead by minor versions.
- Every project carries `jsonVersion` (a string). Importers state the LDtk version they were tested with. One Godot importer's README names 1.4.1, a Unity importer tracks the latest. Compare `jsonVersion` in your file with the importer's stated version before blaming data.
- LDtk keeps a list of planned deprecations at https://ldtk.io/json/ . Read it before writing a custom reader: deprecated fields (for example the old `intGrid` array, replaced by `intGridCsv`) disappear after a cycle.

## 2. Project structure

Top-level keys of the project (from the 1.5.3 schema):

| Key | Meaning |
|---|---|
| `jsonVersion`, `appBuildId`, `iid` | Format and build identifiers |
| `defaultGridSize`, `defaultLevelWidth`, `defaultLevelHeight`, `defaultPivotX/Y` | Defaults for new items |
| `worldLayout`, `worldGridWidth/Height` | World layout; see section 3. These move into `worlds[]` when "Multi-worlds" is enabled and are then null at the root |
| `worlds` | Worlds (`iid`, `identifier`, `worldLayout`, `levels`) |
| `levels` | Level instances (at the root, or inside `worlds[].levels` with multi-worlds) |
| `externalLevels` | True when levels are saved separately |
| `simplifiedExport`, `exportTiled`, `exportPng`, `imageExportMode` | Export options |
| `toc` | Table of contents with world coordinates and custom field values |
| `defs` | Definitions: `layers`, `entities`, `tilesets`, `enums`, `externalEnums`, `levelFields` |
| `flags`, `minifyJson`, `identifierStyle`, `levelNamePattern` | Misc settings |

`defs` is where meaning lives. A layer instance points to its layer definition by `layerDefUid`; IntGrid value names are in `defs.layers[].intGridValues` (`value`, `identifier`, `color`); entity definitions give each entity its tags, size, pivot and field definitions; tileset definitions hold tile enum tags (`enumTags`) and `customData`.

A reader that only walks `levels` sees numbers. A reader that also reads `defs` sees names. Always read both.

## 3. Levels and worlds

A level has `identifier` (the name), `iid` (a stable unique id), `uid` (an integer), `pxWid`, `pxHei`, `worldX`, `worldY`, `worldDepth`, `bgColor`, `fieldInstances` (level fields), `layerInstances`, `externalRelPath` and `__neighbours`.

- `layerInstances` is sorted in display order: the first layer is the top-most. It is `null` in the project file when levels are saved separately.
- `worldX` and `worldY` matter for the `GridVania` and `Free` layouts; for the linear layouts they are -1.

World layouts (values in the schema): `Free`, `GridVania`, `LinearHorizontal`, `LinearVertical`, or `null`.

| Layout | Use |
|---|---|
| `Free` | Levels placed anywhere on a map canvas; world coordinates are pixels |
| `GridVania` | Levels snapped to a coarse world grid (Metroidvania maps; neighbours are explicit) |
| `LinearHorizontal` / `LinearVertical` | A strip of levels in order; the order is the play order |

For a linear game (stage 1, 2, 3), use a linear layout or one level per file and keep the order in `order.json` (core level audit). For a connected world, use `GridVania` and read `__neighbours` to build transitions.

## 4. Layer types and layer instances

A layer instance (`layerInstances[]`) has `__identifier`, `__type`, `__cWid`, `__cHei` (size in cells), `__gridSize` (pixels per cell), `__pxTotalOffsetX/Y`, `__opacity`, `visible`, `layerDefUid`, and per-type data.

| `__type` | Holds | Use it for |
|---|---|---|
| `IntGrid` | `intGridCsv`: one integer per cell, row by row from the top-left. `0` is empty; values start at 1. May also hold `autoLayerTiles` if auto rules are attached | Collision, water, zones, walkable masks. The best gameplay data in LDtk |
| `AutoLayer` | `autoLayerTiles`: tiles generated by rules from an IntGrid (its own or a source layer) | Art that follows the IntGrid. Never hand-painted |
| `Tiles` | `gridTiles`: hand-placed tiles | Decor, props |
| `Entities` | `entityInstances` | Spawns, exits, enemies, pickups, triggers |

A tile record has `px` (position in the layer, in pixels; add the layer offset), `src` (position in the tileset image), `t` (tile id in the tileset), `f` (flip bits: bit 0 flips X, bit 1 flips Y, so 0 to 3), `a` (alpha) and `d` (internal editor data).

IntGrid rules of thumb:

- Make one IntGrid layer the single source of truth for collision. Give values names (`wall`, `water`, `ladder`) so the reader and humans agree. `level_import.py` treats values named `wall`, `solid`, `ground`, `block`, `blocked` or `collision` as solid, falls back to value 1, and accepts `--solid-values` as numbers or names.
- Several IntGrid layers can have different grid sizes (for example 16 px collision and 8 px decor). `level_import.py` samples the collision layer's cell centres onto the main grid.
- Auto-layer rules turn IntGrid values into art, so level designers paint meaning and the art follows. Rules live in `defs.layers[].autoRuleGroups`; tiles they produce are in the instance's `autoLayerTiles`.

Tile enum tags: a tileset can tag tiles with values of an enum (for example `Solid`). Those are in `defs.tilesets[].enumTags` (`enumValueId`, `tileIds`). `level_import.py --solid-property KEY` treats a tile tagged `KEY` as solid in Tiles, AutoLayer and IntGrid layers. Custom tile data (`customData`, a string per tile) is not read by the script.

## 5. Entities and fields

An entity instance has `__identifier` (its definition name), `__grid` (cell position in its layer), `px` (pixel position of the pivot, in level space, before layer offsets), `width`, `height`, `__pivot` (0 to 1 in each axis), `__tags` (tags from the definition), `__tile` (the display tile), `iid`, `defUid`, `__worldX/__worldY` (only in `Free` and `GridVania` worlds) and `fieldInstances`.

Pivot matters. `px` is the pivot position, not the top-left. The top-left is `px - pivot x size`. A character with pivot `(0.5, 1)` has `px` at the bottom centre of its feet, so the cell under `px.y` is the floor, not the entity's own cell. Use the box centre to find the cell: `centre = px - pivot x size + size / 2`.

A field instance has `__identifier`, `__type`, `__value`. Types: `Int`, `Float`, `Bool`, `String`, `Multilines`, `Color` (hex string `#rrggbb`), `FilePath`, `Point` (an object with `cx`, `cy`), `Enum(name)` (the value is a string), `EntityRef` (an object with `entityIid`, `layerIid`, `levelIid`, `worldIid`), and arrays of any of these (the type reads `Array<Int>` and so on; the value is a JSON array). Check `__type` before reading `__value`.

Entity definitions are where design lives: set tags (`spawn`, `exit`, `enemy`, `pickup`), a default size, a pivot, a colour and typed fields. Required fields in the editor become defaults in the data, so readers should not need to guess.

## 6. Separate level files

The editor option is named "Save levels separately" in the schema text. When on:

- `externalLevels` is true.
- Each level is a `.ldtkl` file in a sub-folder named after the project.
- Each level entry in the `.ldtk` has `externalRelPath` (relative to the project file) and `layerInstances: null`.
- The `.ldtkl` file contains the level object: identifier, size, fields and all layers.

Use it for big projects and teams: a designer edits one level without touching the project file, so merges and diffs shrink. A reader must follow `externalRelPath` for every level it needs. `level_import.py` does this and rejects a bare `.ldtkl` (it needs the project for `defs`).

If a level shows no layers, check `externalRelPath` first.

## 7. Other export options

| Option | What it writes | When to use |
|---|---|---|
| Super simple export (`simplifiedExport`) | One folder per level with a composite PNG, one PNG per layer, an `-int` PNG and a CSV per IntGrid layer, and `data.json` | Quick engine integration without writing a reader. Files appear only after the project is saved |
| Tiled export (`exportTiled`) | `.tmx` files in a `tiled` folder beside the project | A stopgap for a framework that reads only TMX. Limits per the LDtk docs: IntGrid layers become tile layers over a dummy sheet, stacked tiles may split across layers, arrays become indexed properties, points and enums become strings, entity coordinates are top-left (anchors in `__anchorX/Y`, cells in `__cx/__cy`) |
| PNG export | Rendered layer images | Previews, thumbnails, store art |

Prefer the JSON project over both conversions: it keeps types and entity references.

## 8. Reading the JSON safely

1. Check `jsonVersion` and the importer's stated version.
2. Read `defs` first and build lookups: layer defs by `uid`, IntGrid values by layer, entity defs, tilesets.
3. Choose one level. Resolve `externalRelPath` if `layerInstances` is null.
4. Use the main collision layer's `__gridSize` as the level's tile size. Level size in cells is `ceil(pxWid / gridSize)` by `ceil(pxHei / gridSize)`.
5. Convert entity positions with the pivot correction; apply layer offsets.
6. Ignore fields starting with `__` only when you know their meaning; they are derived values that are safe to read but should not be written back.
7. Do not trust `intGrid` (deprecated); use `intGridCsv`.

The official schema is JSON Schema draft-07 (`LdtkJsonRoot` plus `otherTypes`). It can generate typed loaders with QuickType, which is what most community importers do.

## 9. Gameplay conventions

| Item | Convention |
|---|---|
| Collision | IntGrid layer named `Collisions` (also `Collision`, `Solid`, `Walls`, `Ground`), value 1 named `wall`; extra values for `ladder`, `water`, `oneway` with names |
| Entities layer | One Entities layer named `Entities` |
| Spawn | Entity `PlayerStart` (tag `spawn`) |
| Exit | Entity `Exit` (tag `exit`), optional field `next_level` (String or EntityRef) |
| Enemy | Entity `Enemy`, field `kind` (Enum or String), optional `hp` (Int), `patrol` (Array of Point) |
| Pickup | Entity `Pickup` or `Coin`, field `kind`, `amount` |
| Hazard | Entity `Spike` or `Hazard` |
| Level fields | `teach` (String: teach, test, twist, reward), `mechanics` (String, comma-separated ids), `moves` (Int), `time_sec` (Float), `target_win_rate` (Float 0 to 1) |

`level_import.py` classifies entities by tag first, then identifier, and also reads a String field named `role` or a Bool field named after a role. Level fields become `metadata.properties` and feed `convert --audit-out`.

## 10. Editing and automation

- LDtk has no documented command-line export to engine formats. The project JSON is the interface: parse it with a script, or enable Super simple export and let the editor write on save.
- Agents can edit `.ldtkl` or `.ldtk` JSON for small changes (move an entity: change `px` and `__grid` together). Do not edit `iid` values and do not reformat the whole file; LDtk rewrites it on save. Open the level in LDtk to confirm it loads.
- Large changes belong in the editor. Auto-layer output is a function of the rules, so changing `autoLayerTiles` by hand is overwritten on the next save.
- Keep the project in version control with "Save levels separately" and minify off (`minifyJson: false`) so diffs are readable.
- The core rule applies: the editor file is the source of truth; generated JSON is rebuilt from it, never edited by hand.

No official LDtk MCP server was found in October 2026, so this plugin ships command-line recipes instead of an `.mcp.json`.

## 11. Pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| Level has no layers | Levels saved separately; `layerInstances` is null | Follow `externalRelPath` |
| Entity one cell too low | Pivot at the bottom; the reader used `px` as top-left | Subtract `pivot x size`, then use the centre |
| Entity coordinates wrong in a multi-grid layer | Grid sizes differ between layers | Convert pixels, not cells, when mixing layers |
| `intGridCsv` length is not `cWid x cHei` | Level resized after the layer was created, or a partly saved file | Re-open and save in LDtk; reject the file |
| Importer errors after an LDtk update | `jsonVersion` newer than the importer supports | Update the importer, or pin the LDtk version in the project README |
| Collision differs between editor and game | The reader used the AutoLayer tiles, not the IntGrid values | Use IntGrid for gameplay; auto tiles are art |
| Two worlds, no levels at the root | Multi-worlds enabled | Read `worlds[].levels` |

## Sources

- Format overview: https://ldtk.io/docs/game-dev/json-overview/
- JSON documentation and deprecations: https://ldtk.io/json/
- Official schema: https://ldtk.io/files/JSON_SCHEMA.json
- Separate level files: https://ldtk.io/docs/game-dev/json-overview/optional-separate-levels/
- Super simple export: https://ldtk.io/docs/game-dev/super-simple-export/
- Export options and Tiled export limits: https://ldtk.io/docs/general/exporting/
- Releases: https://github.com/deepnight/ldtk/releases
