# Arcosian

[![ci](https://github.com/samsamurai301/arcosian/actions/workflows/ci.yml/badge.svg)](https://github.com/samsamurai301/arcosian/actions/workflows/ci.yml) [![licence: MIT](https://img.shields.io/badge/licence-MIT-blue.svg)](LICENSE)

A Claude Code plugin suite that gives Claude the working habits of a principal game developer and a full studio behind them: a deep game-dev codex, a shared ontology with JSON schemas, 24 specialist agents, nine multi-agent workflows, simulators and solvers, an asset and audio gateway with budgets and provenance, Godot and Unity mobile templates, language servers for GDScript and C#, and hooks that enforce a five-gate definition of done.

It is not an engine wrapper. The value is in five layers, and each one is built to stand on its own.

## Why it is different

| Typical "AI game dev" setup | Arcosian |
|---|---|
| Prompts and a few snippets | A codex of 38 skills with about 160 reference files, written as procedures, formulas, decision tables and worked examples |
| "Looks done" | Done means five gates (static, unit, playthrough, visual, perf) with evidence on disk, checked by hooks that block the stop |
| One generalist | A principal agent plus 23 specialists, each with a model tier matched to the work |
| Free-form assets | Style lock, per-project budget, provenance and licence records for every generated asset |
| Vague ideas | Concept tournaments, adversarial critics, a one-page design contract with kill criteria |
| Lock-in | Native Godot or Unity projects you own; no runtime dependency on the plugin |
| Auto-ship | Store submission is never automatic; a human approves style, fun and submission |

## Install

In a terminal, with [Claude Code](https://code.claude.com/docs/en/setup) installed:

```bash
claude plugin marketplace add samsamurai301/arcosian
claude plugin install arcosian@arcosian
```

Or inside a Claude Code session: `/plugin marketplace add samsamurai301/arcosian`, then `/plugin install arcosian@arcosian`.

Add the adapters your project uses:

```bash
claude plugin install arcosian-godot@arcosian      # GDScript language server, Godot MCP bridges
claude plugin install arcosian-unity@arcosian      # Unity-aware C# language server, Unity CLI bridge
claude plugin install arcosian-blender@arcosian    # Blender MCP
claude plugin install arcosian-vendors@arcosian    # PixelLab, Meshy, ElevenLabs, Scenario
claude plugin install arcosian-commerce@arcosian   # RevenueCat, Firebase, Adjust
```

Get new versions with `claude plugin update arcosian@arcosian`, or turn on auto-update for the marketplace in `/plugin`.

Requirements: Node 18+ and Python 3 (scripts use the standard library only). Works on macOS, Linux and Windows; Windows setup (Git for Windows, the `py` launcher, Godot's `_console.exe` build) is in [SETUP.md](plugins/arcosian/docs/SETUP.md). Every API key is optional: without keys the gateway writes placeholder assets at zero cost. Accounts, keys and where each one goes are listed in the same file.

## Quick start

1. `/arcosian:studio` boots the principal persona, detects project state (greenfield, existing engine project, mid-build) and tells you the next step.
2. Have an idea: `/arcosian:new-game a cozy merge game for commuters`. It runs market scan, concept tournament, design contract, feature plan and `gs.py init`.
3. Build: `/arcosian:build-feature F001`. A feature is done only when all five gates hold.
4. Ship: `/arcosian:ship` prepares signed builds and internal-track uploads. You approve store submission yourself.

Full walkthroughs with exact commands: [PLAYBOOKS.md](plugins/arcosian/docs/PLAYBOOKS.md).

## What is in the box

| Plugin | Contents |
|---|---|
| `arcosian` (core) | 53 skills (15 process, 38 codex), 24 agents, 9 workflows, 19 Python scripts, 14 JSON schemas, `studio-gateway` MCP server, 6 hook handlers, Godot and Unity mobile templates, CI templates |
| `arcosian-godot` | GDScript language server (Godot's own, through a stdio bridge), skill `godot-bridge` and two community Godot MCP bridges |
| `arcosian-unity` | Unity-aware C# language server (csharp-ls), skill `unity-bridge` and a Unity CLI bridge |
| `arcosian-blender` | Skill `blender-bridge` and a Blender MCP |
| `arcosian-vendors` | Skill `vendor-mcps` and PixelLab, Meshy, ElevenLabs and Scenario servers |
| `arcosian-commerce` | Skill `commerce-mcps` and RevenueCat, Firebase and Adjust servers (store tooling is covered in the skill) |

Counts come from `scripts/audit_plugin.py --root plugins/arcosian`; rerun it if you extend the suite. Eight eval cases live in `evals/arcosian/`, outside the plugin, so installs stay small.

## What it runs, sends and fetches

- **Runs on your machine:** the hooks (Python, started by a small Node launcher), the Python tools when Claude calls them, the `studio-gateway` MCP server (Node), and with the adapters a headless Godot editor or csharp-ls for code checks plus the MCP servers you enable.
- **Sends:** generation requests only to the providers whose API keys you add (Google, OpenAI, Recraft, fal, Tripo, Meshy, ElevenLabs, Stability AI), within your budget cap; without keys nothing is sent. Adapter MCP servers talk to their own vendors once you enable them.
- **Fetches:** the exact-version npm and PyPI packages that adapter MCP servers run, and NuGet packages for the C# language server's generated project.
- **Never:** no telemetry, nothing sent to the authors, no automatic store submission; the hooks block reading signing keys and `.env` files.

Details per destination: [PRIVACY.md](PRIVACY.md).

## The five layers

1. **Codex**: design theory, mechanics, genres, deconstructions, psychology, analytics, economy, art, audio, tech, live-ops, release, legal and ethics.
2. **Ontology**: verbs, mechanics, dynamics, aesthetics; loops as graphs; resources and flows; schemas for every project state file.
3. **Studio**: specialist agents and workflows from concept tournament to release candidate.
4. **Tools**: `gs.py` project-state CLI, simulators, solvers, generators, compliance pre-flight, store metadata, gateway, templates, language servers.
5. **Enforcement**: hooks and evals that make the definition of done machine-checkable.

## Doctrine

In priority order:

1. Player first: every decision is justified by the experience it creates.
2. Find the fun fast: prototype the core loop in hours; core loop before content, content before polish.
3. Verify by playing: deterministic playthrough, perf budget and visual critique before "done".
4. Data-informed, not data-driven: hypothesis first, telemetry to confirm.
5. Scope ruthlessly: one-page contract, must/should/won't, kill criteria.
6. Mobile-native: thumb reach, 1 to 5 minute sessions, interruptions, low-end devices, battery and heat.
7. Readability over detail; juice what the player touches.
8. Ethical monetization: no dark patterns, transparent odds, respect for minors.
9. Own the output: native builds you own, no runtime lock-in, licences checked.
10. Automatic between taste checkpoints: humans sign off on style, fun and store submission.

## Repository layout

```
.claude-plugin/marketplace.json   catalog of the six plugins
plugins/arcosian/                 core plugin (README, docs/, skills/, agents/, ...)
plugins/arcosian-*/               five optional adapters
evals/arcosian/                   eval cases for claude plugin eval
docs/BLUEPRINT.md                 binding design spec
docs/research/                    the October 2026 research behind the design
.github/workflows/ci.yml          checks on macOS, Linux and Windows
```

## Documentation

- [Core plugin overview](plugins/arcosian/README.md): skills, agents, workflows, tools
- [ARCHITECTURE.md](plugins/arcosian/docs/ARCHITECTURE.md): layers, state, gates, hooks, gateway, security
- [SETUP.md](plugins/arcosian/docs/SETUP.md): accounts, keys, Windows, first-run checklist, troubleshooting
- [PLAYBOOKS.md](plugins/arcosian/docs/PLAYBOOKS.md): four end-to-end procedures
- [KNOWLEDGE-MAP.md](plugins/arcosian/docs/KNOWLEDGE-MAP.md): generated map of every skill and reference
- [CHANGELOG.md](plugins/arcosian/docs/CHANGELOG.md): what changed, what is verified and what is not

## Status and limits

The core plugin is at 0.3.1 and the adapters at 0.3.0 (the first public release was 0.3.0). What has and has not been verified is listed in the CHANGELOG; CI runs the checks on macOS, Linux and Windows. The adapters wrap community MCP servers whose maintenance you should verify before depending on them. Generated art and audio carry licence terms from the vendor; the gateway records provenance but you remain responsible for checking terms before shipping.

## Contributing and security

Contributions are welcome: see [CONTRIBUTING.md](CONTRIBUTING.md). Report security problems privately as described in [SECURITY.md](SECURITY.md).

Arcosian is an independent project. It is not affiliated with or endorsed by Anthropic, the Godot Foundation, Unity Technologies, Apple, Google or any vendor named here; product names belong to their owners.

Licence: [MIT](LICENSE).
