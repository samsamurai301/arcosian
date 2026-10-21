# KPI Dictionary for Mobile Games

The studio's canonical definitions for every player-behaviour and business metric used in contracts, dashboards, experiment readouts and soft-launch reviews. Each KPI has one formula, its unit, the denominator traps that make teams disagree, what it diagnoses, and the levers that move it. Definitions come first because most "the numbers disagree" arguments are definition mismatches (calendar-day vs 24-hour D1, gross vs net revenue, installs vs first opens). The file ends with a KPI driver tree, a fully worked example computed from one week of toy data, and a clearly labelled volatile section with sourced benchmark ranges. Stable formulas live in the body; anything market-dependent lives at the bottom.

## Contents

1. Measurement conventions (decide these before the first dashboard)
2. Audience and engagement: DAU, WAU, MAU, stickiness, sessions, playtime
3. Retention: classic, rolling, bracket; D1/D7/D30; ratios
4. Churn, reactivation and growth accounting
5. Monetization: revenue, ARPDAU, ARPU, ARPPU, payer conversion, ads
6. Lifetime value (LTV) and its variants
7. User acquisition: CPI, IPM, CPM, ROAS, payback, K-factor
8. Technical health KPIs that move business KPIs
9. The KPI driver tree
10. Worked example: one week, every KPI
11. KPI naming in the contract and taxonomy
12. Volatile facts (as of Oct 2026 — verify before relying)

---

## 1. Measurement conventions

Write these into the analytics section of the design contract (or a `metrics.md` next to the taxonomy) before launch. Changing them later breaks every time series.

| Convention | Options | Studio default | Why it matters |
|---|---|---|---|
| Install | store install (MMP), `first_open` (analytics SDK), account creation | `first_open` for product KPIs; MMP install for UA KPIs | Store installs that never open inflate denominators; reinstalls double-count |
| User identity | device/app-instance id, account id, MMP id | Pseudonymous player id generated on first open, migrated to account id on login | Device changes and reinstalls create phantom "new" users; cross-device players split |
| Day boundary | UTC, project time zone, player local time | UTC for all KPIs; local time only for time-of-day analyses | Local-time days make a cohort's "day 1" a different length for each player |
| Retention day N | calendar day N after install day; 24-hour window `[24N, 24N+24)` hours | Calendar day (matches most game dashboards); state it on every chart | The two definitions can differ by several points at D1; never compare across them |
| Active user | any session; any `user_engagement`; a meaningful event (e.g. `level_start`) | Any foreground session with ≥ 1 engagement event | Background pings and push-opened-then-closed sessions inflate DAU |
| Session | SDK session (timeout after inactivity), or app foreground span | SDK session with the default inactivity timeout; record `session_id` as a common param | Different timeouts change sessions/DAU by large factors |
| Revenue basis | gross (what the player paid) or net (after store fee, taxes, refunds; ad revenue after network share) | Report both; decisions on net | ROAS and payback on gross overstate return by the store cut |
| Ad revenue | impression-level revenue from mediation (ILRD), or network reports aggregated daily | ILRD per impression, reconciled weekly to network payouts | ILRD is an estimate; reconciliation catches drift |
| Refunds and chargebacks | ignore, subtract on refund date, subtract from purchase cohort | Subtract from the purchase's cohort | Refund abuse otherwise shows as healthy ARPPU |
| Test and internal users | include, flag, exclude | Exclude by allow-listed device ids and a `debug_build` common param | Developers and QA farms distort small soft-launch cohorts |
| Cohort maturity | include all cohorts, include only cohorts that have reached day N | Only mature cohorts for Dn | Including immature cohorts makes Dn look like it is falling |
| Currency | local, USD at daily rate, USD at fixed rate | USD at daily rate; store price tiers for SKU comparisons | Exchange swings look like monetization changes |

**Rule:** every KPI on a chart carries its definition tag, e.g. `D7 (classic, calendar, UTC, mature cohorts)`.

---

## 2. Audience and engagement

| KPI | Formula | Unit | Notes and traps |
|---|---|---|---|
| DAU | distinct active users on day *d* | users | Define "active" (section 1). Split DAU into new / returning / resurrected (section 4) |
| WAU | distinct active users in the trailing 7 days ending *d* | users | Trailing window, not calendar week, unless labelled |
| MAU | distinct active users in the trailing 30 (or 28) days ending *d* | users | 28 days removes weekday mix effects; state which |
| Stickiness | DAU / MAU (or DAU / WAU) | ratio | Average fraction of a month an active player plays. Not retention: a game with few loyal daily players can be sticky but tiny |
| Sessions per DAU | sessions / DAU | sessions | Session timeout drives this (section 1) |
| Session length | median and p75/p90 of session durations | seconds or minutes | Use the median; the mean is dragged by idle-open sessions. Exclude sessions < 2 s (accidental opens) and cap outliers |
| Playtime per DAU | total foreground engaged time / DAU | minutes | The best single engagement number; equals sessions/DAU × mean session length |
| Days active per month | active days per user in a 30-day window | days | Distribution matters more than the mean; bimodal = two audiences |
| Engaged DAU share | DAU with ≥ 1 core-loop event / DAU | ratio | Catches "opened, collected a reward, left" behaviour from push and daily-login rewards |

**Stickiness interpretation.** DAU/MAU of 0.20 means the average monthly player is active about 6 days a month. Daily-habit genres (puzzle, word, idle) aim higher than session-heavy mid-core titles played in bursts. Compare against your own history and genre peers, not a universal threshold.

**Session-length design check.** Compare the session-length distribution to `contract.meta.session_length_target_sec`. If the median session is half the target, the core loop ends before the designed payoff (or players are interrupted by an interstitial or energy wall); if it is double, sessions may be too long for mobile contexts and energy or natural stopping points are missing.

---

## 3. Retention

Retention is the fraction of an install cohort that comes back. It is the single most predictive product KPI: LTV, organic growth and payback all scale with it.

### 3.1 Three definitions

Let a cohort be all users whose install day is *c*, size *N*. Let `active(u, d)` mean user *u* was active on day *d*.

| Type | Formula for day *n* | Behaviour | Use it for |
|---|---|---|---|
| **Classic (N-day, exact day)** | users active on exactly day *c+n* / *N* | Noisy day-to-day; can go up and down between adjacent days | Industry comparisons (most game dashboards and benchmarks), contract `kpi_targets` |
| **Rolling (unbounded, "return on or after")** | users active on any day ≥ *c+n* / *N* | Monotone non-increasing; always ≥ classic; right-censored for young cohorts (it keeps rising as late returners show up) | Churn estimation ("still around after day n"), lifetime models with sparse play |
| **Bracket (range)** | users active at least once in days `[c+a, c+b]` / *N* | Smooths daily noise; choose brackets like D1, D2–3, D4–7, D8–14, D15–30 | Low-frequency games (weekly players), small soft-launch cohorts, weekly retention (W1 = days 7–13) |

**Never mix them.** A rolling D7 of 25% and a classic D7 of 12% can describe the same game. Every target in `contract.analytics.kpi_targets` means **classic, calendar-day, UTC** unless the contract says otherwise.

### 3.2 Standard retention points

| KPI | What it mostly measures | Primary levers |
|---|---|---|
| D1 | First-session quality: load time, FTUE clarity, time-to-fun, first win, a reason to return (a goal, timer or reward waiting tomorrow) | Load time, FTUE length, aha moment, first-session reward, notification permission timing |
| D3 | Whether the core loop survives repetition | Core-loop variety, early difficulty, first meta unlock |
| D7 | Core loop depth plus early meta: goals beyond the next level | Meta progression, collections, daily structure, social hooks, early difficulty walls |
| D14 / D30 | Meta and content runway; habit formation; social ties | Live events, long-term goals, guilds/friends, economy health, content cadence |
| D60–D180 | Long-term community; live-ops quality | Seasons, events, endgame, social |

### 3.3 Ratios that diagnose the curve shape

| Ratio | Formula | Reading |
|---|---|---|
| D7/D1 | D7 ÷ D1 | How much of the day-1 audience the core loop keeps through the first week. Practitioner heuristic: below about 0.30 suggests a first-session/FTUE problem (players returned once out of curiosity, then left); 0.30–0.44 suggests weak days 2–5 engagement (see volatile section for source) |
| D30/D7 | D30 ÷ D7 | Meta and content depth. A low ratio with a healthy D7 means players run out of goals or hit an economy/difficulty wall in weeks 2–4 |
| D1 drop | 1 − D1 | Size of the first-session problem; usually the biggest single loss in the funnel |
| Curve exponent | *b* in R(t) = a·t^(−b) | One-number summary of decay speed; smaller *b* = flatter tail (see `references/ltv-retention-modeling.md`) |

### 3.4 Statistical precision

A retention rate from *N* installs has a standard error of about √(p(1−p)/N).

| Installs in pool | D1 = 40% (95% CI half-width) | D30 = 5% (95% CI half-width) |
|---|---|---|
| 500 | ±4.3 pp | ±1.9 pp |
| 1,000 | ±3.0 pp | ±1.4 pp (±27% relative) |
| 2,500 | ±1.9 pp | ±0.9 pp |
| 10,000 | ±1.0 pp | ±0.4 pp |

To measure D1 within ±2 pp at 95% confidence you need about 1.96² × 0.4 × 0.6 / 0.02² ≈ 2,300 installs in the pool. Compute exact intervals with `python3 ${CLAUDE_PLUGIN_ROOT}/skills/player-analytics/scripts/analytics_calc.py ci --success 400 --n 1000` (Wilson interval: 37.0%–43.1%).

---

## 4. Churn, reactivation and growth accounting

### 4.1 Churn

Games have no cancellation event, so churn is an inactivity rule.

1. Pick the observation window: for each active user on day *d*, did they return within *k* days?
2. Plot P(return eventually | absent for *k* days) against *k* from historical data.
3. Choose *k* where that probability falls below a threshold (commonly 10–20%). Casual daily games often land at 7–14 days; weekly-burst mid-core games need longer.
4. Define: **churned on day d** = last active day was *d − k* or earlier and no activity since.

| KPI | Formula | Note |
|---|---|---|
| Churn rate (period) | users active in period *P* and not active in *P+1* / users active in *P* | Weekly or monthly; the complement of period-over-period retention |
| Cohort churn by day *n* | 1 − rolling retention at *n* | Rolling retention is the survival function |
| Hazard on day *n* | P(churn on day *n* \| survived to *n*) | Decreases with player age in almost every game: survivors are the committed |
| At-risk share | active users meeting a churn-risk score threshold / DAU | Needs a churn model (see `references/funnels-cohorts-segmentation.md` §9) |

### 4.2 Reactivation

| KPI | Formula |
|---|---|
| Reactivated users (day *d*) | users active on *d* who were churned (per the inactivity rule) before *d* |
| Reactivation rate | reactivated users in period / churned users at period start |
| Reactivation retention | classic retention of reactivated users measured from the reactivation day (treat them as a cohort) |
| Win-back cost | CRM or paid re-engagement spend / reactivated users |

Reactivated players usually retain worse than new players from good channels; measure their own curve before budgeting re-engagement campaigns, and always keep a holdout (see `references/experimentation.md` §11).

### 4.3 Growth accounting

Decompose DAU (or WAU/MAU) changes into flows, as popularised by growth-accounting work at Social Capital and by Duolingo's public description of its user-state model (2023):

```
DAU(d) = new(d) + retained(d) + resurrected(d)
DAU(d) − DAU(d−1) = new(d) + resurrected(d) − churned(d)
quick_ratio = (new + resurrected) / churned          # > 1 means growing
```

States per user per day: `new` (first active day), `current` (active today and recently), `at_risk` (recently active, not today), `dormant/churned` (absent ≥ k days), `resurrected` (active today after being churned). The transition rates between these states are often more actionable than DAU itself: a falling `current → current` rate is a product problem; a falling `new` count is a UA or store-featuring problem.

---

## 5. Monetization

### 5.1 Revenue and per-user averages

| KPI | Formula | Unit | Notes |
|---|---|---|---|
| Gross revenue | IAP gross (player-paid, before store fee) + ad revenue | USD | State whether taxes (VAT) are removed; stores report differently |
| Net revenue | IAP gross × (1 − store fee) − refunds + ad revenue (net of network share) | USD | Use for ROAS, payback, P&L |
| **ARPDAU** | revenue on day *d* / DAU on day *d* | USD per DAU | The daily monetization efficiency. Report IAP ARPDAU and ad ARPDAU separately; they move for different reasons |
| ARPU (period) | revenue in period / distinct active users in period | USD | e.g. monthly ARPMAU. Specify the period |
| **Cohort ARPU at day n** (cumulative ARPU) | cumulative revenue from a cohort through day *n* / cohort installs | USD per install | Realised LTV to date; the numerator of ROAS. Uses installs (including churned) as the denominator |
| **ARPPU** | revenue from payers / number of payers in the period | USD per payer | Daily ARPPU is noisy; weekly or monthly is more useful. Driven by price points, bundles, whales |
| **Payer conversion (daily)** | payers on day *d* / DAU | ratio | Daily conversion; small numbers (a few percent at most for most F2P games) |
| Payer conversion (cohort, by day n) | users in cohort who have paid at least once by day *n* / installs | ratio | The conversion that matters for LTV; compare D7 and D30 |
| Payer share of MAU | monthly payers / MAU | ratio | Monthly view used in many investor decks |
| Time to first purchase | days (or sessions) from install to first purchase; median among payers | days | Long times mean the first offer arrives after most players are gone |
| Repeat purchase rate | payers with ≥ 2 purchases / payers, within a window | ratio | Converts one-time starter-pack buyers into ongoing payers |
| Revenue concentration | share of revenue from top 1% / top 10% of payers | ratio | Heavy concentration = fragile revenue and an ethics review trigger (see `monetization`, `legal-ethics`) |

**Identity check:** ARPDAU = payer conversion (daily) × ARPPU (daily) + ad ARPDAU. Use it to localise a revenue change: did fewer people pay, did payers pay less, or did ads change?

### 5.2 Ads

| KPI | Formula | Notes |
|---|---|---|
| Impressions per DAU | ad impressions / DAU | Split by format (rewarded, interstitial, banner) |
| eCPM | ad revenue / impressions × 1,000 | Varies by geo, format, platform, season (Q4 high, January low) |
| **Ad ARPDAU** | impressions/DAU × eCPM / 1,000 | The ad identity: more impressions or better prices |
| Rewarded opt-in (engagement) rate | DAU who watched ≥ 1 rewarded ad / DAU | Measures how valuable the rewards are; a design metric as much as a monetization one |
| Rewarded views per engaged user | rewarded completions / users who watched ≥ 1 | Placement depth |
| Offer-to-watch rate (per placement) | `rv_started` / `rv_offer_shown` | Per-placement value of the reward |
| Completion rate | rewards granted / ads started | Low = technical problems or long unskippable creatives |
| Fill rate | ads filled / ad requests | Mediation health |
| Show rate | ads shown / ads filled (loaded) | Low = loading too late or ad shown after the moment passed |
| Interstitial frequency | interstitials per session, and minimum seconds between them | Must respect `contract.monetization.ads.interstitial` {`min_interval_sec`, `first_after_sec`} |

### 5.3 Subscription and pass KPIs (when used)

| KPI | Formula |
|---|---|
| Pass attach rate | players who bought the season pass / active players during the season |
| Pass completion rate | pass buyers who reached the final tier / pass buyers |
| Subscription renewal rate | renewals / subscriptions up for renewal |
| Subscription churn (monthly) | 1 − renewal rate |

---

## 6. Lifetime value (LTV)

LTV is the expected revenue a player generates over a horizon. In games always state the horizon (D90, D180, D365) and basis (gross or net).

| Variant | Definition | When to use | Weakness |
|---|---|---|---|
| Realised (cohort ARPU Dn) | cumulative revenue per install through day *n* for a cohort that has aged *n* days | The ground truth; ROAS Dn numerator | Only known after *n* days |
| Retention × ARPDAU | LTV(H) = ARPDAU × Σ_{t=0}^{H} R(t) (expected active days in the horizon) | Early projection from a retention curve; soft launch | Assumes ARPDAU is constant with player age; older players often monetize more (IAP) and see different ad loads |
| ARPU curve fit | fit cumulative ARPU(t) (e.g. power or log curve) and extrapolate to H | Once ≥ 30 days of revenue data | Extrapolation error grows with horizon |
| Multiplier | LTV(H) ≈ ARPU(D7) × m(H), with *m* measured on older cohorts (yours or a comparable title) | UA bidding on day-7 signals | Breaks when product or channel mix changes |
| Payer-based | LTV = cohort payer conversion × payer LTV + ad LTV | IAP-heavy games with few payers | Payer LTV is itself heavy-tailed |
| Predicted (pLTV) | ML model on day-0–3 behaviour | Value-based UA bidding at scale | Needs volume and careful leakage control |
| Subscription formula LTV = ARPU/churn | Constant churn assumption | Rarely right for games | Game churn hazard falls sharply with age |

**Expected lifetime days** L(H) = Σ_{t=0}^{H} R(t), with R(0) = 1. With the curve R(t) = 0.40 · t^(−0.473) (D1 40%, D30 8%), L(365) ≈ 17.5 days: the average install plays about 17.5 days in its first year. At ARPDAU $0.12, the year-one LTV ≈ $2.10 gross. Full methods are in `references/ltv-retention-modeling.md`.

---

## 7. User acquisition

| KPI | Formula | Notes |
|---|---|---|
| CPM (media) | spend / impressions × 1,000 | What the ad network charges for reach |
| CTR | clicks / impressions | Creative appeal |
| IPM | installs / impressions × 1,000 | Creative + store page conversion; the creative-testing KPI |
| **CPI** | spend / attributed paid installs | **CPI = CPM / IPM**: halve CPI by doubling IPM at the same CPM |
| Store conversion rate | installs / store page views | Store listing quality (see `store-release`, `marketing-ua`) |
| Blended (effective) CPI, eCPI | spend / (paid + organic installs) in the period | Shows the organic lift that paid UA creates |
| Organic multiplier ("k" in UA usage) | (organic installs attributable to paid activity) / paid installs | Hard to measure; estimate with geo holdouts or spend pulses |
| CPA / CPE | spend / users who completed an action (e.g. tutorial, level 10, first purchase) | Optimisation events for networks |
| **ROAS Dn** | cohort cumulative revenue through day *n* / spend on that cohort | Specify gross or net and *n* (D7, D30, D90). D7 ROAS is an early proxy; D90/D180 is closer to truth |
| Break-even ROAS | ROAS at which cumulative net revenue = spend (100% net) | A D7 target follows from multipliers: if D180/D7 revenue ≈ 3.0×, a 100% D180 net break-even needs about 33% net D7 ROAS |
| **Payback period** | first day *n* where cumulative net ARPU ≥ CPI | Studios typically set a maximum (e.g. 6 or 12 months) by cash position |
| Contribution margin | LTV(H, net) − CPI | Per-install profit at horizon *H* |
| **K-factor (viral coefficient)** | invites sent per user × conversion rate per invite | Total users per seeded user = 1 / (1 − k) for k < 1. A k of 0.1 adds 11% "free" users; true viral growth (k ≥ 1) is rare and short-lived |
| Viral cycle time | median time from install to invited friend's install | Lower cycle time compounds faster at the same *k* |

**ROAS vs payback trap.** A campaign with 20% D7 ROAS can be better than one with 30% if its later curve is steeper (higher-intent players). Compare whole ROAS curves on matured cohorts, not one early point.

---

## 8. Technical health KPIs that move business KPIs

| KPI | Formula | Why it is in the analytics review |
|---|---|---|
| Crash-free users | users without a crash / active users (daily) | Crashes in the first session are churn, invisible in design metrics |
| User-perceived crash rate, ANR rate (Android) | Play vitals definitions | Above Google's bad-behaviour thresholds, Play can reduce visibility (see volatile section) |
| First-open to first-playable time | p50/p90 of seconds from `first_open` to first interactive frame | One of the largest D1 levers; download-on-first-launch is a common killer |
| Load-time per screen | p90 of `load_time` events | Long loads end sessions |
| Error rate | `error` events per 1,000 sessions, by code | Rising errors after a release explain sudden KPI drops |
| Perf samples | p95 frame time, memory, thermal state from `perf_sample` (sampled) | Low-end devices churn faster when the game runs hot or slow (see `mobile-performance`) |

---

## 9. The KPI driver tree

Use this tree to localise any revenue or growth change before forming hypotheses.

```
Net revenue (period)
├── Active players (DAU)
│   ├── New players = paid installs (spend / CPI) + organic installs (store, featuring, virality k)
│   ├── Retained players = Σ over cohorts (cohort size × R(age))
│   └── Resurrected players = churned pool × reactivation rate
└── Net ARPDAU
    ├── IAP: daily payer conversion × ARPPU × (1 − store fee) − refunds
    │   ├── conversion: offer reach, first-offer timing, price ladder, perceived value
    │   └── ARPPU: price points, bundle value, repeat purchase, pass attach
    └── Ads: impressions/DAU × eCPM / 1000
        ├── impressions: rewarded opt-in × views/engaged user + interstitial frequency
        └── eCPM: geo mix, format mix, mediation/bidding setup, season

Unit economics per install
LTV(H) = net ARPDAU × L(H)        L(H) = Σ R(t), t = 0..H
Margin = LTV(H) − CPI            Payback day = min n: cumulative net ARPU(n) ≥ CPI
```

**Localisation procedure** (run it in this order when a top-line metric moves):

1. Is it real? Check event volumes, SDK versions, release dates, data delays and test-user leakage.
2. Is it mix? Split by platform, country tier, channel (organic vs paid), app version. A shift in the share of low-value geos changes ARPDAU without any product change (Simpson's paradox).
3. Is it audience or efficiency? DAU (new, retained, resurrected) vs ARPDAU.
4. Within ARPDAU: conversion, ARPPU, ad impressions, eCPM.
5. Within retention: which cohort ages moved (diagonal = calendar event; row = cohort quality; column = product change at a given age). See `references/funnels-cohorts-segmentation.md` §4.
6. Only now form hypotheses and pick qualitative follow-ups.

---

## 10. Worked example: one week, every KPI

A hybrid-casual puzzle game, day 2026-10-12 (UTC), soft launch in one country.

| Input | Value |
|---|---|
| DAU | 10,000 |
| MAU (trailing 30 d) | 52,000 |
| IAP gross revenue | $900 |
| Ad revenue (ILRD) | $380 |
| Payers that day | 180 |
| Ad impressions | 52,000 |
| Sessions | 34,000 |
| Engaged playtime | 238,000 minutes |
| UA spend that day | $6,000 for 2,400 paid installs |
| Invites per DAU | 0.30, invite conversion 15% |

Run: `python3 ${CLAUDE_PLUGIN_ROOT}/skills/player-analytics/scripts/analytics_calc.py kpis --dau 10000 --mau 52000 --iap-revenue 900 --ad-revenue 380 --payers 180 --impressions 52000 --sessions 34000 --playtime-min 238000 --spend 6000 --installs 2400 --invites-per-user 0.3 --invite-conversion 0.15`

| KPI | Result | Comment |
|---|---|---|
| Stickiness DAU/MAU | 0.192 | Monthly players are active about 5.8 days a month |
| ARPDAU | $0.128 | IAP $0.090 + ads $0.038 |
| Daily payer conversion | 1.8% | |
| ARPPU (IAP, daily) | $5.00 | Check the price ladder: is $4.99 the dominant SKU? |
| Impressions/DAU | 5.2 | |
| eCPM | $7.31 | |
| Sessions/DAU | 3.4 | |
| Mean session | 7.0 min | Compare with the median from raw sessions |
| Playtime/DAU | 23.8 min | |
| CPI | $2.50 | |
| K-factor | 0.045 | Viral multiplier 1.047: virality is not a growth lever here |

Cohort view, same game: classic retention D1 40%, D7 18%, D30 8% (mature cohorts, 6,000 installs). D7/D1 = 0.45, D30/D7 = 0.44. With ARPDAU $0.12 and CPI $2.50:

`analytics_calc.py payback --points "1:0.40,7:0.18,30:0.08" --arpdau 0.12 --cpi 2.50`

| Day | Lifetime days | Cum. gross ARPU | Gross ROAS |
|---|---|---|---|
| 7 | 2.71 | $0.33 | 13.0% |
| 30 | 5.22 | $0.63 | 25.1% |
| 90 | 8.96 | $1.08 | 43.0% |
| 180 | 12.72 | $1.53 | 61.1% |
| 365 | 18.29 | $2.19 | 87.8% |

No payback within a year even on gross revenue; break-even needs ARPDAU ≈ $0.137 gross at this retention, or CPI ≤ $2.19. **Decision:** do not scale UA. The cheapest lever is probably retention after day 7 (each +1 pp on the D30 point raises L(365) noticeably) or ARPDAU via rewarded-ad placements, and both need experiments before spend increases. The curve fitted here has *a* = 0.414, *b* = 0.470; constant ARPDAU is assumed, which usually understates IAP LTV for older players.

---

## 11. KPI naming in the contract and taxonomy

| Name in `kpis[]` / dashboards | Definition in this file |
|---|---|
| `d1`, `d7`, `d30` | Classic calendar-day retention (§3) — same keys as `contract.analytics.kpi_targets` |
| `session_len_sec`, `sessions_per_day` | Median session length; sessions per DAU (§2) |
| `arpdau_usd` | Gross ARPDAU in USD (§5) |
| `payer_conversion` | Cohort payer conversion by D30 unless labelled `payer_conversion_daily` (§5) |
| `ftue_funnel`, `level_funnel` | Funnels defined in `references/funnels-cohorts-segmentation.md` |
| `level_win_rate`, `attempts_p50`, `churn_by_level` | Level metrics (`references/funnels-cohorts-segmentation.md` §2) |
| `economy_balance` | Source/sink ratios and balances (`references/telemetry-for-design.md` §3) |
| `rv_opt_in_rate` | Rewarded opt-in rate (§5.2) |
| `event_participation` | Live-event participation (`references/telemetry-for-design.md` §5) |
| `perf_health` | Tech KPIs (§8) |
| `roas_d7`, `roas_d30`, `roas_d90`, `payback_days` | §7 |

Use these exact keys so event definitions (`event-taxonomy.schema.json` → `events[].kpis`) link to the same dashboard tiles.

---

## 12. Volatile facts (as of Oct 2026 — verify before relying)

Benchmarks below are directional. Most are secondary write-ups of vendor datasets with different definitions, geographies and genre mixes. Use them to sanity-check targets, never as acceptance criteria without your own genre comparables.

**Retention**
- GameAnalytics data across 16,000+ live mobile games, as relayed by secondary sources: median D1 about 22%, D7 just under 4%, D30 about 0.7–0.8%; the top 1% of games hold about 64–68% D1 and 13–15% D30. — [Segwise (citing GameAnalytics 2026)](https://segwise.ai/blog/mobile-gaming-app-user-retention-strategies); [Playio 2026 benchmarks](https://blog.playio.co/d1-d7-d30-retention-benchmarks-2026)
- Practitioner "viability screen" for marketed titles: about 25–30% D1, 10–15% D7, 3–6% D30; top tier 45%+ D1, 25%+ D7, 12%+ D30. Sources note the common 30–35/10–15/3–6 screen is a heuristic, not a published median. — [Playio](https://blog.playio.co/d1-d7-d30-retention-benchmarks-2026); [Galaxy4Games](https://galaxy4games.com/en/knowledgebase/blog/mobile-game-retention-benchmarks-2026-d1-d7-d30-data-for-publishers)
- Top-quartile D1 reported at about 31–33% on iOS vs 25–27% on Android; genre splits are inconsistent across sources and some trace back to 2022 data. — [Segwise](https://segwise.ai/blog/mobile-gaming-app-user-retention-strategies); [AppAgent](https://appagent.com/blog/mobile-game-retention-benchmarks/)
- D7/D1 diagnostic thresholds (below ~0.30 = first-session problem; 0.30–0.44 = weak days 2–5) are practitioner consensus attributed to Lancaric's 2025 "Soft Launch Bible" and a 2022 Traplight analysis, not hard rules. — [GameDev.net](https://gamedev.net/blogs/entry/2298160-the-d7d1-retention-ratio-for-mobile-games-a-complete-guide)
- "Time to fun": practitioners warn that if the aha moment takes more than about 90 seconds, a significant share of users never return. — [Playio (Aug 2026)](https://blog.playio.co/mobile-game-onboarding-retention)

**Engagement**
- Secondary summaries of GameAnalytics 2026 data (sponsored post; not confirmed against the primary report): top-quartile titles see about 22–24 minutes of daily playtime per user and the top 1% above 90 minutes; top-quartile session length is reported around 5 minutes. No reliable 2026 overall median session length was found. — [GameDev Reports summary of GameAnalytics 2026](https://gamedevreports.substack.com/p/gameanalytics-mobile-and-pc-game); [Game Growth Advisor KPI benchmarks](https://gamegrowthadvisor.com/blog/2026-03-17-mobile-game-kpis-benchmarks-2026/)

**Monetization and UA (low confidence: blog figures, inconsistent definitions)**
- ARPDAU: no verified 2026 primary median was found. One non-primary 2026 blog gives blended ranges of roughly $0.01–0.05 for ads-only casual, $0.03–0.08 hyper-casual and $0.15–0.50 hybrid-casual, and says it found no trusted source for mid-core/RPG. — [Game Growth Advisor](https://gamegrowthadvisor.com/blog/2026-03-17-mobile-game-kpis-benchmarks-2026/)
- CPI: one source citing The Game Marketer puts blended tier-1 game CPI at about $4.22 iOS and $2.97 Android; hyper-casual is cheapest (Android near $0.40, iOS $1.50–2.50 per FoxData); mid-core/strategy tier-1 ranges vary by source from about $4 to $18. — [Segwise CPI/IPM/ROAS benchmarks](https://segwise.ai/blog/cpi-ipm-roas-benchmarks-optimizing-ad-spend.md); [FoxData 2026 UA cost benchmarks](https://foxdata.com/en/blogs/2026-mobile-game-user-acquisition-cost-benchmarks-how-much-should-you-spend/); [Playio CPI benchmarks](https://blog.playio.co/mobile-game-cpi-benchmarks-2026)
- D7 ROAS: Liftoff data relayed by a blog puts global D7 ROAS around 7.6–7.8% for casual and about 4.3% for mid-core; no clean genre-by-platform 2026 table was found. — [The Social Outline (citing Liftoff)](https://thesocialoutline.com/blog/mobile-app-cpi-benchmarks-2026)
- Ad share of game revenue differs sharply by market (Sensor Tower, Jan–May 2026: ads about 70% of game revenue in India vs about 22% in the US); in mature markets IAP is 77–90% of revenue. Geo mix therefore moves ARPDAU composition. — [GameDev Reports summary of Sensor Tower](https://gamedevreports.substack.com/p/sensor-tower-mobile-game-ad-monetization)

**Store fees (affect net revenue and payback)**
- Apple EU terms effective Oct 1, 2026: App Store + Apple IAP 26% (15% for Small Business Program and subscriptions after year one); alternative payment processing 20% (10%); link-out 15% (10%). — [Apple Newsroom, Aug 2026](https://www.apple.com/newsroom/2026/08/apple-announces-changes-for-apps-in-the-european-union/)
- Outside the EU, standard store commissions of 30% with 15% reduced tiers (small-business programmes, subscriptions after year one) are long-standing but US rules changed repeatedly in 2025–26 after the Epic rulings; treat the store fee as a per-storefront config value and check `monetization` and `store-release` for current terms. — [Apple Small Business Program](https://developer.apple.com/app-store/small-business-program/) (background, not re-verified); [Neonpay tracker](https://www.neonpay.com/blog/google-plays-new-u.s.-billing-linking-policies-what-game-developers-need-to-know)

**Analytics platform conventions**
- GA4 / Firebase app collection limits (standard properties): 500 distinctly named events per app user (automatically collected events excluded), event names ≤ 40 characters, 25 parameters per event, parameter names ≤ 40 characters, parameter values ≤ 100 characters, 25 user properties, user-property names ≤ 24 characters and values ≤ 36 characters, user-ID ≤ 256 characters. — [Google Analytics Help: collection limits](https://support.google.com/analytics/answer/9267744)
- Firebase Analytics ends a session after 30 minutes of inactivity by default (configurable). Background knowledge, not re-verified this session. — [Firebase Analytics docs](https://firebase.google.com/docs/analytics)
- Android vitals "bad behaviour" thresholds have been 1.09% user-perceived crash rate and 0.47% user-perceived ANR rate overall (8% on any single device model). Background knowledge, not re-verified this session. — [Android vitals](https://developer.android.com/topic/performance/vitals)
