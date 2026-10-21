# Art asset brief: [batch name]

Revision: [date] | Requester: [name] | Producer: [human / pipeline] | Due: [date]

<!-- One brief per batch of similar assets. The style bible governs the look; this brief governs the list, specs and acceptance. Missing specs are the top cause of rework. -->

## Purpose
[Which feature or screen needs these and why now. Link the feature spec.]

## Asset list
| ID | Name | Type (icon / sprite / bg / VFX / UI) | Size (px) | States / frames | Priority |
|---|---|---|---|---|---|
| [A001] | [..] | [..] | [..] | [..] | [P0-P2] |

## Per-asset description
<!-- Describe what must be readable, not how to draw it. One short paragraph per distinct asset, or per family when they share a template. -->
- [A001]: [subject, pose or angle, mood, distinguishing details, what must read at small size]

## Style and references
- Style bible version: [rev]; approved samples: [file links]
- Specific references for this batch: [links] (inspiration only)
- Must match: [existing assets by ID]

## Technical spec
| Item | Value |
|---|---|
| Format | [PNG with alpha / SVG / layered] |
| Color space and bit depth | [sRGB, 8-bit] |
| Background | [transparent / flat key color] |
| Padding and pivot | [px, anchor point] |
| Naming | [pattern, e.g. `ui_icon_<name>_<size>.png`] |
| Atlas group | [name] |
| Max file size / texture memory | [..] |

## Variants
- Resolutions: [1x / 2x / 3x or single master downscaled]
- Themes, skins or color variants: [..]
- Localization (text in image): [avoid; if unavoidable, list languages]

## Acceptance checklist
- [ ] Silhouette readable at 48 px
- [ ] Palette within style bible; contrast checked
- [ ] No stray pixels or halos on transparent edges (`image_post.py` check)
- [ ] Consistent lighting direction and outline weight
- [ ] Naming, size and padding correct
- [ ] Licence and provenance recorded; AI-generated flagged
- [ ] Reviewed by `art-director`; revisions logged

## Pipeline notes
- Generation: [tool, model version, seed, prompt reference] or Production: [artist]
- Batch size and review cadence: review the first 3 before producing the rest
- Rework budget: [max rounds per asset]
