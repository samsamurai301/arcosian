---
name: technical-art
description: Technical art for games - toon, rim, matcap, dissolve, flipbook and wind shaders in Godot and Unity, VFX language and particle budgets, ASTC/ETC2/KTX2 textures, polycount and LOD budgets, gltfpack, skinning limits, tile-based GPU rendering, overdraw and post-processing cost. Use when writing shaders, building VFX, compressing textures, optimizing 3D assets, or fixing GPU-bound or hot-phone frames.
---

# Technical Art

## What this skill gives you

- A shader library for mobile styles (unlit, toon ramp, rim, matcap, dissolve, flipbook, UV scroll, vertex wind, outlines) with Godot and Unity versions and a cost ladder.
- The VFX grammar (anticipation, impact, follow-through, settle) plus recipes and particle budgets per device tier.
- Texture and mesh pipeline rules: compression formats, sizes and polycounts per tier, LODs, baking, glTF optimization, skinning limits.
- A mental model of tile-based mobile GPUs so you cut the right cost first: bandwidth, overdraw, passes, then arithmetic.
- A cleanup chain that turns AI-generated 3D into engine-ready, budget-compliant assets.
- Profiling and decision tables for GPU-bound, CPU-bound and thermal problems.

## Core models

1. **Mobile is bandwidth, fill and heat limited.** Cheapest frame = fewest pixels touched fewest times. Reduce render scale and transparent coverage before rewriting shaders.
2. **Tile-based GPUs punish mid-frame flushes.** Grab passes, depth-as-texture reads and render-target switching force tiles to memory. Avoid or do once per frame at reduced resolution.
3. **Fragment beats vertex.** Push smooth work to vertices, textures and baking: vertex colour AO, ramp lookup textures, baked light, matcaps.
4. **Texture memory is runtime memory.** PNG shrinks downloads but decodes to RGBA8; ship GPU formats (ASTC where guaranteed, ETC2 or KTX2/Basis as fallback). `bytes = w x h x bpp / 8 x 1.33` with mips.
5. **Draw calls are a CPU budget.** Share materials, atlas, instance, merge static meshes; per-object variation through property blocks or instance uniforms, not new materials.
6. **Overdraw is the VFX budget.** Count and size of translucent layers matter more than particle count. Trim quads to the visible shape.
7. **Every showpiece has a lite fallback**, selected by quality tier and verified on a low-tier device.
8. **Budgets live in the contract.** Tier budgets for tris, textures, draw calls, particles and frame time are numbers checked by `perf_budget.py`, not opinions.
9. **Effects communicate first.** Shape, colour role and timing carry gameplay meaning; decoration comes last and scales down under load.
10. **Profile on the worst device, soaked.** A cold desktop-editor result proves nothing; test the lowest tier after 15 minutes.

## Decision procedures

### Pick a shading approach for a style

| Style | Default shading | Why |
|---|---|---|
| Flat low-poly | Unlit with vertex colour or baked AO | Cheapest; shading is authored |
| Toon characters | Ramp-lit with one fixed light, rim for separation | Distinct, cheap, readable |
| Glossy toy / clay | Matcap | One sample, no lights |
| 2D sprites | Unlit sprite material, shared atlas | Batches |
| Painterly 3D | Baked lighting plus unlit albedo | Moves cost offline |
| Realistic PBR | Rethink for mobile; mid/high tier only | Heat and size |

See `references/mobile-shaders-and-vfx.md` for code and cost.

### Compress a texture

1. List the minimum supported devices. 2. iOS: ASTC. 3. Android: ASTC if guaranteed, else ETC2 or KTX2/Basis. 4. Pick block size by content: 4x4 UI and normals, 5x5/6x6 characters and props, 8x8 backgrounds. 5. Never block-compress pixel art. 6. Verify on device at real size. Details: `references/texture-and-3d-pipeline.md`.

### Budget and check a 3D asset

1. Read the tier class budget (tris, bones, material count, texture size). 2. Inspect: scale, pivot, normals, loose parts, UVs. 3. Decimate or remesh with boundary protection. 4. Cap influences to 4 and normalize weights. 5. Generate LODs if the camera varies. 6. Optimize with gltfpack or gltf-transform; diff counts before and after. 7. Import headless; fail on warnings. 8. Run the acceptance checklist.

### Build an effect

1. Name its gameplay meaning (hit, heal, reward, warning). 2. Choose shape and colour role from the bible. 3. Time the four phases; align the impact peak with sound. 4. Build with flipbook or few quads; additive for light, alpha for smoke. 5. Check overdraw and the particle budget at worst-case density. 6. Add a reduced-effects variant. 7. Pool and warm up shaders.

### Diagnose a slow or hot frame

1. Drop render scale: fps rises = GPU/fill bound; no change = CPU/submission bound.
2. GPU-bound cut order: render scale, post-processing (bloom first), transparent overdraw, shadows and extra lights, shader samples, then geometry.
3. CPU-bound cut order: draw calls (batching), UI rebuilds, script allocations, skinned meshes and physics, CPU particles.
4. Change one thing at a time; log before/after.
5. Soak 15-30 minutes; add adaptive resolution and a frame-rate cap for menus.
6. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/perf_budget.py --report <report> --contract .gamestudio/contract.json`.

### Write a shader with an agent

State engine, version, renderer and tier; ask for the smallest shader and its sample count; compile at once; screenshot on a test mesh; profile on the low tier; write from the idea, not pasted code of unknown licence.

## Mobile specifics

- Phones throttle: plan for about 70 percent of the frame budget at sustained load; cap frame rate where the genre allows (30 for menus).
- Choose the renderer by the minimum device: Godot Mobile or Compatibility, Unity URP; avoid Forward+ and HDRP on phones.
- Render the 3D world below native resolution (about 0.6-0.9 scale) and keep UI at native.
- Real-time shadows, SSAO, DOF, motion blur and screen-space reflections are high-tier only; use blob shadows, baked AO and art tricks.
- Warm up shaders and pipelines at load to avoid first-use hitches, especially on Metal and Vulkan.
- Keep a reduced-flash and reduced-motion path for accessibility and for low tier.
- Test on one low-tier Android and one older iPhone every release.

## Anti-patterns

| Anti-pattern | Detect | Fix |
|---|---|---|
| Full-screen bloom on every tier | HDR target, several downsample passes in the capture | Tier-gate; glow sprites on low |
| Soft particles and grab pass by default | Depth/colour copies in frame debugger | Fake with vertex fade; one distortion pass on demand |
| Giant smoke quads | Overdraw view shows red | Trim, cap size, fewer layers |
| Unique material per object | Draw calls track object count | Shared material plus property blocks or instancing |
| 4096 textures for small objects | Memory report | Size by screen coverage; mips; atlas |
| Per-pixel pow and normalize chains | Shader cost view | Ramp texture, integer powers, vertex math |
| `discard` on large or many objects | Early-z lost; fill spikes | Tight cutout meshes, alpha fade, scale-out |
| Shader keyword explosion | Build time, hitching | `shader_feature`, runtime uniforms, warm-up |
| Trusting the editor | Device is slower and hotter | Profile on device after a soak |
| AI mesh imported untouched | Uneven density, 5+ influences, baked light | Cleanup chain in the texture and 3D pipeline file |
| Flat fix for a hot phone (just lower fps) | Still bandwidth heavy | Cut passes and overdraw; then cap fps |

## Using the ontology

- Tier budgets (tris, texture MiB, particles, draw calls, frame time) belong in `.gamestudio/contract.json` performance fields and are checked by `${CLAUDE_PLUGIN_ROOT}/scripts/perf_budget.py`.
- Effects map to dynamics and feedback in the loop graph: each VFX serves a verb or a state change (hit, reward, warning); name that link when specifying it.
- Shaders, VFX and 3D assets are content units with manifest entries (provenance, licence, bible version); see `ai-asset-pipeline`.
- `${CLAUDE_PLUGIN_ROOT}/scripts/image_post.py` checks image size, alpha and atlas packing; this skill has no scripts of its own.
- Visual quality gates use `art-direction` (critique rubric, palette audit); technical-art supplies the objective numbers (overdraw, memory, draw calls).

## Reference library

| File | What it contains | When to read it |
|---|---|---|
| `references/mobile-shaders-and-vfx.md` | Shader rules and cost ladder; unlit, toon, rim, matcap, dissolve, flipbook, UV scroll, wind, outlines in Godot and Unity; variants and precision; VFX language, recipes, particle budgets | Writing a shader or effect; setting particle limits |
| `references/texture-and-3d-pipeline.md` | Memory maths, ASTC/ETC2/KTX2/Basis, tier texture sizes, atlases, polycount and LOD budgets, baking, gltfpack, skinning limits, AI 3D cleanup, volatile facts | Importing or optimizing textures and meshes; setting budgets |
| `references/rendering-on-mobile.md` | Tile-based GPUs, bandwidth, batching, overdraw, transparency, lighting, post cost, render scale, Vulkan/Metal/GLES, thermals, profiling, quality tiers | Choosing a renderer; diagnosing GPU or CPU bottlenecks |

## Related skills

- `art-direction`: style bible, palette and critique that the shaders and VFX must honor.
- `ai-asset-pipeline`: generation and post-processing that feeds this pipeline; 3D cleanup chain context.
- `mobile-performance`: frame, memory and battery budgets, profiling workflows, device tiers.
- `game-feel`: timing, hit-stop and juice that VFX deliver.
- `engine-godot`: Godot project settings, renderers, export and import specifics.
- `engine-unity`: URP setup, Shader Graph, importers and build settings.
- `mobile-ux`: HUD overdraw, UI canvases and touch targets.
- `accessibility-localization`: flash, motion and contrast settings.
