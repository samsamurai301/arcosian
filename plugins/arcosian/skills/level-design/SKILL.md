---
name: level-design
description: 'Level design codex: teach-test-twist-reward, kishōtenketsu, signposting, affordances, gating, pacing, flow, mobile readability, level metrics; puzzle aha and difficulty theory; match-3/blast production at scale; runner, survivor, platformer, arena and boss design; level-spec, solver gates, PCG and set audits. Use when asked to "design levels", "make 200 match-3 levels", "why does level 47 churn", "tune move limits" or "verify these levels".'
when_to_use: 'Designing, sequencing, tuning, generating or verifying levels, chunks, waves, encounters or bosses; writing .gamestudio/levels specs; diagnosing level churn.'
---

# Level Design

The studio's level-design layer: how to turn a mechanic into levels that teach, test and delight, how to sequence them into a difficulty curve, how to produce hundreds of them for a live casual game, and how to prove each one with a solver, a bot or a simulation before a player sees it. It treats a level as an argument about a mechanic with a measurable target (first-try win rate, attempts, duration) and treats a level set as a product with a curve, variety rules and live telemetry. Data lives in `.gamestudio/levels/*.level.json` (`level-spec.schema.json`); verification uses `puzzle_solver.py`, `match3_sim.py`, `pcg.py` and this skill's `scripts/level_audit.py`.

## What this skill gives you

- Genre-independent principles as checkable rules: one idea per level, teach–test–twist–reward, kishōtenketsu inside a level, signposting hierarchy, the affordance contract, gating types, intensity pacing, Lynch-style landmarks, risk/reward expected value, flow conditions, mobile readability formulas and capability metrics.
- Puzzle theory that produces decisions: the false-assumption model of the aha, design-backwards, constraints and slack bands, fair vs unfair obfuscation, solver-measurable difficulty factors with a calibratable composite, uniqueness and key-move analysis, hint ladders and stuck detection.
- Casual production at volume: goal and blocker taxonomies, board shapes, move limits from bot quantiles, measured colour-count effects, a difficulty-lever table with an elasticity calibration, an archetype-to-ship pipeline, a slotting algorithm, level A/B testing and live tuning.
- Action level design from formulas: reaction budgets, runner chunk grammar and validators, gate-runner maths, survivor spawn pressure, jump arcs and gap tables, arena geometry, enemy roles and threat budgets, boss phase and HP sizing, tower-defense path coverage.
- A pipeline: the level-spec format with an example per layout type, editor adapters, nine level gates, batch and CI recipes, the level event set and derived metrics, bot-to-human calibration, and how level content passes the five gates.
- `scripts/level_audit.py`: audits an ordered level set (mechanic introductions, hard streaks, relief, slack, bot vs target, run counts, duplicates), converts win rates to attempt odds, and merges solver output into specs.

## Core models

### 1. One idea per level, written down first
Every level has a five-line brief: id, the idea (a sentence about the rules, not the layout), the role (`teach|test|twist|reward`), the feeling, and target metrics. At most one element is new to the player. If you cannot write the idea, the level should not exist. (`references/principles.md` §1)

### 2. Teach → test → twist → reward
Introduce anything new safely and visibly (teach, ~0.95+ first-try win), check understanding with known elements only (test), combine or subvert it (twist), then let the player enjoy mastery (reward). Each element gets a test before any twist. With n elements there are n(n−1)/2 pairs — your twist budget. (`principles.md` §2)

### 3. Kishōtenketsu inside the level
Introduce (≈15–20% of the level), develop (≈30–35%), twist (≈30–35%), conclude (≈15–20%), then retire the gimmick. This fits 60–180-second mobile levels and lets a small mechanic set carry many levels. (`principles.md` §3)

### 4. Guidance is a hierarchy; UI arrows come last
Geometry and composition, then light and contrast, reserved colour language, motion, breadcrumbs, sound, characters, and only then UI markers. The test: "where next" is identifiable in a paused screenshot within 5 seconds. Whatever looks interactive must always be interactive (the affordance contract). (`principles.md` §4–5)

### 5. Difficulty is a sawtooth of win-rate targets, not a feeling
Ramp over ~5–10 levels, spike, relieve. Store targets in `difficulty_target`; convert to attempts with the geometric model (median attempts = ⌈ln 0.5 / ln(1−p)⌉): at p = 0.25, 42% of players fail three times running. Never introduce a new element on a spike. (`principles.md` §7, §12; `level_audit.py odds`)

### 6. A puzzle exploits one false assumption
Name the assumption the player will hold (order doesn't matter, every move should progress, this object is for X), build the minimal configuration that breaks it, remove shortcuts with a solver, then add context. The greedy-bot vs optimal gap is the best single "aha required" signal; dead-end density is the best frustration signal. (`references/puzzle-level-design.md` §2–6)

### 7. Colour count is the strongest casual lever; move limit is the finest
In this skill's scratch Monte Carlo of a plain 9×9 match-3 board (no specials or blockers), going from 4 to 5 colours roughly halves tiles cleared per move (14.0 → 7.5) and 5 → 6 cuts valid swaps by about a quarter. Use colours for world-level shifts, move limits (from the bot's moves-to-win quantile) for final tuning, and calibrate every lever's elasticity with simulator sweeps. (`references/casual-level-production.md` §6, §8–9)

### 8. Action levels are built from capability and reaction time
A threat must be visible for ≥ 1.3 × the reaction budget (perceive + decide + input + execute); never design at more than ~90% of a capability (jump distance, speed). Raise one difficulty dimension at a time (speed, density, complexity, precision, memory, endurance). (`references/action-level-design.md` §1)

### 9. Pressure ratios and budgets make action pacing numerate
Survivor waves: P(t) = incoming HP per second ÷ effective player DPS — under 0.6 relaxed, 0.6–0.9 comfortable, 0.9–1.1 tense, above 1.1 only in short swarms. Encounters: threat points per enemy, a growing budget, composition rules. Bosses: HP = duration × expected DPS × uptime. (`action-level-design.md` §4, §8–9)

### 10. Generate, then verify — hard levels most of all
No level enters the set without a machine verdict. Solver budget exhaustion means *unknown*, never *unsolvable*. Research on generated levels shows playability falls sharply at hard difficulty, so hard targets get the strictest checks. (`references/level-pipeline.md` §1, §6)

### 11. Bots predict; players decide
Bot win rates are hypotheses in bot space. Fit `logit(human) = a + b·logit(bot)` on 30+ levels, store converted targets in `difficulty_target.bot_win_rate`, recalibrate monthly, and treat level churn as the primary health signal. (`level-pipeline.md` §12; `casual-level-production.md` §9)

### Rules of thumb (starting values; verify per game)

| Topic | Starting rule | Source of truth |
|---|---|---|
| New elements, early game | One every 3–6 levels; later every 10–20 | `principles.md` §2 |
| Teach / reward first-try win | ≥ 0.95 / 0.9–1.0 | `principles.md` §2 |
| Puzzle move-limit slack (limit ÷ optimum) | teach ≥ 2.0, test 1.3–1.8, twist 1.2–1.5, exam 1.0–1.2 | `puzzle-level-design.md` §4 |
| Match-3 colours | 4 teach/reward, 5 workhorse, 6 hard | `casual-level-production.md` §8 |
| Match-3 move limit | Bot median moves-to-win × 1.10–1.25, then step ±1–2 | `casual-level-production.md` §6 |
| Bot runs for ±5-point tuning | ≥ 500 (s.e. ≈ 2.2 points at p = 0.5) | `casual-level-production.md` §9 |
| Portrait grid cell size | (width − 2·margin) / columns; 9 columns at 375 pt ≈ 39 pt | `principles.md` §11 |
| Colours on screen | ≤ 6, each with a shape cue | `principles.md` §11 |
| Runner rest beat | Every 15–30 s of intense play | `action-level-design.md` §2 |
| Platformer gaps | ≤ 60% / 80% / 90% of max jump for easy / medium / hard | `action-level-design.md` §5 |
| Mobile boss telegraph | ≥ 0.6–1.0 s for dodge-required attacks | `action-level-design.md` §9 |
| Hard levels in a row | ≤ 2, then relief within 2 levels | `level_audit.py` defaults |

## Decision procedures

### A. Design one level
1. Write the brief (idea, role, feeling, target first-try win rate, attempts p50, duration).
2. Check the role's rules (`principles.md` §2): teach = isolated and unmissable; test = known elements only; twist = one combination; reward = generous.
3. Lay out beats (ki–shō–ten–ketsu or a beat chart) and guidance (goal visible early; reserved visual language).
4. Build the minimal layout; write the intended path or solution in `notes`.
5. Verify with the right tool (table H) and record results in `solver`.
6. Tune with the finest lever available (move limit, goal count) until the bot result sits within tolerance of the bot-space target.
7. Run the one-page review (`principles.md` §13) and `level_audit.py audit` with its neighbours.

### B. Sequence a world or chapter
1. List elements to introduce and the known set; draw the mechanic interaction graph (`puzzle-level-design.md` §10).
2. Generate targets: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/difficulty_curve.py generate --levels 20 --pattern sawtooth --base 0.92 --floor 0.40 --period 8 --hard-every 10 --json`.
3. Assign roles per slot: teach on first appearance, test before twist, reward after every spike, hard slots flagged in UI.
4. Fill slots (design or generate), verify, then slot by closest predicted difficulty under the constraints (`casual-level-production.md` §12).
5. Write `order.json`; run `level_audit.py audit --dir .gamestudio/levels`; fix errors, review warnings.
6. Human taste sign-off for the world (doctrine 10).

### C. Produce hundreds of casual levels
1. Compute content burn and the weekly production target from the percentile you will never let run dry (`casual-level-production.md` §1).
2. Write 20–40 archetypes with parameter ranges; generate 5–20 variants each with seeds.
3. Designer pass (curation is the bottleneck; invest in editor ergonomics).
4. Bot gate: `match3_sim.py --runs 500–1000 --seed 1`; tune to ±5 points of the bot-space target.
5. Tag, bucket, slot, enforce variety rules, audit, review on a low-end phone, sign off.
6. After launch: problem-level dashboard weekly; fix by remote config; recalibrate bots monthly.

### D. Diagnose a problem level
| Symptom | Likely cause | First action |
|---|---|---|
| Churn ≫ neighbours, low win rate | Too hard | +2–3 moves or remove a blocker layer (remote config); A/B if traffic allows |
| Churn high, win rate normal | Long, confusing or misleading signifier | Check goal clarity and affordances; shorten |
| Many losses with 1 goal unit left | Back-loaded goal | Reduce the goal count; make last cells reachable |
| Many losses with most of the goal left | Luck-dominated or unreadable | Fewer colours; remove pockets |
| Puzzle quits after long idle | No insight path; stuck | Hint ladder from the solver; lower dead-end density |
| Deaths cluster in one runner chunk | Readability or unfair spacing | Re-run the time-lane validator; check telegraph distance |
| Bot and live diverge after a client update | Rules or simulator changed | Re-run the bot gate on a fixed sample |

### E. Puzzle level from an insight
Insight sentence → minimal configuration → solver (solvable, `min_moves`, key move in every shortest solution) → block shortcuts → context and noise for the audience → limit from the slack band → greedy-vs-optimal gap matches the role → playtest for the moment of insight (`puzzle-level-design.md` §3, §8, §14).

### F. Action level from capabilities
Capability metrics → reaction budget → geometry rules (gaps, telegraph distance, arena cross time) → content (chunks, waves, encounters) → pressure or budget check → validator or simulation → playtest deaths per section (`action-level-design.md` §1–8, §11).

### G. Boss
Exam list (which taught skills it tests) → 2–3 phases at HP thresholds → 3–5 attacks per phase with unique wind-ups → telegraph and punish windows → HP from duration × DPS × uptime, checked at the 25th and 75th percentile of player power → arena supports patterns → checkpoint per phase on mobile (`action-level-design.md` §9).

### H. Choose the verification method
| Level type | Verifier | Command or method |
|---|---|---|
| Sort, Sokoban, sliding, Lights Out | Exact solver | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/puzzle_solver.py --level PATH --algo bfs\|astar --max-nodes N --json` |
| Match-3 | Monte Carlo bots | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/match3_sim.py --level PATH --runs 500 --bot greedy --seed 1 --json` |
| Blast, screw, tray, logic grids | Purpose-built solver or bot in the game project | Record in the same `solver` fields |
| Generated maps | Reachability / connectivity post-check | `pcg.py ... --seed S --json`, then flood fill and BFS |
| Runner chunks | Time-lane BFS at min and max speed | `action-level-design.md` §2 |
| Survivor, encounters, bosses | Headless sim or engine bot runner | Playtest report under `.gamestudio/evidence/<FEATURE-ID>/` |
| A whole set | Set audit | `python3 ${CLAUDE_PLUGIN_ROOT}/skills/level-design/scripts/level_audit.py audit --dir .gamestudio/levels` |

## Mobile specifics

- **Size from the formula, not by eye.** Cell = (screen width − 2·margin) / columns; respect 44 pt (Apple HIG) / 48 dp (Material) minimums for tap targets; portrait match-3 stops at about 9 columns.
- **Readability beats detail.** ≤ 6 simultaneous colours, colour plus shape for every colour cue, HP and layers readable at a glance, nothing critical under thumbs, notches or the home indicator.
- **Session-sized levels.** 1–3 minutes per level; longer content needs checkpoints; turn-based state persists every move; real-time levels auto-pause on interruption.
- **Touch is imprecise and late.** Add input latency to reaction budgets, widen windows 10–20% versus controller designs, avoid precision multi-touch, offset dragged pieces above the finger.
- **Low-end devices set density.** Entity caps from profiling on the low tier (`mobile-performance`); design wave density within them (raise HP, not count).
- **One-handed portrait.** Inputs in the lower two thirds, reading in the top third; the goal visible without scrolling or shown by a landmark.
- **Interruption-tolerant guidance.** A player returning after a notification must re-read the situation in seconds: persistent goal HUD, clear "next move" highlighting on idle.

## Anti-patterns

| Anti-pattern | How to detect | Fix |
|---|---|---|
| Two new elements in one level | `level_audit.py` `multi_intro` | Split into two teach levels |
| New element on a difficulty spike | `intro_on_spike` | Move the introduction to a relief slot |
| Twist before test | `twist_before_test` | Insert a test level |
| Hard streaks, no relief | `hard_streak`, `no_relief` | Reorder; add a reward level |
| Hand-typed solver numbers | `solver` filled without a result file | Re-run the tool; use `level_audit.py merge` |
| "Unsolvable" from a budget cap | Solver hit `--max-nodes` | Record as unknown; raise the cap or use A* |
| Move limit tuned by feel | No bot quantile or slack ratio in `notes` | Set from the solver optimum or bot distribution |
| Tutorial text instead of teaching geometry | Text over 10 words in a teach level | Make the layout force the discovery |
| Broken affordance contract | Repeated taps on scenery; deaths at identical-looking ledges | One visual language; distinct decor |
| Colour-only coding | Greyscale screenshot loses information | Add shapes or icons |
| Hidden per-player spawn rigging to sell boosters | Spawn code branches on spend or fail count without disclosure | Remove; use transparent, bounded assists only (`legal-ethics`) |
| Generated levels shipped unverified | No `solver` block on generated files | Generation policy: verify before storing |
| Damage-sponge bosses | Long phases with no new pattern | Phases with new attacks; HP from duration formula |
| Blind runner threats | Deaths without a visible telegraph window | Validator with reaction distance; extend draw distance |
| Copying a genre leader's levels | Layout hashes match references; no new idea per level | Archetypes from your own mechanic graph |

## Using the ontology

| Concept | Where it lives | Notes |
|---|---|---|
| A level | `.gamestudio/levels/<level_id>.level.json` (`${CLAUDE_PLUGIN_ROOT}/scripts/schemas/level-spec.schema.json`) | `schema_version`, `level_id`, `mechanic_refs`, `layout`, `goals`, `moves_or_time_limit`, `obstacles`, `difficulty_target`, `solver`, `teach`, `notes` |
| Layout variants | `layout.type` = `grid`, `sliding`, `sokoban`, `sort`, `lights_out`, `match3`, `generator`, `custom` | Examples for each in `references/level-pipeline.md` §3 |
| Mechanics used | `mechanic_refs` → contract `mechanics[].id` | Mechanic cards via `mechanic-card.schema.json` (`mechanics-codex`) |
| Level count and generation mode | contract `content.levels` {`target_count`, `generation`, `spec_ref`} | `handmade`, `procedural` or `hybrid` |
| Difficulty model | contract `progression.difficulty` {`model`, `target_win_rate`, `dda`} | Per-level targets in `difficulty_target` |
| Role in rhythm | `teach` enum | Drives sequencing checks |
| Bot-space target | `difficulty_target.bot_win_rate` (extra field) | From the bot-to-human calibration |
| Verification | `solver` {`solvable`, `min_moves`, `bot_win_rate`, `runs`} plus extras | Written from tool output only |
| Level telemetry | `event-taxonomy.schema.json` (`level_start`, `level_end`, `level_hint`, `level_restart`) | Derived metrics in `level-pipeline.md` §12 |
| Playtests and bot sweeps | `playtest-report.schema.json` in `.gamestudio/playtests/` or evidence folders | `metrics.win_rate`, `softlocks`, `findings` |
| Content features | `features.json` (area `content`) | Five-gate evidence mapping in `level-pipeline.md` §13 |

**Tools**

| Task | Command |
|---|---|
| Validate level files | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_json.py --auto .gamestudio/levels` or `gs.py validate PATH` |
| Solve a deterministic puzzle | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/puzzle_solver.py --level PATH [--algo bfs\|astar] [--max-nodes N] [--json]` |
| Simulate a match-3 level | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/match3_sim.py --level PATH [--runs N] [--bot greedy\|random\|cascade] [--seed S] [--json]` |
| Generate a map | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/pcg.py wfc\|bsp\|cave\|noise\|poisson\|maze --w W --h H [--seed S] [--json] [--out PATH]` |
| Target curve / live curve analysis | `difficulty_curve.py generate ...` · `difficulty_curve.py analyze --data levels.csv --json` |
| Level A/B sizing and analysis | `ab_test.py size --baseline 0.80 --mde 0.02 --two-sided` · `ab_test.py analyze ...` |
| Set audit | `python3 ${CLAUDE_PLUGIN_ROOT}/skills/level-design/scripts/level_audit.py audit --dir .gamestudio/levels [--strict] [--json]` |
| Attempt odds | `level_audit.py odds --win-rate 0.3 --attempts 5` |
| Merge solver output into a spec | `level_audit.py merge --level PATH --result RESULT.json [--dry-run]` |
| Search the codex | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py kb "blocker taxonomy" --skill level-design` |

`level_audit.py` is stdlib-only (Python 3.9+), supports `--json`, exits 0/1/2, and passes `--selftest`.

**Who uses this.** The `arcosian:level-designer` agent owns level work; `arcosian:systems-designer` owns the difficulty model and economy coupling; `arcosian:qa-lead` and `arcosian:player-simulator` run sweeps; `arcosian:data-analyst` runs calibration and level A/B tests. Workflows: `/arcosian:balance-pass` and `/arcosian:playtest-sweep`; process skills `/arcosian:balance` and `/arcosian:playtest`.

## Reference library

| File | What it contains | Read it when |
|---|---|---|
| `references/principles.md` | Level brief; teach–test–twist–reward with role rules and cadence; kishōtenketsu; guidance hierarchy and tests; affordance contract; gating types and star-gate arithmetic; pacing and beat charts; Lynch, weenies, prospect–refuge; risk/reward EV; flow conditions; mobile readability formulas; capability and performance metrics; win-rate-to-attempts table; one-page review | Designing or reviewing any level in any genre; settling sequencing and readability questions |
| `references/puzzle-level-design.md` | Puzzle definition and audiences; insight types; design-backwards; constraints and slack bands; red herrings and traps; solver-measurable difficulty factors; composite difficulty model and calibration; uniqueness and key-move analysis; stuck detection and hint ladders; mechanic graphs and open vs linear structure; search and generation strategies; per-type parameter tables; a measured sort-level worked example | Designing deterministic puzzles (sort, Sokoban, sliding, Lights Out, logic, screw, tray); building hints; generating puzzles with solvers |
| `references/casual-level-production.md` | Content burn; match-3 anatomy; goal and blocker taxonomies; board shapes; move limits from bot quantiles; spawn fairness; measured colour-count table; difficulty-lever table and elasticity sweeps; bot-to-human mapping; blast specifics; archetype-to-ship pipeline; slotting algorithm; level A/B tests; live tuning; `match3_sim.py` recipes; 20-level world example; volatile facts on bot-based difficulty | Producing or tuning match-3, blast and other casual levels at volume; fixing problem levels; planning content cadence |
| `references/action-level-design.md` | Reaction budget and fairness; runner chunk spec, reaction distance, speed ramps, selection algorithm and validator; gate-runner maths; survivor pressure model and wave tables; jump-arc formulas, gap tables, rhythm groups, checkpoints; arenas; enemy roles and placement; threat budgets and waves; boss structure and HP sizing; tower-defense paths; verification and level-spec storage | Designing runners, survivor-likes, platformers, arenas, encounters, bosses or TD maps |
| `references/level-pipeline.md` | Level-spec field by field with examples for every layout type; file and id conventions; editor comparison and adapter rules; nine level gates; `puzzle_solver.py`, `match3_sim.py`, `pcg.py` and `level_audit.py` usage; batch and CI recipes; level events and derived metrics; bot calibration; five-gate evidence mapping; live content ops; agent workflow; volatile facts | Setting up or running the level pipeline; writing or validating specs; automating verification; instrumenting levels |

## Related skills

- `progression-difficulty` — difficulty models, curves and DDA that set the targets levels are tuned to.
- `procedural-generation` — generator design in depth (grammars, WFC, constraint solving, runtime seeds).
- `mechanics-codex` — rules of every puzzle and action mechanic that levels instantiate.
- `genre-playbooks` — genre conventions, KPIs and content scope (puzzle, action, hybrid-casual).
- `game-case-studies` — how landmark games structure and pace their levels.
- `design-theory` — interest curves, flow, decisions and pacing theory behind these principles.
- `game-feel` — juice, input forgiveness (coyote time, buffering) and feedback that make levels feel fair.
- `mobile-ux` — HUD, safe areas, thumb zones and FTUE flows that frame levels.
- `player-analytics` — level telemetry, funnels and churn analysis.
- `qa-testing` — bot runners, deterministic playthroughs and evidence for the five gates.
- `economy-design` — boosters, lives and rewards coupled to level difficulty.
- `monetization` — fail-screen offers and boosters, ethically bounded.
- `liveops` — events and content cadence that consume or extend levels.
- `narrative-design` — story beats and environmental storytelling placed along level paths.
- `accessibility-localization` — colour-blind safety, assist modes and readable text.
- `legal-ethics` — limits on hidden difficulty manipulation and loot-like rewards.
- `game-ontology` — the shared vocabulary and schemas, including `level-spec.schema.json`.
