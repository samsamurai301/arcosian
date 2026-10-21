---
name: playtest
description: Runs and interprets playtests for a mobile game build - deterministic scripted playthroughs, bot runs, persona playtests through the player-simulator agent, visual QA, and human TestFlight/internal rounds - and writes playtest reports. Use when the user says "playtest this", "does the FTUE work", "find softlocks", "run the bots", "simulate a casual player", or "QA this build".
argument-hint: "[feature id | build | persona names]"
---

# Playtest

Pick the cheapest method that can answer the question, run it reproducibly, and write findings that someone can act on.

## When to use

- A feature needs its `playthrough` gate (see `build-feature`).
- Before a milestone: FTUE, difficulty, softlock and economy-sanity checks.
- Someone asks "is it fun / clear / stuck?" and you need evidence beyond opinion.
- For a full sweep across modes and personas, run `/arcosian:playtest-sweep`.

## Inputs

`$ARGUMENTS`: a feature id (scope to its acceptance criteria), `build` (whole-game smoke and FTUE), or persona names from `references/personas.md`. Default is `build`.

## Choosing a mode

| Question | Mode | Cost | Catches | Misses |
|---|---|---|---|---|
| Does the flow still work after a change? | Deterministic script | seconds | regressions, broken wiring, state bugs | anything not scripted, feel |
| Is it solvable, how hard, where do bots stall? | Bots (greedy/random) | minutes | softlocks, difficulty cliffs, win-rate drift | comprehension, fun |
| Do real kinds of players understand and enjoy it? | Persona playtest | an agent run | confusing UI, dead time, pacing, friction | true taste, real emotion |
| Does it look right on screen? | Visual QA | minutes | overflow, safe areas, contrast, clipped text | motion feel |
| Will real people stay? | Human (TestFlight / Play internal) | days | everything, honestly | speed |

Agents do not replace humans. They make the human rounds count by removing the obvious problems first.

## Procedure

1. **Scope.** Read the contract's `ftue`, `loops`, `analytics.kpi_targets` and the feature acceptance list. Write down the questions this round must answer.
2. **Evidence dir.** `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py evidence-dir F012` for a feature; otherwise write into `.gamestudio/playtests/`.
3. **Deterministic script.** Author `tests/playthroughs/<name>.json`, then run:
   ```
   godot --headless --path <project> -s res://tools/playtest/runner.gd -- --mode=script --script=res://tests/playthroughs/smoke.json --out=<abs>/playthrough.json --seed=1
   Unity -batchmode -nographics -projectPath <p> -executeMethod Game.EditorTools.PlaytestRunner.Run -gsMode script -gsScript Assets/_Game/Tests/Playthroughs/smoke.json -gsOut <abs>/playthrough.json -quit
   ```
4. **Bots.**
   ```
   godot --headless --path <project> -s res://tools/playtest/runner.gd -- --mode=bot --bot=greedy --runs=200 --seed=1 --out=<abs>/bots.json
   ```
   Run `greedy` and `random`. A big gap between them means skill matters; no gap means choices are cosmetic. Compare win rate to `contract.progression.difficulty.target_win_rate`. Any non-zero `softlocks` is a blocker.
5. **Persona playtests.** Spawn `arcosian:player-simulator` once per persona in `references/personas.md` with: the build/entry point, the persona card, the scenario (first session, day-2 return, hit-a-wall), and the report schema. Simulators play through the headless runner, screenshots, and event logs, narrating intent and confusion in character. Use at least three personas that differ on skill, device tier and session habit.
6. **Visual QA.** Capture screens (`screenshot_mode.gd --screens=menu,game,results`), run structural checks, then `arcosian:critic` reviews. Cover smallest and largest target phone, notch/safe areas, dark mode if supported, and largest accessibility text size.
7. **Human round.** Hand off to `ship` for TestFlight/Play internal. Provide a one-page test plan (`templates/docs/` playtest plan), 5 to 8 testers who match `target_audience`, observation notes rather than opinions, and the metrics from `player-analytics`. Never ship a build to testers outside agreed channels without the user's go-ahead.
8. **Triage.** Merge findings, dedupe, assign severity, link repro. Blockers become `gs.py feature add` entries; log with `gs.py progress`.

## Playthrough script format

```json
{"schema_version":"1.0","seed":1,"steps":[
  {"action":{"type":"new_game"},"expect":{"board.empty_cells":{"op":">=","value":20}}},
  {"action":{"type":"swipe","dir":"left"},"expect":{"moves":1}},
  {"action":{"type":"swipe","dir":"up"},"expect":{"score":{"op":">","value":0}}}
]}
```

Rules: one action per step; `expect` keys are state paths in the sim-core snapshot; a bare value means equality, `{"op","value"}` supports comparison; assert after every action that changes state; seed everything; drive ticks, not wall-clock sleeps. Output follows `playtest-report.schema.json` (`steps[].t/action/expect/observed/ok`, `metrics`, `findings`, `verdict`). Validate with `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py validate .gamestudio/playtests/<file>.json`.

## Writing the playtest report

Save to `.gamestudio/playtests/<date>-<scope>.json` (schema `playtest-report`) plus a short Markdown summary beside it:

- **Verdict** (`pass|fail`) and the question it answers.
- **Metrics**: `win_rate`, `avg_session_sec`, `time_to_first_reward_sec`, `softlocks`, `crashes`, `errors`; compare each to the contract target.
- **Findings** ordered by severity: `blocker` (cannot progress, data loss, crash), `major` (many players hit it, hurts retention), `minor`, `polish`. Each has a title, evidence (screenshot or step), repro, and the suggested owner agent.
- **Not tested** list, so absence of findings is not read as safety.

## Outputs

`.gamestudio/playtests/*.json` and `.md`; for features, `.gamestudio/evidence/<ID>/playthrough.json`, `bots.json`, screenshots; new feature entries and progress notes.

## Quality gates

- Every run is reproducible: build id, seed, command line recorded in the report.
- At least one deterministic script covers the first-session path through first reward.
- Zero softlocks and zero crashes across bot runs before a milestone.
- Every blocker/major finding has a repro and an owner.
- Persona findings are labelled as simulated, never presented as human data.

## Failure modes and recovery

| Symptom | Recovery |
|---|---|
| Script passes but humans are lost | You tested wiring, not comprehension; add a persona round and a human round. |
| Bots win 100% or 0% | Bot is too strong or broken; check against a hand-played baseline before touching balance. |
| Simulator praises everything | Persona card too vague; add concrete habits and what they notice, ask for friction points first. |
| Results differ between runs | Unseeded RNG or time-dependent logic; fix determinism before trusting any metric. |
| Visual shots are blank | Headless without a renderer; use a display or `xvfb-run`. |

## Reference library

| File | Contains | When to read |
|---|---|---|
| `references/personas.md` | Ten player personas with motivation, skill, device tier, habits, what they notice, and how to simulate them | Before spawning `arcosian:player-simulator` |

## Related skills

`qa-testing` (strategy and test design), `player-psychology`, `player-analytics`, `mobile-ux`, `build-feature`, `balance`.
