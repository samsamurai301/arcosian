---
name: deconstruct
description: Deconstructs an existing game into the shared ontology - core loop, mechanics, economy, progression, monetization, live-ops, retention hooks, psychology, weaknesses and lessons - from public sources, writing deconstruction.schema.json and a readable markdown analysis. Use when the user says "deconstruct <game>", "break down how X works", "analyse this game's economy" or "what can we borrow from X".
argument-hint: "[game title]"
---

# Deconstruct

## When to use
To learn from a reference game, scout a competitor, or ground a concept in evidence. Load `game-ontology`, `design-theory`, `player-psychology`, `economy-design`, `monetization` and `game-case-studies`. Delegate market context to `arcosian:market-analyst`, mechanics to `arcosian:game-designer`, economy to `arcosian:systems-designer`, and doubts to `arcosian:critic`. The parallel version is `/arcosian:deconstruct-game`.

## Inputs
`$ARGUMENTS` is the game title (add platform, year or developer to disambiguate). If empty, ask for a title or take it from `contract.meta.comparables`.

## Honest limits
This skill reads public material; it cannot play the game, see live offers, or observe server behaviour. Every statement is tagged: `observed` (stated in a source), `inferred` (reasoned from sources) or `unknown`. Where a number is not published, leave it out or give a labelled estimate with its basis. The user or `arcosian:player-simulator` can add first-hand play notes.

## Procedure
1. **Check existing knowledge first.** `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py kb "<title>" --json` and look in `skills/game-case-studies/references/` (see its `SKILL.md`). If a case study exists, start from it and only deepen or update. Check `.gamestudio/research/deconstructions/` for a previous run.
2. **Collect sources** (record every URL in `sources`): official store pages (description, screenshots, in-app purchase list, update history), patch notes and changelogs, the community wiki, developer talks or interviews, review text (top positive and negative themes), gameplay videos and their transcripts or descriptions, press coverage, and the user's own notes. Prefer primary and recent material; note the date of each.
3. **Apply lenses**, one pass each, noting evidence:
   - Core loop: verbs, challenge, reward, loop length, what makes the next iteration desirable (`design-theory`).
   - Mechanics: as mechanic cards (`mechanics-codex`), with parameters when known.
   - Meta loops and progression: tracks, unlocks, pacing, soft walls.
   - Economy: currencies, sources, sinks, conversion points, scarcity (`economy-design`).
   - Monetization: model, top offers, ad placements, pass structure, ethics concerns (`monetization`, `legal-ethics`).
   - Live-ops and social: cadence, events, competition, cooperation, communication.
   - Retention hooks: daily, weekly, collection, streaks, investment (`player-psychology`).
   - UX and FTUE: time to first reward, teaching order, friction (`mobile-ux`).
   - Art and audio: what carries the identity, readability, juice (`art-direction`, `audio-direction`).
   - Psychology: name principles used and how, in your own words, with attribution to the source framework.
   - Weaknesses, innovations, and what players complain about.
4. **Synthesize.** Write `lessons` (what the game teaches us) and `borrow_for_us` (what to adopt, change and avoid for the current contract; use the `borrow/change` logic from `contract.meta.comparables`). Skip empty lessons.
5. **Write JSON** to `.gamestudio/research/deconstructions/<slug>.json` with `"schema_version": "1.0"`, following `${CLAUDE_PLUGIN_ROOT}/scripts/schemas/deconstruction.schema.json` (required: `game`; fill every lens that has evidence). Slug is lowercase kebab-case of the title. Validate: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_json.py --schema ${CLAUDE_PLUGIN_ROOT}/scripts/schemas/deconstruction.schema.json --instance <file> --json`. Fix until exit 0.
6. **Write the markdown** `.gamestudio/research/deconstructions/<slug>.md`: one-paragraph verdict, core loop diagram in text, tables for economy and monetization, strengths, weaknesses, confidence map (observed/inferred/unknown), lessons, borrow list, source list. Keep it readable in five minutes.
7. **Challenge.** `arcosian:critic` reviews: unsupported claims, survivorship bias (a hit's traits are not necessarily causes), and borrowed features that depend on scale or IP we lack. Revise.
8. **Hand off.** Offer `concept-lab` (new concept), `market-scan`, or `design-review` using the findings. Log with `gs.py progress`.

## JSON skeleton
```json
{
  "schema_version": "1.0",
  "game": {"title": "", "developer": "", "year": 0, "genre": "", "platforms": []},
  "core_loop": {"id": "core", "type": "core", "period": "minutes", "steps": []},
  "meta_loops": [], "mechanics": [], "economy": {"currencies": [], "sources": [], "sinks": []},
  "progression": {}, "monetization": {"model": "", "top_offers": [], "ads": {}},
  "liveops": {}, "retention_hooks": [], "psychology": [], "innovations": [],
  "weaknesses": [], "lessons": [], "borrow_for_us": [], "sources": []
}
```
Confirm exact field types against the schema before writing; put the observed/inferred/unknown tags in the markdown and in `notes` fields where the schema allows.

## Source quality
| Source | Good for | Watch out for |
|---|---|---|
| Store page and update history | Offers, features, cadence | Marketing language, stale text |
| Patch notes | Live-ops rhythm, balance changes | Omitted changes |
| Wiki | Mechanics, numbers, content | Outdated or player-opinion pages |
| Reviews | Pain points, perceived value | Small, vocal samples |
| Developer talks | Intent and rationale | Hindsight and survivorship |
| Videos | UX, pacing, feel | Cannot show economy depth; short sessions only |

## Confidence tags in practice
| Statement | Tag |
|---|---|
| "Store page lists a monthly pass" | observed |
| "The pass probably drives daily return" | inferred (basis: reward track structure) |
| "Payer conversion rate" | unknown unless published; never guess a figure |

Mark inferred items with the basis so a reader can disagree with the reasoning, not just the conclusion.

## Scope control
One game per run. For a genre sweep run `market-scan`; for several titles use `/arcosian:deconstruct-game` so each gets its own file.

## Outputs
`.gamestudio/research/deconstructions/<slug>.json` and `<slug>.md`; progress entry.

## Quality gates
- JSON validates against the schema; `sources` has real URLs actually consulted.
- Claims are tagged observed/inferred/unknown; no invented numbers, revenue or retention figures.
- At least three lessons and one explicit "do not copy" caveat.
- Own words throughout; no long quotations or reproduced guides, only short attributed quotes if essential.
- Critic pass done.

## Failure modes and recovery
| Symptom | Recovery |
|---|---|
| Few public sources | Narrow the scope, mark most lenses `unknown`, ask the user for play notes |
| Title ambiguous or several versions | Ask, or analyse the current store version and say so |
| Economy opaque | Describe structure only (currencies, sinks) and avoid rates |
| Schema validation fails | Read the error path, fix types and enums, re-validate |
| Wiki disagrees with store page | Prefer the more recent primary source and note the conflict |

## Related skills
`game-case-studies`, `game-ontology`, `analogy-engine`, `market-intel`, `concept-lab`, `design-review`.
