# Asset Specs and Marketing Art

This file is the production-spec companion to the style bible: how big to author assets, how to pack and name them, how to build resizable UI, how to prepare sprite sheets, and what marketing art a mobile game needs (icon, store screenshots, key art, preview video). Stable engineering rules sit in the first sections; store-dimension and store-policy details are volatile and are isolated in a dated section near the end. Authoring rules here are studio heuristics, so confirm them against the target engine's current docs and the project's perf budget before hard-coding them in a contract.

## Contents

1. [Resolution strategy](#1-resolution-strategy)
2. [Safe areas and aspect ratios](#2-safe-areas-and-aspect-ratios)
3. [Authoring scale and texture sizes](#3-authoring-scale-and-texture-sizes)
4. [Atlases](#4-atlases)
5. [Naming and folder conventions](#5-naming-and-folder-conventions)
6. [Nine-slice and resizable UI](#6-nine-slice-and-resizable-ui)
7. [Sprite sheets and animation frames](#7-sprite-sheets-and-animation-frames)
8. [Pivots, padding, trim](#8-pivots-padding-trim)
9. [Icons: in-game and app icon](#9-icons-in-game-and-app-icon)
10. [Store screenshots](#10-store-screenshots)
11. [Key art and feature graphics](#11-key-art-and-feature-graphics)
12. [Preview video](#12-preview-video)
13. [Asset checklist before import](#13-asset-checklist-before-import)
14. [Volatile facts (as of Oct 2026 - verify)](#14-volatile-facts-as-of-oct-2026---verify)

---

## 1. Resolution strategy

Pick one **reference resolution** (portrait phones: 1080 x 1920 is the common authoring target; landscape 1920 x 1080) and author all UI and 2D art against it. The engine scales to the device. Decide scaling mode once.

| Decision | Options | Recommendation |
|---|---|---|
| Stretch mode | Fixed canvas with letterbox, expand/keep-aspect, scale-with-screen-size (Unity Canvas Scaler) | UI: scale with screen size matching width or a blend; gameplay: keep the playfield inside a guaranteed aspect range and extend the background |
| Pixel art | Integer scaling only | Choose a base resolution where the target phones give integer or near-integer multiples; otherwise accept letterbox bars or non-integer filtering with a clean sharpening step |
| 3D render resolution | Native, or render scale 0.7-1.0 | Make render scale a quality setting; UI stays at native resolution |
| Asset density | One high-res set, mips down | One set authored at 1x of the reference res; produce a 2x only for hero art or for tablets if needed |

Worked example: reference 1080 x 1920. A button authored at 540 x 160 occupies half the width. On a 720 x 1280 phone it renders at 360 x 107, still sharp because the source is larger than the display size. On a 1440 x 3120 phone it upscales 1.33x, so avoid fine 1 px lines in UI art or use vector/SDF for icons and text.

Rule: author at the largest size that will be displayed 1:1 on the highest common tier; never author at the size of the lowest tier and upscale.

## 2. Safe areas and aspect ratios

- Modern phones are tall (around 19.5:9 to 20:9) with notches, cut-outs, rounded corners and gesture bars; tablets and foldables are closer to 4:3 or square. Read the real safe-area insets at runtime.
- Keep the **playfield** inside a safe central region and let **backgrounds bleed** to a larger canvas (for example author a 1080 x 2400 background for a 1080 x 1920 playfield).
- Keep critical HUD out of the corners and out of the bottom gesture strip. See `skills/mobile-ux` for thumb zones.
- Test matrix: one short narrow phone, one tall phone, one tablet, one landscape, one with a large cut-out.

## 3. Authoring scale and texture sizes

| Asset class | Typical authored size at reference res | Texture size guidance | Notes |
|---|---|---|---|
| Item / pickup icon | 128-256 px square | Pack into atlas | Keep silhouette readable at 64 px |
| Character sprite (static) | 512-1024 px tall | Atlas page 2048 | Larger only for hero or portrait art |
| Character portrait | 1024-2048 px | Separate texture, streamed | Load on demand, never in the main atlas |
| UI panel / frame | 9-slice source 96-192 px | UI atlas | Corner radius rule from the bible |
| Background (parallax layer) | 1.2-2x screen size | One texture per layer, compressed | Check overdraw |
| Tileset tile | 64 / 128 px | Atlas with padding | Extrude edges to avoid seams |
| Particle texture | 64-256 px | Shared VFX atlas or flipbook | See technical-art skill |
| App icon master | 1024 x 1024 | Not in game | Export all platform sizes from the master |

Powers of two are preferred for GPU compression and mipmaps; many compressed formats work with non-power-of-two dimensions but are block-aligned (4 x 4 or 6 x 6, etc.), so multiples of 4 are the floor. Detailed format guidance lives in `skills/technical-art/references/texture-and-3d-pipeline.md`.

## 4. Atlases

Goals: fewer texture binds and draw calls, controlled memory, predictable loading.

| Rule | Reason |
|---|---|
| Group by use-together: one atlas per screen or per feature (HUD, battle, shop, per-biome) | Batching only works within an atlas; loading one atlas must not drag in unrelated art |
| Keep a shared atlas for always-on UI and a separate one per mode | Avoid loading and unloading churn |
| Page size 2048 x 2048 is the common ceiling for broad device support; 4096 only when the minimum device tier is known to handle it | Memory and compatibility |
| Padding 2 px for bilinear filtering, plus edge extrusion for tiles; 4 px for mipmapped textures | Prevents bleeding at distance and seams |
| Do not mix compressed-format-incompatible content (hard-edged UI vs smooth gradients) when quality needs differ | Compression artifacts differ per content |
| Keep alpha and non-alpha art on separate pages when the format differs | Saves memory (no alpha channel) |
| Rotate sprites in the packer only if the engine supports it and your tooling does not break trimming | Rotation saves space but complicates debugging |
| Rebuild atlases in CI from source folders; never commit hand-packed pages without the source | Reproducibility |

Packing tools: engine-native (Unity Sprite Atlas, Godot import and AtlasTexture), or a standalone packer in CI. The studio's `image_post.py atlas` command packs simple cases (`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/image_post.py atlas --in <sprite files> --out atlas.png --max-size 2048 --padding 2`, which also writes `atlas.json`). Estimate memory before committing: uncompressed RGBA is 4 bytes per pixel, so a 2048 x 2048 page is 16 MiB uncompressed; compressed formats cut this by a factor depending on format (see texture file).

Memory budget formula for a screen: sum over pages (width x height x bytes-per-pixel-at-format x 1.33 if mipmapped). Compare the sum to the screen's budget in the contract.

## 5. Naming and folder conventions

Conventions exist so tooling (atlas packers, manifests, AI batch jobs) can rely on paths.

```
assets/
  _bible/                 style sheets, references (not shipped)
  characters/<id>/        <id>_<state>_<dir>_<frame>.png
  items/<category>/       item_<name>_t<tier>.png
  ui/
    atlas_hud/            ui_<widget>_<state>.png
    atlas_menu/
    9slice/               ui_panel_<name>_9s.png
  env/<biome>/            env_<biome>_<element>_<variant>.png
  vfx/                    vfx_<name>_<frames>f.png   (flipbooks: vfx_hit_4x4.png)
  icons/                  icon_<name>_<size>.png
  marketing/              store_*, keyart_*, preview_*
```

Rules:
- lower_snake_case, ASCII only, no spaces; state and direction are suffixes in a fixed order.
- Frame numbers zero-padded to the largest count: `walk_00`, `walk_01`.
- A manifest entry (`id`, `path`, `source`, `provider`, `licence`, `bible_version`) exists for every shipped asset; see `skills/ai-asset-pipeline/references/post-processing-and-provenance.md`.
- Variants use `_a`, `_b`; tiers `_t1`..; localizations `_<lang>`; density `@2x` only if the engine needs it.
- Source files (layered PSD, Aseprite, Spine, Blender) live under `source/` mirroring `assets/` and are never imported by the engine.

## 6. Nine-slice and resizable UI

A 9-slice (9-patch) image keeps its corners and stretches or tiles the edges and centre. It is the default for panels, buttons and speech bubbles.

Authoring checklist:
1. Draw at the reference resolution at the smallest practical size (for example 96 x 96) with corners at least as large as the largest decoration.
2. Define borders as left/top/right/bottom in source pixels. Record them in the filename or a sidecar (`ui_panel_card_9s_24-24-24-24`) so import rules are reproducible.
3. The stretchable centre must be pattern-free or tile cleanly. Gradients in the centre should be vertical only if you stretch vertically.
4. Drop shadows and outer glows belong outside the slice region (keep padding) or as a separate layer, otherwise they stretch.
5. Provide hover, pressed, disabled variants with identical borders.
6. Decide stretch vs tile for edges: stretch for flat colour, tile for patterns, and test at three sizes (small, typical, full width).
7. Minimum touch target: keep the button hit area at the platform guideline size or bigger; art may be smaller than the hit area but never the opposite (see `skills/mobile-ux`).

Engine notes: Unity Image type "Sliced" uses sprite borders from the Sprite Editor; Godot uses `NinePatchRect` or a `StyleBoxTexture` with margins. Both support tiling modes for edges.

## 7. Sprite sheets and animation frames

| Decision | Guidance |
|---|---|
| Cell size | Same size for every frame of a character, with the pivot at the feet or centre-of-mass; trimmed sprites need stored offsets |
| Layout | Pack into the atlas; avoid very wide strips on mobile (texture dimension limits and cache locality) |
| Frame budget | Idle 4-8 frames, walk/run 6-10, attack 5-10, hit 2-4 (heuristics); full-motion animation costs memory fast |
| Timing | Hold keyframes longer; use animation on twos for a hand-drawn feel; reuse mirrored frames for left/right where the design allows |
| Directional sets | 4 or 8 directions multiply cost by that factor; ask whether side-view mirrored is enough |
| Frame rate | Author 12, 15 or 24 fps timing; do not tie to the render frame rate |
| Memory | Frames x cell area x bytes; 24 frames at 256 x 256 RGBA is 6 MiB uncompressed; compress and trim |
| Skeletal alternative | When frame count is large and costume swapping is needed, use skeletal 2D (layered parts) and keep parts on one atlas |

AI-generated sprite sheets: grids often come out with inconsistent cell alignment, background colours (green or magenta) and drifting proportions. Always run a post step: key out the background, slice into cells, align pivots by a fixed anchor (feet y and body centre x), compare silhouettes between frames, and reject frames whose silhouette area varies beyond a tolerance (start at about 10% and tune). See `skills/ai-asset-pipeline/references/post-processing-and-provenance.md`.

## 8. Pivots, padding, trim

- Pivot for characters: bottom-centre (feet) so scaling and flipping behave; for items on a grid, centre.
- Keep a transparent margin of 1-2 px around trimmed sprites to avoid bilinear edge clipping, or rely on atlas padding.
- Trim transparent borders in the packer but store original size and offset so animations do not jitter.
- Premultiplied alpha: choose one convention per project to avoid dark fringes. Straight alpha PNG sources are safest; the importer or packer premultiplies when the engine expects it.
- Colour-bleed fix: dilate RGB values into fully transparent pixels in sources so mip and filter blends do not show dark or white halos.

## 9. Icons: in-game and app icon

**In-game icons** (currency, items, skills): author at 128 or 256 px, design for legibility at 48-64 px, one silhouette per concept, same grid and corner rule as the bible, a visible shape that works in greyscale.

**App icon rules (stable principles):**
- One idea, one focal element, no text or at most one letter or very short mark.
- High contrast against both light and dark home screens; avoid pure white or pure black backgrounds that blend with the wallpaper.
- Fill the canvas to the edges in the master; the platform masks it (rounded square on iOS, adaptive shapes on Android), so keep the key element within the central safe region.
- Avoid borders and drop shadows baked into the master; the OS adds its own treatment.
- Test the icon at the smallest size on a busy wallpaper, in greyscale, and next to ten competitor icons (store test, see style guide).
- Android adaptive icons use separate foreground and background layers with a safe zone; verify layer size and safe-zone numbers in the current Android docs.
- iOS expects a single large master with no transparency; verify current requirements in the Apple docs.
- Icon A/B testing in stores (custom store listings and product page optimization tools) is how the winner is chosen after launch; generate three to five variants with a clear single variable each (character, colour, expression, background, framing).

Icon generation procedure for AI: generate 12-16 candidates at large size from a locked prompt, pick finalists with the tournament method (`references/art-critique-rubric.md`), clean up by hand (alignment, edge, gradient banding), test the thumbnail, and export all platform sizes from the master with a script.

## 10. Store screenshots

Purpose: communicate the core loop and the emotional promise in two seconds each; the first two or three screenshots do most of the work because they appear in search results.

Structure of a strong set:
1. **Hook**: the core action in progress, one headline of 3-6 words, hero character or a satisfying moment.
2. **Core loop clarity**: the main mechanic with a labelled example.
3. **Progression or collection**: shows depth without clutter.
4. **Social, events, or modes** if relevant.
5. **Closing proof**: ratings, awards or a content-count line only if true.

Rules:
- Use real gameplay frames with HUD, composed into a frame with a headline; avoid screenshots that are all marketing art and no gameplay, because stores and players distrust them.
- One idea per screenshot; large high-contrast headline text that survives thumbnail size; consistent background and typography across the set.
- Localize headline text for the top markets; keep text out of the safe-crop area if a store crops.
- Do not show features or content that do not exist, and do not use fake ratings, fake player counts or fake awards; store review and consumer law both punish this (see `skills/legal-ethics`).
- AI-generated art in marketing material may need disclosure on some stores; check the volatile facts in `skills/ai-asset-pipeline/references/post-processing-and-provenance.md`.
- Produce them through a template (a single layered file or a script) so a new language or a new hero is a data change, not a redesign.

## 11. Key art and feature graphics

| Item | Purpose | Procedure |
|---|---|---|
| Key art (hero illustration) | Brand image, store featured, ads, social | One composition with a clear focal character, strong silhouette, brand colour, space for the logo and for platform crops |
| Feature graphic / banner (Google Play) | Top of the store page | Design for a wide crop, keep the focal subject centred, assume text is small |
| Logo | Recognition | Readable at small size, one or two colours, works on light and dark |
| Ad creatives | UA tests | Derive from key art; test several hooks (see `skills/marketing-ua`) |

Key-art workflow: thumbnails (6-10 compositions as sketches or low-fidelity AI) -> choose via comparative review -> high-resolution generation or paint-over -> human finishing (hands, text, edges, logo placement) -> crops for each placement -> disclosure and licence check -> sign-off by the human art owner (taste checkpoint).

Composition rules: rule of thirds or a single dominant diagonal, focal element high-contrast against the surroundings, leave a quiet area for text, avoid clutter near crop edges, maintain palette discipline from the bible.

## 12. Preview video

- Open on the hook within the first 2-3 seconds; show the actual game, not a cinematic that is not in the game.
- Portrait for portrait games unless the store slot demands otherwise; subtitles on because many viewers have sound off.
- Pace: 15-30 seconds is a common target for the store; keep the structure hook, core loop, progression, payoff, call to action.
- Capture from a real build via a deterministic replay (use the playtest runner to script a good-looking run) so footage is reproducible across versions.
- Audio: music and a few punchy SFX; check licences of every audio and art element; do not include copyrighted music.
- Export at the highest resolution the store accepts, then check file size and encoding limits.
- Provide variants for ads: 6, 15 and 30 second cuts from the same footage.

## 13. Asset checklist before import

- [ ] Right size and format for its class (section 3); dimensions multiple of 4 or power of two
- [ ] Transparent background clean, no fringe, premultiply convention respected
- [ ] Pivot and padding set; frames aligned; cell size uniform
- [ ] Palette audit passed for gameplay-critical pairs
- [ ] Named per convention; manifest entry written with provenance and licence
- [ ] Bible version recorded; critique score above the threshold for the milestone tier
- [ ] Perf: texture memory contribution computed against the screen budget
- [ ] No third-party trademarked or copyrighted material; no identifiable real persons or logos

## 14. Volatile facts (as of Oct 2026 - verify)

Store graphics dimensions, counts, safe areas, and policy change often. This skill deliberately does not hard-code them. Look them up at build time and store the verified numbers in the project's `.gamestudio/` store-asset checklist.

| Topic | What to verify | Official source to search (no URL pinned; verify) |
|---|---|---|
| App Store screenshot sizes and counts per device class | Required pixel sizes, maximum count, whether smaller sets scale | Apple App Store Connect Help, screenshot specifications |
| App Store app icon | Master size, transparency rules | Apple Human Interface Guidelines, App icons |
| Google Play graphics (icon, feature graphic, screenshots) | Pixel sizes, aspect rules, file limits, count | Google Play Console Help, preview assets |
| Android adaptive icon safe zone | Layer size and safe zone | Android Developers, adaptive icon design |
| Preview video specs (both stores) | Length, resolution, orientation, size cap | Same App Store Connect and Play Console pages |
| AI-content disclosure for marketing material (Steam, stores) | What must be disclosed | Steamworks content survey and each store's current policy page; see the ai-asset-pipeline provenance file |

When a number is needed in a deliverable, cite the page and the date you checked in the file next to the number.
