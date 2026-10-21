# Action Level Design

Level design for real-time games on phones: endless and level-based runners (including hyper-casual gate runners), survivor-like wave games, platformers, combat arenas, enemy placement, encounters, bosses and tower-defense paths. Action levels are built from the player's capabilities and reaction limits, so this file is formula-heavy: reaction distances, speed ramps, jump arcs, spawn pressure, threat budgets and boss HP sizing, each with a worked example. It closes with how to verify action levels by simulation and how to store them in the level-spec format. Principles shared with all genres are in `principles.md`; data and tooling in `level-pipeline.md`.

## Contents

1. Foundations: capability, reaction and fairness
2. Runner chunk design
3. Hyper-casual gate runners
4. Survivor-like wave design
5. Platformers
6. Arenas
7. Enemy roles and placement
8. Encounter design
9. Boss design
10. Tower-defense paths
11. Verifying action levels
12. Storing action levels in level-spec
13. Action level checklist

---

## 1. Foundations: capability, reaction and fairness

### Capability metrics
Write the player's capabilities down before building any level (`principles.md` section 12): speed, jump height and distance, dash distance and cooldown, attack range and DPS, hitbox size, invulnerability windows. Every level, generator and enemy is designed against these numbers.

### The reaction budget
The time between a threat becoming visible and the player's input taking effect:

```
t_budget = t_perceive + t_decide + t_input + t_execute
```

| Component | What it covers | Starting value for phone design (heuristic; measure) |
|---|---|---|
| t_perceive + t_decide | Notice the threat and choose a response | 0.35–0.6 s for a familiar threat with a choice of 2–3 responses; simple reaction to a single expected stimulus is around 0.2–0.25 s in lab conditions |
| t_input | Touch, swipe recognition, plus display and input latency | 0.05–0.15 s (higher on low-end devices) |
| t_execute | The in-game action completes (lane change, jump apex) | From your own animation timings |

Design rule: a threat must be visible for at least `t_budget × 1.3` (30% margin) before the last moment the player can still avoid it. Early levels use larger margins (×1.6–2.0); late levels shrink toward ×1.2, never below ×1.0.

### Fairness rules for all action levels
1. **Always a way out.** Every configuration has at least one survivable response for a player with the documented capabilities.
2. **No blind threats.** Nothing lethal appears from off-screen without a telegraph (sound plus on-screen indicator).
3. **No pixel-perfect requirements on touch.** Design at most at about 90% of any capability (`principles.md` section 12).
4. **Telegraph scales with damage.** The bigger the hit, the longer and clearer the wind-up.
5. **Consistent rules.** An enemy's attack looks the same every time; variants have different silhouettes or colours.
6. **Recoverable mistakes early.** Early levels forgive (shields, extra lives, generous checkpoints); punishment grows with mastery.

### Difficulty dimensions in action games
Speed, density (threats per second), complexity (distinct threat types at once), precision (tolerance windows), memory (pattern length to learn), endurance (length without rest). Raise **one dimension at a time** between adjacent levels or chunks; raising several at once creates spikes that feel unfair.

## 2. Runner chunk design

Endless runners assemble levels from authored **chunks** (also called segments or modules), selected at runtime by difficulty.

### Chunk spec
| Field | Example | Notes |
|---|---|---|
| id | `c_jump_slide_03` | Stable id for analytics (deaths per chunk) |
| length | 40 m (≈ 3.3 s at 12 m/s) | Express also in seconds at the reference speed |
| lanes | 3 | Most lane runners use 3 lanes |
| entry state | Lanes free on entry: [0, 1, 2] | Which lanes are safe when the chunk starts |
| exit state | Lanes free on exit: [1] | Must match the next chunk's entry |
| actions required | jump, lane change | Vocabulary used |
| difficulty | 3 (of 10) | From the formula below or measured deaths |
| min speed / max speed | 10–18 m/s | Speeds at which the chunk is fair |
| coins | 18, trail in lane 1 | Coins double as guidance |
| tags | tutorial, rest, combo, power-up | For selection rules |

### Obstacle vocabulary (lane runner)
| Obstacle | Response | Telegraph | Combines with |
|---|---|---|---|
| Low barrier | Jump | Visible shape | Lane change before or after |
| High barrier | Slide / roll | Distinct silhouette from low barrier | Jump (alternation) |
| Full block | Lane change | Solid object, lane fully blocked | Moving block |
| Moving obstacle (oncoming) | Lane change, early | Motion plus warning light | Anything; reduces t_budget because closing speed rises |
| Gap / hole | Jump | Visible edge | Coins over the gap |
| Ramp | Run up to an upper level | Ramp shape | High route risk/reward |

### Reaction distance (worked example)
Reference speed v = 12 m/s. Lane change: t_perceive+decide = 0.45 s, t_input = 0.10 s, t_execute = 0.25 s → t_budget = 0.80 s.

```
d_min      = v × t_budget × margin = 12 × 0.80 × 1.3 ≈ 12.5 m
```

- The camera must show an obstacle at least 12.5 m before it reaches the player (more at higher speeds; this sets the draw distance and fog).
- **Spacing between two obstacles that need different actions:** `d_gap ≥ v × (t_execute₁ + t_recover₁ + t_decide₂)`. With jump execute 0.6 s, recover 0.1 s, decide 0.3 s at 12 m/s: d_gap ≥ 12 m. At 18 m/s the same pattern needs 18 m; this is why a chunk has a **max speed** and why chunks must be re-validated when speed grows.

### Speed ramp
Two common forms:

```
linear-capped:  v(t) = min(v_max, v0 + a·t)
asymptotic:     v(t) = v_max − (v_max − v0) · e^(−t/τ)
```

Example asymptotic with v0 = 10, v_max = 20 m/s, τ = 120 s: v(60) ≈ 13.9, v(120) ≈ 16.3, v(180) ≈ 17.8 m/s. The asymptotic form gives fast early growth (boredom prevention) and a soft ceiling (fairness at the top end). Pair the speed ramp with the chunk difficulty ramp; do not let both rise steeply at once (one dimension at a time).

### Chunk difficulty estimate
Start with a formula, then replace it with measured deaths per 1,000 chunk entries:

```
difficulty = Σ obstacles (base_cost[type]) + 2 × combos_requiring_two_actions_within_1s + 1 × moving_obstacles − rest_seconds
```

### Chunk selection algorithm
```text
state: elapsed t, recent chunk ids (last k = 5), last rest at t_rest
D(t) = difficulty budget, e.g. D0 + growth·t, capped at D_max
every chunk boundary:
  if t − t_rest > 25 s: pick from tag "rest"; t_rest = t
  candidates = chunks with entry state compatible with current exit state,
               speed range containing v(t),
               difficulty within [D(t) − band, D(t)],
               id not in recent
  pick weighted random (weight higher for difficulty close to D(t)); if empty, relax band, then pick a rest chunk
  every N chunks: insert a power-up chunk or a coin-showcase chunk
```

Rules:
- **Rest every 15–30 seconds** of intense play (heuristic): a chunk with few obstacles and a coin arc.
- **Coins show the safe path.** The coin trail should always run through a survivable line; coins that lure into death break the guidance contract (`principles.md` section 4). Risky coin routes are fine if the risk is visible (high rail).
- **First runs are tutorials disguised as chunks.** The first 20–30 seconds use only teach chunks: one obstacle type at a time, wide spacing.
- **Deaths per chunk** is the key telemetry: a chunk with a death rate far above others at its difficulty is a design bug (often a readability problem), not a difficulty setting.

### Fairness validator (automatable)
Model the chunk as a time-lane grid sliced at a fixed step (e.g. 0.05 s at the max speed). States are (lane, action state). Transitions follow action durations (lane change takes 0.25 s, jump airtime 0.6 s). BFS from every entry lane must reach the exit with no collision. Run it for each chunk at min and max speed and for each compatible pair of adjacent chunks. Store the result in the chunk's level-spec `solver` block (`solvable`, plus custom fields).

## 3. Hyper-casual gate runners

Short levels (often 20–45 seconds) where the player steers left and right through gates that change a number (crowd size, weapon level, money): "+10", "×2", "−5". The level ends in a payoff (fight a boss crowd, fill a meter, a multiplier ramp).

### Design maths
- Model the level as a sequence of gate pairs; the player picks one gate per pair.
- If every pair is independent and every operation is increasing (+a, ×b with b > 0, −a), then **picking the larger immediate result is always optimal**, so the level has no real decision beyond reading the numbers correctly. Depth appears only when **lane position constrains later gates** (choosing the left gate commits you to the left side for the next stretch) or when operations interact (÷, "set to", gates that only count a subset of the crowd). Compute the best path with dynamic programming over (gate index, lane).
- Model players with simple bots: a **random** bot, and a **naive** bot that avoids negative gates and otherwise picks the larger numeral, ignoring the operator (a common misread at speed).
- Place the finale target (e.g. the enemy crowd) relative to these: for a test level, between the random average and the best path so the naive bot wins and random play mostly loses; for a twist level, between the naive bot and the best path so the player must read the operators.

### Worked example
Start crowd 10. Gate pairs: (+10 | ×2), (×2 | +15), (−5 | ×3), (+20 | −10).
- Best path: 10 → 20 (either gate) → ×2 = 40 → ×3 = 120 → +20 = **140**.
- Naive bot: +10 → 20; +15 → 35; ×3 → 105; +20 → **125** (it took +15 over ×2 at 20).
- Random bot: the 16 equally likely paths average **77.5** (range 20–140).
- Test-level finale: 77.5 + 0.6 × (140 − 77.5) ≈ **115**. The naive bot wins; only 4 of the 16 random paths reach 115.
- Twist-level finale: about **130**, which only the best path reaches (×2 at the second pair, then ×3 and +20); the naive bot's +15 misread loses.

### Rules
- Gate text must be readable at speed: large numerals, high contrast, operator symbols distinct (× vs +), visible for at least the reaction budget.
- Negative gates must be clearly coloured (commonly red vs blue/green) and shaped differently for colour-blind players.
- Avoid gates that require arithmetic beyond one step; the decision should take under a second.
- The finale outcome must be visually proportional to the number (more crowd = visibly bigger army).

## 4. Survivor-like wave design

Survivor-likes (the format popularised by *Vampire Survivors*, 2022) auto-attack; the player moves, collects experience and picks upgrades while enemy density rises. Level design is mostly **spawn direction over time** plus map geometry. Desktop runs are often long (Vampire Survivors' standard stages run 30 minutes); mobile survivor-likes typically use shorter chapters to fit sessions (verify per reference title).

### Run structure
| Phase | Share of run | Design job |
|---|---|---|
| Opening | First ~10% | Low density; first level-ups every ~10–20 s to teach the upgrade loop |
| Build-up | ~10–50% | New enemy types every 1–2 minutes; first elite; build identity forms |
| Mid peak | ~50–60% | First swarm event or mini-boss |
| Late game | ~60–90% | High density; the build is tested; level-ups slower (30–60 s) |
| Finale | ~90–100% | Boss or final swarm; reward |

### Spawn pressure model
Compare enemy health arriving per second with the player's ability to remove it:

```
incoming_HP_per_sec(t) = Σ_types  spawn_rate_i(t) × HP_i(t)
pressure P(t)          = incoming_HP_per_sec(t) / effective_player_DPS(t)
```

`effective_player_DPS` is the build's DPS times an efficiency factor for overkill, misses and movement (start with 0.6–0.8 and calibrate with the simulator).

| P(t) | Feel | Use |
|---|---|---|
| < 0.6 | Relaxed; screen clears | Openings and after-boss relief |
| 0.6–0.9 | Comfortable pressure | Most of the run |
| 0.9–1.1 | Tense; enemies accumulate slowly | Peaks |
| > 1.1 | Overwhelming; only movement and burst save you | Short swarm events (about 20–40 s), then relief |

If P stays above 1 for long, enemies accumulate without bound: the run will end regardless of skill, which is acceptable only at a deliberate finale.

### Worked example (8-minute mobile chapter, hypothetical numbers)
| Minute | Enemy mix | Spawns/s | HP each | Incoming HP/s | Expected player DPS (×0.7 efficiency) | P |
|---|---|---|---|---|---|---|
| 0–1 | grunts | 1.0 | 10 | 10 | 20 × 0.7 = 14 | 0.71 |
| 1–2 | grunts | 1.5 | 12 | 18 | 35 × 0.7 = 24.5 | 0.73 |
| 2–3 | grunts + bats | 2.5 | 12 | 30 | 50 × 0.7 = 35 | 0.86 |
| 3–4 | + first elite at 3:30 | 3.0 | 16 | 48 + elite | 70 × 0.7 = 49 | ~0.98 + elite spike |
| 4–5 | relief | 2.0 | 18 | 36 | 85 × 0.7 = 59.5 | 0.61 |
| 5–6 | swarm 5:30–6:00 | 8.0 | 10 | 80 | 100 × 0.7 = 70 | 1.14 (30 s) |
| 6–7 | tanks + grunts | 3.0 | 30 | 90 | 130 × 0.7 = 91 | 0.99 |
| 7–8 | boss + escorts | 1.0 + boss | 30 | 30 + boss | 150 × 0.7 = 105 | 0.29 + boss |

The DPS column comes from the upgrade curve; if the economy of level-ups changes, the wave table must be re-simulated.

### Experience and level-up pacing
```
level_up_interval(n) ≈ XP_needed(n) / (XP_per_enemy × kills_per_sec)
```
Target intervals: about 10–20 s early, rising to 30–60 s late (heuristic). Since kills per second rise with density, `XP_needed(n)` must grow faster than linearly to keep intervals stable: a polynomial such as `XP_needed(n) = a + b·n^1.3` is a starting point; check with `${CLAUDE_PLUGIN_ROOT}/scripts/progression_calc.py curve --formula poly --levels 40 --base 5 --exponent 1.3`.

### Enemy roster roles (survivor)
| Role | Behaviour | Purpose |
|---|---|---|
| Fodder | Slow, walks at the player | Density and XP |
| Fast swarmer | Fast, low HP | Forces movement |
| Tank | Slow, high HP | Tests single-target DPS |
| Ranged | Keeps distance, shoots | Forces repositioning |
| Charger | Telegraphed dash | Tests reading and dodging |
| Elite | Large, drops a chest | Reward spike; build check |
| Boss | Pattern-based | Finale exam |

### Map geometry for survivors
- Open fields favour kiting in circles; add **sparse obstacles** (pillars, trees) to create routing decisions without dead ends.
- Bounded arenas raise pressure (no escape) — use for boss phases.
- Hazard zones and pickups (healing, magnets, bombs) placed so routes through them are risk/reward choices.

### Mobile performance caps
Set a hard **cap on simultaneous enemies, projectiles and pickups** from profiling on the low-tier device (`mobile-performance`), and design density within it: when the cap is hit, raise HP per enemy instead of count. Pool every entity; merge XP gems when counts are high. The cap is a design constraint, not a late optimisation.

## 5. Platformers

### Jump arcs from design parameters
Kyle Pittman's GDC 2016 talk ("Math for Game Programmers: Building a Better Jump") popularised deriving gravity and launch velocity from the jump you want, rather than tuning physics constants by feel:

```
g  = 2h / t_h²         (gravity during ascent)
v0 = 2h / t_h          (launch velocity)
flat jump distance d = v_x × 2·t_h      (same gravity on the way down)
```

Example: max jump height h = 3 tiles, time to apex t_h = 0.42 s, run speed v_x = 6 tiles/s → g ≈ 34 tiles/s², v0 ≈ 14.3 tiles/s, flat distance ≈ 5.0 tiles. Many games use stronger gravity on the way down for a snappier feel, which shortens distance; recompute d from the actual descent gravity.

### Gap and height tables (from capability)
| Challenge | Easy | Medium | Hard | Never |
|---|---|---|---|---|
| Gap (fraction of max flat jump distance) | ≤ 60% | ≤ 80% | ≤ 90% | 100% |
| Ledge height (fraction of max jump height) | ≤ 65% | ≤ 85% | ≤ 93% | 100% |
| Landing platform width | ≥ 3 tiles | ≥ 2 tiles | ≥ 1 tile | < character width + coyote margin |
| Moving platform speed | ≤ 0.3× run speed | ≤ 0.5× | ≤ 0.7× | > run speed |

Coyote time (a short grace period to jump after leaving a ledge) and jump buffering (accepting a jump press slightly before landing) are standard forgiveness techniques; values around 0.08–0.15 s are common starting points (`game-feel`).

### Rhythm groups
Smith, Treanor, Whitehead and Mateas ("Rhythm-Based Level Generation for 2D Platformers", FDG 2009) structured platformer levels as sequences of **rhythm groups**: short runs of actions with a beat (jump, run, jump, wait), separated by rest areas. Useful for both handmade and generated levels:
- A rhythm group is 2–6 actions with a consistent tempo.
- Rest areas between groups give a safe spot to breathe and read the next group.
- Raise difficulty by tightening tempo, adding actions to a group or shrinking rest areas, one at a time.

### Checkpoints and death cost
```
expected replay after death ≈ (distance since checkpoint / 2) / speed      (uniform death position)
```
Keep the maximum replay after a death to roughly 20–45 s on mobile (heuristic) and place a checkpoint right before each hard rhythm group. Very hard sections should restart within 1–2 seconds (instant respawn) so failure feels like practice, not punishment.

### Mobile platformer constraints
- Virtual buttons are imprecise: widen landing zones and timing windows by about 10–20% relative to a controller-designed level (heuristic; verify with playtests).
- Auto-run platformers (the game runs; the player only jumps) remove one input and suit one-handed play; design every jump from the auto-run speed.
- Keep hazards off the bottom corners where thumbs rest; the camera should lead in the direction of travel (show more ahead than behind).

## 6. Arenas

An arena is a bounded combat space. Its geometry decides the fight before the first enemy spawns.

| Element | Rule of thumb (heuristic) | Why |
|---|---|---|
| Size | Cross time 3–6 s at player run speed for close combat; larger for ranged | Small arenas feel claustrophobic; large ones let players disengage |
| Circulation | At least one loop around the centre; no dead ends | Kiting and escape routes |
| Cover | 2+ cover positions per approach line in shooters; low cover for readability on small screens | Prospect and refuge (`principles.md` section 8) |
| Chokepoints | 1–2, never the only route | Tactical options without forced bottlenecks |
| Verticality | Height advantage visible and reachable | Risk/reward positioning |
| Spawn points | Out of the player's immediate reach, telegraphed, preferably in view (arena games) | Fairness |
| Hazards | Explosive barrels, pits: telegraphed, consistent | Environmental play |
| Camera (top-down mobile) | Arena edges visible or indicated; enemies off-screen get edge indicators | Small screens hide threats |

## 7. Enemy roles and placement

### Roles (general action games)
| Role | Function | Typical counter |
|---|---|---|
| Grunt / fodder | Density, pressure, power fantasy | Any attack |
| Rusher | Forces reaction, closes distance | Dodge, block |
| Ranged | Forces movement and cover use | Close the gap or use cover |
| Tank / shield | Requires a specific approach (flank, break armour) | Positioning, heavy attacks |
| Support | Buffs, heals or summons others | Priority target |
| Area denial | Zones, mines, turrets | Route around or destroy |
| Elite | Combination of the above with more HP | Full kit |

### Combinations
| Combo | Why it works |
|---|---|
| Ranged behind melee | Melee pins the player; ranged punishes standing still |
| Support + tank | Teaches target prioritisation |
| Swarm + area denial | Forces movement through dangerous ground |
| Rusher + turret | Splits attention between reaction and position |

### Placement patterns
| Pattern | Description | Telegraph requirement |
|---|---|---|
| Guard post | Enemies visible ahead, stationary | None beyond visibility |
| Patrol | Moving route; player picks timing | Visible route |
| Ambush | Enemies appear when a trigger is crossed | Audio or visual cue ≥ 0.5–1 s before they act; never on a first encounter with a new enemy |
| Sniper perch | Ranged enemy on high ground | Laser sight or muzzle glint |
| Gauntlet | Continuous stream along a path | Clear exit or end |
| Arena lock | Doors close; waves spawn | Doors visibly close; wave count shown |

### Placement rules
- **First encounter in safe context.** A new enemy type first appears alone or with fodder, visible from a distance, with space to observe its attack.
- **Readable silhouettes.** Each role has a distinct silhouette and colour accent visible at phone size.
- **Limit simultaneous attackers.** Many action games cap how many enemies may attack at once (an "attack token" pattern) so crowds feel threatening without becoming unfair; a cap of 1–3 active melee attackers is a common starting point.
- **Line of sight is the aggro budget.** The number of enemies that can see the player at once is the real difficulty; check sightlines, not only counts.

## 8. Encounter design

### Threat budget model
Give each enemy a threat cost, give each encounter a budget, and fill waves within it.

| Enemy | Threat points (example) |
|---|---|
| Grunt | 1 |
| Rusher | 2 |
| Ranged | 2 |
| Support | 3 |
| Tank | 4 |
| Elite | 8 |

```
budget(level) = B0 × growth^(level − 1)       e.g. B0 = 6, growth = 1.08 → level 10 ≈ 12, level 20 ≈ 26
```

Composition rules (examples): ranged ≤ 40% of the budget; at most one elite per wave until mid-game; at least one fodder group per wave for power fantasy; supports only with something to support.

### Wave structure
| Wave | Budget share | Purpose |
|---|---|---|
| 1 | 25% | Read the situation; introduce the mix |
| 2 | 35% | Pressure |
| 3 | 40% | Peak, with the encounter's signature enemy |
| Breather | — | Pickups, loot, 5–15 s of calm |

- Spawn the next wave when the current one is mostly cleared (e.g. 70–80% of its budget destroyed) or after a timeout, so players are not punished for killing slowly but are not bored either.
- **Telegraph every spawn** (portal, dust, sound) for 0.5–1.0 s before enemies can act.
- **Drops as pacing.** Health and ammo appear after peaks, not before them (the relief beat).

### Encounter spec template
```yaml
encounter: e_w2_03
arena: courtyard_a
budget: 14
waves:
  - {at: start, spawn: [grunt x4, ranged x1], points: [N, NE]}
  - {at: "70% cleared", spawn: [rusher x2, grunt x2, ranged x1], points: [S, W]}
  - {at: "70% cleared", spawn: [tank x1, grunt x3], points: [N]}
rewards: [health_small x2 after wave 2, chest after wave 3]
target: {first_try_win: 0.75, avg_duration_s: 75}
```

## 9. Boss design

A boss is an exam of the skills the preceding levels taught. It should be hard to beat and easy to understand.

### Structure
| Element | Rule |
|---|---|
| Phases | 2–3 phases at HP thresholds (e.g. 66% and 33%); each adds one new attack or one variation |
| Pattern language | 3–5 attacks per phase, each with a unique wind-up (animation, sound, colour) |
| Telegraph | ≥ 0.6–1.0 s on mobile for dodge-required attacks (longer than for gamepad-designed games) |
| Punish window | 1.5–3 s after big attacks where the boss is open; this is where damage is meant to happen |
| Arena | Supports the patterns (space to dodge, safe spots that change per phase) |
| Recovery | Checkpoint per phase for long fights on mobile; health pickups between phases if the genre allows |
| Readability | Boss health bar, phase markers, and clear hit feedback |

### HP sizing
```
boss_HP = target_fight_duration × expected_player_DPS × uptime
```
`uptime` is the share of the fight the player can deal damage (punish windows plus safe openings), often 0.4–0.7. Example: a 90-second fight, expected DPS 50 (from the progression curve at this point), uptime 0.6 → 90 × 50 × 0.6 = 2,700 HP. Check at the 25th and 75th percentile of player DPS: the fight should last roughly 1.5× and 0.7× as long, not 4× and 0.2× — if player power varies that much, scale the boss to the player's power band or narrow the band with progression design (`progression-difficulty`).

### Attempt targets (heuristic)
| Audience | First-try win | Attempts p50 |
|---|---|---|
| Casual action | 0.5–0.7 | 1–2 |
| Midcore | 0.25–0.45 | 2–3 |
| Hardcore | < 0.2 | 4+ |

### Anti-patterns
- Damage sponges: long fights with no pattern change.
- Unavoidable damage from random patterns (two overlapping attacks with no safe spot).
- One-hit kills without long telegraphs.
- Bosses that test skills the game never taught.
- Precision multi-touch requirements on phones.

## 10. Tower-defense paths

Path geometry sets the time enemies spend in range, which sets the DPS players need.

```
time_in_range = length_of_path_inside_tower_range / enemy_speed
required_DPS  = enemy_HP / time_in_range                      (single enemy, single tower)
```

Example: a tower with radius 3 tiles placed at a U-bend covers about 9 tiles of path; an enemy at 1.5 tiles/s spends 6 s in range; a 300-HP enemy needs 50 DPS from that tower alone.

| Path feature | Effect | Use |
|---|---|---|
| Long straight | Little coverage per tower | Early levels: forgiving through length |
| U-bends and switchbacks | One tower covers the path twice | Reward smart placement |
| Multiple entry paths | Splits defence | Mid-game |
| Merging paths | Natural kill zones | Teach area damage |
| Flying units ignoring the path | Breaks the path model | Teach as a twist |

Rules: build spots must offer meaningful choices (at least one obviously good spot and several situational ones); the path is fully visible before wave 1; show the wave composition preview.

## 11. Verifying action levels

Action levels cannot be checked by a puzzle solver, but most can be checked by simulation.

| Level type | Verifier | Gate |
|---|---|---|
| Runner chunk | Time-lane BFS validator (section 2) at min and max speed; adjacency check for chunk pairs | Every chunk solvable at every allowed speed |
| Gate runner | DP best path and bot paths (section 3) | Finale target between bot and best path as designed |
| Survivor wave table | Headless sim with a scripted kiting bot and the upgrade model; record P(t), deaths, time of death | P(t) within designed bands; bot survival rate within target |
| Platformer | Reachability using jump arcs on the tile grid (graph search over standable tiles with jump/fall edges) | Goal reachable; no jump above 90% of capability on easy levels |
| Arena / encounter | Headless sim with a reference bot or Monte Carlo of simplified combat | Win rate and duration within target |
| Boss | DPS check (HP sizing), pattern overlap check (no unavoidable damage), bot attempts if the engine supports it | Duration and win rate within target |

For engine-based verification, use the engine template's bot runner (`godot ... runner.gd -- --mode=bot --bot=greedy|random --runs=200`) and store its output as a playtest report (`playtest-report.schema.json`) under `.gamestudio/evidence/<FEATURE-ID>/`. See `qa-testing`.

## 12. Storing action levels in level-spec

The level-spec schema accepts `layout.type: custom` with a `format` name and a `data` payload, or `layout.type: generator` for runtime-generated content. Keep the format name versioned so tools can skip what they do not understand.

**Runner chunk**
```json
{
  "schema_version": "1.0",
  "level_id": "chunk_jump_slide_03",
  "mechanic_refs": ["lane_run", "jump", "slide"],
  "layout": {
    "type": "custom",
    "format": "runner_chunk_v1",
    "data": {
      "length_m": 40, "lanes": 3, "speed_range": [10, 18],
      "entry_free": [0, 1, 2], "exit_free": [1],
      "obstacles": [
        {"at_m": 8,  "lane": 0, "kind": "low_barrier"},
        {"at_m": 8,  "lane": 2, "kind": "full_block"},
        {"at_m": 24, "lane": 1, "kind": "high_barrier"}
      ],
      "coins": [{"from_m": 2, "to_m": 38, "lane": 1}]
    }
  },
  "goals": ["survive"],
  "moves_or_time_limit": null,
  "obstacles": [],
  "difficulty_target": {"win_rate": 0.92},
  "solver": {"solvable": null, "min_moves": null, "bot_win_rate": null, "runs": null},
  "teach": "test",
  "notes": "Jump then slide in lane 1; coins mark the safe line. Validate at 10 and 18 m/s."
}
```

**Survivor chapter**
```json
{
  "schema_version": "1.0",
  "level_id": "ch03",
  "mechanic_refs": ["auto_attack", "xp_levelup"],
  "layout": {"type": "generator", "generator": "arena_scatter_v1", "seed": 303, "params": {"w": 60, "h": 60, "pillars": 14}},
  "goals": [{"type": "survive_waves", "target": null, "count": 8}],
  "moves_or_time_limit": {"time_sec": 480},
  "obstacles": [{"type": "hazard_pool", "count": 3}],
  "difficulty_target": {"win_rate": 0.6, "attempts_p50": 2},
  "solver": {"solvable": null, "min_moves": null, "bot_win_rate": null, "runs": null},
  "teach": "test",
  "waves": [
    {"from_s": 0,   "to_s": 60,  "spawn_per_s": 1.0, "mix": {"grunt": 1.0}, "hp_mult": 1.0},
    {"from_s": 330, "to_s": 360, "spawn_per_s": 8.0, "mix": {"swarmer": 1.0}, "hp_mult": 1.0, "event": "swarm"},
    {"from_s": 420, "to_s": 480, "spawn_per_s": 1.0, "mix": {"tank": 0.5, "grunt": 0.5}, "boss": "golem_a"}
  ],
  "notes": "Pressure bands per minute in the design doc; swarm 5:30-6:00 at P≈1.1. Re-simulate after any upgrade-curve change."
}
```

Extra top-level fields such as `waves` are allowed by the schema (`additionalProperties: true`); prefer putting format-specific data under `layout.data` when the layout is custom, and use top-level extras only for data that belongs to the level rather than the layout.

## 13. Action level checklist

**Capability and fairness**
- [ ] Capability metrics documented and used; no requirement above ~90% of any capability.
- [ ] Every threat visible for ≥ 1.3× the reaction budget (more in early levels).
- [ ] Always a survivable response; no blind threats; telegraphs scale with damage.
- [ ] One difficulty dimension raised at a time between adjacent chunks or levels.

**Structure**
- [ ] Rest beats every 15–30 s of intense play (runners) or after peaks (encounters, survivors).
- [ ] New enemies and obstacles introduced in safe context first.
- [ ] Checkpoints keep replay after death within the target; hard sections respawn instantly.
- [ ] Boss: phases, unique telegraphs, punish windows, HP sized from DPS and duration.

**Mobile**
- [ ] Inputs and windows widened for touch; nothing critical under the thumbs or in unsafe areas.
- [ ] Entity caps from profiling; density designed within them.
- [ ] Levels or chapters fit the session target; pause and resume work mid-action.

**Verification**
- [ ] Runner chunks pass the time-lane validator at min and max speed and with every compatible neighbour.
- [ ] Survivor wave tables simulated: P(t) within bands; bot survival within target.
- [ ] Results recorded in the level-spec `solver` block and playtest reports stored as evidence.
