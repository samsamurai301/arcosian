---
name: market-scan
description: Budget-aware competitive and market research for a genre or concept - sources, procedure, competitor matrix, positioning statement and a dated research file. Use when the user says "market research", "who are the competitors", "is this genre saturated", "scan the market for", or before a concept tournament or contract.
argument-hint: "[genre or concept]"
---

# Market Scan

## When to use

Before committing to a concept (`new-game` step 2), when a concept's market score is a guess, or when a live game needs fresh competitor context. The scan informs decisions; it does not predict revenue.

## Inputs

`$ARGUMENTS` is a genre ("merge puzzle"), a concept (path to a concept card or a one-line idea) or empty (use `contract.json` `meta.genre`). Also decide the budget level with the user if not stated: **free** (default: store pages and public articles only), **standard** (adds a trend tool or MCP if configured), **deep** (adds paid analytics the user supplies). Never assume paid access.

## Procedure

1. **Frame the question.** Write it in one line: "Is there a winnable lane for <audience> in <genre> with <hook>?" List what would change the decision (for example "three or more strong incumbents with weak retention reviews").
2. **Load knowledge.** `market-intel` (methods and metrics), `genre-playbooks` (genre norms), `analogy-engine` for comparables. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py kb "<genre> benchmarks" --limit 5`.
3. **Run the workflow.** `/arcosian:market-scan` with `{"target": "<genre or concept>", "budget": "free|standard|deep", "slug": "<slug>"}` fans out research agents (`arcosian:market-analyst`). If workflows are unavailable, do the steps below directly.
4. **Collect sources** by budget (table below). Record each source with URL and access date; unsourced numbers are discarded.
5. **Pick 8 to 12 competitors** in three buckets: market leaders, direct comparables (same loop and audience), and adjacent or rising titles. Include at least two recent launches (last 12 months) if any exist.
6. **Build the competitor matrix** (below). One row per title; mark unknown cells "?" instead of guessing.
7. **Read reviews.** Sample the most recent 1 to 3 star and 4 to 5 star reviews per direct comparable; tag themes (ads, difficulty, progress walls, bugs, content drought, love for a feature). Count themes in your sample and say the sample size; do not extrapolate it to all players.
8. **Find the gap.** Look for: an audience segment with weak options, a loop that incumbents all monetise the same way, a frequent complaint you can design away, or a format shift (for example one-hand play). Use method D in `concept-lab`.
9. **Write positioning.** Statement: "For <audience> who <need>, <title> is a <category> that <benefit>. Unlike <nearest competitors>, it <differentiator>." Add the proof you will test (prototype question or metric).
10. **Risks and unknowns.** What would you need to measure (CPI test, store-page test, prototype) to resolve the biggest uncertainty? Propose the cheapest test.
11. **Write the file** `.gamestudio/research/market-<slug>.md` (template below) and log: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py progress "market scan <slug> done: <one-line verdict>"`.

## Sources by budget

| Budget | Sources | Notes |
|---|---|---|
| Free | App Store and Google Play pages (ratings, update dates, IAP lists, screenshots), store charts, public postmortems and developer blogs, public industry articles and reports, social and community discussion | Rate-limited by effort, not money; note the region of the charts |
| Standard | Free sources plus any trend tool or MCP configured in the session; public analytics summaries | Treat vendor estimates as estimates |
| Deep | Paid analytics the user provides (download and revenue estimates, retention panels, creative libraries) | Quote the vendor and period |

Reliability ranking: first-party (store pages, developer statements) over analytics-vendor estimates over press summaries over forum posts. A claim from a forum is a lead to verify, not a fact.

## Competitor matrix

| Field | Meaning |
|---|---|
| Title / developer | Official names |
| Launch / last update | From the store page |
| Core loop | One line in ontology terms: verb, reward, constraint |
| Meta | Collection, progression, social, events |
| Monetization | Ads, IAP types, pass, subscription (as visible in store and in play) |
| Audience signals | Age, skew, region (if evidence) |
| Scale signal | Rating count, chart rank, estimate with source and date |
| Praise / complaints | Top 3 each from review sample |
| Differentiator | What it does that others do not |
| Weakness | The opening for us |

## Positioning check

| Test | Pass |
|---|---|
| Different from the nearest three comparables in one sentence | You can say it without genre jargon |
| Verifiable in a screenshot or 5-second clip | Store creative can show it |
| Audience reachable | A named channel or community exists; cost not asserted without data |
| Defensible | Incumbents cannot copy it with one update |

## Volatile facts (as of Oct 2026 — verify)

Market sizes and shares change quickly; re-check before quoting.

- Hybrid-casual spending rose 17.1% in 2025 ($3.5B to $4.2B); H1 2026 mobile game IAP about $40B (down 2% year on year) with downloads about 24B (down 12%). Source: https://mobilegamer.biz/data-digest-sensor-towers-h1-analysis-hay-days-comeback-julys-top-games-big-krafton-numbers-and-more/
- Mobile game IAP in 2025 was about $82B (up 1%); strategy was the hot genre of 2025. Source: https://sensortower.com/press/press-release-sensor-tower-state-of-gaming-gaming-drove-52-billion-downloads-82b-iap-revenue-on-mobile-and-12b-premium-revenue-on-steam
- Ad-revenue share and ads-versus-IAP mix differ sharply by region (for example India ad-led, US IAP-led). Source: https://sensortower.com/blog/gaming-deep-dive-ad-monetization-report
- Retention medians vary by source; use as order-of-magnitude only. Source: https://blog.playio.co/d1-d7-d30-retention-benchmarks-2026

## Outputs

`.gamestudio/research/market-<slug>.md` with sections: Question, Method and budget, Sources, Competitor matrix, Review themes, Gap analysis, Positioning statement, Risks and cheapest test, Volatile facts. Slug is lowercase kebab-case from the genre or concept.

## Quality gates

- Every number has a source URL and period, or is marked an estimate with its source's name.
- At least 8 titles in the matrix, with at least 2 direct comparables and 2 recent launches when they exist.
- Review sample sizes stated; no generalisation beyond the sample.
- The conclusion states a verdict (lane open, narrow, or saturated), what would change it, and the cheapest next test.
- No invented revenue, download or CPI figures; unknowns are marked.

## Failure modes and recovery

| Failure | Recovery |
|---|---|
| Store pages blocked or login-gated | Use public articles and the user's screenshots; mark cells "?" |
| Only vendor hype available | Say so; lower confidence; propose a prototype or store-page test |
| Too many competitors | Cluster by loop and audience; pick representatives per cluster |
| Workflow agents return conflicting figures | Show both with sources; do not average |
| User wants a revenue forecast | Offer `retention_ltv.py` scenarios with explicit assumptions, labelled as such |
| Scan finds a saturated lane | Report it plainly and hand to `concept-lab` method B or D |

## Related skills

`new-game`, `concept-lab`, `market-intel`, `genre-playbooks`, `marketing-ua`, `design-review`.
