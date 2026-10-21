---
name: player-analytics
description: 'Player-analytics codex: KPI definitions (retention types, ARPDAU, LTV, ROAS, payback), event taxonomies for Firebase/GameAnalytics, funnels, level churn and difficulty spikes, cohorts, segmentation, RFM, churn models, A/B testing (power, SRM, peeking, CUPED), retention/LTV modelling, economy telemetry. Use when asked to "define KPIs", "design analytics events", "why did D7 drop", "size an A/B test", "project LTV" or "read soft-launch data".'
when_to_use: 'Instrumenting a game, reviewing soft-launch or live metrics, planning or reading experiments, projecting LTV and payback, tuning difficulty or economy from telemetry.'
---

# Player Analytics

The studio's measurement layer: how to define, instrument, read and act on player-behaviour data in a mobile game. It turns the doctrine "data-informed, not data-driven" into practice — every number has one definition, every event answers a named question, every experiment is sized before it starts, and every diagnosis is triangulated with what players actually experience. It serves the `data-analyst` agent first, and anyone who must answer "is this working, why, and what do we change?" — from the first internal build's event QA, through soft-launch gates, to live-ops reviews and UA scaling decisions.

## What this skill gives you

- A KPI dictionary with one formula per metric (classic/rolling/bracket retention, stickiness, ARPDAU, ARPU, ARPPU, conversion, ad metrics, LTV variants, CPI, IPM, ROAS, payback, K-factor, churn, reactivation), measurement conventions, a driver tree and sourced benchmark ranges.
- Event taxonomy design: naming, envelope, a full mobile-game event catalogue, parameters, user properties, versioning, privacy rules and mappings to Firebase/GA4 and GameAnalytics, wired to `event-taxonomy.schema.json` and `event_taxonomy.py`.
- Diagnostic methods: FTUE and store funnels, level funnels with churn-after-level and near-miss analysis, progression and content runway, cohort tables (row/column/diagonal reading), segmentation without Simpson's paradox, payer analysis, clustering, RFM, churn-prediction features and BigQuery SQL skeletons.
- Experimentation for games: hypotheses, primary and guardrail metrics, sample size and MDE with worked numbers, randomisation and exposure logging, SRM, novelty, sequential testing, CUPED, multiple comparisons, holdouts, bandits and remote-config design.
- Retention and LTV modelling: power/exponential/Weibull/sBG curves, fitting and holdout validation, tail correction, age-varying ARPDAU, multipliers, ROAS curves, break-even targets and soft-launch reading (the plugin's `retention_ltv.py` fits the power and exponential curves only; Weibull, sBG, hybrid tails and bootstrap intervals are method guidance).
- A stdlib calculator, `scripts/analytics_calc.py` (KPIs, Wilson intervals, funnels, cohort triangles, economy health, RFM, payback, SRM), plus the plugin's `ab_test.py`, `retention_ltv.py`, `difficulty_curve.py` and `event_taxonomy.py`.

## Core models

### 1. Definitions before numbers
Most metric disputes are definition mismatches: calendar-day vs 24-hour D1, installs vs first opens, gross vs net revenue, immature cohorts in averages. Fix the conventions (UTC days, classic retention, `first_open` installs, net revenue for decisions, mature cohorts only) before the first dashboard and tag every chart with its definition. (`references/kpi-dictionary.md` §1)

### 2. Retention is the product; read the shape, not one point
D1 measures the first session (load, FTUE, time-to-fun); D7 the core loop and early meta; D30 meta, content runway and social ties. The ratios diagnose: **D7/D1** below about 0.30 points to a first-session problem (practitioner heuristic), and a low **D30/D7** to goals running out in weeks 2–4. In a power-law model anchored at D30, raising D1 alone barely moves year-one lifetime; LTV lives in the tail. (`references/kpi-dictionary.md` §3, `references/ltv-retention-modeling.md` §4)

### 3. The unit-economics equation
`LTV(H) = net ARPDAU × L(H)`, where `L(H) = Σ R(t)` is expected active days per install in horizon *H*; `margin = LTV − CPI`; payback day = first day cumulative net ARPU ≥ CPI. Always state horizon and basis (gross/net). Extrapolated power-law tails inflate LTV — cap the horizon, use a hybrid tail and show an interval. (`references/ltv-retention-modeling.md`)

### 4. The revenue identity and the driver tree
`ARPDAU = daily payer conversion × ARPPU + impressions/DAU × eCPM / 1000`. Localise every revenue move along the tree: real or data artefact → mix (platform, geo, channel, build) → audience vs ARPDAU → conversion vs ARPPU vs ads. Hypotheses come after localisation, not before. (`references/kpi-dictionary.md` §9)

### 5. Cohorts, not aggregates
Aggregate DAU and revenue mix old and new players and hide everything. Read install-cohort tables: a **row** effect is acquisition quality, a **column** effect is a product change at a player age, a **diagonal** effect is a calendar event. (`references/funnels-cohorts-segmentation.md` §4)

### 6. Events exist to answer questions
The taxonomy is the analytics contract: state changes not clicks, one event per concept with parameters for variants (`level_end` + `success` + `reason`), low cardinality, stable ids, money in micros, no PII, versioned like code, asserted in deterministic playthroughs. (`references/event-taxonomy-design.md`)

### 7. Difficulty is read through churn, not win rate alone
Per level: win rate per attempt, first-try win rate, attempts p50/p90, **churn after level vs a rolling baseline**, quit and assist rates, near-miss and fail-distance distributions. A spike with fails one target short needs a move or two; a spike with fails far from the goal needs a redesign or reorder. (`references/funnels-cohorts-segmentation.md` §2, `references/telemetry-for-design.md` §2)

### 8. Economies are flows and stocks
Per currency: sink/source ratio, net flow per DAU-day, balance percentiles by player age, hoard days (balance ÷ daily spend), broke share (below the cheapest meaningful sink). Hoarders and broke players coexist; one global price change hurts one of them. Check live flows against `economy_sim.py` and fix the model when they drift. (`references/telemetry-for-design.md` §3)

### 9. Experiments: power first, one primary, guardrails, no peeking
Write the hypothesis and decision rule before building. One primary metric, explicit guardrails (D1/D7, crashes, revenue). Size for the MDE the decision needs — halving the MDE quadruples the sample; revenue metrics need far more than proportions. Check SRM before reading anything. Peeking at a fixed-horizon test inflates false positives (about 14% with 5 looks at nominal 5%); use group-sequential boundaries if you must look. (`references/experimentation.md`)

### 10. Every number has a noise band
A rate from *N* users has SE ≈ √(p(1−p)/N). With 1,000 installs D1 = 40% is ±3 pp and D30 = 5% is ±1.4 pp (±27% relative). Decide on pooled weekly cohorts with intervals, not daily rows. (`analytics_calc.py ci`)

### 11. Correlation traps are the default, not the exception
Selection ("payers retain better", "guild members retain better"), Simpson's paradox (mix shifts), survivorship (later levels look easier), right-censoring (recent cohorts look worse on rolling metrics), and segment fishing. Segment on pre-treatment attributes and use experiments, staggered rollouts or matched comparisons for causal claims. (`references/funnels-cohorts-segmentation.md` §5)

### 12. Data-informed: triangulate *what* with *why*
Telemetry says what and where; playtests, persona runs, reviews, support tickets and micro-surveys say why. Score competing hypotheses against both before intervening, and close the loop on both after. (`references/telemetry-for-design.md` §7)

### Rules of thumb (starting points — verify per game)

| Topic | Starting point | Source / status |
|---|---|---|
| D7/D1 | < ~0.30 first-session problem; 0.30–0.44 weak days 2–5 | Practitioner consensus (see volatile section of `references/kpi-dictionary.md`) |
| Retention screen for marketed titles | ~25–30% D1, 10–15% D7, 3–6% D30 | Practitioner heuristic, sourced in `references/kpi-dictionary.md` §12 |
| Time to fun | Aha moment well under ~90 s | Practitioner warning, sourced |
| Sample for D1 ±2 pp | ≈ 2,300 installs | Binomial maths |
| A/B on D7 15% → 16% | ≈ 20,600 per arm (α 0.05, power 0.8; `ab_test.py size --baseline 0.15 --mde 0.01` prints 20,557) | Formula, `references/experimentation.md` §4 |
| SRM alarm | chi-square p < 0.001 | Common practice |
| Level spike | churn after level ≥ 2× rolling baseline, or win rate ~25 pts below neighbours (non-boss) | Studio heuristic |
| Soft-currency sink/source | flag < 0.7 or > 1.05 (configurable) | Studio heuristic |
| LTV extrapolation | ≤ 3–6× beyond the last observed day without tail correction | Studio rule |
| Holdout share | 1–5% global, 5–20% for CRM campaigns | Common practice |
| Taxonomy size | ~15–30 custom events, ≤ 8 common params, ≤ 25 user properties | Platform limits + studio practice |

## Decision procedures

### A. Instrument a new game (slice tier)
1. List the contract's questions: FTUE aha target, level difficulty targets, economy targets, monetization placements, live events, `kill_criteria`.
2. Draft the taxonomy: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/event_taxonomy.py generate --contract .gamestudio/contract.json --out .gamestudio/analytics/<slug>.taxonomy.json`.
3. Edit: triggers precise enough to test, near-miss params on `level_end`, economy `source`/`item_name` = economy-model node ids, enums from contract ids, `kpis[]` keys from the KPI dictionary.
4. Validate: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py validate .gamestudio/analytics/<slug>.taxonomy.json`; set `contract.analytics.taxonomy_ref`.
5. Generate stubs: `event_taxonomy.py stubs --taxonomy <file> --engine godot|unity --out <dir>`; implement the wrapper (single facade, consent gate, recording adapter for tests).
6. Add an `analytics` feature to `features.json`; the deterministic playthrough asserts the P0 event sequence; run the event QA checklist (`references/event-taxonomy-design.md` §14).
7. Privacy pass with the `compliance-officer` agent: no PII, consent per storefront, Data safety / privacy labels updated.

### B. Diagnose a KPI drop
1. Rule out artefacts: data delay, SDK/build changes, event-volume monitors, test users, release and config annotations.
2. Localise with the driver tree; split by platform, geo tier, channel and build; decompose mix vs within-segment change.
3. Cohort table: row, column or diagonal?
4. Drill into funnels (FTUE, level, store), session-end reasons and economy health for the affected cohorts or ages.
5. Write 2–4 competing hypotheses; pull qualitative evidence; score them.
6. Intervene through remote config or a build change, as an experiment where traffic allows; record the decision with `gs.py progress`.

### C. Find and fix difficulty spikes
1. Export counts `level,attempts,wins,churned` for mature users; run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/difficulty_curve.py analyze --data levels.csv --json`. `attempts` is the denominator for both the win and churn rates (put starters there for churn-after-level), the script flags a win-rate dip of 0.15 or more and churn at 2× the neighbour median or more, ignores levels under 30 attempts and exits 1 when it flags anything; it is a shortlist, not the full spike rule (`references/funnels-cohorts-segmentation.md` §2.2–2.3).
2. Compare with `level-spec.difficulty_target` and the role in `teach`; flag churn ≥ 2× baseline.
3. Inspect fail distance, near-miss, quit and assist rates; check offers shown at the level (ethics).
4. Tune by the smallest knob (moves, spawn odds) via remote config, or reorder/redesign; recalibrate the bot-to-human mapping.
5. Verify on the next cohort; update the level spec and `progress.md`.

### D. Size, run and read an A/B test
1. Hypothesis template filled; primary, guardrails and decision rule written (`references/experimentation.md` §2–3).
2. Size: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ab_test.py size --baseline 0.15 --mde 0.01 --power 0.8 --two-sided`. `--mde` is an **absolute** difference in the metric (0.01 = +1 percentage point, so D7 15% → 16%, a 6.7% relative lift), never a relative lift; the output gives `n_per_arm` (20,557 here) and `n_total`. Then compute duration including metric maturation, whole weeks.
3. Assign by player id with a per-experiment salt; log `experiment_exposure`; run an A/A check on new infrastructure.
4. During the run, look only at health: SRM (`analytics_calc.py srm --counts A,B`), crashes, guardrail harm. Use `ab_test.py sequential` boundaries if interim looks are planned.
5. Read out with the template; ship, iterate or kill per the pre-written rule; keep a holdback for long-horizon effects.

### E. Project LTV and decide on UA scaling
1. Pool mature cohort retention per platform/channel: `analytics_calc.py cohort --csv activity.csv`.
2. Fit and validate: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/retention_ltv.py fit --points "1:0.42,7:0.18,30:0.07" --model power` (rates are ratios, 0.42 = 42%, days ≥ 1, at least two points; `--model` is `power` or `exp`). Holdout check: run `fit` on the D1–D14 points only and compare its projected D30 with the observed D30.
3. LTV with age-varying net ARPDAU; apply a hybrid tail beyond ~3× the last observed day. `retention_ltv.py ltv` itself assumes a flat ARPDAU and a smooth power or exponential tail, with no hybrid tail or interval, so do those two adjustments by hand from the method in `references/ltv-retention-modeling.md` §4–5.
4. ROAS and payback: `analytics_calc.py payback --points ... --arpdau A --cpi C --net-share S --horizon 365`.
5. Set D7 ROAS targets from matured multipliers (target = margin / multiplier); scale only channels whose matured curves beat the target; re-derive monthly.

### F. Soft-launch go / iterate / kill
1. Stage the soft launch: technical → retention → monetization → scale (`references/ltv-retention-modeling.md` §8).
2. Gate each stage on `contract.analytics.kpi_targets` with confidence intervals and trend across builds, read per channel and platform.
3. D1 fine but D7/D1 low → iterate first-week loop and difficulty; monetization low with good retention → iterate offers, placements and sinks; D1 low after FTUE fixes with no upward trend → apply `contract.kill_criteria`.
4. Human checkpoint: the principal and the user sign off on go/kill.

### G. Economy health check (weekly in soft launch and live)
1. Aggregate flows by currency and node; take balance snapshots.
2. `analytics_calc.py economy --csv flows.csv --dau-days N --balances balances.csv --max-hoard-days <targets.max_soft_currency_hoard_days> --broke-below "coins:<cheapest sink>"`.
3. Compare with `economy_sim.py` predictions; drift > ~20% on a major node → fix the model or find the exploit.
4. Propose remedies (new sinks, faucet changes, event payout caps) and test them via `balance` / `arcosian:systems-designer`.

### H. Weekly analytics review
Run the template in `references/telemetry-for-design.md` §10: annotations first, scorecard vs targets, only moved metrics, experiments, qualitative themes, data quality, decisions with owners, next week's hypotheses.

### Which analysis answers which question

| Question | Method | Reference |
|---|---|---|
| "Where do new players leave?" | FTUE funnel + level funnel + first-playable time | funnels §1–2 |
| "Why did D7 drop this month?" | Driver tree + cohort table + session-end reasons | kpi §9, funnels §4, telemetry §4 |
| "Is level 23 too hard?" | Level metrics vs role band + near-miss | funnels §2, telemetry §2 |
| "Is our soft currency inflating?" | Sink/source, hoard days, broke share, sim drift | telemetry §3 |
| "How many players do we need for this test?" | Power formula / `ab_test.py size` | experimentation §4 |
| "Can we afford a $2.50 CPI?" | Retention fit → LTV → payback | ltv §5–7 |
| "Did the event make money?" | Uplift vs baseline/holdout minus cannibalisation | telemetry §5 |
| "Who are our players?" | Clustering, RFM, payer tiers | funnels §6–8 |
| "Who is about to churn?" | Churn model with out-of-time validation + holdout interventions | funnels §9 |

## Mobile specifics

- **Interrupted, short sessions.** Phones background constantly; define sessions by SDK inactivity timeout, log `app_paused` inside levels, and treat end-of-session events as best-effort (send summaries at next launch). Offline play produces late events: day-level KPIs for recent days are provisional for ~72 h.
- **Platform split.** iOS and Android differ in retention, ARPDAU, CPI and attribution; set targets and fit curves per platform, never pooled.
- **Attribution limits.** iOS user-level attribution requires the App Tracking Transparency opt-in; otherwise measurement relies on AdAttributionKit/SKAdNetwork aggregated postbacks with coarse conversion values, so the taxonomy must expose strong early signals (tutorial complete, D1 return, first purchase) that the MMP can map into postback windows. Android remains GAID plus consent after Privacy Sandbox's retirement (volatile; see `references/event-taxonomy-design.md` §16).
- **Store fees vary by storefront and programme.** Net revenue share is a per-storefront config value (`config.storefronts`), not a constant; recompute payback when terms change.
- **Many builds live at once.** Players update slowly; segment every KPI by `build`, use staged rollouts (Play staged rollout, App Store phased release) and compare builds on matched cohorts.
- **Device tiers.** Low-end devices churn from load times, heat and frame drops; segment by `device_tier` and keep `perf_sample` sampled and cheap.
- **Permissions shape reach.** Push permission (iOS prompt; Android 13+ runtime permission) gates CRM; log the prompt result and its context, and test prompt timing.
- **Ad revenue is impression-level estimates.** Forward mediation ILRD as `ad_impression`, reconcile monthly, and remember geo mix drives eCPM.
- **Battery and data.** Batch events; never flush per event; sample high-volume telemetry; never sample economy or purchase events.
- **Privacy labels must match reality.** App Store privacy labels and Play Data safety forms are checked against what SDKs send; every taxonomy change that adds a data type triggers a compliance review.

## Anti-patterns

| Anti-pattern | How to detect | Fix |
|---|---|---|
| Vanity dashboards | Tiles nobody can tie to a decision; DAU celebrated while D7 falls | Driver tree; every tile has a target and an owner |
| Click-logging everything | Hundreds of event names; near platform limits; nobody queries most | Question-first taxonomy; prune quarterly |
| Free-text parameters | High-cardinality values, PII risk, unusable reports | Ids and enums; free text never in analytics |
| Repurposed event names | Discontinuities in time series after a release | Versioning rules; new name + deprecation |
| Mixed retention definitions | Team quotes D7 numbers that differ by 2× | Definition tags; classic calendar UTC default |
| Averaging immature cohorts | Dn "declining" every week | Maturity filter |
| Aggregate-only analysis | Changes explained by mix shifts, not product | Cohort tables; mix vs within decomposition |
| Peeking and stopping early | Many "wins" that vanish after shipping | Fixed horizon or sequential boundaries |
| Ignoring SRM | Lopsided arms read as results | SRM check gates every readout |
| Winning on a secondary metric | Primary flat, "but engagement went up" | Pre-registered primary and decision rule |
| Selection-biased feature claims | "Users of X retain 3× better" | Experiments, staggered rollout, matching |
| Gross ROAS for payback | Payback looks 20–30% sooner than cash reality | Net basis per storefront |
| Infinite LTV tails | LTV grows with horizon; projections from 14 days of data | Fixed horizon, hybrid tail, intervals |
| Metrics over players | Difficulty or offers tuned to monetize frustration | Guardrails, ethics review (`monetization`, `legal-ethics`), doctrine |
| No qualitative loop | Repeated fixes that do not move metrics | Triangulation matrix before intervening |

## Using the ontology

| Analytics concept | Where it lives | Notes |
|---|---|---|
| KPI targets | `contract.analytics.kpi_targets` {`d1`, `d7`, `d30`, `session_len_sec`, `sessions_per_day`, `arpdau_usd`, `payer_conversion`} | Classic calendar-day retention; gross ARPDAU unless labelled |
| Taxonomy | `contract.analytics.taxonomy_ref` → `.gamestudio/analytics/*.taxonomy.json` (`event-taxonomy.schema.json`) | Events with `category`, `trigger`, typed `params`, `kpis`, `sampling` |
| FTUE funnel steps | `contract.ftue.steps[].id`, `aha_seconds_target` | Become `tutorial_step.step_id` enum values |
| Economy telemetry | `economy-model.schema.json` → `resources[].id`, `nodes[].id`, `targets` | Event `source`/`item_name` = node ids; hoard target from `targets.max_soft_currency_hoard_days` |
| Level telemetry | `level-spec.schema.json` → `level_id`, `difficulty_target` {`win_rate`, `attempts_p50`}, `solver.bot_win_rate`, `teach` | Spike rules depend on the role |
| Ad pacing guardrails | `contract.monetization.ads.interstitial` {`min_interval_sec`, `first_after_sec`} | Compliance tiles |
| Live events | `contract.liveops.events` | `liveops_event_*` events and post-mortems |
| Pre-launch proxies | `playtest-report.schema.json` → `metrics` | Bot/persona time-to-first-reward, win rate, session length |
| Analytics features | `features.json` → `area: "analytics"`, gate evidence in `.gamestudio/evidence/<ID>/` | Event assertions live in the playthrough gate |
| Kill criteria | `contract.kill_criteria`, `concept.schema.json` → `kill_criteria` | Behavioural, measurable, time-boxed |
| Stage | `config.tier` (`prototype` → `live`) | Determines which telemetry matters (`references/telemetry-for-design.md` §11) |
| Storefronts and revenue | `config.storefronts`, `config.revenue` | Net share and payment rules per storefront |
| Retention hooks in comparables | `deconstruction.schema.json` → `retention_hooks`, `liveops` | Benchmarks for hypotheses |
| Reports | `.gamestudio/reports/` (experiment readouts, weekly reviews, event post-mortems) | Markdown, linked from `progress.md` |

**Tools.**

| Task | Command |
|---|---|
| Derived KPIs from daily aggregates | `python3 ${CLAUDE_PLUGIN_ROOT}/skills/player-analytics/scripts/analytics_calc.py kpis --dau 10000 --mau 52000 --iap-revenue 900 --ad-revenue 380 --payers 180` |
| Interval for any rate | `analytics_calc.py ci --success 400 --n 1000` |
| Funnel and biggest leak | `analytics_calc.py funnel --steps "first_open:10000,tutorial_begin:9200,tutorial_complete:7100"` |
| Retention triangle | `analytics_calc.py cohort --csv activity.csv --days 1,3,7,14,30 [--mode rolling]` |
| Economy health | `analytics_calc.py economy --csv flows.csv --dau-days 70000 --balances balances.csv --max-hoard-days 7` |
| RFM segments | `analytics_calc.py rfm --csv rfm.csv --out scores.csv` |
| ROAS curve and payback | `analytics_calc.py payback --points "1:0.40,7:0.18,30:0.08" --arpdau 0.12 --cpi 2.50 [--net-share 0.8]` |
| Sample-ratio mismatch | `analytics_calc.py srm --counts 10000,10600` (exit 1 on mismatch) |
| A/B sizing and analysis | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ab_test.py size --baseline 0.15 --mde 0.01` (`--mde` is an absolute difference, so this is 15% → 16%; also `analyze`, `mean`, `sequential [--method obf\|pocock]`; `--json` on all) |
| Retention fit and LTV | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/retention_ltv.py fit --points "1:0.42,7:0.18,30:0.07"` and `retention_ltv.py ltv --points "1:0.42,7:0.18,30:0.07" --arpdau 0.11 --horizon 365` (power or exp curve by unweighted log-space least squares, rates as ratios; the `ltv` run prints 15.842 lifetime days and LTV 1.7426) |
| Level telemetry | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/difficulty_curve.py analyze --data levels.csv --json` |
| Economy simulation | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/economy_sim.py --model .gamestudio/economy/model.json --runs 200 --json` |
| Taxonomy draft and stubs | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/event_taxonomy.py generate --contract .gamestudio/contract.json --out <file>` and `event_taxonomy.py stubs --taxonomy <file> --engine godot --out <dir>` |
| Validate, log, search | `gs.py validate PATH` · `gs.py progress "..."` · `gs.py kb "cohort" --skill player-analytics` |

`analytics_calc.py` is stdlib-only (Python 3.9+), supports `--json`, exits 0 ok / 1 check failed / 2 input error, and passes `--selftest`. Live vendor access (Firebase Remote Config and Crashlytics via the official Firebase MCP, Adjust, RevenueCat) is wired by the `arcosian-commerce` adapter plugin; raw-event analysis goes through the Firebase BigQuery export (SQL skeletons in `references/funnels-cohorts-segmentation.md` §10).

## Reference library

| File | What it contains | Read it when |
|---|---|---|
| `references/kpi-dictionary.md` | Measurement conventions; engagement, retention (classic/rolling/bracket), churn, reactivation, growth accounting; monetization and ad KPIs; LTV variants; UA KPIs (CPI = CPM/IPM, ROAS, payback, K-factor); tech KPIs; driver tree; worked week; KPI keys; sourced benchmark ranges | Defining targets, building dashboards, settling metric disputes, sanity-checking numbers |
| `references/event-taxonomy-design.md` | Principles; naming; envelope; full mobile event catalogue; parameter rules; user properties; economy and monetization events; versioning; privacy and consent; wrapper architecture; Firebase/GameAnalytics mapping; schema and `event_taxonomy.py` workflow; event QA checklist; worked example | Instrumenting a game, reviewing a taxonomy, adding events, privacy reviews |
| `references/funnels-cohorts-segmentation.md` | Step funnels; level funnels, spike detection and traps; progression velocity and runway; cohort triangles and reading; segmentation rules and mix decomposition; payer tiers and concentration; clustering; RFM; churn prediction; BigQuery SQL skeletons | Diagnosing drop-offs, difficulty spikes, cohort changes; building segments or churn models |
| `references/experimentation.md` | When to test; hypothesis template; metric roles and OEC; power, sample size, MDE, duration; assignment and exposure; A/A and SRM; novelty; peeking and sequential designs; CUPED and variance reduction; multiple comparisons; holdouts; bandits; remote config; game pitfalls; readout template; tool usage | Planning, monitoring or reading any experiment; designing remote config |
| `references/ltv-retention-modeling.md` | Retention vs survival; power, exponential, Weibull, sBG; fitting and holdout validation; tail and horizon effects; LTV from constant and age-varying ARPDAU; projection methods and multipliers; ROAS, break-even and payback; soft-launch staging, noise and go/kill; modelling mistakes | Projecting LTV, setting ROAS targets, deciding on UA scale, reading soft-launch results |
| `references/telemetry-for-design.md` | Data-informed loop; difficulty tuning bands, signals and knobs; DDA monitoring; economy health metrics, worked example, sim drift and remedies; session-end reasons; live-event metrics and post-mortem; feature impact methods; qual+quant triangulation; data-quality monitors; dashboard set; weekly review template; stage focus | Tuning levels or economies from data, evaluating events and features, running the weekly review |

## Related skills

- `game-ontology` — schemas and vocabulary the taxonomy, KPI targets and economy telemetry plug into.
- `design-theory` — design intent and loop structure that analytics hypotheses come from.
- `player-psychology` — motivation and bias models behind behavioural patterns seen in data.
- `economy-design` — currency architecture and simulation that economy telemetry validates.
- `progression-difficulty` — difficulty curves and DDA that level telemetry tunes.
- `level-design` — level roles, solvers and bots recalibrated with live data.
- `monetization` — ethical offers, ads and passes measured by monetization KPIs and tests.
- `liveops` — events, segmentation and CRM evaluated with uplift and holdouts.
- `marketing-ua` — CPI, IPM, creatives and ROAS-driven acquisition.
- `market-intel` — genre benchmarks and comparables for targets.
- `mobile-ux` — FTUE and flows that funnels diagnose.
- `mobile-performance` — tech KPIs, device tiers and perf telemetry.
- `qa-testing` — event assertions in playthroughs and pre-launch proxies.
- `multiplayer-backend` — server authority for economy and purchase events, remote config hosting.
- `store-release` — staged rollouts, store fees, privacy labels and Data safety.
- `legal-ethics` — privacy, consent, children's data and personalised pricing.
- `genre-playbooks` — genre-specific KPI expectations and loops.
- `production` — milestones, soft-launch plans and kill decisions.
