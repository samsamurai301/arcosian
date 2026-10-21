# Genre and Regional Trends

This file gives a practical view of which mobile genres have been rising, steady or declining from 2024 to 2026 and what each major region rewards. It is deliberately qualitative: genre and country rankings change quickly and most figures come from paid reports, so the file names directions, mechanisms and the questions to verify rather than quoting rankings. Where research notes provide reported data points they are cited in the volatile section. Treat region notes as hypotheses to confirm with current store charts and a soft launch.

## Contents
1. How to use this file
2. Genre trend map 2024-2026
3. Genre detail: rising
4. Genre detail: steady
5. Genre detail: declining or crowded
6. Region profiles (US, China, Japan, Korea, SEA, LATAM, MENA, India, Europe)
7. Region by genre fit matrix
8. Soft-launch market selection
9. Localisation and cultural checklist
10. Volatile facts (as of Oct 2026 — verify)
11. Research prompts

## 1. How to use this file
1. Pick a candidate genre; read its section for the mechanism behind its trend (mechanisms outlast rankings).
2. Pick candidate regions; check fit in the matrix and the region profile.
3. Verify with current charts and ad libraries (see `references/ai-gamedev-landscape-and-methods.md`).
4. Write the assumption into the design contract and test it at soft launch.

## 2. Genre trend map 2024-2026

| Genre | Direction (qualitative) | Mechanism | Fit for small or AI-built team |
|---|---|---|---|
| Hybrid-casual | Rising | Casual loop plus meta and live-ops raises lifetime value | High |
| Puzzle (match, block, merge) | Steady to rising | Evergreen audience, level content scales, ads plus boosters | High |
| 4X and strategy | Strong in 2025 | Social loops, deep monetisation, long lifetime | Low (expensive, live-ops heavy) |
| Idle and incremental | Steady | Low production cost, ad-friendly | High |
| Midcore RPG and gacha | Steady, concentrated | Collection and events, strong IP | Low |
| Hyper-casual | Under pressure | Ad-economy squeeze, short life | Medium (as a prototype funnel) |
| Casual-simulation (lifestyle, cooking, decorating) | Steady | Content treadmill and events | Medium |
| Battle royale and PvP shooters | Mature | Esports and skill, high acquisition cost | Low |
| Social casino | Steady | Specialised, regulated | Low |
| Card and auto-battler | Mixed | Depth for a subset, strong in specific regions | Medium |
| Roguelite | Rising in both PC and mobile ports | Replayability, buildcrafting | Medium |
| Cozy and narrative | Rising niche | Audience seeking calm | Medium |
| Instant and UGC platforms | Emerging | Distribution via feeds, tools | Medium (see AI landscape) |

(Directions come from trade commentary and the cited Sensor Tower summaries; verify before using.)

## 3. Genre detail: rising

### Hybrid-casual
- Core: a hyper-casual-style verb with a meta wrapper (collections, base building, progression), monetised by ads and IAP.
- Why it works: cheap to prototype, testable early with creative and retention data, and benefits from live-ops.
- Risks: retention often depends on the meta, which is where content cost hides; ad and IAP balance needs care; many entrants clone the same mechanics.
- Decision tips: prototype the verb in days; run creative tests before building meta; commit to meta only if D1 and early engagement pass thresholds.

### Puzzle: match, block, merge
- Core: short sessions with a clear success state; difficulty curves and boosters; merge games add collection and orders.
- Why it works: broad demographics, strong lifetime, bots can estimate difficulty.
- Risks: dominated by long-lived incumbents; new entrants need a clear twist (theme plus meta), good onboarding and a level pipeline.
- Decision tips: use solvers and bots to calibrate difficulty (`puzzle_solver.py`, `match3_sim.py`); invest in feel and clarity.

### Roguelite and deck-builder on mobile
- Core: runs of 10 to 25 minutes, permanent upgrades, build variety.
- Why it works: replayability from systems rather than content; good for small teams.
- Risks: session length can clash with mobile interruptions; need save-anywhere design and pause-friendly runs.
- Decision tips: design runs that tolerate being interrupted; offer a quick-run mode.

### Cozy and narrative niches
- Core: comfort, creativity, gentle progression.
- Why it works: audience seeking low-stress play, strong community and word of mouth.
- Risks: small revenue per user; discovery.
- Decision tips: aim at premium or low-pressure monetisation; invest in art direction and audio.

## 4. Genre detail: steady

### Idle and incremental
Low cost, ad-friendly, long-tail; evergreen but crowded; success depends on economy design and prestige loops (`economy-design`).

### Midcore RPG and gacha
Revenue concentrated in a handful of titles driven by IP and live-ops. A small team should avoid unless there is a niche art or mechanic hook. Legal exposure on gacha and loot boxes varies by region (`legal-ethics`).

### Casual simulation, cooking, decoration
Stable and event-driven. Requires a steady content pipeline; consider procedural variety and community events.

### Card and auto-battler
Strong in some regions; mixed elsewhere. Balance cost is high; AI agents can help simulate matchups but taste and fairness still need human checks.

## 5. Genre detail: declining or crowded

### Hyper-casual
Reported as under pressure as ad revenue and acquisition economics shifted, and as its best ideas migrate into hybrid-casual. Useful as a testing ground for verbs and creatives, not as a standalone business for most teams.

### Battle royale and competitive shooters
Mature, expensive, dependent on matchmaking pool and esports ecosystem. Avoid without server and operations capability.

### Generic clones
Any genre where five near-identical titles dominate and the entrant has no difference: skip or find a flank.

### Signs a genre is saturating
- New releases rarely reach the top 100 in their first month without large paid acquisition.
- Ad creatives converge on identical hooks.
- Review themes about monetisation worsen across the genre.
- The same publishers hold the top positions for more than a year.

## 6. Region profiles

For each region: what players reward, monetisation mix, practical notes. All hypotheses; verify.

### United States
- Mature market with high revenue per user; IAP dominant in revenue (reported mix in volatile section).
- Rewards polish, brand, strong live-ops; casual puzzle, strategy and casino are strong; high acquisition cost.
- Practical: English first; strict privacy and consumer rules (children's data, state laws); good first soft-launch comparator for English audiences, though costlier than proxies.

### China
- Distinct ecosystem: domestic licensing regime, fragmented Android stores, domestic platforms and super-apps, heavy social and mini-game distribution.
- Requires a publishing partner and a licence for paid games; foreign studios rarely publish alone.
- Rewards social competition, heavy live-ops, strong IP; mini-programs and super-app mini-games form a large casual channel.
- Practical: treat as a separate business with its own compliance and partners; do not plan a self-serve launch.

### Japan
- High revenue per user; strong affinity for IP, collection, gacha RPGs, anime aesthetics, and polished UX; also puzzle and casual.
- Rewards character art, voice, event structure, and respectful localisation; slow, high-trust adoption.
- Practical: native-quality localisation (not machine-only); cultural and legal review of gacha mechanics; strong competition from domestic publishers.

### South Korea
- High revenue per user; MMO and RPG tradition, auto-play and optimised monetisation; strong competitive culture; Android and local stores matter.
- Rewards deep progression, polished art, guild features; regulatory attention to probability disclosure.
- Practical: local partner often helpful; compliance with disclosure rules; high bar for quality.

### Southeast Asia (SEA)
- Large, young, mobile-first, price-sensitive; strong appetite for MOBA, battle royale, casual and social games; payment methods diverse (carrier billing, e-wallets, vouchers).
- Rewards low-spec performance, small download size, localisation to multiple languages, local payment methods and events.
- Practical: Android-first and low-end device focus; cost per install is typically lower than in the US, revenue per user lower; popular soft-launch region for English and local-language tests.

### Latin America (LATAM)
- Large Android audience, price-sensitive, strong casual and sports and action games; payment diversification (local wallets, vouchers).
- Rewards localisation (Spanish and Portuguese, regional variants), low-end optimisation, local events and sports tie-ins.
- Practical: moderate acquisition cost; payment method support matters; currency volatility affects pricing.

### Middle East and North Africa (MENA)
- Young, high smartphone use, strong spending in some Gulf markets; popular strategy, card and shooter games; Arabic localisation and right-to-left layout are required.
- Rewards cultural alignment, Arabic quality, events around local calendars; content restrictions vary.
- Practical: RTL UI testing, regional content review, careful with religious and cultural sensitivities; Gulf states can show high revenue per user relative to ad cost.

### India
- Massive audience, price-sensitive, ad-supported play dominates; heavy Android and low-end devices; strong casual, card (rummy and similar, which carry real-money regulation) and battle royale titles.
- Rewards small downloads, offline-capable play, vernacular languages, rewarded ads; IAP conversion is low, ad revenue per user also low but volume high.
- Practical: ads are a majority of game revenue in reported data (volatile section); keep real-money gaming separate and consult local legal advice; test payment methods.

### Europe
- Diverse: strong markets in the UK, Germany, France and the Nordics; privacy-conscious regulators; consumer protection and consent rules; multiple languages.
- Rewards quality, privacy transparency, localisation across several languages, premium and subscription acceptance in some markets.
- Practical: GDPR and consent management; loot-box and consumer rules vary by country; fee and billing rules differ under EU digital market regulation (volatile section in the overview file).

## 7. Region by genre fit matrix

Legend: S strong, M medium, W weak, ? unknown. Hypothesis scale for first-pass screening only.

| Genre | US | China | Japan | Korea | SEA | LATAM | MENA | India | Europe |
|---|---|---|---|---|---|---|---|---|---|
| Hybrid-casual | S | M | M | M | S | S | S | S | S |
| Puzzle | S | M | S | M | M | S | M | M | S |
| Strategy | S | S | M | M | M | M | S | M | S |
| Idle | S | M | M | M | S | S | M | S | S |
| Midcore RPG/gacha | M | S | S | S | M | M | M | W | M |
| Card/auto-battler | M | S | M | S | M | M | S | S | M |
| MOBA/BR | M | S | M | S | S | S | S | S | M |
| Casual sim | S | M | M | M | M | M | M | M | S |
| Premium/narrative | M | W | M | M | W | W | W | W | S |

## 8. Soft-launch market selection

Criteria:
1. Behaviourally similar to the intended core market (language, device mix, spending pattern).
2. Lower and more predictable acquisition cost.
3. Supports the store features and payment methods you need.
4. Legal and privacy requirements you can meet.
5. Enough volume to read retention and early monetisation (a cohort size you can compute from the confidence you need).

Procedure:
1. Choose two markets: one mimic (cheaper proxy) and one true target for calibration.
2. Set cohort-size targets before launch, using `ab_test.py` or `retention_ltv.py` to compute needed sample sizes.
3. Plan a 4 to 8 week read-out; thresholds in the contract.
4. Compare cohorts by platform; do not extrapolate from one device tier.
5. Decide the global rollout order from observed payback, not from assumption.

## 9. Localisation and cultural checklist
- Language quality: native review for each launch language; avoid machine-only for narrative and store copy.
- Layout: text expansion, right-to-left, fonts and glyph coverage.
- Cultural content: gestures, colours, symbols, religious and political sensitivities; age ratings.
- Payments: local wallets, carrier billing, vouchers, price points in local currency.
- Legal: loot box rules, probability disclosure, minors, data privacy, real-money gaming restrictions.
- Events: local holidays and sports calendars in the live-ops plan.
See `accessibility-localization` and `legal-ethics`.

## 10. Volatile facts (as of Oct 2026 — verify)

| Fact | Source |
|---|---|
| Ads were reported at about 70.3% of game revenue in India versus about 22.1% in the US (Jan to May 2026); in US, Canada, Korea and Japan, IAP reported at about 77-90% of game revenue | https://gamedevreports.substack.com/p/sensor-tower-mobile-game-ad-monetization |
| Casual and hyper-casual each about 40% of game ad revenue, hybrid about 16%, mid-core about 4% (Feb to Apr 2026) | https://sensortower.com/blog/gaming-deep-dive-ad-monetization-report |
| Hybrid-casual reported as the fastest-growing spending segment in 2025; Strategy (4X) reported as the hot 2025 genre (secondary summary) | https://sensortower.com/press/press-release-sensor-tower-state-of-gaming-gaming-drove-52-billion-downloads-82b-iap-revenue-on-mobile-and-12b-premium-revenue-on-steam |
| Top titles in Q1 2026 reported: Block Blast! for downloads; Last War, Honor of Kings and Whiteout Survival for grossing | https://mobilegamer.biz/data-digest-sensor-towers-h1-analysis-hay-days-comeback-julys-top-games-big-krafton-numbers-and-more/ |
| EU platform fee model changes reported effective Oct 1, 2026 (Apple) | https://developer.apple.com/news/upcoming-requirements/ |

The region profiles above are qualitative judgement from general industry knowledge, not from the research notes; no regional revenue rankings are quoted because none were verified.

## 11. Research prompts
- Which three games hold the top grossing positions in the target country this month, and how long have they been there?
- Which genres appear in the top 100 new releases of the last 90 days?
- What share of ad creatives in the target country use a given mechanic?
- Which payment methods do top games in that country offer?
- What do one-star reviews in the region complain about?
- What local holidays shape the live-ops calendar?
