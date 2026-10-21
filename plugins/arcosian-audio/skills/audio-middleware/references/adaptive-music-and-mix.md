# Adaptive music and mix

How to build music that reacts to the game and a mix that stays clear, with numbers for transitions, ducking, voice limits, loudness, memory and compression. It is engine-neutral: each technique names how FMOD, Wwise and engine-native audio do it. For creative direction (what the music should feel like, loudness philosophy, stems) read `/arcosian:audio-direction` and `/arcosian:audio-production`; this file is the implementation layer. Numbers marked "default" or "estimate" are starting points to tune by ear and by measurement.

## Contents
1. Interactive music techniques
2. Transition rules and timing
3. Mix snapshots and ducking
4. Voice limits and priorities
5. Loudness targets
6. Memory and streaming budgets
7. Compressed formats per platform
8. Worked example
9. Test checklist

## 1. Interactive music techniques

| Technique | What it is | FMOD | Wwise | Native |
|---|---|---|---|---|
| Horizontal re-sequencing | Switch between pre-composed segments on musical boundaries | Event timeline with transition regions and a parameter-driven logic | Music Switch/Playlist Container with Segments and transition rules | Godot `AudioStreamInteractive`; Unity `PlayScheduled` |
| Vertical layering | Stack stems and fade them by intensity | Parameter-controlled volume on tracks | RTPC on Music Tracks, or Blend Containers | Godot `AudioStreamSynchronized`; Unity several sources and ramps |
| Stinger | Short phrase played on top, quantised to the beat | Instrument or a separate event synced to the main timeline | Music Trigger plus Stinger in the music object | Schedule on the next beat |
| Beat-synced transition | Change happens at the next beat, bar or marker | Quantised transitions and markers | Transition rules: exit at next bar/beat/grid | Compute from tempo and sample time |
| Tail and pre-entry | Reverb tails and pickup notes that cross a cut | Transition timeline pre/post regions | Music segment pre-entry and post-exit | Overlap sources by the tail length |

Choosing the model:
- Two or three states (calm, tension) with long scenes: vertical layering on one tempo and key, 3 to 5 stems.
- Distinct sections (explore, combat, boss, victory): horizontal with a transition matrix, and stingers for events (level up, death).
- Puzzle and casual: a simple loop with a cross-fade, plus a short layer for success states.
Decide this once in the music design doc; changing models late means re-recording.

Authoring rules (defaults):
1. Fix tempo and time signature per piece; mark bars in the audio file or use tempo metadata in the tool. Without it, transitions drift.
2. Stems for layering must be the same length and start on the same bar. Render all stems from the same bar 1.
3. Loops end on a bar line; render the tail (reverb ring-out) past the loop point and overlap it, or use the tool's tail handling.
4. Give each layer a fade-in range on its parameter, for example intensity 0 to 1 split into bands 0.0 to 0.33, 0.33 to 0.66, 0.66 to 1.0, with 0.1 overlap.
5. Keep harmony compatible: every stem combination must sound acceptable, not only the full stack.

## 2. Transition rules and timing

Beat arithmetic: seconds per beat = 60 / BPM. A 4/4 bar is 4 beats. At 120 BPM: 0.5 s per beat, 2.0 s per bar. At 90 BPM: 0.667 s per beat, 2.667 s per bar.

| Game event | Transition | Reason (default) |
|---|---|---|
| Enter combat (urgent) | Next beat or half bar, 0.25 to 0.5 s fade, optional stinger | Fast response matters more than smoothness |
| Enter combat (not urgent) | Next bar, cross-fade 1 bar | Feels composed |
| Leave combat | Wait a hold time of 3 to 8 s, then next bar, fade 2 bars | Avoids flapping when combat re-triggers |
| Pause menu | Snapshot, 0.2 s, lowpass and music down | Quick and reversible |
| Level load | Fade out 0.5 to 1 s, hard cut inside the load screen | Hides stalls |
| Death or fail | Immediate stinger, music duck 0.3 s | Reaction first |

Hysteresis: use two thresholds for intensity (enter at 0.6, leave at 0.4) so a value hovering at one number does not toggle music. Rate-limit state changes to one per bar.

Latency budget estimate: if the game requests a change 150 ms before the next beat, you have time; if less than about 50 ms, wait for the following beat. Check scheduling APIs in your engine; `PlayScheduled` in Unity and sample-accurate start times in middleware avoid the drift of frame-timed starts.

## 3. Mix snapshots and ducking

Mix states (use snapshots in FMOD, States or Mixing Sessions in Wwise, mixer snapshots in Unity, bus volume tweens in Godot):

| State | Music | SFX | Voice | UI | Effects |
|---|---|---|---|---|---|
| Normal | 0 dB | 0 dB | 0 dB | 0 dB | none |
| Dialogue | -6 dB | -3 dB | 0 dB | 0 dB | none |
| Pause | -12 dB | mute or -20 dB | 0 dB | 0 dB | lowpass 1 to 2 kHz on music |
| Underwater | -3 dB | -3 dB | -3 dB | 0 dB | lowpass 800 Hz to 1.2 kHz |
| Stun/ringing | -9 dB | -9 dB | -9 dB | 0 dB | lowpass plus a sine tone |

These are defaults to tune; they are not measured values.

Ducking: sidechain compression from Voice to Music, 3 to 6 dB reduction, attack 20 to 50 ms, release 300 to 800 ms. Alternative: a dialogue snapshot triggered by voice playback, with attack 0.2 s and release 0.6 s. Music ducked for every UI click is the common fault: key the sidechain from Voice only, not from UI or SFX.

Rules:
1. Snapshots change levels; they never change content. Keep every snapshot's overrides small and named.
2. Return to Normal by a timed release, not by a second game event that can be missed.
3. Player volume sliders sit before ducking, so ducking still works at low slider values (VCA in FMOD, a Game Parameter or Bus in Wwise, separate group in Unity/Godot).

## 4. Voice limits and priorities

Voices are mixer channels. Mobile CPU may sustain 16 to 32 simultaneous voices comfortably; PC and console can run 64 to 256 or more (estimates; measure on target hardware). Set a global limit and per-event limits.

| Sound class | Max instances | Stealing | Priority (0-100) |
|---|---|---|---|
| Player weapon | 4 to 8 | Oldest | 80 |
| Enemy weapon | 8 | Quietest | 60 |
| Footsteps | 6 | Oldest or furthest | 40 |
| Ambient loops | 8 | Furthest | 30 |
| Impacts | 8 to 12 | Quietest | 50 |
| UI | 4 | Oldest | 90 |
| Voice (dialogue) | 2 to 4 | Never steal | 100 |
| Music | 1 to 3 | Never steal | 100 |

Procedure:
1. Count peak voices in a stress scene with a profiler (FMOD Studio live update, Wwise Profiler, Unity Profiler audio, Godot's audio monitor).
2. Set per-event max instances first, then the global voice cap about 20% above the observed peak.
3. Check that ducking and virtualisation do not hide critical sounds: tag critical sounds with the highest priority.
4. Distance-based culling: stop or virtualise sounds beyond their maximum distance (FMOD and Wwise virtualise; native engines usually stop the sound).

## 5. Loudness targets

Measure integrated loudness over representative play, not a single clip, with a BS.1770-style meter (LUFS/LKFS) and a true-peak limit.

| Target | Value | Source |
|---|---|---|
| PlayStation console titles | About -24 LUFS integrated, plus or minus 2 LU, measured over at least 30 minutes; true peak -1 dBTP | Sony recommendation as cited by Audiokinetic's mastering articles and Designing Sound; verify on Sony's current developer documentation |
| Portable and mobile (guide figure) | About -18 LUFS, plus or minus 2 LU; true peak -1 dBTP | Audiokinetic's "Mastering a Game with Wwise" series, as seen in search results; verify |
| Mobile music samples (practitioner view) | About -16 LKFS | Single blog author; not a platform standard |
| Nintendo Switch, Xbox, Steam/PC, web | No official figure found | Use the console figure when docked and the mobile figure for handheld or browser as a default, and check platform documents if you ship there |

Sources: https://audiokinetic.com/en/mastering-a-game-with-wwise-part1, https://designingsound.org/2013/02/20/different-loudness-ranges-for-console-and-mobile-games, https://designingsound.org/2012/07/30/video-games-and-loudness-standards-interview-with-sonys-garry-taylor/.

Procedure:
1. Add a loudness meter on the master bus (FMOD and Wwise have meter effects; for native, record the output and measure offline).
2. Play a 30-minute representative session; record the integrated value.
3. Move the master trim, not individual sounds, to reach the target. If the dynamic range is too wide, fix with bus compression and per-class mix levels.
4. Re-measure after every content drop.
Mobile speakers cannot reproduce low frequencies, so loudness targets cannot fix a weak mix: high-pass SFX below 100 to 150 Hz for phone speakers (default) and test on a real device.

## 6. Memory and streaming budgets

All numbers here are estimates for planning; measure on target hardware.

| Platform | Audio RAM (starting budget) | Music | Notes |
|---|---|---|---|
| Mobile (low end) | 20 to 40 MB | Stream | Avoid decompressing long clips; limit simultaneous streams to 2 to 4 |
| Mobile (mid/high) | 40 to 80 MB | Stream | Same |
| PC | 100 to 300 MB | Stream | Disk speed varies (HDD still exists) |
| Console | 100 to 400 MB | Stream | Check platform memory documents |
| Web | 10 to 30 MB decoded, plus download size | Stream with care | Decoded audio is much larger than the file |

Arithmetic:
- Uncompressed PCM: sample rate x channels x 2 bytes per second. 44.1 kHz stereo 16-bit = 44,100 x 2 x 2 = 176,400 B/s = about 10.1 MB per minute. Mono at 22.05 kHz = 44,100 B/s = about 2.5 MB per minute.
- A 3-minute stereo music track decompressed in RAM is about 30 MB. That is why music is streamed.
- Compressed Vorbis at 128 kbps is 16 KB/s, 0.96 MB per minute; 3 minutes = 2.9 MB on disk.

Strategy:
1. Short SFX (under about 3 s, played often): in memory, compressed with a cheap decoder (ADPCM) or PCM.
2. Medium sounds (3 to 15 s): compressed in memory, decoded on play.
3. Music, long ambience, long dialogue: stream from disk or network.
4. Bank by level or by feature, not by asset type, so unloading frees a whole scene's audio. Keep a small always-loaded bank for UI and the player.
5. Stream budget: simultaneous streams times bitrate fits well under disk throughput; 4 streams at 128 kbps is 64 KB/s, trivial on SSD but notable on slow mobile storage with other loads.
6. Downsample where it does not hurt: 22.05 kHz for low-frequency SFX, 32 or 44.1 kHz for music; 48 kHz is the common output rate (check the platform).

## 7. Compressed formats per platform

| Platform | Common choices | Notes |
|---|---|---|
| Mobile (iOS, Android) | Vorbis or Opus for music; ADPCM for short SFX; AAC where the engine supports it | Hardware decoders for AAC/MP3 exist but may be limited to one or few streams. Prefer software Vorbis/Opus for many streams (verify per device) |
| PC (Windows, macOS, Linux) | Vorbis or Opus for music; PCM or ADPCM for SFX | CPU is plentiful; use quality 4 to 6 on Vorbis as a default |
| Web | AAC (M4A), Opus/Ogg, MP3 | See engine-native-audio.md section 4 |
| Console | Platform-specific codecs exposed by the middleware (hardware-accelerated) | Names and availability come from each console's SDK under NDA (unverified here) |

Middleware formats: FMOD Studio offers per-platform encodings (Vorbis, FADPCM, PCM and platform codecs); Wwise has conversion settings per platform (Vorbis, ADPCM, PCM and platform codecs). Set the default conversion per platform and override only for exceptions (a few SFX that must be lossless).

Quality ladders (defaults): music Vorbis quality 4 to 5 (about 128 to 160 kbps, estimate); SFX Vorbis quality 3 to 4 or ADPCM; voice 64 to 96 kbps mono Opus or Vorbis.

## 8. Worked example

A 100 BPM action game, 4/4, three music states and two boss stingers.
- Beat = 0.6 s; bar = 2.4 s.
- Layers: pad (always), drums (intensity above 0.3), brass (above 0.7). Each fades over 1 bar = 2.4 s.
- Combat start: next beat, so wait at most 0.6 s; play a stinger on the beat.
- Combat end: hold 5 s (about 2 bars), drums out over 1 bar, brass out over 2 bars.
- Mix: Dialogue snapshot -6 dB music, 0.2 s in, 0.6 s out.
- Memory: 3 stems x 2 minutes stereo Vorbis 128 kbps = 3 x 1.92 MB = 5.8 MB on disk; streamed 3 at a time.
- Loudness: record a 30 minute session on a console profile, trim master to hit -24 LUFS plus or minus 2.

## 9. Test checklist

- Rapidly toggle intensity: no clicks, no stuck layers, no music restart.
- Loop the track for 10 minutes: no drift against stems.
- Trigger every stinger during every state.
- Run the voice stress scene and confirm limits hold, with critical sounds audible.
- Measure loudness per platform and per output (speakers, headphones, handheld).
- Pause and resume, alt-tab, background the app, and take a call (mobile): audio recovers.
- Low memory: unload banks and confirm nothing references them.
