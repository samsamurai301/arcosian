# Arcosian roadmap

From "a studio for mobile games" to **any game, any platform, any tool**. The user decides the genre, the platforms and the engine. Arcosian brings the knowledge, the tools, the connectors, and an understanding layer: what the project is, what a change touches, and what a change will do.

**Status (2026-10-21):** all five batches shipped in 0.4.0. What was verified and what was not is in the [changelog](../plugins/arcosian/docs/CHANGELOG.md).

## Principles

- **The user decides.** Genre, platforms (mobile, desktop, web, console) and engine are choices in the design contract; no skill assumes mobile.
- **Connectors are checked before they ship.** Each one is verified against the tool's official documentation, pinned to an exact version, and disclosed in its README. Anything that needs an account is opt-in.
- **Context stays lean.** Today the core plugin adds about 8,200 tokens to every session. A CI check keeps that budget as skills are added, by keeping descriptions short and detail in reference files.
- **Every batch ships tested.** Tests run on macOS, Linux and Windows; versions go up; the changelog says what was verified and what was not.
- **Humans approve releases.** Uploads to Steam, itch.io, consoles and the mobile stores always ask first.

## Batches

| # | Batch | What it delivers | Status |
|---|---|---|---|
| 1 | Any game, any platform | Desktop, web and console as first-class targets; new genre playbooks; desktop and web builds in both templates | Shipped in 0.4.0 |
| 2 | Understanding layer | Project map for Claude, change impact, what-if predictions, visual dashboard | Shipped in 0.4.0 |
| 3 | Art, animation, UI and level tools | Aseprite, Krita, Spine, Figma, Tiled, LDtk | Shipped in 0.4.0 (`arcosian-art`, `arcosian-levels`) |
| 4 | Audio, team, community and stores | FMOD, Wwise, GitHub, Discord, Steam, itch.io, Sentry | Shipped in 0.4.0 (`arcosian-audio`, `arcosian-community`) |
| 5 | Community kit and polish | Add-on guide and template, code of conduct, connector catalog, token-budget check | Shipped in 0.4.0 |

### 1. Any game, any platform

- **Design flow**: `new-game` and `gs.py init` ask for platforms, input methods and orientation; the principal and every agent read them from the contract.
- **Knowledge**:
  - `platform-targets`: input (touch, mouse and keyboard, gamepad), UX per platform (settings menus, resolutions, accessibility), performance tiers (phones, PC minimum specs, Steam Deck, browsers), save locations, platform rules.
  - `pc-web-release`: Steam (store page, SteamPipe uploads, Steam Deck compatibility, achievements, cloud saves), itch.io (butler), web portals, macOS notarization, Windows code signing, Linux packaging.
  - `console-pathway`: developer programs, dev kits, certification and age ratings. Guidance only: console SDKs are under NDA.
  - New genre playbooks: shooter, platformer and metroidvania, survival and sandbox, simulation and management, action-adventure, racing and sports, fighting, horror, visual novel, deckbuilder, tactics, MMO and live service. Case studies for PC and console games.
  - Existing mobile skills gain desktop and web sections where the advice differs.
- **Templates**: Windows, macOS, Linux and web exports in the Godot template and the matching Unity build targets; keyboard and gamepad input next to touch; layouts that work in landscape and portrait.
- **CI and guards**: desktop and web export jobs in the CI templates; Steam (`steamcmd`), itch.io (`butler`) and console submission commands join the ask-first list.
- **Verified by**: real exports on macOS, desktop builds launched in CI on all three systems, the web build opened in a browser.

### 2. Understanding layer

- **Project map for Claude**: `gs.py map` indexes scenes, nodes, scripts, classes, signals, autoloads, assets and design documents (Godot and Unity in depth, plain files for other engines) into a compact map that agents read before opening files. It refreshes after edits.
- **Change impact**: `gs.py impact <file | class | tuning key>` lists the scenes, scripts, features, tests, assets and gates a change touches. `build-feature` uses it to choose which gates to run again.
- **What-if predictions**: `/arcosian:what-if` runs the bots and simulators (balance, economy, progression, difficulty, performance budget) on the current version and on the proposed change across many seeds, then reports the predicted difference with ranges and a verdict against the contract's targets.
- **Visual dashboard**: `gs.py dashboard` writes one self-contained page with features and their five gates, core-loop and economy diagrams, the dependency graph, budget, an asset gallery with licences, playtest and performance trends, and what-if results. It works offline with no external scripts.
- **Verified by**: runs on both templates and a seeded sample project; the dashboard checked in a browser.

### 3. Art, animation, UI and level tools

- **`arcosian-art`**: Aseprite, Krita and Spine (alternatives such as DragonBones and Rive researched), sprite sheets and atlases, importing into Godot and Unity; Figma for UI design through its official MCP server.
- **`arcosian-levels`**: Tiled and LDtk formats, engine importers, and level checks (solvability, pacing) built on the existing `level_audit`.
- Each tool is checked against its official documentation. MCP servers are added only where an official or vetted one exists; otherwise the skill gives command-line recipes.

### 4. Audio, team, community and stores

- **`arcosian-audio`**: FMOD Studio and Wwise: event design, banks, engine integration, build automation.
- **`arcosian-community`**: GitHub (official MCP server), Discord for player communities and devlogs, Steam and itch.io pages and builds behind the ask-first guard, Sentry crash triage.
- Further 3D tools (Substance, Houdini) researched and added if they meet the same bar.

### 5. Community kit and polish

- `docs/EXTENDING.md`: how to build an add-on (genre pack, engine adapter, tool connector), with layout, skill style, ontology use, security rules, tests, versioning and how to submit it.
- An add-on template and `/arcosian:extend` to scaffold one; a code of conduct (Contributor Covenant); issue and pull-request templates; a community connector catalog with trust levels, checked in CI.
- A CI check on the always-on token budget; a release.

## Next

- Compile and run the Unity template's desktop and web build methods in the Unity Editor (verified so far: the engine-free core on .NET).
- Bots and a what-if path for Unity projects, matching the Godot runner's `--tuning` overrides.
- More genre packs and engine adapters from the community through `/arcosian:extend`.
- Re-check the volatile facts in the new skills each quarter; several vendor pages refused automated fetches in October 2026.

## Not planned for now

- Console SDK integration (NDA); consoles get knowledge and guidance only.
- Automatic store publishing; every upload stays human-approved.
- Unvetted community MCP servers as defaults; they stay documented and opt-in.
- Unreal and other engines as first-class targets; they keep their knowledge skill, and adapters can follow if wanted.
