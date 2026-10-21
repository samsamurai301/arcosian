# Contributing to Arcosian

Thanks for helping. Arcosian is MIT-licensed, and contributions are accepted under the same licence.

## Layout

| Path | What it holds |
|---|---|
| `plugins/arcosian/` | Core plugin: skills, agents, workflows, Python tools and schemas, hooks, the `studio-gateway` MCP server, templates, docs |
| `plugins/arcosian-*/` | Adapters: engines (Godot, Unity, Blender), asset and audio vendors, commerce services |
| `evals/arcosian/` | Cases for `claude plugin eval` |
| `docs/BLUEPRINT.md` | The design contract every component follows |
| `docs/research/` | The research the design is based on |

## Conventions

- **Python**: standard library only, compatible with Python 3.9.
- **Node**: no npm dependencies (gateway, language-server bridges, hook launcher).
- **Paths**: reference plugin files as `${CLAUDE_PLUGIN_ROOT}/...`; hooks use exec form (`node` plus `run-python.mjs`), so they need no shell on any system.
- **Packages**: pin anything an MCP server runs through `npx` or `uvx` to an exact version.
- **Facts that change** (prices, versions, policies): put them in the skill's "Volatile facts" section with a source and date.
- **Secrets**: never in files, examples included; ask for them through a sensitive `userConfig` option.
- **Writing**: plain, specific English; procedures, decision tables and worked examples over general advice.

## Checks before a pull request

```bash
python3 plugins/arcosian/hooks/tests/test_hooks.py
node plugins/arcosian/mcp/studio-gateway/test/run-tests.mjs
python3 plugins/arcosian/scripts/audit_plugin.py --root plugins/arcosian --max-description-chars 34000
for d in plugins/arcosian-*/; do python3 plugins/arcosian/scripts/addon.py check "$d"; done
python3 tools/check_connectors.py
for f in plugins/*/scripts/*.py plugins/*/skills/*/scripts/*.py tools/*.py; do python3 "$f" --selftest >/dev/null || echo "FAIL $f"; done
claude plugin validate --strict plugins/arcosian
```

On Windows, clone with `git -c core.autocrlf=input clone ...` so the eval scaffolds (shell scripts) keep LF line endings. The repository has no `.gitattributes`: Anthropic's plugin directory refuses repositories whose attributes rewrite file contents.

With Godot 4 and csharp-ls installed, also run the language-server self-tests from a copy of each template (commands in the adapters' READMEs). CI runs all of this on macOS, Linux and Windows for every pull request.

New add-ons, genre packs and connectors: see [docs/EXTENDING.md](docs/EXTENDING.md). A new MCP server also needs an entry in `docs/connectors.json` (then `python3 tools/check_connectors.py --write`). Everyone taking part follows the [code of conduct](CODE_OF_CONDUCT.md).

## Releases

- Raise `version` in the `plugin.json` of every plugin you changed: users only receive an update when it changes.
- Add an entry to `plugins/arcosian/docs/CHANGELOG.md` that says what changed, what was verified and what was not.
- Never rename a published plugin; change `displayName` instead.
