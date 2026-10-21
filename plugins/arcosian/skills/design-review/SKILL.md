---
name: design-review
description: Multi-lens review of the design contract (design, economy, UX, monetization ethics, technical feasibility, market, scope, accessibility, compliance) with a four-level severity scale, a pass/fail verdict and a dated report. Use when the user says "review the design", "is this contract any good", "red-team my GDD", "check scope", or before building the vertical slice.
argument-hint: "[path to contract, default .gamestudio/contract.json]"
---

# Design Review

## When to use

After the contract is written (`new-game` step 7), after any material contract change, and before moving from the vertical slice to content. Not for reviewing code or builds: use `playtest` and `build-feature` gates for that.

## Inputs

`$ARGUMENTS` is an optional path to the contract; default `.gamestudio/contract.json`. Also read when present: `.gamestudio/economy/*.json`, `.gamestudio/research/market-*.md`, `.gamestudio/concepts/*.json`, `features.json`, and `config.json`.

## Procedure

1. **Validate first.** `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py validate .gamestudio/contract.json`. A schema failure is itself a critical finding; fix before reviewing content.
2. **Run the workflow.** `/arcosian:design-review` runs the lenses in parallel with specialist agents and collects findings. If workflows are unavailable, run lenses sequentially with the agents below.
3. **Apply each lens** (table below). Each reviewer reads the contract, cites the JSON path of the claim it challenges, and states the evidence or reasoning.
4. **Adversarial pass.** `arcosian:critic` tries to refute the top three strengths claimed by the contract (fun, retention, monetization). A strength that cannot survive refutation is downgraded in the report.
5. **Quantify where possible.** Use simulators, not opinions: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/economy_sim.py --help`, `progression_calc.py`, `retention_ltv.py`. Quote the command and its result in the finding. If the model file does not exist, the finding is "economy unmodelled", severity major.
6. **Classify and consolidate.** Merge duplicates, assign severity (scale below), assign an owner agent and a fix proposal that fits scope.
7. **Verdict.** `pass` (no critical, no major), `pass with conditions` (no critical, majors have owners and a deadline before slice exit), `fail` (any critical, or three or more majors in one lens).
8. **Write the report** to `.gamestudio/reports/design-review-<YYYY-MM-DD>.md` (template below). If a report exists for the date, suffix `-2`.
9. **Fix loop.** For each critical and major finding: delegate the fix, update the contract, re-validate, re-run only the affected lens. Maximum two loops, then escalate to the human with the trade-off.
10. **Log.** `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py progress "design review <date>: <verdict>, <n> critical/<n> major open"`.

## Lenses

| Lens | Agent | Core questions | Codex skill |
|---|---|---|---|
| Design | `arcosian:game-designer` | Is the core loop one clear verb with a reward? Do pillars constrain decisions? Is there depth beyond session 10? | `design-theory`, `mechanics-codex` |
| Economy | `arcosian:systems-designer` | Do sources and sinks balance over the target days? Is there a hoard or starvation point? Is progression pacing set? | `economy-design`, `progression-difficulty` |
| UX | `arcosian:ux-designer` | One-hand reach, aha under target, readable HUD, interruption safety? | `mobile-ux` |
| Monetization ethics | `arcosian:monetization-designer` | Any pressure mechanic, hidden odds, or minor-targeted offer? Does value precede the ask? | `monetization`, `legal-ethics` |
| Technical feasibility | `arcosian:lead-engineer` | Deterministic sim-core possible? Perf budgets realistic on the min spec? Backend needs? | `game-architecture`, `mobile-performance` |
| Market | `arcosian:market-analyst` | Does the lane exist, is the analogy and positioning defensible, are comparables correct? | `market-intel` |
| Scope | `arcosian:producer` | Is `scope.must` buildable at the declared tier? Are kill criteria measurable? | `production` |
| Accessibility | `arcosian:ux-designer` | Colour not the only signal, text scaling, motor options, captions, reduced motion? | `accessibility-localization` |
| Compliance | `arcosian:compliance-officer` | Age rating and audience, privacy and consent, loot-box and odds disclosure, licence and AI-asset disclosure? | `legal-ethics`, `store-release` |

## Severity scale

| Severity | Definition | Examples | Action |
|---|---|---|---|
| Critical | Makes the game unbuildable, illegal, harmful or fundamentally not fun | Schema invalid; core loop has no decision; odds hidden in a game aimed at minors | Block; fix before any build |
| Major | Likely to cause failure of a gate, KPI or store review if unfixed | Economy never sinks soft currency; aha target above 60 s with no plan; scope must list has 20 items | Fix before slice exit |
| Minor | Weakens quality or clarity but has workaround | Pillar vague; missing comparables; accessibility option absent | Schedule in backlog |
| Note | Observation, taste or future option | Idea for a live-ops event | Record, no action |

Rules: a finding without a cited contract path or evidence is a Note at most. Do not invent severity to look thorough; an honest "no major findings in the economy lens, because X was simulated" is valuable.

## Report template

```markdown
# Design review - <title> - <YYYY-MM-DD>
Verdict: pass | pass with conditions | fail
Contract: <path>, validated: yes/no. Reviewed by: <agents>.

## Summary
<5 lines: what is strong, what blocks, the single most important change.>

## Findings
| ID | Lens | Severity | Contract path | Finding | Evidence | Fix | Owner |
|---|---|---|---|---|---|---|---|

## Strengths that survived refutation
<list, with the critic's best counter-argument and why it failed>

## Open questions for the human
<taste or priority calls>

## Re-review trigger
<what change requires another review>
```

## Outputs

`.gamestudio/reports/design-review-<YYYY-MM-DD>.md`; updates to `contract.json` for accepted fixes; a progress entry. Optional new features in `features.json` for fixes that need work.

## Quality gates

- Every lens reported, even if "no findings", with the evidence it used.
- Every critical or major finding has an owner and a concrete fix within the declared scope.
- The ethics and compliance lenses ran with a specific check for minors, odds and AI disclosure; a no-finding result states the audience age assumption.
- Report committed to disk, contract re-validated after fixes, verdict consistent with the severity rules.

## Failure modes and recovery

| Failure | Recovery |
|---|---|
| Reviewers agree with everything | Re-run the critic with the instruction to find the three most likely reasons the game fails |
| Findings are style opinions | Demote to Note; require evidence or a metric |
| Workflow unavailable | Run lenses sequentially; the verdict rules are unchanged |
| Contract too thin to review (placeholders) | Verdict fail with one finding: "contract incomplete", list missing sections |
| Fixes expand scope | Move the item to `scope.should` or `scope.wont` and note the trade-off |
| Human disagrees with a critical finding | Record the override and rationale in the report; do not delete the finding |

## Related skills

`new-game`, `studio`, `market-scan`, `concept-lab`, `production`, `economy-design`, `monetization`, `legal-ethics`.
