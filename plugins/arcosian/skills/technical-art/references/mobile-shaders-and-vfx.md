# Mobile Shaders and VFX

A working library of the shaders and effects a mobile game actually ships: unlit, toon ramp, rim light, dissolve, flipbook, UV scroll, vertex wind, outlines and matcaps, each with the idea, the cost on a tile-based GPU, and implementation notes for both Godot (shading language) and Unity (Shader Graph and HLSL). The second half covers the language of VFX (anticipation, impact, follow-through, readability) and particle budgets by device tier. Snippets are minimal and written to be correct for Godot 4.x and Unity 6 URP; treat them as starting points to adapt, then profile on a real low-tier device. Cost numbers are relative heuristics, not measurements.

## Contents

1. [Mobile shader rules](#1-mobile-shader-rules)
2. [Cost model for shader decisions](#2-cost-model-for-shader-decisions)
3. [Unlit and vertex-colour shading](#3-unlit-and-vertex-colour-shading)
4. [Toon ramp shading](#4-toon-ramp-shading)
5. [Rim light and fresnel](#5-rim-light-and-fresnel)
6. [Matcap](#6-matcap)
7. [Dissolve](#7-dissolve)
8. [Flipbook animation](#8-flipbook-animation)
9. [UV scroll](#9-uv-scroll)
10. [Vertex wind and sway](#10-vertex-wind-and-sway)
11. [Outlines](#11-outlines)
12. [Shader variants, keywords and precision](#12-shader-variants-keywords-and-precision)
13. [Writing shaders with an agent safely](#13-writing-shaders-with-an-agent-safely)
14. [The VFX language](#14-the-vfx-language)
15. [VFX recipes](#15-vfx-recipes)
16. [Particle budgets](#16-particle-budgets)

---

## 1. Mobile shader rules

1. **Fragment cost beats vertex cost.** Mobile screens have many pixels and a limited fill budget; keep per-pixel math small. Move work to the vertex stage or to textures (lookup ramps) when the result is smooth across the surface.
2. **Few texture samples.** Each sample costs bandwidth. Budget roughly: opaque object 1-3 samples; particle 1-2; full-screen pass 1-2 (heuristics).
3. **No dependent texture reads in hot shaders** when avoidable (a texture lookup whose coordinates come from another lookup stalls on many mobile GPUs).
4. **Avoid `discard`/alpha test on big surfaces.** It can defeat early depth rejection on some GPUs. Prefer alpha-blended cutouts with a tight mesh, or use alpha-to-coverage where available.
5. **Avoid heavy transcendental functions per pixel** (pow with variable exponent, sin on large arrays, normalize chains). Precompute or use a lookup texture.
6. **Use the lowest precision that holds.** Colours and UVs can usually be half precision; positions and large UV ranges need full precision. See section 12.
7. **Bake what does not move.** Lighting, ambient occlusion and gradients baked into textures or vertex colours are free at runtime.
8. **Transparent overdraw is the main VFX cost.** Reduce screen coverage before reducing instruction count.
9. **Compile and profile on a low-tier device, not on the editor.** A shader that looks cheap on a desktop GPU can be the whole frame on a low-end phone.
10. **Keep a "lite" fallback** for every showpiece shader, switched by quality tier.

## 2. Cost model for shader decisions

| Feature | Relative cost | Notes |
|---|---|---|
| Unlit, one texture, vertex colour tint | 1 (baseline) | Default for stylized and UI-like 3D |
| Lambert / one directional light | 1.5-2 | Normals needed; baked light cheaper |
| Toon ramp (texture lookup) | 2 | One extra sample or a step function |
| Rim light | +0.5 | A dot product and a power or ramp |
| Matcap | 1.5 | One sample from view-space normal; replaces lights |
| Normal map | +1.5 | Extra sample and tangent-space math; avoid on small objects |
| Dissolve (noise + threshold) | +1 | Extra sample; discard or alpha |
| Soft particles (depth fade) | +2 | Reads depth texture; costly on some GPUs, avoid by default |
| Refraction / grab pass | high | Needs a copy of the screen; avoid on mobile unless one effect |
| Real-time shadows | high | Use blob shadows or baked shadows for most cases |
| Post-processing bloom | high | See `references/rendering-on-mobile.md` |

Read as a ladder: you may spend about 2-4 units on hero characters and about 1-2 on the many background objects; effects get their budget from coverage rather than complexity.

## 3. Unlit and vertex-colour shading

When to use: stylized games where lighting is painted or baked, flat-shaded low-poly, sprites, UI-like 3D, and any object far from the camera.

Godot (`spatial`):

```glsl
shader_type spatial;
render_mode unshaded, cull_back;
uniform sampler2D albedo_tex : source_color, filter_linear_mipmap, repeat_enable;
uniform vec4 tint : source_color = vec4(1.0);
void fragment() {
    vec4 t = texture(albedo_tex, UV);
    ALBEDO = t.rgb * tint.rgb * COLOR.rgb;   // COLOR carries vertex colour
    ALPHA = t.a * tint.a;
}
```

Unity (URP, HLSL, abridged):

```hlsl
Shader "Studio/UnlitVC" {
  Properties { _BaseMap("Base", 2D) = "white" {} _Tint("Tint", Color) = (1,1,1,1) }
  SubShader { Tags { "RenderType"="Opaque" "RenderPipeline"="UniversalPipeline" }
    Pass { Tags { "LightMode"="UniversalForward" }
      HLSLPROGRAM
      #pragma vertex vert
      #pragma fragment frag
      #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
      TEXTURE2D(_BaseMap); SAMPLER(sampler_BaseMap);
      CBUFFER_START(UnityPerMaterial) float4 _BaseMap_ST; half4 _Tint; CBUFFER_END
      struct A { float4 pos:POSITION; float2 uv:TEXCOORD0; half4 col:COLOR; };
      struct V { float4 pos:SV_POSITION; float2 uv:TEXCOORD0; half4 col:COLOR; };
      V vert(A a){ V v; v.pos=TransformObjectToHClip(a.pos.xyz); v.uv=TRANSFORM_TEX(a.uv,_BaseMap); v.col=a.col; return v; }
      half4 frag(V v):SV_Target { return SAMPLE_TEXTURE2D(_BaseMap,sampler_BaseMap,v.uv) * _Tint * v.col; }
      ENDHLSL } } }
```

The `CBUFFER` block keeps the shader compatible with the SRP Batcher, which lowers CPU cost per draw. In Shader Graph the equivalent is an Unlit graph with Sample Texture 2D multiplied by Vertex Color and a colour property.

Tip: put shading information in vertex colours (ambient occlusion in R, gradient in G, wind weight in B) so one atlas texture serves many assets.

## 4. Toon ramp shading

Idea: quantize lighting with a ramp lookup so that light becomes two or three flat bands. Looks distinctive, stays readable, and is cheap if the ramp is a tiny texture or a `step`.

Godot:

```glsl
shader_type spatial;
render_mode diffuse_toon, specular_disabled;   // built-in toon diffuse model
uniform sampler2D albedo_tex : source_color;
uniform sampler2D ramp : source_color, filter_nearest, repeat_disable;
void fragment() { ALBEDO = texture(albedo_tex, UV).rgb; }
void light() {
    float ndl = clamp(dot(NORMAL, LIGHT), 0.0, 1.0) * ATTENUATION;
    vec3 band = texture(ramp, vec2(ndl, 0.5)).rgb;
    DIFFUSE_LIGHT += band * LIGHT_COLOR;
}
```

Unity HLSL core (fragment, main light only):

```hlsl
half ndl = saturate(dot(normalWS, mainLight.direction)) * mainLight.shadowAttenuation;
half3 band = SAMPLE_TEXTURE2D(_Ramp, sampler_Ramp, half2(ndl, 0.5)).rgb;
half3 color = albedo.rgb * band * mainLight.color + albedo.rgb * ambient;
```

Parameters and rules:
- Ramp texture: 64 x 4 or 128 x 4, point sampling for hard bands; two or three bands for most styles.
- Keep the shadow band at 55-70% brightness of the lit band with a hue shift (toward the bible's shadow hue) rather than a pure darkening; this is where art direction lives.
- Use the baked or fixed light direction where possible: one fake directional light as a uniform removes per-light loops entirely.
- Specular: a single hard-edged highlight via `step(threshold, pow(ndh, gloss))` is enough; skip it for characters that read from silhouette.
- In Shader Graph, use Simple Lit node alternatives only if you accept the lighting cost; for toon, a Custom Function node with the HLSL above plus a Sample Texture 2D for the ramp is the standard approach.

## 5. Rim light and fresnel

Idea: brighten surfaces facing away from the viewer to separate characters from the background and to indicate selection or status.

Godot:

```glsl
uniform vec4 rim_color : source_color = vec4(1.0, 0.8, 0.4, 1.0);
uniform float rim_power : hint_range(0.5, 8.0) = 3.0;
uniform float rim_strength : hint_range(0.0, 2.0) = 1.0;
void fragment() {
    float f = pow(1.0 - clamp(dot(NORMAL, VIEW), 0.0, 1.0), rim_power);
    EMISSION += rim_color.rgb * f * rim_strength;
}
```

Unity HLSL: `half f = pow(1.0h - saturate(dot(normalWS, viewDirWS)), _RimPower); color += _RimColor.rgb * f * _RimStrength;`. In Shader Graph, use the Fresnel Effect node (inputs: normal, view direction, power).

Notes: replace `pow` by `f*f` or `f*f*f` for an integer power on low tier; clamp to avoid hot pixels; drive `rim_strength` from gameplay (damage flash, selection, rarity) rather than baking; remember rim needs normals, so it is not available in flat unlit sprites (use an outline or a baked edge for 2D).

## 6. Matcap

Idea: look up shading from a small texture indexed by the view-space normal. One texture sample gives lighting, material and style at once, with no lights at all. Excellent for stylized low-poly, clay, jelly, metal and glossy toy looks on mobile.

Godot:

```glsl
shader_type spatial;
render_mode unshaded;
uniform sampler2D matcap : source_color, filter_linear;
uniform sampler2D albedo_tex : source_color;
void fragment() {
    vec3 n = normalize(NORMAL);                    // view space in fragment()
    vec2 uv = n.xy * 0.5 + 0.5;
    ALBEDO = texture(albedo_tex, UV).rgb * texture(matcap, vec2(uv.x, 1.0 - uv.y)).rgb * 2.0;
}
```

Unity: transform the world normal to view space with `mul((float3x3)UNITY_MATRIX_V, normalWS)` (or `TransformWorldToViewDir(normalWS)`), use `xy * 0.5 + 0.5` as the UV, sample the matcap, multiply by albedo (and by 2 if the matcap is centred on 0.5 grey).

Notes: matcap lighting does not react to scene lights, so it is perfect for fixed-camera games and wrong for day-night cycles; use a matcap array or a lerp for a few time-of-day variants; one 128 x 128 matcap texture is usually enough; art-direct matcaps as part of the bible (one per material class).

## 7. Dissolve

Idea: compare a noise texture to a threshold; pixels below are discarded or faded; an emissive edge band sells it.

Godot:

```glsl
shader_type spatial;
render_mode cull_disabled;
uniform sampler2D albedo_tex : source_color;
uniform sampler2D noise_tex;
uniform float progress : hint_range(0.0, 1.0) = 0.0;
uniform float edge_width : hint_range(0.0, 0.2) = 0.05;
uniform vec4 edge_color : source_color = vec4(1.0, 0.5, 0.1, 1.0);
void fragment() {
    float n = texture(noise_tex, UV).r;
    if (n < progress) discard;
    float edge = 1.0 - smoothstep(0.0, edge_width, n - progress);
    ALBEDO = texture(albedo_tex, UV).rgb;
    EMISSION = edge_color.rgb * edge * 2.0;
}
```

Unity: `clip(n - _Progress)` plus `emission = _EdgeColor.rgb * (1 - smoothstep(0, _EdgeWidth, n - _Progress))`. In Shader Graph, a Sample Texture 2D noise node feeding Alpha Clip Threshold (enable Alpha Clipping) and a Step/Smoothstep for the edge.

Notes: `discard` forfeits early-z on this object while the effect runs; acceptable for one dissolving object, not for a crowd. For crowds, fade scale to zero or use alpha fade. Use a tileable noise sampled in object or world space for continuity across UV islands. Keep the noise texture 128-256 px, single channel, compressed. Drive `progress` from script or an animation curve and clear the effect (swap back to the standard material) when finished.

## 8. Flipbook animation

Idea: a texture atlas of frames (4 x 4, 8 x 8) stepped over time. Used for explosions, smoke, fire, hit sparks and UI sprites.

Godot (particle or quad): in `ParticleProcessMaterial` or a `CanvasItemMaterial`, enable particle animation with `particles_anim_h_frames`, `particles_anim_v_frames`; for a custom shader:

```glsl
uniform int h_frames = 4;
uniform int v_frames = 4;
uniform float fps = 24.0;
vec2 flipbook_uv(vec2 uv, float t) {
    int total = h_frames * v_frames;
    int idx = int(floor(t * fps)) % total;
    vec2 cell = vec2(float(idx % h_frames), float(idx / h_frames));
    return (uv + cell) / vec2(float(h_frames), float(v_frames));
}
```

Unity: Shader Graph has a Flipbook node (width, height, tile index). In the Particle System, the Texture Sheet Animation module picks frames over lifetime, with row mode and start frame randomization. Use a lifetime-driven frame index so the animation matches the particle's life.

Rules: one flipbook sheet at 512-1024 px for 16-64 frames of 128 px is the usual size on mobile; avoid blending between frames (frame blending doubles texture reads) unless necessary; compress with a format that handles alpha well and test banding on smoke; pack RGB as colour and A as shape, or store soft masks in one channel and colour by gradient ramp over lifetime to cut memory.

## 9. UV scroll

Idea: offset UVs over time for water, conveyor belts, energy beams, clouds, shine sweeps and scrolling backgrounds.

Godot: `UV += vec2(speed_x, speed_y) * TIME;` with the texture set to repeat (`repeat_enable`). Unity: `uv += _ScrollSpeed.xy * _Time.y;` with wrap mode Repeat.

Notes: use half precision with care; for long-running scroll, wrap the offset with `fract` on the CPU side or use `fract(TIME * speed)` to avoid precision loss after long sessions; layer two scrolls at different speeds and directions for water instead of one complex shader; a "shine sweep" on UI is a mask multiplied by a scrolling gradient, triggered by script, not always on.

## 10. Vertex wind and sway

Idea: move vertices in the vertex stage using a world-position phase and a weight from vertex colour, for grass, trees, flags, and cloth. Costs very little because it runs per vertex.

Godot:

```glsl
shader_type spatial;
uniform float strength = 0.1;
uniform float speed = 1.5;
uniform vec2 dir = vec2(1.0, 0.3);
void vertex() {
    float w = COLOR.r;                                   // 0 at root, 1 at tip (painted)
    vec3 wp = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
    float phase = dot(wp.xz, normalize(dir)) * 0.7 + TIME * speed;
    VERTEX.x += sin(phase) * strength * w;
    VERTEX.z += cos(phase * 0.8) * strength * w * 0.5;
}
```

Unity HLSL: same math in the vertex function with `TransformObjectToWorld` and `_Time.y`. Shader Graph: Position node (world), Time, Sine, multiply by a Vertex Color channel, add to Position (object space).

Notes: paint the weight in vertex colours (or use height above ground) so roots stay put; keep amplitude small to avoid mesh intersections; for GPU instancing, sample the phase from world position, not from instance index, so adjacent plants desynchronize naturally; disable wind beyond a distance.

## 11. Outlines

| Method | Cost | Quality | Notes |
|---|---|---|---|
| Inverted hull (second pass, back faces pushed along normals) | One extra draw per object, vertex-bound | Good, controllable width, constant world width | Needs smooth normals or baked outline normals in a UV channel or vertex colour; breaks on hard-edged low-poly unless normals are stored separately |
| Screen-space edge detection (depth/normal Sobel) | Full-screen pass, bandwidth heavy | Uniform outline for everything | Usually too expensive for low-tier mobile; use only as a high-tier option |
| Baked outline in texture | Free | Fixed width, does not scale | Good for sprites and for far LODs |
| Sprite outline shader (sample neighbours of alpha) | 4-8 extra samples per pixel | Clean for 2D | Add transparent padding to sprites; expensive for large sprites, so bake in the atlas when possible |
| Rim light as pseudo outline | Cheap | Soft | Good for selection highlights |

Inverted hull in Godot is a second material in the `next_pass` slot:

```glsl
shader_type spatial;
render_mode cull_front, unshaded;
uniform float width = 0.02;
uniform vec4 line_color : source_color = vec4(0.0, 0.0, 0.0, 1.0);
void vertex() { VERTEX += NORMAL * width; }
void fragment() { ALBEDO = line_color.rgb; }
```

In Unity URP, use a Renderer Feature or a second pass with `Cull Front`; keep width constant in screen space by scaling with clip-space w if you need a constant pixel width. Outline colour should come from the bible (darkest shade of the object, not pure black) for a polished look.

## 12. Shader variants, keywords and precision

- Every keyword (`#pragma multi_compile`) doubles variants. Prefer `shader_feature` (stripped when unused) or runtime uniforms for rarely toggled features; strip unused variants in the build.
- Variant explosion raises build time and memory and causes first-use hitches when a variant compiles at runtime; ship a shader warm-up (a hidden scene or a shader variant collection in Unity; ubershader or pipeline pre-compilation in Godot) so the first explosion does not hitch.
- Precision: use `half`/`mediump` for colours, normals, and short UV ranges; use `float`/`highp` for positions, time accumulations and large texture coordinates. Test on a device, because some GPUs ignore half.
- Avoid branching on per-pixel dynamic conditions; prefer `lerp`/`mix` with a computed factor.
- Keep material count low: sharing one material across many objects enables batching; use material property blocks (Unity) or instance uniforms (Godot) for per-object variation without new materials.
- Godot shader notes: use `render_mode` flags to remove work (`unshaded`, `specular_disabled`, `ambient_light_disabled`, `shadows_disabled`) and prefer the Mobile or Compatibility renderer when targeting low-end phones (see `references/rendering-on-mobile.md`).

## 13. Writing shaders with an agent safely

LLMs write plausible shader code that sometimes fails to compile or ignores the target's conventions. Use this protocol:
1. State the engine, version, renderer (Godot Mobile/Compatibility, Unity URP/Built-in), and the target tier.
2. Ask for the smallest shader that does the effect; list the properties; list the cost in samples and operations.
3. Compile immediately (Godot: load the material and read the editor errors or run a headless import; Unity: check the console and the inspector's compiled-code view).
4. Capture a screenshot on a test mesh against a flat background before integrating.
5. Profile on the lowest-tier device or in the engine profiler with the shader on a full-screen worst case.
6. Check licence: do not paste shader code from sources with incompatible licences; write from the idea.
7. Add a lite fallback and register the shader in the project's art spec.

## 14. The VFX language

Effects are communication first and decoration second. Use a consistent grammar so players learn it.

| Phase | Purpose | Typical duration (heuristic) | Techniques |
|---|---|---|---|
| Anticipation | Tell the player something is about to happen | 100-300 ms | Pull-in, glow growth, telegraph shapes on the ground |
| Impact | Deliver force | 50-150 ms | Hit-stop (a few frames), flash, burst of sparks, screen shake scaled to force |
| Follow-through | Show the result | 200-600 ms | Debris, smoke, shockwave ring, damage numbers |
| Settle | Return to calm | 300-1000 ms | Fade, ambient residual, UI count-up |

Principles:
- **Shape**: burst = radial lines or a ring; heal = rising plus-shaped particles; buff = upward ring and icon; debuff = downward drip and desaturation; rare = star and glint.
- **Colour roles** from the bible: friendly vs hostile, damage types, rarity. Never reuse a gameplay colour for decoration.
- **Contrast**: effects must read against every background; use a bright core with a darker or saturated edge, add an outer dark rim for bright effects on bright backgrounds.
- **Timing curves**: fast attack, slow decay; ease-out on scale, linear or ease-in on alpha fade; overshoot on rewards.
- **Hierarchy**: the player's own actions are brighter and larger than ambient and enemy effects; reserve the highest intensity for rare events.
- **Reduce at density**: scale particle counts down when many entities fire effects simultaneously (a per-frame budget system, see section 16).
- **Accessibility**: provide a reduced-flash and reduced-shake option; avoid rapid full-screen flashes; do not rely on colour alone for gameplay information.
- **Audio-visual sync**: the peak frame of the effect aligns with the sound transient within a frame or two (see `skills/game-feel`).

## 15. VFX recipes

| Effect | Ingredients | Cheap version |
|---|---|---|
| Hit spark | 6-12 additive streak sprites, 150-250 ms, bright core, randomized rotation | One flipbook quad with 8 frames |
| Coin burst | 10-20 sprites with gravity, fade, small spin, attracted to the counter | Pooled sprites with simple tweens |
| Explosion | Flash (1-2 frames), fireball flipbook, smoke flipbook, debris, shockwave ring | Flash plus one flipbook plus ring |
| Heal | Rising soft particles, ring on the ground, tint pulse on the unit | Ring plus tint pulse |
| Level-up / reward | Radial burst, light rays (scrolling UV on a quad), confetti, UI count-up | Rays plus confetti with a low count |
| Trail | Ribbon mesh or line renderer with a width curve and alpha fade | Short sprite trail with 4-6 stamps |
| Projectile | Core sprite, glow quad, trail, muzzle flash, impact | Core plus one glow quad |
| Screen feedback | Vignette flash, chromatic pulse, shake | Colour overlay with alpha tween |

Prefer sprite and quad-based effects over meshes; use additive blending for light and alpha blending for smoke and dust (additive smoke looks wrong and costs the same). Use premultiplied alpha particles to blend additive and alpha in one material.

## 16. Particle budgets

Heuristic starting budgets; adjust after profiling. Counts are simultaneous live particles on screen, and "overdraw" means the number of times a typical screen pixel is shaded by transparent layers.

| Tier | Total live particles | Max overdraw from VFX | Max simultaneous emitters | Notes |
|---|---|---|---|---|
| Low | 100-200 | about 2x | 8-12 | Prefer flipbook quads; no soft particles; no per-particle lights |
| Mid | 300-600 | about 3x | 15-25 | Limited soft particles on hero effects |
| High | 800-1500 | about 4x | 30+ | GPU particles, trails, post effects allowed |

Budget practices:
- **Measure overdraw**, not only count: a few huge smoke quads cost more than hundreds of small sparks. Shrink quads to the visible area, use meshes that hug the shape ("cutout" quads) for big soft sprites, and cap the largest particle size.
- **Pool emitters and particles**; never instantiate effects per hit on a hot path without pooling.
- **Limit lifetimes**: shorter lifetime halves the live count at the same emit rate (live ~ rate x lifetime).
- **Drive by LOD tier**: a global `vfx_quality` multiplies counts (low 0.4, mid 0.7, high 1.0 as a starting point) and disables optional layers.
- **Cull**: stop emitters off-screen; for ambient effects reduce emission rate with distance.
- **Combine textures**: one VFX atlas for all effects to batch draws; a single shared additive material and a single alpha material cover most needs.
- **CPU vs GPU particles**: CPU particles are flexible and work everywhere, GPU particles scale to high counts but need compute or transform feedback support and can be slower on some low-end GPUs; in Godot, use CPUParticles on the Compatibility renderer path and test GPUParticles on the target devices; in Unity, the built-in Particle System (CPU) is the safe default on mobile and VFX Graph needs compute support.
- **Debug checklist**: readable on dark, bright and busy backgrounds; peak frame aligned with sound; no first-use hitch (warm shaders); pooled spawns; off-screen emitters stopped; a reduced-effects setting that still communicates.
- **Formula**: estimated fill cost per frame ~ sum over particles of (screen-covered pixels x instruction cost). Compare against a frame budget (see `skills/mobile-performance`).
