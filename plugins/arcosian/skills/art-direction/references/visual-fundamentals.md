# Visual Fundamentals for Mobile Games

Game art is not illustration: it is an interface the player reads under time pressure, on a 6-inch screen held 30–40 cm away, often outdoors, often with one eye on something else. This file is the studio's working reference for the fundamentals that decide whether a screen reads: the readability stack, shape language, silhouette, value structure, colour theory and accessible palettes, composition, hierarchy, the kinds of contrast, physical-size maths for phones, lighting, and edges and detail density. Every section ends in a rule you can check. The file closes with a 25-point fundamentals pass and a worked example in which `scripts/palette_audit.py` catches a colour-blindness failure in the sample project's palette and verifies the fix. Style choice lives in `style-selection-and-bible.md`; documenting the rules for a project lives in `style-selection-and-bible.md`; scoring finished screens lives in `art-critique-rubric.md`.

## Contents

1. [The readability stack](#1-the-readability-stack)
2. [Shape language](#2-shape-language)
3. [Silhouette](#3-silhouette)
4. [Value structure](#4-value-structure)
5. [Colour theory for games](#5-colour-theory-for-games)
6. [Accessible palettes](#6-accessible-palettes)
7. [Composition](#7-composition)
8. [Visual hierarchy: the layer stack](#8-visual-hierarchy-the-layer-stack)
9. [The kinds of contrast](#9-the-kinds-of-contrast)
10. [Readability at phone sizes](#10-readability-at-phone-sizes)
11. [Lighting and shading](#11-lighting-and-shading)
12. [Edges, outlines and detail density](#12-edges-outlines-and-detail-density)
13. [Motion as a visual fundamental](#13-motion-as-a-visual-fundamental)
14. [The 25-point fundamentals pass](#14-the-25-point-fundamentals-pass)
15. [Worked example: fixing the Pebble Keep palette](#15-worked-example-fixing-the-pebble-keep-palette)

---

## 1. The readability stack

A player looking at a game screen answers questions in a fixed order. Art that answers them in that order, fast, is readable. Art that makes the player hunt is not, however beautiful it is.

| Order | Question the eye answers | Typical answer on screen | Time budget |
|---|---|---|---|
| 1 | Where is the play space? | Board, lane, arena, path | < 0.25 s |
| 2 | Which one is me / mine? | Avatar, selected piece, own units | < 0.25 s |
| 3 | What is dangerous? | Enemies, hazards, timers running out | < 0.5 s |
| 4 | What can I touch or do? | Buttons, interactive pieces, drag targets | < 1 s |
| 5 | What is valuable? | Rewards, pickups, currency | < 1 s |
| 6 | What just changed? | Hits, merges, score, state changes | Immediately on change |
| 7 | Everything else | Decoration, background, story texture | Whenever |

**The contrast budget.** A screen has a fixed amount of attention-grabbing power: value contrast, saturation, warmth, edge sharpness, detail and motion. Spend it in stack order. Rows 2–4 get the strongest contrast; row 7 gets the least. When decoration is as loud as the gameplay layer, the player has to work out what matters, and in a 3-minute session they will not bother.

**Rule:** for any screen, list the top three things the player must see. Then check that those three hold the highest value contrast, the highest saturation and the only constant motion on screen. If anything decorative outranks them on any of those, demote it.

---

## 2. Shape language

Simple shapes carry emotional associations that players read before any detail. This is convention, not physics, but it is reliable enough across audiences to design with.

| Primary shape | Reads as | Use for | Watch out for |
|---|---|---|---|
| Circle / round | Friendly, safe, soft, cute, approachable | Heroes in casual games, collectibles, pets, healing, rewards, casual UI buttons | Too many rounds and everything blurs together; add one angular accent |
| Square / rectangle | Stable, sturdy, reliable, heavy, defensive | Tanks, guardians, structures, walls, containers, panels | Boxy and dull if nothing breaks the silhouette |
| Triangle / spike | Danger, speed, aggression, direction | Enemies, hazards, projectiles, arrows, villains, competitive UI | Triangles everywhere make a screen feel hostile and noisy |
| S-curve / flowing | Grace, movement, organic life, magic | Water, vines, spirits, VFX trails | Flowing shapes lose readability at small sizes |

**Combining shapes.** Characters read best with one dominant shape and one secondary accent. A round body with triangular ears is "cute but feisty"; a square body with round eyes is "sturdy but gentle". Pick the combination from the role, not from what looks nice in isolation.

**Big, medium, small.** Shapes read best when their masses vary clearly. Something like 60/30/10 of the silhouette area (one big mass, one medium, one small) is a useful starting proportion. Equal-sized masses ("twinning") look stiff. Shapes that just touch at an edge ("tangents") create visual confusion; overlap them clearly or separate them clearly.

**Exaggeration.** Push one or two features (head size, hands, weapon, eyes) and keep the rest simple. On a phone, a feature that is not exaggerated is usually not visible at all.

**Shape language in UI.** The same rules apply to interface art: rounded rectangles with large radii read casual and friendly; chamfered or sharp corners read competitive or tactical. Keep one corner language across the whole UI. Mixing radii is one of the fastest ways to make UI look unpolished.

**Rule:** write the shape language down as a table in the style bible: role → primary shape → secondary shape → one example. Every new character or enemy brief cites its row.

| Role (example from a merge tower-defence game) | Primary | Secondary | Note |
|---|---|---|---|
| Player units (golems) | Circle / rounded square | Small triangle accents on higher tiers | Higher tiers add angular crystals so "stronger" reads as "sharper" |
| Enemies (snails) | Spiral circle (shell) | Triangle (antennae, horns on elites) | Elites gain spikes; bosses gain size and a triangular silhouette |
| Hazards | Triangle | None | Hazards are the only purely angular objects on the board |
| Rewards | Circle / gem facets | Star | Rewards are the only objects that sparkle |

---

## 3. Silhouette

A silhouette is the object filled solid black. If players can identify an object from its silhouette at the size it appears in play, it will read in colour, in motion, in clutter and under colour-vision deficiency.

### 3.1 The silhouette test (procedure)

1. Render or export each asset at its **actual on-screen size** on the smallest supported phone, not at authoring resolution. A 512 px source that appears at 56 pt is judged at 56 pt.
2. Fill it solid black (or with the background's darkest value) and place it on the real background.
3. Show the set to a tester or a VLM critic, one at a time, for one second each. Ask them to name the object, or to match it to a labelled lineup.
4. Pass if they name or match at least 90% correctly. Investigate any pair that is confused more than once.

### 3.2 What makes silhouettes distinct

- **Proportion:** height-to-width ratio differs (tall and thin vs short and wide).
- **Top contour:** the head and shoulder line, hats, horns, ears and crests; the top of a silhouette is read first.
- **Protrusions:** weapons, tails, wings, tools, antennae that break the outline.
- **Negative space:** gaps between limbs and body. Limbs held inside the body outline disappear.
- **Base:** wide and planted vs narrow and floating.

For a roster, every unit should differ from every other unit in at least two of these five. Tiered upgrades of the same unit (tier 1–5) should differ mainly in size and protrusions, so the family stays recognisable while the tier reads.

### 3.3 Silhouette overlap metric

When the roster is large, measure instead of eyeballing. Normalise each silhouette mask to the same bounding-box height, centre the masks, and compute intersection over union:

```
IoU(A, B) = |A ∩ B| / |A ∪ B|        # on binary alpha masks, same canvas, centred
flag pairs with IoU > 0.85            # studio heuristic: likely confusable at small sizes
review pairs with 0.75 < IoU <= 0.85  # distinct only through colour or detail
```

A pair that is distinct only through colour fails under colour-vision deficiency and in motion blur. Fix it with shape first. The IoU thresholds are working heuristics, not research values; calibrate them against your own silhouette tests.

### 3.4 Pose and view

- **3/4 view** shows more of the form than straight front or side, and is the default for top-down and isometric mobile games.
- **Action poses** should extend the silhouette (arm out, weapon raised). An attack frame whose silhouette matches the idle frame reads as no attack.
- **Readable at the extremes:** in animation, the key poses (anticipation, contact, follow-through) carry the read. In-betweens can blur.

**Rule:** no asset is approved until its silhouette has passed the test at in-game size on the real background.

---

## 4. Value structure

Value (lightness) carries readability. Hue carries identity and mood. If a screen works in grayscale, colour can only help; if it fails in grayscale, no colour scheme will fix it.

### 4.1 Measuring value

Use CIELAB **L\*** (0 = black, 100 = white), not HSV "V". HSV value treats pure yellow `#FFFF00` and pure blue `#0000FF` as equally bright, yet their L\* values are about 97 and 32. `scripts/palette_audit.py` reports L\* and a value band (L\*/10, so 0–10) for every colour.

### 4.2 Value plans

| Plan | Description | Fits | Risk on phones |
|---|---|---|---|
| Two-value (notan) | Every object is light-on-dark or dark-on-light | Minimal puzzle, silhouette art, hyper-casual | Flat if over-applied to complex scenes |
| Three-value | Background mid, playfield one step away, gameplay objects at the extremes | Most casual and mid-core games; the default | Needs discipline when adding VFX |
| High key | Mostly light values, darks reserved for accents and outlines | Cozy, cute, puzzle, kids | Washes out in bright sunlight if darks are too few |
| Low key | Mostly dark values, lights reserved for focus | Horror, mystery, sci-fi, roguelites | Poor readability outdoors and at low brightness; needs strong lights on the gameplay layer |

### 4.3 Value rules for game screens

1. **Compress the background.** Keep backgrounds inside a narrow band of about 2–3 value bands (20–30 L\*). The gameplay layer then sits outside that band or is separated by an outline.
2. **Separate gameplay from ground.** Interactive objects should differ from what is behind them by at least about 20 L\*, or carry an outline or rim light that does. This is a studio heuristic: it keeps objects legible after screen glare, auto-brightness dimming and compression.
3. **Distribute values roughly 60/30/10.** About 60% of the screen in the dominant value, 30% in a second, and 10% for the accent (the extreme value goes to the focal point).
4. **Reserve the extremes.** Pure white and the darkest dark go to the most important elements: the player, the next target, the reward, the call to action.
5. **Squint and grayscale tests.** Squint at the screen, or blur it by about 1% of its width, or desaturate it. The top three items of the readability stack must still pop.

**Rule:** every screenshot that goes to the visual gate is also reviewed in grayscale. Anything that disappears in grayscale gets a value fix, an outline, or a non-colour cue.

---

## 5. Colour theory for games

### 5.1 Work in a perceptual model

Build palettes in a perceptual space: CIELAB / LCh (lightness, chroma, hue) or OKLCH. In these spaces equal steps look roughly equal, and you can change hue without silently changing lightness. HSV and HSL are convenient pickers but poor design spaces, because their "lightness" ignores how the eye weights green and red over blue.

### 5.2 Hue relationships (starting points, not laws)

| Scheme | Construction | Use |
|---|---|---|
| Analogous | 3–4 neighbouring hues | Calm environments, a biome's base palette |
| Complementary | Opposite hues | Player vs enemy, focal vs background (for example warm character on cool background) |
| Split complementary | One hue plus the two neighbours of its complement | A rich but controlled scene palette |
| Triadic | Three hues evenly spaced | Bright casual palettes; needs one dominant hue to avoid noise |
| Monochrome + accent | One hue family plus one contrasting accent | UI, minimalist puzzle games, focus screens |

### 5.3 Temperature

Warm colours (red, orange, yellow) appear to advance; cool colours (blue, cyan, violet) appear to recede. Use warm for the gameplay layer and focal points and cool for depth. Lighting follows the same logic: warm light with cool shadows, or cool light with warm shadows, gives form and atmosphere at no performance cost, because it is painted into the asset or the gradient map.

### 5.4 Saturation hierarchy

- **Backgrounds:** low chroma (muted). Saturated backgrounds compete with gameplay.
- **Playfield and environment:** medium chroma.
- **Interactive objects and characters:** high chroma.
- **Rewards, danger and calls to action:** the highest chroma on screen, used sparingly.

When everything is saturated nothing stands out. A useful check: rank every on-screen element by chroma (`palette_audit.py` reports C\*) and compare that ranking with the readability stack. They should match.

### 5.5 Semantic colour

Players arrive with colour expectations from other games and from everyday life. Use them, but never rely on them alone (see §6).

| Meaning | Conventional colour | Redundant cue to add |
|---|---|---|
| Danger, damage, enemy, stop | Red | Spikes, skull or exclamation icon, shake, warning sound |
| Health, success, go, nature | Green | Plus sign, check mark, upward motion |
| Reward, premium, legendary | Gold / yellow | Sparkle, glint animation, star shape, frame |
| Information, water, mana, calm | Blue / cyan | Droplet or "i" icon |
| Rare, magic, epic | Purple | Gem facets, particle aura |
| Disabled, locked, common | Grey / low chroma | Lock icon, reduced opacity |

**Rarity ladders** (for example grey → green → blue → purple → orange or gold) are a widespread convention. Green and orange, and blue and purple, are hard to tell apart under common colour-vision deficiencies, so always pair rarity colour with frame shape, gem count, pips or a label.

### 5.6 Palette size and ramps

- **Master palette:** for 2D games, roughly 16–32 colours covers most projects. Pixel art often uses fewer (8–32). Sub-palettes per biome or world are subsets plus 2–4 local accents.
- **Ramps:** each material gets a ramp of 3–7 steps from shadow to highlight. Space the steps roughly 10–15 L\* apart so every step is visible at phone size.
- **Hue shifting:** in stylised art, shadows shift hue toward cool (blue or violet) and highlights toward warm (yellow), with chroma peaking in the mid-tones. A ramp that only changes lightness looks muddy and "photocopied". A practical spec in LCh: per step toward highlight, +10 to +15 L\*, hue rotated 5–15° toward yellow (about 60–90° hue angle); per step toward shadow, −10 to −15 L\*, hue rotated 5–15° toward blue-violet (about 270–300°); chroma highest at the base tone.
- **60-30-10 colour ratio:** dominant colour about 60% of the screen, secondary about 30%, accent about 10%. The accent is usually the focal or interactive colour.

### 5.7 Display realities

- **Wide gamut.** Many current phones have Display P3 or wider panels. Author and export in sRGB unless the pipeline is colour-managed end to end. sRGB assets display correctly on P3 screens, while P3-only saturation is clipped on sRGB screens and in many store and ad surfaces.
- **OLED.** Pure black pixels are switched off on OLED panels, which gives deep contrast. Large pure-black areas next to bright elements can show smearing when scrolling on some panels; a very dark grey (L\* 5–10) is safer for scrolling backgrounds.
- **Sunlight and brightness.** Phones are often played outdoors and at reduced brightness. Mid-value, low-contrast palettes that look elegant on a calibrated monitor collapse in sunlight. Check screens at 30–50% brightness on a real device.
- **Night modes and colour filters.** Blue-light filters shift the whole screen warm. Gameplay distinctions that rely only on blue vs yellow can weaken; value separation survives.

**Rule:** the palette is specified in hex with role, L\*, and the ramps it belongs to; it is audited with `palette_audit.py` before any production asset is generated.
