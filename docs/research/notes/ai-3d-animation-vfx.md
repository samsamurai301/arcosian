# AI 3D Asset, Animation and VFX Pipeline for Mobile Games (state as of October 2026)

Research date: 2026-10-18. Most pricing comes from official vendor docs fetched this month. Where only aggregator or reseller numbers exist, the notes say so. Dates are given so older information can be spotted.

## Which image/text-to-3D generators lead in 2026, and how do they compare on mesh quality, topology, PBR, quad remeshing, polycount control, API, cost per model, and open weights?

### Takeaway
For API-driven, mobile-ready output, the strongest hosted choices in October 2026 are:
- **Tripo P1 (Smart Mesh)**: native low-poly, 48–20k faces, PBR, v3 API.
- **Meshy (meshy-6 / meshy-7.1)**: one API covering generate, remesh (quad or tri, 100–300k), UV, rig, animate, and text-to-motion.
- **Hyper3D Rodin Gen-2.5**: quad meshes from 4K to 50K faces. API only on the $120/mo Business plan.
- **Tencent HY 3D Global (Hunyuan3D 3.0/3.1)**: cheapest per call (about $0.20–0.90), with LowPoly, Smart Topology, and rigging endpoints.

For self-hosting:
- **Microsoft TRELLIS.2-4B** (MIT, PBR, 24GB+ GPU) is the leading permissively licensed open model.
- **Hunyuan3D 2.1** is fully open, but its license excludes the EU, UK, and South Korea.
- Hunyuan3D 3.x appears to be cloud-only.

### Cited Findings

**Meshy (meshy.ai): API pricing, official docs fetched Oct 2026**
- Text-to-3D preview costs 20 credits (meshy-6, mesh only). Image-to-3D and Multi-image-to-3D cost 20 credits mesh-only, 30 with 2K/4K textures, and 35 with 8K textures — [Meshy API Pricing](https://docs.meshy.ai/en/api/pricing)
- Other operations — [Meshy API Pricing](https://docs.meshy.ai/en/api/pricing):
  - Refine or Retexture: 10 credits (2K/4K) or 15 (8K)
  - Remesh: 5
  - UV Unwrap: 5
  - Convert: 1
  - Resize: 1
  - Auto-Rigging: 5
  - Animation: 3 per action, up to 10 per request
  - Text-to-Motion: 10 (prime mode) or 3 (swift mode)
- The pricing table names **meshy-7.1** as the latest model. It adds +5 credits for `geometry_resolution: "2k"` or `"4k"` ("Ultra" geometry). The `model_type: "lowpoly"` option uses meshy-6 pricing and **retires on October 30, 2026** — [Meshy API Pricing](https://docs.meshy.ai/en/api/pricing)
- A third-party blog says Meshy's replacement for `lowpoly` is `smart-topology` with `meshy-t2`, and that Smart Topology outputs triangles, not quads. This is unverified secondhand — [GamineAI blog](https://gamineai.com/blog/meshy-remesh-lowpoly-retires-oct-30-indie-migrate-worksheet-2026)
- Meshy's low-poly mode launched with Meshy-6 in January 2026 and is now labelled "Topology Mesh" — [Meshy tutorial](https://www.meshy.ai/ko/tutorials/make-low-poly-3d-models)
- **Remesh API** — [Meshy Remesh API](https://docs.meshy.ai/en/api/remesh):
  - `topology`: `triangle` (default, decimated) or `quad` (quad-dominant)
  - `target_polycount`: 100–300,000 (default 30,000)
  - `decimation_mode`: adaptive levels 1–4
  - `target_formats`: glb, fbx, obj, usdz, blend, stl, 3mf
  - Accepts Meshy task IDs or external glb/gltf/obj/fbx/stl URLs, up to 400 MB. Failed tasks refund credits.
- Webapp plan prices (EUR, from meshy.ai/pricing, Oct 2026) — [Meshy Pricing](https://www.meshy.ai/pricing):

  | Plan | Price | Credits/month | API | License |
  |---|---|---|---|---|
  | Free | €0 | 100 | No | CC BY 4.0 |
  | Pro | €19/mo | 1,000 | Yes | Private, customer-owned |
  | Premium | €38/mo | 3,000 | Yes | Private, customer-owned |
  | Ultra | €95/mo | 8,000 | Yes | Private, customer-owned |
  | Studio | €67/mo | 5,500 shared | Yes | Private, customer-owned |
  | Enterprise | Custom | Custom | Yes | Private, customer-owned |

- API usage is prepaid credits. Volume or custom contracts go through sales — [Meshy API Pricing](https://docs.meshy.ai/en/api/pricing)
- A secondary source lists older USD tiers: Pro $20, Max $60, Enterprise/API $90 as of mid-2026. Its own price-history page shows later renamed tiers ("Premium", "Studio"). This is consistent with the EUR page above, so treat the old USD tiers as outdated — [CostBench Meshy](https://costbench.com/software/ai-3d-generation/meshy/)

**Tripo (tripo3d.ai, VAST): official developer docs**
- **Tripo P1** (snapshot `P1-20260311`) is "optimized for best-in-class low-poly generation" — [Tripo P1 docs](https://developers.tripo3d.com/en/models/p1)
  - Inputs: text, image, or multiview
  - `face_limit`: 48–20,000. Recommended minimums are 150 for simple and 250 for complex models.
  - Topology rated "Cleanest"
  - PBR on by default
  - Speed: about 10 s for a base mesh, about 60 s with texture
  - Parameters: `face_limit`, `texture`, `pbr`, `export_uv`
  - Endpoints: `v3/generation/{text|image|multiview}-to-model`
  - Rate limit: 3 parallel tasks for the P series
- **P1 cost**: text-to-3D 30, image or multiview 40 (no texture). Standard texture adds 10, so 40/50/50. Detailed texture costs 50/60/60. **Quad, smart_low_poly, generate_parts and geometry_quality are not supported on P1** — [Tripo P1 docs](https://developers.tripo3d.com/en/models/p1); same in [Tripo v2→v3 migration guide](https://developers.tripo3d.com/assets/developer/tripo-v2-to-v3-migration/SKILL.md) (sending these keys returns HTTP 400)
- Tripo announced Smart Mesh P1.0 in March 2026 as a native 3D diffusion model for engine-ready, low-poly assets "in as little as two seconds" — [Barchart press release](https://www.barchart.com/story/news/936837/tripo-ai-introduces-smart-mesh-p1-0-defining-a-new-phase-for-ai-3d-production)
- **Tripo 3.0** launched on September 26, 2025, with about 20B parameters. It is a separate model from P1 — [Pasquale Pillitteri review](https://pasqualepillitteri.it/en/news/7811/tripo-ai-review-3d-model-generator)
- Quad output exists on Tripo's H3.1 endpoint, as hosted by reseller Atlas Cloud. Turning on quad exports FBX instead of GLB — [Atlas Cloud Tripo](https://www.atlascloud.ai/models/Tripo)
- Scenario's guide lists P1 controls including Texture level (Standard, Detailed, Extreme), Auto Size, PBR, Face Limit, and Quad. Its Quad claim contradicts Tripo's own docs — [Scenario Tripo guide](https://help.scenario.com/articles/4692888910-tripo-family-the-complete-guide)
- **Billing model**: credits are frozen when a task is created, deducted on success, and refunded on failure or cancel — [Tripo billing docs](https://developers.tripo3d.com/en/docs/billing)
- Historical API price was $0.01 per credit (blocks of 100), with concurrency of 10 Draft and 5 Refine tasks. This is from the launch-era announcement and may be outdated — [Tripo OpenAPI announcement](https://www.tripo3d.ai/blog/announcement-tripo-openapi-platform-payment-system)
- Subscription tiers conflict between aggregators — [PricingSaaS Tripo](https://pricingsaas.com/companies/tripo3d); [CostBench Tripo history](https://costbench.com/software/ai-3d-generation/tripo-ai/price-history/):
  - Pro $19.9, Max $89.9, Team $109.9 (June 2026)
  - Pro $20, Team $55, Max $90 (Oct 2026)
  - One snapshot shows the top tier rising from $110 to $330 per month (August 2026)

**Hyper3D Rodin (Deemos)**
- Plans — [Hyper3D Pricing](https://hyper3d.ai/pricing):
  - Free: direct credits at $1.5 per credit
  - Creator: $30/mo (about 60 models). Includes Smart Low-Poly, baked normals from high-poly, and more polycount options.
  - Business: $120/mo or $96/mo yearly (about 416 models). **Full API access**, High-Poly Quads, 120–240 RPM.
  - Enterprise: on-prem deployment and custom LoRA or fine-tuning
- **Rodin Gen-2.5** launched in May 2026 and builds on SIGGRAPH 2025 Best Paper research — [Scenario Rodin Gen-2.5](https://help.scenario.com/articles/3791851266-rodin-hyper3d-gen-2-5-models-the-essentials)
  - Quad options range from 4K to 50K faces. Triangle options range from 2K to 500K.
  - HighPack multiplies quad face count by about 16×.
  - Quad is the recommended choice for rigging.
- 80.lv describes Gen-2.5 as producing quad meshes with sculpt-level detail plus "Smart Low-Poly topology" — [80.lv Hyper3D](https://80.lv/partners/hyper3d)
- Reseller EmpirioLabs sells Hyper3D Gen-2 at $0.80 per request, pay-as-you-go — [EmpirioLabs](https://empiriolabs.ai/models/hyper3d-gen2)
- A Gen-2 model costs about 40 credits, per an unverified third-party estimate — [CostBench Rodin](https://costbench.com/software/ai-3d-generation/rodin-hyper3d/hidden-costs/)

**Tencent Hunyuan3D / HY 3D Global**
- Tencent Cloud HY 3D Global billing — [Tencent Cloud billing doc](https://www.tencentcloud.com/document/product/1284/75281):
  - Professional API, per generation: Normal (textured) 25 credits, LowPoly 30, Geometry (untextured) 15, Sketch 25
  - Professional add-ons, +10 credits each: MultiViewImages, EnablePBR, FaceCount
  - Express API: 15 credits per text- or image-to-3D call, +10 for PBR
  - Post-processing: Part Generation 30, **Smart Topology 50**, Texture Edit 30, **UV Unfold 10**, **Auto Rigging 10**, Convert Format 5
  - Choosing model version 3.0 or 3.1 costs no extra credits
  - Prepaid packs: $15 per 1,000 credits ($0.015 each) down to $1,350 per 100,000 ($0.0135 each). Postpaid is $0.02 per credit. 200 free credits per user. Failed tasks are not charged.
- Hunyuan3D 3.0 is offered through the Tencent Cloud API and the Hunyuan 3D engine. Open-sourced repos are Hunyuan3D-1, 2/2.1, HunyuanWorld-1.0, Hunyuan3D-Part, and Hunyuan3D-Omni. **3.0 is not on the open-source list.** This is secondary — [ToolNavs](https://toolnavs.com/en/article/823-hunyuan-3d-engine-global-eingef%C3%BChrt-eine-ki-3d-engine-f%C3%BCr-kreative-menschen-welt)
- Hunyuan3D-2.1 is described as fully open: model weights, training and inference code, and data pipelines — [Hunted.space](https://hunted.space/product/hunyuan3d-2-1); [ComfyUI Wiki Hunyuan3D](https://comfyui-wiki.com/en/models/hunyuan3d)
- Resellers: Atlas Cloud lists Hunyuan 3D Pro at $0.02 per generation (unverified) — [Atlas Cloud Tencent](https://www.atlascloud.ai/tr/providers/tencent). Layer lists "Hunyuan3D v3.1 Pro" — [Layer](https://www.layer.ai/models/tencent--hunyuan3d-v3.1-pro)

**Microsoft TRELLIS.2 (open weights)**
- From the official repo — [TRELLIS.2 GitHub](https://github.com/microsoft/TRELLIS.2):
  - 4B parameters, image-to-3D, **MIT license** for model and code (dependencies such as nvdiffrast have their own licenses)
  - Outputs a PBR mesh with base color, roughness, metallic, and opacity, exported to GLB
  - Speed on H100: about 3 s at 512³, about 17 s at 1024³, about 60 s at 1536³
  - Needs an NVIDIA GPU with at least 24GB. Tested on Linux only.
  - `to_glb` supports decimation, remeshing, texture size, and WebP textures. The companion CuMesh package does remesh, decimation, and UV unwrap.
  - About 12.2k stars
- Released December 2025 — [ComfyUI Wiki news](https://comfyui-wiki.com/en/news/2025-12-18-microsoft-trellis2-3d-generation)
- Sources disagree on VRAM: 16GB minimum for 512³ and 40GB recommended for 1024³ — [Codesota](https://www.codesota.com/news/trellis-2-3d-generation); the repo says at least 24GB — [TRELLIS.2 GitHub](https://github.com/microsoft/TRELLIS.2)

**Other models**
- **Meta SAM 3D Objects** is under a custom SAM license. Review the terms before commercial use. HF weights are gated — [Roboflow SAM 3D Objects](https://roboflow.com/model/sam-3d-objects); overview in [The Batch](https://www.deeplearning.ai/the-batch/metas-sam-3-image-segmentation-suite-analyzes-and-creates-3d-bodies-and-other-objects)
- **Stability SPAR3D** (January 2025, older) is free for commercial use under the Stability Community License. An enterprise license is required above $1M annual revenue — [AlternativeTo](https://alternativeto.net/news/2025/1/stability-ai-unveils-stable-point-aware-3d-for-real-time-3d-object-creation-from-images); [The Decoder](https://the-decoder.com/stability-ais-new-3d-model-aims-for-real-time-generation/)
- **3DAIStudio** is an aggregator front end that exposes TRELLIS.2 and Rodin Gen-2.5, among others — [3DAIStudio TRELLIS.2](https://www.3daistudio.com/Models/Trellis-2); [3DAIStudio Rodin Gen-2.5](https://www.3daistudio.com/Models/Rodin-Gen-2-5)

**Benchmarks (3D Arena)**
- The June 2025 paper describes the arena — [3D Arena paper](https://arxiv.org/pdf/2506.18787v1.pdf):
  - Pairwise human-vote ELO with 123,243 votes from 8,096 users across 19 models
  - Textured models gain about 144 ELO over untextured ones
  - Gaussian splats gain about 16.6 ELO over meshes
- The 3D Arena HF org shows recent additions of **TRELLIS.2-4B** and **SAM-3D-Objects** — [3D Arena HF org](https://huggingface.co/3d-arena)

### Inferences

**Approximate cost per mobile-ready asset** (my arithmetic from the official credit tables)
- **Meshy**: one asset (image-to-3D with texture 30 + remesh 5 + rig 5 + 3 animations 9) is about 49 credits.
  - About €0.93 on Pro (€0.019 per credit), or about €0.58 on Ultra (€0.0119 per credit).
  - Meshy does not publish a USD price for separate API credit packs.
- **Tripo P1**: image plus standard texture is 50 credits, rig is 25, and each retarget is 10.
  - At the historical $0.01 per credit, that is about $0.50 + $0.25 + $0.10 per animation.
  - The per-credit price is flagged as possibly outdated.
- **Tencent HY 3D**:
  - Normal + PBR + FaceCount is 45 credits ($0.61–0.90). LowPoly is 30 credits ($0.41–0.60). Express is 15 credits ($0.20–0.30).
  - Auto Rigging (10) adds $0.14–0.20. Smart Topology (50) adds $0.68–1.00.
  - Cheapest of the hosted options.
- **Rodin Business**: about $0.23–0.29 per model at the plan's own model estimate, but it needs a $96–120 monthly commitment for API access.

**Fit for mobile**
- Tripo P1 is the most direct "mobile low-poly by default" generator: hard face caps down to 48 and a 5,000-face mobile recommendation (see the rigging section).
- Use Rodin Gen-2.5 or Meshy quad remesh when you need clean, deformable quad topology for rigged characters.
- Use TRELLIS.2 or Hunyuan3D 2.1 self-hosting for bulk props when API cost or data control matters. Both need a decimation and UV pass afterwards, since their raw outputs are high-poly.
- Meshy is the only vendor with a single documented API covering generation, remesh (quad), UV, rig, animation library, and text-to-motion. That makes it the simplest single-vendor agent backend.
- Hunyuan3D 3.x appears cloud-only, so "open weights" for Tencent means 2.x-era models.

### Gaps
- **3D Arena rankings**: I could not retrieve the current leaderboard. The HF Space renders client-side and no recent ranking article turned up, so there is no independent quality ranking among Meshy-7.1, Tripo P1/3.x, Rodin Gen-2.5, Hunyuan 3.1, and TRELLIS.2.
- **Not researched this session (no 2026 sources)**: Luma Genie, CSM (Common Sense Machines), Kaedim, Sloyd, Zoo, and Stability SF3D. Background knowledge, unverified for 2026: Kaedim had shifted toward artist-in-the-loop production, Sloyd is parametric/procedural with an API, and Zoo is CAD-oriented (text-to-CAD), so it is not a game-asset tool.
- **Tripo**: current USD price per API credit and the current Tripo 3.x (H3.1) API credit table.
- **Hunyuan3D 2.1**: self-host VRAM figures were not verified.
- **Head-to-head tests**: no independent topology or UV comparisons between vendors were found.

## Auto-rigging and animation: what is the status of Mixamo, built-in rigging, AccuRIG, Anything World, Cascadeur, text-to-motion, and video-to-motion, and which are API-callable?

### Takeaway
API-callable rigging is now built into the generators:
- Meshy: humanoid-only, 5 credits
- Tripo: rig-check free, rig 25 credits, retarget 10 credits, Mixamo-compatible skeleton, in-place locomotion
- Tencent HY 3D: 10 credits

For text-to-motion:
- **Uthana** has the most production-ready API (GraphQL plus Python SDK, GLB/FBX output, model 3.0 in limited release since June 2026).
- **Tencent HY-Motion 1.0** (December 2025, open weights, 1B parameters) is the self-host option.
- Meshy also sells text-to-motion at 3–10 credits.

For other tools:
- Mixamo is alive but unmaintained, with no official API.
- RADiCAL was absorbed by Autodesk and closed in 2026.
- Video mocap APIs are mostly enterprise or sales-gated (Move.ai, DeepMotion).

### Cited Findings

**Rigging built into the generators**
- **Meshy Rigging API** — [Meshy Rigging API](https://docs.meshy.ai/en/api/rigging):
  - "currently only works well with standard humanoid (bipedal) assets." Non-humanoid or untextured meshes are not suitable.
  - Face count must be at most 300k (remesh first). The character must face +Z. `height_meters` defaults to 1.7.
  - Outputs a rigged FBX and GLB, plus optional walking and running animations, plus an armature-only GLB.
- Meshy Animation costs 3 credits per action (up to 10 per request). Text-to-Motion costs 10 (prime) or 3 (swift) — [Meshy API Pricing](https://docs.meshy.ai/en/api/pricing)
- **Tripo rigging** — [Tripo Rig docs](https://developers.tripo3d.com/en/models/rig); [Tripo Animation docs](https://developers.tripo3d.com/en/models/animation); [Tripo Quick Start](https://developers.tripo3d.com/en/docs/quick-start):
  - Endpoints: `POST /v3/animations/rig-check` (free), `/v3/animations/rig` (25 credits), `/v3/animations/retarget` (10 credits per animation, batch up to 5)
  - In-place mode removes root motion for game locomotion
  - Quick Start recommends `face_limit` 5000 as mobile- and game-friendly, and the `"mixamo"` skeleton spec for Unity/Unreal
  - Rigging and animation share a limit of 3 parallel tasks
  - Preset libraries differ by snapshot: 90+ biped presets on v1.0 versus 16 universal presets on v2.5
- **Tencent HY 3D Auto Rigging** costs 10 credits per call — [Tencent Cloud billing doc](https://www.tencentcloud.com/document/product/1284/75281)

**Mixamo and standalone riggers**
- **Mixamo**: still online and free with an Adobe account, but in maintenance mode with no feature updates in years and no announced shutdown (July 2026 guide) — [Cinevva Mixamo guide](https://app.cinevva.com/guides/free-character-animations-rigging)
- A vendor blog claims Mixamo upload, download, and rigging are gated by a flaky Adobe identity layer. This is promotional and should be treated cautiously — [Sorceress blog](https://sorceress.games/blog/replace-the-mixamo-auto-rig-browser-no-adobe-id)
- The Mixamo Rig Blender add-on lists Blender 4.2 LTS as compatible and 5.5+ as unsupported — [Blender Extensions](https://extensions.blender.org/add-ons/mixamo-rig/versions/)
- Named alternatives — [Cinevva Mixamo guide](https://app.cinevva.com/guides/free-character-animations-rigging):
  - **Reallusion AccuRIG 2.0**: Windows, free ActorCore account
  - Cinevva browser Auto Rigger
  - Sorceress 3D Studio: browser, claims non-humanoid support
  - Quaternius Universal Animation Library: CC0, retargetable

**Other animation tools**
- **Anything World**: its "Animate Anything" service uses an AI agent to rig static models, alongside Unity and Unreal asset libraries. Current API and pricing are not confirmed — [Anything World itch.io](https://anything-world.itch.io)
- **Cascadeur** (AI-assisted, physics-based keyframing; desktop app with no cloud API found):
  - 2026.1 (April 2026) added a rebuilt Unreal Live Link, Filament rendering, and a generative Root Motion tool — [Digital Production 2026.1](https://digitalproduction.com/2026/04/09/cascadeur-2026-1-adds-unreal-live-link-filament-rendering-and-ai-root-motion/)
  - 2026.2 (August 2026) added Additive Animation Layers (alpha), Easing controls, BVH import, and AutoPosing that adapts to geometry plus better quadrupeds — [Digital Production 2026.2](https://digitalproduction.com/2026/08/03/cascadeur-2026-2-adds-animation-layers/); [Cascadeur blog](https://cascadeur.com/blog/view/cascadeur-2026-2-animation-layers-easing-new-languages)

**Text-to-motion**
- **Uthana**:
  - A changelog entry dated June 15, 2026 says text-to-motion-3.0 is in limited release via the async `create_text_to_motion_job` mutation (poll a Job; contact support for access) — [Uthana API changelog](https://uthana.com/docs/api/changelog)
  - A May 2026 entry added diffusion-v2 parameters (steps, cfg_scale, length, seed), motion stitching, and playback speed — [Uthana API changelog](https://uthana.com/docs/api/changelog)
  - The Python SDK (`ttm.create`) takes prompt, character, model, length, cfg, and seed, and downloads GLB at a chosen fps — [PyPI uthana](https://pypi.org/project/uthana/)
  - Output is skeletal animation, not video — [Uthana TTM](https://uthana.com/models/text-to-motion)
  - 3.0 is positioned as the best for prompt adherence and multi-step sequences. Older models are better for fast, cheap iteration — [Uthana 3.0 blog](https://uthana.com/blog/text-to-motion-30-sets-a-new-bar-for-ai-animation)
  - Scenario hosts Uthana TTM, retargeted to your character, as GLB or FBX at 24, 30, or 60 fps — [Scenario Uthana docs](https://docs.scenario.com/docs/3d-model-generation-uthana)
- **Tencent HY-Motion 1.0** — [HY-Motion arXiv](https://arxiv.org/html/2512.23464v1); [Vitrina](https://vitrina.ai/?p=133462); [NYU Shanghai RITS](https://rits.shanghai.nyu.edu/ai/tencent-open-sources-hy-motion-1-0-a-billion-parameter-text-to-motion-ai-model/):
  - Billion-parameter DiT flow-matching text-to-motion model
  - Trained on 3,000+ hours of pretraining data, 400 hours of curated fine-tuning data, and RLHF
  - Covers 200+ motion categories
  - Weights at HF `tencent/HY-Motion-1.0`, code at GitHub `Tencent-Hunyuan/HY-Motion-1.0`
  - Released December 30, 2025, with a 1B model and a Lite variant

**Video-to-motion mocap**
- **RADiCAL**: Autodesk acquired its core technology and IP (announced April 9, 2026). The RADiCAL site closed on July 6, 2026 — [CG Channel](https://www.cgchannel.com/tag/radical-canvas/)
- **Move.ai**: official consumer plans are Personal $15/mo and Advanced $250/mo, with no API in those plans — [Move.ai docs](https://docs.move.ai/knowledge/move-ai-pricing-plans-credits). API/SDK access is Enterprise, custom pricing — [FitGap Move.ai](https://us.fitgap.com/products/move-ai)
- **DeepMotion**: Animate 3D has a public REST API that produces FBX and BVH, but API pricing is not disclosed — [NeuronFeed](https://neuronfeed.com/compare/move-ai-vs-deepmotion); [Indexator DeepMotion](https://dev.indexator.ai/companies/deepmotion). Its free plan is personal or non-commercial only — [Neolemon guide](https://www.neolemon.com/blog/best-ai-motion-capture-tools-for-character-animation)
- **Rokoko Vision**: free plan limited to 15-second clips. **Plask**: browser-based, free daily limit, FBX/GLB/BVH export. Neither has a shutdown notice — [Neolemon guide](https://www.neolemon.com/blog/best-ai-motion-capture-tools-for-character-animation)

### Inferences
- For an agent pipeline, the API-native path is: generate → remesh → rig → retarget/animate, all inside Tripo or Meshy (or Tencent). Text-to-motion (Uthana API, Meshy TTM, or self-hosted HY-Motion) can produce bespoke clips beyond the preset libraries.
- Mixamo and AccuRIG are GUI-only, so an agent cannot drive them reliably.
- HY-Motion outputs a body-model skeleton (secondary sources say SMPL-H, unverified). It would need a retargeting step, for example in Blender, onto Mixamo or Tripo skeletons.
- Non-humanoid rigging (quadrupeds, creatures) is the weakest automated link. Meshy is explicitly humanoid-only, and Tripo's "universal presets" on v2.5 may partly cover it (unverified).
- Video-to-motion mocap is the least automatable category: Move.ai's API is enterprise-only, DeepMotion's API pricing is opaque, and RADiCAL is gone.

### Gaps
- Exact animation-library size and quadruped support for Meshy's Animation API.
- Anything World API status and pricing in 2026.
- Uthana API pricing per generation.
- DeepMotion API pricing.
- Whether Rokoko Vision or Plask expose an API.
- Any NVIDIA text-to-motion offering for 2026, and "MotionGPT-style" open models beyond HY-Motion. Not researched.
- No confirmation that ActorCore/AccuRIG has any API.

## How can assets be optimized for mobile (decimation, LOD, UV unwrap, baking, KTX2/Basis/ASTC, glTF/FBX pipelines), and where does Blender MCP fit as an agent-driven 3D workstation?

### Takeaway
A fully scriptable, free optimization stack exists:
1. Vendor remesh or face limits (Meshy Remesh, Tripo `face_limit`, Tencent Smart Topology and UV Unfold)
2. Blender headless with Python for cleanup, UV, baking, and retargeting
3. gltfpack/meshoptimizer or gltf-transform for quantization, mesh merging, LOD chains, and KTX2/BasisU textures

On the commercial side, **InstaLOD 2026** is free for indies under $100k revenue and has CLI batch "Pipeline". Simplygon's indie terms are unclear or dated.

**Blender MCP** (ahujasid, about 31.5k stars, MIT) turns a running Blender into an agent workstation. It provides:
- scene inspection
- visual `look` renders
- arbitrary Python execution
- Poly Haven, Sketchfab, and Poly Pizza imports
- `generate_3d` through Tripo, Hunyuan3D, Rodin, and Meshy

### Cited Findings

**Vendor-side optimization**
- Meshy Remesh offers quad or triangle topology, a 100–300k polycount target, adaptive decimation levels, and glb/fbx/obj/usdz/blend/stl/3mf export. UV Unwrap is a separate 5-credit endpoint — [Meshy Remesh API](https://docs.meshy.ai/en/api/remesh); [Meshy API Pricing](https://docs.meshy.ai/en/api/pricing)
- Tencent HY 3D offers Smart Topology (50 credits), UV Unfold (10), and Convert Format (5) — [Tencent Cloud billing doc](https://www.tencentcloud.com/document/product/1284/75281)
- Tripo P1 exposes `face_limit` (48–20k) and `export_uv` — [Tripo P1 docs](https://developers.tripo3d.com/en/models/p1). Its Quick Start suggests `face_limit` 5000 for mobile — [Tripo Quick Start](https://developers.tripo3d.com/en/docs/quick-start)
- TRELLIS.2's `to_glb` supports decimation targets, remeshing, texture size, and WebP. CuMesh handles remesh, decimation, and UV unwrap — [TRELLIS.2 GitHub](https://github.com/microsoft/TRELLIS.2)

**Open-source optimization tools**
- **gltfpack** — [gltfpack man page (Debian)](https://dyn.manpages.debian.org/trixie/gltfpack/gltfpack.1.en.html):
  - Reorders meshes for GPU efficiency
  - Quantizes geometry
  - Merges meshes to cut draw calls
  - Simplifies on request
  - Converts textures to **KTX2 with BasisU supercompression**
- A community 2026 pipeline guide recommends for mobile: meshopt geometry compression, KTX2 textures at 512–1024px, required LODs, and a gltf-transform simplify LOD chain at 1.0/0.5/0.25/0.10. It warns against going below about 10% of original triangles without visual checks — [anthemflynn asset-pipeline-3d skill](https://skills.sh/anthemflynn/ccmp/asset-pipeline-3d)
- The same guide warns against UASTC for diffuse maps on mobile (higher VRAM) in favor of ETC1S. This is a single source, unverified — [anthemflynn asset-pipeline-3d skill](https://skills.sh/anthemflynn/ccmp/asset-pipeline-3d)
- A meshoptimizer v1.0-based LOD tool exports LODs as separate glTF files. Its "permissive simplification" mode is experimental — [antzgames meshoptimizer tool](https://antzgames.itch.io/meshoptimizer)

**Commercial LOD tools**
- **InstaLOD 2026** (February 2026) is free for indie artists under $100k per year. Its Pipeline enables command-line and batch processing (unclear whether Pipeline is in the free tier). Plugins exist for Blender, Maya, 3ds Max, Unity, and Unreal — [CG Channel InstaLOD 2026](https://www.cgchannel.com/?p=174060)
- **Simplygon**: the only indie terms found are from 2016 (free for indies, 2% royalty above $25k per quarter), so they are likely outdated — [CGPress 2016](https://cgpress.org/archives/simplygon-launches-open-access-business-model.html). An aggregator lists commercial pricing at "30000 per year" (GetApp, updated March 2026) — [GetApp Simplygon](https://www.getapp.com/development-tools-software/a/simplygon/)

**Blender MCP**
- Repo details — [blender-mcp GitHub](https://github.com/ahujasid/blender-mcp):
  - The repo now appears as `ahujasid/mcp-for-blender`, MIT licensed
  - About 31.5k stars and 2.9k forks
  - Tools: `get_scene_info`, `look` (renders viewport, camera, multi-angle sheets, animation frames, wireframe), `execute_blender_code`, `search_assets`/`import_asset` (Poly Haven, Sketchfab, Poly Pizza), `generate_3d` (Tripo, Hunyuan3D, Hyper3D Rodin, Meshy)
  - Architecture: a Blender add-on socket server plus a Python MCP server talking JSON over TCP. Requires Blender 3.0+, Python 3.10+, and uv.
  - Clients: Claude Desktop/Code, Codex, Cursor, VS Code, OpenCode, Antigravity, and Windsurf
  - Security: arbitrary Python execution; the socket has no authentication or encryption (keep it on localhost); an optional safe mode blocks file, network, and process access; anonymous telemetry is on by default unless `DISABLE_TELEMETRY` is set
- Hyper3D credentials can be supplied via an environment variable for headless or CI use. A free trial key covers limited daily Rodin generations. Hunyuan3D SecretId/SecretKey are stored in add-on preferences — [Glama README mirror](https://glama.ai/mcp/servers/@ahujasid/blender-mcp/blob/7636d13bded82eca58eb93c3f4cd8708dfdfbe8b/README.md); [mcpservers.org](https://mcpservers.org/es/servers/ahujasid/blender-mcp)

### Inferences

**Recommended agent-driven mobile optimization chain** (synthesis from the above, not a vendor recipe)
1. Generate with a face cap: Tripo P1 at 1.5–5k faces for props or characters, or Meshy Remesh `target_polycount` with quad for characters to be rigged.
2. Bake high-to-low normals where available (Rodin "baked normals", Creator tier) or in Blender headless.
3. Downsize textures to 512–1024px, packing ORM (occlusion/roughness/metallic) into one texture to save samplers.
4. Generate LOD1–LOD3 with gltfpack or gltf-transform, or Blender Decimate.
5. Compress textures to KTX2: ETC1S for albedo, UASTC for normals is a common practice. Use meshopt geometry compression.
6. Import into the engine. Unity and Godot transcode Basis to ASTC or ETC2 on device.

**Unsourced background facts** (verify before relying on them): ASTC is the standard mobile GPU texture format, and Basis Universal transcodes to it. Blender runs headless with `blender -b --python`.

**Role of Blender MCP**
- It is best treated as the interactive "eyes and hands" for an agent: inspect, render previews to judge quality, fix normals and pivots, and retarget.
- Batch production should use plain headless Blender scripts or gltfpack CLIs, because the MCP socket design is single-session, unauthenticated, and GUI-bound.

### Gaps
- No official 2026 Khronos or meshoptimizer docs were fetched. Version-specific gltfpack flags are not cited.
- No benchmarks comparing AI-vendor remesh against Simplygon or InstaLOD quality.
- Current Simplygon indie licensing is unknown.
- Whether InstaLOD's free indie tier includes the CLI or API.
- No source found on automated ASTC block-size selection or on Unity/Godot mobile import presets for AI assets.

## Which AI texturing, material, skybox, and 3D world tools exist (Meshy, Polycam, Substance 3D, text-to-PBR, tileable textures, Blockade Labs, World Labs Marble)?

### Takeaway
Model-level PBR texturing is best handled inside the generators:
- Meshy Retexture: 10–15 credits, 2K/4K/8K
- Tencent Texture Edit: 30 credits
- TRELLIS.2 and Tripo P1: native PBR

Options for tileable PBR materials and environments:
- **Adobe Substance 3D Sampler 4.4**: text-to-texture (beta), but no public generation API found
- **3DAIStudio**: a seamless PBR generator
- **Material Maker**: open source
- **Blockade Labs Skybox AI**: full API only on the $140/seat Business tier
- **World Labs Marble**: has an API (`marble-1.1`), but no public pricing found

### Cited Findings
- **Meshy texturing**: Retexture costs 10 credits (2K/4K) or 15 (8K). Image-to-3D with 8K textures costs 35 — [Meshy API Pricing](https://docs.meshy.ai/en/api/pricing)
- **Tencent HY 3D**: 3D Texture Edit costs 30 credits and EnablePBR adds 10 — [Tencent Cloud billing doc](https://www.tencentcloud.com/document/product/1284/75281)
- **Adobe Substance 3D Sampler 4.4** has Text-to-texture, Text-to-pattern, and Image-to-texture (beta), plus a "Make it Tile" tool — [Adobe Sampler 4.4 release notes](https://helpx.adobe.com/substance-3d-sampler/release-notes/version-4-4---substance-3d-sampler.html). A comparison lists Sampler at $59.99/mo with a 30-day trial (secondary) — [Cinevva texture guide](https://app.cinevva.com/guides/ai-texture-generators)
- **3DAIStudio Seamless Texture Generator** produces tileable PBR sets (base color, normal, roughness, metalness, height) from text or image, at 10 credits per text generation — [3DAIStudio docs](https://docs.3daistudio.com/textures/seamless-texture)
- **Material Maker** is a free, offline, node-based procedural material tool with exports to Godot, Unity, and Unreal — [Cinevva texture guide](https://app.cinevva.com/guides/ai-texture-generators)
- **Blockade Labs Skybox AI** — [Blockade Labs plans](https://skybox.blockadelabs.com/plans):
  - $24/mo: 100 credits, limited API access
  - $60/mo: 300 credits
  - $140/mo: 500 credits, usage-based pricing, **full API**, 16K resolution, custom rate limits
  - All plans include full commercial licensing
- **World Labs Marble**: the API model IDs are `marble-1.1`, `marble-1.1-plus`, `marble-1.0`, and `marble-1.0-draft`. No public prices were found — [LLM Reference Marble](https://www.llmreference.com/model/marble)
- **Rodin** paid tiers include HDRI generation (8K) and "HD and custom texture" — [Hyper3D Pricing](https://hyper3d.ai/pricing)

### Inferences
- For mobile, skyboxes should be downscaled. 16K panoramas from Blockade must be cut to roughly 2K–4K cubemaps or equirects and compressed (my inference).
- Gaussian-splat or world-model outputs (Marble) are not directly mobile-friendly as geometry. They are more useful for concept work or baked backdrops (my inference; no source on Marble mesh export quality).
- Tileable materials for environments (ground, walls) plus low-poly modular meshes is likely more mobile-efficient than per-asset unique 4K textures (inference).

### Gaps
- Polycam AI texturing features in 2026 were not researched.
- Whether Adobe exposes Substance generative features via the Firefly or Substance APIs.
- World Labs Marble pricing and export formats (mesh vs splat).
- Genie-style world models (Google Genie 3, etc.) and HunyuanWorld for game-ready mesh export were not researched. HunyuanWorld-1.0 is listed as open source — [ToolNavs](https://toolnavs.com/en/article/823-hunyuan-3d-engine-global-eingef%C3%BChrt-eine-ki-3d-engine-f%C3%BCr-kreative-menschen-welt)

## What AI tools exist for VFX and shaders (particle effects, LLM-written HLSL/GLSL/Shader Graph, VFX libraries), and what works for mobile performance?

### Takeaway
No dedicated, production-grade "AI VFX generator" API for game particle systems was found as of October 2026. The workable approach is:
- LLMs write shader code (HLSL/GLSL/Godot shader language) or drive the engine via Unity or Blender MCP
- Image models produce flipbook and sprite textures

Practitioner accounts say LLMs handle known effect patterns well but are weak at multi-pass effects, optimization, and novel looks. Mobile performance therefore needs human or automated profiling.

### Cited Findings
- **Keijiro Takahashi's "AI Shader"** is a proof-of-concept that generates Unity shaders from text prompts via ChatGPT (English or Japanese). It produces code, not Shader Graph nodes — [80.lv](https://80.lv/articles/ai-shader-a-chatgpt-powered-shader-generator-for-unity). An early reaction called it "not particularly accurate" — [Appuals](https://appuals.com/chatgpt-unity-shaders/)
- A January 2025 experiment turned text into Shader Graph node structures. The implementation is not public — [Medium, Design Bootcamp](https://medium.com/design-bootcamp/exploring-ai-integration-in-node-based-shaders-5d127fd3cbff)
- A 2026 practitioner account (anecdotal, web-graphics focus) says AI handles known effect patterns well, while complex multi-pass effects, shader optimization, and novel artistic effects remain weak — [Svilenkovic AI shader generation](https://svilenkovic.com/3d/ai-shader-generation)
- Unity MCP servers let agents operate the Unity Editor (and therefore author materials, shaders, and VFX). Options include **IvanMurzak/Unity-MCP** (about 2,979 stars, "AI Skills, MCP Tools, and CLI for Unity Engine") and **MCP Unity** — [Agentpedia Unity MCP](https://agentpedia.codes/mcp/unity-mcp-ai-game-developer); [Agentpedia Unity integration](https://agentpedia.codes/mcp/unity-integration-advanced)
- Blender MCP's `execute_blender_code` and `look` render tools can be used to build and preview procedural materials or effects in Blender — [blender-mcp GitHub](https://github.com/ahujasid/blender-mcp)

### Inferences
**Mobile-safe guidance** (inferences and common practice, not sourced in this session)
- Prefer single-pass, unlit or simple-lit URP shaders.
- Use flipbook (sprite-sheet) particles with additive or alpha-blended materials, and minimize overdraw and transparent layers.
- Avoid VFX Graph on low-end mobile, since it requires compute-shader support; the CPU-based Particle System (Shuriken) is the safer choice.
- Use half precision in shaders.
- An agent can generate flipbook textures with image models and pack them into atlases.

**Agent loop for VFX**: LLM writes the shader or particle config → applied via Unity or Godot MCP → screenshot or profiler capture → iterate. Quality checks need rendered previews, because LLMs cannot judge aesthetics from code alone.

### Gaps
- No 2026 source on AI tools for Unity VFX Graph or Niagara particle generation.
- No source on dedicated AI VFX asset generators (for example, flipbook/sprite-sheet generators with APIs).
- No source benchmarking mobile performance of LLM-written shaders.
- Unity's own first-party AI (Unity AI / Muse successors) features for shaders or VFX in 2026 were not researched.
- Licensing of VFX asset libraries was not researched.

## What are the licensing and commercial terms, including IP indemnification, for each tool?

### Takeaway
Paid tiers of Meshy, Tripo, Rodin, and Blockade grant private, commercial ownership of outputs. Free tiers differ:
- Meshy Free is CC BY 4.0 (commercial use with attribution).
- Tripo Free is contradictory: its help center says Tripo retains rights, while its blogs say CC BY 4.0.

Open-weight models:
- TRELLIS.2: MIT, the cleanest terms.
- SPAR3D: free under $1M revenue.
- SAM 3D: custom license.
- Hunyuan3D 2.x: excludes the EU, UK, and South Korea entirely, and Omni requires a license above 1M MAU.

No vendor IP-indemnification terms were found for any of these 3D tools.

### Cited Findings
- **Meshy**: Free is CC BY 4.0 (commercial use with attribution). Pro and above are private and customer-owned — [Meshy Pricing](https://www.meshy.ai/pricing); [Meshy pricing docs](https://docs.meshy.ai/pricing). Private ownership without attribution requires a paid plan, and rights to models made while subscribed persist after a downgrade — [Meshy Help Center](https://intercom.help/meshy/en/articles/16102098-can-i-use-meshy-assets-commercially)
- **Tripo**:
  - The help center says Tripo retains all rights to free-user inputs and outputs (ToS §5.2.1), while paid users own their outputs — [Tripo Help](https://www.tripo3d.ai/help/privacy-policy/how-to-use-tripo-models-commercially)
  - Tripo blog posts say free outputs are CC BY 4.0, which is contradictory — [Tripo blog](https://www.tripo3d.ai/blog/commercial-use-ai-3d-models)
- **Hyper3D Rodin**: paid plans include "broader export and usage rights". Business adds a ChatAvatar commercial license. Free-plan terms are not specified on the pricing page — [Hyper3D Pricing](https://hyper3d.ai/pricing)
- **Blockade Labs**: all plans include full commercial licensing — [Blockade Labs plans](https://skybox.blockadelabs.com/plans)
- **Hunyuan3D 2.0 / 2.1 Community License**: the Territory is worldwide **excluding the EU, UK, and South Korea** — [Hunyuan3D-2 LICENSE (HF)](https://huggingface.co/tencent/Hunyuan3D-2/blob/main/LICENSE)
- **Hunyuan3D-Omni**: the same exclusions apply, and a license is required above 1M MAU (secondary summary) — [DeepWiki Hunyuan3D-Omni licensing](https://deepwiki.com/Tencent-Hunyuan/Hunyuan3D-Omni/6.1-licensing-and-legal)
- **TRELLIS.2**: MIT for model and code. Dependencies (nvdiffrast, nvdiffrec) carry their own licenses — [TRELLIS.2 GitHub](https://github.com/microsoft/TRELLIS.2)
- **Stability SPAR3D**: Community License, free for commercial use under $1M annual revenue — [AlternativeTo](https://alternativeto.net/news/2025/1/stability-ai-unveils-stable-point-aware-3d-for-real-time-3d-object-creation-from-images)
- **Meta SAM 3D Objects**: custom SAM license with restrictions such as a military-use ban. Review before commercial use — [Roboflow](https://roboflow.com/model/sam-3d-objects)
- **Mocap tools**: DeepMotion's free plan is personal or non-commercial only — [Neolemon guide](https://www.neolemon.com/blog/best-ai-motion-capture-tools-for-character-animation)
- **Animation libraries**: the Quaternius Universal Animation Library is CC0 — [Cinevva Mixamo guide](https://app.cinevva.com/guides/free-character-animations-rigging)
- **Blender MCP**: MIT — [blender-mcp GitHub](https://github.com/ahujasid/blender-mcp)

### Inferences
- A commercial mobile game shipped globally (including the EU and UK app stores) should avoid self-hosted Hunyuan3D 2.x weights. The territorial exclusion plausibly covers distribution or use there (legal review needed).
- Tencent Cloud API-generated outputs fall under Tencent Cloud's service terms rather than the community license. These were not reviewed.
- TRELLIS.2 (MIT) is the lowest-risk open model for a commercial pipeline.
- The agent pipeline should always run on paid tiers to avoid attribution or ownership ambiguity (Meshy CC BY; Tripo's free-tier contradiction).
- No vendor offered IP indemnification in what was found. This is a gap to flag for publishers, since AI-generated 3D assets also face copyright-registrability questions.

### Gaps
- No IP indemnification terms were found for Meshy, Tripo, Rodin, Tencent HY 3D, Uthana, Blockade, or World Labs.
- Tencent Cloud HY 3D output-ownership terms.
- Uthana output licensing.
- Move.ai output licensing.
- World Labs Marble terms.
- Mixamo's terms for use in commercial games (background knowledge: historically royalty-free, but not verified for 2026).

## Which MCP servers exist for these 3D tools (Blender MCP, Meshy, Tripo, Hunyuan3D, Rodin, etc.), with GitHub links and maturity?

### Takeaway
The most mature options are:
- **ahujasid/blender-mcp**: about 31.5k stars, MIT, multi-vendor `generate_3d`
- **Meshy's official MCP server** (`@meshy-ai/meshy-mcp-server`): about 20–24 tools covering generate, retexture, rig, and animate; needs a Pro+ API key

Less mature options:
- **VAST-AI-Research/tripo-mcp**: official but alpha and Blender-coupled
- **DeemosTech Rodin MCP**: official
- Small community multi-provider servers such as trident-mcp
- Unity MCP servers (for example IvanMurzak/Unity-MCP) for engine-side work

No dedicated, confirmed Hunyuan3D MCP repo was found. Hunyuan3D is reachable via Blender MCP.

### Cited Findings
- **Blender MCP** — [GitHub ahujasid/blender-mcp](https://github.com/ahujasid/blender-mcp):
  - About 31.5k stars, 2.9k forks, 246 commits, MIT
  - Integrates Tripo, Hunyuan3D, Hyper3D Rodin, and Meshy via `generate_3d`, plus Poly Haven, Sketchfab, and Poly Pizza
  - Has safe mode and opt-in telemetry
- Directory pages show inconsistent versions (1.4.0 release notes call Hunyuan3D "newest", while others list v1.5.5) and a "last updated January 21, 2026" date — [Glama README mirror](https://glama.ai/mcp/servers/@ahujasid/blender-mcp/blob/7636d13bded82eca58eb93c3f4cd8708dfdfbe8b/README.md); [mcpservers.org](https://mcpservers.org/es/servers/ahujasid/blender-mcp)
- **Meshy MCP (official)**:
  - Repo `meshy-dev/meshy-mcp-server`; install with `npx add-mcp @meshy-ai/meshy-mcp-server` using `MESHY_API_KEY` — [Meshy AI Integration docs](https://docs.meshy.ai/en/api/ai)
  - Tools cover text-to-3D, image-to-3D, multi-image, retexture, rigging, and animation. Tool count is listed as 20 and 24 in different snapshots — [Glama meshy-mcp-server](https://glama.ai/mcp/servers/meshy-dev/meshy-mcp-server); [Glama](https://glama.ai/mcp/servers/apdm4ty7gp)
  - The API key requires Pro or above — [Meshy MCP page](https://www.meshy.ai/mcp)
- **Tripo MCP (official, alpha)**: generates from text and imports into Blender via Tripo's Blender add-on. Runs with `uvx tripo-mcp` in Claude Desktop or Cursor — [GitHub VAST-AI-Research/tripo-mcp](https://github.com/VAST-AI-Research/tripo-mcp)
- **Community Tripo MCPs**: `lxy2109/tripo-mcp` (Python) — [Glama lxy2109/tripo-mcp](https://glama.ai/mcp/servers/lxy2109/tripo-mcp); a Node server for Tripo plus Leonardo.Ai — [Glama](https://glama.ai/mcp/servers/w4hhs2rql1)
- **trident-mcp** (`mordor-forge/trident-mcp`): Go, wraps Tripo, Meshy, and Rodin with retopology and format conversion. About 3 stars, so immature — [Enterprise DNA](https://enterprisedna.co/directories/mcp/mordor-forge-trident-mcp)
- **Rodin MCP**: listed as official, created and maintained by DeemosTech — [Agentpedia Rodin](https://agentpedia.codes/mcp/rodin)
- **Hunyuan3D MCP**: mcp.so lists one server tagged #hunyuan3d without naming a confirmed repo — [mcp.so hunyuan3d tag](https://mcp.so/tags/hunyuan3d)
- **Unity MCP**: IvanMurzak/Unity-MCP (about 2,979 stars), MCP Unity, and a Docker image `ivanmurzakdev/unity-mcp-server` (review the source before use) — [Agentpedia Unity MCP](https://agentpedia.codes/mcp/unity-mcp-ai-game-developer)

### Inferences

**Proposed agent-driven pipeline** (synthesis)
1. **Concept**: an image model produces a front or three-quarter reference, or multiview images.
2. **Generate**: Tripo P1 (`face_limit` about 1.5–5k, PBR) for props and characters. Alternatively Meshy-6/7.1, then Remesh (quad, target polycount), then UV Unwrap. Use Rodin Gen-2.5 Quad for hero characters. Use self-hosted TRELLIS.2 for bulk props.
3. **Rig and animate**: Tripo rig-check → rig (Mixamo spec) → retarget (in-place). Alternatively Meshy Rigging → Animation. Add bespoke clips via Uthana TTM API, Meshy TTM, or HY-Motion, retargeted in Blender.
4. **Optimize**: headless Blender for cleanup, normal baking, and ORM packing. Then gltfpack/gltf-transform for LOD chain, meshopt, and KTX2 (ETC1S/UASTC). Export GLB, or FBX for Unity.
5. **Quality control**: render turntables with the Blender MCP `look` tool and have a vision model score them. Check triangle counts and texture memory budgets automatically.
6. **Engine import**: via Unity MCP or Godot tooling.
7. **Sky, environment, and VFX**: Blockade Skybox API (Business tier), tileable PBR from 3DAIStudio or Material Maker, and LLM-written mobile shaders verified in-engine.

**MCP choice**
- The Meshy MCP is the most "complete" vendor MCP. Blender MCP is the best general workstation.
- For production reliability, call vendor REST APIs directly from scripts. They are async and poll-based with credit refunds on failure.
- Use MCPs for interactive or agent-exploratory steps.

### Gaps
- GitHub star counts and last-commit dates for meshy-mcp-server, tripo-mcp, and the Rodin MCP were not verified.
- No confirmed Hunyuan3D-specific MCP repo.
- No MCP servers found for Uthana, Blockade Labs, World Labs, DeepMotion, gltfpack, or InstaLOD.
- No maturity or security audits of these MCPs found beyond Blender MCP's own warnings.
- Godot MCP servers were not researched.
