# Concept Scoring Rubric

Summary: seven criteria, each scored 1 to 10 on the `concept.schema.json` `scores` object (higher is always better, including `production_cost`, where 10 means cheap). Weights come from the presets in `skills/analogy-engine/scripts/analogy_score.py`. Anchors at 1, 5 and 10 are descriptions of evidence, not feelings. Two guards keep scores honest: gates (minimums on fun and feasibility) and evidence caps (no 9 for fun without a prototype).

## Contents
1. Criteria, weights and formula
2. Anchors per criterion
3. Evidence caps and gates
4. Presets: when to use which
5. Procedure for scoring a batch
6. Worked example
7. Tie-breaks and common errors
8. Checklist

## 1. Criteria, weights and formula

Default preset weights (sum 8.5):

| Criterion | Key | Weight | What it measures |
|---|---|---|---|
| Market | `market` | 1.5 | Is there a reachable audience and a lane not already owned? |
| Novelty | `novelty` | 1.0 | Does the hook change player decisions, not just the theme? |
| Fun potential | `fun_potential` | 2.0 | Will the core loop be compelling for 20+ sessions? |
| Feasibility | `feasibility` | 1.0 | Can the team and tools build it to the contract tier? |
| Monetization | `monetization` | 1.0 | Does it support an ethical model that fits the audience? |
| Production cost | `production_cost` | 1.0 | Is content and art volume affordable (10 = cheap)? |
| Agent buildability | `agent_buildability` | 1.0 | Can AI agents implement and verify it headless? |

Formula: `weighted_total = sum(weight_i * score_i) / sum(weight_i)`, giving a value from 1 to 10. Report it to one decimal; treat differences under 0.3 as ties.

## 2. Anchors per criterion

Score at the nearest anchor, then adjust by one for evidence either way. Scores between anchors (2 to 4, 6 to 9) interpolate.

**Market**
- 1: no identifiable audience, or a lane dominated by a giant with no angle for you.
- 5: audience exists and plays the genre, but you compete head-on with several similar titles and rely on execution.
- 10: a clearly under-served audience or format, competitors weak or stale, and a creative or targeting angle you can state in one line.

**Novelty**
- 1: re-skin of an existing game; the hook is art or theme.
- 5: a known loop with one meaningful rule change that alters a decision players make.
- 10: a new structure that players describe in different words than the genre it came from, yet is learnable in under a minute.

**Fun potential** (always the last criterion you score)
- 1: the core verb is not intrinsically satisfying and has no skill or choice depth.
- 5: a recognisable satisfying verb with some decisions; depth beyond 10 sessions is unproven.
- 10: the verb feels good by itself, decisions compound, and a playtest showed players asking to continue (needs evidence).

**Feasibility**
- 1: needs tech, content or live services the team cannot build (real-time multiplayer, large open worlds).
- 5: buildable but with at least one significant technical risk (physics tuning, large content pipeline).
- 10: deterministic sim-core, small rule set, tested patterns from the templates.

**Monetization**
- 1: only works with pressure mechanics, or the audience will not pay or watch ads.
- 5: a standard model fits (rewarded ads, a few IAP) with unremarkable yield expectations.
- 10: natural, ethical sinks and offers that players value, plus a fit with the audience's spend behaviour and clean compliance.

**Production cost** (10 is cheap)
- 1: hundreds of unique assets, long narrative or unique animation per unit.
- 5: moderate asset set, content can be procedural or templated, a few hand-made hero pieces.
- 10: a few reusable assets and procedurally generated content that stays readable.

**Agent buildability**
- 1: relies on feel that cannot be verified without a human at the controls (precision real-time, haptics).
- 5: logic is testable but visual or timing correctness needs human checks.
- 10: fully deterministic, scriptable playthroughs and bots can estimate difficulty and detect softlocks.

## 3. Evidence caps and gates

Evidence cap on `fun_potential` (`--evidence`):

| Evidence level | Meaning | Cap |
|---|---|---|
| `none` | Idea only | 7 |
| `paper` | Rules simulated on paper or in a spreadsheet | 8 |
| `greybox` | Playable prototype, no testers | 9 |
| `playtest` | Observed playtests with notes | 10 |

Gates: a card whose `fun_potential` is below 5 or `feasibility` is below 4 fails regardless of total (override with `--gate`). A failing card may be shown with its reason but is not recommended. Use stricter gates (`fun_potential=6,feasibility=5`) when the build window is short.

## 4. Presets: when to use which

| Preset | Use when | Shifts |
|---|---|---|
| `default` | Normal commercial mobile project | fun x2, market x1.5 |
| `agent_first` | The build is mostly done by AI agents with little human time | feasibility x1.5, production_cost x1.5, agent_buildability x2 |
| `ua_led` | Growth depends on paid acquisition and ad creatives | market x2, novelty x1.5, monetization x1.5 |
| `premium_indie` | Paid game or small audience of enthusiasts | novelty x2, fun x2.5, monetization x0.5 |

Pick the preset before scoring and record it in `rationale`; never choose it after seeing the ranking.

## 5. Procedure for scoring a batch

1. Score all cards on one criterion at a time (a column at a time), so anchors stay fixed across cards.
2. Write one sentence of evidence for any score of 8 or above and any of 3 or below.
3. Score `fun_potential` last and apply the evidence cap.
4. Run `analogy_score.py rank --dir .gamestudio/concepts --preset <preset>` and read gate failures first.
5. Ask `arcosian:critic` to attack the top two and re-score once, never twice.
6. Report: ranked table, the weakest criterion per card, and the cheapest test that would move it.

## 6. Worked example

Two cards, default preset.

| Criterion (weight) | Card A "Garden Merge" | Card B "Tide Tiles" |
|---|---|---|
| Market (1.5) | 5 | 7 |
| Novelty (1) | 4 | 7 |
| Fun potential (2) | 6 | 6 |
| Feasibility (1) | 8 | 6 |
| Monetization (1) | 6 | 6 |
| Production cost (1) | 7 | 6 |
| Agent buildability (1) | 8 | 7 |
| Weighted sum | 7.5+4+12+8+6+7+8 = 52.5 | 10.5+7+12+6+6+6+7 = 54.5 |
| Total (divide by 8.5) | 6.2 | 6.4 |

Difference of 0.2 is a tie by the 0.3 rule. Tie-break by the weakest criterion: A's weakest is novelty (4), B's is feasibility (6) and fun (6). A fresh prototype of B's hook is a cheaper test than finding novelty for A, so the recommendation is B with a greybox prototype before the contract, and its fun score stays capped at 7 until then.

## 7. Tie-breaks and common errors

Tie-break order: (1) higher `fun_potential`, (2) higher `feasibility`, (3) cheaper test of the weakest criterion, (4) human preference.

| Error | Symptom | Fix |
|---|---|---|
| Halo effect | One great hook lifts every score | Score by column across cards |
| Taste inflation | Every score 7 or 8 | Re-anchor at 5 = "typical"; force a ranked order |
| Cost blindness | High novelty, 10 content types | Score production_cost honestly; cut content types |
| Self-scoring bias | Author scores own idea | Have `arcosian:critic` re-score the top two |
| Market by genre size | "Puzzle is huge so 9" | Score the lane you can win, not the category |
| Unearned fun | 9 with no prototype | Apply the evidence cap |

## 8. Checklist

- Preset and gates chosen before scoring.
- All seven scores integers from 1 to 10, with evidence lines for extremes.
- Fun score capped by evidence level.
- `weighted_total` written with `--write`, ranking run, gate failures listed.
- The recommendation names its weakest criterion and the next test.
