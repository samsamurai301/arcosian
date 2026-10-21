# AI Tools, APIs and Implementation for Mobile Game Audio (state as of October 2026)

Research note: the session's shared web-search budget ran out partway through, so later findings rest on direct fetches of primary pages (vendor docs, pricing pages, GitHub) rather than fresh searches. Areas I could not search are listed under Gaps. Where a source is secondary (a blog or aggregator) or older than 2026, I say so inline.

## 1. Music generation: which services are API-automatable, controllable, and commercially licensable (and which can make loops and stems)?

### Takeaway
As of October 2026, ElevenLabs Eleven Music (v2) is the strongest fit for an agent-driven, commercially licensable game music pipeline. It has an official API, section-level composition plans, a forced-instrumental flag, stems, training on licensed data, and explicit "Indie Game" rights on self-serve plans. Google Lyria is the cheapest official API (Lyria 3.5 / 3 Pro at $0.08 per song via the Gemini API). Lyria RealTime is the only official API with live BPM, key and density controls suited to adaptive music, but it is experimental and instrumental only. Stable Audio 2.5/3.0 is the best choice for instrumental beds, audio-to-audio, inpainting and continuation, and it also offers self-hostable open weights. Suno and Udio are poor fits for automation: neither has an official public API, both have download caps or walled gardens, and Suno is still in active litigation with UMG and Sony. Meta MusicGen weights are non-commercial. None of the official APIs reviewed document a native "seamless loop" mode for music. Looping and stem-based adaptivity still need post-processing or careful generation strategy.

### Cited Findings

**ElevenLabs Eleven Music (v1 Aug 2025 → v2 May 2026)**
- Eleven Music v1 launched Aug 5, 2025. Music v2 launched May 26, 2026, adding better vocals and arrangement, genre shifts within a track, embedded sound effects, section inpainting, improved multilingual output, and API price cuts of up to 50%. — [invideo (Aug 6, 2026, secondary)](https://invideo.io/blog/elevenlabs-music-ai-generator/)
- API: `POST https://api.elevenlabs.io/v1/music`, model ID `music_v2`, Python and JS SDKs (`elevenlabs.music.compose(...)`). Track length via `music_length_ms` runs from 3,000 ms to 600,000 ms (10 min). Composition plans define named sections (intro, verse, chorus, outro), each with its own positive and negative styles, duration (3 s to 2 min) and lyrics. — [ElevenLabs Music API page](https://elevenlabs.io/eleven-music-api)
- The self-serve tier lists "Streaming, stems, timestamps, and editing". In-painting via `source_from` is listed as Enterprise-only on the product page, and Enterprise adds 10+ concurrent generations and 10+ finetune slots. — [ElevenLabs Music API page](https://elevenlabs.io/eleven-music-api). Conflict: invideo describes section inpainting (`store_for_inpainting`) as a general v2 feature — [invideo](https://invideo.io/blog/elevenlabs-music-ai-generator/)
- Search-result snippets of ElevenLabs' music pricing table indicate stem counts vary by tier: lower tiers get 2 or 4 stems and the top listed self-serve tier gets up to 6. I could not confirm this on a fetched page. — [ElevenLabs Music page (search snippet)](https://elevenlabs.io/music)
- v2 has a `force_instrumental` flag for guaranteed no-vocal output. Composition plans and a text prompt are mutually exclusive. Music Finetunes train a custom style on about 5–10 minutes of your audio. Steering accepts a roughly 30-second audio reference. — [invideo](https://invideo.io/blog/elevenlabs-music-ai-generator/)
- Output is up to 44.1 kHz, in MP3 (up to 192 kbps), PCM (up to 48 kHz) or Opus. PCM 44.1 kHz requires the Pro plan or above. Streaming generation is marketed "for games, interactive tools, and dynamic scoring." — [ElevenLabs Music API page](https://elevenlabs.io/eleven-music-api)
- API price: Music $0.15 per minute. Plans: Starter $6/mo, Creator $22, Pro $99, Scale $299, Business $990. — [ElevenLabs API pricing](https://elevenlabs.io/pricing/api)
- Training data: "Trained on licensed stems and music," made in collaboration with labels, publishers and artists. — [ElevenLabs](https://elevenlabs.io/eleven-music-api). Named partners are Merlin Network (indie labels) and Kobalt (publishing). No major labels are named. — [invideo](https://invideo.io/blog/elevenlabs-music-ai-generator/)
- **Game licensing (key finding):** The Eleven Music terms allow "All online and offline commercial use permitted, except film, TV, radio, and Studio Games" on Free through Scale, Business and Enterprise Music Lite. Only Enterprise Music permits all uses. An "Indie Game" is excluded from the Studio Game definition and must meet two tests. First, the game earned less than $500,000 since first commercial release. Second, the developer earned less than $1,000,000 from all games in its most recent financial year, net of platform fees and including affiliates. If a game stops qualifying, you have 60 days to move to a plan that permits Studio Game use, and copies distributed before that deadline may continue to be used. — [Eleven Music Terms](https://elevenlabs.io/music-terms)
- Further terms:
  - The Free plan requires attribution ("Created in collaboration with ElevenLabs").
  - Free, Starter, Creator and Pro are "For Individual Use Only". Scale is limited to entities with fewer than 10 employees, and Business to fewer than 50.
  - Output stays subject to the plan in effect when it was created, even after a downgrade or cancellation.
  - You may not prompt with artist names, song titles or label names, or use Output to build a third-party Music Library.
  - "You are responsible for reviewing Output for clearance."

  — [Eleven Music Terms](https://elevenlabs.io/music-terms)
- Conflict on the Free tier: the API pricing page says "Commercial use licensing on Starter+ plans" — [ElevenLabs API pricing](https://elevenlabs.io/pricing/api) — and invideo says Free has no music commercial use — [invideo](https://invideo.io/blog/elevenlabs-music-ai-generator/) — while the Music Terms text lists Free (with attribution) among plans permitting commercial use except Studio Games — [Music Terms](https://elevenlabs.io/music-terms).

**Google Lyria (Gemini API / Vertex AI)**
- Gemini API music models (doc last updated 2026-10-01):
  - `lyria-3-clip-preview` always produces 30 s of MP3.
  - `lyria-3.5` produces "a couple of minutes", controllable by prompt, as MP3 or WAV.
  - Both output 44.1 kHz stereo and accept text plus up to 10 images.
  - Lyria 3.5 supports vocals and timed lyrics with `[Verse]`/`[Chorus]` tags, structure via timestamp ranges such as `[0:00 - 0:10] Intro`, and instrumental-only output via the prompt.
  - The doc does not mention BPM, key, stems or loop controls.
  - Generation is single-turn: iterative editing is not supported, and results vary between calls even with the same prompt.
  - All audio carries a SynthID watermark.

  — [Gemini API music generation docs](https://ai.google.dev/gemini-api/docs/music-generation)
- Pricing on the Gemini API: Lyria 3.5 $0.08 per song, Lyria 3 Pro Preview $0.08 per song, Lyria 3 Clip Preview $0.04 per song. No free tier. — [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing)
- **Lyria RealTime** (`models/lyria-realtime-exp`, experimental) streams over a persistent WebSocket.
  - Controls: weighted text prompts that can change mid-stream, `bpm` [60–200], `density` and `brightness` [0–1], `scale` (enums such as `C_MAJOR_A_MINOR`), `mute_bass`, `mute_drums`, `only_bass_and_drums`, `guidance` [0–6], `temperature` [0–3], `top_k`, `seed`, and `music_generation_mode` (QUALITY / DIVERSITY / VOCALIZATION).
  - Output is raw 16-bit PCM, 48 kHz stereo. The doc's JS example uses 44.1 kHz, so the doc is inconsistent.
  - Instrumental only and always watermarked. Pricing is not stated.
  - Changing `scale` requires a stop/play or context reset.

  — [Lyria RealTime docs](https://ai.google.dev/gemini-api/docs/realtime-music-generation)
- `lyria-002` (Lyria 2) reached GA on Vertex AI on May 20, 2025 and produces 30 s, 48 kHz instrumental-focused WAV. Lyria 3 Clip/Pro entered public preview Mar 25, 2026. Lyria 3 Pro runs up to 184 s. Vertex per-song pricing for lyria-002 could not be verified. Whether Lyria is covered by Google Cloud's gen-AI indemnification was also unverified. — [invideo Lyria explainer (Aug 6, 2026, secondary)](https://invideo.io/blog/lyria-ai-music-generator/)

**Stability AI Stable Audio 2.5 / 3.0**
- Stable Audio 2.5:
  - Tracks up to 3 minutes, generated in under 2 seconds on a GPU.
  - Supports text-to-audio, audio-to-audio and audio inpainting (upload audio and generate the rest from a chosen start point).
  - Produces multi-part intro/development/outro structure.
  - Trained on a "fully licensed dataset" and marketed as "commercially safe."
  - Available via the Stability API, fal, Replicate and ComfyUI, with on-prem enterprise licensing. Positioned for brand audio "across ads, games…" through a WPP/amp partnership. Announced Sep 10, year not printed on page; context suggests 2025.

  — [Stability AI announcement](https://stability.ai/news-updates/stability-ai-introduces-stable-audio-25-the-first-audio-model-built-for-enterprise-sound-production-at-scale)
- Stable Audio 3.0 has four models:
  - Small SFX (0.6B, open weights, on-device SFX).
  - Small (0.6B, open, music up to 2 min).
  - Medium (2B, open, up to 6:20).
  - Large (API or enterprise self-host only). Large API price: 26 credits ($0.26) per successful generation.

  It adds multi-segment inpainting, causal continuation past the track end, and LoRA training for Small and Medium. The open weights fall under the Stability AI Community License: commercial use requires registration and attribution and is only allowed while annual revenue is under $1M; above that an Enterprise license is required. Outputs are owned by the user "as between" the user and Stability, with no non-infringement guarantee. — [The Rundown review (reviewed Aug 31, 2026, secondary)](https://www.therundown.ai/tools/stable-audio-3-0)
- Stable Audio 2.5 API price conflict: 20 credits ($0.20) per result — [The Rundown](https://www.therundown.ai/tools/stable-audio-2-5) — versus 8 credits listed on a stale Stability pricing page (search snippet) — [Stability pricing](https://platform.stability.ai/pricing).

**Suno / Udio and the label lawsuits (2024–2026)**
- Timeline:
  - The RIAA sued Suno (D. Mass.) and Udio (S.D.N.Y.) on June 24, 2024.
  - UMG settled with Udio in late Oct 2025, including licenses and a planned 2026 licensed subscription service.
  - Warner settled with Suno in Nov 2025 and announced a licensed-AI partnership with artist opt-in.
  - As of May 2026, UMG and Sony v. Suno and Sony v. Udio were still active, and no fair-use ruling had been issued.

  — [Dynamoi timeline (updated May 11, 2026)](https://dynamoi.com/learn/ai-music-distribution/ai-music-copyright-cases-timeline). The UMG–Udio date is reported as Oct 29, 2025 by [Digital Music News](https://www.digitalmusicnews.com/2025/10/29/umg-udio-deal-everything-we-know/) and as Oct 31 by Dynamoi.
- WMG settled with both Suno and Udio (Nov 2025). Suno–UMG/Sony talks reportedly stalled in April 2026 over equity stakes and royalty guarantees. In Sept 2025 the labels added a DMCA stream-ripping claim, and in April 2026 Udio admitted using yt-dlp to download YouTube audio for training. Suno reported 2M paying subscribers and $300M ARR (Feb 2026). Klay Vision is cited as a fully licensed alternative (three majors plus Merlin and Kobalt). — [We Rave You (May 7, 2026)](https://weraveyou.com/2026/05/suno-udio-umg-copyright-lawsuit-musicians-2026/)
- Udio's post-settlement platform is a "walled garden": downloads of audio, stems and video are restricted, and output is confined to Udio's player. A mobile-first app called "Starstruck" was reportedly shown in an April 30, 2026 webinar. — [UMG–Udio coverage via search](https://www.digitalmusicnews.com/2025/10/29/umg-udio-deal-everything-we-know/); [Let's Data Science (secondary, based on a private webinar)](https://letsdatascience.com/news/udio-unveils-starstruck-licensed-ai-music-app-1e5cd967)
- Suno pricing page (Oct 2026):
  - **Free** ($0): 50 credits/day, no downloads, v6-mini model, "No commercial rights."
  - **Pro** ($8/mo): 2,500 credits, 20 downloads/mo, 2 stem types, v6 and v6-wild models, commercial use.
  - **Premier** ($24/mo): 10,000 credits, 60 downloads/mo, 3 stem types, Suno Studio, commercial use.
  - No API is mentioned.

  — [Suno pricing](https://suno.com/pricing)
- Suno has no self-serve public API. Only third-party routes exist, and community wrappers such as rhdeck/suno-api are unofficial. — [Unifically (aggregator)](https://unifically.com/blogs/suno); [rhdeck/suno-api](https://github.com/rhdeck/suno-api). Download caps were reportedly enforced from Sept 3, 2026, and stems count against a song's download. — [MindStudio (secondary)](https://www.mindstudio.ai/blog/suno-v6-pricing-download-limits)
- US Copyright Office guidance: purely AI-generated works cannot be protected, while AI-assisted human creation may qualify. A paid tool license grants usage rights but not copyrightability. — [Dynamoi](https://dynamoi.com/learn/ai-music-distribution/ai-music-copyright-cases-timeline)

**Others**
- Meta AudioCraft: the code is MIT, but the MusicGen, AudioGen, MAGNeT and JASCO weights are CC-BY-NC 4.0 (non-commercial). 23.7k stars. — [facebookresearch/audiocraft](https://github.com/facebookresearch/audiocraft)
- Mubert's developer API is priced separately and requires contacting sales. Beatoven appears as "API available" in comparisons, but no rate card was found. One comparison table lists Soundraw API access as "No". Consumer prices conflict across sources. — [Rework roundup (secondary)](https://resources.rework.com/tools/ai-tools/best-ai-music-generators-2026); [CostBench](https://costbench.com/software/ai-music-apis/beatoven-ai/)
- AIVA is reported to transfer full copyright only on the Pro plan (about €33/mo annual), with AIVA keeping copyright on Free and Standard. One source contradicts this, saying AIVA retains rights and grants a license. API licensing terms and game use were not confirmed. — [Tooliverse (secondary)](https://tooliverse.ai/tools/aiva); [Vantaige (conflicting)](https://vantaige.io/ai-tool/aiva)

### Inferences
- **Recommended music stack for an agent:**
  - (1) ElevenLabs Music v2 as primary. It offers composition plans for intro/loop-body/outro sections, `force_instrumental`, stems for vertical layering, and an explicit Indie Game carve-out. Studios above $500k per game or $1M per year need Enterprise Music.
  - (2) Lyria 3.5 via Gemini API for cheap high-volume ideation and alternates ($0.08 per song, no free tier).
  - (3) Lyria RealTime for prototyping adaptive or procedural layers. With fixed `bpm`, `scale` and `seed`, it can render matching layers by toggling `mute_drums` / `mute_bass` / `only_bass_and_drums`. It is experimental and has no published price, so treat it as R&D, not a shipping dependency.
  - (4) Stable Audio 2.5/3.0 for instrumental beds, inpainting a loop tail, and continuation. 3.0 Small/Medium can be self-hosted for free under the Community License while revenue stays under $1M.
- Avoid Suno and Udio for automated commercial pipelines. Neither has an official API, Suno has per-month download caps (20 or 60), Udio is a walled garden, and UMG/Sony v. Suno is unresolved. Avoid MusicGen weights for commercial use.
- "Seamless loop" for music is not a documented first-class feature in any of the official music APIs reviewed (ElevenLabs Music, Lyria, Stable Audio). Loops must be engineered in one of three ways. You can request a structure with a long steady section and cut it at bar boundaries using the known BPM. You can use inpainting or continuation to make the end flow into the start. Or you can detect loop points afterwards (see Section 4).
- Watermarking (SynthID on Lyria, C2PA on ElevenLabs per invideo) is imperceptible and should not affect game use. It does mean outputs are identifiable as AI, which matters for store disclosure policies.
- Because purely AI music is likely uncopyrightable in the US, a game's AI soundtrack can be freely copied by others. Human arrangement and editing strengthens any claim.

### Gaps
- I could not verify the reported second UMG/Sony suit against Suno (Sept 18, 2026, aimed at V6), or Suno's statement that V6 was developed with WMG, BMG and Believe. Both appear only in secondary search summaries.
- I could not confirm exact stem counts per ElevenLabs tier, or whether ElevenLabs Music stems are API-accessible on self-serve plans (vs UI only).
- No current official Stability price page content was retrievable. Stable Audio prices come from a secondary review.
- MiniMax Music, Mureka, ACE-Step (open source) and Klay were not researched because the search budget ran out.
- No independent head-to-head quality benchmark across music models was found. ElevenLabs publishes none, per invideo.
- No source confirmed loop-specific features in any music model, or loop quality in practice.

## 2. Sound effects and UI sounds: AI generators and programmatically usable royalty-free libraries

### Takeaway
ElevenLabs Sound Effects v2 is the most practical API for agent-generated SFX and UI sounds. It accepts clips of 0.5–30 s, has a native `loop` flag, offers 48 kHz output on paid plans, is royalty-free for commercial use on paid plans, and costs $0.12 per minute via the API. Stable Audio (2.5 API, or the 3.0 Small SFX open-weights model for on-device or self-hosted use) is better for textured ambiences. For curated, human-recorded material, the Sonniss GDC bundles (royalty-free, no attribution, AI training prohibited) and the Freesound API (filter to CC0) are the programmatic library options.

### Cited Findings
- ElevenLabs SFX API:
  - Endpoint `POST https://api.elevenlabs.io/v1/sound-generation`.
  - Params: `text`, `loop` (boolean, "smoothly looping", only with `eleven_text_to_sound_v2`), `duration_seconds` (0.5–30), and `prompt_influence` (0–1, default 0.3).
  - Output formats include `pcm_48000`, `pcm_44100` (Pro+), `opus_48000_*` and MP3 up to 192 kbps (Creator+).
  - Zero-retention mode is enterprise-only.

  — [ElevenLabs SFX API reference](https://elevenlabs.io/docs/api-reference/text-to-sound-effects/convert)
- ElevenLabs SFX pricing and licensing:
  - API rate: $0.12 per minute — [ElevenLabs API pricing](https://elevenlabs.io/pricing/api)
  - Product page: max 30 s on all plans, "Seamless looping", MP3 and WAV at 48 kHz on paid plans.
  - Generations per month: Free 50, Starter 150, Creator 605, Pro 3,000. Extra generations cost $0.03–$0.07.
  - "As long as you have a paid account, you can use our sound effects royalty-free in commercial projects." The Free plan is personal use only.
  - Output may not be used to build competing products.

  — [ElevenLabs Sound Effects](https://elevenlabs.io/sound-effects)
- Stable Audio 3.0 Small SFX is a 0.6B open-weights model intended for on-device sound effects, under the Community License (commercial use under $1M revenue). — [The Rundown](https://www.therundown.ai/tools/stable-audio-3-0)
- Practitioner assessment (June 2026):
  - ElevenLabs is best for "punchy, game-style" impacts, footsteps, UI sounds, magic and weapons.
  - Stable Audio is stronger for textured, layered sounds and ambient beds.
  - Optimizer AI targets short game SFX but trails on range.
  - Generate 3–4 takes and pick the best.
  - A generated file "is not yet a game sound". You still need to convert short effects to WAV (MP3 decode latency can delay instant sounds), trim leading silence or slow attacks, set relative volume, choose a 2D or 3D player, wire it to the event and playtest.

  — [SummerEngine (Jun 6, 2026)](https://www.summerengine.com/blog/ai-sound-effect-generator-for-games)
- Adobe Firefly sound-effect generation accepts text, reference audio or microphone input, with access by Adobe plan and credits. API availability was not confirmed. — [Magic Hour roundup (secondary)](https://magichour.ai/blog/best-ai-sound-effect-generators)
- Freesound API v2:
  - Filters use `filter=filtername:value`, numeric ranges use `[start TO end]` (e.g. `duration:[0.1 TO 0.3]`), and `type:(wav OR aiff)` is supported.
  - `license` is filterable. Allowed values are Attribution, Attribution NonCommercial and Creative Commons 0.
  - Original-quality downloads (`/apiv2/sounds/<id>/download/`) require OAuth2. Previews are lossy: MP3 at about 128/64 kbps and OGG at about 192/80 kbps.
  - Throttling is per user.
  - Descriptor filters include `bpm`, `pitch` and `note_name`.
  - There is a `gen_ai_preference` field recording uploaders' preferences on AI training.

  — [Freesound API docs](https://freesound.org/docs/api/resources_apiv2.html)
- Sonniss GDC Game Audio Bundle license:
  - Royalty-free, commercial use, "No attribution is required", unlimited projects with no expiry, and edited sounds allowed.
  - "Use for AI/ML training is strictly prohibited".
  - Sounds may not be redistributed as SFX (in libraries or asset packs), but may ship inside a finished game.
  - The archive covers 2015–2024 (about 9–48 GB per year). There was no 2025 bundle. The 2026 bundle has its own site.

  — [Sonniss GDC page](https://sonniss.com/gameaudiogdc)
- GDC 2026 bundle: reported as about 7.47 GB of SFX from 17 vendors, free. — [Rekkerd (search snippet)](https://rekkerd.org/sonniss-releases-gdc-2026-game-audio-bundle/)
- Community local generators: sfx-gen-mcp runs Stable Audio Open locally, returns WAV, needs a GPU and a gated Hugging Face license. AudioGen MCP uses Meta AudioGen on Apple Silicon. — [Glama: sfx-gen-mcp](https://glama.ai/mcp/servers/JimCline/sfx-gen-mcp); [Glama: AudioGen MCP](https://glama.ai/mcp/servers/@peerjakobsen/audiogen-mcp/blob/3e0060f6dca98c70b94c023f2136969a7692820c/README.md). Note that AudioGen weights are CC-BY-NC — [audiocraft](https://github.com/facebookresearch/audiocraft)

### Inferences
- **Recommended SFX stack:**
  - ElevenLabs SFX v2 as the primary generator: request `pcm_48000`, use `loop=true` for ambiences and engine hums, and generate 3–4 variations per event for randomization.
  - The Sonniss GDC archive as a human-recorded layer for realism (impacts, foley).
  - Freesound restricted to `license:"Creative Commons 0"` to avoid attribution bookkeeping and non-commercial contamination. Store license metadata per asset.
- The AudioGen MCP path is unsuitable for commercial shipping because the AudioGen weights are CC-BY-NC.
- Sonniss's AI-training prohibition means its sounds should not be fed into fine-tuning, such as Stable Audio LoRA or ElevenLabs finetunes. Using them as `audio-to-audio` references for a generative model is a grey area and should be avoided unless cleared.
- UI sounds (clicks, confirms, coin pickups, level-up stingers) are short, tonal and need consistent pitch and timbre across a set. Generating them in one batch with a shared prompt prefix, then normalizing and trimming, is advisable. Musical stingers might be better from the music model in the soundtrack's key.

### Gaps
- No primary info on Krotos AI products or any dedicated "game SFX" API beyond Optimizer AI (secondary mention only).
- No confirmed API for Adobe Firefly SFX, or its commercial terms for games.
- No quality benchmark comparing ElevenLabs SFX vs Stable Audio for short UI transients.
- Freesound API rate-limit numbers and API terms on commercial use of downloaded sounds were not stated on the fetched page. They are governed per-sound by the CC license.

## 3. Voice acting and dialogue: TTS, voice design, emotion, localization, and union/consent rules

### Takeaway
For agent-driven character dialogue, ElevenLabs v3 has the most complete game-relevant toolkit:
- multi-speaker Text-to-Dialogue with inline audio tags
- prompt-based Voice Design v3
- built-in spatial and reverb effects
- 70+ languages

However, it is the most expensive at roughly $100 per 1M characters. Gemini 3.8 Flash TTS (130+ languages, $9 per 1M output tokens through 2026) and Inworld TTS-2 ($25 down to $5 per 1M characters) are the cost and quality challengers for bulk localization. Cartesia Sonic 3.6 leads a September 2026 blind-preference board. PlayHT (shut down Dec 31, 2025) and Replica Studios (shut down June 30, 2025) are gone. The SAG-AFTRA 2025 Interactive Media Agreement requires informed, specific consent and usage reporting for digital replicas of performers. OpenAI's policy requires disclosing AI voices to end users.

### Cited Findings
- **ElevenLabs Text-to-Dialogue:**
  - Endpoint `POST /v1/text-to-dialogue`, default `eleven_v3`. `inputs` is a list of `{text, voice_id}` with up to 10 unique voices and about 2,000 characters total for reliable generation.
  - Supports `seed`, `previous_text`/`future_text`, request stitching, and up to 3 pronunciation dictionaries.
  - Bracketed audio tags appear inline (e.g. `[giggling]`, `[curious]`).
  - `audio_effects` covers filter presets (phone or radio), `distance`, `environment_id` reverb, background noise beds and `pan`, at no extra cost.
  - Formats: MP3, PCM/WAV at 8–48 kHz (44.1 kHz needs Pro+), and Opus.

  — [ElevenLabs Text-to-Dialogue API](https://elevenlabs.io/docs/api-reference/text-to-dialogue/convert)
- **ElevenLabs Voice Design:**
  - Endpoint `POST /v1/text-to-voice/design` with `voice_description`.
  - `model_id` is `eleven_multilingual_ttv_v2` or `eleven_ttv_v3`. `eleven_ttv_v3` also supports `reference_audio_base64` and `prompt_strength`.
  - `loudness` runs -1 to 1, where 0 is about -24 LUFS. Other params: `guidance_scale` and `seed` for reproducibility.
  - Returns previews with a `generated_voice_id`, which you save via `/v1/text-to-voice`.

  — [ElevenLabs Voice Design API](https://elevenlabs.io/docs/api-reference/text-to-voice/design)
- ElevenLabs TTS API rates per 1K characters: Flash/Turbo $0.04, Multilingual v2 $0.08, v3 $0.08. Speech-to-speech $0.12/min. Dubbing v2 $2.20/min. — [ElevenLabs API pricing](https://elevenlabs.io/pricing/api). ElevenLabs v3 is often cited for expressive narration and 70+ languages — [Haass (secondary)](https://haass.io/blog/best-tts-api-2026). One comparison puts v3 latency at 300 ms or more — [VoiceUps (secondary)](https://voiceups.com/public/best-tts-models)
- **Blind-preference leaderboard** (Artificial Analysis, read Sept 8, 2026, reported by vendor Gradium; English only):

  | Rank | Model | Elo | Price per 1M chars |
  |---|---|---|---|
  | 1 | Cartesia Sonic 3.6 | 1,282 | n/a |
  | 2 | Inworld Realtime TTS-2 | 1,252 | n/a |
  | 8 | ElevenLabs v3 Conversational | 1,210 | $50 |
  | 9 | Gemini 3.1 Flash TTS | 1,208 | $36.60 |
  | 14 | ElevenLabs Eleven v3 | 1,175 | $100 |

  The May 2026 snapshot lists OpenAI TTS-1 at $15/M and TTS-1 HD at $30/M. The page has internal inconsistencies. — [Gradium (vendor source)](https://gradium.ai/content/best-elevenlabs-alternatives-2026-tts-apis-voice-quality-price)
- **Gemini TTS:**
  - Models: `gemini-3.8-flash-tts` (130+ languages) and `gemini-3.8-flash-lite-tts` (100+), plus `gemini-3.1-flash-tts-preview` and `gemini-2.5-pro-preview-tts`.
  - Voices: 30 featured voices plus an Extended Voice Library of "hundreds".
  - Multi-speaker: up to 2 speakers per request. Custom voices must be synthesized turn by turn.
  - Style: a natural-language `style` field (e.g. "whispered urgently") and inline tags (`<laugh>`, `<short pause>`). Voice design is available.
  - Output: 24 kHz mono 16-bit WAV, or raw PCM when streaming.

  — [Gemini speech generation docs](https://ai.google.dev/gemini-api/docs/speech-generation)
- **Gemini TTS pricing:**
  - 3.8 Flash TTS: $0.50 per 1M input tokens and $9.00 per 1M audio output tokens through Dec 31, 2026, doubling to $1.00 and $18.00 from Jan 1, 2027. That is about $0.00225 per 10 s of audio.
  - 3.8 Flash-Lite: $6.00 per 1M output tokens.
  - Batch/Flex runs at half price.
  - The free tier exists, but free-tier content may be used to improve Google products.

  — [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing)
- **OpenAI TTS:**
  - Models: `gpt-4o-mini-tts` (recommended), `tts-1`, `tts-1-hd`.
  - Voices: 13, with `marin` and `cedar` recommended for quality.
  - The `instructions` parameter steers accent, emotion, intonation, impressions, speed, tone and whispering.
  - Formats: MP3, Opus, AAC, FLAC, WAV, and 24 kHz PCM. Language support is roughly Whisper's (about 60), and voices are optimized for English.
  - Custom voices require a speaker consent recording.
  - Policy: you must give "clear disclosure to end users that the TTS voice they are hearing is AI-generated and not a human voice."

  — [OpenAI TTS guide](https://developers.openai.com/api/docs/guides/text-to-speech)
- **Cartesia** (model Sonic-3.6):

  | Plan | Price | Credits/mo | Notes |
  |---|---|---|---|
  | Free | $0 | 20K | No commercial license listed |
  | Pro | $5 | 100K | Commercial license, instant cloning |
  | Startup | $49 | 1.25M | Professional cloning |
  | Scale | $299 | 8M | |

  1 credit is 1 character, and a minute of audio uses about 750–800 credits. Overage runs $38–$65 per 1M. — [Cartesia pricing](https://cartesia.ai/pricing). A roughly 40 ms time-to-first-audio is widely cited, though one source lists 90 ms. — [FutureAGI (secondary)](https://futureagi.com/blog/best-text-to-speech-providers-2026/)
- **Inworld TTS:** TTS-2 costs $25/M characters on-demand, falling to $12.50 (Growth) and "as low as $5" (Enterprise). TTS-2 Flash costs $15/M on-demand, falling to $7. Features include 200+ languages, instant and professional cloning, voice design, steering (TTS-2 only), timestamps, and a commercial license from On-Demand up. — [Inworld pricing](https://inworld.ai/pricing)
- **Hume Octave** is picked by reviewers for emotional fidelity in character work. Language coverage is narrow, with estimates of about 11 to 30+. — [Haass (secondary)](https://haass.io/blog/best-tts-api-2026); [FutureAGI](https://futureagi.com/blog/best-text-to-speech-providers-2026/). The Hume pricing page did not expose Octave pricing. — [Hume pricing](https://www.hume.ai/pricing)
- **Defunct vendors:**
  - PlayHT: Meta acquired it in July 2025 and shut the platform down on Dec 31, 2025. The API reportedly went dark earlier, and user data was deleted without export. — [TextToLab (secondary)](https://texttolab.com/blog/play-ht-shutdown-alternatives); [CognitiveFuture](https://cognitivefuture.ai/elevenlabs-vs-playht-alternatives/)
  - Replica Studios: discontinued service June 30, 2025, after failing to reach profitability. It had signed a 2023 SAG-AFTRA voice-licensing deal. — [MultiLingual](https://multilingual.com/replica-studios-shutdown-2025/)
- **SAG-AFTRA 2025 Interactive Media Agreement:**
  - Ratified July 2025 (95.04%).
  - Requires consent and disclosure before creating a digital replica, a "reasonably specific description" of intended use, and usage reports.
  - Performers can suspend consent for new material during a strike.
  - Routine processing (clarity, noise reduction, timing, pitch) is excluded.
  - A replica must be "objectively identifiable" as the performer.
  - Covers Nov 2022 to Oct 2028. Pay rises 15.17% on ratification, then 3% in each of Nov 2025, 2026 and 2027.

  — [FKKS law-firm summary](https://ipandmedialaw.fkks.com/post/102ksuq/new-sag-aftra-2025-interactive-media-agreement-approved-by-members); [Decrypt](https://decrypt.co/329479/video-game-performers-ai-consent-rules)

### Inferences
- **Recommended voice stack:**
  - ElevenLabs v3 for hero characters: Voice Design v3 to create original non-replica voices, save the `generated_voice_id`, fix the `seed`, use Text-to-Dialogue for scenes with audio tags, and use `audio_effects` for radio or distance treatments.
  - Gemini 3.8 Flash TTS or Inworld TTS-2 for high-volume barks and localization into many languages at much lower cost. Gemini's 2-speaker limit and 24 kHz mono output are fine for mobile.
  - Cartesia if real-time, low-latency runtime TTS is needed, such as live NPC chat.
- Voices built by prompt-based voice design that are not modeled on a real performer are unlikely to be "digital replicas" under the IMA definition ("objectively identifiable" as a performer). Cloning any real actor, union or not, requires written, use-specific consent, and IMA signatory studios must also report usage.
- Vendor-shutdown risk is real, as PlayHT and Replica show. An agent pipeline should cache all generated audio and voice IDs locally. It should also keep the voice-design prompt, seed and reference audio so voices can be recreated on another provider.
- The OpenAI disclosure requirement suggests adding an "AI-generated voices" credit or settings note. That is good practice regardless of vendor.
- For consistent character identity across hundreds of lines, use the same voice ID and seed, keep stability settings consistent, and use pronunciation dictionaries for fantasy names.

### Gaps
- Hume Octave 2 pricing and features could not be retrieved.
- No source for EU AI Act or app-store disclosure rules specific to AI voices in games (search budget exhausted).
- ElevenLabs v3 GA vs alpha status and per-language quality were not confirmed in this session.
- No primary source on SAG-AFTRA rules for wholly synthetic (non-replica) voices, or on the newer "AI voice" provisions beyond the IMA summaries.

## 4. Implementation: middleware vs engine-native on mobile, licensing, adaptive music, formats, loudness, and automated post-processing

### Takeaway
For an indie mobile game, engine-native audio is adequate for simple needs. Unity has Vorbis/ADPCM/PCM import and `PlayScheduled`, and Godot 4.x has `AudioStreamInteractive` for beat- and bar-synced music transitions. FMOD (free Indie tier under a $600k budget per its licensing page) or Wwise (free under a $250K budget, per older sources) add authoring tools for adaptive music, parameters and profiling. Format guidance: uncompressed or lightly compressed for short SFX (PCM/ADPCM in Unity, WAV with QOA in Godot), and Vorbis (or MP3 on mobile) streamed for music and VO. There is no official mobile loudness standard. The most cited targets are about -16 to -18 LUFS integrated for mobile and device speakers, against -24 LUFS for console (ASWG-R001), and these come from older or non-mobile sources. PyMusicLooper (MIT) automates loop-point detection and intro/loop/outro splitting.

### Cited Findings
- **FMOD licensing:** The official page (via search snippet) lists an Indie tier for projects with a development budget under $600k, at "Free or $2,000 (see note) per game". Older coverage said free use applied under $200k yearly revenue, and forum posts quote a once-per-12-months limit, with additional titles at $2,000 each. That limit is unverified for 2026. Gambling and simulation projects are reportedly excluded. — [FMOD licensing (search snippet; direct fetch returned empty)](https://fmod.com/licensing); [Game Developer (older)](https://www.gamasutra.com/audio/small-developers-and-creators-can-now-use-fmod-studio-for-free); [FitGap](https://us.fitgap.com/products/fmod)
- **Wwise licensing** (older data):
  - Indie is free up to a $250K production budget, with budget checks at Greenlight, pre-launch and every 6–12 months post-launch.
  - Pro: $7,000 for the first platform and $3,500 per additional platform, for budgets of $250K–$2M.
  - Premium: $22,000 / $15,000. Platinum: $40,000 / $20,000. These figures are as of Oct 2024.
  - Games-as-a-Service: free until launch, then a monthly revenue-based fee.

  — [Audiokinetic blog (2023)](https://blog.audiokinetic.com/free-wwise-for-indie-developers/); [GameFromScratch](https://gamefromscratch.com/wwise-now-free-for-indie-developers/); [FitGap](https://us.fitgap.com/products/wwise). The current Audiokinetic pricing page returned HTTP 403, so the 2026 terms are unconfirmed.
- **Unity 6.6 audio compression:**
  - PCM is uncompressed with no decode cost and the largest files.
  - ADPCM gives a fixed 3.5x compression with slightly more CPU than PCM, but can add artifacts on smooth music or ambience.
  - Vorbis/MP3 is the default for mobile, with a Quality slider.
  - For long files (music, dialog), lower Vorbis quality until loss is noticeable, then raise it slightly.
  - PCM and ADPCM support sample-rate reduction, and formats can be overridden per platform.

  — [Unity Manual 6.6](https://docs.unity3d.com/Manual/AudioFiles-compression.html)
- **Godot 4.7 audio import:**
  - WAV for short, repetitive SFX. Ogg Vorbis for music, speech and long SFX. On mobile and web, consider MP3 when several compressed sounds play at once, since it uses less CPU than Ogg.
  - The WAV compression default is Quite OK Audio (QOA), which beats IMA ADPCM on size and quality at slightly more CPU.
  - Ogg and MP3 support only a forward loop with a loop offset. WAV supports sample-accurate loop begin and end.
  - The BPM, Beat Count and Bar Beats import fields exist but are "currently unused".

  — [Godot docs: importing audio](https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_audio_samples.html)
- **Godot `AudioStreamInteractive`:**
  - Clips plus a transition table, for interactive music.
  - Transitions can start immediately, on the next beat, on the next bar, or at clip end. The destination can start at the same position, at its start, or at its last played position.
  - Fades are configured in beats (cross-fade or automatic). Optional filler clips play between sections, and "hold previous" lets playback return to an earlier clip.
  - Per-clip auto-advance.

  — [Godot AudioStreamInteractive](https://docs.godotengine.org/en/stable/classes/class_audiostreaminteractive.html)
- **Loudness:**
  - Sony's ASWG-R001 set -24 LUFS based on ITU-R BS.1770-3, and Microsoft and Nintendo followed. Loudness standards "not yet gained the traction among indie and mobile developers". — [Audio Media International / Rob Bridgett (Apr 2015, old)](https://audiomediainternational.com/mobile-loudness-an-adaptive-approach/)
  - The same article cites -16.2 LUFS (iTunes Soundcheck) for device-speaker playback, -18 LUFS as "Sony's Mobile target", and -16 LUFS for noisy headphone listening. It recommends adaptive loudness that switches targets by output route (speaker, headphones, AirPlay) with runtime master compression. — [Audio Media International (2015)](https://audiomediainternational.com/mobile-loudness-an-adaptive-approach/)
  - Meta's official targets are -16 LUFS for standalone Quest apps and -18 LUFS for PCVR/Rift (VR, not phones). — [Meta developer docs](https://developers.meta.com/horizon/documentation/unity/audio-loudness-meter-overview/)
  - A secondary blog suggests -16 to -20 LUFS overall with true peaks safely below 0 dB. — [Bugnet blog](https://bugnet.io/blog/how-loud-should-your-game-be)
  - ElevenLabs Voice Design's `loudness=0` corresponds to about -24 LUFS. — [ElevenLabs](https://elevenlabs.io/docs/api-reference/text-to-voice/design)
- **PyMusicLooper** (MIT, 408 stars) automatically finds the best loop points for seamless, endless music.
  - Commands: `play`, `play-tagged`, `split-audio` (exports intro/loop/outro files), `export-points` (loop points in samples), `tag` (writes loop metadata), `extend` (extends to a target length).
  - Inputs: MP3/OGG/FLAC/WAV, plus others via ffmpeg.

  — [PyMusicLooper GitHub](https://github.com/arkrow/PyMusicLooper)
- Generated SFX should be converted to WAV for short effects, because MP3 decoding adds latency for instant sounds, and leading silence should be trimmed. — [SummerEngine](https://www.summerengine.com/blog/ai-sound-effect-generator-for-games)
- MCP Audio Tweaker exposes ffmpeg batch conversion, bitrate and volume processing as MCP tools. — [Glama: MCP Audio Tweaker](https://glama.ai/mcp/servers/@DeveloperZo/mcp-audio-tweaker/blob/5d64b4f2bf16f23a1b95008ab5108ab06db855c9/README.md)

### Inferences
- **Middleware choice for an AI-agent-driven mobile pipeline:**
  - **Godot:** `AudioStreamInteractive` covers horizontal re-sequencing natively. Vertical layering can be done by running synced stem players with volume automation.
  - **Unity:** use `AudioSource.PlayScheduled` with DSP time for sample-accurate stitching, or adopt FMOD. FMOD's free Indie tier has a lower barrier than Wwise's budget audits, and is the common indie choice for adaptive music and parameter-driven SFX.
  - Middleware bank files can be generated by scripts, but automating FMOD Studio or Wwise authoring (event creation) from an agent is harder than dropping files into engine-native systems. FMOD Studio has a JavaScript scripting API and Wwise has WAAPI, though neither was verified in this session.
- **Adaptive music techniques mapped to AI tools:**
  - (a) Horizontal re-sequencing. Generate sections (explore, combat, victory stinger) at the same BPM and key, using ElevenLabs composition plans or Lyria RealTime with fixed `bpm`/`scale`. Cut to bar lengths and wire into Godot `AudioStreamInteractive` (next-bar transitions) or FMOD transition markers.
  - (b) Vertical layering. Use ElevenLabs/Suno stems, or Lyria RealTime layer renders (`only_bass_and_drums` vs full mix), all sample-aligned and loop-cut to identical lengths.
  - (c) Stingers. Short cues in the same key.
- **Suggested mobile format matrix** (combines the Unity and Godot docs):
  - Short UI and SFX (under ~1–2 s, frequent): PCM or ADPCM in Unity, WAV/QOA in Godot, decompressed on load, with the sample rate reduced to 22–32 kHz where inaudible.
  - Music and VO: Vorbis (Unity) or Ogg/MP3 (Godot), streamed. Mono for VO and most SFX, stereo for music.
- **Suggested loudness targets for mobile** (synthesis of older and non-mobile guidance; no official mobile standard found):
  - Master integrated loudness around -16 to -18 LUFS, with true peak at or below -1 dBTP (my recommendation, not sourced).
  - Normalize asset classes consistently, for example VO, music beds, and UI a few LU below SFX peaks.
  - Optionally add route-aware (speaker vs headphone) master compression, as Bridgett recommends.
- **Automated post-processing chain for an agent** (tools named from general practitioner knowledge; only PyMusicLooper and MCP Audio Tweaker were verified this session):
  - (1) Convert to 48 kHz WAV with ffmpeg.
  - (2) Trim leading and trailing silence (ffmpeg `silenceremove` or pydub `detect_leading_silence`).
  - (3) Loudness-normalize with ffmpeg `loudnorm` (EBU R128, two-pass) to per-class targets.
  - (4) For music loops: run PyMusicLooper `export-points` or `split-audio`, or use librosa beat tracking plus the known BPM to cut at bar boundaries, and apply a short crossfade at the loop seam.
  - (5) Apply short fades to SFX to avoid clicks.
  - (6) Encode to the target format (Ogg Vorbis q4–q6 for music) and write loop metadata. Godot loop offset and Unity loop points are handled per engine.

### Gaps
- I could not directly retrieve the 2026 FMOD or Wwise licensing pages (empty response and HTTP 403). Thresholds above are from a search snippet and older sources.
- No official Apple, Google or Sony mobile loudness target from 2024–2026 was found. The -18 LUFS "Sony mobile" figure comes from a 2015 article.
- Mobile output latency numbers (Android AAudio/Oboe, iOS) and iOS/Android hardware decoding guidance were not covered by the fetched Unity page.
- Unity 6 native adaptive features (e.g. Audio Random Container) were not verified in this session.
- No verified source on ffmpeg `loudnorm`, pydub or librosa specifics (search budget exhausted). They are named above from general knowledge.

## 5. MCP servers for audio tools

### Takeaway
ElevenLabs' original local MCP server (`elevenlabs/elevenlabs-mcp`, 1.5k stars) was deprecated and archived on Aug 20, 2026, in favor of a hosted, OAuth-based MCP endpoint at `https://api.elevenlabs.io/v1/mcp`. That endpoint is the best-supported audio MCP for an agent. Community MCP servers exist for Lyria (Gemini Audio MCP), Suno (via unofficial APIs), local Stable Audio Open SFX, Meta AudioGen and ffmpeg processing. All are unofficial, and several carry licensing or ToS risk.

### Cited Findings
- **elevenlabs/elevenlabs-mcp** ([GitHub](https://github.com/elevenlabs/elevenlabs-mcp)):
  - "This local MCP server is deprecated in favor of the ElevenLabs hosted MCP server" at `https://api.elevenlabs.io/v1/mcp` (OAuth, no local install). Archived Aug 20, 2026.
  - 1.5k stars, 258 forks.
  - Capabilities mentioned: agent creation, voice design, speech-to-speech, sound effects and soundscapes, speech-to-text with diarization, audio isolation, video-to-music, and music upload for inpainting.
  - Tool names: `speech_to_text`, `isolate_audio`, `speech_to_speech`, `video_to_music`, `upload_music_for_inpainting`.
  - Install via `uvx elevenlabs-mcp` with env vars `ELEVENLABS_API_KEY`, `ELEVENLABS_MCP_BASE_PATH` (default `~/Desktop`), `ELEVENLABS_MCP_OUTPUT_MODE` (files, resources or both) and `ELEVENLABS_API_RESIDENCY`.
- **Gemini Audio MCP** uses Lyria 3 models to generate SFX, soundscapes and music with BPM, key and vocal control, plus speech. It includes ffmpeg-based format conversion, crossfades and cleanup. — [Glama listing](https://glama.ai/mcp/servers/d0mpu2pamp)
- **sfx-gen-mcp** generates local SFX with Stable Audio Open and returns WAV. It needs a GPU and Hugging Face gated-license acceptance, and is part of "game-audio-kit", which bundles a music/voice MCP. — [Glama: sfx-gen-mcp](https://glama.ai/mcp/servers/JimCline/sfx-gen-mcp)
- **MCP-Suno** (lioensky) offers custom mode with lyrics, style and title, inspiration mode, continuation and instrumental output. A separate Suno MCP runs on the AceDataCloud API and needs its own token. — [Glama: MCP-Suno](https://glama.ai/mcp/servers/lioensky/MCP-Suno)
- **MCP Audio Tweaker** handles ffmpeg batch conversion, bitrate and volume changes. — [Glama](https://glama.ai/mcp/servers/@DeveloperZo/mcp-audio-tweaker/blob/5d64b4f2bf16f23a1b95008ab5108ab06db855c9/README.md)
- **AudioGen MCP** runs Meta AudioGen SFX on Apple Silicon and needs ffmpeg. — [Glama](https://glama.ai/mcp/servers/@peerjakobsen/audiogen-mcp/blob/3e0060f6dca98c70b94c023f2136969a7692820c/README.md). AudioGen weights are CC-BY-NC — [audiocraft](https://github.com/facebookresearch/audiocraft)

### Inferences
- **Recommended MCP setup for a game-audio agent:**
  - The ElevenLabs hosted MCP as the primary connection (TTS, dialogue, voice design, SFX and music, subject to hosted tool coverage).
  - A small custom MCP or CLI wrapper for Lyria (Gemini API) and Stable Audio (REST).
  - A local post-processing MCP or tool wrapping ffmpeg, PyMusicLooper and loudness normalization.
- Suno MCPs depend on unofficial or reseller APIs. Combined with Suno's download caps and ongoing litigation, they are risky for a commercial pipeline. AudioGen-based MCPs produce non-commercial output.
- Because the local ElevenLabs MCP is archived, plugin docs should not point to it as current. They should reference the hosted endpoint.

### Gaps
- I could not retrieve the hosted ElevenLabs MCP tool list. My guessed docs URL returned 404, so whether music compose and text-to-dialogue are exposed via MCP is unconfirmed.
- GitHub URLs, star counts and maintenance status of the community MCP servers were taken from Glama listings and not verified on GitHub.
- No official MCP servers were found from Google (Lyria), Stability, FMOD or Audiokinetic. This is absence of evidence given the search budget, not confirmed absence.

## 6. How top mobile games approach audio polish, and what AI still cannot do well

### Takeaway
I could not retrieve 2025–2026 primary material on specific top mobile titles' audio practices, because the search budget was exhausted. What the sources do show is that AI output is raw material, not finished game audio. Integration, timing, mixing, loudness management, and cohesive identity across a soundtrack still require deliberate engineering or human direction. Documented AI limitations relevant to polish:
- no iterative editing on Lyria 3.5
- non-deterministic outputs
- no BPM, key, stem or loop controls in most song-level APIs
- instrumental-only real-time generation
- latency for expressive TTS
- no published quality benchmarks for music

### Cited Findings
- A generated SFX file "is not yet a game sound". Trimming, format conversion, relative volume, 2D/3D routing and event wiring are manual, and "timing and mix are only verified by playing." — [SummerEngine (Jun 2026)](https://www.summerengine.com/blog/ai-sound-effect-generator-for-games)
- Lyria 3.5 music generation is single-turn: iterative editing of a generated clip is not supported, and results vary between calls even with the same prompt. BPM, key, stems and loops are not documented controls. — [Gemini API music docs](https://ai.google.dev/gemini-api/docs/music-generation)
- Lyria RealTime is instrumental only and experimental. Changing key (`scale`) requires a stop/play or context reset, so a live key change cannot be seamless. — [Lyria RealTime docs](https://ai.google.dev/gemini-api/docs/realtime-music-generation)
- ElevenLabs publishes no head-to-head music-quality benchmarks, so quality claims rest on demos. Music credits share a pool with voice, so heavy music use competes with VO budgets. — [invideo](https://invideo.io/blog/elevenlabs-music-ai-generator/)
- ElevenLabs v3 latency is reported at 300 ms or more. — [VoiceUps (secondary)](https://voiceups.com/public/best-tts-models). TTS leaderboards measure English-only blind preference, not pronunciation or latency. — [Gradium](https://gradium.ai/content/best-elevenlabs-alternatives-2026-tts-apis-voice-quality-price)
- Mobile audio polish practices recommended by an audio director (Rob Bridgett, 2015):
  - Route-dependent loudness targets (speaker, headphones, mirroring).
  - Runtime compression for noisy environments.
  - Smooth blending between target states.
  - Mix at the middle target first, then tune for the other states.

  — [Audio Media International (2015, old)](https://audiomediainternational.com/mobile-loudness-an-adaptive-approach/)
- Godot's interactive-music system relies on beat- and bar-quantized transitions and filler clips, which require musically consistent tempo and bar lengths across clips. — [Godot AudioStreamInteractive](https://docs.godotengine.org/en/stable/classes/class_audiostreaminteractive.html)
- ElevenLabs' terms make the user responsible for reviewing Output for clearance, and prohibit artist-name prompts. "Sound-alike" direction to a reference artist is therefore not available as a control. — [Eleven Music Terms](https://elevenlabs.io/music-terms)

### Inferences
- **What AI does not yet do well** (synthesized from the limitations above):
  - (1) Precise sync, meaning sample-accurate loop seams, bar-exact section lengths, and hitting specific frames for cutscenes or animations. This needs post-processing, or a human cutting to grid.
  - (2) Cohesive soundtrack identity across dozens of cues. Outputs are non-deterministic and iterative editing is limited. Mitigations: a fixed "style bible" prompt prefix, fixed BPM and key families, seeds, ElevenLabs Music Finetunes or audio-reference steering, and Stable Audio LoRA.
  - (3) Consistent timbre across UI-sound sets.
  - (4) Mixing and loudness balance in context.
  - (5) Truly interactive scoring in shipped builds. Lyria RealTime is the only real-time API and is experimental, instrumental only, and needs a network connection, which matters for offline mobile play.
- **Proposed agent workflow that compensates for these limits:**
  - (1) Define an audio style bible: genre palette, BPM and key per game state, loudness targets.
  - (2) Generate many candidates per cue.
  - (3) Auto-QC: measure LUFS, true peak, duration, leading silence, and loop-seam discontinuity (RMS or spectral difference across the seam).
  - (4) Use human or LLM-judged A/B selection against reference cues.
  - (5) Assemble adaptive structures in-engine.
  - (6) Playtest on-device through the phone speaker and headphones.
- **Licensing hygiene as part of "polish":**
  - Keep a manifest per asset: tool, model version, plan tier at generation time (ElevenLabs output rights follow the plan in effect at creation), prompt, seed, date, and license.
  - For Freesound, record CC0 status.
  - For Sonniss, record bundle year.

### Gaps
- No primary 2024–2026 sources were retrieved on how specific top-grossing mobile games (e.g. Supercell titles, Monument Valley, Genshin mobile, Candy Crush) handle audio: interviews, GDC talks, A Sound Effect articles. The search budget was exhausted before these queries ran.
- No r/GameAudio or GDC 2025–2026 community sentiment on AI audio adoption was gathered.
- No data on player perception of AI music or voice in mobile games, or on app-store policies on AI audio disclosure.
