# 01 — Input Verbs, Movement and Physics Mechanics

Verbs are the atoms of a game: the thing the player physically does with their thumb, and the immediate change it causes in the simulation. This file catalogues the touch verbs (tap, swipe, slice, drag, hold-release, tilt, pinch) and the movement and physics mechanics built on them (jump, dash, slide, grapple, slingshot, auto-run lanes, one-tap impulse, gravity flip, stacking, ragdoll, momentum, vehicles, trajectories, flick, draw-a-path, rhythm timing). Every entry gives precise rules, tuning ranges you can start from, what the mechanic does to feel and difficulty, how it breaks, and how to implement it deterministically. The numeric ranges are practitioner starting points, not laws: set them in data, expose them to a tuning panel, and confirm them with playtests and bots. For full control-scheme layouts (virtual sticks, button maps, accessibility remaps) read `references/11-mobile-input-control-schemes.md`; for the moment-to-moment polish layer read the `game-feel` skill.

## Contents

1. Conventions used in this file
2. Index of mechanics
3. Input verbs (entries 1–7)
4. Character movement (entries 8–14)
5. Physics-driven mechanics (entries 15–23)
6. Cross-cutting implementation rules

## 1. Conventions used in this file

- **Units.** Time in milliseconds (ms) or seconds (s). Screen distances in density-independent units: `dp` (Android) ≈ `pt` (iOS); 1 mm ≈ 6.3 dp. World distances in world units (`wu`); assume 1 wu ≈ half the player character's height unless stated.
- **Frames.** "Frame" means a 60 Hz frame (16.7 ms) unless stated. Simulation runs on a fixed step (60 Hz or 120 Hz) independent of render rate so that tuning values and replays are stable.
- **IDs.** Each mechanic has a kebab-case `id` for use in mechanic cards (`mechanic-card.schema.json` field `id`) and in `combos` lists.
- **OS reference points.** Android framework defaults are roughly 8 dp touch slop and a ~300 ms double-tap timeout; long-press defaults sit around 400–500 ms depending on OS version. Minimum comfortable touch targets are 44×44 pt (Apple HIG) and 48×48 dp (Material). Treat these as floors, not targets.

## 2. Index of mechanics

| # | Mechanic | ID | Category | One-line essence | Typical home genres |
|---|---|---|---|---|---|
| 1 | Tap | `tap` | input verb | Discrete touch → instant action | clicker, hyper-casual, rhythm, UI-driven puzzle |
| 2 | Directional swipe | `directional-swipe` | input verb | Quantized flick direction → command | runner, 2048-likes, card swipe |
| 3 | Slice (swipe-through) | `slice` | input verb | Touch path cuts what it crosses | arcade, physics puzzle |
| 4 | Drag (direct manipulation) | `drag` | input verb | Object follows finger, drops to slot | block puzzle, merge, sort, solitaire |
| 5 | Hold-release (charge) | `hold-release` | input verb | Press accumulates value, release spends it | hyper-casual timing, golf, archery |
| 6 | Tilt | `tilt` | input verb | Device orientation steers | endless climber, ball-rolling |
| 7 | Pinch and two-finger rotate | `pinch-rotate` | input verb | Two-finger scale/rotate as a rule | fitting puzzles, camera |
| 8 | Jump (variable height) | `jump` | movement | Ballistic hop with forgiveness windows | platformer, runner |
| 9 | Dash | `dash` | movement | Short burst, often invulnerable | action, roguelite |
| 10 | Slide and fast-fall | `slide` | movement | Lowered hitbox for a fixed window | runner, platformer |
| 11 | Grapple and swing | `grapple-swing` | movement | Rope constraint converts gravity to speed | swing arcade, platformer |
| 12 | Auto-run lane switching | `auto-run-lanes` | movement | Constant forward motion, discrete lanes | endless runner |
| 13 | One-tap impulse (flap/hop) | `one-tap-impulse` | movement | Each tap sets vertical speed | hyper-casual arcade |
| 14 | Gravity flip | `gravity-flip` | movement | Tap inverts gravity | arcade runner, puzzle-platformer |
| 15 | Slingshot aim-release | `slingshot-aim-release` | physics | Pull back, see arc, release | physics destruction, golf |
| 16 | Trajectory and ballistics | `trajectory-ballistics` | physics | Aim angle + power, bounce and wind | artillery, peg/brick breakers |
| 17 | Flick | `flick` | physics | Release velocity becomes launch velocity | toss, sports, catch games |
| 18 | Physics stacking and timed drop | `physics-stacking` | physics | Drop moving piece; overlap or balance decides | hyper-casual tower, merge-drop |
| 19 | Ragdoll | `ragdoll` | physics | Limp articulated body as payoff or puzzle | dismount, brawler, comedy |
| 20 | Momentum and slopes | `momentum-slopes` | physics | Convert height to speed with timed presses | slope runner, skiing |
| 21 | Physics vehicle (gas/brake) | `physics-vehicle` | physics | Two pedals, suspension, air rotation | hill climb, trials |
| 22 | Draw-a-path | `draw-a-path` | physics/input | The drawn line becomes route or object | traffic control, draw-physics |
| 23 | Rhythm-timed input | `rhythm-timing` | input timing | Inputs judged against the beat clock | rhythm, music runner |

## 3. Input verbs

### 01.01 Tap — `tap`

- **ID:** `tap` · **Category:** input verb (discrete) · **Player fantasy:** "I touch it and it happens, instantly."
- **Core rules:**
  - State per pointer: `{id, down_t, down_pos, moved}`. On `down`, record; on `move`, set `moved = true` once displacement > slop.
  - Trigger: `up` within `max_tap_ms` and not `moved` → emit `tap(pos)`. For action games emit on `down` instead (saves 50–150 ms of perceived latency); for UI and destructive choices emit on `up` so the player can slide off to cancel.
  - Effect: hit-test `pos` against targets using an expanded hit radius; resolve ties by nearest centre, then by priority (gameplay object > background).
  - Multi-tap: a second tap within `double_tap_ms` and `double_tap_radius` becomes `double_tap` (delays single-tap resolution if both are bound — avoid binding both in action contexts).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Fire on down vs up | down for action, up for UI | Down feels snappier; up allows cancel |
| `max_tap_ms` | 150–300 ms | Shorter separates tap from hold; too short drops slow taps |
| Touch slop | 8–16 dp | Larger forgives shaky thumbs; too large eats intended drags |
| Hit radius expansion | +20–50 % or ≥ 44 pt | Main lever against "fat finger" misses |
| Input buffer | 80–150 ms | Queues a tap that arrived just before it was legal |
| Rate cap | 8–15 taps/s | Prevents auto-clicker and multi-finger abuse |

- **Dynamics:** rhythm and cadence; in clickers, tapping speed as early-game power that hands off to idle income; in timing games, anticipation.
- **Aesthetics (MDA):** Challenge (timing), Sensation, Submission (clicker trance).
- **Feedback and juice:** respond on the same frame — scale punch 1.1–1.2× over 80–120 ms, light haptic, short sound with ±5–10 % random pitch, contact particle. Delay of more than ~100 ms between touch and visible response reads as lag.
- **Failure modes and exploits:** tiny targets; taps near OS gesture edges (iOS home indicator, Android back-gesture edges); auto-clickers (detect inter-tap variance below ~5 ms over 50+ taps, or cap rate); multi-finger drumming beating intended pace (count simultaneous pointers).
- **Mobile fit:** the most one-hand-friendly verb; keep tap targets in the lower 60 % of a portrait screen.
- **Monetization hooks and ethical limit:** tap multipliers and auto-tappers in idle games are fine as conveniences. Do not design deliberate tapping fatigue as the pain point a purchase removes.
- **Implementation notes:** keep a per-pointer dictionary; never use "mouse emulation" on mobile, as it collapses multitouch.

```text
on_down(p): ptr[p.id] = {t: now, pos: p.pos, moved: false}; if FIRE_ON_DOWN: emit_tap(p.pos)
on_move(p): if dist(p.pos, ptr[p.id].pos) > SLOP: ptr[p.id].moved = true
on_up(p):   s = ptr.pop(p.id); if !FIRE_ON_DOWN and !s.moved and now - s.t <= MAX_TAP_MS: emit_tap(s.pos)
```

- **Reference games:** Flappy Bird, Piano Tiles, Stack, Cookie Clicker, Tap Titans 2.
- **Combines well with:** `one-tap-impulse`, `hold-release`, `rhythm-timing`, `physics-stacking`, idle generators (`references/04-economy-resource-mechanics.md`).

### 01.02 Directional swipe — `directional-swipe`

- **ID:** `directional-swipe` · **Category:** input verb (gesture) · **Player fantasy:** "My flick is a command — dodge left, now."
- **Core rules:**
  - Track displacement `d = pos - down_pos` and elapsed time while the pointer is down.
  - Trigger: as soon as `|d| >= min_dist` (do not wait for lift; lift-triggered swipes feel 100–200 ms late), with `elapsed <= max_ms`.
  - Direction: `angle = atan2(d.y, d.x)`; quantize to N sectors (4 for runners, 8 for twin-axis puzzles). Apply axis bias: widen the horizontal sectors when lane switching matters most.
  - One command per swipe; re-arm only after lift or after a sharp reversal (allows "left-then-right" chains without lifting).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| `min_dist` | 20–60 dp (3–9 mm) | Lower is twitchier; higher reduces false swipes from taps |
| `max_ms` | 250–500 ms | Rejects slow drags that should scroll or aim |
| Sector count | 4 or 8 | 8 adds expressiveness and diagonal errors |
| Axis bias | 0–15° wider for favoured axis | Reduces up/down misreads in lane games |
| Re-arm on reversal | on/off, ≥ 90° turn | Enables fast chains; risk of double triggers |

- **Dynamics:** split-second reading of patterns; players develop "pre-swipes" (buffered intent), so buffer 1 command for 100–150 ms.
- **Aesthetics (MDA):** Challenge, Sensation.
- **Feedback and juice:** directional squash on the character, whoosh sound panned toward the direction, short trail; on a rejected swipe show nothing (do not punish).
- **Failure modes and exploits:** diagonal ambiguity (log misclassified swipes in playtests); conflict with system edge gestures — start zones within ~20 dp of the left/right edges trigger Android back, bottom edge triggers iOS home; swipe on a scrolling list.
- **Mobile fit:** excellent one-handed in portrait; works anywhere on screen (no fixed button), which is why runners use it.
- **Monetization hooks and ethical limit:** none intrinsic; revives after a missed swipe are common — cap them per run and never shrink buffers to drive revive sales.
- **Implementation notes:** sector index = `round(angle / (2π / N)) mod N` with bias applied by remapping angle before rounding. Unit-test the classifier with recorded human swipe traces, not synthetic straight lines.
- **Reference games:** Subway Surfers, Temple Run 2, 2048, Threes!, Tinder-style card choices in Reigns.
- **Combines well with:** `auto-run-lanes`, `jump`, `slide`, `dash`, sliding-tile and 2048-style merges (`references/03-puzzle-mechanics.md`).

### 01.03 Slice (swipe-through) — `slice`

- **ID:** `slice` · **Category:** input verb (path gesture) · **Player fantasy:** "I am a blade — everything my finger crosses is cut."
- **Core rules:**
  - The touch path is sampled each frame into segments `(p_prev, p_now)`. A segment is "sharp" only if its speed ≥ `min_blade_speed`.
  - Trigger: a sharp segment intersects a sliceable collider → `slice(object, entry, exit)`; the object splits along the chord.
  - Combo: N objects sliced within one continuous stroke (or within `combo_window`) → bonus. Hazards (bombs) end the run or cost a life when sliced.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| `min_blade_speed` | 300–1,000 dp/s | Higher prevents "slow drag" slicing; too high misses gentle players |
| Blade width (hit radius) | 8–24 dp | Wider forgives; reduces precision skill |
| Trail lifetime | 100–250 ms | Longer trails look powerful; must match hit logic |
| Combo window | 150–300 ms or one stroke | Shorter rewards fluid strokes |
| Hazard density | 0–20 % of spawns | Main lever for tension and risk |

- **Dynamics:** sweeping strokes that maximise multi-hits; risk assessment when hazards share space with targets.
- **Aesthetics (MDA):** Sensation (strong), Challenge.
- **Feedback and juice:** split halves inherit velocity plus outward impulse, juice splatter decal, 30–60 ms hit-stop on big combos, ascending pitch per combo step.
- **Failure modes and exploits:** tunnelling at high finger speed if you test only the current touch point (always test segments); scribbling to cover the screen (counter with hazards or stroke-length limits).
- **Mobile fit:** one-hand fine; sessions of 60–90 s suit it.
- **Monetization hooks and ethical limit:** cosmetic blades and trails are the honest hook; avoid stat-boosting blades in a skill game.
- **Implementation notes:** segment-vs-circle test per object per frame; split meshes or swap to pre-cut sprite halves (cheaper on low-end). Cap simultaneous debris pieces (e.g., 40) and recycle via pools.
- **Reference games:** Fruit Ninja, Cut the Rope (rope cutting), Slice It All!.
- **Combines well with:** `physics-stacking`, `trajectory-ballistics` (thrown targets), `rhythm-timing` (slice on beat).

### 01.04 Drag (direct manipulation) — `drag`

- **ID:** `drag` · **Category:** input verb (continuous) · **Player fantasy:** "I pick it up and put it exactly where I want."
- **Core rules:**
  - Grab: on `down`, hit-test pickable objects (expanded radius); grab only after slop is exceeded or after 60–100 ms hold, to keep taps distinct.
  - Follow: object position = finger + `lift_offset` (shift the object above the finger so the thumb does not hide it) with optional smoothing.
  - Drop: on `up`, find the nearest valid slot within `snap_radius`; if valid, commit; else animate back to origin. Lock the drag to the first pointer.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Lift offset | 40–100 dp upward | Keeps piece visible; too much feels detached |
| Follow smoothing | 0 (raw) to 0.5 lerp/frame | Smoothing looks polished but adds latency; keep < 50 ms |
| Snap radius | 0.4–0.6 of a cell | Larger forgives imprecise drops |
| Ghost preview | on/off | Showing the landing cell removes most mis-drops |
| Return animation | 120–250 ms | Fast enough not to stall flow |
| Drop scale-up | 1.0 → 1.15× while held | Signals "held" state clearly |

- **Dynamics:** planning before committing; in block-placement games, the drag is free and the drop is the decision.
- **Aesthetics (MDA):** Expression (arranging), Challenge (spatial), Submission (tidy sorting).
- **Feedback and juice:** pick-up pop and soft haptic, ghost silhouette on valid cells, green/red tint, satisfying "clack" on drop, settle bounce.
- **Failure modes and exploits:** finger occlusion; accidental drops when the thumb slips; dragging under a HUD; multi-touch to drag two pieces at once (lock to one pointer); drag conflicting with board pan (use a dead zone or two-finger pan).
- **Mobile fit:** one-hand friendly when the board fits in the thumb arc; works in portrait.
- **Monetization hooks and ethical limit:** "undo last drop" as a booster is acceptable; ambiguous drop zones that cause mistakes and then sell undos are a dark pattern.
- **Implementation notes:** store the drag as `{piece_id, origin, grab_offset, pointer_id}`. Compute the target cell from the piece's anchor, not the finger, so the ghost and the result agree.
- **Reference games:** Block Blast!, 1010!, Merge Mansion, Solitaire (Microsoft Solitaire Collection), Woodoku.
- **Combines well with:** block placement, merge, sort (`references/03-puzzle-mechanics.md`), `physics-stacking`, crafting grids.

### 01.05 Hold-release (charge) — `hold-release`

- **ID:** `hold-release` · **Category:** input verb (analog over time) · **Player fantasy:** "I build power and choose the perfect moment to let go."
- **Core rules:**
  - Variants: **hold-to-thrust** (continuous force while held), **hold-to-charge** (value accumulates, spent on release), **hold-to-grow** (length or size grows, release commits).
  - State: `charging`, `t_held`. Value = curve(`t_held / T_full`). Release → action with that value. Optional overcharge: past full, value decays, oscillates, or fails.
  - Cancel: dragging off the zone (or a second finger) cancels without spending.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| `T_full` (time to full) | 0.5–1.5 s | Shorter is twitchier; longer adds tension and slows pace |
| Curve | linear, ease-out, ping-pong | Ping-pong (oscillating meter) creates a timing skill test |
| Perfect window | ±40–100 ms or ±3–8 % of meter | Primary difficulty lever |
| Overcharge rule | clamp / decay / fail | Fail adds risk; clamp is friendliest |
| Thrust acceleration (thrust variant) | 1.2–2.5 × gravity | Feel of weight vs floatiness |

- **Dynamics:** anticipation, risk-reward (hold longer for more, risk overcharge); in thrust variants, constant micro-correction.
- **Aesthetics (MDA):** Challenge, Sensation.
- **Feedback and juice:** rising pitch and vibration intensity with charge, meter fill with a "perfect" band, a release snap; telegraph overcharge with flashing.
- **Failure modes and exploits:** invisible charge state (always show a meter or a growing object); OS long-press menus or text selection on web builds; players holding forever when overcharge is clamped (make waiting cost something).
- **Mobile fit:** one-hand perfect; one verb can carry an entire hyper-casual game.
- **Monetization hooks and ethical limit:** "aim guide" or "power guide" boosters are acceptable if the base game remains fair without them.
- **Implementation notes:** linear `v = clamp(t/T, 0, 1)`; ease-out `v = 1 - (1 - t/T)^2`; ping-pong `v = 1 - |((t/T) mod 2) - 1|`. Use simulation time, not wall clock, so pauses and replays are exact.
- **Reference games:** Stick Hero (hold-to-grow), Jetpack Joyride (hold-to-thrust), Golf Clash (power and accuracy timing), Angry Birds-style power meters in archery games.
- **Combines well with:** `jump` (charge jump), `slingshot-aim-release`, `trajectory-ballistics`, `momentum-slopes` (hold to dive).

### 01.06 Tilt — `tilt`

- **ID:** `tilt` · **Category:** input verb (sensor) · **Player fantasy:** "The world tips with my hands — I'm steering the whole thing."
- **Core rules:**
  - Read the gravity vector (accelerometer, low-pass filtered) or the device attitude. Calibrate neutral orientation at level start (and on a "recentre" button).
  - Map tilt angle θ (relative to neutral) through a dead zone and response curve to either velocity (most common) or position.
  - Clamp to `θ_max`; beyond it, output is 1.0.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Dead zone | 2–5° | Stops drift from hand tremor |
| `θ_max` (full output) | 20–35° | Smaller is twitchy; larger tires wrists and hides the screen |
| Low-pass α | 0.1–0.3 per sample | More smoothing = more lag |
| Response exponent | 1.0–2.0 | >1 gives fine control near centre |
| Sensitivity (player setting) | 0.5–2.0× | Accessibility and preference |

- **Dynamics:** whole-body engagement; steering with momentum; hard to do precise stops (so design for flowing motion, not pixel precision).
- **Aesthetics (MDA):** Sensation, Fantasy (physical embodiment), Challenge.
- **Feedback and juice:** world or camera lean (2–5°) to echo the tilt, rolling sound tied to speed.
- **Failure modes and exploits:** unplayable lying down or on transport; screen-orientation auto-rotation fighting the input (lock orientation); motion sickness; accessibility — always provide a touch alternative.
- **Mobile fit:** two hands usually; short sessions; poor for commuting.
- **Monetization hooks and ethical limit:** none intrinsic.
- **Implementation notes:** `out = sign(θ) * ((max(|θ| - dz, 0)) / (θmax - dz))^k`, clamped to [-1, 1]. Record sensor traces for deterministic replays; feed recorded traces to the playtest runner.
- **Reference games:** Doodle Jump, Tilt to Live, Asphalt series (tilt steering option), Super Monkey Ball mobile editions.
- **Combines well with:** `momentum-slopes`, `jump` (auto-jump platforms), ball-rolling physics puzzles.

### 01.07 Pinch and two-finger rotate — `pinch-rotate`

- **ID:** `pinch-rotate` · **Category:** input verb (two-finger) · **Player fantasy:** "I can resize and turn things with my hands, like a real object."
- **Core rules:**
  - Two pointers active. `scale = |p1 - p2| / |p1_0 - p2_0|`; `rotation = angle(p1 - p2) - angle(p1_0 - p2_0)`; pivot = centroid.
  - As a mechanic (not just camera): object scale or rotation is part of the puzzle state, committed on release, with snapping.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Rotation snap | free / 15° / 45° / 90° | Snapping turns an analog skill into a discrete puzzle |
| Scale clamp | 0.5–2.0× | Prevents degenerate states |
| Smoothing | 0–0.3 lerp/frame | Hides jitter, adds latency |
| One-finger fallback | tap-to-rotate 90° | Needed for one-hand play and accessibility |

- **Dynamics:** fitting and alignment problems; inspection of 3D objects.
- **Aesthetics (MDA):** Discovery, Expression.
- **Feedback and juice:** snap detents with tick sound and haptic per detent; outline glow when an orientation fits.
- **Failure modes and exploits:** requires two hands — never make it the only way to progress; conflicts with camera pinch (separate modes clearly).
- **Mobile fit:** two-handed; acceptable for slow puzzles, poor for action.
- **Monetization hooks and ethical limit:** none intrinsic.
- **Implementation notes:** recompute from the initial two-pointer snapshot every frame (not incrementally) to avoid drift; when one pointer lifts, end the gesture and commit.

```text
on_two_down(a, b): s0 = {d: dist(a,b), ang: angle(b-a), obj_scale: obj.scale, obj_rot: obj.rot}
on_move(a, b):     obj.scale = clamp(s0.obj_scale * dist(a,b)/s0.d, MIN, MAX)
                   obj.rot   = s0.obj_rot + (angle(b-a) - s0.ang)
on_lift():         obj.rot = round(obj.rot / SNAP) * SNAP; commit(obj)
```
- **Reference games:** Monument Valley (rotating structures, one-finger), The Room series (object manipulation), camera control in Clash of Clans.
- **Combines well with:** rotation and packing puzzles (`references/03-puzzle-mechanics.md`), hidden-object inspection.

## 4. Character movement

### 01.08 Jump (variable height) — `jump`

- **ID:** `jump` · **Category:** movement · **Player fantasy:** "I'm light, precise and in control mid-air."
- **Core rules:**
  - Grounded check each step. Jump allowed if grounded or within `coyote_time` after leaving ground, and if a jump input occurred within `jump_buffer` before landing.
  - Impulse: `vy = v0`. Variable height: if the button is released while `vy > 0`, set `vy *= cut_factor` (or switch to higher gravity).
  - Gravity: `g_up` while rising and held; `g_fall = g_up * fall_mult` while falling; reduced gravity near apex (`|vy| < apex_threshold`) for hang time; clamp to `v_terminal`.
  - Derive from design targets: for apex height `h` and time-to-apex `t_a`: `g = 2h / t_a²`, `v0 = 2h / t_a`.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Apex height | 2–4 character heights | Defines level metrics (gaps, ledges) |
| Time to apex | 0.30–0.45 s | Shorter = snappy, longer = floaty |
| Fall multiplier | 1.5–2.5× | Higher removes floatiness; key for "weight" |
| Release cut factor | 0.4–0.6 | Lower = more height control |
| Coyote time | 80–150 ms | Forgives late jumps off ledges |
| Jump buffer | 100–150 ms | Forgives early presses before landing |
| Air control | 50–100 % of ground accel | Low = committed arcs; high = forgiving |

- **Dynamics:** spacing and timing over gaps; in runners with one-button jumps, pattern reading at speed.
- **Aesthetics (MDA):** Challenge, Sensation.
- **Feedback and juice:** squash on takeoff (0.8 × 1.2), stretch in air, land squash + dust puff, landing sound scaled by fall speed, camera vertical dead zone to avoid bobbing.
- **Failure modes and exploits:** missing coyote/buffer windows feels like "dropped inputs"; variable height on a touch screen is hard to read (consider hold duration on tap jump, or two jump buttons); ceiling bonk with no corner correction (nudge 2–4 px around corners).
- **Mobile fit:** single tap or whole-screen tap for runners; precision platforming with virtual buttons is weak on glass — prefer auto-run designs.
- **Monetization hooks and ethical limit:** double-jump as a power-up is fine in premium unlock trees; do not tune base jumps worse to sell power-ups.
- **Implementation notes:**

```text
step(dt):
  coyote = grounded ? COYOTE : max(coyote - dt, 0)
  buffer = pressed_this_step ? BUFFER : max(buffer - dt, 0)
  if buffer > 0 and coyote > 0: vy = V0; buffer = 0; coyote = 0
  if released_this_step and vy > 0: vy *= CUT
  g = vy > 0 ? G_UP : G_UP * FALL_MULT
  if abs(vy) < APEX_T: g *= APEX_G_MULT
  vy = max(vy - g*dt, -V_TERM); y += vy*dt
```

- **Reference games:** Super Mario Run, Geometry Dash, Rayman Jungle Run, Leo's Fortune.
- **Combines well with:** `auto-run-lanes`, `dash`, `gravity-flip`, `hold-release` (charged jump), `slide`.

### 01.09 Dash — `dash`

- **ID:** `dash` · **Category:** movement · **Player fantasy:** "I'm faster than danger — I blink through it."
- **Core rules:**
  - Trigger: dash input (swipe, button, or double-tap direction) while `charges > 0` and not in end-lag.
  - Effect: set velocity to `dir * v_dash` for `t_dash` (distance `d = v_dash * t_dash`), optionally ignoring gravity and friction; optional invulnerability for the first `i_frac` of the dash; then `end_lag` during which only movement is allowed.
  - Resource: `charges` (1–3) recharging every `t_recharge`, or a simple cooldown.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Distance | 2–5 character widths | Longer escapes more, trivialises threats if too long |
| Duration | 0.10–0.25 s | Shorter = "blink", longer = readable lunge |
| Charges / cooldown | 1–3 charges, 0.5–3 s recharge | Main lever for how central dashing is |
| I-frame fraction | 0–80 % of duration | 0 = positioning tool; high = dodge tool |
| End lag | 0–150 ms | Punishes spam |
| Direction source | input / facing / toward target | Toward-target makes it an attack-close tool |

- **Dynamics:** threat reading and spacing; dash-cancel tricks (if attacks can be cancelled into dashes, expect combo routes).
- **Aesthetics (MDA):** Challenge, Sensation, Fantasy (agility).
- **Feedback and juice:** afterimages or streak, FOV/zoom kick of 2–5 %, whoosh, brief chromatic or blur on low-cost devices only if the GPU budget allows; charge pips on the HUD.
- **Failure modes and exploits:** dash through walls (sweep-test the whole path with a shape cast); infinite dashing with fast recharge; dash used to skip content or out-of-bounds.
- **Mobile fit:** swipe-to-dash works anywhere; a dedicated button in the right-thumb zone for action games.
- **Monetization hooks and ethical limit:** extra charges as roguelite upgrades are healthy; selling permanent extra charges in PvP is pay-to-win.
- **Implementation notes:** kinematic sweep (`shape_cast(from, to)`) each step; resolve to the hit point minus skin width. Keep dash in the deterministic sim, never in the animation layer.
- **Reference games:** Dead Cells (mobile), Hades (mobile via Netflix Games), Soul Knight, Brawl Stars (dash-based brawlers).
- **Combines well with:** `jump`, i-frames and dodge (`references/02-combat-action.md`), bullet patterns, `grapple-swing`.

### 01.10 Slide and fast-fall — `slide`

- **ID:** `slide` · **Category:** movement · **Player fantasy:** "I duck under danger at full speed."
- **Core rules:**
  - Trigger: swipe down (runner) or crouch button while grounded → `sliding` for `t_slide` with hitbox height reduced to `h_frac`.
  - Mid-air swipe down → fast-fall: set `vy = -v_fast` and, on landing, optionally auto-slide.
  - Cancels: jump cancels slide immediately; obstacles above prevent standing up (extend slide until clear).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Slide duration | 0.5–1.0 s | Longer forgives early input, constrains next action |
| Hitbox height while sliding | 40–60 % | Smaller is more forgiving under bars |
| Fast-fall speed | 1.5–3× normal fall | Enables air-to-slide recovery |
| Jump-cancel window | anytime / after 100 ms | Anytime is friendlier and more expressive |

- **Dynamics:** with jump, creates a binary high/low read; with lanes, a three-way decision space per obstacle row.
- **Aesthetics (MDA):** Challenge, Sensation.
- **Feedback and juice:** body tilt, sparks or dust trail, low "shhh" loop, camera dips 3–6 %.
- **Failure modes and exploits:** standing up into an obstacle (auto-extend); slide-spam staying permanently under all hazards (add ground hazards that require jumping).
- **Mobile fit:** swipe down is natural one-handed.
- **Monetization hooks and ethical limit:** none intrinsic.
- **Implementation notes:** separate the collision shape state from the animation; use an overhead raycast before restoring full height.

```text
start_slide(): state = SLIDING; t = T_SLIDE; hitbox.h = H_FULL * H_FRAC
step(dt): if state == SLIDING: t -= dt
  if t <= 0 and !raycast_up(H_FULL): state = RUNNING; hitbox.h = H_FULL   # else keep sliding
on_jump(): if state == SLIDING: state = RUNNING; hitbox.h = H_FULL; jump()
```
- **Reference games:** Subway Surfers (roll), Temple Run 2 (slide), Minion Rush.
- **Combines well with:** `auto-run-lanes`, `jump`, `momentum-slopes`.

### 01.11 Grapple and swing — `grapple-swing`

- **ID:** `grapple-swing` · **Category:** movement (constraint physics) · **Player fantasy:** "I fling myself through the air with perfect timing."
- **Core rules:**
  - Attach: on press, connect to the nearest valid anchor within `attach_radius` (auto-target) or to the tapped anchor; rope length `L` = current distance (or fixed).
  - While attached: distance constraint keeps the player on a circle of radius `L`; gravity drives a pendulum (period `T = 2π√(L/g)`).
  - Release: on lift, keep velocity (optionally scaled by `release_boost`) and fly ballistically. Optional reel-in shortens `L` over time.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Attach radius | 4–10 wu | Larger is forgiving, removes route choice |
| Auto-target cone | 60–120° ahead | Narrow cones demand aim; wide cones read player intent |
| Rope length | fixed or current distance | Fixed is predictable; current is expressive |
| Release boost | 1.0–1.3× | Rewards releasing at the swing bottom/forward |
| Reel speed | 0–5 wu/s | Adds vertical control |
| Air drag | 0–0.05 per step | Prevents runaway speed |

- **Dynamics:** pumping energy by release timing; route choice between anchors; flow chains.
- **Aesthetics (MDA):** Sensation (speed), Challenge, Fantasy.
- **Feedback and juice:** rope tension stretch, whoosh rising with speed, speed lines, camera lookahead in the velocity direction.
- **Failure modes and exploits:** constraint jitter at low frame rates (fixed timestep + several solver iterations); infinite energy gain from boost (cap speed); anchors behind walls (line-of-sight check).
- **Mobile fit:** hold-to-attach, release-to-fly is ideal one-handed.
- **Monetization hooks and ethical limit:** skins and rope trails; avoid paid "magnet" boosters that make levels auto-complete.
- **Implementation notes:** Verlet integration with a distance constraint is simple and stable; or analytic pendulum (angle θ, ω += -(g/L) sin θ dt).

```text
attach(anchor): L = dist(pos, anchor)
step(dt): vel += g*dt; pos += vel*dt
  d = pos - anchor; if |d| > L: pos = anchor + d.normalized()*L; vel -= project(vel, d.normalized())
release(): vel *= RELEASE_BOOST
```

- **Reference games:** Stickman Hook, Cut the Rope (rope physics), Worms (ninja rope).
- **Combines well with:** `momentum-slopes`, `jump`, `dash`, `one-tap-impulse`.

### 01.12 Auto-run lane switching — `auto-run-lanes`

- **ID:** `auto-run-lanes` · **Category:** movement (constrained) · **Player fantasy:** "I'm sprinting flat out and dodging everything by instinct."
- **Core rules:**
  - Forward speed `v(t) = min(v0 + a·t, v_max)` (or stepped every N metres). N discrete lanes (3 is the genre default).
  - Swipe left/right → move one lane, lerping over `t_switch`; swipe up → `jump`; swipe down → `slide`.
  - Obstacles per lane: low (jump), high (slide), full block (switch lane), moving (trains). Hit rules: frontal collision = crash; side clip = stumble (slow + chaser closes in).
  - World built from authored chunks tagged by difficulty and required verbs, assembled procedurally.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Lanes | 3 (2–5) | 3 gives left/centre/right with an always-adjacent escape |
| Start → max speed | 1.0× → 1.8–2.5× over 3–6 min | Session length and death rate |
| Lane switch time | 0.10–0.20 s | Too slow feels sluggish; too fast is hard to read |
| Obstacle spacing | ≥ reaction distance: `v × (0.6–1.2 s)` | Minimum fairness constraint |
| Chunk difficulty ramp | tier up every 300–800 m | Controls flow vs spikes |
| Coin line density | 30–60 % of lanes | Steers players into risk (coins as lure) |

- **Dynamics:** pattern recognition at increasing speed; risk-taking for coins and power-ups; "one more run".
- **Aesthetics (MDA):** Sensation, Challenge, Submission (flow).
- **Feedback and juice:** camera FOV widens with speed, lane-switch lean, coin pickup pitch ladder, near-miss whoosh.
- **Failure modes and exploits:** unavoidable patterns (validate each chunk: from every reachable lane state there is ≥ 1 legal path given `t_switch` and reaction time); speed ramp outpacing human reaction (cap at the speed where bot-with-human-delay survives ≥ X s).
- **Mobile fit:** the canonical one-hand portrait design; runs of 1–3 min.
- **Monetization hooks and ethical limit:** revives (cap per run, escalating price), head-starts, score multipliers, character skins. Never alter obstacle generation to force deaths near a revive offer.
- **Implementation notes:** chunk library entries: `{id, length_m, tier, lanes[3][rows], verbs_required, coins}`. Validator: BFS over (row, lane, posture) states with transition time costs.
- **Reference games:** Subway Surfers, Temple Run 2, Minion Rush.
- **Combines well with:** `jump`, `slide`, `directional-swipe`, crowd gates (`references/02-combat-action.md`), missions and collection (`references/05-progression-meta-mechanics.md`).

### 01.13 One-tap impulse (flap / hop) — `one-tap-impulse`

- **ID:** `one-tap-impulse` · **Category:** movement (single verb) · **Player fantasy:** "One button, perfect rhythm — I'm threading the needle."
- **Core rules:**
  - Each tap sets `vy = v_flap` (set, not add — makes taps predictable regardless of current fall speed). Constant gravity; horizontal auto-scroll at speed `vx`.
  - Obstacles with gaps; collision = death (pure version) or damage.
  - Discrete variant (hop): each tap moves one grid cell forward; hazards move on timers (Crossy Road).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Gravity / flap velocity | flap reaches 1.5–3 character heights | The fundamental "feel" pair |
| Gap height | 3–4.5 × character height | Primary difficulty lever |
| Gap vertical delta | 0–2 gaps between consecutive pipes | Larger deltas demand faster sequences |
| Obstacle spacing | 1.5–3 s of travel | Recovery time between tests |
| Scroll speed | constant or +2–5 % per milestone | Constant keeps it pure-skill |

- **Dynamics:** rhythmic micro-timing; failure in seconds → instant retry; social score comparison.
- **Aesthetics (MDA):** Challenge (high), Sensation; frustration is part of the appeal in the pure form.
- **Feedback and juice:** wing flap animation per tap, rotation tied to vy, score pop and sound per gate, immediate restart under 1 s.
- **Failure modes and exploits:** restart friction (must be one tap); difficulty wall at the first gates with no ramp (consider 2–3 wider intro gaps).
- **Mobile fit:** one hand, any orientation, 10–60 s runs.
- **Monetization hooks and ethical limit:** cosmetic characters and ads between runs; cap interstitial frequency (e.g., not more often than every few minutes) so retry flow survives.
- **Implementation notes:** fixed timestep is mandatory — variable dt changes jump heights and breaks fairness and replays.
- **Reference games:** Flappy Bird, Crossy Road (hop variant), Jetpack Joyride (hold variant), Geometry Dash (tap jump in a rhythm level).
- **Combines well with:** `gravity-flip`, `rhythm-timing`, collection of characters (`references/09-collection-crafting-building.md`).

### 01.14 Gravity flip — `gravity-flip`

- **ID:** `gravity-flip` · **Category:** movement (state toggle) · **Player fantasy:** "I bend the rules of the world."
- **Core rules:**
  - Global or per-actor gravity sign `s ∈ {+1, -1}`. Tap toggles `s` when allowed (typically only while grounded, so each flip is a commitment).
  - Character accelerates to the opposite surface; the camera may rotate 180° or stay fixed.
  - Hazards on both surfaces; gaps require flipping at the right moment.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Flip allowed airborne | no / once / always | Airborne flips give mid-air correction (easier) |
| Gravity magnitude | high (fast transit) | Faster transit = sharper timing |
| Transition time to other side | 0.2–0.5 s | Defines the "commitment" window |
| Scroll speed | constant or ramped | As in runners |

- **Dynamics:** binary state planning; reading two surfaces at once.
- **Aesthetics (MDA):** Challenge, Discovery (puzzle variants).
- **Feedback and juice:** world tint or background swap per gravity state, whoosh, landing thud on the new surface.
- **Failure modes and exploits:** ambiguous state when camera does not rotate (use colour or particles); flip-spam hovering (require ground contact).
- **Mobile fit:** single tap; excellent.
- **Monetization hooks and ethical limit:** none intrinsic.
- **Implementation notes:** gravity is a vector in the sim (`g_vec = (0, -g*s)`); "grounded" uses a cast along `g_vec`. Level patterns to author: alternating floor/ceiling spikes (rhythm), long single-surface gaps (commitment), and "flip corridors" that require flips at fixed intervals.

```text
on_tap(): if grounded or (AIR_FLIPS > air_flips_used): s = -s; air_flips_used += !grounded
step(dt): vel += Vector2(0, -G * s) * dt; pos += vel * dt
  grounded = shape_cast(pos, dir = (0, -s), dist = SKIN); if grounded: air_flips_used = 0
```
- **Reference games:** VVVVVV, Gravity Guy, Geometry Dash (gravity portals).
- **Combines well with:** `one-tap-impulse`, `auto-run-lanes`, `jump`.

## 5. Physics-driven mechanics

### 01.15 Slingshot aim-release — `slingshot-aim-release`

- **ID:** `slingshot-aim-release` · **Category:** physics (aim and launch) · **Player fantasy:** "I line up the perfect shot and watch the chaos unfold."
- **Core rules:**
  - Press on (or near) the launcher; drag backward. Pull vector `p = anchor - finger`, clamped to `|p| <= pull_max`.
  - Launch velocity `v0 = dir(p) * f(|p| / pull_max) * v_max`, with `f` linear or quadratic.
  - While pulling, draw a trajectory preview for the first `preview_frac` of the flight. Release fires; dragging back inside the dead radius cancels.
  - Projectile then follows simulated physics (gravity, collisions, destruction).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Max pull distance | 80–200 dp | Longer = finer power control, more thumb travel |
| Power curve | linear / quadratic | Quadratic gives precision at low power |
| Preview fraction | 0 %, 25–40 %, 100 % | The main skill lever: full preview turns it into a pure puzzle |
| Angle snap | none / 1–5° | Snap helps repeatable shots (and retries) |
| Shots per level | 2–6 | Pressure and planning |
| Wind / moving targets | 0–strong | Adds estimation skill |

- **Dynamics:** experiment-and-refine across retries; "watching it fall" spectacle; score chasing on physics outcomes (stars).
- **Aesthetics (MDA):** Sensation (destruction), Challenge, Discovery (finding weak points).
- **Feedback and juice:** elastic band stretch with creak sound rising in pitch, slow camera follow on flight, impact debris and dust, score popups per destroyed piece, last-shot slow-motion.
- **Failure modes and exploits:** non-deterministic physics making identical shots differ (players notice — use fixed timestep and deterministic solver settings); towers collapsing on their own (let structures settle and sleep before play); one shot solving everything.
- **Mobile fit:** excellent one-handed; levels of 30–120 s.
- **Monetization hooks and ethical limit:** special projectiles and "aim guide" boosters; keep three-star scores achievable without boosters.
- **Implementation notes:** preview uses the same integrator and step as the sim: `p(t) = p0 + v0·t + ½·g·t²` for the drag-free case; with drag or bounces, step the real physics in a sandbox world (cheap with ≤ 1 body).
- **Reference games:** Angry Birds (Angry Birds 2), Bowmasters, Mini golf games such as Golf Battle.
- **Combines well with:** `trajectory-ballistics`, `physics-stacking`, destruction scoring, `ragdoll`.

### 01.16 Trajectory and ballistics — `trajectory-ballistics`

- **ID:** `trajectory-ballistics` · **Category:** physics (aim) · **Player fantasy:** "I read the arc, the wind and the bounces — and land it."
- **Core rules:**
  - Aim by angle and power (drag, two sliders, or hold-release). Projectile under gravity; optional wind `a_w`, drag, bounces with restitution `e`.
  - Variants: **artillery** (turn-based duels), **bounce shooters** (balls bounce off walls/pegs and blocks), **peg physics** (one ball through a peg field, chance-heavy).
  - Optional aim line: visible to first bounce, to N bounces, or not at all.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Aim line length | none / to first bounce / full | Determines skill vs chance balance |
| Restitution | 0.6–0.95 | High makes chains longer and less predictable |
| Wind | 0–0.3 g sideways, shown as indicator | Adds an estimation layer |
| Balls per shot (bounce shooters) | 1 → grows with progress | Scales power late in a run |
| Turn time (artillery) | 10–30 s | Pressure in PvP |

- **Dynamics:** geometry thinking (banking shots); spectacle of chains; in artillery, mind games and terrain manipulation.
- **Aesthetics (MDA):** Challenge, Sensation, Fellowship (artillery duels).
- **Feedback and juice:** dotted arc that pulses, bounce sparks with ascending pitch, final shot zoom.
- **Failure modes and exploits:** tunnelling through thin geometry at speed (continuous collision or sub-stepping); infinite bounce loops (cap bounces or add slight energy loss); preview disagreeing with simulation.
- **Mobile fit:** one hand; turn-based variants are interruption-friendly.
- **Monetization hooks and ethical limit:** extra balls, aim-line extenders; do not sell trajectory reveals in PvP.
- **Implementation notes:** for aim lines, run the same physics step on a ghost body up to `N` bounces; cache per aim change, not per frame. Bounce shooters can use simple circle-vs-AABB with reflection `v' = v - (1+e)(v·n)n`.
- **Reference games:** Peggle (mobile), Worms series, Ballz, Bowmasters.
- **Combines well with:** `slingshot-aim-release`, `hold-release`, brick and block clearing, turn-based combat (`references/02-combat-action.md`).

### 01.17 Flick — `flick`

- **ID:** `flick` · **Category:** physics (release velocity) · **Player fantasy:** "A flick of my wrist sends it exactly where I want."
- **Core rules:**
  - On release, compute velocity from the last `window_ms` of touch samples (linear regression or first/last sample). Launch velocity = `k * v_touch`, clamped.
  - Curve/spin: lateral curvature of the stroke adds spin, which bends the flight.
  - Aim assist pulls toward targets by `assist` fraction when within a cone.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Velocity window | 50–100 ms | Shorter is responsive but noisy |
| Speed scale k | tuned so a comfortable flick ≈ 70 % of max | Sets the "power" feel |
| Max speed clamp | game-specific | Prevents overpowered flicks |
| Spin factor | 0–1 | Adds expressive curveballs |
| Aim assist | 0–30 % pull within 10–20° cone | Accessibility vs skill expression |

- **Dynamics:** finesse skill with immediate physical feedback; in throw-to-catch loops (Pokémon GO), throw quality adds bonus.
- **Aesthetics (MDA):** Sensation, Challenge.
- **Feedback and juice:** follow-through animation, motion trail, wind-up of target reaction, "Great/Excellent" labels with distinct sounds.
- **Failure modes and exploits:** inconsistent results from noisy samples (smooth and use regression); tiny phone screens limiting stroke length (scale by screen size in dp, not pixels).
- **Mobile fit:** one hand; natural on glass.
- **Monetization hooks and ethical limit:** throw-improving items (e.g., catch-rate berries) are acceptable if base rates are transparent.
- **Implementation notes:** keep a ring buffer of `(t, pos)` samples; fit `v = Σ((t-t̄)(x-x̄)) / Σ((t-t̄)²)` per axis for stable velocity.
- **Reference games:** Pokémon GO (ball throw with curve), Paper Toss, Flick Kick Football.
- **Combines well with:** `trajectory-ballistics`, collection (`references/09-collection-crafting-building.md`), randomness with skill modifiers (`references/07-randomness-chance-mechanics.md`).

### 01.18 Physics stacking and timed drop — `physics-stacking`

- **ID:** `physics-stacking` · **Category:** physics (precision placement) · **Player fantasy:** "Steady hands — my tower keeps rising."
- **Core rules:**
  - A piece moves (slides, swings, or hovers); tap drops it onto the stack.
  - Variant A, **slice overlap** (Stack): the overhang is cut off; the next piece takes the overlap width. Perfect placement (within `perfect_tol`) keeps width; N perfects in a row regrows it.
  - Variant B, **balance** (Tower Bloxx-style): pieces are rigid bodies; the tower sways and can topple.
  - Variant C, **drop-merge** (Suika-style): drop pieces into a container; identical pieces touching merge into the next tier; game over when pieces cross the top line.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Piece speed | starts slow, +2–5 % per level | Core difficulty ramp |
| Perfect tolerance | 2–6 % of width | Fairness of "perfect" streaks |
| Regrow on streak | +5–15 % width after 3–8 perfects | Comeback mechanic, extends runs |
| Sway amplitude (balance) | grows with height | Late-game tension |
| Merge tier count (drop-merge) | 8–11 tiers | Session length and goal horizon |

- **Dynamics:** escalating tension; "just one more" short runs; in drop-merge, spatial planning under physics uncertainty.
- **Aesthetics (MDA):** Challenge, Sensation, Submission (rhythm of drops).
- **Feedback and juice:** perfect-placement ring burst and rising musical note per perfect in a streak; slice debris falling; camera rises with tower.
- **Failure modes and exploits:** simulation non-determinism (topples differ on replay); stacks drifting with floating-point error (snap values to a grid in variant A).
- **Mobile fit:** single tap; runs of 30–120 s.
- **Monetization hooks and ethical limit:** continues and cosmetic themes; never "nudge" physics against the player near a continue offer.
- **Implementation notes:** variant A needs no physics engine — it is interval arithmetic: `overlap = [max(a0,b0), min(a1,b1)]`; if empty → game over. Variant C needs a stable 2D solver with sleep thresholds and merge events queued, not applied mid-step.
- **Reference games:** Stack, Tower Bloxx, Suika Game (drop-merge).
- **Combines well with:** `tap`, `rhythm-timing`, merge (`references/03-puzzle-mechanics.md`).

### 01.19 Ragdoll — `ragdoll`

- **ID:** `ragdoll` · **Category:** physics (articulated body) · **Player fantasy:** "Glorious, physical, unpredictable consequences."
- **Core rules:**
  - An articulated body of 10–15 rigid parts with joint limits. Switch from animation to physics on a trigger (fall, hit, death) or drive it continuously with joint motors (active ragdoll).
  - As a scoring mechanic: points per joint impact energy or broken part (dismount games). As a control mechanic: player input applies forces to limbs (comedy controls).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Bone count | 10–15 (low-end: ≤ 10) | Fidelity vs CPU cost |
| Joint stiffness / damping | soft (comedy) to stiff (realistic) | Comedic floppiness vs believable impact |
| Anim → ragdoll blend | 0.1–0.3 s | Avoids visible pops |
| Active ragdolls on screen | 1–3 on low-end mobile | Physics budget |
| Score per impact energy | linear or log | Log avoids one huge hit dominating |

- **Dynamics:** emergent comedy; replaying for "the perfect crash"; sharing clips.
- **Aesthetics (MDA):** Sensation, Expression, Fellowship (sharing).
- **Feedback and juice:** slow-motion on big impacts (0.2–0.5× for 0.3–1 s), bone-crunch sounds layered by energy, score counters ticking up per impact.
- **Failure modes and exploits:** jitter and explosions from interpenetration (limit solver velocity, use continuous detection for fast parts); expensive at scale; replay divergence.
- **Mobile fit:** one hand for launch-style designs; watch thermal budget.
- **Monetization hooks and ethical limit:** vehicles/props and cosmetic characters; violent content affects age rating.
- **Implementation notes:** sleep ragdolls aggressively after settling (velocity < threshold for 0.5 s); pool ragdoll instances; on low tier swap distant ragdolls for baked fall animations.

```text
on_contact(bone, impulse): if impulse > MIN_IMPULSE:
    pts = BONE_WEIGHT[bone] * log(1 + impulse / IMPULSE_UNIT)   # log damps single huge hits
    score += pts * combo; combo = min(combo + 0.1, COMBO_CAP); spawn_popup(bone.pos, pts)
end_run(): when all bodies asleep or timeout 8 s → final score
```
- **Reference games:** Turbo Dismount, Stickman Dismounting, Human: Fall Flat (mobile).
- **Combines well with:** `slingshot-aim-release`, `physics-vehicle`, hit reactions (`references/02-combat-action.md`).

### 01.20 Momentum and slopes — `momentum-slopes`

- **ID:** `momentum-slopes` · **Category:** physics (energy) · **Player fantasy:** "I flow with the terrain and fly."
- **Core rules:**
  - Speed along terrain follows energy: `v² = v0² + 2·g_eff·Δh` minus friction and drag losses.
  - Player input changes effective gravity or posture: hold to "dive" (heavier) on downslopes, release on upslopes to launch (Tiny Wings pattern); or tap to jump and flip in the air (Alto's pattern).
  - Landings matched to slope angle within `land_tol` keep speed (or boost); bad landings lose speed or crash.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Dive gravity multiplier | 1.5–3× | Strength of the hold-to-dive verb |
| Friction | 0.01–0.05 | Pace of speed bleed |
| Landing tolerance | 10–30° | Forgiveness of landings |
| Perfect-landing boost | +5–20 % speed | Rewards rhythm; drives flow |
| Terrain generator amplitude/period | tuned to speed | Defines the rhythm of hills |

- **Dynamics:** rhythm with terrain; risk of tricks for score vs safe landings; a time pressure (night falls, avalanche chaser) closes the loop.
- **Aesthetics (MDA):** Sensation, Submission (flow), Challenge.
- **Feedback and juice:** wind sound tied to speed, camera zoom-out at speed, trail ribbons, perfect-landing chime.
- **Failure modes and exploits:** terrain seeds that kill flow (validate generated terrain against a bot); runaway speed (cap); loss of readability at speed.
- **Mobile fit:** one hold/release verb; excellent one-handed.
- **Monetization hooks and ethical limit:** characters with different handling (keep sidegrades, not strict upgrades, in score-competitive modes).
- **Implementation notes:** terrain as a sum of sines or Perlin-noise splines; keep the integrator in the sim and terrain sampling deterministic by seed.
- **Reference games:** Tiny Wings, Alto's Adventure, Ski Safari.
- **Combines well with:** `jump`, `hold-release`, `physics-vehicle`, missions (`references/05-progression-meta-mechanics.md`).

### 01.21 Physics vehicle (gas / brake) — `physics-vehicle`

- **ID:** `physics-vehicle` · **Category:** physics (vehicle) · **Player fantasy:** "I'm nursing a ridiculous machine over impossible terrain."
- **Core rules:**
  - Two inputs: gas (right thumb) and brake/reverse (left thumb). Wheels on spring-damper suspension; motor torque drives wheels.
  - In the air, gas rotates the body backward and brake forward (reaction torque), enabling flips and landing control.
  - Fuel or a timer limits distance; head contact or upside-down for `t` seconds = crash. Coins and fuel cans along the track.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Motor torque / top speed | per vehicle and upgrade | Progression via upgrades |
| Suspension stiffness / damping | soft (bouncy) – stiff | Comedy vs control |
| Centre of mass height | low–high | Flip tendency |
| Air rotation torque | 0.5–2× ground torque | Trick control |
| Fuel per distance | tuned to 1–3 min runs | Session length |

- **Dynamics:** throttle feathering; upgrade-and-retry loop (distance improves with upgrades); risky flips for bonus.
- **Aesthetics (MDA):** Sensation, Challenge, Submission (upgrade loop).
- **Feedback and juice:** engine pitch tied to RPM, suspension squash, dust and sparks, flip bonus text.
- **Failure modes and exploits:** upgrades making terrain trivial (scale terrain by distance); physics glitches launching vehicles (cap impulses); unreadable crash causes.
- **Mobile fit:** landscape, two thumbs; sessions of 1–3 min.
- **Monetization hooks and ethical limit:** vehicle and part upgrades, fuel boosts; avoid making upgrades mandatory for basic progress in competitive modes.
- **Implementation notes:** wheels as circle bodies with revolute joints + motors, chassis as a box; or raycast suspension (cheaper, more stable). Fixed timestep with 4–8 velocity iterations.
- **Reference games:** Hill Climb Racing, Trials Frontier, Bike Race.
- **Combines well with:** `momentum-slopes`, `ragdoll`, upgrade economies (`references/04-economy-resource-mechanics.md`).

### 01.22 Draw-a-path — `draw-a-path`

- **ID:** `draw-a-path` · **Category:** input/physics (authored geometry) · **Player fantasy:** "I solve it by drawing — my line becomes real."
- **Core rules:**
  - The player draws a polyline. Three families: **route** (an agent follows the path — Flight Control), **object** (the stroke becomes a rigid body with thickness — Brain It On!, Love Balls), **connector** (the path links nodes — see pipe/flow in `references/03-puzzle-mechanics.md`).
  - Constraints: ink budget (max length), forbidden zones, minimum stroke length, max strokes.
  - Evaluation: physics runs after drawing (object family) or continuously (route family).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Ink budget | 0.5–3 screen widths | Main difficulty lever in object family |
| Resample spacing | 4–10 dp | Smoothness vs collider count |
| Simplification ε (RDP) | 2–4 dp | Fewer segments = cheaper physics |
| Stroke thickness | 6–16 dp | Stability of drawn objects |
| Stroke count limit | 1–3 | Forces elegant solutions |
| Agent speed (route family) | ramps with score | Juggling pressure |

- **Dynamics:** creative problem solving with many valid solutions; star ratings for ink efficiency; in route games, attention juggling.
- **Aesthetics (MDA):** Expression, Discovery, Challenge.
- **Feedback and juice:** ink meter draining, pencil scratch sound, line wobble while drawing, satisfying "solid" tick when the stroke becomes physical.
- **Failure modes and exploits:** giant scribbles that wall off everything (ink budget, forbidden zones); unstable thin strokes (minimum thickness, merge colliders); accidental strokes from palm touches.
- **Mobile fit:** one finger; puzzles fit 1–3 min sessions.
- **Monetization hooks and ethical limit:** hints (show a solution stroke), skips; keep levels solvable within the ink budget without hints.
- **Implementation notes:** resample to even spacing → Ramer–Douglas–Peucker simplify → build a chain of capsule colliders → compound rigid body with mass proportional to length. Validate levels with a solver that searches stroke templates, or at least a recorded reference solution replayed headless.
- **Reference games:** Flight Control, Brain It On!, Love Balls, Draw Climber, Line Rider.
- **Combines well with:** `trajectory-ballistics`, physics puzzles (`references/03-puzzle-mechanics.md`), `physics-stacking`.

### 01.23 Rhythm-timed input — `rhythm-timing`

- **ID:** `rhythm-timing` · **Category:** input timing · **Player fantasy:** "I am the music."
- **Core rules:**
  - A chart schedules notes at beat times `t_i` (from BPM and offsets). Each note expects an input type (tap, hold, swipe, lane).
  - Judgement: `Δ = t_input - t_i - calib_offset`; graded by windows (e.g., Perfect / Great / Good / Miss). Combo increments on non-miss; score = base × judgement weight × combo multiplier.
  - Fail state: health drains on misses, or none (score attack).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Perfect window | ±30–50 ms | Elite precision |
| Good window (outer) | ±100–150 ms | Accessibility floor |
| Note density | 1–8 notes/s | Main difficulty driver per chart |
| Scroll speed | player setting 1–10 | Readability, not difficulty, if done right |
| Calibration offset | −200 to +200 ms | Compensates device audio/display latency |
| Combo multiplier cap | 2–4× | How much one miss costs |

- **Dynamics:** chart memorisation, flow states, mastery ladders across difficulty tiers.
- **Aesthetics (MDA):** Sensation, Challenge, Expression (in freestyle variants).
- **Feedback and juice:** judgement text with colour, hit sparks synced to beat, music filter when health is low, combo counter pulsing on beat.
- **Failure modes and exploits:** timing against frame time instead of the audio clock (drifts); Android audio output latency varies widely by device (ship a calibration screen); Bluetooth headphones add large latency (detect and warn); mashing defeating loose windows (penalise extra inputs).
- **Mobile fit:** portrait lanes one-hand (simple charts), two thumbs for dense charts; songs of 1–3 min fit sessions.
- **Monetization hooks and ethical limit:** song packs and passes are clean; music licensing is the real cost — check licence terms per song (see `legal-ethics`).
- **Implementation notes:** schedule with the audio DSP clock (`audio_time = playback_position + output_latency`); judge in the sim using timestamps from the input event, not the frame in which it was processed.
- **Reference games:** Piano Tiles 2, Beatstar, Cytus II, Deemo, Magic Tiles 3.
- **Combines well with:** `tap`, `one-tap-impulse`, `slice`, combat timing (`references/02-combat-action.md`).

## 6. Cross-cutting implementation rules

1. **Fixed timestep simulation.** Run movement and physics at a fixed 60 or 120 Hz step, render with interpolation. Variable steps change jump heights, break replays and make the deterministic playthrough gate impossible.
2. **Inputs are events with timestamps.** Queue touch events with their OS timestamps; the sim consumes them on the step whose time window contains them. This makes buffers, coyote time and rhythm judgement exact and testable.
3. **One tuning file.** Every knob in this document lives in data (JSON/Resource/ScriptableObject) under a `tuning/` path, with min/max and units mirroring the contract's `mechanics[].parameters` entries.
4. **Forgiveness is invisible.** Coyote time, jump buffers, expanded hit radii, aim assist and lane-switch buffering should never be visible; players experience them as "the controls are good".
5. **Validate generated content with a bot.** Runner chunks, terrain seeds and physics puzzles must pass a headless bot check before shipping (see `qa-testing` and `${CLAUDE_PLUGIN_ROOT}/scripts/pcg.py`).
6. **Budget physics on low-end devices.** Rough starting budget for a low-tier phone: ≤ 100 active rigid bodies, ≤ 3 ragdolls, sleep thresholds enabled, 4–8 solver iterations. Confirm with `mobile-performance` profiling.
7. **Edge gestures and safe areas.** Keep gesture start zones away from OS edge gestures and inside safe-area insets (see `mobile-ux`).
