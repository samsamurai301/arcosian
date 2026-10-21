# Ideation Methods

Summary: five repeatable procedures for generating game concepts, each with the question it answers, steps, check questions, pitfalls and a short worked example. Use two or more per batch. The deep theory (structure mapping, transformation operators, lineages) lives in `analogy-engine`; this file is the practitioner's quick route. Frameworks are summarised in my own words with attribution.

## Contents
1. Choosing methods
2. Method A: analogy
3. Method B: constraint inversion
4. Method C: mechanic transplant
5. Method D: market gap
6. Method E: player-motivation-first
7. Combining methods
8. Divergence and convergence rules
9. Hook tests
10. Anti-patterns

## 1. Choosing methods

| You have | Start with | Add |
|---|---|---|
| Only a theme or mood | A | E to make it playable |
| A saturated genre | B | D to find the lane |
| A proven mechanic you trust | C | A to find a fresh setting |
| A market scan | D | C or B to fill the gap |
| A named audience | E | A for the hook |
| Nothing | E then D | any |

Always run the first-30-seconds test (see `SKILL.md` step 4) on every candidate before spending effort on a card.

## 2. Method A: analogy ("X meets Y")

Idea from structure-mapping research (Dedre Gentner, 1983): a good analogy transfers relations between parts, not surface features.

Steps:
1. Pick a source (a game or a real-world system) and write its structure as verbs, resources, constraints and goals. Ignore its look.
2. Pick a target context (the audience's world or a genre).
3. Map relations: which source verb becomes which target verb; which resource maps to which. List what does not map.
4. Check the mapping: do the relations still create the same decision pressure? If a relation only works because of the source's theme, drop it.
5. State it: "X meets Y: players do <verb> to <goal>, but <twist>."

Score the mapping with `analogy_score.py fitness` when in doubt. Pitfall: surface leakage, where the new game looks different but plays identically. Example: source "tide pools" (resources that flood and recede); target block puzzle. Mapped relation: a board region periodically becomes unplaceable and later returns. Decision change: players plan around the cycle. Hook: placement rows rise and fall on a visible tide clock.

## 3. Method B: constraint inversion

Take a genre's unspoken rules and flip one at a time.

Steps:
1. List 6 to 10 conventions ("the board is a grid", "you can undo", "time ends the level", "the player owns one piece at a time").
2. For each, write the inverse ("the grid is a ring", "undo is the resource", "levels start when you stop").
3. For each inverse, ask what new decision it creates and what it breaks. Keep only inversions that create decisions.
4. Combine with at most one other inversion; two is a different game, three is a mess.

Check: can a new player understand the inversion in one screen? Pitfall: inversions that only add friction (hiding information with no skill payoff). Example: "time ends the level" inverted to "the level ends only when you choose to bank your score", which turns a puzzle into a risk-reward push-your-luck game.

## 4. Method C: mechanic transplant

Move a proven mechanic from one context into another, keeping its dynamics.

Steps:
1. Name the mechanic in ontology terms (verb, rules, parameters, dynamics) using `mechanics-codex`.
2. List the dynamics that made it work (for example "scarcity creates tension", "combos reward planning").
3. Find the target context's equivalent resource for each dynamic. If a dynamic has no equivalent, the transplant will fail.
4. Adjust parameters for mobile sessions (see `mobile-ux`): shorter loops, one-hand input.
5. Write the fantasy for the new context.

Pitfall: transplanting the surface UI rather than the dynamics. Example: a limited-move budget from match puzzles transplanted into a cooking game where each move is an ingredient action, so recipe order matters.

## 5. Method D: market gap

Needs a market scan (`market-scan`).

Steps:
1. From the competitor matrix pick the empty cells: audience segment by loop type by monetization.
2. For each empty cell ask why it is empty: no demand, hard to build, or unnoticed. Discard "no demand".
3. Check one reason it is under-served that your team can fix (for example "no good one-handed version").
4. Define the lane in one line and name the nearest competitor you will beat on a specific dimension.

Check: can UA reach this audience at a plausible cost? Do not state costs without data. Pitfall: confusing "nobody has done it" with "nobody wants it". Example: older players of word and block puzzles like long sessions but many apps are ad-heavy; a calm, low-ad premium-feeling puzzle with offline play is a gap to test, not a given.

## 6. Method E: player-motivation-first

Draw on motivation research such as Self-Determination Theory (Deci and Ryan) and Quantic Foundry's gamer motivation model (Nick Yee); use them as lenses, not as truths (`player-psychology`).

Steps:
1. Write one persona: age band, context (where, how long, how many hands), and the dominant motivation (mastery, relaxation, collection, expression, competition, discovery).
2. Write the feeling the player should have after a session in one sentence.
3. Pick the loop that produces that feeling (what is the verb, what is the reward cadence).
4. Add the one twist that makes the loop theirs.

Pitfall: persona of "everyone". Example: commuter wanting relaxation in 2-minute bursts leads to a loop with no fail state, a visible daily goal, and satisfying audiovisual feedback; the hook decides which of those players will remember.

## 7. Combining methods

- E then A: motivation decides the feeling, analogy supplies the structure.
- D then C: the gap decides where, the transplant decides what.
- B then E: inversion is validated against a persona to filter out friction-only ideas.
Keep the batch diverse: no more than two cards from the same method pair.

## 8. Divergence and convergence rules

- Diverge first: generate at least 12 one-line seeds before judging any.
- Never score during generation.
- Converge with two filters: first-30-seconds test, then constraint fit.
- Keep 3 to 5 for cards; keep 1 as a deliberate wildcard.
- Record rejected seeds in a single line each in progress notes; some return later.

## 9. Hook tests

| Test | Pass looks like |
|---|---|
| Decision test | The twist changes what the player chooses on turn 1 |
| Screenshot test | A screenshot or 5-second clip reveals the twist |
| Retell test | A player can retell the game in one sentence including the twist |
| Remove test | Remove the twist and the game becomes a known one |
| Depth test | The twist creates different decisions at minute 10 than minute 1 |

A hook that fails the decision test is a skin.

## 10. Anti-patterns

| Anti-pattern | Detect | Fix |
|---|---|---|
| Genre salad | Three genres in the logline | Pick one chassis, one twist |
| Feature hook | Hook is "with crafting" | Say which decision crafting changes |
| Nostalgia trap | Pitch depends on loving an old game | Test with someone who never played it |
| Pressure hook | Retention depends on loss, FOMO or streak anxiety | Redesign; see `legal-ethics` |
| Unbuildable charm | Relies on precise real-time feel or large content | Lower feasibility score or cut |
| Copying trade dress | Names or art from a title | Borrow mechanics only |
