# Simulation and Management Playbooks

Simulation and management games sell understanding and control of a system: build it, watch it run, find the bottleneck, fix it, scale it. Their home is PC (mouse, keyboard, large screens, long sessions), with strong console versions of the more accessible titles and mobile versions covered elsewhere. This file holds seven playbooks in a shared 14-part template plus a "Platform notes" part:

1. City builder
2. PC management / tycoon
3. Factory and automation
4. Life sim and farming (PC and console)
5. Job and vehicle sims
6. God games
7. Sports management

Five foundations come first because most playbooks rely on them: production chains and ratios, throughput and queues, agent simulations and their performance cost, information-dense UI, and save and load of large states. Simulation is the most agent-buildable family of PC genres (3–5/5) because the core is deterministic rules plus numbers, and an agent can test both with headless runs. The weak spot is feel: readable overlays, tooltips and pacing need human taste. Mobile tycoon, farming, life sim, home design and time management are in `idle-tycoon-sim.md`; this file does not repeat them. Colony sims (agent-driven survival) are in `survival-sandbox.md` §4. Market numbers live in the dated volatile-facts section.

## Contents

| § | Playbook | Session profile (estimate) | Primary monetisation | Agent-buildability | First project for an agent pipeline? |
|---|---|---|---|---|---|
| 0 | [Shared foundations](#0-shared-foundations) | — | — | — | Read first |
| 1 | [City builder](#1-city-builder) | 1–3 h sessions, 50–500 h total | Premium, DLC, mods | 4/5 | Yes, as a small grid city |
| 2 | [PC management / tycoon](#2-pc-management--tycoon) | 1–2 h, scenario-based | Premium, DLC | 4/5 | Yes |
| 3 | [Factory and automation](#3-factory-and-automation) | 2–4 h, deep focus | Premium, early access | 4/5 | Yes, the best slice for an agent |
| 4 | [Life sim and farming (PC / console)](#4-life-sim-and-farming-pc--console) | 30–90 min, one in-game day per sitting | Premium, DLC, cosmetics | 3/5 | Yes, a small farm |
| 5 | [Job and vehicle sims](#5-job-and-vehicle-sims) | 30 min–3 h, relaxed | Premium, DLC packs, vehicle packs | 3/5 | Yes, with one vehicle and one route |
| 6 | [God games](#6-god-games) | 1–2 h, experimental | Premium | 3/5 | Possible |
| 7 | [Sports management](#7-sports-management) | Seasons over weeks, 15–60 min per matchday | Premium, yearly releases, DLC | 4/5 | Yes, a data-driven league |
| — | [Volatile facts](#volatile-facts-as-of-oct-2026--verify-before-relying) | — | — | — | Check before quoting numbers |

## How to use these playbooks

- Copy the core loop into `contract.json → loops[]`. Set `meta.genre: "simulation"` and `meta.subgenre` to the playbook slug. Set `meta.platforms` (usually `windows`, `macos`, `linux`, plus `playstation`, `xbox`, `switch` where relevant) and `meta.input` (`mouse_keyboard`, `gamepad`). Set `technical.multiplayer` (`none`, `coop`, `async_share`).
- Turn the starter feature list into P0 `features.json` entries with `gs.py feature add`. Each acceptance criterion maps to `unit` or `playthrough` gate evidence (headless sim runs, state hashes, benchmark gates).
- Mechanic category labels: combat, build-craft, collection & randomness, progression & upgrade, economy & resources, time & energy, social & competition, exploration & traversal, live events, UX automation. Resolve them with `gs.py kb "<mechanic>" --skill mechanics-codex`.
- Platform differences (input, session, performance, business model) are in each playbook's "Platform notes" part. See also `platform-targets`, `pc-web-release` and `console-pathway`.
- KPI statements are qualitative unless sourced. Premium simulation is judged by reviews, wishlists, refund rate, hours played and expansion attach rate more than by D1 or D7.

## 0. Shared foundations

### 0.1 Production chains and ratios
A production chain turns raw inputs into products through machines or buildings. Each machine has a rate. The core design tool is the **ratio**: how many machines at each stage keep the next stage fed.

```
Machine rate          r = output_per_cycle / cycle_time
Machines needed       n = ceil(demand / r)
Worked example: smelter makes 1 plate per 3.2 s → r = 0.3125 plates/s
  Gear assembler: 1 gear per 1 s, needs 2 plates per gear → demand 2 plates/s
  n_smelters = 2 / 0.3125 = 6.4 → 7 smelters (6.4 exact, 7 gives 2.19 plates/s, 9% slack)
Chain of stages       demand propagates backwards: D_stage(k) = D_stage(k+1) · input_qty
```

- **Compute the whole chain with a solver.** Write the recipe graph as data, then back-propagate from the target output rate. Output a per-stage machine count, input rates and power draw. Test that the solver agrees with the headless sim.
- **Power and logistics are inputs too.** A chain is limited by the scarcest of: raw supply, machine count, power, transport throughput and storage.
- Link economics (sinks, inflation, balance) to `economy-design` and `balance`.

### 0.2 Throughput and queues
Belts, roads, rails, queues at counters and customer lines all behave like queues.

```
Little's law         L = λ · W            items in system = arrival rate × time in system
Utilisation          ρ = λ / μ            arrival rate over service rate
Average queue (M/M/1) Lq = ρ² / (1 − ρ)   (random arrivals and service, one server)
Worked example: ρ = 0.5 → Lq = 0.5    ρ = 0.9 → Lq = 8.1    ρ = 0.95 → Lq = 18.05
Belt: speed 1.875 tiles/s, item spacing 0.25 tile → throughput = 7.5 items/s per lane   (example numbers)
```

- **Rule of thumb.** Above about 85% utilisation, queues and delays grow fast. Design capacity upgrades so players feel the cliff before they hit it (warning at 80%).
- **Traffic.** Road networks fail by junction capacity, not road length. Model junctions as servers, and expose per-junction flow in an overlay.
- Compute theory values and compare with the headless sim in the balance pass.

### 0.3 Agent simulations and their performance cost
Citizens, customers, workers, vehicles and animals are agents. Agent count multiplies every per-tick cost.

```
Per-tick cost     T = N · (c_decide + c_move + c_render_prep)
Worked example: 10,000 agents × 5 µs per agent = 50 ms per tick
  At 60 Hz the frame budget is 16.7 ms → impossible on one thread.
  At a 10 Hz sim tick (100 ms) it uses 50% of the budget, leaving the rest for rendering and UI.
```

| Technique | Effect | Cost or risk |
|---|---|---|
| Fixed sim tick separate from render (for example 10–30 Hz) | Decouples cost from frame rate | Needs interpolation for smooth motion |
| Spread updates over frames (1/k of agents per frame) | Flattens spikes | Slight decision lag |
| Level of detail for agents (full, simplified, statistical) | Large scale at low cost | Behaviour must match across levels |
| Flow fields or cached paths for crowds | Cost independent of agent count | Memory per goal, invalidation on map change |
| Data-oriented layout (arrays of structs, ECS) | 2–10× faster iteration (estimate) | Harder to author and debug |
| Job system and multi-threading | Uses all cores | Race conditions. Deterministic ordering is hard |
| Statistical or aggregate simulation for far-off areas | Millions of virtual citizens | Players notice when it contradicts what they see |

- **Set the budget first.** Write down target agents, target tick rate and the minimum spec. Then profile. Agent count is a design lever: players love scale, so test at 2× the claimed maximum.
- **Pathfinding dominates.** Budget paths per tick, cache results, use hierarchical search, and invalidate on map change only for the affected region.
- **Determinism.** If saves, replays or multiplayer need identical results, use a fixed tick, a seeded RNG, stable iteration order and integer or fixed-point maths where it matters. Test with a 10,000-tick state hash on all target platforms.
- **Console budgets.** Fixed CPU and memory. Cap agent counts to what the weakest console holds at 30 fps and test early.

### 0.4 Information-dense UI
Management games are UI games. The player reads dozens of numbers per minute and must trust them.

- **Overlays.** One overlay per question: power, traffic, pollution, happiness, coverage, throughput, value. Colour scale with a legend, readable for colour-blind players (see `accessibility-localization`). Toggle by hotkey and by a visible bar.
- **Graphs.** Show trends (income, stock, population) with at least a 10-minute and a full-history range. Mark events on the axis. Let players pin graphs.
- **Tooltips that explain.** Every number answers "why" on hover: a list of contributing factors with values, sorted by size. This is the most-requested feature in reviews of opaque sims.
- **Scale and legibility.** Test at 1080p on a TV 3 metres away (console) and on a 1366×768 laptop. Text at least 18 px at 1080p for console (estimate). Support UI scaling.
- **Controller UI.** Cursor mode with magnetism, radial menus for categories, and shoulder buttons for tabs. A separate design pass, not a port of mouse UI.

### 0.5 Save and load of large states
```
State size      S ≈ N_entities · bytes_per_entity
Worked example: 1,000,000 entities × 64 B = 64 MB uncompressed
  Compression typically cuts simulation state by 3–10× (estimate, test on real data) → 6–21 MB
Load budget: target under 5 s on the minimum spec; use a progress bar beyond 3 s
```

- **Serialise the simulation, not the scene.** Save entities, components and RNG state. Rebuild meshes and caches on load.
- **Version and migrate.** Every save has a format version and a migration for each older version. Keep an archive of saves from each release and load them in CI.
- **Atomic writes.** Write to a temporary file, flush, then rename. Keep rolling backups and an autosave slot. Corrupt saves are the top cause of one-star reviews in long-run games.
- **Round-trip determinism.** Save at tick 5,000, load, run to tick 10,000, and compare the state hash with an uninterrupted run. This one test catches most serialisation bugs.

## 1. City builder

### Definition and player fantasy
The player lays out roads, zones, services and utilities and watches a city grow, then fixes the problems that growth causes. The fantasy is *urban planner and mayor*: a beautiful, working city that is your design. Two modes dominate: sandbox (build freely) and scenario or survival (limited resources, a goal).

### Core loop
```
plan (roads, zones, services) → city grows (population, jobs, traffic)
  → problems appear (traffic, power, crime, pollution, budget) → read overlays
  → fix or redesign → unlock new districts and tools → grow again
```

### Meta loops
- **Milestones and unlocks.** Population thresholds unlock services and tools.
- **Scenarios and challenges.** Fixed maps with goals, disasters or constraints.
- **Districts and policies.** Local rules with trade-offs.

### Session profile
Estimate: 1–3 hours, with a long tail of 50–500 hours per player. Pause-and-plan is central. Players often alternate building and watching. Handheld and console sessions are shorter and benefit from autosave and quick resume.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Road and zone placement | build-craft | Grid or freeform. Freeform costs more in tooling and pathfinding |
| Supply and demand (jobs, housing, goods) | economy & resources | §0.1 ratios. Show demand bars |
| Traffic and public transport | economy & resources; exploration & traversal | §0.2 junction capacity. Overlay is mandatory |
| Services coverage (fire, health, police) | economy & resources | Coverage radius and response time. Overlay |
| Budget, taxes and loans | economy & resources | Keep early game forgiving, with a debt floor |
| Land value and happiness | progression & upgrade | Tooltips that explain each factor |
| Disasters and events | live events | Optional toggle. Telegraph and give counters |
| Terrain and water | exploration & traversal | Cost terrain editing with money or time |

### Monetisation model and typical mix
Premium purchase with DLC (new building sets, themes, transport types) and a mod workshop. Typical mix (qualitative): base game, large expansions, small cosmetic packs and soundtracks. The model works best with clearly labelled paid packs and a robust free update stream. **Ethics flags:** many small paid packs can feel nickel-and-dime. Bundle sensibly and keep core systems free of paywalls.

### KPI expectations
Qualitative. Watch wishlist conversion, review score, refund rate in the first two hours, average hours and DLC attach rate. A weak sim launch is hard to recover from, since reviews cite performance and bugs. Stability at launch matters more than feature count.

### Retention drivers
Creative self-expression, the "one more district" loop, mod and asset ecosystem, scenario variety, DLC themes, and a stable simulation that scales to large cities.

### Content pipeline and production scope (estimates)
Simulation engineering (traffic, economy, agents) is the main cost, with asset content (buildings, props) the second. Rough estimate: 8–30 people and 2–4 years. A small team can ship a tight grid-based or scenario city builder in 12–24 months. Plan the asset pipeline early, since building variety drives perceived richness.

### Reference titles
- *SimCity* (Maxis, 1989, and later entries): the founding template.
- *Cities: Skylines* (Colossal Order, 2015): freeform roads, a large mod community.
- *Anno 1800* (Ubisoft Blue Byte, 2019): production-chain city building with trade.
- *Banished* (Shining Rock Software, 2014): harsh survival city.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Overlays and tooltips explain every problem | The city fails and the player cannot see why |
| The sim scales to large cities at stable frame rates | Performance collapses at 100k population |
| Early game is forgiving, mid-game is rich | Early game is a punishing budget trap |
| Mods and assets thrive | Launch ships with no mod support or broken tools |

### Innovation vectors
- City builders with strong narrative or moral choices.
- Climate, energy and sustainability systems as core play.

### Agent-buildability: 4/5
**Why 4:**
- Grid cities, supply-demand and budgets are data-driven and headless-testable.

**Why not 5:**
- Freeform road tooling, art variety and a convincing "city feel" need human work.

**What agents do well:** demand and budget sims, traffic throughput tests, scenario balancing, save fuzzing, overlay and tooltip generation.

### Starter feature list (P0 vertical slice: 32×32 grid city)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Grid road and zone placement with undo (build) | Placement validated. Undo restores the exact prior state hash |
| 2 | Residential, commercial and industrial demand (economy) | Demand follows the tuning table. Bars match the sim values |
| 3 | Power and water networks (build) | Disconnected buildings flagged. Overlay shows coverage |
| 4 | Citizen agents at 2,000 population (sim) | Tick time under 30 ms on the target spec at 2,000 agents |
| 5 | Road traffic with junction capacity (sim) | A bot reproduces the theoretical queue growth within 15% (§0.2) |
| 6 | Budget, taxes and a loan with a floor (economy) | Ledger balances. Bankruptcy cannot occur before the tutorial end |
| 7 | Three service types with coverage overlays (build) | Coverage radius tested. Response time shown in the tooltip |
| 8 | Happiness with explainable factors (ux) | Tooltip lists the top 5 factors with values summing to the score |
| 9 | Milestones unlocking tools (progression) | Unlock thresholds from the tuning file. Bot reaches each in the target time |
| 10 | Save and load with version (tech) | Round-trip hash identical. Archived v1 saves load |

### Platform notes
| Aspect | PC | Console | Web | Mobile |
|---|---|---|---|---|
| Input | Mouse and keyboard: drag roads, hotkeys, precision | Gamepad: cursor mode, snap, radial menus | Mouse and keyboard, small cities | Touch: large controls, grid snapping |
| Session | Long, pause-and-plan | Couch, suspend and resume | Short | Short, offline-friendly |
| Performance | Heavy CPU tick, mods | Fixed budget, city size caps | WASM limits | Cap agents and map size |
| Business | Premium, DLC, workshop | Premium, DLC, console ports often later, mod support limited | Free demo | Premium port or F2P (see `idle-tycoon-sim.md`) |

- Console ports of PC city builders have shipped with reduced city size and a rebuilt UI. Plan for it from the start.
- Workshop mods are a PC strength. Verify platform policy before promising mods on console.

## 2. PC management / tycoon

### Definition and player fantasy
The player runs a business (theme park, hospital, restaurant, railway, studio, shop) by designing layouts, hiring staff, setting prices and watching customers. The fantasy is *the clever owner*: tuning a machine that makes money and delights customers, one detail at a time.

### Core loop
```
design layout and set prices → hire and assign staff → customers arrive and use the facility
  → read satisfaction, queues and profit → adjust layout, prices, staffing
  → earn cash and reputation → expand and unlock → harder scenario
```

### Meta loops
- **Scenarios and objectives.** Star ratings per map, with growing goals.
- **Research and unlocks.** New rides, rooms, products, staff skills.
- **Reputation and licences.** Higher tiers open bigger sites.

### Session profile
Estimate: 1–2 hours per scenario, with a campaign of 10–40 scenarios. Players pause often. Handheld and console versions use shorter scenarios and autosave.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Layout design and room placement | build-craft | Layout efficiency is the skill. Show path length and queue overlays |
| Staff hiring, training, and shifts | economy & resources | Wages are the main cost sink |
| Pricing and demand | economy & resources | Price elasticity curve. Show "price vs visits" graph |
| Customer needs and satisfaction | time & energy | Needs meters with decay per customer (see `survival-sandbox.md` §0.1) |
| Queues and service times | economy & resources | §0.2. Make queue length the main visible problem |
| Research and unlocks | progression & upgrade | Unlock cadence tied to scenarios |
| Random events (breakdowns, VIPs, epidemics) | live events | Telegraph and offer counters |
| Scenario scoring | progression & upgrade | Star thresholds from a headless run |

**Demand curve.** Use a simple elasticity: `visits = base · (p_ref / p)^e` with `e` about 1.0–2.0 (estimate). Worked example: base 100 visits, reference price 10, price 15, e = 1.5 → 100 · (10/15)^1.5 ≈ 54 visits. Revenue = 54 · 15 = 810 versus 1,000 at the reference price. Raising price loses revenue when elasticity is above 1, so tune `e` to make "too high" and "too low" both feel bad.

### Monetisation model and typical mix
Premium purchase with expansions and themed DLC. Console and handheld ports are common. Typical mix (qualitative): base game, large content expansions, small cosmetic packs. Avoid free-to-play monetisation on PC releases of this type, as it harms reviews.

### KPI expectations
Qualitative. Reviews, scenario completion rate, hours, and DLC attach rate. Campaign completion is a strong quality signal. A launch bug in the economy (infinite money, unsolvable scenarios) is visible fast, so run headless soaks.

### Retention drivers
Optimising layouts, new scenarios and DLC, humour and theme, creative building, sandbox, and mod or blueprint sharing.

### Content pipeline and production scope (estimates)
Content-heavy: buildings, props, staff, customers, scenarios, animation. Rough estimate: 6–25 people and 2–3 years. Many art assets with a consistent style. A small team can ship a focused tycoon (one theme, 10 scenarios) in 12–18 months.

### Reference titles
- *RollerCoaster Tycoon* (Chris Sawyer, 1999) and *Planet Coaster* (Frontier, 2016): theme park design.
- *Theme Hospital* (Bullfrog, 1997) and *Two Point Hospital* (Two Point Studios, 2018): comedy hospital management.
- *Planet Zoo* (Frontier, 2019): animal welfare and habitat design.
- *Transport Tycoon* (Chris Sawyer, 1994) and *OpenTTD*: transport networks.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Customers and staff are readable and funny | Agents are anonymous dots |
| Queue and satisfaction overlays show causes | The player cannot tell why profit fell |
| Scenarios teach one new idea at a time | Scenario difficulty spikes arbitrarily |
| Layout tools are fast and forgiving | Building is fiddly |

### Innovation vectors
- Management with narrative or career arcs.
- Co-op management of one business.

### Agent-buildability: 4/5
**Why 4:**
- Demand, queues, staffing and scoring are formulas and simulations.

**Why not 5:**
- Humour, animation and layout feel need human craft.

**What agents do well:** elasticity and queue sims, scenario solvers, headless soak tests, UI tables, tooltip generators.

### Starter feature list (P0 vertical slice: one venue, one scenario)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Grid layout tool with 8 room or ride types (build) | Placement rules enforced. Undo and redo work |
| 2 | Customer agents with 3 needs (sim) | Decay per tuning table. Needs met by the correct facility |
| 3 | Queue model with service times (sim) | A bot's measured queue length matches §0.2 within 15% |
| 4 | Price setting with elasticity (economy) | Visits follow the curve. Graph matches |
| 5 | Staff hiring with wages and skill (economy) | Wage ledger balances. Skill raises service rate by the table |
| 6 | Satisfaction score with tooltip factors (ux) | Factors sum to the score. Top 3 listed |
| 7 | Research with 10 unlocks (progression) | Prerequisites enforced. Unlocks appear in the build menu |
| 8 | Scenario goals and star thresholds (progression) | Bot clears 1 star at the easy line, 3 stars with a tuned layout |
| 9 | Breakdown and VIP events (live) | Events telegraphed. Counters exist and work |
| 10 | Save and load with hash check (tech) | Round-trip identical |

### Platform notes
| Aspect | PC | Console | Web | Mobile |
|---|---|---|---|---|
| Input | Mouse precision for layout, hotkeys | Gamepad with snap and radial build menu | Mouse | Touch, simplified |
| Session | 1–2 h | 1–2 h, suspend and resume | Short | Short, F2P patterns (see `idle-tycoon-sim.md`) |
| Performance | Agent counts into the thousands | Cap customers | Cap agents | Cap agents |
| Business | Premium, DLC | Premium, DLC, strong console audience for friendly themes | Free demo | F2P or premium port |

## 3. Factory and automation

### Definition and player fantasy
The player extracts raw resources, builds machines and logistics, and scales a production system to meet growing demand, ending in an efficient, self-running factory. The fantasy is *the engineer*: a messy start, then a clean system where numbers go up without you. The satisfaction is solving throughput puzzles.

### Core loop
```
extract resources → hand-craft and build first machines → connect with belts, pipes or vehicles
  → find the bottleneck (§0.1, §0.2) → redesign and scale → unlock next tier of tech
  → bigger target (rocket, mega-project, contract) → repeat
```

### Meta loops
- **Tech tree.** Research unlocks machines and recipes.
- **Mega-project.** A final goal (launch, mega-build) that ends or restarts the game.
- **Optimisation challenges.** Ratio and compactness (blueprints, leaderboards).

### Session profile
Estimate: 2–4 hours of deep focus, with total playtime of 100–1,000+ hours for engaged players. Sessions end when the next milestone is hit. Players often say "one more thing" late into the night, so provide clear stopping points and fast save.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Recipes and production chains | build-craft; economy & resources | §0.1. Solver and ratio display |
| Belts, pipes, rails or drones | build-craft | §0.2. Throughput per lane, junction rules |
| Power networks | economy & resources | Brownouts slow machines proportionally |
| Blueprints and copy-paste | UX automation | Must-have for scale |
| Research tree with science packs | progression & upgrade | Each pack type needs its own chain |
| Pollution and enemies (optional) | combat; time & energy | Pressure that forces defence and efficiency |
| Map and resource patches | exploration & traversal | Finite patches push expansion |
| Statistics and production graphs | UX automation | §0.4. Players live in these |

### Monetisation model and typical mix
Premium purchase, often through early access, with free updates and optional expansions. Modding is central. Typical mix (qualitative): base game, major expansion, soundtrack. Avoid free-to-play monetisation, since the audience reads it as hostile. **Ethics flag:** early access must be honest about scope.

### KPI expectations
Qualitative. Very high hours per player is the norm (hundreds). Reviews, refund rate and long-tail sales through sales events. Players who finish the first milestone usually stay. Performance at scale (thousands of machines) is a top review topic.

### Retention drivers
The "one more fix" loop, optimisation depth, mods, big goals, creative blueprints, co-op, and regular content updates.

### Content pipeline and production scope (estimates)
Engineering-heavy: simulation of items, belts and power at scale, plus UI for dense information. Art is simpler (clear silhouettes). Rough estimate: 5–20 people and 2–5 years, and small teams have shipped hits. Optimisation of update loops (grouping, event-based updates) is the central technical task.

### Reference titles
- *Factorio* (Wube Software, early access 2016, release 2020): the benchmark for belts and performance.
- *Satisfactory* (Coffee Stain Studios, 2019 early access, 1.0 in 2024): first-person 3D factory.
- *Dyson Sphere Program* (Youthcat Studio, 2021): planetary-scale automation.
- *Shapez* and *Shapez 2* (tobspr Games): abstract, light factory puzzles.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Ratios are learnable and the UI shows bottlenecks | Players need a spreadsheet to learn ratios |
| Performance scales to huge factories | Frame rate collapses at 1,000 machines |
| Blueprints and copy-paste exist | Every build is manual and tedious |
| Progression stays interesting for 50 hours | The mid-game is repetitive |

### Innovation vectors
- Factory plus survival or exploration pressure.
- Factory plus tower defence or tactical combat.

### Agent-buildability: 4/5
**Why 4:**
- Recipes, ratios and throughput are exact, so solvers and sims verify them.

**Why not 5:**
- Camera, building feel and visual clarity need human iteration.

**What agents do well:** ratio solvers, belt throughput tests, recipe graph validators, benchmark harnesses, blueprint import and export.

### Starter feature list (P0 vertical slice: 3 tiers, one target)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Resource patches and miners (economy) | Miner rate from the table. Patch depletes at the specified rate |
| 2 | 6 machine types and 12 recipes (build) | Solver output equals sim output within 1% over a 10-minute run |
| 3 | Belts with lanes and splitters (build) | Throughput measured equals the theory. No item loss or duplication in 1 M item test |
| 4 | Power grid with brownout (economy) | Machine speed scales with satisfaction. Overlay shows power state |
| 5 | Ratio and bottleneck overlay (ux) | The slowest stage is highlighted. Tooltip says starved or blocked |
| 6 | Production statistics graphs (ux) | Rates match the sim. 10-minute and 1-hour windows |
| 7 | Research tree with 3 science packs (progression) | Prerequisites enforced. Bot reaches tier 3 in the target time |
| 8 | Blueprint copy, paste, save (ux) | Pasted layout identical (hash). Works across saves |
| 9 | Target goal with a completion screen (progression) | Bot completes the goal in the target band |
| 10 | Performance gate: 2,000 machines (tech) | Tick under 16 ms on the target spec. Update loop only touches active machines |

### Platform notes
| Aspect | PC | Console | Web | Mobile |
|---|---|---|---|---|
| Input | Mouse and keyboard, hotkeys, drag-build | Gamepad: build wheels, cursor snap, controller-first designs ship (3D first-person factory games suit pads) | Mouse, small factories | Touch: simplified (see `idle-tycoon-sim.md`) |
| Session | Deep focus, long | Couch, suspend and resume | Short | Short |
| Performance | CPU-bound at scale, multi-thread | Fixed CPU: cap machine counts | Single-thread limits | Cap machines |
| Business | Early access, mods | Console ports later, fewer mods | Free puzzle variants | F2P puzzle factories |

## 4. Life sim and farming (PC / console)

### Definition and player fantasy
The player lives in a small world (a farm, a town, a household) and shapes daily life: tending crops, forging relationships, decorating, pursuing small goals. The fantasy is *a gentle life of your own*: a place that grows with you. Mobile cosy, farming and life sims are covered in `idle-tycoon-sim.md` §4–5; this section covers PC and console depth.

### Core loop
```
wake → spend energy on chores (water, harvest, craft, fish, mine)
  → sell goods or deliver them → talk to townsfolk (gifts, events)
  → sleep (day ends, crops grow, calendar advances) → unlock something new
```

### Meta loops
- **Seasons and calendar.** Crops, festivals and events by season.
- **Relationships.** Townsfolk with schedules, hearts and story events.
- **Collections.** Fish, bundles, museum, recipes, achievements.

### Session profile
Estimate: 30–90 minutes, typically one in-game day to a few days per sitting. Natural stopping point at sleep. Total 50–200 hours for a first playthrough, then replays. Handheld play is a strong fit.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Energy budget per day | time & energy | Sets the choices of a day. Allow upgrades that raise it |
| Crop growth by season | economy & resources | Table of days-to-grow, price, season. Ratio of profit per day |
| Calendar, weather and festivals | live events; time & energy | Scripted content gives a rhythm |
| NPC schedules and relationships | social & competition | Schedule tables. Gift preference data |
| Collections and bundles | collection & randomness | Soft goals that guide exploration |
| Crafting and machines | build-craft | Small automation loops (see §3 lightly) |
| Mining or combat side loop | combat; exploration & traversal | Optional, scaled to the player |
| Customisation (house, farm, character) | build-craft | Core to the cosy fantasy |

**Crop value check.** Profit per day = (sale price − seed cost) / growth days. Worked example: crop sells 120, seed 40, grows 8 days → 10 per day per tile. A faster crop selling 60 with seed 20 in 4 days → 10 per day, so the two tie on profit and differ on effort. Balance so that the best crop depends on how often the player visits, and avoid one dominant crop.

### Monetisation model and typical mix
Premium purchase with free updates and optional paid expansions or cosmetic packs. Console ports are common. **Ethics flags:** do not add timers or energy refills for money to a premium cosy game. The audience reacts strongly to monetisation changes.

### KPI expectations
Qualitative. Reviews (aim for Overwhelmingly Positive among cosy titles), hours, return after updates, co-op share, and wishlist conversion. Word of mouth and creator coverage drive sales, with long-tail sales for years.

### Retention drivers
Cosy routines, relationships and stories, seasons, collections, customisation, co-op with friends, and regular updates or expansions.

### Content pipeline and production scope (estimates)
Content-heavy: crops, items, NPC dialogue, events, art and music. A solo developer has shipped a landmark title in this genre, so small scope is feasible. Rough estimate: 1–10 people and 2–4 years. Dialogue and event writing is the long pole. Plan localisation early (see `accessibility-localization`).

### Reference titles
- *Harvest Moon* (Natsume, 1996 onwards): the original farming sim.
- *Stardew Valley* (ConcernedApe, 2016): the benchmark for PC farming.
- *Animal Crossing* (Nintendo): real-time-calendar life sim.
- *The Sims* (Maxis and EA): household life sim.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Every day offers 2–3 small meaningful choices | Chores are repetitive with no new goal |
| NPCs feel like people | NPCs are gift dispensers |
| Calm, readable, rewarding visuals and audio | Information overload spoils the cosy tone |
| Free of punishing failure | Crops die, relationships decay with harsh penalties |

### Innovation vectors
- Life sims with deeper NPC simulation.
- Cosy genre fusions (farming plus survival, farming plus dungeon).

### Agent-buildability: 3/5
**Why 3:**
- Crops, calendars, schedules and economy are tables, so they are testable.

**Why not higher:**
- Charm, art, music, writing and NPC personality are human work.

**What agents do well:** crop and price tables, calendar simulators, schedule validators, save tests, UI for inventory and relationships.

### Starter feature list (P0 vertical slice: one farm, one season, 4 NPCs)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Day cycle with energy and sleep (core) | Energy per day from the tuning table. Sleep advances the calendar |
| 2 | 6 crops in 2 seasons (economy) | Profit per day within the intended band. No dominant crop in sim |
| 3 | Tool upgrades and chores (gameplay) | Tool tiers change energy cost and area |
| 4 | 4 NPCs with schedules and gift likes (social) | Schedules validated against map paths. Gift reaction table tested |
| 5 | Relationship events, 2 per NPC (narrative) | Triggers fire once. Save and load keeps flags |
| 6 | Collections: 20 fish or items (collection) | Codex tracks found items. Reward on completion |
| 7 | Festival day (live) | Calendar triggers the festival. Rewards granted once |
| 8 | Crafting and one machine (build) | Recipe and timing from the table |
| 9 | Farm and house decoration (build) | Placement saved. Undo works |
| 10 | Save and load of a full season (tech) | Round-trip hash identical |

### Platform notes
| Aspect | PC | Console | Web | Mobile |
|---|---|---|---|---|
| Input | Mouse or keyboard or pad: all expected | Gamepad: tool wheels, auto-target, simple menus | Mouse | Touch: virtual stick (see `idle-tycoon-sim.md`) |
| Session | One day per sitting | Handheld friendly: suspend at any time | Short | Short, push for daily play |
| Performance | Light, wide spec range | 60 fps expected, small load times, split-screen sometimes | Small download | Battery-friendly |
| Business | Premium, mods, free updates | Premium, strong demand on Switch-class handhelds | Free demo | F2P is a different design |

## 5. Job and vehicle sims

### Definition and player fantasy
The player performs a real-world job or drives a real-world vehicle with simplified or detailed realism: a truck, a train, an aircraft, a bus, a farm machine, a power washer. The fantasy is *competence and calm*: doing a job well, enjoying the machine and the scenery. Mastery is low-stress and satisfying.

### Core loop
```
accept job or route → prepare (vehicle, cargo, planning) → drive or operate under rules
  → deliver or complete the task → earn money and reputation → upgrade or buy new equipment
```

### Meta loops
- **Career and company.** Hire drivers, buy trucks, run routes (a light management layer).
- **Licences and certificates.** Unlock bigger vehicles and cargo.
- **Collection.** Vehicle packs, liveries, locations.

### Session profile
Estimate: 30 minutes to 3 hours, often relaxed and played alongside podcasts or music. Strong replay through routes and DLC. Play is calm, so pause and resume matter. Peripheral setups lead to long sessions.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Vehicle handling model (arcade to sim) | exploration & traversal | Offer assist presets. Realism level is a setting |
| Routes, jobs and contracts | progression & upgrade; economy & resources | Contract value from distance and risk |
| Rules and penalties (speed, damage, fuel) | economy & resources | Clear feedback, fair thresholds |
| Fuel, wear and maintenance | time & energy; economy & resources | Light sinks that keep money relevant |
| Company management layer | economy & resources | Optional. Hire AI drivers |
| Real maps or authored worlds | exploration & traversal | World size drives content cost. Streaming rules §0.7 in `survival-sandbox.md` |
| Weather and time of day | exploration & traversal | Visual and handling changes |
| Mod and DLC pipeline | economy & resources | Vehicle packs and map expansions are the long-term business |

### Monetisation model and typical mix
Premium base game, then many paid DLC packs (new regions, vehicles, cargo) and a mod community. Typical mix (qualitative): large map expansions, cosmetic and vehicle packs, bundles. **Ethics flags:** many small DLCs fragment the player base in multiplayer, so label compatibility clearly.

### KPI expectations
Qualitative. Long tail with steady sales, strong reviews, high hours per player, and very high DLC attach among the core. Peripherals and VR make the audience sticky. Seasonal sales drive spikes.

### Retention drivers
The calm loop, new routes and regions, vehicle collection, mods, multiplayer convoys, peripherals and immersion, and real-world interest (aviation, trucking).

### Content pipeline and production scope (estimates)
Asset-heavy: vehicles, interiors, maps, audio and physics tuning. Real-world licences for vehicles or brands can be a cost and legal task (see `legal-ethics`). Rough estimate: 10–50 people for a flagship, or a team of 3–10 for a focused niche job sim (cleaning, delivery, farming). Map and vehicle packs extend the life.

### Reference titles
- *Euro Truck Simulator 2* (SCS Software, 2012) and *American Truck Simulator*: truck driving with route expansions.
- *Microsoft Flight Simulator* (Asobo Studio and Xbox Game Studios, 2020): large-scale flight with real-world data.
- *Farming Simulator* series (Giants Software): machinery and farm management.
- *PowerWash Simulator* (FuturLab, 2022): a relaxing job sim.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Handling feels good and offers assist levels | Handling is too hard or too floaty |
| Jobs have variety and a sense of progress | Jobs repeat without new reasons to continue |
| Peripherals and VR work well | Peripheral support is poor or buggy |
| DLC and mods add real regions and vehicles | DLC is thin and fragments the community |

### Innovation vectors
- Cosy job sims on small scale (cleaning, gardening, repair).
- Multiplayer convoys and shared companies.

### Agent-buildability: 3/5
**Why 3:**
- Contracts, economy, routes and rules are formulas and tests.

**Why not higher:**
- Handling feel, world art and audio depend on iteration with real play.

**What agents do well:** contract and economy sims, route graph validators, handling parameter sweeps (with human tuning), UI for jobs and garage, save tests.

### Starter feature list (P0 vertical slice: one vehicle, one map, 5 jobs)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Vehicle handling model with 3 assist presets (gameplay) | Lap-time bot stays within tolerance. Presets change parameters only |
| 2 | Map with road graph and 6 locations (world) | Every location reachable. Route length matches the graph |
| 3 | Job board with pay formula (economy) | Pay from distance, cargo and deadline. Worked examples tested |
| 4 | Fuel, damage and repair (economy) | Fuel burn from the table. Repair cost from the table |
| 5 | Traffic rules and fines (gameplay) | Violations detected with the specified thresholds |
| 6 | Garage with 3 vehicle tiers (progression) | Upgrade changes stats as listed |
| 7 | Time of day and weather (world) | Handling modifier applied. Visibility change tested |
| 8 | Career progression with licences (progression) | Licence gates cargo and vehicles |
| 9 | Wheel and gamepad support with rebind (ux) | Axis calibration, dead zones, force feedback toggle |
| 10 | Save and resume mid-route (tech) | Resume at the same position and cargo |

### Platform notes
| Aspect | PC | Console | Web | Mobile |
|---|---|---|---|---|
| Input | Wheel, pedals, flight stick, keyboard, VR | Gamepad primary, some wheel support | Keyboard or pad, light | Touch tilt or on-screen controls |
| Session | Long, relaxed | Couch sessions | Short | Short |
| Performance | Large worlds, mods, VR needs high frame rate | Fixed targets, streaming limits | Small maps | Light maps |
| Business | Premium, DLC, mods | Premium, DLC (platform fees), console ports of PC hits | Free demo | F2P versions with ads exist (different design) |

- VR needs a minimum steady frame rate (for example 72–90 fps depending on headset). Treat it as a separate performance target.
- Racing-style handling and wheel support overlap with `competitive-pvp.md` (racing).

## 6. God games

### Definition and player fantasy
The player is an indirect power over a world of followers or creatures: shaping land, granting or withholding miracles, and watching a society react. The fantasy is *the deity*: curious, playful, sometimes cruel, always powerful. Systemic simulation produces surprising outcomes.

### Core loop
```
observe the world and its people → use powers (terraform, miracles, nudges)
  → people react (build, worship, fight, migrate) → outcomes feed the world
  → gain power or belief → unlock new powers → adapt to new situations
```

### Meta loops
- **Belief or faith economy.** Currency earned from followers and spent on powers.
- **Eras and unlocks.** Tech or cultural stages open powers and challenges.
- **Rival gods or scenarios.** Opponents and goals.

### Session profile
Estimate: 1–2 hours of exploration and experiment. The sandbox mode invites short, playful sessions and video sharing. Campaigns run for 10–40 hours.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Indirect control of autonomous agents | UX automation; social & competition | Players nudge. Agents decide. §0.3 cost |
| Terrain and nature manipulation | build-craft; exploration & traversal | Costly to simulate. Cap the update region |
| Miracles and powers | combat; economy & resources | Cost, cooldown, side effects |
| Belief or faith as a resource | economy & resources | Tie belief to follower happiness, not just count |
| Morality and alignment systems | progression & upgrade | Make consequences visible |
| Emergent events from systems | live events | Chain reactions need guard rails |
| Disasters and weather | live events | Player-triggered and natural |
| Observation tools (inspect agent, history) | UX automation | §0.4. Let players follow a villager |

### Monetisation model and typical mix
Premium purchase, with an optional expansion. A sandbox god game with strong mod support is also sold on a modest early-access price, and mobile variants exist (see `idle-tycoon-sim.md` for light mobile patterns). Avoid monetising miracles with real money, as it breaks the fantasy.

### KPI expectations
Qualitative. Reviews, sandbox hours, share and video clips, and word of mouth. Niche but loyal. A compact scope with a clear fun toy tends to out-perform a large unfinished systems game.

### Retention drivers
Play and experiment, emergent stories, share-worthy chaos, campaign goals, and mod content.

### Content pipeline and production scope (estimates)
Systems and agent AI dominate, with modest art. Rough estimate: 2–10 people and 18–36 months. Tuning chain reactions and preventing degenerate loops (everyone dies, nothing happens) is the long pole. Procedural content and rule-driven worlds scale well (`procedural-generation`).

### Reference titles
- *Populous* (Bullfrog, 1989): the original god game.
- *Black & White* (Lionhead, 2001): a creature as an extension of the god.
- *From Dust* (Ubisoft, 2011): terrain and fluid manipulation.
- *WorldBox* (Maxim Karpenko): a sandbox god toy.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| The toy is fun in the first minute | Players must read a manual to do anything |
| Systems interact in surprising but explainable ways | Chaos feels random and unreadable |
| The world reacts to player powers visibly | Powers feel cosmetic |
| Followers feel alive | Agents are generic and interchangeable |

### Innovation vectors
- Large-language-model or generative storytelling for followers (with deterministic seeds and moderation).
- Ecological and climate god games.

### Agent-buildability: 3/5
**Why 3:**
- Rule-based systems and agent sims are headless-testable.

**Why not higher:**
- Charm, readability and the "toy" feel come from human iteration.

**What agents do well:** rule tables, fuzzing for degenerate worlds, performance benchmarks, UI for inspection tools, save and load tests.

### Starter feature list (P0 vertical slice: one island, 200 followers)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Island terrain with raise, lower, water (world) | Terrain edits saved. Water flow stable (no oscillation over 1,000 ticks) |
| 2 | 200 follower agents with needs and jobs (sim) | Tick time under 20 ms at 200. Needs per tuning table |
| 3 | Belief currency from follower happiness (economy) | Belief rate equals the formula. Tooltip shows factors |
| 4 | 5 powers with cost and cooldown (gameplay) | Costs and cooldowns enforced. Effects tested |
| 5 | Settlement growth: houses, farms, shrines (sim) | Followers build per rules. No deadlocks in 100 seeded runs |
| 6 | One rival tribe with simple AI (gameplay) | AI chooses from the utility table. Wins against idle player |
| 7 | Disaster and weather events (live) | Telegraphed. Counter powers work |
| 8 | Follower inspect panel (ux) | Shows needs, job, mood and history |
| 9 | Degenerate-state fuzzer (qa) | 1,000 random power sequences: no crash, no stuck world (flagged by the checker) |
| 10 | Save and load with hash (tech) | Round-trip identical |

### Platform notes
| Aspect | PC | Console | Web | Mobile |
|---|---|---|---|---|
| Input | Mouse: paint terrain, point at followers | Gamepad: cursor, brush sizes on triggers | Mouse, small worlds | Touch fits brushes and taps |
| Session | 1–2 h, play and watch | Couch sessions | Short sandbox | Short, play-and-share |
| Performance | Agent counts, fluid sim cost | Cap world size | Light sim | Light sim, battery |
| Business | Premium, early access | Premium port | Free toy with ads | F2P or ad-supported toys |

## 7. Sports management

### Definition and player fantasy
The player manages a club: squad selection, tactics, transfers, finances, training and youth development, across seasons and decades. The fantasy is *the manager*: building a team, outthinking rivals and living through a long story of promotions, heartbreaks and dynasties.

### Core loop
```
review squad, finances and fixtures → set lineup, tactics and training
  → simulate matchday (text, 2D or 3D) → read results and reports
  → manage transfers, contracts, youth, board expectations → next fixture
  → end of season (awards, promotion, rollover) → repeat
```

### Meta loops
- **Career arcs.** Club, league and legacy goals over many seasons.
- **Database depth.** Thousands of players, staff and clubs.
- **Online leagues.** Friends or communities run leagues with human managers.

### Session profile
Estimate: matchday sessions of 15–60 minutes, with seasons stretching over weeks of play. A save can last for years. Players check in on lunch breaks and alt-tab during work. Strong overlap with spreadsheets and forums.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Squad selection and tactics | combat; progression & upgrade | Readable tactics sliders with visible effects |
| Match simulation engine | combat | Probabilistic model with seeded RNG. Show key events |
| Player attributes and development | progression & upgrade | Ageing curve: growth to about 25–27, plateau, decline |
| Transfers, contracts and wages | economy & resources | Budget, wage ceiling, agents' demands, fair AI |
| Scouting and hidden information | exploration & traversal | Fog of data. Reports with uncertainty |
| Training and fitness | time & energy | Injury risk tied to load |
| Board, fans and finance | economy & resources | Expectations scale with the club |
| Online leagues | social & competition | Turn deadlines and sync rules |

**Match model sketch.** Estimate expected goals for each side from attack and defence ratings: `λ_home = base · (A_h / D_a)^k`, then draw goals from a Poisson distribution with that mean. Worked example: base 1.4, A_h/D_a = 1.2, k = 1 → λ = 1.68; P(0 goals) = e^−1.68 ≈ 0.19. Calibrate base and k so league tables show realistic spreads (for example, the best team wins about 25–30% of seasons in a 20-team league, an estimate to validate against real data). Test with 10,000 simulated seasons.

### Monetisation model and typical mix
Premium annual or multi-year releases with DLC and, in some franchises, card-collection modes (paid random packs, which need loot-box compliance, see `rpg-gacha.md` §0.3). Licences (leagues, clubs, player names) are a major cost and a legal matter (`legal-ethics`). **Ethics flags:** paid packs in a sports title raise gambling concerns, especially for younger players.

### KPI expectations
Qualitative. Annual sales and returning players, review score, hours played, online league counts, and licence renewals. Loyal audiences accept incremental updates, but quality bugs in the match engine or database errors are punished.

### Retention drivers
The long story, database depth, rivalries and promotion chases, online leagues, community-made rosters and mods, and the annual update.

### Content pipeline and production scope (estimates)
Data-heavy: players, staff, clubs, leagues, researchers to keep the database current. The match engine and AI managers are the technical core. Rough estimate: 10–50 people for a flagship franchise. A small team can ship a niche sport or fantasy-league manager in 18–30 months using generated data and a text-based match engine. Licences are expensive, so many indie titles use fictional names with community-editable databases.

### Reference titles
- *Football Manager* (Sports Interactive, annually): the depth benchmark.
- *Out of the Park Baseball* (OOTP Developments): deep baseball simulation.
- *Motorsport Manager* (Playsport Games, 2016): strategy and team management in racing.
- *Franchise Hockey Manager* (Out of the Park Developments).

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| The match engine feels fair and explainable | Results feel rigged or inexplicable |
| The database is deep and current | Data errors undermine trust |
| AI clubs act plausibly in the transfer market | AI exploits are common (one trick wins every season) |
| UI makes huge data navigable | Menus bury information |

### Innovation vectors
- Narrative layers: press, dressing room and board.
- Better transfer-market AI and explainable scouting.

### Agent-buildability: 4/5
**Why 4:**
- The sim is statistical and deterministic with a seed. Thousands of seasons can be run headless.

**Why not 5:**
- Licences and real-world data are a legal and data-collection problem, not a code problem.

**What agents do well:** match engine calibration, season sims, AI transfer exploit hunts, database validators, UI table work, balance of ageing and injuries.

### Starter feature list (P0 vertical slice: 12-team league, text match engine)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Generated database: 12 clubs × 25 players (data) | Attribute ranges valid. No duplicate names. Seeded |
| 2 | Match engine with Poisson goals and events (sim) | 10,000 seasons: goal averages within 5% of target. Home advantage as specified |
| 3 | Lineup and tactics sliders (gameplay) | Each slider changes ratings by the table. UI shows effect |
| 4 | Fixture calendar and league table (core) | Round-robin valid. Table tie-break rules unit-tested |
| 5 | Player development and ageing (progression) | Ageing curve matches the table. Injuries tied to load |
| 6 | Transfers with AI clubs (economy) | AI offers within valuation band. A bot cannot gain more than the allowed edge by one exploit |
| 7 | Contracts, wages and finance (economy) | Ledger balances. Wage ceiling enforced |
| 8 | Scouting with uncertainty (exploration) | Reports show ranges that narrow with scouting time |
| 9 | Board expectations and a sacking rule (progression) | Thresholds from the table. Warning shown before dismissal |
| 10 | Save and load across 10 seasons (tech) | Round-trip hash identical. Under 3 s load |

### Platform notes
| Aspect | PC | Console | Web | Mobile |
|---|---|---|---|---|
| Input | Mouse and keyboard: tables, search, hotkeys | Gamepad: simplified menus, touch-style cursor | Mouse, light | Touch fits cards and lists (see `idle-tycoon-sim.md`) |
| Session | Matchday bursts and long careers | Couch, suspend and resume | Short | Short, push on matchdays |
| Performance | Huge databases, CPU-heavy sims | Memory limits on database size | Smaller databases | Smaller databases |
| Business | Annual premium, DLC, mods and editor | Premium ports and lite versions | Free browser leagues | F2P and premium mobile editions |

## Volatile facts (as of Oct 2026 — verify before relying)

- Steam reached about 43.5 million concurrent logged-in users on 11 Oct 2026 (SteamDB figure reported by press), about 14.5 million of them in a game. Concurrent users include people with the client open — [Notebookcheck](https://www.notebookcheck.net/Steam-sets-a-new-all-time-concurrent-player-record-after-surpassing-42-million-users-online.1201788.0.html), [Dot Esports](https://dotesports.com/general/news/steam-all-time-record-43-5-million-concurrent-users)
- Steam Next Fest ran 19–26 Oct 2026, and Valve has published its sale and festival schedule through July 2027. Use the festival demo window to test a sim slice — [God Is a Geek](https://godisageek.com/2026/10/steam-next-fest-october-2026/), [Digital Citizen](https://www.digitalcitizen.life/valve-reveals-full-steam-sale-and-festival-schedule-through-july-2027/)
- Steam store revenue share and per-app fee terms are not verified in this session. Check [Steamworks documentation](https://partner.steamgames.com/doc/gettingstarted) before budgeting.
- Console mod and early access policies, licensing costs for sports data and the status of any specific title's release are not verified. Check `console-pathway` and the platform holder's documentation.
- I found no sourced market-size or retention figures for PC simulation genres this session. All numbers labelled "estimate" above are design defaults, not statistics.

## Related skills
- `mechanics-codex`: cards for every mechanic named above.
- `economy-design`: sinks, sources, budgets and price curves.
- `balance`: ratio solvers, bot runs and win-rate bands.
- `game-architecture`: sim-core, ECS, determinism, headless builds.
- `procedural-generation`: terrain, maps and generated databases.
- `qa-testing`: save fuzzing, soak tests and state-hash checks.
- `platform-targets`, `pc-web-release`, `console-pathway`: input, release and certification differences.
- `idle-tycoon-sim.md`: mobile tycoon, farming, life sim, home design and restaurant sims, not repeated here.
- `survival-sandbox.md`, `mmo-live-service.md`: sibling playbooks for colony sims, survival and persistent worlds.
