# Pathfinding and randomness

Two toolkits that decide how a game moves and how it feels fair: graph search (BFS, Dijkstra, A*, jump point search, flow fields) and controlled randomness (PRNG choice, shuffle bags, pseudo-random distribution, alias tables, and the gap between true and perceived fairness). Each section gives when to use the technique, the cost, a compact implementation and the pitfalls that show up on mobile (small CPU budgets, determinism, replay and daily-seed requirements). Algorithms are standard textbook material; the code and decision tables are written for this studio's deterministic core.

## Contents

1. Choosing a search algorithm
2. Grid and graph representation
3. BFS
4. Dijkstra
5. A*
6. Jump point search
7. Flow fields
8. Pathfinding in practice (smoothing, dynamic obstacles, budgets)
9. Choosing a PRNG
10. Seeding, streams and determinism
11. Shuffle bags and deck draws
12. Pseudo-random distribution (pity and streak control)
13. Weighted choice and alias tables
14. Fairness perception
15. Verifying randomness

## 1. Choosing a search algorithm

| Situation | Algorithm | Cost |
|---|---|---|
| Unweighted grid, one source, many targets or distance map | BFS | O(V + E) |
| Weighted costs (terrain, damage), one source | Dijkstra | O((V + E) log V) |
| One source, one target, good heuristic | A* | usually far fewer nodes than Dijkstra |
| Uniform-cost 8-way or 4-way grid, big open maps | Jump point search (JPS) | A* with pruning, large wins in open space |
| Many agents, same target (tower defence, swarms) | Flow field | one BFS/Dijkstra from the target, O(1) per agent |
| Puzzle state spaces (sliding, sokoban) | BFS or A* over states | `puzzle_solver.py --algo bfs|astar` |
| Tiny graphs (under about 100 nodes) | Anything; BFS is fine | negligible |

Default: BFS for unweighted, A* for point-to-point, flow field for crowds. Do not reach for a navmesh in a 2D tile game; do reach for one in 3D free movement (use the engine's).

## 2. Grid and graph representation

- Index cells as `i = y * w + x`; keep `cost: PackedInt32Array` where `0` or a sentinel means blocked.
- Neighbour offsets as a constant table (4-way or 8-way). For 8-way, forbid cutting corners: a diagonal step requires both orthogonal neighbours to be passable (a game rule; decide and test).
- Precompute neighbour lists only if the map is static and large.
- Hex grids: six neighbours in axial coordinates (see `references/math-and-movement.md`); distance heuristic `(|dq| + |dr| + |dq+dr|)/2`.
- Keep search scratch arrays (`came_from`, `dist`, `closed`) allocated once and reset by a version stamp instead of clearing every query:

```gdscript
var _stamp: PackedInt32Array
var _cur: int = 0
func _begin(n: int) -> void:
	if _stamp.size() != n: _stamp.resize(n); _stamp.fill(0); _cur = 0
	_cur += 1
func _seen(i: int) -> bool: return _stamp[i] == _cur
func _mark(i: int) -> void: _stamp[i] = _cur
```

## 3. BFS

Expands in rings; yields shortest path by step count and a full distance map.

```gdscript
func bfs(passable: PackedByteArray, w: int, h: int, start: int) -> PackedInt32Array:
	var dist: PackedInt32Array = PackedInt32Array(); dist.resize(w * h); dist.fill(-1)
	var queue: Array[int] = [start]
	var head: int = 0
	dist[start] = 0
	while head < queue.size():
		var cur: int = queue[head]; head += 1
		var cx: int = cur % w; var cy: int = cur / w
		for d in [[1,0],[-1,0],[0,1],[0,-1]]:
			var nx: int = cx + d[0]; var ny: int = cy + d[1]
			if nx < 0 or ny < 0 or nx >= w or ny >= h: continue
			var n: int = ny * w + nx
			if passable[n] == 0 or dist[n] != -1: continue
			dist[n] = dist[cur] + 1
			queue.append(n)
	return dist
```

Use the head index rather than `pop_front()` (O(n) on arrays). Uses: reachability and softlock checks, flood fill, range highlights (tiles within N moves), puzzle solvers, spawn placement ("farthest reachable tile"). Early exit when the target is dequeued for point-to-point.

```csharp
public static int[] Bfs(bool[] passable, int w, int h, int start) {
    var dist = new int[w * h]; Array.Fill(dist, -1);
    var q = new Queue<int>(); q.Enqueue(start); dist[start] = 0;
    while (q.Count > 0) {
        int c = q.Dequeue(); int cx = c % w, cy = c / w;
        foreach (var (dx, dy) in Dirs4) {
            int nx = cx + dx, ny = cy + dy;
            if ((uint)nx >= (uint)w || (uint)ny >= (uint)h) continue;
            int n = ny * w + nx;
            if (!passable[n] || dist[n] != -1) continue;
            dist[n] = dist[c] + 1; q.Enqueue(n);
        }
    }
    return dist;
}
```

## 4. Dijkstra

Same as BFS with a priority queue on accumulated cost; required when step costs differ (mud 3, road 1, danger tiles 10). Correctness needs non-negative costs. Implementation notes:

- Use a binary heap; engines rarely ship one for GDScript. Write a small min-heap over `[cost, index]` pairs or pack cost and index into one int (`cost << 20 | index`) to keep it allocation-light.
- "Lazy deletion": push duplicates and skip entries whose cost exceeds the best known; simpler than decrease-key.
- Output a cost map for AI "where can I reach with budget B" queries and for influence maps (multi-source Dijkstra from all threats gives danger fields).
- Tie-breaking: with equal costs, prefer lower index so results are deterministic across runs and platforms.

## 5. A*

Dijkstra guided by a heuristic `h(n)` estimating remaining cost: expand lowest `f = g + h`.

| Grid type | Admissible heuristic |
|---|---|
| 4-way, cost 1 | Manhattan |
| 8-way, equal diagonal cost | Chebyshev |
| 8-way, diagonal cost sqrt2 | Octile: `max(dx,dy) + (sqrt2 - 1) * min(dx,dy)` |
| Hex | Hex distance |
| Weighted terrain | Distance times the minimum terrain cost |

Admissible (never overestimates) guarantees an optimal path; multiplying `h` by a weight above 1 (for example 1.2 to 1.5) trades optimality for speed, often fine for game agents.

```gdscript
func astar(start: int, goal: int, w: int, h: int, cost: PackedInt32Array) -> Array[int]:
	var open: Array = [[_h(start, goal, w), start]]      # use a real heap in production
	var g: Dictionary = {start: 0}
	var came: Dictionary = {}
	var closed: Dictionary = {}
	while not open.is_empty():
		open.sort_custom(func(a, b): return a[0] < b[0] or (a[0] == b[0] and a[1] < b[1]))
		var cur: int = int(open.pop_front()[1])
		if cur == goal: return _rebuild(came, cur)
		if closed.has(cur): continue
		closed[cur] = true
		for n in _neighbours(cur, w, h, cost):
			var ng: int = int(g[cur]) + cost[n]
			if not g.has(n) or ng < int(g[n]):
				g[n] = ng; came[n] = cur
				open.append([ng + _h(n, goal, w), n])
	return []
```

Production notes: the sorted-array open list above is for clarity; swap in a heap above a few hundred nodes. Cap expansions (`max_nodes`) and return "no path" or a best-effort partial path, never freezing a frame. Cache paths by `(start, goal, map_version)`. Reconstruct the path by walking `came` back, then reverse.

Tie-breaking for straighter paths: add a tiny cross-product term to `h` or prefer nodes with higher `g` among equal `f`.

## 6. Jump point search

JPS (Harabor and Grastien, 2011) speeds A* on uniform-cost grids by "jumping" along straight lines and diagonals until a forced neighbour or the goal, expanding only those jump points. Properties:

- Wins: large open maps with sparse obstacles; can be an order of magnitude fewer expansions.
- Limits: needs uniform cost (no weighted terrain), static or rarely changing maps (jump results depend on obstacles), and trickier code (corner rules must match your 8-way policy).
- Pre-computation variants exist; skip them on mobile unless profiling demands.

Decision: if your A* spends under about 1 ms per query on target hardware, do not bother. Add JPS only for big uniform maps with many queries per second. Always test JPS output against plain A* on random maps (same path cost) before shipping.

## 7. Flow fields

One search from the target produces, for every cell, the direction to step. Agents just look up their cell.

Procedure:
1. Run BFS/Dijkstra from the goal over passable cells to get a cost field.
2. For each cell, pick the neighbour with the lowest cost: that is its flow vector (optionally store as an index or small direction code).
3. Agents sample the vector at their cell (or bilinearly blend neighbouring vectors for smooth motion), then apply steering for separation (see `game-architecture`).
4. Recompute when obstacles, towers or walls change; throttle (for example at most a few times per second) and spread recomputation across frames for large maps.

Strengths: cost independent of agent count; trivially deterministic; ideal for tower defence, zombie swarms, crowd chasers. Weakness: one field per distinct goal; memory grows with map size times number of goals. Combine: flow field for distant travel, local A* or direct line when within a few cells.

Tower-defence rule: if the player can place blocking towers, validate that a path from spawn to exit still exists (BFS) before accepting the placement; otherwise reject with `rejected{reason:"blocks_path"}` or let enemies attack walls by design.

## 8. Pathfinding in practice

- Smoothing: string-pulling (funnel) or line-of-sight shortcuts: from the current waypoint, skip ahead to the farthest waypoint with clear line of sight (supercover raycast on the grid). Keeps grid paths from looking robotic.
- Dynamic obstacles: either replan on change (cheap with small maps), use local avoidance (steering), or add temporary cost to cells near moving agents. Invalidate cached paths with a map version counter.
- Time budget: process at most N path requests or M node expansions per frame; queue the rest. Agents keep moving along the previous path while waiting.
- Partial paths: when the goal is unreachable, path to the reachable cell nearest the goal and report `unreachable` to the AI rather than spinning.
- Hierarchical search (clusters and abstract graph) only for maps beyond a few thousand cells with many agents.
- Determinism: iterate neighbours in a fixed order, break ties by index, and avoid dictionary iteration order; the core's replays depend on it.
- Navigation in puzzle games is usually not pathing but solving: use `puzzle_solver.py` for solvability and par moves, and keep solver logic out of the shipped core unless hints need it.

## 9. Choosing a PRNG

Requirements for games: fast, small state, reproducible across platforms, good enough statistics, easy to serialise.

| Generator | State | Notes |
|---|---|---|
| PCG32 (O'Neill) | 64-bit state plus stream | Studio default (`core/rng.gd`); good quality, tiny, easy to port to C# |
| xoshiro128/256 variants | 128 or 256 bit | Fast and good; avoid the lowest bits for `**` variants if using plain `+` scramblers |
| SplitMix64 | 64-bit | Great for seeding and for hashing a seed plus index into a sub-seed |
| Xorshift32 | 32-bit | Tiny and fast; weaker statistics; acceptable for cosmetic noise |
| LCG (e.g. classic `a*x + c`) | 32/64-bit | Weak low bits; fine only with the high bits and for throwaway uses |
| Engine global RNG (`randi`, `UnityEngine.Random`, `System.Random`) | hidden | Not for core rules: unseeded, global, and algorithm may differ across engine versions and platforms |
| Cryptographic RNG | OS | For tokens and anything adversaries must not predict (server side); never in the sim |

Rules: one algorithm for the whole core, versioned with `rules_version`; changing it invalidates replays and tuned seeds. Reduce to a range without bias for large `n` (rejection sampling: discard values above the largest multiple of `n`); the template's modulo is fine for small `n` (bias under 2^-20 for `n <= 4096`).

## 10. Seeding, streams and determinism

- Seed from an integer chosen at `new_game`; store it in state (replays) and log it with bug reports.
- Daily or shared seeds: derive from a stable string via a hash you implement (for example FNV-1a 32/64-bit over the UTF-8 date), never from language `hash()` functions that vary by runtime.
- Sub-streams: give each concern its own generator (`loot`, `spawn`, `ai`, `cosmetic`) seeded from `splitmix(seed, concern_id)`. Then adding a draw to AI does not change loot results, which keeps tuned seeds and replays stable.
- Per-entity or per-level seeds: `child = mix(run_seed, index)`; endless content (levels, waves, chunks) reproducible by index regardless of path taken.
- Serialisation: store state as strings in JSON (int64 precision); restore on load. A save mid-run must continue with the identical stream.
- Draw discipline: call RNG only in the core, in a fixed order, once per decision. Never call it in a condition that short-circuits differently between platforms or inside UI code.
- Cosmetic randomness (particles, shake) uses a separate non-core generator and never affects state.
- Server-side validation: if the server replays a run, it needs the same PRNG implementation; keep a test vector (seed and first 10 outputs) in both implementations.

## 11. Shuffle bags and deck draws

Independent draws produce streaks (three identical drops in a row), which players read as unfair or as a bug. A bag draws without replacement from a multiset and refills when empty.

```gdscript
var bag: Array[int] = []
func draw(rng, items: Array[int]) -> int:
	if bag.is_empty():
		bag = items.duplicate()
		for i in range(bag.size() - 1, 0, -1):          # Fisher-Yates
			var j: int = rng.rand_int(i + 1)
			var t: int = bag[i]; bag[i] = bag[j]; bag[j] = t
	return bag.pop_back()
```

Fisher-Yates correctness: swap each position `i` from the end with a random `j` in `[0, i]` inclusive. The common bug is `j` in `[0, n)` for every `i`, which biases results. Never shuffle with a random comparator sort.

Variations: bag of multiples (7 pieces times 2 copies) loosens streak limits; "bag with carry-over" keeps the last item to avoid cross-bag repeats; a deck with discard pile for card games; Tetris-style 7-bag as the canonical example. Bag state must be in the saved core state, including remaining contents and order.

Trade-off: bags make outcomes predictable late in a bag (the last item is known). If predictability harms the design (competitive play), use larger bags or a distribution control (below).

## 12. Pseudo-random distribution (pity and streak control)

Goal: keep the long-run probability `p` while shrinking variance. Two families:

Increasing-probability counter (the technique behind Dota 2's "pseudo-random distribution" for crits and procs): the chance on attempt `n` since the last success is `c * n`. Choose `c` so the overall average success rate equals `p`. The relation is `p = 1 / E[trials]`, where `E[trials] = sum over n of P(first success at n)`; solve `c` numerically once and tabulate it (bisection on `c` for each `p` at build time).

```gdscript
func prd_roll(state: Dictionary, c: float, rng) -> bool:
	state.n += 1
	if rng.rand_float() < minf(c * state.n, 1.0):
		state.n = 0
		return true
	return false
```

Pity and hard guarantees: after `N` failures force success (`if fails >= hard_pity: success`). Soft pity ramps probability from a threshold: `p_n = p + step * max(0, n - soft_start)`. For paid randomness, see `economy-design` and `gacha_calc.py` for computing the effective rate; disclose odds and pity rules (see `legal-ethics`). Pity counters belong in saved state and, for paid draws, on the server.

Streak breakers for failures: bad-luck protection (after K consecutive misses raise the chance); for wins: good-luck brakes (reduce after K successes) only in single-player balance, not in paid contexts.

Choosing: bag for "each of these N outcomes exactly once per cycle", PRD for "proc with average p but no long droughts or streaks", hard pity for "guarantee within N attempts", plain RNG when variance is the point (roguelike surprises, slot-like excitement) and the stakes are low.

## 13. Weighted choice and alias tables

Linear scan with cumulative weights: O(n) per draw, fine for n under about 30.

```gdscript
func pick(weights: PackedFloat32Array, rng) -> int:
	var total: float = 0.0
	for w in weights: total += w
	var r: float = rng.rand_float() * total
	for i in weights.size():
		r -= weights[i]
		if r < 0.0: return i
	return weights.size() - 1                      # float edge case
```

Binary search over a prefix-sum array: O(log n), good for static tables of hundreds of entries.

Alias method (Walker/Vose): O(n) build, O(1) per draw. Worth it for large static tables drawn very often (procedural loot with hundreds of entries, particle or spawn tables).

```gdscript
func build_alias(p: PackedFloat32Array) -> Dictionary:
	var n: int = p.size()
	var prob: PackedFloat32Array = PackedFloat32Array(); prob.resize(n)
	var alias: PackedInt32Array = PackedInt32Array(); alias.resize(n)
	var total: float = 0.0
	for x in p: total += x
	var scaled: Array[float] = []
	for x in p: scaled.append(x * n / total)
	var small: Array[int] = []; var large: Array[int] = []
	for i in n:
		(small if scaled[i] < 1.0 else large).append(i)
	while not small.is_empty() and not large.is_empty():
		var s: int = small.pop_back(); var l: int = large.pop_back()
		prob[s] = scaled[s]; alias[s] = l
		scaled[l] = scaled[l] + scaled[s] - 1.0
		(small if scaled[l] < 1.0 else large).append(l)
	for i in large: prob[i] = 1.0
	for i in small: prob[i] = 1.0
	return {"prob": prob, "alias": alias}

func alias_draw(t: Dictionary, rng) -> int:
	var i: int = rng.rand_int(t.prob.size())
	return i if rng.rand_float() < t.prob[i] else int(t.alias[i])
```

Note: it consumes two draws per sample (fixed, so deterministic). Rebuild when weights change (live-ops remote config), and validate that weights are non-negative with a positive sum.

Weighted without replacement: repeat draws removing the chosen item, or use the key trick (`key = rng.rand_float() ^ (1 / weight)`, take the top k keys) for exactly-k selections.

Conditional tables: filter by level or tags first, then draw from the filtered weights; cache filtered tables per level key.

## 14. Fairness perception

Players misjudge randomness, and the mismatch drives complaints and churn more than the true odds.

| Misperception | What players expect | Design response |
|---|---|---|
| Streaks are suspicious | Alternation, "due" outcomes | Bags or PRD where stakes are felt; hide nothing about odds |
| Stated percentages are optimistic | A "90 percent" shot feels like it should never miss | Games that show hit chances often skew the displayed value in the player's favour at high values; if you do, be consistent and disclose; (the long-running example is the XCOM series, whose designers have discussed adjusting hidden odds on lower difficulties) |
| Own losses outweigh wins | Losses felt about twice as strongly as equal gains (prospect theory, Kahneman and Tversky) | Pad important rolls with mitigation (partial rewards, retries) |
| Near-misses feel meaningful | "Almost won" | Do not manufacture near-misses in paid or chance-for-money contexts; regulators and platform policies increasingly care |
| Coin flips against AI feel rigged | Opponent luck is attributed to cheating | Keep AI on the same rules and RNG visible in the log |
| Difficulty spikes feel like bad luck | Blame the dice | Ensure levels are fair by search and bot evidence (see `progression-difficulty`) |

Principles: make randomness input-side where possible (random options, then skilful choice) rather than output-side (random failure after the choice); give the player agency to mitigate; surface the odds; show rolls and outcomes in a replayable log; keep any assist rules (for example match-3 refill help) consistent and, for monetised contexts, legal-checked. Never silently skew odds against a paying player; see `legal-ethics`.

Protect first-time experiences: scripted or biased early draws in the tutorial are fine and common; label them in design docs and remove them deliberately after.

## 15. Verifying randomness

- Distribution test: draw 100,000 samples, chi-square against the expected table; fail the test only for gross errors so it is not flaky (fixed seed makes it deterministic anyway).
- Run-length test: compute the longest streak and the mean wait to a success for PRD or bags and compare with the target.
- Pity audit: simulate `10^6` pulls and check the empirical rate and worst-case drought against the published numbers (`gacha_calc.py` gives analytic values).
- Cross-implementation vectors: seed 1 first outputs match between Godot, Unity and server code.
- Replay equality: same seed and actions give an identical event stream after serialising and restoring RNG mid-run.
- Level fairness for random generators (puzzles): sample many seeds, run the solver or bot, and report unsolvable and trivial rates (see `procedural-generation` and `puzzle_solver.py`).
