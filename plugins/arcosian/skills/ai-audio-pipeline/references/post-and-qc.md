# Post-Processing and QC

This file explains how to turn generated or recorded audio into shippable game audio with the plugin's `audio_post.py` (normalize, trim, loop, convert, qc), gives recipes per asset class (music loop, stinger, SFX, voice, ambience), a QC checklist with pass criteria and what each check means, and the provenance record that closes each asset. The script wraps ffmpeg and ffprobe, so both must be on the PATH (macOS: `brew install ffmpeg`). Remember the agent cannot hear: QC numbers catch technical faults, and a human listens for everything else.

## Contents
1. The tool at a glance
2. Command reference with examples
3. Recipes per asset class
4. Loudness choices
5. Loop seam verification
6. QC checklist and pass criteria
7. Reading qc output
8. Batch script pattern
9. Human listening checklist
10. Provenance record
11. Troubleshooting
12. Gaps the script does not cover

## 1. The tool at a glance

Path: `${CLAUDE_PLUGIN_ROOT}/scripts/audio_post.py` (in docs: `<plugin-root>/scripts/audio_post.py`). Python 3.9, standard library only, subcommands: `normalize`, `trim`, `loop`, `convert`, `qc`. Exit codes: 0 ok, 1 a QC check or ffmpeg step failed, 2 usage or input error (including ffmpeg missing). Add `--json` for machine output. `--selftest` exercises the logic with built-in fixtures; run it after any change:
```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/audio_post.py --selftest
```

## 2. Command reference with examples

### normalize
Two-pass EBU R128 loudness normalization in linear mode (a single gain, no dynamic compression, so loop seams and stem balance are preserved).
```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/audio_post.py normalize --in loop.wav --out loop_n.wav --lufs -18 --tp -1
```
Defaults: `--lufs -16`, `--tp -1`. Output reports before and after loudness and true peak. If the source needs more gain than the true-peak ceiling allows, a linear normalizer cannot reach the target without limiting; the reported after-loudness shows the result. Do not use it on very short SFX (too short to measure integrated loudness reliably); peak-normalize those instead, or compare by ear.

### trim
Cut by seconds and optionally fade in and out.
```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/audio_post.py trim --in hit.wav --out hit_t.wav --start 0.04 --end 0.60 --fade 0.02
```
`--start` and `--end` are seconds; `--fade` adds fade in and out of that length. Find the leading silence first (qc shows duration; listen or inspect a waveform).

### loop
Create a seamless loop of whole bars with a crossfade between the tail overshoot and the head.
```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/audio_post.py loop --in src.wav --out loop.wav --bpm 120 --bars 8 --beats-per-bar 4 --xfade 0.5
```
Loop length = bars x beats x 60 / BPM (here 16.0 s). `--bpm` and `--bars` must be given together; without them the loop length is the source length minus the crossfade. The source must be at least loop length plus crossfade (else the tool exits with an error naming the required length). Default crossfade 0.5 s, `--beats-per-bar` default 4. Choose the source start at a downbeat first (use `trim --start`), then loop. The file's first `xfade` seconds blend the head with the overshoot tail so the end flows into the start.

### convert
```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/audio_post.py convert --in loop_n.wav --out loop.ogg --format ogg
```
Formats: `ogg` (libvorbis when available, otherwise ffmpeg's native vorbis encoder, which upmixes to stereo, otherwise opus), `m4a` (AAC 128 kbps), `wav` (16-bit PCM). `--out` is optional (same name with the new extension). Vorbis output quality is the script's default; tune quality for a build by hand if you need to, and check size against the budget in `mobile-performance`.

### qc
```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/audio_post.py qc --in loop.wav --lufs -18 --tp -1 --json
```
Checks: integrated loudness within plus or minus 1.5 LU of `--lufs`; true peak at or below `--tp`; clipping (sample peak at or above about 0 dBFS with several samples at peak); DC offset under 0.01; duration over 0.05 s; sample rate 44,100 or 48,000 Hz. Exit code 1 if any check fails.

## 3. Recipes per asset class

### Music loop
```
src=raw/play_candidate.wav
python3 .../audio_post.py trim   --in $src --out work/play_t.wav --start <downbeat_s>
python3 .../audio_post.py loop   --in work/play_t.wav --out work/play_loop.wav --bpm <measured> --bars 16 --xfade 0.5
python3 .../audio_post.py normalize --in work/play_loop.wav --out work/play_n.wav --lufs -18 --tp -1
python3 .../audio_post.py qc     --in work/play_n.wav --lufs -18 --tp -1
python3 .../audio_post.py convert --in work/play_n.wav --out build/play.ogg --format ogg
```
Then set loop points in the engine and test the seam on device. Keep the WAV master.

### Stems
Compute loudness gain from the full mix, apply the same gain to every stem (use `normalize` on the full mix to read the gain from its report; apply the equivalent gain via ffmpeg `volume` to stems), then loop each stem with identical `--bpm --bars --xfade`, verify equal lengths, and convert.
Check stems for equal length:
```
for f in stems/*.wav; do ffprobe -v error -show_entries format=duration -of csv=p=0 "$f"; done
```

### Stinger
Trim head silence so the first transient is at 0, apply a short fade-out (`--fade 0.05`), normalize to the music target or by ear against the loop it plays over, QC, convert to ogg or keep WAV for tiny files.

### Short SFX
Trim head and tail, `--fade 0.01` to avoid clicks, peak-normalize per event class (a short gain tool or ffmpeg `volume`), keep WAV masters, ship WAV (or the engine's recommended decoded format). Use `qc` for clipping, DC offset and sample rate; ignore its loudness check for sub-second sounds (it may be unreliable) or set `--lufs` to the measured value and judge by ear.

### Voice line or bark
Trim silence to a few milliseconds each side, normalize to about -16 LUFS for lines longer than a couple of seconds (use qc for the check; for barks match by ear against lines), convert mono to ogg. Services may return 24 kHz audio: the qc sample-rate check expects 44.1 or 48 kHz, so either resample to 44.1 or 48 kHz for QC and shipping, or accept the sample-rate failure for 24 kHz voice by project decision recorded in the manifest. Resampling does not add information; choose by size.

### Ambience loop
Use the service's loop flag if present, then `loop` with a long crossfade (1-2 s) since ambiences have no bar grid: omit `--bpm --bars` so length equals source minus crossfade. Normalize quieter than music (see mixing reference), QC, convert.

## 4. Loudness choices

Targets are starting points (see `skills/audio-direction/references/mixing-implementation-voice.md`): music loops about -18 LUFS, voice about -16 LUFS, ambience quieter, SFX by peak and ear; true peak at or below -1 dBTP. The `qc` default of -16 LUFS matches voice but not music: always pass `--lufs` explicitly per class. Tolerance in the script is fixed at plus or minus 1.5 LU. Two-pass linear normalization keeps dynamics; if the source is too dynamic to hit both target and peak, fix at source (regenerate with steadier dynamics) or apply a limiter deliberately, then re-QC.

## 5. Loop seam verification

Numeric proxy (optional, not in the script): export 100 ms before and after the seam by rendering the loop twice end to end and compare short-term loudness and spectrum across the join.
```
# make a 2x concatenation and listen around the join; also check level continuity
ffmpeg -hide_banner -y -stream_loop 1 -i loop.wav -c copy loop2x.wav
```
Inspect `loop2x.wav` around the midpoint in an editor, or by listening. Pass criteria: no click, no energy dip or jump greater than about 1-2 dB across the join, rhythm continues without a double or missing beat. Always repeat in the engine on a phone: compressed formats and engines add their own padding and loop handling.

## 6. QC checklist and pass criteria

Technical (automatic):
- [ ] Integrated loudness within tolerance of the class target (qc loudness).
- [ ] True peak at or below -1 dBTP (music, voice) or -3 dBTP (ambience).
- [ ] No clipping; peak count below the threshold.
- [ ] DC offset under 0.01.
- [ ] Duration plausible and matches the cue list (loops equal bars x bar seconds).
- [ ] Sample rate 44.1 or 48 kHz (or documented exception for voice).
- [ ] Loop files: no fades, whole bars, seam test passed.
- [ ] Stems: equal length, sum test passed, same gain.
- [ ] Leading silence under about 20 ms for event sounds and stingers.
- [ ] Format and channel layout per the matrix (mono SFX and VO, stereo music).

Content (human):
- [ ] Matches bible palette, key, tempo; no excluded sounds; no vocals in instrumentals.
- [ ] No artifacts (warble, smearing, metallic ring, clicks).
- [ ] Voice: pronunciation correct; emotion fits; consistent with the character.
- [ ] Phone-speaker review and headphone review done.
- [ ] Mix test in context with music and SFX.
- [ ] Licence and disclosure items complete.

Fail policy: any automatic failure blocks promotion to approved; document waivers with a reason and reviewer.

## 7. Reading qc output

Example human output:
```
QC loop_n.wav: PASS
  [ok] loudness: integrated -18.1 LUFS (target -18.0 +-1.5)
  [ok] true_peak: true peak -14.3 dBTP (max -1.0)
  [ok] clipping: ...
  [ok] dc_offset: ...
  [ok] duration: duration 4.000s
  [ok] sample_rate: sample rate 48000 Hz (expected 44100 or 48000)
```
With `--json` the result contains `format` (codec, sample rate, channels, duration), `lufs`, `true_peak`, `lra`, `peak_db`, `dc_offset` and a `checks` list with `check`, `ok`, `message`, plus overall `ok`. Gate builds on `ok`. A true peak far below the ceiling is fine; very low loudness means normalize.

## 8. Batch script pattern

```
#!/usr/bin/env bash
set -euo pipefail
AP="${CLAUDE_PLUGIN_ROOT}/scripts/audio_post.py"
mkdir -p build work
fail=0
for f in masters/music/*.wav; do
  b=$(basename "$f" .wav)
  python3 "$AP" normalize --in "$f" --out "work/$b.wav" --lufs -18 --tp -1
  python3 "$AP" qc --in "work/$b.wav" --lufs -18 --tp -1 || fail=1
  python3 "$AP" convert --in "work/$b.wav" --out "build/$b.ogg" --format ogg
done
exit $fail
```
Adapt per class; log results into the manifest. A script that is not part of the plugin should live in the project, not in the plugin.

## 9. Human listening checklist

The agent prepares; the human listens. Provide: the files grouped by cue, the numbers, and these questions.
1. Does the first 10 seconds sound like this game?
2. Does the loop repeat without you noticing the join (listen to 3 repeats)?
3. Does anything distract or irritate after 2 minutes?
4. On the phone speaker, is everything important audible at mid volume?
5. In a muted room with headphones, any hiss, clicks, artifacts?
6. Do SFX sets feel like siblings? Does the reward ladder escalate?
7. Voice: is each line understandable over music? Names pronounced right?
Record answers, decisions and reviewer in the approval log.

## 10. Provenance record

Per promoted asset record (fields map to the asset manifest schema):
- id, class, path, status, placeholder false
- provider, model and version, plan tier at generation, date
- prompt or prompt id and prefix version, seed, parameters
- references used (and their rights)
- post chain (commands and parameters) and QC result with date
- measured BPM, key, loop length in samples
- licence text or URL, attribution requirement, revenue-threshold note
- cost (feeds the budget ledger)
- reviewer and approval date
Validate the manifest before building: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_json.py` with the asset-manifest schema.

## 11. Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| "ffmpeg missing" (exit 2) | Not installed | `brew install ffmpeg` |
| loop error about source length | Source shorter than loop plus crossfade | Generate longer or reduce bars or crossfade |
| qc loudness fails after normalize | Peak ceiling limits gain | Regenerate quieter dynamics or limit deliberately |
| qc sample_rate fails for voice | Service output 24 kHz | Resample or record an exception |
| Ogg is stereo from a mono file | Native vorbis encoder upmixes | Install an ffmpeg build with libvorbis or accept; check size |
| Click at loop seam in engine only | Codec padding or engine loop handling | Use Ogg or WAV, set loop offset, re-test |
| Level jump between stems | Per-stem normalization | Apply a shared gain |

## 12. Gaps the script does not cover

- No silence detection or auto-trim: inspect and pass `--start` and `--end` by hand.
- No loop-point detection: use a detector (for example PyMusicLooper, MIT licence) if you cannot design loops by bars.
- No BPM or key analysis: measure with an analysis tool; do not trust prompts.
- No peak normalization for short SFX: use ffmpeg `volume` or a small project script.
- No per-route loudness handling: that is a runtime feature (see `audio-direction`).
