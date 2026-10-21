# Audio Bible and Sonic Identity

This file is the method for deciding what a game sounds like and writing it down so every later cue, generated or recorded, stays coherent. It gives a complete audio-bible template, a procedure for building sonic identity (palette, harmonic home, tempo family, motif), guidance for choosing reference tracks without copying them, a prompt vocabulary that translates taste into generator language, a cue-list format, and a review checklist. Use it at project start and whenever new cues feel like they come from a different game.

## Contents
1. Why a bible, and what it must constrain
2. Audio bible template (complete)
3. Building sonic identity
4. Reference tracks and reference sounds
5. Prompt vocabulary
6. Cue list format and sizing
7. Worked example
8. Coherence review checklist
9. Common failure patterns

## 1. Why a bible, and what it must constrain

Generated and contracted audio drifts: each request is independent, and different sessions use different wording. A bible fixes the decisions that must not drift, and gives generation a stable prefix. It must constrain five things: palette (what instruments and textures exist), harmony (key family), time (tempo family and meter), dynamics (loudness and density by state), and prohibitions (what must never appear). Everything else is freedom. The shorter the bible, the more it is read; target two to four pages. The repo template at `templates/docs/audio-bible.md` has the empty skeleton; this file explains how to fill it.

## 2. Audio bible template (complete)

Copy this structure into the project (`.gamestudio/` or the docs folder).

```markdown
# Audio Bible: <Game>

## 1. Intent
- One-sentence audio fantasy: "<the player should feel ...>"
- Three audio pillars (verbs, not adjectives): e.g. "crisp", "warm", "reward every touch"
- Session shape: typical length, muted-play expectation (percent unknown: state hypothesis)

## 2. Sonic identity
- Palette: 3-5 sound families (e.g. felt piano, soft mallets, airy pad, tape-saturated percussion)
- Forbidden: sounds that break the world (e.g. no orchestral brass, no 8-bit chip if realistic)
- Harmonic home: key(s) or mode family; how modulations are allowed
- Tempo family: base BPM and allowed multiples (e.g. 90 / 120 / 135 with half-time feel)
- Meter: default 4/4; exceptions
- Signature motif: 3-6 notes (written as scale degrees), where it appears, how it varies
- Space: dry / room / large; reverb character for music, SFX, VO

## 3. Music plan
| State | Purpose | Model | Length | Loop | Intensity layers | Tempo/key |
|---|---|---|---|---|---|---|
| Boot / title | Identity hit | One-shot or loop | 20-40 s | yes | 1 | home |
| Menu / meta | Calm, low fatigue | Loop | 60-90 s | yes | 1 | home |
| Core play | Focus, momentum | Loop + layers | 60-120 s | yes | 3-4 | home |
| Tension | Raised stakes | Layer or section | as play | yes | +1 | home or relative |
| Win / fail | Closure | Stinger | 2-6 s | no | - | home |
| Special event | Variation | Section | 60 s | yes | 2 | home family |

## 4. SFX plan
- Families: UI, gameplay (verb acknowledgements), reward, ambience, system
- Per family: timbre rule, pitch centre, max length, variation count, escalation rule
- Haptic pairing table (event, haptic type, intensity)

## 5. Voice plan
- Characters, voice briefs, which lines are hero vs barks, languages
- Provenance: synthetic design vs licensed actor; consent file locations
- AI disclosure wording for settings or credits

## 6. Mix and delivery
- Bus tree and ducking rules
- Loudness targets per class (with tolerance)
- Formats per class, sample rates, mono/stereo
- Runtime behaviour: silent switch, interruptions, headphone unplug

## 7. Provenance and licensing
- Manifest location; fields kept per asset
- Plan tier and revenue-threshold watch-list (see ai-audio-pipeline)

## 8. Reference set
- 3-5 reference tracks and 3-5 reference sound sets with "borrow / avoid" notes

## 9. Prompt prefix
- Fixed text prepended to every generation request (see section 5)

## 10. Approval log
- Style lock: who approved which cue, date, notes
```

Rule: if a field cannot be filled, write "unknown, decide by <milestone>" rather than leaving it blank.

## 3. Building sonic identity

### 3.1 Start from the fantasy, not the genre
Write what the player is doing and how it should feel in three words each for the core verb, the meta layer and the failure state. Example: a cosy merge game: "tactile, gentle, plinky". Then ask what in the real or imagined world makes that sound. Materials are a better start than genres: wood, felt, glass, paper, water, metal, synth, breath.

### 3.2 Palette (3-5 families)
- Choose one lead timbre (carries melody and the motif), one harmonic bed, one rhythmic element, one accent texture, and optionally one signature oddity.
- Each family should be describable in a phrase a generator understands.
- Test: if a cue must be described without naming the palette, it is too generic.

### 3.3 Harmonic home
- Pick a key family, not a single key: tonic plus relative minor plus the dominant area is enough for most casual games.
- Why it matters: cues in compatible keys can be crossfaded and layered without clashing. Cues in unrelated keys need a stinger, a filler or a silent gap.
- Generators often cannot guarantee key. Specify the key in the prompt, then verify by ear or an analysis tool and keep the verified key in the manifest. Treat generator key adherence as unreliable.
- Modal colour guide (starting points, taste decides): major or Lydian for open, light worlds; Mixolydian for playful and sunny; natural minor or Dorian for adventurous or mysterious; Phrygian or chromatic for menace.

### 3.4 Tempo family
- Choose a base tempo, then allowed multiples: half-time, double-time, and one relative (for example 3/4 of base only if meter allows).
- Bar length in seconds = beats per bar x 60 / BPM. At 120 BPM in 4/4, one bar is 2.0 s; at 90 BPM, about 2.67 s. Prefer tempos giving round-ish bar lengths for loop math, but do not bend the music for it.
- All adaptive sections share the base tempo exactly, otherwise bar-quantized transitions break.

### 3.5 Signature motif
- 3-6 notes, written as scale degrees (for example 1-3-5-6-5), so it transposes.
- Use it: at boot, on level complete, in a variation inside the main loop, and as the reward stinger shape.
- Vary by instrument, register and rhythm, not by pitch content, until the player recognizes it.
- Do not put it everywhere. A motif used constantly stops being a signal.

### 3.6 Space and texture
- Decide one reverb family per layer: music slightly wet, SFX mostly dry, VO as the scene needs. A single shared short plate or room gives glue.
- Decide the noise floor: some games want a faint ambience bed, others strict silence between sounds.
- Decide saturation: clean, tape-warm, or lo-fi, applied consistently.

### 3.7 Density and dynamics by state
Express as a small table: menu low, play medium, peak high, with the number of simultaneous layers and the intended loudness delta. Keep the whole range within a few LU; mobile has little dynamic headroom (see `references/mixing-implementation-voice.md`).

## 4. Reference tracks and reference sounds

### 4.1 How to use references
- A reference is for the team and for the process, not for the generator. Several services forbid artist names, song titles or label names in prompts (verify the current terms); and a generator is not a reliable cover tool. Translate the reference into attributes: tempo, instrumentation, texture, mix qualities, structure, energy curve.
- Never ask for a "sound-alike" of a named artist or track. It raises legal risk and produces generic results.
- Where a service accepts an audio reference for steering, use only audio you own or have cleared, and record that in the manifest.

### 4.2 Selecting
- 3-5 tracks across the range of states (menu, play, win), from different media: a game, a film score, a non-game record.
- For each, write: what to borrow (one thing), what to avoid (one thing), and which cue it informs.
- Add 3-5 reference sound sets for SFX: for example "satisfying coin tiers from a hyper-casual hit", "soft UI from a premium puzzler".
- Review games in your genre via `game-case-studies` and `genre-playbooks` to see audio conventions players expect, then decide where to match and where to differ.

### 4.3 Reference analysis template
| Field | Notes |
|---|---|
| Source and cue | what, where |
| Tempo (approx.) | measured |
| Key or mode (approx.) | by ear or tool |
| Palette | families |
| Structure | intro, loop body, tail |
| Energy curve | how it builds |
| Mix | wide/narrow, bright/dark, dry/wet |
| Borrow | one thing |
| Avoid | one thing |

## 5. Prompt vocabulary

Generators respond to concrete descriptors. Build prompts as: role, genre or feel, palette, tempo and key, structure, dynamics, mix, exclusions. Keep a fixed prefix (palette, tempo family, key family, exclusions) and vary the tail per cue.

### 5.1 Descriptor lists (use as menus)
| Axis | Words that tend to steer well |
|---|---|
| Energy | calm, relaxed, steady, driving, building, urgent, frantic |
| Mood | warm, cosy, playful, wistful, mysterious, heroic, tense, triumphant, melancholic |
| Timbre | soft felt piano, glass mallets, plucked strings, warm analog pad, airy flute, muted guitar, wooden percussion, shaker, soft sub bass |
| Texture | sparse, layered, minimal, lush, dry, spacious, lo-fi, tape-saturated |
| Rhythm | half-time, four-on-the-floor, syncopated, swung, straight eighths, no drums, brushed |
| Structure | steady loop body, no fade-out, ends on tonic, 4-bar phrases, section changes every 8 bars |
| Mix | centred bass, wide pad, bright top, restrained low end, no heavy sub (small speakers) |
| Exclusions | no vocals, no lyrics, no spoken words, no sudden drops, no cymbal crashes, no tempo changes, no key changes |

### 5.2 Music prompt template
```
Instrumental game music for <state> in a <genre/feel> mobile game.
Feel: <3 mood words>. Palette: <palette phrases>. Tempo: <BPM> BPM, <meter>, steady, no tempo changes.
Key: <key/mode>, no key changes. Structure: <e.g. 8-bar intro then steady loop body ... ends cleanly>.
Dynamics: <flat/builds>. Mix: <mix notes>. Exclude: no vocals, <others>.
```

### 5.3 SFX prompt template
```
<Sound event> for a <world> game UI/gameplay. Material: <glass/wood/metal/synth>. Character: <soft/crisp/bright>.
Length <seconds>, sharp attack, no reverb tail, no background noise, single hit.
```
For tonal UI sounds, state pitch centre or key so a set stays consistent.

### 5.4 Voice brief template
```
<Character>: <age feel>, <gender presentation if any>, <accent family>, <register: low/mid/high>,
<pace: slow/measured/quick>, <attitude: dry, warm, anxious>, <breathiness/clarity>, <what it must not sound like>.
```
Describe an invented voice; never name or imitate a real person.

### 5.5 Do and do not
- Do state exclusions; generators otherwise add vocals, fades and drops.
- Do state structure for loops ("steady section, no ending flourish").
- Do not stack more than about five descriptors per axis; they conflict.
- Do not rely on a prompt for exact BPM or key; measure the result.

## 6. Cue list format and sizing

A cue list is the production contract. One row per deliverable.

| Field | Example |
|---|---|
| id | `mus_play_01` |
| class | music, sfx, amb, vo |
| state or event | core play, calm |
| duration | 90 s loop |
| loop | yes, bar length 2.0 s, 45 bars |
| tempo/key | 120 BPM, D Dorian |
| layers | 3 stems: bass+drums, harmony, lead |
| variants | 1 |
| priority | must / should / could |
| status | brief, candidate, approved, final |
| source | provider, model, plan tier, prompt id, seed |
| licence | per manifest |

### Typical sizes for a casual mobile game (starting estimates)
| Class | Count | Notes |
|---|---|---|
| Music loops | 3-6 | menu, play (with stems), special, plus title |
| Stingers | 4-8 | win, fail, level up, reward, unlock |
| UI SFX | 12-25 | with 2-3 variants for frequent ones |
| Gameplay SFX | 15-50 | verb acknowledgements plus failures |
| Reward ladder | 5-8 tiers | escalating |
| Ambience | 0-3 loops | optional |
| VO | 0 to hundreds | barks cheap; hero lines expensive |

Cut anything that does not change player behaviour or feeling. A tight set polished well beats a large unfinished set.

## 7. Worked example

Game: a cosy match-and-decorate puzzler, 2-minute sessions, many players muted.

- Intent: "A warm, tactile reward for every tidy move."
- Pillars: tactile, gentle, escalating.
- Palette: felt piano (lead), warm pad (bed), soft mallet percussion, light shaker, airy chime accents. Forbidden: hard synth leads, heavy bass, cymbal crashes.
- Harmonic home: C major / A minor family; Lydian colour allowed for celebration.
- Tempo family: 100 BPM base; half-time for menus. Bar at 100 BPM in 4/4 is 2.4 s.
- Motif: 1-3-5-6-5 (scale degrees), felt piano; chime version for level complete.
- Music plan: menu loop (64 s, one layer), play loop (96 s, three stems: soft percussion, harmony, lead), win stinger (3 s), fail stinger (2 s, no downer).
- SFX: wooden-glass tile taps with five pitched variants (pentatonic steps), combo ladder climbing the pentatonic scale through eight tiers then resetting, each tier adding a chime layer.
- Mix: music bus sits roughly 3-5 dB under the SFX bus at peak play (tune on device); duck music 2-3 dB for 400 ms under big rewards.
- Prefix: "Instrumental, warm cosy puzzle game music, felt piano, warm pad, soft mallets, 100 BPM, 4/4, C major, steady, no tempo changes, no key changes, no vocals."
- Style lock: user approves one play loop, the tile tap set and the win stinger before bulk.

## 8. Coherence review checklist

- [ ] Every cue declares tempo and key in the manifest, and measured values match.
- [ ] No cue contains an excluded sound; scan stems or listen on mute-removed sections.
- [ ] The motif is recognizable at boot, level complete and in the play loop, and not elsewhere.
- [ ] UI sound set shares timbre and pitch centre.
- [ ] Reward ladder is monotonic in perceived excitement.
- [ ] Loudness per class is within tolerance (see qc in `ai-audio-pipeline`).
- [ ] Music and SFX do not mask each other in busy play.
- [ ] Reviewed on phone speaker, wired headphones, and a Bluetooth route.
- [ ] Muted play still communicates all required state.
- [ ] Provenance and licence recorded; plan tier and revenue watch noted.

## 9. Common failure patterns

| Pattern | Symptom | Remedy |
|---|---|---|
| Genre-first identity | "Lo-fi chill" label, generic output | Materials and verbs first, then genre |
| Key chaos | Layers clash when crossfaded | Declare key family, verify, regenerate outliers |
| Tempo drift | Bar-quantized transitions misalign | Measure BPM of every cue, trim or regenerate |
| Overlong bible | Nobody reads it | Cut to constraints that change decisions |
| Motif overuse | Players tune it out | Reserve for milestones |
| Unreviewed prompts | Output includes vocals or fades | Keep a fixed prefix with exclusions |
| Style lock skipped | 30 cues that do not match | One cue per class approved first |
