# Generate and Test: Evaluation, Gates and Expressive Range

A generator is only as good as its tests. This file covers the machinery that turns a random generator into a shippable content source. It explains generate-evaluate-filter pipelines and how to order and budget their gates, acceptance-rate economics (when to generate on device and when offline), solver and bot gates with the sample sizes they need, and expressive range analysis (Smith and Whitehead's linearity and leniency, plus diversity and duplicate checks) to see what a generator *actually* produces rather than what its author hopes. It also covers LLM-assisted PCG and its measured failure rates on hard content, and the concrete tools: the plugin's `pcg.py` generators and this skill's `scripts/pcgkit.py era` analyser. If your generator has no automated test, it ships bugs to players at the rate of its failure probability multiplied by your install base.

## Contents

1. The generate-evaluate-filter pipeline
2. Designing gates: hard constraints, soft scores, ordering by cost
3. Acceptance-rate economics: on device or offline?
4. Solver and bot gates
5. Expressive range analysis
6. Diversity, duplicates and the oatmeal problem
7. Tools: `pcg.py` and `pcgkit.py era`
8. LLM-assisted PCG and its failure rates
9. Pipeline templates
10. Recording results in the ontology and the five gates
11. Anti-patterns
12. Volatile facts (as of Oct 2026, verify before relying)

---

## 1. The generate-evaluate-filter pipeline

Togelius, Yannakakis, Stanley and Browne's survey of search-based PCG (IEEE TCIAIG, 2011) separates **constructive** generators (build once, guaranteed valid by construction, like backward puzzle generation or Spelunky-style templates) from **generate-and-test** generators (build, test, discard or keep). It also sorts generators along several axes that are worth stating for every generator you build:

| Axis | Options | Design consequence |
|---|---|---|
| When | Online (at play time, on device) vs offline (in the studio) | Online needs bounded time and a guaranteed fallback; offline can afford expensive tests |
| Necessity | Necessary content (must be traversable: the level itself) vs optional (side rooms, decoration) | Necessary content needs hard gates; optional content can fail softly |
| Control | Random seed only vs parameter vector | Parameters enable difficulty targeting and LLM or designer control |
| Process | Deterministic vs stochastic | Determinism is required for seeds, dailies and replays |

The pipeline, in stages:

```text
params + seed
   -> GENERATE            (constructive core: noise, CA, WFC, chunks, grammar, LLM proposal ...)
   -> REPAIR (optional)   (tunnel disconnected regions, move a misplaced key)
   -> CHEAP GATES         (schema, bounds, counts, connectivity flood fill): reject fast
   -> EXPENSIVE GATES     (solver, lock-and-key search, bot playthroughs): reject or measure
   -> SCORE               (difficulty estimate, fun proxies, style fit)
   -> SELECT FOR DIVERSITY(dedupe, MAP-Elites cells, cluster quotas)
   -> CURATE              (human spot-check sample; offline only)
   -> SHIP                (as data, or as a verified seed range plus an on-device validator)
```

Every stage logs (seed, generator_version, params, stage reached, reason for rejection). Rejection reasons are your best generator-debugging data: if 70% of rejections are "exit unreachable", fix the generator, not the gate.

---

## 2. Designing gates

**Hard constraints** reject. **Soft scores** rank. Never mix them: a weighted sum that includes "is solvable" as one term lets an unsolvable but pretty level outscore a solvable plain one.

| Gate type | Examples | Typical cost | Output |
|---|---|---|---|
| Schema and bounds | Level-spec validates; size, tile codes and counts in range | Microseconds | pass / fail + reason |
| Structural invariants | Connectivity ≥ 0.95, start and exit in the same region, required objects present, no object inside a wall | Sub-millisecond flood fill | pass / fail + metric values |
| Logical validity | Lock-and-key order, quest DAG acyclic, every key before its lock | Milliseconds (state search) | pass / fail |
| Solvability | BFS/A* solver, SAT check | Milliseconds to seconds; budgeted | solvable / unsolvable / **unknown** + min_moves |
| Difficulty and feel | Bot win rate over N runs, attempts estimate, death positions | Seconds (N × bot runs) | distributions |
| Perceptual | Screenshot critique, human review | Minutes | rubric scores (offline only) |

**Order gates by cost and by rejection power.** The expected cost per candidate is

```text
E[cost per candidate] = c1 + p1·c2 + p1·p2·c3 + ...      # p_i = probability of passing gate i
E[cost per accepted]  = E[cost per candidate] / (p1·p2·p3·...)
```

Worked example: a structural check (0.1 ms, passes 60%), then a solver (40 ms, passes 50% of those), then 200 bot runs (2 ms each = 400 ms, passes 80%). Per candidate: 0.1 + 0.6 × 40 + 0.6 × 0.5 × 400 = 144.1 ms. Overall acceptance is 0.6 × 0.5 × 0.8 = 0.24, so about **600 ms per accepted level**: fine offline, not fine on device. Running the solver first instead would cost 40 + 0.5 × 0.1 + ... per candidate: always put the cheap, high-rejection gate first.

**Treat "unknown" as reject** when the solver hits its node budget, for shipping purposes. Log these separately: a rising unknown rate means content is drifting harder than the solver budget, which is a design signal.

---

## 3. Acceptance-rate economics

If each attempt passes with probability a, independently:

```text
mean attempts      = 1 / a
p-quantile attempts = ln(1 - p) / ln(1 - a)        # attempts needed so that a share p of players succeeds
```

| Acceptance a | Mean attempts | 99th-percentile attempts | Verdict for on-device generation |
|---|---|---|---|
| 0.9 | 1.1 | 2 | Generate on device with a validator |
| 0.5 | 2 | 6.6 | On device if one attempt costs ≤ 20 ms |
| 0.3 | 3.3 | 12.9 | On device only for cheap generators; otherwise offline |
| 0.1 | 10 | 43.7 | Offline, or ship validated seeds |
| 0.01 | 100 | 458 | Offline only; fix the generator |

Rules:
1. Measure acceptance offline over at least 1,000 seeds *per parameter setting and difficulty band*. Acceptance usually falls as target difficulty rises.
2. On device: cap attempts (for example at the 99.9th-percentile count), then fall back to a pre-validated cached level. Players must never see a spinner because a generator is rerolling.
3. If acceptance is below about 0.2, improve the generator (constraints in the constructive step, repair passes), or switch to offline generation with a shipped pool or **validated seed ranges** (seeds pre-tested in CI and shipped as a list).

---

## 4. Solver and bot gates

| Content | Gate | Tool in this plugin |
|---|---|---|
| Deterministic puzzles (sliding, Sokoban, sort, Lights Out) | Optimal or bounded search: solvable, min_moves | `${CLAUDE_PLUGIN_ROOT}/scripts/puzzle_solver.py --level PATH [--algo bfs|astar] [--max-nodes N] --json` |
| Match-3 and other stochastic boards | Monte Carlo bots: win rate and moves-left distribution | `${CLAUDE_PLUGIN_ROOT}/scripts/match3_sim.py --level PATH --runs 500 --bot greedy|random|cascade --seed S --json` |
| Grid maps and dungeons | Flood-fill connectivity, start-to-exit path length, lock-and-key state search | `scripts/pcgkit.py era` (connectivity and linearity metrics); write lock-key checks in the generator |
| Real-time levels (runner chunks, platformers) | Reachability over a movement model (jump arcs, lane switches at speed), then bot playthroughs in the engine's headless mode | Engine playtest runner (`qa-testing`; the Godot template's `runner.gd --mode=bot`) |
| Whole game loop | Bot and persona playtests, deterministic scripted playthroughs | `/arcosian:playtest`, agent `arcosian:qa-lead` |

**Solver ≠ player.** An optimal solver says *whether* a level can be beaten and its minimum length; it says little about how hard it feels. King's work on Candy Crush (Gudmundsson et al., 2018) trained a network on player moves so its bot plays like humans, then used bot win rates to predict level difficulty across more than 1,000 new levels. Without player data, use several simple bots (random, greedy, greedy with lookahead) and later fit a mapping from bot metrics to observed player win rates (`progression-difficulty`).

**Sample sizes for bot win rates.** A win rate from n independent runs has a 95% margin of about `1.96 × sqrt(p(1−p)/n)`:

| Runs n | Margin at p = 0.5 | Margin at p = 0.2 |
|---|---|---|
| 50 | ±13.9 pp | ±11.1 pp |
| 200 | ±6.9 pp | ±5.5 pp |
| 500 | ±4.4 pp | ±3.5 pp |
| 2,000 | ±2.2 pp | ±1.8 pp |

200 runs separate difficulty bands 15 points apart; 500 or more are needed to tune within a band. Seed bot runs (`--seed`) so a regression rerun is comparable.

**Softlock detection** is a gate of its own: a bot that reaches a state with no legal progress (no valid moves, unreachable goal, stuck physics) must report it with the seed and the state, and a single softlock in a necessary-content generator blocks shipping.

---

## 5. Expressive range analysis

Gillian Smith and Jim Whitehead ("Analyzing the Expressive Range of a Level Generator", PCG Workshop 2010) proposed looking at a generator's whole output space: generate a large sample, score every level on a few metrics, and plot two-metric histograms (heatmaps). The shape shows what the generator can and cannot make, where it clusters, and how parameters move it. They used two metrics for their platformer generator:

- **Linearity:** how closely the level's geometry follows a straight line. They fitted a line through the platform positions and measured the deviation. Highly linear levels are flat runs; non-linear ones climb and drop.
- **Leniency:** how forgiving the level is. Each component gets a weight (hazards such as gaps and enemies count against it, safe elements count for it), averaged over the level.

Later work broadened the metric set. Horn and colleagues' comparison of Mario level generators (FDG 2014) used leniency, linearity, density, pattern density, pattern variation and compression distance to compare many generators in one space. Withington, Cook and Tokarchuk (FDG 2024) surveyed how PCG systems are evaluated, found limited consensus, and proposed a taxonomy of evaluation methods. Beukman and colleagues (arXiv 2201.10334) measured diversity and difficulty from the behaviour of a planning agent playing the levels rather than from level geometry alone.

### 5.1 Procedure

1. **Choose 4–8 metrics that encode design intent**, not convenience: difficulty proxies (solver min_moves, bot win rate, hazard density), structure (linearity, branching, loop count), pacing (distance between threats, rest share) and style (open vs cramped).
2. **Generate a large sample** per parameter setting: at least 1,000 levels; 10,000 for on-device generators that millions of players will roll.
3. **Plot pairwise histograms** of the metrics that matter most together (difficulty × structure is the usual first pair).
4. **Read the shape:** Is the intended region covered? Are there dense clusters (sameness) or holes (things it cannot make)? How many degenerate outliers (empty maps, one-room dungeons)?
5. **Inspect extremes by eye.** Render the 10 levels at each corner of the histogram. Bugs live at the edges.
6. **Vary one parameter at a time** and re-plot: this is how you learn which knob moves which metric (the cave fill sweep in `algorithms.md` §7 is an example).
7. **Plot handmade levels in the same space.** If designers' favourite levels sit outside the generator's range, the generator cannot make what the team wants.
8. **Turn findings into gates and targets:** keep filters (reject degenerate regions), quotas per cell (diversity), and difficulty-band boundaries.
9. **Re-run the analysis in CI** on every generator change, with coverage and duplicate thresholds as exit-code checks.

### 5.2 Top-down adaptations used by `pcgkit.py era`

Smith and Whitehead's definitions are for side-on platformers. For top-down grid maps (caves, dungeons, puzzle boards), `scripts/pcgkit.py` computes these adaptations. The names are kept for familiarity; they are **not** the original formulas.

| Metric | Definition in pcgkit | Reads as |
|---|---|---|
| `density` | Wall cells / all cells | Cramped (high) vs open (low) |
| `openness` | Floor cells / all cells (hazards count as floor) | Complement of density |
| `connectivity` | Largest 4-connected floor region / all floor | < 1 means unreachable pockets |
| `components` | Number of floor regions | Fragmentation |
| `linearity` | Cells on the longest shortest path of the largest region (approximate diameter, double BFS) / cells in that region | 1.0 = a single corridor; low = open or highly branched |
| `dead_ends` | Floor cells with exactly one floor neighbour / floor | Maze-likeness, backtracking pressure |
| `leniency` | 1 − hazard cells / floor cells | Forgiveness (needs hazard codes via `--hazard`) |
| `hazards` | Hazard cell count | Raw threat count |

For other content types (runner sequences, puzzles, loot tables), compute your own metrics in the generator harness and feed a CSV or JSONL of metric rows to `pcgkit.py era`; it bins any two numeric columns.

### 5.3 Worked example (run for this file)

200 cellular-automata caves (32 × 24, initial fill swept from 0.40 to 0.50, 4 smoothing steps; output abbreviated to the two plotted metrics):

```text
$ pcgkit.py era --in caves.json --x connectivity --y density --bins 8 --keep "connectivity>=0.9,openness>=0.4"
levels: 200   coverage: 31.2% of 8x8 bins   peak bin: 33.0%   duplicates: 0
connectivity  mean 0.866  p10 0.526  p50 0.978  p90 1.000
density       mean 0.541  p10 0.389  p50 0.525  p90 0.706
keep connectivity>=0.9,openness>=0.4 -> 116/200 accepted (58.0%)
```

Interpretation: a third of the output piles into one cell (fully connected, around half walls), the dense end of the sweep produces fragmented maps, and only 58% pass a basic playability filter. The fixes are a narrower fill range (0.40–0.45) plus a region-connection pass, which moves acceptance toward 100% and removes the fragmented tail. The analysis, not intuition, found both problems.

---

## 6. Diversity, duplicates and the oatmeal problem

Kate Compton's essay on building generators (2016) named the **"10,000 bowls of oatmeal" problem**: a generator can produce endless *technically unique* outputs that are *perceptually identical*. Uniqueness is not variety. Measure variety:

| Measure | How | Threshold to start from |
|---|---|---|
| Exact duplicates | Hash the canonical form (after rotation, reflection and recolouring normalisation) | 0 in a shipped pool; < 1% in on-device sampling |
| Near duplicates | Pairwise Hamming distance on grids, or edit distance on sequences; flag pairs below a threshold | Tune per content; inspect flagged pairs by eye |
| Compression distance | Normalised compression distance, `NCD(x, y) = (C(xy) − min(C(x), C(y))) / max(C(x), C(y))` with zlib | Higher means more different; compare against handmade pairs |
| Histogram coverage | Share of non-empty bins in the expressive-range heatmap | Track over versions; falling coverage = narrowing |
| Peak-bin share | Share of levels in the most populated bin | > 30% suggests sameness (as in §5.3) |
| Perceptual distinctness | Show players or designers pairs; ask "same or different?" | ≥ 70% "different" for content sold as variety |

Variety that players notice comes from **differences in decisions** (routes, threats, tactics), not differences in pixels. Prefer metrics that reflect play (solver paths, bot behaviour) over metrics that reflect layout alone.

---

## 7. Tools: `pcg.py` and `pcgkit.py era`

### 7.1 `pcg.py` (plugin-level generators)

The binding command line (BLUEPRINT §14):

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/pcg.py wfc|bsp|cave|noise|poisson|maze --w W --h H [--seed S] [--json] [--out PATH]
```

- Generators: `wfc` (tile synthesis), `bsp` (rooms), `cave` (cellular automata), `noise` (heightfield), `poisson` (point scatter), `maze` (spanning-tree maze).
- Always pass `--seed`; record the seed and generator in the level spec as `layout: {"type": "generator", "generator": "pcg.py cave", "seed": 17, "params": {"w": 48, "h": 32}}` (the `layout_generator` variant of `level-spec.schema.json`).
- Run `pcg.py <generator> --help` for generator-specific options and check its `--json` output shape before writing a harness. `pcgkit.py era` finds grids inside nested `grid`, `rows`, `layout`, `map`, `tiles` or `cells` keys, or any rectangular array of rows, so most output shapes work without conversion.

**Batch-and-analyse loop:**

```bash
mkdir -p .gamestudio/levels/gen/cave
for s in $(seq 1 1000); do
  python3 ${CLAUDE_PLUGIN_ROOT}/scripts/pcg.py cave --w 48 --h 32 --seed "$s" --json \
    --out ".gamestudio/levels/gen/cave/cave_$s.json" || echo "seed $s failed" >&2
done
python3 ${CLAUDE_PLUGIN_ROOT}/skills/procedural-generation/scripts/pcgkit.py era \
  --in .gamestudio/levels/gen/cave --x linearity --y density --bins 10 \
  --keep "connectivity>=0.95,openness>=0.35" --min-accept 0.8 --max-duplicates 0 \
  --out .gamestudio/reports/era-cave.json
```

### 7.2 `pcgkit.py era` reference

| Flag | Meaning |
|---|---|
| `--in PATH` (repeatable) | Files or directories: `.json` (grids, level specs, lists of either), `.jsonl` (one per line), `.csv` (metric rows) |
| `--x`, `--y` | Metrics for the heatmap axes (defaults: `linearity`, `density`) |
| `--bins N` | Bins per axis (default 10) |
| `--range-x`, `--range-y` | Axis ranges as `lo,hi` (ratio metrics default to 0,1; others to the data range) |
| `--wall`, `--hazard` | Comma lists of cell codes (defaults `#,1,W` and `^,X`) |
| `--keep RULES` | Filter such as `"connectivity>=0.95,density<=0.55"`; reports acceptance and the kept sources |
| `--min-coverage F`, `--max-duplicates N`, `--min-accept F` | CI checks: exit code 1 if violated |
| `--per-level` | Include every level's metrics in the JSON output |
| `--out PATH`, `--json` | Write or print machine-readable results |

Exit codes: 0 ok, 1 a check failed, 2 usage or input error. `--selftest` runs the built-in fixtures.

---

## 8. LLM-assisted PCG and its failure rates

### 8.1 What the evidence says

- An LLM plus GAN approach to Snake levels (FedCSIS 2025) validated difficulty-labelled generated levels with A* pathfinding: **87% of easy levels were playable, but only 36% of hard ones**. The harder the target, the more often the output is broken.
- An early LLM level-generation study (arXiv 2302.05817, 2023, GPT-2 family models) reported novelty, playability and diversity, and framed prompt-based controllability as the main attraction.
- A 2024 survey of PCG methods (arXiv 2410.15644) covers how LLMs are being integrated into classical pipelines. The FDG 2024 evaluation survey (arXiv 2404.18657) notes there is little consensus on how to evaluate any PCG system, LLM-based or not.
- In the GDC 2026 State of the Game Industry survey, respondents who use generative AI named PCG for 10% of their uses, far behind brainstorming (81%) and code assistance (47%).
- No 2025–2026 benchmark comparing LLM level generators on playability across games was found in this plugin's research. Measure on your own content.

### 8.2 Where LLMs help and where they fail

| Role | Reliability | Pattern |
|---|---|---|
| Theme, naming, flavour text, quest framing | High (with filters) | Offline batches, human review, filters from `pcg-for-mobile-games.md` §8 |
| Parameteriser: natural-language intent → generator parameter JSON | High | Schema-validate the JSON; the classical generator plus gates does the spatial work |
| Structure author: mission graphs, room sequences, encounter lists | Medium | Validate graph invariants (acyclic, lock-and-key order, counts) automatically |
| Direct tile or grid author | Low, and falls with difficulty | Only behind solver gates plus a bounded repair loop; expect low acceptance on hard content |
| Critic: theme fit, readability notes, ranking among *valid* candidates | Medium | Advisory only, never the solvability or difficulty oracle |
| Runtime generation on device | Not recommended | Latency, cost, offline play, non-determinism, content-safety risk |

### 8.3 The safe LLM loop

```text
for each request:
    proposal = LLM(prompt with schema, examples, constraints)      # temperature low; log model id and prompt
    if not schema_valid(proposal): reprompt with the validation error (max 2)
    level = generator(proposal.params, seed)  OR  parse(proposal.grid)
    result = gates(level)                                           # structure -> solver -> bots
    if result.fail and repairs < 2:
        reprompt with the solver's diagnosis ("exit unreachable from start; region sizes 140 and 12")
    elif result.fail: discard and record the failure
    else: keep with provenance (model, prompt hash, seed, gate results)
```

**Budgeting with failure rates.** Using the Snake figures as an illustration only (your game will differ): at 36% acceptance, an accepted hard level needs 1/0.36 ≈ 2.8 LLM calls on average and about 6.7 calls at the 95th percentile (`ln(0.05) / ln(0.64)`), *before* repair loops. At 87% acceptance (easy), about 1.15 calls on average. So use LLMs where acceptance is high (easy content, framing, parameters), and produce hard content with constructive methods that guarantee validity (backward generation, constraint solving) or with search against the solver (`algorithms.md` §18–19).

**Provenance.** Keep the model id, prompt hash, seed and gate results with every LLM-assisted level (in the level spec's `notes` or a generation log under `.gamestudio/levels/`). Store disclosure-relevant facts for store AI-content questionnaires (`legal-ethics`, `store-release`).

---

## 9. Pipeline templates

**(a) Offline puzzle pool (sort, sliding, Sokoban).**
1. Generate 20,000 candidates per world with backward or random generation (seeded ranges per world).
2. Canonicalise and dedupe → `puzzle_solver.py --json` → reject unsolvable and unknown.
3. Grade (min_moves, branching, dead-end share) → bucket into difficulty bands.
4. ERA on band × structure; check coverage and duplicates (`pcgkit.py era --in metrics.csv --x min_moves --y branching`).
5. Sequence 60 levels per world with teach/test/twist/reward; human plays 10%.
6. Ship as level-spec JSON; record `solver` blocks.

**(b) On-device runner with a validator.**
1. Offline: 10,000 simulated runs of the chunk selector per speed band; check reachability failures = 0, chunk repetition and death-rate outliers.
2. On device: `next_chunk` with transition BFS (microseconds) and a universal rest-chunk fallback.
3. Telemetry: deaths per chunk id → re-rate difficulty monthly.

**(c) Daily seed validation (CI, weekly).**
1. For each date in the next 60 days: `pcgkit.py seed daily --date D --salt S` → generate → solver and 200 bot runs.
2. Any failure → pick the next derived seed (`"daily:D:alt1"`) and write it to the remote-config override list.
3. Store the report under `.gamestudio/reports/`.

**(d) MAP-Elites difficulty ladder.**
1. Behaviour axes: solver min_moves (difficulty) × linearity (structure); 10 × 10 cells.
2. Run 50,000 mutations offline; feasibility = solver passes.
3. Ship the elite of each cell; sequence along the difficulty axis while alternating structure.

---

## 10. Recording results in the ontology and the five gates

- **Level specs** (`${CLAUDE_PLUGIN_ROOT}/scripts/schemas/level-spec.schema.json`): `layout` (grid, typed layout or `generator` reference with `seed` and `params`), `difficulty_target` {`win_rate`, `attempts_p50`}, `solver` {`solvable`, `min_moves`, `bot_win_rate`, `runs`}, `teach`, `notes` (seed, generator version, rejection history, LLM provenance).
- **Bot sweeps** produce `playtest-report.schema.json` files with `mode: "bot"`, `runs`, `seed`, `metrics.win_rate`, `metrics.softlocks` and `findings`.
- **A generator is a feature** in `features.json` (area `content` or `tech`). Its gates: `static` (code compiles, schema validates), `unit` (golden-seed hash tests, PRNG vectors, invariants), `playthrough` (bot sweep report: zero softlocks, win rates in band), `visual` (screenshots of sampled outputs pass critique, including the ERA extremes), `perf` (p95 generation time on the low-tier device within budget). Evidence lives in `.gamestudio/evidence/<FEATURE-ID>/`.
- Validate after edits: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py validate .gamestudio/levels/<file>.level.json`.

---

## 11. Anti-patterns

| Anti-pattern | Symptom | Fix |
|---|---|---|
| Eyeballing 10 outputs | "Looks great!" then players find broken seeds | ERA over ≥ 1,000 seeds, plus inspecting extremes |
| Weighted sum including validity | Pretty unsolvable levels ship | Hard constraints reject; scores only rank survivors |
| Scramble depth as difficulty | "Hard" puzzles solved in 6 moves | Forward solver min_moves plus grading features |
| Solver budget exhaustion treated as pass | Rare unsolvable levels in production | Unknown = reject; track the unknown rate |
| Unseeded bots | Win rates jump between runs; regressions invisible | Seeded bot runs, fixed run counts, margins reported |
| LLM as the solvability judge | Confident claims of solvable levels that are not | Solver or bot gates only |
| Testing the generator, not the pipeline | Generator passes; repair pass or serialisation breaks levels | Gates run on the final serialised artefact the game loads |
| Infinite reroll loops on device | Hangs on low-end phones for unlucky seeds | Attempt cap plus cached fallback |
| No rejection logging | Cannot tell why acceptance dropped | Log stage and reason per candidate |

---

## 12. Volatile facts (as of Oct 2026, verify before relying)

- LLM plus GAN Snake level generation: 87% playable for easy levels, 36% for hard, validated with A* pathfinding. Source: [FedCSIS 2025, Annals of Computer Science and Information Systems vol. 43](https://annals-csis.org/Volume_43/drp/1909.html).
- Early LLM level-generation study reporting novelty, playability and diversity, with prompt controllability. Source: [arXiv 2302.05817](https://arxiv.org/pdf/2302.05817).
- PCG survey with LLM integration insights. Source: [arXiv 2410.15644](https://arxiv.org/pdf/2410.15644).
- Evaluation taxonomy for PCG (Withington, Cook, Tokarchuk, FDG 2024). Source: [arXiv 2404.18657](https://arxiv.org/pdf/2404.18657).
- Simulation-based diversity and difficulty metrics from agent behaviour. Source: [Beukman et al., arXiv 2201.10334](https://arxiv.org/abs/2201.10334v2).
- King's human-like playtesting bot used to predict difficulty across more than 1,000 new Candy Crush Saga levels. Source: [Gudmundsson et al. 2018](https://www.Gwern.net/doc/reinforcement-learning/imitation-learning/2018-gudmundsson.pdf).
- GDC 2026 State of the Game Industry: among generative-AI users, PCG was 10% of uses (brainstorming 81%, code assistance 47%). Source: [GDC](https://gdconf.com/article/gdc-2026-state-of-the-game-industry-reveals-impact-of-layoffs-generative-ai-and-more/).
- Unreal Engine 5.7 declared its PCG framework production-ready; reported about 2× faster than 5.5, and Epic advises verifying runtime performance before production use. No mobile-specific guidance was found. Sources: [Unreal Engine What's New](https://www.unrealengine.com/whats-new), [Digital Production](https://digitalproduction.com/2025/11/12/unreal-engine-5-7-foliage-pcg-and-in-editor-ai/).