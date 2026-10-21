---
name: balance
description: Tunes game economy and difficulty with simulators instead of guesses - authoring economy models, running economy_sim, difficulty curves, match-3 and puzzle solvers, gacha and progression calculators, then writing results back into the design contract. Use when the user says "balance the economy", "is this too grindy", "tune difficulty", "check drop rates", "simulate the economy", or "levels feel too hard".
argument-hint: "[economy | difficulty | gacha | progression | all]"
---

# Balance

Model it, simulate it, compare to targets, change one thing, repeat. Numbers in the contract are hypotheses until a simulator and then real telemetry agree. To predict one proposed change against the targets before applying it, use `what-if` (`gs.py whatif --set KEY=VALUE`).

## When to use

- A new economy, level set, loot table or progression curve needs first numbers.
- Playtest or analytics shows a wall, a hoard, inflation, or a churn spike at a level.
- Before soft launch, and after any content or offer change.
- For the full multi-agent loop, run `/arcosian:balance-pass`.

## Inputs

`$ARGUMENTS` selects the scope; default `all`. Read `contract.economy`, `contract.progression`, `contract.monetization`, `contract.analytics.kpi_targets`, and any model under `.gamestudio/economy/`. Load `economy-design` and `progression-difficulty` for theory; delegate modeling to `arcosian:systems-designer`.

## Tools

| Tool | Use |
|---|---|
| `${CLAUDE_PLUGIN_ROOT}/scripts/economy_sim.py` | Archetype-driven resource-flow Monte Carlo over days |
| `${CLAUDE_PLUGIN_ROOT}/scripts/difficulty_curve.py` | Generate target win-rate curves; analyze real attempt data |
| `${CLAUDE_PLUGIN_ROOT}/scripts/match3_sim.py` | Bot win rates and moves distribution for match-3 levels |
| `${CLAUDE_PLUGIN_ROOT}/scripts/puzzle_solver.py` | Exact solvability and minimum moves (sliding, sokoban, sort, lights_out) |
| `${CLAUDE_PLUGIN_ROOT}/scripts/gacha_calc.py` | Pull probabilities, pity, expected cost |
| `${CLAUDE_PLUGIN_ROOT}/scripts/progression_calc.py` | XP curves and time-to-level |
| `skills/progression-difficulty/scripts/balance_math.py` | Attempts distribution, funnel, DDA, damage, TTK, cost curves, softcaps |
| `skills/level-design/scripts/level_audit.py` | Audit an ordered level set, attempt odds, merge solver output into level specs |

All plugin scripts live at `${CLAUDE_PLUGIN_ROOT}/scripts/`; skill-local tools at `${CLAUDE_PLUGIN_ROOT}/skills/<skill>/scripts/`. Run any with `--selftest` if results look wrong.

## Procedure

1. **State targets first.** Write them in the model's `targets` and the contract: `days_to_complete_content`, `max_soft_currency_hoard_days`, `payer_conversion`, `progression.difficulty.target_win_rate`, per-level `difficulty_target` (`win_rate`, `attempts_p50`). Without targets there is nothing to tune toward.
2. **Author the economy model** at `.gamestudio/economy/model.json` (schema `economy-model`): `archetypes` (share, sessions per day, session minutes, skill, spend propensity, ad accept rate), `resources` (initial, cap), `nodes` (source, sink, converter, gate, pool with trigger, inputs, outputs, probability), `levels`, `offers`, `targets`. Archetype shares must sum to 1; every source needs a sink; every currency needs a cap or a drain. Validate: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py validate .gamestudio/economy/model.json`.
3. **Run the economy.**
   ```
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/economy_sim.py --model .gamestudio/economy/model.json --runs 200 --seed 1 --days 90 --json --out .gamestudio/economy/sim_001.json
   ```
   Read per-archetype balances over time, days to complete content, hoard days, and offer take-up against the targets. Use the same seed when comparing variants.
4. **Difficulty.**
   ```
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/difficulty_curve.py generate --levels 100 --pattern sawtooth --base 0.8 --floor 0.45 --period 10 --hard-every 10 --json
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/difficulty_curve.py analyze --data attempts.csv --json     # CSV: level,attempts,wins,churned
   ```
   Use `generate` to set per-level targets, `analyze` on bot or live data to find levels whose win rate or churn departs from the curve.
5. **Level solvers.**
   ```
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/puzzle_solver.py --level .gamestudio/levels/L012.level.json --algo astar --json
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/match3_sim.py --level .gamestudio/levels/L012.level.json --runs 500 --bot greedy --seed 1 --json
   python3 ${CLAUDE_PLUGIN_ROOT}/skills/level-design/scripts/level_audit.py audit .gamestudio/levels
   ```
   Merge solver output into each level's `solver` block with `level_audit.py merge`. Run `greedy`, `random` and `cascade` bots: human win rate usually sits between the weak and strong bots; use the gap, not one number.
6. **Gacha and progression.**
   ```
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gacha_calc.py --rate 0.006 --soft-pity-start 74 --soft-pity-step 0.06 --hard-pity 90 --guarantee --pulls 180 --json
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/progression_calc.py curve --formula poly --levels 60 --base 100 --exponent 1.6 --xp-per-min 40 --json
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/progression_calc.py time-to-level --table xp_table.json --xp-per-min 40 --json
   ```
   Example numbers above are placeholders to show syntax, not recommendations. Disclosure of odds and regional loot-box rules are `legal-ethics` and `monetization` questions, and the compliance owner signs them off.
7. **Tune one lever at a time.** Change a single parameter (sink cost, source rate, curve exponent, level move limit), rerun with the same seed, log the delta in a table. Stop when targets are met across archetypes, not just the average.
8. **Write back.** Update contract `mechanics[].parameters` (value, min, max), `progression.tracks[].curve.params`, `economy`, and `progression.difficulty`; keep the model file as the source of numbers and set `economy.model_ref` to it. Run `gs.py validate --all`, then `gs.py progress "balance: <what changed, why, sim id>"`.

## Tuning loop

| Observation | First lever | Check |
|---|---|---|
| Soft currency hoards past target days | Add or raise a sink, or cut the source | `economy_sim` hoard days per archetype |
| Content finishes too fast | Slow the XP or energy source, add gates | days to complete per archetype (fast archetype first) |
| Free archetype stalls hard | Raise rewarded-ad or daily sources | stall days; do not touch payer offers first |
| Win rate drift on one level | Moves/time limit or obstacle count | `match3_sim` win rate across bots |
| Spike in churn at level N | Lower N and neighbors, add a booster grant | `difficulty_curve analyze` churn column |
| Pity feels too stingy | Soft pity start earlier, or step larger | `gacha_calc` expected pulls and p99 |

## Acceptance targets (defaults; override from the contract)

- Every archetype reaches the intended content pace within a stated tolerance of `days_to_complete_content`.
- No currency accumulates beyond `max_soft_currency_hoard_days` of income for the median archetype.
- Per-level simulated win rate within a stated band of the curve target (choose and record the band; many teams use a few percentage points, but verify against your data).
- Zero unsolvable levels; `solver.solvable` true and `runs` recorded for all shipped levels.
- Free-to-complete path exists where the contract promises it.
- Sim variance is reported (runs, seed, spread), not just means.

## Outputs

`.gamestudio/economy/model.json`, `sim_*.json`; `.gamestudio/levels/*.level.json` solver blocks; updated contract parameters; a short balance note (before/after table) in `.gamestudio/reports/` and `progress.md`.

## Quality gates

- Targets exist, simulations are seeded and reproducible, and the final run meets all targets.
- Contract parameters match the model; no numbers hardcoded in game code that live in data.
- Ethics rules in `contract.monetization.ethics` still hold after tuning; `arcosian:critic` reviews any change that raises prices or lowers free rewards.

## Failure modes and recovery

| Symptom | Recovery |
|---|---|
| Sim is smooth but players churn | Archetypes are wrong; refit from telemetry (`player-analytics`) and add a distinct archetype. |
| Bots all win or all lose | Bot too strong or weak; hand-play baselines before tuning. |
| Changing one lever breaks another | Model coupling is hidden; add the missing node or link and rerun. |
| Results not reproducible | Missing `--seed`, or model changed between runs. |
| Script errors on model | `gs.py validate` first; then `--selftest`; fix inputs, not the script. |

## Related skills

`what-if`, `economy-design`, `progression-difficulty`, `level-design`, `monetization`, `player-analytics`, `legal-ethics`, `playtest`.
