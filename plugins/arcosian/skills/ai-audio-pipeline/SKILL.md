---
name: ai-audio-pipeline
description: How to generate, post-process and QC game audio with AI: music, SFX and voice service landscape (licences, revenue-threshold traps, excluded vendors), composition plans, loop and stem engineering, SFX sets, voice design, and audio_post.py normalize/trim/loop/convert/qc. Use when asked "which AI music tool", "generate game music", "make this loop", "generate SFX", "AI voice lines", "check loudness" or "is this licence safe".
---

# AI Audio Pipeline

AI audio output is raw material, not game audio. A generated file is not yet a game sound: it needs trimming, loop engineering, loudness normalization, format conversion, provenance and a listen on a phone. This skill is the generation and post layer. Creative decisions (palette, key, adaptive model, mix targets) come from `audio-direction`; the end-to-end command is `audio-production`.

## What this skill gives you

- A service landscape for music, SFX and voice with licence and revenue-threshold traps, and the vendors to exclude (volatile: verify before relying).
- Generation recipes: composition plans, loop engineering, stems and adaptive sets, SFX variation sets and layering, voice design and localization, prompt templates.
- The post chain with `audio_post.py` (normalize, trim, loop, convert, qc) and a QC checklist with pass criteria.
- A provenance discipline: what to record per asset so licences can be audited later.
- Honest limits: what current generators cannot do and how to compensate.

## Core models

**1. Generate, then engineer.** The pipeline is: brief (from the audio bible), generate many candidates, auto-QC, human select, post-process, in-engine test on device, manifest. Generation is the cheap step; selection and engineering are where quality is made.

**2. Match the service to the job, not the other way round.**

| Job | Pick by | Typical choice (verify) |
|---|---|---|
| Structured music with sections | Plan-based control, instrumental flag, stems, clear game licence | A service with composition plans and stems |
| Cheap ideation and alternates | Price per song, no loops needed | A low-cost official API |
| Real-time adaptive prototypes | Live tempo, key, density controls | Experimental real-time API (R&D only) |
| Instrumental beds, continuation, self-hosting | Open weights or inpainting | Stability audio models (licence has revenue limits) |
| SFX and UI sounds | Short clips, loop flag, 48 kHz output | A text-to-SFX API plus a human-recorded library layer |
| Hero voices | Voice design, audio tags, dialogue | A high-expressiveness TTS |
| Bulk barks and localization | Price per character, language coverage | A cheaper multilingual TTS |

**3. Licence is part of the spec.** Terms can depend on plan tier at generation time, your game's revenue, your company size, and the type of game. Revenue-threshold clauses can force an upgrade mid-life. Record plan tier, model version and date for every asset.

**4. No official music API documents a native seamless-loop mode.** Loops must be engineered (structure the request, cut at bar lines using known BPM, crossfade, or detect loop points afterwards). See `references/generation-pipelines.md`.

**5. Determinism is weak.** Outputs vary between calls even with the same prompt. Fix seeds where supported, keep a fixed prompt prefix, generate sets together, and accept that you will keep 1 in 3 to 1 in 10 candidates.

**6. Purely AI-generated music may not be copyrightable (reported US guidance).** Human arrangement and editing strengthens any claim. A paid licence grants usage rights, not copyright. Do not promise exclusivity in marketing.

## Decision procedures

### A. Set up the audio pipeline for a project
1. Read the audio bible (`audio-direction`) and the cue list; compute counts per class.
2. Pick services per job with `references/model-landscape-2026.md`; check each licence against the game's expected revenue and the company's size now and at a 10x scenario.
3. Confirm credentials arrive via environment variables from plugin `userConfig`; never write keys into files. Prefer the studio-gateway tools with budgets and provenance (see `audio-production`).
4. Set a budget in `.gamestudio/budget.json` terms: estimated candidates times unit price, plus 50 percent reserve.
5. Run a style-lock round: one music cue, one SFX set, one voice line. Human approval before bulk.
6. Generate, post, QC, manifest, import.

### B. Pick a music service (decision table)
| Question | Answer | Action |
|---|---|---|
| Is the game likely to exceed any service's indie revenue cap? | Yes | Choose a service whose licence has no cap for your tier, or plan the upgrade now |
| Is a stem export needed? | Yes | Use a service that supplies stems; verify availability on your plan |
| Need exact structure? | Yes | Use composition-plan style control, not a single prompt |
| Need offline adaptive music? | Yes | Pre-render sections and stems; do not depend on a live API in the shipped game |
| Tempted by a consumer-only tool with no API? | Yes | Exclude it (see landscape: download caps, litigation, walled gardens) |

### C. Make a loop
1. Request structure: "steady loop body, no ending, no fade" at a known BPM; generate 20-40 percent longer than the loop.
2. Measure real BPM (do not trust the prompt); if off by more than about 0.5 percent, regenerate or time-correct.
3. Cut a whole number of bars with `audio_post.py loop --bpm N --bars N --xfade X`.
4. `audio_post.py normalize`, then `convert --format ogg`, then in-engine seam test on device.
See `references/post-and-qc.md`.

### D. Build an SFX set
1. Write the event ladder and variant counts (from `audio-direction`).
2. Use a shared prompt prefix for the family; generate 3-4 takes per variant slot; select similar-length, similar-loudness takes.
3. Layer with a recorded library layer if realism matters; check licences of the library.
4. Trim head silence, fade tails, normalize per class, export WAV masters, then ship format.

### E. Generate voice
1. Voice brief per character; create a synthetic voice by design, save the voice id and seed.
2. Generate barks as sets with fixed settings; generate hero lines scene by scene with context text.
3. Localize with a language-capable model; native-speaker review per language.
4. QC loudness per line, trim silence, disclose AI voices (credits, settings, store form).

### F. QC and release
1. `audio_post.py qc --json` for every shipped file; fail the build on loudness, true peak, clipping or DC offset failures.
2. Human listening checklist on phone speaker and headphones.
3. Manifest complete: provider, model, plan tier, prompt id, seed, date, licence, cost, reviewer.
4. Licence watch: record revenue-threshold clauses with dates and an owner.

## Mobile specifics

- Ship compressed derivatives, keep 48 kHz WAV masters out of the build.
- Offline play is the norm: never call a generation API from the shipped client for core audio. Real-time generators need a network and are experimental; treat as prototyping.
- Voice lines add download size; consider per-language packs fetched on demand.
- Phone speakers cut low frequencies: judge AI music and SFX there before approving.
- Generated SFX files come as MP3 by default on some services; request PCM or WAV for short effects to avoid decode latency.

## Anti-patterns

| Anti-pattern | Detect by | Fix |
|---|---|---|
| Using a consumer tool with no API and download caps for production | Manual downloads, cap warnings | Pick a service with API access and a clear game licence |
| Ignoring revenue thresholds | Licence says "Studio Games excluded" past a revenue figure | Record the thresholds, plan the upgrade |
| Non-commercial weights shipped | Model card says non-commercial | Do not ship their output |
| Cloning a real voice | Reference sample is a person | Synthetic design or signed consent |
| Prompting with artist or song names | Prompt contains them | Describe attributes instead; some terms forbid it |
| Trusting the BPM in the prompt | Loop seam drifts | Measure; cut at bar lines |
| Normalizing loops dynamically | Level pumps at seam | Linear normalization, same gain across stems |
| No provenance | Asset without manifest entry | Block promotion to approved |
| Training on restricted libraries | A library's terms prohibit ML use | Keep those out of fine-tunes and reference audio |
| Claiming a cue sounds good | Agent has no ears | Report measurements; require human sign-off |

## Using the ontology

- Assets are recorded in the asset manifest (`${CLAUDE_PLUGIN_ROOT}/scripts/schemas/asset-manifest.schema.json`): provider, model, prompt, seed, references, licence, cost, status; approved or final entries need an approver and a licence. Spend goes in the budget ledger (`budget.schema.json`).
- Validate with `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_json.py` against these schemas; use `gs.py` for project state.
- Post and QC: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/audio_post.py normalize|trim|loop|convert|qc`. Self-test: `audio_post.py --selftest`.
- Agents: `arcosian:audio-director` (direction), `arcosian:compliance-officer` (licence and disclosure).

## Reference library

| File | Contains | Read when |
|---|---|---|
| `references/model-landscape-2026.md` | Music, SFX and voice services, licences, revenue-threshold traps, excluded vendors, MCP notes (volatile) | Choosing providers or checking a licence |
| `references/generation-pipelines.md` | Composition plans, loop engineering, stems, adaptive sets, SFX sets and layering, voice design and localization, prompt templates | Planning or running generation |
| `references/post-and-qc.md` | `audio_post.py` usage, recipes, QC checklist and thresholds, provenance | Post-processing and release checks |

## Related skills

- `audio-direction` - what the game should sound like and how audio behaves in play.
- `audio-production` - the command that runs this pipeline with checkpoints.
- `ai-asset-pipeline` - the sibling pipeline for visual assets, same gateway and manifest.
- `legal-ethics` - AI disclosure, consent, licences.
- `mobile-performance` - audio memory and CPU budgets.
- `accessibility-localization` - captions and localized VO.
