---
name: narrative-design
description: 'Narrative design codex for games, weighted to mobile: story structures, ludonarrative fit, worldbuilding, characters, Ink/Yarn/Dialogic, branching cost maths, barks, UI-length writing, localisation and meta-stories. Use when asked "write the story", "branching cost", "bark pool", "tone bible" or "lint my Yarn/Ink".'
when_to_use: 'Story, world, characters, dialogue, meta-narrative, FTUE narrative, bark and string-table work, dialogue tool choice.'
---

# Narrative Design

Narrative in a game is a production system, not a script. It has a budget (words, branches, VO minutes, localisation cost), a delivery channel (cutscene, barks, UI text, environment, push notification) and a job (orient, motivate, reward, retain). On mobile the session is 1 to 5 minutes, text is read on a small screen, and many players skip. Good narrative design decides what the story must do, then picks the cheapest structure and tooling that does it, and proves it with checks.

## What this skill gives you

- A decision path from "does this game need story?" to an ambition level, structure and tool.
- Story structure models with honest verdicts on where each fits game units (level, chapter, event, season).
- Procedures for worldbuilding, character sheets, tone bible, dialogue authoring, choice design and state tracking.
- Cost maths for branching and bark repetition, runnable with `scripts/narrative_lint.py`.
- Mobile-specific patterns: renovation and other meta-stories, micro-episodes, narrative in the FTUE, story-led marketing and push copy.
- UI-length and localisation rules so lines survive small screens and translation.

## Core models

1. **Narrative has four jobs on mobile.** Orient (who, where, why this level), motivate (a reason to open the app tomorrow), reward (make a win feel like more than a number), differentiate (marketing and IP). If a piece of writing does none, cut it. See `references/mobile-narrative.md` section 1.
2. **Ambition ladder.** Pick one level before writing: (0) none, UI copy only; (1) flavour and barks; (2) character-led framing; (3) meta-story or episodic arc; (4) branching or choice-driven. Cost rises roughly an order of magnitude per rung once branching or VO enters. Default casual games to level 1 or 2; level 3 only if the meta is the retention hook.
3. **Players hold the controller.** Authorial control is partial: pacing is set by play skill, order is partly the player's. Structure must tolerate being skipped, replayed and interrupted. See `references/story-structures.md` section 2.
4. **Structure is a diagnostic, not a template.** Three-act and sequence structure map well to chapters; kishotenketsu (four-part, twist without conflict) suits puzzle and level design; hero's journey is a checking tool after drafting, because it fits some arcs and distorts others. Use verdicts in `references/story-structures.md`.
5. **Ludonarrative harmony.** What the mechanics reward and what the story says must agree. If the story says "mercy" and the loop pays for kills, players believe the loop. Audit dissonance types before locking the premise.
6. **The unit of delivery is the beat.** Write beats (one purpose, one emotional change, one screen of text) and assemble them, rather than writing scenes and cutting later. A micro-scene for a meta is 1 to 3 beats.
7. **State is the hidden cost.** Every remembered choice multiplies QA and save-migration work. Track the minimum: flags that change later text, not flags that merely record history. See `references/dialogue-and-branching.md` section 9.
8. **Tone is a system.** A tone bible (voice rules, taboo list, sample lines at three intensities) lets several writers, and AI drafts, stay consistent. See `references/worldbuilding-characters.md`.

## Decision procedures

### A. Does this game need narrative, and how much?

1. State the retention or conversion problem narrative is meant to solve (D1 curiosity, mid-game goal, event hook, ad creative). No problem, level 0 or 1.
2. Check capacity: words per week the team can write, review, localise and QA. Convert to content days with `cost` (below).
3. Pick the ladder rung; write it into the design contract's narrative field.
4. Decide skip behaviour up front: players who skip everything must still understand the goal (design for skippers, `references/mobile-narrative.md` section 6.3).

### B. Choosing a structure

| Situation | Use | Why |
|---|---|---|
| 50 to 500 puzzle levels, light story | Sequence structure over level packs, mystery spine optional | Small arcs of 8 to 15 levels each resolve a question |
| Level or room design with no antagonist | Kishotenketsu beats | Twist and reconcile without conflict |
| Live event or season | Story circle or episodic arc, one per event | Self-contained, repeatable on a calendar |
| Meta-game (renovation, town, collection) | Client-of-the-week episodes plus one serial thread | Cheap, endlessly extendable |
| Premium short narrative | Vignette or frame narrative | Emotional completeness in minutes |
| Roguelite | Loop narrative: runs reveal story | Failure advances the story |

### C. Choosing a dialogue tool

| Need | Choose | Notes |
|---|---|---|
| Rich branching, scripted text, tight authoring loop | Ink | Strong for text-heavy games; port the runtime to your engine |
| Dialogue with built-in localisation and VO workflow | Yarn Spinner | Good Unity story; check the engine integration you need |
| Godot, visual or script authoring, small team | Dialogic 2 or Godot Dialogue Manager | Check maturity and licence before committing |
| Linear lines, barks, <200 nodes, no state | JSON beat table | Simplest to localise, test and migrate |

Full comparison and decision table: `references/dialogue-and-branching.md` section 2. Always keep content in data files, never in code.

### D. Branching budget

1. Sketch the structure (linear, tree, branch-and-bottleneck, gauntlet, hub, routes, storylets).
2. Run the cost model: `python3 scripts/narrative_lint.py cost --structure bnb --scenes 20 --branch-points 6 --options 3 --branch-length 2`.
3. Compare to capacity; prefer branch-and-bottleneck or storylets over trees. Make cheap structures feel reactive with callbacks (`references/dialogue-and-branching.md` section 7.4).
4. Schedule payoffs: a choice that never pays off teaches players choices do not matter (section 8.3).

### E. Writing a line for a screen

1. Check the length budget for the context (bark, choice, caption, dialogue box) in `references/dialogue-and-branching.md` section 11.
2. Write for the smallest supported font, then apply the expansion allowance for your languages.
3. Put the key information first; avoid concatenated strings, embedded gender and number, and idioms that will not translate (section 12).
4. Run `lines` on the string table, and read it in pseudo-localisation.

### F. Narrative QA per content drop

1. Graph or script lint (`graph`, `yarn`, `ink`).
2. Line lint (`lines`).
3. Bark repetition maths (`barks`).
4. Playthrough of every dead end and every first-time-user path; skipper pass; interruption pass (kill the app mid-scene, resume).
5. Review stages and telemetry events in `references/dialogue-and-branching.md` section 14 and `references/mobile-narrative.md` section 10.2.

## Mobile specifics

- **Meta-stories** (renovation and kin): the story is a reward wrapper for puzzle progress. Pace one beat per few levels, keep each micro-scene under a screen of text, and tune cadence against difficulty so story arrives when frustration peaks (`references/mobile-narrative.md` section 3).
- **Micro-episodes** for 1 to 5 minute sessions: hook, beat, open loop. Track open loops in a ledger so a season never forgets a promise (section 5.4).
- **Narrative as retention** has mixed evidence; measure it with holdouts or skipper vs reader cohorts before claiming credit (section 6.4).
- **FTUE**: story must not delay the first win. Introduce the character after the first successful action, not before.
- **Marketing and push**: character-voiced notifications and story ads work only if the game delivers what the creative shows. See the misleading-ad line in section 7.2 and compliance notes in `legal-ethics`.
- **Interruptions**: every story screen must resume cleanly after a call, a lock, or process death; store the current beat id, not the text.
- **Voice-over** is expensive on mobile; default to text plus sound design, and reserve VO for a few hero moments (`references/dialogue-and-branching.md` section 13).

## Anti-patterns

| Anti-pattern | Detect | Fix |
|---|---|---|
| Lore dump before first play | Story screens before the first interaction | Move to after the first win; drip |
| Tree explosion | `cost` shows words growing exponentially with depth | Bottleneck or storylets |
| Choices without consequence | Options converge with no callback | Add a flag and one later reference, or drop the choice |
| Variable sprawl | `graph` reports var count over budget | Collapse history flags into a few state enums |
| Barks that repeat in minutes | `barks` reports high repeat probability | Bigger pool, cooldowns, context rules |
| Text that overflows in German or Finnish | `lines` flags length after expansion | Shorter source, flexible containers |
| Story contradicts the loop | Ludonarrative audit finds dissonance | Change story framing or reward |
| Writers' content in code | Strings in scripts, not data | Move to string tables with ids |
| Unreachable or dead-end nodes | `graph`, `yarn`, `ink` errors | Fix before build |

## Using the ontology

- Narrative fields live in the concept card and design contract (`game-ontology`): narrative ambition level, premise, cast, tone, delivery channels, content cadence and capacity.
- Content that changes live (events, seasons) is a content-drop artifact with an id; record it in the feature list so `production` can schedule writing, localisation and QA.
- Telemetry: log story-beat views, skips and choice ids with the events in `references/dialogue-and-branching.md` section 14.2; define them via `player-analytics`.
- Agent: `arcosian:narrative-designer` owns this domain; the `design-review` workflow checks narrative scope against capacity.

### Script: `scripts/narrative_lint.py`

Stdlib Python 3.9. Exit 0 ok, 1 check failed, 2 usage error; `--json` for machine output; `--strict` fails on warnings; `--selftest` runs built-in tests.

| Command | Use | Example |
|---|---|---|
| `graph` | State-aware checks of a JSON narrative graph (dead ends, unreachable nodes, variable budget, option counts); format in `references/dialogue-and-branching.md` section 9.5 | `python3 scripts/narrative_lint.py graph --story story.json --strict` |
| `yarn` | Structural checks of `.yarn` files | `python3 scripts/narrative_lint.py yarn --in dialogue/*.yarn --start Start` |
| `ink` | Structural checks of `.ink` files | `python3 scripts/narrative_lint.py ink --in story.ink` |
| `lines` | String-table checks (CSV or JSON) against context budgets with an expansion factor | `python3 scripts/narrative_lint.py lines --in strings.csv --budgets bark=50,choice=36` |
| `cost` | Content-cost model for linear, tree, bnb, gauntlet, hub, routes, storylets | `python3 scripts/narrative_lint.py cost --structure hub --spokes 5` |
| `barks` | Repetition maths for a bark pool | `python3 scripts/narrative_lint.py barks --pool 12 --triggers 8 --prob 0.5 --sessions 3` |

Run `python3 scripts/narrative_lint.py --selftest` after changing anything.

## Reference library

| File | Contains | Read when |
|---|---|---|
| `references/story-structures.md` | Vocabulary, game-vs-linear storytelling, three-act and sequence, kishotenketsu, hero's journey critique, mystery schedule, ludonarrative harmony | Choosing or critiquing a structure |
| `references/mobile-narrative.md` | Four jobs, ambition levels, renovation meta pattern, character-led casual, micro-episodes, retention and marketing, FTUE, genre table, pipeline, worked examples, checklists | Any phone game with story, meta, events or narrative marketing |
| `references/worldbuilding-characters.md` | Mechanics-first worldbuilding, world bible template, naming, character design, archetypes, arcs, cast design, tone bible, building an IP, canon for live games | Starting a world, cast or tone bible |
| `references/dialogue-and-branching.md` | Dialogue tools and examples, branching cost maths, choice design, state and saves, barks, UI-length writing, localisation, VO, QA, volatile tool facts | Authoring, tooling, branching, strings, QA |
| `scripts/narrative_lint.py` | Lints, cost and bark calculators (above) | Before every content build |

## Volatile facts (as of Oct 2026 — verify)

Tool versions, licences and engine integrations change often; the authoritative list with sources is in `references/dialogue-and-branching.md` section 15. Check these before choosing a tool:

- Ink releases and licence: https://github.com/inkle/ink/releases
- Yarn Spinner releases and engine integrations: https://github.com/YarnSpinnerTool/YarnSpinner/releases
- Dialogic (Godot) status, alpha label and Godot version support: https://github.com/dialogic-godot/dialogic/releases
- TTS pricing, disclosure rules and performer-consent terms for VO: see the sources in section 15 of the dialogue reference.

## Related skills

- `game-ontology`: shared schemas for concept, contract and feature records.
- `design-theory`: core loop and motivation frameworks narrative must serve.
- `player-psychology`: curiosity, goals and retention drivers behind story hooks.
- `mobile-ux`: text sizing, reading time and pop-up hierarchy for story screens.
- `accessibility-localization`: translation workflow, text expansion, reading-level and accessibility options.
- `liveops`: event calendars and season cadence for episodic content.
- `marketing-ua`: story-led creative and the misleading-ad line.
- `legal-ethics`: AI-voice disclosure, consent and age-appropriate content.
- `audio-direction`: VO direction and mix for narrative moments.
