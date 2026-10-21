# UA and Creatives

This file covers the mechanics of paid user acquisition for mobile games: the metrics (CPI, ROAS, payback, LTV), channel types, bidding strategies, attribution on iOS (ATT, SKAdNetwork, AdAttributionKit) and Android (GAID, consent), creative testing methods, playable ads, and the ethics of ad representation. Read it when you plan a UA budget, set up measurement, run creative tests, or review whether ads are honest. Volatile attribution facts are gathered at the end with sources.

## Table of contents
1. Metrics and formulas
2. Break-even and payback worked example
3. Channel landscape
4. Bidding and optimization
5. Budget allocation and scaling
6. Attribution fundamentals
7. iOS: ATT, SKAN and AdAttributionKit
8. Android: GAID, consent
9. MMPs and event design
10. Incrementality and organic uplift
11. Creative strategy
12. Creative testing procedure
13. Playable ads
14. Store page as a funnel step
15. Fraud and quality
16. Ad ethics and misleading-ad risk
17. Weekly metrics checklist
18. Volatile facts (as of Oct 2026 - verify)

## 1. Metrics and formulas
- `CPI = spend / installs` (state paid-only or blended).
- `ARPDAU = revenue / DAU` (split IAP and ads).
- `Retention(d)` = share of cohort active on day d.
- `LTV(T) = ARPDAU x sum_{d=0..T} Retention(d)` (simple form, assumes constant ARPDAU; refine with monetization curves).
- `ROAS(d) = cumulative revenue per install by day d / CPI`.
- `Payback day = first d where ROAS(d) >= 1`.
- `IPM = installs / impressions x 1000`; `CTR = clicks / impressions`; `CVR = installs / clicks`.
- `Cost per retained player (D7) = CPI / D7 retention`. Use it to compare sources with different quality.
- Margin: net revenue after store fees, taxes and refunds; compare ROAS on net revenue.
Use `${CLAUDE_PLUGIN_ROOT}/scripts/retention_ltv.py` to fit a power or exponential retention curve and project LTV. It returns point estimates plus a fit-quality score (`r2_log`), not confidence intervals: bracket decisions with low/base/high scenarios (for example ARPDAU ±25% and the fitted curve versus a steeper one).

## 2. Break-even and payback worked example
Suppose a cohort shows retention at several days and ARPDAU (all numbers hypothetical, for the arithmetic only):
| Day | Retention | Cumulative sessions-days |
|---|---|---|
| 0 | 100% | 1.00 |
| 1 | 40% | 1.40 |
| 3 | 25% | about 1.40 + 2 x (0.40+0.25)/2 = 2.05 |
| 7 | 15% | continue integrating |
Procedure: integrate retention over days to get expected active days in the window; multiply by ARPDAU; compare to CPI. If projected 90-day LTV exceeds CPI by a margin that covers uncertainty and your payback tolerance, scale; if only the optimistic scenario breaks even, do not scale.
Decision table:
| Projected LTV vs CPI | Action |
|---|---|
| Well above CPI at payback target | Scale spend step by step |
| Near CPI | Improve creative CPI, retention, or monetization; small budgets |
| Below CPI | Stop paid UA; fix product or segment geography |
Sensitivity: compute LTV at pessimistic, base and optimistic retention curves; if only optimistic wins, you are gambling.

## 3. Channel landscape
| Channel type | Strengths | Limits |
|---|---|---|
| Ad networks with self-serve (large gaming-focused networks) | Scale, performance optimization, rewarded and playable inventory | Creative dependency, opaque auctions |
| Social platforms | Broad reach, strong creative formats | Cost, creative fatigue, privacy limits |
| Search and app campaigns from the store owners | High intent, store-integrated | Cost variability, limited control |
| Video platforms | Reach, storytelling | Weaker direct response |
| Influencers and creators | Authenticity, niche audiences | Hard to measure, variability |
| Cross-promotion | Cheap, quality players | Needs your own portfolio |
| Offerwalls and incentivized | Cheap volume | Low quality; retention and policy risk |
| Organic (ASO, community, PR) | Sustainable | Slow, needs product pull |
Choose channels by game type: hyper-casual leans on high-volume networks; mid-core leans on social and video plus influencers; narrative or niche leans on community, creators and PR.
Do not name budgets or CPIs by channel from memory; use current benchmarks and your own tests.

## 4. Bidding and optimization
- Bid objectives: installs (cost per install), actions (cost per in-app event), value (return on ad spend, value optimization). Value optimization needs enough purchase events per period for the model to learn.
- Start with install optimization to learn creative performance, then optimize on a proxy event (tutorial complete, level reached) once install volume is stable, then on purchase or value when volume allows.
- Set target CPI or ROAS conservatively; networks may ramp spend aggressively and chase cheap, low-quality traffic if the target is loose.
- Respect learning phases: avoid frequent edits; changes reset learning on many platforms.
- Daily budget pacing: ramp in steps; observe cohort quality for several days before further increases.
- Geo bids: separate campaigns by country tier since economics differ.
- Retargeting and re-engagement: for lapsed players, use deep links to relevant content and cap frequency; check that re-engagement is incremental.
- Bid on the quality signal that predicts revenue: define early events that correlate with later spend (validated in soft launch).

## 5. Budget allocation and scaling
Procedure:
1. Start with a test budget that buys enough installs per creative to read IPM and D1; set rules for stopping.
2. Allocate by cohort ROAS projection, not by CPI.
3. Scale in increments (for example, raising budgets in moderate steps) and watch for CPI inflation and quality drift.
4. Diversify channels when one saturates.
5. Reserve budget for creative exploration, since performance decays as creatives fatigue.
6. Reallocate weekly using the review in the SKILL.
Cash view: payback window times spend equals working capital at risk; confirm you can fund it.
Saturation: as spend grows in a geography, marginal CPI rises; compute marginal ROAS instead of average ROAS for the next dollar.

## 6. Attribution fundamentals
- Attribution links an install to the ad that caused it: click-through (identifier or probabilistic matching) and view-through windows; networks self-report, MMPs reconcile.
- Mobile measurement partners (MMPs): AppsFlyer, Adjust, Singular, Branch, Tenjin, Airbridge and others; all major ones support AdAttributionKit. Pick on price, fraud tools, cost aggregation, SKAN/AAK tooling, and integrations.
- Core setup: SDK integration, event mapping, revenue events (IAP and ad revenue), deep links, cost data import from networks, postback configuration.
- Keep a single event taxonomy (see `event_taxonomy.py`); send only the events needed for optimization and analytics, and keep personal data out.
- Reconcile numbers: MMP vs network vs store install counts will not match; set tolerance and rules, and use the MMP or your own warehouse as the arbiter of truth.

## 7. iOS: ATT, SKAN and AdAttributionKit
- ATT: the app must request permission before accessing the IDFA or tracking across apps. Opt-in rates are reported with conflicting values by source; plan for a minority-to-half opt-in range and do not assume a number.
- SKAdNetwork (SKAN): Apple's privacy-preserving install attribution with delayed, limited postbacks (conversion values, crowd anonymity tiers, multiple postback windows in later versions).
- AdAttributionKit (AAK): Apple's successor framework, keeping SKAN 4's multi-window postbacks and crowd-anonymity tiers, adding configurable attribution windows and re-engagement support. There was no SKAN 5. Sources differ on exact launch framing; verify with Apple documentation.
- Conversion value schema design: with limited bits, choose which early signals encode predicted value (for example, revenue buckets and key engagement milestones). Procedure:
  1. List early events correlated with later revenue (from soft-launch data).
  2. Group into buckets (revenue bands or engagement tiers).
  3. Configure in the MMP; verify in test.
  4. Review quarterly; schemas decay as the game changes.
- Reading SKAN/AAK data: delayed and thresholded; low-volume campaigns return null or coarse data; consolidate campaigns to reach volume; use modeled results from the MMP for planning but validate with incrementality tests.
- Do not attempt fingerprinting; Apple prohibits it.

## 8. Android: GAID, consent
- The Google Advertising ID (GAID) supports device-level attribution when the user has not opted out; consent regimes (GDPR, state laws) govern ad personalization and measurement use.
- Privacy Sandbox on Android was retired in Oct 2025 (see volatile facts), so GAID-based measurement continues for now; policy could change, so keep your stack flexible.
- Install referrer APIs provide reliable click attribution for Play installs; ensure the MMP uses them.
- Integrate UMP consent and pass the state to the MMP and ad SDKs.
- Child-directed apps follow families policy (no advertising ID collection for kids); see `monetization` families section.

## 9. MMPs and event design
Minimum event set for a game:
| Event | Purpose |
|---|---|
| install, open | Baseline |
| tutorial_complete | Early quality signal |
| level_reached (milestones) | Engagement proxy |
| d1/d3/d7 return (derived) | Retention by source |
| purchase (with revenue) | Value optimization |
| ad_revenue (impression level where available) | Hybrid ROAS |
| subscription_start, renewal | Subscription LTV |
Rules: send revenue net or gross consistently; dedupe; map currency; include creative and campaign parameters; validate in the MMP's test console before spending.
Cost data: import spend by campaign, adset and creative so ROAS is computed per creative.
Raw data export: keep access to raw data in your warehouse for your own cohort models.

## 10. Incrementality and organic uplift
- Paid campaigns often lift organic installs (halo); attribution models ignore it unless you measure it.
- Incrementality tests: geo holdouts (pause spend in matched regions), platform lift studies offered by networks, ghost bids. Compare total installs and revenue in test vs control.
- Interpretation: a channel with poor last-touch ROAS but strong incremental lift may be worth keeping; a channel with strong attributed ROAS but low incrementality (capturing installs that would have happened) is not.
- Run tests rarely but deliberately (for example, quarterly) on your largest channels.
- Sample size and duration: use `ab_test.py` for proportions; expect large samples for rare events.

## 11. Creative strategy
Structure the creative program as concepts and variants:
- Concept: the core promise or hook (for example, "satisfying puzzle solve", "base-building fantasy", "extreme difficulty fail", "transformation").
- Variant: execution differences (opening shot, pacing, text, music, call to action, aspect ratio).
Principles:
- Hook within the first seconds; show the gameplay or the "oh" moment early.
- One idea per ad; a clear next step.
- Show real gameplay or faithful depictions; stylized or cinematic assets are fine if they represent actual experiences.
- Sound off by default on many placements; use captions and visual clarity.
- Localize text and cultural references; test per region.
- Refresh cadence: expect creative fatigue; keep a pipeline producing new concepts regularly.
- Reuse in-game capture and short recorded gameplay with edits; AI-generated assets can speed production, but disclose and keep honest (see `ai-asset-pipeline` for provenance and rights).
- Produce multiple aspect ratios and durations for each placement.

## 12. Creative testing procedure
1. Backlog of concepts ranked by hypothesis and effort.
2. Produce a batch (for example, several concepts with several variants).
3. Launch with equal budgets in a stable campaign structure (one creative per adset or use the network's creative testing tool).
4. Read primary metrics in order: IPM (or CTR and CVR) for the top funnel, then CPI, then D1/D7 and ROAS for quality.
5. Statistical discipline: set stop rules (impressions or installs per creative before judging); avoid early winner calls; expect noise; beware of repeating false positives from many variants (multiple comparisons).
6. Analyze elements: hook, first five seconds, length, call to action, music; use tagging so patterns emerge across ads.
7. Winners: scale and iterate on the winning concept with variants; losers: archive notes.
8. Track fatigue: IPM decline over time per creative; rotate.
9. Quality check: a creative that produces cheap installs but poor D1 is a loser, whatever the CPI.
Template for a creative log:
```
id, concept, hook, length, format, variant_notes, spend, impressions, installs, IPM, CPI, D1, D7, ROAS_d7, decision
```

## 13. Playable ads
- A playable ad is an interactive mini-demo of the game inside the ad unit; players try before installing.
- Strengths: self-selection reduces unqualified installs; strong for hyper-casual and puzzle; can raise retention of installers.
- Design: one core mechanic, short (tens of seconds), clear instructions, a tutorial-free first interaction, an end card with a call to action.
- Honest: the playable must reflect the real game's core experience; bait-and-switch hurts retention and violates network policies.
- Build: lightweight HTML5 with strict size limits set by networks; verify each network's technical spec before building; test on low-end devices.
- Metrics: engagement rate, completion rate, IPM, CPI, and D1/D7 of installers.
- A playable is also a prototype test of the hook; use in marketability tests (see `references/marketability-testing.md`).
- Maintain a template to produce playables quickly from game assets.

## 14. Store page as a funnel step
- Store page conversion (page view to install) multiplies all spend; improve it with icon, screenshots, video and short description tests using store experimentation tools.
- Match store assets to the ad promise; a mismatch lowers conversion and retention.
- Ratings and reviews affect conversion; ask for ratings at positive moments with platform APIs, never gate rewards on ratings.
- Localize listing in main markets.
- Coordinate with `store-release` for metadata and `store_metadata.py` for checks.

## 15. Fraud and quality
- Types: click injection, click spamming, install farms, bots, spoofing.
- Controls: MMP fraud suppression, anomaly rules (very short time-to-install, abnormal retention or zero engagement), publisher blacklists, validation of purchase events through server-side receipts.
- Compare cohort quality by source; sources with high installs and near-zero D1 are suspect.
- Contractual: network terms on fraud refunds; document anomalies promptly.
- Incentivized traffic: label it separately and evaluate on retention and revenue only.

## 16. Ad ethics and misleading-ad risk
Rules of the studio:
1. Depict what the player will actually do within the first session; stylized "fake" gameplay used as a hook is a mismatch risk.
2. No false claims about features, rewards, odds, endorsements or reviews.
3. Do not fake interactivity (fake "close" buttons, fake notifications) to induce clicks.
4. No targeting of minors with ads for content not appropriate for them; follow ad network and store policies for child audiences.
5. Disclose influencer sponsorship according to local advertising rules.
6. Comply with platform ad policies; misleading ads risk account suspension and, in many jurisdictions, regulatory action against deceptive advertising.
7. Avoid exploiting emotional vulnerabilities (loneliness, loss) with manipulative creative.
8. Measure honesty: track the gap between ad promise and first-session experience via D1 and survey.
Practical test: show the ad, then the first two minutes of gameplay to a fresh viewer; ask what they expected. If the answer differs materially, fix the ad.
Review with `compliance-officer` for regulated areas.

## 17. Weekly metrics checklist
- Spend vs plan, installs, CPI by channel and country.
- IPM and CTR trends by creative; fatigue flags.
- Cohort D1/D7 vs prior cohorts and projection.
- Cohort ROAS curves; compare to payback target.
- SKAN/AAK coverage and null rates; MMP vs network reconciliation drift.
- Fraud flags; blocked sources.
- Organic share and any halo signals.
- Decisions and next experiments.

## 18. Volatile facts (as of Oct 2026 - verify)
- AdAttributionKit is Apple's successor to SKAN; no SKAN 5; AAK keeps SKAN 4's three postback windows and crowd-anonymity tiers and adds configurable attribution windows and re-engagement. Sources disagree on launch framing; a vendor claim that SKAN endpoints are deprecated by late 2026 is unverified. Sources: https://www.moburst.com/mobile-attribution-in-2026-what-marketers-actually-need-to-know/ and https://mwm.ai/glossary/skadnetwork
- Google retired Privacy Sandbox technologies including Attribution Reporting, Protected Audience, Topics and SDK Runtime on Android (announced Oct 2025); GAID-based measurement continues for now. Sources: https://betanews.com/2025/10/20/google-is-retiring-privacy-sandbox/ and https://www.freevacy.com/news/engadget/google-officially-retires-its-privacy-sandbox-initiative/6843
- ATT opt-in rates reported at about 50 percent (one source) and about 35 percent (another): https://www.moburst.com/blog/idfa-att-update/
- All major MMPs support AdAttributionKit; AppsFlyer reported as largest by share: https://adapty.io/blog/which-services-your-app-needs
- Adjust has an official MCP; AppsFlyer has community MCPs over its Pull API: https://www.adjust.com/blog/adjust-mcp/ and https://glama.ai/mcp/servers/@ysntony/appsflyer-mcp
- Android developer verification affects off-Play distribution in some countries from Sep 30, 2026: https://www.androidauthority.com/p-3679204/
