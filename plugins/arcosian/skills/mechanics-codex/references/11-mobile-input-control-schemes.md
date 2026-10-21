# 11 — Mobile Input and Control Schemes

A control scheme is the full contract between a thumb and the simulation: which screen regions accept which touches, how raw touches become game actions, what the game does for the player automatically, and what alternatives exist for players who cannot use the default. Verbs (tap, swipe, drag, hold, tilt, flick) are catalogued in `01-verbs-movement-physics.md` and auto-attack and auto-aim combat patterns in `02-combat-action.md`; this file covers the scheme layer above them: one-thumb portrait layouts, tap-anywhere schemes, context buttons, virtual sticks, aim sticks with tap-to-auto-aim, MOBA skill clusters, shooter layouts, HUD customisation, target selection, tap-to-move, swipe vocabularies, drag-aim conventions, board and card manipulation, camera gestures, tilt and gyro, auto-play and sweep controls, idle input, haptic languages, accessibility alternatives and controller support. Every entry gives precise rules, tuning values (dead zones, thresholds, sizes, timings) with what each does to feel, the failure modes that ship most often, and an implementation sketch. Values are practitioner starting points: expose them in a tuning panel, set them in data, and confirm on the smallest and largest target phones.

**Entry format.** Every entry maps 1:1 onto `${CLAUDE_PLUGIN_ROOT}/scripts/schemas/mechanic-card.schema.json`. Ids are kebab-case; ids from sibling files carry their file number, e.g. `directional-swipe` (01). Aesthetic targets use the eight MDA aesthetics (Hunicke, LeBlanc and Zubek, 2004). Units: `pt` (iOS) ≈ `dp` (Android) = 1/160 inch, so 1 mm ≈ 6.3 pt; times in ms.

## Contents

1. Scheme-level constants · 2. Index of schemes · 3. Choosing a scheme · 4. One-hand schemes (11.01–11.03) · 5. Stick-and-button schemes (11.04–11.09) · 6. Pointer and gesture schemes (11.10–11.14) · 7. Motion and automation (11.15–11.17) · 8. Feedback, access and hardware (11.18–11.20) · 9. Input QA checklist, platform API notes, related skills

## 1. Scheme-level constants

| Constant | Starting value | Why / source |
|---|---|---|
| Minimum touch target | 44×44 pt (Apple HIG), 48×48 dp (Material); WCAG 2.2 sets 24×24 CSS px as the AA minimum (2.5.8) and 44×44 as AAA (2.5.5) | Floors, not targets |
| Primary in-game action button | 60–90 pt diameter | Struck blind, often mid-motion |
| Gap between adjacent targets | ≥ 8 pt | Reduces fat-finger errors |
| Tap-versus-drag slop | 6–12 pt (Android framework default ≈ 8 dp) | Below: jittery taps register as drags; above: drags feel late |
| Long-press | 250–500 ms (OS defaults ≈ 400–500 ms) | Shorter in games where long-press is a core verb |
| Double-tap window | ≈ 300 ms | Any double-tap delays single-tap recognition by this much |
| One-hand comfort zone (portrait) | bottom ~40 % of the screen, biased to the gripping hand; top corners worst | Steven Hoober's observational study ("How Do Users Really Hold Mobile Devices?", UXmatters, 2013) found about half of users holding one-handed |
| Edge keep-out for game gestures | ≥ 16–24 pt from left/right edges, bottom home-indicator strip | OS back/home gestures live at the edges |
| Simultaneous touches designed for | 2 (core), 3 (advanced "claw" layouts) | More is unreliable across devices and hands |
| Input latency target | react on touch-down; never add frames of smoothing to action input | Each 60 Hz frame costs 16.7 ms on top of the touch and display pipeline |

## 2. Index of schemes

| # | Id | Scheme | Typical genres | Orientation | Hands |
|---|---|---|---|---|---|
| 11.01 | `one-thumb-portrait` | One-thumb portrait layout | puzzle, merge, survivors, card battlers | portrait | 1 |
| 11.02 | `tap-anywhere` | Tap-anywhere single input | hyper-casual, endless, timing | either | 1 |
| 11.03 | `context-action-button` | Context-sensitive action button | adventure, RPG, life sim | either | 1–2 |
| 11.04 | `virtual-stick` | Virtual movement stick (fixed / floating / dynamic) | action, RPG, survivors | either | 1–2 |
| 11.05 | `aim-stick` | Aim stick with tap-to-auto-aim | brawlers, shooters | landscape | 2 |
| 11.06 | `skill-cluster` | MOBA skill cluster with drag-aim and cancel | MOBA, ARPG | landscape | 2 |
| 11.07 | `fps-touch-scheme` | Mobile shooter layout | FPS, TPS, battle royale | landscape | 2–4 fingers |
| 11.08 | `hud-customization` | HUD layout editor | shooters, MOBA, action | landscape | 2 |
| 11.09 | `target-lock` | Target selection and lock-on | MOBA, ARPG, tactics | either | 1–2 |
| 11.10 | `tap-to-move` | Tap-to-move with pathfinding | adventure, RTS-lite, MMO | either | 1 |
| 11.11 | `swipe-command-scheme` | Swipe gesture vocabulary | runners, swipe combat | portrait | 1 |
| 11.12 | `drag-aim-scheme` | Drag-to-aim conventions | physics, golf, artillery, brawlers | either | 1 |
| 11.13 | `board-manipulation` | Board and card manipulation | match-3, merge, card games | portrait | 1 |
| 11.14 | `camera-gestures` | Camera pan, pinch and rotate | builders, strategy | either | 1–2 |
| 11.15 | `tilt-gyro-scheme` | Tilt steering and gyro aim | racers, climbers, shooters | either | 2 |
| 11.16 | `auto-play` | Auto-play, speed-up and sweep controls | squad RPG, gacha | portrait | 0–1 |
| 11.17 | `idle-input` | Idle input model | idle, incremental | portrait | 0–1 |
| 11.18 | `haptic-language` | Haptic patterns as a feedback language | all | — | — |
| 11.19 | `input-accessibility` | Accessibility alternatives | all | — | — |
| 11.20 | `controller-support` | Gamepad support | action, platformers, shooters | landscape | 2 |

## 3. Choosing a scheme

| If the game is… | Default scheme | Add | Avoid |
|---|---|---|---|
| Hyper-casual / timing | `tap-anywhere` | `haptic-language` | any on-screen buttons in the play area |
| Casual puzzle / merge | `one-thumb-portrait` + `board-manipulation` | two-tap alternative (`input-accessibility`) | gestures that need two hands |
| Survivors / auto-shooter | `virtual-stick` (floating) in portrait | `auto-attack` (02) | manual aim |
| Brawler / hero shooter | `virtual-stick` + `aim-stick` | `hud-customization`, `controller-support` | aim without auto-aim tap |
| MOBA | `virtual-stick` + `skill-cluster` + `target-lock` | `hud-customization` | context buttons for combat |
| FPS / battle royale | `fps-touch-scheme` | `hud-customization`, `tilt-gyro-scheme` (gyro), auto-fire | fixed sticks |
| Builder / strategy | `camera-gestures` + `tap-to-move` / tap-select | `board-manipulation` for placement | virtual sticks |
| Squad RPG / gacha | `auto-play` + tap-select | manual ultimate timing | twitch inputs |
| Idle | `idle-input` | `haptic-language` (light) | required rapid tapping |
| Premium action port | `virtual-stick` + face buttons | `controller-support`, `hud-customization` | touch-only release |

## 4. One-hand schemes

### 11.01 One-thumb portrait layout — `one-thumb-portrait`

- **Category:** control scheme · one-hand portrait
- **Player fantasy:** "I can play anywhere — on the bus, holding a coffee."
- **Core rules:**
  - *State:* zone map: primary interaction zone (bottom 40–50 %), play/view zone (middle), read-only HUD (top 10–15 %); handedness setting.
  - *Triggers:* every core verb originates in the primary zone; top-zone elements are display-only or rarely used menus.
  - *Effects:* all core actions are reachable by the gripping thumb; a mirrored layout serves left-handers.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Primary zone height | 40–50 % of screen height | Taller = more reach strain on large phones |
| Core button size | 56–72 pt | Struck without looking |
| Reach radius from grip pivot | ≈ 55–70 mm comfortable | Targets beyond it get missed or force regrips |
| Top HUD band | 10–15 % | Information only; nothing time-critical to tap |
| Handedness | mirror toggle | Left-handers are a meaningful minority |

- **Dynamics:** enables commute and queue play; raises session frequency; the play area sits above the thumb so the thumb never covers the action.
- **Aesthetic targets (MDA):** Submission (comfort), Sensation.
- **Feedback and juice:** pressed states on every control; light haptic ticks on core actions (`haptic-language`).
- **Failure modes and exploits:** pause, settings or close buttons in top corners during play; the thumb covering the thing being controlled; palm touches at the screen edge on large phones; purchase buttons placed where the thumb rests.
- **Mobile fit:** the definition of mobile-native; any session length.
- **Monetization hooks and the ethical limit:** keep offer and purchase buttons out of the reflexive tap path and always behind an explicit confirm; never move a "continue" button so the same tap lands on "buy".
- **Implementation notes:** run an automated reach audit on the layout for the smallest and largest supported screens.

```text
pivot = (W * (0.85 if right_handed else 0.15), H * 1.02)          # thumb base, just below the screen
reach_mm(e) = dist(center(e), pivot) / PT_PER_MM
audit(layout): for e in layout.interactive:
  if e.frequency == "core" and reach_mm(e) > COMFORT_MM: flag(e, "out of thumb reach")
  if e.size_pt < 44: flag(e, "below minimum target")
```
- **Reference games:** Royal Match, Candy Crush Saga, Clash Royale, Archero, Subway Surfers.
- **Combines well with:** `tap-anywhere`, `virtual-stick` (floating), `board-manipulation`, `auto-play`.

### 11.02 Tap-anywhere single input — `tap-anywhere`

- **Category:** control scheme · single input
- **Player fantasy:** "One touch — and total control of my timing."
- **Core rules:**
  - *State:* playfield = one button; exclusion rectangles around HUD buttons; one-slot input buffer.
  - *Triggers:* touch-down (timing games) or touch-up (deliberate commits) anywhere outside exclusions.
  - *Effects:* one game action per press; a hold variant splits tap from hold by duration (verb details in `tap`, `hold-release` and `one-tap-impulse` (01)).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| React on | touch-down for timing; touch-up only for commits | Touch-up adds the whole press duration as latency |
| Input buffer | 80–150 ms | Early presses still count; too long feels unresponsive to cancels |
| Tap/hold split | 120–200 ms | Shorter misreads taps as holds |
| HUD exclusion margin | 8–16 pt around buttons | Prevents pause presses from triggering a jump |
| Scene-start ignore window | 200–300 ms | Stops the "start" tap from also firing the first action |
| Second-finger policy | ignore / same as first | Ignoring prevents double inputs from two-thumb players |

- **Dynamics:** instant learnability; pure timing skill; ideal for playable ads and hyper-casual onboarding.
- **Aesthetic targets (MDA):** Challenge, Sensation.
- **Feedback and juice:** feedback on touch-down (sound, squash, haptic), not on release.
- **Failure modes and exploits:** HUD buttons stealing or leaking taps; the first tap starting a run by accident; double-firing with two thumbs; latency from frame-based polling.
- **Mobile fit:** one hand, either orientation, any session length.
- **Monetization hooks and the ethical limit:** interstitials must never appear where the next game tap would land on the ad (see `interstitial-cadence` (12)).
- **Implementation notes:** handle raw pointer events, timestamped, processed in the next fixed simulation step.

```text
on_pointer_down(e):
  if t_since_scene_start() < IGNORE_MS or in_exclusion(e.pos) or (active_pointer and e.id != active_pointer): return
  active_pointer = e.id; buffer = (e.t, PRESS)
sim_step(): if buffer and now - buffer.t <= BUFFER_MS and can_act(): act(); buffer = None
on_pointer_up(e): if e.id == active_pointer: active_pointer = None
```
- **Reference games:** Flappy Bird, Geometry Dash, Crossy Road, Alto's Adventure, Stack.
- **Combines well with:** `one-thumb-portrait`, `haptic-language`, `input-accessibility`.

### 11.03 Context-sensitive action button — `context-action-button`

- **Category:** control scheme · button economy
- **Player fantasy:** "The game knows what I mean."
- **Core rules:**
  - *State:* candidates within interaction radius; priority table (attack > revive > open > talk > pick up, or per mode); current displayed action.
  - *Triggers:* candidate set changes as the player moves; the player presses the single action button.
  - *Effects:* the button icon and label show the resolved action; pressing performs it on the resolved target; with no candidate it falls back to a default (attack or jump).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Interaction radius | 1–2 character widths | Larger = convenient; smaller = precise |
| Facing weight | candidates in front weighted 1.5–3× | Prevents interacting with things behind you |
| Icon hysteresis | 100–200 ms or a distance margin | Stops flicker between two nearby targets |
| Combat lockout | context actions other than attack disabled in combat | Prevents "talked to the chest instead of attacking" |
| Multi-candidate UI | list of 2–3 prompts vs single best | Lists are explicit but cost screen space |

- **Dynamics:** fewer buttons, less occlusion, faster learning.
- **Aesthetic targets (MDA):** Submission (flow), Fantasy.
- **Feedback and juice:** icon morphs with a short scale pop; target outline on the resolved object.
- **Failure modes and exploits:** wrong action under pressure; flicker; hidden affordances when the player does not know an object is interactable.
- **Mobile fit:** excellent — one big button in the thumb zone replaces three small ones.
- **Monetization hooks and the ethical limit:** never resolve the context button to a store or offer action.
- **Implementation notes:** score candidates, keep the current one unless another beats it by a margin.

```text
resolve(p): best = max(candidates(p), key=lambda c: PRIORITY[c.kind] * 100 + facing(p, c) * F - dist(p, c), default=None)
  if current and best is not current and score(best) < score(current) + HYSTERESIS: best = current
  current = best; button.show(best.kind if best else DEFAULT)
```
- **Reference games:** The Legend of Zelda: Ocarina of Time (context action button), Genshin Impact (mobile interaction prompts), Stardew Valley (mobile tap-to-interact).
- **Combines well with:** `virtual-stick`, `target-lock`, `tap-to-move`.

## 5. Stick-and-button schemes

### 11.04 Virtual movement stick — `virtual-stick`

- **Category:** control scheme · analog movement on glass
- **Player fantasy:** "Fluid, analog control with just my thumb."
- **Core rules:**
  - *State:* mode `fixed | floating | dynamic`; origin; knob position; owning pointer id; activation zone.
  - *Triggers:* touch-down inside the activation zone (fixed: within 1.2 R of the stick; floating/dynamic: anywhere in the zone, origin placed under the thumb); move; up.
  - *Effects:* deflection d = knob − origin; magnitude m = |d| / R clamped to 1; radial dead zone and response curve give the movement vector; in dynamic mode the origin follows when |d| > R so there is no dead edge.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Outer radius R | 45–70 pt (≈ 7–11 mm) | Smaller = twitchy; larger = more thumb travel |
| Radial dead zone | 8–20 % of R | Absorbs tremor; too large feels laggy at start |
| Response curve exponent γ | 1.0–2.0 | Above 1 gives fine control near centre |
| Activation zone (floating) | left 40–50 % of screen, below the HUD | Bigger tolerates sloppy placement |
| Run threshold | ≥ 80–90 % deflection | Walk and run without another button |
| Idle opacity | 20–50 % | Discoverable but unobtrusive |

  Formula: `out = 0 if m < dz else ((m − dz) / (1 − dz))^γ · d/|d|`. Use a radial dead zone, never per-axis, or movement snaps to eight directions.
- **Dynamics:** movement precision and dodging; thumb fatigue in long sessions.
- **Aesthetic targets (MDA):** Sensation, Challenge.
- **Feedback and juice:** knob follows the thumb exactly; base fades in under the thumb; a subtle tick when crossing the run threshold.
- **Failure modes and exploits:** thumb drift off a fixed stick (floating or dynamic fixes it); the stick hidden under the thumb (draw a direction arrow on the character); left-edge conflict with Android back gestures (keep the zone off the edge or request exclusion rects); lost pointer id when another finger lifts; axial dead zones causing eight-way snapping.
- **Mobile fit:** two-thumb landscape standard; one-thumb portrait works with a floating stick plus auto-attack.
- **Monetization hooks and the ethical limit:** none.
- **Implementation notes:** track pointer ids; never read "touch 0".

```text
on_down(e): if stick.pointer is None and in_zone(e.pos): stick.pointer = e.id; stick.origin = e.pos if mode != FIXED else stick.home
on_move(e): if e.id != stick.pointer: return
  d = e.pos - stick.origin
  if mode == DYNAMIC and len(d) > R: stick.origin += d - normalize(d) * R; d = normalize(d) * R
  m = min(len(d) / R, 1); stick.out = 0 if m < DZ else ((m - DZ) / (1 - DZ)) ** GAMMA * normalize(d)
on_up(e): if e.id == stick.pointer: stick.pointer = None; stick.out = 0
```
- **Reference games:** Archero, Brawl Stars, Genshin Impact, PUBG Mobile, Vampire Survivors (mobile).
- **Combines well with:** `aim-stick`, `skill-cluster`, `hud-customization`, `auto-attack` (02).

### 11.05 Aim stick with tap-to-auto-aim — `aim-stick`

- **Category:** control scheme · right-thumb aiming (assist maths: `twin-stick-aim-assist` (02))
- **Player fantasy:** "Quick shots when I'm busy, perfect shots when I take aim."
- **Core rules:**
  - *State:* attack button that doubles as an aim stick; aim vector; mode `tap | aiming | cancel`.
  - *Triggers:* touch-down on the button; drag; release.
  - *Effects:* release within the tap time and inside the aim dead zone → fire at the auto-selected target; drag beyond the aim dead zone → manual aim with a trajectory or area preview, release fires along the aim; dragging back to the centre (or into a cancel zone) and releasing cancels.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Aim dead zone | 15–30 % of stick radius | Below it, input counts as a tap (auto-aim) |
| Tap time | 150–250 ms | Longer accepts slow taps; shorter lets fast flicks count as aimed |
| Auto-target rule | nearest / lowest HP / in-front cone 60–120° | Predictable rules beat "smart" ones players cannot read |
| Preview | line, cone or landing circle; offset above the thumb | Without offset the thumb hides the preview |
| Cancel | back to centre, or a cancel zone above the stick | Missing cancel = wasted cooldowns and frustration |

- **Dynamics:** a skill floor (tap) and a skill ceiling (leading shots, bank shots) in one control; mind games around auto-aim targets.
- **Aesthetic targets (MDA):** Challenge, Sensation.
- **Feedback and juice:** aim preview colour change when a target is in range; cancel state turns the preview grey; distinct sounds for auto and aimed shots.
- **Failure modes and exploits:** auto-aim choosing the tank instead of the low-health target; accidental fire while trying to cancel; the preview occluded by the thumb; inconsistent behaviour between tap and drag.
- **Mobile fit:** landscape, two thumbs; works in portrait only with simplified aim.
- **Monetization hooks and the ethical limit:** never sell aim assistance in competitive modes.
- **Implementation notes:** classify on release; keep the auto-target function shared with bots and replays.

```text
on_release(e):
  d = e.pos - btn.center; held = e.t - btn.down_t
  if in_cancel(e.pos) or (btn.was_aiming and len(d) < AIM_DZ): return cancel()
  if not btn.was_aiming and held <= TAP_MS: fire(direction_to(auto_target(RULE)))
  else: fire(normalize(d))
on_move(e): if len(e.pos - btn.center) >= AIM_DZ: btn.was_aiming = True; show_preview(normalize(e.pos - btn.center))
```
- **Reference games:** Brawl Stars, Pokémon Unite, League of Legends: Wild Rift.
- **Combines well with:** `virtual-stick`, `target-lock`, `hud-customization`, `twin-stick-aim-assist` (02).

### 11.06 MOBA skill cluster with drag-aim and cancel — `skill-cluster`

- **Category:** control scheme · multi-ability layout (ability rules: `cooldown-abilities` (02))
- **Player fantasy:** "Every ability is under my thumb, and I can place it exactly."
- **Core rules:**
  - *State:* basic-attack button (large) bottom-right; 3–4 skill buttons in an arc around it; per-skill cast mode `quick | aimed`; cancel area; cooldown and resource state.
  - *Triggers:* tap, drag, release per button; portrait or enemy tap for target lock.
  - *Effects:* quick cast fires at the auto target; aimed cast maps drag distance to world range and direction, shows an indicator, casts on release; release in the cancel area or back on the button cancels without cooldown.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Basic attack size | 70–90 pt | Most-pressed control; must be unmissable |
| Skill button size | 50–65 pt | Smaller means misfires in fights |
| Arc radius from basic attack | 70–110 pt | Too tight = misfires; too wide = reach strain |
| Drag-to-range mapping | full range at 60–80 pt of drag, linear | Non-linear mappings confuse placement |
| Cancel area | above the cluster or a "drag back" gesture | Needed for every aimed skill |
| Target priority options | closest / lowest HP / lowest HP % | Lets players tune auto-targeting to their role |

- **Dynamics:** high skill ceiling; muscle memory; layout customisation becomes part of mastery.
- **Aesthetic targets (MDA):** Challenge, Fellowship (team play), Sensation.
- **Feedback and juice:** cooldown sweep and number; "ready" pulse and haptic tick; range indicator on the ground.
- **Failure modes and exploits:** fat-finger wrong skill; cancel misfires; occlusion of the battlefield on small phones; indicator hidden under the thumb.
- **Mobile fit:** landscape, two thumbs; sessions of 10–20 minutes per match.
- **Monetization hooks and the ethical limit:** cosmetic skill effects only; never sell larger hitboxes or better indicators.
- **Implementation notes:** a small state machine per button; multi-touch safe (each button owns its pointer id).

```text
state per button: IDLE -(down)-> PRESSED -(move > AIM_DZ)-> AIMING -(enter cancel)-> CANCELLING
  PRESSED -(up)-> quick_cast(auto_target(priority))       AIMING -(up)-> cast(range_from(drag), dir)
  CANCELLING -(up)-> IDLE (no cooldown)                     CANCELLING -(leave cancel)-> AIMING
range_from(drag) = clamp(len(drag) / FULL_RANGE_PT, 0, 1) * skill.max_range
```
- **Reference games:** Mobile Legends: Bang Bang, Honor of Kings, League of Legends: Wild Rift, Pokémon Unite.
- **Combines well with:** `virtual-stick`, `target-lock`, `hud-customization`, `cooldown-abilities` (02).

### 11.07 Mobile shooter layout — `fps-touch-scheme`

- **Category:** control scheme · first/third-person shooting
- **Player fantasy:** "Console-grade shooting on my phone."
- **Core rules:**
  - *State:* left floating stick; right-half look area; fire button(s) on the right and optionally a mirrored fire button on the left; aim-down-sights, crouch, jump, reload; optional auto-fire and gyro.
  - *Triggers:* look-area drags; button presses; crosshair-on-target events (auto-fire).
  - *Effects:* look drag delta rotates the camera by sensitivity (degrees per point); fire buttons can also act as look areas while held; auto-fire shoots when the crosshair overlaps a valid target.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Look sensitivity (hip) | 0.2–0.5° per pt | Higher = fast turns, shaky aim |
| ADS sensitivity | 0.5–0.7× hip | Precision when zoomed |
| Look micro dead zone | 1–3 pt | Removes jitter from a resting thumb |
| Acceleration curve | off by default | Acceleration breaks muscle memory |
| Auto-fire delay | 0–150 ms after overlap | Lower = stronger assist |
| Left fire button | on / off | Lets the right thumb keep looking while firing |

- **Dynamics:** players graduate from two thumbs to three- and four-finger "claw" grips; layouts are shared like settings presets.
- **Aesthetic targets (MDA):** Challenge, Sensation, Fellowship.
- **Feedback and juice:** hit markers, recoil kick, short haptic per shot (rate-limited), damage-direction indicators.
- **Failure modes and exploits:** look-versus-fire thumb conflict (solve with auto-fire or a left fire button); button clutter; edge swipes triggering OS gestures; frame-rate-dependent look sensitivity.
- **Mobile fit:** landscape, two hands, 5–25 minute matches; needs `hud-customization`.
- **Monetization hooks and the ethical limit:** weapon skins only; no stat-bearing purchases in ranked modes.
- **Implementation notes:** convert look deltas using the touch timestamp, never per-frame scaling; separate pointer ownership for stick, look and buttons.

```text
on_move(e):
  if e.id == look.pointer or (e.id == fire.pointer and FIRE_DRAG_LOOKS):
    dx, dy = e.delta_pt; if abs(dx) + abs(dy) < LOOK_DZ: return
    s = ADS_SENS if ads else HIP_SENS; cam.yaw += dx * s; cam.pitch = clamp(cam.pitch - dy * s, -85, 85)
```
- **Reference games:** Call of Duty: Mobile, PUBG Mobile, Free Fire.
- **Combines well with:** `virtual-stick`, `hud-customization`, `tilt-gyro-scheme`, `controller-support`.

### 11.08 HUD layout editor — `hud-customization`

- **Category:** control scheme · player-configurable layout
- **Player fantasy:** "My controls, exactly where my fingers want them."
- **Core rules:**
  - *State:* per-control `{anchor, offset, size, opacity, visible}` in safe-area-relative coordinates; presets; per-orientation and per-aspect profiles.
  - *Triggers:* entering edit mode; dragging, resizing, toggling; selecting a preset; resetting.
  - *Effects:* the layout is validated (no overlaps, minimum sizes, inside the safe area) and saved to the cloud profile.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Size range | 70–150 % of default, never below 44 pt | Accessibility and claw grips both need range |
| Opacity range | 20–100 % | Low opacity reveals more of the scene |
| Snap grid | 4–8 pt | Neat layouts; too coarse frustrates |
| Presets | 2-finger, 3-finger, 4-finger, left-handed | Most players pick a preset rather than editing |
| Overlap tolerance | 0 | Overlaps create ambiguous touches |

- **Dynamics:** personal optimisation; pro layouts shared in the community; competitive edge for invested players.
- **Aesthetic targets (MDA):** Expression, Challenge.
- **Feedback and juice:** live preview over a gameplay screenshot; red outline on invalid placement; one-tap reset.
- **Failure modes and exploits:** unreachable or overlapping controls; layouts that break on a new aspect ratio (store normalised anchors, not pixels); losing the layout on reinstall.
- **Mobile fit:** essential for shooters and MOBAs; optional elsewhere.
- **Monetization hooks and the ethical limit:** none — never sell layout slots.
- **Implementation notes:** anchors relative to safe-area corners; validate on load and fall back to the default if a saved layout is invalid on the current device.

```text
position(ctrl, safe) = corner(safe, ctrl.anchor) + ctrl.offset_norm * min(safe.w, safe.h)
validate(layout, safe): for a, b in pairs(layout.visible): assert not overlap(rect(a), rect(b))
  for c in layout.visible: assert c.size_pt >= 44 and inside(rect(c), safe)
```
- **Reference games:** Call of Duty: Mobile, PUBG Mobile, Genshin Impact, Mobile Legends: Bang Bang.
- **Combines well with:** `fps-touch-scheme`, `skill-cluster`, `virtual-stick`, `input-accessibility`.

### 11.09 Target selection and lock-on — `target-lock`

- **Category:** control scheme · target acquisition (tower-side rules: `tower-targeting` (02))
- **Player fantasy:** "I pick the fight I want, even in chaos."
- **Core rules:**
  - *State:* current target; lock flag; priority rule; candidate list in range.
  - *Triggers:* tap on an enemy (expanded hit area); tap on a portrait or lock button; swipe on the lock button to cycle; target death or out-of-range.
  - *Effects:* abilities and auto-attacks prefer the locked target; the camera softly keeps it framed; the lock breaks on death, range or line-of-sight loss.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Tap hit area | collider × 1.5–2, minimum 44–60 pt | Crowded fights need generous areas plus priority tie-breaks |
| Lock break range | 1.2–1.5× ability range | Too tight drops lock constantly |
| Retarget delay | 0–300 ms after death | Instant retarget can pull players into danger |
| Camera assist | 0–50 % blend | Strong assist fights manual camera control |
| Priority rules | closest / lowest HP / lowest HP % / threat | Expose as a setting for competitive players |

- **Dynamics:** focus fire; target-swapping skill; protecting allies by peeling.
- **Aesthetic targets (MDA):** Challenge, Fellowship.
- **Feedback and juice:** lock ring under the target; portrait highlight; short haptic on lock.
- **Failure modes and exploits:** tapping a crowd selects the wrong unit; the lock lost behind obstacles; camera assist fighting the player; tap-to-target colliding with tap-to-move.
- **Mobile fit:** reduces precision demands on small screens; works in both orientations.
- **Monetization hooks and the ethical limit:** none.
- **Implementation notes:** resolve taps in screen space with priority tie-breaks.

```text
pick_target(tap): hits = [e for e in enemies if screen_dist(tap, e) <= max(HIT_MIN_PT, e.screen_radius * HIT_SCALE)]
  return min(hits, key=lambda e: (PRIORITY(e), screen_dist(tap, e)), default=None)
update(): if lock and (lock.dead or dist(p, lock) > BREAK_RANGE or not los(p, lock)): lock = None; schedule_retarget(RETARGET_MS)
```
- **Reference games:** Mobile Legends: Bang Bang, Pokémon Unite, World of Warcraft (tab targeting, as the PC ancestor).
- **Combines well with:** `skill-cluster`, `aim-stick`, `tap-to-move`, `context-action-button`.

## 6. Pointer and gesture schemes

### 11.10 Tap-to-move with pathfinding — `tap-to-move`

- **Category:** control scheme · point-and-go
- **Player fantasy:** "I point, and my character goes — I think about where, not how."
- **Core rules:**
  - *State:* destination; path; interaction target; hold-to-follow flag.
  - *Triggers:* tap on ground (move), tap on object or NPC (move then interact), tap on enemy (move then attack), hold (continuous follow), double-tap (run).
  - *Effects:* pathfind and walk; arrival triggers the queued interaction; a new tap overrides the queue.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Interactable snap radius | 24–40 pt in screen space | Forgives imprecise taps on small objects |
| Hold-to-follow threshold | 200–300 ms | Separates taps from continuous steering |
| Arrival radius | 0.2–0.5 character widths | Too small causes jitter at the destination |
| Repath interval | 100–500 ms for moving targets | Lower = responsive, more CPU |
| Destination marker | brief ring at the tapped point | Confirms the input landed |

- **Dynamics:** deliberate, planning-oriented movement; accessible to non-gamers.
- **Aesthetic targets (MDA):** Submission, Discovery, Narrative.
- **Feedback and juice:** tap ripple, path preview dots, character turns immediately even before the path resolves.
- **Failure modes and exploits:** UI-versus-world tap ambiguity; imprecise for dodging in action games; paths around moving obstacles stall; tiny targets.
- **Mobile fit:** one hand, portrait or landscape; ideal for adventure, puzzle and builder genres.
- **Monetization hooks and the ethical limit:** none.
- **Implementation notes:** raycast UI first, then interactables (with snap), then ground; A* on a navmesh or grid.

```text
on_tap(pos):
  if ui_hit(pos): return
  obj = nearest_interactable_screen(pos, SNAP_PT)
  goal = obj.approach_point if obj else ground_point(pos)
  path = astar(nav, player.pos, goal); player.follow(path, on_arrive=(obj.interact if obj else None)); show_marker(goal)
```
- **Reference games:** Monument Valley, Old School RuneScape (mobile), Albion Online, Kingdom Rush (hero movement).
- **Combines well with:** `camera-gestures`, `context-action-button`, `target-lock`.

### 11.11 Swipe gesture vocabulary — `swipe-command-scheme`

- **Category:** control scheme · gesture commands (verb details: `directional-swipe`, `slice` (01))
- **Player fantasy:** "Fluid flicks, instant reactions."
- **Core rules:**
  - *State:* vocabulary of 2–6 gestures mapped to commands; gesture recogniser per pointer; one-slot command buffer.
  - *Triggers:* touch movement crossing the distance threshold within the time limit.
  - *Effects:* the gesture is classified by angle sector at the moment the threshold is crossed (not on lift) and its command executes or is buffered.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Minimum distance | 20–40 pt (or 4–6 % of the short side) | Lower = sensitive, more false positives |
| Maximum duration | 250–400 ms | Longer accepts lazy swipes, blurs into drags |
| Angle sectors | 90° each for 4-way; reject or nearest within ±10–15° of diagonals | Diagonal misreads are the top complaint |
| Recognise on | threshold crossing | Lift-based recognition adds the rest of the swipe as latency |
| Command buffer | 100–200 ms | Queues the next lane change during an animation |
| Vocabulary size | ≤ 6 | Larger vocabularies raise error rates sharply |

- **Dynamics:** rhythmic reflex play; gesture fluency becomes skill.
- **Aesthetic targets (MDA):** Sensation, Challenge.
- **Feedback and juice:** immediate character response; swipe trail for slice games; haptic tick per recognised gesture.
- **Failure modes and exploits:** diagonal misclassification; swipes that begin at the screen edge triggering OS navigation; swipe-versus-scroll conflicts in menus; recognition on lift.
- **Mobile fit:** portrait, one thumb; perfect for runners.
- **Monetization hooks and the ethical limit:** none.
- **Implementation notes:** one recogniser per pointer; ignore touches that start in edge keep-out zones.

```text
on_move(e): g = rec[e.id]
  if g.fired or e.t - g.t0 > MAX_MS: return
  d = e.pos - g.p0
  if len(d) >= MIN_PT:
    a = degrees(atan2(-d.y, d.x)) % 360; dir = SECTORS.lookup(a, reject_band=AMBIG_DEG)
    if dir: g.fired = True; buffer_or_execute(COMMANDS[dir])
```
- **Reference games:** Subway Surfers, Temple Run, Infinity Blade, Fruit Ninja.
- **Combines well with:** `one-thumb-portrait`, `haptic-language`, `input-accessibility` (tap alternatives).

### 11.12 Drag-to-aim conventions — `drag-aim-scheme`

- **Category:** control scheme · aim-and-release (physics: `slingshot-aim-release`, `trajectory-ballistics` (01))
- **Player fantasy:** "I line it up just right — then let it fly."
- **Core rules:**
  - *State:* convention `pull_back | push_forward`; drag origin (object or anywhere); aim vector; power; precision mode.
  - *Triggers:* drag start (on the object or anywhere, by design); drag; release; return to origin.
  - *Effects:* pull-back launches opposite to the drag (slingshot); push-forward launches along it (aim stick); power = f(drag length); release inside the cancel radius cancels.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Max drag radius | 80–160 pt | Longer = finer power resolution, more travel |
| Power curve | linear or eased (exponent 1.2–1.5) | Eased curves give control at low power |
| Trajectory preview | 20–60 % of the path (full in casual) | Partial preview keeps skill in the shot |
| Cancel radius | 15–25 pt around the origin | Without it, every touch commits a shot |
| Precision mode | beyond max radius or second finger → 0.25× sensitivity | Fine adjustments without restarting the drag |

- **Dynamics:** physics-based skill expression; readable "one more try" loops.
- **Aesthetic targets (MDA):** Challenge, Sensation.
- **Feedback and juice:** band stretch and creak, power meter, angle readout in golf-style games, haptic detents at power steps.
- **Failure modes and exploits:** the finger occluding the projectile (allow aiming from anywhere); mixing conventions between modes; no cancel; frame-rate-dependent launches.
- **Mobile fit:** one hand, both orientations; turn-based variants suit any session length.
- **Monetization hooks and the ethical limit:** "longer aim line" boosters exist in casual games; never sell them in competitive PvP.
- **Implementation notes:** compute launch velocity at release from the aim vector, in the fixed simulation step.

```text
on_release(e): d = e.pos - origin
  if len(d) < CANCEL_PT: return cancel()
  dir = -normalize(d) if CONVENTION == PULL_BACK else normalize(d)
  power = (min(len(d), MAX_PT) / MAX_PT) ** POWER_EXP; sim.queue(launch(dir, power * MAX_SPEED))
```
- **Reference games:** Angry Birds, Golf Clash, Bowmasters, Brawl Stars (push-forward aiming).
- **Combines well with:** `aim-stick`, `haptic-language`, `input-accessibility`.

### 11.13 Board and card manipulation — `board-manipulation`

- **Category:** control scheme · grid and card interaction (verbs: `drag` (01), rules: `match3-swap` (03))
- **Player fantasy:** "Pieces go exactly where I mean them to."
- **Core rules:**
  - *State:* interaction mode `swipe_swap | drag_drop | tap_tap`; selected piece; drop targets.
  - *Triggers:* swipe across a tile edge; drag and release; tap a piece, then tap a destination.
  - *Effects:* swap, move or play; invalid moves animate back with a shake; cards dropped outside valid zones return to hand.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Swap threshold | 30–50 % of a tile | Lower triggers accidental swaps |
| Lift offset | 30–60 pt above the finger | Keeps the dragged piece visible |
| Drop snap radius | 40–60 % of a cell | Forgiving drops on small grids |
| Pick-up delay | 0 ms on boards; 150–250 ms in scrollable lists | Separates scroll from drag in lists |
| Invalid-move feedback | 150–250 ms shake and return | Clear "no" without punishment |

- **Dynamics:** fast, low-friction play; the board stays readable because the finger does not cover the target.
- **Aesthetic targets (MDA):** Submission, Challenge.
- **Feedback and juice:** lift scale 1.1–1.2× with shadow; target highlight under the dragged item; snap and haptic tick on drop.
- **Failure modes and exploits:** finger hiding the destination; accidental swaps while scrolling; no two-tap alternative for motor-impaired players; ambiguous drop targets on dense boards.
- **Mobile fit:** portrait, one thumb; the backbone of puzzle and card games.
- **Monetization hooks and the ethical limit:** none in the scheme itself; boosters are in file 12.
- **Implementation notes:** support all three modes through one action layer so tap-tap can be an accessibility option.

```text
on_down(e): sel = piece_at(e.pos); start = e.pos
on_move(e): if sel and MODE == SWIPE and len(e.pos - start) > SWAP_FRAC * TILE: try_swap(sel, neighbour(sel, dir(e.pos - start))); sel = None
on_up(e): if MODE == DRAG and sel: drop(sel, snap_target(e.pos + LIFT, SNAP_R))
          elif MODE == TAP_TAP: pending = sel if not pending else (try_move(pending, cell_at(e.pos)) or None)
```
- **Reference games:** Candy Crush Saga, Royal Match, Hearthstone, Clash Royale, Merge Mansion.
- **Combines well with:** `one-thumb-portrait`, `input-accessibility`, `haptic-language`, `merge-board` (09).

### 11.14 Camera pan, pinch and rotate — `camera-gestures`

- **Category:** control scheme · camera navigation
- **Player fantasy:** "I glide over my world and zoom straight to what matters."
- **Core rules:**
  - *State:* camera position, zoom, rotation; gesture state `idle | pan | pinch | object_drag`; velocity for inertia.
  - *Triggers:* one finger on empty ground beyond slop → pan; two fingers → pinch/rotate; touch on a movable object → select, long-press → object drag.
  - *Effects:* pan follows the finger 1:1 in world space; pinch scales around the finger midpoint; release keeps momentum with friction; bounds rubber-band.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Zoom range | 2–4× between min and max | Wider needs LOD and readable icons at both ends |
| Inertia friction | v *= exp(−k·dt), k ≈ 4–8 s⁻¹ | Low k = floaty; high k = sticky |
| Pan slop | 8–12 pt | Prevents taps becoming micro-pans |
| Rubber-band overshoot | 5–10 % of the viewport | Communicates edges softly |
| Object-drag activation | long-press 250–400 ms on placed objects | Stops accidental building moves while panning |

- **Dynamics:** fluid overview-to-detail navigation; less UI chrome.
- **Aesthetic targets (MDA):** Submission, Expression (admiring your creation).
- **Feedback and juice:** smooth inertia; zoom-level icon swaps (LOD); edge bounce.
- **Failure modes and exploits:** moving buildings by accident; zoom jumping because the midpoint is not kept fixed; camera fighting tap-to-move; pinch being misread as two taps.
- **Mobile fit:** essential for builders and strategy; one-finger pan works one-handed, pinch needs two.
- **Monetization hooks and the ethical limit:** none.
- **Implementation notes:** keep the world point under the pinch midpoint fixed while scaling.

```text
on_pinch(p0a, p0b, pa, pb):
  world_mid = screen_to_world((p0a + p0b) / 2)
  cam.zoom = clamp(zoom_start * dist(pa, pb) / dist(p0a, p0b), Z_MIN, Z_MAX)
  cam.pos += world_mid - screen_to_world((pa + pb) / 2)      # keep the midpoint anchored
```
- **Reference games:** Clash of Clans, SimCity BuildIt, Township, Rise of Kingdoms.
- **Combines well with:** `tap-to-move`, `board-manipulation`, `city-zoning` (09).

## 7. Motion and automation

### 11.15 Tilt steering and gyro aim — `tilt-gyro-scheme`

- **Category:** control scheme · device motion (verb: `tilt` (01))
- **Player fantasy:** "I steer with my whole hands — and aim with tiny wrist movements."
- **Core rules:**
  - *State:* neutral orientation; filtered gravity vector (tilt) or angular velocity (gyro); activation mode `always | while_touching | ads_only`.
  - *Triggers:* sensor samples; calibration at level start or on request.
  - *Effects:* tilt angle beyond the dead zone maps to steering up to saturation; gyro rotation adds to camera look on top of touch.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Tilt dead zone | 2–5° | Absorbs hand tremor and posture drift |
| Tilt saturation | 20–35° | Smaller = twitchy; larger = tiring |
| Gyro sensitivity | 0.5–2.0 (camera degrees per device degree) | Higher = small wrist motions turn far |
| Filtering | 1€ filter, min cutoff ≈ 1 Hz | Smooth at rest, responsive in fast motion |
| Activation | while touching fire / ADS only | "Ratcheting" lets players re-centre their wrists |

  The 1€ filter (Casiez, Roussel and Vogel, 2012) adapts its cutoff to speed: heavy smoothing when still, light smoothing when moving fast.
- **Dynamics:** fine aim corrections on top of coarse touch look; physical, embodied steering.
- **Aesthetic targets (MDA):** Sensation, Challenge.
- **Feedback and juice:** horizon tilt in racers; on-screen neutral indicator; recalibrate button.
- **Failure modes and exploits:** playing lying down or in a moving vehicle; motion sickness; drift without recalibration; no alternative input (WCAG 2.2 criterion 2.5.4 asks that motion-operated functions have a UI alternative and can be disabled).
- **Mobile fit:** both hands; always optional, never the only way to play.
- **Monetization hooks and the ethical limit:** none.
- **Implementation notes:** read sensors at their native rate, filter, and sample into the fixed simulation step.

```text
tilt = one_euro(gravity_angle(sample) - neutral, t)
steer = 0 if abs(tilt) < DZ else sign(tilt) * min((abs(tilt) - DZ) / (SAT - DZ), 1)
if gyro_active(): cam.yaw += one_euro(sample.gyro.y, t) * dt * GYRO_SENS
```
- **Reference games:** Doodle Jump (tilt), the Asphalt series (tilt steering option), PUBG Mobile (gyroscope aiming), Call of Duty: Mobile (gyroscope option).
- **Combines well with:** `fps-touch-scheme`, `input-accessibility`, `controller-support`.

### 11.16 Auto-play, speed-up and sweep controls — `auto-play`

- **Category:** control scheme · delegated play (battle resolution: `auto-battle-squad` (02))
- **Player fantasy:** "My team fights while I plan — and I step in for the big moments."
- **Core rules:**
  - *State:* auto toggle; speed multiplier; repeat count; sweep eligibility per stage.
  - *Triggers:* player toggles auto or speed; stage clear with the required rating unlocks sweep; manual input during auto.
  - *Effects:* an AI policy drives the same input layer the player uses; manual input overrides for that action (often the ultimate); repeat re-runs a stage; sweep grants rewards for cleared stages without playing.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Speed options | ×1 / ×2 / ×3–4 | Faster farming; spectacle loss |
| Manual advantage on hard content | small but real, roughly 5–15 % efficiency | Keeps skill relevant without forcing manual play |
| Auto unlock | after first manual clear or account level 3–10 | Teaches the game before automating it |
| Sweep requirement | full-star clear | Converts mastery into time saved |
| Battery-saver mode | 30 fps, dimmed UI during auto | Long farming sessions without heat |

- **Dynamics:** play shifts from execution to preparation (team building, gear); "second-screen" sessions.
- **Aesthetic targets (MDA):** Submission, Expression (team building), Challenge (on hard content).
- **Feedback and juice:** clear auto and speed indicators; highlight when the ultimate is ready for manual timing.
- **Failure modes and exploits:** auto so strong the game plays itself for everyone; so weak farming is tedious; sweep tickets as the main monetization pressure; auto AI wasting ultimates.
- **Mobile fit:** portrait, zero to one hand; ideal for interrupted sessions.
- **Monetization hooks and the ethical limit:** higher speeds or auto-repeat inside VIP or passes are common. Basic auto must be free; sold conveniences must not become required for normal pacing.
- **Implementation notes:** the AI policy emits the same action messages as touch input so replays, determinism and tests stay identical.

```text
tick(): actions = player_inputs.drain()
  if auto_on: actions = merge(actions, policy.decide(sim.state))   # manual actions win conflicts
  sim.step(actions, dt * speed)
```
- **Reference games:** AFK Arena, Raid: Shadow Legends, Summoners War, Honkai: Star Rail.
- **Combines well with:** `one-thumb-portrait`, `auto-battle-squad` (02), `vip-tiers` (12), `offline-progress` (08).

### 11.17 Idle input model — `idle-input`

- **Category:** control scheme · passive with optional bursts (economy: `idle-generators`, `automation-managers` (04))
- **Player fantasy:** "My empire grows on its own — and a little attention makes it boom."
- **Core rules:**
  - *State:* passive rate per second; tap value; temporary boosts; automation unlocks; offline cap.
  - *Triggers:* taps (bursts), boost activation, app resume.
  - *Effects:* taps add value or multiply the rate briefly; automation removes the need to tap; resume grants capped offline earnings with a summary.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Active : idle earning ratio | 2–5× early, converging later | Rewards attention without punishing absence |
| Registered tap-rate cap | 10–15 taps/s | Blunts autoclickers and repetitive strain |
| Hold-to-auto-tap | available | Accessibility and comfort |
| Automation unlock | first 5–15 minutes | Removes tapping before it becomes a chore |
| Offline cap | 2–12 h, upgradable | Defines the check-in rhythm |

- **Dynamics:** check-in rhythm; optimisation of when to be active; numbers-go-up satisfaction.
- **Aesthetic targets (MDA):** Submission, Sensation (number pops).
- **Feedback and juice:** number pops scaled to value; coin fountains; light haptic ticks rate-limited.
- **Failure modes and exploits:** required rapid tapping (strain); autoclickers; overflowing numeric types (use a big-number representation); clock manipulation for offline gains.
- **Mobile fit:** portrait, zero to one hand; any session length.
- **Monetization hooks and the ethical limit:** rewarded ads that double offline earnings are standard (see `rewarded-double` (12)); never make tapping speed a paid advantage.
- **Implementation notes:** server-validated timestamps for offline earnings; tap events rate-limited in the sim.

```text
on_tap(t): if t - last_tap >= 1 / TAP_CAP_HZ: bank += tap_value(); last_tap = t
on_resume(now): away = min(now - last_seen, OFFLINE_CAP); show_summary(rate() * away * OFFLINE_EFF)
```
- **Reference games:** AdVenture Capitalist, Cookie Clicker, Egg, Inc., Tap Titans 2.
- **Combines well with:** `idle-accumulation` (08), `offline-progress` (08), `prestige-rebirth` (04).

## 8. Feedback, access and hardware

### 11.18 Haptic patterns as a feedback language — `haptic-language`

- **Category:** control scheme · tactile feedback and information channel
- **Player fantasy:** "I can feel the game — the click of a lock, the buzz of something close."
- **Core rules:**
  - *State:* a small vocabulary of semantic haptic events (selection tick, confirm, light / medium / heavy impact, success, warning, failure, proximity pulse); global toggle and intensity; device capability flags.
  - *Triggers:* game events mapped to vocabulary entries.
  - *Effects:* the haptic manager plays the pattern if enabled, supported and not rate-limited; as a mechanic, haptics carry information (warmer/colder pulses, lock detents, a fish biting, rhythm cues).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Tick duration | 10–20 ms | Crisp; longer buzzes feel cheap |
| Impact duration | 20–50 ms, three intensity levels | Weight hierarchy for hits and merges |
| Minimum gap / rate cap | 50–80 ms; ≤ 10–15 events/s | Prevents mushy continuous buzz |
| Proximity pulse interval | 1,000 ms far → 200 ms near | Turns haptics into a "warmer/colder" sense |
| Pattern length | ≤ 300 ms | Long patterns drain battery and annoy |

- **Dynamics:** reinforces timing and impact; enables eyes-free play moments (GPS walking, hidden objects).
- **Aesthetic targets (MDA):** Sensation, Discovery.
- **Feedback and juice:** haptics always paired with audio and visual cues, never alone.
- **Failure modes and exploits:** buzz spam; haptics as the only cue (excludes players with haptics off or unsupported devices); ignoring the system haptics setting; large variance across Android devices.
- **Mobile fit:** universal; a cheap, high-impact layer of game feel.
- **Monetization hooks and the ethical limit:** never use haptics to draw attention to offers or purchase buttons.
- **Implementation notes:** one manager with priority and rate limiting; map vocabulary entries to platform primitives (see platform notes below).

```text
play(evt): if not settings.haptics or not supported(evt): return
  if now - last_t < MIN_GAP_MS and PRIORITY[evt] <= last_priority: return
  platform_play(MAP[evt], intensity=settings.intensity * BASE[evt]); last_t, last_priority = now, PRIORITY[evt]
```
- **Reference games:** Pokémon GO (vibration on nearby encounters), 1-2-Switch (HD Rumble ball counting, as design inspiration).
- **Combines well with:** `tap-anywhere`, `board-manipulation`, `gps-location` (10), `input-accessibility`.

### 11.19 Accessibility alternatives — `input-accessibility`

- **Category:** control scheme · alternatives and assists
- **Player fantasy:** "The game adapts to my body, not the other way round."
- **Core rules:**
  - *State:* action layer (actions, not gestures) with multiple bindings each; assist settings.
  - *Triggers:* player enables an option; any gesture or binding.
  - *Effects:* every path or multi-finger gesture has a single-tap alternative (WCAG 2.2 criterion 2.5.1); actions commit on release with cancel possible (2.5.2); motion input has a UI alternative and can be disabled (2.5.4); hold actions can become toggles; timing windows widen; aim and fire can be automated; controls can be remapped, resized and moved; a one-switch scanning mode is possible for simple games.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Timing assist | windows ×1.5–2, or game speed 50–80 % | Opens timing games to more players |
| Hold → toggle | per action | Removes sustained-press strain |
| Target size scale | 100–150 % | Motor and vision support |
| Switch scan speed | 0.5–2 s per item | Single-switch play |
| Assist stigma | assists never lock achievements or content | Locked rewards push players away from assists |

- **Dynamics:** wider audience; longer play sessions without strain; some players use assists situationally (one hand on a bus).
- **Aesthetic targets (MDA):** Submission (comfort); preserves each game's own targets for more players.
- **Feedback and juice:** assists announced clearly; previews of what each option changes.
- **Failure modes and exploits:** options buried in menus; assists untested; engine-drawn UI invisible to VoiceOver and TalkBack (needs an accessibility bridge); assists that disable progress.
- **Mobile fit:** mandatory quality bar; also a store-listing and review advantage.
- **Monetization hooks and the ethical limit:** never sell accessibility features or put assists behind purchases.
- **Implementation notes:** route all input through an action map; test each assist in the deterministic playthrough suite. Summarised from the Game Accessibility Guidelines, the Xbox Accessibility Guidelines and WCAG 2.2 (sources below); see `accessibility-localization`.

```text
ACTIONS = {"jump": [Tap(zone="right"), Button("A"), Switch(1)], "aim": [Drag("aim_stick"), Gyro(), AutoAim()]}
resolve(evt) = first(action for action, binds in ACTIONS.items() if any(b.matches(evt, settings) for b in binds))
```
- **Reference games:** The Last of Us Part II (extensive accessibility options), Celeste (Assist Mode), Hades (God Mode).
- **Combines well with:** `hud-customization`, `board-manipulation`, `tilt-gyro-scheme`, `controller-support`.

### 11.20 Gamepad support — `controller-support`

- **Category:** control scheme · external controller
- **Player fantasy:** "Real buttons, same game, my phone as a handheld console."
- **Core rules:**
  - *State:* connected controllers; active input family (touch or pad); glyph set; menu focus.
  - *Triggers:* connect/disconnect; first input from a device family.
  - *Effects:* on pad input hide the touch HUD, show matching glyphs and enable focus navigation; on touch input restore the touch HUD; disconnect pauses the game.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Stick inner dead zone (radial) | 0.10–0.25 of full deflection | Worn sticks drift; too large feels numb |
| Outer dead zone | 0.90–0.95 | Lets players reach full speed reliably |
| Trigger threshold | 0.1–0.3 | Lower = hair trigger |
| Glyph families | Xbox, PlayStation, generic | Wrong glyphs confuse instantly |
| Menu focus | wraparound, remembered per screen | Menus must be fully usable without touch |

- **Dynamics:** longer, more precise sessions; access for players who struggle with touch.
- **Aesthetic targets (MDA):** Sensation, Challenge.
- **Feedback and juice:** controller rumble mapped from the haptic vocabulary; focus highlight with motion.
- **Failure modes and exploits:** UI stuck in pad mode after touching; menus without focus navigation; touch-only prompts; no pause on disconnect.
- **Mobile fit:** landscape, two hands; a premium-quality signal and an accessibility path.
- **Monetization hooks and the ethical limit:** none.
- **Implementation notes:** iOS exposes controllers through Apple's Game Controller framework (with an on-screen virtual controller option); Android reports gamepads as input devices with standard key codes and axes; Godot and Unity abstract both. Drive everything through the same action map as touch.

```text
on_input(evt): fam = family(evt.device)
  if fam != active: active = fam; hud.set_mode(fam); glyphs.use(glyph_set(evt.device))
stick(v) = 0 if len(v) < IN_DZ else normalize(v) * min((len(v) - IN_DZ) / (OUT_DZ - IN_DZ), 1)
```
- **Reference games:** Genshin Impact, Call of Duty: Mobile, Dead Cells, Stardew Valley, Minecraft.
- **Combines well with:** `input-accessibility`, `hud-customization`, `virtual-stick`.

## 9. Input QA checklist, platform API notes and related skills

- [ ] Every control ≥ 44 pt, inside the safe area, reachable per the `one-thumb-portrait` audit on the smallest and largest supported phones.
- [ ] Multi-touch: each control owns a pointer id; lifting one finger never cancels another control.
- [ ] Edge gestures: no game gesture starts in OS gesture zones; tested with gesture navigation on Android and the home indicator on iOS.
- [ ] Latency: actions fire on touch-down where timing matters; no frame-based smoothing on action input.
- [ ] Interruptions: a call, notification shade or app switch releases all held inputs and pauses (`interruption-safe` (08)).
- [ ] Alternatives: tap alternatives for gestures, motion input optional, hold-to-toggle, remapping, controller navigation.
- [ ] Deterministic playthroughs inject actions (not raw touches) and also replay recorded touch streams for recogniser tests (`qa-testing`).

**Platform API notes (as of Oct 2026 — verify against current SDK docs):**
- iOS haptics: `UIImpactFeedbackGenerator` (light, medium, heavy, soft, rigid), `UISelectionFeedbackGenerator`, `UINotificationFeedbackGenerator`, and Core Haptics for custom patterns — [Core Haptics](https://developer.apple.com/documentation/corehaptics).
- Android haptics: `View.performHapticFeedback` with `HapticFeedbackConstants`; `VibrationEffect` predefined effects (e.g., `EFFECT_TICK`, `EFFECT_CLICK`, `EFFECT_HEAVY_CLICK`) and composition primitives on API 30+, with support checks — [VibrationEffect](https://developer.android.com/reference/android/os/VibrationEffect).
- Godot: `Input.vibrate_handheld()` (check your version's signature for amplitude support) — [Godot Input class](https://docs.godotengine.org/en/stable/classes/class_input.html). Unity: `Handheld.Vibrate()` is on/off only; use a native plugin for patterns — [Unity scripting reference](https://docs.unity3d.com/ScriptReference/Handheld.Vibrate.html).
- Edge gestures: Android `View.setSystemGestureExclusionRects` (the system honours at most 200 dp of exclusion per vertical edge) — [View reference](https://developer.android.com/reference/android/view/View); iOS `preferredScreenEdgesDeferringSystemGestures` — [UIViewController reference](https://developer.apple.com/documentation/uikit/uiviewcontroller/preferredscreenedgesdeferringsystemgestures).
- Controllers: [Apple Game Controller framework](https://developer.apple.com/documentation/gamecontroller) (including `GCVirtualController`); Android gamepads via `InputDevice` sources and `KeyEvent`/`MotionEvent` axes.
- Accessibility references: [WCAG 2.2](https://www.w3.org/TR/WCAG22/), [Game Accessibility Guidelines](https://gameaccessibilityguidelines.com/), [Xbox Accessibility Guidelines](https://learn.microsoft.com/en-us/gaming/accessibility/guidelines).

**Related skills:** `game-feel` (juice, timing, feedback), `mobile-ux` (layout, safe areas, thumb zones), `accessibility-localization` (assists, remapping), `gameplay-programming` (input layers, determinism), `qa-testing` (input injection), `mobile-performance` (sensor and haptic battery cost).
