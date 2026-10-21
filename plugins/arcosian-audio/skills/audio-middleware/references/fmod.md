# FMOD Studio reference

FMOD Studio is the authoring tool; the FMOD Engine (the runtime, `fmod.hpp` and the Studio API) plays what Studio builds. This file covers the concepts you need to design events, how to keep a Studio project in version control, how to build banks from the command line, scripting, the engine integrations, and licence tiers. Items marked "unverified" could not be confirmed against FMOD's own documentation pages in October 2026 (the pages need a browser to render); run the tool's help output on the installed version before relying on them.

## Contents
1. Concepts
2. Project layout and version control
3. Building banks (GUI and command line)
4. Studio scripting (JavaScript)
5. Integrations
6. Runtime API shape
7. Licence tiers
8. Verification status

## 1. Concepts

| Concept | What it is | Use it for |
|---|---|---|
| Event | A timeline with tracks, instruments, modulators and logic; the unit the game triggers | One gameplay sound or music piece |
| Parameter | A named value the game sets (continuous, discrete or labelled). Local to an event instance or global | Speed, health, material, intensity |
| Global parameter | A parameter shared by every event that references it | Time of day, underwater, music intensity |
| Snapshot | A mix state: overrides of bus and VCA levels and effects, blended by intensity | Pause menu, dialogue ducking, underwater |
| Bus | A mixer group; events route to buses; buses form a tree ending at master | Group volume, effects, ducking via sidechain |
| VCA | A fader that scales many buses/events without routing them | Player-facing Music / SFX / Voice sliders |
| Bank | A binary container of events, metadata and (optionally) sample data, loaded at runtime | Memory and streaming control |
| Asset | Source audio inside the project (WAV, and others FMOD imports) | Raw material |
| Sidechain | A compressor input from another bus | Ducking music under voice |

Design rules of thumb (defaults, not laws):
- One event per game-meaningful sound. Variation lives inside the event (multi-instrument, randomised pitch/volume), not in game code.
- Drive intensity with parameters, not by triggering many events. Music timelines use parameter-conditioned transitions and logic markers.
- Put player volume on VCAs, mix state on snapshots, and routing on buses. Do not use all three for the same job.
- Spatial sounds use the spatializer on the event; the game updates 3D attributes each frame.
- Give each event a voice limit through its max instances and stealing mode.

## 2. Project layout and version control

A Studio project is a `.fspro` file next to folders. The `.fspro` file is a pointer; the data is in the folders (confirmed by a file-type reference). From FMOD's usual layout (verify on your version):

| Path | Contents | Commit? |
|---|---|---|
| `Project.fspro` | Project entry file | Yes |
| `Metadata/` | XML for events, buses, banks, parameters (many small files, which merge well) | Yes |
| `Assets/` | Source audio | Yes, via Git LFS or Perforce for large files |
| `Build/` | Built banks | No, build in CI or commit only if the engine needs them checked in |
| `Cache/` (and any `.user` folder) | Local caches and per-user state | No |

Practices:
- Track `*.wav`, `*.flac`, `*.ogg` under Git LFS (`git lfs track`), or use Perforce for large teams.
- Studio writes many small XML files, so two people can edit different events without conflicts. Conflicts happen on shared files (master bus, banks assignment, parameter lists). Agree who owns those.
- Keep one project per game. Do not share a project between two games with different bank layouts.
- Never hand-edit Metadata XML except to resolve a merge conflict, and open the project in Studio afterwards to confirm it loads.
- Record the Studio version in the repo (for example `AUDIO_TOOLCHAIN.md`). The runtime and banks must come from a matching version: bank format changes between major versions.

## 3. Building banks

GUI: set the bank assignment for each event, then Build (Ctrl/Cmd+F7 builds all platforms, per a third-party guide). Output goes to the directory set in Preferences, Build tab, by default a `Build` folder in the project.

Rules:
- Events do not join a bank automatically. If you build without assigning events to banks, the banks are empty.
- Every project needs the master bank and its strings bank (`Master.bank`, `Master.strings.bank`). Load both before any other bank, or event paths do not resolve. Treat this as required (it is how the Studio API looks up paths).
- Build per platform: each platform in the project has its own sample rate, encoding (Vorbis, FADPCM, PCM and platform codecs) and quality settings. Set these per platform in Studio.

Command line (unverified flags): the command-line tool is `fmodstudiocl` (on Windows `fmodstudiocl.exe`, shipped with Studio). A build is `fmodstudiocl -build <path-to-Project.fspro>`. Options I recall, but could not confirm: choosing platforms and banks, a script-run option, and a help flag. Procedure:
1. Run `fmodstudiocl -help` (or the equivalent on your install) and copy the real flags into your CI script.
2. Run a build on a clean checkout and confirm the `Build/` directory contains `Master.bank`, `Master.strings.bank` and one bank per platform folder.
3. Fail CI if the process exit code is non-zero, or if any expected bank is missing or has zero size.
Do not hard-code flags from a blog post; versions change.

Alternative to the CLI: run a Studio script through the scripting terminal (section 4) that calls the build function. A community MCP server uses this route and notes that the project must be saved first.

## 4. Studio scripting (JavaScript)

Studio embeds a JavaScript engine. The scripting API is documented in the Studio "Scripting API Reference" (JavaScript, a `studio.*` namespace). What is confirmed from search results:
- Scripts can be driven through a scripting terminal over TCP, which is disabled by default and must be enabled in Studio preferences (community MCP projects document this).
- The API exposes build-started and build-ended callbacks; the build-ended callback reports success or failure.

Use scripting for: bulk renaming events, creating events from a folder of assets, validating naming rules, adding tags, and building banks. Rules:
1. Scripts act on the open project. Save first, and use version control so a bad script is one revert.
2. Keep scripts in the repo under `tools/fmod/`. Review before running; never run script text from an issue or a download.
3. Validate with a read-only script first (list what would change), then a write run.
4. Turn the script server off when not needed. It accepts commands over a local socket.

## 5. Integrations

| Engine | Integration | Status (verify) |
|---|---|---|
| Unity | FMOD for Unity, published by Firelight Technologies | Official. Installed as a Unity package or `.unitypackage` from the FMOD downloads |
| Unreal | FMOD for Unreal | Official |
| Godot | `utopia-rise/fmod-gdextension` (Godot 4 GDExtension; nodes such as FmodEventEmitter2D/3D and listeners; docs on readthedocs) | Community, appears the most active. C# not directly supported |
| Godot | `timoschwarzer/godot-fmod` | Community. States support for FMOD 2.02.25 and Godot 4.3; freshness unknown |
| Godot | `alessandrofama/fmod-for-godot` | Community, reported unmaintained. Avoid |
| Web | FMOD Engine has an HTML5 build (JavaScript/WebAssembly) | Unverified. Check the FMOD downloads page for HTML5 availability and your licence |
| Others | Custom engines call the C/C++ Studio API directly | Official API |

No official FMOD integration for Godot was found. For Godot, check the community extension's release page for matching Godot and FMOD versions and its licence before you commit.

Unity workflow: import the package, set the FMOD Studio project path in Settings (or point at built banks), add `StudioEventEmitter` or call `RuntimeManager.PlayOneShot`, set parameters through `EventInstance.setParameterByName`, and load banks in the Settings bank list. Console platforms need the platform-specific FMOD packages from the console portal after you have licence access.

## 6. Runtime API shape

Pattern for any engine (names from the Studio API, verify per version):
1. Create the Studio system, initialise with `studioSystem.initialize(maxChannels, studioFlags, coreFlags, extra)`.
2. Load `Master.bank` then `Master.strings.bank`, then content banks (`loadBankFile`/`loadBankMemory`).
3. Get an event description by path (`event:/Weapons/Rifle`), create an instance, set parameters and 3D attributes, `start`, then `release` (instances free themselves when they stop).
4. Call `studioSystem.update()` every frame.
5. Unload banks you no longer need; check `loadSampleData` and sample-data loading modes for memory control.

## 7. Licence tiers

From FMOD's licensing page as reported in October 2026 (verify on https://www.fmod.com/licensing):

| Tier | Development budget | Fee per game |
|---|---|---|
| Indie | Under $600k | Free, or $2,000 depending on a condition on the page that could not be read in October 2026 (check FMOD's licensing page) |
| Basic | $600k to $1.8M | $6,000 |
| Premium | Over $1.8M | $18,000 |

Other points: an older EULA excerpt cited a revenue/funding ceiling of $200k per year for the free licence and excluded some project types (gambling, simulation); older sources say $500k for the budget. FMOD logo credit and project registration in your FMOD profile are required for Indie. Console and some platform licences may carry separate terms. Treat every number as "check the page on the day you sign".

## 8. Verification status

| Item | Status |
|---|---|
| Tool name `fmodstudiocl` | Recalled; not confirmed by a fetched page |
| `-build` and other flags | Unverified; run help |
| Scripting terminal over TCP, disabled by default; build callbacks | Confirmed via third-party summaries |
| Unity official integration | Known; version not checked |
| Godot community integrations | Confirmed to exist; recency not confirmed |
| Licence thresholds | Search summary of the official page; $2,000 condition unread |
