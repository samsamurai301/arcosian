---
name: monetization
description: Senior monetization knowledge for games - business model choice, IAP and subscription implementation (StoreKit 2, Play Billing, RevenueCat), ad mediation and placements, offer design, battle passes, loot-box law, odds disclosure, minors, and payments rules. Use when asked to pick a business model, design IAP, add ads, price offers, build a battle pass, or check monetization ethics.
when_to_use: Choosing, implementing, tuning or auditing how a mobile game earns money.
---

# Monetization

## What this skill gives you
- A decision framework for choosing premium, F2P, ad-supported, hybrid or subscription models from the game's loop, audience and genre.
- An implementation map for purchases: StoreKit 2, Google Play Billing, RevenueCat, server-side validation and entitlements.
- Ad monetization practice: mediation choice, placements, frequency, consent (UMP, ATT) and kids/families policy.
- Offer design and measurement: starter packs, pass design, price ladders, tests, guardrails.
- Regulation and ethics: loot-box law, odds disclosure, refunds, virtual-currency consumer protection, minors, red lines.
- The 2026 payments landscape (link-outs, alternative billing, web shops), clearly flagged as volatile.

## Core models

### 1. Revenue is a function of the loop, not a bolt-on
Money should attach to a need the core loop already creates: time (skip, speed), power (progress), expression (cosmetics), access (content, pass), or convenience (remove friction, remove ads). Design the monetized resource in `economy-design` first; then choose products. If you cannot say which loop tension a product relieves, it is a dark pattern waiting to happen or dead inventory.

### 2. The revenue identity
`Revenue = installs x (ad ARPDAU_ads + payer% x ARPPU) x retained days`. In practice work with these levers:
- Reach: installs and retention (the multiplier on everything). See `marketing-ua`, `player-analytics`.
- Conversion: share of users who ever pay (payer conversion) and how fast (D0/D1/D7 conversion).
- Depth: spend per payer (ARPPU), driven by price ladder, repeat purchase and whales/dolphins/minnows distribution.
- Ads: impressions per DAU x eCPM / 1000, bounded by retention damage.
- Cost side: store commission, payment processing, taxes, refunds and chargebacks.
Use `${CLAUDE_PLUGIN_ROOT}/scripts/retention_ltv.py` to turn retention curves and ARPDAU into LTV and break-even CPI.

### 3. Model selection table
| Model | Fits | Needs | Watch out |
|---|---|---|---|
| Premium (paid up front) | Finite, high-polish, niche, narrative or puzzle | Strong store page, reviews, price anchoring | Tiny reach on mobile; no UA budget possible |
| Premium + optional IAP | Same, with expansions | Content cadence | Feels like a bait if gated badly |
| Ads only (hyper-casual) | Very short sessions, huge reach | Cheap installs, many impressions | Retention decay, ad fatigue, low LTV ceiling |
| IAP F2P | Mid and hardcore, collection, 4X, RPG | Deep economy, live-ops | Whale dependency, ethics exposure |
| Hybrid (ads + IAP) | Casual and hybrid-casual, puzzle, idle | Meta layer that gives IAP something to sell | Ad/IAP cannibalization if poorly segmented |
| Subscription | Utility-like or daily-habit games, pass-like value | Recurring value, content cadence | Churn, store scrutiny, trial abuse |
| Season pass | Any live game with cadence | Seasons, reward track, calendar | Pass fatigue if overlaid with too many tracks |
Rule: pick the simplest model that the loop can carry; add layers only after the first one is proven in soft launch.

### 4. The payer pyramid
Roughly: most players never pay; a small minority pays; a tiny fraction carries a large share of revenue. Do not quote a fixed ratio; measure your own. Design implications: (a) first purchase is a different product from the tenth, (b) price ladder must have rungs from the lowest tier to high tier, (c) spending caps and cool-offs are an ethical and legal safeguard, not just a nicety.

### 5. Guardrail metrics beat revenue metrics
Every monetization test needs guardrails: D1/D7 retention, session length, progression pace, refund rate, support tickets, review sentiment. A change that lifts ARPDAU and drops D7 is usually a loss.

## Decision procedures

### A. Choose a business model (30-minute procedure)
1. Write the session shape (length, frequency) and the loop's scarce resources.
2. Estimate audience geography mix: mature markets lean IAP, many emerging markets lean ads (see volatile facts in `references/payments-landscape-2026.md` and research notes).
3. Estimate retention potential by genre benchmark (use `genre-playbooks`).
4. Compute the break-even CPI window for each candidate model with `retention_ltv.py`; if LTV cannot beat plausible CPI, the model is wrong or the game is not UA-viable (organic, premium, or niche).
5. Pick the model; list what it requires from design (meta layer, events, pass). Record in the design contract.

### B. Ship a first purchase flow
1. Define SKUs: consumables (currency packs), non-consumables (remove ads, unlock), subscriptions (VIP, pass).
2. Use RevenueCat or native StoreKit 2 + Play Billing; see `references/business-models-and-implementation.md`.
3. Server-authoritative grants: validate receipts on your backend, grant by transaction id, make grants idempotent.
4. Handle restore, pending purchases (Play), Ask to Buy / family sharing, refunds and revocation.
5. Test in sandbox/test tracks including interrupted purchases, offline, duplicate delivery.
6. Add telemetry: offer_shown, purchase_started, purchase_completed, purchase_failed (with reason), refund (see `${CLAUDE_PLUGIN_ROOT}/scripts/event_taxonomy.py`).

### C. Add ads without wrecking retention
1. Prefer rewarded video (opt-in) as the primary format; interstitials only at natural breaks.
2. Never show interstitials in the first session or before the first meaningful win.
3. Cap frequency per session and per time window; A/B the caps against retention.
4. Integrate consent first (UMP on both platforms, ATT on iOS when tracking), then the mediation SDK.
5. Set age flags before SDK init for any audience that includes minors.
6. Monitor ad revenue per DAU against D1/D7 by cohort.

### D. Design an offer (see `references/offers-regulation-ethics.md`)
Trigger -> value statement -> price -> scarcity honesty -> expiry -> measurement. Segment by payer state (non-payer, first-time, payer, lapsed). Offers may not exploit emotional states (loss, frustration after fail streaks) in manipulative ways.

### E. Pre-launch monetization audit checklist
- Odds shown before purchase for every randomized paid item; stored and logged.
- No real-money path to unlimited spend without limits for minors; parental gate where required.
- Currency shown in real price equivalents where required by law; no obscuring pricing via multi-layer currencies.
- Refund and support path documented; entitlement revocation handled.
- Ad SDK configuration matches the declared audience and store questionnaires.
- Region toggles for restricted loot boxes (see legal-ethics and compliance preflight).
Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/compliance_preflight.py` before ship.

## Mobile specifics
- Store commission, taxes and platform rules differ per region and change; treat them as config, not constants.
- One-handed, interruptible sessions mean purchase flows must survive app kill and network loss.
- iOS: ATT prompt timing affects ad revenue; prompt after the player has experienced value, with a pre-prompt explanation.
- Android: pending purchases and acknowledgement deadlines; unacknowledged purchases get refunded automatically.
- Low-end devices: ad SDK memory and startup cost counts toward performance budgets (`mobile-performance`).
- Prices should localize through store price tiers, not hand-converted currency numbers.

## Anti-patterns
| Anti-pattern | Detect | Fix |
|---|---|---|
| Pay-to-skip a wall created for that purpose | Difficulty spike aligned with offer trigger | Smooth the curve; offers must help, not manufacture pain |
| Currency obfuscation (gems at awkward bundle sizes) | Packs never divide into item prices | Align pack sizes to price points, show real equivalents |
| Interstitial after every level | Ad count/session high, D1 low | Cap and place at natural breaks; use rewarded |
| Client-side purchase granting | Grants occur before validation | Server-side validation, idempotent |
| Unannounced odds changes | No odds versioning | Version and publish odds; log what each player saw |
| Fake scarcity timers that reset | Same offer per user every day | Honest expiry or no timer |
| Targeting minors or detected problem spenders | Spend spikes on young accounts | Caps, cooling-off, suppress offers, review policies |
| Subscription without value cadence | Cancel after first month | Define weekly value; show renewal clearly |

## Using the ontology
Products are sinks and sources in the resource graph (`game-ontology`): map each SKU to the resource flow it injects (premium currency source, soft-currency converter, time-skip sink). Model pools and gates in `${CLAUDE_PLUGIN_ROOT}/scripts/economy_sim.py` to test inflation from purchases. Use `gacha_calc.py` for randomized item odds and pity design. Record the business model and SKU list in `.gamestudio/` project state via `gs.py`. Use `ab_test.py` for sample sizes and significance on offer tests.

## Reference library
| File | Contains | Read when |
|---|---|---|
| `references/business-models-and-implementation.md` | Models in depth, StoreKit 2, Play Billing, RevenueCat, validation, ad mediation, placements, frequency, consent, families policy | Implementing purchases or ads, choosing a model |
| `references/offers-regulation-ethics.md` | Offer design and measurement, loot-box laws, odds disclosure, refunds, virtual-currency rules, minors, red lines | Designing offers, preparing compliance review |
| `references/payments-landscape-2026.md` | EU DMA terms, US link-outs, commissions, web shops (volatile) | Deciding about alternative payments or web shop |

## Related skills
- `economy-design`: currencies, sinks, sources, inflation; the foundation for any SKU.
- `player-psychology`: motivation and ethical persuasion limits.
- `player-analytics`: KPIs, cohorts, LTV and test analysis.
- `legal-ethics`: wider legal context (privacy, age, licensing).
- `store-release`: store listing, review guidelines, IAP review submission.
- `liveops`: events, passes and offers as a calendar.
- `marketing-ua`: CPI and ROAS targets that LTV must beat.
- `genre-playbooks`: genre-specific monetization patterns.
