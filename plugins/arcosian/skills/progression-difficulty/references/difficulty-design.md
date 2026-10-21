# Difficulty Design

Difficulty is the one parameter a player meets on every attempt. It decides whether they feel clever, bored or cheated, and in free-to-play it also decides where churn and spending happen. This file treats difficulty as something you measure, target and verify. It covers what difficulty is made of, the metrics that quantify it (first-attempt win rate, attempts distributions, the heterogeneity trap), the flow channel as a working model, curve shapes (linear, sawtooth, stepped, hard-every-K), win-rate targets by stage (stated as design targets, not facts), hard and super-hard cadence, failure costs, boosters and continues, levers by genre, bot measurement and calibration, `difficulty_curve.py` usage, telemetry diagnostics, difficulty modes and assists, and a fully worked 60-level plan. Adaptive systems are in `references/dynamic-difficulty.md`. Level construction is in `level-design`.

## Contents

1. What difficulty is made of
2. Measuring difficulty
3. The flow channel as a working model
4. Curve shapes
5. Target win rates by stage (design targets)
6. Hard and super-hard level cadence
7. Failure costs
8. Boosters, continues and the fail screen
9. Difficulty levers by genre
10. Measuring with bots and calibrating to humans
11. `difficulty_curve.py` usage
12. Telemetry diagnostics
13. Difficulty modes, assists and accessibility
14. Worked example: a 60-level saga plan
15. Difficulty checklist
16. Volatile facts (as of Oct 2026 — verify before relying)

---

## 1. What difficulty is made of

| Dimension | What it taxes | Typical levers | Mobile caution |
|---|---|---|---|
| Execution | Timing, precision, dexterity | Speed, windows, hitbox size, enemy density | Touch latency and fat fingers add error; widen windows |
| Cognitive | Planning, look-ahead, pattern recognition | Branching factor, hidden information, number of interacting rules | Interruptions break look-ahead; avoid long mental stacks |
| Knowledge | Knowing rules, enemies, combos | New mechanics, unseen enemy types | Teach before you test (teach → test → twist → reward) |
| Resource | Managing scarce moves, HP, time, currency | Move limits, starting resources, drop rates | Hidden resource walls feel like monetization |
| Time pressure | Speed of decisions | Timers, chasing threats | Short sessions in noisy places; offer untimed modes |
| Variance | Luck in outcomes | Board refills, crits, spawns | High variance hides skill; see `design-theory` on input vs output randomness |

**Perceived vs measured difficulty.** Players judge difficulty by how failure feels: whether it was explainable, how close they came, how costly it was and how fast they could retry. A level with a 40% win rate and instant, explainable failure can feel fairer than a 70% level that fails on a hidden rule. Always measure both: telemetry for the measured side, and playtest questions ("Why did you fail?", "Was that fair?") for the perceived side.

## 2. Measuring difficulty

### 2.1 Core metrics

| Metric | Definition | Use |
|---|---|---|
| First-attempt win rate (FAWR) | Wins on first attempts ÷ first attempts | The primary design target (`level-spec.difficulty_target.win_rate`) |
| Attempts per win (APW) | All attempts ÷ wins | Real effort; includes repeat failures |
| Attempts p50 / p90 | Median and 90th percentile of attempts-to-clear | `difficulty_target.attempts_p50`; p90 is the pain tail |
| Level churn | Players whose furthest level is L and who then go inactive (e.g. 7+ days) ÷ players who reached L | The outcome you actually care about |
| Booster / continue rate | Attempts using a booster ÷ attempts | Shows dependency and monetization pressure |
| Moves (or time) left on win | Distribution of slack at victory | Wide slack = easy; a cluster at 0–1 = tight |
| Progress on loss | Share of goal complete when failing | High progress on loss = near-misses (frustrating if frequent) |
| Time to retry | Seconds from fail screen to next input | Friction; keep it to a few seconds on mobile |

### 2.2 The geometric attempts model

If a player's per-attempt win chance is a constant p, attempts-to-clear are geometric: mean 1/p, P(clear within n) = 1 − (1 − p)^n.

| p | Mean attempts | p50 | p90 | p99 | P(≤3) | P(≤5) | P(≤10) |
|---|---|---|---|---|---|---|---|
| 0.95 | 1.05 | 1 | 1 | 2 | 1.000 | 1.000 | 1.000 |
| 0.90 | 1.11 | 1 | 1 | 2 | 0.999 | 1.000 | 1.000 |
| 0.80 | 1.25 | 1 | 2 | 3 | 0.992 | 1.000 | 1.000 |
| 0.70 | 1.43 | 1 | 2 | 4 | 0.973 | 0.998 | 1.000 |
| 0.60 | 1.67 | 1 | 3 | 6 | 0.936 | 0.990 | 1.000 |
| 0.50 | 2.00 | 1 | 4 | 7 | 0.875 | 0.969 | 0.999 |
| 0.40 | 2.50 | 2 | 5 | 10 | 0.784 | 0.922 | 0.994 |
| 0.30 | 3.33 | 2 | 7 | 13 | 0.657 | 0.832 | 0.972 |
| 0.25 | 4.00 | 3 | 9 | 17 | 0.578 | 0.763 | 0.944 |
| 0.20 | 5.00 | 4 | 11 | 21 | 0.488 | 0.672 | 0.893 |
| 0.15 | 6.67 | 5 | 15 | 29 | 0.386 | 0.556 | 0.803 |
| 0.10 | 10.0 | 7 | 22 | 44 | 0.271 | 0.410 | 0.651 |

Compute any row with `python3 ${CLAUDE_PLUGIN_ROOT}/skills/progression-difficulty/scripts/balance_math.py attempts --win-rate 0.35 --cost-per-loss 1`.

**Caveats.** Real players learn, so p rises across attempts. Boosters and assists raise it further. That makes the table a pessimistic bound for an individual. Populations, though, are heterogeneous, and that makes things worse, not better (2.3).

### 2.3 The heterogeneity trap (Jensen gap)

Average win rate hides the pain. If half your players have p = 0.8 and half have p = 0.2, the population FAWR is 0.5, which suggests 2 attempts. The true mean is 0.5 × 1.25 + 0.5 × 5 = **3.125 attempts**, and 5.4% of all players are still stuck after 10 attempts (`balance_math.py mix --rates "0.8:0.5,0.2:0.5"`). Mean attempts is the average of 1/p, which is always at least 1/(average p).

A more realistic model puts skill on a logistic scale: `p = σ(logit(p_median) + s)` with s ~ Normal(0, 1) in logit units. Under that model:

| Median-player p | Population FAWR | True mean attempts | Naive 1/p | p25 player p (p90 attempts) | p10 player p (p90 attempts) |
|---|---|---|---|---|---|
| 0.90 | 0.866 | 1.18 | 1.11 | 0.821 (2) | 0.714 (2) |
| 0.70 | 0.668 | 1.71 | 1.43 | 0.543 (3) | 0.393 (5) |
| 0.50 | 0.499 | 2.65 | 2.00 | 0.338 (6) | 0.217 (10) |
| 0.45 | 0.458 | 3.02 | 2.22 | 0.294 (7) | 0.185 (12) |
| 0.35 | 0.374 | 4.07 | 2.86 | 0.215 (10) | 0.130 (17) |

**Design rule.** Set targets on the median player, but **gate hard levels on the weak tail**. A useful constraint: "the p10-skill player's p90 attempts on any hard level ≤ ~12 with zero boosters". The 0.35 super-hard above fails that test (17) unless the free-booster economy or a bounded assist covers it (`references/dynamic-difficulty.md`).

### 2.4 Sample size for measured win rates

Standard error of a measured rate ≈ √(p(1−p)/n). At p = 0.5: n = 100 → ±5 points; n = 400 → ±2.5; n = 1,000 → ±1.6. Do not retune a level on fewer than a few hundred first attempts unless the gap to target is larger than about 3 standard errors. Bot runs follow the same maths: 500 runs give about ±2 points.

## 3. The flow channel as a working model

Csikszentmihalyi's flow model (*Flow*, 1990) places enjoyable focus between anxiety (challenge far above skill) and boredom (skill far above challenge). Jenova Chen's MFA thesis *Flow in Games* (2006) made two points that matter for design. Different players have different flow zones. And games should let players steer their own difficulty through choices embedded in play, rather than relying only on silent adjustment.

**Working model.** For any attempt:

```
P(win) = σ(skill + power − difficulty)          # all in logit units
```

- **skill** grows with practice (fast early, slower later; each new mechanic briefly lowers effective skill until learned).
- **power** grows with progression (upgrades, boosters, heroes). See `references/power-and-balance.md`.
- **difficulty** is what the designer controls per level.

**Three-slope rule.** Over any window of about 10 levels, the average rise in difficulty should roughly equal the average rise in skill + power. A steeper difficulty slope pushes players toward anxiety (churn and, in F2P, spend pressure). A shallower slope pushes them toward boredom (churn and content burn). Within the window, oscillate around the trend (sawtooth) so tension rises and releases.

**Implications.**

- Teach levels lower difficulty because effective skill on the new element is near zero.
- After a power spike (a new hero, a big upgrade), you can raise difficulty without lowering P(win). Do this deliberately, and let the player enjoy at least one level of feeling stronger first.
- Content met by late-game players is played by survivors who are more skilled than average installs. The same FAWR at level 500 means much harder content than at level 50.

## 4. Curve shapes

| Shape | Description | Best for | Risk |
|---|---|---|---|
| Linear ramp | Difficulty rises steadily | Short games, tutorials, single-session arcs | Monotony; no release |
| Sawtooth | Ramp over P levels, peak, drop back to relief, repeat with a rising baseline | Saga puzzle, level-based casual, campaign RPG | Peaks too sharp or too frequent |
| Stepped | Plateaus with a jump when a new mechanic or world arrives | Mechanic introductions, world boundaries | Jumps land as walls if the step is too big |
| Hard-every-K | Baseline curve plus a designated hard level every K levels | Monetization-sensitive sagas (use ethically) | Spikes coincide with offers |
| Interest curve | Hand-shaped peaks and valleys with a climax near the end | Chapters, events, boss rushes, story arcs | Hard to automate; needs authoring |
| Endless escalation | Difficulty rises continuously until failure | Runners, survival, endless modes | Must be fast to restart; score is the reward |

**Sawtooth formula** (for target win rates rather than raw difficulty):

```
k = (n − n_start) mod P                    # position in period, 0..P−1
w(n) = hi_c − (hi_c − lo_c) · k/(P − 2)    for k ≤ P − 2   # ramp from relief to tension
w(n) = hard_c                               for k = P − 1   # peak (hard level)
hi_c, lo_c, hard_c drift down slowly with chapter c
```

`difficulty_curve.py generate --pattern sawtooth` implements a simplified, drift-free version of this shape (section 11): every tooth is identical, ramps from `--base` towards the midpoint of base and floor, and the last level of the tooth is set to `--floor`. Chapter drift, an easier onboarding chapter and different hard and super-hard values are hand edits.

**Three scales of shape.** Apply the shape at the scale of the **chapter** (10–20 levels: sawtooth with one hard peak), the **session** (warm-up win first; peak late; end on a win or a cliffhanger) and the **level** (open easy, build pressure, peak near the end; do not front-load the hardest moment).

## 5. Target win rates by stage (design targets)

The values below are **studio starting targets** for level-based mobile games. They are not industry benchmarks or measured facts. They encode the conventions in this skill: near-unlosable onboarding, gentle habit building, then a sawtooth. Recalibrate them with your own soft-launch telemetry (`difficulty_curve.py analyze`, section 11). All values are FAWR for the **median active player at that level**.

**Saga-style puzzle (match-3, sort, block, merge-level):**

| Stage | Example levels | Normal level FAWR | Hard level FAWR | Super-hard FAWR | Notes |
|---|---|---|---|---|---|
| Onboarding | 1–10 | 0.95–1.00 | — | — | Failure only as a teaching beat |
| Habit building | 11–30 | 0.80–0.92 | 0.50–0.65 (first hard around 15–25) | — | One hard per 10; generous relief |
| Early mid | 31–100 | 0.70–0.85 | 0.40–0.55 | 0.30–0.40 at chapter ends | Boosters introduced and gifted |
| Mid | 100–500 | 0.60–0.80 | 0.35–0.50 | 0.20–0.35 | Survivor population; recalibrate often |
| Late | 500+ | 0.55–0.75 | 0.30–0.45 | 0.15–0.30 | Content runway; watch level churn |

**Other genres (starting hypotheses):**

| Genre / mode | Target | Note |
|---|---|---|
| Hyper-casual levels | 0.85–0.98 most levels | Failure is short and cheap; progress drives retention |
| Hybrid-casual stages with meta power | Base 0.75–0.90, with meta adding ≤ +10–15 points | Keeps skill relevant (consistent with `genre-playbooks`) |
| Campaign RPG stages | ~0.90+ at the recommended power; walls at 0.3–0.5 under-powered | Walls ask the player to upgrade, replay or change team |
| Roguelite full run | Low early clear rates (a first win after several runs) | The reward is meta progress and learning, not run wins |
| Boss fights (action) | Attempts p50 of about 2–5 for the target audience | Telegraphs and checkpoints matter more than HP |
| PvP ranked | About 0.50 by construction | Matchmaking targets parity; see `references/dynamic-difficulty.md` §7 |
| Endless / score modes | No win rate; use distance or score percentiles | Tune the time-to-first-death distribution instead |

## 6. Hard and super-hard level cadence

**Rules (studio defaults; adjust per game).**

1. **No hard levels during onboarding.** The first hard level comes after the player has formed a habit: after day 1 for most players, typically somewhere in levels 15–30 of a saga.
2. **Cadence.** One hard level every 5–10 levels; one super-hard level every 20–40 levels, usually at a chapter end. Never two hard levels in a row.
3. **Relief after every peak.** The level after a hard or super-hard is a relief level (FAWR ≥ 0.9), preferably a "reward" beat in `level-spec.teach`.
4. **Hard levels test; they do not teach.** Never introduce a new mechanic on a hard level. Hard levels combine known elements (the test and twist beats).
5. **Label them.** Show "Hard" or "Super Hard" before the attempt, with a visual treatment and a bigger reward. Labelling turns an unexplained wall into an accepted challenge. Several leading match-3 games label hard levels this way.
6. **Reward in proportion.** Hard levels pay more (for example 1.5–3× soft currency, or a guaranteed booster), so the extra attempts feel invested.
7. **Solvable without spending.** A bot or solver must clear every hard level with zero paid boosters at a rate consistent with its target (`level-spec.solver`). Super-hard levels must be clearable with the free booster income a non-payer accumulates (coordinate with `economy-design`).
8. **Tail constraint.** p10-skill player, p90 attempts ≤ about 12 with zero boosters on hard levels (section 2.3). If you exceed it, add free help (a gifted booster on attempt N, or a bounded assist), not a paid offer.
9. **Decouple from offers.** Do not schedule time-limited offers to appear only on hard levels. Fail-screen offers are standard, but their frequency and placement must not track a player's frustration state (`monetization`, `legal-ethics`).

**Cadence template (period 10):**

| Position in chapter | 1 | 2–4 | 5 | 6–8 | 9 | 10 |
|---|---|---|---|---|---|---|
| Beat | Relief / reward | Teach + test new element | Twist (medium) | Ramp | Pre-peak (medium-hard) | Hard (or super-hard at chapter end) |
| FAWR target | ≥ 0.92 | 0.80–0.90 | 0.70–0.80 | 0.65–0.80 | 0.60–0.70 | 0.35–0.55 |

## 7. Failure costs

Every failure charges the player something. The total felt cost per clear is roughly `expected_losses × cost_per_loss`, where `expected_losses = 1/p − 1`.

| Cost type | Examples | Effect | Guidance |
|---|---|---|---|
| Time | Replay length, load screens, unskippable intros | The largest hidden cost on mobile | Retry within a few seconds. Skip intros after the first view. Short levels |
| Resource | Lives, energy, currency spent on entry | Ends sessions; creates the stop-or-pay moment | Charge on loss, not on win. Show regeneration time. Gift lives socially |
| Progress | Lost streak, checkpoint loss, permadeath | Raises stakes and tension | Use for opt-in stakes (streak ladders, hard modes). Show what is at risk before the attempt |
| Emotional | Near-misses, unexplained deaths, sarcastic copy | Frustration or "one more try" | Explain every failure ("2 jellies left"). Never mock the player |
| Social | Letting a team down, visible rank loss | Strong motivation; strong churn | Soft-reset ranks, with demotion protection near boundaries |

**Failure-cost ladder by stage (design defaults):**

| Stage | Cost on failure |
|---|---|
| Onboarding | None. Instant retry, no lives |
| Habit building | A life is charged, but lives are plentiful and refills are gifted |
| Mid game | Lives plus streak loss; boosters at risk only if pre-equipped |
| Opt-in challenge | Progress at stake (event ladders, hard modes), clearly disclosed |

**Worked cost.** A hard level at p = 0.35 for the median player: mean 2.86 attempts, 1.86 expected losses, p90 = 6 attempts (5 losses). With a 5-life bar, about 12% of median players (0.65⁵) lose five times in a row and empty their lives on that one level. For a p25 player (p ≈ 0.215), p90 is 10 attempts, which means two full life bars. Decide in advance whether that is the intended session end. If not, lower the cost (a free life refill on the first hard-level loss streak, or a gifted booster).

**Fail forward.** Patterns that keep failure productive: keep partial rewards (coins collected), show "best attempt" progress, offer an optional hint after N losses, or unlock an alternative path (skip after N losses, as some premium games do). Each of these lowers the felt cost without changing the level.

## 8. Boosters, continues and the fail screen

**Booster types.**

| Type | When | Effect on win rate | Design guidance |
|---|---|---|---|
| Pre-level booster | Before the attempt | Shifts FAWR up by a fixed amount | Measure the uplift with bots on every level; show the player its value |
| In-level booster | During the attempt (hammer, shuffle) | Rescues specific stuck states | Useful for knowledge-poor players; avoid making them mandatory |
| Continue (extra moves or time) | On the fail screen | Converts near-misses into wins | The highest-value offer in many puzzle games; it needs strict ethics |
| Streak boosters | Earned by consecutive wins | Momentum reward | Reward mastery; disclose the loss condition |

**Quantify booster uplift.** For each level, run bots with and without each booster, then record `uplift = FAWR_with − FAWR_without`. Design targets (starting hypotheses): normal levels clear at target **without** boosters. On hard levels, a pre-level booster adds about 15–30 points. A continue converts a material share of near-misses, but never all losses.

**Booster economy.** A non-payer should receive enough boosters from play (rewards, dailies, events, streaks) to use one on most super-hard levels. Model booster sources and sinks as an economy resource in `.gamestudio/economy/` and simulate with `economy_sim.py`.

**Fail-screen ethics (red lines).**

- **Never manufacture near-misses.** Do not alter refills or spawns so a losing attempt ends "one away" in order to sell a continue. Natural near-misses are fine. Engineered ones are a dark pattern, and potentially a consumer-protection issue (`legal-ethics`).
- **The continue must be honest.** If you sell +5 moves, the level state must allow a win within them with a reasonable probability. Do not sell continues on mathematically lost states.
- **No escalating pressure.** Avoid escalating countdowns, or second and third offers stacked in one fail flow. One clear offer and one clear exit.
- **Same rules for everyone.** Difficulty never depends on payer status or wallet balance (`references/dynamic-difficulty.md` §6).

## 9. Difficulty levers by genre

| Genre | Primary levers (strongest first) | Secondary levers | Verify with |
|---|---|---|---|
| Match-3 / swap | Colours, move limit, goal count, blocker layers | Spawn weights, board shape, cascades | `match3_sim.py` |
| Sort / logic / sliding | Solution depth (min moves vs limit), branching, distractors | Buffer slots, hidden info | `puzzle_solver.py` |
| Block / tetromino | Piece distribution, board clutter, scoring thresholds | Preview count, hold slot | Custom bots |
| Merge | Spawn tiers, board space, order complexity | Generator cooldowns | Simulation |
| Runner / arcade | Speed, obstacle density, reaction window | Lane count, pattern novelty | Bot with reaction-time noise |
| Survivor-like / action | Enemy HP and DPS scaling, spawn rate, elite cadence | Telegraph windows, arena size | Kiting bot, wave sims |
| Tower defence / strategy | Wave HP budget, enemy speed, path length | Resource income, build slots | Wave maths (`genre-playbooks` strategy) |
| RPG campaign | Enemy power vs recommended power, enemy composition | Status effects, AI behaviour | Battle sim with team presets |
| Physics puzzle | Tolerance windows, object counts | Gravity, friction | Deterministic replay + search |

**Lever-quality rule.** Prefer levers that create **new decisions** (a new blocker that changes priorities) over levers that only **remove slack** (one fewer move). Slack-removal is cheap and precise, which makes it perfect for fine-tuning. A game whose only lever is slack-removal feels stingy within a few chapters.

## 10. Measuring with bots and calibrating to humans

**Bot ladder.**

| Bot | Role | Expected relation to humans |
|---|---|---|
| Random legal move | Lower bound; softlock and crash finder | Far below humans on skill games |
| Greedy heuristic | Baseline difficulty estimator | Below average humans on look-ahead games |
| Look-ahead / MCTS | Upper bound; solvability proof | Above most humans |
| Imitation / human-like | Production estimator (needs player data) | Closest; the approach King has published |

**Calibration procedure** (after soft launch, or with a human playtest panel):

1. Pick at least 30 levels spanning the difficulty range, each with a few hundred first attempts (±2.5 points at n = 400).
2. Compute `logit(human_FAWR)` and `logit(bot_win_rate)` per level.
3. Fit `logit(human) = a + b·logit(bot)` by least squares. Typical findings: b < 1 (bots spread difficulty wider than humans), and a shifts with bot strength.
4. Use the fit to convert bot results for new levels into predicted human FAWR. Re-fit every content drop, and whenever a new mechanic appears (bots and humans learn new mechanics differently).
5. Keep a **residual watchlist**: levels where live FAWR differs from predicted by more than about 10 points. These usually involve a human perception problem (an unreadable blocker, a misleading layout) that bots cannot see.

**Static difficulty features** worth logging for discrete puzzles, as inputs to a regression or as early warnings: slack = move limit − solver min moves; number of distinct solutions; branching factor; dead-end density (share of states from which the level is unwinnable); number of interacting mechanics; and the novelty flag (first appearance of an element).

## 11. `difficulty_curve.py` usage

The plugin's difficulty tool lives at `${CLAUDE_PLUGIN_ROOT}/scripts/difficulty_curve.py` (stdlib only, `--json`, `--selftest`). Its command lines are fixed by the blueprint:

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/difficulty_curve.py generate --levels N \
    --pattern linear|sawtooth|stepped --base WINRATE --floor WINRATE \
    [--period P] [--hard-every K] [--json]

python3 ${CLAUDE_PLUGIN_ROOT}/scripts/difficulty_curve.py analyze \
    --data CSV(level,attempts,wins,churned) [--json]
```

**generate.** Every rate is the first-attempt win rate of an average player, with `0 < floor ≤ base ≤ 1`. `--help` lists only the flags, so here is what each does (checked by running them):

| `--pattern` | Shape (`--base` B, `--floor` F, `--period` P, default 10) |
|---|---|
| `linear` | Level 1 = B, falling in a straight line to F at level N |
| `sawtooth` | Teeth of P levels. At position i in a tooth (0-based) the rate is `B − (B − F)/2 · i/(P−1)`, so it falls towards the midpoint of B and F, and every K-th level (K = `--hard-every`, default K = P) is set to F instead. With K = P the last ordinary rate is 0.7111 for B = 0.92, F = 0.45, P = 10. The next tooth starts again at B, and every tooth is identical (no chapter drift) |
| `stepped` | Plateaus of P levels stepping evenly from B to F; the last plateau equals F |

`--hard-every K` (default 0 = off, except that sawtooth uses K = P) drops every K-th level to F in any pattern, and all rates are clamped to `[F, 1]`. The output has `win_rates[]`, `expected_attempts[]` (that is 1/rate, the mean attempts per win of a player at that rate, not `attempts_p50`) and a `summary` (mean, min, max). Exit code 0, or 2 on bad input.

Real run: `generate --levels 60 --pattern sawtooth --base 0.92 --floor 0.45 --period 10 --hard-every 10` returns, for every chapter, 0.92, 0.8939, 0.8678, 0.8417, 0.8156, 0.7894, 0.7633, 0.7372, 0.7111 and then 0.45 (mean 0.779). Level 10 is therefore a hard 0.45 level, which breaks the onboarding rule, and there is no relief step beyond the reset to 0.92. Post-edit the output against sections 5–6: overwrite the onboarding levels, vary the hard and super-hard values, add chapter drift and place relief after peaks. The §14 plan below is such an edited curve (for example its chapter 2 ramps 0.92 → 0.72 in steps of 0.025 and peaks at 0.50), not raw generator output. Typical calls:

| Intent | Command |
|---|---|
| Saga chapter plan | `generate --levels 60 --pattern sawtooth --base 0.92 --floor 0.45 --period 10 --hard-every 10 --json` |
| Mechanic-introduction plateaus | `generate --levels 40 --pattern stepped --base 0.90 --floor 0.60 --period 8` (0.90, 0.825, 0.75, 0.675, 0.60 in plateaus of 8 levels) |
| Short tutorial arc | `generate --levels 10 --pattern linear --base 0.99 --floor 0.85` (0.99 falling to 0.85 in equal steps) |

Write each level's target into `level-spec.difficulty_target.win_rate` (and `attempts_p50`, computed as in §2.2). Mirror the curve in `economy-model.levels.difficulty_curve` {`type`, `params`} so the economy simulator uses the same assumptions.

**analyze.** Export one row per level from telemetry as counts: `level,attempts,wins,churned` (rows with the same level are summed). The tool computes `win_rate = wins / attempts` and `churn_rate = churned / attempts` and compares each level with the median of up to three neighbours on each side. It flags `win_rate_dip` (win rate at least 0.15 below the neighbour median) and `churn_spike` (churn rate at least double the neighbour median, at least 0.03 above it, and at least 0.03 itself). Levels with fewer than 30 attempts are marked `low_sample` and never flagged. Each flagged level gets a re-tune target (`target_win_rate`, `attempts_per_win`). The exit code is 1 when any level is flagged, 0 when none is, and 2 on bad input; `--json` returns `levels[]`, `flagged[]`, `summary` and `ok`. The comparison is against neighbours, not against `difficulty_target`, so a deliberate hard level will be flagged `win_rate_dip`: check each flag against the level's target and its `teach` role before re-tuning. Interpret the output with section 12, and set `wins` from first attempts if you want FAWR rather than APW (document which you used); `attempts` and `churned` must use the same population as `wins`.

## 12. Telemetry diagnostics

**Events.** Instrument `level_start`, `level_complete` and `level_fail` with `level_id`, `attempt_index`, `moves_left` (or `time_left`), `goal_progress`, `boosters_used`, `continue_used` and `seed`. Use the event taxonomy (`event_taxonomy.py`, `player-analytics`).

**Diagnostic table.**

| Symptom in data | Likely cause | Check | Fix |
|---|---|---|---|
| Level churn more than about 2× the median of its 10 neighbours | Spike, unreadable mechanic, or a life-bar wall | FAWR, attempts p90, progress on loss | Ease, relabel as hard with a reward, add a hint |
| FAWR far below target but churn normal | Players accept it (labelled, rewarded) | Booster rate, payer share | Leave it, or reduce booster dependency |
| FAWR on target, churn high | Long or boring level, or failure feels unfair | Time per attempt, playtest "why" | Shorten; improve failure explanation |
| Many near-misses (progress on loss > 90%) | Move limit too tight | Moves-left histogram on wins | +1–2 moves; check for engineered near-miss logic |
| High booster rate on a normal level | Hidden difficulty; boosters masking a spike | Bot FAWR without boosters | Ease the level itself |
| Wins cluster at 0–1 moves left | Tight but fair, or a coin flip | Variance across seeds | Reduce variance (refill rules), not only difficulty |
| Late-level FAWR rising over months | Survivor skill rising; meta power creep | FAWR by player-level cohort | Recalibrate targets by cohort; see `power-and-balance.md` §1 |
| Sudden FAWR shift after an update | Bug, RNG change, or booster change | Diff level configs and seeds | Roll back via remote config |

**Rolling recalibration loop:** weekly, list levels outside target ± tolerance (for example ±8 points on normal levels, ±10 on hard ones) that have enough samples (§2.4). Propose changes in 5–10% steps of the lever (moves, colours, HP), re-simulate, and ship through remote config with an A/B holdout (`ab_test.py`).

## 13. Difficulty modes, assists and accessibility

| Approach | Example | Strength | Risk |
|---|---|---|---|
| Explicit modes (Easy / Normal / Hard) | Common in premium games | Transparent; player-owned | Pride stops players lowering difficulty; label modes by experience, not skill |
| Assist toggles | *Celeste* (2018) Assist Mode: game speed, extra stamina, invincibility, framed as non-judgemental | Accessibility; separates challenge from completion | Must not lock out content or achievements without a reason |
| Optional objectives | Star ratings, challenge goals, speed-run timers | Player-driven difficulty (Chen's point) | Must not gate core progress |
| Risk/reward choices | Hard path vs easy path, wagers, elite enemies | Agency; flow by choice | Needs clear signposting |
| Skip after N fails | Some premium puzzle games | Prevents permanent walls | Undermines a challenge identity; use in narrative games |
| Accessibility settings | Larger touch targets, longer windows, colour-blind palettes, reduced motion | Widens the audience; often legally expected | None. Do it (`accessibility-localization`) |

**F2P note.** In free-to-play, an explicit Easy mode competes with booster sales, which is exactly why it should be considered. The doctrine is player first. Offer accessibility options regardless of monetization, and never make them paid.

## 14. Worked example: a 60-level saga plan

**Brief.** Casual sort-puzzle saga, chapters of 10 levels, sawtooth with a hard peak at every chapter end and a super-hard at level 50. Targets are FAWR for the median active player.

**Plan.**

| Levels | Normal levels (ramp) | Peak (level x0) | Chapter avg FAWR | Expected attempts (median player) | Expected losses |
|---|---|---|---|---|---|
| 1–10 | 0.99 → 0.90 (onboarding) | Level 10: 0.80 (first "challenge", not labelled hard) | 0.939 | 10.7 | 0.7 |
| 11–20 | 0.92 → 0.72 | Level 20: hard 0.50 | 0.788 | 13.0 | 3.0 |
| 21–30 | 0.90 → 0.68 | Level 30: hard 0.45 | 0.756 | 13.7 | 3.7 |
| 31–40 | 0.88 → 0.66 | Level 40: hard 0.45 | 0.738 | 14.0 | 4.0 |
| 41–50 | 0.87 → 0.64 | Level 50: super-hard 0.35 | 0.714 | 14.9 | 4.9 |
| 51–60 | 0.86 → 0.62 | Level 60: hard 0.42 | 0.708 | 14.7 | 4.7 |
| **Total** | | | **0.774** | **81.0** | **21.0** |

Chapter 2 detail (levels 11–20): 0.920, 0.895, 0.870, 0.845, 0.820, 0.795, 0.770, 0.745, 0.720, **0.50 (hard)**.

**Population reality check.** With skill spread s ~ N(0, 1) in logit units, the population mean is about **95 attempts** for 60 levels, not 81. A p25 player needs about 101 attempts and a p10 player about 136. The super-hard level 50 fails the tail constraint (the p10 player's p90 is 17 attempts).

**Decisions.**

1. Level 50: raise to 0.40 (p10 player's p90 drops to about 14), **and** gift one pre-level booster on the first attempt of every super-hard level (bot-measured uplift +20 points). The tail is now covered without a paid path.
2. Insert a hard level at 25 (0.55) to break the long 21–30 ramp, and add a reward-beat relief at 26 (0.92). One hard per 5 levels in chapters 3+ matches the cadence template.
3. Add a bounded streak assist (`references/dynamic-difficulty.md` §4): after every 2 consecutive losses on the same level, +0.3 logit, capped at +0.9, never on the first attempt of a labelled hard level, logged, and never tied to spending. Simulate it with `balance_math.py dda-sim --base 0.40 --trigger 2 --step 0.3 --max-assist 0.9`.
4. Lives: a 5-life bar empties (5 straight losses) for about 12% of median players at a 0.35 level (0.65⁵). With decision 1 (0.40, and a booster lifting the first attempt to about 0.60), this drops to about 5% (0.4 × 0.6⁴). Accept that as the designed stop point.
5. Commands to produce artefacts:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/difficulty_curve.py generate --levels 60 --pattern sawtooth \
    --base 0.92 --floor 0.45 --period 10 --hard-every 10 --json > .gamestudio/levels/curve_ch1-6.json
# the raw output is a constant sawtooth with a 0.45 hard level at 10, 20, ... 60: apply the plan's onboarding chapter,
# chapter drift, hard/super-hard values and decisions 1–2 by hand, then write difficulty_target into each level spec
python3 ${CLAUDE_PLUGIN_ROOT}/skills/progression-difficulty/scripts/balance_math.py attempts --win-rate 0.40 --cost-per-loss 1
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/puzzle_solver.py --level .gamestudio/levels/w1_l050.json --json   # solvable, min moves
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py validate .gamestudio/levels/w1_l050.json
```

6. Contract: `progression.difficulty` = `{"model": "sawtooth, period 10, hard at x0 and x5 from chapter 3, super-hard at 50", "target_win_rate": 0.77, "dda": {"trigger": "2 consecutive losses on the same level", "adjustment": "+0.3 logit per step, max +0.9", "bounds": "not on first attempt of labelled hard levels; never tied to spending; logged"}}`.

## 15. Difficulty checklist

- [ ] Each level has `difficulty_target.win_rate` and `attempts_p50`, derived from a named curve.
- [ ] Onboarding levels are near-unlosable, and failure there costs nothing.
- [ ] Hard levels: cadence 5–10, never consecutive, followed by relief, labelled, rewarded, with no new mechanics.
- [ ] Tail constraint checked (p10 player's p90 attempts on hard levels), with free help where it fails.
- [ ] Every level is verified by a solver or bot without paid boosters; booster uplift is measured.
- [ ] Failure cost per stage follows the ladder; retry takes seconds.
- [ ] Fail-screen offers pass the red lines (no engineered near-misses, honest continues, one offer).
- [ ] Bot-to-human calibration fitted after soft launch, with a residual watchlist.
- [ ] Telemetry events exist for start, complete and fail, with attempt index, slack and boosters.
- [ ] The weekly recalibration loop is defined, with sample-size rules and A/B holdouts.
- [ ] Accessibility and assist options exist and are not paid.
- [ ] `contract.progression.difficulty` records the model, target and DDA bounds.

## 16. Volatile facts (as of Oct 2026 — verify before relying)

| Fact | Source |
|---|---|
| King (Candy Crush) published a CNN-based agent trained on player moves to predict "human" moves. Bot playthroughs predicted level difficulty, and the paper reports use across more than 1,000 new Candy Crush Saga levels. | Gudmundsson et al. 2018 — https://www.Gwern.net/doc/reinforcement-learning/imitation-learning/2018-gudmundsson.pdf |
| King-related follow-up work reports difficulty estimates in under a minute, versus about 7 days of human playtesting per 15-level episode. Simulating several player strategies improved error over a single strategy (MAE about 13% better). | Politecnico di Milano thesis — https://www.politesi.polimi.it/handle/10589/141799 |
| LLMs are not human-level players, but have been proposed as difficulty testers (Wordle, Slay the Spire experiments). | Xiao & Yang, arXiv:2410.02829 — https://arxiv.org/abs/2410.02829 |
| LLM-generated, difficulty-labelled Snake levels validated by A* were 87% playable at easy difficulty and 36% at hard. Hard generated content needs the strictest verification. | FedCSIS 2025 — https://annals-csis.org/Volume_43/drp/1909.html |
| Multi-agent LLM self-play combined with Bayesian optimization converged to balanced rule configurations on a simplified civ-like game (research). | RuleSmith, arXiv:2602.06232 — https://arxiv.org/abs/2602.06232 |
