---
name: art-direction
description: Art direction for games - style selection and style bibles, readability, shape language, value and colour (accessible palettes), asset specs, atlases, 9-slice, icons, store screenshots, key art, and a scored critique rubric with tournament selection. Use when asked to choose an art style, write a style bible, review screens, audit a palette, brief assets, or pick the best AI-generated candidate.
---

# Art Direction

## What this skill gives you

- A way to choose a style by five filters (readability, production capacity, technical fit, differentiation, longevity), not by taste alone.
- A complete, checkable style bible template that humans, agents and image generators all follow.
- The visual fundamentals that make a phone screen read: silhouette, value, colour, hierarchy, physical size.
- Production specs for 2D art: reference resolution, atlases, naming, 9-slice, sprite sheets, icons, store art.
- A critique system that does not trust a single judge: anchored rubric, quorum aggregation, pairwise tournaments.
- Scripts that turn colour, ranking and critique into numbers.

## Core models

1. **Art is an interface.** The player reads it for information under time pressure on a small, bright, moving screen. Order of concern: readability, then consistency, then appeal, then polish. A beautiful screen that does not read is a failed screen.
2. **Readability stack.** Silhouette (shape) before value (light/dark) before colour (hue) before detail. If a unit fails in black-and-white at 64 px, no colour or detail fixes it. See `references/visual-fundamentals.md`.
3. **Style is a production decision.** Style sets cost per asset, animation method, AI-generation reliability, and runtime cost. Unique-asset count, especially animated characters, dominates cost. See `references/style-selection-and-bible.md`.
4. **The bible is the contract.** Every visual rule is checkable, numeric and has an example and a counter-example. Assets carry the bible version. Without a bible, AI generation drifts within a dozen assets.
5. **Measure, then judge.** Run objective checks (palette audit, size/alpha checks, silhouette fill) before any subjective critique. Give the numbers to the reviewers.
6. **Compare, do not score.** For choosing among candidates ask "which of these two fits better?" in both orders and rank with Bradley-Terry. Absolute 1-10 scores from models cluster and drift.
7. **Human taste checkpoints.** The human signs off on the style frame, on the bible v1.0 and on store-facing art. Everything between runs automatically.
8. **Gameplay-critical pairs.** Name the colour pairs that carry gameplay (tile vs board, enemy vs ground, ready vs not ready) and protect those with contrast and redundancy (shape, icon, pattern) so colour-blind players are never locked out.
9. **Reference resolution.** Author at one reference resolution; define every pixel number against it and a reference device.

## Decision procedures

### Choose a style (new game)

1. Write the brief: genre, audience, session length, device tier, counts of characters, environments, UI screens, monthly content.
2. Shortlist three styles from the catalogue (one safe, one bold) that fit the device tier.
3. Build one style frame per candidate: hero gameplay screen with HUD, one character, one enemy or obstacle, one pickup, one VFX.
4. Run the pre-lock tests: thumbnail, squint, silhouette, palette audit, sunlight, production, animation, store.
5. Score the five filters with project weights; record the arithmetic and the rejected options.
6. Human checkpoint on the style frame. Then write the bible and freeze v1.0.

### Write or update the style bible

1. Start from the template in `references/style-selection-and-bible.md`; fill the REQUIRED sections first (vision, style definition, colour, technical constraints, AI generation lock).
2. Convert every adjective into a number or a visible example.
3. Run `palette_audit.py` on the master palette with the gameplay-critical pairs, text pairs and UI pairs.
4. Generate the reference sheet (turnaround, expressions, materials, palette swatches) and the do/don't gallery.
5. Version it; classify later changes as patch, minor or major; a major change is a pivot with a re-art cost.

### Brief an asset batch

1. Check the bible has the asset class rules (size, silhouette anchor, palette subset, pivot, naming).
2. Write one brief per asset class: purpose, size and format, states and frames, palette subset, references, forbidden elements, acceptance checks.
3. Hand the brief to `ai-asset-pipeline` (generation) or to a human artist; require manifest entries with provenance.
4. Gate on objective checks, then a critique pass, then a human sample review.

### Run a critique

1. Capture real device-size screenshots plus crops of the focal area and any new asset.
2. Run objective checks (below) and attach the numbers.
3. Run three or more independent passes with the anchored rubric (vary model, crop or framing).
4. Aggregate with `critique_aggregate.py`; route unconfirmed blockers and split decisions to a human.
5. Convert confirmed flags to a fix list tied to bible rules, at most five must-fix items per round.

### Pick the best candidate from a batch

1. Pre-filter by objective checks (size, alpha, garbled text, anatomy, palette audit).
2. Schedule pairwise jobs with `tournament_rank.py schedule` (round-robin up to about 10 items, sampling beyond).
3. Collect both-order judgements, then `rank`; use `--min-margin` to demand a clear winner.
4. Send the top two or three to the human with the ranking. Record the choice in the manifest.

### Prepare store art

1. Look up the current store specs (volatile) and store verified numbers with the date in the project.
2. Build screenshots from templates: hook, core loop, progression, mode, proof; real gameplay with HUD.
3. Generate icon candidates (12-16), tournament them, hand-finish the winner, test small and on a busy wallpaper.
4. Check AI-disclosure and licence status for any generated marketing material before submission.

### Palette audit

```
python3 ${CLAUDE_PLUGIN_ROOT}/skills/art-direction/scripts/palette_audit.py \
  --colors "#1b1f3b,#f4d35e,#ee6c4d,#3d9970" --names ink,gold,coral,green \
  --critical ink:gold,coral:green --text gold:ink --json
```

A pair that looks different to a typical viewer but collapses under a simulated colour-vision deficiency is flagged; fix with a lightness difference or a redundant shape cue, then re-run.

## Mobile specifics

- Physical size matters more than pixel size: design for a 6-inch screen at arm's length; icons and critical sprites must read at 48-64 px.
- Thumbs and notches hide corners and the bottom edge; keep critical art and HUD in safe areas.
- Outdoors, brightness and glare compress contrast: require stronger value separation than a monitor review suggests.
- Memory and heat: big textures and many layers cost more than they show; atlases per screen, compressed formats, trimmed frames.
- First screenshots and the icon do most of the store work: treat them as products with their own tests.
- Fast sessions: HUD hierarchy must work in a glance; animate to guide, not to decorate.
- Cultural and age context: check colours, symbols and gestures in target markets, and the age rating of imagery.

## Anti-patterns

| Anti-pattern | How to detect | Fix |
|---|---|---|
| Style chosen from a mood board only | No numbers in the bible | Add style frames, tests and numeric rules |
| Detail over readability | Greyscale thumbnail loses units | Silhouette and value pass first |
| Colour-only coding | Palette audit fails under colour-vision simulation | Add shape, icon, pattern |
| Absolute scoring by a model | All scores 3-4, results flip between runs | Rubric anchors plus pairwise tournament |
| One-pass visual QA | Defects found by players, not the gate | Three or more independent passes with quorum |
| No bible version on assets | Cannot tell which assets are stale after a style change | Record version in the manifest |
| Marketing art with fake gameplay | Screenshot shows content not in the build | Real captures only; store policy risk |
| Mixed pixel grids or scales | Pixel art shows different pixel sizes | One base resolution; integer scaling; pixelate step |
| Authoring at low-tier size | Blurry on high-end devices | Author at the reference resolution and compress down |
| Style drift in live ops | New seasons look different from launch | Frozen invariants, scheduled drift review |

## Using the ontology

- The project contract (`.gamestudio/contract.json`) holds `art_direction` (style family, palette, reference resolution); `palette_audit.py --contract` reads the palette from it.
- Asset records and provenance go through the project manifest (see `ai-asset-pipeline`); critique outcomes become `approved_by` and `status` updates.
- Visual critique results are evidence for the visual gate of a feature (`evidence/<feature>/visual_review.md` via `critique_aggregate.py --md`).
- Content units in the ontology (characters, items, levels) each need an asset class in the bible; the content count drives style cost.
- Scripts in this skill: `scripts/palette_audit.py`, `scripts/tournament_rank.py`, `scripts/critique_aggregate.py` (all stdlib, each supports `--help` and `--selftest`; exit 0 ok, 1 check failed, 2 input error). Plugin scripts: `${CLAUDE_PLUGIN_ROOT}/scripts/image_post.py` for size, palette and atlas checks.

### Script usage

| Script | Command | Purpose |
|---|---|---|
| `scripts/palette_audit.py` | `palette_audit.py --colors ... --critical a:b --text fg:bg --ui fg:bg [--json]` or `--contract .gamestudio/contract.json` | Colour-difference, lightness and colour-blind checks on critical pairs; WCAG contrast on text and UI pairs |
| `scripts/tournament_rank.py` | `schedule --items a,b,c [--mode roundrobin\|sample]`; `next --votes v.json`; `rank --votes v.json [--min-margin 0.65] [--json]` | Pairwise judging jobs in both orders, Swiss follow-up rounds, Bradley-Terry ranking and position-bias rate |
| `scripts/critique_aggregate.py` | `--in reviews.json --tier slice [--md out.md] [--json]` | Median scores, quorum-confirmed flags, tier verdict, needs-human list |

## Reference library

| File | What it contains | When to read it |
|---|---|---|
| `references/visual-fundamentals.md` | Readability stack, shape language, silhouette, value, colour theory, accessible palettes, composition, physical size maths, 25-point pass, worked palette fix | Any time a screen or asset does not read; before designing a palette |
| `references/style-selection-and-bible.md` | Five style filters, mobile style catalogue with cost and AI-friendliness, genre fit, style tests, full style bible template and worked excerpt, change control | Starting a game, choosing between looks, writing or revising the bible |
| `references/asset-specs-and-marketing-art.md` | Resolution strategy, safe areas, atlases, naming, 9-slice, sprite sheets, icons, store screenshots, key art, preview video, volatile store specs | Briefing assets, building UI art, preparing a store listing |
| `references/art-critique-rubric.md` | Weighted rubric with anchors, severity, tier thresholds, critique protocol, tournament method, critic failure modes | Reviewing art, gating a feature visually, selecting among AI candidates |

## Related skills

- `ai-asset-pipeline`: generates and post-processes assets under the style lock, with provenance.
- `technical-art`: shaders, VFX, texture compression and rendering cost for the chosen style.
- `mobile-ux`: HUD, thumb zones, touch targets and onboarding that the art must serve.
- `game-feel`: motion, juice and feedback timing that art and VFX deliver.
- `accessibility-localization`: colour-vision, contrast and text-expansion requirements.
- `marketing-ua`: ad creative and store-conversion testing built on the key art.
- `mobile-performance`: memory and draw budgets the asset specs must respect.
- `genre-playbooks`: genre conventions that inform style fit.
