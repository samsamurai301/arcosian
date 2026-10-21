# Platformer and Metroidvania Playbooks

Platformers live or die on the jump. A jump that feels right is a few numbers (gravity, apex height, forgiveness windows) tuned by someone who has played it a thousand times. This file holds five playbooks in the shared 14-part template, plus a 15th part, "Platform notes", for PC, console, web and mobile differences:

1. Precision 2D platformer
2. 3D platformer and collectathon
3. Metroidvania
4. Puzzle platformer
5. Roguelite platformer

Three foundations come first: jump physics (with formulas you can paste into a controller and a unit test), the ability-gating graph, and map and backtracking design. Mobile and casual platformers are in `skills/genre-playbooks/references/action-arcade-roguelite.md` §3 and roguelite structure in §5. Combat frame data, stamina and camera for action-adventure are in `skills/genre-playbooks/references/action-adventure.md` §0. Gating-graph detail that serves both genres is in §0.2 here and `action-adventure.md` §0.4. This file does not repeat those. It adds PC and console depth. The headline for an agent pipeline: platformer physics, level solvability and ability graphs are deterministic and solver-verifiable (4–5/5 for small slices). Level feel, art, music and the "one more try" rhythm need human taste. A metroidvania with a full world map is large (2–3/5), while a precision 2D slice is a strong first project.

## Contents

| § | Playbook | Session profile (estimate) | Primary monetisation | Agent-buildability | First project for an agent pipeline? |
|---|---|---|---|---|---|
| 0 | [Shared foundations](#0-shared-foundations) | — | — | — | Read first |
| 1 | [Precision 2D platformer](#1-precision-2d-platformer) | 1–10 min levels, 3–10 h total | Premium | 5/5 | Yes |
| 2 | [3D platformer / collectathon](#2-3d-platformer-and-collectathon) | 30–90 min sittings, 8–25 h | Premium | 2/5 | Only as a single-stage slice |
| 3 | [Metroidvania](#3-metroidvania) | 45–120 min sittings, 10–30 h | Premium, DLC | 3/5 | Yes, a small world graph |
| 4 | [Puzzle platformer](#4-puzzle-platformer) | 20–60 min sittings, 4–10 h | Premium | 4/5 | Yes, with solver validation |
| 5 | [Roguelite platformer](#5-roguelite-platformer) | 10–40 min runs | Premium, early access | 4/5 | Yes |
| — | [Volatile facts](#volatile-facts-as-of-oct-2026--verify-before-relying) | — | — | — | Check before quoting numbers |

## How to use these playbooks

- Copy the core loop into `contract.json → loops[]`. Set `meta.genre: "platformer"` and `meta.subgenre` to the playbook slug. Set `meta.platforms`, `meta.input` (`gamepad` and `mouse_keyboard` for most PC and console titles) and `meta.orientation` (landscape for nearly all).
- Turn the starter feature list into P0 `features.json` entries with `gs.py feature add`. Each acceptance criterion maps to `unit` or `playthrough` gate evidence (bots, replays, solvers).
- Mechanic category labels: combat, collection & randomness, progression & upgrade, economy & resources, exploration & traversal, narrative, UX automation. Resolve them with `gs.py kb "<mechanic>" --skill mechanics-codex`.
- KPI statements are qualitative unless sourced. Premium platformers are judged on review scores, completion rate and word of mouth. Fit real curves after a playtest.
- Write the physics table (§0.1) into the contract's tuning data before any level work. Every level metric derives from it.

## 0. Shared foundations

### 0.1 Jump physics
Choose the jump by design values (height and time), then derive the physics. This gives numbers a designer can reason about.

```
Given  h = apex height (units),  t_up = time to apex (s)
  gravity        g  = 2h / t_up²
  launch speed   v0 = 2h / t_up            (equivalently v0 = g · t_up)
  height check   h  = v0² / (2g)
Worked example: h = 3.0 tiles, t_up = 0.40 s
  g = 6.0 / 0.16 = 37.5 tiles/s²    v0 = 6.0 / 0.40 = 15.0 tiles/s
  air time (flat ground) = 2 · t_up = 0.80 s
Horizontal reach   gap_max = v_x · t_air     v_x = 8 tiles/s → 8 · 0.80 = 6.4 tiles (computed)
Design gaps at about 70–85% of gap_max so that most players clear them (estimate)
```

Integrate with a fixed timestep (for example 1/60 s) using semi-implicit Euler, and never tie gravity to the render frame rate:

```
vy += -g · dt          (use g_fall when vy < 0 or when the button is released)
y  += vy · dt
```

- **Fall gravity multiplier.** Falling faster than rising (g_fall = 1.3–2.0 × g, estimate) makes jumps feel snappy and gives a clear apex. Many classic games use heavier fall gravity.
- **Terminal velocity.** Clamp vy to a maximum fall speed (for example 20–30 tiles/s) so landings are predictable and the camera can follow.
- **Variable jump height.** On button release while rising, either multiply vy by a cut factor (0.4–0.6) or apply a larger gravity (g_cut = 2–4 × g) until the apex. The minimum jump (a tap) should be about 25–40% of the full height. With the example above, a tap gives h_min ≈ 0.75–1.2 tiles. Show this in a test.
- **Apex hang (half gravity).** When |vy| is below a small threshold (for example 10% of v0), use 50% gravity for a few frames. It adds air control at the top and improves precise landings. Optional.
- **Coyote time.** Allow a jump for N frames after leaving a ledge. Typical N is 4–8 frames at 60 fps (about 70–130 ms, estimate). Implementation: a timer reset to N while grounded; a jump is legal if timer > 0. Consume the timer on jump so it cannot double-fire.
- **Jump buffering.** If the jump button is pressed up to M frames before landing, jump on the first grounded frame. Typical M is 4–8 frames (estimate). Store the press time and compare on landing.
- **Corner correction.** If the head clips a ledge by a few pixels, nudge sideways instead of stopping the jump. Same for ledge steps (feet).
- **Acceleration and friction.** Horizontal speed: v_x approaches max with an acceleration a (ground 40–80 tiles/s², estimate) and turns with a higher deceleration. Air control is usually 60–100% of ground control in precision games, and lower in realistic ones. Without friction values the character slides.
- **Wall slide and wall jump.** Cap fall speed on a wall (for example 30% of terminal). The wall jump impulse needs both a vertical and a horizontal component and a short input lock so the player does not climb the same wall in one move.
- **Dash.** Fixed distance or time (for example 0.15 s at 3× speed), with an optional gravity pause. Count dashes per air time.
- **Frame-rate independence.** Run physics at a fixed step with an accumulator and interpolate rendering. Unit-test that 60 Hz and 144 Hz inputs give the same jump height within 1%.
- **Verification.** Unit tests: apex height within 2% of h, time to apex within 1 frame of t_up, tap height within the band, coyote and buffer windows exact in frames, and no tunnelling through one-tile platforms at terminal speed.

```
Tuning table (store in the contract)
 h  t_up  g  g_fall  v0  v_x_max  coyote  buffer  tap_ratio  term_v
 3.0 0.40 37.5  60.0  15.0   8.0     6 f     6 f     0.33      24.0
```

### 0.2 The ability-gating graph
In a metroidvania (and many 3D platformers) abilities open gates. Model the world as a directed graph so a solver can prove it is completable.

```
Nodes  = rooms or areas         Edges = connections, each with a requirement set R(e)
Abilities A = {double_jump, dash, wall_jump, ...}
State  = (location, ability set).  Reach(S): from location, traverse edges where R(e) ⊆ abilities held.
Closure: repeat { collect all abilities in reachable rooms; update reach } until nothing changes.
Complete  ⇔  closure reaches every required room (boss, ending) and every ability pickup.
Soft-lock ⇔  a reachable state exists from which the closure cannot reach the ending without a one-way edge back.
```

- **Requirement sets.** An edge requirement can be a single ability (dash), a conjunction (dash AND wall_jump), a skill option (wall_jump OR a hard dash trick), or a progress flag (boss defeated). Mark tricks as "sequence break" and decide whether they are intended.
- **Reach metrics from the physics table.** Convert each ability into a range: a plain jump clears gaps up to gap_max and heights up to h (§0.1). Double jump adds a second h. A dash adds distance d. Check each gate with the table: a gap that needs 7.5 tiles must need the dash, and must not be clearable by a plain jump (gap_max 6.4 in the example).
- **Hard versus soft gates.** Hard gates are physically impassable without the ability. Soft gates can be passed with skill (a tricky jump) before the ability arrives. Soft gates reward expertise and need the same graph with "skill option" edges.
- **Order and pacing.** A new ability every 30–60 minutes (estimate). Each ability should unlock at least three gates, be used in a combat or a boss, and be taught in a safe room before it is tested.
- **One-way edges.** Drops and collapsing floors are one-way. The solver must verify the player can return, or a warp or alternate path exists.
- **Verification.** Export the graph to JSON. Run the closure and soft-lock check in CI (`level-design`). Gate on: ending reachable, all pickups reachable, no soft-locks, backtrack ratio within the contract's band (§0.3).

### 0.3 Map and backtracking design
Backtracking is the metroidvania's signature, and a big source of friction when done carelessly.

```
Backtrack ratio   b = (distance travelled through already-visited rooms) / (total distance)
  Track in playtest logs or a bot run. Target b below about 0.35 for the main path (estimate).
Travel cost       T(A→B) = path length / mean speed.  Cap the longest forced trip at 2–3 minutes.
```

- **Shortcuts.** After a long forced trip, open a one-way shortcut back to a hub. Players love using a shortcut they opened.
- **Fast travel.** Provide warp points or a similar system at hubs and bosses. Warp unlocking is a reward. Without fast travel, keep the world compact.
- **Map as UI.** Fill the map as rooms are visited. Mark doors by the requirement type (colour or icon) and let the player pin markers. Show unexplored exits. Provide map items (a pickup that reveals a region) if you want a purchase or reward.
- **Room reuse.** Rooms that change after an ability arrives (a hidden wall, a new platform) make backtracking feel fresh. Use sparingly.
- **Save rooms.** Place save points after every major challenge and before every boss. Heal the player there.
- **Loops.** The world should loop: a path that returns to a hub through a one-way door. Avoid long dead-end spurs without a reward.
- **Verification.** A bot walks the graph with a greedy strategy and a "wrong order" strategy. Report the longest forced trip, the number of dead ends, and whether each key area has a save room within N rooms.

### 0.4 Level design rules shared by the playbooks
- **Teach, test, twist, combine.** Introduce a mechanic in a safe place, test it with a small risk, twist it, then combine it with a prior mechanic (`level-design`).
- **Rhythm and checkpoints.** Short challenge sections (5–20 seconds) with checkpoints. Precision games use checkpoint after every screen.
- **Readable hazards.** Same colour and shape for hazards across the game. Telegraph moving hazards with a loop the player can learn.
- **Camera.** For 2D, a look-ahead in the movement direction (about 2–4 tiles) and a vertical dead zone. Avoid camera moves that hide the landing. For 3D see `action-adventure.md` §0.5.
- **Assist options.** Offer invincibility, slower game speed, extra dashes or skip level in precision games. Assist modes widen the audience without changing the default.

## 1. Precision 2D platformer

### Definition and player fantasy
Short, hard levels demanding tight jumps and fast retries. The fantasy is *flow and mastery*: a perfect line through a screen that looked impossible five minutes ago. Death is cheap and instant.

### Core loop
```
enter screen → read hazards → attempt → die and respawn instantly
  → learn the pattern → clear the screen → next screen
  → finish the level → collectible or alternate route → next chapter
```

### Meta loops
- **Collectibles and hard routes.** An optional challenge in each level.
- **Speedrun and time medals.** Level times, replays and ghosts.
- **Chapter structure.** A new mechanic per chapter.
- **Assist and challenge modes.** Harder remix levels after the main game.

### Session profile
Estimate: 1–10 minutes a level, 30–90 minute sittings. Sessions are built from many tiny retries. Instant respawn (under 1 second) is a requirement.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Tuned jump and run (§0.1) | exploration & traversal | The product. Test coyote, buffer and variable height |
| Dash, wall jump or similar | exploration & traversal | One signature move defines the game |
| Instant respawn and short checkpoints | UX automation | Death cost near zero |
| Hazards and moving platforms | exploration & traversal | Learnable loops |
| Collectibles | collection & randomness | Place them in optional hard lines |
| Assist options | UX automation | Invincibility, slow speed, extra dashes |
| Ghosts and replays | social & competition | Share via leaderboards |

### Monetisation model and typical mix
Premium purchase at a low-to-mid price. DLC chapters or soundtrack are common add-ons. Ads and IAP appear only in mobile versions (see `action-arcade-roguelite.md` §3). Keep assist modes free.

### KPI expectations
Qualitative. Per-screen death counts, completion by chapter, share enabling assist mode, speedrun uptake and review score. Use death heat-maps to find spikes. See `progression-difficulty`.

### Retention drivers
Mastery, optional challenge, speedruns, music and style, community, remix levels.

### Content pipeline and production scope (estimates)
Levels are the content: 100–300 screens for a full game. Tools for fast iteration are crucial. Art is often pixel or vector. Rough estimate: 1–8 people over 1–3 years. Level count and polish drive time.

### Reference titles
- *Super Mario Bros. 3* (Nintendo, 1988).
- *Super Meat Boy* (Team Meat, 2010): instant retry.
- *Celeste* (Maddy Makes Games, 2018): dash, coyote time and assist mode.
- *VVVVVV* (Terry Cavanagh, 2010): gravity-flip precision.
- *Super Mario Maker* (Nintendo, 2015): level creation as a game.
- *Cuphead* (Studio MDHR, 2017): run-and-gun boss rush.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Controls feel tight and fair | Input lag or inconsistent jump height |
| Instant retry and short checkpoints | Long respawns, long replays |
| Each level teaches something new | Difficulty from repetition only |
| Assist options for wider reach | One difficulty for all |
| Clear hazard language | Visual noise hides hazards |

### Innovation vectors
- Level editors with shareable codes.
- Procedural precision levels validated by a solver.
- Co-op with tethered characters.
- Rhythm-synced platforming.
- Accessibility-first design with granular assists.

### Agent-buildability: 5/5
**Why high:** physics, level validation and hazards are deterministic. A bot or solver can check every screen is solvable and measure difficulty with a skill model (reaction delay, input noise). Assets are small.
**What needs humans:** the final feel pass, level artistry and music.

### Starter feature list (P0 vertical slice: 1 chapter, 20 screens)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Player controller with the §0.1 tuning table (gameplay) | Apex height within 2%, tap height in band, 60 and 144 Hz give the same result (1%) |
| 2 | Coyote time and jump buffer (gameplay) | Windows exact in frames. A replay with a 1-frame-late jump still jumps |
| 3 | Dash or wall jump (gameplay) | Distance and cooldown per table. Dash count resets on landing |
| 4 | Instant respawn and checkpoint per screen (ux) | Respawn within 20 frames. Checkpoint state persists |
| 5 | 6 hazard types with learnable loops (gameplay) | Loop period documented. Telegraph at least 0.3 s |
| 6 | 20 screens with a teach-test-twist order (content) | Solver proves each solvable. Gap and height limits within 85% of reach |
| 7 | Difficulty estimate per screen (balance) | Skill-model bot death counts fall in the contract's band |
| 8 | Collectible in a hard route (content) | Reachable by a solver using only the abilities allowed |
| 9 | Assist options (accessibility) | Invincibility, speed and extra dash options persist and change nothing else |
| 10 | Timer and ghost replay (meta) | Ghost replays deterministically from the input log |
| 11 | Camera look-ahead (camera) | Landing zone visible for at least 0.3 s before touch-down |

### Platform notes
- **PC.** Keyboard and gamepad both common. Provide digital and analogue movement. Input latency matters: support unlocked frame rates with a fixed physics step. Level editors and workshop support extend life. Steam Deck is a strong audience (volatile facts).
- **Console.** Gamepad native. Fast resume and quick respawn. Switch-class hand-helds suit short sessions.
- **Web.** Excellent fit. Small download and instant start. Control the browser's audio unlock and input focus. Test across frame rates.
- **Mobile.** Touch controls are the main challenge. Use auto-run or one-button designs (`action-arcade-roguelite.md` §3).
- **Business.** Low-to-mid price on PC and console. A demo, speedrun community and streamer appeal help sales.

## 2. 3D platformer and collectathon

### Definition and player fantasy
A character runs, jumps and explores 3D stages to collect items. The fantasy is *playful movement through a toy world*: movement feels good before any goal is given.

### Core loop
```
enter stage → explore and move → find collectibles or complete challenges
  → earn stars or tokens → unlock stages or abilities → boss
  → next world
```

### Meta loops
- **Collectible hunting.** Stars, jiggies, moons or similar. Completionism is a goal.
- **Ability unlocks.** New moves open stage areas.
- **Hub world.** A central area gating progress by collectible count.
- **Challenge stages.** Timed or precision trials.
- **Costumes and cosmetics.**

### Session profile
Estimate: 30–90 minute sittings over 8–25 hours. Players explore at will. Short goals (one collectible in 2–5 minutes) keep sessions flexible.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Rich movement set (run, jump, dive, roll, wall-kick, ground pound) | exploration & traversal | §0.1 extended to 3D, with analogue speed |
| Camera | exploration & traversal | The hardest part. See `action-adventure.md` §0.5 |
| Collectibles with a purpose | collection & randomness | Each collectible is a mini-goal |
| Hub gating by collectible count | progression & upgrade | Gating via counts, not keys |
| Stage themes and verticality | exploration & traversal | Each stage has a mechanic twist |
| Simple combat or enemy stomps | combat | Low stakes |

```
3D air control: horizontal accel in air = 0.6–1.0 × ground accel (estimate). 
Ledge grab / mantle assist radius: 0.2–0.4 × character radius beyond the ledge (estimate).
Shadow or landing marker: show it whenever the player is more than 1 character-height above ground.
```

### Monetisation model and typical mix
Premium purchase, sometimes with DLC stages or an expansion. Cosmetic DLC is rare. Mobile and F2P 3D platformers exist but are uncommon.

### KPI expectations
Qualitative. Completion rate, collectibles per hour, stage drop-off, camera-related quits (flag in playtests) and the number of players reaching the credits. Review score and word of mouth.

### Retention drivers
Movement joy, discovery, stage variety, completionism and music.

### Content pipeline and production scope (estimates)
Stages in 3D with hand-placed collectibles, character animation, camera tuning and art direction. Rough estimate: 10–60 people over 2–5 years for a full title. A tiny-team slice with a limited moveset (1 stage, 8–10 collectibles) fits 2–5 people over 6–12 months.

### Reference titles
- *Super Mario 64* (Nintendo, 1996): the 3D template.
- *Banjo-Kazooie* (Rare, 1998): collectathon.
- *Super Mario Sunshine* (Nintendo, 2002) and *Super Mario Galaxy* (2007).
- *A Hat in Time* (Gears for Breakfast, 2017).
- *Super Mario Odyssey* (Nintendo, 2017).
- *Yooka-Laylee* (Playtonic, 2017): a modern collectathon revival.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Moving is fun with no goal | Controls feel floaty or imprecise |
| Camera is rarely a problem | Camera fights the player |
| Collectibles are varied and clearly signalled | Collectibles are padding |
| Stages have identity and mechanics | Stages repeat |
| Hub gating is generous | Hard walls on collectible counts |

### Innovation vectors
- Procedural stages with hand-made set pieces.
- Co-op collectathon.
- Short-form 3D platformers (4–6 hours).
- Physics-driven movement toys.
- Creator tools for community stages.

### Agent-buildability: 2/5
**Why low:** camera, art volume, animation and level feel need humans. 3D spaces are harder to validate with a solver.
**What agents do well:** movement controller maths, collectible tracking and save logic, gating counts, navigation-mesh reachability checks, UI.

### Starter feature list (P0 vertical slice: 1 stage, 10 collectibles)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | 3D controller with run, jump, long jump and ground pound (gameplay) | Apex and air time per table. Variable jump height tested |
| 2 | Coyote time and buffer in 3D (gameplay) | Windows exact in frames |
| 3 | Camera with collision and manual control (camera) | The player and landing zone remain visible in a 500-run bot test |
| 4 | Landing shadow marker (ux) | Shown when above the threshold height |
| 5 | Stage with 3 sections and verticality (level) | Nav-mesh and jump-reach checks show every collectible reachable |
| 6 | 10 collectibles of 4 types (content) | Count persists. Each has a signpost |
| 7 | 3 enemy types with stomp and avoid (gameplay) | Hit and stomp rules per table |
| 8 | Checkpoints and respawn (tech) | Respawn within 2 seconds. Collectibles kept |
| 9 | Hub gate by count (progression) | Gate opens at the stated count. Count survives restart |
| 10 | Boss encounter (gameplay) | Bot clears in the win-rate band |
| 11 | Camera and motion comfort options (accessibility) | Invert, sensitivity, camera-shake toggles persist |

### Platform notes
- **PC.** Gamepad is expected and mouse camera needs care. A FOV and camera-sensitivity slider help. Performance modes for low-end hardware.
- **Console.** Native fit. Analogue stick movement with a tuned dead zone and curve (`shooters.md` §0.3 gives the formula). 60 fps preferred.
- **Web.** Heavy 3D needs WebGL or WebGPU and careful assets. Small stages are feasible.
- **Mobile.** Touch camera control is hard. Simplified runners and auto-camera variants exist.
- **Business.** Premium. Long production for a small audience. Nintendo's strength here is hard to compete with, so target a niche or a style.

## 3. Metroidvania

### Definition and player fantasy
A large interconnected 2D world explored in a non-linear way. New abilities open previously blocked areas. The fantasy is *the map becoming known*: standing in a place you could not reach three hours ago.

### Core loop
```
explore → meet a blocked path → note it → find an ability or key
  → return and open it → new area → fight and find upgrades
  → boss → next ability
```

### Meta loops
- **Map completion.** Percentage, rooms, secrets.
- **Upgrades.** Health, mana or damage pickups, charms, gear.
- **Boss ladder and alternative endings.**
- **Sequence breaking and speedruns.**
- **New game plus and hard modes.**

### Session profile
Estimate: 45–120 minute sittings over 10–30 hours. Players stop at save rooms. Orientation after a break matters: the map and quest hints help return players.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Ability-gated world (§0.2) | exploration & traversal | The graph is the design |
| Interconnected map with shortcuts (§0.3) | exploration & traversal | Loops and one-way doors |
| Combat with upgrades | combat | Simple enough to play in a long session |
| Map and markers | UX automation | Filled on visit. Markers for blocked doors |
| Bosses as ability tests | combat | Each boss tests the newest ability |
| Secrets and sequence breaks | exploration & traversal | Reward deep knowledge |
| Save rooms and fast travel | UX automation | Spacing from §0.3 |
| Upgrade slots (charms, relics) | progression & upgrade | Build choices, not flat stats |

### Monetisation model and typical mix
Premium purchase, often at a low-to-mid price. Free or paid DLC expansions are common. Some titles give free updates to keep goodwill. Do not add IAP or loot boxes: audience reaction is strongly negative.

### KPI expectations
Qualitative with a sourced anchor in volatile facts. Track share reaching each boss, map completion percentage, longest session without a save, rooms with high death counts, and abandonment points (often a confusing backtrack). Review score and word of mouth are the sales driver.

### Retention drivers
Discovery, exploration reward, atmosphere and music, boss mastery, secrets and speedrun culture.

### Content pipeline and production scope (estimates)
The world graph and map (rooms, secrets), abilities, enemies, bosses, art (often hand-drawn 2D), music, animation. Rough estimate: 2–8 people over 2–5 years for indie titles. A large hand-drawn game can need a bigger team. Procedural variants exist but rarely match authored pacing.

### Reference titles
- *Metroid* (Nintendo, 1986) and *Super Metroid* (1994): the pattern.
- *Castlevania: Symphony of the Night* (Konami, 1997): the RPG-style branch.
- *Ori and the Blind Forest* (Moon Studios, 2015).
- *Hollow Knight* (Team Cherry, 2017) and *Hollow Knight: Silksong* (2025).
- *Axiom Verge* (Thomas Happ, 2015): a solo-developer example.
- *Metroid Dread* (MercurySteam/Nintendo, 2021).

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Strong world identity and map readability | A maze with no landmarks |
| Abilities feel good and open many gates | Abilities used for one gate |
| Shortcuts and fast travel respect time | Long forced backtracking |
| Clear signposts for blocked paths | The player cannot remember where to go |
| Bosses test and reward new abilities | Bosses unrelated to abilities |

### Innovation vectors
- Procedurally generated metroidvania worlds with solver-verified gating.
- Narrative-driven graphs with branching.
- Co-op exploration.
- Smaller, denser worlds (4–6 hours).
- Accessibility features: assist modes, map hints and hint systems.

### Agent-buildability: 3/5
**Why:** the gating graph, map data, room templates, enemy tables and save logic are testable. A solver can prove completability and measure backtracking (§0.2, §0.3). Procedural room assembly is feasible.
**Why not higher:** world art, atmosphere, music, boss feel and hand-tuned pacing.

### Starter feature list (P0 vertical slice: 40 rooms, 3 abilities, 2 bosses)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Player controller from the §0.1 table, with double jump (gameplay) | Physics tests pass. Double-jump height per table |
| 2 | Dash and wall jump (gameplay) | Distance, cooldown and wall rules per table |
| 3 | World graph JSON with requirement sets (level) | Closure reaches the ending and every pickup. No soft-locks |
| 4 | Gate metrics from the physics table (level) | Every ability gate is impassable without the ability and passable with it, per a sim |
| 5 | 40 rooms with enemies and hazards (content) | A bot walks the world. Backtrack ratio under the contract's limit |
| 6 | Map screen filled on visit with door markers (ux) | Rooms appear on entry. Markers show requirement types |
| 7 | Save rooms and a warp network (tech) | A save room within every N rooms. Warp unlocks on first visit |
| 8 | 8 enemy types and 2 bosses (gameplay) | Each boss tests a new ability. Bot clears in the win-rate band |
| 9 | Upgrades: 4 health pickups, 3 relic slots (progression) | Pickups persist. Relic effects match the table |
| 10 | Shortcut doors one-way (level) | Solver confirms each shortcut shortens the forced trip |
| 11 | Hint system for stuck players (ux) | After N minutes of no progress a hint marks the next goal |
| 12 | Save and load (tech) | State survives a kill. No duplicate pickups |

### Platform notes
- **PC.** Keyboard or gamepad. Support full remapping. Mod communities and speedrun tools extend life. Steam is the main store (`pc-web-release`).
- **Console.** Native fit and a strong audience, especially on Switch-class hand-helds. Save-state suspend and resume. Certification needs (`console-pathway`).
- **Web.** Small metroidvanias are feasible. Keep the world compact and use cloud or local saves.
- **Mobile.** Touch controls limit precise combat. A few ports exist. Fit depends on a simple moveset.
- **Business.** Premium at a low-to-mid price. Wishlists, demos and a strong visual identity are the funnel.

## 4. Puzzle platformer

### Definition and player fantasy
A platformer where the challenge is solving spatial puzzles, not just executing jumps. The fantasy is *the click of understanding*: a mechanic you thought you knew does something new.

### Core loop
```
enter a room → observe the layout and mechanics → form a plan
  → execute it (move, push, swap, rewind) → fail and revise
  → solve → next room → new twist
```

### Meta loops
- **World and chapter structure.** One core mechanic per chapter.
- **Hidden collectibles and optional rooms.**
- **Narrative.** Story told through the world.
- **Challenge and speed modes.**

### Session profile
Estimate: 20–60 minute sittings over 4–10 hours. Players stop at a solved room. Stuck players quit, so a hint system matters.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| A single core mechanic with variations | exploration & traversal | Time rewind, shadows, portals, swap, gravity |
| Room-based puzzles | exploration & traversal | Self-contained rooms with a clear goal |
| Undo or rewind | UX automation | Allows experimentation. Must be deterministic |
| Physics objects and switches | exploration & traversal | Predictable rules |
| Gradual twist introduction | progression & upgrade | Teach, test, twist, combine |
| Optional collectibles | collection & randomness | Hard variants of a room |

### Monetisation model and typical mix
Premium purchase at a low-to-mid price. DLC chapters or a level editor are possible. No ads or IAP in PC and console versions.

### KPI expectations
Qualitative. Per-room solve rate and time, hint usage, abandon points, and the share of players who finish. A target is that the median player solves each room within the time band set in the contract. Review scores and word of mouth drive sales.

### Retention drivers
Insight moments, atmosphere, story, optional challenge and community discussion without spoilers.

### Content pipeline and production scope (estimates)
Puzzle rooms (the main cost), art and audio, and narrative. Rough estimate: 2–10 people over 1.5–4 years. Solver tooling speeds validation and finds unintended solutions.

### Reference titles
- *Braid* (Number None, 2008): time manipulation.
- *Limbo* (Playdead, 2010) and *Inside* (2016): physics puzzles with atmosphere.
- *Portal* (Valve, 2007): first-person puzzle platformer.
- *Fez* (Polytron, 2012): perspective rotation.
- *Celeste* and *Baba Is You* (Hempuli, 2019) show adjacent forms (a precision game with puzzles; a pure puzzle game).
- *Unravel* (Coldwood, 2016).

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| A single clear idea explored deeply | Mechanics pile up without depth |
| Rooms are solvable by reasoning | Solutions rely on trial and error |
| Hints for stuck players | Players quit at the first wall |
| Short, clear failure and undo | Costly mistakes |
| Mood and style | Generic art and music |

### Innovation vectors
- Solver-validated procedural puzzle rooms.
- Co-op puzzles.
- Level editors with sharing.
- Rule-changing puzzle platformers.
- Adaptive hint systems.

### Agent-buildability: 4/5
**Why high:** puzzles are deterministic state spaces. A solver (BFS or A*) can prove solvability, find the shortest solution, count solutions and detect unintended shortcuts. `pcg.py` can generate candidates.
**Why not 5:** the "aha" quality, art direction and narrative need human judgement.

### Starter feature list (P0 vertical slice: 12 rooms, one core mechanic)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Player controller from §0.1 (gameplay) | Physics tests pass |
| 2 | Core mechanic (for example time rewind of N seconds) (gameplay) | Deterministic. Rewind restores exact state in 1,000 replays |
| 3 | Puzzle objects: switches, boxes, doors (gameplay) | Rules in data. Each has unit tests |
| 4 | Room format and loader (tech) | A room loads from JSON. State resets on exit |
| 5 | Solver (tools) | Solves each room. Reports solution length and count |
| 6 | 12 rooms in teach-test-twist order (content) | Solver finds a solution. No room has an unintended shortcut shorter than the intended path by more than 30% (estimate) |
| 7 | Undo or restart (ux) | Restart under 1 second. Undo restores the last move |
| 8 | Hint system, 2 levels (ux) | First hint a nudge, second a step. Costs nothing |
| 9 | Optional collectible in 4 rooms (content) | Solver confirms reachability |
| 10 | Save progress per room (tech) | Solved rooms persist. Resume at the last room |
| 11 | Difficulty estimate (balance) | Solution length and branching factor within the target band |

### Platform notes
- **PC.** Keyboard and gamepad. A restart key and an undo key help a lot. Short demo works as a Steam Next Fest entry.
- **Console.** Gamepad native. A rewind button and quick restart. Suited to hand-helds.
- **Web.** An excellent fit. Small download, quick sessions and a shareable link.
- **Mobile.** Touch works for discrete or tap-based puzzles. Hint-based monetisation exists, covered in `puzzle.md`.
- **Business.** Premium at a low-to-mid price. Strong review scores and streamer clips matter.

## 5. Roguelite platformer

### Definition and player fantasy
A platformer with procedural levels, permadeath-style runs and persistent unlocks. The fantasy is *every run is a new story*: a lucky find, a clever combination and a heroic last stand.

### Core loop
```
start a run → clear procedural rooms (move, fight, jump) → collect items and upgrades
  → boss → die or win → spend meta currency → unlock new items and abilities
  → start another run
```

### Meta loops
- **Permanent unlocks.** New items, characters and starting kits.
- **Daily and weekly seeds.** Shared challenges with leaderboards.
- **Mastery.** Tiers or heat levels that raise difficulty.
- **Discovery.** Item synergies and secrets.

### Session profile
Estimate: 10–40 minute runs, with 1–3 hour sittings. Short retry cycles dominate. A run ends with a satisfying summary and a next-step unlock. See `action-arcade-roguelite.md` §5 for roguelite structure.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Procedural rooms from authored pieces | exploration & traversal | Hand-made chunks, seeded assembly, solver check |
| Item synergies | progression & upgrade | Many items, controlled interactions |
| Permadeath with meta progress | progression & upgrade | Death teaches and rewards |
| Tight platforming and combat | combat | Same physics table (§0.1) |
| Secrets and shops | economy & resources | Gold and risk trade-offs |
| Seeds and dailies | social & competition | Deterministic from the seed |
| Run summary | UX automation | Shows what changed the run |

### Monetisation model and typical mix
Premium purchase, often via early access, with updates and DLC. Cosmetic DLC is rare. Do not sell run power. Mobile ports use ads or IAP (see `action-arcade-roguelite.md`).

### KPI expectations
Qualitative. Run length distribution, win rate by difficulty tier, death hot spots, item pick rates (to find over- and under-powered items), runs per player per week and daily-seed participation. Aim for a first-win time that suits the audience (set in the contract). See `progression-difficulty`.

### Retention drivers
Variety, discovery, synergy builds, mastery tiers, daily seeds, community knowledge and frequent updates.

### Content pipeline and production scope (estimates)
Room pieces (hundreds), enemies, bosses, 100+ items, balance and procedural validators. Rough estimate: 2–15 people over 2–4 years, then post-launch updates. Early access is a common funding model.

### Reference titles
- *Spelunky* (Derek Yu, 2008; 2012 HD): procedural platformer.
- *Rogue Legacy* (Cellar Door Games, 2013): metroidvania-style meta progress.
- *Dead Cells* (Motion Twin, 2018): roguelite metroidvania with fast combat.
- *Noita* (Nolla Games, 2020): physics simulation platformer.
- *Hades* (Supergiant, 2020) is a related action roguelite, covered under top-down in `shooters.md` §7.
- *Risk of Rain* (Hopoo, 2013): 2D roguelite with scaling difficulty.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Runs differ in a meaningful way | Runs feel samey |
| Death gives progress and learning | Unfair deaths without reward |
| Items combine in surprising ways | Dominant builds or dead items |
| Fast restart | Slow load between runs |
| Good platforming under the randomness | Random layouts create impossible jumps |

### Innovation vectors
- Solver-validated procedural levels.
- Co-op roguelite platforming.
- Narrative runs.
- Modding and custom items.
- Run-sharing and replays.

### Agent-buildability: 4/5
**Why high:** deterministic seeds, data-driven items, solver-checked rooms and bot runs for balance. `balance` sims find dominant builds.
**Why not 5:** feel, art, and the "one more run" rhythm need human tuning.

### Starter feature list (P0 vertical slice: 3 biomes × 6 rooms, 20 items, 1 boss)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Player controller from §0.1 (gameplay) | Physics tests pass |
| 2 | Room pieces (30) with a seeded assembler (level) | Same seed gives the same level on two machines. 1,000 seeds all solvable |
| 3 | Reach check on generated levels (level) | Every gap and height is within 85% of the physics table's reach |
| 4 | 20 items with tags and synergy rules (progression) | No pair exceeds the damage cap in a sim. Every item has a use case |
| 5 | 8 enemies and 1 boss (gameplay) | Bot clears the boss in the win-rate band |
| 6 | Shops and secret rooms (economy) | Prices follow the table. Secrets are reachable |
| 7 | Meta currency and 10 unlocks (meta) | Persistence verified. Unlocks change the item pool |
| 8 | Run summary screen (ux) | Lists items, kills and cause of death |
| 9 | Daily seed (meta) | The same seed gives the same layout and item rolls |
| 10 | Fast restart (ux) | New run starts in under 3 seconds |
| 11 | Difficulty tiers (progression) | Tiers change HP, speed and hazards. Win rate falls as designed |

### Platform notes
- **PC.** Mouse and gamepad play both work. Early access and Steam leaderboards are common. Mod support extends life.
- **Console.** Native fit. Save at room boundaries to survive suspend. Cross-platform seed sharing needs a backend.
- **Web.** Good fit for small runs. Seeds are shareable through links.
- **Mobile.** Touch roguelite platformers exist with simplified controls. See `action-arcade-roguelite.md` §3 and §5.
- **Business.** Premium and early access. Frequent updates keep the community engaged. Wishlists and a demo help.

## Volatile facts (as of Oct 2026 — verify before relying)

- Hollow Knight: Silksong (Team Cherry, launched 4 September 2025) passed 7 million copies in about three months, excluding Xbox Game Pass players. About 4.2 million sold in the first weeks, with Steam about 3.2 million. A third-party estimate put Steam revenue near $50 million at a $20 price (estimate). Team Cherry announced a free expansion — [TweakTown](https://tweaktown.com/news/109417/hollow-knight-silksong-sells-7-million-copies-since-launch-with-millions-of-game-pass-players/index.html), [WN Hub](https://wnhub.io/news/investment/item-49578)
- Steam Deck Verified requires the default controller configuration to reach all content, on-screen glyphs matching Deck or Xbox buttons, and controller-usable text entry. Criteria may change — [Steamworks docs](https://partner.steamgames.com/doc/steamdeck/compat)
- Steam's revenue share has been reported as 30% up to $10M, 25% from $10M to $50M and 20% above $50M per game (since October 2018). Confirm the current terms in Steamworks — [Fortune](https://fortune.com/2018/12/01/steam-valve-developer-revenue-agreement)
- Loot-box and paid-random regimes apply to any mobile roguelite platformer with random paid packs. Details are in `skills/genre-playbooks/references/rpg-gacha.md` volatile facts.
- Physics defaults in this file (coyote 4–8 frames, buffer 4–8 frames, fall gravity 1.3–2×) are community-practice estimates, not standards. Tune with playtests.

## Related skills
- `game-feel`: jump feel, hit stop, camera and input latency.
- `level-design`: teach-test-twist, gating graphs, solver gates.
- `progression-difficulty`: difficulty curves, death heat-maps, assist options.
- `balance`: item synergies, dominant-build sims, difficulty tiers.
- `procedural-generation`: seeded room assembly and solver validation.
- `gameplay-programming`: fixed-step physics, input buffering, state machines.
- `platform-targets`: input, frame rate and performance tiers per platform.
- `pc-web-release`: Steam, itch.io, demos and wishlists.
- `console-pathway`: console certification and ratings.
- `accessibility-localization`: assist modes, remapping, motion options.
- `qa-testing`: bots, replay tests, physics regression tests.
- `game-architecture`: sim-core, determinism, replays and ghosts.
