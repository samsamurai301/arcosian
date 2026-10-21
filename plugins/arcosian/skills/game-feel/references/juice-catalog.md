# Juice catalog

Forty-five juice techniques with typical starting parameters and compact Godot 4 (typed GDScript, `Tween`) and Unity 6 (C# 9) snippets, grouped by channel: camera and time, object motion, visual effects, numbers and UI, audio, haptics. Use it after the response and the latency are right (`references/input-animation-haptics.md`), and scale every amplitude by the event's tier from the significance ladder in `SKILL.md` (micro 0.25, minor 0.5, major 1.0, hero 1.5). Each entry ends with the lowest tier that normally earns it.

## Contents

1. Conventions  2. Camera and time (1-7)  3. Object motion (8-19)  4. Visual effects (20-26)  5. Numbers and UI (27-35)  6. Audio (36-39)  7. Haptics (40-45)

## 1. Conventions

- Parameters are starting values to tune on a release build on a real device, not constants. Durations are seconds in code and ms in prose.
- Godot snippets run inside a `Node`: `create_tween()` binds the tween to the node and stops it when the node is freed. Unity snippets use the small `Fx.Run`, `Fx.After` and `Ease` helpers and the `Haptics` layer from `references/input-animation-haptics.md` (sections 5 and 6); swap in DOTween or PrimeTween if the project already has one.
- `FeelSettings` is the single accessibility choke point (shake, flash, haptics, particles, hit-stop multipliers) defined in section 6.5 of the same reference. Every effect reads it.
- Kill or replace the previous tween on a property before starting another; combine competing contributions (shake plus kick) by summing offsets in one place. Each code block is a set of independent snippets tagged with their technique number (the trauma camera class excepted), not one script. Snippets use short names (`n` a Node2D, `tr` a Transform, `a` and `b` start and end points, `k` a 0-1 magnitude, `i` a batch index) and omit declarations; numbers in the code are the first value in each range. Verify engine signatures against the class reference if a call fails.

## 2. Camera and time

- **1. Trauma shake.** Add trauma 0.1-0.2 light, 0.3-0.5 heavy, 1.0 catastrophe; decay 1.0-2.0 per second; displacement = trauma² (or trauma³) × max; max offset 2-3% of screen height, max roll 2-4 degrees; noise sampled at 15-20 Hz, never fresh random numbers per frame; shake a camera pivot, not the follow target; run on unscaled time so it plays through hit-stop (Cinemachine: `CinemachineImpulseSource.GenerateImpulse`). Tier: minor.
- **2. Camera kick.** 6-16 px (0.1-0.25 units) opposite the shot or along the hit direction, return in 120-220 ms with a spring-like ease, summed with the shake through `kick_offset`; roll only for heavy hits. Tier: minor.
- **3. Zoom punch.** 2-5% in (6-10% for finishers), ease-out back to 1.0 in 150-250 ms; never pair a heavy zoom with a heavy shake. Tier: major.

```gdscript
extends Camera2D  # 1 trauma shake owns offset and rotation; the 2 kick offset is summed in the same place
var trauma: float = 0.0; var kick_offset: Vector2 = Vector2.ZERO
var _t: float = 0.0; var _noise := FastNoiseLite.new()
func _ready() -> void:
	_noise.frequency = 1.0; ignore_rotation = false
func add_trauma(a: float) -> void:
	trauma = minf(trauma + a * FeelSettings.shake, 1.0)
func _process(delta: float) -> void:
	var dt: float = delta / maxf(Engine.time_scale, 0.001)  # unscaled, so it plays through hit-stop
	_t += dt * 18.0; trauma = maxf(trauma - 1.4 * dt, 0.0)  # 18 samples per second, decay 1.4 per second
	var s: float = trauma * trauma
	offset = Vector2(_noise.get_noise_2d(_t, 0.0), _noise.get_noise_2d(_t, 91.0)) * 48.0 * s + kick_offset  # 48 px max
	rotation = _noise.get_noise_2d(_t, 183.0) * 0.05 * s  # 0.05 rad max
func kick(dir: Vector2) -> void: create_tween().tween_property(self, "kick_offset", Vector2.ZERO, 0.18).from(dir.normalized() * 10.0).set_trans(Tween.TRANS_SPRING).set_ease(Tween.EASE_OUT)  # 2 (from() sets the start value)
func punch() -> void: create_tween().tween_property(self, "zoom", Vector2.ONE, 0.2).from(Vector2.ONE * 1.04).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)  # 3
```

```csharp
public class TraumaShake : MonoBehaviour {  // 1: put on a child pivot of the camera rig
    public Vector3 kickOffset; float trauma, t;
    public void AddTrauma(float a) => trauma = Mathf.Min(trauma + a * FeelSettings.Shake, 1f);
    void LateUpdate() {
        float dt = Time.unscaledDeltaTime;  // plays through hit-stop
        t += dt * 18f; trauma = Mathf.Max(trauma - 1.4f * dt, 0f);
        float s = trauma * trauma;
        float N(float seed) => Mathf.PerlinNoise(t, seed) * 2f - 1f;
        transform.localPosition = new Vector3(N(0.5f), N(17.3f), 0f) * 0.35f * s + kickOffset;  // 0.35 units max
        transform.localRotation = Quaternion.Euler(0f, 0f, N(41.9f) * 3f * s);                  // 3 degrees max
    }
}
// 2 camera kick and 3 zoom punch (orthographic camera), called from a script holding `shake` and `cam`
var k0 = (Vector3)(dir.normalized * 0.15f); Fx.Run(this, 0.18f, u => shake.kickOffset = Vector3.LerpUnclamped(k0, Vector3.zero, u), Ease.OutElastic, true);
float z = cam.orthographicSize; Fx.Run(this, 0.2f, u => cam.orthographicSize = Mathf.Lerp(z * 0.96f, z, u), Ease.OutQuad, true);
```

- **4. Hit-stop.** Light hit 30-60 ms, heavy 70-120 ms, finisher up to 150-200 ms; time scale 0.0-0.05; ignore requests while slow-motion or another stop is active; skip when the event fires faster than about 5 per second; audio, shake and flash keep running through the freeze. To freeze only the two actors involved, set their `AnimationPlayer.speed_scale` or `Animator.speed` to 0 instead. Tier: minor (heavy hits).
- **5. Slow-motion ramp.** Ramp in 40-80 ms to 0.2-0.4, hold 0.2-0.6 s of real time, ramp out over 150-300 ms with ease-out; for run-ending moments (last enemy, near miss, perfect timing); drop music pitch or low-pass only if the fantasy wants it; never during timing-critical input. Tier: hero.

```gdscript
func hit_stop(sec: float) -> void:  # 4 (service or autoload node)
	if Engine.time_scale < 1.0 or sec <= 0.0: return
	Engine.time_scale = 0.05
	await get_tree().create_timer(sec * FeelSettings.hitstop, true, false, true).timeout  # last argument ignores time scale
	Engine.time_scale = 1.0
func slow_motion(speed: float = 0.3, hold: float = 0.4) -> void:  # 5
	var tw := create_tween().set_ignore_time_scale(true)
	tw.tween_property(Engine, "time_scale", speed, 0.06)
	tw.tween_interval(hold)
	tw.tween_property(Engine, "time_scale", 1.0, 0.25).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
```

```csharp
IEnumerator HitStop(float sec) {  // 4
    if (Time.timeScale < 1f || sec <= 0f) yield break;
    Time.timeScale = 0.05f;
    yield return new WaitForSecondsRealtime(sec * FeelSettings.HitStopScale);
    Time.timeScale = 1f;
}
void SlowMotion(float speed = 0.3f, float hold = 0.4f) =>  // 5
    Fx.Run(this, 0.06f, t => Time.timeScale = Mathf.Lerp(1f, speed, t), null, true, () =>
        Fx.After(this, hold, () => Fx.Run(this, 0.25f, t => Time.timeScale = Mathf.Lerp(speed, 1f, t), Ease.OutQuad, true), true));
```

- **6. Screen flash.** White or event-tinted overlay at 15-40% alpha decaying in 60-120 ms; never more than 3 flashes per second (WCAG 2.3.1) and none when "reduce flashing" is on; tint non-damaging events; the overlay sits above the HUD and below popups. Tier: major.
- **7. Post-process pulse.** Vignette or chromatic aberration 0 → 0.4-0.7 → 0 over 150-300 ms for damage, low health or big wins; one full-screen pass at a time; it costs fill rate on low tiers, so gate by device tier or fake the vignette with an overlay sprite. Tier: major.

```gdscript
flash.color = Color(1.0, 1.0, 1.0, 0.3 * FeelSettings.flash); create_tween().tween_property(flash, "color:a", 0.0, 0.1)  # 6 (flash: ColorRect)
create_tween().tween_method(func(v: float) -> void: mat.set_shader_parameter("amount", v), 0.6, 0.0, 0.25)  # 7 (mat: full-screen ShaderMaterial)
```

```csharp
float a0 = 0.3f * FeelSettings.Flash; Fx.Run(this, 0.1f, t => cg.alpha = a0 * (1f - t), null, true);  // 6 (cg: CanvasGroup overlay)
if (volume.profile.TryGet(out ChromaticAberration ca)) Fx.Run(this, 0.25f, t => ca.intensity.Override(Mathf.Lerp(0.6f, 0f, t)), Ease.OutQuad, true);  // 7 (URP Volume)
```

## 3. Object motion

- **8. Squash and stretch.** Stretch 1.15-1.35 along travel, squash 0.7-0.85 on contact, volume kept (`sy = 1/sx`), recover in 150-250 ms with elastic or back ease; pivot at the contact point (feet), not the centre; stay below about 1.5 or it reads as rubber. Tier: micro.
- **9. Anticipation.** Enemies and heavy attacks: 60-150 ms visible wind-up (opposite direction, 10-20% of the main move) plus a telegraph; player-initiated actions: at most 2-3 frames, or input feels late. The effect or hitbox fires when the wind-up ends. Tier: minor.
- **10. Overshoot easing.** Back-out constant s: 1.0 gives about 4% overshoot, 1.2 about 5%, 1.70158 about 10%, 2.0 about 13%. Use 1.0-1.7 for pop-ins, panels and rewards, settling in 120-250 ms. Ease-out for anything the player caused; ease-in only for things leaving or being absorbed. Tier: micro.
- **11. Damped spring.** Stiffness k 80-250, damping c = 2ζ√k with ζ 0.4-0.7 for lively (overshoot about 25% at 0.4, 5% at 0.7), ζ = 1 for none. UI follow, camera lag, tails, drag release; semi-implicit Euler with dt clamped to 1/30 s. Tier: micro.

```gdscript
sprite.scale = Vector2(1.3, 0.77); create_tween().tween_property(sprite, "scale", Vector2.ONE, 0.22).set_trans(Tween.TRANS_ELASTIC).set_ease(Tween.EASE_OUT)  # 8
var tw := create_tween()  # 9: wind-up, then the action, then recovery
tw.tween_property(sprite, "scale", Vector2(1.15, 0.85), 0.09).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
tw.tween_callback(launch)
tw.tween_property(sprite, "scale", Vector2.ONE, 0.2).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
static func out_back(t: float, s: float = 1.70158) -> float:  # 10: tunable overshoot, call inside tween_method
	var u: float = t - 1.0
	return 1.0 + (s + 1.0) * u * u * u + s * u * u
vel += (-k * (pos - target) - c * vel) * delta; pos += vel * delta  # 11: k = 160.0, c = 2.0 * 0.5 * sqrt(k)
```

```csharp
Fx.Run(this, 0.22f, t => tr.localScale = Vector3.LerpUnclamped(new Vector3(1.3f, 0.77f, 1f), Vector3.one, t), Ease.OutElastic);  // 8
Fx.Run(this, 0.09f, t => tr.localScale = Vector3.Lerp(Vector3.one, new Vector3(1.15f, 0.85f, 1f), t), Ease.OutQuad, false, Launch);  // 9: Launch() fires the action
Fx.Run(this, 0.3f, t => tr.position = Vector3.LerpUnclamped(a, b, t), t => Ease.OutBack(t, 1.2f));  // 10
vel += (-k * (pos - target) - c * vel) * dt; pos += vel * dt;  // 11: dt = Mathf.Min(Time.deltaTime, 1f / 30f)
```

- **12. Idle breathing and affordance pulse.** Breathing: scale ±2-4% or y ±2-4 px, 1.6-3 s period, sine in-out. Affordance pulse (claimable, valid target): ±6-8% at 1-1.5 Hz, only while the affordance is true. Many idle tweens cost battery: animate visible items only or drive it from a shader time uniform. Tier: micro.
- **13. Button press and release.** Press: scale 0.94-0.97 and 8-12% darker on the next frame, 50-80 ms ease-out; release: back-out to 1.0 in 80-120 ms; fire the action on release (on press for fast games), never after the animation; pivot at the centre. Tier: micro.
- **14. Spawn pop-in with stagger.** Scale 0 → 1 in 150-250 ms back-out, alpha 0 → 1 over the first 40%; stagger 30-60 ms per item, total stagger at most 400 ms; one spawn sound per batch, not per item. Tier: micro.
- **15. Destroy pop-out.** Swell to 1.1-1.2 in 50-80 ms, then shrink to 0 in 100-160 ms with ease-in back; spawn the burst at the swell peak; free or return to the pool at the end, never mid-tween. Tier: minor.

```gdscript
var br := create_tween().set_loops()  # 12
br.tween_property(sprite, "scale", Vector2.ONE * 1.03, 1.2).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
br.tween_property(sprite, "scale", Vector2.ONE, 1.2).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
button.pivot_offset = button.size / 2.0  # 13
button.button_down.connect(func() -> void: create_tween().tween_property(button, "scale", Vector2.ONE * 0.96, 0.06))
button.button_up.connect(func() -> void: create_tween().tween_property(button, "scale", Vector2.ONE, 0.1).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT))
n.scale = Vector2.ZERO  # 14
create_tween().tween_property(n, "scale", Vector2.ONE, 0.22).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT).set_delay(0.04 * i)
var po := create_tween()  # 15
po.tween_property(n, "scale", Vector2.ONE * 1.15, 0.07).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
po.tween_property(n, "scale", Vector2.ZERO, 0.13).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_IN)
po.tween_callback(n.queue_free)
```

```csharp
void Update() => tr.localScale = Vector3.one * (1f + 0.03f * Mathf.Sin(Time.time * Mathf.PI / 1.2f));  // 12: 2.4 s period
public void OnPointerDown(PointerEventData e) => Fx.Run(this, 0.06f, t => tr.localScale = Vector3.one * Mathf.Lerp(1f, 0.96f, t), Ease.OutQuad, true);  // 13
public void OnPointerUp(PointerEventData e) => Fx.Run(this, 0.1f, t => tr.localScale = Vector3.one * Mathf.LerpUnclamped(0.96f, 1f, t), Ease.OutBack, true);
tr.localScale = Vector3.zero; Fx.After(this, 0.04f * i, () => Fx.Run(this, 0.22f, t => tr.localScale = Vector3.LerpUnclamped(Vector3.zero, Vector3.one, t), Ease.OutBack));  // 14
Fx.Run(this, 0.2f, t => tr.localScale = Vector3.one * (t < 0.35f ? Mathf.Lerp(1f, 1.15f, t / 0.35f) : Mathf.Lerp(1.15f, 0f, Ease.InCubic((t - 0.35f) / 0.65f))), null, false, () => Release(gameObject));  // 15
```

- **16. Bounce landing.** Drop 0.5-1 tile heights with a bounce ease-out in 350-600 ms (or two bounces at 100% then 25% of the height); thud and dust on the first contact only; pair with a squash on contact. Tier: minor.
- **17. Reject wobble.** 3 horizontal cycles of ±6-10 px (or ±3 degrees) damped over 200-280 ms, with a short dull sound and an optional error haptic; it is the non-colour redundant cue for invalid; an invalid drop returns the item in 150-250 ms ease-out. Tier: micro.
- **18. Drag follow with tilt.** Smooth with `x += (target - x) × (1 - e^(-k·dt))`, k 20-40 per second (half-life 35-17 ms); pick-up lift 1.08-1.15 with a 4-8 px shadow offset in 60-80 ms; tilt = clamp(velocity.x × gain, ±10-12 degrees); hold the item 40-80 px above the finger so the thumb does not hide it; drop with ease-out back in 100-160 ms. Tier: micro.
- **19. Knockback with friction.** Impulse 300-600 px/s (4-8 units/s) decayed by friction 8-14 per second (stops in 150-300 ms); give the attacker 20-30% recoil; clamp against walls. Tier: minor.

```gdscript
create_tween().tween_property(n, "position:y", rest_y, 0.45).from(rest_y - 160.0).set_trans(Tween.TRANS_BOUNCE).set_ease(Tween.EASE_OUT)  # 16
create_tween().tween_method(func(t: float) -> void: n.position.x = x0 + sin(t * TAU * 3.0) * 8.0 * (1.0 - t), 0.0, 1.0, 0.25)  # 17
var prev: Vector2 = global_position  # 18 in _process; finger is the touch position
global_position = global_position.lerp(finger + Vector2(0.0, -64.0), 1.0 - exp(-30.0 * delta))
rotation = clampf((global_position.x - prev.x) / delta * 0.0006, -0.2, 0.2)
velocity = dir * 450.0  # 19 once, then every physics tick: velocity *= exp(-10.0 * delta); move_and_slide()
```

```csharp
Fx.Run(this, 0.45f, t => tr.localPosition = new Vector3(x, Mathf.LerpUnclamped(restY + 1.6f, restY, t), 0f), Ease.OutBounce);  // 16
Fx.Run(this, 0.25f, t => tr.localPosition = p0 + Vector3.right * Mathf.Sin(t * 6f * Mathf.PI) * 0.08f * (1f - t));  // 17
Vector3 prev = tr.position; tr.position = Vector3.Lerp(prev, finger + Vector3.up * 0.7f, 1f - Mathf.Exp(-30f * Time.deltaTime));  // 18
tr.rotation = Quaternion.Euler(0f, 0f, -Mathf.Clamp((tr.position.x - prev.x) / Time.deltaTime * 1.2f, -12f, 12f));
vel = dir * 5f;  // 19 once, then every tick: vel *= Mathf.Exp(-10f * Time.deltaTime); rb.MovePosition(rb.position + vel * Time.deltaTime);
```

## 4. Visual effects

- **20. Hit flash.** White or tint for 2-3 frames (40-80 ms), then ease back; implement as a shader mix, not `modulate` above 1 (HDR modulate is unreliable on mobile renderers); restart rather than stack; the material must be per-instance (Godot `resource_local_to_scene` or a duplicate; Unity MaterialPropertyBlock). Tier: micro.
- **21. Particle burst and dust puff.** 8-16 particles light, 20-40 heavy; lifetime 0.25-0.5 s; speed 120-300 px/s ±30%; size over life 1 → 0; one-shot, explosiveness 1; additive for energy, alpha for dust. Dust puff on landing or turning: 4-6 soft particles, 0.25-0.4 s, 20-60 px/s, only above a fall-speed threshold. Pool and pre-warm; scale the count by magnitude k; cap live particles per tier. Tier: minor.
- **22. Debris shards.** 6-12 shards from one particle system with a texture sheet of 4-8 shapes, velocity 150-350 px/s with an upward bias, gravity 600-1200 px/s², spin ±360 degrees per second, lifetime 0.4-0.8 s, fade over the last 30%; a RigidBody per shard is too costly on mobile. Tier: major.
- **23. Trail and afterimage.** Trail 0.12-0.25 s long, 8-16 points, width and alpha taper to 0. Dash afterimages: a ghost sprite every 30-50 ms fading over 150-250 ms, 3-5 alive. Stop emitting when not moving; clear after teleports. Tier: minor.

```gdscript
mat.set_shader_parameter("flash", 1.0); create_tween().tween_property(mat, "shader_parameter/flash", 0.0, 0.08)  # 20
burst.global_position = p; burst.restart()  # 21 (CPUParticles2D or GPUParticles2D with one_shot = true)
debris.amount = 10; debris.lifetime = 0.6; debris.one_shot = true; debris.explosiveness = 1.0  # 22 (CPUParticles2D)
debris.direction = Vector2.UP; debris.spread = 90.0; debris.initial_velocity_min = 150.0; debris.initial_velocity_max = 350.0
debris.gravity = Vector2(0.0, 900.0); debris.angular_velocity_min = -360.0; debris.angular_velocity_max = 360.0; debris.restart()
trail.add_point(global_position)  # 23 (Line2D with top_level = true)
if trail.get_point_count() > 12: trail.remove_point(0)
```

```csharp
Fx.Run(this, 0.08f, t => { sr.GetPropertyBlock(mpb); mpb.SetFloat(FlashId, 1f - t); sr.SetPropertyBlock(mpb); });  // 20: FlashId = Shader.PropertyToID("_Flash")
ps.transform.position = p; ps.Emit(Mathf.RoundToInt(Mathf.Lerp(8f, 24f, k)));  // 21
debrisPs.transform.position = p; debrisPs.Emit(10);  // 22: shape, gravity modifier, rotation and size-over-lifetime live in the prefab
trail.time = 0.2f; trail.emitting = dashing;  // 23 (TrailRenderer)
```

- **24. Impact ring.** Ring scale 0.3 → 1.2-1.8 over 200-300 ms ease-out while alpha 0.8 → 0; one ring per impact, additive; for heavy hits and big merges; if it implies an area of effect, its final size must match the real radius. Tier: major.
- **25. Additive glow pulse.** Overlay or `Light2D` intensity 0 → 0.6-1.0 → 0, attack 60-90 ms, release 150-250 ms; colour from the event palette; one glow layer per object. Tier: minor.
- **26. Shine sweep.** A diagonal gradient band crosses an icon in 400-600 ms, repeating every 3-6 s to mark claimable or premium items; implement as a shader uniform (progress or time), not a separate animated sprite. Tier: micro.

```gdscript
ring.scale = Vector2.ONE * 0.3; ring.modulate.a = 0.8; var rg := create_tween().set_parallel(true)  # 24
rg.tween_property(ring, "scale", Vector2.ONE * 1.5, 0.25).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
rg.tween_property(ring, "modulate:a", 0.0, 0.25)
var gl := create_tween()  # 25 (glow: sprite with an additive CanvasItemMaterial)
gl.tween_property(glow, "modulate:a", 0.8, 0.07)
gl.tween_property(glow, "modulate:a", 0.0, 0.22).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
var sh := create_tween().set_loops()  # 26
sh.tween_property(mat, "shader_parameter/progress", 1.0, 0.5).from(0.0).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
sh.tween_interval(4.0)
```

```csharp
Fx.Run(this, 0.25f, t => { ringTr.localScale = Vector3.one * Mathf.Lerp(0.3f, 1.5f, t); ringSr.color = new Color(1f, 1f, 1f, 0.8f * (1f - t)); }, Ease.OutQuad);  // 24
Fx.Run(this, 0.3f, t => glow.intensity = 0.8f * (t < 0.25f ? t / 0.25f : 1f - Ease.OutQuad((t - 0.25f) / 0.75f)));  // 25 (URP Light2D)
void OnEnable() => InvokeRepeating(nameof(Sweep), 1f, 4.5f);  // 26
void Sweep() => Fx.Run(this, 0.5f, t => mat.SetFloat(ProgressId, t), Ease.InOutSine);  // mat: per-instance copy assigned to the Image
```

## 5. Numbers and UI

- **27. Floating number.** Rise 40-70 px over 0.5-0.8 s, ease-out; pop scale 1.4 → 1.0 in 90 ms; x jitter ±12 px; fade over the last 0.2-0.3 s; merge numbers arriving within 100 ms when hits exceed 10 per second; outline for legibility; crits get shape or size, not only colour. Tier: micro.
- **28. Count-up.** Duration = clamp(0.4 + 0.2 × log10(delta), 0.4, 1.5) s with ease-out; tick sound at most 12-20 Hz, not per digit; a tap finishes instantly; the final value is in the accessibility label from the first frame. Tier: minor.
- **29. Counter bump.** Scale 1.0 → 1.15-1.25 → 1.0 in 100-140 ms on each arrival, restarting rather than stacking; pitch rises per arrival; optional text colour flash. Tier: micro.
- **30. Coin fly-to-counter.** 6-20 sprites (one sprite stands for N coins), stagger 30-60 ms, flight 0.45-0.7 s on a quadratic Bezier whose control point sits 15-25% of the distance off the straight line, ease-in (accelerating pull), scale 1 → 0.6; counter bump and tick on each arrival with rising pitch. Grant the currency in the model first: the flight is cosmetic and must survive interruption. Tier: minor.

```gdscript
l.scale = Vector2.ONE * 1.4; var fl := create_tween().set_parallel(true)  # 27 (l: Label)
fl.tween_property(l, "scale", Vector2.ONE, 0.09)
fl.tween_property(l, "position:y", l.position.y - 56.0, 0.6).set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
fl.tween_property(l, "modulate:a", 0.0, 0.2).set_delay(0.4)
fl.chain().tween_callback(l.queue_free)
create_tween().tween_method(func(v: float) -> void: label.text = str(int(v)), float(old_value), float(new_value), dur).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)  # 28
if _bump: _bump.kill()  # 29 (var _bump: Tween)
label.scale = Vector2.ONE * 1.2; _bump = create_tween()
_bump.tween_property(label, "scale", Vector2.ONE, 0.12).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
var fly := create_tween(); fly.tween_interval(0.04 * i)  # 30: a start, mid control point, b counter position
fly.tween_method(func(t: float) -> void: c.global_position = a.lerp(mid, t).lerp(mid.lerp(b, t), t), 0.0, 1.0, 0.55).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
fly.tween_callback(arrive.bind(c))  # arrive(): free the coin, bump the counter, tick
```

```csharp
rt.localScale = Vector3.one * 1.4f; Vector2 p0 = rt.anchoredPosition + new Vector2(Random.Range(-12f, 12f), 0f);  // 27 (TextMeshPro)
Fx.Run(this, 0.6f, t => { rt.anchoredPosition = p0 + Vector2.up * 56f * t; rt.localScale = Vector3.one * Mathf.Lerp(1.4f, 1f, Mathf.Clamp01(t * 6f)); cg.alpha = 1f - Mathf.Clamp01((t - 0.65f) / 0.35f); }, Ease.OutCubic, true, () => Release(gameObject));
Fx.Run(this, dur, t => label.text = Mathf.RoundToInt(Mathf.Lerp(oldValue, newValue, t)).ToString(), Ease.OutQuad, true);  // 28
if (bump != null) StopCoroutine(bump);  // 29 (Coroutine bump)
bump = Fx.Run(this, 0.12f, t => tr.localScale = Vector3.LerpUnclamped(Vector3.one * 1.2f, Vector3.one, t), Ease.OutBack, true);
Fx.After(this, 0.04f * i, () => Fx.Run(this, 0.55f, t => coin.position = Vector3.Lerp(Vector3.Lerp(a, mid, t), Vector3.Lerp(mid, b, t), t), Ease.InQuad, false, () => Arrive(coin)));  // 30
```

- **31. Lag bar.** The fill drops at once; a lighter ghost bar follows after a 0.25-0.35 s delay over 0.3-0.5 s with ease-out, showing how much just happened. Tier: micro.
- **32. Star sequence.** Stars or rating pips pop in 0.3-0.4 s apart with back-out 0 → 1 over 0.3 s; pitch +2 semitones and a haptic tick per star; skippable; the rating is decided before the animation. Tier: major.
- **33. Combo ladder.** Intensity k = clamp(ln(1 + chain) / ln(1 + cap), 0, 1) with cap 12-16; pitch +1 semitone per link (technique 37), particle count × (1 + k), trauma + 0.05 × k, tier call-outs at chain 3 / 6 / 10 / 15 (visual plus a short voice or sting); the chain resets after 1.5-2.5 s without a link and the meter drains rather than cutting. Tier: minor, escalating.
- **34. Panel transition.** Open: scale 0.9 → 1.0 with alpha 0 → 1 in 180-240 ms back-out (overshoot 2-3%), dim layer to 45-60% in 150 ms; close: 120-160 ms ease-in with no overshoot; list items stagger 30-50 ms up to 6 items; block input on the dimmer only, never for the whole animation; skip the animation on rapid reopen. Tier: micro.
- **35. Reveal sequence.** Total 1.2-2.0 s: inhale 250 ms (scale 0.95, music duck -9 dB), shake ramp 450 ms (roll ±1 → ±4 degrees, haptic charge ramp), then burst (flash 80 ms, particles, trauma 0.3, hit-stop 60 ms) and the item pops in with overshoot. A tap skips to the settled state in 300 ms; repeat opens use a 0.6 s version; rarity scales length and layers, never the outcome (decided before the animation). Tier: hero.

```gdscript
fill.value = v  # 31 (fill and ghost: ProgressBar)
create_tween().tween_property(ghost, "value", v, 0.4).set_delay(0.3).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
var st := create_tween().set_parallel(true)  # 32
for j in earned: st.tween_property(stars[j], "scale", Vector2.ONE, 0.3).from(Vector2.ZERO).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT).set_delay(0.35 * j)
var k: float = clampf(log(1.0 + chain) / log(1.0 + CHAIN_CAP), 0.0, 1.0)  # 33 (log() is the natural log)
player.pitch_scale = pow(2.0, mini(chain, 12) / 12.0); cam.add_trauma(0.05 * k)
panel.pivot_offset = panel.size / 2.0; panel.scale = Vector2.ONE * 0.9; panel.modulate.a = 0.0; var pt := create_tween().set_parallel(true)  # 34
pt.tween_property(panel, "scale", Vector2.ONE, 0.22).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
pt.tween_property(panel, "modulate:a", 1.0, 0.15)
var rv := create_tween()  # 35
rv.tween_property(chest, "scale", Vector2.ONE * 0.95, 0.25).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_OUT)
rv.tween_method(func(t: float) -> void: chest.rotation = sin(t * 60.0) * 0.07 * t, 0.0, 1.0, 0.45)
rv.tween_callback(burst_and_reveal)
```

```csharp
fill.fillAmount = v; float g0 = ghost.fillAmount;  // 31 (Image, Filled)
Fx.After(this, 0.3f, () => Fx.Run(this, 0.4f, t => ghost.fillAmount = Mathf.Lerp(g0, v, t), Ease.OutQuad, true), true);
for (int j = 0; j < earned; j++) { int s = j; Fx.After(this, 0.35f * s, () => { Fx.Run(this, 0.3f, t => stars[s].localScale = Vector3.LerpUnclamped(Vector3.zero, Vector3.one, t), Ease.OutBack, true); PlayStar(s); }, true); }  // 32
float k = Mathf.Clamp01(Mathf.Log(1f + chain) / Mathf.Log(1f + ChainCap));  // 33
src.pitch = Mathf.Pow(2f, Mathf.Min(chain, 12) / 12f); shake.AddTrauma(0.05f * k);
tr.localScale = Vector3.one * 0.9f; Fx.Run(this, 0.22f, t => { tr.localScale = Vector3.one * Mathf.LerpUnclamped(0.9f, 1f, t); cg.alpha = Mathf.Clamp01(t * 1.5f); }, Ease.OutBack, true);  // 34
IEnumerator Reveal() {  // 35
    yield return Fx.Run(this, 0.25f, t => tr.localScale = Vector3.one * Mathf.Lerp(1f, 0.95f, t), Ease.OutQuad, true);
    yield return Fx.Run(this, 0.45f, t => tr.localRotation = Quaternion.Euler(0f, 0f, Mathf.Sin(t * 60f) * 4f * t), null, true);
    BurstAndReveal();
}
```

## 6. Audio

- **36. Pitch variation and variants.** ±3-6% random pitch (0.94-1.06) per play, 3-6 variants chosen without immediate repeat, volume ±1-2 dB; no random pitch on tonal or musical cues or on ladders. Unity's `AudioSource.pitch` is per source, so overlapping one-shots need a small source pool. Tier: micro.
- **37. Semitone ladder.** Pitch ratio = 2^(n/12); +1 semitone per link, or pentatonic steps {0, 2, 4, 7, 9, 12} so rising chains stay consonant; cap at +12, then hold the top note and add layers; reset on break with a short drop sound; keep the sample's tonal centre in the music's key. Tier: minor.
- **38. Layered impact.** Three layers: transient click 5-20 ms (presence), body 80-200 ms (character), tail or sub 200-500 ms (weight, major tier and up). Detune each ±3%; small phone speakers reproduce little low bass, so put weight in a 100-200 Hz thump and in haptics; at most 3 voices per event. Tier: minor.
- **39. Duck and dropout.** Duck the music bus 6-9 dB over 30-60 ms, hold 150-400 ms, release over 400-800 ms on big hits and stingers; before a hero reveal drop the music 12-20 dB (or low-pass to about 1 kHz) for 150-300 ms, then land the hit; never duck SFX. Tier: major.

```gdscript
var r := AudioStreamRandomizer.new()  # 36
r.playback_mode = AudioStreamRandomizer.PLAYBACK_RANDOM_NO_REPEATS; r.random_pitch = 1.05; r.random_volume_offset_db = 1.5
for s in variants: r.add_stream(-1, s)
player.stream = r; player.play()
const STEPS: Array[int] = [0, 2, 4, 7, 9, 12]  # 37
player.pitch_scale = pow(2.0, STEPS[mini(chain, STEPS.size() - 1)] / 12.0)
click.play(); body.play()  # 38 (three AudioStreamPlayers)
if tier >= 2: sub.volume_db = lerpf(-24.0, -6.0, k); sub.play()
var bus: int = AudioServer.get_bus_index("Music")  # 39
var set_db := func(db: float) -> void: AudioServer.set_bus_volume_db(bus, db)
var dk := create_tween().set_ignore_time_scale(true)
dk.tween_method(set_db, 0.0, -9.0, 0.05); dk.tween_interval(0.25); dk.tween_method(set_db, -9.0, 0.0, 0.6)
```

```csharp
int i = clips.Length > 1 ? (last + Random.Range(1, clips.Length)) % clips.Length : 0; last = i;  // 36: never repeats the previous clip
src.pitch = Random.Range(0.95f, 1.05f); src.PlayOneShot(clips[i], Random.Range(0.85f, 1f));
static readonly int[] Steps = { 0, 2, 4, 7, 9, 12 };  // 37
src.pitch = Mathf.Pow(2f, Steps[Mathf.Min(chain, Steps.Length - 1)] / 12f);
click.PlayOneShot(clickClip); body.PlayOneShot(bodyClip);  // 38
if (tier >= 2) sub.PlayOneShot(subClip, Mathf.Lerp(0.06f, 0.5f, k));
Fx.Run(this, 0.05f, t => mixer.SetFloat("MusicVol", Mathf.Lerp(0f, -9f, t)), null, true, () =>  // 39 (AudioMixer exposed parameter)
    Fx.After(this, 0.25f, () => Fx.Run(this, 0.6f, t => mixer.SetFloat("MusicVol", Mathf.Lerp(-9f, 0f, t)), Ease.OutQuad, true), true));
```

## 7. Haptics

All six go through the semantic `Haptics` layer (`references/input-animation-haptics.md` section 6.4), which owns rate limiting, capability checks and the user's setting; game code never calls platform vibration APIs directly.

| # | Technique | Starting pattern | iOS / Android mapping |
|---|---|---|---|
| 40 | Selection tick | 10-15 ms at amplitude 0.3-0.4, only on discrete changes (cell boundary, detent, toggle), at most 10 per second | `UISelectionFeedbackGenerator` / `CLOCK_TICK` or `PRIMITIVE_TICK` |
| 41 | Impact pulse | 15-45 ms at amplitude 0.35-1.0 scaled by magnitude k, aligned with the audio transient, at most one per 45-60 ms | `UIImpactFeedbackGenerator` with intensity / `EFFECT_CLICK`, `EFFECT_HEAVY_CLICK` or `PRIMITIVE_THUD` |
| 42 | Success and fail patterns | Success: 25 ms then 35 ms with a 90 ms gap, rising amplitude. Fail: one 80-120 ms low-amplitude pulse or two firm ones. One pattern per event, never per item | `UINotificationFeedbackGenerator` success and error / `CONFIRM` and `REJECT` |
| 43 | Charge ramp | Pulses every 80 → 40 ms with amplitude 0.15 → 0.8 over the charge time, ending in an impact; cancel on release or pause; cap near 2 s | Repeated transients, or a Core Haptics curve / waveform or composition |
| 44 | Throttled item pulses | Coin showers and multi-hit: one pulse per 90-120 ms (about 10 per second); fold the rest into the next pulse one step stronger; never one per particle | Same calls; the rate limiter lives in the layer |
| 45 | Decaying pulse train | Explosions and big shakes: 3-5 pulses over 200-300 ms with amplitude 1.0 → 0.2; never a continuous buzz | Sequence of `Haptics.pulse` calls |

```gdscript
Haptics.tick(); Haptics.impact(k)  # 40 selection tick, 41 impact pulse (k in 0..1)
Haptics.success()  # 42 (Haptics.fail() for the failure pattern)
for j in 4: get_tree().create_timer(0.07 * j, true, false, true).timeout.connect(Haptics.impact.bind(1.0 - 0.2 * j))  # 45
```

```csharp
Haptics.Tick(); Haptics.Impact(k);  // 40 selection tick, 41 impact pulse (k in 0..1)
Haptics.Success();  // 42 (Haptics.Fail() for the failure pattern)
for (int j = 0; j < 4; j++) { int n = j; Fx.After(this, 0.07f * n, () => Haptics.Impact(1f - 0.2f * n), true); }  // 45
```
