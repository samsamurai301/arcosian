# Test Strategy and Scripted Playthroughs

This file defines how a mobile game team structures testing: the game test pyramid, how to rank risks and spend effort, and how to write deterministic scripted playthroughs that run through the Godot and Unity template runners and emit playtest-report JSON that the playthrough gate accepts as evidence. It also documents the report schema fields, the expectation syntax, a catalogue of playthroughs every game needs, and the habits that keep tests deterministic. The recurring idea: make the game replayable from a seed, then everything else (bots, regression, bug repro) becomes cheap.

## Contents
1. The game test pyramid
2. Risk-based testing
3. Determinism requirements
4. Deterministic scripted playthroughs
5. The template runners
6. Expectation syntax and assertions
7. Playthrough catalogue
8. The playtest-report schema
9. Writing a playthrough: procedure and worked example
10. Unit and integration tests for sim-core
11. Flakiness policy and CI integration
12. Checklists
13. Volatile facts (as of Oct 2026 — verify)

## 1. The game test pyramid

```
                 human playtests (fun, clarity)           few, slow, irreplaceable
              device farm + soak (hardware reality)
           visual QA: structural, golden, VLM triage
        bots and solvers (coverage, balance, softlocks)
     scripted playthroughs (flows, FTUE, purchase, save/load)
  unit + sim-core tests (rules, economy math, edge cases)     many, fast, deterministic
```

| Layer | Speed | Determinism | Catches | Typical count |
|---|---|---|---|---|
| Unit and sim-core | Milliseconds | Total | Rule bugs, math, edge cases | Hundreds to thousands |
| Scripted playthroughs | Seconds | Total (seeded) | Broken flows, state transitions, persistence | Tens |
| Bots and solvers | Minutes | Seeded, statistical | Softlocks, impossible levels, difficulty outliers | Per level and per release |
| Visual QA | Minutes | Medium | Layout and rendering regressions | Per key screen and aspect ratio |
| Device farm and soak | Minutes to hours | Low | Hardware, memory, thermal, driver bugs | Per release candidate |
| Human playtests | Hours | None | Fun, confusion, friction, feel | Per milestone |

Push every bug down the pyramid: when a human finds one, write the lowest-layer test that would have caught it.

Differences from app testing: no stable accessibility tree in most engines (engine UI is drawn, not native), time and randomness in the core, animation-driven state, large input spaces, and subjective quality. The countermeasures are a sim-core API for tests, injected clocks, seeded RNG and explicit "test hooks" (debug commands to jump to a state).

## 2. Risk-based testing

Score each feature or system: Likelihood of defect (new code, complex state, many integrations: 1-5) x Impact (money, data loss, progression block, first-session, store policy: 1-5). Test in descending score. Typical top risks in a mobile game:

| Risk area | Why it ranks high | Primary tests |
|---|---|---|
| Purchases and entitlements | Money and trust; refunds and store rules | Scripted purchase success, cancel, failure, restore; receipt validation mocks |
| Save and load, cloud sync | Data loss destroys retention | Save at every state, kill app mid-write, load older versions (migration), conflict cases |
| First-time user experience | Largest funnel drop | Playthrough of the first session; time to first reward; human test |
| Progression gates | A blocker stops all later play | Bot run through levels; unlock-chain tests |
| Economy exploits | Infinite resource loops break monetization | Sim-core invariants; economy simulation (see `economy-design`) |
| Ads and SDK integration | Crashes, ANRs, policy | Test-mode ad flows, failure and timeout handling |
| Device-sensitive code | Layout, audio, memory | Farm sweep, low-tier device |
| Time-based features | Daily resets, events, clock changes | Injected clock tests across rollover and DST |
| Localization and layout | Overflow, missing glyphs | Pseudo-localization, structural UI checks |

Output of this step: a one-page test plan (risk, layer, test name, owner, automation status) stored with the feature. `templates/docs/playtest-plan.md` is the template for the human-facing part.

## 3. Determinism requirements

A playthrough is only useful if it reproduces. Required of the game:
1. All gameplay randomness flows from one seedable RNG object owned by the sim-core; never the global random, never wall-clock-seeded in logic.
2. Time is injected: the sim advances by ticks or an injected delta, not by reading the system clock.
3. Sim-core is separable from rendering so it runs headless at full speed.
4. Input is represented as commands (a list of actions) that can be recorded and replayed.
5. State can be summarized to a comparable dictionary (the "expect" keys): board contents, resources, counters, status.
6. Asynchronous things (network, ads, store) have test doubles with scripted outcomes.

If any of these is missing, file it as an architecture defect (see `game-architecture`) before writing many tests; fighting nondeterminism later costs more.

## 4. Deterministic scripted playthroughs

A playthrough is a list of steps: an injected action, an expected state afterwards, and an observed record. It runs headless in the engine against the sim-core (or through the real input layer for UI flows), and emits a playtest-report with `mode: "deterministic_script"`.

Two levels of fidelity:
- Sim-level (fast, headless): actions applied to the sim-core directly; asserts game logic. Use for rules, progression, economy, save and load.
- Input-level (slower, needs rendering): simulated touches through the UI layer; asserts flow and UI state. Use for FTUE, menus, purchases, interruption handling. Godot's GdUnit4 scene runner can simulate mouse and keyboard input and wait for signals and has a headless CLI with JUnit XML; AltTester gives object-level access in Unity and Unreal scenes; Appium drives native UI and companion screens but does not see inside engine scene graphs (see section 13).

Rules for good playthrough scripts:
1. One script, one purpose (name it for the purpose: `ftue_first_session`, `purchase_cancel`).
2. Explicit seed in the file; same seed gives same result.
3. Assert after every state-changing step, with only the keys that matter, so unrelated changes do not break the test.
4. Prefer exact expectations for rules and `{op, value}` ranges for things allowed to vary.
5. End with a terminal assertion (win screen, resource totals, save file content).
6. Keep scripts small enough to read; compose from named setup steps rather than one 500-step file.

## 5. The template runners

**Godot (templates/godot-mobile).** Runner: `tools/playtest/runner.gd`. Run headless:

```
godot --headless --path <project> -s res://tools/playtest/runner.gd -- \
  --mode=script --script=res://tests/playthroughs/smoke.json --out=<abs>/playthrough.json [--seed=1]
godot --headless --path <project> -s res://tools/playtest/runner.gd -- \
  --mode=bot --bot=greedy|random --runs=200 --seed=1 --out=<abs>/bots.json
```

Exit codes: 0 pass, 1 fail (script) or softlocks (bots), 2 usage error. Script format (see `tests/playthroughs/smoke.json`):

```json
{
  "schema_version": "1.0",
  "seed": 1,
  "steps": [
    {"action": {"type": "new_game", "seed": 1}, "expect": {"status": "playing", "moves": 0}},
    {"action": {"type": "move", "dir": "left"}, "expect": {"moves": {"op": ">=", "value": 0}}}
  ]
}
```

Time metrics from headless runs are estimates (the template documents seconds-per-move as a constant), so say "estimated" in notes. A run that goes over the move cap without ending counts as a softlock.

**Unity (templates/unity-mobile).** The runner is `Game.EditorTools.PlaytestRunner.Run` (`Assets/_Game/Editor/PlaytestRunner.cs`). It follows the same contract (script file in, playtest-report JSON out, same exit codes) but is a batchmode `-executeMethod` entry point over `Game.Core`, not a Unity Test Framework run; the actual logic is `Playthrough.RunScript` and `Playthrough.RunBots` in `Assets/_Game/Core/Playthrough.cs`. Run it headless (`<p>` = project path, relative `-gsOut` paths resolve against the project root, `-quit` is required):

```
Unity -batchmode -nographics -projectPath <p> -executeMethod Game.EditorTools.PlaytestRunner.Run \
  -gsMode script -gsScript Assets/_Game/Tests/Playthroughs/smoke.json -gsOut <abs>/playthrough.json -quit
Unity -batchmode -nographics -projectPath <p> -executeMethod Game.EditorTools.PlaytestRunner.Run \
  -gsMode bot -gsBot greedy|random -gsRuns 200 -gsSeed 1 -gsOut <abs>/bots.json -quit
```

Flags: `-gsMode script|bot` (default script), `-gsOut` (required), `-gsScript` (script mode), `-gsBot`, `-gsRuns` (default 200), `-gsSeed` (optional; overrides the script's seed). Exit codes: 0 pass, 1 fail or softlocks, 2 usage error. The script format and expect paths are the same as the Godot template's (`smoke.json` ships in both), and `SimTests.cs` runs the same `Playthrough` code as EditMode tests, so a broken playthrough also fails the unit gate (`-runTests -testPlatform EditMode -testResults <abs>/unit.xml`, NUnit XML). The full command table, including scene build, AAB and Xcode builds and the screenshot gate, is in `${CLAUDE_PLUGIN_ROOT}/templates/unity-mobile/README.md`. Input-level flows (touch through the UI layer) are outside the template and need PlayMode tests.

**Adapting to your game.** Add action types to the runner's dispatcher for your game's commands and extend the state summary with the keys you want to assert. Keep action names identical in script files and in bot policies so the same vocabulary serves both.

## 6. Expectation syntax and assertions

| Form | Meaning |
|---|---|
| `{"key": value}` | Exact equality on the summarized state key |
| `{"key": {"op": ">=", "value": 10}}` | Comparison: `==`, `!=`, `>`, `>=`, `<`, `<=` |
| Dotted keys, e.g. `"board.max_tier"` | Nested state access |

Advice:
- Assert on summaries, not on object identity.
- Assert invariants at every step in debug runs: resources non-negative, no duplicate IDs, totals conserved by conversions, board has at least one legal move or is flagged as ended.
- When an assertion fails the runner records `ok: false` with observed values; keep `observed` in the report for the bug template.

## 7. Playthrough catalogue

| Playthrough | Asserts |
|---|---|
| `smoke` | App boots, new game, first valid action, no errors |
| `ftue_first_session` | Tutorial completes without a dead end; first reward at expected step; time_to_first_reward within target |
| `core_loop_win` and `core_loop_lose` | Win and lose paths both reach their end states with correct rewards |
| `save_load_roundtrip` | State after save and reload equals state before; migration from previous save version |
| `purchase_success`, `purchase_cancel`, `purchase_fail`, `restore_purchases` | Entitlements granted once, none on cancel or failure, restore idempotent |
| `economy_invariants` | Sinks and sources match the economy model; no negative balances; no free-resource loop |
| `progression_unlock_chain` | Each unlock reachable in order; no gating cycle |
| `interruption_resume` | Background mid-action, resume restores state; timers continue correctly |
| `daily_rollover` | Injected clock past midnight grants daily reward once; DST and timezone change do not duplicate or lose it |
| `offline_start` | Game playable offline; sync queued; no crash |
| `reduced_motion_and_accessibility` | Settings change layout or timings as promised |

## 8. The playtest-report schema

File: `.gamestudio/playtests/<name>.playtest.json`. Schema: `${CLAUDE_PLUGIN_ROOT}/scripts/schemas/playtest-report.schema.json`.

| Field | Meaning |
|---|---|
| `schema_version` | "1.0" |
| `feature_id`, `build` | What was tested; build id such as "0.3.0+a1b2c3d" |
| `mode` | `deterministic_script`, `bot`, `persona`, `human` |
| `persona` | Persona id or description for persona mode |
| `runs`, `seed` | Number of runs aggregated; seed of the first run |
| `steps[]` | `t`, `action`, `expect`, `observed`, `ok` |
| `metrics` | `win_rate`, `avg_session_sec`, `time_to_first_reward_sec`, `softlocks`, `crashes`, `errors` |
| `screenshots[]` | Project-relative paths |
| `findings[]` | `severity` (blocker, major, minor, polish), `title`, `detail`, `repro` |
| `verdict` | `pass` or `fail` |
| `notes` | Targets, environment, caveats |

Hard rule enforced by the schema: a `pass` verdict requires `metrics.crashes` to be 0 and no `blocker` findings.

Validate: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_json.py --schema ${CLAUDE_PLUGIN_ROOT}/scripts/schemas/playtest-report.schema.json --instance <file>`, or `--auto <dir>` to infer schemas from file names.

## 9. Writing a playthrough: procedure and worked example

Procedure:
1. State the purpose and the risk it covers.
2. List the actions in the game's command vocabulary.
3. For each action write the minimal expectation.
4. Run it; confirm it fails when you deliberately break the rule (mutation check). A test that cannot fail is not a test.
5. Commit with the seed and the runner command in a header comment or README line.

Worked example: merge-game purchase cancel (sim-level with a stubbed store).

```json
{
  "schema_version": "1.0",
  "seed": 7,
  "steps": [
    {"action": {"type": "new_game", "seed": 7}, "expect": {"gems": 0, "ads_removed": false}},
    {"action": {"type": "store_stub", "result": "cancelled"}, "expect": {}},
    {"action": {"type": "buy", "sku": "remove_ads"}, "expect": {"gems": 0, "ads_removed": false, "pending_purchase": false}},
    {"action": {"type": "store_stub", "result": "success"}, "expect": {}},
    {"action": {"type": "buy", "sku": "remove_ads"}, "expect": {"ads_removed": true, "pending_purchase": false}},
    {"action": {"type": "restore_purchases"}, "expect": {"ads_removed": true}}
  ]
}
```

Mutation check: change the cancel handler to grant the entitlement and confirm step 3 fails.

## 10. Unit and integration tests for sim-core

- Pure-function style: given state and action, return new state; assertable and replayable.
- Property tests where easy: after any random legal action sequence, invariants hold (resources conserved, no illegal states). Implement as a seeded bot with invariant checks (see `bots-and-visual-qa.md`).
- Edge cases to enumerate: zero and max values, integer overflow in currencies, simultaneous events, undo or retry, empty inventories, duplicate taps, saving mid-animation.
- Engine-side: Godot headless unit runner (`tools/ci/run_tests.gd`) writes JUnit XML; Unity Test Framework EditMode tests for pure assemblies (`Assets/_Game/Tests/EditMode/SimTests.cs` in the template) write NUnit XML. The same Core and EditMode tests also run on the plain .NET SDK through `templates/unity-mobile/tools/dotnet-harness/build_harness.py`, which needs no Unity licence.

## 11. Flakiness policy and CI integration

- A flaky test is a bug in the test or the game; quarantine within a day, fix within a week, never ignore reruns.
- Retry only to classify (rerun three times: fails always means real, sometimes means flaky), not to turn red green.
- Pipeline order: static checks, unit and sim tests, playthroughs, bots (small N on every PR, large N nightly), visual QA, device sweep per release candidate.
- Every CI job uploads the playtest-report JSON as an artifact; the gate reads those files.
- Keep playthroughs under a few minutes total on the PR path.

## 12. Checklists

Playthrough review:
- [ ] Purpose and risk stated; seed fixed; expectations minimal and meaningful.
- [ ] Mutation check done once.
- [ ] Report validates against the schema; verdict logic correct.
- [ ] Failure path covered, not only the happy path.

Gate evidence (playthrough gate):
- [ ] Release build id in `build`.
- [ ] `verdict: pass`, `crashes: 0`, no blocker findings.
- [ ] Covers the feature's core flow; steps list included.
- [ ] Screenshots attached when UI is involved.

## 13. Volatile facts (as of Oct 2026 — verify)

| Fact | Source |
|---|---|
| AltTester gives object-level access in Unity and Unreal scenes; Unity SDK v2.3.1 and Unreal SDK v1.2.1 released Apr 3, 2026 | https://alttester.com/blog/page/8 |
| Appium does not see inside game engine scene graphs; use AltTester for in-scene gameplay | https://docs.saucelabs.com/mobile-apps/automated-testing/appium/appium-for-games/ |
| GdUnit4 scene runner simulates mouse and keyboard and has headless CLI with JUnit XML and HTML reports | https://godotengine.org/asset-library/asset/1522 |
| GUT has a headless CLI; input simulation API unconfirmed | https://godotengine.org/asset-library/asset/1522 |
| Sauce Labs runs AltTester on real devices | https://docs.saucelabs.com/mobile-apps/automated-testing/alttester/unity/ |
