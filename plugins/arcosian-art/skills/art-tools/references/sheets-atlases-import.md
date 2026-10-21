# Sprite sheets, atlases and engine import

A sprite sheet holds the frames of one animation set; an atlas packs many unrelated sprites to cut draw calls and load time. This file covers packing settings (padding, extrusion, trimming, power-of-two, size limits), texture compression per platform, and how to import into Godot 4 and Unity. Sizes and memory figures are estimates; confirm on target hardware. Texture-size defaults match the checker `scripts/sprite_sheet.py`.

## Contents

1. Packing settings and defaults
2. Maximum texture size per platform
3. Memory arithmetic
4. Texture compression per platform
5. Import into Godot 4
6. Import into Unity
7. Packers: free and paid
8. Procedure: sheet to engine
9. Pitfalls
10. Sources

## 1. Packing settings and defaults

| Setting | Default | Why |
|---|---|---|
| Padding between frames | 2 px | Stops neighbours bleeding in under filtering and block compression. Use 1 px if you extrude edges. |
| Edge extrusion | 1 px | Repeats each frame's edge pixel into the padding; hides seams when sprites move at fractional positions. |
| Trimming | Off for animation frames; on for static sprites | Trimmed frames of different sizes need offsets; a wrong offset makes the sprite jitter. Static props benefit from the saved area. |
| Rotation | Off | Rotated frames need engine support. `sprite_sheet.py godot` rejects rotated frames. |
| Power of two | On for compressed or mipmapped textures on mobile and web | Mipmaps and some compression paths want it; most modern GPUs accept non-power-of-two. Cost: wasted area. |
| Duplicate merge | On for sheets with repeated frames | Saves space; engine-side frames reuse the same region. |
| Extra border around the sheet | 2 px | Guards against edge bleeding at the sheet border. |
| One sheet per... | Per character or per level area | Keep what loads together on one sheet. A sheet that is mostly unused still costs full memory. |

Cell size rule for pixel art: choose a base grid (16, 32 or 64 px) and keep every frame in a tag on one canvas size so the foot pivot never moves.

## 2. Maximum texture size per platform

The checker's defaults (estimates chosen to be safe on the low end of each platform, not hard limits):

| Platform | Safe maximum | Reasoning |
|---|---|---|
| mobile | 2048 | Older and low-end GPUs. 4096 is common on current phones but not universal. |
| web | 4096 | WebGL2 only guarantees 2048; 4096 is near-universal. Check `MAX_TEXTURE_SIZE` for your audience. |
| pc | 8192 | Any GPU from the last decade supports at least this (unverified for integrated GPUs; check your minimum spec). |
| console | 8192 | Current consoles support 8192 or more; confirm in the SDK documentation. |

Run `python3 scripts/sprite_sheet.py check sheet.json --platform mobile`. Override with `--max-size N` when you have measured devices. When a sheet is over the limit, split by animation set, not by arbitrary rows.

## 3. Memory arithmetic

Uncompressed RGBA8 uses 4 bytes per pixel. Mipmaps add about one third.

- 1024 x 1024 RGBA8: 4 MiB
- 2048 x 2048 RGBA8: 16 MiB
- 4096 x 4096 RGBA8: 64 MiB

Compressed block formats store a block of pixels in a fixed number of bits: ASTC 4x4 and BC7 and ETC2 RGBA are 8 bits per pixel (1 byte per pixel, so 2048 x 2048 is 4 MiB), ASTC 8x8 is 2 bits per pixel, BC1 is 4 bits per pixel. These are standard format sizes; confirm in the format specification when budgeting.

Budget before drawing: sheets in memory at once x size. State it in the art bible.

## 4. Texture compression per platform

| Platform | Preferred format | Notes |
|---|---|---|
| iOS | ASTC | Supported on Apple A8 and later; verify the minimum device. |
| Android | ASTC where supported, ETC2 as baseline | ETC2 is required by OpenGL ES 3.0; ASTC needs newer GPUs. Plan a fallback or ship ETC2 only. |
| Windows, macOS (desktop GPUs), Linux | BC7 (high quality), BC3/DXT5 (older), BC1 (opaque) | Apple-silicon Macs also support ASTC; check the engine setting. |
| Web | Basis Universal, transcoded at load | Browsers expose different formats by device: desktop typically BC, mobile ETC2 or ASTC. One Basis file serves all. |
| Console | Per platform SDK (BC on PlayStation and Xbox; ASTC or other on Switch) | Unverified here. Confirm in the SDK documentation under your agreement. |

Pixel art rules:

- Do not use lossy block compression on small, palette-limited sprites: it smears hard edges and shifts colours. Use uncompressed or lossless.
- Compress large backgrounds and painted art; keep character sprites lossless.
- Indexed or palette-swap textures must stay uncompressed with nearest filtering.
- Basis Universal has two modes (ETC1S: small, lower quality; UASTC: larger, better quality). Choose per texture type and compare on the target device.

## 5. Import into Godot 4

Files and nodes:

- `SpriteFrames` is a resource holding named animations; each frame is a texture plus a relative duration. Duration is relative: the absolute time in seconds is `relative_duration / (animation_fps * abs(playing_speed))` (Godot documentation).
- `AnimatedSprite2D` plays a `SpriteFrames` resource. Set `animation`, `autoplay`, and call `play("run")`.
- `AtlasTexture` points at a region of a sheet texture. Each `SpriteFrames` frame is usually an `AtlasTexture`. Its `region` is the rectangle in the sheet; `margin` restores trimmed space; `filter_clip` clips to the region and avoids neighbour bleed.

Generate the resource from Aseprite JSON:

```
python3 scripts/sprite_sheet.py godot hero.json --texture res://art/hero.png --out art/hero_frames.tres
```

What the generator does: one animation per tag (or `default` if the sheet has none); `pingpong` tags expanded to a forward and back list; `reverse` tags reversed; every tag loops unless it has Aseprite `repeat` 1 or you pass `--once`; per-frame durations written relative to the shortest frame in the tag, with `speed` set to 1000 divided by that shortest duration in ms. The `.tres` follows the Godot 4 text format (`format=3`, `AtlasTexture` sub-resources, `animations` array); it was written from the documented format and has not been loaded in a real engine in this repository's tests. Use `--verify` with `GODOT_BIN` set, or open the file in the editor once, before relying on it.

Import settings (select the PNG, Import dock):

- Compress mode: Lossless for pixel art; VRAM Compressed for large painted sheets; Basis Universal if you export for web and want one file for many GPUs (check the Godot version's import options).
- Mipmaps: off for 2D pixel art; on only if the sprite is scaled down a lot.
- Filter: pixel art needs Nearest. Set the project default (Project Settings, Rendering, Textures, Canvas Textures, Default Texture Filter) to Nearest, or set `texture_filter` on the node.
- Godot offers an import preset for 2D pixel art in the Import dock; check that it appears in your version and what it sets.
- Project settings for pixel games: a stretch mode that keeps pixels crisp (check "canvas_items" or "viewport" with integer scaling in your version), and snapping 2D transforms to pixel if sprites shimmer.
- VRAM compression for mobile builds must be enabled in project settings (ETC2/ASTC import) or the importer falls back; set it before exporting to Android or iOS.

## 6. Import into Unity

- Aseprite Importer (`com.unity.2d.aseprite`): drop the `.aseprite` file in the project. With more than one frame and the Animated Sprite mode, the importer can create animation clips and an Animator Controller (read-only). Package versions follow Unity versions, so check the package manager for the one matching your editor.
- PNG route: import the sheet as Sprite, Sprite Mode Multiple, open the Sprite Editor and slice by grid or automatically. Add animation clips by dragging frames. Slower than the Aseprite Importer; use it for packer output.
- Sprite Atlas: packs sprites in a project folder into atlases at build time. Use Sprite Atlas v2 (set in Project Settings, Editor, Sprite Atlas Mode); check the manual for your version. Padding and tight packing are set per atlas.
- Texture import: set Filter Mode to Point for pixel art, Compression to None, and Pixels Per Unit to the base grid size (16 or 32). Match PPU across every sprite so one tile is one unit.
- Pixel Perfect Camera (2D Pixel Perfect package, with URP's 2D renderer): set the Assets PPU and the reference resolution so pixels land on whole screen pixels. Check that your render pipeline supports it.
- Platform overrides: in the texture importer, set per-platform formats (ASTC on iOS and modern Android, ETC2 baseline, BC7 on desktop). Check the default for each build target in your Unity version.

## 7. Packers: free and paid

| Tool | Licence | Notes |
|---|---|---|
| Aseprite `--sheet-pack` | Paid editor | Built in; packs frames from many files; good for sprite-only art |
| TexturePacker (CodeAndWeb) | Commercial, with a free tier (check limits) | Many engine export formats; trimming, rotation, extrusion; CLI available |
| Free Texture Packer | Open source (unverified licence) | Web and desktop; check its export formats |
| libGDX TexturePacker | Open source (Apache-2.0, unverified here) | Java command line; the output format is libGDX-specific |
| Unity Sprite Atlas | Included with Unity | Build-time packing, no JSON |
| Godot | No sheet packer in the editor | Use an external packer, then generate `SpriteFrames` |

Pick by the format you can read: `sprite_sheet.py` reads Aseprite JSON and TexturePacker-style JSON (frames as hash or array, optional `animations` map). For other packers, convert to that shape. Run `check` on every sheet, whatever made it.

## 8. Procedure: sheet to engine

1. Decide the platform limit (section 2) and budget (section 3).
2. Export sheet and JSON from the source (see `pixel-and-painting.md`).
3. `sprite_sheet.py inspect` to read frames, tags and durations.
4. `sprite_sheet.py check --platform <target>` for each target. Fix errors; read warnings.
5. Godot: generate `SpriteFrames`. Unity: use the Aseprite Importer or the Sprite Editor.
6. Set filter, compression and PPU per section 5 or 6.
7. Play every animation in the engine at the target frame rate and compare to the source preview.
8. Record sheet size, memory and the tool versions.

## 9. Pitfalls

- Fuzzy pixels: filter left at Linear; or camera not on whole pixels.
- Colour fringes: premultiplied alpha mismatch; check the importer's alpha settings.
- Seams in tile maps and moving sprites: no padding or extrusion.
- Animation jitter: trimmed frames with a wrong offset, or mixed frame sizes in a tag.
- Mipmaps on pixel art: blurry when zoomed out.
- A 4096 sheet fine on your phone and broken on an older one.
- Android ETC2 fallback forgotten: textures render black on the device that lacks ASTC.

## 10. Sources

- Godot SpriteFrames: https://docs.godotengine.org/en/stable/classes/class_spriteframes.html
- Unity Aseprite Importer: https://docs.unity3d.com/Packages/com.unity.2d.aseprite@7.0/manual/index.html
- Aseprite CLI: https://www.aseprite.org/docs/cli/
