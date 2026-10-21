# arcosian-vendors

Adapter plugin for the `arcosian` core plugin. It registers vendor-hosted MCP servers for asset and audio generation, and ships a skill explaining how to use them without losing the provenance and budget guarantees of the core `studio-gateway`.

Requires the core plugin `arcosian` (declared as a dependency).

## What you get

- Skill `vendor-mcps`: vendor MCP versus gateway decision table, per-vendor strengths, licences and plan requirements, and the rule to register every vendor output with `manifest_update`.
- `.mcp.json` with four servers:

| Server | Transport | Auth | Status |
|---|---|---|---|
| `pixellab` | remote http, `https://api.pixellab.ai/mcp` | Bearer token (`pixellab_api_key`) | Documented in the research notes; subscription required |
| `meshy` | stdio, `npx -y @meshy-ai/meshy-mcp-server@0.6.4` (pinned) | `MESHY_API_KEY` (`meshy_api_key`) | Documented; key needs Pro plan or above |
| `elevenlabs` | remote http, `https://api.elevenlabs.io/v1/mcp` | OAuth in the browser, no key stored | Documented; hosted tool list not confirmed |
| `scenario` | remote http, `https://mcp.scenario.com/mcp` | Authorize through `/mcp` | Official; URL and the `claude mcp add --transport http scenario https://mcp.scenario.com/mcp` setup confirmed in Scenario's help centre (Oct 2026): https://help.scenario.com/articles/2664328768-getting-started-with-the-scenario-mcp-server |

Remote OAuth servers do not break the session when unconfigured: they simply wait for authorization via `/mcp`.

## Opt-in servers (not registered by default)

- **ComfyUI** official MCP. Comfy Cloud MCP (beta, June 2026) is a remote server at `https://cloud.comfy.org/mcp`; add it to a project `.mcp.json` as `{"type": "http", "url": "https://cloud.comfy.org/mcp"}` if your account has beta access (source: https://comfyui-wiki.com/en/news/2026-06-30-comfy-mcp-agent-integration, linking https://docs.comfy.org/agent-tools/partner-mcp). The local server (August 2026) is built on `comfy-cli` 1.x; follow https://docs.comfy.org/agent-tools for its launch command. Local servers load arbitrary custom nodes, which is a supply-chain risk: install only nodes you have reviewed.
- The archived local ElevenLabs server (`elevenlabs-mcp` via uvx) is deprecated; do not use it.

## What this plugin runs, sends and fetches

- **Sends:** your prompts, reference files and generation settings to PixelLab, Meshy, ElevenLabs and Scenario when Claude uses their tools, under your own accounts (keys you enter, or sign-in through `/mcp`).
- **Runs:** the Meshy MCP server locally; the other three are remote servers run by those vendors.
- **Fetches:** `@meshy-ai/meshy-mcp-server@0.6.4` from npm on first start (exact version), and the files the vendors generate.
- **Costs:** these calls bill your vendor accounts and sit outside the core gateway's budget cap; record every output with `manifest_update`.

## Important: provenance and budgets

Vendor MCP calls bypass the gateway. Only `studio-gateway` enforces the per-project spending cap, style lock and provenance records. If you use a vendor MCP directly:

1. State the intended spend first and check the remaining budget.
2. Save outputs under the project's asset folders.
3. Call `manifest_update` immediately with vendor, model, prompt, licence tier and cost.

Assets without a manifest entry fail the compliance pre-flight.

## Plan and licence reminders

- Meshy free tier outputs are CC BY 4.0; paid plans give private ownership. Run the pipeline on a paid plan.
- PixelLab allows commercial use; outputs may not be used to train new models.
- Check ElevenLabs and Scenario terms for your plan before shipping voices or generated art.

## Volatile facts (as of Oct 2026 - verify)

- PixelLab endpoint and auth. Source: https://mcpservers.org/servers/pixellab-code/pixellab-mcp
- Meshy MCP install and Pro requirement. Source: https://docs.meshy.ai/en/api/ai
- ElevenLabs hosted MCP replaces the archived local server. Source: https://github.com/elevenlabs/elevenlabs-mcp
- Scenario MCP. Source: https://help.scenario.com/en/articles/getting-started-with-the-scenario-mcp-server
- ComfyUI MCP. Source: https://comfyui-wiki.com/en/news/2026-08-11-comfy-mcp-local-server

## License

MIT.
