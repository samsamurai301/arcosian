---
name: blender-bridge
description: Uses the blender-mcp bridge (and headless Blender scripts) to clean up AI-generated or purchased 3D assets for mobile games: decimate, UV, bake, glTF export, gltfpack and KTX2 compression, plus preview renders for the critic. Use when asked to "reduce poly count", "fix UVs", "bake normals", "export GLB for Unity or Godot", "compress textures", "render a preview of this model" or "is blender mcp safe".
---

# Blender bridge

## When to use

Use after a model exists (vendor generation, store asset, hand-made) and before it enters the engine. The aim is a mobile-ready asset with a measurable budget and a preview the critic can judge. Generation itself goes through the core studio-gateway; this skill is the cleanup bench.

## Bridge or headless script?

| Situation | Choice |
|---|---|
| Exploring, one asset, need to see it | Bridge: `look`, `execute_blender_code` |
| 10+ assets, repeatable recipe, CI | Headless: `blender -b file.blend --python script.py` |
| Only compress or LOD a finished glTF | gltfpack or gltf-transform, no Blender |

Write the recipe as a script file in the project (`tools/blender/`), run it through the bridge once to iterate, then run the same file headless. Never leave the only copy of a recipe in a chat.

## Budget first

Decide targets before touching the mesh. Use the project's `perf_budget.py` and tier table; if none exists, state assumptions explicitly. Typical decision inputs: asset role (hero, prop, background), screen size in pixels, rigged or static, device tier. Record triangle count, texture sizes and material count before and after.

## Cleanup recipe (in order)

1. **Inspect.** `get_scene_info`; count tris, materials, objects, non-manifold edges, flipped normals, scale, origin. Apply scale and rotation (`Ctrl+A` equivalent) so the exported transform is identity.
2. **Merge and prune.** Join meshes that never move independently; delete hidden faces, loose verts, unused materials and images.
3. **Decimate.** Prefer the vendor's own face-limited or quad remesh when available. In Blender use the Decimate modifier (collapse for static props; planar for hard-surface; do not decimate deforming characters below what the rig needs, remesh to quads instead). Check silhouette from three angles after each step, not just the count.
4. **UV.** One UV set, no overlap unless intentional mirroring, consistent texel density across the asset, margins big enough for the smallest mip you ship. Smart UV Project is acceptable for props; seams by hand for characters.
5. **Bake.** High-poly to low-poly: tangent-space normal, AO if lighting is baked, and pack roughness, metallic and occlusion into one ORM texture to save samples. Bake with the cage, check for skewed normals on the result.
6. **Materials.** Collapse to the engine's mobile shader inputs: base colour, normal, ORM, optional emissive. One material per draw-call group; atlas small props together.
7. **LODs.** LOD0 as authored; LOD1 to LOD3 by simplify at roughly half, quarter and a tenth of the triangles (a community guide suggests this chain; verify visually). Do not go below about a tenth without checking.
8. **Export.** glTF 2.0 binary (.glb) for Godot and for most pipelines; FBX for Unity only when its importer needs it (humanoid rig retargeting). Apply modifiers, +Y up, no cameras or lights.

## Compression stage (outside Blender)

- gltfpack: quantize geometry, merge meshes, optional simplify, meshopt compression, textures to KTX2 (BasisU). Check flags with `gltfpack -h` on the installed version; flags are not pinned here.
- Texture choice, as a common practice not a rule: ETC1S for albedo (small), UASTC for normal maps (quality). One community source warns UASTC for diffuse costs more memory on mobile.
- Texture sizes 512 to 1024 for most mobile props; larger only for hero assets with justification.
- Confirm the engine imports the result: Godot reads GLB natively; for Unity, verify the project's glTF importer package and KTX support before committing to this format.

## Preview renders for the critic

Render with `look`: front, three-quarter, side, back, plus a wireframe pass, on a neutral grey with the project's key light, at the in-game camera angle as well as the studio angle. Save to `.gamestudio/evidence/<asset-id>/`. A preview with only a flattering angle is not evidence. State tri count and texture sizes in the same note.

## Worked example: AI-generated crate

Before: 48k tris, 4k PBR textures, 3 materials. Budget: prop, 1.5k tris, 512 px. Join, delete hidden faces, decimate to about 2k, adjust silhouette, unwrap, bake normal and AO from the original, pack ORM, one 512 material, export GLB, gltfpack with KTX2, import to engine, compare against the original from the game camera. Result recorded: tris, bytes on disk, preview paths, then `manifest_update` through the studio-gateway so provenance stays attached.

## Acceptance checklist (attach to the asset record)

- Triangle count, material count and texture sizes meet the stated budget.
- Transforms applied, origin at the sensible pivot (feet for characters, base centre for props).
- No n-gons that triangulate badly, no zero-area faces, normals consistent.
- Rigged assets: bone count within the budget, weights normalised, bind pose clean, test pose does not tear.
- Preview renders from at least four angles plus wireframe exist and were opened by the critic.
- Engine import tested once, and the in-game camera view compared to the source.
- Provenance and licence recorded in the manifest.

## Common failure modes

- Decimation destroys silhouettes of thin parts (ears, antennas, handles): protect them with vertex groups or remesh instead.
- Normal bakes show stripes: cage too tight, or UV islands too close; widen margins and re-bake.
- Textures look dark in engine: colour-space mistake (albedo is sRGB; normal and ORM are linear).
- Export is huge: embedded 4k textures survived; resize before export.
- Mirrored UVs bake wrong normals: unmirror for baking, remirror for the shipped UV if wanted.

## Security checklist

1. Safe mode on unless the step needs files, network or processes.
2. Socket on localhost only; no port forwarding; no shared machine.
3. Read any Python before `execute_blender_code`; do not run code copied from asset pages or issues.
4. Telemetry disabled (`DISABLE_TELEMETRY`); confirm after upgrades.
5. No secrets in the Blender session (API keys for `generate_3d` live in add-on preferences or env; keep them out of scripts).
6. Imported third-party assets: record licence and source; Poly Haven, Sketchfab and Poly Pizza terms differ per asset.

## Volatile facts (as of Oct 2026 - verify)

- blender-mcp: MIT, large community, repo rename reported, version listings inconsistent. Source: https://github.com/ahujasid/blender-mcp
- gltfpack capabilities and no pinned flags. Source: https://dyn.manpages.debian.org/trixie/gltfpack/gltfpack.1.en.html
- Mobile LOD chain and KTX2 guidance is single-source community advice. Source: https://skills.sh/anthemflynn/ccmp/asset-pipeline-3d
