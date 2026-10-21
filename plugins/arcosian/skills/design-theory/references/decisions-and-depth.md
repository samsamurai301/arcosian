# Decisions, Depth and Strategic Structure

The mathematics and craft of making choices worth making. This file covers what makes a decision meaningful, trade-off and risk/reward design (with expected value and variance), how to find dominant strategies before players do, the game theory a designer actually needs (payoff matrices, intransitivity, Nash equilibria, social dilemmas), depth versus complexity and how to estimate depth, emergence and systemic interaction matrices, orthogonal unit differentiation, counterplay, skill versus luck (input versus output randomness, pseudo-random distribution, best-of-N maths), information structures and asymmetry. Every section ends in a procedure or worked example. A companion calculator, `scripts/decision_math.py`, checks payoff matrices for dominance and equilibria, computes pseudo-random distribution constants, Elo win odds and series odds, and expected value and variance of risky options.

## Contents

1. Anatomy of a meaningful decision
2. Trade-off design
3. Risk and reward: expected value, variance, loss aversion
4. Dominant strategies and how to detect them
5. Game theory for designers
6. Intransitivity and weighted rock–paper–scissors (worked)
7. Depth vs complexity, and how to estimate depth
8. Emergence and systemic design
9. Orthogonal unit differentiation
10. Counterplay
11. Skill vs luck
12. Information structures
13. Asymmetry
14. Worked example: auditing a roguelite skill-card pool
15. Procedure: decision audit for a feature or a whole game
16. Calculator reference: `scripts/decision_math.py`

---

## 1. Anatomy of a meaningful decision

A decision has four parts: **options**, the **values** each option affects, the **information** the player has, and the **consequences** that follow. A decision fails when any part is broken:

| Failure | What it looks like | Diagnosis | Fix |
|---|---|---|---|
| Obvious | One option is always best | Pick rate of one option ≫ others; experts and novices pick the same | Add a cost to the best option, or a situation where another wins |
| Blind | Player cannot reason about outcomes | Choices look random in telemetry; players cannot explain picks | Reveal more information (numbers, previews, telegraphs) |
| Random | Outcome barely depends on the choice | Win rate flat across options | Increase the effect size of the choice relative to noise |
| Irrelevant | Consequence is too small or too short-lived | No downstream difference in outcomes | Make the effect persist or compound |
| Overloaded | Too many options or values to compare | Long hesitation, decision fatigue, abandonment | Fewer options (2–4 is the mobile sweet spot), fewer value axes |

**Decision density.** Count meaningful decisions per minute in the core loop. Fast action games may have dozens of micro-decisions (where to move) and one macro-decision per minute (which upgrade). Puzzle games may have one deep decision every 5–20 seconds. Commute-friendly mobile designs usually cap *heavy* decisions to a few per minute and fill the rest with light, intuitive ones.

**Choice count rule of thumb.** On phones, offer 2–4 options per decision; 3 is the most common because it fits one row of thumb-sized cards and produces a "two reasonable, one tempting" pattern. More than 4 options needs grouping, filtering or progressive reveal.

---

## 2. Trade-off design

A trade-off exists when gaining on one value costs another. Give every option at least one **strength** and one **weakness** on axes the player cares about.

**Common trade-off axes.**

| Axis | Option A | Option B | Mobile example |
|---|---|---|---|
| Power vs cost | Strong, expensive | Weak, cheap | Unit elixir costs in arena battlers |
| Speed vs safety | Fast route, more danger | Slow route, safe | Runner lanes with coins near obstacles |
| Now vs later | Immediate reward | Investment that pays later | Spend gold on a potion or on an upgrade |
| Breadth vs depth | Flexible generalist | Specialist that excels in one situation | Hero roles in squad RPGs |
| Certainty vs upside | Guaranteed small gain | Chance of large gain | Cash-out vs push-your-luck |
| Self vs team | Personal progress | Guild contribution | Donate troops vs keep them |
| Offense vs defense | Kill faster | Survive longer | Damage vs HP upgrade cards |
| Information vs action | Scout / reveal | Act now | Spend a turn peeking at hidden tiles |

**Trade-off triangle procedure.** For a set of three options, draw a triangle with three value axes (e.g., damage, survivability, utility). Each option should be strongest on one axis, middling on one and weakest on one. Check:
1. No option is ≥ another on all three axes (that would be dominance, section 4).
2. The situations where each option wins appear often enough in play (if "utility" matters only in 2% of fights, that option is a trap).
3. Costs are visible at decision time.

**Cost-curve check (numerate version).** Assign every stat a value weight from simulation or from a baseline (e.g., 1 damage = 1 point, 1 HP = 0.25 point, 10% speed = 3 points). Sum each option's value and plot against its cost. Options above the line are overpowered, below are underpowered. Then *deliberately* place a few options off the line where they pay for situational weakness (a unit that cannot hit air gets a discount).

---

## 3. Risk and reward

### 3.1 Expected value and variance

For an option with outcomes *x_i* at probabilities *p_i*:

```
EV       = Σ p_i · x_i
Variance = Σ p_i · (x_i − EV)²
SD       = √Variance
```

**Worked example.** Safe option: +10 guaranteed. Risky option: 60% chance of +25, 40% chance of −5.
- EV(risky) = 0.6·25 + 0.4·(−5) = 15 − 2 = **13** (beats safe by 3).
- Variance = 0.6·(25−13)² + 0.4·(−5−13)² = 0.6·144 + 0.4·324 = 86.4 + 129.6 = **216**; SD ≈ **14.7**.
- `python3 ${CLAUDE_PLUGIN_ROOT}/skills/design-theory/scripts/decision_math.py ev --outcomes "0.6:25,0.4:-5"`

Design reading: an EV edge of 3 with SD ~15 makes the choice genuinely interesting — risk-averse players take the safe option, risk-seekers gamble, and neither is clearly wrong over a single decision. If the EV gap were 20, everyone would gamble; if the risky EV were below the safe one, only thrill-seekers would gamble (fine if that is the intent).

### 3.2 Players do not maximise EV

- **Loss aversion**: losses weigh more than equal gains — prospect theory (Kahneman & Tversky, 1979; Tversky & Kahneman, 1992) estimated losses at roughly twice the weight of gains. A "lose 10 or gain 10" coin flip feels bad. To make a gamble feel fair, the upside usually needs to be noticeably larger than the downside.
- **Small probabilities are overweighted** at the point of choice (the long-shot appeal), which is why rare-reward chances feel bigger than they are. Ethical design discloses real odds (see `legal-ethics`, `monetization`).
- **Framing**: "keep 70%" and "lose 30%" are the same, but feel different. Frame risks honestly.
- **Session context**: on a phone with one minute left, players prefer short, low-variance options; high-variance gambles fit sessions where a loss can be recovered.

### 3.3 The doubling-cube decision (worked)

Backgammon's doubling cube is a classic risk/reward mechanic: a player may offer to double the stakes; the opponent must accept (play on for double) or decline (lose the current stake). Ignoring the extra subtleties of real backgammon (gammons, cube ownership), the opponent with win probability *p* compares:
- Decline: −1.
- Accept: EV = 2·p − 2·(1−p) = 2(2p − 1).
Accept when 2(2p − 1) ≥ −1 → **p ≥ 0.25**.

Design lessons: (1) a stakes-raise forces a decision from *both* players; (2) declining (retreating) converts a likely loss into a smaller loss, which turns defeat into a skilful choice; (3) bluffing emerges when one side cannot see the other's position. Marvel Snap's "Snap" and retreat options apply a similar stakes-raise-or-retreat structure to mobile card play.

### 3.4 Risk ladders and push-your-luck

Push-your-luck loops (continue for more reward with rising bust chance, or cash out) are powerful but sit next to gambling mechanics. Design rules:
- Show the current bust probability or at least its trend.
- Bank partial progress at milestones so a bust never wipes a whole session.
- Keep real money out of the loop entirely; no paid "insurance" against busting at the moment of tension.

---

## 4. Dominant strategies and how to detect them

**Definitions.**
- **Strictly dominant**: an option better than every alternative in every situation.
- **Weakly dominant**: never worse, sometimes better.
- **Degenerate strategy**: a strategy that wins but makes the game boring or unintended (infinite stalling, exploit loops, "turtle forever").
- **Dominated option ("trap")**: an option worse than another in every situation; players who pick it are punished for not knowing.

### 4.1 Detection methods (use several)

| Method | When available | How | Signal |
|---|---|---|---|
| Payoff-matrix dominance | Design time; any discrete choice set | Fill outcomes for each option vs each situation/opponent option; check row dominance | A row ≥ another row everywhere |
| Cost-curve/Pareto check | Design time; stat-based options | Plot value vs cost; find options that beat others on every stat for ≤ cost | Pareto-dominated options |
| Simulation sweep | Prototype; with bots | Run bots forced to each strategy against a field; compare win rates | One strategy > others by a large margin across fields |
| Self-play search | Prototype; deterministic sim | Let a search/learning agent find strategies; inspect what it converges to | Agent converges to a single narrow strategy |
| Telemetry: pick and win rates | Live/soft launch | For each option: offered count, pick rate when offered, win rate when picked | High pick rate *and* high win-rate delta |
| Expert interviews | Any | Ask top players what they always/never do | "Always" and "never" lists are dominance candidates |

Run the matrix check: `python3 ${CLAUDE_PLUGIN_ROOT}/skills/design-theory/scripts/decision_math.py matrix --payoff "3,2,4;1,1,2;2,3,1" --labels Sword,Shield,Bow --col-labels Melee,Ranged,Swarm --situations --col-weights 0.5,0.3,0.2 --fail-on-dominated` (here Sword strictly dominates Shield, so the command exits 1 — usable as a balance CI step; `--col-weights` also reports each option's expected payoff for the given mix of situations).

### 4.2 Fixes for dominance, from mildest to strongest

1. **Situational counters**: add situations or opponents where the dominant option is weak.
2. **Cost adjustment**: raise its cost (resources, cooldown, opportunity cost).
3. **Diminishing returns**: stacking the dominant option yields less each time (stopping mechanism).
4. **Mutual exclusivity**: picking it locks out another strong option.
5. **Rework**: change what the option *does* (orthogonal differentiation, section 9) rather than its numbers.
6. **Remove it.**

Avoid fixing a dominant option only by nerfing numbers until it is dominated by something else — that just moves the problem. Re-run detection after each change.

---

## 5. Game theory for designers

### 5.1 Payoff matrices

A payoff matrix lists outcomes for each combination of choices. In two-player **zero-sum** games, one player's gain is the other's loss, so one number per cell suffices (the row player's payoff). In **non-zero-sum** games, each cell has a pair (row payoff, column payoff).

### 5.2 Nash equilibrium

A set of strategies where no player can do better by changing only their own strategy. Equilibria can be:
- **Pure**: each player picks one option (e.g., both always cooperate).
- **Mixed**: players randomise in specific proportions (rock–paper–scissors: one-third each).

Why designers care: in a competitive game, the equilibrium predicts what a well-informed metagame converges toward. If the equilibrium uses only 2 of your 10 options, 8 options are dead in high-level play. If the equilibrium is mixed across many options, the meta is diverse.

### 5.3 Social dilemmas in co-op and guild design

The **prisoner's dilemma** structure appears whenever individual and group incentives diverge.

| | Teammate contributes | Teammate free-rides |
|---|---|---|
| **I contribute** | 3 / 3 | 0 / 5 |
| **I free-ride** | 5 / 0 | 1 / 1 |

Free-riding dominates individually (5 > 3 and 1 > 0), yet both free-riding (1/1) is worse for everyone than both contributing (3/3). Guild chests, team events and co-op bosses have this shape by default. Design fixes:
- **Personal milestones**: contributors earn individual rewards scaled by contribution, so contributing beats free-riding personally.
- **Threshold rewards with visibility**: show each member's contribution; social accountability changes payoffs.
- **Minimum participation** to receive the team reward.
- **Repeated play**: teams persist across events, so reputation matters (cooperation is sustainable in repeated games).

Check with the calculator: `decision_math.py matrix --payoff "3/3,0/5;5/0,1/1" --labels Contribute,FreeRide` reports the dominant strategy and the (inefficient) pure equilibrium.

### 5.4 Other useful structures

| Structure | Shape | Where it appears | Design use |
|---|---|---|---|
| Chicken / hawk–dove | Mutual aggression is worst; yielding is safe but loses face | Contested resource tiles, alliance standoffs | Creates brinkmanship; needs reputation signals |
| Stag hunt | Cooperating pays most but only if both commit | Co-op raids that fail if one player leaves | Trust signals, commitment mechanics (lock-in) |
| Coordination | Matching choices pays | Team role selection | Provide communication (pings, role picks) |
| Matching pennies / mind games | One wants to match, other to mismatch | Penalty-kick style guessing | Pure yomi; needs readable tells to avoid pure randomness |

---

## 6. Intransitivity and weighted rock–paper–scissors (worked)

**Intransitive** relationships (A beats B, B beats C, C beats A) prevent any single best option and are the backbone of unit-counter systems. Ian Schreiber's *Game Balance Concepts* course (2010) and *Game Balance* (Schreiber & Romero, 2021) treat this in depth.

**Equal-weight RPS** has a mixed equilibrium of one-third each. Real games rarely have equal weights: winning with one option may be more decisive than with another.

**Worked example (lane battler).** Three unit types: Tank, Mage, Assassin. Tank beats Assassin by a payoff of *a*, Assassin beats Mage by *b*, Mage beats Tank by *c* (row player's payoff; ties 0; zero-sum).

```
            Tank    Mage    Assassin
Tank          0      −c        +a
Mage         +c       0        −b
Assassin     −a      +b         0
```

Solving for the mix (t, m, s) that leaves the opponent indifferent gives:

```
c·m = a·s,   b·s = c·t,   a·t = b·m   →   t : m : s = b : a : c
```

Each option's equilibrium share is proportional to the payoff of the matchup **it is not part of**.

With a = 1, b = 2, c = 3: t : m : s = 2 : 1 : 3 → **Tank 33%, Mage 17%, Assassin 50%**.

Check: `python3 ${CLAUDE_PLUGIN_ROOT}/skills/design-theory/scripts/decision_math.py matrix --payoff "0,-3,1;3,0,-2;-1,2,0" --labels Tank,Mage,Assassin` reports a mixed strategy close to 0.333 / 0.167 / 0.500.

**Design lessons.**
1. **Buffing an option's win does not raise its own share — it raises the share of its counter.** Buff Mage's win over Tank (*c* ↑) and the equilibrium shifts toward Assassin (which beats Mage). Expect players to respond to buffs by playing the counter.
2. To raise an option's popularity, increase the payoff of the matchup it is not in, or reduce the payoff of the option that beats it.
3. Real metagames lag the equilibrium; early after a patch players overplay the buffed option, then the counter rises. Read telemetry over weeks, not days.
4. Pure RPS is shallow (pure guessing). Add **partial information** (scouting, telegraphs), **soft counters** (advantage, not auto-win), and **costs** so that skill matters alongside the counter wheel.

---

## 7. Depth vs complexity, and how to estimate depth

**Complexity** is what the player must learn (rules, exceptions, UI concepts). **Depth** is how much meaningful skill and strategy the system supports before it is exhausted. **Elegance** (Sylvester; see `foundational-frameworks.md`) is high depth per unit of complexity.

### 7.1 Proxies for depth

| Proxy | How to measure | Reading |
|---|---|---|
| Skill gap | Win rate of a strong bot vs a random bot over N games | Near 50% → luck-dominated or shallow; near 100% → skill matters |
| Skill ladder length | Rating spread between top and bottom players / bots, converted to "tiers" where each tier beats the one below ~75% of the time (~191 Elo points) | More tiers → deeper (at the population level) |
| Viable strategy count | Number of strategies within a few win-rate points of the best | 1 → solved; many → rich |
| Mastery horizon | Sessions until learning curves flatten (score, time, win rate) | Short → shallow for that audience |
| Expert novelty | Do experts still discover new tactics after months? | Community-discovered tech is a depth signal |

Elo conversions (logistic, 400-point scale): P(win) = 1 / (1 + 10^(−Δ/400)). Δ = 100 → 64%; Δ = 191 → 75%; Δ = 200 → 76%; Δ = 400 → 91%. Use `decision_math.py elo --diff 200` or `elo --p 0.75`.

### 7.2 Complexity budget

Give every concept a cost (1 = intuitive/familiar, 3 = needs a tutorial step, 5 = needs repeated teaching). Typical mobile casual games keep the *first-session* budget small (a handful of points) and add one concept at a time; midcore games can afford more but must stage it. Track the budget in the FTUE plan (`contract.ftue.steps[].teaches`).

### 7.3 Heuristics for depth without complexity

- **Interactions over additions**: a new element that interacts with 4 existing ones adds more depth than 4 isolated elements.
- **Positional and temporal play**: where and when you do something (lanes, timing windows) adds depth with no new rules.
- **Resource tension**: one shared resource for many uses (elixir, action points, a single currency for moves and boosts) creates decisions automatically.
- **Hidden-but-learnable information**: patterns players can learn to read (enemy tells, refill tendencies) reward expertise.
- **Opponent modelling (yomi)**: in PvP, predicting the opponent creates depth on top of the rules (David Sirlin, *Playing to Win*, and his articles on "yomi"; publication years were not checked).

---

## 8. Emergence and systemic design

**Emergence**: behaviour arising from interactions of simple rules that the designer did not script one by one (Juul's games of emergence; see `foundational-frameworks.md`). Systemic games build emergence on purpose: objects have properties, verbs act on properties, and rules are applied consistently. Nintendo's talk on Breath of the Wild (GDC 2017) described its "chemistry engine" in these terms: elements and materials reacting by consistent rules.

### 8.1 Interaction matrix procedure

1. List elements (materials, units, tiles, status effects) as rows and columns.
2. Fill each cell with the interaction (or "none").
3. Compute **interaction density** = meaningful pairs / total pairs. Low density (< ~20%) suggests a list of features rather than a system; very high density can confuse players unless rules are consistent and readable.
4. Mark interactions the player can **discover by intuition** (fire burns wood) vs **must be taught** (ice + electricity = shatter); keep the second group small.

| | Fire | Water | Ice | Wind | Oil |
|---|---|---|---|---|---|
| **Fire** | spreads | extinguished → steam | melts → water | fanned → spreads | ignites → explosion |
| **Water** | — | pools | freezes → ice | pushes | floats oil |
| **Ice** | — | — | slides | none | slippery |
| **Wind** | — | — | — | gusts | spreads slick |
| **Oil** | — | — | — | — | slick |

Diagonal cells are single-element properties; the density count uses pairs of different elements. Here 9 of the 10 pairs interact meaningfully (90% density), and most interactions are intuitive from real-world experience, which is why elemental systems are popular in puzzle and tactics games: high depth at low teaching cost.

### 8.2 Emergence risks
- Unintended dominant combos (infinite loops, unkillable stacks) — search for them with bots and stress tests.
- Unreadable outcomes ("what just happened?") — add clear feedback per interaction (`game-feel`).
- Content cost moves from levels to testing — budget QA time (`qa-testing`).

---

## 9. Orthogonal unit differentiation

The principle of **orthogonal unit differentiation** (a term used in strategy-game design writing and catalogued as a game-design pattern: units described by actions, abilities and characteristics that are orthogonal in functionality, qualitatively and not only quantitatively different; examples given are Age of Empires and Chess) argues that options should differ in *kind*, not just in *amount*. The term is sometimes attributed to David Sirlin, but no source was found for that; one blog credits Will Wright's SimCity-era design instead (single-source and unverified), so treat the origin as unattributed ([pattern description](https://math.vu.nl/~eliens/demo/pattern-orthogonalunitdifferentiation.html)). Sirlin is cited elsewhere in this file for yomi, not for this term. If every unit is a point on the same few stat axes (damage, HP, speed), players compare numbers and the best ratio wins. If units do qualitatively different things — fly over walls, deal area damage, stun, heal, teleport, reveal hidden units — they create different situations, combinations and counters.

**Test: the stat-sheet collapse.** Write each option as a stat vector. If you can rank options by a single weighted sum without losing any important information, they are not orthogonal.

| Unit | Stat-only version | Orthogonal version |
|---|---|---|
| Knight | 100 HP, 10 dmg | Blocks a lane; pushes enemies back |
| Archer | 60 HP, 14 dmg | Hits air and over walls; fragile up close |
| Bomber | 50 HP, 20 dmg | Splash damage; ineffective vs single big targets |
| Priest | 70 HP, 6 dmg | Heals; no damage to buildings |

The stat-only roster collapses to "dmg per HP per cost"; the orthogonal roster creates contexts (air threats, swarms, sieges) where each matters.

**Mobile application.** Small screens limit how many units can be on the field and how much text players read, so each unit's distinct role must read at a glance: silhouette, colour and an icon for the special property (`art-direction`, `mobile-ux`).

---

## 10. Counterplay

**Counterplay** is the ability of a player to respond to what the opponent (or the game) is doing. Without it, play becomes a race of who-does-their-thing-first.

**Counterplay checklist for every strong option.**
- Is there at least one **hard counter** (directly answers it) and two or more **soft counters** (make it less effective)?
- Is it **telegraphed** — can the opponent see it coming in time to respond (wind-up, visible resource, cooldown indicator)?
- Is the **response window** longer than human reaction time plus touch-input and display latency? On phones, err generous: frame-perfect responses are not counterplay.
- Is there **recovery** after being countered (not instantly decisive)?
- Can the counter itself be **countered** (layers of yomi), or does the exchange end in a dead state?

**PvE counterplay.** Bosses and enemies follow the same rules: telegraph attacks, offer dodge/block windows, and make each enemy type ask a different question of the player (orthogonal enemy design).

**Mobile note.** In asynchronous PvP (attacking a stored base), counterplay happens at design time (base layout) rather than live; give defenders meaningful layout choices and show replays so they can adapt.

---

## 11. Skill vs luck

### 11.1 Input vs output randomness

A distinction widely used in tabletop and digital design writing (see, e.g., Engelstein & Shalev, *Building Blocks of Tabletop Game Design*, 2019):
- **Input randomness** happens *before* the decision: the card draw, the generated map, the tile refill. The player then reacts. It creates variety and rewards adaptation.
- **Output randomness** happens *after* the decision: the attack roll, the critical-hit chance. It can override good decisions and feel unfair when stakes are high.

| Use | Prefer | Example |
|---|---|---|
| Variety without unfairness | Input | Random board refill in match-3; random upgrade offers |
| Tension and spectacle | Output (bounded) | Critical hits, small damage variance (±10%) |
| Upsets that let weaker players win sometimes | Some output | Comeback chances in casual PvP |
| Competitive integrity | Mostly input, minimal output | Ranked modes |

### 11.2 Measuring the luck share

1. **Strong-vs-weak bot test.** Run a strong heuristic bot vs a random bot for 1,000+ games. Interpretation (heuristic): ≥ 90% strong wins → skill-dominant; 65–90% → mixed; < 65% → luck-dominant.
2. **Best-of-N test.** If the better player wins a single game with probability *p*, how long a series does it take to be confident?

| Single-game p | Bo1 | Bo3 | Bo5 | Bo7 | Bo11 | Bo21 |
|---|---|---|---|---|---|---|
| 0.55 | 0.55 | 0.575 | 0.593 | 0.608 | 0.633 | 0.679 |
| 0.60 | 0.60 | 0.648 | 0.683 | 0.710 | 0.753 | 0.826 |
| 0.65 | 0.65 | 0.718 | 0.765 | 0.800 | 0.851 | 0.923 |
| 0.75 | 0.75 | 0.844 | 0.896 | 0.929 | 0.966 | 0.994 |

(Computed with `decision_math.py elo --p 0.6 --best-of 7`.) Reading: when the better player only wins 55% of single games, even 21 games do not reliably identify them — ranked ladders need many games, and individual losses will feel random. That can be a feature for broad casual audiences and a bug for competitive ones.

3. **Variance decomposition (live).** Compare outcome variance among players of similar rating with variance across ratings; a high within-rating share means luck dominates.

### 11.3 Taming output randomness

- **Shrink variance**: narrower damage ranges, more rolls of smaller impact (law of large numbers within a match).
- **Pseudo-random distribution (PRD)**: instead of a flat chance *p* per attempt, the chance starts at a constant *C* and rises by *C* after each failure, resetting on success; *C* is chosen so the long-run rate equals *p*. Warcraft III and Dota 2 are well-known users. Streaks of failures and successes become rarer. Constants (computed): p = 10% → C ≈ 1.475%; 20% → 5.570%; **25% → 8.474%**; 30% → 11.895%; 50% → 30.21%. Use `decision_math.py prd --p 0.25`.
- **Bad-luck protection / pity**: guarantee after N failures (common in loot and gacha systems; see `monetization` and `${CLAUDE_PLUGIN_ROOT}/scripts/gacha_calc.py`).
- **Show the odds** and recent history, so players attribute outcomes correctly.
- **Never pair high output randomness with high stakes and real money.**

---

## 12. Information structures

| Structure | Definition | Effect on play | Mobile examples |
|---|---|---|---|
| Perfect information | All state visible to all players | Pure calculation and planning; deep but can be slow and "solvable" | Abstract puzzle games; tactics games that show all enemy intents (Into the Breach-style) |
| Imperfect / hidden information | Some state hidden (hands, fog) | Inference, bluffing, scouting | Card battlers; social deduction (Among Us) |
| Stochastic information | Future state determined by chance | Planning under uncertainty | Tile refills, draws |
| Simultaneous moves | Players commit without seeing others' choices | Prediction and mind games | Simultaneous card reveals in Marvel Snap-style games |
| Sequential, revealed | Moves visible as they happen | Reaction and counterplay | Turn-based PvP |
| Telegraphed intent | Opponent's next action shown in advance | Turns combat into puzzle solving; reduces frustration | Enemy intent icons in deck-builders (Slay the Spire-style) |

**Design rules.**
- **Bluffing requires** hidden information *plus* stakes *plus* a way to signal; remove any one and bluffing disappears.
- **Information as a resource**: let players spend something to gain information (scouting, peeking), creating a trade-off between information and action.
- **Too much hidden information** feels random; **too little** feels solved. Tune by revealing enough for informed decisions and hiding enough to keep prediction alive.
- On mobile, information must fit a small screen: prefer icons and previews over numbers in text; show intent near the actor.

---

## 13. Asymmetry

| Type | Description | Balancing approach | Examples |
|---|---|---|---|
| Symmetric (mirror) | Same options for all players | Balance by first-player advantage only | Classic board games; mirror-match puzzle duels |
| Asymmetric start | Same rules, different starting resources | Handicap/compensation tuned by win rate | Handicap stones in Go; catch-up bonuses |
| Asymmetric factions | Different unit sets, same goals | Per-faction win rates in matched rating bands; orthogonal differences | Faction-based strategy games |
| Asymmetric roles | Different goals and abilities in the same match | Per-role win rates; adjust role counts and tools | 1v4 hunter games; Among Us impostors vs crew |
| Asymmetric information | Some players know more | Tune information reveals; give the uninformed side tools to deduce | Social deduction |
| Asymmetric time/effort | Attacker plays live; defender designed earlier | Defence tools, replays, protection timers | Asynchronous base raids |

**Balancing target.** For asymmetric factions or roles, a common practitioner target is per-side win rates within a few percentage points of 50% *within each rating band*, not just overall. Measure with `ab_test.py analyze` on per-side wins to check whether the difference is statistically meaningful before patching (`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ab_test.py analyze --a-success 5300 --a-n 10000 --b-success 4700 --b-n 10000`).

**First-player advantage** is a special asymmetry in turn-based games. Compensations include giving the second player extra resources, letting the second player choose sides, or simultaneous turns.

---

## 14. Worked example: auditing a roguelite skill-card pool

Context: a one-thumb survivor-like offers 3 random skill cards on each level-up from a pool of 24. Soft-launch telemetry (illustrative numbers, not real data):

| Card | Offered | Pick rate when offered | Run win rate when picked | Win rate when offered but not picked |
|---|---|---|---|---|
| Multishot | 41,000 | 78% | 31% | 18% |
| Ricochet | 39,500 | 52% | 22% | 20% |
| HP Up | 40,200 | 21% | 19% | 21% |
| Freeze Aura | 38,800 | 12% | 27% | 20% |
| Coin Magnet | 40,700 | 35% | 14% | 22% |

**Reading.**
1. **Multishot**: very high pick rate *and* large win-rate delta (+13 points) → dominant. Players know it, and it works. Fix: diminishing returns on stacking, or make it compete with a mutually exclusive projectile mod.
2. **Freeze Aura**: low pick rate but strong delta (+7) → underrated "sleeper". Fix the *information*, not the numbers: better icon, preview of the effect, clearer description.
3. **Coin Magnet**: picked a third of the time but *lowers* win rate (−8) → a trap that trades run success for meta currency. Either intended (a "greed" choice — then label it clearly) or a bug in value.
4. **HP Up**: neutral — a safe filler pick, fine.
5. **Ricochet**: healthy.

**Caveat (selection bias).** Players who pick a card may differ from those who do not (skill, build state). Control by comparing within similar player-skill cohorts or run states, or run a randomized test (force-offer subsets).

**Follow-up.** Re-run after the patch; check that removing Multishot's dominance did not just create a new one; the target is several cards within a few points of each other in "win rate when picked".

---

## 15. Procedure: decision audit for a feature or a whole game

1. **List decision points** in the core and meta loops (`core-loops-and-structure.md`), with frequency per session.
2. **Classify** each with Meier's properties (trade-off, situational, style, persistence, information) — see `foundational-frameworks.md` section 16.
3. **Find non-decisions** (obvious, blind, random, irrelevant). Automate them, remove them, or add a competing value.
4. **Build payoff/cost tables** for discrete choice sets; run `decision_math.py matrix --fail-on-dominated`.
5. **Estimate depth**: strong-vs-random bot gap, viable strategy count (use the game's bots: `${CLAUDE_PLUGIN_ROOT}/scripts/match3_sim.py`, `puzzle_solver.py`, or the template's `--mode=bot` runner).
6. **Check luck placement**: is randomness mostly input-side? Is output randomness bounded where stakes are high?
7. **Check information**: can players make informed decisions at each point?
8. **Check counterplay** for every strong option and enemy.
9. **Write findings** into the contract's mechanic `parameters` notes and risks, and hand balance work to `arcosian:systems-designer` via the `balance-pass` workflow.
10. **Set telemetry** for pick rates and win-rate deltas per option (`player-analytics`).

---

## 16. Calculator reference: `scripts/decision_math.py`

Stdlib-only Python 3.9+. All subcommands accept `--json`. Exit codes: 0 ok, 1 check failed (`--fail-on-dominated`), 2 usage error.

| Command | Purpose | Example |
|---|---|---|
| `matrix --payoff "..." [--labels ..] [--col-labels ..] [--col-weights w,w,..] [--situations] [--iters N] [--fail-on-dominated]` | Dominance (strict/weak), iterated elimination, pure Nash equilibria; mixed strategy via fictitious play for zero-sum matrices; closed-form mixed equilibrium for 2×2 bimatrix games. `--situations` treats columns as situations (not an opponent) and skips equilibria; `--col-weights` adds expected payoff per row for given situation frequencies | `matrix --payoff "0,-3,1;3,0,-2;-1,2,0" --labels Tank,Mage,Assassin` |
| `prd --p P` | Pseudo-random distribution constant C for nominal chance P, plus expected attempts and max streak | `prd --p 0.25` |
| `elo --diff D` / `elo --p P [--best-of N]` | Win probability from rating difference, rating difference from probability, series win odds | `elo --p 0.6 --best-of 7` |
| `ev --outcomes "p:x,p:x,..."` | Expected value, variance, SD, probability of a negative outcome | `ev --outcomes "0.6:25,0.4:-5"` |
| `--selftest` | Runs built-in fixtures (weighted RPS, prisoner's dilemma, PRD 25%, Elo, EV) | `decision_math.py --selftest` |

Payoff syntax: rows separated by `;`, cells by `,`. A plain number means a zero-sum game (row player's payoff; column player gets the negative). `a/b` cells mean a general two-player game (row payoff / column payoff).
