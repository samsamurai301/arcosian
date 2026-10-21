# Programming patterns and game AI

A working catalogue of the patterns that recur in shipped mobile games (fixed timestep, state machines, command/undo/replay, event bus, pooling, composition versus ECS, service location and DI, data-driven design, spatial partitioning) and the AI toolbox that sits on top (FSM, behaviour trees, utility AI, GOAP, steering, director AI). Each entry says what problem it solves, when to reach for it, when not to, and how to write it so it survives a mobile device and a headless test. The pattern framing owes a debt to Robert Nystrom's "Game Programming Patterns" (2014); the examples, trade-offs and code here are written fresh for this studio's sim-core architecture.

## Contents

1. Choosing a pattern: decision table
2. Fixed timestep and the game loop
3. State machines: FSM, HFSM, pushdown
4. Command, undo and replay
5. Event bus and observers
6. Object pooling
7. Composition, components and ECS
8. Service locator and dependency injection
9. Data-driven design
10. Spatial partitioning
11. AI: choosing a technique
12. FSM and behaviour trees
13. Utility AI
14. GOAP
15. Steering behaviours
16. Director AI and dynamic pacing
17. Testing AI

## 1. Choosing a pattern

| Symptom | Reach for | Avoid |
|---|---|---|
| Physics or movement differs between fast and slow phones | Fixed timestep with accumulator | Multiplying everything by variable `dt` in rules |
| Entity has many `if (state == ...)` branches | FSM, then HFSM if states share behaviour | Boolean flags per condition |
| Need undo, replay, tutorial scripts, bot input | Command objects or action dictionaries | Mutating state from UI callbacks |
| Systems need to react without knowing each other | Event bus (typed, few topics) | Global event string soup with no owner |
| Spawn/despawn spikes cause frame hitches | Pool | Instantiate in hot paths |
| Hundreds of similar entities | Struct-of-arrays or ECS | Deep inheritance with virtual update per entity |
| Need to swap ads/IAP/save per platform and in tests | Service interface plus null implementation | Static calls into SDKs from rules |
| Designers keep asking engineers to change numbers | Data files, schema, validation | Constants in code |
| "Who is near me?" queries dominate | Grid or quadtree | N^2 loops once N exceeds a few hundred |

Default posture: the simplest thing that keeps the core deterministic and testable. A match-3 or merge game needs none of ECS, GOAP or quadtrees; a swarm survivor needs pooling, spatial hashing and probably data-oriented storage.

## 2. Fixed timestep and the game loop

Problem: rules that run per rendered frame behave differently at 30, 60 and 120 Hz and cannot be replayed.

Pattern: accumulate real elapsed time, run the sim in constant steps, render once with interpolation.

```gdscript
const STEP: float = 1.0 / 60.0
const MAX_STEPS_PER_FRAME: int = 5
var _acc: float = 0.0

func _process(delta: float) -> void:
	_acc += minf(delta, 0.25)                    # clamp after a hitch or resume
	var steps: int = 0
	while _acc >= STEP and steps < MAX_STEPS_PER_FRAME:
		sim.apply({"type": "tick"})              # one step, deterministic
		_acc -= STEP
		steps += 1
	if steps == MAX_STEPS_PER_FRAME:
		_acc = 0.0                               # drop time rather than spiral
	view.render(_acc / STEP)                     # alpha for interpolation
```

```csharp
void Update() {
    acc += Mathf.Min(Time.unscaledDeltaTime, 0.25f);
    int steps = 0;
    while (acc >= Step && steps++ < MaxSteps) { sim.Apply(Tick); acc -= Step; }
    view.Render(acc / Step);
}
```

Decisions:

| Choice | Guidance |
|---|---|
| Step rate | 30 Hz saves battery for slow games; 60 Hz for action; networked games choose the tick rate first (see `multiplayer-backend`) |
| Clamp | Always clamp accumulated time; background resume can deliver minutes |
| Interpolation | Render previous and current state blended by alpha; without it 30 Hz sims look steppy at 60 fps |
| Turn-based or event-driven games | No loop at all: `apply(action)` only. Do not add a tick to a puzzle game |
| Idle games | Tick is a coarse accumulator; offline time is one big step with closed-form math (see `gameplay-programming`) |
| Engine physics | Godot `_physics_process` and Unity `FixedUpdate` give a fixed step but use floats and engine solvers; fine for feel, not for lockstep |

## 3. State machines

FSM: one current state, explicit transitions, enter/exit hooks. Use it for entity behaviour, UI flows, game flow (boot, menu, play, pause, results), tutorial steps and purchase flows.

```gdscript
enum S { IDLE, CHASE, ATTACK, STUNNED }
var state: S = S.IDLE

func step(ctx: Dictionary) -> void:
	var next: S = _transition(state, ctx)
	if next != state:
		_exit(state); state = next; _enter(state)
	_update(state, ctx)

func _transition(s: S, ctx: Dictionary) -> S:
	match s:
		S.IDLE:  return S.CHASE if ctx.dist < 8.0 else s
		S.CHASE: return S.ATTACK if ctx.dist < 1.5 else (S.IDLE if ctx.dist > 12.0 else s)
		S.ATTACK: return S.CHASE if ctx.dist > 2.0 else s
		_: return s
```

Rules: transitions in one function (a table) so you can read and test them; hysteresis (enter at 8, leave at 12) prevents flapping; any state may be interrupted by a global transition (stun, death) checked first; log transitions in debug builds.

HFSM (hierarchical): states grouped under parents that handle shared transitions. Use when 3+ states share the same escape (all combat states can be stunned, all UI screens can show a modal). Implementation: each state has an optional parent; unhandled events bubble up.

Pushdown automaton: a stack of states. Push a modal (dialog, tutorial overlay, pause) and pop to return exactly where you were, with no "previous state" bookkeeping. Ideal for UI navigation and for interrupt handling (incoming call pauses play, pop resumes).

| Technique | Good for | Breaks down when |
|---|---|---|
| FSM | up to roughly 8 states with simple triggers | transitions between every pair appear (state explosion) |
| HFSM | shared parent behaviours | parents start needing their own conditions that conflict with children |
| Pushdown | modal flows, interrupts | you need two states active at once (use concurrent FSMs or components) |
| Behaviour tree | reactive decision priority | tiny logic (overkill) |

State machine for game flow in the sim core: keep `status` as data (`playing`, `won`, `lost`) and make every action check it, as the Godot template's `_move` does with `game_over` rejections. Presentation flow (scenes) is a separate pushdown.

## 4. Command, undo and replay

A command is a reified action: data describing an intent, plus an executor. The studio core already uses data-shaped actions (`{"type":"move","dir":"left"}`), which gives you replay for free and undo with one of two strategies.

| Undo strategy | How | Use when |
|---|---|---|
| Snapshot | Push `to_dict()` before each action; undo restores | State is small (puzzle boards); simplest and safest |
| Inverse command | Each action returns the data needed to invert it | State is large (open world, big boards) or you need fine-grained undo |
| Re-simulate | Keep seed + action log; undo = reload and replay N-1 actions | Deterministic core and cheap steps; also gives rewind scrubbing |

Concerns: RNG state must be in the snapshot, otherwise undo then redo yields different spawns (and players exploit it by undoing until a favourable draw; decide on purpose whether that is allowed). Limit undo depth and make it a monetisable or earned resource only if the design wants it. For input buffering, queue commands with a timestamp and discard stale ones.

Replay file: `{rules_version, seed, actions[], result_hash}`. Uses: bug reports ("attach replay"), tutorials (scripted actions drive the real sim), attract mode, daily challenge validation, ghost races, regression tests in CI, bot corpora. Compress by run-length encoding repeated ticks. Version rules; a replay is only valid for its `rules_version`.

## 5. Event bus and observers

Two different things share the name:

1. Core events: the ordered list returned by `apply`. Synchronous, data, owned by the sim. This is the main path.
2. Service bus: a signal hub for decoupling presentation and services (`sim_events`, `app_paused`, `settings_changed` in the Godot template's `services/event_bus.gd`).

Guidelines: keep the number of topics small and typed; document the owner of each; subscribers must not mutate what they observe; unsubscribe on teardown (leaked subscriptions to freed nodes are a classic crash source); avoid cascades where one handler emits another event that emits a third (hard to debug, order-dependent). If you find yourself needing a return value from an event, you wanted a direct call or a query service.

Debugging aid: a debug overlay or log ring buffer of the last N events with timestamps. It is the cheapest tool for "why did that happen".

## 6. Object pooling

Why on mobile: allocation spikes and GC collections cause hitches (Unity's managed GC; Godot's node instantiate and free cost), and instantiating scenes is expensive. Pool anything that spawns frequently: projectiles, hit effects, damage numbers, tiles, coins, audio players.

```gdscript
class_name Pool extends RefCounted
var _scene: PackedScene
var _free: Array[Node] = []
var _parent: Node

func _init(scene: PackedScene, parent: Node, prewarm: int = 0) -> void:
	_scene = scene; _parent = parent
	for i in prewarm: _free.append(_make())

func acquire() -> Node:
	var n: Node = _free.pop_back() if not _free.is_empty() else _make()
	n.process_mode = Node.PROCESS_MODE_INHERIT
	n.show()
	return n

func release(n: Node) -> void:
	n.hide()
	n.process_mode = Node.PROCESS_MODE_DISABLED
	_free.append(n)

func _make() -> Node:
	var n: Node = _scene.instantiate()
	_parent.add_child(n)
	return n
```

Unity: `UnityEngine.Pool.ObjectPool<T>` exists; use `actionOnGet`/`actionOnRelease` to reset state. Checklist: reset every field on acquire (stale velocity, tweens, particle state are the bugs); cap the pool and decide overflow policy (grow, or drop the oldest effect); prewarm during a loading screen, not mid-fight; keep pooled things out of the sim (the core holds ids and data, the view pools nodes); stop tweens and timers on release.

Don't pool what is created rarely, and don't pool without measuring: pools hide leaks and add reset bugs. Pool when the profiler shows spawn cost or GC spikes.

## 7. Composition, components and ECS

Inheritance trees (Enemy -> FlyingEnemy -> FlyingShootingEnemy) collapse when design asks for a combination. Composition assembles behaviour from small parts: `Health`, `Mover`, `Shooter`, `Loot`. Godot scenes and Unity GameObjects are already component-based; use them that way.

| Level | Description | Use when |
|---|---|---|
| Plain composition | Node or GameObject with child components | Up to a few hundred entities; most mobile games |
| Component data in core | Core keeps `entities: Array` of dictionaries or structs, systems loop over them | You need determinism and headless sim for many entities |
| Data-oriented arrays | Parallel typed arrays (`pos_x[]`, `hp[]`) or `PackedFloat32Array` | Thousands of entities; cache friendliness matters; Godot packed arrays are a good fit |
| Full ECS (Unity DOTS/Entities, or a library) | Archetypes, jobs, Burst | Truly massive counts or heavy simulation; high learning and tooling cost; rarely justified for casual mobile |

Heuristic: count the entities at peak on the lowest target device. Under about 300 active, plain components win on simplicity. Between 300 and a few thousand, use packed arrays in the sim and draw with multimesh/instancing or batched sprites. Above that, evaluate ECS and check that your team can debug it.

Anti-pattern: "ECS because it is modern". The cost is tooling, debugging and onboarding; pay it only when numbers demand.

## 8. Service locator and dependency injection

Services (audio, save, analytics, ads) need to be reachable and replaceable. Options:

| Option | Pros | Cons |
|---|---|---|
| Autoload/singleton accessed globally | Trivial in Godot; fine for leaf services | Hidden dependencies; hard to swap in tests unless the autoload itself is mockable |
| Service locator (`Services.get("audio")`) | One registration point; swap implementations at boot | Still hidden dependency; runtime lookup failures |
| Constructor/property injection | Explicit; core stays pure | More wiring code; frameworks (Zenject/VContainer on Unity) add weight |

Studio default: core receives everything it needs as data and never calls services. Presentation and service classes use autoloads (Godot) or a small locator (Unity) with interface plus null implementation (`NullAds`, `NullAnalytics`). In tests the bootstrap registers nulls. Reach for a DI container only when a Unity project has many cross-cutting services and a team larger than a few people; keep scopes simple (project, scene).

## 9. Data-driven design

Move numbers, tables and content out of code into validated data: tuning, level layouts, enemy stats, item definitions, shop catalogues, localisation, event schedules. Benefits: designers iterate without builds; remote config can override; the sim reads data so balance sims can mutate it; AI-assisted content generation targets schemas.

Practices:

- One schema per data kind (JSON Schema or typed resource), validated in CI (`validate_json.py` in this plugin does it for the studio's own schemas).
- Stable string ids, never array indices, as references; ids survive reordering and remote overrides.
- Defaults in code, overrides in data (as `core/tuning.gd` does): a missing file or key never crashes.
- Separate content (what exists) from tuning (how much) from presentation (how it looks).
- Expression fields (damage formulas) are code in disguise: restrict to a tiny vetted grammar, or use named formula ids implemented in code.
- Data hot-reload in dev builds for faster tuning loops.
- Reference-check pass at load: every id mentioned exists; every required field present; numeric ranges sane. Fail loudly in dev, fall back safely in release.

Anti-pattern: building a general scripting language in JSON. If designers need logic, give them composable named behaviours (triggers, conditions, effects) with a bounded vocabulary.

## 10. Spatial partitioning

| Structure | Best for | Notes |
|---|---|---|
| Uniform grid / spatial hash | Many same-sized entities, bounded world (swarms, bullets, match-3 boards) | Cell size about the typical query radius; update on move; O(1) neighbours |
| Quadtree | Varied sizes and clustered distributions | Rebuild or update cost; good for static plus few dynamic |
| BVH / engine broadphase | 3D and physics | Use the engine's |
| Sorted sweep (sweep and prune) | 1D-dominant layouts, scrolling runners | Simple and cache friendly |

Procedure: profile first; if proximity queries exceed a few percent of frame time, add a grid. Keep the grid in the core as plain arrays so headless sims share it. Pitfalls: entities exactly on cell borders (query neighbouring cells); entities spanning cells (insert in all or use centre plus radius check); stale cells after teleports.

## 11. AI: choosing a technique

| Need | Technique | Complexity |
|---|---|---|
| A few modes, clear triggers | FSM | low |
| Reactive priorities (flee > attack > patrol) with reusable pieces | Behaviour tree | medium |
| Many competing desires scored continuously (companions, shopkeepers, sim needs) | Utility AI | medium |
| Open-ended goal planning where designers add actions, not scripts | GOAP | high |
| Local movement (avoid, flock, follow) | Steering | low-medium |
| Whole-session pacing and difficulty feel | Director AI | medium |
| Puzzle/board bots for balance | Search (greedy, beam, MCTS) over the sim | medium |

Most mobile games need FSM plus steering plus a director. Choose by the number of behaviours and how often design changes them, not by prestige. The best AI is legible: the player can predict and exploit it. Telegraph before attacking; make mistakes on purpose in low tiers.

## 12. FSM and behaviour trees

Behaviour tree (BT): a tree ticked each decision step; nodes return success, failure or running.

| Node | Behaviour |
|---|---|
| Selector (fallback) | Try children in order until one succeeds |
| Sequence | Run children in order until one fails |
| Decorator | Modify a child: invert, repeat, cooldown, until-fail |
| Condition | Check blackboard data |
| Action | Do something, may return running |

```gdscript
# priority: flee > attack > patrol
func tick(bb: Dictionary) -> int:           # 0 fail, 1 success, 2 running
	if _flee(bb) != 0: return 1
	if _attack(bb) != 0: return 1
	return _patrol(bb)
```

Practical guidance: store running state per agent (which child is running), not in the shared tree; use a blackboard dictionary for shared data (target, last-seen position); put cooldowns in decorators; tick at a lower rate than render (4 to 10 Hz is typical) and stagger agents across frames; keep leaf actions short. Compare to FSM: a BT is better at priority and reuse, an FSM at explicit modes with clear entry/exit effects. Combining them (FSM for macro modes, BT inside a mode) is common.

## 13. Utility AI

Score each candidate action by considerations mapped through response curves, combine, pick the best (or sample among the top).

```
score(action) = weight * product_or_mean( curve_i(input_i) )
choose argmax score          # or weighted random among scores within 10% of best
```

| Piece | Guidance |
|---|---|
| Inputs | Normalise to 0..1 (health fraction, distance / max range, hunger) |
| Curves | Linear, quadratic, logistic, inverse; plot them; most bugs are curve bugs |
| Combine | Multiplication makes any zero a veto; add a compensation factor when many considerations multiply |
| Stability | Add inertia: bonus for the current action to avoid dithering; minimum commit time |
| Debug | Dump the score table for the chosen agent; without it tuning is guesswork |
| Tuning | Data-driven curves in files so designers tune; log decisions in playtests |

Good for: companions deciding between heal and attack, NPC needs, city or colony sims, enemy target selection. Bad for: strict scripted sequences.

## 14. GOAP

Goal-oriented action planning: actions declare preconditions and effects over a world-state of facts; a planner (A* over action sequences) finds a cheap sequence that satisfies a goal.

Components: world state (set of key/values), goals with priority, actions with cost, preconditions, effects, and an executor for each. Replan when the plan is invalidated.

Use when: agents must assemble solutions from many small capabilities and designers want to add new actions without rewiring (stealth or survival sims). Avoid when: the behaviour set is small (FSM or BT is simpler and more predictable), or when designers need tight scripted control; planning is harder to debug and to tune for fun. On mobile, plan rarely, cap search depth, cache plans, and keep the fact set small (bitmasks). Many shipped "GOAP" systems are really BT plus utility with a tiny planner; that is fine.

## 15. Steering behaviours

Reynolds-style steering produces local movement from simple forces: seek, flee, arrive (slow near target), pursue/evade (predict), wander, separation, alignment, cohesion, obstacle avoidance, path following. Combine by weighted sum, then clamp speed and turn rate.

```gdscript
func arrive(pos: Vector2, target: Vector2, max_speed: float, slow_radius: float) -> Vector2:
	var to: Vector2 = target - pos
	var d: float = to.length()
	if d < 0.001: return Vector2.ZERO
	var speed: float = max_speed * minf(d / slow_radius, 1.0)
	return to / d * speed                       # desired velocity; steering = desired - current
```

Guidance: use priority or weights per context (flee outranks cohesion); add a small random jitter to break symmetry; for crowds, separation by spatial hash neighbours only; for pathing around obstacles combine A* paths (see `gameplay-programming`) with steering for local smoothing; cap forces to avoid jitter. For deterministic sims, steering in the core must be fixed-timestep and use the seeded RNG.

## 16. Director AI and dynamic pacing

A director observes player state and adjusts content intensity, in the tradition of tension and release popularised by games such as Left 4 Dead (Valve's "AI Director"). In mobile terms it manages spawn rates, drop rates, assists and levels' difficulty feel.

Minimal director:

```
stress = f(recent damage, near-death moments, failures in a row, time since last reward)
if stress low and time since peak > T:  raise intensity (spawn wave, rarer event)
if stress high:                          lower intensity, grant relief (health drop, easier next level)
```

Design rules: state the player-experience target first (relief after peak, rising tension, mastery moments); keep adjustments within bounds so the game stays honest; never silently rig outcomes in games with real-money stakes or competitive ranking; log director decisions so QA can reproduce; expose a setting or telemetry hook. Ethical note: rubber-banding that pushes players towards purchases is a dark pattern; use it only to protect fun and fairness (see `legal-ethics`, `economy-design`).

Related, cheaper variants: adaptive difficulty after N consecutive failures (small assist, never hidden at the top of a ranked mode), pity timers (see `gameplay-programming`), weighted level selection from a pool by recent performance.

## 17. Testing AI

- Unit-test decisions as pure functions: given a context dictionary, expect a chosen action.
- Seeded scenario tests: fixed seed, run 1,000 ticks, assert invariants (never stuck, never leaves bounds, reaches the goal within N ticks).
- Property tests for steering: speed never exceeds max; no NaN.
- Bot-vs-bot or bot-vs-content to check difficulty: win rate bands per level (see `progression-difficulty` and the `playtest` skill).
- Visual debug: draw state labels, paths, steering vectors and utility scores in a debug overlay toggled by a gesture.
- Watch for time-slicing bugs: agents ticked at staggered rates must still be deterministic (stagger by stable id, not by frame count of a variable-rate loop).
