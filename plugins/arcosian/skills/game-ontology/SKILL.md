---
name: game-ontology
description: 'The shared vocabulary and schemas of the studio: layered model (player, motivation, aesthetics, dynamics, mechanics, verbs and rules, entities and resources), loops, flows, content, sessions, live-ops, and how each maps to the JSON schemas. Use when asked to "describe this game in the ontology", "write a mechanic card", "model this loop", "which schema holds X", "validate a contract" or "what goes in the design contract".'
when_to_use: 'Writing or reviewing any .gamestudio document, deconstructing a game, modelling loops or economy flows, or deciding where a piece of design information belongs.'
---

# Game Ontology

The closed vocabulary every other skill, agent and script in the studio speaks. A game is described as a stack of layers (who plays, what they feel, what emerges, what is specified, what exists) crossed by two dimensions (time: loops, sessions, seasons; content: levels, worlds, characters). Each concept has exactly one home in a JSON schema, so documents can be validated, diffed and fed to simulators. Learn this before writing a contract, a mechanic card, an economy model or a deconstruction.

## What this skill gives you

- The **layered model** (player to motivation to aesthetics, dynamics, mechanics, verbs and rules, entities and resources) with a test question for each layer.
- **Loop notation** and ten health checks, so loops are written once and judged the same way everywhere.
- A **mapping from Machinations-style primitives** (Adams and Dormans) to the `economy-model` node kinds.
- A **field-by-field schema guide** for all thirteen documents, with validation commands and common errors.
- A **worked example** following one game through the whole document chain, plus cross-document consistency checks.
- A **60-second classification** for any feature request: verb, rule, parameter, economy node, feedback, content or loop.

## Core models

### The stack, in one picture

```
PLAYER -> MOTIVATION -> AESTHETICS <- DYNAMICS <- MECHANICS <- VERBS + RULES <- ENTITIES + RESOURCES
 (who)      (why)        (feel)       (emerge)     (specify)     (inputs/world)      (things/quantities)
```

Design from the aesthetic target down; observe from the mechanics up. A symptom at layer N is usually caused at layer N-1 or N-2. Aesthetics and dynamics follow the MDA framework (Hunicke, LeBlanc and Zubek, 2004); the eight aesthetic words are the enum used by mechanic cards.

### Layer test questions

| Layer | Test question | Schema home |
|---|---|---|
| Player | Could you name three real people who match, and would one dislike the core loop? | `meta.target_audience` |
| Motivation | Which motivation does each loop reward serve? | `motivations`, loop descriptions |
| Aesthetics | Would a playtester use two of your words unprompted? | `player_fantasy`, `meta.pillars`, card `aesthetics` |
| Dynamics | Can you name one expert strategy and one degenerate strategy? | card `dynamics`, playtest `findings` |
| Mechanics | Do the rules fit on a card, implementable with no questions? | `mechanics[]`, `*.mechanic.json` |
| Verbs and rules | If this verb vanished, would a loop break? | `verbs[]`, `mechanics[].rules` |
| Entities, resources | Must two of them be told apart? (entity) Or interchangeable? (resource) | levels, assets; `economy`, `resources[]` |

### Loops

| `type` | Typical `period` | Job |
|---|---|---|
| `core` | `seconds` or `minutes` | Moment-to-moment pleasure |
| `meta` | `session` | Purpose beyond the level |
| `social` | `daily` or `weekly` | Relatedness |
| `monetization` | `minutes` or `session` | Optional offers and continues |
| `liveops` | `weekly` or `season` | Reasons to return |

A step is `{id, action, reward, next}`; `next` may be a step id, a list, `"loop:<id>"` or null. The core loop hands off to a meta loop, and the meta loop returns to `loop:core`.

### Flow and pacing

Resource flow (sources, pools, converters, gates, sinks) lives in the economy model; experience flow (challenge against skill) lives in `progression.difficulty` and level specs. Level pacing uses the four beats `teach`, `test`, `twist`, `reward`.

### Conventions that prevent most validation failures

- Ratios are 0 to 1 (`0.72`, not `72`). Money is decimal USD. Paths are project-relative.
- Ids are `snake_case` and match `^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$`; feature ids are `F` plus 3 or 4 digits.
- Every top-level document carries `"schema_version": "1.0"`.

## Decision procedures

### Where does this piece of information go?

1. New player input: add a `verbs[]` entry, then a mechanic that uses it.
2. New rule or number on an existing mechanic: edit `rules` or add a `parameters` entry with `min`, `max`, `unit`, `note`.
3. New earn or spend: an `economy-model` node (kind `source`, `sink`, `converter`, `gate` or `pool`) and the contract currency `sources` and `sinks`.
4. New response (particles, sound, haptics): `feedback` on the mechanic; the specialist skill owns detail.
5. New things for the rules to process: content (`level-spec`, assets).
6. New reason to return at a new cadence: a loop, usually `meta`, `social` or `liveops`.
7. Change to who the game is for: stop; it is a contract change needing `design-review`.
8. Record it as a feature (`features.json`, with area and testable acceptance) and validate.

### Describe a game in the ontology (for a concept or a deconstruction)

1. Write the player fantasy in one sentence and pick at most three aesthetics.
2. List the verbs (1 to 3 core), then the mechanics with numbered rules.
3. Draw the loops: core first, then every meta, social, monetization and liveops loop, linked by `loop:` hand-offs.
4. List resources with sources, sinks and caps.
5. State progression curves and the difficulty model with a target win rate.
6. List dynamics you observe or predict, including one degenerate strategy, and weaknesses.
7. Validate, then run the loop health checks (`references/loops-flows-and-mda.md`).

### Write a mechanic card

Follow the eleven steps in `references/loops-flows-and-mda.md` section 11. Minimum bar: rules are one testable sentence each, every number is a ranged parameter with a note that contains the arithmetic, each failure mode has a detection signal, aesthetics come from the eight-word enum.

### Loop health check (short form)

Closed and linked; reward at least once per turn; at least one real decision; everything spent is earned somewhere; each turn escalates; safe exit and re-entry; core period times about three fits the session; every reward key is a declared resource. Details and failure patterns: `references/loops-flows-and-mda.md` section 2.

### Validate

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_json.py --auto PATH [PATH ...]      # schema inferred from the file name
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py validate --root PROJECT_DIR           # all of .gamestudio/ plus feature rules
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py validate --schema level-spec my.json   # force a schema
```

Exit codes: 0 valid, 1 invalid, 2 usage error. Schemas: `${CLAUDE_PLUGIN_ROOT}/scripts/schemas/<name>.schema.json`. Examples to copy: `${CLAUDE_PLUGIN_ROOT}/scripts/schemas/examples/`.

### Cross-document consistency (run when two documents change together)

Loop reward keys exist as resources; contract currencies appear in the economy model; contract `perf_budgets` equal the perf report `budgets`; level `mechanic_refs` exist; FTUE step seconds sum to the aha target; every KPI target has events that can compute it. Table in `references/worked-example.md` section 12.

## Mobile specifics

- Session length is a first-class contract field (`session_length_target_sec`, 10 to 7200). Derive loop periods, FTUE budgets and daily loop counts from it.
- Interruption is normal: every mechanic card needs a safe-exit statement in `mobile_fit.notes`, and every loop needs a resumable step.
- Keep the core verb set to one to three, each with an `input` that one thumb can perform in portrait.
- The economy's `archetypes` carry `sessions_per_day` and `session_minutes`; a loop that only works at ten sessions a day is a design error for most casual audiences.
- Daily and weekly cadence belongs to the day and the season (`trigger: "daily"`, loop `period: "weekly"`), not to the session.

## Anti-patterns

| Anti-pattern | Detect | Fix |
|---|---|---|
| Mechanics without stated aesthetics | Contract has `mechanics` but empty pillars and fantasy | Write the aesthetic target first, then check each mechanic serves it |
| Dynamics written as rules | A "rule" that says players will do something | Move to `dynamics`; rules say what the system does |
| Prose rules | Adjectives ("fast", "strong") in `rules` | Replace with parameters with units and ranges |
| Unranged parameters | `min` and `max` missing | Derive bounds from where the design breaks |
| Island loops | A loop with no `loop:` link in or out | Link it or cut it |
| Orphan rewards | Reward key not in `resources` | Add the resource, sources and sinks |
| Percent as ratio | Value above 1 in a ratio field | Divide by 100 |
| Currency with a source and no sink | Economy audit | Add a sink, cap or gate, and a hoard target |
| Verb inflation | More than three core verbs on casual mobile | Merge or cut |
| Live-ops as new game | Event needs new core rules | Express as a delta on resources, nodes or content, or move it to a new contract |
| Unverified content | Generated levels without a `solver` block | Run a solver or bot and record it |
| Schema drift in prose | Field names invented in notes | Use the exact names in `references/schema-reference.md` |

## Using the ontology

This skill is the ontology. Other skills use it as follows:

- `design-theory`, `mechanics-codex`, `genre-playbooks`: supply the content of aesthetics, dynamics and mechanic cards.
- `economy-design`, `progression-difficulty`: own `economy-model` and `progression` details; simulate with `economy_sim.py`, `progression_calc.py`, `difficulty_curve.py`.
- `level-design`, `procedural-generation`: own `level-spec` and solver evidence (`puzzle_solver.py`, `pcg.py`).
- `player-analytics`: owns `event-taxonomy` (`event_taxonomy.py`).
- `game-case-studies` and the `deconstruct` process skill: produce `*.deconstruction.json`.
- `qa-testing`, `mobile-performance`: own `playtest-report` and `perf-report`, the evidence for gates in `features.json`.

Project layout and gate rules are in `docs/BLUEPRINT.md` sections 5 and 6: `.gamestudio/config.json`, `contract.json`, `features.json`, `budget.json`, `assets/manifest.json`, and the folders `concepts/`, `research/`, `economy/`, `levels/`, `analytics/`, `evidence/<FEATURE-ID>/`, `playtests/`, `reports/`. A feature is done only when `static`, `unit`, `playthrough`, `visual` and `perf` are each `pass` (with evidence on disk) or `n/a` (with a note). Search the codex with `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py kb "query" --skill game-ontology`.

## Volatile facts (as of Oct 2026 — verify)

The ontology itself is stable: it is a local, versioned schema set (`schema_version` 1.0), so nothing in it depends on store rules, prices or SDK versions. Two things outside it do move:

- The Machinations tool and its node vocabulary evolve; this skill maps the book-level primitives (Adams and Dormans, 2012), not any product version. Verify current features at https://machinations.io/ before promising a specific node type.
- The DDE framework citation (Walk, Goerlich and Barrett, around 2017) should be checked before it is quoted formally.

## Reference library

| File | What it contains | When to read it |
|---|---|---|
| `references/ontology-overview.md` | The layered model in depth; loops, flows, content, sessions, live-ops; layer-to-schema table; id conventions; 60-second feature classification; common confusions | First, when describing a game or deciding where information belongs |
| `references/loops-flows-and-mda.md` | Loop notation and ten health checks; Machinations-to-economy-model mapping; feedback and runaway analysis; MDA and DDE worksheets; precise rules; parameter hygiene; mechanic card procedure; validated JSON examples | When drafting or reviewing loops, mechanics or economy skeletons |
| `references/schema-reference.md` | Field-by-field guide to all thirteen schemas, enums, constraints, validation commands and a table of common errors | When writing a document or interpreting a validation error |
| `references/worked-example.md` | Walk-through of the example documents in `${CLAUDE_PLUGIN_ROOT}/scripts/schemas/examples/`, reviewer reasoning at each stage, cross-document checks, an end-to-end exercise | To calibrate document density and quality, or to practise the full chain |

## Related skills

- `design-theory`: the theory behind aesthetics, dynamics, flow and decisions that this ontology organises.
- `mechanics-codex`: a library of mechanics already expressed as cards.
- `economy-design`: building, simulating and balancing the economy model.
- `progression-difficulty`: curves, difficulty models and dynamic difficulty fields.
- `level-design`: level specs, pacing beats and solver evidence.
- `player-analytics`: event taxonomy and KPI mapping.
- `game-case-studies`: deconstructions written in this vocabulary.
- `game-glossary`: short definitions of the terms used here.
