# 03 — Puzzle Mechanics

Puzzle mechanics are the commercial backbone of casual mobile: tile-matching, merge, sort, block placement and their many offshoots dominate downloads and long-term revenue because they fit one-handed, interruptible sessions and scale to thousands of levels. This file covers 23 puzzle mechanics, from match-3 and its special-piece and blocker systems to sort, screw-out, triple-match trays, logic puzzles, word, perception and physics puzzles. Each entry gives precise rules, the levers that actually move difficulty, the solvability and generation problems, and how to verify levels with bots or solvers before a human sees them. The single most important habit: **every puzzle level ships with machine evidence** — a solver proof of solvability and minimum moves for deterministic puzzles, or a bot win-rate distribution for stochastic ones (see the `level-design` and `qa-testing` skills, and the scripts named in section 1).

## Contents

1. Puzzle fundamentals: solvability, difficulty levers, verification
2. Index of mechanics
3. Tile-matching family (entries 1–4)
4. Merge, sort and place (entries 5–8)
5. Spatial logic (entries 9–13)
6. Tile-pick and tray family (entries 14–15)
7. Logic and word (entries 16–18)
8. Perception (entries 19–20)
9. Physical and geometric (entries 21–23)
10. Volatile facts

## 1. Puzzle fundamentals

**Deterministic vs stochastic.** Deterministic puzzles (sokoban, sliding, sort, nonogram, flow) have a fixed state space: prove solvability and compute `min_moves` with search. Stochastic puzzles (match-3, blast, block placement with random pieces, triple-match with hidden layers) depend on refills and draws: measure difficulty as a **win-rate distribution from bot runs**, then calibrate bots against real player data after soft launch.

**Difficulty levers, in rough order of power** (for most families):

| Lever | Deterministic puzzles | Stochastic puzzles |
|---|---|---|
| State-space branching | Number of movable pieces, empty cells, colours | Colours, board openness, refill randomness |
| Move/time budget | Slack over `min_moves` (e.g., +0 to +50 %) | Moves vs bot median moves-to-win |
| Hidden information | Covered tiles, fog | Layer depth, unknown refills |
| Blockers | Immovable cells, one-way paths | Layered blockers, spreaders, locks |
| Required insight | Non-greedy first move, counter-intuitive sacrifice | Combo setups, special-piece planning |

**Level role** (`level-spec.teach`): `teach` (new element alone, near-certain win), `test` (element with known ones), `twist` (unexpected interaction), `reward` (easy, spectacular). A typical 10-level beat: teach, test, test, twist, reward, test, test, hard (twist), reward, super-hard spike, then easy.

**Verification tools in this plugin:**

- `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/puzzle_solver.py --level PATH [--algo bfs|astar] --json` for level specs whose `layout.type` is `sliding`, `sokoban`, `sort` or `lights_out`; writes `solver.solvable` and `solver.min_moves`.
- `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/match3_sim.py --level PATH --runs 500 --bot greedy|random|cascade --json` for match-3 levels (`layout.type` must be `match3`; swap rules only, so `blast-collapse` boards are rejected with `layout.type must be match3`); gives `win_rate` (copy it to `solver.bot_win_rate`), the `moves_left` distribution and a `difficulty_band`.
- `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/difficulty_curve.py generate|analyze` to plan and audit a level sequence.

## 2. Index of mechanics

| # | Mechanic | ID | Family | One-line essence | Solvability proof |
|---|---|---|---|---|---|
| 1 | Match-3 swap | `match3-swap` | tile-matching | Swap adjacent tiles to make lines of 3+ | bot win rate |
| 2 | Blast / collapse | `blast-collapse` | tile-matching | Tap a group of 2+ same-colour tiles | bot win rate |
| 3 | Special pieces and combos | `special-pieces` | tile-matching | Big matches create power pieces that combine | bot win rate |
| 4 | Blocker taxonomy | `blockers` | tile-matching | Obstacles that shape goals and difficulty | bot win rate |
| 5 | Merge-2 / merge-3 | `merge` | merge | Combine identical items into the next tier | economy sim |
| 6 | Sort (water / ball / goods) | `sort-puzzle` | sort | Move stacks until each container is uniform | BFS/A* |
| 7 | Block placement | `block-placement` | place | Place polyominoes; full lines clear | bot survival |
| 8 | Falling-piece line clear | `line-clear` | place | Falling tetrominoes; complete rows vanish | bot survival |
| 9 | Sliding tiles and blocks | `sliding-tiles` | spatial logic | Slide pieces in a frame to a target | BFS/A*, parity |
| 10 | Sokoban (push) | `sokoban` | spatial logic | Push boxes onto goals; never pull | BFS/A* + deadlock |
| 11 | Pipe / flow connect | `flow-connect` | spatial logic | Connect pairs with non-crossing paths | constraint search |
| 12 | Pin-pull | `pin-pull` | spatial logic (physics) | Pull pins in the right order | scripted physics replay |
| 13 | Screw-out | `screw-out` | spatial logic | Unscrew in an order that frees layered plates | search over order |
| 14 | Triple-match tray | `triple-match-tray` | tile-pick | Pick items into a tray; triples clear | search / bot |
| 15 | Mahjong solitaire | `mahjong-solitaire` | tile-pick | Remove free matching pairs from a layered stack | reverse generation |
| 16 | Nonogram | `nonogram` | logic | Fill cells to satisfy row/column run clues | line solver + uniqueness |
| 17 | Sudoku and variants | `sudoku-variants` | logic | Fill digits under region constraints | constraint solver + uniqueness |
| 18 | Word formation | `word-formation` | word | Build words from letters under constraints | dictionary search |
| 19 | Hidden object | `hidden-object` | perception | Find listed items in a dense scene | human/VLM check |
| 20 | Spot-the-difference | `spot-the-difference` | perception | Find N differences between two images | mask check |
| 21 | Physics puzzles | `physics-puzzle` | physical | Manipulate a simulation to reach a goal | headless replay |
| 22 | Rotation puzzles | `rotation-puzzle` | geometric | Rotate pieces to connect or align | constraint propagation |
| 23 | Tangram and packing | `packing-puzzle` | geometric | Fit pieces exactly into a shape | exact cover (DLX) |

## 3. Tile-matching family

### 03.01 Match-3 swap — `match3-swap`

- **ID:** `match3-swap` · **Category:** puzzle / tile-matching · **Player fantasy:** "I spot the move that sets off a glorious chain reaction."
- **Core rules:**
  - State: a grid (commonly up to 9×9, with holes for shaped boards) of tiles with `colour ∈ {1..k}` plus blockers and specials. Gravity direction (usually down).
  - Trigger: swap two orthogonally adjacent tiles. The swap is legal only if it creates at least one line of ≥ 3 same-colour tiles; otherwise it animates back (and usually costs no move).
  - Resolution loop: find all matches → clear them (spawn specials from 4+, L/T shapes) → apply damage to adjacent blockers → gravity drops tiles → refill from top with random colours → repeat until no matches (cascades).
  - Goals per level: collect N of colour/item, clear all under-tiles (jelly), bring items to the bottom, reach score; limited by moves (common) or time.
  - If no legal move exists, reshuffle (and never cost the player for it).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Colour count k | 4–6 | The strongest lever: a random line of 3 is monochrome with probability 1/k² (6.25 % at k=4, 4 % at k=5, 2.8 % at k=6), so more colours = fewer matches and cascades |
| Moves | 15–40 | Second lever; tune to bot median + slack |
| Board shape / holes | full to fragmented | Fragmented boards reduce cascades and combo room |
| Refill bias | pure random to goal-weighted | Hidden DDA lever; disclose policy internally, keep it honest |
| Goal amount | per colour 20–80 | Length of level |
| Special-spawn shapes | 4-line, L/T, 5-line, 2×2 | Power curve |

- **Dynamics:** scanning for moves; deciding between immediate goal progress and setting up specials; cascades as luck-driven surprise rewards; end-of-level tension around the last moves.
- **Aesthetics (MDA):** Challenge, Sensation, Submission (relaxing scan), Discovery (new blockers).
- **Feedback and juice:** swap with slight overshoot, matched tiles pop with particles, cascade sound pitch rises per chain step, goal counter fly-to-HUD animations, "Sweet!"-style praise on cascades, end-of-level special-piece "sugar crush" bonus.
- **Failure modes and exploits:** boards generated with pre-existing matches or no moves (generator must prevent both); difficulty from pure RNG with no agency (players notice; keep a skill component via specials); "near-miss" engineered losses to sell extra moves (an ethical red line).
- **Mobile fit:** the archetypal one-hand portrait mechanic; levels of 1–4 min; fully interruption-safe (turn-based).
- **Monetization hooks and ethical limit:** extra moves on fail (+5 moves), pre-level boosters, in-level boosters, lives (see `references/04-economy-resource-mechanics.md`). Do not manipulate refills to create artificial near-misses timed with offers.
- **Implementation notes:** board as 1D array `w*h`; match detection by row and column scans producing runs, then union runs sharing cells to detect L/T shapes. Initial fill: draw each cell from colours excluding any that would complete a run with the two cells left or above; then verify ≥ 1 legal move (try all swaps, O(w·h)).

```text
resolve(): chain = 0
  loop: runs = find_runs(board); if !runs: break
        groups = union_by_shared_cells(runs); for g in groups: spawn_special_if_any(g); clear(g); damage_adjacent(g)
        apply_gravity(); refill(rng); chain += 1
  if !has_legal_move(board): reshuffle_preserving_colours(rng)
```

- **Reference games:** Candy Crush Saga, Royal Match, Homescapes / Gardenscapes, Bejeweled (origin of the modern form).
- **Combines well with:** `special-pieces`, `blockers`, meta decoration and narrative (`references/10-narrative-exploration-mechanics.md`), lives and boosters (`references/04-economy-resource-mechanics.md`).

### 03.02 Blast / collapse — `blast-collapse`

- **ID:** `blast-collapse` · **Category:** puzzle / tile-matching · **Player fantasy:** "Tap, boom — I smash big clusters with zero friction."
- **Core rules:**
  - Grid of coloured cubes. Trigger: tap any cube in an orthogonally connected same-colour group of size ≥ `min_group` (2 in modern blast games).
  - Effect: the group is removed; larger groups spawn a special at the tapped cell by size thresholds (in Toon Blast, roughly 5+ → rocket, 7+ → bomb, 9+ → colour-clearing disco ball). Gravity and refill follow; tapping specials activates them.
  - Group-size hints: cubes in big groups display the icon of the special they would create.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| `min_group` | 2 (casual) – 3 | 2 removes "no move" states almost entirely |
| Colour count | 4–6 | Group size distribution — the main lever |
| Special thresholds | 5 / 7 / 9 | Power accessibility |
| Moves | 20–40 | Length and pressure |
| Refill from top vs from columns | — | Cascade frequency (low in blast; matches are tapped, not formed) |

- **Dynamics:** faster and less deliberate than swap match-3; the planning is about growing groups (removing a separator colour to merge two clusters) for bigger specials.
- **Aesthetics (MDA):** Sensation, Submission, Challenge.
- **Feedback and juice:** immediate pop with satisfying low thud, special-icon previews on big groups, big rocket and bomb animations; tap response under 50 ms.
- **Failure modes and exploits:** mindless tapping working too well (blockers and goals force deliberate group-building); boards with only singletons (rare at `min_group` 2 but must reshuffle).
- **Mobile fit:** single-tap verb, the most accessible tile-matcher; very low cognitive entry.
- **Monetization hooks and ethical limit:** identical to match-3 (moves, boosters, lives).
- **Implementation notes:** flood fill (BFS) from the tapped cell; cache group IDs per board state for hint icons (recompute after each resolution, O(cells)). Verification: `match3_sim.py` cannot run these boards (it implements swap rules only), so write a seeded project simulator with a greedy largest-group bot and a one-tap lookahead bot, and record the result in `solver.bot_win_rate` and `solver.runs`; store the board as `layout.type: "custom"` because the level-spec schema has no blast layout.
- **Reference games:** Toon Blast, Toy Blast, Pet Rescue Saga, SameGame (classic ancestor).
- **Combines well with:** `special-pieces`, `blockers`, team chests and social help (`references/06-social-competitive-mechanics.md`).

### 03.03 Special pieces and combos — `special-pieces`

- **ID:** `special-pieces` · **Category:** puzzle / tile-matching power system · **Player fantasy:** "I engineer a massive combo that wipes the board."
- **Core rules:**
  - Specials spawn from match shapes (swap games) or group sizes (blast games). A canonical swap-game set:

| Shape | Candy Crush Saga | Royal Match | Effect pattern |
|---|---|---|---|
| 4 in a line | striped candy | rocket | Clears a full row or column |
| 2×2 square | — | propeller | Flies to a goal-relevant tile |
| L or T (5 tiles) | wrapped candy | TNT | Area blast (3×3, often twice) |
| 5 in a line | colour bomb | light ball | Clears every tile of the swapped colour |

  - Combos: swapping two specials triggers a combined effect stronger than both. Typical pattern: line + line = cross; line + area = 3-wide cross; area + area = large area (5×5); colour + line = convert all tiles of a colour into line clearers then fire; colour + colour = clear board.
  - Specials activate when matched, tapped (some games), or hit by another special (chain activation).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Special spawn thresholds | 4 / 5 / L-T / square | Frequency of power moments |
| Area blast radius | 1 (3×3) – 2 (5×5) | Board-clearing power |
| Combo strength | 2–4× the sum of parts | Reward for setup skill |
| Specials preserved between levels | no (usual) | Avoids snowballing |
| End-of-level conversion | remaining moves → specials | Celebration, score |

- **Dynamics:** the skill layer of tile-matchers — players trade immediate goal progress for special setups; combos create memorable peaks and social sharing moments.
- **Aesthetics (MDA):** Sensation, Challenge, Discovery.
- **Feedback and juice:** unique sound and VFX per special, anticipation glow when two specials are adjacent, screen shake for combos, slow-motion on colour-colour.
- **Failure modes and exploits:** specials too common (board trivialises), combos too weak (no reason to set up), chain reactions too long (cap visual duration ~2–3 s, resolve logically instantly).
- **Mobile fit:** big readable icons; good thumb affordance.
- **Monetization hooks and ethical limit:** pre-level boosters that start the board with specials; sell them only as optional advantages, with levels tuned to be passable without them.
- **Implementation notes:** specials as tile `kind` with an `activate(board, origin, partner?)` function returning affected cells; a combo table keyed by unordered pair of kinds. Process activations in a queue (BFS order) for deterministic chain results.

```text
queue = [initial_activation]; while queue: a = queue.pop(0); cells = a.pattern(board)
  for c in cells: if board[c].is_special and !board[c].activated: queue.append(activation(board[c])); board[c].activated = true
  damage(cells)
```

- **Reference games:** Candy Crush Saga, Royal Match, Toon Blast (blast specials), Bejeweled (Flame and Hypercube gems).
- **Combines well with:** `match3-swap`, `blast-collapse`, `blockers`, boosters (`references/04-economy-resource-mechanics.md`).

### 03.04 Blocker taxonomy — `blockers`

- **ID:** `blockers` · **Category:** puzzle / tile-matching obstacle system · **Player fantasy:** "Every board is a new problem to crack."
- **Core rules:** blockers are cell modifiers with defined clearing rules. Taxonomy by behaviour (design new blockers by picking a row and giving it a theme):

| Type | Rule | Clearing | Example (game) | Difficulty role |
|---|---|---|---|---|
| Layered | n hit points (1–5) | Adjacent match or special, −1 layer per hit | frosting/boxes (Candy Crush, Royal Match) | Volume and goal length |
| Lock / cage | Tile inside cannot move | Match the locked tile itself | licorice lock (Candy Crush) | Constrains swaps |
| Under-tile | Lies under a tile; goal object | Match on top of it | jelly (Candy Crush), grass (Royal Match) | Spatial coverage goals |
| Spreader | Grows into neighbours each turn not hit | Adjacent match | chocolate (Candy Crush) | Time pressure, tempo |
| Collect / drop | Item must reach an exit row | Clear tiles below it | ingredients (Candy Crush) | Directional planning |
| Countdown | Explodes after N moves | Clear before 0 | candy bombs (Candy Crush) | Hard fail condition |
| Generator | Spawns tiles or blockers | Usually indestructible or n-hit | candy cannons | Ongoing pressure |
| Special-only | Immune to normal matches | Specials only | various | Forces special setups |
| Immovable / hole | Not part of the board | Never | shaped boards | Reduces cascades |
| Conveyor / portal | Moves tiles each turn | n/a | conveyors, portals | Disorientation (use sparingly) |

  - Each blocker has: `hp`, `damage_sources` (adjacent match, special, colour-specific), `blocks_gravity` (bool), `blocks_swap` (bool), `on_turn_end` behaviour.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Blocker coverage | 10–50 % of cells | Main board-difficulty lever after colours |
| Layer count | 1–5 | Goal length |
| Spreader growth | 1 cell per un-hit turn | Tempo pressure |
| Countdown start | 5–15 moves | Fail risk |
| New blocker cadence | one new type every 15–40 levels | Novelty pacing |

- **Dynamics:** board-specific strategies; prioritisation (which threat first); blockers interact with specials (rockets through boxes).
- **Aesthetics (MDA):** Challenge, Discovery.
- **Feedback and juice:** distinct crack/shatter per layer, layer count readable, spreader growth animation telegraphed, countdown numbers pulsing red at ≤ 3.
- **Failure modes and exploits:** too many blocker types at once (introduce one per teach level); unreadable layer counts; blockers that soft-lock goals (collect item trapped behind indestructible generator — validate with bots).
- **Mobile fit:** must be legible at 40–50 dp tile size.
- **Monetization hooks and ethical limit:** blocker-clearing boosters (hammer); avoid "impossible without booster" boards.
- **Implementation notes:** data-driven blocker definitions; damage events routed through a single `damage_cell(c, source)` function so new blockers need no core changes. Bot-test every new blocker in 20+ level configurations.
- **Reference games:** Candy Crush Saga, Royal Match, Homescapes, Toon Blast.
- **Combines well with:** `match3-swap`, `blast-collapse`, `special-pieces`, level content pipelines (`level-design`).

## 4. Merge, sort and place

### 03.05 Merge-2 / merge-3 — `merge`

- **ID:** `merge` · **Category:** puzzle / merge · **Player fantasy:** "From humble pieces I grow something grand — and my board becomes a world."
- **Core rules:**
  - Items have `chain` and `tier`. Merging identical items (same chain and tier) produces tier+1.
  - **Merge-2:** drag one item onto an identical one → one item of tier+1 (Merge Mansion, Travel Town).
  - **Merge-3:** group 3 identical connected items → one tier+1; merging 5 yields 2 (Merge Dragons pattern) — a bonus for patience.
  - **Generators** produce base items on tap (cost energy) or on timers; **orders** request specific items for rewards; **board space** is finite (e.g., 7×9) — the central constraint.
  - Slide variant: 2048 (all tiles slide; equal tiles merge, powers of two). Drop variant: Suika (physics merge, see `physics-stacking` in file 01).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Board size | 7×9 – 9×11 cells | Space pressure |
| Chain length | 8–15 tiers | Goal horizon |
| Items per merge | 2 or 3 (+5→2 bonus) | Effort per tier: 2^n vs 3^n base items |
| Generator energy cost | 1 per tap | Energy as session limiter |
| Generator cooldown/charges | 10–30 charges, 1–4 h recharge | Session cadence |
| Order difficulty | tier 3–10 items | Progress pacing |

- **Dynamics:** inventory management and space optimisation; long-horizon planning toward high tiers; tidy-board satisfaction; energy-paced sessions.
- **Aesthetics (MDA):** Submission, Expression (board arrangement), Discovery (new tiers), Narrative (renovation meta).
- **Feedback and juice:** merge pop with tier-up shimmer, new-tier discovery card the first time, magnetic snapping, sparkle on mergeable pairs (hint after 3–5 s idle).
- **Failure modes and exploits:** board clog with no way forward (always provide sell/storage/bin); exponential base-item requirements making high tiers impossible without spend (simulate: tier n merge-2 needs 2^(n−1) base items; tier 10 = 512); energy starvation in the first sessions.
- **Mobile fit:** drag one-handed; sessions bounded by energy (3–10 min).
- **Monetization hooks and ethical limit:** energy refills, generator speed-ups, extra storage, bubble items (pay to keep a duplicate). Keep energy pricing transparent and avoid FOMO bubbles that disappear in seconds.
- **Implementation notes:** merge-3 group detection via flood fill from the drop cell; merge-2 is a simple drop-target check. Economy should be simulated end-to-end: generator outputs → merge costs → order rewards (model with `${CLAUDE_PLUGIN_ROOT}/scripts/economy_sim.py` and an `economy-model` file).

```text
on_drop(item, cell): t = board[cell]
  if t and t.chain == item.chain and t.tier == item.tier and t.tier < MAX[t.chain]: board[cell] = Item(t.chain, t.tier+1); remove(item)
  elif t is null: move(item, cell) else: swap_or_return(item, cell)
```

- **Reference games:** Merge Mansion, Travel Town, Merge Dragons!, 2048, Threes!.
- **Combines well with:** energy and generators (`references/04-economy-resource-mechanics.md`), renovation narrative (`references/10-narrative-exploration-mechanics.md`), collection (`references/09-collection-crafting-building.md`).

### 03.06 Sort (water / ball / goods) — `sort-puzzle`

- **ID:** `sort-puzzle` · **Category:** puzzle / sort · **Player fantasy:** "I bring order to chaos, one satisfying pour at a time."
- **Core rules:**
  - **Water/ball sort:** `n` containers of capacity `c` (typically 4) hold coloured units; `k` colours with exactly `c` units each; usually `k + 2` containers (two empty).
  - Move: take the top contiguous run of one colour from a source; place onto a destination whose top is the same colour or that is empty, as many units as fit. Goal: every container uniform (full single colour) or empty.
  - **Goods sort:** shelves with slots (often 3) and hidden layers behind; placing 3 identical items on one shelf clears them and reveals the next layer. Adds hidden information and a timer.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Colours k | 3 – 12+ | Primary difficulty lever |
| Capacity c | 3–5 | Higher = longer runs, more planning |
| Empty containers | 1–3 | 1 is very hard; 2 is standard; 3 is easy |
| Hidden units (mystery) | 0–50 % | Information uncertainty |
| Undo / extra tube | booster | Recovery from dead ends |

- **Dynamics:** look-ahead planning; recognising dead ends; satisfying completion streaks.
- **Aesthetics (MDA):** Submission (calm), Challenge, Sensation (pouring).
- **Feedback and juice:** liquid pour arc with gurgle, container "complete" cap and confetti, colour-blind patterns on units.
- **Failure modes and exploits:** unsolvable shuffles (generate by solver or reverse moves from solved state with verification); colour discrimination (≥ 8 colours needs patterns/symbols — accessibility); dead-end states without warning (offer undo or detect "no progress possible").
- **Mobile fit:** tap source, tap destination; turn-based; perfect one-hand.
- **Monetization hooks and ethical limit:** extra empty container, undo charges; ads between levels at a measured cadence.
- **Implementation notes:** state = tuple of stacks; canonicalise by sorting containers for transposition tables. BFS for `min_moves` on small levels, A* with heuristic "number of colour boundaries" for larger. `puzzle_solver.py` supports `layout.type: sort`.
- **Reference games:** Water Sort Puzzle, Ball Sort Puzzle, Goods Sort (triple-shelf variant).
- **Combines well with:** `triple-match-tray`, level meta (`references/05-progression-meta-mechanics.md`), rewarded ads (`references/12-monetization-linked-mechanics.md`).

### 03.07 Block placement — `block-placement`

- **ID:** `block-placement` · **Category:** puzzle / place · **Player fantasy:** "I fit every piece perfectly and clear lines in big satisfying combos."
- **Core rules:**
  - Board `w×h` (Block Blast 8×8, 1010! 10×10, Woodoku 9×9 with 3×3 boxes also clearing).
  - A tray presents 3 polyomino pieces; drag each onto the board where it fits (no rotation in the classic form). When all 3 are placed, the tray refills with 3 new pieces.
  - Any full row or column (and full 3×3 box in Woodoku) clears. Multiple simultaneous clears and consecutive-turn clears give combo bonuses.
  - Game over: none of the remaining tray pieces fits anywhere. Endless score-attack; adventure modes add goals.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Board size | 8×8 – 10×10 | Smaller = tenser |
| Piece set | 1–5 cell polyominoes, 15–30 shapes | Large shapes are the killers |
| Piece weighting | uniform vs adaptive (easier when board is full) | Hidden DDA lever |
| Combo multiplier | +1 step per consecutive clearing turn | Rewards planning |
| Tray size | 3 | Planning horizon |

- **Dynamics:** keep the board open; reserve space for 3×3 and long-line pieces; plan multi-line clears; risk vs safety.
- **Aesthetics (MDA):** Submission (flow), Challenge, Sensation (clears).
- **Feedback and juice:** ghost preview, highlight of lines that would clear, cascading line clear with rising notes, big "combo ×N" text, screen shake scaled to lines.
- **Failure modes and exploits:** generator dealing unplaceable trays early (guarantee at least one placeable piece per refill in early game); adaptive piece weighting players perceive as unfair (keep it subtle and symmetric).
- **Mobile fit:** drag one-handed; turn-based; infinitely interruptible. Block Blast! was reported as the most-downloaded mobile game of H1 2026 (see Volatile facts).
- **Monetization hooks and ethical limit:** ads between games, continue with rotation/clear boosters; avoid intrusive interstitials mid-run.
- **Implementation notes:** board as bitmask rows (`uint16` per row) for O(1) row checks; column checks via precomputed masks. Placement test: `(board_rows[y+i] & (piece_row[i] << x)) == 0` for all i.
- **Reference games:** Block Blast!, 1010!, Woodoku, Tetris (as the line-clear ancestor).
- **Combines well with:** `line-clear`, `drag` (`references/01-verbs-movement-physics.md`), adventure goals (`blockers`), leaderboards (`references/06-social-competitive-mechanics.md`).

### 03.08 Falling-piece line clear — `line-clear`

- **ID:** `line-clear` · **Category:** puzzle / place (real-time) · **Player fantasy:** "Calm under pressure, I keep the well clean as speed rises."
- **Core rules:**
  - Well of `10 × 20` visible cells (Tetris Guideline). Tetrominoes spawn at top and fall at gravity `G` (cells/frame); the player moves, rotates and drops.
  - A piece locks after resting for `lock_delay`; full rows clear; rows above fall. Clearing 4 rows at once ("Tetris") scores most.
  - Modern guideline conventions: 7-bag randomiser (each set of 7 contains each piece once), hold slot, next-piece queue, ghost piece, wall kicks.
  - Game over when a new piece cannot spawn.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Gravity curve | level 1 slow → 20G at top levels | Core difficulty |
| Lock delay | ~0.5 s, with move-reset limit | Forgiveness at high speed |
| Randomiser | 7-bag vs pure random | Bag prevents droughts; random adds variance |
| Preview count | 1–6 | Planning horizon |
| Garbage rows (versus) | 1–4 per attack | PvP pressure |

- **Dynamics:** stacking for multi-line clears vs safety; T-spins as expert techniques; versus garbage exchanges.
- **Aesthetics (MDA):** Challenge, Submission (flow), Fellowship (versus).
- **Feedback and juice:** line flash before clear, drop trail on hard drop, level-up music tempo increase.
- **Failure modes and exploits:** touch controls are the main problem — precise left/right movement is hard on glass (use drag-to-position with ghost, tap to rotate, swipe down to drop); licensing: "Tetris" name and trade dress are trademarked (see `legal-ethics`).
- **Mobile fit:** portrait; sessions 2–10 min; needs good control design (file 11).
- **Monetization hooks and ethical limit:** cosmetics, battle pass; avoid pay-to-win in versus.
- **Implementation notes:** bag randomiser = shuffle 7 pieces with seeded RNG, pop, refill when empty. Rotation system as data tables of kick offsets per piece and rotation transition.
- **Reference games:** Tetris (mobile editions), Puyo Puyo (colour-chain falling variant), Dr. Mario World (falling capsules, discontinued).
- **Combines well with:** `block-placement`, versus multiplayer (`references/06-social-competitive-mechanics.md`), `rhythm-timing` (`references/01-verbs-movement-physics.md`).

## 5. Spatial logic

### 03.09 Sliding tiles and blocks — `sliding-tiles`

- **ID:** `sliding-tiles` · **Category:** puzzle / spatial logic · **Player fantasy:** "I see the sequence that untangles the jam."
- **Core rules:**
  - **Tile variant (15-puzzle):** an `n×n` frame with `n²−1` numbered tiles and one gap; slide a tile adjacent to the gap into it; goal is a target arrangement (numbers or an image).
  - **Block variant (Rush Hour / Unblock Me):** rectangular blocks on a 6×6 grid slide along their long axis only; goal is to get the target block out of the exit.
  - **Exit variant (parking jam):** each car can only move in its facing direction until it leaves the board or hits something; order of removal is the puzzle.
  - Solvability (tile variant): half of all permutations are unsolvable. With width `n` odd, solvable iff inversion count is even; with `n` even, solvable iff `(inversions + row of the gap counted from the bottom, 1-based)` is odd.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Grid size | 3×3 – 5×5 (tiles); 6×6 (blocks) | State space |
| Min moves | 5–60 (blocks) | Primary difficulty measure |
| Blockers / walls | 0–4 fixed cells | Constrains space |
| Move counting | moves vs cells moved | Scoring strictness |
| Star thresholds | `min_moves`, +20 %, +50 % | Mastery targets |

- **Dynamics:** backward reasoning from the goal; recognising which blocks must move first; satisfying "aha" chains.
- **Aesthetics (MDA):** Challenge, Discovery.
- **Feedback and juice:** smooth slides with soft click at end, exit celebration, move counter vs par.
- **Failure modes and exploits:** generated levels with trivial solutions (filter by `min_moves` and by "number of distinct blocks moved"); unsolvable shuffles (only generate by random moves from solved, or check parity).
- **Mobile fit:** drag or swipe on a block; turn-based; very interruption-friendly.
- **Monetization hooks and ethical limit:** hints (next optimal move from solver), skip-level; never make levels unsolvable to sell skips.
- **Implementation notes:** BFS over states (encode block positions as a compact integer/string); for Rush Hour-sized puzzles BFS completes quickly. Rank generated levels by `min_moves` and branching. `puzzle_solver.py --algo bfs` with `layout.type: sliding`.

```text
solvable_15(perm, n): inv = count_inversions([t for t in perm if t != 0])
  if n % 2 == 1: return inv % 2 == 0
  gap_row_from_bottom = n - (perm.index(0) // n); return (inv + gap_row_from_bottom) % 2 == 1
```

- **Reference games:** Unblock Me, Rush Hour (ThinkFun, physical original), Parking Jam 3D, 15-puzzle apps.
- **Combines well with:** `sokoban`, `directional-swipe` (`references/01-verbs-movement-physics.md`), hint economies (`references/12-monetization-linked-mechanics.md`).

### 03.10 Sokoban (push) — `sokoban`

- **ID:** `sokoban` · **Category:** puzzle / spatial logic · **Player fantasy:** "One wrong push and it's stuck — I think ahead and get it right."
- **Core rules:**
  - Grid with walls, floor, goals, boxes and a player. The player moves orthogonally; walking into a box pushes it one cell if the cell beyond is free. Boxes cannot be pulled; the player cannot push two boxes at once.
  - Goal: all boxes on goals. Undo is standard on mobile.
  - Deadlocks: a box in a non-goal corner, two boxes side-by-side against a wall with no goals, a box against a wall with no goal along that wall segment — positions from which the level cannot be solved.
  - Computational note: Sokoban is PSPACE-complete in general (Culberson, 1997), so large levels need heuristics, not brute force.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Boxes | 1–6 (mobile) | State space explodes per box |
| Level size | 6×6 – 12×12 | Navigation vs puzzle density |
| Min pushes | 5–80 | Difficulty measure (pushes matter more than moves) |
| Variants | ice (slides), switches, one-way doors, rule pushing (Baba Is You) | Twist content |
| Undo | unlimited | Mobile essential |

- **Dynamics:** irreversibility forces planning; recognising deadlocks; elegant minimal-element designs.
- **Aesthetics (MDA):** Challenge, Discovery.
- **Feedback and juice:** box scrape sound, goal lock-in click and glow, deadlock indicator (optional assist: tint stuck boxes).
- **Failure modes and exploits:** tedium from long walking (tap-to-move pathfinding to any reachable cell); unsolvable generated levels; frustration without undo.
- **Mobile fit:** swipe or tap-to-path; turn-based.
- **Monetization hooks and ethical limit:** hints and level packs; premium works well (puzzle purists dislike energy systems).
- **Implementation notes:** solver state = (box positions set, player reachable-region canonical cell). Prune with static deadlock cells (precomputed: cells from which a box can never reach any goal) and freeze deadlocks. `puzzle_solver.py` supports `layout.type: sokoban` with BFS or A* (heuristic: sum of min box-goal distances).
- **Reference games:** Sokoban (Thinking Rabbit, 1982), Baba Is You (mobile port), Monument Valley (contrast: no irreversibility).
- **Combines well with:** `sliding-tiles`, switches and doors (`references/10-narrative-exploration-mechanics.md`), premium level packs.

### 03.11 Pipe / flow connect — `flow-connect`

- **ID:** `flow-connect` · **Category:** puzzle / spatial logic · **Player fantasy:** "Every line finds its partner and the whole board fills perfectly."
- **Core rules:**
  - **Flow variant:** grid with pairs of coloured endpoints. Draw paths (orthogonal steps) connecting each pair; paths cannot cross or overlap; the level is complete when all pairs are connected and every cell is covered.
  - **Pipe-placement variant:** a stream of pipe pieces is placed on a grid before liquid starts flowing (Pipe Mania); the goal is a path of minimum length before the flow arrives.
  - **One-stroke variant:** draw a single path visiting every edge or node exactly once (Eulerian path puzzles).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Grid size | 5×5 – 15×15 | Size and time per level |
| Pairs | 4–16 | Interaction density |
| Bridges / warps / walls | 0–few | Twists |
| Fill-all rule | required / bonus | Required raises difficulty a lot |
| Unique solution | enforced / not | Enforced makes deduction possible |

- **Dynamics:** deduction (forced cells near corners and edges), path routing intuition, global vs local reasoning.
- **Aesthetics (MDA):** Challenge, Submission (calm), Discovery.
- **Feedback and juice:** path trail with endpoint pulse, "connected" chime per pair, fill percentage meter, final board-fill flourish.
- **Failure modes and exploits:** multiple solutions making deduction impossible (enforce uniqueness at generation); finger hiding path ends (show a zoom bubble above the finger).
- **Mobile fit:** single-finger draw; turn-based; excellent.
- **Monetization hooks and ethical limit:** hints that reveal one full path; level packs.
- **Implementation notes:** generate by constructing a full random Hamiltonian-ish partition of the grid into paths (random walks with backtracking), then keep only endpoints; verify uniqueness with a SAT/constraint solver (each cell one colour; each endpoint degree 1; each path cell degree 2 within its colour).
- **Reference games:** Flow Free, Pipe Mania (classic), One Line puzzle apps, Two Dots (path-connect matching hybrid).
- **Combines well with:** `draw-a-path` (`references/01-verbs-movement-physics.md`), `rotation-puzzle`, daily puzzles (`references/08-time-energy-session-mechanics.md`).

### 03.12 Pin-pull — `pin-pull`

- **ID:** `pin-pull` · **Category:** puzzle / spatial logic (physics) · **Player fantasy:** "Pull the right pin and everything falls into place — gold for the hero, lava for the monster."
- **Core rules:**
  - A vertical cross-section with compartments separated by removable pins. Compartments hold particulates (gold coins, water, lava, gems), enemies, hazards, the hero.
  - Tap/swipe a pin to remove it; contents fall and flow under physics. Interactions: lava + water → stone (safe); lava touching hero → lose; enemies fall into lava → die; gold reaching hero → win.
  - Order matters: a wrong first pin is often fatal. Level is a short sequence (2–5 pins) with one or few valid orders.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Pins per level | 2–6 | Number of orderings (n!) |
| Element interactions | 3–6 rules | Depth of reasoning |
| Particles | 50–300 small bodies | Spectacle vs determinism and perf |
| Valid orderings | 1–3 | Strictness |
| Decoy pins | 0–2 | Trap content |

- **Dynamics:** quick causal reasoning; visual prediction of flows; "obvious trap" humour.
- **Aesthetics (MDA):** Discovery, Sensation (flow), Fantasy (rescue story).
- **Feedback and juice:** pin slide-out with metallic zing, satisfying particle flow sounds, hero reaction animations (fear, joy).
- **Failure modes and exploits:** physics non-determinism making the same order produce different outcomes (use fixed timestep and deterministic particle sim, or rule-based flow on a grid); ads promising this mechanic while the game is something else (store policy and reputation risk).
- **Mobile fit:** single swipe per move; 10–30 s levels; hyper-casual staple.
- **Monetization hooks and ethical limit:** skip level via rewarded ad, cosmetic hero skins.
- **Implementation notes:** brute-force every pin order offline (n! ≤ 720 for 6 pins), replaying the physics headlessly; record the winning orders in `level-spec.solver`.
- **Reference games:** Hero Rescue, Pull the Pin, Hero Wars (its widely discussed ads showcased pin puzzles; the core game is an RPG).
- **Combines well with:** `physics-puzzle`, narrative rescue framing (`references/10-narrative-exploration-mechanics.md`), hybrid-casual meta (`references/05-progression-meta-mechanics.md`).

### 03.13 Screw-out — `screw-out`

- **ID:** `screw-out` · **Category:** puzzle / spatial logic · **Player fantasy:** "I take the whole contraption apart, piece by piece, without getting stuck."
- **Core rules:**
  - Layered plates (wood, metal) are held by screws. A plate falls away when all its screws are removed. Screws can only be removed if no plate above covers their head.
  - **Hole-transfer variant:** tap a screw, then tap an empty hole; the screw moves there (possibly pinning a different plate). Goal: drop all plates.
  - **Colour-box variant:** removed screws go into colour boxes (often 3 slots each) of matching colour; a full box is cleared and replaced; non-matching screws go to a limited buffer — when the buffer is full, you lose (tray logic like `triple-match-tray`).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Plates / layers | 5–40 plates, 3–10 layers | Volume and occlusion |
| Screw colours (box variant) | 3–8 | Buffer pressure |
| Buffer slots | 4–7 (+1 via booster) | Primary fail lever |
| Free holes (transfer variant) | 1–4 | Planning tightness |
| Timer | none – 3 min | Pressure |

- **Dynamics:** occlusion reasoning (what is on top), ordering, buffer management; satisfying physical "clatter" of falling plates.
- **Aesthetics (MDA):** Sensation (tactile), Submission, Challenge.
- **Feedback and juice:** screw unscrew spin and squeak, plate swing then fall with physics, box fill and close animation.
- **Failure modes and exploits:** ambiguous occlusion in 3D views (allow rotation or use 2D layering); unsolvable colour sequences in the box variant (generate by reverse disassembly and verify).
- **Mobile fit:** taps only; 1–3 min levels; one-hand.
- **Monetization hooks and ethical limit:** extra buffer slot, hole drill, undo; the buffer-fail pattern is prone to engineered near-misses — tune for fairness.
- **Implementation notes:** model occlusion as a DAG (plate A covers screw s if A is above s's plate and overlaps the head point). Solve the box variant as a search over removal orders with the buffer as state; prune with dominance (removing a screw that completes a box is never worse).
- **Reference games:** Wood Nuts & Bolts Puzzle, Screw Jam, Screw Puzzle apps (many interchangeable titles — check current charts).
- **Combines well with:** `triple-match-tray`, `pin-pull`, boosters (`references/04-economy-resource-mechanics.md`).

## 6. Tile-pick and tray family

### 03.14 Triple-match tray — `triple-match-tray`

- **ID:** `triple-match-tray` · **Category:** puzzle / tile-pick · **Player fantasy:** "I scan the pile, grab the right ones and clear it before time runs out."
- **Core rules:**
  - A pile of items (3D objects in a physics heap, or 2D tiles in layered stacks). Every item type appears in multiples of 3.
  - Tap an accessible item → it moves into a tray of `s` slots (commonly 7). When 3 identical items are in the tray, they clear. If the tray fills with no triple, the level is lost.
  - Optional timer; goals (collect N of specific items); 2D tile variant: only uncovered tiles are tappable (layer occlusion).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Tray slots | 6–8 (7 is common) | Primary fail lever |
| Item types | 10–40 per level | Search difficulty |
| Pile size | 30–150 items | Duration |
| Timer | 60–300 s or none | Pressure |
| Look-alike items | 0–30 % | Perception difficulty |
| Occlusion depth (2D) | 2–6 layers | Planning under hidden info |

- **Dynamics:** visual search, then tray management (never take a third type when two pairs are open with only 1–2 free slots); hidden-information risk in layered variants.
- **Aesthetics (MDA):** Sensation, Challenge, Submission.
- **Feedback and juice:** items fly to tray in an arc, auto-sort tray so pairs sit together, triple-clear burst, tray slot warning (red pulse when ≤ 2 free).
- **Failure modes and exploits:** physics heaps hiding items forever (gentle shake/ shuffle); unwinnable layered deals (generate by reverse play: place triples in reverse order respecting the tray); timers that are too tight on low-end devices if physics slows.
- **Mobile fit:** single taps; portrait; 1–3 min levels.
- **Monetization hooks and ethical limit:** extra slot, undo, magnet (auto-collect a triple), time freeze, revive. Tray-full losses are near-misses by nature — tune by bot win rate, not by offer conversion.
- **Implementation notes:** tray as sorted list grouped by type; insertion keeps identical items adjacent. Reverse generator for 2D: start empty, repeatedly pick a type, place 3 tiles at currently-uncoverable positions, ensuring the forward game is winnable with tray capacity.
- **Reference games:** Match Factory!, Triple Match 3D, Zen Match (2D tile variant).
- **Combines well with:** `mahjong-solitaire`, `sort-puzzle`, `screw-out`, collection meta (`references/09-collection-crafting-building.md`).

### 03.15 Mahjong solitaire — `mahjong-solitaire`

- **ID:** `mahjong-solitaire` · **Category:** puzzle / tile-pick · **Player fantasy:** "Calm, methodical — I dismantle the whole tower pair by pair."
- **Core rules:**
  - A layered layout of tiles (classic: 144 mahjong tiles in the "turtle" arrangement). Tiles come in matching pairs (season and flower groups match within group).
  - A tile is **free** if no tile lies on top of it and at least its left or right side is open.
  - Remove any two free matching tiles. Win when all tiles are removed; lose when no free pair remains (shuffle optional).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Tile count | 36–144 | Duration |
| Layer depth | 2–5 | Occlusion difficulty |
| Distinct tile faces | 10–42 | Visual search load |
| Shuffles / hints | 0–3 free | Forgiveness |
| Deal generation | random vs solvable-by-construction | Fairness |

- **Dynamics:** foresight about which pair to take when more than two copies are free; freeing stacked tiles early.
- **Aesthetics (MDA):** Submission (calm), Challenge, Sensation (tactile clacks).
- **Feedback and juice:** selected tile lift, matching highlight on hint, pair-removal swoosh, dim non-free tiles (accessibility toggle).
- **Failure modes and exploits:** random deals can be unwinnable (generate by reverse placement); tiny tiles on phones (zoom, larger face art, simplified face sets for seniors).
- **Mobile fit:** taps; landscape for classic layouts, portrait layouts for mobile; senior-friendly audience.
- **Monetization hooks and ethical limit:** hints, shuffles, themes; ads between deals.
- **Implementation notes:** solvable generation — start with the empty layout; repeatedly choose two positions that would be free if placed now (respecting placement order), assign a matching pair; forward play following reverse order guarantees a solution.
- **Reference games:** Shanghai (1986, the computer origin), Mahjong Titan, Microsoft Mahjong, Vita Mahjong.
- **Combines well with:** `triple-match-tray`, daily challenges (`references/08-time-energy-session-mechanics.md`), collection of themes (`references/09-collection-crafting-building.md`).

## 7. Logic and word

### 03.16 Nonogram — `nonogram`

- **ID:** `nonogram` · **Category:** puzzle / logic · **Player fantasy:** "Pure deduction reveals a hidden picture."
- **Core rules:**
  - Grid `w×h`. Each row and column has a clue: the ordered lengths of consecutive filled runs (e.g., "3 1 2"). Fill cells and mark empties to satisfy all clues. The solution forms a picture.
  - Good puzzles have a unique solution reachable by line-by-line logic (no guessing). Nonogram solving is NP-complete in general, so uniqueness and logic-solvability must be checked by a solver.
  - Colour nonograms use coloured runs with clue colours.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Grid size | 5×5 – 30×30 | Duration |
| Logic depth needed | line-only vs multi-line contradiction | Difficulty |
| Mistake policy | immediate feedback vs check at end | Forgiveness |
| Lives / mistakes allowed | 3 – unlimited | Pressure |
| Colours | 1–6 | Complexity |

- **Dynamics:** overlap reasoning on long runs; edge logic; satisfying reveal.
- **Aesthetics (MDA):** Challenge, Discovery, Submission.
- **Feedback and juice:** completed rows/columns dim their clues, fill drag across multiple cells, final picture colourises and animates.
- **Failure modes and exploits:** non-unique puzzles from naive image conversion (always run uniqueness check); tiny cells on phones (zoom and drag-fill).
- **Mobile fit:** drag-fill; turn-based; perfect for commuting.
- **Monetization hooks and ethical limit:** hints, puzzle packs; lives systems feel punitive in logic puzzles — prefer hints.
- **Implementation notes:** line solver: for each line, enumerate (or DP) all placements consistent with known cells; cells filled in all placements → fill; empty in all → mark. Iterate to fixpoint; if unsolved, the puzzle needs guessing (reject or rate "expert").
- **Reference games:** Picross series (Nintendo), Nonograms Katana.
- **Combines well with:** `sudoku-variants`, collection of pictures (`references/09-collection-crafting-building.md`), daily puzzle (`references/08-time-energy-session-mechanics.md`).

### 03.17 Sudoku and variants — `sudoku-variants`

- **ID:** `sudoku-variants` · **Category:** puzzle / logic · **Player fantasy:** "My reasoning cracks a problem that looked impossible."
- **Core rules:**
  - Classic: 9×9 grid in 3×3 boxes; place 1–9 so each row, column and box contains each digit once. Given clues make the solution unique; the minimum for a uniquely solvable classic sudoku is 17 clues (McGuire, Tugemann and Civario, 2012).
  - Variants add constraints: **Killer** (cages with sums), **Jigsaw** (irregular regions), **Diagonal** (both diagonals unique), **Thermo** (digits increase along thermometers), **Arrow**, **Sandwich**, **Kakuro**-like sums, mini 4×4/6×6 for beginners.
  - Difficulty is graded by the hardest technique required (singles → pairs/triples → pointing/claiming → X-wing/swordfish → chains).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Clue count | 22–40 (classic) | Weak proxy; technique grading is better |
| Required technique tier | 1–6 | True difficulty |
| Notes / auto-notes | manual vs auto | Accessibility vs purity |
| Mistake limit | 3 – unlimited | Pressure |
| Timer | visible / hidden | Stress vs competition |

- **Dynamics:** constraint propagation by hand; flow from long scanning sessions; mastery of named techniques.
- **Aesthetics (MDA):** Challenge, Submission.
- **Feedback and juice:** highlight same digits and row/column/box of the selected cell, completion flash per unit, error shake.
- **Failure modes and exploits:** non-unique puzzles (verify by solver counting solutions up to 2); "guess-required" puzzles labelled as easy; ads interrupting long solving sessions.
- **Mobile fit:** tap cell + digit pad in the thumb zone; sessions 5–20 min (longer than most casual; supports pause).
- **Monetization hooks and ethical limit:** hints, ad-free subscription, daily challenge streaks; avoid punitive energy.
- **Implementation notes:** generator: create a full valid grid (randomised backtracking), remove clues while uniqueness holds (DLX or backtracking solver with solution count cap 2), grade with a human-technique solver; reject if technique tier mismatches target.
- **Reference games:** Sudoku.com, Killer Sudoku apps, Good Sudoku.
- **Combines well with:** `nonogram`, daily challenges and streaks (`references/08-time-energy-session-mechanics.md`), leaderboards (`references/06-social-competitive-mechanics.md`).

### 03.18 Word formation — `word-formation`

- **ID:** `word-formation` · **Category:** puzzle / word · **Player fantasy:** "My vocabulary is my superpower."
- **Core rules:** four families share one verb (form a valid word from available letters):
  - **Letter wheel crossword:** a wheel of 4–8 letters; swipe to connect letters into words that fill a fixed crossword; bonus words count toward rewards.
  - **Guess-the-word deduction:** guess a hidden word (e.g., 5 letters, 6 tries); feedback per letter: correct place, wrong place, absent.
  - **Grid word search / connect:** find words by connecting adjacent letters (Boggle-like) or straight lines (word search).
  - **Tile placement:** place letter tiles on a board with scoring multipliers (Scrabble-like), often asynchronous PvP.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Letter count | 4–8 (wheel) | Search space |
| Word length | 3–8 | Difficulty |
| Dictionary size / obscurity | common-word list vs full | Accessibility |
| Hints | reveal letter, reveal word | Recovery |
| Guess count (deduction) | 5–7 | Difficulty |

- **Dynamics:** recall and anagramming; daily shared puzzles create social talk; bonus-word hunting for completionists.
- **Aesthetics (MDA):** Challenge, Discovery, Fellowship (shared daily).
- **Feedback and juice:** letter connection lines, word flies into the crossword, distinctive chime per word length, celebratory full-board fill.
- **Failure modes and exploits:** obscure or offensive words (curated answer lists separate from the accept list); localisation is a whole new content set per language, not a translation; cheating via solver websites in competitive modes.
- **Mobile fit:** swipe-connect one-hand; levels 1–3 min; strong with older audiences.
- **Monetization hooks and ethical limit:** hints (coins), ad-supported level flow, themes; keep hint pricing reasonable relative to coin income.
- **Implementation notes:** dictionary as a trie or DAWG for prefix pruning; generate wheel levels by choosing a seed word, enumerating sub-anagrams from the curated list, then laying out a crossword with a backtracking placer.
- **Reference games:** Wordscapes, Wordle (NYT), Words With Friends, Word Cookies.
- **Combines well with:** daily puzzles and streaks (`references/08-time-energy-session-mechanics.md`), async PvP (`references/06-social-competitive-mechanics.md`), narrative wrappers.

## 8. Perception

### 03.19 Hidden object — `hidden-object`

- **ID:** `hidden-object` · **Category:** puzzle / perception · **Player fantasy:** "Sharp eyes — nothing escapes me, and every scene tells a story."
- **Core rules:**
  - A dense illustrated scene and a list of `n` items to find (shown as words, silhouettes, or pictures). Tap an item → found; it is removed from the list.
  - Mis-taps: rapid random tapping is penalised (temporary input lock, time loss, or score reduction).
  - Hints recharge over time or cost currency; scenes repeat with shuffled item sets and modes (silhouette, night/dark with flashlight, word riddles, mirrored scene).
  - Levels are often embedded in a narrative and a meta (renovation, investigation).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Items per round | 6–15 | Duration |
| Item size on screen | ≥ 24–32 dp tap target | Fairness on phones |
| Camouflage level | colour/shape blending | Difficulty |
| Mis-tap penalty | 3–5 rapid misses → 2–5 s lock | Anti-spam |
| Hint recharge | 30–120 s | Forgiveness |
| Scene reuse | same scene 5–20 times, shuffled | Content cost control |

- **Dynamics:** visual search and memory of scenes; mastery of a scene through replays; narrative curiosity drives continuation.
- **Aesthetics (MDA):** Discovery, Narrative, Submission.
- **Feedback and juice:** found item sparkles and flies to the list, list item strikes through, combo bonus for quick finds, zoom and pan with pinch.
- **Failure modes and exploits:** items smaller than a fingertip; unfair camouflage (use a VLM or human check for each item's findability); spam tapping (penalty); asset cost — each scene is expensive (AI pipelines change this; see `ai-asset-pipeline`).
- **Mobile fit:** pinch zoom needed on phones (two-handed for zoom); sessions 2–5 min; tablets excel.
- **Monetization hooks and ethical limit:** energy per scene, hints, story chapters; keep energy generous enough for a satisfying session.
- **Implementation notes:** each item has a polygon hit mask (not a bounding box); per-item metadata: `{id, name, mask, difficulty, variants}`. Validate masks automatically (non-overlapping, minimum area at target resolution).
- **Reference games:** June's Journey, Hidden City, Hidden Folks (hand-drawn, list-free variant).
- **Combines well with:** `spot-the-difference`, narrative chapters (`references/10-narrative-exploration-mechanics.md`), energy (`references/04-economy-resource-mechanics.md`).

### 03.20 Spot-the-difference — `spot-the-difference`

- **ID:** `spot-the-difference` · **Category:** puzzle / perception · **Player fantasy:** "My eye catches what others miss."
- **Core rules:**
  - Two near-identical images side by side (or stacked in portrait). There are `n` differences (added, removed, recoloured, moved, resized objects).
  - Tap a difference on either image → both mark it. Mis-taps cost time or a life. Timer or lives limit the round.
  - Hints point out one difference; zoom aids small screens.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Differences per image | 3–10 | Duration |
| Difference size | ≥ 2 % of image area (easy) → < 0.5 % (hard) | Primary difficulty |
| Difference type mix | colour (easy), removal (medium), subtle shift (hard) | Variety |
| Timer | 60–180 s or none | Pressure |
| Mis-tap penalty | −5 to −10 s or −1 life | Anti-spam |

- **Dynamics:** systematic scanning (quadrants) vs gestalt; relaxed pace without timer.
- **Aesthetics (MDA):** Discovery, Submission.
- **Feedback and juice:** circle drawn on both images, chime, counter, final reveal of any missed differences.
- **Failure modes and exploits:** accidental differences from image editing (compression artefacts, regenerated details) — generate the diff mask from pixel comparison and check it matches the intended list exactly; differences in areas covered by UI or notch.
- **Mobile fit:** portrait stacked images halve size — prefer swipe-to-toggle or flicker mode as an accessibility option; sessions 1–3 min.
- **Monetization hooks and ethical limit:** hints, ads between rounds, themed packs.
- **Implementation notes:** store differences as masks; tap hit-test with a tolerance radius (8–16 dp); automated pipeline: base image → targeted edits → pixel diff → cluster → compare with intended edit list → reject on mismatch.
- **Reference games:** a long-standing print puzzle format; mobile titles are numerous and interchangeable (check current charts for leaders); HO games such as June's Journey include perception modes.
- **Combines well with:** `hidden-object`, daily challenges (`references/08-time-energy-session-mechanics.md`), collection albums (`references/09-collection-crafting-building.md`).

## 9. Physical and geometric

### 03.21 Physics puzzles — `physics-puzzle`

- **ID:** `physics-puzzle` · **Category:** puzzle / physical · **Player fantasy:** "I set things in motion and the world solves itself — because I understood it."
- **Core rules:**
  - A physics simulation with a goal condition (deliver object A to region B; destroy all targets; keep object C intact).
  - Player actions alter the simulation: cut ropes, remove/place objects, dig terrain, draw shapes, tap to trigger, set timing.
  - Star objectives: optional collectibles along the ideal path, minimal actions, or time.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Actions available | 1–6 | Search space |
| Timing sensitivity | none (static) – tight (moving parts) | Dexterity vs pure thought |
| Solution tolerance | wide region vs exact | Fairness under physics variance |
| Star collectibles | 3 per level | Mastery layer |
| New element cadence | every 10–25 levels | Novelty |

- **Dynamics:** hypothesis → test → refine loop; spectacle of chain reactions; multiple valid solutions.
- **Aesthetics (MDA):** Discovery, Sensation, Challenge.
- **Feedback and juice:** anticipatory character reactions, slow-motion near success, star pickups with escalating chimes.
- **Failure modes and exploits:** non-determinism (identical input → different result); exploits via physics glitches (tunnelling, jitter launches); levels solvable by unintended brute force.
- **Mobile fit:** taps/cuts/drawing; 30–120 s levels.
- **Monetization hooks and ethical limit:** hints (show solution path), skips, episode packs; premium has worked well for this genre historically.
- **Implementation notes:** fixed timestep, deterministic solver settings, no frame-dependent logic; store a reference solution per level as an input script and replay it headless in CI as the playthrough gate (see `qa-testing`).
- **Reference games:** Cut the Rope, Where's My Water?, Angry Birds, Brain It On!.
- **Combines well with:** `pin-pull`, `draw-a-path` and `slingshot-aim-release` (`references/01-verbs-movement-physics.md`), star-based level meta (`references/05-progression-meta-mechanics.md`).

### 03.22 Rotation puzzles — `rotation-puzzle`

- **ID:** `rotation-puzzle` · **Category:** puzzle / geometric · **Player fantasy:** "A twist here, a turn there — and suddenly everything connects."
- **Core rules:**
  - **Tile-rotation:** a grid of tiles each with connectors on some sides; tapping rotates a tile 90° (or 60° on hex). Goal: all connectors matched (closed loops — ∞ Loop) or a path from source to sinks (pipe rotation).
  - **Structure rotation:** rotate a whole structure or part of it to change paths, creating impossible-geometry connections (Monument Valley).
  - **Ring rotation:** concentric rings rotate to align an image or symbols.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Grid size | 4×4 – 12×12 | Duration |
| Tile types | end, straight, corner, T, cross | Constraint strength |
| Locked tiles | 0–20 % | Anchors for deduction |
| Rotation step | 90° (square), 60° (hex) | Possibilities per tile |
| Unique solution | yes / no | Deduction vs exploration |

- **Dynamics:** constraint propagation from edges and fixed tiles; relaxing exploratory play in loose variants.
- **Aesthetics (MDA):** Submission (zen), Discovery, Challenge.
- **Feedback and juice:** connected segments light up, flow animation through completed pipes, final glow and colour shift.
- **Failure modes and exploits:** random tapping solves easy levels (fine for zen games; for logic games enforce uniqueness and size); tiny tiles on large grids.
- **Mobile fit:** tap-only; one hand; 30 s – 3 min levels.
- **Monetization hooks and ethical limit:** hints, themes, ad-supported progression.
- **Implementation notes:** generate by building a random spanning tree/loop set on the grid, converting to tile connector masks, then randomising rotations; solver uses arc consistency per tile (allowed rotations shrink as neighbours fix).
- **Reference games:** ∞ Loop (Infinity Loop), Monument Valley, pipe-rotation puzzle apps.
- **Combines well with:** `flow-connect`, `pinch-rotate` (`references/01-verbs-movement-physics.md`), exploration (`references/10-narrative-exploration-mechanics.md`).

### 03.23 Tangram and packing — `packing-puzzle`

- **ID:** `packing-puzzle` · **Category:** puzzle / geometric · **Player fantasy:** "Every piece has its place — and I found it."
- **Core rules:**
  - A target silhouette and a fixed set of pieces. Place (drag), rotate (tap or two-finger), and flip pieces so they exactly cover the silhouette without overlap.
  - Families: **tangram** (7 classic geometric pieces, free angles snapped to 45°), **polyomino packing** (e.g., 12 pentominoes into a 6×10 rectangle — 2,339 distinct solutions), **fill-the-shape block puzzles** on grids, **luggage/packing** themed variants.
  - Partial credit variants score coverage; strict variants require exact fit.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Piece count | 3–12 | Search space |
| Rotation / flip allowed | none / 90° / 45° / flip | Possibilities per piece |
| Number of solutions | 1 (hard) – many (easy) | Difficulty and satisfaction |
| Outline hints | full outline vs silhouette only | Difficulty |
| Snap tolerance | 0.3–0.5 cell or 5–10° | Precision forgiveness |

- **Dynamics:** spatial reasoning, trying "hard pieces first", recognising sub-shapes.
- **Aesthetics (MDA):** Challenge, Expression (in creative modes), Submission.
- **Feedback and juice:** snap clicks, outline fills in, final fill shimmer, piece shadow while dragging.
- **Failure modes and exploits:** rotation controls on touch (one tap = 90° is simplest); fiddly snapping; trivial levels with many solutions.
- **Mobile fit:** drag + tap rotate; one hand for grid variants.
- **Monetization hooks and ethical limit:** hints (place one piece), level packs.
- **Implementation notes:** grid packing is an exact-cover problem — Knuth's Algorithm X with Dancing Links (DLX) counts solutions efficiently; use it to accept only levels with the intended solution count. For free-angle tangrams, use polygon boolean operations (clipper libraries) with tolerance.
- **Reference games:** classic Tangram, Katamino (physical pentomino game), Block puzzle "fill the shape" apps.
- **Combines well with:** `block-placement`, `drag` and `pinch-rotate` (`references/01-verbs-movement-physics.md`), collection of shapes (`references/09-collection-crafting-building.md`).

## 10. Volatile facts (as of Oct 2026 — verify before relying)

- Block Blast! topped mobile game downloads in H1 2026; overall H1 2026 mobile game IAP was about $40B (−2 % YoY) with downloads down 12 %. Source: Sensor Tower data via [Mobilegamer.biz data digest](https://mobilegamer.biz/data-digest-sensor-towers-h1-analysis-hay-days-comeback-julys-top-games-big-krafton-numbers-and-more/).
- King has used human-like bots for Candy Crush level difficulty prediction since about 2018, applied across more than 1,000 levels; later work reports difficulty estimates in under a minute versus days of human playtesting per episode. Sources: [Gudmundsson et al. 2018 (King)](https://www.Gwern.net/doc/reinforcement-learning/imitation-learning/2018-gudmundsson.pdf); [Politecnico di Milano thesis](https://www.politesi.polimi.it/handle/10589/141799).
- Puzzle and hybrid-casual are where automated bot and VLM testing works best today and where hybrid-casual spending grew (+17.1 % in 2025). Source: [Mobilegamer.biz](https://mobilegamer.biz/data-digest-sensor-towers-h1-analysis-hay-days-comeback-julys-top-games-big-krafton-numbers-and-more/).
