# Feel review rubric

A before/after critique rubric for the `critic` agent (`arcosian:critic`) and human reviewers who judge game feel from evidence: short clips, frame-stepped timelines and peak-frame screenshots. It defines the evidence to capture, nine scored dimensions with anchors at 1, 3 and 5, a weighted roll-up into the 1-5 "Feel" dimension of the critic's rubric (3 is acceptable, below 3 blocks), a critique template, a worked example, and a feel acceptance checklist for features. Anchors are calibration aids, not laws: adjust thresholds per genre and record the change.

## Contents

1. Principles of feel review  2. Evidence protocol  3. The nine dimensions and anchors  4. Roll-up and verdicts  5. Critique template  6. Worked example  7. Stills versus clips  8. Feature acceptance checklist  9. Reviewer pitfalls

## 1. Principles of feel review

- **Judge the player's experience, not the effect count.** More is not better; proportional, readable and timely is better. A quiet, tight interaction beats a loud, late one.
- **Compare, do not score in isolation.** Put A (before) and B (after) side by side, shuffle the labels if you can, score both, then compare. Absolute scores drift between reviewers; relative ones hold.
- **Score only what the evidence can show.** Mark the rest "not assessable" and request the evidence. A still cannot show latency, easing or sound.
- **Review the worst case, not the happy path:** rapid repeat, maximum chain, lowest device tier, interruption, every accessibility option on.
- **Name the owning layer.** A late response is an input or simulation defect and no effect can fix it; a flat impact is a juice defect. Each finding states which layer owns the fix.
- **Tie every finding to a frame, a timestamp or a screenshot path.** No finding without evidence; no evidence without a finding or a "protect" note.

## 2. Evidence protocol

Capture per interaction type (tap, merge or match, hit, reward, fail, UI button):

1. **Same conditions for A and B.** Release build, same device (record model and OS), same seed or the same scripted playthrough (`qa-testing`), same settings (sound on, haptic log on, refresh rate noted).
2. **Three clips each, 5-15 s:** one single event; rapid repeat (five events in two seconds); worst case (maximum chain, maximum simultaneous events).
3. **Record at 60 fps or the native refresh** with touches visible (Android: Developer options, Show taps; otherwise a debug overlay in the game that draws touches) and audio on. Clips cannot show haptics, so log each haptic call with a timestamp.
4. **Extract five reference frames per clip.** Contact (first frame with the finger down), response (first frame the game state visibly changes), impact (peak of the primary effect), peak load (most simultaneous effects), settle (first frame at rest). Convert frame numbers to ms by dividing by fps (one frame is 16.7 ms at 60 fps). `ffmpeg -i clip.mp4 -vf fps=60 frames/%04d.png` does it if ffmpeg is installed.
5. **For a model reviewer** pass the five frames per clip as a contact sheet with timestamps, the haptic log, and the parameter diff, and tell it which dimensions are assessable (section 7).
6. **File layout:** clips and `frames.md` under `.gamestudio/evidence/F###/feel/` named `<interaction>_<A|B>_<single|rapid|worst>.mp4`; the review in `.gamestudio/evidence/F###/feel_review.md`.

## 3. The nine dimensions and anchors

Scores are 1-5. Use 2 and 4 when the evidence sits between anchors. Weights sum to 100; D1 and D4 are gates.

### D1 Responsiveness (weight 20, gate)

Evidence: clip with frame numbers. Latency applies to caused feedback only.

| Score | Anchor |
|---|---|
| 1 | No contact acknowledgement, or acknowledgement later than 6 frames at 60 fps (100 ms), or response later than 12 frames, or inputs dropped under spam |
| 3 | Acknowledgement within 3 frames and response within 6 frames; buffering exists but misses some inputs under spam |
| 5 | Acknowledgement on the next frame, response within 4 frames (66 ms); buffering and forgiveness verified; no dropped input at 10 taps per second |

### D2 Weight and impact (weight 15)

Evidence: clip, impact frame.

| Score | Anchor |
|---|---|
| 1 | The event reads as a silent state change: no motion, flash, audio or camera cue at the impact frame |
| 3 | Two channels fire at impact (for example sound and flash) but magnitude is uniform and there is no anticipation or recovery |
| 5 | Three or more channels land on the same frame (motion, flash or particles, audio; camera and haptic from the major tier up); anticipation, impact and recovery are all readable; magnitude follows significance |

### D3 Motion quality (weight 15)

Evidence: clip, frame-stepped.

| Score | Anchor |
|---|---|
| 1 | Linear or instant changes, teleporting, jitter, tweens fighting over one property |
| 3 | Easing present but durations inconsistent; abrupt stops; no overshoot, or overshoot that wobbles too long |
| 5 | A small consistent set of durations and curves; ease-out on caused motion; anticipation where earned; clean settle; volume preserved in squash; no conflicts when events overlap |

### D4 Readability under juice (weight 15, gate)

Evidence: peak-load frame, a greyscale copy of it, a thumb-circle overlay at the touch point.

| Score | Anchor |
|---|---|
| 1 | Decision-critical information (board state, enemies, HUD numbers) is covered or unreadable at peak load, or more than half the screen flashes for more than 3 frames |
| 3 | Information survives except in chain worst cases; the thumb sometimes hides the feedback; recovers within 300 ms |
| 5 | Everything the next decision needs stays legible at peak load; feedback sits outside the thumb zone; effect shapes are distinct in greyscale |

### D5 Proportionality and escalation (weight 10)

Evidence: clips of several tiers, shuffled.

| Score | Anchor |
|---|---|
| 1 | Every event has the same intensity (all huge or all flat) |
| 3 | Two or three tiers are distinguishable; the top tier is not clearly special, or escalation saturates early |
| 5 | Four tiers are distinguishable when clips are shuffled; streaks escalate smoothly and then cap; rare events are unmistakable |

### D6 Cross-channel coherence (weight 10)

Evidence: clip with audio, haptic log.

| Score | Anchor |
|---|---|
| 1 | Audio or haptic is off by more than 3 frames or unrelated to the visual; a haptic fires with no matching event |
| 3 | Channels within 2-3 frames; character mismatches (sharp haptic on a soft sound, bright flash on a dull thud) |
| 5 | Transients align within 1 frame; character matches across channels; pitch and intensity track magnitude |

### D7 Restraint and fatigue (weight 5)

Evidence: rapid-repeat clip, a five-minute session clip.

| Score | Anchor |
|---|---|
| 1 | The same long sequence plays every time and blocks input; one sample repeats several times a second |
| 3 | Variants and skip exist, but repeated events still feel heavy after five minutes |
| 5 | Variation, shortened repeats, skip and frequency scaling; still pleasant after twenty minutes |

### D8 Mobile fitness (weight 5)

Evidence: perf report, lowest-tier clip, interruption test (background and resume mid-effect).

| Score | Anchor |
|---|---|
| 1 | Frame drops during effects on the lowest supported tier, or state (time scale, camera offset, bus volume) stuck after pause, resume or scene change |
| 3 | Within budget on the mid tier, occasional drops on the low tier; state resets correctly |
| 5 | Within budget at maximum effect load on the lowest tier; effects pooled; state resets on lifecycle events; identical timing at 60, 90 and 120 Hz |

### D9 Accessibility and control (weight 5)

Evidence: settings screens, option-off clips.

| Score | Anchor |
|---|---|
| 1 | No options; flashing above 3 per second; information carried only by haptics, flash or colour |
| 3 | A haptics toggle exists; reduced motion is partly honoured |
| 5 | Haptics, shake, flash and reduce-motion options; OS defaults respected; every cue has a redundant non-haptic, non-colour channel |

## 4. Roll-up and verdicts

Weighted score = (20·D1 + 15·D2 + 15·D3 + 15·D4 + 10·D5 + 10·D6 + 5·D7 + 5·D8 + 5·D9) / 100.

| Weighted score | Feel score for the critic's rubric |
|---|---|
| 4.5 or more | 5 |
| 3.5 to 4.49 | 4 |
| 2.5 to 3.49 | 3 |
| 1.5 to 2.49 | 2 |
| below 1.5 | 1 |

Gates: if D1 or D4 is 2 or lower, the Feel score is capped at 2 whatever the sum says. Any dimension at 1 is at least a Major finding.

| Result | Verdict | Required follow-up |
|---|---|---|
| Feel 4-5, no gate | Approve | Note what to protect |
| Feel 3, no gate | Approve with conditions | The two lowest dimensions become Major findings with a fix and an owner each |
| Gate tripped (D1 or D4 at 2 or lower) | Reject | Blocker; re-review only the gated dimension after the fix |
| Feel 2 or 1, no gate | Reject | Major findings per dimension at 1-2 |

Severity: **Blocker** (D1 or D4 at 2 or lower; stuck global state; flashing above 3 per second without an option), **Major** (any other dimension at 1-2; missing options), **Minor** (polish, parameter nudges).

## 5. Critique template

```markdown
# Feel review: <feature or mechanic id> (<date>)
Build A (before): <build>   Build B (after): <build>   Device: <model, OS, refresh>   Settings: <sound, haptics>
Evidence: <paths under .gamestudio/evidence/F###/feel/>

| Dimension | A | B | Delta | Evidence (clip, frame, screenshot) | Note |
|---|---|---|---|---|---|
| D1 Responsiveness | | | | | |
| D2 Weight and impact | | | | | |
| D3 Motion quality | | | | | |
| D4 Readability under juice | | | | | |
| D5 Proportionality | | | | | |
| D6 Cross-channel coherence | | | | | |
| D7 Restraint and fatigue | | | | | |
| D8 Mobile fitness | | | | | |
| D9 Accessibility | | | | | |

Weighted: A = _._  B = _._   Feel score: A = _  B = _   Gates: <none | D1 | D4>
Findings: <Blocker / Major / Minor>: what, where (timestamp or frame), why it matters to the player, fix, owning layer (response or juice)
Protect: <what is good and why>
Not assessable: <dimensions and the evidence needed>
Verdict: <Approve | Approve with conditions | Reject>
```

## 6. Worked example

Illustrative merge feature on a match-and-merge board. A is the bare prototype, B the first juice pass, B' after fixing the review. Numbers are invented for the example.

| Dimension | A | B | B' | Evidence note |
|---|---|---|---|---|
| D1 Responsiveness | 2 | 4 | 4 | A: no pressed state, response at frame 11 (183 ms). B: acknowledgement frame 1, response frame 3 |
| D2 Weight and impact | 1 | 4 | 4 | A swaps a sprite silently. B: pull-in, pop, burst, sound and light haptic land on the impact frame |
| D3 Motion quality | 2 | 4 | 4 | A: instant swap. B: back-out pop, clean settle |
| D4 Readability under juice | 5 | 2 | 4 | B: 40 particles and number pop-ups hide the three neighbouring cells at chain 4. B': 12 particles, 0.4 s lifetime, numbers moved above the finger |
| D5 Proportionality | 1 | 4 | 4 | A: every merge identical. B: four tiers by result tier |
| D6 Cross-channel coherence | 2 | 4 | 4 | B: audio and haptic within 1 frame of the pop |
| D7 Restraint and fatigue | 3 | 3 | 3 | Pitch ±3% and three variants; sequence under 0.5 s so no skip needed |
| D8 Mobile fitness | 4 | 3 | 3 | Burst pooled; one frame spike on first use, pre-warm in the next pass |
| D9 Accessibility | 3 | 3 | 3 | Haptics toggle only; reduce motion planned |
| Weighted | 2.40 | 3.55 | 3.85 | A: 40+15+30+75+10+20+15+20+15 = 240. B: 80+60+60+30+40+40+15+15+15 = 355. B': 385 |
| Feel score | 2 (gate D1) | 2 (gate D4) | 4 | B would map to 4 but the D4 gate caps it at 2 |
| Verdict | Baseline | Reject: Blocker, readability at chain 4 | Approve | Minor: add reduce motion; pre-warm the burst |

The lesson of the example: B improved five dimensions and still failed, because juice hid the board. The gate exists so that a feel pass cannot trade away readability.

## 7. Stills versus clips

| Dimension | From stills | From clips | Notes |
|---|---|---|---|
| D1 Responsiveness | Not assessable | Yes, by frame count | Needs touch overlay |
| D2 Weight and impact | Partly (channels visible at the impact frame) | Yes | Sound needs the clip |
| D3 Motion quality | Not assessable | Yes, frame-stepped | |
| D4 Readability | Yes (peak-load frame) | Yes | Always also check greyscale and the thumb overlay |
| D5 Proportionality | Partly (stills across tiers) | Yes | Shuffle before scoring |
| D6 Coherence | Not assessable | Yes, with audio and the haptic log | |
| D7 Restraint | Not assessable | Yes, long clip | |
| D8 Mobile fitness | Partly (effect density) | Perf report required | |
| D9 Accessibility | Partly (settings screens) | Yes, option-off clips | |

Stills-only review scores D4 and the partial rows, marks the rest "not assessable" and asks for a clip. Never infer motion, timing or sound from a still, and never raise a score on the strength of a description of the effect.

## 8. Feature acceptance checklist

A feature that touches player input or feedback is not done until these hold. Evidence goes in `.gamestudio/evidence/F###/`.

**P0 (blocks acceptance)**
- [ ] Every input has contact acknowledgement on the next displayed frame at the touch point.
- [ ] Cause to visible effect is at most 100 ms on the lowest supported device (70 ms for timing-critical verbs), measured on a release build.
- [ ] The mechanic's `feedback` lists channels and tier; tuned values are in `parameters` with min and max.
- [ ] Effects do not alter outcomes: a deterministic playthrough gives identical results with all juice off.
- [ ] No more than three flashes per second; haptics, shake, flash and reduce-motion options exist and are honoured.
- [ ] No global state stuck after pause, resume, scene change or backgrounding (time scale, camera offset, audio bus volume, haptic engine).
- [ ] Decision-critical information is readable at peak load and feedback is not under the thumb.

**P1 (fix this milestone)**
- [ ] Significance ladder applied: four tiers distinguishable, frequent events scaled down.
- [ ] Hit-stop capped at one per 150 ms and absent from timing and rhythm modes.
- [ ] Effects pooled, no per-event allocation in release builds; frame time within budget at maximum effect load on the lowest tier (`perf_budget.py`).
- [ ] Sequences over 1 s are skippable and non-blocking; repeats shortened; rewards granted before the animation.
- [ ] Audio has variants and pitch variation, at most 3 voices per event, ladders reset on break.
- [ ] Haptics throttled to about 10 per second, paired with audio and visual, semantic patterns only.

**P2 (polish)**
- [ ] Anticipation and follow-through on hero events; idle animation disabled off-screen; post effects gated by device tier; remote-config hooks on the top feel parameters.
- [ ] Before/after clips, the frames file and the rubric result are stored with the feature evidence.

## 9. Reviewer pitfalls

- Rewarding the busiest version. Count what the player can read, not what the engine draws.
- Scoring from the editor or from a debug build at an unrealistic frame rate: latency and frame drops only count on release builds on target devices.
- Reviewing only the single-event clip: fatigue, stacking and occlusion show up in rapid-repeat and worst-case clips.
- Fixing feel in the wrong layer: stacking effects to hide a late response, or tuning the response to compensate for missing feedback.
- Ignoring the settings: a build that cannot be played with haptics off, shake at zero and reduced motion on is not finished.
- Moving the goalposts between iterations: re-review only the changed claims, keep the anchors fixed, and note any threshold changed for the genre.
