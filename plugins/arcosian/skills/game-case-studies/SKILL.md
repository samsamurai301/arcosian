---
name: game-case-studies
description: Deconstructions of about 90 landmark games (puzzle, hyper/hybrid-casual, midcore strategy, RPG/gacha/cards, casual-social-sim, premium indie) in one 16-lens format, plus the method to deconstruct any game into deconstruction.schema.json and use precedents for decisions and analogies. Use when asked "how does X do it", "deconstruct X", "which games did this", "comparables", "X meets Y", or before choosing a loop, economy or offer.
when_to_use: Before a design decision a shipped game already faced, when filling contract.meta.comparables or analogy, or when deconstructing a competitor.
---

# Game Case Studies

Precedent is the cheapest playtest. This skill holds deconstructions of landmark games in a single format, plus the method to deconstruct any other game the same way. Its purpose is decisions: finding which shipped game already faced your choice, what it chose, why it worked in its context, and what transfers to yours.

## What this skill gives you

- **About 90 case studies** across six reference files, each in the same 16 lenses: snapshot, core loop, meta, economy, monetization, live-ops, retention, social, UX, art and audio, psychology, innovations, weaknesses, lessons, analogy hooks, and an ontology encoding.
- **A deconstruction method**: lenses, sources with evidence grades, a 1–2 day procedure, and a field-by-field encoding into `deconstruction.schema.json`.
- **Precedent search and analogy procedures** that turn cases into contract decisions (`contract.meta.comparables`, `analogy`, mechanics, economy).
- **A master index** with controlled genre tags (aligned with the `genre-playbooks` genre slugs) and a "study it for" column.
- **Cross-game patterns** (`references/cross-game-patterns.md`) that generalise the cases into reusable design moves.

## Core models

**1. Chassis + twist (lineage).** Commercial winners rarely invent a new genre. They keep a proven chassis and change one or two things. Name both before you borrow.

| Game | Chassis kept | Twist |
|---|---|---|
| Royal Match | Toon Blast / Homescapes match-3 + renovation | Speed, a single currency, win-streak boosters |
| Survivor.io | Vampire Survivors rules | Portrait, Archero-style gear meta, idle rewards |
| Block Blast! | 1010! block puzzle | Juice, tuning, ad-led long sessions at scale |
| Stumble Guys | Fall Guys format | Mobile-first, on phones before the original |
| Marvel Snap | Hearthstone-style CCG | Very small decks, short games, a stakes ("snap") bet |
| Monopoly Go! | Coin Master social loop | Board-game IP and dice board |

**2. Four clocks.** Every game runs four clocks, and a case is understood only when all four are described:
- seconds: verb and feel;
- minutes: core loop;
- days: meta and appointments;
- months: live-ops and seasons.

A missing clock is usually the main weakness. Flappy Bird had only seconds. Many premium games have no months clock, by design.

**3. Feature → rule → need (abstraction ladder).** Never transplant a feature. Climb to the rule, then to the player need, and come back down in your own genre. For example, "Butler's Gift" → "a start bonus that grows with consecutive wins and resets on loss" → competence plus loss aversion, smoothing early failure. In a roguelite, that comes down as a starting relic after a win streak.

**4. Context filter.** The same feature produces different results in a different context. Check each one:
- era: install cost, ad targeting before and after 2021 ATT;
- channel: organic or viral versus paid UA;
- IP;
- audience age and region;
- platform: premium PC versus free mobile;
- studio capability: content pipeline, UA budget.

**5. Spend-moment fit.** Monetization follows session shape (see `genre-playbooks` Core model 3):
- ads need natural breaks (Block Blast!, Crossy Road);
- IAP needs a high-intent moment (the near-miss continue, the gear wall);
- premium needs an authored experience worth a price (Monument Valley, Balatro).

When you copy a monetization feature, copy its moment as well.

**6. Survivorship and counterfactuals.** For every winner, ask who did the same thing and failed, and why. Examples: hundreds of Flappy clones, voxel hoppers after Crossy Road, sibling titles that cannibalised their parent. Weaknesses are mandatory in every case for this reason.

**7. Evidence grades.** Tag claims A to D (see Method). Never present a grade-C or grade-D number as fact, and never invent revenue figures.

## Deconstruction method

### The 16 lenses

| Lens | Question it answers | Capture | Schema field |
|---|---|---|---|
| Snapshot | Who, when, what genre, what model, how big | Developer, year, genre, model; scale only if grade A/B | `game` |
| Core loop | What the player repeats each minute | Numbered steps: action → reward → next | `core_loop` |
| Meta and progression | Why the core matters across days | Tracks, unlocks, walls | `meta_loops`, `progression` |
| Economy | What flows in and out | Currencies with kind, sources, sinks, caps; earn rates | `economy` |
| Monetization | What is sold, when, how | Offers, price ladder, triggers, ad placements and pacing | `monetization` |
| Live-ops | The months clock | Event types, cadence, passes, content drops | `liveops` |
| Retention hooks | Why players return tomorrow | Timers, streaks, obligations, cliffhangers | `retention_hooks` |
| Social layer | Who else is involved | Teams, PvP, gifting, sharing, async vs sync | `social` |
| UX and onboarding | How fast to fun, how readable | FTUE timestamps, input mapping, HUD | `ux_notable` |
| Art and audio | Identity and feedback | Style, palette, readability, juice, sonic identity | `art_audio_notable` |
| Psychology | Which principles drive behaviour | Named principle → mechanic → ethical line | `psychology` |
| Innovations | What was new *at the time* | Firsts relative to the predecessors | `innovations` |
| Weaknesses | What fails, who is harmed | Design, business and ethical criticism | `weaknesses` |
| Lessons | What a designer should do | Imperative, testable statements | `lessons` |
| Analogy hooks | What transfers where | Rule → target genre | `borrow_for_us` (project-specific) |
| Ontology encoding | Machine-readable summary | Loops and currencies in contract field names | all of the above |

### Psychology vocabulary used in the cases (summarised, with attribution)

| Principle | Source | Typical mechanic | Ethical line |
|---|---|---|---|
| Variable-ratio reinforcement | Skinner | Refills, drafts, chests | Disclose odds; no paid randomness for minors |
| Loss aversion / prospect theory | Kahneman and Tversky, 1979 | Streak loss, revive prompts | No fabricated losses or countdown pressure on minors |
| Near-miss effect | Reid, 1986 | Fail screen with one goal left | Never manufacture near-misses |
| Goal-gradient | Hull, 1932; Kivetz et al., 2006 | Progress bars, maps | — |
| Endowed progress | Nunes and Drèze, 2006 | Pre-filled bars | — |
| Zeigarnik effect | Zeigarnik, 1927 | Unfinished levels, story cliffhangers | — |
| Flow | Csikszentmihalyi, 1990 | Difficulty matched to skill | — |
| Self-determination (competence, autonomy, relatedness) | Deci and Ryan, 1985 | Mastery, choice, teams | — |
| IKEA effect / endowment | Norton, Mochon and Ariely, 2012; Thaler, 1980 | Décor choices, gear investment | Watch sunk-cost exploitation |
| Social proof, reciprocity, scarcity | Cialdini, 1984 | Friend maps, gifting, limited offers | No fake scarcity |
| Information gap (curiosity) | Loewenstein, 1994 | Secrets, next room, hidden layers | — |
| Peak-end rule | Kahneman et al., 1993 | End-of-level spectacle | — |

### Sources and evidence grades

| Grade | Source type | Examples | Use for |
|---|---|---|---|
| A | First-hand or primary | Your own recorded play; patch notes; in-game odds disclosures; developer talks (GDC Vault); developer blogs; company filings | Mechanics, odds, official numbers |
| B | Reputable secondary | Trade press (GamesIndustry.biz, PocketGamer.biz, Mobilegamer.biz); market intelligence (Sensor Tower, AppMagic); peer-reviewed papers | Scale, dates, trends |
| C | Community | Wikis, Reddit and Discord datamines, video deconstructions, independent analyst newsletters | Earn rates, hidden rules (verify) |
| D | Inference | Your estimates from observation | Label "inferred"; never as fact |

Ad libraries (for example, Meta's Ad Library) show a game's user-acquisition creatives, which is grade A evidence of how the game is *marketed* but not of how it plays. One- to three-star store reviews, sorted by "most helpful", are the fastest grade-C map of weaknesses.

### Procedure: deconstruct a game in 1–2 working days

1. **Frame (15 min).** Write the decision this deconstruction serves, for example "should our runner use energy?". Deconstructions without a question sprawl.
2. **Desk research (60–90 min).** Gather the store page, patch notes, official site and blog, developer talks, odds disclosures, wiki and community pages, market data for scale, and the ad library. Log every source URL with its grade.
3. **FTUE capture (60 min on a real phone, screen-recorded).** Log the timestamp of each event below, then compute time-to-first-input, time-to-aha, taps-to-gameplay, first-offer and first-ad times.

| t (mm:ss) | Event |
|---|---|
| | First input |
| | First win |
| | First fail |
| | First currency grant |
| | First spend prompt |
| | First offer |
| | First ad |
| | First social prompt |
| | First permission ask (notifications, ATT) |
| | First wall or energy-out |
| | Aha moment |

4. **Day 1–7 diary (or a compressed equivalent).** Log sessions, what brought you back (notifications, timers), the first wall, and the first event joined.
5. **Economy map.** For each currency, record kind, sources, sinks and cap. Measure earn per session. Tabulate price per hard-currency unit across packs (the value curve). Estimate days-to-wall for a non-payer.
6. **Monetization map.** List every offer with its trigger, price tier and contents, and every ad placement with its pacing (interstitial interval, first-ad time). Spend tests are done by a human with an approved budget. Agents never make purchases.
7. **Live-ops calendar.** Observe 2–4 weeks, or reconstruct from community calendars. Record event types, cadence and pass structure.
8. **Synthesis.** Write the four clocks, psychology (principle → mechanic → ethical line), innovations relative to predecessors, weaknesses (including review mining), lessons, and analogy hooks.
9. **Encode and validate.** Write `.gamestudio/research/deconstruction-<slug>.json`, then run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py validate .gamestudio/research/deconstruction-<slug>.json`.
10. **Critic pass.** `arcosian:critic` challenges every number, every "first", and every lesson. Downgrade or cut what cannot be sourced.

### Encoding into `deconstruction.schema.json`

Conventions used in every case file (and expected in new deconstructions):
- **Currency `kind`** (the design-contract schema and `economy-design` definitions; `economy-design/references/currency-architecture.md` §2 has the full table):
  - `soft`: earned freely, high volume, spent constantly. It may also be sold as a top-up.
  - `hard`: scarce, earnable **and** purchasable. This is the usual mobile gem, diamond or coin (Royal Match coins, Genshin's Primogems). A currency that is both earned and bought is `hard`, never `premium`.
  - `premium`: purchase-only, a paid balance. Use it for a paid-only currency or a paid-only half of a split currency (Genesis Crystals, Poké Gold, Minecoins).
  - `energy`: lives, energy, stamina.
  - `material`: spendable progression tokens and items (stars spent on décor, gear scrolls, boosters). A scarce currency that cannot be bought is `material`, `soft` or `event`, whichever fits.
  - `xp`: non-spendable progression (score, unlock counters, pass XP).
  - `event`: seasonal tokens.
- **Loop `type` and `period`**:
  - Core loops are `core` with period `seconds` or `minutes`.
  - Account progression is `meta` with period `session` or `daily`.
  - Events and seasons are `liveops`, team loops `social`, and offer cycles `monetization`.
- **Step ids** are short (`c1`, `m1`) and `next` closes the cycle. Actions and rewards are snake_case verbs and nouns.
- **Unknown numbers** are `null` with a note, never guesses.

Worked example (abridged; the full case is in `references/hyper-hybrid-casual.md` §10):

```json
{"schema_version": "1.0",
 "game": {"title": "Archero", "developer": "Habby", "year": 2019, "genre": "hybrid-casual", "platforms": ["ios", "android"]},
 "core_loop": {"id": "ar_core", "type": "core", "period": "minutes", "steps": [
   {"id": "c1", "action": "move_to_dodge_stop_to_autoshoot", "reward": "room_cleared_xp_coins", "next": "c2"},
   {"id": "c2", "action": "draft_one_of_three_abilities", "reward": "run_power_spike", "next": "c3"},
   {"id": "c3", "action": "beat_boss_or_die", "reward": "chapter_progress_or_revive_offer", "next": "c1"}]},
 "meta_loops": [{"id": "ar_meta", "type": "meta", "period": "daily", "steps": [
   {"id": "m1", "action": "spend_energy_on_runs", "reward": "coins_gear_scrolls", "next": "m2"},
   {"id": "m2", "action": "upgrade_and_fuse_gear", "reward": "account_power", "next": "m1"}]}],
 "mechanics": [{"id": "stop_to_shoot", "name": "Stop-to-shoot", "category": "input", "verbs": ["move", "stop"],
   "rules": ["moving suppresses attacks", "standing still auto-targets the nearest enemy"],
   "parameters": [{"key": "attack_interval", "value": null, "unit": "s", "note": "not public; measure"}],
   "dynamics": ["kite-and-plant rhythm"], "aesthetics": ["challenge"], "references": ["Archero"]}],
 "economy": {"currencies": [
   {"id": "energy", "kind": "energy", "sources": ["regen", "gems", "rewarded_ad"], "sinks": ["run_start"], "cap": null},
   {"id": "gems", "kind": "hard", "sources": ["iap", "events"], "sinks": ["chests", "energy", "revive"], "cap": null}],
   "sources": ["runs", "chests", "events", "iap", "rewarded_ad"], "sinks": ["gear_levels", "talents", "chests", "revive"]},
 "progression": {"tracks": [{"id": "chapters", "type": "content"}, {"id": "gear_rarity", "type": "power"}]},
 "monetization": {"model": "hybrid", "top_offers": ["starter_pack", "gem_packs", "equipment_chests", "pass"],
   "ads": {"rewarded": ["revive", "reroll", "double_rewards"], "interstitial": null}},
 "liveops": ["limited_modes", "new_chapters_and_heroes", "seasonal_pass"],
 "retention_hooks": ["energy_cadence", "gear_power_curve", "next_chapter"],
 "social": ["leaderboards"], "ux_notable": ["one_thumb_stop_to_shoot", "portrait", "pause_safe_drafts"],
 "art_audio_notable": ["readable_projectiles_and_telegraphs"],
 "psychology": ["variable_reward_drafts", "endowed_progress", "loss_aversion_at_revive"],
 "innovations": ["context-sensitive single input", "F2P gear meta on a roguelite core"],
 "weaknesses": ["late-chapter gear walls", "energy gating", "random chests under loot-box rules"],
 "lessons": ["one thumb, two meanings", "run draft plus account gear is the hybrid-casual backbone"],
 "borrow_for_us": ["stop-to-act aiming for our turret mode"],
 "sources": ["https://<store-page>", "https://<patch-notes>"]}
```
Replace the placeholder URLs. This example validates against the schema as written (`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_json.py --schema ${CLAUDE_PLUGIN_ROOT}/scripts/schemas/deconstruction.schema.json --instance FILE`). Field shapes to remember: `monetization.ads` is a string, an object or `null` (not a list); `economy.currencies[]` entries may be strings or objects; `liveops`, `social` and `progression` accept a string, list or object. If the schema changes, follow the validator output.

## Decision procedures

### A. Precedent search for a design decision
1. Write the decision as a question with options, for example "lives, no lives, or unlimited-lives offers for our block puzzle?".
2. Search the master index tags and run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py kb "lives energy" --skill game-case-studies --limit 8`.
3. Pick 3–5 precedents, including at least one counterexample and one game in a different genre.
4. Fill a table: game | option chosen | context (model, audience, era) | evidence it worked (grade) | transfers to us? (yes, partly, no — and why).
5. Decide, then record each precedent in `contract.meta.comparables` as `{title, borrow, change}` and log the reasoning with `gs.py progress "..."`.

Worked example. Block Blast! (ads-led, long sessions) and Wordscapes (hint sink) run no energy. Candy Crush and Royal Match (IAP-led, authored levels) gate with lives. Vampire Survivors (premium) uses no gates. **Decision**: an ads-led systemic puzzle runs with no energy, monetizes at natural breaks, and offers rewarded continues. An IAP-led authored ladder may use generous lives.

### B. Analogy transplant (structure mapping)
Following Gentner's structure-mapping theory (1983), good analogies map *relations*, not surface attributes ("it has candy").
1. State the source rule as a relation: "consecutive wins → a growing start bonus; a loss resets it".
2. Build a role-mapping table: source element → target element (level win → run win; start booster → starting relic).
3. Check systematicity. Does the target have the supporting structure (discrete attempts with win and loss, short attempts, a visible streak)? If not, stop.
4. Check constraints: session length, input, economy balance, ethics (is the streak loss used to push purchases?).
5. Write the hypothesis as a metric: "raises D7 by more than 2 points without lowering win-rate fairness".
6. Run the smallest test: a prototype, a bot simulation, or an A/B test (`ab_test.py size --baseline 0.12 --mde 0.02`).
7. Encode the result as a mechanic card (`mechanic-card.schema.json`, `references` = source titles) and add it to `comparables`.

The "Analogy hooks" line in every case is the starting list. `analogy-engine` holds the general method.

### C. Picking comparables for a concept (`concept-lab`, `new-game`)

| Question | Read these cases |
|---|---|
| FTUE and time-to-aha | Royal Match, Fruit Ninja, Helix Jump, Monument Valley |
| Energy vs no energy | Candy Crush, Block Blast!, Archero, Vampire Survivors |
| One currency vs many | Royal Match, Archero, Genshin Impact |
| Ads-led monetization | Block Blast!, Crossy Road, Wordscapes, Magic Sort! |
| Live-ops cadence | Subway Surfers, Royal Match, Genshin Impact, Monopoly Go! |
| Social retention | Toon Blast, Clash of Clans, Among Us, Duolingo |
| Premium positioning | Monument Valley, Balatro, Bloons TD 6, Stardew Valley |
| Indie rule → F2P product | Vampire Survivors → Survivor.io; Hearthstone → Marvel Snap |
| Ethical-risk precedents | Candy Crush (fail offers), Coin Master, Raid: Shadow Legends, Homescapes (ads) |
| Second game from a studio | Royal Kingdom, Homescapes, Toon Blast |

### D. Clone-and-improve vs innovate

| Situation | Move | Precedent |
|---|---|---|
| Consolidated genre, large UA budget, execution edge | Refine the chassis; compete on speed and feel | Royal Match |
| Consolidated genre, small UA budget | Do not clone. Find a twist, a niche audience or premium positioning | Two Dots, Wordscapes |
| Emerging trend with no mobile incumbent | Fast-follow with mobile-native controls | Stumble Guys, Survivor.io |
| Novel rule from a small team | Innovate; premium or fair free-to-play | Vampire Survivors, Balatro |
| Commodity mechanic, ad-led | Win on tuning, juice and distribution | Block Blast! |

### E. Weakness mining → opportunity
For the top 3–5 competitors, list each case's "Weaknesses" plus the clusters from one- to three-star reviews. Fill a table: weakness | who is hurt | our answer | cost to us (ARPDAU, scope) | risk. Keep only answers that a player would notice in the first session or the first week. Example: "gear walls in survivor-likes" → skill-based progression with cosmetic monetization → lower ARPDAU, which must be offset by lower CPI from a fairness message.

## Mobile specifics
- **Session shapes from the cases**:
  - Hyper-casual runs of 30 s to 3 min (Flappy Bird, Helix Jump).
  - Hybrid runs of 3–10 min (Archero, Survivor.io).
  - Puzzle levels of 1–3 min inside 5–20 min sessions.
  - Matches from about 3 min (Clash Royale, Brawl Stars) to 10–20+ min (MOBAs, battle royales) in the midcore PvP cases.

  Copy the session shape, not just the loop.
- **One-thumb portrait** dominates the casual and hybrid cases. Use landscape only where two sticks are required (several midcore shooters).
- **Thumb occlusion**: drag games float the piece above the finger (Block Blast!). Check every drag verb for it.
- **Interruptions**: draft and level-up screens pause the action (Archero, Vampire Survivors). Treat every 3-second interruption as normal.
- **Ad placements are designed moments**: compare opt-in rewarded video at desire moments (Crossy Road) with frequent interstitials (hyper-casual). Set pacing in `contract.monetization.ads`.
- **UA and creatives**: the 3-second muted-clip readability test (Helix Jump, Count Masters), and creative honesty (the Homescapes ad ruling).
- **Low-end devices**: Free Fire's market fit, and particle load in survivor-likes. Deconstruct on a mid- or low-tier Android phone as well as a flagship.

## Anti-patterns

| Anti-pattern | Detect it | Fix |
|---|---|---|
| Feature-list deconstruction | No loop steps, no four clocks | Rewrite with the 16 lenses; the core loop first |
| Surface analogy | The mapping lists looks, theme or setting only | Use procedure B; map relations |
| Cargo-cult feature | The borrowed feature lacks its supporting structure (a streak bonus without discrete attempts) | Climb the feature → rule → need ladder |
| Survivorship bias | No failed comparables named | Add counterexamples (Core model 6) |
| Era blindness | Copying 2014 paid-to-free or 2018 hyper-casual economics unchanged | Apply the context filter; re-run the LTV maths |
| Unsourced numbers | Revenue or retention with no grade A/B source | Cut, or label "reported, approximate" with source |
| Copying dark patterns | "The top-grosser does it" used as the justification | Check `legal-ethics` and `monetization` ethics rules first |
| Copying expression | Matching art, layout or trade dress of a hit | Mechanics are not protected; close visual copying is a legal risk (see Tetris in `references/puzzle-casual.md`) |
| First-hour-only analysis | No day-7 wall, no live-ops observed | Run procedure steps 4 and 7 |
| Hagiography | The weaknesses section is empty or soft | `arcosian:critic` review before use |

## Using the ontology
- **Documents**: deconstructions follow `${CLAUDE_PLUGIN_ROOT}/scripts/schemas/deconstruction.schema.json` and live in `.gamestudio/research/`. Validate with `gs.py validate PATH`.
- **Contract links**:
  - `contract.meta.comparables` takes `{title, borrow, change}` for each precedent.
  - `contract.meta.analogy` takes the "X meets Y" line.
  - `concept.schema.json` uses `comparables`, `analogy` and `hook` (the one changed thing from Core model 1).
- **Mechanics**: extract reusable mechanics as `mechanic-card.schema.json` cards, with the case titles in `references` (see `mechanics-codex`).
- **Economy replicas**: rebuild a case economy in `economy-model.schema.json` to test a borrowed structure: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/economy_sim.py --model .gamestudio/economy/replica.json --runs 200 --seed 1 --json`.
- **Difficulty patterns from the cases**:
  - Saga sawtooth: `difficulty_curve.py generate --levels 60 --pattern sawtooth --base 0.85 --floor 0.35 --period 10 --json`.
  - Match-3 boards: `match3_sim.py --level PATH --runs 500 --bot greedy --seed 1 --json`.
  - Sort levels: `puzzle_solver.py --level PATH --algo bfs --json`.
- **Gacha and pity checks** (the RPG cases): `gacha_calc.py --rate R --soft-pity-start N --hard-pity N --pulls N --json`. **Retention comparisons**: `retention_ltv.py fit --points "1:0.42,7:0.18,30:0.07" --json`.
- **Workflow and agents**:
  - Run the process skill `deconstruct` (`/arcosian:deconstruct`), which drives the `/arcosian:deconstruct-game` workflow.
  - Typical agents are `arcosian:market-analyst` (sources, market), `arcosian:game-designer` (loops, mechanics), `arcosian:systems-designer` (economy), `arcosian:monetization-designer` (offers, ethics) and `arcosian:critic` (claims).

## Reference library

| File | Contains | Read when |
|---|---|---|
| `references/puzzle-casual.md` | 14 cases: Candy Crush Saga, Royal Match, Homescapes, Toon Blast, Block Blast!, Wordscapes, Two Dots, triple-match, Magic Sort!/water sort, screw and pin puzzles, Cut the Rope, Threes!/2048, Tetris (mobile), Royal Kingdom; lineages, archetype table, spend moments, difficulty knobs | Any puzzle or casual concept; level pipelines; IAP vs ads for puzzles |
| `references/hyper-hybrid-casual.md` | 14 cases: Flappy Bird, Crossy Road, Helix Jump, Hole.io, Subway Surfers, Temple Run, Fruit Ninja, Angry Birds, Stumble Guys, Archero, Survivor.io, Vampire Survivors, Count Masters, Paper.io 2; LTV maths, hybrid-casual recipe, verb table | Ad-led or marketability-first concepts; adding a meta to a simple core |
| `references/midcore-strategy.md` | 16 cases: base builders, 4X, tower defense, MOBA, battle royale and shooters | Strategy, PvP, alliance and season design |
| `references/rpg-gacha-cards.md` | 15 cases: gacha RPGs, idle RPGs, CCGs, location-based, trainer sims | Collection, gacha, card and hero designs; pity and banner decisions |
| `references/casual-social-sim.md` | 16 cases: social casino-adjacent, farming, merge, life sim, UGC platforms, social deduction, async word and sports, gamified apps | Social loops, timers, merge, narrative choice, sports PvP |
| `references/premium-indie.md` | 15 cases: premium and indie mobile and cross-platform landmarks | Premium pricing, authored experiences, roguelite and deckbuilder design |
| `references/cross-game-patterns.md` | 59 pattern cards (P01–P59) in seven families (core loop and feel, run structure, meta and progression, economy and randomness, social, live-ops and time, identity and positioning), each with definition, mechanism, games, risks, ontology tags and apply/avoid; a pattern index with ethics risk ratings; stacks of patterns by game archetype; a conflicts and interactions table; a procedure for selecting patterns for a concept; and an ethics screen | When a design question spans genres, as a checklist after picking comparables, or to turn chosen patterns into contract entries |

## Master index of case studies

Tags: the first tag is the `genre-playbooks` genre slug (`other` where none fits), followed by subgenre tags. Model: IAP, ads, hybrid (ads + IAP), premium, sub (subscription), free.

| # | Game | File | Tags | Model | Study it for |
|---|---|---|---|---|---|
| 1 | Candy Crush Saga | puzzle-casual | puzzle; match-3, saga-map | IAP | Content cadence, near-miss continue, bot-tested difficulty |
| 2 | Royal Match | puzzle-casual | puzzle; match-3, renovation-meta | IAP | Time-to-fun, single currency, win-streak boosters |
| 3 | Homescapes | puzzle-casual | puzzle; match-3, renovation-meta, story | IAP | Narrative meta; ad-creative honesty |
| 4 | Toon Blast | puzzle-casual | puzzle; blast, teams | IAP | Simplest verb; team tournaments |
| 5 | Block Blast! | puzzle-casual | puzzle; block-puzzle | hybrid (ads-led) | Evergreen mechanic + juice; generator as difficulty |
| 6 | Wordscapes | puzzle-casual | puzzle; word | hybrid | Audience-first aesthetic; hint economy |
| 7 | Two Dots | puzzle-casual | puzzle; connect | IAP | Power move from the core gesture |
| 8 | Triple-match (Triple Match 3D genre) | puzzle-casual | puzzle; tile-match, triple-match | hybrid | Bounded buffer as difficulty knob |
| 9 | Magic Sort! / water sort | puzzle-casual | puzzle; sort | hybrid (ads-led) | Solver-verified deterministic levels |
| 10 | Screw and pin puzzles (genre) | puzzle-casual | puzzle; screw-pin, physics | hybrid (ads-led) | Ad-creative discovery; deterministic physics |
| 11 | Cut the Rope | puzzle-casual | puzzle; physics-puzzle | premium → F2P | Reactive character; 3-star mastery |
| 12 | Threes! and 2048 | puzzle-casual | puzzle; number-merge | premium / free | Depth vs accessibility; cloning |
| 13 | Tetris (mobile) | puzzle-casual | puzzle; falling-block | varies by licensee | Touch controls; randomiser fairness; legal risk |
| 14 | Royal Kingdom | puzzle-casual | puzzle; match-3, kingdom-meta | IAP | Second-hit strategy |
| 15 | Flappy Bird | hyper-hybrid-casual | hypercasual; one-button | ads | Instant retry; five-parameter tuning; virality |
| 16 | Crossy Road | hyper-hybrid-casual | hypercasual; endless-hopper | hybrid | Opt-in rewarded video; cosmetic collection |
| 17 | Helix Jump | hyper-hybrid-casual | hypercasual; one-gesture | ads | 3-second readability; marketability tests |
| 18 | Hole.io | hyper-hybrid-casual | hypercasual; io | ads | In-round escalation; bot honesty |
| 19 | Subway Surfers | hyper-hybrid-casual | action-arcade; endless-runner | hybrid | World Tour re-theming live-ops |
| 20 | Temple Run | hyper-hybrid-casual | action-arcade; endless-runner | IAP | Swipe-to-turn; paid → F2P switch |
| 21 | Fruit Ninja | hyper-hybrid-casual | action-arcade; touch-native | premium → hybrid | Juice the verb; modes per motivation |
| 22 | Angry Birds | hyper-hybrid-casual | puzzle; physics-puzzle | premium → IAP | Readable physics; brand extension |
| 23 | Stumble Guys | hyper-hybrid-casual | party; party-royale | IAP | Trend fast-follow; filled lobbies |
| 24 | Archero | hyper-hybrid-casual | hybrid-casual; roguelite | hybrid | Stop-to-shoot; draft + gear backbone |
| 25 | Survivor.io | hyper-hybrid-casual | hybrid-casual; survivor-like | hybrid | Indie rules + F2P meta + idle rewards |
| 26 | Vampire Survivors | hyper-hybrid-casual | roguelite; survivor-like | premium (mobile free + optional ads) | Movement-only input; evolution recipes |
| 27 | Count Masters | hyper-hybrid-casual | hypercasual; crowd-runner | ads | Math gates; number as avatar |
| 28 | Paper.io 2 | hyper-hybrid-casual | hypercasual; io, territory | ads | Visible exposure; greed-sized bets |
| 29 | Clash of Clans | midcore-strategy | strategy; base-builder, async-pvp | IAP | Builder-time gating; async raids; clans |
| 30 | Clash Royale | midcore-strategy | pvp; card-battler | IAP | Short real-time duels; card ladder |
| 31 | Brawl Stars | midcore-strategy | pvp; hero-shooter | IAP | Short team matches; roster progression |
| 32 | Rise of Kingdoms | midcore-strategy | strategy; 4x | IAP | Civilisation 4X; seasonal kingdom wars |
| 33 | Last War: Survival | midcore-strategy | strategy; 4x | IAP | Casual mini-game funnel into a 4X |
| 34 | Whiteout Survival | midcore-strategy | strategy; 4x, survival-city | IAP | Survival city-builder framing for 4X |
| 35 | Lords Mobile | midcore-strategy | strategy; 4x, hero-rpg | IAP | Hero RPG layered on kingdom war |
| 36 | Boom Beach | midcore-strategy | strategy; base-builder, co-op | IAP | Co-op operations; exploration map |
| 37 | Plants vs. Zombies 2 | midcore-strategy | strategy; tower-defense | hybrid | Lane TD readability; premium → F2P sequel |
| 38 | Bloons TD 6 | midcore-strategy | strategy; tower-defense | premium + IAP | Upgrade-path depth; premium with live content |
| 39 | Kingdom Rush | midcore-strategy | strategy; tower-defense | premium + IAP | Hero + barracks; authored levels |
| 40 | Mobile Legends: Bang Bang | midcore-strategy | pvp; moba | IAP | MOBA compressed for phones; emerging markets |
| 41 | Honor of Kings | midcore-strategy | pvp; moba | IAP | Mass-market MOBA; social graph |
| 42 | PUBG Mobile | midcore-strategy | pvp; battle-royale | IAP | Console-grade BR on phones; device scaling |
| 43 | Free Fire | midcore-strategy | pvp; battle-royale | IAP | Short BR for low-end devices |
| 44 | Call of Duty: Mobile | midcore-strategy | pvp; shooter, battle-royale | IAP | IP translation; multimode shooter |
| 45 | Genshin Impact | rpg-gacha-cards | rpg; gacha, open-world | IAP | Console-quality gacha; pity; version cadence |
| 46 | Honkai: Star Rail | rpg-gacha-cards | rpg; gacha, turn-based | IAP | Turn-based gacha; respect for player time |
| 47 | AFK Arena | rpg-gacha-cards | idle; idle-rpg, gacha | IAP | Offline accrual; hero collection |
| 48 | Raid: Shadow Legends | rpg-gacha-cards | rpg; gacha, hero-collector | IAP | Collection depth; UA scale; criticism |
| 49 | Summoners War | rpg-gacha-cards | rpg; gacha, turn-based | IAP | Rune endgame; arena PvP |
| 50 | Fate/Grand Order | rpg-gacha-cards | rpg; gacha, story | IAP | IP and story-led gacha |
| 51 | Puzzle & Dragons | rpg-gacha-cards | rpg; match-3, gacha | IAP | Puzzle combat + monster collection |
| 52 | Monster Strike | rpg-gacha-cards | rpg; physics, co-op | IAP | Local co-op slingshot RPG |
| 53 | Pokémon GO | rpg-gacha-cards | other; location-based, collection | IAP | Real-world movement loop; community events |
| 54 | Marvel Snap | rpg-gacha-cards | pvp; ccg | IAP | Small decks, short games, stakes bet |
| 55 | Hearthstone | rpg-gacha-cards | pvp; ccg | IAP | Digital-native CCG design |
| 56 | Uma Musume: Pretty Derby | rpg-gacha-cards | rpg; trainer-sim, gacha | IAP | Run-based training + idol IP |
| 57 | Arknights | rpg-gacha-cards | strategy; tower-defense, gacha | IAP | Strategic TD gacha; generous economy |
| 58 | Pokémon TCG Pocket | rpg-gacha-cards | pvp; ccg, collection | IAP | Daily pack ritual; simplified TCG |
| 59 | Legend of Mushroom (idle-RPG exemplar) | rpg-gacha-cards | idle; idle-rpg | IAP-led | Idle auto-battle progression |
| 60 | Monopoly Go! | casual-social-sim | social-casino; board-dice | IAP | Dice board + raids + IP; sticker albums |
| 61 | Coin Master | casual-social-sim | social-casino; slot-adjacent | IAP | Spin-attack-raid loop; regulatory scrutiny |
| 62 | Hay Day | casual-social-sim | tycoon-sim; farming | IAP | Production chains; player trade |
| 63 | Township | casual-social-sim | tycoon-sim; farming, city | IAP | Farm + town + mini-game hybrid |
| 64 | Merge Mansion | casual-social-sim | puzzle; merge-2, story | IAP | Merge board + mystery story |
| 65 | Travel Town | casual-social-sim | puzzle; merge-2 | IAP | Energy-driven merge with orders |
| 66 | Animal Crossing: Pocket Camp | casual-social-sim | tycoon-sim; life-sim | IAP → premium | IP-led cosy sim; service sunset |
| 67 | Among Us | casual-social-sim | party; social-deduction | hybrid (mobile) | Social deduction; streamer-led revival |
| 68 | Roblox | casual-social-sim | other; ugc-platform | IAP | UGC platform; creator economy |
| 69 | Minecraft | casual-social-sim | other; sandbox | premium | Creative sandbox; cross-platform |
| 70 | The Sims FreePlay | casual-social-sim | tycoon-sim; life-sim | IAP | Real-time timers in a life sim |
| 71 | Episode / Choices | casual-social-sim | narrative; interactive-story | IAP | Premium choices as monetization |
| 72 | Words With Friends | casual-social-sim | puzzle; word, async-pvp | hybrid | Async turn-based social |
| 73 | 8 Ball Pool | casual-social-sim | pvp; sports | hybrid | Stakes matchmaking; cue upgrades |
| 74 | Golf Clash | casual-social-sim | pvp; sports | IAP | 1v1 timing skill; club progression |
| 75 | Duolingo (gamification) | casual-social-sim | educational; gamification | sub + ads | Streaks, leagues, XP as retention |
| 76 | Alto's Odyssey | premium-indie | action-arcade; endless-runner | premium | Art- and audio-led zen runner |
| 77 | Monument Valley | premium-indie | puzzle; narrative-puzzle | premium | Impossible geometry; short authored arc |
| 78 | Florence | premium-indie | narrative; interactive-story | premium | Mechanics as metaphor |
| 79 | Balatro | premium-indie | roguelite; deckbuilder | premium | Poker hands + joker synergies |
| 80 | Stardew Valley | premium-indie | tycoon-sim; farming, rpg | premium | Farming + relationships; solo-dev scope |
| 81 | Slay the Spire | premium-indie | roguelite; deckbuilder | premium | Deckbuilder template; enemy intent |
| 82 | Dead Cells | premium-indie | roguelite; action-platformer | premium | Roguelite metroidvania; touch port |
| 83 | Mini Metro | premium-indie | strategy; minimalist-sim | premium | Systems as minimalist art |
| 84 | Reigns | premium-indie | narrative; swipe-choice | premium | Binary swipe choices; resource balance |
| 85 | Downwell | premium-indie | action-arcade; roguelite | premium | Portrait one-hand vertical design |
| 86 | Sky: Children of the Light | premium-indie | other; social-adventure | IAP (cosmetic) | Wholesome social; cosmetic monetization |
| 87 | Shattered Pixel Dungeon | premium-indie | roguelite; roguelike | free (open source) | Traditional roguelike on touch |
| 88 | Wordle | premium-indie | puzzle; daily-puzzle, word | free | One-a-day scarcity; shareable grid |
| 89 | Pocket City | premium-indie | tycoon-sim; city-builder | premium | Premium sim without IAP |
| 90 | Grindstone | premium-indie | puzzle; chain-puzzle | sub → premium | Chain-drawing combat puzzles |

Cases 29–90 are written in their own files by companion builders. Their file is authoritative for facts, and this index only routes.

## Related skills
- `analogy-engine`: the general "X meets Y" and transplant method behind procedure B.
- `genre-playbooks`: genre norms and slugs, and the agent-buildability score for each case's genre.
- `mechanics-codex`: canonical mechanic cards for mechanics extracted from cases.
- `game-ontology`: schema semantics for loops, resources and deconstructions.
- `design-theory` and `design-philosophies`: the frameworks (MDA, loops, studio doctrines) the lenses rest on.
- `player-psychology`: depth on the principles in the psychology vocabulary, and their ethical limits.
- `economy-design` and `progression-difficulty`: rebuilding and tuning borrowed economies and curves.
- `monetization`, `liveops` and `marketing-ua`: offer, calendar and creative design behind the business lenses.
- `market-intel`: current charts and scale data for snapshots (grade B sources).
- `legal-ethics`: loot boxes, misleading ads, minors, IP and clone risk.
- `game-feel`, `mobile-ux` and `level-design`: the UX, juice and level lessons the cases point to.
- Process skills `deconstruct`, `concept-lab` and `market-scan`: where this skill is applied.

## Volatile facts (as of Oct 2026 — verify before relying)
- Block Blast! topped worldwide downloads in H1 2026. Last War, Honor of Kings and Whiteout Survival led grossing in Q1 2026. Source: [Mobilegamer.biz (Sensor Tower)](https://mobilegamer.biz/data-digest-sensor-towers-h1-analysis-hay-days-comeback-julys-top-games-big-krafton-numbers-and-more/).
- Hybrid-casual spending grew 17.1% in 2025 ($3.5B → $4.2B). Source: as above.
- Voodoo moved from about 1,000 prototypes a year (2024) to about four hybrid-casual launches a year. Source: [mobilegamer.biz](https://mobilegamer.biz/voodoo-to-launch-just-four-games-per-year-after-hard-hybridcasual-pivot/).
- King's human-like playtesting bots predicted difficulty across more than 1,000 Candy Crush levels. Source: [Gudmundsson et al., 2018](https://gwern.net/doc/reinforcement-learning/imitation-learning/2018-gudmundsson.pdf).
- Case-level facts were checked on 2026-10-20 against store metadata and reputable secondary sources, and each case file's own "Volatile facts" section lists the links. Checked: Magic Sort! (Grand Games), Screw Jam (Rollic Games), Count Masters (Freeplay LLC), Block Blast! (Hungry Studio; seller Aretis Limited), Royal Kingdom (global launch 21 November 2024; protagonist King Richard), Stumble Guys (Kitka Games is Finnish; Scopely announced the deal in September 2022), Last War (publisher FUNFLY PTE. LTD.), Uma Musume (global release 26 June 2025), Subway Surfers (one billion Google Play downloads in March 2018), Flappy Bird ($50,000 a day was a developer claim to The Verge on 5 February 2014), Crossy Road (Polygon, March 2015: over $10M and 50M downloads in three months), Balatro (PEGI history, inspirations), Roblox DevEx ($0.0038 per Earned Robux since 5 September 2025) and Pocket Camp Complete (transfer window to 1 June 2025). The following stay hedged: the exact Coin Master launch day, the Travel Town acquisition year (2021 per PitchBook, 2022 per one analyst), the current mobile Tetris licensee after August 2024, the Pocket Camp Complete list price, Duolingo's energy rollout by platform, and any Savvy Games Group deal involving Dream Games.
