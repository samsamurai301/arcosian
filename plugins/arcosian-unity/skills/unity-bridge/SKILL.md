---
name: unity-bridge
description: Drives a Unity 6 project through the C# language server (diagnostics after edits, LSP go to definition, references, symbols), the Unity CLI (unity command, unity eval, unity mcp) and CoplayDev unity-mcp for compile checks, EditMode and PlayMode tests, play mode control, screenshots, headless builds and procedural scene building. Use when asked to "find where this C# class is defined", "find all references", "C# language server not working", "run the Unity tests", "build the Android player", "screenshot the game in play mode", "create the scene from code", "unity mcp not connecting" or "which Unity automation tool should I use".
---

# Unity bridge

## When to use

Use the C# language server while writing scripts: compiler errors after each edit and symbol navigation without text search. Use the rest of this skill when a claim about a Unity game must be verified in the Editor or when Editor work must be automated: compile status, tests, play mode, screenshots, builds, scene and prefab generation. Do not use it to author C# or asset text; edit source files directly and keep diffs reviewable.

## Pick the channel

| Need | Channel | Why |
|---|---|---|
| Definition, references, members of a C# symbol | `LSP` tool (goToDefinition, findReferences, documentSymbol, workspaceSymbol, hover) | Answers from the compiler's model, not text search |
| Compiler errors in the file just edited | Language-server diagnostics after the edit | Seconds, no Editor needed for engine-free code |
| Install editors, headless build, run tests in CI | `unity` CLI, shell | No Editor session, cheap, scriptable |
| One-off Editor action or query | `unity command` / `unity eval` | Drives the open Editor directly, no MCP schema cost |
| Persistent session, many small scene ops | `unity-cli` MCP server (`unity mcp`) | Tool calls with structured results |
| Play-mode screenshot, profiler, scene hierarchy ops the CLI lacks | CoplayDev unity-mcp (opt-in; setup snippet in this plugin's README) | Broader tool surface, community maintained |
| Last resort, no Editor available | `Unity -batchmode -executeMethod` | Classic headless entry point |

Default order: CLI first, MCP second, community bridge third. Confirm exact subcommands with `unity --help`; they have changed between releases and this skill does not pin flags.

## Code intelligence (C# language server)

`lsp/unity-csharp-lsp.mjs` runs csharp-ls for the project and picks a mode at start:

- **Unity mode** when a `.slnx` or `.sln` sits next to `Assets/` (written by the Visual Studio Editor package): every script, real Unity references.
- **Engine-free mode** otherwise: only assemblies whose asmdef has `noEngineReferences` (in the template `Game.Core`). Files outside them get no diagnostics at all; that silence means "not checked", not "clean". Check those files with the Editor's compile gate.

Diagnostics are for iterating; the compile gate in the Editor (or the template's licence-free .NET harness for `Game.Core`) stays the evidence. If the user asks for full coverage, tell them to open the project in Unity once with an external script editor set (Preferences > External Tools) and click Regenerate project files.

Check the server from the Unity project folder:
`node ${CLAUDE_PLUGIN_ROOT}/lsp/lsp-selftest.mjs --file Assets/_Game/Core/Sim.cs -- node ${CLAUDE_PLUGIN_ROOT}/lsp/unity-csharp-lsp.mjs`
It prints PASS or FAIL per check; add `--also <file>` for files that must report no errors.

## Preflight (do once per session)

1. `git status` clean or committed. Agents can delete assets.
2. Confirm Unity 6.0 LTS or newer and that the project path is the one the CLI sees.
3. Check the console is clean after a compile. A red console blocks every later gate.
4. Note whether another bridge already holds the Editor. One bridge at a time.

## Gate recipes

**Compile gate.** Trigger a script refresh, wait for the domain reload to finish, read the console. Pass means zero errors; warnings are listed, not ignored. Never proceed on a stale console read.

**Tests.** The template in `arcosian/templates/unity-mobile/` splits Core (pure C#), Presentation and Editor assemblies. Run EditMode tests first (sim-core, fast, deterministic), PlayMode second. Report counts, failing test names and the first stack frame in project code. A flaky test is a bug in the test or in the determinism seam; do not retry until green without saying so.

**Play mode and screenshots.** Enter play mode, run the scripted playthrough (seeded RNG, fixed timestep), capture frames at named checkpoints (main menu, first level start, a win state, a fail state), exit play mode. Save images under the project's `.gamestudio/` evidence folder so the critic agent can open them. If a screenshot is black, the usual causes are: capture before the first rendered frame, UI on a camera not in the capture path, or a Game view at zero size.

**Builds.** Android and iOS player builds go through the template's BuildScript (an `-executeMethod` entry) so settings live in code, not in a hand-edited Editor window. Report: build time, output size, scripting backend, and the warnings list. iOS produces an Xcode project; signing and upload belong to the `ship` skill and fastlane, not this adapter.

## SceneBuilder pattern

Do not hand-write scene YAML. Instead:

1. Put a static `SceneBuilder.Build()` in the Editor assembly that creates the scene from code: camera, lights, canvas with a safe-area root, prefab instances, and wiring through serialized references.
2. Run it with `unity eval` or the MCP, or `-executeMethod` in batch mode.
3. Make it idempotent: delete-and-recreate the generated root, never append duplicates.
4. Save the scene and prefabs, then run the compile and test gates.
5. Commit the generated assets; keep the builder as the source of truth for regeneration.

Benefit: scenes become reviewable code, regenerate cleanly after a refactor, and the agent never edits YAML with unstable file IDs.

## Worked example: "does the merge animation fire?"

1. `SceneBuilder.Build()` creates the board scene.
2. Enter play mode with seed 42, inject two matching tiles through the Core API (not by simulating pixels).
3. Step N fixed frames; assert in a PlayMode test that the merge event was raised and the tile count dropped by one.
4. Capture a screenshot at the frame after the event; the critic checks the VFX is visible.
5. Evidence: test name and result, screenshot path, console clean.

## Troubleshooting

- "C# language server unavailable": the message names the cause (csharp-ls or the .NET 10 SDK missing, no Unity project near the session folder, or neither project files nor an engine-free asmdef). Install with `dotnet tool install --global csharp-ls`, or set `GS_UNITY_PROJECT` / `GS_CSHARP_LS`.
- `/plugin` warns `LSP server "<name>" is not used for .cs files`: Anthropic's `csharp-lsp` plugin is also enabled; disable one of the two.
- Diagnostics flag every UnityEngine type: the Unity-generated solution is stale or `Library/` is missing after a fresh clone; open the project in Unity once.
- "Editor busy" or timeouts: a domain reload is running; wait, then retry once. Repeated failure means two bridges or a modal dialog in the Editor.
- Tools missing after install: restart the Editor and Claude Code; check `/mcp`.
- Works locally, fails in CI: CI has no licence activation; see licence notes.

## Licence notes

- The CLI is reported free and separate from Unity AI; the Editor itself still needs a valid Unity licence, including on CI runners. Activate through your CI provider's documented flow and keep serials in secrets, never in the repo.
- CoplayDev unity-mcp is MIT and not affiliated with Unity; its README promotes commercial tools. Treat it as a third-party dependency and review updates.
- The deprecated in-editor MCP server was reported to require a paid Unity AI plan; do not build workflows on it.

## Safety

`unity eval` and script tools execute arbitrary C# with your user's rights. Do not run code you have not read, do not point them at projects containing secrets, and keep builds free of debug bridges (strip the Pipeline or MCP packages from release configurations).

## Volatile facts (as of Oct 2026 - verify)

- Unity CLI replaces the in-editor MCP server and can build, test and drive a running Editor on Unity 6.0+. Source: https://docs.unity.com/en-us/unity-cli/replace-mcp-server-unity-cli
- CoplayDev/unity-mcp: active, MIT, monthly releases. Source: https://github.com/CoplayDev/unity-mcp
- Which exact CLI subcommands cover play mode and screenshots was not confirmed in the research; test before depending on them.
- csharp-ls 0.28.0 needs the .NET 10 SDK; the Visual Studio Editor package writes `.slnx` for SDK-style projects since 2.0.24 (2.0.28 current). Sources: https://github.com/razzmatazz/csharp-language-server ; packages.unity.com
