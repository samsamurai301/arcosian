# Model Landscape 2026 (Volatile)

This file surveys the AI music, SFX and voice services relevant to a mobile game pipeline as of October 2026, with capabilities, reported prices, licence terms, revenue-threshold traps, vendors to exclude and MCP options. Everything here is volatile: model names, prices and terms change monthly, and several figures come from secondary sources or conflict between sources. Use it to shortlist; verify the vendor's own current page before committing money or shipping output. The stable guidance (how to choose, what to record) is in `SKILL.md` and `references/generation-pipelines.md`.

## Contents
1. How to read this file
2. Selection rules that outlast the numbers
3. Volatile facts (as of Oct 2026 — verify): music
4. Volatile facts: SFX and libraries
5. Volatile facts: voice
6. Volatile facts: middleware and implementation licences
7. Excluded or avoid list
8. Revenue-threshold traps
9. MCP and tooling options
10. Recommended stacks
11. Pre-commit licence checklist
12. Unknowns

## 1. How to read this file

- Dollar figures are per the cited page at research time and are reported, not guaranteed. Where sources conflict, both are noted.
- "Secondary" means a blog or aggregator, not the vendor.
- Stable decision rules are in section 2; they remain true when prices move.
- Source URLs appear next to facts. Cite original sources in manifests, not this file.

## 2. Selection rules that outlast the numbers

1. **Licence before quality.** A cue you cannot ship is worth nothing. Confirm game use, commercial use, revenue and company-size caps, attribution, and output ownership for your plan tier.
2. **API and automation.** An agent pipeline needs an official API with predictable limits. Consumer web apps with download caps, walled gardens or only unofficial wrappers are unsuitable for production automation.
3. **Control.** For music: section-level structure, instrumental-only flag, stems, tempo and key control, audio steering. For SFX: duration, loop flag, output format, seeds. For voice: voice design, audio tags or style control, consistent voice ids.
4. **Training-data provenance.** Prefer services trained on licensed data, and avoid models whose weights are non-commercial.
5. **Offline shippability.** The shipped game should contain files, not API dependencies.
6. **Plan tier at generation time** can govern output rights permanently; record it.
7. **Disclosure and watermarking.** Some outputs are watermarked or tagged as AI. This is imperceptible but matters for store disclosure.

### Capability matrix (reported, verify; blank means not documented in research)
| Service | Official API | Sections or plan | Stems | Loop flag | Instrumental | Real time | Open weights |
|---|---|---|---|---|---|---|---|
| ElevenLabs Music | yes | yes (composition plans) | reported, tier-dependent | no | flag | streaming generation marketed | no |
| Lyria (Gemini API) | yes | timestamp ranges in prompt | no | no | via prompt | RealTime variant (experimental) | no |
| Stable Audio 2.5 / 3.0 | yes | multi-part structure | no | no | yes | no | 3.0 Small and Medium |
| Suno | no | n/a | caps apply | n/a | n/a | no | no |
| Udio | no | n/a | restricted | n/a | n/a | no | no |
| MusicGen family | self-host | no | no | no | yes | no | yes, non-commercial |
SFX: ElevenLabs offers a loop flag and 0.5-30 s duration; Stable Audio SFX is open-weights on-device (revenue-gated licence).

### Spot-check protocol before committing to a service
Spend a small, capped amount (for example under the price of a coffee) to test, and record the results in the manifest:
1. Generate the same 3 briefs (one loop, one stinger, one SFX) with 5 candidates each.
2. Measure BPM drift, key adherence, loop-ability (cut at bars, check seam), loudness spread, and silence at head.
3. Count usable candidates out of 5 per brief; below 2 of 5 means high regeneration cost.
4. Check that returned files are the format and sample rate promised (PCM vs MP3, 44.1 vs 48 kHz).
5. Re-read the licence page and save a dated copy.
6. Log cost per usable asset, not per call; use that for budgeting.

## 3. Volatile facts (as of Oct 2026 — verify): music

### ElevenLabs Eleven Music (v2)
- Model id `music_v2`, endpoint `POST https://api.elevenlabs.io/v1/music`, SDK `music.compose`; track length 3 s to 10 min via `music_length_ms`. Source: https://elevenlabs.io/eleven-music-api
- Composition plans: named sections with positive and negative styles, section duration (3 s to 2 min) and lyrics; plans and a plain text prompt are mutually exclusive; `force_instrumental` guarantees no vocals (per a secondary source, https://invideo.io/blog/elevenlabs-music-ai-generator/).
- Stems and editing are listed on the self-serve tier; stem counts per tier were not confirmed (search snippet only suggested 2, 4 or up to 6). Inpainting is listed as Enterprise on the product page while a secondary source describes it as a general v2 feature: conflicting. Verify.
- Outputs up to 44.1 kHz; formats MP3 (up to 192 kbps), PCM (up to 48 kHz) and Opus; PCM 44.1 kHz needs Pro or above. Source: https://elevenlabs.io/eleven-music-api
- Reported API price: about $0.15 per minute. Source: https://elevenlabs.io/pricing/api
- Training data: licensed stems and music with named partners among indie labels and publishers (secondary). Music Finetunes train a custom style from roughly 5-10 minutes of your own audio; a roughly 30 s audio reference can steer (secondary).
- **Game licence terms** (Eleven Music Terms): commercial use is permitted except film, TV, radio and "Studio Games" on most plans; only the Enterprise Music plan permits all uses. An "Indie Game" is excluded from the Studio Game definition if both hold: the game earned under $500,000 since first commercial release, and the developer earned under $1,000,000 from all games in its latest financial year (net of platform fees, including affiliates). If a game stops qualifying you have 60 days to move to a qualifying plan; copies distributed before the deadline may continue to be used. Source: https://elevenlabs.io/music-terms
- Other terms: the Free plan requires attribution; lower tiers are "individual use only"; Scale is limited to entities under 10 employees and Business under 50; output stays under the plan in effect at creation; prompting with artist names, song titles or label names is prohibited; building a third-party music library from output is prohibited; you are responsible for clearance. Source: https://elevenlabs.io/music-terms
- Conflict on the Free tier: the API pricing page says commercial use licensing on Starter and above; the terms text lists Free with attribution as permitted. Do not rely on Free for shipping.

### Google Lyria (Gemini API, Vertex AI)
- Gemini API models: a 30 s clip model (MP3), and a longer-form model producing "a couple of minutes" as MP3 or WAV; stereo 44.1 kHz; text plus up to 10 images as input; supports lyrics tags and timestamp structure; instrumental via prompt; no documented BPM, key, stems or loop controls; single-turn, no iterative editing; results vary between calls; all audio carries a SynthID watermark. Source: https://ai.google.dev/gemini-api/docs/music-generation
- Reported price: $0.08 per song for the longer-form and the Pro preview models, $0.04 for the clip model; no free tier. Source: https://ai.google.dev/gemini-api/docs/pricing
- **Lyria RealTime** (experimental): WebSocket streaming with weighted prompts changeable mid-stream, `bpm` 60-200, `density` and `brightness` 0-1, `scale` enums, `mute_bass`, `mute_drums`, `only_bass_and_drums`, `seed`; raw 16-bit PCM stereo; instrumental only; always watermarked; price not stated; changing `scale` needs a context reset so key changes cannot be seamless. Source: https://ai.google.dev/gemini-api/docs/realtime-music-generation
- A Vertex-hosted older instrumental model is GA at 30 s, 48 kHz WAV; Vertex per-song price and whether Google Cloud's gen-AI indemnification covers Lyria were not verified. Source (secondary): https://invideo.io/blog/lyria-ai-music-generator/

### Stability AI Stable Audio
- Stable Audio 2.5: tracks up to 3 minutes, text-to-audio, audio-to-audio, inpainting, trained on a licensed dataset; available via the Stability API and partner hosts. Source: https://stability.ai/news-updates/stability-ai-introduces-stable-audio-25-the-first-audio-model-built-for-enterprise-sound-production-at-scale
- Stable Audio 3.0 (secondary review): a Small SFX model (0.6B, open weights), a Small (0.6B, music up to 2 min), a Medium (2B, up to 6:20, open), and a Large (API or enterprise only; reported at 26 credits, about $0.26, per generation); adds multi-segment inpainting, causal continuation and LoRA training for Small and Medium. Open weights are under the Stability Community License: commercial use requires registration and attribution and is reported as allowed only below $1M annual revenue, above which an enterprise licence applies. Outputs are owned by the user as between user and Stability, with no non-infringement guarantee. Source: https://www.therundown.ai/tools/stable-audio-3-0
- Price (checked against Stability's API reference on 2026-10-20): the Stable Audio 3 text-to-audio endpoint (`POST /v2beta/audio/stable-audio/text-to-audio`, asynchronous: returns an id, then poll `GET /v2beta/audio/results/{id}`) costs a flat 8 credits, about $0.08, per generation. Source: https://docs.stability.ai/api-reference/stable-audio/text-to-audio.md. Older reviews quoted 20 credits for 2.5 and 26 for Large; treat those as outdated. The studio-gateway uses this endpoint for `audio_music` and `audio_sfx` with `provider: stability`.

### Suno and Udio (do not automate)
- Suno has no self-serve public API; community wrappers are unofficial. Consumer plans reported: Free (no commercial rights, no downloads), Pro (commercial use, limited monthly downloads, limited stem types), Premier (higher caps). Download caps reportedly enforced from Sept 2026, with stems counting against a song's download. Sources: https://suno.com/pricing, https://www.mindstudio.ai/blog/suno-v6-pricing-download-limits (secondary)
- Litigation: the RIAA sued both on June 24, 2024; Universal settled with Udio in late Oct 2025 and Warner settled with both in Nov 2025; as of May 2026 UMG and Sony v. Suno and Sony v. Udio were still active with no fair-use ruling. Source: https://dynamoi.com/learn/ai-music-distribution/ai-music-copyright-cases-timeline (secondary, dated May 2026); sources disagree by a couple of days on the Udio settlement date.
- Udio's post-settlement platform is described as a walled garden with restricted downloads. Source: https://www.digitalmusicnews.com/2025/10/29/umg-udio-deal-everything-we-know/

### Others
- Meta AudioCraft: code MIT, but MusicGen, AudioGen, MAGNeT and JASCO weights are CC-BY-NC 4.0 (non-commercial). Source: https://github.com/facebookresearch/audiocraft
- Mubert API requires contacting sales; Beatoven shows "API available" without a found rate card; Soundraw API access reported as none; AIVA copyright transfer reported only on its top plan with a conflicting source. Sources (secondary): https://resources.rework.com/tools/ai-tools/best-ai-music-generators-2026, https://tooliverse.ai/tools/aiva, https://vantaige.io/ai-tool/aiva
- Not researched: MiniMax Music, Mureka, ACE-Step, Klay. Do not assume anything about them.

## 4. Volatile facts: SFX and libraries

### ElevenLabs Sound Effects
- Endpoint `POST https://api.elevenlabs.io/v1/sound-generation`; params `text`, `loop` (only with the v2 text-to-sound model), `duration_seconds` 0.5-30, `prompt_influence` 0-1 (default 0.3); formats include `pcm_48000`, `pcm_44100` (Pro and above), Opus and MP3. Source: https://elevenlabs.io/docs/api-reference/text-to-sound-effects/convert
- Reported API price about $0.12 per minute. Paid accounts may use sound effects royalty-free in commercial projects; Free is personal use only; output may not be used to build competing products. Sources: https://elevenlabs.io/pricing/api, https://elevenlabs.io/sound-effects

### Stable Audio for SFX
- Stable Audio 3.0 Small SFX is an open-weights on-device model under the Community License (revenue-gated, see above). Practitioners describe Stable Audio as stronger for textured ambient beds and ElevenLabs as stronger for punchy game-style hits (single secondary source, June 2026): https://www.summerengine.com/blog/ai-sound-effect-generator-for-games

### Human-recorded libraries
- **Sonniss GDC Game Audio Bundles**: royalty-free, no attribution, unlimited projects, edits allowed; **use for AI or ML training is prohibited**; sounds may ship inside a finished game but not be redistributed as SFX libraries. Do not use them for fine-tunes or LoRA, and avoid them as reference audio for generators unless cleared. Source: https://sonniss.com/gameaudiogdc
- **Freesound API**: filter by licence (restrict to Creative Commons 0 to avoid attribution and non-commercial contamination), filter by duration and type; original-quality downloads need OAuth2; previews are lossy; a per-sound `gen_ai_preference` field records uploader AI-training preferences. Source: https://freesound.org/docs/api/resources_apiv2.html

### Local and community generators
- Local Stable Audio Open servers need a GPU and gated licence acceptance; AudioGen-based servers use CC-BY-NC weights and are unsuitable for shipping. Sources: https://glama.ai/mcp/servers/JimCline/sfx-gen-mcp, https://github.com/facebookresearch/audiocraft

## 5. Volatile facts: voice

### ElevenLabs
- Text-to-Dialogue: `POST /v1/text-to-dialogue`, default model `eleven_v3`; `inputs` of `{text, voice_id}` with up to 10 unique voices and about 2,000 characters for reliable generation; inline audio tags in brackets; `seed`, context text and request stitching; `audio_effects` for phone, radio, distance and reverb. Source: https://elevenlabs.io/docs/api-reference/text-to-dialogue/convert
- Voice Design: `POST /v1/text-to-voice/design` with `voice_description`; models include a v3 design model with optional reference audio; `loudness` -1 to 1 (0 is about -24 LUFS); `seed` and `guidance_scale`; returns previews with a `generated_voice_id` to save. Source: https://elevenlabs.io/docs/api-reference/text-to-voice/design
- Reported API rates per 1K characters: Flash/Turbo $0.04, Multilingual v2 $0.08, v3 $0.08. Source: https://elevenlabs.io/pricing/api. Latency for v3 reported at 300 ms or more by a secondary source, so unsuited to live NPC chat.

### Google Gemini TTS
- Models include a Flash TTS (130+ languages) and Flash-Lite TTS (100+); 30 featured voices plus an extended library; up to 2 speakers per request; natural-language style direction and inline tags; output 24 kHz mono 16-bit WAV. Source: https://ai.google.dev/gemini-api/docs/speech-generation
- Reported price: $9 per 1M audio output tokens through Dec 31, 2026, rising to $18 from Jan 1, 2027; batch at half price; free-tier content may be used to improve Google products. Source: https://ai.google.dev/gemini-api/docs/pricing

### OpenAI TTS
- Models `gpt-4o-mini-tts`, `tts-1`, `tts-1-hd`; an `instructions` parameter steers delivery; custom voices need a speaker consent recording; policy requires clear disclosure to end users that the voice is AI-generated. Source: https://developers.openai.com/api/docs/guides/text-to-speech

### Cartesia
- Sonic 3.6; plans from a free tier without a commercial licence to a $5 Pro tier with commercial licence; one credit is one character, roughly 750-800 credits per minute of audio; time to first audio widely cited around 40 ms (one source says 90 ms). Sources: https://cartesia.ai/pricing, https://futureagi.com/blog/best-text-to-speech-providers-2026/ (secondary)

### Inworld
- TTS-2 reported at $25 per 1M characters on demand, lower on higher tiers; a Flash variant is cheaper; 200+ languages; cloning, voice design, steering; commercial licence from the on-demand tier. Source: https://inworld.ai/pricing

### Quality rankings
- An English-only blind-preference leaderboard (Artificial Analysis, reported by a vendor) in Sept 2026 ranked Cartesia Sonic 3.6 first and Inworld TTS-2 second, with ElevenLabs v3 variants lower. Such boards measure English preference, not pronunciation across languages, latency or consistency; use for shortlisting only. Source: https://gradium.ai/content/best-elevenlabs-alternatives-2026-tts-apis-voice-quality-price (vendor, internal inconsistencies).
- Hume Octave is reported for emotional fidelity with narrow language coverage; pricing not retrieved. Source: https://www.hume.ai/pricing

### Union and consent
- The SAG-AFTRA 2025 Interactive Media Agreement requires consent and disclosure for digital replicas, a reasonably specific description of use and usage reports; routine processing is excluded; a replica must be objectively identifiable as the performer. Sources: https://ipandmedialaw.fkks.com/post/102ksuq/new-sag-aftra-2025-interactive-media-agreement-approved-by-members, https://decrypt.co/329479/video-game-performers-ai-consent-rules
- Wholly synthetic voices not modelled on a performer are unlikely to be digital replicas under that definition, but no primary source on non-replica synthetic voices was found; get counsel for union contexts.

## 6. Volatile facts: middleware and implementation licences

See `skills/audio-direction/references/music-and-sfx-systems.md` for the FMOD and Wwise licensing notes. Current pages were inaccessible during research; thresholds are unconfirmed.

## 7. Excluded or avoid list

| Vendor or tool | Reason | Source |
|---|---|---|
| Suno | No official API, download caps, unresolved litigation with some labels | sections above |
| Udio | Walled garden, restricted downloads | section 3 |
| MusicGen, AudioGen, MAGNeT, JASCO weights | Non-commercial licence | https://github.com/facebookresearch/audiocraft |
| PlayHT | Shut down Dec 31, 2025 (reported); do not build on it | https://texttolab.com/blog/play-ht-shutdown-alternatives (secondary) |
| Replica Studios | Discontinued June 30, 2025 | https://multilingual.com/replica-studios-shutdown-2025/ |
| Unofficial Suno wrappers and reseller APIs | Terms-of-service and reliability risk | https://github.com/rhdeck/suno-api |
| Sonniss content as ML training or fine-tune data | Licence prohibits | https://sonniss.com/gameaudiogdc |
| Local ElevenLabs MCP server | Archived Aug 2026, superseded by hosted MCP | https://github.com/elevenlabs/elevenlabs-mcp |
Re-check each before relying on this list: status changes.

## 8. Revenue-threshold traps

| Trap | What happens | Mitigation |
|---|---|---|
| Per-game revenue cap in a music licence (reported $500,000 per game) | Game stops qualifying; short window to move plans | Track revenue; budget the enterprise tier; ship fixed files before expiry where terms allow |
| Per-developer annual revenue cap (reported $1,000,000 across games) | Applies to the whole company, including affiliates | Aggregate across titles; forecast |
| Employee-count caps on plans | Plan ineligible as you grow | Check headcount at each hiring step |
| Open-weights community licence capped by annual revenue (reported $1M) | Needs an enterprise licence above | Log registration; plan migration |
| Plan tier locked at generation | Downgrade or cancel does not change old output rights, but new output follows new plan | Generate on the right plan up front |
| Free plan attribution | Missing credit breaches terms | Do not ship Free-tier output unless the terms clearly allow, and add attribution |
| Middleware budget checks (FMOD, Wwise) | Free tier ends when budget crosses a line | Check at each milestone |
| Currency and "net of platform fees" definitions | Easy to miscalculate | Keep the calculation sheet with source figures |
Assign an owner and a calendar reminder for each threshold; the compliance pre-flight (`arcosian:compliance-officer`) should read the manifest for tier and date.

## 9. MCP and tooling options

- ElevenLabs: a hosted OAuth MCP endpoint at https://api.elevenlabs.io/v1/mcp replaced the archived local server; whether music and dialogue are exposed there was unconfirmed. Source: https://github.com/elevenlabs/elevenlabs-mcp
- Community MCP servers exist for Lyria-based generation, Stable Audio Open SFX, ffmpeg batch conversion, Suno (unofficial) and AudioGen (non-commercial weights); all unofficial, with licensing or terms risk; verify before use. Sources: https://glama.ai/mcp/servers/d0mpu2pamp, https://glama.ai/mcp/servers/@DeveloperZo/mcp-audio-tweaker/blob/5d64b4f2bf16f23a1b95008ab5108ab06db855c9/README.md
- Recommended: use the plugin's `studio-gateway` audio tools (budgets, provenance), a thin REST wrapper for providers without MCP, and the local `audio_post.py` for post.
- PyMusicLooper (MIT) detects loop points and splits intro, loop, outro. Source: https://github.com/arkrow/PyMusicLooper

## 10. Recommended stacks

| Scenario | Music | SFX | Voice | Notes |
|---|---|---|---|---|
| Indie, under the indie caps, mobile casual | Plan-based music API with stems | Text-to-SFX API plus CC0 library layer | Voice design for heroes, cheaper multilingual TTS for barks and localization | Track the caps |
| Above caps or premium | Enterprise music licence or human composer | Same plus recorded foley | Human cast for heroes | Budget the licence |
| Prototype and exploration only | Cheapest official API; real-time generator for experiments | Local open-weights SFX if licence allows | Any, labelled prototype | Do not ship prototypes |
| Hard offline, zero cloud policy | Self-hosted open-weights within licence limits | Self-hosted | Human cast | Check revenue cap on weights |

## 11. Pre-commit licence checklist

- [ ] Plan tier and plan terms saved (URL, date, PDF or screenshot).
- [ ] Game-use clause read, including any "Studio Game" or genre exclusions.
- [ ] Revenue and headcount thresholds written down with owner.
- [ ] Attribution requirements met.
- [ ] Output ownership statement noted; AI-copyright limits understood.
- [ ] Prohibited prompt content (artist names) respected.
- [ ] Disclosure plan (credits, store forms).
- [ ] No restricted libraries used as training or reference data.
- [ ] Cost estimate within budget.

## 12. Unknowns

Items not verified in research: exact stem counts per tier; whether Eleven Music stems and inpainting are API-accessible on self-serve plans; FMOD and Wwise 2026 terms; hosted ElevenLabs MCP tool list; store and EU rules for AI voice disclosure; quality benchmarks for music models; loop quality in practice for any service. Treat each as open and test with a small paid sample.

## 13. Cost estimation worked example

Use reported rates only as order-of-magnitude inputs and recompute from the live price page.

```
music:   cues x candidates_per_cue x avg_minutes x price_per_minute
sfx:     events x variants x takes_per_variant x avg_seconds/60 x price_per_minute
voice:   lines x avg_characters x takes x price_per_character
total  = (music + sfx + voice) x 1.5      # reserve for retries and style-lock rounds
```
Example shape: 6 music cues x 8 candidates x 2 minutes at a reported $0.15 per minute is about $14; 40 SFX events x 4 variants x 3 takes x 2 s at a reported $0.12 per minute is about $1.90 of raw generation; 300 bark lines of 40 characters x 2 takes at a reported $0.08 per 1,000 characters is about $1.90. The numbers show that generation is cheap next to licence tier choices, subscription minimums and, above all, human review time. Log actual spend through the budget ledger so estimates improve.
