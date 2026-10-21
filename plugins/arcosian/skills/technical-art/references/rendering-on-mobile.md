# Rendering on Mobile

How mobile GPUs actually spend a frame, and what that means for art and engineering decisions: tile-based rendering, memory bandwidth, batching and draw calls, overdraw, post-processing cost, render scale, and the choice of graphics API and renderer (Vulkan, Metal, OpenGL ES) in Godot and Unity. The recurring theme is that mobile is limited by bandwidth, fill and heat rather than raw arithmetic, so the cheapest frame is the one that touches the fewest pixels the fewest times. Numbers are planning heuristics; always confirm with a GPU profiler on the lowest-tier target.

## Contents

1. [The mobile frame budget](#1-the-mobile-frame-budget)
2. [Tile-based GPUs](#2-tile-based-gpus)
3. [Bandwidth](#3-bandwidth)
4. [Draw calls and batching](#4-draw-calls-and-batching)
5. [Overdraw and fill rate](#5-overdraw-and-fill-rate)
6. [Transparency and sorting](#6-transparency-and-sorting)
7. [Lighting and shadows](#7-lighting-and-shadows)
8. [Post-processing cost](#8-post-processing-cost)
9. [Render scale and resolution strategy](#9-render-scale-and-resolution-strategy)
10. [Graphics APIs and renderers](#10-graphics-apis-and-renderers)
11. [Thermals, battery and frame pacing](#11-thermals-battery-and-frame-pacing)
12. [Profiling procedure](#12-profiling-procedure)
13. [Quality tiers](#13-quality-tiers)
14. [Decision tables](#14-decision-tables)
15. [Worked example](#15-worked-example)

---

## 1. The mobile frame budget

Frame time targets: 33.3 ms for 30 fps, 16.6 ms for 60 fps, 8.3 ms for 120 fps. Do not spend the whole budget: sustained load heats the phone and the OS throttles clocks, so a game that runs at 16 ms cold may run at 25 ms after ten minutes. Plan for **70 percent of the budget** at sustained load (about 11.5 ms for 60 fps) on the lowest supported device, and cap frame rate (30 or 45 fps, or 60 with a lighter scene) when the genre does not need more.

| Budget item | Typical share of a 60 fps frame (heuristic) |
|---|---|
| Game logic and scripts (CPU) | 2-4 ms |
| Physics and animation (CPU) | 1-3 ms |
| Render submission (CPU draw calls) | 2-4 ms |
| GPU geometry and opaque pass | 3-5 ms |
| GPU transparent and VFX | 1-3 ms |
| GPU post-processing and UI | 1-3 ms |
| Headroom for thermal and spikes | remainder |

Identify first whether the game is CPU-bound or GPU-bound: reduce render resolution; if the frame time falls, you are GPU (fill) bound; if not, you are CPU or submission bound.

## 2. Tile-based GPUs

Most mobile GPUs divide the screen into small tiles, render each tile in fast on-chip memory, and write the finished tile to main memory once. Consequences:

- **Good**: opaque overdraw is cheap on some architectures that do hidden-surface removal inside a tile (deferred-style rejection); depth and MSAA samples live on chip and cost little bandwidth if they are not stored.
- **Bad**: anything that forces the GPU to **flush a tile to memory and reload it** is expensive: reading the framebuffer mid-frame (grab pass, screen-texture refraction), switching render targets repeatedly, and reading depth as a texture.
- **Load and store actions**: tell the API not to load the previous contents (clear or don't-care) and not to store attachments you do not need later (depth, MSAA). Unity URP and Godot Mobile manage most of this; custom render passes must set these correctly.
- **Render pass count**: each pass that writes a full-screen target costs a full read and write of that target. Fewer passes beat cheaper passes.
- **Binning cost**: geometry is processed twice (binning, then shading), so very high vertex counts hurt more on tile-based GPUs than on desktop; keep vertex counts reasonable and avoid sub-pixel triangles.
- Behaviour differs between GPU vendors and generations; do not assume that opaque overdraw is free on all of them. Sort opaque front to back anyway (engines do this by default).

## 3. Bandwidth

Memory bandwidth is the shared, power-hungry resource. Every full-screen texture read or write counts.

Estimate per full-screen pass: `bytes = width x height x bytes_per_pixel x (reads + writes)`. At 1080 x 2340 with an RGBA8 target (4 bytes) that is about 10 MB per read or write; at 60 fps, one read plus one write is about 1.2 GB/s. Several such passes in a frame explain heat and throttling.

Reduce bandwidth:
- Compressed textures (see `references/texture-and-3d-pipeline.md`), mipmaps for 3D, and small atlases.
- Lower precision render targets (RGB565 or R11G11B10 where acceptable, 8-bit instead of half-float unless HDR is needed).
- Avoid HDR rendering unless the look needs bloom; HDR targets double the bandwidth.
- Avoid MSAA beyond 2x, and prefer 2x or none with clean art and a sharp UI; keep MSAA samples on chip (do not resolve to memory more than once).
- Fewer, larger-scope passes; combine post effects into one shader.
- Do not copy the screen (grab pass) per object; do it once per frame at most, at reduced resolution.
- Vertex data: quantize attributes, drop unused streams.

## 4. Draw calls and batching

CPU cost per draw call (state changes, uniform uploads, driver overhead) is a common bottleneck on mobile, especially with many unique objects or on OpenGL ES. Planning targets for visible draw calls (heuristics): low tier 100-200, mid 200-400, high 400-1000 (fewer for 120 fps targets).

| Technique | Unity | Godot 4 | Conditions |
|---|---|---|---|
| Shared materials | Same material instance | Same material resource | Foundation of all batching |
| SRP Batcher | Yes (URP/HDRP), shader must declare a per-material constant buffer | n/a | Reduces CPU cost of material setup |
| GPU instancing | Enable on material; per-instance data via arrays or property blocks | MultiMeshInstance3D | Many copies of one mesh and material |
| Static batching | Mark static; merges meshes (memory cost) | Merge meshes at import or bake; MeshInstance merging in the editor | Static scenery |
| Dynamic batching | Small meshes, limited vertices; often not worth it with SRP Batcher | n/a | Rarely the right tool now |
| Sprite/2D batching | Sprite Atlas, same material | CanvasItem batching in the 2D renderer, shared texture and material | Pack sprites by atlas, avoid interleaving different atlases in the draw order |
| Mesh combining at runtime | Manual combine | Manual combine | Particle-like sets of static objects; mind culling granularity |
| UI | Separate canvases for static and dynamic UI; avoid rebuilding large canvases per frame | Separate CanvasLayers; avoid redraw of big containers | UI rebuilds are a frequent mobile spike |

Batch-breaking causes to avoid: unique materials per object, material property changes that require a new material instance (use property blocks or instance uniforms), mixing atlases in a draw order, alternating transparent and opaque order, scissor and mask changes in UI, and per-object real-time shadow settings.

2D specifics: draw order by layer and atlas; sprites from the same atlas in contiguous order batch to one call; a single text or sprite from a different atlas between them breaks the batch. Arrange sorting layers so that same-atlas sprites are adjacent.

## 5. Overdraw and fill rate

Overdraw is the number of times a pixel is shaded per frame. A full-screen 1080 x 2340 frame is about 2.5 million pixels; each additional full-screen layer adds that many shaded pixels and the bandwidth to blend them.

| Source | Typical impact | Fix |
|---|---|---|
| Full-screen backgrounds stacked (parallax layers, gradients) | 3-6 layers of full-screen alpha | Merge layers into one texture where they do not need independent motion; use opaque for the bottom layer |
| Large transparent particles (smoke, fog) | Dominant VFX cost | Trim quads to visible shape, cap size, reduce layers, fade early |
| UI panels over the whole screen | Several layers | Opaque base panel, avoid translucent stacking |
| Transparent 3D objects (glass, foliage) | Variable | Alpha-cutout with tight meshes, or opaque geometry; avoid sorting-dependent soft edges |
| Post-processing | Whole-screen passes | See section 8 |
| Large sprites with transparent margins | Pays for invisible area | Tight-fit meshes (sprite mesh mode instead of full quad) |

Tools: engine overdraw views (Unity Scene view draw mode Overdraw; Godot Debug Draw "Overdraw" in the 3D viewport), plus vendor GPU profilers that report shaded pixels or fill cost. Targets (heuristic): average overdraw under 2x for the whole scene on low tier, with VFX contributing at most 1x extra.

Opaque-first rule: render everything that can be opaque as opaque; opaque draws are depth-sorted front-to-back so hidden pixels are rejected early on GPUs that do so; transparent draws are sorted back-to-front and always shade every covered pixel.

## 6. Transparency and sorting

- Alpha test (`discard`/alpha clip) disables early depth rejection on some GPUs for that draw; prefer it only for small objects (foliage cards), and cull aggressively.
- Alpha blend sorts per object, not per pixel; intersecting transparent objects show popping; avoid by splitting meshes, adding sort offsets, or using additive blending for lights.
- Additive blending for light-like effects (sparks, glow) is order-independent and cheap to sort; alpha blending for smoke and dust.
- Premultiplied alpha lets one material support both blends.
- Soft particles (depth fade at intersections) require depth texture reads, which on tile-based GPUs can force a flush or an extra pass; avoid on low tier. Fake with a vertex-colour fade or push particles away from surfaces.
- Order UI after the world and keep UI transparency shallow.

## 7. Lighting and shadows

| Option | Cost | Use |
|---|---|---|
| Unlit / baked / matcap | Lowest | Default for stylized mobile games |
| One real-time directional light, no shadows | Low | Characters in a fixed-lit scene |
| Additional real-time lights | Per-pixel cost per light | Keep to 1-2 on mid tier; none on low |
| Lightmaps and light probes | Baked, low runtime cost | Static environments with some dynamic objects |
| Blob shadow (projected quad or decal) | Very low | Default for characters on mobile |
| Real-time shadow map | High (extra pass, bandwidth, fill) | Hero shots or high tier only; one cascade, small resolution (512-1024), short distance, soft filtering off on low |
| Screen-space ambient occlusion | High | High tier only; prefer baked AO |
| Reflection probes / SSR | High | Baked cubemap or matcap fakes |

Godot: the Mobile renderer limits lights per object and supports a smaller feature set than Forward+; the Compatibility renderer targets older devices and web. Unity URP: set additional-lights to per-vertex or disabled on low tier, disable shadow cascades beyond one, and set the shadow distance to the playable area.

## 8. Post-processing cost

Each full-screen effect reads and writes the screen: bandwidth and fill. Typical effects ranked by relative cost on mobile:

| Effect | Relative cost | Mobile guidance |
|---|---|---|
| Colour grading (LUT) | Low (one pass, tiny LUT) | Usually acceptable; combine with tone mapping |
| Vignette, simple tint | Low | Can be folded into the UI or the final pass |
| FXAA / cheap AA | Low-medium | Preferred over MSAA when affordable |
| Bloom | High (multiple downsample/upsample passes) | Use sparingly on mid and high; fake with glow sprites on low |
| Depth of field | High | Avoid; fake with art |
| Motion blur | High | Avoid |
| SSAO | High | Avoid; bake AO |
| Screen-space reflections | Very high | Avoid |
| Chromatic aberration, film grain | Low-medium | Optional pulse effects only |
| Distortion / heat haze | Medium-high (grab) | Single full-screen distortion for shockwaves, short duration |

Rules: one combined post shader beats several separate passes; run bloom at a quarter resolution and cap the number of mip steps; apply effects only when needed (a shockwave distortion only during the shockwave); make all post effects tier-gated and test the game with them all off to confirm it is still readable; never rely on bloom to make things look bright without a non-bloom fallback.

## 9. Render scale and resolution strategy

- Modern phones have far more pixels than a casual game needs. Rendering the 3D world at a scale of 0.6-0.85 of native and compositing the UI at native resolution gives large savings with small quality loss, especially for stylized art.
- Make **render scale** a quality setting and a dynamic knob: Unity URP has a render scale and dynamic-resolution support; Godot 4 has 3D scaling (`scaling_3d/scale` and modes such as bilinear or FSR where supported). Keep the UI in its own layer at native resolution.
- Dynamic resolution: when GPU frame time exceeds the target for several frames, step the scale down in small increments (for example 5 percent) and recover slowly when there is headroom, with hysteresis to avoid oscillation.
- Pixel-art games: render to a low-resolution target at an integer ratio and scale up with point filtering; this is both a look and a cost saving.
- Cap frame rate by scene: menus at 30 fps, gameplay at the target; the OS will cool down and save battery.
- Anti-aliasing at lower render scale costs less; test on-device for shimmer.

## 10. Graphics APIs and renderers

| API | Platform | Notes |
|---|---|---|
| Metal | iOS (and macOS) | The only API on iOS; engines abstract it; shader compilation hitches possible on first use, so warm up shaders |
| Vulkan | Android (and desktop) | Lower CPU overhead than OpenGL ES, better multithreading; driver quality varies on some older or low-end devices, so provide a fallback |
| OpenGL ES 3.x | Android (older devices), Godot Compatibility | Widest reach on old hardware; higher CPU overhead and weaker feature set |

Engine choices:

| Decision | Godot 4.x | Unity 6 |
|---|---|---|
| Renderer for modern phones | Mobile renderer (Vulkan/Metal) | URP with Vulkan or Metal |
| Renderer for old or low-end phones, widest reach | Compatibility renderer (OpenGL ES 3) | URP on GLES3 as a fallback, or ship a separate lower tier |
| 2D games | Compatibility or Mobile renderer; 2D draw is cheap in both | URP 2D renderer |
| Avoid on mobile | Forward+ (desktop-class features) | HDRP |
| Shader warm-up | Pre-compile via ubershaders and pipeline caches; render hidden meshes at load | Shader variant collections and graphics pipeline warm-up at load |

Policy: pick the lowest-common-denominator renderer that still delivers the art direction; choose by **the minimum supported device**, because switching renderers late changes shaders, lighting and post effects. Test every release on at least one low-tier Android device and one older iPhone.

## 11. Thermals, battery and frame pacing

- **Thermal throttling**: sustained GPU or CPU load raises temperature; clocks drop; frame time rises after minutes. Test with 15-30 minute sessions, not 30 second captures.
- **Battery**: players notice drain; reduce load in menus and idle states, cap frame rate, avoid unneeded full-screen effects.
- **Frame pacing**: consistent frame intervals matter more than a high average; use the platform's swap interval and the engine's frame-pacing support (Android Frame Pacing library, Unity's Adaptive Performance if available) to keep steady 30 or 60 instead of an erratic 45.
- **Adaptive quality**: monitor thermal state or frame time and step down quality tiers automatically with a visible setting to override.
- **Background and interruptions**: pause rendering when the app loses focus; free caches under memory warnings.

## 12. Profiling procedure

1. Pick the lowest-tier target device and a worst-case scene (most units, most effects).
2. Capture 60 seconds in a release or development build (not the editor) with the engine profiler: CPU time, GPU time, draw calls, triangles, texture memory.
3. Classify: CPU-bound, GPU-bound, bandwidth-bound, or memory-bound (render scale test, texture quality test, effect toggles).
4. Open a vendor GPU profiler or frame debugger (Xcode GPU capture on iOS; Android GPU Inspector or the vendor tool on Android; RenderDoc where supported) to see per-pass cost and overdraw.
5. Change one thing at a time; record before/after frame time in a table.
6. Write the result in a perf report and run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/perf_budget.py --report <report> --contract .gamestudio/contract.json` to check the budget.
7. Repeat on a mid-tier device and after a 15 minute soak for thermals.

## 13. Quality tiers

| Setting | Low | Mid | High |
|---|---|---|---|
| Render scale (3D) | 0.6-0.75 | 0.8-0.9 | 1.0 |
| Target frame rate | 30 | 30 or 60 | 60 (or 120 where supported) |
| Shadows | Blob only | One light, small map | One light, medium map |
| Post-processing | LUT only | LUT plus light bloom | Bloom, optional extras |
| MSAA | Off (FXAA at most) | Off or 2x | 2x |
| Texture quality | Half-res on big textures | Full | Full |
| Particles | 0.4x | 0.7x | 1.0x |
| LOD bias | Aggressive | Normal | Conservative |

Assign tiers by device class (RAM, GPU family, OS version) with an initial rule table, then adjust by a short runtime benchmark or by adaptive quality; always allow a manual override and store the choice.

## 14. Decision tables

**Which renderer?**

| Situation | Choice |
|---|---|
| Android reach to old phones is a priority | Godot Compatibility or Unity URP on GLES3 fallback |
| Mid-range and up, 3D stylized | Godot Mobile or Unity URP on Vulkan/Metal |
| Pure 2D, simple | Either engine's 2D path; keep the renderer lightweight |
| Needs heavy lighting or screen-space effects | Reconsider the design or the target devices |

**GPU-bound and fill-bound: what to cut first?**

1. Render scale down (fastest, biggest win).
2. Remove or reduce post-processing (bloom first).
3. Cut transparent overdraw (VFX quad size, stacked backgrounds, UI).
4. Remove real-time shadows and extra lights.
5. Simplify the most expensive shaders (remove normal maps, extra samples).
6. Only then reduce geometry.

**CPU-bound: what to cut first?**

1. Draw calls: batch, atlas, instance, merge static meshes.
2. UI rebuilds and layout churn.
3. Script allocations and per-frame searches (see `skills/mobile-performance`).
4. Skinned mesh and physics counts.
5. Particle systems running on CPU.

## 15. Worked example

Situation: a stylized 3D runner targeting 60 fps on a low-tier Android phone runs at 38 fps and the device is hot after five minutes.

1. Render scale test: setting 0.7 raises fps to 52, so the game is GPU/fill bound.
2. Overdraw view shows three full-screen cloud layers, a glow quad stack on the player, and a translucent HUD panel. Estimated overdraw is about 4x.
3. Fixes in order: merge two cloud layers into one texture (saves one full-screen blend); replace the glow stack with one additive quad trimmed to the visible shape; make the HUD panel opaque; replace bloom with a baked glow on the coin sprites. Result: 55 fps.
4. Bandwidth check: the build used an HDR render target for bloom; with bloom removed, switch to an 8-bit target, and drop MSAA 4x to FXAA. Result: 60 fps, with the frame time at 11 ms.
5. Thermal soak for 20 minutes shows frame time creeping to 14 ms; add adaptive resolution (step down by 5 percent when the 30-frame average exceeds 14 ms) and cap menus at 30 fps. Frame time stays at or under 14 ms after the soak.
6. Record the before/after table in the perf report and add the settings to the low-tier profile.
