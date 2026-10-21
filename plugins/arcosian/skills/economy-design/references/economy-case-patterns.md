# Economy Case Patterns

Well-known mobile games are the best textbook on economy design because their structures have survived years of live tuning and millions of players. This file deconstructs the economic patterns of landmark titles — Clash Royale, the casual-puzzle lineage that leads to Royal Match, Coin Master, Monopoly Go, Hay Day, Genshin Impact, idle/incremental games and season-pass systems — in the studio's own words: currency maps, source/sink structure, signature devices, monetization surfaces, lessons, criticisms and how to model each in the ontology. It ends with cross-case comparisons and an analogy method for transplanting a pattern into a new game. Specific numbers (rates, timers, prices) in live games change often and are frequently community-measured; treat any figure here as illustrative and check the current game before quoting it. Full game deconstructions use `deconstruct` and `game-case-studies`; this file is economy-only.

## Contents

1. [How to read a game's economy](#1-how-to-read-a-games-economy)
2. [Clash Royale: duplicates as the upgrade currency](#2-clash-royale-duplicates-as-the-upgrade-currency)
3. [Casual puzzle lineage to Royal Match: the continue economy](#3-casual-puzzle-lineage-to-royal-match-the-continue-economy)
4. [Coin Master: inflationary coins, escalating sinks](#4-coin-master-inflationary-coins-escalating-sinks)
5. [Monopoly Go: energy multipliers and stacked events](#5-monopoly-go-energy-multipliers-and-stacked-events)
6. [Hay Day: production chains, storage and a capped market](#6-hay-day-production-chains-storage-and-a-capped-market)
7. [Genshin Impact: transparent gacha at scale](#7-genshin-impact-transparent-gacha-at-scale)
8. [Idle and incremental games: exponential costs and prestige](#8-idle-and-incremental-games-exponential-costs-and-prestige)
9. [Pass systems: selling a reward track](#9-pass-systems-selling-a-reward-track)
10. [Cross-case comparison](#10-cross-case-comparison)
11. [Transplanting patterns: the analogy method](#11-transplanting-patterns-the-analogy-method)
12. [Volatile facts](#12-volatile-facts-as-of-oct-2026--verify-before-relying)

---

## 1. How to read a game's economy

Run this checklist on any title (it feeds `deconstruction.schema.json → economy {currencies, sources, sinks}`):

1. **Currency map**: every currency, its kind (ontology enum), where it is shown, whether it is purchasable.
2. **The main faucet**: which loop produces most of the soft currency? (Usually the core loop; if it is ads or events, note it.)
3. **The main sinks**: what absorbs median income (inelastic) and surplus (elastic)?
4. **The pacing device**: energy, timers, storage caps, content gates or difficulty?
5. **The monetization surfaces**: what does money buy — time, power, chance, expression, access?
6. **Signature device**: the one structural idea that makes this economy distinctive.
7. **Feedback structure**: positive loops (snowball) and negative loops (friction); where the game resets.
8. **Social flows**: trading, gifting, stealing, team pools.
9. **Criticisms**: where players or regulators push back; this is where the doctrine draws its lines.
10. **Model sketch**: the minimal set of economy-model nodes that reproduces the behaviour.

---

## 2. Clash Royale: duplicates as the upgrade currency

**Snapshot.** Supercell, 2016; real-time PvP card battler. The classic economy (launch to the early 2020s) is described here; Supercell has reworked rewards, upgrade materials and passes several times since, so verify current systems.

**Currency map (classic):**

| Currency | Kind | Role |
|---|---|---|
| Gold | soft | Paid with card copies to upgrade a card; also buys cards in the shop |
| Gems | hard | Open/skip chests, buy chests and offers, event entries |
| Card copies (per card) | material | Required duplicates to upgrade that specific card |
| Chest slots / timers | energy-like | Four slots; chests take hours to unlock (longer for better chests) |
| Trophies | xp-like | Matchmaking rating and progression road |

**Core economic loop.** Win battle → receive a chest if a slot is free → unlock on a timer (or skip with gems) → cards + gold → upgrade cards (copies + gold, both scaling steeply by level) → stronger deck → more trophies → new arenas and a better reward pool.

**Signature devices:**
- **Duplicates are the progression currency.** Every card copy is useful until max level, so random rewards rarely feel wasted; the cost curve of copies and gold per level is the main long-term sink.
- **Chest slots as session pacing.** Four slots with multi-hour timers mean a player can bank only a limited number of rewards; once the slots are full, extra wins yield no chest. It drives return visits (open, refill) and sells gem skips.
- **Rarity-scaled scarcity.** Rarer cards need fewer copies per level but drop far less often; legendary-tier cards become the chase.

**Lessons to borrow:**
- Make duplicates useful (upgrade input) rather than waste.
- Use a small number of reward "slots" as a gentle cap on session value.
- Equalise card levels in competitive event modes so that skill modes exist for free players.

**Criticisms and doctrine limits:** level differences in ladder PvP read as pay-to-win; full slots make extra play feel unrewarded (players stop when slots are full, which caps engagement); chest contents were random and purchasable. Under the studio doctrine: cap power gaps in matchmaking, show chest odds, and keep a deterministic path (shop, wild cards) to targeted upgrades.

**Model sketch:**

```text
per_level_win  source  chest_slot_fill(+1) if slots < 4
per_session    converter  chest_slot(-1) → cards_by_rarity(+), gold(+)        (unlock, once timers elapse)
per_session    converter  cards_X(-copies_L) + gold(-gold_L) → card_level_X(+1)   (gate: copies and gold affordable)
on_purchase    gems → skip timers / chests
```

---

## 3. Casual puzzle lineage to Royal Match: the continue economy

**Lineage.** Candy Crush Saga (King, 2012) set the mobile template: five lives that regenerate over time, a hard currency (gold bars) and boosters, with a level map as the content gate. Royal Match (Dream Games, 2021) refined it with a decoration meta, aggressive production values and an economy built around the **continue** moment.

**Currency map (Royal Match, as publicly observed; verify):**

| Currency | Kind | Role |
|---|---|---|
| Coins | soft (and the main IAP currency) | Earned in small amounts per win; bought in packs; spent mainly on continues (+moves) and boosters |
| Lives | energy | Lost on failure only; regenerate over time; unlimited-lives windows as rewards |
| Stars | xp-like (spent) | One per level won; spent on castle/area decoration tasks |
| Boosters (pre-level and in-level) | material | Earned from streaks, chests, events; bought in bundles |

**Core economic loop.** Play level → win (coins, star, streak progress) or fail (lose a life; offered +moves for coins) → stars build the castle area by area (meta progress and story beats) → chests at milestones grant boosters and coins.

**Signature devices:**
- **The continue is the purchase.** Fail screens show how close the player was and offer extra moves for coins, with the price typically rising on repeated continues within the same level (verify current values). Monetization sits exactly where frustration and near-success meet — the strongest and most ethically sensitive point in casual design.
- **Win-streak rewards.** Consecutive wins grant starting boosters; losing the streak loses them. It makes continues more valuable (they protect the streak) and gives skilled players a bonus.
- **Lives that only failures consume.** Skilled play is never gated; the energy system only paces struggling players.
- **One spendable currency for most things.** Coins act as both the earned and purchased currency, keeping the HUD simple; the earn rate is small relative to continue prices, so coins earned in play feel like a cushion rather than an income.
- **Dense live-ops layer**: team features, leaderboards, short competitive events and a pass sit on top of the level map, each paying out boosters and coins.

**Lessons to borrow:** price the continue relative to the effort at risk; reward streaks; decorate rather than just count levels; keep the currency surface minimal.

**Doctrine limits:** near-miss continue offers must be honest (no rigged "one move short" boards to sell continues); escalating continue prices need visible prices before tapping; cap the number of continue prompts per level; never show continue offers to accounts flagged as minors with aggressive framing.

**Model sketch:** Lantern Lane in `sources-sinks-balancing.md` §7 is a deliberately simplified version of this structure (coins, continues at 300, boosters, stars → decor).

---

## 4. Coin Master: inflationary coins, escalating sinks

**Snapshot.** Moon Active; social casual game built on a slot-machine core. Numbers below are illustrative; verify current values.

**Currency map:**

| Currency | Kind | Role |
|---|---|---|
| Spins | energy | Regenerate a handful per hour up to a cap; gifted by friends; bought in packs |
| Coins | soft | Produced in large quantities by spins, raids and events; spent on village building |
| Village items | progression sink | Each village has a set of items to build/upgrade; each new village is far more expensive |
| Cards (sets, albums) | material/collection | From chests bought with coins and from events; sets complete for rewards; tradable with friends |
| Shields | defence item | Block attacks |
| Pets (food, XP) | material | Boost raids/attacks |

**Core economic loop.** Spin → coins, attacks, raids, shields, spins → spend coins to build village → complete village → next village (higher prices, new card set) → events reward spins and boosts.

**Signature devices:**
- **Escalating village prices as the master sink.** Coins inflate massively by design; each new village's prices rise to match, so the number on the counter keeps growing without breaking progression.
- **Coin-to-collection conversion.** Chests bought with coins grant cards, turning inflationary currency into collection progress — an elastic sink that never saturates while sets are incomplete.
- **Bet multiplier on energy.** Spending several spins per pull for multiplied rewards lets engaged players accelerate (and deplete energy faster), which creates demand for spin packs during events.
- **Social attrition.** Attacks and raids take coins from friends or strangers; revenge and shields create social loops and virality (invites for spins).

**Lessons to borrow:** pair an inflationary currency with an escalating sink; convert surplus soft currency into collection progress; use friend gifting for energy.

**Doctrine limits:** the slot-machine presentation is simulated gambling optics, which affects age ratings in some markets (Australia's classification rules, see `gacha-and-loot.md` §11); bet multipliers must show the energy cost clearly; raids should cap losses so victims are not ruined.

**Model sketch:**

```text
per_session (or per_minute)  converter  spins(-bet) → coins(+X·bet) with probability table (model as several probabilistic sources)
per_session  sink/gate       coins(-price_village_k_item_j) → village_progress(+1)   (prices × growth per village)
per_session  converter       coins(-chest_price) → cards(+n)                          (elastic sink)
daily        source          spins(+gifts)
```

---

## 5. Monopoly Go: energy multipliers and stacked events

**Snapshot.** Scopely, 2023; board-game-inspired social casual game. One of the fastest-grossing mobile launches of its period (reported). Verify current systems; event names and rules rotate.

**Currency map:**

| Currency | Kind | Role |
|---|---|---|
| Dice rolls | energy | Regenerate over time up to a cap; the universal reward of events |
| Cash | soft | From landing on tiles, heists, shutdowns; spent building landmarks on each board |
| Net worth | xp-like | Accumulates from building; drives board progression |
| Stickers (albums, sets) | collection | From packs earned in events and purchases; season albums; trading with friends |
| Shields | defence | Block shutdowns |
| Event tokens / points | event | Each concurrent event has its own milestone track |

**Core economic loop.** Roll dice (choose a multiplier) → move, earn cash/tokens, trigger mini-games → build landmarks with cash → finish board → next board (higher prices) → event milestones pay dice, cash and sticker packs → more rolling.

**Signature devices:**
- **Roll multiplier.** Players choose how many dice to spend per roll for multiplied outcomes. During events, high multipliers convert dice into milestone progress faster, so demand for dice spikes when events are rich — the economy's elastic sink for energy.
- **Stacked concurrent events.** Several events run at once (tournaments, a milestone event, partner co-op events, a daily quick-win list), all paying dice. Dice → event progress → dice forms a self-reinforcing loop that the designers throttle through milestone spacing.
- **Season sticker albums with trading.** Collection completion is the long-term goal; trading duplicates with friends is social glue, and special high-rarity stickers can be traded only in specific windows.
- **Board pricing ladder.** Each board's landmarks cost more cash than the previous board's, absorbing the growth in cash income — the same escalating-sink pattern as Coin Master.

**Lessons to borrow:** energy multipliers to let engaged players accelerate; concurrent event tracks with shared reward currency; collection seasons with trading.

**Doctrine limits:** dense concurrent events can feel like obligations; milestone pacing must not require purchases to finish on time for median engaged players; multiplier UI must show dice spent per roll before rolling; album completion must not hinge on extremely rare stickers obtainable mainly through paid packs (kompu-adjacent risk; see `gacha-and-loot.md` §7.1).

---

## 6. Hay Day: production chains, storage and a capped market

**Snapshot.** Supercell, 2012; farming and trading sim, still operating more than a decade later.

**Currency map:**

| Currency | Kind | Role |
|---|---|---|
| Coins | soft | From orders, sales to other players; spent on buildings, animals, decorations, expansions |
| Diamonds | hard | Speed-ups, missing items, special purchases |
| XP | xp | Levels unlock buildings and products |
| Crops, animal goods, processed goods | material | Inputs and outputs of production chains |
| Barn and silo capacity | capacity | Storage caps for goods and crops |
| Expansion and upgrade materials (tools such as bolts, planks, nails…) | material | Drop at controlled rates; needed to expand land and upgrade storage |

**Core economic loop.** Plant/produce (timers) → fill orders (truck, boat) or sell to players → coins and XP → buy buildings and expansions → longer, more valuable chains → storage pressure → upgrade storage with special materials.

**Signature devices:**
- **Storage caps as the pacing device.** Barns and silos fill fast; players must sell, fulfil orders or upgrade capacity. Capacity upgrades require special materials that drop at a controlled rate — so the cap itself becomes a long-term sink and a reason to trade.
- **Player market with price limits.** Players sell goods from a roadside shop at prices they choose within a range tied to each item's value. The cap prevents runaway prices, real-money trading leverage and exploitation of new players, while still letting supply and demand operate.
- **Seed reinvestment.** Crops yield more than they consume when replanted, a gentle positive-feedback engine with time as the limit.
- **Orders as a demand sink.** Order boards absorb produced goods at known prices, giving every chain a guaranteed outlet.
- **Cooperative social layer** (neighbourhoods, derbies) adds shared goals without zero-sum stealing.

**Lessons to borrow:** use storage caps plus controlled special-material drops to pace a long-lived economy; let players trade within price bands; give every produced good a guaranteed sink (orders).

**Doctrine limits:** timers and storage pressure can drift into "pay to remove friction we added"; keep diamond speed-ups optional and fairly priced (concave curve, `currency-architecture.md` §4.3); keep special-material drops visible with a deterministic exchange route.

**Model sketch:**

```text
per_session  converter  wheat(-1) → wheat(+2)                             (replant, gated by field count and timers)
per_session  converter  wheat(-3) → feed(+1);  feed(-1) → eggs(+1)          (production chain)
per_session  sink       goods(-order_basket) → coins(+), xp(+)             (orders)
per_session  source     probability 0.1 → expansion_material(+1)           (controlled drops)
per_session  gate       expansion_material(-k) → barn_cap(+25)             (resource cap upgrade)
resources: barn_goods {"cap": 75}  — overflow blocked, not lost
```

---

## 7. Genshin Impact: transparent gacha at scale

**Snapshot.** miHoYo/HoYoverse, 2020; open-world action RPG with character and weapon gacha, cross-platform, with a large content cadence. Its banner rules became a genre reference. Values quoted below are those widely published in-game and by the community; verify current details.

**Currency map:**

| Currency | Kind | Role |
|---|---|---|
| Primogems | hard | Earned through exploration, quests, events, dailies; converted to pull tickets |
| Genesis Crystals | premium | Purchase-only; convert to Primogems; first purchase of each pack tier has historically granted a bonus |
| Fates (pull tickets, two types) | material | One per pull; limited-banner and standard-banner types |
| Mora | soft | Levelling, talents, crafting |
| Resin | energy | Regenerating stamina spent on reward claims from domains and bosses (not on exploration) |
| Pull byproducts (two exchange currencies) | material | Earned from every pull and duplicates; spent in an exchange shop for tickets and items |
| Character/weapon materials | material | Ascension and talent inputs, many types |

**Signature devices:**
- **Disclosed pity with a 50/50 guarantee.** The top-tier base rate, consolidated rate, hard pity, featured share and guarantee are published; pity carries across limited banners. Players plan pulls around it. (Reference maths: `gacha-and-loot.md` §3.2, config A.)
- **Paid/free split.** Purchase-only currency converts to the earnable hard currency, which keeps the paid balance trackable (refunds, accounting, regulation) while giving players one spendable unit.
- **Exchange shop from pull byproducts.** Every pull yields a byproduct currency, so even "bad" pulls progress toward guaranteed tickets and items — a built-in spark-like floor.
- **Monthly card and pass as best value.** A low-price monthly card that pays daily, and a season pass with a premium track, are the highest value-per-dollar products and convert many low spenders into regular payers.
- **Resin paces reward claims, not play.** Exploration remains free; stamina gates only the farmable reward loop.

**Lessons to borrow:** publish full banner rules; carry pity over; give every pull a byproduct that accumulates to something certain; split paid and free currency in the backend; make the cheapest recurring product the best value.

**Criticisms and doctrine limits:** duplicate-based power upgrades (constellations) make "complete" characters very expensive; stamina limits on progression materials are a frequent complaint; and the US FTC announced a $20 million settlement with the publisher (Cognosphere, HoYoverse) in January 2025 over loot-box odds and cost presentation and sales to minors, including a bar on loot-box sales to under-16s without a parent's affirmative express consent (checked against the [FTC press release](https://www.ftc.gov/news-events/news/press-releases/2025/01/genshin-impact-game-developer-will-be-banned-selling-lootboxes-teens-under-16-without-parental); see `gacha-and-loot.md` §14). The doctrine response: show expected and worst-case real-money costs, keep most function in the first copy, and age-gate paid randomness.

---

## 8. Idle and incremental games: exponential costs and prestige

**Snapshot.** Cookie Clicker (Orteil, 2013, browser) popularised the modern idle loop; AdVenture Capitalist (Hyper Hippo, 2014), Egg, Inc. (Auxbrain) and Idle Miner Tycoon (Kolibri Games) took it to mobile. Anthony Pecorella's "The Math of Idle Games" series on the Kongregate developer blog (2016) is the standard practitioner reference for the maths summarised here.

**Currency map (typical):** one primary soft currency (cash), a prestige currency (angels, souls, prestige points), a hard currency (gold, gems) and sometimes boosts (time warps, multipliers).

**The maths:**

```
generator cost after owning n:      c_n = c_0 × r^n          (r typically about 1.07–1.15)
cost to buy k more:                 c_0 × r^n × (r^k − 1) / (r − 1)
max affordable with cash C:         k = floor( log_r( 1 + C (r − 1) / (c_0 r^n) ) )
income from n generators:           n × base_rate × multipliers   (milestones: ×2 at 25, 50, 100, … owned)
prestige currency (one common form):P = floor( a × sqrt(lifetime_earnings / scale) )   → 4× lifetime earnings = 2× prestige
```

**Worked example (hypothetical generator: c_0 = 4, r = 1.07, 1 cash/s per generator):**

| Owned n | Next generator cost | Seconds to afford next (no milestones) | With ×2 milestones at 25/50/100/200 |
|---|---|---|---|
| 10 | 7.9 | 0.8 | 0.8 |
| 50 | 117.8 | 2.4 | 0.6 |
| 100 | 3,471 | 34.7 | 4.3 |
| 150 | 102,240 | 681.6 (11 min) | 85.2 |
| 200 | 3.0 million | 15,059 (4.2 h) | 941 (16 min) |

(At n = 50, buying 10 more costs 1,628; with 10,000 cash you can afford 28.) Exponential costs always outrun polynomial income: the **wall** arrives by design. Milestones push it back; **prestige** resets progress in exchange for a permanent multiplier and makes the next run faster — a voluntary reset sink that converts accumulated wealth into long-term power.

**Signature devices:** offline earnings (with a cap to bring players back), managers/automation (removes the tapping chore as a reward), ad boosts (×2 income for a period — the most natural rewarded placement in mobile), premium time warps (instant hours of income), and event worlds with separate economies (isolation, `currency-architecture.md` §10).

**Lessons to borrow:** use explicit cost growth ratios and milestone multipliers; place the first prestige after the first real wall but before boredom; make ad boosts generous and capped; isolate event economies.

**Doctrine limits:** time-warp pricing must be fair against the time it replaces; offline caps should be generous enough not to punish normal absence; avoid locking prestige multipliers behind purchases.

---

## 9. Pass systems: selling a reward track

**Lineage.** Dota 2's Compendium (2013) is commonly cited as the origin of the battle pass; Fortnite (from late 2017) made the season pass mainstream, including the well-known pattern where the premium track returns more premium currency than the pass costs (reported for many seasons). Mobile followed: Clash Royale's Pass Royale, Brawl Stars' Brawl Pass, Royal Match's Royal Pass and countless event passes in casual games.

**Patterns:**

| Pattern | What it does | Example family |
|---|---|---|
| Free + premium tracks | Non-payers progress; payers unlock richer rewards retroactively | Nearly all passes |
| Premium-currency rebate | Pass "pays for itself" for players who finish | Fortnite-style |
| Short event passes (1–2 weeks) | Monetise each event; casual-friendly length | Casual puzzle and merge games |
| Tier skips / premium+ | Sell catch-up or a head start | Mid-core passes |
| Pass as subscription | Auto-renewing monthly pass | Some mobile titles |
| Mission-based progress | Daily/weekly missions feed pass points | Most passes |

**Economics (see `pricing-and-offers.md` §11):** compute the full-completion value ratio (house band 5–10×) and the realised ratio for median buyers (≥ 3×); design completion so median engaged players finish with 15–25% of the season to spare; place the most-wanted premium rewards by mid-track.

**Lessons:** passes align revenue with engagement and are the default transparent alternative to paid randomness; the rebate pattern trades revenue per player for loyalty and conversion; short event passes suit casual cadences.

**Doctrine limits:** no hidden tiers; missions never require spending; median engaged players must finish without buying skips; unclaimed rewards are delivered at season end.

---

## 10. Cross-case comparison

| Game/pattern | Spendable currencies | Pacing device | Master sink | Signature device | Borrow | Avoid |
|---|---|---|---|---|---|---|
| Clash Royale (classic) | Gold, gems, card copies | Chest slots + timers | Card upgrades (copies + gold) | Duplicates as upgrade currency | Useful duplicates; reward slots | Power gaps in ranked PvP |
| Royal Match | Coins (+ boosters) | Lives (failure only) | Continues (+moves) | Continue at near-miss; streaks | Minimal currency surface; streak rewards | Manipulative near-miss framing |
| Coin Master | Coins, spins | Spin regen | Escalating villages; coin chests | Inflation matched by escalating sinks | Coin-to-collection conversion | Gambling optics; harsh raids |
| Monopoly Go | Cash, dice | Dice regen | Escalating boards; dice multipliers in events | Multiplier + stacked events | Shared event reward currency | Event obligation overload |
| Hay Day | Coins, diamonds, goods | Timers + storage caps | Capacity upgrades; expansions | Capped player market | Price bands; guaranteed order sinks | Friction-for-sale timers |
| Genshin Impact | Primogems/crystals, mora, resin | Resin (reward claims) | Pulls; levelling materials | Disclosed pity + byproduct exchange | Full disclosure; carry-over pity | Expensive duplicate power |
| Idle games | Cash, prestige, gems | Exponential costs | Generators; prestige resets | Prestige multiplier | Explicit growth ratios; ad boosts | Unfair time-warp pricing |
| Pass systems | Pass points | Season length | Premium track | Retroactive reward track | Value-ratio discipline | Hidden tiers; skip-or-fail pacing |

**Recurring truths across the cases:**
1. Successful economies have **one master sink** that scales with progress (upgrades, villages, boards, capacity, generators).
2. Inflation is fine if the master sink **escalates at the same rate**; it is fatal when prices are flat.
3. Energy is most accepted when it gates **failure** (lives) or **reward claims** (resin) rather than all play.
4. Collection systems are the best **elastic sink** — until they rely on paid rarity for completion.
5. Every long-lived economy found a **deterministic path** (shops, exchanges, selectors, wild cards) to soften randomness.

---

## 11. Transplanting patterns: the analogy method

Use the `analogy-engine` method: name the source pattern, abstract it to its ontology structure, check that the target game has the same structural preconditions, then adapt.

| Source pattern | Abstract structure | Preconditions in target | Example transplant |
|---|---|---|---|
| Coin Master coin chests | Elastic sink converting surplus soft → collection progress | A surplus currency and a collection meta | Match-3: surplus coins buy decoration "theme packs" whose contents are shown (transparent) |
| Hay Day price bands | Player market with price floor/ceiling tied to reference value | Tradable goods; social layer | Merge game: trade merge items with friends within ±50% of reference value |
| Clash Royale duplicates | Duplicates → upgrade input | Random or repeated rewards of the same item | Roguelite meta: duplicate relics upgrade the relic instead of being discarded |
| Monopoly Go multiplier | Optional energy multiplier for accelerated outcomes | Energy-gated actions with scalable rewards | Idle/merge: "spend 3 energy for 3× merge rewards" during events, with clear cost display |
| Genshin byproduct exchange | Every chance action yields a certain currency toward a guaranteed item | Any chance-based reward | Chest system: every chest yields keys; 50 keys = chosen item |
| Royal Match streaks | Consecutive success grants a starting advantage | Discrete attempts with win/lose | Runner: streak of 3 completed runs grants a starting shield |
| Idle prestige | Voluntary reset for permanent multiplier | Exponential progression with walls | Tycoon sim: "sell the company" for a permanent management bonus |
| Pass rebate | Track returns more premium currency than cost | Premium currency and a season | Casual puzzle: pass returns 120% of its gem value for players who finish |

**Transplant check (all must be yes):** the structural preconditions exist; the pattern serves the target's pillars; it does not add a currency that fails the one-job test; it survives the doctrine-8 review; and the sim shows it does not break hoard or starvation targets.

---

## 12. Volatile facts (as of Oct 2026 — verify before relying)

- **Market context**: Sensor Tower's H1 2026 analysis (as summarised by Mobilegamer.biz) reported global mobile game IAP of about $40B in H1 2026, down 2% year on year, with downloads down 12%; the same digest highlighted a Hay Day comeback, and hybrid-casual spending grew 17.1% in 2025 — [Mobilegamer.biz data digest](https://mobilegamer.biz/data-digest-sensor-towers-h1-analysis-hay-days-comeback-julys-top-games-big-krafton-numbers-and-more/). Q1 2026 grossing leaders were reported as Last War, Honor of Kings and Whiteout Survival — same source.
- **Genshin Impact banner figures** (0.6% base, 1.6% consolidated, 90-pull guarantee for top-tier characters) are those shown on the in-game details page; soft-pity shape is community-measured — see `genre-playbooks` `references/rpg-gacha.md` §0.1. Check the current details page before quoting.
- **Live-game systems change.** Clash Royale, Royal Match, Coin Master and Monopoly Go update their reward systems, events and prices frequently; every structural description above is a pattern summary, not a current specification. Re-check in the live game (or with a fresh `deconstruct` run) before using any as a requirement.
- **FTC action involving Genshin Impact's publisher (Jan 2025)** — checked on 2026-10-20 against the FTC's own press release (a $20 million penalty plus conduct terms; a proposed order that needed court approval); details and sources in `gacha-and-loot.md` §14.
