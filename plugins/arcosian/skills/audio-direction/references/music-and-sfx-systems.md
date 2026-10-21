# Music and SFX Systems

This file covers how sound behaves inside the game: adaptive music models (horizontal re-sequencing, vertical layering, stingers), beat and bar transitions, loop engineering rules, engine wiring in Godot (AudioStreamInteractive) and Unity (scheduled playback), the triggers that justify FMOD or Wwise, and then the SFX side: categories, layering recipes, variation, reward escalation, small-speaker design and haptic pairing. Use it when deciding what music structure to build and request from generation, when implementing it, and when designing a feedback sound set.

## Contents
1. Vocabulary and timing math
2. Horizontal re-sequencing
3. Vertical layering
4. Stingers
5. Loop engineering rules
6. Godot implementation
7. Unity implementation
8. When FMOD or Wwise pay off
9. SFX categories
10. Layering recipe
11. Variation
12. Reward escalation
13. Small-speaker design
14. Haptic pairing
15. Voice budget and priority
16. Test checklist

## 1. Vocabulary and timing math

- **Horizontal re-sequencing**: switch between separate musical sections at musically valid points.
- **Vertical layering** (also remixing): several time-aligned stems play together; volumes change with game state.
- **Stinger**: a short cue played over or instead of the bed to mark an event.
- **Quantization**: delaying an action to the next beat or bar so it lands musically.
- **Loop body**: the repeating section; **intro** and **outro/tail** are optional one-shot parts.

Timing formulas (4/4 unless noted):
```
beat_s      = 60 / BPM
bar_s       = beats_per_bar * 60 / BPM
loop_len_s  = bars * bar_s
samples     = round(loop_len_s * sample_rate)     # keep integer: choose BPM/bars so this is whole, or trim to whole samples
max_wait_s  = bar_s   # worst-case latency of a next-bar quantized transition
```
Worked example: 120 BPM, 4/4 gives bar_s 2.0 s; an 8-bar loop is 16.0 s, which is 768,000 samples at 48 kHz. At 100 BPM, bar_s is 2.4 s and an 8-bar loop is 19.2 s. A next-bar transition at 90 BPM can wait up to about 2.67 s; if the state change is urgent, add a stinger or use next-beat quantization (about 0.67 s).

Decide per transition whether waiting is acceptable. Player-caused events usually need an immediate stinger plus a quantized bed change; system-caused changes can simply wait.

## 2. Horizontal re-sequencing

### Model
A graph of clips (sections) with a transition table: from clip, to clip, when to leave (immediate, next beat, next bar, end of clip), where to enter the destination (start, same position, previous position), and how to fade (beats-based crossfade or cut).

### Design rules
1. All sections share tempo and a key family (see `references/audio-bible-and-identity.md`).
2. Author each section to be cut at bar lines: no reverb tails or notes ringing across the section end unless a tail clip or crossfade covers them.
3. Give each section an in-point that can follow any other section; avoid sections that begin with a pickup unless you transition on the beat before.
4. Provide a loop-back for every section, otherwise the music ends when the player lingers.
5. Use "same position" entry for sibling sections that are variations of one arrangement (explore to combat at the same bar offset) to preserve groove; use "start" for distinct sections.
6. Mask difficult transitions with a short filler clip (a riser, a drum fill, a silence) or a stinger.
7. Keep the graph small: 3-6 sections cover most mobile games.

### Transition table template
| From | To | Trigger | Leave at | Enter at | Fade |
|---|---|---|---|---|---|
| menu | play | start level | next bar | start | cross 1 beat |
| play | tension | health < 30% | next bar | same position | cross 2 beats |
| tension | play | health >= 50% | next bar | same position | cross 2 beats |
| play | win | level complete | immediate stinger, then end of bar | start | cut under stinger |
| play | fail | out of moves | immediate stinger | start | fade 1 beat |
| any | menu | pause | immediate | start | fade 0.5 s |

Use hysteresis (the 30% and 50% thresholds above) so the music does not flicker at a boundary. Add a minimum dwell time (for example 8 bars) before leaving a section.

## 3. Vertical layering

### Model
Stems are rendered together from one arrangement, equal length, equal sample rate, identical loop points. A control parameter (intensity 0-1) maps to per-stem gain curves.

### Design rules
1. 3-4 stems: for example rhythm, bass and harmony, lead or counter-melody, accent texture.
2. Every stem must sound acceptable alone and in any cumulative order; build a stack order (base first, then add).
3. Smooth the parameter: attack of 1-2 beats up, release of 4-8 beats down, so layers do not flutter.
4. Map thresholds to game concepts (combo count, enemy count, time left), not raw numbers; keep one intensity scalar rather than many.
5. Start all stems at the same time and keep them synced; muted stems still play (costing CPU and memory) unless the engine can start them in sync later. On mobile, 4 streamed stereo Vorbis stems is usually fine; test on the lowest device tier.
6. Alternative to streaming many stems: pre-mix 2-3 cumulative versions and crossfade between them at bar lines. It is cheaper but less flexible.

### Gain map example
| Intensity | Rhythm | Bass/harmony | Lead | Accent |
|---|---|---|---|---|
| 0.0-0.25 | -6 dB | 0 dB | off | off |
| 0.25-0.6 | 0 dB | 0 dB | off | -9 dB |
| 0.6-0.85 | 0 dB | 0 dB | -6 dB | 0 dB |
| 0.85-1.0 | 0 dB | 0 dB | 0 dB | 0 dB |
Interpolate between rows in dB, not linear amplitude.

### Generation implications
Stems must be time-aligned. If the service provides stems, still verify equal lengths and loop cleanly; if it does not, render layer versions with identical timing parameters, or build stems by muting parts in a real-time generator (see `ai-audio-pipeline` for options and caveats).

## 4. Stingers

- Purpose: instant, event-linked feedback in the music's world: level complete, unlock, big reward, fail, near-miss.
- Length 1-6 seconds. Same key as the bed, ending on a resolved chord or a clean decay.
- Play on top of the bed with a 2-4 dB music duck for about 300-600 ms, or cut the bed to silence for the stinger when the moment deserves it.
- Quantize start to the next beat only if the latency stays under about a beat; otherwise play immediately and rely on key compatibility.
- Provide 2-3 variants for events that repeat; never an identical stinger twice in a row.
- Write the motif into the stingers (see identity reference).

## 5. Loop engineering rules

1. Loop lengths are whole bars. Length = bars x bar_s. The loop body should end where it started harmonically (usually the tonic or a cadence that returns).
2. Cut at zero crossings or use a short crossfade (typically 10-50 ms for sample-accurate cuts; longer, up to a beat, if a tail overlaps the start) so there is no click.
3. Ensure the tail of the source (reverb, decay) overlaps the head at the seam; the seam should be inaudible when loop-played repeatedly.
4. Prefer sample-accurate loop points in the engine. Engine fact (checked on Godot 4.7.2): `AudioStreamOggVorbis` and `AudioStreamMP3` expose only a forward `loop` and a `loop_offset`, while `AudioStreamWAV` exposes `loop_mode` (disabled, forward, ping-pong, backward) with `loop_begin` and `loop_end` in samples; compressed music can add decoder padding at the seam, so test seams in-engine, not only in an editor.
5. No fade-in or fade-out inside a loop file; fades belong to transitions.
6. Intro plus loop: play the intro once then the loop body; in engines without such a feature, schedule the loop clip at the intro's end time.
7. Check the seam numerically and by ear on a phone: compare energy (RMS) in the 50 ms either side; look for clicks. `audio_post.py loop` creates a loop of bars x beats at a given BPM with a crossfade; `audio_post.py qc` checks level, true peak, clipping and DC offset. Seam inspection beyond that is by listening.
8. Keep a loop at least 30-60 seconds before it repeats if play sessions are long, to reduce fatigue; for short hyper-casual sessions, shorter is fine.

## 6. Godot implementation

Godot 4.x provides `AudioStreamInteractive`: a stream resource holding clips plus a transition table, played by an `AudioStreamPlayer`. The facts below were checked on Godot 4.7.2 with a headless introspection run (`ClassDB.class_exists`, `ClassDB.class_get_method_list`) and a playback run on the dummy audio driver.

- **Transition vocabulary.** A transition leaves at `TRANSITION_FROM_TIME_IMMEDIATE`, `_NEXT_BEAT`, `_NEXT_BAR` or `_END`; enters the destination at `TRANSITION_TO_TIME_START`, `_SAME_POSITION` or `_PREVIOUS_POSITION`; and fades with `FADE_DISABLED`, `FADE_IN`, `FADE_OUT`, `FADE_CROSS` or `FADE_AUTOMATIC` over a number of **beats**, not seconds. Filler clips, a "hold previous" option and per-clip auto-advance (`AUTO_ADVANCE_DISABLED`, `_ENABLED`, `_RETURN_TO_HOLD`) exist too. `AudioStreamInteractive.CLIP_ANY` (-1) is the wildcard clip index and is how the `any` row of a transition table is expressed (an immediate `CLIP_ANY` to `menu` transition switched from another clip in 56 ms).
- **`add_transition` parameter order.** `add_transition(from_clip: int, to_clip: int, from_time: TransitionFromTime, to_time: TransitionToTime, fade_mode: FadeMode, fade_beats: float, use_filler_clip: bool = false, filler_clip: int = -1, hold_previous: bool = false)`. The snippet below uses exactly that order. Unit-test the table with `has_transition`, `get_transition_list` (a flat list of from, to pairs) and the `get_transition_*` getters.
- **Beat and bar timing comes from the clip streams.** `bpm`, `beat_count` and `bar_beats` are properties of `AudioStreamOggVorbis` and `AudioStreamMP3` (they are also the importer's `bpm`, `beat_count` and `bar_beats` options, and edited import values reach the loaded resource) and the interactive stream uses them. With `bpm = 120` and `bar_beats = 4`, a `NEXT_BAR` switch requested 0.5 s into playback took effect at the 2.0 s bar line, about 1.6 s after the call, and `NEXT_BEAT` waited for the next beat. `AudioStreamWAV` has no BPM properties, and a clip with `bpm` left at 0 behaves as immediate (the same `NEXT_BAR` switch completed in under 0.1 s). Use Ogg Vorbis (or MP3) clips with the BPM fields set for any bar-aligned transition, even though WAV offers sample-accurate loop points.
- **Missing table entries.** A switch with no matching entry still happens (after about half a second with 120 BPM clips), but on the engine's own timing, so define every pair you use.

```gdscript
extends Node
class_name MusicDirector

@export var player: AudioStreamPlayer
var _playback: AudioStreamPlaybackInteractive

func _ready() -> void:
	var interactive := AudioStreamInteractive.new()
	interactive.clip_count = 3
	interactive.set_clip_name(0, &"menu")
	interactive.set_clip_stream(0, load("res://audio/music/menu.ogg"))
	interactive.set_clip_name(1, &"play")
	interactive.set_clip_stream(1, load("res://audio/music/play.ogg"))
	interactive.set_clip_name(2, &"tension")
	interactive.set_clip_stream(2, load("res://audio/music/tension.ogg"))
	interactive.initial_clip = 0
	# add_transition(from_clip, to_clip, from_time, to_time, fade_mode, fade_beats[, use_filler_clip, filler_clip, hold_previous])
	# Clips must be Ogg Vorbis or MP3 with bpm, beat_count and bar_beats set, or the bar-aligned transitions fire immediately.
	interactive.add_transition(
		0, 1,
		AudioStreamInteractive.TRANSITION_FROM_TIME_NEXT_BAR,
		AudioStreamInteractive.TRANSITION_TO_TIME_START,
		AudioStreamInteractive.FADE_CROSS, 1.0)
	interactive.add_transition(
		1, 2,
		AudioStreamInteractive.TRANSITION_FROM_TIME_NEXT_BAR,
		AudioStreamInteractive.TRANSITION_TO_TIME_SAME_POSITION,
		AudioStreamInteractive.FADE_CROSS, 2.0)
	player.stream = interactive
	player.play()
	_playback = player.get_stream_playback() as AudioStreamPlaybackInteractive

func to_state(state: StringName) -> void:
	if _playback != null:
		_playback.switch_to_clip_by_name(state)
```
Notes: set the loop on each clip stream (Ogg and MP3 expose `loop` and `loop_offset`; WAV exposes `loop_mode`, `loop_begin` and `loop_end` in samples) together with the BPM fields; clips of the same arrangement must share bar length. `get_stream_playback()` returns an `AudioStreamPlaybackInteractive` only after `play()` has been called on a player that is inside the scene tree, and its whole API is `switch_to_clip_by_name(name)`, `switch_to_clip(index)` and `get_current_clip_index()`. Route the player to the Music bus.

**Vertical layering with `AudioStreamSynchronized`.** The class exists in 4.7.2 (`ClassDB.class_exists(&"AudioStreamSynchronized")` returned true; on an older engine make that call before relying on it, and fall back to N `AudioStreamPlayer` nodes started in the same frame with tweened `volume_db`). One `AudioStreamPlayer` plays up to 32 stems in sync (`stream_count`, `MAX_STREAMS`): `set_sync_stream(index, stream)` assigns a stem and `set_sync_stream_volume(index, volume_db)` sets its gain, with an inspector range of -60 to +12 dB, so -60 dB is "off". Gains can change while it plays (in the test, two stems at 0 dB peaked at -3.1 dBFS, both at -60 dB at -63 dBFS, and one restored gave -8.7 dBFS). The gain lives on the shared resource, so ramp a stem with `Tween.tween_method` calling `set_sync_stream_volume`, not by tweening `AudioStreamPlayer.volume_db`, which would move every stem together. The gain map from section 3 becomes (tested on 4.7.2: each row's gains were reached, and a ramp halfway between two rows sat halfway in dB):

```gdscript
extends Node
class_name MusicLayers

const OFF_DB: float = -60.0  # bottom of the per-stem volume range
const ROW_STARTS: PackedFloat32Array = [0.0, 0.25, 0.6, 0.85]  # intensity where each gain-map row begins
# dB per stem (rhythm, bass/harmony, lead, accent), one row per range of the gain map
const GAINS_DB: Array = [
	[-6.0, 0.0, OFF_DB, OFF_DB],
	[0.0, 0.0, OFF_DB, -9.0],
	[0.0, 0.0, -6.0, 0.0],
	[0.0, 0.0, 0.0, 0.0],
]

@export var player: AudioStreamPlayer
var _layers: AudioStreamSynchronized
var _tween: Tween

func start(stems: Array[AudioStream]) -> void:
	_layers = AudioStreamSynchronized.new()
	_layers.stream_count = stems.size()
	for i in stems.size():
		_layers.set_sync_stream(i, stems[i])
		_layers.set_sync_stream_volume(i, GAINS_DB[0][i])
	player.stream = _layers
	player.play()  # all stems start sample-aligned

## Ramp every stem to the gain-map row for `intensity`, linearly in dB over `seconds`
## (about 1-2 beats going up, 4-8 beats going down).
func set_intensity(intensity: float, seconds: float) -> void:
	var row: int = ROW_STARTS.size() - 1
	while row > 0 and intensity < ROW_STARTS[row]:
		row -= 1
	if _tween != null:
		_tween.kill()
	if seconds <= 0.0:
		for i in _layers.stream_count:
			_layers.set_sync_stream_volume(i, GAINS_DB[row][i])
		return
	_tween = create_tween().set_parallel(true)
	for i in _layers.stream_count:
		_tween.tween_method(func(db: float) -> void: _layers.set_sync_stream_volume(i, db),
				_layers.get_sync_stream_volume(i), GAINS_DB[row][i], seconds)
```

Godot specifics: buses live in `AudioServer`; ducking is done by tweening a bus volume or an `AudioEffectCompressor` with sidechain on the music bus; SFX use pooled `AudioStreamPlayer` nodes (non-positional UI) or `AudioStreamPlayer2D`; `AudioStreamRandomizer` provides random selection and pitch/volume randomization, which covers most variation needs.

## 7. Unity implementation

Engine-native pieces: `AudioSource.PlayScheduled` with `AudioSettings.dspTime` for sample-accurate starts, `AudioMixer` with snapshots and exposed parameters, `AudioMixerGroup` buses. Unity has no built-in horizontal re-sequencing graph; you write a small scheduler.

```csharp
using UnityEngine;

public sealed class BarScheduler : MonoBehaviour
{
    [SerializeField] AudioSource[] sources = new AudioSource[2]; // ping-pong pair
    [SerializeField] double bpm = 120.0;
    [SerializeField] int beatsPerBar = 4;
    int _next;
    double _loopStartDsp;   // dsp time when current section began
    double _sectionLenSec;  // length of current section in seconds

    double BarSeconds => beatsPerBar * 60.0 / bpm;

    public void BeginSection(AudioClip clip, int bars)
    {
        var src = sources[_next];
        _next = 1 - _next;
        // Start at the next bar line of the running section (or now + small lead if none).
        double now = AudioSettings.dspTime;
        double startAt = _sectionLenSec <= 0.0
            ? now + 0.1
            : _loopStartDsp + System.Math.Ceiling((now - _loopStartDsp) / BarSeconds) * BarSeconds;
        src.clip = clip;
        src.loop = true;
        src.PlayScheduled(startAt);
        var prev = sources[_next];
        if (prev.isPlaying) prev.SetScheduledEndTime(startAt + 0.05); // short overlap, add a fade in the mixer
        _loopStartDsp = startAt;
        _sectionLenSec = bars * BarSeconds;
    }
}
```
This is a minimal pattern: add gain fades (mixer volume or per-source) for crossfades, use `clip.frequency` and `clip.samples` for exact loop lengths, and keep the DSP buffer small enough for acceptable latency but large enough to avoid glitches on low-end Android (test; do not assume a value). Unity import: Vorbis for streamed music with a quality setting; PCM or ADPCM for short SFX; override per platform. Also check whether your Unity 6 version offers Audio Random Containers or other native features before writing custom code (not verified here).

## 8. When FMOD or Wwise pay off

Engine-native is enough when: one or two music states, no per-parameter mixing, few designers, tight build size. Adopt middleware when at least two of these hold:

| Trigger | Why middleware helps |
|---|---|
| Music with 3+ layers driven by multiple parameters | Authoring curves, previews, no custom code |
| Transitions graph with many exceptions | Visual transition rules, markers |
| A dedicated audio person or iterative design in the build | Live-connect tuning, banks swapped without code |
| Many sounds with randomization, ducking and mixer snapshots | Profiling, voice limiting, snapshot mixing |
| Platform-specific loudness or compression tuning | Per-platform encoding settings |
| Large live-ops audio updates | Bank-level content updates |

Costs: integration time, build size, another tool to automate (an agent can generate and drop files into engine-native systems more easily than it can author middleware events; scripting APIs exist but verify before relying on them). Licence terms are budget-gated and change: see the volatile facts below.

### Volatile facts (as of Oct 2026 — verify)
- FMOD: an indie tier tied to a development budget (reported under a figure in the hundreds of thousands of dollars) was listed on the official licensing page; the direct page fetch returned empty during research. Verify. Source: https://fmod.com/licensing
- Wwise: indie free tier reported with a production-budget ceiling in older sources; the current pricing page was inaccessible during research. Verify. Sources: https://blog.audiokinetic.com/free-wwise-for-indie-developers/ and Audiokinetic's current pricing page.
- Godot AudioStreamInteractive and import notes: https://docs.godotengine.org/en/stable/classes/class_audiostreaminteractive.html and https://docs.godotengine.org/en/stable/tutorials/assets_pipeline/importing_audio_samples.html
- Unity audio compression guidance: https://docs.unity3d.com/Manual/AudioFiles-compression.html

## 9. SFX categories

| Category | Examples | Rules |
|---|---|---|
| UI navigation | tap, back, tab, toggle | Very short (under about 150 ms), soft, consistent timbre, low priority, 2-3 variants for taps |
| UI feedback | confirm, cancel, error, locked | Distinct pitch contours: up confirms, down cancels, buzz or dull for error; never harsh |
| Gameplay verbs | merge, swipe, jump, place, hit | Tied to feel; must sync with animation to the frame; highest variation need |
| Reward | coin, gem, chest, level up, unlock | Escalating tiers; musical and in key; sparkle tail |
| Feedback state | low health, timer warning, combo timeout | Readable, repeatable, not annoying; allow mute-able |
| Ambience | room tone, nature bed | Looping, quiet, low CPU, optional |
| System | notification, purchase success | Calm; purchase sounds must never feel pressure-inducing (see `legal-ethics`) |
| VO barks | grunts, quips | See voice section in `references/mixing-implementation-voice.md` |

## 10. Layering recipe

Build a significant sound from four layers; each lives in a distinct band and time slot so they do not mask:

| Layer | Role | Typical band | Time |
|---|---|---|---|
| Transient | Click, snap, tap; defines the hit | 2-8 kHz | 0-30 ms |
| Body | Tone or thud; defines the identity | 200 Hz - 2 kHz | 20-250 ms |
| Tail or air | Shimmer, resonance, reverb | above 4 kHz | 100 ms - 1 s |
| Sub (optional) | Weight on headphones | below 150 Hz | 0-300 ms |

Steps: choose the body first (it must be recognizable on its own), add the transient to sell contact, add a tail for reward only (gameplay hits stay dry), add sub only if headphone weight matters and cut it from the speaker mix (high-pass the phone-speaker path or keep it low level). Align layers within about a millisecond at their attacks; check phase when stacking similar sounds. Bounce to one file per event to save voices, unless runtime variation of layers is wanted.

## 11. Variation

- Frequency of use sets variant count: heard under 5 times a session, 1 variant is fine; 5-30 times, 3-4; constantly (taps, footsteps, merges), 5-8 plus pitch/level jitter.
- Jitter ranges to start from: pitch plus or minus 2-6 percent (about 0.5-1 semitone) for non-tonal sounds, none or scale-locked steps for tonal ones; volume plus or minus 1-2 dB.
- No immediate repeat: pick randomly excluding the last played.
- Do not randomize tonal UI sounds off-key; use pitch steps from the game's scale.
- Generating variants: use the same prompt with different seeds or small prompt changes, then pick the ones that are similar enough in loudness and length to swap (see `ai-audio-pipeline`).

## 12. Reward escalation

Pseudo-code for a chain reward:
```
tier = min(chain_count - 1, MAX_TIER)           # e.g. MAX_TIER = 7
note = scale[tier % len(scale)]                  # pentatonic steps up
layers = base + (sparkle if tier >= 2) + (chord if tier >= 4) + (swell if tier >= 6)
gain = base_gain + tier * 0.5 dB                 # modest
play(pitch_shifted(sfx, note), layers, gain)
on_chain_break: tier = 0; optionally play a soft descending cue
```
Rules: cap the ladder so it cannot overwhelm; reserve the top tier for rare events; at the cap, change something other than pitch (add a stinger, brief music duck); keep each step perceptibly distinct on a phone speaker; test the loop of a 30-step chain for fatigue. For monetary rewards, never exaggerate size beyond the actual value (see `monetization` and `legal-ethics`).

## 13. Small-speaker design

- Phone speakers roll off steeply below roughly 150-300 Hz (varies by device; verify on target devices). A kick or sub that carries the meaning will vanish; add a mid-range click or harmonics so the sound survives. Synthetic bass can be given upper harmonics (saturation) to suggest weight.
- Avoid narrow harsh peaks around 2-5 kHz repeated often; they fatigue on a tiny speaker.
- Mono compatibility: check that stereo SFX and music do not cancel when summed (phone speakers are effectively mono). Wide reverb or chorus may thin out.
- Test at low and mid volume, not only loud.
- Noise: players use phones in noise; mid-range content and rhythmic clarity help, dynamic range should be modest.

## 14. Haptic pairing

- Pair haptics with audio events the player causes (taps, merges, impacts), not with ambient audio.
- iOS: Core Haptics for custom patterns, simpler feedback generators for taps. Android: `VibrationEffect` and predefined effects where available; support varies widely across devices, so degrade gracefully.
- Keep haptic and audio onset aligned; haptic latency is device dependent, test on device.
- Provide a haptics toggle and honour system settings; reduce intensity for frequent events (battery, fatigue).
- Table to include in the bible:

| Event | Audio | Haptic | Intensity |
|---|---|---|---|
| Tap | soft click | light tick | low |
| Merge | warm pop | medium thump | medium |
| Big reward | chime swell | short double pulse | medium-high |
| Error | muted thud | single soft pulse | low |

## 15. Voice budget and priority

- Set a maximum of simultaneous voices (a few tens is typical for casual games; tune and measure).
- Priority classes: VO and critical feedback (highest), reward, gameplay, UI, ambience (lowest). When over budget, steal the lowest priority, then the quietest, then the oldest.
- Rate-limit spammy events (for example no more than one coin sound every 50-80 ms; collapse bursts into one louder or pitched-up sound).
- Do not duck for every sound; duck for VO and for key reward moments only.

## 16. Test checklist

- [ ] Transitions land on bar lines; no clicks at seams, on device.
- [ ] Music state does not flicker; hysteresis and dwell present.
- [ ] Stems stay in sync after pause, resume and app switching.
- [ ] No identical SFX twice in a row; variant counts match the table.
- [ ] Reward ladder is audibly monotonic and capped; resets cleanly.
- [ ] Mix verified on phone speaker, wired and Bluetooth headphones.
- [ ] Voice stealing works under stress (spam test).
- [ ] Haptics present, toggleable and aligned.
- [ ] Muted play still communicates all required state.
