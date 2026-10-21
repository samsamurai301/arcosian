# GDScript and Project Structure

Summary: how to lay out a Godot 4 mobile project, write typed GDScript that passes the parser first time, use autoloads, signals, Resources and the node lifecycle correctly, and avoid the specific errors AI agents make (invented UIDs, Python idioms, wrong indentation). Written for Godot 4.5+ and correct on 4.7. Examples follow the conventions of `templates/godot-mobile/`.

## Contents
1. Project layout
2. Typed style guide
3. Language reference for agents (valid vs invalid)
4. Autoloads and the event bus
5. Signals
6. Resources and data
7. Node lifecycle
8. Scenes, UIDs and text files
9. Input and timing
10. Save data
11. Static analysis and formatting
12. AI-agent pitfalls checklist

## 1. Project layout

```
project.godot
export_presets.cfg
core/            RefCounted, deterministic, no Node, no autoload access
  rng.gd  sim.gd  game_state.gd  tuning.gd  save_data.gd  data/tuning.json
services/        autoload scripts (save, audio, analytics, ads, iap, haptics, lifecycle, safe area)
presentation/    scenes + scripts: boot, menu, game, results, views, ui
tools/ci/        check_all.gd, run_tests.gd (headless gates)
tools/playtest/  runner.gd (scripted playthrough and bots)
tests/unit/      test_*.gd
tests/playthroughs/*.json
assets/          art, audio, fonts (import settings live next to files as .import)
addons/          third-party plugins (vendor deliberately, pin versions)
```

Rules:
- Folder by layer first, feature second. A feature that spans layers gets matching names (`core/merge_rule.gd`, `presentation/merge_view.gd`).
- Do not commit `.godot/` (cache). Do commit `.import` files and `project.godot`.
- Keep one scene per file, one root script per scene. If a scene script exceeds ~300 lines, split behavior into child nodes or helper RefCounted classes.
- `core/` may preload other `core/` files only. A grep for `Node`, `get_tree`, `Engine.`, `OS.` in `core/` should return nothing.

## 2. Typed style guide

| Rule | Example |
|---|---|
| Indent with tabs | one tab per level |
| `snake_case` for vars, funcs, files; `PascalCase` for classes and nodes; `UPPER_SNAKE` for constants and enum members | `const MAX_HP: int = 5` |
| Type everything | `var speed: float = 120.0`, `func add(a: int, b: int) -> int:` |
| Typed collections | `var tiles: Array[int] = []`, `var by_id: Dictionary = {}` (Dictionary typing is available in newer 4.x; verify before relying) |
| Private by convention | leading underscore: `_cache`, `_on_timer_timeout` |
| Order inside a script | `class_name`, `extends`, doc comment, signals, enums, constants, `@export` vars, public vars, private vars, `@onready` vars, lifecycle methods, public methods, private methods |
| Explicit inference | `var n := 3` is fine when the right side is obviously typed; use explicit types for anything from a Dictionary, `get_node`, or `load` |
| Prefer `preload` for static paths | `const SimScript := preload("res://core/sim.gd")` |
| Names of handlers | `_on_<node>_<signal>` |

Typical header:

```gdscript
extends RefCounted
## Deterministic rules for a 5x5 merge board. No Node access.

signal changed(events: Array)   # RefCounted can declare signals too

const Rng := preload("res://core/rng.gd")
const SIZE: int = 5

var _rng: Rng
var _grid: PackedInt32Array = PackedInt32Array()

func apply(action: Dictionary) -> Array:
	var events: Array = []
	match action.get("type", ""):
		"swipe":
			events.append_array(_swipe(String(action.get("dir", ""))))
		_:
			push_warning("unknown action %s" % [action])
	return events
```

Enable these project warnings as errors in a real game: untyped declaration, unsafe property/method access, unused variable, shadowed variable. Introduce them early; retrofitting is expensive.

## 3. Language reference for agents (valid vs invalid)

| Intent | Valid GDScript 4 | Invalid (common mistake) |
|---|---|---|
| Null | `null` | `None`, `nil` |
| Booleans | `true`, `false` | `True`, `False` |
| Logic | `and`, `or`, `not` (also `&&`, `||`, `!`) | mixing is legal but pick one style |
| Else-if | `elif` | `else if` on one line |
| String format | `"hp %d/%d" % [hp, max_hp]` or `"{a}".format({"a": 1})` | f-strings `f"hp {hp}"` |
| Ternary | `x if cond else y` | `cond ? x : y` |
| Loop with index | `for i in range(n):` or `for i in arr.size():` | `for i, v in enumerate(arr)` |
| Dictionary iterate | `for k in d:` then `d[k]`; `d.keys()`, `d.values()` | `d.items()` |
| Membership | `x in arr`, `d.has(k)` | `d.contains(k)` |
| Lambdas | `func(x): return x * 2` (anonymous Callable) | `lambda x: x*2` |
| List ops | `arr.append(x)`, `arr.size()`, `arr.pop_back()`, `arr.map(func(x): ...)`, `arr.filter(...)` | `len(arr)`, `arr.add`, list comprehension |
| Length | `.size()` (Array, Dictionary, String uses `.length()`) | `len()` is not a built-in |
| Integer division | `a / b` on ints truncates; use `float(a) / b` for float | assuming Python `//` (not valid) |
| Casting | `int(x)`, `float(x)`, `str(x)`, `x as Node` | `int(x, 10)` |
| Static | `static func util() -> int:` and `static var` (4.1+) | `@staticmethod` |
| Constants of enums | `enum State { IDLE, RUN }` then `State.IDLE` | `State("IDLE")` |
| Class declaration | `class_name Foo` at top level; inner `class Bar:` | `class Foo():` |
| Assert | `assert(cond, "message")` (stripped in release) | relying on it for runtime validation |
| Await | `await get_tree().create_timer(0.5).timeout` | `yield(...)` (Godot 3) |
| Call deferred | `call_deferred("method")` or `method.call_deferred()` | `call_deferred(self, ...)` |
| Property setters | `var hp: int = 3: set(v): hp = clampi(v, 0, 5)` | `setget` (Godot 3) |

Variants and untyped Dictionaries: reading `d["x"]` yields `Variant`. Assign through an explicit type: `var n: int = int(d.get("n", 0))`. This avoids warnings and runtime type errors.

`match` supports patterns on literals, arrays and dictionaries and has no fall-through; `_` is the default. `match` on a `StringName` vs `String` compares by value but be consistent.

## 4. Autoloads and the event bus

Autoloads are singletons registered in `project.godot` under `[autoload]`. In the template they have no `class_name` (the autoload name is the global identifier, and a `class_name` with the same name causes a conflict).

Guidelines:
- One autoload per service with a narrow purpose: `SaveService`, `AudioService`, `Analytics`, `Ads`, `Iap`, `Haptics`, `AppLifecycle`, `SafeArea`, `EventBus`.
- Autoloads must not call each other's internals; they emit and listen through `EventBus`.
- Order in `project.godot` is initialization order. Put `EventBus` first.
- Every external SDK sits behind an interface plus a mock: `Ads.set_backend(mock)`. Headless runs use mocks, never real SDKs.
- Autoloads must tolerate being absent in tests (`tools/ci` scripts run as `-s` scripts where autoloads may not be present); resolve them lazily when needed in `core/`-adjacent code, or pass dependencies in.

Event bus example:

```gdscript
extends Node
signal app_paused
signal run_finished(score: int, won: bool)
signal purchase_completed(sku: String)
```

Rule of thumb: if two services need to know about each other, the event goes on the bus; if one node owns another, use a direct signal.

## 5. Signals

```gdscript
signal health_changed(old: int, new: int)

func _ready() -> void:
	button.pressed.connect(_on_button_pressed)
	health_changed.connect(_on_health_changed, CONNECT_ONE_SHOT)

func take_damage(d: int) -> void:
	var old: int = hp
	hp -= d
	health_changed.emit(old, hp)
```

- Typed parameters in the declaration give editor hints and type checks.
- `connect` with a `Callable`; bind extras with `.bind(extra)`; unbind with `.unbind(n)` to drop signal args the handler does not accept.
- Check `is_connected` before reconnecting in code that can run twice (scene reload).
- Signals are synchronous by default; handlers run inside `emit`. Heavy handlers stall the emitter; use `CONNECT_DEFERRED` when needed.
- `await some_signal` pauses the function until emitted. If the emitter is freed first, the coroutine never resumes; guard long awaits with a timeout.
- Disconnect or free listeners when their owner is freed; connections to freed objects are cleaned automatically for Callables of that object.
- Do not use signals for hot-path per-frame data; use direct method calls or shared state.

## 6. Resources and data

- `Resource` subclasses with `@export` fields give typed data editable in the inspector: define `class_name ItemDef extends Resource`.
- Saved as `.tres` (text) or `.res` (binary). Text is diffable; use it for authoring.
- Loaded resources are cached and shared. `duplicate()` (and `duplicate(true)` for deep sub-resources) before mutation.
- For pure-logic data, JSON via `FileAccess` + `JSON.parse_string` is simple and testable headless. In the template, tuning lives in `core/data/tuning.json`.
- JSON numbers parse as floats. Convert deliberately (`int(v)`), and store 64-bit ints as strings (JSON and doubles lose precision above 2^53). The template stores RNG state as strings for this reason.
- Do not store Node references in Resources.
- Large content (levels): one file per level, loaded on demand with `ResourceLoader.load_threaded_request` for non-trivial sizes.

## 7. Node lifecycle

Order for a scene instance added to the tree:
1. `_init()`: object created; exported values not yet set from the scene; no tree access.
2. `_enter_tree()`: entering the tree, parent first.
3. `_ready()`: children are ready before parent; `@onready` vars assigned just before. Called once per tree entry unless `request_ready()`.
4. `_process(delta)` every rendered frame; `_physics_process(delta)` at fixed rate (default 60 Hz).
5. `_exit_tree()` then `queue_free()` frees at end of frame.

Practical rules:
- Never `free()` a node mid-signal or mid-physics callback; use `queue_free()`.
- If a node can be freed while awaiting, check `is_instance_valid(self)` after the await.
- To run something after the first frame: `await get_tree().process_frame`.
- Disable processing when idle: `set_process(false)`, `set_physics_process(false)`.
- Changing scene: `get_tree().change_scene_to_packed(packed)` (deferred to idle frame). Preload scenes as `const GameScene := preload("res://presentation/game.tscn")`.
- Pausing: `get_tree().paused = true`; nodes opt out through `process_mode = Node.PROCESS_MODE_ALWAYS`.
- Time: use `delta` and tweens, never frame counting, so 30, 60 and 120 Hz behave identically.

## 8. Scenes, UIDs and text files

- Godot 4 writes `uid="uid://..."` in `.tscn`, `.tres` and `.import`. They are globally unique identifiers allocated by the editor.
- Never invent one. A duplicate UID silently redirects a reference to the wrong file. Omit the attribute; references by path still work; Godot adds UIDs when you save in the editor.
- If you copy a scene file, delete its `uid` attribute in the copy.
- `ext_resource` entries need an `id` string unique inside that file; use simple strings like `"1_script"` only if you must hand-write.
- Prefer building dynamic UI in code and instancing packed scenes for anything reused.
- `load_steps` in the header is advisory; a wrong value is harmless.
- After editing any text scene by hand, run the static gate; it loads every scene and fails on engine errors.
- Merge conflicts in `.tscn` are easiest when each scene is small and nodes are not reordered gratuitously.

Minimal hand-written scene (no UIDs):

```
[gd_scene load_steps=2 format=3]

[ext_resource type="Script" path="res://presentation/game.gd" id="1_game"]

[node name="Game" type="Control"]
layout_mode = 3
anchors_preset = 15
anchor_right = 1.0
anchor_bottom = 1.0
script = ExtResource("1_game")
```

## 9. Input and timing

- Use the Input Map for actions (`Input.is_action_just_pressed("confirm")`). For touch, handle events in `_unhandled_input` or `_gui_input` on a Control.
- Swipe detection: record `ScreenTouch` press position and time, on release compute delta; accept if distance above a threshold (about 8 percent of the shorter screen side is a reasonable start) and time below ~600 ms; choose the dominant axis. Make the threshold configurable.
- Multi-touch: `InputEventScreenTouch.index` identifies fingers.
- `Input.vibrate_handheld(ms)` exists for Android and iOS but is coarse; wrap in `Haptics`.
- Tweens: `var t := create_tween()`, chain with `tween_property`, `set_trans`, `set_ease`; kill a tween before starting a conflicting one on the same property.
- Timers: `get_tree().create_timer(sec)` for one-shots; `Timer` node for repeating.
- Randomness in gameplay: seeded `RandomNumberGenerator` or the project's own PCG; never global `randi()` in rules.

## 10. Save data

- Versioned dictionary with a `version` int; migrations are functions `v1_to_v2(d)` applied in order.
- Atomic write: write `save.tmp`, then rename over `save.json`; keep `save.bak`.
- Location: `user://` (per-app, writable on mobile).
- Flush on pause, focus-out and quit; also periodically after meaningful changes with a dirty flag.
- Never trust loaded data: validate types and clamp ranges; fall back to the backup then defaults.
- Cloud save later: keep the schema free of device-specific data.

## 11. Static analysis and formatting

- The parser is the first linter. `godot --headless --path <project> --check-only -s <script>` parses one script and quits (`--help` on 4.7.2: "Only parse for errors and quit (use with --script)"). It prints `SCRIPT ERROR: Parse Error: ...` lines, but it does not set a failing exit code: a script with three parse errors still exited 0 on 4.7.2, so grep the output for `SCRIPT ERROR` rather than trusting `$?`. The template's `check_all.gd` is the gate to use in CI: it loads every `.gd`, `.tscn` and `.json`, reports engine errors and exits 1 when anything fails.
- GDScript Toolkit (`gdformat`, `gdlint`) is a community formatter and linter; version it in CI if the team uses it.
- Treat warnings as work items; do not ship with a pile of suppressed warnings.
- Use `@warning_ignore("...")` locally with a comment explaining why.

## 12. AI-agent pitfalls checklist

Run through this before declaring a Godot change done.

| # | Pitfall | Check |
|---|---|---|
| 1 | Invented `uid://` | `grep -R "uid://" <changed files>`; any you did not copy from Godot output must go |
| 2 | Spaces for indent | `grep -nP "^ +" *.gd` in changed files |
| 3 | Python idioms (`None`, `True`, `len`, f-strings, `elif` mistakes) | read the diff against section 3 |
| 4 | Godot 3 API (`yield`, `setget`, `export var`, `onready var`, `connect("sig", obj, "m")`, `KinematicBody2D`, `OS.get_ticks_msec` still exists but check) | use `@export`, `@onready`, `await`, `.connect(callable)`, `CharacterBody2D` |
| 5 | Untyped Variant arithmetic | add explicit types |
| 6 | Wrong node type names | check class reference: `Sprite2D`, `AnimatedSprite2D`, `TextureRect`, `CanvasLayer` |
| 7 | `get_node` on a path that does not exist at `_init` | move to `_ready` |
| 8 | Using `$Path` in a script attached to a scene whose tree differs | prefer `@export var x: Node` or unique names `%Name` |
| 9 | Forgetting `queue_free` for spawned nodes | check pooled or freed on exit |
| 10 | Editing `.godot/` or `.import` by hand | never |
| 11 | Calling gameplay logic from `_process` without `delta` | multiply by `delta` or use tweens |
| 12 | Forgetting to run the import after adding assets headlessly | `godot --headless --path <project> --import` |
| 13 | Assuming `assert` runs in release | use explicit errors |
| 14 | Hard-coded balance numbers | move to tuning file |
| 15 | Treating the Godot editor as available on CI | use headless scripts only |

Unique names (`%NodeName`) are handy: set "Access as Unique Name" in the editor, then `@onready var label: Label = %ScoreLabel`. In hand-written `.tscn` this is `unique_name_in_owner = true`.

When uncertain about an API signature, check the class reference for your engine version (the Godot docs "stable" and version-pinned pages) instead of recalling from memory. Wrong signatures fail at parse or run time, and the static gate catches most of them.
