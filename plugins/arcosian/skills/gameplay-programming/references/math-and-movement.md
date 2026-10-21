# Math and movement for gameplay code

The small amount of maths that does most of the work in mobile games: vectors, interpolation and easing, springs and smoothing, Bezier curves, grid and hex coordinates, collision primitives, kinematic character controllers, jump arcs and cameras. Everything is given as formulas plus short GDScript or C# you can paste into a core or a view, with notes on frame-rate independence and determinism. Use it when implementing feel, movement, aiming, camera behaviour or grid logic, and when a bug turns out to be a sign, a unit or a frame-rate assumption.

## Contents

1. Vectors you actually use
2. Interpolation and frame-rate independent smoothing
3. Easing functions
4. Springs and damped motion
5. Bezier and splines
6. Grids: square and hex
7. Collision primitives
8. Kinematic controllers
9. Jump arcs and platforming feel
10. Cameras
11. Aiming, projectiles and prediction
12. Numerical hygiene
13. Quick formula sheet

## 1. Vectors you actually use

| Need | Formula | Notes |
|---|---|---|
| Length, distance | `|v| = sqrt(x^2 + y^2)`; compare squared distances when you can | Avoid sqrt in hot loops: `d2 < r*r` |
| Normalise | `v / |v|`, guard zero length | Return zero vector, never NaN |
| Dot | `a.b = ax*bx + ay*by = |a||b|cos(theta)` | Facing test: `dot(forward, to_target) > cos(half_fov)` |
| 2D cross (scalar) | `a x b = ax*by - ay*bx` | Sign tells which side; turn direction |
| Project | `proj_b(a) = b * dot(a,b) / dot(b,b)` | Slide along a wall: `v - n * dot(v, n)` |
| Reflect | `v - 2 * dot(v, n) * n` | `n` must be unit length |
| Rotate | `(x cos t - y sin t, x sin t + y cos t)` | Angle unit (radians) must match engine |
| Angle between | `atan2(cross, dot)` | Signed, robust at all angles |
| Perpendicular | `(-y, x)` | Left normal in y-up coordinates; flips in y-down screen space |

Coordinate spaces: Godot 2D is y-down on screen; Unity 2D is y-up. Write core maths in one convention and convert at the view edge. Cross-product signs and rotation directions flip between them: this causes most "turns the wrong way" bugs.

Angle lerp: interpolate the shortest way. `diff = fposmod(b - a + PI, TAU) - PI; a + diff * t` (GDScript has `lerp_angle`).

## 2. Interpolation and frame-rate independent smoothing

Linear: `lerp(a, b, t) = a + (b - a) * t`. The classic bug is `x = lerp(x, target, 0.1)` per frame: speed depends on frame rate. Use an exponential decay with a time constant instead:

```
x = target + (x - target) * exp(-dt * k)        # k = responsiveness (per second)
# equivalent: t = 1 - exp(-k * dt); x = lerp(x, target, t)
```

```gdscript
func smooth(current: float, target: float, k: float, dt: float) -> float:
	return lerpf(current, target, 1.0 - exp(-k * dt))
```

```csharp
static float Smooth(float cur, float tgt, float k, float dt) => Mathf.Lerp(cur, tgt, 1f - Mathf.Exp(-k * dt));
```

Rule of thumb: half-life `h` seconds corresponds to `k = ln 2 / h`; `k = 10` reaches about 63% of the gap in 0.1 s.

Move toward at constant speed: `move_toward(x, target, speed * dt)` never overshoots.

Inverse lerp and remap: `t = (v - a) / (b - a)`; `remap(v, a, b, c, d) = lerp(c, d, t)`; always clamp `t` if the input can leave range.

Inertia and acceleration: velocity approaches desired velocity by an acceleration limit (`v = move_toward(v, desired, accel * dt)`), with separate accel and decel values (snappy stop, softer start) for feel (see `game-feel`).

## 3. Easing functions

Easing maps `t in [0,1]` to a shaped `[0,1]` progress. Pick by purpose:

| Purpose | Curve | Formula (t in 0..1) |
|---|---|---|
| UI element enters | ease-out cubic | `1 - (1 - t)^3` |
| UI element leaves | ease-in cubic | `t^3` |
| Moves between states | ease-in-out | `t < 0.5 ? 4t^3 : 1 - (-2t + 2)^3 / 2` |
| Gentle settle | smoothstep | `t*t*(3 - 2t)` |
| Smoother settle | smootherstep | `t^3*(t*(6t - 15) + 10)` |
| Playful overshoot | back-out | `1 + c3*(t-1)^3 + c1*(t-1)^2`, `c1 = 1.70158`, `c3 = c1 + 1` |
| Bounce | bounce-out | piecewise parabolas (use the engine's tween) |
| Elastic pop | elastic-out | `2^(-10t) * sin((10t - 0.75) * 2pi/3) + 1` |

Durations: small UI changes about 100 to 200 ms; screen transitions 200 to 350 ms; celebratory moments longer but skippable. Make the timing a tuning value. Easing belongs in presentation; the core never depends on it (it would couple rules to rendering time).

Tweens fight: kill the previous tween on a property before starting a new one, or you get jitter. In Godot keep a tween reference and call `kill()`; in Unity use a tween library's ID/kill API or your own coroutine handle.

## 4. Springs and damped motion

A critically damped spring gives smooth, interruptible follow motion with continuous velocity (better than easing curves when targets move). Semi-implicit Euler with damping:

```
a = -k * (x - target) - c * v
v += a * dt
x += v * dt
# critical damping: c = 2 * sqrt(k)      (mass = 1)
# underdamped (bouncy): c < 2*sqrt(k); overdamped (sluggish): c > 2*sqrt(k)
```

Stability: large `k*dt^2` blows up. Clamp `dt` (for example 1/30 s) or sub-step. A stable closed form exists (the critically damped spring "SmoothDamp" used by Unity's `Mathf.SmoothDamp`); prefer it when you want robustness without tuning.

Use springs for: camera follow, UI wobble on press, score counters, tilt toward touch, squash and stretch recovery. Parameters: `k` 100 to 400 gives quick motion, damping ratio `zeta = c / (2 sqrt(k))` of 0.6 to 0.8 gives a subtle bounce, 1.0 none. Treat these ranges as starting points to tune by feel.

Trauma-style shake (a camera effect popularised in a GDC talk by Squirrel Eiserloh): keep `trauma` in 0..1 decaying linearly; offset = `max_offset * trauma^2 * noise(t)`. Squaring makes small hits subtle and big hits dramatic. Use smooth noise rather than random per frame.

## 5. Bezier and splines

Quadratic Bezier: `B(t) = (1-t)^2 P0 + 2(1-t)t P1 + t^2 P2`. Cubic: `B(t) = (1-t)^3 P0 + 3(1-t)^2 t P1 + 3(1-t)t^2 P2 + t^3 P3`.

```gdscript
func cubic(p0: Vector2, p1: Vector2, p2: Vector2, p3: Vector2, t: float) -> Vector2:
	var u: float = 1.0 - t
	return p0 * (u*u*u) + p1 * (3.0*u*u*t) + p2 * (3.0*u*t*t) + p3 * (t*t*t)
```

Uses: coin-fly-to-HUD arcs (control point above the line), card draw arcs, projectile lobs, path-following enemies, curved runner tracks.

Constant speed along a curve: `t` is not arc length. Precompute a table of cumulative lengths (for example 32 samples), then map distance to `t` by binary search and interpolation. Otherwise objects speed up and slow down through curves.

Splines through points: Catmull-Rom passes through control points (good for authored paths): `0.5 * (2P1 + (-P0 + P2) t + (2P0 - 5P1 + 4P2 - P3) t^2 + (-P0 + 3P1 - 3P2 + P3) t^3)`. Use the engine's `Curve2D`/`Path2D` (Godot) or splines package (Unity) when available.

Tangents and facing: derivative of the cubic is `3(1-t)^2 (P1-P0) + 6(1-t)t (P2-P1) + 3t^2 (P3-P2)`; use it to orient sprites along the path.

## 6. Grids: square and hex

Square grid index: `i = y * width + x`; neighbours via offset tables (4-way or 8-way); check bounds before indexing. World to cell: `floor((pos - origin) / cell_size)`. Cell centre: `(cell + 0.5) * cell_size + origin`. Use `floor`, not truncation toward zero, for negatives.

Distances: Manhattan `|dx| + |dy|` for 4-way; Chebyshev `max(|dx|, |dy|)` for 8-way with equal diagonal cost; octile `max + (sqrt2 - 1)*min` when diagonals cost sqrt2.

Isometric: screen = `((x - y) * w/2, (x + y) * h/2)`; inverse: `x = (sx/(w/2) + sy/(h/2)) / 2`, `y = (sy/(h/2) - sx/(w/2)) / 2`. Sort draw order by `x + y` (plus height).

Hex grids: choose a representation once and stay in it. Axial coordinates `(q, r)` (third cube coordinate `s = -q - r`) make most maths simple (the widely used reference is Amit Patel's Red Blob Games hex guide).

| Operation | Axial / cube formula |
|---|---|
| Neighbours | add one of six direction vectors: `(+1,0) (+1,-1) (0,-1) (-1,0) (-1,+1) (0,+1)` |
| Distance | `(|dq| + |dr| + |dq + dr|) / 2` |
| Pixel from hex (pointy-top) | `x = size * (sqrt3 * q + sqrt3/2 * r)`, `y = size * (3/2 * r)` |
| Pixel from hex (flat-top) | `x = size * (3/2 * q)`, `y = size * (sqrt3/2 * q + sqrt3 * r)` |
| Hex from pixel | invert the matrix, convert to fractional cube, round (round all three, fix the component with the largest rounding error so `q + r + s = 0`) |
| Ring / range | loop `dq` from `-N` to `N`, `dr` from `max(-N, -dq-N)` to `min(N, -dq+N)` |
| Rotation (60 degrees) | cube `(q, r, s) -> (-r, -s, -q)` |

Storage of hex maps: a dictionary keyed by packed int (`(q + OFFSET) << 16 | (r + OFFSET)`) or a 2D array with offset; document the offset convention (odd-r, even-q) when interfacing with an engine tilemap.

Grid snapping and dragging: snap by rounding the cell from pointer position, but preview the target cell and validity during the drag and offset the drag point so the piece does not jump under the finger (see `mobile-ux`).

## 7. Collision primitives

Prefer simple tests in the core for deterministic puzzle and arcade logic; use the engine's physics for feel-driven action when determinism is not needed.

| Test | Method |
|---|---|
| Point in AABB | `min.x <= p.x <= max.x` and same for y |
| AABB vs AABB | overlap on both axes: `a.min < b.max and a.max > b.min` |
| Circle vs circle | `dist2 < (ra + rb)^2` |
| Circle vs AABB | clamp circle centre to the box, compare `dist2` with `r^2` |
| Point in circle | `dist2 <= r^2` |
| Segment vs segment | cross-product orientation tests |
| Ray vs AABB (slab) | per axis compute `t1`, `t2`; `tmin = max(min(t1,t2))`, `tmax = min(max(t1,t2))`; hit if `tmax >= max(tmin, 0)` |
| Swept AABB / continuous | move along axes separately (X then Y), or sweep by time of impact |
| Point in polygon | ray-casting or winding number |
| Overlap vs touching | decide `<` vs `<=` once and document it (matters for grids and frame-perfect inputs) |

Resolution: push out along the axis of least penetration; for moving-vs-static use separate axis moves to avoid corner snagging. Tunnelling: bullets at speed `v` with radius `r` skip walls when `v * dt > 2r`; sub-step, sweep or raycast. Use layers or masks to limit pairs; add a spatial hash when pair counts grow (see `game-architecture`).

Forgiveness: players want generosity. Shrink hurtboxes relative to sprites (for example 60 to 80 percent, tune it), enlarge pickup and button hit areas, give coyote time and input buffering, and use the thumb-sized touch targets from `mobile-ux`. Collision that feels unfair is a bug even if mathematically correct.

## 8. Kinematic controllers

A kinematic controller moves by explicit velocity and resolves collisions itself (Godot `CharacterBody2D` with `move_and_slide`; Unity `CharacterController` or custom raycast controller), as opposed to a dynamic rigidbody pushed by forces. For platformers and top-down games, kinematic gives predictable, tunable feel.

Platformer controller outline (per fixed step):

```gdscript
func _physics_process(delta: float) -> void:
	var input_x: float = Input.get_axis("left", "right")
	var target: float = input_x * max_speed
	var accel: float = ground_accel if is_on_floor() else air_accel
	if absf(input_x) < 0.01:
		accel = ground_decel if is_on_floor() else air_decel
	velocity.x = move_toward(velocity.x, target, accel * delta)
	velocity.y = minf(velocity.y + gravity * delta, max_fall_speed)
	if jump_buffer > 0.0 and coyote > 0.0:
		velocity.y = -jump_speed
		jump_buffer = 0.0; coyote = 0.0
	move_and_slide()
	coyote = coyote_time if is_on_floor() else maxf(coyote - delta, 0.0)
	jump_buffer = maxf(jump_buffer - delta, 0.0)
```

Feel parameters (starting points only): coyote time about 0.08 to 0.12 s; jump buffer about 0.1 to 0.15 s; variable jump height by cutting upward velocity when the button is released; apex hang (reduce gravity near the apex) for control; faster fall than rise (gravity multiplier about 1.5 to 2) for snappy arcs; corner correction (nudge around ledge corners by a few pixels); max fall speed to keep readability.

Top-down: normalise diagonal input so diagonals are not faster; slide along walls by projecting velocity; separate movement from facing.

Touch controls: virtual stick with dynamic origin (appears where the thumb lands), dead zone about 10 to 15 percent, and response curve (squared magnitude for fine control near centre); one-thumb schemes (tap-to-move, drag-to-aim) beat dual sticks on phones for casual play.

Slopes and steps: use floor snap length, max floor angle, and step-up heights; test with ramps and one-way platforms specifically.

## 9. Jump arcs and platforming feel

Derive jump parameters from design numbers instead of guessing: desired height `H` and time to apex `T`.

```
gravity  g  = 2H / T^2
launch   v0 = 2H / T        (v0 = g * T)
```

Example: `H = 3.0` units, `T = 0.4` s gives `g = 37.5` units/s^2, `v0 = 15` units/s. Falling gravity multiplier `m` (for example 1.6) shortens the fall; total air time `T + T/sqrt(m)`.

Horizontal reach: `distance = speed_x * air_time`. Design gaps from this: required jump distance `D` and speed `vx` gives `air_time = D / vx`, then pick `H` and `T` to match; keep the gap at roughly 70 to 80 percent of max reach for standard challenges so execution is comfortable (a tuning heuristic, verify by playtest).

Discrete integration matters: with semi-implicit Euler the realised apex differs slightly from the formula; fix by applying half the gravity step on the launch frame or verify with a test that runs the controller headlessly and asserts apex height within tolerance. Compute jump arcs in the core with a fixed timestep so replays match.

Projectile arcs: `p(t) = p0 + v0 t + 0.5 g t^2`. To hit a target at horizontal distance `d` and height difference `h` with launch speed `s` and gravity `g`, solve the quadratic for angle (two solutions: low and high arc; none if out of range):

```
tan(theta) = (s^2 +- sqrt(s^4 - g*(g*d^2 + 2*h*s^2))) / (g*d)
```

## 10. Cameras

| Camera | Technique | Notes |
|---|---|---|
| Fixed puzzle board | Fit board to safe area: `scale = min(w_avail / board_w, h_avail / board_h)` | Recompute on resize, rotation and safe-area changes |
| Follow | Critically damped spring or exponential smoothing toward target | Smooth on dt, not per frame |
| Look-ahead | Offset along velocity (clamped) | Prevents running into unseen hazards |
| Dead zone | Camera moves only when target leaves a box | Reduces motion sickness in precise games |
| Bounds clamp | Clamp camera rect to level bounds | Clamp after smoothing |
| Runner / auto-scroll | Constant or ramping speed | Make speed a tuning curve |
| Zoom | Scale about the pinch centre | Keep the world point under fingers fixed: `new_offset = centre - (centre - offset) * (new_zoom / old_zoom)` |
| Shake | Trauma model | Offset the view, not the logic position; honour reduced-motion setting |
| Pixel-art | Snap camera to whole pixels | Avoid shimmer |

Safe areas and aspect ratios: design for a range from tall phones to tablets; anchor HUD to safe-area edges; keep important gameplay inside a central region; test notched devices (see `mobile-ux` and the template's `services/safe_area.gd`).

Camera in the sim-core model: camera position is presentation state unless gameplay depends on it (for example auto-scroll that kills the player, or spawning off-screen). If gameplay depends on it, move that state into the core and let the view follow.

## 11. Aiming, projectiles and prediction

- Lead the target: solve for the intercept time `t` with `|target_pos + target_vel * t - shooter_pos| = projectile_speed * t`; quadratic in `t`; pick the smallest positive root; fall back to aiming directly if none.
- Auto-aim assist for touch: snap to nearest valid target within a cone, with stickiness so aim does not jitter between targets; scale assist by difficulty.
- Homing: limit turn rate (`angle_step = max_turn * dt`) so projectiles curve rather than snap.
- Hit detection for fast thin projectiles: raycast from previous to current position each step.
- Spread patterns: angle offsets `base + (i - (n-1)/2) * step`; randomise within a cone using the seeded RNG in the core.

## 12. Numerical hygiene

- Compare floats with an epsilon; never `==` after arithmetic.
- Guard divisions and normalisations; return safe defaults, never NaN. NaN propagates and corrupts state silently; assert `is_finite` at boundaries in debug.
- Large coordinates lose precision: keep worlds within a modest range or recentre (floating origin) for endless runners.
- Cast and rounding: define `floor`, `round`, `ceil` choice per rule; engines differ for negative numbers and halves.
- Angles: pick radians internally; convert for display and tools.
- Frame rate: all rates are per second; all integrations take `dt`; clamp `dt`.
- Determinism: for cross-platform lockstep use integers or fixed point; otherwise keep float rules out of anything replayed on another device model.
- Units: write units in names (`speed_px_s`, `duration_ms`); mixing pixels, world units and tiles is the main source of scale bugs.

## 13. Quick formula sheet

| Task | Formula |
|---|---|
| Frame-rate independent lerp factor | `1 - exp(-k * dt)` |
| Critical damping coefficient | `c = 2 * sqrt(k)` |
| Jump gravity / launch from height H, apex time T | `g = 2H / T^2`, `v0 = 2H / T` |
| Hex distance (cube) | `max(|dq|, |dr|, |ds|)` |
| Circle overlap | `dist2 < (ra + rb)^2` |
| Reflect | `v - 2 (v.n) n` |
| Slide | `v - (v.n) n` |
| Signed angle | `atan2(cross(a,b), dot(a,b))` |
| Remap | `lerp(c, d, (v - a) / (b - a))` |
| Trauma shake offset | `max_offset * trauma^2 * noise(t)` |
| Pinch zoom keep-centre | `offset' = centre - (centre - offset) * z'/z` |
