---
name: liveops
description: Live-operations craft for mobile games - event taxonomy and design, content calendar, seasons, segmentation, CRM and push, win-back, soft launch gates, remote config, incident handling, economy hotfixes and compensation. Use when asked to plan events, build a live-ops calendar, segment players, run soft launch, ship a hotfix via remote config, or handle a live incident.
when_to_use: Planning or running a game after (or just before) launch.
---

# Live-Ops

## What this skill gives you
- An event taxonomy and a procedure for designing one event: goal, rewards, difficulty, duration, economy impact, measurement.
- A calendar method: layers (daily, weekly, seasonal, special), holidays, content cadence and team capacity.
- Segmentation, personalized offers, push and win-back practice with guardrails.
- A soft-launch playbook with KPI gates, market selection method and a global-launch checklist.
- Operational runbooks: remote-config workflows, live incidents, economy hotfixes and player compensation.

## Core models

### 1. Live-ops is the product after launch
A live game is a service: content, economy and community are continuously adjusted. The unit of work is the event or season, planned on a calendar, built from reusable templates, measured against a stated goal. If every event is bespoke, cadence collapses; if every event is a template reskin, players notice. Mix: template backbone, fresh theme and twist.

### 2. The goal ladder
Every event serves one primary goal: re-engage lapsed players, deepen engagement of core players, convert non-payers, monetize payers (ethically), onboard new players, or build community. Name the goal first; it fixes the metric, the reward shape and the segment.
| Goal | Primary metric | Typical shape |
|---|---|---|
| Re-engage | Reactivation rate, D1 return | Login streak, welcome-back track |
| Deepen | Sessions per DAU, time in mode | Collection or milestone event |
| Convert | First-purchase rate | Offer paired with event need |
| Monetize | ARPDAU, pass attach | Season pass, bundle |
| Onboard | D1/D7 retention of new cohorts | Beginner-only event |
| Community | Participation, social actions | Cooperative or guild goal |

### 3. Layering
Run layers with different periods so the game always has something new but the load stays sane:
- Daily: login rewards, daily quests, rotating shop.
- Weekly: weekly challenge, leaderboard reset, short event.
- Seasonal (several weeks): pass, theme, meta narrative.
- Special: holiday, anniversary, collaboration, big content drop.
Rule: no more than a small number of concurrent competing obligations per player; count "must-do" tasks per day and keep it humane.

### 4. Economy impact is the hidden cost
Every reward is a source in the economy. Before launching an event, estimate injected currency and items per player and per segment, and model inflation with `${CLAUDE_PLUGIN_ROOT}/scripts/economy_sim.py`. Events that give power permanently are different from events that give temporary or cosmetic value; the former need sink planning.

### 5. Measure with holdouts
Events change many things at once. To learn their effect, hold out a segment (or stagger rollout by region) and compare. Without holdouts you only know the event period looked good.

### 6. Operational safety
Everything that can be changed live (rewards, odds, difficulty, prices, schedules) goes behind remote config with validation, staged rollout and a rollback. Every live change has an owner, a reason, an expected effect and a review time.

## Decision procedures

### A. Design an event (checklist)
1. Goal and primary metric (table above); target segment.
2. Fantasy and theme: how it fits the game's narrative and the calendar.
3. Mechanic: reuse a template (collection, milestone ladder, tournament, co-op, limited mode).
4. Duration: long enough for slow players to finish, short enough for urgency; start with a few days to two weeks for most events, weeks for seasons, then tune from data.
5. Difficulty and effort: define expected time per tier for casual, core, and hardcore; completion goals for each (for example, most engaged players finish, casual players reach mid-track).
6. Rewards: free lane and optional paid lane; reward value budgeted in economy terms; exclusive cosmetic anchor.
7. Economy impact: sources injected, sinks offered; simulate.
8. Monetization tie-in (optional, ethical): see `monetization`.
9. Telemetry: event_start, task_progress, reward_claimed, event_complete, purchase tied to event; define before building.
10. Success criteria and kill criteria: what result means repeat, change or retire.
11. Operations: config keys, timezones, localization, support macros, rollback plan.
12. Post-mortem template: results vs goals, learnings, next iteration.

### B. Build the calendar
1. List fixed dates: holidays and cultural moments relevant to your markets, platform events, planned content releases, store featuring windows.
2. Place the seasons (spine), then weekly rhythm, then special events.
3. Check team capacity: designers, artists, QA, localization, support; apply a buffer.
4. Check economy: cumulative reward injection per week against sinks.
5. Check fatigue: count concurrent events and tasks; leave breathing room after big events.
6. Freeze windows: no risky changes before big launches or around holidays when support is thin.
7. Publish internally; keep a change log.

### C. Run a soft launch (summary; details in references)
1. Choose markets that are cheap and similar enough to target markets; plan the tests and thresholds first.
2. Instrument analytics; verify the data before spending on UA.
3. Run iterations: fix retention, then monetization, then scale.
4. Gate decisions on KPI thresholds relative to genre benchmarks and unit economics (LTV vs CPI).
5. Go or no-go with a written rationale; kill early if gates fail.

### D. Handle a live incident
1. Detect: alerts on crash rate, purchase failures, server errors, economy anomalies.
2. Triage severity: data loss and payment errors are top.
3. Contain: feature flags, remote-config kill switches, maintenance mode.
4. Communicate: in-game notice and community channels; honest, short, with next update time.
5. Fix and verify in staging; stage rollout.
6. Compensate fairly (see references).
7. Postmortem within days; add monitoring and tests.

### E. Segment and message
1. Define segments from behavior (lifecycle, engagement, payer state, preferences), not demographics alone.
2. Map each segment to a goal and a message or offer with suppression rules.
3. Respect consent and quiet hours; cap push frequency.
4. Measure incremental effect with holdouts.

## Mobile specifics
- Push notifications and permissions: OS permission prompts (iOS asks at runtime; Android 13 and later also asks); ask after value is shown, with context.
- Local time: schedule events in local time for daily rhythms, and in UTC for competitive end times; communicate both.
- App updates lag: remote config must be backward compatible with older client versions; version-gate features.
- Asset delivery: events needing new assets should ship with content bundles or downloadable content, because store review delays binaries.
- Battery, storage and data: large event downloads should be optional or on wifi.
- Store review: new IAP products or policy-relevant changes may need store review; plan lead time.

## Anti-patterns
| Anti-pattern | Detect | Fix |
|---|---|---|
| Event treadmill with no rest | Every day has FOMO tasks; fatigue in surveys | Count obligations; design off-days |
| Permanent power from limited events | Power creep, balance drift | Cosmetics or convertible rewards; sink planning |
| Reward inflation | Currency balances rise week over week | Simulate; add sinks; adjust rewards |
| Missing holdouts | Event "wins" without causal proof | Randomized holdout or staggered start |
| Client-hardcoded schedule | Needs release to change event | Config-driven schedule with validation |
| Push spam | Opt-out rate up | Frequency caps, relevance, quiet hours |
| Silent hotfixes | Players discover changes by surprise | Patch notes, in-game notice |
| Compensation without rules | Ad hoc gifts create expectations and exploits | Written compensation policy |
| Launching globally unmeasured | No soft launch gates | Gate on KPIs |

## Using the ontology
Events are content units (`game-ontology`) with time windows, rewards and goals; rewards are flows in the resource graph. Model event reward injection with `economy_sim.py`, compute events and funnels with `event_taxonomy.py`, estimate LTV and payback with `retention_ltv.py`, and compute test sizes with `ab_test.py`. Track the calendar and results in `.gamestudio/` through `gs.py`, and use the `operate` command skill for post-launch cycles.

## Reference library
| File | Contains | Read when |
|---|---|---|
| `references/liveops-fundamentals-and-events.md` | Event taxonomy, cadence, layering, event design, economy impact, measurement | Designing or reviewing events |
| `references/calendar-segmentation-crm.md` | Calendar building, seasons, holidays, segments, personalized offers, push, win-back | Planning a quarter, building CRM |
| `references/soft-launch-and-ops.md` | Soft-launch markets (volatile), KPI gates, global launch checklist, remote config, incidents, hotfixes, compensation | Soft launching, operating live |

## Related skills
- `monetization`: pass, offers and ethics around event monetization.
- `economy-design`: sources and sinks, inflation control.
- `player-analytics`: KPI definitions, cohorts, test analysis.
- `player-psychology`: motivation, FOMO ethics, habit.
- `multiplayer-backend`: remote config, push and event servers.
- `marketing-ua`: user acquisition at scale after soft launch.
- `store-release`: store review lead times, release trains.
- `operate`: the user-facing post-launch command skill.
