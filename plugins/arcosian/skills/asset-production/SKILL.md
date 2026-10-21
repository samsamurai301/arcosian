---
name: asset-production
description: Runs the visual asset pipeline for a mobile game - style bible, asset list from the contract, style lock, generation through the studio-gateway tools, post-processing, engine import, manifest status flow and licence checks. Use when the user says "make the art", "generate sprites", "asset batch", "lock the style", "build the asset list" or "import these assets".
argument-hint: "[asset kind or list]"
---

# Asset Production

## When to use
Any time visual assets (sprites, UI, icons, backgrounds, tilesets, textures, 3D models, VFX sheets) are created, imported or promoted. Load `art-direction`, `ai-asset-pipeline` and `technical-art` for theory; this skill is the procedure. Delegate judgment to `arcosian:art-director`, import and atlas work to `arcosian:technical-artist`, licence questions to `arcosian:compliance-officer`.

## Inputs
`$ARGUMENTS` is either an asset kind (`sprite`, `ui`, `icon`, `background`, `tileset`, `texture`, `model`, `vfx`), a path to an asset list file, or empty (meaning: derive the whole list from the contract). Requires `.gamestudio/contract.json` with `art_direction`; if missing, stop and route to `new-game`.

## Procedure
1. **Preconditions.** `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py status` and `... budget`. Call `gs_status` (studio-gateway) to see which providers are configured and whether mock mode is on. Mock output is placeholder only and must never be promoted past `placeholder`.
2. **Style bible first.** If `contract.art_direction.bible_ref` is empty, copy `${CLAUDE_PLUGIN_ROOT}/templates/docs/style-bible.md` to `.gamestudio/art/style-bible.md` and have `arcosian:art-director` fill it: silhouette rules, palette (run `skills/art-direction/scripts/palette_audit.py`), line weight, lighting, camera, texture density, readability at the smallest on-screen size, forbidden motifs, reference list. Write the path back to `art_direction.bible_ref`. No generation before the bible exists; unlocked style is the main cause of rework.
3. **Asset list from the contract.** Derive from `mechanics[].feedback`, `ux.screens`, `content.worlds/characters`, `monetization.iap[].contents`, store needs (icon, feature graphic). Each row: id, kind, size at 1x and target density, variants (states, directions), animation frames, priority P0/P1/P2, transparency needed, tier it must reach. Write to `.gamestudio/assets/asset-list.md`. Register P0 items in the manifest as `placeholder` with `placeholder: true` so the game builds immediately with greyboxed art.
4. **Style lock** (do once, then reuse). Order matters:
   a. Bible sheet: 4-6 hero images (one character, one prop, one environment, one UI panel) via `image_generate` with `n: 4`.
   b. Tournament: judge candidates pairwise, not by absolute score. `python3 ${CLAUDE_PLUGIN_ROOT}/skills/art-direction/scripts/tournament_rank.py schedule ...` then `next` / `rank` (see its `--help`); vision-critique passes are combined with `python3 ${CLAUDE_PLUGIN_ROOT}/skills/art-direction/scripts/critique_aggregate.py --in reviews.json --tier <tier>`.
   c. Reference set: promote winners to `approved`, store them under `assets/style/`, pass them as `references` and `style_ref` on every later call.
   d. LoRA / fine-tune only if a provider supports it (e.g. via `fal`), the reference-image approach drifts after ~20 assets, and budget allows. Record the model id in `config.providers`. Default is references plus a fixed prompt prefix and fixed seed policy.
   **Human checkpoint 1:** the user approves the style lock (bible sheet plus winner) before bulk generation.
5. **Generate.** Always `dry_run: true` first to read the cost estimate, then real calls. Tools: `image_generate` (prompt, kind, provider, references, transparent, seed, style_ref), `image_edit` for fixes (prefer edit over regenerate to keep identity), `image_postprocess` (`remove_background`, `vectorize`, `upscale`), `model3d_generate` / `model3d_status` for 3D. Build prompts from the bible prefix + subject + framing + negative prompt; keep the exact prompt in the manifest. Batch many assets via `/arcosian:asset-batch`.
6. **Post-process.** `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/image_post.py check --in <png> --json` (size, alpha, power-of-two, edge halos), `palette`, `resize`, `pixelate` (pixel art), `atlas` for sheets. Use TexturePacker or the engine's own atlas packer where animation or trimming matters. Fix halos, off-centre pivots and inconsistent scale here, not in-engine.
7. **Engine import.** Settings by kind:

| Kind | Godot 4 | Unity 6 |
|---|---|---|
| Pixel art | Filter off (Nearest), no mipmaps | Point filter, no compression, PPU consistent |
| Smooth sprites / UI | Linear, mipmaps off for UI | Sprite mode, compression tuned per platform |
| Large backgrounds | VRAM compressed (ETC2/ASTC on mobile) | ASTC, max size capped |
| 3D textures | VRAM compressed, mipmaps on | ASTC, mipmaps on, sRGB only for colour maps |
| Atlases | One atlas per screen or biome | Sprite Atlas v2, include in build |
Check the memory budget in `contract.technical.perf_budgets` with `arcosian:technical-artist`; see `mobile-performance`.
8. **Status flow.** `placeholder -> candidate -> approved -> final` (side exit: `rejected`). Gateway writes `candidate`. Use `manifest_update {asset_id, status, approved_by, notes}`. `approved` needs an art-director pass (and `critique_aggregate.py` verdict for batches). `final` needs steps 6, 7 and 9 done.
   **Human checkpoint 2:** a human signs off every asset that is player-facing at first sight (icon, hero character, title screen) before `final`; record in `approved_by`.
9. **Licence check.** `licence_check {}` for the whole manifest before any `final`. It flags non-commercial terms, free-tier ownership problems and missing provenance. Resolve every flag or reject the asset. Keep AI-disclosure facts for `ship`.
10. **Visual gate evidence.** Capture screenshots in context (engine screenshot mode), save under `.gamestudio/evidence/<FEATURE-ID>/`, attach to the feature's `visual` gate via `gs.py feature`.

## Outputs
`.gamestudio/art/style-bible.md`, `.gamestudio/assets/asset-list.md`, generated files under `config.paths.generated_dir`, updated `assets/manifest.json` and `budget.json`, engine-imported assets, critique and tournament records under `.gamestudio/art/`.

## Quality gates
- Bible exists and `bible_ref` set; every asset has `style_ref`.
- Every manifest entry has prompt, provider, model, licence and sha256; `licence_check` clean.
- No `final` asset with `placeholder: true`; no mock output shipped.
- Spend within `budget.json` cap (`budget_status`).
- Assets pass `image_post.py check` and meet size/memory budgets on the lowest device tier.
- Legible at the smallest real on-screen size (test on device or at 1x downscale).

## Failure modes and recovery
| Symptom | Cause | Fix |
|---|---|---|
| Style drifts across batch | References not passed, prompt prefix edited | Re-pass `style_ref`, regenerate with `image_edit` against an approved asset |
| Halo or fringe on cut-outs | Background removal on busy background | Generate on flat colour, or `transparent: true`, then `image_post.py check` |
| Budget refusal | Estimate exceeds cap | Lower `n`, smaller size, raise cap only with user approval |
| Provider unconfigured | Empty key, mock output | Say so; keep placeholders; ask user to set the key in plugin settings |
| Hands, text, symmetry errors | Model limits | Crop, edit, hand-fix, or redesign to avoid |
| Licence flag | Free-tier or non-commercial terms | Reject or regenerate on a paid tier; never ship |

## Decision tables

**Which tool for which need**

| Need | Tool | Notes |
|---|---|---|
| New 2D image from text | `image_generate` | Pass `references` and `style_ref` after the lock |
| Fix one flaw, keep identity | `image_edit` | Cheaper and safer than regenerating |
| Transparent sprite | `image_generate` with `transparent: true`, else `image_postprocess remove_background` | Verify edges with `image_post.py check` |
| Flat logo/icon shape | `image_postprocess vectorize` | Good only for simple shapes |
| Low-res source needing detail | `image_postprocess upscale` | Re-check style consistency afterwards |
| Prop or character in 3D | `model3d_generate` then `model3d_status` | Set `face_limit` for mobile; retopo and bake in the DCC if rigged |
| Find or reuse an asset | `manifest_query` | Query before generating anything |

**Generate vs. buy vs. hand-make:** generate for volume and exploration; buy or commission for the hero set (icon, key art, main character) when the budget allows, because ownership and consistency are cleaner; hand-make where precision is the point (UI frames, 9-slice, pixel-perfect type).

## Worked example: a 40-item puzzle game list
Contract says portrait, flat vector-ish style, 12 tile types. List: 12 tiles x 2 states, 6 UI panels, 8 icons, 3 backgrounds, store icon, feature graphic. Register all 55 as placeholders (flat colour rectangles) on day one. Style lock uses one tile, one panel, one background. After approval, generate tiles in batches of 4 with the same prefix and seed policy, tournament each batch, edit the one off-model tile instead of rerolling. Pack tiles into one atlas, import with Linear filter and no mipmaps, run a visual gate screenshot on a low-tier device. Cost is read from `budget_status` after each batch, and the batch stops when it reaches 80 percent of the cap so the user can decide.

## Batch discipline
- One kind per batch, one style per batch.
- Estimate first (`dry_run`), then stop at 80 percent of cap.
- Judge in pairs, promote winners, reject the rest with a reason in `notes`.
- Log the batch in `.gamestudio/progress.md` via `gs.py progress`.

## Naming and folders
`assets/generated/<kind>/<id>.png` for candidates, `assets/<kind>/<id>.png` for approved imports, `snake_case` ids stable across states (`tile_07_idle`). Never overwrite an approved file in place: derive a new asset with `derived_from` so the history stays auditable.

## Volatile facts (as of Oct 2026 - verify)
Provider names, model ids, list prices and licence terms for image and 3D services change often. The studio-gateway keeps defaults in `mcp/studio-gateway/pricing.json` with an "as of Oct 2026, verify" note; read it instead of trusting memory, and confirm commercial-use terms on the provider's current terms page before promoting anything to `final`. Source for pricing and model ids: the provider docs, for example https://ai.google.dev/gemini-api/docs/pricing and https://platform.openai.com/docs/pricing.

## Related skills
`art-direction`, `ai-asset-pipeline`, `technical-art`, `mobile-performance`, `legal-ethics`, `audio-production`.
