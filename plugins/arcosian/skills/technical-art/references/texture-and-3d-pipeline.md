# Texture and 3D Pipeline for Mobile

How art becomes shippable mobile data: GPU texture compression (ASTC, ETC2, Basis/KTX2), atlases and mipmaps, texture and polycount budgets per device tier, level of detail, baking, glTF optimization with gltfpack and meshoptimizer, and skinning limits. The goal is predictable memory, download size and frame time. Numbers are studio heuristics for planning; confirm them with the project's `perf_budget.py` contract and a profile on the lowest-tier device. Format support varies by GPU generation and by engine version, so the "Volatile facts" section lists what to verify before relying on it.

## Contents

1. [Memory and size maths](#1-memory-and-size-maths)
2. [Texture compression formats](#2-texture-compression-formats)
3. [Choosing a format](#3-choosing-a-format)
4. [Mipmaps, filtering, sRGB, normal maps](#4-mipmaps-filtering-srgb-normal-maps)
5. [Texture sizes per tier](#5-texture-sizes-per-tier)
6. [Atlases and texture arrays](#6-atlases-and-texture-arrays)
7. [KTX2 and Basis Universal](#7-ktx2-and-basis-universal)
8. [Polycount and mesh budgets](#8-polycount-and-mesh-budgets)
9. [LOD strategy](#9-lod-strategy)
10. [Baking](#10-baking)
11. [UVs, vertex data and mesh layout](#11-uvs-vertex-data-and-mesh-layout)
12. [glTF, gltfpack and meshoptimizer](#12-gltf-gltfpack-and-meshoptimizer)
13. [Skinning, rigs and animation data](#13-skinning-rigs-and-animation-data)
14. [Import pipeline in the engines](#14-import-pipeline-in-the-engines)
15. [AI-generated 3D cleanup chain](#15-ai-generated-3d-cleanup-chain)
16. [Asset acceptance checklist](#16-asset-acceptance-checklist)
17. [Volatile facts (as of Oct 2026 - verify)](#17-volatile-facts-as-of-oct-2026---verify)

---

## 1. Memory and size maths

Two sizes matter: **download/disk size** (what the store and the user see) and **runtime memory** (what the GPU holds). They differ: PNG and JPEG shrink the download but are decoded to uncompressed RGBA in memory unless converted to a GPU format; GPU-compressed formats stay compressed in memory.

| Format | Bits per pixel | 2048 x 2048 size (no mips) | With mipmaps (x1.33) |
|---|---|---|---|
| RGBA8 uncompressed | 32 | 16 MiB | about 21.3 MiB |
| RGB565 / RGBA4444 | 16 | 8 MiB | about 10.7 MiB |
| ETC2 RGB | 4 | 2 MiB | about 2.7 MiB |
| ETC2 RGBA (EAC alpha) | 8 | 4 MiB | about 5.3 MiB |
| ASTC 4x4 | 8 | 4 MiB | about 5.3 MiB |
| ASTC 6x6 | 3.56 | about 1.8 MiB | about 2.4 MiB |
| ASTC 8x8 | 2 | 1 MiB | about 1.3 MiB |

Formula: `bytes = width x height x bpp / 8`, times about 1.33 if mipmapped. Sum for a screen: all textures live on that screen plus render targets. A full-screen render target at 1080 x 2340 RGBA8 is about 9.6 MiB, and a mobile frame may need several (colour, depth, post). Memory pressure kills the app on low-RAM phones, so budget it like frame time.

## 2. Texture compression formats

| Format | Where it works | Alpha | Quality character | Notes |
|---|---|---|---|---|
| ASTC | Modern iOS GPUs and most current Android GPUs; widely supported on recent hardware | Yes | Excellent, selectable block size (4x4 to 12x12) trades size for quality | The default choice when the minimum device supports it |
| ETC2 / EAC | OpenGL ES 3.0+ and Vulkan Android devices; Godot Mobile and Compatibility export | Yes (EAC) | Good for RGB, adequate alpha | The Android fallback when ASTC is not guaranteed |
| ETC1 | Very old Android | No | Poor | Avoid for new projects |
| PVRTC | Old iOS GPUs | Yes | Weak quality, square power-of-two only | Legacy only |
| BC / DXT | Desktop | Yes | Good | Not a mobile format (except for some Android or desktop-class devices); do not ship as the mobile default |
| Basis Universal (ETC1S, UASTC) in KTX2 | Transcodes at load to the device's native format | Yes | ETC1S small and lossy; UASTC high quality | One file, many devices, small download; see section 7 |
| Uncompressed RGBA8 | Everywhere | Yes | Lossless | Only for tiny textures, gradients that band, and render targets |

ASTC block size guide (planning heuristic): 4x4 for UI, text-adjacent art and normal maps of hero assets; 5x5 or 6x6 for most characters and props; 8x8 for backgrounds, terrain and large soft textures. Always compare visually on a device; gradients (skies, soft glows) band first, and sharp UI edges ring first.

## 3. Choosing a format

Decision procedure:
1. List the minimum supported devices for each platform from the contract (not the average).
2. iOS: ASTC. Anything else is legacy.
3. Android: if the minimum GPU tier guarantees ASTC, use ASTC; otherwise ship ETC2 or KTX2/Basis, and make it a build-time choice (one Android artifact per format is rarely worth it, so prefer Basis or ETC2 for a single universal build).
4. Alpha-heavy UI atlases: ASTC 4x4 (or uncompressed if size is small and banding is visible); avoid ETC2 for soft-alpha gradients if quality suffers.
5. Normal maps: ASTC 4x4 or 5x5 with a two-channel encoding; do not compress normals with ETC1S.
6. Pixel art: do not compress (or use the least lossy mode, point filtering, no mipmaps); pixel art is damaged by block compression. Keep pixel-art atlases small; they are already small.
7. Render targets and dynamic textures: uncompressed, with the lowest format that holds (RGB565, RG11B10, R8 for masks).
8. Verify on a device, in motion, at the real display size, not in the inspector at 400% zoom.

Engine switches:
- Godot: Project Settings > Rendering > Textures > VRAM Compression (Import ETC2/ASTC); import presets per texture ("VRAM Compressed", "Lossless", "Basis Universal" options for some paths); mobile export presets enable the format flags.
- Unity: per-platform overrides in the texture importer (Android: ASTC with block size; iOS: ASTC), a project default texture compression format in Android build settings, and the Crunch option to reduce download size at the cost of import time.

## 4. Mipmaps, filtering, sRGB, normal maps

- **Mipmaps** reduce shimmer and cache misses for textures drawn at varying sizes (3D, scaled sprites). Disable them for UI and pixel art drawn at 1:1; they add about a third in memory.
- **Filtering**: bilinear is the default; trilinear costs more; anisotropic filtering is costly on mobile, so use it only for ground planes in racing-style games and keep levels low.
- **sRGB vs linear**: colour textures are sRGB; masks, roughness, noise and normal maps are linear. A wrong flag shifts the look and breaks blending of ramps and gradient masks.
- **Alpha handling**: premultiplied or straight, consistently; dilate colour into transparent texels to avoid halos.
- **Normal maps**: avoid on small objects and low-tier devices; bake detail into albedo and vertex colour instead. If used, 2-channel encoding with reconstructed Z saves memory.
- **Mask packing**: pack single-channel data into the RGBA channels of one linear texture (for example AO in R, emission mask in G, wind weight in B) to cut samples.

## 5. Texture sizes per tier

Planning heuristics for the largest single texture and the per-screen budget; adjust after profiling. "Memory" is texture memory in a typical gameplay screen.

| Tier | Max texture | Typical character | Typical prop | Environment/background | Screen texture memory (rough) |
|---|---|---|---|---|---|
| Low (older, 2-3 GB RAM class) | 1024 | 512 | 256 | 1024 | 60-100 MiB |
| Mid | 2048 | 1024 | 512 | 2048 | 120-200 MiB |
| High | 2048-4096 (only hero) | 2048 | 1024 | 2048-4096 | 250-400 MiB |

Rules: screen-space size drives texture size; a texture displayed at 200 px never needs 2048; check **texel density** (texels per metre or per screen pixel) across assets so hero and background objects match the style; scale textures down per quality tier through an import-time variant (Unity: texture quality "half/quarter res"; Godot: import `size_limit` or a lower-resolution variant set).

Streaming and loading: keep the minimum set resident; load per-screen atlases asynchronously; avoid loading full-screen art at a larger size than the display.

## 6. Atlases and texture arrays

- Sprite and UI atlases are described in `skills/art-direction/references/asset-specs-and-marketing-art.md`.
- 3D props: share one atlas or trim sheet across a set of props so they batch; trim sheets (a strip texture with reusable details mapped by UVs) give variety at one material.
- Texture arrays (same size and format layers addressed by index) let different objects use different textures in one draw; they need support in the engine and the shader, and every layer must match size and format.
- Colour-ramp lookup textures (gradients for toon ramps, palette swaps, team colours) are tiny and very useful: palette-swap by sampling a row index per instance.
- Vertex-colour tinting: one texture, tint by vertex colour per object; cheap variants for enemy recolours.
- Atlas packing in CI: rebuild from source; keep padding 2-4 px; verify with `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/image_post.py check` and `atlas`.

## 7. KTX2 and Basis Universal

KTX2 is a container for GPU textures that can hold Basis Universal data, which transcodes to the device's native compressed format at load time. Why it matters: one file supports ASTC and ETC2 devices, the download is small, and tooling exists in the glTF ecosystem.

| Mode | Use for | Trade-off |
|---|---|---|
| ETC1S | Albedo of props, backgrounds, large soft textures | Smallest files, visible blocky or banding artifacts on gradients; not for normals or UI |
| UASTC | Normals, UI, hero textures | Larger, much higher quality; can be supercompressed (Zstandard) for download |

Process: author PNG at the final size -> encode with a Basis/KTX2 tool (for example the `toktx` tool from the Khronos KTX software, Basis Universal's encoder, or `gltfpack -tc`) -> check on device -> load through the engine's KTX2 importer (Godot imports KTX2 in recent 4.x versions, Unity supports KTX2 through the graphics packages; verify per version). Transcoding costs CPU time at load, so budget it during loading screens and avoid transcoding large textures on the main thread during gameplay.

Zstandard supercompression reduces download size but adds decode time; test the trade on the lowest device.

## 8. Polycount and mesh budgets

Triangle counts are a guide, but draw calls, skinning cost and overdraw usually bind first. Heuristic budgets for visible triangles per frame and per object class:

| Tier | Visible scene tris | Hero character | NPC / enemy (many on screen) | Prop | Environment chunk |
|---|---|---|---|---|---|
| Low | 50k-100k | 2-4k | 0.5-1.5k | 100-500 | 5-10k |
| Mid | 150k-300k | 5-10k | 1.5-3k | 300-1.5k | 15-30k |
| High | 400k-800k | 10-30k | 3-6k | 1-3k | 30-60k |

Notes:
- Stylized or low-poly games are far below these; the budgets are ceilings.
- Count what the camera sees, including shadow passes (a shadow pass re-renders casters).
- Many small meshes cost more in draw calls than a few larger ones; merge static geometry per room or per chunk, but keep chunk size compatible with culling.
- Thin triangles and tiny triangles waste GPU quad efficiency; avoid dense meshes far from the camera.
- Vertex attribute count matters: position, normal, UV0, UV1, tangent, colour, bone indices and weights all cost bandwidth; drop UV1 and tangents when unused.

Budget procedure: set tier budgets in the contract -> list asset classes with counts on screen -> compute worst-case tris (count x tris) -> compare to tier -> assign per-class limits -> verify in the profiler on the lowest device.

## 9. LOD strategy

| Technique | When | Notes |
|---|---|---|
| Discrete LODs (3-4 levels) | Characters and props seen at varying distance | LOD0 100%, LOD1 about 50%, LOD2 about 25%, LOD3 billboard or impostor (heuristic ratios); switch by screen coverage, not distance |
| Fixed-camera games | Often no LODs needed | Author at the single viewing size instead |
| Impostors / billboards | Far crowds, trees | Render the object into a sprite atlas from several angles; very cheap |
| Culling | Everything | Frustum culling by default; add occlusion culling or room-based visibility for indoor scenes; distance cull small props |
| Animation LOD | Many characters | Update skeleton at half or quarter rate when far; drop bones; freeze off-screen |
| Material LOD | High-end effects | Switch to simpler shaders by distance or tier |

Generate LODs by tool (gltfpack simplification, Blender Decimate, engine LOD generators) and then inspect silhouettes at the switch distance; auto-decimation destroys UV seams and animated joints if run blindly, so lock boundary edges and protect deforming areas (shoulders, elbows, knees, face).

## 10. Baking

Baking moves expensive computation into textures or vertex data before runtime.

| Bake | Result | Use |
|---|---|---|
| Ambient occlusion | Grey mask in a texture or vertex colour | Contact shading on props and characters without lights |
| Lightmaps | Static lighting for environments | Fixed-camera levels; adds UV2 and memory; use low resolution |
| High-to-low normal map | Detail from a high-poly sculpt onto a low-poly mesh | Only where normal maps are affordable |
| Curvature, thickness, gradient | Masks | Stylized edge wear, subsurface fakes, toon tweaks |
| Texture bake of procedural materials | Albedo from a node network | Remove runtime cost |
| Vertex-colour bake | Per-vertex AO and gradients | Free shading for low-poly styles |
| Impostor bake | Multi-angle sprites | Far LODs |

Procedure (Blender, scriptable headless):
1. Create or select the low-poly mesh with clean, non-overlapping UVs and padding (margin of 4 to 16 px at the bake resolution).
2. Select high-poly sources and set cage or ray distance to avoid bleed.
3. Bake maps at 2x then downsample, or bake directly at target size with a margin.
4. Check for seams, inverted normals, tangent space mismatch (match the engine's convention: Godot and OpenGL use Y up, Unity uses the same tangent convention as OpenGL-style normal maps on import in most cases, verify with a test sphere).
5. Pack channels into the project's mask texture layout.

Automation: `blender --background --python bake.py -- input.glb output.glb` with the `bpy` API is the standard route; an agent can drive a running Blender through a Blender MCP server for exploratory work, then convert the steps into a headless script for CI.

## 11. UVs, vertex data and mesh layout

- One UV set for albedo (UV0) and an optional non-overlapping set for lightmaps (UV1).
- Keep UV islands within 0-1 unless using a deliberate tiling trim sheet; pad islands to match mip level (more padding for lower-res textures).
- Keep texel density consistent across a set, then adjust by importance.
- Mirror UVs for symmetric objects to double the effective resolution; avoid mirrored normal-map seams on faces.
- Vertex colour carries masks (AO, wind weight, tint); name the channels in the spec.
- Weld vertices where normals and UVs match; split only where required for hard edges or UV seams to reduce vertex count (a mesh's real cost is unique vertices, not faces).
- Origin and pivot at the base for props, at the feet for characters; apply scale and rotation before export so scale is 1.

## 12. glTF, gltfpack and meshoptimizer

glTF 2.0 (`.glb`) is the interchange format of choice for AI-generated and DCC output; both engines import it (Godot natively, Unity via a package). `meshoptimizer` and its CLI `gltfpack` compress and optimize glTF.

Typical command patterns (verify flags against the installed version with `gltfpack -h`):

```
# Quantize, reorder for the GPU cache, merge meshes and materials, simplify to a ratio, KTX2 textures
gltfpack -i in.glb -o out.glb -cc -si 0.5 -tc
# Keep it loadable by engines without the meshopt extension: do not compress geometry, only optimize
gltfpack -i in.glb -o out.glb -noq -si 0.5
# LOD chain: write separate files at different simplification ratios
gltfpack -i in.glb -o out_lod1.glb -si 0.5 && gltfpack -i in.glb -o out_lod2.glb -si 0.25
```

Key behaviours:
- `-cc` compresses with the meshopt extension (EXT_meshopt_compression); the runtime loader must support it. Check engine support before choosing it; a safe fallback is to skip geometry compression and rely on download compression (zip/brotli) while keeping quantization.
- `-tc` converts textures to KTX2 using Basis encoding; `-si` simplifies by ratio; `-vp`/`-vt`/`-vn` control position, texcoord and normal quantization bits; `-kn` and `-km` keep nodes and materials when the engine needs names.
- Quantization reduces vertex bandwidth; check for visible faceting on large meshes.
- Vertex cache and overdraw reordering are on by default and are always worth it.
- Alternative: `gltf-transform` (Node) offers a scripted pipeline (`optimize`, `dedup`, `prune`, `resample`, `draco`/`meshopt`, `etc1s`/`uastc`); Node tools fit the plugin's zero-install philosophy only if the user already has them.
- Always diff before and after: triangle count, vertex count, material count, texture sizes, file size. Fail the asset if it exceeds its class budget.

## 13. Skinning, rigs and animation data

| Limit | Heuristic | Why |
|---|---|---|
| Influences per vertex | 4 maximum (2 for small background characters) | GPU skinning cost and engine defaults; AI-generated rigs may carry more, so cap and renormalize |
| Bones per mesh | Low tier 30-40, mid 60-80, high up to about 120 | Uniform limits in shaders and CPU skinning cost; varies by engine and renderer |
| Skinned meshes on screen | Low tier 8-12, mid 15-25 | CPU and GPU skinning scale with count |
| Animation clips per character | Only what is used; share across rigs via retargeting | Memory and load |
| Animation sampling | Resample to 30 fps or lower and drop redundant keys | Clip size shrinks significantly |
| Blend shapes | Avoid on low tier; keep to a handful for faces | Memory and per-vertex cost |
| Cloth/physics bones | Few, low-update | CPU cost |

Procedure for cleaning a rigged character: import -> check bone hierarchy names against the engine's retarget profile (humanoid) -> remove unused bones and weights below a small threshold -> limit to 4 influences and normalize -> verify bind pose is a T or A pose and scale is 1 -> test with three clips (idle, run, attack) for candy-wrapper joints -> export. Prefer a Mixamo-compatible humanoid skeleton when retargeting shared animations. Instancing skinned meshes: Unity can use GPU instancing with baked animation textures (vertex animation textures) for crowds; Godot can use `MultiMesh` with a custom shader for baked vertex animation; both trade flexibility for large counts and are worth the effort for crowds of the same enemy type.

For 2D skeletal rigs, keep part count and mesh vertex count low, and put all parts on one atlas.

## 14. Import pipeline in the engines

| Concern | Godot 4.x | Unity 6 |
|---|---|---|
| glTF import | Native importer; scene import settings; editor import hooks (`EditorScenePostImport`) | glTFast package for glTF; FBX native; `AssetPostprocessor` scripts |
| Automation on import | Import presets; `.import` files; editor scripts with `EditorImportPlugin` | `AssetPostprocessor`, presets, texture importer settings by folder |
| Texture settings | Import dock per texture, with defaults in Project Settings | Per-platform overrides, default presets by folder |
| Compression | VRAM compressed (ETC2/ASTC) and KTX2 paths | ASTC/ETC2 with block sizes, Crunch, KTX2 |
| LODs | `visibility_range` on GeometryInstance3D and automatic mesh LOD import | LOD Group component, importers |
| Batching aids | MultiMesh, shared materials | SRP Batcher, GPU instancing, static batching |

Rules: import settings live in version control with the asset; use folder-level defaults (presets) rather than per-asset manual tweaks; a CI step runs a headless import and fails on errors; generated assets enter through the import checklist in section 16.

## 15. AI-generated 3D cleanup chain

Generators output meshes with uneven density, messy UVs and baked lighting in the albedo. Treat their output as a sculpt to be retopologized, not as a final asset.

1. **Request low-poly where possible**: pass a face limit or low-poly mode to the generator (see `skills/ai-asset-pipeline/references/model-landscape-2026.md`); native low-poly beats decimating a dense mesh.
2. **Inspect**: bounds, scale, orientation, face count, non-manifold edges, flipped normals, loose parts, texture resolution, lighting baked into albedo.
3. **Remesh/decimate** to the class budget with boundary and UV protection; prefer quad-dominant remesh when the object will be deformed or sculpted further.
4. **UV**: re-unwrap if islands are fragmented; target consistent texel density and padding.
5. **Texture**: remove baked shadows and highlights (de-light) when the shader provides lighting; re-bake AO if needed; downscale to the tier size.
6. **Rig**: use the generator's auto-rig or a humanoid auto-rigger, then clean weights (section 13).
7. **Material**: map to the project's shader (toon ramp, matcap, unlit) and set the palette via the style bible, replacing the generator's PBR if the style is stylized.
8. **Optimize**: gltfpack or gltf-transform, LODs, KTX2.
9. **Validate**: import into the engine, check silhouette against the bible, run the budget check.
10. **Record**: manifest entry with provider, prompt, model version, licence status, bible version, and the list of manual edits (supports copyright and disclosure, see the provenance file).

## 16. Asset acceptance checklist

- [ ] Triangle, vertex, bone and material counts within the class budget
- [ ] Texture sizes and formats per tier; memory contribution computed
- [ ] Single material or shared atlas where possible; no unused materials, UV sets or vertex attributes
- [ ] Scale 1, pivot correct, axes match the engine, naming per convention
- [ ] Normals correct, no flipped faces, no non-manifold geometry
- [ ] Skinning: at most 4 influences, weights normalized, clips tested
- [ ] LODs generated and checked at switch distance, or justified as unnecessary
- [ ] sRGB/linear flags right; normal-map convention right
- [ ] Imports headless in CI without warnings
- [ ] Provenance and licence entries present; no baked third-party IP

## 17. Volatile facts (as of Oct 2026 - verify)

| Fact | Status in the research notes | Source |
|---|---|---|
| Free scriptable optimization stack: vendor remesh/face limits, Blender headless Python, gltfpack/meshoptimizer or gltf-transform for quantization, merging, LODs and KTX2/Basis textures | Reported as available | Research notes (3D pipeline section); confirm tool versions locally with `gltfpack -h` |
| TexturePacker CLI supports ETC1/ETC2/PVRTC/DXT/ASTC/Basis (ETC1S, UASTC) and outputs PKM/KTX/KTX2/ASTC | Reported | CodeAndWeb TexturePacker CLI documentation (verify current page and licence terms for CI use) |
| InstaLOD 2026 free for indies under a revenue threshold, with CLI batch pipeline; Simplygon indie terms unclear | Reported, unverified details | Vendor sites (verify terms) |
| Generator face-limit and remesh parameters (Tripo `face_limit` 48-20k faces; Meshy remesh 100-300k; Tencent Smart Topology) | Reported | https://docs.meshy.ai/en/api/pricing for Meshy; vendor docs for the others (verify) |
| Engine KTX2 and meshopt extension support, ASTC availability on Android GPU tiers | Not covered in notes | Check the engine release notes and the Android device-capability statistics for the minimum supported devices |

Do not hard-code these in contracts; store verified values with the date in the project.
