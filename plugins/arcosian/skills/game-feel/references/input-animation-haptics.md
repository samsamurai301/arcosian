# Input, animation and haptics

The layer under every effect: how long the player waits, how forgiving input is, how motion is timed and eased, and how haptics are produced on phones. It covers the finger-to-pixel latency chain and budgets, forgiveness windows (coyote time, buffering), gesture thresholds and dead zones, the 12 animation principles applied to gameplay and UI, easing formulas with a timing table, the `Fx` and `Ease` helpers behind the catalog's Unity snippets, and a haptics layer for iOS, Android, Godot and Unity with audio pairing and accessibility settings. Numbers are starting values to tune on device.

## Contents

1. Latency chain and budgets  2. Forgiveness and input handling  3. Touch precision, gestures and dead zones  4. The 12 animation principles in games  5. Easing, springs, timing and the Unity helpers  6. Haptics (6.1 principles, 6.2 iOS, 6.3 Android, 6.4 Godot and Unity layer, 6.5 settings and accessibility, 6.6 pairing)  7. Volatile facts

## 1. Latency chain and budgets

The delay between finger-down and the first changed pixel is a stack; each stage can add up to a frame, and you control the middle ones.

| Stage | What adds delay | What you control |
|---|---|---|
| Touch sensor and OS | Digitizer scan, gesture arbitration, recognisers that wait to disambiguate (double tap, long press) | No delaying recognisers on the primary play surface; keep system-gesture edges free of critical touches |
| Event delivery | Events batched or accumulated once per frame | Godot: `Input.use_accumulated_input = false` for drag and drawing, read `_input` events and stamp the time; Unity Input System: process events in dynamic update and read event timestamps |
| Simulation | A fixed-step tick consumes input at its next step | Apply state changes in the event or `Update` path, interpolate rendering, keep the fixed step at or below 1/60 s for action games |
| Render queue | Each frame in flight adds a refresh interval | Keep the queue shallow, use platform frame pacing (`mobile-performance`), avoid CPU-GPU sync stalls |
| Display | Scanout and panel response; 60 Hz = 16.7 ms, 90 Hz = 11.1 ms, 120 Hz = 8.3 ms | Higher refresh where battery allows; durations in seconds so feel is identical across rates |
| Audio and haptics | Audio buffer size, mixer latency, actuator onset | Low-latency audio path, short pre-decoded SFX, pre-warmed haptic engine |

Budgets (targets to verify on the lowest supported device, not measurements):

| Signal | Target | Why |
|---|---|---|
| Contact acknowledgement (pressed state, ripple at the finger) | The next displayed frame after the event | The one piece of feedback that must never wait |
| Cause to visible effect | At most 100 ms from finger-down to first changed pixel for taps; 50-70 ms for timing-critical verbs (parry, rhythm, jump) where hardware allows | 0.1 s is the classic "feels instantaneous" limit in HCI literature (summarised by Jakob Nielsen); timing games punish more |
| Audio onset | Within 1-3 frames of the visual; audio late hurts more than audio early | Perceived sync |
| Haptic onset | Within about one frame of the audio transient | Reads as one event |
| Reward flourishes | No ceiling; 100-300 ms of deliberate anticipation is good | Latency rules apply to caused feedback only |

How to measure: (1) film the screen and the finger with a second phone at 240 fps (1 frame = 4.2 ms), count frames from finger-down to the first changed pixel, repeat 20 times and report the median and worst; (2) in the engine, timestamp the input event and the frame that first renders its effect, log 1,000 taps and track p50 and p95 for the part you control; (3) always on release builds on the lowest supported device. Android audio latency varies widely by device: measure it separately.

Latency checklist: read input on arrival, not only on the next fixed tick, and apply it in the same frame; pre-warm shaders, particle systems, audio voices and the haptic engine (a first-use hitch is a latency bug); never instantiate or load inside the input callback; decode short SFX at load instead of streaming; keep scroll and gesture containers that delay touches off the play view.

## 2. Forgiveness and input handling

Forgiveness is feel the player never sees: windows that make the game do what they meant. It should favour the player; being generous to the player and strict with enemies is normal.

| Mechanic | Starting window | Purpose |
|---|---|---|
| Coyote time | 80-120 ms (5-7 frames at 60 Hz) | A jump still works just after leaving a ledge |
| Jump buffer | 100-150 ms | A press just before landing still jumps |
| Action buffer (attack, dodge, ability) | 100-200 ms | Queue the next action during recovery, consume at the first cancel frame |
| Variable jump height | Cut upward velocity to 40-50% on release | Taps hop, holds jump |
| Gravity shaping | Fall gravity 1.5-2.0× rise gravity; half gravity for 60-100 ms near the apex | Removes floatiness and keeps air control |
| Corner correction | Nudge 4-8 px (10-20% of a tile) past ledge and ceiling corners | Stops head bonks and ledge snags |
| Hurtbox vs sprite | 10-30% smaller than the sprite | Reads as fair |
| Pickup magnet | 1.5-3× the visual radius | Reads as generous |
| Timing windows (parry, perfect) | ±50-100 ms casual, ±30-50 ms tight; show the window | Difficulty is the window width: tune per genre |
| Touch aim assist | Snap to the nearest target within 40-60 dp or 6-10 degrees | Fat-finger tolerance (section 3) |

Coyote time, jump buffer and variable height together:

```gdscript
func _physics_process(delta: float) -> void:  # CharacterBody2D; consts COYOTE = 0.10, BUFFER = 0.12, FALL_MULT = 1.7; float vars _coyote, _buffer
	_coyote = COYOTE if is_on_floor() else maxf(_coyote - delta, 0.0)
	_buffer = BUFFER if Input.is_action_just_pressed("jump") else maxf(_buffer - delta, 0.0)
	if _buffer > 0.0 and _coyote > 0.0:
		velocity.y = -JUMP_SPEED; _buffer = 0.0; _coyote = 0.0
	if Input.is_action_just_released("jump") and velocity.y < 0.0:
		velocity.y *= 0.5  # variable height
	velocity.y += GRAVITY * (FALL_MULT if velocity.y > 0.0 else 1.0) * delta  # Godot's y axis points down
	move_and_slide()
```

```csharp
void Update() {  // fields coyote, buffer, vel, jumpSpeed, gravity, fallMult; grounded, jumpPressed, jumpReleased come from your input layer; Coyote = 0.10f, Buffer = 0.12f
    float dt = Time.deltaTime;
    coyote = grounded ? Coyote : Mathf.Max(coyote - dt, 0f);
    buffer = jumpPressed ? Buffer : Mathf.Max(buffer - dt, 0f);
    if (buffer > 0f && coyote > 0f) { vel.y = jumpSpeed; buffer = coyote = 0f; }
    if (jumpReleased && vel.y > 0f) vel.y *= 0.5f;
    vel.y -= gravity * (vel.y < 0f ? fallMult : 1f) * dt;
}
```

Action buffering for combat and abilities: store `(action, timestamp)`, expire after 100-200 ms, and when the character reaches a cancel window or the end of recovery, consume the newest valid entry. Stamp events with the time they arrived, not the time the simulation read them. Log dropped inputs in debug builds: a dropped input is the most common hidden cause of "unresponsive".

## 3. Touch precision, gestures and dead zones

Platform defaults for touch slop and press timeouts are of the same order as below; when you use native gestures read the live values (Android `ViewConfiguration`, iOS gesture recognisers) rather than hard-coding.

| Gesture | Starting thresholds | Notes |
|---|---|---|
| Tap | Movement under 8-12 dp or pt, duration under 250-300 ms | Fire on release for UI; on touch-down for fast games; show a pressed state either way |
| Long press | 400-500 ms, movement under slop | Progress ring after about 150 ms; tick haptic at trigger |
| Double tap | Second tap within 250-300 ms and 40 dp | Delays the single tap by the window: never on a primary action |
| Drag start | Movement beyond slop; commit direction after 2-3 samples | Lift a draggable on touch-down, before any movement |
| Swipe | Distance 40-60 dp or 8-10% of the short side; velocity 300-600 dp/s; within ±25-35 degrees of the axis | Commit when the threshold is crossed, not on release, in action games |
| Flick | Release velocity from the last 60-100 ms of samples | Use velocity, not distance, to decide fling and throw |
| Pinch | Scale change of 5-8% before engaging | Ignore while a single-finger drag is active |

- **Target selection.** The contact point is imprecise and the thumb hides the target. Choose the interactive object under the touch centroid, else the nearest within about 0.6× target size. On dense boards add hysteresis (switch the selected cell only after the finger is 55-60% into the neighbour) to stop flicker.
- **Grab offset.** Attach a dragged item at the grab offset, not its centre, then hold it 40-80 px above the finger so it stays visible.
- **Virtual sticks.** Radial dead zone 8-15% of the stick radius with rescale: `v = max(0, |x| - dz) / (1 - dz) × sign(x)`; saturate at 90-95%; response exponent 1.3-2.0 (`v^p`) for finer control near the centre; let a floating stick follow the thumb beyond its radius so it never needs to travel back.
- **Multi-touch and cancels.** Track fingers by index; ignore touches in a 16-24 dp edge margin (palms, system gestures); one finger owns one gesture until lift. Treat `touch cancelled` (calls, notifications, system gestures) as release without effect and return the item to its origin with an ease-out.

## 4. The 12 animation principles in games

Frank Thomas and Ollie Johnston's *The Illusion of Life* (1981) lists twelve principles of Disney animation. Applied to games, each becomes a rule about readable motion.

| Principle | Gameplay use | UI use | Starting timing |
|---|---|---|---|
| Squash and stretch | Deform on launch and landing, volume kept | Button press, coin pop | 80-250 ms |
| Anticipation | Enemy wind-up and telegraph; player crouch before a jump (2-3 frames) | Button depresses before release, chest inhales | 60-150 ms (at most 50 ms player-side) |
| Staging | One hero element per event, strong silhouette, camera and light direct the eye | One primary action per screen, dim the background | rule, not timing |
| Straight ahead and pose to pose | Physics and procedural motion versus authored key poses | Tweens between authored key states | n/a |
| Follow-through and overlapping action | Tails, capes, trails and camera lag settle after the body stops | List items settle after their container | 100-300 ms lag |
| Slow in and slow out | Ease-out for caused motion, ease-in-out for ambient motion | Transitions and panels | section 5 |
| Arcs | Thrown and flung things curve; fly-to-counter flights use Béziers | Reward flights, menu swooshes | n/a |
| Secondary action | Dust, sparks and glints that support the main action | Counter bump while coins land | starts 30-80 ms after the main action |
| Timing | Duration conveys mass and intent: heavy means longer wind-up and slower recovery | Duration scales with importance | section 5 |
| Exaggeration | Push scale, speed and overshoot past realism, keeping it readable | Overshoot, big reward pops | 1.2-1.4× scale |
| Solid drawing | Consistent volume, shading and perspective | Consistent shadows and elevation | n/a |
| Appeal | Distinct silhouette, readable emotion | Charming micro-interactions | n/a |

In this skill: anticipation, impact, recovery is the shape of every event; follow-through and secondary action are where juice lives; staging is the readability budget; timing and exaggeration scale with the significance tier.

## 5. Easing, springs, timing and the Unity helpers

### 5.1 Easing formulas

`t` runs 0 to 1. "Out" means fast start, slow end (decelerating): the default for anything the player caused.

| Curve | f(t) | Use |
|---|---|---|
| Out quad | `1 - (1 - t)²` | Default response, fades, counters |
| Out cubic | `1 - (1 - t)³` | Rises, slides, floating numbers |
| In cubic | `t³` | Exits, things absorbed by the counter |
| In-out sine | `-(cos(πt) - 1) / 2` | Ambient loops, breathing |
| Out back | `1 + (s + 1)(t - 1)³ + s(t - 1)²`; s = 1.70158 gives about 10% overshoot, 1.0 about 4% | Pop-ins, panels, rewards |
| Out elastic | `2^(-10t) · sin((10t - 0.75) · 2π/3) + 1`, with f(0) = 0 and f(1) = 1 | Squash recovery, springy settles (sparingly) |
| Out bounce | Piecewise parabolas, n = 7.5625, d = 2.75 | Drops and landings |
| Exponential smoothing | `x += (target - x) · (1 - e^(-k·dt))`; half-life = ln 2 / k (k = 20 gives 35 ms, k = 40 gives 17 ms) | Follow, drag, camera; frame-rate independent |
| Damped spring | `a = -k(x - target) - c·v`, ζ = c / (2√k) | Lively follow; overshoot about 37% at ζ 0.3, 16% at 0.5, 5% at 0.7, none at 1 |

The named curves come from Robert Penner's easing equations (early 2000s); easings.net plots them. In Godot, `Tween.TRANS_QUAD`, `CUBIC`, `SINE`, `BACK`, `ELASTIC`, `BOUNCE` and `SPRING` with `EASE_IN`, `EASE_OUT` and `EASE_IN_OUT` cover the table; evaluate a curve by hand with `Tween.interpolate_value(0.0, 1.0, t, 1.0, Tween.TRANS_BACK, Tween.EASE_OUT)`. Godot's back overshoot is fixed, so use a custom `out_back` for a tunable one (catalog technique 10). In Unity use the `Ease` class below, an `AnimationCurve`, or DOTween or PrimeTween.

### 5.2 Timing table

Starting durations; scale with mass (bigger is slower) and frequency (more frequent is shorter). All in seconds in code.

| Event | Duration | Curve | Notes |
|---|---|---|---|
| Button press / release | 50-80 / 80-120 ms | Out quad / out back | Acknowledge on the next frame |
| Hit flash | 40-80 ms | Linear or out quad | 2-3 frames |
| Anticipation | 60-150 ms | In-out sine | At most 50 ms for player-initiated actions |
| Squash recovery | 150-250 ms | Out elastic or out back | |
| Camera kick / zoom punch | 120-220 / 150-250 ms | Spring / out quad | |
| Shake | 0.3-0.8 s total | Trauma decay | Linear drain, squared output |
| Hit-stop | 30-120 ms (finisher 150-200) | n/a | Cap one per 150 ms |
| Pop-in / panel open | 150-250 ms | Out back | Close: 120-160 ms, in cubic |
| Toast or banner | 250 ms in, hold 1.2-2.5 s, 200 ms out | Out cubic / in cubic | Queue, do not stack |
| Count-up | 0.4-1.5 s | Out quad | Skippable with a tap |
| Coin fly-to-counter | 0.45-0.7 s | In quad on a Bézier | Stagger 30-60 ms |
| Reveal sequence | 1.2-2.0 s | Mixed | Skippable; repeats 0.6 s |
| Screen transition | 200-300 ms | In-out sine or out cubic | Never block input longer than this |

Rules: durations are time, not frames; UI and feedback run on unscaled time so hit-stop and slow-motion do not freeze menus; overlapping events restart or sum, they never queue behind each other; anything over 1 s is skippable.

### 5.3 Unity helpers (`Fx` and `Ease`)

The catalog's Unity snippets assume these. Each call starts one coroutine: fine for feedback, pool or batch for hundreds of simultaneous effects.

```csharp
using System; using System.Collections; using UnityEngine;
public static class Fx {
    // Calls step(ease(t)) for dur seconds, then done(). Returns the coroutine so callers can StopCoroutine it.
    public static Coroutine Run(MonoBehaviour host, float dur, Action<float> step, Func<float, float> ease = null, bool unscaled = false, Action done = null) {
        if (ease == null) ease = Ease.Linear;
        return host.StartCoroutine(Loop(dur, step, ease, unscaled, done));
    }
    public static Coroutine After(MonoBehaviour host, float sec, Action act, bool unscaled = false) => host.StartCoroutine(Wait(sec, act, unscaled));
    static IEnumerator Loop(float dur, Action<float> step, Func<float, float> ease, bool unscaled, Action done) {
        for (float e = 0f; e < dur; e += unscaled ? Time.unscaledDeltaTime : Time.deltaTime) { step(ease(e / dur)); yield return null; }
        step(ease(1f)); done?.Invoke();
    }
    static IEnumerator Wait(float sec, Action act, bool unscaled) {
        if (unscaled) yield return new WaitForSecondsRealtime(sec); else yield return new WaitForSeconds(sec);
        act();
    }
}
public static class Ease {
    public static float Linear(float t) => t;
    public static float OutQuad(float t) => 1f - (1f - t) * (1f - t);
    public static float InQuad(float t) => t * t;
    public static float OutCubic(float t) => 1f - Mathf.Pow(1f - t, 3f);
    public static float InCubic(float t) => t * t * t;
    public static float InOutSine(float t) => -(Mathf.Cos(Mathf.PI * t) - 1f) / 2f;
    public static float OutBack(float t) => OutBack(t, 1.70158f);
    public static float OutBack(float t, float s) { float u = t - 1f; return 1f + (s + 1f) * u * u * u + s * u * u; }
    public static float OutElastic(float t) => t <= 0f ? 0f : t >= 1f ? 1f : Mathf.Pow(2f, -10f * t) * Mathf.Sin((t * 10f - 0.75f) * (2f * Mathf.PI / 3f)) + 1f;
    public static float OutBounce(float t) {
        const float n = 7.5625f, d = 2.75f;
        if (t < 1f / d) return n * t * t;
        if (t < 2f / d) { t -= 1.5f / d; return n * t * t + 0.75f; }
        if (t < 2.5f / d) { t -= 2.25f / d; return n * t * t + 0.9375f; }
        t -= 2.625f / d; return n * t * t + 0.984375f;
    }
}
```

## 6. Haptics

### 6.1 Principles

- **Semantic, not literal.** A vocabulary of four to six patterns (selection tick, impact scaled by magnitude, success, failure, charge ramp), not one buzz per event. Short and sparse: 10-45 ms pulses, at most about 10 per second, nothing continuous beyond roughly 0.3 s except an explicit charge ramp.
- **Paired and redundant.** Always with a visual and an audio cue; haptics alone carry no information because many players turn them off and hardware differs.
- **Proportional and optional.** Amplitude follows tier and magnitude; ship an in-game Off, Low, Normal setting on top of the OS switch.
- **Hardware varies.** Older eccentric-rotating-mass motors give on-off pulses with a duration only; linear actuators give amplitude and sharpness; some devices have none. Query capability and degrade to a simple pulse or silence.

### 6.2 iOS

- `UIImpactFeedbackGenerator` (light, medium, heavy, soft, rigid; `impactOccurred(intensity:)` on iOS 13 and later), `UISelectionFeedbackGenerator` and `UINotificationFeedbackGenerator` (success, warning, error) are system-tuned and the best default. Keep one instance per generator and call `prepare()` shortly before the expected event to cut latency.
- Core Haptics (`CHHapticEngine`, iOS 13 and later) builds custom patterns from transient and continuous events with intensity and sharpness, parameter curves, optional audio events and AHAP files. Check `CHHapticEngine.capabilitiesForHardware().supportsHaptics`, start the engine ahead of use and handle its stop and reset handlers.
- Neither Godot nor Unity exposes these directly: bridge through a native plugin (Unity `[DllImport("__Internal")]`, Godot an iOS plugin or GDExtension) behind the same semantic interface.

```swift
let impact = UIImpactFeedbackGenerator(style: .medium); impact.prepare(); impact.impactOccurred(intensity: 0.7)
UINotificationFeedbackGenerator().notificationOccurred(.success)
let engine = try CHHapticEngine(); try engine.start()  // keep the engine and its handlers alive
let tap = CHHapticEvent(eventType: .hapticTransient, parameters: [
    CHHapticEventParameter(parameterID: .hapticIntensity, value: 0.8),
    CHHapticEventParameter(parameterID: .hapticSharpness, value: 0.4)], relativeTime: 0)
try engine.makePlayer(with: CHHapticPattern(events: [tap], parameters: [])).start(atTime: CHHapticTimeImmediate)
```

### 6.3 Android

- `Vibrator` (or `VibratorManager` on API 31 and later) with `VibrationEffect`: `createOneShot(ms, amplitude)` (API 26, amplitude 1-255, check `hasAmplitudeControl()`), `createWaveform`, `createPredefined` with `EFFECT_CLICK`, `EFFECT_TICK`, `EFFECT_HEAVY_CLICK`, `EFFECT_DOUBLE_CLICK` (API 29), and `VibrationEffect.Composition` primitives such as click, tick, thud and rises (API 30; query `areAllPrimitivesSupported`). `vibrate` needs the normal `VIBRATE` permission.
- `View.performHapticFeedback(HapticFeedbackConstants.*)` (`CONFIRM`, `REJECT`, `CLOCK_TICK`, `CONTEXT_CLICK`, `VIRTUAL_KEY`, newer constants on recent API levels) needs no permission and follows the user's touch-feedback setting: best for UI ticks.
- Actuators and tuning differ widely between OEMs; the same amplitude can feel faint or harsh. Test the lowest tier and at least two OEMs.

```kotlin
val vib = context.getSystemService(Vibrator::class.java)  // API 31+: VibratorManager.defaultVibrator
if (vib.hasAmplitudeControl()) vib.vibrate(VibrationEffect.createOneShot(25, 180))
else vib.vibrate(VibrationEffect.createPredefined(VibrationEffect.EFFECT_CLICK))  // API 29+; a plain duration below that
view.performHapticFeedback(HapticFeedbackConstants.CONFIRM)  // no permission, follows the system setting
```

### 6.4 Godot and Unity layer

Game code calls only these semantic functions; they own the 45 ms rate limit, the user's strength setting and the platform call. Godot uses `Input.vibrate_handheld(duration_ms, amplitude)` (Android needs the Vibrate permission ticked in the export preset). Unity's `Handheld.Vibrate()` has no duration or amplitude control and is a poor fit: call the platform APIs through `AndroidJavaObject` and a small iOS native plugin, and add `android.permission.VIBRATE` to a custom manifest if you call the vibrator directly (verify what your Unity version adds automatically).

```gdscript
extends Node  # autoload "Haptics"
var _last_ms: int = 0
func pulse(ms: int, amp: float) -> void:
	var now: int = Time.get_ticks_msec()
	if FeelSettings.haptics <= 0.0 or now - _last_ms < 45:
		return
	_last_ms = now
	Input.vibrate_handheld(ms, clampf(amp * FeelSettings.haptics, 0.05, 1.0))
func tick() -> void: pulse(12, 0.35)
func impact(k: float) -> void: pulse(int(lerpf(15.0, 45.0, k)), lerpf(0.35, 1.0, k))
func fail() -> void: pulse(90, 0.8)
func success() -> void:
	pulse(25, 0.6)
	get_tree().create_timer(0.09, true, false, true).timeout.connect(func() -> void: pulse(35, 0.9))
```

```csharp
public static class Haptics {
    public static MonoBehaviour Host;  // any persistent MonoBehaviour, set at boot
    static float last = -1f;
    public static void Pulse(int ms, float amp) {
        float now = Time.realtimeSinceStartup;
        if (FeelSettings.HapticsScale <= 0f || now - last < 0.045f) return;
        last = now; amp = Mathf.Clamp01(amp * FeelSettings.HapticsScale);
#if UNITY_ANDROID && !UNITY_EDITOR
        using var player = new AndroidJavaClass("com.unity3d.player.UnityPlayer");
        using var act = player.GetStatic<AndroidJavaObject>("currentActivity");
        using var vib = act.Call<AndroidJavaObject>("getSystemService", "vibrator");
        using var fx = new AndroidJavaClass("android.os.VibrationEffect");  // API 26+; below that use vib.Call("vibrate", (long)ms)
        using var effect = fx.CallStatic<AndroidJavaObject>("createOneShot", (long)ms, Mathf.Max(1, Mathf.RoundToInt(amp * 255f)));
        vib.Call("vibrate", effect);
#elif UNITY_IOS && !UNITY_EDITOR
        _HapticImpact(amp);  // native plugin wrapping UIImpactFeedbackGenerator or Core Haptics
#endif
    }
#if UNITY_IOS && !UNITY_EDITOR
    [System.Runtime.InteropServices.DllImport("__Internal")] static extern void _HapticImpact(float intensity);
#endif
    public static void Tick() => Pulse(12, 0.35f);
    public static void Impact(float k) => Pulse(Mathf.RoundToInt(Mathf.Lerp(15f, 45f, k)), Mathf.Lerp(0.35f, 1f, k));
    public static void Fail() => Pulse(90, 0.8f);
    public static void Success() { Pulse(25, 0.6f); Fx.After(Host, 0.09f, () => Pulse(35, 0.9f), true); }
}
```

### 6.5 Settings and accessibility

One settings object multiplies every channel; that is what makes reduced motion, a haptics slider and a flash limit possible without touching individual effects.

- Expose haptics (Off, Low, Normal), screen shake (0-100%), reduce flashing, reduce motion (swap shake, zoom and parallax for fades or small pulses, skip hit-stop) and particle density (Low, Medium, High); persist them with the other settings.
- Default from the OS on first run (iOS `UIAccessibility.isReduceMotionEnabled`; on Android a `Settings.Global.ANIMATOR_DURATION_SCALE` of 0 indicates the user removed animations; bridge natively where the engine has no API), and let the in-game setting override it.
- No more than three flashes in any one second (WCAG 2.3.1) and no large high-contrast flashing areas; prefer a tint over white when in doubt.
- Never carry information only in haptics, flashes or colour: pair a haptic with a visual and an audio cue, add a shape or icon to colour. Test with every option off and every option at minimum: the game must stay readable and the outcomes identical.

```gdscript
extends Node  # autoload "FeelSettings": every effect multiplies by these; 0.0 switches the channel off
var shake: float = 1.0; var flash: float = 1.0; var haptics: float = 1.0; var particles: float = 1.0; var hitstop: float = 1.0
func apply_reduce_motion(on: bool) -> void:
	shake = 0.2 if on else 1.0; flash = 0.3 if on else 1.0; hitstop = 0.0 if on else 1.0; particles = 0.5 if on else 1.0
```

```csharp
public static class FeelSettings {  // every effect multiplies by these; 0 switches the channel off
    public static float Shake = 1f, Flash = 1f, HapticsScale = 1f, ParticleScale = 1f, HitStopScale = 1f;
    public static void ApplyReduceMotion(bool on) { Shake = on ? 0.2f : 1f; Flash = on ? 0.3f : 1f; HitStopScale = on ? 0f : 1f; ParticleScale = on ? 0.5f : 1f; }
}
```

### 6.6 Pairing haptics with audio and visuals

- Fire the haptic and the audio transient in the same frame; if the haptic feels late, start it up to one frame earlier. Actuators have their own onset delay, so judge on the device, not in the editor.
- Match character: click and tick sounds pair with short sharp pulses, thuds with longer softer ones, sustained sounds with a continuous event only in a charge ramp.
- Add haptics only for sounds that correspond to touch or achievement (selection, impact, success, failure), never for ambience or UI whooshes.
- Long or rapid pulses can be audible through the speaker in quiet scenes; keep them short. Silence before a reveal can pair with a charge ramp; the reveal lands with audio, flash and impact haptic together.

## 7. Volatile facts (as of Oct 2026 — verify before relying)

| Fact | Source |
|---|---|
| Feedback generator styles, `impactOccurred(intensity:)` and Core Haptics need iOS 13 or later; capability check is `supportsHaptics` | https://developer.apple.com/documentation/uikit/uifeedbackgenerator and https://developer.apple.com/documentation/corehaptics |
| `VibrationEffect` one-shot (API 26), predefined effects (API 29), composition primitives (API 30); newer `HapticFeedbackConstants` on recent API levels | https://developer.android.com/reference/android/os/VibrationEffect and https://developer.android.com/reference/android/view/HapticFeedbackConstants |
| Godot `Input.vibrate_handheld(duration_ms, amplitude)`: amplitude documented from 4.3, Android needs the Vibrate permission in the export preset, iOS duration support depends on OS version; `Input.use_accumulated_input` | https://docs.godotengine.org/en/stable/classes/class_input.html |
| Unity `Handheld.Vibrate()` takes no duration or amplitude | https://docs.unity3d.com/ScriptReference/Handheld.Vibrate.html |
| WCAG 2.3.1: no more than three flashes in any one-second period | https://www.w3.org/WAI/WCAG22/Understanding/three-flashes-or-below-threshold.html |
| Touch slop, long-press and double-tap timeouts are platform values (Android `ViewConfiguration`): read them instead of hard-coding | https://developer.android.com/reference/android/view/ViewConfiguration |
