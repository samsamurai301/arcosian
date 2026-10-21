# Style Selection and the Style Bible

This file covers the two decisions that fix a mobile game's look for its whole life: which art style to commit to, and how to write that commitment down so humans, agents and AI generators can all reproduce it. Style choice is a production decision as much as an aesthetic one: it sets asset cost, animation method, how well AI generation works, how the game reads on a 6-inch screen and how it looks in a store thumbnail. The second half is a complete, fill-in style bible template; the style bible is the single source of truth that `studio-gateway` prompts, critique rubrics and asset briefs all point to.

## Contents

1. [Selecting a style: the five filters](#1-selecting-a-style-the-five-filters)
2. [Style catalogue for mobile](#2-style-catalogue-for-mobile)
3. [Genre fit table](#3-genre-fit-table)
4. [Style decision procedure](#4-style-decision-procedure)
5. [Style tests before lock](#5-style-tests-before-lock)
6. [The style bible: purpose and rules](#6-the-style-bible-purpose-and-rules)
7. [Style bible template](#7-style-bible-template)
8. [Style bible worked example (excerpt)](#8-style-bible-worked-example-excerpt)
9. [Change control](#9-change-control)

---

## 1. Selecting a style: the five filters

Apply the filters in order. A style that fails an early filter is not rescued by a later one.

| # | Filter | Question | Fail signal |
|---|---|---|---|
| 1 | Readability | Can the player parse every gameplay-critical element at phone size in 200 ms? | Critical objects share value and hue with the background; detail below ~2 mm physical size |
| 2 | Production capacity | Can the team, including AI tooling, produce the full content count at consistent quality? | Count of unique assets x cost per asset exceeds the budget even at 50% rework |
| 3 | Technical fit | Does it run on the lowest target device tier with the memory and draw budget? | Needs real-time lighting, large textures or heavy post on a low-tier phone |
| 4 | Market differentiation | Does it read as distinct in a store thumbnail row of ten competitors? | It looks like the genre default in greyscale at 64 px |
| 5 | Longevity | Can live content (events, seasons, skins) be added without a style drift? | Style depends on one artist's hand or one model version |

Rule: score each candidate 1-5 on each filter, multiply by a weight that reflects the project (a hyper-casual game weights readability and production at 2x; a collectible RPG weights differentiation and longevity at 2x). Show the arithmetic in the decision record.

## 2. Style catalogue for mobile

Cost bands are relative production effort for the same content count, not prices. "AI-friendliness" describes how reliably current image and 3D generators can hold the style across hundreds of assets with a style lock (see `skills/ai-asset-pipeline/references/style-lock-and-prompts.md`).

| Style | Relative cost | AI-friendliness | Runtime cost | Strengths | Risks |
|---|---|---|---|---|---|
| Flat vector / geometric minimal | Low | High for shapes; medium for exact geometry | Very low (vector or small atlases) | Maximum readability, tiny downloads, easy palette control | Generic look, differentiation needs strong colour and motion |
| Cartoon 2D (clean outline, flat or two-tone fill) | Medium | High | Low | Broad appeal, forgiving, easy UI cohesion | Crowded genre, consistency across poses is the work |
| Painterly 2D (soft shading, visible brushwork) | High | Medium-high for stills, low for animation | Medium (large textures) | Premium feel, strong key art | Animation cost, edge cleanup, inconsistent lighting across assets |
| Pixel art (low-res, limited palette) | Medium | Medium; needs native-resolution tools, general models drift on pixel grid | Very low | Strong nostalgia niche, small files, clear grid | Pixel inconsistency (mixed grids), integer scaling on odd screens |
| Hand-drawn / sketch | Medium-high | Medium | Low | Distinct personality | Line weight consistency, text/UI clash |
| Paper cut-out / collage | Medium | Medium | Low | Cheap skeletal animation (parts rotate) | Needs disciplined part layering |
| Low-poly 3D (flat-shaded facets) | Low-medium | High for props, medium for characters | Low | Fast to build, cheap runtime, AI 3D tools output low face counts | Easy to look like asset-store filler |
| Stylized 3D, baked or toon-lit | Medium | Medium; textures consistent, topology and rigs need cleanup | Low-medium | Premium look on cheap hardware, strong silhouettes | Needs a shader pass and baked lighting discipline |
| Voxel | Medium | Medium-low | Medium (many cubes, needs instancing or meshing) | Moddable look, built-in cohesion | Fine detail impossible, heavy meshing cost |
| Isometric 2.5D (pre-rendered or sprites) | High | Medium; perspective consistency is a known weak point | Low | Rich scenes on cheap hardware | Camera angle must be locked; every asset must match it |
| 2D skeletal (Spine or similar, layered parts) | Medium-high | Low-medium; rigs are semi-manual | Low | Smooth animation, small memory | Part separation discipline; limited AI help for rigging |
| Realistic or PBR 3D | Very high | Low for consistency, medium for stills | High | Only if the genre demands it | Heat, size, thermals; rarely right for mobile indie |
| Mixed (2D UI + 3D world, or 3D with 2D VFX) | Medium | Depends | Medium | Standard for many hit games | Two pipelines must share one palette and lighting logic |

Cost heuristics: unique-asset count dominates. A style with a cheap per-asset cost but high count (match-3 with hundreds of tiles skins) can cost more than an expensive style with few assets (a single-screen puzzle). Cost per animated character is typically an order of magnitude above a static prop, so characters decide the style more than environments do.

## 3. Genre fit table

Fit is a starting guide, not a rule; the best-known exceptions to a genre norm are usually the most memorable games. Use "differentiation move" as the question to ask when the default is crowded.

| Genre | Common fits | Why | Differentiation move |
|---|---|---|---|
| Hyper-casual | Flat vector, low-poly | Instant readability, tiny size, fast iteration | Signature colour world, satisfying material (glossy, clay, paper) |
| Match-3 / puzzle | Cartoon 2D, glossy 3D-rendered sprites | Distinct piece shapes and colours, juicy VFX | Unusual silhouette set, strong theme world |
| Idle / incremental | Cartoon 2D, flat vector | Dense UI, many currencies, long sessions | Character personality and visual progression of the base |
| Merge | Cartoon 2D with strong item ladders | Item tiers must read at a glance | Tier language: each tier changes silhouette, not only detail |
| Action RPG / collector | Stylized 3D, painterly 2D portraits | Character appeal drives collection and monetization | Hero art direction and skin system |
| Strategy / base builder | Stylized 3D, isometric | Readable units at distance, many buildings | Faction shape language |
| Racing / runner | Low-poly, stylized 3D | Speed readability, low overhead | Lighting and colour grading per biome |
| Roguelike / deckbuilder | Pixel, hand-drawn, painterly cards | Rapid content volume, strong card art | A coherent iconography for keywords and rarity |
| Simulation / cozy | Soft cartoon, painterly, low-poly warm | Comfort tone, long session | Texture and ambient animation |
| Hidden object / adventure | Painterly 2D, pre-rendered | Detail rewards looking | Scene composition and clear item contrast |
| Word / trivia / card | Flat vector, typographic | Text is the product | Type design as the art |
| Shooter (casual) | Stylized 3D, low-poly | Threat and cover readability | Team colour logic and VFX clarity |

## 4. Style decision procedure

1. Write the one-page brief: audience, session length, platform tier, genre, count of unique characters, environments and UI screens, and the monthly live-content count.
2. Pick three candidate styles from section 2 that pass filter 3 (technical fit) on paper. Include one "safe" and one "bold" candidate.
3. For each candidate, produce a **style frame**: one hero gameplay screen at real phone resolution with the HUD, one character, one enemy or obstacle, one pickup, one VFX. Use AI generation freely at this stage (see `skills/ai-asset-pipeline`), but one human art-direction pass is required to make the three frames comparable in effort.
4. Run the tests in section 5 on each frame.
5. Score with the five filters and weights. Record scores and the rejected options in `.gamestudio/` decision notes.
6. Human checkpoint: the user signs off on the style frame (this is a taste checkpoint; never skip it).
7. Write the style bible (section 7), generate the reference sheet (character turnaround, palette, material swatches), and freeze it as version 1.0.
8. Only after sign-off: batch production. The first batch is a **vertical slice of assets**, not a breadth pass.

## 5. Style tests before lock

| Test | How | Pass threshold (studio heuristic) |
|---|---|---|
| Thumbnail test | Shrink the key frame to ~64 px and to ~180 x 320, in colour and greyscale | The game's genre, hero and core action are identifiable |
| Squint test | Blur heavily or view at arm's length | Value structure shows foreground, midground and background layers |
| Silhouette test | Fill each character and enemy with solid black | Every unit is distinguishable (see `references/visual-fundamentals.md`) |
| Palette audit | `python3 ${CLAUDE_PLUGIN_ROOT}/skills/art-direction/scripts/palette_audit.py --colors ... --critical ...` | Gameplay-critical pairs pass colour-blind simulation |
| Sunlight test | Reduce device brightness to low and view under bright light or simulate with a contrast reduction | Gameplay-critical contrast survives |
| Production test | Time the production of two additional assets in the style from a prompt and the bible alone | Both are on-style without handholding; the time is within budget |
| Animation test | Animate one idle and one action in the style | Frame count, rig complexity and file size fit the budget |
| Store test | Place the key art next to ten competitors' icons | It is not the same silhouette and palette as the genre default |

## 6. The style bible: purpose and rules

The style bible is operational, not inspirational. It exists so that a new contributor, an AI generator and a critic can each decide whether an asset is on-style without asking the art director.

Rules:
- Every rule must be checkable. "Warm and friendly" is not a rule; "outline 3 px at 1080 px height, colour is the object's darkest shade at 70% saturation, no pure black" is.
- Every rule has an example and a counter-example (an image path in `assets/_bible/`, or a prompt-produced sample).
- Numbers are in physical or normalized units (px at the reference resolution, percent of screen height) so they survive device scaling.
- The bible declares the **reference resolution** and the **reference device**; all pixel numbers hang off them.
- The bible holds the locked prompt block for AI generation (positive, negative, seeds, reference set); see `skills/ai-asset-pipeline/references/style-lock-and-prompts.md`.
- Version it. Assets record which bible version they were made under.
- It is short enough to be read: target 4-8 pages plus the sample sheet.

## 7. Style bible template

Copy this block into `.gamestudio/art/style-bible.md` (or `templates/docs/style-bible.md` if the project template is used) and fill every field. Fields marked REQUIRED gate asset production.

```markdown
# <Game> Style Bible v<major.minor>   (status: draft | locked)

## 0. Meta
- Owner: art-director   Approved by: <human>   Date: <YYYY-MM-DD>
- Reference resolution: <e.g. 1080 x 1920 portrait>   Reference device: <model/tier>
- Target tiers: low / mid / high; min supported device: <...>
- Orientation and safe areas: <notch, home indicator, thumb zones>

## 1. Vision (REQUIRED)
- One-sentence look: <e.g. "tactile clay diorama lit by a warm late sun">
- Three adjectives, and three anti-adjectives (what it must never feel like)
- Emotional target per context: menu / play / reward / failure
- Three reference images with what we take from each and what we reject
- Competitor differentiation statement

## 2. Style definition (REQUIRED)
- Style family (section 2 of the style guide) and dimensionality
- Shape language: primary shapes per category (heroes, enemies, props, terrain, UI)
- Proportions: head-to-body ratio, hand/foot exaggeration, eye size rule
- Line: outline presence, weight at reference res, colour rule, taper rule
- Shading: flat | cel (n bands) | gradient | painted; light direction; shadow colour rule
- Detail density: max detail frequency (px) per asset class; where detail is allowed
- Texture: surface language (paper grain, brushwork, none); tiling rules
- Materials palette: matte, glossy, metal, glass, liquid, with a swatch each

## 3. Colour (REQUIRED)
- Master palette: <name: #RRGGBB, role> (target 12-24 named colours for most mobile games)
- Ramps: base-shadow-highlight per hue, with hue shift rule (shadows shift toward <hue>)
- Semantic colours: success, danger, rare, premium, interactive, locked, team A/B
- Gameplay-critical pairs (for `palette_audit.py`): <a:b ...>
- Text pairs and UI pairs with minimum contrast targets
- Colour-blind policy: shape/icon/pattern redundancy for any colour-coded mechanic
- World palettes: per biome, per time of day, per event (each a derived subset)

## 4. Characters
- Roster structure: tiers, silhouettes, rarity cues (frame, aura, accessory, not detail only)
- Turnaround and expression sheet paths; pose language (idle, action, victory, fail)
- Costume/skin rules: what may change, what is invariant (silhouette anchor, eye style)
- Animation style: frame count or rig, timing (e.g. on twos), squash/stretch limits

## 5. Environment and props
- Camera: angle, FOV or projection, fixed or free; horizon/tilt
- Layer plan: foreground / playfield / background, value and saturation per layer
- Prop scale chart relative to the player unit; tile size and grid
- Lighting rules: baked or dynamic; ambient colour; shadow style

## 6. UI and typography
- Type: display and body faces, licences, sizes at reference res, min size (see mobile-ux)
- Button states: normal, pressed, disabled, focus; 9-slice sources and corner radii
- Icon system: grid, stroke, corner radius, filled vs outlined, padding
- Panels, frames, rarity borders, currency icons, badges
- Safe areas and thumb zones; min touch target in dp or points

## 7. VFX and motion
- VFX language: shape, colour roles, duration ranges, easing curves
- Hit, reward, level-up, error, ambient: one reference per category
- Particle budget classes (see technical-art skill) and overdraw rules
- Screen transitions and UI motion timings

## 8. Technical constraints (REQUIRED)
- Texture formats and max sizes per tier; atlas size and padding
- Poly budgets, bone counts, LOD rules (3D)
- File naming, folders, pivot and origin conventions
- Memory budget per screen; draw-call budget

## 9. AI generation lock (REQUIRED if AI is used)
- Locked style prompt block (positive), negative block
- Reference set paths, seed policy, model and version used for the lock
- Allowed models/providers; excluded ones; licence notes
- Prompt templates per asset type (or a link to the pipeline file)
- Required human edit step before an asset becomes `approved`

## 10. Do / Don't gallery
- 6-10 on-style and off-style pairs with a one-line reason each

## 11. Review and change log
- Critique rubric weights for this project; pass thresholds per milestone tier
- Version history: <version, date, change, assets affected>
```

## 8. Style bible worked example (excerpt)

Project: a one-thumb merge game with a cozy workshop theme, portrait 1080 x 1920, mid-tier phones.

```markdown
## 2. Style definition (excerpt)
- Style family: soft cartoon 2D with painted two-tone shading.
- Shape language: items are rounded rectangles and circles (corner radius >= 12% of item width);
  tools and hazards use triangles. Silhouette must distinguish tiers 1-5 at 96 px.
- Line: 4 px at 1080 px height, colour = darkest ramp colour of the object, no pure black.
- Shading: two bands (base, shadow), plus one specular dot on glossy objects. Light from top-left.
- Detail density: no feature smaller than 6 px at reference res on items; backgrounds may have 3 px texture.
## 3. Colour (excerpt)
- Master palette: 18 named colours. Shadows shift 10-15 degrees toward blue-violet; highlights toward yellow.
- Gameplay-critical pairs: item vs board cell, item vs next-tier ghost, merge-ready glow vs board.
- Redundancy: tier is shown by silhouette and a pip count, never by colour alone.
```

Why this works: each line is something a critic or `palette_audit.py` can verify, and each ties to a gameplay purpose (tier readability).

## 9. Change control

- Patch (typo, clarified rule): update in place, note in the log.
- Minor (new palette ramp, new asset class rules): art-director approves; regenerate affected examples; no re-art of existing assets.
- Major (style family, outline rule, camera angle, palette hue shift): treat as a pivot. Costs the re-art of everything made so far; require a human checkpoint and a re-estimate.
- Assets store the bible version in the manifest; a critique after a major bump flags assets still on the old version for rework or sunset.
- Live games: new seasons may add world palettes and costume motifs, but the invariants in sections 2-4 stay frozen. Drift is the main long-term risk, so schedule a drift review every few content drops: compare a random sample of new assets to launch assets side by side.
