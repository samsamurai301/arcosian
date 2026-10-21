---
name: procedural-generation
description: 'Procedural generation codex: noise, fBm, domain warping, CA caves, BSP and room-and-corridor, wave function collapse, Poisson disk, Voronoi, L-systems, graph grammars, constraint and search PCG, runner chunks, roguelite runs, loot affixes, solvable puzzles, seeded PRNGs, daily seeds, replays, expressive range. Use when asked to "generate levels", "make it procedural", "add endless mode", "daily challenge" or "why are generated levels broken".'
when_to_use: 'Designing, choosing or debugging any generator (levels, maps, chunks, puzzles, loot, names), seeds and determinism, replays, and validating generated content with solvers and expressive range.'
---

# Procedural Generation

The studio's knowledge of how to make content with code, and how to make that content trustworthy. On mobile, procedural generation is rarely open-ended synthesis. It is usually **authored pieces plus rules plus a verifier**: runner chunks, roguelite rooms, puzzle boards generated backward from their solutions, loot tables, daily seeds. The algorithm is the easy part. The hard parts are guarantees (connected, solvable, fair), determinism (the same seed gives the same level on every phone and every build), and evidence (expressive range and solver gates over thousands of seeds). This skill gives the algorithms, the mobile patterns, the determinism engineering and the testing machinery, and hands off to `level-design` for authored level craft and to `progression-difficulty` for difficulty curves.

## What this skill gives you

- An algorithm shelf with pseudo-code, parameters, guarantees and failure modes: value, Perlin and simplex noise, fBm, domain warping, Worley, cellular-automata caves (with a measured parameter sweep), drunkard walk, BSP, room-and-corridor, wave function collapse (both models), Poisson disk, Voronoi/Delaunay, L-systems, shape and graph grammars (Dormans), agents, constraint solving, search-based PCG and MAP-Elites.
- Mobile PCG patterns that ship: runner chunk assembly with reaction-time fairness formulas, endless streaming and pacing directors, roguelite map/room/reward generation, loot affix systems with exact odds, guaranteed-solvable puzzles (backward generation), seeded daily challenges, naming generators.
- Determinism engineering: PRNG choice and porting traps (GDScript, C#, JS), unbiased bounded draws, stream architecture, float pitfalls, fixed point, replays and desync detection, daily seeds and shareable seed codes.
- Generate-and-test discipline: gate design and ordering, acceptance-rate economics, solver and bot gates with sample sizes, expressive range analysis (linearity, leniency), diversity checks, and LLM-assisted PCG with measured failure rates.
- Tools: `scripts/pcgkit.py` (PRNG reference vectors, seed derivation, daily seeds, seed codes, expressive range analysis with CI checks), plus the plugin's `pcg.py`, `puzzle_solver.py` and `match3_sim.py`.

## Core models

### 1. A generator is a pipeline, not an algorithm
Constructive core → optional repair → cheap gates → expensive gates (solver, bots) → scoring → diversity selection → curation → ship. Every stage logs seed, generator version, params and rejection reason. When content is broken, find the stage that should have caught it. (`references/generate-and-test.md` §1–2)

### 2. Local structure is cheap; global guarantees cost extra
Noise, CA, WFC and grammars give local coherence almost free. Connectivity, solvability, fairness and pacing come from **an extra constraint, a repair pass or a verifier**, never from the algorithm alone. For every generator, write down what it guarantees and what it does not (`references/algorithms.md` §1).

### 3. Authored quality, procedural variety
Hand-made pieces carry readability; rules and seeds recombine them (Spelunky's room templates on a guaranteed path; Dead Cells' hand-made rooms placed procedurally within an authored level structure). Pure synthesis is for things players read loosely: terrain, decoration, names. (`references/algorithms.md` §20, `references/pcg-for-mobile-games.md`)

### 4. Determinism is designed in, not patched in
Every generator is a pure function of (seed, generator_version, params). Use your own PRNG (PCG32 is the default), one stream per system (layout, loot, enemies, cosmetic), random access by key (`level_seed(i) = derive(root, "level:i")`), integer-only generation where possible, and a version bump whenever outputs change. (`references/determinism-and-seeds.md`)

### 5. Evidence comes from scale
Ten outputs prove nothing. Generate at least 1,000 seeds per parameter setting, run expressive range analysis, and inspect the extremes by eye. Gates and thresholds run in CI on every generator change. (`references/generate-and-test.md` §5)

### 6. Backward generation guarantees solvability, not difficulty
Working back from the solved state proves a solution exists. Difficulty must still be *measured* with a forward solver (min_moves, branching, dead-end share), then calibrated against real attempts. (`references/pcg-for-mobile-games.md` §6)

### 7. Fairness encodes human limits
Solvable is not fair. Encode perception, decision and gesture time: `min_spacing = speed × (t_decide + t_gesture + t_motion) × safety`, visibility before threat, no forced hits, one new obstacle type at a time. (`references/pcg-for-mobile-games.md` §2.2)

### 8. Variety lives in decisions, not pixels
"10,000 bowls of oatmeal" (Kate Compton): unique but perceptually identical outputs. Measure variety with play-relevant metrics (routes, solver paths, bot behaviour), duplicates after canonicalisation, and histogram coverage.

### 9. Cheap on device, expensive offline
Acceptance rate a gives 1/a mean attempts and `ln(0.01)/ln(1−a)` attempts at the 99th percentile. Generate on device only with high acceptance and cheap attempts, an attempt cap and a cached fallback. Everything else (search, constraint solving, large WFC, LLM output) runs offline and ships as data or verified seeds. (`references/generate-and-test.md` §3)

### 10. LLMs frame, generators build, solvers judge
LLMs are reliable for themes, names, parameters and high-level structure, and unreliable for exact spatial content: in one study, 87% of easy LLM-generated levels were playable but only 36% of hard ones. Never use an LLM as the solvability oracle. (`references/generate-and-test.md` §8)

### Rules of thumb (starting values; measure and tune)

| Topic | Start here |
|---|---|
| CA caves | Fill 0.45, rule "wall if ≥ 5 of 9", 4 steps; sharp connectivity cliff between 0.45 and 0.50 fill; always run a region pass |
| Drunkard walk | 30–45% coverage; momentum 0.5–0.7 for corridors; always cap steps |
| Room graphs | MST plus 10–15% of the remaining Delaunay edges as loops; choose the loop ratio from the verbs |
| fBm | 4–6 octaves, lacunarity about 2.0, gain 0.5; domain warp strength 0.5–4 × feature size |
| Poisson disk | k = 30; expect about area / (1.6 r²) points |
| WFC | Measure the contradiction rate over 1,000 seeds; fix the tileset if above about 5%; on device keep it small (≈ 32² cells) with a time budget |
| Runner fairness | Reaction-plus-gesture budget 0.6–0.8 s early, 0.4–0.5 s at peak; a rest chunk every 6–10 chunks |
| Sample sizes | ≥ 1,000 seeds for ERA; 200 bot runs to separate bands 15 pp apart; 500+ to tune within a band |
| Puzzle gates | Solver "unknown" (budget exhausted) = reject; store measured `min_moves`, never scramble depth |
| Dailies | UTC reset from server time; pre-validate 30–60 days ahead; override list in remote config |

## Decision procedures

### A. Should this content be procedural?

| Question | If yes | If no |
|---|---|---|
| Does content burn exceed authoring capacity? (`levels/week consumed > levels/week authored`; formula in `references/pcg-for-mobile-games.md` §1) | Procedural or hybrid for the tail | Handmade; PCG only for decoration |
| Is replayability or "a new run every time" a pillar? | Procedural runs, with authored pieces | Handmade |
| Do players need to share or compete on the same content? | Seeded generation plus dailies | Either |
| Is the quality bar "every level is designed"? | Hybrid: offline generation, human curation, ship as data | — |
| Can you build a fast, automatic validator for it? | Online generation is possible | Offline only, or handmade |
| Is it monetized random content? | Server-side rolls, disclosed odds; not seeded on the client | — |

Record the decision in `contract.content.levels.generation` (`handmade | procedural | hybrid`).

### B. Choosing an algorithm
1. Name the content type and the **guarantees** it needs (connected? solvable? exact counts? fair timing?).
2. Pick from the selection table in `references/algorithms.md` §1. Prefer the simplest constructive method that gets the look.
3. For each guarantee the algorithm lacks, choose a mechanism: constraint inside generation (best), repair pass, or verify-and-reject.
4. Check the cost against the device budget (`references/algorithms.md` §21). If it fails, move it offline.
5. Combine as a macro-to-micro pipeline: graph → layout → room content → decoration → validation, with one seed stream per stage.

### C. Building a new generator (end to end)
1. **Write the intent:** the experience, the 4–8 metrics that encode it (difficulty, structure, pacing, style), and the hard constraints. Put targets in the level-spec `difficulty_target`.
2. **Choose the representation:** tiles, chunks, graph, parameter vector. Parameters make difficulty targeting and LLM or designer control possible.
3. **Build the constructive core** with a seeded rng argument and no global randomness; give it a `GENERATOR_VERSION` constant.
4. **Write the validators first-class:** structure (flood fill), logic (lock-and-key), solvability (`puzzle_solver.py` or a custom solver), feel (bots).
5. **Determinism:** derive per-stage streams; golden-seed hash tests; PRNG port checked against `pcgkit.py prng` vectors.
6. **Expressive range:** at least 1,000 seeds → `pcgkit.py era` → inspect the corners → adjust parameters → repeat. Plot handmade reference levels in the same space.
7. **Gates in CI:** `--min-accept`, `--max-duplicates`, `--min-coverage`; solver and bot gates; golden hashes tied to the version.
8. **Device budget:** p95 generation time on the low-tier device; attempt cap; cached fallback; generation outside gameplay moments.
9. **Telemetry:** log seed, generator version and content id on level start, fail and quit; blocklist bad seeds server-side.
10. **Register it as a feature** in `features.json` and pass the five gates (see "Using the ontology").

### D. Debugging "generated levels are broken"
1. Get the **seed and generator version** from the bug or telemetry; reproduce it deterministically. If you cannot, fix determinism first (`references/determinism-and-seeds.md` §13).
2. Classify the failure: structural (unreachable), logical (key behind its lock), solvability, fairness (unreactable timing), perceptual (unreadable), or performance (hitch).
3. Find which gate should have caught it. If none exists, add it. If it exists but passed, the gate is wrong (often a solver budget treated as a pass, or a gate run before a later repair or serialisation step).
4. Run ERA over 1,000+ seeds with the new gate to measure how common the failure is, and look for the parameter region that produces it.
5. Fix in the generator (constraint) rather than the gate where possible; bump the generator version; update golden hashes; add the seed to the regression suite.

### E. Seeds, dailies and sharing (quick checklist)
- [ ] Seeds pass through `mix64`/`derive` before use (sequential seeds are correlated).
- [ ] One stream per system; cosmetic randomness isolated.
- [ ] Seed codes carry the generator version and mode; Crockford base32; optional check symbol.
- [ ] Dailies: UTC or fixed-hour reset from server time; generator version frozen per date; pre-validated; override list.
- [ ] Paid random outcomes are rolled server-side, never from client seeds.

### F. Reviewing someone else's generator (10 questions)
1. What does it guarantee, and how is each guarantee enforced?
2. What is its acceptance rate per difficulty band, measured over how many seeds?
3. What does its expressive range look like, and where do handmade levels sit in it?
4. Which outputs are at the extremes, and has anyone looked at them?
5. Is it deterministic across devices? Where are the golden tests?
6. What happens on device when it fails: cap, fallback, time budget?
7. How is difficulty measured: solver, bots, calibrated against players?
8. How many exact and near duplicates?
9. Is the seed or generator version logged in telemetry?
10. Could a seed or an LLM output produce offensive, unfair or monetisation-sensitive content, and what filters it?

## Mobile specifics

- **Sessions are 1–5 minutes:** a generated level must be readable in seconds, and a run must survive interruption. Save stream states at node boundaries and resume exactly.
- **Generate between moments:** on a worker thread during transitions or result screens, with a time budget (for example 2 ms per frame for streaming) and a cached fallback. Never generate on the main thread during play.
- **Low-end devices set the budget:** measure p95 generation time and memory on the low-tier reference device (`mobile-performance`). Interpreted scripts can be 10–50× slower than native code; use engine-native noise (Godot's `FastNoiseLite`) or precompute.
- **Offline-first:** generation must not need the network; daily seeds fall back to the last confirmed date key, with later submission.
- **Portrait camera limits look-ahead:** in runners, view distance (not difficulty) often caps speed (`references/pcg-for-mobile-games.md` §2.2).
- **Readability over novelty:** one new element at a time, consistent visual language for hazards, and generated text that fits the narrowest label in every locale.
- **Battery and heat:** heavy generation in bursts (big WFC, search) drains battery; ship such content as data.

## Anti-patterns

| Anti-pattern | How to detect it | Fix |
|---|---|---|
| One global RNG for everything | Adding a VFX random call changes levels; golden hashes churn | Stream per system; `derive(root, name)` |
| Engine or OS RNG for seeded content | Seeds differ between platforms or engine versions | Ship your own PRNG; check it against vectors |
| Algorithm assumed to guarantee connectivity | Unreachable exits in bug reports | Flood fill gate plus repair or reject |
| Scramble depth used as difficulty | "Hard" puzzles solved in a few moves | Forward solver `min_moves` plus grading features |
| Ten-sample validation | Surprises after launch | ERA over ≥ 1,000 seeds; inspect extremes |
| Unbounded reroll on device | Hitches or hangs on unlucky seeds | Attempt cap plus cached fallback; offline if acceptance < ~0.2 |
| Float-heavy generation with libm trig | Shared seeds differ between iOS and Android | Integer or fixed point; trig tables |
| Unique but samey output ("oatmeal") | High duplicate-like share; one dominant histogram bin | Diversity metrics, MAP-Elites quotas, more authored variety |
| LLM grids shipped without solver gates | Hard content broken at high rates | Solver gates plus bounded repair; LLM for framing only |
| Generator changes without version bumps | Old seeds and dailies silently change | `generator_version` in seeds, saves, dailies; CI guard |
| Seeded client-side loot boxes | Predictable paid outcomes | Server-side CSPRNG rolls, disclosed odds |

## Using the ontology

| PCG concept | Where it lives | Notes |
|---|---|---|
| Authored vs procedural decision | `contract.content.levels.generation` (`handmade|procedural|hybrid`), `content.levels.target_count`, `content.levels.spec_ref` | Justify with content-burn numbers |
| Determinism requirement | `contract.technical.deterministic` | Per-system levels (L0–L4) in notes or the architecture doc |
| Generated level | `level-spec.schema.json` → `layout` `{"type": "generator", "generator": "pcg.py cave", "seed": 17, "params": {...}}` | Or a concrete grid / typed layout after baking |
| Difficulty target and measurement | `level-spec.schema.json` → `difficulty_target` {`win_rate`, `attempts_p50`}; `solver` {`solvable`, `min_moves`, `bot_win_rate`, `runs`} | Solver fields stay null until a tool has run |
| Rhythm | `level-spec.schema.json` → `teach` (`teach|test|twist|reward`) | Sequence generated pools with it |
| Bot sweeps | `playtest-report.schema.json` (`mode: "bot"`, `runs`, `seed`, `metrics.win_rate`, `metrics.softlocks`) | Evidence for the playthrough gate |
| Generation performance | `perf-report.schema.json` (scenario "generate level N", `frame_ms.p95`, `memory_mb.peak`) | Evidence for the perf gate |
| Loot and drop economy | `economy-model.schema.json` nodes (`source` on `per_level_win`, with `probability`) | Simulate drop rates with `economy_sim.py` |
| Generator as a feature | `features.json` (area `content` or `tech`), five gates with evidence under `.gamestudio/evidence/<ID>/` | static, unit (golden seeds), playthrough (bots), visual (sampled outputs), perf |
| Generated assets (art via the gateway) | `assets/manifest.json` (`seed`, `prompt`, `model`, `provider`) | Asset seeds are provider seeds, not gameplay seeds |

**Tools.**

| Task | Command |
|---|---|
| Generate a map | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/pcg.py cave --w 48 --h 32 --seed 17 --json --out .gamestudio/levels/gen/cave_17.json` |
| Expressive range plus CI gates | `python3 ${CLAUDE_PLUGIN_ROOT}/skills/procedural-generation/scripts/pcgkit.py era --in .gamestudio/levels/gen --x linearity --y density --keep "connectivity>=0.95" --min-accept 0.8 --max-duplicates 0` |
| PRNG port vectors | `pcgkit.py prng --algo pcg32 --seed 42 --seq 54 --n 6` · `pcgkit.py prng --algo splitmix64 --seed 1234567 --n 5 --json` |
| Unbiased bounded draws (port check) | `pcgkit.py prng --algo pcg32 --seed 7 --bound 6 --n 20` |
| Stream and daily seeds | `pcgkit.py seed derive --root 123456789 --stream layout --stream loot` · `pcgkit.py seed daily --date 2026-10-19 --salt mygame-v1` |
| Shareable seed codes | `pcgkit.py seed encode --value 123456789 --check` · `pcgkit.py seed decode --code 3nqk-8nu --check` |
| Solve or grade a puzzle | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/puzzle_solver.py --level .gamestudio/levels/w2_l014.level.json --algo astar --json` |
| Match-3 bot difficulty | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/match3_sim.py --level PATH --runs 500 --bot greedy --seed 1 --json` |
| Difficulty curve for generated ladders | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/difficulty_curve.py generate --levels 60 --pattern sawtooth --base 0.85 --floor 0.45 --period 5` |
| Validate a level spec | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py validate .gamestudio/levels/w2_l014.level.json` |
| Search the codex | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py kb "wave function collapse" --skill procedural-generation` |

`pcgkit.py` is stdlib-only (Python 3.9+), supports `--json`, uses exit codes 0/1/2 and passes `--selftest`. Delegate generator design and content pipelines to `arcosian:level-designer`, loot and drop economies to `arcosian:systems-designer`, determinism architecture to `arcosian:lead-engineer`, and gates and bot sweeps to `arcosian:qa-lead`.

## Reference library

| File | What it contains | Read it when |
|---|---|---|
| `references/algorithms.md` | Selection table; pseudo-code, parameters and failure modes for value, Perlin and simplex noise, Worley, fBm variants, domain warping, terrain and biome use; CA caves with a measured fill sweep; drunkard walk; BSP; room-and-corridor (place-and-reject, separation + Delaunay + MST, accretion); WFC tiled and overlapping; Poisson disk; Voronoi, Delaunay, Lloyd; L-systems; shape and split grammars; Dormans graph grammars, lock-and-key validation, cyclic generation; agents; CSP, SAT and ASP; search-based PCG, novelty search, MAP-Elites; composition patterns; device cost table | Choosing or implementing an algorithm; reviewing a generator's guarantees |
| `references/pcg-for-mobile-games.md` | Content-burn maths; runner chunk data model, fairness formulas with worked numbers, selection algorithm, ramps, pool repetition maths; streaming worlds and pacing directors; roguelite maps, rooms, encounter budgets, reward pacing; loot affix models with exact odds and time-to-find; backward and constructive puzzle generation recipes per puzzle type, difficulty grading, pipeline; daily challenge design; naming generators and filters; ship checklist | Building runners, roguelites, loot, puzzles, dailies or name generators for phones |
| `references/determinism-and-seeds.md` | Determinism levels L0–L4; PRNG comparison; PCG32, SplitMix64 and xorshift64* reference code and test vectors; GDScript, C#, JS and Python porting traps; unbiased bounds, floats, Fisher–Yates, alias tables, bags; stream architecture and save-scum policy; float divergence table and strategy ladder; fixed-point formats and operations; input-log replays, state hashes, server validation, ghosts; daily and weekly seeds; seed codes and sharing UX; what must not be client-seeded; CI checklist; volatile engine RNG facts | Seeds, dailies, replays, leaderboards, porting a PRNG, or any "same seed, different result" bug |
| `references/generate-and-test.md` | Generator taxonomy; pipeline stages; gate types and cost ordering with a worked example; acceptance-rate table; solver and bot gates with sample-size margins; expressive range analysis (Smith and Whitehead; later metric sets) with procedure and a worked run; diversity and duplicate measures; `pcg.py` and `pcgkit.py era` usage; LLM-assisted PCG evidence, roles, safe loop and failure-rate budgeting; four pipeline templates; ontology and five-gate mapping; anti-patterns; volatile facts | Validating any generator, setting CI gates, planning LLM use in content, or deciding on-device vs offline |
| `scripts/pcgkit.py` | PRNG reference outputs (PCG32, SplitMix64, xorshift32, xorshift64*, xoshiro128**), unbiased bounded draws, seed derivation, daily and weekly seeds, Crockford base32 seed codes, expressive range analysis with keep-filters and CI exit codes | Porting a PRNG, deriving seeds, analysing a batch of generated levels |

## Related skills

- `level-design` — authored level craft, teaching through levels, pacing within a level; consumes generated pools.
- `progression-difficulty` — difficulty curves, win-rate targets and DDA policy that generated ladders must follow.
- `game-architecture` — sim-core plus presentation split that makes deterministic generation and replays cheap.
- `gameplay-programming` — implementing generators, fixed-timestep sims and RNG streams in engine code.
- `qa-testing` — bot playthroughs, golden tests and the playthrough gate for generated content.
- `mobile-performance` — device-tier budgets for generation time, memory and streaming.
- `economy-design` — drop rates, loot sinks and sources, time-to-find in the economy model.
- `monetization` — ethical rules for paid randomness, odds disclosure and pity.
- `legal-ethics` — loot-box law, AI-content disclosure, trademark and offensive-content risk in generated text.
- `narrative-design` — quest and mission structures, tone for generated names and flavour text.
- `liveops` — daily and weekly challenge calendars, streaks and event seeds.
- `genre-playbooks` — genre conventions for runners, roguelites, puzzles and idle games.
- `mechanics-codex` — the mechanics that generated content combines.
- `game-ontology` — the schemas (level spec, playtest report, features) generated content is recorded in.
- `engine-godot` / `engine-unity` — engine-specific noise, threading and RNG APIs.
- `multiplayer-backend` — server-side validation of seeded runs and replays.
- `player-analytics` — logging seeds and content ids, finding bad seeds and mis-rated chunks.
- `accessibility-localization` — generated text length, fonts and locale-specific name grammars.
