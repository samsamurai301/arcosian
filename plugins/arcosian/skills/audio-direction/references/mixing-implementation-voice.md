# Mixing, Implementation and Voice

This file is the delivery half of audio direction: the bus tree and ducking rules, loudness targets (given with honest uncertainty, because no official mobile standard exists), file formats and streaming choices for iOS and Android, runtime audio-session behaviour (iOS AVAudioSession, Android audio focus, the silent switch, interruptions, route changes), and voice direction (casting, briefs, barks, consent for real performers, AI disclosure). Use it when you set up the mixer, when a build sounds wrong on a phone, and when a project includes voice.

## Contents
1. Bus tree
2. Ducking and sidechain rules
3. Loudness targets and uncertainty
4. Headroom, limiter, dynamics
5. Formats, sample rates, compression
6. Streaming vs preload, memory budget
7. iOS audio session
8. Android audio focus and latency
9. Interruptions, routes, lifecycle
10. Mix review procedure
11. Voice direction
12. Barks
13. Consent, rights and AI disclosure
14. Volatile facts (as of Oct 2026 — verify)

## 1. Bus tree

Keep it small. A typical casual game:

```
Master (limiter)
 ├─ Music        (stems and sections)
 ├─ SFX
 │   ├─ UI
 │   ├─ Gameplay
 │   └─ Reward
 ├─ Ambience
 └─ Voice        (VO, barks)
```
Rules:
- Player-facing volume sliders: Music, SFX (including ambience), Voice if present; plus a master mute. Persist the settings.
- Exposed parameters: bus volume for each, a master low-pass for pause or underwater effects, and a music-duck amount.
- Effects per bus: Music gets a gentle low-shelf cut around 100-150 Hz if bass competes (check on speaker), Voice gets a compressor and a high-pass at roughly 80-100 Hz, Master gets a limiter with ceiling near -1 dB true peak.
- Godot: `AudioServer` buses and `AudioEffect*` resources; save a bus layout. Unity: `AudioMixer` groups, snapshots (for example Gameplay, Paused, Cutscene) with blend times, exposed parameters for sliders (convert slider 0..1 to dB with `20*log10(x)`, clamp at -80 dB).

## 2. Ducking and sidechain rules

| Source | Target | Amount | Attack | Hold | Release |
|---|---|---|---|---|---|
| Voice | Music and ambience | 4-8 dB | 50-100 ms | duration of line | 300-600 ms |
| Big reward | Music | 2-4 dB | 20-50 ms | 300-600 ms | 400-800 ms |
| Stinger | Music bed | 3-6 dB or mute | immediate | stinger length | 500 ms |
| Pause menu | Gameplay buses | low-pass and 6 dB | 100 ms | menu open | 300 ms |
Starting values; tune by ear on a phone. Implementation options: (a) event-driven: script tweens bus volume on VO start and end (simple, deterministic, preferred on mobile); (b) sidechain compressor keyed from the source bus (smoother for overlapping events, extra DSP). Avoid pumping: slow release and modest depth. Never duck the SFX bus broadly; players need feedback.

## 3. Loudness targets and uncertainty

There is no official, current Apple, Google or console-style loudness standard specifically for mobile games that the research found. What exists is older or from adjacent platforms:
- Console guidance from Sony's audio working group (ASWG-R001) centres on about -24 LUFS for long-form content; a 2015 mobile-audio article by an audio director reported targets around -16 to -18 LUFS for device speaker playback and slightly louder for noisy headphone listening. A VR platform vendor lists -16 LUFS for standalone and -18 LUFS for tethered. A secondary blog suggests -16 to -20 LUFS overall with true peaks below 0 dB.
- These sources disagree because use contexts differ. Treat all numbers as starting points, then validate on devices.

Recommended working defaults (this skill's recommendation, not a standard):

| Asset class | Integrated target | Tolerance | True peak |
|---|---|---|---|
| Music loops (mixed bed) | about -18 LUFS | plus or minus 1.5 LU | at or below -1 dBTP |
| Voice lines | about -16 LUFS | plus or minus 1.5 LU | at or below -1 dBTP |
| Short SFX | peak-normalized per event class, not LUFS (too short to measure reliably) | match perceived loudness by ear | at or below -1 dBFS |
| Ambience | about -26 to -22 LUFS | plus or minus 2 LU | at or below -3 dBTP |
| Whole-game master during play | about -16 to -18 LUFS short-term typical | check across a full session | limiter ceiling -1 dB |

Notes:
- Integrated loudness is meaningful for assets longer than a few seconds; for stingers and SFX use peak and short-term values and judge by ear.
- Normalize loops with a linear (non-dynamic) gain so loop seams do not shift; the two-pass method in `audio_post.py normalize` uses linear mode for this reason.
- Give the player headroom: the system volume is the real control. Mixes pushed to the limiter give no room for emphasis.
- Optional route-aware behaviour: raise overall level a little or add gentle master compression when on the built-in speaker, relax it on headphones; blend smoothly on route change (an approach described by Rob Bridgett, 2015). Implement only if you can test it.
- Check voice against music: voice should sit a few LU above the music bed at the moment it plays, via ducking rather than by making files louder.

## 4. Headroom, limiter, dynamics

- Keep stems and one-shots at moderate levels (peaks around -6 to -3 dBFS) so many sounds can sum without clipping; the master limiter catches the rest.
- Reduce dynamic range by design, not by crushing: cap the loudness delta between quietest and loudest cue at a few LU in normal play.
- Watch sum-of-voices peaks during chain rewards or explosions; rate-limit and voice-limit rather than lowering everything.
- Mono-summing test: sum to mono and compare; phone speakers behave this way.

## 5. Formats, sample rates, compression

Starting matrix (combine with engine docs for your version):

| Asset | Godot | Unity | Rate | Channels |
|---|---|---|---|---|
| Short SFX (under about 1-2 s, frequent) | WAV (the importer's default `compress/mode` is QOA; checked on 4.7.2, where the imported stream reports `FORMAT_QOA`. QOA is reported to beat IMA ADPCM on quality, which was not measured here) | PCM or ADPCM, decompress on load | 44.1/48 kHz, or 22-32 kHz if inaudible | mono |
| Longer SFX, ambience | Ogg Vorbis | Vorbis | 44.1 kHz | mono or stereo |
| Music | Ogg Vorbis (MP3 reported to cost less CPU than Ogg on mobile when many compressed sounds play at once; measure) | Vorbis, streamed | 44.1 kHz | stereo |
| Voice | Ogg Vorbis, streamed or decompress-on-load for short barks | Vorbis | 24-44.1 kHz | mono |
- Masters stay uncompressed 48 kHz 16 or 24-bit WAV in the source repo; ship compressed derivatives. Convert with `audio_post.py convert --format ogg|m4a|wav`.
- Vorbis quality: lower until artifacts are noticeable, then raise one step (the approach in Unity's manual); typical music quality settings land in the mid range, verify per project.
- MP3 and AAC add decoder padding that can break seamless loops; prefer Ogg or WAV for loops, or verify gapless behaviour in-engine.
- Unity ADPCM has a fixed compression ratio and can introduce artifacts on smooth music; avoid it there.
- Sample-rate reduction saves memory for short SFX; keep full rate where transients matter.
- Per-platform overrides: allowed in both engines; use them when the low tier needs lower quality.

## 6. Streaming vs preload, memory budget

| Class | Load strategy | Why |
|---|---|---|
| UI and gameplay SFX | Preload decoded at scene load | Instant start, no decode latency |
| Reward stingers | Preload | Must fire on time |
| Music | Stream compressed | Large; one or a few at a time |
| Stems | Stream, started in sync | Test CPU on low tier |
| VO hero lines | Stream or decompress on demand | Large, played rarely |
| Barks | Preload per level | Frequent and short |
| Ambience | Stream | Long loops |
Budget: write the numbers into the project perf budget (see `mobile-performance`). Compute decoded size: `seconds * sample_rate * channels * 2 bytes` (16-bit). Example: 1 s mono at 44.1 kHz is about 88 KB decoded; a 60 s stereo track is about 10.6 MB decoded, which is why music is streamed. Prefetch the next level's assets during a loading moment, unload on scene exit.

## 7. iOS audio session

The audio session category decides interaction with the system:
- A category that **mixes with other audio and respects the ring/silent switch** (the ambient-style category) is the right default for most games: the player's podcast keeps playing, the silent switch mutes the game.
- A category that **ignores the silent switch and takes over audio** (playback-style) suits media-first apps; for games it surprises players in quiet places. Use it only if sound is the product, and offer an in-game mute.
- Options: allow mixing with others; optionally duck others for VO moments; configure once at launch, and again after interruptions.
- Handle: interruption notifications (phone call, Siri, alarm): pause and remember state, resume on the interruption-ended notification if the system says should-resume; route-change notifications (old device unavailable, such as headphones unplugged: pause music or lower volume, never blast); app backgrounding (pause audio unless a background-audio capability is declared, which games rarely should).
- Latency on iOS is generally low with engine defaults, but Bluetooth routes add noticeable delay: do not compensate by shifting gameplay timing; rhythm games should offer calibration.
- Test with: silent switch on and off, a call arriving, Control Center music playing, unplugging headphones, AirPlay.

## 8. Android audio focus and latency

- Use audio attributes with a game usage so the system routes volume controls and policy correctly.
- Request audio focus on start of play (or when music starts). Responses to handle: loss (permanent): stop; transient loss: pause; transient loss can-duck: lower volume; gain: restore. Do not hold focus when muted.
- Low-latency audio paths and device behaviour vary widely across the Android ecosystem; engine audio backends handle most of it, but test on the lowest device tier and on common Bluetooth routes. Report measured latency in the perf notes rather than assuming.
- Respect system volume streams; do not set the media volume programmatically.
- Test: incoming call, another media app taking focus, notification sounds, headphones unplugged, Do Not Disturb, battery saver.

## 9. Interruptions, routes, lifecycle

Checklist (applies to both platforms):
1. On pause (background or interruption): pause all music and ambience, stop looping SFX, keep state.
2. On resume: do not restart music from zero unless the state demands it; fade in over 0.3-1 s.
3. On route change: if headphones were removed, pause or lower; re-evaluate route-based settings.
4. Cold start: delay the first music until the audio session is configured; show nothing that depends on audio.
5. Mute state persists across sessions; a muted game must never unmute itself after an interruption.
6. Never play sound while the device is in silent mode unless the player opted in to ignore it.
7. Handle first-touch audio unlock only for web builds (not relevant to native).

## 10. Mix review procedure

1. Run `audio_post.py qc` on all shipped files; fix LUFS, peak, clipping and DC offset outliers.
2. Build a play session capture (screen and audio recording on the device) of two minutes including peak chain events.
3. Listen on the phone speaker at mid volume, then wired headphones, then Bluetooth. Note: unintelligible VO, masked SFX, harsh peaks, missing bass-dependent cues.
4. Adjust bus gains and ducking, not individual file levels, unless a class is off.
5. Re-run after each content drop; mixes drift as assets are added.
6. Record the final bus gains in the audio bible approval log.
Because an agent cannot hear audio, produce measurements and a listening checklist for the human, and do not claim the mix is good.

### Mix troubleshooting table
| Symptom | Likely cause | Fix |
|---|---|---|
| Thin, weak on phone | Meaning carried below about 200 Hz | Add mid harmonics or saturation, cut sub from the speaker path |
| VO unintelligible | Music dense in 1-4 kHz, no ducking | Duck 4-8 dB, carve 2-4 kHz on music, compress VO |
| Clipping during combos | Voices sum, no rate limit | Voice limit, rate-limit event, lower per-event peaks |
| Music pumping | Sidechain too fast or deep | Slower release, less depth, or event-driven ducking |
| Loop click | Seam not on zero crossing, codec padding | Re-cut, use Ogg or WAV, check in-engine |
| Louder after interruption | Volume restored without limiter, session reset | Reapply bus state on resume, fade in |
| SFX sets uneven | Per-file levels differ | Re-normalize per class, balance at bus |
| Harsh on headphones | Excess 3-6 kHz in tonal SFX | Shelve highs, soften attacks |

### Worked bus gain example (starting point)
Music bus -6 dB, SFX bus -3 dB, Voice bus -2 dB, Ambience bus -12 dB, master limiter ceiling -1 dB. During VO, music ducks a further 6 dB for the line length; during a top-tier reward, music ducks 3 dB for 500 ms. These are values to start tuning from on a real device, not targets.

## 11. Voice direction

### Choosing hero vs bark
Hero lines (tutorial, story, named characters) get the budget: voice brief, multiple takes, human review. Barks (short reactions) are cheap and numerous: consistent voice, many variants.

### Voice brief (per character)
Fields: role and function in the game; age feel; register (low, mid, high); pace; attitude; accent family; clarity or breathiness; relationship to the player; things the voice must never do; languages. Add 2-3 sample lines in the character's idiom. The brief serves both a synthetic voice-design prompt and a human casting call.

### Direction notes per line
Give each line: context, emotion, intensity (1-5), pace, and any emphasis. Keep lines short (mobile UI must fit; players skim). Write for the ear: short sentences, no tongue twisters, pronunciation notes for invented names, and a pronunciation dictionary where the service supports it.

### Performance consistency
Fix voice identity (voice id, seed or equivalent), keep style settings constant across a character's lines, regenerate lines as sets, and re-QC loudness per line against the voice target. Sample generated lines in context with music and SFX before bulk generation.

### Localization
Plan text expansion (many languages run longer than English), keep lines timing-tolerant, and treat quality per language as unverified until a native speaker reviews. See `accessibility-localization`. Keep captions available for all VO.

## 12. Barks

- Define categories: acknowledge, success, fail, idle, warning, greeting.
- Variants: 5-12 per frequently used category; avoid repeating within the last N plays.
- Throttle: global cooldown (for example a few seconds between barks), per-category cooldown, and do not play over hero VO.
- Short: under about 1.5 s, with trimmed silence at head and tail.
- Keep them skippable and optionally disable-able; frequent barks annoy.
- Write them with game-world flavour and avoid sarcasm that could read as mocking the player's failure (see `player-psychology`).

## 13. Consent, rights and AI disclosure

Practices to put in the audio bible, not legal advice (see `legal-ethics` and consult counsel for union or large-studio contexts):
- **Real performers**: any voice that imitates, clones or is trained on a real person needs written, specific consent describing intended use, with records kept. Do not clone a celebrity or any identifiable person without it. Union agreements (for example the SAG-AFTRA 2025 Interactive Media Agreement) require informed consent and specific description of use for digital replicas of performers, plus usage reporting for signatory studios; verify current terms if your project has a union context.
- **Synthetic invented voices**: designing a voice from a text description that is not modelled on a real performer is generally lower risk than cloning, but do not describe or prompt it with a real person's name.
- **Provider terms**: some providers require disclosing that a voice is AI generated to end users, some tie licence to plan tier, and some restrict use of output for competing products. Read terms per provider and record plan tier and date per asset.
- **Disclosure**: put an "AI-generated voices" line in credits or the settings About screen where voices are synthetic, and complete store AI-content disclosures where the store asks (policies change, verify at submission; coordinate with `arcosian:compliance-officer`).
- **Children**: if the game targets minors, apply stricter data and consent practices; do not collect voice data from players without compliance review.
- **Manifest fields** per voice asset: character, provider, model, voice id or design prompt, seed, plan tier, date, consent reference, disclosure status.

## 14. Volatile facts (as of Oct 2026 — verify)

- No official mobile loudness standard found; figures cited above come from older or adjacent sources. Sources: https://audiomediainternational.com/mobile-loudness-an-adaptive-approach/ (2015), https://developers.meta.com/horizon/documentation/unity/audio-loudness-meter-overview/ (VR targets), https://bugnet.io/blog/how-loud-should-your-game-be (secondary).
- Engine import and compression guidance: https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_audio_samples.html and https://docs.unity3d.com/Manual/AudioFiles-compression.html
- SAG-AFTRA 2025 Interactive Media Agreement summaries: https://ipandmedialaw.fkks.com/post/102ksuq/new-sag-aftra-2025-interactive-media-agreement-approved-by-members and https://decrypt.co/329479/video-game-performers-ai-consent-rules
- OpenAI's text-to-speech policy requires clear end-user disclosure that voices are AI-generated: https://developers.openai.com/api/docs/guides/text-to-speech
- Not verified in research: current iOS and Android mobile latency numbers, store-level AI voice disclosure rules, EU AI Act implications for AI voices. Check platform documentation and store policy at submission time.
