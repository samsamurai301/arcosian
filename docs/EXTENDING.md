# Extending Arcosian

Arcosian grows through add-ons: separate Claude Code plugins that depend on the core `arcosian` plugin. This guide covers the three kinds, the layout, the rules every add-on follows, how to test it, and how to share it. Inside Claude Code, `/arcosian:extend` walks through the same steps and runs the tools for you.

## Contents

1. Kinds of add-on
2. Scaffold one
3. Layout
4. Writing skills
5. Connectors (MCP servers)
6. Scripts
7. Security rules
8. Checks and tests
9. Versioning and sharing
10. Proposing changes to the core

## 1. Kinds of add-on

| Kind | Holds | Example |
|---|---|---|
| Genre pack | One codex skill and its references: loops, mechanics, numbers, case studies, platform notes | Rhythm roguelites, sports management |
| Engine adapter | A process skill, scripts, optionally a language server or MCP bridge, mapped to the five gates | RPG Maker, Defold, Bevy |
| Tool connector | A process skill, an MCP server or command-line recipes, scripts | A tilemap editor, an audio tool, a store or analytics service |

## 2. Scaffold one

```bash
python3 plugins/arcosian/scripts/addon.py new --name arcosian-rpgmaker --kind engine --skill rpgmaker-bridge \
  --description "Drives RPG Maker MZ projects: data files, plugins, playtest and deployment." --author "your-name" --with-script
```

From an installed plugin the script lives at `${CLAUDE_PLUGIN_ROOT}/scripts/addon.py`. It copies `plugins/arcosian/templates/addon/`, fills in the names and never overwrites files.

## 3. Layout

```
arcosian-rpgmaker/
  .claude-plugin/plugin.json   name, version, description, author, license, keywords, dependencies: ["arcosian"]
  README.md                    disclosure README (section 7)
  LICENSE
  icon.png                     optional
  skills/rpgmaker-bridge/
    SKILL.md
    references/*.md            each listed in SKILL.md
  scripts/*.py                 optional, standard library only, each with --selftest
  .mcp.json                    optional, pinned servers only
```

`dependencies: ["arcosian"]` works when the add-on is published in the Arcosian marketplace. In another marketplace, tell users to install Arcosian first in your README, unless the Claude Code version you target documents dependencies across marketplaces.

## 4. Writing skills

The binding format is section 3 of [BLUEPRINT.md](BLUEPRINT.md). In short:

- Frontmatter: `name` equals the folder name; `description` at most 450 characters, saying what the skill gives and then "Use when ..." with phrases users actually type. Descriptions are loaded into every session, so they are the add-on's permanent cost.
- Genre packs (codex skills) use these sections: what this skill gives you, core models, decision procedures, platform specifics, anti-patterns, using the ontology, reference library, volatile facts with sources, related skills.
- Engine and tool add-ons (process skills) use: when to use, setup, procedures, how it maps to the five gates, worked example, failure modes, security.
- SKILL.md stays under 450 lines. Each reference file is 120 to 800 lines and starts with a summary and a contents list.
- Write procedures, formulas, decision tables and worked examples with real numbers. Never invent tool versions, command flags, prices or statistics; mark unverified facts as such.
- Map the genre or tool onto the core ontology (verbs, mechanics, dynamics, loops, resources) so agents can reason across skills.

## 5. Connectors (MCP servers)

- Prefer the vendor's official server. A community server must be maintained, licensed for reuse and pinned to an exact version.
- Pin every launcher: `npx -y pkg@1.2.3`, `uvx pkg==1.2.3`. Remote servers use https URLs from the vendor's documentation.
- Secrets reach a server only through sensitive plugin options (`"sensitive": true` in `userConfig`, referenced as `${user_config.<key>}`) or environment variables. Never in files.
- A server that needs an account must do nothing until the user signs in.
- Every connector in this repository is listed in [CONNECTORS.md](CONNECTORS.md) with a trust level (first-party, official, community). CI fails when a plugin registers a server that is not in `docs/connectors.json`. To add one, open a connector proposal issue.

## 6. Scripts

- Python 3 standard library only; argparse; exit codes 0 ok, 1 check failed, 2 usage error.
- `--selftest` runs offline and exits 0 on Windows, macOS and Linux.
- Start the `__main__` block by switching stdout and stderr to UTF-8 (the template shows the three lines), and pass `encoding="utf-8"` to every file read and write.
- Scripts run only when Claude calls them for a task. Hooks that run on every tool call need a strong reason and a test suite.

## 7. Security rules

- No API keys, tokens, passwords or personal email addresses in any file.
- Uploads to stores (Steam, itch.io, console portals, app stores) and posts to communities always wait for a human's approval in chat. The core hooks ask before `fastlane deliver`, `steamcmd +run_app_build`, `butler push` and similar commands; do not work around them.
- The README must have a "What this plugin runs, sends and fetches" section and a "Security" section that say plainly what runs locally, what leaves the machine and where it goes.
- Never read signing keys, keystores or `.env` files from a skill or script.

## 8. Checks and tests

```bash
python3 plugins/arcosian/scripts/addon.py check path/to/arcosian-rpgmaker --run-selftests
claude plugin validate path/to/arcosian-rpgmaker
```

`addon.py check` runs the skill audit, the README and licence checks, the connector rules, the script rules and the plugin directory's file rules (no `.gitattributes`, portable file names, files under 256 KiB, at most 512 files). Then install the add-on from a local marketplace in a throwaway `CLAUDE_CONFIG_DIR`, run it on a sample project, and write down what you ran.

## 9. Versioning and sharing

- Start at 0.1.0. Raise `version` in `plugin.json` on every release: users only receive an update when it changes.
- Keep a short changelog in the README or a `CHANGELOG.md`: what changed, what was verified, what was not.
- Share through your own marketplace (a repository with `.claude-plugin/marketplace.json`), or propose the add-on for the Arcosian marketplace with a pull request that adds it under `plugins/` and to the catalog.

## 10. Proposing changes to the core

Read [CONTRIBUTING.md](../CONTRIBUTING.md). Pull requests run the same checks as CI: self-tests, hook tests, the gateway tests, the skill audit with the always-on description budget, the connector catalog check, the Godot template gates and exports, and the language-server tests, on macOS, Linux and Windows.
