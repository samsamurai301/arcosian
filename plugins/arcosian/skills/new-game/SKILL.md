---
name: new-game
description: Takes a one-line game brief to a validated, reviewed project - intake, market scan, concept tournament, human concept pick, design contract, design review, vertical-slice feature plan, engine choice, project template, bibles, placeholder assets, and the first build-feature run. Use when the user says "new game", "I have a game idea", "start a project", "make me a puzzle game", or "turn this brief into a plan".
argument-hint: "[one-line brief]"
---

# New Game: brief to buildable plan

## When to use

Greenfield projects. For an existing repo use `studio` (onboarding). If a concept is already chosen, skip to step 5. If only ideation is needed, use `concept-lab`.

## Inputs

`$ARGUMENTS` is the one-line brief ("a cozy one-handed merge game for commuters"). It may be vague; step 1 tightens it. Output goes to the current directory unless the user names a project root.

## Procedure

1. **Intake (max 8 questions, ask only what is unknown).** Record answers as the `constraints` object used below.

   | Question | Why it matters | Default if unanswered |
   |---|---|---|
   | Who plays, and when (age band, session context)? | Audience drives genre, session length, ethics | Adults 25 to 45, commute and break sessions |
   | Platforms (phones, PC, Steam Deck, web, consoles) and input (touch, mouse and keyboard, gamepad)? | Input, UI, performance tiers, exports and stores (`platform-targets`) | Always ask; never assume. Suggest from the genre: casual on phones and web, action and strategy on PC and console |
   | Monetization: premium, IAP, ads, hybrid, subscription? | Shapes the loops and economy | Hybrid, rewarded ads first |
   | Team and time: who builds, how many weeks to a slice? | Scope tier | AI-agent build, slice in days to weeks |
   | Art and audio: AI-generated placeholders OK? Budget cap USD? | Gateway budget | Placeholders OK, cap from `config.budgets` |
   | Hard no's (themes, mechanics, dark patterns)? | Contract `wont` list | No gambling mechanics, no pay-to-win |
   | Comparable games you love or hate? | Seeds analogies | none |
   | What would make you stop the project? | Kill criteria | Core loop not fun after a prototype playtest |

   Minors in the audience (under 13) raises compliance load: load `legal-ethics` and tell the user now.
   Console targets need a developer programme and certification: load `console-pathway` and say so now.

2. **Market scan.** Run the `market-scan` skill with the genre or brief (writes `.gamestudio/research/market-<slug>.md`). Needed to avoid concepts in saturated lanes with no angle. Keep it to the free-budget level unless the user asks for deep.

3. **Concept tournament.** Run `/arcosian:concept-tournament` with args:
   ```json
   {"brief": "<tightened one-line brief>", "constraints": {"audience": "...", "platforms": ["<from intake>"], "input": ["<from intake>"], "monetization": "hybrid", "tier": "slice", "wont": ["..."], "market_file": ".gamestudio/research/market-<slug>.md"}, "n": 5}
   ```
   Use `n` 5 for a normal run, 8 only when the user wants breadth. Cards land in `.gamestudio/concepts/` (see `concept-lab` for the rubric). Rank them:
   `python3 ${CLAUDE_PLUGIN_ROOT}/skills/analogy-engine/scripts/analogy_score.py rank --dir .gamestudio/concepts --preset default`

4. **Human pick (checkpoint).** Show the top 3 as a table: title, analogy, hook, weighted total, biggest risk, kill criteria. Recommend one with a reason. Wait for the human. Record: `gs.py progress "concept chosen: <id> <why>"`. If none is liked, return to step 3 with their feedback added to `constraints`; do not argue for a rejected concept.

5. **Initialise the project.** Engine rule:

   | Condition | Engine |
   |---|---|
   | 2D, casual, puzzle, idle, card, UI-driven, small team | Godot (default) |
   | 3D-heavy, advanced rendering, large asset store dependence, console path without a porting partner | Unity |
   | User names an engine or has existing code in one | That engine, say what the template does not cover |
   | Anything else (Unreal, web) | Warn that no template exists; use `engine-alternatives` |

   ```
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py init --title "<Title>" --engine godot|unity --genre "<genre>" --platforms <list> [--input <list>] [--orientation portrait|landscape|both] --root .
   ```
   Copy the template into the project root (never overwrite existing files; use `cp -n -R`): `${CLAUDE_PLUGIN_ROOT}/templates/godot-starter/` or `${CLAUDE_PLUGIN_ROOT}/templates/unity-starter/`. Rename the project title in `project.godot` or Unity `ProjectSettings` per the template README. Copy CI from `${CLAUDE_PLUGIN_ROOT}/templates/ci/` only if the user wants it. Both templates build for phones, desktop and web and take touch, mouse, keyboard and gamepad input; delete the export presets or build jobs for platforms the contract does not list.

6. **Write the design contract.** Delegate to `arcosian:game-designer` (mechanics, loops, FTUE) with `arcosian:systems-designer` (economy, progression), `arcosian:monetization-designer` (monetization and ethics), `arcosian:lead-engineer` (technical). Output `.gamestudio/contract.json` conforming to `${CLAUDE_PLUGIN_ROOT}/scripts/schemas/design-contract.schema.json`; field names per the schema (`meta`, `player_fantasy`, `verbs`, `mechanics`, `loops`, `economy`, `progression`, `content`, `ftue`, `ux`, `art_direction`, `audio_direction`, `monetization`, `liveops`, `analytics`, `technical`, `scope`, `risks`, `kill_criteria`). Rules:
   - 3 to 5 pillars, each testable ("every tap yields a visible result within 100 ms").
   - `scope.must` has the vertical-slice items only; everything tempting goes to `should` or `wont`.
   - `ftue.aha_seconds_target` set (aim for well under a minute for casual).
   - `technical.architecture` stays `sim-core+presentation`, `deterministic: true`.
   - At least two `kill_criteria` with numbers the team can measure in a playtest.
   Validate: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py validate .gamestudio/contract.json`. Fix until exit 0.

7. **Design review.** Run the `design-review` skill (`/arcosian:design-review`). Fix every critical and major finding in the contract, re-validate, and log. Present the contract summary (one screen) to the human for approval (checkpoint).

8. **Feature plan.** Read the matching `genre-playbooks` reference for the genre's P0 slice features and FTUE norms. Write features with `gs.py feature add`:
   ```
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py feature add --id F001 --title "Core loop: <verb>" --area gameplay --priority P0 --accept "deterministic playthrough completes the loop" --accept "<measurable criterion>" --desc "..."
   ```
   Vertical-slice P0 skeleton (adapt to the game):

   | ID | Feature | Area | Depends |
   |---|---|---|---|
   | F001 | Sim-core: rules and state for the core loop, unit-tested | gameplay | none |
   | F002 | Core loop presentation with input and feedback | gameplay | F001 |
   | F003 | FTUE to first reward under the aha target | ux | F002 |
   | F004 | Win/lose/results flow and restart | ui | F002 |
   | F005 | One polished level or run, readable on a small phone | content | F002 |
   | F006 | Juice pass: tap, reward, fail feedback | vfx | F002 |
   | F007 | Placeholder art and audio via gateway, style lock | art | F002 |
   | F008 | Perf baseline on a low-tier profile | perf | F002 |
   P1 and P2 hold meta, economy, monetization and live-ops. Keep acceptance criteria checkable by a script or a screenshot.

9. **Bibles and docs.** Copy from `${CLAUDE_PLUGIN_ROOT}/templates/docs/` into `docs/`: one-page GDD (fill it from the contract), style bible, audio bible. Delegate to `arcosian:art-director` and `arcosian:audio-director` to fill the bibles from `art_direction` and `audio_direction`. The playtest and soft-launch plans stay unfilled until needed.

10. **Placeholder assets.** If the `studio-gateway` MCP is available (`gs_status`), generate only what the slice needs (`image_generate` with `kind`, `dry_run: true` first to see the cost). Keep within `config.budgets`. For style direction, produce 3 to 5 candidates and stop for the human style pick (checkpoint). Without keys, mock mode yields valid placeholders; that is fine for the slice. Use `asset-production` for batches.

11. **Start building.** `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py feature next --json`, then run `build-feature` on it. Stop after the first feature passes its gates and report; do not chain the whole slice without the user's go-ahead unless they asked.

## Outputs

`.gamestudio/` (config, contract, features, progress, budget, concepts/, research/market-*.md, reports/design-review-*.md), the engine template at the project root, `docs/` bibles, `assets/generated/` placeholders with manifest entries.

## Quality gates

- `gs.py validate --all` exits 0.
- Contract has pillars, kill criteria, `scope.wont` non-empty, and a design-review report with no open critical or major finding.
- Every P0 feature has at least one measurable acceptance criterion and a dependency order with no cycles.
- A human picked the concept and approved the contract; both are logged in `progress.md`.
- No template file overwritten, no secret written anywhere.

## Failure modes and recovery

| Failure | Recovery |
|---|---|
| All concepts score low on fun or feasibility | Relax one constraint with the user, or run `concept-lab` with a different method (market gap, motivation-first) |
| Template directory missing | Run `gs.py init` only, build the sim-core by hand following `game-architecture`, tell the user |
| Contract fails validation repeatedly | Read the error path, fix that field only; do not rewrite the whole file |
| Scope keeps growing during the contract | Count `must` items; more than about 8 for a slice means cut, using the `production` skill |
| Budget cap hit during placeholders | Stop generation, use mock or programmer art, ask before raising the cap |
| User changes the brief after step 5 | Re-run steps 2 and 3 only if the genre changes; otherwise amend the contract and re-review |

## Related skills

`studio`, `market-scan`, `concept-lab`, `design-review`, `build-feature`, `asset-production`, `genre-playbooks`, `game-architecture`.
