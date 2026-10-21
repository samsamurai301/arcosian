# Unity Editor Automation, CI and Services

Summary: how an agent drives the Unity editor without a human: the 2026 Unity CLI (which replaced the deprecated in-editor MCP server), plain batchmode with `-executeMethod`, the SceneBuilder and BuildScript patterns, CI licence activation, and community MCP servers such as CoplayDev unity-mcp. It also covers the service SDK landscape for mobile (IAP, LevelPlay, AppLovin MAX, Firebase, RevenueCat, notifications, Adaptive Performance). Tool availability and pricing in this area move quickly, so those facts sit in a volatile-facts section.

## Contents
1. Choosing an automation channel
2. Batchmode basics
3. SceneBuilder pattern
4. BuildScript pattern
5. Unity CLI (2026)
6. CoplayDev unity-mcp and other MCP servers
7. CI and licence activation
8. Services overview
9. IAP
10. Ads and mediation
11. Analytics, crash and remote config
12. RevenueCat and entitlements
13. Notifications
14. Adaptive Performance
15. SDK integration checklist
16. Volatile facts (as of Oct 2026 - verify)

## 1. Choosing an automation channel

| Channel | Strength | Weakness | Use for |
|---|---|---|---|
| Batchmode `-executeMethod` | deterministic, no extra tooling, works in CI | each call starts the editor (slow, tens of seconds) | builds, scene generation, tests, asset import, release pipeline |
| Unity CLI | manages editor installs and projects, runs headless builds and tests, drives a running editor (`unity command`, `unity eval`) | newer tool; verify exact subcommands | agent loops with a running editor, CI |
| Community MCP server (CoplayDev unity-mcp and others) | rich editor tools: hierarchy, components, scripts, console, play mode | third party, security surface, version coupling | interactive building and debugging |
| In-editor official MCP server | was official | reported deprecated in favor of the CLI; gated by a paid add-on for some tiers | do not depend on it |

Rule: pipelines that must be reproducible (CI, release candidates) use batchmode or CLI. Interactive exploration may use an MCP server. Whatever the agent does interactively must be captured as code in `Assets/_Game/Editor/` so the result can be rebuilt.

## 2. Batchmode basics

```
"<UnityPath>/Unity" -batchmode -nographics -quit \
  -projectPath "<abs project>" \
  -executeMethod Game.EditorTools.SceneBuilder.BuildAll \
  -logFile "<abs>/unity.log"
```

That is the real scene-generation command of `${CLAUDE_PLUGIN_ROOT}/templates/unity-starter/` (macOS editor path: `/Applications/Unity/Hub/Editor/<ver>/Unity.app/Contents/MacOS/Unity`). The template's other batch entry points follow the same shape:

| Entry point (namespace `Game.EditorTools`) | Extra flags | Output and exit codes |
|---|---|---|
| `PlaytestRunner.Run` | `-gsMode script\|bot`, `-gsOut <report.json>` (required), `-gsScript <playthrough.json>` (script mode), `-gsBot greedy\|random`, `-gsRuns 200`, `-gsSeed 1` | playtest-report JSON; 0 pass, 1 fail or softlocks, 2 usage |
| `SceneBuilder.BuildAll` | none | `Assets/_Game/Scenes/Main.unity` plus Player settings; 0 ok, 1 error |
| `BuildScript.BuildAndroid` | `-gsOut Builds/Android/game.aab` (must end in `.aab`) | AAB; 0 built, 1 failed, 2 usage |
| `BuildScript.BuildIOS` | `-gsOut Builds/iOS` | Xcode project; 0 built, 1 failed |
| `ScreenshotCapture.Run` | `-gsOut <abs dir>`; omit `-nographics` | `start.png`, `played.png`; 0 ok, 1 failed, 2 usage |

All of them read the `-gs*` flags through the shared `GsArgs` helper (`Assets/_Game/Editor/BuildScript.cs`), resolve relative paths against the project root and exit through `EditorApplication.Exit(code)`, so the process exit code is the method's own. The EditMode test run is Unity's, not a method: `-runTests -testPlatform EditMode -testResults <abs>/unit.xml` without `-quit`. The complete table is in `${CLAUDE_PLUGIN_ROOT}/templates/unity-starter/README.md`.

| Flag | Meaning |
|---|---|
| `-batchmode` | no interactive UI |
| `-nographics` | no GPU device (cannot render screenshots; omit when capturing images or running tests needing graphics) |
| `-quit` | exit after the method returns (do not use with async operations that need frames) |
| `-projectPath` | absolute path |
| `-executeMethod` | `Namespace.Class.StaticMethod`; must be static, in an Editor assembly or `Editor` folder |
| `-logFile` | write log to a file (use `-` for stdout) |
| `-buildTarget` | switch active target before running |
| `-runTests -testPlatform EditMode` | run tests (see testing reference) |
| `-username -password -serial` | manual licence activation (CI secrets) |
| `-returnlicense` | release a serial licence |
| `-accept-apiupdate` | allow automatic API updater to run |

Exit codes: 0 success; non-zero on failure, but a failed `executeMethod` may only log exceptions. Make your method set the exit code explicitly: `EditorApplication.Exit(1)` after catching exceptions. Always read the log for `error CS` and `Exception`.

Practical rules:
- First run on a fresh checkout imports every asset and can take long; cache `Library/` in CI by hash of `Packages/` and `ProjectSettings/`.
- Only one Unity instance can open a project; close the editor or use a copy. A stale lock file `Temp/UnityLockfile` means another instance runs or crashed.
- Compile errors anywhere in the project abort `executeMethod`; fix compile first (run a no-op method to compile).
- The editor log location on macOS: `~/Library/Logs/Unity/Editor.log`.
- Use `Debug.Log` prefixes (for example `[BUILD]`) and grep the log.

## 3. SceneBuilder pattern

Goal: scenes and prefabs are generated by code, never edited as YAML, so builds are reproducible and agent-safe.

The template's own `SceneBuilder` (`Assets/_Game/Editor/SceneBuilder.cs`) is the smallest instance of the pattern: `Build()` (also the `Game > Build Scene and Settings` menu item) creates `Assets/_Game/Scenes/Main.unity` holding only a camera and the `Bootstrap` component, wires `Bootstrap.tuningJson` to `Assets/_Game/Data/tuning.json` through a `SerializedObject`, registers the scene in Build Settings and applies the mobile Player settings (portrait, IL2CPP, ARM64, min SDK 24, a placeholder bundle id only while it is still Unity's default). `BuildAll()` wraps it in `GsArgs.Run` for batch use. The sample below is the multi-scene, prefab-based version of the same idea.

```csharp
#nullable enable
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Game.EditorTools
{
    public static class SceneBuilder
    {
        [MenuItem("Game/Build Scenes")]
        public static void Build()
        {
            try
            {
                BuildBoot();
                BuildGame();
                AssetDatabase.SaveAssets();
                Debug.Log("[BUILD] scenes ok");
            }
            catch (System.Exception e)
            {
                Debug.LogError("[BUILD] " + e);
                if (Application.isBatchMode) EditorApplication.Exit(1);
            }
        }

        private static void BuildGame()
        {
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var root = new GameObject("GameRoot");
            var view = root.AddComponent<Game.Presentation.BoardView>();
            var so = new SerializedObject(view);
            so.FindProperty("cellPrefab").objectReferenceValue =
                AssetDatabase.LoadAssetAtPath<GameObject>("Assets/_Game/Prefabs/Cell.prefab");
            so.ApplyModifiedPropertiesWithoutUndo();
            EditorSceneManager.SaveScene(scene, "Assets/_Game/Presentation/Scenes/Game.unity");
        }

        private static void BuildBoot() { /* similar */ }
    }
}
```

Guidelines:
- Idempotent: running twice yields the same output; delete and recreate rather than patch.
- Create prefabs first (`PrefabUtility.SaveAsPrefabAsset`), then scenes referencing them.
- Set private fields via `SerializedObject`/`SerializedProperty` (names must match field names, a rename needs updating here).
- Register scenes in Build Settings: `EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(path, true), ... }`.
- Keep a `Validate()` method that loads each scene and asserts required components exist; run it in CI.
- UI via code: build Canvas, CanvasScaler (reference resolution), EventSystem with the Input System UI module, TextMeshPro objects; prefer prefabs for repeated widgets.
- Never reference objects by name search at runtime; wire serialized references here.
- Keep the builder under ~400 lines per scene; split by scene.

## 4. BuildScript pattern

The template's `BuildScript` (`Assets/_Game/Editor/BuildScript.cs`) differs from the sample below in four ways, and you should keep the template's versions: the entry points are `BuildAndroid` and `BuildIOS`; the output comes from `-gsOut` (defaults `Builds/Android/game.aab` and `Builds/iOS`, and an Android output must end in `.aab`); signing and numbering come from `GS_ANDROID_KEYSTORE_PATH`, `GS_ANDROID_KEYSTORE_PASS`, `GS_ANDROID_KEY_ALIAS`, `GS_ANDROID_KEY_PASS` (defaults to the keystore password) and the optional `GS_BUILD_NUMBER` (Android version code and iOS build number), and without a keystore it warns and builds a debug-signed AAB that Play will reject; and the exit codes are 0 built, 1 failed, 2 usage error. It runs `SceneBuilder.Build()` itself when Build Settings has no enabled scene.

```csharp
#nullable enable
using System;
using System.IO;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEngine;

namespace Game.EditorTools
{
    public static class BuildScript
    {
        public static void Android() => Run(BuildTarget.Android, BuildTargetGroup.Android, "Builds/Android/game.aab");
        public static void IOS() => Run(BuildTarget.iOS, BuildTargetGroup.iOS, "Builds/iOS");

        private static void Run(BuildTarget target, BuildTargetGroup group, string output)
        {
            SceneBuilder.Build();
            var opts = new BuildPlayerOptions
            {
                scenes = Array.ConvertAll(EditorBuildSettings.scenes, s => s.path),
                locationPathName = output,
                target = target,
                options = BuildOptions.None,
            };
            if (target == BuildTarget.Android)
            {
                EditorUserBuildSettings.buildAppBundle = true;
                PlayerSettings.Android.useCustomKeystore = true;
                PlayerSettings.Android.keystoreName = Env("ANDROID_KEYSTORE_PATH");
                PlayerSettings.Android.keystorePass = Env("ANDROID_KEYSTORE_PASS");
                PlayerSettings.Android.keyaliasName = Env("ANDROID_KEY_ALIAS");
                PlayerSettings.Android.keyaliasPass = Env("ANDROID_KEY_PASS");
                PlayerSettings.Android.bundleVersionCode = int.Parse(Env("BUILD_NUMBER"));
            }
            PlayerSettings.bundleVersion = Env("VERSION_NAME");
            var report = BuildPipeline.BuildPlayer(opts);
            Debug.Log("[BUILD] result=" + report.summary.result + " size=" + report.summary.totalSize);
            EditorApplication.Exit(report.summary.result == BuildResult.Succeeded ? 0 : 1);
        }

        private static string Env(string k)
        {
            var v = Environment.GetEnvironmentVariable(k);
            if (string.IsNullOrEmpty(v)) throw new InvalidOperationException("missing env " + k);
            return v;
        }
    }
}
```

Rules:
- Secrets only from environment variables populated by CI secrets; never in the repo or in `ProjectSettings`. Reset custom keystore fields after the build if running locally.
- Run Addressables content build before `BuildPlayer` if used.
- Increment the build number from CI; version name from a tag.
- Output the `BuildReport` summary (size, warnings, steps) as JSON for evidence; check size against the budget.
- iOS: `BuildPlayer` produces an Xcode project; signing and archive happen in fastlane or `xcodebuild`.
- Development builds for profiling: `BuildOptions.Development | BuildOptions.ConnectWithProfiler | BuildOptions.AllowDebugging`.
- Run on a clean clone in CI to catch missing `.meta` or untracked assets.

## 5. Unity CLI (2026)

The notes report that Unity released a free official **Unity CLI** and deprecated the MCP server component of the in-editor AI assistant package, recommending the CLI instead. Reported capabilities:
- Install and manage Editor versions and projects.
- Run headless builds and test suites.
- Drive a running Editor directly with `unity command` and `unity eval`, described as faster and cheaper in tokens than MCP because no protocol layer sits between agent and editor (driving a running Editor needs Unity 6.0 LTS or later).
- Its own MCP server mode built on the Unity Pipeline package, with helper commands to configure a client (for example `unity mcp configure claude`) and to install agent skills (`unity skill install <agent>`).
- Does not require a Unity AI subscription.

Because command names, flags and capabilities were only partly verified in the notes (one page snippet advertised play mode, screenshots and live runtime control, but the fetched body listed builds and tests), do this on first use:
1. Run `unity --help` and each subcommand's `--help`; record the real syntax in the project's `AGENTS.md`/README.
2. Prefer the CLI for builds and tests in CI if it is installed; otherwise batchmode.
3. Use `unity eval` for small inspections (read a setting, list scenes) and `unity command` for named editor commands; wrap any recurring action as a static method callable by batchmode too.
4. Treat output as data; do not paste secrets into commands.

## 6. CoplayDev unity-mcp and other MCP servers

CoplayDev/unity-mcp ("MCP for Unity", MIT) was the most-starred Unity MCP server in the notes, with frequent releases. It exposes roughly fifty tool entry points: create scenes and GameObjects, edit C# scripts with Roslyn validation, manage assets, run tests, profile and build, with tool groups, multi-instance routing and an optional remote-hosted mode. It is not affiliated with Unity and its README promotes commercial products. Other community servers exist (for example IvanMurzak Unity-MCP and CoderGamester mcp-unity, the latter reportedly offering play-mode control with single-frame stepping). Verify maturity at adoption time.

Usage rules:
1. Install the Unity package from the server's documented source, start the bridge in the editor, and register the server in the agent's MCP configuration.
2. Use it for: inspecting hierarchy, reading console errors after a compile, entering play mode and stepping, taking a screenshot, running tests.
3. Do not let it become the only record: if the agent adds a GameObject through MCP, also encode it in SceneBuilder, or the next rebuild loses it.
4. Security: the bridge listens locally and can execute editor code. Run only on trusted projects; keep it updated; disable when not needed; never expose it to the network without authentication.
5. Version coupling: pin the package version in `manifest.json`.
6. Token budget: prefer text queries (hierarchy, component JSON, console) over screenshots.

## 7. CI and licence activation

Unity licensing in CI differs by licence type; options (verify current procedure on Unity docs):
- Personal: GameCI's activation flow uses a manual activation file exchanged for a licence file stored as a CI secret; the process has changed over time.
- Pro/Enterprise: serial number with `-serial -username -password`, or a license server.
- Always return the licence at the end (`-returnlicense`) for serial-based activation.

GameCI (open source GitHub Actions: `game-ci/unity-builder`, `unity-test-runner`, `unity-activate`) runs Unity in Docker images matching the editor version and handles caching, licence activation and build outputs. A workflow outline:

1. Checkout with LFS if used.
2. Cache `Library/`.
3. `unity-test-runner` for EditMode and PlayMode, upload NUnit XML.
4. `unity-builder` with `targetPlatform: Android` and custom `buildMethod: Game.EditorTools.BuildScript.BuildAndroid` (the template's method name; pass `-gsOut Builds/Android/game.aab` through `customParameters`), with `GS_ANDROID_KEYSTORE_PATH`, `GS_ANDROID_KEYSTORE_PASS`, `GS_ANDROID_KEY_ALIAS`, `GS_ANDROID_KEY_PASS` and `GS_BUILD_NUMBER` from secrets and the CI run number.
5. iOS: build the Xcode project on a Linux runner via the builder, then archive and sign on a macOS runner (fastlane). Templates in `templates/ci/`.
6. Upload artifacts and the build report JSON.

Pitfalls: editor version mismatch between Docker image and project (`ProjectSettings/ProjectVersion.txt`), missing Android modules, cache poisoning after package changes, licence expiry, long first import time (set a generous timeout).

## 8. Services overview

Unity ships first-party packages for several services and many networks provide Unity SDKs; Unity is generally the easiest engine for the ad and analytics SDK ecosystem. Every SDK must sit behind an interface in Presentation (or a Services assembly) with a mock implementation so tests and editor runs never call the network.

| Capability | Options |
|---|---|
| IAP | Unity IAP package (`com.unity.purchasing`), RevenueCat Purchases Unity SDK, native store plugins |
| Ads and mediation | Unity LevelPlay (ironSource), AppLovin MAX, Google AdMob (with mediation), Unity Ads |
| Analytics | Unity Analytics, Firebase Analytics, GameAnalytics, custom HTTP |
| Crash reporting | Firebase Crashlytics, Unity Cloud Diagnostics, Sentry |
| Remote config / A-B | Unity Remote Config and Game Overrides, Firebase Remote Config |
| Attribution | AppsFlyer, Adjust, Singular, Branch (SDKs; check privacy impact) |
| Push / local notifications | Mobile Notifications package (`com.unity.mobile.notifications`), Firebase Cloud Messaging |
| Auth, cloud save | Unity Authentication and Cloud Save, Play Games Services, Game Center, Firebase Auth |
| Performance scaling | Adaptive Performance (Samsung provider and others) |

## 9. IAP

- Use the current Unity IAP package API (the package's API has been reorganized across major versions; read the package docs for your version instead of copying old snippets).
- Products: define SKUs in the stores and in a catalog; map store SKUs to game rewards in a ScriptableObject or JSON tied to the economy design (`monetization`, `economy-design`).
- Flow: initialize, fetch product metadata (localized price), purchase, validate receipt, grant, confirm purchase to the store, persist. Handle pending, deferred and restored purchases; grant idempotently using the transaction id.
- Server-side receipt validation is strongly recommended for any meaningful currency; at minimum local validation with the store key.
- Restore purchases button is required on iOS for non-consumables and subscriptions.
- Test: Google Play license testers and internal testing track; Apple sandbox accounts and StoreKit configuration files. Do not test with real money.
- Edge cases to test: app killed mid-purchase, no network after purchase, refund/revocation, family sharing, price change.

## 10. Ads and mediation

- Pick one mediation layer (LevelPlay or MAX) rather than integrating several; add networks as adapters.
- Formats: rewarded (opt-in, best player experience), interstitial (between natural breaks, with frequency caps and no ads in the first session unless justified), banner (low yield, steady), app open. Ethics and policy: no ads on top of fail/retry dark patterns, child-directed handling (`legal-ethics`).
- Consent: Google UMP/consent management for EU/UK, Apple App Tracking Transparency prompt before using the advertising identifier on iOS; pass consent flags to the SDK before initialization.
- Test mode: use the SDK's test devices and test ad units; never click your own live ads.
- Integration steps: add the SDK package, set app keys through config (not hard-coded in the repo), initialize on a background-safe path after consent, preload ads, show with callbacks for completion, rewards granted only on the reward callback.
- Pitfalls: Android manifest merge conflicts between SDKs, Gradle dependency version clashes (use the External Dependency Manager or the mediation tool's resolver), iOS CocoaPods resolution, adapter version mismatches, 16 KB page-size incompatibility in old native libraries, large size increase.
- Measure: ad impressions per DAU, rewarded opt-in rate, ad-attributed retention impact (`liveops`, `player-analytics`).

## 11. Analytics, crash and remote config

- Define the event taxonomy first (`event_taxonomy.py` in the plugin scripts); implement a single `IAnalytics` interface with a Firebase or Unity implementation and a debug implementation.
- Firebase for Unity: import the SDK packages (`FirebaseAnalytics`, `FirebaseCrashlytics`, `FirebaseRemoteConfig`) and add the config files (`google-services.json`, `GoogleService-Info.plist`) which are per-environment and treated as non-secret but project-specific; keep them out of public repos where the project is sensitive. External Dependency Manager resolves native deps.
- Crashlytics needs symbol upload on iOS and mapping/symbol upload on Android IL2CPP builds; automate in CI; verify with a test crash.
- Remote config: define defaults in code, fetch and activate at a safe point (not mid-run), keep keys few and typed, never put secrets in remote config.
- Send events batched; avoid per-frame events; respect consent.

## 12. RevenueCat and entitlements

RevenueCat provides a cross-platform subscription and purchase backend with a Unity SDK. Use it when you have subscriptions or want a managed receipt validation and entitlement service without running servers. Steps: create the project and entitlements in the dashboard, add the SDK, configure with public API keys per platform (public SDK keys are not secrets but still come from config), fetch offerings, purchase, listen for customer info updates, check entitlements to unlock features. Costs and terms are volatile; verify on their pricing page.

## 13. Notifications

- Local notifications: Mobile Notifications package; schedule with channels (Android) and request permission (iOS and Android 13+ runtime permission).
- Ask for permission at a moment of value, not on first launch; explain what you will send.
- Content rules: useful and infrequent; no guilt or deceptive copy; allow opt out in settings; respect quiet hours.
- Remote push: Firebase Cloud Messaging plus APNs key; handle token refresh.
- Test with a device build; notifications do not fire reliably in the editor.

## 14. Adaptive Performance

Adaptive Performance (a Unity package with device-vendor providers, notably on Samsung devices) reports thermal and performance state and offers scalers that adjust quality (resolution, LOD, shadows, frame rate) before the OS throttles. Use it as an additional signal, not a replacement for tiered quality settings:
1. Install the package and a provider; check provider support for target devices.
2. Read `Thermal` warning level and `PerformanceLevels`; lower targets proactively (render scale, particle counts).
3. Provide your own scalers for game-specific load.
4. Log thermal events in analytics to learn which devices overheat.
Support varies by device; always have a fallback quality heuristic.

## 15. SDK integration checklist

- [ ] Interface plus mock exists; tests run without the SDK.
- [ ] SDK version pinned; changelog read; Unity and Gradle/Xcode compatibility confirmed.
- [ ] Android manifest and iOS Info.plist entries and usage strings reviewed; unnecessary permissions removed.
- [ ] 16 KB page-size and iOS privacy manifest compatibility confirmed for the SDK.
- [ ] Consent and age gating wired before init.
- [ ] Keys/IDs come from config or CI secrets; none committed.
- [ ] Build size delta recorded.
- [ ] Device test on both platforms; failure paths tested (offline, SDK init failure).
- [ ] Listed in the dependency inventory for compliance review (`legal-ethics`, `store-release`).

## 16. Volatile facts (as of Oct 2026 - verify)

| Fact | Source |
|---|---|
| Unity AI entered open beta in May 2026 with an in-editor assistant, AI Gateway and an in-editor MCP server | https://app.cinevva.com/news/2026-05-04-unity-ai-open-beta |
| Official MCP tool categories (scene, scripts, console, components, build settings inspection) and requirements (Unity 6, AI Assistant package, Cloud-linked project, subscription or trial) | https://unity.com/blog/unity-ai-mcp-how-to-get-started |
| Reported pricing and connection limits for Unity AI MCP are user-reported and contested | https://discussions.unity.com/t/mcp-versus-built-in-assistant/1719106 |
| The in-editor MCP server component (`com.unity.ai.assistant`) is deprecated in favor of the free Unity CLI | https://docs.unity.com/en-us/unity-cli/replace-mcp-server-unity-cli |
| CoplayDev/unity-mcp: about 15k GitHub stars, MIT, about 50 tool entry points, monthly releases | https://github.com/CoplayDev/unity-mcp |
| Other Unity MCP servers (IvanMurzak, CoderGamester) | https://github.com/IvanMurzak/Unity-MCP and https://github.com/CoderGamester/mcp-unity |
| Batchmode and command-line arguments | https://docs.unity3d.com/Manual/EditorCommandLineArguments.html |
| Unity first-party packages cover major ad mediation and analytics while Godot relies on community plugins | https://oceanviewgames.co.uk/blog/posts/unity-vs-godot-vs-unreal-mobile-games |
| Licence activation flow for CI, IAP package API shape, LevelPlay/MAX/Firebase versions, RevenueCat pricing | not in the notes; check GameCI docs (https://game.ci), the packages' own documentation and vendor pricing pages |
