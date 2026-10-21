# Importing Tiled and LDtk levels into Godot and Unity

A level editor file only becomes a game level when an engine reads it. This file explains the choices: import in the editor or at run time, which importer to use for Godot 4 and Unity, how collision, draw order and pixel snapping map across, and how to keep the editor file as the single source of truth. Importer names, versions and maintenance status were checked in October 2026 and change often; the last section lists what to re-check.

## Contents

1. The decision: editor import, runtime import, or your own loader
2. Source of truth
3. Godot 4
4. Unity
5. Collision, draw order and pixel snapping side by side
6. Parity test: does the engine see the same walls?
7. Post-import hooks for gameplay
8. Failure modes
9. What to re-check

## 1. The decision

| Option | How it works | Choose it when | Cost |
|---|---|---|---|
| Editor import | An importer plugin converts the editor file to engine assets (scenes, tilemaps, prefabs) when the file changes. | Levels ship inside the build; designers work in the editor and expect automatic refresh | A plugin to maintain; generated assets can be edited by mistake |
| Runtime import | The game reads the editor's JSON at run time and builds tiles and entities in code. | User-made levels, mods, very large worlds, live reload without the engine editor, or tools that need the raw data | You write and test the loader; bigger load time |
| Own loader on `level.json` | A build step runs `level_import.py convert`; the engine reads the normalised JSON | You want one loader for Tiled and LDtk, plus the same data the checks use | Tile art and tile properties are not in `level.json`, so art still needs an importer or an atlas mapping |
| Hand-built in the engine | Designers paint in the engine's own tilemap editor | Small game, art-driven levels, no tool chain | No editor-independent data; no reachability checks unless you export a grid |

Default for a team with Tiled or LDtk: editor import for visuals and tiles, plus `level_import.py convert` and `check` in CI on the same source files. The importer builds what the player sees; the script verifies what the rules say. Section 6 compares the two.

## 2. Source of truth

1. The Tiled or LDtk file is the source. Commit it with its tilesets and images.
2. Everything generated from it (scenes, `.tres`, prefabs, `level.json`, audit specs) is derived. Mark generated files read-only in the repository README and ignore hand edits in review.
3. Never edit an imported scene to fix a level. Fix the editor file and re-import. If you must add engine-only behaviour (a script, a particle), do it in a post-import step or in a wrapper scene that instances the imported one, so re-import does not erase it.
4. Keep the map and its tileset images inside the engine project folder, with relative paths intact. Importers resolve references relative to the file.
5. Re-import must be deterministic. Two imports of the same file give the same output; commit the output only if the engine requires it.
6. When designers and engineers disagree about a wall, the editor wins; change the editor file.

## 3. Godot 4

### Native tile nodes

- Since Godot 4.3 the single `TileMap` node is deprecated and replaced by one `TileMapLayer` node per layer (confirmed in the 4.3 class reference). Use `TileMapLayer`, and plan to migrate older projects. The editor can extract a TileMap's layers into `TileMapLayer` nodes.
- A `TileSet` resource defines tile size, atlas sources, terrain sets, physics layers, navigation layers, occlusion layers and custom data layers. A tile gets collision only if the TileSet has a physics layer and that tile has a polygon on it. A common cause of "no collision after import" is a TileSet without a physics layer.
- Custom data layers on the TileSet give tiles typed properties (for example `damage`, `oneway`). Both importers below can map editor tile properties to these.
- `TileMapLayer.y_sort_enabled`, `z_index`, `collision_enabled` and `rendering_quadrant_size` control draw order, physics and batching. Stable-branch docs: https://docs.godotengine.org/en/stable/classes/class_tilemaplayer.html

### Tiled into Godot

| Route | What it is | Status (Oct 2026) |
|---|---|---|
| YATI, "Yet Another Tiled Importer" (`Kiamo2/YATI`) | Addon importing `.tmx` and `.tmj` as Godot scenes. GDScript and C# versions. MIT | Maintained: latest GitHub release v2.2.10 on 2026-10-05; README states GDScript 2.2.9 and C# 2.2.10, needs Godot 4.3.0 or higher (1.7.1 for 4.2.x), tested with Godot 4.7.2 and Tiled 1.12.2. The C# build does not support zstd |
| Tiled's built-in Godot 4 exporter | Tiled writes `.tscn` scenes directly (File, Export, or `--export-map` with the Godot format name from `--export-formats`). Since Tiled 1.10 | Shipped with Tiled; the manual says it was written for the revamped TileMap and assumes maps, scenes and tileset art share a folder hierarchy under a `.godot` project. Check whether your Tiled build emits `TileMapLayer` nodes before relying on it |
| `vnen/godot-tiled-importer` | The long-standing Godot 3 importer | Not for Godot 4: last push 2023-03-15 |
| Your own loader | Read `level.json` from `level_import.py convert` | Always available; no tile art |

YATI notes from its README:

- Place the map with all parts (PNGs, tilesets, templates) inside the Godot project, with the folder structure preserved, then (re)start the project to import.
- It recommends turning off "Use multiple threads" in Project Settings, Editor, Import, because several maps can freeze or crash the import. Treat that as a risk to test on your machine.
- Supported: all layer and object kinds, orientations, tile collisions, animations, templates and custom properties. Limits: Godot has no ellipse shapes (a capsule is used for objects, polygons approximate tile shapes), tile animation needs equidistant tiles in a row or column, and zstd is unsupported in C#.
- Custom import properties on Tiled layers, maps and objects (documented in its Reference) tune the output: set a layer's collision, z-index, y-sort and node class from Tiled.

### LDtk into Godot

| Route | Status (Oct 2026) |
|---|---|
| `heygleeson/godot-ldtk-importer` (MIT) | Imports `.ldtk` as scenes: worlds, levels (with external level support), tile layers from Tiles, IntGrid and AutoLayer, tilesets as atlases, entity placeholders and a post-import script hook. Latest tagged release 2.0.1 (2024-09-19); the repository was still receiving pushes in October 2026. README states Godot 4.1+ and LDtk 1.4.1. It builds "TileMaps" per its README, so check whether it produces `TileMapLayer` nodes on your Godot version |
| Your own loader | Read the project JSON, or `level.json`, and place tiles with `TileMapLayer.set_cell` |
| Super simple export | Load the per-layer PNGs and the IntGrid CSV; read entities from `data.json` |

The importer treats entity layers as arrays of entities, to be turned into your own scenes by placeholders or a post-import script. Plan that script early (section 7).

### Collisions in Godot

- Tile collision comes from physics-layer polygons painted in the TileSet. Importers copy Tiled tile collision shapes into them; LDtk has no tile shapes, so you need a rule: an IntGrid value becomes a full-tile square on the TileSet's physics layer (the importer's tile custom data or your post-import script), or you build collision from `level.json` rows.
- For a collision layer that should not be drawn, hide the layer or give the tiles a transparent atlas entry; keep collision-only layers named clearly.
- A moving platform made of tiles needs `use_kinematic_bodies` on its `TileMapLayer`.

### Draw order and snapping in Godot

- Layers draw in tree order. Tiled layer order maps to node order; keep the importer's order unless you set `z_index` deliberately.
- Top-down games: enable `y_sort_enabled` on the parent and on layers whose tiles must interleave with characters; set a `y_sort_origin` per tile for tall objects.
- Pixel art: set the default texture filter to Nearest (Project Settings, Rendering, Textures, Canvas Textures), set the stretch mode to `canvas_items` or `viewport` with scale mode `integer` for whole-number scaling, and turn on the 2D snap-to-pixel options under Rendering, 2D, Snap. The atlas source has a texture padding option (on by default) that reduces seams between tiles; leave it on.

## 4. Unity

### Native tile components

A Unity tilemap is a `Grid` with child `Tilemap` and `TilemapRenderer` objects. Tiles are assets painted from a tile palette. Collision uses `Tilemap Collider 2D`; adding `Composite Collider 2D` and a static `Rigidbody 2D` merges adjacent tiles into one outline, which removes seams that stop characters on flat floors. Sorting uses the renderer's sorting layer and order, or a transparency sort axis for top-down games. Manual: https://docs.unity3d.com/Manual/class-Tilemap.html

### Tiled into Unity

| Route | Status (Oct 2026) |
|---|---|
| SuperTiled2Unity (`Seanba/SuperTiled2Unity`) | Scripted importers that turn `.tmx`, `.tsx` and `.tx` into prefabs and tilemaps; updates when the map is saved. MIT. The README points to itch.io for the package download and to Read the Docs for documentation. The repository's most recent commit is from 2026-05-25 (a build against Unity 6000.4.8); the newest tag is v2.3.0; it has no GitHub release entries. Treat it as maintained at a slow pace and test against your Unity version |
| Your own loader | Read `level.json` and instantiate tiles or prefabs from editor code |
| Tiled's CSV or JSON exports plus a hand-written importer | Possible; you maintain it |

SuperTiled2Unity gives you custom property import into component fields, a "Super Map" prefab with per-layer objects, tile collision shapes and object-to-prefab replacement through its own settings. Names for these options change between versions; read its docs for the installed release.

### LDtk into Unity

| Route | Status (Oct 2026) |
|---|---|
| LDtkToUnity (`Cammin/LDtkToUnity`, package `com.cammin.ldtkunity`) | Scripted importer: drag the `.ldtk` into the project. MIT. Release 6.12.4 on 2026-10-10 (OpenUPM and GitHub); package declares Unity 2019.3 or newer. Features per its README: separate level files, entity prefab replacement, imported fields, enum script generation, collision options, animated tiles, post-import scripting and a sprite-atlas option |

It re-imports when the project saves. Entities map to prefabs through a prefab-replacement table; fields become component data. Use its post-import API (section 7) to attach gameplay.

### Collisions in Unity

- Per-tile shapes come from the tile's sprite physics shape (Tiled tile shapes and LDtk IntGrid values map through importer options).
- For IntGrid collision, importers generate collider tilemaps or colliders per layer; use `Composite Collider 2D` with the Tilemap Collider's merge operation to merge tiles into outlines.
- Set the collision layer and physics layer matrix in the project once, and make the importer's output use them.

### Draw order and snapping in Unity

- Sprite import: Pixels Per Unit equal to the tile size in pixels (16 for 16 px tiles) so one tile is one world unit; Filter Mode Point (no filter); Compression None for pixel art; Mesh Type Full Rect for atlas tiles to avoid gaps.
- Use the Pixel Perfect Camera component of the 2D renderer package you have installed (it differs between URP and the built-in renderer; check your project's package list). Tilemap seams usually come from non-integer camera positions or a wrong PPU.
- Top-down: set Transparency Sort Mode to Custom Axis with (0, 1, 0), so characters sort by Y against tall tiles.

## 5. Side by side

| Topic | Godot 4 | Unity |
|---|---|---|
| Tile node | `TileMapLayer` (one per layer) | `Tilemap` + `TilemapRenderer` under a `Grid` |
| Tile source | `TileSet` with atlas sources | Tile assets in a palette, from a sprite sheet |
| Collision | TileSet physics layer, per-tile polygons | Tilemap Collider 2D, optional Composite Collider 2D |
| Tile properties | TileSet custom data layers | ScriptableObject tile fields or importer-generated components |
| Draw order | Node order, `z_index`, `y_sort_enabled` | Sorting layer and order, sort axis |
| Pixel art | Nearest filter, integer scale, snap options | Point filter, PPU = tile size, Pixel Perfect Camera |
| Entities | Placeholders replaced by scenes | Prefab replacement table |
| Tiled importer | YATI; Tiled's TSCN exporter | SuperTiled2Unity |
| LDtk importer | heygleeson/godot-ldtk-importer | LDtkToUnity |

## 6. Parity test

An importer and the check script read the same file, but they can disagree: a tile with a collision shape in Tiled might be solid in the engine and not in the grid, or the reverse. A short parity test catches that before playtest.

1. Convert: `level_import.py convert maps/level1.tmj --out build/level1.json`.
2. Dump the engine's own solid cells from the imported scene to a file with the same rows convention (`#` solid, `.` walkable).
3. Diff the two row lists. Zero differing cells is the pass condition for a collision-by-layer setup. For collision-by-shape setups, expect differences at partial tiles and explain each one.

Godot (headless script, run with the engine's `--headless --script` options; the node path is an example):

```gdscript
extends SceneTree

func _init() -> void:
	var scene: Node = load("res://levels/level1.tscn").instantiate()
	var layer: TileMapLayer = scene.get_node("Collision")
	var cells := layer.get_used_cells()
	var w := 0
	var h := 0
	for c in cells:
		w = maxi(w, c.x + 1)
		h = maxi(h, c.y + 1)
	var rows: Array = []
	for y in h:
		var row := ""
		for x in w:
			var data := layer.get_cell_tile_data(Vector2i(x, y))
			var solid := data != null and data.get_collision_polygons_count(0) > 0
			row += "#" if solid else "."
		rows.append(row)
	var f := FileAccess.open("res://build/level1_engine_rows.json", FileAccess.WRITE)
	f.store_string(JSON.stringify(rows))
	quit()
```

Compare it with `solid.rows` of `level.json`. The grid size may differ (the engine dump stops at the last used cell); compare the overlap and pad the rest with `.`.

Unity: write an Editor script that loads the scene, walks the collider tilemap's `cellBounds`, writes the same rows, and run it with `-batchmode -quit -executeMethod`. Keep the script in the project's Editor folder.

Entities: also compare counts per role between `level.json` and the instanced scene (spawns, exits, enemies, pickups).

## 7. Post-import hooks for gameplay

Importers build tiles. Gameplay is attached afterwards, by a script the importer calls.

- Godot (LDtk importer): set the entity, tileset, level or world post-import script in the import options. Each script receives the imported node and the editor data and returns the node, so a placeholder `LDTKEntity` becomes your enemy scene.
- Godot (YATI): use the custom import properties and, where needed, a post-import script on the scene.
- Unity (LDtkToUnity): use the prefab replacement table for entities and the post-import API for levels.
- Unity (SuperTiled2Unity): map object types to prefabs and custom properties to component fields in its settings.

Keep post-import code idempotent and free of side effects, because the importer runs it on every re-import. Spawn points, exits and checkpoints are the usual first hooks; write them so a missing spawn raises an error visible in the editor, not a silent default at the origin.

## 8. Failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| No collision after import | TileSet has no physics layer, or the editor collision layer was not mapped | Add the physics layer, or choose collision by layer in importer options |
| Walls where the editor shows floor | Collision layer drawn from the wrong source (AutoLayer vs IntGrid) | Use IntGrid for collision in LDtk; a dedicated Collision layer in Tiled |
| Entities in the wrong cell | Pivot or bottom-left anchor ignored by a custom loader | Use the centre cell as `level_import.py` does |
| Seams or lines between tiles | Non-integer scale or camera position; atlas bleeding | Integer scale, snap to pixel, texture padding on, correct PPU |
| Characters catch on flat floors | Per-tile collider seams | Merge colliders (Unity composite collider); in Godot use rectangular shapes aligned to tile edges and test your controller |
| Import freezes the editor | Several maps importing in parallel (YATI notes this) | Disable multi-threaded import; split huge maps |
| Importer errors after an editor update | Format version newer than the importer | Check the importer's stated editor version, update or pin |
| Hand fixes disappear | Imported scene edited directly | Move the change to the editor file or a post-import hook |
| Level plays differently from `check` | Grid and engine collision differ | Run the parity test; fix the source |

## 9. What to re-check before relying on this file

| Fact | Where to look |
|---|---|
| YATI release and Godot support | https://github.com/Kiamo2/YATI |
| LDtk importer for Godot 4 | https://github.com/heygleeson/godot-ldtk-importer |
| SuperTiled2Unity | https://github.com/Seanba/SuperTiled2Unity and https://seanba.itch.io/supertiled2unity |
| LDtkToUnity | https://github.com/Cammin/LDtkToUnity |
| Tiled's Godot 4 export | https://doc.mapeditor.org/en/stable/manual/export-tscn/ |
| `TileMapLayer` | https://docs.godotengine.org/en/stable/classes/class_tilemaplayer.html |
| Unity Tilemap | https://docs.unity3d.com/Manual/class-Tilemap.html |
| Latest Godot stable (4.7.2 on 2026-08-18 per GitHub releases) | https://github.com/godotengine/godot/releases |

For engine project structure, templates and build commands see the core skills `engine-godot` and `engine-unity`.
