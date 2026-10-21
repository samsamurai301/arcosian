# PCG Algorithms: Catalogue with Pseudo-code

This is the algorithm shelf for the studio's procedural generation work. Each entry covers what the algorithm is for, what it guarantees and what it does not, the parameters that matter with starting values, failure modes, cost, and language-neutral pseudo-code you can port to GDScript, C# or Python. The families are coherent noise (value, Perlin, simplex, fBm, domain warping, Worley), grid sculpting (cellular automata, drunkard walk, BSP, room-and-corridor, agents), example-driven synthesis (wave function collapse, both models), point and region structure (Poisson disk, Voronoi, Delaunay), rewriting systems (L-systems, shape grammars, Dormans-style mission and space graph grammars), and declarative or search approaches (constraint solving, search-based PCG, quality-diversity). One rule applies throughout: an algorithm gives you *local* structure cheaply, and *global* guarantees (connected, solvable, fair, readable) almost always come from an extra constraint, a repair pass or a verifier (`generate-and-test.md`).

## Contents

1. Choosing an algorithm (selection table)
2. Pseudo-code conventions
3. Coherent noise: value, Perlin, simplex, Worley
4. fBm and its variants
5. Domain warping
6. Using noise for terrain, biomes and placement
7. Cellular-automata caves (with a measured parameter sweep)
8. Drunkard walk
9. BSP rooms
10. Room-and-corridor (place-and-reject, separation, Delaunay + MST)
11. Wave function collapse: tiled and overlapping models
12. Poisson disk sampling (Bridson)
13. Voronoi diagrams, Delaunay triangulation, Lloyd relaxation
14. L-systems
15. Shape grammars and split grammars
16. Graph grammars: Dormans' missions and spaces, lock-and-key, cyclic generation
17. Agent-based generation
18. Constraint solving (CSP, SAT, ASP)
19. Search-based PCG, novelty search and MAP-Elites
20. Composition patterns: pipelines, templates and hybrids
21. Cost and suitability on device

---

## 1. Choosing an algorithm

| Content you need | First choice | Why | What it does *not* guarantee | Add |
|---|---|---|---|---|
| Terrain heightfield, biome maps, resource density | fBm over simplex/Perlin, plus domain warp | Continuous, infinite, random access by coordinate | Playability, paths, fairness | Flatten spawn areas, then a path check |
| Organic caves | Cellular automata | Natural-looking blobs, very cheap | Connectivity | Flood fill: keep the largest region or tunnel between regions |
| Winding tunnels, minimum-coverage maps | Drunkard walk | Always connected (it is one walk) | Interesting rooms, pacing | Room stamps at turning points |
| Rectangular dungeons with no overlaps | BSP | Even space use, simple | Loops, variety (looks gridded) | Extra edges, irregular room shapes |
| Classic dungeons with loops | Room placement + Delaunay + MST + extra edges | Controllable loopiness | Pacing, lock-and-key logic | Mission graph on top |
| Tile maps "in the style of" an example | WFC (overlapping) or WFC (tiled) | Local coherence learned from art | Global connectivity, solvability, termination without restarts | Pre-constraints, a path constraint, a verifier |
| Even scatter (trees, rocks, spawn points) | Poisson disk | No clumps, no grid look | Semantics (a tree on a road) | Masks from noise or a layout |
| Regions, territories, cracked or cell-like surfaces | Voronoi (+ Lloyd) | Natural partitions, adjacency for free via Delaunay | Region sizes, borders that read well | Relaxation, merging small cells |
| Plants, rivers, coral, branching structures | L-systems | Compact rules, organic recursion | Collision avoidance, budgets | Environment-sensitive rules, depth caps |
| Buildings, facades, props with structure | Shape or split grammar | Architectural regularity | Variety unless rules are rich | Stochastic rule choice with weights |
| Quest or dungeon *logic* (keys, locks, gates) | Graph grammar (Dormans) | Structure and pacing are explicit | Spatial layout | A second, space-generating step |
| Puzzles that must be solvable, unique or exact | Backward generation or constraint solving | Guarantees by construction or proof | Fun, difficulty | Solver-measured difficulty |
| Content that must hit numeric targets (difficulty, density) | Search-based (evolutionary, MAP-Elites) | Optimises measurable goals | Speed (slow), readability | Offline batch, curated output |
| Endless runner, roguelite rooms, mobile levels | Template/chunk assembly + rules | Handmade quality, procedural variety | Freshness if the pool is small | Variants, flips, recency penalty (`pcg-for-mobile-games.md`) |

**Rule of thumb for mobile:** generate on device only what is cheap and deterministic (chunks, noise, CA, Poisson, small WFC); generate expensive or risky content (search, constraint solving, large WFC, LLM output) offline, verify it, and ship it as data or as curated seeds.

---

## 2. Pseudo-code conventions

- `rng` is a seeded PRNG instance (see `determinism-and-seeds.md`). `rng.float()` returns a value in [0, 1), `rng.int(a, b)` an integer in [a, b] inclusive, `rng.pick(list)` a uniform element, `rng.weighted(items, weights)` a weighted pick, `rng.shuffle(list)` an in-place Fisher–Yates shuffle.
- Grids are `grid[y][x]`, row 0 at the top. `WALL` and `FLOOR` are cell codes.
- `lerp(a, b, t) = a + (b - a) * t`; `clamp(v, lo, hi)`; `floor` is mathematical floor (careful with negatives: `int()` truncates toward zero in most languages).
- Never call a global `random()` in generator code. Every generator takes its `rng` (or a seed) as an argument.

---

## 3. Coherent noise

"Coherent" noise is random but smooth: nearby inputs give nearby outputs. It is a pure function of (coordinates, seed), which is what makes it ideal for infinite worlds and chunked generation: any chunk can be generated independently, in any order, and agree at its borders.

### 3.1 Value noise

Assign a random value to each integer lattice point and interpolate. Cheapest of the family, but it shows blocky, axis-aligned artefacts at low octave counts.

```text
function hash2(ix, iy, seed) -> uint32:        # integer hash of the lattice point
    h = seed XOR (ix * 0x27D4EB2D) XOR (iy * 0x165667B1)
    h = (h XOR (h >> 15)) * 0x85EBCA6B         # all operations mod 2^32
    h = (h XOR (h >> 13)) * 0xC2B2AE35
    return h XOR (h >> 16)

function value_noise2(x, y, seed) -> float in [0, 1]:
    ix = floor(x); iy = floor(y)
    fx = x - ix;   fy = y - iy
    v00 = hash2(ix,   iy,   seed) / 2^32
    v10 = hash2(ix+1, iy,   seed) / 2^32
    v01 = hash2(ix,   iy+1, seed) / 2^32
    v11 = hash2(ix+1, iy+1, seed) / 2^32
    u = fade(fx); v = fade(fy)                  # smoothstep or quintic
    return lerp(lerp(v00, v10, u), lerp(v01, v11, u), v)

function fade(t) = t*t*t*(t*(t*6 - 15) + 10)   # 6t^5 - 15t^4 + 10t^3 (C2-continuous)
```

The mixing constants above are an example of a decent integer hash. Any well-mixed 32-bit hash works; what matters is that it is integer-only, so it is bit-identical across platforms.

### 3.2 Perlin (gradient) noise

Ken Perlin's gradient noise (SIGGRAPH 1985, "An Image Synthesizer"; revised in "Improving Noise", SIGGRAPH 2002) assigns a pseudo-random *gradient* to each lattice point and interpolates the dot products of those gradients with the offset vectors. The value at every lattice point is 0, so features do not align with the grid as obviously as value noise does. The 2002 revision replaced the cubic fade with the quintic above (removing second-derivative discontinuities) and used a fixed set of 12 gradient directions in 3D.

```text
# permutation table: 256 entries shuffled with the seed, then doubled to 512
function init_perm(seed):
    p = [0..255]; rng = PRNG(seed); rng.shuffle(p)
    perm = p + p

GRAD2 = [(1,1),(-1,1),(1,-1),(-1,-1),(1,0),(-1,0),(0,1),(0,-1)]

function perlin2(x, y) -> float, roughly in [-1, 1]:
    ix = floor(x); iy = floor(y)
    fx = x - ix;   fy = y - iy
    ix = ix AND 255; iy = iy AND 255
    g00 = GRAD2[perm[ix   + perm[iy  ]] AND 7]
    g10 = GRAD2[perm[ix+1 + perm[iy  ]] AND 7]
    g01 = GRAD2[perm[ix   + perm[iy+1]] AND 7]
    g11 = GRAD2[perm[ix+1 + perm[iy+1]] AND 7]
    n00 = dot(g00, (fx,   fy  ))
    n10 = dot(g10, (fx-1, fy  ))
    n01 = dot(g01, (fx,   fy-1))
    n11 = dot(g11, (fx-1, fy-1))
    u = fade(fx); v = fade(fy)
    return lerp(lerp(n00, n10, u), lerp(n01, n11, u), v)   # scale by ~1/0.7 if you need full [-1,1]
```

Notes: the output range is not exactly [-1, 1] and the distribution is bell-shaped (most values near 0). Measure the empirical range on 10^5 samples and normalise, rather than assuming. The permutation table repeats every 256 units; for very large worlds use a coordinate hash (as in 3.1) instead of the table.

### 3.3 Simplex noise

Perlin's simplex noise (2001 course notes) evaluates gradients on the corners of a simplex (a triangle in 2D, a tetrahedron in 3D) instead of a hypercube: N+1 corners instead of 2^N, so it scales better with dimension and shows fewer directional artefacts. Stefan Gustavson's "Simplex noise demystified" (2005) is the standard plain-language derivation. OpenSimplex and OpenSimplex2 (Kurt Spencer) are popular alternatives that arose partly to avoid a US patent on 3D-and-up simplex noise, a patent that has since expired. Prefer whichever implementation your engine already ships: Godot's `FastNoiseLite` resource offers simplex, Perlin, value, cellular and domain-warp types.

```text
F2 = (sqrt(3) - 1) / 2       # skew factor  ~0.3660254
G2 = (3 - sqrt(3)) / 6       # unskew factor ~0.2113249

function simplex2(x, y) -> float in about [-1, 1]:
    s = (x + y) * F2
    i = floor(x + s); j = floor(y + s)
    t = (i + j) * G2
    x0 = x - (i - t); y0 = y - (j - t)            # offset from first corner
    (i1, j1) = (1, 0) if x0 > y0 else (0, 1)      # which triangle
    x1 = x0 - i1 + G2;      y1 = y0 - j1 + G2
    x2 = x0 - 1 + 2*G2;     y2 = y0 - 1 + 2*G2
    n = 0
    for (cx, cy, gi) in [(x0,y0, grad_index(i,j)), (x1,y1, grad_index(i+i1,j+j1)), (x2,y2, grad_index(i+1,j+1))]:
        t = 0.5 - cx*cx - cy*cy                     # radial falloff
        if t > 0:
            t = t * t
            n += t * t * dot(GRAD2[gi], (cx, cy))
    return 70 * n                                   # 70 is the usual 2D normaliser
```

### 3.4 Worley (cellular) noise

Steven Worley's "A Cellular Texture Basis Function" (SIGGRAPH 1996): scatter feature points (one or more per grid cell, positions from a hash), and return the distance to the nearest (F1), the second nearest (F2), or combinations such as F2 − F1 (cell borders). Uses: cracked earth, scales, stone tiles, cell-like biome masks, and Voronoi regions without building a diagram.

```text
function worley2(x, y, seed) -> (F1, F2, id_of_nearest):
    ix = floor(x); iy = floor(y)
    F1 = F2 = +inf; id = none
    for oy in -1..1: for ox in -1..1:
        cx = ix + ox; cy = iy + oy
        h = hash2(cx, cy, seed)
        px = cx + (h AND 0xFFFF) / 65536          # feature point inside the cell
        py = cy + (h >> 16) / 65536
        d = (px - x)^2 + (py - y)^2               # squared Euclidean; Manhattan or Chebyshev change the look
        if d < F1: F2 = F1; F1 = d; id = h
        elif d < F2: F2 = d
    return (sqrt(F1), sqrt(F2), id)
```

### 3.5 Noise parameter starting points

| Parameter | Meaning | Start | Effect of increasing |
|---|---|---|---|
| frequency (1 / scale) | Features per world unit | Largest feature you want ≈ 1/frequency units | Smaller, busier features |
| octaves | Layers of detail in fBm | log2(largest feature / smallest visible feature); 4–6 for terrain | More detail, linear extra cost |
| lacunarity | Frequency multiplier per octave | 2.0 (use ~1.9–2.1 to avoid lattice alignment between octaves) | Detail jumps faster in scale |
| gain (persistence) | Amplitude multiplier per octave | 0.5 | Rougher, noisier result |
| warp strength | Domain-warp displacement | 0.5–4 × the base feature size | More swirled, eroded look; can tear |
| seed offset per octave | Decorrelate octaves | Add a large prime offset per octave | Avoids visible stacking at the origin |

---

## 4. fBm and its variants

Fractional Brownian motion (fBm) sums octaves of a noise at doubling frequency and halving amplitude. The result looks like natural terrain because natural surfaces are roughly self-similar across scales.

```text
function fbm(x, y, octaves=5, lacunarity=2.0, gain=0.5, seed=0) -> float in about [-1, 1]:
    sum = 0; amp = 1; freq = 1; norm = 0
    for o in 0 .. octaves-1:
        sum  += amp * noise(x*freq + o*131.7, y*freq + o*71.3, seed + o)   # decorrelate octaves
        norm += amp
        amp  *= gain
        freq *= lacunarity
    return sum / norm
```

| Variant | Formula per octave | Look | Typical use |
|---|---|---|---|
| fBm | `n` | Rolling hills, clouds | Base terrain, moisture, temperature |
| Turbulence (billow) | `abs(n)` | Puffy, creased | Clouds, smoke, rocky ground |
| Ridged multifractal | `(1 - abs(n))^2`, weighted by the previous octave | Sharp ridges, mountain chains | Mountains, canyons (inverted) |
| Hybrid / heterogeneous | Scale each octave by the running value | Smooth valleys, rough peaks | Terrain where lowlands should be flat |
| Terraced | `round(h * k) / k`, blended | Steps, mesas | Stylised terrain, readable heights for gameplay |

The ridged and hybrid multifractal forms are from F. Kenton Musgrave's chapters in *Texturing and Modeling: A Procedural Approach* (Ebert et al.).

**Cost:** octaves × base-noise cost. A 256 × 256 heightmap at 5 octaves is about 330k noise evaluations: well under a frame on a modern phone in native code, but often tens of milliseconds in an interpreted script. Bake it on a worker thread, or use the engine's native noise.

---

## 5. Domain warping

Domain warping distorts the *input* coordinates of a noise function with another noise function. Inigo Quilez's article on domain warping (iquilezles.org) popularised the nested form. It turns regular blobby fBm into flowing, eroded or marbled shapes at the cost of 2–3× the evaluations.

```text
function warped(x, y):
    qx = fbm(x + 0.0, y + 0.0);  qy = fbm(x + 5.2, y + 1.3)          # first warp field
    rx = fbm(x + 4*qx + 1.7, y + 4*qy + 9.2)
    ry = fbm(x + 4*qx + 8.3, y + 4*qy + 2.8)                          # second warp field
    return fbm(x + 4*rx, y + 4*ry)
```

Practical notes:
- The constants (5.2, 1.3 and so on) only decorrelate the warp fields; any distinct offsets work.
- Warp strength (4 above) is in units of the base frequency. Above about 6 the result starts to look torn.
- Use the warp fields themselves (`q`, `r`) as extra outputs: they make good colour or biome-variation channels.
- For gameplay maps, warp *masks* (where the coast is) rather than heights; that keeps slopes walkable.

---

## 6. Using noise for terrain, biomes and placement

1. **Redistribution.** Raw fBm clusters around 0. Push it with `h' = sign(h) * abs(h)^p` (p > 1 flattens valleys and sharpens peaks), or remap through a designer-authored curve (a lookup table of 16–64 points). The curve is the single best art-direction handle.
2. **Island or arena masks.** Multiply by a radial falloff `1 - smoothstep(r0, r1, distance_to_center)` so the edges are water or walls. Mobile maps need hard, readable borders.
3. **Biomes from two fields.** Height × moisture (or temperature × moisture) into a 2D lookup table, Whittaker-diagram style. Use different seeds and frequencies for each field, and a lower frequency for moisture than for height.
4. **Placement from noise and points.** Use noise as a *density mask* and Poisson disk (§12) for the positions: `accept candidate if rng.float() < density(x, y)`. Never place objects on raw noise thresholds alone; you get clumps and stripes.
5. **Gameplay carve-outs.** After generating, stamp hand-made constraints: flatten the spawn, guarantee a path (A* over a cost field derived from slope), and clear sight lines around objectives.
6. **Chunk seams.** Because noise is a function of world coordinates, chunks agree at their borders automatically. Post-processes that look at neighbours (erosion, CA smoothing) do not; give each chunk a skirt of 1–2 cells from its neighbours, or run them on overlapping windows.
7. **Precision far from the origin.** 32-bit floats keep about 7 significant digits: at x = 100,000 the spacing between representable floats is about 0.008, which makes high-frequency octaves stair-step. For endless worlds, feed the noise with chunk-local coordinates plus a chunk offset computed in integers or doubles, or wrap the noise domain.

---

## 7. Cellular-automata caves

Fill the grid randomly, then repeatedly apply a neighbourhood rule that turns cells into walls where walls are common and into floor where floor is common. This rule family was popularised by the roguelike community (RogueBasin's cave articles) and studied for infinite cave levels by Johnson, Yannakakis and Togelius ("Cellular automata for real-time generation of infinite cave levels", PCG Workshop 2010).

```text
function ca_cave(w, h, rng, fill=0.45, steps=4, birth=5):
    grid[y][x] = WALL if border(x, y) or rng.float() < fill else FLOOR
    repeat steps times:
        next = copy(grid)
        for each cell (x, y):
            n = count of WALL in the 3x3 block around (x, y), counting the cell itself
                and treating out-of-bounds as WALL
            next[y][x] = WALL if n >= birth else FLOOR
        grid = next                               # double-buffer; never update in place
    return grid

function keep_largest_region(grid):
    regions = flood_fill_all(grid, FLOOR, 4-connected)
    largest = max(regions, by size)
    for r in regions except largest: fill r with WALL      # or: tunnel r to largest (below)
    return grid, size(largest) / total_floor_before

function connect_regions(grid, regions, rng):
    # Minimum spanning tree over region centroids, then dig an L-shaped or drunkard tunnel per edge
    edges = mst(complete_graph(centroids(regions)), weight=manhattan)
    for (a, b) in edges: dig_tunnel(grid, closest_cells(a, b), width=1 or 2)
```

**Measured parameter sweep (this skill's own test, not a published figure).** 48 × 32 grid, solid border, Moore-neighbourhood rule "wall if ≥ 5 of 9", 4 steps, 300 seeds per row; metrics from `scripts/pcgkit.py era`:

| Initial fill | Mean wall density | Mean connectivity (largest region / all floor) | Median floor regions | Share with connectivity ≥ 0.9 |
|---|---|---|---|---|
| 0.40 | 0.34 | 0.995 | 1 | 99% |
| 0.45 | 0.47 | 0.93 | 2 | 79% |
| 0.50 | 0.63 | 0.66 | 5 | 14% |
| 0.55 | 0.78 | 0.40 | 9 | 0% |

Read it this way: the rule has a sharp phase transition between 0.45 and 0.50 fill. Below it you get one big open cave; above it, an archipelago of pockets. Tune fill in steps of 0.01 near your target, and always run the region pass, because even at 0.45 about one map in five fails a 0.9 connectivity bar. Re-run the sweep for your own grid size and rule: border effects shift the curve on small grids.

Variants:
- **Two-phase rule** (common in roguelike tutorials): for the first few steps, also turn a cell to wall if it has 2 or fewer walls within radius 2. This breaks up large open areas into pillars; then run plain smoothing steps.
- **Seeding structure:** stamp a guaranteed floor corridor (from a drunkard walk or a spline) before smoothing, and lock those cells; connectivity rises without tunnelling afterwards.
- **Infinite caves:** generate per chunk with a margin of `steps` cells read from neighbouring chunks' initial noise (the initial fill is a pure hash of world coordinates), so chunk borders match.

Cost: O(w × h × steps × 9). Trivial on device for grids up to a few hundred cells per side.

---

## 8. Drunkard walk

A random walker carves floor until a coverage target is reached. The result is always connected because it is one path.

```text
function drunkard(w, h, rng, coverage=0.40, max_steps=w*h*20, bias=None):
    grid = all WALL
    (x, y) = center; grid[y][x] = FLOOR; carved = 1
    target = coverage * (w-2) * (h-2)
    steps = 0
    while carved < target and steps < max_steps:
        dir = rng.pick(DIRS4) if bias is None else biased_pick(DIRS4, bias, rng)
        (x, y) = clamp_to_interior(x + dir.x, y + dir.y)
        if grid[y][x] == WALL: grid[y][x] = FLOOR; carved += 1
        steps += 1
    return grid
```

Tuning and variants:
- Plain walks spend most time re-visiting carved floor. Expected steps rise steeply with coverage: past about 50% coverage, cost and blobbiness both grow quickly. 30–45% is the useful range.
- **Momentum bias:** repeat the previous direction with probability 0.5–0.7 for longer, corridor-like tunnels.
- **Multiple walkers:** start 3–6 walkers from carved cells, each with a step budget, for branching caves.
- **Room stamps:** with probability p per step (0.01–0.03), carve a 3×3 to 5×5 room at the walker's position.
- **Bias toward the unexplored:** weight directions by distance to the nearest uncarved region to spread coverage, for maps that must fill a screen.

Cost: O(steps). Steps can be large; always set `max_steps`.

---

## 9. BSP rooms

Binary space partitioning recursively splits the map into two parts until the leaves are room-sized, puts a room inside each leaf, then connects sibling leaves bottom-up. Rooms never overlap and the space is used evenly.

```text
function bsp(rect, rng, min_leaf=8, max_leaf=20, depth=0):
    if (rect.w <= max_leaf and rect.h <= max_leaf and rng.float() < 0.3) or depth > 12:
        return Leaf(rect)
    horizontal = (rect.h > rect.w * 1.25) or (rect.w <= rect.h * 1.25 and rng.float() < 0.5)
    span = rect.h if horizontal else rect.w
    if span < 2 * min_leaf: return Leaf(rect)
    cut = rng.int(min_leaf, span - min_leaf)
    (a, b) = rect.split(horizontal, cut)
    return Node(bsp(a, rng, ...), bsp(b, rng, ...))

function place_rooms_and_connect(node, grid, rng):
    if node is Leaf:
        rw = rng.int(4, node.rect.w - 2); rh = rng.int(4, node.rect.h - 2)
        rx = node.rect.x + rng.int(1, node.rect.w - rw - 1)
        ry = node.rect.y + rng.int(1, node.rect.h - rh - 1)
        node.room = Rect(rx, ry, rw, rh); carve(grid, node.room)
        return node.room
    ra = place_rooms_and_connect(node.left, grid, rng)
    rb = place_rooms_and_connect(node.right, grid, rng)
    carve_corridor(grid, center(ra), center(rb), rng)    # L-shape: horizontal then vertical, or vice versa
    return rng.pick([ra, rb])                             # representative room for the parent's connection
```

Notes: the aspect-ratio rule (split the longer side) prevents sliver leaves. BSP produces a tree, so there are **no loops**: add 1–3 extra corridors between rooms that are spatially close but far apart in the tree. Otherwise the map plays as a series of dead ends with forced backtracking. The look is gridded; vary room shapes (L-rooms, CA blobs inside leaves) to hide it.

---

## 10. Room-and-corridor

The Rogue (1980) lineage. Three common implementations, from simplest to most controllable:

**(a) Place-and-reject.** Try N random rectangles, keep those that do not overlap (with a 1–2 cell margin), connect each new room to the previous one with an L-corridor.

```text
rooms = []
for attempt in 1..max_attempts:                       # e.g. 200 attempts for ~12 rooms
    r = Rect(rng.int(...), rng.int(...), rng.int(min_w, max_w), rng.int(min_h, max_h))
    if all(not r.inflate(margin).intersects(o) for o in rooms):
        carve(grid, r)
        if rooms: carve_corridor(grid, center(rooms[-1]), center(r), rng)
        rooms.append(r)
    if len(rooms) == target_rooms: break
```

**(b) Separation, Delaunay, MST, extra edges.** Popularised by the developer of TinyKeep in a widely shared 2013 write-up: spawn many rooms in a small circle, push them apart (a simple separation step, or a physics engine) until none overlap, select the larger rooms as "main" rooms, triangulate their centres (Delaunay, §13), take the minimum spanning tree so everything is connected, then add back roughly 10–15% of the remaining Delaunay edges to create loops. Corridors are L-shapes along the kept edges; small rooms crossed by corridors become part of them.

```text
rooms = [random_rect_in_circle(radius, rng) for i in 1..150]
repeat until no overlaps (cap iterations):
    for each overlapping pair (a, b): push a and b apart along the axis of least overlap, snap to grid
main = [r for r in rooms if r.w >= 1.25*mean_w and r.h >= 1.25*mean_h]
tri = delaunay([center(r) for r in main])
tree = mst(tri.edges, weight=length)
extra = rng.sample(tri.edges - tree, k=round(0.12 * len(tri.edges - tree)))
for (a, b) in tree + extra: carve_L_corridor(a, b), absorbing any small rooms it crosses
```

**(c) Accretion.** Start with one room; repeatedly pick a random room template, try to attach it to a random wall cell of the existing dungeon with a door, keep it if it fits. Brogue's developer has described a method of this kind. It produces organic, dense layouts and supports hand-made room templates naturally, which is the bridge to template assembly (§20).

Loop ratio is the key design dial. Tree-like maps (0 extra edges) force backtracking and make every dead end a reward location; highly looped maps (25% or more) remove backtracking and support chase gameplay and flanking. Pick the ratio from the game's verbs, not from looks.

---

## 11. Wave function collapse

Maxim Gumin's WaveFunctionCollapse (GitHub, 2016, MIT licence) generates output that is locally similar to an input example. It builds on Paul Merrell's model synthesis (2007). Karth and Smith ("WaveFunctionCollapse is Constraint Solving in the Wild", FDG 2017) showed it is a constraint solver: a minimum-entropy variable-ordering heuristic plus arc-consistency propagation, usually *without* backtracking. Treat it as a CSP solver with a good heuristic. That framing explains both its power and its failure modes.

### 11.1 Two models

| | Tiled (simple tiled) model | Overlapping model |
|---|---|---|
| Input | A tileset plus adjacency rules (explicit pairs, or edge "sockets" that must match) | An example bitmap or tilemap |
| Unit of the output | One tile per cell | One N×N pattern per cell (N = 2 or 3; 3 is common) |
| Adjacency | Declared by the designer | Two patterns may be neighbours if they agree on their overlap |
| Weights | Designer-set tile frequencies | Pattern frequencies counted in the example |
| Symmetry | Declared per tile (rotations and reflections allowed) | Optional augmentation: add rotated and reflected patterns |
| Best for | Modular kits (dungeon tiles, roads, pipes, buildings in 3D) | Texture-like maps "in the style of" a sample |
| Typical pattern count | Tens of tiles × rotations | Hundreds to thousands of patterns for a 3×3 window over a 32×32 sample |

### 11.2 Core algorithm (both models)

```text
# wave[c] = set of patterns still possible at cell c (a bitset in practice)
# compatible[c][p][d] = number of patterns at neighbour c+d that support p at c (AC-4 style counts)

function wfc(W, H, patterns, weights, propagator, rng, max_restarts=20):
    for attempt in 1..max_restarts:
        init wave: every cell allows all patterns; init compatible counts
        apply_preconstraints(wave)              # borders, fixed cells, path cells; propagate after
        loop:
            c = argmin over undecided cells of entropy(c) + rng.float() * 1e-6   # tiny noise breaks ties
            if no undecided cell: return decode(wave)                          # success
            p = rng.weighted(wave[c], weights)   # collapse
            ban all q != p at c (push each ban on a stack)
            if not propagate(): break            # contradiction: restart (or backtrack)
    return FAIL

function entropy(c):                             # Shannon entropy of the remaining weights
    S = sum(w[p] for p in wave[c]); SL = sum(w[p] * ln(w[p]) for p in wave[c])
    return ln(S) - SL / S

function propagate():
    while stack not empty:
        (c, p) = stack.pop()
        for d in DIRECTIONS:
            n = c + d
            for q in propagator[p][d]:           # patterns at n that p supported
                compatible[n][q][opposite(d)] -= 1
                if compatible[n][q][opposite(d)] == 0 and q in wave[n]:
                    ban q at n; push (n, q)
                    if wave[n] is empty: return false
    return true
```

Gumin's implementation counts supports per direction like this, so each ban costs only the patterns it affects.

### 11.3 Making WFC shippable

1. **Contradictions are normal.** The restart rate depends on the tileset. Measure it: run 1,000 seeds offline and record the success rate and the median and p95 time. If more than about 5% of runs fail, fix the tileset (add transition tiles, loosen sockets) before adding backtracking.
2. **Backtracking** (save the wave before each collapse and roll back on contradiction, with a depth cap) turns most failures into successes at the cost of memory. Use it for large outputs where restarts are too costly.
3. **Global properties need explicit constraints.** WFC guarantees local agreement only. For connectivity, solvability, a required exit or a count of special tiles: (a) pre-collapse a path skeleton (generated by a drunkard walk or A*) into the wave before solving; (b) add a global constraint checked during propagation, as libraries such as Boris the Brave's DeBroglie (C#) do with path and count constraints; or (c) generate, then verify and reject (`generate-and-test.md`).
4. **Ground the edges.** Fix the border cells to "outside" or "wall" patterns. Unconstrained borders produce half-structures cut off at the edge.
5. **Weights steer style.** Raising a floor pattern's weight opens the map; lowering a rare decoration's weight keeps it rare. Weights do not give hard counts; use constraints or a post-pass for "exactly 3 chests".
6. **Chunked or infinite WFC.** Solve chunk by chunk with the already-solved neighbour edges as pre-constraints. Contradictions at chunk seams are the main risk; re-solve a slightly larger window around a failed seam.
7. **Mobile budget.** On device, keep outputs small (for example up to 32×32 cells with 50–150 tiles), run on a worker thread with a time budget, and fall back to a cached or pre-generated layout if the budget runs out. Large or 3D WFC should run offline, with its output shipped as data.

### 11.4 Overlapping-model extraction

```text
function extract_patterns(sample, N, symmetry):
    counts = {}
    for each (x, y) in sample (wrapping if the sample tiles, else only full windows):
        base = window(sample, x, y, N)
        for v in symmetry_variants(base, symmetry):     # up to 8: 4 rotations x 2 reflections
            counts[v] += 1
    patterns = keys(counts); weights = values(counts)
    for each pair (p, q) and each direction d:
        agrees = overlap_of(p shifted by d) == overlap_of(q)   # N x (N-1) region must match
        if agrees: propagator[p][d].add(q)
    return patterns, weights, propagator
```

The output pixel or tile at a cell is the top-left element of its collapsed pattern.

---

## 12. Poisson disk sampling

Points that are random but never closer than r to each other ("blue noise"). Robert Bridson's algorithm ("Fast Poisson Disk Sampling in Arbitrary Dimensions", SIGGRAPH 2007 sketch) runs in O(n) using a background grid with cell size r/√d, so each cell holds at most one point.

```text
function poisson(width, height, r, rng, k=30):
    cell = r / sqrt(2)                             # 2D
    gw = ceil(width / cell); gh = ceil(height / cell)
    grid = gw x gh array of -1
    p0 = (rng.float()*width, rng.float()*height); points = [p0]; active = [0]
    grid[cell_of(p0)] = 0
    while active not empty:
        i = rng.pick_index(active); found = false
        for t in 1..k:
            a = rng.float() * 2*PI; d = r * (1 + rng.float())       # annulus [r, 2r)
            q = points[active[i]] + (cos(a)*d, sin(a)*d)
            if in_bounds(q) and no point within r in the 5x5 grid cells around cell_of(q):
                points.append(q); active.append(len(points)-1); grid[cell_of(q)] = len(points)-1
                found = true; break
        if not found: remove active[i]
    return points
```

- k = 30 candidates per active point is Bridson's suggested value; lower k is faster but leaves more gaps.
- Expected count: in this skill's own measurement (100 × 100 area, r = 1, 5 seeds) Bridson produced about `area / (1.59 r²)` points with k = 30 and `area / (1.69 r²)` with k = 10. Use this to size budgets, then measure your own r and bounds.
- **Variable density:** make r a function of position (`r(x, y) = lerp(r_min, r_max, mask(x, y))`) and check against the larger of the two radii.
- **Determinism trap:** `cos` and `sin` are not bit-identical across platforms (`determinism-and-seeds.md` §5). For cross-platform identical placement, use a precomputed table of unit vectors, or do grid-jittered sampling (one random point per grid cell with a minimum-distance reject) in fixed point.
- **Cheap alternative on device:** jittered grid (one point per cell, jitter up to 0.4 × cell). Not true blue noise, but often visually sufficient for grass and debris.

---

## 13. Voronoi diagrams, Delaunay triangulation, Lloyd relaxation

The Voronoi diagram of a point set assigns every location to its nearest point. The Delaunay triangulation is its dual: two points share a Delaunay edge exactly when their Voronoi cells share a border. Delaunay gives you a planar neighbour graph (for corridors, roads, region adjacency); Voronoi gives regions (territories, biomes, districts, cracked surfaces).

**Bowyer–Watson** (Bowyer 1981; Watson 1981) builds a Delaunay triangulation incrementally. It is simple and fine for the hundreds to low thousands of points typical in games. Fortune's sweep-line algorithm (1986) computes Voronoi directly in O(n log n) if you need more.

```text
function bowyer_watson(points):
    tris = [super_triangle_containing(points)]
    for p in points:
        bad = [t for t in tris if p is inside circumcircle(t)]
        boundary = edges of bad triangles that are not shared by two bad triangles
        tris = tris - bad
        for e in boundary: tris.add(Triangle(e.a, e.b, p))
    remove triangles that use a super-triangle vertex
    return tris
```

Robustness: the in-circumcircle test on floats fails on near-degenerate input (four nearly co-circular points). Snap points to a grid and jitter them by a tiny seeded amount, or use exact integer predicates on grid coordinates.

**Grid Voronoi (no diagram).** For tile maps, label each cell with the nearest seed using a multi-source BFS (gives Manhattan or Chebyshev regions) or a brute-force nearest search for up to ~100 seeds. This is simpler and deterministic.

**Lloyd relaxation** (Lloyd's algorithm): move each seed to the centroid of its Voronoi cell and repeat. Two or three iterations turn clumpy random points into evenly sized, rounder cells; many more converges toward a hexagonal look, which reads as artificial. Typical use is a "polygon map" pipeline: Poisson or random points → 2 Lloyd iterations → Voronoi cells as map polygons → Delaunay edges as adjacency → elevation, moisture and rivers on the graph.

---

## 14. L-systems

Aristid Lindenmayer (1968) introduced parallel string rewriting to model plant growth; Prusinkiewicz and Lindenmayer's *The Algorithmic Beauty of Plants* (1990) is the standard reference. Every symbol is rewritten simultaneously each generation, and the final string is drawn by a "turtle".

```text
axiom = "X"
rules = { "X": "F+[[X]-X]-F[-FX]+X",  "F": "FF" }      # a classic fractal plant
angle = 25 degrees

function expand(axiom, rules, n, rng):
    s = axiom
    repeat n times:
        s = concat(rule_for(ch, rules, rng) if ch in rules else ch for ch in s)
    return s

function interpret(s, step, angle):                    # turtle graphics
    stack = []; pos = (0,0); heading = 90 degrees
    for ch in s:
        if ch == 'F': new = pos + step*dir(heading); emit_segment(pos, new); pos = new
        elif ch == '+': heading += angle
        elif ch == '-': heading -= angle
        elif ch == '[': stack.push((pos, heading))
        elif ch == ']': (pos, heading) = stack.pop()
```

- **Stochastic L-systems:** several right-hand sides per symbol with probabilities, so each plant differs. Pass the seeded rng.
- **Parametric L-systems:** symbols carry numbers (`F(l)` → `F(l*0.7)`) for tapering branch lengths and widths.
- **Budget:** string length grows exponentially (in the plant above, each generation quadruples the X count and doubles the F count). Cap generations at 4–6 and cap total segments; precompute variants offline and instance them.
- **Game uses beyond plants:** river and road networks, cave branching, lightning and crack VFX, decorative patterns, and "dungeon as a growth process" (rooms as symbols).

---

## 15. Shape grammars and split grammars

George Stiny and James Gips introduced shape grammars (1971): rules replace a shape matching a pattern with other shapes. The practical descendant in games is the **split grammar** used in CGA shape (Müller, Wonka, Haegler, Ulmer and Van Gool, "Procedural Modeling of Buildings", SIGGRAPH 2006): a box is recursively split into floors, bays and tiles, and leaves become meshes.

```text
rules:
  Lot      -> extrude(height=rng.int(3,8)*3.0) Mass
  Mass     -> comp(faces) { front: Facade | sides: SideFacade | top: Roof }
  Facade   -> split(y) { 4.0: GroundFloor | ~3.0: Floor* }        # '~' = flexible size, '*' = repeat
  Floor    -> split(x) { 0.5: Wall | ~2.5: WindowBay* | 0.5: Wall }
  WindowBay-> 0.7: Window | 0.2: Balcony | 0.1: Wall              # stochastic choice

function derive(shape, symbol, rng, depth):
    if depth > MAX or symbol is terminal: emit(shape, symbol); return
    rule = choose_rule(symbol, shape, rng)          # may depend on size, position, neighbours
    for (child_shape, child_symbol) in rule.apply(shape):
        derive(child_shape, child_symbol, rng, depth+1)
```

Use split grammars for buildings, facades, furniture layouts, UI-like structured props, and spaceship hulls. Their strength is guaranteed structural regularity; their weakness is sameness when the rule set is small. Budget for 30–100 rules for a convincing city style, and use occlusion and level-of-detail rules (no balconies on faces that are never seen) on mobile.

---

## 16. Graph grammars: missions, spaces, lock-and-key

Joris Dormans ("Adventures in level design: generating missions and spaces for action adventure games", PCG Workshop 2010; with Bakkes, "Generating missions and spaces for adaptable play experiences", IEEE TCIAIG 2011) separates a level into a **mission** (the abstract sequence of tasks: keys, locks, bosses, rewards) and a **space** (the geometry that hosts it). Graph grammars generate the mission; a second transformation embeds it in space. The point is that *pacing and logic are designed explicitly* instead of hoped for.

```text
# Mission graph rewriting. Nodes: start, task, key(k), lock(k), boss, reward, goal. Directed edges = "must come before".
rules = [
  "Start   -> start -> Chain -> goal",
  "Chain   -> task -> Chain                    (weight 3)",
  "Chain   -> key(k) -> Chain -> lock(k) -> Chain   (weight 2, k = fresh id, max 3 keys)",
  "Chain   -> task -> boss -> reward           (weight 1, terminal)",
  "task    -> task || task  (parallel branch, rejoin)   (weight 1)",
]
function generate_mission(rng, min_tasks=6, max_nodes=20):
    G = graph("Start")
    while G has nonterminals and size(G) < max_nodes:
        nt = rng.pick(nonterminal nodes of G)
        rule = rng.weighted(applicable rules for nt)
        G = rewrite(G, nt, rule)
    force-terminate remaining nonterminals with their terminal rule
    return G if count(task) >= min_tasks else retry
```

**From mission to space.** Simple, robust approach for mobile: lay the mission graph out on a coarse room grid (each mission node becomes a room, each edge a door) with a search over placements (backtrack when a node cannot be placed adjacent to its parent), then fill each room from a template pool matching its node type (key room, lock door, boss arena).

**Lock-and-key validation** (always run it, the grammar alone is not proof): search over states (room, keys held). The level is valid if the goal is reachable, and every lock(k) is reachable only after key(k). Also check there is no "key behind its own lock".

```text
function valid_lock_key(rooms, doors, start, goal):
    seen = {(start, {})}; queue = [(start, {})]
    while queue:
        (r, keys) = queue.pop()
        keys = keys + keys_in(r)
        if r == goal: return true
        for (r2, needs) in doors[r]:
            if needs is none or needs in keys:
                if (r2, keys) not in seen: seen.add((r2, keys)); queue.push((r2, keys))
    return false
```

**Cyclic generation.** Dormans' later "cyclic" approach, used in *Unexplored* (Ludomotion, 2017), starts from loops instead of trees: a main cycle between entrance and goal, with patterns such as "lock on the short path, key on the long path" or "hidden shortcut back to the start". Loops create the feeling of an authored place. Use cycles as the top-level rule set when backtracking feels bad in a tree layout.

---

## 17. Agent-based generation

Software agents move through the world and modify it with local rules. They are good at producing features with a "process history": tunnels, rivers, erosion, settlements. Doran and Parberry ("Controlled procedural terrain generation using software agents", IEEE TCIAIG 2010) used specialised agents (coastline, smoothing, beach, mountain, river) with per-agent budgets that act as designer controls.

```text
function digger(grid, rng, steps=2000, turn_p0=0.05, room_p0=0.02):
    (x, y) = center; dir = rng.pick(DIRS4); turn_p = turn_p0; room_p = room_p0
    for i in 1..steps:
        carve(grid, x, y); (x, y) = step_in_bounds(x, y, dir)
        if rng.float() < turn_p: dir = rng.pick(perpendicular(dir)); turn_p = turn_p0
        else: turn_p += 0.02                         # the longer it goes straight, the likelier a turn
        if rng.float() < room_p: carve_room(grid, x, y, rng.int(3,6), rng.int(3,6)); room_p = room_p0
        else: room_p += 0.01
```

Controls are intuitive (budgets, probabilities, which agents run and in what order), but global properties are not guaranteed and results are sensitive to agent ordering. Run validators afterwards. Agents also make good *evaluators*: a simulated player agent walking a level is the cheapest playability test (`generate-and-test.md`).

---

## 18. Constraint solving

Describe *what* must be true and let a solver find assignments. Strong guarantees (exactly N enemies, every room reachable, a puzzle with a unique solution) in exchange for unpredictable run time.

- **CSP with backtracking:** variables (cells, room types), domains, constraints; heuristics MRV (pick the most constrained variable), LCV (try the least constraining value first), forward checking or arc consistency. WFC is a special case without backtracking (§11).
- **SAT/SMT:** encode as Boolean clauses (or with Z3, integers and arithmetic). Good for "exists or not" questions and uniqueness checks: solve, add a clause forbidding the found solution, and solve again. If unsatisfiable, the solution is unique.
- **Answer set programming:** Adam Smith and Michael Mateas ("Answer Set Programming for Procedural Content Generation: A Design Space Approach", IEEE TCIAIG 2011) framed PCG as declaring a design space of choice rules plus integrity constraints and letting an ASP solver (for example clingo from the Potassco project) enumerate valid artefacts.

```text
function solve(assignment, vars, domains, constraints, rng):
    if all vars assigned: return assignment
    v = argmin over unassigned vars of |domains[v]|            # MRV
    for value in shuffled_by(rng, domains[v]):                 # random value order = variety
        if consistent(v, value, assignment, constraints):
            pruned = forward_check(v, value, domains)          # remove now-impossible values
            if no domain became empty:
                result = solve(assignment + {v: value}, vars, domains, constraints, rng)
                if result: return result
            restore(domains, pruned)
    return FAIL
```

Practice: put a node or time limit on every solve; randomise value order with the seeded rng for variety; run solvers **offline**. A solver that takes 50 ms on a desktop can take far longer on a low-end phone, and its worst case is unbounded.

---

## 19. Search-based PCG, novelty search and MAP-Elites

Togelius, Yannakakis, Stanley and Browne ("Search-based procedural content generation: a taxonomy and survey", IEEE TCIAIG 2011) define search-based PCG as generate-and-test where the test returns a *number* (fitness) and a search algorithm, usually evolutionary, improves candidates. The three design decisions are the **representation** (direct tiles vs indirect parameters vs grammar genomes), the **evaluation function** (direct metrics, simulation-based play, or interactive human rating), and the **search algorithm**.

```text
function evolve(pop_size=50, generations=200, rng):
    pop = [random_genome(rng) for i in 1..pop_size]
    for g in 1..generations:
        scored = [(fitness(decode(x)), x) for x in pop]         # fitness can include a solver or bot run
        elite = top 20% of scored
        children = []
        while len(children) < pop_size - len(elite):
            a, b = tournament(scored, k=3, rng), tournament(scored, k=3, rng)
            children.append(mutate(crossover(a, b, rng), rng))
        pop = genomes(elite) + children
    return best of pop
```

- **Constraint handling:** FI-2Pop (Kimbrough et al., 2008) keeps a feasible and an infeasible population; infeasible individuals evolve toward feasibility (minimise constraint violations) and feasible ones toward fitness. This works better than penalty terms for levels that must be playable.
- **Novelty search** (Lehman and Stanley, 2011): reward being different from an archive of previous solutions instead of a fitness. It avoids deception and yields varied content.
- **MAP-Elites** (Mouret and Clune, 2015): split a 2D or 3D behaviour space (for example linearity × difficulty) into cells and keep the best individual per cell. The output is a *map of good, different levels*, which is exactly what a level pool or a difficulty ladder needs. Pair it with expressive range axes (`generate-and-test.md`).

```text
archive = {}                                   # cell -> (fitness, genome)
for i in 1..iterations:
    x = mutate(rng.pick(archive.values()).genome) if len(archive) > init_n else random_genome(rng)
    lvl = decode(x)
    if not feasible(lvl): continue             # e.g. solver says unsolvable
    cell = discretise(behaviour(lvl))          # e.g. (linearity bin, solver min_moves bin)
    if cell not in archive or fitness(lvl) > archive[cell].fitness: archive[cell] = (fitness(lvl), x)
```

Cost: thousands to millions of evaluations. Always offline, always with a cache of evaluations keyed by genome hash.

---

## 20. Composition patterns

Production generators are pipelines and hybrids, rarely a single algorithm.

1. **Macro to micro.** Graph (mission) → layout (rooms on a grid) → room content (templates, WFC) → decoration (Poisson + noise masks) → validation. Each stage has its own seed stream and its own validator.
2. **Templates and chunks.** Hand-authored pieces assembled by rules. *Spelunky* (Mossmouth, 2008/2012) lays a 4×4 grid of rooms, walks a guaranteed solution path from top to bottom, picks room templates by the path's needs (open left/right, drop down), and randomises template cells (described in Derek Yu's book *Spelunky*, Boss Fight Books 2016, and Darius Kazemi's interactive "Spelunky Generator Lessons"). This gives handmade quality and guaranteed traversal.
3. **Hybrid authored/procedural.** Motion Twin's Sébastien Benard described *Dead Cells* (2017–2018) as a hand-designed level "concept graph" per biome, filled with hand-made room tiles chosen procedurally (Gamasutra, 2017, "Building the Level Design of a procedurally generated Metroidvania: a hybrid approach"). Use this when the game's quality bar is handmade but you need replayability.
4. **Generate-and-repair.** Run a cheap constructive generator, then repair (tunnel disconnected regions, move a misplaced key, delete an unreachable chest) instead of rejecting. Repairs must be validated too.
5. **Offline generation, online selection.** Generate 10–100× more than you need offline, verify, cluster by metrics, and ship a curated pool with metadata (difficulty, tags). The device only selects by seed. This is the safest pattern for mobile puzzle games and daily challenges.

---

## 21. Cost and suitability on device

Orders of magnitude for a typical mid-range phone and native or compiled code; interpreted scripting can be 10–50× slower. Measure on your low-tier reference device (`mobile-performance`).

| Algorithm | Complexity | Typical size | On device at runtime? | Notes |
|---|---|---|---|---|
| Value/Perlin/simplex noise | O(samples × octaves) | 256² × 5 octaves | Yes (prefer engine native) | Bake to texture or array on a worker thread |
| Domain warp | 3× fBm | 256² | Yes, offline for large maps | |
| Cellular automata | O(cells × steps × 9) | 100² × 5 steps | Yes | Plus a flood fill |
| Drunkard / agents | O(steps) | 10⁴–10⁵ steps | Yes | Cap steps |
| BSP / room placement | O(rooms log rooms) | 10–50 rooms | Yes | |
| Delaunay (Bowyer–Watson) | O(n log n) average, O(n²) worst | ≤ 1,000 points | Yes for small n | Robust predicates |
| Poisson disk (Bridson) | O(n × k) | 10³–10⁴ points | Yes | Trig determinism caveat |
| WFC | Roughly O(cells × patterns) with restarts | ≤ 32² × ≤ 150 tiles | Small only, with a time budget | Offline for 3D and large maps |
| L-system | Exponential in generations | 4–6 generations | Precompute variants | Cap segments |
| Graph grammar + layout search | Small graphs, backtracking | 10–30 nodes | Yes, with a retry cap | Validate lock-and-key |
| CSP / SAT / ASP | Worst case exponential | Puzzles, small levels | No (offline) | Time limits |
| Search-based / MAP-Elites | 10³–10⁶ evaluations | Any | No (offline) | Cache evaluations |
| LLM generation | Network round trip, seconds | Any | No (offline, verified) | `generate-and-test.md` §8 |
