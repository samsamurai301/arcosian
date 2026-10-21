# Racing, Sports and Fighting Playbooks

Racing, sports and fighting games are judged by feel: the weight of a car, the timing of a shot, the frame in which a punch connects. This file holds six playbooks in a shared 15-part template (the 14-part format used elsewhere, plus platform notes), with a focus on PC and console. Mobile racing, mobile sports and mobile brawlers are covered in `skills/genre-playbooks/references/competitive-pvp.md`; read that file for ratings, matchmaking and integrity and do not repeat it here.

1. Arcade racing
2. Simulation racing
3. Kart racing
4. Team sports simulation
5. Extreme sports / skate
6. Fighting games (2D, 3D and platform fighter)

Five foundations come first: vehicle handling models, catch-up mechanics and their fairness, sports AI, frame data with rollback netcode, and input buffers with motion inputs. Single-player racing and sports against AI are deterministic and bot-testable. Fighting games are the most agent-friendly of the three because the whole game is a frame-exact state machine, but the feel still needs human hands. Market numbers live in the dated volatile-facts section.

## Contents

| § | Playbook | Session profile (estimate) | Primary monetisation | Agent-buildability | First project for an agent pipeline? |
|---|---|---|---|---|---|
| 0 | [Shared foundations](#0-shared-foundations) | — | — | — | Read first |
| 1 | [Arcade racing](#1-arcade-racing) | 3–5 min races, 20–60 min sittings | Premium, DLC car packs | 3/5 | Yes, single-player time trial plus AI |
| 2 | [Simulation racing](#2-simulation-racing) | 10–60+ min races | Premium plus DLC, subscription | 2/5 | No, physics tuning needs real hardware and wheels |
| 3 | [Kart racing](#3-kart-racing) | 2–4 min races, party sessions | Premium, DLC tracks | 4/5 | Yes |
| 4 | [Team sports sim](#4-team-sports-simulation) | 10–25 min matches, seasons | Annual premium, ultimate-team style modes | 2/5 | No, licences and data dominate |
| 5 | [Extreme sports / skate](#5-extreme-sports--skate) | 2-min runs, 30–90 min sittings | Premium, DLC | 3/5 | Yes, one skatepark |
| 6 | [Fighting games](#6-fighting-games-2d-3d-platform-fighter) | 1–3 min rounds, 20–120 min sittings | Premium plus character DLC, battle pass | 4/5 | Yes, 2D with a bot ladder and rollback |
| — | [Volatile facts](#volatile-facts-as-of-oct-2026--verify-before-relying) | — | — | — | Check before quoting numbers |

## How to use these playbooks

- Copy the core loop into `contract.json → loops[]`. Set `meta.genre` to `racing`, `sports` or `fighting` and `meta.subgenre` to the playbook slug. Set `meta.platforms`, `meta.input` (`gamepad`, `mouse_keyboard`, plus `other` for wheels and arcade sticks) and `technical.multiplayer` (`none`, `local`, `async` or `realtime`).
- Turn the starter feature list into P0 `features.json` entries with `gs.py feature add`. Each acceptance criterion maps to `unit`, `playthrough` or `replay` gate evidence.
- Mechanic category labels used here: combat, movement & traversal, competition, progression & upgrade, economy & resources, collection & randomness, social & competition, UX automation. Resolve them against the `mechanics-codex` taxonomy with `gs.py kb "<mechanic>" --skill mechanics-codex`.
- Read the "Platform notes" part of each playbook before choosing a platform. Input devices change the design more in these genres than in any other. For general input and performance tiers see `platform-targets`. For store pages and builds see `pc-web-release` and `console-pathway`.
- KPI statements are qualitative unless sourced. Premium games track attach rate, completion, review score and refund rate more than D1 and D30.

## 0. Shared foundations

### 0.1 Vehicle handling models: arcade, simulation and a simplified tyre model
Handling sits on a line from "steer and drift" to "solve the tyre". Choose the point on the line first, then build the minimum model that reaches it.

| Model | What it simulates | Typical use | Cost |
|---|---|---|---|
| Arcade (kinematic plus drift state) | Speed along a heading, a steer-rate limit, a drift state that adds yaw and a boost on exit | Arcade and kart racers | Low. Tuning is by feel |
| Semi-sim (rigid body plus simplified tyres) | Mass, four tyre contact patches, slip, weight transfer, aero drag | Sim-cade racers, most PC racers | Medium. Needs a fixed timestep |
| Full sim | Suspension geometry, tyre temperature and wear, differential and engine maps, fuel | Dedicated sim racing | High. Needs force feedback and real data |

**Simplified tyre model.** Lateral force from each tyre is a function of slip angle α, the angle between where the wheel points and where it moves. A common curve shape (the "magic formula" family) is:

```
Fy = Fz · μ · sin( C · atan( B·α − E · (B·α − atan(B·α)) ) )
Starter values: B = 10, C = 1.5, E = 0.9, μ = 1.1 (road tyre)  (estimates, tune by feel)
Peak grip near α ≈ 6–10°. Past the peak force falls: that is understeer or oversteer.
```

A simpler alternative for agent-built prototypes is a clamped linear model: `Fy = clamp(Cα · α, −μ·Fz, +μ·Fz)`, with a friction circle so braking and cornering share one budget: `sqrt(Fx² + Fy²) ≤ μ·Fz`.

**Worked example (my arithmetic).** A 1,200 kg car at 30 m/s with μ = 1.2 can reach about 1.2 × 9.81 = 11.8 m/s² lateral acceleration. The tightest steady corner is r = v² / a = 900 / 11.8 ≈ 76 m. Weight transfer in a corner of 8 m/s² with centre-of-gravity height 0.5 m and track width 1.6 m is ΔFz = m·a·h / t = 1,200 × 8 × 0.5 / 1.6 = 3,000 N moved to the outside tyres. Because grip is not linear in load, this loss on the inside tyre costs more than the outside tyre gains. That is the physical reason cars slide at the limit.

Rules for building it:
- Run vehicle physics at a fixed step of 120 Hz or higher (60 Hz at minimum for arcade) and decouple it from rendering. Sub-step the wheel solver if the car is fast.
- Provide a data file per car: mass, wheelbase, centre-of-gravity height, power curve, gear ratios, tyre B/C/E/μ, drag. No magic numbers in code.
- Add speed-sensitive steering lock and a steering-assist layer (counter-steer assist, stability control) as toggles. Assists are how one model serves both casual and expert players.
- Test with scripted inputs: full-throttle straight (top speed within 2% of the data), skid-pad circle (lateral g within 5% of μ), 100 km/h brake test (distance within 5% of the formula v² / 2μg).
- Ghost laps and replays need determinism (see §0.4 and `game-architecture`).

### 0.2 Catch-up mechanics and fairness
Catch-up keeps the pack together so the last player still has a race. It also breaks trust if it is hidden or too strong.

| Mechanic | How it works | Fairness risk |
|---|---|---|
| Rubber-banding (AI speed scales with gap to the player) | AI top speed ± a few percent by distance | Feels like cheating if the player is punished for being fast |
| Slipstream / draft | Reduced drag behind a car | Fair and skill-based. Prefer this |
| Position-weighted items | Better items for trailing racers | Fair if odds are public and bounded |
| Boost on recovery or drift | Reward skilled cornering | Fair, but rewards skilled players more |
| Blue-shell-style leader attack | Targets first place | High frustration. Use a warning and a counter |

Procedure:
1. Cap total catch-up at about ±5–10% speed or equivalent. Anything above makes the leader's skill irrelevant (estimate; test with bots).
2. Apply AI catch-up on a gap measured in seconds, not metres, so it scales with speed.
3. Never rubber-band against the player in a time trial or ranked online race.
4. Give the leader a defence (shield, dodge window) for any item that targets them.
5. Measure with bots at three skill levels: the skill gap in finishing position should stay above 1.5 places on average over 100 races. If it falls below, catch-up is too strong.
6. Show the odds table in the pause menu or a codex. Players forgive random items they can read.

### 0.3 Sports AI
Sports AI has three layers. Build and test them separately.

```
Team layer      formation, roles, pressing / zonal rules, set plays      (updates 2–5 Hz)
Agent layer     utility scoring: pass, shoot, dribble, mark, support run (updates 10–20 Hz)
Motion layer    steering (seek, arrive, separation), animation, collisions (every tick)
```

- **Formation as data.** Each role has a home position and a rule for shifting by ball position (for example, 30% of the ball's offset). A formation file plus a shift function covers most behaviour.
- **Utility scoring.** Each option gets a score from inputs (distance to goal, pass lane open, defender distance, fatigue). Pick the best score plus noise. Tune the noise per difficulty.
- **Difficulty by perception, not stats.** Raise reaction delay (150–400 ms, estimate), position error and pass-accuracy variance on easy modes. Avoid giving harder AI extra speed or free possession. Players detect the "cheating" feel within a match.
- **Fixed tick and seeded RNG** so a match replays exactly. Log inputs as `(tick, player, input)`.
- **Test with simulation.** Run 1,000 bot-versus-bot matches per build. Check goals per match against the contract band (for football, 2–3.5 total goals is typical of real matches; set your own), possession balance near 50% for mirrored teams, and no stuck players.
- **Referee and rules** are a separate module (offside, fouls, advantage). Keep it data-driven.

### 0.4 Frame data and rollback netcode
Fighting games are discrete, frame-exact games, usually at 60 frames per second (one frame is 16.67 ms).

```
Move timing      startup (frames before the hit is active) · active · recovery
Frame advantage  on block = defender's stun left − attacker's recovery left
                 Example: stun 14, attacker recovery remaining 9 → attacker is +5. 
                 A 4-frame jab then links if the gap is under 4 frames.
Frame trap       a gap of a few frames between hits that looks open but punishes a button press
```

**Delay-based netcode** waits for the remote input, so latency becomes input lag. **Rollback netcode** runs the game immediately with a prediction of the remote input, and when the real input arrives it rewinds to that frame and re-simulates. Requirements:
1. A fully deterministic sim: fixed step, seeded or integer RNG, no float-order dependence, no wall-clock reads (see `strategy.md` §0.3 and `game-architecture`).
2. A cheap save/restore of the whole sim state (keep it small, under a few hundred KB, so you can store 8–12 frames).
3. Re-simulating up to N frames within one render frame. Budget: the sim must run N+1 steps in under 16.67 ms. If a step costs 1 ms, 8 rollback frames fit comfortably.
4. Visual and audio effects decoupled from the sim, so a rollback does not replay a sound or a particle twice.
5. A small input delay (often 1–3 frames, estimate) plus a rollback window (commonly about 7–8 frames, estimate). Beyond the window, stall or drop.
6. Desync detection: hash the sim state every few frames and compare between clients.

For ratings, matchmaking and integrity see `skills/genre-playbooks/references/competitive-pvp.md` §0. A sim-core with a replay file is also the fastest way to build a bot ladder and a training mode. See `multiplayer-backend`.

### 0.5 Input buffers and motion inputs
- **Input buffer.** Store the last 3–6 frames of presses, so a button pressed slightly early still fires when the character can act. Fighters commonly use roughly 3–8 frames (estimate; tune per game). Longer buffers hide timing errors and make combos easier.
- **Motion inputs.** A quarter-circle forward is down, down-forward, forward then a button. Give each step a lenient window (about 10–16 frames for the whole motion, estimate) and accept sloppy diagonals.
- **Simultaneous opposing directions (SOCD).** Decide what happens when left and right (or up and down) are held together. Common choices are neutral or last-input-wins. Pick one, document it, and apply it equally on keyboard and pad.
- **Negative edge and release inputs.** Decide whether releasing a button can trigger a move.
- **Simplified control schemes.** Optional "modern" layouts map specials to single buttons. If offered online, label them so a match can be fair. Keep the sim identical; only the mapping changes.
- **Input display and frame step** in training mode are required for debugging and for testers.
- **Gamepad and keyboard.** Support remapping, a dead zone setting and a hold-versus-toggle option. Test d-pad, stick and hit-box (digital) layouts. See `platform-targets`.

## 1. Arcade racing

### Definition and player fantasy
Fast, forgiving cars on stylised tracks. Drift through corners, chain boosts and weave through traffic. The fantasy is being *a driver who never fails to look cool*: speed, spectacle and a quick restart.

### Core loop
```
pick car + track → race 2–4 min (drift, boost, overtake) → position and points
  → unlock cars, tracks, parts → next race or event → championship
```

### Meta loops
- **Career or event ladder.** Cups, tiered championships and one-off challenges with star ratings.
- **Garage and tuning.** Upgrade parts, paint, decals. Light tuning only.
- **Time trial and ghosts.** Compare against friends and the world.
- **Open-world variant.** Roam, find events and photo spots. Larger content cost.
- **Online lobbies and seasonal events.**

### Session profile
Estimate: 20–60 minute sittings on PC and console, with races of 2–5 minutes. Restarts must take under 5 seconds. Couch play and quick online rooms are common.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Drift into boost | movement & traversal | Core skill. Tune the drift entry angle and boost reward together (§0.1) |
| Slipstream | competition | Fair catch-up. See §0.2 |
| Traffic and near-miss rewards | movement & traversal | Reward risk. Keep traffic readable at speed |
| Nitro / boost meter | progression & upgrade | Fills from skilled play. Cap boost speed gain |
| Track shortcuts and branching routes | movement & traversal | Rewards route knowledge |
| Ghost lap and rewind | UX automation | Rewind lowers frustration. Mark rewound runs on leaderboards |
| Car classes and PP-style rating | progression & upgrade | Keeps races fair across a catalogue |

### Monetisation model and typical mix
Mostly premium purchases with optional DLC car or track packs. Free-to-play versions use car currencies and passes, which need loot-box and offer-cadence care (see `skills/genre-playbooks/references/rpg-gacha.md` §0.3). Licensed cars carry fees and approval steps that dominate cost. The `critic` agent should audit any pay-to-win upgrade path.

### KPI expectations
Qualitative. Premium racers track completion of the first championship, review score, refund rate within two hours of play, and weekly active online lobbies. Time-trial leaderboards and shared ghosts are cheap long-tail retention drivers.

### Retention drivers
Mastery of a handful of tracks. Leaderboard and friend ghosts. Car collection. Seasonal events. Photo mode. Mod and livery sharing if supported.

### Content pipeline and production scope (estimates)
Tracks are the expensive asset: design, art, lighting, AI lines and test laps. A small team can ship about 8–12 tracks and 15–25 cars as a vertical slice plus launch set. Licensing real cars multiplies calendar time. Procedural track pieces help but need a solver check (see `procedural-generation` and `level-design`).

### Reference titles
- *Ridge Racer* (Namco): drift-led arcade racing.
- *Burnout* series (Criterion): crash and takedown spectacle.
- *Need for Speed* series (EA): street racing with tuning.
- *Forza Horizon* series (Playground Games): open-world sim-cade.
- *Horizon Chase* (Aquiris): retro arcade homage.
- *Wreckfest* (Bugbear): contact-heavy racing and demolition.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| The car feels good within 30 seconds of the first race | Handling is floaty or the drift has no clear rule |
| Restarts are instant and tracks have memorable landmarks | Tracks blur together and loading is slow |
| AI is fair and the player can see why they lost | Rubber-banding punishes a lead (§0.2) |
| Each car feels different | Cars are cosmetic reskins of one model |
| A strong audio mix gives speed cues | Engine sound and music mask each other |

### Innovation vectors
- Rewind and assist options that let casual players finish.
- Procedural tracks with solver-checked racing lines.
- Photo and livery sharing as a social loop.
- Cross-play lobbies between PC and console.
- Weather and time-of-day as route variants.
- Short roguelite-style race runs.

### Agent-buildability: 3/5
**Why mid:**
- Track data, AI lines, lap timing, leaderboards and unit-tested physics curves suit agents.
- Bots can drive laps for balance and regression.

**Why not higher:**
- Car feel, camera, speed sensation and audio need human hands on a controller.
- Art and licensed content are the cost drivers.

### Starter feature list (P0 vertical slice: one car class, three tracks, AI)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Fixed-step vehicle model with data-driven car file (gameplay) | Top speed within 2% of data. Skid-pad lateral g within 5% of μ |
| 2 | Drift state with boost on exit (gameplay) | Entry angle and boost values come from the tuning table. A bot test confirms drifting beats grip on the tuning track |
| 3 | Track with spline, checkpoints and lap timer (gameplay) | Cutting a checkpoint is rejected. Lap time accurate to 1 frame |
| 4 | AI drivers on racing lines, three skill levels (gameplay) | Finishing-position gap between levels above 1.5 places over 100 bot races |
| 5 | Catch-up capped at the contract value (gameplay) | A sim shows the cap never exceeds the limit. Disabled in time trial |
| 6 | Instant restart and rewind option (ux) | Restart under 5 seconds. Rewound runs are flagged |
| 7 | Ghost recording and playback (tech) | Same inputs reproduce the same lap time within 1 frame |
| 8 | Car select with 4 cars and 3 upgrade slots (meta) | Upgrades change the named stats. Class rating recomputes |
| 9 | Pause menu with assists, remapping and camera options (ux) | Remaps persist. Assist toggles change the model as documented |
| 10 | Local leaderboard and ghost list (meta) | Sorted by time. Ghost loads on selection |
| 11 | Audio: engine pitch by RPM and speed cue mix (audio) | Engine layer follows RPM within 50 ms. Mix passes `audio-direction` checks |

### Platform notes
- **PC.** Support wheels (force feedback), pad and keyboard. Offer uncapped frame rates and a graphics options menu with shader pre-compilation to avoid stutter. Steam features: leaderboards, workshop for liveries (`pc-web-release`).
- **Console.** Pad-first. Use trigger vibration and haptics for traction cues if the platform has them. Target a stable 60 fps. Certification covers suspend/resume and accounts (`console-pathway`).
- **Web.** Browser builds work for simple arcade racers. Keep assets small, use a fixed step and handle keyboard focus. Instant load beats fidelity.
- **Mobile.** Tilt and touch steering suit auto-accelerate designs. See `skills/genre-playbooks/references/competitive-pvp.md` (mobile racing). Mobile monetisation is more ad- and pass-led; PC and console are premium-led.

## 2. Simulation racing

### Definition and player fantasy
A faithful model of real cars, tyres, tracks and series. The fantasy is *being a real driver*: lap-time discipline, car setup, race craft and consequence for errors.

### Core loop
```
choose car + setup → practice (learn the track, tune) → qualify → race (tyre, fuel, pit strategy)
  → results and licence / rating → next event
```

### Meta loops
- **Licence and safety rating.** A driver rating and a clean-driving score gate access to online series.
- **Career or league.** Season of races, teams, contracts.
- **Setup sharing.** Players publish setups.
- **Official esports or leagues** with rules and stewards.
- **Subscription content and DLC** (cars, laser-scanned tracks).

### Session profile
Estimate: 10–60+ minutes per race, long practice sessions, and sittings of 1–3 hours. Players invest in wheels, pedals and rigs. Race scheduling (fixed start times) is common for online series.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Tyre model with temperature and wear | movement & traversal | §0.1. Wear creates strategy |
| Fuel, pit stops, damage | economy & resources | Resource management on top of driving |
| Setup editor (aero, springs, gearing) | progression & upgrade | Expose with plain-language helpers |
| Force feedback | UX automation | Main feel channel. Needs a tuned signal, not raw physics output |
| Rating and safety rating | social & competition | Reward clean racing. See `competitive-pvp.md` §0.1 |
| Flags and penalties | competition | Rules module, data-driven |
| Replays and telemetry | UX automation | Compare laps and find lost time |

### Monetisation model and typical mix
Premium base game plus paid car and track packs, or a subscription. Hardware bundles are common. Licensing and laser-scanned tracks are costly and drive pricing. Avoid loot boxes. The audience is price-aware and values content accuracy.

### KPI expectations
Qualitative. Track hours per player, online-series participation, content-pack attach rate and review score. The audience is smaller than arcade racing but spends more per player.

### Retention drivers
Mastery and lap-time progression. Rating and licence climb. Scheduled online races and leagues. Constant content updates. Hardware investment as sunk cost.

### Content pipeline and production scope (estimates)
The most data-heavy racing genre: car physics data, tyre data, track scans and audio recordings per car. A realistic indie scope is one racing discipline (for example, one GT class and 3–5 tracks). A full platform is a multi-year, large-team effort. Online infrastructure and stewarding add backend cost (`multiplayer-backend`).

### Reference titles
- *iRacing* (iRacing.com): subscription online sim with licences.
- *Assetto Corsa* / *Assetto Corsa Competizione* (Kunos): PC sim with strong modding (the first).
- *rFactor 2* (Studio 397).
- *Gran Turismo* series (Polyphony Digital): console sim-cade with a collector slant.
- *Forza Motorsport* series (Turn 10).
- *Automobilista 2* (Reiza).

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Force feedback is clear and trusted | Force feedback is noisy or clipping |
| Online racing is clean with a good rating system | Online lobbies are full of ramming and no consequence |
| Assists and presets welcome newcomers | A wall of setup sliders with no guidance |
| The sim runs smoothly on mid-range PCs and consoles | Frame pacing issues break the feel |
| Content is accurate and regularly added | Thin content at launch with no roadmap |

### Innovation vectors
- Adaptive coaching overlays (braking points, racing line) that fade out with skill.
- AI drivers trained on real driver behaviour for believable offline racing.
- Cloud setup sharing with telemetry comparisons.
- Accessible entry modes (pad-first physics tuning).
- Cross-platform leagues.
- VR support as a premium option.

### Agent-buildability: 2/5
**Why low:**
- Physics fidelity is judged by feel and by real-world data. Neither is verifiable by client gates alone.
- Force feedback and wheel support need hardware testing.
- Licences and content accuracy are business and data work.

**What agents do well:**
- Telemetry tooling, setup-editor UI, rating and licence logic, replay and race-control modules, test harnesses with scripted laps.

### Starter feature list (P0 vertical slice: one car, one track, practice plus race)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Fixed-step vehicle with tyre slip model (gameplay) | 120 Hz step. Skid-pad and brake tests within tolerance (§0.1) |
| 2 | Tyre temperature and wear (gameplay) | Grip falls with wear by the data curve. Unit tested |
| 3 | Fuel use and pit-stop procedure (gameplay) | Fuel burn matches data. Pit time follows rule values |
| 4 | Basic setup editor, 6 parameters (ui) | Each parameter changes the named model value. Reset to default works |
| 5 | Force-feedback output with gain and filter settings (ux) | Signal clamped and never saturating on the test lap. Gain persists |
| 6 | Wheel, pad and keyboard input with calibration (input) | Calibration persists. Dead zones adjustable |
| 7 | AI field of 12 on a data-driven line, three levels (gameplay) | AI laps within the band of the reference lap. No stuck cars in 100 races |
| 8 | Flags, track limits and penalties (gameplay) | Cutting a corner by the rule triggers the stated penalty |
| 9 | Replay and telemetry trace (tech) | Replay is deterministic. Speed, throttle and brake traces overlay two laps |
| 10 | Rating or safety score after each race (meta) | Score follows the formula. Contact lowers it |

### Platform notes
- **PC.** Home of sim racing. Wheel and pedal support, triple screens, VR, mods, telemetry export and high frame rates. Support common wheel drivers and test force feedback on at least two wheel families. See `platform-targets`.
- **Console.** Pad-first physics tuning, a smaller wheel audience, and platform-specific wheel support lists. Haptic triggers help traction feel. Certification affects online and licensing (`console-pathway`).
- **Web.** Not suited to full sims. A browser time-attack toy is possible but fidelity is limited.
- **Mobile.** Rarely a true sim. Treat it as arcade. Business model is subscription or premium on PC, pass and cosmetics on mobile.

## 3. Kart racing

### Definition and player fantasy
Cartoon karts, short tracks, items and drift boosts. The fantasy is *a party where anyone can win*: chaos, comebacks and friendly rivalry.

### Core loop
```
pick character + kart → race 2–3 min (drift boost, collect items, use items)
  → points over a cup of 4 races → cup result → unlock next cup, kart parts
```

### Meta loops
- **Cups and engine classes.** Grand prix of 4 tracks across speed classes.
- **Battle mode** (balloon or arena).
- **Time trial with ghosts.**
- **Online rooms and tournaments.**
- **Unlockables.** Characters, karts, wheels, gliders.

### Session profile
Estimate: 2–4 minute races, cups of 8–15 minutes, party sittings of 30–90 minutes. Couch co-op with split screen is a core use on console and PC.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Item boxes with position-weighted odds | collection & randomness | §0.2. Publish the table |
| Drift mini-turbo | movement & traversal | Charge levels by drift duration |
| Slipstream and coins/speed pickups | movement & traversal | Rewards clean lines |
| Hit recovery and invulnerability frames | combat | Prevents chain-hit frustration |
| Leader-attack item | competition | Needs a warning and a counter |
| Split screen | social & competition | Needs performance headroom for 4 views |
| Track hazards and shortcuts | movement & traversal | Rewards route knowledge |

### Monetisation model and typical mix
Premium with DLC tracks on console and PC. Mobile versions are free-to-play with currencies and passes (see `competitive-pvp.md` for mobile racing). Licensed characters add fees and approval. Keep gambling-like item crates out of premium titles.

### KPI expectations
Qualitative. Premium: completion of the first cup, review score, local multiplayer usage and DLC attach rate. Free-to-play: see the mobile racing section of `competitive-pvp.md`.

### Retention drivers
Social and couch play. Short cups. Unlock curve. Time-trial mastery and online rooms. Seasonal tracks.

### Content pipeline and production scope (estimates)
Roughly 12–16 tracks, 8–12 characters and 4–8 kart bodies for a launch set. Tracks are the main cost. Items need animation, effects and balance work. Lightweight enough that a small team can finish a solid slice.

### Reference titles
- *Super Mario Kart* and *Mario Kart* series (Nintendo): the template.
- *Crash Team Racing Nitro-Fueled* (Beenox).
- *Sonic & All-Stars Racing Transformed* (Sumo Digital): vehicle transformation.
- *Team Sonic Racing* (Sumo Digital): team play.
- *Mario Kart Tour* (Nintendo): the mobile free-to-play variant.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Items create comebacks without feeling unfair | A single item decides most races |
| Tracks teach shortcuts and have clear visual flow | Tracks are long and repetitive |
| Anyone can pick up the pad and play | Controls need expert drift knowledge |
| Local multiplayer is smooth and readable | Four-way split screen drops frames |
| A clear unlock curve | Unlocks are gated behind grind or chance |

### Innovation vectors
- Items that are skill-based (aimed, deflectable).
- Team and co-op racing modes.
- Level editors with sharing.
- Accessibility: auto-steer, auto-drift and smart steering as assists.
- Road-trip or roguelite kart runs.
- Cross-play with party rooms.

### Agent-buildability: 4/5
**Why high:**
- Arcade physics, item tables, race logic and AI are testable with bots.
- Odds and catch-up are measurable by simulation (§0.2).

**Why not 5:**
- Track charm, item readability, camera and "feel" still need human iteration.

### Starter feature list (P0 vertical slice: 2 cups of 4 tracks, 8 racers)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Arcade kart model with steer, drift and boost (gameplay) | Drift tiers match the tuning table. Unit tested with scripted inputs |
| 2 | Item boxes with position-weighted table (gameplay) | Table loads from data. A 10,000-roll sim matches odds within 1% |
| 3 | Six items including one leader-attack with warning (gameplay) | Warning shown at least 2 s before impact. A counter exists |
| 4 | Hit recovery with invulnerability window (gameplay) | A racer cannot be hit twice within the window |
| 5 | 8 AI racers at three skill levels (gameplay) | Skill gap above 1.5 places over 100 bot races. Catch-up within cap |
| 6 | Cup mode with points and results (meta) | Points follow the table. Cup unlocks persist |
| 7 | Time trial and ghost (gameplay) | Ghost replays within 1 frame of the original |
| 8 | Two-player split screen (tech) | Holds target frame rate on the minimum-spec target |
| 9 | Auto-steer and auto-drift assist toggles (ux) | Assists change inputs only. Results are flagged |
| 10 | Character and kart select with stat display (ui) | Stats change the sim values shown |

### Platform notes
- **PC.** Local play with pads (Steam Input), and online rooms. Support keyboard sharing for two players only as a fallback. Offer resolution and frame-rate options.
- **Console.** The home of couch kart racing. Split screen, a stable 60 fps and instant join of extra controllers matter. Platform guests and profile handling are certification items (`console-pathway`).
- **Web.** Good fit for a light kart racer with shared-screen or a simple online room. Keep the bundle small.
- **Mobile.** One-thumb steering, auto-accelerate, short races and free-to-play. See `competitive-pvp.md`. Premium on PC and console, pass-led on mobile.

## 4. Team sports simulation

### Definition and player fantasy
Control a team in a real sport (football, basketball, American football, ice hockey, baseball) with licensed or fictional clubs. The fantasy is *being the star or the manager*: scoring the winner, building a dynasty, climbing the table.

### Core loop
```
choose team → play match 10–25 min (pass, shoot, defend, set plays)
  → result and stats → season / career progression → upgrades, transfers, squad
```

### Meta loops
- **Career or franchise mode.** Seasons, contracts, scouting, finances.
- **Squad-building card mode** (ultimate-team style). Collect players, build a squad, play online.
- **Online leagues and ranked divisions.**
- **Annual roster and rules updates.**
- **Creation tools.** Custom players, teams and kits.

### Session profile
Estimate: 10–25 minute matches (shorter in arcade variants), sittings of 30–120 minutes. Annual release cycles tie into the real sporting calendar.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Player control with context-sensitive buttons | combat | One button, several actions by context. Tune the context rules |
| Team AI and formations | competition | §0.3 |
| Stamina, form, injuries | economy & resources | Drives rotation and squad depth |
| Set plays and tactics editor | progression & upgrade | Data-driven plays |
| Transfer and contract market | economy & resources | Needs economy design (`economy-design`) |
| Squad cards with rarity | collection & randomness | Paid randomness. Apply compliance (`legal-ethics`) |
| Replays, broadcast presentation | UX automation | A large share of perceived quality |

### Monetisation model and typical mix
Annual premium purchase plus a card-pack mode, which draws most live revenue and most regulatory attention. Some titles are free-to-play (arcade or card-led). Licences from leagues and player unions are a major cost and gate. Review loot-box law per market before shipping packs (see `rpg-gacha.md` §0.3).

### KPI expectations
Qualitative. Annual titles track sell-through, season attach, online-ranked participation and card-mode spend. Review scores often hinge on gameplay changes year to year and on server stability.

### Retention drivers
Real-world sporting calendar. Squad building and chasing rare players. Online division rank. Career mode narrative. Community leagues and clubs.

### Content pipeline and production scope (estimates)
Very large: animation (thousands of clips, motion capture), player likenesses and data, stadiums, commentary, licences. Even a fictional-league indie sports game needs a deep AI layer and animation set. Realistic indie scope is an arcade or simplified sport (for example, 5-a-side football or 3-on-3 basketball) with fictional teams.

### Reference titles
- *EA Sports FC* series (formerly *FIFA*): football, annual.
- *eFootball* (Konami): free-to-play football.
- *NBA 2K* series (Visual Concepts): basketball.
- *Madden NFL* series (EA): American football.
- *NHL* series (EA): ice hockey.
- *Rocket League* (Psyonix): vehicle football, an arcade-sport design.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Passing, shooting and defending feel responsive | Input delay or animation lock makes control feel late |
| AI teammates and opponents behave sensibly | AI stands still or exploits repeat tactics |
| Modes beyond a single match (career, online) are polished | Features copied forward year to year with no gains |
| Servers are stable for online play | Online lag decides matches |
| Licences give authenticity | Fictional teams with weak identity |

### Innovation vectors
- Simplified arcade sports with strong physics hooks.
- Co-op and 3v3 online instead of 11v11.
- Tactics-first managers with real-time match view.
- Procedurally generated fictional leagues with stories.
- Player-created leagues and clubs.
- Accessible control schemes.

### Agent-buildability: 2/5
**Why low:**
- Animation depth, licences and live service dominate the work.
- "Feel" of player control is judged by humans.

**What agents do well:**
- Match-sim and season-sim modules, tactics and formation data, career-mode economy, bot-versus-bot tests (§0.3), stat tracking and UI.

### Starter feature list (P0 vertical slice: 5-a-side fictional football)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Fixed-tick match sim with ball physics (gameplay) | Deterministic. Same inputs give the same score over 1,000 replays |
| 2 | Player control with pass, shoot and tackle (gameplay) | Pass accuracy and power follow formula tables. Input-to-action latency under 100 ms |
| 3 | Formation data with role shift by ball position (gameplay) | Formation file loads. Role positions follow the shift rule |
| 4 | Utility AI for pass, shoot, mark and support run (gameplay) | Mirrored bot match: possession within 45–55% over 1,000 matches |
| 5 | Three difficulty levels by reaction and error (gameplay) | Win rate of hard over easy above 80% for a fixed bot |
| 6 | Referee module with out of play and fouls (gameplay) | Rule table unit tested. Restarts correct |
| 7 | Stamina and substitutions (gameplay) | Stamina follows the curve. Sprint speed falls as defined |
| 8 | 8-team league with fixture list and table (meta) | Fixtures round-robin. Table sorts by points, goal difference |
| 9 | Replay camera and goal replay (ux) | Replay uses logged inputs. Skip works |
| 10 | Local two-player and online room stub (tech) | Two pads on one screen. Online uses the same sim |

### Platform notes
- **PC.** Pad is standard. Support keyboard remapping, ultrawide cameras and high frame rates. Mod communities patch kits and rosters, so decide on mod support early. Anti-cheat matters for card and ranked modes.
- **Console.** The main platform. Platform-holder licence rules for online, matchmaking and microtransactions apply (`console-pathway`). Haptics and adaptive triggers can carry feel.
- **Web.** Simple arcade sports and managers work well in a browser. Real-time online play needs a server.
- **Mobile.** Touch controls, short matches and card-collection business models. See `competitive-pvp.md` (competitive sports).

## 5. Extreme sports / skate

### Definition and player fantasy
Skateboarding, snowboarding, BMX, surfing, wingsuit or similar. Chain tricks, land clean and flow through a space. The fantasy is *self-expression through movement*: style, flow and mastery of a physical vocabulary.

### Core loop
```
enter spot / course → trick, grind, manual, gap (build combo, hold balance)
  → land or bail → score, goal, or run complete → unlock gear, spots, goals
```

### Meta loops
- **Goals and challenges.** Collect items, hit score targets, gaps and lines.
- **Career with sponsors and magazines or video-part goals.**
- **Park or course creator** with sharing.
- **Online score attack and session modes.**
- **Cosmetic and gear unlocks.**

### Session profile
Estimate: 2-minute scored runs or free-roam sessions, sittings of 30–90 minutes. Free skate with no timer is a common comfort mode.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Trick input vocabulary (flick, stick, button) | movement & traversal | Map inputs to a trick grammar, see below |
| Combo chain with multiplier | progression & upgrade | Grind, manual and air connect. Bail resets |
| Balance meters on grind and manual | movement & traversal | A small skill check that keeps combos honest |
| Spot and park design | movement & traversal | Lines matter more than size (`level-design`) |
| Replay and clip tools | UX automation | Sharing is a social loop |
| Bail and ragdoll physics | movement & traversal | Funny, but must reset quickly |
| Level editor | social & competition | Creator content extends life |

**Trick grammar (worked example).** Define a trick as `(input direction) × (rotation) × (grab or flip)` and score it as `base × (1 + 0.1 × combo_length)` with a diminishing return on repeats (for example, 100% first use, 50% second, 25% third). Data-drive it so designers can balance scores in a table.

### Monetisation model and typical mix
Premium with DLC packs (spots, gear, licensed brands and soundtrack). Licensing brands and music is a notable cost. Free-to-play mobile versions use ads and gear currencies. Real brands in gear need approval.

### KPI expectations
Qualitative. Premium: completion of the first career goals, review score, replay and clip shares, DLC attach rate. Community-made parks extend lifetime.

### Retention drivers
Flow and mastery. Goals and lines. Creator tools and shared parks. Replay sharing. Cosmetic customisation. Soundtrack.

### Content pipeline and production scope (estimates)
Spots and parks (art, collision and line design), trick animations, character customisation, audio and soundtrack licences. A vertical slice is one park, 40–60 tricks and a combo system. A launch set might be 6–10 spots.

### Reference titles
- *Tony Hawk's Pro Skater* series (Neversoft, Activision): arcade skating with combo scoring.
- *skate.* series (EA): flick-stick trick input and a sim-leaning feel.
- *Skater XL* (Easy Day Studios): twin-stick realistic skating with strong mods.
- *OlliOlli* series (Roll7): 2D skating with a precision score focus.
- *SSX* series (EA): arcade snowboarding.
- *Riders Republic* (Ubisoft): open-world mass sports.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Controls are learnable in 10 minutes and deep after 10 hours | Input mapping is arbitrary and unreadable |
| Spots are built for lines and flow | Spots are empty or confusing |
| Bails reset in under a second | Long bail animations break flow |
| Clip sharing is simple | No replay or share tooling |
| Audio and music reinforce rhythm | Poor landing and grind audio feedback |

### Innovation vectors
- Procedural spot generation with line analysis.
- Physics-driven trick systems with fewer canned animations.
- Co-op and multiplayer sessions with shared score.
- Player-created content and marketplace.
- Rhythm-assisted trick scoring.
- Accessible assists for balance and landing.

### Agent-buildability: 3/5
**Why mid:**
- Trick grammar, scoring, goal systems, level data and replay tools are structured and testable.
- Bots can attempt lines for solvability.

**Why not higher:**
- Animation blending and physics feel need human tuning with a pad.
- Art, audio and brand licences.

### Starter feature list (P0 vertical slice: one skatepark)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Character controller with push, ollie, landing (gameplay) | Jump height and airtime match the tuning table. Unit tested |
| 2 | Trick grammar and 30 tricks from data (gameplay) | Input maps to the named trick. Scores come from the table |
| 3 | Grind and manual with balance (gameplay) | Balance drifts per the curve. Failure causes a bail |
| 4 | Combo multiplier with repeat penalty (gameplay) | Score follows `base × (1 + 0.1 × length)` with repeat decay |
| 5 | Bail and fast reset (ux) | Reset under 1 second. No input lock beyond it |
| 6 | One park with 10 goals (content) | A scripted bot completes each goal. Goal state persists |
| 7 | Replay recording and clip export (tech) | Replay is deterministic. Clip saves to disk |
| 8 | Camera with follow and look options (ux) | Camera never clips terrain on the test line |
| 9 | Gear and cosmetic unlocks (meta) | Unlocks apply to the model and persist |
| 10 | Audio: wheels by surface, grind, landing (audio) | Each event triggers its cue within 50 ms |

### Platform notes
- **PC.** Pad is primary, with keyboard fallback. Mods and creator tools do well. Support high frame rates for responsiveness.
- **Console.** Pad-first. Clip capture buttons integrate with the platform share features. Haptic feedback on landings helps.
- **Web.** Good for 2D or simple 3D trick games. Keep physics light and load times low.
- **Mobile.** Touch-gesture tricks and endless-runner skaters. Ad- and cosmetic-led business model. See `action-arcade-roguelite.md` for runner designs.

## 6. Fighting games (2D, 3D, platform fighter)

### Definition and player fantasy
Two (or more) characters fight in short rounds using moves with exact frame timing. Sub-types: 2D fighters (side-on, motion inputs), 3D fighters (sidestep, limb-based buttons) and platform fighters (stocks and percent damage, ring-out). The fantasy is *a duel of reads*: outthinking the opponent, executing under pressure and a character that expresses you.

### Core loop
```
pick character → round 60–99 s or stock match (neutral → attack → defend → punish)
  → win/loss → rank or session continues → learn, lab (training mode), return
```

### Meta loops
- **Ranked ladder and lobbies.** Rating, leagues, rematches.
- **Training and trials.** Combo trials, frame data display, tutorials.
- **Story or arcade mode.** Single-player draw.
- **Character roster and seasons.** New characters, balance patches.
- **Tournaments and replays.** Community events and replay sharing.
- **Cosmetics and passes.**

### Session profile
Estimate: 1–3 minute rounds or 3–5 minute stock matches, sittings of 20–120 minutes. Rematch speed matters. Training mode is a core place players spend time.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Frame data and hit/hurtboxes | combat | §0.4. Source of truth for balance |
| Neutral, block, throw triangle | combat | Strike, block and throw beat each other |
| Combos, links and cancels | combat | Execution requirement. Tune difficulty with buffers (§0.5) |
| Meters (super, drive, burst) | progression & upgrade | A comeback and resource system |
| Rollback netcode | social & competition | §0.4. Make it the default for online |
| Training mode with frame step | UX automation | Required for learning |
| Platform-fighter percent and stocks | combat | Knock-back grows with percent. Edge-guarding and recovery matter |
| Ratings and matchmaking | social & competition | See `competitive-pvp.md` §0.1–0.2 |

### Monetisation model and typical mix
Premium base game plus character DLC and season passes, with cosmetics and battle passes. Free-to-play fighters exist but are rarer. Avoid pay-to-win character locks on ranked play, or give every character in a free rotation. Esports and community events are a marketing channel rather than a revenue line.

### KPI expectations
Qualitative. Premium: online match counts, ranked participation, training mode usage, DLC character attach rate and review sentiment about netcode. The core audience is small but loyal, and a healthy casual funnel (story, simple controls) widens it.

### Retention drivers
Mastery and rank. Character attachment. Community events and tournaments. Balance patches that change the metagame. Rematch loops. Content seasons.

### Content pipeline and production scope (estimates)
Characters dominate: each needs animation, hit and hurtboxes, move lists, audio and balance work. A roster of 8–12 at launch is common for small teams (estimate). 2D hand-drawn sprites are expensive per frame. 3D models reuse a skeleton. A solid vertical slice is 2 characters, 1 stage, training mode and local versus.

### Reference titles
- *Street Fighter II* and later *Street Fighter* series (Capcom): the 2D template.
- *Guilty Gear* series (Arc System Works): anime 2D fighting.
- *Tekken* series (Bandai Namco): 3D fighting.
- *Virtua Fighter* series (Sega): 3D, no-frills mechanics.
- *Super Smash Bros.* series (Nintendo): platform fighter.
- *Rivals of Aether* (Dan Fornace): indie platform fighter.
- *Skullgirls* (Lab Zero): 2D with a strong training mode.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Rollback netcode with a clear connection indicator | Delay-based netcode makes online unplayable |
| Training mode shows frame data and records dummies | Players need an external site to learn |
| A fair, readable ruleset with clear hit feedback | Hit effects hide what happened |
| A balanced roster with regular, transparent patches | A dominant character for months without a response |
| A path for beginners (simple controls, tutorials) | Only experts can have fun |

### Innovation vectors
- Simplified control schemes alongside classic.
- Built-in coaching using frame-data overlays.
- Rollback for platform fighters with many players.
- AI opponents trained on player replays (ghost sparring).
- Cross-play across PC and consoles.
- Roguelite or party modes around the duel.

### Agent-buildability: 4/5
**Why high:**
- The game is a deterministic frame-by-frame state machine. Frame data, hitboxes and move lists are structured data.
- Unit tests and replays verify rules. A bot ladder balances the roster by simulation.
- Rollback needs deterministic design, which agents can enforce by architecture.

**Why not 5:**
- Hit feel, effects, animation timing, audio and character appeal need human judgement and hands-on play.
- Real-world netcode quality depends on field testing across networks.

### Starter feature list (P0 vertical slice: 2D, two characters, local plus rollback)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Fixed 60 Hz deterministic sim-core (tech) | Same inputs give identical state hash over 1,000 replays |
| 2 | Character state machine with frame data from file (gameplay) | Startup, active and recovery match the data table. Unit tested |
| 3 | Hitbox and hurtbox overlap with hitstop and blockstun (gameplay) | Frame advantage values match the table for each tested move |
| 4 | Input buffer and motion detection (input) | Buffer window and motion leniency come from config. Replays pass |
| 5 | Throw, block, strike triangle (gameplay) | Each beats the third by the rules. Throw tech window as specified |
| 6 | Combos with damage scaling (gameplay) | Scaling follows the table. A 10-hit test combo yields the expected damage |
| 7 | Meter and one super per character (gameplay) | Meter gains and spends per rule. Super is not buffered through blockstun if the rule forbids it |
| 8 | Training mode: dummy record/playback, frame step, input display (ux) | Frame step shows state each frame. Recorded dummy loops |
| 9 | Rollback netcode with desync hash check (tech) | Two clients with simulated 100 ms latency and 2% loss stay in sync. No desync in 10,000 frames |
| 10 | Bot opponent with three levels (gameplay) | Hard beats easy above 80%. Bot obeys the same rules and inputs |
| 11 | Replay save and load (tech) | Replay reproduces the match state hash |
| 12 | Remappable controls and simple-control option (ux) | Remaps persist. Simple mode uses the same sim |

### Platform notes
- **PC.** Strong fighting community. Support pads, arcade sticks and hit-box controllers, keyboard remapping, wired-connection guidance, SOCD handling (§0.5) and cross-play. Frame-rate lock at 60 for the sim. Steam networking and input services are available; see `pc-web-release`.
- **Console.** Pad and stick support. Cross-play is increasingly expected. Certification covers online rules and account handling (`console-pathway`). Dead zones and d-pad quality vary by pad, so allow button-based directions.
- **Web.** Possible for small 2D fighters with WebRTC or a relay. Browser timing jitter makes rollback harder. Keep the sim deterministic and test across browsers.
- **Mobile.** On-screen buttons limit execution, so mobile fighters use simplified inputs and auto-combos. The business model is gacha- or pass-led versus premium plus DLC on PC and console. See `competitive-pvp.md` (brawlers).

## Volatile facts (as of Oct 2026 — verify before relying)

- Steam charges a US$100 submission fee per product, and the revenue share is reported as 30% on the first US$10 million per game, 25% from US$10–50 million and 20% above that. The fee is from Valve's onboarding page. The tiers come from secondary reports and should be checked against Steamworks — [Steamworks onboarding](https://partner.steamgames.com/doc/gettingstarted/onboarding), [Neowin on the tiers](https://www.neowin.net/news/valve-introduces-new-revenue-share-tiers-for-steam-promising-bigger-cuts-for-studios/)
- Frame, buffer and rollback-window numbers in this file (input delay of 1–3 frames, rollback about 7–8 frames, buffers of 3–8 frames) are design estimates, not sourced figures. Test with your own netcode and players.
- Loot-box and paid-random regimes apply to card packs and crate-style modes in sports and racing games. Details and sources: `skills/genre-playbooks/references/rpg-gacha.md` volatile facts.
- Mobile racing, sports and brawler market figures are in `skills/genre-playbooks/references/competitive-pvp.md`.
- Platform certification, wheel-support lists and cross-play rules change often. Confirm in the vendor's current documentation before committing a platform list (`console-pathway`, `pc-web-release`).

## Related skills
- `mechanics-codex`: cards for every mechanic named above.
- `game-feel`: hit stop, screen shake, camera and input response.
- `gameplay-programming`: controllers, physics and state machines.
- `game-architecture`: sim-core plus presentation, determinism, rollback state.
- `multiplayer-backend`: rollback relays, lobbies, matchmaking and replays.
- `level-design`: tracks, skate spots and stages.
- `audio-direction`: engine, impact and crowd audio.
- `qa-testing`: bots, replay tests and soak runs.
- `balance`: frame-data tables, character and car balance.
- `platform-targets`: input devices, performance tiers and saves.
- `pc-web-release`: Steam and web release steps.
- `console-pathway`: console programmes and certification.
