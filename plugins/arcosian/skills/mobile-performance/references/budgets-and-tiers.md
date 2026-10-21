# Budgets and Device Tiers

This file tells you how to set the numbers a mobile game is held to: frame time, memory, thermal and battery behaviour, download size and startup, per device tier. The numbers here are working defaults from practice and from Google's public games guidance; anything dated or device-specific is isolated in the "Volatile facts" section. Treat suggested thresholds as proposals to tune against your own game and your own reference devices, and always write the final numbers into the design contract so the perf gate can enforce them.

## Contents
1. Why budgets come first
2. Frame-time budgets
3. Choosing the tier matrix
4. Memory budgets
5. Thermal and battery
6. Download size and install footprint
7. Startup and load time
8. Budget worksheet and worked example
9. Budget review checklist
10. Volatile facts (as of Oct 2026 — verify)

## 1. Why budgets come first

A budget turns "make it fast" into a pass/fail check. Without one, optimization has no stopping point and regressions have no alarm. Set budgets at the start of the vertical slice, not at the end of production, because architecture (pooling, streaming, atlas strategy) is cheap to choose early and expensive to retrofit.

Rules:
- One budget set per tier, not one global set.
- Budgets apply to a named worst-realistic scenario ("level 30, wave 10, max VFX"), not to an empty menu.
- Every budget has an owner metric in the perf report and a test that fails when it is exceeded.
- Budgets move only by an explicit decision recorded in the contract, never by quietly editing the test.

## 2. Frame-time budgets

| Target fps | Frame interval | Typical genres | Notes |
|---|---|---|---|
| 30 | 33.3 ms | puzzle, idle, card, board, turn-based, narrative | Lowest power; late frame costs a full extra 33 ms |
| 60 | 16.6 ms | action, runner, shooter, rhythm, anything with continuous touch tracking | Default for responsiveness-critical play |
| 90/120 | 11.1 / 8.3 ms | rare on mobile; only on devices that advertise it | Needs an explicit battery and thermal decision |

How to turn the interval into per-thread budgets. Frame time is the slowest pipeline stage, so give each stage its own ceiling with headroom, because frames also lose time to the OS compositor and to variance:

| Stage | Budget rule of thumb at 60 fps | At 30 fps |
|---|---|---|
| Main thread (game logic + script) | about 8-10 ms | about 16-20 ms |
| Render thread (draw submission) | about 6-8 ms | about 12-16 ms |
| GPU | about 10-12 ms on the reference device | about 20-24 ms |
| UI update | 2-3 ms (Google's games guidance) | 2-3 ms |

These are planning heuristics; the contract-level numbers are `fps_target` and `frame_ms_p95`. Gate on:
- p95 frame time at or under budget (33.3 ms on the low tier is the research-suggested ceiling; 16.6 ms on mid and high).
- Average fps at least 0.95 x target (that is the tolerance `perf_budget.py` applies for capture noise).
- 1% low fps: define your own floor; a common practice is 1% low at no worse than about 70-80% of target. Mark that as a project decision.
- Jank: frames slower than 2x median frame time; track the count per minute and fail on a threshold you choose.

Frame pacing: a game that renders in 14 ms but presents frames unevenly feels worse than one at a locked, even interval. Use the platform frame-pacing facility (Android Frame Pacing library, engine vsync settings, iOS CADisplayLink/preferred frame rate) and measure frame-to-frame delta variance, not just render time.

## 3. Choosing the tier matrix

Tier = a hardware class you budget for and test on. Keep it to three.

| Tier | Definition (proposal) | Role |
|---|---|---|
| Low | The weakest device you still promise to support: low RAM, older GPU, throttles early | Decides crash rate, review scores in cheap-phone markets, memory design |
| Mid | The median active device in your target markets | Primary tuning target; quality settings default here |
| High | Recent flagship | Headroom for polish, higher resolution scale, optional 60 fps |

Selection procedure:
1. Pull active-device distribution by RAM, GPU family, OS version and chipset from your store console or analytics if live; for pre-launch use soft-launch market data.
2. Define the support floor by RAM and OS first (ex: RAM floor, OS floor), then pick one physical device sitting at that floor.
3. Pick a median-market device for mid and a current flagship for high. Include at least one Android device with a different GPU vendor than the others (Adreno, Mali, PowerVR/Immortalis families behave differently).
4. Include one older iPhone that is still supported by your minimum iOS target, because the iOS floor is often lower than people expect.
5. Buy or borrow real devices for low and mid. Farms (see `perf-testing-automation.md`) extend coverage but do not replace the low-tier device on your desk.
6. Map tiers to settings (resolution scale, texture quality, effect LOD, shadow, frame target, particle caps) and make the mapping data-driven so a tier can be added without code changes.

Android specifics: do not equate tier with "year". Cheap new phones ship with old GPUs and small RAM. Use a capability probe (RAM, GPU renderer string, Vulkan/GLES level) to assign a tier at first launch, with a remote-config override so a bad guess can be fixed live.

## 4. Memory budgets

Define two numbers per tier: peak resident memory budget (`memory_mb` in the contract) and a leak slope (MB growth per 10 minutes of steady play, target near zero).

| Tier | Peak memory budget as a share of physical RAM | Rationale |
|---|---|---|
| Low | about 25-30% | OS, other apps and the compositor take most of a 2-3 GB device; the research notes suggest staying under about 1 GB on 3 GB devices |
| Mid | about 30-35% | More headroom, but background apps still contend |
| High | about 35-40% | iOS jetsam limits and Android low-memory killer still apply |

These fractions are proposals. The real ceiling is per-device and per-OS-version; confirm by pushing a test build to exhaustion on the reference device and recording where it is killed, then budget 20-30% below that.

Where memory goes in a typical 2D mobile game, in rough order: textures (largest), audio (decoded music and long SFX), meshes and animation data, managed heap (C# or GDScript objects), engine and native plugin overhead, UI. Texture math:
- Uncompressed RGBA32: width x height x 4 bytes. A 2048x2048 texture is 16 MB; with a full mip chain add about 33% (Google's textures guidance).
- ASTC and ETC2 compressed formats are a fraction of that (ASTC block size sets the ratio: 4x4 is 8 bpp, 6x6 is about 3.6 bpp, 8x8 is 2 bpp). ETC2 RGBA is 8 bpp.
- Audio: a 60 s stereo 44.1 kHz clip decoded to 16-bit PCM is about 10 MB. Stream music; decode short SFX once into memory only if used often.

Rules:
1. Budget textures explicitly per scene (a table of atlas names and sizes), not as an afterthought.
2. Unload what the next scene does not need before loading what it does, or peak is the sum of both.
3. Test backgrounding and returning with other apps open; the app can be killed in the background and must restore state.
4. Track managed heap separately from total; heap growth plus GC pauses is its own failure mode.

## 5. Thermal and battery

Thermal state is a budget dimension because it shrinks every other budget over time.

| Signal | Android | iOS |
|---|---|---|
| Discrete state | Thermal API status, NONE through SHUTDOWN (API 30+) | ProcessInfo thermal state: nominal, fair, serious, critical |
| Predictive | ADPF `getThermalHeadroom()` forecasts headroom before severe throttling | None equivalent; rely on state notifications and own frame-time trend |
| Perf hints | Performance Hint API (API 31+) | Game Mode, preferred frame rate |

Budget rules:
- Define a thermal end-state budget: after the 45-50 minute soak the status must not exceed a threshold you choose (a sensible default is "never reach severe on mid tier; never reach critical on low tier"), and p95 frame time in the last 10 minutes must stay within a stated percentage of the first 10 minutes (for instance 15%; project decision).
- Define a battery budget: percent drain per 30 minutes at the standard brightness setting on a fixed device. Measure with the platform battery stats; compare builds to each other rather than to absolute claims.
- Cheap wins in order: cap frame rate to the design target (never render 120 fps for a 30 fps game), render only on change for static screens, lower resolution scale on low tier, reduce particle counts and post-process passes, avoid keeping radios and sensors active without need.
- Screen brightness and charging while playing change thermals dramatically; fix both in test protocol and record them in the report notes.

## 6. Download size and install footprint

| Budget | What to define | Notes |
|---|---|---|
| Install download (store-delivered) | `download_mb` in contract | Smaller installs convert better and survive weak connections; choose a number for your market |
| Installed size | Separate number | Uncompressed assets on disk; users uninstall big apps when storage is low |
| First-session download | Content fetched after install | Keep the first session playable from the install pack |
| Mobile-data cap | Size above which you wait for Wi-Fi | Product decision |

Delivery tools (volatile; see section 10): Play Asset Delivery for larger Android games with install-time, fast-follow and on-demand packs; Apple Background Assets for iOS on-demand content. Install-time packs count toward the base install and need free space of roughly twice their size during install, so keep them small.

Size budgeting by type: allocate a share of the budget to textures, audio, code and native libraries, meshes and data. Track each in CI so growth is attributed to a type, not just a total.

## 7. Startup and load time

Define three timestamps and budget each:
1. Cold start to first frame (splash visible).
2. Cold start to interactive (player can act); this is `cold_start_sec` in the contract.
3. Warm resume from background to interactive.

Rules of thumb:
- Anything beyond a few seconds to interactive risks early drop-off; set the number from your own funnel data once available.
- Initialize only what the first screen needs. Defer analytics, ads, remote config, store SDKs and heavy asset loads until after interactive, or run them on background threads.
- Test cold start on the low tier with a cleared cache and also with a first-ever install (first-run shader compilation, asset import and permission prompts all add time).
- Scene transitions get a budget too: under a second for common transitions, with a progress or skeleton state when longer.

## 8. Budget worksheet and worked example

Worksheet (copy into the contract):

| Field | Low tier | Mid tier | High tier |
|---|---|---|---|
| Reference device | | | |
| fps_target | | | |
| frame_ms_p95 | | | |
| memory_mb (peak) | | | |
| download_mb | | | |
| cold_start_sec | | | |
| thermal end state | | | |
| scenario | | | |

Worked example. A 2D merge puzzle game, portrait, target markets include cheap Android.
- fps_target 30 on low, 60 on mid and high (animation smoothness on drags is a feel feature).
- frame_ms_p95: 33.3 low, 16.6 mid/high.
- Low device has 3 GB RAM: memory budget about 0.3 x 3072 = roughly 900 MB; measured kill point on the device was found at a higher number, so 900 MB leaves safety margin.
- Texture plan: five atlases of 2048x2048 ASTC 6x6 at about 3.6 bpp is about 1.9 MB each, so about 10 MB for atlases; the budget is dominated by audio and engine overhead, not art. That changes where optimization effort goes.
- Download: pick the number from market research (for instance, "stay under a size users on mid-range plans accept without Wi-Fi") and enforce it in CI.
- Soak: 45-minute session loop on low and mid devices with a bot, thermal and battery logged.

Contract fragment:
```json
"technical": { "perf_budgets": {
  "fps_target": 30, "frame_ms_p95": 33.3,
  "memory_mb": 900, "download_mb": 150, "cold_start_sec": 5
} }
```
(Numbers illustrative; replace with measured values for your game.)

## 9. Budget review checklist

- [ ] Three reference devices named, physically available, and recorded in the device matrix.
- [ ] fps target justified by genre and battery, not by habit.
- [ ] frame_ms_p95 consistent with fps_target.
- [ ] Peak memory budget below a measured kill point with margin.
- [ ] Texture and audio memory plan exists per scene.
- [ ] Download budget and delivery strategy (single pack or split) chosen.
- [ ] Cold start budget measured on a first-ever install on the low tier.
- [ ] Thermal end state and battery drain budgets defined with a fixed test protocol.
- [ ] Every budget maps to a perf-report field and an automated check.
- [ ] Scenario for each budget written down.

## 10. Volatile facts (as of Oct 2026 — verify)

| Fact | Source |
|---|---|
| No industry-standard Android minimum spec in 2026; per-title floors cluster around 2-4 GB RAM, Android 7-8+, Adreno 306-530 class GPUs at the low end (examples: BGMI Lite targets 1.5 GB RAM and Adreno 306; Fortnite needs 4 GB with Adreno 530 or Mali-G72 MP12) | Research notes section 7, device-coverage survey of per-title requirements; verify on each title's store page |
| ASTC supported on over 75% and ETC2 on over 90% of active Android devices; mipmaps add about 33% memory | https://developer.android.com/games/optimize/textures |
| Thermal API from Android 11 (API 30), Performance Hint API from Android 12 (API 31) | https://developer.android.com/stories/games/mediatek-adpf |
| Frame rates often degrade after 45-50 minutes; UI update budget 2-3 ms; late frame at 30 fps costs an extra 33 ms | https://developer.android.com/games/optimize |
| Play Asset Delivery replaces OBBs for games over 200 MB; install-time packs need about 2x their size in free space | https://developer.android.com/guide/playcore/asset-delivery |
| Apple On-Demand Resources called legacy and slated for deprecation at WWDC25; Background Assets is the successor | https://developer.apple.com/videos/play/wwdc2025/325 |
| Google Play 16 KB page-size requirement for new apps and updates targeting Android 15+ (dates reported on Unity forums; verify) | https://discussions.unity.com/t/google-play-16kb-page-size-requirements/1681037 |

## Appendix: tier-to-settings map (starting point)

Keep this table as data (a config resource or ScriptableObject) so QA can force any tier on any device.

| Setting | Low | Mid | High |
|---|---|---|---|
| Frame target | 30 (or 60 only if the budget holds) | 60 or 30 per genre | 60 |
| Render resolution scale | 0.6-0.8 of native, UI at native | 0.8-1.0 | 1.0 |
| Texture quality | Half-resolution mip bias on large art | Full | Full |
| Particle cap and quad size | Strict cap, small quads | Moderate | Generous |
| Post-processing | Off or a single cheap pass | One or two cheap passes | Full chain within GPU budget |
| Shadows | Off or blob shadows | Simple | Simple to soft |
| Audio voices | Lower voice cap, mono SFX | Standard | Standard |
| Dynamic resolution and thermal adaptation | On, aggressive | On | On, gentle |

Procedure to validate a tier mapping: force each tier on the low device and on the high device; the low device on the low preset must meet the low budget, and the high preset must not be selectable on it. If a preset only passes on the device it was designed for, the tier boundary is in the wrong place.
