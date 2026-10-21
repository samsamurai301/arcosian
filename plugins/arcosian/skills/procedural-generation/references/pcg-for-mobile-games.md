# PCG for Mobile Games: Patterns that Ship

This file turns the algorithm catalogue into the generators mobile games actually ship: chunk assembly for endless runners, endless and streamed worlds with pacing directors, roguelite run and map generation, loot and affix generation, guaranteed-solvable puzzle generation by working backward from the solution, seeded daily challenges, and naming generators. Each pattern comes with a data model, pseudo-code, fairness constraints with the formulas behind them, tuning numbers to start from, and the verification step that keeps it from shipping a broken level to millions of phones. The common thread is that on mobile, PCG is usually *authored pieces plus rules plus a verifier*, not open-ended synthesis. Sessions are short, readability beats novelty, and a single unfair death in a 90-second run costs more retention than a hundred fresh layouts earn.

## Contents

1. Mobile PCG principles and content-burn maths
2. Runner chunk assembly
3. Endless generation: streaming, budgets and pacing directors
4. Roguelite run generation: maps, rooms, encounters, rewards
5. Loot and affix generation
6. Guaranteed-solvable puzzle generation (backward generation)
7. Seeded daily challenges
8. Naming generators
9. Mobile PCG ship checklist

---

## 1. Mobile PCG principles and content-burn maths

1. **Authored quality, procedural variety.** Hand-made pieces (chunks, rooms, templates) carry the readability and the "designed" feel; rules and seeds provide recombination. Pure synthesis is reserved for things players read loosely: terrain, decoration, names.
2. **Fairness is perceived, not computed.** A level can be solvable and still feel unfair: hidden threats, a forced hit, a reaction window shorter than a thumb swipe. Constraints must encode *human* limits (§2.2).
3. **Generate between moments, never during them.** Generate during transitions, loading screens or the previous level's result screen, on a worker thread, with a time budget and a cached fallback.
4. **Offline-first and deterministic.** Phones go offline and get interrupted. Generation must not need the network, must be reproducible from (seed, generator version), and must resume exactly after the OS kills the app (`determinism-and-seeds.md`).
5. **Verify before players see it.** Anything generated on device must come from a generator whose output space has been verified offline (expressive range plus gates over thousands of seeds), or must be checked on device by a fast validator with a fallback (`generate-and-test.md`).

**Content-burn estimate** (decide authored vs procedural with numbers):

```text
levels_consumed_per_week = sessions_per_day × levels_per_session × 7
weeks_of_content         = pool_size / levels_consumed_per_week            # authored pool
effective_pool           = authored_pieces × variants × combinations_that_pass_gates   # procedural
```

Worked example with assumed values: a puzzle game whose engaged players play 3 sessions a day of 4 levels each consume 84 levels a week. A 600-level handmade launch pool lasts about 7 weeks for them. If the team can author 20 levels a week, it falls behind by 64 levels a week. Options are procedural levels for the endless tail, daily challenges, or a slower meta. Feed the real values from `contract.analytics.kpi_targets` and the production plan (`production`).

---

## 2. Runner chunk assembly

### 2.1 Chunk data model

```json
{
  "id": "train_jump_03",
  "length_m": 40,
  "difficulty": 4,
  "entry": {"lanes_open": [0, 1, 2], "height": "ground"},
  "exit":  {"lanes_open": [1],       "height": "ground"},
  "requires": ["jump"],
  "tags": ["teach_jump", "trains"],
  "weight": 10,
  "cooldown_chunks": 8,
  "mirror_ok": true,
  "coins": "guide_line",
  "min_speed": 8, "max_speed": 22
}
```

- **Sockets (entry and exit):** which lanes are passable at the boundary, and the player's height state (ground, roof, rail). Two chunks may join only if the previous exit is compatible with the next entry *and* the player can move between the open lanes within the transition distance at the current speed.
- **Difficulty** is an integer band (1–10) set by designers, later re-estimated from telemetry deaths per chunk.
- **Requires** lists abilities (jump, slide, double jump) so chunks are only drawn once that verb has been taught.
- **Mirror** doubles the pool for free in lane-based runners.

### 2.2 Fairness constraints from human limits

The core constraint: every threat must be visible, and leave enough time to perceive it, decide and complete the gesture.

```text
time_available = distance_to_threat / speed
required_time  = t_perceive_and_decide + t_gesture + t_motion
fair if time_available >= required_time × safety_factor
min_spacing(v) = v × (t_decide + t_gesture + t_motion) × safety_factor
min_view_distance(v) = v × (t_decide + t_gesture + t_motion) + max_obstacle_length
```

Design budgets, not physiological facts. Simple visual reaction time for alert adults is commonly cited at around a quarter of a second, but choosing between responses takes longer, and a swipe plus the character's lane-change animation adds more. Start with a total budget of **0.6–0.8 s** early in a run and **0.4–0.5 s** at peak difficulty, then calibrate from playtest death heatmaps (`qa-testing`, `player-analytics`).

Worked example: lane change animation 0.15 s, swipe 0.10 s, decision budget 0.35 s, safety factor 1.2. At 10 m/s, min_spacing = 10 × 0.60 × 1.2 = **7.2 m** between threats needing different responses. At 20 m/s with the decision budget tightened to 0.25 s, min_spacing = 20 × 0.50 × 1.2 = **12 m**, and the camera must show at least 20 × 0.5 + obstacle length ≈ 10 m plus the obstacle ahead. In portrait orientation the visible track depth is limited, so speed caps often come from the camera, not from difficulty.

Also enforce:
- **No forced hits:** from every reachable lane state at the chunk entry there is a path to the exit (BFS over lane × height × position-step, with move durations converted to distance at the current speed).
- **No double-blind:** never two consecutive threats that each require a different response with a total window below the budget.
- **Readable stacking:** at most one new obstacle *type* per chunk; never introduce a new type at peak speed.

### 2.3 Selection algorithm

```text
function next_chunk(state, pool, rng):
    cands = [c for c in pool
             if sockets_compatible(state.last.exit, c.entry, state.speed)
             and c.requires ⊆ state.unlocked_verbs
             and state.speed in [c.min_speed, c.max_speed]
             and c.difficulty in difficulty_window(state)
             and chunks_since(c.id, state.history) >= c.cooldown_chunks]
    if state.chunks_since_rest >= REST_EVERY: cands = [c for c in cands if "rest" in c.tags] or cands
    if not cands: return FALLBACK_REST_CHUNK          # always have a universal-socket rest chunk
    weights = [c.weight * novelty_bonus(c, state) for c in cands]
    c = rng.weighted(cands, weights)
    if c.mirror_ok and rng.bounded(2) == 1: c = mirror(c)
    assert transition_reachable(state, c)              # cheap BFS; else retry with c removed
    return c

difficulty_window(state):
    target = difficulty_at(state.distance)              # from the ramp below
    return [floor(target) - 1, ceil(target)]             # mostly at or slightly below target
```

### 2.4 Difficulty ramps for endless runs

```text
speed(d)      = v0 + (v_max - v0) × (1 - exp(-d / D))        # fast early ramp, asymptote at v_max
difficulty(d) = min(cap, 1 + (d / step_m)) with a sawtooth: every K chunks drop 2 bands for 1–2 chunks
```

Starting values to tune: v0 = 8–10 m/s, v_max = 2–2.5 × v0, D chosen so speed reaches 63% of the way to v_max at the median run distance of new players. Rest chunks every 6–10 chunks. Track deaths per chunk id: a chunk whose death rate is far above its band's average is mis-rated or unfair (`difficulty_curve.py analyze` works on per-level CSVs; treat chunk ids as levels).

### 2.5 Pool size and repetition

With a uniform pick from P eligible chunks over S chunks in a session, the expected number of distinct chunks seen is `P × (1 − (1 − 1/P)^S)`. Example: P = 40 eligible chunks and S = 30 per session gives about 21 distinct, so about 9 repeats. Cooldowns cut visible repetition; mirrors and theme skins (same geometry, different art) stretch the pool further. Size the pool per difficulty band, since only that band is eligible at any moment.

---

## 3. Endless generation: streaming, budgets and pacing directors

### 3.1 Streaming worlds

```text
on_player_moved():
    want = chunks within LOAD_RADIUS of player chunk
    for c in want - loaded: enqueue_generate(c, seed=chunk_seed(world_seed, c))
    for c in loaded where distance(c, player) > UNLOAD_RADIUS: release(c)   # UNLOAD > LOAD (hysteresis)
per_frame():
    budget_ms = 2.0                                   # e.g. 2 ms of a 16.7 ms frame at 60 fps
    while queue and elapsed < budget_ms: step_generation(queue.front)   # time-sliced, resumable
```

- **Hysteresis:** unload radius at least one chunk beyond the load radius, so a player standing on a border does not thrash.
- **Pooling:** reuse chunk objects and meshes; instantiate nothing per frame on low-end Android.
- **Floating origin:** recentre the world when the player is far from the origin (threshold set by float precision; see `algorithms.md` §6).
- **Memory cap:** loaded chunks × per-chunk memory must stay within the contract's `perf_budgets.memory_mb` share for the world (`mobile-performance`).

### 3.2 Pacing directors

A director chooses what to generate next from a model of player intensity rather than from distance alone. Valve's AI Director in *Left 4 Dead* (2008), described by Michael Booth in 2009 talks, is the best-known example: it tracks player "emotional intensity", builds up, peaks, then holds a relax phase before building again.

```text
intensity += damage_taken × a + near_misses × b + enemies_on_screen × c       # per tick
intensity  = max(0, intensity - decay × dt)
phase: BUILD (spawn normally) -> PEAK when intensity > hi (spawn the climax set piece)
       -> RELAX for T_relax seconds, or until intensity < lo (rest chunks, rewards) -> BUILD
```

For mobile: use the director to place rest beats, reward moments and rewarded-ad-free safe zones; do not use it to secretly lower difficulty in competitive or daily modes, where all players must face the same content (`progression-difficulty` on DDA ethics and transparency).

---

## 4. Roguelite run generation

### 4.1 Run structure

```text
run  = [act_1, act_2, act_3]                      # biomes with their own pools and bosses
act  = map graph of floors; each floor has 1..k nodes; edges go up one floor
node = {type: fight | elite | event | shop | rest | treasure | boss, seed}
```

*Slay the Spire* (Mega Crit; full release 2019) popularised the layered branching map: per act, a grid of floors with several upward paths that branch and merge, node types placed under rules, and the whole map shown in advance so routing is a decision. *Hades* (Supergiant Games, 2020) instead shows the reward of the next room on its door; *Archero* (Habby, 2019) is the usual reference for room-by-room roguelite play with level-up skill choices in mobile portrait.

### 4.2 Layered map generation

```text
function gen_map(rng, floors=15, width=7, paths=6):
    edges = set()
    for p in 1..paths:
        x = rng.bounded(width) if p > 2 else distinct start   # first two paths start apart
        for f in 0..floors-2:
            nx = clamp(x + rng.int(-1, 1), 0, width-1)
            if crosses_existing_edge(f, x, nx, edges): nx = x       # no crossing edges (readability)
            edges.add(((f, x), (f+1, nx))); x = nx
    nodes = endpoints of edges
    assign_types(nodes, rng)
    return nodes, edges

function assign_types(nodes, rng):
    fixed: floor 0 = fight; a mid-act floor = treasure; last floor = rest (before the boss)
    for node in remaining (bottom-up):
        choose type by weights (fight 45, event 22, elite 16, rest 12, shop 5)   # example weights to tune
        subject to rules:
            no elite or rest in the first ~5 floors
            no two rest or shop or elite nodes in a row on one path
            siblings (same parent) get different types where possible        # meaningful choice
        if no type satisfies the rules: fight
    validate: every path from start to boss contains >= 1 rest and an elite count within [min, max]
```

The example weights and floor counts are a starting point to tune, not a copy of any game's values. The validation step is mandatory: rules applied node by node can still produce a path with no rest site.

### 4.3 Rooms and encounters

- **Room geometry:** authored room templates per biome, tagged by exits and size, selected by the map position; procedural decoration and hazard variants inside.
- **Encounter budget:** `budget(floor) = b0 + b1 × floor` (or × g^floor for steeper acts). Each enemy group has a cost from its measured threat (damage per second × effective HP, normalised). Fill the budget from eligible groups under constraints: at most one "control" enemy type early, no two ranged-heavy groups in a row, at least one group per room that counters the current dominant build archetype later in the act.
- **Elite and boss modifiers** come from a separate stream so adding a modifier never changes room layouts.

### 4.4 Reward pacing

```text
offer(rng, pool, player):
    cands = eligible(pool, player)                         # unlocked, not owned, fits the build rules
    k = 3
    picks = weighted_sample_without_replacement(cands, k, weight = base × synergy_bias(player))
    enforce: at least 2 distinct categories among picks; no duplicate
    rarity: roll per pick; pity counter forces >= 1 rare if none in the last N offers
```

- **Power curve check:** simulate 10,000 seeded runs with a simple bot and compare the median player power per floor with the encounter budget per floor. The ratio should dip before bosses (tension) and recover after. Long flat stretches mean boring; dips below about 0.7 of the target mean walls.
- **Build-defining items:** guarantee the chance to see at least one build-defining option per act (a pity rule), or runs without them feel dead.
- **Variance budget:** a roguelite needs variance, but losing a run to a bad seed in the first two floors is a retention leak. Keep early floors low-variance and let variance rise with player agency (more rerolls and shops later).

### 4.5 Mobile specifics for runs

- Target run length 8–20 minutes, split at node boundaries; auto-save at every node and mid-fight snapshots for interruptions (phone calls, app switching). Resuming must reproduce the exact state: store stream states, not just the root seed.
- Portrait one-thumb play: choices of 3 large cards; map scrolls vertically.
- Offer a "quick run" (one act) for short sessions.

---

## 5. Loot and affix generation

### 5.1 Data model

```text
BaseItem   { id, slot, implicit_stats, ilvl_min, tags }
Affix      { id, kind: prefix|suffix, group, tags_allowed, weight, tiers: [ {ilvl_min, min, max, weight} ] }
Rarity     { id, weight, affix_count: (min, max), prefix_max, suffix_max }
Item       { base, ilvl, rarity, affixes: [ (affix_id, tier, value) ], power, seed }
```

The prefix/suffix split, item level gating tiers, and affix groups that cannot repeat are the long-standing action-RPG conventions (for example *Diablo II* magic items carry at most one prefix and one suffix, and rares up to three of each; *Path of Exile* uses the same caps and exposes tiers and weights to players).

### 5.2 Generation

```text
function roll_item(source, ilvl, rng):
    base   = rng.weighted(eligible_bases(source, ilvl))
    rarity = roll_rarity(source, ilvl, rng)                # with a pity counter per player and per source
    n      = rng.int(rarity.affix_count.min, rarity.affix_count.max)
    affixes = []; used_groups = {}
    repeat n times:
        pool = [a for a in AFFIXES if base.tags ∩ a.tags_allowed
                and a.group not in used_groups
                and count_kind(affixes, a.kind) < rarity.max_for(a.kind)
                and any tier with tier.ilvl_min <= ilvl]
        if not pool: break
        a    = rng.weighted(pool, [x.weight for x in pool])
        tier = rng.weighted([t for t in a.tiers if t.ilvl_min <= ilvl], by t.weight)
        value = rng.int(tier.min, tier.max)                # integer rolls; floats only for display
        affixes.append((a.id, tier, value)); used_groups.add(a.group)
    return Item(base, ilvl, rarity, affixes, power=score(base, affixes))
```

**Budget-based alternative** (simpler to balance, common in mobile RPGs): `budget = f(ilvl, rarity)`; each affix tier has a cost; draw affixes until the budget is spent. Every item of the same ilvl and rarity then has similar total power, and variance moves into *which* stats you get rather than how strong the item is. Choose the classic model when chasing perfect rolls is the long-term goal (a hardcore audience); choose the budget model for readability and fairness.

### 5.3 Odds you must compute, not guess

Sampling without replacement changes odds in ways designers misjudge. Worked example (computed exactly for this file): an affix pool with weights A = 100, B = 100, C = 200, D = 600 (total 1,000). A's single-draw chance is 10%. On an item with 2 affixes, the chance that A appears is **28.6%**, not 20%. When D (60%) is drawn first, it leaves the pool and A's share of the remainder jumps to 25%. With 3 affixes, A appears **59.0%** of the time. Always compute target-item odds by exact enumeration (small pools) or Monte Carlo (≥ 10^5 seeded rolls), then convert to *expected time to find*: with per-drop probability p, the expected number of drops is 1/p, and the 90th-percentile player needs `ln(0.1) / ln(1 − p)`, about 2.3/p drops for small p. Publish the 90th percentile in the economy review, not the mean (`economy-design`).

### 5.4 Readability and longevity

- Mobile item cards: at most 3–4 affix lines visible, plus a single power score and green or red comparison arrows against the equipped item. Hide the rest behind a tap.
- Kill dead affixes (stats no build wants): they make loot feel like trash. Audit by pick rate in telemetry.
- Plan stat inflation across seasons (power creep) before launch. Budget models make a later "squish" easier.
- If any loot is purchasable or comes from paid boxes: rolls happen server-side, odds are disclosed, and pity is honoured (`determinism-and-seeds.md` §12, `monetization`, `legal-ethics`).

---

## 6. Guaranteed-solvable puzzle generation

### 6.1 Three strategies

| Strategy | How | Guarantees | Cost | Use when |
|---|---|---|---|---|
| Forward random + solver gate | Random layout, solve, keep if solvable | Solvable (proven by the solver) | Wasted attempts; the acceptance rate can be tiny | Solver is fast; random layouts are often solvable |
| **Backward generation** | Start from a solved state and apply inverse moves | Solvable by construction | Cheap; but scramble depth ≠ difficulty | Moves are reversible, or have well-defined inverses |
| Constructive with a solution first | Build the solution path, then add obstacles that do not block it | Solvable; a designed solution | Medium | Path and flow puzzles, platform puzzles |

**The rule that matters:** backward generation guarantees solvability, *not difficulty*. Random inverse moves wander back toward the start, so a 100-move scramble may be solvable in 12 moves. Always grade with a forward solver (`${CLAUDE_PLUGIN_ROOT}/scripts/puzzle_solver.py`) and store the measured `min_moves`, never the scramble length.

### 6.2 Puzzle-type recipes

| Puzzle | Backward recipe | Watch out for |
|---|---|---|
| Sliding tiles (15-puzzle family) | From the goal, apply random legal blank moves (never immediately undo the previous move) | Half of all random permutations are unsolvable (parity), so never shuffle tiles directly. Grade with A* (Manhattan heuristic) |
| Lights Out | From all-off, "press" a random subset of cells | On 5×5 only 1/4 of configurations are solvable (the press matrix has rank 23 of 25 over GF(2), verified for this file); random lit patterns fail 75% of the time. Presses commute and are self-inverse, so the pressed set *is* a solution, but possibly not the shortest |
| Sokoban | From boxes-on-goals, apply reverse moves (the player *pulls* boxes); pick the reachable start state farthest from the goal | Pulling cannot create forward deadlocks, but check that the player's start region is reachable. Taylor and Parberry ("Procedural Generation of Sokoban Levels", 2011) combined template rooms with a search backward from goal states for the most distant start |
| Sort (water/ball/nut sort) | Simplest: deal colours randomly into tubes, then solver-gate. A reverse pour is not always a legal forward pour, so naive backward play can produce unsolvable states | The acceptance rate depends on tube count, capacity and empty tubes: measure it. Use `puzzle_solver.py` with `layout.type: "sort"` |
| Flow / numberlink | Partition the grid into random non-crossing paths (random walks plus merges), keep the endpoints, then check uniqueness | Puzzles with multiple solutions feel loose; reject or add a blocker |
| Sudoku, nonograms, logic grids | Generate a full valid solution, then remove clues one at a time while the solution stays unique (the solver counts solutions up to 2) | Grade by the deduction techniques a human-style solver needs, not by clue count |
| Mazes | Spanning-tree algorithms: recursive backtracker (long corridors), randomised Prim (many short dead ends), Wilson's algorithm (uniform spanning tree, unbiased) | A perfect maze has exactly one path between any two cells; add loops for "braid" mazes |
| Match-3 boards | Fill with no initial matches (re-roll a cell's colour while it would match) and require at least one valid move; reshuffle when none remain | Goal feasibility comes from bot simulation (`match3_sim.py`), not construction |

### 6.3 Backward generation with farthest-state selection

```text
function backward_generate(goal_state, rng, scramble_steps=200, keep_best=True):
    s = goal_state; prev = none
    for i in 1..scramble_steps:
        moves = inverse_moves(s) minus undo(prev)
        if not moves: break
        prev = rng.pick(moves); s = apply_inverse(s, prev)
    return s

function generate_puzzle(target_min_moves, rng, attempts=50):
    best = none
    for a in 1..attempts:
        start = backward_generate(GOAL, rng)
        sol = solve(start)                                # BFS/A*; returns min_moves, nodes, branching
        if sol.min_moves in [target_min_moves - 1, target_min_moves + 1]: return (start, sol)
        best = closer_of(best, (start, sol), target_min_moves)
    return best                                           # caller decides whether "close" is acceptable
```

### 6.4 Grading difficulty

Minimum solution length is only one feature. Combine several, then calibrate against real attempts:

| Feature | Measured by | Why it matters |
|---|---|---|
| `min_moves` | Optimal solver | Lower bound on effort |
| Solution-path branching | Count legal moves at each state along the solution | High branching hides the right move |
| Dead-end share | Share of reachable states from which the goal is unreachable | Traps make puzzles hard and frustrating |
| Counter-intuitive moves | Moves on the solution that increase a naive heuristic (e.g. move a box away from its goal) | The "aha" moves |
| Search effort | Nodes expanded by a fixed-budget greedy or human-like bot | Proxy for human search |
| Bot win rate within the move limit | Random or greedy bot over many runs | Proxy for slack (how forgiving the limit is) |

Fit `difficulty = w · features` to observed `attempts_p50` from playtests or soft launch, then use the fitted model to bucket new puzzles. Until there is data, sort by `min_moves`, then branching. Record results in the level spec's `solver` block and compare them with `difficulty_target` (`level-design`, `progression-difficulty`).

### 6.5 The puzzle pipeline

```text
generate (seeded) -> canonicalise (rotate/reflect/recolour to a canonical form) -> dedupe by hash
 -> solve (puzzle_solver.py --json) -> reject unsolvable or out-of-band -> grade
 -> bucket by difficulty -> sequence with teach/test/twist/reward -> human spot-check 5–10% -> ship as data
```

Example commands:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/puzzle_solver.py --level .gamestudio/levels/w2_l014.level.json --algo astar --json
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/match3_sim.py --level .gamestudio/levels/w1_l003.level.json --runs 500 --bot greedy --seed 1 --json
```

---

## 7. Seeded daily challenges

The daily challenge is one of the highest-leverage PCG features on mobile: one piece of content per day, shared by everyone, which creates a reason to return, a social object and a fair leaderboard. *Wordle* (2021) made the "one shared puzzle a day plus a spoiler-free share grid" pattern famous; roguelites (*Spelunky*'s daily challenge, daily seeded runs in many deckbuilders) use the same idea with a shared seed.

**Design decisions:**

| Decision | Options | Recommendation |
|---|---|---|
| Content source | Seeded generation / curated list / curated seeds | Curated seeds from an offline-validated pool, fetched a day ahead |
| Difficulty | Flat / weekday ramp | A ramp across the week is a proven pattern (the *New York Times* crossword gets harder from Monday to Saturday); label the day's difficulty |
| Attempts | One / limited / unlimited with best score | One scored attempt plus unlimited practice for competitive modes; unlimited for relaxed puzzles |
| Rules | Player's loadout / locked loadout | Locked loadout, so leaderboards are fair |
| Sharing | Score / spoiler-free result grid / replay link | Spoiler-free grid or emoji summary plus a deep link |
| Leaderboards | Global / friends / percentile | Percentile ("you beat 72% of players") motivates more players than a global top 100 that few can reach |
| Streaks | Strict / with freeze | A streak freeze (earned, not only bought) keeps the streak from becoming a stress source (`liveops`, `economy-design`) |

**Engineering checklist** (details in `determinism-and-seeds.md` §10): UTC or fixed-hour reset from server time; `daily_seed = derive(salt, "daily:YYYY-MM-DD")`; generator version frozen per date in remote config; next 30–60 days pre-validated in CI with an override list for failures; replay-based score validation for the leaderboard top; offline play allowed with later submission tagged with the date key.

**Validation gate for a daily** (stricter than for normal levels, because everyone sees it): solvable (solver or bot) at 100%; difficulty within the band for that weekday; no softlock found by 200+ bot runs; a human checks the next week's dailies on a device (5 minutes a week, and worth it).

---

## 8. Naming generators

Names for characters, places, items, ships, guilds and pets. Three families:

**(a) Markov chains over characters.** Train on a curated list of names in the target style (order 2 or 3; higher orders copy the training set).

```text
function train(names, order=2):
    model = {}
    for n in names:
        s = "^" * order + lower(n) + "$"
        for i in 0 .. len(s)-order-1:
            model[s[i:i+order]].append(s[i+order])
    return model

function generate(model, rng, order=2, min_len=4, max_len=9, tries=50):
    for t in 1..tries:
        ctx = "^" * order; out = ""
        loop:
            ch = rng.pick(model[ctx])                 # list with repeats = frequency weighting
            if ch == "$" or len(out) > max_len: break
            out += ch; ctx = ctx[1:] + ch
        if min_len <= len(out) <= max_len and out not in training_set and passes_filters(out):
            return capitalise(out)
    return fallback_name(rng)
```

**(b) Syllable combinators.** Curated onset, nucleus and coda lists, or prefix and suffix lists per culture or faction ("Kal", "Dor", "Vex" + "-ara", "-ion"). The most controllable family, and the easiest to keep pronounceable.

**(c) Template grammars.** Kate Compton's *Tracery* (2015) popularised small JSON grammars where symbols expand into weighted alternatives. Good for item names, quest titles and flavour text:

```json
{
  "origin": ["#adj# #noun#", "#noun# of #place#", "#owner#'s #noun#"],
  "adj":   ["Rusted", "Gilded", "Whispering", "Sunken"],
  "noun":  ["Blade", "Lantern", "Compass", "Crown"],
  "place": ["the Tidelands", "Emberfall", "the Hollow Reach"],
  "owner": ["#name#"]
}
```

**Quality controls (mandatory for anything players see):**
1. **Length** fits the narrowest UI label at the largest supported text size, in every locale (`mobile-ux`, `accessibility-localization`).
2. **Pronounceability:** cap consonant runs at 3 and vowel runs at 2, and reject unpronounceable bigrams per language.
3. **Profanity and slur filtering** in every shipped language: normalise (lowercase, strip accents, map leetspeak 0→o, 1→i, 3→e, 4→a, 5→s), then check substrings against blocklists. Generate 10,000 names offline and have a human, ideally a native speaker per major locale, review a sample. Generators *will* produce offensive strings eventually.
4. **No real people, brands or trademarks:** filter against a list of famous names and brand terms for generated character and product names (`legal-ethics`).
5. **Uniqueness:** reject names already used in the run or world; hash the name into the entity's id space if it must be unique.
6. **Reproducibility:** derive the name from the entity's seed (`derive(world_seed, "name:" + entity_id)`) so it survives save and load without being stored, and a shared seed shows the same names.
7. **Localisation:** proper nouns usually stay untranslated, but they must be renderable by every locale's font, and transliteration may be needed for CJK markets. For translated templates, each locale needs its own grammar because word order and gender agreement differ.
8. **LLM-generated name lists:** acceptable as an *offline* source of candidates for the curated lists in (a) and (b), followed by the same filters and human review. Never call an LLM at runtime for player-visible names.

---

## 9. Mobile PCG ship checklist

- [ ] Every generator takes (seed, generator_version, params) and is deterministic at the level the design needs (`determinism-and-seeds.md` §2).
- [ ] Generation runs outside gameplay moments, on a worker thread, within a measured time budget on the low-tier reference device, with a cached fallback.
- [ ] Fairness constraints encode human limits (reaction and gesture budgets, visibility, no forced hits), and a validator enforces them on every output.
- [ ] Puzzles and levels pass a solver or bot gate; measured difficulty is stored in the level spec's `solver` block.
- [ ] Expressive range was analysed over at least 1,000 seeds per generator; no large unintended clusters, no degenerate outputs (`generate-and-test.md`).
- [ ] Daily content is pre-validated for the next 30+ days, with an override list in remote config.
- [ ] Player-visible generated text passes length, profanity and trademark filters in every shipped locale.
- [ ] Seeds shown to players carry a generator version; old versions still decode or fail gracefully.
- [ ] Paid random outcomes are rolled server-side with disclosed odds; they never use client seeds.
- [ ] Telemetry logs the seed, generator version and content id with every level start, fail and quit event, so bad seeds can be found and blocklisted (`player-analytics`).
