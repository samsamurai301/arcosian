---
name: economy-design
description: 'Game economy codex: currency architecture (soft, hard, premium, energy, event, material), sources and sinks, inflation and hoarding, sim-based balancing with economy_sim.py, price ladders, offers, passes, gacha maths and pity, loot-box law, ad economics, and patterns from landmark games. Use when asked to "design the economy", "add a currency", "balance sinks", "price the shop", "design a banner" or "why are players hoarding".'
when_to_use: 'Designing or reviewing currencies, shops, offers, passes, gacha or ad rewards; running a balance pass; diagnosing hoarding, starvation or inflation from sim or telemetry.'
---

# Economy Design

The economy is the set of rules by which resources enter the game, change form, wait and leave. It sets the pace of progress, gives choices weight and is where nearly all monetization attaches — which is why it needs the most care. An economy that inflates kills goals, one that starves kills fun, and one tuned to extract spend kills trust. This skill gives the studio a complete, numerate method: decide the currency architecture, model every flow in the ontology, balance it with spreadsheets and then Monte Carlo simulation, price it honestly, add randomness and ads only where they serve the player, and keep it healthy after launch.

## What this skill gives you

- **Currency architecture**: the one-job rule, the seven ontology kinds, single/dual/multi layouts, time-anchored exchange rates, arbitrage-proof conversion guards, naming and presentation rules, inflation, caps, hoarding and regional pricing (`references/currency-architecture.md`).
- **Balancing method**: Machinations-style flow modelling, a sink taxonomy, earn-rate targets set backwards from pacing, the ten-step spreadsheet-to-simulation workflow ending in `economy_sim.py`, a fully worked schema-valid model, and economy health metrics (`references/sources-sinks-balancing.md`).
- **Pricing and offers**: price ladders with a computed bonus curve, the value-ratio formula, first purchase, starter packs, limited-time and personalised offers, piggy banks, bundles, subscriptions, pass economics and hard ethical guardrails (`references/pricing-and-offers.md`).
- **Gacha and loot maths**: exact expected-value and percentile tables for seven banner configurations, pity, rate-up, spark, duplicate protection, free-player generosity targets, statistical verification, and the disclosure regimes of the major markets (`references/gacha-and-loot.md`).
- **Ad economics**: rewarded placements as value exchange, interstitial caps, ad ARPDAU and ad LTV, IAP/ads cannibalisation tests and the ad-free price floor (`references/ad-economy.md`).
- **Case patterns**: the economic structure of Clash Royale, Royal Match, Coin Master, Monopoly Go, Hay Day, Genshin Impact, idle games and pass systems, with an analogy method for transplanting patterns (`references/economy-case-patterns.md`).

## Core models

These rules settle most economy decisions. Details, formulas and sources are in the references.

### 1. Every currency has exactly one job
Pace (soft), scarcity/premium (hard, premium), session gating (energy), isolation (event), mastery record (XP) or specificity (material). If a proposed currency's job could be done by an existing one, merge it. Keep the visible HUD to 1–3 currencies for casual audiences. (`currency-architecture.md` §1–3)

### 2. Model every flow or it will surprise you
Sources, sinks, converters, gates and pools, each with a trigger, are the ontology's vocabulary (`economy-model.schema.json`). Unmodelled faucets — compensation gifts, friend gifts, promo codes, event payouts, ad rewards — are the main reason launched economies diverge from plan. If it grants or removes a resource, it is a node.

### 3. Balance in three phases
Faucet/drain ratio for soft currency: generous onboarding (≈1.3–2.0 in days 0–2), small surplus in growth (≈1.0–1.2), near-equilibrium at maturity for free players (≈0.9–1.05). Payers running below 1.0 is the monetization surface; free players running below 1.0 is starvation. (`sources-sinks-balancing.md` §3)

### 4. Pair every engine with an escalating master sink
Income that grows with progress must meet prices that grow at the same rate (upgrade curves, escalating villages and boards, capacity upgrades, exponential generator costs). Inflation is harmless when the master sink escalates with it and fatal when prices are flat. (`economy-case-patterns.md` §10)

### 5. Hold an inelastic and an elastic sink for every soft currency
Inelastic sinks (progression, capacity) absorb median income; elastic sinks (cosmetic, consumable, convenience, collection) absorb surplus from engaged and paying players. Missing elastic sinks produce hoarding; missing inelastic sinks mean nobody needs to spend. (`sources-sinks-balancing.md` §4)

### 6. Anchor value to time and publish a reference price
One hard-currency unit should equal a stated number of minutes of median play income. Every offer's value claim is computed from a published reference price per unit: `value_ratio = Σ quantity × ref_usd / price`. (`currency-architecture.md` §4.2; `pricing-and-offers.md` §3)

### 7. Conversions must lose value around every cycle
For any cycle of exchanges, the product of rates must be below 1 after real integer rounding; check it automatically (negative-cycle detection on −log rates). Soft → hard conversion is almost never allowed, and only with hard caps. (`currency-architecture.md` §4.4)

### 8. Read distributions, not averages
Spreadsheets say whether it adds up on average; Monte Carlo says for whom it breaks. Judge p10/p50/p90 balances per archetype, hoard-day breaches, starvation stretches and cap overflow — and re-run with several seeds. (`sources-sinks-balancing.md` §6)

### 9. Pity fixes the tail more than the mean
For a 0.6% top-tier rate, pity at 90 with soft pity from 74 cuts expected pulls from 167 to 62.3, but cuts p99 from 766 to 83. Always disclose base and consolidated rates, pity, guarantee and the worst-case real-money cost. (`gacha-and-loot.md` §3–4)

### 10. Ads are a capped faucet, not a replacement for play or purchases
Rewarded ads are opt-in exchanges that give players far more reference value than the developer earns per view; the guard is a daily ceiling (≤ 15–20% of a free player's soft income, and below the value of the cheapest relevant IAP). Interstitials cost retention: none in the FTUE, minimum intervals, never after purchases. (`ad-economy.md` §3–4)

### 11. Transparent first (doctrine 8)
Direct purchase, passes and fixed bundles are the default; paid randomness needs a reason, a deterministic path to every item, full disclosure and per-storefront/age flags. Real-money prices visible, real scarcity only, no targeting of minors or vulnerability signals, no leftover-currency traps. (`pricing-and-offers.md` §14; `gacha-and-loot.md` §1, §11)

### Rules of thumb (starting points; verify by sim and test)

| Topic | Starting rule | Source of truth |
|---|---|---|
| Spendable currencies at launch (casual) | 2–4, 1–2 on the HUD | `currency-architecture.md` §1 |
| Soft-currency hoard (casual) | p50 ≤ 2–3 days of income, p90 ≤ 7 | `sources-sinks-balancing.md` §3.3 |
| Next meaningful purchase | Affordable within 1–3 sessions | `sources-sinks-balancing.md` §5 |
| One level/loop reward | 5–20% of the next common sink | `sources-sinks-balancing.md` §5.2 |
| Ad share of free players' soft income | ≤ 15–20% | `ad-economy.md` §3.2 |
| Speed-up pricing | Concave: `gems = ceil(k × minutes^a)`, 0.5 ≤ a ≤ 0.85 | `currency-architecture.md` §4.3 |
| Currency-pack bonus at the top tier | +20% to +40% vs entry rate, monotonic | `pricing-and-offers.md` §2.2 |
| Starter pack | 3–5× value at an entry price, once per account | `pricing-and-offers.md` §5 |
| Season pass | 5–10× value at full completion; median engaged buyer finishes with 15–25% of the season spare | `pricing-and-offers.md` §11 |
| Free gacha generosity | One featured item every 2–5 banners for a committed free player | `gacha-and-loot.md` §8 |
| 10-pull | Guarantee ≥ 1 high-tier result | `gacha-and-loot.md` §2.3 |
| Energy | Time-to-full ≈ typical gap between sessions; wins never consume lives | `currency-architecture.md` §11 |
| Event payout of core currency | ≤ 1–3 days of core income per event | `currency-architecture.md` §10 |
| Interstitials | First after 2–3 sessions or 5–10 min of play; 60–180 s minimum interval | `ad-economy.md` §4 |

## Decision procedures

### A. Design a new economy (from the design contract)
1. Read the contract's pillars, loops, session target and `monetization_model`. Load `design-theory` if the core loop is not yet one sentence.
2. Pick the architecture with the decision table in `currency-architecture.md` §3.2. Write each currency with the one-job test.
3. Write the **pacing table**: milestones and the session/day each archetype should reach them (`sources-sinks-balancing.md` §5.1). Pull progression curves from `progression-difficulty` (`progression_calc.py curve ...`).
4. List every source and sink per currency, with triggers; ensure each soft currency has an inelastic and an elastic sink.
5. Define 3–5 archetypes (share, sessions/day, minutes, skill, spend propensity, ad acceptance). Mark guesses as guesses.
6. Build the mean-field spreadsheet; compute net flow, hoard days, days to milestones and content runway.
7. Fix the largest gap with one lever; repeat until targets pass.
8. Encode `.gamestudio/economy/<name>.v1.economy.json`; validate; run `economy_sim.py`; read p10/p50/p90 (§6–7 of the balancing reference).
9. Write `contract.json → economy.currencies[]` and `economy.model_ref`; log the decision with `gs.py progress`.
10. Hand the model to the `critic` agent and, if monetized, to `monetization-designer` and `compliance-officer`.

### B. Add a currency or resource to a live game
1. One-job test; if it fails, use an existing currency or a material.
2. Define sources, sinks, cap, overflow behaviour and (for event currencies) the end-of-event policy.
3. Add conversion edges and re-run the arbitrage cycle check with real rounding.
4. Add nodes to the model; simulate before/after with the same seeds.
5. Plan its tutorial moment and UI placement with `mobile-ux`.
6. Ship behind remote config; watch the health metrics for a full weekly cycle.

### C. Balance pass (hoarding, starvation, inflation)
1. Pull telemetry: hoard days p50/p90, starvation rate, FDR per cohort, sink participation, basket index (`sources-sinks-balancing.md` §8).
2. Locate the problem by archetype and level band; check whether a difficulty spike is the real cause (`progression-difficulty`, `difficulty_curve.py analyze`).
3. Hypothesis → one lever: prefer new sinks over price rises, and reward changes over price changes; never nerf owned items.
4. Re-simulate; A/B test with `ab_test.py size` for sample size and a retention guardrail; roll out; record. The `balance` process skill (`/arcosian:balance`) runs this as the `balance-pass` workflow.

### D. Design the shop and offers
1. Fix the reference price per currency; build the ladder with a monotonic bonus curve (`pricing-and-offers.md` §2).
2. Check common hard-currency prices against pack sizes (no leftover traps).
3. Design first purchase and starter pack (3–5×), then the offer ladder (one tier up after purchase, one down after ignores).
4. Add pass and/or monthly card; compute full and realised value ratios; check completion pacing by archetype.
5. Add every offer to the model's `offers[]` and simulate conversion against `targets.payer_conversion`.
6. Run the dark-pattern detector (`pricing-and-offers.md` §14) on screenshots of every shop screen.

### E. Design a gacha banner (only after `gacha-and-loot.md` §1 says yes)
1. Choose the target expected and worst-case pulls for the featured item from the free-generosity target (2–5 banners).
2. Set base rate, soft/hard pity, featured share and guarantee; compute with `gacha_calc.py`; compare with the reference table (§3.2).
3. Convert to real-money ranges at entry and best pack rates; put them on the info page.
4. Add spark or byproduct exchange; duplicate conversion at published rates; no set-completion prizes.
5. Configure per-storefront and per-age flags; get `compliance-officer` sign-off; run `compliance_preflight.py`.

### F. Add or retune ad placements
1. List placements with reward, daily cap and cannibalisation risk (`ad-economy.md` §3.1).
2. Size rewards against the daily ceiling; add `on_ad` nodes and `ad_accept_rate` to the model.
3. Set interstitial `first_after_sec` and `min_interval_sec`; suppress for payers.
4. Test against a holdout on total revenue per user and D7 retention, not ad ARPDAU alone.
5. Price "Remove Ads" above the floor (`ad-economy.md` §7.1).

### G. Economy review checklist (fast pass before any milestone)
- [ ] Every currency passes the one-job test; counts within budget.
- [ ] Every flow is a node in the model; telemetry `source`/`sink` values equal node ids.
- [ ] Sim run with ≥ 3 seeds; hoard, starvation, runway and conversion targets pass for every archetype.
- [ ] No arbitrage cycles; server-authoritative balances for anything purchasable.
- [ ] Shop: real-money prices, computed value labels, no fake scarcity, no leftover traps.
- [ ] Randomness: odds, pity, worst-case cost disclosed; regional/age flags; deterministic path.
- [ ] Ads: daily caps; no FTUE interstitials; payer suppression.

## Mobile specifics

- **Short sessions (1–5 minutes)** mean every session must end with visible progress and, ideally, "almost enough" for the next purchase; tune reward sizes to the session, not to the hour.
- **Interruptions and absence**: energy fills rather than decays; offline earnings are capped generously; caps never silently destroy overnight income.
- **One currency icon per tier at thumb-glance size**: distinct silhouettes at 24 px, consistent across HUD, shop, rewards and odds pages.
- **Store-rendered prices**: always use the localised price string from the store APIs; never hard-code currency symbols.
- **Platform rules shape design**: both stores require odds disclosure for paid random items; subscriptions need ongoing value; family and age features restrict purchases by minors (see volatile facts in the references).
- **Commission and channel variation**: net revenue per pack differs by programme, region and payment channel (IAP, alternative billing, web shop); recompute value and floors per channel.
- **Ad-led regions**: where IAP conversion is structurally low, keep contents identical and lean on rewarded ads and low entry prices rather than cutting the whole ladder.
- **Low-end devices and offline play**: economy state must be server-authoritative for purchasable goods but tolerant of offline sessions (queue grants with transaction ids; reconcile on reconnect).

## Anti-patterns

| Anti-pattern | Detection | Fix |
|---|---|---|
| Currency bloat | More than the complexity budget; two currencies with the same sinks | Merge; convert to materials |
| Unmodelled faucets | Live balances far above the sim | Audit telemetry sources against node ids |
| Balancing on averages | Plan passes, casual players churn at walls | Read p10; simulate unlucky streaks |
| Flat prices with growing income | Basket index falling; hoard days rising with level | Scale prices; add escalating master sink |
| Event payouts in core currency | Post-event balances never return to baseline | Event currency with published end policy; payout cap |
| Converter arbitrage | Players with impossible balances | Cycle check with real rounding; server authority |
| Economy friction to cover content gaps | Engaged players finish content early; prices raised to slow them | Content cadence (levels per week ≥ burn rate) |
| Hidden or obscured real-money cost | Multi-step currency chains; per-day-only prices | One intermediate step max; real-money ranges shown |
| Fake scarcity or fake "was" prices | Countdowns that reset; strikethroughs never charged | Real end times; computed value labels |
| Paid randomness without pity or disclosure | No odds page; unbounded worst case | Pity/spark, disclosure, deterministic path, flags |
| Uncapped rewarded ads | Ad share of income > 20%; IAP conversion falls | Daily caps; holdout test |
| Nerfing owned items | Community backlash after balance pass | Grandfather or compensate; add new sinks instead |

## Using the ontology

**Contract fields** (`.gamestudio/contract.json`):
- `economy.currencies[]` — `id`, `kind` (`soft|hard|premium|energy|event|xp|material`), `sources`, `sinks`, `cap`; and `economy.model_ref` → the accepted economy model path.
- `monetization.iap[]` (`id`, `type`, `price_tier`, `contents`), `monetization.ads.rewarded` (placements) and `monetization.ads.interstitial` (`min_interval_sec`, `first_after_sec`), `monetization.pass`, `monetization.ethics` (rules).
- `analytics.kpi_targets` (`payer_conversion`, `arpdau_usd`, retention) as the economy's outcome targets.

**Economy model** (`${CLAUDE_PLUGIN_ROOT}/scripts/schemas/economy-model.schema.json`, files in `.gamestudio/economy/*.economy.json`): `archetypes`, `resources` (`initial`, `cap`), `nodes` (`kind` source/sink/converter/gate/pool, `trigger`, `inputs`, `outputs`, `probability`, `condition`), `levels`, `offers`, `targets` (`days_to_complete_content`, `max_soft_currency_hoard_days`, `payer_conversion`). Resource ids must match contract currency ids. A worked, validated model is in `references/sources-sinks-balancing.md` §7.5; the plugin's example is `${CLAUDE_PLUGIN_ROOT}/scripts/schemas/examples/example.economy-model.json`.

**Deconstructions** map a game's economy into `deconstruction.schema.json → economy {currencies, sources, sinks}` (`references/economy-case-patterns.md` §1). **Event taxonomy**: economy events use category `economy` (`currency_earned`, `currency_spent` with node ids as `source`/`sink`).

**Scripts** (exact command lines):

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_json.py --auto .gamestudio/economy/
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py validate .gamestudio/economy/<name>.vN.economy.json
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/economy_sim.py --model .gamestudio/economy/<name>.vN.economy.json --runs 500 --seed 1 --days 60 --json --out .gamestudio/economy/<name>.vN.sim.json
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gacha_calc.py --rate 0.006 --soft-pity-start 74 --soft-pity-step 0.06 --hard-pity 90 --rate-up 0.5 --guarantee --pulls 180 --json
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/progression_calc.py curve --formula exp --levels 50 --base 100 --growth 1.15 --json
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/difficulty_curve.py generate --levels 60 --pattern sawtooth --base 0.85 --floor 0.45 --period 10 --hard-every 10 --json
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ab_test.py size --baseline 0.15 --mde 0.01 --alpha 0.05 --power 0.8
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/retention_ltv.py ltv --points "1:0.40,7:0.15,30:0.06" --arpdau 0.037 --horizon 365 --json
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/event_taxonomy.py generate --contract .gamestudio/contract.json --out .gamestudio/analytics/taxonomy.json
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/compliance_preflight.py --project . --platform all --json
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py kb "soft pity" --skill economy-design
```

**Agents and workflows:** `arcosian:systems-designer` owns economy models and balance passes; `arcosian:monetization-designer` owns ladders, offers and passes; `arcosian:data-analyst` replaces archetype guesses with cohorts and runs A/B analysis; `arcosian:compliance-officer` signs off paid randomness and regional flags; `arcosian:critic` attacks the model before approval. Run `/arcosian:balance` (workflow `balance-pass`) for tuning and `/arcosian:design-review` for multi-discipline review.

## Reference library

| File | What it contains | When to read it |
|---|---|---|
| `references/currency-architecture.md` | One-job rule; ontology currency kinds; single/dual/multi layouts; time-anchored exchange rates; speed-up pricing; arbitrage cycle check; naming and psychology with ethical limits; inflation, caps, hoarding; premium and event currencies; energy; materials; regional pricing; spec template | Before adding or changing any currency; when balances drift; when designing the HUD or shop presentation |
| `references/sources-sinks-balancing.md` | Flow model and feedback patterns; faucet/drain accounting and phase targets; sink taxonomy; earn-rate targets; spreadsheet-to-simulation method; worked Lantern Lane example with a schema-valid model and `economy_sim.py` usage; health metrics; telemetry; change protocol | Designing a new economy; every balance pass; reading sim output or live economy telemetry |
| `references/pricing-and-offers.md` | Price ladders and bonus curves; reference price and value ratio; first purchase; starter packs; LTOs; personalised offers and the offer ladder; piggy banks; bundles and chains; subscriptions and VIP; pass economics; regional pricing; offer measurement; ethical guardrails; offer spec template | Building or reviewing the shop, offers, passes or subscriptions; checking value claims |
| `references/gacha-and-loot.md` | When to use paid randomness; rarity and pools; EV and percentile tables; pity, rate-up, spark; duplicate protection and coupon-collector maths; free generosity; chests; statistical verification; disclosure regimes (platforms, China, Korea, Japan, Belgium, Netherlands, Brazil, others); transparent alternatives | Before any banner, chest or random reward sold for money; compliance review of random items |
| `references/ad-economy.md` | Ad formats' economy roles; rewarded value exchange and caps; interstitial frequency caps; ad ARPDAU and ad LTV maths; IAP/ads cannibalisation and holdout tests; ad-free price floor; consent and child-directed basics; telemetry | Designing ad placements, hybrid monetization, or pricing "Remove Ads" |
| `references/economy-case-patterns.md` | Economy deconstructions of Clash Royale, the casual-puzzle lineage to Royal Match, Coin Master, Monopoly Go, Hay Day, Genshin Impact, idle games and pass systems; cross-case comparison; analogy method for transplanting patterns | Looking for a proven structure; deconstructing a competitor; borrowing a pattern safely |

## Related skills

- `game-ontology` — the shared vocabulary and schemas the economy model uses.
- `progression-difficulty` — cost and XP curves, difficulty curves and walls that the economy must match.
- `monetization` — store implementation, IAP products, ad mediation setup and monetization strategy.
- `liveops` — event calendars, segmentation and remote config that drive event economies.
- `player-analytics` — cohorts, KPIs, retention and LTV models that replace archetype guesses.
- `player-psychology` — motivation, reward schedules and the ethical limits of persuasion.
- `legal-ethics` — loot-box law, consumer protection, minors and virtual-currency rules in depth.
- `mechanics-codex` — mechanic cards for currencies, energy, chests, pity, rate-up and spark.
- `genre-playbooks` — genre-specific economy scaffolds (merge, idle, farming, RPG gacha, social casino).
- `game-case-studies` — full deconstructions beyond the economy layer.
- `design-theory` — loops, decisions and the diagnostic checklist (economy section E01–E12).
- `analogy-engine` — the method for transplanting patterns between games.
- `mobile-ux` — shop, offer and HUD presentation on phones.
- `marketing-ua` — CPI and UA economics that LTV must cover.
