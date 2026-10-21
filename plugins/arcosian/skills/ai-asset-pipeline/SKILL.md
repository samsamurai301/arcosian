---
name: ai-asset-pipeline
description: AI visual asset pipeline for games - 2D and 3D model landscape and licences, style lock and prompt templates, tournament selection, background removal, upscaling, palette and sprite-sheet post chains, 3D cleanup, manifest provenance, disclosure, and studio-gateway usage with budgets. Use when generating sprites, icons, key art or 3D props with AI, keeping a style consistent, choosing a provider, or preparing provenance and AI disclosure.
---

# AI Asset Pipeline

## What this skill gives you

- A provider selection method and a dated landscape of image, game-art and 3D generators, with licence and exclusion rules.
- The consistency recipe: style frame, reference set, locked prompt block, seed policy, trained style models, drift control.
- Prompt templates per asset type and a failure catalogue with mitigations.
- Post-processing chains for 2D, pixel art, sprite sheets and 3D, ending in objective checks.
- Provenance discipline: manifest fields, status gates, licence allowlist, copyright posture, store disclosure.
- Exact usage of the `studio-gateway` tools, mock mode, budgets and call patterns.

## Core models

1. **Generation is cheap; acceptance is expensive.** Judge cost per accepted asset: `(candidates x price) / acceptance_rate + post + human time`. Improve acceptance (lock, references, templates) before buying a pricier model.
2. **Consistency is engineered.** Same locked block, same references, pinned model id, same post chain, plus a gate that rejects drift. Prompting harder is the weakest lever.
3. **Climb the consistency ladder only as needed.** Locked prompt, then references, then multi-reference edits, then a trained style model, then graph pipelines.
4. **Native output beats repair.** Native transparency, native pixel grid, native vector, native low-poly. Post steps are for finishing, not for rescuing the wrong form.
5. **Compare, do not score.** Select among candidates by pairwise tournament in both orders; a human picks among the top for style-defining and store-facing art.
6. **Every asset has provenance.** Provider, model, prompt, seed, references, licence, cost, approver and edits are in the manifest, or the asset does not ship.
7. **Licence before quality.** A beautiful asset from a non-commercial tier or weights is a liability. Paid, commercial-rights plans only for shipping assets.
8. **Human authorship carries ownership.** Purely generated art is weakly protected; add real human work to hero IP and record it.
9. **The gateway is the only door.** Budget checks, manifest entries and licence rules live there; ad hoc API scripts bypass them.
10. **Humans sign off on style and store art.** Everything between checkpoints runs automatically.

## Decision procedures

### Choose a provider for an asset class

1. Filter by licence (paid plan, commercial rights, no non-commercial weights, region fine).
2. Filter by automatability (official API or MCP; terms allow automation).
3. Match output form: pixel, vector, transparent, sprite sheet, low-poly mesh, rig.
4. Pilot two candidates with the lock on six subjects; compare by tournament at phone size.
5. Compute cost per accepted asset; pick; record the choice and date in the bible.
Defaults and market context: `references/model-landscape-2026.md`; gateway mapping: `references/gateway-usage.md`.

### Lock a style for generation

1. Get the human-approved style frame and sheet (see `art-direction`).
2. Write the locked block (style, palette, light, camera, material, background, negatives).
3. Test on five diverse subjects; revise until they look like siblings; run the palette audit.
4. Freeze as lock v1.0 in the bible with model id, references, seeds and date.
5. Re-test a golden set after any model update; reject updates that lose by tournament.

### Run an asset batch

1. `gs_status`, `budget_status`; read lock and allowlist.
2. List assets from content units; estimate cost.
3. Mock pilot, real pilot of 6-10; measure acceptance and cost.
4. Full batch in stages with spend checks.
5. Pre-filter (`image_post.py check`, `palette_audit.py`), tournament contested classes, human pick for key assets.
6. Post chain per class, objective checks again.
7. Visual critique gate; `manifest_update` to approved; `licence_check`.
8. Import, run feature gates, report counts and spend.

### Pick the best candidate

```
python3 ${CLAUDE_PLUGIN_ROOT}/skills/art-direction/scripts/tournament_rank.py schedule --items c01,c02,c03,c04 --mode roundrobin
python3 ${CLAUDE_PLUGIN_ROOT}/skills/art-direction/scripts/tournament_rank.py rank --votes votes.json --min-margin 0.65 --json
```
Pre-filter first, show judges the image at phone size, send the top two or three to the human.

### Clean a 3D model for mobile

Request low-poly (`face_limit`), inspect, remesh or decimate with protection, UV, de-light, rig and cap influences at 4, map to the project shader, gltfpack, LODs, headless import, budget check, manifest edits. Details: `skills/technical-art/references/texture-and-3d-pipeline.md`.

### Prepare provenance and disclosure before a release candidate

1. `licence_check {}` with `GS_PLAN_<PROVIDER>` set; fix every error; justify warnings.
2. Confirm no `placeholder` asset is `approved` or `final`.
3. `manifest_query` shipping assets by provider and kind; draft disclosure text; classify player-facing, store-page and tooling use.
4. Verify current store rules (volatile) and answer questionnaires honestly; hand to `compliance-officer`.
5. Keep the manifest snapshot in the release evidence.

## Mobile specifics

- Generate large masters, deliver small: crisp edges and room to crop; the shipped size is dictated by the class spec and texture budget.
- Judge at phone size: downscale candidates in tournaments so detail that vanishes does not win.
- Atlas, compression and memory budgets shape every class chain; check them in the post chain, not at the end.
- Keep prompts free of player data and confidential material; references and prompts are sent to third parties.
- Low-poly and fixed-camera games get the most from AI 3D; characters need rig and weight cleanup.
- Store listing art is generated and disclosed differently from in-game art; track it separately.
- Budgets are real money: pilot first, stage the batch, stop when acceptance falls.

## Anti-patterns

| Anti-pattern | Detect | Fix |
|---|---|---|
| Rewriting the style prompt per asset | Look drifts within a dozen assets | Locked block plus one subject line |
| Choosing by arena rank | Great demos, poor consistency | Pilot and tournament on your own subjects |
| Free-tier outputs in the build | `licence_check` warnings, unknown plan | Paid plan; regenerate; tag exploration assets |
| Non-commercial segmentation or weights | Tool licence says non-commercial | Replace with a licensed service or model |
| Midjourney or wrapper services | No official API, bans automation | Use allowed providers |
| Generative upscale on pixel art | Soft, invented pixels | Native pixel tools; integer scaling |
| Text baked into generated art | Garbled words | Add text in layout |
| Regenerating to tweak an approved asset | Identity changes | Edit mode from the approved source |
| Asset without manifest entry | Binary in assets, not in manifest | Register; fill provenance; run the hook reminder |
| Placeholders in a release | Mock files approved | Replace; block via `licence_check` |
| Ignoring model version changes | Batch shifts after an update | Pin ids; golden-set regression |
| Auto-shipping store art from a model vote | No human sign-off | Human checkpoint |
| Unreviewed community MCP with keys | Unknown source, broad permissions | Prefer gateway or vetted official servers |

## Using the ontology

- Assets are content units; the manifest (`.gamestudio/assets/manifest.json`, schema `${CLAUDE_PLUGIN_ROOT}/scripts/schemas/asset-manifest.schema.json`) records kind, status (placeholder, candidate, approved, rejected, final), provider, model, prompt, seed, references, licence, cost, approver, derivation and notes.
- Configuration (`.gamestudio/config.json`): `budgets.asset_usd_cap`, `budgets.per_call_usd_cap`, `paths.generated_dir`, provider preferences, `revenue` for licence thresholds.
- The style bible AI lock section (see `art-direction`) is the contract this pipeline follows.
- Tools: `studio-gateway` (`image_generate`, `image_edit`, `image_postprocess`, `model3d_generate`, `model3d_status`, `manifest_query`, `manifest_update`, `licence_check`, `budget_status`, `kb_search`); scripts `${CLAUDE_PLUGIN_ROOT}/scripts/image_post.py` (check, palette, resize, pixelate, atlas), `${CLAUDE_PLUGIN_ROOT}/scripts/validate_json.py`, and the `art-direction` scripts for palette, tournament and critique.
- Workflow: `/arcosian:asset-batch` runs this pipeline with agents; the process skill `asset-production` is the user-facing entry.

## Reference library

| File | What it contains | When to read it |
|---|---|---|
| `references/model-landscape-2026.md` | Selection logic, capability matrix, general and game-specialized 2D models, 3D generators, MCP servers, licences, excluded vendors, defaults, volatile prices with sources | Choosing or revisiting providers; checking licence posture |
| `references/style-lock-and-prompts.md` | Consistency ladder, style lock, locked block, references, seeds, prompt templates per asset type, failure catalogue, tournament selection, LoRA training, drift control, batch procedure | Starting a batch; fixing inconsistency |
| `references/post-processing-and-provenance.md` | 2D and 3D post chains, background removal, palette and pixel-art handling, sprite sheets, atlases, objective checks, manifest discipline, licence allowlist, copyright, disclosure, volatile rules | After generation; before approval and release |
| `references/gateway-usage.md` | Gateway tools and parameters, mock mode, budgets, provider choice per asset type, call patterns, errors, batch workflow, security, gaps | Any time you call `studio-gateway` |

## Related skills

- `art-direction`: style bible, palette audit, critique rubric and tournament scripts used here.
- `technical-art`: texture, mesh, shader and VFX budgets that assets must meet.
- `asset-production`: the user-facing command that runs this pipeline through the `asset-batch` workflow.
- `ai-audio-pipeline`: the audio counterpart on the same gateway.
- `legal-ethics`: copyright, disclosure and licence risk decisions.
- `store-release`: store AI-disclosure questionnaires and listing art requirements.
- `marketing-ua`: creative testing built on generated key art and ads.
- `mobile-performance`: memory and size budgets for imported assets.
