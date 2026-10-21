# Sim-core + presentation: the studio core abstraction

This is the one architectural idea the whole studio standardises on: game rules live in a deterministic, engine-free simulation core that accepts actions and returns events; everything visible, audible or platform-specific lives outside it and only reads state, sends actions and animates events. It is what makes headless tests, scripted playthroughs, bots, replays, balance sims and save/restore cheap, and it is what lets the same design move between Godot and Unity. This file defines the contract, maps it onto the two reference templates (`templates/godot-mobile` and `templates/unity-mobile`, which implement the same sample game with the same event vocabulary and the same PCG32 stream), gives worked sketches in GDScript and C# that quote the real file and member names, and ends with a migration recipe and review checklist.

## Contents

1. The three layers and the dependency rule
2. The core contract (apply, events, state, rng)
3. Godot mapping (what each template file does)
4. Unity mapping (assemblies and C# interface)
5. Determinism rules
6. Actions and events: designing the vocabulary
7. Presentation: consuming events
8. Services layer
9. Headless tooling that falls out of the split
10. Saves, replays and snapshots
11. Migrating an existing project
12. Review checklist

## 1. The three layers and the dependency rule

```
presentation/  nodes, scenes, tweens, input, audio cues     reads state, sends actions, plays events
services/      save, audio, haptics, ads, iap, analytics     talk to each other through an event bus
core/          pure data + rules, no engine types, seeded    apply(action) -> events
```

Dependencies point one way: presentation -> core, services -> core (for save data only), core -> nothing. A core file that mentions `Node`, `Input`, `Time`, an autoload, a scene path or a global random function is a bug. The rule is mechanical, so enforce it mechanically: in Godot grep `core/` for `Node`, `get_tree`, `randi(`, `randf(`, `Time.`, `OS.`; in Unity put core in an assembly definition with `noEngineReferences` enabled so the compiler refuses `UnityEngine`.

Why not just "keep logic out of UI"? Because that advice is unenforceable. A layer that cannot import the engine cannot cheat.

| Question | Core | Presentation | Service |
|---|---|---|---|
| Does a merge produce 8? | yes | no | no |
| How long does the merge pop animation last? | no | yes | no |
| Is the player allowed to move? | yes | asks core | no |
| Which sound plays on a merge? | no | yes (event -> cue) | audio service plays it |
| When is the save written? | produces the dictionary | no | save service (on pause, on milestones) |
| Which RNG draws the spawn? | yes (seeded, in state) | no | no |
| Screen shake direction? | no | yes (cosmetic random is fine) | no |
| Ad shown after a loss? | emits `lose` | decides to ask | ads service enforces caps |

## 2. The core contract

Every studio game exposes the same four things from its core, whatever the genre:

| Member | Meaning |
|---|---|
| `apply(action) -> events` | The only way to mutate state. Takes one action, returns an ordered list of events. Rejections are events, not exceptions. Godot: `Sim.apply(Dictionary) -> Array` of event dictionaries. Unity: `Sim.Apply(GameAction) -> List<SimEvent>`, where `GameAction.FromDict` lets playthrough JSON drive it. |
| `to_dict() / load_dict(d)` | Lossless round trip of all state including RNG state. JSON-safe (int64 as strings). Unity names: `Sim.ToDict()` / `Sim.LoadDict(Dictionary<string, object>)`; `MiniJson.Write` turns the dictionary into text. |
| state queries | Read-only: `lookup(path)` for tests (a method of `GameState` in both templates: `state.lookup`, `State.Lookup`), plus typed getters for the view. |
| tuning input | All numbers a designer may change arrive as data (`tuning.json`), never constants buried in rules. |

Invariants worth writing tests for:

1. Same seed plus same action list gives the same event list and the same final `to_dict()`.
2. `load_dict(to_dict())` then continuing equals continuing without the round trip.
3. An invalid action changes nothing (state hash before equals after) and returns a `rejected` or `invalid_*` event.
4. Events are sufficient to rebuild the view: replaying all events from `new_game` onto an empty view yields what `to_dict()` describes.
5. No event references a node, resource path or time.

The fourth invariant is the one teams skip and regret: if the view needs to peek into state to know what happened, the event vocabulary is too thin.

## 3. Godot mapping (templates/godot-mobile)

The sample game is a deterministic 5x5 merge puzzle. Names below are real files in the template.

| File | Role |
|---|---|
| `core/sim.gd` | `apply(action: Dictionary) -> Array`, plus `new_game`, `to_dict`, `load_dict`, the test helper `set_grid`, and static pure helpers (`slide_grid`, `can_move`) so tests and bots can call rules without a full sim |
| `core/game_state.gd` | Plain data: `size`, `grid`, `score`, `moves`, `status`, `seed_value`, `rng`; `lookup(path)` resolves playthrough `expect` paths; `to_dict` / `from_dict` |
| `core/rng.gd` | PCG32 (`next_u32`, `rand_int`, `rand_float`) with state saved as strings; the only randomness core may use |
| `core/tuning.gd` + `core/data/tuning.json` | Designer-owned numbers (`size`, `win_tile`, `initial_tiles`, `spawn_four_chance`) with safe defaults via `Tuning.load_tuning()` |
| `core/save_data.gd` | Save schema, `default_save()`, `migrate()` chain |
| `services/event_bus.gd` | Autoload signal hub (`sim_events`, `game_over`, `settings_changed`, `app_paused`, `app_resumed`) |
| `services/save_service.gd` | Atomic write (temp file + rename) with `.bak` fallback |
| `presentation/game.gd`, `board_view.gd` | `try_move(dir)` sends `{"type":"move","dir":...}`; `BoardView.play(events, grid)` animates the returned events, then `sync(grid)` snaps to state |
| `tools/playtest/runner.gd` | Script and bot modes over `core/` only |
| `tools/perf/perf_probe.gd` | Perf-gate producer: plays the real game scene (`presentation/game.tscn`) with a greedy bot through `Game.try_move` and writes a perf-report JSON (desktop proxy; its headless mode is CPU-only) |
| `tools/ci/check_all.gd`, `run_tests.gd` | Static gate (loads every `.gd`, `.tscn` and `.json`, so parse errors fail it) and unit gate (JUnit XML). The template does not ship the `core/` token grep from section 1; add it to CI if you want the boundary enforced mechanically |

Skeleton of the loop on the Godot side, abridged from `presentation/game.gd` (`try_move` is connected to the swipe detector's `swiped` signal and to the arrow keys):

```gdscript
extends Control
const Sim = preload("res://core/sim.gd")
const BoardView = preload("res://presentation/board_view.gd")

var sim: Sim = Sim.new(1)
var board: BoardView
var _busy: bool = false

func try_move(dir: String) -> void:
	if _busy:
		return
	var events: Array = sim.apply({"type": "move", "dir": dir})
	var kind: String = events[0].type
	if kind == "invalid_move" or kind == "rejected":
		Haptics.light()                       # feedback only; state is untouched
		return
	_busy = true
	EventBus.sim_events.emit(events)          # audio/haptics/analytics subscribe
	await board.play(events, sim.state.grid)  # animation owns time, not the sim
	_busy = false
	refresh()                                 # snap HUD and board to state
```

Rules the template follows that you should keep: core scripts `extends RefCounted`; constants preloaded rather than relying on global `class_name` registration order; events are plain `Dictionary` with a `"type"` string; RNG state serialised as strings because JSON numbers lose precision above 2^53; `Array[int]` typed arrays for grids.

Adding a mechanic to the template, in order: write the rule as a static pure function; write a unit test with `set_grid`-style helpers; add the action and events to `apply`; extend `lookup` paths so playthroughs can assert; extend `board_view.play` for the new events; add a playthrough step. Never start in the view.

## 4. Unity mapping (templates/unity-mobile)

The Unity template mirrors the same split with assemblies instead of folders (BLUEPRINT section 6 and 13). The files below are real; the C# block that follows is abridged from `Assets/_Game/Core/Sim.cs`, `GameState.cs` and `Rng.cs` and keeps their member names and signatures. Status (see the template README): the Core and EditMode tests compile and pass on the plain .NET SDK through `tools/dotnet-harness`, while the Presentation and Editor code was written without Unity installed and still needs a first open in Unity 6.

```
Assets/_Game/
  Core/            Game.Core.asmdef          noEngineReferences = true, references nothing
                   Sim.cs  GameState.cs  Rng.cs  Tuning.cs (+ MiniJson)  SaveData.cs  Playthrough.cs
  Presentation/    Game.Presentation.asmdef  references Game.Core, Unity.InputSystem, UnityEngine.UI
                   Bootstrap.cs  BoardView.cs  SwipeInput.cs  ScreenShake.cs
    Services/      EventBus  SaveService  AudioService  Haptics  Analytics  Ads  Iap  SafeArea (same assembly)
  Editor/          Game.Editor.asmdef        Editor platform only; references Game.Core and Game.Presentation
                   PlaytestRunner  SceneBuilder  BuildScript (+ GsArgs)  ScreenshotCapture  (namespace Game.EditorTools)
  Tests/EditMode/  Game.Tests.EditMode.asmdef  references Game.Core and Game.Presentation (it tests SwipeInput.Classify); SimTests.cs
  Tests/Playthroughs/smoke.json              same format as Godot
  Data/tuning.json                           size, win_tile, initial_tiles, spawn_four_chance
```

`Playthrough.RunScript` and `Playthrough.RunBots` live in Core (so the .NET harness can run them); `Editor/PlaytestRunner.Run` only parses the `-gs*` flags, calls them and writes the playtest-report JSON.

```csharp
// Abridged: member signatures as in the template, method bodies omitted.
namespace Game.Core
{
    // Event type names, shared with the Godot template ("new_game", "slide", "merge", ...).
    public static class SimEventType
    {
        public const string NewGame = "new_game";
        public const string Slide = "slide";
        public const string Merge = "merge";
        public const string Score = "score";
        public const string Spawn = "spawn";
        public const string Win = "win";
        public const string Lose = "lose";
        public const string InvalidMove = "invalid_move";
        public const string Rejected = "rejected";
    }

    // One fact, described as data. Which fields are filled depends on Type:
    // slide{Dir,Moves}, merge{At,Value}, score{Delta,Total}, spawn{At,Value}, win/lose{Score},
    // new_game{Seed}, invalid_move{Dir}, rejected{Reason}.
    public sealed class SimEvent
    {
        public string Type; public string Dir; public int At = -1; public int Value;
        public int Delta; public int Total; public int Score; public long Seed;
        public string Reason; public List<TileMove> Moves;
        public override string ToString();   // stable text form: tests compare event streams with it
    }

    // Input to the sim: {"type":"move","dir":"left|right|up|down"} or {"type":"new_game","seed":n}.
    public sealed class GameAction
    {
        public string Type = ""; public string Dir = ""; public long? Seed;
        public static GameAction Move(string dir);
        public static GameAction NewGame(long seed);
        public static GameAction FromDict(Dictionary<string, object> d);   // playthrough JSON -> action
    }

    public sealed class Sim
    {
        public static readonly string[] Dirs = { "left", "right", "up", "down" };
        public GameState State { get; private set; }
        public Tuning Tuning { get; private set; }

        public Sim(long seed = 1, Tuning tuning = null);
        public List<SimEvent> NewGame(long seed);
        public List<SimEvent> Apply(GameAction action);                 // the only mutator; rejections are events
        public Dictionary<string, object> ToDict();                     // lossless, includes RNG state
        public bool LoadDict(Dictionary<string, object> d);             // false, state untouched, when malformed
        public void SetGrid(int[] values);                              // test helper
        public static SlideResult SlideGrid(int[] grid, int size, string dir);   // pure rule, used by bots too
        public static bool CanMove(int[] grid, int size);
    }

    public sealed class GameState                                       // plain data plus queries
    {
        public int Size; public int[] Grid; public int Score; public int Moves;
        public string Status;            // GameState.Playing | Won | Lost
        public long SeedValue; public Rng Rng;
        public object Lookup(string path);                              // playthrough expect paths; null when unknown
        public Dictionary<string, object> ToDict();
        public bool FromDict(Dictionary<string, object> d);
    }

    // PCG32 (XSH-RR): same stream as core/rng.gd for the same seed; state serialises as signed-decimal strings.
    public sealed class Rng
    {
        public Rng(long seed = 1, long seq = 54);
        public uint NextU32();
        public int RandInt(int n);       // [0, n)
        public double RandFloat();       // [0, 1)
        public Dictionary<string, object> ToDict();
        public void FromDict(Dictionary<string, object> d);
    }
}
```

Both engines must produce identical event streams for the same seed; that is a cheap cross-engine regression test when a studio ships the same design on both. The template already makes the event side typed (one `SimEvent` class whose `Type` comes from `SimEventType`, with `ToString()` as the comparison form) while keeping the action side data-shaped (`GameAction.FromDict`) so playthrough JSON can drive it. Split `SimEvent` into one sealed class per event only once the vocabulary stabilises.

The template has no `ISim` interface and no `legal_actions` method. Bots decide legality by calling `Sim.SlideGrid(...).Moved` per direction (see `Pick` in `Core/Playthrough.cs`); once a game has more actions than four directions, add a `LegalActions()` query on `Sim` and have bots, hints and softlock checks use it.

Unity specifics: use `ScriptableObject` or JSON for tuning and convert to plain C# data at the boundary so core never sees `UnityEngine.Object` (the template reads `Data/tuning.json` through `Tuning.Parse(string)`, which clamps and falls back to defaults); MonoBehaviours in Presentation get their `Sim` from a composition root, never from a static singleton that tests cannot reset (the template's `Bootstrap` creates and owns the `Sim`, builds the UI in code, and clears `Bootstrap.Current` in `OnDestroy`); avoid `System.Random` (algorithm may differ across runtimes) and `UnityEngine.Random` (global, unseeded in core). The template's presentation flow is `Bootstrap.OnSwiped` -> `Sim.Apply(GameAction.Move(dir))` -> `BoardView.Play(events, state)`, `ScreenShake`, `AudioService`, `Haptics`, then `EventBus.RaiseSimEvents(events)` for subscribers such as analytics.

## 5. Determinism rules

| Hazard | Rule |
|---|---|
| Global random | Only the seeded RNG held in state. One stream per concern if you need draw-order independence (loot vs AI vs spawns). |
| Iteration order | Never iterate a hash map to make a decision; Godot dictionaries keep insertion order, C# `Dictionary` does not guarantee it. Use sorted keys or arrays. |
| Time | Core receives ticks or an explicit `dt` in an action; it never reads a clock. Offline progress is an action `{"type":"offline","seconds":n}` with the clamp inside core. |
| Floats | Same-binary same-platform is usually stable; cross-platform is not guaranteed for transcendental functions. For lockstep or cross-engine replays use integers or fixed point. Puzzle and idle games rarely need more than integers plus careful rounding rules. |
| Frame rate | Fixed timestep for physics-like sims (see `references/patterns-and-ai.md`). Variable `dt` in rules makes replays diverge. |
| Float to int | Specify rounding (floor, banker, half-up) in the rule and test it; engines differ in defaults. |
| Collections order | Spawn lists, enemy ids, inventory slots get stable ids assigned by core, not by node instance ids. |
| Draw count | Add a draw to a rule and every later draw shifts; that changes replays and tuned seeds. Version the sim rules together with replay files (`rules_version`). |

## 6. Designing the action and event vocabulary

Actions are intents from the player or from a script: `move`, `place_block`, `use_booster`, `claim_reward`, `tick`, `offline`, `new_game`, `resume`. Keep them coarse enough that one action equals one player decision, fine enough that a bot can enumerate legal ones. Provide `legal_actions() -> Array` in core; bots, hint systems, tutorials and softlock detection all use it. (The sample game has only four actions, so the templates skip it and let the bots test each direction with the pure `slide_grid` / `SlideGrid` helper; add the query as soon as the action space grows.)

Events describe what changed, in causal order, with enough payload to animate without querying state:

| Good event | Why |
|---|---|
| `slide{dir, moves[{from,to,value,merged}]}` | Gives the view start and end for each tile |
| `merge{at,value}` | Triggers juice at a place with a magnitude |
| `score{delta,total}` | View never recomputes score |
| `spawn{at,value}` | Spawn animation without peeking |
| `win{score}` / `lose{score}` | Terminal state transitions are explicit |
| `rejected{reason}` / `invalid_move{dir}` | Feedback (shake, tooltip) without exceptions |

Naming: past-tense facts, lower snake case, stable across versions (analytics and replays key on them). Do not put presentation timing (`duration`) in events; the view decides pacing and may skip it for fast-forward or reduced motion.

Ordering rule: the first event after an action is the direct result, side-effects follow, terminal events come last. A view that processes events in order is always consistent.

## 7. Presentation: consuming events

Pattern: one `play(events)` coroutine that walks the list and dispatches per type; each handler returns when its animation completes, or immediately if `skip_animations` is set (tests, fast-forward, reduced motion, low power).

```gdscript
func play(events: Array) -> void:
	for e: Dictionary in events:
		match String(e.type):
			"slide": await _animate_slide(e.moves)
			"merge": _pop(e.at, int(e.value))        # fire and forget
			"spawn": _spawn_tile(int(e.at), int(e.value))
			"win", "lose": _show_end(String(e.type))
			"invalid_move": _shake()
```

The template's `BoardView.play(events, grid)` is a simplified version of this pattern: it tweens every `slide` move in parallel, snaps to the given grid with `sync(grid)`, then plays the merge and spawn pops. The Unity equivalent is `BoardView.Play(events, state)`, with `Render(state)` as the snap.

Input is translated to actions at the edge: a swipe detector maps touch deltas to `"left"` etc. (`presentation/swipe_detector.gd` emits `swiped(dir)`; Unity's `SwipeInput` raises `Swiped` and `Tapped`, and exposes `Classify` for tests). Input during animation: either queue one buffered action (feels responsive) or block; the template blocks with a `_busy` flag in `game.gd`, so choose per genre and write it down. After `play` completes, snap the view to state as a safety net (the template's `refresh()` calls `board.sync(sim.state.grid)`); in debug builds assert that the animated result equals the snapped result to catch missing events.

Pause, background and resume: the view can be destroyed and rebuilt at any time (scene change, memory warning). If the view can be rebuilt from `to_dict()` in one call, those cases cost nothing.

## 8. Services layer

Services are autoloads (Godot) or plain singletons behind an interface (Unity) that wrap platform capability: save, audio, haptics, analytics, ads, IAP, app lifecycle, safe area. Rules:

- Services subscribe to the event bus; core never calls them. Analytics maps events to telemetry; audio maps events to cues; haptics maps events to patterns. One mapping table per service, data-driven where possible.
- Every service has a null or mock implementation so tests and headless runs need no SDK. Ads and IAP in particular must compile and run without the SDK present.
- Services own their failure policy: ad fails to load, save write fails, purchase pending. Presentation sees a result event, never an exception.
- Lifecycle: `app_paused` flushes saves and analytics; `app_resumed` recomputes offline progress. Never rely on a quit callback on mobile; it may not run.

## 9. Headless tooling that falls out of the split

Because core is engine-free, these run in milliseconds without a renderer (commands are the binding ones from BLUEPRINT section 13):

| Tool | Uses | Output |
|---|---|---|
| Unit tests | `apply` and static helpers | JUnit XML from `run_tests.gd`; NUnit XML from the Unity EditMode run (`-runTests -testPlatform EditMode`) |
| Scripted playthrough | action list + `expect` paths | playtest-report JSON (`runner.gd --mode=script`, `PlaytestRunner.Run -gsMode script`) |
| Bots | legality query (`legal_actions`, or the sample's `slide_grid` / `SlideGrid` check) + policy (random, greedy) | win rate, softlock count (`--mode=bot --bot=greedy --runs=200`) |
| Balance sims | core run thousands of times | feed `economy_sim.py` assumptions or direct distributions |
| Replay verification | action log + seed | pass/fail on divergence |

Playthrough format (shared by both engines): `{"schema_version":"1.0","seed":1,"steps":[{"action":{"type":"move","dir":"left"},"expect":{"status":"playing","moves":{"op":">=","value":0}}}]}`. To make a new game testable you implement `lookup(path)` on the state and a legality query (`legal_actions()`, or per-action `slide_grid`-style checks as in the sample); nothing else. The Unity commands are in `templates/unity-mobile/README.md`: `Game.EditorTools.PlaytestRunner.Run` with `-gsMode script -gsScript Assets/_Game/Tests/Playthroughs/smoke.json -gsOut <abs>/playthrough.json`, or `-gsMode bot -gsBot greedy -gsRuns 200 -gsSeed 1`.

Bot time metrics in the template are estimates (a fixed per-move cost, 0.8 s per accepted move), not measurements; do not quote them as perf data. Measured frame cost comes from the Godot template's separate perf probe (`tools/perf/perf_probe.gd`, which drives the real scene rather than `core/` alone and writes a perf-report JSON); the Unity template has no equivalent.

## 10. Saves, replays and snapshots

- Persist `to_dict()` plus a `version`; see `references/data-persistence-and-quality.md` for migrations.
- A replay is `{rules_version, seed, actions[]}`. It is tiny, shareable (ghost runs, daily challenges, bug reports) and doubles as a regression test. Verify by re-running and comparing a final state hash.
- Snapshots for undo, rewind or rollback are `to_dict()` copies; for large states use deltas or command inversion (see patterns file).
- Daily challenge: seed from the date string through a stable hash, never from `hash()` builtins that may vary by platform; everyone gets the same board and you can validate scores server-side by replay (see `multiplayer-backend`).

## 11. Migrating an existing project

1. Pick one vertical slice (one rule, e.g. scoring). Extract it into a pure function with data in, data out; add three tests with real captured inputs.
2. Introduce the state object and `apply` for that slice. Make the old code call it and compare outputs in debug builds ("shadow mode") until identical.
3. Replace global random calls in the slice with the seeded RNG held in state.
4. Define the events the old code implicitly produced (sounds, particles, UI refresh) and route them through `play`.
5. Repeat slice by slice; resist rewriting everything at once. Stop when `core/` can run a full session headlessly.
6. Add the grep or assembly-definition guard so the boundary stays closed.

Typical effort signal: if extracting a rule needs more than a handful of engine references passed in, the rule is entangled with presentation state; split the decision (core) from the effect (view) first.

## 12. Review checklist

- [ ] No engine type, global random, clock or singleton access in `core/` (grep or asmdef enforces it).
- [ ] `apply` is the only mutator; rejections are events; invalid actions leave state untouched.
- [ ] State round-trips including RNG; int64 values serialised as strings.
- [ ] Tuning in data; no magic numbers in rules.
- [ ] Event vocabulary rebuilds the view; no `duration` or node refs in events.
- [ ] A legality query (`legal_actions`, or the sample's per-direction `slide_grid` / `SlideGrid` check) and `lookup` exist; at least one playthrough and one bot run in CI.
- [ ] Services use mocks headlessly; no SDK call from core.
- [ ] View can be rebuilt from state at any moment (resume, scene change).
- [ ] `rules_version` recorded with saves and replays.
- [ ] Debug assertion compares animated result with state snapshot.
