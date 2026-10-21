# Generation Pipelines

This file is the how-to for generating game audio with AI services: composition plans for structured music, loop engineering (three methods), stems and adaptive sets, SFX variation sets and library layering, voice design and localization, prompt templates, batching and selection, and failure recovery. It assumes services are chosen per `references/model-landscape-2026.md` and that direction (palette, key, tempo) comes from the audio bible in `audio-direction`. Post-processing and QC details are in `references/post-and-qc.md`. Parameter names are as reported at research time: check the live API docs.

## Contents
1. Pipeline overview
2. Candidate economics and selection
3. Music: composition plans
4. Music: loop engineering
5. Music: stems and adaptive sets
6. Music: continuation, inpainting and extension
7. Stingers and short musical cues
8. SFX: single events
9. SFX: variation sets
10. SFX: library layering
11. UI sound families
12. Voice: design and consistency
13. Voice: dialogue, barks and localization
14. Prompt templates (copy blocks)
15. Batching, manifests and cost control
16. Failure modes and recovery

## 1. Pipeline overview

```
audio bible + cue list
   -> style-lock round (1 cue per class) -> human approval
   -> generate candidates (seeds, fixed prefix)
   -> auto-QC (duration, LUFS, peak, silence, loop seam)
   -> select (human, or LLM judge against rubric + human spot check)
   -> post (trim, loop, normalize, convert)
   -> engine import and on-device test
   -> manifest + licence record
```
Rules: never skip the style-lock; never promote an asset without a manifest entry; never claim a candidate sounds good (report measurements, ask the human); never put keys in files.

## 2. Candidate economics and selection

- Expect to discard most candidates. Start with: music 4-8 per cue, SFX 3-4 per variant slot, voice 2-3 per hero line, 1-2 per bark.
- Selection rubric (score 1-5, human or LLM-assisted with human confirmation): fit to bible, loopability or clean ending, tempo and key accuracy, timbre match, absence of artifacts (warble, smear, vocal ghosts), mix balance, memorability.
- Automatic rejects (before any listening): wrong duration, clipping, silence over a threshold at the head, wrong sample rate, vocals when instrumental was required (spot check), loudness outside tolerance by more than a few LU (normalization can fix mild cases).
- Keep the rejects' prompts: patterns in failures tell you which words to remove.
- Blind A/B against the reference cue helps avoid fatigue bias; limit one session to about an hour of listening.

## 3. Music: composition plans

For services that support section-level plans (reported for ElevenLabs Music), describe the track as named sections, each with positive styles (what to include), negative styles (what to exclude), duration and optional lyrics. A plan and a free text prompt are mutually exclusive in that API (reported).

### Plan design for a loopable game track
| Section | Duration | Positive styles | Negative styles |
|---|---|---|---|
| intro | 1 bar to 2 bars (2-5 s) | soft entry, motif, sparse | drums, big hits |
| loop body A | 8-16 bars | steady groove, palette, constant energy | fills, crashes, fade |
| loop body B (variation) | 8-16 bars | same palette, different melody | key change, tempo change |
| tail (optional) | 1-2 bars | resolves to tonic, decay | new material |
Notes:
- Section durations in seconds = bars x bar_s (see timing formulas in `skills/audio-direction/references/music-and-sfx-systems.md`). Services have minimum and maximum section lengths (reported 3 s to 2 min): keep within.
- Put the same palette and tempo words into every section so the model holds identity across sections.
- Ask for "no fade-out" and "ends on tonic" in tail sections; omit the tail if you will cut loops from the body.
- Generate the body longer than needed (20-40 percent) so post can pick the best bars.
- Use the instrumental flag where available; also add "no vocals" to prompts.

### Prompt-only fallback (no plan support)
Request: "<palette>, <BPM> BPM, steady, 16 bars loop body, no intro, no ending, no fade, constant energy". Then cut by bars in post.

### Example plan (pseudo-JSON, adapt to the API)
```json
{
  "positive_global_styles": ["warm cosy puzzle music", "felt piano", "soft mallets", "100 BPM", "C major"],
  "negative_global_styles": ["vocals", "heavy bass", "cymbal crash", "tempo change", "key change"],
  "sections": [
    {"name": "intro", "duration_ms": 4800, "positive": ["sparse motif"], "negative": ["drums"]},
    {"name": "body", "duration_ms": 38400, "positive": ["steady groove"], "negative": ["fills", "fade out"]}
  ]
}
```
Check: 100 BPM, 4/4 gives bar 2.4 s; 2 bars intro is 4.8 s; 16 bars is 38.4 s. Exact field names differ by vendor.

## 4. Music: loop engineering

No reviewed official music API documents a native seamless-loop mode, so loops are made in one of three ways.

### Method A: bar-aligned cut of a steady section (default)
1. Generate a track with a long steady section at a known BPM.
2. Measure actual BPM and the beat grid offset (first downbeat time). If the measured BPM differs from the target, compute the true bar length from the measurement, not the prompt.
3. Choose a start at a downbeat and length of N whole bars. The tail beyond the loop end provides overlap material.
4. `audio_post.py loop --in src.wav --out loop.wav --bpm <measured> --bars N --xfade 0.5`. The tool needs the source to be at least loop length plus crossfade; it fades the post-loop tail over the head so the end flows into the start.
5. Test the seam by looping 4-8 times and listening; check no click, no energy dip, no double-hit.
Pass criteria: no audible seam at normal listening on a phone; QC clean; length equals bars x bar_s within a sample or two of rounding.

### Method B: continuation or inpainting so the end returns to the start
Where a service offers audio-to-audio, inpainting or continuation (reported for Stable Audio family and, per a secondary source, for ElevenLabs on some plans), upload the loop candidate, mask the last bar(s) or tail, and ask the model to continue so it resolves back toward the opening material. Then cut as in Method A. Results are non-deterministic; generate several. Check the licence on uploaded reference audio.

### Method C: detect loop points afterwards
Use a loop-point detector (PyMusicLooper is MIT and finds loop points, exports intro/loop/outro, and reports points in samples) on candidates that were not designed to loop. Quality varies: prefer A for designed cues. Verify the detected point lands on a bar line; if it does not, use A.

### Loop checklist
- [ ] Whole number of bars; length in samples recorded in the manifest.
- [ ] No fade-in or fade-out in the loop file.
- [ ] Loudness normalized with linear gain.
- [ ] Format that loops cleanly in engine (Ogg or WAV; check MP3 and AAC padding).
- [ ] Engine loop points set (Godot loop offset for compressed formats; WAV loop begin and end; Unity loop on the source).
- [ ] Seam tested in engine on device.

## 5. Music: stems and adaptive sets

### Goals
A set of cues sharing tempo and key that can be re-sequenced, plus stems for vertical layering. Design the set before generation (see `audio-direction`).

### Getting stems
| Route | How | Caveats |
|---|---|---|
| Service-supplied stems | Request stems with the track (reported for some plans) | Count and availability vary by tier; verify API access; check alignment and length |
| Plan-based layer renders | Generate the same plan with different positive and negative styles (for example "drums and bass only", "harmony only", "lead only") using the same seed and tempo | Not guaranteed to align or share harmony; verify by summing |
| Real-time generator layers | Fixed BPM, scale and seed; toggle drums, bass, "only bass and drums" to render layer variants | Experimental, instrumental only, key changes need a reset; treat as R&D |
| Stem separation tools | Separate a full mix into stems | Artifacts; check licence of the separation tool; use only for refinement |
| Human arrangement | A musician rebuilds layers from the AI sketch | Highest quality, strongest authorship claim |

### Stem verification procedure
1. All stems have identical length in samples and the same sample rate.
2. Sum test: add all stems; compare to the reference mix; the sum should not clip and should sound like the full mix.
3. Each stem loops cleanly alone.
4. Cumulative order test: base, base+harmony, base+harmony+lead: each step must sound intentional.
5. Normalize all stems with the same gain (compute from the full mix), never per stem, to preserve balance.

### Adaptive set blueprint (casual game)
| Cue | Role | Bars | Stems | Notes |
|---|---|---|---|---|
| menu | Calm | 16 | 1 | half-time feel |
| play | Core | 16-32 | 3 | rhythm, harmony, lead |
| tension | Stakes up | 16 | same as play + accent | same position entry |
| win | Stinger | 2 | 1 | key-resolved |
| fail | Stinger | 2 | 1 | gentle |
Generate with a shared prefix; verify tempo and key of every cue; keep a table in the manifest.

## 6. Music: continuation, inpainting and extension

- Extending a loop: use continuation to add a variation section that starts where the base ends, then re-cut. Continuation can drift in key or tempo: measure.
- Fixing a bad bar: inpaint the faulty region (where supported) rather than regenerating the whole track.
- Licensing caution: uploaded audio may be subject to the service's terms; do not upload material you lack rights to, and do not use restricted libraries (some prohibit ML use).
- Single-turn services (reported for the Gemini API music models) do not support iterative editing: regenerate with a revised prompt instead.

## 7. Stingers and short musical cues

- Generate in the soundtrack's key, 2-6 s, "ends on a resolved chord", "no drums unless stated", "clean decay".
- Better from the music model than the SFX model because they need harmonic consistency.
- Generate 6-10 candidates, choose 2-3 variants; trim head silence so the hit lands on time; fade the tail to avoid clipping the decay abruptly.
- Time-align: stingers meant to land on a beat should have the first transient at sample 0 after trimming.

## 8. SFX: single events

1. Prompt with: event, material, character, length, "sharp attack", "no reverb tail", "no background noise", "single hit" (see template in section 14).
2. Request raw PCM or WAV, 48 kHz, if the API allows; avoid MP3 for short effects (decode latency and padding).
3. Generate 3-4 takes; choose by transient clarity and body.
4. Trim leading silence and slow attacks (`audio_post.py trim --start`), apply a short fade-out (`--fade`), peak-normalize per event class, export WAV masters.
5. Wire to the event; check sync with the animation frame.
6. For looping ambiences or engine hums, use the service's loop flag if present (reported for ElevenLabs SFX v2), then still verify the seam with `audio_post.py` loop checks and qc.
Reported duration range for one service is 0.5-30 s; most UI sounds are under 1 s, so ask for the length you need and trim.

## 9. SFX: variation sets

Variation should be designed, not accidental. Target per slot: 3-8 variants depending on frequency (see `audio-direction`).

Procedure:
1. Define the slot (for example `tile_tap`) and the family prefix.
2. Generate N+2 takes with the same prompt (different seeds) and small prompt variations ("slightly higher", "slightly softer").
3. Filter: duration within 20 percent of median; peak within 3 dB; attack within 10 ms of median.
4. Cluster by timbre similarity (listen or compare spectra); discard outliers that do not feel like siblings.
5. Normalize variants to the same level; keep natural differences in pitch and envelope.
6. In engine: random selection excluding the last; additional pitch jitter of a few percent for non-tonal sounds.
Pitch-stepped tonal sets (for example combo ladders): generate one clean tone and derive steps by pitch-shift in a tool that preserves transients, or generate each step in key with a shared prefix; verify intonation against the scale.

## 10. SFX: library layering

Combine generated sounds with human-recorded layers where realism matters.
1. Select a recorded layer for the transient or body (licence-checked: CC0 on Freesound, or a library with game-use terms such as a game-audio bundle).
2. Generate the complementary layer (tail, magic sparkle, synthetic tone).
3. Align at the transient, balance levels, check phase, bounce.
4. Record both sources in the manifest, including bundle year or the Freesound sound id and licence.
5. Never use a library whose licence forbids ML use as reference or training input for a generator or fine-tune.
6. Keep stems of the layers in the project for later re-bounces.

## 11. UI sound families

- One prefix per family: material, timbre, pitch centre, length cap (under about 150-300 ms for navigation).
- Generate the whole ladder in one session so characteristics stay close: tap, select, confirm, cancel, error, reward small, reward big, level up.
- Tonal sounds in the key family; atonal sounds (clicks) tuned by spectral centre.
- Normalize per class; judge on a phone speaker.
- Reserve a "signature" sound (the primary confirm or reward) and polish it most.
- Consider musical stingers from the music model for level-up and unlock.

## 12. Voice: design and consistency

1. Write the voice brief (see `audio-direction`).
2. Create the voice by design where the service supports it (reported: text description to previews, then save the chosen preview as a voice id). Generate several previews, choose, save the id, record seed and description.
3. Lock settings (stability, style, speed, model) per character; changing them changes identity.
4. Generate a sample set (neutral, excited, whisper, shout) and have the human approve before bulk.
5. Use pronunciation dictionaries or phonetic respelling for invented names; test names early.
6. Keep the voice-id to character mapping in the manifest; never reuse a real person's likeness.
7. Where a service adds a loudness setting in design, record it; still normalize afterwards.

## 13. Voice: dialogue, barks and localization

### Dialogue scenes
Use multi-speaker dialogue generation for scenes where available (reported: up to 10 voices and about 2,000 characters reliable per request on one service; two speakers per request on another). Provide previous and next text for continuity when the service supports it. Use inline emotion tags sparingly and verify the service's tag syntax (it differs). Split long scenes into chunks at sentence boundaries.

### Barks
- Generate in sets per category, 5-12 variants, same voice and settings.
- Trim silence at head and tail to a few milliseconds of margin; target under about 1.5 s.
- Normalize to the voice target; cap peaks.
- Test in context with music at play volume.

### Localization
1. Freeze the English text and notes (intent, emotion, length limit).
2. Translate with human or reviewed machine translation; keep length within about 120-130 percent of source for fit (a planning heuristic, not a rule).
3. Choose a model with the needed languages (coverage claims vary: 70+ to 130+ languages for different services; verify the specific languages).
4. Generate per language with a voice that fits the character; check that a "same voice across languages" feature (if any) preserves identity.
5. Native-speaker review for pronunciation, naturalness and cultural fit; recorded per language in the manifest.
6. QC loudness and trim per file; package per-language bundles for on-demand download.
7. Keep captions available (see `accessibility-localization`).
Leaderboards for TTS are usually English-only: do not extrapolate to other languages.

## 14. Prompt templates (copy blocks)

```
[MUSIC LOOP]
Instrumental <genre/feel> game music for <state>. Palette: <palette>. <BPM> BPM, 4/4, steady, no tempo changes.
Key: <key>, no key changes. Structure: steady loop body, constant energy, no intro, no ending, no fade-out.
Mix: <mix notes>. No vocals, no lyrics, <exclusions>.

[STINGER]
Short <win/fail/unlock> stinger, <2-4> seconds, <palette>, key <key>, resolves on the tonic chord, clean decay, no drums, no vocals.

[SFX HIT]
<event> sound effect, <material> material, <crisp/soft> character, <0.3> seconds, sharp attack, no reverb tail,
no background noise, single hit, <pitch note if tonal>.

[SFX LOOP]
<ambience or hum>, seamless loop, steady, no distinct events, no music, <5-10> seconds.

[VOICE DESIGN]
<age feel> <register> voice, <accent family>, <pace>, <attitude>, clear diction, <what to avoid>. Fictional character, not modelled on any real person.

[BARK SET]
Character <id>. Say: "<line>". Emotion: <emotion>, intensity <1-5>. Short, natural, no filler.
```
Keep a fixed prefix across a family; version the prefix in the bible and reference its version in every manifest entry.

## 15. Batching, manifests and cost control

- Batch by class and family so settings stay constant; cap candidates per call; use the budget ledger to enforce a spending ceiling and stop on overrun.
- Manifest entry per candidate and per promoted asset: id, class, provider, model and version, plan tier, prompt (or prompt id), seed, parameters, date, cost, source files, post chain used, QC result, licence, reviewer, status (candidate, approved, final), placeholder flag false for final.
- Idempotence: name files deterministically (`<cue_id>__<provider>__<seed>`); never overwrite approved assets.
- Retries: bounded (for example 3) with backoff; stop on repeated authentication or quota errors.
- Secrets only from environment variables; never log keys.

## 16. Failure modes and recovery

| Failure | Cause | Recovery |
|---|---|---|
| Vocals in instrumental cue | Prompt ambiguity | Use instrumental flag, negative styles, regenerate |
| Tempo or key off | Generators approximate | Measure; time-stretch slightly or regenerate; record measured values |
| Loop seam clicks or dips | Cut off bar line, tail not overlapped | Re-cut with bar math, longer crossfade, verify in engine |
| Stems misaligned | Independent renders | Use plan-based same-seed renders or service stems; verify sum |
| SFX has slow attack or silence | Model style | Trim; regenerate with "sharp attack" |
| Voice drifts between lines | Settings or seed changed | Lock settings, regenerate the set |
| Mispronounced names | Dictionary missing | Add phonetic spelling or pronunciation dictionary |
| Output MP3 for short SFX | Default format | Request PCM or WAV, or convert and trim padding |
| Rate limit or quota | Burst requests | Backoff, batch, check plan limits |
| Licence tier mismatch | Generated on wrong plan | Regenerate on a qualifying plan if terms say output keeps the old plan |
