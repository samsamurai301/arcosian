---
name: marketing-ua
description: Mobile game marketing and user acquisition - CPI, ROAS and payback math, channels and bidding, attribution (SKAN, AdAttributionKit, GAID, MMPs), creative testing and playables, community, influencers, PR, pre-registration, launch timing, virality, and pre-production marketability tests. Use when asked about CPI targets, UA budgets, ad creatives, fake-door tests, launch plans or K-factor.
when_to_use: Planning how a mobile game finds players, before and after launch.
---

# Marketing and User Acquisition

## What this skill gives you
- The unit-economics core: CPI, ROAS, payback, LTV and how they gate whether paid UA is viable at all.
- Channel, bidding and attribution knowledge for iOS (ATT, SKAN, AdAttributionKit) and Android (GAID, consent).
- A creative testing system, including playables, and the ethics of ads that represent the game honestly.
- Community, influencer, PR, pre-registration and launch-timing practice, plus virality math.
- Cheap pre-production marketability tests (CPI tests, fake doors, landing pages) and how to read the numbers.

## Core models

### 1. Unit economics decide everything
`ROAS(d) = cumulative revenue per install by day d / CPI`. Paid UA is viable if projected ROAS crosses 100 percent within your payback window and the margin covers store fees and overhead. Compute LTV from retention and ARPDAU with `${CLAUDE_PLUGIN_ROOT}/scripts/retention_ltv.py`. If LTV cannot plausibly beat CPI, fix retention or monetization, change genre or audience, or choose organic and premium routes instead of buying installs.
| Term | Meaning |
|---|---|
| CPI | Cost per install (blended or paid-only; say which) |
| eCPI | Effective CPI including organic uplift; do not mix with paid CPI |
| CPA / CPP | Cost per action or payer |
| ROAS | Return on ad spend by cohort day |
| Payback | Days until ROAS reaches 100 percent |
| LTV | Lifetime value projected; always with an interval |
| IPM | Installs per thousand impressions, a creative quality signal |
| CVR, CTR | Conversion and click-through rates |

### 2. The funnel view
Impression -> click -> store page view -> install -> open -> tutorial -> D1 -> D7 -> payer. Each stage has a leak; fix the biggest leak in terms of cost. Creative drives the top; store page and first-session experience drive the middle; retention and monetization drive the bottom. Most UA problems are product problems seen too late.

### 3. Creative is the main lever
On modern auction-based networks targeting is largely algorithmic, so creative is the variable you control most. Systematic testing of many concepts beats polishing a few.

### 4. Measurement is probabilistic on iOS
With ATT and aggregated postbacks, you read trends and cohorts, not individual users. Plan decisions around modeled and aggregated data, MMP tooling, and incrementality tests.

### 5. Marketing starts in design
Marketability: is the hook visible in a 5 to 15 second video? Does the game have a "show-me" moment? Test before building (`references/marketability-testing.md`).

### 6. Honesty is a strategy
Ads that misrepresent gameplay generate cheap installs and poor retention, plus store and regulator risk. The right measure is cost per retained player, not cost per install.

## Decision procedures

### A. Should we buy UA at all?
1. Get D1/D7/D30 and ARPDAU from soft launch (`liveops`).
2. Project LTV with an interval; compare to expected CPI by geography and channel.
3. Compute payback; compare with cash constraints.
4. If margin is thin, run smaller tests to learn the real CPI and cohort quality, or improve the product first.
5. Record decision and thresholds in the plan; revisit weekly.

### B. Launch a paid UA test
1. Pick one or two channels; set a fixed test budget and geography.
2. Prepare creative set (several concepts, several variants each).
3. Configure the MMP, events and conversion value schema, consent flow.
4. Run until sample is meaningful; read IPM, CPI, D1/D7 by creative and channel.
5. Scale winners gradually; kill laggards; keep exploring new concepts.

### C. Plan a creative test cycle
1. Hypothesis per concept (what hook, what promise).
2. Produce quickly; video, playable, static, with honest representation.
3. Test with equal budget; stop rules by sample size.
4. Analyze by concept, then by element (hook, pacing, call to action).
5. Feed learnings to the next batch; archive.

### D. Plan the launch
Timeline: months out (community and pre-registration), weeks out (press kit, influencers, store assets), launch week (UA ramp, featuring requests, events), after (retention focus, content cadence). Details in `references/community-launch-virality.md`.

### E. Compute break-even CPI
`max_CPI = LTV(payback window) x target_margin_factor`. Example logic: if projected 30-day revenue per install is X and you need ROAS of 100 percent by day 30, CPI above X fails; with a margin target below 100 percent, subtract. Always present the interval.

### F. Weekly UA review (30 minutes)
1. Spend, installs, CPI by channel, country, creative.
2. Cohort ROAS curves vs the projection; flag cohorts off track.
3. Creative fatigue: IPM trend per concept; retire decaying creatives.
4. Quality: D1/D7 by source; fraud flags.
5. Decide: scale, hold, cut; log the reason and expected effect.
6. Feed product issues found in cohorts back to design and live-ops.

## Mobile specifics
- iOS: ATT prompt shapes data; use AdAttributionKit and SKAN via the MMP; conversion value schemas are a design problem (what early signals predict value).
- Android: GAID plus consent remains the measurement base; Privacy Sandbox on Android was retired, so no migration plan is needed on that front (see volatile facts in the UA file).
- Store pages (ASO) are part of the funnel: icon, screenshots, video, title, ratings; test with store experiments.
- Regional differences: CPI, ARPDAU and creative taste vary strongly by country; localize creatives and store pages.
- Device targeting: do not buy installs on devices that cannot run the game well; it wastes budget and hurts ratings.
- Fraud: install fraud and bots exist; use MMP fraud tools and watch cohort quality.

## Anti-patterns
| Anti-pattern | Detect | Fix |
|---|---|---|
| Buying installs before retention is proven | LTV below CPI | Soft launch, fix product |
| Misleading creatives (fake gameplay) | High CTR, low D1 | Honest creative; measure cost per retained player |
| One creative concept at a time | Slow learning, fatigue | Batch testing across concepts |
| Reading iOS data as exact | Overreacting to noise | Cohort aggregates, incrementality tests |
| Optimizing CPI instead of ROAS | Cheap installs, no revenue | Bid on value events where possible |
| Ignoring organic effects | Blended metrics unexplained | Track paid vs organic; test uplift |
| Influencer spend without tracking | Cannot tell what worked | Unique links, codes, cohort tags |
| Launch with no community | Silent store page | Build community and wishlist early |
| Gaming ratings or fake reviews | Policy violation | Never; ask happy players ethically |

## Using the ontology
Marketing hypotheses map to the player-motivation aesthetics in the ontology: the creative promises a fantasy and an aesthetic (`game-ontology`, `player-psychology`); the first-session loop must deliver it. Acquisition cohorts are keyed in telemetry by channel and creative. Use `retention_ltv.py` for LTV and payback, `ab_test.py` for test sizing, and `event_taxonomy.py` to define the install and early events sent to the MMP. Store metadata and ASO assets connect to `store_metadata.py` (see `store-release`). Record the UA plan in project state with `gs.py`.

## Reference library
| File | Contains | Read when |
|---|---|---|
| `references/ua-and-creatives.md` | CPI, ROAS, channels, bidding, attribution (SKAN, AdAttributionKit, GAID), creative testing, playables, ad ethics | Planning or running paid UA |
| `references/community-launch-virality.md` | Community, influencers, PR, pre-registration, launch timing, K-factor, referrals, UGC | Planning launch and organic growth |
| `references/marketability-testing.md` | Pre-production CPI tests, fake doors, landing pages, reading the numbers | Validating a concept before building |

## Related skills
- `monetization`: LTV side of the equation and ethical limits.
- `liveops`: soft launch, retention gates, events that support UA.
- `player-analytics`: cohorts, LTV and test statistics.
- `market-intel`: market sizing, competitor and trend research.
- `store-release`: store page assets, ASO, release logistics.
- `legal-ethics`: advertising law, privacy, child audiences.
- `genre-playbooks`: genre benchmarks for CPI and retention targets.
- `market-scan`: process skill for competitive research.
