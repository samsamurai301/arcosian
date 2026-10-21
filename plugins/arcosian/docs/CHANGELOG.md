# Changelog

Versions before 0.3.0 were internal builds under the working name `game-studio`; their entries keep the names those builds had.

## 0.4.0 (2026-10-21): any game, any platform, and an understanding layer

Core, `arcosian-godot`, `arcosian-unity`, `arcosian-vendors` and `arcosian-commerce` are at 0.4.0; four new adapters start at 0.4.0; `arcosian-blender` is unchanged at 0.3.1.

### Any game, any platform
- Platforms, input and orientation are the user's choice. `gs.py init` now requires `--platforms` (any of ios, android, windows, macos, linux, web, switch, playstation, xbox, other), takes `--input` (touch, mouse_keyboard, gamepad, motion, other; default from the platforms) and defaults orientation to portrait only for phone-only games. The contract and config record `input`; `new-game` asks for platforms and input instead of assuming iOS and Android.
- New codex skills: `platform-targets` (input and controls, platform UX, performance tiers, saves and platform rules, a platform matrix), `pc-web-release` (Steam, itch.io, web portals, other PC stores, signing and packaging) and `console-pathway` (programmes and access, certification and ratings, porting plans; public information only, console SDKs are under NDA).
- Nine new genre playbook files: shooters, action-adventure, platformer and metroidvania, survival and sandbox, simulation and management, MMO and live service, racing, sports and fighting, horror and narrative, PC strategy and card games. Two new case-study files: 15 PC and console games, 8 web and cross-play games.
- Skill and agent descriptions no longer assume mobile where the knowledge is general; mobile-specific skills point to the platform skills. Doctrine 6 is now "platform-native".
- Templates renamed `godot-mobile` to `godot-starter` and `unity-mobile` to `unity-starter`. The Godot template gains Windows, macOS, Linux and Web export presets (web without threads, so any static host works), keyboard (arrows, WASD) and gamepad (D-pad, left stick) input actions, pause and fullscreen actions, focus for keyboard and gamepad menus, a Quit button on desktop, and `<build> --headless -- --smoke` to check any exported build. The Unity template gains Windows, macOS, Linux and Web build methods and WASD and gamepad input.
- CI templates: desktop and web export jobs, and a smoke test of each desktop build on its own OS (Godot); a desktop and web build matrix (Unity).
- The release guard also asks before `steamcmd ... +run_app_build`, `+run_workshop_build`, `butler push`, Epic `BuildPatchTool -mode=UploadBinary|LabelBinary` and `msstore publish`.

### Understanding layer
- `gs.py map` indexes the project into `.gamestudio/map/MAP.md` (a compact summary to read before opening files) and `map.json`: scenes and nodes, scripts, classes, signals, autoloads, input actions, tuning keys, assets, tests and design documents. Godot and Unity in depth (Unity through .meta GUIDs), other engines by files and imports. Rebuilds re-parse only changed files; the session summary points at the map.
- `gs.py impact <file|class|autoload|tuning key|input action|feature>` lists the scenes, scripts and tests that depend on it, the done features whose new `paths` globs cover them, and which of the five gates to run again, with reasons. `build-feature` uses it for re-checks.
- `gs.py whatif --set KEY=VALUE` and the new `what-if` skill: the current and the proposed version on the same seeds through the Godot template's bots (`runner.gd --tuning=<overrides>`), `economy_sim.py` or `match3_sim.py`, with Wilson and Student t intervals and a verdict (improves, mixed, worsens, no clear effect, reject) against the contract's targets. Results are saved to `.gamestudio/whatif/`.
- `gs.py dashboard` writes `.gamestudio/reports/dashboard.html`: features and the five gates, loops as diagrams, the economy as a flow, bot win-rate and frame-time trends, what-if results, the dependency graph by folder, the asset gallery with licences and provenance, and the budget. One file, no external requests, light and dark themes.
- `gs.py feature add --path <glob>` records which code a feature owns.

### New adapters
- `arcosian-art`: skill `art-tools` (Aseprite, LibreSprite, Pixelorama, Krita; Spine, Rive, DragonBones; sheets, atlases and texture compression; Figma and Penpot; Substance and Houdini notes), `sprite_sheet.py` (inspect and check sheets per platform; Aseprite JSON to a Godot SpriteFrames `.tres`) and Figma's official remote MCP server.
- `arcosian-levels`: skill `level-editors` (Tiled, LDtk, Godot and Unity importers, level checks) and `level_import.py` (TMJ, TMX with CSV, base64, zlib or gzip, LDtk single-file and external levels into one format; reachability for top-down and platformer levels, dead ends and pacing; output for the core level audit).
- `arcosian-audio`: skill `audio-middleware` (FMOD Studio, Wwise, engine-native audio, adaptive music and mixing) and `waapi.py`, a minimal Wwise WAAPI HTTP client. No MCP server: neither vendor publishes one.
- `arcosian-community`: skill `community-ops` (GitHub for game teams, Discord and devlogs, Steam and itch.io community pages, crash and feedback triage) and GitHub's (read-only) and Sentry's official remote MCP servers. Every post stays human-approved.

### Community kit
- `extend` skill and `scripts/addon.py`: scaffold an add-on from `templates/addon/` and check it against the house rules (manifest, skill format, README disclosure, licence, pinned MCP launchers, secrets only through placeholders, self-tested scripts, the directory's file rules).
- `docs/EXTENDING.md`, `CODE_OF_CONDUCT.md` (Contributor Covenant 2.1 by reference), issue forms (bug, feature, connector proposal) and a pull-request template.
- `docs/CONNECTORS.md`, generated from `docs/connectors.json`: all 14 registered MCP servers with source, vendor, authentication and trust level (first-party, official, community). `tools/check_connectors.py` fails CI when a plugin registers a server that is not catalogued, unpinned or holding a literal secret.
- `audit_plugin.py --core` resolves an adapter's links to core skills and agents; `--max-description-chars` fails when skill and agent descriptions, which load into every session, pass a budget (CI: 34,000 characters; now 30,409, about 7,600 tokens). Four adapter skill descriptions were shortened to fit the 450-character target.

### Fixed
- Godot template: swipes and drags never reached the game on any platform. The swipe detector called `set_anchors_preset()` in `_ready`, which keeps a 0x0 rectangle once the node has a parent; `Ui.full_rect()` had the same trap. Both now use `set_anchors_and_offsets_preset()`. The scripted playthroughs and bots drive the simulation directly, so no earlier gate could see it. `tests/unit/test_input.gd` now fails on the old code and passes on the fix, and `run_tests.gd` runs tests on the first frame so tests can add nodes to the tree.
- The art adapter's `sprite_sheet.py --verify` now imports the texture before loading the `.tres`.

### Verified
- Godot 4.7.2 on macOS: Windows, macOS (universal, ad-hoc signed), Linux and Web exports of the template; the macOS build passes `--smoke`; the web build in a browser (menu by Enter and by click, arrow keys, mouse drags merging tiles); 34 unit tests and the static gate pass.
- What-if with the real template bots: `win_tile` 1024 to 512 gives MIXED (sessions fall from 561 s to 282 s, into a 240-360 s target; win rate rises from 0.85 to 1.0, out of a 0.80-0.90 band).
- Project map and impact on both templates (48 and 34 files); the dashboard rendered and checked in a browser in dark mode.
- A SpriteFrames `.tres` from `sprite_sheet.py` loads in Godot 4.7.2 with the expected animations, speeds and per-frame durations; `level_import.py` fails a Tiled map whose exit is walled off and passes it once a door is opened.
- Every self-test, the hook tests (40) and the gateway tests pass; all ten plugins pass `claude plugin validate`, and all nine adapters pass `addon.py check`.

### Not verified
- Unity changes (desktop and web build methods, WASD and gamepad input) are not compiled in the Unity Editor here; the engine-free core still builds and passes on .NET.
- Desktop builds launched on Windows and Linux, and the CI template jobs, run only in GitHub Actions.
- New adapter content was researched in October 2026; each file lists what could not be checked against the vendor's own pages (for example itch.io and Discord help pages that refused automated fetches).

## 0.3.2 (2026-10-21): ready for Anthropic's plugin directory (core 0.3.2, adapters 0.3.1)

### Fixed
- The directory's validator stopped at "Couldn't validate that repository": it refuses `.gitattributes` rules that rewrite file contents, line-ending conversion included, at the repository root or inside a plugin folder. The root `.gitattributes` is gone, and the Godot and Unity templates ship theirs as `gitattributes.example`: rename it to `.gitattributes` after copying a template. The Unity file also carries the Git LFS rules that were in `gitattributes-lfs.example`.

### Added
- Every plugin has an icon (`icon.png`, original artwork) and `documentationUrl`, `supportUrl` and `privacyPolicyUrl` in its manifest, as the directory asks. These fields need Claude Code 2.1.281 or later to pass `claude plugin validate --strict`; older versions warn about unknown fields and still load the plugin.

## 0.3.1 (2026-10-21): fixes from the first Windows CI run (core plugin only)

### Fixed
- Windows: the `gs.py` state lock and the parse-check hook's import lock did nothing, because both relied on the Unix-only `fcntl`. They now lock through `msvcrt` on Windows, so parallel agents can no longer lose updates to `features.json`.
- A gslib self-test assumed Unix paths; it now builds its outside-the-project path from the platform's own root.

### Verified
- GitHub Actions on Windows: both language servers with a real Godot 4.7.2 (the GUI build swapped for its `_console.exe` twin) and csharp-ls 0.28.0, and the Godot parse-check hook tests, passed on the first run.

## 0.3.0 (2026-10-21): first public release, as Arcosian

All six plugins are at 0.3.0.

### Changed
- Renamed for release: `game-studio` is now `arcosian` (display name Arcosian), the adapters are `arcosian-godot`, `arcosian-unity`, `arcosian-blender`, `arcosian-vendors` and `arcosian-commerce`, and the marketplace is `arcosian`. Commands follow (`/arcosian:studio`, agents `arcosian:<name>`). The project-state folder `.gamestudio/` and the `gs.py` tools keep their names.
- Every package an adapter runs through a launcher is pinned to an exact version: `@satelliteoflove/godot-mcp@4.1.11`, `@meshy-ai/meshy-mcp-server@0.6.4`, `firebase-tools@15.34.0`, `blender-mcp==2.0.0`.
- Eval cases moved out of the plugin to the repository's `evals/arcosian/`, so installs stay small (the core plugin now has 453 files).
- The Unity template's Git LFS rules moved to `gitattributes-lfs.example` (append them after copying the template): a plugin folder may not contain LFS filters.

### Added
- Repository files for public use: MIT `LICENSE` (also in every plugin folder), `PRIVACY.md`, `SECURITY.md`, `CONTRIBUTING.md`, `.gitignore`, `.gitattributes`.
- A "What this plugin runs, sends and fetches" section in every plugin's README.
- `homepage`, `repository` and publisher (`samsamurai301`) in every manifest.
- CI on macOS, Linux and Windows (`.github/workflows/ci.yml`): Python self-tests, hook tests, gateway tests, audit, JSON and syntax checks, `claude plugin validate --strict`, the Python launcher on real Windows, and both language-server self-tests with Godot 4.7.2 and csharp-ls 0.28.0 on Linux and Windows.
- `docs/research/`: the October 2026 research behind the design.

## 0.1.3 (2026-10-21): Windows support (Godot and Unity adapters 0.2.1)

### Fixed
- Hooks on Windows: every hook called `python3`, which a python.org install on Windows does not provide, so the five-gate checks and the release and secret guards would silently not run. Hooks now start in exec form as `node hooks/scripts/run-python.mjs <hook>.py` (no shell, so Git Bash, PowerShell-only setups, macOS and Linux behave the same); the launcher uses `python3`, `python` or `py -3`, skips the Microsoft Store placeholders and caches its choice. With no Python at all, each hook reports a visible, non-blocking error.
- Release and secret guards now cover Claude Code's PowerShell tool (on by default on Windows): `Get-Content`/`gc`/`type`/`certutil`/`[IO.File]::ReadAll*` of keystores, `.p12`, `.p8`, `.mobileprovision` or `.env` files are denied, as are Windows credential-store reads; store submissions ask first; `Remove-Item -Recurse`, `rm -r` and `rd /s` on project state ask first. Windows paths with backslashes are recognised on every host.
- Godot lookup (parse-check hook and GDScript bridge): accepts versioned Windows downloads on PATH (`Godot_v4.x-stable_win64.exe`), a folder, or a macOS `.app`, and swaps a Windows GUI build for its `_console.exe` twin; the hook now also reads the Godot adapter's `godot_bin` option. The bridge no longer refuses a Godot build that prints nothing for `--help`.
- Processes started by the bridges and launchers no longer open console windows on Windows; the C# launcher finds .NET under `Program Files` and ignores `.cmd` shims Node cannot start; the LSP self-test checks for leftover processes on Windows too.

### Added
- On machines where Python 3 is not `python3`, the SessionStart hook tells Claude which command to use for the plugin's scripts.
- `docs/SETUP.md`: a Windows section (Git for Windows, Node, the `py` launcher, Godot's `_console.exe` build, iOS through CI, installing the marketplace from a local folder).
- 14 hook tests (39 in total): PowerShell guards, the Python launcher on Windows-like PATHs (no `python3`, Store placeholder, only `py`, no Python, stale cache, exit codes and stdin), Godot lookup layouts.

### Verified (2026-10-21, macOS)
- Hook tests 39/39; in a real Claude Code 2.1.267 session the exec-form hooks ran through the launcher (SessionStart added the project summary, the PreToolUse guard denied `cat release.keystore`).
- GDScript bridge with Windows-named stand-ins for Godot: a GUI build given, the `_console.exe` twin used; a build that prints nothing for `--help` still starts; a versioned name found on PATH; a folder.

### Not verified
- Nothing in this release has run on a Windows PC yet.

## 0.1.2 (2026-10-21): language servers (Godot and Unity adapters 0.2.0)

### Added
- `game-studio-godot`: Godot's own GDScript language server for Claude Code. `lsp/gdscript-bridge.mjs` (Node, no dependencies) bridges Claude Code's stdio to the editor's TCP server: it finds the project, starts a headless editor on free ports (or attaches to an open editor with the `godot_lsp_port` option), answers `shutdown`/`exit` itself, sends full document text, drops Godot-only notifications, maps URIs back to the client's strings, and a watchdog stops the editor if the bridge dies.
- `game-studio-unity`: a Unity-aware C# language server. `lsp/unity-csharp-lsp.mjs` runs csharp-ls on the Editor's `.slnx`/`.sln` when they exist, and otherwise on a generated solution of the engine-free asmdefs (`noEngineReferences`), keeping Unity-dependent files silent instead of full of false errors.
- `lsp/lsp-selftest.mjs` in both adapters: a small LSP client that checks a server the way Claude Code uses it (clean file, injected error on its line and cleared, symbols, definition, clean shutdown, no leftover processes).
- Unity template: Visual Studio Editor package 2.0.28 in the manifest, so the Editor writes the project files the language server reads.

### Fixed
- Docs: marketplace README listed stale versions, a "Known issues" section that no longer exists, and omitted the Scenario and Adjust servers.

### Verified (2026-10-21, macOS)
- GDScript (Godot 4.7.2): the self-test passes on the template, including a project path with a space, a never-imported project, incremental edits, attach mode and a killed bridge.
- C# (csharp-ls 0.28.0, .NET SDK 10.0.402): engine-free mode passes on the template with push and pull diagnostics and cross-file go to definition; Unity mode passes with a stand-in SDK-style `.slnx`.
- Inside Claude Code 2.1.267: both servers load and start, the `LSP` tool answers (document symbols, go to definition), and Claude Code receives each server's errors right after an edit.

### Not verified
- Delivery of those errors to the model: in the test sessions Claude Code 2.1.267 queued them but never showed them to the model; Anthropic's own `clangd-lsp` configuration behaved the same way in the same setup.
- Unity-generated project files from a real Editor (needs a licence).

### Known limitation
- Claude Code 2.1.267 does not load a language server whose `env` contains `${user_config.*}` (plugin MCP servers are unaffected), so plugin options reach the Godot bridge through a SessionStart hook instead.

## 0.1.1 (2026-10-20)

### Fixed
- Godot iOS export: the preset now exports the Xcode project only (`application/export_project_only=true`) and leaves building and signing to fastlane; Godot CI and Codemagic inject `APPLE_TEAM_ID` before exporting. Verified locally: Godot 4.7.2 export plus an unsigned `xcodebuild` for generic iOS devices succeeds.
- Godot Android CI: export uses `--install-android-build-template`, required by the Gradle-based preset.
- Android export verified for real (2026-10-21): Godot 4.7.2 + JDK 17 + SDK platform 36 / build-tools 36.1.0 / NDK 29.0.14206865 produced a signed release AAB through Gradle; bundletool validates it; manifest shows `com.example.mergefive`, min SDK 24, target SDK 36, portrait, no extra permissions; arm64-v8a only; 16 KB page-size compliant (ELF LOAD alignment 0x4000, `zipalign -c -P 16` passes).
- Unity CI: the Android and iOS artifact uploads pointed at `build/...` while the build writes `Builds/...`; both artifacts would have been empty.
- Godot adapter: removed an `npx -y` entry for a package name that does not exist on npm (a typosquatting risk); `tugcantopaloglu/godot-mcp` is now documented as an opt-in local build.
- Godot template: screenshot capture no longer overwrites the player's real save file, and capturing the game screen first no longer crashes.
- Hooks: the Godot parse check no longer blocks valid scripts that use `class_name` types or preload unimported assets when the editor cache is stale.
- Cross-file conventions: `.gamestudio/` layout unified (adds `design/`, `art/`, `audio/`); currency kinds in the case studies match the schema; script semantics in worked examples match the real scripts.

### Added
- `tools/perf/perf_probe.gd` in the Godot template: the perf gate now produces a perf-report JSON (windowed or headless CPU-only); Godot CI runs it as an informational smoke test.
- `gs.py validate --cross` / `gslib.cross_check()`: cross-document checks (duplicate ids, dangling references, missing evidence).
- `studio-gateway`: providers checked against official docs (Gemini Interactions API, OpenAI GPT Image 2.5, Recraft V4.1, Tripo v3, Meshy 7.1, Stable Audio 3); chained 3D stages (rig, refine) with refunds on failure; `test/live-smoke.mjs` for one capped real call with your own key; 49 test groups.
- Unity template: pinned to Unity 6.3 LTS (6000.3.26f1) with package versions checked against Unity's registry; `tools/dotnet-harness/` runs `Game.Core` and the EditMode tests on the .NET SDK without a Unity licence (20/20 pass); Unity CI gains a licence-free core-tests job.
- Adapters: Scenario (vendors) and Adjust (commerce) registered after checking their official docs; Unity CLI, CoplayDev `mcpforunityserver`, `blender-mcp` and ComfyUI launch details confirmed.
- Knowledge: about 40 flagged facts confirmed or corrected with sources (store dates, developers, legal and regulatory items); 197 source links checked.

### Not verified (needs your accounts, licences or devices)
- Unity Presentation/Editor code in the Unity Editor (licence), signing with your own keys and store uploads (Apple and Google accounts), live paid generation calls (your keys), real-device input, haptics and performance, and the eval suite run.

## 0.1.0

Initial release of the core plugin and five adapters.

- 53 skills: 15 process skills (`studio`, `new-game`, `concept-lab`, `design-review`, `market-scan`, `deconstruct`, `build-feature`, `playtest`, `balance`, `optimize`, `asset-production`, `audio-production`, `ship`, `operate`, `postmortem`) and 37 codex skills with about 157 reference files.
- 24 agents with opus or sonnet routing.
- 9 workflows: concept-tournament, deconstruct-game, design-review, market-scan, build-feature, asset-batch, playtest-sweep, balance-pass, release-candidate.
- 19 Python scripts (stdlib only), 14 JSON schemas.
- `studio-gateway` MCP server with 8 providers, budgets, provenance and mock mode.
- Hooks for session state, release and secret guards, five-gate enforcement and state snapshots.
- Godot and Unity mobile templates, CI templates (GitHub Actions, fastlane, Codemagic), document templates, 8 eval cases.
- Adapters: godot, unity, blender, vendors, commerce.

### Verification at release

- `scripts/audit_plugin.py`: 0 errors, 0 warnings (53 skills, 160 reference files, 24 agents, 9 workflows).
- All 31 Python self-tests, the `studio-gateway` test suite (mock mode), 19 hook tests, workflow syntax checks and `claude plugin validate` on all six plugins and the marketplace pass.
- Godot template on Godot 4.7.2: static check (39 scripts), 23 unit tests, scripted playthrough and 100 bot runs pass.
- Not verified: the Unity template (Unity not installed), live paid provider calls, Android/iOS exports, and running the eval suite.
