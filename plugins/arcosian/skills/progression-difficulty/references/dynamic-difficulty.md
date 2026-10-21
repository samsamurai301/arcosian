# Dynamic Difficulty

Dynamic difficulty adjustment (DDA) changes the challenge while the game is played, based on how the player is doing. Done well, it is an invisible safety net that keeps weak players out of frustration loops and strong players out of boredom. Done badly, it erases mastery, invites exploitation, or becomes a covert monetization lever that destroys trust. This file catalogues the methods (rubber banding, adaptive spawns and intensity directors, hidden assists, streak-based adjustment, skill-rating models, content selection, gifted help, player-chosen difficulty). It shows how to design a bounded controller, how to evaluate DDA with experiments, the engagement-optimized matchmaking controversy, competitive-mode rules, and the ethics and transparency standard this studio enforces. Static curves are in `references/difficulty-design.md`.

## Contents

1. Definitions and taxonomy
2. Landmarks: what shipped games and research established
3. Method catalogue
4. Designing a DDA controller
5. Evaluating DDA
6. Ethics and transparency (the studio standard)
7. Competitive modes and matchmaking
8. The engagement-optimized matchmaking controversy
9. Implementation, telemetry and QA
10. Worked examples
11. DDA checklist
12. Volatile facts (as of Oct 2026 — verify before relying)

---

## 1. Definitions and taxonomy

| Axis | Options | Notes |
|---|---|---|
| Who decides | Player (explicit modes, assists, optional objectives) · System (automatic DDA) · Hybrid (system suggests, player accepts) | The doctrine prefers player-driven where possible |
| Visibility | Visible (announced, toggled, labelled) · Discoverable (documented, not shown) · Hidden | Hidden must pass the config-reading test (§6) |
| Timing | Pre-attempt (level parameters, seeds) · In-attempt (spawns, AI speed, drops) · Post-attempt (gifts, hints, skips) | Pre-attempt changes are easiest to log and audit |
| Signal | Outcomes (wins and losses, streaks) · Performance (HP lost, time, accuracy) · Model (skill rating, churn risk) · Spending | Spending as a signal is a red line (§6) |
| Direction | Help only (assist) · Both (assist and challenge) | Challenge-raising DDA is the most often resented |
| Scope | Single player PvE · Co-op · PvP matchmaking | PvP has separate rules (§7) |

**Fairness assists vs adaptive assists.** Some assists compensate for the medium, not the player: touch latency, small screens, frame-rate variance. Examples are coyote time, input buffering and generous hitboxes. These are always on and are part of game feel (`game-feel`), not DDA. Adaptive assists respond to a particular player's performance. Only adaptive assists need the controls in this file.

## 2. Landmarks: what shipped games and research established

Summaries in our own words, for orientation:

- **Hunicke, "The Case for Dynamic Difficulty Adjustment in Games" (ACE 2005).** Described the Hamlet system, built on *Half-Life*, which estimated when a player was likely to run short (health, ammunition) and adjusted supply (pickups) and demand (enemy strength) to prevent repeated failure. It argued that well-hidden, bounded adjustment can keep players engaged without them feeling patronised.
- **Valve's *Left 4 Dead* AI Director (Michael Booth, AIIDE 2009 talk).** Tracked an estimate of each survivor's stress (damage taken, nearby threats) and cycled pacing through build-up, peak, fade and relax phases. Spawns followed the pacing state, not a fixed script. It is the reference design for adaptive spawning.
- **Kart racing item distribution (the *Mario Kart* series).** Item odds depend on race position: trailing players get stronger catch-up items, and a famous item targets the leader. Fully visible to players, it shows that catch-up can be part of the fun when it is legible.
- **Hidden adjustments in classic action games.** *Resident Evil 4* (2005) is widely documented by players as adjusting an internal difficulty rank from performance. Andy Gavin's "Making Crash Bandicoot" blog series (2011) describes quietly helping players who died repeatedly. Both stayed largely invisible for years, which shows how far subtle help can go unnoticed.
- **Opt-in rescue.** *New Super Mario Bros. Wii* (2009) offered a Super Guide demonstration after repeated deaths in a level. *Celeste* (2018) shipped Assist Mode with game speed, stamina and invincibility options, presented without judgement. Both represent the player-chosen side of the spectrum.
- **Research on engagement-optimized matchmaking** (Chen et al., WWW 2017) and a 2017 Activision patent on matchmaking to drive purchases mark where adaptation becomes contested (§8).

## 3. Method catalogue

### 3.1 Rubber banding (racing and chase games)

Adjust AI opponents (or pickups) based on the gap to the player.

```
gap = (ai_progress − player_progress) / track_length          # signed; + means AI ahead
m   = 1 − k · clamp(gap / gap_ref, −1, 1)                       # AI speed multiplier
m   = clamp(m, 1 − m_max, 1 + m_max)
```

Typical parameters (starting points): k so that the AI gives up or gains about 3–8% speed at `gap_ref`, and `m_max` ≤ 10%. Apply changes smoothly (a low-pass filter over seconds), never as visible jumps.

| Do | Don't |
|---|---|
| Rubber-band the pack, not the single rival the player is duelling | Let the AI catch up instantly after a perfect lap |
| Fade rubber banding out in the final stretch so the result is earned | Make the leader slower than physically plausible |
| Prefer visible catch-up (items, drafting) over invisible speed | Use rubber banding in time trials, ranked or replays |

### 3.2 Adaptive spawns and intensity directors (action, survivor-likes, runners)

```
stress(t) = decay · stress(t−Δ) + w_dmg·damage_taken + w_near·threats_in_radius + w_low·(HP < 30%)
phase: BUILD (raise spawn budget) → PEAK (hold for T_peak) → FADE → RELAX (minimal spawns for T_relax) → BUILD
switch BUILD→PEAK when stress ≥ S_high; PEAK→FADE after T_peak; FADE→RELAX when stress ≤ S_low
```

Starting parameters for a mobile survivor-like (tune per game): T_peak 15–30 s, T_relax 8–15 s, and a spawn budget in BUILD that rises 5–10% per 10 s. RELAX must still feel alive (pickups, loot, a low-threat trickle).

**Variants.** Distance-based escalation for runners, plus a relief section after a near-death. Elite cadence that skips an elite if the player is below 30% HP. Drop-rate tilt toward health when HP is low (Hamlet-style supply adjustment).

### 3.3 Hidden assists catalogue

| Assist | Mechanism | Adaptive? | Notes |
|---|---|---|---|
| Coyote time / jump buffering | Accept input slightly late or early | Always on | Game feel, not DDA |
| Aim assist / magnetism | Bend projectiles or the cursor toward targets | Often always on; can scale | Disclose in competitive modes; off or equalised in cross-input PvP |
| Generous hitboxes | Player hurtbox smaller than the sprite; enemy hitbox larger | Always on | Mobile staple |
| Last-sliver protection | Final fraction of HP drains slower or needs an extra hit | Can be adaptive | Creates "barely survived" moments; do not apply to enemies in PvP |
| Mercy invulnerability | Brief invulnerability after a hit | Always on; duration can scale | Stops stun-lock deaths |
| Attack tokens | Cap how many enemies attack at once | Can scale with stress | Keeps crowds readable |
| Favourable refills / spawns | Bias the RNG toward useful pieces | Adaptive if triggered by losses | Board games: must stay within disclosed rules; log the seed |
| Dynamic hints | Highlight a move after idle time or N losses | Adaptive | Visible; good for cognitive puzzles |
| Checkpoint relocation | Move the checkpoint closer after repeated deaths | Adaptive | Low perceptibility; strong effect |

### 3.4 Streak-based adjustment

The most common mobile DDA. It is cheap, explainable and easy to bound.

```
on level_fail(level):
    losses[level] += 1
    if losses[level] % trigger == 0 and not (level.hard and attempt_index == 1):
        assist[level] = min(max_assist, assist[level] + step)
on level_win(level):
    assist[level] = 0; losses[level] = 0
effective_p = σ(logit(p_base) + assist[level])           # assist in logit units
```

**Parameters (starting points):** trigger = 2–3 consecutive losses on the same level; step = 0.2–0.4 logit; max_assist = 0.6–1.0 logit. For a median player on a 0.40 level, a +0.9 cap lifts the win chance to about 0.62. Express the assist as a concrete lever (moves +1, HP −8%, one extra colour removed) and calibrate the lever-to-logit mapping with bots.

**Win-streak challenge (use sparingly).** Raising difficulty after a win streak punishes mastery and is the variant players resent most. If you need to challenge strong players, use **opt-in** stakes instead: streak ladders, hard modes, bonus goals.

### 3.5 Skill-rating models (player vs content)

Treat each level as a rated "opponent" and each player as having a rating θ. This is the Elo idea applied to PvE.

```
P(win) = σ(θ_player − d_level)                       # logit units; or the Elo form 1/(1+10^(−Δ/400))
after attempt: θ ← θ + K · (outcome − P(win))         # outcome 1 = win, 0 = loss
               d ← d − K_level · (outcome − P(win))   # levels learn from the whole population
```

Uses: predict each player's chance on upcoming levels, pick procedural levels near a target P(win), choose assist size, and flag levels whose `d` drifts. Use K around 0.2–0.4 per attempt (in logit units) for players, and a much smaller K for levels. Glicko-style uncertainty, with a larger K for new players, helps early. For PvP rating systems see §7.

### 3.6 Content selection and personalised ordering

With procedural or large handmade pools, choose the **next** level by predicted P(win) rather than adjusting the current one: easier picks after losses, harder after wins, within a band around the curve target. This is low-perceptibility, deterministic per seed, and easy to audit (log the chosen level id). It still counts as DDA: disclose it the same way.

### 3.7 Gifted help (economy-side)

After N losses on a level: a free booster, a life refill, a hint token. This is visible, feels generous, and teaches booster use. Bound it, for example to one gift per level per day. **Never** replace a gift with a paid offer for the same trigger. The trigger is frustration, and selling into frustration is the pattern the doctrine forbids.

### 3.8 Player-chosen difficulty

Modes, assist toggles, optional objectives, hard/easy paths and wagers (`references/difficulty-design.md` §13). These are the most respectful options and the first choice wherever the genre allows.

### 3.9 Method comparison

| Method | Perceptibility | Exploitability | Dev cost | Best genres |
|---|---|---|---|---|
| Rubber banding | Medium–high | Low | Low | Racing, chase |
| Intensity director | Low | Low | Medium | Action, survivor-like, horror |
| Hidden assists (always on) | Very low | None | Low | All real-time |
| Streak assist | Low–medium | Medium (sandbagging) | Low | Level-based casual |
| Skill-rating selection | Low | Medium | Medium–high | Procedural puzzle, roguelite |
| Gifted help | Visible | Low (cap it) | Low | F2P casual |
| Player-chosen | Visible | None | Low–medium | All |

## 4. Designing a DDA controller

Every DDA is a control loop. Specify all seven parts in the contract (`progression.difficulty.dda` as an object) before writing code.

| Part | Question | Example |
|---|---|---|
| Target | What value are we steering toward? | Median player's chance on this level ≈ curve target ± 10 points |
| Signal | What do we observe? | Consecutive losses on the level |
| Estimator | How do we turn signals into state? | Loss counter; or a rating θ |
| Actuator | What do we change? | Move limit +1 per step |
| Bounds | How far can it go? | Max +3 moves; never on the first attempt of a labelled hard level |
| Cadence and decay | How often, and does it reset? | Per 2 losses; resets on win and after 24 h |
| Logging | How do we audit and replay? | `dda_adjust` event with level, step, lever, seed |

**Proportional controller with deadband** (for continuous systems such as spawn budgets):

```
error = target_stress − measured_stress
if |error| < deadband: no change
else: budget += Kp · error, clamped to [budget_min, budget_max]; at most Δmax per tick
```

**Stability rules.**

- **Deadbands and rate limits** stop oscillation (easy → hard → easy within a minute).
- **Asymmetric speeds:** help quickly (after 2 losses), withdraw help slowly (reset on win, not by ramping up difficulty).
- **Hysteresis** for mode switches: enter "relief" at stress ≥ 0.8, exit at ≤ 0.4.

**Anti-exploitation (sandbagging).** If losing makes the game easier, some players will lose on purpose: fail quickly twice, then win the assisted attempt. Countermeasures: count only "real" attempts (minimum moves made or time spent), cap assist per level per day, and keep the assist smaller than the value of a skilled first-attempt win (rewards for first-attempt wins, star ratings). Measure it: a spike of very short failed attempts before a win is the signature.

**Determinism.** In a sim-core architecture (`game-architecture`), DDA state must be part of the seeded simulation input: the assist level is an explicit parameter of the attempt, not a hidden global. Then replays, bot runs and bug reports reproduce exactly. Store DDA parameters in remote config with defaults in code.

## 5. Evaluating DDA

**Hypothesis template.** "Bounded streak assist on levels 20–200 reduces 7-day level churn at hard levels by ≥ X% without reducing the payer conversion or the first-attempt win share by more than Y."

**Experiment design.**

1. Randomise at the **player** level, not per session. Keep a long-lived holdout (5–10%) to measure cumulative effects.
2. Primary metric: a retention or churn measure (D7, level churn at hard levels). Secondary: sessions per day, attempts per clear, the share of players stuck more than 3 days.
3. **Guardrails:** first-attempt win share (mastery should still be rewarded), reported fairness (in-game survey), booster purchase rate (watch for a *rise*, which would suggest the system is shaping spend), and very-short-failed-attempt rate (sandbagging).
4. Size it before launch: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ab_test.py size --baseline 0.18 --mde 0.01 --power 0.8 --two-sided`. As a sanity check, the standard two-proportion formula gives about 24,000 players per arm for 18% → 19% at α = 0.05, power 0.8.
5. Analyse with `ab_test.py analyze --a-success … --a-n … --b-success … --b-n …`. If you peek weekly, use `ab_test.py sequential`.
6. Before the live test, simulate the controller with `balance_math.py dda-sim` to choose the trigger, step and cap. A live test should not be the first time anyone sees the distribution of assists.

**Expected shape of results** (what a well-designed bounded assist typically does in simulation, not a promise of live uplift): first-attempt win rate unchanged, the mean and p90 attempts on hard levels down, the longest-losing-streak tail shortened, and a minority of clears assisted. See §10.1.

## 6. Ethics and transparency (the studio standard)

This section is binding for every game the studio builds. It operationalises doctrine principle 8 (ethical monetization) and the schema rule that DDA "must never be tied to spending".

**Red lines (never):**

1. **No spend-linked difficulty.** Difficulty, odds, matchmaking or assists never depend on payer status, wallet balance, purchase history, purchase propensity, or time since last purchase.
2. **No frustration selling.** Never make content harder to create demand for a paid item, and never time paid offers to a model of the player's frustration (loss streak, churn risk). Gifts on those triggers are fine; sales are not.
3. **No engineered near-misses** on paid continues or paid random outcomes (`references/difficulty-design.md` §8).
4. **No hidden DDA in ranked or competitive modes,** and no undisclosed bots presented as humans in ranked play.
5. **No adaptive odds on paid random items.** Paid loot odds are fixed and disclosed (`economy-design`, `legal-ethics`). Pity rules are disclosed rules, not adaptation.
6. **No exploitation of minors.** Where an age signal says the player may be a child, assists may help; nothing adaptive may touch monetization (`legal-ethics`).

**Transparency ladder (choose the highest rung that fits the design):**

| Rung | What the player knows | Example |
|---|---|---|
| 4: Player-controlled | They choose it | Assist toggles, modes |
| 3: Announced | Shown when it happens | "Bonus move added after 2 tries" |
| 2: Documented | Explained in help or FAQ | "The game gives a little help after repeated losses" |
| 1: Hidden but defensible | Not shown, but passes the config-reading test | Intensity director pacing |
| 0: Hidden and indefensible | Would embarrass the studio if read | Not allowed |

**The config-reading test.** Imagine the full DDA configuration and its triggers published on a fan wiki tomorrow. If the honest community reaction would be "that's thoughtful", it passes. If it would be "they rig it to sell boosters", it fails, and it fails even if no law forbids it. Players do read configs: datamining of mobile builds is routine.

**Regulatory awareness.** Consumer-protection regulators in several jurisdictions have been examining manipulative design in games (dark patterns, pressure selling, minors). This is volatile and jurisdiction-specific. Route specific questions to `legal-ethics` and `compliance-officer`, and keep the red lines above regardless of what a given market allows.

**Documentation duty.** Every DDA in a project is listed in `contract.progression.difficulty.dda` (trigger, adjustment, bounds) and reviewed by `arcosian:critic` and `arcosian:compliance-officer` in the `design-review` workflow.

## 7. Competitive modes and matchmaking

**Rating systems (stable background).**

| System | Origin | Key idea | Use |
|---|---|---|---|
| Elo | Arpad Elo; *The Rating of Chessplayers, Past and Present* (1978) | Expected score = 1/(1 + 10^(−Δ/400)); update by K × (result − expected) | 1v1, simple ladders; +191 points ≈ 75% expected |
| Glicko / Glicko-2 | Mark Glickman | Adds rating deviation (uncertainty) and volatility | Faster convergence for new or returning players |
| TrueSkill | Herbrich, Minka & Graepel (Microsoft Research), NIPS 2006 | Bayesian skill (μ, σ) for teams and free-for-all | Team games, many players per match |
| Open-source Bayesian variants | Various | TrueSkill-like, permissively licensed | Mobile backends (check licences) |

**Matchmaking objectives.** Parity (P(win) near 0.5), queue time, connection quality, party fairness and variety. Typical trade: widen the rating band as queue time grows.

**Acceptable adaptive practices (with disclosure):**

| Practice | Condition |
|---|---|
| New-player protection (separate pools, softer early opponents) | Time- or match-limited; disclosed in help |
| Bots in early or casual matches | Disclosed (label or help text); never in ranked; no rank points farmed from bots |
| Loss-streak protection in casual queues | Easier matchmaking band for a few matches; never in ranked |
| Rank floors and demotion protection | Visible rules |
| Level or stat normalisation in tournaments | Visible rules (some games use capped "tournament standard" levels) |

**Not acceptable:** matching to showcase items the opponent does not own in order to drive purchases; matching newly purchased items into favourable games to reward spending; hiding bots in ranked; adjusting in-match outcomes (damage, odds) based on rating gaps.

## 8. The engagement-optimized matchmaking controversy

**What was proposed.** Chen, Xue, Kolen, Aghdaie, Zaman, Sun and Seif El-Nasr, "EOMM: An Engagement Optimized Matchmaking Framework" (Proceedings of WWW 2017; authors from Electronic Arts and Northeastern University), framed matchmaking as an optimisation over **predicted churn**. Model each player's churn risk given their recent match outcomes, then choose pairings that minimise expected churn across the pool, instead of pairing purely by skill. The authors reported that, in their experiments, it beat skill-based and random matchmaking on their engagement measure.

**The patent.** In 2017 Activision Publishing was granted US patent 9,789,406, "System and method for driving microtransactions in multiplayer video games". Its description includes matchmaking that pairs players to encourage purchases. One example is matching a newer player with a "marquee" player who uses an item the newer player does not own. Another is placing a buyer in matches where a newly purchased item performs well. When the patent drew public attention, Activision said publicly that the patent had not been implemented in its games (verify current statements before citing).

**Why it is contested.**

- **Agency and fairness.** Players believe matches reflect skill. Optimising for a hidden objective (retention or spend) changes the meaning of winning.
- **Manufactured streaks.** Engagement models can learn that controlled loss-then-win patterns retain players, so outcomes feel orchestrated.
- **Monetization coupling.** Once the objective includes purchases, matchmaking becomes a sales funnel. That violates red lines 1–2 (§6).
- **Persistent suspicion.** Communities in shooters and sports titles regularly accuse games of secret "scripting" or skill-based matchmaking tuned for engagement. Publishers have had to issue public denials. Suspicion alone damages trust, which is why disclosure matters.

**Studio position.**

1. Matchmaking optimises parity, queue time, connection and party fairness. Retention may be a **guardrail metric**, never the objective function.
2. Never use spend or monetization signals in matchmaking.
3. Publish the matchmaking principles in help text: what is considered (skill, latency, party) and what is not (spending).
4. Engagement modelling is allowed for **content and support** decisions (gift a booster, suggest an easier mode, send a helpful tip), within the rules in §6.

## 9. Implementation, telemetry and QA

**Event.** `dda_adjust` {`level_id`, `attempt_index`, `trigger` (e.g. `loss_streak_2`), `lever` (e.g. `moves`), `delta`, `assist_level`, `cap`, `seed`}. Also add `assist_level` as a parameter on `level_start`, `level_complete` and `level_fail`, so win rates can be split by assist (`player-analytics`, `event_taxonomy.py`).

**Remote config keys (example):** `dda.enabled`, `dda.trigger_losses`, `dda.step`, `dda.max_assist`, `dda.exclude_first_attempt_hard`, `dda.daily_cap`. Defaults in code; changes only through A/B-tested rollouts.

**Unit tests (gate `unit`):**

- The assist never exceeds the cap across 10,000 random fail/win sequences.
- The assist is zero on the first attempt of labelled hard levels.
- The assist function has no input from wallet, purchase history or payer flags. Enforce this structurally: the function signature does not receive them.
- The same seed and assist level reproduce the same board or spawn sequence.

**Simulation (gate `playthrough` support):** run bots with DDA on and off over the level set. Compare win-rate distributions, attempts p90 and assisted-clear share. Then run `balance_math.py dda-sim` per hard level to sanity-check parameters.

## 10. Worked examples

### 10.1 Match-3 hard level: bounded streak assist

**Setup.** A hard level at median FAWR 0.40. Skill spread s ~ N(0, 1) logit. Assist: +0.3 logit after every 2 consecutive losses, capped at +0.9 (implemented as +1 move per step, bot-calibrated). Up to 30 attempts.

```
python3 ${CLAUDE_PLUGIN_ROOT}/skills/progression-difficulty/scripts/balance_math.py dda-sim \
    --base 0.40 --trigger 2 --step 0.3 --max-assist 0.9 --players 4000
```

| Metric | No DDA | DDA |
|---|---|---|
| First-attempt win rate | 0.411 | 0.411 (unchanged) |
| Clear rate within 30 attempts | 0.993 | 1.000 |
| Mean attempts among clears | 3.19 | 2.76 |
| p90 attempts | 7 | 6 |
| p95 longest losing streak | 10 | 7 |
| Share of clears that were assisted | — | 0.375 |

The cap lifts a median player from 0.40 to about 0.62, never to "free win" territory. With a churn proxy (`--quit-after-loss 0.12`, a 12% chance of quitting after any loss), the clear rate rises from 0.81 to 0.83 and the quit rate falls from 0.19 to 0.17. The effect is modest and bounded, which is what a safety net should be. **Decision:** ship behind remote config with a 10% holdout. Guardrail: first-attempt win share and booster purchase rate.

### 10.2 Runner: adaptive obstacle density

**Setup.** Endless runner; obstacle density rises with distance. Stress signal: near-misses and hits in the last 20 s.

- BUILD: density +6% per 10 s; PEAK: hold 20 s; RELAX: 10 s at 60% density with a coin trail.
- After a hit that leaves one life: force RELAX for 8 s (mercy window).
- Bounds: density never below the distance-based floor (score integrity), and never adjusted in leaderboard or event modes.
- Disclosure: none needed for pacing (rung 1). Leaderboard modes use the fixed curve, stated in the mode description.

### 10.3 Kart racer: pack rubber banding

- AI speed multiplier m = 1 − 0.06·clamp(gap/150 m, −1, 1), so at most ±6%, smoothed over 2 s.
- Disabled for the final 15% of the last lap. Disabled in time trial and ranked.
- Catch-up items by position, visible in the item roulette.
- Test: a bot driving at the 25th-percentile human line finishes in the top half 30–50% of the time (design target); an expert line wins at least 85% of races (mastery preserved).

### 10.4 PvP card battler: new-player protection

- First 10 matches: separate pool. If the queue is above 20 s, fill with labelled practice bots ("Training match").
- Casual queue: after 3 consecutive losses, widen the search toward lower ratings for the next 2 matches (rung 2, documented in help).
- Ranked: pure rating plus latency; no bots; no loss-streak adjustment.
- Help text: "Matchmaking considers your rating, connection and party, never your purchases."

## 11. DDA checklist

- [ ] Every adaptive system is listed in `contract.progression.difficulty.dda` with trigger, adjustment, bounds and transparency rung.
- [ ] The controller spec covers target, signal, estimator, actuator, bounds, cadence and logging.
- [ ] Caps are small enough to preserve mastery (assisted clears are a minority; the first-attempt win rate is unchanged).
- [ ] Sandbagging countermeasures and a detection metric exist.
- [ ] No input from spend, wallet, payer status or purchase propensity, enforced structurally and by unit test.
- [ ] No hidden DDA or undisclosed bots in ranked or competitive modes.
- [ ] DDA state is part of the seeded simulation input; `dda_adjust` events are logged.
- [ ] Simulated with `balance_math.py dda-sim` and bots before any live test; A/B with holdout and guardrails.
- [ ] Passes the config-reading test; reviewed by `critic` and `compliance-officer`.

## 12. Volatile facts (as of Oct 2026 — verify before relying)

| Fact | Source |
|---|---|
| US 9,789,406 B2, "System and method for driving microtransactions in multiplayer video games", assignee Activision Publishing Inc., granted 17 Oct 2017. Its description covers matchmaking that steers purchases (for example, pairing newer players with "marquee" players who use items they lack, or placing buyers in matches where a new item performs well). | Google Patents — https://patents.google.com/patent/US9789406B2/en |

Company statements about whether the patent was ever implemented were reported in contemporary press. Re-check current coverage before quoting any statement.

**Stable references (cite by author, title and year):** Hunicke, "The Case for Dynamic Difficulty Adjustment in Games", ACE 2005. Booth, "The AI Systems of Left 4 Dead", AIIDE 2009. Chen, Xue, Kolen, Aghdaie, Zaman, Sun and Seif El-Nasr, "EOMM: An Engagement Optimized Matchmaking Framework", WWW 2017. Elo, *The Rating of Chessplayers, Past and Present*, 1978. Glickman's Glicko and Glicko-2 rating systems. Herbrich, Minka and Graepel, "TrueSkill: A Bayesian Skill Rating System", NIPS 2006. Chen (Jenova), *Flow in Games*, MFA thesis, 2006.
