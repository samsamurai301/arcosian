# Unity C# Project Structure, URP and Mobile Settings

Summary: how to organize a Unity 6 mobile project with assembly definitions and a pure core assembly, the lifecycle and serialization rules that cause most agent mistakes, why an agent must never hand-edit YAML assets, and the URP, Player, Addressables, Input System, UI and safe-area settings that matter on phones. Targets Unity 6 LTS with C# 9; version-sensitive details are flagged for verification.

## Contents
1. Folder layout
2. Assembly definitions
3. Lifecycle
4. ScriptableObjects
5. Serialization pitfalls
6. Never hand-edit YAML
7. Coding rules for mobile (allocation, caching)
8. URP settings for mobile
9. Player settings
10. Addressables
11. Input System
12. UI choice
13. Safe area and aspect
14. Project hygiene
15. Volatile facts (as of Oct 2026 - verify)

## 1. Folder layout

```
Assets/
  _Game/
    Core/            Game.Core.asmdef (noEngineReferences)
      Rules/ State/ Rng/ Save/ Tuning/
    Presentation/    Game.Presentation.asmdef -> Game.Core
      Scenes/ Views/ Input/ Audio/ UI/ Services/
    Editor/          Game.Editor.asmdef (Editor only, namespace Game.EditorTools)
      SceneBuilder.cs BuildScript.cs PlaytestRunner.cs ScreenshotCapture.cs Importers/
    Tests/
      EditMode/      Game.Tests.EditMode.asmdef -> Game.Core (+ Game.Presentation if you test view helpers)
      Playthroughs/  smoke.json (data for PlaytestRunner)
      PlayMode/      Game.Tests.PlayMode.asmdef -> Game.Presentation
    Data/            ScriptableObjects, JSON tuning
    Art/ Audio/ Prefabs/ Addressable/
  Plugins/           native SDK libraries (Android/ iOS/)
Packages/manifest.json
ProjectSettings/
```

`${CLAUDE_PLUGIN_ROOT}/templates/unity-starter/` implements this layout with a flat `Core/` (`Sim.cs`, `GameState.cs`, `Rng.cs`, `Tuning.cs`, `SaveData.cs`, `Playthrough.cs`), `Presentation/` (`Bootstrap.cs`, `BoardView.cs`, `SwipeInput.cs`, `ScreenShake.cs`, `Services/`), `Editor/`, `Tests/EditMode`, `Tests/Playthroughs` and `Data/tuning.json`. The `Rules/ State/ Rng/ Save/ Tuning/` sub-folders above are an optional split for larger games, and `PlayMode/`, `Art/`, `Audio/`, `Prefabs/` and `Addressable/` are not created until you need them.

Rules:
- Group by layer first, feature second inside the layer. Keep the number of top-level folders small.
- Commit `Packages/manifest.json`, `packages-lock.json`, `ProjectSettings/`, all `.meta` files. Ignore `Library/`, `Temp/`, `Logs/`, `obj/`, `UserSettings/`, build outputs.
- Set Version Control mode to Visible Meta Files and Asset Serialization to Force Text, so diffs and merges are possible.
- Avoid the `Resources/` folder except for a tiny bootstrap; everything else via Addressables or direct references.

## 2. Assembly definitions

An `.asmdef` file defines a compilation unit. Benefits: faster incremental compile, enforced dependency direction, test isolation.

Core assembly (`Game.Core.asmdef`):

```json
{
  "name": "Game.Core",
  "rootNamespace": "Game.Core",
  "references": [],
  "includePlatforms": [],
  "excludePlatforms": [],
  "allowUnsafeCode": false,
  "overrideReferences": false,
  "autoReferenced": true,
  "noEngineReferences": true
}
```

(This is the template's `Assets/_Game/Core/Game.Core.asmdef`, which sets `autoReferenced: true` so scripts in the predefined assemblies can use Core without an extra asmdef; set it to `false` if you want every consumer to reference Core explicitly.)

Presentation (`Game.Presentation.asmdef`): the template references `["Game.Core", "Unity.InputSystem", "UnityEngine.UI"]` because its sample UI is legacy uGUI and Addressables is only staged in the manifest. A game that uses them adds `"Unity.Addressables"`, `"Unity.ResourceManager"` and `"Unity.TextMeshPro"`; reference packages by assembly name (check the package's own asmdef). Mind that GUID-based references can be used instead of names; names are easier to write by hand.

Editor (`Game.Editor.asmdef`): `includePlatforms: ["Editor"]`, references Core and Presentation, `autoReferenced: false`.

Tests: EditMode asmdef has `includePlatforms: ["Editor"]`, `optionalUnityReferences: ["TestAssemblies"]` (older) or references `UnityEngine.TestRunner` and `UnityEditor.TestRunner` and the define constraint `UNITY_INCLUDE_TESTS`; copy from a test asmdef Unity generated. PlayMode asmdef has no platform restriction.

Rules:
- Core must compile with zero Unity references: no `Mathf` (use `System.Math`), no `Vector2` (define your own `struct Int2`), no `Debug.Log` (inject a logger interface), no `Random.value` (own seeded PRNG such as PCG32).
- No cyclic references. If Core needs to call presentation, define an interface in Core and implement it in Presentation.
- `autoReferenced: false` for assemblies other code should reference explicitly (the template does this for `Game.Editor` and `Game.Tests.EditMode`).
- Keep third-party code in its own asmdef to prevent recompiling it with game code.
- Use `#if UNITY_EDITOR` sparingly; prefer an Editor assembly.
- Version defines in asmdef (`versionDefines`) can toggle code if a package is present.

## 3. Lifecycle

| Callback | When | Use for |
|---|---|---|
| `Awake` | on instantiate/scene load, once, even if disabled | own initialization, cache `GetComponent` |
| `OnEnable` | each time enabled | subscribe to events |
| `Start` | before first `Update`, once | cross-object initialization |
| `FixedUpdate` | fixed timestep (default 0.02 s) | physics forces |
| `Update` | each frame | input polling, light logic |
| `LateUpdate` | after all `Update` | camera follow |
| `OnDisable` | disabled or destroyed | unsubscribe |
| `OnDestroy` | destroyed | final cleanup |
| `OnApplicationPause(bool)` | app backgrounded | save, pause audio |
| `OnApplicationFocus(bool)` | focus change | same on some platforms |
| `OnApplicationQuit` | quit (not reliable on mobile) | do not depend on it |

Rules:
- `Awake` order between objects is not guaranteed unless configured in Script Execution Order; do not rely on it.
- Destroyed Unity objects compare equal to `null` via overloaded `==`; `?.` and `??` bypass that and can touch destroyed objects. Use `if (obj != null)` for UnityEngine.Object.
- Coroutines stop when the GameObject is disabled; `await` continuations do not unless you pass a cancellation token (Unity 6 `Awaitable` supports cancellation and `destroyCancellationToken` is available on MonoBehaviour).
- `Time.deltaTime` for visuals, `Time.fixedDeltaTime` in physics; `Time.unscaledDeltaTime` for UI when paused.
- `Application.targetFrameRate` is ignored if vsync count is set on some platforms; set `QualitySettings.vSyncCount = 0` when you want to control the cap.

## 4. ScriptableObjects

```csharp
[CreateAssetMenu(menuName = "Game/Level Definition")]
public sealed class LevelDefinition : ScriptableObject
{
    [SerializeField] private int id;
    [SerializeField] private int moves = 20;
    [SerializeField] private int[] goals = System.Array.Empty<int>();

    public int Id => id;
    public int Moves => moves;
}
```

- They are assets referenced by GUID; ideal for tuning tables, item definitions, config, event channels.
- Runtime changes to an asset persist in the Editor session but not in builds. Treat as read-only; copy into runtime state classes in Core.
- For Core consumption, convert to plain data at the boundary (`LevelDefinition` -> `LevelData` record) so Core stays Unity-free.
- Creating them: editor script `ScriptableObject.CreateInstance<T>()` + `AssetDatabase.CreateAsset(...)` + `AssetDatabase.SaveAssets()`. Do not write the `.asset` YAML by hand.
- JSON data alternative: `TextAsset` with JSON parsed in Core. Good for content generated by tools and easy to diff.

## 5. Serialization pitfalls

| Pitfall | Effect | Fix |
|---|---|---|
| Public property or auto-property | not serialized | field with `[SerializeField]`; for auto-property `[field: SerializeField]` |
| `Dictionary<K,V>` | not serialized by Unity | list of key/value structs, convert at load |
| Interface or abstract field | not serialized | `[SerializeReference]` with concrete types |
| Rename a serialized field | data lost | `[FormerlySerializedAs("oldName")]` |
| `readonly` / `static` / `const` fields | not serialized | use normal fields |
| Nested lists of lists | not supported | wrapper class `[Serializable] class Row { public int[] cells; }` |
| Generic class fields | serializable in recent versions only for concrete generic types | wrap in a concrete subclass |
| Class without `[Serializable]` | not shown or saved | add attribute |
| Null for custom serializable class | Unity creates default instance | check for default state, not null |
| Shared reference in two fields | becomes two copies | `[SerializeReference]` if sharing is needed |
| Changing script class name or namespace | MonoBehaviour link lost | rename via IDE with `[MovedFrom]` or keep file/class names matching |
| File name differs from MonoBehaviour class name | script not attachable | one MonoBehaviour per file, same name |

Save data (not Unity serialization): use your own versioned JSON (`System.Text.Json` is not always available; Unity ships Newtonsoft JSON as a package `com.unity.nuget.newtonsoft-json`, or use `JsonUtility` for simple types with its limits: no dictionaries, no top-level arrays). Atomic write to `Application.persistentDataPath`: write temp file, then `File.Replace`/move, keep a backup.

## 6. Never hand-edit YAML

`.unity`, `.prefab`, `.asset`, `.mat`, `.controller`, `.anim` files are Unity YAML with `fileID` and `guid` links. An agent editing them can:
- break references (wrong `fileID`) without a compile error,
- duplicate fileIDs causing load failures,
- produce merge states the editor reverts.

Instead:
1. Write an editor script `SceneBuilder.Build()` that creates scenes via `EditorSceneManager.NewScene`, instantiates prefabs via `PrefabUtility.InstantiatePrefab`, adds components, sets serialized fields through `SerializedObject`, and saves via `EditorSceneManager.SaveScene`.
2. Run it in batchmode (the template's entry is `-executeMethod Game.EditorTools.SceneBuilder.BuildAll -quit`, a wrapper that exits with code 0 or 1 around the same `Build()` that backs the `Game > Build Scene and Settings` menu item). Idempotent: re-running yields the same scenes.
3. Create prefabs via `PrefabUtility.SaveAsPrefabAsset`.
4. Set private serialized fields in editor code with `var so = new SerializedObject(comp); so.FindProperty("field").objectReferenceValue = x; so.ApplyModifiedPropertiesWithoutUndo();`
5. For read-only inspection of YAML (finding references), reading is fine; do not write.
6. Exception: `ProjectSettings/*.asset` values (like bundle id) are better set via `PlayerSettings.*` APIs in an editor script than by YAML edits. `Packages/manifest.json` is plain JSON and safe to edit.

## 7. Coding rules for mobile

Allocation and GC (the Unity runtime GC causes hitches when it collects):
- Avoid per-frame `new`, boxing, string concatenation/interpolation, LINQ, `foreach` over non-array/List in old runtimes (modern Mono/IL2CPP handle `List<T>` foreach without allocation), closures capturing locals, `GetComponent` and `Find*` in `Update`.
- Cache references; reuse `List<T>` buffers (`Clear()`); use `StringBuilder` or `TextMeshPro.SetText` with number overloads for HUD.
- Pool bullets, popups, particles (`UnityEngine.Pool.ObjectPool<T>` exists).
- Use `CompareTag("x")` not `tag == "x"`.
- Prefer `struct` for tiny immutable data; avoid huge structs passed by value.
- Use `Physics.RaycastNonAlloc`/`OverlapSphereNonAlloc` variants.

Other:
- Prefer events (`System.Action`, UnityEvents sparingly) over polling.
- Use `Awaitable` (Unity 6) or UniTask (third-party) for async; remember Unity's synchronization context is the main thread.
- Logging: strip logs in release (`[Conditional("UNITY_EDITOR")]` wrapper or `Debug.unityLogger.logEnabled = false` for release builds); string building for logs allocates.

## 8. URP settings for mobile

URP (Universal Render Pipeline) is the default recommended pipeline for mobile. Settings live in a URP Asset (one per tier) plus a Renderer asset.

| Setting | Low | Mid | High | Notes |
|---|---|---|---|---|
| Render scale | 0.7-0.85 | 0.85-1.0 | 1.0 | lower on high-DPI phones; UI renders at full res in overlay canvas |
| HDR | off | off | on only if used | HDR costs bandwidth |
| MSAA | off | 2x | 2x-4x | use FXAA/SMAA in post only if needed |
| Shadows | off | main light, 1 cascade, short distance | 2 cascades | shadows are expensive; fake blob shadows for 2D/stylized |
| Soft shadows | off | off | on | |
| Additional lights | off or per-vertex | few per-pixel | more | forward+ rendering path removes per-object limits but costs more; verify device support |
| Depth texture / Opaque texture | off unless a shader needs them | | | |
| Post-processing | minimal (bloom light, vignette) | | | each effect is a full-screen pass; tile-based GPUs dislike many passes |
| SRP Batcher | on | on | on | needs SRP-compatible shaders |
| GPU instancing / GPU Resident Drawer | enable where content fits | | | verify support per version |
| Dynamic batching | off (rarely helps) | | | |

Guidance:
- Create three URP assets (Low, Mid, High); map them in Project Settings > Quality per platform; select at startup by device tier (`SystemInfo.graphicsMemorySize`, `processorCount`, device model lists, or Adaptive Performance indices).
- Use URP/Lit sparingly on mobile; prefer URP/Simple Lit or Unlit for most content; write custom shaders with Shader Graph and keep instruction counts small.
- Transparent overdraw is the most common mobile GPU killer: avoid large alpha-blended layers; use tight sprite meshes (Sprite Mesh type: Tight) and compress particle count.
- 2D games: use the Universal 2D renderer; sprite atlases (Sprite Atlas v2); keep to few materials; 2D lights are costly, bake or fake them.
- Some newer versions add on-tile post-processing for HDR, tone mapping and color grading in one pass on Vulkan and Metal; reported in a recent non-LTS release, so verify it exists in your LTS before relying on it.
- Test the Frame Debugger to count draw calls and see why batches break; use RenderDoc (Android) and Xcode GPU capture (iOS) for GPU detail.

## 9. Player settings

| Setting | Android | iOS |
|---|---|---|
| Scripting backend | IL2CPP | IL2CPP (only option) |
| Architectures | ARM64 (add ARMv7 only if you must) | ARM64 |
| Graphics APIs | Vulkan + GLES3 fallback (or Vulkan only if min device allows) | Metal |
| Minimum API / iOS | choose by audience; min SDK per your SDK deps | choose per SDK deps |
| Target API level | highest installed, meeting Play policy | n/a |
| Compression | LZ4 (dev) / LZ4HC (release) | LZ4 |
| Managed stripping | Medium or High + `link.xml` | same |
| Build format | AAB for Play | Xcode project |
| Orientation | lock to supported orientation(s) | same |
| Splash | custom or default per plan | launch screen |
| Incremental GC | enabled | enabled |
| Camera/Mic usage strings | n/a | required for any permission API used |
| Texture compression | ASTC | ASTC |
| Optimize Mesh Data, strip unused shader variants | on | on |
| Multithreaded rendering / Graphics jobs | on after testing | on |

Additional:
- Strip engine code: enable "Strip Engine Code"; remove unused modules in Package Manager built-in packages.
- `link.xml` preserves types accessed via reflection (JSON libraries, some SDKs).
- Set the bundle identifier and versions through a build script from CI variables.
- 16 KB page-size: Unity versions after a given 6.x patch support aligned native libs; verify your editor version and every native plugin (volatile).

## 10. Addressables

Use when content exceeds ~tens of MB, you want remote content or on-demand loading, or you need memory control.

- Mark assets addressable (groups). Pack Together by feature or level pack; Pack Separately for large unique assets.
- Load with `Addressables.LoadAssetAsync<T>(key)` and always `Release` handles; track handles in a cache with reference counts.
- Instantiate with `Addressables.InstantiateAsync` and release with `ReleaseInstance`.
- Labels for bulk preloading (for example "level_pack_1").
- Remote content: build with a catalog, host on a CDN, versioned paths; check catalog update at startup; keep a local fallback. Store policies on downloaded code: assets and data are fine; downloading executable code is restricted on iOS.
- CI: run the Addressables build (`AddressableAssetSettings.BuildPlayerContent()`) before the player build in the BuildScript.
- Pitfalls: forgetting to release leaks memory; duplicating dependencies across groups bloats size (use Analyze rules); content built against a different editor version breaks.
- Small projects: direct references and scene loading are simpler. Do not adopt Addressables just because.

## 11. Input System

Use the new Input System package for new projects; the legacy Input Manager still works but is on the way out. Set Active Input Handling to the new system (or both during migration).

- Create an Input Actions asset: action maps (Gameplay, UI), actions (Tap, Swipe, Pan, Pinch), control schemes.
- Touch: `EnhancedTouchSupport.Enable()` then `Touch.activeTouches`; use `Touch.onFingerDown/Move/Up` events. `Pointer` and `Touchscreen` devices are also available; use one approach consistently.
- UI: Input System UI Input Module on the EventSystem (the `InputSystemUIInputModule`).
- Swipe: track start position and time; thresholds relative to screen size in inches (`Screen.dpi`) rather than pixels.
- Simulator: Device Simulator in the editor for safe area and screen sizes; mouse emulates touch.
- Remap or disable actions by map to prevent UI and gameplay from both reacting to a tap.
- Test: `InputTestFixture` from the Input System test package to simulate touches in PlayMode tests.

## 12. UI choice

| Option | Strengths | Weaknesses | Pick when |
|---|---|---|---|
| uGUI (Canvas + TextMeshPro) | mature, many assets, tooling, runtime-friendly | Canvas rebuilds, GC pitfalls, scene-based | most mobile games today |
| UI Toolkit | retained mode, USS styling, good for editor tools and scalable UI, UXML text assets agents can write | runtime feature gaps for some game UI needs (world space, some effects, depending on version), verify | menu-heavy apps, tools, data-driven UI |
| IMGUI | quick debug panels | slow, editor-oriented | debug only |

Canvas performance:
- Split canvases by update frequency (static background, dynamic HUD, animating popups); a change in one element rebuilds its canvas batch.
- Disable `Raycast Target` on non-interactive Images and text.
- Avoid layout groups on frequently changing content; avoid nested layout groups; avoid `Mask` (use `RectMask2D`).
- Use sprite atlases for UI; keep text objects few; TextMeshPro for text; avoid per-frame text allocation.
- Canvas Scaler: Scale With Screen Size, reference 1080x1920 (portrait), match 0.5 or width/height by orientation.
- Use Screen Space - Overlay for HUD (cheapest) or Camera space when you need post effects on the UI.

For an agent, UI Toolkit's UXML/USS are text and easier to write correctly than uGUI scene hierarchies, which must be built by SceneBuilder code; weigh that against runtime capability gaps.

## 13. Safe area and aspect

```csharp
public sealed class SafeAreaFitter : MonoBehaviour
{
    [SerializeField] private RectTransform target = null!;
    private Rect _last;
    private Vector2Int _res;

    private void OnEnable() => Apply();
    private void Update()
    {
        if (_last != Screen.safeArea || _res.x != Screen.width || _res.y != Screen.height) Apply();
    }
    private void Apply()
    {
        _last = Screen.safeArea; _res = new Vector2Int(Screen.width, Screen.height);
        var min = _last.position; var max = _last.position + _last.size;
        min.x /= Screen.width; min.y /= Screen.height;
        max.x /= Screen.width; max.y /= Screen.height;
        target.anchorMin = min; target.anchorMax = max;
    }
}
```

(`null!` with nullable context is a common Unity idiom for serialized fields; if nullable is off, drop the `!`.)

- Put the interactive HUD under the fitter; let backgrounds fill the full screen.
- Handle extremes: 16:9 to 21:9 portrait, tablets (4:3), foldables. Use Device Simulator and test devices.
- Touch target at least 48 dp: convert with `Screen.dpi` (`dp = px / (dpi/160)`).

## 14. Project hygiene

- Use `.editorconfig`, enable analyzers; treat compile warnings as errors in Core.
- Pin package versions in `manifest.json`; update deliberately.
- Keep a `README` listing editor version, required modules (Android/iOS build support, IL2CPP), and command to run tests and build.
- Use `Debug.Assert` in editor and conditional logging.
- Avoid `Resources.Load`, `SendMessage`, string-based `Invoke` (renames break them silently).
- Beware of third-party assets with their own asmdef-less code in `Assets/`; move to `Plugins` or wrap.

## 15. Volatile facts (as of Oct 2026 - verify)

| Fact | Source |
|---|---|
| Unity 6.3 LTS shipped Dec 2025 and is supported to Dec 2027; a 6.5 release (June 2026) was already end of life by Oct 2026; Unity was progressing towards a 6.7 LTS; 6.0 LTS support ends Oct 2026 | https://www.cgchannel.com/2025/12/unity-6-3-lts-is-out-see-5-key-features-for-cg-artists/ and https://discussions.unity.com/t/unity-6-5-is-now-available/1723176 |
| 6.3 LTS: GPU Resident Drawer reported to cut CPU frame time in heavily instanced scenes (third-party claim); URP and HDRP share a compiler and API | https://www.cgchannel.com/2025/12/unity-6-3-lts-is-out-see-5-key-features-for-cg-artists/ |
| 6.5: On-Tile Post Processing, ThinLTO Android builds, reported average gain around 5 percent, experimental Swift project type for iOS | https://discussions.unity.com/t/unity-6-5-is-now-available/1723176 |
| Unity Personal is free under a revenue and funding threshold; Pro price rose in Jan 2026; runtime fee cancelled in 2024 | https://unity.com/products/pricing-updates |
| Native library 16 KB alignment, privacy manifest and Play target API requirements | not in the notes; check Unity release notes for your editor version and store policy pages |

Do not hard-code any of these into project docs without re-checking; choose the newest LTS that your SDK set supports.
