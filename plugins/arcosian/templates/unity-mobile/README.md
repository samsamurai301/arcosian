# unity-mobile: reference template (Unity 6 LTS, C# 9)

A portrait mobile project with the same **sim-core + presentation** split and the same sample game as
`templates/godot-mobile`: a deterministic 5x5 "merge numbers" puzzle (swipe to slide, seeded spawns, win at a
tuning target, lose when no move remains). Copy it, rename it, replace the mechanic, keep the split.

> **Status: written without Unity installed.** The C# was reviewed by hand and the logic mirrors the verified
> Godot sim, but it has not been compiled or run. Open it once in Unity 6, run the three checks under "First open",
> and fix anything the compiler reports before building features on top. Record the result in `.gamestudio/progress.md`.

## Architecture

```
Assets/_Game/Presentation/   MonoBehaviours, uGUI, input, services  ->  reads state, sends actions
Assets/_Game/Core/           plain C#, no UnityEngine (noEngineReferences), deterministic
Assets/_Game/Editor/         batchmode entry points (Editor-only assembly)
```

- `Sim.Apply(GameAction)` returns `List<SimEvent>`. Same seed + same actions = same events (`SimEvent.ToString()` is the
  stable text form tests compare). State round-trips through `ToDict()` / `LoadDict()`.
- Presentation never mutates state: `Bootstrap` turns a swipe into an action, applies it, then hands the events to
  `BoardView.Play`, `ScreenShake`, `AudioService`, `Haptics` and `Analytics`.
- Everything the headless tools do (tests, playthroughs, bots) uses `Game.Core` only.
- Randomness lives in `Rng` (PCG32, same stream as the Godot template for the same seed; state saved as strings because JSON
  loses int64 precision). Never use `UnityEngine.Random` or `System.Random` in Core; cosmetic effects may.
- `MiniJson` (in `Core/Tuning.cs`) is a tiny hand-written parser/writer so Core needs no engine or third-party serializer.
- C# 9, nullable annotations not enabled (Unity default). Core has no `UnityEngine` reference; the asmdef enforces it.

## Folder map

| Path | Purpose |
|---|---|
| `Packages/manifest.json` | URP, Input System, Test Framework, Performance Testing, Addressables, Localization, uGUI (see note) |
| `ProjectSettings/ProjectVersion.txt` | Pinned to Unity 6.3 LTS 6000.3.26f1 (latest 6.3 LTS on 2026-10-08); Unity Hub rewrites it if you open with another 6000.x editor |
| `Assets/_Game/Core/` | `Rng`, `GameState`, `Sim`, `Tuning` (+ `MiniJson`), `Playthrough`, `SaveData` (schema and migrations), `Game.Core.asmdef` |
| `Assets/_Game/Presentation/` | `Bootstrap`, `BoardView`, `SwipeInput`, `ScreenShake`, `Game.Presentation.asmdef` |
| `Assets/_Game/Presentation/Services/` | `EventBus`, `SaveService`, `AudioService`, `Haptics`, `Analytics` (`IAnalytics`, `DebugAnalytics`), `Ads` (`IAds`, `MockAds`), `Iap` (`IIap`, `MockIap`), `SafeArea` |
| `Assets/_Game/Editor/` | `SceneBuilder`, `BuildScript`, `PlaytestRunner`, `ScreenshotCapture` (namespace `Game.EditorTools`) |
| `Assets/_Game/Tests/EditMode/` | `SimTests.cs` (NUnit) |
| `Assets/_Game/Tests/Playthroughs/` | `smoke.json`, deterministic playthrough |
| `tools/dotnet-harness/` | Builds a plain .NET project around `Game.Core` + the EditMode tests, so they run without a Unity licence (see below) |
| `Assets/_Game/Data/tuning.json` | Balance numbers (`size`, `win_tile`, `initial_tiles`, `spawn_four_chance`) |

Package versions in `manifest.json` were checked against Unity's package registry (packages.unity.com) for Unity 6.3 LTS in
Oct 2026: Addressables 4.1.1, Input System 1.20.1, Localization 1.5.13, Performance Testing 3.6.0, Test Framework 1.4.6,
Visual Studio Editor 2.0.28 (writes the `.slnx`/`.csproj` files that IDEs and the `arcosian-unity` C# language server read).
URP (17.3.x) and uGUI (2.0.0) are core packages bundled with the editor, so Unity pins them to the editor's own version on open.
Commit the generated `Packages/packages-lock.json`. Addressables and Localization are staged for later and not used by the sample.

## First open

1. Install Unity 6 LTS with Android Build Support (SDK, NDK, OpenJDK) and iOS Build Support as needed.
2. Add the folder as a project in Unity Hub and open it with your installed 6000.x editor (this rewrites `ProjectVersion.txt`).
   Unity generates every `.meta` file, `ProjectSettings/*.asset` and `Library/` itself. Commit the `.meta` files
   (they hold asset GUIDs); never hand-write them. Each folder gets one when Unity first imports it.
3. If prompted to enable the new Input System backend, accept the restart. `SwipeInput` also compiles against the legacy
   Input Manager when that is the only active handler.
4. Run `Game > Build Scene and Settings` (or the batch command below). It creates `Assets/_Game/Scenes/Main.unity`, adds it
   to Build Settings, sets portrait orientation, IL2CPP + ARM64, min SDK 24, and a placeholder bundle id (only if still Unity's default).
5. Run the unit tests (Window > General > Test Runner > EditMode) and the playthrough below. Play `Main.unity`: arrow keys or mouse drag.
6. Change the bundle id, product name and company in Project Settings before the first store build.

## Core tests without Unity (free, CI-friendly)

`Game.Core` has no engine references, so the core and the EditMode tests also build and run on the .NET SDK
(checked Oct 2026 with .NET 10.0.402: Core compiles as C# 9 / .NET Standard 2.1 with 0 warnings, and all 20 EditMode tests pass).

```bash
python3 tools/dotnet-harness/build_harness.py . /tmp/unity-harness
cd /tmp/unity-harness/Tests && UNITY_ASSETS_DIR="$OLDPWD/Assets" dotnet test   # packages are pinned in the generated Tests.csproj
```

The harness compiles the real `Assets/_Game/Core/**/*.cs` and `Assets/_Game/Tests/EditMode/*.cs`; it stubs only
`Application.dataPath`, `Vector2` and `Mathf.Abs`, and copies `SwipeInput.Classify` verbatim from the source. Presentation and
Editor code still need the Unity Editor: run the EditMode tests in Unity and `SceneBuilder.BuildAll` on first open.

## Code intelligence in Claude Code

With the `arcosian-unity` adapter, Claude gets C# compiler errors after its edits and symbol navigation from csharp-ls.
Before Unity has written project files, only `Game.Core` (the engine-free asmdef) is checked; after you set an external
script editor in Preferences > External Tools and click Regenerate project files, every script is. Details and setup:
the adapter's README.

## Commands

`Unity` is your 6000.x editor binary (macOS: `/Applications/Unity/Hub/Editor/<ver>/Unity.app/Contents/MacOS/Unity`).
`<p>` = project path, `<abs>` = absolute path. Add `-quit` to every `-executeMethod` call.

| Gate | Command | Output | Exit |
|---|---|---|---|
| unit | `Unity -batchmode -nographics -projectPath <p> -runTests -testPlatform EditMode -testResults <abs>/unit.xml -logFile <abs>/unity.log` | NUnit XML | 0 ok, 2 failures (Unity's own codes) |
| playthrough | `Unity -batchmode -nographics -projectPath <p> -executeMethod Game.EditorTools.PlaytestRunner.Run -gsMode script -gsScript Assets/_Game/Tests/Playthroughs/smoke.json -gsOut <abs>/playthrough.json -quit` | playtest-report JSON | 0 pass, 1 fail, 2 usage |
| bots | same method with `-gsMode bot -gsBot greedy\|random -gsRuns 200 -gsSeed 1 -gsOut <abs>/bots.json` | playtest-report JSON | 0 pass, 1 softlocks, 2 usage |
| scene | `Unity -batchmode -nographics -projectPath <p> -executeMethod Game.EditorTools.SceneBuilder.BuildAll -quit` | `Main.unity`, settings | 0 ok, 1 error |
| Android | `Unity -batchmode -nographics -projectPath <p> -executeMethod Game.EditorTools.BuildScript.BuildAndroid -gsOut Builds/Android/game.aab -quit` | AAB | 0 built, 1 failed, 2 usage |
| iOS | `Unity -batchmode -nographics -projectPath <p> -executeMethod Game.EditorTools.BuildScript.BuildIOS -gsOut Builds/iOS -quit` | Xcode project (archive and sign in Xcode) | 0 built, 1 failed |
| visual | `Unity -batchmode -projectPath <p> -executeMethod Game.EditorTools.ScreenshotCapture.Run -gsOut <abs dir>` | `start.png`, `played.png` | 0 ok, 1 failed, 2 usage |

Notes:
- `-gsOut` relative paths resolve against the project root. The editor exits with the code of the method (`EditorApplication.Exit`).
- The visual gate needs a graphics device: no `-nographics`, and on Linux CI run under `xvfb-run -a`. It enters play mode,
  so the editor reloads scripts once. It is the least tested path here; if Game view capture is empty in batchmode, capture
  from a device or the Simulator instead and say so in the gate notes.
- Bot and script time metrics are estimates (0.8 s per accepted move), not measurements.
- Unity writes `-logFile` itself; read it when a batch run fails. A compile error makes every `-executeMethod` fail before it runs.

## Mapping to the five gates

| Gate | Evidence this template produces |
|---|---|
| `static` | A clean batchmode compile: the unit-test or `SceneBuilder.BuildAll` run exits 0 and `unity.log` has no `error CS`. Add Roslyn analyzers or `dotnet format --verify-no-changes` on the generated solution if you want more |
| `unit` | `unit.xml` from the EditMode run |
| `playthrough` | `PlaytestRunner` report (script mode; bot mode for difficulty and softlock estimates) |
| `visual` | `ScreenshotCapture` PNGs, reviewed by the critic |
| `perf` | Not produced here: profile on a device (Profiler, Unity Performance Testing package, Xcode Instruments, Android GPU Inspector) and write a perf-report JSON |

Playthrough format: `{"schema_version":"1.0","seed":1,"steps":[{"action":{...},"expect":{"<path>": value | {"op":">=","value":n}}}]}`.
Expect paths: `score`, `moves`, `status`, `won`, `lost`, `max_tile`, `empty_count`, `grid_sum`, `grid.<index>`.
Ops: `==` (default), `!=`, `>=`, `<=`, `>`, `<`. Actions: `{"type":"move","dir":"left|right|up|down"}`, `{"type":"new_game","seed":n}`.

## CI notes

- Cache `Library/` keyed on `Packages/packages-lock.json` and `ProjectSettings/`; it is the slow part of a cold run.
- Unity needs a license in CI (personal activation or a floating/serial license through the vendor's CI tooling); never commit it.
- Android signing: `GS_ANDROID_KEYSTORE_PATH`, `GS_ANDROID_KEYSTORE_PASS`, `GS_ANDROID_KEY_ALIAS`, `GS_ANDROID_KEY_PASS` (defaults to the
  keystore pass), populated from your secret store. Without a keystore the AAB is debug-signed and Play will reject it.
  `GS_BUILD_NUMBER` sets the Android version code and iOS build number (CI run number works). Play needs a current target SDK:
  the script uses "highest installed" (`AndroidApiLevelAuto`); verify against Play policy at release time.
- iOS: `BuildIOS` produces an Xcode project; archive, sign and upload with Xcode or `xcodebuild` on a macOS runner.
- `.gitattributes` keeps text and Unity YAML at LF line endings. Git LFS rules for textures, audio, models and fonts are in `gitattributes-lfs.example`: append them to `.gitattributes` after copying the template and run `git lfs install` before the first commit that adds such files. They ship separately because a plugin folder may not contain LFS filters.
- Run in this order and stop on the first failure: unit, playthrough, bots, scene, build, visual.

## Services at a glance

- `SaveService`: versioned JSON (`Core/SaveData.cs`), write temp then copy `.bak` then move into place, `.bak` fallback on load,
  `Flush()` writes only when dirty. `Bootstrap` flushes on pause, focus loss, quit and run end, and stashes the run so it resumes.
- `EventBus`: static events (`AppPaused`, `AppResumed`, `SimEvents`, `RunEnded`), cleared on every play-mode start.
- `Analytics.Log(name, params)`: fan-out to backends; `DebugAnalytics` keeps a 64-entry ring buffer. Names must be snake_case and match your taxonomy.
- `IAds` / `IIap`: interfaces plus mocks. Set `Bootstrap.Current.Ads` / `.Iap` to your SDK adapters.
- `SafeArea`: fits a RectTransform to `Screen.safeArea`; `SafeArea.DebugRect` previews a notch in the editor.
- `AudioService`: 8-voice SFX pool, music crossfade; clips load from `Resources/Audio/<key>` (`merge`, `move`, `win`, `lose`) and missing clips are skipped.
- `Haptics`: Unity only offers `Handheld.Vibrate()`, used for win and lose; assign `Haptics.CustomBackend` for graded haptics.
- UI uses legacy uGUI `Text` with `LegacyRuntime.ttf` so no TextMeshPro import is needed; swap to TMP when you add real UI.

## Add a mechanic

1. Write the rule in `Core/` as pure functions on `GameState` (extend `ToDict` / `FromDict` and `Lookup`).
2. Add an action type in `Sim.Apply` and emit events describing what happened, not how to draw it.
3. Put numbers in `Data/tuning.json`, read them through `Tuning`; never hard-code balance values.
4. Write the test first in `Tests/EditMode/`, then add steps to a playthrough JSON.
5. React to the events in `Presentation/` (animation, sound, haptics). No rules there.
6. If the save format changes, bump `SaveData.Current`, add a migration step and a test.
7. Run every gate; record evidence under `.gamestudio/evidence/<FEATURE-ID>/`.

## Conventions

- Namespaces: `Game.Core`, `Game.Presentation(.Services)`, `Game.EditorTools`, `Game.Tests`.
- Touch targets at least 48 dp (about 130 px at the 1080 reference width); the Canvas scales from 1080x1920.
- The scene holds only a camera and `Bootstrap`; the UI is built in code, so there are no prefab or scene references to break on merge.
