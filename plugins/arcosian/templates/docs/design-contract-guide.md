# Design contract - authoring guide

Revision: [date] | Owner: `principal`

<!-- The design contract is the structured document (validated by `gs.py validate`) that locks what the game is before building. This guide is the human-readable companion: fill it in, then transcribe into the schema-backed file under `.gamestudio/`. Check the exact field names against the schema in `<plugin-root>/scripts/schemas/` rather than trusting this list. -->

## Purpose
A contract exists so that every later decision (feature, asset, price) can be checked against one source of truth. Changes are allowed, but only through an explicit amendment with a reason.

## Sections to complete
| Section | Question it answers | Done when |
|---|---|---|
| Vision | What is this game and for whom? | One-line pitch and one audience sentence agreed |
| Pillars (3 max) | What do we protect when we must cut? | Each pillar is testable ("a player can X in under Y seconds") |
| Core loop | What does the player repeat? | Loop beats timed; first-session path listed |
| Systems | Which systems exist and how do they connect? | Each system has inputs, outputs, owner |
| Economy | Which resources exist, sinks and sources? | `economy_sim.py` run with the draft numbers |
| Monetization | How does it earn, and what is off-limits? | Reviewed by `compliance-officer` |
| Content plan | How much, how produced? | Counts per tier and a production rate |
| Tech constraints | Engine, devices, budgets | Budgets from `perf_budget.py` |
| Non-goals | What we are not building | At least three, each tempting |
| Success metrics | What proves it works? | KPI targets labeled benchmark or assumption |

## Authoring procedure
1. Start from the one-page GDD; copy the pitch, loop and risks.
2. Write pillars last of the design sections, after the loop is clear.
3. For every system, write one acceptance test sentence ("given X, the player sees Y").
4. Run the economy and progression calculators on draft numbers; paste results below.
5. Run a `design-review`; record dissent rather than deleting it.
6. Transcribe into the schema-backed file, run `python3 <plugin-root>/scripts/gs.py validate --all`, fix errors.
7. Get explicit human sign-off; record name and date.

## Amendment log
| Date | Change | Reason | Approved by |
|---|---|---|---|
| [date] | [what] | [why] | [who] |

## Sign-off
- Human approver: [name], [date]
- Open questions carried forward: [list, each with an owner and due date]

<!-- Smell tests: pillars that could describe any game; a loop with no failure state; an economy with no sink; "TBD" in a locked section. -->
