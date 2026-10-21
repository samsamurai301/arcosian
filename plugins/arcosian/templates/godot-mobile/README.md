# godot-mobile: reference template (Godot 4.x, tested on 4.7.2)

A portrait mobile project that demonstrates the **sim-core + presentation** architecture. The sample game is a
deterministic 5x5 "merge numbers" puzzle (2048-style swipes, seeded spawns, win at a tuning target, lose when no
move remains). Copy it, rename it, and replace the mechanic; keep the split.

## Architecture

```
presentation/  Nodes, scenes, tweens, input   ->  reads state, sends actions
services/      autoloads (save, audio, ads...) ->  talk to each other via EventBus
core/          RefCounted only, no Node/scene/autoload access, deterministic
```

- `core/sim.gd`: `apply(action: Dictionary) -> Array` of event Dictionaries. Same seed + same actions = same events.
  State round-trips through `to_dict()` / `load_dict()`.
- Presentation never mutates state; it sends actions and animates the returned events (`BoardView.play`).
- Everything the headless tools do (tests, playthroughs, bots) uses `core/` only, so they run in milliseconds without a renderer.
- Randomness lives in `core/rng.gd` (PCG32; state saved as strings because JSON loses int64 precision). Never call
  `randi()` in `core/`. Presentation effects (screen shake) may use global random.

## Folder map

| Path | Purpose |
|---|---|
| `project.godot` | Portrait 1080x1920, `canvas_items` + `expand`, Mobile renderer, ETC2/ASTC import, autoloads |
| `export_presets.cfg` | Android (gradle, AAB, arm64-v8a, min SDK 24, target SDK 36) and iOS (placeholder bundle id); no secrets |
| `core/` | `rng.gd`, `game_state.gd`, `sim.gd`, `tuning.gd`, `save_data.gd` (schema + migrations), `data/tuning.json` |
| `services/` | `event_bus`, `save_service`, `audio_service`, `haptics`, `analytics`, `ads`, `iap`, `app_lifecycle`, `safe_area` |
| `presentation/` | `boot`, `main_menu`, `game`, `results` scenes; `board_view`, `swipe_detector`, `screen_shake`, `ui` |
| `tools/ci/` | `check_all.gd` (static gate), `run_tests.gd` (unit gate), shared `cli.gd`, `error_capture.gd` |
| `tools/playtest/` | `runner.gd`: scripted playthrough and bot modes |
| `tools/capture/` | `screenshot_mode.gd`: PNGs for the visual gate and store |
| `tools/perf/` | `perf_probe.gd`: bot-driven frame-time and memory probe, writes a perf-report JSON |
| `tests/unit/` | `test_case.gd` base + `test_*.gd` |
| `tests/playthroughs/` | `smoke.json` deterministic playthrough |
| `addons/` | Nothing vendored; see `addons/README.md` |

## Copy and rename

1. Copy this folder to your game repo root (or `cp -R templates/godot-mobile <game>/`).
2. `project.godot`: change `config/name`, `config/description`; `export_presets.cfg`: change `package/unique_name`,
   `package/name`, `application/bundle_identifier` (reverse-DNS, one per store) and `version/*`.
3. Replace `icon.svg`. Delete `.godot/` if you copied from a working checkout. Rename `gitattributes.example` to
   `.gitattributes` (LF line endings, binary assets); it ships under that name because a plugin folder may not contain one.
4. Import once so global caches exist: `godot --headless --path <project> --import`.
5. Run the gates below; all must pass before you change anything.
6. Replace the sample mechanic (see "Add a mechanic"), keep `tests/` and `tools/` in place.

Do not hand-write `uid://` values. Scenes here omit them; Godot adds them when you save in the editor.

### `.gd.uid` files: commit them

Godot 4.4 and later writes a `<script>.gd.uid` sidecar next to every script (and `.gdshader.uid` next to every
shader) the first time the editor scans or saves the project; `godot --headless --path <project> --import` creates
them too, and they are absent from this template until then. They hold the script's `uid://` so scene and resource
references survive a move or rename. **Commit them with the scripts** (`git add -A` after the first import or editor
save) and never list them in `.gitignore`: if each checkout regenerates its own, scenes that reference the old
uid log "invalid UID" warnings and renames stop being tracked. Delete a `.uid` file only together with its script.

## Commands

`godot` is your Godot 4.x binary. `<abs>` = absolute path. All non-rendering commands run with `--headless`.

| Gate | Command | Output | Exit |
|---|---|---|---|
| static | `godot --headless --path <project> -s res://tools/ci/check_all.gd -- --out=<abs>/static.log` | log, one line per file | 0 ok, 1 failures |
| unit | `godot --headless --path <project> -s res://tools/ci/run_tests.gd -- --out=<abs>/unit.xml` | JUnit XML | 0 ok, 1 failures or no tests |
| playthrough | `godot --headless --path <project> -s res://tools/playtest/runner.gd -- --mode=script --script=res://tests/playthroughs/smoke.json --out=<abs>/playthrough.json [--seed=1]` | playtest-report JSON | 0 pass, 1 fail, 2 usage |
| bots | `godot --headless --path <project> -s res://tools/playtest/runner.gd -- --mode=bot --bot=greedy\|random --runs=200 --seed=1 --out=<abs>/bots.json` | playtest-report JSON | 0 pass, 1 softlocks, 2 usage |
| visual | `godot --path <project> -s res://tools/capture/screenshot_mode.gd -- --out=<abs dir> --screens=menu,game,results` | `menu.png` `game.png` `results.png` | 0 ok, 2 cannot render |
| perf | `godot --path <project> -s res://tools/perf/perf_probe.gd -- --out=<abs>/perf.json [--seconds=20] [--budget-frame-ms=16.7] [--budget-memory-mb=512]` | perf-report JSON | 0 pass, 1 budget violated, 2 usage or cannot run |
| perf (CPU-only) | `godot --headless --path <project> -s res://tools/perf/perf_probe.gd -- --out=<abs>/perf-headless.json [--seconds=20]` | perf-report JSON, flagged `headless` | same |
| Android | `godot --headless --path <project> --export-release "Android" <out>.aab` | AAB | export result |
| iOS | `godot --headless --path <project> --export-release "iOS" <out-dir>/game.xcodeproj` | Xcode project | export result |

Notes:
- `screenshot_mode` needs a renderer. Under `--headless` it exits 2 with a message. On Linux CI run it as
  `xvfb-run -a godot --path <project> -s res://tools/capture/screenshot_mode.gd -- --out=<dir>`. Add `--resolution 540x960` for a phone-sized shot.
- Bot and script time metrics are estimates (0.8 s per accepted move), not measurements.
- The static gate (and the plugin's PostToolUse parse check) read Godot's class cache, `.godot/global_script_class_cache.cfg`.
  After you add or rename a `class_name` script, or add assets that scripts `preload`, run `--import` again, otherwise a
  script that uses the new type fails with "Could not find type" although the type exists.
- `perf_probe.gd` plays the real game scene with a greedy bot (the same policy as `runner.gd`), restarts after each finished
  game and samples every frame; it keeps the bot's saves out of your real save file (`user://perf_probe_save.json`, removed
  at the end). Options (all `--key=value`): `out` (required), `seconds` (measured window, default 20), `warmup` (default 1),
  `seed`, `budget-frame-ms` (16.7), `budget-memory-mb` (512), `budget-fps` (60), `tier` (low|mid|high), `device-name`,
  `build`, `scenario`, `feature` (F012), `frames` (embed the raw `frames_ms` series), `pace-fps` (headless only, default 60).
  Budgets default to the plugin's contract defaults; pass the contract's `technical.perf_budgets` values, or re-judge a report
  with `python3 <plugin>/scripts/perf_budget.py --report <abs>/perf.json --contract .gamestudio/contract.json`.
  The windowed run needs a display (on Linux CI wrap it in `xvfb-run -a`, like the screenshot gate) and a real renderer; it
  keeps the project's own vsync and `max_fps`, and exits 2 when the window is never drawn.
- What the report means: `frame_ms` is CPU work per frame on the main thread without vsync, present or idle waits (windowed:
  scene processing + render CPU + frame setup, or the driver's GPU time when longer, which Metal does not report; headless:
  scene processing only). `fps.avg` and `fps.p1_low` derive from `frame_ms`; `fps.engine_avg` is the delivered rate.
  `memory_mb` is process RSS where the OS allows it (`basis: "rss"`), else the engine's static + video memory.
- Headless runs have no renderer: the probe flags them (`device.name: "desktop-headless"`, `headless: true`, `draw_calls` and
  `gpu_ms` null, a HEADLESS line in `notes`) and they are not valid evidence for a device. The probe paces headless frames at
  `pace-fps` by spinning; add the engine flag `--fixed-fps 60` and `--pace-fps=0` for an instant, deterministic run
  (20 s of game time in under a second).
- Both modes are desktop proxies measured on an editor/debug binary. For the perf gate on a release build, profile on the
  reference device (Godot monitors, Android Studio or Xcode Instruments) and write the report there; use the probe for
  regression checks, to catch per-frame allocation spikes, and to produce the first report.
- Reference results on 4.7.2 (seed 1, 200 runs, win tile 1024): greedy bot wins about 85 percent, random bot about 25 percent, 0 softlocks.
- Android export needs the Android build template and a keystore. Supply it by environment variables
  (`GODOT_ANDROID_KEYSTORE_RELEASE_PATH`, `_USER`, `_PASSWORD`); never commit keystores or passwords. Play requires a current target SDK (preset says 36; verify at release time).
- Verified on 2026-10-21 with Godot 4.7.2: `godot --headless --path . --install-android-build-template --export-release "Android" build/android/game.aab`
  produced a signed AAB (about 26 MB) in about 90 s on the first Gradle run. Toolchain it needs (from the 4.7.2 build template's `config.gradle`):
  JDK 17, Android SDK platform 36, build-tools 36.1.0, NDK 29.0.14206865, Gradle 8.11.1 (downloaded by the wrapper). Set the SDK and JDK
  paths in Editor Settings (`export/android/android_sdk_path`, `export/android/java_sdk_path`). Checked in the result: package and version,
  min SDK 24 / target SDK 36, arm64-v8a only, no extra permissions, and 16 KB pages (ELF LOAD segments aligned 0x4000; `zipalign -c -P 16`
  passes on a bundletool universal APK).
- iOS: set `application/app_store_team_id` (CI injects `APPLE_TEAM_ID`). The preset exports the Xcode project only
  (`application/export_project_only=true`); fastlane gym builds and signs it. Verified on 2026-10-20: export plus an unsigned
  `xcodebuild -scheme game -destination 'generic/platform=iOS'` succeeds (minimum iOS 15.0, privacy manifest included).

## Mapping to the five gates

| Gate | Evidence this template produces |
|---|---|
| `static` | `check_all.gd` log (also fails on any engine error raised while loading a script or scene) |
| `unit` | `run_tests.gd` JUnit XML |
| `playthrough` | runner `--mode=script` report (and `--mode=bot` for difficulty/softlock estimates) |
| `visual` | `screenshot_mode.gd` PNGs, reviewed by the critic |
| `perf` | `perf_probe.gd` report: a desktop proxy (windowed with a renderer; headless is CPU-only and flagged). Release evidence still needs a device capture |

Playthrough format: `{"schema_version":"1.0","seed":1,"steps":[{"action":{...},"expect":{"<path>": value | {"op":">=","value":n}}}]}`.
Expect paths: `score`, `moves`, `status`, `won`, `lost`, `max_tile`, `empty_count`, `grid_sum`, `grid.<index>`.
Ops: `==` (default), `!=`, `>=`, `<=`, `>`, `<`.

## Services at a glance

- `SaveService`: versioned JSON (`core/save_data.gd`), atomic write (temp file then rename), `.bak` fallback, `flush()` writes only if dirty.
- `AppLifecycle`: on pause, focus-out or close request emits `EventBus.app_paused` and flushes the save; `game.gd` stashes the run so "Continue" works after the OS kills the app.
- `Analytics.log_event(name, params)`: fan-out to backends; the debug backend keeps a ring buffer. Names must match your event taxonomy.
- `Ads` / `Iap`: interfaces plus mocks. Swap with `set_backend(...)` (see `addons/README.md`).
- `SafeArea.insets()`: notch and gesture-bar insets in canvas pixels (zero on desktop; set `debug_insets` to preview).
- `Haptics`, `AudioService` (Music and SFX buses, crossfade, 8-voice SFX pool): both tolerate missing assets.

## Add a mechanic

1. Write the rule in `core/` as pure functions on `GameState` (add fields to `to_dict` / `from_dict`).
2. Add an action type in `Sim.apply` and emit events describing *what happened* (not how to draw it).
3. Put numbers in `core/data/tuning.json` and read them through `tuning.gd`; never hard-code balance values.
4. Write unit tests first in `tests/unit/test_<mechanic>.gd` (extend `test_case.gd`; methods named `test_*`).
5. Extend `GameState.lookup` with any new state paths, then add steps to a playthrough JSON.
6. In `presentation/`, react to the new events (tween, particle, sound, haptic). No rules there.
7. If the save format changes, bump `SaveData.CURRENT`, add a migration step and a test in `test_save_migration.gd`.
8. Run all four headless gates, the screenshot gate and the perf probe; record evidence under `.gamestudio/evidence/<FEATURE-ID>/`.
   The probe drives `Game.sim`, `Game.refresh()` and `Game.try_move()`: if your gameplay scene changes those, update
   `_decide()` and `greedy_move()` in `tools/perf/perf_probe.gd` to play your mechanic.

## Conventions

- Static typing everywhere; no `class_name` in the template so tools run even before the first import.
- Cross-file references use `preload` constants.
- Autoload scripts have no `class_name` (the autoload name is the global).
- Touch targets are at least 130 canvas px high at 1080 wide (about 48 dp on a typical phone).
