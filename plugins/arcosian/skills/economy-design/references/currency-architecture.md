# Currency Architecture

A game's currencies are its units of account: they decide what the player can measure, save, compare and trade off, and therefore which decisions exist at all. This file is the studio's reference for choosing how many currencies a game has, what job each one does (soft, hard, premium, energy, event, XP, material), how they convert into one another without arbitrage, how to name and present them honestly, and how to control inflation, caps, hoarding and regional pricing. Every rule here maps to the `contract.json → economy.currencies[]` fields (`id`, `kind`, `sources`, `sinks`, `cap`) and to the `resources[]` and `nodes[]` of an economy model that `economy_sim.py` can run. Read it before adding any new currency, before writing the shop, and whenever balances drift.

## Contents

1. [The one-job rule](#1-the-one-job-rule)
2. [Currency kinds in the ontology](#2-currency-kinds-in-the-ontology)
3. [Single, dual and multi-currency architectures](#3-single-dual-and-multi-currency-architectures)
4. [Conversion rates and guards](#4-conversion-rates-and-guards)
5. [Naming, presentation and psychology](#5-naming-presentation-and-psychology)
6. [Inflation and deflation](#6-inflation-and-deflation)
7. [Caps and storage](#7-caps-and-storage)
8. [Hoarding](#8-hoarding)
9. [Premium and hard currency specifics](#9-premium-and-hard-currency-specifics)
10. [Event currencies](#10-event-currencies)
11. [Energy and stamina](#11-energy-and-stamina)
12. [Materials, shards and collection currencies](#12-materials-shards-and-collection-currencies)
13. [Regional pricing and currency amounts](#13-regional-pricing-and-currency-amounts)
14. [Currency spec template and review checklist](#14-currency-spec-template-and-review-checklist)
15. [Volatile facts](#15-volatile-facts-as-of-oct-2026--verify-before-relying)

---

## 1. The one-job rule

A currency earns its place only if it does a job no other currency can do. Every extra currency costs UI space, onboarding time, a new balance to tune, a new exploit surface and a new line on the odds and price disclosures. The jobs are:

| Job | What it controls | Typical kind | Failure if missing | Failure if duplicated |
|---|---|---|---|---|
| **Pace** | How fast the player progresses through the main loop | soft | Progress feels flat or free | Two soft currencies doing the same thing confuse players |
| **Scarcity / premium** | Access to accelerators, cosmetics, gacha | hard / premium | No monetization surface | "Which gem do I spend?" paralysis |
| **Session gating** | How much can be played per sitting | energy | Binge-and-burn content consumption | Two timers compound into hostility |
| **Isolation** | Keeps a temporary economy from polluting the main one | event | Event rewards inflate the core economy | Players feel every event is a chore currency |
| **Mastery record** | Measures cumulative play, never spent | xp | No sense of long-term growth | Rarely duplicated; risk is XP that gets spent (then it is soft) |
| **Specificity** | Ties progress to a specific item, hero or building | material | Generic currency buys everything; no collection goals | Material bloat (30 shard types) |

**The test.** For each proposed currency, write: "Players earn X by \_\_\_, spend it on \_\_\_, and it exists because \_\_\_ would break if we used [existing currency] instead." If the last blank is weak, merge it.

**Complexity budget (house heuristics, verify per audience):**

| Audience | Currencies visible on the main HUD | Total spendable currencies at launch | Material types at launch |
|---|---|---|---|
| Hyper/hybrid-casual | 1 (2 max) | 1–2 | 0–3 |
| Casual puzzle (match-3, merge) | 2 (soft + lives or hard) | 2–4 | 0–5 (boosters count as materials) |
| Farming/sim/builder | 2–3 | 3–5 | 5–20 (production goods are materials) |
| Strategy/4X | 3–5 resource bars | 4–6 | 10–30 |
| Gacha RPG | 2–3 | 4–8 | 15–60 (shards, ascension mats, skill books) |
| Idle/incremental | 1–2 primary + 1 prestige | 3–4 | 0–10 |

Add currencies over time only through live-ops, one at a time, each with a tutorial moment.

---

## 2. Currency kinds in the ontology

The ontology enum is `soft | hard | premium | energy | event | xp | material` (`contract.json → economy.currencies[].kind`). Use the kinds precisely:

| Kind | Definition (house) | Earned in play? | Purchasable? | Typical sinks | Cap? | Examples (generic) |
|---|---|---|---|---|---|---|
| `soft` | Abundant, earned constantly, spent constantly; sets pace | Yes, every loop | Yes, as a top-up | Upgrades, continues, boosters, decoration, crafting fees | Usually uncapped; storage-capped in builders | Coins, gold, cash |
| `hard` | Scarce, earned slowly in play **and** purchasable | Yes, trickle | Yes, primary IAP unit | Speed-ups, gacha pulls, premium items, refills, soft top-ups | No | Gems, diamonds, crystals |
| `premium` | Purchase-only (or paid-only balance of a split currency) | No | Yes | Same as hard, sometimes exclusive items | No | "Paid gems" balance, paid-only stones |
| `energy` | Regenerating permission to play | Regen + gifts | Refills | Starting a level/run/action | Yes (regen cap; overfill allowed from gifts) | Lives, stamina, spins, dice rolls |
| `event` | Exists only during an event; isolated | Yes, during event | Sometimes (event packs) | Event shop, event milestones | Often; expires or converts at end | Tokens, tickets, event points |
| `xp` | Accumulated, never spent; drives levels | Yes | Indirectly (boost) | None (thresholds instead) | No | Player XP, account level, mastery points |
| `material` | Specific input to a specific upgrade or craft | Yes, drops | Bundled | Upgrades of a specific item; crafting | Storage caps | Shards, ore, planks, hero cards, boosters |

**Hard vs premium.** Most mobile games use one hard currency that is both earned and bought. Split it into a `hard` free balance plus a `premium` paid balance when (a) some items must be paid-only, (b) local law or accounting requires tracking unspent paid balances separately (see §9 and volatile facts), or (c) you need to refund or reverse purchases precisely. When split, always spend the free balance first unless the item is paid-only, and show the player both balances.

**Boosters are materials.** A pre-level booster (rocket, bomb, extra moves) is a material with a single sink. Model it as a resource with its own sources (rewards, packs) and a per-attempt sink, not as an item outside the economy.

---

## 3. Single, dual and multi-currency architectures

### 3.1 The three families

| Architecture | Shape | Strengths | Weaknesses | Good fits |
|---|---|---|---|---|
| **Single** | One currency does pace and monetization (IAP sells it directly) | Zero learning cost; every reward means something | Every price competes with progress; hard to protect premium value; inflation hits everything | Hyper-casual, arcade with skins, premium games with light IAP, idle games where the only "currency" is cash |
| **Dual** | Soft (pace) + hard (premium) | Clear mental model; premium protected from soft inflation; most common F2P pattern | Hard→soft exchange must be guarded; temptation to add a third "just for this feature" | Casual puzzle, merge, runner, card battlers, most hybrid-casual |
| **Multi** | Soft + hard + energy/event/materials, often 5–30 resources | Many independent levers; collection goals; segment-specific sinks | Onboarding cost; tuning combinatorics; UI clutter; exploit surface | Builders, farming, strategy, gacha RPG, MMO-lites |

### 3.2 Decision table

| Question | If yes | If no |
|---|---|---|
| Is the session under 3 minutes and the audience mass-market? | Single or dual; one HUD currency | Continue |
| Do you sell time-skips or randomized items? | Dual minimum, hard currency required | Single may suffice (direct-purchase skins, ad-free) |
| Do you need to throttle session count? | Add energy (lives/stamina) | Avoid energy; gate by content instead |
| Will live events run on a cadence with their own rewards? | Add an event currency that expires or converts | Reuse soft/hard rewards |
| Is collection a pillar (heroes, cards, decorations)? | Add materials/shards per collectible family | Avoid materials |
| Do production chains exist (farm → factory → order)? | Materials per good; storage caps | Avoid |

### 3.3 Worked layout: three archetypes

```
Casual puzzle (dual + energy + boosters)
  coins (soft)   ← level wins, daily rewards, ads     → continues (+moves), boosters, decor fees
  gems  (hard)   ← rare milestones, IAP               → coins top-up, lives refill, special boosters
  lives (energy) ← regen 1 per ~20–30 min, cap 5      → 1 per failed attempt (wins do not consume)
  stars (xp-like, spent) ← 1 per win                  → decoration tasks (meta progress)
  boosters (material)    ← streaks, chests, packs     → pre-level use

Builder / farm (multi)
  coins, diamonds, XP, ~10 crops, ~20 goods, 6 expansion materials, storage capacity (barn, silo)

Gacha RPG (multi)
  gold (soft), gems (hard, earned+bought), paid gems (premium), stamina (energy),
  pull tickets (material for gacha), shards per hero (material), ascension mats per element,
  event tokens (event), account XP (xp)
```

---

## 4. Conversion rates and guards

### 4.1 Direction rules

| Conversion | Allowed? | Rule |
|---|---|---|
| Premium/hard → soft | Yes | Sold in fixed packs; price per soft unit should be **worse** than earning it through play for engaged players and **better** than nothing for payers. Anchor: 1 hard unit ≈ N minutes of median play income. |
| Soft → hard | Almost never | Breaks scarcity and IAP. If used (e.g., a weekly exchange), cap it hard (small weekly limit) and price it so a full week of soft income buys at most a token amount of hard. |
| Hard → energy (refill) | Yes | Price a full refill below the cheapest IAP's hard-currency amount so first refills are affordable from free earnings. |
| Energy → anything | No | Energy is permission, not wealth. |
| Event → core | Only at event end, at a published rate, capped | Otherwise events become the best farm in the game. |
| Duplicates → material | Yes | Fixed rate by rarity; publish it. |
| Material → soft (selling) | Yes, at a steep discount | Prevents material hoards becoming dead weight; discount prevents arbitrage. |

### 4.2 Anchoring the exchange rate to time

The most robust anchor is **time**. Define the value of one hard-currency unit as the minutes of play it replaces for a median non-paying player.

```
soft_per_hour_median   = median soft income per hour of play (from the sim, by archetype)
hard_to_soft_rate      = soft units granted per hard unit in the shop
minutes_per_hard_unit  = 60 × hard_to_soft_rate / soft_per_hour_median
```

House starting point: one hard unit buys 2–10 minutes' worth of median soft income in early game. Payers get time, not power they could never earn.

### 4.3 Speed-up (time-skip) pricing

Builders and strategy games convert hard currency to time. Use a **concave** curve so long skips are cheaper per minute (otherwise nobody skips long timers, and short skips feel extortionate).

```
gems_to_skip(minutes) = ceil( k × minutes^a ),   0.5 ≤ a ≤ 0.85
example (k = 1.0, a = 0.7):   1 min → 1 gem;  60 min → 18 gems;  8 h (480 min) → 76 gems;  24 h → 163 gems
```

(Arithmetic: 60^0.7 ≈ 17.6; 480^0.7 ≈ 75.3; 1440^0.7 ≈ 162.5; each rounded up.) Make very short remainders free (e.g., under 5 minutes) to reduce frustration; many builders do this for low-level timers.

### 4.4 Guards (implement all of them)

1. **No arbitrage cycles.** For any cycle of conversions A → B → … → A, the product of rates must be **< 1** (strictly losing). Check automatically:

```text
# rates[a][b] = units of b received per unit of a (after fees, at best available pack)
# Arbitrage exists iff a cycle has product > 1  ⇔  negative cycle in weights w = -log(rate)
for each node v: dist[v] = 0
repeat |V|-1 times: for each edge (a,b): dist[b] = min(dist[b], dist[a] - log(rates[a][b]))
for each edge (a,b): if dist[a] - log(rates[a][b]) < dist[b] - 1e-9: report arbitrage via (a,b)
```

Run this in CI over the live shop config, including event shops and duplicate conversions. Rounding matters: test with integer rounding exactly as the client and server do it.

2. **Server authority.** Balances, conversions and prices live on the server (or are validated there) for anything purchasable. Client-side economies get edited by memory tools within days of launch for any game with real spend.
3. **Rate limits.** Daily/weekly caps on soft→hard, on ad-granted currency and on event-shop purchases of core resources.
4. **Floors and ceilings.** Dynamic prices (player markets, auctions) need price floors and ceilings or a tax per trade to stop wash trading and bot laundering.
5. **Idempotent transactions.** Each grant/spend has a transaction id; replays are no-ops. Duplicate-grant bugs are the most common economy incident after launch.
6. **Compensation discipline.** Outage compensation is a faucet. Log it as a source node, cap it, and include it in the sim.

---

## 5. Naming, presentation and psychology

### 5.1 Naming and visual tiering

- **Tier must be readable without text.** Soft = warm, common material (copper/gold coin, leaf); hard = cool, gem-like, rarer shape; energy = heart/bolt/dice; event = seasonal motif. Keep silhouettes distinct at 24 px.
- **Names should say what it is in the fiction and how valuable it is.** "Coins" and "Gems" are clichés because they work; invent names only when the fiction makes them obvious (e.g., "Seeds" in a garden game). Never give two currencies near-identical names or colours.
- **One icon, everywhere.** The same icon on HUD, shop, rewards, odds pages and receipts.
- **Number sizes.** Keep early balances in readable ranges (tens to thousands). Idle games inflate into millions and beyond by design: use suffix notation (K, M, B, T, then aa/ab or scientific) and test that every label fits at that length.

### 5.2 Psychology to understand (and the ethical limit)

| Effect | Summary (own words, with attribution) | Legitimate use | Line not to cross |
|---|---|---|---|
| **Decoupling / pain of paying** | Separating payment from consumption reduces the felt cost of spending (Prelec & Loewenstein, "The Red and the Black", 1998) | Buying a pack once and spending gems over many small choices is easier for players | Using intermediate currency to hide the real price of an item; leftover-currency pack sizes |
| **Mental accounting** | People treat money in different "accounts" differently (Thaler, 1985 and later work) | Event currencies feel like "house money" for experimentation | Exploiting it to push spending of real money |
| **Goal-gradient** | Effort rises as a goal gets closer (Hull 1932; Kivetz, Urminsky & Zheng 2006 on reward programmes) | Progress bars, near-complete albums, piggy banks | Artificially slowing the last steps to sell completion |
| **Endowment** | Owned things feel more valuable (Kahneman, Knetsch & Thaler 1990) | Trial items, free premium taste | Granting then removing items to sell them back |
| **Anchoring** | First numbers seen shape judgments of later ones (Tversky & Kahneman 1974) | Showing the best-value pack beside a mid pack | Fake "was" prices; anchors that were never real |

**House rules for presentation (doctrine 8):**
1. Show the real-money price on every IAP button (stores render localized prices; never replace them with currency icons).
2. For items priced in hard currency that was bought with money, show the approximate real-money equivalent somewhere reachable in one tap (at minimum on gacha and large purchases).
3. Size packs so common purchases do not systematically leave unusable remainders (see §9.2).
4. Never use more than one intermediate step between money and the item (money → gems → item is the maximum; money → gems → tokens → pulls is not acceptable).
5. Give minors the same or stricter presentation; no targeted offers to under-age accounts.

---

## 6. Inflation and deflation

### 6.1 Definitions

- **Inflation**: the purchasing power of a currency falls over a player's lifetime — rewards and balances grow faster than useful sinks, so prices become irrelevant and rewards stop motivating.
- **Deflation / starvation**: sinks outgrow sources; players cannot afford the next meaningful step and stall.
- In single-player-economy games (no trading), inflation is **per player**. In trading economies, it is also **global**, and bots and real-money trading (RMT) amplify it.

### 6.2 Causes and detectors

| Cause | Detector (telemetry or sim) | Fix |
|---|---|---|
| Rewards scale with level, sinks do not | Balance in days-of-income rises with player level | Scale sink prices on the same curve as rewards, or add level-scaled sinks |
| Unbounded generators (idle) | Income growth rate exceeds cost growth rate | Exponential costs with growth ≥ income growth; prestige resets |
| Event dumps | Balance spikes after each event and never returns | Event currencies with expiry; cap event payouts of core currencies |
| Compensation and promo codes | Spikes after incidents | Cap and log; prefer cosmetics or energy over soft currency |
| Ad rewards uncapped | Ad-heavy players are richest non-payers | Daily ad caps; fixed reward per view rather than "double everything" at late game |
| Converter arbitrage | Specific players with impossible balances | §4.4 cycle check; server authority |
| Trading with bots/RMT | Global price index rising; wealth concentration | Trade taxes, untradeable premium goods, bot detection |

### 6.3 Measuring purchasing power

Track a **basket index**: the hours of median play needed to afford a fixed basket of representative purchases at each player level.

```
basket_hours(level L) = Σ_i price_i(L) / soft_income_per_hour(L)
healthy: roughly flat or gently rising across L (each upgrade takes similar or slightly more time)
inflation: falling sharply (rewards outpace prices)  →  sinks too weak
starvation: rising sharply (prices outpace rewards)  →  wall; check if intended (monetization wall) and ethical
```

### 6.4 Controls, from mildest to harshest

1. Add attractive optional sinks (cosmetics, decoration, gambling-free upgrades of convenience).
2. Scale prices with progress (cost curves; see `progression-difficulty`).
3. Storage caps (§7).
4. Seasonal currencies and resets (event currencies expire; leagues reset).
5. Prestige / rebirth (voluntary resets with permanent multipliers; idle standard).
6. Upkeep/decay (maintenance costs; spoilage). Use rarely on mobile: absence should not be punished harshly.
7. Currency sunset/redenomination (replace an inflated currency with a new one at a published rate). Last resort; communicate early.

---

## 7. Caps and storage

Caps do three jobs: they **pace** (you must spend before you can earn more), they **create a sink** (capacity upgrades cost resources), and they **protect the economy** (bounded balances are easier to tune and to secure).

### 7.1 Sizing caps

```
cap = k × typical income between sessions
  energy:  cap = sessions_gap_hours × regen_per_hour  (players should rarely wake to a full bar more than once a day)
  storage: cap ≈ 1.5–3 × income per session for builders (forces a spend decision every session)
  soft currency: usually uncapped; use hoard targets instead (§8)
```

### 7.2 Overflow behaviour (pick one, document it)

| Behaviour | Feels | Use for |
|---|---|---|
| Lost silently | Punishing | Never |
| Lost with warning before collection | Acceptable | Production buildings (collect-or-lose) |
| Blocked (cannot collect until space) | Pacing pressure, clear | Storage-capped goods (barns) |
| Overfill allowed from gifts/purchases, regen stops at cap | Generous | Energy (bought refills above the cap must never be lost) |
| Routed to mailbox/inbox | Safe | Event rewards, compensation |
| Auto-converted at a published rate | Fair | Event leftovers, duplicate shards beyond max |

### 7.3 Capacity as a sink

Storage upgrades are among the best long-term sinks because they are needed by every player, scale naturally, and convert directly into quality of life. Builders often gate them on special **expansion materials** dropped at a controlled rate (so the cap upgrade itself becomes a pacing device). Keep the drop rate visible and add a deterministic route (e.g., a shop exchange) to avoid pure-luck walls.

### 7.4 Ethics of caps

Caps must be visible, explained once, and reachable in UI. A cap that silently eats a player's overnight income reads as theft (`design-theory` diagnostic E10). Never sell "cap anxiety" relief as the main monetization driver.

---

## 8. Hoarding

### 8.1 Healthy vs unhealthy hoarding

| Type | Signal | Verdict |
|---|---|---|
| **Saving for a known target** (banner, big upgrade) | Balance rises, then drops sharply at the target | Healthy; creates anticipation |
| **Nothing worth buying** | Balance rises steadily; sink participation falls | Unhealthy; sinks too weak or unappealing |
| **Fear of future scarcity** | Players refuse to spend because next content is unknown | Communicate roadmaps; make spending reversible early |
| **Power hoarding by payers** | Payer balances balloon after bundles | Bundles too generous in soft currency; shift to items or hard currency |

### 8.2 Measuring hoarding

```
hoard_days(player, t) = balance(t) / mean_daily_income(player, last 7 active days)
target (house default): p50 ≤ 2–3 days, p90 ≤ 7 days for soft currency in casual games
schema: economy-model targets.max_soft_currency_hoard_days
```

Mid-core and gacha games tolerate larger hard-currency hoards because saving for a banner is part of the design; set a separate target per currency.

### 8.3 Interventions

1. A new desirable sink (cosmetic line, decoration theme, collection set).
2. A limited-time shop that rotates (gives hoards a reason to move without raising base prices).
3. Prestige or seasonal reset with a reward proportional to what is invested (not to what is held).
4. Interest-free "spend-to-earn" mechanics (e.g., completing a decoration area grants hard currency).
5. Avoid confiscation, decay of balances, or "use it or lose it" pressure on purchased currency.

---

## 9. Premium and hard currency specifics

### 9.1 Free drip ("taste of premium")

Give every non-paying player enough hard currency to make **one meaningful hard-currency decision early** (e.g., the first refill or a cheap premium booster) and a slow, predictable trickle afterwards. House starting points (verify by sim and test):

| Genre | Free hard currency per active day (as % of the cheapest pack's hard amount) |
|---|---|
| Casual puzzle | 5–15% (milestones, area completion, events) |
| Builder/farm | 5–20% (achievements, mystery boxes, level-ups) |
| Gacha RPG | Substantial: free pulls per banner cycle is a published design target (see `gacha-and-loot.md`) |

### 9.2 Pack sizing and leftovers

- Price items in round amounts that **divide** the common pack sizes, or offer exact-amount "top-up" purchases.
- Avoid a structure where the item you want costs slightly more than the pack the player can afford (e.g., packs of 500, item at 600): consumer regulators have criticised leftover-currency designs (see volatile facts).
- Price 10-pull gacha bundles so that one mid-tier pack covers them, or show the shortfall in real money.

### 9.3 Paid vs free balances (accounting and law)

- Track **paid** and **free** hard currency separately in the backend even if you show one number. Reasons: refunds and chargebacks, revenue recognition (sold virtual currency is often recognised as revenue when consumed rather than when bought — ask your accountant), and jurisdictions that regulate unspent prepaid balances (verify with counsel; Japan is the usual example, see volatile facts).
- Spend order: free first for general items, paid-only for paid-exclusive items. Log both.

---

## 10. Event currencies

**Purpose:** isolate a temporary economy so events can be generous and exciting without inflating the core.

Design rules:
1. **Single event currency per event** (two only if one is premium-purchasable and must be separated).
2. **Earned through the event's verb** (play levels during the event, complete event tasks) — not purchasable directly unless as part of a bundle with a fixed cap.
3. **Shop or milestone track** with a visible full price list on day one. Total earnable by a median engaged player should cover the "headline" reward plus most mid-tier items; paying or highly engaged players clear the rest.
4. **End-of-event policy** published in advance: leftovers convert to soft currency at a fixed rate, roll into the next event, or expire. Expiry is acceptable for free event currency if clearly stated; never expire currency the player bought.
5. **Core payout cap**: total soft currency an event can inject ≤ N days of core income (house default: 1–3 days for casual). Hard currency injected by events must be in the sim.
6. **Calendar overlap**: two events running together must not stack payouts beyond the cap; model both as nodes with `condition` on the day range.

---

## 11. Energy and stamina

Energy is a regenerating permission to play. It paces content consumption, creates return triggers, and is a monetization surface (refills, unlimited-time passes). It is also the most resented mechanic when mis-tuned.

```
time_to_full = cap × regen_interval
design: time_to_full ≈ typical gap between sessions (casual: 2–4 h; overnight: 6–8 h)
lives model: lose 1 life only on failure; wins are free  ⇒  skilled play is never gated
spins/dice model: every action consumes; regen is the pacing dial; multipliers let players spend faster
```

| Parameter | Casual lives | Action stamina (RPG) | Spin/dice energy (social casino-like) |
|---|---|---|---|
| Cap | 5 | Grows with account level | Tens of units |
| Regen | 1 per 20–30 min | 1 per several minutes | A handful per hour |
| Consumed by | Failed attempts | Each stage/run | Each spin/roll × multiplier |
| Overfill | From gifts/purchases | From items | From rewards/gifts |
| Typical monetization | Refill, "unlimited lives for N minutes" | Refill packs, monthly cards | Packs; events that reward spending energy |

Rules: never gate the FTUE behind energy; give "unlimited lives" bursts as rewards; respect absence (energy fills, it does not decay); if energy multipliers exist, show the expected spend per action clearly.

---

## 12. Materials, shards and collection currencies

- **One material per upgrade family**, not per item, unless collection is the pillar (hero shards in gacha).
- **Duplicates → shards → targeted crafting** is the standard duplicate-protection loop (detail in `gacha-and-loot.md` §7).
- **Drop control**: materials that gate progression should have a **guaranteed minimum** per time unit (daily quest, shop exchange) so no player is stuck on pure luck.
- **Sell-back**: allow converting surplus materials to soft currency at a steep discount to avoid dead inventory.
- **Inventory caps** on materials double as a sink (capacity upgrades) in builders; avoid them in casual games.

---

## 13. Regional pricing and currency amounts

Principles (stable):
1. **Keep in-game amounts identical across regions; vary the real-money price.** Different amounts per region create fairness complaints, support confusion and cross-region gifting arbitrage.
2. **Use the store's price grid**, set a base storefront, and let the store generate local prices, then adjust markets where purchasing power differs sharply. Both stores support per-storefront pricing and automatic equalisation (see volatile facts).
3. **Purchasing-power reference.** Use a PPP index or a reference such as Valve's published regional pricing recommendations for Steam as a starting point for emerging markets, then test. Mobile store accounts are tied to a country and payment method, which limits (but does not remove) VPN arbitrage compared with PC.
4. **Taxes.** Many storefronts display tax-inclusive prices (VAT/GST), so the developer's net varies per country even at the "same" price.
5. **Ads-heavy regions.** Where IAP conversion is structurally low, lean on rewarded ads and low-price entry offers rather than cutting core prices to the floor (see `ad-economy.md`).
6. **Do not reveal regional differences in-game** (e.g., "price in other countries"), and do not change prices mid-offer.

---

## 14. Currency spec template and review checklist

Write one block per currency into `contract.json → economy.currencies[]` and mirror it in the economy model `resources[]`:

```json
{
  "id": "coins",
  "kind": "soft",
  "sources": ["level_win 40", "level_loss 10", "daily_chest 100", "rewarded_ad 40 (cap 10/day)", "area_complete bonus"],
  "sinks": ["continue +5 moves 300", "pre-level booster 200", "decor task 7 per star"],
  "cap": null
}
```

Model counterpart: `{"id": "coins", "initial": 300, "cap": null}` with one node per source and sink (see `sources-sinks-balancing.md` §6).

**Review checklist (run before every economy change):**

- [ ] Each currency passes the one-job test (§1); total count within the complexity budget.
- [ ] Every currency has at least one source and one sink in the contract and in the model.
- [ ] Conversion table written; cycle check finds no arbitrage, with real rounding.
- [ ] Hard currency has a free drip target; first meaningful hard-currency decision happens in session 1–3.
- [ ] Pack sizes divide common prices or exact top-ups exist; no leftover traps.
- [ ] Event currencies have a published end-of-event policy and a core payout cap.
- [ ] Energy: time-to-full matches the session gap; FTUE is not energy-gated; wins do not consume lives.
- [ ] Caps visible; overflow behaviour documented per resource.
- [ ] Hoard targets set per currency and checked in the sim (`targets.max_soft_currency_hoard_days`).
- [ ] Paid and free balances tracked separately server-side.
- [ ] Real-money prices visible on every IAP; real-money equivalents reachable for big hard-currency spends.
- [ ] Regional prices set via the store grid; identical in-game amounts everywhere.

---

## 15. Volatile facts (as of Oct 2026 — verify before relying)

- **Store commissions shape net revenue per pack.** In the EU, Apple's single business model (effective Oct 1, 2026) lists IAP commissions of 26% (15% for the Small Business Program and similar cases), 20%/10% for alternative payment providers and 15%/10% for link-outs, plus a 5% Core Technology Commission for apps distributed outside the App Store (checked 2026-10-20 against [Apple's newsroom post of Aug 18, 2026](https://www.apple.com/newsroom/2026/08/apple-announces-changes-for-apps-in-the-european-union/); a secondary summary is [iGeeksBlog](https://www.igeeksblog.com/eu-welcomes-apple-new-app-store-terms/)); see also the research summary of US rulings: [Justia: 9th Cir. No. 25-2935](https://law.justia.com/cases/federal/appellate-courts/ca9/25-2935/25-2935-2025-12-11.html). Use your actual programme rate in all "net per pack" calculations.
- **Google Play one-time products** now support multiple purchase options and offers (discounts, pre-orders) through Play Billing Library 8 and the `monetization.onetimeproducts` API — [Android Developers Blog, July 2025](https://android-developers.googleblog.com/2025/07/new-tools-to-help-drive-success-for-one-time-products.html). Relevant to how regional discounts and limited offers can be configured.
- **Apple IAP pricing is REST-only**: IAPs, subscriptions, metadata and pricing are managed through the App Store Connect REST API; the XML feed no longer supports them — [Apple Upcoming Requirements](https://developer.apple.com/news/upcoming-requirements/). Base-storefront pricing with automatically generated prices for other storefronts, the number of price points, and periodic tax/FX adjustments are background knowledge: verify in App Store Connect help before relying on them.
- **EU consumer-protection principles on virtual currencies** (background, not re-verified in the Oct 2026 research): the EU Consumer Protection Cooperation network published key principles on in-game virtual currencies in 2025 (price transparency in real money, no obscuring of costs, attention to minors). Check the European Commission consumer-protection pages before launch in the EU.
- **Japan, unspent prepaid balances** (background, not re-verified): Japan's Payment Services Act regulates prepaid payment instruments, which is why many Japanese titles split paid and free currency balances. Confirm obligations with Japanese counsel.
- **Steam regional pricing reference**: Valve publishes recommended regional prices in Steamworks documentation (background) — [Steamworks pricing docs](https://partner.steamgames.com/doc/store/pricing). Useful as a PPP sanity check for mobile storefront pricing.
