# Market Overview 2026

This file summarises the state of the mobile games market as of October 2026, based on the research notes compiled for this plugin, which draw mainly on Sensor Tower releases and trade-press digests. The headline is a mature, flat market: spending roughly steady, downloads falling, growth coming from monetising and retaining existing players through live-ops, with hybrid-casual the fastest-growing slice in the data reviewed. All numbers are volatile and many come through secondary summaries; the stable reading skills in the first half matter more than any single figure. Volatile facts are collected in one dated section with source URLs; verify before relying on them.

## Contents
1. How to read market numbers (stable)
2. Structure of the market (stable)
3. Revenue models and platform economics (stable)
4. Reading the 2025-2026 picture (interpretation)
5. Implications for an AI-built or small-team game
6. Benchmarks and how to use them
7. Volatile facts (as of Oct 2026 — verify)
8. Freshness protocol
9. Checklists
10. Segment taxonomy
11. Signals dashboard
12. Worked bottom-up sizing example
13. Scenario thinking
14. Common misreadings

## 1. How to read market numbers (stable)

| Question | Rule |
|---|---|
| Who produced the number? | Prefer the primary publisher (data firm or platform) over a secondary blog |
| What is measured? | Consumer spend (gross, before store fee) vs developer revenue (net) differ; IAP only vs IAP plus ads differ; check it |
| What period and geography? | Calendar year vs rolling; global vs ex-China; store coverage (Android in China is fragmented) |
| What is estimated? | Third-party firms model revenue and downloads from panels and store ranks; small apps carry big error |
| Is it a percent change? | Ask the base: a large percent on a small base is not a large market |
| Is it nominal? | Currency and inflation affect year-on-year; compare in local terms for regional questions |

Never mix numbers from different definitions in one sentence ("IAP market of X and ad market of Y" must come from one source or be labelled).

## 2. Structure of the market (stable)

- **Revenue concentration.** A small number of titles and publishers take a large share of grossing; the long tail earns little. Plan for a power-law outcome: the median new game does not earn back its cost.
- **Genre economics.** Casual and hyper-casual rely on advertising; mid-core and strategy rely on high-spending minority players (whales) and social competition; hybrid-casual adds meta and IAP to casual loops.
- **Live-ops dependence.** Revenue of top games is dominated by long-lived titles with constant events; the market rewards retention and cadence, not launches.
- **Acquisition is the tax.** Cost per install rises with competition and privacy changes; success depends on creative testing, retention and monetisation payback.
- **Platform split.** Two stores dominate outside China; in China, Android distribution runs through multiple stores and a licence regime; PC and console are separate markets with different dynamics, but cross-play and PC mobile ports blur lines for strategy and RPG.
- **Publisher platforms.** Large platforms (UGC and instant-play) form their own markets; see the AI landscape reference.

## 3. Revenue models and platform economics (stable)

| Model | Typical genres | Strengths | Risks |
|---|---|---|---|
| Ads (rewarded, interstitial, banner) | Hyper-casual, casual, idle | High reach, low friction | Low ARPU, ad fatigue, quality perception, privacy rules |
| In-app purchase (consumable) | Mid-core, RPG, strategy, puzzle | High ARPPU from a minority | Ethics, regulation (loot boxes), whale dependence |
| Subscription / pass | Casual and mid-core | Predictable revenue | Needs ongoing value |
| Hybrid (ads + IAP + pass) | Hybrid-casual, merge, puzzle | Monetise payers and non-payers | Complexity, economy balance |
| Premium (paid) | Niche mobile, Apple Arcade-style catalogues | Clean design | Small audience, discovery |

Rules:
- Match model to region (see `references/genre-and-regional-trends.md`).
- Platform fee levels, programs and alternative payment rules change; always check the volatile section and recompute payback.
- Unit-economics identity: lifetime value over a horizon must exceed cost to acquire by a margin that covers overhead and live-ops; model with `retention_ltv.py`.

Payback quick check: cost per install C; cumulative revenue per install over 30 days R30. If R30 / C is below the break-even you can afford, you need either better retention, better monetisation or cheaper installs; ask which lever the soft launch can move.

## 4. Reading the 2025-2026 picture (interpretation)

As reported in the sources in section 7:
- Spending was roughly flat in 2025 and slightly down in the first half of 2026, while downloads fell more steeply. Read: fewer, more valuable installs; the market is being fought on retention and monetisation efficiency.
- Growth is concentrated in genres where meta layers and live-ops lift lifetime value; hybrid-casual is described as having the biggest spending jump in 2025, and strategy was the hot genre.
- Ad revenue is split mainly between casual and hyper-casual, with hybrid taking a smaller but growing share; in markets where ad-supported play dominates, ads are the majority of game revenue, while in mature markets IAP dominates.
- Regulation and platform rulings are widening payment options in some regions; margin structure for direct-to-consumer web shops is improving for large publishers. Small studios should verify the cost and compliance of alternative billing before building around it.

What to conclude for planning:
1. Do not plan on a rising tide; plan on retention and efficient acquisition.
2. Prefer genres with proven live-ops economics and short-loop prototyping (hybrid-casual and puzzle).
3. Budget soft launch to prove payback, not just retention.

## 5. Implications for an AI-built or small-team game

- **Production cost fell, distribution cost did not.** AI tooling cuts content and code cost; the bottleneck moves to discovery, acquisition and retention. Differentiate on the loop and polish.
- **Volume is not an advantage.** If many teams can produce games quickly, the supply of mediocre games grows; chart competition is on quality signals (retention, reviews, creative performance).
- **Hybrid-casual and puzzle fit** a lean pipeline: short loops, data-driven level difficulty, lower content cost per minute.
- **Avoid the most expensive formulas** (large-scale 4X strategy, PvP-heavy mid-core) unless there is a distinctive angle and live-ops capacity; these are dominated by well-funded incumbents.
- **Ethics and policy matter more** as scrutiny of loot boxes, minors and AI-generated content increases; build compliance into the pipeline (`legal-ethics`).
- **Owning native builds** keeps access to both stores and avoids dependence on a UGC platform's feed and terms.

## 6. Benchmarks and how to use them

Retention benchmarks vary widely by source, genre, platform and cohort year. Use them as screening heuristics only:
- Medians for the broad mobile market are low (single digit percent by day 7 or 30 in widely repeated summaries); a marketed title needs far higher.
- A practitioner "viability screen" circulates for D1/D7/D30; treat it as a working hypothesis. The D7/D1 ratio is a diagnostic: low means a first-session or onboarding problem; mid means weak engagement in days 2-5.
- iOS cohorts often show higher early retention than Android in published splits, with exceptions by region.
- "Time to fun": if the first aha moment takes much more than about a minute and a half, expect a drop-off in second sessions (practitioner heuristic).
Use your own genre cohorts as soon as you have them; see `player-analytics`.

## 7. Volatile facts (as of Oct 2026 — verify)

| Fact | Source |
|---|---|
| Sensor Tower State of Gaming 2026 (2025 data): mobile game in-app purchase revenue rose about 1% to about $82B; downloads about 52B; growth attributed to live-ops, events and IP collaborations; premium revenue on Steam reported about $12B in the same release | https://sensortower.com/press/press-release-sensor-tower-state-of-gaming-gaming-drove-52-billion-downloads-82b-iap-revenue-on-mobile-and-12b-premium-revenue-on-steam |
| Hybrid-casual had the largest spending increase in 2025 (about +17.1%, from $3.5B to $4.2B, as reported). First half of 2026: mobile game IAP about $40B (down about 2% year on year), downloads about 24B (down about 12%). Block Blast! reported as top for downloads; Last War, Honor of Kings and Whiteout Survival reported as leading grossing in Q1 2026 | https://mobilegamer.biz/data-digest-sensor-towers-h1-analysis-hay-days-comeback-julys-top-games-big-krafton-numbers-and-more/ |
| Ad monetisation split (Feb to Apr 2026): casual and hyper-casual each about 40% of game ad revenue, hybrid about 16%, mid-core about 4%; ads about 70.3% of game revenue in India versus about 22.1% in the US (Jan to May 2026); in mature markets (US, Canada, Korea, Japan) IAP reported at about 77-90% of revenue | https://gamedevreports.substack.com/p/sensor-tower-mobile-game-ad-monetization and https://sensortower.com/blog/gaming-deep-dive-ad-monetization-report |
| Retention medians (GameAnalytics data via secondary write-ups, 16,000+ games): D1 about 22%, D7 just under 4%, D30 about 0.7-0.8%; top 1% about 64-68% D1 | https://blog.playio.co/d1-d7-d30-retention-benchmarks-2026 and https://segwise.ai/blog/mobile-gaming-app-user-retention-strategies |
| Apple EU: a new single business model effective Oct 1 (Apple's announcement is dated Aug 18, 2026): IAP 26% standard / 15% reduced; alternative payment processing 20% / 10%; link-out purchases 15% / 10%; a 5% Core Technology Commission for transactions in apps distributed outside the App Store, replacing the Core Technology Fee; child-safety rules (no link-outs in Kids-category or under-13 apps, parental gate for under-18 apps using alternative payments or link-outs). Checked 2026-10-20 | https://www.apple.com/newsroom/2026/08/apple-announces-changes-for-apps-in-the-european-union/ and https://developer.apple.com/support/apps-in-the-eu/ |
| Apple upload requirements (checked 2026-10-20): since Apr 28, 2026 apps must be built with Xcode 26 or later and the 26 SDKs; since Sep 9, 2026 uploaded iOS apps must target iOS 13 or later | https://developer.apple.com/news/upcoming-requirements/ |
| Hybrid-casual IAP growth "37%" appeared in secondary sources with conflicting years; the airflux.ai blog page that was cited for it now returns 404, so the figure has no working source here. Do not cite it | (no working source; the airflux.ai URL is dead) |
| Google Play: US billing and link-out terms changed following the Epic v. Google settlement; fee rates reported in secondary sources, verify the current schedule | https://www.stash.gg/blog/blog-epic-v-google-settlement-update-april-2026 |

Notes: no primary 2026 benchmark report on hybrid-casual ARPDAU, ad/IAP split or retention was found in the research; only secondary summaries of Sensor Tower data. Strategy as the hot 2025 genre is from a secondary summary of Sensor Tower State of Mobile 2026 and should be verified against the original.

## 8. Freshness protocol

1. Before using any number in a pitch, open the source URL and confirm the figure, period, geography and definition.
2. Record the date you checked next to the number.
3. Anything older than two quarters in a fast-moving area (fees, chart leaders) is stale; refresh.
4. When two sources conflict, report the range and why (definition, period) rather than picking one.
5. Prefer primary sources: Sensor Tower and AppMagic public reports, platform developer notices, company filings.

## 9. Checklists

Market sizing checklist:
- [ ] Defined the addressable segment (genre, platform, region) before looking at numbers
- [ ] Used one definition of revenue throughout
- [ ] Labelled estimates versus reported figures
- [ ] Listed three comparables and their reported performance with dates
- [ ] Included a bottom-up sanity check (installs x conversion x ARPPU)

Pitch fact checklist:
- [ ] Every market figure has source, period, date
- [ ] No unsourced growth claims
- [ ] Platform fee assumptions match the current published schedule
- [ ] Conflicts disclosed

Bottom-up sizing formula (use when top-down numbers are not available):
Revenue = installs x (payer conversion x ARPPU + ad ARPDAU x active days). Replace every term with an estimate range from comparables, then compute low/likely/high.

## 10. Segment taxonomy (stable)

Use consistent segment names so comparisons are valid. Data firms draw the lines differently; record which taxonomy a source uses.

| Segment | Defining traits | Monetisation | Session | Production profile |
|---|---|---|---|---|
| Hyper-casual | One mechanic, instant play, minimal meta | Ads almost entirely | Seconds to a minute | Very cheap, very fast, very short life |
| Casual | Simple loop with levels or modes, light meta | Ads plus modest IAP | 2-5 minutes | Moderate content volume |
| Hybrid-casual | Hyper-casual core loop plus meta layer (collection, progression, events) | Ads plus IAP and pass | 3-8 minutes | Cheap prototypes, live-ops needed |
| Puzzle / match / merge | Level- or board-based, difficulty curves | Boosters, lives, ads | 3-10 minutes | Data-driven levels; heavy level content |
| Midcore (RPG, shooters, action) | Character progression, collection, competition | IAP, gacha, passes | 5-20 minutes | Expensive; art and systems heavy |
| Strategy / 4X | Base building, timers, alliances | High-ARPPU IAP | Many short sessions | Expensive; social and live-ops heavy |
| Casino / social casino | Slots and card variants | Virtual currency IAP | Variable | Regulated, highly specialised |
| Idle / incremental | Automation and prestige loops | Ads and IAP | Short, frequent | Cheap; economy design critical |
| Simulation / lifestyle | Building, decoration, role-play | IAP and ads | Medium | Content treadmill |
| Premium and subscription catalogues | Paid up front or catalogue | Fixed fee | Longer | Niche; discovery depends on curation |

## 11. Signals dashboard for a market scan

Collect these per comparable and per country; plot or tabulate so patterns appear.

| Signal | Source type | What it tells you | Caveat |
|---|---|---|---|
| Top free and top grossing chart rank over 8-12 weeks | Store charts, chart trackers | Stability of demand | Paid UA can inflate free ranks |
| Estimated downloads and revenue | Third-party estimates | Rough scale | Modelled; small-app error |
| Rating count and average | Store pages | Audience size, satisfaction | Prompting patterns bias ratings |
| Update cadence | Version history | Live-ops intensity | Cosmetic updates inflate |
| Event cadence | Patch notes, in-game | Monetisation levers | Needs playing the game |
| Ad creative volume and longevity | Ad libraries | Acquisition spend and what works | Not revenue |
| Review themes | Review text | Unmet needs and pain | Sampling bias |
| Search interest and keyword difficulty | ASO tools | Discoverability | Tool estimates |
| Community size | Social platforms | Brand strength | Not retention |

Triangulation rule: a title counts as "proven demand" only when at least two independent signals agree over multiple weeks (for example stable chart rank plus continuous ad creatives plus steady updates).

## 12. Worked bottom-up sizing example

Question: what could a hybrid-casual puzzle game earn in year one in two English-speaking markets, if it reaches comparables' lower-quartile performance?
1. Installs: planned paid plus organic installs = I (a range based on budget divided by an assumed cost per install, plus an organic multiplier taken from comparables). Do not use a precise value until soft launch measures it.
2. Payer conversion p and ARPPU a for IAP, from comparable estimates or your own early data; ads revenue per daily active user d, with average active days D per install from the retention curve.
3. Revenue per install = p x a_ltv + d x D, where a_ltv is the payer's lifetime spend inside the horizon.
4. Total = I x revenue per install; subtract store fees and ad network fees; compare to cost of acquisition and fixed costs.
5. Run low, likely and high. If low is far below break-even and high barely clears it, the project is a gamble; seek a higher-probability variant or accept the risk deliberately.
Sensitivity: rank the terms by how much they move the total; the top two terms are your soft-launch hypotheses.

## 13. Scenario thinking

| Scenario for next 12 months | Signal to watch | Response |
|---|---|---|
| Flat spend, falling downloads continues | Quarterly revenue and downloads releases | Favour retention and efficient UA; reduce launch cost |
| Alternative payment adoption accelerates | Fee schedule changes, publisher announcements | Evaluate web shops for payers; check compliance |
| Generative AI floods stores with similar games | Chart composition, review sentiment | Differentiate on craft; invest in feel and original IP |
| Platform cracks down on low-quality or AI-disclosure | Policy updates | Keep provenance and disclosure in compliance checklist |
| Strategy and hybrid growth saturates | New-release performance in the genre | Look for adjacent sub-genres |

## 14. Common misreadings

- "Downloads fell, so the market is dying": revenue fell far less; the market is consolidating toward higher-value installs.
- "Genre X earns the most": earnings concentrate in a few titles; the median entrant in the top-earning genre may earn little.
- "Ads are dead": ad revenue remains the dominant model in casual segments and in some regions.
- "Hybrid-casual is easy": the prototype is cheap but retention and live-ops decide survival.
- "A rank-one title proves the formula": it may reflect a single marketing success or a one-off event; look at its curve over time.
- "iOS-only is enough": depends on region and genre; Android reach dominates in some markets.

## 15. Questions to ask any market report
1. Who paid for it, and what do they sell? A data vendor wants you to need data; a network wants you to believe ads are growing.
2. Does the headline match the table? Check the denominators.
3. Is the sample the whole market or only the vendor's panel?
4. Are the top titles driving the average? Ask for the median or the distribution.
5. What changed in methodology since the last edition?
6. What would make the opposite conclusion true?

## 16. How the volatile numbers feed decisions
- If you must quote growth, quote the period and direction ("flat in 2025, slightly down in H1 2026 per the cited releases") rather than a bare percentage.
- If a number drives a gate or budget (for example payback assumptions), store its source and check date in the contract's assumptions list so the next reviewer can refresh it.
- If a fee schedule enters your unit economics, keep it as a named parameter in the model so it can change without rewriting the model.
