# Model Landscape 2026 (2D and 3D Generation)

A map of the image, game-art and 3D generation tools relevant to a mobile game pipeline as of October 2026: what each is good at, how it is accessed (API, MCP), licence posture, and which vendors the studio excludes. Almost everything here is volatile: model names, prices and terms change monthly, and several figures in the source notes come from resellers or marketing pages, so each volatile item carries a source and a confidence note. The stable part is the selection logic in the first sections: choose the provider by asset type, consistency need, licence safety and budget, never by leaderboard rank alone. Use `studio-gateway` defaults first; reach for specialist platforms only when the gateway lacks the capability.

## Contents

1. [Selection logic (stable)](#1-selection-logic-stable)
2. [Capability matrix by asset type](#2-capability-matrix-by-asset-type)
3. [General image models](#3-general-image-models)
4. [Game-specialized 2D platforms](#4-game-specialized-2d-platforms)
5. [Orchestration layers](#5-orchestration-layers)
6. [2D animation tools](#6-2d-animation-tools)
7. [3D generators](#7-3d-generators)
8. [Rigging, motion and texturing](#8-rigging-motion-and-texturing)
9. [Post-processing services](#9-post-processing-services)
10. [MCP servers](#10-mcp-servers)
11. [Licences and commercial terms](#11-licences-and-commercial-terms)
12. [Excluded and restricted vendors](#12-excluded-and-restricted-vendors)
13. [Default provider recommendations](#13-default-provider-recommendations)
14. [Volatile facts (as of Oct 2026 - verify)](#14-volatile-facts-as-of-oct-2026---verify)

---

## 1. Selection logic (stable)

Rank providers on six questions, in this order:

1. **Licence safe?** Commercial use allowed on the plan you will actually use; outputs not owned by the vendor; no non-commercial weights in the shipping path. A fail removes the provider.
2. **Automatable?** Official API or MCP, stable model ids, no terms against automated access. Consumer-only tools are not pipeline tools.
3. **Controllable?** Reference images, seeds, transparency, size control, edit mode. Consistency features decide whether hundreds of assets stay on style.
4. **Right output form?** Native transparency, native pixel grid, vector, sprite sheet, low-poly mesh, rig. Native output beats post-processing.
5. **Quality at the readable size?** Judge at the phone size the player sees, by tournament (see `references/style-lock-and-prompts.md`), not by arena rank.
6. **Cost per accepted asset**, not per generated image: `cost_per_accepted = (candidates_per_asset x price_per_candidate) / acceptance_rate + post_cost + human_minutes x rate`.

Worked example: a model at 0.034 per image with 3 candidates and a 40 percent acceptance rate costs about 0.255 per accepted asset before post-processing; a model at 0.21 with a 70 percent acceptance rate and 2 candidates costs 0.6. The expensive model wins only where acceptance rate or text fidelity dominates (hero art, store screenshots, text-heavy UI).

## 2. Capability matrix by asset type

| Asset type | Needs | Typical best fit (verify) | Fallback |
|---|---|---|---|
| Concept and style frames | Quality, variety | A top general model (OpenAI or Google class) | Open-weights model on a hosted aggregator |
| Character sheets and variants | Multi-reference consistency | Multi-reference edit models (Google Nano Banana line, OpenAI edit mode) | Trained style model (LoRA) on Scenario or fal |
| Bulk sprites and items | Consistency, transparency, low cost | Edit/generation with references plus background removal; LoRA at scale | Platform with style training |
| Pixel art | Native pixel grid, palette | PixelLab, Retro Diffusion | General model plus pixelate and palette quantization (weaker) |
| Icons and UI | Clean shapes, vector, text | Recraft (vector), OpenAI for text-heavy | General model plus vectorize |
| Tilesets and textures | Seamless tiling | Specialist tileset tools (PixelLab for pixel; texture generators) | General model plus manual seam repair |
| Backgrounds | Large size, no characters | General model, upscale | Panorama tools |
| Sprite sheets and animation | Frame consistency | Ludo.ai, PixelLab, Retro Diffusion, AutoSprite | Edit-model grids plus heavy post |
| Key art, store screenshots | Fidelity, text | Top general model, human finishing | n/a |
| 3D props | Low-poly, UVs, PBR | Tripo, Meshy, Tencent HY 3D | Self-hosted open weights (check licence) |
| 3D characters | Rig, topology | Meshy or Tripo with rig, then cleanup | Human modeller |
| Rigging and motion | Humanoid skeleton | Generator built-in rigs; Uthana for text-to-motion | Open-weights motion model, manual mocap clips |

## 3. General image models

The notes' leaderboard snapshot (Artificial Analysis text-to-image arena) places OpenAI's GPT Image line at the top by quality and Google's Nano Banana line as the best quality per price, with other vendors (xAI, Microsoft, Meta, Black Forest Labs, ByteDance Seedream, Alibaba Qwen, Ideogram) in the next tier. Rank is a preference arena result for generic prompts; it says little about game-asset consistency.

| Model family | Role in a mobile pipeline | Access | Notes |
|---|---|---|---|
| OpenAI GPT Image (2, 2.5 Flare/Sunburst) | Hero art, text-heavy UI mockups, store screenshots, tight edits | Official API, token billed, batch at half price | Transparent background reportedly opened as a preview; check current docs |
| Google Nano Banana line | Bulk generation and edits; multi-reference consistency (up to 14 references reported) | Official Gemini API; batch discount | Practical reports: reliable for 1-2 main characters per prompt |
| Recraft V4.x | Vector and SVG, icons, UI; custom styles | Official API, prepaid units | Paid plans own outputs; free plan outputs not commercial |
| FLUX family (Black Forest Labs) | Quality open-ish models; editing | Hosted APIs, aggregators | Licence varies by variant: only the small klein 4B is reported Apache 2.0; others non-commercial for self-hosting |
| Qwen-Image / Qwen-Image-Edit | Self-hosted, trainable, permissive | Open weights (Apache 2.0 reported) | Good base for LoRA training |
| Seedream, Grok Imagine, MAI-Image, Muse | Alternatives | Varied; API availability and terms not verified in the notes | Treat as optional until terms are checked |
| Ideogram | Typography-forward images | API; weights status unverified | Verify terms |

The gateway's `image_generate` supports providers `gemini`, `openai`, `recraft`, `fal`, `stability` and `auto`; `image_edit` supports `gemini` and `openai`. Default model ids live in the gateway's `pricing.json` and may lag the newest releases; override with `GS_MODEL_<PROVIDER>_<KIND>`.

## 4. Game-specialized 2D platforms

| Platform | Strength | Access | Licence and terms notes |
|---|---|---|---|
| Scenario | Custom style training (LoRAs), hub of third-party models, background removal, upscaling, vectorization, video and 3D | REST API, official MCP (about 17-19 tools), OAuth or API key | Output ownership and indemnity terms not retrieved; pricing is credit based and per-call costs not published |
| PixelLab | Pixel art: characters with 4/8 directions, walk/run/idle/attack animation, tilesets (Wang, dual grid), UI elements, style references | Web, Aseprite extension, SDKs, REST v2, official remote MCP (subscription, bearer token) | Commercial use allowed; outputs may not train new models; disclosure needed on Steam |
| Retro Diffusion | Pixel art by pay-per-generation; animations, tilesets, free cost estimate | API, official MCP | Pay per image, prepaid credits; verify terms |
| Ludo.ai | Static character to sprite sheet via motion presets; icons, UI, textures, backgrounds, audio | REST API and MCP on select plans | Terms not retrieved |
| Leonardo | Custom model training (Elements), transparency, upscale | REST API with SDKs | Commercial rights on paid plans only |
| Layer.ai | Custom models, engine exports | API and webhooks reported; only a community MCP | Verify; unmaintained wrappers are a risk |
| AutoSprite, God Mode AI, FalSprite | Sprite-sheet generation | Varied; AutoSprite reports REST plus MCP | Check terms; FalSprite is open source (verify licence) |

## 5. Orchestration layers

| Layer | When | Caveats |
|---|---|---|
| `studio-gateway` (this plugin) | Default: budgeted, manifest-writing, licence-checking calls to first-party APIs | Limited to the providers it implements |
| ComfyUI with its MCP | ControlNet, IP-Adapter, LoRA stacking, deterministic seeds, repeatable graphs | Higher maintenance; official cloud MCP announced June 2026 and a local server in August 2026 (per the notes) |
| Hosted aggregators (fal, Replicate) | Many models behind one key | Official MCP status unconfirmed; community MCPs vary in quality |
| Scenario | Training plus a model hub in one account | Credit pricing opaque |

Rule: wrap first-party APIs in the gateway rather than depend on unmaintained community MCP servers for the main path.

## 6. 2D animation tools

- Frame-based sprite animation is well served by PixelLab, Retro Diffusion, Ludo.ai and AutoSprite; skeletal rigging automation for Spine or Live2D remains immature as of the notes.
- Practical path for non-pixel styles: generate layered body parts (head, torso, limbs) with an edit model, then rig semi-manually in Spine; or skip rigging and use short frame-based sheets for small sprites.
- A community Spine automation skill exists under a non-commercial licence, so it cannot ship in a commercial plugin; treat it as inspiration only.
- Always run the sprite-sheet post chain (key out background, slice, align pivots, silhouette consistency) described in `references/post-processing-and-provenance.md`.

## 7. 3D generators

| Platform | Strengths | Access | Notes |
|---|---|---|---|
| Tripo | Native low-poly mode (face limit range reported 48-20k), PBR, rig, retarget, Mixamo-compatible skeleton | API (gateway `model3d_generate` with `provider: tripo`) | Free-tier terms contradictory in sources; use paid tier |
| Meshy | One API for generate, remesh (quad or tri), UV, rig (humanoid), animate, text-to-motion | API (gateway `provider: meshy`), official MCP | Free tier is CC BY 4.0 (attribution); paid tiers private commercial |
| Hyper3D Rodin | Quad meshes from 4K to 50K faces | API only on a business plan | Higher entry cost |
| Tencent HY 3D (Hunyuan3D 3.x) | Cheapest per call, low-poly and topology endpoints, rigging | Cloud API | Open Hunyuan3D 2.x weights exclude the EU, UK and South Korea |
| Microsoft TRELLIS.2 | Open weights, MIT, PBR | Self-host, needs a large GPU | Cleanest open licence in the notes |
| SPAR3D, SAM 3D | Open weights, custom licences | Self-host | SPAR3D free under a revenue threshold; check terms |

Use the gateway's `face_limit` to request mobile budgets up front. Gateway providers for 3D are `tripo` and `meshy` only.

## 8. Rigging, motion and texturing

- Built-in rigging in generators (Meshy humanoid only; Tripo rig and retarget; Tencent rigging) removes a manual step but still needs weight cleanup (see `skills/technical-art/references/texture-and-3d-pipeline.md`).
- Text-to-motion: Uthana has the most production-ready API in the notes (limited release of its newer model); Tencent HY-Motion is an open-weights self-host option; Meshy sells text-to-motion at low credit costs.
- Texturing and PBR are best done inside the generators; for stylized games re-map to the project shader and remove baked lighting.
- No dedicated, production-grade AI generator for particle systems or shaders was found; use an agent to write shader code under the safety protocol in `skills/technical-art`.
- Optimization is scriptable: vendor remesh or face limits, Blender headless Python, then gltfpack or gltf-transform. Blender MCP can drive a live Blender for exploration.

## 9. Post-processing services

| Operation | Options | Notes |
|---|---|---|
| Background removal | Native transparency (some OpenAI, Leonardo, PixelLab outputs); Recraft; Scenario; self-hosted segmentation | BRIA RMBG 2.0 weights are non-commercial (CC BY-NC); do not ship without a commercial agreement. Verify the licences of other self-hosted segmenters before use |
| Vectorization | Recraft, Scenario | Good for icons and flat art |
| Upscaling | Recraft crisp upscale (cheap), creative upscalers (expensive, can invent detail), other vendors | Never use generative upscalers on pixel art |
| Atlas and compression | TexturePacker CLI or engine tools; `image_post.py atlas` | See the texture file |

Gateway `image_postprocess` covers `remove_background`, `vectorize`, `upscale` through Recraft.

## 10. MCP servers

| Server | Status in the notes |
|---|---|
| Scenario | Official, 17-19 tools, OAuth recommended |
| PixelLab | Official remote HTTP MCP, subscription and bearer token |
| Retro Diffusion | Official, with cost estimation |
| Ludo.ai | Official on select plans |
| ComfyUI | Official cloud MCP (June 2026) and local server (August 2026) |
| Meshy | Official npm server, roughly 20-24 tools, needs a paid API key |
| Tripo | Official but alpha and Blender-coupled |
| Rodin | Official from the vendor |
| Blender MCP (community, MIT) | Most mature Blender bridge; multi-vendor generation helper |
| fal, Replicate | Community servers only in the notes |
| Unity MCP servers | Community; for engine-side work |

Policy: MCP servers can read or write the project and spend money; install only maintained, source-visible servers, store keys through plugin `userConfig`, and route spending through the gateway's budget where possible.

## 11. Licences and commercial terms

| Topic | Summary | Confidence |
|---|---|---|
| US copyright | Purely AI-generated material is not copyrightable; human authorship (selection, arrangement, substantial edits) is protectable | High for the general rule; case law evolving |
| Output ownership on paid plans | Reported granted to the user by Recraft, PixelLab, Leonardo, Meshy, Tripo, Rodin | Medium; read the current terms |
| Free tiers | Often non-commercial or attribution only (Recraft free: vendor owned and non-commercial; Meshy free: CC BY 4.0; Tripo contradictory) | Medium |
| Open weights | Prefer permissive (Apache 2.0, MIT) for self-hosting; FLUX non-commercial variants and Hunyuan regional exclusions need care | Medium |
| IP indemnity | None found for the 3D tools; Adobe's partner-model terms exclude non-Adobe models from indemnity; other vendors' 2026 indemnity unverified | Low; ask counsel for any large commercial risk |
| Midjourney | No public API; terms bar automated access | High |

The gateway's `licence_check` flags non-commercial terms, free-tier output, revenue-threshold licences and missing provenance; set `GS_PLAN_<PROVIDER>` so it knows the plan tier.

## 12. Excluded and restricted vendors

| Vendor / tool | Status | Reason |
|---|---|---|
| Midjourney (including third-party wrappers) | Excluded | No official API; terms bar automation and resale; wrapper accounts risk bans |
| Free tiers of any provider for shipping assets | Excluded | Non-commercial or attribution-only terms |
| Non-commercial weights in the shipping path (BRIA RMBG 2.0, FLUX dev and 9B variants without a licence, community tools under non-commercial licences) | Excluded unless licensed | Licence |
| Hunyuan3D 2.x self-hosted for EU, UK or South Korea audiences | Restricted | Licence excludes those regions |
| Unmaintained community MCP wrappers for paid APIs | Restricted | Security and reliability; keys and budgets at risk |
| Any provider whose terms for output ownership were not retrieved (Scenario, Ludo) | Provisional | Read the terms before shipping assets; record the date |

Keep the allowlist and excluded list in `.gamestudio/config.json` provider preferences and in the style bible's AI generation lock.

## 13. Default provider recommendations

| Need | First choice | Second choice | Rationale |
|---|---|---|---|
| Bulk raster candidates | Gemini via gateway | OpenAI | Cost per candidate |
| Hero, key art, text-heavy | OpenAI via gateway | Gemini | Fidelity and text |
| Icons, flat UI, vector | Recraft vector | OpenAI plus vectorize | Native SVG |
| Pixel art | PixelLab or Retro Diffusion (outside gateway) | Pixelate plus palette step | Native grid |
| Sprite sheets | Ludo.ai or PixelLab | Edit-model grid plus post | Frame consistency |
| Custom style at 200+ assets | LoRA training (Scenario, fal, or self-hosted Qwen) | Reference-image edits | Consistency |
| 3D props | Tripo with `face_limit` | Meshy | Low-poly native |
| 3D rigged characters | Meshy or Tripo with rig, then cleanup | Human modeller | Rig built in |
| Background removal | Native transparency, then Recraft | Scenario | Quality and licence |

## 14. Volatile facts (as of Oct 2026 - verify)

All figures are as reported in October 2026 research notes; prices are list prices at the time and many come from third-party listings.

| Fact | Source |
|---|---|
| Artificial Analysis leaderboard: GPT Image 2.5 Sunburst and Flare at the top (about 0.21 per image at max quality), Nano Banana 2.1 fourth at about 0.034 per 1K image and about 0.017 on batch, FLUX 3 Image about 0.048 | https://artificialanalysis.ai/image/leaderboard/text-to-image |
| OpenAI image models: GPT Image 2 and 2.5 share token rates; output about 30 per million tokens, batch half price; approximate per-image 1024 px cost low 0.006, medium 0.053, high 0.211 (reseller-reported) | https://developers.openai.com/api/docs/pricing |
| Gemini image pricing: Nano Banana 2.1 1K 0.0336, 2K 0.0504, 4K 0.113; batch about half; original Nano Banana model shut down 2 Oct 2026 | https://ai.google.dev/gemini-api/docs/pricing |
| Recraft V4.1 raster about 0.035, vector about 0.08; background removal and vectorize about 0.01 each, crisp upscale about 0.004, creative upscale about 0.25 (units of about 0.001; parsed figures, confirm) | https://www.recraft.ai/pricing?tab=api |
| Retro Diffusion about 0.015 to 0.18 per image, animations 0.07-0.25, tilesets 0.10 | https://mcpservers.org/servers/retro-diffusion/retro-diffusion-mcp |
| PixelLab capabilities, MCP endpoint https://api.pixellab.ai/mcp, licence statements | https://www.pixellab.ai/llms-full.txt |
| Scenario MCP and API capabilities | https://help.scenario.com/en/articles/getting-started-with-the-scenario-mcp-server and https://docs.scenario.com |
| Ludo.ai API and MCP on select plans | https://ludo.ai/docs/api-mcp |
| Leonardo API and commercial rights on paid plans | https://docs.leonardo.ai |
| Meshy API credit costs (text-to-3D preview 20 credits; image-to-3D 20-35 depending on texture; refine 10-15) | https://docs.meshy.ai/en/api/pricing |
| Tripo P1 low-poly, rig 25 credits, retarget 10; Tencent HY 3D about 0.20-0.90 per call; Rodin API on the 120 per month business plan | Vendor docs and research notes (3D section); verify each |
| ComfyUI official MCP (cloud, 30 Jun 2026; local, 11 Aug 2026) | https://comfyui-wiki.com/en/news/2026-06-30-comfy-mcp-agent-integration |
| BRIA RMBG 2.0 is CC BY-NC 4.0 | https://github.com/Bria-AI/RMBG-2.0 |
| Midjourney terms bar automated access (version effective 27 May 2026) | https://unifically.com/blogs/midjourney-api |
| Adobe partner-model terms (non-Adobe models outside Firefly indemnity, effective 8 May 2026) | https://helpx.adobe.com/uk/legal/product-descriptions/partner-model.html |

Gateway defaults: `studio-gateway/pricing.json` lists model ids and prices with a `verified` flag; only some entries are verified against these notes. Treat any `verified: false` price as an estimate.
