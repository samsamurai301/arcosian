---
name: platform-targets
description: 'Platform-target codex for one game on many platforms: choosing platforms, input and controls (touch, mouse/keyboard, gamepad), platform UX, performance tiers, saves and platform rules for mobile, PC, Steam Deck, web and consoles (public info). Use when asked "which platforms", "add PC/web/console", "gamepad support", "Steam Deck", "port this game" or "set min spec".'
when_to_use: 'Choosing target platforms, input schemes, UI scaling, tier budgets, save locations, port planning.'
---

# Platform Targets

A game is designed for the platforms its players use, not retrofitted to them. The platform choice decides the input, the screen, the session length, the performance budget, where saves live and which store rules apply. This skill turns a platform list into obligations the build must meet, and tells you what each added platform will cost.

## What this skill gives you

- A decision procedure for choosing platforms from genre, input, session length, business model, team size and porting cost.
- The recipe for recording the choice in the design contract (`meta.platforms`, `meta.input`, `meta.orientation`) and a short build checklist per platform.
- A compact per-platform table: input, UI, performance target, save location, rules.
- Five references: input and controls, platform UX, performance tiers, saves and platform rules, and an engine and porting matrix with worked plans.
- Pointers to the skills that own store mechanics, console programmes and mobile depth, so nothing is duplicated.

## Core models

1. **Platform = input + screen + session + store + hardware.** Change any one and the design may break. A one-thumb tap game does not become a PC game by adding a mouse; a mouse-precision game does not become a phone game by adding a touch layer.
2. **Design for the hardest input first.** Touch has no hover, no buttons, no precision and covers the screen. Gamepad has no cursor. If the core verbs work on the weakest input you intend to ship, the others are cheap. Write each verb once as an action, then bind it per input (see `references/input-and-controls.md`).
3. **Sim-core plus presentation.** Keep rules, saves and economy independent of input, resolution and renderer (`game-architecture`). Platform work then lives in a thin layer: input mapping, UI layout, rendering quality, storage and services.
4. **Every platform adds a permanent test cost.** Each extra platform multiplies QA, patching, support and store work. Add a platform when the audience gain beats that recurring cost, not when it is technically possible.
5. **Budgets come from the weakest supported tier.** Name the tier (for example "2021 mid-range Android", "Steam Deck", "integrated-GPU laptop"), set frame time, memory and size budgets for it, and test on it (`references/performance-tiers.md`).
6. **Where the player is decides the session.** Phone: one to five minutes, interrupted. PC: thirty to ninety minutes, deliberate. Console and handheld: thirty minutes to hours, suspend and resume. Web: first minute decides everything. Session length belongs in the contract (`meta.session_length_target_sec`).
7. **Verified beats claimed.** Steam Deck, console and store status come from the platform holder's own process. Never write "Deck Verified" or "console ready" in a contract or store page until the evidence exists.
8. **Accessibility and localisation are platform features.** Remapping, text size, colour-blind safety and font coverage are expected on PC and console and required by some stores. Plan them at design time (`accessibility-localization`).

## Decision procedures

### A. Choose platforms

Run these steps in order and write the result and the reasons into `.gamestudio/research/platform-decision.md`.

1. **Genre fit.** Look up the genre in the fit table in `references/platform-matrix.md` section 5. A "poor" cell is a blocker unless the design changes (for example real-time twin-stick on touch).
2. **Input fit.** List the verbs from the contract (`verbs[].input`). For each platform, mark whether every verb has a natural binding. One unmapped verb blocks that platform.
3. **Session fit.** Compare `meta.session_length_target_sec` with the platform norm (core model 6). A 40-minute run on a phone needs suspend, resume and mid-run saves; a 90-second round on a console needs a reason to launch it.
4. **Business model fit.** Free-to-play with ads and IAP is a mobile and web model, and a thin one on PC and console. Premium sells on PC and console and in small volume on mobile. Check `monetization` and `store-release` for what each store allows.
5. **Team and budget fit.** Count people and months. Use the porting cost table (`references/platform-matrix.md` section 4). Rule of thumb: a solo developer or team of two should ship one lead platform, plus at most one adjacent platform that shares input (iOS plus Android, or Windows plus Steam Deck, or web plus desktop).
6. **Porting cost.** Estimate the added platform as a percentage of lead-platform effort, including QA and store work. If the estimate is above 30 percent of the lead build and the platform is not in the audience's top two, defer it.
7. **Pick one lead platform and an ordered list.** Lead gets full design attention. Others are "supported" (tested, in the store) or "deferred" (architecture does not block them, nothing shipped).
8. **Record in the contract** (procedure B), then add a `must`/`should`/`wont` line per platform to `scope`.

Quick decision table:

| Situation | Lead | Add next | Avoid early |
|---|---|---|---|
| Casual, short sessions, F2P | iOS plus Android | Web portals for reach | Console |
| Premium, mid-core, 3 to 30 hours | Windows via Steam | Steam Deck (nearly free if gamepad-ready), then Switch | Mobile unless designed for touch |
| Browser-first casual, ad-funded | Web desktop | Web mobile, then app wrapper | Console |
| Controller-first action or platformer | Windows via Steam | Steam Deck, consoles via porting partner | Mobile |
| Turn-based or card game, slow decisions | PC plus mobile together | Web | Console unless a publisher asks |
| Competitive real-time multiplayer | PC | Consoles (cross-play needs platform approval) | Web, mobile at launch |

### B. Record the choice in the design contract

Fields live in `.gamestudio/contract.json` (`docs/BLUEPRINT.md` section 5).

| Field | Rule |
|---|---|
| `meta.platforms` | Subset of `ios`, `android`, `web`, `windows`, `macos`, `linux`, `switch`, `playstation`, `xbox`, `other`. List only platforms you will ship or test, lead first. Steam Deck is `linux` for the contract; note Deck in `scope.must`. |
| `meta.input` | Union of inputs you support: `touch`, `mouse_keyboard`, `gamepad`, `motion`, `other`. Derived from platforms: ios or android give `touch`; windows, macos, linux give `mouse_keyboard` and usually `gamepad`; switch, playstation, xbox give `gamepad`; web gives `touch` and `mouse_keyboard`, plus `gamepad` if you support it. |
| `meta.orientation` | `portrait`, `landscape` or `both`. Desktop, console and web desktop are landscape. If phones are targeted with a landscape game, say so; locking is an acceptable choice. |
| `verbs[].input` | One action name per verb, with a binding note per input type. |
| `technical.min_spec`, `technical.perf_budgets` | Set from the weakest supported tier (`references/performance-tiers.md`). |
| `scope.must`, `scope.wont` | Name every deferred platform in `wont` so scope creep is visible. |
| `risks` | Add a risk per platform that lacks a devkit, a test device or a certification path. |

Validate after editing: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py validate --root PROJECT_DIR`. Note `.gamestudio/config.json` `platforms` is currently documented as `ios` and `android` only; when the project targets others, keep the contract as the source of truth and mention the gap in the decision file.

### C. What each choice obliges the build to do

Tick each box with evidence (test log, screenshot, device note) before a feature is done on that platform.

**iOS and Android**
- [ ] Touch targets, thumb zones and safe areas per `mobile-ux`; both orientations or a deliberate lock.
- [ ] Suspend, resume and process death restore the player to where they were; autosave on background.
- [ ] Frame, memory, thermal and battery budgets measured on the lowest supported device (`mobile-performance`).
- [ ] Permissions asked in context, with a decline path.
- [ ] Android: 16 KB page size support for native code, tested on a 16 KB device or image; many screen sizes and foldables; back gesture handled.
- [ ] Optional gamepad support if the genre benefits; glyphs swap on use.

**Windows, macOS, Linux**
- [ ] Mouse and keyboard fully usable; keyboard rebinding; gamepad if the genre allows.
- [ ] Settings menu with resolution, window mode, quality preset, frame cap, V-Sync, FOV if 3D, audio, keybinds, accessibility (`references/platform-ux.md` section 4).
- [ ] 16:9, 16:10, 21:9 and 4:3 render correctly; UI scales; text stays legible at 1080p and 4K.
- [ ] Alt-tab, focus loss, minimise and monitor change do not crash or lose input; game pauses if single-player.
- [ ] Saves in the per-OS user data folder, versioned, cloud-sync-safe (`references/saves-and-platform-rules.md`).
- [ ] Minimum and recommended specs written from measurement, not guesses.
- [ ] macOS: signing and notarisation; Linux: native build or Proton tested. Mechanics are in `pc-web-release`.

**Steam Deck (as a PC target)**
- [ ] Full gamepad play with default controls and no mouse; on-screen keyboard for text entry.
- [ ] Glyphs match the active controller; 1280x800 supported; smallest text at least 9 px high at 1280x800 and 12 px recommended.
- [ ] No launcher dialogs, no unsupported-hardware warnings, 30 fps or better at 800p on defaults.
- [ ] Tested in Game Mode on a real Deck; verification itself is Valve's process (`pc-web-release`).

**Web (desktop and mobile browsers)**
- [ ] Loads to the first interaction fast; download size budgeted; loading progress shown.
- [ ] Audio unlocks after the first user gesture; fullscreen and pointer lock (if used) are started from a gesture and have an Escape path.
- [ ] Saves use IndexedDB with a quota check and an export or cloud option; players are told when storage can be cleared.
- [ ] WebGL 2 baseline; WebGPU only behind feature detection with a WebGL fallback.
- [ ] Threads and SharedArrayBuffer only if the host can send COOP and COEP headers; otherwise ship single-threaded.
- [ ] Touch and mouse both work; the page survives tab backgrounding, resize and device rotation.

**Switch family, PlayStation, Xbox**
- [ ] Gamepad-only play for every flow including menus, text entry and purchases; 10-foot UI with TV safe margins.
- [ ] Handheld and docked modes (Switch) or performance and quality modes tested; suspend and resume, controller disconnect and user sign-out handled.
- [ ] Platform-correct glyphs and confirm/cancel convention; platform terminology in text.
- [ ] Saves through the platform save API, not raw files; no quit-to-desktop option on consoles.
- [ ] Access to developer programmes, devkits and certification are planned early. Details are in `console-pathway`.

### D. Add a platform to an existing game

1. Re-run procedure A with the current build as lead.
2. List what is platform-bound in the code: input reads, hard-coded resolutions, file paths, store or ads SDKs, shader features, threading, plugins with no target support. Count occurrences; this is the size of the port.
3. Insert the abstraction layer first (actions instead of keys, a storage interface, a platform service interface). Ship that refactor on the lead platform before porting.
4. Port the smallest vertical slice (boot, menu, one playable level, save, quit) and test on real hardware.
5. Fill the checklist in C, then the performance tier tests (`references/performance-tiers.md` section 8).
6. Plan store and release work with `pc-web-release`, `store-release` or `console-pathway`.

### E. Write PC minimum and recommended specs

1. Measure on three reference machines: low (integrated GPU laptop or Steam Deck), mid, high.
2. Minimum = the weakest machine that holds the target frame rate at the lowest preset. Recommended = a mid machine at the default preset.
3. Compare against the Steam Hardware Survey (`references/performance-tiers.md` section 7) to see what share of players each spec covers. Aim for the minimum to cover the large majority of your audience.
4. Write OS, CPU, RAM, GPU, VRAM, storage and display. Say HDD or SSD if load times depend on it.

## Platform specifics

Compact table. Figures are defaults, not guarantees; detail and sources are in the references.

| Platform | Input | UI | Performance target | Save location | Rules to know |
|---|---|---|---|---|---|
| iOS | Touch; MFi and DualSense/Xbox pads optional | Safe areas, notch, home indicator, Dynamic Type optional; 44 pt targets | 60 fps (30 for heavy 3D); thermal limit is the real cap | App sandbox (`persistentDataPath`, `user://`); iCloud optional | App Review, privacy labels, ATT for tracking; see `store-release` |
| Android | Touch; gamepads optional | Many aspect ratios and foldables; 48 dp targets; edge-to-edge | 30 or 60 fps by device tier; test low RAM | App-private storage; Play Games cloud save optional | Target API level, 16 KB pages, Data safety form; see `store-release` |
| Windows | Mouse and keyboard; gamepad | Resolution and DPI scaling; settings menu | 60 fps at 1080p on recommended spec; 30 at minimum | `%APPDATA%` or Saved Games; Steam Cloud | Store rules via Steam or others; see `pc-web-release` |
| macOS | Mouse and keyboard; gamepad | Retina scaling; fullscreen spaces; notch | 60 fps on Apple silicon base chips | `~/Library/Application Support/<game>` | Signing and notarisation; see `pc-web-release` |
| Linux | Mouse and keyboard; gamepad | Wayland and X11; fractional scaling | As Windows; Proton or native | `$XDG_DATA_HOME` (`~/.local/share/<game>`) | Native build or Proton; see `pc-web-release` |
| Steam Deck | Gamepad plus touch; Steam Input | 1280x800, 16:10, 7-inch; text 9 px minimum | 30 fps at 800p on defaults; 40 or 60 fps better; battery matters | As Linux; Steam Cloud | Valve Verified criteria; see `pc-web-release` |
| Web desktop | Mouse and keyboard; Gamepad API | Any window size; resize events; fullscreen | 60 fps WebGL 2; small download | IndexedDB (browser storage) | Portal and host rules; see `pc-web-release` |
| Web mobile | Touch | Browser chrome changes viewport height; safe areas | 30 fps typical; tight memory | IndexedDB; may be evicted | iOS Safari quirks; no install prompts by default |
| Switch family | Gamepad; touch in handheld; motion optional | Handheld 720p (Switch) or 1080p (Switch 2); docked TV | 30 or 60 fps; stay inside memory budget | Platform save data API | Programme and certification; see `console-pathway` |
| PlayStation | Gamepad; touchpad and haptics optional | 10-foot UI, TV safe area | 60 fps expected for most genres | Platform save data API | Programme and certification; see `console-pathway` |
| Xbox | Gamepad | 10-foot UI, TV safe area; Series S as the low tier | 60 fps expected; Series S is the floor | Platform save data (connected storage) | Programme and certification; see `console-pathway` |

For mobile depth use `mobile-ux` and `mobile-performance`; do not copy their rules here.

## Anti-patterns

| Anti-pattern | Why it hurts | Detect and fix |
|---|---|---|
| "We will add console later" with raw file I/O, hard-coded keys and mouse-only UI | Later means a rewrite | Grep for direct `Input.is_key_pressed`, `Keyboard.current`, `File.WriteAllText`; move behind actions and a storage interface now |
| Touch controls pasted onto a keyboard game | Unplayable and rated badly | Play a full level with touch only on a real phone before listing `touch` |
| One tier of testing on a developer machine | Low-end players crash or stutter | Test on the weakest named tier every milestone |
| Hard-coded resolution or aspect | Black bars, clipped HUD on 21:9 and phones | Test five aspect ratios (`references/platform-ux.md` section 1) |
| Glyphs that do not change with the controller | Players cannot find buttons | Last-used-device switching (`references/input-and-controls.md` section 7) |
| Claiming Deck Verified, console ready or age rating before evidence | Store rejection and trust loss | Treat these as milestones with evidence on disk |
| Unversioned saves | An update corrupts player progress | Version and migrate (`references/saves-and-platform-rules.md` section 5) |
| Web build that needs threads on a host without COOP/COEP | Blank page | Single-thread default; test on the real host |
| Cloud-syncing graphics settings | A 4K desktop setting breaks the Deck | Keep machine-specific config out of cloud saves |
| Assuming mobile everywhere | Wrong defaults for PC, web and consoles | Fill the Platform specifics table for each platform in the contract |
| Adding every platform at launch | QA and support collapse a small team | Procedure A step 5 and 6 |

## Using the ontology

- `contract.json`: set `meta.platforms`, `meta.input`, `meta.orientation`, `verbs[].input`, `technical.min_spec`, `technical.perf_budgets`, `scope` and `risks` as in procedure B. Validate with `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py validate --root PROJECT_DIR`.
- `features.json`: add per-platform feature entries (for example "gamepad support", "Deck pass"). A feature is done only when `static`, `unit`, `playthrough`, `visual` and `perf` are `pass` with evidence in `evidence/<FEATURE-ID>/`, or `n/a` with a note. Perf evidence is a `perf-report` from `mobile-performance` or `optimize`; playthrough evidence is a `playtest-report` from `qa-testing`.
- `config.json`: `platforms` and `orientation` mirror the contract; `engine` constrains which platforms are reachable (`references/platform-matrix.md` section 1).
- `budget.json` and `technical.perf_budgets`: derive from the tier tables in `references/performance-tiers.md`.
- Search the codex: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py kb "steam deck" --skill platform-targets`.
- Agents: `arcosian:gameplay-engineer` and `arcosian:lead-engineer` implement; `arcosian:ux-designer` owns layout; `arcosian:performance-engineer` owns tier budgets; `arcosian:release-manager` owns store work.

## Reference library

| File | Contains | Read when |
|---|---|---|
| `references/input-and-controls.md` | Touch, mouse and keyboard, gamepad layouts and conventions, glyph swapping, dead zones, aim assist, rumble, rebinding, hold versus toggle, last-used-device switching, Steam Input, web Gamepad API and Pointer Lock, Godot and Unity setup, worked action map | Binding any input, adding gamepad, or porting controls |
| `references/platform-ux.md` | Resolutions and aspect ratios, DPI and scaling, safe areas, 10-foot UI, PC settings menu, focus loss, window modes, platform conventions, text sizes, accessibility checklists | Building UI for a new platform or writing the settings menu |
| `references/performance-tiers.md` | Tiers and budgets for phones, Steam Deck, laptops, PCs, web and consoles; min and recommended specs; how to test each tier | Setting budgets, writing specs, planning device tests |
| `references/saves-and-platform-rules.md` | Save and config paths by OS and engine, web storage, cloud saves, versioning, Steam Deck criteria, platform rules that shape design, localisation and fonts | Writing the save system, adding cloud saves, planning Deck or console work |
| `references/platform-matrix.md` | Engine support per platform, porting cost, genre by platform fit, three worked plans | Choosing engine and platforms, estimating a port |

## Volatile facts (as of Oct 2026 — verify)

Checked on the vendor pages below in Oct 2026 unless marked unverified.

- Steam Deck Verified criteria (controller input, glyphs, text input, 1280x800 or 1280x720, 9 px minimum and 12 px recommended text height, 30 fps at 800p, no launcher or compatibility warnings): https://partner.steamgames.com/doc/steamdeck/compat
- Steam Deck LCD hardware (Zen 2 4 cores, 8 RDNA 2 compute units, 16 GB LPDDR5, 1280x800 at 60 Hz, 40 Wh): https://www.steamdeck.com/en/tech/deck
- Steam Hardware Survey, September 2026 (Windows 95.03 percent, Linux 3.05, macOS 1.92; 1920x1080 at 47.91 percent; 32 GB RAM 42.22 percent and 16 GB 37.82; Steam Deck GPU 0.28 percent): https://store.steampowered.com/hwsurvey
- WebGPU support (caniuse reports 87.82 percent global usage; Chromium desktop since 113, Safari 26 on macOS partial and iOS 26 supported; Firefox shown disabled by default on that page, which may lag Firefox release notes, so verify): https://caniuse.com/webgpu and https://developer.mozilla.org/en-US/docs/Web/API/WebGPU_API
- Godot web export (Compatibility renderer and WebGL 2 only, no WebGPU, single-threaded default since 4.3, COOP/COEP for threads): https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_web.html
- Godot console access (no official ports; private templates via approved developers, middleware or porting houses): https://godotengine.org/consoles/
- Unity 6 platform requirements (Android 6.0 or later, iOS 13 or later, consoles require Windows editor): https://docs.unity3d.com/6000.0/Documentation/Manual/system-requirements.html
- Defold platforms (mobile, desktop, HTML5, Switch, PlayStation 4 and 5, Xbox): https://defold.com/manuals/introduction/
- Android 16 KB page size (updates for apps with native code targeting Android 15 or higher blocked on Play from 1 February 2027 if unsupported): https://developer.android.com/guide/practices/page-sizes
- Web storage quotas and eviction (Chromium up to 60 percent of disk, Firefox smaller of 10 percent or 10 GiB group limit, Safari about 60 percent, Safari 7-day script-data cap): https://developer.mozilla.org/en-US/docs/Web/API/Storage_API/Storage_quotas_and_eviction_criteria
- Steam Cloud and Auto-Cloud: https://partner.steamgames.com/doc/features/cloud
- Nintendo Switch 2 public specs (7.9 inch 1080p LCD, up to 120 Hz VRR, dock output up to 4K 60); RAM is not on Nintendo's own sheet and is unverified: https://www.nintendolife.com/guides/nintendo-switch-2-specs-how-powerful-is-the-new-switch
- Xbox Accessibility Guidelines: https://learn.microsoft.com/en-us/gaming/accessibility/guidelines ; Game Accessibility Guidelines: https://gameaccessibilityguidelines.com/ (not re-fetched in this pass)
- Unreal Engine platform support, Unity WebGPU status and console SDK details were not confirmed in this pass; check https://dev.epicgames.com/documentation/en-us/unreal-engine/supported-platforms-and-hardware-for-unreal-engine and the Unity manual before committing.

## Related skills

- `pc-web-release`: Steam, itch.io, web portals, signing, packaging, Steam Deck verification mechanics.
- `console-pathway`: console programmes, certification, ratings, devkits.
- `store-release`: mobile store listings, review, rules and submission.
- `mobile-ux`, `mobile-performance`: mobile interaction, layout, and performance depth.
- `engine-godot`, `engine-unity`, `engine-alternatives`: engine specifics and alternatives.
- `game-architecture`: sim-core plus presentation, the structure that makes ports cheap.
- `accessibility-localization`: full accessibility and localisation workflow.
- `qa-testing`: device matrices and playthrough evidence.
- `optimize`: profiling and performance fixes.
- `monetization`: business model fit per platform.
- `genre-playbooks`: genre conventions that affect platform fit.
