# AI Tools and APIs for Production-Quality 2D Mobile Game Art (state as of October 2026)

Research date: 2026-10-18. Many sources are third-party API resellers, aggregators or vendor blogs; official pages were used wherever reachable (Artificial Analysis leaderboard, Google Gemini API pricing, OpenAI API pricing, Recraft API pricing, Scenario docs/help center, PixelLab llms-full.txt, Ludo.ai docs, Leonardo docs, TexturePacker docs). Conflicts and unverified items are flagged inline.

## 1. Which general image models lead in quality and controllability, which have official APIs, and what do they cost per image?

### Takeaway
As of October 2026 OpenAI's GPT Image 2.5 (Sunburst/Flare, Sept 2026) and GPT Image 2 top the Artificial Analysis (AA) text-to-image arena but cost about $0.21/image at max/high quality, while Google's Nano Banana 2.1 (Oct 2026) ranks #4 at about $0.034/image (1K) and $0.017 on batch, making it the best quality-per-dollar workhorse for high-volume asset generation. Midjourney still has no official API (and its ToS bans automation), so it is unusable in an automated pipeline. Open-weight options (Qwen-Image 2.1/Edit, FLUX.2 [dev]/[klein], HunyuanImage 3.0) matter mainly for self-hosted LoRA-based style locking.

### Cited Findings

**Leaderboard (AA-Image-T2I v2.1, fetched 2026-10-18; page shows no explicit snapshot date, latest entries are Oct 2026; prices are per 1,000 images at 1024x1024 default settings)** — [Artificial Analysis T2I leaderboard](https://artificialanalysis.ai/image/leaderboard/text-to-image)
- #1 GPT Image 2.5 Sunburst (max), OpenAI, Elo 1220, $210.7/1k, Sep 2026
- #2 GPT Image 2.5 Flare (max), OpenAI, Elo 1207, $210.7/1k, Sep 2026
- #3 GPT Image 2 (high), OpenAI, Elo 1186, $211/1k, Apr 2026
- #4 Nano Banana 2.1, Google, Elo 1174, $33.6/1k, Oct 2026
- #5 Grok Imagine Image 2.0, "SpaceXAI", Elo 1167, $60/1k, Aug 2026
- #6 MAI-Image-2.6, Microsoft AI, Elo 1166, $38.9/1k, Aug 2026
- #7 Nano Banana 2 (Gemini 3.1 Flash Image), Google, Elo 1140, $67/1k, Feb 2026
- #8 Muse Image, Meta, Elo 1127, $10/1k, Jul 2026
- #9 GPT Image 1.5 (high), OpenAI, Elo 1123, $133/1k, Dec 2025
- #12 FLUX 3 Image, Black Forest Labs, Elo 1116, $48/1k, Oct 2026
- #13 Nano Banana Pro (Gemini 3 Pro Image), Elo 1115, $134/1k, Nov 2025
- #15 Nano Banana 2 Lite, Elo 1106, $33.6/1k, Jun 2026
- #16 Seedream 5.0 Pro, ByteDance Seed, Elo 1100, $90/1k, Jul 2026
- #17 Qwen-Image-3.0-Pro, Alibaba, Elo 1094, $40/1k; #18 Qwen-Image-3.0 Elo 1071, $30/1k (Jul 2026)
- Open-weights leaders: Qwen-Image-2.1 (Elo 1042, no first-party API listed, Sep 2026); Ideogram 4.0 (Quality) Elo 1026 $100/1k and Ideogram 4.0 Elo 1001 $60/1k (listed by AA among open-weights models, Jun 2026); FLUX.2 [dev] Elo 1000 $12/1k (Nov 2025); FLUX.2 [dev] Turbo (fal) $8/1k; HunyuanImage 3.0 Instruct (Tencent) Elo 988, no API listed (Jan 2026).
- Note: earlier 2026 snapshots differ (e.g., GPT Image 2 at #1 with Elo 1369 on the older arena scale; MAI-Image-2.6-Preview took #1 on AA's *Image Editing* leaderboard and #2 in T2I in Aug 2026) — [AA on X: GPT Image 2 debut](https://x.com/ArtificialAnlys/status/2047184062012706980); [AA on X: MAI-Image-2.6](https://x.com/ArtificialAnlys/status/2092284543705456991?lang=en). AA also offers a UI/UX-design category filter relevant to HUD/icon work — [AA UI/UX category](https://artificialanalysis.ai/image/leaderboard/text-to-image?category=uiux_design).

**OpenAI (official API; token-billed)** — [OpenAI API pricing](https://developers.openai.com/api/docs/pricing)
- Model IDs: `gpt-image-2.5-sunburst`, `gpt-image-2.5-flare`, `gpt-image-2`, `gpt-image-1.5`, `gpt-image-1-mini`, `gpt-image-1`, `chatgpt-image-latest`.
- GPT Image 2 / 2.5: image input $8/M tokens, cached $2/M, image output $30/M; text input $5/M. Batch: $4 / $1 / $15 (half price). gpt-image-1-mini: image output $8/M ($4 batch). gpt-image-1: output $40/M. Cached-input rates for GPT Image 2/2.5 apply only via the Responses API.
- Approximate per-image output cost for gpt-image-2 at 1024x1024 (reported from OpenAI's calculator as of 2026-10-03): low ~$0.006, medium ~$0.053, high ~$0.211; prompt text and reference images billed on top — [laozhang blog](https://blog.laozhang.ai/en/posts/gpt-image-2-api-pricing.md). One catalog lists double these figures ($0.012/$0.106/$0.422) — treated as an outlier — [EmpirioLabs](https://catalog.empiriolabs.ai/models/gpt-image-2).
- GPT Image 2.5 released Sept 8, 2026 as "ChatGPT Images 2.5"; Flare = speed/default (≈50% lower latency than GPT Image 2), Sunburst = tighter control across edits for premium/production work; same token rates as GPT Image 2; also available in Adobe Firefly — [Grida docs](https://grida.co/docs/models/gpt-image-2.5); [DataNorth](https://datanorth.ai/news/openai-launches-chatgpt-images-2-5); [fal GPT Image 2.5](https://fal.ai/gpt-image-2.5).
- Transparent backgrounds: `background: "transparent"` with `output_format` png/webp reportedly opened for gpt-image-2 as a preview on 2026-08-21 (generations, edits, and Responses image tool) — [APIYI docs](https://docs.apiyi.com/en/live/2026-08/gpt-image-2-transparent-background); [The Decoder](https://the-decoder.com/openais-gpt-image-2-can-now-generate-images-without-a-background/). CONFLICT: an OpenAI community thread reports "Transparent background is not supported for this model" on gpt-image-2, with a reply that the preview was discontinued and GPT Image 2.5 has more robust transparency — [OpenAI Community](https://community.openai.com/t/is-transparent-background-support-broken-in-gpt-image-2/1402707).

**Google Gemini image models (official Gemini API)** — [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing)
- Nano Banana 2.1 (ID shown as `gemini-nano-banana-2.1`): 1K $0.0336, 2K $0.0504, 4K $0.113; batch 1K $0.0168 / 2K $0.0252 / 4K $0.0567.
- Nano Banana 2 (`gemini-3.1-flash-image`): 0.5K $0.045, 1K $0.067, 2K $0.101, 4K $0.151; batch about half.
- Nano Banana 2 Lite (`gemini-3.1-flash-lite-image`): 1K $0.0336 (batch $0.0168).
- Nano Banana Pro (`gemini-3-pro-image`): 1K/2K $0.134, 4K $0.24; batch $0.067/$0.12.
- Original Nano Banana (`gemini-2.5-flash-image`) deprecated, shut down Oct 2, 2026. No free tier for image output on paid rows (AI Studio UI is free to test). Imagen 4 pricing was not on this page.
- Nano Banana 2 accepts up to 14 reference images for character/object consistency — [Krea docs](https://docs.krea.ai/user-guide/features/nano-banana-2); [Runware character consistency guide](https://runware.ai/docs/models/google-nano-banana-2/guides/character-consistency). Practical reports: reliable for 1–2 primary characters, 3+ distinct characters significantly harder; per-character tagging of references helps — [Zilliz FAQ](https://zilliz.com/ai-faq/how-many-consistent-characters-can-nano-banana-2-maintain-across-a-workflow); [Atlas Cloud](https://www.atlascloud.ai/blog/guides/nanobanana-14-reference-images-consistency).
- Nano Banana 2.1 feature claims (built on "Gemini 3.6 Flash", 14 refs, stronger consistency) appear only on a third-party marketing site — UNVERIFIED — [Llamagen](https://llamagen.ai/ja/im/nano-banana-2-1).

**Midjourney** — no official public API, no API keys/usage pricing; ToS (version effective May 27, 2026) bars automated access and reselling; third-party wrappers (APIFrame, PiAPI, CometAPI) automate Discord/web and risk account bans — [Unifically](https://unifically.com/blogs/midjourney-api); [MyArchitectAI](https://www.myarchitectai.com/blog/midjourney-apis). (Vendor blogs; no Midjourney announcement of an API found.)

**Black Forest Labs FLUX**
- FLUX.2 tiers (third-party price listings; BFL's own page not fetched): [klein] 4B ~$0.014/img, klein 9B from $0.015; [pro] from $0.03 (edit from $0.045); [flex] from $0.05 (or $0.06/MP in and out); [max] from $0.07 (first MP $0.07, each additional MP $0.03); [dev] hosted ~$0.01–0.012; [flash] $0.005/MP via fal — [Puter guide](https://developer.puter.com/tutorials/flux-api-pricing/); [OpenRouter BFL listing](https://openrouter-gw-kz.just-ai.com/black-forest-labs); [UF docs on klein](https://docs.ai.it.ufl.edu/docs/navigator_models/models/blackforest-flux.2-klein); [Opper FLUX.2 flash](https://opper.ai/black-forest-labs/flux-2-flash).
- FLUX 3 announced July 23, 2026 (Video, Image, Action, and planned open-source FLUX 3 Dev); Image initially gated — [DataNorth](https://datanorth.ai/news/black-forest-labs-releases-flux-3); [LetsDataScience](https://letsdatascience.com/news/black-forest-labs-releases-multimodal-flux-3-56455df8). AA now lists "FLUX 3 Image" released Oct 2026 at $48/1k (#12), implying it is now API-accessible — [AA leaderboard](https://artificialanalysis.ai/image/leaderboard/text-to-image).

**Recraft (official API; strongest for vector/SVG, icons, UI)** — [Recraft API pricing](https://www.recraft.ai/pricing?tab=api)
- Prices in API units (1 unit ≈ $0.001; the page renders dollar figures run together with unit counts, so values below are parsed and should be confirmed): V4.1 35 units (~$0.035); V4.1 Flash 7 (~$0.007); V4.1 Pro 210 (~$0.21); V4.1 Vector 80 (~$0.08); V4.1 Pro Vector 300 (~$0.30); V4 Styles 35, V4 Styles Vector 50, V4 Styles Pro 100, V4 Styles Pro Vector 120; image-to-image/inpaint/replace or generate background 40 (~$0.04); custom style creation 40; vectorization 10 (~$0.01); background removal 10; crisp upscale 4; creative upscale 250; erase region 2. Vector edits 80 each.
- Ownership: paid plans own outputs with commercial rights (persists after cancellation); free plan outputs owned by Recraft, public, non-commercial. API units are prepaid, non-refundable, non-expiring — [Recraft API pricing](https://www.recraft.ai/pricing?tab=api).

**ByteDance Seedream 5.0 (BytePlus ModelArk API)** — Lite ~$0.035/image (supports 2K–4K, batch/streaming); Pro (`seedream-5-0-pro-260628`) pricing inconsistent across sources ($0.045 at 1.5K / $0.09 at 2K per Higgsfield; flat $0.12 via APIYI; official uses output-pixel tiers ≤2.36MP/>2.36MP plus a fee for extra reference images); Pro limited to 1K/2K — [Opper](https://opper.ai/bytedance/seedream-5); [Higgsfield](https://higgsfield.ai/blog/best-platforms-seedream-5); [APIYI](https://docs.apiyi.com/en/api-capabilities/seedream-image); [mer.vin](https://mer.vin/2026/07/seedream-5-0-pro-api-on-byteplus-precision-image-generation-and-multi-reference-editing/).

**Qwen-Image (Alibaba)** — Qwen-Image and Qwen-Image-Edit-2509/2511 are Apache 2.0; 2511 improves character identity retention during edits and folds popular LoRAs into the base model — [Qwen-Image-Edit-2511 HF](https://huggingface.co/Qwen/Qwen-Image-Edit-2511); [Qwen-Image-Edit-2509 README](https://huggingface.co/Qwen/Qwen-Image-Edit-2509/blob/main/README.md). A community "Consistency LoRA" for Qwen-Image 2.1 (Oct 1, 2026) targets pixel drift in edits — [ComfyUI Wiki](https://comfyui-wiki.com/en/news/2026-10-01-qwen-image-2-1-consistency-lora).

### Inferences
- For an automated mobile pipeline, the best default split is: Nano Banana 2.1 (batch) for bulk generation/edits at ~$0.017–0.034/image; GPT Image 2.5 Sunburst/Flare for hero key art, store screenshots/marketing composites and text-heavy UI mockups (~$0.21/image at max quality, cheaper at medium); Recraft V4.1 Vector for icons/UI/SVG; FLUX.2/Qwen open weights when a trained LoRA is needed for strict style lock.
- At 1,000 assets with ~3 candidates each, Nano Banana 2.1 batch costs roughly $50 vs ~$630 for GPT Image 2.5 at max — significant at scale (derived from listed per-image prices).
- Midjourney should be excluded from any compliant automated plugin.

### Gaps
- Imagen 4 / Imagen family current pricing and status not found on the Gemini API page.
- Official BFL pricing page not fetched; FLUX 3 Image API pricing beyond AA's $48/1k not confirmed.
- MAI-Image-2.6, Muse Image (Meta) and Grok Imagine 2.0 API availability/terms not researched.
- Ideogram 4.0 API terms and whether its weights are truly open (AA lists it as open weights) not verified.
- Hunyuan Image 3.0 hosted API availability not confirmed.

## 2. Game-specialized platforms: style consistency, sprite sheets/animation, transparency, tileables, upscaling, API/MCP

### Takeaway
Scenario (custom-trained style LoRAs + a hub of 3rd-party models + official 17–19-tool MCP), PixelLab (deepest pixel-art toolset with official remote MCP at api.pixellab.ai/mcp), Retro Diffusion (pay-per-generation pixel art API + MCP), and Ludo.ai (sprite-sheet animation + REST API + MCP on select plans) are the most agent-ready game-specific platforms. Leonardo has a mature REST API (custom "Elements" training, transparency) but is less game-workflow-specific; Layer.ai and God Mode AI lack well-documented public APIs.

### Cited Findings

**Scenario (scenario.com, formerly Scenario.gg)**
- API capabilities: image generation via third-party models (providers incl. Alibaba, BFL, Google, OpenAI, Ideogram, Krea, Luma, Meta, Microsoft, MiniMax, Recraft, Runway, Tencent, xAI), video, 3D, audio, background removal, image/video upscaling, vectorization, content API, and a Training API to train models and compose LoRAs; OpenAPI spec downloadable; credit/compute-unit pricing — [Scenario API docs](https://docs.scenario.com).
- Official MCP server: connects a coding agent to your Scenario workspace; help center lists 17 tools (image, video, 3D, audio), setup guides for 11 platforms incl. Claude Code; OAuth recommended, API keys need write permission — [Scenario help center](https://help.scenario.com/en/articles/getting-started-with-the-scenario-mcp-server). Launch blog says 19 tools and works with your custom-trained models — [Scenario blog](https://www.scenario.com/blog/Scenario-Is-Now-Available-Directly-in-Your-AI-Agent); feature page says custom model training and LoRA composition are available through the agent — [Scenario MCP feature page](https://www.scenario.com/features/mcp).
- Pricing (secondary, partially stale): Free tier ~50 credits; Starter ~$15/mo (~$10 annual) 1,500 credits; studio tiers up to ~$200/mo; Enterprise custom; per-API-call credit costs not published — [Stork](https://www.stork.ai/en/scenario); [eesel (2024)](https://www.eesel.ai/blog/scenario-ai-pricing); [DataStudios](https://www.datastudios.org/post/scenario-custom-trained-ai-game-asset-generation-style-consistency-and-pricing-explained).
- A Ludo-authored comparison claims Scenario has no sprite-sheet/animation pipeline (vendor-biased) — [Ludo comparison](https://ludo.ai/compare/best-ai-sprite-generators).

**PixelLab (pixellab.ai) — pixel art specialist** — [PixelLab llms-full.txt](https://www.pixellab.ai/llms-full.txt)
- Models: PixFlux (medium–XL images, better text understanding), BitForge (small–medium).
- Characters with 4 or 8 directions + walk/run/idle/attack animations; skeleton animation (16–256px canvas); animate-with-text (4–16 frames); animation-to-animation; interpolation (64x64); edit animation (2–16 frames); 8-directional rotation (max 168x168).
- Tilesets: top-down and sidescroller, export as Wang, dual-grid 15-tile, or 3x3 sets (Wang works with Sprite Fusion); tiles in square/hex/isometric/octagon; isometric tiles 16/32px; map create/extend (200–400px canvases by tier).
- UI elements (up to 512x512 Pro); style-reference generation (up to 4 references, up to 512px); inpainting; image-to-pixel-art.
- Access: web creator, Aseprite extension (v1.3.7+), Pixelorama, Python/JS SDKs, REST API v2, and an MCP server (Godot tooling included) requiring an active subscription.
- Official MCP endpoint `https://api.pixellab.ai/mcp` over HTTP with Bearer token; tools include `create_character` (4/8 directions) and animation tools — [mcpservers.org listing](https://mcpservers.org/servers/pixellab-code/pixellab-mcp); [lobehub](https://lobehub.com/fr/mcp/pixellab-pixellab-mcp).
- Licensing: commercial use allowed; only restriction is not using outputs to train new models; PixelLab says it does not train on user inputs/outputs; Steam OK subject to disclosure — [PixelLab llms-full.txt](https://www.pixellab.ai/llms-full.txt). Dollar pricing not given in that document.

**Retro Diffusion — pixel art API**
- Pay-per-generation, prepaid credits that never expire; ~$0.015 (RD Fast) to $0.18/image (RD Pro); animations $0.07–$0.25; tilesets $0.10; free cost estimation endpoint; official MCP server listed — [mcpservers.org Retro Diffusion MCP](https://mcpservers.org/servers/retro-diffusion/retro-diffusion-mcp); API examples repo — [GitHub Retro-Diffusion/api-examples](https://github.com/Retro-Diffusion/api-examples). (Prices from secondary listings; official page says it is the source of truth.)

**Ludo.ai**
- REST API and MCP server expose the same features: sprites, icons, UI assets, textures, backgrounds, spritesheet animations, image-to-video, 2D-to-3D, SFX/music/voices; API/MCP only on select subscription plans — [Ludo API & MCP docs](https://ludo.ai/docs/api-mcp).
- Sprite animation: apply motion presets (walk/run/idle/attack) to a static character, export GIF/per-frame/JSON for Unity/Godot/GameMaker — [Ludo sprite generator for Godot](https://ludo.ai/tools/sprite-generator-for-godot).

**Leonardo.ai**
- Official REST API with Python/TypeScript SDKs; custom "Elements" training via `/api/rest/v1/elements` (example uses SDXL base); transparency generation (PNG without background) on compatible models/elements (example: Kino XL); Lucid Origin model available via API — [Leonardo custom training](https://docs.leonardo.ai/docs/custom-model-training); [Leonardo transparency](https://docs.leonardo.ai/docs/generate-images-using-transparency); [Leonardo SDKs](https://docs.leonardo.ai/docs/leonardoai-official-sdks).
- Pricing: consumer plans $12/$30/$60/mo; separate pay-as-you-go Production API with $5 starter credit; commercial rights on paid plans (not free); AWS Marketplace custom API contract $10,000/12 months — [PricePerToken](https://pricepertoken.com/leonardo-ai-pricing); [AWS Marketplace](https://aws.amazon.com/marketplace/pp/prodview-kb2orjd43snf6); [eesel 2025](https://www.eesel.ai/blog/leonardo-ai-pricing).

**Layer.ai** — platform for 2D/3D/video/audio with custom model training, Unity/Unreal/Godot exports, "API and webhook access" per a third-party profile; only a community (AI-made, "use with caution") MCP wrapper found — [yespress profile](https://yespress.io/layer.md); [community Layer MCP](https://glama.ai/mcp/servers/@bahadirbklg/layer-ai-mcp-server/blob/6ccd1d13606c8ade07d99bba262cbd6449e46068/README.md).

**God Mode AI** — sprites, 2D/3D animation, 360° rotation, UI; credit packs from $12 (non-expiring) and $19/mo plan (200 generations if results shared publicly); claims 100+ animation types; no public API confirmed — [Ludo comparison](https://ludo.ai/compare/best-ai-sprite-generators); [dolphinvoice listing](https://dolphinvoice.ai/zh/ai-apps/god-mode-ai-1052529).

**Other sprite-sheet tools** — AutoSprite (PNG sheets + atlas metadata for Unity/Godot/Phaser, REST API + MCP) — [FutureTools](https://futuretools.io/tools/autosprite-e77791ff); FalSprite open source (fal.ai image model + LLM prompt rewriting + BRIA bg removal, 2x2–6x6 grids) — [GitHub lovisdotio/falsprite](https://github.com/lovisdotio/falsprite); Segmind sprite sheet API — [Segmind](https://www.segmind.com/pixelflow/2d-character-animation-sprite-sheet-generator/api); Sprite-AI cited as budget pixel option — [Ludo comparison](https://ludo.ai/compare/best-ai-sprite-generators).

### Inferences
- For pixel-art mobile games, PixelLab (characters/animation/tilesets) + Retro Diffusion (pay-per-use) are the strongest API/MCP-native choices; both handle directional sprites and tilesets that general models struggle with.
- For non-pixel (painted/cartoon) styles, Scenario is the most complete agent-ready platform because it combines custom LoRA training, many frontier models, bg removal, upscaling, vectorization and an official MCP in one account.
- Ludo.ai is the most direct "static character -> sprite sheet" API/MCP option for non-pixel styles.

### Gaps
- No official per-call API pricing found for Scenario, PixelLab, Ludo, Layer.
- Rosebud AI art features/API not researched.
- No independent quality benchmark comparing game-specialized platforms found.

## 3. How do pipelines achieve character/style consistency across hundreds of assets, and is ComfyUI (+MCP) the best orchestration layer?

### Takeaway
The 2026 toolset is a hybrid: (a) multi-reference edit models (Nano Banana 2/2.1 with up to 14 references, GPT Image 2.5 Sunburst for controlled edits, Qwen-Image-Edit-2511, FLUX.2/Kontext-style editing) for zero-training consistency, and (b) trained LoRAs (Scenario Training API, fal LoRA trainers for FLUX.2/Qwen-Image, Leonardo Elements, Recraft custom styles) for strict style lock at scale. ComfyUI now has an official MCP (cloud, June 2026; local, Aug 2026), making it a strong orchestration layer for self-hosted/open-weight graphs, but hosted APIs (fal, Scenario, Gemini, OpenAI) are simpler for an agent that does not need custom node graphs.

### Cited Findings
- Nano Banana 2 accepts up to 14 reference images for character/object consistency; works best for 1–2 characters; tag references per character — [Krea](https://docs.krea.ai/user-guide/features/nano-banana-2); [Zilliz](https://zilliz.com/ai-faq/how-many-consistent-characters-can-nano-banana-2-maintain-across-a-workflow); [Atlas Cloud](https://www.atlascloud.ai/blog/guides/nanobanana-14-reference-images-consistency).
- GPT Image 2.5 Sunburst is positioned for "tighter control across edits" — [Grida](https://grida.co/docs/models/gpt-image-2.5).
- Qwen-Image-Edit-2511 (Apache 2.0) improves identity retention — [HF](https://huggingface.co/Qwen/Qwen-Image-Edit-2511).
- LoRA training costs on fal: FLUX.2 [dev] edit trainer = 0.0226 × steps × reference multiplier (~$47 for 1,000 steps, 1 ref); FLUX.2 [klein] 4B base trainer = 0.0046 × steps × multiplier (~$9.71 per 1,000 steps); fal guide cites Qwen-Image training at $2 per 1,000-step run and klein 4B at $5 (conflicts with the $9.71 figure, possibly edit vs. base trainer) — [fal FLUX.2 trainer](https://fal.ai/models/fal-ai/flux-2-trainer-v2/edit); [fal klein trainer](https://fal.ai/models/fal-ai/flux-2-klein-4b-base-trainer/edit); [fal FLUX vs Qwen guide](https://fal.ai/learn/tools/flux-vs-qwen-image).
- Scenario Training API trains custom models and composes LoRAs; available via MCP — [Scenario docs](https://docs.scenario.com); [Scenario MCP](https://www.scenario.com/features/mcp).
- Recraft offers custom style creation (40 units ≈ $0.04) and V4 Styles models that accept style references — [Recraft API pricing](https://www.recraft.ai/pricing?tab=api).
- PixelLab offers style-reference generation with up to 4 references — [PixelLab](https://www.pixellab.ai/llms-full.txt).
- ComfyUI: official Comfy MCP announced June 30, 2026 — agents search models/nodes/template workflows, execute shared workflow URLs, generate image/video/3D/audio on Comfy Cloud GPUs — [ComfyUI Wiki](https://comfyui-wiki.com/en/news/2026-06-30-comfy-mcp-agent-integration). Local server support (built on comfy-cli, works with Claude Code/Cursor) announced Aug 11, 2026 — [ComfyUI Wiki](https://comfyui-wiki.com/en/news/2026-08-11-comfy-mcp-local-server). Community alternative artokun/comfyui-mcp — [mdskills](https://www.mdskills.ai/apps/comfyui-mcp); a community ComfyUI MCP for 2D game assets exists (ComfyAI-MCP-GameAssets) — [glama](https://glama.ai/mcp/servers/@tuannguyen14/ComfyAI-MCP-GameAssets/blob/7e61ef062a7cab3d1938ff10d6d2eb47001796df/mcp_config.json).

### Inferences
- Recommended consistency recipe for an agent: (1) generate/approve a character "bible" sheet (turnaround + expressions) with a top model; (2) feed it as references to Nano Banana 2.1/GPT Image 2.5 edits for poses/variants; (3) once ~20–50 approved images exist, train a LoRA (Scenario or fal FLUX.2/Qwen) for bulk production; (4) enforce palette and canvas constraints in post (palette quantization for pixel art).
- ComfyUI + official Comfy MCP is the best choice when the pipeline needs ControlNet/IP-Adapter/LoRA stacking, deterministic seeds and repeatable graphs; for a plugin that must "just work," a hosted aggregator (fal/Replicate/Scenario) plus first-party APIs is lower-maintenance.

### Gaps
- No 2026 GDC talk or case study on AI 2D art pipelines located in this pass.
- FLUX.2 / FLUX Kontext editing specifics in 2026 (reference counts, pricing) not separately verified.
- IP-Adapter/ControlNet support status for the newest models (FLUX.2, Qwen-Image 2.x) not verified.

## 4. Best tools for 2D animation: sprite animation generation, skeletal rigging automation, frame interpolation

### Takeaway
Frame-based sprite animation is well served by PixelLab (pixel art, 4/8-direction walk/run/idle/attack, interpolation), Retro Diffusion (animations $0.07–0.25), Ludo.ai (motion presets -> sprite sheets via API/MCP), AutoSprite, God Mode AI and open-source FalSprite. Automated Spine/Live2D skeletal rigging remains immature: no official AI auto-rig from Esoteric (Spine) or Live2D was found; the main option is a community Claude skill with a non-commercial license.

### Cited Findings
- PixelLab: skeleton animation, animate with text (4–16 frames), animation-to-animation, interpolation, edit animation, 8-direction rotation — [PixelLab](https://www.pixellab.ai/llms-full.txt).
- Retro Diffusion animations $0.07–$0.25 — [mcpservers.org](https://mcpservers.org/servers/retro-diffusion/retro-diffusion-mcp).
- Ludo.ai motion presets, GIF/frames/JSON export, API + MCP — [Ludo](https://ludo.ai/tools/sprite-generator-for-godot); [Ludo API docs](https://ludo.ai/docs/api-mcp).
- AutoSprite REST API + MCP with atlas metadata — [FutureTools](https://futuretools.io/tools/autosprite-e77791ff); FalSprite (2x2–6x6 grids; idle/walk/run/attack/jump) — [GitHub](https://github.com/lovisdotio/falsprite); community approach using GPT + Image 1.5 grids (Mar 2026) — [OpenSkillIndex](https://openskillindex.com/skills/jamditis-claude-skills-journalism-animated-sprite-gen).
- MindStudio "Generate Spritesheet" outputs #00ff00 backgrounds requiring chroma key — [MindStudio](https://www.mindstudio.ai/capabilities/run-packaged-workflow-generate-spritesheet).
- Spine: community "Spine Animation AI" Claude skill (computer vision positions body parts, builds skeleton JSON, preset animations, Spine Web Player previews; Reskin Studio uses Gemini) — PolyForm Noncommercial license, ~252 stars — [GitHub GenielabsOpenSource/spine-animation-ai](https://github.com/GenielabsOpenSource/spine-animation-ai); [oosmetrics](https://oosmetrics.com/repo/GenielabsOpenSource/spine-animation-ai). Spine forum thread shows auto-rigging is only a feature request — [Esoteric forum](https://it.esotericsoftware.com/forum/d/25605-ai-and-spine). Pixa/Pixelcut auto-detect joints in flat 2D characters but no Spine/Live2D export documented — [Pixa](https://www.pixa.com/create/2d-character-rigging).

### Inferences
- For mobile, a practical path is: generate characters as layered parts (head/torso/limbs) with an edit model, then rig semi-manually in Spine; or skip rigging and use frame-based sprite sheets from PixelLab/Ludo for small sprites.
- The Genielabs skill could inspire an in-house rigging step but cannot be shipped commercially as-is due to its PolyForm Noncommercial license.

### Gaps
- No Live2D Cubism 2026 AI features found.
- Dedicated frame interpolation for sprites (e.g., RIFE/FILM applicability to pixel art) not researched.
- Video-model-to-sprite-sheet workflows (e.g., using video generators then frame extraction) not researched.

## 5. Post-processing: background removal, upscaling, vectorization, texture atlas packing

### Takeaway
Cheap API-based post-processing is widely available: Recraft (bg removal ~$0.01, vectorize ~$0.01, crisp upscale ~$0.004, creative upscale ~$0.25), Scenario (bg removal, upscaling, vectorization endpoints), Leonardo (bg removal/upscale), Magnific via Freepik API (~$0.08/2K, ~$0.16/4K community estimates), and Crystal upscaler on Replicate (~$0.025). Beware that BRIA RMBG 2.0 open weights are CC BY-NC (commercial use needs a BRIA license). TexturePacker's CLI supports ASTC/ETC2/Basis/KTX2 output and has a CI/Docker license, making it the standard atlas step.

### Cited Findings
- Recraft post-processing prices (units ≈ $0.001): vectorization 10, background removal 10, crisp upscale 4, creative upscale 250, erase region 2 — [Recraft API pricing](https://www.recraft.ai/pricing?tab=api).
- Scenario API includes background removal, image upscaling and vectorization endpoints — [Scenario docs](https://docs.scenario.com).
- Leonardo Production API exposes upscaling, background removal and Blueprints — [PricePerToken](https://pricepertoken.com/leonardo-ai-pricing).
- BRIA RMBG 2.0 (BiRefNet-based) is CC BY-NC 4.0; commercial use requires a BRIA agreement or API — [GitHub Bria-AI/RMBG-2.0](https://github.com/Bria-AI/RMBG-2.0); [BRIA blog](https://bria.ai/introducing-the-rmbg-v2-0-model-the-next-generation-in-background-removal-from-images).
- Magnific is now sold via Freepik plans (Premium+ $45/mo, Pro $280/mo); Freepik API offers Magnific Creative/Precision upscalers at ~$0.08 (2K)/~$0.16 (4K) community estimates; Topaz upscalers included in Freepik Premium+/Pro; Crystal on Replicate ~$0.025/image up to 200MP — [MyArchitectAI Magnific pricing](https://www.myarchitectai.com/blog/magnific-ai-pricing); [Vantaige](https://vantaige.io/ai-tool/magnific); [Rangy comparison](https://rangy.ai/blog/topaz-vs-magnific-vs-crystal).
- GPT Image 2 transparent output: same token cost as opaque (per APIYI) — [APIYI](https://docs.apiyi.com/en/live/2026-08/gpt-image-2-transparent-background).
- TexturePacker: CLI `TexturePacker --format phaser --sheet out.png --data out.json spritefolder`; supports ETC1/ETC2/PVRTC/DXT/ASTC/Basis Universal (ETC1S/UASTC); outputs PKM/KTX/KTX2/ASTC; `--convert-texture` mode for GPU compression; `.tps` project builds; CI/Docker license — [TexturePacker CLI docs](https://www.codeandweb.com/texturepacker/documentation/commandline); [Texture settings](https://www.codeandweb.com/texturepacker/documentation/texture-settings); [Supported formats](https://www.codeandweb.com/texturepacker/knowledgebase/supported-image-formats); Godot importer — [Godot Asset Store](https://store.godotengine.org/asset/codeandweb/texturepacker-importer).

### Inferences
- For pixel art, avoid generative "creative" upscalers; use nearest-neighbor scaling plus palette quantization; PixelLab/Retro Diffusion generate at native pixel resolution.
- Default automated post-chain: native transparency (GPT Image 2.5 / Leonardo / PixelLab) or bg removal (Recraft/Scenario API, or self-hosted BiRefNet after license check) -> trim/pad -> crisp upscale if needed -> TexturePacker CLI to ASTC/ETC2 atlases.

### Gaps
- Original BiRefNet and Real-ESRGAN license terms not verified in this pass.
- Official Topaz developer API pricing not found.
- Recraft V3/V2 vector pricing (older) not on current page.

## 6. Commercial licensing, IP risk, and App Store / Google Play / Steam AI-disclosure rules

### Takeaway
Most paid APIs grant users ownership/commercial rights to outputs (Recraft paid plans, PixelLab, Leonardo paid plans; OpenAI's terms historically assign output to the user), but purely AI-generated art is not copyrightable in the US, so studios cannot stop others copying raw AI assets without meaningful human authorship. Indemnification is limited and model-specific (e.g., Adobe Firefly's IP indemnity excludes partner models like OpenAI's). Steam requires disclosure of player-facing AI content (dev tools exempt since Jan 2026); Google Play and Apple focus on AI-generated content shown to users and generative-AI app safety, with no confirmed games-specific disclosure for pre-made AI art.

### Cited Findings
- US Copyright Office: purely AI-generated works not copyrightable; Thaler v. Perlmutter (D.C. Cir.) human authorship required; Part 2 report (Jan 29, 2025) — "prompts alone do not provide sufficient control"; Zarya of the Dawn: Midjourney images' copyright revoked while human text/arrangement protected — [Promise Legal](https://blog.promise.legal/ai-game-assets-copyright-steam-disclosure-2026/).
- Steam: Valve rewrote AI disclosure rules mid-January 2026 (dates reported as Jan 16/17/19); internal dev tools (e.g., code assistants) no longer require disclosure; player-facing generated content, store page assets, marketing materials and live-generated content still must be disclosed; developers liable for guardrails; players report via Steam Overlay — [Gigazine](https://gigazine.net/gsc_news/en/20260120-steam-updates-ai-disclosure-guidelines); [Notebookcheck](https://www.notebookcheck.net/Steam-updates-AI-disclosure-form-requiring-developers-to-report-visible-and-in-game-AI-but-not-background-tools.1206103.0.html); [Slashdot](https://games.slashdot.org/story/26/01/19/1735231/valve-has-significantly-rewritten-steams-rules-for-how-developers-must-disclose-ai-use). ~1 in 5 Steam games carried an AI disclosure by July 2026; Tim Sweeney called tags "irresponsible" — [Tech Insider](https://tech-insider.org/steam-ai-disclosure-2026); [LetsDataScience](https://letsdatascience.com/news/epic-ceo-criticizes-valve-steam-ai-disclosures-06e02306). ~8,000 games disclosed AI use in H1 2025 vs ~1,000 in all of 2024 — [Promise Legal](https://blog.promise.legal/ai-game-assets-copyright-steam-disclosure-2026/).
- Google Play: a law-firm analysis says Play policy does not expressly require disclosing AI use in descriptions (may be misleading to omit if AI is a key feature) — [Revera Legal](https://www.revera.legal/?p=3557); Aug 2026 Android Developers Blog reiterates enhanced GenAI app requirements targeting NCII/"nudify" content — [Android Developers Blog](https://android-developers.googleblog.com/2026/08/ensuring-safety-genai-preventing-non-consensual-intimate-content.html). CONFLICT/UNVERIFIED: Promise Legal claims AI-generated content labeling rules became enforceable April 15, 2026 with a visible label adjacent to generated output, extended to third-party AI integrations July 15, 2026 — [Promise Legal](https://blog.promise.legal/ai-game-assets-copyright-steam-disclosure-2026/); this appears to target apps that generate content for users at runtime and was not confirmed against Google's policy text. IARC questionnaire reportedly includes AI-content questions (same source, unverified).
- Apple App Store: AI-generated content must not deceive; Guideline 5.1.2(i) requires explicit consent before sending personal data to third-party AI services — [Promise Legal](https://blog.promise.legal/ai-game-assets-copyright-steam-disclosure-2026/).
- Adobe: partner-model terms effective May 8, 2026 — non-Adobe models (incl. OpenAI image models) fall outside Firefly IP indemnity; separate "Creative Partner Model Supplemental Coverage" only on certain paid plans — [Adobe partner-model terms](https://helpx.adobe.com/uk/legal/product-descriptions/partner-model.html).
- OpenAI/Google/IBM announced indemnity policies in late 2023, "subject to various terms and conditions"; 2026 status unverified — [Internet & Technology Law](https://www.internetandtechnologylaw.com/openai-generative-ai-indemnity-infringement-claims/).
- Recraft: paid plans own outputs with commercial rights; free plan outputs owned by Recraft and non-commercial — [Recraft](https://www.recraft.ai/pricing?tab=api).
- PixelLab: commercial use allowed, no training of new models on outputs — [PixelLab](https://www.pixellab.ai/llms-full.txt).
- Leonardo: commercial rights on paid plans only — [PricePerToken](https://pricepertoken.com/leonardo-ai-pricing).
- Midjourney ToS bans automated access — [Unifically](https://unifically.com/blogs/midjourney-api).
- FLUX licenses: only FLUX.2 [klein] 4B is Apache 2.0; klein 9B and FLUX.2 [dev] use the FLUX Non-Commercial License (self-hosting commercially needs a BFL license); sources conflict on whether outputs of non-commercial models may be used commercially — [klein model card mirror](https://huggingface.co/YuCollection/FLUX.2-klein-4B-bf16/blob/main/README.md); [InVideo license matrix](https://invideo.io/blog/open-source-image-models-licenses/); [canirun.ai](https://canirun.ai/license/flux-non-commercial/). Using BFL's hosted API (paid) avoids the self-hosting license issue.
- Qwen-Image/Qwen-Image-Edit: Apache 2.0 — [HF](https://huggingface.co/Qwen/Qwen-Image-Edit-2511).
- BRIA RMBG 2.0 weights: CC BY-NC 4.0 — [GitHub](https://github.com/Bria-AI/RMBG-2.0).

### Inferences
- A plugin should log provenance (model, prompt, references, date) per asset and auto-generate Steam AI-disclosure text; it should encourage human editing/arrangement to strengthen copyright claims on final assets.
- For self-hosted open weights, prefer Apache-2.0 models (Qwen-Image family, FLUX.2 klein 4B) to avoid license ambiguity.

### Gaps
- Current (2026) OpenAI Terms of Use output-ownership text could not be fetched (403); Google Gemini API / Vertex AI generated-output indemnity 2026 terms not verified.
- Scenario and Ludo output-ownership/indemnity terms not retrieved.
- Apple's specific App Review guideline text for AI-generated game art not verified from primary source.

## 7. Existing MCP servers for these image tools

### Takeaway
Official MCP servers now exist for Scenario (17–19 tools incl. training), PixelLab (remote HTTP at api.pixellab.ai/mcp), Retro Diffusion, Ludo.ai, and ComfyUI (Comfy Cloud MCP + local server). fal.ai and Replicate MCP servers found were community-built. An agent can cover most needs with Scenario/PixelLab/Ludo MCPs plus direct first-party API calls (OpenAI, Gemini, Recraft).

### Cited Findings
- Scenario official MCP — [Scenario help center](https://help.scenario.com/en/articles/getting-started-with-the-scenario-mcp-server); [Scenario blog](https://www.scenario.com/blog/Scenario-Is-Now-Available-Directly-in-Your-AI-Agent). Community Scenario MCP (generate_image, remove_background) — [mcp.so](https://mcp.so/ja/servers/scenario-ai-mcp-server).
- PixelLab official MCP (`https://api.pixellab.ai/mcp`, Bearer token; subscription required; Godot tooling); npm `pixellab-mcp` (get_balance etc.); PixelLabRat desktop app/MCP — [mcpservers.org](https://mcpservers.org/servers/pixellab-code/pixellab-mcp); [unpkg README](https://app.unpkg.com/pixellab-mcp@1.1.0/files/README.md); [glama PixelLabRat](https://images.glama.ai/mcp/servers/DasDarki/PixelLabRat); [PixelLab llms-full](https://www.pixellab.ai/llms-full.txt).
- Retro Diffusion MCP (incl. free cost-estimate) — [mcpservers.org](https://mcpservers.org/servers/retro-diffusion/retro-diffusion-mcp).
- Ludo.ai MCP + REST API (select plans) — [Ludo docs](https://ludo.ai/docs/api-mcp).
- ComfyUI official MCP (cloud, Jun 30 2026; local, Aug 11 2026) — [ComfyUI Wiki](https://comfyui-wiki.com/en/news/2026-06-30-comfy-mcp-agent-integration); [ComfyUI Wiki local](https://comfyui-wiki.com/en/news/2026-08-11-comfy-mcp-local-server); community artokun/comfyui-mcp — [mdskills](https://www.mdskills.ai/apps/comfyui-mcp).
- fal.ai community MCPs (600+ models; generate_image/run_model; e.g., raveenb/fal-mcp-server; install `claude mcp add fal --env "FAL_KEY=..." -- npx -y fal-mcp-server`) — [glama raveenb](https://glama.ai/mcp/servers/@raveenb/fal-mcp-server/blob/1bfc317cf094a50b741e7221bd588f0a8ac681b4/README.md); [glama Gravicity](https://glama.ai/mcp/servers/@Gravicity/fal-mcp-server/blob/187bfbe2841238835d96ee3beb2bbcfcac123c00/README.md).
- Replicate: only community MCP servers found (e.g., tzafrir, gerred FastMCP early alpha) — [mcp.so](https://mcp.so/zh/servers/tzafrir_mcp-server-replicate); [glama gerred](https://glama.ai/mcp/servers/gerred/mcp-server-replicate/tree/568024cbab6f7da22a85d7bd5787f2e835e4e54a/src).
- AutoSprite MCP + REST — [FutureTools](https://futuretools.io/tools/autosprite-e77791ff).
- Layer.ai: community MCP only — [glama](https://glama.ai/mcp/servers/@bahadirbklg/layer-ai-mcp-server/blob/6ccd1d13606c8ade07d99bba262cbd6449e46068/README.md).

### Inferences
- For the plugin, wrapping first-party image APIs (OpenAI, Gemini, Recraft) in a small in-house MCP or skill is likely more reliable than relying on unmaintained community fal/Replicate MCPs.

### Gaps
- Official OpenAI image MCP / Google Gemini image MCP not found in this pass.
- Whether fal.ai or Replicate launched official MCP servers in 2026 is unconfirmed (searches returned only community projects).
