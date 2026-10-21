---
name: game-feel
description: 'Game feel and juice codex: Swink-style response model, input latency budgets, coyote time and buffering, trauma-based screen shake, hit-stop, squash and stretch, easing, particles, number pop-ups, audio and haptic pairing, mobile battery cost, feel review rubric. Use when a game "feels floaty", "add juice", "make it satisfying", "screen shake", "hit-stop", "haptics", "tween" or "input lag".'
---

# Game Feel and Juice

Feel is what a verb is like in the hand: how soon it answers, how it moves, how loudly the game confirms it. On a phone it is the cheapest way to look expensive and the easiest way to burn battery, hide the board under a thumb, or annoy a player who turned haptics off. Senior work here separates response (the simulation) from juice (the presentation), measures latency before decorating, scales feedback to the significance of the event, and keeps every effect budgeted, optional and interruptible. Numbers in this skill are typical starting values to tune on a real device, not constants.

## What this skill gives you

- A working model of feel (Swink's response model, the input-response-juice loop, trauma-based shake) and a juice budget that protects readability.
- A tuning procedure and juice checklists for the six common interactions: tap, merge or match, hit, reward, fail and UI button.
- A catalog of 45 juice techniques with parameters and Godot 4 and Unity snippets (`references/juice-catalog.md`).
- Latency budgets, forgiveness windows (coyote time, buffering), gesture thresholds, easing and timing tables, and a haptics layer for iOS, Android, Godot and Unity (`references/input-animation-haptics.md`).
- A before/after rubric and feature acceptance checklist the critic applies to clips and screenshots (`references/feel-review-rubric.md`).

## Core models

**1. Feel is control, space and polish (Swink).** Steve Swink's *Game Feel* (2008) frames feel as real-time control of something in a simulated space, with the interaction emphasised by polish. His six building blocks make a practical review lens; tune from the top down, because polish cannot fix a wrong response curve.

| Block | Working question | Typical knobs |
|---|---|---|
| Input | How is the gesture read, and how late? | Latency, sampling, thresholds, dead zones, buffering |
| Response | How does the object answer over time? | Acceleration, max speed, damping, gravity, jump curve |
| Context | What does the space do to that answer? | Collision, friction, bounds, camera, level geometry |
| Polish | What emphasises the action without changing rules? | Animation, particles, sound, shake, haptics |
| Metaphor | What does the motion claim the thing is? | Weight, size, material, speed that fits the fantasy |
| Rules | What do systems do with the result? | Scoring, damage, combos, win and lose |

**2. The loop: input, response, juice.** Three layers, built in this order. Acknowledge: the touch gets a visible or audible echo at the contact point within about one frame. Respond: the simulation changes and the change is visible within about 100 ms (the classic "feels instantaneous" limit from HCI response-time literature; timing-critical verbs want tighter). Juice: non-functional emphasis scaled to the event's significance, played with the response and never before it. "Juice" as a design term was popularised by Martin Jonasson and Petri Purho's talk "Juice it or lose it" (GDC Europe 2012). Juice amplifies a good loop and cannot create one; if the verb is dull with every effect off, fix the rules first (`design-theory`).

**3. Trauma model for shake (Squirrel Eiserloh, GDC 2016).** Keep one scalar `trauma` in 0..1. Events add to it (0.1-0.2 light, 0.3-0.5 heavy), time drains it (about 1-2 per second), and the visible shake is trauma squared or cubed, so small events barely register and big ones escalate sharply. Drive offset and roll from smooth noise, not per-frame random numbers, which read as jitter. Contributions from many sources sum and clamp, so shake never needs per-event special cases. Starting amplitude at full trauma: offset 2-3% of screen height, roll 2-4 degrees. Code in `references/juice-catalog.md` (technique 1).

**4. Significance ladder and juice budget.** Feedback magnitude follows the importance and rarity of an event and shrinks with its frequency. Every event gets a tier; a tier is a budget of channels (motion, flash or particles, audio, camera, haptic, number), a duration cap and an amplitude multiplier.

| Tier | Example | Channels | Duration cap | Amplitude |
|---|---|---|---|---|
| Micro | Tap, step, one coin | 1-2 (motion plus sound) | 120 ms | 0.25 |
| Minor | Match, pickup, enemy hit | 2-3 | 300 ms | 0.5 |
| Major | Chain of 4+, boss hit, level-up | 3-5 including camera | 700 ms | 1.0 |
| Hero | Win, rare reward, final blow | All, sequenced | 1-2 s, skippable | 1.5 |

Rules: one hero effect per event; an event firing four times a second gets a fraction of the flash of one firing once a minute; at most three flashes per second (WCAG 2.3.1); effects never cover the next decision; every effect is optional and removable without changing outcomes.

**5. Presentation never decides rules.** Effects subscribe to simulation events (`gameplay-programming`); they do not gate, delay or alter outcomes, so a deterministic playthrough gives identical results with all juice off. Grant rewards in the model first, then animate them.

**6. Feel is data.** Durations, amplitudes, caps and curve choices live in one resource per feature (Godot `Resource`, Unity ScriptableObject) and in the mechanic's `parameters`, so they can be tuned live, reviewed and, where sensible, remote-configured. Time-based everywhere (seconds, `delta`), never frame counts, so 60, 90 and 120 Hz play the same.

**7. Habituation is real.** The tenth identical flourish is a tax. Shorten repeats, vary pitch and variants, escalate only for streaks and rare events, and make anything over about one second skippable.

## Decision procedures

### A. Tune the feel of one verb

1. Write a feel sentence ("heavy and decisive", "light and slippery") and name two reference games with the same verb (`game-case-studies`).
2. Grey-box it: no art, no effects. If it is not fun for 30 seconds, stop; juice will not fix it.
3. Measure latency on the target device and fix the pipeline first (`references/input-animation-haptics.md` section 1).
4. Tune response with 3-5 exposed parameters (speed, acceleration, gravity, buffer windows), one at a time, on device, in the player's hand.
5. Add forgiveness before flourish: buffering, coyote time, hurtbox shrink, magnet radius.
6. Layer feedback in cost order: contact acknowledgement, audio, motion (squash, easing), particles and flash, camera, haptics, numbers. After each layer toggle it off and on and keep it only if "on" is clearly better; adding one thing at a time is the method Jan Willem Nijman demonstrated in his Vlambeer talk "The Art of Screenshake".
7. Assign every event a tier and scale amplitudes by it, then scale the most frequent events down again.
8. Stress it: spam inputs, trigger 20 events in one frame, run the lowest-tier device, background and resume, mute, haptics off, reduce motion on.
9. Record before/after clips, score them with `references/feel-review-rubric.md`, and write the final values into the mechanic's `parameters`.

### B. Juice checklist by interaction

| Interaction | Always | Add by tier | Watch out |
|---|---|---|---|
| Tap (board or world) | Pressed or selected state on the same frame at the contact point; soft tick sound, 4% pitch variation; response within 100 ms | Scale 1.0 to 1.08 over 60-80 ms; ripple; selection haptic tick | The thumb covers feedback: offset it up and aside; never delay selection to wait for a double tap |
| Merge or match | Anticipation 60-100 ms (pieces pull together); pop 1.0 to 1.2 to 1.0 in about 180 ms with back-out; burst of 8-16 particles for 0.4 s; pitch up one step per chain link | Number pop-up, combo meter bump, light to medium haptic at the pop, trauma +0.1-0.2, hit-stop at most 40 ms on big chains | Chains: shrink per-event amplitude and escalate the chain feedback instead; cap simultaneous pops |
| Hit or damage | Hit flash for 2-3 frames; layered impact sound; knockback; hit-stop 40-90 ms; trauma +0.15-0.3 | Directional camera kick, debris, number pop-up, medium haptic, music duck on heavy hits | Multi-hit weapons: one hit-stop per 150 ms; never in rhythm or timing modes |
| Reward or collect | Pop-in with overshoot; fly-to-counter 0.45-0.7 s with 30-60 ms stagger; counter bump per arrival; rising pitch; anticipation before big reveals | Light burst, shine sweep on claimable items, haptic ticks at no more than 10 per second, final flourish on the total | Skippable and non-blocking; shorten repeats; grant the reward before the animation |
| Fail or loss | Short (under 0.6 s), unmistakable, never mocking: dull low-passed sound, brief desaturation or small shake, one error-style haptic; show the cause; retry in one tap | Slow-motion of the fatal moment up to 0.4 s if it reads as fair | Fail feedback is smaller than success feedback; no scolding jingle; no offer before the cause is understood (`monetization`) |
| UI button | Pressed state on the next frame (scale 0.95-0.97, about 10% darker); release back-out in 80-120 ms; click sound within one frame | Selection haptic on release for primary actions only; ripple at the touch; disabled state that says why | Hit area at least the platform minimum (`mobile-ux`); the action fires on release and the flourish plays alongside, never before it |

### C. Diagnose "it feels bad"

| Report | Likely cause | First fix |
|---|---|---|
| "Floaty" | Symmetric gravity, long acceleration or deceleration, no landing feedback | Fall gravity 1.5-2.0 times rise gravity, shorter deceleration, landing squash, dust and thud |
| "Laggy" | Latency stack, input read late in the frame, long anticipation on player actions, deep render queue | Measure; process events on arrival; cut player-side anticipation to 2-3 frames; check frame pacing |
| "Flat" or "no impact" | No hit-stop or audio layers, uniform magnitudes, linear motion | Layered impact sound, ease-out with overshoot, scale by tier |
| "Noisy" or "can't see" | Too many simultaneous effects, no frequency scaling, effects over the play field | Apply the ladder, lower rates, move effects off the thumb and board, cut particles |
| "Unfair" | Visual and hit-box mismatch, no buffering, no telegraph | Shrink the hurtbox 10-30%, add buffers, telegraph 300-600 ms |
| "Rewards are boring" | Same size every time, no anticipation, fast habituation | Tiered reveals, anticipation, shorter repeats; rarity changes the presentation, never the outcome |
| "Makes me dizzy" | Continuous shake or zoom, strobing, heavy parallax | Lower amplitude and rate, reduce-motion mode, at most 3 flashes per second |
| "Stutters on hits" | Stacked hit-stop, per-effect allocation, particle spikes | Cap hit-stop, pool effects, pre-warm particles and shaders |

### D. Set the juice budget for a screen

1. List the screen's events with their frequency per minute.
2. Assign tiers; the three most frequent events are Micro unless playtests prove otherwise.
3. Cap concurrency: one full-screen effect at a time, trauma clamped at 1.0, one hit-stop per 150 ms, at most 3 audio layers per event, no more than 3 flashes per second.
4. Cap cost: set live-particle and overdraw limits per device tier and gate them with `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/perf_budget.py --report perf.json --contract contract.json` (`mobile-performance`).
5. Route every channel through one settings object (shake, flash, haptics, particles, hit-stop) with reduce-motion defaults (`references/input-animation-haptics.md` section 6.5).

## Mobile specifics

- **Touch latency is a stack, not a number.** Digitizer scan, OS dispatch, your input read, the simulation step, the render queue and display scanout each add up to a frame. Read input on arrival, apply it in the same frame, keep the render queue shallow, and measure finger-down to first changed pixel with a 240 fps camera on a release build.
- **The thumb hides the feedback.** A fingertip covers roughly a centimetre of screen. Put numbers, rings and sparkles above and beside the contact point, hold dragged objects 40-80 px above the finger, and never leave essential state only under the thumb.
- **Haptics etiquette.** Haptics are semantic, short and paired with a visual and an audio cue: selection ticks, impact pulses scaled to magnitude, one success or fail pattern. Rate-limit to about 10 pulses per second, never buzz per particle or per frame, never carry information only in haptics, and ship an in-game Off, Low, Normal setting beside the OS one. Hardware varies widely: query capability and degrade gracefully.
- **Battery and heat.** Particles, full-screen post effects and transparent overdraw cost GPU time and heat. Cap live particles per tier, prefer flipbooks and shader uniforms over many nodes, pool everything, stop idle loops that are off-screen, and run post-process pulses on mid and high tiers only.
- **Interruptions strand effects.** A background event during hit-stop can leave the time scale at 0.05 or a tween half-applied. Reset time scale, camera offsets, bus volumes and the haptic engine on pause, resume and scene change.
- **Refresh rates differ.** Durations in seconds and exponential smoothing keep 60, 90 and 120 Hz identical; frame-count timings do not.
- **Respect the OS.** Use reduced-motion and system haptics settings as defaults, then offer finer in-game controls (`accessibility-localization`).

## Anti-patterns

| Anti-pattern | Detect | Fix |
|---|---|---|
| Juice as rescue for a weak loop | The verb is dull with all effects off | Fix rules and response first; juice amplifies |
| Everything is a 10 | Shuffled clips cannot be ordered by importance | Significance ladder and frequency scaling |
| Hit-stop on frequent events | Input feels sticky in multi-hit or rapid-fire play | One per 150 ms, skip above about 5 events per second, never in timing modes |
| Per-frame random shake | Reads as jitter or static | Trauma with smooth noise, squared |
| Anticipation on player actions | Frame-step shows the response later than 100 ms | Wind-ups on enemies and heavy actions only; player side 2-3 frames |
| Blocking sequences | Next input ignored during a coin flight or reveal | Non-blocking and skippable; state granted first |
| Ease-in on feedback | Responses start slowly and feel laggy | Ease-out for caused motion; ease-in only for exits and absorption |
| Effects under the thumb | Overlay a thumb circle on the clip | Offset feedback; lift dragged items |
| Haptic spam | A buzz on every tap, coin or particle; audible motor | Semantic patterns, rate limit, pairing, settings |
| Global state leaks | Time scale, camera offset or bus volume stuck after pause or scene change | Reset on lifecycle events; own state in one manager |
| Competing tweens | A property jumps or fights when events overlap | Kill or replace the previous tween per property; sum offsets |
| Frame-count timing | Feel changes at 120 Hz or under load | Seconds, `delta`, exponential smoothing |
| Repeated identical audio | The same sample four or more times a second | Variants, 3-6% pitch variation, voice limits |
| Deceptive juice | Celebration on non-wins, fake near-misses | Feedback reflects real state; see `legal-ethics` |
| No opt-out | No reduce-motion, haptics or flash settings | One settings object with OS defaults |
| Tuning only in the editor | Different feel on a release build on device | Tune on release builds on target hardware |

## Using the ontology

- The mechanic `feedback` field is the contract for feel. It lives in the design contract's `mechanics[]` (`${CLAUDE_PLUGIN_ROOT}/scripts/schemas/common.schema.json`) and in mechanic cards (`${CLAUDE_PLUGIN_ROOT}/scripts/schemas/mechanic-card.schema.json`), and accepts text or a list. Write one entry per channel plus a tier tag so the critic and the engineer read the same thing, and put the tunable numbers in `parameters`:

```json
{
  "id": "merge_two",
  "feedback": [
    "tier: major",
    "motion: pieces pull together 80 ms, pop 1.0 to 1.2 to 1.0 in 180 ms (back-out)",
    "particles: 12-particle burst, 0.4 s, family colour",
    "audio: merge sample, +1 semitone per chain link up to +7, 3% random pitch",
    "haptic: light impact at the pop, medium from chain 4, at most 10 per second",
    "numeric: +N pop-up above the merge point, counter bump on arrival"
  ],
  "parameters": [
    { "key": "hit_stop_ms", "value": 0, "min": 0, "max": 40, "unit": "ms", "note": "Only on chains of 4 or more; 0 in timing modes" },
    { "key": "haptic_max_hz", "value": 10, "min": 0, "max": 15, "unit": "Hz", "note": "Rate limit across all haptic calls" }
  ]
}
```

- Feel knobs (`hit_stop_ms`, `shake_trauma_hit`, `pop_overshoot`, `haptic_max_hz`) use lower snake_case keys with `min`, `max` and a `note` stating what breaks outside the range, so balance tools and remote config can see them.
- Juice failure modes belong in `failure_modes` with a detection signal: occlusion at chain depth, repeat fatigue, frame spike on first burst, stuck time scale after interruption. Thumb and occlusion notes go in `mobile_fit.notes` (mechanic card) or `mobile_notes` (contract mechanic).
- Accessibility commitments (reduced motion, haptics toggle, flash limit) go in the contract's `ux.accessibility`; effect cost ceilings go in `technical.perf_budgets`. Validate cards with `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_json.py --auto <file>`.
- Features with `area` of `vfx`, `audio` or `ux` should cite the mechanic id and tier. Their evidence is a before/after clip set plus the rubric result in `.gamestudio/evidence/F###/feel_review.md`, attached to the visual gate of `build-feature` next to `visual_review.md`.
- Agents: `arcosian:critic` scores the Feel dimension with the rubric; `arcosian:gameplay-engineer` implements the effects behind simulation events; `arcosian:ux-designer` writes the timing tables for interface feedback.

## Reference library

| File | Contains | Read when |
|---|---|---|
| `references/juice-catalog.md` | 45 numbered juice techniques in six channels (camera and time, object motion, visual effects, numbers and UI, audio, haptics), each with starting parameters, the lowest tier that earns it, and Godot 4 and Unity snippets | Adding, tuning or reviewing an effect |
| `references/input-animation-haptics.md` | Latency chain and budgets, forgiveness windows with code, gesture thresholds and dead zones, the 12 animation principles applied to games, easing formulas, timing table, Unity `Fx` and `Ease` helpers, haptics for iOS, Android, Godot and Unity, the `FeelSettings` layer, pairing and accessibility, volatile facts | Diagnosing input lag, writing motion specs, wiring haptics or accessibility options |
| `references/feel-review-rubric.md` | Evidence protocol, nine scored dimensions with anchors, weighted roll-up and gates, critique template, worked example, stills-versus-clips rules, feature acceptance checklist | Reviewing a build, comparing before and after, signing off a feature |

## Volatile facts (as of Oct 2026 — verify before relying)

Haptic API levels, engine method signatures and OS accessibility settings change; the dated list with sources is in `references/input-animation-haptics.md` section 7. Sources to recheck first:

- Apple Core Haptics and feedback generators: https://developer.apple.com/documentation/corehaptics
- Android `VibrationEffect` and `HapticFeedbackConstants`: https://developer.android.com/reference/android/os/VibrationEffect
- Godot `Input.vibrate_handheld`: https://docs.godotengine.org/en/stable/classes/class_input.html
- WCAG 2.3.1 Three Flashes or Below Threshold: https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold.html

## Related skills

- `mobile-ux`: thumb zones, touch targets, pop-up hierarchy and button states that feel specs rely on.
- `art-direction`: style and silhouette language the effects must obey.
- `technical-art`: shaders, VFX atlases and particle budgets that implement the catalog.
- `audio-direction`: SFX layers, pitch ladders, ducking and the mix that pair with visual juice.
- `gameplay-programming`: the simulation events presentation subscribes to; input buffering in the sim.
- `engine-godot`: Tween, particles, audio buses and export settings such as the Vibrate permission.
- `engine-unity`: coroutine and tween libraries, URP volumes, audio mixer and mobile plugin specifics.
- `qa-testing`: deterministic playthroughs and clip capture for before/after evidence.
- `accessibility-localization`: reduced motion, flash limits and haptic options in full.
- `mobile-performance`: particle and overdraw budgets, thermal behaviour and frame pacing.
