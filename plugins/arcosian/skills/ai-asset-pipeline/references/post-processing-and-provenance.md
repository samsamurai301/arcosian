# Post-Processing and Provenance

What happens to a generated asset between the model and the engine, and how to prove where it came from. The first half is the post chain for 2D (background removal, trim, upscaling, vectorization, palette mapping, pixel-art handling, sprite sheets, atlases) and for 3D (cleanup chain). The second half is manifest discipline, the licence allowlist, copyright posture and store disclosure. Rule of thumb: every generated asset is raw material; it becomes a game asset only after a deterministic post chain, an objective check, a critique pass and a manifest entry with provenance. Disclosure rules and licences are volatile and listed with sources at the end.

## Contents

1. [Post-processing principles](#1-post-processing-principles)
2. [2D chain by asset class](#2-2d-chain-by-asset-class)
3. [Background removal](#3-background-removal)
4. [Trim, pad, resize and upscale](#4-trim-pad-resize-and-upscale)
5. [Vectorization](#5-vectorization)
6. [Palette mapping](#6-palette-mapping)
7. [Pixel art handling](#7-pixel-art-handling)
8. [Sprite sheets from grids](#8-sprite-sheets-from-grids)
9. [Atlases and export](#9-atlases-and-export)
10. [3D cleanup chain](#10-3d-cleanup-chain)
11. [Objective checks after post](#11-objective-checks-after-post)
12. [The manifest](#12-the-manifest)
13. [Manifest discipline](#13-manifest-discipline)
14. [Licence allowlist](#14-licence-allowlist)
15. [Copyright posture](#15-copyright-posture)
16. [Disclosure](#16-disclosure)
17. [Privacy and data](#17-privacy-and-data)
18. [Volatile facts (as of Oct 2026 - verify)](#18-volatile-facts-as-of-oct-2026---verify)

---

## 1. Post-processing principles

- **Deterministic and scripted.** The same input produces the same output; the chain is a script or a documented sequence of gateway and `image_post.py` calls, not hand edits in a GUI that cannot be repeated. Hand edits are allowed as a final craft step and are logged in the manifest `notes`.
- **Non-destructive.** Keep the raw generation under the generated directory and write derived files with `derived_from` set to the source id.
- **Native output first.** Native transparency, native pixel grid and native vector beat repairing a wrong output form.
- **One chain per asset class**, documented in the bible, so assets of a class are processed identically.
- **Check after every lossy step.** Resizing, quantizing and keying each add risk; the objective checks in section 11 catch regressions before critique.
- **Do not hide defects.** If post cannot fix it (anatomy, text, perspective), regenerate or hand-fix.

## 2. 2D chain by asset class

| Class | Chain |
|---|---|
| Sprite / item / icon (raster) | generate on flat colour or native transparent -> remove background -> trim -> palette map -> resize to class size -> edge cleanup -> check -> atlas |
| UI element | generate -> remove background -> trim -> define 9-slice borders -> resize to authoring size -> check -> UI atlas |
| Tile / texture | generate -> seam test -> fix seam -> resize to power of two -> compress per texture rules |
| Background | generate -> upscale if needed -> crop to aspect -> check banding -> compress |
| Pixel art | native pixel tool, or generate large -> pixelate -> quantize to palette -> nearest-neighbour only from there |
| Sprite sheet | generate grid -> key out -> slice -> align pivots -> silhouette consistency check -> pack |
| Icon (vector) | generate vector or vectorize -> clean paths -> rasterize per size |
| App icon / key art | tournament -> human finish -> export all sizes -> store checks |
| VFX frame | generate on black or transparent -> trim -> normalize brightness -> flipbook layout |

## 3. Background removal

Options in order of preference:
1. **Native transparency** from the generator when offered (some models and platforms output transparent PNG; the notes report OpenAI image models gained a transparent-background preview in 2026; verify current API behaviour).
2. **Service**: gateway `image_postprocess` with `op: remove_background` (Recraft) or a platform endpoint (Scenario, Leonardo).
3. **Chroma key** when the asset was generated on a flat colour that does not appear in the subject: key by colour distance with feathering, then despill (remove the key colour's tint from edges).
4. **Self-hosted segmentation** only with a commercially licensed model; BRIA RMBG 2.0 weights are non-commercial, so they are excluded unless a commercial agreement exists. Check the licence of any other segmenter before shipping.

Quality checks after keying: edge halo (dark or light fringe), holes inside the subject, lost thin parts (antennae, strings), semi-transparent areas that should be solid, and shadows kept or removed on purpose. Fix halos by eroding the mask one pixel and dilating RGB into transparent pixels (colour bleed fix).

## 4. Trim, pad, resize and upscale

- **Trim** transparent borders, then add uniform padding of 1-2 px (or the atlas padding) and record the original canvas offset where animation needs it.
- **Resize** with Lanczos for painted art and nearest-neighbour for pixel art: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/image_post.py resize --in a.png --out b.png --width 256 --resample lanczos` (needs Pillow; the script prints the install hint).
- **Downscale from a larger master** (generate at 1024, deliver at 256) gives crisper edges than generating small.
- **Upscale** only when the master is too small. Order of preference: regenerate at a larger size; crisp (non-generative) upscaler; creative upscaler only for backgrounds and key art, never for pixel art, and review for invented detail.
- Keep dimensions to the class spec (multiples of 4 or powers of two for compressed textures); see `skills/art-direction/references/asset-specs-and-marketing-art.md`.

## 5. Vectorization

Use for flat icons and simple shapes: gateway `image_postprocess` with `op: vectorize` (Recraft) or native vector generation. Check path count (very high counts are heavy and not crisp), stray specks, gradient handling, and that the SVG renders identically in the engine's importer (Unity needs the Vector Graphics package; Godot imports SVG as a texture at a chosen scale). For shipping, rasterize SVG at the needed sizes in the pipeline rather than rely on runtime SVG.

## 6. Palette mapping

Generators approximate palettes. To enforce the bible palette:
1. Extract the current colours: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/image_post.py palette --in a.png --colors 16`.
2. Quantize to the bible palette (nearest colour in a perceptual space such as Lab) with optional dithering off for flat styles and on for gradients in pixel art.
3. For painterly assets, do a soft palette pull instead: shift hues toward the nearest palette hue by a fraction (for example 50 percent) to keep gradients.
4. Re-run `skills/art-direction/scripts/palette_audit.py` on the project palette and check gameplay-critical pairs.
5. Keep skin, brand and semantic colours exact (see the bible semantic palette).

## 7. Pixel art handling

- Generate at the **native resolution** with a pixel-aware tool (PixelLab, Retro Diffusion) when possible.
- For general models: generate large with a flat background, then `pixelate --block N` (block-average then nearest-neighbour upscale), then quantize to the palette, then clean stray single pixels by hand or script.
- **Never** apply smoothing, generative upscaling or non-integer scaling to pixel art; export at 1x and let the engine scale by integer factors with point filtering; no mipmaps and no block compression.
- Check **pixel grid consistency**: no mixed pixel sizes inside one sprite, outline thickness 1 px, consistent light direction.
- Animation frames must share the palette and silhouette scale; compare frame silhouettes.

## 8. Sprite sheets from grids

Procedure for a generated grid (cols x rows):
1. Key out the background (section 3).
2. Detect or compute cell bounds; if cells are not evenly spaced, find connected components and assign them to cells by centroid.
3. Extract each frame, trim, and re-place it onto a uniform cell canvas with a fixed anchor: horizontal centre of mass or of the feet, vertical at the lowest opaque row (feet).
4. Compare frames: silhouette area variance (start with a tolerance of about 10 percent), height variance, palette equality; flag outliers for regeneration.
5. Check loop: first and last frame closeness for cycles.
6. Export per-frame PNGs and a JSON describing animation names, frame order, fps and pivots; pack into the character atlas.

If more than about a third of the frames fail, regenerate the grid with a stronger reference or switch to a tool with native animation.

## 9. Atlases and export

- Pack with the engine or `image_post.py atlas --in <files> --out atlas.png --max-size 2048 --padding 2` (writes `atlas.json`; add `--pot` to round up to a power of two).
- Use the naming and folder conventions in the asset-specs file; rebuild atlases in CI from sources.
- Run `image_post.py check --in <file> --max-kb <N> --pot` on exported textures; `--no-alpha` for icons that must be opaque.
- Compress for the target in the engine import step (see `skills/technical-art/references/texture-and-3d-pipeline.md`).

## 10. 3D cleanup chain

Summary (full procedure in `skills/technical-art/references/texture-and-3d-pipeline.md`, section "AI-generated 3D cleanup chain"):
1. Request low-poly with `face_limit` from `model3d_generate`.
2. Inspect scale, normals, non-manifold edges, loose parts.
3. Remesh or decimate with boundary and UV protection.
4. Re-unwrap if needed; unify texel density.
5. De-light albedo; re-bake AO if needed.
6. Rig and clean weights (at most 4 influences).
7. Map to the project shader; apply the bible palette.
8. Optimize with gltfpack or gltf-transform; generate LODs.
9. Import headless; budget check; silhouette check.
10. Manifest with the list of manual edits.

## 11. Objective checks after post

| Check | Command or method | Fail example |
|---|---|---|
| Size, alpha, power-of-two, file size | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/image_post.py check --in <files> --max-kb 512 --max-dim 2048 --json` | Opaque icon with alpha, oversize atlas |
| Palette conformity | `image_post.py palette` then compare to the bible; `palette_audit.py` for critical pairs | Extra hues, low contrast pair |
| Silhouette distinctness | Black fill comparison | Two enemies with near-identical outline |
| Edge quality | Visual crop at 400 percent on dark and light backgrounds | Halos |
| Perf contribution | Texture memory formula; `perf_budget.py` | Atlas over budget |

Only assets that pass go to critique (`skills/art-direction/references/art-critique-rubric.md`).

## 12. The manifest

The project manifest is `.gamestudio/assets/manifest.json`, validated by `${CLAUDE_PLUGIN_ROOT}/scripts/schemas/asset-manifest.schema.json`. `studio-gateway` appends an entry for every generation with `status: "candidate"`. Per-asset fields:

| Field | Meaning |
|---|---|
| `id`, `path` | Unique id; path under the assets directory (required) |
| `kind` | sprite, spritesheet, ui, icon, background, tileset, texture, model, animation, vfx, music, sfx, voice, font, video, other |
| `status` | placeholder, candidate, approved, rejected, final |
| `placeholder` | True for mock or hand-made stand-ins; never ships |
| `provider`, `model` | Who and which version generated it |
| `prompt`, `negative_prompt`, `seed`, `params` | Reproducibility inputs |
| `references`, `style_ref` | Paths of reference images (provenance) |
| `licence` | Terms recorded by the gateway (plan tier, commercial flag, notes) |
| `cost_usd`, `created_at`, `sha256` | Budget and integrity |
| `approved_by` | Who signed off (human for style and store art) |
| `derived_from` | Source asset id for post-processed or edited versions |
| `notes` | Manual edits, tournament result, bible version |

Add the bible version to `notes` (or a `params` entry) so stale assets can be found after a style change.

## 13. Manifest discipline

1. **No asset without an entry.** Everything under the generated directory and every engine-imported art asset has a manifest entry; the post-tool hook reminds when a binary asset is missing from the manifest.
2. **Statuses move forward through gates**: candidate -> approved (after objective checks, critique and, where required, human sign-off) -> final (shipped in a release candidate). Rejected assets stay in the manifest with the reason in `notes`; do not delete provenance.
3. **Derived files link to sources** with `derived_from`; hand-edited assets say what was changed.
4. **Hand-made or placeholder content is marked** (`placeholder: true` or provider `human`), because disclosure and copyright depend on the mix.
5. **Update through the tool**: `manifest_update` {asset_id, status, approved_by, notes, licence}; avoid editing the JSON manually, and validate with `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_json.py` when you must.
6. **Run `licence_check` before every release candidate** and before any batch is marked approved.
7. **Keep hashes**: `sha256` detects silent replacement of files.
8. **Snapshot the manifest** into the release evidence so disclosure text is reproducible for that build.

## 14. Licence allowlist

Maintain an explicit allowlist in `.gamestudio/config.json` provider preferences and in the bible's AI lock.

| Category | Rule |
|---|---|
| Allowed providers | Providers with commercial rights on the plan in use, official APIs, recorded plan tier (`GS_PLAN_<PROVIDER>`) |
| Plan tier | Paid only for shipping assets; free tiers are allowed for exploration only and their outputs are tagged and excluded from approval |
| Attribution licences (for example CC BY) | Allowed only if attribution is carried in the credits; prefer paid tiers that remove it |
| Non-commercial licences (weights or services) | Not allowed in the shipping path |
| Regional exclusions | Check the audience region before using a model with exclusions |
| Revenue-threshold licences | Record the threshold; `licence_check` compares with `config.revenue` |
| Third-party reference material | Only material the studio owns or has licensed; record in `references` |
| Fonts and audio inside marketing assets | Licence checked separately; recorded in the manifest |

Re-check terms at each batch start; terms change. Record the date you read them in `notes`.

## 15. Copyright posture

- In the US, purely AI-generated material is not copyrightable; protection attaches to human authorship such as selection, arrangement and substantial edits (reported from the US Copyright Office guidance and case law; verify, and consult counsel for your jurisdiction).
- Consequence: you may be unable to stop others copying raw AI assets. Strengthen ownership by adding real human authorship to what matters most: logo, hero characters, key art, UI identity, level layouts, animation and final compositing; record those edits in the manifest.
- Trademarks and likenesses: do not prompt for or ship real people, franchise characters or brand marks; reject outputs that resemble them even by accident.
- Training data risk: models may reproduce copyrighted style or content; screen for near-copies of famous characters and for visible watermarks; prefer providers with clear commercial terms.
- Keep prompts and references as evidence of the creative process.
- IP indemnity is limited or absent for most tools in the notes; accept the residual risk consciously for hero IP and prefer human-made assets for the core brand.

## 16. Disclosure

Platforms are moving toward disclosure of generated content. Do not hard-code rules; read them at release (see volatile facts).

Procedure:
1. Query the manifest for generated assets that ship (`manifest_query` with `status: final`, provider not human).
2. Classify: player-facing in-game content, store page and marketing assets, internal development tools.
3. Generate the disclosure text from the manifest (providers, asset kinds, where used, human editing).
4. Verify against each store's current rules and fill the store's AI-content questionnaire honestly.
5. Keep the disclosure draft with the release evidence; the compliance officer agent reviews it (`skills/legal-ethics`, `skills/store-release`).
6. If live-generated content exists in the game (generated at runtime for players), it needs guardrails, moderation and often stricter disclosure and age rules.
7. If personal data goes to a third-party AI service from the game, consent rules apply (see section 17).

## 17. Privacy and data

- Do not send player data, internal confidential material or unreleased IP to providers whose terms allow training on inputs without checking those terms.
- Reference images that contain identifiable people require consent.
- The reported Apple guideline requires explicit consent before sending personal data to third-party AI services; verify the current text.
- Keys come only from environment variables populated from plugin `userConfig`; never write keys into prompts, manifests or logs.

## 18. Volatile facts (as of Oct 2026 - verify)

| Fact | Source |
|---|---|
| Valve rewrote Steam AI disclosure rules in January 2026: internal dev tools no longer need disclosure; player-facing generated content, store page assets and marketing materials, and live-generated content still do; developers liable for guardrails | https://blog.promise.legal/ai-game-assets-copyright-steam-disclosure-2026/ |
| Google Play: a law-firm analysis says policy does not expressly require disclosing AI use in descriptions, though omission may mislead if AI is a key feature; August 2026 developer blog reiterates generative-AI app requirements against non-consensual sexual content | https://www.revera.legal/?p=3557 |
| Apple: AI-generated content must not deceive; guideline 5.1.2(i) reportedly requires explicit consent before sending personal data to third-party AI services (primary text not verified) | https://blog.promise.legal/ai-game-assets-copyright-steam-disclosure-2026/ |
| US Copyright Office: purely AI-generated works not copyrightable; prompts alone do not give sufficient control (Part 2 report, 29 January 2025) | https://blog.promise.legal/ai-game-assets-copyright-steam-disclosure-2026/ |
| Adobe: non-Adobe partner models fall outside Firefly IP indemnity (terms effective 8 May 2026) | https://helpx.adobe.com/uk/legal/product-descriptions/partner-model.html |
| BRIA RMBG 2.0 is CC BY-NC 4.0; commercial use needs an agreement or the vendor API | https://github.com/Bria-AI/RMBG-2.0 |
| Recraft: paid plans own outputs with commercial rights; free plan outputs owned by Recraft and non-commercial | https://www.recraft.ai/pricing?tab=api |
| PixelLab: commercial use allowed; outputs may not train new models; Steam disclosure applies | https://www.pixellab.ai/llms-full.txt |
| Leonardo: commercial rights on paid plans only | https://docs.leonardo.ai |
| FLUX licences: only klein 4B reported Apache 2.0; other variants non-commercial for self-hosting; sources conflict on outputs | Research notes (2D art, licensing section); verify at the vendor |
| Recraft post-processing prices (background removal and vectorize about 0.01, crisp upscale about 0.004) | https://www.recraft.ai/pricing?tab=api |
| OpenAI transparent-background preview for gpt-image-2 (reported 21 August 2026) | https://docs.apiyi.com/en/live/2026-08/gpt-image-2-transparent-background |
