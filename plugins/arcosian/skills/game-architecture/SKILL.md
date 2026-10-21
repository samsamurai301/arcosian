---
name: game-architecture
description: 'Game architecture codex: the studio sim-core + presentation split, deterministic cores, fixed timestep, state machines, command/undo/replay, event bus, pooling, ECS vs composition, DI, data-driven design, AI techniques, versioned saves, remote config, testing. Use when asked to structure a game project, choose a pattern, design saves or migrations, plan tests, or review code architecture.'
when_to_use: 'Starting or refactoring a game codebase; choosing state machine, ECS or AI approaches; designing saves, cloud sync or remote config; setting up tests and code review.'
---

# Game Architecture

The studio builds every game on one rule: deterministic, engine-free rules in `core/`, everything the player sees or hears in `presentation/`, platform wrappers in `services/`. This skill explains that split, the patterns that sit on top of it, and the persistence and quality practices that keep a mobile codebase shippable.

## What this skill gives you

- The studio core abstraction (`apply(action) -> events`, serialisable state, seeded RNG) mapped to the real files of `templates/godot-starter` (`core/sim.gd` and friends) and `templates/unity-starter` (`Assets/_Game/Core`: `Sim`, `SimEvent`, `SimEventType`, `GameState`, `Rng`).
- A pattern catalogue with when-to-use and when-not-to-use: fixed timestep, FSM/HFSM/pushdown, command/undo/replay, event bus, pooling, composition vs ECS, DI, data-driven design, spatial partitioning.
- Game AI selection and recipes: FSM, behaviour trees, utility AI, GOAP, steering, director AI.
- Persistence and quality: versioned saves with migrations, atomic writes, cloud conflict policy, remote config layering, localisation tables, testing pyramid, allocation-aware code, review checklist.
- A migration recipe for moving an existing project onto the split one slice at a time.

## Core models

**1. The dependency rule.** presentation -> core, services -> core data only, core -> nothing. A core file that references a Node, a clock, an autoload or a global random call is a bug. Enforce by grep in Godot and `noEngineReferences` asmdefs in Unity; do not rely on discipline.

**2. Actions in, events out.** The core has one mutator. `apply(action) -> events`. Rejections are events. The view animates events and never mutates state. If the view must peek at state to know what happened, the event vocabulary is too thin.

**3. Determinism is a feature you design.** Seeded RNG stored in state; no hash-order decisions; time arrives as data; floats only where cross-platform drift is acceptable. Payoffs: replays, bots, bug reports as seed plus actions, daily challenges, server validation.

**4. State is data.** `to_dict()`/`load_dict()` round-trips everything including RNG. JSON-safe (int64 as strings). The view can be destroyed and rebuilt from state at any moment, which makes pause, resume and scene changes free.

**5. Simplest pattern that fits the entity count.** Puzzle and merge games need no ECS or GOAP. Count peak active entities on the lowest target device: under about 300 use plain components; a few thousand use packed arrays; beyond that evaluate ECS and its tooling cost.

**6. Data over code for anything a designer touches.** Validated schemas, stable string ids, safe defaults in code, overrides in data, remote config as a late layer with a kill switch.

**7. Saves are a contract with the player.** Version at the root, migration for every shipped version, atomic write plus backup, never overwrite what you could not read.

**8. Legible AI beats clever AI.** Choose FSM plus steering plus a director before reaching for planners. Telegraph, debug-draw, and test decisions as pure functions.

## Decision procedures

### Structure a new project

1. Write the core contract first: list actions, events, state fields, `lookup` paths for tests, `legal_actions` for bots (see `references/sim-core-presentation.md`).
2. Copy `templates/godot-starter` or `templates/unity-starter`; replace the sample mechanic; keep the tests and tools (`tests/` and `tools/` in Godot, `Assets/_Game/Tests` and `Assets/_Game/Editor` in Unity).
3. Implement the rule as static pure functions, test them, then add `apply`.
4. Add a scripted playthrough and a random bot run to CI before building any scene.
5. Build the view last: one `play(events)` function, plus a snap-to-state safety net (`refresh()` calling `board.sync(grid)` in the Godot template, `BoardView.Render(state)` in Unity).
6. Add services behind interfaces with null implementations.

### Pick a state/AI technique

| Situation | Choose |
|---|---|
| Few modes, clear triggers | FSM with a transition table and hysteresis |
| Shared escapes across many states | HFSM |
| Modals, interrupts, UI back-stack | Pushdown automaton |
| Reactive priorities, reusable behaviours | Behaviour tree at 4 to 10 Hz |
| Continuous competing desires | Utility AI with plotted curves and inertia |
| Designers add capabilities, not scripts | GOAP, only if the action set is large |
| Movement among crowds | Steering plus spatial hash |
| Session pacing | Director with bounded, logged adjustments |

Details and code in `references/patterns-and-ai.md`.

### Choose how to handle time

1. Turn-based or event-driven game: no loop, just `apply`.
2. Real-time sim: fixed timestep accumulator, clamp elapsed time, interpolate rendering.
3. Idle or offline: one `offline(seconds)` action with a clamp and closed-form math.
4. Networked: pick tick rate first (see `multiplayer-backend`).

### Design saves

1. Bucket data by lifetime: profile, run, settings, cache, entitlements.
2. Root `version`; `default_save()`; chained `migrate()`; fixtures per version.
3. Atomic write (tmp, rotate to `.bak`, rename); flush on pause and milestones; debounce otherwise.
4. Cloud: shape data for merge (sets, ledgers, monotonic counters); document the conflict policy; use a server revision, not the device clock.
5. Keep the corrupt file; telemetry on every recovery path.

Details in `references/data-persistence-and-quality.md`.

### Review a codebase (30-minute pass)

1. grep `core/` for engine types, random, clock; open the asmdefs.
2. Read `apply` and the event list: can the view be rebuilt from events? Is every mutation here?
3. Round-trip test: save, load, continue; compare with uninterrupted run.
4. Look at the save code: version, migrations, atomic write, corrupt handling.
5. Profile one hot scene on the lowest device: GC allocations, spawn cost.
6. Check tests: pyramid shape, determinism, CI gates.
7. Report as: blockers (data loss, determinism holes), risks (boundary leaks), debts (naming, structure).

## Mobile specifics

- Background kills are normal. Only pause and background callbacks are reliable; save there. Do not depend on a quit hook.
- Interruptions (calls, notifications, share sheets) must pause the sim cleanly; pushdown states make this trivial.
- Allocation spikes and GC are felt as hitches. Pool, reuse collections, avoid LINQ and string building in hot paths; measure on the lowest device.
- Battery and heat: prefer 30 Hz sims for slow games; stagger AI ticks; cap frame rate; avoid constant polling.
- Storage and memory are small and shared. Keep saves small, textures budgeted, and streams limited.
- Cloud sync is intermittent: never block play on network; retry with backoff; show last sync time.
- Clocks are unreliable and user-editable. Use server time for anything with value (events, timers that pay out), device time only for cosmetics.
- Install sizes and cold start time matter for retention; defer heavy initialisation behind a loading screen.

## Anti-patterns

| Anti-pattern | How to detect it | Fix |
|---|---|---|
| Logic in UI callbacks | Rules inside `_on_button_pressed`; cannot run headless | Extract to core action |
| Global random in core | `randi()`, `Random.Range` in rule code; replays diverge | Seeded RNG in state |
| God singleton | One `GameManager` touched by everything | Split by layer; services behind interfaces |
| Boolean-flag state | Many `is_x and not is_y` conditions | FSM with explicit states |
| Event soup | String events with no owner; cascades | Few typed topics; core events as data |
| Premature ECS | ECS adopted at 50 entities | Plain components; measure |
| Saves without version | Single JSON blob, no `version` | Add version now; migrate forward |
| Writing over the only copy | `save` truncates file then writes | Tmp + rename + backup |
| Trusting device clock | Rewards computed from `Time.now` | Server time or clamp and verify |
| Constants in code | Designer requests need engineers | Tuning data and schema |
| Per-frame allocations | GC spikes in profiler | Reuse, pool, cache |
| Hard-coded strings | Missing translations, concatenated plurals | Keys and ICU-style plurals |
| Mocking nothing | Tests need real SDKs | Null service implementations |

## Using the ontology

- Core `state` maps to the project's game state in `.gamestudio/` only through the design contract; the **ontology** (`game-ontology`) describes loops, resources and content units that the core implements as rules and data.
- Actions correspond to ontology **verbs**; events correspond to observable **outcomes** that telemetry and feedback hook into.
- Resource flows (sources, sinks, converters, gates) become core state fields plus rules; `economy_sim.py` models them before you write them.
- Content units are data files validated against schemas (`${CLAUDE_PLUGIN_ROOT}/scripts/schemas/`); validate with `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_json.py`.
- Evidence for the five gates comes straight from this architecture: static and unit gates from the engine runners, the playthrough gate from `tools/playtest/runner.gd` or the Unity `Game.EditorTools.PlaytestRunner.Run` (`Assets/_Game/Editor/PlaytestRunner.cs`), bots for difficulty.
- Event names feed `event_taxonomy.py`, which turns the event contract into analytics stubs for Godot or Unity.
- Reference commands (Godot): `godot --headless --path <project> -s res://tools/ci/run_tests.gd -- --out=<abs>/unit.xml` and `... -s res://tools/playtest/runner.gd -- --mode=script --script=res://tests/playthroughs/smoke.json --out=<abs>/playthrough.json`.
- Reference commands (Unity, from `${CLAUDE_PLUGIN_ROOT}/templates/unity-starter/README.md`): `Unity -batchmode -nographics -projectPath <p> -runTests -testPlatform EditMode -testResults <abs>/unit.xml -logFile <abs>/unity.log` and `Unity -batchmode -nographics -projectPath <p> -executeMethod Game.EditorTools.PlaytestRunner.Run -gsMode script -gsScript Assets/_Game/Tests/Playthroughs/smoke.json -gsOut <abs>/playthrough.json -quit`.

## Reference library

| File | What it contains | When to read it |
|---|---|---|
| `references/sim-core-presentation.md` | Layers and dependency rule; core contract and invariants; Godot template mapping; Unity assembly and C# interface; determinism rules; action/event vocabulary design; presentation consumption; services; headless tooling; replays; migration recipe; checklist | Starting a project; reviewing the boundary; adding a mechanic; making a game testable headlessly |
| `references/patterns-and-ai.md` | Pattern chooser; fixed timestep; FSM/HFSM/pushdown; command/undo/replay; event bus; pooling; composition vs ECS; locator vs DI; data-driven design; spatial partitioning; AI selection, behaviour trees, utility AI, GOAP, steering, director AI; testing AI | Choosing a pattern; building enemy or NPC behaviour; fixing hitches; designing pacing |
| `references/data-persistence-and-quality.md` | Save buckets and formats; atomic writes; migrations; corruption recovery; cloud conflict strategies; remote config layers; localisation tables; module boundaries; testing pyramid; allocation-aware rules; logging; review checklist | Designing saves or sync; shipping remote config; setting up CI and tests; code review |

## Related skills

- `gameplay-programming` — the math, movement and system recipes that run inside the core.
- `multiplayer-backend` — networking models, backends and server authority for the same core.
- `engine-godot` — Godot specifics: scenes, GDScript, export and tooling.
- `engine-unity` — Unity 6 specifics: assemblies, URP, editor scripting.
- `engine-alternatives` — other engines and how the split ports to them.
- `mobile-performance` — profiling, budgets and device tiers.
- `qa-testing` — test strategy, bots, deterministic playthroughs, visual QA.
- `game-ontology` — vocabulary and schemas the core implements.
- `liveops` — remote config, events and experiments in operation.
- `economy-design` — economy models that become core state and data.
- `player-analytics` — events and telemetry design.
- `production` — scope, milestones and technical risk management.
