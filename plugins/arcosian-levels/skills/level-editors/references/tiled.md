# Tiled

Tiled is a general 2D tile map editor. It saves maps as XML (`.tmx`) or JSON (`.tmj`), supports tile layers, object layers, custom properties, templates, infinite maps and terrain tools, and has a small command line for exporting. This file covers what an agent needs to read, edit, export and automate Tiled files, and how to mark gameplay (spawn, exit, enemy, pickup, solid) so `level_import.py` and the engine importers find it.

## Contents

1. Files and formats
2. Map structure: layers, tiles, GIDs
3. Tile data encodings and compression
4. Objects and properties
5. Tilesets: embedded, external, collisions
6. Infinite maps and chunks
7. Terrains and Wang sets
8. Automapping
9. Projects, custom types, templates
10. Command line
11. Gameplay conventions (property table)
12. Editing files by hand or by script
13. Pitfalls

## 1. Files and formats

| Extension | What it is | Notes |
|---|---|---|
| `.tmx` | Map, XML | Original format. Properties are child elements. |
| `.tmj` | Map, JSON | Same data as TMX. Older files and some tools use `.json`. |
| `.tsx` / `.tsj` | Tileset, XML / JSON | External tileset, referenced by `source` from a map. |
| `.tx` / `.tj` | Object template, XML / JSON | Reusable object with default properties. |
| `.world` | World file (JSON) | Places several maps on one canvas. Not read by `level_import.py`. |
| `.tiled-project` | Project | Folders, extensions, automapping rules, custom types. Source verified in the Tiled repository: the project suffix is `tiled-project`. |
| `.tiled-session` | Personal editor state | Sits beside the project. Do not commit it. |

Pick one map format per project. Use TMJ when agents or scripts edit maps: JSON is easy to parse and diff. Use TMX when a library you rely on only reads XML. Tiled converts between them with `File > Save As` or the command line.

Tiled writes a `version` (the format version, a string since format 1.6) and `tiledversion` (the editor version) into every file. Older Tiled opens newer files with warnings or data loss. Set the project's Compatibility Version if a library or engine importer lags behind.

## 2. Map structure

A map has `orientation` (`orthogonal`, `isometric`, `oblique`, `staggered`, `hexagonal`), `width` and `height` in tiles, `tilewidth` and `tileheight` in pixels, `infinite`, `renderorder`, `properties`, `tilesets` and `layers`. `level_import.py` reads orthogonal maps only; it refuses the others with a message.

Layer types:

| Type | JSON `type` | Contents |
|---|---|---|
| Tile layer | `tilelayer` | A grid of GIDs (`data`, or `chunks` on infinite maps) |
| Object layer | `objectgroup` | A list of `objects` |
| Image layer | `imagelayer` | One image |
| Group layer | `group` | Child `layers`; offsets and opacity apply to children |

Every layer has `name`, `visible`, `opacity`, optional `offsetx` / `offsety` (pixels), optional `class` (since 1.9) and `properties`. Layer order is draw order: the first layer in the file is drawn first (at the back).

### Global tile IDs (GIDs)

A tile layer cell holds a 32-bit GID. The top four bits are flip flags, and they must be cleared before the number is used. Per the Tiled documentation: bit 32 is a horizontal flip, bit 31 a vertical flip, bit 30 a diagonal flip (rotation in orthogonal maps), bit 29 is hexagonal rotation and must still be cleared. In code: `gid & 0x1FFFFFFF`, flags in `gid >> 28`.

`0` means empty. To find the tile: take the tileset with the greatest `firstgid` not above the GID; the local tile id is `gid - firstgid`. GIDs are only meaningful inside one map, because tileset order can differ between maps.

## 3. Tile data encodings and compression

Set in Map Properties as "Tile Layer Format". The format applies to the whole map.

| Format | TMX | TMJ | `level_import.py` |
|---|---|---|---|
| CSV | `<data encoding="csv">` comma-separated text | `data` is an array of integers | yes |
| Base64, uncompressed | `encoding="base64"` | `encoding: "base64"`, `data` is a string | yes |
| Base64 + zlib | `compression="zlib"` | `compression: "zlib"` | yes |
| Base64 + gzip | `compression="gzip"` | `compression: "gzip"` | yes |
| Base64 + zstd | `compression="zstd"` (since Tiled 1.3) | `compression: "zstd"` | no: refused with a message |
| XML tiles | `<tile gid="..."/>` children (legacy) | n/a | yes (TMX) |

Decoding base64 data: decode, decompress if needed, then read `width x height` little-endian unsigned 32-bit integers, row by row from the top-left. A wrong byte count means the wrong size or a corrupt file. `compressionlevel` (map property, default -1) only affects writing.

zstd needs a library that the Python standard library does not include. To feed a zstd map to `level_import.py`, set the format to CSV or zlib in Tiled, or export a copy with the command line (section 10).

For files agents will edit, choose CSV: it is diffable and needs no codec.

## 4. Objects and properties

Object fields: `id`, `name`, `type` (the object's class; named `type` in JSON for objects and tiles), `x`, `y`, `width`, `height`, `rotation`, `visible`, `properties`, and shape markers `point`, `ellipse`, `capsule` (Tiled 1.12), `polygon`, `polyline`, `text`. A tile object also has `gid`. A `template` field means the object was made from a template file.

Rules that cause bugs:

- Positions are in pixels, not tiles. Divide by tile size.
- Rectangles and ellipses are anchored top-left.
- **Tile objects (with a `gid`) are anchored bottom-left.** Their top edge is `y - height`.
- Polygons and polylines store points relative to the object's `x`, `y`.
- The `class` / `type` naming changed: format 1.9 renamed `type` to `class` on objects and tiles, and 1.10 reverted it. `class` still exists on maps, layers and tilesets. Readers should accept both on objects.

Custom properties have a name, a type and a value. Types: `string`, `int`, `float`, `bool`, `color`, `file`, `object` (a reference to another object), and `class` (a group of named values, since 1.8). TMX stores the type as an attribute and omits it for strings. In TMJ a property is `{ "name": ..., "type": ..., "value": ... }` in a list. Multi-line strings in TMX may sit in the element text instead of the `value` attribute.

Properties can be set on the map, layers, tilesets, tiles, objects and Wang sets.

## 5. Tilesets

- **Embedded**: stored inside the map. Simple and self-contained. Many copies of the same tileset in many maps diverge when edited.
- **External** (`.tsx` / `.tsj`): the map holds `firstgid` and `source`. One file to edit for all maps. The importer must resolve the relative path.

Per-tile data in a tileset: properties, `type` / class, collision shapes (an object group on the tile, drawn in the Tile Collision Editor), animation frames, probability and the tile image for collection-of-images tilesets.

Two ways to mark solid tiles:

1. A tile layer that only holds solid tiles (for example `Collision`). Anything non-empty is solid.
2. A boolean tile property (for example `solid`) set on the tiles in the tileset. The collision map is then derived from every tile layer.

Use method 1 when the art and the collision differ (a bridge you walk under). Use method 2 when collision follows tile type (all grass tiles walkable, all water tiles solid) and designers paint once. Do not mix both in one project without a written rule.

Engine importers handle tile collision shapes differently from layer-based collision (see `engine-import.md`).

## 6. Infinite maps and chunks

An infinite map (`infinite: true`) has no fixed size. Tile layers store `chunks`, each with `x`, `y`, `width`, `height` and its own `data` in the same encoding. Coordinates can be negative. The Map Properties "Output Chunk Width/Height" set the chunk size (check the current defaults in the editor).

Consequences:

- The map `width` and `height` are not the playable size. Compute the bounding box of non-empty cells.
- Chunks may contain empty cells; an empty chunk is simply absent.
- Object positions use the same origin, so they can be negative.
- Many engine importers do not support infinite maps, or flatten them. `level_import.py` computes the bounding box over all tile layers and objects, shifts everything to a zero origin, and records the shift in `origin`.

Use finite maps for hand-built levels (a platformer stage, a dungeon floor). Use infinite maps only when the world really grows without a boundary.

## 7. Terrains and Wang sets

Terrain tools paint tiles that join correctly with their neighbours. In the file they are `wangsets` on a tileset, each with a `type` (`corner`, `edge` or `mixed`; Tiled 1.5 merged the older terrain and Wang formats), a list of colours, and a map from tiles to colour ids. These are editor aids: the map stores only the resulting tile GIDs. Engines and `level_import.py` never need the Wang data.

Use terrains for ground, water, walls and paths that need clean edges. Use plain stamps for props.

## 8. Automapping

Automapping places or replaces tiles from rules, so designers paint a coarse layer and the borders, shadows and variations fill in. Details from the Tiled manual:

- **Rule maps** are ordinary map files. A `rules.txt` file lists them in order; lines can name rule maps, other `.txt` files, comments (`#` or `//`) and filters such as `[town*]` (Tiled 1.9+) that limit the following rules to matching map names.
- Rules are assigned by the project property "Automapping rules", or by a `rules.txt` in the map's own folder (which overrides the project setting).
- Input layers are named `input[not][index]_name`; output layers `output[index]_name`. `name` is the target layer in the working map; a missing output layer is created.
- Map properties for rules: `DeleteTiles`, `AutomappingRadius`, `MatchOutsideMap`, `OverflowBorder`, `WrapBorder`, `MatchInOrder`, `NoOverlappingOutput`. Layer properties: `AutoEmpty`, `IgnoreHorizontalFlip`, `IgnoreVerticalFlip`, `IgnoreDiagonalFlip`, `IgnoreHexRotate120`, `Probability`.
- An object layer named `rule_options` holds per-rule options (`ModX`, `ModY`, `OffsetX`, `OffsetY`, `Probability`, `Disabled`, `NoOverlappingOutput`, `IgnoreLock`).
- Run it from the Map menu (AutoMap, or AutoMap While Drawing). There is no documented command-line flag to automap; do it in the editor before export, and commit the result.

Rules change tile layers only. Keep gameplay (collision, spawn, exit) on separate layers that automapping does not touch, or the rules may overwrite them.

## 9. Projects, custom types, templates

A project file lists asset folders and carries the Compatibility Version, the extensions folder, the automapping rules and the custom types. Open maps through the project so custom classes resolve.

Custom types (classes, enums) are defined in the Custom Types Editor and stored in the project. A class used as an object's `type` can carry default property values. When a map is exported, those defaults are not written unless the export resolves them (section 10, `--resolve-types-and-properties`). An importer that reads the raw map sees only the properties a designer changed. This is the most common reason "the enemy has no health value".

Templates (`.tx` / `.tj`) hold a reusable object. An instance keeps a `template` reference and stores only overrides. Detach templates on export when the consumer cannot read template files (section 10).

## 10. Command line

Flags below were read from the Tiled source (`src/tiledapp/main.cpp`, master branch) in October 2026 and match Tiled 1.12.x. Always confirm with `tiled --help` on the installed version.

| Flag | Meaning |
|---|---|
| `--export-map [format] <map> <target>` | Export a map file to the target; the format is optional |
| `--export-tileset [format] <tileset> <target>` | Export a tileset file |
| `--export-formats` | Print the supported export formats and quit |
| `--embed-tilesets` | Embed tilesets into the exported map |
| `--detach-templates` | Replace template instances with plain objects |
| `--resolve-types-and-properties` | Write resolved class defaults and inherited properties |
| `--export-version <v>` | Compatibility version used while exporting |
| `--minimize` | Omit unnecessary whitespace in the exported file |
| `--project <file>` | Load a project (needed for custom types) |
| `--evaluate <script>` / `-e` | Run a script file and quit (scripting API) |
| `--quit` | Check the arguments and quit without opening the editor |
| `--new-instance` | Do not reuse a running Tiled |
| `--disable-opengl` | Turn off hardware-accelerated rendering |
| `-v`, `--version` / `-h`, `--help` | Version / help |

Format choice: the source matches the format argument against each format's short name (case-insensitive), and without one it picks the format from the target file extension and refuses an ambiguous extension. Run `tiled --export-formats` to see the names. The JSON map format is normally listed as `json`; confirm on your build.

Recipes:

```
# one map to JSON for a tool that cannot read XML or external tilesets
tiled --project game.tiled-project --export-map json \
      --embed-tilesets --detach-templates --resolve-types-and-properties \
      maps/level1.tmx build/level1.tmj

# every map in a folder (POSIX shell)
for f in maps/*.tmx; do
  tiled --project game.tiled-project --export-map json --embed-tilesets \
        --detach-templates --resolve-types-and-properties "$f" "build/$(basename "${f%.tmx}").tmj"
done
```

```
# PowerShell
Get-ChildItem maps\*.tmx | ForEach-Object {
  tiled --project game.tiled-project --export-map json --embed-tilesets --detach-templates `
        --resolve-types-and-properties $_.FullName "build\$($_.BaseName).tmj"
}
```

Headless Linux: the manual says Tiled still needs an X server for command-line export. In CI run `xvfb-run tiled --export-map ...`. The exact `--export-map` argument order is source then target; if a build rejects the flags, run `tiled --help` first.

Preview what a converter will see: export with the three resolve flags, then run `level_import.py convert` on the `.tmj`.

The export step belongs to CI or a build script, never to a hook that runs on every edit: it launches the editor binary.

## 11. Gameplay conventions

Choose one convention per project and write it in the project's `README`, because `level_import.py` and the engine importers read names and properties, not intentions.

Layers:

| Layer name | Type | Purpose |
|---|---|---|
| `Collision` | tile or object layer | Solid cells (any tile) or shapes. `level_import.py` finds names `collision`, `solid`, `walls`, `ground`, `blocking` (any case) automatically |
| `Ground`, `Walls`, `Decor` | tile layers | Art only |
| `Entities` | object layer | Spawn, exits, enemies, pickups, hazards |
| `Triggers` | object layer | Rectangles that fire events (cutscene, checkpoint) |

Objects (set `type`, the class, on each object):

| `type` | Required properties | Role |
|---|---|---|
| `PlayerStart` | none; optional `facing` | spawn |
| `Exit` | optional `next_level` (string) | exit |
| `Enemy` | `kind` (string), optional `hp` (int), `patrol` (object reference) | enemy |
| `Pickup` | `kind` (string), optional `amount` (int) | pickup |
| `Hazard` | optional `damage` (int) | hazard |
| `Checkpoint` | optional `order` (int) | other |

Roles are inferred from the type or name by token (`PlayerStart`, `spawn`, `Exit`, `goal`, `Enemy`, `coin`, `Spike` and similar). To override, set a string property `role` (`spawn`, `exit`, `enemy`, `pickup`, `hazard`, `other`) or pass `--role TYPE=ROLE` to `convert`.

Tile properties for solid method 2: `solid` (bool). Also useful: `oneway` (bool, platforms you can jump through; `level_import.py` does not model them, see `level-checks.md`), `damage` (int), `friction` (float), `climbable` (bool).

Map properties used by `convert --audit-out`: `teach` (`teach`, `test`, `twist`, `reward`), `mechanics` (comma-separated mechanic ids), `moves` (int), `time_sec` (number), `target_win_rate` (0 to 1).

## 12. Editing files by hand or by script

- Prefer TMJ with CSV data for scripted edits. Change only what you mean to: keep key order, do not reformat, and preserve unknown keys.
- Never hand-edit base64 data.
- After any edit, open the map in Tiled once (or run an export) to prove it loads. Tiled rewrites the file, which can reorder keys; commit that result.
- Object `id` values are unique per map; `nextobjectid` and `nextlayerid` must stay above the highest used. Adding an object by hand means bumping `nextobjectid`.
- Adding a tile layer by hand needs a unique layer `id`, and `data` of exactly `width x height` integers.
- Keep tileset images next to the tilesets and use relative paths. An absolute path breaks on every other machine.

## 13. Pitfalls

| Symptom | Cause | Fix |
|---|---|---|
| Tiles look wrong or flipped | Flip bits left in the GID | Mask with `0x1FFFFFFF` before the lookup |
| Entities half a tile off | Tile objects anchor bottom-left; points have no size | Use the corrected top-left, then the centre cell |
| Enemy has no default properties | Class defaults not resolved | Export with `--resolve-types-and-properties` |
| Importer says tileset not found | External `source` path wrong after a move | Keep `.tsx` and images beside the map; use relative paths |
| Everything walkable after convert | No layer or property recognised as solid | Name the layer `Collision`, or pass `--solid-layer` / `--solid-property` |
| Importer fails on a map | zstd data or an infinite map in an engine that lacks support | Switch to CSV or zlib; use a finite map |
| Objects vanish in the engine | Importer skips unknown classes, or an object layer was hidden | Check the importer's object handling and layer visibility |
| Merge conflicts in maps | Base64 data and key reordering | CSV in TMJ, one map per designer, merge in the editor |

## Sources

- Tiled manual and format references: https://doc.mapeditor.org/en/stable/
- Command-line parser source: https://github.com/mapeditor/tiled/blob/master/src/tiledapp/main.cpp
- JSON map format: https://doc.mapeditor.org/en/stable/reference/json-map-format/
- Global tile IDs: https://doc.mapeditor.org/en/stable/reference/global-tile-ids/
- Automapping: https://doc.mapeditor.org/en/stable/manual/automapping/
