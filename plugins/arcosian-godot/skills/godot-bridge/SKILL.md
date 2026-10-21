---
name: godot-bridge
description: Uses the GDScript language server (diagnostics, go to definition, references) and the Godot MCP bridges to check and drive a running Godot 4 game, wired into the five gates and the playtest runner. Use when asked to "find where this function is defined", "check this script for errors", "verify in the running game", "simulate input" or "which Godot MCP tool should I use", or when the language server or MCP will not connect.
---

# Godot bridge

## When to use

Use the language server while writing GDScript: it reports type errors after each edit and answers symbol questions (definition, references, members) without text search. Use the bridges when a claim about the game must be checked **in the running game**, not in source: does the merge animate, does state match after N frames, does a touch on the button fire. Do not use either to author files; Godot scenes, scripts and resources are text, so edit them directly and keep diffs reviewable.

## Decide: file edit, CLI gate, or bridge

| Need | Use |
|---|---|
| Create or change scene, script, resource | File edit (omit hand-made `uid://` values; Godot regenerates them) |
| Find a definition, every caller, a class's members | `LSP` tool (goToDefinition, findReferences, documentSymbol, workspaceSymbol, hover) |
| Type errors in the script just edited | Language-server diagnostics after the edit (the core plugin's hook also parse-checks each edited `.gd`) |
| Parse and type check every script | CLI static gate `check_all.gd` (CI-safe), or the bridge `validate_script` for a quick single-file check |
| Unit tests | CLI `run_tests.gd` |
| Deterministic sequence with expected state | Playtest runner script mode (preferred, reproducible, CI-safe) |
| Inspect live state, poke a UI, try a one-off interaction | satelliteoflove bridge |
| Touch and gesture simulation on a running scene | tugcantopaloglu `game_touch` |
| Export from an agent session | `export_project` or the plain `godot --headless --export-release` command (prefer the CLI in CI) |

Rule: if a bridge session finds a bug, convert the repro into a playthrough script or unit test before fixing, so the gate keeps it fixed.

## Code intelligence (GDScript language server)

This plugin runs Godot's own language server through `lsp/gdscript-bridge.mjs`: it starts a headless Godot editor for the project on the first `.gd` edit (about 3 seconds; longer the first time a project is imported) and stops it when the session ends.

- **Diagnostics** after an edit come from the same analyzer the Godot editor uses. Treat an error as real and fix it before moving on; Godot often reports one mistake twice (the expression and the statement).
- **Navigation**: the `LSP` tool's goToDefinition, findReferences, hover, documentSymbol and workspaceSymbol work. Godot has no goToImplementation or call hierarchy; use findReferences instead.
- **Evidence**: diagnostics are for iterating. The static gate's evidence is still `check_all.gd` over every script.
- **Check the server** from the project folder:
  `node ${CLAUDE_PLUGIN_ROOT}/lsp/lsp-selftest.mjs --file <some .gd file> -- node ${CLAUDE_PLUGIN_ROOT}/lsp/gdscript-bridge.mjs`
  It prints PASS or FAIL per check (clean file, injected error on its line and cleared, symbols, clean shutdown, no leftover processes).
- **Editor already open?** Set the plugin option `godot_lsp_port` to 6005 so the bridge uses that editor's server instead of starting a second editor on the same project.

## Tool guide

**satelliteoflove/godot-mcp** (reported as around 21 tools): built for an agent to verify its own work.
- Freeze the game clock and step exact time slices, or step until a condition holds. Use this for anything timing-related instead of sleeping.
- Read live entity state as structured JSON rather than screenshots; cheaper and exact.
- Inject real input (actions, keys, mouse, text, joypad) to drive the game as a player would.
- Take screenshots only when a visual judgment is needed.
- Read and write tools are separate: allow reads, ask for writes.
- One client per editor: do not attach two agents to the same editor.

**tugcantopaloglu/godot-mcp** (fork of Coding-Solo, reported as around 157 tools; treat the number as approximate):
- `validate_script` and `validate_scripts`: headless type and syntax check with structured errors; run over changed files before launching anything.
- `export_project` and `manage_export_presets`: headless export; verify presets before blaming the exporter.
- Headless scene operations (no running game required) and runtime node inspection.
- `game_touch`: simulated touch and gestures for mobile UI checks.

Launch: satelliteoflove is enabled by this plugin (`npx -y @satelliteoflove/godot-mcp@4.1.11`, pinned; checked against its README and the npm registry in Oct 2026; install its editor addon with `npx @satelliteoflove/godot-mcp@4.1.11 --install-addon <project>`). tugcantopaloglu is opt-in: its README documents a local build (`node /abs/path/godot-mcp/build/index.js` with `GODOT_PATH` and `GODOT_MCP_ALLOWED_DIRS`), and the npm copy lags the repo; see this plugin's README for the snippet. Exact tool names come from secondary research notes: confirm them with the server's tool list before relying on them.

## Plugging into the five gates

The `build-feature` workflow runs five gates. Where the bridges help:

| Gate | CLI evidence (authoritative) | Bridge role |
|---|---|---|
| Static | `check_all.gd` log | Fast per-file `validate_script` while iterating |
| Unit | `run_tests.gd` JUnit XML | None; do not replace tests with bridge pokes |
| Playthrough | runner `--mode=script` JSON report | Author and debug the script: step, read state JSON, decide `expect` values |
| Bots / balance | runner `--mode=bot` report | None |
| Visual | screenshot mode, or bridge screenshot | Capture a specific state and judge layout, safe areas, text clipping |

CLI results are the gate evidence. Bridge output is investigative; attach it as notes, never as the pass record.

## Using with the playtest runner

1. Start the project in the editor with the bridge connected.
2. Drive the scenario with input injection, stepping the clock deterministically with a fixed seed.
3. Read state JSON after each step; write down the state paths and values.
4. Turn the sequence into `tests/playthroughs/<name>.json` (`steps[].action` and `expect`), using those state paths.
5. Run `godot --headless --path <project> -s res://tools/playtest/runner.gd -- --mode=script --script=res://tests/playthroughs/<name>.json --out=<abs>/playthrough.json --seed=1`.
6. Commit the script; CI keeps it.

## Security

- **Localhost only.** Bind and connect bridges to 127.0.0.1; never expose the editor port or the MCP server to a network or tunnel.
- **Trusted projects only.** These tools can run scripts and write files; treat an untrusted project as untrusted code.
- **CVE history of Coding-Solo/godot-mcp.** A command-injection issue via the `projectPath` parameter was reported (CVE-2026-25546) and described as fixed in 0.1.1; the repository also showed no pushes for roughly six months at last check. Sources are secondary; verify at https://github.com/Coding-Solo/godot-mcp. The tugcantopaloglu bridge is a fork of it: **check whether it inherits unpatched code paths** before enabling, and never pass unsanitized strings (user-supplied paths) to either bridge.
- Allow-list read tools; require confirmation for writes, exports and anything spawning processes.
- Keep secrets (keystores, API keys) out of the project directory the bridge can read.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `LSP` tool missing, or "GDScript language server unavailable" | No Godot found, no `project.godot` near the session folder, or Node missing | The error names the cause: set `godot_bin` (or `GODOT_BIN`), start Claude Code in the project (or set `GS_GODOT_PROJECT`), install Node 18+; then run the self-test above |
| Language server starts but never answers | Godot without `--lsp-port`, or a slow first import | Check `godot --help`; read `gdscript-lsp/godot-*.log` in the plugin data folder; import once with `godot --headless --path . --import` |
| Windows: Godot not found | The download keeps its versioned name and is not on PATH | Set `godot_bin` (or `GODOT_BIN`) to `Godot_v4.x-stable_win64.exe` or its folder; the `_console.exe` twin is used automatically |
| Language server errors flag `class_name` types as unknown | Class cache missing or stale | Run `godot --headless --path . --import`, then edit the file again |
| Server fails to start | Node/npx missing, addon not installed, or editor not running | Install Node 18+, run the `--install-addon` step, open the project in the editor; for tugcantopaloglu check the local build path |
| Tools listed but calls time out | Editor not running or addon disabled | Open the project, enable the addon, restart the server |
| "Godot not found" | `godot_bin` unset or wrong version | Set the plugin config to the pinned 4.x binary |
| Two agents fight | One client per editor limit | Detach one |
| Stepping gives different results | Missing fixed seed or real-time waits | Seed the run, step the frozen clock |
| Headless validate passes, editor errors | Import cache stale | Run `godot --headless --path <p> --import`, retry |
| Touch has no effect | Input not routed to the UI node | Check mouse filter and that the scene is the active one |

## Volatile facts (as of Oct 2026 — verify)

- satelliteoflove/godot-mcp: reported 21 tools / 86 actions, last push 2026-10-02. https://github.com/satelliteoflove/godot-mcp
- tugcantopaloglu/godot-mcp: reported 157 tools, last push 2026-10-09. https://github.com/tugcantopaloglu/godot-mcp
- Coding-Solo/godot-mcp: last push reported 2026-04-16; CVE-2026-25546 reported fixed in 0.1.1 (secondary source). https://www.summerengine.com/blog/best-godot-mcp-server
- Godot 4.7.2 stable current. https://github.com/godotengine/godot/releases

## Related skills

- `engine-godot`: Godot 4 patterns, export, typed GDScript.
- `qa-testing`: gate design, deterministic playthroughs, bots.
- `build-feature`: the five-gate workflow these bridges support.
- `playtest`: runner modes and persona playtests.
