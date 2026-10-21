# Unreal, Defold and Cocos Creator

Summary: when Unreal Engine is a defensible choice for a mobile game and what it costs you, how the experimental official MCP plugin in UE 5.8 changes agent workflows, and quick-start procedures for Defold (Lua, tiny builds, bob.jar headless builds) and Cocos Creator (TypeScript, web and native exports). Facts about versions, licences and tooling are volatile and listed with sources at the end; commands marked "verify" were not confirmed in the research notes.

## Contents
1. Unreal on mobile: decision
2. Unreal constraints
3. Unreal agent workflow and the official MCP plugin
4. Unreal build and verification
5. Defold overview
6. Defold quick-start
7. Defold agent workflow
8. Cocos Creator overview
9. Cocos Creator quick-start
10. Cocos Creator agent workflow
11. Choosing among the three
12. Volatile facts (as of Oct 2026 - verify)

## 1. Unreal on mobile: decision

Choose Unreal for mobile only when all of these hold:
1. The product's differentiator is high-fidelity 3D that Unity URP or Godot cannot reach with reasonable effort.
2. The target audience owns high-end phones (recent flagship tier) and accepts a large download.
3. The team has Unreal-experienced engineers and artists (C++ or Blueprint, Material Editor, Niagara).
4. The schedule and budget tolerate long iteration, long builds and large assets.
5. The monetization plan is compatible with the SDK situation (Epic Online Services is reported as adequate; third-party ad and IAP SDKs need native integration work).

If any fail, use `engine-unity` or `engine-godot`. For casual, puzzle, idle and most live-ops mobile games Unreal is the wrong tool.

## 2. Unreal constraints

| Area | Constraint | Consequence |
|---|---|---|
| Rendering | Nanite and Lumen do not run on mobile; the mobile renderer is a separate, desktop-derived path with fewer features | Art must be authored for the mobile path (baked lighting, simpler materials); desktop screenshots mislead |
| Size | Reported minimal builds in the 150-300 MB range (one blog; measure your own) | Install conversion and low-end storage suffer; plan asset streaming and compression |
| Assets | `.uasset` and `.umap` are binary | Poor diffs and merges; agents cannot edit directly; rely on editor automation (Python, C++, Blueprints via tools) |
| Code | C++ with slow compile; Blueprints are graph assets | Agent edits C++ well but iteration is slow; Blueprint logic needs tooling support |
| Build | UAT (`RunUAT BuildCookRun`) is the standard CLI path (not confirmed in notes; verify); iOS needs macOS and Xcode | Heavy CI machines, long cook times |
| Licence | Royalty above a lifetime gross threshold (verify current terms) | Model at expected revenue |
| Device | High memory and GPU needs | Narrower device support |
| Version coupling | Plugins and project must match the engine version | Upgrade effort per release |

Mitigations: set a mobile scalability profile early; use texture streaming and mobile-friendly materials; keep a content size dashboard; profile on device from week one; keep gameplay rules in portable C++ or a pure module with tests.

## 3. Unreal agent workflow and the official MCP plugin

UE 5.8 (June 2026) includes an experimental official Model Context Protocol plugin that embeds an MCP server in the editor process (localhost HTTP endpoint on a configurable port; the notes report 127.0.0.1:8000/mcp). Reported characteristics:
- A config generator targets several agent clients, Claude Code among them, so setup is generating the client config rather than hand-writing it (verify the exact flow in the engine docs; this is the closest thing to an "Epic plugin for Claude Code" in the notes).
- A Toolset Registry exposes Python or C++ functions as tools; shipped toolsets cover scene, actor, material instance and object operations; capabilities reported include spawning actors, configuring lighting, creating material instances, inspecting Slate widgets and running automation tests.
- Limits reported: experimental and incomplete, no authentication, localhost only, tool calls run serially on the game thread.
- A companion toolset plugin is reported to add Blueprints, materials, Niagara and Sequencer coverage (sources conflict; verify).

Community alternatives: the most mature in the notes is a TypeScript-based server (ChiR24 "Unreal_mcp") with play-in-editor, synthetic input, screenshots and package builds; several older servers are stale; commercial agents (Ludus, Aura, a paid Claude assistant plugin) exist. Check last-push dates and licences before use.

Usage rules:
1. Treat the MCP server as unauthenticated: bind to localhost only, run on trusted projects, close it when idle.
2. Prefer scripting through Unreal's Python editor scripting for repeatable tasks (create assets, set properties) and commit those scripts, like SceneBuilder in Unity.
3. Use MCP for inspection, small edits and tests; do not rely on it as the sole record of changes.
4. Keep tool timeouts generous; editor operations and shader compiles can be slow.

## 4. Unreal build and verification

Steps (verify commands against the docs for your version):
1. Project settings: Android and iOS platform setup, mobile scalability, texture compression (ASTC), target architectures (arm64), package name and version.
2. Cook and package with UAT: `RunUAT BuildCookRun -project=<path.uproject> -platform=Android -clientconfig=Shipping -build -cook -stage -pak -archive -archivedirectory=<dir>` (typical shape; flags vary).
3. Android signing via project settings and environment-provided keystore; iOS signing via Xcode and provisioning profiles on macOS.
4. Verification: automation tests (Functional tests, Gauntlet or the Automation system), PIE runs with scripted input, screenshots via the screenshot comparison tools, and device profiling (Unreal Insights, stat commands, platform profilers).
5. Record artifact size and cold-start time as evidence; check against budgets.

Agent hazards: editing binary assets blindly, assuming desktop features exist on mobile, long builds timing out tool calls (run in background and poll the log), and mixing engine versions.

## 5. Defold overview

Defold is a free engine (source-available licence) with a small runtime, strong 2D, a component model (game objects, collections, factories, GUI scenes), Lua 5.1 scripting (with Teal and TypeScript-to-Lua community options) and native extensions in C++/Java/ObjC for SDKs. Reported properties in the notes: iOS 15+ arm64, Android API 21+, HTML5, desktop, and console targets; Vulkan became the default on Android in 1.13; official extensions include AppLovin MAX, Unity LevelPlay and Google AdMob. Project and scene files are text (`.collection`, `.go`, `.script`, `.gui`), making them diffable and editable.

Strengths: smallest builds among the major engines (older forum benchmarks flagged as dated), fast startup, headless build tool, good 2D performance, stable APIs.
Weaknesses: Lua (smaller idiom for agents; use strict module style), 3D limited, smaller asset ecosystem, thin MCP tooling, editor required for some authoring tasks.

## 6. Defold quick-start

1. Install the editor from the official site; create a project from the Mobile or 2D template.
2. Structure: `main/` (bootstrap collection), `core/` (pure Lua modules, no `go.*`/`msg.*` calls), `gui/`, `assets/`, `input/*.input_binding`, `game.project`.
3. `game.project`: set title, bundle identifier, display size (portrait 1080x1920), orientation, Android package and version code, iOS bundle id.
4. Input: bind `touch` and `touch_multi`; handle `action_id == hash("touch")` in `on_input`, check `action.pressed/released`.
5. Messaging: scripts communicate with `msg.post(url, hash("event"), data)`; keep rules in pure Lua modules required by scripts.
6. Run: `F5` in the editor. Headless build with bob.jar (JDK 17+ per the notes):
```
java -jar bob.jar --platform arm64-android --archive --variant release build bundle --bundle-output build/android
java -jar bob.jar --platform arm64-ios --archive --variant release build bundle --bundle-output build/ios
```
(Flags for signing: keystore, key password, provisioning profile and identity options; read `java -jar bob.jar --help` for your version and supply secrets through the environment.)
7. Extensions: add the extension dependency URL to `game.project` Dependencies, fetch, and rebuild; native extensions build on Defold's cloud build server or a local one.
8. Safe area: use `defold-safe-area`-style calculation from `sys.get_display_info` plus platform specifics, or a community library; verify per version.
9. Tests: pure Lua modules can be tested with a small runner (busted, luaunit or a hand-written script) outside the engine using a system Lua 5.1 or LuaJIT; keep `core/` free of engine globals so this works.
10. CI: cache the bob.jar and the engine version; run `build` first (compile errors), then `bundle`.

## 7. Defold agent workflow

- Files are text; edit them directly but keep generated IDs consistent; Defold uses string ids and hashes rather than opaque UIDs.
- Verification: a community MCP (small) reportedly builds headlessly, hot-reloads, takes screenshots and records video; first builds may take minutes, so raise tool timeouts. Without MCP, run the engine with the built-in test harness or log output.
- Hot reload helps iteration but never ship without a clean build.
- Guard against Lua pitfalls: accidental globals (use `local`), 1-based indexes, `nil` vs `false`, `~=` operator, string concatenation with `..`.
- Add a lint step (luacheck) in CI.

## 8. Cocos Creator overview

Cocos Creator is a free-to-download editor and engine (custom licence; terms not confirmed in the notes) with TypeScript scripting, 2D and basic 3D, exports to web, mini-games, Android, iOS and others. It is popular in the Asian mobile and mini-game market. The notes report engine 3.8.8 as the latest tagged release with ongoing repository activity, and a popular community MCP server (scene, node, component and prefab operations with snapshot rollback, controlling the build panel and preview server).

Strengths: TypeScript (agent-friendly, static checking), web-first export, strong 2D tools, mini-game platform support.
Weaknesses: scenes and prefabs are JSON with internal ids (editable but fragile), CLI build documentation less visible in the notes (verify), English documentation depth, licence clarity, smaller Western SDK ecosystem.

## 9. Cocos Creator quick-start

1. Install Cocos Dashboard and the pinned Creator version; create a 2D project (TypeScript).
2. Layout: `assets/scripts/core/` (pure TypeScript, no `cc` imports), `assets/scripts/view/`, `assets/scenes/`, `assets/prefabs/`, `assets/resources/` (only when dynamic loading is needed), `settings/` and `profiles/` in version control as the docs advise.
3. Components: `@ccclass('BoardView') export class BoardView extends Component { @property(Node) cellPrefab: Node | null = null; ... }`.
4. Input: node events `Node.EventType.TOUCH_START/MOVE/END`; use `UITransform` for hit areas.
5. Design resolution: set in Project Settings > Project Data (portrait 1080x1920), fit width or height by device aspect, use `Widget` for anchoring and `SafeArea` component for notches.
6. Build: Build panel for Android/iOS/Web Mobile; the editor also supports command-line builds (documented as running the editor executable with `--project <path> --build "platform=android;debug=false"`; verify for your version).
7. Native: Android needs Android Studio, SDK/NDK paths in preferences; iOS needs Xcode; outputs are native projects you build with Gradle or Xcode.
8. SDKs: native plugins via JSB bridges (`jsb.reflection.callStaticMethod`) to Java/ObjC; check for maintained ad and IAP plugins before committing.
9. Tests: pure TypeScript core tests with Vitest or Jest in Node (zero engine dependency), plus manual device checks.
10. CI: pin the Creator version, cache engine, run the headless build step on a machine with a display or virtual display if required (verify).

## 10. Cocos Creator agent workflow

- Core logic in plain TypeScript with Node-based tests is the strongest agent loop.
- Edit scripts freely; avoid hand-editing `.scene` and `.prefab` JSON; create them via the editor or the MCP server with snapshot rollback.
- The `.meta` files carry UUIDs: never invent them; delete a meta only with its asset and let the editor regenerate.
- For web builds, verify in headless Chrome or Playwright before native builds.
- MCP caveat: only one popular server was found; check security and version coupling (Creator 3.8+).

## 11. Choosing among the three

| Situation | Pick |
|---|---|
| Premium high-end 3D, experienced Unreal team | Unreal |
| Tiny size, 2D, official ad extensions | Defold |
| TypeScript team, web and mini-game reach, 2D | Cocos Creator |
| Casual game, first project, agent-driven | consider `engine-godot` or `engine-unity` first |

Hard checks before committing to any of these: run the one-day spike in `references/engine-selection-matrix.md`, confirm the monetization SDK path, and confirm licence terms against expected revenue.

## 11b. Spike checklists per engine

**Unreal spike (two days, not one, because of build times)**
- [ ] Project created with the mobile preview rendering level; a stress scene with the intended materials and lighting.
- [ ] Android shipping package built and installed; size recorded.
- [ ] p95 frame time and thermal behaviour over ten minutes on a mid-tier and a high-tier phone.
- [ ] One Python editor script that creates an asset, run headless; one automation test run.
- [ ] Ad or IAP integration path identified (native plugin or Epic Online Services), with an owner.
- Go only if the size and frame budget hold on the mid-tier device.

**Defold spike**
- [ ] Template project exports with bob.jar for Android and iOS on a clean machine.
- [ ] Official ad extension added and a test ad shown.
- [ ] Pure Lua core tested outside the engine; one scripted playthrough passes.
- [ ] Touch input and safe-area handling confirmed on a notched phone.
- [ ] Install size and cold start recorded against the budget.

**Cocos Creator spike**
- [ ] Pinned Creator version builds Android and iOS native projects from the command line or documented flow.
- [ ] TypeScript core tests run in Node; the view layer loads the same core.
- [ ] A maintained ad or IAP plugin is identified and tested, or a JSB bridge is prototyped.
- [ ] Licence terms read and filed against expected revenue.
- [ ] Web build verified in a headless browser.

## 11c. Common failure modes

| Engine | Failure | Cause | Response |
|---|---|---|---|
| Unreal | Looks great on desktop, poor on phone | mobile renderer lacks Lumen and Nanite | author for the mobile path from day one |
| Unreal | MCP calls time out | serial game-thread execution, shader compile | raise timeouts, batch operations |
| Defold | Silent logic bug | accidental global or nil comparison | luacheck in CI, strict module pattern |
| Defold | Bundle fails on iOS | missing provisioning or identity options | read bob.jar help, supply via environment |
| Cocos | Scene reference broken | edited JSON or meta by hand | rebuild through editor or MCP with rollback |
| Cocos | Native build fails | SDK/NDK or Xcode path misconfigured | fix preferences, rerun on clean checkout |

## 12. Volatile facts (as of Oct 2026 - verify)

| Fact | Source |
|---|---|
| UE 5.8 released June 17, 2026 | https://www.pixelsdesign.it/blog/unreal-engine-mcp-claude-code-explained.html and https://ludusengine.com/blog/unreal-mcp-plugin-ue5-8-setup |
| UE 5.8 experimental MCP plugin: embedded server, config generator for several clients including Claude Code, toolsets, limits (experimental, no auth, localhost, serial game-thread calls) | https://www.vp-land.com/stories/unreal-engine-5-8-embeds-an-mcp-server-so-ai-agents-can-drive-the-editor |
| Community Unreal MCP servers and maintenance status | https://github.com/ChiR24/Unreal_mcp ; https://github.com/flopperam/unreal-engine-mcp |
| Lumen and Nanite not on mobile; minimal Unreal build 150-300 MB (one blog) | https://oceanviewgames.co.uk/blog/posts/unity-vs-godot-vs-unreal-mobile-games |
| Unreal royalty above a lifetime gross threshold | https://www.unrealengine.com/en-US/news/unreal-engines-improved-royalty-reporting-system |
| Defold 1.14.0; Vulkan default on Android since 1.13; official AppLovin MAX, LevelPlay and AdMob extensions | https://github.com/defold/defold/releases and https://gamedev.net/news/5363-defold-summer-newsletter-2026/ |
| Defold platform targets (iOS 15+, Android API 21+, HTML5, desktop, consoles) and free licensing | https://defold.com/faq/faq/ |
| Defold headless MCP (bob.jar, JDK 17+, hot reload, screenshots) | https://github.com/Fulviuus/defold-mcp |
| Cocos Creator 3.8.8 latest tag; free download, custom licence | https://github.com/cocos/cocos-engine/releases and https://www.cocos.com/en/creator |
| Cocos MCP server (scene/node/prefab ops, build panel control) | https://github.com/DaxianLee/cocos-mcp-server |
| UAT flags, Defold bob.jar signing flags, Cocos CLI build syntax | not in the notes; verify in each engine's official documentation |

## 13. Decision notes for the principal

- Record in the design contract: engine, version, renderer path, target device tier, size budget, SDK plan, and the kill criterion (for example "if the mid-tier phone misses p95 of 33 ms after two optimization passes, reconsider the engine").
- Keep sim-core portable (`game-architecture`) so a late engine change costs a presentation rewrite only.
- Revisit this file's volatile facts at every milestone; versions and tooling here change within months.
- Never let an experimental tool (Unreal MCP, small community MCPs) be the only path to a build; keep a scripted CLI path.
- If the spike is inconclusive, prefer the engine whose build and test automation you already trust.
- Escalate licence questions (Unreal royalties, Cocos terms, Unity seats) to `legal-ethics` before production starts.
