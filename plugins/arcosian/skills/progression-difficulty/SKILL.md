---
name: progression-difficulty
description: 'Progression and difficulty codex: XP and cost curves (linear, poly, exp, logistic, piecewise), time-to-level, soft caps, catch-up; sawtooth difficulty, win-rate targets, hard-level cadence, failure costs, boosters; DDA methods and ethics; unlock pacing and FTUE; power curves, damage formulas, cost curves, PvP balance. Use when asked to "design the XP curve", "tune difficulty", "add DDA", "pace unlocks", "fix the tutorial" or "balance units".'
when_to_use: 'Designing or auditing progression tracks, level difficulty, DDA, unlock schedules, FTUE, stat and damage formulas, unit costs or PvP balance.'
---

# Progression and Difficulty

This skill turns pacing from a feeling into numbers you can verify. It answers five recurring questions. How long should each step of progress take? How hard should each level be, and for whom? When, and how far, may the game adapt to the player? In what order do features and concepts arrive? Does power stay meaningful without dominating skill or the wallet? Every model here ends in a procedure, a formula, a target table or a command. Most outputs land in `contract.progression`, `contract.ftue` and level specs.

## What this skill gives you

- **Curve maths that starts from time:** five curve families with closed forms, side-by-side tables, famous XP tables and their lessons, the pacing equation t(n) = c(n)/i(n), and income-aware design, caps, soft caps, catch-up and pass tracks, plus `progression_calc.py` usage.
- **Difficulty as a measured quantity:** first-attempt win rate, attempts distributions, the heterogeneity (Jensen) trap, the flow channel, sawtooth/stepped/hard-every-K shapes, stage targets (stated as design targets), hard and super-hard cadence, failure costs, boosters, bot calibration and `difficulty_curve.py` usage.
- **A DDA standard:** rubber banding, intensity directors, hidden assists, streak assists, skill-rating selection and gifted help, with a controller spec, evaluation design, the engagement-optimized matchmaking controversy, and binding ethics red lines.
- **Unlock and FTUE design:** complexity budget, novelty schedule, a gating catalogue, time to aha, teaching in context, progressive disclosure, first session/day/week templates, onboarding funnel targets and diagnosis.
- **Power and balance:** power share, power ratio → win rate, stacking, damage and armour formulas, EHP, TTK, PvP metrics, weighted RPS, cost curves, Lanchester's laws and a spreadsheet-plus-simulation methodology.
- **A calculator:** `scripts/balance_math.py`: attempts, population mix, funnels, DDA Monte Carlo, damage formulas, TTK, robust cost-curve fits, Lanchester and soft caps. Stdlib only, `--json`, passes `--selftest`.

## Core models

### 1. Design time, derive numbers
Players feel time-to-level (TTL) and power gaps, never raw costs. Write a beat sheet in play minutes, set TTL at 3–5 anchor levels, model income i(n), then derive cost c(n) = t(n) × i(n). Only the cost-to-income ratio matters. Absolute numbers are a feel choice. (`references/progression-curves.md` §2, §6)

### 2. Curve families have personalities
Linear flattens, polynomial front-loads growth and then eases, exponential back-loads into a wall, logistic saturates, and piecewise lets each phase have the right shape. Exponential cost against linear income is the most common progression bug. Always compute TTL at the last level. Keep level-over-level growth in a stated band, and make every exception a named beat. (§3–4)

### 3. Income grows too
The felt growth rate is the cost growth minus the income growth (exactly ×r/q for exponentials). Check for TTL inversions (unplanned faster levels) and runaway walls (TTL growth above about 15% per level for more than 5 levels). (§7)

### 4. Soft caps express value in the player's unit
Use hyperbolic (`x/(x+k)`), exponential or piecewise diminishing returns rather than hard cliffs. Express a stat in the unit whose value is linear to the player (effective HP, casts per minute), then convert to a displayed percentage. Convert overflow at caps into something useful. (§9)

### 5. Difficulty is a win rate, and averages lie
Store first-attempt win rate (FAWR) and attempts p50 per level. Mean attempts is the average of 1/p, so a population FAWR of 0.5 can hide 3+ mean attempts and a long stuck tail. Set targets on the median player, and gate hard levels on the weak tail (p10 player's p90 attempts ≤ about 12 without boosters). (`references/difficulty-design.md` §2)

### 6. Flow is three slopes
P(win) = σ(skill + power − difficulty). Over any window of about 10 levels, the difficulty rise should match skill growth plus power growth. Oscillate around that trend (sawtooth): ramp, peak, relief. Teach levels lower difficulty because skill on the new element is near zero. (§3–4)

### 7. Hard levels are labelled, rewarded, followed by relief, and never teach
Cadence: hard every 5–10 levels, super-hard every 20–40, never consecutive, never in onboarding. Each must be solvable by bots without paid boosters, show its label before the attempt, and pay more. (§6)

### 8. Failure cost is a design lever
Felt cost per clear ≈ (1/p − 1) × cost per loss. Retry in seconds, explain every failure, charge nothing in onboarding, and put progress at stake only in opt-in modes. The fail screen is both the churn moment and the offer moment, so it carries the strictest ethics. (§7–8)

### 9. DDA is a bounded control loop, never a sales tool
Specify target, signal, estimator, actuator, bounds, cadence and logging. Help fast, withdraw slowly, cap the assist so mastery is preserved, and defend against sandbagging. Never use spend signals, never sell into frustration, never hide DDA in ranked play. Apply the config-reading test. (`references/dynamic-difficulty.md` §4, §6)

### 10. Teach one thing at a time, just in time
Use a complexity budget of 1–2 concepts in the first minute and 4–6 in session 1, with one currency. Unlock a system at its pull moment, dangle locked features with their conditions, celebrate each unlock and give it a mini-FTUE of at most 3 beats. (`references/unlocks-pacing-ftue.md` §1–5)

### 11. Get to the aha fast
First input within about 10–15 s of the first frame. Aha within 30–60 s for casual games (practitioner guidance treats more than about 90 s as a retention risk). First win within 1–2 minutes. Meta hook and exit hook in session 1. No interstitials, purchases or account walls before value. (§6–7)

### 12. Bound the power bridge
Meta power should move bot win rates by at most about 10–15 points on designed content in skill-led games. Map power ratio to win rate with P(win) = σ(β·ln(P/E)), fitted from sims. Walls must show the shortfall, have a free path within about a daily cycle, and never be synchronised with offers. (`references/power-and-balance.md` §1–2)

### 13. Balance is curves plus counters plus evidence
Fit costs against a power metric that matches your combat law (Lanchester: square law → cost ∝ √(DPS·HP); linear law → ∝ DPS·HP). Give every option a counter. Buffing an option mainly raises the play rate of its counter (weighted RPS). Change numbers in 5–10% steps, simulate before shipping, and watch after. (§8–11)

### Rules of thumb (starting points, then verify)

| Topic | Starting rule | Source of truth |
|---|---|---|
| First-session TTL | 1–3 min per level-up | `progression-curves.md` §6 |
| Level-over-level cost growth, main game | Inside a stated band (e.g. 3–12%) | `progression-curves.md` §4 |
| Exponential doubling | ln 2 / ln r levels (1.08 → 9.0; 1.15 → 5.0) | `progression-curves.md` §3.3 |
| Pass completion | A 75%-of-days player finishes; a daily player gets overflow tiers | `progression-curves.md` §13 |
| Onboarding FAWR | 0.95–1.00 | `difficulty-design.md` §5 |
| Hard / super-hard FAWR (early mid) | 0.40–0.55 / 0.30–0.40 | `difficulty-design.md` §5 |
| Win-rate sample size | ±2.5 points needs ~400 first attempts at p ≈ 0.5 | `difficulty-design.md` §2.4 |
| Streak assist | +0.2–0.4 logit per 2–3 losses, cap 0.6–1.0 logit | `dynamic-difficulty.md` §3.4 |
| Complexity budget | ≤ 4–6 new concepts in session 1; ≤ 1 currency | `unlocks-pacing-ftue.md` §2 |
| Tutorial step conversion | ≥ 97–98% per mandatory step (internal target) | `unlocks-pacing-ftue.md` §8 |
| Meta power uplift | ≤ +10–15 points of bot win rate | `power-and-balance.md` §1 |
| Hyperbolic armour | Each point = HP/k effective HP; buy armour while HP > k + def | `power-and-balance.md` §5 |
| PvP flags | Win rate outside ~45–55%; blind-pick matchup beyond ~65/35 | `power-and-balance.md` §7 |

All targets marked as targets are studio starting hypotheses, not industry facts. Recalibrate them with telemetry.

## Decision procedures

### A. Design a progression track
1. Name the track's role (fast, medium, slow, seasonal) and decide whether it is the spine that drives unlocks.
2. Write the beat sheet in play minutes for the target archetype (usually mid), with 3–5 anchors.
3. Choose TTL per segment; pick a family per segment (procedure G); join the seams continuously.
4. Model income i(n) from all sources; derive c(n) = t(n) × i(n); round to readable numbers.
5. Check the growth band, TTL inversions and runaway walls; check calendar days for light, mid and heavy archetypes.
6. Add the cap, overflow conversion, soft caps and catch-up.
7. Generate the table: `progression_calc.py curve …` or `time-to-level --table …`; hand-tune within ±10%.
8. Write `contract.progression.tracks[]` (`type`, `curve` {`formula`, `params`}, `unlocks`), then `gs.py validate`.

### B. Plan a level difficulty curve
1. Choose the shape (sawtooth by default for level-based games) and the period (usually 10).
2. Set stage targets from `difficulty-design.md` §5. Place hard and super-hard levels per §6; add relief after every peak.
3. Generate targets: `difficulty_curve.py generate --levels N --pattern sawtooth --base 0.92 --floor 0.45 --period 10 --hard-every 10 --json`. The output is a constant sawtooth: each 10-level tooth ramps from 0.92 to 0.7111 and level 10, 20, … is set to the floor 0.45, so level 10 is a hard level. Post-edit for onboarding, chapter drift and relief rules (`references/difficulty-design.md` §11).
4. Compute `attempts_p50` per level (`balance_math.py attempts`) and check the tail constraint with the population model.
5. Build levels with the teach-test-twist-reward plan (`level-design`); verify with solvers or bots without paid boosters; record `level-spec.solver`.
6. Calibrate bots to humans after soft launch (fit logit-human vs logit-bot); keep a residual watchlist.
7. Set the weekly recalibration loop (`difficulty_curve.py analyze`), with sample-size rules and an A/B holdout.

### C. Decide whether and how to adapt (DDA)
| Situation | Choose |
|---|---|
| Premium or narrative game with a broad audience | Player-chosen modes and assist toggles first |
| Level-based F2P casual | Bounded streak assist + gifted help, rung 2–3 transparency |
| Real-time action, survivor-like, runner | Intensity director for pacing; always-on fairness assists |
| Racing | Pack rubber banding, faded out at the finish; visible catch-up items |
| Procedural content pool | Skill-rating content selection within a band |
| Ranked PvP | No DDA. Pure rating + latency matchmaking, published principles |
| Casual PvP | New-player pools, labelled bots, short loss-streak relief, documented |

Then specify the controller (`dynamic-difficulty.md` §4), simulate (`balance_math.py dda-sim`), A/B with guardrails (§5), and pass the ethics review (§6).

### D. Design the FTUE and the unlock schedule
1. Set `contract.ftue.aha_seconds_target` (30–60 s for casual) and list beats with one concept each and `max_seconds`.
2. Budget the seconds from cold start to aha; cut logos and lore; constrain the first boards.
3. Apply the progressive-disclosure order for HUD and menus; place permission, account and ad surfaces after value.
4. Build the novelty schedule (first 10 minutes, first hour, days 2–7) and place unlocks at their pull moments, converting minutes to levels via the TTL table.
5. Check the complexity budget and the gate graph (acyclic, solo path, no paid core gates).
6. Instrument the funnel with contract step ids; verify with a deterministic FTUE playthrough and persona playtests; analyse with `balance_math.py funnel --min-step 0.97`.

### E. Balance pass (power, units, PvP)
1. State the power-share position for the genre; measure meta uplift and skill gap with bots.
2. Pick the damage formula (`power-and-balance.md` §4.3) and the stacking rules; write the order of operations.
3. Compute EHP marginal values, TTK/TTD bands and breakpoints.
4. Fit the cost curve with the right power metric (`balance_math.py costcurve`); resolve outliers.
5. Check counters (`decision_math.py matrix`) and the matchup matrix with self-play.
6. Change in 5–10% steps, run the balance regression suite, ship via remote config, and watch for 1–2 weeks. Hand larger sweeps to `/arcosian:balance` (`balance-pass` workflow).

### F. Diagnose from telemetry
| Symptom | Likely cause | First check | Read |
|---|---|---|---|
| Churn spike at one level | Spike, unreadable mechanic, life-bar wall | FAWR, attempts p90, progress on loss | `difficulty-design.md` §12 |
| Steady churn through the mid game | TTL runaway or novelty drought | TTL growth table; unlocks per day | `progression-curves.md` §7, `unlocks-pacing-ftue.md` §3 |
| Poor D1 with good installs | Slow aha; weak exit hook; FTUE leaks | Funnel, time to aha | `unlocks-pacing-ftue.md` §8 |
| Low D7/D1 | Days 2–7 lack new goals | First-week schedule | `unlocks-pacing-ftue.md` §7.4 |
| Players stall at the cap | No overflow or catch-up | Income wasted at cap | `progression-curves.md` §9–10 |
| High booster use on normal levels | Hidden difficulty | Bot FAWR without boosters | `difficulty-design.md` §8 |
| Spike of very short failed attempts | DDA sandbagging | Attempt duration before wins | `dynamic-difficulty.md` §4 |
| One option dominates PvP | Under-costed or missing counter | Cost-curve residual, matchup matrix | `power-and-balance.md` §7–9 |
| Payers win much more at equal skill | Power share too high in PvP | Win rate vs level differential | `power-and-balance.md` §7.4 |

### G. Choose a curve family
| Track | Family | Why |
|---|---|---|
| Tutorial ramp, chapters, star gates | Linear | Readable; short |
| Character, hero or card levels with growing income | Polynomial (e ≈ 1.5–3) | Steady growth that eases |
| Idle generators; deliberate late walls | Exponential (r ≈ 1.07–1.15 for idle) | Matches compounding income |
| Mastery, collections, endgame grinds | Logistic | Bounded; predictable plateau |
| Anything longer than ~30 levels | Piecewise | Right shape per phase |
| Pass tiers | Flat (linear with g = 0) | Players compare with the calendar |

## Mobile specifics

- **Sessions are short and interrupted.** Pace in sessions, not hours: at least one visible bar moves every session. The first session must reach aha, first win and meta hook even if it lasts 3 minutes.
- **Retry speed is a difficulty parameter.** A fail-to-retry loop of a few seconds makes a 40% level tolerable; a 20-second loop makes it punishing.
- **Lives and energy turn difficulty into session length.** A 0.35 hard level empties a 5-life bar for about 12% of median players (0.65⁵). Decide whether that is the designed stop point.
- **Touch input and small screens lower effective skill.** Widen execution windows, use fairness assists (coyote time, generous hitboxes), and favour cognitive over twitch difficulty in casual games.
- **Archetype spread is huge.** Light and heavy players reach the same level about 9× apart in calendar time. Use dailies, timers and catch-up to compress the spread without punishing the heavy player.
- **F2P puts money next to frustration.** Hard levels, fail screens and walls are where offers live. Labelled, rewarded, booster-free-solvable hard levels and the DDA red lines keep this ethical.
- **Datamining is routine.** Players will read DDA configs and drop tables. Design for the config-reading test.
- **Low-end devices change difficulty.** Frame drops widen effective reaction windows in the wrong direction. Test difficulty on the low tier from `contract.technical.min_spec` (`mobile-performance`).

## Anti-patterns

| Anti-pattern | How to detect | Fix |
|---|---|---|
| Formula-first curves | Costs defined before any TTL target | Beat sheet → TTL → derive cost |
| Exponential cost, linear income | Runs or minutes per level explode after mid game | Lower r, compound income, or go piecewise |
| Average-only difficulty | Targets met but churn spikes at hard levels | Population model; tail constraint |
| Hard levels in onboarding | Level churn spikes before level 15–20 | Move peaks after habit formation |
| Unlabelled walls | Players report "impossible level"; reviews mention paywalls | Label, reward, show the shortfall, give a free path |
| Booster-dependent normal levels | Normal levels unwinnable for bots without boosters | Re-tune levels; boosters for hard levels only |
| Engineered near-misses | Loss states cluster at "one away" more than the bot baseline | Remove the manipulation; honest continues |
| Spend-linked or hidden ranked DDA | Assist or matchmaking reads payer, wallet or purchase data | Structural separation plus unit tests; publish principles |
| Win-streak punishment | Difficulty rises after wins | Opt-in stakes instead |
| Everything unlocked at once | > 6 concepts in session 1; menu tours | Complexity budget; just-in-time unlocks |
| Monetization in the FTUE | Offers, interstitials or account walls in session 1 | Gate surfaces until value is proven |
| Cross-gated tracks | Track A needs B, B needs A; players deadlock | Acyclic gate graph; one spine |
| Wasted income at the cap | XP still earned at cap with no outlet | Overflow track; prestige; cosmetics |
| Stat-sheet power creep | Each release sits above the cost curve | Fit every release to the curve; rotate, don't inflate |
| Displayed power that doesn't predict wins | Equal "combat power" teams with very different win rates | Re-weight the score; say "recommended" |
| Hard counters in blind pick | Matchups beyond 65/35 with no adaptation | Soften counters; add re-picks or information |

## Using the ontology

This domain maps directly onto the shared schemas in `${CLAUDE_PLUGIN_ROOT}/scripts/schemas/` (full definitions in `game-ontology`).

| Concept | Where it lives | Notes |
|---|---|---|
| Progression tracks | `contract.progression.tracks[]` {`id`, `type`, `curve` {`formula`, `params`}, `unlocks` [{`at`, `unlock`}]} | `formula`: `linear`, `poly`, `exp`, `logistic`, `piecewise` or an explicit expression; types such as `player_level`, `chapter`, `character_level`, `mastery`, `battle_pass`, `prestige` |
| Difficulty model | `contract.progression.difficulty` {`model`, `target_win_rate`, `dda`} | `dda`: `false` or {`trigger`, `adjustment`, `bounds`}; never tied to spending |
| Per-level targets | `level-spec.difficulty_target` {`win_rate`, `attempts_p50`}, `level-spec.teach` (`teach`, `test`, `twist`, `reward`) | Targets from the curve; beats from the cadence template |
| Verification | `level-spec.solver` {`solvable`, `min_moves`, `bot_win_rate`, `runs`} | Written by `puzzle_solver.py` / `match3_sim.py` |
| Economy-side difficulty | `economy-model.levels` {`count`, `base_win_rate`, `difficulty_curve` {`type`, `params`}} | Keep in sync with the contract curve |
| Booster and lives flows | `economy-model.resources`, `nodes` (`per_level_loss`, `per_level_win` triggers) | Simulate free booster income per hard level |
| FTUE | `contract.ftue` {`aha_seconds_target`, `steps` [{`id`, `goal`, `teaches`, `max_seconds`}]} | Step ids become the tutorial event's `step` parameter |
| Tunable parameters | `contract.mechanics[].parameters` [{`key`, `value`, `min`, `max`, `unit`}] | Balance changes stay within min/max |
| KPI targets | `contract.analytics.kpi_targets` (`d1`, `d7`, `d30`, …) | Funnel and retention checks |
| Evidence | `playtest-report.metrics` (`win_rate`, `time_to_first_reward_sec`) | Bot and FTUE playthroughs for the `playthrough` gate |
| Events | `event-taxonomy` categories `ftue`, `progression`, `economy` | `level_start/complete/fail`, `dda_adjust`, tutorial steps |

**Tools.**

| Task | Command |
|---|---|
| Curve exploration | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/progression_calc.py curve --formula exp --levels 50 --base 100 --growth 1.08 --xp-per-min 40 --json` (`--growth` means: linear XP added per level, exp multiplier, logistic steepness, piecewise late-game multiplier; poly uses `--exponent` instead) |
| TTL for an edited table | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/progression_calc.py time-to-level --table .gamestudio/economy/xp_table.json --xp-per-min 40` (table: JSON list, `curve --json` output or CSV with an `xp_to_next` column) |
| Level win-rate targets | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/difficulty_curve.py generate --levels 60 --pattern sawtooth --base 0.92 --floor 0.45 --period 10 --hard-every 10 --json` (first-attempt win rates; `linear`, `sawtooth` or `stepped`; hard levels are set to `--floor`; every tooth is identical) |
| Telemetry analysis | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/difficulty_curve.py analyze --data level_stats.csv --json` (CSV of counts `level,attempts,wins,churned`; flags `win_rate_dip` ≥ 0.15 below the neighbour median and `churn_spike` at ≥ 2× the neighbour median and ≥ 0.03 above it; levels under 30 attempts are never flagged; exit 1 when anything is flagged) |
| Attempts and failure cost | `python3 ${CLAUDE_PLUGIN_ROOT}/skills/progression-difficulty/scripts/balance_math.py attempts --win-rate 0.4 --cost-per-loss 1` |
| Population tail | `… balance_math.py mix --rates "0.8:0.5,0.2:0.5"` |
| DDA simulation | `… balance_math.py dda-sim --base 0.40 --trigger 2 --step 0.3 --max-assist 0.9` |
| FTUE / level funnel | `… balance_math.py funnel --steps "first_open:10000,tutorial_start:9400,…" --min-step 0.97` |
| Damage formulas / TTK | `… balance_math.py damage --atk 100` · `… balance_math.py ttk --hp 1200 --damage 90 --rate 1.25` |
| Cost curve | `… balance_math.py costcurve --units "archer:3:52,knight:4:66,…" --fail-on-outlier` |
| Lanchester / soft caps | `… balance_math.py lanchester --a 20 --b 10 --a-eff 1 --b-eff 3` · `… balance_math.py softcap --formula hyperbolic --k 100` |
| Payoff matrices | `python3 ${CLAUDE_PLUGIN_ROOT}/skills/design-theory/scripts/decision_math.py matrix --payoff "…"` |
| Economy and boosters | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/economy_sim.py --model .gamestudio/economy/model.json --runs 200` |
| Level verification | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/match3_sim.py --level PATH --runs 500` · `puzzle_solver.py --level PATH` |
| A/B sizing and analysis | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ab_test.py size --baseline 0.18 --mde 0.01` |
| Validate after edits | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py validate .gamestudio/contract.json` |
| Search the codex | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py kb "hard level cadence" --skill progression-difficulty` |

`balance_math.py` exit codes: 0 ok, 1 check failed (`funnel --min-step`, `costcurve --fail-on-outlier`), 2 usage error. `progression_calc.py` exits 0 or 2 only; `difficulty_curve.py analyze` exits 1 when it flags levels.

The `logistic` and `piecewise` families of `progression_calc.py` are fixed shapes, not the general forms of `references/progression-curves.md` §3: logistic costs run from about the base to 10 × the base with the midpoint at the middle level, and piecewise grows in three thirds at 25%, 60% and 100% of the growth rate you pass (exact formulas in §14 of that file). Hand-built segment curves are shipped as tables.

## Reference library

| File | What it contains | Read it when |
|---|---|---|
| `references/progression-curves.md` | Pacing equation; linear, polynomial, exponential, logistic and piecewise curves with closed forms; comparison tables; RuneScape, Pokémon and tabletop XP tables; TTL-first design; income growth; archetype calendar time; caps and soft caps; catch-up; multi-track rules; idle and pass curves; `progression_calc.py`; four worked examples | Designing or auditing any XP, upgrade, mastery or pass track |
| `references/difficulty-design.md` | Difficulty dimensions; FAWR, attempts tables, the Jensen trap, sample sizes; flow channel model; curve shapes; stage win-rate targets; hard and super-hard cadence; failure costs; boosters and fail-screen ethics; levers by genre; bot calibration; `difficulty_curve.py`; telemetry diagnostics; modes and assists; a 60-level worked plan; volatile facts | Planning level targets, placing hard levels, tuning from telemetry, designing boosters and lives |
| `references/dynamic-difficulty.md` | DDA taxonomy; landmarks; rubber banding, directors, hidden assists, streak assists, skill ratings, content selection, gifted help; controller design; evaluation; ethics red lines and transparency ladder; PvP matchmaking rules; the EOMM and patent controversy; implementation and QA; four worked examples | Adding any adaptive system, reviewing matchmaking, or answering "is this DDA ethical?" |
| `references/unlocks-pacing-ftue.md` | Pacing principles; complexity budget; novelty schedule; gating catalogue and methods; FTUE goals, time to aha, teaching in context, progressive disclosure, beat structure, consent prompts, anti-patterns; first session/day/week templates; funnel targets and diagnosis; re-onboarding; worked examples; volatile retention facts | Designing onboarding, scheduling unlocks, diagnosing D1/D7, onboarding new features |
| `references/power-and-balance.md` | Power share; power ratio → win rate; stacking; damage and armour formulas; EHP investment; TTK/TTD; PvP metrics and process; weighted RPS; cost curves and the combat-law insight; Lanchester; spreadsheet structure, simulation toolkit, sensitivity analysis, regression suite; worked examples | Itemisation, unit or card costs, combat formulas, PvP balance patches, balance tooling |
| `scripts/balance_math.py` | Calculators: `attempts`, `mix`, `funnel`, `dda-sim`, `damage`, `ttk`, `costcurve`, `lanchester`, `softcap` (`--json`, `--selftest`) | Whenever a number in these references needs recomputing for your game |

## Related skills

- `game-ontology`: the schemas and vocabulary these models write into.
- `design-theory`: flow, loops, interest curves and decision maths that underpin pacing.
- `mechanics-codex`: progression and meta mechanic cards (XP, unlock trees, passes, streaks, prestige).
- `economy-design`: currencies, sources and sinks, booster and lives economies, prestige maths.
- `level-design`: building levels that hit these targets (teach-test-twist-reward, solvers).
- `procedural-generation`: generators whose output needs difficulty verification.
- `player-psychology`: motivation, loss aversion and frustration, which explain why the curves feel as they do.
- `player-analytics`: funnels, cohorts and level telemetry that calibrate the targets.
- `mobile-ux`: onboarding screens, HUD reveal and thumb-friendly tutorial UI.
- `game-feel`: fairness assists, retry speed and feedback that change perceived difficulty.
- `monetization`: offers, boosters and passes placed ethically around difficulty.
- `liveops`: events and seasons that take over the novelty schedule after the first month.
- `multiplayer-backend`: rating systems and matchmaking implementation.
- `genre-playbooks`: genre conventions for power bridges, walls and level cadence.
- `legal-ethics`: dark patterns, minors and consumer-protection limits on adaptive systems.
- `accessibility-localization`: assist modes and accessibility settings.
