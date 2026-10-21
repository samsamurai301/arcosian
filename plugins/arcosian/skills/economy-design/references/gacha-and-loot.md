# Gacha and Loot

Paid randomness (gacha banners, loot boxes, chests, card packs, prize wheels) is the most lucrative and the most regulated pattern in mobile economies. This file gives the economy designer the full toolkit: when to use randomness at all, rarity and pool design, the expected-value and percentile maths (with exact numbers from the studio's calculator), pity and soft pity, rate-up with guarantees, spark ceilings, duplicate protection and collection maths, free-player generosity targets, chests in non-gacha games, implementation and statistical verification, the legal disclosure regimes that shape design (China, South Korea, Japan, Belgium, the Netherlands, Brazil, platform rules and others), and the transparent alternatives the studio defaults to. Mechanic-level cards for pity, rate-up and spark live in `mechanics-codex` (`references/07-randomness-chance-mechanics.md`); genre playbooks in `genre-playbooks` (`references/rpg-gacha.md`); law in `legal-ethics`.

## Contents

1. [Should this game use paid randomness?](#1-should-this-game-use-paid-randomness)
2. [Rarity tiers and pool design](#2-rarity-tiers-and-pool-design)
3. [Expected-value and percentile maths](#3-expected-value-and-percentile-maths)
4. [Pity and soft pity](#4-pity-and-soft-pity)
5. [Rate-up and featured guarantees](#5-rate-up-and-featured-guarantees)
6. [Spark (exchange ceiling)](#6-spark-exchange-ceiling)
7. [Duplicate protection and collection maths](#7-duplicate-protection-and-collection-maths)
8. [Free-player generosity and banner cadence](#8-free-player-generosity-and-banner-cadence)
9. [Chests and loot boxes outside gacha](#9-chests-and-loot-boxes-outside-gacha)
10. [Implementation and statistical verification](#10-implementation-and-statistical-verification)
11. [Legal and platform disclosure regimes](#11-legal-and-platform-disclosure-regimes)
12. [Transparent alternatives](#12-transparent-alternatives)
13. [Pre-launch checklist](#13-pre-launch-checklist)
14. [Volatile facts](#14-volatile-facts-as-of-oct-2026--verify-before-relying)

---

## 1. Should this game use paid randomness?

The studio default (doctrine 8, and the research report's recommendation) is **transparent monetization first**: direct purchase, passes, fixed bundles. Paid randomness needs a reason.

| Question | If yes → | If no → |
|---|---|---|
| Is collecting many characters/cards the core fantasy? | Randomness can fit; continue | Use direct purchase and passes |
| Will the game ship to Belgium, or to under-18s in Brazil? | Need a no-paid-random variant per region/age (§11) | Continue |
| Is the audience young or mixed-age? | Paid random items off for minors; strongly prefer alternatives | Continue |
| Can the free experience obtain the featured content within a stated number of banners? | Continue | Fix generosity first (§8) |
| Can you show odds, pity, expected and worst-case real-money cost before purchase? | Continue | Do not ship paid randomness |
| Is there a deterministic path to every item (exchange, selector, shop)? | Ship | Add one (§12) |

**Removal test** (from `design-theory`): if the random reward disappeared, would the loop still be worth doing? If not, the loop is a slot machine with a theme.

---

## 2. Rarity tiers and pool design

### 2.1 Tier structure

| Tier | Typical base rate band | Pool size | Role |
|---|---|---|---|
| Top (5★, legendary) | 0.5–3% | Small (5–20 standard + featured) | Chase items; power or prestige |
| High (4★, epic) | 5–15% | Medium | Team-building filler; frequent satisfaction |
| Base (3★, rare/common) | Remainder | Large or consumables | Materials, fodder; never an "empty" pull |

### 2.2 Per-item probability

```
P(item i per pull) = P(tier of i) × share of i within tier
example: top tier 0.6%, one featured item takes 50% of the top tier, 7 standard items share the other 50%
  featured: 0.006 × 0.5       = 0.30% per pull (base, before pity)
  each standard top item: 0.006 × 0.5 / 7 = 0.043% per pull
```

Disclose **both** tier rates and per-item rates. When pity exists, also disclose the **consolidated rate** (rate including pity), defined as 1 / expected pulls.

### 2.3 Multi-pull guarantees

A 10-pull usually guarantees at least one high-tier item. Without it, at a 5.1% high-tier rate, a 10-pull has no high-tier item 59.2% of the time ((1 − 0.051)^10); even at 10% it is 34.9%. Empty multi-pulls feel like theft, so guarantee one high-tier result per 10 (implemented as a per-10 pity counter, not as a rate change).

### 2.4 Pool hygiene

- Pool contents and rates are **versioned config**, immutable once live; the odds page renders from the same config.
- Adding items to a pool **dilutes** per-item rates; disclose the new per-item rates the moment the pool changes.
- Keep the top-tier pool small enough that collection goals feel achievable; grow it with permanent selectors or exchanges.

---

## 3. Expected-value and percentile maths

### 3.1 Formulas

```
no pity, rate p:
  P(≥1 hit in n pulls)   = 1 − (1 − p)^n
  expected pulls          = 1 / p
  pulls for quantile q    = ln(1 − q) / ln(1 − p)

any schedule p(n) (pity, soft pity):
  P(first hit at n)       = p(n) × Π_{k<n} (1 − p(k))
  expected pulls E        = Σ_n n × P(first hit at n)
  consolidated rate       = 1 / E

featured item with share F and guarantee after a loss:
  distribution            = F × D + (1 − F) × (D ⊛ D)    (D = top-tier distribution, ⊛ = convolution)
  expected pulls          = E × (1 + (1 − F)) = 1.5 E for F = 0.5
  worst case              = 2 × hard pity

real-money cost:
  cost(n pulls)           = n × currency_per_pull × usd_per_currency  (state the pack rate used: best and entry)
```

### 3.2 Reference table (computed exactly; reproduce with `gacha_calc.py`)

| Config | Top-tier E (pulls) | Consolidated rate | p50 / p90 / p99 | Featured (50/50 + guarantee) E | Featured p50 / p90 / p99 |
|---|---|---|---|---|---|
| A: 0.6%, soft pity from 74 (+6 pp/pull), hard 90 | 62.30 | 1.605% | 76 / 80 / 83 | 93.45 | 80 / 155 / 161 |
| B: 0.6%, hard 90 only | 69.70 | 1.435% | 90 / 90 / 90 | 104.55 | 90 / 180 / 180 |
| C: 1.0%, soft from 60 (+5 pp), hard 80 | 47.56 | 2.102% | 61 / 67 / 70 | 71.34 | 66 / 127 / 134 |
| D: 2.0%, hard 50 | 31.79 | 3.145% | 35 / 50 / 50 | 47.69 | 50 / 90 / 100 |
| E: 2.0%, no pity | 50.00 | 2.000% | 35 / 114 / 228 | 75.00 | 58 / 163 / 297 |
| F: 0.6%, no pity | 166.65 | 0.600% | 116 / 383 / 766 | 249.98 | 191 / 545 / 996 |
| G: 1.5%, soft from 55 (+8 pp), hard 70 | 38.95 | 2.568% | 46 / 59 / 62 | 58.42 | 58 / 111 / 120 |

Reading the table:
- **Pity compresses variance more than it lowers the mean.** Config A vs F: the mean falls from 167 to 62 pulls, but p99 falls from 766 to 83 — the tail is what pity really fixes.
- **Soft pity makes outcomes predictable:** in A, half of players hit by pull 76 and 90% by pull 80. Players learn to plan around the soft-pity zone.
- **The featured distribution is bimodal** (win the 50/50 near pull 76–80, or need a second cycle near 150–160). Median 80, mean 93: always disclose the worst case (180 in A).
- Config A reproduces a widely played gacha's published figures (0.6% base, 1.6% consolidated, 90-pull guarantee); its soft-pity start and step are community measurements, not official — see `genre-playbooks` `references/rpg-gacha.md` §0.1.

Commands (exact CLI from the blueprint):

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gacha_calc.py --rate 0.006 --soft-pity-start 74 --soft-pity-step 0.06 --hard-pity 90 --pulls 90 --json
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gacha_calc.py --rate 0.006 --soft-pity-start 74 --soft-pity-step 0.06 --hard-pity 90 --rate-up 0.5 --guarantee --pulls 180 --json
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gacha_calc.py --rate 0.02 --hard-pity 50 --rate-up 0.5 --guarantee --pulls 100 --json
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gacha_calc.py --rate 0.006 --pulls 300 --json      # no pity: shows the tail
```

### 3.3 Real-money cost (hypothetical currency)

Using the Gems ladder from `pricing-and-offers.md` §2.2 and 100 gems per pull:

| Pack rate used | USD per pull | Featured, expected (93.45 pulls, config A) | Featured, worst case (180 pulls) |
|---|---|---|---|
| Entry ($0.99 pack, $1.238/100 gems) | $1.24 | $115.64 | $222.75 |
| Mid ($9.99 pack, $1.135/100 gems) | $1.14 | $106.09 | $204.34 |
| Best ($99.99 pack, $1.00/100 gems) | $1.00 | $93.44 | $179.98 |

These are the numbers the banner's info page should show (as ranges in local currency), next to the odds and pity rules. If the numbers look uncomfortable on the info page, the banner is too expensive.

---

## 4. Pity and soft pity

### 4.1 Parameters

| Parameter | Effect | Design guidance (house) |
|---|---|---|
| Base rate | Headline odds; sets the mean when pity is far away | Lower base + pity = more predictable; higher base + no pity = swingy |
| Hard pity H | Worst case per top-tier item | H at or below the no-pity mean (1/p) is meaningful (0.6%: mean 167 vs H = 90); H far above it is decorative; show the counter |
| Soft pity start s | Where odds start ramping | ~70–85% of H; earlier start = lower mean, tighter distribution |
| Soft pity step Δ | Ramp per pull | Steep ramps (5–10 pp/pull) put almost all hits in a narrow band |
| Carry-over | Counter persists across banners of the same type | Always carry over; resetting on banner change reads as confiscation |
| 10-pull floor | ≥1 high-tier per 10 | Always |

### 4.2 Design procedure

1. Decide the **target expected cost** of a top-tier item in pulls (from the free-generosity target, §8, and the price ladder).
2. Decide the **worst case** you are willing to print on the info page (hard pity, or 2 × hard pity for featured).
3. Choose base rate and soft-pity shape to hit the target mean between the two; check p50, p90 and p99 with `gacha_calc.py`.
4. Disclose: base rate, consolidated rate, hard pity, soft-pity existence (and shape if known), carry-over rule, guarantee rule.
5. Implement the counter server-side; show it on the banner screen.

---

## 5. Rate-up and featured guarantees

- **Featured share F**: share of top-tier results that are the featured item. F = 50% with a guarantee after a loss is the familiar "50/50" pattern; F = 100% removes the loss state entirely.
- **Guarantee**: after an off-banner top-tier result, the next top-tier result is featured. Without it, the worst case is unbounded.
- **Multi-featured dilution**: three featured items sharing 50% gives each about 16.7% of top-tier results; a specific target becomes far more expensive. Show the per-item probability, not just "rate up".
- **Chosen target ("path")**: the player picks one featured item; after k off-target results, the next is the target. Converts a multi-featured banner into a bounded one.

Featured maths for config A (exact): expected 93.45 pulls; median 80; p90 155; p99 161; worst case 180. For a specific featured item at 0.3% per pull **without** pity, the mean is 333 pulls, the median 231 and p90 766 — this is why pity-free featured banners need a spark.

---

## 6. Spark (exchange ceiling)

A spark gives one point per pull; at N points the player picks a featured item. It converts an unbounded or wide distribution into a known maximum.

```
expected pulls with spark at N = E[min(T, N)]       (T = pulls to obtain the target without spark)
probability spark is needed     = P(T > N)
```

| Banner | Spark N | P(target before spark) | E[min(T, N)] | Comment |
|---|---|---|---|---|
| Config A featured (pity + 50/50) | 100 | 63.4% | 78.1 | Pity already bounds at 180; a spark at 100 is a big generosity boost |
| Config A featured | 150 | 80.0% | 92.3 | Barely changes the mean (93.45); acts as reassurance only |
| No pity, 0.3% specific featured | 300 | 59.4% | 198.0 | Unbounded → worst case 300; mean falls from 333 |
| No pity, 0.3% specific featured | 200 | 45.2% | 150.6 | More than half of players need the spark |

Guidance: in pity-free systems, set N between the no-pity median and mean for the target (231–333 pulls for a 0.3% item) so the spark is a real ceiling, not decoration. Prefer sparks that **carry over** or **convert** at banner end over sparks that expire (expiry creates last-day spending pressure).

---

## 7. Duplicate protection and collection maths

### 7.1 Coupon-collector maths

Collecting all k equally likely items with replacement needs on average `k × H_k` draws (H_k = 1 + 1/2 + … + 1/k):

| Set size k | Expected draws (with duplicates) | With no-duplicate pool |
|---|---|---|
| 5 | 11.4 | 5 |
| 10 | 29.3 | 10 |
| 20 | 72.0 | 20 |
| 50 | 225.0 | 50 |

Unequal rates are much worse: a 6-item set with five items at 19.8% and one at 1% needs about 101 draws on average, against 14.7 for six equal items. This is the arithmetic behind **"complete gacha"** (kompu gacha) — a prize for completing a set of random items — which Japan's consumer regulator banned in 2012 and which the studio treats as a dark pattern everywhere.

### 7.2 Duplicate protection patterns

| Pattern | How | Effect |
|---|---|---|
| Duplicates → shards/dust | Fixed conversion by rarity; shards craft chosen items | Bounded collection cost; common in card games |
| Duplicates → upgrades (constellations, limit breaks) | Copies power up the unit | Deep monetization; pay-to-win risk; put most function in copy 1 |
| No-duplicate pool | Owned items removed from the pool until the set is complete | Collection cost = set size; very player-friendly |
| Duplicate cap | After max copies, further copies auto-convert at a fixed rate | Prevents dead pulls |
| Bad-luck protection per item | Guaranteed new item after k duplicates | Predictable progress |

### 7.3 Collection-cost formula with shards

```
cost to finish set via crafting ≈ Σ_missing craft_cost(rarity) − shards already held
weekly_shard_income             = pulls per week × P(duplicate) × shards per duplicate (+ shards from other sources)
craft_cost(top tier)            ≤ 4–6 × weekly_shard_income of a committed free player   (house heuristic: any one
                                  targeted item craftable within 4–6 weeks of normal play)
```

---

## 8. Free-player generosity and banner cadence

Write the generosity target into the contract: "a committed free player obtains one featured item every N banners". Then size free pulls:

```
free_pulls_per_banner = free premium income per banner period / currency per pull
banners_per_featured  = E_featured / free_pulls_per_banner
```

With config A (E_featured = 93.45):

| Free pulls per banner | Banners per featured item |
|---|---|
| 20 | 4.7 |
| 28 | 3.3 |
| 40 | 2.3 |

House band: N between 2 and 5. Above 5, free players feel shut out and churn (and payers lose the community they play with); below 2, there is too little scarcity to sell. Verify the free-income assumption in `economy_sim.py` (model pulls as a converter from gems to `pulls` and the banner as a gate).

**Cadence.** Banner length and rerun policy are economy levers: shorter banners raise spending peaks and pressure; reruns of limited items reduce FOMO resentment. Publish rerun policy where possible.

---

## 9. Chests and loot boxes outside gacha

Casual and mid-core games use chests as reward packaging even when they are not sold directly. Rules:

- **Earned chests** (from wins, milestones) are rewards; their contents still deserve disclosure if chests are also sold or speed-uppable with paid currency.
- **Chest EV**: compute the reference value of the expected contents.

```
EV(chest) = Σ_i P(i) × ref_usd(i)
example: 60% 500 coins ($0.83), 25% 1,500 coins ($2.49), 12% 3 boosters ($1.00), 3% 100 gems ($1.14)
         EV = 0.60×0.83 + 0.25×2.49 + 0.12×1.00 + 0.03×1.14 ≈ $1.27  (sold for 100 gems = $1.14 → EV ratio ≈ 1.12)
```

- **Timer chests** (unlock slots with timers, skip with hard currency) are a session-return mechanic and a speed-up sink; price skips with the concave curve in `currency-architecture.md` §4.3, and never sell the chest's random contents at a premium over EV without disclosure.
- **Transparent chests** (contents shown before opening or buying) keep the excitement of the reveal without the regulatory exposure of paid randomness.

---

## 10. Implementation and statistical verification

**Engineering rules** (see also the RNG checklist in `mechanics-codex`):
1. Server-side rolls for anything paid; seeded, auditable PRNG; append-only pull log with config version.
2. Pure functions for rate schedules (`p(n)`), unit-tested at boundaries: pull s−1, s, H−1, H; guarantee set/cleared; spark threshold.
3. Odds page generated from live config; config change → new version → new disclosure.
4. Telemetry per pull: `gacha_pull` with `banner_id`, `config_version`, `pity_counter`, `guarantee_flag`, `result_tier`, `result_item`, `currency_spent`, `paid_share`.

**Statistical verification.** Sample size to confirm a rate p within ±δ at 95% confidence (normal approximation):

```
n ≈ 1.96² × p(1 − p) / δ²
p = 0.6%, δ = ±0.1 pp   → n ≈ 22,900 pulls
p = 0.6%, δ = ±0.05 pp  → n ≈ 91,600 pulls
p = 5%,   δ = ±0.5 pp   → n ≈ 7,300 pulls
```

Run Monte Carlo of the full schedule in CI (millions of simulated pulls are cheap) and compare the empirical distribution with `gacha_calc.py`. In production, monitor observed rates per config version with the same tolerance; a deviation is a legal incident, not a bug report.

---

## 11. Legal and platform disclosure regimes

Summary for design decisions; details, dates and sources are in §14 and in `legal-ethics`. The `compliance-officer` agent signs off per market before launch.

| Regime | What it requires or restricts (summary) | Design response |
|---|---|---|
| **Apple App Store** | Disclose odds of each item type before purchase of randomized items | Odds page one tap from every paid random purchase |
| **Google Play** | Clearly disclose odds before, and close to, the purchase | Same page; also in-store listing notes where useful |
| **China** | Mandatory public disclosure of random-draw item names and probabilities since May 2017; the NPPA's December 2023 draft with further limits was pulled from its site in January 2024 and its status is unclear (§14) | Full per-item odds, draw records; verify current rules with a local publisher |
| **South Korea** | Statutory mandatory disclosure of probability-item information from March 2024; consumer regulator fined Nexon Korea 11.6 billion won in January 2024 over undisclosed odds changes (§14) | Per-item odds everywhere the item is advertised; change logs; zero tolerance for silent rate changes |
| **Japan** | "Complete gacha" (prize for completing a set of random items) treated as unlawful since 2012; industry self-regulation on rate display | No kompu mechanics; display rates; consider expected-cost caps per target |
| **Belgium** | Paid loot boxes treated as illegal gambling since 2018 | Disable paid random items for Belgian storefronts; offer direct purchase |
| **Netherlands** | Regulator's enforcement against packs overturned by the highest administrative court (2022); no effective ban | Disclosure and age-gating anyway; watch EU developments |
| **Brazil** | Sale of loot boxes to under-18s banned from March 2026 (ECA Digital); court enforcement in 2026 | Age assurance; disable paid random items for minors; disclose probabilities |
| **Australia** | Classification: paid chance items → at least M; simulated gambling → R18+ (from Sep 2024) | Rating impacts store age; avoid casino-like presentation |
| **US (FTC)** | Enforcement against misleading odds and virtual-currency cost presentation; minors' purchases (HoYoverse, January 2025: $20M penalty, parental consent for loot boxes under 16, odds and exchange-rate disclosure; Epic Games, December 2022) | Show odds and real-money cost; parental consent for minors |
| **EU-wide** | Consumer-protection principles on virtual currency; a possible Digital Fairness Act later | Real-money price transparency; minors protections |

**Default architecture for compliance:** one economy, with a per-storefront and per-age **feature flag** that swaps paid random purchases for deterministic equivalents (same items, direct prices or exchange tokens). Building this from day one costs little; retrofitting it costs a lot.

---

## 12. Transparent alternatives

| Alternative | How it works | Keeps | Loses | Reference pattern |
|---|---|---|---|---|
| **Direct purchase** | Buy the exact item | Trust, simplicity | Reveal excitement | Rotating item shops in live-service games |
| **Selector tickets** | Pick any item from a set | Choice; targetable | Some excitement | Common as gacha milestone rewards |
| **Exchange shop** | Pull remnants or event tokens buy items | Long-term certainty | — | Spark-style exchanges |
| **Preview ("transparent") boxes** | Contents visible before buying; reroll costs disclosed | Reveal moment | Pure surprise | Increasingly used to reduce loot-box exposure |
| **Earned-only randomness** | Random rewards only from play, never purchasable or speed-uppable | Excitement | Direct revenue from randomness | Free chests, daily spins |
| **Fixed-sequence drops** | Deterministic reward schedule disguised as variety | Predictability | Surprise | Progression roads |
| **Season pass** | Fixed rewards for play over a season | Engagement alignment | Unbounded spend | `pricing-and-offers.md` §11 |
| **Crafting** | Collect materials to build chosen items | Agency | — | Dust/shard systems |

A widely discussed precedent (background, verify): a major mobile title (Supercell's Brawl Stars) removed paid loot boxes in 2022 in favour of a progression road, later reintroducing random rewards in an earned form. The general lesson: randomness can remain as **earned** delight while purchases become **deterministic**.

---

## 13. Pre-launch checklist

- [ ] §1 decision recorded in the contract (`monetization.ethics`), with the removal-test answer.
- [ ] Tier and per-item rates, consolidated rates, pity, guarantee, spark and carry-over rules disclosed in one tap from every paid pull.
- [ ] Expected and worst-case real-money cost shown as ranges in local currency.
- [ ] Free generosity target N (banners per featured item) between 2 and 5, verified in the sim.
- [ ] 10-pull floor; no empty multi-pulls; no kompu (set-completion prize) mechanics.
- [ ] Duplicate protection: every duplicate converts to something useful at a published rate.
- [ ] Per-storefront and per-age flags: Belgium off; Brazil minors off; other markets per `compliance-officer`.
- [ ] Server-side rolls; config versioned; Monte Carlo CI test against `gacha_calc.py`; production rate monitoring.
- [ ] Spending insights and optional limits; no pressure timers on random purchases; no offers of random items to minors.
- [ ] `compliance_preflight.py --project DIR` passes before every store build.

---

## 14. Volatile facts (as of Oct 2026 — verify before relying)

Sourced in the October 2026 research:
- **Apple**: App Review Guideline 3.1.1 requires apps offering randomized virtual items for purchase to disclose the odds of receiving each type of item before purchase (background, long-standing) — [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/).
- **Google Play**: games offering randomized virtual items from a purchase must clearly disclose odds in advance of and close to the purchase (background, long-standing) — [Play Console Help: Payments policy](https://support.google.com/googleplay/android-developer/answer/9858738).
- **Brazil**: the ECA Digital law (Law 15.211/2025, signed Sep 2025) bans loot-box sales to under-18s, in force March 2026. On June 9, 2026 a Brazilian court ordered Riot Games to pay damages (reported figures conflict: €2.5M or $3M) and to add age verification and probability disclosure — [Sheep Esports](https://www.sheepesports.com/articles/brazil-court-orders-riot-games-to-pay-eur2-5m-over-league-of-legends-loot-boxes/en); [Programming Insider](https://programminginsider.com/loot-boxes-regulation-and-where-the-line-sits-in-2026/). The primary text of the loot-box article was not retrieved.
- **Belgium**: paid loot boxes banned under gambling law since 2018; reported penalties up to €800k and five years' prison, doubled where minors are involved — [Programming Insider](https://programminginsider.com/loot-boxes-regulation-and-where-the-line-sits-in-2026/).
- **Netherlands**: sources describe the regulator's approach as reversed by the courts; background: in March 2022 the Council of State overturned the penalty against EA over FIFA packs, finding packs were not a separate game of chance, so there is no effective Dutch ban — [Programming Insider](https://programminginsider.com/loot-boxes-regulation-and-where-the-line-sits-in-2026/).
- **Australia**: games classified after Sep 22, 2024 with paid chance-based items are rated at least M; simulated gambling is R18+ — [PCWorld](https://www.pcworld.com/article/2464538/all-games-with-loot-boxes-will-be-rated-m-or-higher-in-australia.html).
- **EU**: a Digital Fairness Act could bring an EU-wide approach, reportedly not before 2028 — [Programming Insider](https://programminginsider.com/loot-boxes-regulation-and-where-the-line-sits-in-2026/).

Checked on 2026-10-20 against the sources linked below (the primary regulator texts were not all retrievable; confirm with `compliance-officer` and local counsel before relying):
- **China**: a Ministry of Culture notice (Culture Market Release [2016] No. 32, issued December 2016) took effect on May 1, 2017. It requires publishers to announce the name, content, quantity and draw probability of virtual items and services obtained by random draw, to publish draw results, and to keep records for inspection (reported as more than 90 days) — [China Law Translate](https://www.chinalawtranslate.com/en/ministry-of-culture-notice-regarding-strengthening-regulation-online-gaming-operations/), [Mondaq](https://www.mondaq.com/china/gaming/558200/china-ministry-of-culture-released-new-regulation-on-online-game-operation); the operative text is cited from unofficial translations. The NPPA's draft online-game measures were published on December 22, 2023 for comment until January 22, 2024. Reported provisions included spending limits and a direct-purchase option for loot-box or gacha content. The draft was removed from the NPPA website around January 23, 2024 with no formal retraction notice, and its later status is unconfirmed — [DT Next news report](https://www.dtnext.in/lifestyle/technology/china-regulator-removes-draft-video-game-rules-from-website-shares-jump-763035), [Insider Gaming](https://insider-gaming.com/chinese-gaming-rules-tencent/).
- **South Korea**: an amendment to the Game Industry Promotion Act made disclosure of probability-type item information mandatory from March 2024 (this date comes from Nexon's own appeal argument that the duty only took effect then, as reported by [Inven Global](https://www.invenglobal.com/articles/20319/nexons-maplestory-appeals-fine-as-seoul-high-court-resumes-hearing-in-april); the exact day, the statute text and the monitoring body were not confirmed here). In January 2024 the Korea Fair Trade Commission fined Nexon Korea 11.6 billion won (about US$8.8 million) for undisclosed changes to the odds of MapleStory Cubes, under the Act on Consumer Protection in Electronic Commerce; Nexon appealed to the Seoul High Court — [Anime News Network](https://www.animenewsnetwork.com/news/2024-01-05/korean-ftc-fines-nexon-usd8.8-million-for-allegedly-manipulating-draw-odds-in-maplestory-game/.206181), [TechRadar](https://www.techradar.com/gaming/nexon-fined-almost-dollar9-million-for-allegedly-changing-probability-structure-of-certain-items-in-maplestory-without-informing-players).
- **Japan**: in May 2012 the Consumer Affairs Agency said "complete gacha" (kompu gacha) violated the Act against Unjustifiable Premiums and Misleading Representations, with enforcement from July 2012; GREE and other operators withdrew the mechanic in May 2012, and the Platform Liaison Council issued its own guidelines — [Bloomberg](https://www.bloomberg.com/news/articles/2012-05-18/japan-consumer-agency-says-complete-gacha-game-feature-illegal), [Game Developer](https://www.gamedeveloper.com/business/why-quot-kompu-gacha-quot-was-banned), [Monolith Law Office](https://monolith.law/en/general-corporate/game-random-complete-illegal). Current industry rate-display guidelines were not checked.
- **United States**: the FTC announced on January 17, 2025 a settlement with Cognosphere (HoYoverse) over Genshin Impact: a $20 million civil penalty; a ban on letting children under 16 buy loot boxes without a parent's affirmative express consent; required disclosure of loot-box odds and of exchange rates for multi-tiered virtual currency; and COPPA terms (verifiable parental consent before collecting data from under-13s, and deletion of previously collected under-13 data). It was a stipulated order filed in the Central District of California that needed the judge's approval; press coverage later described it as finalized, which was not confirmed here — [FTC press release](https://www.ftc.gov/news-events/news/press-releases/2025/01/genshin-impact-game-developer-will-be-banned-selling-lootboxes-teens-under-16-without-parental), [FTC case page](https://www.ftc.gov/legal-library/browse/cases-proceedings/222-3152-cognosphere-llc-us-v). Related precedent: [FTC v. Epic Games (December 2022)](https://www.ftc.gov/news-events/news/press-releases/2022/12/fortnite-video-game-maker-epic-games-pay-more-half-billion-dollars-over-ftc-allegations), $275 million for COPPA violations plus $245 million in refunds over dark-pattern charges.
- **United Kingdom**: the government's response of July 18, 2022 chose industry self-regulation over amending the Gambling Act 2005; the games industry's "Principles and guidance on paid loot boxes" (11 principles, drafted by a technical working group convened by DCMS) followed in July 2023, with a 12-month review commitment. Independent research later reported weak compliance — [CMS](https://cms.law/en/gbr/legal-updates/loot-boxes-11-new-principles-for-an-industry-led-approach), [Lewis Silkin](https://www.lewissilkin.com/insights/2023/07/24/new-uk-principles-and-guidance-on-loot-boxes-published-102ik8a), [5Rights Foundation](https://5rightsfoundation.com/research-reveals-non-existent-enforcement-of-industry-led-standards-on-loot-boxes).
- **Brawl Stars precedent**: removal of paid boxes in 2022 is widely reported; check Supercell's own announcements for exact details.
