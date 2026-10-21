---
name: engine-unity
description: Senior Unity 6 mobile practice - C# project layout with asmdefs and a pure core assembly, URP and Player settings for phones, Addressables, Input System, editor automation (Unity CLI, batchmode, SceneBuilder/BuildScript), tests, CI and SDKs. Use when asked to build, fix, test, automate or ship a Unity mobile game, write C# for Unity, configure URP, or set up IAP, ads or CI.
---

# Unity 6 for Mobile

## What this skill gives you
- A project structure (Core / Presentation / Editor assemblies) where rules are plain C# with no `UnityEngine` reference, so they test in milliseconds.
- Serialization and YAML pitfalls, and the rule that an agent never hand-edits scene, prefab or asset YAML.
- URP, Player and quality settings for phones, Addressables, Input System and UI toolkit choices.
- Editor automation recipes: batchmode `-executeMethod`, SceneBuilder and BuildScript patterns, the 2026 Unity CLI, community MCP servers, CI licence activation.
- Testing layers (EditMode, PlayMode, Performance Testing, Graphics tests, device automation) and service SDK options (IAP, ads, Firebase, RevenueCat, notifications).

## Core models

**1. Pure core, thin presentation.**
`Game.Core.asmdef` has `noEngineReferences: true`: rules, state, RNG, save schema, tuning loading from strings. `Game.Presentation.asmdef` references Core and UnityEngine: MonoBehaviours, views, input, audio. `Game.Editor.asmdef` is editor-only (namespace `Game.EditorTools`): `SceneBuilder`, `BuildScript`, `PlaytestRunner`, `ScreenshotCapture`, importers. Dependencies flow Presentation -> Core; never the reverse. EditMode tests can then cover Core with no scene.

**2. Unity owns the YAML; the agent writes C#.**
Scenes, prefabs and assets are YAML with GUIDs and fileIDs. Hand edits corrupt references silently. Create and modify scenes and prefabs by editor scripts (`SceneBuilder`) executed in batchmode, or through an automation bridge. Never write `.meta` GUIDs by hand; commit `.meta` files.

**3. Serialization rules decide what survives a reload.**
Unity serializes public fields and `[SerializeField]` private fields of serializable types; not properties, static fields, interfaces, or `Dictionary` (use lists of pairs). Polymorphism needs `[SerializeReference]`. Renaming a serialized field loses data unless `[FormerlySerializedAs("old")]`.

**4. Lifecycle order.**
`Awake` (own init) -> `OnEnable` -> `Start` (cross-object init, first frame) -> `Update`/`FixedUpdate`/`LateUpdate` -> `OnDisable` -> `OnDestroy`. Do not depend on Awake order between objects; use Start or explicit init. Unsubscribe events in `OnDisable`.

**5. ScriptableObjects are shared data assets.**
Use for tuning tables, item definitions, config. Runtime mutation of a ScriptableObject persists in the editor but not in builds; copy with `Instantiate` for per-run state.

**6. Measure on device.**
Editor frame times mean little. Profile on a development build with the Profiler and platform tools; budget on p95.

## Decision procedures

### A. Start a project
1. Copy `${CLAUDE_PLUGIN_ROOT}/templates/unity-mobile/` into the game repo. It ships with this plugin: Unity 6 LTS, the `Game.Core` / `Game.Presentation` / `Game.Editor` assemblies under `Assets/_Game/`, a deterministic merge-puzzle sample, `PlaytestRunner`, `SceneBuilder`, `BuildScript` and `ScreenshotCapture` editor entry points, and a `manifest.json` that already lists URP, Input System, Test Framework, Performance Testing, Addressables and Localization. `references/csharp-project-and-urp.md` explains the layout when you extend it.
2. Open it once in Unity 6 (Unity Hub rewrites `ProjectVersion.txt` and generates the `.meta` files; commit them), then run the template's three first-open checks: `Game > Build Scene and Settings` (or the `SceneBuilder.BuildAll` batch command below), the EditMode tests, and the smoke playthrough. The template was written without Unity installed, so fix anything the compiler reports before building features and note the result in `.gamestudio/progress.md`. Core and the EditMode tests also run without a Unity licence through `tools/dotnet-harness/build_harness.py`.
3. Set the platform to Android or iOS early; add Input System, Addressables and Performance Testing usage as the game needs them (all are already in the manifest).
4. Replace the sample mechanic in `Core/` with EditMode tests first (see the template README, "Add a mechanic"), then extend `SceneBuilder` so the scenes stay reproducible.
5. Run `BuildScript` in batchmode before writing features, so CI is proven early.

**Template batchmode commands** (`<p>` = project path, `<abs>` = absolute path; every `-executeMethod` call also needs `-quit`; `-gsOut` relative paths resolve against the project root; the exit code is the method's own):

| Gate | Command | Exit |
|---|---|---|
| unit | `Unity -batchmode -nographics -projectPath <p> -runTests -testPlatform EditMode -testResults <abs>/unit.xml -logFile <abs>/unity.log` | 0 ok, 2 failures |
| playthrough | `Unity -batchmode -nographics -projectPath <p> -executeMethod Game.EditorTools.PlaytestRunner.Run -gsMode script -gsScript Assets/_Game/Tests/Playthroughs/smoke.json -gsOut <abs>/playthrough.json -quit` | 0 pass, 1 fail, 2 usage |
| bots | same method with `-gsMode bot -gsBot greedy\|random -gsRuns 200 -gsSeed 1 -gsOut <abs>/bots.json` | 0 pass, 1 softlocks, 2 usage |
| scene | `Unity -batchmode -nographics -projectPath <p> -executeMethod Game.EditorTools.SceneBuilder.BuildAll -quit` | 0 ok, 1 error |
| Android | `Unity -batchmode -nographics -projectPath <p> -executeMethod Game.EditorTools.BuildScript.BuildAndroid -gsOut Builds/Android/game.aab -quit` | 0 built, 1 failed, 2 usage |
| iOS | `Unity -batchmode -nographics -projectPath <p> -executeMethod Game.EditorTools.BuildScript.BuildIOS -gsOut Builds/iOS -quit` | 0 built, 1 failed |
| visual | `Unity -batchmode -projectPath <p> -executeMethod Game.EditorTools.ScreenshotCapture.Run -gsOut <abs dir>` (no `-nographics`) | 0 ok, 1 failed, 2 usage |

Run them in this order and stop on the first failure: unit, playthrough, bots, scene, build, visual. Full notes, CI and signing variables are in `${CLAUDE_PLUGIN_ROOT}/templates/unity-mobile/README.md`.

### B. Choose an automation channel
| Need | Channel |
|---|---|
| Deterministic, CI-friendly | batchmode `-executeMethod` with static editor methods |
| Interactive agent loop with a running editor | Unity CLI (`unity command`, `unity eval`) or a community MCP server |
| Rich editor control (hierarchy, components, play mode) | MCP server (CoplayDev unity-mcp, others) |
| Avoid dependence on a paid or deprecated feature | batchmode plus CLI; do not depend on the in-editor MCP server |
Details and volatile status in `references/editor-automation-and-services.md`.

### C. Write or change C# (agent checklist)
1. Put rule code in `Game.Core`; if it needs `UnityEngine`, it belongs in Presentation.
2. No `FindObjectOfType`/`GameObject.Find` in `Update`; cache references in `Awake`/`Start`.
3. No allocations per frame: no `new List`, string concat, LINQ, or closures in hot paths; pool objects.
4. Fields: `[SerializeField] private`, not public; add `[FormerlySerializedAs]` on rename.
5. Use `async`/Awaitable or coroutines carefully: check `this != null` after awaits; stop on `OnDisable`.
6. Run EditMode tests and compile in batchmode; read the Editor log for warnings.

### D. URP and quality for a new mobile game
1. Pick a URP asset per quality tier (Low/Medium/High); assign in Quality settings per platform.
2. Disable what you do not use: HDR (unless needed), depth/opaque textures, SSAO, soft shadows, MSAA beyond 2x on low tier.
3. Choose Vulkan and Metal (default) with GLES3 fallback only if you must support old devices.
4. Set render scale and frame rate cap per tier; use Adaptive Performance where available.
5. Verify on a low-end device with the Profiler and Frame Debugger. See `references/csharp-project-and-urp.md`.

### E. Ship a build
1. EditMode tests green (plus PlayMode tests if you added any); `PlaytestRunner.Run` in `-gsMode script` and `-gsMode bot` green (commands in procedure A).
2. Build with `Game.EditorTools.BuildScript.BuildAndroid` or `BuildIOS` in batchmode. The Android AAB is signed from `GS_ANDROID_KEYSTORE_PATH`, `GS_ANDROID_KEYSTORE_PASS`, `GS_ANDROID_KEY_ALIAS` and `GS_ANDROID_KEY_PASS` (CI secrets; without them the AAB is debug-signed and Play rejects it), and `GS_BUILD_NUMBER` sets the version code; iOS produces an Xcode project that you archive via fastlane or Xcode.
3. Verify IL2CPP, ARM64, stripping settings, version code increments.
4. Record artifact and hash as evidence; hand to `release-manager`.

### F. Worked example: add a daily reward without touching YAML
1. Core: `DailyReward` class in `Game.Core` taking `(lastClaimUtc, nowUtc, streak)` and returning a reward and new streak; time is an input, never `DateTime.Now`.
2. EditMode tests: same-day claim rejected, next-day increments streak, gap over 48 hours resets, clock moved backwards ignored.
3. Data: reward table as a ScriptableObject created by an editor script (`CreateAssetMenu` plus a SceneBuilder step), not by hand.
4. Presentation: a view MonoBehaviour listens to a Core event and plays animation; the button calls a controller method.
5. Build: rerun SceneBuilder in batchmode so the scene gains the popup reproducibly; run PlayMode smoke test.

## Mobile specifics
- Scripting backend IL2CPP, ARM64 (Android) and managed stripping at Medium or High with `link.xml` for reflection-dependent code.
- Texture compression ASTC; sprite atlases; avoid per-frame UI rebuilds (split canvases by update frequency).
- Safe area via `Screen.safeArea`; handle notches, rotation and aspect extremes.
- Application lifecycle: `OnApplicationPause(true)` and `OnApplicationFocus(false)`: save and pause timers.
- Memory limits kill apps silently; test on low-RAM devices; unload Addressables handles.
- Heat: cap `Application.targetFrameRate`, lower in menus; use Adaptive Performance indices when supported.
- Packages and SDKs add native libraries and manifests; check 16 KB page-size support and privacy manifests (volatile).

## Anti-patterns
| Anti-pattern | Detect | Fix |
|---|---|---|
| Hand-editing `.unity`/`.prefab` YAML | diffs in YAML you wrote | SceneBuilder or editor script |
| Logic in MonoBehaviours with no Core | no EditMode tests possible | Extract to Core |
| `Update` polling everything | profiler shows many Update calls | events, timers, central tick |
| `Resources/` folder for everything | startup and memory bloat | Addressables |
| Singletons via `static` + `DontDestroyOnLoad` sprawl | hidden dependencies, test pain | explicit bootstrap and service locator with interfaces |
| Public fields everywhere | inspector clutter, accidental writes | `[SerializeField] private` |
| Editor-only code in runtime assembly | build fails | `Editor` asmdef or `#if UNITY_EDITOR` |
| Missing `.meta` in VCS | broken references on other machines | commit `.meta`, force text serialization |
| Trusting editor perf | no device profile | development build on device |
| Depending on the in-editor MCP server | feature gated or deprecated | Unity CLI and batchmode |

## Using the ontology
- Core implements verbs and mechanics (`game-ontology`); state and events are plain C# types serializable to JSON for save and replay.
- Tuning data: ScriptableObjects or JSON mirror the schemas from `economy-design` and `progression-difficulty`.
- Gate evidence: EditMode/PlayMode XML (NUnit), playtest-report JSON, screenshots (Graphics tests or capture), perf-report JSON from Performance Testing, in `.gamestudio/evidence/<FEATURE-ID>/`.
- Scripts: `${CLAUDE_PLUGIN_ROOT}/scripts/perf_budget.py`, `${CLAUDE_PLUGIN_ROOT}/scripts/gs.py`.

## Reference library
| File | What it contains | When to read |
|---|---|---|
| `references/csharp-project-and-urp.md` | Folders, asmdefs, lifecycle, ScriptableObjects, serialization pitfalls, URP and Player settings, Addressables, Input System, UI choice, safe area | Structuring code or configuring rendering |
| `references/editor-automation-and-services.md` | Unity CLI, batchmode, SceneBuilder/BuildScript, CI activation, MCP servers, IAP/ads/Firebase/RevenueCat/notifications, Adaptive Performance | Automating the editor or integrating SDKs |
| `references/testing-and-cheatsheet.md` | EditMode/PlayMode, Performance Testing, Graphics tests, AltTester, GameCI, API recipes | Verifying changes and writing tests |

## Related skills
- `game-architecture`: engine-agnostic sim-core + presentation design.
- `gameplay-programming`: patterns to implement in C#.
- `mobile-performance`: budgets and device tiers.
- `qa-testing`: five gates and evidence.
- `technical-art`: atlases, shaders and import pipelines for URP.
- `store-release`: signing and submission after the build.
- `engine-godot`: sibling skill; `engine-alternatives`: when Unity is not the right engine.
- `unity-bridge` (in the `arcosian-unity` adapter): the Unity-aware C# language server (csharp-ls) and Editor automation.
