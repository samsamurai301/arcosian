# Ad Economy

In ad-supported and hybrid games, advertising is both a revenue stream and an economy faucet: every rewarded view injects currency, energy or items, and every interstitial costs some player goodwill. This file treats ads as part of the economy design: rewarded placements as a value exchange and how to size their rewards, interstitial frequency caps, the ad-revenue and ad-LTV maths, balancing ads against IAP (and measuring cannibalisation), pricing the ad-free purchase, the operational basics an economy designer must know (mediation, consent, child-directed flags), telemetry, and anti-patterns. Market eCPM figures are not given as facts here: the October 2026 research found no verified primary eCPM benchmark, so every worked example uses clearly labelled hypothetical inputs and tells you where to get real values. Implementation of SDKs and mediation lives in `monetization`; UA economics in `marketing-ua`.

## Contents

1. [Ads in the economy: two flows](#1-ads-in-the-economy-two-flows)
2. [Formats and their economy roles](#2-formats-and-their-economy-roles)
3. [Rewarded placements: value exchange](#3-rewarded-placements-value-exchange)
4. [Interstitial frequency caps](#4-interstitial-frequency-caps)
5. [Ad revenue and ad LTV maths](#5-ad-revenue-and-ad-ltv-maths)
6. [Hybrid IAP/ads balance and cannibalisation](#6-hybrid-iapads-balance-and-cannibalisation)
7. [The ad-free purchase](#7-the-ad-free-purchase)
8. [Operational basics for economy designers](#8-operational-basics-for-economy-designers)
9. [Ad telemetry and KPIs](#9-ad-telemetry-and-kpis)
10. [Anti-patterns](#10-anti-patterns)
11. [Volatile facts](#11-volatile-facts-as-of-oct-2026--verify-before-relying)

---

## 1. Ads in the economy: two flows

```
player attention ──(view)──► ad network ──(eCPM / 1000 per impression)──► developer revenue
        ▲                                                                  
        └──────────(reward: currency, energy, item, continue)── economy faucet (node trigger on_ad)
```

- **Rewarded ads** are opt-in exchanges: the player gives ~15–30 seconds of attention, the game gives a reward. They are an economy **source** and must be modelled (`trigger: "on_ad"` nodes; `ad_accept_rate` per archetype in the economy model).
- **Interstitials and banners** are not exchanges; they are a cost the player pays for a free game. They are not economy flows, but they affect retention and therefore every flow.
- The economy designer's job: size rewarded rewards so ads are worth watching but do not replace play or purchases, and cap interruptive formats so retention is protected.

---

## 2. Formats and their economy roles

| Format | Opt-in? | Economy role | Player cost | Typical placement |
|---|---|---|---|---|
| **Rewarded video** | Yes | Faucet; conversion gateway | Time, voluntary | Results screen, out-of-lives, chest speed-up, free currency button |
| **Rewarded interstitial** | Semi (skippable intro) | Faucet | Time; feels less voluntary | Between levels with a reward offer |
| **Interstitial** | No | None (retention cost) | Interruption | Level transitions, after N levels or minutes |
| **Banner** | No | None | Screen space; accidental taps | Menus; avoid over gameplay on small screens |
| **Offerwall** | Yes | Large faucet (installs/tasks for currency) | Leaves the game | Hard-currency store tab |
| **Native / in-world** | No | None | Low if well integrated | Billboards in-world, store tiles |
| **Playable** (as inventory) | Mostly no | None | Interruption | Rare as publisher inventory; mainly a UA creative format |

---

## 3. Rewarded placements: value exchange

### 3.1 Placement taxonomy

| Placement | Reward | Economy impact | Cannibalisation risk | House cap |
|---|---|---|---|---|
| Double level reward | +100% of the win payout | Scales with progress; inflation risk late-game | Medium (competes with coin packs) | 1 per level result; ~10/day |
| Continue / revive | Extra moves, second life | Converts a loss into a win; strong value | High (competes with gem continues) | 1 per level attempt |
| Free energy | 1 life / some stamina | Session extension | Medium (competes with refills) | 3–5/day |
| Free currency button | Fixed soft amount | Pure faucet | Low–medium | 3–5/day |
| Chest/timer speed-up | Skip X minutes | Faster loop | Medium (competes with gem skips) | Per timer, limited |
| Extra spin / roll | One more chance | Faucet into a chance mechanic | Medium | 3–5/day |
| Trial item | Use a premium booster/skin for one level | Conversion gateway (endowment) | Low; often lifts IAP | 1–2/day |
| Daily bonus multiplier | ×2 daily reward | Habit | Low | 1/day |

### 3.2 Sizing the reward

```
ad_value_to_player(reward) = ref_usd(reward)           (reference price, pricing-and-offers.md §3.1)
ad_revenue_per_view        = eCPM_rewarded / 1000
player_value_ratio         = ad_value_to_player / ad_revenue_per_view
```

Rewarded ads are almost always a much better deal for the player per revenue-dollar than IAP — that is intended (they monetise people who would never pay). Example with hypothetical inputs: a view grants 40 coins (reference value 40 × $0.00166 = $0.066); at a hypothetical rewarded eCPM of $10 the view earns $0.01, so the player receives about 6.7× more reference value than the developer earns. The economy guard is therefore **not** per-view value but the **daily ceiling**:

```
daily_ad_income_cap(currency) ≤ 15–20% of a free player's daily income of that currency  (sources-sinks-balancing.md §5.2)
daily_ad_value_cap            < value of the cheapest relevant IAP     (so ads never make the entry pack pointless)
```

Lantern Lane (hypothetical): cap 10 rewarded views/day × 40 coins = 400 coins; median engaged income 516/day from all sources, of which ads contribute 80 (15.5%) at observed acceptance — within the band; the cap binds only for heavy ad watchers.

### 3.3 Placement rules

1. **Opt-in, always.** The player taps a clearly labelled button; the reward is shown before the ad.
2. **Natural pauses only**: results screens, out-of-lives, shop tab — never mid-level.
3. **Reward reliably**: if the ad fails to load or the network has no fill, either grant the reward anyway (generous) or hide the button (honest). Never show a button that may fail after the player commits.
4. **Scale with progress carefully**: "double reward" scales automatically; fixed rewards need periodic re-tuning so late-game ads stay attractive without inflating.
5. **Count views server-side** when rewards are valuable (otherwise reward replay exploits appear).

---

## 4. Interstitial frequency caps

Contract fields: `monetization.ads.interstitial.min_interval_sec` and `first_after_sec`.

| Rule | House default (test before shipping) | Why |
|---|---|---|
| No interstitials during FTUE | First interstitial after the first 2–3 sessions or ≥ 5–10 minutes of cumulative play (`first_after_sec`) | D1 retention is the most sensitive metric |
| Minimum interval | 60–180 s of gameplay between interstitials (`min_interval_sec`) | Prevents back-to-back ads on short levels |
| Placement | Level end/transition only, never after a loss streak, never mid-level | Respect the player's moment |
| After a rewarded view | Skip the next interstitial | Rewarded viewers have already "paid" |
| Payers | Suppress interstitials for any payer (or after first purchase above a threshold) | Protects the most valuable relationship |
| Session cap | e.g., ≤ 1 per 2–3 levels and ≤ N per session | Caps annoyance on long sessions |
| Ad-free purchasers / subscribers | None, ever | They bought this |

**Tune with an A/B test**, not opinion: vary `min_interval_sec` across arms and compare D7 retention and total ARPDAU (ads + IAP). Size the test with `ab_test.py size --baseline <D7> --mde <delta>`; the right cap is the one that maximises LTV, not ad ARPDAU.

---

## 5. Ad revenue and ad LTV maths

### 5.1 Ad ARPDAU

```
impressions_per_DAU(placement) = opportunities_per_DAU × show_rate × fill_rate
   rewarded: opportunities = button views; show_rate = engagement (accept) rate
   interstitial: opportunities = eligible transitions after caps
ad_ARPDAU = Σ_placements impressions_per_DAU × eCPM_placement / 1000
```

### 5.2 Worked example (hypothetical inputs — replace with your mediation dashboard values)

| Placement | Impressions per DAU | eCPM (hypothetical) | ARPDAU contribution |
|---|---|---|---|
| Rewarded | 4 offers × 40% accept = 1.6 | $10 | $0.016 |
| Interstitial | 3 | $5 | $0.015 |
| Banner | 20 | $0.30 | $0.006 |
| **Total** | | | **$0.037** |

Sensitivity of rewarded ARPDAU to the two levers (4 offers/DAU):

| Rewarded eCPM → / accept rate ↓ | $5 | $10 | $20 |
|---|---|---|---|
| 30% | $0.006 | $0.012 | $0.024 |
| 50% | $0.010 | $0.020 | $0.040 |

Lesson: placement design (accept rate) moves revenue as much as eCPM does, and is under your control.

### 5.3 Ad LTV

```
ad_LTV(horizon) = Σ_{t=0}^{horizon} retention(t) × ad_ARPDAU(t)
expected active days = Σ retention(t)
```

With retention points D1 40%, D7 15%, D30 6% fitted by a power law r(t) = 0.4 × t^(−0.558) (fits D1 and D30 exactly; predicts D7 ≈ 13.5%), expected active days per install are about 12.6 over 365 days and 9.3 over 180 days. At ad ARPDAU $0.037 (hypothetical), ad LTV ≈ $0.47 per install at 365 days and $0.34 at 180 days. Use the plugin calculator for real cohorts:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/retention_ltv.py fit --points "1:0.40,7:0.15,30:0.06" --model power --json
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/retention_ltv.py ltv --points "1:0.40,7:0.15,30:0.06" --arpdau 0.037 --horizon 365 --json
```

Compare ad LTV + IAP LTV with CPI (from `marketing-ua`) to judge viability; ad LTV alone rarely covers paid UA in mature markets.

### 5.4 What moves ad revenue (in order of controllability)

1. Retention (more days × same ARPDAU).
2. Rewarded placement value and visibility (accept rate).
3. Interstitial caps (impressions, at a retention cost).
4. Mediation setup (bidding, network mix) — engineering/ops.
5. Geography and platform mix (UA decision).
6. Seasonality of eCPM (advertiser demand varies through the year; commonly observed to peak in Q4 — verify in your own data).

---

## 6. Hybrid IAP/ads balance and cannibalisation

### 6.1 Segment the experience

| Segment | Interstitials | Rewarded | Offers |
|---|---|---|---|
| New player (FTUE) | None | Introduce one placement after the first win | None |
| Non-payer, engaged | Capped | Full set, daily caps | Starter pack at a natural moment |
| Non-payer, at churn risk | Reduce | Generous rewarded | Comeback gift |
| First-time payer | Suppress | Keep (opt-in) | Offer ladder (`pricing-and-offers.md` §7.2) |
| Regular payer | None | Keep, optional | Pass, subscription, bundles |
| Ad-free purchaser | None | Keep opt-in rewarded | Normal |

### 6.2 Cannibalisation mechanisms and detection

| Mechanism | Example | Detect | Mitigate |
|---|---|---|---|
| Rewarded replaces a product | Ad continue makes gem continues pointless | Gem-continue purchases fall when ad continue launches | Limit ad continues to 1 per level; gems allow further continues |
| Ad rewards remove scarcity | Uncapped free currency | Hoard days rise in ad-heavy cohorts | Daily caps (§3.2) |
| Interstitials push payers away | Payers churn after ad exposure | Payer retention vs ad exposure | Payer suppression |
| Ad-free underpriced | Cheap removal gives away long-term ad revenue | Ad-free buyers' projected ad LTV > price | Price floor (§7) |
| Delayed conversion | Players satisfied by ads never buy | Conversion lower in arms with richer rewarded | Trial-item placements that showcase premium |

**Measure with holdouts.** The only reliable test of cannibalisation is a randomised experiment: arm A without the placement, arm B with it; compare **total** revenue per user (IAP + ads) and retention over at least 2–4 weeks. Short tests overstate ad wins because IAP effects lag.

### 6.3 Revenue mix by context

Where IAP conversion is structurally low (ad-led markets), lean on rewarded ads and low-price offers; in mature IAP markets, ads matter mostly for the non-paying majority. The October 2026 research summary of Sensor Tower data shows ads at about 70% of game revenue in India versus about 22% in the US, and IAP at 77–90% in mature markets (see volatile facts). Design the economy so either revenue stream can carry its segment without breaking the other.

---

## 7. The ad-free purchase

### 7.1 Price floor

```
lost_ad_revenue_per_buyer = (interstitial + banner ARPDAU of a likely buyer) × expected remaining active days of a buyer
price_floor_gross          = lost_ad_revenue_per_buyer / (1 − store_fee)
```

Worked example (hypothetical): interstitial + banner ARPDAU $0.021 (from §5.2), buyers are engaged players with an assumed 150 remaining active days → lost revenue $3.15 → gross floor $4.50 at a 30% fee or $3.71 at 15%. A $4.99 price clears both. Buyers are self-selected heavy players, so use their retention, not the average player's.

### 7.2 What ad-free removes and keeps

| Remove | Keep |
|---|---|
| Interstitials | Opt-in rewarded ads (they are a benefit, not an annoyance) |
| Banners | Rewarded placements' daily caps unchanged |
| Ad-break interruptions | Optional: "rewards without watching" as a premium perk in a subscription instead of the one-off |

Clearly state what "No Ads" includes before purchase. Selling "No Ads" and then still showing rewarded prompts as forced breaks is deceptive.

### 7.3 When to surface it

After the player has experienced several interstitials (e.g., the 5th–10th) and has shown commitment (day 2+). Offer it in settings and the shop permanently; avoid pop-ups after every ad.

### 7.4 One-off vs subscription

One-off non-consumable "Remove Ads" is simple and player-friendly. An ad-free subscription can capture more value from long-lived players but must deliver ongoing value (store rules) and complicates expectations. Pick one primary model; offering both confuses players.

---

## 8. Operational basics for economy designers

- **Mediation**: a mediation platform runs an auction across networks for each impression; **bidding** (real-time) has largely replaced manual waterfalls. The economy designer needs per-placement eCPM and fill by country from the dashboard to keep the economy model honest.
- **Consent and tracking**: GDPR/UK consent via a consent management platform; iOS App Tracking Transparency affects personalised ads and therefore eCPM; attribution uses Apple's AdAttributionKit (successor to SKAdNetwork) on iOS. Model eCPM separately for consented and non-consented traffic if they differ materially.
- **Children and mixed audiences**: child-directed or under-age traffic requires the networks' child-directed flags (non-personalised ads), and COPPA obligations in the US; rewarded placements remain possible but eCPM is lower. Never use reward placements to encourage children to watch ads repeatedly.
- **Ad quality**: block categories inappropriate for the audience; monitor for deceptive or auto-redirect creatives; give players a report path.
- **Server-side control**: frequency caps, reward sizes and placement toggles in remote config, so they can be tuned without a release.

---

## 9. Ad telemetry and KPIs

| Event | Params | KPI it feeds |
|---|---|---|
| `ad_opportunity` | `placement`, `format`, `eligible` (after caps) | Opportunities per DAU |
| `ad_offer_shown` | `placement`, `reward_currency`, `reward_amount` | Rewarded button views |
| `ad_started` / `ad_completed` | `placement`, `network`, `ecpm_estimate` (if exposed by the SDK) | Engagement rate, completion rate |
| `ad_reward_granted` | `placement`, `reward_currency`, `amount`, `transaction_id` | Economy faucet (joins `currency_earned`) |
| `ad_failed` | `placement`, `reason` (no_fill, timeout) | Fill rate; broken placements |

| KPI | Formula | Watch for |
|---|---|---|
| Rewarded engagement rate | Started / offers shown | Falling → reward too small or offers too frequent |
| Impressions per DAU | Impressions / DAU, per format | Rising interstitial imps with falling D7 |
| Ad ARPDAU | Ad revenue / DAU | Compare per segment and per country |
| Ad share of soft income | Ad-granted currency / total granted | Above 15–20% for free players (§3.2) |
| Retention delta by ad exposure | D7 of high-exposure vs low-exposure (from A/B, not observational) | Interstitial caps too loose |

---

## 10. Anti-patterns

| Anti-pattern | Why it hurts | Detection |
|---|---|---|
| Interstitials in the FTUE | Kills D1 | First interstitial timestamp < `first_after_sec` |
| Forced "rewarded" (no reward choice) | Deceptive; store-policy risk | Rewarded ad plays without a tap |
| Ad after a purchase | Breaks trust with payers | Ad impressions for users with purchases in the session |
| Uncapped rewarded currency | Inflation; IAP cannibalisation | Ad share of income > 20% |
| Fake close buttons, disguised ads | Dark pattern; policy violations | Visual review of every ad-adjacent screen |
| Rewarded ads as the only way to progress | Pay-with-time wall | Starvation rate for non-ad watchers |
| Ad-free that still interrupts | Deception | Interstitial events for ad-free buyers |
| Judging ad changes on ad ARPDAU alone | Ignores retention and IAP effects | Decision memos without total-LTV comparison |

---

## 11. Volatile facts (as of Oct 2026 — verify before relying)

- **eCPM benchmarks: none verified.** The October 2026 research found no primary 2026 benchmark for eCPM or hybrid-casual ARPDAU, only secondary summaries. Use your own mediation dashboard (per placement, format, country, platform) and the networks' reporting APIs; do not quote third-party eCPM tables as facts. All eCPMs in this file are hypothetical inputs. Research gap noted in the build/monetization notes; no source to cite.
- **Revenue mix**: Sensor Tower data (summarised) shows that from Feb to Apr 2026 casual and hyper-casual each took about 40% of game ad revenue, hybrid 16% and mid-core 4%; ads were 70.3% of game revenue in India vs 22.1% in the US (Jan–May 2026); in mature markets (US, CA, KR, JP), IAP is 77–90% of revenue — [GameDev Reports summary](https://gamedevreports.substack.com/p/sensor-tower-mobile-game-ad-monetization); [Sensor Tower ad monetization deep dive](https://sensortower.com/blog/gaming-deep-dive-ad-monetization-report).
- **Mediation market**: in 2025 AppLovin MAX, Unity LevelPlay and AdMob together held more than 90% of mediation; among top-grossing ad-monetised games MAX had 55%, LevelPlay 25% and AdMob 13.3% — [PocketGamer.biz](https://www.pocketgamer.biz/nine-facts-about-the-mediation-space-in-2025). Unity LevelPlay ended waterfall-only support for Unity Ads in January 2026, making bidding the standard path — [Segwise](https://segwise.ai/blog/applovin-publisher-monetization-guide).
- **Attribution**: AdAttributionKit is Apple's successor to SKAdNetwork (there was no SKAN 5); it keeps three postback windows and crowd-anonymity tiers and adds configurable windows and re-engagement — [Moburst](https://www.moburst.com/mobile-attribution-in-2026-what-marketers-actually-need-to-know/).
- **SDK privacy manifests**: SDKs on Apple's list must ship privacy manifests and signatures; AppLovin and GoogleMobileAds were not on the list at the time of research — [Apple third-party SDK requirements](https://developer.apple.com/support/third-party-SDK-requirements/).
- **COPPA**: the amended COPPA Rule's compliance deadline was April 22, 2026 (expanded personal information including biometrics; operator responsibility for third-party integrations touching children's data) — [Toy Association](https://toyassociation.org/PressRoom2/News/2026-News/updated-coppa-rule-requirements-take-effect-april-22.aspx). Relevant to ad SDK configuration for child or mixed audiences.
