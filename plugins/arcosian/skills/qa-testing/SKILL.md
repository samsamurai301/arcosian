---
name: qa-testing
description: Game QA codex - game test pyramid, risk-based testing, deterministic scripted playthroughs, bots (random, greedy, MCTS, RL), difficulty and softlock detection with match3_sim.py and puzzle_solver.py, structural UI and VLM visual QA, device matrices, crash and ANR handling, human playtests, bug and severity templates. Use when asked "test this build", "write a playthrough", "find softlocks", "visual QA", "device matrix" or "triage crashes".
---

# QA and Testing for Mobile Games

Games fail in ways ordinary apps do not: they have state spaces too large to enumerate, balance that is "wrong" without any exception being thrown, and visuals that are broken while every assertion passes. QA here means a layered system: cheap deterministic tests for logic, bots for coverage and balance, structural and visual checks for presentation, real devices for hardware reality, and humans for fun. This skill tells you which layer to use for which risk and how to write results into the shared report formats.

## What this skill gives you

- A game test pyramid and a risk-based method for deciding what to test first (`references/test-strategy-and-playthroughs.md`).
- Recipes for deterministic scripted playthroughs using the Godot and Unity template runners and the playtest-report schema.
- A bot ladder (random, greedy, MCTS, RL, human-like) with difficulty and softlock detection using `match3_sim.py` and `puzzle_solver.py`, plus a visual QA stack with honest false-positive rates (`references/bots-and-visual-qa.md`).
- Device matrix design, device farms, crash symbolication, ANR and Android vitals thresholds, human playtest protocols, a bug template and severity definitions (`references/devices-crashes-human-playtests.md`).
- A definition of what counts as playthrough gate evidence.

## Core models

**1. Test the layer where the bug lives.** Logic bugs belong in headless unit and simulation tests (fast, deterministic). Flow bugs (FTUE, shop, level transitions) belong in scripted playthroughs. Balance and softlock bugs belong in bots and solvers over thousands of runs. Presentation bugs belong in structural and visual checks. Hardware bugs belong on real devices. Fun belongs to humans.

**2. Determinism is the enabling property.** Seeded RNG, injected time, and a sim-core separate from presentation turn flaky "it sometimes fails" into reproducible "seed 42, step 17". Every playthrough records its seed; every bug report carries it. Architecture that blocks this (RNG from global state, wall-clock in logic) is a QA defect to raise early.

**3. Risk first.** Rank features by likelihood of failure times cost of failure (money paths, save data, progression blockers, first-session flow, store-policy items). Spend test effort proportionally; do not spread it evenly.

**4. Bots are measurement instruments, not players.** A greedy bot's win rate is a floor on skill, a random bot's is a floor on luck; the spread between them tells you how much skill the level rewards. Use bots to find softlocks, dead ends, impossible levels and difficulty outliers, then confirm with humans.

**5. Pixels are the last resort for UI checks.** Structural checks (text overflows its box, element off-screen, missing sprite, null texture) are more reliable than image comparison. Golden images catch regressions on fixed screens; VLM review is triage with known false positives, never a gate on its own.

**6. Real devices find what emulators hide.** Memory kills, GPU driver bugs, notch and cutout layouts, thermal throttling, touch latency, audio routing. Test on the low tier and on a spread of OEMs.

**7. Severity is about player impact.** Blocker (cannot ship; progression or data loss, crash on launch), major, minor, polish. A pass verdict cannot coexist with a blocker or any crash.

## Decision procedures

### A. Plan testing for a new feature (build-feature gate)
1. Read the feature spec; list risks: logic, state transitions, persistence, economy impact, UI states, device-sensitive parts, analytics events.
2. For each risk pick the layer (core model 1) and write the test names before writing tests.
3. Logic: unit tests on the sim-core with fixed seeds, edge cases (zero, max, overflow, empty, simultaneous events).
4. Flow: one scripted playthrough that drives the feature through its happy path and one for its main failure path; save as a template-format script.
5. Run the playthrough through the template runner (commands under "Using the ontology" below), which writes a playtest-report JSON; validate it against `playtest-report.schema.json`.
6. Add the feature to the bot run if it affects progression or balance; check softlocks equal zero.
7. Add the feature's screens to structural UI checks and golden images where stable.
8. Record evidence paths in the feature's gate record.

### B. Hunt softlocks and impossible levels
1. Puzzle with exact solver (sliding, sokoban, sort, lights-out): run `puzzle_solver.py --level <spec>`; unsolvable or over the move limit is a blocker.
2. Match-3: run `match3_sim.py --level <spec> --runs 500 --bot greedy|random|cascade`; compare win rates to the difficulty target; zero wins is a level bug.
2a. Blast / collapse levels cannot go through `match3_sim.py` (swap rules only; it rejects any `layout.type` other than `match3`): use a project-owned simulator and bots, as in step 3.
3. Other genres: write a seeded bot over the sim-core and flag runs that exceed a move cap or stop having legal moves (softlock definition in the report schema). The templates' bot mode is exactly this for the sample game (`--mode=bot` in Godot, `-gsMode bot` in Unity).
4. Reproduce with the seed; file with the bug template.

### C. Choose the test devices
1. Start from analytics or market data; define low, mid and high reference devices (see `mobile-performance`).
2. Add coverage axes: Android OEM skins, GPU vendors, screen aspect ratios and cutouts, OS versions at the floor and the latest, one tablet if supported, one older iPhone.
3. Own the low-tier device physically; rent the rest from a farm per release candidate.

### D. Triage a crash report
1. Group by signature (top frames) and device, OS, app version.
2. Symbolicate: native crashes with the matching symbols (dSYM for iOS, NDK symbols or Unity symbol files for Android); managed stacks via engine mapping.
3. Rank by affected users and by proximity to vitals thresholds; reproduce on a matching device with the logged seed or session trace.
4. Fix, add a regression test at the lowest possible layer, verify on the farm devices that showed it.

### E. Release readiness (QA view)
1. Deterministic playthrough passes on the release build (verdict pass, zero crashes, no blocker).
2. Bots: zero softlocks over the agreed run count; difficulty within band.
3. Visual QA clean on key screens at all supported aspect ratios.
4. Device farm sweep: no new crashes or ANRs; crash and ANR projections under store thresholds.
5. Human playtest of the first session if the FTUE changed; critic pass on findings.

## Mobile specifics

- Interruptions: incoming call, notification shade, backgrounding mid-animation, low memory kill and restore, airplane mode toggle mid-purchase, rotating the device if supported.
- Input: multi-touch, palm rejection, edge swipes (system gesture conflicts), fast taps, long-press, drag off-screen, touches during transitions.
- Layout: notches and cutouts, safe areas, foldables, tall aspect ratios, font scaling and system accessibility settings, dark mode, language expansion (German is long).
- Connectivity: offline start, flaky network, server errors in purchase and sync flows; ads and SDKs failing to load.
- Store-driven items: Android vitals thresholds, 16 KB alignment, permission prompts, privacy flows, age gates.
- Time: system clock changes (cheating or travel), daylight savings, day rollover during a session for daily rewards.

## Anti-patterns

| Anti-pattern | Detect | Fix |
|---|---|---|
| "QA at the end" | Bugs found in the last week | Playthrough and bot per feature, in CI |
| Non-deterministic tests | Flaky reruns | Seeded RNG, injected clock, sim-core separation |
| Testing only the happy path | Bugs in purchase failure, resume, offline | Failure-path playthroughs and interruption tests |
| Trusting emulator results | Device-only crashes in production | Low-tier real device and farm sweep |
| Screenshot diff on everything | Flaky failures from drivers and animation | Structural checks first; goldens on stable screens with tolerances |
| VLM as gate | Fails on noise, misses real bugs | Triage only; majority vote; human confirm |
| Win-rate as the only balance metric | Levels feel same but win rates match | Add move-efficiency, near-miss and attempts-to-win distributions |
| Closing bugs without a regression test | Same bug returns | Test at lowest layer before closing |
| Severity by developer effort | Easy-to-fix blockers labelled polish | Severity by player impact only |

## Using the ontology

- Playthroughs, bots, personas and human sessions all write `playtest-report` JSON (`${CLAUDE_PLUGIN_ROOT}/scripts/schemas/playtest-report.schema.json`): `mode` is `deterministic_script`, `bot`, `persona` or `human`; metrics include `win_rate`, `softlocks`, `crashes`, `errors`; `findings` carry severity blocker, major, minor or polish. Reports go in `.gamestudio/playtests/*.playtest.json`; the playthrough gate accepts them as evidence.
- Level specs (`level-spec.schema.json`) feed the solvers: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/puzzle_solver.py --level <spec> --json` and `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/match3_sim.py --level <spec> --runs 500 --bot greedy --json`.
- Template runners (both write playtest-report JSON; exit 0 pass, 1 fail or softlocks, 2 usage error; time metrics are estimates at 0.8 s per accepted move):
  - Godot (`${CLAUDE_PLUGIN_ROOT}/templates/godot-mobile`): `godot --headless --path <project> -s res://tools/playtest/runner.gd -- --mode=script --script=res://tests/playthroughs/smoke.json --out=<abs>/playthrough.json [--seed=1]`, or `-- --mode=bot --bot=greedy|random --runs=200 --seed=1 --out=<abs>/bots.json`.
  - Unity (`${CLAUDE_PLUGIN_ROOT}/templates/unity-mobile`): `Unity -batchmode -nographics -projectPath <p> -executeMethod Game.EditorTools.PlaytestRunner.Run -gsMode script -gsScript Assets/_Game/Tests/Playthroughs/smoke.json -gsOut <abs>/playthrough.json -quit`, or `-gsMode bot -gsBot greedy|random -gsRuns 200 -gsSeed 1 -gsOut <abs>/bots.json`. The EditMode unit gate is `-runTests -testPlatform EditMode -testResults <abs>/unit.xml` (NUnit XML); the full command table is in `templates/unity-mobile/README.md`.
- Validate reports: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_json.py`.
- Performance scenarios reuse the same deterministic drivers; see `mobile-performance`. The Godot template's perf gate producer is `tools/perf/perf_probe.gd` (a bot-driven desktop proxy that writes a perf-report JSON; headless runs are CPU-only); the Unity template has none.
- Agents: `arcosian:qa-lead` owns strategy and gates; `arcosian:player-simulator` produces persona reports; workflow `/arcosian:playtest-sweep` orchestrates them.

## Reference library

| File | What it contains | When to read |
|---|---|---|
| `references/test-strategy-and-playthroughs.md` | Game test pyramid, risk-based testing, deterministic scripted playthroughs with the template runners, playtest-report schema | Planning tests, writing a playthrough, producing gate evidence |
| `references/bots-and-visual-qa.md` | Random, greedy, MCTS, RL and human-like bots; difficulty and softlock detection with the simulators; structural UI checks, golden images, VLM review with voting and false-positive rates | Balance and softlock hunting, visual regression |
| `references/devices-crashes-human-playtests.md` | Device matrices, farms, crash symbolication, ANRs, Android vitals, human playtests, bug template, severity definitions | Device strategy, crash triage, running real-player sessions |

## Volatile facts (as of Oct 2026 — verify)

| Fact | Source |
|---|---|
| Android vitals bad-behaviour thresholds: user-perceived crash rate 1.09%, ANR rate 0.47% overall, 8% per phone model | https://developer.android.com/games/optimize/vitals |
| VLMs for game QA: best image glitch detection in one 2025 benchmark was about 83%, with a notable false-positive rate; authors judged VLMs not ready for many QA tasks | https://arxiv.org/abs/2505.15952 |
| Best LLM QA agent found 48.39% of bugs on a 124-bug benchmark | https://arxiv.org/abs/2604.02648 |
| Firebase Test Lab Game Loop tests on iOS and Android | https://blog.back4app.com/firebase-test-lab/ |

## Related skills

- `mobile-performance` - perf scenarios, soak tests and the perf gate that reuse the playthrough drivers.
- `game-architecture` - sim-core and determinism that make testing possible.
- `progression-difficulty` - difficulty targets that bot results are judged against.
- `level-design` - level specs and solvers.
- `player-analytics` - telemetry that complements pre-release QA.
- `store-release` - store technical gates and compliance checks.
- `mobile-ux` - layout and input behaviours worth testing.
