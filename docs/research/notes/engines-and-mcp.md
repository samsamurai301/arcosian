# Game Engines and Engine MCP/Automation for AI-Agent-Driven Mobile Game Development (state as of 2026-10-18)

Research notes. GitHub stars, last-push dates and open-issue counts were pulled live from the GitHub REST API on 2026-10-18. Search budget ran out before Bevy mobile, Capacitor/WKWebView performance, and Unreal mobile build specifics could be searched; those are flagged in Gaps. Information older than 2026 is flagged **[DATED]**.

### Current engine versions (snapshot, Oct 2026)
- **Godot**: 4.7.2-stable (2026-08-18), 4.7.1 (2026-07-14); 4.7.0 shipped mid-June 2026. Sources disagree on the day: June 19 per Cinevva, June 18 per StraySpark. — [GitHub releases](https://github.com/godotengine/godot/releases); [Cinevva](https://app.cinevva.com/hi/news/2026-06-19-godot-4-7-released)
- **Unity**: Unity 6.3 LTS (Dec 2025, supported to Dec 2027). Unity 6.5 shipped June 15, 2026 and is already end-of-life ("upgrade to Unity 6.6 or above"). Unity is "progressing towards the 6.7 LTS". Unity 6.0 LTS support ends October 2026. — [CG Channel](https://www.cgchannel.com/2025/12/unity-6-3-lts-is-out-see-5-key-features-for-cg-artists/); [Unity Discussions 6.5](https://discussions.unity.com/t/unity-6-5-is-now-available/1723176); [Unity 6 release page](https://unity.com/unity-6-release)
- **Unreal**: UE 5.8 (released June 17, 2026). — [Pixels Design](https://www.pixelsdesign.it/blog/unreal-engine-mcp-claude-code-explained.html); [Ludus](https://ludusengine.com/blog/unreal-mcp-plugin-ue5-8-setup)
- **Defold**: 1.14.0 (2026-10-12). — [GitHub releases](https://github.com/defold/defold/releases)
- **Cocos Creator engine**: 3.8.8 (2025-12-16) is still the latest tagged release, but the repo saw pushes as recently as 2026-10-08. — [GitHub releases](https://github.com/cocos/cocos-engine/releases)
- **Bevy**: v0.20.0 (2026-10-08). — [GitHub releases](https://github.com/bevyengine/bevy/releases)
- **Web stacks**:
  - Phaser v4.2.1 (2026-07-09)
  - PixiJS v8.22.0 (2026-10-01)
  - three.js r186 (2026-09-24)
  - Babylon.js 9.30.0 (2026-10-08)
  - PlayCanvas engine v2.23.3 (2026-10-15)
  - Capacitor 8.5.3 stable / 9.0.0-alpha.8 (2026-10-07)
  - react-native-skia v3.7.0 (2026-10-18)
  - Sources: [phaser](https://github.com/phaserjs/phaser/releases), [pixijs](https://github.com/pixijs/pixijs/releases), [three.js](https://github.com/mrdoob/three.js/releases), [Babylon.js](https://github.com/BabylonJS/Babylon.js/releases), [PlayCanvas](https://github.com/playcanvas/engine/releases), [Capacitor](https://github.com/ionic-team/capacitor/releases), [react-native-skia](https://github.com/Shopify/react-native-skia/releases)

---

## Q1. Which MCP servers / editor-automation tools exist for each engine, and how mature are they?

### Takeaway
Unity and Godot have by far the deepest MCP ecosystems.
- **Unity**: CoplayDev/unity-mcp has about 15.1k stars and releases monthly. Unity's own in-editor MCP server, launched May 2026, is already deprecated in favor of a free official **Unity CLI**. The CLI has an MCP mode plus `unity command`/`unity eval` for shell-capable agents.
- **Godot**: there is no official server. Instead there are a dozen-plus active community servers, several built specifically for agent self-verification (deterministic stepping, input injection, screenshots, headless validation).
- **Unreal**: UE 5.8 ships an **experimental official MCP plugin**. The best community server (ChiR24 "EngineWire") is mature but smaller.
- **Cocos, Defold, Bevy**: only thin community servers.
- **Web stacks**: need no engine MCP, because the agent drives a browser.

### Cited Findings

**Unity: official**
- **May 4, 2026 open beta.** Unity AI entered open beta for all Unity 6 developers on May 4, 2026. It includes:
  - an in-editor AI Assistant with Ask, Plan and Agent modes
  - an AI Gateway that brokers third-party models (OpenAI, Anthropic, custom); Gemini is the announced backbone
  - a Unity MCP Server for external IDE agents
  - Unity AI "is not Unity Muse", which is described as the deprecated predecessor. — [Cinevva news](https://app.cinevva.com/news/2026-05-04-unity-ai-open-beta)
- **Official MCP tool categories** (May 11, 2026 Unity blog):
  - scene management ("read hierarchy, create/modify/delete GameObjects, manage scenes")
  - C# script create/read/modify
  - console log/warning/error access
  - component read/write
  - build settings inspection only (not builds)
  - custom C# tools
  - Requirements: Unity 6 (6000.0)+, the AI Assistant package, a Unity Cloud-linked project, and "an active trial or subscription to Unity's AI tools beta". — [Unity blog](https://unity.com/blog/unity-ai-mcp-how-to-get-started)
  - A secondary source additionally lists running play mode and capturing screenshots. — [Cinevva](https://app.cinevva.com/news/2026-05-04-unity-ai-open-beta)
- **Pricing controversy.**
  - Personal users reportedly need the $10/month Unity AI subscription to activate MCP (one concurrent connection).
  - Pro reportedly includes 3 MCP connections and 2,000 credits; Enterprise 5 connections and 3,000 credits. These figures are user-reported, not shown from the pricing page.
  - Threads titled "Call to make Unity MCP usage free" (July 2026) and "Request for official clarification…" (Aug 2026) were active.
  - An "AI Assistant 2.7.0 MCP Server 'Capacity Limit'" thread exists.
  - Users name Coplay and the open-source "Locus" agent as fallbacks.
  - Source: [Unity Discussions](https://discussions.unity.com/t/mcp-versus-built-in-assistant/1719106). It conflicts with the Unity blog claim (relayed via search summary) that MCP needs no credits.
- **In-editor MCP deprecated (≈Aug 2026), replaced by the Unity CLI.** Unity "has deprecated the MCP server component of the in-editor AI assistant package" (`com.unity.ai.assistant`). The replacement is the **Unity CLI**:
  - It has its own MCP server built on the Unity Pipeline package (`unity pipeline install`, `unity mcp configure claude`, `unity skill install <agent>`).
  - `unity command` and `unity eval` "drive the Editor directly, without MCP in between… faster and use fewer tokens than MCP".
  - It can install and manage Editor versions, manage projects, "run headless builds" and "run test suites".
  - Driving a running Editor needs Unity 6.0 LTS+.
  - The CLI "is free and separate from Unity AI… doesn't require a Unity AI subscription".
  - The doc page was "last updated 2 months ago" as of Oct 2026.
  - Source: [Unity docs: replace MCP server with Unity CLI](https://docs.unity.com/en-us/unity-cli/replace-mcp-server-unity-cli)
  - The page's search snippet advertises "play mode, tests, screenshots, live runtime control, and eval, all from your terminal". The fetched body only explicitly listed builds and tests. — [same page](https://docs.unity.com/en-us/unity-cli/replace-mcp-server-unity-cli)

**Unity: community (GitHub API, 2026-10-18)**
- **CoplayDev/unity-mcp** ("MCP for Unity"; the old `justinpbarnett/unity-mcp` URL now 301-redirects here)
  - 15,088 stars; last push 2026-10-17; 104 open issues; MIT
  - Releases: v10.3.0 (2026-10-04), v10.2.0 (2026-09-01), v10.1.x (Jul–Aug 2026)
  - "50 focused MCP tool entrypoints": create scenes and GameObjects, edit C# scripts, manage assets, run tests, profile, and build
  - Tool groups (vfx/animation/ui/testing), Roslyn script validation, multi-Unity-instance routing, a remote-hosted server with auth, and v10 asset generation
  - Not affiliated with Unity; the README promotes commercial "Aura" tools
  - Source: [GitHub](https://github.com/CoplayDev/unity-mcp)
- **IvanMurzak/Unity-MCP** ("AI Game Developer")
  - 4,492 stars; last push 2026-10-18; 58 open issues
  - Tools include:
    - `screenshot-camera`, `screenshot-game-view`, `screenshot-scene-view`, `screenshot-isolated`
    - `console-get-logs`
    - `editor-application-set-state` (start/stop/pause play mode)
    - `tests-run`, `script-execute`, `reflection-method-call`
    - prefab, material and package add/remove tools
  - Auto-generates agent "skills"; ships an `unity-mcp-cli` (`npx unity-mcp-cli setup-skills claude-code`)
  - Also works inside compiled games (runtime)
  - Source: [GitHub](https://github.com/IvanMurzak/Unity-MCP)
- **CoderGamester/mcp-unity**
  - 1,936 stars; last push 2026-10-11; 7 open issues
  - Tools:
    - `run_tests` (Unity Test Runner)
    - `get_console_logs`
    - `set_play_mode_status` (play/pause/stop/step one frame)
    - `recompile_scripts`
    - `batch_execute` (atomic, with rollback)
    - prefab, material and scene tools
  - Writes a project-local `.mcp.json` for Claude Code
  - Source: [GitHub](https://github.com/CoderGamester/mcp-unity)
- **Smaller Unity servers**:
  - AnkleBreaker-Studio/unity-mcp-server: 514 stars, claims "268 tools"
  - isuzu-shiranui/UnityMCP: 332 stars; the Editor serves MCP over HTTP
  - FunplayAI/funplay-unity-mcp: 266 stars; execute_code, input simulation
  - youichi-uda/unity-mcp-pro-plugin: 82 stars, 147 tools
  - Source: [GitHub search API](https://github.com/search?q=unity+mcp&type=repositories)

**Godot: no official server; community (GitHub API, 2026-10-18)**
- **Coding-Solo/godot-mcp**
  - 6,148 stars; **last push 2026-04-16 (~6 months stale)**; 75 open issues
  - Features: launch editor, run project in debug, capture debug output, start/stop, create scenes and add nodes, load sprites, export MeshLibrary, UID management (4.4+)
  - Uses the Godot CLI for simple ops. — [GitHub](https://github.com/Coding-Solo/godot-mcp)
  - Sources disagree on whether it is an editor-level bridge ([Summer Engine](https://www.summerengine.com/blog/best-godot-mcp-server)) or CLI/file-based ([Ziva](https://ziva.sh/blogs/use-claude-or-chatgpt-with-godot)).
  - Reported CVE-2026-25546 (command injection via projectPath) fixed in 0.1.1. — [Summer Engine roundup](https://www.summerengine.com/blog/best-godot-mcp-server) (secondary, vendor)
- **tugcantopaloglu/godot-mcp** (fork of Coding-Solo)
  - 492 stars; last push 2026-10-09; **157 tools**
  - Headless scene operations (no running game needed)
  - `validate_script`/`validate_scripts`: headless GDScript type/syntax check that returns structured errors
  - `export_project`: headless export builds, "CI/CD ready"
  - `manage_export_presets`
  - Runtime node inspection, spawn and scene change
  - `game_touch`: simulate touch and gestures
  - Source: [GitHub](https://github.com/tugcantopaloglu/godot-mcp)
- **satelliteoflove/godot-mcp**
  - 178 stars; last push 2026-10-02; 21 tools / 86 actions
  - Built around "letting an agent verify its own work":
    - deterministic playtesting (freeze game clock, step exact time slices or step until a condition holds)
    - live entity state as structured JSON ("no pixels, no guessing")
    - real input injection (actions, joypad, keys, mouse, text)
    - screenshots
  - Read and write tools are split so reads can be auto-allowed
  - One client per editor
  - Source: [GitHub](https://github.com/satelliteoflove/godot-mcp)
- **Other active Godot servers**:
  - yurineko73/Godot-MCP-Native: 856 stars, pushed 2026-08-03; a native GDScript MCP server with no dependencies
  - youichi-uda/godot-mcp-pro: 627 stars, pushed 2026-09-24, "162 tools"; paid Node server with a free addon per [Asset Library](https://godotengine.org/asset-library/asset/4961) and search summary
  - DaxianLee/godot-mcp: 549 stars
  - tomyud1/godot-mcp: 438 stars, pushed 2026-10-17
  - IvanMurzak/Godot-MCP: 295 stars, pushed 2026-10-18
  - HaD0Yun "GoPeak": 268 stars; 95+ tools including a GDScript LSP, DAP debugger and screenshot capture
  - wgt19861219/godot-mcp-enhanced: 100 stars; Godot 4.5–4.7, 33 tools / 199 actions, headless + editor + runtime layers
  - Erodenn/godot-mcp-runtime: 93 stars
  - GDAI MCP (3ddelano): 101 stars; paid ([gdaimcp.com](https://gdaimcp.com/))
  - ee0pdt/Godot-MCP: 620 stars, **stale since 2025-03 [DATED]**
  - Source: [GitHub search API](https://github.com/search?q=godot+mcp&type=repositories)

**Unreal: official**
- **UE 5.8 experimental "Model Context Protocol" plugin** (June 2026)
  - Embeds an MCP server in the editor process at `http://127.0.0.1:8000/mcp`
  - Config generator targets Claude Code, Cursor, VS Code, Gemini and Codex
  - A Toolset Registry exposes Python or C++ functions as tools
  - Shipped toolsets: SceneTools, ActorTools, MaterialInstanceTools, ObjectTools
  - Capabilities: spawn actors, configure lighting, create material instances, inspect Slate widgets, run automation tests
  - Limits: "experimental and incomplete"; no auth; localhost only; tool calls run serially on the game thread
  - Source: [VP Land](https://www.vp-land.com/stories/unreal-engine-5-8-embeds-an-mcp-server-so-ai-agents-can-drive-the-editor)
  - Conflicting detail: Pixels Design says tools come from a companion "AllToolsets" plugin covering actors, **Blueprints**, materials, Niagara and Sequencer, and that new tools require an editor restart. — [Pixels Design](https://www.pixelsdesign.it/blog/unreal-engine-mcp-claude-code-explained.html) (vendor)
  - Ludus (a competitor) says it discovers the project "one tool call at a time", so it is best for single-file edits. — [Ludus](https://ludusengine.com/blog/unreal-mcp-plugin-ue5-8-setup)

**Unreal: community (GitHub API, 2026-10-18)**
- **ChiR24/Unreal_mcp ("EngineWire")**
  - 958 stars; last push 2026-10-17
  - A native C++ editor plugin over Streamable HTTP (:3000) or stdio via Node
  - Builds levels, **Blueprints (whole event graphs in one batch)**, UMG, materials, GAS, and AI (BT/StateTree/EQS)
  - "Run Play-In-Editor with synthetic input, take screenshots… read logs, profile, run Python, and package builds"
  - Supports UE 5.0–5.8; needs a C++ project (prebuilt binaries for Blueprint-only projects); version 0.6.0-beta
  - Source: [GitHub](https://github.com/ChiR24/Unreal_mcp)
- **chongdashu/unreal-mcp**: 2,097 stars, but **last push 2025-04-22 [DATED/stale]**. — [GitHub](https://github.com/chongdashu/unreal-mcp)
- **flopperam/unreal-engine-mcp**: 1,109 stars; last push 2026-06-26; "now owned by Aura". — [GitHub](https://github.com/flopperam/unreal-engine-mcp)
- **Stale or new Unreal servers**: kvick-games/UnrealMCP (614 stars, stale 2025-06), runreal/unreal-mcp (116 stars, Python remote execution, stale 2025-06), GenOrca (145), IvanMurzak/Unreal-MCP (48, new). — [GitHub search API](https://github.com/search?q=unreal+mcp&type=repositories)
- **Commercial Unreal agents**:
  - Ludus AI ([ludusengine.com](https://ludusengine.com/blog/unreal-mcp-plugin-ue5-8-setup))
  - Aura ([tryaura.dev, via flopperam README](https://github.com/flopperam/unreal-engine-mcp))
  - "Claude Assistant" by Pixels Design: $49.90, 351 tools, UE 5.3–5.8 ([Pixels Design](https://www.pixelsdesign.it/blog/unreal-engine-mcp-claude-code-explained.html))

**Cocos, Defold, Bevy, web, Blender**
- **Cocos Creator**:
  - DaxianLee/cocos-mcp-server: 1,459 stars; last push 2026-07-08; Cocos Creator 3.8.0+. Scene, node, component and prefab ops with snapshot rollback; `project_build_system` controls the build panel, checks build status and manages the preview server; `debug_console` reads logs. — [GitHub](https://github.com/DaxianLee/cocos-mcp-server)
  - FunplayAI/funplay-cocos-mcp: 344 stars (`execute_javascript`). — [GitHub search API](https://github.com/search?q=cocos+mcp&type=repositories)
- **Defold**:
  - Fulviuus/defold-mcp: only 13 stars, pushed 2026-06-29, but a capable design. "Everything works headlessly — no Defold editor required". It drives bob.jar build/bundle for all platforms, hot-reloads changed scripts into the running game, screenshots and records gameplay video, and searches version-matched API docs. — [GitHub](https://github.com/Fulviuus/defold-mcp)
  - Other Defold MCPs have 0–19 stars.
- **Bevy**: natepiano/bevy_brp has 77 stars (MCP tools over the Bevy Remote Protocol); other Bevy MCPs have 0–2 stars. — [GitHub](https://github.com/natepiano/bevy_brp)
- **Web stacks**:
  - phaserjs/editor-mcp-server (for Phaser Editor) has only 36 stars and has been stale since 2025-09. — [GitHub](https://github.com/phaserjs/editor-mcp-server)
  - Godogen verifies Babylon.js and three.js games by capturing them in Chrome/Chromium with hardware WebGL2. — [Godogen README](https://github.com/htdt/godogen)
- **Blender (adjacent)**: ahujasid's server, now `ahujasid/mcp-for-blender` (redirected), has 31,548 stars and was pushed 2026-10-18. It is a "Community plugin… Not affiliated with the official Blender Foundation". — [GitHub](https://github.com/ahujasid/blender-mcp)
  - Godogen scripts Blender for 3D models and animation that generators don't make well. — [Godogen](https://github.com/htdt/godogen)

### Inferences
- **Maturity ranking for agent-driven loops.**
  1. Unity (CoplayDev, plus the official free Unity CLI with `eval` and tests)
  2. Godot: fragmented, but the best "self-verification" designs (satelliteoflove's deterministic stepping and JSON state; tugcantopaloglu's headless validate and export)
  3. Unreal: official plugin, but experimental, 5.8-only and serial
  4. Cocos
  5. Defold and Bevy: hobby-scale
- **Unity's official direction** (CLI plus skills plus `eval`, with MCP as a fallback) matches Claude Code's strengths: shell commands are cheaper than MCP tool schemas. A plugin should prefer the CLI where installed and keep CoplayDev MCP for play-mode screenshots and scene ops.
- **Godot's text formats** mean many "MCP tools" (creating nodes, attaching scripts) are unnecessary. satelliteoflove explicitly avoids duplicating what file edits can do. The MCP is needed mainly for runtime verification. That is a structural advantage for a code-generating plugin.
- **Risk.** Unity's official MCP story changed twice in about 4 months (launch in May, then deprecation). Pricing for the official path is unstable. Third-party MCPs are not affected by the deprecation.

### Gaps
- Unity CLI's exact screenshot and play-mode command list could not be confirmed from the fetched page body (only the snippet). Its GA/beta status and release date were not found.
- Epic's own UE 5.8 MCP documentation page was not fetched. The tool list relies on VP Land, Pixels Design and Ludus, which conflict on Blueprint toolsets.
- An "official Blender Lab MCP" is hinted at by repo bpy-dev/blender-mcp ("Independent enhanced distribution of Blender Lab MCP") but was not verified.
- A claim that MCP is a "core pillar" of UE6 (Early Access late 2027, from State of Unreal 2026) appeared only in search summaries and was not verified against Epic.

---

## Q2. Which engines support fully headless/CLI builds for iOS and Android, and how well can an agent verify gameplay without a human?

### Takeaway
- **Godot** has the cleanest headless story. A single binary runs `--headless --export-release <preset> <path>` driven by a text `export_presets.cfg`. `--script`/`--check-only` handle validation, and `--write-movie` with `--fixed-fps` gives deterministic video capture.
- **Unity** is fully scriptable via `-batchmode -executeMethod -buildTarget android|ios`, plus the new official Unity CLI for headless builds and test suites. It needs license activation and is heavyweight.
- **Defold** (bob.jar) and the **web stacks** (Vite + Capacitor) are also fully CLI.
- **Unreal** can package from the command line, but agent verification relies on community or experimental MCP.
- **iOS** final signing and IPA creation needs macOS/Xcode for every engine.

### Cited Findings

**Godot CLI**
- `--headless` "is **required** on platforms that do not have GPU access (such as continuous integration)".
- `--export-release` and `--export-debug` export using a preset defined in `export_presets.cfg`.
- `--export-pack` writes PCK or ZIP.
- Export templates must be installed, and the binary must be an editor binary.
- `--script` runs a SceneTree/MainLoop script. `--check-only` "Only parse for errors and quit".
- `--quit-after <n>` and `--import` (import resources and quit).
- `--write-movie <file>` forces `--fixed-fps`, giving deterministic frame capture.
- Source: [Godot docs: command line tutorial](https://docs.godotengine.org/en/stable/tutorials/editor/command_line_tutorial.html)

**Godot testing, mobile and C#**
- Godot 4.6 added **Android instrumented tests** on physical devices via Firebase Test Lab (the free tier limits the number of devices).
- Godot 4.5 added native Android debug symbols for the Play Console.
- Perfetto and Instruments tracing were added.
- 4.6 can mirror connected Android devices in the editor.
- Source: [Godot mobile update, Apr 11 2026](https://godotengine.org/article/godot-mobile-update-apr-2026/)
- Godot 4.7 has a per-platform export template downloader and a stable GABE (Android build environment with Gradle export). — [Godot 4.7 release page](https://godotengine.org/releases/4.7/)
- **C# on Godot mobile is still "experimental"** in the 4.7 docs for both Android and iOS. iOS can only be exported from macOS. C# cannot export to web at all. Android needs .NET 7+ and iOS .NET 8+. — [Godot 4.7 C# docs](https://docs.godotengine.org/en/4.7/tutorials/scripting/c_sharp/index.html)
- **Community MCP verification tooling for Godot:**
  - headless `validate_scripts` over git-changed `.gd` files
  - headless `export_project`
  - `game_touch` simulated touch
  - Source: [tugcantopaloglu/godot-mcp](https://github.com/tugcantopaloglu/godot-mcp)
  - frozen-clock deterministic stepping with inputs, plus JSON runtime-state digests to avoid spending vision tokens — [satelliteoflove/godot-mcp](https://github.com/satelliteoflove/godot-mcp)
- **Godogen's capture setup.** For unattended capture it requires `xvfb`, `vulkan-tools` and `ffmpeg`, and it produces a 15–20s "proof recording". The agent "judges results from the running game… not from a clean compile". — [Godogen README](https://github.com/htdt/godogen)

**Unity CLI and batch mode**
- `-batchmode` runs "without the need for human interaction" and exits with code 1 on failure.
- `-nographics` skips GPU initialization (so no GI baking).
- `-executeMethod` calls a static method in an Editor folder; throw an exception or call `EditorApplication.Exit` to fail.
- `-buildTarget` accepts `android` and `ios`.
- `-serial` requires `-batchmode`.
- `-quit` combined with `-runTests` quits before tests finish.
- Test args are documented in the Test Framework docs.
- Source: [Unity Manual: command-line arguments](https://docs.unity3d.com/Manual/EditorCommandLineArguments.html)
- The new Unity CLI "Run[s] headless builds" and "test suites", and `unity eval` drives the Editor directly. — [Unity CLI docs](https://docs.unity.com/en-us/unity-cli/replace-mcp-server-unity-cli)
- Agent play-mode and screenshot verification in Unity comes via community MCPs. Examples: `set_play_mode_status` with step-one-frame ([mcp-unity](https://github.com/CoderGamester/mcp-unity)), and `screenshot-game-view`/`screenshot-camera` ([IvanMurzak/Unity-MCP](https://github.com/IvanMurzak/Unity-MCP)).

**Unreal**
- The official MCP plugin can run automation tests. — [VP Land](https://www.vp-land.com/stories/unreal-engine-5-8-embeds-an-mcp-server-so-ai-agents-can-drive-the-editor)
- EngineWire runs PIE with synthetic input, screenshots and package builds. — [ChiR24/Unreal_mcp](https://github.com/ChiR24/Unreal_mcp)

**Defold**
- defold-mcp builds and bundles headlessly via bob.jar (JDK 17+), hot-reloads into a running game, and screenshots and records video. First builds "can run for minutes", so raise MCP tool timeouts. — [Fulviuus/defold-mcp](https://github.com/Fulviuus/defold-mcp)

**Cocos**
- The MCP can control the build panel and the preview server. — [DaxianLee/cocos-mcp-server](https://github.com/DaxianLee/cocos-mcp-server)

**Practitioner caveat**
- With Godot, "the agent reads the scene file, it does not run the scene", so without runtime tooling it can't play-test or read live debugger errors. — [Medium survey (search snippet; page returned 403)](https://chierhu.medium.com/claude-code-for-game-development-7a88fcd19992)

### Inferences
- **Headless-friendliness ranking:**
  - Godot ≈ Defold ≈ web: single-binary or Node CLIs, text configs, fast cold start
  - then Unity: works, but needs Editor install via Hub/CLI, license activation (`-serial` / `-manualLicenseFile`), slow project import, and macOS for iOS
  - then Unreal: multi-GB engine, long cook/package times, C++ toolchain
- **Recommended verification loop for a plugin:**
  1. Static check (Godot `--check-only` or validate_scripts; Unity Roslyn validation; `tsc` for web).
  2. Headless deterministic run with scripted input and state assertions (Godot `--script` or MCP stepping; Unity Test Framework PlayMode tests).
  3. Screenshot or `--write-movie` capture judged by a vision model.
  4. Device tests via Firebase Test Lab (Godot 4.6 instrumented tests).
- **Not cited:** for Unreal, `RunUAT BuildCookRun` is the standard CLI packaging path. For web, `vite build && npx cap sync && xcodebuild/gradlew` is the usual Capacitor flow. Both should be verified.

### Gaps
- Unity license activation requirements for headless CI in 2026 (e.g., GameCI, Personal-license batch mode) were not researched.
- Unreal BuildCookRun docs and mobile packaging times were not fetched (search budget exhausted).
- Capacitor build automation docs were not fetched.
- I found no source that measures agent success rates per engine.

---

## Q3. Mobile-specific strengths and weaknesses: build size, startup, battery/thermal, rendering, ad/IAP SDK ecosystem

### Takeaway
- **Unity (URP)** remains the strongest all-round mobile engine, with first-party ad mediation, IAP and analytics, tile-GPU-aware URP, and 30–50 MB minimal builds per one 2026 estimate.
- **Godot** is competitive for 2D and mid-tier 3D. Its mobile stability improved a lot in 2025–26, but monetization SDKs are mostly community-made (the Foundation maintains billing and StoreKit 2 plugins; AppLovin ships an official MAX plugin).
- **Unreal** produces 150–300 MB builds, and Lumen/Nanite don't run on mobile.
- **Defold** has the smallest builds and officially maintained MAX, LevelPlay and AdMob extensions.
- **Web stacks** are capped by WebView performance. WebGPU is now available on iOS 26+.

### Cited Findings

**Build size**
- Ocean View Games (May 2026; a Unity-specialist author with no methodology given): minimal builds are Unity 30–50 MB, Godot 30–60 MB (Android template about 40 MB before stripping), Unreal 150–300 MB. — [Ocean View Games](https://oceanviewgames.co.uk/blog/posts/unity-vs-godot-vs-unreal-mobile-games)
- **[DATED, ~2019–2020, biased source]** Defold forum benchmark (Unity 2019.4 vs Defold 1.2.170): Android APK Unity about 5.7 MB vs Defold about 1.6 MB; iOS IPA Unity about 9.8 MB vs Defold about 2.6 MB. — [Defold forum](https://forum.defold.com/t/build-size-auto-stripping-or-manual-configuration/1819?page=4)
- **[DATED, same forum]** Another post: Android Defold 3.3 MB, Unity 11 MB, Godot 7.1 MB. — [Defold forum](https://forum.defold.com/t/why-defold-instead-of-other-game-engines/65854/3)
- These conflict with Ocean View's 2026 figures, presumably because of modern 64-bit/AAB requirements and engine growth.
- **[DATED]** A Unity forum thread reports an empty 2D scene APK of about 20 MB (about 11 MB ARMv7-only), and installs larger than the APK. — [Unity Discussions](https://discussions.unity.com/t/apk-size-of-empty-scene-is-20mb-after-installation-on-phone-its-62mb/653413)

**Rendering and performance: Unity**
- **Unity 6.3 LTS (Dec 2025)**:
  - GPU Resident Drawer can cut CPU frame time by up to 50% in heavily instanced scenes on URP and HDRP (third-party claim).
  - URP and HDRP now share one compiler and API, a step toward a unified renderer for desktop and mobile.
  - Sources: [CG Channel](https://www.cgchannel.com/2025/12/unity-6-3-lts-is-out-see-5-key-features-for-cg-artists/); [Unity](https://unity.com/unity-6-release)
- **Unity 6.5 (June 2026)**:
  - **On-Tile Post Processing** runs HDR, tone mapping, color grading and vignette in one tile pass on Vulkan and Metal, with a Tile-Only mode.
  - **ThinLTO** Android engine builds plus Master IL2CPP give about a 5% average gain in startup, scene load and CPU frame time.
  - Experimental Swift project type for iOS.
  - Custom 2D lights and shadows, a RenderSprite API, and a 2D Profiler.
  - Source: [Unity Discussions](https://discussions.unity.com/t/unity-6-5-is-now-available/1723176)

**Rendering and performance: Godot**
- Ocean View says Godot offers Forward+ (Vulkan) or Compatibility (GLES3), with Compatibility as the default for mobile. It calls Godot competitive for 2D and mid-tier 3D but lagging on high-end 3D. — [Ocean View](https://oceanviewgames.co.uk/blog/posts/unity-vs-godot-vs-unreal-mobile-games)
  - Contradicted in part by Godot's own 4.7 page, which describes a dedicated **Mobile** renderer. With Vulkan subsampled images it "now matches or beats Compatibility in some benchmarks". — [Godot 4.7](https://godotengine.org/releases/4.7/)
- Godot 4.7 adds HDR output (including iOS), AreaLight3D, clearcoat improvements and per-pass environment UBOs. — [Godot 4.7](https://godotengine.org/releases/4.7/)
- Foundation contractors fixed Vulkan API usage and added GPU-driver workarounds. Crash rates for Kamaeru and Rift Riff dropped from about 4% to under 1%. Android spans more than 12,000 device models. — [Godot mobile update](https://godotengine.org/article/godot-mobile-update-apr-2026/)
- iOS Metal exports (Forward+/Mobile) now default to A12-or-newer devices; this was backported to 4.5.2. — [Godot 4.5.2 release notes, via search summary](https://godotengine.org/article/maintenance-release-godot-4-5-2/)

**Rendering and performance: Unreal**
- Lumen and Nanite "do not run on mobile devices" and fall back to traditional paths. The mobile renderer is described as desktop-first. — [Ocean View](https://oceanviewgames.co.uk/blog/posts/unity-vs-godot-vs-unreal-mobile-games)

**Rendering and performance: Defold**
- Defold 1.13 made Vulkan the default on Android and added a Light component and instanced models with morph targets. — [GameDev.net / Defold summer newsletter 2026](https://gamedev.net/news/5363-defold-summer-newsletter-2026/)
- Defold runtime targets iOS 15+ (arm64), Android 5.0+ (API 21), HTML5, desktop, and PS4/PS5/Switch. — [Defold FAQ](https://defold.com/faq/faq/)

**Rendering and performance: web**
- Phaser 4 is WebGL2 with no WebGPU renderer yet.
- PixiJS supports WebGPU but defaults to WebGL.
- three.js offers WebGPU via `three/webgpu` with automatic WebGL2 fallback.
- WebGPU is listed for Safari 26+ and iOS/iPadOS 26+.
- Source: [Cinevva WebGPU vs WebGL 2026](https://app.cinevva.com/guides/webgpu-vs-webgl-games)
- Phaser 4's SpriteGPULayer draws a million or more sprites in a single call at "roughly the cost of a few hundred", with reduced flexibility and 168 bytes per member (May 2026). — [Phaser news](https://phaser.io/news/2026/05/phaser4-spritegpulayer-performance)

**Ads and IAP ecosystem**
- **Unity** has first-party packages for major ad mediation and analytics. **Godot** relies "mostly [on] community plugins or manual native integration". **Unreal** is rated "Good" (Epic Online Services). — [Ocean View](https://oceanviewgames.co.uk/blog/posts/unity-vs-godot-vs-unreal-mobile-games)
- **Godot**:
  - The Godot Foundation maintains core plugins for **Google Play Billing, Google Play Games Services and StoreKit 2**; others live in the godot-sdk-integrations org. — [Godot mobile update](https://godotengine.org/article/godot-mobile-update-apr-2026/)
  - An official AppLovin MAX Godot plugin (Android and iOS) is published by "AppLovin Mobile Engineering"; the Asset Library lists v1.0.3 for Godot 4.0. — [AppLovin docs](https://developers.applovin.com/en/max/godot/overview/integration)
  - godot-iap is an OpenIAP-protocol cross-platform IAP plugin. — [dooboolab/Medium](https://medium.com/dooboolab/building-in-app-purchases-for-godot-engine-the-openiap-journey-112c98c765fd)
  - AdMob support is only through third-party plugins such as Thunder Plugins (undated). — [itch.io](https://thunderplugins.itch.io/admob-for-godot-4)
- **Defold**'s official extensions include AppLovin MAX 13.6.3, Unity LevelPlay SDK 9 and Google AdMob 4.2.1. — [GameDev.net / Defold](https://gamedev.net/news/5363-defold-summer-newsletter-2026/)

### Inferences
- **Monetization**: for a plugin that must ship ad-monetized F2P games end to end, Unity has the lowest integration risk. Godot needs per-SDK plugin wiring, which is agent-doable but brittle across SDK versions.
- **Visual quality ceiling on mobile**:
  - Unity URP ≥ Unreal mobile (Lumen/Nanite are unavailable anyway) > Godot Mobile renderer > Babylon/PlayCanvas/three.js in a WebView
  - For 2D: Unity 6.5's 2D lights ≈ Godot's dedicated 2D engine ≈ Defold > Phaser/Pixi (adequate for casual)
- **Size**: if download size matters (hyper-casual, emerging markets), Defold and web are smallest; Unity and Godot are similar; Unreal is disqualifying for casual.

### Gaps
- No credible 2025–26 measured benchmarks were found for **startup time, battery drain or thermal throttling** across engines. Ocean View explicitly gives none.
- No 2026 measured APK/IPA sizes with stated methodology (e.g., Calinou/godot-size-benchmarks, referenced in the Defold forum, was not fetched).
- Capacitor/WKWebView game performance and App Store review outcomes for WebView games were not researched (search budget exhausted).
- Bevy mobile maturity: the repo contains `examples/mobile` with an Android project and an Xcode project ([GitHub](https://github.com/bevyengine/bevy/tree/main/examples/mobile)), but production readiness on mobile was not verified.

---

## Q4. Licensing and fees as of 2026

### Takeaway
- **Unity**: no runtime fee (cancelled in 2024). Personal is free under $200K revenue+funding. Pro rose 5% on Jan 12, 2026 to $2,310/yr per seat. Official AI/MCP is gated behind a separate Unity AI subscription for Personal users, but the new Unity CLI is free.
- **Unreal**: 5% royalty above $1M lifetime gross per title (3.5% under Launch Everywhere).
- **Godot**: MIT, no fees.
- **Defold**: free, no royalties.
- **Cocos Creator**: free download, custom license.
- **Web libraries**: MIT or Apache-2.0.

### Cited Findings
**Unity**
- The Runtime Fee was scrapped (Sept 2024).
- Pro and Enterprise rose 5% from **Jan 12, 2026**. Pro costs **$2,310/yr or $210/month per seat**.
- Personal is free for up to **$200,000 revenue and funding**.
- Havok Physics is no longer bundled with Pro from Unity 6.3 (some Unity pages say 6.0 LTS, so this conflicts).
- Sources: [Unity pricing updates](https://unity.com/products/pricing-updates); [80.lv](https://80.lv/articles/unity-announces-its-upcoming-2026-price-changes); [CG Channel](https://www.cgchannel.com/?p=171673)

**Unity AI**
- Personal gets a 14-day trial with 1,000 credits, then **$10/month** for 1,000 credits. Pro, Enterprise and Industry include credits and MCP access. — [Cinevva](https://app.cinevva.com/news/2026-05-04-unity-ai-open-beta); [Unity Discussions](https://discussions.unity.com/t/mcp-versus-built-in-assistant/1719106)
- **Unity CLI is free** and needs no Unity AI subscription. — [Unity docs](https://docs.unity.com/en-us/unity-cli/replace-mcp-server-unity-cli)

**Unreal**
- 5% royalty on projects exceeding **$1,000,000 lifetime gross**. — [Meta Horizon docs (Apr 2026)](https://developers.meta.com/horizon/documentation/unreal/unreal-oculus-license/)
- Epic Games Store revenue is excluded from royalty calculation. — [Unreal Engine news](https://www.unrealengine.com/en-US/news/unreal-engines-improved-royalty-reporting-system)
- The **Launch Everywhere** program gives a 3.5% rate when launching on EGS simultaneously or first, including Android and "soon iOS". — [Seeles (secondary)](https://www.seeles.ai/resources/blogs/unreal-engine-pricing-royalties-and-licensing-guide)
- The UE 5.8 MCP plugin is free and included in the engine. — [Pixels Design](https://www.pixelsdesign.it/blog/unreal-engine-mcp-claude-code-explained.html)

**Godot**
- MIT license per the [GitHub repo](https://github.com/godotengine/godot); "no fees or royalties". — [Ocean View](https://oceanviewgames.co.uk/blog/posts/unity-vs-godot-vs-unreal-mobile-games)

**Defold**
- "completely free of charge… No hidden costs, fees or royalties". — [Defold FAQ](https://defold.com/faq/faq/)
- Source is under the "Defold License, Version 1.0, May 2020". — [GitHub LICENSE](https://github.com/defold/defold)

**Cocos Creator**
- "Download for free", described as open source, with "More authorization types and business cooperation options" for custom needs. — [cocos.com](https://www.cocos.com/en/creator)
- GitHub reports the license as NOASSERTION (custom). — [GitHub](https://github.com/cocos/cocos-engine)

**Bevy**
- GitHub API reports Apache-2.0. — [GitHub](https://github.com/bevyengine/bevy)

**Web stacks** (GitHub API)
- Phaser, PixiJS, three.js, PlayCanvas engine, Capacitor and react-native-skia are MIT. Babylon.js is Apache-2.0.
- Sources: [phaser](https://github.com/phaserjs/phaser), [pixijs](https://github.com/pixijs/pixijs), [three.js](https://github.com/mrdoob/three.js), [PlayCanvas](https://github.com/playcanvas/engine), [Capacitor](https://github.com/ionic-team/capacitor), [Babylon.js](https://github.com/BabylonJS/Babylon.js)

### Inferences
- A plugin generating many games for many users fits zero-royalty, zero-seat engines best: Godot, Defold and web.
- Unity is fine for users under $200K, but each successful title above the threshold needs Pro seats.
- Unity's AI/MCP pricing is still in flux; avoid depending on the official in-editor MCP.

### Gaps
- Cocos Creator royalty terms and the exact license text were not found.
- Unity's official AI pricing page was not fetched directly; MCP connection and credit quotas are user-reported.
- Unreal's EULA was not fetched; the 3.5% Launch Everywhere details come from a secondary source.

---

## Q5. What do practitioners report about Claude Code / Cursor / agents with each engine? Which engine do AI-native studios favor?

### Takeaway
Practitioner consensus in 2026, mostly anecdotal, is that **Godot is the easiest engine for Claude Code**. Its plain-text `.tscn`/`.tres`/`project.godot` files are readable and editable. The main pitfalls are LLM-invented resource UIDs and GDScript hallucinating Python idioms.
- **Unity** works but needs more manual intervention (YAML scenes with GUID references, .meta files), and its MCP bridges have been flaky.
- **Godogen**, the most prominent open-source autonomous game generator, supports Godot (C# or GDScript), Bevy, Babylon.js and three.js. It does **not** support Unity or Unreal.
- No AI-native studio with verified shipped mobile titles was found.

### Cited Findings
**Godot vs Unity file formats and language**
- Godot's 10-line `.tscn` is "the entire scene". Unity scenes are "hundreds of lines of dense, ID-heavy YAML", so for an AI it is "essentially reading a database dump".
- Generating Unity projects requires valid GUIDs, serialized MonoBehaviour data and linked .meta files.
- GDScript's smaller training corpus causes occasional hallucinated Python idioms.
- The author still recommends Unity for 3D-heavy, AAA-scale or C#-expert projects.
- Source: [dev.to, Mar 19 2026](https://dev.to/mistyhx/why-ai-writes-better-game-code-in-godot-than-in-unity-10hf)
- Counterpoint: Unity does have a text (YAML) scene format meant for version control and tooling. — [Unity Manual](https://docs.unity3d.com/Manual/TextSceneFormat.html); [HN comment by doctorpangloss](https://news.ycombinator.com/item?id=47146712)

**HN thread on "I'm helping my dog vibe code games"**
- Godot's text scene format was "a huge advantage"; Claude reads and edits .tscn directly.
- Unity's MCP bridge "often hung".
- Bevy's visuals and coordinate handling gave Claude trouble.
- LLMs invent placeholder UIDs in .tscn/.tres. Fixes: a duplicate-UID linter, or an AGENTS.md rule to generate IDs with `uuidgen`.
- Codex 5.2 reportedly skipped the linter more often than Claude.
- MonoGame (pure C#) also works well with Claude Code.
- Source: [Hacker News](https://news.ycombinator.com/item?id=47146712)

**Hands-on reports**
- A Japanese developer found Unity with Claude Code needed frequent manual work. After switching to Godot, "you can leave almost everything to the AI" (via search summary). — [note.com/zizochan](https://note.com/zizochan/n/n7a5c52819bba)
- A counter-view: Unity's closed source and large training footprint is argued as a plus; another commenter says closed source leaves the bot without a way to check engine API behavior. — [itch.io "unity to godot and back"](https://itch.io/blog/926428/unity-to-godot-and-back); [HN](https://news.ycombinator.com/item?id=47404012) (via search summary)

**Godogen** (htdt/godogen)
- 7,158 stars; last push 2026-10-16; MIT
- "Autonomous game development for Godot (C# or GDScript), Bevy, Babylon.js, and three.js with Claude Code and Codex". It builds, generates assets, runs the engine and "proves the result" with live URLs or recorded video.
- Godot C# gives "the fewest runtime surprises in long unattended runs", because `dotnet build` type-checks before running.
- Bevy's "API moves between releases faster than model training data catches up", so the agent reads the installed source.
- Godot is "the natural pick for 2D"; the web engines are 3D-first.
- Source: [GitHub README](https://github.com/htdt/godogen)
- Its author reported the best results with Claude Code + Opus 4.6 (March 2026). — [Gigazine](https://gigazine.net/gsc_news/en/20260317-godogen/)

**Unity AI's own agent**
- It handles scaffolding and boilerplate well but struggles with large prefab hierarchies, cross-scene references and performance-sensitive code. Plan mode is recommended for non-trivial work. — [Cinevva](https://app.cinevva.com/news/2026-05-04-unity-ai-open-beta)

**Studio templates and AI-native engines**
- **Claude Code Game Studios** (Donchitos): 26,822 stars, last push 2026-10-08, v1.1.3. A template of 49 agents and 72+ skills that "mirror real studio hierarchy" and supports Unity, Unreal and Godot. It is a workflow template, not a studio with shipped games. — [GitHub](https://github.com/donchitos/claude-code-game-studios); [aitoolly](https://aitoolly.com/ai-news/article/2026-04-19-claude-code-game-studios-transforming-ai-into-a-full-scale-development-environment-with-49-specializ)
- **Summer Engine**: an "AI-native game engine" built on a Godot 4 foundation that exports to iOS, Android and web, and is driven by Claude Code via MCP and CLI (vendor-style listing). — [Ludo.ai comparison](https://ludo.ai/compare/best-ai-game-makers); [Summer Engine](https://www.summerengine.com/godot-mcp)
- **Commercial AI agents** exist for Unity and Unreal (Aura, Ludus, Coplay), showing vendor investment in those engines. — [CoplayDev README](https://github.com/CoplayDev/unity-mcp); [flopperam](https://github.com/flopperam/unreal-engine-mcp); [Ludus](https://ludusengine.com/blog/unreal-mcp-plugin-ue5-8-setup)

### Inferences
- **Open-source autonomous builders favor Godot and web.** Godot's ecosystem has a Godot fork (Summer Engine), the largest generator (Godogen), and the most MCP servers. Vendor commercial agents cluster on Unity and Unreal, where paying studios are.
- **Godot pitfalls for the plugin to guard against:**
  - Lint for duplicate or invalid `uid://` values and generate them with `uuidgen` or by having Godot resave.
  - Use statically typed GDScript or C# for compile-time checks.
  - Inject current GDScript API docs, since model knowledge of Godot 4.7 APIs is likely incomplete.
- **Unity pitfalls:**
  - Avoid hand-writing scene and prefab YAML. Build scenes procedurally via editor scripts (`-executeMethod` or `unity eval`) or MCP.
  - Keep logic in C#, which LLMs write very well.

### Gaps
- No controlled, quantitative comparison of agent success per engine was found; all evidence is anecdotal.
- No verified case of a commercially shipped, AI-agent-built *mobile* game (any engine) with a postmortem was found.
- No GDC 2025/2026 talk on agent-driven engine development was located (search budget).
- Cursor-specific engine reports were not separately found.

---

## Q6. Final recommendation: primary engine for 3D-heavy mobile, one for 2D-heavy/casual, and rationale

### Takeaway
- **2D/casual (and default) primary: Godot 4.7.x with statically typed GDScript.** Reasons: text-diffable scenes, single-binary headless export, MIT license, the richest community MCP set built for self-verification, and the de facto choice of open-source autonomous generators. Mobile C# is still experimental, so use GDScript for mobile.
- **3D-heavy primary: Unity 6 LTS (6.3 now, 6.7 LTS upcoming) with URP**, driven by the free Unity CLI plus CoplayDev/unity-mcp. Reasons: highest mobile 3D quality and performance tooling (tile-based post, GPU Resident Drawer, ThinLTO), first-party ads/IAP, C# fluency, and the largest MCP project.
- **Not recommended:** Unreal for mobile (150–300 MB builds, no Lumen/Nanite on mobile, experimental MCP). Bevy (API churn, tiny MCP ecosystem). Web stacks only for hyper-casual or web-first titles.

### Cited Findings (supporting evidence, restated with sources)
**Godot**
- Plain-text scenes and single `project.godot`. — [dev.to](https://dev.to/mistyhx/why-ai-writes-better-game-code-in-godot-than-in-unity-10hf)
- Headless `--export-release` and `--check-only`. — [Godot CLI docs](https://docs.godotengine.org/en/stable/tutorials/editor/command_line_tutorial.html)
- MIT license. — [GitHub](https://github.com/godotengine/godot)
- C# mobile is experimental, C# web is unsupported. — [Godot 4.7 C# docs](https://docs.godotengine.org/en/4.7/tutorials/scripting/c_sharp/index.html)
- Mobile crash rate cut from about 4% to under 1%; Android instrumented tests. — [Godot mobile update](https://godotengine.org/article/godot-mobile-update-apr-2026/)
- Self-verifying MCPs. — [satelliteoflove](https://github.com/satelliteoflove/godot-mcp); [tugcantopaloglu](https://github.com/tugcantopaloglu/godot-mcp)
- Godogen's engine choice. — [Godogen](https://github.com/htdt/godogen)
- Lags on high-end 3D. — [Ocean View](https://oceanviewgames.co.uk/blog/posts/unity-vs-godot-vs-unreal-mobile-games)

**Unity**
- URP is built for mobile and ARM GPUs; first-party ads and analytics. — [Ocean View](https://oceanviewgames.co.uk/blog/posts/unity-vs-godot-vs-unreal-mobile-games)
- 6.5 On-Tile Post Processing and ThinLTO. — [Unity Discussions](https://discussions.unity.com/t/unity-6-5-is-now-available/1723176)
- Free CLI with headless builds and tests. — [Unity CLI docs](https://docs.unity.com/en-us/unity-cli/replace-mcp-server-unity-cli)
- CoplayDev has 15k stars and monthly releases. — [GitHub](https://github.com/CoplayDev/unity-mcp)
- YAML/GUID friction for agents. — [dev.to](https://dev.to/mistyhx/why-ai-writes-better-game-code-in-godot-than-in-unity-10hf)

**Unreal**
- Lumen and Nanite are not on mobile; 150–300 MB builds. — [Ocean View](https://oceanviewgames.co.uk/blog/posts/unity-vs-godot-vs-unreal-mobile-games)
- The MCP is experimental, 5.8-only and serial. — [VP Land](https://www.vp-land.com/stories/unreal-engine-5-8-embeds-an-mcp-server-so-ai-agents-can-drive-the-editor)

**Bevy**
- API churn outpaces training data. — [Godogen](https://github.com/htdt/godogen)
- Claude struggled with Bevy visuals and coordinates. — [HN](https://news.ycombinator.com/item?id=47146712)

**Defold**
- Headless MCP with hot reload exists but has 13 stars. — [defold-mcp](https://github.com/Fulviuus/defold-mcp)
- Official MAX, LevelPlay and AdMob extensions. — [GameDev.net](https://gamedev.net/news/5363-defold-summer-newsletter-2026/)

### Inferences

#### Agent-friendliness matrix (synthesis; ✅ strong, ⚠️ workable, ❌ weak)

| Criterion | Godot 4.7 | Unity 6 LTS | Unreal 5.8 | Cocos Creator 3.8 | Defold 1.14 | Bevy 0.20 | Web (Phaser/Pixi/three/Babylon/PlayCanvas + Capacitor) |
|---|---|---|---|---|---|---|---|
| Text/diffable scenes | ✅ .tscn/.tres; UID pitfalls | ⚠️ YAML + GUID + .meta | ❌ binary .uasset (inference, uncited) | ⚠️ JSON scenes (uncited) | ✅ text .collection/.go (uncited) | ✅ code-only ECS | ✅ code/JSON |
| Headless CLI build (Android/iOS) | ✅ `--headless --export-*`; iOS needs macOS | ✅ `-batchmode -executeMethod`; Unity CLI; license + macOS for iOS | ⚠️ UAT (uncited); heavy | ⚠️ (MCP build panel; CLI uncited) | ✅ bob.jar | ⚠️ cargo + Xcode/Gradle examples | ✅ Vite + Capacitor (uncited) |
| Language LLMs write well | ⚠️ GDScript (smaller corpus) / C# experimental on mobile | ✅ C# | ⚠️ C++ (slow compiles); Blueprints are graph assets | ✅ TypeScript | ⚠️ Lua 5.1 | ⚠️ Rust; API churn | ✅ TypeScript/JS |
| Run/test without GUI | ✅ `--script`, `--write-movie`, MCP stepping | ✅ batch-mode tests, MCP play mode and screenshots | ⚠️ MCP automation tests / PIE | ⚠️ | ✅ MCP headless run, screenshot, video | ✅ offscreen capture (Godogen) | ✅ headless Chrome / Playwright (inference) |
| Hot reload | ⚠️ (uncited) | ⚠️ domain reload (uncited) | ⚠️ Live Coding (uncited) | ? | ✅ (defold-mcp) | ⚠️ | ✅ Vite HMR (uncited) |
| MCP ecosystem | ✅ many, no official | ✅ largest + official CLI | ⚠️ official experimental + EngineWire | ⚠️ 1 popular | ❌ tiny | ❌ tiny | n/a (browser tools) |
| License | ✅ MIT | ⚠️ seats above $200K | ⚠️ 5% above $1M | ✅ free (custom) | ✅ free | ✅ Apache/MIT | ✅ MIT/Apache |
| Mobile perf ceiling | ⚠️ mid-tier 3D | ✅ | ✅ raw, but no Lumen/Nanite on mobile | ⚠️ (uncited) | ✅ 2D | ? | ❌ WebView-bound |
| App size | ⚠️ 30–60 MB (2026 est.) | ⚠️ 30–50 MB | ❌ 150–300 MB | ? | ✅ smallest | ? | ✅ small (uncited) |
| Visual ceiling 2D / 3D | ✅ / ⚠️ | ✅ / ✅ | ⚠️ / ✅ | ✅ / ⚠️ | ✅ / ❌ | ⚠️ / ⚠️ | ⚠️ / ⚠️ (WebGPU on iOS 26+) |

#### Recommendation rationale
- **2D-heavy/casual: Godot 4.7.x + GDScript (typed).**
  - Every artifact (scenes, resources, input map, export presets) is text, so the agent edits files directly. MCP is needed only for runtime verification.
  - The headless export pipeline is trivially scriptable.
  - Zero licensing friction.
  - The dedicated 2D engine is strong.
  - Mitigations: a UID linter, static typing, version-pinned API docs injected into context, and Foundation billing/StoreKit plugins plus the official AppLovin MAX plugin for monetization.
  - **Alternative for ultra-light hyper-casual:** Defold (smallest builds, best-maintained ad extensions among small engines), at the cost of Lua and a nascent MCP. Or Phaser 4 / PixiJS + Capacitor when web distribution (playable ads, web portals) matters and fast browser-based verification is valued.
- **3D-heavy: Unity 6 LTS + URP.**
  - Mobile rendering features (on-tile post, GPU Resident Drawer, SRP Batcher), Android startup gains, and the strongest ads/IAP/analytics stack give the highest "visually impressive and shippable" ceiling.
  - C# is the language agents write most reliably among engine languages.
  - The agent should build scenes and prefabs **procedurally via editor scripts** run through `unity eval` / `-executeMethod` or CoplayDev MCP, not by writing YAML.
  - Verification: Unity Test Framework PlayMode tests in batch mode plus MCP screenshots.
  - Pin to an LTS: 6.0 LTS reaches end of support in Oct 2026, so target 6.3 LTS now and 6.7 LTS when it ships.
  - Budget for macOS build hosts (iOS) and Unity license activation in CI.
- **If a single engine is mandatory:** Godot for both. It is more agent-friendly and has no fees, while accepting a lower high-end 3D ceiling (Ocean View) and community-maintained monetization plugins.
  - Godogen's choice of C# for unattended runs suggests C# may be preferable for 3D Godot projects on desktop. On mobile, C# remains experimental, so GDScript is the safer mobile default.
- **Unreal:** revisit only if UE6 (reportedly with MCP as a core pillar, unverified) improves mobile. For 2026 mobile, its build size, hardware and toolchain weight, binary assets, and an experimental MCP make it a poor fit for an automated plugin.

### Gaps
- The matrix cells marked "uncited" or "?" reflect general knowledge or missing data and need verification:
  - Unreal .uasset binary format and Blueprint diffability
  - Cocos scene format and CLI build
  - Defold text formats
  - hot-reload behavior per engine
  - Capacitor/WebView performance
  - Bevy mobile maturity
- No head-to-head benchmark of agent task completion across engines exists in the sources found.
- Godot's default mobile renderer conflicts between Ocean View (Compatibility) and Godot's own 4.7 page (Mobile renderer improvements); check Godot docs.
