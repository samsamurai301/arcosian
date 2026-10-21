# Godot Mobile Export, Platform Settings and Plugins

Summary: project settings that matter on phones (renderer, stretch, touch, safe area), the complete path from a green headless gate to a signed Android AAB and an iOS archive, the headless CLI commands that automate it, and the plugin landscape for billing, StoreKit 2, ad mediation, Firebase and haptics. Plugin and store-rule details change fast; they are collected under a volatile-facts heading with sources and must be verified at release time.

## Contents
1. Renderer selection
2. Display, stretch and orientation
3. Touch and input on devices
4. Safe area and notches
5. Import and compression settings
6. Android export step by step
7. iOS export and signing
8. Headless CLI reference
9. Plugin options by capability
10. Haptics and lifecycle
11. Export checklist
12. Volatile facts (as of Oct 2026 - verify)

## 1. Renderer selection

Godot 4 has three rendering methods: Forward+, Mobile and Compatibility. Set under Project Settings > Rendering > Renderer (`rendering/renderer/rendering_method` and the `.mobile` override).

| Renderer | Backend | Use for | Watch out |
|---|---|---|---|
| Compatibility | OpenGL ES 3 / WebGL2 | 2D games, widest Android coverage, older devices, web export | fewer 3D features; shader differences from other renderers |
| Mobile | Vulkan (Android), Metal (iOS) | 3D and richer 2D on mid/high devices | Vulkan driver quirks on some Android GPUs; test broadly |
| Forward+ | Vulkan/Metal desktop-class | Desktop-class visuals | Heavy for phones; avoid as the mobile default |

Decision: start with Compatibility for 2D or hyper-casual; choose Mobile when you need 3D lighting, post effects or many shader features. Do not choose by benchmark articles; build a stress scene of your real content and test on three Android tiers (low, mid, high) and one older iPhone. Switching later changes materials and shaders, so decide before art production.

Per-platform override: `rendering/renderer/rendering_method.mobile` lets desktop dev use a different renderer than phones. Keep dev and device renderer identical for visual QA unless you have a reason.

## 2. Display, stretch and orientation

Recommended starting values (portrait):

| Setting | Value | Why |
|---|---|---|
| `display/window/size/viewport_width` x `height` | 1080 x 1920 | common portrait base |
| `display/window/stretch/mode` | `canvas_items` | UI scales crisply; for pixel art use `viewport` with integer scale |
| `display/window/stretch/aspect` | `expand` | fills tall phones; anchor UI to edges |
| `display/window/handheld/orientation` | portrait (or landscape) | lock explicitly |
| `display/window/vsync/vsync_mode` | enabled | battery and tear-free |
| `application/run/max_fps` | 60 (or 0 plus dynamic) | cap for heat; raise for action games |

Design for the extremes: 16:9 (1080x1920) up to ~20:9 (taller) and tablets (4:3). With `expand`, extra space appears vertically on tall phones; anchor HUD to top and bottom, keep the play area in a container that scales with `aspect_ratio` handling (`AspectRatioContainer`, `SubViewportContainer`, or a computed scale).

Pixel-art games: stretch mode `viewport`, scale mode `integer`, base size small (for example 360x640), texture filter `nearest`.

## 3. Touch and input on devices

- Touch events are `InputEventScreenTouch` and `InputEventScreenDrag`. Enable `input_devices/pointing/emulate_mouse_from_touch` (default on) so Controls work with touch; disable it if you handle both and double-handle events.
- `Control` nodes receive taps via `gui_input`; set `mouse_filter` correctly (STOP, PASS, IGNORE) so overlays do not eat input.
- Minimum touch target: 48 dp, about 130 canvas px on a 1080-wide base. Spacing between adjacent targets at least 8 dp.
- Thumb zones: place primary actions in the bottom third; keep destructive actions away from frequent-tap areas.
- Virtual keyboard: `DisplayServer.virtual_keyboard_show(text)` and `virtual_keyboard_get_height()` to lift UI when typing.
- Back button (Android): handled as `ui_cancel`/`NOTIFICATION_WM_GO_BACK_REQUEST`; define behavior for every screen (back closes popup, then goes up one screen, then asks to quit). Set `application/config/quit_on_go_back` false when you handle it.
- Test with a real finger; mouse emulation hides problems with fat-finger accuracy and multi-touch.

## 4. Safe area and notches

`DisplayServer.get_display_safe_area()` returns a `Rect2i` in screen pixels excluding cutouts and gesture areas on supported platforms. Convert to canvas coordinates:

```gdscript
static func insets(window: Window) -> Dictionary:
	var safe: Rect2i = DisplayServer.get_display_safe_area()
	var screen: Vector2i = DisplayServer.screen_get_size()
	if screen.x <= 0 or screen.y <= 0:
		return {"left": 0, "top": 0, "right": 0, "bottom": 0}
	var scale_x: float = float(window.content_scale_size.x) / float(screen.x)
	var scale_y: float = float(window.content_scale_size.y) / float(screen.y)
	return {
		"left": int(safe.position.x * scale_x),
		"top": int(safe.position.y * scale_y),
		"right": int((screen.x - safe.end.x) * scale_x),
		"bottom": int((screen.y - safe.end.y) * scale_y),
	}
```

This is a sketch: with `expand` stretch the content scale and the actual viewport can differ; use the template's `SafeArea` service as the reference and test with a `debug_insets` override on desktop. Apply insets to a root `MarginContainer` for UI; let backgrounds extend under the notch. Re-query on `size_changed` and on rotation.

## 5. Import and compression settings

- Project Settings > Rendering > Textures > VRAM Compression: enable ETC2/ASTC import for mobile. ASTC gives better quality per byte on modern hardware; ETC2 is the broad Android baseline. S3TC/BPTC are desktop.
- Per-texture: UI and pixel art often use lossless to avoid artifacts; 3D textures use VRAM compressed with mipmaps.
- Atlas sprites: use `AtlasTexture` or sprite sheets to reduce draw calls. In 2D, Godot batches draw calls for items sharing a texture and material in order; interleaving materials breaks batches.
- Fonts: use dynamic fonts with MSDF only when you need scaling; bake or subset large CJK fonts.
- Audio: Ogg Vorbis for music (streamed), WAV for short effects (decoded in memory), set loop points in import settings.
- Keep a texture size budget table in the technical-art docs (`technical-art`).

## 6. Android export step by step

Prerequisites: JDK (version matching your Godot's docs), Android SDK command-line tools and platform tools, export templates installed for the exact engine version, Android build template installed into the project (Project > Install Android Build Template, or `--install-android-build-template` on the command line together with `--export-release`) when using gradle builds.

Verified toolchain for Godot 4.7.2 (read from the 4.7.2 build template's `config.gradle` and used for a real signed AAB export on 2026-10-21): JDK 17, compileSdk/targetSdk 36, minSdk 24, build-tools 36.1.0, NDK 29.0.14206865, Gradle 8.11.1 (wrapper), Kotlin 2.1.21. Install with `sdkmanager "platform-tools" "platforms;android-36" "build-tools;36.1.0" "ndk;29.0.14206865"`. The result passed Play's 16 KB page check (LOAD segments aligned 0x4000; `zipalign -c -P 16` OK on a universal APK). Other engine versions pin other numbers: read `android/build/config.gradle` after installing the template.

1. Editor settings (Editor Settings > Export > Android): set SDK path, JDK path, debug keystore. Headless CI can set these through a generated `editor_settings-4.tres` or environment variables the docs describe; verify names for your version.
2. Preset in `export_presets.cfg`: name `Android`; `gradle_build/use_gradle_build=true`; `gradle_build/export_format` AAB for Play; architectures `arm64-v8a` (add `armeabi-v7a` only if you must support 32-bit devices; Play requires 64-bit support for new apps).
3. Package: `package/unique_name` reverse-DNS (`com.studio.game`), `version/code` integer that increases every upload, `version/name` display string.
4. SDK levels: `gradle_build/min_sdk` (template default 24), `gradle_build/target_sdk` set to the level Google Play currently requires (volatile; see section 12).
5. Release keystore: generate with `keytool`, store outside the repo. Provide via environment variables:
   `GODOT_ANDROID_KEYSTORE_RELEASE_PATH`, `GODOT_ANDROID_KEYSTORE_RELEASE_USER`, `GODOT_ANDROID_KEYSTORE_RELEASE_PASSWORD`. Never commit a keystore or password; back up the upload key securely. Use Play App Signing so Google holds the app signing key.
6. Permissions: tick only what you use (INTERNET for ads/analytics, VIBRATE for haptics). Each permission is a store and privacy disclosure.
7. Export: `godot --headless --path <project> --export-release "Android" /abs/out/game.aab`. Debug APK for device tests: `--export-debug "Android" out.apk`, then `adb install -r out.apk`.
8. Verify the artifact: size, `bundletool` or `aapt2 dump badging` for package, version and target SDK; install on a device and launch.
9. 16 KB memory page size: Google Play requires apps targeting recent Android versions to support devices with 16 KB pages, which affects native libraries (`.so`) alignment. The engine's own libraries come from the export template; third-party native plugins must also be rebuilt compatible. Check each plugin's release notes and test with an emulator image or device using 16 KB pages. Treat as a release blocker for the date Play enforces it (volatile).
10. Symbols: Godot can package native debug symbols for the Play Console to symbolicate native crashes (feature added in a recent 4.x release; verify the preset option).
11. Upload to Play Console internal testing first; check pre-launch report.

Common failures:
| Symptom | Likely cause | Fix |
|---|---|---|
| "Could not find Android SDK" | editor setting missing in headless | set path in editor settings file / env |
| Gradle build fails on first export | missing build template or JDK mismatch | install template, match JDK |
| App installs but crashes at start on some GPUs | Vulkan driver issue on Mobile/Forward+ | test on Compatibility; report with device model |
| Play rejects upload: version code used | not incremented | bump `version/code` |
| Play rejects: target API too low | outdated target SDK | raise, test behavior changes |
| Huge AAB | unstripped templates, uncompressed textures, unused architectures | custom template build with disabled modules, ASTC, one ABI per split |

## 7. iOS export and signing

iOS export requires macOS with Xcode and an Apple Developer account.

1. Preset `iOS`: `application/bundle_identifier` (matches App Store Connect), `application/app_store_team_id`, `application/short_version` and `application/version` (build number must increase per upload).
2. Capabilities: only enable what you use (in-app purchase, push, Game Center); `Info.plist` usage strings (`application/*_usage_description` options) must be present for any permission API, or App Review rejects.
3. Icons and launch screen: provide a 1024 px marketing icon; use the project's launch storyboard settings.
4. Export an Xcode project: `godot --headless --path <project> --export-release "iOS" /abs/out/game.xcodeproj` (the extension and layout depend on the version; follow the docs for your build).
5. Open in Xcode (or script with `xcodebuild`), set automatic signing with your team, archive, upload to TestFlight. In CI use fastlane (`match` for certificates, `gym`, `pilot`); see `templates/ci/`.
6. Minimum device support: Metal exports default to A12-or-newer devices in recent versions (volatile); decide whether older devices matter.
7. Privacy manifest and required-reason APIs: Apple requires a privacy manifest for apps and listed SDKs; include manifests from every plugin you add (volatile).
8. Test on at least one physical iPhone; the simulator does not reproduce Metal performance or haptics.
9. C# exports for iOS and Android are still described as experimental; prefer GDScript for mobile unless you have verified your case.

## 8. Headless CLI reference

`godot` is your Godot 4 binary; on macOS it is inside the app bundle (`Godot.app/Contents/MacOS/Godot`). Every flag below was checked against `godot --help` on 4.7.2, and the ones marked "run" were also executed there.

| Task | Command | Availability and behaviour (4.7.2) |
|---|---|---|
| Import assets, build caches | `godot --headless --path <project> --import` | Editor binary only. Starts the editor, waits for imports, quits; exit 0 (run) |
| Run a script | `godot --headless --path <project> -s res://tools/x.gd -- --arg=value` | `-s` or `--script`; editor binary or export templates built with `disable_path_overrides=false`. A `SceneTree` script's `quit(code)` becomes the exit code (run: 3) |
| Parse-check a script | `godot --headless --path <project> --check-only -s res://x.gd` | "Only parse for errors and quit (use with --script)". Prints `SCRIPT ERROR: Parse Error` lines but exits 0 even with errors (run) |
| Run a scene | `godot --headless --path <project> --scene res://scenes/x.tscn` | `--scene` takes a path or UID; a positional `res://scenes/x.tscn` also worked (run); `get_tree().quit(code)` becomes the exit code (run: 7) |
| Export release | `godot --headless --path <project> --export-release "<preset>" <out>` | Editor binary only; preset name must match `export_presets.cfg`; `<out>` includes the file name and its directory must exist. Missing templates or SDKs print the config errors and exit 1; an unknown preset lists the detected presets and exits 1 (run) |
| Export debug | `godot --headless --path <project> --export-debug "<preset>" <out>` | Same rules |
| Export PCK or ZIP only | `--export-pack "<preset>" out.pck` | The extension picks PCK or ZIP; `--export-patch` with `--patches` exports changed files only |
| Quit after N frames | `--quit-after <frames>` | Counts main-loop iterations; 0 disables; `--quit` is N = 1 (run) |
| Fixed frame rate | `--fixed-fps <n>` | Disables real-time synchronization (deterministic stepping) |
| Movie capture | `--write-movie out.avi` | Needs a renderer: windowed run produced an MJPEG AVI, `.png` produces numbered PNGs plus a `.wav`, and `--headless` crashed (run; see the testing cheat sheet) |
| Resolution | `--resolution 540x960` | `<W>x<H>` window size request |
| Headless | `--headless` | Same as `--display-driver headless --audio-driver Dummy` |
| Verbose, debugger | `--verbose`, `--debug` | `-v` and `-d` short forms |

User arguments go after `--` (or `++`) and are read with `OS.get_cmdline_user_args()`. Exit codes come from `get_tree().quit(code)` in your script. Under `--headless` the display server is a dummy: no rendering, no real input, no screenshots. The editor prints `cannot connect to daemon at tcp:5037` during `--import` and exports when no `adb` server is running; it is harmless.

CI notes: cache export templates (per engine version), cache `.godot/` only if you accept stale-cache risks, pin the exact engine version, and always run `--import` before the first script on a fresh checkout.

## 9. Plugin options by capability

| Capability | Options | Notes |
|---|---|---|
| Android billing | Godot Foundation-maintained Google Play Billing plugin; community alternatives | Prefer the maintained one; verify min versions |
| iOS purchases (StoreKit 2) | Foundation-maintained StoreKit 2 plugin; cross-platform wrappers (for example godot-iap based on the OpenIAP protocol) | Server-side receipt validation recommended |
| Subscriptions / entitlements | RevenueCat SDK integration if a Godot plugin exists for your version, else a thin server | verify maturity |
| Ad mediation | AppLovin MAX official Godot plugin; AdMob via community plugins | Test on both platforms; consent flow (UMP, ATT) is yours to implement |
| Analytics / crash | Firebase via community plugins or native wrappers; or HTTP endpoints you control | Keep behind `Analytics` interface |
| Game services | Foundation-maintained Google Play Games Services plugin; Game Center plugin | optional |
| Push notifications | Firebase Cloud Messaging plugins, APNs via native plugin | requires permission UX |
| Haptics | `Input.vibrate_handheld`; plugins for richer patterns | wrap in `Haptics` |
| Native share, rate prompt, review | community plugins | prompt rarely |

Selection procedure:
1. Define the interface in `services/` (`Ads`, `Iap`) with a mock backend first.
2. Check the plugin's supported Godot version, last release date, open issues, and licence.
3. Check 16 KB page-size and target-SDK compatibility on Android and privacy manifest on iOS.
4. Integrate behind the interface; add an integration smoke test on a device build.
5. Pin the plugin version in `addons/` notes; record in the dependency list for compliance (`legal-ethics`).
6. If no maintained plugin exists, weigh writing a thin native plugin (Android AAR / iOS static library through Godot's plugin system) against a different engine.

Plugin ecosystem risk: Unity ships first-party packages for much of this; Godot relies on a mix of Foundation-maintained and community plugins. Budget time for plugin integration and device testing; it is a common schedule risk.

## 10. Haptics and lifecycle

- `Input.vibrate_handheld(duration_ms, amplitude)` (amplitude parameter in 4.x; verify availability on your version) is the built-in call. On iOS, richer patterns need a plugin.
- Gate haptics behind a user setting and respect the OS reduce-motion style preferences where you can detect them.
- Lifecycle notifications: `NOTIFICATION_APPLICATION_PAUSED`, `NOTIFICATION_APPLICATION_RESUMED`, `NOTIFICATION_APPLICATION_FOCUS_OUT/IN`, `NOTIFICATION_WM_CLOSE_REQUEST`. Handle them in one autoload and emit bus signals. On pause: save, pause audio, stop timers that should not run, and log a session event.
- Interruptions (calls, notifications): treat as pause; on resume, do not assume state is unchanged (network, time zone, clock).
- Offline time: if you use timers that span sessions, use server time or clamp with anti-cheat awareness.

## 11. Export checklist

- [ ] Static, unit, playthrough gates green on the exact commit.
- [ ] Engine and export template versions pinned and equal.
- [ ] Bundle identifiers, version code/number incremented.
- [ ] Release keystore/certificates only in environment or CI secrets.
- [ ] Permissions and usage strings match what the app does.
- [ ] Target SDK and Xcode/SDK requirements verified against current store rules.
- [ ] 16 KB page-size verified for every native library.
- [ ] Privacy manifest and data-safety forms updated for each SDK.
- [ ] Installed and played on at least one low-end Android and one older iPhone.
- [ ] Artifact size within the budget in the design contract.
- [ ] Debug symbols uploaded; crash reporting verified with a test crash.
- [ ] Build recorded as evidence (path, hash, commit) for `release-manager`.

## 12. Volatile facts (as of Oct 2026 - verify)

| Fact | Source |
|---|---|
| Godot 4.7.2 was the latest stable in the notes snapshot; 4.7 added a per-platform export template downloader and a stable Gradle-based Android build environment | https://github.com/godotengine/godot/releases and https://godotengine.org/releases/4.7/ |
| The Godot Foundation maintains plugins for Google Play Billing, Play Games Services and StoreKit 2; others live in the godot-sdk-integrations organization | https://godotengine.org/article/godot-mobile-update-apr-2026/ |
| Godot 4.6 added Android instrumented tests on physical devices through Firebase Test Lab; 4.5 added native Android debug symbols for Play Console | https://godotengine.org/article/godot-mobile-update-apr-2026/ |
| An AppLovin MAX Godot plugin exists (Android and iOS), published by AppLovin; the Asset Library listing was old | https://developers.applovin.com/en/max/godot/overview/integration |
| godot-iap is an OpenIAP-based cross-platform IAP plugin | https://medium.com/dooboolab/building-in-app-purchases-for-godot-engine-the-openiap-journey-112c98c765fd |
| AdMob support relies on third-party plugins | https://thunderplugins.itch.io/admob-for-godot-4 |
| C# on Godot mobile is documented as experimental for Android and iOS; iOS exports need macOS | https://docs.godotengine.org/en/4.7/tutorials/scripting/c_sharp/index.html |
| iOS Metal exports default to A12 or newer devices (backported to 4.5.2) | https://godotengine.org/article/maintenance-release-godot-4-5-2/ |
| Godot CLI flags and export commands | https://docs.godotengine.org/en/stable/tutorials/editor/command_line_tutorial.html |
| Google Play target SDK and 16 KB page-size deadlines, Apple privacy manifest requirements | not in the research notes; check Play Console policy pages and Apple developer documentation at release time |

Unverified in the notes: exact preset option names for your engine version, current Play deadlines, and plugin version compatibility. Open the plugin READMEs and the Godot docs for your pinned version before relying on any of them.
