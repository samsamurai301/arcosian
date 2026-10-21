---
name: what-if
description: Predicts what a proposed change will do before anyone ships it - runs the current and the changed version through the project's bots or simulators on the same seeds, then reports the difference with ranges and a verdict against the design contract's targets. Also maps what the change touches. Use when the user asks "what if we change X", "will this make it too easy", "predict the effect", or before a tuning, economy or level change.
argument-hint: "[KEY=VALUE ...]"
---

# What-if

Predict, then decide, then build. A change to tuning, the economy or a level gets a prediction from the same bots and simulators the gates use, compared on identical seeds, before it is applied. The prediction is evidence for a decision, not a substitute for a playtest.

## When to use

- Someone proposes a tuning change ("make the win tile 512", "spawn more enemies", "cut the starter pack price").
- A balance pass needs to compare options before picking one (run one what-if per option).
- A playtest or telemetry finding suggests a fix and you want to know its side effects first.
- Before `build-feature` touches a tuning key or the economy model of a feature that already passed its gates.

Not for: changes with no simulator behind them (art, UI copy, audio). Use `playtest` and `design-review` for those.

## Inputs

- `$ARGUMENTS`: one or more `KEY=VALUE` changes. VALUE is JSON (`512`, `0.2`, `true`) or relative: `*1.25` multiplies, `+=10` adds.
- The project's `.gamestudio/contract.json` targets: `progression.difficulty.target_win_rate`, `analytics.kpi_targets.session_len_sec`; for the economy, the model's own `targets`.
- One simulator (picked automatically, or with `--sim`):

| Simulator | Needs | KEY is |
|---|---|---|
| `godot` | A Godot project built from the template (`tools/playtest/runner.gd`), a Godot binary on `GODOT_BIN` or PATH | A key in the tuning JSON (for example `win_tile`) |
| `economy` | An economy model (`.gamestudio/economy/*.json` or `--model`) | A dotted path into the model; list items by id: `offers.starter_pack.price_usd` |
| `match3` | A match-3 level spec (`--level`) | A dotted path into the level: `moves_or_time_limit` |

## Procedure

1. **Map the change first.** Know what it touches before predicting what it does:
   ```
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py impact <KEY or file>
   ```
   For a tuning key this lists the scripts that read it, the scenes and tests behind them, and the gates a real change would re-run.
2. **Check the targets exist.** Without targets the verdict is `unknown`. If `target_win_rate` or `kpi_targets` are 0 or missing, ask the game designer (`arcosian:game-designer`) for the intended value, or say the verdict will only describe the change.
3. **Run the prediction.** Defaults are 5 seeds x 100 runs, paired:
   ```
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py whatif --set win_tile=512
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py whatif --set days=*0.8 --model .gamestudio/economy/model.json
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py whatif --set moves_or_time_limit=+=3 --level .gamestudio/levels/L012.json
   ```
   Several `--set` flags test one combined change. Compare options with one run each and a `--label`.
4. **Read the result.** Each metric shows current and proposed means with 90% intervals, the paired change, the target band and an assessment: `closer`, `further`, `no clear change`, `changes` (no target), `breaks` (softlocks, crashes, errors or a failed economy check went up).
5. **Decide with the verdict.**

   | Verdict | Meaning | Next step |
   |---|---|---|
   | `improves` | At least one targeted metric moves toward its band, none moves away | Apply the change through `build-feature`; re-run the gates `impact` named |
   | `mixed` | Some targeted metrics improve, others get worse | Present the trade-off to the human; try a smaller step or a second lever |
   | `worsens` | Targeted metrics move away from their bands | Do not apply; record why in progress |
   | `no clear effect` | Differences are inside the noise | Increase `--runs` or `--seeds` once; if still flat, the lever is weak |
   | `reject` | A hard rule broke (softlock, crash, error, economy check) | Do not apply; file the repro as a bug feature |
   | `unknown` | No targets to judge against | Set targets in the contract, then rerun |

6. **Record.** Results are saved to `.gamestudio/whatif/` and appear on the dashboard (`gs.py dashboard`). Log the decision:
   `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py progress "what-if win_tile 1024->512: mixed (session into band, win rate above band); not applied"`.

## How the numbers are made

- Each seed runs the current and the proposed version with identical random streams, so differences come from the change, not luck (common random numbers).
- Win rates use Wilson intervals over all runs and Newcombe's interval for the change; other metrics use a Student t interval across seeds. With one seed there is no interval.
- A metric is `clear` when its change interval excludes zero. The target band is the contract value plus or minus `--tolerance` (0.05) for win rate, plus or minus 20% for session length.
- Bots are not players. Greedy bots overrate skill; random bots underrate it. Use the bot that matches the persona, and confirm any shipped change with a real playtest (`playtest`).

## Worked example

Template game, contract target win rate 0.85 and session 300 s. Proposal: lower `win_tile` from 1024 to 512.

```
gs.py whatif --set win_tile=512 --runs 40 --seeds 3
avg_session_sec   561 [531, 590] -> 282 [272, 291]   -279   target 240-360   closer
win_rate          0.85 [0.79, 0.90] -> 1 [0.98, 1]   +0.15  target 0.8-0.9   further
Verdict: MIXED
```

Reading: sessions land in the band, but every bot now wins, so the game stops being a challenge. A second run with `spawn_four_chance=0.3` shortened sessions to 468 s without changing the win rate (`improves`). The designer picked the second lever and kept the win tile.

## Outputs

- `.gamestudio/whatif/<time>-<label>.json`: changes, seeds, per-metric statistics, verdict and reasons.
- A progress entry with the decision.
- When applied: the tuning or model change, made through `build-feature` with the gates `impact` lists.

## Quality gates

- At least 3 seeds and 100 runs per seed before a decision that ships; 5 x 100 is the default.
- Targets present, or the report says the verdict is `unknown`.
- `reject` is never overridden without a human decision recorded in progress.
- Applied changes go through the five gates like any other change.

## Failure modes

| Symptom | Fix |
|---|---|
| "cannot pick a simulator" | Pass `--sim godot`, `--model` or `--level`; non-Godot engines need a simulator script or an economy model |
| "no Godot binary" | Set `GODOT_BIN` to the editor binary (on Windows the `_console.exe`) |
| "KEY is not a key in tuning.json" | Use a key from the tuning file; add new keys to the tuning loader first |
| Every result is `no clear change` | The lever is weak or the bots ignore it; raise runs, or choose a bot that uses the mechanic |
| Results differ between machines | Engine or simulator versions differ; pin them and keep `--seed` the same |

## Related skills

`balance`, `progression-difficulty`, `economy-design`, `playtest`, `build-feature`, `level-design`.
