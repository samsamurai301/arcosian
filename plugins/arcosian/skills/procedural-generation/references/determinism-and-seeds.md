# Determinism and Seeds

Procedural content is only an asset if you can reproduce it. The same seed must give the same level on an iPhone, a low-end Android phone, the CI server and next year's build, or daily challenges diverge, shared seeds lie, replays desync, leaderboards cannot be verified and bugs cannot be reproduced. This file covers how to get there: picking and porting a seeded PRNG (PCG32, xorshift, SplitMix64, xoshiro), using it without bias, splitting it into independent streams, the floating-point traps that break cross-platform determinism and the fixed-point alternative, input-log replays and desync detection, daily and weekly seeds, and human-shareable seed codes. Reference outputs for every PRNG here can be printed with `scripts/pcgkit.py prng`, so an engine port can be checked bit for bit.

## Contents

1. What depends on determinism
2. Determinism levels: decide which one you need
3. Choosing a PRNG
4. Reference implementations and porting notes
5. Using a PRNG correctly: bounds, floats, shuffles, weights
6. Stream architecture: one root seed, many independent streams
7. Cross-platform floating point: what breaks and why
8. Fixed-point arithmetic
9. Replays, ghosts and desync detection
10. Daily, weekly and event seeds
11. Seed sharing and seed codes
12. Randomness that must not be seeded on the client
13. Testing determinism: the CI checklist
14. Volatile facts (as of Oct 2026, verify before relying)

---

## 1. What depends on determinism

| Feature | Needs | Breaks when |
|---|---|---|
| Bug reproduction ("seed 48213, level 7 is unwinnable") | Same build, same device class | Any hidden global RNG call or wall-clock input |
| Save files that store a seed, not the world | Same build and later builds | Generator changes without versioning |
| Seed sharing between players | Across devices | Float or library differences between iOS and Android |
| Daily challenge with a global leaderboard | Across devices, all players on one build | Timezone mistakes; generator changes mid-day |
| Input-log replays and ghosts | Whole simulation, across devices | Frame-rate-dependent logic, float drift |
| Server validation of scores | Client and server (often different languages) | Any platform-specific math |
| Lockstep multiplayer | Bit-exact simulation on every peer | Anything above |
| Golden tests in CI | Same build, CI vs device | Unordered containers, threads |

Every one of these is cheaper to build into the generator from day one than to retrofit. Retrofitting determinism means auditing every random call, every float operation and every container iteration in the codebase.

---

## 2. Determinism levels

| Level | Promise | What you must do | Typical game need |
|---|---|---|---|
| L0 | Same run reproduces (in-memory) | Seeded RNG instance, no global RNG | Prototype |
| L1 | Same build + same device reproduces | No wall-clock, no unordered iteration, no thread races in generation | Bug repro, save-by-seed |
| L2 | Same build reproduces across devices and OSes | L1 + integer/fixed-point generation, or a controlled float subset; own PRNG (not engine/OS) | Seed sharing, dailies, leaderboards |
| L3 | Across builds and versions | L2 + versioned generators; old generator code paths kept or content frozen as data | Long-lived dailies, replays, saves by seed |
| L4 | Across languages and engines (client C#, server Python or Go) | L3 + a spec'd algorithm with published test vectors, integer-only | Server-verified competitive scores |

Decide the level per system in the design contract (`contract.technical.deterministic` is the project-wide flag; record the per-system level in `notes` or the architecture doc). Most mobile PCG needs **L2 for generation** and **L3 for anything stored as a seed**. Simulation-wide L2 (for replays) is a larger commitment that belongs to `game-architecture` and `gameplay-programming`.

---

## 3. Choosing a PRNG

Never use these for generation you want to reproduce: `Math.random()` in JavaScript (cannot be seeded), C `rand()` (implementation-defined), the engine's global RNG (shared state, any system can advance it), and the platform `System.Random` or equivalents (implementations differ by runtime, and the seeded and unseeded constructors can use different algorithms). Ship your own small PRNG in the generator code.

| Generator | State | Output | Period | Quality (statistical test suites) | Notes |
|---|---|---|---|---|---|
| LCG (e.g. 64-bit, output high bits) | 64-bit | 32-bit | 2^64 | Low bits weak; fine if you only use high bits | Simplest; the base of PCG |
| xorshift32 (Marsaglia 2003, shifts 13/17/5) | 32-bit | 32-bit | 2^32 − 1 | Fails several tests; adequate for VFX | Never seed with 0 |
| xorshift64* (Vigna) | 64-bit | 64-bit | 2^64 − 1 | Good for its size | Nonzero seed |
| xoshiro128** (Blackman & Vigna 2018) | 128-bit | 32-bit | 2^128 − 1 | Good; supports jump-ahead | Seed the state with SplitMix64 |
| xoshiro256** | 256-bit | 64-bit | 2^256 − 1 | Good; jump-ahead | 64-bit platforms |
| PCG32 (O'Neill 2014, PCG-XSH-RR) | 64-bit + 64-bit stream | 32-bit | 2^64 per stream, 2^63 streams | Good; small, fast | Built-in stream selection; the default recommendation |
| SplitMix64 (Steele, Lea, Flood 2014) | 64-bit | 64-bit | 2^64 | Good | Ideal as a **seeder** and **hash** (each output is a bijective mix of a counter) |

**Studio default:** PCG32 for sequential draws, SplitMix64's mixing function (`mix64`) to derive child seeds and hash coordinates, and 32-bit outputs throughout gameplay code because they port cleanly to every language. These are statistical generators, not cryptographic ones (§12).

---

## 4. Reference implementations and porting notes

All arithmetic is unsigned and wraps modulo 2^32 or 2^64. Port these exactly and check your port against the test vectors before using it.

```text
# PCG32 (PCG-XSH-RR 64/32), seeding as in the minimal C library
state: u64, inc: u64
seed(initstate, initseq):
    state = 0; inc = (initseq << 1) | 1
    next_u32(); state += initstate; next_u32()
next_u32():
    old = state
    state = old * 6364136223846793005 + inc                 # mod 2^64
    xorshifted = u32(((old >> 18) XOR old) >> 27)
    rot = u32(old >> 59)
    return (xorshifted >> rot) | (xorshifted << ((-rot) AND 31))   # 32-bit rotate right

# SplitMix64
x: u64
next_u64():
    x += 0x9E3779B97F4A7C15
    return mix64(x)
mix64(z):
    z = (z XOR (z >> 30)) * 0xBF58476D1CE4E5B9
    z = (z XOR (z >> 27)) * 0x94D049BB133111EB
    return z XOR (z >> 31)

# xorshift64* (nonzero seed)
next_u64():
    x ^= x >> 12; x ^= x << 25; x ^= x >> 27
    return x * 0x2545F4914F6CDD1D
```

**Test vectors** (computed by `scripts/pcgkit.py`; the PCG32 row agrees with the output of the PCG C library's demo program, and the SplitMix64 row with the reference outputs commonly used in SplitMix64 test suites; reproduce them with `pcgkit.py prng`):

| Generator and seed | First outputs |
|---|---|
| PCG32, initstate 42, initseq 54 | `0xa15c02b7 0x7b47f409 0xba1d3330 0x83d2f293 0xbfa4784b 0xcbed606e` |
| SplitMix64, seed 1234567 | `6457827717110365317 3203168211198807973 9817491932198370423 4593380528125082431 16408922859458223821` |
| xorshift32 (13/17/5), seed 1 | `270369` (first output) |

**Language porting traps:**

| Language | Trap | Fix |
|---|---|---|
| GDScript (Godot 4) | `int` is a signed 64-bit integer. Multiplication wraps to the same low 64 bits as unsigned, but `>>` is an arithmetic shift that copies the sign bit into the top | Mask after every right shift of a value that may have bit 63 set: `(x >> 30) & ((1 << 34) - 1)`. Store 32-bit outputs masked with `& 0xFFFFFFFF`. Verify against the vectors |
| GDScript | Hex literals above `0x7FFFFFFFFFFFFFFF` do not fit a signed int | Write such constants as their signed two's-complement value (compute it with Python: `c - 2**64`) |
| C# (Unity) | Overflow checking may be enabled in some build configurations; mixing `int` and `uint` promotes to `long` | Use `ulong`/`uint` with explicit `unchecked { }` blocks; cast results back to `uint` |
| JavaScript / TypeScript | Numbers are doubles; bitwise ops are 32-bit signed | 32-bit generators with `Math.imul` and `>>> 0`; use `BigInt` for 64-bit state (slow) or a 32-bit-only generator |
| Python | Integers are unbounded | Mask every operation with `& 0xFFFFFFFFFFFFFFFF` (see `scripts/pcgkit.py`) |
| Lua 5.3+ | 64-bit integers wrap; `>>` is logical | Fine for 64-bit; Lua 5.1/LuaJIT need a different approach (doubles; use 32-bit generators) |

---

## 5. Using a PRNG correctly

### 5.1 Bounded integers: no raw modulo

`next_u32() % n` is biased whenever n does not divide 2^32: the first `2^32 mod n` values occur once more than the others. For dice (n = 6) the bias is negligible (about 1 part in 7×10^8), but for large n it is not: with n = 3×10^9 the low values are twice as likely as the high ones. Use rejection:

```text
function bounded(n):                       # unbiased integer in [0, n), n <= 2^32 - 1
    threshold = (2^32 - n) mod n            # = (-n) mod n in unsigned 32-bit arithmetic
    loop:
        r = next_u32()
        if r >= threshold: return r mod n
function range(a, b): return a + bounded(b - a + 1)     # inclusive
```

This is the method of PCG's `pcg32_boundedrand_r`. It loops more than once with probability below n / 2^32.

### 5.2 Floats

- 64-bit to double in [0, 1): `(x >> 11) * 2^-53` (exact).
- 32-bit to float in [0, 1): `(x >> 8) * 2^-24` (exactly representable in float32 too, so the same value on every platform).
- Do not compute `x / 4294967295.0`: it can return exactly 1.0, and float rounding makes it platform-sensitive.
- For gameplay decisions, compare integers instead of floats: "20% chance" is `bounded(100) < 20` (exactly 0.2) or `next_u32() < 858993459` (0.2 × 2^32 rounded down, off by about 5×10^-11). Both are portable; neither touches floating point.

### 5.3 Shuffles

Fisher–Yates, and nothing else:

```text
for i from n-1 down to 1:
    j = bounded(i + 1)                     # 0 <= j <= i
    swap(a[i], a[j])
```

The common bug, swapping with `bounded(n)` at every step, produces a measurably non-uniform permutation distribution. Sorting with a random comparator is worse, and depends on the sort implementation.

### 5.4 Weighted choice

- **Small tables (fewer than about 50 entries) or tables that change:** integer cumulative weights and a linear or binary search on `bounded(total)`. Keep weights as integers so the total is exact.
- **Large static tables (loot, spawn tables):** Walker's alias method (Vose's variant) gives O(1) draws after an O(n) build. Build it from integer weights in a fixed order.
- **Weights from data files:** sort entries by a stable key (id) before building, so file order or dictionary iteration order cannot change results.

### 5.5 Other distributions

- **Normal-ish:** sum of 3 or 4 uniforms gives a bell shape with bounded tails, uses no transcendental functions and is portable. Box–Muller needs `log`, `sqrt` and `cos`, which break L2 determinism unless you use your own implementations (§7).
- **Without replacement:** shuffle-and-take for small pools; Floyd's algorithm for k of n when n is large.
- **Bags and shuffle bags:** fill a bag with outcomes in the desired proportions, shuffle, draw until empty, refill. This bounds streaks; Tetris-style "7-bag" randomisers are the classic example. Bags are deterministic given the seed and feel fairer than independent draws.

---

## 6. Stream architecture

**The single most common determinism bug in PCG:** one RNG shared by everything. Adding one random call anywhere (a new particle effect, a new loot roll) shifts every later draw, so the same seed now generates a different level. Call this RNG coupling.

```text
root = run_seed (u64)
layout_rng  = PCG32(derive(root, "layout"))
loot_rng    = PCG32(derive(root, "loot"))
enemy_rng   = PCG32(derive(root, "enemies"))
cosmetic_rng= PCG32(derive(root, "cosmetic"))     # VFX, idle animations: may use anything, affects nothing
level_seed(i) = derive(root, "level:" + str(i))    # random access: level 37 without generating 1..36
chunk_seed(cx, cy) = mix64(root XOR (cx * 0x9E3779B97F4A7C15) XOR (cy * 0xC2B2AE3D27D4EB4F))

derive(root, name) = mix64(root XOR fnv1a64(name))  # pcgkit.py seed derive
```

Rules:
1. **One stream per system, per independent decision domain.** Layout, population, loot, combat, AI and cosmetics each get their own stream.
2. **Random access by key, not by sequence.** Level i, chunk (x, y), room r and wave w take seeds derived from (root, key). Generating level 37 must not require generating levels 1–36, and generation order must not matter (this also makes parallel or lazy generation safe).
3. **Cosmetic randomness never touches gameplay streams.** Presentation code (VFX, audio variation, idle animation) gets its own unseeded or cosmetic stream.
4. **Stateless hashing for spatial randomness.** For "is there a tree at (x, y)?", use `mix64(seed, x, y)` rather than a sequential RNG. Squirrel Eiserloh's GDC 2017 talk "Math for Game Programmers: Noise-Based RNG" makes the case for position-keyed noise functions as RNGs.
5. **Persist RNG state in saves** when the game continues a sequence (a roguelite run mid-floor). Store the stream states, not just the root seed, or re-derive per-floor seeds so that loading at a floor boundary is exact.
6. **Decide on save-scum behaviour deliberately.** If the per-action RNG state is saved, reloading reproduces the same outcome (players cannot reroll a miss by reloading). Keying draws by (turn, action) gives the same result. *XCOM: Enemy Unknown* (2012) is a well-known case of a game that persists its random seed across reloads.

Seed hygiene: Godot's documentation for `RandomNumberGenerator` notes that its generator has no avalanche effect, so similar seeds can give similar streams, and recommends hashing externally sourced seeds. Always pass user-visible or sequential seeds (1, 2, 3; dates; level numbers) through `mix64` or `derive` before seeding.

---

## 7. Cross-platform floating point

IEEE 754 requires the basic operations (+, −, ×, ÷, square root) to be correctly rounded. Given the same inputs, the same precision and the same rounding mode, every conforming platform returns the same bits. Cross-platform float divergence therefore comes from the conditions around those operations:

| Source of divergence | What happens | Where you meet it | Mitigation |
|---|---|---|---|
| Transcendental functions (`sin`, `cos`, `exp`, `log`, `pow`, `atan2`) | Not required to be correctly rounded; each math library (Apple, Android's Bionic, glibc, MSVC, the engine's own) can differ in the last bits | Everywhere: angles, Poisson disk, Box–Muller, curves | Own implementations from basic ops (polynomial or table, fixed evaluation order), or fixed-point tables |
| Fused multiply-add contraction | The compiler may turn `a*b + c` into one FMA with a single rounding; results differ from two roundings | Native code on ARM64 and modern x86, depending on compiler flags; any C# → C++ path (Unity IL2CPP) inherits the C++ toolchain's settings | Disable contraction for simulation code where the toolchain allows it, or avoid floats in the sim |
| Fast-math, reassociation | `(a + b) + c` reordered to `a + (b + c)` | Aggressive optimisation flags, some SIMD or Burst-style compilers | No fast-math on sim code; check the documented float mode of your compiler |
| Extended precision | Intermediates kept at 80 bits, then rounded | Legacy 32-bit x86 (x87) builds; not phones | Use SSE2 or 64-bit targets |
| Summation order | Parallel or SIMD reductions sum in a different order | Multithreaded generation, job systems | Deterministic reduction order; integer accumulation |
| Float ↔ int conversion of NaN or out-of-range values | Platform-defined results | Edge cases in clamps and casts | Clamp before converting; never convert NaN |
| Float formatting and parsing | Locale (comma decimal separators) and shortest-round-trip differences | JSON and CSV configs, save files | Store integers or fixed point; invariant-culture parsing |
| Mixed precision | float32 vectors in one code path, float64 in another | Godot: GDScript `float` is 64-bit but `Vector2`/`Vector3` are 32-bit in standard builds | Pick one precision for the sim and stay in it |
| GPU computation | Different hardware, drivers and precision | Compute-shader generation, GPU noise | Never use the GPU for gameplay-relevant generation; cosmetic only |
| Physics engines | Iteration order, solver details, platform math | Rigid-body-driven layouts (e.g. separating rooms with physics) | Do not use engine physics inside generators; write a small integer separation step |

**Strategy ladder** (pick the lowest rung that meets your determinism level):
1. **Integer-only generation (recommended for PCG).** Grids, integer weights, integer RNG outputs, integer geometry. Convert to floats only in presentation. Most 2D mobile generators (runner chunks, puzzle boards, dungeon grids, loot) are naturally integer.
2. **Fixed-point maths** (§8) where you need fractions: positions, angles, curves.
3. **Restricted floats:** only basic operations, no transcendental library calls (use your own polynomial or table versions), contraction and fast-math disabled, one precision. Prove it with a cross-device hash test on every release. Fragile: a compiler or engine upgrade can break it silently.
4. **Give up bit-exactness:** keep a server-authoritative simulation and sync state or snapshots instead of inputs. Valid for real-time multiplayer (`multiplayer-backend`), but you lose seed-shareable float content.

---

## 8. Fixed-point arithmetic

Represent a real number v as an integer `round(v × 2^F)`. Addition and comparison are plain integer operations; multiplication and division need a rescale.

| Format | Storage | Range | Resolution | Notes |
|---|---|---|---|---|
| Q16.16 | int32 | ±32,768 | 2^-16 ≈ 1.5×10^-5 | Classic; multiply needs a 64-bit intermediate |
| Q24.8 | int32 | ±8.4 million | 2^-8 ≈ 0.0039 | Tile or pixel coordinates in large worlds |
| Q32.32 | int64 | ±2.1×10^9 | 2^-32 ≈ 2.3×10^-10 | Multiply needs a 128-bit intermediate |
| Q48.16 | int64 | ±1.4×10^14 | 1.5×10^-5 | Good default in GDScript or C# `long` for positions and sums; a product only fits in int64 when both operands are below about ±46,000 in value (raw below 2^31.5), so split larger multiplies or use a 128-bit product |

```text
F = 16; ONE = 1 << F; HALF = 1 << (F - 1)
from_int(i)   = i << F
add(a, b)     = a + b
mul(a, b)     = (a * b + HALF) >> F              # 64-bit intermediate for Q16.16; round half up
div(a, b)     = (a << F) / b                      # integer division truncates toward zero: define your rounding
to_float(a)   = a / 65536.0                       # presentation only

function sqrt_fx(a):                               # integer Newton iteration on a << F
    if a <= 0: return 0
    n = a << F; x = max(n >> 1, 1)                # needs 64-bit for Q16.16
    loop: y = (x + n / x) >> 1; if y >= x: return x; x = y

# sin/cos: quarter-wave lookup table generated OFFLINE, stored as integers in source
SIN_Q = [round(sin(i / 1024 * PI/2) * ONE) for i in 0..1024]   # 1,025 entries
function sin_fx(angle_turns_q16):                  # angle in turns (1.0 = full circle) in Q16
    t = angle_turns_q16 AND 0xFFFF                  # wrap to [0, 1) turn
    quadrant = t >> 14; idx = (t >> 4) AND 0x3FF; frac = t AND 0xF
    # mirror idx for quadrants 1 and 3, negate for 2 and 3, lerp between SIN_Q[idx] and SIN_Q[idx+1] by frac/16
```

Rules:
- **Pick one rounding policy** and implement it in one helper. Arithmetic right shift rounds toward negative infinity; integer division truncates toward zero. Mixing them causes asymmetric drift (things slowly move left).
- **Generate tables offline** and commit them as integer literals. Generating them at startup with the platform's `sin` defeats the purpose.
- **Angles in turns or binary angle units** (a full circle = 2^16) wrap for free with a mask, unlike radians.
- **Overflow checks** in debug builds on every multiply; the most common fixed-point bug is a silent overflow in a squared distance. Compare squared distances in Q-format with a wider type, or compare in Q24.8.
- **GDScript note:** `int` is signed 64-bit, so Q16.16 multiplies of operands within ±32,768 (2^31 raw) fit in the 64-bit product. **C# note:** use `long` and `checked` in debug; for Q32.32 you need a 128-bit product (`Math.BigMul` where your .NET profile provides it, or split into 32-bit halves).

---

## 9. Replays, ghosts and desync detection

**Two replay models:**

| | Input-log replay | Snapshot replay |
|---|---|---|
| Stores | Seed, versions, settings, and inputs per simulation tick | Full or delta state at keyframes plus interpolation |
| Size | Tiny (bytes per minute) | Large (KB to MB per minute) |
| Requires | Bit-exact deterministic simulation (L2 or better) | Nothing special |
| Survives a sim change | No; replays are invalidated or need the old sim | Yes |
| Server can verify a score | Yes, by re-simulating | No (state can be forged) |
| Use for | Puzzle and turn-based games, runners with a fixed tick, ghosts, competitive dailies | Real-time action without a deterministic sim, kill-cams |

**Input-log format** (one JSON or binary blob):

```text
header: { game_version, sim_version, generator_version, content_hash, seed, mode, settings }
inputs: [ (tick, action, args), ... ]        # only ticks with input; sim runs at a fixed rate (e.g. 30 or 60 Hz)
checks: [ (tick, state_hash), ... ]          # every N ticks (e.g. every 60) and at the end
result: { score, outcome, final_tick, final_state_hash }
```

Sizing example: a runner at 60 ticks per second with about 1 input per second, stored as a 4-byte tick delta plus 1 byte of action, is roughly 300 bytes per minute before compression. A 3-minute daily run fits easily in one network request.

**Rules for a replayable simulation:**
1. Fixed timestep for the sim (accumulate render delta, step the sim in whole ticks). Never feed render delta time into game logic.
2. All randomness from seeded streams (§6); nothing from the clock, frame count or input timing outside the logged inputs.
3. Deterministic iteration order: no hash-map iteration in sim logic unless the map type preserves insertion order; sort entity lists by stable id before processing.
4. Inputs are applied at tick boundaries, identically in live play and replay. Live play should literally record and then replay its own input stream through the same code path.
5. **State hash** per check interval: serialise the sim state canonically (sorted keys, integers, fixed field order) and hash it (FNV-1a 64 or similar). On mismatch, binary-search the ticks between the last good and first bad check to find the divergent tick, then dump both states and diff them.
6. **Version everything:** `sim_version` bumps when any rule or generator change alters outcomes. Old replays either play on an archived sim build, or are retired. Never "mostly" replay.

**Server validation:** re-simulate submitted runs server-side and accept the score only if the result and final hash match. That needs the same simulation code on the server: a C# sim core that compiles for both Unity and a .NET server is the easiest path; with GDScript, run a headless Godot instance on the server, or keep the sim core in a portable language. Validate a sample, not every run, if compute is tight, and always validate leaderboard top entries.

**Ghosts** (async racing against another player's run) are input-log replays rendered as translucent actors. They need the same level (seed plus generator version) and a deterministic sim for the ghost's own actor only, which is easier than a whole-world replay.

---

## 10. Daily, weekly and event seeds

```text
daily_seed(date_utc) = derive(fnv1a64(GAME_SALT), "daily:" + date_utc.iso())     # pcgkit.py seed daily
weekly_seed(date)    = derive(fnv1a64(GAME_SALT), "weekly:" + iso_year_week(date))
```

Design and engineering checklist:
1. **One global day boundary.** Use UTC midnight (or one fixed reset hour in UTC, chosen to fall in a low-traffic window for your main markets). Local-midnight dailies give different players different "todays", which breaks leaderboards and lets players preview tomorrow's level by changing timezone.
2. **Server time is the authority.** Fetch the current date key from your backend (or a signed timestamp). Device clocks can be changed; offline play can use the last confirmed key and submit later with the date key attached.
3. **Freeze the generator per daily.** Store `generator_version` alongside each date in remote config. When you ship a new generator, keep the old code path until all dailies generated with it have expired from leaderboards. Otherwise players on different app versions get different levels for the same date.
4. **Pre-validate.** Each week in CI, generate the next 30–60 days, run the solver or bot gates (`generate-and-test.md`), and write an **override list** to remote config for dates whose seed fails (`date → replacement seed`). Never let a raw seed reach players unverified. A broken daily is public and has no fix until midnight.
5. **The curated-list alternative.** The original *Wordle* shipped its answer list in the client and indexed it by days since launch. A curated list indexed by date is the simplest daily system and gives full editorial control. The trade-off is that the content is predictable to anyone who reads the client. Hybrid: a curated list of *seeds*, fetched from the server a day ahead.
6. **Fairness.** Everyone gets the same seed *and* the same rules: lock modifiers, boosters and difficulty for daily runs, or segment leaderboards by loadout.
7. **Attempts and streaks.** Decide: one attempt (high stakes, as in *Spelunky*'s daily challenge) or best-of-N. Streak logic keys on the date key, not on 24-hour windows, with a grace mechanic (a streak freeze) designed into the economy if you use one (`liveops`, `economy-design`).
8. **Event seeds.** Weekly or event content uses the same derivation with a different namespace (`"event:halloween-2026:stage:3"`), so event content is reproducible and testable before it goes live.

---

## 11. Seed sharing and seed codes

**Encoding.** Raw 64-bit integers are unshareable. Use Crockford's Base32 (alphabet `0123456789ABCDEFGHJKMNPQRSTVWXYZ`): it omits I, L and O to avoid confusion with 1 and 0, and omits U (the specification gives avoiding accidental obscenity as the reason). Decoding is case-insensitive and maps O→0 and I/L→1, so typos of that kind still decode. A 32-bit seed is 7 characters and a 64-bit seed 13; group them in fours with hyphens (`41HN-QSWG-J640-3`). An optional Crockford check symbol (value mod 37) catches most single-character typos. All of this is implemented in `pcgkit.py seed encode|decode [--check]`.

**What a seed code must carry:**
- The seed itself.
- The **generator version** and **mode or ruleset** (`v3-HARD-41HN-QSWG`): a seed without a version silently changes meaning after an update.
- Optionally, a mode-specific prefix the UI can validate before generating.

**UX on mobile:**
- Show the seed on the run-start and results screens with a copy button and a share sheet (deep link plus the code as text).
- Seed entry: an uppercase alphanumeric keyboard, auto-inserted hyphens, forgiving decoding, and instant validation (check symbol, version known).
- **Word seeds** as an alternative: three words from a curated 2,048-word list encode 33 bits and are easy to say aloud. Curate the list for all supported languages, and screen combinations for offensive phrases, as you should for any player-visible generated string (`pcg-for-mobile-games.md` §8).

**Design consequences of shareable seeds:**
- Players will find and share the best seeds. Separate leaderboards or achievements for set-seed and random-seed runs, as speedrunning communities do.
- A seed that generates something broken will be shared *because* it is broken. Keep a server-side blocklist that maps bad seeds to a regenerate.
- Seeds are not secret and not a security boundary (§12).

---

## 12. Randomness that must not be seeded on the client

Seeded PRNGs are predictable by design: anyone with the seed (or a few outputs) can predict the future. That is fine for levels and cosmetic variety. It is not acceptable for:
- **Paid random rewards** (loot boxes, gacha, paid rerolls). Roll on the server with a cryptographically secure generator, log every roll, disclose odds, and implement pity rules server-side. Client-predictable odds are a fairness and legal problem (`monetization`, `legal-ethics`).
- **Competitive outcomes worth cheating for** (PvP drops, tournament rewards). Server-side rolls, or commit–reveal schemes.
- **Anything security-related** (tokens, IDs, session keys). Use the platform's CSPRNG.

Rule of thumb: if a player would pay or cheat to know the next value, it must not come from a client-side seeded stream.

---

## 13. Testing determinism: the CI checklist

- [ ] **Golden tests:** for 20–100 fixed seeds per generator, hash the canonical output and compare with committed hashes. Run on every commit.
- [ ] **Twice-in-a-row:** generate(seed) twice in one process, in different orders, and on a background thread. Results must be identical.
- [ ] **Order independence:** generate chunks or levels in shuffled order; compare with sequential generation.
- [ ] **Cross-platform matrix:** run the golden tests on CI (desktop), one iOS device and one low-end Android device (device farm or a manual pre-release step) for each release candidate.
- [ ] **PRNG port vectors:** the engine's PRNG port reproduces `pcgkit.py prng` outputs (unit test with the vector table in §4).
- [ ] **Coupling test:** add a dummy draw to the cosmetic stream; the golden hashes for gameplay content must not change.
- [ ] **Version guard:** a change to golden hashes requires a `generator_version` bump in the same commit (enforce with a test that compares the hash file and the version constant).
- [ ] **Replay round-trip:** record a bot playthrough, replay it, compare per-interval state hashes (`qa-testing`, playthrough gate).
- [ ] **No forbidden calls:** lint the generator and sim directories for `randf()`, `randi()`, `UnityEngine.Random`, `System.Random`, `Math.random`, wall-clock reads and `Time.deltaTime` in sim code.

---

## 14. Volatile facts (as of Oct 2026, verify before relying)

- Godot's `RandomNumberGenerator` documentation says it "currently uses PCG32" and that the algorithm is an implementation detail that should not be depended upon. It also says a given seed gives a reproducible sequence, that the generator has no avalanche effect (similar seeds can give similar streams, so hash external seeds), and that `state` should only be restored from values read from `state`. Source: [Godot docs, RandomNumberGenerator](https://docs.godotengine.org/en/stable/classes/class_randomnumbergenerator.html). Implication: fine for cosmetic randomness; ship your own PRNG for anything that must match across Godot versions or other runtimes.
- Unity's `UnityEngine.Random` documentation describes it as a static class with globally shared state, using an Xorshift 128 generator after Marsaglia's paper. It is seeded once at process start from the OS unless you call `InitState`, and it errors if used off the main thread. Source: [Unity Scripting API, Random](https://docs.unity3d.com/ScriptReference/Random.html). Implication: global state means any system can advance it, which is RNG coupling by construction. Use an instance PRNG (your own, or a per-system instance type) in generators and the sim core.
