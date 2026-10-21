# Pricing and Offers

Pricing turns the economy's scarcity into revenue. Done well, it gives every willingness-to-pay segment a fair, clearly valued option and leaves non-payers with a complete game; done badly, it hides costs, pressures minors and burns trust. This file covers the economics of the shop as the economy designer sees it: price ladders and value curves, value framing and the value-ratio maths, first purchase and starter packs, limited-time and personalised offers, piggy banks, bundles and chains, subscriptions and VIP, battle/season pass economics, regional pricing, offer measurement, and the ethical guardrails that are non-negotiable under doctrine 8. Store implementation (StoreKit 2, Play Billing, RevenueCat, receipts) lives in `monetization` and `store-release`; currency structure lives in `currency-architecture.md`.

## Contents

1. [Principles](#1-principles)
2. [Price ladders](#2-price-ladders)
3. [Value framing and the value ratio](#3-value-framing-and-the-value-ratio)
4. [First purchase](#4-first-purchase)
5. [Starter packs](#5-starter-packs)
6. [Limited-time offers](#6-limited-time-offers)
7. [Personalised offers](#7-personalised-offers)
8. [Piggy banks](#8-piggy-banks)
9. [Bundles, chains and progression packs](#9-bundles-chains-and-progression-packs)
10. [Subscriptions, monthly cards and VIP](#10-subscriptions-monthly-cards-and-vip)
11. [Pass economics](#11-pass-economics)
12. [Regional pricing](#12-regional-pricing)
13. [Measuring offers](#13-measuring-offers)
14. [Ethical guardrails](#14-ethical-guardrails)
15. [Offer spec template](#15-offer-spec-template)
16. [Volatile facts](#16-volatile-facts-as-of-oct-2026--verify-before-relying)

---

## 1. Principles

1. **Spend is heavy-tailed.** In F2P, a small share of players produces most IAP revenue. The ladder must serve the first-time $1–5 buyer, the regular $10–30/month buyer and the rare high spender — without designing the game around extracting from the last group.
2. **The economy creates value; the shop only prices it.** If the soft and hard currencies have no meaningful sinks, no price will work. Fix `sources-sinks-balancing.md` problems before touching prices.
3. **Sell time, expression, convenience and access — not frustration.** A purchase should feel like a shortcut or a gift to oneself, not ransom.
4. **Every price is honest.** Real-money prices are shown; value claims are computed from a published reference; scarcity is real.
5. **Non-payers are the audience payers play with.** Ads, social and competitive modes need them. A generous free experience is a monetization asset.
6. **Test, don't guess.** Prices and offers are remote-configured and A/B tested with guardrail metrics (`ab_test.py`).

---

## 2. Price ladders

### 2.1 Price points

Mobile stores price on a grid. In USD the conventional F2P ladder uses $0.99, $1.99, $2.99, $4.99, $9.99, $19.99, $49.99 and $99.99. Five to seven currency SKUs is typical; more creates choice paralysis.

### 2.2 The bonus curve

Larger packs give more currency per dollar. The bonus must be **monotonic** (never a worse rate at a higher price) and **moderate** (if the top pack is twice as good per dollar, small packs feel like a rip-off and anchor resentment).

Hypothetical "Gems" ladder (used across this skill):

| Price (USD) | Gems | Gems per $ | Bonus vs $0.99 rate | USD per 100 gems |
|---|---|---|---|---|
| 0.99 | 80 | 80.8 | — | 1.238 |
| 4.99 | 420 | 84.2 | +4.2% | 1.188 |
| 9.99 | 880 | 88.1 | +9.0% | 1.135 |
| 19.99 | 1,800 | 90.0 | +11.4% | 1.111 |
| 49.99 | 4,750 | 95.0 | +17.6% | 1.052 |
| 99.99 | 10,000 | 100.0 | +23.8% | 1.000 |

House band: top-pack bonus +20% to +40% over the entry rate. Show the bonus as "+N% bonus" computed against the entry pack — never against an invented "regular" rate.

### 2.3 Ladder design checklist

- [ ] Monotonic gems-per-dollar; computed bonus labels.
- [ ] Common hard-currency prices (10-pull, refill, premium booster) are reachable with one mid-tier pack, without large leftovers (`currency-architecture.md` §9.2).
- [ ] "Most popular" and "best value" tags are true (most popular = highest purchase count in the last period; best value = highest gems per dollar).
- [ ] No SKU exists only as a decoy. A deliberately inferior option placed to steer choice (the decoy effect; Huber, Payne & Puto, 1982) is a dark pattern when its only purpose is to mislead.
- [ ] Soft-currency packs priced so that buying soft with money is never better than earning it for engaged players by more than the time it saves.

### 2.4 Pricing beyond currency packs

| Product | Price anchor | Typical tiers |
|---|---|---|
| Starter pack | 3–5× value at an entry price | $0.99–$4.99 |
| Remove ads (non-consumable) | Lost interstitial revenue over expected lifetime ÷ (1 − store fee) (`ad-economy.md` §7) | $2.99–$9.99 |
| Season/battle pass | 5–10× reference value if fully completed | $4.99–$14.99 |
| Monthly card / subscription | 2–4× reference value if claimed daily | $2.99–$9.99 per month |
| Cosmetic skin | Perceived quality, not currency value | $1.99–$19.99 |
| Bundle (event/hero) | 2–5× reference value | $4.99–$49.99 |

These bands are house starting points to test, not market benchmarks.

---

## 3. Value framing and the value ratio

### 3.1 The reference price

Define one **reference price per unit** for each currency and good, published in the economy spec:

```
ref_usd_per_gem  = price / gems of the mid-tier pack            (Gems ladder: 9.99 / 880 = $0.01135)
ref_usd_per_coin = price / coins of the standard coin pack      (e.g. 4.99 / 3,000 = $0.00166)
ref_usd(item)    = its shop price in gems × ref_usd_per_gem      (for items sold for gems)
```

### 3.2 The value ratio

```
value_ratio(offer) = Σ_i quantity_i × ref_usd(i)  /  price_usd(offer)
```

- Bundle labels such as "5× value" must equal the computed ratio, rounded down.
- Items that cannot be bought elsewhere (exclusive skins) have no reference price; do not include them in the ratio, and do not inflate the claim with a made-up value.
- Track **realised value**: the ratio the median buyer actually collects (passes and subscriptions deliver over time; unclaimed rewards are not value).

### 3.3 Framing that respects the player

| Frame | Example | Use |
|---|---|---|
| Quantity | "880 gems" | Always shown |
| Bonus | "+9% bonus" | Computed vs the entry pack |
| Time | "Skip about 3 days of waiting" | When the time equivalence is derived from the sim |
| Progress | "Finish the Lighthouse area now" | Contextual offers |
| Social | "Gift to your team" | Social bundles |
| Price per day | "$0.17/day" for a $4.99 monthly card | Subscriptions; also show the full price |

Charm prices ($4.99) exploit left-digit bias modestly (Thomas & Morwitz, 2005); they are the store norm and acceptable. What is not acceptable: hiding the total, showing only per-day costs, or showing strikethrough prices the item never had.

---

## 4. First purchase

The first purchase is the hardest conversion and the best predictor of later spend. Design it as a moment of obvious value at an easy price.

**Timing.** Present it after the player has felt the need it solves (first loss with a near-miss, first wall, first decoration they love), not in the first minutes. House starting points: casual puzzle level 5–15 or day 1–2; builder day 1–3; RPG after the first gacha experience.

**Mechanics:**
- **First-time bonus per pack** ("first purchase of each pack gives double gems") rewards trying any price point once and is widely used; make the rule visible and per-pack.
- **Low-price entry** ($0.99–$2.99) with exceptional value (starter pack, §5).
- **No pressure**: one presentation at a natural moment, then available in the shop; not repeated pop-ups every session.

**Measure:** conversion to first purchase by day 1/3/7, time-to-first-purchase distribution, and the share of first purchases that are starter packs vs currency.

---

## 5. Starter packs

**Composition:** a mix that relieves the early economy's tightest constraint plus something that feels premium. Typical: a large soft-currency amount, a meaningful hard-currency amount, a few boosters or a hero/skin.

**Worked example (Lantern Lane, hypothetical):** $1.99 for 2,000 coins + 50 gems + 5 boosters.

```
coins:    2,000 × $0.00166            = $3.33
gems:        50 × $0.01135            = $0.57
boosters:     5 × 200 coins × $0.00166 = $1.66
reference value                        = $5.56   →  value ratio 5.56 / 1.99 = 2.79×
```

House band for starter packs: 3–5× at the entry price. At 2.79× this pack is slightly under; adding 1,000 coins (+$1.66) lifts it to about 3.6×.

**Availability:** one per account. Prefer "available until bought" or a clearly stated window that starts when the trigger fires (e.g., "72 hours from now") over a generic countdown. If the window expires, it can return later as a different offer, but never as the "same last chance" the next day.

**Upgrade path:** after the starter pack, show a second-tier "value pack" (e.g., $4.99 at ~3×), then the regular ladder. This is the offer ladder of §7.2.

---

## 6. Limited-time offers

| Type | Trigger | Cadence (house default) | Notes |
|---|---|---|---|
| Event bundle | Event start | Per event | Themed content + event currency head start |
| Seasonal | Calendar (holidays) | 4–8 per year | Exclusive cosmetics; region-aware calendars |
| Contextual | Game state (out of lives, near-miss loss, area almost done) | Max 1 per session | Must solve the current problem |
| Flash | Random/time | Rare | High fatigue; use sparingly |
| Comeback | Return after lapse | Once per lapse | Gift first, offer second |

Rules:
1. **Scarcity must be real.** If the countdown says 24 hours, the offer ends in 24 hours and does not reappear unchanged.
2. **Frequency caps**: at most one interruptive offer pop-up per session (house default), none during the first sessions before the first meaningful win, none after a purchase in the same session.
3. **Offer fatigue**: track conversion per impression over time; falling conversion with rising impressions means you are training players to ignore offers.
4. **Cannibalisation**: measure LTO revenue against a holdout group, not against the previous week (§13).

---

## 7. Personalised offers

### 7.1 Inputs

Spend history (never, small, regular, large), current balances, level band, recent loss streaks, churn-risk score, region (for price level), and engagement depth. Segmentation and prediction live with `player-analytics` and `liveops`; the economy owns the contents and values.

### 7.2 The offer ladder

```
state: current_tier (index into [0.99, 1.99, 4.99, 9.99, 19.99, 49.99])
on purchase:         next offer at current_tier + 1 (one step up), value ratio held or slightly lower
on N ignores (N=3):  step down one tier, raise value ratio slightly
never:               more than one tier jump; offers to accounts flagged as minors; offers during spend-limit cooldowns
```

### 7.3 Personalise contents before prices

Prefer different **bundles** (contents fit the player's needs: the booster they use, the hero they play) at standard prices over different **prices for the identical item**. Price discrimination for the same item within one storefront is legally sensitive in some jurisdictions and corrosive to trust when discovered (see volatile facts on EU personalised-pricing disclosure).

### 7.4 Guardrails

- No targeting by vulnerability signals (late-night spending bursts, rapid repeat purchases, chasing after losses). Treat these as triggers for cooldowns, not offers.
- No personalised offers to minors; no personalised offers on paid random items.
- Personalisation models are audited: log the features used for each offer decision.

---

## 8. Piggy banks

A piggy bank (pool node) accumulates hard currency visibly as the player plays; paying a fixed price "breaks" it. It converts engagement into perceived value and gives a natural, low-pressure first or repeat purchase.

```
fill:       +g gems per level win (pool node, trigger per_level_win)
min break:  B_min gems (cannot buy before), cap: B_max (fill stops)
price:      P
value at cap = B_max × ref_usd_per_gem;  ratio = value / P
```

**Worked example (hypothetical):** +10 gems per win, break allowed from 300, cap 600, price $2.99.

```
value at cap = 600 × $0.01135 = $6.81  →  ratio 2.28×   (at 300: $3.41 → 1.14×)
days to fill: engaged (7.2 wins/day) 600 / 10 / 7.2 = 8.3 days;  casual (2.4 wins/day) 25 days
```

Design notes: show the fill on win screens; let it reach the cap and wait (no decay); refresh after breaking; never fill it with currency the player already earned elsewhere (it must be extra); tune `g` so engaged players cap in 1–2 weeks. Model it as a `pool` node and the break as an offer with trigger `piggy_gems >= 300` (see the plugin's example economy model).

---

## 9. Bundles, chains and progression packs

| Format | Structure | Strength | Watch-out |
|---|---|---|---|
| **Fixed bundle** | Set contents at a price | Simple; clear value | Contents must suit the player's stage |
| **Hero/character bundle** | Unit + upgrade materials | High intent | Power balance in PvP |
| **Progression pack** | Unlocks rewards at level milestones after purchase | Sustained value, aligned with play | Value must be realised by normal play pace |
| **Chain ("endless") offer** | Sequence of steps alternating free and paid rewards | Momentum; free steps feel generous | Sunk-cost pressure; cap the length; show the full chain |
| **Tiered event bundle** | Same theme at 2–3 price levels | Serves all segments | Clear differences, no decoy tier |
| **Gift bundle** | Purchase for team/friends | Social goodwill | Opt-in only; no social pressure to buy |

Bundle composition rules: (1) lead with what the player needs now; (2) include at most 4–5 item types; (3) compute and show the value ratio; (4) do not bundle paid random items with deterministic items in a way that obscures odds.

---

## 10. Subscriptions, monthly cards and VIP

### 10.1 Formats

| Format | Delivery | Value logic | Risk |
|---|---|---|---|
| **Monthly card** (30-day) | Some currency now + daily claim | Rewards daily return; strong value for regulars | Missed days = lost value; disclose claim rules |
| **Auto-renewing subscription** | Ongoing perks (ad-free, daily gems, extra rewards, exclusive track) | Recurring revenue | Must deliver ongoing value; easy cancellation; store rules |
| **Ad-free subscription** | Removes interstitials (keep opt-in rewarded) | Alternative to one-off remove-ads | Overlap with one-off purchase; pick one model |
| **VIP by cumulative spend** | Permanent perks by lifetime spend tier | Rewards loyalty | Encourages escalation; ethically fraught; avoid spend-tier status displays to other players |

### 10.2 Worked example (hypothetical monthly card)

$4.99 for 100 gems immediately + 30 gems per daily claim for 30 days.

```
full claim: 100 + 30 × 30 = 1,000 gems × $0.01135 = $11.35  →  2.28×
claims 20 of 30 days: 700 gems = $7.95                       →  1.59×
```

Keep the daily share high enough to reward returning (habit) but the upfront share large enough that a busy month is not a loss. Show remaining days and unclaimed totals.

### 10.3 VIP guidance

Prefer **subscription-based** or **activity-based** status to lifetime-spend tiers. If spend tiers exist (common in some markets), keep perks to convenience, never show tiers publicly, and pair them with spending insights and limits.

---

## 11. Pass economics

A season (battle) pass sells **access to a reward track** that is completed by playing. It aligns monetization with engagement: the more you play, the more value you receive.

### 11.1 Structure

```
tiers T (e.g. 30), points per tier p (e.g. 100), season length S days (e.g. 28)
free track: modest rewards on most tiers (keeps non-payers progressing)
premium track: richer rewards on every tier; sometimes a premium-currency rebate
optional premium+: tier skips (e.g. +10 tiers) and extra cosmetics
points per day by archetype: from daily/weekly missions and play (sim them)
```

### 11.2 Completion design

| Archetype | Points/day (hypothetical) | Days to complete 3,000 points | Completes within 28 days? |
|---|---|---|---|
| casual | 60 | 50.0 | No — reaches ~56% |
| engaged | 140 | 21.4 | Yes, with ~6 days spare |
| payer | 170 | 17.6 | Yes |

Design target (house): the **median engaged player completes the premium track with 15–25% of the season to spare**; casual players reach the most-wanted premium rewards (place them by ~50% of the track). If the median engaged player needs tier skips to finish, the pass is a trap.

### 11.3 Value ratio of the pass

Hypothetical premium track at $9.99: 1,200 gems, 10 pull tickets (100 gems each), 20,000 coins, 30 boosters (200 coins each), plus exclusive cosmetics (excluded from the ratio).

```
gems       1,200 × $0.01135            = $13.62
tickets       10 × 100 × $0.01135      = $11.35
coins     20,000 × $0.00166            = $33.27
boosters      30 × 200 × $0.00166      =  $9.98
reference value                        = $68.22  →  6.83× at full completion
casual realised (56% of track, rewards spread evenly) ≈ 3.8×
```

House band: full-completion value ratio 5–10×, realised by median buyers ≥ 3×. A **premium-currency rebate** (the track returns more hard currency than the pass costs) is a well-known pattern that turns the pass into a loyalty programme; it lowers effective price for regular buyers and raises retention, but caps the pass's revenue per player, so model it explicitly.

### 11.4 Rules

- Show every reward on both tracks on day one; no hidden tiers.
- Retroactive unlock: buying the premium track late grants all premium rewards already earned.
- No expiring purchased currency; unclaimed rewards are auto-claimed or mailed at season end.
- Missions completable by normal play; no missions that require spending.
- Tier skips priced so they are a convenience for players who fall behind, not the expected path.

---

## 12. Regional pricing

Keep in-game contents identical worldwide and vary real-money prices per storefront (`currency-architecture.md` §13). Procedure:

1. Set the US (or your base market) ladder.
2. Let the store generate equalised local prices; review markets with very different purchasing power and adjust down where conversion is structurally low, using a PPP reference.
3. A/B test price levels per region only where the store and law allow, with guardrail metrics; never vary prices for the same item within a storefront without disclosure.
4. Revisit after currency swings and tax changes; stores may adjust local prices automatically (verify current behaviour).
5. In ad-led regions, add low-price entry offers and ad-free options instead of collapsing the whole ladder.

---

## 13. Measuring offers

| Metric | Definition | Use |
|---|---|---|
| Impression → purchase conversion | Purchases / offer impressions | Offer appeal; fatigue when falling |
| Revenue per impression | Revenue / impressions | Compare placements |
| Incremental revenue | Revenue(test) − revenue(holdout), per user | The only honest measure of an offer's value |
| Cannibalisation | Drop in other SKUs' revenue during the offer | Net effect of LTOs |
| Repeat purchase rate | Share of payers who buy again within 30 days | Ladder health |
| Refund / chargeback rate | Refunds / purchases | Misleading offers, accidental purchases, minors |
| Realised value ratio | Value collected / price, median buyer | Pass and subscription honesty |
| ARPPU distribution | Revenue per paying user, by percentile | Dependence on high spenders |

Always keep a **holdout** (e.g., 5–10% of eligible players who never see the offer) for major offer systems; without it, offers look like they create revenue they only move.

---

## 14. Ethical guardrails

These are hard rules for the studio (doctrine 8). The `compliance-officer` and `critic` agents check them on every shop change.

**Never:**
1. Hide the real-money price, or show only per-day or currency prices for real-money products.
2. Use fake countdowns, fake "was" prices, fake scarcity ("only 3 left" for digital goods).
3. Confirm-shame ("No thanks, I like losing").
4. Interrupt gameplay with offers at moments of frustration more than once per session, or immediately after a loss streak specifically to exploit tilt.
5. Target offers at minors or at vulnerability signals (§7.4); sell paid random items to minors where the law forbids it (`gacha-and-loot.md`).
6. Expire or confiscate purchased currency or items.
7. Design leftover-currency traps (§2.3).
8. Require purchases to complete standard content in a premium-marketed game or to finish a pass on time at normal play.
9. Make cancellation of subscriptions harder than sign-up.

**Always:**
1. Real-money prices from the store, localised.
2. Value claims computed from the published reference.
3. Purchase confirmation for anything over a threshold, and spending summaries in settings.
4. Optional spending limits and parental controls respected (platform family features).
5. A refund/support path linked from the shop.

**Dark-pattern detector (run on screenshots of every shop and offer screen):** countdown present → is the end time real? Strikethrough present → was that price ever charged? Value label present → does it match `value_ratio`? Close button visible within the first second and at least 44 pt touch target? Price visible in local currency? Minor account → offer suppressed?

---

## 15. Offer spec template

Contract side (`contract.json → monetization.iap[]`):

```json
{ "id": "starter_pack", "type": "bundle", "price_tier": "USD 1.99",
  "contents": { "coins": 3000, "gems": 50, "boosters": 5 } }
```

Model side (`economy-model → offers[]`), so `economy_sim.py` includes it:

```json
{ "id": "starter_pack", "price_usd": 1.99, "contents": { "coins": 3000, "gems": 50, "boosters": 5 }, "trigger": "level >= 8" }
```

Design sheet fields (keep beside the contract): reference value, value ratio, target segment, trigger, frequency cap, availability window, holdout share, primary KPI, guardrail KPIs, ethical review sign-off.

---

## 16. Volatile facts (as of Oct 2026 — verify before relying)

- **Commission rates change net price per SKU.** EU: Apple's single business model effective Oct 1, 2026 lists IAP 26%/15%, alternative PSP 20%/10%, link-out 15%/10%, and a 5% Core Technology Commission outside the App Store — [Apple newsroom, Aug 18, 2026](https://www.apple.com/newsroom/2026/08/apple-announces-changes-for-apps-in-the-european-union/) (checked 2026-10-20; secondary summary: [iGeeksBlog](https://www.igeeksblog.com/eu-welcomes-apple-new-app-store-terms/)). US: Apple link-outs are allowed with only a cost-based fee on remand after the Ninth Circuit's December 2025 decision, and the Supreme Court granted review (No. 25-1311) — [Justia](https://law.justia.com/cases/federal/appellate-courts/ca9/25-2935/25-2935-2025-12-11.html). Google Play US alternative billing and external links are permitted under the Epic injunction; the fee schedule and settlement approval were unresolved in mid-2026 — [Stash, Apr 2026](https://www.stash.gg/blog/blog-epic-v-google-settlement-update-april-2026). Web shops are now standard for mid-size and large games; recompute net revenue per pack per channel.
- **Google Play one-time products** support multiple purchase options and offers (discounts, pre-orders in early access) via PBL 8 and `monetization.onetimeproducts` — [Android Developers Blog](https://android-developers.googleblog.com/2025/07/new-tools-to-help-drive-success-for-one-time-products.html).
- **RevenueCat's official MCP** can manage products, entitlements, offerings and experiments and edit store product state — useful for implementing ladders and passes — [RevenueCat MCP docs](https://www.revenuecat.com/docs/tools/mcp). Battle passes are commonly modelled as non-consumable or auto-renewing products with server-side entitlements (an inference in the research, not a sourced rule).
- **Hybrid-casual spending** grew 17.1% in 2025 (from about $3.5B to $4.2B) while overall mobile game IAP was roughly flat, per Sensor Tower data summarised by Mobilegamer.biz — [Mobilegamer.biz data digest](https://mobilegamer.biz/data-digest-sensor-towers-h1-analysis-hay-days-comeback-julys-top-games-big-krafton-numbers-and-more/). Hybrid models (ads + IAP + passes) are where this file's ladders matter most.
- **Apple auto-renewable subscriptions** must provide ongoing value (App Review Guideline 3.1.2, background, not re-verified) — [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/).
- **EU personalised pricing and price-reduction rules** (background, not re-verified): EU consumer law amended by the Omnibus Directive (2019/2161) requires informing consumers when a price is personalised by automated decision-making, and regulates how price reductions are announced (reference to a prior price). How these apply to in-app digital content should be confirmed with counsel before running personalised prices or strikethrough promotions in the EU.
- **US FTC and virtual currency** (checked 2026-10-20): on January 17, 2025 the FTC announced a settlement with Cognosphere (HoYoverse), the publisher of Genshin Impact: a $20 million civil penalty, a bar on letting children under 16 buy loot boxes without a parent's affirmative express consent, and required disclosure of loot-box odds and of exchange rates for multi-tiered virtual currency, plus COPPA terms. It was a proposed order that needed court approval — [FTC press release](https://www.ftc.gov/news-events/news/press-releases/2025/01/genshin-impact-game-developer-will-be-banned-selling-lootboxes-teens-under-16-without-parental). For dark-pattern charges, see FTC v. Epic Games (December 2022: $245 million in refunds plus a $275 million COPPA penalty) — [FTC press release](https://www.ftc.gov/news-events/news/press-releases/2022/12/fortnite-video-game-maker-epic-games-pay-more-half-billion-dollars-over-ftc-allegations).
