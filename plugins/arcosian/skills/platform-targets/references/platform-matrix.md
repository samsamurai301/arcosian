# Platform matrix

This reference compares engines by platform support, explains how console access works for each engine, estimates the cost of porting a game to another platform, gives a genre by platform fit table, and works through three plans: a mobile-first puzzle game adding PC, a PC roguelite adding Steam Deck and Switch, and a web-first casual game adding mobile. Support statements were checked on vendor pages in Oct 2026 where a URL is given; everything else is labelled. Cost figures are planning estimates, not quotes.

## Contents

1. Engine support per platform
2. Console access
3. Web engines and wrappers
4. Porting cost estimates
5. Genre by platform fit table
6. Worked plan A: mobile-first puzzle game adding PC
7. Worked plan B: PC roguelite adding Steam Deck and Switch
8. Worked plan C: web-first casual game adding mobile
9. Checks before you commit to a platform list

## 1. Engine support per platform

Legend: yes = supported by the engine vendor; partial = supported with limits or through third parties; no = not supported; ? = unverified in this pass.

| Platform | Godot 4 | Unity 6 | Unreal Engine 5 | Defold |
|---|---|---|---|---|
| iOS | yes | yes (iOS 13 or later) | yes | yes |
| Android | yes | yes (Android 6.0 or later, API 23) | yes | yes |
| Windows | yes | yes | yes | yes |
| macOS | yes | yes | yes | yes |
| Linux | yes | yes | yes | yes |
| Steam Deck | via Linux or Proton | via Linux or Proton | via Linux or Proton | via Linux or Proton |
| Web | yes, WebGL 2 and Compatibility renderer only; no WebGPU | yes, WebGL 2; WebGPU status unverified | no official HTML5 in recent versions (unverified in this pass; check Epic documentation) | yes (HTML5) |
| Switch family | no official export; private templates, middleware or porting houses | yes (Switch and Switch 2 listed, needs Windows editor and platform access) | yes through the platform holder's programme (unverified in this pass) | yes (Switch listed) |
| PlayStation | same as Switch row | yes (PS4 and PS5 listed) | yes via programme (unverified) | yes (PS4 and PS5 listed) |
| Xbox | same as Switch row | yes (Xbox Series X and S, One listed) | yes via programme (unverified) | yes (Xbox listed) |

Sources:

- Godot web export: https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_web.html (WebGL 2 and Compatibility renderer only; WebGPU not supported; single-threaded default since 4.3).
- Godot consoles: https://godotengine.org/consoles/ (no official console ports; private export templates built with the official SDKs and shared with approved developers; middleware option and porting houses).
- Unity 6 platforms and minimum OS: https://docs.unity3d.com/6000.0/Documentation/Manual/system-requirements.html (consoles listed there: Nintendo Switch and Switch 2, Xbox Series X and S and One, PlayStation 4 and 5 including VR; console builds need the Windows editor).
- Defold: https://defold.com/manuals/introduction/ (Android, iOS, Switch, PlayStation 4 and 5, Xbox, HTML5, Linux, macOS, Windows).
- Unreal: the supported platforms page did not load usable content in this pass; confirm at https://dev.epicgames.com/documentation/en-us/unreal-engine/supported-platforms-and-hardware-for-unreal-engine.

Engine fit summary (see also `engine-godot`, `engine-unity`, `engine-alternatives`):

| Need | Pick | Reason |
|---|---|---|
| 2D game for mobile, PC and web, small team, no console in the first year | Godot 4 | Light, free, good 2D, web via Compatibility renderer |
| Mobile, PC and consoles with an established ecosystem and middleware | Unity | Largest console and SDK ecosystem, many plugins |
| High-end 3D on PC and consoles | Unreal | Strong 3D tooling; heavy for mobile and web |
| Small download, tiny web and mobile 2D | Defold | Small runtime, HTML5 and consoles listed |
| Browser-first | A web engine (section 3), or Godot or Defold | Download size and web integration |
| Existing engine in the project | Keep it unless a platform need forces a change | Engine switch costs more than most ports |

## 2. Console access

Public information only. You never get console tooling by buying an engine licence alone. The steps below are the generic public sequence; each platform holder runs its own programme, with its own approvals, fees and agreements, covered in `console-pathway`.

1. **Register as a developer with the platform holder** and get approved. Approval gives access to SDKs, documentation and devkits.
2. **Get devkit or test hardware** (price and terms are confidential per Godot's console page).
3. **Get an engine console export**: Unity ships console support that unlocks after platform access; Defold lists console platforms; Unreal builds consoles through the programme; Godot provides no official console export, and its project page says export templates are built from the official SDKs and shared privately with approved developers (source: https://godotengine.org/consoles/).
4. **Choose who ports**: yourself (needs engineers who know the SDK), a **porting house** (a studio that does the port for a fee or revenue share), or **middleware** (for Godot, W4 Games offers ports for Switch, Xbox Series X and S, and PlayStation 5 per the same page; the page lists several porting houses too, says the list is not exhaustive and not a guarantee of quality, so compare offers and reviews).
5. **Rate and certify** the game through the platform's process and regional rating bodies (`console-pathway`).
6. **Publish** through a publisher or self-publishing programme where the platform offers one (`console-pathway`).

Planning rules:

- Budget **time for approvals** (weeks to months, an estimate) before you commit a release date.
- Keep the game **console-ready in architecture** from the start (sim-core separation, pad-only UI, platform service interface, atomic saves; `references/saves-and-platform-rules.md`) so a porting partner has less to untangle.
- A porting partner typically needs the full source, build instructions and a stable game; ports go badly on games still changing every week.
- Ask porting partners about: engine version, performance targets, QA and certification support, patching responsibilities, revenue share or fixed fee, who owns console-specific code, and timeline.
- Do not discuss or store SDK material outside the agreement. This skill contains none.

## 3. Web engines and wrappers

| Option | Notes |
|---|---|
| Godot web export | WebGL 2 only; single-threaded default; size is a few MB to tens of MB for the engine (measure your build); Safari WebGL 2 issues are noted by Godot's docs (https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_web.html) |
| Unity WebGL | WebGL 2; larger builds, slower startup; works with portals; mobile browser support is limited by memory (verify) |
| Defold HTML5 | Small builds; strong for portals; has integrations with some portals according to its own manual |
| Phaser, PixiJS, Three.js, Babylon.js, PlayCanvas | JavaScript or TypeScript web-native engines and libraries; smallest download, best web integration, no console path; check each project's current licence and release status before adopting |
| Construct, GDevelop and similar no-code tools | Fast for casual 2D web and mobile wraps; limited for large games (verify exports and licences) |
| Native wrappers (Capacitor, Cordova, WebView shells) | Wrap a web game into an iOS or Android app; store review rules still apply and performance depends on the OS WebView (verify current tooling) |

Notes:

- A web-native game can be wrapped for mobile, but a Godot or Unity web build wrapped in a WebView is rarely the best path; export native instead.
- WebGPU: caniuse reports about 87.82 percent global usage in Oct 2026 (https://caniuse.com/webgpu), but engines like Godot do not use it in web export yet. Web-native engines may offer it; use feature detection and a WebGL fallback.

## 4. Porting cost estimates

Costs are shown as a share of the effort already spent on the lead platform (design, art and content excluded because they are reused). Estimates assume a game architected with sim-core and presentation separation. If input, saves, UI and platform calls are tangled with game logic, multiply by 1.5 to 3. All figures are estimates for planning only.

| From to | Extra effort (share of lead build) | Main work | Main risks |
|---|---|---|---|
| iOS to Android (same engine) | 10 to 20 percent | Device fragmentation, 16 KB page support, back button, store setup, ads and IAP SDKs, performance on low devices | Low-end device performance, certification of billing, long-tail bugs |
| Android to iOS | 10 to 20 percent | Metal and device tests, App Review, Apple sign-in and tracking rules, safe areas | Review rejections |
| Mobile to PC (Windows) | 20 to 40 percent | Mouse and keyboard, gamepad, settings menu, window modes, resolutions, saves, Steam integration, achievements, store page | Touch-first design that feels wrong with a mouse; monetisation changes (premium or a different economy; `monetization`) |
| Mobile to PC with a redesigned UI | 40 to 70 percent | As above plus new HUD, menus, content depth | Scope creep |
| PC to Steam Deck | 5 to 15 percent | Controller-only flow, glyphs, text size, 800p, performance tuning, Steam Input, Valve verification | Anti-cheat or launcher blockers, 9 px text |
| PC (Windows) to Linux native or macOS | 5 to 15 percent each | Build and test, signing and notarisation for macOS, graphics API differences | Plugin support, tooling |
| PC to web | 25 to 50 percent | Size, memory, WebGL 2 limits, saves, audio unlock, no threads, no native plugins, portal SDKs | Performance and memory; some features cannot be ported (heavy 3D) |
| Web to mobile (native) | 30 to 60 percent | Engine change if web-native; or native export plus touch UI and store requirements | Rewrite if the web game is JavaScript-only |
| Web to mobile (wrapper) | 10 to 25 percent | Wrapper, store requirements, performance, native features | Review rejections of thin wrappers; store rules (`store-release`) |
| PC to Switch family | 30 to 80 percent | Console programme, port or middleware, performance (memory, GPU), handheld UI, certification, saves, ratings | Memory and performance limits, approval time |
| PC to PlayStation or Xbox | 25 to 60 percent | Programme, SDK, certification, ratings, platform features, achievements, accessibility | Approval and certification time, platform feature requirements |
| Console to console (after the first) | 15 to 40 percent | New SDK, certification | Same |
| Any to a new store on the same platform (e.g. Steam to Epic or GOG) | 3 to 10 percent | Store SDK, store page, builds | Low |

Add the **recurring cost** per platform: patching and certification rounds, QA per release, support, store fees and revenue share, SDK updates, OS updates (new iOS, Android and Windows versions). A common planning figure is 10 to 20 percent of the lead platform's ongoing work per added platform (estimate).

Port-or-not rule: add the platform when `expected_extra_revenue_or_reach × margin` exceeds `one-time cost + 12 months of recurring cost`. If you cannot estimate reach, test demand cheaply first (a web demo, a Steam page wishlist count, a store coming-soon page).

Sizing the port from the code (procedure D in SKILL.md): count the platform-bound call sites by category and apply per-site times. Example counts for a 40,000-line Godot game: 120 direct input reads (about 1 to 2 days to move behind actions), 35 file paths (half a day), 14 platform SDK calls (1 to 3 days), 6 shaders not supported on the target (2 to 5 days), 3 plugins without a target build (variable, replace or drop).

## 5. Genre by platform fit table

Rating: A = natural fit, B = good with design work, C = possible with significant redesign, D = poor. These are design judgements, not market data; check demand with `market-intel` and `market-scan`. "Consoles" combines Switch, PlayStation and Xbox; the Switch family often fits lighter games better than the others.

| Genre | Phone | Tablet | PC | Steam Deck | Web desktop | Web mobile | Consoles |
|---|---|---|---|---|---|---|---|
| Match-3 and casual puzzle | A | A | B | B | A | A | C |
| Hyper-casual, endless runner | A | B | C | C | A | A | D |
| Idle and incremental | A | A | B | B | A | A | D |
| Card battler and deck builder | B | A | A | A | A | B | B |
| Turn-based tactics | B | A | A | A | B | C | A |
| Roguelite (action) | C | C | A | A | B | D | A |
| Platformer (precision) | C | C | A | A | B | D | A |
| Metroidvania | D | D | A | A | C | D | A |
| Twin-stick shooter | C | C | A | A | B | D | A |
| First-person shooter | C | C | A | B | C | D | A |
| Third-person action | D | D | A | B | D | D | A |
| Racing (arcade) | B | B | A | A | C | C | A |
| Puzzle platformer and logic puzzles | A | A | A | A | A | B | A |
| Visual novel and narrative | A | A | A | A | B | B | B |
| Point-and-click adventure | B | A | A | B | B | C | C |
| City builder and management | C | B | A | B | C | D | B |
| 4X and grand strategy | D | C | A | C | D | D | C |
| RTS | D | C | A | C | C | D | C |
| RPG (turn-based) | B | A | A | A | C | C | A |
| ARPG | C | C | A | A | D | D | A |
| MMO | C | C | A | C | D | D | B |
| Rhythm | A | A | B | B | B | B | B |
| Party and local multiplayer | C | B | B | C | C | D | A |
| Sports and fighting | C | C | A | A | D | D | A |
| Survival and crafting | C | C | A | A | D | D | A |
| Social, word and trivia | A | A | B | C | A | A | D |
| Farming and cozy sim | A | A | A | A | B | B | A |
| Tower defence | A | A | A | A | A | B | B |

Reading the table:

- Rows with "D" on phone and web (such as metroidvania, 4X and heavy 3D) usually need a premium PC or console plan.
- Rows with "A" on phone and web (casual, idle, hyper-casual) rarely justify a console port.
- Controller-friendly slow-decision games (card, tactics, turn-based RPG) are the cheapest cross-platform: one UI with large targets and focus navigation works everywhere.
- Players' session length and monetisation (`monetization`) matter as much as the fit: see procedure A in SKILL.md.

## 6. Worked plan A: mobile-first puzzle game adding PC

**Game**: a premium-with-IAP match-based puzzle game, portrait, one-thumb, 3-minute sessions, built in Godot 4. Team: two people. Lead: iOS and Android. Goal: add Windows via Steam after the mobile launch.

**Step 1: fit check.** Table says match puzzle on PC is B. PC audience wants depth, a settings menu, controller support and a different price. The decision: add PC only if the mobile launch has retention and the PC version can offer more (modes, daily challenge, leaderboards).

**Step 2: contract changes**

- `meta.platforms`: `["ios", "android", "windows", "linux"]` (Linux for Steam Deck; Deck is noted in `scope.must`).
- `meta.input`: `["touch", "mouse_keyboard", "gamepad"]`.
- `meta.orientation`: `both` (portrait on phones, landscape on PC). The puzzle board is square or tall: on landscape, place it centre with side panels.
- `meta.session_length_target_sec`: 180 stays; PC adds an optional 20-minute "run" mode in `scope.should`.
- `monetization_model`: `iap` stays on mobile; the PC build is premium with no ads (`monetization`, `store-release`).

**Step 3: input**

| Verb | Touch | Mouse and keyboard | Gamepad |
|---|---|---|---|
| swap pieces | drag a piece to a neighbour | click and drag or click two pieces | move a cursor with stick or d-pad, confirm on south |
| use booster | tap booster, tap target | click or hotkeys 1 to 3 | shoulder buttons cycle, confirm |
| pause | icon | Esc | Menu |

Implementation: one action map (`references/input-and-controls.md` section 12). The board reads a `cursor` and `select` command from each scheme. Gamepad needs a visible cursor and focus navigation: this is the largest UI addition.

**Step 4: UI.** Landscape layout with the board centred and side panels for boosters and goals; UI scale slider; 16:9 and 21:9 tests; settings menu (display, audio, controls, accessibility); window modes; quit button on desktop (not on consoles).

**Step 5: build obligations** (from SKILL.md procedure C): settings menu, resolutions, focus loss pause, saves in `user://` with versioning, cloud save through Steam Auto-Cloud, minimum spec by measurement (a low-end laptop), Steam integration and achievements (`pc-web-release`).

**Step 6: effort estimate** (section 4): mobile to PC with a redesigned UI is 40 to 70 percent of the lead build. For a two-person team with a 9-month mobile build that is about 4 to 6 months (estimate); the architecture work (action map, UI containers) done during mobile development cuts it toward the low end.

**Step 7: evidence.** Features in `features.json`: "PC input", "landscape UI", "settings menu", "Steam Cloud saves", "Deck pass". Playthrough evidence per input scheme; perf evidence on a low-end laptop and the Deck; visual evidence at five aspect ratios.

**Risks**: touch-first UX feels thin on PC (mitigate with a PC-only mode), price expectations differ, IAP economy must be redesigned or removed for the premium version (`economy-design`).

## 7. Worked plan B: PC roguelite adding Steam Deck and Switch

**Game**: a top-down action roguelite, 30 to 60 minute runs, controller-first, built in Unity 6 (or Godot with a porting partner). Team: four. Lead: Windows on Steam. Targets: Steam Deck (verification) and Switch.

**Step 1: fit.** Roguelite: PC A, Steam Deck A, consoles A (table). Gamepad-first design makes both additions realistic.

**Step 2: contract**

- `meta.platforms`: `["windows", "linux", "switch"]` with macOS deferred (listed in `scope.wont`).
- `meta.input`: `["gamepad", "mouse_keyboard"]`. Touch only for Switch handheld menus if desired (optional).
- `meta.orientation`: `landscape`.
- Risks added: no devkit yet; Switch memory limit unknown until programme access; certification time; ratings.

**Step 3: Steam Deck (cost 5 to 15 percent)**

1. Make every menu gamepad-navigable and add glyph switching (Deck, Xbox glyphs).
2. Check text: the smallest on-screen font is at least 9 px at 1280x800, target 12 px.
3. Remove launcher or dialog needing a mouse; use the Steamworks on-screen keyboard for name entry.
4. Add a Deck preset: 800p, 40 or 60 fps, Medium effects; test 30 minutes in Game Mode for battery and thermals.
5. Verify against Valve's published criteria (`references/saves-and-platform-rules.md` section 6); submit through Steamworks (`pc-web-release`).

**Step 4: Switch (cost 30 to 80 percent)**

1. Apply to the platform holder's developer programme (`console-pathway`). Until approved, do not plan dates.
2. After approval and devkit: pick the in-house port or a porting partner. Unity has Switch support listed on its system requirements page; Godot would need a middleware or porting house route (https://godotengine.org/consoles/).
3. Performance: budget for the original Switch (4 GB class memory, 720p handheld, 1080p docked, public figures) if supporting it, or for Switch 2 (1080p handheld, up to 4K docked) if targeting only that; decide in the contract. The original Switch version also runs on Switch 2 hardware subject to the platform's rules (verify in the programme).
4. UI: handheld (small screen, 720p or 1080p) and docked (TV) layouts; touch screen optional; platform button names; no quit item; suspend and resume; save via platform API; remove PC-only settings (window mode, resolution list).
5. Content: texture and audio budgets lowered; load times; dynamic resolution; 30 fps fallback in heavy rooms.
6. QA: certification rounds, ratings, localisation requirements.

**Step 5: sequence**

| Month | Work |
|---|---|
| 0 to 6 | Windows build and Steam early access or release; gamepad-first design; Deck-ready UI from the start |
| 6 to 7 | Deck pass and verification submission |
| 3 to 6 (parallel) | Apply to console programme; get devkit; ask a porting partner for quotes |
| 7 to 12 | Switch port, certification, ratings |
| 12 | Switch launch; patch parity plan |

(These month figures are estimates.)

**Risks**: memory on Switch is the usual blocker; anti-cheat or middleware that does not support the target; the patch cadence now spans multiple platforms (certification delays make fixes slower on consoles), so plan feature parity rules (`liveops`, `production`).

## 8. Worked plan C: web-first casual game adding mobile

**Game**: a browser casual game (short rounds, 2D), ad-funded on web portals, built with Defold or Godot (Compatibility renderer). Team: one person. Lead: web desktop. Goal: mobile browser first, then native apps.

**Step 1: fit.** Casual: web desktop A, web mobile A, phone native A. Console D.

**Step 2: contract**

- `meta.platforms`: `["web", "ios", "android"]`; `meta.input`: `["mouse_keyboard", "touch"]`; `meta.orientation`: `both` or locked to the portal's shape; decide per portal.
- Budgets: first load under 10 MB, total under 30 MB, 60 fps on desktop, 30 fps on a mid Android phone, memory under 400 MB for mobile browsers (estimates; `references/performance-tiers.md` section 5).

**Step 3: web-to-mobile-web (cost small)**

1. Touch controls through pointer events; large targets; no hover-only UI.
2. Layout reflows between desktop and portrait mobile; safe areas through CSS env values.
3. Memory and size: compress textures, reduce audio, test on a mid phone and an iPhone in Safari.
4. Audio unlock on first tap; fullscreen button; handle tab hidden (pause) and device rotation.
5. Saves in IndexedDB with export; persistence request after the first win; a warning about Safari eviction (`references/saves-and-platform-rules.md` section 2).
6. Portals: each has size, SDK and iframe rules (`pc-web-release`).

**Step 4: web to native mobile (30 to 60 percent if the engine is web-native; 10 to 25 percent if wrapped)**

| Route | Use when | Watch for |
|---|---|---|
| Re-export from Godot or Defold natively | The game is built in an engine that exports to iOS and Android | Native ads and IAP SDKs, store requirements, 16 KB page size, target API (`store-release`) |
| WebView wrapper (Capacitor and similar) | The game is JavaScript and performs well in a WebView | Store review rules about thin wrappers, performance and memory differ by OS WebView |
| Rewrite in a native engine | The game outgrows the browser | Highest cost |

**Step 5: monetisation shift.** Web portal ad revenue is mostly shared with the portal; mobile uses ad networks and IAP with different expectations (`monetization`, `marketing-ua`). Changing the ad model changes session design: rewarded video placements and interstitial spacing go into the contract (`monetization` section of contract).

**Step 6: evidence.** Performance on a real mid Android phone and an iPhone in browser and as an app; saves surviving reload and private-mode tests; sizes recorded per build.

**Risks**: iOS Safari memory limits, WebGL 2 issues in Safari noted by Godot's docs, save loss from eviction, portal policy changes, store rejection of thin wrappers.

## 9. Checks before you commit to a platform list

- [ ] Every platform in `meta.platforms` has a lead or supported status with an owner and a test device.
- [ ] Each platform's input is covered by every verb (section 1 of the input reference).
- [ ] Engine and plugins support every platform (section 1); no key plugin is missing a target.
- [ ] Console platforms have an application, devkit and porting plan, and dates assume approval time.
- [ ] Porting cost (section 4) and recurring cost are in the plan and the production schedule (`production`).
- [ ] Business model works on each platform (`monetization`, `store-release`).
- [ ] Rules and ratings per platform are noted (`references/saves-and-platform-rules.md` section 7).
- [ ] Deferred platforms are listed in `scope.wont` with the trigger that would re-open them.
- [ ] Volatile support facts (engine versions, browser support) were re-verified this month.
