---
name: postmortem
description: Runs a structured, blameless postmortem for a game project, milestone, soft launch or release and captures lessons into the project record. Writes .gamestudio/reports/postmortem-<date>.md from the postmortem template using evidence from progress, features, playtests, budget and analytics. Use when the user says "postmortem", "retro", "what went wrong", "lessons learned" or "wrap up the project".
---

# Postmortem

## When to use
At a milestone end, after soft launch or launch, after a cancelled or killed project, or after a serious incident (failed release, economy exploit, store rejection). The aim is decisions for the next project, not a narrative. Delegate evidence gathering to `arcosian:producer`, metrics to `arcosian:data-analyst`, and challenge to `arcosian:critic`. Load `production` for estimation and scope theory.

## Inputs
Optional `$ARGUMENTS`: the scope (`project`, a milestone name, or an incident description). Empty means the whole project to date.

## Procedure
1. **Gather evidence, not memories.** Read `.gamestudio/progress.md`, `features.json` (status, gate failures, notes), `contract.json` (original scope, `kill_criteria`, `risks`), `budget.json` (planned vs. spent), `playtests/`, `reports/`, `evidence/` and any analytics exports. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py status` and `gs.py budget`. List facts with dates and file paths first; opinions come later.
2. **Build the timeline.** Milestones planned vs. actual, scope added or cut, decisions that changed direction, incidents. Compute: features planned vs. done, share of features that failed a gate at least once (and which gate), asset spend vs. cap, and time from first playable to first external playtest.
3. **Start from the template.** Copy `${CLAUDE_PLUGIN_ROOT}/templates/docs/postmortem.md` to `.gamestudio/reports/postmortem-<YYYY-MM-DD>.md` and fill every section. Use a consistent structure: summary, context and goals, timeline, outcomes against targets, what went well, what went wrong, root causes, lessons, actions.
4. **Outcomes against targets.** Table of each contract target (pillars, kpi_targets, perf budgets, scope tier) with the actual and a verdict. If there is no data, write "not measured" and make measurement an action.
5. **Root-cause the problems.** For each significant problem ask why until a process or decision is reached, not a person. Typical roots: unclear contract, scope added without cut, late playtesting, late performance testing, style drift, missing instrumentation, untested economy, optimistic estimates. Blameless rule: describe decisions and systems; never name fault.
6. **Challenge it.** `arcosian:critic` tries to refute the top three conclusions: could luck or timing explain it, is the evidence enough, what is the counter-example. Drop or downgrade claims that survive poorly.
7. **Lessons.** Write each lesson as an if-then rule that could change a future decision, with the evidence link. Mark each as `process`, `design`, `tech`, `art/audio`, `business` or `team`. Prefer five good lessons to twenty vague ones.
8. **Actions.** Each action has an owner, a due point (milestone, not a guessed date) and a way to check it. Add engineering or process actions to `features.json` or the backlog via `gs.py feature`.
9. **Capture knowledge.** Append the top lessons to `.gamestudio/progress.md` with `gs.py progress "<lessons>"`. Where a lesson generalises, propose (do not silently make) an addition to a codex skill or a plugin-level note, and tell the user where it would go. If the game was deconstructable as a case study, offer `deconstruct` on it.
10. **Human checkpoint.** Present the report; the user confirms facts and tone. Never share externally (blog, talk, store page) without the user's decision.

## Question prompts (use as a menu, not a script)
- What did we believe at the start that turned out false?
- Which decision cost the most time or money, and what information would have changed it?
- Where did the five gates catch real problems, and where did something slip through?
- What would we do on day one next time?
- Which risks in the contract came true, and was the mitigation used?

## Report skeleton
```markdown
# Postmortem: <title> (<scope>, <date>)
## Summary (five lines max: outcome, biggest win, biggest miss, top lesson)
## Context and goals (contract targets, tier, team and budget)
## Timeline (date, event, evidence path)
## Outcomes vs. targets (table: target, actual, verdict, evidence)
## What went well / What went wrong
## Root causes (problem -> why chain -> process or decision)
## Lessons (if-then, category, evidence)
## Actions (owner, due milestone, check)
## Appendix: metrics, links, open questions
```

## Examples of good lessons
| Weak | Strong |
|---|---|
| "Playtest more" | "If a feature touches the core loop, run an external playtest before building the second feature on top of it" |
| "Scope creep" | "If a feature is added after the contract freeze, name the feature it replaces in the same entry" |
| "Art took long" | "If the style bible is not approved, no bulk generation runs; unlocked style cost one full regeneration of the tile set" (use the project's own evidence) |

## Metrics worth computing
- Plan accuracy: done features divided by planned features per milestone.
- Gate escape: features passing one gate but failing a later one, and which.
- Rework: assets or features regenerated or rewritten after approval.
- Spend: asset and audio spend against cap, per approved asset.
- Cycle time: first playable to first external playtest, and to soft launch.
Report only what the files support; leave unmeasured items as "not measured".

## Handling special cases
- **Cancelled project:** focus on the kill criterion that fired (or should have), cost to reach the decision, and assets that are reusable. Killing early with evidence is a success to record.
- **Incident postmortem:** timeline in minutes, detection, impact, mitigation, root cause, prevention action. Same blameless rules.
- **Milestone retro:** shorter, forward-looking; skip outcomes-vs-targets for targets not yet measurable.

## Tone
Write for a reader joining the next project cold: plain statements, dated facts, no drama, no praise padding.

## Outputs
`.gamestudio/reports/postmortem-<date>.md`, appended progress entry, backlog or process actions, optional proposal for codex updates.

## Quality gates
- Every claim links to evidence on disk or is marked as recollection.
- Blameless: no individuals blamed.
- Lessons are actionable if-then rules; actions have owner and check.
- Targets-versus-actuals table complete.
- The critic pass is recorded.

## Failure modes and recovery
| Symptom | Recovery |
|---|---|
| Little project history | Run it anyway; list what was not recorded and make recording an action |
| Report is a story with no decisions | Rewrite lessons as if-then rules |
| Everything blamed on scope | Ask what was added, by whom (role), on what evidence, and what was cut |
| Success credited to skill only | Look for luck, timing and market factors with the critic |
| User wants a quick summary | Deliver sections 1, 4, 7 and 8 only and say so |

## Related skills
`production`, `qa-testing`, `player-analytics`, `liveops`, `operate`, `deconstruct`.
