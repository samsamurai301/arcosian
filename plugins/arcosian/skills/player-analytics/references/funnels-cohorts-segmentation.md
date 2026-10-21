# Funnels, Cohorts and Segmentation

The analyst's core toolkit for turning raw game events into diagnoses: step funnels (FTUE, store, offers), level funnels and difficulty-spike detection, progression analysis, cohort tables and how to read them, segmentation (by source, geography, device, behaviour and spend), payer analysis, behavioural clustering, RFM, and churn-prediction features. Every method comes with the exact metric definitions, a procedure, a worked example with numbers, the statistical traps (survivorship, Simpson's paradox, selection bias, censoring), and SQL patterns for the Firebase BigQuery export. The skill-local calculator `scripts/analytics_calc.py` computes funnels, cohort triangles and RFM segments from CSV; level analysis uses the plugin's `difficulty_curve.py analyze`.

## Contents

1. Step funnels: definitions and construction
2. Level funnels and difficulty spikes
3. Progression analysis
4. Cohort tables: building and reading them
5. Segmentation: dimensions and traps
6. Payer segmentation and spend analysis
7. Behavioural clustering
8. RFM for games
9. Churn prediction: labels, features, models, action
10. SQL patterns (Firebase → BigQuery export)
11. Tool commands

---

## 1. Step funnels: definitions and construction

A funnel is an ordered list of steps and the share of users who complete each.

| Choice | Options | Default for games |
|---|---|---|
| Unit | users (did the user ever do step *k*) or events | Users |
| Order | strict (step *k* must follow step *k−1*) or any order | Strict for FTUE and purchase; any order for "feature discovery" |
| Window | time allowed from step 1 to step *k* | FTUE: first session or first 24 h; purchase funnel: same session |
| Open vs closed | closed (must enter at step 1) or open (can enter at any step) | Closed; an open funnel can show steps larger than previous ones |
| Population | all users, a cohort, a segment | One install cohort or week; never mix app versions with different step definitions |

**Metrics per step:** count, conversion from previous step, conversion from start, absolute drop, share of total loss, and median time from previous step. Normalise long steps: a 30-second step losing 8% is worse than a 3-minute step losing 8%.

### 1.1 The FTUE funnel

```
store install ─► first_open ─► first playable frame (load) ─► tutorial_begin ─► tutorial_step[1..n]
  ─► tutorial_complete ─► level 3 complete ─► level 10 complete ─► session 2 ─► D1 return
```

Worked example (one week's installs, 10,000 first opens):

`python3 ${CLAUDE_PLUGIN_ROOT}/skills/player-analytics/scripts/analytics_calc.py funnel --steps "first_open:10000,tutorial_begin:9200,ftue_step_3:7800,tutorial_complete:7100,level_5_complete:5600,d1_return:3900"`

| Step | Users | From previous | Share of total loss |
|---|---|---|---|
| first_open | 10,000 | — | — |
| tutorial_begin | 9,200 | 92.0% | 13.1% |
| ftue_step_3 | 7,800 | 84.8% | 22.9% |
| tutorial_complete | 7,100 | 91.0% | 11.5% |
| level_5_complete | 5,600 | 78.9% | 24.6% |
| d1_return | 3,900 | 69.6% | 27.9% |

Reading: 8% of players never reach the first tutorial frame — that is a loading or crash problem (check first-playable time p90 and crash-free rate by device tier) and the cheapest to fix. Steps 1–3 lose 15% in what should be a 30-second span; inspect that step's clarity in playtest video. Levels 4–5 lose 21% — look at their level metrics (section 2). D1 return of 39% of first opens equals classic D1 (calendar) if `d1_return` is "active on day 1".

**Fix order:** biggest absolute loss × cheapest fix × earliest step (an early fix lifts every later step).

### 1.2 Other funnels worth building

| Funnel | Steps | Typical question |
|---|---|---|
| Store | `store_opened` → `offer_shown` (product viewed) → `iap_purchase_started` → `iap_purchase_completed` | Where does purchase intent die: price, value perception, payment failure? |
| Offer | `offer_shown{offer_id}` → start → complete, per trigger | Which triggers convert without frustration timing? |
| Rewarded ad | `rv_offer_shown` → `rv_started` → `rv_completed` per placement | Which rewards are valued? Where do ads fail to load? |
| Social | `social_invite_sent` → link opened → install → `social_invite_accepted` → invitee D1 | K-factor components |
| Live event | eligible → `liveops_event_join` → milestone 1..n → final reward | Event difficulty and reward pacing |
| Notification | permission prompt shown → granted → push received → `push_opened` → session | CRM reach and value |

---

## 2. Level funnels and difficulty spikes

### 2.1 Metrics per level

| Metric | Formula | What it shows |
|---|---|---|
| Starters | unique users with ≥ 1 `level_start` on level *L* | Reach (the level funnel) |
| Attempts | count of `level_start` on *L* | Effort |
| Win rate per attempt | wins / attempts | Raw difficulty; the number tuned against `level-spec.difficulty_target.win_rate` |
| First-try win rate | users winning on attempt 1 / starters | Difficulty for a fresh player; less biased by stuck players' repeated attempts |
| Attempts per success | attempts / wins; also p50 and p90 of attempts-to-win per user | `level-spec.difficulty_target.attempts_p50` |
| Completion rate | users who ever win *L* / starters | Hard wall detection |
| **Churn after level** | users whose furthest `level_start` is *L* and who have been inactive ≥ *k* days / starters of *L* | The level's cost in players |
| Quit rate | `level_end{reason=quit}` / attempts | Frustration and interruption |
| Assist rate | attempts with boosters, continues or revives / attempts | Hidden difficulty: a "fair" win rate propped up by boosters |
| Monetization at level | purchases, gem continues and rewarded views per starter | Whether a spike is acting as a paywall (an ethics flag) |
| Near-miss share | wins with ≤ 2 moves left / wins; fails with ≤ 1 target left / fails | Tension; distinguishes tense-but-fair from unwinnable |
| Time per attempt | median `duration_sec` | Long attempts amplify the pain of failure |

### 2.2 Spike detection procedure

1. Use only users whose install is at least *k* + 7 days old so "churned after level" is mature (right-censoring otherwise inflates churn at recent levels).
2. Compute the metrics above for every level.
3. Estimate the **baseline** per-level churn as the rolling median over the neighbouring ±5 levels (players leave at a slowly decaying base rate even with perfect levels).
4. Flag a level as a **spike** when churn-after-level ≥ 2× baseline **or** win rate per attempt is more than ~25 points below the neighbouring median and the level is not a designed `test`/boss level (the level spec's `teach` field says which levels are intended to be hard).
5. For each spike, look at near-miss distributions, quit rate and assist rate before changing the level: a spike with many near-misses needs a small tuning step (one or two moves); one with no near-misses needs a redesign.
6. Change via remote config where possible; verify with the next cohort; re-run bots to recalibrate (see `level-design`, `progression-difficulty`).

### 2.3 Worked example

| Level | Starters | Attempts | Wins | Win rate/attempt | Attempts per win | Churn after | Churn rate |
|---|---|---|---|---|---|---|---|
| 1 | 10,000 | 10,400 | 10,000 | 96.2% | 1.04 | 150 | 1.50% |
| 2 | 9,850 | 10,600 | 9,850 | 92.9% | 1.08 | 120 | 1.22% |
| 3 | 9,730 | 10,900 | 9,730 | 89.3% | 1.12 | 110 | 1.13% |
| 4 | 9,620 | 12,200 | 9,620 | 78.9% | 1.27 | 140 | 1.46% |
| 5 | 9,480 | 11,800 | 9,480 | 80.3% | 1.24 | 130 | 1.37% |
| **6** | 9,350 | 23,400 | 9,100 | **38.9%** | **2.57** | **610** | **6.52%** |
| 7 | 8,740 | 10,300 | 8,740 | 84.9% | 1.18 | 120 | 1.37% |
| 8 | 8,620 | 10,800 | 8,620 | 79.8% | 1.25 | 115 | 1.33% |
| 9 | 8,505 | 14,300 | 8,505 | 59.5% | 1.68 | 160 | 1.88% |
| 10 | 8,345 | 16,300 | 8,345 | 51.2% | 1.95 | 190 | 2.28% |
| 11 | 8,155 | 9,600 | 8,155 | 84.9% | 1.18 | 100 | 1.23% |
| 12 | 8,055 | 10,500 | 8,055 | 76.7% | 1.30 | 105 | 1.30% |

Baseline churn ≈ 1.37% per level (median). Level 6 churns 4.8× baseline at a 39% win rate in the FTUE zone — a clear spike; 250 players never beat it. Levels 9–10 are a designed boss pair (spec says `test`): churn 1.4–1.7× baseline is acceptable if near-miss share is high; watch them. Action for level 6: if most fails end with 1 target left, add one or two moves via remote config; otherwise swap it with a later level and replace it with a `teach` level. Expected recovery: roughly the excess churn, 610 − 9,350 × 1.37% ≈ 480 players per 10,000 installs (about 5% of the cohort reaching level 6) — significant for D7.

A first screen from a CSV of counts `level,attempts,wins,churned`: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/difficulty_curve.py analyze --data levels.csv --json`. The script is coarser than the procedure in §2.2. It compares each level with the median of up to three neighbours on each side (not ±5), flags `win_rate_dip` at 0.15 below that median (15 points, not 25) and `churn_spike` at ≥ 2× the median and ≥ 0.03 above it, divides both `wins` and `churned` by the `attempts` column you supply, never flags levels under 30 attempts, and exits 1 when it flags anything. It does not read `level-spec`, so designed hard levels are flagged too. On the table above with attempts as the denominator it flags levels 6, 9 and 10 for `win_rate_dip` only (level 6's churn is 2.6% of attempts, under the +0.03 margin). With starters in the `attempts` column and users who won in `wins`, it flags level 6 for `churn_spike` (6.5% against a 1.4% median) and leaves the boss pair alone. Choose the denominator on purpose, and treat the output as a shortlist for §2.2.

### 2.4 Traps

- **Survivorship.** Later levels are played only by players who survived earlier ones (more skilled, more committed), so raw win rates rise artificially with level number. Compare levels within a narrow band, or use first-try win rate of players with similar recent performance.
- **Attempt-weighting.** Win rate per attempt is dominated by stuck players replaying; report first-try win rate alongside.
- **Boosters mask difficulty.** A level with 75% win rate and 60% assist rate is a hard level.
- **DDA contamination.** If dynamic difficulty adjusts levels, analyse by `dda_step` and report "unassisted" difficulty separately.
- **Time-based churn vs level-based churn.** A player who stops at level 6 on day 5 may have churned for meta reasons; cross-check churn-after-level against days since install.

---

## 3. Progression analysis

| Metric | Definition | Use |
|---|---|---|
| Progression velocity | levels completed per active day, by cohort and segment (median and p25/p75) | Content runway and pacing vs `contract.progression` |
| Time to milestone | days (or sessions) from install to milestone *M*, distribution among those who reach it plus share who reach it by day 7/30 | Meta pacing; compare against the progression model (`progression_calc.py time-to-level`) |
| Content runway | (levels available − median level reached) / median velocity | Days until median player runs out of content; must exceed the content-release cadence |
| Progress-retention curve | D7 (or D30) retention grouped by level reached on day 0 (or day 1) | Which early depth predicts retention ("players who reach level 15 on day 0 retain 2× better") — correlation, test causally before acting |
| Wall detection | velocity drop by player age: levels/day falling sharply at a given level band | Economy or difficulty walls (cross-check currency balances at that band) |
| Catch-up gap | p90 − p10 of level reached at day 14 | Social/competitive features need cohorts not to be too spread |

**Careful with the progress-retention curve.** Players who progress further on day 0 are partly just more engaged players. "Make everyone reach level 15 on day 0" by making levels easier may not transfer the retention — verify with an experiment (`references/experimentation.md`).

**Worked runway example.** 600 levels shipped; median player at day 30 has reached level 140 with a velocity of 4.5 levels/active day and plays 18 active days/month. Runway ≈ (600 − 140) / 4.5 ≈ 102 active days ≈ 5–6 months. Content cadence of 20 levels per 2 weeks (≈ 1.4 levels/calendar day) is lower than median consumption of ≈ 2.7 levels/calendar day (4.5 × 18/30), so the gap closes eventually: plan non-level content (events, meta) or increase level throughput (`procedural-generation`, `level-design`).

---

## 4. Cohort tables: building and reading them

### 4.1 Building a retention triangle

Rows = install cohorts (day or week), columns = days since install, cells = classic retention. Only show cells where the cohort has aged enough (maturity).

`python3 ${CLAUDE_PLUGIN_ROOT}/skills/player-analytics/scripts/analytics_calc.py cohort --csv activity.csv --days 1,3,7,14,30 [--mode rolling] [--asof 2026-10-05]`

Input: one row per user-active-day, columns `user_id,install_date,active_date`. Output: the triangle, the installs-weighted average across mature cohorts with a Wilson 95% interval, and D7/D1 and D30/D7 diagnostics.

```
cohort      installs     D1     D3     D7    D14    D30
2026-09-01       482  42.1%  25.7%  18.7%  11.2%   7.5%
2026-09-02       404  40.6%  28.2%  17.6%  11.9%   7.9%
2026-09-03       576  42.0%  26.2%  14.9%  13.2%   6.2%
...
weighted: D1 42.0% [41.1-43.0] n=10764 ... D30 7.1% [6.2-8.1] n=2555
d7_over_d1 = 0.395   d30_over_d7 = 0.427
```

### 4.2 Reading a cohort table

| Pattern | Looks like | Likely cause | Check |
|---|---|---|---|
| **Row** effect | One cohort row lower across all ages | Acquisition quality changed for that install date (new channel, creative, geo, incentivised traffic, featuring) | Split the row by channel and country |
| **Column** effect | A given age (e.g. D7) drops for all cohorts after some date | Product change that affects players at that age (meta unlock, difficulty wall, economy change) | Release notes; which cohorts crossed that age after the release |
| **Diagonal** effect | Cells on the same calendar date move together across cohorts | Calendar event: outage, holiday, live event, server issue, store featuring, push campaign | Calendar annotations; DAU on that date |
| Smooth improvement down the rows | Newer cohorts retain better at every age | Product improvements in FTUE/early game | Attribute to builds; confirm with an A/B where possible |
| Curve flattening later | D14→D30 decay slows in newer cohorts | Better meta, social features, events | Feature adoption by cohort |

### 4.3 Revenue and conversion cohorts

Build the same triangle with cumulative ARPU (revenue per install) and cumulative payer conversion. These are the inputs for ROAS curves and LTV multipliers (`references/ltv-retention-modeling.md`). Use the same maturity rule; never average a D30 cell that includes cohorts younger than 30 days.

### 4.4 Precision and minimum sizes

Each cell is a binomial proportion. For a daily cohort of 500 installs, a D7 of 15% has a 95% interval of about ±3.1 pp — day-to-day row differences of 2–3 points are noise. Weekly cohorts or pooled averages with intervals are the default for decisions; daily rows are for spotting outages and channel changes.

---

## 5. Segmentation: dimensions and traps

| Dimension | Values | Typical insight |
|---|---|---|
| Acquisition source | organic, paid by network, campaign, creative; cross-promo; referral | Channel quality: retention and payer conversion vary several-fold across networks |
| Geography | country, or tiers by purchasing power | ARPDAU, eCPM and CPI differ widely; mix shifts move averages |
| Platform | iOS, Android | iOS typically higher ARPDAU and retention; never pool for targets |
| Device tier | low/mid/high | Low-end churn from performance; load times |
| App version | build | Release regressions |
| Engagement level | sessions/day or active days/week bands | Who your core is |
| Spend | non-payer, payer tiers | Monetization and live-ops targeting (section 6) |
| Lifecycle state | new, current, at-risk, churned, resurrected | CRM and live-ops targeting |
| Experiment variant | per experiment | Only with randomised assignment |

**Rules:**
1. **Segment on pre-treatment attributes.** Segment by things fixed before the behaviour you measure (install source, country, device), not by outcomes ("players who bought the pass retain better" is selection, not effect).
2. **Watch Simpson's paradox.** Overall ARPDAU can fall while every country's ARPDAU rises, if the mix shifts toward low-ARPDAU countries. Always decompose a change into within-segment change and mix change:
   `Δ overall = Σ_s (w_s,new × m_s,new − w_s,old × m_s,old) = Σ_s w_s,new Δm_s (within) + Σ_s m_s,old Δw_s (mix)`.
3. **Minimum segment size.** Do not report a segment whose metric's 95% interval is wider than the effect you care about; merge small segments ("other").
4. **Fix the segmentation before looking.** Choosing segments after seeing the data (until one looks significant) is a multiple-comparisons trap.

---

## 6. Payer segmentation and spend analysis

### 6.1 Spend tiers

Avoid fixed industry labels (minnow/dolphin/whale) with borrowed dollar thresholds. Derive tiers from your own distribution, e.g. lifetime spend percentiles **among payers**:

| Tier | Definition (example) | Typical role |
|---|---|---|
| `non_payer` | lifetime spend = 0 | The large majority; ad revenue, social fabric, liquidity in PvP and economies |
| `payer_low` | payer, below the 50th percentile of payer spend | Starter packs, single purchases |
| `payer_mid` | 50th–90th percentile | Repeat buyers, passes |
| `payer_high` | top 10% of payers | Large share of IAP revenue; service, fairness and well-being considerations |

Recompute thresholds quarterly and store the tier as the `payer_tier` user property.

### 6.2 Concentration

Sort payers by lifetime spend; plot the cumulative share of revenue vs cumulative share of payers (Lorenz curve). Report the revenue share of the top 1% and top 10% of payers and the Gini coefficient. Rising concentration means the game depends on fewer people: revenue is fragile, and the ethics review (`monetization`, `legal-ethics`) should check spending-limit features, purchase-frequency alerts and age signals.

### 6.3 First-purchase analysis

| Question | Metric |
|---|---|
| When do players convert? | Distribution of days (and sessions) from install to first purchase; share of all eventual payers who converted by D1/D3/D7 |
| What do they buy first? | First-purchase SKU mix and price; conversion of `offer_shown` by trigger |
| Does the first purchase lead to more? | Repeat purchase rate within 30 days by first SKU |
| Are payers more retained because they paid? | Compare against matched non-payers with similar pre-purchase engagement (not all non-payers) |

**Selection-bias trap:** "Payers retain 3× better" is mostly because engaged players pay, not because paying retains. Use matched comparisons or experiments with offer exposure.

---

## 7. Behavioural clustering

Clustering groups players by how they play, to inform personas, feature priorities and live-ops targeting. A well-known example in the research literature is Drachen and colleagues' work on clustering player behaviour in commercial games (e.g. *Guns, Swords and Data*, IEEE CIG 2012), which applied k-means and archetypal analysis to telemetry.

### 7.1 Procedure

1. **Window and population.** One behavioural window (e.g. days 1–14 since install) for players who were active at least *n* days in it; separate clustering for very different modes (PvP vs PvE).
2. **Features (8–20).** Intensity: sessions/day, minutes/day, active days. Progression: levels/day, % levels won first try. Economy: earn/spend ratio, booster use per level, hoard days. Monetization: rewarded views/day, purchases (flag, not amount, to avoid spend dominating). Social: friends, group membership, invites. Live-ops: event participation share. Timing: weekend share, session-start hour spread.
3. **Transform.** Log-transform heavy-tailed counts (`log1p`), cap at p99, standardise (z-scores). Drop near-duplicate features (correlation > 0.9).
4. **Algorithm.** k-means as a baseline (fast, interpretable centroids); Gaussian mixtures for soft membership; hierarchical clustering for small samples; archetypal analysis to describe extremes.
5. **Choose k.** Elbow and silhouette as guides, then interpretability: 4–7 clusters that a designer can describe in a sentence and act on.
6. **Name and profile.** For each cluster: size, centroid in original units, retention, ARPDAU, top features vs the population. Example names: "Daily routine solvers", "Weekend bingers", "Collectors", "Competitors", "Socialisers", "Lapsing samplers".
7. **Validate.** Re-run on a different cohort; clusters should reappear with similar centroids (stability). Check that clusters differ on outcomes you did not cluster on (retention, LTV), otherwise they are descriptive only.
8. **Use.** Persona briefs for `player-simulator` runs, live-ops segment definitions (via user properties or remote-config audiences), feature prioritisation (which cluster a feature serves).

### 7.2 Pitfalls

- Clustering on outcomes (spend, retention) produces "spenders" and "churners", which is circular.
- Unscaled features let one variable (minutes played) define every cluster.
- Clusters drift with game updates; refresh quarterly and version cluster definitions.

---

## 8. RFM for games

RFM (recency, frequency, monetary) is a fast, explainable segmentation from direct marketing, adapted for games:

| Letter | Game definition | Score direction |
|---|---|---|
| R | days since last active day (or since last purchase for payer-only RFM) | lower = better |
| F | active days in the last 28 (or purchases in the last 90 for payers) | higher = better |
| M | spend in the last 90 days (IAP net; optionally + ad revenue) | higher = better; non-spenders score 1 |

`python3 ${CLAUDE_PLUGIN_ROOT}/skills/player-analytics/scripts/analytics_calc.py rfm --csv rfm.csv --out rfm_scores.csv` (columns `user_id,recency_days,frequency,monetary`; quantile scores 1–5; non-spenders get M = 1 and spenders are binned among themselves).

| Segment (first matching rule) | Rule on 1–5 scores | Typical action |
|---|---|---|
| `champions` | R ≥ 4, F ≥ 4, M ≥ 4 | Recognition, early access, fair-value bundles; avoid over-messaging |
| `loyal` | R ≥ 3, F ≥ 4 | Social and competitive features, passes, events |
| `cant_lose` | R ≤ 2, F ≥ 4, M ≥ 4 | Personal win-back (what changed?), service outreach |
| `at_risk` | R ≤ 2, F ≥ 3 | Re-engagement push with content news; check recent difficulty walls |
| `new_or_promising` | R ≥ 4, F ≤ 2 | Onboarding continuation, first-week goals, starter value |
| `potential_loyal` | R ≥ 3, F ≥ 2 | Habit hooks: daily goals, streaks with forgiveness |
| `lost` | R = 1, F = 1 | Low-cost reactivation only; exclude from frequent messaging |
| `hibernating` | R ≤ 2 (rest) | Event-driven win-back with holdout |
| `needs_attention` | everything else | Inspect manually |

Always measure CRM actions against a random holdout within the segment (`references/experimentation.md` §11).

---

## 9. Churn prediction: labels, features, models, action

### 9.1 Label

- **Observation date** *t₀*; **observation window** of past behaviour, e.g. the 14 days before *t₀*; **prediction window**, e.g. the next 7 days.
- Label = 1 if the player has no activity in (*t₀*, *t₀* + inactivity *k*] (use the churn rule from `references/kpi-dictionary.md` §4.1).
- Train on many observation dates (rolling) to avoid seasonal artefacts; score only players active in the last few days (others are already churned).
- Separate models for new players (days 0–7) and established players; their churn drivers differ.

### 9.2 Features that tend to carry signal in games

| Family | Features |
|---|---|
| Recency and trend | days since last session; sessions in last 3 days vs prior 11 (ratio); slope of daily minutes over the window |
| Session shape | median session length and its change; sessions ending within 60 s of a fail; share of sessions ending on a fail |
| Progression | levels completed in window; consecutive fails on current level; attempts on current level; days stuck on current level |
| Economy | soft-currency balance vs cost of next meaningful sink; boosters in inventory; energy-depletion events per day |
| Social | friends active in last 7 days; group membership; group activity |
| Monetization | payer flag; days since last purchase; offers declined; rewarded views trend |
| Live-ops | participation in current event; event progress vs pace needed |
| Technical | crashes, errors, long loads in window; device tier |
| Lifecycle | days since install; install source; push enabled |

Published examples of game churn prediction from telemetry include work by Hadiji and colleagues (*Predicting Player Churn in the Wild*, IEEE CIG 2014) across several freemium titles; recency and activity-trend features tend to rank among the strongest predictors in such studies.

### 9.3 Models and evaluation

1. Baseline: logistic regression on 10–20 features (interpretable, calibrated).
2. Stronger: gradient-boosted trees; check feature importance and partial dependence for sense.
3. Evaluate on later time periods (out-of-time validation), not random splits.
4. Metrics: AUC for ranking, precision/recall at the top *k*% you can act on, calibration (predicted vs observed churn by decile), lift vs recency-only rule. A recency-only rule is a strong baseline; a model that barely beats it is not worth operating.
5. Leakage checks: no features computed after *t₀*; no features that encode the label (e.g. "days active in next week").

### 9.4 From risk to action

Risk is not the same as responsiveness: the highest-risk players may be unpersuadable, and some low-risk players respond strongly. Use an experiment per intervention (push with content news, difficulty assist, gift) with a holdout, and ideally an uplift model (difference in retention between treated and holdout as a function of features). Never use churn risk to target pressure offers at vulnerable players; route intervention designs through the ethics rules in `monetization`.

---

## 10. SQL patterns (Firebase → BigQuery export)

The Firebase export writes one table per day (`events_YYYYMMDD`, plus intraday tables) with one row per event: `event_date`, `event_timestamp` (microseconds), `event_name`, `event_params` (repeated key/value), `user_pseudo_id`, `user_id`, `user_first_touch_timestamp`, `platform`, `geo.country`, `app_info.version`. Adapt names to your dataset; these are skeletons, not tested against a live dataset.

**Parameter helper**

```sql
-- string param
(SELECT ep.value.string_value FROM UNNEST(event_params) ep WHERE ep.key = 'level_id') AS level_id,
-- int param
(SELECT ep.value.int_value FROM UNNEST(event_params) ep WHERE ep.key = 'attempt') AS attempt
```

**Classic retention triangle (calendar days, UTC)**

```sql
WITH activity AS (
  SELECT user_pseudo_id,
         DATE(TIMESTAMP_MICROS(user_first_touch_timestamp)) AS install_date,
         DATE(TIMESTAMP_MICROS(event_timestamp))            AS active_date
  FROM `proj.analytics_123.events_*`
  WHERE _TABLE_SUFFIX BETWEEN '20260901' AND '20261015'
    AND event_name = 'user_engagement'
  GROUP BY 1, 2, 3
), cohorts AS (
  SELECT install_date, COUNT(DISTINCT user_pseudo_id) AS installs
  FROM activity WHERE active_date = install_date GROUP BY 1
)
SELECT a.install_date, c.installs,
       DATE_DIFF(a.active_date, a.install_date, DAY) AS day_n,
       COUNT(DISTINCT a.user_pseudo_id) / c.installs AS retention
FROM activity a JOIN cohorts c USING (install_date)
WHERE DATE_DIFF(a.active_date, a.install_date, DAY) IN (1, 3, 7, 14, 30)
  AND DATE_ADD(a.install_date, INTERVAL DATE_DIFF(a.active_date, a.install_date, DAY) DAY) <= DATE '2026-10-15'
GROUP BY 1, 2, 3
ORDER BY 1, 3;
```

**Level metrics with churn after level**

```sql
WITH lv AS (
  SELECT user_pseudo_id, event_name, DATE(TIMESTAMP_MICROS(event_timestamp)) AS d,
         (SELECT ep.value.string_value FROM UNNEST(event_params) ep WHERE ep.key = 'level_id') AS level_id,
         (SELECT ep.value.int_value    FROM UNNEST(event_params) ep WHERE ep.key = 'success')  AS success
  FROM `proj.analytics_123.events_*`
  WHERE event_name IN ('level_start', 'level_end')
), last_seen AS (
  SELECT user_pseudo_id, MAX(DATE(TIMESTAMP_MICROS(event_timestamp))) AS last_active
  FROM `proj.analytics_123.events_*` GROUP BY 1
), furthest AS (   -- furthest level started; assumes level ids sort in play order (w1_l001...)
  SELECT user_pseudo_id, MAX(level_id) AS furthest_level FROM lv WHERE event_name = 'level_start' GROUP BY 1
)
SELECT l.level_id,
       COUNT(DISTINCT IF(l.event_name = 'level_start', l.user_pseudo_id, NULL)) AS starters,
       COUNTIF(l.event_name = 'level_start')                                    AS attempts,
       COUNTIF(l.event_name = 'level_end' AND l.success = 1)                     AS wins,
       COUNT(DISTINCT IF(f.furthest_level = l.level_id
                         AND s.last_active <= DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY),
                         l.user_pseudo_id, NULL))                                AS churned_after
FROM lv l JOIN furthest f USING (user_pseudo_id) JOIN last_seen s USING (user_pseudo_id)
GROUP BY 1 ORDER BY 1;
```

Booleans may arrive as `int_value` 0/1 or `string_value` depending on the SDK; check one event first. Export the result as `level,attempts,wins,churned` for `difficulty_curve.py analyze`.

**Strict funnel within the first 24 hours**

```sql
WITH e AS (
  SELECT user_pseudo_id, event_name, event_timestamp,
         MIN(IF(event_name = 'first_open', event_timestamp, NULL)) OVER (PARTITION BY user_pseudo_id) AS t0
  FROM `proj.analytics_123.events_*`
  WHERE event_name IN ('first_open', 'tutorial_begin', 'tutorial_complete')
)
SELECT
  COUNT(DISTINCT IF(event_name = 'first_open', user_pseudo_id, NULL)) AS s1_first_open,
  COUNT(DISTINCT IF(event_name = 'tutorial_begin'    AND event_timestamp - t0 <= 86400000000, user_pseudo_id, NULL)) AS s2_begin,
  COUNT(DISTINCT IF(event_name = 'tutorial_complete' AND event_timestamp - t0 <= 86400000000, user_pseudo_id, NULL)) AS s3_complete
FROM e WHERE t0 IS NOT NULL;
```

(This counts step reach within the window; enforce strict order with per-user `MIN(timestamp)` per step and compare timestamps when order matters.)

---

## 11. Tool commands

| Task | Command |
|---|---|
| Funnel conversion and biggest leak | `python3 ${CLAUDE_PLUGIN_ROOT}/skills/player-analytics/scripts/analytics_calc.py funnel --steps "a:1000,b:800,c:500"` |
| Retention triangle from activity CSV | `analytics_calc.py cohort --csv activity.csv --days 1,3,7,14,30 [--mode rolling]` |
| Confidence interval for a cell | `analytics_calc.py ci --success 75 --n 500` |
| RFM segments | `analytics_calc.py rfm --csv rfm.csv --out scores.csv` |
| Level difficulty and churn analysis | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/difficulty_curve.py analyze --data levels.csv --json` |
| Target curve for comparison | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/difficulty_curve.py generate --levels 60 --pattern sawtooth --base 0.9 --floor 0.45 --period 5` |
| Codex search | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py kb "churn after level" --skill player-analytics` |
