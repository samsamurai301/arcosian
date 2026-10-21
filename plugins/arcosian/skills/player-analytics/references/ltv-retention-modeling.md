# Retention Curves, LTV and ROAS Modelling

How to turn a handful of early retention and revenue points into decisions about scaling user acquisition, setting soft-launch gates and judging whether a game can pay back its players. Covers the retention curve families that fit games (power, exponential, Weibull, shifted-beta-geometric), how to fit and validate them, why the horizon and the tail dominate LTV, lifetime-days and LTV from ARPDAU (constant and age-varying), cohort LTV projection by curve fitting, multipliers and payer models, ROAS curves and payback, and how to read soft-launch numbers without fooling yourself. Every method has a worked example with numbers computed by the tools: the plugin's `retention_ltv.py` (fit and LTV) and this skill's `analytics_calc.py payback` (ROAS curve and payback day).

## Contents

1. What we are modelling and why
2. Curve families
3. Fitting procedure and validation
4. The tail problem: horizons, extrapolation and hybrid tails
5. Lifetime days and LTV from ARPDAU
6. Cohort LTV projection methods
7. ROAS curves, break-even and payback
8. Reading soft-launch numbers
9. Common modelling mistakes
10. Tool usage
11. Volatile facts (as of Oct 2026 — verify before relying)

---

## 1. What we are modelling and why

| Quantity | Definition | Decision it supports |
|---|---|---|
| Retention curve R(t) | Classic retention: share of a cohort active on day *t* (R(0) = 1) | Product health, D1/D7/D30 targets, kill criteria |
| Survival curve S(t) | Share of a cohort not yet churned at *t* (from rolling retention or an inactivity rule) | Churn modelling, hazard analysis |
| Lifetime days L(H) | Σ_{t=0}^{H} R(t): expected active days per install within horizon *H* | Bridge from retention to LTV |
| LTV(H) | Expected revenue per install within *H* | Maximum affordable CPI, payback |
| ROAS(t) | Cumulative revenue per install by *t* / CPI | UA bidding and scaling |

Classic retention is not survival: players skip days, so R(t) < S(t). Use R(t) for active-day and ARPDAU-based LTV, S(t) for churn and hazard questions. Never fit a survival model to classic retention points and call it churn.

---

## 2. Curve families

| Model | Formula | Hazard behaviour | Fits | Linearisation for fitting |
|---|---|---|---|---|
| **Power** | R(t) = a · t^(−b), *t* ≥ 1 | Decreasing (≈ b/t): survivors are increasingly committed | Most F2P games over days 1–90; the studio default | ln R = ln a − b ln t |
| **Exponential** | R(t) = a · e^(−λt) | Constant | Very short windows, hyper-casual first days, or the far tail after a plateau | ln R = ln a − λt |
| **Weibull survival** | S(t) = exp(−(t/λ)^k) | k < 1 decreasing, k = 1 constant, k > 1 increasing | Survival/rolling retention; churn analysis | ln(−ln S) = k ln t − k ln λ |
| **Shifted-beta-geometric (sBG)** | Each player churns with a constant per-period probability θ; θ varies across players as Beta(α, β) | Decreasing at cohort level purely from heterogeneity | Discrete periods (weeks, months, subscriptions); explains *why* churn falls with age (Fader and Hardie, *How to Project Customer Retention*, Journal of Interactive Marketing, 2007) | Maximum likelihood on period counts |
| Power with plateau | R(t) = c + (a − c) · t^(−b) | Decreasing to a floor | Games with a durable core community | Nonlinear least squares |
| Piecewise / empirical | Observed points with interpolation, model only beyond data | — | When enough mature data exists | — |

**Why power fits games.** Mixed populations of "samplers" (who churn fast) and "committed players" (who churn slowly) produce a cohort-level hazard that falls over time even when each individual's risk is roughly constant — the same heterogeneity argument behind sBG. A single exponential cannot represent that mix and badly underestimates the tail.

---

## 3. Fitting procedure and validation

1. **Data.** Pooled classic retention for mature cohorts only, weighted by installs, from one platform and a consistent acquisition mix (separate iOS/Android and organic/paid if they differ). Include D1, D3, D7, D14, D30 and later points when available. Exclude D0 (it is 1 by definition).
2. **Fit in log space** (weighted least squares; weights = cohort sizes or inverse variances). The plugin's `retention_ltv.py` is unweighted: it fits the points you pass by ordinary least squares in log-log space (power) or semi-log space (exp), so pool and weight the cohorts first (`analytics_calc.py cohort` prints the weighted points). For two points only, the power model is exact: b = ln(R₁/R₂) / ln(t₂/t₁), a = R₁ · t₁^b.
3. **Holdout check.** Fit on early points (D1–D14), predict a later observed point (D30); report the error. A model that cannot predict D30 from D1–D14 has no business predicting D365.
4. **Compare models** on the holdout error and on plausibility of the tail, not on in-sample R².
5. **Uncertainty.** Bootstrap over cohorts (resample cohort rows, refit) to get an interval for L(H) and LTV; report the interval with every projection.
6. **Refit weekly** in soft launch; plot how projections change as data matures.

### Worked example

Observed (pooled, 8,000 installs): D1 42%, D3 27%, D7 18%, D14 13%, D30 8%.

| Day | Observed | Power fit (a = 0.442, b = 0.482) | Exponential fit (a = 0.323, λ = 0.051; the script prints λ as `b`) |
|---|---|---|---|
| 1 | 42.0% | 44.2% | 30.7% |
| 3 | 27.0% | 26.1% | 27.7% |
| 7 | 18.0% | 17.3% | 22.6% |
| 14 | 13.0% | 12.4% | 15.8% |
| 30 | 8.0% | 8.6% | 7.0% |
| 60 (projected) | — | 6.2% | 1.5% |
| 90 (projected) | — | 5.1% | 0.3% |

| Lifetime days | Power | Exponential |
|---|---|---|
| L(30) | 5.4 | 5.8 |
| L(90) | 9.2 | 7.1 |
| L(180) | 13.0 | 7.2 |
| L(365) | 18.5 | 7.2 |

Holdout (fit D1–D14, predict D30 = 8.0%): power predicts 9.4%, exponential 3.1%. The exponential model's constant hazard kills the tail and would cut projected year-one LTV by more than half; the power model slightly overestimates. **Use the power model, and treat its tail as optimistic** (section 4).

Commands:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/retention_ltv.py fit --points "1:0.42,3:0.27,7:0.18,14:0.13,30:0.08" --model power --json
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/retention_ltv.py fit --points "1:0.42,3:0.27,7:0.18,14:0.13,30:0.08" --model exp --json
```

### Weibull on survival data

Rolling-retention (survival) points S(1) = 62%, S(7) = 38%, S(14) = 31%, S(30) = 22% fit a Weibull with k ≈ 0.34 and λ ≈ 8.5 days (fitted 61.6%, 39.2%, 30.6%, 21.6%). k well below 1 confirms a strongly decreasing hazard. Projected survival: S(90) ≈ 11%, S(365) ≈ 3%. Use this for churn questions ("what share of D30 survivors will still be around at D90?" ≈ 11/22 = 50%), not for active-day LTV.

---

## 4. The tail problem: horizons, extrapolation and hybrid tails

For the power model with b < 1, Σ t^(−b) grows without bound as H increases (roughly like H^(1−b)), so **lifetime and LTV depend heavily on the chosen horizon and on extrapolation far beyond the data**. In the example above, L(365) = 18.5 but L(730) = 26.4: the second year adds about 42% to "lifetime" purely from extrapolation.

Rules:

1. **Always state the horizon** (LTV-D180, LTV-D365). Finance and UA should agree on one; D180 or D365 is common for casual games, longer only with live-ops evidence.
2. **Do not extrapolate more than ~3–6× beyond the last observed day** without a tail correction. With D30 data, projections beyond D180 are speculation.
3. **Hybrid tail.** Use the power curve until a cut-over day T (e.g. 90 or the last observed day × 3), then an exponential tail whose hazard matches the power curve's local hazard at T (λ = b/T). For the example: λ = 0.482/90 ≈ 0.0054 per day and L(365) falls from 18.5 to 16.5 days (−11%).
4. **Live-ops and content runway** change the tail: a game that runs out of content at day 60 will fall below any fitted curve; one with strong seasons may sit above it. Cross-check with the content runway from `references/funnels-cohorts-segmentation.md` §3.
5. **Sensitivity is in the tail.** Anchoring D1 = 40% and varying D30:

| D30 | Exponent b | L(180) | L(365) |
|---|---|---|---|
| 6% | 0.558 | 9.3 | 12.6 |
| 7% | 0.512 | 10.7 | 15.0 |
| 8% | 0.473 | 12.2 | 17.5 |
| 9% | 0.439 | 13.7 | 20.1 |
| 10% | 0.408 | 15.2 | 22.8 |

Each D30 point is worth roughly 2.5 lifetime days in year one (about +15%). By contrast, raising D1 from 40% to 45% while D30 stays at 8% does not raise L(365) at all in this model (it steepens the decay). D1 improvements pay off only when they carry through to later days — which is why D7 and D30 belong in kill criteria alongside D1.

---

## 5. Lifetime days and LTV from ARPDAU

### 5.1 Constant ARPDAU

```
LTV(H) = ARPDAU × L(H),   L(H) = 1 + Σ_{t=1}^{H} R(t)
```

Example: L(365) = 18.5 (power fit above), gross ARPDAU $0.12 → LTV-D365 ≈ $2.22 gross. If 70% of revenue is IAP and the store keeps 30% of it, net share ≈ 1 − 0.7 × 0.3 = 0.79 (compute your own mix and fee), so net LTV ≈ $1.75.

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/retention_ltv.py ltv --points "1:0.42,3:0.27,7:0.18,14:0.13,30:0.08" --arpdau 0.12 --horizon 365 --json
```

### 5.2 Age-varying ARPDAU (more realistic for IAP)

New players rarely pay on day 0; payers accumulate and older players carry more purchasing intent, while ad ARPDAU may be flatter. Measure ARPDAU by player age (days since install) from mature cohorts and use:

```
LTV(H) = Σ_{t=0}^{H} R(t) × ARPDAU(t)
```

Example: ARPDAU rises linearly from $0.08 on day 0 to $0.15 by day 30, then stays flat. With the power curve above, LTV-D365 ≈ $2.53, versus $1.48 if you had used the day-0–7 ARPDAU of $0.08 for all ages, and $2.22 at a blended $0.12. Using early ARPDAU as a constant **understates** IAP-heavy LTV; using the blended DAU-weighted ARPDAU of a mature game for a new cohort may **overstate** it if the mature DAU is dominated by long-term payers.

### 5.3 Decomposed LTV

```
LTV(H) = IAP_LTV + Ad_LTV
IAP_LTV = cohort payer conversion by H × average payer LTV
Ad_LTV  = Σ R(t) × impressions per DAU(t) × eCPM(t) / 1000
```

Decomposition tells you which lever to pull and makes geo comparisons honest (eCPM and IAP propensity vary by country very differently).

---

## 6. Cohort LTV projection methods

| Method | Inputs | Strength | Weakness |
|---|---|---|---|
| Retention × ARPDAU (section 5) | Retention points, ARPDAU by age | Works from day 7–14; transparent | ARPDAU assumptions; tail extrapolation |
| Cumulative ARPU curve fit | Cumulative revenue per install by day for mature cohorts | Fits the money directly | Needs ≥ 30 days; payer noise in small cohorts |
| Multipliers | Ratios ARPU(H)/ARPU(D7) from older cohorts or comparable titles | Simple; standard in UA teams | Breaks when the product, monetization or channel mix changes |
| Payer model | Conversion curve, payer ARPPU curve, payer retention | Good for IAP-heavy games | Many parameters; heavy tails |
| Predictive (pLTV) | Day 0–3 behavioural features → regression/GBM | Enables value-based bidding at scale | Needs volume; leakage and drift risks |

### 6.1 Cumulative ARPU curve

Fit cumulative ARPU per install, e.g. ARPU(t) = c · t^d (0 < d < 1) or ARPU(t) = c · ln(1 + t), on matured days, then extrapolate to H with the same tail caution as retention. Check that the implied daily revenue per install (the derivative) declines smoothly.

### 6.2 Multipliers

Derive from your own matured cohorts (or the closest comparable title you operate):

| | D7 | D30 | D90 | D180 |
|---|---|---|---|---|
| Matured cohorts, cumulative ARPU (gross) | $0.30 | $0.62 | $1.05 | $1.45 |
| Multiplier vs D7 | 1.00 | 2.07 | 3.50 | 4.83 |
| New cohort: D7 observed $0.34 → projected | $0.34 | $0.70 | $1.19 | $1.64 |

Re-derive multipliers after major monetization or live-ops changes, separately per platform and per major channel; low-intent traffic often has a flatter post-D7 curve (lower multiplier) than organic traffic.

### 6.3 Payer model

`IAP_LTV(H) = conversion(H) × payer_LTV(H)`. Conversion by day typically rises fast in the first week and slowly afterwards; payer LTV depends on repeat purchase and payer retention (payers retain better than non-payers, largely by selection). Use when payer counts are large enough (hundreds per cohort) that ARPPU is stable.

---

## 7. ROAS curves, break-even and payback

```
ROAS(t) = cumulative revenue per install by day t / CPI          (gross or net — always say which)
Payback day = min t such that cumulative net revenue per install ≥ CPI
Break-even ARPDAU at horizon H = CPI / (net_share × L(H))
```

### 7.1 Worked payback example

Retention D1 40%, D7 18%, D30 8%; ARPDAU $0.12 gross; CPI $2.50.

`python3 ${CLAUDE_PLUGIN_ROOT}/skills/player-analytics/scripts/analytics_calc.py payback --points "1:0.40,7:0.18,30:0.08" --arpdau 0.12 --cpi 2.50`

| Day | Retention (fit) | Lifetime days | Cum. ARPU (gross) | ROAS (gross) |
|---|---|---|---|---|
| 7 | 16.6% | 2.71 | $0.33 | 13.0% |
| 30 | 8.4% | 5.22 | $0.63 | 25.1% |
| 90 | 5.0% | 8.96 | $1.08 | 43.0% |
| 180 | 3.6% | 12.72 | $1.53 | 61.1% |
| 365 | 2.6% | 18.29 | $2.19 | 87.8% |

No payback within 365 days even on gross revenue; break-even ARPDAU ≈ $0.137 gross. With `--net-share 0.75`, D365 ROAS falls to about 66% and break-even ARPDAU rises to about $0.182. The unit economics do not support paid UA at this CPI: improve D30 (each point ≈ +15% lifetime), raise ARPDAU, or lower CPI through creative work (CPI = CPM / IPM; see `marketing-ua`).

### 7.2 Setting D7 ROAS targets

1. Choose the payback horizon *H* (cash position, risk appetite).
2. From matured cohorts, compute the multiplier m = ARPU(H) / ARPU(D7) on a **net** basis.
3. Required D7 net ROAS = 1 / m. With m = 4.83 (table in §6.2) for D180 break-even: D7 net ROAS ≥ 20.7%. Add a margin (e.g. target 120% at H) → D7 ≥ 24.8%.
4. Re-derive per platform and channel; a channel with a flatter curve needs a higher D7 target.

### 7.3 Reading ROAS curves

- Compare whole curves on matured cohorts; early ROAS ranks channels imperfectly.
- Gross-vs-net confusion is the most common error: IAP gross includes the store fee; mediation ad revenue is usually already net of the network's share.
- Cohort ROAS includes organic uplift only if you attribute it; blended ROAS (all revenue / all spend) is the finance view.
- ROAS on low CPI from incentivised or low-quality networks can look fine early and flatten fast.

---

## 8. Reading soft-launch numbers

Soft launch exists to answer, in order: does the game work technically, do players stay, do they pay, and can we buy them at a profit? Typical staged plan (durations depend on traffic and changes):

| Stage | Question | Primary KPIs | Gate examples (set your own in the contract) |
|---|---|---|---|
| 1. Technical | Does it run on real devices and networks? | Crash-free users, ANR, first-playable time p90, event QA pass | Crash-free users and ANR within store vitals thresholds; first playable p90 under target; analytics QA checklist passes |
| 2. Retention / engagement | Is the core loop and early meta sticky? | D1, D7, D7/D1, session length and sessions/DAU, FTUE funnel, level churn | `contract.analytics.kpi_targets` (`d1`, `d7`), D7/D1 ≥ ~0.33 as a practitioner screen |
| 3. Monetization | Do players pay and watch ads at healthy rates? | D7/D30 payer conversion, ARPDAU (IAP/ads), rewarded opt-in, cumulative ARPU D7/D30 | `arpdau_usd`, `payer_conversion` targets; offer funnel health |
| 4. Scale / UA | Can we acquire at a CPI the LTV supports, in target markets? | CPI by channel/creative, IPM, D7 ROAS, projected payback, D30 | Projected net payback within the chosen horizon with margin |

**Geo selection (practitioner convention, not a law):** tech and early retention tests often run in lower-CPI markets with device diversity; monetization and scale tests in markets whose players behave like the target launch markets (for English-speaking Western launches, Canada, Australia, New Zealand and the Nordics/Netherlands are frequently used proxies). Retention and monetization transfer imperfectly between geos; apply a geo adjustment or confirm in the target market before global launch.

### 8.1 Noise and sample size

| Installs per readout pool | D1 = 40% CI | D7 = 15% CI | D30 = 5% CI |
|---|---|---|---|
| 1,000 | ±3.0 pp | ±2.2 pp | ±1.4 pp |
| 3,000 | ±1.8 pp | ±1.3 pp | ±0.8 pp |
| 10,000 | ±1.0 pp | ±0.7 pp | ±0.4 pp |

With 1,000 installs you cannot tell D30 = 4% from 6%. Plan UA spend for each stage from these widths, and pool weekly cohorts rather than reacting to daily rows.

### 8.2 Traffic quality

- Retention depends on who you buy. A campaign optimised for cheap installs, incentivised traffic or a single viral creative can lower retention without any product change. Read KPIs by channel and creative; hold the UA mix stable while testing product changes.
- Organic and featured users retain differently from paid users; report them separately.
- Small soft launches over-weight early adopters of the genre; expect some regression at scale.

### 8.3 Trends beat snapshots

Plot each KPI by weekly cohort with confidence bands and release annotations. A rising D7 across three builds is stronger evidence than one good week. Decide on the latest **stable** build's cohorts, not on an average across builds.

### 8.4 Go / iterate / kill

| Evidence | Decision |
|---|---|
| Retention gates met, monetization near target, payback projected within horizon with margin | Scale UA gradually; keep monitoring ROAS curves on matured cohorts |
| Retention gates met, monetization below target | Iterate on monetization (offers, rewarded placements, economy sinks) with experiments; hold UA |
| D1 OK, D7/D1 low | First-week problem: core loop depth, early meta, difficulty walls; iterate 2–3 builds |
| D1 well below target after FTUE fixes, no trend up across builds | Kill or pivot per `contract.kill_criteria` (doctrine: scope ruthlessly) |
| Good KPIs but CPI too high for LTV | Creative and store-page work (IPM), audience/geo strategy; or redesign hook for broader appeal |

### 8.5 Pre-launch proxies

Before any real players, the studio can only proxy retention: bot time-to-first-reward, first-session length from persona playthroughs, FTUE step timings, level win-rate curves from bot runs (`playtest-report.schema.json` → `metrics`). These catch broken FTUEs and difficulty spikes but do not predict retention; none of the surveyed AI QA tools claim to (see `qa-testing`).

---

## 9. Common modelling mistakes

| Mistake | Symptom | Fix |
|---|---|---|
| Fitting an exponential to game retention | LTV projections far below reality; tail collapses | Power or hybrid tail; validate on a holdout point |
| Extrapolating a power curve to infinity | LTV keeps growing with horizon; "LTV" of $10 from 14 days of data | Fixed horizon; hybrid tail; ≤ 3–6× extrapolation |
| Including immature cohorts | Dn appears to fall over time | Maturity filter |
| Mixing platforms/channels in one curve | Curve shape changes as mix shifts | Fit per segment; weight to target mix |
| Constant early ARPDAU for IAP games | LTV understated | ARPDAU by player age |
| Gross revenue in payback | Payback appears 20–30% sooner than reality | Net revenue; state basis |
| No uncertainty | Single-point projections drive large spend | Bootstrap intervals; scenario table (low/base/high) |
| Classic retention as survival | Churn overstated | Rolling retention or inactivity rule for survival |
| Treating soft-launch geo as target geo | Global launch underperforms | Geo adjustment; confirm in target market |
| Ignoring content runway | Curve fitted on days 1–30 assumes content forever | Runway check; live-ops plan |

---

## 10. Tool usage

```bash
# Fit retention curves (plugin script; --model power|exp, default power; rates are ratios in (0, 1], days > 0, at least two points)
# Prints a=0.4417 b=0.52181 R2(log)=0.987 and the D1..D365 projection; --json adds per-point fitted values and warnings
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/retention_ltv.py fit --points "1:0.42,7:0.18,30:0.07" --model power --json

# LTV from retention points and a flat ARPDAU over a horizon (default 365, maximum 3650 days)
# Prints 15.842 lifetime days and LTV = 0.11 x 15.842 = 1.7426; --json adds ltv_by_day for D7, D30, D90, D180 and D365
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/retention_ltv.py ltv --points "1:0.42,7:0.18,30:0.07" --arpdau 0.11 --horizon 365 --json

# ROAS checkpoints, payback day, break-even ARPDAU (skill script; --net-share for net basis, --strict exits 1 without payback)
python3 ${CLAUDE_PLUGIN_ROOT}/skills/player-analytics/scripts/analytics_calc.py payback --points "1:0.42,7:0.18,30:0.07" --arpdau 0.11 --cpi 1.80 --net-share 0.8 --horizon 365

# Retention triangle and weighted points from raw activity (feeds --points above)
python3 ${CLAUDE_PLUGIN_ROOT}/skills/player-analytics/scripts/analytics_calc.py cohort --csv activity.csv --days 1,3,7,14,30

# Interval for a soft-launch KPI
python3 ${CLAUDE_PLUGIN_ROOT}/skills/player-analytics/scripts/analytics_calc.py ci --success 152 --n 1000
```

Record soft-launch gates as `contract.analytics.kpi_targets` and kill criteria as `contract.kill_criteria`; store each weekly readout in `.gamestudio/reports/`.

---

## 11. Volatile facts (as of Oct 2026 — verify before relying)

- Retention benchmarks (GameAnalytics data via secondary sources): median D1 about 22%, D7 just under 4%, D30 about 0.7–0.8%; top 1% about 64–68% D1 and 13–15% D30. Practitioner viability screens for marketed titles: about 25–30% D1, 10–15% D7, 3–6% D30. — [Segwise](https://segwise.ai/blog/mobile-gaming-app-user-retention-strategies); [Playio](https://blog.playio.co/d1-d7-d30-retention-benchmarks-2026)
- D7/D1 below ~0.30 as a first-session warning is practitioner consensus, not a rule. — [GameDev.net](https://gamedev.net/blogs/entry/2298160-the-d7d1-retention-ratio-for-mobile-games-a-complete-guide)
- D7 ROAS reference points relayed from Liftoff data: about 7.6–7.8% for casual and about 4.3% for mid-core globally (blog relay; definitions unclear). — [The Social Outline](https://thesocialoutline.com/blog/mobile-app-cpi-benchmarks-2026)
- CPI ranges are inconsistent across vendor blogs (e.g. blended tier-1 about $4.22 iOS / $2.97 Android per one source; hyper-casual Android near $0.40). — [Segwise](https://segwise.ai/blog/cpi-ipm-roas-benchmarks-optimizing-ad-spend.md); [FoxData](https://foxdata.com/en/blogs/2026-mobile-game-user-acquisition-cost-benchmarks-how-much-should-you-spend/)
- Apple EU commission structure from Oct 1, 2026 (affects net share): App Store + IAP 26% (15% reduced), alternative PSP 20% (10%), link-out 15% (10%). — [Apple Newsroom, Aug 2026](https://www.apple.com/newsroom/2026/08/apple-announces-changes-for-apps-in-the-european-union/)
- Market context: mobile game IAP revenue about $82B in 2025 (+1%); H1 2026 IAP about $40B (−2% YoY) with downloads down about 12% — a flat market that rewards retention and live-ops over pure UA scale. — [Sensor Tower press release](https://sensortower.com/press/press-release-sensor-tower-state-of-gaming-gaming-drove-52-billion-downloads-82b-iap-revenue-on-mobile-and-12b-premium-revenue-on-steam); [MobileGamer.biz data digest](https://mobilegamer.biz/data-digest-sensor-towers-h1-analysis-hay-days-comeback-julys-top-games-big-krafton-numbers-and-more/)
