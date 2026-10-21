---
name: build-feature
description: Implements one feature from .gamestudio/features.json through the five gates (static, unit, playthrough, visual, perf) with evidence on disk, sim-core first. Use when the user says "build the next feature", "implement F012", "work the feature list", "make this feature pass", or when a feature needs gates run and recorded.
argument-hint: "[F### | next]"
---

# Build Feature

One feature, five gates, evidence on disk. A feature is done when `gs.py feature pass` says so, not when the code looks right.

## When to use

- Implementing a single feature from `.gamestudio/features.json`.
- Re-running gates after a fix, or finishing a feature that stalled at `in_progress`.
- For features spanning many files or several agents, run `/arcosian:build-feature` (the workflow) instead of doing it inline; this skill is the procedure that workflow follows.

## Inputs

`$ARGUMENTS` is a feature id (`F012`) or `next` (default). `next` picks the highest-priority `todo` feature whose `depends_on` all pass. If none qualifies, report what blocks the list and stop.

## Procedure

1. **Select and start.**
   ```
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py feature next --json      # only when $ARGUMENTS is next
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py feature start F012
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py evidence-dir F012        # prints the absolute evidence dir; call it EV
   ```
   Read `.gamestudio/config.json` (engine, paths), the feature entry, and the contract sections it touches (`mechanics`, `loops`, `ux`, `technical.perf_budgets`).
2. **Write the feature contract (before code).** Three short blocks in the progress note or a scratch file: *Behavior* (rules, parameters by contract key, never hardcoded numbers), *Acceptance criteria* (each testable and mapped to a gate: rule -> unit, flow -> playthrough, look -> visual, cost -> perf), *Out of scope*. If an acceptance string is vague ("feels good"), rewrite it as a measurable check and update features.json via the producer, not silently.
3. **Delegate to the engine specialist.** Engine from config: `arcosian:godot-engineer` or `arcosian:unity-engineer`; others route to `arcosian:gameplay-engineer`. Hand over the feature contract, the file boundaries, and the gate commands below. Architecture questions go to `arcosian:lead-engineer`. Load `game-architecture` and `gameplay-programming` if you implement inline.
4. **Sim-core first, with unit tests.** Implement rules in the engine-free core (no nodes, no `UnityEngine`), driven by a seeded RNG and explicit inputs, returning state. Write unit tests that cover each rule and edge case in the acceptance list before wiring presentation. Presentation only reads state and sends intents.
5. **Static gate.** Run, save output to EV, then record.
   ```
   godot --headless --path <project> -s res://tools/ci/check_all.gd -- --out=$EV/static.log
   ```
   Unity: the compile step is the `-runTests` build or `SceneBuilder.BuildAll` log; save the log to `$EV/static.log`. Also `gs.py validate --all` if you touched `.gamestudio/` JSON.
   ```
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py feature gate F012 static pass --evidence .gamestudio/evidence/F012/static.log
   ```
6. **Unit gate.**
   ```
   godot --headless --path <project> -s res://tools/ci/run_tests.gd -- --out=$EV/unit.xml
   Unity -batchmode -nographics -projectPath <p> -runTests -testPlatform EditMode -testResults $EV/unit.xml -logFile $EV/unity.log
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py feature gate F012 unit pass --evidence .gamestudio/evidence/F012/unit.xml
   ```
7. **Playthrough gate.** Add or extend a script in `tests/playthroughs/` (format in `skills/playtest/SKILL.md`: steps of `action` + `expect`), then:
   ```
   godot --headless --path <project> -s res://tools/playtest/runner.gd -- --mode=script --script=res://tests/playthroughs/smoke.json --out=$EV/playthrough.json --seed=1
   Unity -batchmode -nographics -projectPath <p> -executeMethod Game.EditorTools.PlaytestRunner.Run -gsMode script -gsScript Assets/_Game/Tests/Playthroughs/smoke.json -gsOut $EV/playthrough.json -quit
   ```
   For balance-sensitive features use bots (`--mode=bot --bot=greedy --runs=200`) and compare to contract targets. Record with `gate F012 playthrough pass --evidence ...playthrough.json`.
8. **Visual gate (skip as `n/a` with a note only for features with no visible change).**
   ```
   godot --path <project> -s res://tools/capture/screenshot_mode.gd -- --out=$EV --screens=menu,game,results
   ```
   Run structural UI checks first (safe areas, 44pt/48dp tap targets, text overflow, contrast), then ask `arcosian:critic` to review the screenshots against the rubric in `skills/mobile-ux`, `skills/art-direction` and the contract's art direction. The critic's verdict goes to `$EV/visual_review.md`; the gate evidence lists the shots and the review.
9. **Perf smoke.** Run the reference scenario on the lowest available device tier, save a perf-report, then check it:
   ```
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/perf_budget.py --report $EV/perf.json --contract .gamestudio/contract.json --json
   ```
   Exit 0 -> `gate F012 perf pass --evidence .../perf.json`. Exit 1 -> fix or run `optimize`. Use `n/a` plus a note only for features that cannot affect runtime (pure data).
10. **Pass.** `gs.py feature pass F012`. It refuses unless every gate is `pass` or `n/a` (with a note) and every evidence path exists. Never edit features.json by hand to get around it.
11. **Progress note.** `gs.py progress "F012 done: <what changed>, <decisions>, <follow-ups>"`. Add follow-up features via `gs.py feature add`.

## Regenerate vs patch

| Situation | Action |
|---|---|
| Failure localized to one function, test points at it | Patch. |
| Second failed patch on the same symptom | Stop patching; re-read the contract and the failing test; the premise is probably wrong. |
| More than about a third of the feature's files change to fix one gate | Regenerate that module from the contract, keep the tests. |
| Tests encode behavior the contract does not require | Fix the test, note why in the gate note. |
| Gate fails after an unrelated feature merged | Bisect by reverting the last change; do not stack fixes. |

Always regenerate from the contract and the existing tests, never from memory of the previous attempt.

## Escalation when stuck

Three failed attempts at the same gate, or any gate that needs a design change: `gs.py feature block F012 --reason "<specific>"`, log it with `gs.py progress`, and escalate: design ambiguity -> `arcosian:game-designer`; architecture -> `arcosian:lead-engineer`; fun or quality dispute -> `arcosian:critic`; scope -> `arcosian:producer`. Human checkpoint: tell the user which acceptance criterion cannot be met and the options (cut, change, defer).

## Outputs

- Code and tests in the game project; `.gamestudio/evidence/F012/{static.log, unit.xml, playthrough.json, shot_*.png, visual_review.md, perf.json}`.
- Updated `features.json` (gates, evidence, `passes`), appended `progress.md`.

## Quality gates

- Every gate `pass` or `n/a` with a gate note; every evidence file exists and was produced by the commands above in this session.
- Unit tests cover each acceptance criterion that is a rule; no tuning numbers hardcoded outside contract parameters or data files.
- No unrelated files changed; no secrets written.

## Failure modes and recovery

| Symptom | Likely cause | Recovery |
|---|---|---|
| `feature pass` refuses | Missing evidence file or `n/a` without note | Run `gs.py feature list --json`, rerun the gate with `--evidence`/`--note`. |
| Headless run exits 0 but log shows errors | Runner swallowed script errors | Grep the log for `ERROR`/`SCRIPT ERROR`; treat as fail and record `fail`. |
| Screenshot gate cannot render | No renderer in headless env | Use `xvfb-run` on Linux CI or run locally; never fake the evidence. |
| Flaky playthrough | Unseeded RNG or timing-based waits | Seed it, advance by ticks not seconds. |
| Perf passes on desktop only | Wrong device tier | Re-run on a low-tier device; see `optimize`. |

## Related skills

`playtest`, `optimize`, `balance`, `qa-testing`, `game-architecture`, `gameplay-programming`, `engine-godot`, `engine-unity`.
