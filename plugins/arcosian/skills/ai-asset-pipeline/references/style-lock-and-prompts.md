# Style Lock and Prompts

How to keep hundreds of AI-generated assets looking like one game: the consistency recipe (style frame, reference set, locked prompt block, seeds, trained style model), prompt templates per asset type, a negative-prompt and failure catalogue, and the selection step (pre-filter, tournament, human pick). The core idea is that consistency is engineered, not prompted: every asset is generated from the same locked inputs, through a gate that rejects drift, and the lock is versioned in the style bible. Tool and model names are examples; the method is model-agnostic. Pairwise selection uses `skills/art-direction/scripts/tournament_rank.py`.

## Contents

1. [Why consistency fails](#1-why-consistency-fails)
2. [The consistency ladder](#2-the-consistency-ladder)
3. [Building the style lock](#3-building-the-style-lock)
4. [The locked prompt block](#4-the-locked-prompt-block)
5. [Reference sets](#5-reference-sets)
6. [Seeds and determinism](#6-seeds-and-determinism)
7. [Prompt anatomy and templates](#7-prompt-anatomy-and-templates)
8. [Templates by asset type](#8-templates-by-asset-type)
9. [Negative prompts and failure catalogue](#9-negative-prompts-and-failure-catalogue)
10. [Candidate counts and selection](#10-candidate-counts-and-selection)
11. [Training a style model](#11-training-a-style-model)
12. [Drift control over time](#12-drift-control-over-time)
13. [Batch procedure](#13-batch-procedure)
14. [Worked example](#14-worked-example)

---

## 1. Why consistency fails

| Cause | Symptom | Countermeasure |
|---|---|---|
| Prompt paraphrase | Each asset described slightly differently | One locked block, assets add only a subject line |
| No visual anchor | Colours, line weight and lighting wander | Reference images with every call |
| Model or version change | Whole batch shifts after a provider update | Pin model id; record in the manifest; re-test on update |
| Too many subjects per image | Characters merge, props change | One main subject per call; compose later |
| Random seeds | Non-reproducible results | Seed policy, where the provider exposes seeds |
| Post-processing differences | Edge, scale and palette vary | Same post chain for every asset class |
| Human taste drift | Approved set slowly moves | Drift review against the launch set |

## 2. The consistency ladder

Climb only as far as the project needs; each rung costs more.

| Rung | Method | Good for | Cost |
|---|---|---|---|
| 1 | Locked text prompt block | Under about 20 assets, simple styles | Lowest |
| 2 | Locked prompt plus style reference images | About 20-100 assets | Low |
| 3 | Multi-reference edit with a character or world sheet | Characters, variants, poses | Medium |
| 4 | Trained style or character model (LoRA) on 20-50 approved images | 100+ assets, strong identity | Training fee plus time |
| 5 | Graph pipeline with ControlNet, IP-Adapter and seeds (ComfyUI) | Exact poses, deterministic batch | Highest maintenance |

Decision rule: start at rung 2. Move up when the acceptance rate for the asset class falls below about 40 percent after prompt tuning, or when identity must persist across poses (heroes).

## 3. Building the style lock

1. **Style frame**: a human-approved image (or set) that defines the look (see `skills/art-direction/references/style-selection-and-bible.md`). Generate many, pick by tournament, finish by hand.
2. **Sheet**: character turnaround, expression sheet, prop sample, tile sample, UI sample, palette swatches. These are your reference set.
3. **Extract the vocabulary**: describe the style in observable terms (line weight, shading bands, palette names, material cues, camera). Avoid artist names and trademarked franchise names.
4. **Write the locked block** (section 4) and test it on five diverse subjects. Revise until the five look like siblings.
5. **Measure**: palette audit and silhouette checks on the five (`skills/art-direction/scripts/palette_audit.py`).
6. **Freeze** as lock v1.0 in the style bible, section 9 of the template, with model id, provider, seeds used, reference paths and date.

## 4. The locked prompt block

Structure the block in a fixed order so changes are diffable:

```
STYLE: <family>, <line description>, <shading description>, <detail density>.
PALETTE: <named colours with hex>, limited to these, shadows shift toward <hue>.
LIGHT: <direction, softness>. CAMERA: <angle, framing>.
MATERIAL: <surface language>.
BACKGROUND: <plain flat colour | transparent | none> (assets are generated on a single flat colour for later keying unless native transparency is available).
NEGATIVE: <list from section 9>.
```

Per-asset prompt = `SUBJECT: <one sentence>` + locked block + asset-type template (section 8). Never rewrite the locked block per asset.

Rules:
- Specific beats evocative: "3 px dark outline, two flat shadow bands" beats "cute and clean".
- Use palette names plus hex; models follow hex loosely, so enforce palette in post (palette quantize or map).
- Do not include text to be rendered in the image unless the model is known to handle it; add text in the engine or in layout.
- Keep the block short enough that the subject remains the strongest instruction (heuristic: block under about 120 words).

## 5. Reference sets

- Use 2-6 references per call: the style frame, one on-style example of the same asset class, and for characters the turnaround sheet. More references dilute attention; the notes report that edit models handle 1-2 primary characters reliably even though more references are accepted.
- Tag references in the prompt ("image 1 is the style reference; image 2 is the character") when the API supports labelled references.
- Store references under `assets/_bible/refs/` and list them in the lock; pass them through the gateway's `references` parameter (`image_generate`, `image_edit`) and `style_ref` where supported.
- When the approved set grows, rotate in fresh approved assets as references to prevent the model from over-fitting to the first frame, but keep the original style frame in every set as the anchor.
- Never use another studio's or artist's copyrighted art as a reference for a shipping style; references are provenance and are recorded in the manifest.

## 6. Seeds and determinism

- Where a provider exposes a seed (the gateway's `seed` parameter), record it; with the same model, prompt, references and seed you can often reproduce or minimally vary an asset. Hosted models change under the same name, so reproducibility lasts only as long as the model id does.
- Use a **seed policy**: a fixed base seed per asset class for exploration; incrementing seeds for candidates; the winning seed stored in the manifest.
- To make a variant of an approved asset, use edit mode with the approved image as the source, not a new generation with a similar prompt.
- Providers without seeds: reproducibility comes from references and edit mode; store the output file and treat it as the artifact.
- Do not rely on seeds across model versions. Re-test a handful of approved prompts after any model update and compare by tournament against the old outputs.

## 7. Prompt anatomy and templates

Order of information: (1) subject, (2) action or pose, (3) framing and camera, (4) style block, (5) background and output form, (6) negatives. Models weight early text more.

Variation controls (use one at a time so that you learn what changed): pose, expression, colour variant within the palette, costume part, prop.

Edit-mode prompt pattern:

```
Keep exactly: <what must not change: silhouette, face, outfit colours, line weight>.
Change only: <the single change>.
Do not alter: background, canvas size, style.
```

## 8. Templates by asset type

Each template is appended after the locked block. Replace angle brackets.

**Character (concept sheet)**
```
SUBJECT: <name>, <role>, <one-line description>. Turnaround: front, side, back, 3/4 view, same scale, neutral pose, on a flat <colour> background, evenly spaced, no overlap, no text.
```

**Character pose (edit mode, reference = sheet)**
```
Draw the character from image 2 <pose>, in the style of image 1. Same proportions, costume and palette. Single character, flat <colour> background, full body in frame, feet visible.
```

**Item / pickup / icon**
```
SUBJECT: <item>. Single object, centred, three-quarter view, large readable silhouette, fills about 80 percent of the frame, flat <colour> background, no shadow on the ground, no text.
```

**UI element (button, panel)**
```
SUBJECT: <element> for a mobile game UI, front view, no perspective, symmetrical, empty centre for content, clean edges suitable for 9-slice, flat <colour> background.
```

**Tile / texture**
```
SUBJECT: seamless tileable <surface>, top-down orthographic, even lighting, no focal point, no objects crossing edges, <size> square.
```
Tile seam check: offset by half and inspect; fix seams by hand or with an inpainting step.

**Background / environment**
```
SUBJECT: <scene> backdrop for a <genre> mobile game, <time of day>, depth layers (foreground, midground, background) clearly separated, low-contrast detail in the play area, no characters, portrait <aspect>.
```
Generate layers separately when parallax is needed.

**Sprite sheet (grid)**
```
SUBJECT: <character> sprite sheet, <N> frames of <action> in a <cols> x <rows> grid, each cell the same size, character the same scale and position in every cell, side view facing right, flat <colour> background (#00ff00 style keying colour not used in the character), no cell borders, no text.
```
Expect misalignment; use the post chain. Prefer platform tools with native animation when budgets allow.

**Pixel art**
```
SUBJECT: <sprite>, <W> x <H> pixel sprite, <N> colour palette from the reference, no anti-aliasing, no gradients, one pixel outline, flat background.
```
Generate at native pixel size with a pixel-aware tool; for general models, generate large then pixelate and quantize (see `references/post-processing-and-provenance.md`).

**VFX sprite / flipbook frame**
```
SUBJECT: <effect> frame <i> of <N>, centred on black (additive) or transparent background, soft edges, no solid object, no text.
```

**3D model (text or image to 3D)**
```
SUBJECT: <prop or character>, single object, neutral A-pose for characters, clean silhouette, simple shapes, stylized <style family>, no ground plane, no background, low-poly friendly.
```
Prefer image-to-3D from an approved on-style concept image (front or three-quarter view on a plain background); pass `face_limit` for the tier budget.

**Store screenshot background or key art**
```
SUBJECT: <hero> in a dynamic pose, <emotion>, <setting>, composition with a quiet area on the <side> for the headline, <aspect> crop-safe centre.
```
Add text, logos and UI in layout, not in the generator.

## 9. Negative prompts and failure catalogue

Not every API supports negatives; where unsupported, put the constraint positively ("exactly five fingers", "plain flat background").

| Failure | Typical cause | Mitigation |
|---|---|---|
| Extra or fused fingers, odd hands | Hands are hard | Hide hands in the design; hands in pockets or gloves; targeted crop critique; manual fix |
| Garbled or invented text | Text in the prompt | Remove text; add in layout |
| Background not flat | Model adds scenery | State the flat colour; segmentation fix; regenerate |
| Cropped or touching the frame | Subject too large | "fills 80 percent, margin all around" |
| Inconsistent proportions across poses | Weak identity anchor | Turnaround sheet reference, edit mode, LoRA |
| Baked lighting in textures or 3D albedo | Model lights the object | Request "flat, unlit albedo" for texture sources; de-light in post |
| Perspective inconsistency in isometric | Camera not enforced | Reference with the exact angle; prefer sprites from a 3D render for isometric |
| Style drift toward the model default | Weak style block | Stronger references, lower prompt variation, LoRA |
| Watermarks or signature marks | Training artifacts | Reject and flag; remove only if licence allows; log |
| Over-detail at small sizes | Model loves detail | "simple shapes, large forms"; downscale-judge in the tournament |
| Palette leak (extra hues) | Hex ignored | Palette mapping in post |
| Real person or trademark likeness | Prompt or references | Never prompt for a real person or brand; reject likenesses |

Standard negative block (adapt): `text, letters, watermark, signature, extra fingers, deformed hands, blurry, cropped, background clutter, photo realistic (if stylized), inconsistent outline, gradient banding`.

## 10. Candidate counts and selection

| Asset class | Candidates per accepted asset (starting point) | Selection |
|---|---|---|
| Style frames, key art, app icon | 12-24 | Pre-filter, then tournament, then human |
| Hero characters | 8-16 | Tournament, human sign-off |
| Common items and props | 3-4 | Pre-filter, pick by rubric; tournament if close |
| Backgrounds | 4-6 | Rubric and human glance |
| Tiles, UI parts | 2-4 | Objective checks, rubric |
| 3D props | 2-3 | Budget check, silhouette, human sample |

Procedure:
1. **Pre-filter**: automated checks for size, alpha or background, palette audit, garbled text (OCR if available), duplicate detection.
2. **Pairwise tournament** for the contested classes: schedule both orders, collect judgements, rank, require a margin (`rank --min-margin`); see `skills/art-direction/references/art-critique-rubric.md`.
3. **Human pick** from the top two or three for style-defining and store-facing art.
4. **Mark statuses** in the manifest via `manifest_update` (`approved`, `rejected`) with `approved_by`.
5. **Learn**: add the common failures to the negative block; record acceptance rate per class; if it falls, climb the consistency ladder.

Budget the batch before running: `estimated = assets x candidates x unit_price` plus post-processing; compare with `budget_status`.

## 11. Training a style model

When: 100+ assets in one style, or hero characters needing identity across many poses, and rung 2-3 acceptance is poor.

1. **Dataset**: 20-50 approved images that cover the range (subjects, poses, angles); clean backgrounds; no unlicensed material; consistent resolution. Quality beats quantity.
2. **Captions**: short, consistent captions that name the subject and omit style words you want the model to absorb into the trigger.
3. **Train** on a platform with a Training API (Scenario, Leonardo Elements, fal trainers) or self-host an open model with a permissive licence (the notes flag Qwen-Image as Apache 2.0 and the small FLUX klein variant as the only Apache FLUX). Training costs reported by fal are step-based and vary; the notes show conflicting figures, so estimate from the current price page before committing.
4. **Validate**: generate a fixed test set of 12 prompts, compare against the style frame by tournament, run the palette audit, check for overfitting (copied compositions) and for memorized third-party IP.
5. **Version and record**: model id, dataset hash, date, licence of the base model and of the training service; store in the manifest `notes` and in the bible.
6. **Retrain** only on a major style change; do not keep fine-tuning on generated output without human selection, as quality degrades.

Legal note: check that the training service's terms allow commercial use of the resulting model outputs, and that no training image is third-party copyrighted without rights.

## 12. Drift control over time

- Pin model ids; the gateway records `model` per asset.
- Keep a **golden set** of 10 approved prompts and outputs; after any provider update, regenerate and compare by tournament; reject the update if the golden set loses.
- Monthly drift review: sample 12 recent assets, view side by side with launch assets at phone size.
- Bible version bumps trigger the regeneration plan: list assets with older versions and decide rework or sunset.
- Live-ops seasons: derive world palettes and motifs from the bible, keep invariants.

## 13. Batch procedure

1. Read the bible and lock; confirm the lock version and provider allowlist.
2. Build the asset list from content units (ids, class, subject lines, count).
3. Dry run with `dry_run: true` or mock mode to check paths, ids and costs.
4. Generate candidates through `image_generate` with the class template, references and seed policy; ids use a class prefix.
5. Pre-filter, tournament, human pick.
6. Post-process with the class chain, then re-check objectively.
7. Update the manifest status and notes; run `licence_check`.
8. Import into the engine; run the visual critique gate.
9. Report: counts, acceptance rate, cost versus budget, defects found, lock changes.

## 14. Worked example

Project: merge game, 60 item sprites in five tiers, soft cartoon style.

1. Lock v1.0: block names palette and outline rule; references are the style frame plus two approved items.
2. Pilot batch: 6 items, 4 candidates each (24 images). Acceptance 50 percent; failures are outline thickness and stray shadows.
3. Tune: add "no ground shadow" and a numeric outline rule, add a third reference (a tier-3 item). Acceptance rises to about 70 percent.
4. Full batch: 60 items x 3 candidates = 180 images at a cheap bulk model. Pre-filter removes about 15 percent. Tier-5 hero items get 8 candidates and a tournament.
5. Post chain: background removal, trim, palette map, resize to 256, pack atlas.
6. Gate: palette audit passes; critique on the board screenshot at tier `slice`; two items fail silhouette distinctness between tiers 3 and 4; regenerate with an explicit shape difference.
7. Manifest shows model, prompt, seed, references and approver for all 60.
