---
name: concept-lab
description: Concept ideation lab - five ideation methods (analogy, constraint inversion, mechanic transplant, market gap, player-motivation-first), concept cards written to .gamestudio/concepts/ against concept.schema.json, and a weighted scoring rubric with 1/5/10 anchors, gates and evidence caps. Use when the user says "give me game ideas", "brainstorm concepts", "score these concepts", "X meets Y", or "which idea should we make".
argument-hint: "[theme, genre, audience or constraint]"
---

# Concept Lab

## When to use

Before a contract exists: to generate, sharpen and rank game concepts. `new-game` calls this through `/arcosian:concept-tournament`; call it directly when the user wants ideas without committing to a project, or wants an existing idea scored honestly.

## Inputs

`$ARGUMENTS` is any seed: a genre ("cozy puzzle"), an audience ("older block-puzzle players"), a constraint ("one-handed, 90-second sessions"), a source game ("what if Tetris met gardening") or empty. Empty means ask for audience and platform, then use method E.

## Procedure

1. **Fix constraints first.** Audience, platform, session length, monetization model, build tier (prototype or slice), what is off-limits. Write them in one line; every card must satisfy them. Missing answers use the defaults in `new-game`.
2. **Load knowledge.** `analogy-engine` (operators, chassis library, lineages), `genre-playbooks` (genre norms, saturated lanes), `player-psychology` (motivation), `mechanics-codex` (verbs and mechanics). Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py kb "<seed>" --limit 5` to pull relevant passages.
3. **Pick methods.** Use at least two different methods per batch so cards are not siblings. Detail in `references/ideation-methods.md`.

   | Method | Start from | Best when | Typical output |
   |---|---|---|---|
   | A. Analogy ("X meets Y") | A source game or domain | Brief is a theme or a vibe | Mapped structure plus hook |
   | B. Constraint inversion | A genre convention | Genre is saturated | Same genre, broken rule |
   | C. Mechanic transplant | A proven mechanic | You want a safe core with a new context | Familiar loop in a new fantasy |
   | D. Market gap | Competitor matrix | A market scan exists | Under-served audience or loop |
   | E. Player-motivation-first | A player and their need | Audience is known | Loop built for one motivation |

4. **Generate** at least `n` (default 6) candidates, then cut to 3 to 5 for full cards. Cut with one test per candidate: "can I describe the first 30 seconds of play, with the verb and the reward?" If not, drop it.
5. **Write cards.** One JSON file each in `.gamestudio/concepts/<id>.json` with `schema_version: "1.0"` and the schema fields: `id` (kebab-case slug), `title`, `logline`, `analogy`, `genre`, `player_fantasy`, `core_loop`, `hook`, `pillars`, `target_audience`, `monetization_model`, `comparables`, `scores`, `risks`, `kill_criteria`, `rationale`. Schema: `${CLAUDE_PLUGIN_ROOT}/scripts/schemas/concept.schema.json`; example: `${CLAUDE_PLUGIN_ROOT}/scripts/schemas/examples/example.concept.json`.
   - `hook` is one sentence naming the novel twist and why it changes decisions, not decoration.
   - `comparables` name what you borrow and what you change.
   - `kill_criteria` carry numbers measurable in a prototype playtest.
6. **Score** each card with `references/scoring-rubric.md`. Score fun_potential last, and cap it by evidence (a paper concept cannot earn more than 7 on the default cap). Compute totals:
   ```
   python3 ${CLAUDE_PLUGIN_ROOT}/skills/analogy-engine/scripts/analogy_score.py concept --card .gamestudio/concepts/<id>.json --preset default --gate "fun_potential=5,feasibility=4" --evidence none --write
   python3 ${CLAUDE_PLUGIN_ROOT}/skills/analogy-engine/scripts/analogy_score.py rank --dir .gamestudio/concepts --preset default
   ```
7. **Critique.** Delegate to `arcosian:critic`: ask it to refute the top two cards (is the hook real, is the audience reachable, does the loop survive 20 sessions). Update scores where the critique lands; note it in `rationale`.
8. **Tournament (optional, for breadth).** `/arcosian:concept-tournament` with `{"brief": "...", "constraints": {...}, "n": 5}`; it generates, critiques and ranks in parallel with agents. Then read its ranking and apply steps 6 to 7 yourself.
9. **Present** the top three as a table (title, analogy, hook, weighted total, gate status, biggest risk) and recommend one. Cheaper and riskier options should be labelled as such. Validate cards: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py validate --all`.

## Card skeleton

```json
{
  "schema_version": "1.0",
  "id": "tide-tiles",
  "title": "Tide Tiles",
  "logline": "A calm block puzzle where the board floods and recedes on a visible tide clock.",
  "analogy": "Tetris meets tide pools",
  "genre": "puzzle/block",
  "player_fantasy": "Reading the rhythm of the sea and always having the perfect move ready.",
  "core_loop": "Place pieces, clear lines before the tide closes rows, bank the exposed rows.",
  "hook": "Rows become unplaceable on a visible cycle, so players plan placements around the tide.",
  "pillars": ["Calm, readable, one-handed", "Planning beats reflexes", "Every clear is juicy"],
  "target_audience": {"age_min": 13, "segments": ["adults 35+ who play block puzzles on commutes"], "motivations": ["relaxation", "mastery"]},
  "monetization_model": "hybrid",
  "comparables": [{"title": "<block puzzle>", "borrow": "placement verb", "change": "timed row availability"}],
  "scores": {"market": 7, "novelty": 7, "fun_potential": 6, "feasibility": 6, "monetization": 6, "production_cost": 6, "agent_buildability": 7},
  "risks": ["Tide clock may feel like a timer and add stress"],
  "kill_criteria": ["Under 6 of 10 testers finish three levels voluntarily"],
  "rationale": "Default preset; fun capped at 7 until a greybox exists."
}
```

Illustrative only: replace every field with the real concept, and check field types against the schema before writing (`gs.py validate`).

## Outputs

- `.gamestudio/concepts/<id>.json`, one per concept (valid against `concept.schema.json`, with `scores.weighted_total` after `--write`).
- A ranked summary in chat; optionally appended to `.gamestudio/progress.md` via `gs.py progress`.

## Quality gates

- Every card passes schema validation and names a hook that is not a skin.
- Scores justified in `rationale` for any criterion at 8 or above and any at 3 or below.
- Gates applied (default fun_potential at least 5 and feasibility at least 4); a card that fails a gate is shown but not recommended.
- At least two methods contributed to the batch; no two top cards share a chassis (core loop) unless the hooks differ materially.
- Ethics screen: no concept depends on a pressure mechanic as its main hook (`legal-ethics`).

## Failure modes and recovery

| Failure | Recovery |
|---|---|
| Every card is a clone of a top-grosser | Apply method B or D; require a named audience the clone under-serves |
| Hook is a theme swap | Reject; restate as "players now decide X instead of Y" |
| Scores all land between 6 and 8 | Re-anchor with the 1/5/10 anchors; force a rank order and score the relative difference |
| Fun_potential scored 9 with no prototype | Apply the evidence cap; schedule a greybox prototype to earn it |
| User falls in love with one card | Score it honestly anyway and show the weakest criterion plus the cheapest test that would resolve it |
| `analogy_score.py` exits 2 | A score is missing or outside 1 to 10; fix the card |

## Reference library

| File | Contains | Read when |
|---|---|---|
| `references/scoring-rubric.md` | Seven criteria with weights, 1/5/10 anchors, evidence caps, gates, presets, tie-breaks, worked example | Scoring or defending a score |
| `references/ideation-methods.md` | Five methods as procedures with prompts, checks, pitfalls and worked examples | Generating candidates |

## Related skills

`analogy-engine` (operators, chassis, scoring script), `genre-playbooks`, `player-psychology`, `mechanics-codex`, `market-scan`, `new-game`, `design-review`.
