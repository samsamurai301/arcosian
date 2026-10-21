---
name: production
description: 'Game production codex: phase gates and kill criteria, scoping and MoSCoW, estimation for humans and AI agents, milestones, risk registers, roles and RACI, kanban for games, crunch avoidance, lean GDD, one-pagers, design contract, pitch decks, postmortems. Use when planning a game, cutting scope, estimating, setting milestones, writing a GDD or pitch, running a risk review or postmortem.'
when_to_use: 'Planning, scoping, scheduling, risk-reviewing or documenting a game project, or deciding whether to continue or kill it.'
---

# Production

## What this skill gives you
- A phase model (concept, prototype, vertical slice, production, soft launch, launch, live) with an entry gate and an explicit kill rule for each.
- Scoping tools: the one-page design contract, MoSCoW with a hard Must budget, and estimation methods that work when the "team" is an AI-agent crew plus one human.
- Risk and team process: a risk register format, the recurring top risks for mobile and AI-built games, roles, RACI, a kanban board that fits game work, and crunch-avoidance rules.
- Documentation templates: lean GDD, one-pager, pitch deck outline and three postmortem formats.
- Decision tables for the calls producers actually make: cut or slip, continue or kill, build or buy, human review or automatic.

## Core models
**1. Gates, not dates.** A phase ends when evidence exists, not when a calendar says so. Every gate has three parts: a deliverable you can play or measure, a threshold, and a pre-agreed kill or pivot action if the threshold is missed. Write the kill action before the phase starts, while nobody is emotionally attached.

**2. Fun risk first, then tech risk, then content volume.** Order work by the cost of being wrong. Most expensive unknowns: is the core loop fun (hours to test), can it run on a low-end phone (days), can we make 100x the content (weeks). Never schedule content volume before the first two are answered.

**3. Scope is a budget with a hard Must ceiling.** Budget the Musts at no more than roughly 60% of capacity, Shoulds around 20%, and keep the rest as slack and Coulds. When the Must list alone exceeds capacity, the game is too big: cut a feature, not quality.

**4. Estimates are ranges with a confidence level.** Give best/likely/worst and the assumptions. Use reference-class estimates (how long did the last comparable feature take) before bottom-up estimates. Multiply novel work by a larger buffer than known work. See `references/lifecycle-and-planning.md`.

**5. Throughput over utilisation.** Kanban with WIP limits beats keeping everyone busy. The metric is cycle time of a finished, playable feature, not tasks closed.

**6. Vertical slice as the truth serum.** One representative minute of the final game at final quality (art, audio, UI, perf, monetisation touchpoints) converts guesses into measured per-minute content cost. All later estimates multiply that measured number.

**7. The AI-agent team changes the bottleneck.** Agents make code, asset drafts and docs cheap; they do not make taste, integration, review and device testing cheap. Plan the human checkpoints (style, fun, store submission) as the critical path and let agents fill the gaps between them. Never let agent throughput create content faster than the human can review it.

**8. Postmortems feed the next plan.** A game is not finished until lessons are written down in a form that changes the next gate checklist.

## Decision procedures
**Phase gate review (run at every gate)**
1. State the phase goal and the gate threshold, copied from the contract.
2. Show evidence: a build, telemetry, a playtest summary. No slides without a build.
3. Compare to threshold. Classify: pass, pass with conditions, pivot, kill.
4. For "pass with conditions", list conditions with owners and a date; they become Must items.
5. Update the risk register and the contract. Append the decision to the project log with `gs.py progress` (see below).
6. Human checkpoint: the human owner signs off on taste, fun and any spend increase.

**Cut or slip?** Use this table.
| Situation | Default |
|---|---|
| A Must feature is late, others are on track | Cut the scope of the feature, keep the date |
| Quality below gate on a Must | Slip once, with a smaller scoped fix list, then kill-review |
| Should/Could behind | Cut without discussion |
| Platform/store deadline fixed (event, season) | Cut scope; never cut compliance, crash fixes or the FTUE |
| Fun gate missed | Do not slip: pivot the loop or kill (see kill criteria) |

**Continue or kill?** Ask: (a) did the last gate pass without moving the threshold, (b) is the remaining Must list under capacity, (c) is there a measured reason to believe the next gate will pass, (d) has the risk register's top risk shrunk since the last gate. Two "no" answers means kill-review; three means recommend kill or a full pivot.

**Estimating a feature**
1. Find a comparable finished feature; use its actual (including review and device test), not its estimate.
2. Break the new feature into design, implementation, content, UI, audio, telemetry, QA and review.
3. Give each part a range; add integration at 20-30% of the parts for first-of-kind work (judgement, tune it from your own history).
4. State the confidence and the single biggest unknown; schedule a spike if unknown costs more than a day.

**Planning an AI-agent crew** (details in the reference)
1. Split into lanes that own disjoint files or assets.
2. Put each lane behind a gate: it must pass tests or a visual critique before merge.
3. Schedule human taste checkpoints first; agent work in between.
4. Budget API/asset spend per lane and track it like cash.

**Human or automatic?**
| Decision | Who decides |
|---|---|
| Concept choice, style lock, fun verdict | Human |
| Spend increase, store submission, legal/ethics call | Human |
| Kill recommendation | Producer and critic recommend; human decides |
| Task ordering, lane assignment, refactors inside budget | Agents |
| Gate evidence collection and risk-register upkeep | Agents (producer) |

**Weekly rhythm (small team)**: Monday goal and WIP review; midweek playtest of the latest build; Friday demo, risk-register update, burn-down of the Must list. Skip ceremonies that do not change a decision.

## Worked example: a gate call
A hybrid-casual puzzle prototype reaches the fun gate. Contract threshold: 8 of 10 outside testers start a second session unprompted and median first-session length is over 4 minutes. Evidence: 10 sessions, 6 restarted, median 3 minutes; testers stalled on a confusing booster. Classification: pass-with-conditions is wrong because the threshold is missed on the primary metric and the cause is partly fixable. Call: one bounded iteration (3 working days) on the booster explanation and the first five levels, then retest with 10 fresh testers. If the retest misses again, kill or pivot the loop; do not move the threshold. Log it with `gs.py progress "fun gate: miss 6/10, 1 iteration allowed, retest by Fri"` and add the retest to the Must list.

## Procedure checklist for a new project
1. Draft the one-page design contract (`references/docs-and-postmortems.md`) with pillars, Must/Should/Won't and kill criteria.
2. Pick the lifecycle template and write each gate's threshold into the contract.
3. Seed the risk register with the top risks from `references/risk-team-process.md`; add game-specific ones.
4. Build the vertical-slice plan backwards from the soft-launch date; cap Musts at the budget.
5. Assign roles and a RACI for the human checkpoints; set WIP limits.
6. Schedule the first playtest inside week one.

## Mobile specifics
- Plan device-tier testing (low, mid, high) from the prototype phase, not before release; budget calendar time for store review, signing and provisioning, and keep a buffer for at least one rejection cycle.
- Soft launch is a gate with numeric thresholds (retention, session length, early ARPDAU, crash-free rate); define the kill criteria before you spend on user acquisition.
- Session design (1-5 minutes) shapes scope: content is consumed faster than console content, so the live pipeline cost must be in the plan from the start.
- Store requirements, SDK minimums and policy dates change; treat them as volatile and check them at the start of the release phase.
- Ad networks, analytics, consent and age gates are production tasks with owners, not afterthoughts.

## Anti-patterns
| Anti-pattern | Symptom | Fix |
|---|---|---|
| Design by accretion | Must list grows every week | Contract change requires removing something of equal size |
| Content before fun | Many levels, loop untested | Gate: external players want a second session |
| Hero estimate | Single number, no range | Ranges plus reference class |
| Eternal prototype | No vertical slice by the planned date | Forced slice date; kill review |
| Polish debt | Everything 80% done | Finish-before-start WIP limit |
| Crunch as plan | Overtime in baseline schedule | Cut scope at the gate; see crunch rules |
| Unowned risk | Register lists risks with no owner/date | Every risk: owner, trigger, response |
| Agent flood | More generated content than reviewed content | Review quota caps generation |
| Sunk-cost continuation | Thresholds moved after a miss | Thresholds frozen in the contract |

## Using the ontology
- Project state lives in `.gamestudio/` files managed by `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py`; use `gs.py status`, `gs.py feature` (feature list and five gates), `gs.py progress` (dated log entry for gate decisions), `gs.py budget` (asset/audio spend vs cap) and `gs.py validate` instead of hand-editing files.
- The one-page design contract and feature list conform to the project-state schemas in `${CLAUDE_PLUGIN_ROOT}/scripts/schemas/`; validate with `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py validate` or `validate_json.py`.
- Content units and progression tracks (see `game-ontology`) are what you count when you estimate content cost per minute of play.
- Templates (`gdd-one-pager.md`, `risk-register.md`, `soft-launch-plan.md`, `postmortem.md`, `pitch-deck-outline.md`, `design-contract-guide.md`) live in `${CLAUDE_PLUGIN_ROOT}/templates/docs/`.
- Agent roles: `arcosian:producer` owns this skill; `arcosian:principal` signs off gates; `arcosian:critic` challenges gate evidence.

## Reference library
| File | What it contains | When to read it |
|---|---|---|
| `references/lifecycle-and-planning.md` | Phases with gates and kill criteria, scoping, MoSCoW, estimation, milestones, planning an AI-agent team | Starting a project, setting milestones, estimating, cutting scope |
| `references/risk-team-process.md` | Risk register, top mobile and AI-build risks, roles, RACI, kanban, crunch avoidance | Risk review, staffing, setting process |
| `references/docs-and-postmortems.md` | Lean GDD, one-pager, design contract, pitch deck, postmortem formats | Writing or reviewing any project document |

## Related skills
- `design-theory`: what the contract must protect (core loop, pillars).
- `market-intel`: market evidence that feeds gate decisions and pitches.
- `qa-testing`: gate evidence, deterministic playthroughs, device matrix.
- `store-release`: submission mechanics and review buffers.
- `liveops`: the post-launch cadence that the production plan must fund.
- `player-analytics`: soft-launch metrics and thresholds.
- `game-glossary`: shared terms (vertical slice, FTUE, ARPDAU).
