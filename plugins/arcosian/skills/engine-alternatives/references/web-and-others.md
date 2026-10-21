# Web Stacks, Hybrid Wrappers and Other Engines

Summary: how to build mobile games with web technology (Phaser 4, PixiJS 8, three.js, Babylon.js, PlayCanvas), how to ship them as store apps with Capacitor, what WebGPU on iOS 26+ changes, how to make playable ads, and short profiles of Bevy and other options (GameMaker, Construct, GDevelop, Solar2D, Flame, native). The web route has the fastest agent loop (code in TypeScript, verify in a headless browser) and the hardest performance ceiling (WebView). Versions and browser support are volatile and listed with sources at the end.

## Contents
1. When the web route fits
2. Stack choice
3. Project skeleton and tooling
4. Rendering and performance on mobile web
5. Audio, input and lifecycle quirks
6. Verification loop for agents
7. Capacitor: shipping as a store app
8. PWA and web portals
9. WebGPU status
10. Playable ads
11. Bevy
12. Other engines
13. Checklists
14. Volatile facts (as of Oct 2026 - verify)

## 1. When the web route fits

Good fit: 2D casual, puzzle, card, word, idle, quick prototypes, playable ads, portals and social platforms, teams strong in TypeScript, projects that need instant updates.
Poor fit: heavy 3D at high frame rates on low-end phones, large asset sets (memory-bound WebView), deep native integration (frequent background work, complex ad mediation stacks) unless plugins exist.
Distribution options: browser or PWA (no store fees, discoverability depends on you), portals, Capacitor app in the stores (store policies still apply, and apps must provide more than a repackaged site; verify current guidelines).

## 2. Stack choice

| Stack | Type | Good for | Notes |
|---|---|---|---|
| Phaser 4 | 2D game framework | full 2D games with scenes, physics, input, tweens | WebGL2 renderer; large community; new GPU sprite layer for huge sprite counts with flexibility tradeoffs |
| PixiJS 8 | 2D renderer | custom games, UI-heavy apps, playables | WebGL default, WebGPU supported; you build structure yourself |
| three.js | 3D library | stylized 3D, product-like scenes | WebGPU path with WebGL2 fallback; you assemble the game framework |
| Babylon.js | 3D engine | fuller 3D engine features, tooling, physics | Apache-2.0; heavier bundle |
| PlayCanvas | engine plus cloud editor | team workflows, mobile web 3D, ads | editor is web-based; the engine is open source |
| Others | Kaplay, Excalibur, melonJS, Cocos web | small 2D games | verify maintenance |

Selection rules:
1. 2D and want batteries included: Phaser. 2D and want control or smallest bundle: PixiJS.
2. 3D: three.js if you can build the game layer yourself; Babylon.js or PlayCanvas for more built-in engine features.
3. Prefer one renderer and one physics approach; do not mix several large libraries.
4. Keep rules in a pure TypeScript sim-core with no DOM or renderer imports; it tests in Node in milliseconds and ports to other engines.

## 3. Project skeleton and tooling

```
package.json  tsconfig.json  vite.config.ts  capacitor.config.ts
src/
  core/        pure TS: rng, state, sim, save schema, tuning (no DOM, no PIXI/Phaser imports)
  view/        renderer scenes, sprites, tweens, input adapters
  services/    ads, iap, analytics, storage (interfaces + mocks)
  main.ts
tests/         vitest unit tests; playthroughs/*.json
public/        assets (atlases, audio)
```

- Build tool: Vite for dev server and bundling; TypeScript strict mode; ESLint; Vitest for unit tests.
- Pin dependencies exactly; commit the lockfile.
- Asset pipeline: texture atlases (TexturePacker or open-source packers), compressed textures (KTX2/Basis) for 3D, audio as Ogg plus AAC/MP3 fallback for iOS (verify codec support), fonts subset.
- Seeded RNG in core; no `Math.random()` in rules.
- Save with `localStorage` for small data or IndexedDB for larger; in Capacitor use the Preferences/Filesystem plugins, since WebView storage can be cleared by the OS.

## 4. Rendering and performance on mobile web

| Limit | Symptom | Action |
|---|---|---|
| WebView memory | tab or app killed, black textures | smaller atlases (max ~2048 px on low-end, 4096 on newer), unload scenes, avoid huge decoded images |
| GPU fill/overdraw | frame drops with layered alpha | reduce overlapping transparent sprites, lower resolution scale (`devicePixelRatio` cap at 2) |
| Draw calls | CPU bound | batch sprites in atlases; PixiJS and Phaser batch by texture |
| JS garbage | periodic hitches | pool objects, avoid allocations in the frame loop, reuse arrays and vectors |
| Main thread blocking | input lag | chunk heavy work, use Web Workers for generation and solvers |
| Layout/DOM cost | slow UI | draw UI in canvas or keep DOM overlays small; avoid layout thrash |
| Battery/heat | warm device | cap to 30 or 60 FPS via `requestAnimationFrame` throttling, pause when hidden |

Rules of thumb:
- Cap `devicePixelRatio` (for example `Math.min(window.devicePixelRatio, 2)`); rendering at 3x is rarely worth it.
- Use `visibilitychange` to pause the loop and audio.
- Test in the real target WebView (WKWebView on iOS, Chrome-based WebView on Android), not only desktop Chrome.
- Measure with the browser's performance tools remotely (Safari Web Inspector for iOS devices, Chrome remote debugging for Android) and with an on-screen FPS and memory overlay during QA.

## 5. Audio, input and lifecycle quirks

- Audio unlock: browsers require a user gesture before audio plays; create or resume the `AudioContext` on the first touch. iOS has additional silent-switch and interruption behaviors.
- Touch: use Pointer Events; set `touch-action: none` on the canvas to stop scrolling and zoom gestures; prevent double-tap zoom with viewport meta settings.
- Viewport: `<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">`; use CSS `env(safe-area-inset-*)` for notches.
- Fullscreen and orientation: limited in browsers; in Capacitor lock orientation through native config or plugin.
- Lifecycle: the OS may suspend or kill the WebView in the background; save on `visibilitychange` and `pagehide`, not on `beforeunload`.
- Haptics: `navigator.vibrate` is not available on iOS Safari; use a Capacitor haptics plugin in the wrapper.
- Time: do not trust wall-clock for anti-cheat; use `performance.now()` for frame timing; handle large deltas after resume by clamping.

## 6. Verification loop for agents

1. Unit and playthrough tests run in Node with Vitest against `core/` (same JSON playthrough format as the Godot template: seed, steps, expectations).
2. Browser run: start Vite, drive with Playwright or headless Chromium; take screenshots at phone viewports (for example 390x844 with touch emulation and device scale factor 3), read console errors, fail on uncaught exceptions.
3. Expose a debug hook (`window.__game.getState()`) in dev builds so tests read JSON state instead of parsing pixels.
4. Visual review by the critic from screenshots across two aspect ratios.
5. Device checks: Android via USB debugging and Chrome remote inspector; iOS via Safari Web Inspector on macOS.
6. Performance: record a trace over a 60 second session, extract frame times and memory; compare with the perf budget.
Hardware WebGL2 matters for realistic 3D captures (one generator in the notes captures three.js and Babylon.js games in Chrome with hardware WebGL2); software rendering can mislead performance conclusions.

## 7. Capacitor: shipping as a store app

Capacitor wraps a web app in a native shell with plugin access.

1. `npm i @capacitor/core @capacitor/cli`; `npx cap init <name> <bundle.id> --web-dir=dist`.
2. Add platforms: `npm i @capacitor/android @capacitor/ios`; `npx cap add android`; `npx cap add ios`.
3. Build and sync: `npm run build && npx cap sync`.
4. Open native projects: `npx cap open android` (Android Studio) or `npx cap open ios` (Xcode, macOS only). CI can run `./gradlew bundleRelease` and `xcodebuild archive` or fastlane (see `templates/ci/`).
5. Plugins: official ones for haptics, preferences, status bar, splash screen, app lifecycle, filesystem, push notifications; community plugins for AdMob, in-app purchases (for example RevenueCat Capacitor SDK or cordova-plugin-purchase variants), analytics. Verify maintenance and compatibility with your Capacitor major version.
6. Native config: Android manifest permissions, iOS `Info.plist` strings, App Transport Security, privacy manifest, 16 KB page-size compatibility of native libraries (verify), orientation lock, edge-to-edge handling and safe-area insets.
7. Signing: Android keystore and Play App Signing; iOS certificates and profiles; secrets via CI environment.
8. Updates: live updates of web assets are possible with some tools, but store rules restrict changing the app's primary behavior; keep changes to content and bug fixes and check current policy.
9. Review risk: wrapper apps that feel like websites get rejected more often; add native-quality touch response, offline support, saved progress, and native features such as haptics and notifications.
10. Performance: WKWebView on iOS and Android WebView differ; test low-end Android (older WebView versions), limit memory, and avoid very large JS bundles (code-split and lazy-load scenes).

The notes did not research WebView game performance or review outcomes in depth; treat those as items for your own spike.

## 8. PWA and web portals

- PWA: manifest plus service worker for offline play and home-screen install; iOS support is more limited (no reliable background tasks, restricted push in some contexts; verify current behavior).
- Portals and platforms (game portals, social or messaging mini-game platforms): each has an SDK for ads, saves and leaderboards, size limits and review rules; integrate behind the same services interfaces.
- Monetization on web: ads through portal SDKs, IAP via platform-specific systems; there is no unified store billing in plain browsers.

## 9. WebGPU status

- The notes report WebGPU support in Safari 26+ and iOS/iPadOS 26+, which makes it reachable on recent iPhones; Android Chrome support depends on device and version.
- three.js offers a WebGPU renderer with automatic WebGL2 fallback; PixiJS supports WebGPU but defaults to WebGL; Phaser 4 is WebGL2 with no WebGPU renderer yet.
- Decision: default to WebGL2 for reach; adopt WebGPU only for features you need (compute, heavy instancing) and always keep a fallback path. Feature-detect with `navigator.gpu` and request an adapter; log the renderer used in analytics to learn real distributions.
- Test both paths in CI screenshots; shader languages differ (WGSL vs GLSL), so budget extra work for custom shaders.

## 10. Playable ads

A playable ad is a tiny interactive demo shown inside an ad slot. Constraints differ per network; verify each network's current specification.

Typical constraints and practices:
- Hard size cap (low single-digit megabytes in many networks) and often a single self-contained HTML file; no external network requests.
- Must call network-provided hooks (open store, "game ended", "install" call to action) via the network's SDK object; a bundler step injects per-network wrappers.
- Start fast (first interaction within a few seconds), loop quickly, end with a call to action.
- Use light stacks: PixiJS or raw canvas, compressed audio, atlas textures inlined as base64, minimal fonts.
- Build pipeline: Vite with `vite-plugin-singlefile` (or similar), terser minification, image compression, asset budget script that fails the build over the size cap.
- Test: each network provides a previewer; also test on real devices with slow connections and both portrait and landscape; no autoplay sound before touch.
- Compliance: ads must represent the real game honestly (store policies and ad network rules prohibit misleading playables); coordinate with `marketing-ua` and `legal-ethics`.
- Reuse the sim-core from the real game so the playable's rules match.

## 11. Bevy

Bevy is a Rust, code-only ECS engine (permissive licence). The notes report v0.20.0 in Oct 2026, a mobile example project in the repository (Android and Xcode projects), and a small MCP ecosystem (for example tools over the Bevy Remote Protocol). Key caveats:
- The API changes between releases faster than model training data; agents should read the installed crate source and release migration guides rather than relying on memory.
- Mobile production readiness and SDK ecosystem (ads, IAP) are weak or unverified; expect to write native glue.
- Strengths: performance, correctness from the type system, data-oriented design, headless runs for simulation tests.
- Use when the team is Rust-first and the game is simulation-heavy or the target is desktop with mobile as a stretch goal; not recommended as the first choice for monetized mobile titles.

## 12. Other engines

| Engine | Notes for this plugin |
|---|---|
| GameMaker | 2D focus, GML; fast prototyping; mobile export and extensions exist; closed ecosystem; agent verification limited; check current licensing tiers |
| Construct | browser-based no-code editor; HTML5 export wrapped for mobile; good for non-programmers; automation limited |
| GDevelop | open-source no-code event system; cloud build for mobile; JSON project; good for simple games and teaching |
| Solar2D | Lua, lightweight 2D; plugin-based SDKs; small community; verify maintenance |
| Flame (Flutter) | Dart; fits apps that are mostly Flutter UI with game parts; strong plugin ecosystem for IAP/ads/notifications; performance fine for casual 2D |
| MonoGame | pure C# framework; reported to work well with agents; no editor; mobile support via .NET; SDK integration manual |
| React Native + Skia | UI-driven games via react-native-skia; JS/TS; good for simple 2D and UI-heavy apps |
| Native (SpriteKit/Metal, Kotlin/Vulkan) | maximum control; double the work; consider only for tiny or platform-specific needs |

For any of these, run the spike in `references/engine-selection-matrix.md` before committing, with emphasis on monetization SDK coverage and headless builds.

## 13. Checklists

Web game release checklist:
- [ ] Tested on real low-end Android WebView and an older iPhone (WKWebView).
- [ ] Memory profile stable over ten minutes; no growth after repeated scene changes.
- [ ] Audio unlock, interruption and silent-switch behavior verified.
- [ ] Safe area and orientation handled; no accidental scroll or zoom.
- [ ] Save/restore works after the OS kills the WebView.
- [ ] Bundle size budget met; assets lazy-loaded.
- [ ] Store wrapper has native features and passes policy review checklist.
- [ ] Dependency licences recorded; analytics consent handled.

Playable ad checklist:
- [ ] Under the network size cap; single file; no external requests.
- [ ] Network hooks implemented and previewed in each network's tool.
- [ ] Honest representation of the game; no fake UI that misleads.
- [ ] Works in both orientations; first touch within seconds.

## 14. Volatile facts (as of Oct 2026 - verify)

| Fact | Source |
|---|---|
| Phaser v4.2.1, PixiJS v8.22.0, three.js r186, Babylon.js 9.30.0, PlayCanvas engine v2.23.3, Capacitor 8.5.3 stable (9.0.0-alpha in progress), react-native-skia 3.7.0 | https://github.com/phaserjs/phaser/releases ; https://github.com/pixijs/pixijs/releases ; https://github.com/mrdoob/three.js/releases ; https://github.com/BabylonJS/Babylon.js/releases ; https://github.com/playcanvas/engine/releases ; https://github.com/ionic-team/capacitor/releases |
| Licences: Phaser, PixiJS, three.js, PlayCanvas engine, Capacitor, react-native-skia MIT; Babylon.js Apache-2.0 | the repositories above |
| Phaser 4 is WebGL2 with no WebGPU renderer yet; PixiJS supports WebGPU but defaults to WebGL; three.js offers WebGPU with WebGL2 fallback; WebGPU listed for Safari 26+ and iOS/iPadOS 26+ | https://app.cinevva.com/guides/webgpu-vs-webgl-games |
| Phaser 4 SpriteGPULayer for very large sprite counts | https://phaser.io/news/2026/05/phaser4-spritegpulayer-performance |
| Phaser Editor MCP server stale since 2025-09 | https://github.com/phaserjs/editor-mcp-server |
| A generator verifies Babylon.js and three.js games in Chrome with hardware WebGL2 | https://github.com/htdt/godogen |
| Bevy v0.20.0 and mobile example; Bevy Remote Protocol MCP tools | https://github.com/bevyengine/bevy and https://github.com/natepiano/bevy_brp |
| Capacitor build automation, WebView game performance, store review outcomes for wrapper apps, playable ad network size caps | not in the notes; check Capacitor docs, Apple and Google guidelines, and each ad network's playable specification |

## 15. Decision notes

- Keep `core/` free of DOM and renderer imports so the same rules run in Node tests, the playable ad and a later native port.
- Record the WebView targets and memory budget in the design contract.
- If the spike shows p95 over budget on the low-end Android tier after two optimization passes, move presentation to a native engine and keep the core.
- Re-verify versions and WebGPU support at each milestone.
