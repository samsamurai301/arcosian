# Loops, flows and MDA in practice

This file turns the ontology's time and flow dimensions into working procedures: how to write a loop so a machine and a human can both read it, how to health-check one, how Machinations-style resource primitives (Adams and Dormans) map onto the `economy-model` node kinds, how to apply MDA and the DDE extension, how to write rules and parameters that an engineer can implement without a meeting, and how to fill in a mechanic card. Every JSON block here was validated with `validate_json.py`. Use it when drafting or reviewing loops, mechanics or economy skeletons.

## Contents
1. Loop notation
2. Loop health checks
3. A worked loop graph (validated JSON)
4. Resource flow primitives and the economy-model mapping
5. Reading a flow diagram: stability, feedback, runaway
6. A mini economy model (validated JSON)
7. MDA applied: working in both directions
8. DDE: design, dynamics, experience
9. Writing precise rules
10. Tunable parameters: ranges, notes, units
11. Mechanic cards: procedure and template (validated JSON)
12. Review checklist

## 1. Loop notation

### 1.1 Prose form (for concepts and chat)

One line, arrows between verbs and rewards, `*` for the repeat point:

```
spawn -> merge -> defend -> earn -> (back to spawn)*
```

Use it in concept cards (`core_loop` accepts a plain string) and in pitches. It is a sketch, not a spec.

### 1.2 Graph form (for contracts and deconstructions)

A loop is `{id, name?, type, period, description?, steps[]}`. Each step is `{id, action, reward, next}`.

| Field | Rule |
|---|---|
| `id` on the loop | Short and stable (`core`, `meta_restore`). Other loops refer to it |
| `type` | `core`, `meta`, `social`, `monetization`, `liveops` |
| `period` | `seconds`, `minutes`, `session`, `daily`, `weekly`, `season`. The time for one full turn of the loop for a typical player |
| step `action` | A verb phrase the player (or the system on their behalf) performs. Concrete: "drag a unit onto an equal unit", not "engage with merging" |
| step `reward` | `null` (no reward at this step, which is legitimate), a string (qualitative), or an object of resource amounts (`{"coins": 40}`). Prefer objects when the reward is a currency, because simulators and the economy model can cross-check them |
| step `next` | A step id, a list of step ids (branching), `"loop:<id>"` (hand-off to another loop), or `null` (end) |

Branching represents real player choice or an outcome fork (win or lose). A list of two or more targets should correspond to a decision or a probabilistic result; if it is neither, merge the paths.

### 1.3 Annotating periods

A loop's `period` is the full-turn time. Put the arithmetic in `description` when it is not obvious: "A level takes 3 minutes, a star per win, 3 stars per task: a task every 9 minutes of winning play." This is what lets a reviewer check the loop against the session length.

## 2. Loop health checks

Run these on every loop before it enters a contract. Each has a detection method.

| # | Check | Pass condition | How to detect |
|---|---|---|---|
| 1 | Closure | Following `next` from the first step returns to a step already visited, or hands off to another loop that eventually does | Walk the graph; a `null` end on the core loop is a defect (the player hits a dead end) |
| 2 | Reward within period | A reward of some kind appears at least once per turn | Count steps with non-null `reward` |
| 3 | Reward cadence | Time between rewards is at most about one third of the loop period at the core level | Estimate seconds per step; flag stretches over the target |
| 4 | Decision present | At least one step offers a meaningful choice (two or more branches, or a parameterised action with trade-offs) | Look for branching `next` or a step that spends a resource |
| 5 | Input matches output | Everything spent in the loop is earned somewhere in the loop or a linked loop | Compare `reward` resources against the economy sinks; unmatched means leak or starvation |
| 6 | Escalation | Each turn is not identical: something grows, unlocks or changes | Check for a progression link (unlock, tier, level) |
| 7 | Exit and re-entry | The player can leave at a natural point and resume without penalty | Is there a step marking a safe end? Mobile interruptions make this mandatory |
| 8 | Linked | Core loop hands off to a meta loop; the meta loop returns to the core | Search for `loop:` references in both directions |
| 9 | Period consistency | Core loop period times about three is at most the session length | `3 * core_period <= session_length_target_sec` |
| 10 | No orphan reward | Every reward object key exists as a resource id | Compare to `economy.currencies[].id` and `resources[].id` |

Typical failures and their meaning:

- Closed but boring: checks 1 to 3 pass, 4 fails. The loop is a treadmill; add a decision.
- Decisions but no pull: check 2 fails. Add rewards or shorten the period.
- Everything passes but retention is poor: check 6 fails; the loop is a plateau. See `progression-difficulty`.

## 3. A worked loop graph

A core loop that hands off to a meta loop, with a mechanic and two verbs (design-contract subset; validated).

```json
{
  "schema_version": "1.0",
  "meta": { "title": "Loop Notation Demo" },
  "verbs": [
    { "id": "tap_spawn", "input": "tap", "description": "Spend energy to place a unit." },
    { "id": "drag_merge", "input": "drag", "description": "Fuse two equal units." }
  ],
  "loops": [
    {
      "id": "core",
      "name": "Spawn, merge, defend",
      "type": "core",
      "period": "seconds",
      "steps": [
        { "id": "s1", "action": "tap to spawn a tier-1 unit", "reward": null, "next": "s2" },
        { "id": "s2", "action": "drag a unit onto an equal unit", "reward": "stronger unit", "next": "s3" },
        { "id": "s3", "action": "units defeat the wave", "reward": { "energy": 3 }, "next": ["s1", "s4"] },
        { "id": "s4", "action": "clear the final wave", "reward": { "coins": 40, "stars": 1 }, "next": "loop:meta_restore" }
      ]
    },
    {
      "id": "meta_restore",
      "type": "meta",
      "period": "session",
      "steps": [
        { "id": "m1", "action": "spend stars on a restoration task", "reward": "a visible repair", "next": "loop:core" }
      ]
    }
  ],
  "mechanics": [
    {
      "id": "merge_two",
      "name": "Merge-two upgrade",
      "category": "merge",
      "verbs": ["drag_merge"],
      "rules": ["Two units of equal family and tier fuse into one unit of tier + 1 on the target cell."],
      "parameters": [
        { "key": "tier_multiplier", "value": 1.9, "min": 1.6, "max": 2.4, "unit": "x", "note": "Power of tier n+1 over tier n." }
      ]
    }
  ]
}
```

Reading it against the checks: s1 has a null reward (fine, the spawn is the cost), s2 gives a qualitative reward, s3 branches (keep spawning or finish: a real decision about when to spend), s4 hands off. Check 10 flags that `energy`, `coins` and `stars` must exist as resources in the economy; the contract's `economy.currencies` should list them.

## 4. Resource flow primitives and the economy-model mapping

Adams and Dormans (Game Mechanics: Advanced Game Design, 2012) describe a visual language, later productised as Machinations, in which games are networks of nodes that move resources along connections. Summarised in my own words, the primitives most useful here are:

- **Source**: creates resources from nothing (the world gives you something).
- **Drain**: destroys resources (spent and gone).
- **Pool**: stores resources and can have a capacity.
- **Converter**: consumes one kind of resource and produces another.
- **Gate**: routes or blocks flow based on a condition or probability.
- **Trader**: swaps resources between two parties at a ratio.
- **Delay**: holds resources for a time before releasing them.
- **Register**: shows a value (a derived number) without moving resources.
- Connections can be **pull** (the target takes when it can) or **push** (the source sends); some are modified by dice or by the state of another element (**state connections**, **modifiers**, **triggers**).

Mapping to the `economy-model` schema (`nodes[].kind` is one of `source`, `sink`, `converter`, `gate`, `pool`):

| Machinations-style primitive | `kind` | How to encode it | Note |
|---|---|---|---|
| Source | `source` | `outputs: {res: amount}`, a `trigger`, optional `probability` | A level win paying 40 coins is a source triggered `per_level_win` |
| Drain | `sink` | `inputs: {res: amount}`, a `trigger`, optional `condition` | The schema calls drains "sinks" |
| Pool | `pool` | A `resources[]` entry with `cap`, plus a `pool` node that feeds it | The cap lives on the resource, the filling on the node |
| Converter | `converter` | Both `inputs` and `outputs` | Crafting, upgrades and stars-to-progress conversions |
| Gate | `gate` | `condition` plus `inputs` and `outputs` describing what passes | A threshold gate: "12 restore points open an area" |
| Trader | two nodes or an `offers[]` entry | An offer swaps USD for resources; an in-game exchange is a converter | The schema keeps real-money trades in `offers` |
| Delay | `trigger` choice | Use `per_minute`, `daily` or `weekly` timing, or a `condition` on a timer variable | No dedicated delay node: model the wait as the trigger period |
| Register | not modelled | Derived numbers go in `targets` or in a report | The sim reports them; they are not nodes |
| Random gate / dice | `probability` | Ratio from 0 to 1 on the node | A 1-in-5 bonus is `probability: 0.2` |
| Pull vs push | implicit | All nodes pull when their trigger fires and the condition holds | Document special push behaviour in `note` |

Triggers (`nodes[].trigger`): `per_session`, `per_minute`, `per_level_attempt`, `per_level_win`, `per_level_loss`, `daily`, `weekly`, `on_purchase`, `on_ad`. The trigger is the event that causes the node to fire; the condition is a guard evaluated at that moment. Keep conditions to comparisons of resource ids and simulator variables (`day`, `level`, `session`) joined with `and` and `or`; `economy_sim.py` defines the exact grammar.

## 5. Reading a flow diagram: stability, feedback, runaway

A resource network has feedback structure. Learn to recognise three shapes.

**Balancing feedback.** The more you have, the more you lose or the less you gain. Example: spawn cost that rises per spawn in a run. It stabilises behaviour. Healthy economies have several.

**Reinforcing feedback.** The more you have, the more you gain. Example: units that kill faster earn more energy, which buys more units. It produces snowballs and comebacks that never come. Use it deliberately and cap it (a board cell limit, a wave timer, a resource cap).

**Runaway.** A reinforcing loop with no sink or cap. Detection signal in simulation: a resource curve that is convex for the whole horizon. Fix: add a drain proportional to the stock, add a cap, or add a gate that converts the surplus into something finite.

Quick audit per resource, answering each in one sentence:

1. What are its sources and their rates per session?
2. What are its sinks and their rates?
3. Net flow per session for each archetype (casual, engaged, payer)?
4. Where does the surplus go when sources exceed sinks (hoard, cap, decay)?
5. What does the player do when it hits zero? (Starvation needs a recovery path.)

Rules of thumb (hedged): a soft currency should have at least one sink that absorbs the average player's income each session, otherwise hoarding days grow without bound; `targets.max_soft_currency_hoard_days` exists to make that explicit. A resource with a source and no sink is a counter, not an economy.

## 6. A mini economy model

A small, validated model illustrating each node kind (economy-model schema).

```json
{
  "schema_version": "1.0",
  "name": "Machinations mapping demo",
  "days": 14,
  "archetypes": [
    { "id": "casual", "share": 0.8, "sessions_per_day": 3, "session_minutes": 4, "skill": 0.5, "spend_propensity": 0.01, "ad_accept_rate": 0.3 },
    { "id": "engaged", "share": 0.2, "sessions_per_day": 5, "session_minutes": 6, "skill": 0.7, "spend_propensity": 0.04, "ad_accept_rate": 0.5 }
  ],
  "resources": [
    { "id": "coins", "initial": 100, "cap": null },
    { "id": "stars", "initial": 0, "cap": null },
    { "id": "tasks_done", "initial": 0, "cap": 40 },
    { "id": "piggy", "initial": 0, "cap": 150 }
  ],
  "nodes": [
    { "id": "win_reward", "kind": "source", "trigger": "per_level_win", "outputs": { "coins": 40, "stars": 1 } },
    { "id": "daily_chest", "kind": "source", "trigger": "daily", "outputs": { "coins": 100 } },
    { "id": "restore_task", "kind": "converter", "trigger": "per_session", "inputs": { "stars": 3 }, "outputs": { "tasks_done": 1 }, "condition": "stars >= 3" },
    { "id": "upgrade_tax", "kind": "sink", "trigger": "per_session", "inputs": { "coins": 250 }, "condition": "coins >= 250" },
    { "id": "piggy_fill", "kind": "pool", "trigger": "per_level_win", "outputs": { "piggy": 3 } },
    { "id": "unlock_world2", "kind": "gate", "trigger": "per_session", "inputs": { "tasks_done": 12 }, "condition": "tasks_done >= 12" }
  ],
  "levels": { "count": 40, "base_win_rate": 0.8, "difficulty_curve": { "type": "sawtooth", "params": { "period": 10, "floor": 0.5 } } },
  "offers": [ { "id": "starter", "price_usd": 1.99, "contents": { "coins": 1500 }, "trigger": "level >= 6" } ],
  "targets": { "days_to_complete_content": 21, "max_soft_currency_hoard_days": 3, "payer_conversion": 0.02 }
}
```

Hand check, no simulator needed: assume a casual player plays 3 levels a day and wins about 65 percent of them. Daily coin income is about 3 x 0.65 x 40 + 100 = 178, and stars about 2 per day. The `upgrade_tax` sink needs 250 coins, so it fires roughly every 1.4 days, which absorbs income at about the rate it arrives; a design where income is 3x the sink would hoard. That arithmetic is what the simulator repeats across archetypes and days. Run it:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_json.py --auto path/to/mini.economy.json
```

Then use the `economy-design` skill for simulation and balancing.

## 7. MDA applied: working in both directions

The MDA paper by Hunicke, LeBlanc and Zubek (2004) separates the designer's view (mechanics, then dynamics, then aesthetics) from the player's view (aesthetics, then dynamics, then mechanics). The practical use is a worksheet with four columns.

| Aesthetic target (in priority order) | Dynamics that would deliver it | Mechanics that enable those dynamics | Signal that it works |
|---|---|---|---|
| Challenge | Board pressure forces choices under time | Finite cells, rising spawn cost | Win rate 60 to 80 percent on mid levels, high retry rate |
| Expression | Players invent holding patterns and family focus | Optional merges, several families | Varied loadouts in telemetry |
| Submission | Low-stakes rhythm between peaks | Short waves, Rune-Sort-style bonus levels | Long sessions with low error rates |

Procedure:

1. Write the aesthetic list first, max three, from the eight words.
2. For each, write the dynamics you predict (not hope for) and one counter-dynamic that would undermine it.
3. For each dynamic, choose or alter mechanics and set initial parameters with ranges.
4. Define the signal: a telemetry event, a bot metric, or a persona playtest question.
5. Prototype the smallest build that can show the dynamics, and read the signals.

Aesthetics mismatch is the most common root cause of "polished but dull": the mechanics deliver challenge and the audience wants submission.

## 8. DDE: design, dynamics, experience

Walk, Goerlich and Barrett extended MDA into DDE (Design, Dynamics, Experience) in a paper published around 2017 (verify the exact citation before quoting it): the designer's artefacts (rules, content, tuning) interact with the player's behaviour to yield dynamics, which in turn yield the experience; and the player's experience feeds back into what they do next. In my words, the extension adds two ideas the original lacks: the loop closes (experience changes behaviour, which changes dynamics), and "design" includes content, tuning and presentation, not only rules.

How to use it here:

- When a mechanic card lists `dynamics`, add the feedback path: "if X feels unfair, players stop doing Y". That sentence is a failure mode.
- Treat tuning (`parameters`) and content as first-class design inputs: the same rules with different numbers produce different dynamics.
- Plan measurement per arrow: design to dynamics (bot runs, telemetry), dynamics to experience (surveys, persona playtests, retention).

## 9. Writing precise rules

A rule is precise when two engineers implementing it independently get the same behaviour. Checklist:

| Check | Bad | Good |
|---|---|---|
| Names the trigger | "Units merge" | "When a unit is dropped onto another unit of the same family and tier, ..." |
| States preconditions | "Spawn a unit" | "Spawn is disabled when the board is full or energy is below spawn_cost" |
| States the effect fully | "Becomes stronger" | "Becomes one unit of tier + 1 on the target cell; the origin cell is freed" |
| Covers the failure path | (silent) | "An invalid drop returns the unit to its origin cell with no penalty" |
| Uses parameters, not numbers | "costs 10" | "costs spawn_cost_base, rising by spawn_cost_step per spawn" |
| Specifies order | "then the wave moves" | "Merges resolve before the wave tick in the same frame" |
| Specifies randomness | "random cell" | "uniform over empty cells, seeded from the run seed" |
| One rule per line | A paragraph | Numbered sentences, each testable |

Edge cases to ask about every rule: what if it is simultaneous with another rule, what if the resource is zero, what if the board is full or empty, what if the player is interrupted mid-action, what if the same input arrives twice.

Test: each rule should map to one unit test or one assertion in a scripted playthrough. A rule you cannot test is a wish.

## 10. Tunable parameters: ranges, notes, units

Every number in a rule becomes a parameter `{key, value, min, max, unit, note}` (common.schema.json `parameter`).

- `key` is an id (`snake_case`).
- `value` is the shipped default (number, string, boolean or null).
- `min` and `max` bound safe tuning: balance tools and remote config stay inside them. Choose bounds from where the design breaks, not from where you feel comfortable.
- `unit` is explicit (`x`, `s`, `pebbles`, `cells`, `ratio`). Never leave a bare number.
- `note` explains the trade-off and what happens at each edge ("below 2.0 a merge trades power for space"), and when the value is untested, say so ("confirm in playtests").

Parameter hygiene:

1. One concept per parameter; do not encode two effects in one number.
2. Prefer ratios and multipliers over absolute numbers when the quantity scales with progression.
3. Record the dependency when two parameters interact (spawn cost and starting energy together set time to the first merge).
4. Name derived quantities in the note with the formula: "Reaching tier n takes 2^(n-1) tier-1 units".
5. Expose to remote config only parameters with sane bounds and a rollback.

## 11. Mechanic cards: procedure and template

A mechanic card (`mechanic-card.schema.json`) is the stand-alone form of a mechanic. Procedure:

1. **Name and category**: pick from the suggested vocabulary (movement, aiming, timing, placement, merge, match, sort, physics, combat, resource, construction, chance, collection, progression, social, narrative, puzzle, economy).
2. **Player fantasy**: one sentence, from the player's side.
3. **Verbs**: ids or full verb objects.
4. **Rules**: numbered, precise (section 9).
5. **Parameters**: with ranges and notes (section 10).
6. **Dynamics**: predicted emergent behaviours, including one degenerate strategy.
7. **Aesthetics**: from the enum, most important first.
8. **Feedback**: visual, audio, haptic and numeric responses.
9. **Failure modes**: each with a detection signal and a fix.
10. **Mobile fit**: `one_hand` (boolean), `session_fit`, `notes` (target sizes, interruption behaviour).
11. **References and combos**: real titles; ids of mechanics that combine well.

Template (validated):

```json
{
  "schema_version": "1.0",
  "id": "spawn_bag",
  "name": "Spawn from a shuffled bag",
  "category": "chance",
  "player_fantasy": "A fair hand of surprises: variety without droughts.",
  "verbs": ["tap_spawn"],
  "rules": [
    "Spawn places a tier-1 unit on a random empty cell; disabled when the board is full or energy is short.",
    "The family is drawn from a bag holding each of the 5 families once; the bag refills when empty."
  ],
  "parameters": [
    { "key": "bag_size", "value": 5, "min": 3, "max": 8, "unit": "families", "note": "Longest possible drought is 2 * bag_size - 2 spawns." }
  ],
  "dynamics": ["Players plan around a known maximum drought and hold pairs for the family they are due."],
  "aesthetics": ["challenge", "expression"],
  "feedback": ["Spawn button pulses when affordable"],
  "failure_modes": ["Board clog from unlucky positions: detect with bot runs reporting share of runs with a full board and no legal merge."],
  "mobile_fit": { "one_hand": true, "session_fit": "short", "notes": "Button in the bottom thumb zone." },
  "references": ["Tetris (piece bag)"],
  "combos": ["merge_two"]
}
```

Check on the drought formula: with a bag of n distinct families refilled when empty, the worst gap between two draws of the same family is when it is drawn first in one bag and last in the next, which is 2n - 1 draws apart, so at most 2n - 2 draws between them (n = 5 gives 8). Always do this kind of arithmetic in the note; it makes the number defensible.

Save cards as `*.mechanic.json` and validate:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_json.py --auto spawn_bag.mechanic.json
```

## 12. Review checklist

- [ ] Every loop passes the ten health checks, or the exceptions are stated.
- [ ] Every reward resource exists in the economy.
- [ ] Every sink has a matching source family, and every source has a sink or cap.
- [ ] Every rule is one testable sentence; every number is a parameter with a range.
- [ ] Each aesthetic has at least one predicted dynamic and one measurement.
- [ ] Core period times three fits the session length.
- [ ] Documents validate (`validate_json.py --auto`, or `gs.py validate`).
