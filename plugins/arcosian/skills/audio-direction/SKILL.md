---
name: audio-direction
description: Audio direction for games - audio bible and sonic identity, adaptive music (re-sequencing, layering, stingers), SFX layering and reward escalation, bus mixing and ducking, loudness targets, formats, iOS/Android audio session rules, voice direction and AI-voice consent. Use when asked to "write the audio bible", "make the music adaptive", "design UI sounds", "set up the mix", "fix loudness", "direct voice lines" or "plan the audio".
---

# Audio Direction

Audio is half the feel of a mobile game and the cheapest place to look expensive. This skill is the direction layer: what the game should sound like, how sound behaves in the game, how it is mixed and delivered on phones. The generation layer (which AI service, which prompt, which post step) lives in `ai-audio-pipeline`; the run-it-end-to-end command is `audio-production`.

## What this skill gives you

- A complete audio-bible method: sonic identity, palette, reference tracks, prompt vocabulary, cue list, loudness and format targets.
- Adaptive music models (horizontal re-sequencing, vertical layering, stingers, bar-quantized transitions) with engine wiring for Godot and Unity, and a rule for when FMOD or Wwise pay for themselves.
- SFX design rules: categories, layering recipe, variation counts, reward escalation, small-speaker survival, haptic pairing.
- A mix and implementation spec: bus tree, ducking, loudness targets (with honest uncertainty), formats, streaming vs preload, iOS and Android session behaviour.
- Voice direction: casting by description, barks, consent and AI disclosure.

## Core models

**1. Audio serves feedback first, mood second.** On a phone played for 90 seconds in a queue, the player learns state from sound: tap registered, combo grew, reward landed, danger. Mood music is the second job. Design the feedback layer first (see `game-feel`), then the bed under it.

**2. One sonic identity, three constraints.** Identity = a small palette (3-5 instrument or texture families), a harmonic home (a key or a mode family), and a tempo family. Every cue draws from the same palette, lives in compatible keys, and lands on a tempo that divides cleanly. Consistency is what makes generated audio feel authored. Details: `references/audio-bible-and-identity.md`.

**3. Frequency and time budget.** The phone speaker is weak below roughly 200 Hz and is a single driver. Put identity-critical information in the 300 Hz to 5 kHz range, and let the low end be a bonus on headphones. In time, gameplay audio has a few hundred milliseconds of tolerance; UI feedback should start within one frame or two of the event (aim for under about 50 ms end to end, verify on device).

**4. Adaptivity is a budget, not a goal.** Pick the cheapest model that expresses the game's state changes:

| Game state shape | Model | Cost |
|---|---|---|
| One mood, long sessions | One loop plus slow variation | Lowest |
| Discrete modes (menu, play, win, fail) | Horizontal re-sequencing with bar-quantized transitions | Low |
| Continuous intensity (combo, tension, health) | Vertical layering (stems faded by a parameter) | Medium |
| Both | Layered sections with transitions | Highest, only for hero modes |

**5. Reward escalation.** The Nth success within a chain should sound strictly more rewarding than the (N-1)th: pitch up a scale step, add a layer, widen the stereo image, or add a sparkle tail. Cap it, then reset on break. Otherwise streaks fatigue.

**6. Silence is a sound.** Brief ducks and rests before a big payoff increase its impact. Mobile players often mute; the game must also work silent (visual and haptic cover), see `mobile-ux` and `accessibility-localization`.

**7. Interruptibility.** Phones ring, switch apps and change output route. Audio must pause and resume cleanly, never restart a long cue from zero without a reason, and never blast when headphones unplug.

## Decision procedures

### A. Establish the audio direction (new project)
1. Read the design contract's fantasy, tone and session shape (`arcosian` state; `gs.py` loads it).
2. Fill the audio bible from `templates/docs/audio-bible.md` using `references/audio-bible-and-identity.md`: pillars, palette, key and tempo family, references, do-not list.
3. Build the cue list: every music state, every SFX event class, every voice need. Estimate counts before generating anything.
4. Choose the adaptive model with the table in Core model 4, and the engine implementation from `references/music-and-sfx-systems.md`.
5. Define the mix: bus tree, ducking rules, loudness targets, formats from `references/mixing-implementation-voice.md`.
6. Human checkpoint: the user listens to one music cue, one SFX set and one voice line (the audio style lock) before bulk generation. You cannot hear audio; never claim a cue sounds good. Report numbers and structure only.

### B. Choose the music model
1. List game states and which transitions are player-driven (instant) vs system-driven (can wait for a bar).
2. If a transition must feel instant (a hit, a fail), use a stinger over the old music, then transition at the next boundary.
3. If intensity is continuous, build 3-4 stems that sum to the full mix and fade them with a smoothed parameter.
4. Everything shares one tempo and one key family, or transitions need a filler or a stinger to mask the change.
5. Use engine-native until you need parameters, snapshots and profiling in bulk; adopt FMOD or Wwise only when a trigger in `references/music-and-sfx-systems.md` fires (licence budget terms are volatile, verify).

### C. Design an SFX family (for example UI)
1. Fix the family timbre: material, attack shape, pitch centre, length cap.
2. Define the event ladder: tap, select, confirm, cancel, error, reward small, reward big, level up.
3. Assign roles by spectral and temporal slot so sounds do not mask each other (transient click, body, tail).
4. Make variation sets for anything heard more than a few times a minute (3-5 variants, pitch and level jitter).
5. Audit on a phone speaker, then headphones. Pair with haptics (see systems reference).

### D. Loudness pass
1. Pick targets per asset class (see mixing reference); treat numbers as starting points, not standards.
2. Normalize assets per class, then balance in the engine at the bus level.
3. Play a full session through the phone speaker at a mid volume and again with headphones; fix anything that makes you reach for the volume.
4. Run `audio_post.py qc` on every shipped file (see `ai-audio-pipeline`).

### E. Voice
1. Decide which lines are hero (cutscenes, tutorial, named characters) and which are barks.
2. Write a voice brief per character: age feel, register, pace, attitude, accent family, dos and don'ts, no real-person likeness.
3. Cast by synthetic voice design or licensed actors; never clone a real performer without written, use-specific consent.
4. Credit AI voices in settings or credits and in store disclosure where policy asks (see `legal-ethics`).

## Mobile specifics

- Output routes change mid-session: speaker, wired, Bluetooth (adds latency, often 100 ms or more, never tune timing to it), AirPlay. Re-evaluate loudness and low-end content per route if the engine allows.
- iOS: the audio session category decides whether the silent switch mutes you and whether you mix with the user's music. Default games to a mixing, silent-switch-respecting category unless audio is the product. Android: request audio focus, duck or pause on loss, resume on gain.
- Memory and CPU: decoded PCM is large. Preload short SFX, stream music and VO. Cap simultaneous voices (a budget of tens, not hundreds) and steal the quietest or oldest.
- Battery and heat: avoid many simultaneous compressed decodes; prefer lightly compressed or PCM for hot short sounds.
- Sessions are 1-5 minutes. The first 10 seconds carry the identity: a signature motif at the start, and a short quiet moment is fine.
- Many players are muted. Never put required information only in audio.

## Anti-patterns

| Anti-pattern | Detect by | Fix |
|---|---|---|
| Ten unrelated cues, no identity | Cues differ in key, tempo family and palette | Audio bible with palette and key family; regenerate to it |
| Music loops audibly at the seam | Click or energy dip at loop point | Cut at bar boundaries, check seam with qc, add tail overlap |
| Identical SFX repeated | Player notices the same sample within 5 hits | 3-5 variants, pitch and level jitter, no immediate repeat |
| Everything loud | Reaching for volume, clipping meters | Per-class targets, bus compression, headroom |
| Music masks UI feedback | Feedback inaudible during busy music | Duck music 2-4 dB under key SFX, carve mid band |
| Tuned for studio monitors | Fine on headphones, thin on a phone | Review on phone speaker first |
| Ignoring the silent switch and interruptions | Audio plays over a call or in silent mode | Correct session category, interruption handlers |
| Voice cloned without consent | Reference is a real performer | Synthetic design or signed consent; disclose AI |
| Generating before the style lock | Bulk cues do not match | Human checkpoint on one cue per class first |
| Adaptive for its own sake | Layers nobody notices | Cut to the cheapest model that expresses state |

## Using the ontology

- State lives in `.gamestudio/` (`gs.py`): the audio bible path, cue list and approval status. Every generated or imported asset gets an entry in the asset manifest (`asset-manifest.schema.json`) with provider, model, plan tier at generation time, prompt, seed, licence and review status.
- Audio events map to the ontology's verbs and feedback: each verb needs an acknowledge sound, each aesthetic target (tension, mastery, delight) a music or SFX answer. Resource flows with reward tiers drive the escalation ladder.
- Tools: `${CLAUDE_PLUGIN_ROOT}/scripts/audio_post.py` (normalize, trim, loop, convert, qc); `${CLAUDE_PLUGIN_ROOT}/scripts/gs.py` for state. Agent: `arcosian:audio-director`.

## Reference library

| File | Contains | Read when |
|---|---|---|
| `references/audio-bible-and-identity.md` | Audio bible template, sonic identity method, reference tracks, prompt vocabulary, cue list | Starting a project or reviewing coherence |
| `references/music-and-sfx-systems.md` | Re-sequencing, layering, stingers, loops, Godot and Unity wiring, middleware triggers, SFX categories, layering, variation, escalation, haptics | Designing or implementing music and SFX behaviour |
| `references/mixing-implementation-voice.md` | Buses, ducking, loudness, formats, streaming, iOS and Android sessions, VO direction, barks, consent, AI disclosure | Setting up the mix, shipping on devices, directing voice |

## Related skills

- `ai-audio-pipeline` - which services generate what, pipelines, post and QC.
- `audio-production` - the command that runs the whole audio pass.
- `game-feel` - juice and feedback timing that audio must match.
- `mobile-ux` - mute-first design, interruptions, haptic use.
- `narrative-design` - tone bible and dialogue that voice direction serves.
- `legal-ethics` - AI disclosure, consent, licences.
- `accessibility-localization` - captions, visual cover for audio, localized VO.
- `technical-art` - synchronizing VFX with audio events.
