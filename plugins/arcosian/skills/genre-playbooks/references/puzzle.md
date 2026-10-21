# Puzzle Playbooks

Puzzle is the most mobile-native family of genres. It fits portrait, one thumb and 2-minute levels. It serves broad audiences, often older and female-skewing, and has the longest tails in mobile. It is also the family an agent pipeline handles best. State is discrete and deterministic. Levels can be generated and then checked by a solver or a bot. The art is small and easy to style-lock. This file covers twelve subgenres in the shared 14-part playbook format from `SKILL.md`. Match-3 and blast are IAP-led sagas with renovation metas. Merge-2 is an energy-and-orders economy game. Sort and jam, block, screw/pin, logic and solitaire games are ad-led, high-volume and generator-friendly. Word and trivia depend on their content. Hidden object is art-heavy. Physics puzzles depend on determinism. Two caveats apply throughout. KPI ranges appear only where a source exists, tagged `[Vn]` and listed at the end of this file. Team and time figures are labelled estimates.

## Contents

| # | Playbook | AB (1–5) | Lead monetization | Notes |
|---|---|---|---|---|
| 0 | Shared puzzle conventions | — | — | Difficulty model, solver gates, level pipeline |
| 1 | Match-3 (swap) | 5 | IAP | Saga + renovation meta |
| 2 | Blast / collapse | 5 | IAP | No invalid moves; spectacle |
| 3 | Merge-2 | 4 | IAP | Energy, generators, orders |
| 4 | Sort / jam | 5 | Ads | Water/ball, goods, hexa, vehicle jam |
| 5 | Block puzzle | 5 | Ads | Endless + adventure modes |
| 6 | Screw / pin puzzles | 3 | Ads | Physics presentation, discrete core |
| 7 | Word | 4 | Ads + hints IAP | Per-locale content |
| 8 | Trivia | 3 | Ads + IAP | Fact-checking pipeline |
| 9 | Solitaire / mahjong / tile-match | 5 | Ads + IAP | Older audience, solvable deals |
| 10 | Hidden object | 2 | IAP | Art-heavy scenes, narrative |
| 11 | Physics puzzle | 3 | Ads / premium | Determinism is the risk |
| 12 | Logic (nonogram, sudoku …) | 5 | Ads / premium | Unique-solution generators |
| 13 | Adjacent puzzle formats | — | — | Pointers |
| 14 | Volatile facts used in this file | — | — | Sources |

## 0. Shared puzzle conventions

- **Difficulty is a sawtooth.** Ramp difficulty over 5–10 levels, place a hard level, then drop back to a relief level. Introduce each new element as a teach level (trivial, obvious), then a test level, then a twist level that combines it with an earlier element. A reward level follows. Record this in `level-spec.teach`. Generate curves with `${CLAUDE_PLUGIN_ROOT}/scripts/difficulty_curve.py generate --pattern sawtooth`.
- **Targets are win rates, not feelings.** For each level store `difficulty_target.win_rate` and `attempts_p50`. Early levels should be close to unlosable. Later hard levels can be much lower. These are heuristics; recalibrate with `difficulty_curve.py analyze` on soft-launch data.
- **Every level has a machine verdict.** Grid swap games use bots (`match3_sim.py`, swap rules only; blast / collapse levels need their own simulator, see §2). Discrete puzzles use solvers (`puzzle_solver.py` for sort, sliding, sokoban and lights-out, or a purpose-built solver). LLM-generated levels fail often, and hard ones fail most. In one study, LLM-generated Snake levels were 87% playable at easy difficulty and only 36% at hard [V5]. Generate, verify, then reject or repair.
- **Bots are good enough to replace most difficulty playtests.** King's human-like bots predicted difficulty across more than 1,000 Candy Crush levels. Estimates now take under a minute, against 7 days of human testing per 15-level episode [V4]. With no player data, start with heuristic bots and recalibrate after soft launch.
- **The fail screen is the monetization moment** in IAP puzzles. It is also the churn moment. Show progress ("2 jellies left") and one clear offer. Never stack more than two offers.
- **Readability rules.** Use colour plus a shape or icon for every colour-coded element (colour-blind safety). Keep 6 or fewer simultaneous colours. Animations must be skippable after the first few views.

## 1. Match-3 (swap)

**Definition and player fantasy.** Swap two adjacent tiles to line up three or more of a colour on a grid, clearing goals within a move limit. The fantasy is "I saw the clever move", followed by a gravity cascade that pays out more than planned. It mixes mastery and luck in a cosy, low-stakes package. The meta fantasy is usually restoration: rebuild the mansion, the garden or the castle.

**Core loop** (seconds). Scan the board → swap → match → gravity refill → cascade → goal counters drop → repeat until goals are met or moves run out. A win pays stars and coins. A loss shows a "+5 moves" offer, then a retry.

**Meta loops.**
- A linear level map. Each win pays a meta currency (stars) spent on renovation or story tasks. This gives players a progress track that does not depend on skill.
- Lives (commonly 5, refilled on a timer) pace the number of sessions. Win streaks award pre-placed boosters.
- The wrapper: teams with life gifting, team tournaments, collection events across levels, a season or royal pass, and race events.

**Session profile** (estimate). 3–10 minutes per session, 3–6 sessions a day, 1–3 minutes per level. A session ends when lives run out or a meta task completes.

**Signature mechanics** (`mechanics-codex`: matching, cascade-gravity, collection, progression-unlocks).
- **Specials.** A 4-in-line makes a line clearer. An L or T makes a bomb. A 5-in-line makes a colour bomb. Special + special combos are the big moment. With N special types there are N(N+1)/2 pair combos, and each needs its own effect and test.
- **Layered obstacles.** Covers (ice, grass), blockers with HP (boxes), spreaders (chocolate), drop-items and conveyors. Each new obstacle goes through teach, test and twist.
- **Goals.** Collect N of a colour, clear all covers, drop items, or reach a score.
- **Difficulty levers, strongest first.** Colour count (4–6; each extra colour sharply cuts spontaneous matches and cascades), then move limit, obstacle density, board shape and holes, spawn bias.

| Parameter | Starting value to tune (heuristic) | Effect |
|---|---|---|
| Colours | 4 early, 5 mid, 6 for hard spikes | The strongest lever on cascade frequency and win rate |
| Moves | Bot median moves-to-win + 10–25% | Sets near-miss frequency; too generous kills fail-offer value |
| Board | 7×7 to 9×9, holes for shape | Smaller boards cascade less and read better on small phones |
| Obstacle density | 0–40% of cells | More density means more planning and slower pace |
| Spawn bias | Neutral; never per-player stealth rigging | Hidden manipulation erodes trust (`legal-ethics`) |

**Monetization model and typical mix.**
- IAP leads. Coins buy "+moves" on fail (the highest-intent moment), pre-level boosters and lives.
- Starter and personalized offers, plus a season pass.
- Rewarded ads are secondary. Top-grossing Western titles keep interstitials light or absent (qualitative).

**KPI expectations.** A secondary 2026 summary cites install-weighted benchmarks "as high as" 47% D1, 24% D7 and 13% D30 for top-grossing match-3 [V2]. The source is unnamed, so treat these as a ceiling, not a target. Beyond that, the picture is qualitative: the genre has a long tail where D30+, payer conversion and years of lifetime matter more than D1.

**Retention drivers.**
- Novelty cadence: a new obstacle or goal type every 10–20 levels, sequenced teach → test → twist.
- Story and renovation cliffhangers that end sessions on "one more task".
- Win-streak rewards that make the next first-try attempt feel valuable.
- Team membership: gifting lives, chat and team tournaments create obligation and belonging.
- Near-miss fails that show exactly how close the player was.

**Content pipeline and production scope** (estimates).
- Soft launch with 100–300 bot-verified levels. A live game adds levels on a regular cadence; King's cadence is 15-level episodes [V4].
- Tooling: a level editor that exports `level-spec` JSON, a `match3_sim.py` bot farm, and dashboards comparing bot win rates with live win rates.
- Team: a vertical slice takes 1–2 people plus agents, 3–6 weeks. A competitive soft launch takes 10–25 people, 12–18 months. Incumbents run far larger art and live-ops teams.

**Reference titles.** Bejeweled (PopCap), Candy Crush Saga (King), Homescapes and Gardenscapes (Playrix), Royal Match (Dream Games), Lily's Garden (Tactile Games).

**What makes it succeed / fail.**
- Succeeds: cascades and combos feel superb (game feel is the product).
- Succeeds: a meta with emotional pull, and a sawtooth difficulty tuned with data.
- Succeeds: a well-designed fail-screen offer and relentless live-ops.
- Fails: obstacles copied with no twist, or hard levels before habits form.
- Fails: slow animations, or outcomes that feel decided by spawns.
- Fails: installs cost far more than incumbents pay, so the game cannot buy scale.

**Innovation vectors.**
- Speed and polish. Royal Match is widely cited as having raised the bar on pacing and polish in a mature genre.
- Narrative and character-driven metas instead of generic renovation.
- Competitive event layers such as races and team battles.
- Hybrid metas (RPG battles, 4X bases) and personalized difficulty within ethical limits (`progression-difficulty`).

**Agent-buildability: 5/5.** The grid simulation is seeded and deterministic. Headless bots (`match3_sim.py`) produce win rates and attempts for every level. The tile art is small and style-lockable. The residual risks are animation polish, which needs a human taste checkpoint, and level volume, which needs a generator plus a bot pipeline.

**Starter feature list (P0 vertical slice).**
1. Board model and seeded RNG — grids up to 9×9 with holes; the same seed and inputs produce an identical state (unit-tested).
2. Swap and match resolution — only match-creating swaps are accepted; invalid swaps animate back within 0.25 s.
3. Gravity, refill and cascade — the board always settles with no standing matches; deadlocked boards auto-shuffle.
4. Specials and pair combos — three special types plus all pairwise combos, each covered by a unit test.
5. Goal system — collect, clear and drop goals with HUD counters; win when all are met, lose at 0 moves.
6. Two obstacles — one cover (ice) and one blocker (box, 1–2 HP), each with a teach level.
7. Level loader — 20 levels from `level-spec` JSON; each bot win rate is within ±10 points of its target over 500 runs.
8. Fail flow — the fail screen offers +5 moves for soft currency or a rewarded ad, shows the price clearly, and has one dismiss path.
9. Lives and map — 5 lives on a refill timer; a loss costs a life and a win does not; the map shows the next level.
10. Meta currency and one area — stars from wins buy 5 decoration tasks with visible before and after.
11. Juice pass — match pops, a cascade combo counter, shake of 4 px or less, haptics on specials; the visual gate passes.
12. Analytics — `level_start` and `level_end` (result, moves_left, boosters_used) per the event taxonomy.
13. Performance — p95 frame time ≤ 16.6 ms on the mid tier and ≤ 33.3 ms on the low tier during 5-step cascades.

## 2. Blast / collapse

**Definition and player fantasy.** Tap a group of two or more adjacent same-colour blocks to remove it. Big groups create specials such as rockets, bombs and colour balls. There are no invalid moves, only better and worse taps. The fantasy is instant gratification and spectacle: every tap does something, and big chain reactions feel earned through planning rather than precise pattern-finding.

**Core loop** (seconds). Scan → tap a group → collapse and refill → specials spawn → goal counters drop → repeat → win (stars, coins) or loss ("+5 moves" offer, then retry).

**Meta loops.** These match the match-3 saga: a level map, a decoration or story meta, lives, streaks, teams and events. Blast games lean harder on team features and competitive events because the core is faster and lighter.

**Session profile** (estimate). 3–10 minutes, 3–6 sessions a day. Levels average shorter than swap match-3.

**Signature mechanics** (`mechanics-codex`: matching, cascade-gravity, randomness-loot).
- **Group-size ladder.** For example, 5 makes a line rocket, 7 a bomb and 9 a colour clearer. Tune the thresholds per game; they set how much planning is rewarded.
- **Special combos.** Adjacent specials fire together when tapped, giving an N(N+1)/2 combo matrix as in match-3.
- **Idle hint.** After a few seconds without input, pulse the largest group (or a special-creating group) so new players learn group-building without a tutorial.
- **Obstacles.** Balloons popped by adjacent blasts, crates, cages and toys that must reach the bottom row.
- **Difficulty levers.** Colour count, the frequency of isolated single blocks (dead cells), move limit, obstacle density and the spawn bias towards large groups.

| Parameter | Starting value to tune (heuristic) | Effect |
|---|---|---|
| Colours | 4–5 | Fewer colours mean bigger natural groups and more specials |
| Special thresholds | 5 / 7 / 9 | Lower thresholds flatten the skill ceiling |
| Moves | Greedy-bot median + 15–30% | Greedy bots underplay; planners need less slack |
| Minimum group | 2 | Raising it to 3 adds dead cells and frustration |
| Refill bias | Neutral | Visible "lucky" refills are fine; hidden rigging is not |

Expected group size falls steeply as colour count rises. Measure it from 1,000 seeded boards per configuration rather than guessing.

**Monetization model and typical mix.** IAP-led and much like match-3: +moves on fail, boosters, lives, team-event passes and offers. Rewarded ads for small boosts.

**KPI expectations.** No sourced blast-specific benchmark. Qualitatively it behaves like match-3 sagas: long tails, with payer conversion and D30+ as the decisive metrics.

**Retention drivers.**
- Teams: chat, life gifting and help requests.
- Team tournaments and co-op events where each member's levels count.
- Collection events that span many levels.
- Decoration and story progress.
- Fresh obstacles on a steady cadence.

**Content pipeline and production scope** (estimates). Same as match-3, with a level editor, a bot farm and a regular level cadence. Bot design differs: a greedy bot taps the largest group, and a planner bot looks ahead one tap for specials. `match3_sim.py` cannot run blast levels. It implements swap rules only: a swap of two adjacent tiles that makes a run of 3 or more, run-based specials (4-run line clearer, L/T bomb, 5-run colour bomb), cascades with seeded refill, box and ice obstacles, and collect, clear and score goals, with `random`, `greedy` and `cascade` bots. It exits with `layout.type must be match3` for any other layout type, and it has no tap-a-group move, group-size special ladder, balloon or drop-to-the-bottom goal. The level-spec schema has no blast layout type either, so store blast boards as `layout.type: "custom"` (a `format` name plus a `data` payload) or as a `grid` with a legend. Write a project-owned, seeded simulator (flood-fill tap, collapse, refill, special ladder, goals) with greedy and one-tap-lookahead bots, and have it fill `solver.bot_win_rate` and `solver.runs`. Use `match3_sim.py --help` as the model for the command line and its JSON fields (`win_rate`, `moves_left`, `difficulty_band`). Team size matches match-3.

**Reference titles.** Toon Blast and Toy Blast (Peak), Pet Rescue Saga (King).

**What makes it succeed / fail.**
- Succeeds: blasts that are explosive and readable, and specials that feel generous.
- Succeeds: team play that is genuinely social, and fast pacing.
- Fails: boards that feel random ("nothing I do matters").
- Fails: blocks too small to tap accurately (keep each cell at least 44 pt on the smallest supported phone).
- Fails: a game indistinguishable from the leaders, with nothing to show in a 3-second ad.

**Innovation vectors.**
- Character-driven themes and IP-style mascots.
- Hybrid boards that add swap specials to tap boards.
- Team co-op goals and asynchronous team races.
- Faster meta-story beats between levels.

**Agent-buildability: 5/5.** The core is flood-fill on a grid, deterministic and trivial to bot-test. The art is small. The residual risk is the spectacle VFX, which needs a taste review. The score assumes the project writes its own blast simulator and bots, because the plugin's `match3_sim.py` does not cover blast rules (see the production-scope note above).

**Starter feature list (P0 vertical slice).**
1. Grid and flood-fill groups — taps on groups of 2 or more remove exactly the connected group (unit-tested on 20 fixtures).
2. Collapse and refill — columns settle deterministically for a given seed; there is no frame where a cell is floating.
3. Special ladder — three specials at configurable thresholds, spawning at the tapped cell.
4. Special combos — adjacent specials chain on tap; every pair combination is tested.
5. Dead-board detection — if no group of 2 or more exists, an auto-shuffle runs within 1 s.
6. Goals and moves — collect and drop goals; win and lose states and results screens.
7. Two obstacles — a balloon (adjacent pop) and a crate (2 HP), each with a teach level.
8. Bot verification — 20 levels within ±10 points of target win rate using the project's own blast simulator and greedy bot (500 runs); `match3_sim.py` cannot run blast levels.
9. Fail offer — +5 moves for coins or a rewarded ad; the decline path returns to the map.
10. Lives and map — 5 lives, a refill timer and map progression.
11. Juice — blast particles, a combo counter and haptics; VFX stays within the perf budget on the low tier.
12. Analytics — `level_start` and `level_end` with taps used, specials created and boosters.

## 3. Merge-2

**Definition and player fantasy.** Drag two identical items together to make one item of the next tier. Generators spawn tier-1 items at an energy cost. Orders ask for specific items, and filling them pays coins, XP and story progress. The fantasy is tidying up and discovery: clutter becomes treasure, players find out what sits at the top of each chain, and they restore a place while uncovering a story.

**Core loop** (seconds to minutes). Tap a generator (spends energy) → items spawn → merge up chains → fill an order → rewards → spend them on meta tasks → unlock new generators, chains and board areas.

**Meta loops.**
- Renovation or story tasks paid for with order rewards. Level-ups clear fogged board cells and add chains.
- Event boards with themed chains and separate currencies, plus collections and albums.
- Storage and inventory slots, generator upgrades, and daily orders.

**Session profile** (estimate). 5–15 minutes, gated by energy, 3–8 sessions a day. Tune so a full energy bar is roughly one satisfying session.

**Signature mechanics** (`mechanics-codex`: merging, generators-timers, economy-flow, spatial-packing, collection).
- **Merge rule.** 2→1 is standard. Merge Dragons! uses 3→1, with a bonus for merging 5.
- **Chains.** Typically 8–15 tiers per chain. Each tier needs a silhouette that reads at thumbnail size.
- **Board space is the core tension.** Energy is the brake. Bubbles (paid duplicates), scissors and wildcards relieve it.

| Parameter | Starting value to tune (heuristic) | Effect |
|---|---|---|
| Board | About 7×9 cells | Smaller boards raise space tension |
| Energy cap | About one session of play | A bigger cap means fewer, longer sessions |
| Regeneration | One full bar in a few hours | Sets the return cadence and notification timing |
| Generator upgrade yield | +5–15% higher-tier chance per upgrade | Lowers the energy cost of orders |
| Concurrent orders | 3–5 | More orders give more choice and more clutter |

- **Cost of an order.** With 2→1 merging, a tier-n item costs 2^(n−1) tier-1 items. If a generator yields a tier-2 item 15% of the time, it averages 0.85 × 1 + 0.15 × 2 = 1.15 tier-1 equivalents per energy. An order for one tier-6 item then costs about 32 / 1.15 ≈ 28 energy. Express every order's cost in energy and minutes of regeneration, then run `economy_sim.py` to check how many days the content lasts.

**Monetization model and typical mix.** IAP-led: energy refills and gem bundles, buying bubbles, extra storage, event passes and starter packs. Rewarded ads give small amounts of energy. Interstitials are rare in leading titles (qualitative).

**KPI expectations.** No sourced merge-specific benchmark. Qualitatively, D1 depends on how clear the first orders are and how fast the story hooks. Long-term value depends on events and payer depth.

**Retention drivers.**
- Story cliffhangers at the end of each task chain.
- "What is the next tier?" curiosity, helped by a visible chain codex with silhouettes.
- Energy-refill return loops, with opt-in notifications.
- Events with their own boards and collection completion.

**Content pipeline and production scope** (estimates).
- Asset volume is the cost: 20–40 chains × 8–15 tiers means hundreds of consistent item sprites, plus event chains every few weeks.
- This suits a style-locked image pipeline (`ai-asset-pipeline`), with human review of tier readability.
- Writing for the story meta is ongoing.
- Team: a slice takes 1–3 people plus agents, 4–8 weeks. Soft launch takes 6–15 people, 9–15 months.

**Reference titles.** Merge Dragons! (Gram Games), Merge Mansion (Metacore), EverMerge (Big Fish Games), Travel Town (Magmatic Games), Gossip Harbor.

**What makes it succeed / fail.**
- Succeeds: clear order goals and satisfying tier reveals.
- Succeeds: good space tension, a story with hooks, and generous early energy.
- Fails: a cluttered board with no relief valve, or energy starvation in the first sessions.
- Fails: chains whose tiers look alike, too many currencies, or an economy no one simulated.

**Innovation vectors.**
- Narrative-first merge built around mystery and drama.
- Merge fused with other cores (merge plus match, merge plus tycoon).
- Co-op orders and shared event boards.
- Lighter economies with fewer currencies, and shorter chains of more meaningful items.

**Agent-buildability: 4/5.** The simulation is discrete and deterministic. A greedy order-filling bot measures time-to-complete, and `economy_sim.py` checks energy flow. Points are lost for art volume and consistency across hundreds of items, and for story writing that needs human taste.

**Starter feature list (P0 vertical slice).**
1. Board grid and drag-merge — dragging onto an identical item merges to the next tier; a mismatched drop swaps or bounces back.
2. Chain data — 3 chains × 8 tiers defined in data; sprites load from the manifest; tier order is unit-tested.
3. Generators and energy — each tap costs 1 energy and spawns per a seeded drop table; at 0 energy, taps are blocked with an explanation.
4. Energy regeneration — +1 per configured interval up to the cap; offline time is credited using a guarded clock.
5. Orders board — 3 concurrent orders drawn from tier and chain rules; filling one pays coins and XP and removes the items.
6. Board space rules — full-board state detected; a storage slot (1) and a sell-for-coins action are available.
7. Fogged cells and level-up — XP level-ups unfog a region and add a chain; tested by a scripted playthrough.
8. Meta task list — 5 renovation tasks costing coins or stars; completion plays a before-and-after reveal.
9. Economy sim pass — `economy_sim.py` shows the slice content lasts the target days for each archetype.
10. Bubble or rewarded relief — a rewarded ad grants energy (daily cap); the offer appears only at energy 0.
11. Save and resume — every merge is persisted; killing the app mid-drag loses no items.
12. Analytics — `merge`, `order_complete` and `energy_depleted` events with tier and chain parameters.
13. Readability check — every tier is identifiable at 64 px in the visual-gate screenshot review.

## 4. Sort / jam

**Definition and player fantasy.** Rearrange coloured items into uniform containers under capacity rules. The family has four common forms:
- **Water and ball sort.** Pour the top layer onto a matching top layer or into an empty tube.
- **Goods (triple) sort.** Three identical goods on a shelf clear.
- **Hexa sort.** Stack hexagon piles; matching tops merge and clear at a threshold.
- **Vehicle jam.** Tap vehicles to drive out in the direction they face; passengers board the bus of their colour.

The fantasy is order out of chaos: calm, visible progress and a satisfying completion moment.

**Core loop** (seconds). Inspect → move an item → a container completes and clears → repeat → win when everything is sorted. A loss comes when the player is stuck, the holding slots fill, or (in some variants) a timer runs out.

**Meta loops.**
- Level progression with themed backgrounds and an optional light decoration or collection album.
- A daily challenge and streak.
- Unlockable container and background skins.

**Session profile** (estimate). Levels of 1–3 minutes, several per session, many short sessions a day. Commute and queue play.

**Signature mechanics** (`mechanics-codex`: sorting, deduction-constraint, spatial-packing).
- Capacity constraints and empty buffers are the whole design. Undo, "+1 tube" and "+1 slot" boosters relieve them.
- Hidden layers (question-mark items revealed when uncovered) add information uncertainty without adding hand dexterity.
- Locks, keys, frozen containers and conveyors are twist elements.

| Parameter (water sort) | Starting value to tune (heuristic) | Effect |
|---|---|---|
| Colours k | 3 early, up to 10–12 late | State space grows explosively with k |
| Capacity c | 4 | Larger c means longer solutions |
| Empty tubes e | 2; 1 for hard spikes | e = 1 removes most slack |
| Hidden layers | 0 early, 30–60% late | Adds risk; needs the solver to plan over expected outcomes, or reveal-safe levels |
| Minimum solution length | Rises across the curve | The main difficulty proxy from `puzzle_solver.py` |

**Monetization model and typical mix.**
- Ad-led: interstitials between levels after the first few, and rewarded ads for an extra tube, slot or undo.
- A no-ads IAP, plus small booster packs.
- Optional season pass in more developed versions.

**KPI expectations.** No sourced sort-specific benchmark. Qualitatively this is a casual, ad-led, high-volume category. Casual and hyper-casual games each took 40% of game ad revenue in Feb–Apr 2026 [V3]. Retention depends on difficulty pacing and ad load.

**Retention drivers.**
- Endless, fair levels; the solver guarantees every level can be won.
- Satisfying completion feedback (sound, haptics, particles).
- Daily challenge and streak.
- Visible progress counters and theme unlocks.

**Content pipeline and production scope** (estimates).
- Generate levels by shuffling from a solved state, then verify with `puzzle_solver.py --algo astar` (layout type `sort`).
- Reject unsolvable levels and levels whose minimum moves fall below the target band.
- Assets are tiny: a few container types, colour sets with shape markers, and backgrounds.
- Team: slice 1 person plus agents, 1–3 weeks; soft launch 2–5 people, 3–6 months.

**Reference titles.** Water Sort Puzzle and Ball Sort Puzzle style games; goods/triple sort games; Hexa Sort style games; Parking Jam 3D and bus-jam style games. Many publishers ship near-identical versions, so differentiation is the problem.

**What makes it succeed / fail.**
- Succeeds: crisp readability with colour plus shape, and fair, solver-verified levels.
- Succeeds: fast pour and slide animations, and a satisfying "container complete" moment.
- Fails: unsolvable or luck-gated levels, especially with hidden layers.
- Fails: colours that are hard to tell apart, too many ads, or being a clone with no hook.

**Innovation vectors.**
- New container physics (hexa stacking, 3D jams).
- Hybrid metas: collections, decoration, light narrative.
- Accessibility as a differentiator: colour-blind modes and a relaxing no-fail mode.
- Themed live events using the same generator with new constraints.

**Agent-buildability: 5/5.** State is discrete and solver-verifiable, the art is tiny, and timing does not matter. The only human checkpoint is the feel of the pour and slide animations.

**Starter feature list (P0 vertical slice).**
1. Container model — tubes with capacity and a top-of-stack rule; a move is legal only onto a matching top or an empty tube (unit-tested).
2. Pour and move animation — a move completes in 0.6 s or less and can be interrupted by the next tap.
3. Completion detection — a full single-colour container clears or locks, with feedback.
4. Win and stuck detection — a win when all are sorted; a "no legal moves" state shows the restart or booster offer.
5. Undo — at least 1 free undo per level; further undos via booster.
6. Level generator — shuffle from a solved state with seed, k, c and e parameters.
7. Solver gate — every shipped level is solvable per `puzzle_solver.py`; `min_moves` is stored in `level-spec`.
8. Difficulty curve — 30 levels follow a sawtooth over `min_moves` produced by `difficulty_curve.py`.
9. Colour-blind safety — every colour carries a distinct shape or pattern; the visual gate checks it.
10. Rewarded "+1 tube" — offered only when stuck, with a daily cap.
11. Interstitial policy — none before level 5; minimum interval from config; never mid-level.
12. Analytics — `level_end` with moves, undos and boosters, plus `stuck` events.

## 5. Block puzzle

**Definition and player fantasy.** Drag polyomino pieces onto a grid. Completing rows or columns clears them (and 3×3 regions in Woodoku-style games). The game ends when none of the offered pieces fit. The fantasy is calm spatial planning that tightens into tension near the end, and chasing a personal best.

**Core loop** (seconds). See three offered pieces → place each one → lines clear → combo and streak score → a new set of three → repeat until nothing fits → game over (rewarded revive offer) → restart.

**Meta loops.**
- Endless high-score mode with a personal best and weekly leagues.
- Adventure mode with goal levels, such as collecting gems embedded in blocks or clearing marked cells.
- Daily puzzles and themes or skins.

**Session profile** (estimate). Endless runs of 3–15 minutes; adventure levels of 1–3 minutes; many sessions a day.

**Signature mechanics** (`mechanics-codex`: spatial-packing, randomness-loot, progression-unlocks).
- **Grid.** 8×8 (Block Blast!-style), 9×9 with 3×3 regions (Woodoku), or 10×10 (1010!).
- **Piece generator fairness** is the central system. Use weighted random with a placeability check, so at least one offered piece fits until the difficulty drift intends otherwise. Use mercy weighting after long dry spells.
- **Scoring example.** `points = cells_placed + 10 × lines² + streak_bonus`. Simultaneous multi-line clears are the skill payoff.
- **Drag offset.** Render the piece 1–2 cm above the finger so the thumb never hides the target cells.

| Parameter | Starting value to tune (heuristic) | Effect |
|---|---|---|
| Piece set | 15–25 shapes, mono to 3×3 | Large pieces end runs; monos are mercy |
| Offer size | 3 | Fewer offers mean harder planning |
| Difficulty drift | Raise the big-piece weight with score | Controls run length |
| Placeability check | Always, or after a dry spell | Fairness versus tension |
| Revive | Clear a 3×3 area or offer small pieces | Rewarded-ad value |

**Monetization model and typical mix.**
- Ad-led: an interstitial on game over (with a minimum interval), a rewarded revive, and sometimes banners.
- A no-ads IAP, plus themes and skins.

**KPI expectations.** Block Blast! topped global downloads in H1 2026 [V1]. This is a scale signal for the format, not a retention benchmark. Retention is otherwise qualitative: a broad casual audience with daily-habit play.

**Retention drivers.**
- Personal-best chasing and near-miss game overs.
- Daily puzzles and streaks.
- Adventure goals that give the endless mode a sense of direction.
- Leagues and async tournaments.

**Content pipeline and production scope** (estimates).
- Content is mostly procedural. Adventure levels come from a generator plus a bot (a greedy placement bot measures goal-completion rate).
- Assets are minimal; themes are the main art spend.
- Team: slice 1 person plus agents, 1–3 weeks; soft launch 2–5 people, 3–6 months.

**Reference titles.** 1010! (Gram Games), Woodoku (Tripledot Studios), Block Blast!. Tetris is the ancestor, but falling-tetromino designs carry IP risk: a US court found a close clone infringed (Tetris Holding v. Xio Interactive, 2012). See `legal-ethics`.

**What makes it succeed / fail.**
- Succeeds: a generator that feels fair, and satisfying multi-line clears.
- Succeeds: a precise drag with offset, and a relaxed tempo.
- Fails: pieces hidden under the thumb, or obviously unfair offers.
- Fails: game-over ads every run, or copying Tetris trade dress.

**Innovation vectors.**
- Adventure goals and themed boards.
- Special blocks (bombs, colour clears) and gentle physics clears.
- Social leagues and daily seeded runs that everyone plays.
- Merge and block hybrids.

**Agent-buildability: 5/5.** The rules are discrete and fully headless. Bots measure run length and goal rates, and the art is minimal. The residual risk is drag feel on small screens, which needs device testing.

**Starter feature list (P0 vertical slice).**
1. Grid and piece model — 8×8 grid, 20 shapes; placement legality is unit-tested, including the edges.
2. Drag and drop with offset — the piece renders above the finger; a snap preview shows the target cells; an invalid drop returns the piece.
3. Line clear — full rows and columns clear simultaneously; the score follows the documented formula.
4. Offer generator — 3 pieces per round, seeded and weighted, with a placeability check flag.
5. Game over detection — when no offered piece fits, the game-over screen shows within 0.5 s.
6. Combo and streak — multi-line and consecutive-clear bonuses with distinct feedback.
7. Personal best and persistence — the best score survives an app kill; the current run resumes after an interruption.
8. Rewarded revive — once per run; a 3×3 clear or a small-pieces offer; the ad never auto-plays.
9. Interstitial policy — game over only, minimum interval from config, none in the first runs.
10. Bot balance — a greedy bot's median run length sits in the target band (1,000 seeded runs).
11. Juice — clear flash, particles and haptics; 60 fps on the mid tier during a 4-line clear.
12. Analytics — `run_end` (score, lines, pieces placed, revive used) and `ad_impression` with placement.

## 6. Screw / pin puzzles

**Definition and player fantasy.** Two related families.
- **Pin pull.** Pull pins in the right order so balls, liquids or treasure fall where they should while hazards (lava, enemies) go elsewhere.
- **Screw jam (nuts and bolts).** Tap coloured screws to move them into boxes of their colour. Free plates drop under physics. A small buffer holds screws whose box is not yet available.

The fantasy is the "aha" of a causal chain and the satisfaction of releasing things.

**Core loop** (seconds).
- Pin pull: read the level → pull a pin → physics plays out → success or fail → next level.
- Screw jam: tap a screw → it goes to an open box of its colour or to the buffer → a full box (commonly 3 screws) clears and the next colour box arrives → plates drop → win when all screws are cleared, loss when the buffer is full.

**Meta loops.** Level progression, light collections or decoration, daily levels, skins.

**Session profile** (estimate). Levels of 1–3 minutes; many short sessions.

**Signature mechanics** (`mechanics-codex`: physics, deduction-constraint, sorting).
- **Pin pull** relies on ordering and physics simulation, sometimes particle liquids. The level is a small causal graph.
- **Screw jam** relies on occlusion layers: plate A blocks screw S. Add buffer capacity, a queue of box colours and physics drops.
- The logic can be modelled discretely as a dependency graph (which screws are free given the removed plates). Physics then becomes presentation only. This is the key to verifying it.

| Parameter (screw jam) | Starting value to tune (heuristic) | Effect |
|---|---|---|
| Buffer slots | 4–6 | The main difficulty lever |
| Colours | 3–8 | More colours mean more buffer pressure |
| Layers | 2–6 | Deeper occlusion means more planning |
| Box queue visibility | Next 1–2 colours visible | More visibility rewards planning |
| Screws per box | 3 | Changing it reshapes the whole curve |

**Monetization model and typical mix.**
- Ad-led: interstitials between levels and rewarded "+1 slot" or "remove a screw".
- A no-ads IAP and booster packs.

**KPI expectations.** No sourced benchmark. Qualitatively it is a casual, ad-led category with fast creative cycles.

**Retention drivers.**
- Clever, fair levels with an "aha".
- Satisfying physics drops and sounds.
- Fresh twists (locked plates, chained screws, timers) every few levels.

**Content pipeline and production scope** (estimates).
- Screw jam: model levels as dependency graphs and verify with a search solver over removal orders, accounting for buffer capacity and the box queue. Physics must not change the logical outcome; freeze plates until they are fully free.
- Pin pull: validate with many seeded physics runs per level and require a 100% success rate for the intended order and a 0% success rate for wrong orders.
- Team: slice 1–2 people plus agents, 2–5 weeks; soft launch 3–6 people, 4–8 months.

**Reference titles.** "Pull the pin" style puzzles; screw-jam and "nuts and bolts" style games. Pin-pull puzzles became widely known through ad creatives for other genres before shipping as standalone games.

**What makes it succeed / fail.**
- Succeeds: deterministic outcomes, readable layers, and a visible box queue.
- Succeeds: satisfying release physics.
- Fails: physics that makes the same input give different results.
- Fails: ads promising a mode the game does not contain. Regulators such as the UK ASA have acted on unrepresentative game ads; check current rulings via `legal-ethics`.

**Innovation vectors.**
- 3D screw structures that the player rotates.
- Hybrid metas.
- Pin-pull as a mini-game mode inside larger games, now shipped for real.
- Tactile haptic design.

**Agent-buildability: 3/5.** The logical core is verifiable once it is modelled as a dependency graph. Points are lost because physics presentation needs determinism work (fixed timestep, frozen bodies), pin-pull liquid physics is costly to verify, and 3D layering adds asset and perf work.

**Starter feature list (P0 vertical slice).**
1. Dependency model — plates, screws and occlusion as data; "free screw" queries are unit-tested.
2. Tap-to-move — a free screw animates to its matching open box, otherwise to the buffer; a blocked screw wiggles.
3. Box queue — boxes of 3; a full box clears and the next colour enters; the next colour is visible.
4. Buffer and lose state — loss when the buffer is full and no box matches; the retry costs nothing.
5. Plate physics — plates drop only when all their screws are removed; the drop never alters logical state.
6. Solver gate — 30 levels proven solvable, with the minimum buffer use recorded in `level-spec.solver`.
7. Difficulty curve — buffer pressure follows a sawtooth across the 30 levels.
8. Rewarded "+1 slot" — offered at the loss point, once per level.
9. Determinism test — a scripted playthrough gives an identical result over 100 seeded runs on the same build.
10. Juice — unscrew rotation, a clink on box entry and a satisfying plate fall within the perf budget.
11. Analytics — `level_end` (result, buffer peak, boosters) and `stuck` events.

## 7. Word

**Definition and player fantasy.** Form words from letters under a structure. Common forms:
- **Crossword-connect.** Swipe letters on a wheel to fill a small crossword.
- **Word search, anagram and daily word-guess** (Wordle-style).
- **Asynchronous board play** (Scrabble-like).

The fantasy is feeling sharp and articulate: a relaxing brain workout with pride in vocabulary.

**Core loop** (seconds). Read the wheel and the empty slots → swipe a word → it fills a slot if it is an answer, or banks a bonus coin if it is a valid extra word → complete the grid → coins → next level.

**Meta loops.**
- Level packs with scenic backgrounds and travel themes.
- Daily puzzles with a streak calendar.
- Tournaments and leagues.
- A piggy bank of bonus-word coins that can be bought out (monetization).
- Asynchronous friend matches (board variants).

**Session profile** (estimate). 5–15 minutes, 2–4 sessions a day. Daily-ritual play suits morning and evening.

**Signature mechanics** (`mechanics-codex`: word-language, deduction-constraint, progression-unlocks).
- **Dictionaries.** An answer list of common, inoffensive words and a larger valid-bonus list. Profanity and slur filters apply per locale.
- **Hints.** Reveal a letter, reveal a word, shuffle.
- **Level generation.** Pick a root word of 5–7 letters, find its sub-anagrams in the answer list, then lay out a crossword with a constraint solver (maximize intersections, keep it connected).

| Parameter | Starting value to tune (heuristic) | Effect |
|---|---|---|
| Root length | 3–4 early, 6–7 late | Longer roots mean more words and longer levels |
| Words per level | 3 early, 6–12 late | Level duration |
| Answer frequency band | Most common words early | Obscure words feel unfair |
| Hint cost | About one level's coins | Pace of the hint economy |
| Bonus-word payout | Small, piggy-banked | Rewards vocabulary; feeds an IAP offer |

**Monetization model and typical mix.**
- Ads: interstitials between levels and rewarded hints.
- IAP: coins for hints, piggy bank, no-ads.
- Some daily word games use a subscription or are bundled into a news or games subscription; Wordle sits in The New York Times' games offering.

**KPI expectations.** No sourced word-specific range. One 2026 summary says board, card, puzzle and idle games often match or beat RPG-level D7 and D30 [V2]. That supports a long tail, qualitatively.

**Retention drivers.**
- Daily puzzle and streak.
- Calm progression through beautiful themes.
- Bonus-word discovery.
- Leagues.
- Social sharing of daily results, where it applies.

**Content pipeline and production scope** (estimates).
- The generator plus validator covers thousands of levels per locale.
- The real cost is per-language curation of answer lists, offensive-word review and cultural fit. Native-speaker review is needed for each locale.
- Check dictionary licences: open word lists exist, but tournament dictionaries are licensed.
- Team: slice 1 person plus agents, 2–4 weeks; soft launch 2–6 people, 4–8 months, plus about 1 linguist per extra locale.

**Reference titles.** Wordscapes (PeopleFun), Words of Wonders, Words With Friends (Zynga), Wordle (The New York Times).

**What makes it succeed / fail.**
- Succeeds: a fair answer list, a calm aesthetic and large readable letters.
- Succeeds: a satisfying swipe trail, and a daily ritual.
- Fails: obscure or offensive words, and tiny letters on small phones.
- Fails: machine-translated locales, or ads interrupting a flow state.

**Innovation vectors.**
- Word plus narrative metas.
- Cooperative daily puzzles.
- Learning-language crossovers (`narrative-rhythm-edu-kids.md`).
- Accessibility: dyslexia-friendly fonts and audio pronunciation.

**Agent-buildability: 4/5.** Generation and validation are exact and the art is light. A point is lost for locale curation, offensive-word review and taste in word choice, all of which need humans.

**Starter feature list (P0 vertical slice).**
1. Dictionary service — answer and bonus lists loaded per locale; lookups under 1 ms; profanity filter tests pass.
2. Letter wheel input — swipe through letters with a visible trail; release submits; supports 3–7 letters.
3. Crossword grid — words fill their slots with animation; a level completes when all slots are filled.
4. Level generator — root word to answers to crossword layout; every layout is connected (validator).
5. 40 levels — generated and checked: no duplicate answers, every word in the answer list.
6. Bonus words — valid non-answer words pay into the piggy bank and are not counted twice.
7. Hints — reveal letter and shuffle, with a coin cost and clear feedback.
8. Coins and level rewards — balanced so a hint is affordable about every N levels (economy sim).
9. Daily puzzle — one per local day; streak tracked; resets at local midnight.
10. Accessibility — letters ≥ 24 pt on the smallest phone; high-contrast theme.
11. Interstitial policy — none before level 6; minimum interval; never during a level.
12. Analytics — `level_end` (time, hints, bonus words) and `daily_complete`.

## 8. Trivia

**Definition and player fantasy.** Answer knowledge questions under time pressure, often against friends or strangers asynchronously. The fantasy is proving what you know, social bragging rights and learning something along the way.

**Core loop** (seconds). Pick or spin a category → answer a timed multiple-choice question → right or wrong feedback → score or crowns → round end → asynchronous turn passes to the opponent.

**Meta loops.**
- Category crowns and collections, levels and leagues.
- Themed events (sport seasons, film releases).
- User-submitted questions with community review; Trivia Crack's question factory is a well-known example.

**Session profile** (estimate). 3–10 minutes; several sessions a day, driven by turn notifications in asynchronous PvP.

**Signature mechanics** (`mechanics-codex`: knowledge, competition, randomness-loot).
- Timer per question (10–20 s); power-ups such as "remove two options" or "extra time".
- An Elo-style or difficulty-tiered question selection that matches question difficulty to the player.
- Category spinner for variety; streak multipliers.

| Parameter | Starting value to tune (heuristic) | Effect |
|---|---|---|
| Question bank per locale | Thousands at launch | Repetition is the top churn cause in trivia |
| Target correct rate | About 60–75% | Too hard feels humiliating, too easy feels boring |
| Timer | 10–20 s | Accessibility versus tension |
| Repeat window | No repeats within N weeks for a player | Needs per-player tracking |
| Expiry tags | Date-sensitive questions expire | Stops stale facts |

**Monetization model and typical mix.** Ads (interstitials between rounds, rewarded extra lives or power-ups), IAP for lives, power-ups, cosmetics and no-ads, and sometimes a subscription.

**KPI expectations.** No sourced benchmark. Qualitatively, asynchronous PvP trivia retains through friend graphs, while solo trivia retains like casual puzzles.

**Retention drivers.**
- Friend turns waiting (asynchronous obligation).
- Leagues and events.
- Collection of category crowns.
- Fresh, topical questions.

**Content pipeline and production scope** (estimates).
- **The content is the product, and accuracy is the risk.** LLM-generated questions hallucinate. Required pipeline:
  1. Generate each question with a cited source.
  2. A second, independent model verifies the answer against the source.
  3. A human spot-checks a sample (start at about 10% and raise it if errors appear).
  4. Players can report errors in-app, and reported questions are pulled automatically.
- Localize culturally, not just linguistically.
- Team: slice 1 person plus agents, 2–4 weeks; soft launch 3–8 people including editors, 4–9 months.

**Reference titles.** Trivia Crack (Etermax), Kahoot! (education crossover), QuizUp and HQ Trivia as historical examples of social and live-show formats that did not last.

**What makes it succeed / fail.**
- Succeeds: accurate, varied, well-tuned questions, and social rivalry.
- Succeeds: fast rounds, and good answer feedback with a "learn more" link.
- Fails: wrong answers, which destroy trust, and repeated questions.
- Fails: culturally narrow banks, and cheating in PvP (answer lookup) without question-time limits.

**Innovation vectors.**
- AI-assisted question generation with verification pipelines.
- Personal-interest packs.
- Live events and co-op team quizzes.
- Educational crossovers.

**Agent-buildability: 3/5.** The app and game rules are easy and verifiable. Points are lost because factual correctness cannot be verified as reliably as a puzzle solution, and quality depends on editorial judgment.

**Starter feature list (P0 vertical slice).**
1. Question schema — id, locale, category, difficulty, answers, correct index, source URL, expiry date, status.
2. Question bank — at least 500 questions in one locale, each with a source and a second-model verification flag.
3. Round flow — 5 questions per round, a timer per question and correct or wrong feedback within 0.3 s.
4. Category spinner — weighted selection that avoids three of the same category in a row.
5. Difficulty matching — question difficulty adapts to keep the player's correct rate in the target band (simulated test).
6. Async PvP vs bot — turn-based match against a bot with a configurable skill; the friend flow is stubbed.
7. Repeat suppression — no repeat question for a player within the configured window (unit-tested).
8. Report-a-question — one-tap report; a question with N reports is auto-disabled.
9. Power-up — "remove two" with a coin cost, never removing the correct answer (tested).
10. Results and crowns — a round summary and a category crown collection.
11. Analytics — `question_answered` (category, difficulty, correct, time) and `question_reported`.

## 9. Solitaire / mahjong / tile-match

**Definition and player fantasy.** Familiar card and tile games moved onto phones.
- **Classic solitaire:** Klondike, Spider, FreeCell.
- **Level-based TriPeaks:** clear the peaks with run-building, boosters and goals.
- **Mahjong solitaire:** match pairs of free tiles.
- **Tile-match (triple):** tap tiles into a tray of about 7 slots; three identical tiles clear; a full tray loses. Match 3D does the same with 3D objects.

The fantasy is calm mastery of a classic, a feeling of keeping sharp, and nostalgia.

**Core loop** (seconds). Scan the layout → choose a legal move (play a card, match a pair, send a tile to the tray) → clear progress → repeat → win (cleared) or loss (stuck or tray full) → booster or retry.

**Meta loops.**
- Classic: daily challenges, trophies, statistics, themes and card backs.
- Level saga: a map, stars, collections and a farming, travel or decoration meta (Solitaire Grand Harvest pairs TriPeaks with farming).
- Tile-match: level progression, album collections and events.

**Session profile** (estimate). 5–20 minutes. Older audiences play longer, steadier sessions, often at fixed times of day.

**Signature mechanics** (`mechanics-codex`: matching, deduction-constraint, randomness-loot, collection).
- **Deal solvability.** Generate by reverse-play from a solved state, or check with a solver, and offer a "winnable deals only" option. Not every random Klondike deal can be won.
- **Mahjong free-tile rule.** A tile is free if no tile is on top of it and its left or right side is open. Generate layouts by placing pairs in reverse so that every deal can be solved.
- **Tile-match tray.** Slot count and tile-type count set difficulty. Undo, shuffle and "pull out 3" boosters relieve pressure.
- Undo, hint and auto-complete are expected quality-of-life features.

| Parameter | Starting value to tune (heuristic) | Effect |
|---|---|---|
| Tray slots (tile-match) | 7 | One fewer slot is a large difficulty jump |
| Tile types per level | 8 early, 20+ late | Visual search load |
| Layers (mahjong, tile-match) | 2–6 | Planning depth and occlusion |
| TriPeaks draw pile | Tuned so bots need about 0–2 boosters on hard levels | Fail-offer value |
| Hint delay | 8–15 s of inactivity | Helps without nagging |

**Monetization model and typical mix.**
- Classic: ads (interstitials between deals, rewarded hints or undos), no-ads, themes.
- Level modes: IAP for boosters, "+5 cards" on fail, passes and offers.

**KPI expectations.** No sourced range. The 2026 summary that groups card and puzzle with genres matching or beating RPG D7/D30 is qualitative [V2]. Expect a long tail.

**Retention drivers.**
- Daily challenge medals and streaks.
- Lifetime statistics (win rate, best times).
- Collection albums and meta-building in level modes.
- Habit and ritual play.

**Content pipeline and production scope** (estimates).
- Classic modes need almost no content.
- Level modes need a generator plus a solver-verified level set and events.
- Card and tile art is small but must be very legible.
- Team: slice 1 person plus agents, 1–3 weeks for classic, 3–6 weeks for a level saga; soft launch 3–10 people, 4–12 months.

**Reference titles.** Microsoft Solitaire Collection (Microsoft), Solitaire Grand Harvest (Supertreat), Vita Mahjong, Zen Match and Tile Busters-style tile-match games, Match 3D.

**What makes it succeed / fail.**
- Succeeds: legibility (large cards and tiles, high contrast), and solvable deals.
- Succeeds: relaxed pacing, and respect for an older audience (no aggressive pop-ups).
- Fails: unwinnable levels presented as fair, tiny tiles, and ad overload.
- Fails: a dark-pattern booster push at every fail.

**Innovation vectors.**
- Meta fusions (farming, travel, story).
- Accessibility-first design: senior-friendly UI, left-handed mode, large-print mode.
- Social clubs and calm co-op events.
- 3D tile-match variants.

**Agent-buildability: 5/5.** The rules are discrete and solvers are well understood. Reverse-generation guarantees that levels can be solved, and the art is small. Little depends on feel.

**Starter feature list (P0 vertical slice).** Example: a tile-match mode.
1. Layout model — layered tiles with a "selectable" rule (not covered); unit tests across 10 fixtures.
2. Tap-to-tray — a selectable tile moves to the tray, which auto-sorts same types together; three identical tiles clear.
3. Win and lose — a win when the board is cleared; a loss when the tray is full without a triple; results screen.
4. Reverse generator — places triples in reverse so every level can be solved; seed stored in `level-spec`.
5. Solver gate — 30 levels verified solvable with a 7-slot tray; the minimum boosters needed is 0 for all non-hard levels.
6. Boosters — undo, shuffle and "pull out 3", each with a clear cost and an effect test.
7. Difficulty curve — tile types and layers follow a sawtooth across 30 levels.
8. Legibility — tiles ≥ 48 pt on the smallest phone; distinct icons; the colour-blind check passes.
9. Fail offer — "+1 slot" or "pull out 3" for coins or a rewarded ad, shown once.
10. Daily challenge — a seeded daily layout, a calendar and medals.
11. Analytics — `level_end` (result, boosters, tray peak) and `daily_complete`.

## 10. Hidden object

**Definition and player fantasy.** Find listed objects hidden in detailed illustrated scenes, against time or for score, inside a mystery or adventure story. The fantasy is being a sharp-eyed detective or explorer uncovering a narrative.

**Core loop** (seconds to minutes). Enter a scene (costs energy) → find N listed objects → combo bonus for fast finds, penalty for random tapping → scene complete → coins, XP and collection items → story progress.

**Meta loops.**
- Story chapters unlocked by scene mastery.
- Scene modes that reuse the same art in new ways: silhouettes, night or flashlight, anagram lists, mirrored, word-to-picture.
- Collections, an estate or decoration meta (June's Journey), clubs and events.

**Session profile** (estimate). 5–15 minutes, gated by energy, 2–5 sessions a day.

**Signature mechanics** (`mechanics-codex`: search-observation, narrative-choice, collection, generators-timers).
- **Object lists and hitboxes.** Each object needs a precise polygon hitbox. Tap tolerance is about 8–12 pt beyond the silhouette.
- **Anti-spam.** Rapid random taps trigger a time penalty or a cooldown.
- **Hints.** A magnifier or highlight, earned or bought.
- **Mastery.** Repeating a scene raises its level, which shortens the timer and adds modes, so art is amortized across many plays.

| Parameter | Starting value to tune (heuristic) | Effect |
|---|---|---|
| Objects per round | 8–15 | Round length |
| Hideable objects per scene | Several times the per-round list | Variety on replay |
| Timer | Generous early, tighter with mastery | Pressure curve |
| Energy per scene | About 1/6 to 1/10 of the cap | Sessions per day |
| Hint regeneration | Slow, plus purchasable | IAP lever |

**Monetization model and typical mix.** IAP-led: energy, hints, chapter unlocks, decoration bundles and event passes. Light rewarded ads.

**KPI expectations.** No sourced range. Qualitatively, an older audience with story-driven retention and monetization through energy.

**Retention drivers.**
- Story cliffhangers.
- Scene-mastery progress.
- Collections and albums.
- Club events and new chapters.

**Content pipeline and production scope** (estimates).
- **Art is the cost.** Each scene is a dense, consistent illustration with dozens of separable, recognizable objects, each with a hitbox and a localized name.
- AI generation helps with base painting, but placement, recognizability, avoiding duplicates and ambiguous objects, and style consistency all need art direction and human review (`ai-asset-pipeline`, `art-direction`).
- Narrative writing is ongoing.
- Team: slice 2–3 people plus agents, 6–10 weeks; soft launch 10–25 people, 12–18 months.

**Reference titles.** June's Journey (Wooga), Hidden City (G5 Entertainment), Seekers Notes (MyTona), Hidden Folks (premium; Adriaan de Jongh and Sylvain Tegroeg).

**What makes it succeed / fail.**
- Succeeds: beautiful, coherent, fair scenes where objects are findable but not obvious.
- Succeeds: a compelling story, and generous scene reuse.
- Fails: objects that are unrecognizable or ambiguous (two "keys"), and hitboxes that are too tight.
- Fails: visible inconsistency in generated art, and energy that is too stingy.

**Innovation vectors.**
- Premium hand-drawn interactive scenes (the Hidden Folks direction).
- Detective-deduction hybrids.
- Co-op scene races.
- Accessibility zoom modes.

**Agent-buildability: 2/5.** The code is simple. Content is heavy and judged by taste: scene composition, object recognizability, hitbox authoring and visual verification all need humans. VLM checks help with triage but are unreliable as a gate [V6].

**Starter feature list (P0 vertical slice).**
1. Scene renderer — a high-resolution scene with pinch-zoom (1×–3×) and pan; 60 fps on the mid tier.
2. Object registry — per-scene JSON of objects (id, name key, polygon hitbox); validator checks hitboxes against the image bounds.
3. Find interaction — a tap inside a hitbox plus tolerance marks the item found with feedback; the list updates.
4. Anti-spam penalty — more than N wrong taps in T seconds applies a time penalty, with clear feedback.
5. Round generator — picks 10 objects from the scene's pool with no recent repeats (seeded).
6. Timer and scoring — combo for quick finds; results screen with stars.
7. Hint — highlights one remaining object; costs a hint charge.
8. Energy — a scene costs energy; regeneration timer; out-of-energy offer.
9. Two scenes × two modes — normal and silhouette modes for each scene.
10. Story beat — completing scenes unlocks a dialogue panel and the next chapter node.
11. Art review gate — each scene passes an object-recognizability review by a human checkpoint and VLM triage.
12. Analytics — `scene_end` (time, wrong taps, hints, mode) and `energy_depleted`.

## 11. Physics puzzle

**Definition and player fantasy.** Solve levels by acting on a simulated physical world. The main forms:
- Cut ropes and release objects (Cut the Rope).
- Launch projectiles (Angry Birds).
- Route fluids (Where's My Water?).
- Draw shapes that become physical objects (Happy Glass).
- Build contraptions (World of Goo).

The fantasy is playful experimentation and the delight of a causal chain that works.

**Core loop** (seconds). Observe → act (cut, launch, draw, place) → the simulation runs → evaluate (stars or goal) → retry or next level.

**Meta loops.** Level packs or worlds with star gates, collectibles, cosmetic skins and daily challenges.

**Session profile** (estimate). 2–10 minutes, levels of 30–120 seconds, high retry counts.

**Signature mechanics** (`mechanics-codex`: physics, path-drawing, aiming-trajectory, deduction-constraint).
- **Determinism.** Physics engines are generally not bit-identical across devices and frame rates. Use a fixed timestep, fixed iteration counts and deterministic seeding. For the core, consider a simpler custom simulation. Never let a variable frame rate change outcomes.
- **Star criteria.** Collect items, use fewer actions, finish faster. Stars give experts depth while novices can still pass.
- **Multiple solutions** are a feature. Verify that at least one solution exists and estimate the size of the solution space.

| Parameter | Starting value to tune (heuristic) | Effect |
|---|---|---|
| Physics step | Fixed (for example 60 Hz) with fixed iterations | Reproducibility |
| Solution-space ratio | Share of sampled actions that succeed | A difficulty proxy; lower is harder |
| Retry cost | Instant (under 1 s) | High-retry genres die on slow restarts |
| Ink or launch budget | Tuned per level | Constraint depth |
| Tolerance | Generous contact thresholds | Fairness on low-end devices |

**Monetization model and typical mix.** Historically premium, or freemium with ads. Today: ads plus IAP for hints and skips, level packs, cosmetics and no-ads.

**KPI expectations.** No sourced range. Qualitatively, strong novelty early, with a risk of a content cliff once levels run out.

**Retention drivers.**
- Star completion, and new physical elements per world.
- Daily levels.
- Discovering playful secrets.
- Shareable "look what I did" moments.

**Content pipeline and production scope** (estimates).
- Levels are mostly handcrafted with an editor. Validate each one by sampling the action space (cut times, launch angles and power, simplified drawn paths) in a headless deterministic simulation.
- Store `solver.solvable` and a success ratio in `level-spec`.
- Team: slice 1–2 people plus agents, 3–6 weeks; soft launch 4–10 people, 6–12 months.

**Reference titles.** Cut the Rope (ZeptoLab), Angry Birds (Rovio), Where's My Water? (Disney), World of Goo (2D Boy), Happy Glass (Lion Studios).

**What makes it succeed / fail.**
- Succeeds: a lovable character or goal, and readable physics.
- Succeeds: instant retry, varied elements, and multiple valid solutions.
- Fails: non-deterministic outcomes that feel random.
- Fails: levels with a single pixel-perfect solution, slow restarts, and content droughts.

**Innovation vectors.**
- Drawing-based creativity puzzles.
- UGC level sharing, verified by the simulator.
- Physics with narrative.
- Tactile haptics.

**Agent-buildability: 3/5.** Simulated search can verify levels when the physics is made deterministic. Points are lost for cross-device determinism work, feel tuning and handcrafted level ideation.

**Starter feature list (P0 vertical slice).**
1. Deterministic physics step — fixed timestep and iterations; the same inputs produce the same outcome in 100 headless runs.
2. Core action — one verb (for example a rope cut by swipe) with input tolerance and immediate feedback.
3. Goal and failure detection — the goal object reaches its target, or is lost off-screen or destroyed.
4. Instant retry — restart in under 1 s with no reload stutter.
5. Star system — three star criteria per level, shown before and after.
6. Level editor format — `level-spec` JSON for bodies, joints and goals, loaded at runtime.
7. Solver sampler — a headless sampler confirms 20 levels are solvable and records the success ratio.
8. Difficulty curve — success ratios descend in a sawtooth across 20 levels.
9. Two physical elements — for example a bubble that floats and spikes that destroy, each with teach and twist levels.
10. Hint or skip — a rewarded or coin-based hint that shows the first action.
11. Juice — squash and stretch, impact particles and sound on contact; perf budget held.
12. Analytics — `level_end` (attempts, stars, time) and `hint_used`.

## 12. Logic (nonogram, sudoku and family)

**Definition and player fantasy.** Pure deduction puzzles with exactly one solution: sudoku and killer sudoku, nonograms (picross), kakuro, minesweeper, Flow-style path puzzles, bridges (hashi), star battle, sliding blocks, sokoban and lights-out. Premium puzzle adventures such as Monument Valley and The Room sit at the narrative end. The fantasy is the satisfaction of certainty: a calm, self-improving daily ritual.

**Core loop** (seconds to minutes). Read the clues → deduce a cell → fill it or mark it → verify → complete the puzzle (a nonogram reveals a picture) → time and score → the next or daily puzzle.

**Meta loops.**
- Difficulty tiers and technique unlocks.
- Daily challenges with monthly trophies.
- Picture-collection journeys (nonogram), events and statistics.

**Session profile** (estimate). 5–20 minutes per puzzle; daily ritual play.

**Signature mechanics** (`mechanics-codex`: deduction-constraint, progression-unlocks, collection).
- **Unique-solution guarantee.** It is non-negotiable. A puzzle that needs guessing is broken.
- **Difficulty by technique.** Grade each puzzle by the hardest technique a human-style solver needs. For sudoku that runs from singles to pairs to more advanced patterns, not merely by the number of given clues.
- Pencil marks and notes, a mistake limit or free checking (a mode choice), and hints that teach the next technique rather than revealing a cell.

| Parameter | Starting value to tune (heuristic) | Effect |
|---|---|---|
| Size | Sudoku 9×9; nonogram 5×5 to 25×25+ | Duration and tap precision |
| Technique tier | Unlocked progressively | The real difficulty |
| Mistake limit | 3 in challenge modes, unlimited in relaxed | Stress versus stakes |
| Hint type | Technique explanation first | Teaches rather than skips |
| Daily difficulty | Easy early in the week, harder later | Habit plus a weekly peak |

**Monetization model and typical mix.** Ads (interstitials between puzzles, rewarded hints), no-ads IAP, puzzle packs, and in some titles a premium subscription. Narrative logic adventures are premium.

**KPI expectations.** No sourced range. Qualitatively, puzzle-family games are cited as often matching or beating RPG-level D7 and D30 [V2], with daily-ritual audiences.

**Retention drivers.**
- Daily challenges and trophies.
- Self-improvement statistics.
- Picture reveals.
- Technique mastery.
- Streaks.

**Content pipeline and production scope** (estimates).
- **Generator plus solver plus grader:**
  - *Sudoku:* generate a full grid, remove clues while the solver confirms uniqueness, then grade with a technique-based solver.
  - *Nonogram:* start from a pixel image, compute the clues, then verify that a line solver completes it without guessing.
  - *Sliding, sokoban and lights-out:* use `puzzle_solver.py`.
- Team: slice 1 person plus agents, 1–3 weeks; soft launch 2–5 people, 3–6 months.

**Reference titles.** Sudoku.com and Nonogram.com (Easybrain), Flow Free (Big Duck Games), Monument Valley (ustwo games), The Room (Fireproof Games).

**What makes it succeed / fail.**
- Succeeds: every puzzle is unique and fair, and input is precise (zoom, row and column highlight).
- Succeeds: hints that teach, a calm UI, and a daily habit loop.
- Fails: puzzles that need guessing, and fat-finger errors on small grids.
- Fails: ads mid-solve, and difficulty graded by clue count instead of technique.

**Innovation vectors.**
- Narrative logic adventures.
- New constraint types and hybrids such as picture-logic with story.
- Co-op solving.
- Personalised technique coaching.

**Agent-buildability: 5/5.** It is the ideal agent genre. Correctness is provable, content can be generated without limit, the art is minimal and timing does not matter. The human checkpoint is the UI feel on small grids.

**Starter feature list (P0 vertical slice).** Example: a nonogram.
1. Grid model and clues — row and column clues computed from the solution image (unit-tested).
2. Input modes — fill, cross and drag-fill across cells; undo and redo; zoom for grids above 10×10.
3. Line solver — verifies that a puzzle is solvable without guessing; rejects ambiguous puzzles.
4. Generator — converts 64 pixel-art images (5×5 to 15×15) into verified puzzles.
5. Difficulty grading — technique-depth score stored per puzzle; packs ordered by grade.
6. Mistake handling — relaxed mode (no limit) and challenge mode (3 mistakes) as a settings switch.
7. Hint — highlights a row or column where a deduction exists and explains why.
8. Completion reveal — a colour picture animates on completion; collection album updated.
9. Daily puzzle — one per local day with a trophy calendar.
10. Persistence — mid-puzzle state survives an app kill; resume restores the exact grid.
11. Interstitial policy — only between puzzles; never mid-solve; minimum interval.
12. Analytics — `puzzle_end` (size, grade, time, mistakes, hints) and `daily_complete`.

## 13. Adjacent puzzle formats

| Format | Closest playbook | Key difference |
|---|---|---|
| Bubble shooter | Blast / collapse plus archery (`action-arcade-roguelite.md`) | Aim-and-bank shots; trajectory preview is the core skill |
| Connect / dots | Match-3 | Draw paths through same-colour dots; squares clear all of a colour |
| Jigsaw | Logic (relaxed) | Image packs drive monetization; a near-zero-skill relaxation audience |
| Colour-by-number | Logic (relaxed) | Creativity and relaxation; picture packs and subscriptions |
| Escape room / point-and-click | Logic (narrative end) | Handcrafted, premium or chapter IAP; low agent-buildability for content |
| Spot the difference | Hidden object | Image-pair generation and verification |

## 14. Volatile facts used in this file (as of Oct 2026 — verify before relying)

- [V1] Block Blast! topped mobile game downloads in H1 2026 (Sensor Tower data). Source: [Mobilegamer.biz](https://mobilegamer.biz/data-digest-sensor-towers-h1-analysis-hay-days-comeback-julys-top-games-big-krafton-numbers-and-more/).
- [V2] Install-weighted match-3 benchmarks for top-grossing ambitions are cited "as high as" 47% D1, 24% D7 and 13% D30, with no named source. The same article says board, card, puzzle and idle games often match or beat RPG-level D7/D30. Treat both as secondary. Source: [Playio](https://blog.playio.co/d1-d7-d30-retention-benchmarks-2026).
- [V3] Feb–Apr 2026: casual and hyper-casual each took 40% of game ad revenue. Source: [GameDev Reports summary of Sensor Tower](https://gamedevreports.substack.com/p/sensor-tower-mobile-game-ad-monetization).
- [V4] King's bots predicted difficulty across more than 1,000 Candy Crush levels. Follow-up work reports estimates in under a minute, against 7 days of human playtesting per 15-level episode. Sources: [Gudmundsson et al. 2018](https://www.Gwern.net/doc/reinforcement-learning/imitation-learning/2018-gudmundsson.pdf), [Politecnico di Milano thesis](https://www.politesi.polimi.it/handle/10589/141799).
- [V5] LLM-plus-GAN Snake levels were 87% playable at easy difficulty and 36% at hard, validated with A*. Source: [FedCSIS 2025](https://annals-csis.org/Volume_43/drp/1909.html).
- [V6] On VideoGameQA-Bench (May 2025, older models), GPT-4o had a 17.8% image false-positive rate, implying about 20% precision at a 5% glitch prevalence. Source: [arXiv:2505.15952](https://arxiv.org/html/2505.15952v1).
- Retention anchors for all genres (D1/D7/D30 medians, viability screens, D7/D1 diagnostic, 90-second aha) are listed in `SKILL.md`, Core model 9.
