---
name: operate
description: Post-launch operations for a live mobile game - KPI review with the data analyst, live-ops calendar, A/B tests with ab_test.py, remote config changes, crash triage, store review replies and a weekly cadence. Use when the user says "how is the game doing", "weekly review", "plan an event", "run an A/B test", "triage crashes", "reply to reviews" or "live-ops calendar".
---

# Operate

## When to use
After soft launch or launch, when real player data exists. Load `player-analytics`, `liveops`, `monetization` and `economy-design`. Delegate to `arcosian:data-analyst` (KPIs, cohorts, tests), `arcosian:liveops-manager` (calendar, segmentation, config), `arcosian:monetization-designer` (offers) and `arcosian:critic` (challenge conclusions before acting).

## Inputs
Optional `$ARGUMENTS`: `weekly`, `kpi`, `calendar`, `ab <idea>`, `crashes` or `reviews`. Empty runs the weekly cadence. Data comes from files the user provides (exports, dashboards, CSV, store console numbers); without data say so and do not invent numbers.

## Procedure
1. **Load context.** `gs.py status`, contract `analytics.kpi_targets`, `analytics/` taxonomy, last week's report in `.gamestudio/reports/`.
2. **KPI review.** Ask `arcosian:data-analyst` to compare actuals with targets: D1/D7/D30 retention, session length, sessions per day, ARPDAU, payer conversion, crash-free users, FTUE funnel step drop-off, ad impression per DAU. Rules:
   - Compare cohorts by install week, not blended averages.
   - Report sample sizes and uncertainty; small cohorts get no conclusions.
   - Separate acquisition mix effects from product effects (by channel and country).
   - Fit curves with `retention_ltv.py fit --points "1:...,7:...,30:..."` and project value with `retention_ltv.py ltv --points "..." --arpdau <A>`.
   Write findings, not dashboards: each finding states the metric, the delta, the likely cause, a confidence level and the next action.
3. **Diagnose before prescribing.** Map each problem to the lever: early drop = FTUE or first-session difficulty (`progression-difficulty`); mid drop = content or economy pacing (`balance`); low conversion = offer fit and placement; high churn after a spike = difficulty wall (`difficulty_curve.py analyze --data levels.csv`).
4. **A/B tests.** Only test one hypothesis with a pre-registered primary metric.
   - Size it: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ab_test.py size --baseline <p> --mde <d> --two-sided`. If the sample is not reachable in a sensible time, do not run the test; ship the change behind a flag and watch.
   - Several looks at the data: use `ab_test.py sequential --baseline <p> --mde <d> --looks <K>`; never stop on the first significant peek.
   - Read out: `ab_test.py analyze --a-success X --a-n N --b-success Y --b-n M --json` (rates) or `ab_test.py mean ...` (means such as revenue per user). Check guardrails (retention, crashes, refunds) alongside the primary.
   - Record hypothesis, variants, dates and decision in `.gamestudio/reports/ab-<name>.md`.
5. **Live-ops calendar.** `arcosian:liveops-manager` maintains `.gamestudio/design/liveops-calendar.md`: week, event, content needed, config keys, offers, comms, owner, success metric, rollback. Rules: fixed weekly rhythm so players learn it, one big event per cycle with smaller ones between, content built two cycles ahead, no event without an end-of-event review.
6. **Remote config.** Change values, not code. Each key has default, safe range and owner; roll out to a small percentage first, watch guardrails, then widen. Keep a changelog in the report. Ethical limits from `monetization` apply to any price or odds change (no hidden odds changes, no targeting vulnerable players).
7. **Crash triage.** Rank by crash-free-user impact, not raw count. For each top cluster: version, device/OS, stack, reproduction, owner, fix or mitigation (remote flag off). Hand to `arcosian:gameplay-engineer` or the engine engineer; hotfixes go through `ship` (production submission still needs human approval).
8. **Review replies.** Draft replies for the user to send; never post on their behalf. Be specific, brief, non-defensive, never promise dates, never ask for ratings in exchange for anything. Group reviews into themes for the backlog.
9. **Weekly cadence.**

| Day | Activity |
|---|---|
| Mon | KPI review, decisions, set week's tests and config |
| Tue-Thu | Ship fixes and content, run events |
| Thu | Crash triage, review themes |
| Fri | Calendar check two cycles out, write report, update `contract.kill_criteria` status |

10. **Report.** Append to `.gamestudio/reports/ops-<date>.md` and `gs.py progress "<summary>"`.

## Diagnosis table
| Observation | First hypothesis | First check |
|---|---|---|
| D1 low, D7/D1 ratio healthy | FTUE or first-session promise mismatch | Funnel by FTUE step, store listing vs. real game |
| D1 fine, D7 collapses | No reason to return, content or goal gap | Day-2 to day-7 session content, daily hooks |
| Payers few, ARPPU fine | Offer fit, price ladder, placement | First-purchase moment, offer views vs. buys |
| Revenue up, retention down | Pressure monetization | Guardrail cohorts, review sentiment |
| Crash rate spike after release | New SDK or asset change | Version split, device split, config rollback |

## Worked example: an A/B test decision
Hypothesis: a softer level 12 raises D7. Baseline D7 is read from the last three install-week cohorts; pick a minimum detectable effect the team would actually act on; `ab_test.py size` returns the per-arm sample. If acquisition delivers that sample in about two weeks, run it with crash rate and D1 as guardrails; if it would take months, change the level behind a config flag instead and monitor the level's win rate with `difficulty_curve.py analyze`. State the decision rule before the data arrives.

## Review reply rules
- Do: thank specifically, acknowledge the issue, say what you are checking, point to support for bugs.
- Do not: argue, promise dates, offer rewards for rating changes, share player data, or paste the same text on every review.

## Calendar template
| Week | Event | Content ready by | Config keys | Offers | Comms | Success metric | Rollback |
|---|---|---|---|---|---|---|---|
| W+1 | <name> | W-1 | `event_x_enabled`, `event_x_reward_mult` | <id> | Store post, in-game banner | Participation rate, D7 of participants | Flag off |

Guardrail metrics for every event: crash-free users, session length, refund requests, review sentiment.

## Escalation
Stop the event and roll back config first, then investigate, when: crash-free users drop notably below target, a currency exploit appears, or a payment flow fails. Tell the user immediately; do not wait for the weekly review.

## Principles
- Decide with the smallest sufficient evidence, then watch the result.
- One change at a time when you want to learn; many when you must fix.
- Protect trust: never change odds, prices or progression silently.

## Outputs
Weekly ops report, A/B test records, calendar, config changelog, crash cluster list, drafted review replies, backlog additions in `features.json` (new IDs via `gs.py feature`).

## Quality gates
- Every claim has a number, a sample size and a source file.
- Each test has size calculation, guardrails and a recorded decision.
- Config changes have a rollback value.
- Kill criteria and targets re-checked; a recommendation to stop or pivot is allowed and explicit.
- Nothing posted publicly or sent to players without user approval.

## Failure modes and recovery
| Symptom | Recovery |
|---|---|
| No data supplied | Produce a data request list; do not guess |
| Underpowered test | Stop, increase effect size, or ship behind a flag |
| Metric moved after a config change | Roll back first, analyse second |
| Novelty bump mistaken for retention gain | Compare by cohort age and wait a full cycle |
| Event fatigue | Reduce cadence, increase variety, review reward value |

## Related skills
`player-analytics`, `liveops`, `monetization`, `economy-design`, `progression-difficulty`, `postmortem`.
