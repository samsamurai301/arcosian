---
name: extend
description: Scaffolds and checks an Arcosian add-on - a genre pack, an engine adapter or a tool connector - from the bundled template, then holds it to the house rules (skill format, pinned MCP servers, secrets only in sensitive options, disclosure README, self-tested scripts) before it is shared. Use when asked to "make an add-on", "add support for <engine or tool>", "write a genre pack", "publish my own Arcosian plugin" or "check my add-on".
argument-hint: "[genre | engine | tool] [name]"
---

# Extend Arcosian

An add-on is a separate Claude Code plugin that depends on the core `arcosian` plugin. Write it the way the core is written: knowledge as procedures and tables, tools with self-tests, connectors pinned and disclosed, nothing published or uploaded without a human.

## When to use

- A genre the playbooks do not cover yet (a genre pack: one codex skill plus references).
- An engine without a template or bridge (an engine adapter: a process skill, optional language server, scripts).
- A tool the studio should drive: an editor, a DCC app, a middleware, a store or a service (a tool connector: a process skill, optional MCP server, scripts).

Not for: changes to the core itself (open a pull request against the repository instead), or a one-off script inside a game project (keep it in the project).

## Inputs

- Kind (`genre`, `engine` or `tool`), a plugin name (`arcosian-<something>`, lower case and hyphens), a skill name and a one-sentence description of what it gives and when to use it.
- For connectors: the vendor's own documentation link, the exact package version or URL, how it authenticates and what it can read or write.

## Procedure

1. **Check it is not already covered.** `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py kb "<topic>"` searches every skill. Extend an existing add-on when one fits.
2. **Scaffold.**
   ```
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/addon.py new --name arcosian-rpgmaker --kind engine --skill rpgmaker-bridge \
     --description "Drives RPG Maker MZ projects: data files, plugins, playtest and deployment." --author "<you>" [--with-script]
   ```
   It writes `.claude-plugin/plugin.json`, `README.md`, `LICENSE`, `icon.png`, `skills/<skill>/SKILL.md`, a starter reference, and with `--with-script` a standard-library Python helper with `--selftest`. It refuses to overwrite anything.
3. **Write the skill.** Genre packs use the codex sections (what it gives, core models, decision procedures, platform specifics, anti-patterns, ontology mapping, reference library, volatile facts, related skills). Engine and tool add-ons use the process sections (when to use, setup, procedures, mapping to the five gates, worked example, failure modes, security). Rules:
   - `description` at most 450 characters: what it gives, then "Use when ..." with the user's own phrases. Descriptions load into every session; detail goes into `references/`.
   - SKILL.md under 450 lines; each reference file 120 to 800 lines, opening with a summary and contents, and listed in SKILL.md.
   - Plain English, numbers and procedures. Never invent versions, flags or prices: check the vendor's documentation and put changeable facts under "Volatile facts" with sources.
   - Link core skills by name (`balance`, `playtest`) and core agents as `arcosian:<agent>`.
4. **Add the connector, if any.** Only an official server (published by the vendor) or a well-maintained community one, pinned to an exact version (`npx -y pkg@1.2.3`, `uvx pkg==1.2.3`) or an https URL from the vendor's docs. Secrets come from sensitive `userConfig` options referenced as `${user_config.<key>}`, never from files. Servers that need an account stay inert until the user signs in.
5. **Write the README disclosure.** Sections: What you get, Setup, What this plugin runs, sends and fetches, Security, Typical session, Volatile facts, License. Say plainly what you verified and what you did not.
6. **Check.**
   ```
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/addon.py check <dir> --run-selftests
   claude plugin validate <dir>
   ```
   Fix every error. Warnings about unknown listing fields from `claude plugin validate` are expected on older CLI versions.
7. **Test it for real.** Install from a local marketplace in a throwaway config directory, run the skill on a sample project, and record what you ran in the README.
8. **Version and share.** Start at 0.1.0 and raise `version` on every release (users only receive updates when it changes). Publish in your own marketplace, or propose it for the Arcosian marketplace through a pull request. Uploads to stores and posts to communities stay human-approved in every add-on.

## Outputs

- A plugin folder that passes `addon.py check` and `claude plugin validate`.
- A README that discloses what it runs, sends and fetches.
- For connectors, an entry proposed for the connector catalog (`docs/connectors.json` in the repository) with its trust level.

## Quality gates

- No unfilled template text, no secrets, no unpinned launchers, no `.gitattributes`, portable file names.
- Every script has `--selftest` that passes offline on Windows, macOS and Linux.
- Every factual claim about a third-party tool is sourced or marked unverified.

## Failure modes

| Symptom | Fix |
|---|---|
| `arcosian:<x> is not an agent or skill` | Use a real core name, or run the check with `--core` pointing at the core plugin |
| "launcher must pin an exact version" | Pin `pkg@x.y.z` (npm) or `pkg==x.y.z` (PyPI) after confirming the version exists |
| Skill never triggers | Rewrite the description around the user's words ("Use when ...") and keep it under 450 characters |
| Validation passes but the plugin does nothing | The skill folder or `name` does not match; `name` must equal the folder name |
| Directory submission refused | Remove `.gitattributes`, rename files with device names or colons, keep files under 256 KiB |

## Related skills

`studio`, `engine-alternatives`, `genre-playbooks`, `game-ontology`, `legal-ethics`.
