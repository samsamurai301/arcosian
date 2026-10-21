# arcosian-godot

Adapter plugin for `arcosian`. It connects Claude Code to **Godot's own GDScript language server** (type errors after each edit, go to definition, references, symbols), registers two community Godot MCP bridges used for **runtime verification** (the agent plays and inspects its own build), and ships the `godot-bridge` skill that explains when to use which tool and how it plugs into the five gates and the playtest runner.

Godot scenes and scripts are text, so file edits already cover most authoring. The language server checks those edits the way the Godot editor does; the bridges are for what files cannot tell you: what the running game actually does.

## Install

```
/plugin install arcosian-godot@arcosian
```

Requires `arcosian` (declared dependency) and Node 18+. Set the optional `godot_bin` config to your Godot 4.x binary.

## GDScript language server

Claude Code runs language servers over stdin/stdout; Godot serves its language server over TCP from inside the editor. `lsp/gdscript-bridge.mjs` (Node, no dependencies) closes that gap:

- Finds the project: `project.godot` in the folder you start Claude Code in, a parent folder, or up to three levels below.
- Starts a headless Godot editor on free ports (never Godot's default 6005/6006, which an editor you open later expects to own) and relays messages. The first edit of a `.gd` file starts it: about 3 seconds on the template; a project that was never imported is imported first.
- Covers Godot's gaps: answers `shutdown`/`exit` itself (Godot 4.7.2 replies "Method not found"), always sends Godot full document text, drops Godot-only notifications (a 60 KB class list at start), and maps file URIs back to the exact strings Claude Code sent, including paths with spaces and symlinks.
- Stops the headless editor when the session ends; a detached watchdog stops it even if the bridge is killed.

Godot is looked up in this order: the `godot_bin` option, `GODOT_BIN`, `GODOT`, `godot` or `godot4` on PATH, versioned Windows downloads on PATH (`Godot_v4.x-stable_win64*.exe`), `/Applications/Godot.app`. Each value may be the binary, a macOS `.app` or the folder holding Godot. On Windows, point it at `Godot_v4.x-stable_win64.exe` or its folder: the `_console.exe` twin next to it is used, because only the console build reliably prints to a pipe. The binary needs the `--lsp-port` option (any recent Godot 4; tested with 4.7.2). The core plugin's parse-check hook reads the same `godot_bin` option.

| Option | Effect |
|---|---|
| `godot_bin` | Godot binary for the language server and the MCP bridge |
| `godot_lsp_port` | Set 6005 (Godot's default) to use the language server of the editor you keep open instead of starting a headless one, so two editors never run on one project |

Plugin options reach the bridge through a SessionStart hook (`lsp/save-options.mjs` writes them to the plugin data folder). `.lsp.json` does not reference them because in Claude Code 2.1.267 any `${user_config.*}` in a language server's `env` stops the server from loading. Advanced overrides: `GS_GODOT_BIN`, `GS_GODOT_LSP_PORT`, `GS_GODOT_PROJECT`; `GS_LSP_LOG=<file>` traces every message. The editor's own output goes to `gdscript-lsp/godot-<hash>.log` in the plugin data folder (`~/.claude/plugins/data/<plugin id>/`).

Check it from your project folder (the `godot-bridge` skill has the command with the installed path filled in):

```bash
node <plugin dir>/lsp/lsp-selftest.mjs --file core/sim.gd -- node <plugin dir>/lsp/gdscript-bridge.mjs
```

**Verified 2026-10-21 (Godot 4.7.2, macOS):** the self-test passes on the template (clean files report no errors; an injected type error is reported on its line and clears when reverted; document symbols; go to definition; shutdown with no leftover processes), also from a project path with a space, on a project that was never imported, with incremental edits, in attach mode, and when the bridge is killed. Inside Claude Code 2.1.267 the server loads, the `LSP` tool answers, and Claude Code receives Godot's errors within milliseconds of an edit.

**Not verified:** in those Claude Code test sessions (non-interactive runs, and one interactive run started from inside another session) Claude Code queued the errors but never showed them to the model. Anthropic's own `clangd-lsp` configuration behaved the same way in the same setup, so the delivery step is Claude Code's, not this plugin's. In a normal session, look for `Found N new diagnostic issues` under an edit that breaks a script.

## Bridges

| Server | Strength | Status |
|---|---|---|
| `godot-satelliteoflove` | Deterministic stepping (frozen clock), live state as JSON, input injection, screenshots; read and write tools split so reads can be auto-allowed | Enabled. Launch command `npx -y @satelliteoflove/godot-mcp@4.1.11` (pinned) checked against the project README and the npm registry (Oct 2026) |
| `tugcantopaloglu/godot-mcp` | Headless `validate_script(s)`, `export_project`, `manage_export_presets`, runtime inspection, `game_touch` | **Opt-in, not in `.mcp.json`.** Its README documents running a local build, and the npm copy (`@tugcantopaloglu/godot-mcp` 1.0.0) lags the repo (3.x) |

**satelliteoflove setup:** install the editor addon into your project with `npx @satelliteoflove/godot-mcp@4.1.11 --install-addon /path/to/your/project`, then enable it in Godot under Project > Project Settings > Plugins > Godot MCP. Keep one editor running per client.

**tugcantopaloglu setup (optional):** clone and build the repository, then add this to your project's `.mcp.json` (the form documented in its README):

```json
{
  "mcpServers": {
    "godot-tugcantopaloglu": {
      "command": "node",
      "args": ["/absolute/path/to/godot-mcp/build/index.js"],
      "env": {
        "GODOT_PATH": "/path/to/godot",
        "GODOT_MCP_ALLOWED_DIRS": "/path/to/your/projects"
      }
    }
  }
}
```

`GODOT_MCP_ALLOWED_DIRS` restricts the bridge to the listed project roots; set it.

Never add an `npx -y <name>` entry for a package you have not checked on the npm registry: an unclaimed or look-alike name can be registered by anyone, and `npx -y` runs whatever it downloads.

## Not included on purpose

`Coding-Solo/godot-mcp` has a reported command-injection CVE history and looked stale at last check (see the skill's security section). Prefer the two bridges above.

## What this plugin runs, sends and fetches

- **Runs:** a headless Godot editor (your own Godot binary) for the GDScript language server, on free localhost ports, stopped when the session ends; a SessionStart hook (`node lsp/save-options.mjs`) that copies this plugin's options into its data folder; the `godot-satelliteoflove` MCP server.
- **Fetches:** `@satelliteoflove/godot-mcp@4.1.11` from npm the first time that server starts (exact version).
- **Sends:** nothing off your machine; the MCP server talks to its editor add-on over localhost.
- **Writes:** the editor's usual caches in your project's `.godot/`, and logs in the plugin data folder.

## Security

Keep bridges on localhost, run them only against projects you trust, and review tool permissions before auto-allowing writes. Details in `skills/godot-bridge/SKILL.md`.

## Volatile facts (as of Oct 2026 — verify)

- Godot 4.7.2 stable was current; both bridges were being updated in Sep-Oct 2026. Sources: https://github.com/godotengine/godot/releases ; https://github.com/satelliteoflove/godot-mcp ; https://github.com/tugcantopaloglu/godot-mcp
- Godot 4.7.2's language server: `--lsp-port` and `--dap-port` command-line options, full-text sync only, no `shutdown` handler (all observed with the self-test). Claude Code 2.1.267: `${user_config.*}` in a language server's `env` stops it from loading; plugin MCP servers are not affected (tested with a probe plugin). Language-server plugin format: https://code.claude.com/docs/en/plugins/components#lsp-servers
