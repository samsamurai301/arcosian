# Engine-native audio and the native-versus-middleware decision

Most games do not need FMOD or Wwise. This file lists what Godot, Unity and the web platform give you without middleware, where each runs out, and a decision table that weighs team size, platforms and budget. Godot items refer to 4.x; check the class reference for your exact version. Items marked "verify" were taken from search summaries or memory, not from a fetched official page.

## Contents
1. What native audio does well
2. Godot 4.x
3. Unity
4. Web
5. Where native runs out
6. Decision table
7. Migration and exit costs
8. Worked decisions

## 1. What native audio does well

- Play one-shots and loops, positional (2D and 3D) with attenuation, panning and pitch.
- Group sounds on buses or mixer groups, apply effects (reverb, EQ, compression) and set group volume.
- Cross-fade music, and with recent Godot, do clip transitions and layered streams.
- Fit a small team: no extra tool, no extra licence, no bank build step, one fewer thing in CI.

## 2. Godot 4.x

| Feature | Class or system | Notes |
|---|---|---|
| Buses | `AudioServer`, the Audio bus layout (a resource file) | Bus tree, per-bus effects, send routing, mute/solo/volume |
| Players | `AudioStreamPlayer`, `AudioStreamPlayer2D`, `AudioStreamPlayer3D` | 2D/3D have distance attenuation and panning; 3D adds doppler and area-based bus overrides |
| Randomised sound | `AudioStreamRandomizer` | Random pitch, volume and stream choice; use for footsteps and impacts |
| Many simultaneous sounds | `AudioStreamPolyphonic` | Several voices on one player with low overhead; added in Godot 4.1 (verify) |
| Synchronised layers | `AudioStreamSynchronized` | Plays sub-streams together from one start; up to 32 sub-streams per the 4.3 class reference. Set each layer's volume to do vertical layering |
| Interactive music | `AudioStreamInteractive` | Clips with transition rules and a state-style switch; supports transitions at a time such as next beat or bar (verify exact options in the class reference) |
| Playlist | `AudioStreamPlaylist` | Sequential or random playback with simple next-track transitions |
| Formats | WAV, Ogg Vorbis, MP3 | Use Ogg for music and long sounds, WAV for short SFX |

AudioStreamInteractive, AudioStreamSynchronized and AudioStreamPlaylist are listed as AudioStream subclasses in the Godot 4.3 class reference; the interactive features arrived in 4.3 (verify against the 4.3 release notes, which I could not fetch). A forum thread from the 4.3 era suggests nesting an AudioStreamInteractive inside an AudioStreamSynchronized for layered music with transition tables. One forum user reported a start delay on AudioStreamPlaylist that did not occur with AudioStreamInteractive; test latency on your target.

Godot patterns:
1. Create buses `Master > Music, SFX, UI, Voice`. Put the player sliders on these buses with `AudioServer.set_bus_volume_db` and convert slider values with `linear_to_db`.
2. Duck music under voice with a compressor on Music whose sidechain is the Voice bus.
3. Autoload an `Audio` singleton that owns music state and pools one-shot players, so scenes do not hold audio logic.
4. For web exports, test the first-input unlock (section 4) and any sample/streaming playback mode your Godot version offers for web (4.3 added web sample playback; verify).

Limits: no event authoring UI, no profiler with live mix view comparable to Wwise or FMOD, no parameter-curve system, no built-in voice stealing by priority across the whole mix (verify), and designers need the editor and scene files.

## 3. Unity

| Feature | System | Notes |
|---|---|---|
| Mixer | `AudioMixer` asset with groups (`AudioMixerGroup`) | Effects per group, send/receive, Duck Volume effect for ducking |
| Exposed parameters | `AudioMixer.SetFloat("MusicVol", dB)` | Expose a parameter in the editor, then set it from code |
| Snapshots | `AudioMixerSnapshot`, `TransitionTo(seconds)`; `AudioMixer.TransitionToSnapshots` blends several | Mix states such as paused or underwater |
| Sources | `AudioSource` (spatial blend 0 to 1, rolloff curves) | Pool them; do not instantiate per sound |
| Load types | Decompress On Load, Compressed In Memory, Streaming | Per-clip import settings |
| Formats | Vorbis, ADPCM, PCM (and platform hardware options) | ADPCM for short frequent SFX |
| Scheduling | `AudioSource.PlayScheduled`, `AudioSettings.dspTime` | Sample-accurate starts for beat-synced music |

Native Unity has no interactive music system. You build horizontal re-sequencing and vertical layering yourself with `PlayScheduled` and volume ramps, or use Timeline. That is workable for a few tracks and painful beyond about a dozen interlocking cues.

Unity patterns:
1. Groups `Master > Music, SFX, UI, Voice`; expose volume parameters; map sliders with `Mathf.Log10(v) * 20`, clamping the floor (for example 0.0001).
2. Snapshots for Default, Paused, Dialogue, Underwater. Transition times 0.2 to 1 s (a default, tune by ear).
3. Beat sync: read `AudioSettings.dspTime`, compute the next bar boundary, `PlayScheduled` the next clip on a second source, and ramp the first out.

## 4. Web

Browsers block audio until the user interacts with the page. Rules:
1. Create or resume the `AudioContext` inside the first pointer, key or touch handler (`audioContext.resume()`). A context created before a gesture starts in the suspended state.
2. Show a clear "tap to start" screen. It doubles as the unlock input. Do not start music before it.
3. After a tab is hidden and shown, or after an interruption, the context can suspend again on some browsers; resume on `visibilitychange` and on the next input.
4. iOS Safari also respects the device silent switch for some audio paths (verify on your target iOS version) and needs a gesture for each first play on an element in older versions.

Codec support (verify at ship time; detect with `HTMLAudioElement.canPlayType` and `AudioContext.decodeAudioData` instead of user-agent sniffing):

| Codec / container | Support summary (as I know it, unverified for Oct 2026) |
|---|---|
| MP3 | Universal |
| AAC in MP4/M4A | Universal on current browsers |
| Ogg Vorbis | Chrome, Firefox, Edge yes; Safari historically no or late |
| Opus (in WebM or Ogg) | Chrome, Firefox, Edge yes; Safari support arrived later and varies by container |
| WAV (PCM) | Universal, large |

Default plan: ship AAC (M4A) as the universal choice and Opus/Ogg as an optional smaller fallback, or ship MP3 if you want one file. Engines that export to web (Godot, Unity) handle decoding themselves; check how the engine's web build handles audio threads and memory. Streaming big music files over the network needs HTTP range support and a loading state.

Latency: Web Audio output latency is often tens of milliseconds and device-dependent. Do not promise tight rhythm timing without a calibration screen.

## 5. Where native runs out

Signs it is time to consider middleware:
- Audio staff (a sound designer) who must iterate without a programmer or a rebuild.
- More than about 50 to 100 distinct events that share behaviour (variation, ducking rules, priorities).
- Complex interactive music with many states and transition rules.
- A need for live profiling and mixing while the game runs on a console or phone.
- A platform codec or hardware path the engine does not expose.
- Dialogue localisation with many languages and per-language banks.

## 6. Decision table

| Situation | Choose | Reason |
|---|---|---|
| Solo or 2 people, no dedicated audio person, jam or small game | Native | Zero setup, no licence |
| Casual mobile or hyper-casual, mostly one-shots and one music loop | Native | Middleware adds build size and steps |
| Web game | Native (or FMOD if you already own it and it has an HTML5 build; verify) | Wwise has no known first-party web runtime |
| Godot project with a dedicated sound designer and rich adaptive music | Native first (4.3 interactive streams); FMOD via community extension if you outgrow it | Community extension carries upgrade risk |
| Unity or Unreal with an audio specialist, console targets, many events | FMOD or Wwise | Official integrations |
| Team already trained in one tool | That tool | Training cost dominates |
| Heavy interactive music and hierarchical mixing, large team | Wwise | Strong music and profiler tooling (judgement, not a measured claim) |
| Small team that wants fast iteration and a simple model, Unity | FMOD | Event-based model is quick to learn (judgement) |
| Budget under the Indie threshold of either tool | Either is free for the game | Check both licences and credit requirements |
| Budget above $600k (FMOD) or $250k (Wwise) | Price the licence per game or platform before committing | See the licence sections |

Tie-breakers in order: (1) does an official integration exist for the engine; (2) who will author, and which tool do they know; (3) platforms, since console certification may need the middleware vendor's platform packages; (4) licence cost at your budget; (5) the exit cost.

## 7. Migration and exit costs

- Native to middleware: sounds move into events one by one. Keep a thin `Audio.Play(id)` wrapper from day one so game code never names engine or middleware classes. The wrapper is the cheapest insurance.
- FMOD to Wwise or back: authoring content (events, parameter curves, music logic) does not convert. Source WAV files do. Budget re-authoring time, not code time.
- Banks are version-locked to the runtime; upgrading the middleware mid-project means regenerating all banks.

## 8. Worked decisions

1. A 3-person Godot 4.3 puzzle game, one music loop per world, 40 SFX. Native. Buses, a randomiser for tile sounds, an AudioStreamInteractive with two clips for calm and tense music.
2. A 12-person Unity action game for PC and Switch, 400 events, a composer who iterates daily, layered combat music. FMOD or Wwise. Choose by the composer's skills and by the licence at the studio's budget.
3. A browser rhythm game. Native Web Audio with a calibration screen; middleware would add weight and little else.
