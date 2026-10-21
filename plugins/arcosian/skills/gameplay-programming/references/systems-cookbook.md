# Gameplay systems cookbook

Implementation recipes for the systems mobile games keep rebuilding: inventory, crafting, quests, achievements, timers, spawners and waves, match-3 board logic, merge boards, idle big numbers with offline progress, block placement, and endless-runner chunk generation. Each recipe gives the data model, the rules that matter, pitfalls, and GDScript or C# you can adapt. All logic is written to live in a deterministic core (see `game-architecture`): data in, data out, seeded RNG passed explicitly, time passed as data.

## Contents

1. Conventions
2. Inventory
3. Crafting
4. Quests and objectives
5. Achievements
6. Timers, cooldowns and energy
7. Spawners and waves
8. Match-3 board logic
9. Merge boards
10. Idle games: big numbers and offline progress
11. Block placement puzzles
12. Runner chunk generation
13. Testing these systems

## 1. Conventions

- Content is data with stable string ids; every mutation is an action that returns events.
- Time never comes from a clock inside the core: pass `now` (a server-validated timestamp) or `dt` in the action.
- RNG: a `Rng` object stored in state, passed to functions that need randomness (`rng.rand_int(n)` as in the template's `core/rng.gd`).

## 2. Inventory

Data model:

```
items:      { "id": {stack_max, category, tags[], ...} }       # content, read-only
inventory:  { slots: [ {id, count} | null ], capacity }         # state
```

Variants: slot-based with stacks (most common), weight-based, grid (Tetris-like, rarely right on mobile), and counted dictionary (`{id: count}`) with no slots, which is simplest and best when capacity is not a design lever.

```gdscript
# counted inventory with optional cap per item
func add(inv: Dictionary, id: String, n: int, cap: int) -> int:   # returns amount actually added
	var have: int = int(inv.get(id, 0))
	var room: int = maxi(cap - have, 0)
	var added: int = mini(n, room)
	if added > 0:
		inv[id] = have + added
	return added

func remove(inv: Dictionary, id: String, n: int) -> bool:
	var have: int = int(inv.get(id, 0))
	if have < n: return false
	inv[id] = have - n
	if inv[id] == 0: inv.erase(id)
	return true
```

Rules and pitfalls:
- All-or-nothing transactions: check every cost before removing any (never half-spend). Provide `can_afford(costs)` and `spend(costs)` that is atomic.
- Equipment: slots keyed by slot name referencing item ids; stat aggregation as a pure function `stats(base, equipped, buffs)` so tests cover it; apply modifiers in a fixed order (flat, then percent additive, then multiplicative) and document it.

Modifier stack formula (common and predictable): `final = (base + sum(flat)) * (1 + sum(percent_additive)) * product(multipliers)`.

## 3. Crafting

Recipe data: `{id, inputs: [{id, n}], outputs: [{id, n}], time_s, station, unlock}`.

Procedure for `craft(recipe_id, count)`:
1. Validate unlock, station and capacity.
2. Check `can_afford(inputs * count)`; spend atomically.
3. If `time_s > 0` push a job `{recipe, finish_at}` to a queue; otherwise add outputs.
4. On completion events add outputs; collection can be manual (a satisfying tap) or automatic.

Queue design: fixed number of slots; jobs finish by absolute timestamps (not elapsed counters) so they progress offline; speed-ups convert remaining seconds to a hard-currency price with a stepped formula (see `economy-design`).

Recipe graph hygiene (run as a test): no cycles that create free value (arbitrage check), every input is obtainable, every output has a use or a sink, no recipe's output value is below its input value unless intended. Compute each item's base cost by recursive expansion with memoisation.

Compute each item's base cost by recursive expansion with memoisation: `cost(item) = sum(n_i * cost(input_i)) / output_count`, raw materials from the price table; track a visiting set so a cycle is reported rather than looping.

## 4. Quests and objectives

Model quests as a list of objectives that listen to core events.

```
quest: {id, title_key, objectives: [ {kind, target, count, filter?} ], rewards: [...], prerequisites: [...], expires_at?}
state: {quest_id: {status, progress: [n...], accepted_at}}
```

Objective evaluation is a pure function over events:

```gdscript
func on_event(quests: Dictionary, defs: Dictionary, e: Dictionary) -> Array:
	var out: Array = []
	for qid in quests:
		var q: Dictionary = quests[qid]
		if q.status != "active":
			continue
		var objs: Array = defs[qid].objectives
		for i in objs.size():
			if _matches(objs[i], e):
				q.progress[i] = mini(int(q.progress[i]) + int(e.get("amount", 1)), int(objs[i].count))
				out.append({"type": "quest_progress", "quest": qid, "index": i, "value": q.progress[i]})
		if _all_done(q, objs):
			q.status = "complete"
			out.append({"type": "quest_complete", "quest": qid})
	return out
```

Design and data rules:
- Objective kinds from a closed vocabulary (collect, reach, win, spend, use, merge, visit); each maps to one event type; new kinds need code, new quests do not.
- Claim step: completion and claiming are separate (players like pressing "claim"); rewards are granted by one atomic action with idempotency (claiming twice does nothing).
- Daily and weekly quests: generated from pools with seeded selection by day key; reroll costs and caps set by design; reset times based on server time zone policy (documented). Do not let clock edits give extra dailies (server time or monotonic checks).

## 5. Achievements

Two layers: your internal achievements (progress, rewards, telemetry) and platform achievements (Game Center, Google Play Games Services) mirrored through a service.

Model: `{id, kind: counter|threshold|flag, stat, target, hidden, reward?}`. Track stats as monotonic counters in the profile (`total_merges`, `best_streak`); achievements are derived: `unlocked = stat >= target`. Re-evaluating from stats after each relevant event is idempotent and survives lost events. Sync to platform on unlock with a retry queue; keep a local `synced` flag.

## 6. Timers, cooldowns and energy

Use absolute timestamps for anything that must progress while the app is closed, and tick counters for in-session sim time.

| Use case | Representation |
|---|---|
| Crafting job, build timer, cooldown after death | `ready_at` absolute time |
| Combat ability cooldown | remaining ticks, reduced in `tick` |
| Daily reset | `last_reset_day` key compared with server day |
| Energy / lives regeneration | `value`, `updated_at`, computed lazily |

Lazy regeneration (no timers running):

```gdscript
func energy_now(value: int, updated_at: int, now: int, max_e: int, secs_per: int) -> Dictionary:
	if value >= max_e:
		return {"value": value, "updated_at": now}
	var gained: int = (now - updated_at) / secs_per      # integer division
	var v: int = mini(value + gained, max_e)
	var ts: int = now if v >= max_e else updated_at + gained * secs_per
	return {"value": v, "updated_at": ts}
```

```csharp
public static (int value, long updatedAt) EnergyNow(int value, long updatedAt, long now, int max, int secsPer) {
    if (value >= max) return (value, now);
    long gained = Math.Max(0, now - updatedAt) / secsPer;
    int v = (int)Math.Min(value + gained, max);
    return (v, v >= max ? now : updatedAt + gained * secsPer);
}
```

Rules: spending energy first normalises (applies regen), then subtracts and, if it was full, sets `updated_at = now` (so regen restarts from the spend). Clamp negative elapsed time (clock set back). For anything that pays out value, validate against server time; local time is only for display (see `multiplayer-backend` for server authority). Display countdowns by recomputing from `ready_at - now` each second rather than decrementing, so backgrounding cannot drift them.

## 7. Spawners and waves

Data-driven waves: `{time or trigger, group: [{enemy, count, interval, lane|pattern}], reward?}`.

```gdscript
func tick(state: Dictionary, dt: float) -> Array:   # fixed dt, schedule precomputed
	var events: Array = []
	state.t += dt
	while state.next < state.schedule.size() and state.schedule[state.next].at <= state.t:
		events.append({"type": "spawn", "enemy": state.schedule[state.next].enemy})
		state.next += 1
	return events
```

Precompute the schedule at wave start. Difficulty scaling (starting points, tune with bots):
- Count: `n(w) = round(base * growth^(w-1))` with growth about 1.05 to 1.15 per wave, or linear `base + step*w` for gentle curves.
- Budget method: each wave has a point budget; each enemy costs points by threat; fill the budget by weighted random choice with caps per type. This lets designers add enemies without rewriting waves.

```
budget(w) = B0 + B1 * w^p        # p about 1.2 to 1.5
while budget > min_cost: choose enemy by weight among those with cost <= budget and w >= unlock; budget -= cost
```

## 8. Match-3 board logic

Board: `w x h` array of piece ids (0 = empty), plus blockers or layers as separate arrays. Core loop per swap:

1. Validate swap adjacency and that it creates a match (or allow invalid swaps that swap back, an animation concern).
2. Apply swap; find matches; resolve specials and cascades until stable; refill; check for possible moves; shuffle if none.

Match finding (runs of 3+): scan rows and columns, mark runs.

```gdscript
func find_matches(b: Array[int], w: int, h: int) -> Array[int]:
	var marked: Dictionary = {}
	for line in w + h:                                   # first h lines are rows, then columns
		var is_row: bool = line < h
		var n: int = w if is_row else h
		var run: int = 1
		for i in range(1, n + 1):
			var cur: int = (line*w + i) if is_row else (i*w + line - h)
			var prev: int = cur - 1 if is_row else cur - w
			var same: bool = i < n and b[cur] != 0 and b[cur] == b[prev]
			if same:
				run += 1
				continue
			if run >= 3:
				for k in run:
					marked[(prev - k) if is_row else (prev - k*w)] = true
			run = 1
	var out: Array[int] = []
	for i in marked:
		out.append(int(i))
	out.sort()
	return out
```

Shapes and specials: detect L/T intersections (a cell marked by both a horizontal and vertical run) and 4 or 5 runs to spawn specials (line clear, bomb, colour clearer) at the swapped cell or the last-moved cell; rules for combining two specials are a table (pairs to effects). Keep the table in data.

Gravity and refill: for each column compact non-empty pieces downward, then spawn new pieces from the top using a refill generator. Cascade loop: `while matches: clear, score with cascade multiplier, gravity, refill`. Emit one event per phase (`clear{cells}`, `fall{moves}`, `refill{cells}`) so the view animates in order.

Refill generator (the fairness lever, see `references/pathfinding-and-rng.md` for RNG): pure random can create initial matches and dead boards. Techniques: reject colours that would create an immediate match at spawn; weighted colours by level goal needs; guarantee a possible move after refill (check with `has_move`, reroll or shuffle); controlled luck for difficulty (assist when the player is stuck, tightening on easy-to-win levels). Keep any assist rules documented and consistent for ethics (see `legal-ethics`).

Simulation: use `match3_sim.py --level PATH --bot greedy|random|cascade` for win rates and move limits (see `progression-difficulty`).

## 9. Merge boards

Core rule: two identical items of tier `t` combine into one of tier `t+1` (sometimes 3 or 5 for bigger chains); items spawn from generators; the board is small and finite so capacity pressure is the main resource.

Data: `chains: {chain_id: [tier items...]}`, `generators: {id: {chain, cooldown, capacity, weights per tier}}`, board cells `{chain, tier} | null`.

```gdscript
func try_merge(board: Array, a: int, b: int, chains: Dictionary) -> Array:
	var ia: Variant = board[a]; var ib: Variant = board[b]
	if a == b or ia == null or ib == null: return []
	if ia.chain != ib.chain or ia.tier != ib.tier: return []
	if ia.tier + 1 >= chains[ia.chain].size(): return []           # max tier
	board[a] = null
	board[b] = {"chain": ia.chain, "tier": ia.tier + 1}
	return [{"type": "merge", "from": [a, b], "to": b, "tier": ia.tier + 1}]
```

Design and implementation notes:
- Value grows roughly exponentially in tier (2x or more per tier in items-needed terms); keep the top tiers rare and meaningful.
- Spawn tables: weighted random with a seeded RNG, plus a small chance of bonus tiers; pity for rare drops (see pathfinding-and-rng file).
- Board full handling: block spawning with clear feedback, offer sell or storage, never delete items.
- Orders or requests give goals: `{items needed, reward}`; generate from the board's current chains to avoid impossible asks.
- Energy gating of generator taps is the economy hook; keep rules in `economy-design`.

## 10. Idle games: big numbers and offline progress

Big numbers: idle values pass `1e308`, the double limit, and can pass any fixed range. Options:

| Approach | Precision | Cost | Use |
|---|---|---|---|
| double | about 15 digits, max about 1.8e308 | cheapest | most games if the design caps below 1e300 |
| mantissa + exponent (`m * 10^e`, `m` in [1,10), `e` an int64) | about 15 digits mantissa | cheap | most idle games |
| BigInteger / arbitrary precision | exact | slow, allocation heavy | only when exactness is a rule |
| Logarithmic storage (`log10 value`) | relative | cheap for multiplication | late-game multiplicative layers |

```gdscript
# mantissa/exponent big number (value = m * 10^e), normalised so 1 <= m < 10 (or m == 0)
func big_add(am: float, ae: int, bm: float, be: int) -> Array:
	if am == 0.0: return [bm, be]
	if bm == 0.0: return [am, ae]
	if ae < be:
		var tm: float = am; var te: int = ae
		am = bm; ae = be; bm = tm; be = te
	var diff: int = ae - be
	if diff > 15: return [am, ae]                  # b is negligible
	var m: float = am + bm * pow(10.0, -diff)
	return _norm(m, ae)

func _norm(m: float, e: int) -> Array:
	if m == 0.0: return [0.0, 0]
	while m >= 10.0: m /= 10.0; e += 1
	while m < 1.0: m *= 10.0; e -= 1
	return [m, e]
```

Serialise as strings (`"1.234e57"`) in saves. Display formats: suffix (K, M, B...) up to a point, then scientific or engineering notation; make the format a player setting; keep three significant digits; avoid layout jumps by fixed-width labels.

Cost growth: the standard idle upgrade price is `cost(n) = base * growth^n` with growth about 1.07 to 1.15 per level (design lever; tune with sims). Cost of buying `k` levels from `n`: geometric sum `base * growth^n * (growth^k - 1) / (growth - 1)`. Max affordable `k` given budget `B`: `k = floor( log(B*(growth-1)/(base*growth^n) + 1) / log(growth) )`. Implement "buy max" with this closed form, not a loop.

Production: `income/s = sum(owned_i * output_i) * global_multiplier`; multipliers stack by documented rules (additive within a group, multiplicative across groups).

Offline progress: on resume compute `elapsed = clamp(now - last_seen, 0, cap)` where `cap` is a design lever (for example hours to a day; longer caps reward infrequent play but cheapen active play). Rules:
1. Use closed-form where income is constant: `gain = income * elapsed * offline_efficiency`.
2. If income changes during the period (auto-buy, timers), simulate in coarse steps (for example split elapsed into at most 100 to 500 steps) rather than per second.
3. Apply one `offline` action; emit one summary event for a "welcome back" screen; offer an ad-doubling option only with transparent framing.
4. Anti-cheat: `now` from server time when available; if only device time, clamp and detect backwards jumps; a skipped-ahead clock should not grant more than the cap.
5. Test: simulate N minutes online versus one offline action and compare within the efficiency factor.

## 11. Block placement puzzles

Core: a grid, a set of polyomino pieces offered in a tray, placement validity, line clears.

```gdscript
func can_place(grid: Array[int], w: int, h: int, cells: Array, ox: int, oy: int) -> bool:
	for c in cells:
		var x: int = ox + int(c.x); var y: int = oy + int(c.y)
		if x < 0 or y < 0 or x >= w or y >= h or grid[y*w + x] != 0:
			return false
	return true

func clear_lines(grid: Array[int], w: int, h: int) -> Dictionary:
	var rows: Array[int] = []
	var cols: Array[int] = []
	for y in h:
		var full: bool = true
		for x in w:
			if grid[y*w + x] == 0:
				full = false
		if full:
			rows.append(y)
	for x in w:
		var fullc: bool = true
		for y in h:
			if grid[y*w + x] == 0:
				fullc = false
		if fullc:
			cols.append(x)
	for y in rows:
		for x in w:
			grid[y*w + x] = 0
	for x in cols:
		for y in h:
			grid[y*w + x] = 0
	return {"rows": rows, "cols": cols}
```

(Compute full rows and columns before clearing so intersections clear together.)

Piece supply fairness is the design: pure random trays produce unwinnable states. Techniques: generate a tray of three and verify that at least one ordering of placements is solvable (search over placements, depth up to 3) and reroll otherwise; bias toward pieces that fit current free space when the board is crowded; ensure the tray is rarely three large pieces on a nearly full board; track an "assist level" that grows with consecutive near-fail states. Solvability search is cheap on small grids; run it in the core with the seeded RNG so replays match.

Scoring: points per cell placed plus line-clear bonus growing with simultaneous lines and combo streaks (consecutive placements that clear). Dead-board detection: no piece in the tray has any valid placement, which is the game-over test; run it after each placement and after each tray refill.

## 12. Runner chunk generation

Endless runners assemble hand-authored chunks into an unbounded track with a controlled difficulty curve.

Data: `chunk: {id, length, difficulty: 1..N, entry_lane_mask, exit_lane_mask, tags, content...}`.

Generation:
1. Maintain `distance` and a target `difficulty(distance)` curve (ramp then plateau with periodic relief, see `progression-difficulty`).
2. Choose the next chunk among those whose `entry` compatibility matches the previous chunk's `exit` and whose difficulty is within a window of the target.
3. Weighted random with a recency penalty (avoid repeating the last K chunks); seeded RNG per run, and per-chunk sub-seed `hash(run_seed, chunk_index)` for content inside the chunk.
4. Guarantee fairness: every chunk has a validated safe path at the speed limit; run a headless checker over all chunks at build time (reachability by lane and jump timing).

Speed ramp: `speed(d) = min(max_speed, base + a * d^0.5)` or stepwise by milestone; reaction-time constraint: obstacle spacing must satisfy `spacing >= speed * min_reaction_time` (for example 0.4 to 0.6 s of travel as a starting point, tune with playtests).

Determinism: generation is a pure function of `(seed, distance_travelled_chunks)`; storing the seed and action log reproduces a run; daily runs share a date-derived seed.

## 13. Testing these systems

- Property tests with the seeded RNG: random action sequences never produce negative counts, exceed caps, or break conservation (items, energy, quest progress).
- Round trips: save, load, continue gives identical outcomes; golden seeds catch accidental rule changes.
- Fairness checks: match-3 boards always have a move after refill; block trays solvable by search; runner chunks have safe paths; crafting graphs have no free-value cycles.
- Bot sims through levels and waves for win rates and softlocks (see `qa-testing` and the template's bot mode).
