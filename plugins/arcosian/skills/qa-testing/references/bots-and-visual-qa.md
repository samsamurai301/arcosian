# Bots, Difficulty and Visual QA

This file covers the two automated QA families that go beyond scripted flows. First, bots: random, greedy, Monte Carlo tree search, reinforcement learning and human-like policies, and how to use them (with `match3_sim.py` and `puzzle_solver.py`) to measure difficulty, find softlocks and catch impossible levels. Second, visual QA: structural UI checks, golden-image tests, and VLM review with majority voting, including the published false-positive evidence that dictates how far to trust each. The guiding rule is that bots measure, solvers prove, and humans judge.

## Contents
1. The bot ladder
2. Choosing a bot
3. Difficulty measurement
4. Softlock and dead-end detection
5. Using puzzle_solver.py
6. Using match3_sim.py
7. Bot-run procedure and report mapping
8. RL and learned agents: when they pay
9. Black-box AI QA services
10. Visual QA stack
11. Structural UI checks
12. Golden images
13. VLM review with voting
14. Checklists and worked examples
15. Volatile facts (as of Oct 2026 — verify)

## 1. The bot ladder

| Bot | How it plays | Cost to build | What it tells you |
|---|---|---|---|
| Random | Uniform over legal actions | Trivial | Luck floor; crash, softlock and invariant fuzzing |
| Greedy | Best immediate score or goal progress | Low | Skill floor of a casual player; difficulty band |
| Heuristic or scripted persona | Rules mimicking a player type (rusher, completionist, spender) | Medium | Persona-specific pacing and economy outcomes |
| Search (MCTS, beam, lookahead) | Simulates futures using the sim-core | Medium (needs a fast forkable sim) | Near-optimal play; true solvability and skill ceiling |
| Exact solver | Exhaustive or A* over the state graph | Medium, game-specific | Proof of solvability and optimal moves (small state spaces) |
| RL agent | Learns a policy by trial | High | Emergent exploits; playstyles; large non-searchable games |
| Human-like (noise, delay, error model) | A strong policy degraded by reaction time, misclicks, imperfect planning | Medium | Realistic win rates and attempts-to-win for casual populations |

Decision rule: always run random and greedy (cheap, universal); add search or exact solvers where the sim-core is fast and forkable; add RL only when the game is too large for search and you have a stable sim interface.

## 2. Choosing a bot

| Game type | Primary bot | Why |
|---|---|---|
| Sliding, sokoban, sort, lights-out | Exact solver | State space small enough to prove solvability and min moves |
| Match-3 | Greedy and cascade (lookahead) bots | Randomness in refill makes exact solving infeasible; need win-rate distribution |
| Merge, idle, incremental | Scripted persona bots over the economy sim | Pacing and economy balance matter more than tactics |
| Card, deck-builder | MCTS or heuristic bots | Imperfect information handled by sampling |
| Runner, action | Input-level bots with simple reflex rules, or RL | Needs real-time sim; difficulty via reaction-time model |
| Strategy, tower defense | Scripted build orders plus random perturbation | Balance across strategies |

## 3. Difficulty measurement

Primary signals per level (from a few hundred seeded runs):
- Win rate of each bot; spread (greedy minus random) estimates skill depth.
- Attempts-to-win distribution for a human-like bot: median and tail (p90). Tail is where players quit.
- Move efficiency: moves used divided by move limit at win; near-1.0 means razor-thin levels.
- Near-miss share: losses that ended within a small margin of the goal; high values feel unfair or exciting depending on the genre.
- Outlier detection across a level sequence: compute the difficulty index (for instance, 1 minus greedy win rate) per level and flag levels more than about two standard deviations from a local moving average, plus any level where difficulty drops sharply below its neighbours (a "free" level) or spikes above.

Calibrate bots against reality when live data exists: compare bot win rate to player first-attempt win rate per level; fit a simple mapping (often monotone but not 1:1). Until then treat bot numbers as relative, not absolute. Targets live in the level spec (`difficulty_target`) and in `progression-difficulty`.

## 4. Softlock and dead-end detection

Definitions: a softlock is a reachable state with no legal progress and no automatic recovery (no legal move, no way to reach the goal, no reset or shuffle offered). An impossible level is a start state with no winning line.

Detection recipe:
1. Define `legal_actions(state)` in the sim-core; zero legal actions and not terminal is a softlock.
2. For games with a shuffle or auto-reshuffle, test that the reshuffle always yields at least one legal move.
3. Cap run length (as the Godot runner does with its move cap): exceeding it without termination is a suspected softlock or a loop.
4. For solvable-by-design puzzles, run the exact solver on every level in CI.
5. Run random bots with many seeds and record the first state at which each stuck run stopped; cluster those states.
6. Save the seed and the action trace of every softlock for reproduction; file with the bug template.

## 5. Using puzzle_solver.py

`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/puzzle_solver.py --level <level-spec.json> [--algo bfs|astar] [--max-nodes N] [--json]`

- Supports `layout.type` of sliding, sokoban, sort and lights_out; input is a level-spec (`level-spec.schema.json`).
- Reports solvable, min_moves (optimal for BFS and for the admissible A* heuristics used), a move path, nodes expanded and difficulty signals; also checks the move limit.
- Move notation: sliding = tile plus direction; sokoban = u/d/l/r (capital means push); sort = "i->j" with 1-based tubes; lights_out = "row,col" presses solved by GF(2) elimination (the algorithm flag is ignored).
- Exit codes: 0 solvable within the move limit; 1 unsolvable, over the limit or search truncated; 2 usage or input error. A truncated search means "unknown", not "unsolvable"; raise `--max-nodes` or simplify.

Use: a CI job loops over all level files and fails on exit 1. Write `min_moves` back into the spec's `solver` block so design and QA agree on par values. Compare `min_moves` to `moves_or_time_limit`: slack ratio = limit / min_moves; very tight (below about 1.1) is expert-only; very loose (above about 2) is relaxed. Interpret by the target audience.

## 6. Using match3_sim.py

`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/match3_sim.py --level <level-spec.json> [--runs N] [--bot greedy|random|cascade] [--seed S] [--json]`

- Real match-3 engine with swap rules (a swap is legal only if it makes a run of 3 or more or involves a colour bomb or two specials), gravity, cascades, seeded refill, specials (4-run line clearer, L/T bomb, 5-run color bomb), obstacles (box and ice with hit points) and goals (collect, clear, score). It requires `layout.type: "match3"` and does not implement blast / collapse (tap-a-group) rules: such levels need their own simulator.
- Bots: random (any valid move), greedy (best immediate clear, goal-weighted), cascade (greedy top five, then rollouts with unseen random refill).
- Each run uses a fresh random fill for `.` cells; `--seed` makes the batch reproducible. Exit 0 ok; 1 selftest failure or the bot never won (check the level); 2 usage or input error.

Procedure per level:
1. Run `--bot greedy --runs 500` and `--bot random --runs 500`; record win rates.
2. Run `--bot cascade` for a stronger-player estimate.
3. Compare to the level's `difficulty_target.win_rate`: casual-targeted levels should have a greedy win rate near the target; if cascade is far above greedy the level rewards planning (good for puzzle depth, bad for casual pacing).
4. Zero wins across all bots: the level is likely impossible or mis-specified (goal count, blocked layout); inspect the spec before tuning numbers.
5. Record bot win rates and runs in the spec's `solver` block, write the playtest-report (`mode: "bot"`) with `win_rate` and softlocks.

Worked example: level target win rate 0.6 for the median casual player. Greedy 0.72, random 0.18, cascade 0.91. Skill depth is high (0.54 spread). A casual player is between random and greedy, so the real win rate will likely sit below 0.72, possibly near the target; do not nerf. A second level with greedy 0.15, cascade 0.17, random 0.02 has low depth and low win rate: tuning moves or obstacle HP is the lever, not hints.

## 7. Bot-run procedure and report mapping

1. Seed list: seeds 1..N (N of 200 for PR checks, 1,000+ nightly).
2. For each run record: win or loss, moves, score, steps to end, softlock flag, error count.
3. Aggregate to `metrics.win_rate`, `metrics.softlocks`, `metrics.errors`, `metrics.crashes`.
4. Findings: one per softlock cluster or impossible level, severity blocker for progression-blocking ones.
5. `runs`, `seed` fill the report header; notes state the bot type and what it cannot do.
6. Godot template: `godot --headless --path <project> -s res://tools/playtest/runner.gd -- --mode=bot --bot=greedy|random --runs=200 --seed=1 --out=<abs>.json`; exit 1 on softlocks. Unity template: `Unity -batchmode -nographics -projectPath <p> -executeMethod Game.EditorTools.PlaytestRunner.Run -gsMode bot -gsBot greedy|random -gsRuns 200 -gsSeed 1 -gsOut <abs>.json -quit`; exit 1 on softlocks. Both bots pick among the moves the pure slide helper reports as legal, and a run that exceeds 5,000 moves without ending counts as a softlock.

Statistical care: with N runs the 95% interval on a win rate p is about plus or minus 1.96 times sqrt(p(1-p)/N). At p=0.5 and N=200 that is roughly plus or minus 7 points; use 1,000 runs for ±3. Compare bots with the same seeds where possible.

## 8. RL and learned agents: when they pay

Pays off when: the game is too large for search, you need to discover exploits or dominant strategies in an economy or combat system, or you want diverse playstyles for balance coverage. Costs: reward design, a fast headless sim, training compute, brittleness when the game changes.

Practical guidance:
- Start with scripted and search bots; escalate only if they fail to cover the space.
- Reward shaping must not reward the bug you want to find; log the policy's behaviours, not just returns.
- Unity ML-Agents is maintained (4.x series) per the research notes; Godot has community RL bridges (verify).
- Treat a trained agent as a stress tester: its discoveries (infinite loops, overpowered combos) become unit tests and balance changes.
- Research agents that play from pixels are weak: one 2025 benchmark of VLM agents on classic games reported under 1% average progress, and a 2026 bug-finding benchmark saw a leading agent find under half of 124 verified bugs. Expect assistance, not autonomy.

## 9. Black-box AI QA services

Several vendors market agents that look at the screen and act with no SDK (nunu.ai, modl.ai, Razer QA Companion-AI, among others). They suit smoke tests, menu and flow exploration and crash or softlock hunting on real devices, and need no engine integration. Caveats from the research: no independent effectiveness numbers were found; timing-critical gameplay is reportedly not fully supported by some; reports typically contain screenshots, video, logs and an AI severity score that needs human confirmation. Treat them as another coverage source and keep deterministic tests as the gate.

## 10. Visual QA stack

Layered, most reliable first:

| Layer | Detects | Reliability | Gate? |
|---|---|---|---|
| Structural checks (engine introspection) | Text overflow, off-screen elements, overlapping rects, missing sprites, null textures, wrong font, touch targets too small | High | Yes |
| Golden images (pixel or perceptual diff) | Unintended rendering changes on fixed screens | High for stable screens, flaky across GPUs and drivers | Yes with tolerances, on a fixed renderer |
| Screenshot matrix capture | Layout at all aspect ratios, locales, dark mode | Collection step | n/a |
| VLM review with rubric | Clipping, missing textures, placeholder art, overlaps, obvious glitches | Medium; false positives and misses | No; triage only |
| Human visual critique (art director, critic agent) | Style, polish, readability | Subjective but the real bar | Taste checkpoint |

Capture matrix: key screens (main menu, core gameplay at three states, shop, results, settings, a popup) x aspect ratios (short, standard, tall, tablet) x locales (English, one long language such as German, one CJK, one RTL if supported) x dark or light if relevant. The Godot template has `tools/capture/screenshot_mode.gd` producing `menu.png`, `game.png`, `results.png` (needs a rendering context, not headless).

## 11. Structural UI checks

Implement as a pass over the UI tree after each screen settles:
1. Every text element's rendered bounds fit within its container, with no truncated glyphs (compare required text size with box size).
2. Every interactive element is on-screen, inside the safe area, and has a touch target of at least about 44-48 density-independent pixels per side (platform guidance; verify current figures).
3. No unintended overlap between sibling interactive elements or between HUD and notches.
4. No missing sprite, null texture, default placeholder, or magenta fallback materials.
5. Localized strings exist for every key; no raw keys showing.
6. Contrast ratio of text over background meets the chosen accessibility target (see `accessibility-localization`).
Run per locale and aspect ratio; emit findings with screenshot references. In Unity use scene introspection (or AltTester's object tree); in Godot walk the Control tree and compare `get_combined_minimum_size()` and `get_global_rect()` against parents and the viewport.

## 12. Golden images

Unity's Graphics Test Framework offers `ImageAssert.AreEqual()` comparing a rendered camera output to a reference image with per-pixel and whole-image thresholds; results write `TestResults.xml` and actual images that you approve into reference folders organised by color space, platform and graphics API. Principles that apply to any engine:
- Render on one fixed environment (fixed renderer, resolution, seed, locale, time); animation frozen or advanced to a known frame.
- Simplify test scenes where possible (solid background, no skybox) to reduce false positives.
- Thresholds: a small per-pixel tolerance plus a cap on the fraction of differing pixels; tune from observed noise between identical runs.
- Update goldens only through a reviewed approval step, never automatically on failure.
- Store goldens per platform and graphics API; cross-GPU comparison causes the flakiness the research warns about.
- Perceptual metrics such as SSIM can reduce false alarms compared with raw pixel diff; I did not verify game-CI usage, so evaluate on your own noise data.

## 13. VLM review with voting

Evidence (VideoGameQA-Bench, 2025, older models): image glitch detection best about 83% accuracy for one model and about 65% for another; visual regression best about 45%; UI unit tests best about 40%; localizing glitch onset in video at most about 36%; one model's image false-positive rate of 17.8% implies roughly 20% precision when glitches appear in about 5% of images. Models hallucinate clipping, miss unusual poses and small UI details. Authors concluded VLMs are not ready for many game QA tasks. Frontier models are likely better now but no updated numbers were found, and no benchmark of "polish" judgments exists.

Procedure that respects those numbers:
1. Give the VLM a strict rubric (list any text clipping, missing textures, overlapping UI, placeholder art, wrong language) and ask for evidence regions, not scores.
2. Sample each screenshot several times (3 to 5) with varied prompts or temperature; flag only issues reported by a majority.
3. Pair with structural checks: a VLM flag that structural checks do not confirm goes to a human, not to the bug tracker.
4. Estimate your own precision: label 50 flagged items; track precision per rubric item; drop rubric items below roughly 50% precision.
5. Budget for prevalence: if true defects are rare, even a good model yields mostly false alarms; do not let flags block builds.
6. Use VLMs well for: first-pass triage of a large screenshot matrix, finding obviously broken screens, comparing before and after screenshots with a human-readable summary.
7. Do not use VLMs for: aesthetic sign-off, fun, balance, or as the only evidence for a gate.

## 14. Checklists and worked examples

Visual QA checklist:
- [ ] Capture matrix defined and automated.
- [ ] Structural checks run per locale and aspect ratio, zero blocker findings.
- [ ] Goldens approved for stable screens; tolerance tuned.
- [ ] VLM triage run with majority voting; flags confirmed by structure or human.
- [ ] Findings logged with screenshot paths and severity.

Worked example: German locale breaks the shop. Structural check flags "Buy bundle" text overflowing the button (required width 1.4x the box). A VLM triage independently flags clipped text in 4 of 5 samples. The fix is a flexible button width with a smaller font cap, verified by the structural check; the golden for the German shop is added.

Worked example: bot-found softlock. Random bot, 1,000 seeds on a sort puzzle with extra empty tubes removed in a new level: 31 runs end with no legal pour. The first stuck states cluster: two tubes each topped with different colors and no empty tube. The exact solver confirms the level start is solvable but reachable dead ends exist; design adds an undo or an extra empty tube. Regression test: the level plus a seed list that previously reached the dead end.

## 14b. Review checklist

- [ ] Every level or content unit has at least a random and a greedy run recorded in its spec.
- [ ] Exact solver runs in CI for every solver-supported layout, failing the build on exit code 1.
- [ ] Softlock definition written down in the sim-core (legal_actions, terminal test) and tested.
- [ ] Seeds and action traces saved for every stuck or failing run.
- [ ] Bot win rates reported with run counts and an interval, not as bare percentages.
- [ ] Bot limitations stated in the report notes (no human error model, no learning, no fatigue).
- [ ] Results compared with live player data once soft launch starts, and the bot-to-player mapping updated.

## 15. Volatile facts (as of Oct 2026 — verify)

| Fact | Source |
|---|---|
| VideoGameQA-Bench figures (image glitch, visual regression, UI tests, FP rate) | https://arxiv.org/html/2505.15952v1 |
| GBQA: Claude Opus 4.6 baseline found 48.39% of 124 verified bugs in 30 games | https://arxiv.org/abs/2604.02648 |
| TITAN LLM agent: 95% task completion, 4 new bugs on two commercial MMORPGs | https://arxiv.org/abs/2509.22170 |
| VideoGameBench: VLM agents under 1% average progress in original results | https://arxiv.org/html/2505.18134v3 |
| Unity ML-Agents 4.0.3 (2026-04-17) maintained, not deprecated | https://docs.unity3d.com/Packages/com.unity.ml-agents@4.0/changelog/CHANGELOG.html |
| Unity Graphics Test Framework ImageAssert and reference image workflow | https://blog.unity.com/technology/graphics-tests-the-last-line-of-automated-testing |
| modl.ai black-box QA; nunu.ai plain-English tests; Razer QA Companion-AI (Mar 2026) | https://nunu.ai/blog ; https://www.razer.com/newsroom/company-news/razer-at-gdc-2026 |
