---
name: engine-godot
description: Senior Godot 4 practice for mobile games - typed GDScript, project layout, autoloads, signals, Resources, mobile renderer and export (Android gradle, iOS), headless CLI gates, testing, perf and plugin options. Use when asked to build, fix, export, test or optimize a Godot project, write GDScript, set up Android/iOS builds, or choose Godot plugins.
---

# Godot 4 for Mobile

## What this skill gives you
- A house style for statically typed GDScript and a project layout that keeps rules out of nodes (sim-core + presentation), matching `templates/godot-mobile/`.
- A checklist of mistakes AI agents make in Godot (invented `uid://` values, Python idioms, space indentation, wrong signal syntax) and how to prevent them.
- Mobile project settings, export procedures for Android and iOS, and the headless commands that give an agent verifiable evidence.
- Testing and performance recipes (unit tests, deterministic playthroughs, movie capture, renderer choices, cost model).
- A map of volatile plugin and store facts (billing, StoreKit 2, ad mediation, Firebase) with a place to verify them.

## Core models

**1. Three layers, one direction of dependency.**
`core/` (RefCounted, deterministic, no Node access) <- `services/` (autoloads, talk via an event bus) <- `presentation/` (scenes, tweens, input). Presentation sends actions and animates events; it never mutates rules state. Everything headless (tests, bots, playthroughs) touches `core/` only, so it runs in milliseconds with no renderer.

**2. Scenes are text; the agent edits text, Godot owns identity.**
`.tscn`/`.tres` are hand-editable but fragile. Omit `uid=` attributes and let the editor or `--import` regenerate them. Prefer building scenes in code (`_ready` assembling nodes) for simple UI, and edit `.tscn` only for trivial property changes.

**3. Signals up, calls down.**
A parent calls methods on children; children emit signals the parent connects. Cross-cutting events (app paused, purchase done, level won) go through one `EventBus` autoload with typed signals. Never reach up with `get_parent().get_parent()`.

**4. Resources are data, nodes are behavior.**
Tuning tables, item definitions and save schemas are `Resource` subclasses or JSON read once. Resources are shared by reference: call `duplicate()` before mutating a per-instance copy, or you will edit the shared one.

**5. Lifecycle order matters.**
`_init` (no tree) -> `_enter_tree` -> children `_ready` first, then parent `_ready` -> `_process`/`_physics_process`. `@onready` vars resolve right before `_ready`. `await` yields; after any `await` re-check `is_instance_valid(self)` if the node can be freed meanwhile.

**6. Verify by running the engine.**
The agent reads text but cannot see a scene tree work. Every change ends with the static, unit, playthrough gates (see `references/testing-perf-cheatsheet.md`), plus a screenshot for visual changes.

## Decision procedures

### A. Starting a new Godot project
1. Copy `templates/godot-mobile/` (see its README: rename, `--import`, run all gates green first).
2. Set orientation, base size (1080x1920 portrait is the template default), stretch `canvas_items` + `expand`.
3. Pick the renderer with the table below; record it in the design contract's tech section.
4. Write the sim-core rule first with unit tests, then the playthrough JSON, then the views.
5. Add services only when needed; each service gets a mock backend so headless runs never hit the network.

### B. Renderer choice

| Situation | Renderer | Reason |
|---|---|---|
| 2D, casual, widest Android reach, low-end devices | Compatibility | OpenGL ES 3, fewest driver surprises |
| 3D or heavy 2D lighting/shaders on mid and high tier | Mobile | Vulkan/Metal, tile-friendly; it is the Mobile renderer, not Forward+ |
| Desktop-class visuals | Forward+ | Do not ship on phones without a device tier plan |

Test on a real low-end device before committing; behavior differs by GPU driver. Details in `references/mobile-export-and-plugins.md`.

### C. Writing or modifying GDScript (agent checklist)
1. Tabs for indentation, not spaces (the editor and `gdformat` expect tabs).
2. Type every variable, parameter and return: `var hp: int = 3`, `func hit(dmg: int) -> void:`; typed arrays `Array[int]`.
3. No Python idioms: no `self` parameter, no `elif` mistakes (`elif` is valid; `else if` is not), no list comprehensions, no `None` (use `null`), no `True/False` (use `true/false`), no `print(f"...")` (use `%` formatting or `String.format`).
4. Signals: `signal scored(points: int)`, `scored.emit(10)`, `button.pressed.connect(_on_pressed)`. Not `emit_signal("x")` strings and not `connect("x", self, "m")` (Godot 3).
5. Never write a `uid://` value. Never invent `ext_resource` ids you cannot trace; copy a form Godot produced.
6. Run the static gate; fix every parse error before touching anything else.

### D. Exporting a release build
1. Static, unit and playthrough gates green.
2. Android: build template installed, keystore via environment variables, AAB, arm64-v8a, target SDK current (verify), 16 KB page-size compatibility checked (volatile).
3. iOS: export on macOS to an Xcode project, set bundle id and team, sign and archive with Xcode or fastlane.
4. Record the build artifact path and hash as evidence. See `references/mobile-export-and-plugins.md`.

### E. A frame is too slow
1. Measure first: Godot monitors and the profiler on a real device; note CPU vs GPU bound.
2. CPU bound: reduce per-frame `_process` nodes, move work to signals/timers, batch via MultiMesh or a single custom-drawn node.
3. GPU bound: fewer overdraw layers, smaller textures, simpler shaders, lower render scale, avoid per-frame full-screen effects.
4. Re-measure and write a perf-report JSON for the `perf` gate. The template produces a desktop-proxy report with `godot --path <project> -s res://tools/perf/perf_probe.gd -- --out=<abs>/perf.json` (exit 0 pass, 1 budget violated, 2 usage or cannot run; add `--headless` for a CPU-only run whose `draw_calls` and `gpu_ms` are null and which is not device evidence). Release evidence still comes from the reference device, written in the same perf-report shape. Recipes in `references/testing-perf-cheatsheet.md`.

### F. Worked example: add an "undo last move" feature
1. Rule: in `core/`, keep a bounded history (`Array[Dictionary]` of `to_dict()` snapshots, cap 5). `Sim.apply({"type":"undo"})` pops and calls `load_dict`, returns an `undone` event.
2. Test first: apply 3 moves, undo, assert `grid_sum` and `moves` equal the state after move 2. Add a playthrough step with `expect`.
3. Save format: history is not saved (derived from the run); if you do save it, bump the save version and add a migration.
4. View: on the `undone` event, rebuild the board without tweens, play a short sound and a light haptic.
5. Service: an `undo` button costs a rewarded ad or a currency; route through `EventBus`, not directly into the ad service.
6. Gates: unit, playthrough, then a screenshot of the button in its disabled state.

## Mobile specifics
- Touch: handle `InputEventScreenTouch`/`ScreenDrag` or enable emulate-mouse; make targets at least ~130 canvas px at 1080 wide.
- Safe area: query `DisplayServer.get_display_safe_area()` and convert to canvas insets; the template's `SafeArea` service does this.
- Lifecycle: save on `NOTIFICATION_APPLICATION_PAUSED` / focus-out; the OS may kill the app without a close event.
- Import settings: ASTC/ETC2 compression, mipmaps only where needed, audio as Ogg for music and WAV for short SFX.
- Heat and battery: cap FPS (`Engine.max_fps`) for menus, use `OS.low_processor_usage_mode` in static UIs.
- C# on Godot mobile is still marked experimental in the docs (see volatile facts in the export reference); default to GDScript.

## Anti-patterns
| Anti-pattern | Detect | Fix |
|---|---|---|
| Gameplay rules inside `Node` scripts | `randi()` or scene access in rule code | Move to `core/` with seeded RNG |
| God autoload holding all state | one script > 400 lines with many unrelated signals | Split by service, use `EventBus` |
| Untyped code | `var x = ...` everywhere, slow and unchecked | Type and enable warnings as errors for untyped declarations |
| Hand-written UIDs | `uid://` in diffs you authored | Delete the attribute, re-import |
| `get_node("../../X")` chains | paths with `..` | Export a `NodePath`/node reference or use signals |
| Per-frame `get_node` and string concatenation | profiler hot spots | Cache in `@onready`, reuse buffers |
| Mutating shared Resources | state bleeds between instances | `duplicate()` |
| Skipping real-device test | only desktop run | Test on a low-end Android and an older iPhone |
| Secrets in `export_presets.cfg` | keystore path or password | Environment variables only |

## Using the ontology
- Rules in `core/` implement the verbs and mechanics of the design (`game-ontology`); events returned by `Sim.apply` are the observable dynamics.
- Tuning values live in `core/data/tuning.json` and map to resource and progression definitions (`economy-design`, `progression-difficulty`).
- Gate evidence: static log, JUnit XML, playtest-report JSON, screenshots, perf-report JSON (`tools/perf/perf_probe.gd` for the desktop proxy), stored under `.gamestudio/evidence/<FEATURE-ID>/` (see `qa-testing`).
- Scripts: `${CLAUDE_PLUGIN_ROOT}/scripts/perf_budget.py` for budget checks, `${CLAUDE_PLUGIN_ROOT}/scripts/gs.py` for project state.

## Reference library
| File | What it contains | When to read |
|---|---|---|
| `references/gdscript-and-project.md` | Layout, typed style guide, autoloads, signals, Resources, lifecycle, AI-agent pitfalls | Writing or reviewing any GDScript or scene |
| `references/mobile-export-and-plugins.md` | Renderer, stretch, touch, safe area, Android and iOS export, headless CLI, billing/ads/Firebase options | Setting up a build, signing, or choosing plugins |
| `references/testing-perf-cheatsheet.md` | Template gates, GdUnit4, movie capture, MCP bridges, mobile perf, API recipes | Verifying a change or chasing performance |

## Related skills
- `game-architecture`: sim-core + presentation design at the engine-agnostic level.
- `gameplay-programming`: patterns (state machines, command queues) to implement in GDScript.
- `mobile-performance`: device tiers and budgets that this skill's recipes serve.
- `qa-testing`: the five gates and evidence format.
- `store-release`: submission steps after the build exists.
- `engine-alternatives`: when Godot is the wrong choice.
- `engine-unity`: the sibling skill for Unity 6.
- `godot-bridge` (in the `arcosian-godot` adapter): Godot's GDScript language server (errors after edits, go to definition, references) and the runtime MCP bridges.
