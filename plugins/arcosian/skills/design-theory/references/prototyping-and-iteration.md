# Prototyping and Iteration

How to find the fun fast and prove it before spending on content and polish. This file covers the prototype types and what question each one answers, how to write falsifiable prototype questions, toy-first, paper, greybox and simulation prototyping, how to playtest prototypes and read the signals, iteration cadence and time boxes, kill criteria and the pivot/persevere/kill decision, design pillars, constraint-driven design, the vertical slice and its exit criteria, lean documentation (one-page designs and the design contract), stage gates mapped to the plugin's project tiers, and a genre table of what to prototype first. It is written to work for a human team or for the Arcosian agents, which build in hours rather than weeks and must therefore be even stricter about questions and kill criteria.

## Contents

1. Principles
2. Prototype types and the question each answers
3. Writing prototype questions
4. Toy-first prototyping
5. Paper prototyping
6. Greybox (digital core) prototyping
7. Simulation prototypes
8. Playtesting prototypes and reading the signals
9. Iteration cadence and time boxes
10. Kill criteria and the pivot / persevere / kill decision
11. Design pillars
12. Constraint-driven design
13. The vertical slice
14. Lean documentation
15. Stage gates and project tiers
16. What to prototype first, by genre
17. Running this with Arcosian agents

---

## 1. Principles

1. **Core loop before content, content before polish** (plugin doctrine). No art pass, no meta systems, no monetization until the core micro-loop passes its test.
2. **One question per prototype.** A prototype that tries to answer everything answers nothing.
3. **Cheapest artefact that can answer the question.** Paper beats code for rules; a spreadsheet or script beats a build for economy; a greybox beats art for feel.
4. **Decide success and kill criteria before building.** Afterwards, everyone rationalises.
5. **Observe behaviour, discount opinions.** What testers *do* (replay voluntarily, lean in, lose track of time) outweighs what they *say*.
6. **Throw prototype code away when the question is answered** — unless it was deliberately built on the production architecture (sim-core + presentation) and passes the static and unit gates.
7. **Expect most ideas to fail.** Prototyping is a filter; a high kill rate is a sign the filter works.

---

## 2. Prototype types and the question each answers

| Type | Answers | Fidelity | Typical time box (human team) | Time box (agent build) |
|---|---|---|---|---|
| Paper / tabletop | Do the rules create interesting decisions? | Cards, tokens, grid paper | Hours to 2 days | n/a (or simulate in script) |
| Toy / feel scene | Is the core verb pleasant on its own? | Primitive shapes, real input | 1–3 days | 1–3 hours |
| Greybox core loop | Is the micro-loop fun repeatedly? | Placeholder art, real rules, no meta | 3–10 days | 2–8 hours |
| Systems simulation | Does the economy/progression behave? | Spreadsheet or Python sim | 1–5 days | 1–3 hours |
| UX click-through | Can players navigate and understand flows? | Wireframes, clickable mockups | 1–3 days | 1–2 hours |
| Art target / mood | What will it look and sound like at quality? | 1–3 final-quality frames, a music sketch | 3–10 days | hours (generated candidates + human taste check) |
| Technical spike | Can we build it on target devices within budget? | Minimal code on device | 1–5 days | 1–4 hours |
| Vertical slice | Is the whole experience good at final quality? | One small section, everything final | Weeks | Days |

Pick the type from the riskiest open question, not from habit.

---

## 3. Writing prototype questions

**Template.**

```
Question:   Is <specific experience> <specific property> for <target player>?
Build:      <the minimum artefact>
Measure:    <behavioural signal> and <metric with threshold>
Pass if:    <threshold met>
Kill if:    <threshold missed after N iterations>
Time box:   <hours/days>
```

**Good vs weak questions.**

| Weak | Good |
|---|---|
| "Is the game fun?" | "Do target players voluntarily replay the 20-second reel-in loop more than 15 times with no rewards?" |
| "Does the economy work?" | "In simulation, do median players reach world 2 between day 3 and day 5 without spending, and does no archetype hoard more than 3 days of soft currency?" |
| "Do people like the art?" | "In a 5-second exposure test, can 8 of 10 target players identify the genre and fantasy from one screenshot?" |
| "Are the controls OK?" | "Can a first-time player perform the swipe-dash within 3 attempts, one-handed, on a 6-inch phone?" |

**Order of questions (risk-first).** Rank open questions by *probability it is false* × *cost if discovered late*. Prototype the top one first. In most mobile projects the order is: core verb feel → micro-loop fun → session fit → meta pull → economy stability → monetization fit → production feasibility.

---

## 4. Toy-first prototyping

A **toy** is something pleasant to manipulate with no goal; a **game** adds goals, rules and stakes. Will Wright's SimCity was famously presented as a "software toy" — the idea that a satisfying system to play with can come before (or instead of) win conditions.

**Procedure.**
1. Build only the verb and its immediate physical or visual response (no score, no fail state, no UI beyond what the verb needs).
2. Tune response curves, timing, animation, sound and haptics (`game-feel`) until fiddling with it is pleasant.
3. Hand it to testers with no instructions. Watch for **unprompted play** — do they invent goals ("can I flick it into that corner?")?
4. Harvest the goals players invent; they are candidate game rules.
5. Only then add a goal and a failure condition, one at a time.

**Kill signal.** If testers stop touching the toy within ~30 seconds and invent no goals after two tuning passes, the verb is the problem. Change the verb, not the wrapper.

---

## 5. Paper prototyping

**Best for:** turn-based games, card and deck systems, board-like puzzles, economy rules, level layouts, narrative branching, social deduction.
**Poor for:** real-time action, game feel, physics, anything timing-based.

**Kit.** Index cards, tokens, dice, grid paper, a timer, sticky notes for UI states.

**Procedure.**
1. Write the rules on one page. If they do not fit, simplify.
2. Play it yourself 3 times; fix contradictions.
3. Play with 2–4 others; one person acts as "the computer" (handles hidden state, random draws, AI moves) and must follow written rules exactly — every judgement call they make is a missing rule.
4. Record decisions players agonise over (good) and decisions they make instantly (candidates for automation or removal).
5. Change one rule per round; replay.

**Translating to digital.** Rules that require lots of bookkeeping on paper may be fine digitally (the computer does it), but every hidden calculation must still be *readable* to the player through feedback.

---

## 6. Greybox (digital core) prototyping

**Rules for greyboxes.**
- Primitive shapes and flat colours; colour codes function (red = danger, green = goal, yellow = collectable). No final art — it biases testers toward commenting on visuals and wastes time if the design changes.
- Real input on the real device class: touch on a phone, one thumb if that is the target. Desktop mouse testing misleads on reach, occlusion and precision.
- Real rules, tunable parameters exposed in a debug panel or a data file.
- Instrumentation from day one: log every core event with timestamps so playtest sessions produce data.
- Built on a deterministic simulation core where possible so bots can play it (`game-architecture`; the plugin templates use a sim-core + presentation split).

**What to include and exclude.**

| Include | Exclude |
|---|---|
| Core verb, core loop, one failure condition | Meta progression, shops, currencies (unless that *is* the question) |
| 3–10 handmade situations/levels that vary | Content beyond what the question needs |
| Minimal feedback: sound blips, flashes | Final VFX, music |
| Restart button, parameter panel | Menus, settings, accounts, ads |

**Minimum telemetry in a greybox:** session start/end, attempt start/end with result, core verb count, time between failure and retry, voluntary quit points.

---

## 7. Simulation prototypes

Some questions are answered faster by simulation than by play:

| Question | Tool | Example command |
|---|---|---|
| Does the economy inflate or starve? | Economy simulator | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/economy_sim.py --model .gamestudio/economy/model.json --runs 200 --days 30` |
| How long does progression take? | Progression calculator | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/progression_calc.py curve --formula poly --levels 60 --base 100 --exponent 1.6 --xp-per-min 40` |
| Are puzzle levels solvable, and how hard? | Solver | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/puzzle_solver.py --level .gamestudio/levels/L001.json --algo astar` |
| What is a match-3 level's win rate for bots? | Match-3 simulator | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/match3_sim.py --level .gamestudio/levels/L010.json --runs 500 --bot greedy` |
| Is any option dominated? | Decision maths | `python3 ${CLAUDE_PLUGIN_ROOT}/skills/design-theory/scripts/decision_math.py matrix --payoff "..." --fail-on-dominated` |
| What do random-reward tails look like? | Gacha calculator | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gacha_calc.py --rate 0.006 --soft-pity-start 74 --hard-pity 90 --pulls 180` |

Simulation answers "does the system behave?", never "is it fun?". Pair every simulation result with a play test.

---

## 8. Playtesting prototypes and reading the signals

**How many testers.** For finding usability and comprehension problems, small rounds work: Jakob Nielsen's widely cited guidance ("Why You Only Need to Test with 5 Users", 2000) argues that about five users per round reveal most usability problems, and that several small rounds beat one big one. Small rounds do *not* give reliable metrics (retention, win rates) — those need bots or large samples.

**Who.** Target-segment players who have not seen the game. Teammates and friends are useful only for catching bugs.

**Protocol (30 minutes per tester).**
1. No instructions beyond "play as you normally would on your phone".
2. Observe silently; note hesitations, wrong taps, facial expressions, posture (leaning in vs leaning back).
3. Let them play until they choose to stop (cap the session); note the stop point and reason.
4. Short debrief: "What were you trying to do?", "What was the best moment?", "What was confusing?", "Would you play again tomorrow? Why?" Avoid leading questions ("Did you like the cool explosion?").

**Signal strength ranking (strongest first).**
1. **Voluntary continuation** past the requested time, or asking to play again later.
2. **Invented goals and self-imposed challenges.**
3. **Behavioural engagement**: leaning in, verbal reactions, retries without being asked.
4. **Accurate explanation** of rules and strategy after play (comprehension).
5. **Stated enjoyment** ("it's fun") — weakest; people are polite.

**Red flags.** Testers asking "what am I supposed to do?" after 60 seconds; checking their own phone; tapping through feedback quickly; inability to say why they failed.

**Persona and bot playtests.** Between human rounds, run the `playtest` skill with `arcosian:player-simulator` personas and bot runs to catch softlocks, difficulty spikes and FTUE friction cheaply. Treat simulated "fun" judgements as hypotheses for human confirmation, not as verdicts.

---

## 9. Iteration cadence and time boxes

**Daily loop (prototype phase).** Build → play yourself → play with at least one other person (or persona/bot run) → write 3 observations → change one or two parameters or rules → log the change in `progress.md` (`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py progress "Proto v7: halved reel tension decay; testers retried 2x more"`).

**Weekly review.** Revisit the prototype question: answered yes, answered no, or still unknown? Apply kill criteria. Decide the next riskiest question.

**Time boxes (guidance for small teams; agents should compress these heavily).**

| Stage | Exit question | Time box | If over time |
|---|---|---|---|
| Concept → toy | Is the verb pleasant? | ≤ 1 week | Change the verb or kill |
| Toy → core loop greybox | Is the micro-loop fun 20+ times? | ≤ 2–3 weeks | Pivot the loop or kill |
| Core → first playable (with one meta loop) | Do players want to come back? | ≤ 4–6 weeks | Simplify meta; re-test |
| First playable → vertical slice | Is it good at final quality? | Project-dependent | Cut scope |

**Iteration hygiene.**
- Change one thing at a time when testing a hypothesis; change many things at once only when exploring.
- Keep tuning parameters in data files, not code, so iterations are cheap.
- Keep a **design decision log**: date, decision, evidence, alternatives rejected. It prevents re-litigating settled questions.

---

## 10. Kill criteria and the pivot / persevere / kill decision

**Write kill criteria at concept time** and store them in `contract.kill_criteria` (and concept cards: `concept.schema.json` → `kill_criteria`). Good kill criteria are behavioural, measurable, time-boxed and agreed in advance.

**Example kill criteria by stage (illustrative thresholds — set your own per project).**

| Stage | Example criterion |
|---|---|
| Toy | After 2 tuning passes, fewer than half of 6 testers keep playing with the toy for 60 s unprompted |
| Core loop | After 3 iterations, fewer than half of 8 target testers voluntarily continue past 10 minutes |
| First playable | Fewer than 3 of 8 testers ask to play again / return next day in a multi-day test |
| Simulation | No parameter set in a broad sweep yields progression within target pacing without a dominant strategy |
| Soft launch | Retention and engagement remain below the agreed screen after 2–3 update cycles (see volatile benchmarks in `core-loops-and-structure.md`) |

**Decision table.**

| Evidence | Decision |
|---|---|
| Core signals strong; problems are in usability, content or tuning | **Persevere**: fix and continue |
| Core verb liked but loop or meta not working | **Pivot the structure**: keep the verb, change loop/meta |
| Loop works but audience or market fit is wrong | **Pivot the positioning**: theme, audience, monetization model (`market-intel`) |
| Core verb not liked after the time box | **Kill** (or return to concept with the lessons) |
| Signals ambiguous after the time box | Tighten the question and run one more round; if still ambiguous, **kill** — ambiguity at this stage rarely resolves in your favour |

**Guard against sunk cost.** Judge the next investment on expected future value, not effort spent. Supercell is widely reported to kill many more games than it launches and to treat killed projects as learning rather than failure; whatever the exact figures, the principle — make killing cheap, safe and normal — is sound.

**Kill well.** Write a short postmortem (`postmortem` skill): what was learned, which parts are reusable (verbs, tech, art directions), and what question to ask next.

---

## 11. Design pillars

**Pillars** are 3–5 short statements of the experience the game must deliver, used to make decisions. They are stored in `contract.meta.pillars`.

**Good pillars are:**
- **Experiential**, not featural ("Every tap feels crunchy", not "Has particle effects").
- **Distinctive** — they would not fit every game in the genre.
- **Exclusive** — they imply things you will *not* do.
- **Testable** — you can check a feature against them.
- **Few** — 3 is ideal, 5 the maximum.

**Template:** `<Short name>: <one sentence of player experience>. Means: <2–3 implications>. Never: <1–2 exclusions>.`

**Example set (invented cosy fishing game).**
- **Cosy discovery**: every cast might reveal something new. Means: varied fish behaviours, collection book with silhouettes. Never: punishing failure.
- **One thumb, anywhere**: playable standing on a train. Means: portrait, single-thumb controls, 30-second casts, auto-save per catch. Never: multi-finger gestures, mandatory sound.
- **My aquarium, my style**: what you catch becomes your space. Means: decoration, visiting friends. Never: competitive leaderboards.

**Using pillars to decide.** For any proposed feature, score its support for each pillar: +1 supports, 0 neutral, −1 conflicts. A feature with any −1 needs redesign or rejection unless the pillar itself is being revised (a deliberate, documented decision). A feature with all zeros is a candidate for "won't" scope.

---

## 12. Constraint-driven design

Constraints narrow the search space and force novelty. Many memorable small games come from tight constraints (game jams, one-button games, tiny-screen games).

**Constraint types.**

| Type | Example constraint | What it forces |
|---|---|---|
| Input | One tap only; one thumb; tilt only | Depth from timing, position and context instead of more buttons |
| Session | Every session ≤ 60 s | Self-contained micro-loops; instant resume |
| Scope | 1 screen, 10 objects, 3 rules | Elegance; interaction density |
| Theme | "Things that grow" | Unusual verb–fiction pairings |
| Mechanic inversion | "You are the obstacle, not the runner" | Fresh perspectives on familiar genres (see `analogy-engine`) |
| Technical | 50 MB install, 2 GB RAM devices | Asset discipline; procedural content |
| Time | Prototype in 48 hours | Ruthless focus on the core |

**Method: constraint sprints.** Kyle Gabler and colleagues' Experimental Gameplay Project (described in the 2005 article "How to Prototype a Game in Under 7 Days") showed the value of very short, constrained prototyping cycles: pick a theme or constraint, build something playable within days, keep what works. For an agent studio: run several parallel 2–4 hour constrained prototypes on the same theme (`concept-lab`, `concept-tournament` workflow), then playtest and keep the strongest.

**Constraint deck.** Combine one constraint from each of two or three rows above to generate concept seeds ("one tap" + "≤ 60 s sessions" + "you are the obstacle").

---

## 13. The vertical slice

**Definition.** A vertical slice is a small portion of the game (for mobile: the FTUE plus a few levels or one full session, including its meta step) built to **final quality across every discipline**: gameplay, art, audio, UI, feel, performance on target devices, analytics and, if planned, monetization surfaces. It proves the team can deliver the intended experience and shows what the final game will feel like.

**Related terms.**

| Term | What it is | Purpose |
|---|---|---|
| Prototype | Throwaway build answering one question | Learn |
| First playable | Core loop + minimum meta playable start to finish | Validate the loop and return motivation |
| Vertical slice | Thin, final-quality cut through all disciplines | Validate quality bar, pipeline and production estimates |
| Horizontal slice | All systems at low fidelity | Validate system integration and scope |
| MVP / soft-launch build | Smallest releasable game | Validate the market with real players |

**Vertical slice exit criteria (checklist).**
- [ ] Core loop passes the micro-loop test with target players (`core-loops-and-structure.md` section 13).
- [ ] FTUE reaches the "aha" moment within the contract target (`contract.ftue.aha_seconds_target`).
- [ ] Art and audio match the style and audio bibles; approved by the human taste checkpoint.
- [ ] Every feature in the slice passes the five gates (static, unit, playthrough, visual, perf) per the definition of done.
- [ ] Performance within `technical.perf_budgets` on the low-tier reference device.
- [ ] Analytics events fire per the taxonomy; a funnel can be read from a test session.
- [ ] Production metrics captured: time and cost per level, per asset, per feature — used to re-estimate full scope (`production`).
- [ ] Pillars hold: every element scores ≥ 0 against every pillar.

**Common vertical-slice mistakes.** Polishing a slice whose core loop was never validated; choosing a slice unrepresentative of typical play (the best boss fight instead of an ordinary session); hand-crafting slice assets in ways the production pipeline cannot repeat at scale.

---

## 14. Lean documentation

Documentation exists to align people and agents and to record decisions. Write the least that achieves that.

**Document set (lean).**

| Document | Format | Owner | Notes |
|---|---|---|---|
| Design contract | `.gamestudio/contract.json` | `arcosian:principal` / `arcosian:game-designer` | One-page truth of the game; machine-readable; validated by schema |
| One-page design (human-facing) | `templates/docs/` GDD one-pager | `arcosian:game-designer` | Stone Librande's "One-Page Designs" (GDC 2010) popularised single-page, highly visual design documents |
| Feature specs | Short Markdown per feature, linked from `features.json` | Feature owner | Goal, player story, rules, parameters, acceptance criteria, telemetry, open questions |
| Decision log | Append-only Markdown or `progress.md` entries | Producer | Date, decision, evidence, alternatives |
| Style and audio bibles | `templates/docs/` | Art/audio directors | Visual and sonic rules with references |

**Feature spec template (keep under ~1 page).**

```
F0xx — <title>
Player story:  As a <segment>, I want <experience> so that <motivation>.
Pillars:       <pillar: +1/0/−1 each>
Rules:         <bullet rules>
Parameters:    <key, value, min, max, unit> (mirrors contract.mechanics[].parameters)
Feedback:      <what the player sees/hears/feels>
Acceptance:    <testable criteria> (mirrors features.json acceptance[])
Telemetry:     <events and KPIs>
Risks / open questions:
```

**Do not write**: 100-page GDDs nobody reads, specs for features not yet validated by prototype, duplicated information that will drift (the contract is the single source of truth; human docs link to it).

---

## 15. Stage gates and project tiers

The plugin's `config.json` → `tier` field tracks the project stage: `prototype | slice | soft_launch | global | live`.

| Tier | Entry gate | Main questions | Key artefacts |
|---|---|---|---|
| `prototype` | Concept card scored; kill criteria written | Is the verb pleasant? Is the micro-loop fun? Does the session fit? | Toy, greybox, sims, concept card |
| `slice` | Core loop passed micro-loop test; first playable shows return motivation | Can we hit the quality bar? What does production cost? | Vertical slice, bibles, production estimates |
| `soft_launch` | Slice exit criteria met; analytics and compliance ready | Do real players retain and convert? | Soft-launch build, KPI dashboard, A/B plan |
| `global` | Soft-launch KPIs meet agreed screen; scalable content pipeline | Can we acquire profitably and scale? | Global build, UA plan, live-ops calendar |
| `live` | Launched | How do we sustain and grow? | Events, updates, balance passes |

Human taste checkpoints (doctrine): style sign-off before content production, fun sign-off at the end of `prototype`, store submission approval before release.

---

## 16. What to prototype first, by genre

| Genre | First question | First prototype | Success signal | Common trap |
|---|---|---|---|---|
| Match-3 / tile puzzle | Does the board generate satisfying cascades and decisions under a move limit? | Greybox board with 10 handmade levels + bot sim | Testers retry failed levels; bots show controllable difficulty | Building meta before levels feel distinct |
| Block puzzle (Block Blast-style) | Is placement satisfying and tense as the board fills? | Greybox with piece generator and line clears | Long sessions; "one more" behaviour | Unfair piece generation |
| Merge | Is discovering the next item compelling? | Board + 2 merge chains + silhouettes | Players merge beyond the requested goal | Board clutter; energy gating too early |
| Idle / incremental | Does the number-growth curve feel rewarding over 30 minutes and across a return? | Spreadsheet/sim + minimal UI | Players return after a break to collect; understand prestige | Walls before prestige is understood |
| Hybrid-casual arcade | Is the 30-second level instantly readable and satisfying? | Toy + 5 levels, one upgrade stat | Immediate understanding with no tutorial | Shallow core; relying on upgrades for interest |
| Roguelite survivor | Do level-up choices create distinct builds within a 5-minute run? | Greybox arena, 12 skills, 1 enemy type set | Players describe their build; replay to try another | Dominant skill picks; runs too long for sessions |
| Tower defense | Are placement decisions interesting against varied waves? | Paper or greybox map, 4 towers, 4 enemy types | Testers plan before waves; adapt after leaks | Single best tower |
| Card battler (async/turn) | Do card interactions create decisions and swings? | Paper prototype with 30 cards, then digital | Players debate plays; remember key turns | Too many keywords; first-player advantage |
| Real-time PvP arena | Do 2–3 minute matches feel fair and readable on a phone? | Greybox with bots, then local 1v1 | Losers understand why they lost and requeue | Netcode assumptions untested (`multiplayer-backend`) |
| 4X / base builder | Is the build–raid–defend loop satisfying before timers? | Sim of economy + greybox raid | Players plan bases and enjoy raids without timers | Timer gating hides a weak raid loop |
| Narrative / choice | Do choices feel meaningful and the voice distinctive? | Twine-style branching script | Testers argue about choices; replay for branches | Branch explosion; choices without consequences |
| Physics puzzle | Is the physics toy satisfying and predictable enough to plan? | Toy scene + 5 puzzles | Players experiment; solutions feel earned | Physics nondeterminism frustrating planning |
| Rhythm | Does input timing feel tight on touch at target latency? | Technical spike on low-end device + one track | Players hit the beat consistently after calibration | Device latency variance |
| Word game | Is the core word interaction fresh and shareable? | Paper or web prototype | Testers share results unprompted | Dictionary problems; no daily ritual |
| Social deduction / party | Do bluffing and deduction emerge in short rounds? | Paper role cards with timer | Laughter, accusations, "one more round" | Needs many players; matchmaking cost |

---

## 17. Running this with Arcosian agents

- **Concept stage**: `concept-lab` generates and scores concepts (`concept.schema.json` scores include `fun_potential` and `agent_buildability`); the `concept-tournament` workflow compares them. Every concept card carries kill criteria.
- **Prototype stage**: `arcosian:game-designer` writes the prototype question; `arcosian:gameplay-engineer` (or the engine specialist) builds the greybox on the project template; `arcosian:qa-lead` and `arcosian:player-simulator` run deterministic playthroughs and persona/bot tests (`playtest` skill).
- **Evidence**: playtest reports follow `playtest-report.schema.json`; decisions are logged with `gs.py progress`.
- **Human checkpoint**: the human signs off on fun at the end of `prototype` and on style before `slice` asset production.
- **Critic**: `arcosian:critic` attempts to refute "it's fun" claims before sign-off; it should ask for behavioural evidence (section 8 signal ranking), not opinions.
