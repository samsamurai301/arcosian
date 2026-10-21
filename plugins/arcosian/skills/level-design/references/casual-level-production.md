# Casual Level Production (Match-3, Blast and Friends)

How to design, tune and mass-produce levels for match-3 (swap), blast (tap-to-collapse) and neighbouring casual formats, where a live game needs hundreds or thousands of levels on a predictable difficulty curve. It covers the anatomy of a level, goal and blocker taxonomies, board shapes, move limits, spawn rates, the effect of colour count (with measured numbers), a difficulty-lever table and how to calibrate it, the production line for hundreds of levels, ordering levels into a curve, A/B testing levels, live tuning, and how to drive `match3_sim.py`. Genre economics and KPIs are in `genre-playbooks` (`references/puzzle.md`); landmark titles are in `game-case-studies` (`references/puzzle-casual.md`); deterministic puzzles (sort, screw, Sokoban) are in `puzzle-level-design.md`.

## Contents

1. The production problem: content burn
2. Anatomy of a match-3 level
3. Goal taxonomy
4. Blocker taxonomy
5. Board shapes
6. Move limits
7. Spawn rates and fairness
8. Colour count: the strongest lever (measured)
9. Difficulty-lever table and calibration
10. Blast / collapse specifics
11. Producing hundreds of levels
12. Ordering levels into a curve
13. A/B testing levels
14. Live tuning and problem levels
15. Driving match3_sim.py
16. Worked example: one world of 20 levels
17. Production checklist
18. Volatile facts

---

## 1. The production problem: content burn

A saga-style casual game is a content treadmill: engaged players consume levels faster than designers make them. Plan production from consumption, not from ambition.

```
weekly_consumption(P) = levels_per_day(P) × 7
runway_weeks(P)       = (total_levels − current_level(P)) / weekly_consumption(P)
weekly_production     ≥ weekly_consumption(P_target)
```

Where `P` is a player percentile (for example the 90th percentile of progress speed among active players) and `P_target` is the percentile you commit to never letting run out of content.

**Worked example (hypothetical numbers).** At soft launch you ship 300 levels. Telemetry shows that the 90th-percentile active player clears 18 levels a day in week 1 and about 8 a day afterwards as difficulty rises. Week 1 consumes 126 levels; the remaining 174 last 174 / 8 ≈ 22 days. That player runs out of content in about 29 days, and keeping them supplied needs 8 × 7 = 56 new levels a week. King ships Candy Crush levels in 15-level episodes (see volatile facts); a small team typically cannot match that by hand, which is why section 11 is a pipeline, not a craft process.

**Levers when production cannot keep up:**
- Raise difficulty gradually in late game (slower consumption) — only if churn data allows it.
- Add replayable content that does not consume levels: events, daily challenges, leaderboards, collections (`liveops`).
- Use procedural or template levels for side modes, keeping handcrafted levels for the main path.
- Show a clear "new levels on <day>" state at the end of content; players who see a date are more likely to return than players who see nothing (design hypothesis; measure).

## 2. Anatomy of a match-3 level

| Part | What it is | Level-spec home |
|---|---|---|
| Board | Cells, holes, spawners, exits, gravity direction | `layout` (`type: match3`, `rows` or `grid`, `width`/`height`, `legend`) |
| Colours | Number of tile colours that can spawn | `layout.colors` |
| Goals | What must be collected or cleared | `goals` |
| Moves | Move limit (or time limit for timed modes) | `moves_or_time_limit` |
| Blockers | Covers, overlays, cell blockers, spreaders, generators | `obstacles` plus `layout.legend` codes |
| Pre-placed specials | Specials on the board at start | `layout` codes plus `legend` |
| Spawn rules | Colour weights, drop-item frequency | `notes` or a custom field such as `spawn` (schema allows extra properties) |
| Difficulty target | Designed first-try win rate and attempts | `difficulty_target` |
| Bot results | Bot win rate and runs | `solver` |
| Role | teach / test / twist / reward | `teach` |

Use a stable legend across the whole game (`.` random tile, `#` hole, letters for fixed colours, other codes for blockers) and keep it in one shared file that the editor, the simulator and the engine all read.

## 3. Goal taxonomy

| Goal | Mechanism | Player strategy | Difficulty character | Sim needs |
|---|---|---|---|---|
| Collect N of colour X | Matches of X count | Prioritise X; specials that hit many X | Smooth; sensitive to colour count | Count matched tiles by colour |
| Clear all covers | Match on top of every covered cell | Work toward corners and isolated cells | Back-loaded: the last few cells are the hardest | Track covered cells; specials reach |
| Drop items | Bring items down to exits | Clear the columns under items | Depends on board shape and exits | Item physics and exits |
| Free caged or locked tiles | Match the locked tile | Target specific cells | Positional; plays like covers | Overlay state |
| Collect hidden objects | Clear covers to reveal pieces | Uncover whole shapes | Back-loaded; luck in reveal order | Object footprints |
| Destroy N blockers | Hit boxes, stones and similar | Adjacent matches and specials | Positional | Blocker HP |
| Score | Reach a score | Big combos | Low-skill fallback; rarely used in modern games | Score model |
| Spread / paint | Turn every cell into a state by matching | Spread from existing coloured areas | Positional and back-loaded | Spread rules |
| Boss / HP | Damage a target with matches or specials | Charge and fire specials | Smooth, legible progress bar | Damage model |

**Rules**
- **One or two goals per level** in early game; three in late game at most. Every extra goal multiplies failure modes.
- **Back-loaded goals** (clear all covers, hidden objects) create "1 left" losses. They are powerful for near-miss tension and dangerous for frustration; check the moves-left distribution (section 6).
- **Goal counts are a fine-tuning lever**: "collect 40 red" to "collect 45 red" is a small, predictable step.

## 4. Blocker taxonomy

Generic class names are used here; each game gives them its own fiction.

| Class | Examples (generic) | Rule | HP / layers | Interaction with specials | Effect on difficulty | Readability rule |
|---|---|---|---|---|---|---|
| Cover (under tile) | Jelly, grass, carpet | Cleared by a match on top | 1–2 layers | Cleared by special blasts | Positional; back-loaded | Layer count visible (two tints) |
| Overlay (on tile) | Ice, chains, locks | Tile is matchable or not movable; overlay breaks on match | 1–3 | Specials break overlays | Reduces swap options locally | Distinct silhouette, not just tint |
| Cell blocker | Boxes, stones, crates | Occupies the cell; broken by adjacent match | 1–5 | Specials hit it | Blocks gravity and space; strong | Crack stages show HP |
| Colour blocker | Coloured boxes | Only adjacent matches of its colour damage it | 1–3 | Specials hit it | Couples with colour count; strong | Colour plus symbol |
| Indestructible | Walls, pillars | Never cleared | — | — | Shapes the board permanently | Clearly different material |
| Spreader | Slime, chocolate, moss | Grows each turn no adjacent instance was cleared | 1 | Specials clear it | Pressure over time; punishes slow play | Animate growth so cause is clear |
| Generator | Pipes, hives | Spawns items or blockers periodically | Often indestructible or high HP | Some are damaged by specials | Adds sustained pressure | Show the spawn timer |
| Bomb / timer | Countdown tiles | Lose if counter reaches 0 | — | Clearing removes it | Sharp pressure; creates priority | Big readable number |
| Collectable drop | Ingredients, keys | Must reach an exit | — | Specials below help | Board-flow dependent | Exit arrows visible |
| Mover | Conveyors, portals, gravity changers | Move tiles each turn or redirect gravity | — | — | Raises planning load; reduces luck predictability | Arrows; preview the next movement |
| Link / chain group | Linked tiles | Must be cleared together | — | — | Positional | Visible links |

### Blocker rules
- **Teach each blocker in isolation** (teach level), with a goal that requires interacting with it, then test, then twist with one known blocker (`principles.md` section 2).
- **Readability first.** HP and layer count must be visible at a glance on a 375-pt-wide screen; crack stages or numerals beat tint differences.
- **Specials must interact predictably.** Document for every special × blocker pair what happens. With S special types and B blocker types there are S×B interactions; every one needs a defined rule, an animation and a test.
- **Spreaders and generators change the tempo.** Use them sparingly; they convert a planning puzzle into a race.
- **Never use a blocker the bot cannot simulate.** If `match3_sim.py` does not model a blocker, the level cannot pass the bot gate; either extend the simulator in the game project or record results from the engine's own headless bot.

## 5. Board shapes

| Shape pattern | Description | Effect | Use for |
|---|---|---|---|
| Open rectangle (7×7 to 9×9) | Full board, few holes | Maximum cascades and options | Teach, reward |
| Hourglass / neck | Narrow middle section | Cascades rarely cross the neck; the far side is hard to reach | Twist; drop-item levels |
| Pockets | Small isolated areas | Hard to reach without specials | Late-game clear-all levels; use 1–2 pockets max |
| Columns / stripes | Vertical strips separated by holes | Gravity per strip; fewer horizontal matches | Variety, drop items |
| Split boards | Two boards connected by gravity or portals | Two mini-puzzles | Late game, variety |
| Top-heavy | Wide top, narrow bottom | Spawns are plentiful, matches funnel down | Drop items |
| Islands with spawners | Spawners only on some columns | Refill only where spawners exist | Positional difficulty |
| Symmetric shapes | Mirrored layouts | Read as intentional; calmer | Most levels (asymmetry signals "special") |

**Board rules**
- Every cell must be reachable by falling tiles or by specials. Isolated cells with no spawner above them and no special path become softlocks for clear-all goals.
- Drop-item levels need exits under every column an item can enter, or obvious routes to them.
- Smaller boards read better on phones but cascade less; compensate with fewer colours or more moves.
- Keep the board inside the safe area with the HUD at top (goals, moves) and boosters at the bottom (`mobile-ux`).
- Portrait 9 columns at 375 pt gives about 39-pt cells (`principles.md` section 11); do not exceed 9 columns in portrait.

## 6. Move limits

### Setting the limit from the bot
For a stochastic game there is no optimum; use the bot's distribution of moves-to-win on an unlimited (or very large) limit.

```
moves_limit = ceil( Q_q(moves_to_win) )
```

where `Q_q` is the q-th quantile of the bot's moves-to-win distribution. Choose q from the target win rate after mapping bot to human (section 9). If the bot is roughly human-strength for this game, `q ≈ target_win_rate`: a level whose limit is the bot's 60th percentile of moves-to-win is won by about 60% of bot runs.

Practical alternative used by many teams: start at the bot's median moves-to-win × 1.10–1.25 (puzzle playbook heuristic), simulate, then step the limit by ±1–2 moves until the bot win rate sits in the target band.

### Slack bands by role (heuristic; calibrate)
| Role | Bot win rate band at the limit (before human calibration) |
|---|---|
| teach | ≥ 0.95 |
| reward | 0.85–0.95 |
| test | 0.55–0.80 |
| twist | 0.40–0.65 |
| hard spike | 0.20–0.45 |
| super-hard (rare, flagged in UI) | 0.10–0.25 |

### The moves-left distribution
Look at the distribution of moves remaining on wins and goal remaining on losses:
- **Wins with 0–2 moves left**: near-miss wins, exciting. If more than about half of wins land here, the level feels rigged; add a move.
- **Losses with 1 goal unit left**: near-miss losses, the strongest "+5 moves" moment. If they dominate losses, the level is tuned for monetization pressure; check against ethics (doctrine 8) and churn.
- **Losses with most of the goal left**: the player never had a chance; the level is too hard or too luck-dependent.

## 7. Spawn rates and fairness

| Spawn control | Purpose | Default |
|---|---|---|
| Colour weights | Bias toward or away from colours | Uniform; bias only with a documented reason (e.g. collect-goal colour slightly up in teach levels) |
| Drop-item spawn | When ingredients or keys appear | Fixed schedule or "spawn when fewer than N on board" |
| Special pre-placement | Generosity | Teach and reward levels |
| Initial board | Fixed, seeded or random | Fixed or seeded for the first 20–50 levels (repeatable experience); seeded random later |
| Deadlock shuffle | Guarantee at least one valid move | Always on; shuffle with a visible animation |
| Anti-match on spawn | Avoid spawning ready-made matches at start | On for the initial board; off for refills (cascades are the fun) |

### Fairness and ethics
- Spawn behaviour must be **the same for all players** at the same level, or the difference must be disclosed as part of a transparent assist feature. Do not secretly rig spawns per player to push purchases (`legal-ethics`, `monetization`).
- **Dynamic difficulty, if used, only helps** (e.g. after repeated failures), is bounded, is applied before the attempt (not mid-move), and is documented internally (`progression-difficulty`).
- Players notice patterns: a level that "always gives the colour you need after you buy moves" reads as manipulation even if accidental. Bot-test the continue flow with the same spawn rules as the base attempt.

## 8. Colour count: the strongest lever (measured)

For a uniformly random fill with C colours, the chance that three given cells share a colour is 1/C², so spontaneous matches scale roughly with 1/C². Going from 5 to 6 colours multiplies that by (5/6)² ≈ 0.69. A simulation shows the effect on real play quantities.

**Scratch Monte Carlo** (this skill's authors; 9×9 full board, uniform spawns, initial board generated without matches, no specials or blockers, one random valid swap then full cascade resolution; 1,500 boards per colour count):

| Colours | Valid swaps on a fresh board (mean) | P(move causes ≥ 1 cascade) | Cascade rounds per move (mean) | Tiles cleared per move (mean) |
|---|---|---|---|---|
| 4 | 36.6 | 0.67 | 1.91 | 14.0 |
| 5 | 25.5 | 0.50 | 0.94 | 7.5 |
| 6 | 19.0 | 0.40 | 0.63 | 5.7 |
| 7 | 14.6 | 0.29 | 0.40 | 4.7 |

Reading it:
- **4 → 5 colours roughly halves tiles cleared per move** (14.0 → 7.5): the single biggest difficulty step in the genre.
- **5 → 6 colours** cuts valid swaps by about a quarter and tiles cleared per move by about a quarter.
- Use 4 colours only for teach and reward levels; 5 is the workhorse; 6 for hard levels; 7 is rare and needs generous moves. This matches the genre convention of 4–6 colours (`genre-playbooks`).
- These numbers ignore specials, blockers and board shape. Re-measure with `match3_sim.py` on your rules; treat the table as orientation, not as constants.

## 9. Difficulty-lever table and calibration

| Lever | Raise difficulty by | Relative strength | Granularity | Side effects | Prefer when | Avoid when |
|---|---|---|---|---|---|---|
| Colour count | +1 colour | Very strong | Coarse (one step ≈ large win-rate change) | Fewer cascades, less spectacle | Big spikes; world-level shifts | Fine-tuning |
| Move limit | −1 to −3 moves | Strong, smooth | Fine | More near-miss losses | Final tuning of almost every level | Already near-miss-heavy levels |
| Goal count | +5–10% of the count | Medium, smooth | Fine | Longer levels | Fine-tuning collect goals | Back-loaded goals |
| Blocker HP | +1 layer | Medium | Medium | Slower pace | Positional levels | Teach levels |
| Blocker density | +5–10% of cells | Medium to strong | Medium | Fewer free cells, fewer cascades | Twist and hard levels | Small boards |
| Board area | −1 row or column, more holes | Medium | Coarse | Fewer options; better readability | Variety | Already cramped boards |
| Board shape (necks, pockets) | Add a neck or pocket | Strong, positional | Coarse | Specials become mandatory | Hard and twist | Teach and reward |
| Spreader / generator | Add one | Strong, tempo | Coarse | Turns planning into a race | Variety spikes | Early game |
| Drop-item count or exits | More items or fewer exits | Medium | Medium | Column-focused play | Drop levels | — |
| Pre-placed specials | Remove them | Medium | Fine | Less spectacle | Fine-tuning | Teach levels |
| Spawn bias | Toward non-goal colours | Strong and invisible | Fine | Feels unfair if noticed | Never as a hidden per-player lever | Always for per-player rigging |

### Calibrating the levers for your game (elasticity sweep)
The relative strengths above are qualitative. Measure them:
1. Pick 10–20 representative levels (one per role and blocker family).
2. For each lever, create copies with the lever moved one step each way (e.g. moves −2, +2; colours −1, +1).
3. Run `match3_sim.py --level <copy> --runs 1000 --bot greedy --seed 1 --json` on each.
4. Record Δ bot win rate per step: that is the lever's **elasticity** for your rules.
5. Store the table in the project (e.g. `.gamestudio/levels/elasticity.json`) and use it to tune new levels in one or two iterations instead of five.

**Run counts.** A bot win rate from n runs has a standard error of about √(p(1−p)/n). At p = 0.5: n = 200 gives ±3.5 points (1 s.e.), n = 500 gives ±2.2, n = 1,000 gives ±1.6. Use at least 500 runs when tuning to a ±5-point band at 95% confidence (1.96 × 2.2 ≈ 4.4 points).

### Mapping bot to human
Bots are not humans: a greedy bot is often weaker than a good player at planning and stronger at noticing every valid move. Build a mapping once you have human data:
1. For 30–100 levels, collect human first-try win rate (playtest or soft launch) and bot win rate.
2. Fit `logit(human) = a + b · logit(bot)` (a two-parameter logistic map) per bot type.
3. Invert it to convert human targets into bot targets for all future levels, and store each converted target in `difficulty_target.bot_win_rate` so `level_audit.py` compares like with like.
4. Refit monthly. King has reported that simulating several player strategies predicts difficulty better than a single strategy (volatile facts); if you have more than one bot, fit on all of them.

## 10. Blast / collapse specifics

Blast games (tap a group of adjacent same-colour cubes to clear it) share most of match-3's level design, with these differences:

| Topic | Blast difference |
|---|---|
| Move | Tap a group of size ≥ 2 (genre standard); no swap; every group is a legal move |
| Skill expression | Choosing which group to pop to grow large groups for specials |
| Specials | Created by popping large groups; commonly reported thresholds in Toon Blast–style games are 5, 7 and 9 cubes for successively stronger specials (verify against your reference build) |
| Colour count | Even stronger lever than in match-3, because large groups (specials) depend on colour density |
| Move limit | Usually lower counts than match-3 (each tap can clear more) |
| Dead boards | Rare (any pair is a move), but "no good move" states are common at high colour counts |
| Bot | `match3_sim.py` with a blast rule if supported; otherwise a game-side bot (largest-group-first greedy is a reasonable baseline) |

Lever priority in blast: colour count, minimum group size (rarely changed after launch), special thresholds (global, not per level), move limit, blocker density.

## 11. Producing hundreds of levels

A production line, not a craft studio. Each stage has an owner (designer, generator, bot, reviewer) and a gate.

```
Archetype library → Parameterised generation → Designer pass → Bot gate → Tag & bucket → Slotting → Review → Ship → Telemetry → Recalibrate
```

### Stage 1: archetype library
Write 20–40 **archetypes**: reusable level ideas with a parameter range.

```yaml
archetype: neck_drop
idea: "Drop items must pass through a 3-wide neck; specials above the neck are the key."
board: hourglass 9x9, neck width 3
goals: drop 2–4 items
colors: 5–6
blockers: boxes 0–6 above neck (1–2 HP)
roles: test, twist
mechanic_refs: [drop_items, boxes]
```

### Stage 2: parameterised generation
Generate 5–20 variants per archetype by sampling the parameter ranges with a seeded RNG (write them as level-spec files). Shapes can come from a template set or `pcg.py` (e.g. `pcg.py noise --w 9 --h 9 --seed 42 --json` thresholded into holes; `level-pipeline.md` section 9), with the rule that generated holes must not create unreachable cells.

### Stage 3: designer pass
A designer (human or the `arcosian:level-designer` agent) curates: rejects ugly or unreadable boards, adjusts symmetry, places the key blocker clusters, writes `notes` with the intent. Curation rate matters more than generation rate.

### Stage 4: bot gate
Run `match3_sim.py` (500–1,000 runs). Reject or retune until the bot win rate (after bot-to-human mapping) is within ±5 points of the target band for the role. Record `solver.bot_win_rate` and `solver.runs`.

### Stage 5: tag and bucket
Tag each level with: archetype, mechanic_refs, goal types, blocker set, colour count, measured difficulty, duration estimate (bot moves × seconds per move), layout hash. Buckets: difficulty band × mechanic set.

### Stage 6: slotting (section 12)

### Stage 7: review
Spot-check levels in the engine on a low-end phone: readability, animation pacing, goal clarity. Run `level_audit.py audit` on the ordered set. A human signs off each world (taste checkpoint, doctrine 10).

### Throughput maths
```
levels_shipped_per_week = generated × pass_rate_designer × pass_rate_bot × pass_rate_review
```
If generation produces 400 candidates a week and the pass rates are 0.3, 0.5 and 0.9, you ship 54 levels a week. The bottleneck is usually the designer pass; invest in editor ergonomics (one-click "regenerate this region", live bot win rate in the editor) before more generators.

### Variety rules (enforced by the audit or the slotter)
- No identical layout hashes in the game.
- In any window of 10 consecutive levels: at least 3 goal types or goal combinations; no more than 3 levels of the same archetype; at least one reward level.
- A new blocker or goal type every 10–20 levels in a live game (genre convention).

## 12. Ordering levels into a curve

### Target curve
Generate per-slot targets:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/difficulty_curve.py generate --levels 100 --pattern sawtooth --base 0.92 --floor 0.40 --period 8 --hard-every 10 --json
```
Each slot gets a target win rate; hard slots are flagged.

### Slotting algorithm
Assign bucketed levels to slots so that every constraint holds and the total deviation from target is minimal.

```text
inputs: slots[1..N] with target win rate t_i and role r_i
        pool of verified levels with predicted win rate w_j, mechanics M_j, tags
constraints:
  C1 a mechanic's first appearance is in a slot with role teach
  C2 at most one new mechanic per slot
  C3 every mechanic has a test slot before any twist slot that uses it
  C4 variety rules (section 11)
  C5 hard slots are followed within 2 slots by a reward or a slot with t ≥ t_hard + 0.15
procedure (greedy with repair):
  for i in 1..N:
     candidates = pool levels satisfying C1–C4 given slots[1..i−1]
     pick j minimising |w_j − t_i| + penalty(tags repetition)
     if none: insert a placeholder and request an archetype that fits (back to Stage 2)
  run level_audit.py on the result; fix violations by swapping adjacent compatible levels
```

For large pools, the assignment step can be solved optimally as a min-cost assignment (Hungarian algorithm) per world, with the constraints enforced by filtering candidate pairs. Greedy with repair is usually good enough.

### Ordering rules of thumb
- The first 10–20 levels: very high win rates (close to unlosable), one new element every 2–3 levels, short.
- First real failure is a designed moment: put it after players have formed a habit (several sessions), and make the fail screen helpful (show progress, offer retry).
- Hard spikes at regular, predictable intervals (e.g. every 8–12 levels), marked in the UI ("Hard level") so failure feels expected, not unfair.
- Do not place two hard levels within 3 slots of each other.
- End each world or episode on a satisfying (not brutal) level.

## 13. A/B testing levels

Test level changes like any product change: hypothesis, primary metric, guardrails, sample size, fixed duration.

### What to test
- Move limit or goal-count changes on a problem level.
- Replacement levels (new layout in the same slot).
- Order changes (swap two levels).
- Difficulty curve variants for a whole range (e.g. levels 40–80).

### Metrics
| Type | Metric | Definition |
|---|---|---|
| Primary (level) | Pass-through rate | Share of players who start level L and reach level L+1 within N days (e.g. 7) |
| Primary (range) | Progression depth | Mean or median max level reached by day N |
| Secondary | Attempts p50, first-try win rate | As in `level-pipeline.md` section 12 |
| Secondary | Level churn | Share of players whose last-ever session ended on the level |
| Guardrail | D7 and D30 retention of the cohort | Must not drop |
| Guardrail | Revenue per player in the cohort | Report, do not optimise blindly |
| Guardrail | Booster and continue spend | Large increases may signal over-hard tuning |

**Ethics.** Do not choose the variant that makes more money by being harder if it raises churn or frustration markers; the doctrine puts the player first (`monetization`, `legal-ethics`).

### Sample size
Assign at the player level, only for players who reach the level (randomise on entering the level range so arms are comparable). For a pass-through rate baseline of 0.80 and a minimum detectable improvement of 2 points (0.80 → 0.82), α = 0.05 two-sided, power 0.8:

```
n per arm ≈ (z₀.₉₇₅ + z₀.₈)² · [p₁(1−p₁) + p₂(1−p₂)] / (p₂ − p₁)²
          = (1.96 + 0.84)² · (0.16 + 0.1476) / 0.0004 ≈ 6,000 players per arm
```

Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ab_test.py size --baseline 0.80 --mde 0.02 --two-sided` for the exact figure, and `ab_test.py analyze --a-success X --a-n N --b-success Y --b-n M --json` afterwards. For small games, test bigger changes (larger MDE) or test whole ranges, because per-level traffic shrinks with depth.

### Pitfalls
- **Survivorship.** Players deep in the game are not representative; results at level 400 do not transfer to level 40.
- **Interference.** Two concurrent tests on overlapping level ranges contaminate each other; keep tests on disjoint ranges or use a factorial design.
- **Peeking.** Decide the duration up front, or use a sequential design (`ab_test.py sequential --baseline P --mde D --looks K`).
- **Delayed effects.** A harder level can raise short-term spend and lower 30-day retention; keep the guardrails running long enough to see it.

## 14. Live tuning and problem levels

### Finding problem levels
Flag a level when any holds (thresholds are starting points):
- Level churn more than about 2× the median of its neighbours.
- First-try win rate more than 10–15 points below its target.
- Attempts p90 above about 3× the target attempts p50.
- A sudden change after a client update (simulation or spawn regression).

Use `difficulty_curve.py analyze --data levels.csv --json` with a CSV of `level,attempts,wins,churned` to spot outliers.

### Fixing
| Symptom | Likely cause | First fix |
|---|---|---|
| High churn, low win rate | Too hard | +2–3 moves (remote config) |
| High churn, normal win rate | Long, boring or confusing level | Shorten goals; clarify the goal UI; check for a misleading signifier |
| Many losses with 1 goal unit left | Back-loaded goal | Reduce the goal count by 1–2 units or make the last cells reachable |
| Many losses with most of the goal left | Luck-dominated or unreadable | Fewer colours; remove a pocket |
| Win rate fine, booster use very high | Hidden difficulty bought away | Treat as too hard; tune down |

### Remote config
Keep move limits, goal counts and colour counts remotely tunable per level (with a version stamp) so fixes do not need a client release. Record every live change in the level file's `notes` and in `.gamestudio/progress.md`; keep `level_id` stable so analytics remain comparable.

## 15. Driving match3_sim.py

CLI (binding, BLUEPRINT section 14):
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/match3_sim.py --level PATH [--runs N=500] [--bot greedy|random|cascade] [--seed S] [--json]
```

| Bot | Behaviour (by name; check `--help` for the exact policy) | Use |
|---|---|---|
| `random` | Picks any valid move | Lower bound; luck baseline |
| `greedy` | Picks the move with the best immediate value | Main reference bot; most levels are tuned against it |
| `cascade` | Favours moves that set up cascades or specials | Skilled-player proxy |

**Recipes**

```bash
# single level, reference bot
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/match3_sim.py --level .gamestudio/levels/w2_l014.level.json --runs 1000 --bot greedy --seed 1 --json

# skill spread: random vs greedy vs cascade (large gaps mean skill matters)
for b in random greedy cascade; do
  python3 ${CLAUDE_PLUGIN_ROOT}/scripts/match3_sim.py --level L.level.json --runs 500 --bot $b --seed 1 --json > sim_$b.json
done

# move-limit sweep: copy the level with different limits and simulate each
for m in 18 20 22 24 26; do
  python3 - "$m" <<'PY'
import json, sys
m = int(sys.argv[1]); d = json.load(open("L.level.json"))
d["moves_or_time_limit"] = {"moves": m}; d["level_id"] += f"_m{m}"
json.dump(d, open(f"sweep_m{m}.level.json", "w"), indent=2)
PY
  python3 ${CLAUDE_PLUGIN_ROOT}/scripts/match3_sim.py --level sweep_m$m.level.json --runs 500 --bot greedy --seed 1 --json > sweep_m$m.json
done
```

Interpreting:
- Write the reference bot's win rate and run count into `solver.bot_win_rate` and `solver.runs` (add `bot`, `seed` and any other output fields as extra properties; the schema allows them).
- Always use a fixed seed for reproducibility; change the seed to check stability (two seeds disagreeing by more than about 2 standard errors means too few runs).
- **Random ≈ greedy** means the level is luck-dominated: add structure (blockers, shape) or reduce colours.
- **Greedy ≈ 1.0 with a tight limit** means the limit is not binding; the level is a reward whether you meant it or not.
- If the simulator does not support a blocker or goal the level uses, it should say so; do not ship numbers from a simulation that ignored part of the level.

## 16. Worked example: one world of 20 levels

Inputs: world 3, introduces **chains** (overlay: tile cannot move; breaks on match). Known: boxes, covers, drop items. Colours: 4–6. Targets from `difficulty_curve.py` (sawtooth, period 8) with hard slots at 10 and 18.

| Slot | Role | Target first-try win | Archetype | Mechanics | Colours | Notes |
|---|---|---|---|---|---|---|
| 1 | teach | 0.97 | open_square | chains | 4 | 6 chains on the centre row; goal: break 6 chains |
| 2 | test | 0.85 | open_square | chains, covers | 5 | Chains on covered cells |
| 3 | reward | 0.92 | stripes | covers | 4 | Breather; pre-placed specials |
| 4 | test | 0.75 | pockets | chains | 5 | Chains guard two pockets |
| 5 | twist | 0.62 | neck_drop | chains, drop items | 5 | Chained tiles in the neck block drops |
| 6 | test | 0.72 | open_square | boxes, chains | 5 | Mixed |
| 7 | reward | 0.90 | symmetric | chains | 4 | Chain showcase, many line specials |
| 8 | test | 0.65 | columns | covers, drop items | 5 | Variety |
| 9 | test | 0.60 | hourglass | chains, boxes | 5 | Ramp |
| 10 | twist (hard) | 0.38 | pockets | chains, boxes, covers | 6 | Flagged "Hard" in UI |
| 11 | reward | 0.90 | open_square | drop items | 4 | Relief |
| 12–17 | test/twist mix | 0.55–0.75 | mixed | known set | 5 | Variety rules apply |
| 18 | twist (hard) | 0.35 | split board | chains, drop items | 6 | Second spike |
| 19 | reward | 0.92 | symmetric | chains | 4 | Relief |
| 20 | test | 0.70 | open_square | chains, covers | 5 | World finale: satisfying, not brutal |

Pipeline: generate 10 variants per slot from the archetype library, bot-gate them (`match3_sim.py`, 1,000 runs, greedy, seed 1), slot the closest to target, run `level_audit.py audit --dir .gamestudio/levels/w3`, review on a low-end phone, sign off.

## 17. Production checklist

**Per level**
- [ ] Brief: idea, role, target first-try win rate and attempts p50.
- [ ] Legend codes are from the shared legend; every blocker is supported by the simulator.
- [ ] Every cell reachable; drop items have exits; no softlock pockets.
- [ ] ≤ 6 colours (≤ 5 outside hard levels); ≤ 2 goals early, ≤ 3 late.
- [ ] Bot win rate (500+ runs, fixed seed) within ±5 points of the mapped target; `solver` fields filled.
- [ ] Moves-left distribution checked: not dominated by 0–1-move wins or 1-unit losses.
- [ ] Readable on a 375-pt-wide screen: HP visible, chains and locks distinct by silhouette.

**Per world**
- [ ] One new element per teach slot; test before twist; reward after each spike.
- [ ] Variety rules hold (goal types, archetypes, layout hashes).
- [ ] `level_audit.py audit` passes with no errors.
- [ ] Human taste sign-off recorded.

**Live**
- [ ] Move limits, goal counts and colours are remotely tunable with version stamps.
- [ ] Problem-level dashboard (churn, win rate vs target, attempts p90) reviewed weekly.
- [ ] Every live change logged in the level's `notes` and `progress.md`.

## 18. Volatile facts

As of Oct 2026 — verify before relying.

- King's human-like playtesting bot (a CNN trained on player moves) predicted level difficulty and had been in use for more than a year across more than 1,000 new Candy Crush Saga levels. Source: [Gudmundsson et al., 2018 (King)](https://www.Gwern.net/doc/reinforcement-learning/imitation-learning/2018-gudmundsson.pdf).
- Follow-up work with King reported difficulty estimates in under a minute, against 7 days of human playtesting per 15-level episode, and that simulating several player strategies improved prediction error (MAE about 13% better, MSE about 23%). Source: [Politecnico di Milano thesis (King collaboration)](https://www.politesi.polimi.it/handle/10589/141799).
- King AI Labs (2024) described a playtesting bot that automatically adjusts levels designers flag, against set criteria, with designers reviewing the best solutions. Source: [WN Hub, June 2024](https://wnhub.io/news/Generative_AI/item-43934).
- King has also described using MCTS, automatic heuristic construction and NEAT-based bots to predict success rates. Source: [StickyMinds talk](https://www.stickyminds.com/presentation/using-artificial-intelligence-test-candy-crush-saga-game).
- The Toon Blast–style special thresholds in section 10 are commonly reported, not confirmed from an official source in this session; check against the current build of any reference title.
