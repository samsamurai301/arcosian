# Optimization and Thermal Playbooks

This file is the repair manual: once triage has told you whether you are CPU-bound, GPU-bound, memory-bound, I/O-bound or thermally bound, this is what you change, in priority order, with the cost and risk of each change. It covers CPU and garbage collection, GPU overdraw and bandwidth, batching, memory, asset streaming, app size, ADPF and Adaptive Performance, frame pacing and dynamic resolution. Principles over engine trivia: most advice applies to Unity, Godot and native code alike, with engine notes where they differ.

## Contents
1. The optimization loop
2. CPU and GC
3. GPU: overdraw, bandwidth, fill
4. Batching and draw calls
5. Memory
6. Asset streaming and loading
7. App size
8. Thermal management: ADPF and Adaptive Performance
9. Frame pacing
10. Dynamic resolution and quality scaling
11. Decision tables
12. Worked examples
13. Volatile facts (as of Oct 2026 — verify)

## 1. The optimization loop

1. Define the budget and scenario (see `budgets-and-tiers.md`).
2. Measure on the low-tier device, release build.
3. Classify the bottleneck.
4. Choose the single highest-payoff change in that class.
5. Change one thing, re-measure the same scenario, compare p95, p99 and jank, not only average.
6. Keep the change only if the metric moved by more than run-to-run noise.
7. Stop when the budget is met; encode the scenario in an automated test.

Payoff order within any class: remove work (do not do it at all), then reduce work (lower resolution, fewer instances), then amortize work (spread over frames, cache, pool), then make the work cheaper (micro-optimization). Teams do the last one first because it feels like engineering; it pays least.

## 2. CPU and GC

**Find the real cost.** Main thread versus render thread versus worker threads. Gameplay script and UI layout usually dominate main thread; draw submission dominates render thread; Google's guidance recommends separating game and render threads (in Unity, enable multithreaded rendering) and budgeting about 2-3 ms for UI update.

**Allocation discipline (garbage-collected runtimes: C#, GDScript is reference-counted but still churns).**
- No allocation in per-frame code. Typical sources: string concatenation and formatting for HUD text, LINQ, closures and lambdas capturing variables, boxing value types, `foreach` over non-struct enumerators in older runtimes, creating arrays or lists per call, `GetComponent` returning arrays, coroutine yield instructions created fresh each time.
- Fixes: cache strings and update text only when the value changes; reuse lists (clear and refill); pool objects; use struct-based data in hot loops; cache component references.
- Pre-allocate to a known maximum at level load, outside gameplay.
- GC settings: incremental GC spreads collection cost over frames (Unity has an incremental GC option) but does not remove allocation cost; the goal is near-zero steady-state allocation. Trigger collections yourself at safe moments (scene transitions) only if you also removed the in-play allocations.

**Update loop hygiene.**
- Do not run `Update` on thousands of objects; drive them from one manager iterating arrays (data-oriented layout), or use jobs and burst-style code where the engine supports it.
- Tick low-frequency systems at lower rates (AI at 5-10 Hz, UI refresh on change).
- Avoid searches per frame (`Find`, tag lookups, per-frame raycasts you could cache).
- Physics: lower fixed timestep rate if gameplay allows; simplify colliders; use layers to prune pairs. For 2D puzzle games, consider no physics engine at all; a sim-core with grid logic costs almost nothing.
- Pin short-duration worker tasks to little cores where the platform allows (Google guidance); keep latency-critical work on big cores.

**Sim-core separation.** Keep simulation logic in plain code with no engine dependencies (see `game-architecture`). It is faster to test, easier to profile, and lets headless bots run thousands of simulated sessions without rendering.

**Script versus native.** Prefer IL2CPP over Mono on Unity for load time and speed (Google guidance). In Godot, move proven hot loops to typed GDScript first (static typing helps), then to GDExtension or C# only if profiling demands it.

## 3. GPU: overdraw, bandwidth, fill

Mobile GPUs are tile-based; the costs that dominate are fill (pixels shaded), bandwidth (memory traffic) and shader complexity, not raw triangle counts for 2D and stylized 3D.

**Overdraw.** Every transparent layer shades pixels that are later covered.
- Visualize with engine overdraw views; fix hot spots first.
- Full-screen UI panels: disable the layers behind a fully opaque panel; do not leave the whole game rendering under a menu that covers it.
- Particles: large soft quads with additive blending are the classic killer. Reduce quad size, use tighter meshes around the sprite (tight-mesh sprites), cap counts, and fade out by shrinking instead of only alpha.
- Sprite atlases with large transparent margins waste fill: use tight meshes or polygon outlines.
- Order opaque front-to-back and let early-z help; keep transparents few.

**Bandwidth.**
- Texture compression: ASTC primary and ETC2 fallback on Android; on iOS, ASTC. Compressed textures cut memory and bandwidth sharply. Use mipmaps for anything that scales; skip them for fixed-size UI (mipmaps add about 33% memory).
- Texture sizes: do not sample 2048 textures for sprites drawn at 100 pixels; use power-of-two sizes and smaller secondary maps.
- Texture filtering: Google notes bilinear with 2x anisotropic often beats trilinear with 1x on quality-per-cost, and texture filtering can account for a large share of GPU energy; do not default to the most expensive filter.
- Render targets: avoid unnecessary render-target switches, copies and resolves; on tile-based GPUs each resolve is bandwidth. Post-processing chains are the usual cause; combine passes or drop them on low tier.
- Vertex data: compress formats and avoid unneeded attributes.

**Shader cost.**
- Use half precision where visual quality allows on mobile; avoid dependent texture reads and branching heavy loops in fragment shaders; bake what you can; keep variants under control (variant explosion also increases build time and memory).
- Prewarm shader variants during loading to avoid first-use hitches (Unity shader variant collections; Godot ubershaders and pipeline compilation settings, verify on your version).
- Check cost offline with vendor shader compilers (for example Arm's Mali Offline Compiler) before you ship a shader.

**Resolution.** Fill cost scales with pixel count. Rendering the 3D or game layer at 0.7-0.8 scale and the UI at native resolution is often visually near-lossless and cuts GPU time substantially. See section 10.

## 4. Batching and draw calls

- Targets are per tier and per scenario; no universal number is valid. Track draw calls and SetPass (material changes) calls; the latter is usually more expensive.
- Sprite atlases: put sprites that draw together in one atlas and one material. Break batches only for a reason. Dynamic batching of small meshes, SRP batching (Unity) and GPU instancing for repeated meshes each have constraints; check the Frame Debugger for the break reason.
- UI: a canvas rebuild is costly. Split static and dynamic UI into separate canvases; avoid animating things that dirty a big canvas every frame; disable raycast targets on non-interactive elements; avoid layout groups on large dynamic lists (pool and virtualize list items).
- Text: dynamic text is expensive to rebuild; update only on change; use atlases of pre-rendered glyphs for fixed sets.
- 3D: LODs and culling; static batching or combined meshes for static scenery; occlusion culling only if it pays.

Worked example: a match-3 board of 8x8 tiles, each a separate sprite from different atlases, drew 140 batches. Moving all tile sprites into one atlas, giving them a shared material and moving highlight glows into the same atlas cut the board to a handful of batches; CPU render thread time dropped by about the share batching had been costing, measured not guessed.

## 5. Memory

- Textures first (largest), then audio, then meshes and animation, then managed heap.
- Texture checklist: correct compression per asset type (UI with sharp edges may need higher-quality or less aggressive block sizes), no uncompressed textures in shipping, atlas packing to avoid waste, max-size overrides per tier (halve large backgrounds on low tier), read/write disabled unless needed (read/write keeps a CPU copy and doubles memory).
- Audio: stream long music, use compressed in-memory for short SFX decoded on load only if frequently used, mono for 3D or small SFX, limit simultaneous voices.
- Managed heap: pool; avoid per-object finalizers; avoid large temporary arrays; watch for events and static references that keep scenes alive (the classic leak: unsubscribed handlers).
- Scene lifecycle: unload before load; call explicit unload of unused assets after scene change (Unity `Resources.UnloadUnusedAssets` or addressables release; Godot resource references drop when unreferenced).
- Detect leaks: snapshot at steady state, loop a neutral action, snapshot again, diff. Anything that grows each loop is a leak. In the soak test watch memory slope.
- Under pressure: respond to the platform low-memory callbacks (Android `onTrimMemory`, iOS memory warnings) by dropping caches; the game should survive and restore after being backgrounded.

## 6. Asset streaming and loading

- Load asynchronously; never block the main thread on disk reads during gameplay. Spread instantiation across frames.
- Addressables (Unity) or `ResourceLoader.load_threaded_request` (Godot) for async loads and for pack-level lifetime management; group assets by lifetime (always, per-world, per-level) so unloading frees whole bundles.
- Predictive preload: begin loading the next level's assets during the results screen or during a fade.
- Loading screens: budget them; show progress; do not run network calls and asset decompression on the same thread as rendering.
- First-run costs (shader compile, cache build) are part of the startup budget; test with a clean install.
- Delivery: ship a playable first session in the install pack; fetch the rest in the background (Play Asset Delivery fast-follow or on-demand; Apple Background Assets). Always handle a failed or paused download gracefully.

## 7. App size

Procedure: measure by type, then cut in this order.
1. Textures: right-size, correct compression (ASTC block size tuning), atlas packing, remove unused, lower resolution for backgrounds with blur or fixed viewing distance.
2. Audio: encode music at a bitrate that survives phone speakers (lower than console-grade), mono where sufficient, trim silence, loop short stems instead of long recordings.
3. Code and libraries: strip unused engine modules; managed code stripping; remove unused plugins and SDKs (each can add native libraries per ABI); ship only needed ABIs per store rules (AAB handles splits).
4. Meshes and animation data: compress, reduce keyframes, remove unused clips.
5. Split content: install-time minimal pack, remainder as on-demand.
6. Guard: a CI job fails the build when download size exceeds budget or grows more than a threshold between builds, and reports the per-type breakdown.

16 KB page-size compliance (Android): all native libraries must be built for 16 KB alignment for current Play requirements; old third-party plugins are the usual culprit even on an updated engine; verify with APK Analyzer. See the volatile facts.

## 8. Thermal management: ADPF and Adaptive Performance

Why: when a device overheats the OS lowers CPU and GPU clocks without asking; your frame rate collapses abruptly. Adapting before that point keeps a stable lower workload instead of an unstable crash in frame rate.

**Android Dynamic Performance Framework (ADPF)** includes thermal APIs and performance hints:
- Thermal status API: statuses from NONE up to SHUTDOWN (Android 11 and up); register a listener and reduce workload at light and moderate levels rather than waiting for severe.
- `getThermalHeadroom()`: a forecast of headroom before severe throttling, usable to scale proactively (values and interpretation vary by device; calibrate on your test devices).
- Performance Hint API (Android 12 and up): tell the system your target frame duration and thread work durations so it can pick CPU frequency and core placement sensibly; also game mode and game state APIs. Vendors differ in support depth (reports note MediaTek and UNISOC supporting ADPF; verify per device).
- Unity: the Adaptive Performance package with the Android (Google) provider wraps thermal headroom and status; it exposes indexers and automatic scalers (resolution, frame rate, LOD, shadow settings) that you configure per tier.

**iOS:** observe `ProcessInfo.thermalState` notifications (nominal, fair, serious, critical) and Low Power Mode changes; there is no headroom forecast, so trigger on state changes plus your own frame-time trend. Use game mode and preferred frame rate APIs where appropriate.

**Adaptation ladder (apply in order, restore in reverse with hysteresis):**
1. Lower cap on render resolution scale in small steps (dynamic resolution).
2. Reduce particle counts and post-process passes.
3. Reduce effect LOD, shadows, animation update rates for off-screen entities.
4. Lower target frame rate (60 to 45 to 30) as the last resort; changing frame rate is visible, so do it in menus or at natural breaks where possible.
5. Never drop correctness: input latency, game logic tick and fairness must not change with thermal state (competitive fairness and replay determinism).

Hysteresis: require a sustained improvement before scaling back up (for instance, tens of seconds below a threshold) to avoid oscillation, which is more visible than a stable lower setting.

Telemetry: log thermal state transitions and applied adaptation levels to analytics; it tells you which devices need a lower default tier. Cite results from your own data rather than vendor case studies; published vendor case studies (for example Kakao Games reporting improved FPS stability with Adaptive Performance, a 2023 result) show the approach works but are not predictions for your game.

## 9. Frame pacing

- Late frames hurt more than slow average: at 30 fps a missed vsync costs an extra 33 ms. Use the Android Frame Pacing library (Swappy) or the engine's equivalent to align frame presentation to vsync intervals; on iOS use the display link and preferred frame-rate APIs.
- Set the target frame rate explicitly (`Application.targetFrameRate` in Unity, `Engine.max_fps` and vsync mode in Godot) rather than leaving defaults; in menus, lower it.
- Avoid mixing vsync-off uncapped rendering with heavy workloads; it burns power with no visible benefit.
- Measure delta between presented frames, not just render duration; Perfetto's frame timeline gives actual presentation data.
- Input latency: keep input sampling and rendering in step; a stable 30 fps with fresh input beats an unstable 45.

## 10. Dynamic resolution and quality scaling

- Scale the 3D or game layer resolution; keep UI and text at native resolution (render UI to a separate layer or canvas).
- Controller: measure GPU time (or frame time) over a short window; if above threshold, reduce scale by a small step (about 5-10%); if comfortably below for a longer window, increase; clamp to a minimum (for example 0.6-0.7) that the art direction approves.
- Temporal smoothing and a minimum interval between changes avoid visible flicker.
- Combine with sharpening or an upscaler where the engine supports it; review visually on device, because a blurry game is a quality regression.
- Pure CPU-bound games gain nothing from lowering resolution; check classification first.

## 11. Decision tables

| Symptom | Likely class | First actions |
|---|---|---|
| Main thread near budget, GPU idle | CPU | Profile scripts; remove per-frame allocations; manager-driven updates; lower tick rates |
| GPU time near budget, CPU idle | GPU | Overdraw view; reduce resolution scale; cut post-process; check shader cost |
| Both idle, frames uneven | Pacing | Frame pacing library; set target fps; check vsync and compositor |
| Periodic spikes | GC / loading / shaders | Allocation sources; async load; shader prewarm |
| Steady fps decays over minutes | Thermal | Soak test; ADPF adaptation; reduce sustained load |
| Crash on low-RAM devices | Memory | Texture budget; unload before load; low-memory handlers |
| Slow first launch only | Startup / first-run | Defer SDK init; prewarm; async load; check install-time work |
| Big download | Size | Size by type; compression; split content |

## 12. Worked examples

**A. Particles melt a mid-tier GPU.** Symptom: a merge-puzzle chain reaction drops from 60 to 35 fps. GPU ms is 24, CPU 6. Overdraw view shows the particle layer saturating the board. Changes in order: shrink quads to the visible size with tight meshes (large drop), cap simultaneous emitters at a number set from the budget, fade by scale. Result: GPU ms drops enough to hit 16.6 ms. Cost: tiny art tweak; no code risk.

**B. GC hitch every 4 seconds.** Symptom: p99 frame 60 ms, p50 15 ms. Profiler: GC.Collect aligned with spikes; allocations from score label formatting and a per-frame `new List`. Fix: update text only on value change, reuse list. Result: spikes gone; managed heap flat.

**C. Soak decay.** Symptom: mid device holds 60 fps for 10 minutes, 42 fps by minute 40; thermal status rose. Cause: sustained high GPU resolution plus continuous full particles. Fix: dynamic resolution driven by thermal headroom, particle cap by thermal state, default to 30 fps on low tier. Result: flat 30 fps with stable pacing beats the decaying 60.

## Pre-merge performance checklist for feature work

- [ ] No new per-frame allocations in hot paths (checked with the profiler GC Alloc column on the scenario).
- [ ] New textures use the agreed compression, sit in an atlas and respect the per-scene texture budget.
- [ ] New particles and UI layers checked in the overdraw view on a low-tier device.
- [ ] New assets load asynchronously and unload with their scene.
- [ ] New SDK or plugin: size delta, startup delta, native library alignment, background threads and permissions reviewed.
- [ ] Perf scenario re-run; p95, p99 and jank within budget; report attached as evidence.
- [ ] Thermal effect considered: does the feature add sustained GPU or CPU load in long sessions?

## 13. Volatile facts (as of Oct 2026 — verify)

| Fact | Source |
|---|---|
| ADPF Thermal API (Android 11+), Performance Hint API (Android 12+); `getThermalHeadroom()` for pre-emptive scaling | https://developer.android.com/stories/games/mediatek-adpf |
| Unity Adaptive Performance Android provider (v5.x) wraps ADPF thermal APIs | https://docs.unity3d.com/Packages/com.unity.adaptiveperformance.google.android@5.1/manual/index.html |
| Kakao Games case study of FPS stability improvement with Adaptive Performance (2023) | https://android-developers.googleblog.com/2023/09/kakao-games-increased-fps-stability-through-android-adapatability.html |
| Netmarble used ADPF for resolution scaling and dynamic frame rate | https://developer.android.com/stories/games/netmarble-got-adpf |
| UNISOC supports core ADPF APIs from Android 14 | https://developer.android.com/stories/games/unisoc-adpf |
| Texture guidance (ASTC primary, ETC2 fallback, filtering and mipmap costs) | https://developer.android.com/games/optimize/textures |
| Google games optimization guidance (threads, frame pacing, IL2CPP, UI budget, little cores) | https://developer.android.com/games/optimize |
| Play Asset Delivery modes; Apple Background Assets replacing ODR | https://developer.android.com/guide/playcore/asset-delivery ; https://developer.apple.com/videos/play/wwdc2025/325 |
| 16 KB page size: Unity support from 6000.0.38f1 and 6000.1+; stale plugin `.so` files may still be flagged | https://discussions.unity.com/t/info-unity-engine-support-for-16-kb-memory-page-sizes-android-15/1589588 |
