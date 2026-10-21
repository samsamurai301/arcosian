# 04 — Economy and Resource Mechanics

Economy mechanics are the rules by which resources enter the game (faucets), change form (converters), wait (pools, storage, queues), are gated (timers, caps, energy) and leave (sinks). They set the pace of progress, give choices weight, and are where most monetization attaches, which is why they need the most care: an economy that inflates kills goals, one that starves kills fun, and one tuned to extract spend kills trust. This file catalogues 21 economy and resource mechanics — currencies, generators and idle production, exponential upgrades, multipliers, automation, offline earnings, prestige, production chains, crafting, build queues, storage, converters, trading, markets, energy, lives, boosters, gold sinks, chests, upkeep and gathering — each with rules, formulas, tuning ranges, failure modes and ethical limits. For macro economy architecture and simulation workflow read the `economy-design` skill; for time-gating and session design read `references/08-time-energy-session-mechanics.md`; for offers and pricing read `references/12-monetization-linked-mechanics.md` and the `monetization` skill.

## Contents

1. Economy fundamentals: flows, the node vocabulary, core formulas
2. Index of mechanics
3. Currencies and production (entries 1–8)
4. Conversion, crafting and time (entries 9–12)
5. Exchange between players (entries 13–14)
6. Session gates and level consumables (entries 15–17)
7. Sinks, rewards and maintenance (entries 18–21)
8. Economy review checklist
9. Volatile facts

## 1. Economy fundamentals

**Node vocabulary.** This plugin uses the Machinations-style flow vocabulary (Joris Dormans and Ernest Adams, *Game Mechanics: Advanced Game Design*, 2012), which maps one-to-one onto `economy-model.schema.json` node kinds:

| Concept | Meaning | `economy-model` node `kind` | Examples |
|---|---|---|---|
| Source (faucet) | Creates resource from nothing | `source` | level rewards, generators, daily login |
| Sink (drain) | Destroys resource | `sink` | upgrade costs, repairs, taxes, consumables |
| Converter | Turns inputs into outputs | `converter` | crafting, merge, exchange, dust |
| Pool | Holds a resource (with optional cap) | `pool` | wallet, storage, inventory |
| Gate | Controls flow by condition or probability | `gate` | energy check, timers, drop tables, level win |

Each node has a `trigger` (`per_session`, `per_minute`, `per_level_attempt`, `per_level_win`, `per_level_loss`, `daily`, `weekly`, `on_purchase`, `on_ad`) and `inputs`/`outputs` per resource. Simulate any economy built from this file with `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/economy_sim.py --model .gamestudio/economy/<model>.json --runs 200 --json`.

**Core formulas.**

| Quantity | Formula | Use |
|---|---|---|
| Net daily flow | `Σ sources/day − Σ sinks/day` per archetype | Inflation check: should hover near 0 for engaged players over a week |
| Hoard days | `balance / typical_daily_spend_need` | Keep under the contract's `targets.max_soft_currency_hoard_days` (often 3–7) |
| Geometric cost | `cost_n = base × r^n` | Upgrades, buildings, levels |
| Bulk cost (k items from n) | `base × r^n × (r^k − 1) / (r − 1)` | "Buy ×10 / max" buttons |
| Max affordable | `k = floor(log_r(cash × (r − 1) / (base × r^n) + 1))` | "Buy max" |
| Payback time | `cost / Δincome` | Idle upgrade attractiveness; the player optimises this |
| Effective price | `real_money / (value in soft-currency terms)` | Compare offers consistently |

**Feedback loops.** Positive loops (wealth buys production which makes more wealth) create snowballing and must be counterweighted by geometric costs, caps or resets; negative loops (rubber banding, catch-up bonuses) stabilise but feel unfair if visible. Name every loop in the contract (`loops[]`) and decide which one is allowed to run away.

## 2. Index of mechanics

| # | Mechanic | ID | Node kinds | One-line essence | Typical home genres |
|---|---|---|---|---|---|
| 1 | Currency architecture | `currency-architecture` | pool | Which currencies exist and what each one means | all F2P |
| 2 | Generators and idle production | `idle-generators` | source | Owned producers create resources over time | idle, tycoon, builder |
| 3 | Exponential upgrade costs | `exponential-upgrades` | sink | Each level costs r× the last | idle, RPG, builder |
| 4 | Multipliers and milestones | `multiplier-milestones` | converter | Count thresholds multiply output | idle, tycoon |
| 5 | Automation (managers) | `automation-managers` | gate | Pay once to remove a repeated tap | idle |
| 6 | Offline earnings | `offline-earnings` | source | Production continues while away, capped | idle, builder |
| 7 | Prestige / rebirth | `prestige-rebirth` | converter + sink | Reset progress for a permanent multiplier | idle, roguelite |
| 8 | Production chains and bottlenecks | `production-bottlenecks` | converter + pool | Throughput is limited by the slowest stage | tycoon, farm |
| 9 | Crafting chains | `crafting-chains` | converter | Recipes turn materials into higher items | farm, survival, RPG |
| 10 | Build queues and timers | `build-queues` | gate | Work takes real time; slots run in parallel | builder, 4X, farm |
| 11 | Storage caps and inventory limits | `storage-caps` | pool | Capacity forces spending and sorting | builder, RPG, merge |
| 12 | Converters and exchange rates | `converters-exchange` | converter | Fixed-rate conversions with deliberate loss | CCG, RPG |
| 13 | Player trading | `player-trading` | converter | Direct swaps between players | collection, MMO-lite |
| 14 | Markets and auctions | `markets-auctions` | converter + sink | Player-priced exchange with fees | farm, MMO |
| 15 | Energy | `energy` | gate + pool | Regenerating stamina spent to play | merge, RPG, HO |
| 16 | Lives | `lives-pool` | gate + pool | Losing costs a life; lives regenerate | puzzle |
| 17 | Boosters | `boosters` | pool + sink | Consumables that help a level | puzzle, runner |
| 18 | Gold sinks | `gold-sinks` | sink | Meaningful ways to spend surplus | all |
| 19 | Chests | `chests` | gate + source | Containers opened by time, keys or currency | RPG, PvP, collection |
| 20 | Upkeep and decay | `upkeep-decay` | sink | Ownership costs over time | survival, farm, 4X |
| 21 | Gathering nodes and respawn | `gathering-nodes` | source + gate | World resources replenish on timers | farm, survival, location-based |

## 3. Currencies and production

### 04.01 Currency architecture — `currency-architecture`

- **ID:** `currency-architecture` · **Category:** economy / structure · **Player fantasy:** "I understand what I'm earning, what it buys and why it matters."
- **Core rules:**
  - Each currency has: `kind` (`soft|hard|premium|energy|event|xp|material` in the contract), `sources`, `sinks`, `cap`, `persistence` (permanent, seasonal, event-expiring), and `exchange` (what it converts to).
  - **Soft** currency: earned plentifully, spent on routine progress. **Hard/premium**: scarce, purchasable, spent on acceleration, convenience and premium content. **Event** currencies: time-limited; expire or convert at event end. **Materials**: specific to upgrade tracks (shards, ores).
  - Rule of thumb: every currency must have at least one meaningful sink the player wants and one source they understand; if two currencies always move together, merge them.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Number of player-facing currencies | 2–4 core (+ event and materials) | Clarity vs depth; > 6 overwhelms casual players |
| Free hard-currency income | 5–20 % of what an active payer spends | Lets non-payers taste premium sinks |
| Soft-to-hard exchange | one-way hard → soft only | Prevents grinding into premium |
| Event currency expiry | convert at a published rate or expire with warning | Fairness |
| Purchase pack bonus ladder | larger packs +10 % to +100 % more per dollar | Anchoring; keep honest and consistent |

- **Dynamics:** players form mental "exchange rates"; scarcity of hard currency makes spending decisions feel significant; event currencies focus attention.
- **Aesthetics (MDA):** Challenge (resource planning), Submission (accumulation).
- **Feedback and juice:** distinct icon, colour and sound per currency; fly-to-wallet animations; wallet counters that tick rather than jump.
- **Failure modes and exploits:** obfuscated pricing via many intermediate currencies (a dark pattern and, increasingly, a regulatory concern); dead currencies with no sinks; inflation from uncapped event rewards; exchange loops (A→B→A at profit).
- **Mobile fit:** wallet HUD in the top bar within safe areas; keep it to 2–3 visible counters.
- **Monetization hooks and ethical limit:** hard currency is the purchase vehicle. Show real-money equivalents on high-value spends where possible, never sell odd-sized packs designed to leave unusable remainders.
- **Implementation notes:** server-authoritative ledger for hard currency (append-only transactions with reason codes); soft currency can be client-side in offline games but log sources/sinks for analytics (`economy` events in the taxonomy).
- **Reference games:** Clash of Clans (gold, elixir, dark elixir, gems), Candy Crush Saga (gold bars), Genshin Impact (multiple currencies — an example of high complexity), Royal Match (coins and stars).
- **Combines well with:** every mechanic below; `converters-exchange`, `gold-sinks`, `energy`, battle passes (`references/12-monetization-linked-mechanics.md`).

### 04.02 Generators and idle production — `idle-generators`

- **ID:** `idle-generators` · **Category:** economy / source · **Player fantasy:** "I build an empire that earns while I watch — then while I sleep."
- **Core rules:**
  - Generator type `i` has `count_i`, `base_rate_i` (resource per second or per cycle), `cycle_time_i`, `cost_i(n)`, and multipliers.
  - Output per second: `income = Σ_i count_i × base_rate_i × mult_i / cycle_time_i` (or per cycle completion for cycle-based generators that need a tap unless automated).
  - New generator tiers unlock at thresholds and typically produce roughly an order of magnitude more than the previous tier at a proportionally higher cost.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Tier count | 6–12 generators per "world" | Content length per prestige |
| Tier output ratio | ~5–15× the previous tier | Pacing of unlock excitement |
| Tier cost ratio | slightly above output ratio | Keeps early tiers relevant briefly |
| Cycle time | 0.5 s – 1 h by tier | Slow tiers feel weighty; fast tiers feel lively |
| Click/tap contribution | dominant early, < 5 % late | Active-to-idle handoff |

- **Dynamics:** compounding growth; constant "what to buy next" decisions optimising payback time; number-go-up satisfaction.
- **Aesthetics (MDA):** Submission, Challenge (optimisation), Fantasy (tycoon).
- **Feedback and juice:** coins arcing off generators, counters with suffix notation (K, M, B, T, aa…), progress bars per cycle, "affordable" glows.
- **Failure modes and exploits:** walls where payback time explodes (insert milestones, new tiers or prestige); number formatting overflow (use big-number types or log-space floats); clock manipulation for offline gains (see `offline-earnings`).
- **Mobile fit:** perfect for short check-ins; one hand; low performance cost.
- **Monetization hooks and ethical limit:** permanent multipliers, time warps, ad-for-2× boosts. Keep the free curve progressing — design walls as prestige prompts, not paywalls.
- **Implementation notes:** large numbers — store as `(mantissa, exponent)` or `double` with log formatting; compute income analytically per frame (no per-generator objects ticking).
- **Reference games:** AdVenture Capitalist, Cookie Clicker, Idle Miner Tycoon, Egg, Inc.
- **Combines well with:** `exponential-upgrades`, `multiplier-milestones`, `automation-managers`, `offline-earnings`, `prestige-rebirth`.

### 04.03 Exponential upgrade costs — `exponential-upgrades`

- **ID:** `exponential-upgrades` · **Category:** economy / sink · **Player fantasy:** "Every level is a bigger achievement — and I can always reach the next one."
- **Core rules:**
  - Level `n` costs `cost_n = base × r^n`; benefit grows linearly or polynomially. Because costs grow faster than benefits, each purchase has diminishing returns, which forces diversification across upgrade tracks and eventually a reset or new content.
  - Common growth rates (summarised from Anthony Pecorella, "The Math of Idle Games", Kongregate blog, 2016): idle building costs typically use `r` between about 1.07 and 1.15 (Cookie Clicker buildings use 1.15).
  - RPG/levelling variants use polynomial costs `cost_n = a × n^p` (p ≈ 1.5–3) which grow gentler than geometric at high n.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Growth rate r (geometric) | 1.05–1.20 | Higher = faster walls, more resets |
| Polynomial exponent p | 1.5–3.0 | Gentler late curve for long-lived RPG tracks |
| Base cost ratio between tracks | 10× between tiers | Track identity |
| Benefit per level | +flat or +% | % benefits compound; cap or use with lower r |
| "Buy max" support | on | Respect for player time at large n |

- **Dynamics:** payback-time optimisation; switching between tracks as each becomes efficient; periodic walls that set up prestige or new content.
- **Aesthetics (MDA):** Challenge (optimisation), Submission.
- **Feedback and juice:** level-up flash, "next level in X min" estimates, best-value highlight (the plugin can compute payback and mark the best option).
- **Failure modes and exploits:** benefits that also grow geometrically (runaway); walls with no escape; precision errors at large exponents.
- **Mobile fit:** neutral; works with quick check-ins.
- **Monetization hooks and ethical limit:** paid multipliers shift the curve; never sell "levels" in competitive PvP without a cap.
- **Implementation notes:** use `progression_calc.py curve --formula exp --levels N --base B --growth G --json` to tabulate; simulate time-to-level with `progression_calc.py time-to-level`.

```text
cost(n) = BASE * R**n
bulk_cost(n, k) = BASE * R**n * (R**k - 1) / (R - 1)
max_affordable(n, cash) = floor(log(cash * (R - 1) / (BASE * R**n) + 1, R))
```

- **Reference games:** AdVenture Capitalist, Cookie Clicker, Tap Titans 2, Clash of Clans (building upgrade costs, polynomial-like in time and resource).
- **Combines well with:** `idle-generators`, `multiplier-milestones`, `prestige-rebirth`, damage scaling (`references/02-combat-action.md`).

### 04.04 Multipliers and milestones — `multiplier-milestones`

- **ID:** `multiplier-milestones` · **Category:** economy / converter (rate modifier) · **Player fantasy:** "Hitting that milestone doubled everything — I can feel the jump."
- **Core rules:**
  - Owning `count_i ≥ threshold_j` of generator `i` multiplies its output (×2, ×3) or speed (cycle time halved). Thresholds commonly at 10, 25, 50, 100, 200… Global multipliers come from upgrades, prestige, events, ads.
  - Multipliers apply multiplicatively across categories (`total = Π categories`), additively within a category (`Σ sources`), which keeps growth controllable.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Milestone thresholds | 10/25/50/100/200/300/400 | Medium-term goals |
| Milestone reward | ×2–×3 output or ×2 speed | Size of the "jump" |
| All-generator milestone | when every type reaches k | Encourages balanced buying |
| Ad/temporary boost | ×2 for 1–4 h | Session hooks |
| Category structure | 3–5 multiplicative buckets | Prevents runaway stacking |

- **Dynamics:** goal-setting (saving to hit a threshold), spikes that break walls created by exponential costs; balanced vs focused investment strategies.
- **Aesthetics (MDA):** Challenge, Submission, Sensation (jump moments).
- **Feedback and juice:** progress-to-milestone bars, big multiplier flash and sound, income number visibly jumps.
- **Failure modes and exploits:** additive-everything (multipliers become negligible late) or multiplicative-everything (runaway); milestones that can be skipped by buy-max without notice (always celebrate).
- **Mobile fit:** perfect; milestones give reasons to open the app.
- **Monetization hooks and ethical limit:** permanent ×2/×3 purchases (classic idle IAP), timed boosts via rewarded ads; avoid stacking dozens of paid multipliers that make free play feel pointless.
- **Implementation notes:** compute `mult_i = milestone_mult(count_i) × Π global_buckets` only when counts or buckets change; cache.

```text
MILESTONES = [(25, 2), (50, 2), (100, 2), (200, 3), (300, 3), (400, 3)]   # (count, factor)
milestone_mult(n) = product(f for (c, f) in MILESTONES if n >= c)
global_mult = product(1 + sum(bonuses in bucket) for bucket in [upgrades, prestige, events, ads])
income_i = count_i * base_i * milestone_mult(count_i) * global_mult / cycle_i
```
- **Reference games:** AdVenture Capitalist (unlock milestones), Idle Miner Tycoon, Egg, Inc. (research multipliers).
- **Combines well with:** `idle-generators`, `exponential-upgrades`, `prestige-rebirth`, rewarded ads (`references/12-monetization-linked-mechanics.md`).

### 04.05 Automation (managers) — `automation-managers`

- **ID:** `automation-managers` · **Category:** economy / gate removal · **Player fantasy:** "I hired someone to do the tapping — now I manage, not labour."
- **Core rules:**
  - Cycle-based generators require a tap to collect each cycle. Buying a manager/automation for that generator makes it collect automatically (and enables offline production).
  - Managers may add effects (cost reduction, speed, output) and can be swapped or upgraded.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Manager cost | 1–5 minutes of current income at unlock | Early relief vs meaningful purchase |
| Active vs idle ratio | taps 2–5× faster before automation | Rewards early engagement |
| Manager abilities | cost −x %, speed ×y for a duration | Active play layer late |
| Automation order | cheapest generators first | Gradual transition |

- **Dynamics:** the transition from active clicker to idle manager is a deliberate arc — tapping teaches value, automation rewards it.
- **Aesthetics (MDA):** Submission, Fantasy (management), Challenge (when to buy).
- **Feedback and juice:** manager character portrait, "hired!" celebration, progress bars that now fill on their own.
- **Failure modes and exploits:** automation too early (no active phase) or too late (tap fatigue); auto-clicker tools outrunning design (cap tap rate).
- **Mobile fit:** central to idle's appeal on phones.
- **Monetization hooks and ethical limit:** premium managers or auto-collect passes; keep base automation reachable for free.
- **Implementation notes:** automation is a boolean per generator plus optional ability timers; production math becomes continuous once automated (`income per second`), cycle-based before.
- **Worked example:** a 3 s-cycle generator earning 100 per cycle yields 33/s only if the player taps every cycle; a realistic active player collects about every 5–10 s (10–20/s). Pricing its manager at ~2–4 minutes of the automated rate (≈ 4,000–8,000) makes the purchase feel like an immediate raise rather than a luxury.
- **Reference games:** AdVenture Capitalist (managers), Idle Miner Tycoon (managers per shaft), Cookie Clicker (contrast: no manual collection beyond the big cookie).
- **Combines well with:** `idle-generators`, `offline-earnings`, `production-bottlenecks`.

### 04.06 Offline earnings — `offline-earnings`

- **ID:** `offline-earnings` · **Category:** economy / source (time-based) · **Player fantasy:** "Welcome back, boss — look what you made while you were away."
- **Core rules:**
  - On resume: `elapsed = min(now − last_seen, cap)`; `earned = income_rate × elapsed × efficiency`. Show a "welcome back" summary; optionally offer ×2 via rewarded ad or currency.
  - Only automated production counts; active-only sources do not.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Offline cap | 2–12 h (upgradeable) | Return cadence (cap ≈ desired max gap) |
| Efficiency | 25–100 % of online rate | Keeps online play more valuable |
| Doubler | ×2 via ad / ×3 via currency | Re-engagement hook |
| Cap upgrades | +1–2 h per tier | Long-term goal |

- **Dynamics:** sets the return rhythm (players return roughly when the cap fills); morning/evening check-ins.
- **Aesthetics (MDA):** Submission, Fantasy.
- **Feedback and juice:** big summary card with counted-up total, collect button with coin burst.
- **Failure modes and exploits:** device clock manipulation (use server time when online, and monotonic uptime plus last trusted timestamp offline; clamp negative deltas); huge offline gains trivialising online play (efficiency < 100 %).
- **Mobile fit:** native fit to how phones are used — interruptions become rewards.
- **Monetization hooks and ethical limit:** doubler via rewarded ad is widely accepted; avoid caps so short that players feel punished for sleeping.
- **Implementation notes:** store `last_seen_server_time`; on resume, if offline, use `max(0, min(device_now − last_seen, cap))` and flag suspicious jumps (> cap × 3) for analytics.

```text
on_resume(): now = server_time() or device_time_guarded()
  dt = clamp(now - save.last_seen, 0, OFFLINE_CAP); if now < save.last_seen: flag("clock_rollback")
  earned = automated_income_rate(save) * dt * EFFICIENCY; show_welcome_back(earned, offer_doubler=True)
  save.last_seen = now
```
- **Reference games:** AdVenture Capitalist, Idle Miner Tycoon, Egg, Inc., AFK Arena (idle reward chest).
- **Combines well with:** `automation-managers`, `storage-caps`, idle rewards and notifications (`references/08-time-energy-session-mechanics.md`).

### 04.07 Prestige / rebirth — `prestige-rebirth`

- **ID:** `prestige-rebirth` · **Category:** economy / converter + sink (reset loop) · **Player fantasy:** "I burn it all down — and come back far stronger."
- **Core rules:**
  - The player may reset run progress (generators, upgrades, soft currency) in exchange for a prestige currency computed from lifetime or run earnings. Prestige currency gives a permanent multiplier (e.g., +1–2 % income per point) and/or unlocks a prestige upgrade tree.
  - Formula families use sub-linear roots so that each prestige requires substantially more earnings: `P = floor(k × (lifetime_earnings / unit)^(1/2))` (square-root family) or `^(1/3)` (cube-root family; Cookie Clicker's prestige level is the cube root of total cookies baked over 10^12).
  - Optimal prestige timing: reset when the prestige points you would gain would at least double (or meaningfully raise) your multiplier relative to current run progress speed.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Root exponent | 1/2 – 1/3 | Lower = slower prestige growth, longer play |
| Bonus per point | +1–5 % income | Strength of each reset |
| First prestige timing | 1–3 days of play | When the system is revealed |
| Kept on reset | milestones, some upgrades | Reduces reset pain |
| Prestige layers | 1–3 (prestige of prestige) | Very long-term depth |

- **Dynamics:** cycles of fast re-climb; optimisation of reset timing; "the second run is 10× faster" delight.
- **Aesthetics (MDA):** Challenge, Discovery, Submission.
- **Feedback and juice:** preview "+N prestige → ×M income", dramatic reset animation, fast early re-climb with frequent celebrations.
- **Failure modes and exploits:** resets that feel like loss (show clear gains before confirming); multiplier growth outpacing cost growth (runaway after a few prestiges — simulate 10+ resets); hidden formulas.
- **Mobile fit:** suits multi-day engagement; each run fits short sessions.
- **Monetization hooks and ethical limit:** prestige boosters, permanent multipliers; avoid making resets so slow that only payers can progress.
- **Implementation notes:** keep prestige computation pure and tested; simulate many cycles to find the equilibrium time-per-prestige.

```text
prestige_points(lifetime) = floor(K * (lifetime / UNIT) ** (1/ROOT))
gain_if_reset = prestige_points(lifetime) - points_already_claimed
multiplier(points) = 1 + BONUS * points
```

- **Reference games:** Cookie Clicker (heavenly chips), AdVenture Capitalist (angel investors), Egg, Inc. (soul eggs), Realm Grinder.
- **Combines well with:** `idle-generators`, `exponential-upgrades`, `multiplier-milestones`, roguelite meta progression (`references/05-progression-meta-mechanics.md`).

### 04.08 Production chains and bottlenecks — `production-bottlenecks`

- **ID:** `production-bottlenecks` · **Category:** economy / converter + pool network · **Player fantasy:** "I run a smooth machine — and I know exactly which part to fix next."
- **Core rules:**
  - Resources flow through stages (extract → transport → process → sell). Each stage has a capacity per second. Throughput = `min(stage capacities)`; upstream surplus piles up in buffers (pools with caps).
  - Upgrading a non-bottleneck stage yields nothing until the bottleneck is raised: the core decision is finding the bottleneck.
  - Multi-input recipes create branching chains (bread needs wheat + eggs), with co-dependencies.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Stages per chain | 2–5 | Complexity |
| Buffer capacities | 1–10 minutes of throughput | Visibility of bottlenecks |
| Upgrade granularity | +10–25 % capacity per level | Frequency of bottleneck shifts |
| Inter-chain dependencies | 0–3 shared inputs | Strategic depth |
| Visual throughput cues | piles, queues, idle workers | Diagnosability |

- **Dynamics:** bottleneck hunting; satisfying optimisation; shifting bottlenecks create a continuous decision loop.
- **Aesthetics (MDA):** Challenge, Submission, Expression (layout in builders).
- **Feedback and juice:** visible piles at the bottleneck, idle workers animating boredom, numbers per stage, a "bottleneck" warning icon.
- **Failure modes and exploits:** invisible bottlenecks (show rates per stage); deadlocks where chains need each other's outputs with no seed stock; too many chains for small screens.
- **Mobile fit:** good in idle tycoons; complex chains need zoomable views.
- **Monetization hooks and ethical limit:** stage boosts, extra workers; keep upgrade paths understandable so purchases are informed.
- **Implementation notes:** compute flows analytically per tick for idle (min over stages, buffer deltas), event-driven for builders; show per-stage rates from the same numbers.
- **Reference games:** Idle Miner Tycoon (shafts → elevator → warehouse), Hay Day, Township, Factorio (PC, the deep-end reference for chain design).
- **Combines well with:** `crafting-chains`, `storage-caps`, `build-queues`, `automation-managers`.

## 4. Conversion, crafting and time

### 04.09 Crafting chains — `crafting-chains`

- **ID:** `crafting-chains` · **Category:** economy / converter tree · **Player fantasy:** "I turn raw stuff into treasures through my own know-how."
- **Core rules:**
  - A recipe: `{inputs: {item: qty}, outputs: {item: qty}, station, time, unlock}`. Recipes form a DAG from raw materials (tier 0) to final goods (tier N).
  - Total raw cost of item X = recursive expansion of its recipe tree; total time = critical path if stations work in parallel, sum if serial.
  - Variants: **grid/shape recipes** (Minecraft), **station queues** (Hay Day bakery), **discovery crafting** (combine to find recipes — Little Alchemy), **quality/random affixes** on crafted items.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Tier depth | 2–6 | Goal horizon and complexity |
| Branching factor | 1–4 inputs per recipe | Logistics load |
| Raw-to-final value multiplier | 1.2–2× per tier | Reward for processing |
| Craft time per tier | seconds (casual) – hours (builders) | Session cadence |
| Recipe discovery | given / unlocked / discovered | Exploration vs clarity |

- **Dynamics:** planning backwards from goals (orders, quests); specialisation; trading surplus.
- **Aesthetics (MDA):** Expression, Discovery, Submission.
- **Feedback and juice:** recipe cards with have/need counts, craft completion pop, new-recipe discovery fanfare.
- **Failure modes and exploits:** recipe spaghetti (too many intermediate items — each must be used by ≥ 2 recipes or be a goal itself); value inversions (selling inputs worth more than outputs); hidden raw requirements.
- **Mobile fit:** queues fit check-in play; grid crafting needs larger screens.
- **Monetization hooks and ethical limit:** speed-ups and rare inputs; avoid recipes whose only practical input source is paid.
- **Implementation notes:** expand trees with memoisation to compute raw costs and times for balance tables; validate the DAG has no cycles unless intentional (recycling loops must lose value).

```text
raw_cost(item): if item in RAW: return {item: 1}
  r = RECIPE[item]; total = {}
  for inp, q in r.inputs: for raw, n in raw_cost(inp): total[raw] += n * q / r.outputs[item]
  return total
```

- **Reference games:** Hay Day, Minecraft, Stardew Valley, Little Alchemy.
- **Combines well with:** `production-bottlenecks`, `build-queues`, `markets-auctions`, collection and building (`references/09-collection-crafting-building.md`).

### 04.10 Build queues and timers — `build-queues`

- **ID:** `build-queues` · **Category:** economy / gate (real time) · **Player fantasy:** "My kingdom grows while I'm busy living my life."
- **Core rules:**
  - Starting a task (build, upgrade, research, craft, train) occupies a slot for `duration`. Parallel slots = builders/stations; completed tasks must often be collected.
  - Durations grow with level (seconds early → hours or days late). Speed-ups convert hard currency (or ads, or help from team members) into time.
  - Speed-up price curves are concave (cheaper per hour for longer timers). Example, as documented by the Clash of Clans community wiki (verify): about 1 gem for 1 minute, 20 for 1 hour, 260 for 1 day, 1,000 for 1 week, interpolated between.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Slots | 1–5 builders/stations | Parallelism and planning |
| Early durations | 5 s – 5 min | FTUE pace (keep first hour snappy) |
| Late durations | 4 h – 7 days | Long-term cadence |
| Free skip threshold | last 5 min free (common pattern) | Removes trivial waits |
| Help mechanic | each ally help −1 % or −1 min | Social glue |

- **Dynamics:** appointment play (return when done), scheduling decisions (start long tasks before sleep), queue optimisation.
- **Aesthetics (MDA):** Submission, Challenge (planning), Fellowship (help).
- **Feedback and juice:** timer bubbles, completion notifications (opt-in), "ready" bouncing icons, satisfying collect.
- **Failure modes and exploits:** timers dominating play with nothing else to do (always have a playable loop alongside waiting); time-zone/clock exploits (server time); excessive push notifications.
- **Mobile fit:** native to phone check-in behaviour; notifications must be respectful and opt-in.
- **Monetization hooks and ethical limit:** speed-ups, extra builders, passes. Avoid inflating timers solely to sell skips — test that the free cadence still produces a satisfying day of progress.
- **Implementation notes:** store absolute `complete_at` server timestamps; never tick down stored durations. Speed-up price by piecewise-linear interpolation over anchor points.

```text
SPEEDUP_ANCHORS = [(60, 1), (3600, 20), (86400, 260), (604800, 1000)]   # seconds → gems (example)
price(sec): find anchors (s0,g0),(s1,g1) around sec; return ceil(g0 + (g1-g0) * (sec-s0)/(s1-s0))
```

- **Reference games:** Clash of Clans, Hay Day, Township, Rise of Kingdoms.
- **Combines well with:** `crafting-chains`, `storage-caps`, guild help (`references/06-social-competitive-mechanics.md`), timers and notifications (`references/08-time-energy-session-mechanics.md`).

### 04.11 Storage caps and inventory limits — `storage-caps`

- **ID:** `storage-caps` · **Category:** economy / pool capacity · **Player fantasy:** "My vaults are full — time to spend, sort and expand."
- **Core rules:**
  - Each pool has `cap`; income beyond cap is lost (or held in an overflow mailbox). Cap upgrades are a progression track.
  - Inventory variants: slot-limited (N slots, stacks of S), weight-limited, or per-category bags. Full inventory blocks pickups or forces choices.
  - In raid games, storage determines how much can be stolen (with a protected fraction).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Soft-currency cap | 1–3 days of income | Forces regular spending (anti-hoard) |
| Cap upgrade cost | grows with cap | Long-term track |
| Inventory slots | 20–200 | Management load |
| Stack size | 10–999 | Clutter control |
| Overflow behaviour | lost / mailbox / auto-sell | Frustration level |

- **Dynamics:** spend-it-before-you-lose-it; sorting and selling; upgrading storage as a goal.
- **Aesthetics (MDA):** Challenge (management), Submission.
- **Feedback and juice:** fill bars turning amber/red near cap, "storage full" warnings with a direct upgrade or spend shortcut.
- **Failure modes and exploits:** caps that punish absence (combine with offline caps thoughtfully); inventory management tedium (auto-sort, bulk sell); paid slots as the primary relief valve.
- **Mobile fit:** inventory UIs must be thumb-friendly with large slots and filters.
- **Monetization hooks and ethical limit:** extra slots and storage are common IAP; ensure free expansion exists and caps do not destroy earned rewards silently.
- **Implementation notes:** apply caps at credit time (`credited = min(amount, cap − balance)`), log overflow for analytics (it reveals friction).
- **Reference games:** Clash of Clans (storages), Pokémon GO (item bag and Pokémon storage upgrades), Hay Day (barn and silo), Diablo Immortal.
- **Combines well with:** `offline-earnings`, `gold-sinks`, `build-queues`, collection (`references/09-collection-crafting-building.md`).

### 04.12 Converters and exchange rates — `converters-exchange`

- **ID:** `converters-exchange` · **Category:** economy / converter · **Player fantasy:** "Nothing I own is useless — I can turn duplicates into what I actually want."
- **Core rules:**
  - Fixed-rate conversion between resources with deliberate loss (a sink): duplicates → dust/shards → targeted crafting; hard → soft currency at a published rate; event currency → shop items.
  - Asymmetry rule: breaking down returns a fraction of creation cost, so conversion cannot be looped for profit.
  - Example (Hearthstone, long-standing values): crafting costs 40/100/400/1,600 dust for common/rare/epic/legendary; disenchanting returns 5/20/100/400.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Disenchant return | 10–25 % of craft cost | Value of duplicates; sink size |
| Conversion direction | one-way vs two-way | Exploit safety |
| Daily exchange limits | none – small caps | Prevents arbitrage |
| Rate transparency | always shown | Trust |
| Shard targeting | specific item vs pool | Determinism vs gamble |

- **Dynamics:** "bad luck protection" via deterministic targets; collection completion paths; value judgments about what to break down.
- **Aesthetics (MDA):** Challenge (choices), Submission, Expression.
- **Feedback and juice:** conversion animation showing items dissolving into the target resource; preview totals before confirming.
- **Failure modes and exploits:** circular conversions at profit (graph-check all conversion cycles: product of rates around any cycle must be < 1); confusing multi-step conversions hiding real prices.
- **Mobile fit:** neutral; keep conversion screens simple.
- **Monetization hooks and ethical limit:** converters soften randomness of paid draws — a pro-consumer feature; publish rates.
- **Implementation notes:** represent conversions as a directed weighted graph; verify `Π rate < 1` around every cycle (Bellman-Ford on −log(rate) detects profitable cycles).
- **Reference games:** Hearthstone (dust), Genshin Impact (starglitter/stardust shops), Pokémon GO (candy transfer).
- **Combines well with:** `chests`, gacha pity (`references/07-randomness-chance-mechanics.md`), collection (`references/09-collection-crafting-building.md`).

## 5. Exchange between players

### 04.13 Player trading — `player-trading`

- **ID:** `player-trading` · **Category:** economy / converter (social) · **Player fantasy:** "I trade with friends to complete my collection."
- **Core rules:**
  - Two players exchange items directly. Constraints prevent abuse: friendship or level requirements, trade costs (currency scaled by rarity), daily limits, tradability flags (bound vs tradable), cooldowns.
  - Escrow: both sides confirm the final offer; any change resets confirmation.
  - Real-money trading (RMT) prevention: value caps, rarity restrictions, account age requirements.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Trade cost | scaled by rarity and novelty | Sink + RMT friction |
| Daily trade cap | 1 special trade/day – unlimited | Market liquidity vs abuse |
| Tradable rarities | common–rare only, or all | Value of top items |
| Friendship requirement | days of friendship or level | Bot/RMT defence |
| Confirmation flow | two-step with final review | Scam prevention |

- **Dynamics:** social bonding, negotiation, collection completion; a black market if limits are too loose.
- **Aesthetics (MDA):** Fellowship, Expression, Discovery.
- **Feedback and juice:** side-by-side offer view, dual confirmation animation, special effects for rare trades.
- **Failure modes and exploits:** scams (item swap before confirm — reset confirmations on change), RMT, multi-account farming, trading undermining monetization of rare items; minors and exploitative trades (age policies).
- **Mobile fit:** async trade requests fit mobile; real-time trades need presence.
- **Monetization hooks and ethical limit:** trade costs paid in soft currency; do not sell "trade tokens" that make trading primarily a paid activity.
- **Implementation notes:** server-authoritative atomic swap transaction; log all trades with values for fraud analytics.
- **Reference games:** Pokémon GO (trading with Stardust costs and special-trade limits), Pokémon TCG Pocket (trading with limits and costs, widely criticised as restrictive when the feature launched), Monopoly GO! (sticker trading between friends for album sets).
- **Combines well with:** collection (`references/09-collection-crafting-building.md`), friends and guilds (`references/06-social-competitive-mechanics.md`), `markets-auctions`.

### 04.14 Markets and auctions — `markets-auctions`

- **ID:** `markets-auctions` · **Category:** economy / converter + sink (player-priced) · **Player fantasy:** "I read the market, buy low, sell high — and supply what others need."
- **Core rules:**
  - Players list items with prices; others buy. Variants: **fixed-price stalls** (Hay Day roadside shop — price set within a min–max band per item), **order books** (buy and sell orders matched — Grand Exchange, Albion Online), **timed auctions** (highest bid at expiry).
  - Fees and taxes on sales act as gold sinks; buy limits per time window throttle bots and manipulation.
  - Price bands or reference prices prevent RMT via extreme prices.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Sales tax / listing fee | 1–10 % | Sink strength; too high kills trading |
| Price band | ±50–100 % around reference | RMT prevention vs free market |
| Buy limits | per item per 4 h (Old School RuneScape uses 4-hour limits) | Bot and manipulation throttle |
| Listing duration | 12 h – 7 days | Liquidity |
| NPC buy/sell floor | present / absent | Price stability |

- **Dynamics:** emergent prices, arbitrage, specialisation (crafters supply, fighters consume); inflation if faucets exceed sinks.
- **Aesthetics (MDA):** Challenge, Fellowship, Expression.
- **Feedback and juice:** price history charts, "sold!" notifications, coin collect animations.
- **Failure modes and exploits:** market manipulation and cornering (buy limits, NPC floors), RMT (price bands, tradability), bots flooding gathering markets, inflation (monitor median prices weekly).
- **Mobile fit:** list/buy flows are UI-heavy — use filters, recent prices and one-tap relist.
- **Monetization hooks and ethical limit:** extra listing slots; never sell market intelligence that gives paying players information asymmetry against others.
- **Implementation notes:** order matching on the server: price-time priority; settle atomically; store price history aggregates (OHLC per hour) for charts and economy monitoring.
- **Reference games:** Hay Day (roadside shop and newspaper), Old School RuneScape (Grand Exchange, on mobile), Albion Online (player-driven markets), EVE Online (PC; reference for deep markets).
- **Combines well with:** `crafting-chains`, `gathering-nodes`, `gold-sinks`, guild economies (`references/06-social-competitive-mechanics.md`).

## 6. Session gates and level consumables

### 04.15 Energy — `energy`

- **ID:** `energy` · **Category:** economy / gate + regenerating pool · **Player fantasy:** "I'm fresh and ready — let's make the most of this session."
- **Core rules:**
  - Pool `E` with cap `E_max`, regenerating 1 unit per `t_regen` up to cap (overflow from rewards allowed above cap). Actions cost energy (per level, per generator tap, per run).
  - When empty: wait, watch an ad, use a refill item, or pay. Level-ups or events often refill.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Cap | enough for one satisfying session (≈ 10–30 min of play) | Session length |
| Full regen time | 2–6 h | Sessions per day (≈ waking hours / full regen) |
| Cost per action | 1–10 | Granularity |
| Overflow from rewards | allowed up to 2–5× cap | Generosity without breaking cap math |
| Free refills | level-up, daily, ad (cap 3–5/day) | Softens hard stops |

- **Dynamics:** sessions bounded and paced; return appointments; spend decisions about what to use energy on.
- **Aesthetics (MDA):** Submission, Challenge (allocation).
- **Feedback and juice:** energy bar with countdown to next unit and to full, "full energy" notification (opt-in), refill celebration.
- **Failure modes and exploits:** energy too tight in the first days (kills D1 — first sessions should rarely hit empty); energy on failure-prone actions (losing energy for losing feels punitive — consider refunds on loss in skill games); clock manipulation (server time).
- **Mobile fit:** designed for mobile session patterns; respect sleep with full regen in the morning.
- **Monetization hooks and ethical limit:** refills and cap increases are classic IAP; keep the free session satisfying and avoid "energy runs out mid-goal" engineered with an offer (see `references/08-time-energy-session-mechanics.md` and `references/12-monetization-linked-mechanics.md`).
- **Implementation notes:** store `(energy, last_update_ts)`; compute current energy lazily: `e = min(E_max, e0 + floor((now − ts) / t_regen))` when below cap, carry the remainder of the timer.

```text
current(now): if e0 >= E_MAX: return e0
  gained = (now - ts) // T_REGEN; e = min(E_MAX, e0 + gained)
  ts_new = ts + gained * T_REGEN if e < E_MAX else now; return e, ts_new
```

- **Reference games:** Merge Mansion, June's Journey, Genshin Impact (Original Resin), Archero.
- **Combines well with:** `merge` (`references/03-puzzle-mechanics.md`), `lives-pool`, session design (`references/08-time-energy-session-mechanics.md`).

### 04.16 Lives — `lives-pool`

- **ID:** `lives-pool` · **Category:** economy / gate + regenerating pool · **Player fantasy:** "Each attempt matters — but I'll always get more chances."
- **Core rules:**
  - Pool of lives (genre standard 5, popularised by Candy Crush Saga, with roughly 30 minutes per life regeneration). Starting a level is free; **losing** consumes a life (winning does not). Quitting mid-level counts as a loss.
  - Zero lives → wait, ask friends/team for lives, ad, or buy refill. Timed **unlimited lives** (30 min – several hours) are common rewards and offers.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Max lives | 5 (3–7) | Attempts per session |
| Regen per life | 20–30 min | Session cadence |
| Unlimited-lives rewards | 15 min – 3 h | Generosity and event fuel |
| Team life gifting | 1 per request, team-limited | Social glue |
| Hard-level warnings | flag before start | Expectation setting |

- **Dynamics:** each attempt feels weighty near the end of the pool; social requests; binge sessions during unlimited-lives windows.
- **Aesthetics (MDA):** Challenge, Fellowship (gifting).
- **Feedback and juice:** heart animations, countdown, "life lost" gentle (not shaming) screen, unlimited-lives infinity icon with timer.
- **Failure modes and exploits:** lives + very hard levels = frustration paywall; closing the app to avoid losing a life (count as loss when re-opened mid-level, but be lenient on genuine crashes).
- **Mobile fit:** native to puzzle session lengths; good with interruptions.
- **Monetization hooks and ethical limit:** life refills and unlimited-lives bundles; do not pair life depletion with difficulty spikes tuned to monetization rather than design intent.
- **Implementation notes:** same lazy-regeneration math as energy; mark "level in progress" in save data to resolve quits.
- **Worked example:** with 5 lives and 30-minute regeneration, a player who plays 3 sessions a day 4 hours apart starts each session full (5 lives) and can lose at most 5 times per session; on a level with a 25 % win rate, the expected attempts to win are 4, so one hard level can consume an entire session — which is why hard-level frequency and lives must be tuned together (see `progression-difficulty`).
- **Reference games:** Candy Crush Saga, Royal Match, Toon Blast, Homescapes.
- **Combines well with:** `match3-swap` (`references/03-puzzle-mechanics.md`), team help (`references/06-social-competitive-mechanics.md`), `boosters`.

### 04.17 Boosters — `boosters`

- **ID:** `boosters` · **Category:** economy / consumable pool + sink · **Player fantasy:** "I've got a trick up my sleeve for exactly this moment."
- **Core rules:**
  - Three timings: **pre-level** (chosen before start: e.g., start with specials), **in-level** (applied mid-level: hammer removes one tile, shuffle, extra time), **post-fail** (continue with extra moves).
  - Sources: level rewards, chests, events, win streaks (escalating free pre-level boosts after consecutive wins), purchase. Sinks: use.
  - Hoarding is natural (players save boosters "for a hard level"); time-limited or streak-based boosters counter it.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Free booster income | ~1 per 3–10 levels | Familiarity and generosity |
| Booster strength | 5–20 % win-rate uplift on hard levels | Value; measure via bots |
| Post-fail continue | +5 moves / +15 s, escalating price | Recovery and revenue |
| Win-streak boosts | 3 escalating steps | Rewards consistency, reduces hoarding |
| Timed infinite boosters | 15–60 min | Event excitement |

- **Dynamics:** resource judgment (when to use); risk mitigation; streak protection behaviour.
- **Aesthetics (MDA):** Challenge, Fantasy (power), Submission.
- **Feedback and juice:** booster unlock tutorial on first grant, strong activation VFX, counters on booster buttons.
- **Failure modes and exploits:** levels that need boosters to be fair (tune with bots without boosters first); hoards of hundreds (raise sinks or switch to timed); confusing booster tutorials.
- **Mobile fit:** booster bar in the bottom thumb zone during levels.
- **Monetization hooks and ethical limit:** boosters and continues are core puzzle revenue. Price continues transparently; do not show "you were so close!" manipulation unless it is true and measured (it often is not).
- **Implementation notes:** booster effects reuse level mechanics (a hammer is a `damage_cell` call); measure uplift with `match3_sim.py` runs with and without each booster to price them.
- **Reference games:** Candy Crush Saga (lollipop hammer, colour bomb starts), Royal Match, Subway Surfers (head starts, score boosters).
- **Combines well with:** `lives-pool`, `chests`, `special-pieces` (`references/03-puzzle-mechanics.md`), offers (`references/12-monetization-linked-mechanics.md`).

## 7. Sinks, rewards and maintenance

### 04.18 Gold sinks — `gold-sinks`

- **ID:** `gold-sinks` · **Category:** economy / sink catalogue · **Player fantasy:** "There's always something worth spending on."
- **Core rules:** every faucet needs drains the player *wants* to use. Sink families:

| Sink family | Examples | Player perception | Notes |
|---|---|---|---|
| Progression | upgrades, levels, unlocks | Positive (power) | Primary sink; exponential costs |
| Cosmetic / expression | decorations, skins, furniture | Positive (identity) | Infinite capacity, no power creep |
| Consumables | boosters, potions, ammo | Neutral | Repeatable; tie to difficulty |
| Rerolls and retries | shop refresh, stat reroll, continues | Neutral–negative | Watch gambling-like loops |
| Fees and taxes | market tax, trade cost, travel cost | Negative but accepted | Small % |
| Maintenance | repairs, upkeep | Negative | Use sparingly (see `upkeep-decay`) |
| Risky upgrades | chance-to-fail enhancement | Strongly negative when failing | Ethical risk; disclose odds; prefer pity |
| Status and social | guild donations, gifts | Positive (belonging) | Social reinforcement |

- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Sink capacity vs faucet | ≥ 100 % of engaged-player income | Prevents inflation |
| Cosmetic sink share | 10–40 % of late-game spend | Long-tail sink without power creep |
| Fee rates | 1–10 % | Market health |
| Reroll cost escalation | +25–100 % per reroll per day | Limits compulsive rerolling |

- **Dynamics:** keeps currencies meaningful; sinks shape what players value.
- **Aesthetics (MDA):** Expression, Challenge, Submission.
- **Feedback and juice:** spending should feel like gaining (fly-from-wallet into the item, instant visible change).
- **Failure modes and exploits:** sinks that feel like taxes only; late-game players with nothing to buy (inflation, boredom); risky-upgrade loops that resemble gambling (regulatory and ethical risk).
- **Mobile fit:** neutral.
- **Monetization hooks and ethical limit:** cosmetic sinks are the healthiest late-game monetization; disclose odds on any chance-based sink.
- **Implementation notes:** tag every sink in analytics (`economy_spend` with `sink_id`) and chart sink share by player segment monthly; an `economy-model` should list sinks as `sink` nodes with triggers.
- **Reference games:** Hay Day (decorations), Animal Crossing (furniture and home loan as sinks; console reference), Old School RuneScape (Grand Exchange tax), Gardenscapes (renovation as sink).
- **Combines well with:** `currency-architecture`, `markets-auctions`, `storage-caps`, decoration meta (`references/09-collection-crafting-building.md`).

### 04.19 Chests — `chests`

- **ID:** `chests` · **Category:** economy / gate + source (container) · **Player fantasy:** "What's inside? Opening it is a little celebration."
- **Core rules:**
  - A chest has `rarity`, a contents table (guaranteed items + weighted random rolls), and an opening gate: **time** (unlock timer; limited chest slots), **key** (keys earned from wins or currency), **currency** (instant), **progress** (fill a meter by playing).
  - Classic slot pattern (Clash Royale's original design, since reworked — verify current state): wins award chests into 4 slots; each unlocks over hours by rarity; only one unlocks at a time unless paid.
  - Paid random chests are loot boxes: disclose odds, check per-country rules (Belgium bans paid loot boxes; Brazil's ECA Digital restricts sales to under-18s from March 2026 — see Volatile facts and `legal-ethics`).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Guaranteed content share | 50–100 % of chest value | Reduces gambling feel |
| Rarity tiers | 3–5 | Excitement ladder |
| Unlock times | 15 min – 24 h by rarity | Session cadence (time-gated variant) |
| Slots | 2–4 | Forces returns; slot-full = lost rewards (avoid) |
| Pity / bad-luck protection | guaranteed rare every N chests | Fairness |

- **Dynamics:** anticipation; appointment returns; collection progress via drops.
- **Aesthetics (MDA):** Sensation, Discovery, Submission.
- **Feedback and juice:** shaking chest, burst of light by rarity, items revealed one by one with rising tension, rarity-coloured beams.
- **Failure modes and exploits:** chest slots full → earned rewards discarded (frustrating; provide a queue); opaque odds; chests as the only route to key items (combine with converters or direct purchase).
- **Mobile fit:** satisfying 3–10 s unboxing moments fit mobile; allow skip-to-results.
- **Monetization hooks and ethical limit:** keys, instant opens, premium chests. Paid randomness needs published odds and age-appropriate handling; prefer transparent, fixed-content bundles where regulation is strict.
- **Implementation notes:** server-side rolls with seeded RNG and audit logs; contents tables as data with versioning; compute expected value per chest for pricing (`gacha_calc.py` for pity math).
- **Reference games:** Clash Royale (classic chest slots), Brawl Stars (reported removal of Brawl Boxes in 2022 in favour of a visible reward road, later adding Starr Drops), Archero (chests), Hearthstone (card packs).
- **Combines well with:** `converters-exchange`, gacha and drop tables (`references/07-randomness-chance-mechanics.md`), battle passes (`references/12-monetization-linked-mechanics.md`).

### 04.20 Upkeep and decay — `upkeep-decay`

- **ID:** `upkeep-decay` · **Category:** economy / ongoing sink · **Player fantasy:** "My world feels alive — it needs me."
- **Core rules:**
  - Owned things cost resources over time (troop food upkeep, building maintenance, pet hunger) or lose value (crops wither if not harvested, items lose durability with use, food spoils).
  - Variants: **durability** (per use), **time decay** (per hour), **upkeep** (per tick proportional to holdings), **spoilage** (perishables).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Decay grace period | 0–24 h after "ready" | Absence tolerance |
| Durability per item | 50–500 uses | Repair cadence |
| Repair cost | 10–30 % of item value | Sink size |
| Upkeep rate | 1–5 % of holdings per day | Caps hoarding of units |
| Protection (vacation mode) | available / not | Fairness for breaks |

- **Dynamics:** maintenance routines; caps on army size or holdings; meaningful logistics.
- **Aesthetics (MDA):** Challenge, Fantasy (living world), Narrative.
- **Feedback and juice:** visual wilting or wear, warnings before loss, satisfying repair animations.
- **Failure modes and exploits:** punishing absence (players who lose progress after a holiday churn); chores instead of fun; anxiety-driven engagement (an ethical concern). Prefer "pause" decay (things stop producing) over "destroy" decay.
- **Mobile fit:** notifications tempt overuse; keep decay gentle for casual audiences.
- **Monetization hooks and ethical limit:** repair kits and protection items; never sell relief from anxiety the game deliberately manufactured.
- **Implementation notes:** compute decay lazily from timestamps like energy; durability as integer counters on item instances.

```text
crop_state(now): if now < ready_at: return GROWING
  if now < ready_at + GRACE: return READY
  return PAUSED if DECAY_MODE == "pause" else WITHERED   # prefer pause: stops yielding, never destroys
```
- **Reference games:** FarmVille (withering crops, the cautionary example), Tamagotchi-style pet games, Last Day on Earth: Survival (item durability), Minecraft (tool durability).
- **Combines well with:** `gold-sinks`, `gathering-nodes`, survival loops (`references/10-narrative-exploration-mechanics.md`).

### 04.21 Gathering nodes and respawn — `gathering-nodes`

- **ID:** `gathering-nodes` · **Category:** economy / source + gate (world resources) · **Player fantasy:** "I know where the good stuff is and when it comes back."
- **Core rules:**
  - World nodes (trees, ore veins, bushes, map points) yield resources on interaction (tap, hold, minigame), then deplete and respawn after `t_respawn`, or have per-player cooldowns.
  - Yield tables with tool-level requirements and rare drops; nodes can be shared (competition) or instanced per player (no competition).
  - Location-based variant: real-world points of interest with per-player cooldowns.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Respawn / cooldown | 1 min – 24 h | Return cadence |
| Yield per interaction | 1–10 units + rare roll | Grind rate |
| Shared vs instanced | instanced on mobile (usual) | Avoids griefing |
| Tool gating | tier per node type | Progression hook |
| Rare drop chance | 1–5 % | Excitement |

- **Dynamics:** routing and loops through the world; scheduling returns; exploration for richer nodes.
- **Aesthetics (MDA):** Discovery, Submission, Fantasy.
- **Feedback and juice:** hit/harvest animations with particles, resource popups, respawn shimmer, map icons showing ready nodes.
- **Failure modes and exploits:** bots farming shared nodes; tedious tapping (auto-gather for low tiers); location spoofing in location-based games.
- **Mobile fit:** short gathering loops fit sessions; location-based play depends on safety and accessibility considerations.
- **Monetization hooks and ethical limit:** tools, gathering speed, extra yield; keep the free rate adequate for core progress.
- **Implementation notes:** per-player node state `{node_id: ready_at}`; generate node placements with `pcg.py poisson` for even distribution.
- **Reference games:** Pokémon GO (PokéStops with ~5-minute cooldowns), Stardew Valley (forage and ore), Hay Day (trees and bushes), Albion Online (gathering tiers).
- **Combines well with:** `crafting-chains`, `storage-caps`, `upkeep-decay`, exploration (`references/10-narrative-exploration-mechanics.md`).

## 8. Economy review checklist

- [ ] Every currency has named sources and sinks, a cap or a reason it needs none, and an analytics event for each flow.
- [ ] An `economy-model` JSON exists and `economy_sim.py` runs show net flow, hoard days and days-to-complete-content per archetype within the contract targets.
- [ ] No conversion cycle returns more than it consumes (product of rates < 1 around every cycle).
- [ ] Exponential cost curves and multipliers simulated across at least 10 prestige cycles (idle) or 90 days (others) without runaway or dead walls.
- [ ] Energy/lives tuned so that new players rarely hit empty in their first sessions.
- [ ] Every paid random reward has published odds and a deterministic alternative path (pity, shards, direct purchase).
- [ ] Offline and timer systems use trusted time and clamp negative or extreme deltas.
- [ ] Monetized relief (speed-ups, refills, storage) never fixes friction that exists only to be sold.

## 9. Volatile facts (as of Oct 2026 — verify before relying)

- Loot-box rules: Belgium has treated paid loot boxes as illegal gambling since 2018; Brazil's ECA Digital law (signed Sep 2025) bans selling loot boxes to under-18s, effective March 2026; Australia applies M and R18+ classification rules for paid loot boxes and simulated gambling (since Sep 22, 2024). Sources: [Programming Insider](https://programminginsider.com/loot-boxes-regulation-and-where-the-line-sits-in-2026/), [Sheep Esports](https://www.sheepesports.com/articles/brazil-court-orders-riot-games-to-pay-eur2-5m-over-league-of-legends-loot-boxes/en). Full treatment in `legal-ethics`.
- Designing around direct-purchase or transparent mechanics (battle passes, fixed bundles) rather than paid random loot avoids most loot-box exposure across these regimes (an inference from the same sources, not legal advice).
