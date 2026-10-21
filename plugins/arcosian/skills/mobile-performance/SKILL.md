---
name: mobile-performance
description: Mobile game performance codex - per-tier frame, memory, size and startup budgets, thermals, profiling (Unity, Godot, Instruments, Android Studio, Perfetto, AGI), optimisation playbooks, ADPF and soak tests, perf-report schema and perf_budget.py; PC, Steam Deck, web and console tiers are in platform-targets. Use when asked "why is it slow", "set perf budgets", "profile this", "it gets hot", "reduce APK size" or "perf gate".
---

# Mobile Performance

Performance on phones is a budget problem, not a tuning problem. You decide the numbers first (per device tier), measure on real hardware in release builds, find the one bottleneck that actually dominates, fix it, and lock the result with an automated gate. This skill is the playbook for that loop.

## What this skill gives you

- Budget tables for frame time, memory, download size and cold start per device tier, and the rules for choosing a tier matrix (`references/budgets-and-tiers.md`).
- A profiler selection guide and headless/CI recipes for every major mobile profiling tool (`references/profiling-toolkit.md`).
- Optimization playbooks for CPU/GC, GPU fill and bandwidth, memory, streaming, app size, thermal adaptation and frame pacing (`references/optimization-and-thermal.md`).
- The automation layer: perf tests, 45-50 minute soak tests, device farms, the perf-report schema, `perf_budget.py` and regression tracking (`references/perf-testing-automation.md`).
- A bottleneck triage procedure that tells you which of CPU, GPU, memory, I/O or thermal to attack first.

## Core models

**1. The frame budget is a deadline, not an average.** At 60 fps a frame has 16.6 ms; at 30 fps, 33.3 ms. A single late frame is a visible hitch, so gate on p95 and p99, plus "1% low" fps, never on average fps alone. A frame that misses vsync costs a whole extra interval (at 30 fps that is an extra 33 ms), which is why frame pacing matters as much as raw speed.

**2. Pipeline, not a single number.** CPU main thread, render thread, GPU and (on mobile) the display compositor run in a pipeline. Frame time is the slowest stage. Optimizing the wrong stage changes nothing. Always classify first: CPU-bound (main or render thread saturated, GPU idle), GPU-bound (GPU time near frame time), or vsync/pacing-bound (both idle, frames still late).

**3. Sustained beats peak.** A phone that hits 60 fps for two minutes and throttles to 40 fps at minute 20 is a 40 fps device. Budgets are defined for the thermally steady state. Google's games guidance warns that frame rates often degrade after roughly 45-50 minutes of play; design the soak test around that.

**4. Tiers define the contract.** Pick low, mid and high reference devices, set budgets for each, and let quality settings (resolution scale, effects, texture size, frame target) map to tiers. The low tier is the one that decides your market reach and your crash rate; the high tier is where you spend headroom on polish.

**5. Memory is a hard wall, not a soft one.** CPU frame time degrades gracefully; memory does not. The OS kills foreground apps that exceed their per-device limit, and the player sees that as a crash. Budget peak resident memory well under physical RAM and test on the lowest RAM tier.

**6. Measure in release, on device.** Editor numbers, debug builds and emulators mislead on GPU, thermal and memory behaviour. Use a development build only to attach a profiler and a release build for the numbers that go into a report.

**7. Power is the hidden budget.** Frames you do not need are battery and heat you pay for. 30 fps for a puzzle game, on-demand rendering for static screens and a capped frame rate in menus are performance wins even when fps was fine.

## Decision procedures

### A. Set budgets (new project or new tier)
1. List target devices and pick three reference devices (low/mid/high) with real hardware in hand. See the tier rules in `references/budgets-and-tiers.md`.
2. Choose fps target per genre: 30 fps for puzzle, idle and card games is normal; 60 fps for action, runners, anything with continuous touch-tracking; justify anything higher by a battery decision.
3. Fill `technical.perf_budgets` in the contract: `fps_target`, `frame_ms_p95`, `memory_mb`, `download_mb`, `cold_start_sec`. Derive `frame_ms_p95` from the target (16.6 or 33.3) for the reference device.
4. Add pipeline-suggested extras per tier: draw calls, UI ms, peak memory fraction of RAM, thermal end state. Record them as proposals, not facts.
5. Record the scenario that stresses the game (worst realistic content, VFX on, long session), because budgets apply per scenario.

### B. "It's slow" triage (30 minutes, in order)
1. Reproduce on the low-tier device in a release build with a fixed scenario. If you cannot reproduce on device, stop; the Editor lies.
2. Capture 30-60 s of frame times. Run `perf_budget.py --report frames.csv` to get avg fps, 1% low, p50/p95/p99 and jank.
3. Classify the bottleneck: compare CPU ms and GPU ms per frame (see `references/profiling-toolkit.md`). CPU main thread near budget: CPU path. GPU ms near budget: GPU path. Both low but late: pacing/vsync path. Spikes only: GC, loading or shader compilation path.
4. Pick the single largest cost item in that path and fix only that. Re-measure the same scenario. Repeat until budget is met, then stop; do not optimize past the budget.
5. Add the scenario to the automated perf test so the fix cannot silently regress (`references/perf-testing-automation.md`).

### C. Hitch hunting (spikes, not averages)
1. Plot frame times; list frames over 2x median (that is the `jank` metric in `perf_budget.py`).
2. Correlate spike frames with events: GC.Collect, scene or asset load, shader compile, instantiate bursts, save to disk, ad or SDK callbacks.
3. Fix by category: pool and pre-warm objects, preload and prewarm shaders, move I/O off the main thread, spread work across frames, remove per-frame allocations.

### D. Thermal or battery complaint
1. Run the soak test (45-50 minutes) on the low and mid devices, logging thermal status, frame times and battery every 10 s.
2. If frame time drifts upward while thermal status rises, the cause is sustained load; reduce work per frame (resolution scale, effect LOD, fps cap) rather than micro-optimizing code.
3. Wire runtime adaptation (ADPF thermal headroom, Unity Adaptive Performance, iOS thermal state notifications) so the game scales down before the OS forces it. See `references/optimization-and-thermal.md`.

### E. App size or download over budget
1. Produce a size report: per-asset-type bytes (textures, audio, meshes, code, native libs). Android Studio APK Analyzer or Unity build report.
2. Rank by bytes. Textures and audio dominate most 2D mobile games; native libraries and engine code dominate small games.
3. Apply the cheapest cuts first: compression format and quality, atlas packing, audio bitrate and mono, strip unused modules and plugins, then split content into install-time versus on-demand packs.

## Mobile specifics

- Thermal throttling and battery drain define the real ceiling; screen brightness, radios and GPU load all feed heat.
- Low-end Android (2-4 GB RAM, older GPUs) is the memory and fill-rate floor; iOS devices are more uniform but older models still exist in the install base.
- Fill rate and memory bandwidth beat triangle count as GPU limits on tile-based mobile GPUs. Overdraw from transparent UI and particles is the most common 2D-game GPU problem.
- Startup time and size drive installs and early retention; they are product metrics, not just engineering ones.
- Interruptions (calls, backgrounding) must not leak memory or break state; test backgrounding under memory pressure.
- Android requires 16 KB page-size compatibility for current Play targets (see Volatile facts) and an APK Analyzer check for stale native libraries.

## Anti-patterns

| Anti-pattern | Detect | Fix |
|---|---|---|
| Profiling in the Editor or an emulator | Report device name is "editor" | Re-measure on a real low-tier device, release build |
| Optimizing average fps | Avg fine, players complain of stutter | Gate on p95, p99, 1% low and jank count |
| Optimizing before classifying | Changes do not move frame time | Triage CPU vs GPU vs pacing first |
| One reference device | Crash or lag reports from unseen models | Three-tier matrix, plus farm sweep |
| Per-frame allocations | GC spikes in profiler, rising managed heap | Pool, cache, avoid LINQ/strings/closures in Update |
| Unbounded transparent overdraw | GPU-bound, overdraw view solid red | Trim UI layers, tighten particle quads, mask atlases |
| No soak test | Fine at 5 min, bad at 40 | 45-50 minute soak on low and mid tier |
| Budgets only in a doc | No test fails when budget is exceeded | Perf gate in CI via `perf_budget.py` |
| Fixing past the budget | Weeks spent for 2 ms nobody sees | Stop at budget; spend time on content |

## Using the ontology

- Budgets live in the design contract at `technical.perf_budgets` (`${CLAUDE_PLUGIN_ROOT}/scripts/schemas/design-contract.schema.json`).
- Measurements are written as perf reports (`${CLAUDE_PLUGIN_ROOT}/scripts/schemas/perf-report.schema.json`) into `.gamestudio/reports/*.perf.json`; the perf gate accepts them as evidence.
- Check a report: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/perf_budget.py --report <report.json|frames.csv> --contract .gamestudio/contract.json [--json]`. Exit 0 pass, 1 budget failed, 2 input error. Budgets with no measurement are reported as skipped, never as passes.
- Validate report shape with `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_json.py` against the perf-report schema.
- Template evidence sources. `templates/godot-starter` ships the perf gate tool `tools/perf/perf_probe.gd`. It plays the real game scene with a greedy bot and writes a perf-report JSON to the `--out` path (name it `.gamestudio/reports/<feature-or-build>.<device>.perf.json`). Windowed: `godot --path <project> -s res://tools/perf/perf_probe.gd -- --out=<abs>/perf.json [--seconds=20] [--budget-frame-ms=16.7] [--budget-memory-mb=512]`. CPU-only: the same command with `--headless`. Exit 0 pass, 1 budget violated, 2 usage or cannot run. Options (`--tier`, `--device-name`, `--build`, `--scenario`, `--feature`, `--frames`, `--pace-fps`) and the full semantics are in `templates/godot-starter/README.md`.
- Reading probe reports: `frame_ms` is main-thread CPU work per frame without vsync or idle waits. **Headless runs are CPU-only**: no renderer, so `draw_calls` and `gpu_ms` are null, the report is flagged `headless: true` with `device.name` `desktop-headless`, and it is not valid device evidence. **Metal reports no GPU timing**, so on a Metal renderer `gpu_ms` is null and `frame_ms` is CPU-side only even windowed (take GPU time from Xcode Instruments). Both modes are desktop proxies run on an editor or debug binary; the gate's release evidence is still a capture from the reference device in the same shape.
- `templates/unity-starter` produces no perf report (its README marks the `perf` gate "not produced here"), so Unity projects add a sampler or Performance Testing tests; its batchmode commands for the unit, playthrough and build gates are in `templates/unity-starter/README.md` and `engine-unity`. Details in `references/perf-testing-automation.md` §3.
- Recorded metrics map to resources and loops: frame cost per loop iteration and session length from the player model feed budget scenarios.

## Reference library

| File | What it contains | When to read |
|---|---|---|
| `references/budgets-and-tiers.md` | Frame and memory budgets per tier, device-tier examples (volatile), thermal and battery, download size, startup | Setting or reviewing budgets, choosing devices |
| `references/profiling-toolkit.md` | Unity, Godot, Instruments, Android Studio, Perfetto and Trace Processor, AGI, Snapdragon, Arm Performance Studio, RenderDoc; headless and CI use | Choosing a profiler or scripting a capture |
| `references/optimization-and-thermal.md` | CPU/GC, GPU overdraw and bandwidth, batching, memory, streaming, app size, ADPF, frame pacing, dynamic resolution | Fixing a classified bottleneck |
| `references/perf-testing-automation.md` | Automated perf tests, soak tests, device farms, perf-report schema, `perf_budget.py`, regression tracking | Building or running the perf gate |

## Volatile facts (as of Oct 2026 — verify)

| Fact | Source |
|---|---|
| Thermal API broadly available from Android 11 (API 30); Performance Hint API from Android 12 (API 31) | https://developer.android.com/stories/games/mediatek-adpf |
| Google guidance on 45-50 minute frame-rate degradation, frame pacing, UI budget 2-3 ms | https://developer.android.com/games/optimize |
| Play Asset Delivery for games above 200 MB; Apple Background Assets replaces On-Demand Resources | https://developer.android.com/guide/playcore/asset-delivery ; https://developer.apple.com/videos/play/wwdc2025/325 |
| Google Play 16 KB page-size requirement | https://discussions.unity.com/t/info-unity-engine-support-for-16-kb-memory-page-sizes-android-15/1589588 |

## Related skills

- `technical-art` - shaders, atlases, import settings that feed art performance.
- `game-architecture` - sim-core separation and update-loop design that make perf predictable.
- `qa-testing` - playthrough and soak automation that the perf tests ride on.
- `engine-unity`, `engine-godot` - engine-specific profiler and build settings.
- `store-release` - size limits, vitals and store technical gates.
- `mobile-ux` - 30 vs 60 fps and loading-state decisions from the player side.
