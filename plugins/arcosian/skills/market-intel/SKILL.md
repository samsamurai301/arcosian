---
name: market-intel
description: 'Mobile games market intelligence codex: market size and trend reading, genre and regional trends, AI game-creation competitors, and research methods (Sensor Tower, AppMagic, charts, review mining, ad libraries). Use when sizing a market, choosing a genre or region, running a competitor scan, reading store charts, positioning against AI game tools, or checking how fresh a market claim is.'
when_to_use: 'Market sizing, genre or region selection, competitor research, positioning, or validating a market claim in a pitch or concept.'
---

# Market Intelligence

## What this skill gives you
- A method for turning store data into a go / no-go on a genre, region or concept, with the signals that matter and the traps that mislead.
- A snapshot of the 2025-2026 mobile market (clearly labelled volatile) and the structural trends that outlive any single report.
- Genre and regional playbooks: what rises, what declines, what each region rewards.
- A map of AI game-creation competitors and how this plugin differs.
- Concrete research workflows for third-party intelligence tools, charts, review mining and ad libraries, including how to cite and date findings.

## Core models
**1. Market claims decay.** Every number has a source, a period and a publication date; without all three it is not usable. Stable knowledge (how to read a chart, what genres monetise how) is separated from volatile knowledge (sizes, rankings, fees). Volatile facts live in `references/market-overview-2026.md` under a dated section.

**2. Demand, competition, fit.** A concept is attractive when demand is proven (comparables earn or retain), the top of the market is beatable on a specific axis, and your team's strengths fit the winning formula. Score each 1-5 with evidence; skip any concept with demand below 3.

**3. Saturated is not the same as closed.** A big genre with dominant incumbents is hard for generic entries but open to a sharply differentiated sub-genre, a new theme layered on a proven loop, or a better meta. Look for "gaps in the middle": proven loop plus under-served audience, region or aesthetic.

**4. Downloads, revenue and retention tell different stories.** Downloads measure reach, revenue measures monetisation, retention measures fit. A rising chart position built on paid acquisition is not proof of organic demand. Triangulate at least two signals.

**5. Revenue models by genre.** Ads dominate casual and hyper-casual; in-app purchases dominate mid-core and strategy; hybrid-casual blends both. Regions differ in the ads-to-IAP mix. Choose a model that fits where your players live (see regional file).

**6. Estimates from tools are estimates.** Third-party revenue and download numbers are modelled; error is larger for small apps, niche regions and non-store channels. Use them for ranking and direction, not for accounting.

**7. Platform and channel shifts change the margin.** Fee changes, web shops and alternative billing alter unit economics; treat them as volatile and recompute payback when they move.

**8. The window is time-bound.** Trends move: a mechanic that tops the charts today may be a crowded format in a year. Estimate time-to-market and ask whether the window will still be open.

## Decision procedures
**Genre/concept go-no-go (half a day)**
1. List 5-10 comparables (top grossing and top free charts in target countries, plus 2-3 breakout new releases).
2. For each, record: core loop, monetisation, release date, update cadence, rating, review themes, ad creatives, estimated revenue and downloads (source and date).
3. Identify the winning formula (what all share) and the open flank (what none do well).
4. Score demand, competition, fit (model 2) and write the one-sentence differentiation.
5. Decide: build the prototype, refine the concept, or drop. Record in the one-pager and the contract's assumptions list.

**Choosing launch markets**
1. Decide the monetisation model first (ads vs IAP vs hybrid).
2. Shortlist regions where that model performs and where the genre has proven demand (regional file).
3. Check localisation cost, payment methods, legal and platform factors (`accessibility-localization`, `legal-ethics`).
4. Pick one or two soft-launch markets that resemble the target on behaviour but cost less to buy users in; confirm with `marketing-ua`.

**Competitor teardown (2 hours per title)**
1. First-session recording: time to fun, tutorial length, first ad or offer, permissions asked.
2. Economy and meta: currencies, timers, shops, passes, event cadence.
3. Live-ops: event calendar from the last 8-12 weeks (patch notes, store updates).
4. Marketing: ad creatives (ad libraries), store page, keywords, review replies.
5. Weaknesses: one-star themes, complaint frequency.
6. Output a card in the deconstruction format (`deconstruct` skill).

**Review mining** (details in `references/ai-gamedev-landscape-and-methods.md`)
1. Pull 200-500 recent reviews per competitor (own the compliance with store terms).
2. Tag by theme: difficulty, ads, monetisation, bugs, content, social, controls.
3. Count tags per rating band; surface the top three complaints and top three loves.
4. Convert to design requirements with evidence ("ads after every level: 18% of 1-star reviews").

**Claim check** before a pitch or concept goes forward: for each market statement, record source, period, date, and whether it is primary or a secondary summary; downgrade or delete the unsourced.

## Worked example: scoring a concept
Concept: a one-handed merge-puzzle with a cozy theme. Comparables: five merge and puzzle titles across top free and top grossing in two target countries. Demand 4 (several comparables hold chart positions across months, not days). Competition 3 (incumbents are strong on meta but weak on onboarding according to review themes: "too many timers" appears in a large share of low ratings). Fit 4 (small team, art pipeline suits cozy). Differentiator: no energy timers, a calm session loop. Decision: build the prototype, with the assumption "players will trade timer-free sessions for slower monetisation" added to the contract's assumptions list and tested at soft launch. The scores are judgement, so the evidence column (chart dates, review counts, sources) must be filled in or the scores are void.

## Report format for a market scan
1. Question and decision it supports (one line).
2. Method and sources with dates; limits and gaps.
3. Findings in a table: claim, evidence, source, period, confidence.
4. Implications for the concept, region and monetisation.
5. Recommendation and what would change it.
6. Open questions for soft launch.

## Source hierarchy
1. Platform notices and primary data-firm releases.
2. Trade-press digests that quote the primary release.
3. Practitioner blogs and vendor guides (often useful, often biased).
4. Aggregator and directory sites (treat as unverified leads).
When only tiers 3-4 exist, say so in the claim and keep the claim out of pitch headlines.

## Mobile specifics
- Store charts are country-specific and category-specific; compare like with like (country, platform, chart type, time window).
- iOS skews toward higher revenue per user in many markets, Android toward reach, but patterns differ by region; verify locally.
- Install counts include low-quality and incentivised installs; weight retention and rating signals.
- Seasonality (holiday periods, regional events) distorts week-to-week comparisons; compare to the same weeks of the previous year when available.
- Platform policy and fee changes alter margins and channels; check the volatile section before building a model.

## Anti-patterns
| Anti-pattern | Symptom | Fix |
|---|---|---|
| Top-chart copying | "X is number 1, so clone X" | Ask what the clone adds; gap analysis first |
| Single-source numbers | One tool's estimate used as fact | Triangulate; label as estimate |
| Undated claims | "The market is growing" | Source, period, date on every number |
| Survivorship | Only studying hits | Include failed and flat releases |
| Region blindness | US assumptions applied to every market | Use regional file; test in soft launch |
| Trend chasing | Entering a format at its peak | Model time-to-market; look for next gap |
| Review cherry-picking | Quoting vivid reviews | Count themes, not anecdotes |
| AI-hype positioning | Claiming differentiation by using AI | Differentiate by player value |
| Vendor-blog trust | Competitor guides taken at face value | Cross-check with primary source |

## Using the ontology
- Competitor teardowns map to the deconstruction schema (`deconstruction.schema.json`); a market scan produces concept inputs (`concept.schema.json`) and assumptions in the design contract.
- Record market evidence and dates in the project folder (for example `.gamestudio/` market notes) via `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py progress`, and search the codex with `gs.py kb`.
- Model unit economics with `${CLAUDE_PLUGIN_ROOT}/scripts/retention_ltv.py` and test payback assumptions before committing to a region or channel.
- The `market-scan` process skill and workflow run this skill's procedures in parallel; `arcosian:market-analyst` owns it.

## Reference library
| File | What it contains | When to read it |
|---|---|---|
| `references/market-overview-2026.md` | Market size, revenue and download trends, platform and monetisation splits, with sources and a volatile-facts section | Sizing a market, writing a pitch, checking a number |
| `references/genre-and-regional-trends.md` | Rising and declining genres 2024-2026; US, China, Japan, Korea, SEA, LATAM, MENA, India, Europe notes | Choosing genre, region, soft-launch market |
| `references/ai-gamedev-landscape-and-methods.md` | AI game-creation competitors, this plugin's differentiation, research methods and tool workflows | Positioning, competitor research, review and ad mining |

## Related skills
- `production`: turns market evidence into gate thresholds and plans.
- `genre-playbooks`: the genre mechanics behind the market categories.
- `marketing-ua`: acquisition cost, creatives, channels.
- `monetization`: models that fit each market.
- `player-analytics`: your own cohort data to validate market assumptions.
- `game-case-studies`: landmark games that explain why formulas work.
- `legal-ethics`: regional legal constraints (loot boxes, age, data).
