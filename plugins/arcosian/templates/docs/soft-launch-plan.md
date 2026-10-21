# Soft-launch plan: [game title]

Revision: [date] | Owner: `producer` with `data-analyst` | Build: [version]

<!-- Soft launch exists to answer: will this game retain, monetize and scale at a cost we can sustain? Set gates BEFORE you see data. Every threshold below is a placeholder labeled "assumption" until you replace it with a benchmark you can cite for your genre and market. -->

## Objectives
1. Validate retention shape (is there a flattening curve?).
2. Validate monetization and ad yield per user.
3. Validate technical stability on the real device mix.
4. Estimate a sustainable acquisition cost.

## Markets and cohorts
| Item | Plan |
|---|---|
| Countries | [chosen for similarity to target and cheap installs; reason] |
| Platforms | [iOS / Android / both] |
| Sample size | [installs needed; compute from the metric variance, see `ab_test.py`] |
| Duration | [weeks; at least through the D7 or D30 window you gate on] |
| Spend cap | [amount, source: budget] |

## KPI gates
<!-- Fill thresholds from cited genre benchmarks; mark each as benchmark or assumption. Use `retention_ltv.py` to turn D1/D7/D30 into a projected LTV. -->
| KPI | Kill below | Iterate between | Scale above | Basis |
|---|---|---|---|---|
| D1 retention | [x%] | [x-y%] | [y%] | [assumption] |
| D7 retention | [..] | [..] | [..] | |
| D30 retention | [..] | [..] | [..] | |
| Session length / count per day | [..] | [..] | [..] | |
| Tutorial completion | [..] | [..] | [..] | |
| ARPDAU | [..] | [..] | [..] | |
| Payer conversion | [..] | [..] | [..] | |
| CPI (blended) | [..] | [..] | [..] | |
| Projected LTV / CPI | [< 1] | [1-x] | [> x] | formula-driven |
| Crash-free sessions | [..] | [..] | [..] | |

## Decision rules
- Scale only if retention AND unit economics both clear; one strong metric is not enough.
- Iterate if retention is acceptable but monetization is weak (or vice versa), with a named hypothesis per change and one change at a time where traffic allows.
- Kill if retention is below the kill line after two iteration cycles.
- Decisions made by [names] on [date]; record the data cut used.

## Experiments queue
| ID | Hypothesis | Variant | Primary metric | Min sample | Result |
|---|---|---|---|---|---|
| [E1] | [..] | [..] | [..] | [..] | [..] |

## Instrumentation checklist
- [ ] Event taxonomy validated (`event_taxonomy.py`); first-session funnel events present
- [ ] Attribution and consent flows tested; tracking permission handled per platform rules
- [ ] Crash reporting and performance monitoring on
- [ ] Remote config and kill switches working
- [ ] Dashboards built before day one

## Cadence
Daily: crashes, install volume, D1 flow. Weekly: cohort review, decision meeting. End: gate review and written recommendation.

## Risks
Small samples mislead; seasonal effects; different-country payment behavior; store featuring skewing cohorts. Note each and its mitigation here: [..]
