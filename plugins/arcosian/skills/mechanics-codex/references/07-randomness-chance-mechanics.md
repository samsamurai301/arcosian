# Randomness and Chance Mechanics

Randomness creates variety, tension, surprise and replayability. Badly handled, it also creates frustration, distrust and, when money touches it, legal exposure. This file catalogues 21 chance mechanics in the shared mechanic-card format: physical-feeling randomness (dice, cards, wheels), distribution-shaping tools (shuffle bags, weighted RNG, loot tables, pseudo-random distribution), paid-randomness systems (gacha banners, rate-up, pity, spark, mystery boxes, slots) and the design theory that decides how much randomness to use and where (input vs output randomness, perceived fairness). Each entry gives exact rules and probabilities, tuning ranges, dynamics, failure modes, mobile verdict, the monetization hook with its ethical limit, and an implementation sketch. The last sections cover RNG engineering (seeding, streams, determinism, testing) and the current odds-disclosure and loot-box rules. Simulate any paid-random design with `${CLAUDE_PLUGIN_ROOT}/scripts/gacha_calc.py` before it reaches a contract.

**Entry format.** Every entry maps onto `${CLAUDE_PLUGIN_ROOT}/scripts/schemas/mechanic-card.schema.json`. Ids are kebab-case; ids from sibling files carry their file number, e.g. `collections-albums` (05). Aesthetic targets use the eight MDA aesthetics (Hunicke, LeBlanc and Zubek, 2004). The **Paid?** column flags mechanics that, when sold for money, trigger odds-disclosure rules and loot-box regulation.

**Sibling overlaps.** Chest economics (sources, pacing, slot timers) are in `chests` (04); this file covers their probability design, disclosure and regulation.

## Contents

| # | Id | Mechanic | Primary job | Paid? |
|---|---|---|---|---|
| 07.01 | `dice` | Dice | Visible, tactile chance; risk evaluation | sometimes |
| 07.02 | `card-draw` | Card draw | Hidden-order randomness with planning | — |
| 07.03 | `deck-building` | Deck-building (in-run) | Shape your own odds over a run | — |
| 07.04 | `shuffle-bag` | Shuffle bags | Bound droughts and floods | — |
| 07.05 | `weighted-rng` | Weighted RNG | Exact designer-controlled frequencies | — |
| 07.06 | `loot-tables` | Loot tables | Structured, nested drop logic | sometimes |
| 07.07 | `pity-timers` | Pity timers | Bound bad luck with guarantees | yes |
| 07.08 | `gacha-banners` | Gacha banners | Time-boxed pull pools around featured content | yes |
| 07.09 | `rate-up` | Rate-up and featured guarantees | Target a specific featured item | yes |
| 07.10 | `spark` | Spark (exchange ceiling) | Deterministic cap on the cost of a target | yes |
| 07.11 | `mystery-boxes` | Mystery boxes / loot boxes | Bundled random rewards | yes |
| 07.12 | `slot-spin` | Slot / spin mechanics | Fast outcome loop on an energy budget | sometimes |
| 07.13 | `prize-wheel` | Prize wheels | Daily or ad-gated chance moments | sometimes |
| 07.14 | `run-generation` | Roguelike run generation | Seeded variety per run | — |
| 07.15 | `crits` | Critical hits | Damage spikes and build identity | — |
| 07.16 | `procedural-affixes` | Procedural affixes | Item variety and the "god roll" chase | sometimes |
| 07.17 | `prd` | Pseudo-random distribution | Same average, fewer streaks | — |
| 07.18 | `input-output-randomness` | Input vs output randomness | Decide where chance sits relative to decisions | — |
| 07.19 | `perceived-fairness` | Perceived fairness | Make randomness feel fair to human brains | — |
| 07.20 | `duplicate-protection` | Duplicate protection and crafting | Deterministic floor under random collections | yes |
| 07.21 | `assisted-refill` | Assisted refill (board RNG) | Tune puzzle difficulty through spawn odds | — |

## Choosing where randomness goes

| Goal | Use | Avoid |
|---|---|---|
| Replayability with skill expression | input randomness: `run-generation`, `card-draw`, `deck-building` | heavy output randomness on decisive actions |
| Excitement spikes in casual play | cascades (`assisted-refill`), `crits`, `prize-wheel` | randomness that can erase a whole session's progress |
| Fair-feeling percentages | `prd`, `shuffle-bag`, `perceived-fairness` techniques | raw independent rolls on visible small percentages |
| Collection monetization | earned random + `duplicate-protection` + `pity-timers` + `spark` | paid random with no ceiling, no odds page, no deterministic path |
| Competitive PvP | low-variance outcomes, server-side rolls, shared seeds where symmetrical | crits or misses deciding matches |

---

### 07.01 Dice — `dice`

- **Category:** randomness · visible output randomness
- **Player fantasy:** "Come on, six!" — chance you can see and feel.
- **Core rules:**
  - *State:* dice pool `k × d(s)`, faces, modifiers, rerolls left.
  - *Triggers:* roll action; reroll; modify (set face, +1, lock die).
  - *Effects:* result maps to movement, damage, resource or slot allocation. 1d6 is uniform (16.7 % per face); 2d6 is triangular (7 = 16.7 %, 2 or 12 = 2.8 %); more dice converge toward a bell curve.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Dice count | 1 (swingy) to 3+ (predictable) | More dice reduce variance relative to the mean |
| Rerolls / locks | 0–2 rerolls; lock individual dice | Converts output randomness into decisions (Yahtzee pattern) |
| Allocation | dice as resources placed into slots | Turns rolls into puzzles (input randomness) |
| Roll multiplier | spend ×N rolls for ×N result | Amplifies variance and spending; treat as betting-like |

- **Dynamics:** odds estimation; hope and dread; allocation puzzles when dice are resources.
- **Aesthetic targets (MDA):** Sensation, Challenge, Submission.
- **Feedback and juice:** physical tumble settling in 0.6–1.2 s; last die slows for tension; result face pops with a number flash.
- **Failure modes and exploits:** physics deciding outcomes nondeterministically (pre-decide, then animate to the face); multiplier dice escalating spend; perceived rigging after streaks.
- **Mobile fit:** excellent — tap or flick to roll, one-hand.
- **Monetization hooks and the ethical limit:** selling rolls (energy) and multipliers. Cap multipliers, avoid casino framing for young audiences, and keep roll purchases from looking like wagers.
- **Implementation notes:** roll with the seeded gameplay stream first, then play a canned or solved animation that lands on the chosen face; never read the result from physics.
- **Reference games:** Monopoly GO, Dicey Dungeons, Yahtzee with Buddies, backgammon.
- **Combines well with:** `slot-spin`, `energy-stamina` (08), `perceived-fairness`.

### 07.02 Card draw — `card-draw`

- **Category:** randomness · hidden-order input randomness
- **Player fantasy:** "I built this deck; now I play the hand I'm dealt."
- **Core rules:**
  - *State:* draw pile (ordered, hidden), hand (limit), discard, deck list.
  - *Triggers:* game start (shuffle, opening hand, mulligan), turn start (draw), card effects (draw, discard, tutor).
  - *Effects:* hypergeometric odds: P(≥1 of k copies in h cards from n) = 1 − C(n−k, h) / C(n, h). A 30-card deck with 2 copies: 25 % in a 4-card opener, 56 % by 10 cards seen. A 12-card deck where about 9 cards are seen per game (Marvel Snap) shows each card ~75 % of the time.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Deck size | 12–60 | Smaller = more consistent, more repetitive |
| Copy limit | 1–4 per card | Higher limits increase consistency |
| Draw per turn / hand limit | 1 per turn; hand 7–10 | Faster draw shortens games and raises combo potential |
| Mulligan rule | replace any, or redraw minus one | Reduces non-games from bad openers |

- **Dynamics:** planning around probabilities; consistency vs power trade-offs; topdeck drama.
- **Aesthetic targets (MDA):** Challenge, Expression, Sensation.
- **Feedback and juice:** card slides from deck with a flip; rare cards glint; "last card" tension on near-empty decks.
- **Failure modes and exploits:** resource screw/flood (separate resource from cards or smooth it); draw engines producing long non-interactive turns; client knowing deck order in PvP (keep hidden state server-side).
- **Mobile fit:** good with 3–7 cards in hand; tap-to-select + tap-to-play beats precise drags.
- **Monetization hooks and the ethical limit:** card packs (see `mystery-boxes`). Provide crafting so any deck is buildable deterministically.
- **Implementation notes:** Fisher–Yates with a seeded RNG; the server holds the order in PvP and reveals only drawn cards.

```text
shuffle(a, rng): for i in len(a)-1 down to 1: j = rng.int(0, i); swap(a[i], a[j])   # unbiased
draw(p): if p.pile empty: p.pile = shuffle(p.discard); p.discard = []; return p.pile.pop()
```
- **Reference games:** Hearthstone, Marvel Snap, Magic: The Gathering Arena.
- **Combines well with:** `deck-building`, `duplicate-protection`, `matchmaking-rating` (06).

### 07.03 Deck-building (in-run) — `deck-building`

- **Category:** randomness · player-shaped probability
- **Player fantasy:** "I turn a weak starter deck into an engine that breaks the game."
- **Core rules:**
  - *State:* run deck (starts small and weak), card pool by class and rarity, gold, removal opportunities.
  - *Triggers:* after encounters, choose 1 of 3 offered cards or skip; shops and events remove or upgrade cards.
  - *Effects:* deck composition changes draw odds. Thinning raises density: a key card in a 10-card deck appears in a 5-card hand 50 % of turns; in 20 cards, 25 %.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Starter deck | 10–12 weak cards (Slay the Spire's Ironclad: 10) | Defines the "make it better" arc |
| Offer size / skip | 3 offers, skip allowed | Skip teaches that less can be more |
| Removal access | every 2–4 floors, at a rising cost | Strong lever on consistency |
| Offer weighting | rarity × archetype synergy | Pure random offers feel incoherent |

- **Dynamics:** archetype pivots; thinning vs adding power; emergent combos; community "broken build" discovery.
- **Aesthetic targets (MDA):** Challenge, Discovery, Expression.
- **Feedback and juice:** offer cards fan in with rarity frames; deck-view counts; combo turns get escalating SFX.
- **Failure modes and exploits:** runs decided by early luck (guarantee useful early offers); dominant archetypes; infinite combos breaking the game (cap or celebrate deliberately).
- **Mobile fit:** excellent — turn-based, interruptible; proven on phones (Slay the Spire, Balatro).
- **Monetization hooks and the ethical limit:** usually premium; in F2P unlock card pools through meta progression. Never sell in-run cards.
- **Implementation notes:** synergy-weighted offers drawn from a dedicated `rng_offers` stream so seeds stay reproducible.

```text
offer(run): pool = class_cards - run.excluded
  w(c) = RARITY_W[c.rarity] * (1 + SYN * overlap(c.tags, run.deck_tags))
  return weighted_sample_without_replacement(pool, w, 3, run.rng_offers)
```
- **Reference games:** Slay the Spire, Balatro, Monster Train, Dominion (the tabletop origin of the genre, 2008).
- **Combines well with:** `card-draw`, `run-generation`, `prestige` (05).

### 07.04 Shuffle bags — `shuffle-bag`

- **Category:** randomness · sampling without replacement
- **Player fantasy:** none directly — the player simply never suffers an absurd drought.
- **Core rules:**
  - *State:* bag template (outcome → count); current bag contents.
  - *Triggers:* draw request.
  - *Effects:* draw a random item without replacement; refill and reshuffle when empty. Tetris's 7-bag deals each piece once per 7, so the longest possible gap between two I-pieces is 12 pieces.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Bag size | 1–2× the number of distinct outcomes, up to ~50 | Small = predictable; large ≈ independent random |
| Composition | counts proportional to target frequencies | Exact long-run frequencies |
| Early refill | refill when k items remain | Hides the pattern from counters |
| Bag scope | per player (not shared) | Shared bags let one player drain good outcomes |

- **Dynamics:** players can learn and plan (counting); fewer complaints about streaks.
- **Aesthetic targets (MDA):** Challenge (plannable), Submission (no frustration).
- **Feedback and juice:** "next" preview of 1–5 upcoming items turns the bag into a planning tool.
- **Failure modes and exploits:** too predictable in competitive play (counting); a bag shared across players; refills not persisted (save bag state).
- **Mobile fit:** invisible, zero cost.
- **Monetization hooks and the ethical limit:** a bag on reward drops is a simple, honest form of bad-luck protection.
- **Implementation notes:** persist the bag in the save so quitting cannot reroll it.

```text
draw(bag, rng): if empty(bag.items): bag.items = shuffle(copy(bag.template), rng)
  return bag.items.pop()
```
- **Reference games:** Tetris (modern guideline games such as Tetris 99), Puyo Puyo Tetris.
- **Combines well with:** `loot-tables`, `prd`, `assisted-refill`.

### 07.05 Weighted RNG — `weighted-rng`

- **Category:** randomness · core sampling primitive
- **Player fantasy:** none directly — it is the tool that makes every rarity mean what it says.
- **Core rules:**
  - *State:* items with non-negative weights `w_i`; `P(i) = w_i / Σw`.
  - *Triggers:* any weighted pick.
  - *Effects:* linear scan O(n); cumulative array + binary search O(log n); Vose's alias method O(1) per pick after O(n) setup.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Weight scale | integers (e.g. basis points, sum 10,000) | Integers avoid float drift and make odds pages exact |
| Dynamic weights | decay a weight after it hits, restore over time | Softens repeats without a bag |
| Exclusions | filter by context before sampling | Avoid impossible or irrelevant outcomes |
| Generator | PCG32 / xoshiro-family, 64-bit state | Poor generators (small LCGs) show patterns |

- **Dynamics:** precise designer control; the backbone of every table in this file.
- **Aesthetic targets (MDA):** supports Discovery and Sensation by controlling surprise frequency.
- **Feedback and juice:** n/a (pair with the presentation layer of the mechanic using it).
- **Failure modes and exploits:** modulo bias (`rng() % n`; use rejection sampling); disclosed odds drifting from live weights after a config change; float sums that never reach 1.0.
- **Mobile fit:** negligible CPU cost.
- **Monetization hooks and the ethical limit:** weights for paid outcomes must be the single source of truth for the published odds page.
- **Implementation notes:** generate the odds page from the same config the server samples from; unit-test with a chi-square goodness-of-fit over ≥ 100k samples.

```text
pick(weights, rng): r = rng.int(0, sum(weights) - 1)             # integer weights, unbiased int
  for i, w in enumerate(weights): if r < w: return i; r -= w
alias_build(w): Vose's algorithm -> (prob[], alias[]);  alias_pick: i = rng.int(0,n-1); return i if rng.float() < prob[i] else alias[i]
```
- **Reference games:** the Diablo series (item drops), Pokémon (wild encounter tables).
- **Combines well with:** `loot-tables`, `gacha-banners`, `procedural-affixes`.

### 07.06 Loot tables — `loot-tables`

- **Category:** randomness · structured drop logic
- **Player fantasy:** "This boss might drop the thing I'm farming for."
- **Core rules:**
  - *State:* table `{rolls, guaranteed[], entries[{item | subtable | none, weight, qty_min, qty_max, conditions}]}`.
  - *Triggers:* kill, chest, level clear, quest reward.
  - *Effects:* guaranteed items, then `rolls` weighted picks among entries passing conditions; subtables recurse (rarity table → item-within-rarity table).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Rolls per source | 1–5 | More rolls feel generous; inflate the economy |
| "Nothing" weight | 0–80 % | High empty weight makes drops events |
| Rarity split | e.g. 70 / 25 / 4.5 / 0.5 % | 0.5 % legendary = one per 200 drops; 3 rolls per boss ≈ 67 bosses |
| Conditions | level range, first clear, quest state | Prevents useless drops; first-clear guarantees reward exploration |

- **Dynamics:** farming routes; target farming; community drop-rate research.
- **Aesthetic targets (MDA):** Discovery, Sensation.
- **Feedback and juice:** drop fountain with rarity colour beams; distinct rare-drop SFX; loot summary at session end.
- **Failure modes and exploits:** stacked multiplicative find bonuses producing absurd rates; untested condition branches that drop nothing; save-scumming chest rolls (roll at spawn time, not open time, and persist).
- **Mobile fit:** good — auto-collect and summary screens.
- **Monetization hooks and the ethical limit:** paid chests use tables, so they need odds disclosure (expand nested tables into effective per-item odds).
- **Implementation notes:** data-driven JSON; validate (weights > 0, references resolve, no cycles); Monte Carlo verification of expected per-item rates in CI.

```text
roll(t, ctx, rng): out = list(t.guaranteed)
  repeat t.rolls: e = weighted_pick([x for x in t.entries if ok(x.conditions, ctx)], rng)
    if e.subtable: out += roll(e.subtable, ctx, rng) elif not e.none: out.append((e.item, rng.int(e.qty_min, e.qty_max)))
  return out
```
- **Reference games:** the Diablo series, World of Warcraft, Borderlands, Minecraft (data-driven loot tables).
- **Combines well with:** `weighted-rng`, `gear-rarity` (05), `procedural-affixes`, `pity-timers`.

### 07.07 Pity timers — `pity-timers`

- **Category:** randomness · bad-luck protection
- **Player fantasy:** "Even if I'm unlucky, I know exactly when it has to happen."
- **Core rules:**
  - *State:* failure counter per player per pool type (carried across banners of that type).
  - *Triggers:* each pull or drop attempt.
  - *Effects:* hard pity guarantees success at N; soft pity raises the probability per pull after a threshold; counter resets on success.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Base rate | 0.5–3 % for top rarity | Sets the headline odds |
| Soft pity start | ~70–85 % of hard pity | Most players hit the item inside the soft zone |
| Soft pity step | +5–10 % per pull | Steeper = more predictable |
| Hard pity | 50–100 pulls | The worst case players plan around |
| Carry-over | across banners of the same type | Resetting on banner change feels like a loss |

  Worked example (the script's soft-pity model: from the soft-pity start `n0` the n-th pull since the last top-rarity item succeeds with probability `rate + step × (n − n0 + 1)`, capped at 1, and exactly 1 at the hard-pity pull): base 0.6 %, soft pity from pull 74 at +6 percentage points per pull, hard pity 90. That gives 6.6 % on pull 74, 42.6 % on pull 80 and a guaranteed hit on pull 90. The command below reports 62.30 expected pulls per top-rarity item (62.2973; consolidated rate 1.605 %, `consolidated_5star_rate` 0.016052), median pull 76, p90 pull 80, p99 pull 83, and cumulative odds of 39.81 % by pull 74 and 91.85 % by pull 80 (the `disclosure_table` rows for pulls 74 and 80). Without pity only 41.82 % of players would succeed within 90 pulls and the expectation would be 166.7 pulls (`gacha_calc.py --rate 0.006 --pulls 90`). This model reproduces a widely played gacha's published 0.6 % base / 1.6 % consolidated / 90-pull guarantee; the soft-pity shape is community-measured, not officially published.
  Run: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gacha_calc.py --rate 0.006 --soft-pity-start 74 --soft-pity-step 0.06 --hard-pity 90 --pulls 90 --json`. Read `any_5star.expected_pulls`, `any_5star.percentiles` and `disclosure_table`; the script labels the top rarity "5star" throughout.
- **Dynamics:** pull planning; saving currency until a pity threshold; pity counters become part of community vocabulary.
- **Aesthetic targets (MDA):** Submission (safety), Fantasy.
- **Feedback and juice:** visible pity counter ("guaranteed within 17 pulls"); escalating reveal effects in the soft zone.
- **Failure modes and exploits:** hidden pity (players cannot trust it); resets on banner change; hard pity so far above the expected value that it rarely matters.
- **Mobile fit:** n/a — show the counter on the banner screen.
- **Monetization hooks and the ethical limit:** pity is the ethical core of paid randomness. Disclose it, show the counter, carry it over, and state the worst-case cost in real money.
- **Implementation notes:** server-side counter; pure rate function, unit-tested at every boundary.

```text
p(n) = 1.0 if n >= HARD else (BASE if n < SOFT else min(1.0, BASE + STEP * (n - SOFT + 1)))
pull(s, rng): n = s.counter + 1
  if rng.float() < p(n): s.counter = 0; return TOP
  s.counter = n; return roll_lower_tiers(rng)
```
- **Reference games:** Genshin Impact, Honkai: Star Rail, Hearthstone (packs guarantee a legendary within a fixed number of openings).
- **Combines well with:** `gacha-banners`, `rate-up`, `spark`, `prd`.

### 07.08 Gacha banners — `gacha-banners`

- **Category:** randomness · paid pull pools
- **Player fantasy:** "My favourite character is finally on a banner — I'm going for it."
- **Core rules:**
  - *State:* banner `{id, type (standard | limited | weapon), start, end, rates_by_rarity, featured[], pool[], pity_type}`; currency and tickets.
  - *Triggers:* single pull or 10-pull (often with "≥ 1 item of rarity X per 10").
  - *Effects:* rarity roll (with pity), then item roll within rarity (with rate-up); duplicates convert per `duplicate-protection`.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Top-rarity base rate | 0.5–3 % | Sets headline odds and expected cost |
| Banner duration | 2–3 weeks | Longer = less FOMO, fewer revenue peaks |
| 10-pull guarantee | ≥ 1 mid-rarity per 10 | Prevents empty-feeling multi-pulls |
| Rerun policy | limited units return after months | No reruns = maximum FOMO, maximum resentment |
| F2P pull income | measured in pulls per banner cycle vs expected pulls per featured item | Too stingy kills the non-paying base that payers play alongside |

- **Dynamics:** anticipation and saving; leak-driven planning; "pull or skip" decisions; whale vs F2P parity debates.
- **Aesthetic targets (MDA):** Fantasy, Discovery, Sensation.
- **Feedback and juice:** pull animation with rarity tells (colour shift before reveal); skippable after the first view; collection page updates.
- **Failure modes and exploits:** power creep through each new banner; regulatory exposure by country and age; reroll accounts (accepted in many markets; make onboarding pulls good enough that rerolling is pointless).
- **Mobile fit:** the genre's home — but pull screens must be skippable and quick.
- **Monetization hooks and the ethical limit:** the primary revenue engine. Publish odds (required by both stores), show pity, show expected and worst-case cost in local currency, support spending limits, and disable paid pulls where law requires (see Volatile facts).
- **Implementation notes:** banner configs versioned and immutable once live; server-side pulls with an append-only audit log; the odds page renders from the same config.
- **Reference games:** Genshin Impact, Fate/Grand Order, Fire Emblem Heroes, Granblue Fantasy.
- **Combines well with:** `pity-timers`, `rate-up`, `spark`, `hero-ascension` (05).

### 07.09 Rate-up and featured guarantees — `rate-up`

- **Category:** randomness · targeting within a rarity
- **Player fantasy:** "If I don't get the featured hero this time, the next one is guaranteed."
- **Core rules:**
  - *State:* `guaranteed` flag per banner type; featured set; optional chosen target ("path") with a failure counter.
  - *Triggers:* each top-rarity result.
  - *Effects:* featured with probability `F` (commonly 50 %) unless `guaranteed`; losing sets `guaranteed = true`; winning clears it.
  - *Maths:* starting with the guarantee flag clear, expected pulls for a featured item = E[top rarity] × (1 + (1 − F)); with F = 50 % and E = 62.30 (see `pity-timers`) → 93.45 pulls (`featured.expected_pulls` from the command under Implementation notes, which also reports featured p50 / p90 / p99 = 80 / 155 / 161 pulls); worst case = 2 × hard pity = 180 pulls.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Featured share F | 50–100 % | 100 % removes the "lost 50/50" pain entirely |
| Guarantee after loss | yes / no | Without it, worst case is unbounded |
| Featured count | 1–3 sharing the share | 3 featured at 50 % = 16.7 % each for a specific one |
| Chosen-target path | guaranteed after 1–2 off-target results | Converts a multi-featured banner into a targetable one |

- **Dynamics:** "50/50" folklore; planning around guarantee status; saving for guaranteed pulls.
- **Aesthetic targets (MDA):** Fantasy, Submission.
- **Feedback and juice:** banner shows "next top item is guaranteed featured" when the flag is set.
- **Failure modes and exploits:** multi-featured dilution hidden in fine print; guarantee state not shown; guarantee lost when the banner changes.
- **Mobile fit:** n/a — status shown on the banner page.
- **Monetization hooks and the ethical limit:** state the expected and worst-case cost of the featured item, not only the rarity.
- **Implementation notes:**

```text
on_top_rarity(s, rng):
  if s.guaranteed or rng.float() < F: s.guaranteed = false; return pick(FEATURED, rng)
  s.guaranteed = true; return pick(OFF_BANNER, rng)
```
  Validate with `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gacha_calc.py --rate 0.006 --soft-pity-start 74 --soft-pity-step 0.06 --hard-pity 90 --rate-up 0.5 --guarantee --pulls 180 --json` (expect `featured.expected_pulls` 93.45 and `featured.p_within_pulls` 1.0; without `--guarantee` the same inputs give 124.59 expected pulls and only 80.97 % within 180).
- **Reference games:** Genshin Impact (50/50 with guarantee; Epitomized Path on the weapon banner), Honkai: Star Rail.
- **Combines well with:** `pity-timers`, `spark`, `gacha-banners`.

### 07.10 Spark (exchange ceiling) — `spark`

- **Category:** randomness · deterministic ceiling
- **Player fantasy:** "However unlucky I am, after N pulls I can simply pick the one I want."
- **Core rules:**
  - *State:* spark points per banner (or banner family).
  - *Triggers:* each pull earns 1 point; exchange action at the threshold.
  - *Effects:* spend N points for a chosen featured item; leftover points expire or convert at banner end.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Threshold N | ≤ 2–3× expected pulls for the target | Higher = whale-only promise |
| Scope | per banner vs shared across banners | Shared scope is kinder |
| Expiry | expire, carry over, or convert | Expiry creates end-of-banner spend pressure |
| Target pool | featured only, or any banner item | Broader pools increase perceived value |

- **Dynamics:** commitment once close to the threshold (sunk-cost pull); clear planning maths; trust.
- **Aesthetic targets (MDA):** Submission, Fantasy.
- **Feedback and juice:** spark meter on the banner; exchange screen with the full target list.
- **Failure modes and exploits:** expiring points used to pressure last-day spending; a threshold so high it is decorative.
- **Mobile fit:** n/a.
- **Monetization hooks and the ethical limit:** spark converts unbounded cost into a known maximum. Show the maximum in real money; prefer carry-over or conversion to expiry.
- **Implementation notes:** points tracked server-side per player per scope; exchange is an idempotent transaction.
- **Reference games:** Granblue Fantasy (the 300-draw spark), Fire Emblem Heroes (sparks on some banners).
- **Combines well with:** `pity-timers`, `rate-up`, `duplicate-protection`.

### 07.11 Mystery boxes / loot boxes — `mystery-boxes`

- **Category:** randomness · bundled random rewards
- **Player fantasy:** "What's inside?" — a burst of anticipation and a pile of rewards.
- **Core rules:**
  - *State:* box types with content tables (slots × rarity tables), guaranteed minimums, duplicate handling.
  - *Triggers:* earned (wins, events, pass) or purchased; open action.
  - *Effects:* server rolls contents; reveal sequence; duplicates convert.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Items per box | 3–10 | More items = more reveals, longer animations |
| Guaranteed minimum | ≥ 1 rare per box | Protects against empty-feeling opens |
| Earned vs bought ratio | most boxes earned in play | Earned boxes are a reward; bought boxes are a regulated product |
| Tier ladder | 3–5 box tiers | Clarity of value |

- **Dynamics:** anticipation; variable-ratio reinforcement; collection progress; the social "pack opening" moment.
- **Aesthetic targets (MDA):** Sensation, Discovery.
- **Feedback and juice:** shake, crack, light burst; rarity tells; skip-all after the first reveal.
- **Failure modes and exploits:** regulatory risk (paid random items are banned in some jurisdictions, age-restricted in others); minors; pay-to-win perception. The industry trend has been away from paid boxes: Overwatch 2 launched without the original game's loot boxes (2022) and Brawl Stars retired its Brawl Boxes (2022).
- **Mobile fit:** short reveal sequences fit; long ones need skip.
- **Monetization hooks and the ethical limit:** publish odds per item class before purchase (both stores require it); offer deterministic alternatives (direct purchase, crafting); geo- and age-gate paid boxes where required; never sell boxes whose contents can be cashed out.
- **Implementation notes:** contents rolled server-side at purchase or grant time (not at open time) and logged; region and age feature flags; odds page generated from config.
- **Reference games:** EA Sports FC (Ultimate Team packs), Overwatch (original loot boxes), Brawl Stars (Brawl Boxes, retired), Hearthstone (card packs).
- **Combines well with:** `duplicate-protection`, `pity-timers`, `collections-albums` (05).

### 07.12 Slot / spin mechanics — `slot-spin`

- **Category:** randomness · fast outcome loop
- **Player fantasy:** "One more spin — maybe it's the big one, or a raid on my friend's village."
- **Core rules:**
  - *State:* spins (energy-like, regenerating), outcome table, bet multiplier.
  - *Triggers:* spin action consumes `multiplier` spins.
  - *Effects:* outcome chosen from a weighted table (currency, attack, raid, shield, spin refund, jackpot), scaled by multiplier; reels are display only.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Outcome table | currency outcomes most of the time; social outcomes rarer | Social outcomes drive the meta loop |
| Spin regen | ~1 spin per several minutes, capped | Sets session cadence (see `energy-stamina` (08)) |
| Multiplier | ×1 to ×N | Amplifies variance and spend; betting-like |
| Jackpot rate | rare | Headline excitement |

- **Dynamics:** rapid, compulsive loop; revenge raids; spin hoarding for events.
- **Aesthetic targets (MDA):** Sensation, Fellowship (attacks, raids).
- **Feedback and juice:** reel blur and staggered stops; coin showers; jackpot fanfare.
- **Failure modes and exploits:** engineered near-misses (reels stopping one symbol off the jackpot more often than chance) — a gambling technique; simulated-gambling age ratings (see Volatile facts); multipliers training betting behaviour.
- **Mobile fit:** extremely high — one tap, any session length.
- **Monetization hooks and the ethical limit:** spin packs and multipliers. No engineered near-misses beyond the natural rate, no cash-out, cap multipliers, and rate the game honestly for simulated gambling.
- **Implementation notes:** decide the outcome first, then choose reel stops that display it from a separate cosmetic RNG stream.

```text
outcome = weighted_pick(OUTCOMES, rng_game)             # the only roll that matters
stops   = display_stops_for(outcome, rng_cosmetic)      # never biased toward near-misses
```
- **Reference games:** Coin Master, Monopoly GO (dice with roll multipliers), Slotomania (social casino).
- **Combines well with:** `dice`, `energy-stamina` (08), `async-base-raid` (06).

### 07.13 Prize wheels — `prize-wheel`

- **Category:** randomness · chance moment (daily, ad-gated or event)
- **Player fantasy:** "Spin the wheel — come on, jackpot!"
- **Core rules:**
  - *State:* segments `{reward, weight}`; free spins per day; ad spins.
  - *Triggers:* free daily spin; rewarded ad; event tokens.
  - *Effects:* segment chosen by weight; wheel animates to land on it.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Segments | 6–12 | More segments = finer reward spread, harder to read |
| Visual honesty | segment arc ∝ probability, or odds shown | Mismatched arcs mislead players |
| Free / ad spins | 1 free + 1–3 ad spins per day | Ad spins are strong rewarded-ad placements |
| Jackpot segment | rare, visually prominent | Headline excitement |

- **Dynamics:** daily return ritual; ad engagement; mild anticipation.
- **Aesthetic targets (MDA):** Sensation, Submission.
- **Feedback and juice:** 3–5 s ease-out spin with ticking peg sound slowing; landing flash; reward fly-to-wallet.
- **Failure modes and exploits:** big jackpot arcs with tiny weights (deceptive); ad-spin fatigue; client-side result (decide on server for valuable prizes).
- **Mobile fit:** excellent — one tap, short.
- **Monetization hooks and the ethical limit:** rewarded ads, paid spins. Paid spins are paid random items (odds disclosure); keep visual segment size honest.
- **Implementation notes:**

```text
i = weighted_pick(WEIGHTS, rng)
target_deg = 360 * TURNS + center_deg(i) + rng.uniform(-0.4, 0.4) * seg_width_deg(i)
animate(angle: 0 -> target_deg, ease = out_cubic, duration = 4.0 s)
```
- **Reference games:** Wheel of Fortune game adaptations; daily bonus wheels across social casino and casual games.
- **Combines well with:** `login-calendar` (05), `reset-cadences` (08), `mystery-boxes`.

### 07.14 Roguelike run generation — `run-generation`

- **Category:** randomness · seeded run structure (input randomness)
- **Player fantasy:** "Every run is a new path; I choose my risks."
- **Core rules:**
  - *State:* run seed; independent RNG streams per subsystem (map, encounters, loot, offers); generated map graph of typed nodes.
  - *Triggers:* run start; floor/act transitions.
  - *Effects:* nodes typed (fight, elite, event, shop, rest, treasure, boss) under placement rules; daily seed shared by all players.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Depth per act | 10–17 nodes | Defines run length (target 20–60 min for mobile runs, with mid-run saves) |
| Branching | 2–4 choices per step | More branching = more route planning |
| Node weights | fights 45–55 %, events 15–25 %, elites, shops, rests the rest | Sets risk/reward texture |
| Placement rules | no elites in the first floors, rest before boss, no adjacent shops | Guarantees good rhythm |
| Seed sharing | daily/weekly seeds with leaderboards | Fair comparison and community talk |

- **Dynamics:** route planning; risk/reward elites; replayability; seeded races.
- **Aesthetic targets (MDA):** Discovery, Challenge.
- **Feedback and juice:** map reveals floor by floor; node icons readable at thumb size; path preview highlights.
- **Failure modes and exploits:** unwinnable seeds (validate with bots); sameness from too few node types; one subsystem consuming another's random numbers so shared seeds diverge (separate streams); save-scumming (persist RNG state).
- **Mobile fit:** good with save-anywhere and runs broken into 3–10 minute floors.
- **Monetization hooks and the ethical limit:** premium or meta-unlocks; never sell in-run rerolls in competitive daily seeds.
- **Implementation notes:** path-walk generation on a grid, then type assignment with constraints; see `procedural-generation` and `${CLAUDE_PLUGIN_ROOT}/scripts/pcg.py` for generators.

```text
rng_map, rng_enc, rng_loot = split(seed)                          # independent streams
for p in 1..PATHS: x = rng_map.int(0, W-1)
  for y in 0..H-2: nx = clamp(x + rng_map.pick([-1,0,1]), 0, W-1); edge((x,y),(nx,y+1)); x = nx
assign_types(nodes, WEIGHTS, rules=[no_elite_before(5), rest_before_boss, no_adjacent(SHOP)], rng_map)
```
- **Reference games:** Slay the Spire, Hades, Spelunky, Dead Cells.
- **Combines well with:** `deck-building`, `procedural-affixes`, `leaderboards` (06).

### 07.15 Critical hits — `crits`

- **Category:** randomness · output randomness on damage
- **Player fantasy:** "Massive crit — did you see that number?"
- **Core rules:**
  - *State:* crit chance `c`, crit multiplier `m`, optional PRD counter.
  - *Triggers:* each hit or ability resolution.
  - *Effects:* on crit, damage × m. Expected multiplier = 1 + c·(m − 1): c 20 %, m 2× → ×1.2; c 50 %, m 2.5× → ×1.75; c 100 %, m 2× → ×2 with zero variance.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Base chance | 5–15 % | Low base keeps crits special |
| Multiplier | 1.5–2.5× | High multipliers make crits decisive |
| Chance cap | 50–100 % | A 100 % cap turns crit into a flat buff and a mandatory build |
| Distribution | independent vs `prd` | PRD removes long droughts and streaks |

- **Dynamics:** crit-centred builds; damage spikes; players over-value crit relative to flat damage (show EV in tooltips).
- **Aesthetic targets (MDA):** Sensation, Expression.
- **Feedback and juice:** larger, differently coloured number; 50–80 ms hit-stop; distinct SFX layer; light screen shake (respect reduced-motion settings).
- **Failure modes and exploits:** crit stacking to the cap becomes the only build; crits deciding PvP outcomes (lower variance in PvP); streaks feel rigged (use PRD).
- **Mobile fit:** excellent — passive, pure feedback.
- **Monetization hooks and the ethical limit:** crit stats on gear; keep paid power out of PvP crit maths.
- **Implementation notes:** roll on the combat RNG stream; server-side in PvP; log crit rate per build for balance.
- **Reference games:** the Diablo series, Archero, Pokémon (critical hits), Dota 2 (PRD-based crits).
- **Combines well with:** `prd`, `procedural-affixes`, `talent-tree` (05).

### 07.16 Procedural affixes — `procedural-affixes`

- **Category:** randomness · item generation
- **Player fantasy:** "A rare with exactly the stats I need — maybe even a perfect roll."
- **Core rules:**
  - *State:* item base, item level, rarity; affix pools (prefix/suffix) with tiers `{min_ilvl, lo, hi, weight, group}`.
  - *Triggers:* item generation; crafting reroll.
  - *Effects:* affix count from rarity; affixes sampled without duplicate groups; values rolled within tier ranges.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Affixes by rarity | magic 1–2, rare 3–6 | More affixes = more evaluation work |
| Tier gating | top tiers need high item level | Ties chase to progression |
| Roll range width | ±10–30 % around the tier midpoint | Wide = "god roll" chase; narrow = calmer |
| Crafting rerolls | reroll one / all affixes for a cost | Converts randomness into a sink |

- **Dynamics:** god-roll chase; crafting economy; trading.
- **Aesthetic targets (MDA):** Discovery, Expression.
- **Feedback and juice:** comparison arrows vs equipped item; star or glow for top-tier rolls.
- **Failure modes and exploits:** affix soup (many weak affixes); one dominant affix; evaluation burden on phones (show a single comparison score and auto-equip).
- **Mobile fit:** acceptable with auto-compare and auto-salvage filters.
- **Monetization hooks and the ethical limit:** reroll materials. Paid rerolls are paid randomness — disclose the affix odds.
- **Implementation notes:**

```text
roll_item(base, ilvl, rarity, rng): item = new(base, ilvl, rarity); used = set()
  repeat rng.int(*AFFIX_COUNT[rarity]):
    a = weighted_pick([x for x in POOL[base.slot] if x.min_ilvl <= ilvl and x.group not in used], rng)
    used.add(a.group); item.affixes.append((a.id, rng.uniform(a.lo, a.hi)))
```
- **Reference games:** Diablo II–IV, Path of Exile, Borderlands.
- **Combines well with:** `gear-rarity` (05), `loot-tables`, `crits`.

### 07.17 Pseudo-random distribution — `prd`

- **Category:** randomness · streak-dampened probability
- **Player fantasy:** none directly — 25 % finally feels like 25 %.
- **Core rules:**
  - *State:* counter `N` (attempts since last success).
  - *Triggers:* each attempt.
  - *Effects:* success chance `P(N) = C·N`; on success reset `N = 1`. `C` is chosen so the long-run average equals the nominal chance.
- **Tuning knobs (computed constants):**

| Nominal | C | Guaranteed by attempt | Nominal | C | Guaranteed by attempt |
|---|---|---|---|---|---|
| 5 % | 0.00380 | 264 | 25 % | 0.08474 | 12 |
| 10 % | 0.01475 | 68 | 30 % | 0.11895 | 9 |
| 15 % | 0.03222 | 32 | 40 % | 0.20155 | 5 |
| 20 % | 0.05570 | 18 | 50 % | 0.30210 | 4 |

- **Dynamics:** fewer streaks in both directions; same expected value; slightly exploitable by "charging" the counter on harmless targets.
- **Aesthetic targets (MDA):** Challenge (more reliable planning), Submission.
- **Feedback and juice:** none required — the point is that nothing feels off.
- **Failure modes and exploits:** counter charging (attack weak targets to build N before the important hit — reset counters on target change if this matters); players expecting PRD in paid systems (paid odds must be disclosed exactly, including any counter mechanics).
- **Mobile fit:** invisible.
- **Monetization hooks and the ethical limit:** if used on paid outcomes, the published odds must describe the PRD rule, not just the nominal rate.
- **Implementation notes:** solve C by bisection so that 1 / E[attempts] equals the nominal rate; precompute a table.

```text
attempt(s, rng): p = min(1.0, C * s.n)
  if rng.float() < p: s.n = 1; return true
  s.n += 1; return false
```
- **Reference games:** Warcraft III and Dota 2 (PRD for critical strikes, bash and evasion).
- **Combines well with:** `crits`, `pity-timers`, `perceived-fairness`.

### 07.18 Input vs output randomness — `input-output-randomness`

- **Category:** randomness · design framework
- **Player fantasy:** "Luck sets the stage; my decisions decide the outcome" (input) vs "I made my move — now the dice decide" (output).
- **Core rules:**
  - *Input randomness* happens before the decision (map, hand, piece queue, shop offers); players adapt to it. *Output randomness* happens after the decision (hit roll, crit, drop); it decides whether a choice worked. The framing was popularised by Keith Burgun and is discussed at length by Geoff Engelstein (GameTek; *Building Blocks of Tabletop Game Design*, with Isaac Shalev, 2019).
  - Classify every random call in the design: input, output, or cosmetic.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Output share on decisive actions | ~0 in competitive skill games; moderate in casual | Output on decisive moments shifts blame to luck |
| Telegraphing | show enemy intent / next pieces | Converts output into input randomness |
| Mitigation | rerolls, previews, retries, insurance | Gives agency back after a bad roll |
| Variance per decision | low in PvP; higher in PvE spectacle | Matches skill expression to audience |

- **Dynamics:** input-heavy games reward planning and adaptation; output-heavy games produce drama and comeback stories, and luck complaints.
- **Aesthetic targets (MDA):** Challenge (input), Sensation (output).
- **Feedback and juice:** preview UI (next piece, enemy intent) is the feedback that turns randomness into input.
- **Failure modes and exploits:** output randomness in PvP ranked; zero randomness making content solvable and stale; hidden output randomness presented as skill.
- **Mobile fit:** casual mobile thrives on input randomness (board layouts) with small output delights (cascades).
- **Monetization hooks and the ethical limit:** do not sell mitigation of output randomness in competitive modes (pay-to-win).
- **Implementation notes:** one RNG stream per class (input, output, cosmetic) so tuning one never changes another.
- **Reference games:** Into the Breach (telegraphed enemy attacks, near-zero output randomness), XCOM (hit chances), Tetris (piece queue), Slay the Spire (card draw and enemy intents).
- **Combines well with:** `perceived-fairness`, `shuffle-bag`, `run-generation`.

### 07.19 Perceived fairness — `perceived-fairness`

- **Category:** randomness · psychology of chance
- **Player fantasy:** "The game is fair to me."
- **Core rules:**
  - Humans misjudge randomness: the gambler's fallacy (a miss is "due" a hit), the hot-hand belief, clustering illusions, and loss aversion make true randomness feel rigged against them.
  - Sid Meier's GDC 2010 keynote (*The Psychology of Game Design*) described adjusting Civilization Revolution's odds because players rejected losses at displayed favourable odds; XCOM: Enemy Unknown was reported to give hidden aim help after misses on lower difficulties; several Fire Emblem entries compute displayed hit rates from the average of two random numbers, which makes high displayed odds hit more often than shown.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Displayed-vs-actual bias (single-player only) | high displayed odds hit more often than shown | Feels fair; but it is a lie, so never in paid systems |
| Streak breaker | after 2–3 consecutive failures at ≥ 50 %, nudge | Removes the worst stories |
| Luck ledger | nudge when actual successes trail expected by > 1.5σ | Long-run fairness per player |
| Transparency | exact % shown; history log | Builds trust, especially in paid randomness |

- **Dynamics:** trust; fewer rage-quits; but players who discover undisclosed manipulation feel betrayed.
- **Aesthetic targets (MDA):** Challenge, Submission.
- **Feedback and juice:** outcome history log ("last 10 rolls"); near-miss presentation that is honest.
- **Failure modes and exploits:** manipulating against the player to drive purchases (a dark pattern); paid odds that differ from displayed odds (violates store rules and consumer law); over-smoothing so randomness disappears.
- **Mobile fit:** n/a — applies everywhere.
- **Monetization hooks and the ethical limit:** player-favouring bias is acceptable in single-player, non-paid outcomes; paid outcomes must match published odds exactly; no bias ever depends on spend.
- **Implementation notes:**

```text
ledger.expected += p; ledger.var += p * (1 - p); ledger.actual += success      # per player, per outcome class
deficit = (ledger.expected - ledger.actual) / sqrt(max(1, ledger.var))
p_eff   = p if (deficit < 1.5 or PAID_OUTCOME) else min(1.0, p + NUDGE)
```
- **Reference games:** Civilization Revolution, XCOM: Enemy Unknown, Fire Emblem series.
- **Combines well with:** `prd`, `pity-timers`, `input-output-randomness`.

### 07.20 Duplicate protection and crafting — `duplicate-protection`

- **Category:** randomness · deterministic floor under collections
- **Player fantasy:** "Duplicates still count toward something, and I can craft exactly what I need."
- **Core rules:**
  - *State:* crafting currency (dust, shards, wildcards); craft and disenchant prices per rarity; ownership.
  - *Triggers:* duplicate obtained; craft action; optional "no duplicate until owned all of rarity X" rule.
  - *Effects:* duplicates convert to currency or are rerolled; any item craftable for a fixed cost.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Disenchant ÷ craft ratio | 10–25 % (Hearthstone legendary: 400 vs 1,600 dust = 25 %) | Higher shortens time to target |
| No-dupe scope | top rarity only, or all rarities | Strongly reduces the cost of a full collection |
| Wildcards | earned per N pulls | Universal targeting |
| Exchange shop | rotating, priced in duplicate currency | Adds choice and a sink |

- **Dynamics:** bounded cost to any target; deck and roster experimentation; less frustration at duplicates.
- **Aesthetic targets (MDA):** Submission, Expression.
- **Feedback and juice:** duplicate converts with a visible currency burst; "craftable" badge when affordable.
- **Failure modes and exploits:** conversion rates so low they are decorative; crafting excluded for new items (forces paid randomness); nerf-refund abuse windows (time-box full refunds after balance changes).
- **Mobile fit:** good — one tap convert or craft.
- **Monetization hooks and the ethical limit:** reduces revenue per collector but is the strongest trust signal a random economy can offer; required to keep paid randomness defensible.
- **Implementation notes:** conversion at grant time (server); crafting as an idempotent transaction; simulate time-to-complete with and without protection.
- **Reference games:** Hearthstone (dust and duplicate protection), Clash Royale (wild cards), Marvel Snap (collection without duplicates).
- **Combines well with:** `mystery-boxes`, `gacha-banners`, `collections-albums` (05).

### 07.21 Assisted refill (board RNG) — `assisted-refill`

- **Category:** randomness · spawn-odds difficulty control
- **Player fantasy:** "Cascade! The board is on my side today."
- **Core rules:**
  - *State:* colour weights; assist level (0..k); board.
  - *Triggers:* tiles fall to fill gaps; level start; no-moves detection.
  - *Effects:* new tiles sampled from weights, optionally biased toward colours that complete matches; starting boards validated (no pre-matches, ≥ N moves); reshuffle when no valid move exists.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Colour count | 4–6 | Each extra colour sharply reduces cascades and raises difficulty |
| Refill bias | 0–30 % weight boost to match-completing colours | Invisible difficulty lever |
| Cascade cap | none or soft cap | Prevents runaway auto-wins |
| Start validation | ≥ 3–5 available moves, no matches | Fair openings |

- **Dynamics:** cascades as output-randomness delight; level difficulty dominated by colour count and refill bias.
- **Aesthetic targets (MDA):** Sensation, Challenge.
- **Feedback and juice:** chain counter with rising pitch per cascade step; "Sweet!"-style callouts at chain thresholds.
- **Failure modes and exploits:** hidden difficulty manipulation that targets payers or near-payers (never — difficulty adjustments must not depend on spend); bias so strong levels play themselves; refill RNG shared with goal spawns (separate streams).
- **Mobile fit:** core of the casual puzzle genre.
- **Monetization hooks and the ethical limit:** boosters and extra moves sell at failure; assistance should be used to rescue frustrated players, not to engineer failures.
- **Implementation notes:** tune with bots before players: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/match3_sim.py --level L.json --runs 500 --bot cascade --seed 1 --json`.

```text
refill(cell, s, rng_board): w = copy(BASE_WEIGHTS)
  if s.assist > 0: for c in colours_completing_match(cell): w[c] *= 1 + ASSIST_STEP * s.assist
  return weighted_pick(w, rng_board)
```
- **Reference games:** Candy Crush Saga, Royal Match, Bejeweled.
- **Combines well with:** `saga-map` (05), `win-streaks` (05), `perceived-fairness`.

---

## RNG engineering checklist

- [ ] One seeded, high-quality PRNG (PCG or xoshiro family) behind an interface; no platform `Math.random()`/`Random()` in simulation code.
- [ ] Independent streams per subsystem (map, combat, loot, offers, cosmetic), derived from one run seed with a splitter (e.g. SplitMix64).
- [ ] RNG state persisted in saves; outcomes rolled at grant time, not reveal time (no save-scumming).
- [ ] Server-side rolls for anything paid, competitive or tradable; client rolls only cosmetics.
- [ ] Unbiased integer sampling (rejection, not modulo); integer weights.
- [ ] CI test: chi-square goodness-of-fit over ≥ 100k samples for every table; Monte Carlo of pity, rate-up and spark against `gacha_calc.py`.
- [ ] Odds page generated from the live config, versioned, and shown before purchase; config changes require a new version.
- [ ] Telemetry: `gacha_pull` / `loot_open` events with `banner_id`, `pity_counter`, `rarity`, `config_version`.

## Volatile facts (as of Oct 2026 — verify before relying)

- **Apple** (App Review Guideline 3.1.1): apps offering randomized virtual items for purchase must disclose the odds of each item type before purchase — [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/).
- **Google Play** (Payments policy): games offering randomized virtual items from a purchase must clearly disclose the odds in advance of, and close to, the purchase — [Play Console Help: Payments policy](https://support.google.com/googleplay/android-developer/answer/9858738).
- **Belgium:** paid loot boxes treated as illegal gambling since 2018; reported penalties up to €800k and prison, doubled where minors are involved — [Programming Insider](https://programminginsider.com/loot-boxes-regulation-and-where-the-line-sits-in-2026/).
- **Brazil:** the ECA Digital law (signed Sep 2025) bans selling loot boxes to under-18s from March 2026; a June 2026 court decision against Riot Games ordered damages, age verification and probability disclosure — [Sheep Esports](https://www.sheepesports.com/articles/brazil-court-orders-riot-games-to-pay-eur2-5m-over-league-of-legends-loot-boxes/en).
- **Australia:** games classified after Sep 22, 2024 with paid chance-based items get at least an M rating; simulated gambling is R18+ — [PCWorld](https://www.pcworld.com/article/2464538/all-games-with-loot-boxes-will-be-rated-m-or-higher-in-australia.html).
- **Netherlands:** no effective ban after the courts overturned the regulator's approach (sources conflict on details) — [Programming Insider](https://programminginsider.com/loot-boxes-regulation-and-where-the-line-sits-in-2026/).
- **EU:** a Digital Fairness Act could bring EU-wide rules, reportedly not before 2028 — [Programming Insider](https://programminginsider.com/loot-boxes-regulation-and-where-the-line-sits-in-2026/).
- **Not re-verified (background only, reported positions):** China reportedly requires public disclosure of random-item odds (a 2017 ministry notice, with later draft online-game measures); Japan's consumer authority reportedly found "kompu gacha" (complete-the-set prizes) problematic from about 2012, and the industry self-regulates; South Korea reportedly began requiring probability disclosure for chance-based items in 2024. None of these was re-checked for this file.
- **Where current status lives:** `${CLAUDE_PLUGIN_ROOT}/skills/legal-ethics/references/privacy-children-gambling.md` (section 10, loot boxes by jurisdiction; section 15, volatile facts) is the maintained source. Treat this list as a snapshot, and confirm with `compliance-officer` before launch in any market.

## Related skills

- `monetization` — gacha product design, pricing, spending limits.
- `economy-design` — currencies, sinks, collection pacing.
- `legal-ethics` — loot-box law, minors, consumer protection.
- `procedural-generation` — generators and solvers behind `run-generation`.
- `player-psychology` — reinforcement schedules, biases and their ethical limits.
