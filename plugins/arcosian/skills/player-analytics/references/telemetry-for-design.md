# Telemetry for Design Decisions

How designers and the studio's agents use behaviour data to tune a game rather than just report on it: tuning difficulty from level telemetry, checking economy health (source/sink ratios, hoarding, broke rates, inflation, sim-vs-live drift), finding why sessions end, judging live events and features, and triangulating numbers with qualitative evidence so the team learns *why* as well as *what*. It closes with data-quality monitoring, the standard dashboard set and a ready-to-run weekly analytics review template. The doctrine applies throughout: **data-informed, not data-driven** — every analysis starts with a design hypothesis, and telemetry confirms, refutes or sharpens it; numbers never override the player experience the game is meant to create.

## Contents

1. The data-informed design loop
2. Tuning difficulty with telemetry
3. Economy health
4. Session-end reasons
5. Live-event performance
6. Feature adoption and impact
7. Qualitative + quantitative triangulation
8. Data quality and anomaly monitoring
9. The dashboard set
10. Weekly analytics review template
11. What to watch at each stage
12. Mapping to studio artefacts and tools

---

## 1. The data-informed design loop

```
Design intent (contract pillars, target aesthetics, kpi_targets)
   └─► Hypothesis ("players quit level 6 because the blocker pattern is unreadable")
         └─► Instrumentation (events + params that can confirm or refute it)
               └─► Observation (funnels, level metrics, economy flows)
                     └─► Triangulation (playtest video, reviews, survey, persona sim)
                           └─► Intervention (remote-config tweak or build change, ideally as an experiment)
                                 └─► Decision + record (progress.md, experiment readout, contract update)
```

**Question bank by design area** (each maps to sections below):

| Area | Questions telemetry can answer | Questions it cannot answer alone |
|---|---|---|
| Difficulty | Which levels have outlier win rates, attempts and churn? How close are wins and losses? | Is the level *fun*? Is the failure perceived as fair? |
| Economy | Are currencies accumulating or draining? Which faucets and sinks dominate? | Do rewards *feel* generous? Is the shop understood? |
| Sessions | When and after what do sessions end? Are sessions the designed length? | Was the stop satisfying or frustrated? |
| Meta / features | Who uses a feature, how often, and do users retain better? | Why non-users ignore it; whether it is understood |
| Live-ops | Participation, completion, uplift, cannibalisation | Whether players enjoyed the theme and rewards |
| Monetization | Offer funnels, conversion timing, ad opt-in | Perceived fairness and value |

Anything in the right column needs the qualitative sources in section 7.

---

## 2. Tuning difficulty with telemetry

### 2.1 Target bands by level role

Starting points used by the studio for casual and puzzle levels; calibrate per game (see `progression-difficulty` for curve design and `level-design` for level roles). The level spec's `teach` field (`teach|test|twist|reward`) says which band applies, and `difficulty_target` {`win_rate`, `attempts_p50`} records the chosen target.

| Role (`teach`) | Win rate per attempt (starting band) | Attempts p50 | Churn after level vs baseline |
|---|---|---|---|
| `teach` | ≥ 90% | 1 | ≤ 1.2× |
| `reward` | ≥ 90% | 1 | ≤ 1.0× |
| `test` | 55–80% | 1–2 | ≤ 1.5× |
| `twist` | 50–75% | 1–2 | ≤ 1.5× |
| Boss / hard (a `test` flagged hard) | 30–50% | 2–4 | ≤ 2.0×, with high near-miss share |

Inside the FTUE window (first session, roughly the first 10–15 levels in a puzzle game), keep everything in the `teach`/`reward` bands; an early spike costs far more players than the same spike at level 80.

### 2.2 Signals beyond win rate

| Signal | Computation | Reading |
|---|---|---|
| Near-win share | wins with ≤ 2 moves (or ≤ 10% time) left / wins | High = tense finishes; good for hard levels, exhausting if every level is like this |
| Fail distance | distribution of `targets_left` on fails | Mostly 1–2 left = fair and close (tune by a move or two); mostly many left = unreadable or unwinnable for most players |
| Quit-before-end share | `level_end{reason=quit}` / attempts | Frustration or interruption; check time in level and whether quits follow fail streaks |
| Assist dependence | attempts with boosters/continues/revives / attempts, and win rate without assists | A level "passes" only because players spend |
| Retry latency | seconds from fail to next `level_start` on the same level | Short = motivated retry; long gaps or session end = discouragement |
| Fail streak exit | P(session ends) after 1, 2, 3, 4 consecutive fails | Where patience runs out; informs DDA trigger points |
| Time per attempt | median `duration_sec` | Long levels make failure costlier; consider checkpoints or shorter layouts |

### 2.3 Procedure: bots → soft launch → live

1. **Pre-launch:** run bots on every level (`match3_sim.py`, `puzzle_solver.py`, engine bot runs) and record `solver.bot_win_rate` in the level spec. Bots estimate relative difficulty, not human win rates.
2. **First live data:** for each level, fit the relationship between bot win rate and human first-try win rate (a simple linear or logistic mapping over all levels). Levels far from the fitted line are where bots misjudge humans (often readability, not solvability).
3. **Recalibrate:** predict human win rates for unreleased levels from the mapping; tune them before release.
4. **Live tuning:** adjust move counts, goals or spawn tables through remote config; prefer changes of one or two moves at a time and verify on the next cohort.
5. **Re-run analysis weekly** with `difficulty_curve.py analyze` on `level,attempts,wins,churned` exports and compare to the target curve (`difficulty_curve.py generate`).

### 2.4 Symptom → knob

| Symptom | First knobs to try | Avoid |
|---|---|---|
| Spike with high fail distance near 1 target | +1–2 moves; slightly easier spawn odds | Redesigning the whole level |
| Spike with high fail distance far from goal | Swap with a later level; add a teaching level before it; improve readability (contrast, telegraphing) | Only adding moves (hides a comprehension problem) |
| Many quits mid-level | Shorter level; checkpoint; pause/resume reliability | Penalising quits |
| High assist dependence | Reduce base difficulty; make boosters earnable in play | Removing boosters abruptly |
| Plateau of identical win rates for 20 levels | Sawtooth pacing: insert hard and reward levels | Uniform difficulty (boredom) |

### 2.5 Dynamic difficulty adjustment (DDA) monitoring

If the contract enables DDA (`contract.progression.difficulty.dda`), log `dda_step` on `level_start` and monitor: share of attempts with assists active, win rate by `dda_step`, retention of players who received assists vs comparable players who did not (selection-biased — prefer an experiment), and whether competitive or leaderboard modes are excluded. Silent DDA must never interact with purchases (no "harder when you have money" logic); the doctrine's ethics rules apply.

---

## 3. Economy health

The live economy is checked against the economy model (`economy-model.schema.json`) and its targets (`targets.max_soft_currency_hoard_days`, `days_to_complete_content`, `payer_conversion`).

### 3.1 Metrics

| Metric | Formula | Healthy pattern |
|---|---|---|
| **Sink/source ratio** | currency spent / currency granted over a window (per currency) | Near but below 1.0 for soft currency in steady state (players accumulate slowly for big goals); sustained values well below ~0.7 mean accumulation; above ~1.05 means balances drain. Bands are configurable starting points |
| Net flow per DAU-day | (granted − spent) / Σ DAU over the window | Small positive for soft currency |
| Balance percentiles by player age | p10/p50/p90/p99 of balance at day 1, 7, 30 | Rising slowly with age; no runaway p90 |
| **Hoard days** | balance / average daily spend per player | Within `targets.max_soft_currency_hoard_days`; very high = nothing worth buying |
| **Broke share** | players with balance below the cheapest meaningful sink / players | Low but not zero (some scarcity creates goals); high = frustration or paywall |
| Earn rate | currency granted per minute of play, by player age | Should match the economy model; drift reveals exploits or unbalanced events |
| Price-to-balance ratio | cost of the next meaningful purchase / median balance at that progress | Around one or a few sessions of earning for regular goals; much higher = wall |
| Faucet concentration | share of inflow from the top source | Diversified soft-currency faucets; IAP dominance is normal for hard currency |
| Currency velocity | spend per day / average balance | Falling velocity = hoarding |
| Hard→soft conversion | hard currency spent on soft currency / total hard spend | High = soft-currency scarcity driving purchases; watch for paywalls |
| Event currency leftover | event currency unspent at event end / granted | High = rewards not attractive or prices too high |

### 3.2 Worked example

One week, 70,000 DAU-days, events aggregated by node:

`python3 ${CLAUDE_PLUGIN_ROOT}/skills/player-analytics/scripts/analytics_calc.py economy --csv flows.csv --dau-days 70000 --balances balances.csv --max-hoard-days 7 --broke-below "coins:40,gems:5"`

| Currency | Source/DAU-day | Sink/DAU-day | Sink/source | Balance p50 / p90 | Hoard days p50 / p90 | Broke share | Flags |
|---|---|---|---|---|---|---|---|
| coins | 15.0 | 10.2 | 0.68 | 91 / 340 | 8.9 / 33 | 20% below 40 | Accumulating; median hoard 8.9 days > target 7 |
| gems | 0.93 | 0.90 | 0.97 | 6 / 30 | 6.7 / 33 | 41% below 5 | In band; IAP supplies 65% of inflow (expected) |

Top coin sources: level wins 74%, rewarded "double coins" 14%, daily chest 11%. Top sinks: meta builds 53%, boosters 41%, continues 6%.

Reading and actions:
- Coins accumulate (0.68) while 20% of players are nearly broke: the distribution is wide — engaged players hoard, casual players run dry. A single global price change will hurt one group. Options: add aspirational sinks that scale with balance (cosmetic upgrades, prestige builds) for hoarders; keep early meta costs affordable for the bottom quartile.
- 41% of players hold fewer than 5 gems: if a continue costs 9 gems, most players face an IAP or ad wall at the first gem prompt. Check whether that prompt coincides with difficulty spikes (an ethics flag) and whether earned-gem faucets reach casual players.
- Next step: run `economy_sim.py` with the live parameters and compare predicted vs observed balances by day; adjust the model (section 3.3), then test one change via remote config.

### 3.3 Sim-vs-live drift

1. Export live per-node daily totals per DAU and balance percentiles by player age.
2. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/economy_sim.py --model .gamestudio/economy/model.json --runs 200 --json` with archetype shares matched to live segment shares.
3. Compare per node: |live − sim| / sim. Over ~20% on a major node means the model is wrong (archetypes, probabilities, triggers) or the game has a bug/exploit.
4. Fix the model first, then use it to evaluate proposed changes before live testing.

### 3.4 Symptoms and remedies

| Symptom | Likely cause | Remedies (test them) |
|---|---|---|
| Hoarding (high hoard days, falling velocity) | Nothing worth buying; prices flat while income grows | New sinks with escalating cost, limited-time items, upgrade tiers, collections; avoid confiscation |
| Mass brokeness early | Faucets too small or slow; sinks required for core play | Larger early grants, guaranteed income per session, cheaper essentials |
| Inflation after an event | Event rewards injected large amounts | Event currencies that expire into fixed rewards; cap event payouts; rebalance next event |
| Hard currency devalued | Too many free gems from events/login | Rebalance free gem faucets; protect IAP value perception |
| Dominant faucet exploited | Farming a replayable level or ad reward | Daily caps, diminishing returns, server validation |
| Sink unused | Overpriced or unclear value | Price test, preview the benefit, tutorialise the sink |

---

## 4. Session-end reasons

Sessions end for reasons the game can influence (frustration, walls, ads, loading) and reasons it cannot (life interruptions). Classifying them shows which endings are design problems.

### 4.1 Method

1. For each session, take the last gameplay-relevant events before the session's final event (or `session_end_summary.end_context` if implemented).
2. Classify with ordered rules:

| Rule (first match) | Class |
|---|---|
| Crash or `client_error{severity=fatal}` within the last 10 s | `crash` |
| `load_time` started but not finished | `loading` |
| `inter_shown` within the last 15 s | `after_interstitial` |
| `level_end{success=false}` with no further `level_start`, and `offer_shown` (continue/IAP) declined | `fail_offer_declined` |
| `level_end{success=false}` with no further `level_start` | `after_fail` |
| Lives/energy depleted event | `out_of_energy` |
| `app_paused` inside a level and no resume | `interrupted_in_level` |
| Daily tasks or all available goals complete | `goals_complete` |
| `level_end{success=true}` then menu idle | `natural_stop` |
| Otherwise | `menu_idle` |

3. Compute the distribution per segment and player age; compare against the previous build.

### 4.2 Reading the distribution

| Class share rising | Interpretation | Action |
|---|---|---|
| `after_fail`, `fail_offer_declined` | Frustration endings; difficulty or offer pressure | Section 2 tuning; review offer frequency on fails |
| `out_of_energy` | Energy gate is the binding stop | Fine if sessions reach designed length first; otherwise adjust caps or refill |
| `after_interstitial` | Interstitials end sessions | Increase `first_after_sec` and `min_interval_sec`; move interstitials to natural breaks |
| `loading`, `crash` | Technical churn | Performance and stability work (`mobile-performance`, `qa-testing`) |
| `interrupted_in_level` | Mobile interruption; risk of lost progress | Robust pause/resume and auto-save (doctrine: mobile-native) |
| `goals_complete`, `natural_stop` | Healthy, designed stops | Good; ensure a reason to return tomorrow (timers, daily goals) |

### 4.3 Final-session analysis for churned players

For players who churned (per the inactivity rule), classify their **last** session separately. If `after_fail` is much more common in final sessions than in all sessions (e.g. 34% vs 18%), failure is a churn trigger; if `after_interstitial` is over-represented, ads are. Combine with level-of-last-session to locate the trigger.

**Rage-quit indicator:** a session ending within 30 s of the third consecutive fail on the same level. Track its rate per level as part of the level dashboard.

---

## 5. Live-event performance

| Metric | Formula |
|---|---|
| Reach | eligible players who saw the event entry point / DAU during the event |
| Participation | players with ≥ 1 event action / eligible DAU |
| Completion funnel | share of participants reaching each milestone; final-reward completion |
| Pace | median points per day vs points needed per day to finish |
| Engagement uplift | DAU, sessions/DAU, minutes/DAU during the event vs baseline (same weekdays in prior weeks) or vs a holdout |
| Revenue uplift | revenue per DAU during the event vs baseline/holdout; split event-specific offers vs base store |
| Cannibalisation | change in base-store revenue and normal-progression rate during the event |
| Post-event dip | DAU and revenue in the week after vs baseline |
| Economy injection | currency granted by the event / normal weekly inflow |
| Segment response | participation and completion by payer tier, engagement cluster, player age |

**Worked example.** A 7-day collection event: eligible DAU 40,000; participation 62%; milestone completion 100% / 71% / 44% / 18% (final); event-offer revenue $2,900 while base-store revenue fell from $8,000 to $7,300 per week vs baseline; DAU +6% during the event, −3% the week after. Net revenue uplift ≈ 2,900 − 700 = $2,200 (+27% vs the $8,000 base); final-milestone completion of 18% is below a typical design target if the final reward is the headline prize — players saw it advertised and most could not reach it. Next event: lower the final threshold or add catch-up mechanics, and check that the 44% → 18% drop is not an economy wall requiring purchases (ethics review).

**Event post-mortem template** (store in `.gamestudio/reports/event-<id>.md`): goal and hypothesis; design (duration, mechanics, rewards, offers); KPIs vs targets (table above); segment response; economy injection; qualitative feedback; what to keep, change, stop; next-event parameters.

---

## 6. Feature adoption and impact

| Metric | Definition |
|---|---|
| Exposure | players who reached the feature's unlock point |
| Adoption | exposed players who used it at least once |
| Frequency | uses per active day among adopters |
| Feature retention | adopters still using it N days after first use |
| Impact | effect on retention/revenue caused by the feature |

**Correlation trap.** "Players who join a guild retain 3× better" is mostly selection (engaged players join guilds). Ways to estimate impact, strongest first:

1. **Randomised experiment** (feature on/off or prominence variants) — `references/experimentation.md`.
2. **Staggered rollout** across geos or time with comparable groups; difference-in-differences on retention and revenue.
3. **Matched comparison**: adopters vs non-adopters matched on pre-adoption engagement, progress, spend and age (propensity score or exact matching on buckets).
4. **Within-player timing**: compare each adopter's behaviour before and after first use (beware of regression to the mean and life-cycle trends).

Report which method produced each impact claim.

---

## 7. Qualitative + quantitative triangulation

### 7.1 Sources

| Source | Strength | Weakness | Studio access |
|---|---|---|---|
| Moderated playtests (think-aloud, video) | Shows *why*: comprehension, emotion, confusion | Small samples; artificial setting | `playtest` process skill; human sessions |
| Persona playtests by agents | Fast, repeatable friction discovery across builds | Not real players; no true emotion | `player-simulator` agent (`playtest-report.schema.json`, `mode: persona`) |
| In-game micro-surveys | Ties attitudes to behaviour via pseudonymous id | Response bias; interrupts play if mistimed | Trigger at natural stops, 1–3 questions, sampled, consented |
| Store reviews and ratings | Unfiltered complaints, by version and country | Skewed to extremes; vocal minority | Theme-coded weekly |
| Support tickets | Concrete bugs, payment and progress-loss issues | Skewed to problems | Tag taxonomy aligned with telemetry areas |
| Community (Discord, Reddit) | Engaged players' views, exploit discovery | Core players over-represented | Weekly digest |
| Interviews with churned players | Rare insight into leaving | Hard to recruit; recall bias | Occasional |

### 7.2 Triangulation procedure

1. **Anomaly in telemetry** (e.g. level 6 churn spike) → write the competing hypotheses (difficulty, readability, a bug, an offer popup).
2. **Pull qualitative evidence for each:** playtest clips of level 6; reviews mentioning "level 6" or the blocker type; support tickets; a persona run focused on the level.
3. **Score hypotheses** in a matrix: which evidence supports or contradicts each.
4. **Choose the intervention** that addresses the best-supported hypothesis; run it as an experiment where possible.
5. **Close the loop:** after the change, check both the metric and the qualitative signal (fewer complaints about level 6).

| Hypothesis | Telemetry | Playtest | Reviews/support | Verdict |
|---|---|---|---|---|
| Too few moves | Fail distance mostly 1–2 targets | Players close but run out | "Impossible without boosters" | Supported |
| Blocker unreadable | Would show far fail distance | Players ignore blocker at first | Few mentions | Weak |
| Bug | No error spike | Not reproduced | No tickets | Rejected |

**Say vs do.** When players say one thing and do another (they complain about ads but rewarded opt-in is high), trust behaviour for *what* happens and words for *how it feels*; both matter for decisions (doctrine: player first).

### 7.3 Micro-survey rules

- One question (plus an optional follow-up), shown after a natural stop (level won, daily goal complete), never mid-level or after a fail streak.
- Sample a small share of eligible players; cap one survey per player per few weeks.
- Use closed scales tied to a hypothesis ("How fair did that level feel?" 1–5), plus optional free text that is never logged to analytics as an event parameter (store separately, scrubbed of PII).

---

## 8. Data quality and anomaly monitoring

| Monitor | Rule of thumb | Typical cause when it fires |
|---|---|---|
| Events per DAU per event name | ±20% vs trailing 4-week same-weekday median | Logging bug in a new build; SDK change; trigger moved |
| New build event mix | Any P0 event missing or > 2× volume on the new build | Instrumentation regression |
| Required-param null rate | > 0.5% | Code path not passing params |
| Unknown enum values | Any | New content ids not added to the taxonomy |
| Duplicates (`session_id` + `event_seq`) | > 0.5% | Retry logic, offline replay |
| Late events | Share arriving > 72 h late rising | Offline play; queue issues — affects day-level KPIs |
| Revenue reconciliation | Analytics vs store/network reports differ > 5% | Missing validation, refunds, FX, sandbox purchases |
| Test-user leakage | `debug_build` events in production views | Filter misconfiguration |
| Bot/cheater share | Implausible speeds or currency gains | Exploits; exclude from KPIs and alert the economy owner |

Annotate every dashboard with releases, config changes, live events, UA changes and outages — most "insights" in week-over-week reviews turn out to be one of these.

---

## 9. The dashboard set

| Dashboard | Audience | Tiles |
|---|---|---|
| Executive | Principal, producer | DAU/MAU, installs (paid/organic), D1/D7/D30 by weekly cohort, net revenue, ARPDAU split, payback projection |
| Product health | Designers | FTUE funnel, level funnel and churn-after-level, session length distribution, session-end reasons, progression velocity |
| Economy | Systems designer | Sink/source per currency, balances by age, hoard days, broke share, top faucets/sinks, sim-vs-live drift |
| Monetization | Monetization designer | Offer funnels, payer conversion by cohort age, ARPPU, first-purchase timing, revenue concentration, rewarded opt-in by placement, interstitial compliance |
| UA | Marketing | CPI, IPM, D7 ROAS by channel/creative/geo, ROAS curves on matured cohorts |
| Tech | Engineers | Crash-free users, ANR, first-playable p90, load times, error codes, perf samples by device tier |
| Live-ops | Live-ops manager | Event participation, milestone funnel, uplift vs baseline, economy injection |
| Experiments | Data analyst | Running tests, SRM status, days to readout, decisions log |

Every tile shows its definition tag (see `references/kpi-dictionary.md` §1) and a comparison (previous period, target from `contract.analytics.kpi_targets`, or confidence band).

---

## 10. Weekly analytics review template

Cadence: weekly, 45–60 minutes, same weekday; owner: `data-analyst`; attendees: principal or producer, game/systems designers, monetization, live-ops. Pre-read sent 24 h before. Output: decisions and owners recorded in `.gamestudio/progress.md` via `gs.py progress` and in the experiment/decision log.

```markdown
# Weekly analytics review — <game> — week <YYYY-Www>
Build(s) live: <versions + rollout %>   Data through: <date, UTC>   Analyst: <name/agent>
Annotations this week: <releases, config changes, events, UA changes, outages>

## 1. Headline (3 bullets max)
- <the one thing that changed most and why we think so>
- <biggest risk>
- <decision needed today>

## 2. Scorecard (vs target and vs last week)
| KPI | This week | Last week | Target | Status |
|---|---|---|---|---|
| Installs (paid / organic) | | | | |
| D1 / D7 / D30 (weekly cohort, classic) | | | contract kpi_targets | |
| DAU, DAU/MAU | | | | |
| Net revenue, ARPDAU (IAP / ads) | | | | |
| Payer conversion D7 (cohort) | | | | |
| Crash-free users, first-playable p90 | | | | |
| CPI, D7 ROAS (if UA live) | | | | |

## 3. Diagnostics (only what moved)
- Driver tree localisation: audience vs ARPDAU; mix vs within-segment (kpi-dictionary §9)
- Funnels: FTUE and level funnel changes; new spikes (levels, metrics, proposed fix)
- Economy: sink/source and hoard/broke changes per currency; sim-vs-live drift
- Session-end reasons: shifts vs last build
- Live event: KPIs vs targets (if running)

## 4. Experiments
| Experiment | Status | SRM | Primary (effect, CI) | Guardrails | Decision / next step |
|---|---|---|---|---|---|

## 5. Qualitative signals
- Reviews/support/community themes (top 3, with counts and versions)
- Playtest/persona findings linked to metrics above

## 6. Data quality
- Monitors fired, fixes in flight, metrics to treat with caution this week

## 7. Decisions and actions
| Decision | Owner | Due | Evidence link |
|---|---|---|---|

## 8. Next week's questions (hypotheses to test)
```

**Rules for the meeting:** start with annotations (rule out calendar and data causes first); discuss only metrics that moved beyond their noise band; every proposed change leaves as an experiment or a recorded decision with a kill/keep criterion; no decision on a segment cut found during the meeting (it becomes next week's hypothesis).

---

## 11. What to watch at each stage

| Stage (`config.tier`) | Telemetry focus | Evidence sources |
|---|---|---|
| `prototype` | None in production; bot and playtest proxies: time to first reward, first-session length, win-rate curves | `playtest-report.schema.json` metrics, bot runs |
| `slice` | Taxonomy implemented and asserted in playthroughs; internal-test dashboards working | Event QA checklist (`references/event-taxonomy-design.md` §14) |
| `soft_launch` | Technical health → D1/D7 → monetization → ROAS (staged); level and FTUE funnels; economy health | Weekly review, experiments, soft-launch readouts (`references/ltv-retention-modeling.md` §8) |
| `global` | Cohort quality by channel/geo, payback, economy drift at scale, live-event performance | Full dashboard set |
| `live` | Long-term retention, content runway, live-ops calendar, holdouts measuring cumulative impact | Global holdout, quarterly segmentation refresh |

---

## 12. Mapping to studio artefacts and tools

| Need | Artefact / tool |
|---|---|
| Level targets and bot estimates | `level-spec.schema.json` → `difficulty_target`, `solver.bot_win_rate`, `teach` |
| Level telemetry analysis | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/difficulty_curve.py analyze --data levels.csv --json` |
| Economy model and targets | `economy-model.schema.json` → `nodes`, `targets`; `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/economy_sim.py --model PATH --runs 200 --json` |
| Live economy health | `python3 ${CLAUDE_PLUGIN_ROOT}/skills/player-analytics/scripts/analytics_calc.py economy --csv flows.csv --dau-days N --balances balances.csv` |
| Pre-launch proxies | `playtest-report.schema.json` → `metrics` (`win_rate`, `avg_session_sec`, `time_to_first_reward_sec`, `softlocks`) |
| KPI targets and kill criteria | `contract.analytics.kpi_targets`, `contract.kill_criteria` |
| Analytics features and gates | `features.json` items with `area: "analytics"`; evidence under `.gamestudio/evidence/<ID>/` |
| Decisions log | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py progress "Weekly review: shipped L6 +2 moves (exp-014), D7 +1.2 pp"` |
| Knowledge lookup | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py kb "hoarding" --skill player-analytics` |
