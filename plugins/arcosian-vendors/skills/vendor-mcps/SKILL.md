---
name: vendor-mcps
description: Decides when to call a vendor MCP (PixelLab, Meshy, ElevenLabs, Scenario, ComfyUI) directly versus the core studio-gateway, covers each vendor's strengths, licences and plan requirements, and requires manifest_update registration so provenance and budgets stay intact. Use when asked to "generate pixel art with PixelLab", "use the Meshy MCP", "make SFX with ElevenLabs", "connect Scenario or ComfyUI", "which asset vendor should I use" or "why is this asset missing provenance".
---

# Vendor MCPs

## When to use

The core `studio-gateway` is the default path for generation: it applies the style lock, enforces the per-project budget, records provenance and runs post-processing. Reach for a vendor MCP only when the vendor offers a capability the gateway does not wrap (for example directional pixel-art characters or interactive 3D rigging), or when exploring.

## The one rule

Provenance and budgets are enforced only by the gateway. A vendor MCP call does not check the budget, does not write a manifest entry and does not apply the style lock. Therefore every vendor output must be registered with `manifest_update` before it counts as a project asset.

Minimum manifest record: asset id, file path, vendor, model or endpoint, prompt or input references, seed if any, plan tier or licence, cost estimate, date, reviewer status. Missing fields are recorded as unknown, never guessed.

## Decide: gateway or vendor MCP

| Situation | Choice |
|---|---|
| Hero art, icons, UI, store art, standard SFX or music | Gateway |
| Batch of 20+ assets with a style lock | Gateway, `asset-batch` workflow |
| 4 or 8 direction pixel characters, pixel animation, tilesets | PixelLab MCP, then register |
| Rigging and animation of a humanoid in one vendor | Meshy MCP, then register |
| Voice design, dialogue, tuned SFX through an authorized hosted session | ElevenLabs MCP, then register |
| Custom-trained style model, many hosted models in one account | Scenario (registered by this plugin), then register outputs |
| Exact repeatable graphs, ControlNet or LoRA stacking, deterministic seeds | ComfyUI (opt-in, see README), then register outputs |
| You do not know the cost | Gateway estimate first, or ask the human |

## Vendor notes

**PixelLab.** Strongest tool in the notes for pixel art: characters with 4 or 8 directions, animation, tilesets. Remote MCP, Bearer token, subscription required. Commercial use allowed; do not use outputs to train new models. Disclose AI use on stores that ask.

**Meshy.** One API for text and image to 3D, remesh, UV, rigging, animation and text-to-motion. Rigging is humanoid-only. MCP key requires Pro or above. Free tier output is CC BY 4.0, so production work must run on a paid plan. A `lowpoly` model type was reported retiring on 2026-10-30; check the current topology options. Credits are prepaid; compute a per-asset estimate (generation plus remesh plus rig plus animations) before starting and multiply by variants.

**ElevenLabs hosted MCP.** OAuth, no local install, replaces the archived local server. Which tools the hosted endpoint exposes (music, dialogue) was not confirmed; list tools with `/mcp` before planning. Voice and likeness rights: only use voices you created or have licensed; log the voice id.

**Scenario.** Agent-ready platform for custom-trained styles and a hub of third-party models, with an official MCP. Registered as the remote server `https://mcp.scenario.com/mcp` (confirmed in Scenario's help centre, Oct 2026); authorize through `/mcp`. API keys need write permission if used instead of OAuth.

**ComfyUI.** Official MCP for cloud and for local servers. Best when graphs must be repeatable. Comfy Cloud MCP (beta) is `https://cloud.comfy.org/mcp`; the local server runs on `comfy-cli` 1.x (setup in this plugin's README); local servers load arbitrary custom nodes, which is a supply-chain risk.

## Procedure for a direct vendor call

1. Confirm the server is connected (`/mcp`) and authorized.
2. Read the style bible and any existing manifest entries for the asset family.
3. Estimate cost, compare with the remaining project budget (`.gamestudio/config.json` overrides the default), and ask the human if the call is above the usual size.
4. Generate one sample, not a batch. Show it to the art-director agent.
5. Download outputs into the project; never leave the only copy at the vendor.
6. Run the studio post-processing scripts (`image_post.py`, `audio_post.py`) as relevant.
7. Register with `manifest_update`. Then run the critic.

## Cost sketch (formula, no prices)

Per-asset cost = sum over steps of (credits per step x retries x variants). Plan for retries at 2 or 3 for generative steps. Compare against the budget remaining, and stop at 80 percent to ask.

## Worked example: a pixel-art enemy set

1. Gateway cannot produce 8-direction sprites, so PixelLab is justified; note the reason in the task log.
2. Check budget: 3 enemies x 8 directions x 4 animations. Ask PixelLab for one enemy first and estimate the rest from that.
3. Art-director reviews the sample against the palette in the style bible; adjust prompt, not palette.
4. Generate the remaining enemies, download, run `image_post.py` for palette and padding checks.
5. `manifest_update` for each sprite sheet with vendor, plan tier and cost; critic reviews the in-game screenshot.

## Failure modes

- Output exists but no manifest entry: the pre-flight fails; register it, do not delete the file.
- Auth errors on a remote server: re-authorize via `/mcp` (OAuth) or reset the userConfig key (Bearer).
- Free-tier outputs slipped into production: re-generate on a paid plan or add the required attribution; record the decision.

## Security and privacy

- Keys are stored through plugin userConfig as sensitive values; never paste them in chat or commit them.
- Prompts and reference images go to the vendor; do not send unreleased proprietary art or personal data.
- OAuth authorization is done by the human in the browser; do not try to automate it.

## Volatile facts (as of Oct 2026 - verify)

- PixelLab remote MCP and Bearer auth. Source: https://mcpservers.org/servers/pixellab-code/pixellab-mcp
- Meshy pricing, plan requirement and low-poly retirement. Source: https://docs.meshy.ai/en/api/pricing
- ElevenLabs hosted MCP. Source: https://github.com/elevenlabs/elevenlabs-mcp
- Scenario MCP tool count and auth. Source: https://help.scenario.com/en/articles/getting-started-with-the-scenario-mcp-server
- ComfyUI official MCP. Source: https://comfyui-wiki.com/en/news/2026-06-30-comfy-mcp-agent-integration
