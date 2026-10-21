# Puzzle Level Design

How to design puzzle levels that produce a real "aha", are fair, can be tuned to a target difficulty, and can be checked by a machine. It covers puzzle theory (what a puzzle is, the anatomy of an insight, constraints, red herrings), the factors that make a puzzle hard and how to measure them with a solver, solution uniqueness, hint and stuck systems, how to sequence a puzzle game's mechanics, and solver-driven design and generation. Per-type parameter tables cover sort, Sokoban, sliding tiles, Lights Out, flow-connect, nonogram, sudoku and the casual physical-puzzle family. Match-3 and blast are in `casual-level-production.md`; tooling and the level-spec format are in `level-pipeline.md`.

## Contents

1. What a puzzle is
2. Anatomy of an aha
3. Designing backwards from the insight
4. Constraints
5. Red herrings, noise and decoys
6. Difficulty factors and how to measure them
7. A composite difficulty estimate
8. Solution uniqueness and shortcut control
9. Hints, undo and stuck support
10. Sequencing a puzzle game
11. Solver-driven design and generation
12. Per-type parameter tables
13. Worked example: a sort level from brief to verified spec
14. Puzzle level review checklist

---

## 1. What a puzzle is

Scott Kim's commonly quoted definition: a puzzle "is fun, and it has a right answer". The right answer separates a puzzle from a toy (no goal) and from a game against an opponent (the answer depends on the other player). The fun separates it from a chore.

A puzzle level is a tuple:

| Part | Meaning | Level-spec field |
|---|---|---|
| State | The configuration the player sees | `layout` |
| Moves | The legal actions and their rules | contract `mechanics[].rules`, referenced by `mechanic_refs` |
| Goal | The test for a solved state | `goals` |
| Constraints | Limits on moves, time, resources or information | `moves_or_time_limit`, `obstacles` |
| Insight | The idea the player must discover to solve it | `notes` (write it down) |

**Puzzle vs challenge.** A puzzle is solved once by understanding; a challenge (dexterity, reaction) is repeated by execution. Casual mobile puzzles blend both: sort and screw puzzles are mostly puzzle; match-3 is mostly a probabilistic challenge with puzzle moments. Know which you are designing, because hints, retries and monetization behave differently. A pure puzzle solved once has no replay value; a challenge improves with practice.

**The three audiences.**

| Audience | Example titles | Expects | Tolerates |
|---|---|---|---|
| Mass casual | Water-sort, screw-sort, tile-match games | Steady progress, short levels, almost no dead ends | Little frustration; no red herrings |
| Midcore puzzle | Two Dots, Monument Valley, Cut the Rope | Clever moments, light challenge | Occasional retry; mild misdirection |
| Dedicated puzzle | Baba Is You, Stephen's Sausage Roll, Snakebird, The Witness | Deep insights, minimal hand-holding | Being stuck for a long time; red herrings only if fair |

## 2. Anatomy of an aha

An aha is the moment a player abandons a wrong model of the rules or the situation and adopts a right one. The most useful working model: **every good puzzle exploits one false assumption the player is likely to hold.** Name the assumption, and you have named the puzzle.

### Insight types

| Insight type | False assumption broken | Generic example |
|---|---|---|
| Hidden property of a rule | "This rule only does what I saw it do first" | Pushing a block also pushes the block behind it |
| Sequencing | "Order does not matter" | Clear the left tube first so the right tube has somewhere to pour |
| Temporary regression | "Every move should make progress" | Move a box *away* from its goal to reposition |
| Sacrifice | "I should keep every resource" | Fill the empty tube with the wrong colour to unlock two others |
| Repurposing | "This object is for X" | A box used as a step, not as a goal object |
| Invariant / parity | "Any arrangement is reachable" | A tile can only reach squares of one colour; the puzzle is solved by noticing which |
| Working backwards | "Start from the current state" | The last move must be X, so the second-to-last must be Y |
| Combination | "Each mechanic works alone" | Ice plus gravity: frozen tiles hold up the column above them |
| Reframing the goal | "The goal means what it seems to mean" | Baba Is You–style: the win condition itself can be changed |
| Perspective | "The view shows everything" | Monument Valley–style: what connects depends on viewpoint |

### Rules for insight
- **One primary insight per level.** Two insights in one level multiply difficulty unpredictably; reserve that for late "exam" levels.
- **The insight must be discoverable from the board.** Players should be able to reason their way to it; if it can only be found by random trial, it is not an insight, it is a lottery.
- **Make the false assumption tempting.** The obvious first move should be plausible and should fail informatively (the player sees *why* it fails).
- **Pay off the insight with a visible change.** The board should transform when the key move is made: a cascade, a door opening, two tubes completing.

## 3. Designing backwards from the insight

The reliable method used by many puzzle designers: start from the idea, not the board.

1. **State the insight** in one sentence: "You must fill a tube with the wrong colour to free two others."
2. **Build the minimal configuration** that requires it. Fewest pieces, smallest board. If the insight can be shown with 3 tubes, do not use 7.
3. **Run the solver.** Confirm the level is solvable and that every shortest solution uses the insight (section 8). If a shortcut exists, block it with the smallest change: a wall, a capacity limit, one extra piece.
4. **Add the context.** Only now add the elements that make it a level: theme, a little noise for the target audience, a move limit with the right slack.
5. **Set the first reading.** Arrange the opening so the obvious move is plausible but wrong in an informative way (for midcore and dedicated audiences) or plausible and right (for mass casual teach levels).
6. **Re-run the solver and record results** in `solver` (`min_moves`, `solvable`, `bot_win_rate`, `runs`).
7. **Playtest** with 3–5 target players or persona bots; watch for the moment of insight. If nobody has it, the level is too obscure; if nobody needs it, there is a shortcut.

For mass casual games, steps 1–3 are often replaced by **generate and filter** (section 11): generate many random deals, measure them, and keep those whose metrics match the target. Designers then curate. Both methods end at the same verification gate.

## 4. Constraints

Constraints force insight by closing the easy roads. They also define difficulty.

| Constraint | Effect | Over-constrained symptom | Under-constrained symptom |
|---|---|---|---|
| Move limit | Forces efficient solutions; creates tension | Only the optimal solution works; feels like an exam | No tension; trial and error wins |
| Space (board size, empty cells, empty tubes) | Limits manoeuvring room | Dead ends everywhere | Brute force works |
| Piece count | Limits tools | The single solution is opaque | Many trivial solutions |
| Irreversibility | Mistakes accumulate | Players must restart often | No planning needed |
| Time limit | Adds execution pressure | Thinking is punished; puzzle becomes reflex | — |
| Hidden information | Requires exploration or inference | Feels random | No discovery |

### Move-limit slack
For a deterministic puzzle with optimum `m*` (from the solver) and limit `L`:

```
slack ratio  s = L / m*
```

| Role | Slack ratio (heuristic starting band) | Feel |
|---|---|---|
| teach | ≥ 2.0 or no limit | Free exploration |
| reward | 1.8–2.5 | Breather |
| test | 1.3–1.8 | Some planning |
| twist | 1.2–1.5 | Must understand the insight |
| hard / exam | 1.0–1.2 | Near-optimal play required; use sparingly |

The example level in `${CLAUDE_PLUGIN_ROOT}/scripts/schemas/examples/example.level-spec.json` uses L = 30 over m* = 13 (s ≈ 2.3) for a reward level. `level_audit.py` warns when `s` falls outside a configurable band and errors when `L < m*` (unwinnable).

Many casual sort and screw games have **no move limit**; difficulty then comes from dead ends and the scarcity of empty space, and the "constraint" is the cost of restarting or using an undo or extra-tube booster.

## 5. Red herrings, noise and decoys

A red herring is an element that suggests a wrong approach. Noise is anything not on the solution path. Both raise difficulty and both can feel unfair.

| Kind | Definition | Fair when | Unfair when |
|---|---|---|---|
| Noise | Extra elements irrelevant to the solution | It is visually subordinate and consistent with the world | It is visually identical to key elements and slows reading |
| Decoy | A plausible first move that fails | It fails visibly and teaches something | It fails silently or many moves later |
| Red herring | A deliberately misleading element | The audience is dedicated and the rules give enough information to rule it out | The only way to rule it out is trial |
| Trap | A move that leads to an unwinnable state | Undo is free or the dead end is detectable within 1–2 moves | Undo is scarce and the dead end appears 10 moves later |

**Guidelines by audience**
- Mass casual: noise low, decoys only in test and twist levels, no red herrings, traps detectable quickly and always recoverable with free undo or restart.
- Midcore: one decoy per level is fine; traps only with undo.
- Dedicated: red herrings acceptable if the rules logically exclude them; avoid them in tutorial chapters.

**Measure it:** count elements not touched by any shortest solution (`noise count`) and count legal moves on the solution path that lead to dead-end states (`trap count`, section 6). Track both per level so difficulty from obfuscation is visible.

## 6. Difficulty factors and how to measure them

Difficulty is not length. A 40-move sort level with an obvious greedy path can be easier than a 9-move Sokoban that needs one counter-intuitive push. Measure several factors.

| Factor | What it is | How to measure (solver / bot) | Direction |
|---|---|---|---|
| Solution length `m*` | Moves in the shortest solution | BFS / A* `min_moves` | Longer = harder, weakly |
| State space size | Reachable states | Number of states BFS visits (bounded) | Larger = harder to reason about |
| Branching factor `b` | Legal moves per state on the solution path | Average legal-move count along the path | More choices = harder |
| Dead-end density | Share of reachable states from which the goal is unreachable | Reverse search from goal or forward search with goal-reachability marking | More dead ends = harder, more frustrating |
| Trap count | Legal moves along the solution path that enter a dead end | For each solution-path state, count moves to dead-end states | More traps = harder, needs undo |
| Counter-intuitive moves | Optimal moves a greedy heuristic would rank low | Compare each optimal move's rank under a simple heuristic (e.g. "moves that complete or extend a run first") | Strongest predictor of "aha" difficulty |
| Number of solutions | Distinct shortest (or near-shortest) solutions | Count optimal paths (with a cap) | Fewer = harder |
| Irreversible moves | Moves that cannot be undone by another legal move | Check whether the inverse move is legal | More = more planning |
| Random-bot success | Share of random-play runs that solve within the limit | Bot runs | Lower = harder; ≈ 1 means trivially solvable by accident |
| Greedy-bot success | Share of greedy-heuristic runs that solve | Bot runs | Gap between greedy and optimal shows "insight required" |
| Information load | Elements the player must track at once | Count distinct colours, pieces, hidden items | More = harder, especially on small screens |
| Insight count | Distinct insights needed | Designer tag in `notes` | Each extra insight multiplies difficulty |

### Measurement notes
- **Search effort as a proxy for human effort is imperfect.** Humans prune with insight; BFS does not. Use solver metrics as features in a model calibrated on human data (section 7), not as difficulty itself.
- **Greedy-versus-optimal gap is the best single "aha" signal.** If a greedy bot solves the level as often as an optimal planner, the level has no required insight. If greedy never solves it, the level requires at least one non-greedy move.
- **Dead-end density is the best single frustration signal.** High dead-end density with scarce undo produces churn.

### Theoretical cautions (stable facts)
- Many puzzle families are computationally hard in general: Sokoban is PSPACE-complete (Culberson, late 1990s); finding shortest solutions for the generalised sliding-tile puzzle is NP-hard (Ratner and Warmuth, 1990); solving nonograms in general is NP-complete. This does not matter at mobile sizes, but it means **solver node budgets must be capped** and "budget exceeded" must be reported as *unknown*, never as *unsolvable*.
- The 8-puzzle has 181,440 reachable states and every position is solvable in at most 31 moves; the 15-puzzle needs at most 80 single-tile moves, and exactly half of all tile arrangements are reachable (a parity invariant). Use the parity check before searching sliding puzzles.
- In 5×5 Lights Out, only one quarter of start patterns are solvable, and each solvable pattern has exactly four solutions (the press matrix over GF(2) has rank 23). Order of presses never matters, and pressing a cell twice cancels out, so solutions are sets of cells.
- A classic sudoku needs at least 17 givens to have a unique solution (McGuire, Tugemann and Civario, 2012).

## 7. A composite difficulty estimate

Use solver features to predict human difficulty, then calibrate on playtest or soft-launch data. Start with a simple linear form; the weights below are placeholders to be fitted, not published constants.

```
D = w1 · log2(states_visited)
  + w2 · min_moves
  + w3 · counter_intuitive_moves
  + w4 · 10 · dead_end_density
  + w5 · trap_count
  − w6 · log2(1 + optimal_solution_count)
  + w7 · (1 − greedy_bot_win_rate)
```

Calibration procedure:
1. Measure the features for every level with the solver and bots (batch, `level-pipeline.md` section 11).
2. Collect human outcomes for at least 30–50 levels: first-try win rate and attempts p50 (playtest or soft launch).
3. Fit the weights with ordinary least squares on a transformed target such as `logit(first_try_win_rate)`. Keep only features with stable, sensible-signed coefficients; drop the rest.
4. Check the fit on held-out levels (mean absolute error in win-rate points). If the error is above about 10 points, add features (e.g. information load) or use separate models per mechanic family.
5. Use the model to slot new levels into the curve before they ship, then refit monthly with live data.

This mirrors the production approach reported by King for Candy Crush (bots predicting level difficulty, recalibrated against player data; see `casual-level-production.md` volatile facts) applied to deterministic puzzles.

## 8. Solution uniqueness and shortcut control

### When uniqueness matters
| Puzzle kind | Uniqueness | Why |
|---|---|---|
| Logic grids (nonogram, sudoku, Kakuro) | **Required** | Players deduce; a second solution breaks the deduction chain and forces guessing |
| Insight puzzles (Sokoban-like, rule puzzles) | Uniqueness of the *key move* matters, not of the full sequence | The intended aha must be unavoidable; move order around it can vary |
| Casual sort, screw, tile-match | Not required | Many solutions make levels forgiving; difficulty comes from dead ends |
| Match-3 / blast | Not applicable | Stochastic; use bot win rates instead |

### Key-move analysis (for insight puzzles)
1. Find all shortest solutions (cap the count, e.g. 1,000) and near-shortest ones up to `m* + k` (k = 2–4).
2. Identify **bottleneck states**: states every solution passes through, or **key moves** every solution contains.
3. Confirm the intended insight corresponds to a key move. If some solutions avoid it, there is a shortcut.
4. Block the shortcut with the smallest change and re-run.

### Logic-puzzle uniqueness
- Nonograms: require **line-solvability** for casual audiences: the puzzle can be solved by applying single-line deductions repeatedly, without guessing. Check with a line solver; if it stalls before completion, the puzzle needs guessing or has multiple solutions.
- Sudoku-style: count solutions with a backtracking solver capped at 2 (stop on the second). Grade difficulty by the hardest deduction technique a human-style solver needs (singles, then pairs and triples, then fish and chains), not by the number of givens.

### Robustness checks (all puzzle kinds)
- **Off-by-one exploits:** try the level with the move limit reduced by one; if it is still solvable, the stated `min_moves` is wrong or there is a shorter path.
- **Symmetry duplicates:** canonicalise states (sort interchangeable tubes; rotate and mirror boards where rules allow) so two levels that differ only by symmetry are not shipped as different levels.
- **Unintended softlocks:** search for reachable states with no legal moves that are not solved. Every such state needs a visible "stuck" response (auto-offer undo or restart).

## 9. Hints, undo and stuck support

Stuck is the puzzle player's churn moment. Design the response.

### Detecting stuck
| Signal | Threshold (heuristic; tune by telemetry) | Notes |
|---|---|---|
| Idle time | 8–15 s without input in a turn-based puzzle | Shorter for teach levels |
| Revisiting states | The same state hash 3+ times | Cycles indicate the player has no plan |
| Move count | > 2× `m*` without solving | Wandering |
| Dead-end entered | Solver says the goal is unreachable from the current state | Precise; requires a fast solver on device or a precomputed dead-end table |
| Restarts | 3+ restarts in one session on the level | Frustration |

### Hint ladder
Offer hints in ascending specificity; each step gives the player the chance to have the insight themselves.

| Step | Content | Example (sort puzzle) |
|---|---|---|
| 0 Nudge | Draw attention to a region | Pulse the two tubes involved in the next useful move |
| 1 Direction | Name the sub-goal | "Free up the blue tube first" |
| 2 Next move | Show the next optimal move from the current state | Animate pouring tube 3 into tube 6 |
| 3 Recovery | If in a dead end, show where to undo to | Rewind to the last solvable state |
| 4 Solution | Play the rest | Rarely appropriate outside kids' games |

**Solver-generated hints.** Compute the shortest path from the *current* state; its first move is the hint. If the current state is a dead end, walk back through the undo stack to the latest state from which the goal is reachable and offer to rewind there. For small puzzles this runs on device; for large ones, precompute a table of solution-path states and fall back to "restart" when the player leaves it.

### Undo and restart policy
- Free restart, always. Restart should take under a second.
- Undo: free and unlimited in dedicated puzzles; limited or booster-based in many casual games. If undo is scarce, keep dead-end density low and make dead ends visible within 1–2 moves.
- Skips: allow skipping a level after N failures in dedicated puzzle games, or keep several puzzles open at once (section 10) so a stuck player always has something else to try.

### Hint economy and ethics
- Every level must be **solvable without paying**. Hints and boosters sell convenience, not solvability.
- Show the price of a hint before use; never auto-spend.
- Do not tune levels to be unsolvable without a booster to raise booster sales (`monetization`, `legal-ethics`).

## 10. Sequencing a puzzle game

### The mechanic graph
List every mechanic and rule interaction as nodes; draw an edge where two interact in an interesting way. Introduce nodes in an order where each new node connects to ones already taught.

```
gravity ──── ice ──── chains
   │           │
 portals    spreaders
```

- Introduce the root (core rule) first, then nodes with the most edges to already-taught nodes.
- Each node gets its own teach and test levels before it appears in a twist with a neighbour.
- Leaf nodes with few edges are cheap novelty; hub nodes with many edges carry long-term depth.

### Exhausting a mechanic
A mechanic's design space runs out when new levels stop producing new insights. Signs: twist levels start reusing the same key move; solver key-move analysis shows the same pattern; playtesters solve new levels faster than old ones. When this happens, retire the mechanic from new twists and introduce the next one. Dedicated puzzle games often give each mechanic a world of roughly 8–15 levels; casual games mix mechanics more freely over hundreds of levels (`casual-level-production.md`).

### Linear vs open selection
| Structure | Fits | Stuck behaviour |
|---|---|---|
| Strict linear (saga map) | Casual, match-3, sort | One stuck level blocks everything; needs hints and slack |
| Open hub (several unlocked at once) | Dedicated puzzle (e.g. hub-world designs such as The Witness or Stephen's Sausage Roll) | Players leave a hard puzzle and return later; the subconscious keeps working |
| Packs of N with "solve K of N to proceed" | Midcore mobile puzzles | Good compromise; K/N around 0.7–0.8 |

## 11. Solver-driven design and generation

Solvers are design tools, not only QA. Use them in the loop.

### Search algorithms for level checking
| Algorithm | Use | Notes |
|---|---|---|
| BFS | Shortest solution, small spaces; exhaustive state statistics | Memory grows with state count; cap with `--max-nodes` |
| A* | Shortest solution with an admissible heuristic | Sliding: Manhattan distance; Sokoban: sum of box-to-nearest-goal distances (admissible lower bound) |
| IDA* | Large spaces with low memory | Repeats work; good for 15-puzzle-class problems |
| Bidirectional BFS | When the goal state is known and moves are reversible | Sliding puzzles |
| Backtracking with propagation | Logic grids (nonogram, sudoku) | Count solutions up to 2 |
| Monte Carlo bots | Stochastic games (match-3, blast) | Win-rate estimates with confidence intervals |

`puzzle_solver.py` implements BFS and A* for `layout.type` sliding, sokoban, sort and lights_out (`level-pipeline.md` section 7). For other families, write a purpose-built solver inside the game project and record its results in the same `solver` fields.

### State engineering
- **Canonical hashing.** Represent a state compactly and canonically: sort interchangeable containers (tubes in sort puzzles), normalise player position in Sokoban to the reachable region's top-left cell, ignore cosmetic data.
- **Deadlock pruning.** Sokoban: a box on a non-goal corner cell is dead; two boxes side by side against a wall with no goals are dead ("freeze" deadlocks). Sort: a state with no legal move that is not solved is dead.
- **Move compression.** Treat a pour of several matching items as one move if the game does; treat a Sokoban "walk then push" as one push move.

### Generation strategies
| Strategy | How | Strengths | Weaknesses | Fits |
|---|---|---|---|---|
| Random + filter | Generate random valid configurations; solve; keep those matching target metrics | Simple; huge variety | Many rejects for hard targets | Sort, screw, tile-match, Lights Out |
| Reverse play | Start from the goal and apply reversed moves | Every output is solvable by construction | Reverse-move rules can be subtle; outputs cluster near the goal unless the walk is long and biased | Sokoban (pull moves), sliding |
| Mutate and climb | Start from a level; apply small edits; keep edits that move metrics toward the target | Reaches hard targets; preserves designer intent | Local optima; needs a fitness function | Any puzzle with a solver |
| Constraint solving (SAT / ASP) | Encode level rules and desired properties; let a solver find layouts | Can guarantee properties (unique solution, key move) | Expertise needed; slow for large levels | Logic puzzles, small insight puzzles |
| Template + parameter | Designer templates with parameter slots filled by the generator | Keeps authored feel at volume | Variety limited by template count | Casual production |
| LLM proposal + verify | An LLM proposes layouts or variations from a brief; the solver verifies | Fast ideation, good for themed sets | Unreliable on hard targets; never ship unverified | Ideation and variants |

**Fitness for mutate-and-climb**, given target win rate `t` and the composite estimate `D` (section 7):
```
fitness = − | predicted_win_rate(D) − t |
          − λ1 · max(0, noise_count − noise_cap)
          − λ2 · [shortcut found]
          − λ3 · [layout hash already used]
```

**Generation policy (hard rule):** every generated level passes the solver gate before it is stored as a candidate. Research on LLM-generated levels shows playability falls sharply as requested difficulty rises (see `level-pipeline.md` volatile facts), so hard targets get the most verification, never the least.

## 12. Per-type parameter tables

Parameters are starting points. Measure with the solver; record in level-spec.

### Sort (water, ball, nut)
`layout.type: sort`, fields `capacity`, `tubes` (bottom first), `pour` (`max` or `single`), optional `colors`.

| Parameter | Typical range | Effect on difficulty |
|---|---|---|
| Colours C | 3 (teach) to 12+ (late game) | Strongest lever: state space and planning grow quickly with C |
| Capacity K | 4 (genre standard); 3 or 5 for variety | Higher K means longer runs to assemble |
| Empty tubes E | 2 standard; 1 for hard; 3 for relief | Fewer empty tubes means more dead ends |
| Pour rule | `max` (water) or `single` (ball) | `single` gives finer control, usually easier to recover |
| Hidden layers | Unknown items revealed when exposed | Adds inference and luck; teach separately |
| Pre-sorted runs | Matching items already stacked | Lowers difficulty; useful for teach levels |

Rules: each colour appears exactly K times; no tube exceeds K; start state is not solved; verify solvable; record `min_moves`.

### Sokoban
`layout.type: sokoban`, XSB rows (`#` wall, `@` player, `+` player on goal, `$` box, `*` box on goal, `.` goal, space, `-` or `_` floor).

| Parameter | Typical range (mobile) | Effect |
|---|---|---|
| Boxes | 1–2 teach, 3–4 mid, 5+ hard | Difficulty rises steeply with each box |
| Free floor cells | Small rooms are often harder than large ones | Tight space creates dead ends |
| Goal placement | Corners and walls are easier; open-floor goals harder | Pushing into open space needs more planning |
| Dead squares | Cells where a box can never reach a goal | Count them; high counts mean many traps |

### Sliding tiles
`layout.type: sliding`, integer grid with `0` as the blank, optional `goal`.

| Size | Character |
|---|---|
| 2×3, 3×3 | Approachable; 3×3 optimal solutions ≤ 31 moves |
| 3×4, 4×4 | Hard for casual players; offer hints |
| Picture tiles | Easier than numbers for casual players (gestalt cues) |

Always check the parity invariant before searching; half of arrangements are unreachable.

### Lights Out
`layout.type: lights_out`, grid of 0/1.

| Parameter | Effect |
|---|---|
| Grid size | 3×3 to 5×5 on phones; larger grids get tedious |
| Toggle pattern | Classic is plus-shaped; variants (diagonals, wrap-around) change solvability |
| Start pattern | Generate by pressing random cells from the solved state, which guarantees solvability |

Solve exactly with linear algebra over GF(2) or with BFS on small grids. Generating by random presses from all-off guarantees a solvable pattern.

### Flow / connect pairs
| Parameter | Effect |
|---|---|
| Grid size | 5×5 teach to 9×9+ hard; must respect cell-size formula on phones |
| Pairs | More pairs per area means more interaction |
| Fill-every-cell rule | Turns the puzzle into a deduction puzzle; usually paired with a unique solution |

### Nonogram
| Parameter | Effect |
|---|---|
| Grid size | 5×5 to 15×15 on phones; larger needs zoom |
| Line-solvability | Required for casual; dedicated players accept some lookahead |
| Clue density | Long runs make easier deductions |

### Sudoku family
| Parameter | Effect |
|---|---|
| Givens | ≥ 17 for a unique classic solution; more givens is generally easier but not reliably |
| Hardest technique required | The real difficulty grade |
| Variant rules (killer, thermo) | New deduction types; teach each separately |

### Casual physical and tray puzzles
| Family | Key knobs | Verification |
|---|---|---|
| Screw / pin | Holding slots, colour order of boxes, plate layering | State-space solver on the abstract model (which screws are free) |
| Pin pull | Pin order dependencies, liquids, hazards | Physics simulation runs; check every pin order |
| Tile-match tray (triple) | Tray slots, item types, occlusion depth | Solver over the occlusion graph; random-bot win rate |
| Block placement | Piece-mix weights, grid size, "guarantee a fit" rule | Bot runs measuring survival length |

See `mechanics-codex` (`references/03-puzzle-mechanics.md`) for the rules of each family and `genre-playbooks` (`references/puzzle.md`) for genre economics.

## 13. Worked example: a sort level from brief to verified spec

**Brief.** World 3, level 7, role *test*: "Spend the empty tubes carefully: the obvious early pours fill both empty tubes and dead-end." Target first-try win rate 0.55, attempts p50 2. 6 colours, capacity 4, 2 empty tubes, `max` pour. Move limit planned at about 1.4× optimum.

**Steps.**
1. Generate candidate deals with a seeded RNG: shuffle 6 colours × 4 items into 6 full tubes plus 2 empty tubes, and write each as a level-spec file (or design a few deals by hand).
2. Solve each candidate:
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/puzzle_solver.py --level cand_0006.level.json --algo bfs --max-nodes 200000 --json
   ```
3. Measure a greedy bot (prefers pours onto a matching top and pours that complete a tube, random tie-break) at the planned limit, 200 runs.
4. Filter: `min_moves` in 15–19 and greedy-bot win rate at the planned limit in 0.2–0.5. Until a bot-to-human calibration exists (section 7), this band is a stand-in for "planning required but not opaque".
5. Prefer the candidate whose opening offers a tempting pour into an empty tube.
6. Set the limit to `round(1.4 × min_moves)` and record the results. Store the human target in `difficulty_target.win_rate` and the provisional bot-space target in `difficulty_target.bot_win_rate` (an extra field the schema allows); `level_audit.py` compares the bot result against the bot-space target when it is present.

**What the numbers looked like.** A scratch run of 600 seeded random deals in this configuration (BFS with the same sort rules as `puzzle_solver.py`, tube order canonicalised) found **every deal solvable**, with optimal lengths from 12 to 22 moves, most of them 16–20. So for this configuration, random-plus-filter rejects on *difficulty*, not on solvability; with fewer empty tubes or more colours, re-measure, because unsolvable deals appear. 56 of the 600 deals passed the filter in step 4. The chosen deal:

```json
{
  "schema_version": "1.0",
  "level_id": "w3_l007",
  "mechanic_refs": ["sort_pour"],
  "layout": {"type": "sort", "capacity": 4, "pour": "max",
             "tubes": [["b","e","f","d"],["d","a","f","c"],["e","e","c","d"],
                       ["a","a","c","f"],["e","b","a","b"],["b","d","f","c"],[],[]]},
  "goals": [{"type": "sort_all", "target": null, "count": 6}],
  "moves_or_time_limit": {"moves": 25},
  "obstacles": [],
  "difficulty_target": {"win_rate": 0.55, "attempts_p50": 2, "bot_win_rate": 0.35},
  "solver": {"solvable": true, "min_moves": 18, "bot_win_rate": 0.34, "runs": 200,
             "algo": "bfs", "states_visited": 3511,
             "bot": "greedy (matching-top and completion first, random tie-break), seed 1, 25-move limit"},
  "teach": "test",
  "notes": "Greedy bot wins 34% at 25 moves and only 54% even at 36 moves, so its failures are dead ends, not the limit: the level tests planning with empty tubes. difficulty_target.bot_win_rate 0.35 is the centre of the provisional bot band until a bot-to-human calibration exists. Re-run puzzle_solver.py after any edit."
}
```

7. Run `level_audit.py audit --dir .gamestudio/levels` to check the level in context: it must not sit next to another hard level, and an earlier level using `sort_pour` should have been a *teach*.
8. Playtest with 5 persona runs or human testers. Expected: several fill both empty tubes early and stall, then restart and plan. If testers win first try more than about 80% of the time, the level is easier than the target: remove one empty-tube-friendly opening or pick a candidate with a lower bot rate.

Note that the greedy bot's win rate barely moved when the limit grew from 25 to 36 moves. When extra slack does not help a bot, difficulty comes from dead ends, and the levers are empty tubes, colours and undo policy, not the move limit.

## 14. Puzzle level review checklist

**Design**
- [ ] The insight and the false assumption it breaks are written in `notes`.
- [ ] Exactly one primary insight (two only in deliberate exam levels).
- [ ] The minimal configuration was found first; noise was added deliberately for the audience.
- [ ] The opening read is plausible and fails informatively (or succeeds, for teach levels).

**Verification**
- [ ] `solver.solvable` is true from `puzzle_solver.py` or a purpose-built solver; budget exhaustion is recorded as unknown, not unsolvable.
- [ ] `moves_or_time_limit` ≥ `min_moves`, with slack inside the role's band.
- [ ] Every shortest solution uses the intended key move (no shortcuts), or the level is casual and does not need one.
- [ ] Greedy-bot versus optimal gap matches the role (small for teach, large for twist).
- [ ] Dead-end density and trap count are acceptable for the undo policy.
- [ ] Logic puzzles: unique solution; casual nonograms are line-solvable.
- [ ] Symmetric duplicates of shipped levels are excluded (canonical hash).

**Player support**
- [ ] Stuck detection is configured; the hint ladder works from any reachable state.
- [ ] Restart is free and instant; dead ends are visible within 1–2 moves or undo is free.
- [ ] The level is solvable without paying.

**Mobile**
- [ ] Cell size meets the target for the smallest supported screen; ≤ 6 colours at once or colour plus symbol coding.
- [ ] State persists every move; resume restores exactly.
