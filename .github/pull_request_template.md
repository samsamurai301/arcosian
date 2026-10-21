## What this changes

<!-- One paragraph: what and why. Link the issue if there is one. -->

## How it was verified

<!-- Commands you ran and their results. Say what you could not verify. -->

## Checklist

- [ ] Self-tests pass: every changed script's `--selftest`, `hooks/tests/test_hooks.py`, gateway tests
- [ ] `python3 plugins/arcosian/scripts/audit_plugin.py --root plugins/arcosian --max-description-chars 34000` passes
- [ ] `python3 plugins/arcosian/scripts/addon.py check plugins/<adapter>` passes for changed adapters
- [ ] `python3 tools/check_connectors.py` passes (new MCP servers are in `docs/connectors.json`)
- [ ] `version` raised in every changed `plugin.json`, and a CHANGELOG entry added
- [ ] No keys, tokens or personal data in any file; uploads and posts stay human-approved
