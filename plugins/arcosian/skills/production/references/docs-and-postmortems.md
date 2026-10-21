# Documents and Postmortems

This file gives the document set a small mobile game team actually needs, kept as short as possible: the lean GDD, the one-pager, the design contract, the pitch deck, the feature spec, and three postmortem formats. The rule for every document is that it must change a decision or enable work; if nobody will act on it, do not write it. Templates in `templates/docs/` mirror these outlines. Framework attributions are summarised in my own words.

## Contents
1. Document principles
2. One-pager
3. Design contract
4. Lean GDD
5. Feature spec
6. Pitch deck
7. Style and audio bibles (pointers)
8. Postmortem formats
9. Running a postmortem
10. Knowledge capture
11. Checklists and review questions

## 1. Document principles
- Living, short, searchable. A 3-page doc that is read beats a 60-page doc that is not.
- One source of truth per fact. The contract owns scope; the GDD owns rules; the feature spec owns acceptance criteria; the economy model owns numbers.
- Numbers live in data files (`economy-model.schema.json`, level specs), not prose. Prose links to them.
- Every document has an owner, a version or date, and a "last reviewed at gate" mark.
- Write for two readers: a new human teammate and an AI agent that has no context. Define terms; avoid references to things only in someone's head.
- Prefer diagrams for loops and flows, tables for rules, and examples for edge cases.
- Delete stale sections instead of marking them deprecated.

## 2. One-pager

Purpose: let a stranger understand and judge the game in two minutes. Use for concept selection and for stakeholder sharing.

Template:
| Field | Content |
|---|---|
| Title / working name | |
| Genre and comparables | "X meets Y" only if it helps; list 3 comparable live games |
| Player promise | One sentence: what the player gets to feel or do |
| Target player | Motivation, play context (commute, couch), age band |
| Core loop | Verb, challenge, reward, in 3 lines |
| Session | Length and frequency target |
| Meta | What makes players return tomorrow and next month |
| Differentiator | The one thing nobody else does, stated plainly |
| Monetisation | Model and ethical limits |
| Platform and tech | Engine, devices, offline or online |
| Scope | Team, time, budget, content size |
| Biggest risks | Top three |
| Kill criteria | The numbers that would end the project |

Test: a reader can answer "who is it for, what do they do, why again tomorrow, why us".

## 3. Design contract

The design contract is the binding one-page agreement among owner, director and producer. See `templates/docs/design-contract-guide.md` and the `design-contract.schema.json` schema for the exact fields.

Sections (in order):
1. Promise and audience.
2. Pillars (at most three), each with an observable test (e.g. "a first-time player completes a level in under 60 seconds without reading text").
3. Core loop and session design.
4. Must / Should / Could / Won't.
5. Monetisation and ethics limits (no dark patterns, transparent odds, minor protections).
6. Budgets: time, cash, API and asset spend, performance (frame rate, memory, size, load).
7. Gate table: phase, threshold, kill or pivot action.
8. Assumptions to test, ordered by cost of being wrong.
9. Change log: who changed what, why, what was removed to compensate.

Change rules:
- Pillars and kill thresholds change only with an explicit owner decision and a note on what evidence justified it.
- Scope additions require subtractions.
- Validate with `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py validate`.

## 4. Lean GDD

Target length: 5 to 12 pages for a mobile casual or hybrid-casual game. Link to data files for numbers.

Outline:
1. Vision (copy from the contract).
2. Core loop diagram (moment-to-moment, session, meta).
3. Controls and camera: gesture map, thumb zones, one-hand and two-hand modes, accessibility alternatives.
4. Rules: state variables, verbs, win and lose conditions, edge cases as a table of "if X then Y".
5. Content structure: levels, modes, enemies, items; counts and authoring pipeline; difficulty curve intent.
6. Progression: tracks, unlock order, pacing targets (links to progression data).
7. Economy: currencies, sources, sinks, key prices (link to the economy model).
8. FTUE: first 3 minutes beat by beat; what the player learns when.
9. UX: screen map, flows, HUD, interruptions (calls, backgrounding), notifications policy.
10. Audio and art direction pointers.
11. Monetisation touchpoints: where, what, frequency caps, what is never sold.
12. Telemetry plan: events, funnels, dashboards (link to the event taxonomy).
13. Technical notes: architecture, save data, performance budgets.
14. Live-ops hooks: what is configurable remotely; event templates.
15. Open questions: owner, due date.

Quality bar for rules: someone not on the team could implement the rule or write a test for it from the text. For each rule give one worked example with numbers.

How to keep it lean:
- Write the GDD after the prototype, not before; before then, use the one-pager and a loop sketch.
- Replace long prose with a table or a diagram.
- Move anything that changes weekly (numbers, level lists) into data.
- A feature without a feature spec is not allowed into the Must list.

## 5. Feature spec

Template (see `templates/docs/feature-spec.md`):
- Goal: the player experience in one sentence and the pillar served.
- Non-goals.
- User story and flow, including failure and interruption paths.
- Rules and numbers (link to data).
- UI states: empty, loading, error, success, offline.
- Telemetry events fired.
- Acceptance criteria written as testable statements that map to the five gates: static (lint, types), unit (rules), playthrough (deterministic scenario), visual (screenshot critique), perf (budget).
- Edge cases and risks.
- Dependencies and estimate range.

Example acceptance criteria for a "daily reward" feature:
- Claiming twice in one local day grants once; device clock changes cannot grant extra (server or monotonic check as the design requires).
- Streak resets after a missed day by the documented rule, with an optional grace item.
- Playthrough script claims on day 1, 2, 4 and asserts streak and reward values.
- Reward popup passes visual critique at the smallest supported screen size.
- Event `daily_reward_claimed` fires with streak length.

## 6. Pitch deck

Audiences differ. Choose the variant:
| Audience | Emphasis |
|---|---|
| Publisher | Retention proof (prototype or soft-launch data), market gap, team track record, ask and use of funds |
| Investor | Market, differentiation, unit economics, team, milestones |
| Platform feature team | Polish, platform fit, accessibility, uniqueness |
| Internal green-light | Risk, cost, kill criteria, opportunity cost |

Outline (10 to 14 slides, adapt; see `templates/docs/pitch-deck-outline.md`):
1. Title with one-line promise and a playable link or video.
2. The problem or the gap (from `market-intel`, with sources and dates).
3. The game: what the player does in 30 seconds (GIF or video).
4. Why it works: loop and retention design in one diagram.
5. Market and comparables: what they do, what you do differently.
6. Traction: prototype test results, soft-launch metrics, wishlists; real numbers only.
7. Monetisation and unit economics: assumptions labelled as assumptions.
8. Production plan: phases, gates, kill criteria, budget.
9. Team and how the studio works (including AI pipeline and where humans decide).
10. Risks and mitigations.
11. Roadmap and ask.
Appendix: detailed economy, legal and provenance, tech.

Rules: every number has a source or is labelled an assumption; do not claim performance data you do not have; do not copy competitor statistics without citing the source and date; show the build, not renders; state AI usage honestly and describe provenance and licence practices.

## 7. Style and audio bibles
Short pointers: the style bible (`templates/docs/style-bible.md`) and audio bible (`templates/docs/audio-bible.md`) are the lock documents for assets; production owns that they exist before the slice gate. Content belongs to `art-direction` and `audio-direction`.

## 8. Postmortem formats

Pick the format by purpose. All are blameless: they examine decisions and systems, not individuals.

### 8.1 Went right / went wrong / lessons (classic)
Sections: Summary, What went right (5), What went wrong (5), What we would do differently, Data. Quick, good for public write-ups and small projects. Weakness: tends toward lists without causes. Mitigate by requiring a cause statement per item.

### 8.2 Timeline + causal analysis (for failures and incidents)
1. Timeline of key events and decisions with dates.
2. For each major miss, ask "why" at least three times: what decision was taken, what information was available, what incentive or constraint drove it.
3. Contributing factors table: people/process/tool/environment; controllable vs not.
4. Counterfactual: what would have changed the outcome at the earliest affordable point.
5. Actions: each with an owner, a date, and the change it makes to a template or checklist.

### 8.3 Gate-based review (for projects)
Walk the gates: for each phase record the planned vs actual duration and cost, whether the gate threshold was predictive of the next phase, what the kill criteria would have said in hindsight, and what the estimate error was. Output: a calibration table you can reuse.

| Phase | Planned | Actual | Gate predictive? | Estimate error | Lesson |
|---|---|---|---|---|---|

### 8.4 Quick retro (for sprints or features)
Keep / Stop / Start, plus one experiment for next period. Ten minutes.

### 8.5 Live-ops event review
Event goal, KPIs vs target (participation, revenue, retention effect, support load), what worked, what to change, whether to repeat. Link to `liveops` and `player-analytics`.

## 9. Running a postmortem

1. Schedule within two weeks of the milestone or incident while memory is fresh, but after the stress has settled.
2. Collect data first: schedule history, board metrics, cohort data, bug trends, spend, tester notes, risk register history (realised risks).
3. Each participant writes private notes before the meeting to avoid anchoring.
4. Facilitate: timeline first, then themes, then root causes, then actions. Limit to 90 minutes.
5. Rule: no names in the cause statements; "the schedule assumed" not "X failed to".
6. Convert lessons into changes: edit a gate threshold, a checklist, a template, an estimate multiplier, or a skill reference. If a lesson changes nothing, drop it.
7. Share: internal write-up and, with permission, a public version.
8. Revisit actions at 30 days.

With agents: have an agent compile the timeline from git history, progress log and evidence folders, and draft candidate causes; humans decide causes and actions. Treat the draft as a hypothesis list. Use the `postmortem` process skill for the workflow.

## 10. Knowledge capture

Capture after every project, even killed ones:
- Calibration data: estimate vs actual by feature type; cost per content minute; agent throughput per lane; review minutes per asset.
- Reusable assets: tools, templates, pipelines, prompts, style references with licences.
- Market facts learned and their dates.
- Decision records for non-obvious choices (what, alternatives, why).
- Failure log: what killed or hurt the project, as a pattern name for the risk register.

Storage: project `.gamestudio/` for project-specific; the plugin's codex for general lessons (propose edits to the relevant skill reference). Search existing knowledge with `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py kb "<query>"`.

## 11. Checklists and review questions

Document review questions:
- What decision does this document change?
- Could a newcomer or an agent act on it without asking?
- Which facts are stale or unsourced?
- What is duplicated elsewhere?
- What can be deleted?

Pitch review checklist:
- [ ] One-line promise a stranger repeats back
- [ ] Gameplay footage or playable link in the first minute
- [ ] Every statistic sourced and dated, or labelled assumption
- [ ] Comparables honest about strengths
- [ ] Risks and kill criteria stated
- [ ] AI use and licences disclosed accurately
- [ ] Ask is specific

Postmortem checklist:
- [ ] Data gathered before the meeting
- [ ] Blameless framing kept
- [ ] Each lesson mapped to a concrete change with an owner
- [ ] Calibration data stored
- [ ] Follow-up scheduled at 30 days
