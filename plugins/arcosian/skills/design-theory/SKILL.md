---
name: design-theory
description: 'Game design theory codex: MDA/DDE, kinds of fun, flow, SDT and motivation models, core/meta/social loops, pacing, meaningful decisions, dominance and game theory, depth vs complexity, skill vs luck, failure design, prototyping, pillars, kill criteria and a 130-question design diagnostic. Use when asked "is this fun?", "design the core loop", "why is this boring", "review this design", "find dominant strategies" or "what do we prototype first".'
when_to_use: 'Concepting, writing or reviewing a design contract, diagnosing flat or churning designs, balancing choices, planning prototypes and kill criteria.'
---

# Design Theory

The foundation layer of the studio's design knowledge: the frameworks senior designers actually use, converted into procedures, tables, formulas and checklists that produce decisions. It answers four recurring questions — *what experience are we making, what structure delivers it, are the player's choices worth making, and how do we prove it fast* — and hands off to specialist skills (economy, progression, feel, UX, monetization) once the question becomes specialised.

## What this skill gives you

- A working digest of 20+ canonical frameworks (MDA, DDE, LeBlanc, Caillois, Huizinga, Salen & Zimmerman, Juul, Koster, Schell, Fullerton, Adams & Dormans, Sylvester, Swink, Cook, Meier, flow/Chen, Lazzaro, Bartle, Quantic Foundry, SDT/PENS, Hodent), each with how to apply it, a mobile example and its limits.
- Loop architecture: core/meta/social loops in the ontology's `loops[]` format, the time-scale ladder, session design for phones, interest curves, pacing, teach–test–twist–reward, and nested loop diagrams for six mobile archetypes.
- Decision maths: trade-offs, expected value and variance, dominance detection, payoff matrices and equilibria, weighted rock–paper–scissors, depth proxies, skill vs luck, pseudo-random distribution — with a calculator, `scripts/decision_math.py`.
- Motivation design: motivation → mechanic maps, competence/autonomy/relatedness patterns, overjustification, variable-reward maths and ethics, curiosity, arousal, failure design and mobile segments.
- Prototyping discipline: prototype questions, toy-first, paper and greybox, kill criteria, pillars, vertical slice exit criteria, lean docs, and what to prototype first in 15 genres.
- An original 130-question diagnostic checklist with failure signals and routing, plus a critical-20 fast pass.

## Core models

These are the 20% of theory that settle 80% of design arguments. Each is actionable; details and sources are in the references.

### 1. Experience first, mechanics second (MDA)
Designers can only write mechanics; players only feel aesthetics; dynamics sit between. Always state the **top three target aesthetics** before discussing features, then reason backwards: aesthetic → required dynamic → mechanics and parameters → evidence. When a mechanic "works but feels flat", run a DDE pass on interface, art, audio and fiction before touching rules. (`references/foundational-frameworks.md` §2–3)

### 2. "Fun" is plural — name the kind
Use a shared vocabulary: LeBlanc's eight kinds (sensation, fantasy, narrative, challenge, fellowship, discovery, expression, submission), Lazzaro's four keys (hard, easy, serious, people fun) and Quantic Foundry's twelve motivations. Rank, keep the top three, and reject features that only serve the bottom of the list. A game that claims every kind has no focus.

### 3. The loop stack
- Core loop = **act → reward → invest**, writable in one sentence.
- Every meta loop must return **power, variety, goals or meaning** to the core through a named anchor step.
- Each slower loop should contain roughly **3–10 cycles** of the faster loop below it (seconds → minutes → session → daily → weekly → season).
- Loops are cheap per hour but need depth; arcs (one-time content) are expensive per hour but give novelty. Compute content burn before promising an arc-heavy live game. (`references/core-loops-and-structure.md`)

### 4. Fun comes from learning; mastery has a horizon
Koster: enjoyment is pattern-learning; mastered patterns bore, unlearnable ones frustrate. Cook: each skill atom (action → simulation → feedback → model update) burns out once mastered. For every pattern, estimate its **mastery horizon** and what replaces it (twist, combination, opponent, new content).

### 5. Interesting decisions and elegance
A decision is interesting when it has a **real trade-off**, depends on the **situation**, allows **style**, has **persistent consequences**, and comes with **enough information** (Meier). Remove or automate non-decisions (obvious, blind, random, irrelevant). Elegance = depth per unit of complexity (Sylvester): prefer rules that interact with many existing rules. (`references/decisions-and-depth.md`)

### 6. Challenge–skill balance, steered by the player
Flow lives between anxiety and boredom (Csikszentmihalyi). Players have different flow zones, so prefer **player-driven difficulty** — optional objectives, risk/reward paths — over silent adjustment (Chen). Use system DDA only as an invisible safety net, never in competitive modes. Shape difficulty as tension–release (sawtooth), not a straight ramp.

### 7. Needs, not tricks
Sustained motivation comes from **competence, autonomy and relatedness** (SDT/PENS). Rewards framed as *information* ("you played well") support it; rewards framed as *control* ("do X to get Y") on already-fun activities can undermine it (overjustification). Let intrinsic loops carry the core; use extrinsic structures as scaffolding.

### 8. Put luck where it helps
**Input randomness** (before the decision: draws, refills, offers) creates variety and rewards adaptation. **Output randomness** (after: hit rolls, crits) overrides skill and feels unfair at high stakes. Bound output randomness with smaller variance, pseudo-random distribution and pity, and show the odds.

### 9. Pace like a story
Interest curves: hook early, rising peaks and valleys, climax near the end, short resolution — at every scale (level, session, FTUE, season). Introduce each new element with **teach → test → twist → reward** (the level-spec `teach` field), never in the same level as a difficulty spike.

### 10. Engagement, not compulsion
Run the **removal test** on every loop: remove the random reward — is the loop still worth doing? Then the **reflective-endorsement test**: would players, thinking calmly afterwards, be glad it exists? Loops that fail both are slot machines with a theme; the doctrine forbids building them.

### 11. Find the fun fast, kill early
One falsifiable question per prototype; cheapest artefact that answers it; success and kill criteria written **before** building; observe behaviour over opinion (voluntary continuation is the strongest signal). Core loop before content, content before polish. (`references/prototyping-and-iteration.md`)

### Rules of thumb (numbers to start from, then verify)

| Topic | Starting rule | Source of truth |
|---|---|---|
| Options per decision on a phone | 2–4; 3 is the default | `decisions-and-depth.md` §1 |
| Micro-loop length | 10–30 s for most mobile genres | `core-loops-and-structure.md` §13 |
| Minimum meaningful session | ≤ 60–90 s; natural stop every 2–5 min | `core-loops-and-structure.md` §9 |
| Loop nesting | 3–10 faster cycles per slower cycle | `core-loops-and-structure.md` §7 |
| New elements in early game | ≤ 1 per 3–5 levels | `core-loops-and-structure.md` §12 |
| Pillars | 3 (max 5), experiential and exclusive | `prototyping-and-iteration.md` §11 |
| Usability test round | ~5 target players per round, several rounds | `prototyping-and-iteration.md` §8 |
| Skill check | Strong bot vs random bot: < 65% wins suggests luck-dominated | `decisions-and-depth.md` §11 |
| 1% drop chance | Mean 100 tries; 5% of players need ~299+ | `fun-and-motivation-design.md` §6 |
| Elo | +191 points ≈ 75% win chance | `decisions-and-depth.md` §7 |

## Decision procedures

### A. Concept → design-theory brief (before any contract)
1. Write the player fantasy ("I get to …") and the target segment in one sentence each.
2. Rank the eight kinds of fun; keep three. Pick the segment's top 3–4 motivations (Quantic Foundry labels).
3. Score Caillois mix (agon/alea/mimicry/ilinx) and paidia–ludus position; check alea vs agon against the audience.
4. Draft the core loop with act → reward → invest; run the one-sentence test.
5. Choose one meta loop and name its anchor (power/variety/goals/meaning).
6. List the skill atoms of the first 30 minutes as a chain; mark teach points.
7. Write 3 pillars and 3 kill criteria.
8. Write the riskiest prototype question with pass/kill thresholds.
9. Record in `contract.json` (`meta.pillars`, `player_fantasy`, `meta.target_audience.motivations`, `loops`, `kill_criteria`) — see "Using the ontology".

### B. Diagnose "it's not fun"

| Symptom (observed, not reported) | Likely structural cause | Fast test | Read |
|---|---|---|---|
| Testers stop touching the game within a minute | Core verb unpleasant or unreadable | Toy test: verb only, no goals | `prototyping-and-iteration.md` §4 |
| Fun for 5 minutes, then bored | Short mastery horizon; no variation source | Count distinct situations per 10 cycles | `core-loops-and-structure.md` §2, §13 |
| Players grind but look unhappy | Extrinsic rewards carrying a weak core | Removal test on rewards | `fun-and-motivation-design.md` §5 |
| Players quit right after failing | Failure unexplained, costly, or slow to retry | Ask "why did you fail?"; measure fail→retry time | `fun-and-motivation-design.md` §9 |
| Everyone does the same thing | Dominant strategy | Pick/win-rate table; payoff matrix check | `decisions-and-depth.md` §4 |
| Players can't tell good from bad play | Luck-dominated or invisible feedback | Strong vs random bot test; feedback audit | `decisions-and-depth.md` §11 |
| "What am I supposed to do?" | Goals or feedback unclear; overloaded first session | Complexity budget; usability round | `foundational-frameworks.md` §22 |
| Long sessions then churn | Binge structure, no exit hooks or return reasons | Session anatomy review | `core-loops-and-structure.md` §9 |
| Engagement collapses when an event ends | Mode played for rewards only | Compare activity before/after reward end | `fun-and-motivation-design.md` §5 |
| Feels mechanical but rules are fine | Interface/feel/fiction not supporting the experience | DDE pass: swap feedback, keep rules | `foundational-frameworks.md` §3, `game-feel` |

### C. Design or review a core loop
1. One-sentence test (act → reward → invest).
2. Toy, repetition, variation, decision/skill, feedback, stakes and mobile tests (`core-loops-and-structure.md` §2 table).
3. Micro-loop test with ≥ 5 target players, 20 repetitions, no meta.
4. Meta anchor check; time-scale ladder check; session anatomy (entry, warm-up win, core block, peak, exit hook).
5. Compulsion test on every loop that touches randomness or money.
6. Store loops in the contract; instrument start/end events per loop.

### D. Decision and dominance audit
1. List decision points with frequency; classify with Meier's properties.
2. Build payoff or cost tables; run `python3 ${CLAUDE_PLUGIN_ROOT}/skills/design-theory/scripts/decision_math.py matrix --payoff "…" --fail-on-dominated`.
3. Check luck placement (input vs output) and information at decision time.
4. Check counterplay for every strong option; telegraph windows suited to touch input.
5. After launch: pick rate when offered × win-rate delta per option; control for selection bias.
6. Hand tuning to `arcosian:systems-designer` via the `balance` skill / `balance-pass` workflow.

### E. Pick the right framework
Use the selection matrix in `references/foundational-frameworks.md` §1. Default sequence for a new concept: MDA → motivation model → Cook skill atoms → Meier decision audit → SDT need audit → Hodent usability check.

### F. Structural triage of retention symptoms
| Symptom | Structural suspects | First moves |
|---|---|---|
| Weak first-day return | FTUE too long before the "aha"; no exit hook; early failure cost | Shorten time-to-fun; warm-up win; zero-cost failure in FTUE |
| Day-2–7 decay | Meta not revealed or not compelling; novelty drought; daily loop empty | Reveal the long goal in session 1; novelty schedule; feed dailies |
| Long-term decay | Content burn; solved meta; social loop absent | Loop-based modes; balance pass; team features with solo fallback |
Benchmarks (D1/D7/D30 screens, the D7/D1 ratio, time-to-fun) are volatile and live in `references/core-loops-and-structure.md` §17 with sources; diagnose with `player-analytics`.

## Mobile specifics

- **Sessions are short and interrupted**: design a meaningful session under ~90 s, a natural stop every 2–5 minutes, autosave on every action, and resume into play in one tap. The magic circle is porous — move ads, permission prompts and offers to boundaries.
- **One thumb is the input budget**: few verbs, generous telegraphs and response windows (touch and display latency add delay), 2–4 options per decision, thumb-reachable actions.
- **Attention is scarce**: tiny screens make the HUD compete with the board; show only what the current decision needs and teach one concept at a time, by doing.
- **Arousal varies with context**: players move between a noisy commute and a quiet bed; avoid timers on planning tasks, make the game fully playable muted, and offer calm modes.
- **Audiences are broad**: layer optional systems (ranked, collections, decoration) around a core that one primary segment loves; never make an optional layer mandatory for progress.
- **Free-to-play pressure is constant**: every loop near money gets the removal and reflective-endorsement tests; disclose odds, cap tails, never prompt purchases at frustration peaks.
- **Content burn is fast**: compute it (`core-loops-and-structure.md` §6) before choosing an arc-heavy structure; prefer loop-heavy cores or validated procedural pipelines.

## Anti-patterns

| Anti-pattern | How to detect | Fix |
|---|---|---|
| Feature-first design | Concept described as a feature list; no aesthetic targets | Restart from fantasy + top-three aesthetics (MDA) |
| Meta before core | Shops, currencies and passes exist while the micro-loop fails its test | Freeze meta; iterate the core until it passes |
| "Fun for everyone" | No named segment; motivations conflict across features | Pick a primary segment; layer optional systems |
| Framework worship | Long theory documents, no prototype | One question, one prototype, this week |
| Disconnected meta | Meta loop has no anchor step back to the core | Name what the meta returns (power/variety/goals/meaning) or cut it |
| Stat-sheet design | Options differ only in numbers; one best ratio | Orthogonal differentiation: different roles and properties |
| Hidden dominant strategy | One option has high pick rate and large win-rate delta | Counters, costs, diminishing returns, rework |
| Output-luck at high stakes | Players blame dice for losses | Move randomness to input; shrink variance; PRD; disclose odds |
| Paying for fun | Quests reward the activity players already enjoy | Reward quality, variety and exploration; surprise rewards |
| Punitive failure in short sessions | Churn right after losses; long fail→retry times | Lower failure cost, fail forward, instant retry |
| Difficulty walls as sales funnels | Spikes coincide with offers; stuck players only progress by paying | Fair curve; skill paths past walls; offers decoupled from frustration |
| Novelty drought | Nothing new between day 2 and day 7 | Novelty schedule; teach–test–twist–reward cadence |
| Compulsion loops | Loop collapses without random reward; players report regret | Rebuild around mastery, curiosity or expression |
| Opinion-driven playtests | Decisions justified by "testers said it was fun" | Behavioural signals: voluntary continuation, retries, invented goals |
| No kill criteria | Projects drift for months on ambiguous signals | Write criteria at concept time; enforce at the time box |

## Using the ontology

Design theory maps directly onto the shared schemas (`${CLAUDE_PLUGIN_ROOT}/scripts/schemas/`); see `game-ontology` for full definitions.

| Theory concept | Where it lives | Notes |
|---|---|---|
| Player fantasy | `contract.json` → `player_fantasy` | One sentence, player's point of view |
| Pillars | `contract.meta.pillars` (3–5) | Score features +1/0/−1 against each |
| Target motivations | `contract.meta.target_audience.motivations` | Quantic Foundry labels recommended |
| Verbs | `contract.verbs[]` {`id`, `input`, `description`} | One primary verb per core loop |
| Mechanics and parameters | `contract.mechanics[]` (`rules`, `parameters`, `feedback`, `mobile_notes`) | Parameters carry `min`/`max` for tuning ranges |
| MDA targets per mechanic | `mechanic-card.schema.json` → `dynamics`, `aesthetics`, `failure_modes` | Aesthetics use LeBlanc vocabulary |
| Loops | `contract.loops[]` {`type`, `period`, `steps` {`action`, `reward`, `next`}} | Types: core, meta, social, monetization, liveops |
| Economy graph | `economy-model.schema.json` nodes (`source`, `sink`, `converter`, `gate`, `pool`) | Machinations-style; simulate after each change |
| Difficulty and DDA | `contract.progression.difficulty` {`model`, `target_win_rate`, `dda`} | Per-level `difficulty_target` in level specs |
| Teach–test–twist–reward | `level-spec.schema.json` → `teach` | Plan one new element per few levels |
| FTUE and time-to-fun | `contract.ftue` {`aha_seconds_target`, `steps[].teaches`} | Complexity budget per step |
| Session target | `contract.meta.session_length_target_sec` | Design for the distribution, not the mean |
| Kill criteria | `contract.kill_criteria`, `concept.schema.json` → `kill_criteria` | Behavioural, measurable, time-boxed |
| Concept fun score | `concept.schema.json` → `scores.fun_potential` | Justify with the micro-loop plan |
| Psychology used | `deconstruction.schema.json` → `psychology` | Name principles explicitly when deconstructing |
| Playtest evidence | `playtest-report.schema.json` (`metrics.time_to_first_reward_sec`, `findings`) | Behavioural evidence for fun claims |

**Tools.**

| Task | Command |
|---|---|
| Dominance / equilibria / weighted RPS | `python3 ${CLAUDE_PLUGIN_ROOT}/skills/design-theory/scripts/decision_math.py matrix --payoff "0,-3,1;3,0,-2;-1,2,0" --labels Tank,Mage,Assassin` |
| PRD constant, Elo and series odds, EV | `decision_math.py prd --p 0.25` · `decision_math.py elo --p 0.6 --best-of 7` · `decision_math.py ev --outcomes "0.6:25,0.4:-5"` |
| Difficulty curve targets | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/difficulty_curve.py generate --levels 60 --pattern sawtooth --base 0.85 --floor 0.45 --period 5` |
| Economy behaviour | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/economy_sim.py --model .gamestudio/economy/model.json --runs 200` |
| Progression pacing | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/progression_calc.py curve --formula poly --levels 60 --base 100 --exponent 1.6 --xp-per-min 40` |
| Random-reward tails | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gacha_calc.py --rate 0.01 --hard-pity 90 --pulls 200` |
| Search the codex | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py kb "interest curve" --skill design-theory` |
| Validate contract after edits | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py validate .gamestudio/contract.json` |

`decision_math.py` is stdlib-only (Python 3.9+), supports `--json`, and passes `--selftest`.

## Reference library

| File | What it contains | Read it when |
|---|---|---|
| `references/foundational-frameworks.md` | Selection matrix; 21 frameworks (MDA and critiques, DDE, LeBlanc, Caillois, Huizinga, Salen & Zimmerman, Juul, Koster, Schell's method, Fullerton, Adams & Dormans, Sylvester, Swink, Cook, Meier, flow/Chen, Lazzaro, Bartle, Quantic Foundry, SDT/PENS, Hodent) with application, mobile example and limits; a combined worked pass | Framing a concept, choosing a lens, or settling a "what kind of fun" debate |
| `references/core-loops-and-structure.md` | Loop vocabulary in ontology terms; core/meta/social loops; loops vs arcs and content burn; time-scale ladder; engagement vs compulsion; session design; interest curves; pacing; kishōtenketsu; "30 seconds of fun"; six archetype loop diagrams; loop telemetry; volatile retention benchmarks | Drafting `loops[]`, designing sessions, deconstructing a game's structure, diagnosing retention |
| `references/decisions-and-depth.md` | Decision anatomy; trade-offs; EV/variance and loss aversion; dominance detection; payoff matrices, Nash, social dilemmas; weighted RPS solution; depth proxies; emergence matrices; orthogonal differentiation; counterplay; skill vs luck, PRD, best-of-N; information and asymmetry; card-pool audit; `decision_math.py` reference | Designing choices, units, cards or upgrades; balance reviews; competitive modes |
| `references/fun-and-motivation-design.md` | Motivation → mechanic map; competence/autonomy/relatedness patterns; overjustification; reinforcement schedules, drop-odds maths and ethics; curiosity and novelty schedules; Yerkes–Dodson; failure design; behavioural effects; mobile segments and personas | Choosing rewards, quests and retention features; reviewing monetization-adjacent loops; writing personas |
| `references/prototyping-and-iteration.md` | Prototype types; question template; toy-first, paper, greybox, simulation; playtest protocol and signal ranking; cadence and time boxes; kill criteria; pillars; constraints; vertical slice exit criteria; lean docs; stage gates; what to prototype first in 15 genres; agent workflow | Planning a prototype, setting kill criteria or pillars, defining a slice, choosing the first build |
| `references/design-diagnostic-checklist.md` | 130 original diagnostic questions across 11 areas with bad-answer signals and routing; critical-20 fast pass; finding format; stage subsets | Design reviews, stage gates, critic passes, self-review before hand-off |

## Related skills

- `game-ontology` — formal vocabulary and schemas these models map onto.
- `design-philosophies` — studio ideologies and schools of design that apply these theories differently.
- `mechanics-codex` — encyclopedia of mechanics to instantiate the loops and decisions designed here.
- `genre-playbooks` — genre-specific loops, KPIs and conventions.
- `game-case-studies` — deconstructions that show the theory in shipped games.
- `analogy-engine` — "X meets Y" concept generation and mechanic transplants.
- `player-psychology` — deeper cognitive and behavioural science behind motivation and biases.
- `player-analytics` — telemetry, cohorts and retention diagnostics that validate design hypotheses.
- `economy-design` — currencies, sources and sinks, simulation.
- `progression-difficulty` — curves, difficulty models, DDA.
- `level-design` — level structure, teaching through levels, solvers.
- `game-feel` — juice, response curves and feedback polish.
- `mobile-ux` — FTUE, HUD, thumb zones and flows.
- `monetization` — ethical offers, ads and passes built on these loops.
- `legal-ethics` — loot-box law, minors, consumer protection.
- `production` — scope, milestones and content pipeline capacity.
