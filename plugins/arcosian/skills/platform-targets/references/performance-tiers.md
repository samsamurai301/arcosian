# Performance tiers

This reference sets performance budgets per hardware tier: frame time, memory, draw calls and download or install size, for low-end and high-end phones, Steam Deck, integrated-GPU laptops, mid and high PCs, the web, and current consoles (public figures only). It explains how to write PC minimum and recommended specs from the Steam Hardware Survey and how to test each tier. Figures marked "estimate" are starting points to be replaced by measurements; figures with a source were checked in Oct 2026. Mobile profiling depth is in `mobile-performance`; general optimisation is in `optimize`.

## Contents

1. Frame time arithmetic and how to use budgets
2. Mobile tiers
3. Steam Deck
4. PC tiers: integrated-GPU laptops, mid, high
5. Web tiers
6. Consoles (public information)
7. Writing PC minimum and recommended specs from the Steam Hardware Survey
8. How to test each tier
9. Budget table to copy into the contract

## 1. Frame time arithmetic and how to use budgets

| Target | Frame time | Notes |
|---|---|---|
| 30 fps | 33.3 ms | Acceptable for slow games and weak devices; needs consistent frame pacing |
| 40 fps | 25 ms | Fits a 120 Hz display (every third refresh); popular on Steam Deck |
| 60 fps | 16.7 ms | Default for action games |
| 90 fps | 11.1 ms | Some handhelds, VR |
| 120 fps | 8.3 ms | High-refresh phones and consoles |
| 144 fps | 6.9 ms | PC monitors |

Use these rules:

1. Set the budget for the **weakest supported tier**, then check the stronger tiers just scale up.
2. Budget **p95 frame time**, not average. Players feel the spikes. The contract field is `technical.perf_budgets.frame_ms_p95`. Also track 1 percent low fps on PC.
3. Leave 20 to 30 percent headroom for thermal throttling and background load on mobile and handhelds (estimate). A mobile game that hits 60 fps for 30 seconds and then throttles to 40 is not a 60 fps game.
4. Split the frame: CPU main thread, render thread, GPU. The slowest of the three sets the frame time; optimise that one. A typical split target at 60 fps: game logic 5 ms, rendering CPU 4 ms, GPU 12 ms, with overlap (estimate).
5. Frame pacing matters as much as average: uneven 16 and 33 ms frames look worse than a steady 30 fps. Use a cap that divides the display refresh (30, 40 or 60 on 120 Hz, 30 on 60 Hz).
6. Memory budgets: leave headroom for the OS. Exceeding it on mobile and console leads to the OS killing the app with no warning; on PC it leads to paging and stutters.
7. Record every budget with its tier and device in the contract (`technical.min_spec`, `technical.perf_budgets`), and produce a `perf-report` as gate evidence (`mobile-performance`, `optimize`).

Draw calls and triangle counts are engine and renderer dependent; the figures below are estimates that depend on batching, instancing and shader cost. Measure with the engine profiler and a GPU capture tool; the shader cost per pixel and overdraw usually matter more than raw counts.

## 2. Mobile tiers

Tiers change yearly. Define tiers by devices you can buy and test, not by names in this file. The table is a starting estimate.

| Tier | Example profile (estimate) | RAM | Frame target | Per-frame GPU | Practical memory budget | Draw calls (2D / 3D) | Install size target |
|---|---|---|---|---|---|---|---|
| Low-end phone | Android with 2 to 3 GB RAM, older mid-range SoC, 720p to 1080p screen, no sustained GPU headroom | 2 to 3 GB | 30 fps (60 for 2D simple) | 20 ms | 300 to 500 MB resident (leave the rest to the OS) | under 100 / under 150 | under 150 MB initial, stream the rest |
| Mid phone | 4 to 6 GB, mid-range SoC from the last three to four years | 4 to 6 GB | 60 fps 2D; 30 to 60 3D | 12 to 14 ms | 700 MB to 1 GB | under 200 / under 300 | under 300 MB initial |
| High-end phone | Flagship from the last two years, iPhone recent models | 8 GB and up | 60 to 120 fps | 8 to 12 ms | 1.5 to 2 GB | under 400 / under 600 | Up to store limits; consider asset packs |
| Tablet | Similar to phones with more pixels | 4 to 16 GB | 60 fps | resolution scale to hold the budget | like the phone tier, plus larger textures | same | same |

All values are estimates. iOS and Android enforce different memory kill thresholds that depend on device RAM and other apps; measure with the platform tools and treat the first out-of-memory termination as the real limit (`mobile-performance`).

Specifics:

- **Thermals and battery** are the real limit: a sustained 60 fps in a 3D game heats and drains quickly. Offer a battery saver or 30 fps mode. Measure for at least 20 to 30 minutes, not 30 seconds.
- **Resolution**: render the 3D scene below native on high-density screens (for example 0.7 to 0.85 scale) and keep the UI native.
- **Texture memory**: use ASTC on modern iOS and Android GPUs (verify device support), ETC2 as the baseline fallback in Android with GLES 3; no uncompressed 2048 textures for sprites that are 128 px.
- **Android 16 KB pages**: for apps with native code (Unity and Godot builds include native libraries), 16 KB page size support is required for Play updates targeting Android 15 or above from 1 February 2027 (source: https://developer.android.com/guide/practices/page-sizes). Rebuild with NDK r28 or later (16 KB alignment is the default there), test on a 16 KB image, and check ELF alignment of plugin libraries.
- **Minimum OS**: Unity 6 supports Android 6.0 (API 23) and iOS 13 or later (source: Unity 6 system requirements, https://docs.unity3d.com/6000.0/Documentation/Manual/system-requirements.html). Your own floor should be higher and set by the audience share you want and the store requirements (`store-release`).
- **Download size**: store limits and cellular-download behaviours change; take them from `store-release`. Practical rule: keep the first download under about 150 MB, since larger downloads lose installs on cellular networks (estimate); fetch the rest with asset packs or on-demand downloads.
- **Cold start**: under 3 to 5 seconds to the first interactive screen (estimate; `contract technical.perf_budgets.cold_start_sec`).

## 3. Steam Deck

Source for hardware: https://www.steamdeck.com/en/tech/deck (LCD model). Zen 2 CPU, 4 cores and 8 threads at 2.4 to 3.5 GHz; GPU with 8 RDNA 2 compute units at 1.6 GHz, about 1.6 TFLOPS FP32; 16 GB LPDDR5 shared between CPU and GPU; 7 inch 1280x800 screen at 60 Hz; 40 Wh battery; 4 to 15 W APU power draw. The OLED model has a different screen and battery (I recall 7.4 inch, up to 90 Hz and 50 Wh, unverified here); the APU class is the same, so budget for the LCD model.

| Item | Budget |
|---|---|
| Valve's bar for Verified | 30 fps at 800p on default settings (source: https://partner.steamgames.com/doc/steamdeck/compat) |
| Better target | 40 fps with the 40 Hz refresh option or a locked 60 fps for action games |
| Frame time | 25 ms (40 fps) or 16.7 ms (60 fps); 33.3 ms for 30 fps |
| Render resolution | 1280x800 native, or 1280x720 (also accepted); use FSR-style upscaling from a lower internal resolution if needed |
| Memory | 16 GB is shared, so the game gets roughly 8 to 12 GB at most in practice; aim for under 6 GB total (estimate) so the OS and overlays have room |
| Battery | 40 Wh at 15 W is under 3 hours; a 30 fps cap and lowered TDP can double play time; offer a frame cap |
| Storage | Many Decks have 256 GB or 64 GB; large installs hurt; keep size reasonable and load times short on the internal SSD or microSD |
| Input | Gamepad controls, trackpads, gyro, touch; see input reference |
| OS | SteamOS (Linux) running Windows games through Proton, or native Linux builds |

Rules:

1. Tune a "Steam Deck" graphics preset: either auto-detect the Deck (Steamworks `IsSteamRunningOnSteamDeck`, or the `SteamDeck=1` environment variable that Steam sets; verify current guidance in Steamworks documentation) and choose Low or Medium with an upscaler, or document it as the Medium preset.
2. Test using Game Mode on real hardware at the shipping settings, with the performance overlay (set to show frame rate and power) and 15 W TDP. A developer Windows PC at 1080p tells you nothing.
3. Check shader cache handling: Proton and Vulkan games compile shaders; first-run hitching is a known source of complaints; precompile or warm up shaders in a loading screen.
4. The OS suspends the game when the Deck sleeps. Handle resume without crashes (network, audio device, controller).
5. Steam Hardware Survey shows Steam Deck GPU at about 0.28 percent of surveyed systems in Sept 2026, but Deck players are valuable, especially for indie and controller-first games, and the Deck is the standard handheld test target for other PC handhelds.

## 4. PC tiers: integrated-GPU laptops, mid, high

Define three reference machines. The classes below are descriptions, not product lists; fill them with real parts you own. Compare against the survey (section 7).

| Tier | Class | CPU | RAM | GPU | VRAM | Target |
|---|---|---|---|---|---|---|
| Low: integrated-GPU laptop | A recent thin laptop with integrated graphics or a Steam Deck-class APU; also older dedicated GPUs | 4 cores | 8 to 16 GB | Integrated (shares RAM); about 1.5 to 4 TFLOPS | Shared | 1080p lowest preset (or 720p scaled), 30 to 60 fps |
| Mid | Mainstream gaming PC or laptop | 6 cores | 16 GB | An entry or mid dedicated GPU from the last four to five years (for example the class of the RTX 3060 or 4060, which appear in the survey's top entries) | 8 GB | 1080p high preset, 60 fps |
| High | Enthusiast | 8 or more cores | 32 GB | Current high-end GPU | 12 to 16 GB | 1440p or 4K high or ultra, 120 fps or more where relevant |

Survey context (Sept 2026, source https://store.steampowered.com/hwsurvey): 8 physical cores is the most common at 30.06 percent, then 6 cores at 27.23 percent and 4 cores at 10.79 percent; 32 GB RAM is the most common at 42.22 percent, with 16 GB at 37.82 percent and 8 GB at 6.47 percent; VRAM 16 GB at 27.21 percent, 8 GB at 26.71 percent and 12 GB at 13.06 percent. The survey is of Steam users who opt in, so it describes the Steam audience, not all gamers; it skews toward gaming hardware.

Budgets (estimates):

| Resource | Low | Mid | High |
|---|---|---|---|
| Frame time at the target | 16.7 to 33.3 ms | 16.7 ms | 6.9 to 8.3 ms |
| System RAM (game process) | under 4 GB | under 8 GB | under 12 GB |
| VRAM | under 2 GB | under 6 GB | under 10 GB |
| Draw calls (3D) | under 1,500 | under 3,000 | engine limits |
| Install size | State clearly; SSD helps; HDD users need longer loads | | |
| Load time | under 15 s to gameplay on HDD or slow SSD | under 10 s | under 5 s |

Notes:

- **Integrated GPUs share memory**. Memory bandwidth is the bottleneck; lower texture resolution, reduce overdraw, avoid heavy post-processing.
- **Apple silicon Macs**: unified memory, Metal; the base chips are comparable to mid-range PC integrated or low-end dedicated GPUs (estimate); only a small share of Steam players (macOS 1.92 percent in the survey) but large on other storefronts. Unity and Godot support Metal; Unreal supports macOS with caveats; verify your engine version.
- **Linux**: 3.05 percent in the survey (Sept 2026), including Steam Deck; Proton lets Windows builds run, native builds are optional.
- **CPU**: 4 cores at 3 GHz or more is the realistic floor for many games; if you run simulation heavy loads (RTS, sim), budget for single-thread speed; use multithreading carefully.
- **Storage**: SSD is common but not universal; do not assume instant streaming of large assets.
- **Resolution scaling and upscalers** let low tiers reach target; offer the choice but do not hide the native option.

## 5. Web tiers

Browser games ship in a sandbox with their own limits. Treat web as two tiers: desktop browser and mobile browser.

| Item | Desktop browser | Mobile browser |
|---|---|---|
| Graphics API | WebGL 2 baseline; WebGPU where available | WebGL 2; WebGPU only on recent iOS and Android browsers |
| Frame target | 60 fps | 30 to 60 fps; lower for 3D |
| Memory | Aim under 1 GB (estimate); WebAssembly 32-bit memory is capped at 4 GB by the platform, and browsers may allow less | Aim under 300 to 500 MB (estimate); mobile browsers kill tabs that use too much, notably iOS Safari |
| Download | First interactive under about 10 MB if possible; total under 50 MB for casual portal games (estimate); show loading progress | Smaller still; assume cellular |
| Startup | Under 5 seconds to a playable state on broadband (estimate) | Under 8 seconds |
| Audio | Web Audio; unlock on first gesture | Same, strict on iOS |
| Saves | IndexedDB (section 2 of the saves reference) | Same, with eviction risk |

### WebGL 2 and WebGPU

- **WebGL 2** is the safe baseline across Chrome, Edge, Firefox and Safari. Godot's web export supports only the Compatibility renderer (WebGL 2); Forward+ and Mobile renderers do not run on the web, and WebGPU is not supported by Godot's web export (source: https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_web.html). Unity WebGL requires a WebGL 2 capable, 64-bit, WebAssembly-capable browser (source: https://docs.unity3d.com/6000.0/Documentation/Manual/system-requirements.html).
- **WebGPU availability (caniuse, Oct 2026)**: global usage about 87.82 percent (85.8 full plus 2.02 partial); Chrome and Edge from version 113 on desktop, Chrome for Android recent versions, Safari 26 on macOS partial and on iOS supported, Samsung Internet supported; the page showed Firefox as disabled by default (Firefox's own release notes may say otherwise for some platforms, so verify) (source: https://caniuse.com/webgpu; MDN notes it is not Baseline: https://developer.mozilla.org/en-US/docs/Web/API/WebGPU_API). Use it only behind `navigator.gpu` feature detection, with a WebGL fallback, unless the game has a hard need (compute-heavy effects).
- **Shader and feature limits**: WebGL 2 lacks compute shaders and some formats; texture compression formats differ per platform (BC on desktop, ASTC on mobile, ETC2 broadly): ship Basis Universal or multiple formats, or use a loader that picks one.

### WebAssembly memory, threads and COOP/COEP

- Wasm memory grows but never shrinks; peak memory sets the footprint. Pre-size to avoid reallocation stutter (engine option).
- **Threads need SharedArrayBuffer**, which needs cross-origin isolation: `Cross-Origin-Opener-Policy: same-origin` and `Cross-Origin-Embedder-Policy: require-corp` response headers (source: Godot web export page above). Isolation blocks third-party ads and embeds on the same page, and many portals and hosts do not allow it. Godot 4.3 and later default to single-threaded web export, which works without special headers and suits itch.io, Poki and CrazyGames (same source). Default to single-threaded unless you control the host.
- If you cannot set headers, a service-worker approach (Godot's PWA option) can simulate them; test it on the real host.
- Audio in single-threaded mode: Godot's web sample playback has low latency but no effects; stream playback has more features and more latency (same source). Decide with the audio design (`audio-production`).

### Download size

- Compress `.wasm`, data and `.pck` with Brotli or gzip; gzip shrinks a Godot wasm module to about a quarter (same Godot source). itch.io does not compress on the fly, so precompress and set the right headers or choose a host that does it (`pc-web-release`).
- A custom engine build with unused modules removed cuts the wasm size, important for mobile web.
- Split content into a small boot bundle and streamed levels. Show a progress bar and a first interactive moment quickly.
- Cache with a service worker so second loads are instant; handle updates.
- Portals set their own size, loading and SDK rules; read them in `pc-web-release`.

## 6. Consoles (public information)

Public specifications only. Developer-only budgets (memory available to titles, CPU cores reserved for the OS, certification performance requirements) are under non-disclosure agreements and come from the platform holder after you are in a programme (`console-pathway`). The figures below are the widely published consumer specifications and should be rechecked.

| Console | Public headline | Typical target |
|---|---|---|
| Switch (original, including Lite and OLED) | NVIDIA Tegra X1 class SoC, 4 GB RAM, 720p handheld, up to 1080p docked (public Nintendo information) | 30 fps typical, 60 fps for lighter games; handheld and docked both tested |
| Switch 2 | 7.9 inch 1080p LCD, HDR10 and VRR up to 120 Hz in handheld; docked output up to 4K at 60 fps (120 fps at 1080p or 1440p); 256 GB internal storage; microSD Express cards (source: https://www.nintendolife.com/guides/nintendo-switch-2-specs-how-powerful-is-the-new-switch). RAM is not on Nintendo's own spec sheet; leaks say 12 GB, unverified | 30 or 60 fps; handheld 1080p, docked up to 4K via upscaling; check what the original Switch version must do for compatibility |
| PlayStation 5 | About 10 TFLOPS GPU, 16 GB GDDR6 (public Sony specification) | 60 fps standard for many genres; 30 fps with a quality mode; resolution targets up to 4K |
| Xbox Series X | About 12 TFLOPS GPU, 16 GB (public Microsoft specification) | 60 fps; up to 4K |
| Xbox Series S | About 4 TFLOPS GPU, 10 GB (public Microsoft specification) | The lowest Xbox target; usually 1080p to 1440p at 60 fps |

Design points:

- Plan a quality and a performance mode on PS5 and Xbox for GPU-heavy 3D games; the performance mode targets 60 fps at lower resolution.
- Series S is the memory and GPU floor on Xbox; if the game works there it generally works on Series X. Platforms and publishers may require Series S support (verify in the programme).
- Switch family: you must hold the same frame time in handheld and docked; dynamic resolution is standard; design the UI for both screens.
- Cross-gen: original Switch and PS4-class hardware still exist; decide if you support the previous generation (`console-pathway`).
- Loading and suspend or resume time are certified behaviours on consoles; fast start matters.
- Memory is fixed, with no virtual memory to fall back on; budget assets and leaks tightly; run long soak tests.
- Engine choice affects console cost. Godot has no official console export (private templates through approved developers, middleware or porting houses; https://godotengine.org/consoles/). Unity supports Switch, PlayStation 4 and 5, and Xbox from its Windows editor (Unity 6 system requirements page). Defold lists Switch, PlayStation 4 and 5, and Xbox (https://defold.com/manuals/introduction/). See `references/platform-matrix.md`.

## 7. Writing PC minimum and recommended specs from the Steam Hardware Survey

Source: https://store.steampowered.com/hwsurvey (Sept 2026 data quoted below; the page updates monthly).

Figures from the survey page (Sept 2026):

| Metric | Leading values |
|---|---|
| OS | Windows 95.03 percent (Windows 11 64-bit 71.34, Windows 10 64-bit 23.61), Linux 3.05, macOS 1.92 |
| System RAM | 32 GB 42.22 percent, 16 GB 37.82, 8 GB 6.47 |
| VRAM | 16 GB 27.21 percent, 8 GB 26.71, 12 GB 13.06 |
| Primary display | 1920x1080 47.91 percent, 2560x1440 27.04, 2560x1600 5.22, 3840x2160 4.79 |
| Physical CPU cores | 8 cores 30.06 percent, 6 cores 27.23, 4 cores 10.79 |
| GPU leaders | RTX 5070 5.86 percent, RTX 5060 4.20, RTX 5060 Ti 3.87, RTX 4060 3.72, RTX 3060 3.54 |
| Steam Deck GPU | 0.28 percent |

Procedure:

1. **Fetch the current survey** and note the date. Record the numbers in the spec document.
2. **Measure**, do not guess. Run the shipping build on your low, mid and high reference machines and record frame rate, 1 percent lows, peak RAM, peak VRAM, load times.
3. **Minimum spec** = the weakest machine where the game holds the minimum target (usually 30 fps, or 60 if the genre needs it) at the lowest preset and 720p or 1080p. State the target in the spec ("1080p, Low, 30 fps").
4. **Recommended spec** = a mid machine at the default preset: "1080p, High, 60 fps".
5. **Check coverage.** Use the survey to see how much of the audience your minimum excludes. For example, a minimum of 8 GB RAM excludes the roughly 6 percent or fewer on lower amounts (8 GB is 6.47 percent, so lower tiers are smaller still); a VRAM minimum of 8 GB would exclude players below that (the survey shows 8 GB or more for the leading three bins; smaller bins are not given here, so read the full table). If the minimum excludes more than about 10 to 15 percent of the audience you want (estimate), optimise or lower the minimum.
6. **State**: OS (version), CPU (model class and cores), RAM, GPU (model class), VRAM, DirectX or Vulkan version, storage (free space, SSD recommended or required), network, and special requirements (a controller, 64-bit only, AVX). Do not list a requirement the game does not need (some CPU instruction sets exclude old CPUs for little gain).
7. **List named parts** only for parts you tested. Use class language ("six-core CPU from the last five years") for the rest.
8. **Update** specs after performance patches and when adding content that changes the budget.
9. **Steam Deck and Linux**: state Deck status only through Valve's verification (`pc-web-release`); give the tested Deck settings in the store description.
10. **macOS and Linux**: list the OS versions you test and whether Apple silicon is native or runs under translation.

## 8. How to test each tier

| Tier | Hardware to use | Method | Evidence to store |
|---|---|---|---|
| Low-end phone | A real device with 2 to 3 GB RAM from the lowest tier you support, plugged in and unplugged | 30-minute session; record frame time, memory (platform tools), temperature, battery drop; test cold start and background resume | `perf-report`, screenshots, device model and OS |
| Mid and high phone | One of each | Same; check 60 and 120 fps options and notch handling | Same |
| Tablet and foldable | One tablet, one foldable or emulator | Layout and resolution scale | Screenshots |
| iOS vs Android | At least one device of each; Xcode Instruments and Android Studio profilers, Perfetto | Platform tools (`mobile-performance`) | Reports |
| Steam Deck | A real Deck in Game Mode, 15 W | Frame rate overlay, battery and thermals over 30 minutes; suspend and resume; controller-only play | Video, overlay screenshots |
| Integrated-GPU laptop | A real laptop (not a VM) on battery and plugged in | Lowest preset, 1080p and 720p; frame time capture | Capture files and logs |
| Mid and high PC | Reference machines | Preset sweeps; 1440p and 4K; ultrawide | Benchmarks (average and 1 percent low) |
| Web | Chrome, Firefox, Safari, plus a mid Android phone and an iPhone | Browser dev tools performance panel; memory panel; throttle CPU 4x and network to Fast 3G or slow 4G in dev tools; test on the real host with the real headers | Lighthouse-style load timings, size breakdown, console log |
| Consoles | Devkits and test kits through the programme | Platform profilers and requirements | Provided by the platform process (`console-pathway`) |

General procedure:

1. Build a **deterministic benchmark scene or replay** that exercises the worst case (most enemies, biggest effect, densest level). Use the sim-core input replay (`game-architecture`).
2. Run it three times per device, take the median.
3. Record: average fps, p95 frame ms, 1 percent low, peak memory, load time, install size, temperature or battery where relevant.
4. Compare with the budget; fix the largest overage first (`optimize`).
5. Run the **soak test**: 30 to 60 minutes of play or a loop of the benchmark; look for memory growth, thermal throttling and frame drift.
6. Test first-run (cold shader cache, cold disk cache) and the second run.
7. Check low-memory and low-storage conditions: the game should fail gracefully with a message, not corrupt saves.
8. Re-test after every large content drop and engine upgrade; store the numbers in `evidence/<FEATURE-ID>/` and trend them over time.
9. Test with background load for PC and mobile: a browser or video call open.
10. For online games: test the netcode under latency and loss (`multiplayer-backend`).

Cloud device farms exist for mobile (Firebase Test Lab, AWS Device Farm and similar; verify availability and cost) and can cover the long tail of Android devices; they are not a substitute for a physical low-end device for thermals.

## 9. Budget table to copy into the contract

Fill one row per supported tier and copy the weakest tier into `technical.min_spec` and `technical.perf_budgets`.

| Tier (name the device) | Frame target | p95 frame ms | Memory MB (peak) | VRAM or GPU memory MB | Install or download MB | Cold start s | Measured? |
|---|---|---|---|---|---|---|---|
| Low phone: ______ | 30 | 33 | 400 | n/a | 150 | 4 | no |
| Mid phone: ______ | 60 | 16.7 | 800 | n/a | 250 | 3 | no |
| Steam Deck | 40 or 60 | 25 or 16.7 | 6000 | shared | install on disk | 10 | no |
| Integrated laptop: ______ | 30 | 33 | 3500 | shared | install on disk | 10 | no |
| Mid PC: ______ | 60 | 16.7 | 7000 | 6000 | install on disk | 8 | no |
| Web desktop | 60 | 16.7 | 1000 | n/a | 30 | 5 | no |
| Web mobile | 30 | 33 | 400 | n/a | 15 | 8 | no |
| Console (named) | per programme | per programme | per programme | per programme | per programme | per programme | no |

The numbers in the example rows are estimates from this reference. Replace "no" by "yes" only when a `perf-report` exists on disk.
