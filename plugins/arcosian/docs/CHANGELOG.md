# Changelog

Versions before 0.3.0 were internal builds under the working name `game-studio`; their entries keep the names those builds had.

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
