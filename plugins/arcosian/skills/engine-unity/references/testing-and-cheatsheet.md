# Unity Testing, Verification and API Cheatsheet

Summary: the Unity test stack an agent can run headless and read as data. It covers the Test Framework (EditMode and PlayMode, NUnit XML output), the Performance Testing package for budgets, the Graphics Test Framework for image comparison, device automation with AltTester, CI with GameCI, deterministic playthroughs through the pure Core assembly, and a set of short API recipes for frequently needed tasks. Pairs with `references/editor-automation-and-services.md` for the batchmode mechanics.

## Contents
1. The verification ladder
2. Test Framework basics
3. Running tests headless
4. EditMode tests for Core
5. PlayMode tests
6. Deterministic playthroughs and bots
7. Performance Testing package
8. Graphics Test Framework
9. Device automation: AltTester and others
10. GameCI in CI
11. Reading results
12. API recipes
13. Troubleshooting

## 1. The verification ladder

| Rung | Proves | Cost | Tool |
|---|---|---|---|
| Compile | code builds, no missing references | seconds to minutes | a clean batchmode run (template: `SceneBuilder.BuildAll` or the EditMode run exits 0 and `unity.log` has no `error CS`) |
| EditMode | Core rules, save migrations, tuning data | seconds | Test Framework |
| PlayMode | MonoBehaviours, scene wiring, UI flows | tens of seconds | Test Framework |
| Playthrough | scripted or bot run through Core reaches expected states | seconds | `Game.EditorTools.PlaytestRunner.Run` in batchmode (section 6), or the same `Playthrough` code inside an EditMode test |
| Perf | frame time, allocations, memory against budget | minutes, needs device for truth | Performance Testing |
| Visual | rendered frames match or are reviewed | needs GPU | Graphics tests, screenshots |
| Device | real touch, thermals, SDKs | manual or farm | AltTester, Firebase Test Lab, device cloud |

Done means the cheapest applicable rungs pass on the exact commit, with output files stored under `.gamestudio/evidence/<FEATURE-ID>/`.

## 2. Test Framework basics

The Unity Test Framework (`com.unity.test-framework`, built on NUnit) provides:
- EditMode tests: run in the editor without entering play mode; can use `UnityEditor` APIs; fast.
- PlayMode tests: run in play mode (or on a device build); `[UnityTest]` methods are coroutines that yield frames.

Assembly rules: tests live in test assemblies (asmdef referencing `UnityEngine.TestRunner` and `UnityEditor.TestRunner` with the `UNITY_INCLUDE_TESTS` constraint). EditMode test asmdef includes only the Editor platform. Generate one through Assets > Create > Testing > Test Assembly Folder and then edit references, so the boilerplate is right.

Attributes (NUnit): `[Test]`, `[TestCase(1, 2)]`, `[TestCaseSource(nameof(Cases))]`, `[SetUp]`, `[TearDown]`, `[OneTimeSetUp]`, `[Category("Slow")]`, `[Timeout(ms)]`, `[UnityTest]` (returns `IEnumerator`), `[UnitySetUp]`, `[UnityTearDown]`.

## 3. Running tests headless

```
"<Unity>" -batchmode -projectPath "<abs>" \
  -runTests -testPlatform EditMode \
  -testResults "<abs>/editmode.xml" \
  -logFile "<abs>/unity.log"
```

The template (`${CLAUDE_PLUGIN_ROOT}/templates/unity-mobile/`) runs its EditMode suite as `Unity -batchmode -nographics -projectPath <p> -runTests -testPlatform EditMode -testResults <abs>/unit.xml -logFile <abs>/unity.log` (exit 0 ok, 2 failures; NUnit XML output). The same Core and EditMode tests also build and run on the plain .NET SDK without a Unity licence: `python3 tools/dotnet-harness/build_harness.py . /tmp/unity-harness`, then `cd /tmp/unity-harness/Tests && UNITY_ASSETS_DIR="$OLDPWD/Assets" dotnet test` (the harness compiles the real `Assets/_Game/Core/**/*.cs` and `Assets/_Game/Tests/EditMode/*.cs`, stubbing only `Application.dataPath`, `Vector2` and `Mathf.Abs`).

- `-testPlatform PlayMode` for play mode (requires a graphics device unless tests avoid rendering; do not pass `-nographics` if tests need a camera or UI).
- `-testFilter "Namespace.Class.Method;Other"` and `-testCategory "Fast"` select subsets.
- Do not combine with `-quit`; the runner exits itself.
- Exit code is non-zero when tests fail (code 2 commonly signals failures; verify with your version) and other non-zero codes mean runner errors; always parse the XML.
- Results are NUnit 3 XML: `<test-run result="Passed" total="n" passed="n" failed="0">`, nested `<test-case name= result= duration=>`. Convert to JUnit for generic CI if needed (GameCI does this).
- With the Unity CLI (see the automation reference) a test command may exist; verify with `--help`.
- Compile errors cause the run to fail before any test; check the log first.

## 4. EditMode tests for Core

Because Core has no Unity references, tests are plain NUnit and can even run outside Unity with `dotnet test` if you add an SDK-style csproj that includes the same sources; this gives sub-second feedback and a second CI path. Do this when the team will iterate on Core heavily.

```csharp
using System.Collections.Generic;
using NUnit.Framework;
using Game.Core;

public class MergeRulesTests
{
    // SimEvent.ToString() is the stable text form that tests compare.
    private static string Flat(List<SimEvent> events) { return string.Join("\n", events); }

    [Test]
    public void SameSeedSameEvents()
    {
        var a = new Sim(5); var b = new Sim(5);
        foreach (string dir in new[] { "left", "down", "right", "up" })
            Assert.AreEqual(Flat(a.Apply(GameAction.Move(dir))), Flat(b.Apply(GameAction.Move(dir))), dir);
        CollectionAssert.AreEqual(a.State.Grid, b.State.Grid);
    }

    [Test]
    public void EachTileMergesOnce()
    {
        var grid = new int[25]; grid[0] = grid[1] = grid[2] = grid[3] = 2;
        SlideResult r = Sim.SlideGrid(grid, 5, "left");     // pure rule, no Sim instance needed
        Assert.AreEqual(4, r.Grid[0]); Assert.AreEqual(4, r.Grid[1]); Assert.AreEqual(8, r.Gain);
    }

    [Test]
    public void SaveRoundTrip()
    {
        var s = new Sim(1); s.Apply(GameAction.Move("up"));
        var copy = new Sim(99);
        Assert.IsTrue(copy.LoadDict((Dictionary<string, object>)MiniJson.Parse(MiniJson.Write(s.ToDict()))));
        Assert.AreEqual(MiniJson.Write(s.ToDict()), MiniJson.Write(copy.ToDict()));
    }
}
```

These use the template's real API (`Sim`, `GameAction`, `SimEvent`, `SlideResult`, `MiniJson`); the template's own `Assets/_Game/Tests/EditMode/SimTests.cs` holds the full suite. Test checklist: determinism, round trips, boundaries, invalid input, migrations, invariants over thousands of seeded random actions, economy rules (never negative currency, idempotent grants).

Data validation tests (EditMode): load every ScriptableObject or JSON level and assert shape (ids unique, goals reachable via solver, references non-null). These catch content errors early.

## 5. PlayMode tests

```csharp
using System.Collections;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

public class GameSceneSmoke
{
    [UnityTest]
    public IEnumerator GameSceneLoadsAndShowsBoard()
    {
        yield return SceneManager.LoadSceneAsync("Game");
        yield return null; // one frame for Start
        var view = Object.FindFirstObjectByType<Game.Presentation.BoardView>();
        Assert.IsNotNull(view);
        LogAssert.NoUnexpectedReceived();
    }
}
```

Tips:
- `LogAssert.Expect` for expected errors; any unexpected `LogType.Error` or exception fails the test by default, which is useful.
- Use `InputTestFixture` (Input System package) to simulate touches: `Begin`/`Move`/`End` on a `Touchscreen`.
- Keep PlayMode tests few and meaningful; they are slower and flakier. Prefer EditMode on Core for rules.
- Load scenes by name registered in Build Settings, or use `EditorSceneManager.LoadSceneInPlayMode` in editor-only tests.
- Use `yield return new WaitForSeconds` sparingly; wait on conditions (`yield return new WaitUntil(() => cond)` with a timeout attribute).
- Mock services with the interfaces from the services layer.

## 6. Deterministic playthroughs and bots

The Unity template already contains this machinery, in the same format as the Godot template: a playthrough is data (seed plus a list of actions with expectations) executed against Core. The runners are `Playthrough.RunScript(json, tuning, seedOverride, build, out error)` and `Playthrough.RunBots(bot, runs, seed, tuning, build, out error)` in `Assets/_Game/Core/Playthrough.cs`; each returns a playtest-report dictionary (schema_version 1.0) that `MiniJson.Write` serialises. `Editor/PlaytestRunner.Run` wraps them for batchmode, so no PlayMode or Unity Test Framework run is involved:

```
Unity -batchmode -nographics -projectPath <p> -executeMethod Game.EditorTools.PlaytestRunner.Run \
  -gsMode script -gsScript Assets/_Game/Tests/Playthroughs/smoke.json -gsOut <abs>/playthrough.json -quit
Unity -batchmode -nographics -projectPath <p> -executeMethod Game.EditorTools.PlaytestRunner.Run \
  -gsMode bot -gsBot greedy -gsRuns 200 -gsSeed 1 -gsOut <abs>/bots.json -quit
```

Exit codes: 0 pass, 1 fail or softlocks, 2 usage error.

- Store playthrough JSON under `Assets/_Game/Tests/Playthroughs/` (`smoke.json` ships with the template). Format: `{"schema_version":"1.0","seed":1,"steps":[{"action":{"type":"move","dir":"left"},"expect":{"status":"playing","moves":{"op":">=","value":0}}}]}`; expect paths are those of `GameState.Lookup` (`score`, `moves`, `status`, `won`, `lost`, `max_tile`, `empty_count`, `grid_sum`, `grid.<index>`); ops are `==` (default), `!=`, `>=`, `<=`, `>`, `<`.
- The same code runs inside EditMode tests (`SmokePlaythrough_Passes`, `Playthrough_ReportsFailedExpectations`, `GreedyBot_NeverSoftlocks` in `SimTests.cs`), so a failing playthrough also fails the unit gate.
- Bots are `greedy` and `random`; both pick among the moves for which `Sim.SlideGrid(...).Moved` is true (the template has no `LegalActions` method; add one when your game has more than four actions). For a new game, extend `GameState.Lookup` with your state paths and `GameAction.FromDict` with your action types, and keep action names identical in scripts and bot policies.
- Assert softlocks == 0; assert greedy win rate in the designed range; the random-vs-greedy gap shows skill depth.
- Time metrics are modeled (`Playthrough.SecPerMove` = 0.8 s per accepted move), not measured; label them "estimated".
- Because Core has no engine dependency, thousands of games run in seconds.

## 7. Performance Testing package

`com.unity.test-framework.performance` adds measurement APIs for tests and output to JSON.

```csharp
using Unity.PerformanceTesting;

[Test, Performance]
public void SimApply_1000Actions()
{
    var sim = new Sim(1);
    Measure.Method(() => sim.Apply(RandomAction()))
        .WarmupCount(10).MeasurementCount(20).IterationsPerMeasurement(50)
        .GC().Run();
}

[UnityTest, Performance]
public IEnumerator GameScene_FrameTime()
{
    yield return SceneManager.LoadSceneAsync("Game");
    using (Measure.Frames().Scope()) { yield return new WaitForSeconds(5); }
}
```

- `Measure.Method`, `Measure.Frames`, `Measure.Scope`, `Measure.ProfilerMarkers(...)`, `Measure.Custom(...)`, and `.GC()`.
- Results are written into the test result XML/JSON with sample groups (median, min, max, percentiles, standard deviation). Compare to baselines in CI and fail on regressions beyond a tolerance (for example 10 percent over the stored median).
- Editor and desktop numbers are not mobile numbers. Run PlayMode performance tests on a device build via the Test Runner (player build) when budgets matter, and treat editor runs as relative regression detection only.
- Convert results into the plugin's perf-report JSON and check with `${CLAUDE_PLUGIN_ROOT}/scripts/perf_budget.py`.
- Allocation checks: assert zero GC allocation for hot paths with `Measure.Method(...).GC()` and `Assert` on the sample group value.

Device profiling procedure:
1. Development build with autoconnect profiler (`BuildOptions.Development | BuildOptions.ConnectWithProfiler`).
2. Profiler (CPU, GPU, memory, rendering) and Frame Debugger; capture 60 seconds of representative play.
3. Platform tools: Android Studio profiler / Perfetto / RenderDoc; Xcode Instruments (Metal System Trace, Energy, Thermal State).
4. Record p50 and p95 frame time, GC allocations per frame, peak memory, draw calls, thermal state, device and OS version.
5. Check against the budgets in the design contract.

## 8. Graphics Test Framework

`com.unity.testframework.graphics` renders a scene and compares the image to a stored reference with a tolerance (`ImageAssert.AreEqual`). Use for shader and VFX regression where deterministic output is expected.
- Requires a GPU; run on a fixed runner; references differ between GPUs and APIs, so keep one reference set per configuration and a generous threshold.
- Good fit: UI layouts at fixed resolutions, shader outputs, sprite rendering. Poor fit: particle randomness, anything time-dependent unless seeded and time-stepped.
- Capture screenshots for human or critic review otherwise: `ScreenCapture.CaptureScreenshot(path)` or render a camera to a `RenderTexture` and `EncodeToPNG`.
- Review checklist for a screenshot: clipped text, overlap, safe-area violations, contrast, touch target sizes, placeholder art, debug UI visible.

## 9. Device automation: AltTester and others

- AltTester (AltTester Unity SDK plus a driver in Python, C#, Java or other) instruments a development build so tests can find GameObjects by name/path/component, click and swipe, read properties and take screenshots on a real device or emulator. Use for end-to-end flows (FTUE, purchase mock, shop navigation) on devices.
- Requires a development build with the AltTester instrumentation and a running AltTester server; strip it from release builds (use a scripting define such as `ALTTESTER` only in test builds).
- Other options: Firebase Test Lab or device clouds running Robo tests or instrumented tests against the APK; Appium for black-box UI automation (weak for game canvases); the Unity Test Framework run on-device (build a player with tests included and run `-runTests -testPlatform Android`; check docs for your version).
- Keep a small, stable E2E suite (smoke: launch, play first level, win, reward, restart) rather than a large flaky one.
- Licensing and pricing for AltTester features, device farms and their limits are volatile; verify.

## 10. GameCI in CI

GameCI provides GitHub Actions and Docker images for Unity.
- `game-ci/unity-test-runner`: runs EditMode and PlayMode tests, outputs XML, supports code coverage packages.
- `game-ci/unity-builder`: builds players for the target platform with `buildMethod`, `versioning`, `androidKeystoreBase64` and related secrets inputs.
- `game-ci/unity-activate`: licence activation helper.
- Matrix over editor version and target platform; cache `Library`.
- Run tests on every pull request; build only on main and tags; upload test XML, build report and artifacts.
- Pin action versions by commit or tag; review third-party actions before giving them secrets.

Minimal job outline: checkout (with LFS) -> cache Library -> test-runner (EditMode) -> test-runner (PlayMode) -> builder (Android) -> upload artifacts. See `templates/ci/` for the maintained workflow files.

## 11. Reading results

| Artifact | How to read |
|---|---|
| NUnit XML | `<test-run>` attributes for totals; each failing `<test-case>` has `<failure><message>` and `<stack-trace>`; first failure is usually the root cause |
| Unity log | grep `error CS`, `Exception`, `NullReferenceException`, `[BUILD]` markers, `Build completed with a result of` |
| Build report | `BuildReport.summary` (result, totalSize, totalTime), `report.steps`, `report.GetFiles()` for size attribution |
| Performance results | sample group name, median, p95 (if configured), unit; compare to baseline |
| Playtest report JSON | pass/fail, win rate, softlock count, per-seed details |

Triage order: compile errors -> test failures -> warnings in the log that mention serialization, missing scripts or missing references -> perf regressions.

## 12. API recipes

Project settings from an editor script:

```csharp
PlayerSettings.SetApplicationIdentifier(NamedBuildTarget.Android, "com.studio.game");
PlayerSettings.SetScriptingBackend(NamedBuildTarget.Android, ScriptingImplementation.IL2CPP);
PlayerSettings.Android.targetArchitectures = AndroidArchitecture.ARM64;
PlayerSettings.SetManagedStrippingLevel(NamedBuildTarget.Android, ManagedStrippingLevel.Medium);
PlayerSettings.defaultInterfaceOrientation = UIOrientation.Portrait;
```

(`NamedBuildTarget` overloads are the current API; older `BuildTargetGroup` versions are deprecated.)

Frame rate and vsync:

```csharp
QualitySettings.vSyncCount = 0;
Application.targetFrameRate = 60;
```

Addressables load and release:

```csharp
var handle = Addressables.LoadAssetAsync<GameObject>("level_03");
var prefab = await handle.Task;
// ... use ...
Addressables.Release(handle);
```

Save file atomically:

```csharp
var path = System.IO.Path.Combine(Application.persistentDataPath, "save.json");
var tmp = path + ".tmp";
System.IO.File.WriteAllText(tmp, json);
if (System.IO.File.Exists(path)) System.IO.File.Replace(tmp, path, path + ".bak");
else System.IO.File.Move(tmp, path);
```

Pause handling:

```csharp
private void OnApplicationPause(bool paused) { if (paused) saveService.Flush(); }
```

Object pool:

```csharp
private readonly ObjectPool<Popup> _pool = new(
    createFunc: () => Instantiate(prefab),
    actionOnGet: p => p.gameObject.SetActive(true),
    actionOnRelease: p => p.gameObject.SetActive(false),
    defaultCapacity: 8, maxSize: 32);
```

Tween alternatives: DOTween and LeanTween (third-party, check licences) or hand-rolled lerps in a central ticker; Unity 6 has no built-in general tween library.

Read a JSON text asset in Core-friendly way: `TextAsset ta = Resources.Load<TextAsset>(...)` is discouraged; use a serialized `TextAsset` field or Addressables, then `ta.text` into Core parse functions.

Detect low-end device (heuristic):

```csharp
bool low = SystemInfo.systemMemorySize < 3000 || SystemInfo.processorCount <= 4;
```

Treat as a starting point and refine with a device list from analytics.

Safe area: see the SafeAreaFitter in `references/csharp-project-and-urp.md`.

Editor script that creates a ScriptableObject asset:

```csharp
var asset = ScriptableObject.CreateInstance<LevelDefinition>();
AssetDatabase.CreateAsset(asset, "Assets/_Game/Data/Levels/Level01.asset");
AssetDatabase.SaveAssets();
```

## 13. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `-executeMethod` silently does nothing | method not static, wrong name, or compile error | check log for `executeMethod class ... not found` and fix |
| Tests not discovered | missing `UNITY_INCLUDE_TESTS` constraint or asmdef references | regenerate test asmdef from Unity menu |
| PlayMode tests hang in CI | `-nographics` with rendering tests, or missing `-quit` handling | remove `-nographics` for those tests, set timeouts |
| Different results editor vs device | IL2CPP stripping removed code, or different GPU API | add `link.xml`, test on device |
| `MissingReferenceException` after scene build | SceneBuilder set a field by wrong name | verify `FindProperty` names against serialized fields |
| Project opens with "needs upgrade" in CI | editor version mismatch | match `ProjectSettings/ProjectVersion.txt` |
| Build size jumped | new SDK or uncompressed textures | read build report file list, fix import settings |
| Android build fails on Gradle resolution | SDK dependency conflicts | use the External Dependency Manager resolve, pin versions |
| Licence error in CI | activation expired or wrong secret | re-activate, check the licence type flow |
