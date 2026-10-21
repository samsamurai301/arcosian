---
name: audio-production
description: Runs the music, SFX and voice pipeline for a mobile game - audio bible, cue list, generation via studio-gateway audio tools, audio_post.py normalize/loop/convert/qc, engine implementation with buses and adaptive music, QC and licence revenue thresholds. Use when the user says "make the music", "add sound effects", "generate voice lines", "loop this track", "check loudness" or "audio pass".
---

# Audio Production

## When to use
Whenever audio is designed, generated, processed or wired into the game. Theory lives in `audio-direction` and `ai-audio-pipeline`; delegate creative direction to `arcosian:audio-director`, licence questions to `arcosian:compliance-officer`, engine wiring to `arcosian:godot-engineer` or `arcosian:unity-engineer`.

## Inputs
Optional `$ARGUMENTS`: a cue id, a kind (`music`, `sfx`, `voice`) or a cue-list path. Empty means the whole cue list. Needs `.gamestudio/contract.json` (`audio_direction`) and a budget in `budget.json`.

## Procedure
1. **Preconditions.** `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py budget`; `gs_status` to see configured audio providers and mock mode. Mock audio is silent/placeholder and stays `placeholder`.
2. **Audio bible.** If `audio_direction.bible_ref` is empty, copy `${CLAUDE_PLUGIN_ROOT}/templates/docs/audio-bible.md` to `.gamestudio/audio/audio-bible.md`; `arcosian:audio-director` fills it: palette and instrumentation, tempo/key families, loop and transition rules, SFX design language (pitch families per verb, no-fatigue rules for the most repeated sounds), voice casting and tone, loudness targets, mix priorities, forbidden sounds. Write path to `bible_ref`.
3. **Cue list.** Derive from `mechanics[].feedback`, `ux.screens`, `ftue.steps`, `monetization` moments (purchase, reward), `liveops.events`. One row per cue: id, kind, trigger event, length or loop flag, variations needed (rule of thumb: frequent sounds need several variants with pitch/volume jitter), bus, priority, ducking behaviour. Save as `.gamestudio/audio/cue-list.md`. Register all as `placeholder`.
4. **Generate.** Always estimate with a dry run first.
   - `audio_music {prompt, duration_sec, instrumental: true, provider, composition_plan?}`: prompt from the bible (genre, instruments, tempo, mood, loop-friendliness). For adaptive music generate stems or sections of equal bar length in one key and tempo.
   - `audio_sfx {prompt, duration_sec?, loop?, provider}`: generate 3-6 candidates per cue, short and dry (no baked reverb) so the engine controls space.
   - `audio_voice {text, voice_id | voice_description, provider, lines?}`: use `lines` for dialogue batches; keep one voice id per character and record it in the bible.
   **Human checkpoint:** the user listens to one music cue, one SFX set and one voice line (the "audio style lock") before bulk generation. You cannot hear audio; do not claim a cue "sounds good". Rely on `audio_post.py qc` numbers and human review.
5. **Post-process** with `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/audio_post.py`:
   - `trim --in x.wav` remove leading/trailing silence (keep a few ms to avoid clicks).
   - `normalize --in x.wav --lufs -16 --tp -1` for music; SFX are leveled relative to each other by ear and by peak, not individually to -16 LUFS.
   - `loop --in x.wav --out x_loop.wav` find a seamless loop point and crossfade; verify click-free.
   - `convert --in x.wav --format ogg|m4a|wav` ogg for Godot and Android, m4a/AAC for iOS where needed, wav for short SFX if decode cost matters.
   - `qc --in x.wav --json` check loudness, true peak, clipping, silence, DC offset, sample rate and loop seam. Exit 1 means fix before import.
   Targets above are starting points; confirm the loudness target in the bible. Mobile speakers roll off bass, so judge on phone speakers and cheap earbuds.
6. **Engine implementation.**
   - Godot: buses `Master > Music, SFX, UI, Voice`; ducking with a compressor/sidechain-style effect on Music when Voice plays; `AudioStreamPlayer` pools for repeated SFX, `AudioStreamRandomizer` for variation, `AudioStreamInteractive` for adaptive music (clips and transitions); music player persistent across scenes.
   - Unity: AudioMixer with groups Music/SFX/UI/Voice, exposed volume parameters on a log scale, snapshots for pause/duck, AudioSource pooling; adaptive layers via mixer snapshots or a small layered-stem controller.
   - Common: settings screen with Music/SFX sliders and mute; respect the device silent switch behaviour for the platform; pause audio on app background and resume on focus; limit simultaneous voices; preload small SFX, stream music; audio focus handling on Android and interruptions on iOS.
7. **Wire to events.** Subscribe audio to the sim-core's events (presentation layer only), never to input directly, so audio stays testable and deterministic. See `game-architecture`.
8. **Licence.** `licence_check {}` and review thresholds against `config.revenue` (`lifetime_gross_usd`, `developer_annual_games_revenue_usd`). Some music services restrict commercial use by revenue band or plan tier; a game that crosses a threshold later needs a plan change or replacement before release. Record `plan_tier` in each manifest `licence`.
9. **Promote.** `manifest_update` through `candidate -> approved -> final` as in `asset-production`; `final` needs QC pass, engine import and licence clean.

## Outputs
`.gamestudio/audio/audio-bible.md`, `.gamestudio/audio/cue-list.md`, audio files under `generated_dir`, manifest and budget entries, bus layout in the project, QC JSON under `.gamestudio/evidence/<FEATURE-ID>/`.

## Quality gates
- Every cue in the list is `final` or explicitly deferred with a placeholder noted.
- `audio_post.py qc` passes for every shipped file; loops are seamless.
- Mix: voice intelligible over music, UI sounds not fatiguing at 100 repeats, nothing clips.
- `licence_check` clean against current `config.revenue`.
- Download size impact within `perf_budgets.download_mb`.
- Human has approved the audio style lock.

## Failure modes and recovery
| Symptom | Fix |
|---|---|
| Loop pops | Re-run `loop`, regenerate with a bar-aligned length, or crossfade longer |
| SFX too loud/quiet vs music | Adjust bus gains, not file loudness |
| Music repetitive | Add variations or stems, longer sections, randomised transitions |
| Voice inconsistent between lines | Pin `voice_id`, batch via `lines`, same model |
| Licence threshold crossed | Move to the right plan or replace the cue before the build |
| Large download | Convert to ogg/m4a, lower sample rate for SFX, stream music |

## Decision tables

**Format by use**

| Use | Format | Why |
|---|---|---|
| Looping music | ogg (Godot/Android), m4a (iOS if needed) | Streamed, small |
| Short SFX, very frequent | wav or low-bitrate ogg | Avoid decode latency |
| Long voice | ogg/m4a, streamed | Size |
| Source masters | wav, kept out of the build | Re-export later |

**Cue priority and ducking**

| Priority | Examples | Behaviour |
|---|---|---|
| 1 | Voice, purchase confirmation | Never dropped; ducks music |
| 2 | Core feedback (match, hit, win) | Pooled, variants, limited voices |
| 3 | UI taps | Short, quiet, rate-limited |
| 4 | Ambience | First to be culled |

## Worked example: casual puzzle game
Cue list has 1 menu loop, 2 gameplay loops, 14 SFX, no voice. Bible sets music at about -16 LUFS integrated and a true peak ceiling of -1 dBTP, and SFX pitched to rise with combo level. Generate three gameplay loops at the same tempo, pick two by human listening, run `loop` and `qc`, convert to ogg. The match sound gets five variants played via `AudioStreamRandomizer` with small pitch jitter. Ducking is unnecessary without voice. Total audio target is a fraction of the download budget, checked with `perf_budgets.download_mb`.

## Audio review checklist
- Play each cue in context on a phone speaker and with earbuds.
- Repeat the most frequent SFX 50 times in a row; if it grates, add variants or shorten it.
- Switch scenes and background the app; music must resume cleanly.
- Test with sound off: the game must stay understandable (accessibility, see `accessibility-localization`).

## Naming
`audio/<kind>/<id>.ogg`, ids stable across status changes (`sfx_match_01`), variants suffixed `_01.._NN`, loops suffixed `_loop`.

## Volatile facts (as of Oct 2026 - verify)
Provider terms, model ids, pricing and revenue-band licence limits change. Read `mcp/studio-gateway/pricing.json` and the provider's current terms before relying on a plan. Source: https://elevenlabs.io/pricing and https://elevenlabs.io/terms (verify the commercial-use and music licensing terms in force when you ship).

## Related skills
`audio-direction`, `ai-audio-pipeline`, `game-feel`, `legal-ethics`, `asset-production`.
