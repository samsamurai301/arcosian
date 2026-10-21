---
name: design-philosophies
description: Codex of game-making ideologies. Doctrines of influential studios (Nintendo, Supercell, Valve, King, HoYoverse, indie craft houses), rules derived from notable designers, schools of thought and debates, and this plugin's 10-point house doctrine made operational. Use when asked "what would Nintendo do", "which philosophy fits this game", "settle this design debate", "is this ethical F2P", "should we kill it", or for a philosophy lens review.
---

# Design Philosophies

Ideologies are compressed experience: each studio doctrine or designer rule is a bet about what matters most when everything cannot be done. This skill turns those bets into decision tools. It never replaces the house doctrine; it supplies the reasoning, precedents and lenses that let agents apply the doctrine with judgement, settle recurring debates quickly, and borrow from great studios without cargo-culting them.

## What this skill gives you

- **Studio doctrines** of nearly thirty studios, from Nintendo, Valve and Supercell to Habby, Mega Crit and LocalThunk, each with beliefs, practices, outcomes, and how this plugin borrows the idea (`references/studio-doctrines.md`).
- **Designer rules**: more than twenty designers' philosophies, each reduced to one testable rule and a mobile worked example, plus where the plugin checks it (`references/designer-philosophies.md`).
- **Schools of thought**: eighteen debates (systems vs content, premium vs F2P, data vs intuition, cozy, roguelite, accessibility, crunch, AI in production and more) with "when each side is right" tables and the house position (`references/schools-of-thought.md`).
- **The house doctrine operationalized**: each of the ten principles with its enforcement mechanisms, settled decisions, failure signs, conflict rules and a milestone audit (`references/studio-doctrine-operationalized.md`).
- **Procedures** for picking a philosophy profile, settling debates, testing whether a practice transfers, running a lens review, making kill calls and writing pillars that carry a philosophy.

## Core models

### 1. Every philosophy optimizes a scarce resource

Name the scarcest resource for the project first; then choose the doctrines built to protect it.

| Scarce resource | Doctrines that optimize it | Plugin lever |
|---|---|---|
| Player attention in the first minute | Nintendo (teach through play), Playdead (subtraction), Bushnell's law | `ftue.aha_seconds_target`, `ftue.steps[].teaches` |
| Team capacity and focus | Supercell (small cells, kill most games), Yokoi (novelty in one dimension) | `scope.must/should/wont`, `kill_criteria` |
| Information about players | Valve (silent playtests), King (funnels, bots), Mega Crit (run metrics) | `playthrough` gate, event taxonomy, `ab_test.py` |
| Player trust | Riot (player-focused), ConcernedApe (generosity), thatgamecompany (prosocial design) | `monetization.ethics`, `compliance-officer` |
| Content production | Mojang and Klei (systems), Spelunky (templates plus generation), King (bot-verified, designer-tuned level pipelines) | `procedural-generation`, solvers and simulators |
| Device resources | Yokoi (withered technology), Dream Games (speed as polish) | `technical.min_spec`, `perf_budgets` |
| Acquisition money | Voodoo-era testing (appeal before build), Scopely (execution plus IP) | `market` score in `concept-tournament` |

### 2. The doctrine stack (precedence)

1. **House doctrine** (the ten principles in priority order, listed in `references/studio-doctrine-operationalized.md` section 1) — never overridden.
2. **Project pillars and contract** (`meta.pillars`, `player_fantasy`, `scope`, `kill_criteria`, `monetization.ethics`).
3. **Discipline codex rules** (other codex skills such as `economy-design` or `level-design`).
4. **Borrowed philosophies** (this skill's references).
5. **Personal taste** of any agent.

A borrowed philosophy can sharpen a pillar but cannot license breaking a higher layer. "FromSoftware does it" does not justify unreadable deaths in a casual game; "Moon Active does it" does not justify paid randomness for minors.

### 3. Convergent beliefs are near-laws

When studios with opposite business models agree, treat the belief as settled:

1. The build is the truth; play it constantly.
2. Small teams with full ownership ship better games.
3. Cancel or cut what is not great, early and by pre-agreed criteria.
4. Teach through play, not text.
5. Readability and feel are product quality.
6. Long-term player trust is an asset that compounds.
7. Instrument, then decide.

Evidence and exemplars for each are in `references/studio-doctrines.md` section 2.1.

### 4. Splits are contextual, not tribal

Throughput vs craft, data vs vision, product vs service, authored vs systemic, premium vs F2P, central vision vs autonomous teams: each pole is right under specific conditions. Never argue the pole; argue the conditions. The condition tables are in `references/studio-doctrines.md` section 2.2 and in each section of `references/schools-of-thought.md`.

### 5. Borrow mechanisms, not surfaces

A practice works because of a causal mechanism under specific conditions. Supercell's kills work (on our reading) because of pre-committed bars and cheap redeployment of people, not because killing is good in itself. Copy the mechanism, check the conditions (Procedure C), and adapt the surface to the project.

### 6. Constraints generate style

Yokoi's withered technology, Rosewater's "restrictions breed creativity" and Lucas Pope's 1-bit rendering show that a chosen constraint focuses design. Pick one or two deliberate constraints per project (one thumb, one-minute runs, no text, three colours) and write them into the pillars.

### 7. Philosophy profiles

A profile is a named combination of doctrines for a recurring kind of project. Choosing one at concept time aligns every agent's defaults.

| Profile | Lead doctrines | Typical pillar shape | Red flags to watch |
|---|---|---|---|
| Hybrid-casual engine | Habby, King, Supercell kill discipline | "One thumb, one minute, one more run" | Meta bloat; energy walls; gear-chest randomness for minors |
| Craft puzzle | Nintendo, Blow, Playdead, Zach Gage | "Every level teaches one idea" | Filler levels; text tutorials; auteur scope creep |
| Cozy generosity | ConcernedApe, thatgamecompany, Daniel Cook | "Nothing is lost, everything grows" | Hidden grind; absence penalties; stress mechanics |
| Run-based depth | Mega Crit, Supergiant, LocalThunk | "Every run teaches, every death advances" | Meta-power trivializing runs; unreadable synergies |
| Live competitive | Riot, Supercell, Tencent | "Fair, fast, readable matches" | Pay-to-win; toxicity; matches too long for mobile |
| Collection live-ops | HoYoverse, Scopely (within doctrine 8) | "Collect, express, belong" | Opaque odds; content scope beyond capacity; FOMO |

**Concept score weights per profile** (for the 1–10 `scores` in `concept.schema.json`, where every score is "higher is better" and `production_cost` is already inverted: 10 = cheapest, so no conversion is needed before weighting; these profile weights sum to 1.0). The presets in `skills/concept-lab/references/scoring-rubric.md` and `skills/analogy-engine/scripts/analogy_score.py` (`default`, `agent_first`, `ua_led`, `premium_indie`) govern the actual scoring tool; where this table differs, the presets win, and the table shows how each philosophy profile would tilt them:

| Profile | market | novelty | fun_potential | feasibility | monetization | production_cost | agent_buildability |
|---|---|---|---|---|---|---|---|
| Hybrid-casual engine | 0.20 | 0.10 | 0.25 | 0.10 | 0.15 | 0.05 | 0.15 |
| Craft puzzle | 0.10 | 0.25 | 0.30 | 0.10 | 0.05 | 0.05 | 0.15 |
| Cozy generosity | 0.15 | 0.15 | 0.25 | 0.10 | 0.10 | 0.10 | 0.15 |
| Run-based depth | 0.10 | 0.20 | 0.30 | 0.10 | 0.05 | 0.10 | 0.15 |
| Live competitive | 0.20 | 0.10 | 0.25 | 0.15 | 0.15 | 0.05 | 0.10 |
| Collection live-ops | 0.25 | 0.10 | 0.20 | 0.15 | 0.15 | 0.05 | 0.10 |

`weighted = Σ weight × score`. `fun_potential` never weighs less than 0.20 in any profile (doctrines 1 and 2). These are philosophy-profile defaults; `concept-lab` ranks with its presets (named in the paragraph above). The `principal` may adjust weights per brief and should state the change in the concept's `rationale`.

## Decision procedures

### Procedure A — Choose a philosophy profile for a new project

1. Read the brief and fill `meta.target_audience` (age, segments, motivations) and `monetization_model`.
2. Name the scarcest resource (Core model 1).
3. Pick the closest profile (Core model 7). If none fits, combine at most two lead doctrines; more than two produces contradictory pillars.
4. Write 3–5 pillars in the profile's shape (Procedure G) and one or two deliberate constraints (Core model 6).
5. Copy the profile's red flags into `risks` and the relevant prohibitions into `scope.wont`.
6. Rank concepts in `concept-tournament` with the `concept-lab` preset that fits (see the weights note under Core model 7); use the profile's weights to explain or adjust that choice, not to replace the preset silently.
7. Record the chosen profile in the concept `rationale` and in `progress.md` via `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py progress "Profile: <name> because <reason>"`.

### Procedure B — Settle a recurring design debate

1. State the debate as a binary question with the decision it blocks.
2. Find its school in `references/schools-of-thought.md` and read "when each is right".
3. Check which conditions hold for this project, with evidence (contract fields, playtest data, market scan).
4. If the house position applies, adopt it. If deviating, write the reason into `risks` or a design-review report under `.gamestudio/reports/`.
5. Write the outcome where it will stop the argument recurring: a pillar, a `scope.wont` item, a `monetization.ethics` rule or a `kill_criteria` entry.
6. If evidence is missing, convert the debate into a test: a prototype question (`schools-of-thought.md` section 9) or a hypothesis with a sample size (`ab_test.py size`).

### Procedure C — Transfer test (before borrowing a studio practice)

| Step | Question | Record |
|---|---|---|
| 1 | What exactly is the practice? (one sentence, observable) | Practice |
| 2 | What mechanism makes it work? | Mechanism |
| 3 | Which 2–4 conditions did the source studio have? (budget, IP, audience, team size, era, platform) | Conditions |
| 4 | Which of those conditions do we share? | Shared count / total |
| 5 | Does it conflict with any house principle? | Conflict yes/no |
| 6 | What is the smallest version we can test? | Test |

Decision: conflict → do not borrow. Shared conditions below half → borrow the principle only, redesign the practice. Half or more → borrow and test the smallest version. Store the result in a deconstruction's `borrow_for_us` or the contract's `comparables[].borrow` and `change`.

*Worked example:* "Adopt Supercell's long soft launch with redesigns." Mechanism: cheap iteration on a live audience before scale. Conditions: (a) capacity to iterate cheaply, (b) budget to buy months of soft-launch installs, (c) enough players to read retention reliably. Shared: (a) yes, agents make iteration cheap; (b) no; (c) no — one of three. Result: borrow the principle (pre-set KPI bars, willingness to redesign), not the practice (months of paid soft launch); use a short soft launch with a fixed install target and a kill date.

### Procedure D — Philosophy lens review (fast critique)

Apply each lens to the build or design, record pass/fail and one line of evidence. Choose at least six for a feature review; all twelve for a contract review. Rules and sources are in `references/designer-philosophies.md`.

| # | Lens (designer) | Pass when |
|---|---|---|
| 1 | Empty room (Miyamoto) | The core verb is enjoyable without goals |
| 2 | One novelty (Yokoi) | Only one dimension is novel; the rest is proven |
| 3 | Risk and return (Sakurai) | Strong options carry visible proportional risk |
| 4 | Interesting decisions (Meier) | No dominant choice; consequences visible |
| 5 | Mastered pattern (Koster) | A new pattern arrives when the old one is mastered |
| 6 | Meaningful play (Zimmerman and Salen) | Every verb has immediate feedback and a later consequence |
| 7 | Skill chain (Cook) | No atom without feedback or a downstream atom |
| 8 | Loop sentence (Romero) | What the loop rewards matches the pillars |
| 9 | Fun is optimal (Rosewater) | The optimal strategy is the fun strategy |
| 10 | Perceived simulation (Sylvester) | Nothing simulated that the player cannot perceive |
| 11 | Nameable death (Miyazaki) | Every failure has a cause the player can name |
| 12 | Session ends half-done (Barone) | Each session ends with a goal almost complete |

Three or more fails on a feature means it returns to design before build; any fail on lens 9 or 11 in a shipped feature is a `major` finding.

### Procedure E — Kill or continue

1. Retrieve `kill_criteria` from the contract. If none exist, write them now, before looking at the latest data.
2. Gather evidence: fun checkpoint outcome, persona and bot playtests, simulation results, soft-launch KPIs vs `analytics.kpi_targets`.
3. Decide with the table:

| Situation | Decision |
|---|---|
| A kill criterion is met | Kill or pivot as pre-committed |
| No criterion met, but three loop iterations without a fun signal | Pivot the hook once; kill if the pivot fails |
| KPIs below target but a specific, testable cause is identified | Continue with a dated fix-and-retest plan |
| KPIs at target but the team has lost conviction | Continue; conviction is not a criterion. Re-examine pillars |

4. On a kill, run `/arcosian:postmortem` and save the lessons; a kill is a successful use of the process (Supercell's doctrine).

### Procedure F — Monetization ethics quick check

Before any offer, ad placement or randomized item enters the contract, answer: Would we show it to a 13-year-old's parent? Are real prices visible? Are odds published? Is any urgency real? Does it interrupt play? Can a non-payer still finish the core experience? Does it target a loss moment? Any "no" or "unsure" goes to the `monetization-designer` and `compliance-officer`; details and red lines are in `references/studio-doctrine-operationalized.md` section 9 and `references/schools-of-thought.md` section 6.

### Procedure G — Write pillars that carry a philosophy

Pillar formula: **verb or experience + feeling + constraint**, short enough to chant, testable by a playtest.

| Weak pillar | Strong pillar | Test |
|---|---|---|
| "Fun gameplay" | "One thumb, one minute, one more run" | Run length and input count from playthrough logs |
| "Beautiful art" | "Readable at a glance on the smallest phone" | Thumbnail test on the visual gate |
| "Deep strategy" | "Every pick changes the run" | Pick-rate vs win-rate spread |
| "Relaxing" | "Nothing is lost, everything grows" | No progress loss events in the economy simulation |

## Mobile specifics

- **Philosophies that translate directly:** Yokoi (build on mature, universal phone capabilities such as a single touch, the accelerometer and haptics, and budget for low-end Android), Nintendo teach-through-play (no text walls on a small screen), Supercell kill discipline (soft launch as the decision point), King funnels (level-by-level churn data), Habby one-thumb hybrid design, thatgamecompany prosocial constraint (emotes before chat in F2P social games), Dream Games speed (time per move as polish).
- **Philosophies that need adapting:** Souls-style death costs (cap the loss to about one minute of play), immersive-sim multiple solutions (fewer, clearly telegraphed routes on small screens), authored long-form narrative (chunk into 1–5 minute beats), premium pricing (mobile users expect free; premium works mainly via distinct quality, press, or subscription channels such as Apple Arcade), heavy juice (bounded by thermal and frame budgets).
- **Sessions and interruptions** turn every philosophy's pacing into 1–5 minute units: a kishōtenketsu level, a roguelite run, a cozy day and a competitive match all have to fit, pause and resume.
- **Market reality** (see the volatile sections of `references/studio-doctrines.md` and `references/schools-of-thought.md`): a flat market rewards retention, craft and live ops over volume, and hybrid-casual is where spending has grown fastest. Both favour profiles that combine fast prototyping with finishing quality.

## Anti-patterns

| Anti-pattern | Symptom | Fix |
|---|---|---|
| Cargo-cult doctrine | "Supercell kills games, so we kill" with no written criteria; "King uses lives, so we add lives" | Run the transfer test (Procedure C); write the mechanism and conditions |
| Quote as argument | Decisions justified by a famous name or an unsourced quote | Restate as a testable rule and test it on the build; flag misattributed quotes |
| Philosophy soup | Pillars drawn from four doctrines that contradict (cozy plus raids plus gacha) | One profile, at most two lead doctrines (Procedure A) |
| Survivorship bias | Studying only hits; ignoring the killed games and failed services | Read the cautionary entries (Zynga, hypercasual decline, live-service failures) |
| Auteur scope creep | Craft-studio ambitions on an agent budget; slice keeps growing | Principle 5: move items to `wont`; time-box polish per feature |
| Data theatre | A/B tests with no hypothesis or power; dashboards as decisions | Principle 4 template; `ab_test.py size` before launching |
| Juice as rescue | Effects added to make a weak loop feel fun | Fun checkpoint on grey boxes first (principle 2) |
| Ethics laundering | "It's industry standard" used to justify a dark pattern | Doctrine 8 is a floor; Procedure F |
| Doctrine drift | Pillars stop appearing in reviews after the first month | Milestone audit (`references/studio-doctrine-operationalized.md` section 13) |
| Clone dressed as fast-follow | Same game, new skin | "Genre yes, game no" (`references/schools-of-thought.md` section 19) |
| Premature service | Live-ops calendar before retention is proven | Earn the right to be a service (`references/schools-of-thought.md` section 5) |

## Using the ontology

Philosophies become operational only when they are written into the shared schemas (`game-ontology`):

| Philosophy element | Schema field | Notes |
|---|---|---|
| Profile, pillars, constraints | `contract.meta.pillars`, `contract.player_fantasy` | Pillars in the Procedure G formula |
| Borrowed precedent | `contract.meta.analogy`, `contract.meta.comparables[]` (`title`, `borrow`, `change`) | Transfer-test outcome goes in `borrow` and `change` |
| Scope discipline | `contract.scope` (`tier`, `must`, `should`, `wont`), `contract.kill_criteria`, `contract.risks` | Profile red flags go in `risks` |
| Teaching philosophy | `contract.ftue.steps[].teaches`, `ftue.aha_seconds_target` | One concept per step |
| Kishōtenketsu rhythm | level-spec `teach` (`teach`, `test`, `twist`, `reward`) | Levels alternate the four roles |
| Player-chosen difficulty | `contract.progression.difficulty` (`model`, `target_win_rate`, `dda`) | Chen's rule: voluntary first, hidden DDA as backstop |
| Ethics | `contract.monetization.ethics`, `monetization.ads.interstitial` | Red lines from principle 8 |
| Concept ranking | `concept.scores`, `concept.rationale` | Profile weights (Core model 7) |
| Studio lessons | deconstruction `psychology`, `innovations`, `weaknesses`, `lessons`, `borrow_for_us` | Fill `borrow_for_us` through Procedure C |
| Mechanic intent | mechanic-card `player_fantasy`, `aesthetics`, `failure_modes`, `mobile_fit` | Lens review findings land in `failure_modes` |

**Scripts and tools that serve philosophies.**
- Search this codex: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py kb "kishotenketsu level rhythm" --skill design-philosophies` (or the gateway's `kb_search`).
- Meier's bracket tuning: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/economy_sim.py --model PATH --runs 200` at ×0.5 and ×2 of the disputed value.
- King's sawtooth: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/difficulty_curve.py generate --levels 60 --pattern sawtooth --base 0.85 --floor 0.45 --period 10`; after launch, `difficulty_curve.py analyze --data CSV`.
- HoYoverse-style transparency: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gacha_calc.py --rate 0.006 --hard-pity 90 --json` to state the expected cost to a guarantee.
- Data-informed testing: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ab_test.py size --baseline 0.40 --mde 0.02`.
- Ethics floor: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/compliance_preflight.py --project DIR --platform all`.
- Record decisions: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py progress "<decision and doctrine reference>"`; review reports go under `.gamestudio/reports/`.

## Reference library

| File | What it contains | When to read it |
|---|---|---|
| `references/studio-doctrines.md` | Nearly thirty studios (Nintendo, Valve, Blizzard, Riot, Mojang, Supercell, King, Rovio, Dream Games, Playrix, Moon Active, Scopely, HoYoverse, Tencent, NetEase, Habby, Voodoo/Homa/SayGames, Zynga, FromSoftware, thatgamecompany, Playdead, Klei, Supergiant, Mega Crit, LocalThunk, Team Cherry, ConcernedApe): beliefs, practices, outcomes, how to apply, what to verify; convergence and split tables; studio rituals worth stealing; failure gallery; borrowing matrix; volatile facts | Choosing a profile; deconstructions; "what would studio X do"; filling `borrow_for_us` |
| `references/designer-philosophies.md` | Twenty-plus designers (Miyamoto to Ismail) plus short entries for eighteen more; one rule and one mobile example each; disagreements; rules index mapped to plugin checks | Lens reviews; tie-breaking design disputes; teaching a junior agent a principle |
| `references/schools-of-thought.md` | Eighteen debates with positions, evidence, when each is right and house positions; formulas for content runway, service break-even and test sizing; decision matrix; volatile market and regulation facts | Settling debates (Procedure B); product-vs-service and premium-vs-F2P calls; ethics and accessibility positions |
| `references/studio-doctrine-operationalized.md` | The ten house principles with enforcement mechanisms, settled decisions, failure signs, conflict rules with worked cases, milestone audit and doctrine-health metrics | Any time a principle is invoked; tier changes; resolving conflicts between principles |

## Related skills

- `design-theory` — formal frameworks (MDA, loops, flow, motivation models) that these philosophies build on.
- `game-case-studies` — full deconstructions of landmark games referenced here.
- `analogy-engine` — the "X meets Y" method and transfer of mechanisms between games.
- `player-psychology` — motivation, cognition and ethics of persuasion behind the doctrines.
- `mechanics-codex` — mechanic cards that the lens review critiques.
- `genre-playbooks` — genre-specific application of the profiles.
- `economy-design` and `monetization` — economies and offers inside the ethics floor.
- `progression-difficulty` and `level-design` — difficulty philosophy and kishōtenketsu in practice.
- `game-feel` and `mobile-ux` — juice budgets and readability craft.
- `player-analytics` — data-informed practice and metrics.
- `production` — scope, milestones and anti-crunch planning.
- `legal-ethics` and `accessibility-localization` — regulatory and access floors.
- `market-intel` — current market context for doctrine choices.
- `game-ontology` — the schemas this skill writes into.
- Process skills that should load this codex: `concept-lab`, `design-review`, `deconstruct`, `postmortem`; agents that rely on it most: `principal`, `game-designer`, `critic`.
