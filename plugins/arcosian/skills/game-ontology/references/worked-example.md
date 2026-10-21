# Worked example: following one game through every document

The folder `${CLAUDE_PLUGIN_ROOT}/scripts/schemas/examples/` holds one example per schema, almost all of them about the same fictional game, "Pebble Keep" (a portrait, one-thumb merge-tower-defence game with a keep-restoration meta). The deconstruction example is a different, real game (Royal Match) used to show how an existing game is described. This file walks through them in the order a project produces them, shows which ontology layer each document captures, and points out the reasoning a senior reviewer applies at each stage. Use it as a pattern for your own documents and as a calibration of how dense a good document is. All figures quoted come from the example files; they are illustrative, not market data.

## Contents
1. The document chain
2. Concept: the idea in one card
3. Design contract: the layered model filled in
4. Mechanic cards: the stand-alone form
5. Economy model: resource flow in numbers
6. Level spec: one unit of content
7. Event taxonomy: how the game reports itself
8. Features: delivery through the five gates
9. Config, assets and budget
10. Playtest and perf reports: evidence
11. Deconstruction: reading someone else's game
12. Cross-document consistency checks
13. Exercise: add a new mechanic end to end

## 1. The document chain

| Stage | Document | Example file | Layer emphasis |
|---|---|---|---|
| Ideation | Concept card | `example.concept.json` | Player, motivation, hook |
| Design | Contract | `example.design-contract.json` | All layers, loops, content, session |
| Design | Mechanic cards | `example.mechanic-card.json` | Mechanics to dynamics to aesthetics |
| Design | Economy model | `example.economy-model.json` | Resources and flows |
| Content | Level spec | `example.level-spec.json` | Content, pacing |
| Telemetry | Event taxonomy | `example.event-taxonomy.json` | Measurement of dynamics |
| Delivery | Features | `example.features.json` | Gates |
| Setup | Config, budget, assets | `example.config.json`, `example.budget.json`, `example.asset-manifest.json` | Production state |
| Evidence | Playtest, perf | `example.playtest-report.json`, `example.perf-report.json` | Observed dynamics and budgets |
| Research | Deconstruction | `example.deconstruction.json` | Analysis of an existing game |

Validate all of them in one command:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_json.py --auto ${CLAUDE_PLUGIN_ROOT}/scripts/schemas/examples
```

## 2. Concept: the idea in one card

The concept (`id: c03_pebble_keep`, `status: winner`) states an analogy ("Rush Royale meets Royal Match"), a one-sentence player fantasy (young keeper of a crumbling garden keep waking stone golems), a core loop as a graph (spawn, merge, defend, with branches back), and a hook: every win restores a visible piece of the keep, and the restoration unlocks new golem families, so the meta feeds the core instead of sitting beside it.

What to notice:

- **The hook is a relationship between loops**, not a feature. That is the pattern worth copying: novelty often lives in how the core and meta loops connect.
- **Comparables carry a `borrow` and a `change`.** Each names what is taken and how it is transformed, which prevents a clone.
- **Scores** come with their weighting in the `rationale` (fun potential doubled, market 1.5, others 1), so `weighted_total` of 7.47 can be recomputed. The weakest score (novelty) is named, along with the bet that addresses it.
- **Kill criteria are measurable**: a count of persona playtests choosing a second run, and a creative test against a pre-set cost ceiling.

## 3. Design contract: the layered model filled in

Walk the contract top to bottom against the layer model in `references/ontology-overview.md`.

| Layer | Where in the example | What it says |
|---|---|---|
| Player | `meta.target_audience` | Age floor 13; segments such as casual merge and puzzle players and commute players; motivations strategy, completion, design, challenge |
| Motivation | `motivations`, loop descriptions | Completion and design are served by the restoration loop; challenge by the core |
| Aesthetics | `player_fantasy`, `meta.pillars` | Four pillars: one thumb in three minutes, visible power spikes, readable chaos on small phones, a keep that grows |
| Dynamics | on cards (section 4) | Board pressure, holding patterns, family focus |
| Mechanics | `mechanics[]`: `spawn_bag`, `merge_two`, `lane_defense`, `rune_sort` | Each with precise rules and ranged parameters |
| Verbs | `verbs[]`: `tap_spawn`, `drag_merge`, `tap_pour` | Three verbs, two of them in the core |
| Resources | `economy.currencies[]` | Coins (soft), gems (hard), stars and runes (material), shells (event), with sources, sinks and caps |
| Loops | `loops[]` | `core` (seconds), `meta_restore` and `rune_bonus` (session), `revive` (monetization, minutes), `snail_rally` (liveops, weekly) |
| Content | `content` | Counts and generation approach, with `spec_ref` to level specs |
| Session | `meta.session_length_target_sec` 240 | Four minutes; FTUE aha target 45 seconds |

How a reviewer reads the loops:

1. `core` s3 branches to `s1` (keep spawning) or `s4` (boss cleared). That is a real fork; the player decides how long to hold before spending.
2. `s4` hands off to `loop:meta_restore`; the meta loop m4 returns to `m1`, and `rune_bonus` b3 returns to `loop:core`. Every loop is reachable and has an exit, so health checks 1 and 8 pass.
3. `revive` is a monetization loop with a single optional choice, framed as a continue offered once per run. It is a loop that the player can decline at no cost, which is the ethical pattern the contract's `monetization.ethics` should state.
4. `snail_rally` is expressed as a delta (a new resource, `shells`, with a cap of 500, and event chests with disclosed odds), not as a new game.

Reconciliation items a careful reviewer would raise in this example (they are good habits even if the example is internally consistent): the contract's `session_length_target_sec` is 240 while `analytics.kpi_targets.session_len_sec` is 300; confirm the first is play time and the second includes menus, or align them. Every reward key in the loops (`pebbles`, `coins`, `stars`, `gems`, `runes`, `shells`) should exist as a currency or resource; `pebbles` is an in-run resource and is a good candidate to list explicitly.

Progression: two tracks. `keep_restoration` uses a linear curve (base 12, growth 4, so area n needs 12 + 4(n-1) stars) with unlocks at 1, 2, 3 and 5. `family_level` uses an exponential curve (base 100, growth 1.6). Difficulty is a sawtooth with a hard level every tenth, a target win rate of 0.72, and a dynamic-difficulty rule with stated bounds (never on the first levels, at most two steps). Each of these is a number a simulator can read.

FTUE has four steps with `max_seconds` budgets (8, 12, 20, 90) teaching `tap_spawn`, `drag_merge`, the power idea and the meta loop. The first three sum to 40 seconds, inside the 45-second aha target; that arithmetic is the check.

Technical: `architecture: sim-core+presentation`, deterministic simulation, and perf budgets (60 fps target, 16.6 ms p95 frame, 450 MB memory, 150 MB download, 5 s cold start) that later appear in the perf report's `budgets`.

## 4. Mechanic cards: the stand-alone form

`example.mechanic-card.json` is `merge_two`, the same mechanic that appears in compact form inside the contract. The card adds what the contract omits: `player_fantasy` ("Turning clutter into power"), full `dynamics` (board pressure, holding pattern, family focus, snowballing), `aesthetics` (challenge, sensation, expression, submission, in priority order), `failure_modes` with detection signals, and `mobile_fit`.

Things to copy:

- **Parameter notes contain arithmetic.** `max_tier` 7 notes that reaching tier n takes 2^(n-1) tier-1 items, so 64 for tier 7. `tier_power_multiplier` 1.9 has a range of 1.6 to 2.4 and a note explaining why under 2.0 a merge trades total power for space.
- **Every failure mode names how to detect it.** "Board clog from unlucky spawns: detect with bot runs reporting the share of runs with a full board and no legal merge." A failure mode without a detector cannot be tested.
- **Mobile fit is specific**: cells of at least 48 pt, atomic merges so interruptions lose nothing, one thumb in portrait.
- **References are real titles**, which helps the reviewer reproduce the design intent.

The contract's `spawn_bag` shows the same discipline in the compact form: four parameters (starting pebbles, base cost, cost step, cost cap) each with a range and a note saying why.

## 5. Economy model: resource flow in numbers

The economy example has three archetypes (casual 0.70, engaged 0.25, payer 0.05; shares sum to 1), eight resources, ten nodes, a sawtooth difficulty block, four offers and targets.

Pattern recognition on the nodes:

| Node | Kind | Machinations-style reading |
|---|---|---|
| `win_reward`, `loss_consolation`, `daily_chest`, `ad_double_coins` | `source` | Faucets at different triggers (`per_level_win`, `per_level_loss`, `daily`, `on_ad`) |
| `rune_sort_bonus` | `source` with `probability: 0.2` | A dice-gated source modelling "every fifth level" as a 1-in-5 chance |
| `restore_task` | `converter` | Stars become restoration points when `stars >= 3` |
| `area_complete` | `gate` | 12 restore points open an area and pay gems |
| `family_upgrade` | `converter` | Coins and runes become family levels, a flat approximation of the contract's exponential curve, as the node's note says |
| `revive_gems` | `sink` with `probability: 0.15` | A drain triggered on a loss, taken in 15 percent of losses |
| `piggy_fill` | `pool` | Fills a capped resource (150) that an offer releases |

What a reviewer checks:

- Every contract currency (`coins`, `gems`, `stars`, `runes`, `shells`) should have a model resource; `shells` is an event currency and the example model carries a baseline only, so the live event would be a delta (section 3).
- Notes that call out approximations are a feature: they tell the next person which parts of the contract the model does not yet cover.
- `targets` state the success tests: 21 days to complete content, no more than 3 days of soft-currency hoarding, 2 percent payer conversion. Simulation output is judged against these, not against taste.

Run the simulator (see `economy-design` for options):

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/economy_sim.py --help
```

## 6. Level spec: one unit of content

`example.level-spec.json` is `bonus_005`, a Rune Sort puzzle: five colours by four runes in seven tubes, two empty, capacity four. Reading it as a level designer:

- `teach: "reward"` marks it as the breather beat; `difficulty_target.win_rate` is 0.9 with `attempts_p50` 1.
- `moves_or_time_limit: {"moves": 30}` against `solver.min_moves` 13 is about 2.3 times the optimum, so it plays as a breather. The notes record this ratio, and that the winning bot runs had a median of 16 moves.
- The `solver` block records `solvable: true`, `bot_win_rate` 0.97 over 200 runs, the algorithm (BFS), the number of states visited and a description of the bot. A level that ships without such a block is unverified.
- The extra solver keys (`algo`, `states_visited`, `bot`) show that the schema allows additional detail.

Checks to apply to any level spec: the limit is at least `min_moves`; the bot win rate is consistent with `difficulty_target.win_rate` (0.97 against a target 0.9 means a bit easier than intended, a bot being a rough proxy for humans); the `mechanic_refs` all exist in the contract.

## 7. Event taxonomy: how the game reports itself

The example defines `snake_case` events across the categories ftue, progression, economy, ads, monetization, liveops, ux and tech: `tutorial_begin`, `tutorial_step`, `tutorial_complete`, `level_start`, `level_end`, `earn_virtual_currency`, `spend_virtual_currency`, `restore_task_complete`, `rv_offer_shown`, `rv_completed`, `iap_purchase_completed`, `liveops_event_progress`, `settings_changed`, `perf_sample`. Common params (`session_id`, `build`, `player_level`, `ab_cohort`) attach to every event and count toward the parameter limit.

Link each event to the layer it measures: the FTUE events measure the FTUE steps in the contract; `level_end` measures difficulty against `target_win_rate`; the economy pair measures sources and sinks against the economy model; `rv_*` measure the revive and ad loops. A taxonomy where an event cannot be tied to a contract field or a KPI is noise; an economy node with no event is blind. See `player-analytics`.

## 8. Features: delivery through the five gates

The features example has 14 features in mixed states, which makes it a good picture of the gate rules.

| Feature | State | What it teaches |
|---|---|---|
| F001 sim core (tech, P0) | done, `passes: true`, playthrough and visual `n/a`, others `pass` | A pure-logic feature legitimately skips two gates, with notes explaining why |
| F002 spawn and merge | done, all five gates pass, depends on F001 | The normal complete case, with evidence for every pass |
| F004 hearts and results screen | `in_progress`, `playthrough: "fail"`, visual and perf null | A failing gate keeps the feature open; `passes` stays false |
| F005 FTUE | `todo`, all gates null, depends on F002, F003, F004 | Dependencies chain; `gs.py feature next` will not offer it before they pass |
| F008 economy wired to model | `blocked` | `status` records a blocker, details go in `notes` |
| F010 analytics taxonomy | done | Data features are features too |

Rules recap: `done` implies `passes: true`; `passes: true` implies each gate is `pass` or `n/a`, each `pass` has an existing evidence path, each `n/a` has a note. Validate with `gs.py validate`, which applies the rules the schema cannot (file existence).

## 9. Config, assets and budget

- **Config** (`example.config.json`): Godot 4.5, iOS and Android, portrait, `tier: prototype`, an asset cap of 50 USD and a per-call cap of 2 USD, revenue figures at zero, a licence allowlist of `CC0-1.0`, `provider-commercial` and `handmade`, and provider choices per asset type.
- **Asset manifest** (`example.asset-manifest.json`): seven assets covering sprite, background, UI, sfx and music, in states `approved`, `rejected`, `candidate` and `placeholder`. The rejected variant stays recorded (rejections are information), the placeholder is flagged `placeholder: true` with `handmade` licence terms so it cannot ship by accident, and generated assets carry prompt, seed, params, licence terms, `commercial_ok`, restrictions and cost. A sprite derived from another lists `derived_from`.
- **Budget** (`example.budget.json`): cap 50, spent 0.42, with ledger entries whose costs sum to exactly 0.42. A mock-provider call is recorded at cost 0 so the ledger is a full history. Invariant to verify after every call: spent equals the sum of the ledger.

## 10. Playtest and perf reports: evidence

**Playtest** (`example.playtest-report.json`): a deterministic script for F002 with seed 1, simulated time in seconds, steps each carrying an `action`, an `expect` and the `observed` state, with `ok` flags. Metrics report win rate 1.0 over one run, zero softlocks, crashes and errors. Two findings (minor and polish) exist alongside a `pass` verdict: findings and verdicts are independent as long as nothing is a blocker or major. The notes explain that `t` is simulated time and that one step deliberately tests a rejection, a good practice: a playthrough should include a negative case.

**Perf** (`example.perf-report.json`): feature F009 on a low-tier Android device in a worst-case scenario (hard level, boss wave, full board, all effects). Frame-rate averages 58.7 with a 1 percent low of 41; p95 frame time 15.9 ms against a 16.6 ms budget (pass); peak memory 489 MB against 450 (fail); a violation entry names the cause (four uncompressed 2048 by 2048 particle atlases at 16 MB each) and the verdict is `fail`. This is the right shape: a failing report with a diagnosis is more valuable than a passing one without scenario detail, and it blocks the `perf` gate for F009 until fixed.

## 11. Deconstruction: reading someone else's game

`example.deconstruction.json` describes Royal Match using the same loop vocabulary: a core loop graph (start level, swap tiles, meet goals within moves, or run out and choose extra moves or failure), meta loops (`renovate`, `team`), mechanics with rules, dynamics and aesthetics (`match3_swap`, `powerup_creation`, `rescue_level`), monetization model `iap`, lessons and `borrow_for_us` actions, and `sources` as URLs. It carries an `as_of` date because such documents age.

What makes it useful rather than a summary:

- Loops use the same notation, so core loops of different games can be compared step by step.
- `lessons` are statements about design ("label difficulty spikes up front; surprise difficulty feels unfair"), and `borrow_for_us` turns each into an action for our contract (one star per win spent on visible restoration, with restoration unlocking something that feeds the core).
- Claims are sourced, and numbers that cannot be sourced are left out.

Procedure and quality bar for new deconstructions are in `deconstruct`; the case-study library is `game-case-studies`.

## 12. Cross-document consistency checks

Run these whenever two documents change together.

| Check | Documents | How |
|---|---|---|
| Every loop reward key is a resource | contract loops vs economy | List reward keys; compare to `resources[].id` |
| Every contract currency has sources and sinks in the model | contract economy vs economy model | For each currency, find nodes producing and consuming it |
| Contract `perf_budgets` equal the perf report `budgets` | contract vs perf | Diff the two objects |
| `kpi_targets` match event coverage | contract analytics vs taxonomy | Each KPI has events that can compute it |
| Level `mechanic_refs` exist | level specs vs contract | Check ids |
| Feature acceptance criteria trace to contract rules | features vs contract | Each rule has a feature |
| FTUE step budgets sum to the aha target | contract | Add `max_seconds` of steps before the aha |
| Asset licences within allowlist | manifest vs config | Terms in `licence_allowlist` or flagged for review |

## 13. Exercise: add a new mechanic end to end

Add a "shuffle" power-up to Pebble Keep, following the document chain.

1. **Classify** it (section 12 of the overview): new verb (`tap_shuffle`) and a mechanic with cost, so also an economy node (a sink).
2. **Card**: write `shuffle.mechanic.json` with rules (reshuffles all board positions, keeps tiers, costs `shuffle_cost` gems, limited per run by `shuffle_cap`), parameters with ranges and notes, dynamics (players use it to escape clogs; a degenerate strategy is shuffling for merge adjacency every wave), aesthetics (challenge, submission), failure modes with detectors, mobile fit.
3. **Contract**: add the verb and the compact mechanic, link it from the core loop description, and add a pillar check (does it break "readable chaos"?).
4. **Economy**: add a `sink` node triggered `per_level_attempt` with a probability for usage and a guard condition; re-run the simulation and compare gem sinks to sources.
5. **Features**: add `F015` with area `gameplay`, acceptance criteria per rule, `depends_on: ["F002"]`.
6. **Telemetry**: add an event (`shuffle_used`) with params (`level_id`, `cost_gems`, `board_state_clogged` as bool).
7. **Validate**: `gs.py validate` for the project and `validate_json.py --auto` for each new file.
