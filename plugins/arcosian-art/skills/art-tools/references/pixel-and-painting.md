# Pixel art and painting tools

Aseprite is the usual tool for pixel art and sprite animation, and its command line makes sheet export scriptable. LibreSprite and Pixelorama are free alternatives with fewer batch features. Krita is the free painting tool, with animation, a command-line export and Python scripting. This file gives CLI syntax checked against vendor documentation (Oct 2026), recipes for tagged sprite sheets, and palette and indexed-colour handling.

## Contents

1. Choosing between the tools
2. Aseprite command line (batch mode)
3. Aseprite recipes: sheets with tags
4. Palettes and indexed colour
5. Aseprite Lua scripting
6. LibreSprite and Pixelorama
7. Krita: animation, export, scripting
8. Verification checklist
9. Sources

## 1. Choosing between the tools

| Need | Pick | Why |
|---|---|---|
| Pixel art with tags, onion skin, slices, scripted export | Aseprite | Tags, slices and a documented CLI; Godot and Unity both import its files |
| Same, no budget | LibreSprite or Pixelorama | Free; check each for the export options you need before committing |
| Hand-painted frames, large canvases, brushes | Krita | Free; frame-by-frame animation; layers; PNG sequence export |
| Pixel art made inside the Godot editor | Pixelorama | Built with Godot; check its export formats |
| Skeletal or vector animation | See `skeletal-and-vector-animation.md` | Different workflow |

Aseprite is paid software. Its source is available under a licence that restricts redistribution; you may build it yourself for personal use. Check the current terms on aseprite.org before you rely on that. LibreSprite is a fork of the last GPL release of Aseprite and has not tracked newer Aseprite features (unverified: check the repository's last release before relying on it). Krita is GPL.

## 2. Aseprite command line (batch mode)

Run with `-b` (or `--batch`) so no window opens. Options apply to the files named after them on the command line, so order matters: put `--split-layers`, `--ignore-layer` and `--tag` before the file they affect.

| Option | Meaning |
|---|---|
| `-b`, `--batch` | Run without the UI |
| `--sheet FILE.png` | Write a sprite sheet image |
| `--data FILE.json` | Write sheet metadata; `--data=""` writes JSON to stdout |
| `--format json-hash` or `json-array` | JSON shape; hash is the default |
| `--sheet-type` | `horizontal`, `vertical`, `rows`, `columns` or `packed` |
| `--sheet-pack` | Use the packing algorithm (no value) |
| `--list-tags`, `--list-layers`, `--list-slices` | Print them; with `--data`, they add `frameTags`, `layers` and `slices` to the JSON `meta` |
| `--split-layers` | Treat each layer as its own set of cels; must come before the file |
| `--tag NAME` | Export only one tag |
| `--layer NAME`, `--ignore-layer NAME`, `--all-layers` | Choose layers (`--all-layers` includes hidden ones) |
| `--frame-range from,to` | Export a frame range |
| `--trim` | Trim transparent borders (sheet and `--save-as`) |
| `--inner-padding N` | Border inside each frame, in pixels |
| `--shape-padding N` | Gap between frames, in pixels |
| `--border-padding N` | Border around the whole sheet |
| `--extrude` | Duplicate each frame's edge pixels by one (sheet only) |
| `--merge-duplicates` | Merge identical frames into one in the sheet |
| `--ignore-empty` | Skip empty frames and cels |
| `--filename-format`, `--tagname-format` | Templates for frame and tag names in the JSON |
| `--scale N` | Resize the images named before it |
| `--color-mode` | `rgb`, `grayscale` or `indexed` |
| `--palette FILE` | Apply a palette file when saving |
| `--script FILE`, `--script-param k=v` | Run a Lua script (the docs show a single dash: `-script`) |

Notes:

- Version history matters. `--extrude` and `--palette` date from 1.2 betas; `--tag`, `--list-slices` and others are older than 1.3. Run `aseprite --version` and `aseprite --help` before writing a pipeline; flags are not guaranteed identical across versions.
- The JSON frame durations are in milliseconds. Tag direction is present in recent output (`forward`, `reverse`, `pingpong`, `pingpong_reverse`); the CLI documentation page does not describe it, so confirm on your version. `sprite_sheet.py` treats a missing direction as `forward`.
- Frame `0` is the first frame in the JSON. Tag `from` and `to` are zero-based and inclusive.

## 3. Aseprite recipes: sheets with tags

### Recipe A: one character, one sheet, tags kept

```
aseprite -b hero.aseprite --list-tags --sheet-type packed --trim \
  --shape-padding 2 --border-padding 2 --extrude \
  --sheet hero.png --data hero.json --format json-array
```

Then `python3 scripts/sprite_sheet.py check hero.json --platform mobile`.

Decisions:

- Use `--trim` only if the engine side honours the offsets (Godot: `margin` in `AtlasTexture`, written by `sprite_sheet.py godot`; Unity: sprite pivot and rect). Without trimming, every frame in a tag keeps one size and nothing jitters. For a first pipeline, leave `--trim` off.
- Padding: 2 pixels between frames is the default here. It costs about 1 to 3 per cent of sheet area for 32-pixel frames and protects against bleed from filtering and compression blocks. With `--extrude`, 1 pixel padding is also workable (estimate).
- `json-array` keeps frame order explicit. The hash form also keeps order in practice, but array form avoids relying on key order.

### Recipe B: split by layer (body, weapon, effects)

```
aseprite -b --split-layers hero.aseprite --list-tags --list-layers \
  --sheet hero_layers.png --data hero_layers.json
```

Use when the weapon or an effect must be swappable at runtime. Each layer then needs its own tag set on the engine side. Keep the layer names stable; they become part of frame names.

### Recipe C: many files into one atlas

```
aseprite -b enemies/*.aseprite --sheet-pack --sheet-type packed \
  --shape-padding 2 --sheet enemies.png --data enemies.json
```

Check that `--tagname-format` and `--filename-format` give unique names per source file, or tags from different files will collide.

### Recipe D: one PNG per tag (for tools that do not read JSON)

```
aseprite -b --tag "Run" hero.aseprite --save-as hero_run_{frame}.png
```

### Recipe E: GIF preview for review

```
aseprite -b --tag "Run" hero.aseprite --scale 4 --save-as run_preview.gif
```

Scaled previews are for review only. Ship the unscaled sheet; scale in the engine.

### Tag conventions (write these into the art bible)

- Lowercase, no spaces: `idle`, `run`, `attack_1`, `hit`, `die`.
- One tag per animation; no overlapping tags (the Godot script gives each tag its own animation, so overlap just duplicates frames).
- Set per-frame durations in Aseprite in milliseconds. Never leave a frame at 0.
- A one-shot animation: set the tag repeat to 1 in Aseprite (recent versions) or list it with `--once` in `sprite_sheet.py godot`.

## 4. Palettes and indexed colour

Why: a locked palette is the cheapest style lock. It also lets you swap colours at runtime (hit flash, team colours) with a lookup.

1. Save the project palette as a `.gpl` or a PNG strip, named in the art bible, with the colour count (16 to 32 colours is typical for retro looks; estimate, not a rule).
2. Draw in indexed mode if you need palette-swap shaders. Indexed sprites keep palette indices; the engine must sample them as exact values (no filtering, no compression, no mipmaps). In Godot this is a shader on a nearest-filtered texture; in Unity, Point filter and no compression.
3. To force a whole folder onto the palette: `aseprite -b old.png --palette locked.gpl --color-mode indexed --save-as new.png`. Check the result by eye. Mapping to the nearest palette colour can merge two shades you meant to keep.
4. For RGB output with a locked palette, export RGB and run an automated check that every opaque pixel colour is in the palette (a ten-line Python script with Pillow, or compare against the palette file). Do this in CI for any shipped sprite.
5. Save palettes in the repo (`art/palettes/`) with the source licence if the palette came from a third party (for example a palette shared on a community site: record the author and terms).

Pitfall: when a sprite is indexed and exported to PNG, the PNG may keep an index plus palette. Godot and Unity import it as RGBA, which is fine; a palette-swap shader needs a separate indexed or grey-ramp texture. Decide this before drawing.

## 5. Aseprite Lua scripting

Run with `aseprite -b --script tools/export.lua` (add `--script-param key=value` and read it from `app.params.key`). The scripting API is documented in the Aseprite API repository. Keep scripts small and in version control. Example that lists tags:

```lua
local spr = app.sprite
if not spr then return print("no sprite open") end
for _, tag in ipairs(spr.tags) do
  print(tag.name, tag.fromFrame.frameNumber, tag.toFrame.frameNumber)
end
```

Use scripts for things the CLI cannot do: rename layers, check frame durations are non-zero, assert canvas size, reject files with colours outside the palette. Read any script before running it, including ones from forums: a Lua script can use the file system and, in some builds, run other programs.

## 6. LibreSprite and Pixelorama

- LibreSprite: free and GPL, a fork of the last GPL Aseprite. Expect a similar interface and its own CLI. Verify the CLI options you need with `libresprite --help` on your build; do not assume the Aseprite flags above exist.
- Pixelorama: a free open-source pixel-art tool written in Godot. Check its current export options (sprite sheets, animated PNG, GIF) in its own documentation before planning a pipeline around it. Whether it offers an unattended CLI export is unverified here.
- Both can export a PNG sheet. If a tool does not write Aseprite-style JSON, drive the sheet layout by a fixed grid and write the tag list by hand (a small JSON you can feed to `sprite_sheet.py`).

## 7. Krita: animation, export, scripting

- Krita has frame-by-frame animation on a timeline. Save as `.kra`.
- Command-line export (checked against the Krita manual, Oct 2026): `krita file.kra --export --export-filename out.png` exports the image; the file extension picks the format.
- Animation export: `krita --export-sequence --export-filename frames.png file.kra` (added in 4.2) writes a PNG sequence; if the file has no animation Krita prints a message and does nothing. The manual page documents no frame-range or tag options for this command; use the in-app Render Animation dialog for those.
- Krita has no Aseprite-style tags. Assemble the sheet from the sequence with a packer (`sheets-atlases-import.md`) and write the tag list yourself.
- Python scripting (PyKrita) is built in. The Scripter dialog and the plugin system exist; check the current Krita manual, "Krita Scripting", for the API for your version. Python use in unattended runs has restrictions you should test on your install (unverified here).
- Hand-painted frames get large: a 512-pixel frame x 12 frames x 8 animations will not fit a mobile-safe 2048 sheet. Use the checker and plan atlases early.

## 8. Verification checklist

- `aseprite --version` recorded in the pipeline notes; flags above tested against it.
- Sheet and JSON regenerate from the `.aseprite` source with one command.
- `sprite_sheet.py check` passes for each target platform.
- Palette check passes (if palette-locked).
- Every tag has non-zero durations and one frame size.
- Source `.aseprite` files stored in the repo (provenance), not only the PNG.

## 9. Sources

- Aseprite CLI: https://www.aseprite.org/docs/cli/
- Krita command line: https://docs.krita.org/en/reference_manual/linux_command_line.html
