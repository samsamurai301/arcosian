# Profiling Toolkit

This file is a field guide to the profilers a mobile game team actually uses: Unity Profiler and friends, Godot's profiler and monitors, Xcode Instruments, Android Studio and adb tools, Perfetto with its Python Trace Processor, Android GPU Inspector, Snapdragon Profiler, Arm Performance Studio and RenderDoc. For each it says what question it answers, how to capture, and how far it can be driven headlessly from a script or CI job. Facts that I could not verify against current official docs are marked "verify"; scriptability claims marked "verify" should be tried once on your toolchain before you build a pipeline on them.

## Contents
1. Choosing a tool by question
2. Capture hygiene (applies to every tool)
3. Unity
4. Godot
5. Xcode Instruments
6. Android Studio, adb and dumpsys
7. Perfetto and Trace Processor (Python)
8. Android GPU Inspector, Snapdragon Profiler, Arm Performance Studio
9. RenderDoc
10. Headless and CI matrix
11. Worked example: from trace to verdict
12. Volatile facts (as of Oct 2026 — verify)

## 1. Choosing a tool by question

| Question | First tool | Second tool |
|---|---|---|
| Is the game CPU-bound, GPU-bound or pacing-bound? | Engine profiler plus frame-time capture | Perfetto system trace (all threads, GPU queue, vsync) |
| Which function or system burns CPU? | Unity Profiler / Godot profiler / Instruments Time Profiler | Simpleperf, Arm Streamline |
| Where do GC spikes and allocations come from? | Unity Profiler (GC Alloc column), Memory Profiler | Instruments Allocations |
| What is in memory, what leaked? | Unity Memory Profiler snapshots, Instruments Leaks and Allocations | Android Studio memory profiler, `dumpsys meminfo` |
| What does the GPU spend time on? | Xcode GPU capture (Metal), AGI, Snapdragon Profiler, Arm Frame Advisor | RenderDoc frame capture |
| Overdraw and bandwidth? | Engine overdraw views, Arm and Snapdragon counters | RenderDoc and vendor tools |
| Is it thermal? | Perfetto thermal and frequency tracks, `dumpsys thermalservice`, Instruments thermal state | Soak test with logged status |
| Why is the install big? | Android Studio APK Analyzer, Unity build report | Per-asset size diff in CI |
| Why is startup slow? | Perfetto, Instruments App Launch, Unity startup markers | Android `am start -W` launch timing |

## 2. Capture hygiene (applies to every tool)

1. Real device, release configuration (or development build only where the profiler demands it, and then say so in the report).
2. Fixed scenario, scripted or bot-driven, so two captures are comparable.
3. Warm up first: discard the first several seconds (shader compile, cache fill, JIT where relevant).
4. Fixed environment: airplane mode or controlled network, fixed screen brightness, no charging unless that is the scenario, same thermal starting state (let the device cool between runs), no other foreground apps.
5. Capture long enough: 30-60 s for steady state, 45-50 minutes for the soak.
6. Record device model, OS build, app build, tier, scenario and tool version with every capture; a number without that metadata is not evidence.
7. Profiler overhead is real: deep profiling, memory snapshots and GPU captures perturb frame time. Use them to find causes, then measure the fix with a light capture.

## 3. Unity

**Unity Profiler.** CPU Usage (timeline and hierarchy), GPU Usage where the platform exposes it, Rendering (batches, SetPass calls, triangles), Memory (managed, native, graphics), Audio, UI. Use Deep Profile sparingly; it distorts timings. Attach to a development build over USB or Wi-Fi. Mark your own scopes with `ProfilerMarker` so game systems appear by name.

**Frame Timing Manager / FrameTimingManager.** Runtime API that reports CPU and GPU frame times in a build without the Profiler attached, which is how you collect GPU ms in a release-like build for a perf report (platform and graphics API support varies; verify on target devices).

**Profile Analyzer.** Compares two captures statistically (median, upper quartile, outlier frames). Use it for before-and-after verification of an optimization.

**Memory Profiler package.** Takes snapshots and compares two of them; works with development builds and the Editor. Capturing can briefly freeze the app and allocate memory, so never use the capture itself as a memory reading. Programmatic capture is available through `MemorySnapshot.RequestNewSnapshot`. Procedure: snapshot at scene A steady state, play the loop that should be neutral (enter and leave a level five times), snapshot again, diff; any growing category is a leak.

**Performance Testing Extension** (`com.unity.test-framework.performance`). Test Framework attributes plus measurement helpers; writes JSON results with player and build metadata; Unity Test Framework always builds a development player for these runs. Pattern (verify API names against your installed version):

```csharp
[UnityTest, Performance]
public IEnumerator Level30_Wave10_Frames()
{
    yield return LoadScenario("level30_wave10");
    yield return new WaitForSeconds(5);                 // warmup, not measured
    using (Measure.Frames().WarmupCount(10).MeasurementCount(1800).Scope())
        yield return null;                              // let frames run
    Measure.Custom("peak_memory_mb", Profiler.GetTotalAllocatedMemoryLong() / 1048576.0);
}
```

**Frame Debugger.** Step through draw calls for a frame; shows why batches broke (material, texture, keyword differences). Editor only for most use.

**Build Report and Editor log.** Per-asset size contributions; read `Editor.log` "Build Report" section or the BuildReport API in a build script for CI size tracking.

**Headless:** Test Framework in batch mode (`-batchmode -runTests -testPlatform PlayMode`), Performance Testing JSON, BuildReport API. The interactive Profiler and Memory Profiler UI are GUI; agents should rely on exported data (saved `.data` captures opened by a human, JSON from tests, runtime logs from your own telemetry).

## 4. Godot

- **Built-in debugger Profiler and Monitors** (Debugger panel): per-function script time, physics and render times, object counts, memory, draw calls, video memory. Remote debug a device build from the editor over the network.
- **Visual Profiler** shows CPU and GPU time per render pass (platform support varies; verify on mobile renderers).
- **Rendering debug views** in the editor: overdraw, wireframe, unshaded.
- **Headless scripted metrics:** write your own sampler as an autoload that records `Performance.get_monitor(...)` values (time per frame, process time, draw calls, object count, static memory) plus `Engine.get_frames_per_second()` to a CSV or perf-report JSON, so a CI or device run produces numbers without the editor. The `templates/godot-starter/` template already ships that sampler as `tools/perf/perf_probe.gd`: it plays the real game scene with a greedy bot (the same policy as `tools/playtest/runner.gd`), samples every frame and writes a perf-report JSON (`godot --path <project> -s res://tools/perf/perf_probe.gd -- --out=<abs>/perf.json [--seconds=20]`, add `--headless` for a CPU-only run). It is a desktop proxy measured on an editor or debug binary, so use it for regression checks and a first report, and capture release numbers on the reference device. Headless runs have no renderer, so `draw_calls` and `gpu_ms` are null and the report is flagged `headless`. Metal reports no GPU timing, so on Metal `gpu_ms` is null and `frame_ms` is CPU-side only even windowed: read GPU time from Xcode's Metal System Trace (section 5).
- **Platform tools on top:** for Android use Perfetto and `dumpsys`; for iOS use Instruments attached to the exported Xcode build.
- Rendering method matters: Mobile renderer versus Compatibility renderer have different costs; profile the one you ship.

## 5. Xcode Instruments

| Template | Use |
|---|---|
| Time Profiler | CPU hot paths by call tree |
| Allocations and Leaks | Memory growth, leaked objects |
| Metal System Trace | CPU/GPU timeline, frame pacing, shader compile stalls; the source of GPU time when an engine's own probe (for example the Godot template's `perf_probe.gd`) reports none on Metal |
| Game Performance (where available) | Combined frame-rate and Metal view; verify template names on your Xcode version |
| Energy Log / Power Profiler | Battery impact, CPU/GPU/network/location power contributions |
| App Launch | Startup phases |
| Thermal State (in the system view) | Correlate throttling with frame drops |

GPU: Xcode's Metal frame capture and GPU Counters show per-pass cost, bandwidth and occupancy; Metal HUD overlays live fps on device.

Headless: Instruments can be driven from the command line with `xcrun xctrace record --template "<name>" --device <udid> --launch <bundle>` and read back with `xcrun xctrace export` (scriptable but not verified in this session's research; verify on your Xcode version). The GUI timeline is for humans; export tables for agents.

Measure on a real device with the Release configuration plus debug symbols; Simulator timings are meaningless for performance.

## 6. Android Studio, adb and dumpsys

- **Android Studio Profiler:** CPU (system trace, Java/Kotlin and native sampling), Memory (heap dump, native allocations), Energy. For game engines most of the value is in the system trace and memory views.
- **APK Analyzer:** per-file sizes inside APK or AAB; also use it to confirm native libraries are 16 KB aligned (stale third-party `.so` files are the common failure).
- **Command-line signals** (scriptable; exact output format varies by OS version, so parse defensively and verify):

| Command | Gives you |
|---|---|
| `adb shell dumpsys gfxinfo <package> framestats` | Per-frame timestamps for jank analysis (best for UI-rendered apps; engine games using their own surface may report less) |
| `adb shell dumpsys SurfaceFlinger --latency <layer>` | Frame presentation timestamps for a surface layer |
| `adb shell dumpsys meminfo <package>` | PSS breakdown (native, graphics, Java, code) |
| `adb shell dumpsys thermalservice` | Current thermal status and sensors |
| `adb shell dumpsys battery` / `batterystats` | Battery level, temperature, per-app usage |
| `adb shell am start -W <activity>` | Launch time (ThisTime, TotalTime, WaitTime) |
| `adb shell simpleperf` | Native CPU sampling |
| `adb logcat -b crash` | Crash buffer |

Always run `adb shell dumpsys` against a release build on a cooled device with the screen on.

## 7. Perfetto and Trace Processor (Python)

Perfetto is the system-wide tracer on Android: scheduling, CPU frequency, GPU, thermal, frame timeline and app slices in one trace. Google's guidance puts system-tracing overhead under about 1% and notes a buffer of roughly 10-15 MB per core giving about 20 seconds of trace; size buffers to your capture length.

Capture options: the Perfetto UI web recorder (device over WebUSB), the Android Studio system trace, or `adb shell perfetto` with a text config (scriptable; verify the flags on your Android version). Add app-level markers via Unity `ProfilerMarker` to Perfetto (engine-dependent) or `android.os.Trace` sections from native or plugin code so your game's phases appear as named slices.

Trace Processor Python API (`pip install perfetto`): loads a trace from file, stream or URI, runs PerfettoSQL, returns pandas or Polars DataFrames when those are installed, exports to sqlite or Arrow, and pins and downloads a `trace_processor` binary for reproducibility. It has no GUI dependency, so it suits headless analysis. `trace_summary()` is the structured-summary path; the older `metric()` is deprecated. CI use is plausible but not explicitly documented; pin versions.

```python
from perfetto.trace_processor import TraceProcessor
tp = TraceProcessor(trace="game.perfetto-trace")
q = tp.query("""
  select ts, dur/1e6 as ms
  from actual_frame_timeline_slice
  where upid = (select upid from process where name like '%mygame%')
""")
frames = [r.ms for r in q]          # list of frame durations in ms
open("frames.csv","w").write("frame_ms\n" + "\n".join(f"{x:.3f}" for x in frames))
```

Table and column names evolve between Perfetto versions; check the PerfettoSQL standard-library docs for your pinned version (verify). Then run `perf_budget.py --report frames.csv`.

Useful queries to write once and keep: frames over 2x median with their overlapping slices; CPU frequency and thermal tracks around the slow window; main-thread state (running, runnable, sleeping) during spikes (runnable-but-not-running means CPU contention or little-core placement).

## 8. AGI, Snapdragon Profiler, Arm Performance Studio

**Android GPU Inspector (AGI).** Google's GPU profiler for Android: frame profile, system profile and GPU counters. Useful for per-draw GPU cost on supported devices. The official docs URL for its command line returned an error during research; treat CLI scripting as unverified and plan for GUI use by a human, with exported results handed to the agent.

**Snapdragon Profiler.** Qualcomm tool for Adreno GPUs: real-time counters, system trace, snapshot capture. Command-line control exists but was not verified; assume GUI for now.

**Arm Performance Studio** (formerly Arm Mobile Studio): five components, namely Streamline (CPU and GPU counters, timeline), Frame Advisor (frame replay with per-draw cost), RenderDoc for Arm, Mali Offline Compiler (shader cost estimation without a device) and Performance Advisor. Performance Advisor is part of Streamline and can generate reports in a CI workflow alongside regular builds; Arm publishes a learning path on CI integration. This is the most CI-friendly vendor profiler in the research.

Vendor tools matter when the question is "why is this one chip slow": Mali and Adreno behave differently on overdraw, bandwidth and shader precision. Use them after the engine profiler says GPU-bound.

## 9. RenderDoc

Frame-capture graphics debugger (Vulkan and OpenGL ES on Android, with Arm's build for Mali devices; PC for the Editor). Use it to inspect a single frame: draw order, render-target switches, overdraw, texture sizes bound per draw, and shader inputs. It has a Python API that can script replay and extraction (not verified here; verify). Capture on device is intrusive, so use it for diagnosis, not for numbers.

Typical findings: full-screen passes at full resolution that should be half resolution; render-target ping-pong from stacked post effects; huge textures sampled for small sprites; unnecessary clears or resolves that cost tile-memory bandwidth.

## 10. Headless and CI matrix

| Tool | Scriptable headless | Output | Confidence |
|---|---|---|---|
| Unity Test Framework (batch mode) | Yes | NUnit XML (`-testResults`; the `templates/unity-starter` EditMode command is in its README) | Cited in research; format confirmed by the template README |
| Unity Performance Testing | Yes, inside tests | JSON | Cited |
| Unity BuildReport API | Yes, in build script | Size per asset | Standard API |
| Perfetto Trace Processor | Yes | DataFrames, CSV | Cited |
| Arm Performance Advisor | Yes | Report files | Cited |
| APK Analyzer checks | Yes | Size and alignment data | Cited |
| `adb shell perfetto` capture | Yes | Trace file | Unverified here; verify |
| `xcrun xctrace record/export` | Yes | Trace bundle, XML tables | Unverified here; verify |
| `adb shell dumpsys gfxinfo/meminfo` | Yes | Text | Unverified here; verify |
| AGI CLI | Unknown | n/a | Doc URL failed; verify |
| RenderDoc Python API | Probably | Captures | Unverified; verify |
| Snapdragon Profiler CLI | Unknown | n/a | Unverified; verify |
| Unity Profiler UI, Memory Profiler UI, Instruments UI | No (GUI) | Exportable data only | Mostly GUI-only |

Policy: an agent-driven pipeline should depend only on "Yes, cited" rows for gates, and treat the rest as optional evidence a human or a one-off job produces.

## 11. Worked example: from trace to verdict

Symptom: mid-tier Android device averages 54 fps on the busiest level, with visible stutter.
1. Capture 60 s via Perfetto on a cooled device after a 10 s warmup. Pull frame durations with the query above and write `frames.csv`.
2. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/perf_budget.py --report frames.csv --json` shows avg fps below target, p99 well above p50, and a jank count. A big gap between p50 and p99 says spikes, not steady cost.
3. Query spike frames: the main thread is "running" and the slice named for your GC step overlaps each one. That is a GC spike, not GPU.
4. Open the Unity Profiler on a development build in the same scenario: GC Alloc column points at string formatting in the HUD update and a per-frame list allocation in the match finder.
5. Fix both (cache strings, reuse list), re-capture with the same protocol, rerun `perf_budget.py`; p99 drops and jank count falls to near zero.
6. Add the scenario to the automated perf test with the post-fix p95 as the regression threshold plus tolerance.

## Capture checklist (print and tick)

- [ ] Device cooled to the same starting state; battery above a stated level; brightness fixed.
- [ ] Build type recorded (release or development) and symbols available.
- [ ] Scenario named, warmup excluded, duration at least 30 s (soak: 45-50 min).
- [ ] Tool and version recorded; overhead acknowledged.
- [ ] Raw capture archived next to the derived frames CSV or perf-report JSON.
- [ ] A second run to estimate variance; if two runs differ more than your tolerance, fix the protocol before trusting either.

## 12. Volatile facts (as of Oct 2026 — verify)

| Fact | Source |
|---|---|
| Unity Performance Testing package `com.unity.test-framework.performance` (v3.0.3 listed for 2020.3-2023.2); builds a development player; JSON results | https://docs.unity3d.com/Packages/com.unity.test-framework.performance@3.0/manual/index.html |
| Unity Memory Profiler works only with development builds and the Editor; snapshot capture can freeze the app | https://unity.com/blog/engine-platform/everything-you-need-to-know-about-memory-profiler |
| Perfetto Trace Processor Python API: `pip install perfetto`, DataFrames, `trace_summary()`, binary pinning | https://perfetto.dev/docs/analysis/trace-processor-python |
| Arm Performance Studio components; Performance Advisor reports in CI | https://developer.arm.com/community/arm-community-blogs/b/mobile-graphics-and-gaming-blog/posts/what-is-arm-performance-studio |
| System tracing overhead under 1%, buffer sizing guidance | https://developer.android.com/games/optimize |
| AGI CLI documentation URL returned an error in research (404) | https://developer.android.com/games/optimize (links to AGI docs; re-check) |
