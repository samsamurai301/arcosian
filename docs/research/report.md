# Verified Loops, Not Prompts, Ship Mobile Games

The way to build a world-class automatic mobile-game plugin for Claude Code in October 2026 is to make it an **orchestration and verification layer on top of free engine bridges**, not another prompt-to-game generator. Use **Godot 4.7 with typed GDScript for 2D and casual titles** and **Unity 6.3 LTS with URP for 3D-heavy ones**, drive both headlessly through their CLIs and pinned MCP servers, and send every asset class through one budgeted, provenance-logging gateway. In that gateway, Nano Banana 2.1 and GPT Image 2.5 cover 2D, Tripo P1 and Meshy cover 3D, and ElevenLabs covers music, SFX and voice. No feature counts as done until headless play tests, device performance budgets and a vision-model critic all pass. That aims at the real bottleneck. The strongest agent scores only **41.46%** on GameCraft-Bench's 140 Godot game tasks ([arXiv](https://arxiv.org/abs/2606.17861)), and the best QA agent finds **48%** of known bugs ([arXiv](https://arxiv.org/abs/2604.02648)). Generating content is cheap; verified playability is scarce. It also aims at the clearest market gap. Well-funded rivals host web games inside their own feeds, Astrocade for example ($56M raised, about 5M MAU, web-only) ([Fortune](https://www.fortune.com/2026/05/05/astrocade-raises-56-million-series-b-sequoia-video-games-platform-ali-amir-sadeghian/)). The largest open-source Claude Code game kits ship no iOS, Android, monetization or store skills ([GitHub](https://github.com/gamedev-skills/awesome-gamedev-agent-skills)). Nobody takes a brief all the way to a native, store-ready game that the user owns. Per-asset API costs are small: by my arithmetic, all the art and audio for a 2D casual game costs roughly $60–100 at list prices. The larger costs are model tokens, subscriptions, macOS build minutes and device farms. The main risks are licensing traps inside revenue thresholds and free tiers, store requirements that kept changing through 2026, vendor churn, and player stigma toward visible AI content. "Automatic" should therefore mean automatic between a few human checkpoints for taste and for irreversible actions. Build in four phases, starting with a Godot 2D vertical slice that reaches TestFlight and Play internal testing.

## Nobody ships owned native mobile games, and agent quality tops out near 41%

The prompt-to-game category is well funded, but it is aimed at the wrong target. **Astrocade** raised $56M across rounds led by Sea and Sequoia and reports about 5M MAU and 140M plays per month, but it is a website with no iOS or Android app ([Fortune](https://www.fortune.com/2026/05/05/astrocade-raises-56-million-series-b-sequoia-video-games-platform-ali-amir-sadeghian/)), and a competitor's review notes it offers no code export or file you own ([Cinevva, vendor](https://app.cinevva.com/guides/ai-game-generators-2026)). **Aippy** reached a **$250M post-money valuation** with about 2M MAU and markets "one-click error repair" ([36Kr](https://eu.36kr.com/en/p/3834400181741440)). **Rosebud** generates Phaser and Three.js browser games, and gates code download and Windows export behind a $50/month plan, with no mobile export at all ([Rosebud pricing](https://rosebud.ai/pricing)). These companies make money from the feed and the remix network, not from exported games. They have little reason to help users ship standalone store apps and keep the revenue.

The closest native-mobile options are compromises. GDevelop's AI agent writes into an editable project that exports to Android and iOS, and Buildbox targets hyper-casual with engine lock-in ([Cinevva, vendor](https://app.cinevva.com/guides/ai-game-generators-2026)). General app builders such as Rork and a0.dev produce React Native or SwiftUI apps. One reviewer says Rork's output "requires substantial engineering work to reach App Store review standards" ([Rork review](https://www.rapidevelopers.com/blog/rork-ai-review)). Summer Engine, a Godot-compatible "AI game studio," lists only Windows and macOS export on its own page ([Summer Engine](https://www.summerengine.com/ai-game-studio)).

Meanwhile, the engine vendors have made "Claude Code drives the editor" a first-party pattern. **Unity ships a free official plugin** that adds engineering skills, including **IAP, LevelPlay** and localization, plus its CLI and MCP server to Claude Code ([Unity AI](https://unity.com/ai)). **Epic ships an official MIT-licensed "Unreal Engine Skills for Claude Code" plugin** that exposes hundreds of tools across 30+ toolsets ([GitHub](https://github.com/EpicGames/unreal-engine-skills-for-claude-code-plugin)). Third-party assistants compete on closed-loop checking: Bezi added an Agent mode that edits, plays and verifies inside Unity Play Mode ([Bezi](https://www.bezi.com/)). Two things follow. A new plugin should not build its own engine bridges. And basic monetization snippets are already commoditized inside Unity.

The open-source Claude Code ecosystem is broad but has nothing for shipping mobile games. **Claude-Code-Game-Studios** (about 26.8k stars) models a 49-agent studio hierarchy. Its own author reports that a "standard" rigor build, which wrote 30 documents before any code, **ranked last** against a minimal-process build in blind review. The sample was small: one brief and four games ([GitHub](https://github.com/donchitos/claude-code-game-studios)). **awesome-gamedev-agent-skills** has 74 skills and none for iOS/Android builds, monetization or store submission ([GitHub](https://github.com/gamedev-skills/awesome-gamedev-agent-skills)). **Godogen** (7,158 stars) builds games autonomously for Godot, Bevy, Babylon.js and three.js and "proves the result" with recorded video, but it does not support Unity or Unreal ([GitHub](https://github.com/htdt/godogen)).

The research shows where the ceiling is. On GameCraft-Bench's 140 Godot tasks, agents "implement recognizable mechanics but struggle to deliver complete games with enough content, functional visual feedback, and coherent presentation" ([arXiv](https://arxiv.org/abs/2606.17861)).

The market punishes volume without quality. Steam passed **21,388 releases by October 16, 2026**, and Kotaku blames part of the flood on vibe-coded clones ([Kotaku](https://kotaku.com/steam-valve-slop-ai-genai-vibe-coding-pc-game-releases-2000746749)). AI-flagged games were **33% of Q2 2026 releases but only 10% of sales** ([GamesRadar](https://www.gamesradar.com/games/steam-study-of-over-53-000-games-finds-60-90-percent-of-the-growth-in-monthly-releases-on-valves-store-is-from-games-using-ai-and-almost-none-of-them-make-money/)). Games that disclose AI use get about **53% fewer reviews** ([Recognizing Patterns](https://recognizingpatterns.substack.com/p/use-ai-to-build-your-game-just-keep)). **52%** of GDC 2026 survey respondents say generative AI is harming the industry ([GDC](https://gdconf.com/article/gdc-2026-state-of-the-game-industry-reveals-impact-of-layoffs-generative-ai-and-more/)).

Mobile itself is flat. In 2025, game IAP grew 1% to about $82B ([Sensor Tower](https://sensortower.com/press/press-release-sensor-tower-state-of-gaming-gaming-drove-52-billion-downloads-82b-iap-revenue-on-mobile-and-12b-premium-revenue-on-steam)). In H1 2026, IAP fell 2% and downloads fell 12%, while **hybrid-casual spending grew 17.1%** in 2025 ([Mobilegamer.biz](https://mobilegamer.biz/data-digest-sensor-towers-h1-analysis-hay-days-comeback-julys-top-games-big-krafton-numbers-and-more/)). Sett raised a $30M Series B to sell AI-generated playable ads and mini-games to mobile studios ([SiliconANGLE](https://siliconangle.com/2026/03/30/sett-raises-30m-grow-agent-based-ai-platform-game-studios/)), which shows a B2B wedge also exists.

The defensible position follows from all this. Promise owned, verified, store-ready games. Keep AI behind the scenes. Focus on hybrid-casual and puzzle genres, where automated players already work.

## Godot leads for 2D, Unity for 3D, and the bridges already exist

### Godot 4.7: text-native, headless, free

**Godot 4.7.2** is the best default because everything is text and everything runs headless. Scenes, resources, the input map and export presets are all plain text. `--headless --export-release` builds from `export_presets.cfg`, `--check-only` parses scripts for errors, and `--write-movie` forces fixed-FPS capture for deterministic video evidence ([Godot docs](https://docs.godotengine.org/en/stable/tutorials/editor/command_line_tutorial.html)). One practitioner calls a 10-line `.tscn` "the entire scene," while reading Unity's GUID-heavy YAML is "essentially reading a database dump" ([dev.to](https://dev.to/mistyhx/why-ai-writes-better-game-code-in-godot-than-in-unity-10hf)). The license is MIT.

Mobile maturity has improved sharply:

- Foundation contractors cut crash rates for two shipped titles from about **4% to under 1%** ([Godot](https://godotengine.org/article/godot-mobile-update-apr-2026/)).
- Godot 4.6 added Android instrumented tests on Firebase Test Lab (same source).
- The Foundation maintains plugins for **Google Play Billing, Play Games Services and StoreKit 2** (same source).
- AppLovin publishes an official MAX plugin ([AppLovin](https://developers.applovin.com/en/max/godot/overview/integration)).

There are three weaknesses to design around. First, C# on Android and iOS is still "experimental" in the 4.7 docs, so mobile projects should use statically typed GDScript ([Godot 4.7 C# docs](https://docs.godotengine.org/en/4.7/tutorials/scripting/c_sharp/index.html)). Second, LLMs invent placeholder resource UIDs and slip Python idioms into GDScript. Practitioners fix this with a duplicate-UID linter and by generating IDs with `uuidgen` ([Hacker News](https://news.ycombinator.com/item?id=47146712)). Third, Godot lags on high-end 3D ([Ocean View Games](https://oceanviewgames.co.uk/blog/posts/unity-vs-godot-vs-unreal-mobile-games)). Sources disagree on which renderer is the mobile default: Ocean View says Compatibility, while Godot's own 4.7 notes describe an improved dedicated Mobile renderer ([Godot 4.7](https://godotengine.org/releases/4.7/)).

Godot has no official MCP server, and the plugin does not need many MCP tools. File edits handle scene construction. The MCP is needed for runtime verification, and two community servers are built for exactly that:

- **satelliteoflove/godot-mcp** freezes the game clock, steps exact time slices or until a condition holds, injects real input, returns live entity state as JSON, and splits read tools from write tools so reads can be auto-allowed ([GitHub](https://github.com/satelliteoflove/godot-mcp)).
- **tugcantopaloglu/godot-mcp** has 157 tools, including headless `validate_scripts`, `export_project` and simulated touch through `game_touch` ([GitHub](https://github.com/tugcantopaloglu/godot-mcp)).

The most-starred server, Coding-Solo/godot-mcp (6,148 stars), has had no pushes since April 2026 ([GitHub](https://github.com/Coding-Solo/godot-mcp)). A vendor roundup also reports a command-injection CVE in it, since fixed ([Summer Engine](https://www.summerengine.com/blog/best-godot-mcp-server)). Pin it with care or avoid it.

### Unity 6.3 LTS: the mobile 3D standard, with a moving AI story

**Unity 6.3 LTS with URP** has the highest ceiling for 3D mobile games that look impressive and can still ship:

- Unity 6.5 added On-Tile Post Processing on Vulkan and Metal.
- ThinLTO plus Master IL2CPP gives about a 5% average gain in startup, scene load and CPU frame time on Android.

([Unity Discussions](https://discussions.unity.com/t/unity-6-5-is-now-available/1723176)). Unity also has first-party ads and IAP packages, and agents write C# reliably.

Unity's official agent tooling changed twice in four months. The in-editor MCP server launched in May 2026 behind a Unity AI subscription ([Unity blog](https://unity.com/blog/unity-ai-mcp-how-to-get-started)). Around August it was deprecated in favor of a **free Unity CLI**. Its `unity command` and `unity eval` "drive the Editor directly, without MCP in between… faster and use fewer tokens than MCP," and it runs headless builds and test suites ([Unity docs](https://docs.unity.com/en-us/unity-cli/replace-mcp-server-unity-cli)). For play-mode control and screenshots, **CoplayDev/unity-mcp** (15,088 stars, v10.3.0 on October 4, 2026) is the dominant bridge, with Roslyn script validation ([GitHub](https://github.com/CoplayDev/unity-mcp)).

Unity's main agent friction is its scene format. Agents should never hand-write scene YAML. They should build scenes and prefabs procedurally through editor scripts run via `unity eval` or `-executeMethod` ([Unity Manual](https://docs.unity3d.com/Manual/EditorCommandLineArguments.html)).

Licensing has no runtime fee. Personal is free under $200K of revenue and funding, and Pro costs **$2,310 per seat per year** from January 12, 2026 ([Unity pricing](https://unity.com/products/pricing-updates)). Unity 6.0 LTS support ends in October 2026, so target 6.3 LTS and plan for 6.7 LTS ([Unity](https://unity.com/unity-6-release)).

### Unreal, Defold and web stacks: niche roles only

**Unreal is a poor fit for an automated mobile plugin.** Minimal builds run 150–300 MB, and Lumen and Nanite do not run on mobile ([Ocean View Games](https://oceanviewgames.co.uk/blog/posts/unity-vs-godot-vs-unreal-mobile-games)). The UE 5.8 MCP plugin is experimental, localhost-only, unauthenticated, and runs tool calls serially on the game thread ([VP Land](https://www.vp-land.com/stories/unreal-engine-5-8-embeds-an-mcp-server-so-ai-agents-can-drive-the-editor)).

**Defold** makes the smallest builds and has official MAX, LevelPlay and AdMob extensions ([GameDev.net](https://gamedev.net/news/5363-defold-summer-newsletter-2026/)). Its MCP has 13 stars, and its scripting language is Lua ([GitHub](https://github.com/Fulviuus/defold-mcp)).

**Web stacks** (Phaser 4, PixiJS 8, three.js plus Capacitor) suit playable ads and web portals. WebGPU now works on iOS 26+ ([Cinevva](https://app.cinevva.com/guides/webgpu-vs-webgl-games)).

| Engine | Agent fit | Headless mobile build | Mobile visual ceiling | Monetization SDKs | License | Role in plugin |
|---|---|---|---|---|---|---|
| Godot 4.7.2 | Best: text scenes, self-verifying MCPs | `--headless --export-release`; iOS needs macOS | Strong 2D, mid-tier 3D | Foundation billing/StoreKit 2, official MAX | MIT | Default and 2D/casual |
| Unity 6.3 LTS | Good: C#, free CLI, 15k-star MCP; YAML friction | batchmode/Unity CLI; license activation; macOS for iOS | Highest for mobile 3D | First-party ads/IAP | Free under $200K; Pro $2,310/yr | 3D-heavy titles |
| Unreal 5.8 | Experimental MCP, binary assets | UAT, heavy | High raw, no Lumen/Nanite on mobile | Good | 5% above $1M | Not recommended |
| Defold 1.14 | Lua, tiny MCP | bob.jar, headless | Strong 2D | Official MAX/LevelPlay/AdMob | Free | Ultra-light hyper-casual option |
| Web + Capacitor | Browser verification | Vite + Capacitor | WebView-bound | Plugins | MIT/Apache | Playable ads, web portals |

## Route each asset class to a specialist and lock the style before scaling volume

### 2D art and UI: a cheap workhorse, a premium hero model, a vector specialist

On the Artificial Analysis text-to-image arena, **GPT Image 2.5 Sunburst ranks first at $210.7 per 1,000 images**, and **Nano Banana 2.1 ranks fourth at $33.6 per 1,000** ([Artificial Analysis](https://artificialanalysis.ai/image/leaderboard/text-to-image)). Through the Gemini API, Nano Banana 2.1 costs **$0.0336 per 1K image and $0.0168 in batch** ([Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing)). At 1,000 assets with three candidates each, that is about $50, against about $630 for GPT Image 2.5 at max quality. That makes Nano Banana the bulk workhorse.

Reserve GPT Image 2.5 for key art, store screenshots and text-heavy UI mockups. Its Sunburst variant is positioned for "tighter control across edits" ([Grida](https://grida.co/docs/models/gpt-image-2.5)). Transparent-background support on gpt-image-2 is contested, so do not depend on it ([OpenAI Community](https://community.openai.com/t/is-transparent-background-support-broken-in-gpt-image-2/1402707)).

**Recraft V4.1 Vector** costs about $0.08 per image and is the specialist for icons and UI. Background removal and vectorization cost about $0.01 each, and outputs are owned only on paid plans ([Recraft](https://www.recraft.ai/pricing?tab=api)). Midjourney has no official API, and its terms ban automated access. It cannot be part of a compliant pipeline ([Unifically](https://unifically.com/blogs/midjourney-api)).

Game-specialized platforms add what general models lack:

- **Scenario** offers custom LoRA training and composition, a hub of third-party models, and an official MCP server with 17–19 tools ([Scenario](https://help.scenario.com/en/articles/getting-started-with-the-scenario-mcp-server)).
- **PixelLab** is the pixel-art specialist. It makes 4- and 8-direction characters with walk, run, idle and attack animations, plus Wang and dual-grid tilesets. Its official MCP is at `api.pixellab.ai/mcp`, and commercial use is allowed ([PixelLab](https://www.pixellab.ai/llms-full.txt)).
- **Retro Diffusion** sells pay-per-image pixel art from $0.015 to $0.18 ([mcpservers.org](https://mcpservers.org/servers/retro-diffusion/retro-diffusion-mcp)).
- **Ludo.ai** turns static characters into sprite sheets through its API and MCP, available on select plans ([Ludo](https://ludo.ai/docs/api-mcp)).
- **ComfyUI** has shipped official MCPs for Comfy Cloud (June 2026) and local servers (August 2026). It is the right layer when the plugin needs repeatable open-weight graphs ([ComfyUI Wiki](https://comfyui-wiki.com/en/news/2026-08-11-comfy-mcp-local-server)).

Consistency across hundreds of assets takes a staged recipe:

1. Approve a character "bible" sheet.
2. Generate variants through multi-reference edits. Nano Banana 2 accepts up to 14 references but is reliable only for one or two characters ([Zilliz](https://zilliz.com/ai-faq/how-many-consistent-characters-can-nano-banana-2-maintain-across-a-workflow)).
3. Once 20–50 images are approved, train a LoRA. On fal, a FLUX.2 [klein] 4B LoRA costs about $9.71 per 1,000 steps and a FLUX.2 [dev] edit LoRA about $47 ([fal](https://fal.ai/models/fal-ai/flux-2-klein-4b-base-trainer/edit)).
4. Enforce palette and canvas rules in post.

For self-hosting, prefer Apache-licensed weights such as Qwen-Image and FLUX.2 [klein] 4B. FLUX.2 [dev] and the BRIA RMBG 2.0 background remover are non-commercial unless licensed ([InVideo](https://invideo.io/blog/open-source-image-models-licenses/); [GitHub](https://github.com/Bria-AI/RMBG-2.0)).

The post-processing chain ends in TexturePacker's CLI. It packs atlases and outputs ASTC, ETC2 and KTX2/Basis, and it offers a CI/Docker license ([TexturePacker](https://www.codeandweb.com/texturepacker/documentation/commandline)). No vendor offers automated skeletal rigging for Spine or Live2D. The only AI option is a community skill under a non-commercial license ([GitHub](https://github.com/GenielabsOpenSource/spine-animation-ai)). For now, frame-based sprite sheets are the automatable path.

### 3D models: cap faces at generation, clean up in Blender, compress with gltfpack

The leading 3D generators each fit a different job:

- **Tripo P1** is built for mobile low-poly. `face_limit` runs from 48 to 20,000, a base mesh takes about 10 seconds, and a textured model about 60. P1 does not output quads ([Tripo](https://developers.tripo3d.com/en/models/p1)). Tripo's quick start recommends 5,000 faces for mobile ([Tripo](https://developers.tripo3d.com/en/docs/quick-start)).
- **Meshy** is the only vendor with one documented API that covers generation, quad or triangle remesh (100–300k), UV, rigging, an animation library and text-to-motion ([Meshy](https://docs.meshy.ai/en/api/pricing)). By my arithmetic, a rigged, animated asset costs about 49 credits, or **€0.58–0.93**, on the €95 Ultra or €19 Pro plans ([Meshy pricing](https://www.meshy.ai/pricing)). Note that Meshy's `lowpoly` mode retires on **October 30, 2026**.
- **Rodin Gen-2.5** produces 4K–50K-face quad meshes suited to rigged hero characters ([Scenario](https://help.scenario.com/articles/3791851266-rodin-hyper3d-gen-2-5-models-the-essentials)), but the API comes only with the $120/month Business plan ([Hyper3D](https://hyper3d.ai/pricing)).
- **Tencent HY 3D** is cheapest, at $0.015 per credit and 30 credits for LowPoly ([Tencent Cloud](https://www.tencentcloud.com/document/product/1284/75281)).
- **TRELLIS.2** (MIT, 4B parameters, 24GB+ GPU) is the clean self-host option ([GitHub](https://github.com/microsoft/TRELLIS.2)).

Avoid self-hosted Hunyuan3D 2.x weights for global launches. Their license excludes the EU, UK and South Korea ([Hugging Face](https://huggingface.co/tencent/Hunyuan3D-2/blob/main/LICENSE)). No independent quality ranking across these generators was found, so the plugin should run its own blind comparisons.

After generation comes a free, scriptable optimization chain. Headless Blender handles cleanup, normal baking and retargeting. gltfpack handles quantization, mesh merging and KTX2/BasisU textures ([gltfpack](https://dyn.manpages.debian.org/trixie/gltfpack/gltfpack.1.en.html)). A community guide recommends 512–1024 px textures and an LOD chain at 1.0/0.5/0.25/0.10 for mobile ([skills.sh](https://skills.sh/anthemflynn/ccmp/asset-pipeline-3d)).

**Blender MCP** (about 31.5k stars, MIT) works well as the agent's eyes and hands. It renders `look` previews for a vision critic and can call Tripo, Hunyuan3D, Rodin and Meshy. However, it runs arbitrary Python over an unauthenticated socket, and telemetry is on by default ([GitHub](https://github.com/ahujasid/blender-mcp)). Keep it on localhost and use plain scripts for batch work. Meshy's official MCP needs a Pro key ([Meshy](https://www.meshy.ai/mcp)). For production, call vendor REST APIs directly: they are async and refund credits on failure.

For environments, Blockade Labs' Skybox API needs the $140/month Business tier and outputs 16K panoramas that must be downscaled ([Blockade Labs](https://skybox.blockadelabs.com/plans)). Meshy's $400M Series B at a $1.5B valuation ([Crunchbase News](https://news.crunchbase.com/venture/2026-global-gaming-startup-funding-up-ai-meshy-decart/)) makes it the lowest vendor-survival risk among 3D APIs.

### Rigging, animation and VFX remain the weakest automated links

API rigging now comes built into the generators:

- **Meshy** works only on humanoid characters ([Meshy](https://docs.meshy.ai/en/api/rigging)).
- **Tripo** offers a free rig-check, rigging at 25 credits, retargeting at 10 credits per animation, a Mixamo-compatible skeleton, and in-place locomotion ([Tripo](https://developers.tripo3d.com/en/models/rig)).

For bespoke clips, Uthana's text-to-motion 3.0 API is in limited release ([Uthana](https://uthana.com/docs/api/changelog)), and Tencent's HY-Motion 1.0 provides open weights ([arXiv](https://arxiv.org/html/2512.23464v1)).

The rest of the animation toolchain cannot be automated. Mixamo is GUI-only and in maintenance mode ([Cinevva](https://app.cinevva.com/guides/free-character-animations-rigging)). RADiCAL closed in July 2026 ([CG Channel](https://www.cgchannel.com/tag/radical-canvas/)). Move.ai's API is enterprise-only ([Move.ai](https://docs.move.ai/knowledge/move-ai-pricing-plans-credits)). Non-humanoid rigging remains a manual step.

No production AI VFX generator API exists. The workable loop is: the LLM writes shader code or particle configs through the engine bridge, image models produce flipbook textures, and screenshots plus the profiler judge the result. A practitioner reports that LLMs handle known effect patterns but are weak at multi-pass effects, optimization and novel looks ([Svilenkovic](https://svilenkovic.com/3d/ai-shader-generation)). Mobile-safe defaults are single-pass unlit shaders, CPU particles instead of compute-based VFX Graph, and half precision. These come from common practice, not a cited benchmark.

## Audio generation is good enough; licensing thresholds and loop engineering are not

**Music.** **ElevenLabs Music v2** is the best primary music engine:

- Composition plans with named sections of 3 seconds to 2 minutes, a `force_instrumental` flag, and stems on self-serve plans.
- **$0.15 per minute** ([ElevenLabs](https://elevenlabs.io/eleven-music-api); [pricing](https://elevenlabs.io/pricing/api)).
- Trained on licensed music.

Its terms carry the single most important audio licensing trap. Self-serve plans exclude "Studio Games." A game qualifies as an "Indie Game" only while it has earned **under $500,000** and the developer earns **under $1,000,000 a year** from all games. Above that, the developer has 60 days to move to Enterprise Music ([Eleven Music Terms](https://elevenlabs.io/music-terms)). The plugin must track revenue against this threshold.

Other music options:

- **Lyria 3.5** costs **$0.08 per song**. It is watermarked with SynthID, single-turn and not editable ([Gemini docs](https://ai.google.dev/gemini-api/docs/music-generation)).
- **Lyria RealTime** exposes BPM, scale, density and stem muting, but it is experimental, instrumental only and unpriced, so treat it as R&D ([Gemini docs](https://ai.google.dev/gemini-api/docs/realtime-music-generation)).
- **Stable Audio 3.0** adds inpainting and continuation. Its open Small and Medium weights are usable commercially only under $1M revenue ([The Rundown](https://www.therundown.ai/tools/stable-audio-3-0)).

Exclude Suno, which has no API, a 20–60 downloads-per-month cap and active UMG/Sony litigation ([Suno](https://suno.com/pricing); [Dynamoi](https://dynamoi.com/learn/ai-music-distribution/ai-music-copyright-cases-timeline)). Exclude MusicGen too: its weights are CC-BY-NC ([GitHub](https://github.com/facebookresearch/audiocraft)). None of the official music APIs reviewed documents seamless looping. Loops have to be engineered: request a long steady section at a known BPM, cut at bar boundaries, and verify the seam with PyMusicLooper (MIT), which exports intro, loop and outro files ([GitHub](https://github.com/arkrow/PyMusicLooper)).

**SFX.** **ElevenLabs Sound Effects v2** generates 0.5–30-second clips with a native `loop` flag and 48 kHz PCM, at **$0.12 per minute**, royalty-free on paid plans ([API reference](https://elevenlabs.io/docs/api-reference/text-to-sound-effects/convert); [Sound Effects](https://elevenlabs.io/sound-effects)). A practitioner recommends ElevenLabs for punchy impacts and UI sounds and Stable Audio for textured ambiences. The same practitioner warns that a generated file "is not yet a game sound": it still needs trimming, WAV conversion, mixing and event wiring ([Summer Engine](https://www.summerengine.com/blog/ai-sound-effect-generator-for-games)).

For human-recorded layers there are two programmatic sources. The Sonniss GDC bundles are royalty-free with no attribution, but they prohibit AI training ([Sonniss](https://sonniss.com/gameaudiogdc)). The Freesound API can be filtered to CC0 ([Freesound](https://freesound.org/docs/api/resources_apiv2.html)).

**Voice.** For hero characters, **ElevenLabs v3** has the most complete toolkit. Text-to-Dialogue handles up to 10 voices, inline audio tags and free spatial and radio effects. Voice Design v3 creates original voices that can be reproduced from a seed ([Text-to-Dialogue](https://elevenlabs.io/docs/api-reference/text-to-dialogue/convert); [Voice Design](https://elevenlabs.io/docs/api-reference/text-to-voice/design)). It costs $0.08 per 1,000 characters.

For bulk barks and localization there are two cheaper options:

- **Gemini 3.8 Flash TTS** covers 130+ languages at **$9 per million output tokens through December 31, 2026**, doubling to $18 on January 1, 2027 ([Gemini pricing](https://ai.google.dev/gemini-api/docs/pricing)).
- **Inworld TTS-2** runs from $25 down to $5 per million characters ([Inworld](https://inworld.ai/pricing)).

Vendors die. PlayHT shut down on December 31, 2025 ([TextToLab](https://texttolab.com/blog/play-ht-shutdown-alternatives)), and Replica Studios closed in June 2025 ([MultiLingual](https://multilingual.com/replica-studios-shutdown-2025/)). The pipeline must therefore cache every audio file and keep the voice prompts, seeds and reference audio so each voice can be rebuilt on another provider. Cloning any real performer requires informed, use-specific consent under the SAG-AFTRA 2025 Interactive Media Agreement ([FKKS](https://ipandmedialaw.fkks.com/post/102ksuq/new-sag-aftra-2025-interactive-media-agreement-approved-by-members)).

**Implementation.** Engine-native audio covers indie mobile needs:

- **Godot's `AudioStreamInteractive`** handles horizontal re-sequencing, with transitions on the next beat or bar and filler clips ([Godot](https://docs.godotengine.org/en/stable/classes/class_audiostreaminteractive.html)).
- Godot recommends WAV (QOA) for short effects and Ogg or MP3 for music. MP3 is cheaper on mobile CPUs when several sounds play at once ([Godot](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_audio_samples.html)).
- Unity defaults to Vorbis on mobile, and ADPCM compresses at 3.5x ([Unity Manual](https://docs.unity3d.com/Manual/AudioFiles-compression.html)).
- FMOD's Indie tier is free under a $600k budget ([FMOD](https://fmod.com/licensing)).

No official mobile loudness standard exists. The commonly cited target is about -16 to -18 LUFS integrated, from older guidance ([Audio Media International](https://audiomediainternational.com/mobile-loudness-an-adaptive-approach/)).

ElevenLabs archived its local MCP server on August 20, 2026, in favor of a hosted OAuth endpoint at `api.elevenlabs.io/v1/mcp` ([GitHub](https://github.com/elevenlabs/elevenlabs-mcp)). The hosted tool list was not confirmed, so the plugin's own gateway should wrap ElevenLabs, Lyria, Stable Audio and an ffmpeg loudness, trim and loop chain directly.

## Design by simulation, then gate every feature on play, performance and pixels

**Design and balance.** LLMs write good design documents. In one small study, experts scored an LLM-written hyper-casual GDD 4.71/5 against 3.29/5 for a human one, but rated the two similarly on creativity ([Aydınalp et al.](https://openaccess.izu.edu.tr/entities/publication/b51838a1-dd18-4aa8-b6de-1d5450c8a0e2/full)). An LLM's taste is therefore an idea source, not a balance oracle.

Production evidence for automated balance comes from simulated players:

- King's human-like bots predicted difficulty across more than 1,000 Candy Crush levels ([Gudmundsson et al.](https://www.Gwern.net/doc/reinforcement-learning/imitation-learning/2018-gudmundsson.pdf)). Follow-up work cut the estimate to under a minute, against 7 days of human playtesting per 15-level episode ([Politecnico di Milano](https://www.politesi.polimi.it/handle/10589/141799)).
- **RuleSmith** combines multi-agent LLM self-play with Bayesian optimization to converge on balanced rules ([arXiv](https://arxiv.org/abs/2602.06232)).

The plugin should encode its design contract as JSON: core loop, win and lose conditions, progression curve and tuning tables. The game reads that file and so does a Monte Carlo or bot simulator, and an optimizer tunes the parameters. The same generate-then-verify rule applies to procedural levels. LLM-generated Snake levels were **87% playable at easy difficulty but only 36% at hard** ([FedCSIS 2025](https://annals-csis.org/Volume_43/drp/1909.html)), so every generated level needs a solver gate.

**Retention.** GameAnalytics data gives a median of about **22% D1, under 4% D7 and 0.7–0.8% D30** ([Segwise](https://segwise.ai/blog/mobile-gaming-app-user-retention-strategies)). A D7/D1 ratio below 0.30 points to a first-session problem ([GameDev.net](https://gamedev.net/blogs/entry/2298160-the-d7d1-retention-ratio-for-mobile-games-a-complete-guide)). Practitioners warn that if the "aha" moment takes longer than about 90 seconds, a significant share of users never return ([Playio](https://blog.playio.co/mobile-game-onboarding-retention)). Before launch, the plugin can only proxy these numbers, for example with bot time-to-first-reward and first-session length. After soft launch they become acceptance thresholds.

**QA layering.** Mature, scriptable frameworks form the base:

- GdUnit4 runs Godot scene tests headlessly with input simulation and JUnit output ([GdUnit4](https://fr.github.com/MikeSchulze/gdUnit4)).
- AltTester gives object-level control inside Unity and Unreal scenes ([AltTester](https://alttester.com/blog/page/8)).
- Appium handles only menus, because it "does not see inside game engines' internal scene graphs" ([Sauce Labs](https://docs.saucelabs.com/mobile-apps/automated-testing/appium/appium-for-games/)).

Black-box AI testers exist, but none publishes independent results. nunu.ai runs plain-English tests on real devices ([nunu.ai](https://nunu.ai/blog)). modl.ai supports Android and PC, with iOS in development, and says fast, timing-critical gameplay is "not fully supported yet" ([modl.ai](https://modl.ai)).

Research results set expectations:

- **TITAN** reached 95% task completion and is deployed in 8 QA pipelines ([arXiv](https://arxiv.org/abs/2509.22170)).
- **GBQA**'s best agent, Claude Opus 4.6 in thinking mode, found only 48.39% of bugs ([arXiv](https://arxiv.org/abs/2604.02648)).
- VLMs playing real-time games from raw frames made under 1% progress ([arXiv](https://arxiv.org/html/2505.18134v3)).

The architectural lesson is to build every game with a deterministic, headless logic layer and a semantic action API. Bots can then play thousands of runs cheaply, and pixel-reading agents are needed only for FTUE and exploratory checks. The same evidence argues for turn-based, puzzle and UI-heavy genres.

**Visual QA.** Golden-image tests compare renders against reference images with per-pixel tolerances, but GPU and driver differences make them brittle ([Unity](https://docs.unity3d.com/Packages/com.unity.testframework.graphics@8.9/manual/index.html)). VLM review catches obvious glitches but produces many false alarms. On VideoGameQA-Bench, GPT-4o detected 82.8% of image glitches but had a **17.8% false-positive rate**. At a realistic 5% glitch rate, the authors estimate its precision falls to about 20% ([arXiv](https://arxiv.org/html/2505.15952v1)). Those results come from older models.

The working order is:

1. Structural UI checks through engine introspection (overflowing text, off-screen elements, missing textures).
2. VLM triage with a strict rubric and majority voting.
3. Tournament-style comparisons for aesthetics, since comparative judgment is more reliable than absolute scores ([Claude blog](https://claude.dev/blog/a-harness-for-every-task-dynamic-workflows-in-claude-code/)).

**Performance.** Hold budgets of **16.6 ms per frame at 60 fps and 33.3 ms at 30 fps**. The toolchain is scriptable:

- Unity Performance Testing writes results as JSON ([BugNet](https://bugnet.io/blog/performance-regression-tracking-builds)).
- Perfetto Trace Processor has a Python API with no GUI dependency ([Perfetto](https://perfetto.dev/docs/analysis/trace-processor-python)).
- Arm Performance Advisor generates reports inside CI ([Arm](https://developer.arm.com/community/arm-community-blogs/b/mobile-graphics-and-gaming-blog/posts/automated-performance-advice-for-android-games)).

Google's guidance warns that frame rates often degrade after **45–50 minutes** as devices heat up. Run soak tests and read ADPF thermal headroom ([Android Developers](https://developer.android.com/games/optimize)).

Asset and store requirements to build in:

- Ship ASTC with ETC2 as fallback. ASTC runs on over 75% of active Android devices and ETC2 on over 90% ([Android Developers](https://developer.android.com/games/optimize/textures)).
- Use Play Asset Delivery above 200 MB ([Android Developers](https://developer.android.com/guide/playcore/asset-delivery)), and Apple's Background Assets in place of the deprecated On-Demand Resources ([WWDC25](https://developer.apple.com/videos/play/wwdc2025/325)).
- Stay under Play's bad-behavior thresholds of **1.09% crash rate and 0.47% ANR rate** ([Android Developers](https://developer.android.com/games/optimize/vitals)).

**Device testing.** AWS Device Farm charges **$0.17 per device-minute**, or $250 per unmetered slot per month ([AWS](https://aws.amazon.com/device-farm/pricing/)). A nightly suite of 10 devices × 15 minutes therefore costs about $765 a month. Real low-end devices are mandatory, because emulators do not reproduce GPU, thermal or memory behavior.

## The store last mile automates end to end except a handful of human gates

**Build and release.** The most reliable automated path builds engine exports headlessly on Linux, with GameCI for Unity or a pinned godot-ci image for Godot ([godot-ci](https://hub.docker.com/r/barichello/godot-ci)). iOS is finished on a macOS runner with **fastlane 2.241.1**: `match`, then `gym`, then `pilot` ([fastlane](https://github.com/fastlane/fastlane/releases)). Authenticate only with an App Store Connect **Team** API key, because individual keys cannot reach provisioning endpoints ([fastlane docs](https://docs.fastlane.tools/app-store-connect-api/)). Push Android AABs with `supply` and a Play service account. At WWDC25, Apple added a Build Upload API, HMAC-signed webhooks and a Feedback API ([WWDC25](https://developer.apple.com/videos/play/wwdc2025/324/)). The agent can react to events instead of polling.

CI options and prices:

- GitHub Actions macOS runners cost $0.062 per minute after a January 2026 price cut ([IT Brief](https://itbrief.co.uk/story/github-cuts-actions-runner-prices-adds-new-usage-fee)).
- Codemagic includes 500 free M2 minutes a month ([Codemagic](https://codemagic.io/pricing/)).
- Xcode Cloud includes 25 compute hours a month ([Apple](https://developer.apple.com/xcode-cloud/get-started)).

Human steps remain. fastlane's `produce` cannot create the app record with an API key ([fastlane docs](https://docs.fastlane.tools/app-store-connect-api/)). Unity Personal licenses need a machine-bound `.ulf` file generated in Hub ([GameCI](https://game.ci/docs/github/activation)). Long-standing Play rules also require the first AAB to be uploaded through the Console ([fastlane supply](https://docs.fastlane.tools/actions/supply/)). New personal accounts must pass a 12-tester, 14-day closed test before getting production access ([Play Console Help](https://support.google.com/googleplay/android-developer/answer/14151465)). Store screenshots need an in-engine "screenshot mode," because XCUITest-based capture cannot see engine UI.

**Compliance gates for a pre-flight hook.** On Apple's side ([Apple](https://developer.apple.com/news/upcoming-requirements/)):

- Since **April 28, 2026**, builds must use **Xcode 26 and an iOS 26 SDK**.
- Since **September 9, 2026**, uploads must target **iOS 13 or later**.
- The new age-rating questionnaire was due January 31, 2026.
- Required-reason API declarations are mandatory.
- Listed SDKs must include privacy manifests. The list includes UnityFramework and Firebase ([Apple](https://developer.apple.com/support/third-party-SDK-requirements/)).
- Guideline 5.1.2(i) requires explicit consent before sending personal data to third-party AI services ([Radom](https://www.radom.com/insights/apple-updates-app-review-guidelines-to-strengthen-privacy-protections-against-third-party-ai-data-sharing)).

On Google's side:

- Builds must target **API 36 by August 31, 2026**, with extensions to November 1 ([Android Developers](https://developer.android.com/google/play/requirements/target-sdk)).
- **Play Billing Library 8+** is required by the same deadlines ([RevenueCat](https://www.revenuecat.com/blog/engineering/play-billing-8-migration)).
- Native libraries must support **16 KB pages**. Godot projects need 4.5+ ([Godot forum](https://forum.godotengine.org/t/godot-and-google-play-policy-warning-about-16-kb-memory-page-size/120934)).

Age and youth rules:

- The amended COPPA Rule's compliance deadline was **April 22, 2026**, and biometric identifiers now count as personal data ([Toy Association](https://toyassociation.org/PressRoom2/News/2026-News/updated-coppa-rule-requirements-take-effect-april-22.aspx)).
- Age-assurance laws took effect in Texas, Utah and Louisiana, and route through Apple's Declared Age Range API ([9to5Mac](https://9to5mac.com/2025/11/04/app-store-texas-sb2420-new-apis/)).
- Brazil banned loot-box sales to under-18s from March 2026, and a court ordered Riot to pay damages in June ([Sheep Esports](https://www.sheepesports.com/articles/brazil-court-orders-riot-games-to-pay-eur2-5m-over-league-of-legends-loot-boxes/en)).

Default to transparent monetization, such as battle passes and fixed bundles, over paid random items.

**Monetization.** AppLovin MAX held **55% of top-grossing ad-monetized games**, with LevelPlay at 25% ([PocketGamer.biz](https://www.pocketgamer.biz/nine-facts-about-the-mediation-space-in-2025)). LevelPlay dropped waterfall-only Unity Ads in January 2026 ([Segwise](https://segwise.ai/blog/applovin-publisher-monetization-guide)).

RevenueCat's **official hosted MCP** manages products, entitlements, offerings and experiments, and can even edit store product state in App Store Connect and Play Console ([RevenueCat](https://www.revenuecat.com/docs/tools/mcp)). That makes it the most agent-native IAP layer.

Payment rules now differ by jurisdiction:

- **EU:** Apple's single business model took effect **October 1, 2026**. Commission is 26% with Apple IAP, 20% with an alternative processor, 15% for link-outs, and a 5% Core Technology Commission outside the App Store ([Apple Newsroom](https://www.apple.com/newsroom/2026/08/apple-announces-changes-for-apps-in-the-european-union/)).
- **US, Apple:** link-out fees await the Supreme Court in No. 25-1311 ([SCOTUS docket](https://www.supremecourt.gov/DocketPDF/25/25-1311/424150/20260914154510009_2026-09-14%20No.%2025-1311%20Apple-Epic%20Merits%20Opening%20Brief.pdf)).
- **US, Google:** the alternative-billing fee schedule remains unsettled ([Stash](https://www.stash.gg/blog/blog-epic-v-google-settlement-update-april-2026)).

The plugin should treat storefront country as a config dimension.

**Analytics and backend.** Firebase's official MCP controls Remote Config, Crashlytics, Auth, Firestore and Cloud Messaging, but not App Distribution ([Firebase](https://firebase.google.com/docs/ai-assistance/mcp-server)). Google retired Privacy Sandbox on Android in October 2025, so Android measurement stays on GAID plus consent ([BetaNews](https://betanews.com/2025/10/20/google-is-retiring-privacy-sandbox/)). On iOS, AdAttributionKit has succeeded SKAN ([Moburst](https://www.moburst.com/mobile-attribution-in-2026-what-marketers-actually-need-to-know/)). Adjust publishes an official MCP ([Adjust](https://www.adjust.com/blog/adjust-mcp/)).

Two managed backends restructured in 2026. **Unity deprecated Multiplay on April 1, 2026** ([Unity](https://status.unity.com/info_notices/362941)). **PlayFab replaced Development Mode with Foundation Mode, free for only 1,000 unique users** ([Microsoft Learn](https://learn.microsoft.com/en-za/xbox/playfab/pricing/development-mode)). Both argue for Firebase first, then self-hostable Nakama, with Satori from $1,800/month for live-ops ([Heroic Labs](https://heroiclabs.com/pricing)).

App Store Connect and Play have no first-party MCP servers, only community ones. forgeopslabs/appstore-mcp has 101 tools and is listed in the MCP Registry ([mcpservers.org](https://mcpservers.org/servers/forgeopslabs/appstore-mcp)). Vet and pin one, or wrap fastlane and the REST APIs yourself.

## Architect the plugin as a lean harness: skills know, hooks enforce, workflows scale

### What each Claude Code component carries

Each Claude Code component type has a clear job in this plugin.

**Skills carry knowledge.** Engine APIs pinned to the installed version, store rules, art-direction guides and mobile-hardening checklists belong here. Skills cost almost nothing until invoked: descriptions stay in context, truncated at 1,536 characters, and the body loads on demand. Keep each `SKILL.md` under 500 lines ([Skills](https://code.claude.com/docs/en/skills)).

**Agents carry roles,** each with its own tools, model and effort. Plugin subagents ignore `hooks`, `mcpServers` and `permissionMode`, so enforcement and servers must be declared at plugin level ([Subagents](https://code.claude.com/docs/en/sub-agents)).

**Hooks carry enforcement.** Exit code 2 blocks an action. `decision: "block"` on Stop, SubagentStop and TaskCompleted keeps the agent working. `asyncRewake` lets a long build wake Claude when it fails ([Hooks](https://code.claude.com/docs/en/hooks)).

**MCP servers carry control.** That covers the engine bridge, the asset gateway, a device controller, and the RevenueCat and Firebase servers. Sensitive `userConfig` values go to the OS keychain and reach servers through `${user_config.KEY}`, so they never enter model context ([Plugin reference](https://code.claude.com/docs/en/plugins-reference)).

**Workflows carry scale.** These are JavaScript orchestration scripts with `agent()`, `parallel()` and `pipeline()`. They run up to 16 concurrent agents by default and 1,000 per run, and they are resumable ([Workflows](https://code.claude.com/docs/en/workflows)). That fits batch asset pipelines and release candidates.

Other components help at the edges:

- **Monitors and channels** stream engine logs and CI events into the session.
- **LSP servers** push GDScript and C# diagnostics after each edit.
- **`${CLAUDE_PLUGIN_DATA}`** holds caches that survive updates.

There are three packaging constraints. A top-level `bin/` folder blocks installation on claude.ai and Cowork. Names starting with `claude-` or `cc-plugin-` are rejected. A root `CLAUDE.md` is not loaded ([Plugin reference](https://code.claude.com/docs/en/plugins-reference)).

```
mobile-game-forge/
├── .claude-plugin/plugin.json   # userConfig (sensitive API keys), dependencies on engine adapters
├── skills/  design-contract, genre-templates, godot-mobile, unity-mobile, asset-direction,
│            audio-direction, mobile-hardening, store-compliance, monetization, liveops
├── agents/  producer, gameplay-engineer, technical-artist, audio-designer,
│            qa-playtester, perf-engineer, release-manager, critic
├── workflows/ build-feature.js, asset-batch.js, audio-batch.js, release-candidate.js
├── hooks/hooks.json             # compile gate, done-gate, signing/submit ask-gate, session summary
├── .mcp.json                    # pinned engine bridge, asset+audio gateway, device controller,
│                                #   RevenueCat, Firebase, vetted store MCP
└── evals/<case>/ prompt.md, graders/, case.yaml; evals/mocks/<server>/<tool>.md
```

### The long-horizon harness and the definition of done

Anthropic's long-running harness research is the right template. An initializer writes `init.sh`, a progress log and a JSON feature list in which every item starts as `passes: false`. Coding agents take one feature per session and may change only the `passes` flag. JSON was chosen because models overwrite it less than Markdown. Prompting agents to test "as a human user would" markedly improved results; without it, agents declared features done after unit tests ([Anthropic](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)).

Translated to games, the brief becomes a one-page design contract, then `features.json`, `assets/manifest.json` (provenance, license, cost, status) and `progress.md`. A SessionStart hook injects a compact summary, capped at 10,000 characters ([Hooks](https://code.claude.com/docs/en/hooks)).

A feature flips to `passes: true` only when all five gates pass:

1. The static check passes: `godot --check-only` or Roslyn validation.
2. The headless unit tests pass.
3. A deterministic scripted playthrough with input injection and state assertions passes.
4. A screenshot or `--write-movie` clip clears the critic's rubric.
5. The performance smoke test stays within budget.

TaskCompleted and Stop hooks block until evidence paths exist. Scene and project-settings files are shared and conflict-prone, so they get a single owner agent. Scripts and assets parallelize in worktrees.

Keep the process lean. That means a one-page contract, not 30 documents, plus an explicit regenerate-versus-patch rule. Practitioners advise patching isolated bugs but regenerating when the game has no real core loop ([MakeGame](https://makegame.io/blog/why-ai-generated-games-break)).

### Model routing, runtime modes and security

| Role | Model and effort | Price (input/output per MTok) |
|---|---|---|
| Producer, architect, final critic | Opus 5.5, high/xhigh | $4 / $20 |
| Gameplay engineers, visual critic | Sonnet 5.5, medium/high | $2 / $10 |
| Manifest bookkeeping, log triage, prompt writing | Haiku 5.5, low/medium | from $0.10 / $0.50 |
| Stuck debugging, whole-game redesign | Fable 5.1 (escalation only) | $10 / $50 |

Prices are from [Anthropic's models overview](https://platform.claude.com/docs/en/about-claude/models/overview). The role mapping is my recommendation, to be validated with evals.

Multi-agent systems use about **15x the tokens of chat** ([Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)). Enterprise Claude Code use averages about $13 per developer per active day ([Costs](https://code.claude.com/docs/en/costs.md)). Claude Code's budget flags cover only model tokens, so the asset gateway must enforce its own dollar budget.

The plugin runs in four modes:

- **Interactive sessions** for creative direction and sign-off.
- **Headless runs** (`claude --bare -p --plugin-dir … --output-format stream-json --max-budget-usd N`) for overnight build-and-test loops ([Headless](https://code.claude.com/docs/en/headless.md)).
- **`anthropics/claude-code-action@v1`** for CI gates ([GitHub Actions](https://code.claude.com/docs/en/github-actions.md)).
- **Routines** for nightly builds and crash triage ([Routines](https://code.claude.com/docs/en/routines.md)).

Agent teams are interactive-only, so headless pipelines should use subagents and workflows ([Agent teams](https://code.claude.com/docs/en/agent-teams.md)). A hosted "build my game" SaaS would have to be an Agent SDK or Managed Agents product billed by API key. Third-party products cannot offer claude.ai login ([Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview)).

Security rules for the plugin:

- Turn on the OS sandbox with a domain allowlist. MCP servers and hooks run outside the sandbox ([Sandboxing](https://code.claude.com/docs/en/sandboxing.md)).
- Keep signing keys and store credentials behind deny rules. Expose signing and submission only through a dedicated tool gated by a PreToolUse `ask`, and never inside routines.
- Use `--bare` in CI, because a plain `-p` run executes repository hooks and MCP servers without a trust prompt ([Headless](https://code.claude.com/docs/en/headless.md)).

### Evals as the product's quality contract

`claude plugin eval` runs each case three times with the plugin and three times without, and reports the difference. It offers regex, tool-use, tool-order, file-exists, LLM and baseline graders, mockable MCP servers and `--max-cost-usd` caps. It has **no custom-code graders** ([Plugin evals](https://code.claude.com/docs/en/plugin-evals)). To grade deterministic results such as build success, APK size or FPS, have the run write them to files and grade those files.

Add an internal benchmark modeled on GameCraft-Bench: dozens of briefs across mobile genres, scripted input replays, and multimodal rubric judging. Publish its pass rate as the headline quality metric.

## Recommended top-tier toolchain and its October 2026 price tags

| Layer | Pick | Cost (list, Oct 2026) |
|---|---|---|
| Orchestration | Claude Code plugin + headless/SDK runners; Opus 5.5 / Sonnet 5.5 / Haiku 5.5, Fable 5.1 escalation | $4/$20, $2/$10, from $0.10/$0.50, $10/$50 per MTok ([Anthropic](https://platform.claude.com/docs/en/about-claude/models/overview)) |
| Engine, 2D/default | Godot 4.7.2, typed GDScript | Free, MIT ([GitHub](https://github.com/godotengine/godot)) |
| Engine, 3D | Unity 6.3 LTS + URP (6.7 LTS next) | Free under $200K; Pro $2,310/seat/yr ([Unity](https://unity.com/products/pricing-updates)) |
| Engine bridges | satelliteoflove + tugcantopaloglu godot-mcp; Unity CLI + official plugin + CoplayDev unity-mcp | Free ([Unity docs](https://docs.unity.com/en-us/unity-cli/replace-mcp-server-unity-cli)) |
| 2D workhorse | Nano Banana 2.1 | $0.0336/1K image; $0.0168 batch ([Gemini](https://ai.google.dev/gemini-api/docs/pricing)) |
| Hero/marketing art | GPT Image 2.5 (Sunburst/Flare) | ~$0.21 at max quality, 1024² ([AA](https://artificialanalysis.ai/image/leaderboard/text-to-image)) |
| Icons/UI vector, bg removal | Recraft V4.1 Vector | ~$0.08/image; ~$0.01 bg removal/vectorize ([Recraft](https://www.recraft.ai/pricing?tab=api)) |
| Style lock | Scenario (MCP + LoRA) or fal LoRA trainers | Scenario ~$15–200/mo (secondary) ([Stork](https://www.stork.ai/en/scenario)); fal ~$9.71–47 per 1,000 steps ([fal](https://fal.ai/models/fal-ai/flux-2-trainer-v2/edit)) |
| Pixel art | PixelLab (MCP) + Retro Diffusion | PixelLab subscription; RD $0.015–0.18/image ([mcpservers.org](https://mcpservers.org/servers/retro-diffusion/retro-diffusion-mcp)) |
| Atlases | TexturePacker CLI (ASTC/ETC2/KTX2) | CI/Docker license ([CodeAndWeb](https://www.codeandweb.com/texturepacker/documentation/commandline)) |
| 3D props / low-poly | Tripo P1 | 40–60 credits/model ([Tripo](https://developers.tripo3d.com/en/models/p1)) |
| 3D generate→rig→animate | Meshy (meshy-7.1) + official MCP | €19 Pro (1,000 cr) to €95 Ultra (8,000 cr); ~49 cr per rigged animated asset ([Meshy](https://www.meshy.ai/pricing)) |
| Hero quad characters | Rodin Gen-2.5 | $120/mo Business for API ([Hyper3D](https://hyper3d.ai/pricing)) |
| Bulk self-host 3D | TRELLIS.2 | Free, MIT; 24GB+ GPU ([GitHub](https://github.com/microsoft/TRELLIS.2)) |
| 3D optimization | Headless Blender + Blender MCP, gltfpack/gltf-transform | Free ([GitHub](https://github.com/ahujasid/blender-mcp)) |
| Skyboxes | Blockade Labs Skybox API | $140/mo Business ([Blockade](https://skybox.blockadelabs.com/plans)) |
| Music | ElevenLabs Music v2; Lyria 3.5 for alternates | $0.15/min; $0.08/song ([ElevenLabs](https://elevenlabs.io/pricing/api); [Gemini](https://ai.google.dev/gemini-api/docs/pricing)) |
| SFX | ElevenLabs SFX v2 + Sonniss GDC + Freesound CC0 | $0.12/min; free libraries ([ElevenLabs](https://elevenlabs.io/pricing/api)) |
| Voice | ElevenLabs v3 (hero); Gemini 3.8 Flash TTS or Inworld TTS-2 (bulk) | $0.08/1K chars; $9/M output tokens to Dec 31, 2026; $25→$5/M chars ([Inworld](https://inworld.ai/pricing)) |
| Audio post | ffmpeg loudnorm + PyMusicLooper; FMOD only if needed | Free; FMOD Indie free under $600k budget ([FMOD](https://fmod.com/licensing)) |
| Tests | GdUnit4, Unity Test Framework, AltTester, Appium | Mostly free/open source (AltTester terms not researched) |
| Devices | Firebase Test Lab, AWS Device Farm | ~$5/physical device-hour (third-party) ([Back4App](https://blog.back4app.com/firebase-test-lab/)); $0.17/device-min ([AWS](https://aws.amazon.com/device-farm/pricing/)) |
| Performance | Perfetto Trace Processor, Unity Performance Testing, Arm Performance Studio, ADPF | No license cost found in research |
| CI/release | GitHub Actions or Codemagic; GameCI/godot-ci; fastlane | macOS $0.062/min ([IT Brief](https://itbrief.co.uk/story/github-cuts-actions-runner-prices-adds-new-usage-fee)); Codemagic 500 free M2 min ([Codemagic](https://codemagic.io/pricing/)) |
| IAP | RevenueCat (official MCP) over StoreKit 2 / PBL 8 | Free tier, then revenue share ([RevenueCat](https://www.revenuecat.com/pricing)) |
| Ads | AppLovin MAX with bidding (official Godot plugin) | Pricing not researched |
| Analytics/live-ops | Firebase (official MCP); Adjust when paid UA starts | Firebase core products no-cost ([Firebase](https://firebase.google.com/pricing)) |
| Backend scale-up | Nakama self-host → Satori; Photon Fusion for real-time | Satori from $1,800/mo ([Heroic Labs](https://heroiclabs.com/pricing)) |

Metered generation costs are small. Here is my arithmetic for a 2D casual game at the list prices above:

- 400 sprites, UI pieces and backgrounds at three candidates each in Nano Banana batch: about $20.
- 50 GPT Image 2.5 hero and marketing images: about $10.
- 60 Recraft vector icons: about $5.
- One LoRA: $10–47.
- 72 minutes of candidate music: about $11.
- About 480 short SFX takes: about $2.

That totals roughly **$60–100**. A 3D game with 150 rigged, animated models needs about 7,350 Meshy credits, which fits inside one €95 Ultra month. The real cost lines are subscriptions: ElevenLabs Pro at $99/month is needed for 44.1 kHz PCM output, and Rodin, Blockade and Unity Pro add more if used. Then come macOS minutes, a device farm (about $765/month for nightly runs) and model tokens. No source measures token spend for a full game build, so Phase 0 must instrument it with `--max-budget-usd` and `total_cost_usd`.

## Build in four phases, shipping a Godot 2D slice to the stores first

The timings below are my recommendation, not sourced estimates.

| Phase | Timing | What gets built | Exit gate |
|---|---|---|---|
| 0. Harness | Weeks 0–4 | Plugin skeleton and `userConfig` keys; asset/audio gateway MCP with budgets and provenance manifest; pinned Godot bridges; `features.json`/`progress.md` harness; compile, done and ask hooks; eval suite skeleton with MCP mocks | A template 2D game builds headlessly to a signed AAB; `claude plugin eval` shows a positive Δ over no-plugin baseline; token and asset spend measured per run |
| 1. 2D vertical slice | Months 1–3 | Design-contract skill and 4–6 mobile genre templates (puzzle, merge, runner, idle, match-3, hybrid-casual); 2D style-lock pipeline; audio pipeline with loop and loudness QC; GdUnit4 plus deterministic-stepping playtests and vision critic; mobile-hardening skill (safe areas, touch, pause/resume, audio focus, low-end budgets); fastlane lanes and compliance pre-flight | Internal benchmark: at least 20 briefs produce installable builds on TestFlight and Play internal testing that pass the five-gate definition of done; human reviewers rate art cohesion acceptable |
| 2. Monetize and operate | Months 3–6 | MAX, RevenueCat and Firebase wiring; analytics event taxonomy; Remote Config A/B; balance simulator with bot playthroughs; device-farm perf and soak gates; screenshot mode, store metadata, age-rating and Data safety generators; storefront-country payment config | A soft-launch-ready build whose projected crash/ANR rates sit under Play vitals thresholds and whose bot FTUE proxies meet targets |
| 3. Unity 3D adapter | Months 6–9 | Unity CLI and CoplayDev integration with procedural scene building; 3D pipeline (Tripo/Meshy/Rodin → Blender → gltfpack/KTX2); URP mobile presets; AltTester and golden-image tests; GameCI with license-server activation | A 3D sample game holds p95 frame time ≤33.3 ms on the low device tier and passes the same release gates |
| 4. Live-ops and scale | Months 9–12+ | Routines for nightly builds, crash triage and review replies; playable-ad generator for CPI tests; optional LLM-NPC modules with cost caps; public benchmark; Agent SDK hosted offering billed by API key | Published benchmark results and at least one externally soft-launched title with retention data |

The sequence follows the evidence. Godot comes first because text scenes, single-binary headless export and MIT licensing remove the most failure points for an agent. 2D casual comes first because bots and VLM testers work best in turn-based, puzzle and UI-heavy genres ([modl.ai](https://modl.ai)), and hybrid-casual is where spending is growing. Unity waits until Phase 3 because license activation, YAML scenes and macOS-bound iOS builds add operating cost, and because its official agent tooling only settled on the CLI in August 2026.

## Key risks: licensing traps, moving store gates, and predictable quality failures

| Risk | Concrete exposure | Built-in mitigation |
|---|---|---|
| Revenue-threshold licenses | ElevenLabs Music self-serve excludes games earning ≥$500K or devs earning ≥$1M a year ([terms](https://elevenlabs.io/music-terms)); Stable Audio open weights free only under $1M ([The Rundown](https://www.therundown.ai/tools/stable-audio-3-0)) | Revenue fields in project config; alerts before thresholds; plan tier recorded per asset, since output follows the plan at creation |
| Non-commercial or territorial weights | Hunyuan3D 2.x excludes EU/UK/South Korea ([license](https://huggingface.co/tencent/Hunyuan3D-2/blob/main/LICENSE)); FLUX.2 [dev], BRIA RMBG, MusicGen/AudioGen non-commercial; Spine AI skill PolyForm NC | License allowlist enforced in the gateway; prefer MIT/Apache models and paid APIs |
| Free-tier ownership | Meshy Free is CC BY ([Meshy](https://www.meshy.ai/pricing)); Tripo's free terms contradict each other ([Tripo](https://www.tripo3d.ai/help/privacy-policy/how-to-use-tripo-models-commercially)); Recraft free outputs belong to Recraft | Gateway refuses free-tier keys for production assets |
| Copyright and indemnity | Purely AI-generated art is not copyrightable in the US ([Promise Legal](https://blog.promise.legal/ai-game-assets-copyright-steam-disclosure-2026/)); no 3D vendor indemnity found; Adobe excludes partner models ([Adobe](https://helpx.adobe.com/uk/legal/product-descriptions/partner-model.html)) | Provenance manifest; human-edit and arrangement checkpoints for key assets |
| Disclosure and stigma | Steam requires disclosure of player-facing AI content ([Gigazine](https://gigazine.net/gsc_news/en/20260120-steam-updates-ai-disclosure-guidelines)); AI-disclosing games get ~53% fewer reviews | Auto-generated disclosure text; style lock and human art swap-in; keep AI behind the scenes |
| Runtime AI features | Apple 5.1.2(i) consent; Google Play gen-AI apps must offer in-app reporting ([9to5Google](https://9to5google.com/2023/10/25/google-play-gen-ai-policy/)); OpenAI requires disclosing AI voices ([OpenAI](https://developers.openai.com/api/docs/guides/text-to-speech)) | AI-as-mechanic modules ship with consent dialogs, report buttons and disclosure credits |
| Moving store gates | Xcode 26 SDK, iOS 13 floor, API 36, PBL 8, 16 KB pages, age assurance, COPPA | Versioned compliance skill plus pre-flight hook that blocks uploads |
| Payment-rule flux | SCOTUS No. 25-1311 pending; Google US fees unsettled; EU 12-month payment-choice lock | Storefront-country config; never hard-code commission assumptions |
| Vendor churn | Unity MCP launched then deprecated within ~4 months; PlayFab free tier cut to 1,000 users; Multiplay deprecated; PlayHT/Replica shut down; Meshy `lowpoly` retires Oct 30; original Nano Banana shut down Oct 2 ([Gemini](https://ai.google.dev/gemini-api/docs/pricing)) | Adapter layer per vendor; SHA-pinned bridges; cached outputs with re-creation recipes; fallback providers |
| Quality failure modes | 41.46% best GameCraft-Bench score; touch, state-reset and restart bugs ([MakeGame](https://makegame.io/blog/why-ai-generated-games-break)); "features that had never met each other" ([DEV](https://dev.to/seagamesai/my-first-ai-generated-game-looked-great-on-paper-and-boring-on-screen-5eo4)); hard procedural levels only 36% playable | Five-gate definition of done; solver gates; regenerate-vs-patch policy; human playtest builds via TestFlight/internal track |
| False confidence in QA | VLM precision ~20% at realistic glitch rates; GBQA 48% recall | Structural checks first; majority-vote VLM triage; humans review flagged items |
| Security | Blender MCP unauthenticated socket; Epic plugin's arbitrary Python and asset deletion ([GitHub](https://github.com/EpicGames/unreal-engine-skills-for-claude-code-plugin)); community store MCPs | Sandbox and allowlists; signing via gated tool only; vetted, pinned servers; `--bare` in CI |

Of these, the quality failure modes deserve the most design attention, because they repeat across every source. Agents produce games that run but cannot be played: dead input, broken resets, desktop-only touch handling, unscaled touch coordinates and restart loops ([MakeGame](https://makegame.io/blog/why-ai-generated-games-break)). Their systems are shallow: inventory, save/load and economy rarely work in depth. Their presentation is incoherent. Output is non-deterministic, so the same prompt yields a different game ([Althera Games](https://altheragames.com/en/blog/ai-game-generators-2026)). Long chat iterations decay, because fixing one mechanic breaks another ([HackerNoon](https://hackernoon.com/making-playable-things-part-1-the-problem-with-ai-generated-games-isnt-the-ai)).

Fun itself is not solved by generation. The plugin can only approximate it through game-feel checklists, bot-simulated difficulty curves and fast human playtest builds. Treat it as a human checkpoint, not an automated claim.

## Conclusion

The research changes the meaning of "world-class" for this product. Generation is no longer the hard part. Assets for a whole casual game cost less than a Unity Pro seat costs in a month, and two engine vendors give away their Claude Code bridges. The scarce capability is a **machine-checkable definition of done for mobile games**: deterministic playthroughs, device performance budgets, compliance pre-flights and rubric-judged visuals, enforced by hooks and measured by evals. Whoever encodes that best, and publishes benchmark numbers against the roughly 41% state of the art, owns the category. The same evidence explains why the best-funded competitors are poorly placed. Their business model rewards feed engagement, not exported, store-ready, owned games.

The honest framing for users is "automatic between taste checkpoints," not "fully autonomous." The benchmarks (48% bug recall, 20% VLM precision) and the market signals (the Steam flood, 53% fewer reviews for disclosed AI) point the same way. Human sign-off on style, fun and store submission is still where quality and trust come from. Build the plugin so those checkpoints are few, fast and well informed, and keep everything else agent-driven, verified and reproducible. The vendor churn of 2026 also argues for engine-agnostic orchestration with pinned adapters. Godot's text-native design fits agents structurally, and Unity's own shift from MCP to a CLI suggests the rest of the industry is moving the same way.
