---
name: mechanics-codex
description: Encyclopedia of 250+ game mechanics in twelve families (verbs/physics, combat, puzzle, economy, progression, social, randomness, time/session, collection/building, narrative/exploration, mobile controls, monetization) with rules, tuning ranges, dynamics, failure modes and implementation notes. Use when choosing, combining, specifying or tuning mechanics, writing mechanic cards, or asking which mechanic would make a game feel a certain way.
---

# Mechanics Codex

A mechanic is a rule that changes game state in response to a player verb or a system event, plus the feedback that makes the change readable. This codex is the studio's shared catalogue of mechanics, written so that a designer can pick one, an engineer can build it, a balancer can tune it and a QA lead can verify it without asking further questions. Every entry in `references/` uses the same anatomy, so mechanics from different files can be compared and combined directly.

## What this skill gives you

- A catalogue of 250+ mechanics across twelve reference files, each entry with: ID, category, player fantasy, precise rules (state, triggers, effects), a tuning-knob table with typical ranges, dynamics, MDA aesthetic targets, feedback and juice, failure modes and exploits, mobile fit, monetization hooks with an explicit ethical limit, implementation notes (data structures, algorithms, pseudo-code), reference games and combinations.
- Methods for **choosing** mechanics from a target experience, **combining** them (mechanic chemistry), keeping the **verb economy** lean, and getting **depth from few rules**.
- A procedure and a validated example for writing a **mechanic card** (`${CLAUDE_PLUGIN_ROOT}/scripts/schemas/mechanic-card.schema.json`) and moving it into the design contract.
- A master index by category with stable kebab-case IDs usable in `combos`, `contract.mechanics[].id` and `level-spec.mechanic_refs`.
- Pointers to the solvers and simulators that verify each mechanic family (puzzle solver, match-3 sim, economy sim, difficulty and progression calculators).

## Core models

**1. Verbs → mechanics → dynamics → aesthetics.** After the MDA framework (Hunicke, LeBlanc and Zubek, 2004): designers author mechanics; players experience aesthetics; dynamics are what emerges between them when real people play. Design backwards: choose 2–3 target aesthetics (from the eight in the schema enum: sensation, fantasy, narrative, challenge, fellowship, discovery, expression, submission), then pick mechanics whose dynamics produce them, then pick the verbs that drive those mechanics on a phone.

**2. Anatomy of a mechanic.** `state` (what data it owns) + `trigger` (verb or event) + `rule` (condition) + `effect` (state change) + `feedback` (how the player perceives it) + `parameters` (knobs with ranges). If you cannot write each part in one or two precise sentences, the mechanic is not designed yet.

**3. Verb economy.** Every verb costs learning time, screen space and thumb travel. Mobile cores typically run on 1–3 verbs. Grow the game by adding new **contexts** for existing verbs (new objects, new rules acting on the same verb) before adding a new verb. Subway Surfers is the reference: four swipe directions reused against trains, barriers, coins, power-ups and the chaser across endlessly reassembled runs. Audit with a verb × context matrix: every verb should appear in ≥ 3 contexts; any verb used in only one context is a candidate for removal.

**4. Depth from few rules.** Depth is the number of meaningfully different strategies and decisions that emerge; complexity is the number of rules a player must learn. Aim for a high depth-to-complexity ratio, as Go does with almost no rules. Orthogonal elements (each differs in a distinct dimension: speed vs armor vs range vs area) create more depth per rule than "the same but bigger" (see Harvey Smith's GDC talk "Orthogonal Unit Differentiation"). Measure depth empirically with a **bot ladder**: random < greedy < lookahead bots. If greedy ≈ lookahead in win rate, there is no planning depth; if random ≈ greedy, decisions do not matter.

**5. Mechanic chemistry.** Two mechanics have chemistry when one reads or writes state the other uses. Interaction types: **amplify** (A makes B stronger), **enable** (A creates opportunities for B), **counter** (A works against B — creates tension), **transform** (A turns B's output into something new), **gate** (A controls access to B), **tax** (A drains B). Systemic design — objects with properties and rules acting on properties — multiplies chemistry; Nintendo's GDC 2017 talk on *Breath of the Wild* described this as a "chemistry engine". Mechanics with no interactions are "mechanic soup": content, not depth.

**6. Skill atoms and learning.** Dan Cook ("The Chemistry of Game Design", Lostgarden, 2007) models play as loops of action → simulation → feedback → updated mental model, chained into skill trees. Raph Koster (*A Theory of Fun for Game Design*, 2004) frames fun as the act of mastering patterns; once patterns are exhausted, boredom follows. Practical rule: teach each atom alone, then combine; keep supplying new patterns (twists, blockers, enemy affixes) at the rate players exhaust old ones.

**7. Interesting decisions.** A choice is interesting when options have real trade-offs, the player has enough information to reason, and consequences are felt (Sid Meier's widely quoted definition of a game as a series of interesting decisions). Dominant options, blind choices and inconsequential choices are the three failure shapes.

**8. Where randomness lives.** Input randomness (random situation, then the player decides — card draws, refills) preserves agency; output randomness (the player decides, then a roll decides the outcome — crits, drops) creates suspense but can feel unfair. Details and fairness techniques are in `references/07-randomness-chance-mechanics.md`.

**9. Loops and flows.** Mechanics that move resources form feedback loops. Positive loops snowball, negative loops stabilise; name every loop and decide which may run away. Resource mechanics map to source, sink, converter, pool and gate nodes (`references/04-economy-resource-mechanics.md`).

**Aesthetic → mechanic shortlist** (IDs from the reference files):

| Target aesthetic | Strong mechanic choices | Watch out for |
|---|---|---|
| Sensation | `slice`, `physics-stacking`, `ragdoll`, `blast-collapse`, `special-pieces`, `hitstop-hitboxes` | Juice cannot rescue shallow rules |
| Fantasy | `auto-aim-survivors`, `crowd-mob-combat`, `idle-generators`, `renovation-meta` | Needs art and narrative support to land |
| Narrative | `dialogue-choice`, `storylets`, `progress-gated-story`, `renovation-meta` | Content cost per hour of play |
| Challenge | `jump`, `parry`, `bullet-patterns`, `sokoban`, `rhythm-timing`, `boss-encounters` | Frustration; touch latency |
| Fellowship | `clans-guilds`, `team-chests`, `co-op-events`, `gifting-help`, `async-base-raid` | Population liquidity |
| Discovery | `discovery-crafting`, `elemental-reactions`, `secrets`, `map-reveal`, `fog-of-war` | Content consumed once |
| Expression | `free-placement-decor`, `auto-battle-squad`, `draw-a-path`, `talent-tree` | Dominant builds kill expression |
| Submission | `merge`, `sort-puzzle`, `idle-generators`, `block-placement`, `farming-cycle` | Boredom without goals |

## Decision procedures

### A. Choose the core mechanic for a concept

1. Write the player fantasy in one sentence and pick 2–3 target aesthetics in priority order.
2. Fix the input budget: one-hand portrait (tap, swipe, drag, hold-release) or two-thumb landscape (sticks, buttons). See `references/01-verbs-movement-physics.md` and `references/11-mobile-input-control-schemes.md`.
3. Shortlist 3–5 core mechanics from the aesthetic table and the relevant family file. For each, read the entry's dynamics and failure modes.
4. Score each candidate 1–5 on: fantasy match, mobile fit (verbs and session), depth potential (does the bot ladder have room?), production cost (content per hour), verification ease (solver/bot available?), market proof (reference games). Drop anything scoring ≤ 2 on mobile fit or verification.
5. Choose the core and **one** hook: a twist transplanted from another family (table C). The hook must interact with the core's state (chemistry), not sit beside it.
6. Prototype the core loop with placeholder art in hours; run bots; only then layer meta (05), economy (04), social (06), session (08) and monetization (12).
7. Write kill criteria: e.g., "if testers do not voluntarily replay within 3 sessions" or "if greedy and lookahead bots differ by < 5 % win rate".

### B. Combine mechanics with a chemistry matrix

1. List the core mechanic and every candidate secondary mechanic (max 6 at concept stage).
2. Build a matrix: rows act on columns. Mark each cell with an interaction type (amplify ↑, enable →, counter ⊣, transform ⇄, gate ⧖, tax $) or `·` for none.
3. Require: every secondary mechanic has ≥ 2 non-empty cells with the core; at least one **two-way loop** (A affects B and B affects A); no mechanic whose row and column are both empty.
4. For each two-way loop, name the dynamic it should produce and the failure mode to watch.
5. Cut the weakest secondary mechanic; repeat until every remaining mechanic earns its complexity.

Worked example — "block placement where cleared lines attack monsters":

| acts on → | `block-placement` | `wave-director` | `status-effects` | `boosters` |
|---|---|---|---|---|
| `block-placement` | — | ↑ line clears deal damage; combos multiply it | ⇄ clearing coloured rows applies matching element | $ spends boosters |
| `wave-director` | ⊣ enemy attacks drop junk blocks onto the board | — | → elites carry status immunities | ⧖ boss waves unlock booster drops |
| `status-effects` | ↑ "frozen" enemies give extra placement turns | ⊣ slows delay spawns | — | · |
| `boosters` | → hammer clears a junk block | · | · | — |

The two-way loop (placement damages enemies; enemies pollute the board) is the heart of the design: it converts a solitary puzzle into a pressure duel. Watch for a death spiral when junk accumulates (cap junk per wave; test with bots).

### C. Proven transplants (core + hook)

| Core mechanic | Transplanted hook | Reference result |
|---|---|---|
| `match3-swap` | hero collection + `auto-battle-squad` stats | Empires & Puzzles |
| `match3-swap` | `renovation-meta` + narrative | Homescapes, Gardenscapes |
| `merge` | `tower-targeting` / lane defense | Rush Royale, Random Dice |
| `auto-run-lanes` | `crowd-mob-combat` gates | Count Masters |
| `stop-to-shoot` | `projectile-upgrades` draft | Archero |
| `card-draw` + `deck-building` | `run-generation` (roguelike) | Slay the Spire |
| `physics-stacking` (drop) | `merge` tiers | Suika Game |
| `slingshot-aim-release` | destruction physics + special projectiles | Angry Birds |
| `idle-generators` | `prestige-rebirth` + `automation-managers` | AdVenture Capitalist |
| `gps-location` | `creature-collection` + `flick` | Pokémon GO |
| `lane-defense` (real-time duel) | card collection + regenerating deploy resource | Clash Royale |

### D. Audit verb economy and depth

- [ ] Verb list ≤ 3 for the core loop; each verb used in ≥ 3 contexts (verb × context matrix written).
- [ ] Every verb has a forgiveness mechanism appropriate to touch (buffer, expanded hit radius, aim assist, coyote time).
- [ ] Bot ladder run: random, greedy and lookahead (or human-like) bots show a meaningful win-rate spread (≥ 10 percentage points between adjacent rungs is a healthy signal for puzzle and strategy cores).
- [ ] No dominant option: pick rates of any upgrade, unit or move type below ~40 % when ≥ 4 options exist.
- [ ] New patterns arrive at the rate the content plan consumes them (one new element every 10–40 levels or every few sessions).

### E. Write a mechanic card

1. Start from the codex entry; copy its ID if the mechanic is used as-is, or create a project ID (lower snake_case or kebab-case; both match the schema's id pattern) if you adapt it.
2. Map entry fields to card fields:

| Codex entry field | Card field | Notes |
|---|---|---|
| ID / Name / Category | `id`, `name`, `category` | Category from the schema's suggested vocabulary (movement, aiming, timing, placement, merge, match, sort, physics, combat, resource, construction, chance, collection, progression, social, narrative, puzzle, economy) |
| Player fantasy | `player_fantasy` | One sentence, player's voice |
| (verbs used) | `verbs` | Verb ids from `contract.verbs`, or full `{id, input, description}` objects |
| Core rules | `rules` | One precise, implementable rule per string, including edge cases |
| Tuning knobs | `parameters` | `{key, value, min, max, unit, note}`; value is the starting point |
| Dynamics | `dynamics` | Emergent behaviours you expect, phrased so playtests can confirm them |
| Aesthetics (MDA) | `aesthetics` | Lowercase enum values, most important first |
| Feedback and juice | `feedback` | Visual, audio, haptic, numeric |
| Failure modes | `failure_modes` | Each with its detection signal (bot metric, telemetry, playtest observation) |
| Mobile fit | `mobile_fit` | `one_hand` bool, `session_fit` micro/short/medium/long, `notes` |
| Reference games / Combines well with | `references`, `combos` | `combos` are mechanic IDs |

3. Save as `<id>.mechanic.json` (the `.mechanic.json` suffix selects the schema anywhere, e.g. `.gamestudio/concepts/slingshot-aim-release.mechanic.json`). Validate: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py validate <path>` or `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_json.py --auto <path>`.
4. Copy the contract-relevant subset into `contract.json` → `mechanics[]` (`id`, `name`, `category`, `verbs`, `rules`, `parameters`, `feedback`, `mobile_notes`). The card stays the detailed source; the contract stays one page.
5. Reference the mechanic ID from every level that uses it (`level-spec.mechanic_refs`) and from feature acceptance criteria in `features.json`.

Validated example (abridged; full file passes `validate_json.py --auto`):

```json
{
  "schema_version": "1.0",
  "id": "slingshot-aim-release",
  "name": "Slingshot aim-release",
  "category": "aiming",
  "player_fantasy": "I line up the perfect shot and watch the chaos unfold.",
  "verbs": [{ "id": "drag_aim", "input": "drag", "description": "Drag back from the launcher to set direction and power." },
            { "id": "release_fire", "input": "hold_release", "description": "Lift to launch; release inside the dead zone to cancel." }],
  "rules": ["Pull vector p = anchor - finger, clamped to |p| <= pull_max_dp.",
            "Launch velocity = normalize(p) * power_curve(|p| / pull_max_dp) * v_max.",
            "While dragging, draw the predicted path for the first preview_fraction of flight using the runtime integrator.",
            "Releasing inside cancel_radius_dp of the anchor cancels without spending a shot."],
  "parameters": [{ "key": "pull_max_dp", "value": 140, "min": 80, "max": 200, "unit": "dp", "note": "Finer control vs thumb travel." },
                 { "key": "preview_fraction", "value": 0.3, "min": 0.0, "max": 1.0, "unit": "ratio", "note": "Main skill lever." },
                 { "key": "shots_per_level", "value": 3, "min": 2, "max": 6, "unit": "shots", "note": "Tune with bot win rate." }],
  "dynamics": ["Experiment-and-refine across retries.", "Weak-point hunting on structures."],
  "aesthetics": ["sensation", "challenge", "discovery"],
  "feedback": ["Elastic stretch with rising creak pitch", "Debris, dust and score popups on impact"],
  "failure_modes": ["Non-deterministic physics: replay recorded inputs 20 times headless and diff outcomes.",
                    "One shot solves most levels: bot first-shot win rate above 40 %."],
  "mobile_fit": { "one_hand": true, "session_fit": "short", "notes": "Turn-based between shots; launcher in the lower third." },
  "references": ["Angry Birds 2", "Bowmasters", "Golf Battle"],
  "combos": ["trajectory-ballistics", "physics-stacking", "ragdoll"]
}
```

### F. Tune a mechanic

1. Put every knob from the entry's table into data with `min`/`max` (contract `parameters`), never in code.
2. Set start values at the middle of the typical range; adjust toward the edge that serves the target aesthetic (e.g., shorter `time to apex` for snappy challenge).
3. Run the family's verifier (section "Using the ontology") to get win rates, `min_moves` or flow curves; tune the strongest lever first (the entry tables list levers roughly in order of power).
4. Change one knob at a time between bot runs; log each run's parameters and results under `.gamestudio/reports/`.
5. Confirm with persona playtests (`arcosian:player-simulator`) and finally humans: bots measure difficulty, not fun.

## Mobile specifics

| Concern | Rule of thumb | Where detailed |
|---|---|---|
| Verbs | One-hand portrait: tap, swipe, drag, hold-release. Two-hand: sticks, pinch, tilt (always with a touch fallback) | `references/01-verbs-movement-physics.md`, `references/11-mobile-input-control-schemes.md` |
| Precision | Targets ≥ 44 pt / 48 dp; timing windows ≥ 100 ms for core actions; expand hit areas 20–50 % | Entry knob tables |
| Occlusion | The thumb hides what it touches: lift dragged objects 40–100 dp, offset cameras toward aim | `drag`, `twin-stick-aim-assist` |
| Session fit | Map each core to `micro` (< 1 min), `short` (1–5), `medium` (5–15), `long` (> 15) and keep at least one complete, rewarding loop inside the target session | `references/08-time-energy-session-mechanics.md` |
| Interruptions | Prefer turn-based or pause-safe mechanics; serialise full mechanic state on background; resume exactly | `gameplay-programming` |
| Determinism | Fixed-step simulation, seeded RNG, input events with timestamps — required for the playthrough gate | `qa-testing` |
| Performance | Budget entity counts (hordes, bullets, ragdolls, particles) per device tier before design locks | `mobile-performance` |
| OS gestures | Keep gesture start zones away from screen edges and inside safe areas | `mobile-ux` |

## Anti-patterns

| Anti-pattern | Symptom / detection | Fix |
|---|---|---|
| Verb bloat | Tutorial teaches > 3 verbs before the first win; FTUE drop-off at verb lessons | Cut or merge verbs; add contexts instead |
| Mechanic soup | Chemistry matrix has empty rows/columns | Remove isolated mechanics or wire them to shared state |
| Dominant strategy | One option's pick rate > 40–50 %; bots converge on one move | Add counters, costs or situational value |
| Complexity masquerading as depth | Many rules, but greedy bot ≈ lookahead bot | Remove rules; add interactions between remaining ones |
| Cargo-cult cloning | Copying a hit's core without its supporting systems (e.g., match-3 without blockers, specials and a level pipeline) | Copy the whole system stack or none; read `game-case-studies` |
| Juice over substance | Playtesters say "pretty" but do not replay | Fix rules first; juice amplifies, it does not create |
| Monetization-first mechanics | Friction that only exists to be sold (energy walls on day 1, rigged near-misses) | Apply the entry's ethical limit; review with `monetization` and `legal-ethics` |
| Untestable mechanics | Non-deterministic physics or frame-dependent timing; replays diverge | Fixed step, seeded RNG, timestamped inputs |
| Two-hand core on a casual title | Low one-hand session share; commute play impossible | Re-map to one-hand verbs or accept a mid-core audience |
| Tuning by feel only | No bot or solver evidence in level specs | Use the verifiers; record `solver` fields |

## Using the ontology

- **Verbs** → `contract.verbs[]` (`{id, input, description}`); mechanic cards list verb IDs in `verbs`.
- **Mechanics** → stand-alone `*.mechanic.json` cards (`mechanic-card.schema.json`) and the one-page subset in `contract.mechanics[]`. Deconstructions embed the same card shape in `deconstruction.mechanics[]`.
- **Dynamics and aesthetics** → card `dynamics` and `aesthetics` (MDA enum); playtest reports (`playtest-report.schema.json`) should confirm or refute listed dynamics.
- **Resources** → mechanics from `references/04-economy-resource-mechanics.md` become `economy-model` nodes (`source|sink|converter|gate|pool`) with triggers.
- **Levels** → `level-spec.mechanic_refs` lists the mechanic IDs a level exercises; `teach` marks teach/test/twist/reward.
- **Loops** → `contract.loops[]` steps reference the mechanics that produce each action and reward.

Verifiers by family:

| Family | Tool | Output used |
|---|---|---|
| Sliding, sokoban, sort, lights-out puzzles | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/puzzle_solver.py --level PATH --algo astar --json` | `solver.solvable`, `solver.min_moves` |
| Match-3 (swap rules only; blast needs its own simulator) | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/match3_sim.py --level PATH --runs 500 --bot greedy --json` (level `layout.type` must be `match3`) | `win_rate` (copy to `solver.bot_win_rate`), `moves_left`, `difficulty_band` |
| Economy and resource mechanics | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/economy_sim.py --model PATH --runs 200 --json` | Net flows, hoard days, completion days |
| Upgrade and level curves | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/progression_calc.py curve --formula exp --levels N --base B --growth G --json` | Cost tables, time-to-level |
| Difficulty sequencing | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/difficulty_curve.py generate --levels N --pattern sawtooth --base 0.8 --floor 0.35 --json` | Target win rates per level |
| Gacha, chests, pity | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gacha_calc.py --rate R --hard-pity N --json` | Expected pulls, cost distribution |
| Procedural layouts for mechanics | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/pcg.py wfc\|bsp\|cave\|noise\|poisson\|maze --w W --h H --seed S --json` | Layouts to verify with solvers/bots |
| Engine playthroughs and bots | Godot/Unity runners (BLUEPRINT section 13) | `playtest-report` JSON for the playthrough gate |
| Search this codex | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py kb "hold release charge" --skill mechanics-codex` | Ranked snippets with file paths |

## Master index by category

IDs are stable; use them in `combos`, cards and contracts. Each file opens with its own index table (one-line essence, family, home genres).

<!-- MASTER-INDEX:START -->
| File | Category | Count | Mechanic IDs (in file order) |
|---|---|---|---|
| 01 | Verbs, movement and physics | 23 | `tap`, `directional-swipe`, `slice`, `drag`, `hold-release`, `tilt`, `pinch-rotate`, `jump`, `dash`, `slide`, `grapple-swing`, `auto-run-lanes`, `one-tap-impulse`, `gravity-flip`, `slingshot-aim-release`, `trajectory-ballistics`, `flick`, `physics-stacking`, `ragdoll`, `momentum-slopes`, `physics-vehicle`, `draw-a-path`, `rhythm-timing` |
| 02 | Combat and action | 23 | `auto-attack`, `auto-aim-survivors`, `stop-to-shoot`, `twin-stick-aim-assist`, `auto-battle-squad`, `cooldown-abilities`, `combos`, `parry`, `dodge-iframes`, `bullet-patterns`, `projectile-upgrades`, `crowd-mob-combat`, `elemental-reactions`, `status-effects`, `damage-model`, `aggro-threat`, `tower-targeting`, `lane-defense`, `wave-director`, `boss-encounters`, `elite-affixes`, `hitstop-hitboxes`, `knockback-poise` |
| 03 | Puzzle | 23 | `match3-swap`, `blast-collapse`, `special-pieces`, `blockers`, `merge`, `sort-puzzle`, `block-placement`, `line-clear`, `sliding-tiles`, `sokoban`, `flow-connect`, `pin-pull`, `screw-out`, `triple-match-tray`, `mahjong-solitaire`, `nonogram`, `sudoku-variants`, `word-formation`, `hidden-object`, `spot-the-difference`, `physics-puzzle`, `rotation-puzzle`, `packing-puzzle` |
| 04 | Economy and resources | 21 | `currency-architecture`, `idle-generators`, `exponential-upgrades`, `multiplier-milestones`, `automation-managers`, `offline-earnings`, `prestige-rebirth`, `production-bottlenecks`, `crafting-chains`, `build-queues`, `storage-caps`, `converters-exchange`, `player-trading`, `markets-auctions`, `energy`, `lives-pool`, `boosters`, `gold-sinks`, `chests`, `upkeep-decay`, `gathering-nodes` |
| 05 | Progression and meta | 20 | `xp-levels`, `account-level`, `unlock-schedule`, `talent-tree`, `star-ratings`, `saga-map`, `chapters-worlds`, `renovation-meta`, `collections-albums`, `achievements`, `mastery-tracks`, `hero-ascension`, `gear-rarity`, `research-trees`, `prestige`, `seasonal-ladder`, `win-streaks`, `login-calendar`, `missions-quests`, `pass-tracks` |
| 06 | Social and competitive | 20 | `async-base-raid`, `async-arena`, `async-turn-matches`, `leaderboards`, `leagues-divisions`, `matchmaking-rating`, `tournaments`, `clans-guilds`, `guild-wars`, `co-op-events`, `team-races`, `team-chests`, `gifting-help`, `friends-graph`, `chat-emotes`, `spectating-replays`, `trading`, `raids`, `ghosts`, `referrals` |
| 07 | Randomness and chance | 21 | `dice`, `card-draw`, `deck-building`, `shuffle-bag`, `weighted-rng`, `loot-tables`, `pity-timers`, `gacha-banners`, `rate-up`, `spark`, `mystery-boxes`, `slot-spin`, `prize-wheel`, `run-generation`, `crits`, `procedural-affixes`, `prd`, `input-output-randomness`, `perceived-fairness`, `duplicate-protection`, `assisted-refill` |
| 08 | Time, energy and session | 20 | `energy-stamina`, `lives`, `build-timers-and-skips`, `appointment-mechanics`, `offline-progress`, `idle-accumulation`, `reset-cadences`, `daily-streaks`, `streak-protection`, `comeback-bonus`, `limited-time-events`, `session-caps`, `rest-bonus`, `cooldowns-charges`, `level-limits`, `content-drip`, `realtime-vs-turn`, `interruption-safe`, `notification-hooks`, `real-world-clock` |
| 09 | Collection, crafting and building | 20 | `set-bonuses`, `collection-log`, `recipe-crafting`, `discovery-crafting`, `storage-capacity`, `base-defense-layout`, `hq-gated-building`, `city-zoning`, `farming-cycle`, `free-placement-decor`, `design-challenge`, `creature-collection`, `creature-breeding`, `branching-evolution`, `fusion-tables`, `virtual-pet`, `merge-board`, `merge-world`, `order-board`, `production-chain` |
| 10 | Narrative and exploration | 20 | `dialogue-choice`, `branching-narrative`, `storylets`, `relationship-meters`, `premium-choice`, `progress-gated-story`, `realtime-narrative`, `quest-arcs`, `waypoint-guidance`, `fog-of-war`, `map-reveal`, `ability-gating`, `secrets`, `lore-collectibles`, `environmental-storytelling`, `deduction`, `time-loop`, `expeditions`, `gps-location`, `ar-play` |
| 11 | Mobile input and control schemes | 20 | `one-thumb-portrait`, `tap-anywhere`, `context-action-button`, `virtual-stick`, `aim-stick`, `skill-cluster`, `fps-touch-scheme`, `hud-customization`, `target-lock`, `tap-to-move`, `swipe-command-scheme`, `drag-aim-scheme`, `board-manipulation`, `camera-gestures`, `tilt-gyro-scheme`, `auto-play`, `idle-input`, `haptic-language`, `input-accessibility`, `controller-support` |
| 12 | Monetization-linked | 20 | `rewarded-revive`, `rewarded-double`, `rewarded-free-spin`, `rewarded-unlock`, `interstitial-cadence`, `paid-boosters`, `continues`, `timer-skips`, `refill-offers`, `starter-pack`, `triggered-offers`, `piggy-bank`, `currency-store`, `cosmetic-shop`, `web-shop`, `vip-tiers`, `premium-pass`, `subscription-perks`, `offer-wall`, `paid-random-rewards` |
<!-- MASTER-INDEX:END -->

**Overlaps by design.** Some mechanics appear in two files through different lenses; read both when designing them:

| Topic | Mechanic lens | Companion lens |
|---|---|---|
| Energy | `energy` (04: pool maths, pricing) | `energy-stamina` (08: session architecture) |
| Lives | `lives-pool` (04: pool and booster economy) | `lives` (08: session gate) |
| Timers | `build-queues` (04: speed-up pricing) | `build-timers-and-skips` (08: appointment cadence) |
| Offline and idle | `offline-earnings`, `idle-generators` (04) | `offline-progress`, `idle-accumulation` (08) |
| Prestige | `prestige-rebirth` (04: formulas) | `prestige` (05: meta pacing) |
| Production and crafting | `production-bottlenecks`, `crafting-chains` (04) | `production-chain`, `recipe-crafting` (09) |
| Storage | `storage-caps` (04) | `storage-capacity` (09) |
| Merge | `merge` (03: puzzle rules) | `merge-board`, `merge-world` (09: meta and orders) |
| Trading | `player-trading` (04) | `trading` (06: social safety) |
| Random rewards | `chests` (04) | `mystery-boxes`, `loot-tables`, `pity-timers` (07) |
| Crits and affixes | `damage-model`, `elite-affixes` (02) | `crits`, `procedural-affixes` (07) |
| Board refills | `match3-swap` refill bias (03) | `assisted-refill` (07: fairness) |
| Cooldowns | `cooldown-abilities` (02: combat) | `cooldowns-charges` (08: session) |
| Controls | `tap`, `directional-swipe`, `tilt`, `pinch-rotate` (01), `twin-stick-aim-assist` (02) | `tap-anywhere`, `swipe-command-scheme`, `tilt-gyro-scheme`, `camera-gestures`, `aim-stick` (11: full schemes) |
| Monetized relief | `boosters`, `energy`, `lives-pool`, `build-queues`, `chests` (04: economy) | `paid-boosters`, `refill-offers`, `timer-skips`, `paid-random-rewards` (12: offers, ethics, regulation) |

## Reference library

| File | What it contains | Read it when |
|---|---|---|
| `references/01-verbs-movement-physics.md` | 23 touch verbs and movement/physics mechanics (tap, swipe, slice, drag, hold-release, tilt, pinch, jump, dash, slide, grapple, auto-run lanes, one-tap impulse, gravity flip, slingshot, trajectories, flick, stacking, ragdoll, momentum, vehicles, draw-a-path, rhythm) with forgiveness windows and fixed-step implementation rules | Choosing a core verb, tuning controls feel, building runners, physics or hyper-casual cores |
| `references/02-combat-action.md` | 23 combat mechanics: auto-attack, survivors, stop-to-shoot, twin-stick aim assist, auto-battle squads, cooldowns, combos, parry, i-frames, bullet patterns, projectile upgrades, crowd armies, elemental reactions, status effects, damage model, aggro, tower targeting, lane defense, wave director, bosses, elite affixes, hit-stop/hitboxes, poise; TTK and damage formulas | Designing or balancing any fight, TD, survivors or idle RPG battle |
| `references/03-puzzle-mechanics.md` | 23 puzzle mechanics: match-3, blast, specials, blocker taxonomy, merge, sort, block placement, line clear, sliding, sokoban, flow, pin-pull, screw-out, triple-match tray, mahjong, nonogram, sudoku, word, hidden object, spot-the-difference, physics, rotation, packing; solvability rules and generators | Building a puzzle core, level pipeline, solver or bot verification |
| `references/04-economy-resource-mechanics.md` | 21 economy mechanics: currencies, generators, exponential costs, multipliers, automation, offline earnings, prestige, bottlenecks, crafting, build queues, storage, converters, trading, markets, energy, lives, boosters, sinks, chests, upkeep, gathering; flow vocabulary and formulas | Designing resource flows, idle maths, energy/lives, sinks, or writing an `economy-model` |
| `references/05-progression-meta-mechanics.md` | Progression and meta: XP and levels, account level, unlock schedules, talent trees, stars, saga maps, chapters, renovation meta, collections, achievements, mastery, hero ascension, gear rarity, research, prestige, seasonal ladders, win streaks, login calendars, missions, pass tracks | Designing the meta layer and long-term goals around a proven core |
| `references/06-social-competitive-mechanics.md` | Social and competitive: async raids and arenas, async turns, leaderboards, leagues, matchmaking ratings, tournaments, clans, guild wars, co-op events, team races, team chests, gifting, friends, chat, spectating, trading, raids, ghosts, referrals; integrity and liquidity maths | Adding social retention, PvP or guild systems |
| `references/07-randomness-chance-mechanics.md` | Randomness: dice, card draw, deck-building, shuffle bags, weighted RNG, loot tables, pity, gacha banners, rate-up, spark, mystery boxes, slots, prize wheels, run generation, crits, affixes, PRD, input vs output randomness, perceived fairness, duplicate protection, assisted refill | Placing randomness, designing drops or gacha, fairness and odds disclosure |
| `references/08-time-energy-session-mechanics.md` | Time and session: energy/stamina, lives, build timers and skips, appointments, offline progress, idle accumulation, reset cadences, streaks and protection, comeback bonuses, limited-time events, session caps, rest bonuses, cooldowns and charges, move limits vs timers, content drip, real-time vs turn-based, interruption-safe design, notification hooks, real-world clock; session equations | Shaping session length, return cadence and time-gated systems |
| `references/09-collection-crafting-building.md` | Collection, crafting and building: set bonuses, catalogues, recipe and discovery crafting, storage, base layout, HQ-gated building, city zoning, farming cycles, decoration, design challenges, creature capture, breeding, evolution, fusion, virtual pets, merge boards and worlds, order boards, production chains | Designing collection, base-building, farming, creature or merge-meta games |
| `references/10-narrative-exploration-mechanics.md` | Narrative and exploration: dialogue choices, branching, storylets, relationship meters, premium choices, progress-gated story, real-time messaging stories, quests, waypoints, fog of war, map reveal, ability gating, secrets, lore, environmental storytelling, deduction, time loops, expeditions, GPS and AR play | Adding story, exploration or location-based layers |
| `references/11-mobile-input-control-schemes.md` | Control schemes above the verb layer: one-thumb portrait, tap-anywhere, context buttons, virtual sticks, aim sticks with tap-to-auto-aim (`aim-stick`), MOBA skill clusters, shooter layouts, HUD customisation, target lock, tap-to-move, swipe vocabularies, drag-aim, board and card manipulation, camera gestures, tilt and gyro, auto-play with speed-up and sweep controls (`auto-play`), the idle input model (`idle-input`), haptic languages, accessibility alternatives, controller support | Mapping mechanics to touch controls, choosing a scheme per genre, or reviewing control feel and accessibility |
| `references/12-monetization-linked-mechanics.md` | Monetization-linked mechanics with an ethical limit and regulatory notes per entry: rewarded revives, reward doubling, ad-funded spins, rewarded unlocks, interstitial cadence and Remove Ads, paid boosters, continues, timer skips, refills, starter packs, triggered and chain offers, piggy banks, currency stores, cosmetic shops, web shops, VIP tiers, premium passes, subscriptions, offer walls, paid randomized rewards; ethics baseline and regulatory map | Attaching monetization to a mechanic, reviewing an offer for dark patterns, or preparing compliance notes |

## Related skills

- `game-ontology` — the shared vocabulary and schemas these cards plug into.
- `design-theory` — MDA, flow, motivation and the frameworks behind the core models.
- `design-philosophies` — studio doctrines for choosing what to build.
- `genre-playbooks` — which mechanic stacks each genre ships with.
- `game-case-studies` — deconstructions showing mechanics in their full system context.
- `analogy-engine` — the "X meets Y" method for mechanic transplants.
- `player-psychology` — why mechanics motivate, and where persuasion turns into manipulation.
- `game-feel` — the juice and responsiveness layer on top of every verb.
- `economy-design` — macro economy architecture and simulation for resource mechanics.
- `progression-difficulty` — curves, difficulty and DDA for tuned mechanics.
- `level-design` — turning mechanics into teach/test/twist level sequences.
- `procedural-generation` — generating content that exercises mechanics, with verification.
- `gameplay-programming` — implementing mechanics deterministically in the sim core.
- `mobile-ux` — touch, thumb zones, safe areas and HUD for mechanic controls.
- `monetization` and `legal-ethics` — the ethical limits referenced in every entry.
- `qa-testing` — bots, solvers and playthrough evidence for the five gates.
