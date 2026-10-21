---
name: optimize
description: Runs a mobile performance pass against the contract's budgets - frame time, memory, download size, cold start, thermals - with per-engine profiling, device tiers, perf_budget.py checks, a prioritized fix checklist and a perf report that sets the perf gate. Use when the user says "optimize performance", "it stutters", "too much memory", "build is too big", "check the perf budget", or "why is it hot".
argument-hint: "[F### | scenario | device tier]"
---

# Optimize

Measure first, fix the largest cost, measure again. Budgets come from the contract, not from taste.

## When to use

- A feature reaches the `perf` gate (see `build-feature`).
- Reports of stutter, heat, crashes on low-end devices, slow launch, or oversized builds.
- Before soft launch, before a release candidate, after adding content or SDKs.

## Inputs

`$ARGUMENTS`: a feature id (profile its scenario), a named scenario, or a device tier (`low|mid|high`). Default is the reference scenario on the lowest available tier. Delegate profiling and fixes to `arcosian:performance-engineer`; engine work to `arcosian:godot-engineer` or `arcosian:unity-engineer`. Load `mobile-performance`, plus `engine-godot` or `engine-unity`.

## Budgets

Read `contract.technical.perf_budgets`; do not invent replacements.

| Key | Meaning | Measure |
|---|---|---|
| `fps_target` | Target frame rate (commonly 30 or 60) | avg and 1 percent low |
| `frame_ms_p95` | 95th percentile frame time | frame time capture over the scenario |
| `memory_mb` | Peak resident memory | platform memory tool at peak scene |
| `download_mb` | Install/download size | built artifact size |
| `cold_start_sec` | Launch to interactive | cold launch after force-quit, median of several |

If a key is missing, ask `arcosian:lead-engineer` to propose it and record it in the contract before measuring. Sanity: `frame_ms_p95` must be at or below `1000 / fps_target`, and p95 matters more than average because players feel spikes.

## Device tiers

Define three reference devices in `.gamestudio/config.json` notes or the report: **low** (oldest and weakest you still support, from `min_spec`), **mid** (typical in your target markets), **high** (current flagship, for headroom only). Budgets must pass on **low**. Profile on real hardware; simulators and editors mislead about GPU, thermals and memory. Also test after 10 or more minutes of play, because thermal throttling shows up late.

## Procedure

1. **Pick the scenario.** The worst plausible gameplay moment (busiest screen, most effects, biggest level) plus a 60-second steady-state run and one cold launch. Write it down so it is repeatable.
2. **Capture a baseline** on the low tier and save to `.gamestudio/evidence/<ID>/` (`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py evidence-dir F012`) or `.gamestudio/reports/`. Record build id, device, OS, scenario, duration.
3. **Profile by engine.**

   | Engine | Tools | Look for |
   |---|---|---|
   | Godot 4 | built-in Profiler, Monitors (frames, memory, draw calls, objects), Visual Profiler for GPU, `--print-fps` | per-frame script cost, node count, draw calls, unfreed resources |
   | Unity 6 | Profiler (CPU, GPU, Memory), Memory Profiler package, Frame Debugger, Profile Analyzer, Build Report | GC allocs per frame, SetPass/batches, overdraw, texture memory, build size by asset |
   | iOS | Xcode Instruments (Time Profiler, Metal System Trace, Allocations), MetricKit for field data | main-thread stalls, GPU time, memory peaks, thermal state |
   | Android | Android Studio Profiler, Perfetto, GPU inspector tools from the vendor, Play Console vitals | jank, CPU big/little scheduling, memory, ANRs |

   Tool names and menus change between versions; check current docs for your version.
4. **Build the report** as `perf-report` JSON (`device`, `scenario`, `fps`, `frame_ms` p50/p95/p99, `memory_mb`, `draw_calls`, `cpu_ms`, `gpu_ms`, `thermal`, `download_mb`, `cold_start_sec`). If you only have frame times, a CSV of milliseconds works.
5. **Check budgets.**
   ```
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/perf_budget.py --report .gamestudio/evidence/F012/perf.json --contract .gamestudio/contract.json --json
   ```
   Exit 0 means within budget; exit 1 lists `violations`; exit 2 is bad input.
6. **Classify the bottleneck** before fixing: CPU-bound (main thread or script ms high, GPU idle), GPU-bound (gpu_ms high; fill-rate or shader), memory-bound (peak near limit, GC or alloc spikes), IO/load-bound (cold start, hitches on scene load), size-bound (download).
7. **Fix in priority order** (below), one change per measurement, re-run step 4-5 after each.
8. **Set the gate** only from a passing report on the low tier:
   ```
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py feature gate F012 perf pass --evidence .gamestudio/evidence/F012/perf.json
   ```
   On failure record `fail` with a note; do not use `n/a` for anything that touches runtime.

## Prioritized fix checklist

1. **Allocations in the frame loop**: pool objects, reuse buffers, avoid string building and LINQ/array churn per frame, cache lookups.
2. **Draw calls and overdraw**: atlas sprites and UI, batch, cut transparent full-screen layers, limit particle overdraw.
3. **Update work**: move logic off per-frame polling to events; step sim-core at a fixed rate; skip offscreen entities.
4. **Textures**: right-size, compress with platform formats, drop mip levels you do not need, unload unused scenes' assets. See `technical-art`.
5. **Shaders and post-processing**: remove expensive full-screen effects on low tier; provide a quality switch.
6. **Physics and pathfinding**: lower rates, simplify colliders, query less often.
7. **Loading**: async load, preload next level during idle, defer SDK init off the launch path (analytics, ads, attribution).
8. **Audio**: compressed streams for music, short samples in memory, cap voices.
9. **Download size**: strip unused assets and code, compress audio and textures, split on-demand content, audit dependencies.
10. **Thermals and battery**: cap frame rate to `fps_target`, reduce work when idle or in menus, avoid constant redraw of static screens.

Sensitive rule: never trade away a visible quality tier for the low device silently; add a graphics-quality setting and record the decision.

## Outputs

`.gamestudio/evidence/<ID>/perf.json` or `.gamestudio/reports/perf-<date>.json` (schema `perf-report`), a short Markdown perf summary (baseline, changes, after table, remaining risks), updated feature gate, `progress.md` entry.

## Quality gates

- Measured on real low-tier hardware, build id and scenario recorded, at least one 10-minute thermal run before release.
- `perf_budget.py` exits 0 against the contract budgets; violations list is empty.
- Each fix has a before/after number; no unmeasured "optimizations".
- No regression in gameplay tests: rerun the `unit` and `playthrough` gates after changes.

## Failure modes and recovery

| Symptom | Recovery |
|---|---|
| Fast in editor, slow on device | Profile on device; editor numbers are not evidence. |
| Averages pass, players report stutter | Check p95/p99 and GC spikes, not the mean. |
| Fix helps one device, hurts another | Keep the per-tier numbers in the report; gate on the low tier. |
| Cannot hit budget without cutting content | Escalate to `arcosian:producer` and `arcosian:lead-engineer`: change scope, tier, or the budget in the contract explicitly. |
| `perf_budget.py` rejects the report | Validate with `gs.py validate`; check units (ms vs fps). |

## Related skills

`mobile-performance`, `technical-art`, `game-architecture`, `engine-godot`, `engine-unity`, `build-feature`, `qa-testing`.
