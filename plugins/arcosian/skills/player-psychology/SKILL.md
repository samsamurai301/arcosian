---
name: player-psychology
description: 'Player psychology codex: motivation models (SDT/PENS, Quantic Foundry, Bartle, Lazzaro, Fogg, Hook, flow), behavioural economics with ethical boundaries, emotion and cognition for game UI, dark patterns and studio red lines, minors and wellbeing, and player research methods. Use when asked "why do players quit", "what motivates our audience", "is this offer manipulative", "plan a playtest", "write personas" or "check our ethics".'
when_to_use: 'Defining audiences and motivations; designing rewards, offers, social and FTUE features; reviewing monetization ethics; planning playtests, surveys, interviews and personas.'
---

# Player Psychology

Why players start, stay, feel, decide, spend and stop — and how the studio uses that knowledge to make games people are glad they played. This skill turns motivation science, behavioural economics, emotion and cognition research, and player-research practice into procedures, thresholds and red lines. It is the psychological foundation under `design-theory` (structure), `monetization` (offers), `mobile-ux` (screens) and `player-analytics` (measurement), and it is where doctrine item 8 — ethical monetization, transparent odds, respect for minors — becomes enforceable.

## What this skill gives you

- **Motivation models you can act on**: SDT/PENS (with need *frustration*, informational vs controlling rewards, the OIT continuum), Quantic Foundry's 12 motivations for audience definition and feature triage, Bartle as a population-dynamics lens, Yee, Lazzaro's four keys, Fogg B = MAP for "why don't players do X", the Hook model with Eyal's manipulation matrix, flow/GameFlow, achievement goals and social comparison, and a working set of ten mobile player segments mapped to economy archetypes.
- **Behavioural economics with boundaries**: 21 biases and effects (reinforcement schedules with drop-tail maths, loss aversion, endowment, sunk cost, goal gradient, open loops, IKEA effect, anchoring, decoys, scarcity, social proof, reciprocity, commitment, peak-end, near-miss, present bias, defaults, framing, mental accounting, choice overload, fresh start), each with game uses, the abuse pattern, a green/amber/red boundary and a metric.
- **Emotion and cognition for design**: appraisal-based emotion recipes, emotional arcs at seven time scales, fiero, curiosity, surprise and prediction error, wanting vs liking, tension–release, awe, a rage-quit trigger catalogue with telemetry signatures, cognitive load, attention, working memory, learning curves, Hick–Hyman and Fitts, and Gestalt readability tests for game UI.
- **Operational ethics**: a 51-pattern game dark-pattern catalogue (temporal, monetary, social, psychological) with detection and ethical alternatives, 24 binding studio red lines (RL-01…RL-24), a protections matrix for minors, problematic-play signals and wellbeing features, labelled volatile regulatory facts, and a scorecard.
- **Player research methods**: method selection, playtest protocols (moderated, think-aloud, RITE, FTUE, diary, persona-agent), sample-size formulas, survey design, validated scales with licence notes (PENS, BANGS, GEQ, PXI, IMI, UEQ, SUS, NASA-TLX…), interviews, heuristic evaluation with a 16-point studio mobile set, telemetry triangulation, personas and jobs-to-be-done.
- **A calculator and checker**: `scripts/psych_check.py` (problem-discovery sample sizes, survey margins, Cronbach's alpha, and a static red-line audit of `contract.json`).

## Core models

The 20% of player psychology that settles 80% of decisions. Each is actionable; depth and sources are in the references.

### 1. Motivation is plural and situational
Name the audience with **3–4 Quantic Foundry motivations** (lower-case labels in `contract.meta.target_audience.motivations`) *and* a **situation** (commute, bedtime, lunch with friends). Every feature must serve a primary motivation; features that serve only low-ranked motivations are cost centres. Typologies (Bartle) describe population dynamics, not individuals. (`references/motivation-models.md` §1, §4, §11)

### 2. Needs, not tricks
Durable engagement comes from **competence, autonomy and relatedness** (SDT). Audit both *satisfaction* and *frustration* per feature. Frame rewards as **information** ("Perfect clear") rather than **control** ("Log in or lose your streak"), and move extrinsic structures rightward on the external → introjected → identified → integrated → intrinsic continuum. (`motivation-models.md` §2)

### 3. Behaviour = Motivation × Ability × Prompt
When players don't do something, find the funnel step where they drop and classify it M, A or P. Fix **prompts and ability first** (cheaper), motivation last. Use the same model to make quitting, cancelling and spending control *easy* — never to make spending easy while making its cost hard to see. (`motivation-models.md` §7)

### 4. Design emotions through appraisal
Emotions follow from how players appraise events: goal relevance, help/hurt, who caused it, can I cope. To change an emotion, change the appraisal input: explain the failure (attribution, coping) instead of adding a cheerful sound. Plot valence/arousal arcs for levels, sessions, FTUE and seasons; end every arc positive. (`references/emotion-and-cognition.md` §1–2)

### 5. Fiero needs real, fair frustration
Triumph requires perceived difficulty, self-attribution and a clear payoff. Keep frustration **attributable, short, recoverable and informative**: fail recap, one-tap retry under 3 s, help after the 3rd consecutive fail, no progress loss in casual play, no randomness deciding high-stakes outcomes alone. (`emotion-and-cognition.md` §3, §8)

### 6. Wanting is not liking
Reward-prediction systems drive *wanting*; pleasure is *liking*. Healthy loops produce both; compulsion loops keep wanting high while liking falls. Detect with the **removal test** (does the loop survive without the random reward?) and the **reflective-endorsement test** (would players, calm the next day, be glad of the time and money?). (`emotion-and-cognition.md` §5; `design-theory`)

### 7. Every bias has a legitimate and an exploitative use
Psychology is unavoidable — every price has a frame, every screen a default. Judge each use with three tests: **Sunlight** (works even if the player fully understands it?), **Alignment** (serves the player's own goals?), **Vulnerability** (avoids frustration peaks, minors, problem spenders?). Grade green / amber / red; red is never built. (`references/behavioral-economics-in-games.md` §1)

### 8. Respect the cognitive budget
Working memory holds about **four chunks** — fewer under phone-typical distraction. One new concept at a time, taught by doing; externalise memory (show what the decision needs); 2–4 options for time-pressured choices (Hick–Hyman); big, near targets (Fitts; ≥ 44 pt / 48 dp). (`emotion-and-cognition.md` §9–13)

### 9. Readability is perception, not decoration
Use Gestalt grouping (proximity, similarity, common region, figure–ground) and value contrast so the three most important things on screen survive the blur, greyscale and silhouette tests. Never encode critical information by hue alone. Monetisation UI must be visually separate from gameplay UI. (`emotion-and-cognition.md` §14–15)

### 10. Behaviour over opinion, triangulated
Voluntary continuation, retries and errors beat "was it fun?". Telemetry says *what*, observation and interviews say *why*, surveys say *how it is perceived*; use each to check the others. Qualitative rounds of 5–8 per segment find common problems; rarer problems and prevalence need more (formulas in `references/player-research-methods.md` §4).

### 11. Design for the most vulnerable permitted player
Minors, players in a losing streak, late-night players and high spenders get **more** protection, not more pressure. Unknown age is treated as a minor for risky features. Red lines RL-01…RL-24 are binding and belong in `contract.monetization.ethics`. (`references/ethics-and-dark-patterns.md` §6, §8–9)

### Rules of thumb (starting points; verify with your data)

| Topic | Rule | Source of truth |
|---|---|---|
| Audience motivations | 3–4 Quantic Foundry labels + one situation sentence | `motivation-models.md` §4, §12 |
| Drop tails | p = 1%: mean 100 tries, 1 in 100 players needs 459+; cap with pity | `behavioral-economics-in-games.md` §2 |
| Loss aversion | Losses often weigh ~2× gains; size is context-dependent — test | `behavioral-economics-in-games.md` §3 |
| Fail → retry | < 3 s, one tap, nothing in between | `emotion-and-cognition.md` §8.3 |
| Help after failing | Free hint after 3rd consecutive fail; earned skip after 5–7 (non-competitive) | `emotion-and-cognition.md` §8.3 |
| FTUE step budget | 1 new element, ≤ 2 competing on screen, ≤ 12 words | `emotion-and-cognition.md` §9 |
| Threat telegraph on mobile | ≥ 500 ms; windows, not frame-perfect timing | `emotion-and-cognition.md` §13 |
| Home-screen badges | ≤ 3 simultaneous | `behavioral-economics-in-games.md` §7 |
| Spend confirmation | Any spend ≥ USD 5 equivalent asks to confirm; real-money equivalent always shown | RL-07 |
| Interstitial floor | Not before FTUE complete and ≥ 300 s cumulative play; never mid-play | RL-14; `psych_check.py redlines` |
| Usability round | 5–8 per segment; ~85% chance to see a problem affecting 31% of users with 5–6 | `player-research-methods.md` §4.1 |
| Survey margin | ±5 points needs ~385 per subgroup (p = 0.5, 95%) | `player-research-methods.md` §4.2 |
| Scale reliability | Cronbach's α ≥ 0.70 for research use | `player-research-methods.md` §6.1 |
| Interviews | ~12 for a focused question in a homogeneous group | `player-research-methods.md` §4.4 |

## Decision procedures

### A. Define the audience and its motivations (concept → contract)
1. Write the primary segment's **situation** and **job-to-be-done** ("When I …, I want to …, so I can …") — `player-research-methods.md` §11.
2. Pick 3–4 Quantic Foundry motivations; check for conflicting pairs (Competition vs Community, Excitement vs Strategy, Completion vs Discovery) and split conflicts into modes.
3. Choose the primary mobile segment and up to two secondary ones (`motivation-models.md` §11); translate them into `economy-model.schema.json` archetypes.
4. Score every planned feature 0–2 against the primary motivations; challenge every 0.
5. Write to `contract.meta.target_audience` (`age_min`, `segments`, `motivations`) and validate: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py validate .gamestudio/contract.json`.

### B. Psychology review of a feature (rewards, offers, social, notifications, FTUE)
1. **Motivation fit**: which primary motivation does it serve? (Core model 1)
2. **Need audit**: competence/autonomy/relatedness satisfaction and frustration, −2…+2; fix any −2 (`motivation-models.md` §2.3).
3. **Emotion map**: intended emotion per step; check frustration budget and peak-end (`emotion-and-cognition.md` §2, §8).
4. **Bias inventory**: list every bias the design leans on; apply Sunlight / Alignment / Vulnerability; grade green/amber/red (`behavioral-economics-in-games.md` §1 and the per-bias entries).
5. **Catalogue and red-line check**: map to pattern ids (T/M/S/P) and RL ids (`ethics-and-dark-patterns.md` §4, §6). Red → redesign using the listed ethical alternative.
6. **Cognitive check**: new elements, options per decision, recall required, attention competition (`emotion-and-cognition.md` §16 checklists).
7. **Instrument**: events that verify the hypothesis and the guardrails (e.g. `offer_shown.trigger`) — `player-research-methods.md` §9.4.
8. Record decisions in the feature's `gate_notes` and, for amber items, in `contract.monetization.ethics`. Hand monetisation items to `arcosian:monetization-designer`; legal questions to `arcosian:compliance-officer`.

### C. "Players don't do X" (behaviour gap)
1. Define X precisely and the window ("joins a team within 3 sessions").
2. Build the funnel: prompt shown → tapped → each step → done (event taxonomy).
3. Find the biggest drop; classify **M** (doesn't care), **A** (too hard/costly now), **P** (never prompted at an actionable moment).

| Drop type | First fixes |
|---|---|
| P | Prompt at a natural break where the player can act; contextual, not a popup chain |
| A | Remove steps, defer costs, pre-fill, one-tap entry, fix discoverability |
| M | Show the concrete payoff; tie to a primary motivation; better reward fit; or accept that X doesn't fit this audience |

4. Change one factor per test; confirm with `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ab_test.py analyze ...`.

### D. Diagnose churn spikes and rage-quits
1. Locate the spike in telemetry (level, screen, event, time since install) with `arcosian:data-analyst` (`player-analytics`; `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/difficulty_curve.py analyze --data levels.csv`).
2. Match the signature to the rage-quit catalogue (`emotion-and-cognition.md` §8.2): unclear failure, input misreads, spike, output randomness, progress loss, long retry loop, perceived P2W, repeated identical failure, humiliation, interrupted flow, unfair AI.
3. Confirm the mechanism with 5–8 targeted playtests at that point (§E) or session replays.
4. Fix the cause (curve, telegraphs, retry flow, randomness placement), never by monetising the spike (RL-05).
5. A/B or staged rollout with retention and sentiment guardrails.

### E. Plan player research
1. Write the decision the research informs and 3–5 research questions with falsifiable hypotheses.
2. Choose the method from the matrix (`player-research-methods.md` §1): heuristic review → moderated playtest/RITE → unmoderated or diary → survey/A/B for prevalence.
3. Size it: `python3 ${CLAUDE_PLUGIN_ROOT}/skills/player-psychology/scripts/psych_check.py discovery --p 0.15 --target 0.85` for qualitative rounds; `psych_check.py moe --margin 0.05` for surveys; `ab_test.py size ...` for experiments.
4. Recruit from the contract's segments on target-tier devices; consent (and parental consent plus child assent for minors).
5. Run the protocol (FTUE test, think-aloud, RITE); log behaviour first, quotes second.
6. Report in `playtest-report.schema.json` format (`mode: "human"`; persona-agent runs as `mode: "persona"`), findings with severity and "x of n".
7. Triangulate with telemetry before large decisions (`player-research-methods.md` §9).

### F. Ethics review before a gate, soft launch or season
1. Inventory every offer, timer, random reward, notification, social prompt, ad and currency **in the build**.
2. Run `python3 ${CLAUDE_PLUGIN_ROOT}/skills/player-psychology/scripts/psych_check.py redlines --contract .gamestudio/contract.json` and `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/compliance_preflight.py --project .`.
3. Walk the vulnerable paths: new player (first 30 min), 5-level losing streak, minor per the age gate, player who spent USD 50 today.
4. Score the five-dimension scorecard; any red line fails; total ≥ 12/15 with no dimension < 2 passes (`ethics-and-dark-patterns.md` §11).
5. Write `.gamestudio/reports/ethics-review-<date>.md`; `arcosian:critic` challenges the conclusions before sign-off.

### G. Deconstruct the psychology of a comparable game
1. For each system, name the motivation(s) served, the emotion targeted and the biases used.
2. Grade each technique green/amber/red and note what we would borrow and what we would change.
3. Fill `deconstruction.schema.json` → `psychology` (principles, each with grade), `retention_hooks`, `weaknesses` (any red techniques) and `borrow_for_us` (ethical versions only).

## Mobile specifics

- **Context swings motivation.** The same player is a time-filler on the bus and an unwinder in bed; design the primary situation's experience and let other contexts layer in (`motivation-models.md` §11).
- **Sessions are short and interrupted.** Competence microdose in the first 30–60 s; natural stop every 2–5 minutes; autosave every action; resume shows a one-line goal recap (RL-20).
- **Attention is scarce and the thumb occludes.** One animated attention-grabber at a time; critical info near the point of focus and out of the thumb's shadow; game fully playable muted.
- **Arousal varies with place.** Avoid timers on planning decisions; offer calm or no-timer variants for relaxers.
- **Notifications are the external trigger.** Opt-in, ≤ 1 non-transactional per day by default, value-bearing copy, quiet hours (mandatory for minors, RL-21).
- **Premium currency and one-tap purchases are close at hand.** Real-money equivalents, confirmation thresholds, purchase UI separated from gameplay positions (RL-07, RL-13).
- **Children use phones too.** Neutral age screens, platform age signals, and the protections matrix (`ethics-and-dark-patterns.md` §8); unknown age = minor for paid randomness, personalised offers and open chat.
- **Research must match the device.** Test on mid/low-tier phones in the shipped orientation, one-handed where the design claims it, outdoors and in low light.

## Anti-patterns

| Anti-pattern | How to detect | Fix |
|---|---|---|
| "Our audience is Achievers" | Bartle types in the contract; no situation | Quantic Foundry labels + situation + JTBD |
| Motivation soup | Four models' vocabularies mixed in one artefact | One vocabulary per artefact; separate passes |
| Extrinsic everything | Every activity paid with currency; quests reward what players already enjoy | Informational feedback; surprise rewards; quests that invite exploration |
| Engagement at any cost | KPIs rise while endorsement and "rather be doing something else" items worsen | Track wellbeing/endorsement items; removal and reflective-endorsement tests |
| Frustration selling | Offers or ads on fail screens; purchase share spikes after failure | RL-05; free help after fails; offers in neutral contexts |
| Fake urgency | Timers that reset; recurring "last chance" | RL-04; server-verified timers; recurrence policy |
| Currency fog | Gem-only prices; leftovers engineered; > 1 premium currency | RL-07, RL-08; leftover analysis |
| Paid randomness as default | Loot boxes in a 13+ game; odds hidden; no pity | Direct purchase; RL-01/RL-02 for adults only |
| Cognitive overload FTUE | Several new systems in the first minutes; text walls | One element per step, teach by doing, ≤ 12 words |
| Colour-only coding | Fails greyscale test | Redundant shape/icon/position coding |
| Opinion-driven playtests | "Testers said it was fun"; leading questions | Behavioural signals; neutral prompts; voluntary continuation |
| Five users for everything | Reporting percentages from 5 people; rare issues missed | Several rounds; compute n for rarer problems; report "x of n" |
| Modified validated scales | Reworded PENS/GEQ items; translated without back-translation | Use unchanged; check licences; validate translations |
| Agent personas as proof of fun | Persona-agent reports cited as fun evidence | Treat as friction hypotheses; confirm with humans |
| Personas as fiction | Demographic stories with no evidence | Cite sources per claim; behaviour and situation first |

## Using the ontology

| Psychology concept | Where it lives | Notes |
|---|---|---|
| Target motivations | `contract.meta.target_audience.motivations` | Quantic Foundry labels, lower-case |
| Segments | `contract.meta.target_audience.segments` | Plain words incl. situation, e.g. "commute players 25–45" |
| Minimum age | `contract.meta.target_audience.age_min` | < 18 disables paid randomness; < 13 triggers children's protections |
| Ethics rules | `contract.monetization.ethics` | Copy applicable RL ids verbatim; record amber safeguards |
| Ad pacing | `contract.monetization.ads.interstitial` {`first_after_sec`, `min_interval_sec`}; `rewarded[].cap_per_day` | Checked by `psych_check.py redlines` |
| Currencies | `contract.economy.currencies[].kind` | At most one purchasable `hard`/`premium` currency |
| FTUE and aha | `contract.ftue` {`aha_seconds_target`, `steps[].teaches`, `max_seconds`} | One new element per step |
| Emotion per loop step | `contract.loops[].steps[]` (`action`, `reward`) + notes | Lazzaro key and intended emotion |
| Difficulty and DDA | `contract.progression.difficulty` {`target_win_rate`, `dda`} | DDA never depends on spending (RL-09) |
| Player archetypes | `economy-model.schema.json` → `archetypes[]` (`skill`, `spend_propensity`, `ad_accept_rate`) | Segments → archetypes (`motivation-models.md` §11) |
| Psychology of comparables | `deconstruction.schema.json` → `psychology`, `retention_hooks`, `weaknesses` | Grade each technique green/amber/red |
| Concept audience | `concept.schema.json` → `target_audience`, `rationale` | Include the job statement |
| Playtest evidence | `playtest-report.schema.json` (`mode` `human`/`persona`, `findings[].severity`, `metrics`) | Severity mapping in `player-research-methods.md` §13 |
| Psychology telemetry | `event-taxonomy.schema.json` (categories `ux`, `ftue`, `monetization`) | `level_fail.cause`, `retry_start.seconds_since_fail`, `offer_shown.trigger`, `session_end.end_reason` |

**Tools**

| Task | Command |
|---|---|
| Red-line audit of the contract | `python3 ${CLAUDE_PLUGIN_ROOT}/skills/player-psychology/scripts/psych_check.py redlines --contract .gamestudio/contract.json [--strict] [--json]` |
| Participants for a playtest round | `psych_check.py discovery --p 0.15 --target 0.85` · `psych_check.py discovery --p 0.31 --n 5` |
| Survey sample size / margin | `psych_check.py moe --margin 0.05 [--population 2000]` · `psych_check.py moe --n 200` |
| Scale reliability | `psych_check.py alpha --csv responses.csv --reverse 3 --scale-min 1 --scale-max 7 --fail-below 0.7` |
| Drop tails and pity | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gacha_calc.py --rate 0.01 --hard-pity 90 --pulls 200` |
| Experiment sizing / analysis | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ab_test.py size --baseline 0.30 --mde 0.02` |
| Difficulty and churn by level | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/difficulty_curve.py analyze --data levels.csv` |
| Instrument psychology events | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/event_taxonomy.py generate --contract .gamestudio/contract.json --out .gamestudio/analytics/taxonomy.json` |
| Compliance pre-flight | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/compliance_preflight.py --project . --platform all` |
| Search the codex | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py kb "near-miss" --skill player-psychology` |

`psych_check.py` is stdlib-only (Python 3.9+), supports `--json`, exits 0/1/2 (ok / check failed / usage error) and passes `--selftest`. Its red-line audit covers only machine-checkable rules; the full review (procedure F) still applies.

## Reference library

| File | What it contains | Read it when |
|---|---|---|
| `references/motivation-models.md` | Model-selection table; SDT/PENS with CET, OIT and need frustration; Bartle (dynamics, 8 types, limits); Quantic Foundry 12 motivations with mechanics that serve/alienate each; Yee; Lazzaro's four keys; Fogg B = MAP diagnosis; Hook model and manipulation matrix; flow, GameFlow, player-driven flow; achievement goals and leaderboard rules; ten mobile segments with telemetry signatures and archetype parameters; the motivation pass; worked example on Pebble Keep; limits table | Defining the audience, triaging features, diagnosing behaviour gaps, designing leaderboards or habit loops |
| `references/behavioral-economics-in-games.md` | The three tests and grading; 21 biases (reinforcement schedules with drop maths, loss aversion, endowment, sunk cost, goal gradient, Zeigarnik/Ovsiankina, IKEA effect, anchoring, decoys, scarcity, social proof, reciprocity, commitment, peak-end, near-miss, present bias, defaults, framing, mental accounting, choice overload, fresh start) each with uses, abuse, boundary and metric; stacked-offer dissection and ethical rewrite; audit checklist; abuse-detection metrics | Designing or reviewing rewards, prices, offers, timers, store layouts, streaks or social features |
| `references/emotion-and-cognition.md` | Valence/arousal and appraisal recipes; emotional arcs at seven scales with a worked level arc; fiero; curiosity gap; surprise, prediction error, wanting vs liking; tension–release; awe; productive vs destructive frustration, rage-quit catalogue, frustration budget, mercy mechanics; cognitive load; attention; working memory; learning curves; Hick–Hyman and Fitts; Gestalt for game UI; readability and colour; per-level/screen/session checklists | Designing levels, sessions, FTUE, HUDs and feedback; diagnosing frustration and confusion |
| `references/ethics-and-dark-patterns.md` | Definitions; Zagal et al. 2013, darkpattern.games, deceptive.design and academic taxonomies; 51-pattern game catalogue (T/M/S/P) with detection and alternatives; regulatory exposure; studio red lines RL-01…RL-24 and the amber zone; volatile regulatory facts with sources; minors protections matrix; problematic play signals and wellbeing features; ethical monetization patterns; review procedure and scorecard | Any monetization, notification, social or age-related decision; ethics reviews; contract sign-off |
| `references/player-research-methods.md` | Method-selection matrix; study planning and recruitment; playtest protocols (moderated, think-aloud, RITE, unmoderated, FTUE, diary, group, persona-agent); sample-size formulas and tables; survey design; validated scales with licence notes; interviews; heuristic evaluation incl. 16 studio mobile heuristics; telemetry triangulation and psychology events; personas template; jobs-to-be-done and switch interviews; biometrics; reporting into `playtest-report.schema.json`; research ethics and minors | Planning or running playtests, surveys, interviews or heuristic reviews; writing personas; explaining telemetry anomalies |
| `scripts/psych_check.py` | `discovery`, `moe`, `alpha`, `redlines` subcommands; `--json`; `--selftest` | Sizing research, checking scale reliability, auditing a contract against red lines |

## Related skills

- `design-theory` — loops, MDA, flow, decision design; the removal and reflective-endorsement tests originate there.
- `game-ontology` — the schemas and vocabulary these concepts map onto.
- `player-analytics` — telemetry, cohorts, funnels and experiments that test psychological hypotheses.
- `monetization` — offers, pricing, ads and passes designed within this skill's boundaries.
- `economy-design` — currencies, sinks and archetype simulation (segments → archetypes).
- `progression-difficulty` — difficulty curves, DDA and frustration control.
- `mobile-ux` — FTUE, HUD, thumb zones and flows built on the cognitive rules here.
- `game-feel` — feedback, juice and timing that deliver fiero and tension–release.
- `narrative-design` — curiosity, cliffhangers and emotional arcs in story.
- `liveops` — events, scarcity and notifications run within the red lines.
- `legal-ethics` — loot-box law, consumer protection, children's privacy (legal interpretation).
- `accessibility-localization` — readability, colour vision, motion sensitivity, cultural adaptation.
- `qa-testing` — playtest automation and the playthrough gate.
- `marketing-ua` — honest creatives (RL-19) and positioning from jobs-to-be-done.
- `market-intel` — audience sizing and competitor psychology.
- `game-case-studies` — shipped examples to deconstruct with procedure G.
- `game-glossary` — definitions of the terms used here.
