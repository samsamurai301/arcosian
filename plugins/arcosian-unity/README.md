# arcosian-unity

Adapter plugin for the `arcosian` core plugin. It connects Claude to a Unity 6 project so the studio's gates (compile, tests, play mode, screenshot, build) run against the real Editor instead of guesses.

Requires the core plugin `arcosian` (declared as a dependency).

## What you get

- A C# language server (`.lsp.json` → `lsp/unity-csharp-lsp.mjs` → csharp-ls): compiler errors after each edit and symbol navigation for Unity scripts. See below.
- Skill `unity-bridge`: how to choose between `unity command`, `unity eval`, the CLI's MCP mode and CoplayDev unity-mcp; test and build recipes; the SceneBuilder pattern; licence notes.
- `.mcp.json` registers one server, `unity-cli`, which runs `unity mcp`.

## C# language server

The launcher runs [csharp-ls](https://github.com/razzmatazz/csharp-language-server) (MIT, Roslyn-based) in one of two modes, chosen per session:

| Mode | When | Coverage |
|---|---|---|
| Unity | The Editor has written its project files: a `.slnx` or `.sln` next to `Assets/` | Every script, compiled against Unity's own assemblies |
| Engine-free | No project files yet (Editor never opened, no licence, CI) | Assemblies whose asmdef sets `noEngineReferences` (the template's `Game.Core`, which holds the game logic). Every other `.cs` file gets no diagnostics rather than false "UnityEngine not found" errors |

Engine-free mode writes a small solution to the plugin data folder (one SDK-style project per engine-free asmdef, .NET Standard 2.1, C# 9 or the `-langversion` in `Assets/csc.rsp`, references between asmdefs kept), runs `dotnet restore` once, and rebuilds it only when an asmdef changes. `GS_UNITY_CSHARP_MODE=unity` or `engine-free` forces a mode; `GS_LSP_LOG=<file>` traces messages.

Setup:

1. Install the .NET 10 SDK (csharp-ls requires it), then `dotnet tool install --global csharp-ls` (tested with 0.28.0). The launcher also finds it in `~/.dotnet/tools` (Windows: `%USERPROFILE%\.dotnet\tools`) when that folder is not on PATH, or at `GS_CSHARP_LS`; on Windows it looks for .NET in `Program Files` too.
2. For Unity mode: the template's manifest includes the Visual Studio Editor package (`com.unity.ide.visualstudio` 2.0.28). In Unity, set Preferences > External Tools > External Script Editor to Visual Studio Code, Visual Studio or Rider, then click Regenerate project files. Since 2.0.24 the package writes SDK-style projects and a `.slnx` for VS Code and Visual Studio 2026. The template's `.gitignore` already excludes them.
3. Do not enable Anthropic's `csharp-lsp` plugin in the same project: when two servers claim `.cs`, Claude Code uses the first one registered and `/plugin` shows `LSP server "<name>" is not used for .cs files`.

Check it from the Unity project folder (the `unity-bridge` skill has the command with the installed path filled in):

```bash
node <plugin dir>/lsp/lsp-selftest.mjs --file Assets/_Game/Core/Sim.cs -- node <plugin dir>/lsp/unity-csharp-lsp.mjs
```

**Verified 2026-10-21 (csharp-ls 0.28.0, .NET SDK 10.0.402, macOS):** engine-free mode passes the self-test on the template: clean Core files, an injected error reported on its line and cleared, go to definition across files (`GameState` → `GameState.cs`), the Unity-dependent `BoardView.cs` silenced, with push and pull diagnostics, clean shutdown and no leftover processes. Unity mode passes with a stand-in SDK-style `.slnx`. Inside Claude Code 2.1.267 the server starts in engine-free mode, the `LSP` tool's go to definition and document symbols answer, and Claude Code receives csharp-ls's errors after an edit.

**Not verified:** real Unity-generated project files (needs the Editor and a licence). Delivery of the queued errors to the model shows the same Claude Code behaviour described in the Godot adapter's README: Anthropic's own LSP configuration behaved identically in the same setup.

## Install the tools

1. Install the free official Unity CLI (see the Unity docs link below) and make sure `unity` is on PATH.
2. In the project: `unity pipeline install` (adds the Unity Pipeline package), then `unity mcp configure claude` if you want the CLI to write its own client config.
3. Open the project in Unity 6.0 LTS or newer. Driving a running Editor needs 6.0+.
4. Restart Claude Code and run `/mcp` to confirm `unity-cli` connected.

## Server status

| Server | Status | Notes |
|---|---|---|
| `unity-cli` (`unity mcp`) | Registered | Confirmed against Unity's docs (Oct 2026): `unity mcp` is the Unity CLI's own MCP server and replaces the in-Editor server; `unity mcp configure claude` writes client config and `unity mcp configure --list` shows status. Source: https://docs.unity.com/en-us/unity-cli/replace-mcp-server-unity-cli |
| CoplayDev unity-mcp | Opt-in (snippet below) | Community, MIT, not affiliated with Unity. Server package `mcpforunityserver` on PyPI (10.3.0 in Oct 2026), console script `mcp-for-unity`, stdio by default. Not registered by default because it needs its Unity package in each project and two Unity bridges at once conflict. |
| Unity's in-editor MCP server (`com.unity.ai.assistant`) | Do not use | Reported deprecated in favour of the CLI; it also reportedly needed a Unity AI subscription. |

Prefer the CLI for everything it can do (`unity command`, `unity eval`, builds, tests): shell calls cost fewer tokens than MCP tool schemas. Use MCP only when you need a persistent session, play-mode screenshots or scene operations the CLI does not expose.

## Adding CoplayDev unity-mcp (opt-in)

CoplayDev/unity-mcp ("MCP for Unity") offers scene and GameObject creation, C# editing, asset management, tests, profiling and builds, with tool groups, multi-instance routing and Roslyn script validation. Steps (checked against the project README and its `Server/pyproject.toml`, Oct 2026):

1. In Unity: Package Manager > Add package from git URL: `https://github.com/CoplayDev/unity-mcp.git?path=/MCPForUnity#main`. Pin the release tag you reviewed instead of `#main` (or use `openupm add com.coplaydev.unity-mcp`).
2. Either let the package write client config (`Window > MCP for Unity > Configure All Detected Clients`), or add this to the project's `.mcp.json`:

```json
{
  "mcpServers": {
    "unity-mcp": {
      "command": "uvx",
      "args": ["--from", "mcpforunityserver==10.3.0", "mcp-for-unity"],
      "env": { "DISABLE_TELEMETRY": "true" }
    }
  }
}
```

   `DISABLE_TELEMETRY` (also `UNITY_MCP_DISABLE_TELEMETRY`) turns off the server's telemetry, per its `core/telemetry.py`. Requires Python 3.10+ through `uv`.
3. Run only one Unity MCP server at a time against one Editor; two bridges fighting over the same domain reload are a common source of "Editor busy" errors. If you enable CoplayDev, disable `unity-cli` in `/mcp` for that project.

Review the source before running any third-party server: it executes with your user's rights and can modify the project.

## What this plugin runs, sends and fetches

- **Runs:** csharp-ls (your own install) through `lsp/unity-csharp-lsp.mjs`, and the `unity-cli` MCP server (`unity mcp`, your Unity CLI install).
- **Fetches:** in engine-free mode, `dotnet restore` downloads NuGet packages for a small generated project, once and again when an asmdef changes.
- **Sends:** nothing else off your machine.
- **Writes:** the generated C# project in the plugin data folder, never inside your Unity project.

## Safety

- Editor control can run arbitrary C# in your project (`unity eval`, script tools). Work on a clean git tree and commit before large agent sessions.
- Builds and test runs are fine to automate; store submission is not part of this plugin.
- The studio hooks still apply: provenance, budgets and the five gates live in the core plugin.

## Volatile facts (as of Oct 2026 - verify)

- The Unity CLI replaces the deprecated in-editor MCP server; it is described as free and separate from Unity AI. Source: https://docs.unity.com/en-us/unity-cli/replace-mcp-server-unity-cli
- CoplayDev/unity-mcp release cadence and tool count change monthly. Source: https://github.com/CoplayDev/unity-mcp
- Unity AI plans and MCP connection limits were disputed in forum threads; do not rely on them. Source: https://discussions.unity.com/t/mcp-versus-built-in-assistant/1719106
- csharp-ls 0.28.0 (2026-09-13) requires the .NET 10 SDK and loads `.slnx` files. Source: https://github.com/razzmatazz/csharp-language-server (CHANGELOG)
- Visual Studio Editor package 2.0.28 (2026-05-26); `.slnx` generation for SDK-style projects since 2.0.24. Source: the package CHANGELOG on packages.unity.com

## License

MIT.
