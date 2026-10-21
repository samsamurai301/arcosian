# Sources, Sinks and Balancing

An economy is balanced when every archetype of player can always see a next meaningful purchase, can usually afford it within one to three sessions, and never sits on a pile of currency with nothing worth buying. This file gives the studio's method for getting there: the Machinations-style flow vocabulary (sources, sinks, converters, gates, pools) and its feedback patterns, a taxonomy of sinks, how to set earn-rate targets backwards from pacing goals, the spreadsheet-to-simulation workflow that ends in `economy_sim.py`, a fully worked example with numbers and a schema-valid model, and the health metrics to watch after launch. Read it when designing a new economy, before every balance pass (`/arcosian:balance`), and whenever telemetry shows hoarding or starvation.

## Contents

1. [The flow model](#1-the-flow-model)
2. [Feedback patterns that make or break economies](#2-feedback-patterns-that-make-or-break-economies)
3. [Faucet and drain accounting](#3-faucet-and-drain-accounting)
4. [Sink taxonomy](#4-sink-taxonomy)
5. [Earn-rate targets](#5-earn-rate-targets)
6. [Spreadsheet-to-simulation method](#6-spreadsheet-to-simulation-method)
7. [Worked example: Lantern Lane](#7-worked-example-lantern-lane)
8. [Economy health metrics](#8-economy-health-metrics)
9. [Economy telemetry](#9-economy-telemetry)
10. [The economy change protocol](#10-the-economy-change-protocol)
11. [Balancing pitfalls](#11-balancing-pitfalls)
12. [Volatile facts](#12-volatile-facts-as-of-oct-2026--verify-before-relying)

---

## 1. The flow model

The ontology uses the resource-flow vocabulary popularised by Joris Dormans' Machinations framework (Adams & Dormans, *Game Mechanics: Advanced Game Design*, 2012). Each element maps to an `economy-model.schema.json` node `kind`:

| Element | Meaning | Schema `kind` | Mobile examples |
|---|---|---|---|
| **Source** (faucet) | Creates resources from nothing | `source` | Level-win coins, daily chest, ad reward, offline earnings |
| **Sink** (drain) | Destroys resources | `sink` | Continue (+5 moves), booster purchase, repair fee, gacha pull |
| **Converter** | Consumes inputs, produces different outputs | `converter` | Stars → decoration progress; coins + runes → upgrade level; duplicates → shards |
| **Gate** | Fires only when a condition or threshold holds | `gate` | Area completes at 20 decor points; chapter unlock at level 50 |
| **Pool** | Accumulates for later release | `pool` | Piggy bank, offline-earnings vault, battle-pass progress |

Triggers (`per_session`, `per_minute`, `per_level_attempt`, `per_level_win`, `per_level_loss`, `daily`, `weekly`, `on_purchase`, `on_ad`) decide when nodes fire; `probability` models drop rates and voluntary behaviour; `condition` encodes affordability and unlocks.

**Rule:** if a flow exists in the game, it exists in the model. Unmodelled faucets (compensation gifts, friend gifts, promo codes, event payouts) are the main reason launched economies diverge from the plan.

---

## 2. Feedback patterns that make or break economies

Adams & Dormans catalogue recurring structural patterns; the ones below matter most for mobile (summarised in our own words):

| Pattern | Structure | Player experience | Where it bites | Control |
|---|---|---|---|---|
| **Positive feedback (snowball)** | Output increases future output (income buys income) | Exhilarating growth; leaders run away | Idle games (intended); PvP (unintended) | Exponential costs, caps, prestige; matchmaking by power |
| **Negative feedback (rubber band)** | Output reduces future output or helps the trailing player | Stability, comebacks | Over-damped economies feel pointless | Keep it weak and visible; never punish success harshly |
| **Engine** | A source whose rate the player can invest in | Investment decisions, compounding | Engines without sinks inflate | Pair every engine with a scaling sink |
| **Converter engine** | Two converters feeding each other | Production chains | Arbitrage loops if the round trip gains | Cycle check (`currency-architecture.md` §4.4) |
| **Static friction** | A fixed drain regardless of player state | Predictable tax | Feels like rent | Use sparingly; tie to visible value |
| **Dynamic friction** | Drain that grows with the player's wealth or power | Keeps balances in a band | Feels like being punished for progress | Make it a purchase (upgrade costs) not a tax |
| **Attrition** | Players destroy each other's resources | PvP tension | Victims churn on mobile | Shields, protection windows, loss caps |
| **Escalation** | Challenge grows with player power | Constant tension | Treadmill feeling | Sawtooth difficulty, periodic relief |

**Design check:** for each currency, draw the loop and label every feedback arrow `+` or `−`. A currency with only `+` arrows will inflate; one with only `−` arrows will feel inert.

---

## 3. Faucet and drain accounting

### 3.1 Daily flow per archetype

For each archetype `a` and resource `r`:

```
income_r(a)  = Σ_sources  fires_per_day(node, a) × probability × output_r
spend_r(a)   = Σ_sinks/converters  fires_per_day(node, a) × probability × input_r   (only when affordable)
net_r(a)     = income_r(a) − spend_r(a)
balance_r(a, t) ≈ initial_r + t × net_r(a)       (mean-field; ignores variance and affordability guards)

fires_per_day by trigger:
  per_session      = sessions_per_day
  per_minute       = sessions_per_day × session_minutes
  per_level_attempt= attempts_per_day = sessions_per_day × session_minutes / minutes_per_attempt
  per_level_win    = attempts_per_day × win_rate(a)
  per_level_loss   = attempts_per_day × (1 − win_rate(a))
  daily            = 1 (on active days)
  on_ad            = ad_offers_per_day × ad_accept_rate(a)
```

### 3.2 Faucet/drain ratio and the three phases

```
FDR_r(a) = income_r(a) / spend_r(a)
```

| Phase | Player age | Target FDR (soft currency, house heuristic) | Why |
|---|---|---|---|
| Onboarding | Day 0–2 | 1.3–2.0 | Generosity builds competence and endowment; balances grow so the first purchases feel easy |
| Growth | Day 3–30 | 1.0–1.2 | Small surplus; each session ends with "almost enough" for the next thing |
| Maturity | Day 30+ | 0.9–1.05 for free players | Balances stable in a band; spend matches income; payers below 1.0 (they top up) |

FDR well above these bands → hoarding and inflation; well below → starvation and churn. Payers running FDR < 1 is expected: purchases fill the gap (that is the monetization surface), provided free players are not starving.

### 3.3 Hoard and starvation indicators

```
hoard_days(a)       = balance(a, t) / income_per_day(a)               target: ≤ targets.max_soft_currency_hoard_days
starvation(a)       = share of sessions where balance < price of the cheapest *essential* sink
affordability_gap   = sessions needed to afford the next meaningful purchase (target 1–3)
```

---

## 4. Sink taxonomy

Sinks are where currencies turn into meaning. A good sink is **wanted**, **repeatable** or **scalable**, and **felt as a purchase, not a tax**.

| Sink type | Examples | Elasticity | Scales with progress? | Perceived as | Risk |
|---|---|---|---|---|---|
| **Progression** | Upgrades, unlocks, building levels, hero levels | Low (players must buy) | Yes, by cost curve | Purchase (best) | Walls if curve outruns income |
| **Consumable (performance)** | Boosters, continues, revives | Medium | Optional scaling | Purchase in the moment | Pay-to-win perception in PvP |
| **Convenience** | Speed-ups, auto-collect, extra queue slots | High | Yes | Purchase | Becomes "pay to remove friction you added" |
| **Cosmetic / decoration** | Skins, decorations, themes | High | No (flat prices; new items) | Purchase (expressive) | Weak sink for non-expressive audiences |
| **Capacity** | Storage, inventory, energy cap upgrades | Low | Yes | Purchase (QoL) | Cap anxiety if too tight |
| **Chance** | Chests, gacha pulls, wheels | High | Optional | Excitement | Regulatory and ethical exposure (`gacha-and-loot.md`) |
| **Social** | Gifts, guild donations, team chests | Medium | Optional | Generosity | Pressure in guilds; keep voluntary |
| **Maintenance / upkeep** | Repairs, spoilage, rent | Low | Yes | Tax | Resented on mobile; absence punishment |
| **Fees / taxes** | Market fee, trade tax, crafting fee | Low | Yes | Tax | Acceptable when it buys a service (a trade) |
| **Reset** | Prestige, seasonal resets | Voluntary | — | Investment for multiplier | Confusing if introduced too early |
| **Entry fee** | Tournament tickets, event entry, PvP wager | Medium | Optional | Commitment | Gambling optics if prize pools are random |

**Sink portfolio rule:** every soft currency needs at least one **inelastic** sink (progression or capacity) to absorb median income and at least one **elastic** sink (cosmetic, consumable, convenience) to absorb surplus from engaged and paying players. Without the elastic sink, engaged players hoard; without the inelastic one, nobody needs to spend.

---

## 5. Earn-rate targets

Set earn rates **backwards from pacing goals**, never forwards from "what feels generous".

### 5.1 Procedure

1. Write the **pacing table**: for each milestone (first upgrade, first area, chapter 1, first hero ascension…), the session or day by which the median engaged free player should reach it, and the same for casual free.
2. Sum the prices of everything required to reach each milestone (`required_spend(milestone)`).
3. Required income rate = required_spend / play time available before the milestone.
4. Split income across sources by **intent**: core loop (the majority), daily/retention rewards, ads (capped), events.
5. Compare with the sim; adjust reward sizes before prices (players notice price changes more than reward changes).

### 5.2 Starting heuristics (house defaults; verify by sim and test)

| Target | Casual puzzle | Builder/farm | Gacha RPG | Idle |
|---|---|---|---|---|
| First purchase affordable | Session 1, < 3 min | Session 1, < 5 min | Session 1 (tutorial pull) | First minute |
| Meaningful soft purchase cadence | Every 1–2 sessions | Every session | Every 1–2 sessions (levels, gear) | Every few seconds to minutes (by design) |
| Single level/loop reward as % of next common sink | 10–20% | 5–15% | 5–10% | Grows with multipliers |
| Share of soft income from core loop | ≥ 60% | ≥ 60% | ≥ 50% | ≥ 70% (production) |
| Share from rewarded ads (non-payers) | ≤ 15–20% | ≤ 15% | ≤ 10% | Up to 30% (2× boosts) |
| Daily login/chest share | 10–20% | 10–20% | 10–25% | 5–10% |

**Reward/price coherence:** a level reward that is 1% of the next purchase feels meaningless; one that is 100% removes decisions. Keep most rewards in the 5–20% band so each win visibly moves a bar.

---

## 6. Spreadsheet-to-simulation method

Spreadsheets answer "on average, does it add up?". Simulation answers "for whom does it break, and how often?" Use both, in this order.

```
Step 1  Inventory     List every resource (contract economy.currencies) and every flow (sources, sinks, converters, gates, pools).
Step 2  Archetypes    Define 3–5 archetypes with share, sessions/day, minutes/session, skill, spend propensity, ad acceptance.
                      Start from soft-launch data when available; otherwise use conservative guesses and say so.
Step 3  Spreadsheet   Mean-field daily flows per archetype (§3.1). Compute net flow, balance at days 1/7/30, hoard days,
                      days to each pacing milestone, and content runway (days to finish all levels).
Step 4  Diagnose      Compare with targets. Fix the largest gap first, one lever at a time.
Step 5  Encode        Write the economy model JSON (economy-model.schema.json) in .gamestudio/economy/<name>.vN.economy.json.
Step 6  Validate      python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_json.py --auto .gamestudio/economy/
                      (or: python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py validate .gamestudio/economy/<file>)
Step 7  Simulate      python3 ${CLAUDE_PLUGIN_ROOT}/scripts/economy_sim.py --model <file> --runs 500 --seed 1 --days 60 --json --out .gamestudio/economy/<name>.vN.sim.json
Step 8  Read          Distributions, not means: p10/p50/p90 balances per archetype, hoard-day breaches, starvation,
                      cap overflow, conversion, days to complete content (see §7.6).
Step 9  Iterate       Change one lever, bump vN, re-run with the same seed, then with 2–3 other seeds.
Step 10 Record        Write the decision and numbers to .gamestudio/progress.md (gs.py progress "...") and update
                      contract economy.model_ref to the accepted model.
```

**Why Monte Carlo matters.** Means hide the failures that cause churn: the casual player who loses five levels in a row and cannot afford a continue; the lucky player who gets three rare drops and runs out of things to buy; affordability guards that stop a sink from firing (non-linear); caps that clip income. Run enough runs that p10 and p90 are stable (500 is a sensible default for a small model; increase until results stop moving between seeds).

**What the spreadsheet must contain** (one tab per archetype): inputs (behaviour assumptions), a row per node (fires/day, amount, probability, net), totals per resource, balance projection (day columns), and a targets block with pass/fail cells. Keep it as CSV beside the model if the team needs a human-readable artefact; the JSON model stays the source of truth.

---

## 7. Worked example: Lantern Lane

*Lantern Lane* is a hypothetical casual puzzle game used to demonstrate the method. All numbers are design inputs or the arithmetic that follows from them — not market benchmarks.

### 7.1 Inputs

| Parameter | Value |
|---|---|
| Minutes per level attempt | 2.5 |
| Win reward / loss consolation | 40 / 10 coins |
| Daily chest | 100 coins |
| Rewarded ad | 40 coins per view; offers per day: casual 3, engaged 4, payer 4 (client cap 10) |
| Continue (+5 moves) | 300 coins, taken on 25% of losses when affordable |
| Booster | 200 coins; bought 0.25/day (casual), 0.5/day (engaged), 1.5/day (payer) |
| Levels at launch | 300 |
| Targets | Hoard ≤ 3 days of income at day 30; median engaged player needs ≥ 60 days to finish content |

| Archetype | Share | Sessions/day | Min/session | Win rate | Ad accept |
|---|---|---|---|---|---|
| casual_free | 70% | 3 | 4 | 0.50 | 0.35 |
| engaged_free | 25% | 5 | 6 | 0.60 | 0.50 |
| payer | 5% | 6 | 8 | 0.62 | 0.20 |

### 7.2 Spreadsheet v1 (starting coins 500, no coin cost on decoration)

| Archetype | Attempts/day | Wins | Losses | Ads | Coin income/day | Coin spend/day | Net/day | Balance day 30 | Hoard days | Days to finish 300 levels |
|---|---|---|---|---|---|---|---|---|---|---|
| casual_free | 4.8 | 2.40 | 2.40 | 1.05 | 262 | 230 | +32 | 1,460 | 5.6 | 125 |
| engaged_free | 12.0 | 7.20 | 4.80 | 2.00 | 516 | 460 | +56 | 2,180 | 4.2 | 42 |
| payer | 19.2 | 11.90 | 7.30 | 0.80 | 681 | 847 | −166 | (tops up via IAP) | — | 25 |

Derivation for engaged_free: attempts = 5 × 6 / 2.5 = 12; income = 7.2 × 40 + 4.8 × 10 + 100 + 2.0 × 40 = 288 + 48 + 100 + 80 = 516; spend = 4.8 × 0.25 × 300 + 0.5 × 200 = 360 + 100 = 460.

### 7.3 Diagnosis

1. **Hoarding.** Both free archetypes breach the 3-day hoard target (5.6 and 4.2 days). The starting gift of 500 coins alone is ~1.9 days of casual income, and there is no elastic sink for surplus.
2. **Content runway.** The median engaged player wins 7.2 levels a day, about 50 levels a week, and finishes 300 levels in 42 days — below the 60-day target.
3. **Payers** run a deficit of 166 coins/day, which is the intended monetization surface (continues and boosters bought with purchased coins). Fine, as long as free players are not in deficit.

### 7.4 Spreadsheet v2 (one change per problem)

- Hoarding fix: starting coins 500 → 300, and each decoration task (one per star, one star per win) now costs 7 coins. This adds an inelastic, progress-linked sink that scales with play.
- Runway fix (content, not economy): either launch with 450 levels or commit to a cadence of ≥ 50 new levels per week. The economy should not slow players artificially to cover a content gap.

| Archetype | Coin income/day | Coin spend/day | Net/day | Balance day 30 | Hoard days | Areas completed in 30 days (20 stars each) |
|---|---|---|---|---|---|---|
| casual_free | 262 | 246.8 | +15.2 | 756 | 2.9 | 3.6 |
| engaged_free | 516 | 510.4 | +5.6 | 468 | 0.9 | 10.8 |
| payer | 681 | 930.5 | −249.4 | (IAP) | — | 17.9 |

Both free archetypes now pass the hoard target. Engaged free players hover around 450–500 coins, roughly one continue plus a booster: tight but not starving. The sim must confirm that p10 engaged players are not stuck below 300 coins for long stretches.

### 7.5 The model (schema-valid)

`.gamestudio/economy/lantern-lane.v2.economy.json` (validated against `economy-model.schema.json`):

```json
{
  "schema_version": "1.0",
  "name": "Lantern Lane v2 - hoard fix (start 300 coins, decor 7 coins per star)",
  "days": 60,
  "archetypes": [
    { "id": "casual_free",  "share": 0.70, "sessions_per_day": 3, "session_minutes": 4, "skill": 0.45, "spend_propensity": 0.004, "ad_accept_rate": 0.35 },
    { "id": "engaged_free", "share": 0.25, "sessions_per_day": 5, "session_minutes": 6, "skill": 0.60, "spend_propensity": 0.02,  "ad_accept_rate": 0.50 },
    { "id": "payer",        "share": 0.05, "sessions_per_day": 6, "session_minutes": 8, "skill": 0.62, "spend_propensity": 0.30,  "ad_accept_rate": 0.20 }
  ],
  "resources": [
    { "id": "coins", "initial": 300, "cap": null },
    { "id": "gems", "initial": 15, "cap": null },
    { "id": "decor_points", "initial": 0, "cap": null },
    { "id": "areas", "initial": 0, "cap": 25 },
    { "id": "boosters", "initial": 3, "cap": 99 }
  ],
  "nodes": [
    { "id": "win_reward", "kind": "source", "trigger": "per_level_win", "outputs": { "coins": 40 } },
    { "id": "loss_consolation", "kind": "source", "trigger": "per_level_loss", "outputs": { "coins": 10 } },
    { "id": "daily_chest", "kind": "source", "trigger": "daily", "outputs": { "coins": 100 } },
    { "id": "ad_reward", "kind": "source", "trigger": "on_ad", "outputs": { "coins": 40 }, "note": "Client caps at 10 per day." },
    { "id": "decor_task", "kind": "converter", "trigger": "per_level_win", "inputs": { "coins": 7 }, "outputs": { "decor_points": 1 } },
    { "id": "area_complete", "kind": "gate", "trigger": "per_session", "inputs": { "decor_points": 20 }, "outputs": { "areas": 1, "gems": 10 }, "condition": "decor_points >= 20" },
    { "id": "continue_buy", "kind": "sink", "trigger": "per_level_loss", "probability": 0.25, "inputs": { "coins": 300 }, "condition": "coins >= 300" },
    { "id": "booster_buy", "kind": "converter", "trigger": "per_session", "probability": 0.1, "inputs": { "coins": 200 }, "outputs": { "boosters": 1 }, "condition": "coins >= 200" },
    { "id": "booster_use", "kind": "sink", "trigger": "per_level_attempt", "probability": 0.15, "inputs": { "boosters": 1 }, "condition": "boosters >= 1" },
    { "id": "streak_gift", "kind": "source", "trigger": "per_level_win", "probability": 0.1, "outputs": { "boosters": 1 } }
  ],
  "levels": {
    "count": 300,
    "base_win_rate": 0.6,
    "difficulty_curve": { "type": "sawtooth", "params": { "base": 0.75, "floor": 0.40, "period": 10, "hard_every": 10 } }
  },
  "offers": [
    { "id": "starter_pack", "price_usd": 1.99, "contents": { "coins": 2000, "gems": 50, "boosters": 5 }, "trigger": "level >= 8" },
    { "id": "coins_m", "price_usd": 4.99, "contents": { "coins": 3000 }, "trigger": "per_level_loss" },
    { "id": "gems_m", "price_usd": 9.99, "contents": { "gems": 880 }, "trigger": "per_session" }
  ],
  "targets": { "days_to_complete_content": 60, "max_soft_currency_hoard_days": 3, "payer_conversion": 0.03 }
}
```

Modelling notes: the per-session booster probability 0.1 approximates 0.3–0.6 purchases a day across archetypes (the schema has one node for all archetypes; archetype differences come from sessions, skill and propensities). The star is spent immediately in play, so the model folds it into `decor_task` as a per-win converter. The difficulty curve parameters follow `difficulty_curve.py generate --pattern sawtooth` options.

### 7.6 Run and read

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_json.py --auto .gamestudio/economy/lantern-lane.v2.economy.json
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/economy_sim.py --model .gamestudio/economy/lantern-lane.v2.economy.json \
  --runs 500 --seed 1 --days 60 --json --out .gamestudio/economy/lantern-lane.v2.sim.json
# repeat with --seed 2 and --seed 3; results should agree within a few percent
```

Read the output (field names as the script reports them; see its `--help`) for:

| Question | Pass condition for Lantern Lane v2 |
|---|---|
| Soft-currency hoard vs `max_soft_currency_hoard_days` | p50 ≤ 3 days for both free archetypes; p90 ≤ 7 |
| Starvation | p10 engaged_free not below 300 coins (one continue) for more than ~2 consecutive days |
| Content runway vs `days_to_complete_content` | Median engaged player does **not** finish 300 levels before day 60 — v2 still fails this unless levels are added; the sim confirms the content decision, it cannot fix it |
| Conversion vs `payer_conversion` | Within ±50% of 0.03 given the propensities; otherwise revisit offer triggers |
| Gems | Free players earn ~10 gems per area (3.6–10.8 areas/month) → 36–108 gems/month: enough for an occasional refill, not enough to skip spending decisions |
| Cap overflow | No overflow on `boosters` (cap 99); if reported, raise the cap or lower `streak_gift` |

Decision recorded: "v2 accepted for soft-launch; content plan raised to 450 levels at launch; re-simulate after first soft-launch cohort replaces the archetype guesses."

---

## 8. Economy health metrics

| Metric | Definition | Healthy band (house heuristic) | Alarm | Typical fix |
|---|---|---|---|---|
| **Faucet/drain ratio (FDR)** | Currency created / destroyed, per cohort, per day | See §3.2 phase bands | Mature free cohort FDR > 1.2 for 2+ weeks | New elastic sink; trim a faucet |
| **Hoard days p50 / p90** | Balance / mean daily income | p50 ≤ 2–3, p90 ≤ 7 (soft, casual) | p50 rising week over week | New sinks; rotating shop |
| **Starvation rate** | Share of sessions with balance < cheapest essential sink | < 10–15% of sessions | > 25%, or concentrated in one level band | Raise rewards in that band; check difficulty spike |
| **Sink participation** | Share of DAU using each sink per week | Every major sink used by ≥ 20% of eligible players | A sink nobody uses | Reprice, reposition or remove |
| **Currency velocity** | Spend per day / average balance | Stable or rising | Falling (money sits idle) | Hoard interventions |
| **Basket index** | Hours of play to afford a fixed basket at each level (`currency-architecture.md` §6.3) | Flat or gently rising | Steep fall (inflation) or rise (wall) | Rescale prices or rewards |
| **Free vs bought hard currency** | Share of hard currency spent that was earned free | Stable; design-dependent | Free share climbing (payers hoarding free gems; promotions too generous) | Audit event and compensation faucets |
| **Unspent paid currency** | Total paid hard currency held by players | Track as a liability | Rising faster than revenue | Check sink appeal; check accounting |
| **Cap overflow** | Currency lost or blocked at caps | Low, explained | Players losing income overnight | Raise caps; notify before overflow |
| **Wealth concentration** | Gini or top-1% share of balances (trading economies) | Stable | Rising sharply | Bot/RMT detection; trade taxes |
| **Event inflation** | Core currency injected per event / daily core income | ≤ 1–3 days of income per event | Post-event balance never returns to baseline | Cap event payouts; event currency |
| **Payer conversion, ARPPU, ARPDAU** | Monetization outcomes of the economy | From `contract.analytics.kpi_targets` | Conversion falling after an economy change | Roll back; A/B test the change |

Benchmarks for retention and monetization KPIs live in `player-analytics` and `monetization`; this table covers the economy's internal health.

---

## 9. Economy telemetry

Every grant and spend must be logged. Minimum events (category `economy` in `event-taxonomy.schema.json`):

| Event | Required params | Notes |
|---|---|---|
| `currency_earned` | `currency`, `amount`, `source` (node id), `balance_after`, `level`, `transaction_id` | `source` must match an economy-model node id |
| `currency_spent` | `currency`, `amount`, `sink` (node id), `item_id`, `balance_after`, `level`, `transaction_id` | |
| `currency_overflow` | `currency`, `amount_lost`, `cap` | Only if overflow can happen |
| `shop_viewed` / `offer_shown` | `offer_id`, `placement`, `price_tier` | Joins economy and monetization funnels |
| `iap_purchase` | `product_id`, `price_local`, `currency_code`, `contents`, `transaction_id` | Validate server-side |
| `ad_reward_granted` | `placement`, `reward_currency`, `amount` | Joins ad and economy flows |

Generate the taxonomy and engine stubs with `event_taxonomy.py generate --contract .gamestudio/contract.json --out .gamestudio/analytics/taxonomy.json` and `event_taxonomy.py stubs`. Use node ids as `source`/`sink` values so live telemetry can be compared node-by-node with the sim.

---

## 10. The economy change protocol

1. **State the hypothesis** ("engaged free players hoard because there is no elastic sink; adding decoration coin costs will cut p50 hoard days from 4 to under 3 without reducing D7").
2. **Change one lever** in the model (`vN+1`), re-simulate with the same seeds, and record before/after.
3. **Prefer reward changes to price changes**, and **prefer new sinks to higher prices**. Players compare prices; they rarely audit rewards.
4. **Never nerf what players already own** (purchased items, earned currency). Grandfather or compensate.
5. **Ship behind remote config**, with an A/B test sized by `ab_test.py size --baseline P --mde D` on the primary KPI (D7 retention or conversion) and a guardrail (session length, churn).
6. **Watch the health metrics** for one full weekly cycle before judging; economies have lag.
7. **Roll back fast** if guardrails break; log the outcome in `progress.md` either way.

---

## 11. Balancing pitfalls

| Pitfall | Symptom | Prevention |
|---|---|---|
| Balancing on averages | Plan "works" but casual churns at level walls | Read p10 in the sim; simulate unlucky streaks |
| Unmodelled faucets | Live balances 2–5× the plan | Every grant path is a node; audit telemetry `source` values against node ids |
| Archetypes from imagination | Sim says fine, soft launch disagrees | Replace archetypes with soft-launch cohorts as soon as data exists |
| Fixing content gaps with economy friction | Players feel squeezed to "make levels last" | Solve runway with content cadence; keep economy honest |
| Tuning prices and rewards at once | Cannot attribute the result | One lever per iteration |
| Price hikes on live items | Community backlash | New sinks or new items instead |
| Ad rewards as the main faucet | Ads cannibalise IAP; non-ad players starve | Cap ad share of income (§5.2); see `ad-economy.md` |
| Event payouts in core currency | Post-event inflation | Event currencies with published end policy |
| Ignoring rounding | Converter arbitrage at specific amounts | Test conversions with exact integer rounding |
| Client-authoritative balances | Edited balances within days of launch | Server validation for anything purchasable |

---

## 12. Volatile facts (as of Oct 2026 — verify before relying)

- **Machinations** remains the dominant dedicated economy-design tool. It describes itself as a platform to describe, simulate and balance game economies and loops, advertises AI-assisted system building, publishes a LiveOps handbook, and lists studios such as Amazon Games, Wooga, Zynga, Big Fish, LEGO and Behaviour Interactive among users. Pricing tiers were not listed on the homepage, and a public headless-simulation API could not be confirmed — [machinations.io](https://machinations.io/).
- **No well-known open-source Python economy simulator** surfaced in October 2026 research; the alternatives listed were GUI tools (e.g., Flowtrix) — [AlternativeTo: Machinations alternatives](https://alternativeto.net/software/machinations). This is why the plugin ships its own Monte Carlo simulator driven by the same JSON model the game reads.
- **Simulation-led balancing in research**: RuleSmith (Feb 2026) combined multi-agent LLM self-play with Bayesian optimisation over a rule space and converged to balanced configurations on a simplified civ-like game — [arXiv:2602.06232](https://arxiv.org/abs/2602.06232). The studio pattern that follows: draft economy tables with the LLM, encode them as the JSON model, evaluate with simulated players, tune parameters with search; the LLM is for ideation, not the balance oracle (method recommendation, not a sourced result).
