# Performance Testing and Automation

This file covers turning performance from a periodic fire-drill into a gate that runs on every build: automated perf scenarios, soak tests that catch the 45-50 minute thermal decay, device farms, the perf-report schema this plugin uses, the `perf_budget.py` checker, and regression tracking over time. The design principle is that a number is only evidence if it comes from a release build on a real device in a named scenario with recorded metadata, and that every budget in the contract has a test that can fail.

## Contents
1. Test layers
2. Designing perf scenarios
3. Running scenarios per engine
4. Soak tests (45-50 minutes)
5. Device farms
6. The perf-report schema
7. perf_budget.py
8. Regression tracking
9. CI pipeline shape
10. Failure triage and flakiness
11. Worked example
12. Volatile facts (as of Oct 2026 — verify)

## 1. Test layers

| Layer | Runs on | Cost | Catches | Valid as release evidence |
|---|---|---|---|---|
| Static budgets (size, alignment, asset rules) | CI, no device | Seconds | Size growth, uncompressed textures, 4 KB-aligned libraries | Yes for size items |
| Headless sim cost (sim-core step time, bot throughput) | CI | Minutes | CPU regressions in game logic | No (proxy only; Godot template: `perf_probe.gd --headless`, CPU-only) |
| Editor or desktop perf run | CI or dev machine | Minutes | Gross regressions, allocation counts | No (proxy; label "editor" or "desktop-headless"; Godot template: windowed `perf_probe.gd`) |
| Device perf scenario (60-120 s) | Real device or farm | 5-15 min | Frame time, memory, draw calls on target hardware | Yes |
| Soak (45-50 min) | Real device, dedicated | About an hour | Thermal decay, leaks, memory slope, battery | Yes |
| Field telemetry (frame time, thermal, crash by device) | Live users | Continuous | Real-world device mix | Yes (statistical) |

Policy: the perf gate in the five-gate definition of done accepts a perf-report from a device layer; proxies run on every commit to catch regressions early but never satisfy the gate by themselves. The Godot template's `perf_probe.gd` is exactly such a proxy (section 3 has its commands and caveats); the Unity template has none.

## 2. Designing perf scenarios

A scenario is a deterministic, repeatable workload that stresses the game realistically.

Requirements:
1. Deterministic input: use the playthrough runner or a seeded bot (see `qa-testing`) so every run does the same work.
2. Worst realistic content: busiest level, maximum entities, all VFX on, ads or overlay SDKs initialized, audio playing.
3. Warmup excluded: first 5-10 seconds dropped.
4. Window: 60-120 s for the standard run; thermal effects need longer, hence the soak.
5. Fixed environment: tier settings forced, brightness fixed, network mode fixed, device cooled between runs.
6. Named: scenario text goes into the report (`scenario` field) because budgets apply per scenario.

Recommended scenario set for a typical mobile game:

| Scenario | Purpose |
|---|---|
| menu_idle | Menus and meta screens at their frame cap; catches UI cost and battery waste |
| core_loop_typical | A median level or session segment |
| core_loop_worst | The heaviest content with all effects |
| transition_stress | Repeated scene or level loads; catches leaks and load hitches |
| background_resume | Background, wait, foreground cycles; catches state and memory issues |
| cold_start | Fresh process start to interactive; run N times for a distribution |
| soak | Looping real session for 45-50 minutes |

## 3. Running scenarios per engine

**Unity.** Use Performance Testing Extension tests (`[UnityTest, Performance]`) in a development player for per-frame sampling and custom metrics; batch-mode runs write results to JSON. For release-like numbers, add a lightweight in-game sampler (FrameTimingManager plus memory counters) enabled by a command-line or intent flag, which writes a CSV or perf-report JSON on exit; run it in a release build on the device. Keep two CI build flavours: development (profiling) and release (size, startup, evidence). The `templates/unity-mobile` template does not produce a perf report (its README marks the `perf` gate "not produced here"; its `Packages/manifest.json` already includes the Performance Testing package, 3.6.0 at the time of writing), so the sampler and the Performance Testing tests are yours to add. Its bot report cannot stand in for them: `PlaytestRunner.Run -gsMode bot` time metrics are a fixed 0.8 s per accepted move, not measurements. To measure sim cost, wrap `Playthrough.RunBots` or `Sim.Apply` in a Performance Testing `Measure.Method` test on the Core assembly.

**Godot.** For device evidence, add an autoload sampler that records frame time, `Performance` monitors and memory to JSON; trigger via a command-line user argument (`-- --perf-scenario=core_loop_worst`) in an exported release build. For regression checks and a first report, the template already ships `tools/perf/perf_probe.gd`, which plays the real game scene with a greedy bot and writes a perf-report JSON:

```
godot --path <project> -s res://tools/perf/perf_probe.gd -- --out=<abs>/perf.json [--seconds=20] [--budget-frame-ms=16.7] [--budget-memory-mb=512]
godot --headless --path <project> -s res://tools/perf/perf_probe.gd -- --out=<abs>/perf-headless.json [--seconds=20]
```

Exit codes: 0 pass, 1 budget violated, 2 usage or cannot run (for example when the windowed run never draws its window). The output is a perf-report (`schema_version` 1.0) with `device`, `scenario`, `duration_sec`, `fps` (`avg` and `p1_low`; windowed runs add `engine_avg` and `engine_min`, the rate the engine actually delivered), `frame_ms` (`p50`, `p95`, `p99`, `mean`, `max`, `warmup_max`), `memory_mb` (`peak`, `avg`, `basis`), `draw_calls`, `cpu_ms`, `gpu_ms`, `renderer`, `debug_build`, `budgets`, `violations`, `verdict` and `notes`. A windowed run on this Mac's Metal renderer (Godot 4.7.2) reported `draw_calls` 20.2, `cpu_ms` equal to the mean `frame_ms` and `gpu_ms` null. Point `--out` at `.gamestudio/reports/<feature-or-build>.<device>.perf.json`, pass `--feature F012` (your feature id), `--tier`, `--device-name` and `--build` to fill the metadata, and pass the contract's `technical.perf_budgets` through `--budget-frame-ms`, `--budget-memory-mb` and `--budget-fps` (the defaults are 16.7 ms, 512 MB and 60 fps).

How to read it: `frame_ms` is main-thread CPU work per frame without vsync, present or idle waits. Windowed it is scene processing plus render CPU plus frame setup, or the driver's GPU time when that is longer; headless it is scene processing only. `fps` is derived from `frame_ms` (what the measured cost could sustain), and `memory_mb` is process RSS where the OS allows it (`basis: "rss"`, else the engine's static plus video memory).

- **Headless runs are CPU-only.** There is no renderer, so the report sets `headless: true`, `device.name` to `desktop-headless`, `draw_calls` and `gpu_ms` to null, and adds a HEADLESS line to `notes`. They are good for logic and allocation regressions and are not valid evidence for a device. Add the engine flag `--fixed-fps 60` (before the `--` separator) with `--pace-fps=0` (after it) for an instant, deterministic run (20 s of game time took 0.6 s on 4.7.2); without the engine flag, `--pace-fps=0` only removes the probe's own pacing and the frame count is wall-clock bound.
- **Metal reports no GPU timing.** On a Metal renderer (macOS, iOS) the driver gives no GPU time, so `gpu_ms` is null and `frame_ms` is CPU-side only even when windowed; get GPU time from Xcode Instruments (see `references/profiling-toolkit.md`).
- **The windowed run needs a display and a real renderer** (on Linux CI wrap it in `xvfb-run -a`), keeps the project's own vsync and `max_fps`, and runs an editor or debug binary.

Both modes are desktop proxies; re-judge any report with `perf_budget.py --report <abs>/perf.json --contract .gamestudio/contract.json`. Options and caveats are in `${CLAUDE_PLUGIN_ROOT}/templates/godot-mobile/README.md`.

**Native Android/iOS wrapper layer.** Use `adb shell am start -W` for launch time, Perfetto for frame timeline, `dumpsys meminfo` for memory; on iOS use `xcrun xctrace` (verify) or an on-device sampler.

Capture sequence for a device run:
1. Install the release build; cool the device; set brightness and airplane or network mode.
2. Launch with the scenario flag; wait for the scenario to finish; pull the CSV or JSON from the device (`adb pull` or `xcrun devicectl` file copy, verify) .
3. In parallel, record thermal status and battery every few seconds with a host-side script.
4. Convert to a perf-report; run `perf_budget.py`.

## 4. Soak tests (45-50 minutes)

Why: Google's games guidance reports frame rates commonly degrade after about 45-50 minutes as the device heats; leaks and slow memory growth also only show over time.

Protocol:
1. Device: the low and mid reference devices, not on the charger (or on it, but record which; charging adds heat), screen brightness fixed, same case or no case across runs, room temperature recorded.
2. Workload: a looping bot session through the typical content mix, including menus, level starts, purchases dialogs (mocked), ads (test mode), and backgrounding at fixed intervals.
3. Duration: at least 50 minutes; for games meant to be played for hours, extend and note.
4. Sampling: frame times continuously, aggregated per 60 s window (p50, p95, p99, jank count); memory (PSS or total footprint) every 10 s; thermal status every 10 s; battery percent and temperature every 60 s; CPU and GPU frequency if available.
5. Report per-window series plus aggregate; compare the last 10 minutes with the first 10 minutes.

Pass criteria (proposals; set in the contract):
- p95 in the last 10 minutes within a stated percentage of the first 10 minutes (for example 15%) and still under the budget.
- Memory slope near zero: growth below a stated MB per 10 minutes after the first 5 minutes of settling.
- Thermal status never reaches severe on mid tier; no critical on low tier.
- No crash, ANR or forced restart; no unexpected process death.
- Battery drain per 30 minutes below the defined budget and not worse than the previous release by more than a threshold.

Interpretation:
| Observation | Likely cause | Next step |
|---|---|---|
| Frame time rises with thermal state | Sustained load | Add adaptation (see `optimization-and-thermal.md`), lower defaults |
| Frame time rises with memory | Leak or fragmentation | Memory snapshot diff, find the growing category |
| Periodic spikes at constant interval | Timers, autosave, GC, network polling | Correlate with events; spread work |
| Drain high but fps fine | Wasted frames | Cap fps, render on demand, reduce wakeups |
| Crash at a late time | Memory limit | Memory budget and low-memory handlers |

## 5. Device farms

Use farms to extend coverage across models; do not use them as the only low-tier device.

| Service | Strength for games | Notes (pricing volatile; see section 12) |
|---|---|---|
| Firebase Test Lab | Game Loop tests on Android and iOS: run a scripted demo loop across many physical devices and collect logs, crashes and video without an external driver | Pricing is third-party reported; verify |
| AWS Device Farm | Per-minute or unmetered slots on real devices | Only service whose price was verified against its pricing page in research |
| BrowserStack App Automate | Broad device list, parallel sessions | Price from third-party sources; verify |
| Sauce Labs | AltTester and Appium on real devices | See `qa-testing` for functional use |

What farms can and cannot do for perf: they reliably provide crashes, ANRs, logs and screenshots across models, and basic timing. Whether a given farm exposes Perfetto traces, `dumpsys` output or GPU counters varies and was not verified; check before you design a pipeline that depends on it. For thermal truth, rely on your own devices; farm devices are often cooled and idle between sessions, so thermals are optimistic.

Farm strategy:
1. Device list from your tier matrix plus the top devices in your analytics by active users and by crash share.
2. Run the cold-start and core_loop_worst scenarios on every device per release candidate, the full set nightly or weekly.
3. Compare each device against its own baseline (regression) and against the tier budget (absolute).
4. Pull crash stack traces and symbolicate (see `qa-testing`).

## 6. The perf-report schema

Reports are JSON files at `.gamestudio/reports/<feature-or-build>.<device>.perf.json` (evidence name `perf.json`). Validate with `${CLAUDE_PLUGIN_ROOT}/scripts/schemas/perf-report.schema.json`.

| Field | Meaning |
|---|---|
| `schema_version` | Always "1.0" |
| `feature_id`, `build` | What was measured; use a release build id |
| `device` {name, tier, os} | Where; tier is low, mid or high; "editor" or "desktop-headless" mark proxies |
| `scenario`, `duration_sec` | Workload and window (60 s or more recommended) |
| `fps` {avg, p1_low} | Frame rate and 1% low |
| `frame_ms` {p50, p95, p99} | Percentiles in ms |
| `memory_mb` {peak, avg} | Resident memory |
| `draw_calls`, `cpu_ms`, `gpu_ms` | Optional render stats |
| `thermal` {start, end} | State labels, Android status number or temperature |
| `download_mb`, `cold_start_sec` | Install size and startup |
| `budgets` | Budgets used (copy from contract) |
| `violations` | Human-readable list; must be empty for pass |
| `verdict` | "pass" or "fail"; pass requires empty violations |
| `notes` | Method, profiler, caveats |

Producers: the Godot template's `tools/perf/perf_probe.gd` writes this shape. Its windowed and headless reports both validate against the schema (`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_json.py --auto <name>.perf.json`) and `perf_budget.py` accepts them (checked with Godot 4.7.2). It adds probe-specific keys that the schema allows (`headless`, `renderer`, `debug_build`, `frames_over_budget`, `fps.engine_avg`, `frame_ms.mean`, `max` and `warmup_max`, `memory_mb.basis` and `engine_peak`). Pass `--frames` to embed the raw `frames_ms` series; without it `perf_budget.py` reports frame count and jank as `None` because it has only the summary values. Unity has no producer in its template, so a Unity project writes this shape from its own sampler or from Performance Testing results.

You may also include a `frames_ms` array (per-frame times) so the checker can recompute statistics instead of trusting reported percentiles.

Minimal example:
```json
{
  "schema_version": "1.0",
  "build": "0.4.0+abc1234 (release, Android arm64)",
  "device": {"name": "Reference low", "tier": "low", "os": "Android 13"},
  "scenario": "core_loop_worst, 120 s after 10 s warmup",
  "duration_sec": 120,
  "fps": {"avg": 29.8, "p1_low": 24.0},
  "frame_ms": {"p50": 33.3, "p95": 34.1, "p99": 41.0},
  "memory_mb": {"peak": 640},
  "budgets": {"fps_target": 30, "frame_ms_p95": 33.3, "memory_mb": 900},
  "violations": ["frame_ms.p95 34.1 > 33.3"],
  "verdict": "fail"
}
```

## 7. perf_budget.py

`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/perf_budget.py --report <file> [--contract <contract.json>] [--json]`

- Input: a CSV of frame times in ms (one column, or a header column named frame_ms, frametime, frame_time, frametime_ms, ms or dt_ms), or a perf-report JSON (uses `frames_ms` if present, otherwise reported values).
- Statistics: average fps = 1000 / mean frame ms; 1% low = fps of the mean of the slowest 1% of frames; p50, p95, p99 by linear interpolation; jank = frames slower than 2x the median.
- Budgets from `--contract` (`technical.perf_budgets`) or the report's own `budgets`: `fps_target` (average fps must be at least 0.95 x target), `frame_ms_p95`, `memory_mb`, `download_mb`, `cold_start_sec`. A budget with no measurement is reported as skipped, never as a pass.
- Exit codes: 0 pass or no budgets, 1 a budget failed, 2 usage or input error. `--selftest` runs built-in fixtures.
- Without budgets the verdict is "no-budgets" with exit 0; do not treat that as a pass in a gate. Always supply budgets.

Typical use in CI:
```bash
python3 "$PLUGIN/scripts/perf_budget.py" --report out/low.perf.json --contract .gamestudio/contract.json --json > out/low.verdict.json || echo "perf gate failed"
```

## 8. Regression tracking

Absolute budgets catch big failures; regression tracking catches slow drift.

1. Store every perf report per build in an artifacts folder or a small database keyed by build, device, scenario.
2. Baseline: the median of the last N passing builds (N of 5 is a reasonable start) per device and scenario.
3. Regression rule: fail or warn when p95 frame time rises by more than a tolerance relative to baseline (choose from your measured run-to-run noise; if two runs of the same build differ by 3%, a 5% threshold would flap, so measure noise first), or when memory peak, download size or cold start rise beyond their own thresholds.
4. Report deltas in the PR or build summary: metric, baseline, current, change, link to report.
5. When a regression is real, bisect over builds using the stored reports before profiling, which usually isolates the change in minutes.
6. Re-baseline deliberately (a commit that says why), never by editing thresholds in the same change that regressed.

Noise control: same device, same scenario, cooled start, a median of three runs for gating, and treat a single outlier run as a re-run trigger, not a failure.

## 9. CI pipeline shape

```
build release + dev flavours
  -> static checks: size by type, native lib alignment, asset rules, texture compression
  -> unit and headless sim tests (fast)
  -> editor/desktop perf proxy (warn only)
  -> device or farm: cold_start + core_loop_worst on low tier (gate)
  -> nightly: full scenario set across the farm, soak on dedicated devices
  -> perf_budget.py per report -> verdict JSON
  -> upload reports as artifacts, update trend dashboard, comment on PR
```

CI templates live under `templates/ci/` (GitHub Actions for Godot and Unity, fastlane, Codemagic). Physical-device steps usually need a self-hosted runner with attached devices or a farm API call.

## 10. Failure triage and flakiness

| Symptom | Likely cause | Action |
|---|---|---|
| Run-to-run swing above tolerance | Warm device, background processes, variable brightness | Cool between runs, fixed protocol, median of three |
| Only the first run is slow | Shader compile or cache fill | Count as cold; add prewarm; exclude from steady-state stats but keep in cold-start metrics |
| Farm device slower than own device | Different OS build, other tenants, thermal state | Compare against farm baseline of that device only |
| Passing locally, failing in CI | Debug versus release build, different tier setting | Align build flavour and forced tier |
| Failing only on one model | Driver or GPU quirk | Vendor profiler on that device; consider tier override |

## 11. Worked example

Contract: `fps_target 30`, `frame_ms_p95 33.3`, `memory_mb 900`, `download_mb 150`, `cold_start_sec 5` on the low tier.
1. Nightly job runs `core_loop_worst` for 120 s on the low device and writes `low.perf.json` with `frames_ms`.
2. `perf_budget.py` recomputes p95 = 34.0 ms: fails by 0.7 ms; exit 1; violation listed.
3. Trend shows p95 was 31.5 ms five builds ago; stored reports allow a bisect: the jump coincides with a build that added a full-screen vignette post-process.
4. Fix: drop the vignette on the low tier (baked into the UI frame art instead); p95 returns to 31 ms.
5. The soak runs that night; last-10-minute p95 is within the stated tolerance of the first 10; memory slope flat; gate green.

## 12. Volatile facts (as of Oct 2026 — verify)

| Fact | Source |
|---|---|
| Firebase Test Lab supports Game Loop tests (iOS and Android) alongside instrumentation and Robo tests; third-party reports about $1 per virtual-device-hour and $5 per physical-device-hour on Blaze with a small free daily quota | https://blog.back4app.com/firebase-test-lab/ ; https://www.drizz.dev/post/firebase-test-lab-guide |
| AWS Device Farm reported at $0.17 per device-minute or $250 per slot per month unmetered | Verify on the AWS Device Farm pricing page (research notes section 7) |
| BrowserStack App Automate reported from about $199 per month per parallel (third-party) | Verify on BrowserStack's pricing page |
| Google reports frame rates often degrade after 45-50 minutes of play | https://developer.android.com/games/optimize |
| Unity Performance Testing package writes JSON and builds a development player | https://docs.unity3d.com/Packages/com.unity.test-framework.performance@3.0/manual/index.html |
| Perfetto Trace Processor Python API | https://perfetto.dev/docs/analysis/trace-processor-python |
| Arm Performance Advisor reports in CI | https://developer.arm.com/community/arm-community-blogs/b/mobile-graphics-and-gaming-blog/posts/what-is-arm-performance-studio |
