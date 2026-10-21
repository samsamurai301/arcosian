# Connector catalog

Every MCP server that an Arcosian plugin registers, with where it comes from and how much to trust it. Generated from `docs/connectors.json` by `tools/check_connectors.py --write`; CI fails when the two differ or when a plugin registers a server that is not listed here.

Trust levels:

- **first-party**: Written and tested in this repository.
- **official**: Published by the tool's own vendor; URL or package taken from the vendor's documentation.
- **community**: Third-party bridge, pinned to an exact version, documented and opt-in. Check its maintenance before depending on it.

Servers that need an account do nothing until you sign in or add a key; nothing is sent before that.

| Plugin | Server | Transport | Source | Vendor | Trust | Auth | Checked |
|---|---|---|---|---|---|---|---|
| `arcosian` | `studio-gateway` | stdio | `node ${CLAUDE_PLUGIN_ROOT}/mcp/studio-gateway/server.mjs` | Arcosian | first-party | optional API keys in plugin options; mock assets without keys | 2026-10-21 |
| `arcosian-art` | `figma` | http | `https://mcp.figma.com/mcp` | Figma | official | OAuth through /mcp | 2026-10-21 |
| `arcosian-blender` | `blender` | stdio | `uvx blender-mcp==2.0.0` | ahujasid/blender-mcp (MIT) | community | none; talks to a local Blender add-on | 2026-10-21 |
| `arcosian-commerce` | `adjust` | http | `https://mcp.adjust.com/mcpo` | Adjust | official | sign in through /mcp | 2026-10-21 |
| `arcosian-commerce` | `firebase` | stdio | `npx -y firebase-tools@15.34.0 mcp` | Google (Firebase CLI) | official | Firebase CLI login or Application Default Credentials | 2026-10-21 |
| `arcosian-commerce` | `revenuecat` | http | `https://mcp.revenuecat.ai/mcp` | RevenueCat | official | OAuth through /mcp | 2026-10-21 |
| `arcosian-community` | `github` | http | `https://api.githubcopilot.com/mcp/readonly` | GitHub | official | personal access token in the sensitive github_token option; read-only endpoint | 2026-10-21 |
| `arcosian-community` | `sentry` | http | `https://mcp.sentry.dev/mcp` | Sentry | official | OAuth through /mcp | 2026-10-21 |
| `arcosian-godot` | `godot-satelliteoflove` | stdio | `npx -y @satelliteoflove/godot-mcp@4.1.11` | satelliteoflove/godot-mcp | community | none; talks to a local Godot editor add-on | 2026-10-21 |
| `arcosian-unity` | `unity-cli` | stdio | `unity mcp` | Unity (official Unity CLI, installed separately) | official | Unity account sign-in in the CLI | 2026-10-21 |
| `arcosian-vendors` | `elevenlabs` | http | `https://api.elevenlabs.io/v1/mcp` | ElevenLabs | official | OAuth through /mcp | 2026-10-21 |
| `arcosian-vendors` | `meshy` | stdio | `npx -y @meshy-ai/meshy-mcp-server@0.6.4` | Meshy | official | API key in the sensitive meshy_api_key option | 2026-10-21 |
| `arcosian-vendors` | `pixellab` | http | `https://api.pixellab.ai/mcp` | PixelLab | official | bearer token in the sensitive pixellab_api_key option | 2026-10-21 |
| `arcosian-vendors` | `scenario` | http | `https://mcp.scenario.com/mcp` | Scenario | official | OAuth through /mcp | 2026-10-21 |

## Documented, not registered

These appear in the skills as options but are not started by any plugin.

| Plugin | Server | Source | Why not registered |
|---|---|---|---|
| `arcosian-community` | sentry (stdio) | npx -y @sentry/mcp-server@0.42.0 | Sentry calls the stdio server a work in progress; the hosted server is registered instead. |
| `arcosian-godot` | tugcantopaloglu/godot-mcp | see the godot-bridge skill | An alternative bridge; documented, not registered. |
| `arcosian-unity` | CoplayDev/unity-mcp | see the unity-bridge skill | Community Unity bridge; documented, not registered. |

## Proposing a connector

Open a connector proposal issue with the vendor's documentation link, the exact package version or URL, what it can read and write, and how it authenticates. See [EXTENDING.md](EXTENDING.md).
