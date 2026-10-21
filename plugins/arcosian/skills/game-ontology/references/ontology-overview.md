# Ontology overview: one vocabulary for every game

This file defines the layered model that every Arcosian document uses to describe a game, from the player's motivation at the top to the entities and resources at the bottom. It explains what each layer means, how the layers constrain each other, what loops, flows, content, sessions and live-ops add on top, and which schema field carries each concept. Read it first when you need to describe a game, deconstruct one, or decide where a piece of information belongs. The goal is that two agents who have never spoken produce documents that can be diffed, validated and fed to simulators.

## Contents
1. Why an ontology at all
2. The layered model
3. Layer by layer (definition, test question, schema home)
4. Direction of causation: design down, observe up
5. Loops: the time dimension
6. Flows and pacing
7. Content: levels, worlds, characters
8. Sessions and the day
9. Live-ops and the season
10. Mapping layers to schemas (table)
11. Naming and id conventions
12. Classifying a feature request in 60 seconds
13. Common confusions

## 1. Why an ontology at all

A game design is normally scattered across a pitch deck, a spreadsheet, a few Slack threads and the lead designer's head. Agents cannot work from that. They need a closed vocabulary, a place for every fact, and machine-checkable shapes. The ontology gives three things.

- **A decomposition**: any game, from Tetris to a live-service RPG, can be described as the same stack of layers. Missing layers are visible, which is the single most useful diagnostic ("we have mechanics and no stated aesthetics").
- **A routing table**: each layer has an owner skill and a schema field, so a question like "where do I record that spawn cost rises per spawn" has one answer (a mechanic parameter, with a range).
- **A test surface**: parameters have ranges, loops have steps, resources have sources and sinks. Simulators (`economy_sim.py`, `difficulty_curve.py`) and gates read those fields instead of prose.

The model is deliberately a synthesis. The top half follows the MDA framework by Hunicke, LeBlanc and Zubek (2004): mechanics produce dynamics, dynamics produce aesthetics. The bottom half borrows the entity-and-rule thinking common in system-design practice. Loops and economy primitives follow Adams and Dormans, "Game Mechanics: Advanced Game Design" (2012), which treats games as networks of resource flows.

## 2. The layered model

```
PLAYER            who plays, with what motivations and constraints
  |
MOTIVATION        why they start and why they return (competence, autonomy, relatedness, ...)
  |
AESTHETICS        the target experience, in the eight MDA words
  ^                 (what the player feels)
DYNAMICS          emergent behaviour in play: strategies, tensions, rhythms
  ^                 (what happens when systems run with a player in them)
MECHANICS         rule bundles with tunable parameters
  ^                 (what the designer specifies)
VERBS + RULES     what the player can do, and what the world does back
  ^
ENTITIES          things that exist: units, tiles, items, characters
RESOURCES         quantities that flow: coins, energy, health, time, moves
```

Two orthogonal dimensions cross every layer:

- **Time**: loops (seconds to season), sessions, the day, the season. Each layer repeats at some period.
- **Content**: levels, worlds, characters, items, events, the stuff the rules process.

Arrows: the designer works from the bottom up (specify entities, rules, parameters) but decides from the top down (pick the aesthetic target first, then the dynamics that produce it). Players experience the reverse: they feel aesthetics, notice dynamics, and only later infer mechanics.

## 3. Layer by layer

### 3.1 Player

Who the game is for, expressed as a short list the rest of the stack can be checked against: `age_min`, segments (a behavioural description, not a demographic cliche), and motivations. Include hard constraints that bind the lower layers: one hand, two-minute sessions, no sound.

- Test question: could a stranger pick three specific people who match this, and would one of them dislike the core loop?
- Schema: `meta.target_audience {age_min, segments, motivations}` in the contract; `target_audience` in a concept card.

### 3.2 Motivation

Why a segment starts and returns. The studio uses self-determination theory language (competence, autonomy, relatedness; Ryan and Deci) plus a few game-specific drives (completion, collection, expression, mastery, social comparison). Motivation is not stored as a separate object; it appears as the `motivations` list and drives which loops exist.

- Test question: for each loop, which motivation does its reward serve? A loop that serves none is decoration.
- Schema: `meta.target_audience.motivations`; per-loop rationale in `loops[].description`.

### 3.3 Aesthetics

The target experience, using the eight words from the MDA paper: sensation, fantasy, narrative, challenge, fellowship, discovery, expression, submission. Order matters: most important first. A mechanic card lists its aesthetics as an enum array (`mechanic-card.schema.json`, `aesthetic`). A game usually has two or three dominant aesthetics; five means none.

- Test question: if a playtester describes the game in three words, are two of them in your list?
- Schema: `aesthetics` on a mechanic card and in deconstructed mechanics; `player_fantasy` (one sentence) and `meta.pillars` (3 to 5) in the contract.

### 3.4 Dynamics

Behaviour that is not written anywhere in the rules but appears when a player interacts with them. Examples: holding matching pairs to time a power spike; hoarding a soft currency; camping a choke point; rushing the first minute. Dynamics are hypotheses until observed. Record them as predictions on the card (`dynamics`) and confirm or refute them in playtests (`playtest-report.findings`).

- Test question: can you name one strategy a good player will adopt that a new player will not, and one degenerate strategy to guard against?
- Schema: `dynamics` on mechanic cards; `findings` in playtest reports; `weaknesses` in deconstructions.

### 3.5 Mechanics

A mechanic is a named bundle of verbs, rules and parameters that produces one coherent kind of decision. "Merge two equal items" is a mechanic; "merge" is a verb; "tier multiplier 1.9" is a parameter. The test of a good mechanic is that its rules fit on a card and an engineer can implement them without asking questions. See `references/loops-flows-and-mda.md` for the card procedure.

- Test question: can you state the rules as numbered sentences with no adjectives?
- Schema: `mechanics[]` in the contract (compact form); `mechanic-card.schema.json` (full form, adds fantasy, dynamics, aesthetics, failure modes, mobile fit, references, combos).

### 3.6 Verbs and rules

Verbs are the atomic player inputs mapped to intent: tap-to-spawn, drag-to-merge, swipe-to-aim. Rules are what the system does in response, including constraints and win/lose conditions. Keep the core verb set at one to three for casual mobile (the schema's own description says so). Each verb has an `input` (tap, drag, swipe, hold, tilt, text, ...) and a one-line `description`.

- Test question: if you removed this verb, would any loop break? If not, cut it.
- Schema: `verbs[]` with `{id, input, description}`; mechanics reference verbs by id (`verbs: ["drag_merge"]`).

### 3.7 Entities and resources

Entities are things with identity and state (a golem with a tier and a family; a tile with a colour). Resources are interchangeable quantities (coins, energy, moves, time). The distinction matters for economy modelling: only resources appear in `economy-model.schema.json`; entities appear in level layouts and asset manifests.

- Test question: do two of them have to be told apart? Then it is an entity. Otherwise a resource.
- Schema: `resources[]` in the economy model (`id`, `initial`, `cap`); `economy.currencies[]` in the contract (adds `kind`, `sources`, `sinks`); asset entries for entity art.

## 4. Direction of causation: design down, observe up

| Direction | Question | Example |
|---|---|---|
| Top-down (design) | "We want challenge and expression. Which dynamics produce them? Which mechanics enable those dynamics?" | Challenge + expression suggests board pressure and optional holding of pairs, hence a merge board with a finite cell count |
| Bottom-up (analysis) | "Players hold pairs. Which rule makes that rational? Which aesthetic does it serve?" | The tier multiplier is under 2, so merging costs power; holding times spikes |
| Diagnosis | "Players report boredom. Which layer failed?" | Aesthetics unstated (nobody knows the target), dynamics absent (one dominant strategy), mechanic parameters mis-tuned, or loop reward too slow |

Rule of thumb: a symptom reported at layer N is usually caused at layer N-1 or N-2. "The game feels flat" (aesthetics) is usually a dynamics problem (no tension) caused by a parameter (costs too low to matter).

## 5. Loops: the time dimension

A loop is a cycle of player action, system response, reward and a reason to act again. Loops nest by period.

| Loop type (`loops[].type`) | Typical `period` | Job |
|---|---|---|
| `core` | `seconds` or `minutes` | The moment-to-moment pleasure. If this is not fun, nothing else matters |
| `meta` | `session` | Gives each session a purpose beyond the level: collection, upgrade, restoration |
| `social` | `daily` or `weekly` | Relatedness: gifting, teams, leaderboards |
| `monetization` | `minutes` or `session` | Offers, continues, ad placements, framed as optional loops |
| `liveops` | `weekly` or `season` | Fresh reasons to return: events, seasons, passes |

Loops link to each other through steps whose `next` is `"loop:<id>"`. The core loop's reward step typically points to a meta loop; the meta loop's last step points back to `loop:core`. A loop graph with no inbound edge from another loop and no exit is an island; flag it. Notation and health checks are in `references/loops-flows-and-mda.md`.

## 6. Flows and pacing

"Flow" has two senses and both are used.

- **Experience flow** (Csikszentmihalyi): the balance between challenge and skill. In the ontology it appears as `progression.difficulty` (`model`, `target_win_rate`, `dda`) and level specs with `difficulty_target`.
- **Resource flow** (Adams and Dormans): quantities moving between sources, pools, converters, gates and sinks. In the ontology it appears as the economy model.

Pacing is the arrangement of intensity over time: teach, test, twist, reward. The level spec's `teach` field uses exactly those four beats. A good level sequence alternates them and never stacks two twists without a reward.

## 7. Content

Content is data the rules process: levels, worlds, characters, items, dialogue, events.

| Content kind | Contract field | Detail schema |
|---|---|---|
| Levels | `content.levels {target_count, generation, spec_ref}` | `level-spec.schema.json` (one file per level: layout, goals, limits, obstacles, difficulty target, solver result, teach beat) |
| Worlds | `content.worlds` (integer or list) | Narrative and art documents |
| Characters | `content.characters` (integer or list) | Narrative and art documents |
| Items and offers | `monetization.iap`, economy `offers` | Economy model |
| Events | `liveops.events` | Event calendar in `.gamestudio/` docs |

`generation` is `handmade`, `procedural` or `hybrid`. Choose it early: procedural content needs a validator (solver or bot) before it ships, so the level spec's `solver` block (`solvable`, `min_moves`, `bot_win_rate`, `runs`) is not optional for generated levels.

## 8. Sessions and the day

A session is one continuous stretch of play. The contract states `meta.session_length_target_sec` (10 to 7200 s). Everything about a session is derived from it:

- The core loop period must fit inside it at least three times for the session to feel like progress.
- The FTUE (`ftue.steps`, each with `max_seconds`) must reach the "aha" moment (`ftue.aha_seconds_target`) in the first session.
- The economy's `archetypes[]` carry `sessions_per_day` and `session_minutes`, so the number of daily loop iterations is computable.
- The daily loop (chests, streaks) belongs to the day, not the session; model it with a node whose `trigger` is `daily`.

A one-line check: `loops_per_session = session_seconds / core_loop_period_seconds`. If it is below three, the loop is too long for the session; if above about forty, the loop is probably too shallow to carry a session without escalation.

## 9. Live-ops and the season

Live-ops adds a third nesting level above the day: weekly events and seasonal arcs. In the ontology live-ops is a loop (`type: "liveops"`, `period: "weekly"` or `"season"`) plus event entries and a cadence string or object (`liveops.cadence`, `liveops.events`). Live-ops never changes the layers; it re-parameterises them (an event multiplies a source, adds a temporary resource, swaps a content set). Keep a rule: every live event must be describable as a delta on the base contract (new resource, changed node, new content), otherwise it is a new game.

## 10. Mapping layers to schemas

| Layer / concept | Contract field | Standalone schema | File pattern |
|---|---|---|---|
| Player, motivation | `meta.target_audience` | `concept` | `.gamestudio/concepts/*.concept.json` |
| Aesthetics | `player_fantasy`, `meta.pillars`; `aesthetics` on cards | `mechanic-card` | `*.mechanic.json` |
| Dynamics | `dynamics` on cards | `playtest-report` (observed) | `.gamestudio/playtests/*.playtest.json` |
| Mechanics | `mechanics[]` | `mechanic-card` | `*.mechanic.json` |
| Verbs, rules | `verbs[]`, `mechanics[].rules` | none | in contract |
| Entities | level layouts, assets | `asset-manifest`, `level-spec` | `.gamestudio/assets/manifest.json`, `*.level.json` |
| Resources, flows | `economy.currencies[]` | `economy-model` | `.gamestudio/economy/*.economy.json` |
| Loops | `loops[]` | (embedded) | in contract, concept, deconstruction |
| Progression, difficulty | `progression` | `level-spec` (targets) | in contract |
| Content | `content` | `level-spec` | `.gamestudio/levels/*.level.json` |
| Analytics | `analytics` | `event-taxonomy` | `.gamestudio/analytics/*.taxonomy.json` |
| Whole-game analysis | none | `deconstruction` | `.gamestudio/research/*.deconstruction.json` |
| Delivery status | none | `features` | `.gamestudio/features.json` |
| Quality evidence | none | `playtest-report`, `perf-report` | `playthrough.json`, `perf.json` |
| Project setup | none | `config`, `budget` | `config.json`, `budget.json` |

Field-by-field detail is in `references/schema-reference.md`.

## 11. Naming and id conventions

- Ids match `^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$`. Use `snake_case` for verbs, mechanics, resources and nodes (`drag_merge`, `piggy_gems`).
- Feature ids are `F` plus 3 or 4 digits and are never reused.
- Slugs are kebab-case (`pebble-keep`).
- Loop references use the `loop:<loop_id>` form inside `next`.
- Ratios are 0 to 1, never 0 to 100. `0.72` means 72 percent.
- Money is decimal USD (`1.99`); in event params money is an int in minor units.
- Paths are project-relative with forward slashes.

## 12. Classifying a feature request in 60 seconds

1. Does it change what the player can do (a new input)? It is a **verb**, and probably a new mechanic.
2. Does it change what happens in response (a new rule or number)? It is a **rule or parameter** of an existing mechanic.
3. Does it change how much of something is earned or spent? It is an **economy node or offer**.
4. Does it change what the player sees or hears in response? It is **feedback** on a mechanic, owned by `game-feel`, `art-direction` or `audio-direction`.
5. Does it add things for the rules to process? It is **content**.
6. Does it add a reason to come back at a new cadence? It is a **loop**, probably meta, social or live-ops.
7. Does it change who the game is for? Stop: this is a contract change that needs a review.

Then record it: update the contract, add a `features.json` entry with area and acceptance criteria, and validate.

## 13. Common confusions

| Confusion | Resolution |
|---|---|
| Verb vs mechanic | A verb is one input-to-intent pair; a mechanic is a rule bundle that may use several verbs |
| Mechanic vs dynamic | Mechanics are specified; dynamics emerge. "Players hoard pairs" is never a rule |
| Aesthetic vs feedback | Aesthetics are the target feeling; feedback (particles, sound, haptics) is a tool serving it |
| Currency vs resource | Every currency is a resource; not every resource is a currency (moves and time are resources players never buy) |
| Meta loop vs progression | The meta loop is the repeating cycle; progression is the long-term curve it climbs |
| Level vs content | Levels are content instances; the level spec describes one, the contract states how many and how they are made |
| Feature vs mechanic | A feature is a unit of delivery with gates; a mechanic is a unit of design. One mechanic is often several features |
