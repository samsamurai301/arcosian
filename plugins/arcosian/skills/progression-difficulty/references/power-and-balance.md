# Power and Balance

Progression gives players power. Balance makes sure that power means something: options stay distinct, nothing dominates, fights last the intended time, and in PvP the better decision wins more often than the bigger wallet. This file covers the power budget (how much of success comes from skill versus power), power curves and how a power ratio maps to win rate, stat scaling and stacking, damage and armour formulas with effective HP, time-to-kill design, PvP balance metrics and process, intransitive (rock-paper-scissors) design including the weighted case, cost curves, Lanchester's laws for unit counts, and a full balancing methodology with spreadsheets and simulations. All calculators referenced are in `scripts/balance_math.py`, plus `skills/design-theory/scripts/decision_math.py` for payoff matrices. Frameworks are summarised from Ian Schreiber and Brenda Romero (*Game Balance*, 2021), Schreiber's online course *Game Balance Concepts* (2010), David Sirlin's writing on competitive balance (*Playing to Win*, 2006, and later essays), and F. W. Lanchester (*Aircraft in Warfare*, 1916).

## Contents

1. The power budget: skill vs power
2. Power curves and the power ratio
3. Stat scaling and stacking
4. Damage and armour formulas
5. Effective HP and investment choices
6. Time-to-kill and encounter design
7. PvP balance
8. Intransitive design
9. Cost curves
10. Lanchester's laws: numbers vs quality
11. Balancing methodology: spreadsheets, sims, telemetry
12. Worked examples
13. Power and balance checklist

---

## 1. The power budget: skill vs power

Use the working model from `references/difficulty-design.md` §3:

```
P(win) = σ(skill + power − difficulty)       # logit units
```

**Power share.** For a given level or match, the power share is the part of the win-probability change that comes from progression rather than play. Measure it with bots. Run the same bot policy with day-1 power and with expected day-N power, and compare win rates. Then run strong and weak bot policies at equal power.

| Measure | How | Healthy range (studio starting targets) |
|---|---|---|
| Meta power uplift | Bot win rate at expected day-7 power − at day-1 power, same level | ≤ +10–15 points on a level designed for day-7 players (consistent with `genre-playbooks`' bounded power bridge) |
| Skill gap | Strong bot − weak bot win rate at equal power | ≥ 25–35 points in skill-led genres; under that, play feels luck- or stat-led |
| Power-to-skill ratio | Meta uplift ÷ skill gap | < 0.5 in skill-led games; RPG and idle genres can go above 1 by design |

**Genre positions.** Puzzle and casual action are skill-led (power is a bridge over walls). Campaign RPGs and gacha are power-led with skill seasoning (team building is the skill). Idle games are almost entirely power-led. PvP card and strategy games need **normalised** modes when power differences are large. Decide the position in the contract (`progression.difficulty.model` notes) before building the upgrade economy.

**Why bound power.** If power dominates, levels are not tested by skill but by the wallet or the calendar, and difficulty tuning collapses into economy tuning. If power is negligible, the meta loop feels pointless. The bounded bridge keeps both loops meaningful.

## 2. Power curves and the power ratio

Define a scalar **power** for the player (P) and for content (E): enemy team, stage, opponent. The **ratio R = P/E** drives outcomes. A convenient form is Bradley–Terry:

```
P(win) = P^β / (P^β + E^β) = σ(β · ln R)
```

β measures how decisive power is. Fit β from simulations, by regressing logit(win rate) on ln R. Values for illustration:

| R = P/E | β = 3 | β = 4 | β = 6 |
|---|---|---|---|
| 0.7 | 0.255 | 0.194 | 0.105 |
| 0.8 | 0.339 | 0.291 | 0.208 |
| 0.9 | 0.422 | 0.396 | 0.347 |
| 1.0 | 0.500 | 0.500 | 0.500 |
| 1.1 | 0.571 | 0.594 | 0.639 |
| 1.2 | 0.633 | 0.675 | 0.749 |
| 1.3 | 0.687 | 0.741 | 0.828 |
| 1.5 | 0.771 | 0.835 | 0.919 |

High β (stat-heavy auto-battles) makes small power deficits decisive. Low β (skill-heavy action) leaves room for play. A **recommended power** label on a stage should correspond to a stated win rate, for example "recommended = the power at which the reference bot wins 90%". At β = 4 that is R ≈ 1.73.

**Designing the content power curve.** Express E(n) as the player's expected power at the moment they reach stage n (from the progression TTL and upgrade economy), times a target ratio:

```
E(n) = P_expected(n) / R_target(n)
R_target follows the difficulty sawtooth: relief stages R ≈ 1.3–1.6, normal 1.1–1.3, walls 0.85–1.0
```

A **wall** (R < 1 for the expected player) asks the player to upgrade, replay for resources, change composition or wait for timers. Walls are legitimate when (a) a free path through them exists within about one daily cycle, (b) the game shows the shortfall ("Your team: 8,400 / recommended 9,000"), and (c) walls are not synchronised with paid offers (`references/dynamic-difficulty.md` §6).

**Displayed power scores.** Many RPGs show a single "combat power" number. It must **predict** outcomes. Validate it by plotting simulated win rate against the displayed power ratio. If two teams with the same displayed power have very different win rates, the score weights are wrong, or the game has synergy and counter effects the score ignores. In that case, say "recommended" rather than promising a win.

## 3. Stat scaling and stacking

### 3.1 Additive vs multiplicative stacking

| Model | Five +10% damage items | Behaviour | Use |
|---|---|---|---|
| Additive | 1 + 5×0.10 = 1.50× | Linear; each item worth less relative to the total | Default for same-type bonuses |
| Multiplicative | 1.10⁵ = 1.61× | Compounding; each item worth the same relative amount | Different sources ("more" vs "increased") |
| Buckets (additive within, multiplicative across) | (1 + Σ bucket A) × (1 + Σ bucket B) × … | Rewards diversifying across buckets | ARPG-style builds |

**Bucket example.** Base 100 damage. Bucket A (increased damage) +20%, +30% and +50% gives ×2.0. Bucket B (separate "more" multipliers) of ×1.2 and ×1.3 gives ×1.56. Total 312 damage. Stacking a fourth bucket-A item adds less than adding a first item to an empty bucket. That pushes build diversity. Document buckets in the stat tooltip, or players will feel cheated by "wasted" stats.

### 3.2 Two-axis growth

If both HP and damage grow 8% per level, then:

- **TTK against equal-level enemies stays constant** (both sides scaled).
- **Combat power vs lower-level content grows about 16.6% per level** (1.08², since outcome strength ∝ DPS × HP; see §10).

Consequence: over-levelled players steamroll old content fast. If that is not desired, scale enemy *both* axes with player level, or cap the effective level (level sync).

### 3.3 Stat budgets per item or level

Give items a **budget** that rises with item level, `budget(ilvl) = a · ilvl^k` (often k ≈ 1, with rarity multipliers), and price each stat in budget points via **stat weights**: the marginal value of one point toward the target outcome (DPS, EHP or TTK). Recompute stat weights whenever formulas change. Hyperbolic stats change value as totals grow (§5).

**Rules.**

- Rarity should buy **more budget or more interesting effects**, but in competitive modes, prefer interesting effects over raw budget.
- Growth per level for primary stats: pick one percentage (for example 5–10%) and hold it constant across classes. Differences between classes come from base values and kits, not growth rates. Diverging growth rates break balance at the cap.
- Keep displayed numbers readable. If numbers exceed about 6–7 digits in a non-idle game, compress them (K/M suffixes, or a level squish in a live game).

## 4. Damage and armour formulas

### 4.1 The standard families

| Family | Formula (damage taken) | Properties | Seen in |
|---|---|---|---|
| Subtractive | `max(atk − def, floor)` | Readable with small numbers; sharp thresholds; armour can nullify weak hits; needs a floor | Classic JRPGs, board-game-like combat |
| Divisive (ratio) | `atk · atk / (atk + def)` | Never zero; depends on the atk:def ratio, so it scales with level automatically | Many mobile RPGs |
| Hyperbolic constant | `atk · k / (k + def)` | Each point of def adds the same effective HP (linear EHP); k is "def for 50% reduction" | *League of Legends* has long used this form for armour, with k = 100 |
| Percentage with cap | `atk · (1 − min(def%, cap))` | Simple; needs a hard cap; stacking cliffs | Resistances in many ARPGs (*Path of Exile* has long used a 75% default resistance cap) |
| Level-normalised | `atk · K(L) / (K(L) + def)`, with K rising with attacker level | The same armour is worth less against higher-level attackers | MMO-style rating systems |
| Composite | Multiple stages: base × skill power × atk/def ratio × modifiers (type, crit, random) | Rich but opaque; needs a tooltip and a damage preview | The Pokémon formula: `((2L/5 + 2)·Power·A/D)/50 + 2`, times modifiers |

### 4.2 Comparison at atk = 100 (k = 100, subtractive floor 10%)

| def | Subtractive | Divisive | Hyperbolic | EHP multiplier (hyperbolic) |
|---|---|---|---|---|
| 0 | 100 | 100 | 100 | 1.00 |
| 25 | 75 | 80 | 80 | 1.25 |
| 50 | 50 | 66.7 | 66.7 | 1.50 |
| 100 | 10 (floor) | 50 | 50 | 2.00 |
| 200 | 10 (floor) | 33.3 | 33.3 | 3.00 |
| 400 | 10 (floor) | 20 | 20 | 5.00 |

`balance_math.py damage --atk 100 --def-values 0,25,50,100,200,400 --k 100 --min-frac 0.1`

Note that at atk = 100, divisive and hyperbolic coincide (k = atk). They diverge as atk grows. Divisive armour weakens against bigger hits; hyperbolic armour does not.

### 4.3 Choosing a formula

| Requirement | Choose |
|---|---|
| Small numbers, readable mental maths (board-game feel) | Subtractive with a floor |
| Long progression with growing numbers; armour should never fully nullify | Divisive or hyperbolic |
| "Each point of armour is worth the same" (clean itemisation) | Hyperbolic constant |
| Big hits should pierce armour (tank vs nuke identity) | Divisive |
| Level differences should matter strongly | Level-normalised hyperbolic |
| Players must preview outcomes on a phone | Any formula, plus a damage preview in the UI |

**Order of operations.** Write it once and keep it fixed: base → flat additions → additive % buckets → multiplicative buckets → crit → mitigation (armour, then resist) → flat reduction → floor and caps → rounding. Put the order in the stat tooltip spec and in unit tests. Penetration: flat penetration (subtract from def before the formula) favours low-def targets; percent penetration favours high-def targets. Choose deliberately, because each one creates different counters.

## 5. Effective HP and investment choices

```
EHP = HP / (1 − damage_reduction)
Hyperbolic armour: damage_reduction = def/(k + def)  →  EHP = HP · (k + def)/k
```

**Marginal values (hyperbolic).** ∂EHP/∂def = HP/k, and ∂EHP/∂HP = (k + def)/k. At equal cost per point, buy armour while **HP > k + def**, otherwise buy HP. Balanced builds sit near HP ≈ k + def.

**Worked check.** HP 1,500, def 200, k = 100: EHP = 4,500. One more armour point adds 15 EHP. One more HP point adds 3 EHP. At equal prices, armour is 5× better, so the build is HP-starved. If an item shop sells both at equal prices, every player will discover this. Either price them by marginal value or accept armour stacking as the dominant strategy, and then counter it with percent penetration.

**Mixed damage types.** If damage splits between physical (armour) and magic (resist), EHP depends on the enemy mix. Compute EHP against the expected mix per content tier, and show players a threat indicator so they can adapt.

## 6. Time-to-kill and encounter design

```
expected hit = dmg · mitigation · (1 + crit_chance · (crit_mult − 1))
DPS = expected hit · hits_per_sec
hits_to_kill = ceil(HP / expected hit)      TTK = hits_to_kill / hits_per_sec
```

**Worked example.** HP 1,200, damage 90, 1.25 hits/s, 20% crit at 2×, mitigation 0.8. Per hit 72, expected 86.4, DPS 108, 14 hits, TTK 11.2 s. With crit variance, hits p10/p50/p90 = 13/14/16, so TTK ranges from 10.4 to 12.8 s.
`balance_math.py ttk --hp 1200 --damage 90 --rate 1.25 --crit-chance 0.2 --crit-mult 2 --mitigation 0.8`

**TTK design targets (studio starting hypotheses for mobile; tune per game):**

| Target | TTK | Why |
|---|---|---|
| Trash mob (survivor-like, runner) | 0.2–1.5 s | Mass clearing is the fantasy; readability over detail |
| Elite | 4–12 s | A short decision window: kite, dodge, focus |
| Boss (casual action) | 30–90 s | Enough phases to tell a story within a 2–5 min session |
| Auto-battler / RPG team fight | 15–45 s | Watchable; shows synergies; respects short sessions |
| PvP duel (real-time action) | 3–10 s | Room for reaction and counterplay on touch input |

**Encounter checks.**

- **TTK vs TTD:** compare time-to-kill the enemy with time-to-die. A player TTD / enemy TTK ratio of about 1.5–3 gives tension without despair on normal content. Below 1 the player cannot win without better play or power.
- **Overkill waste:** if hits_to_kill is often 1 with large overkill, damage upgrades feel useless. Raise HP or add multi-target value.
- **Breakpoints:** players feel the step from 4 hits to 3 hits, not +5% damage. Place upgrades so meaningful breakpoints occur every few upgrades, and show them ("Kills Grunts in 3 hits").

## 7. PvP balance

### 7.1 Goals

1. **Fairness:** outcomes depend on decisions and execution, not on spending or luck beyond the disclosed amount.
2. **Diversity:** many viable options at every skill level.
3. **Counterplay:** every strong option has an answer the opponent can execute.
4. **Legibility:** players can understand why they lost.

### 7.2 Metrics

| Metric | Definition | Flag (studio heuristics; need adequate samples) |
|---|---|---|
| Win rate | Wins ÷ games, per option (hero, card, deck archetype) | Outside about 45–55% overall; outside about 47–53% at top skill |
| Pick rate | Share of games where the option is chosen | Very high pick plus a positive win rate = dominant; very low pick = dead |
| Ban rate (if bans exist) | Share of drafts banning the option | Persistently high = frustrating, even if win rate is fine |
| Win rate by skill bracket | Win rate split by rating band | A large slope means the option is noob-stomping or skill-gated; tune separately |
| Matchup matrix | Win rate of A vs B for all pairs | Any matchup beyond about 65/35 in blind pick needs attention |
| Level / gear differential | Win rate vs difference in player level or card level | A steep slope = pay-to-win perception; normalise or bracket |
| First-move / side advantage | Win rate by seat, side or turn order | Beyond about 52–53%: compensate (komi-style bonus, alternate starts) |
| Game length | Distribution of match durations | Long tails = stalemates; short spikes = snowballing |

**Statistical hygiene.** Use the standard-error rule (`references/difficulty-design.md` §2.4). Correct for selection: specialists who pick niche options can inflate their win rate. Compare win rate when the option is played by players at similar ratings, or use a regression with player rating as a covariate. Treat win rates within the first days after a patch as learning noise.

### 7.3 Process

1. **Detect** with metrics and community signals. Distrust either alone.
2. **Diagnose** the cause, not the symptom: a number (stats), a kit interaction (two cards combo), a counter missing from the pool, or a map or mode bias.
3. **Prefer targeted changes:** nerf the specific interaction rather than the whole option. Buff counters and alternatives, not only nerf the top. Change one lever per option per patch where possible.
4. **Size changes** in about 5–10% steps for numbers. Larger changes only for broken outliers. Simulate before shipping: self-play bots replay the matchup matrix.
5. **Ship with notes** that explain intent ("Reduced Wizard splash radius to give swarm decks counterplay"). Transparent notes build trust.
6. **Watch** for 1–2 weeks with the same metrics. Roll back via remote config if the change overshoots.

### 7.4 Spending and fairness

- If players can buy power, PvP needs one or more of: **matchmaking that includes power** (not only skill), **level caps or normalisation** in tournaments and some ranked modes, and **brackets** by power band.
- Publish what matchmaking considers (`references/dynamic-difficulty.md` §7) and keep the red lines in §6 of that file.
- Track the win-rate slope against the level or gear differential (§7.2) as a standing KPI. If paying players win dramatically more against equal-skill opponents, the game is pay-to-win, whatever the marketing says.

## 8. Intransitive design

### 8.1 Why intransitivity

A transitive ranking (A > B > C) ends in a solved meta: everyone picks A. Intransitive relationships (A > B > C > A) keep every option relevant, as long as players can adapt (information, re-picks, deck variety).

### 8.2 Weighted rock-paper-scissors

Let R beat S by payoff a, S beat P by b, and P beat R by c (zero-sum). The equilibrium mix for both players is:

```
r : p : s = b : a : c
```

**Worked example.** a = 1, b = 2, c = 3 gives r = 1/3, p = 1/6, s = 1/2.
Check: against that mix, every option has expected payoff 0.

**The counter-intuitive lesson.** Making Paper's win against Rock bigger (raising c) does **not** make Paper more common at equilibrium. It makes **Scissors**, Paper's counter, more common. Buffing an option's payoff mainly raises the play rate of its counter. This is why naive buffs often "fail" in live metas. Model it before patching:
`python3 ${CLAUDE_PLUGIN_ROOT}/skills/design-theory/scripts/decision_math.py matrix --payoff "0,-3,1;3,0,-2;-1,2,0" --labels Rock,Paper,Scissors`

### 8.3 Counter structures

| Structure | Example | Notes |
|---|---|---|
| 3-cycle | Melee > Ranged > Cavalry > Melee; fire/water/grass types | Easy to teach; icons and colours |
| 5-cycle (each beats two, loses to two) | RPS-Lizard-Spock style wheels | More options without dominance; harder to learn |
| Soft counters | +20–50% effectiveness, not a guaranteed win | Skill and power can overcome; good for blind pick |
| Hard counters | Near-guaranteed win | Only where players can adapt mid-match (swap, re-pick) |
| Role triangles | Tank > Assassin > Mage > Tank | Ties counters to kits, not only numbers |

**Rules.**

- Every option has at least one counter and at least one favourable matchup. No option has more than about 2× as many bad matchups as good ones.
- Counters must be **accessible**: not locked behind rarity or payment in competitive modes.
- In blind-pick formats, prefer soft counters (matchups within about 60/40). Reserve hard counters for formats with information and adaptation.
- Show the counter wheel in the UI. Hidden counters feel like random losses.

## 9. Cost curves

### 9.1 The method (after Schreiber)

1. **List costs** (mana, gold, elixir, supply, cooldown, card slots, rarity) and **benefits** (stats, effects).
2. **Pick a common unit** of value and assign a value to each benefit and each cost. Draft values from first principles (DPS × EHP for combat units), then refine with sims and telemetry.
3. **Define the curve:** value as a function of cost. It can be linear, or super-linear when higher costs carry extra hidden costs (tempo, vulnerability while saving up, card slots).
4. **Benchmark against vanilla objects.** Units or cards with no special abilities define the curve. Abilities are priced as add-ons. Card-game designers have long benchmarked creatures this way (a plain 2-cost 2/2 is the classic reference point).
5. **Plot every object** against the curve. Outliers above are under-costed (overpowered), below over-costed (underpowered).
6. **Account for situational value.** Effects that are strong only in some matchups get a discount; universally useful effects get a premium.

### 9.2 The combat law sets the curve's shape

From Lanchester (§10): under **square-law** fighting (everyone can target anyone), army strength ∝ N² × DPS × HP. Equal cost-efficiency then needs cost ∝ √(DPS × HP). Under **linear-law** fighting (fixed frontage, duels in sequence), strength ∝ N × DPS × HP, so cost ∝ DPS × HP. The right price of a big unit therefore depends on how your game resolves fights. Ranged, open-field games make cheap swarms strong. Chokepoints and area damage make elites strong. Use the power metric that matches your combat law when fitting the curve.

### 9.3 Worked example: a 6-unit roster

Power metric: √(DPS × EHP), scaled. Costs in elixir-like units.

```
python3 ${CLAUDE_PLUGIN_ROOT}/skills/progression-difficulty/scripts/balance_math.py costcurve \
  --units "archer:3:52,knight:4:66,giant:5:80,wizard:5:96,goblins:2:30,golem:8:118" --tolerance 0.15
```

| Unit | Cost | Power | Curve prediction | Residual | Fair cost | Verdict |
|---|---|---|---|---|---|---|
| archer | 3 | 52 | 51.5 | +1.0% | 3.0 | ok |
| knight | 4 | 66 | 65.8 | +0.2% | 4.0 | ok |
| giant | 5 | 80 | 80.2 | −0.2% | 5.0 | ok |
| wizard | 5 | 96 | 80.2 | +19.8% | 6.1 | over-powered for cost |
| goblins | 2 | 30 | 37.2 | −19.3% | 1.5 | under-powered for cost |
| golem | 8 | 118 | 123.2 | −4.2% | 7.6 | ok (within tolerance) |

The fit is robust (Theil–Sen): power ≈ 8.5 + 14.3 × cost. **Decisions:** Wizard to cost 6, or cut its splash damage about 15%. Goblins get +20% power rather than a cost of 1.5 (half costs are unreadable). Golem's −4% is within tolerance, and arguably a fair discount for being slow. Re-run after changes, then verify with self-play matchups (§7.3), because the curve ignores synergies and counters.

### 9.4 Rarity and the curve

In fair PvP, rarity should buy **novelty, complexity or niche strength**, not more value per cost. If legendary units sit systematically above the curve, rarity has become power, and the game is pay-to-win in proportion to how hard legendaries are to obtain (`monetization`, `legal-ethics`).

## 10. Lanchester's laws: numbers vs quality

F. W. Lanchester (1916) modelled attrition between two forces A and B with per-unit effectiveness α and β (kills per unit time per unit).

| Law | Applies when | Strength | Survivors of the winner |
|---|---|---|---|
| Linear | Fixed frontage, one-on-one duels, chokepoints, melee lines | α·A vs β·B | A − (β/α)·B |
| Square | Everyone can target anyone (ranged, aimed fire, open field) | α·A² vs β·B² | √(A² − (β/α)·B²) |

**Worked example.** 20 swarm units (effectiveness 1) vs 10 elite units (effectiveness 3).

| Law | Strength A vs B | Winner | Survivors |
|---|---|---|---|
| Square | 400 vs 300 | Swarm | 10 |
| Linear | 20 vs 30 | Elites | 3.3 |

`balance_math.py lanchester --a 20 --b 10 --a-eff 1 --b-eff 3 --law square` (and `--law linear`). You can give `--a-dps --a-hp --b-dps --b-hp` instead; effectiveness is then computed as own DPS ÷ enemy HP.

**Design levers this explains.**

- **Area damage** turns square-law fights toward linear (or worse for swarms). That is why splash units counter swarms.
- **Chokepoints and lanes** enforce linear-law fighting, which favours elites and tanks.
- **Unit caps and supply** limit N, which bounds square-law snowballing.
- **Focus fire and overkill:** square-law strength assumes no overkill waste. Big-hit units waste damage on small targets. That is another reason splash and multi-hit matter.
- In tower defence, enemy waves fight under something close to linear law against towers with fixed coverage. Wave HP budgets should scale with total tower DPS × time-in-range (see `genre-playbooks` strategy).

## 11. Balancing methodology: spreadsheets, sims, telemetry

### 11.1 The loop

```
model (formulas, cost curve) → spreadsheet (tables, derived stats, checks)
→ simulation (Monte Carlo, bots, self-play) → playtest (feel, readability)
→ telemetry (soft launch / live) → change proposal → simulate again → ship via remote config → watch
```

Balance by numbers first, so nothing is obviously broken. Then by simulation, so emergent interactions surface. Then by feel, because readability and fun beat spreadsheet purity. Record every change in a balance changelog with intent, numbers and evidence.

### 11.2 Spreadsheet structure (one workbook per system)

| Tab | Contents | Rules |
|---|---|---|
| `params` | Global constants (k for armour, growth rates, crit multiplier) | Single source of truth; everything references it |
| `curves` | Progression and content power curves per level | Generated from formulas; hand edits flagged |
| `objects` | One row per unit, card or item: costs, raw stats | No formulas except lookups |
| `derived` | DPS, EHP, TTK, power metric, value per cost | Formulas only; never typed numbers |
| `curve_fit` | Cost-curve fit, residuals, fair cost | Mirrors `balance_math.py costcurve` |
| `matchups` | Pairwise duel results (analytic or simulated) | Colour-scale; flag beyond 65/35 |
| `checks` | Assertions: no residual > tolerance, TTK in band, no option dominated | All green before export |
| `export` | Columns exactly as the game's data files and remote config expect | Exported to JSON consumed by the game and the simulator |

**Rule.** The same exported JSON feeds the game, the simulators (`economy_sim.py`, bots) and the spreadsheet. Duplicated hand-typed numbers in code are a balance bug waiting to happen. Contract parameters (`contract.mechanics[].parameters` with `min`/`max`) bound what tuning may change.

### 11.3 Simulation toolkit

| Question | Tool |
|---|---|
| Is any option dominated in a payoff matrix? | `decision_math.py matrix` (design-theory) |
| Is the roster on the cost curve? | `balance_math.py costcurve` |
| How long do fights last; what is crit variance? | `balance_math.py ttk` |
| Swarm vs elite under each combat law? | `balance_math.py lanchester` |
| Which armour formula fits the progression? | `balance_math.py damage` |
| Diminishing returns on a stat? | `balance_math.py softcap` |
| Economy and upgrade pacing? | `economy_sim.py`, `progression_calc.py` |
| Level win rates? | `match3_sim.py`, `puzzle_solver.py`, game-specific bots |
| Full matchup matrix? | Headless self-play in the sim-core (`game-architecture`) |

### 11.4 Sensitivity analysis

For each tunable parameter, change it by ±10% one at a time and measure the win-rate (or TTK) change. The **elasticity** = (% change in outcome) ÷ (% change in parameter). Tune with high-elasticity levers for big corrections and low-elasticity levers for fine-tuning. Parameters with near-zero elasticity are dead weight: remove them or make them matter.

### 11.5 Balance regression suite

After every balance change, automated runs must confirm:

- All levels stay within ±10 points of their bot win-rate targets (puzzle and PvE).
- No unit or card residual exceeds the tolerance; no option is strictly dominated.
- No matchup crosses the blind-pick threshold.
- TTK bands hold for each content tier.

Store results as playtest-report evidence (`playtest-report.schema.json`) for the `playthrough` gate.

## 12. Worked examples

### 12.1 Armour formula for a hero RPG

**Setup.** Hero HP 2,000. A tier-3 enemy hits for 150. Armour from gear runs 0–300 over the game.

| Armour | Hyperbolic (k = 100) damage | Hits to kill | Subtractive (floor 10%) damage | Hits to kill |
|---|---|---|---|---|
| 0 | 150 | 14 | 150 | 14 |
| 50 | 100 | 20 | 100 | 20 |
| 100 | 75 | 27 | 50 | 40 |
| 200 | 50 | 40 | 15 (floor) | 134 |
| 300 | 37.5 | 54 | 15 (floor) | 134 |

**Decision.** Subtractive armour makes the hero effectively immortal against tier-3 enemies past about 135 armour. Content would then need a constant hit-size escalation to stay relevant, a treadmill that breaks old content. Hyperbolic armour keeps every point worth 20 EHP (HP/k), so armour never nullifies. Choose hyperbolic with k = 100. Set level-normalised k (k grows 6% per enemy level) only if old-content steamrolling becomes a problem.

### 12.2 HP vs armour shop pricing

With HP 1,500 and def 200 (k = 100), armour's marginal EHP is 5× that of HP (§5). If both cost 1 gold per point, price armour at about 3–5× HP per point, or accept armour stacking and add percent penetration to elite enemies. Verify with a gold-optimal build search (greedy by marginal EHP per gold), and check that the optimal build is not "all armour".

### 12.3 Weighted RPS rebalance

**Telemetry.** In a 3-class PvP game, Cavalry beats Archers 70/30, Archers beat Infantry 60/40, and Infantry beat Cavalry 55/45. Pick rates: Cavalry 45%.

**Payoffs as win-rate margins:** Cavalry > Archers by 0.40, Archers > Infantry by 0.20, Infantry > Cavalry by 0.10. With R = Cavalry, S = Archers and P = Infantry, so that a = 0.40, b = 0.20, c = 0.10, the equilibrium mix is Cavalry : Infantry : Archers = b : a : c = 0.2 : 0.4 : 0.1, that is 29% / 57% / 14%. Players who over-pick Cavalry (45%) are playing far from equilibrium, so Infantry should be winning more than it is. Check whether Infantry's counter is under-performing in practice (execution difficulty, map bias) before touching numbers. If you change numbers, buff Infantry vs Cavalry: raising c raises the equilibrium share of Archers (Infantry's counter), so watch Archers next.

## 13. Power and balance checklist

- [ ] The power-share position is chosen and measured: meta uplift ≤ the stated bound; the skill gap is large enough in skill-led genres.
- [ ] The power-ratio → win-rate mapping (β) is fitted from sims; "recommended power" has a stated win rate.
- [ ] Walls show the shortfall, have a free path within about one daily cycle, and are not synchronised with offers.
- [ ] Stacking rules (additive, multiplicative, buckets) are defined and shown in tooltips.
- [ ] The damage formula is chosen with the decision table; the order of operations is written and unit-tested.
- [ ] EHP marginal values are checked; shop prices do not create a dominant stat.
- [ ] TTK and TTD are inside the bands per content tier; breakpoints are visible.
- [ ] PvP metrics are dashboarded (win, pick, ban, by skill bracket, matchup matrix, level differential, side advantage).
- [ ] Counters exist for every option, are accessible, and are soft in blind pick.
- [ ] The cost curve is fitted with the power metric that matches the combat law; outliers are resolved.
- [ ] One exported data source feeds the game, the simulators and the spreadsheet; a balance changelog is kept.
- [ ] The balance regression suite runs after every change and stores evidence.
