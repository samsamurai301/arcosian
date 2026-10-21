# Concept Generation Playbook: From Player to Scored Concept Card

This file is the studio's step-by-step concept generator. It starts from a target player and motivation, picks a proven core loop (a chassis), applies one or two transformation operators, adds a hook, checks the market for a gap, and scores the result with `concept.schema.json` so that concepts can compete in the `concept-tournament` workflow. It includes scoring anchors for all seven criteria, weight presets (implemented in `scripts/analogy_score.py`), a generation grid for batches, a fully worked example, and 25 concept seeds produced by the procedure. The seeds are illustrative outputs with pre-test estimates, not validated concepts: each must pass the market-gap check and a prototype before anyone treats it as a plan. Scoring numbers here are house heuristics aligned with `genre-playbooks` (agent-buildability and scope mappings).

## Contents

1. The pipeline at a glance
2. Step 0: constraints
3. Step 1: target player and motivation
4. Step 2: choose a proven core loop (chassis library)
5. Step 3: apply one or two operators (generation grid)
6. Step 4: add a hook (hook types and hook tests)
7. Step 5: market-gap check
8. Step 6: score with concept.schema.json (anchors, presets, gates, evidence caps)
9. Step 7: write the card and hand off to the tournament
10. Worked example: from "older block-puzzle players" to a scored card
11. 25 concept seeds produced by the procedure
12. Batch protocol for agents
13. Anti-patterns
14. Volatile facts (as of Oct 2026 — verify before relying)

---

## 1. The pipeline at a glance

```
Step 0  constraints ─┐
Step 1  player + motivation ──► Step 2  proven core loop (chassis)
                                  │
                                  ▼
                        Step 3  apply 1–2 operators ──► Step 4  hook (emergent structure)
                                                            │
                                                            ▼
                        Step 5  market-gap check ──► Step 6  score (7 criteria, preset weights, gates)
                                                            │
                                                            ▼
                        Step 7  concept card (.gamestudio/concepts/<id>.concept.json) ──► concept-tournament
```

| Step | Output | Owner (agent) | Time box per concept |
|---|---|---|---|
| 0 | Constraint sheet | `arcosian:producer` | once per batch |
| 1 | Segment card | `arcosian:game-designer`, `arcosian:market-analyst` | 10 min |
| 2 | Chassis pick with loop line | `arcosian:game-designer` | 10 min |
| 3 | Transformed loop + operator codes | `arcosian:game-designer` | 15 min |
| 4 | Hook sentence + pitch line | `arcosian:game-designer` | 10 min |
| 5 | Gap statement + saturation score | `arcosian:market-analyst` | 20–40 min |
| 6 | Scores + weighted total | judges in `concept-tournament`; `arcosian:critic` | 10 min |
| 7 | Validated JSON card | any | 5 min |

---

## 2. Step 0: constraints

Write these once per batch (from `genre-playbooks` procedure A step 1). Concepts that violate a hard constraint are not generated.

| Constraint | Example value | Effect |
|---|---|---|
| Minimum audience age | 13 | Under 13 rules out wagers, paid randomness, behavioural ads (`legal-ethics`) |
| Platforms and orientation | iOS + Android, portrait | Rules out two-stick landscape chassis unless justified |
| Storefronts | US, EU, JP | Sets IAP vs ads mix expectations |
| Team and calendar | 1 developer + agents, 4 months to soft launch | Scope ≤ S–M; production_cost weight up |
| Art capability | 2D only | Rules out 3D-heavy chassis |
| Backend appetite | offline or async | Rules out real-time PvP |
| Monetization model | hybrid | Needs both a rewarded-ad moment and an IAP moment |
| Ethics rules | contract `monetization.ethics` | Ethics gate in step 6 |
| Scoring preset | `agent_first` | Weights in step 6 |

---

## 3. Step 1: target player and motivation

### 3.1 Segment card

```
Segment:        <plain words, e.g. "lapsed block-puzzle players 35-60, mostly US/EU">
Play context:   <when and where: commute, evening sofa, work breaks>
Session habit:  <length x sessions/day>
Top motivations: <two from the Quantic Foundry model>
Current games:  <3 titles they play now>
Unmet need:     <what those games do not give them, from reviews or interviews>
Spend profile:  <ads-tolerant | small IAP | deep spenders | premium buyers>
```

### 3.2 Motivations (Quantic Foundry Gamer Motivation Model, Nick Yee and colleagues)

Six clusters, twelve motivations: Action (destruction, excitement), Social (competition, community), Mastery (challenge, strategy), Achievement (completion, power), Immersion (fantasy, story), Creativity (design, discovery). Pick the top two for the segment and write them into `target_audience.motivations`.

### 3.3 Motivation → candidate chassis (house mapping; see also `genre-playbooks` procedure A)

| Top-two motivations | Chassis to consider (section 4 IDs) | Operators that usually help |
|---|---|---|
| challenge + strategy | K05 block, K09 logic, K16 roguelite deck-builder, K17 tower defense | OP15, OP19, OP23 |
| completion + power | K03 merge-2, K10 idle clicker, K15 survivor-like, K12 farming | OP14, OP29, OP16 |
| design + discovery | K12 farming, K21 absence pet, K06 tile-match, K22 sandbox builder | OP29, OP27, far analogy |
| fantasy + story | K01 match-3 + renovation, K12 farming | OP30, OP14 |
| competition + community | K18 async PvP, K19 async raid, K20 social deduction | OP11, OP18, OP22 |
| excitement + destruction | K14 runner, K15 survivor-like, K13 arcade | OP05, OP03, OP17 |
| completion + design | K03 merge-2, K12 farming, K06 tile-match | OP14, OP29 |
| challenge + completion | K01 match-3, K02 blast, K04 sort, K09 logic | OP14, OP28 |

---

## 4. Step 2: choose a proven core loop (chassis library)

A chassis is a core loop with market evidence. AB is the agent-buildability score (1–5) from `genre-playbooks`; scope from its comparison table. Saturation notes are qualitative; step 5 replaces them with evidence.

| ID | Chassis | Core loop line | Session | Monetization fit | AB | Scope | Saturation note |
|---|---|---|---|---|---|---|---|
| K01 | Swap match-3 (+ renovation) | swap → match → clear goals → star → renovate | 3–10 min | IAP + rewarded | 5 | L | Consolidated |
| K02 | Blast / collapse | tap group → clear → goals → reward | 3–10 min | IAP + rewarded | 5 | L | Consolidated |
| K03 | Merge-2 + orders | generate → merge → fulfil order → unlock | 5–15 min | IAP (energy) | 4 | M–L | Crowded |
| K04 | Sort / jam | pour or move → sort → clear | 2–8 min | Ads + light IAP | 5 | S | Crowded, fast-moving |
| K05 | Block puzzle | place pieces → clear lines → score | 3–15 min | Ads | 5 | S | Dominated by a few hits |
| K06 | Tile-match (triple) | tap tile → tray → triple clears | 5–20 min | Ads + IAP | 5 | S–M | Crowded |
| K07 | Screw / pin | unscrew → drop → clear colours | 2–8 min | Ads + light IAP | 3 | S–M | Trend-driven |
| K08 | Word | form words → fill grid → progress | 5–15 min | Ads + hints | 4 | S–M | Stable, older audience |
| K09 | Logic (nonogram, sudoku, deduction) | deduce → fill → solve | 5–20 min | Ads / premium / subscription | 5 | S | Many small titles |
| K10 | Idle clicker | earn → upgrade → automate → prestige | 1–5 min many | Rewarded + IAP | 5 | S | Crowded |
| K11 | Arcade idle / tycoon | walk and carry → serve → expand → hire | 5–15 min | Rewarded + IAP | 4 | M | Crowded |
| K12 | Farming | plant → wait → harvest → fulfil orders → expand | 5–15 min | IAP | 3 | L | Consolidated |
| K13 | Arcade score attack | play → die → retry for score | 1–5 min | Ads / premium | 4 | S | Commodity |
| K14 | Endless runner | run → dodge → collect → upgrade | 2–6 min | Ads + IAP | 3 | M | Consolidated |
| K15 | Survivor-like | move → auto-attack → level up draft → survive | 10–20 min runs | IAP + rewarded or premium | 3 | M | Crowded |
| K16 | Roguelite deck-builder | draft card → fight → path choice → escalate | 10–30 min runs | Premium or IAP | 4 | M | Growing on PC, thinner on mobile |
| K17 | Tower defense | place → upgrade → survive waves | 3–10 min | Hybrid | 4 | M | Stable |
| K18 | Async turn-based PvP | take turn → wait → opponent turn → result | 2–10 min | IAP + ads | 3 | M | Stable |
| K19 | Async raid base | build base → raid others → loot → upgrade | minutes, many check-ins | IAP | 3 (estimate) | L | Consolidated |
| K20 | Social deduction | task or talk → accuse → vote → reveal | 5–20 min | Ads + IAP cosmetics | 3 | M | Real-time dominated |
| K21 | Absence pet / collection | set up → leave → return → collect | 1–3 min, many | IAP cosmetics | 4 (estimate) | S | Niche |
| K22 | Sandbox builder | gather → build → share | 5–20 min | IAP cosmetics | 2–3 (estimate) | M–L | UGC platforms dominate |
| K23 | Time management | serve queue → upgrade → next level | 3–10 min | IAP + rewarded | 4 | M | Consolidated |
| K24 | Daily ritual puzzle | one puzzle → share → streak | 2–5 min, daily | Subscription / premium / light ads | 5 | S | Newspaper brands strong |

---

## 5. Step 3: apply one or two operators (generation grid)

Operators and their procedures are in `references/transformation-operators.md`. To generate many concepts quickly and with diversity, use a **chassis × operator grid**:

1. Pick 4–6 chassis from step 2 that fit the segment.
2. Pick 5–8 operators from the selection matrix (`transformation-operators.md` section 8) that fit the batch goal.
3. Fill each cell with a one-line transformed loop in 2 minutes. Empty cells are fine.
4. For promising cells, add a far source (`references/cross-domain-sources.md`) for the hook or the meta.
5. Prune cells that break the expectation budget (more than one broken expectation) or a hard constraint.

Example grid fragment (segment: older block-puzzle players; goal: retention without energy):

| Chassis \ Operator | OP01 transplant | OP14 meta graft | OP23 ritual | OP17 session shape | OP29 collection |
|---|---|---|---|---|---|
| K05 block puzzle | bowling frame scoring → S16 | delivery orders + town → S03 | one shared board per day | 10-frame runs | postcard album per town |
| K09 logic | — | fossil museum → S14 | daily tactics → S05 | 5-minute timed sprint | species album |
| K04 sort | pantry freshness ordering → S22 | restaurant prep meta | daily sort with shared seed | — | ingredient album |

Rules: maximum two operators per concept on different layers; apply core-layer operators before meta-layer ones; run the ethics gate after OP13, OP18 or OP29.

---

## 6. Step 4: add a hook

The hook is the emergent structure (`references/analogy-method.md` section 4.4): true in the concept, false in both the chassis and the source. It goes in `concept.hook`.

### 6.1 Hook types

| Type | What is new | Example from the lineages |
|---|---|---|
| Rule hook | One inverted or transplanted rule | No aiming (Vampire Survivors) |
| Stakes hook | A new reason each match matters | Snap and retreat (Marvel Snap) |
| Structure hook | A new session or time structure | One shared puzzle a day (Wordle) |
| Social hook | A new relation between players | Teams feeding lives (Toon Blast) |
| Fantasy hook | A new role or perspective | Be the pathogen (Plague Inc.) |
| Bridge hook | The meta changes the core | Restored keep wakes new golem families (example concept card) |
| Ritual hook | A real-world rhythm drives play | Sleep as input (Pokémon Sleep) |

### 6.2 Hook tests (score 0–2 each; keep hooks scoring ≥ 7 of 10)

| Test | 0 | 1 | 2 |
|---|---|---|---|
| Visible in 3 seconds of muted gameplay | Needs text | Visible after setup | Visible immediately |
| Emergent | Exists in chassis or source | Partly new | True only in the blend |
| Verb-level | Theme or art only | Changes a reward or goal | Changes what the player does or decides |
| Retention link | One-time novelty | Supports days | Creates a reason to return tomorrow |
| Tell-a-friend sentence | Cannot be said in one line | Needs explanation | One line a player would repeat |

---

## 7. Step 5: market-gap check

The goal is evidence that a segment lacks this blend, or gets it at poor quality. Run it through the `market-scan` process skill (`/arcosian:market-scan`) or delegate to `arcosian:market-analyst`; `market-intel` holds the method and sources.

### 7.1 Procedure
1. **Existence search (15 min).** Search both stores with at least five phrasings: chassis term + hook term ("block puzzle bowling", "block puzzle frames", "bowling puzzle"), the "X meets Y" line, and the source's own name with the chassis. Add Steam for premium chassis. Record title, developer, last update, rating, rating count.
2. **Creative check (10 min).** Search ad libraries (for example Meta's Ad Library) for the chassis plus hook. Ads show how competitors *market* the blend and whether creative fatigue exists.
3. **Saturation score (1–5)**, following `genre-playbooks` procedure A step 5: lower for top-10 concentration by titles older than 3 years with deep live-ops and for creative fatigue; raise for new entrants in the last 6–12 months and for open innovation vectors.
4. **Clone rule.** If 3 or more live titles already ship the same blend with good ratings and updates in the last 6 months, it is not a gap: drop the concept or lower novelty by 2–3 points and name the edge you would compete on (quality, audience, region, ethics).
5. **Gap typing.** Name the gap: audience, platform, quality (from 1–3-star review clusters), monetization-ethics (e.g. "no energy walls"), theme, session shape, or region.
6. **Write the gap statement** into `concept.rationale`: "For <segment>, no current title offers <relation> in <session/platform>; evidence: <titles and dates>; risk: <...>".

### 7.2 Gap statement examples

| Gap type | Statement shape |
|---|---|
| Audience | "Survivor-likes target young men; none offer a cosy theme and no-fail runs for players 35+" |
| Platform | "This premium PC rule has no portrait one-thumb version" |
| Quality | "Top three titles' 1–3-star reviews cluster on forced interstitials before the first win" |
| Monetization-ethics | "All competitors gate with energy; an ads-led no-energy version is untested" |
| Session | "Matches last 8+ minutes; nobody offers a 2-minute version" |

---

## 8. Step 6: score with concept.schema.json

`concept.scores` holds seven criteria, each 1–10, **higher is better** (production_cost 10 = cheapest; feasibility 10 = lowest risk). Unknown keys are rejected by the schema. `weighted_total` is optional and computed.

### 8.1 Scoring anchors

| Criterion | 1–2 | 3–4 | 5–6 | 7–8 | 9–10 |
|---|---|---|---|---|---|
| `market` (= 2 × saturation score from step 5) | Saturated, old incumbents, creative fatigue, shrinking | Consolidated, little growth | Competitive but with room for a clear edge | Growing segment, few strong entrants | Open, growing, proven demand, no strong incumbent |
| `novelty` | Literal clone | Theme swap or feature tweak | One relation changed in a known chassis | Emergent hook absent from top titles and recent entrants | New genre-level relation (inversion creating a new decision) |
| `fun_potential` | Core verb unpleasant in a toy test | Fun for a minute; no variation | Plausible loop, untested | Paper or greybox shows voluntary repeat play | Playtests show unprompted repeat runs and invented goals |
| `feasibility` (10 = low risk) | Unsolved technology or design risk | Several hard risks (netcode, physics determinism, 3D animation) | One hard risk with a known mitigation | Known techniques, minor risks | Deterministic, offline, proven tech, small rule set |
| `monetization` (ethical potential) | No spend moment; ads do not fit | Weak or ethically doubtful spend moment | One clear ethical spend moment | Ads and IAP both fit naturally | Several proven ethical spend moments with genre precedent |
| `production_cost` (scope from `genre-playbooks`) | XL (1–2) | L (3–5) | M (6–7) | S–M (7–8) | S (8–10) |
| `agent_buildability` | AB 1 → 2 | AB 2 → 4 | AB 3 → 6 | AB 4 → 8 | AB 5 → 10 |

### 8.2 Evidence caps (house rules)

| Evidence available | Cap |
|---|---|
| No prototype | `fun_potential` ≤ 7 |
| Paper prototype only | `fun_potential` ≤ 8 |
| Greybox with persona or bot runs | `fun_potential` ≤ 9 |
| No market scan (step 5 not run) | `market` ≤ 6 and `novelty` ≤ 7 |

`analogy_score.py concept --evidence none|paper|greybox|playtest` applies the `fun_potential` cap automatically.

### 8.3 Weight presets (implemented in `scripts/analogy_score.py`)

| Criterion | default | agent_first | ua_led | premium_indie |
|---|---|---|---|---|
| market | 1.5 | 1 | 2 | 1 |
| novelty | 1 | 1 | 1.5 | 2 |
| fun_potential | 2 | 2 | 1.5 | 2.5 |
| feasibility | 1 | 1.5 | 1 | 1 |
| monetization | 1 | 1 | 1.5 | 0.5 |
| production_cost | 1 | 1.5 | 1 | 1.5 |
| agent_buildability | 1 | 2 | 1 | 1 |
| **Sum of weights** | 8.5 | 10 | 9.5 | 9.5 |

`weighted_total = Σ(score × weight) ÷ Σ(weight)`, rounded to 2 decimals. The `default` preset reproduces the example card (`scripts/schemas/examples/example.concept.json`): 63.5 ÷ 8.5 = 7.47.

### 8.4 Gates and tie-breakers
- **Gates** (default): `fun_potential` ≥ 5 and `feasibility` ≥ 4. A concept that fails a gate is parked regardless of its total. The ethics gate is binary and comes first: any hard ethics or legal violation kills the concept.
- **Tie-breakers** (totals within 0.15): higher `fun_potential`, then higher `agent_buildability`, then fewer high-impact risks.

### 8.5 Commands

```
python3 ${CLAUDE_PLUGIN_ROOT}/skills/analogy-engine/scripts/analogy_score.py concept --card .gamestudio/concepts/c16_frame_blast.concept.json --preset agent_first --evidence none --write
python3 ${CLAUDE_PLUGIN_ROOT}/skills/analogy-engine/scripts/analogy_score.py concept --scores "market=6,novelty=6,fun_potential=7,feasibility=9,monetization=6,production_cost=9,agent_buildability=10"
python3 ${CLAUDE_PLUGIN_ROOT}/skills/analogy-engine/scripts/analogy_score.py rank --dir .gamestudio/concepts --preset agent_first
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py validate .gamestudio/concepts/c16_frame_blast.concept.json
```

---

## 9. Step 7: write the card and hand off to the tournament

1. Write `.gamestudio/concepts/<id>.concept.json` with at least: `schema_version`, `id`, `title`, `status: "draft"`, `logline`, `analogy`, `genre`, `player_fantasy`, `core_loop`, `hook`, `pillars` (3–5), `target_audience`, `monetization_model`, `comparables` (`title`, `borrow`, `change`), `scores`, `risks`, `kill_criteria`, `rationale`.
2. Optional extension keys (the concept schema allows extra top-level keys): `operators` (for example `["OP01", "OP17"]`) and `analogy_fitness` (the AFS result of the main borrowed relation).
3. Run `analogy_score.py concept --card ... --write` and `gs.py validate ...`.
4. Log: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py progress "Concept c16 Frame Blast drafted: agent_first 7.90, AFS 100 (bowling frames)"`.
5. Hand the batch to `/arcosian:concept-tournament` (via the `concept-lab` process skill). Judges re-score; `arcosian:critic` attacks every score above 7; the winner seeds the design contract (`new-game`).

---

## 10. Worked example: from "older block-puzzle players" to a scored card

**Step 0.** Solo developer plus agents, 2D, offline, hybrid model, portrait, age 13+, preset `agent_first`.

**Step 1.** Segment: lapsed and current block-puzzle players aged 35–60 in the US and EU; evening and break sessions of 5–15 minutes; motivations *challenge* and *completion*; current games: Block Blast!, Woodoku-style puzzles, solitaire. Unmet need (hypothesis): endless play has no natural end and no sense of a "good game", so sessions drift and stop without satisfaction.

**Step 2.** Chassis K05 block puzzle: place three pieces → clear rows and columns → score; AB 5; scope S.

**Step 3.** Operators: OP01 mechanic transplant from bowling (sports source S02: strike and spare lookahead scoring) and OP17 session shape (fixed 10-frame runs). Layers: scoring rule (core) and session structure (wrapper). AFS of the bowling transplant:

| Source relation | Target relation | Status |
|---|---|---|
| `CONSISTS_OF(game, 10 frames)` | A run is 10 frames of N trays each | mapped |
| `CAUSES(strike, bonus = next two rolls)` | A full-board clear ("strike") adds the next two frames' line clears as bonus | mapped |
| `CAUSES(spare, bonus = next roll)` | Clearing all lines placed in a frame ("spare") adds the next frame's first tray | mapped |
| `ENABLES(lookahead bonus, comeback and chase)` | Late strikes still swing the total; a "perfect game" is a chase goal | mapped |
| Support: discrete attempts, visible scoreboard | Frames give discrete attempts; a bowling-style scorecard shows them | present |

RC 1.0, HC 1.0, SF 1.0, V 0, L 0 → AFS 100 → GO.

**Step 4.** Hook: "every run has a perfect game to chase: clear the board to strike and carry the bonus forward". Hook tests: visible in 3 s (2: scorecard and strike burst), emergent (2), verb-level (1: changes decisions about when to clear), retention link (2: daily "best game" and perfect-game chase), tell-a-friend (2) → 9/10.

**Step 5.** Market check (to run): store and ad-library searches for "block puzzle bowling", "block puzzle frames", "puzzle 300 perfect game". Pre-scan saturation estimate 3 (block puzzles are dominated by a few hits, but the frame structure is not evidently present) → market 6, pending evidence.

**Step 6.** Scores (pre-test, evidence none): market 6, novelty 6, fun_potential 7 (cap), feasibility 9, monetization 6 (rewarded "re-roll the tray" and interstitials between runs), production_cost 9 (scope S), agent_buildability 10 (AB 5). Totals: default 7.41; agent_first 7.90. Gates pass.

**Step 7.** Card:

```json
{
  "schema_version": "1.0",
  "id": "c16_frame_blast",
  "title": "Frame Blast",
  "status": "draft",
  "logline": "A block puzzle played in ten-frame games, where clearing the whole board is a strike that carries bonus points forward.",
  "analogy": "Block Blast meets bowling",
  "genre": "puzzle / block puzzle",
  "player_fantasy": "I bowl a perfect game with puzzle pieces.",
  "core_loop": "place three pieces -> clear lines -> finish the frame -> strike or spare bonus -> next frame",
  "hook": "Full-board clears are strikes that add the next two frames to your score, so every run has a perfect game to chase.",
  "pillars": ["Calm placement, tense finishes", "Every run has a clean ending", "A perfect game is always possible", "One thumb, no timers"],
  "target_audience": {"age_min": 13, "segments": ["block-puzzle players 35-60, US and EU"], "motivations": ["challenge", "completion"]},
  "monetization_model": "hybrid",
  "comparables": [
    {"title": "Block Blast!", "borrow": "three-piece tray, free placement, row and column clears", "change": "fixed 10-frame runs with lookahead bonus scoring"},
    {"title": "Ten-pin bowling scoring", "borrow": "strike and spare bonuses that add future frames", "change": "a strike is a full-board clear; a spare clears every line placed in the frame"}
  ],
  "scores": {"market": 6, "novelty": 6, "fun_potential": 7, "feasibility": 9, "monetization": 6, "production_cost": 9, "agent_buildability": 10, "weighted_total": 7.9},
  "operators": ["OP01", "OP17"],
  "analogy_fitness": {"source": "bowling scoring", "afs": 100, "verdict": "GO"},
  "risks": [
    {"id": "R1", "risk": "Strikes too rare or too common", "likelihood": "medium", "impact": "high", "mitigation": "bot sims (greedy and random) to tune tray weights; target a strike in roughly one of five frames for a skilled bot"},
    "Frame structure may shorten sessions and reduce interstitial inventory"
  ],
  "kill_criteria": [
    "Bot sims cannot reach a strike-rate band that a greedy bot hits 2-4x more often than a random bot",
    "Persona playtest: fewer than 6 of 10 personas start a second run unprompted",
    "Market check finds 3+ live, well-rated block puzzles with frame scoring"
  ],
  "rationale": "Agent-first preset 7.90 (default 7.41). Deterministic 2D grid sim with bot verification. Gap hypothesis: endless block puzzles lack a satisfying end; to be confirmed by the market check."
}
```

Note: the `weighted_total` above is the `agent_first` value (the batch preset); record which preset you used in `rationale`.

---

## 11. 25 concept seeds produced by the procedure

These seeds were generated with steps 1–4 and scored with **pre-test, pre-scan estimates** (evidence none and no market scan: `fun_potential` ≤ 7, `market` ≤ 6, `novelty` ≤ 7). They are inputs to a tournament, not recommendations. Step 5 has **not** been run for any of them: similar games may already exist. Score order in the table: market / novelty / fun / feasibility / monetization / production_cost / agent_buildability. Totals computed with `analogy_score.py concept` (default and agent_first presets); all pass the default gates.

### 11.1 Summary table

| ID | Title | Line | Chassis | Operators | Scores (Mk/Nv/Fn/Fe/Mo/PC/AB) | Default | Agent-first |
|---|---|---|---|---|---|---|---|
| S01 | Sourdough Club | Neko Atsume meets a sourdough starter | K21 | OP16, OP11 + far (fermentation) | 5/7/6/8/5/8/8 | 6.53 | 6.90 |
| S02 | Snap Letters | Words With Friends meets Marvel Snap | K18 | OP18, OP17 | 5/7/7/7/5/8/6 | 6.41 | 6.55 |
| S03 | Pebble Courier | Block Blast meets Hay Day orders | K05 | OP14, OP02 + far (logistics) | 6/5/7/9/6/9/10 | 7.29 | 7.80 |
| S04 | Hive Run | Can't Stop meets an idle bee farm | K21/K10 | OP16, OP01 (push-your-luck) | 5/7/6/8/6/7/8 | 6.53 | 6.85 |
| S05 | Daily Breach | Into the Breach meets Wordle | K09/K24 | OP23, OP08 | 5/7/7/8/4/9/10 | 7.00 | 7.55 |
| S06 | Swarm Lord | Vampire Survivors where you are the horde | K15 | OP04 | 6/7/7/5/6/6/6 | 6.24 | 6.15 |
| S07 | Rush Hour Roguelite | Cooking Fever meets Slay the Spire | K23 | OP15 | 6/6/7/6/6/6/6 | 6.24 | 6.20 |
| S08 | Night Market | Merge Mansion meets a night market | K03 | OP06 (day/night phases), B32-lite haggling | 5/5/6/7/7/5/8 | 6.06 | 6.30 |
| S09 | Tidepool | Neko Atsume meets predator–prey cycles | K21 | OP03 (balance, not maximise) + far (ecosystems) | 4/7/6/6/4/7/8 | 5.88 | 6.25 |
| S10 | Ghost Fleet | Battleship meets Clash of Clans | K19 | OP19, OP01 (deduction) | 6/7/7/6/7/6/6 | 6.47 | 6.40 |
| S11 | Paper Lantern | Monument Valley meets origami | spatial puzzle | OP12 (fold) + far (craft) | 4/7/7/5/4/5/6 | 5.53 | 5.60 |
| S12 | Stitch Saga | Two Dots meets knitting patterns | connect puzzle | OP02 (relational theme), OP29 | 5/6/6/8/6/7/10 | 6.65 | 7.15 |
| S13 | Week of Wolves | Werewolf, one vote a day | K20 | OP23, OP06 (async) | 5/7/6/5/4/7/6 | 5.71 | 5.80 |
| S14 | Fossil Survey | Minesweeper meets a museum | K09 | OP14, OP29 | 6/5/7/9/5/9/10 | 7.18 | 7.70 |
| S15 | Peloton | Can't Stop meets the Tour de France | turn-based race | OP06, far (cycling classifications) | 3/7/6/7/4/7/8 | 5.82 | 6.30 |
| S16 | Frame Blast | Block Blast meets bowling | K05 | OP01, OP17 | 6/6/7/9/6/9/10 | 7.41 | 7.90 |
| S17 | Swiss Weekend | Puzzle tournaments with chess Swiss pairing (live-ops feature) | K01/K02 events | OP11, far (Swiss system) | 5/5/6/7/6/8/8 | 6.29 | 6.65 |
| S18 | Bonsai Days | Tamagotchi meets bonsai | K21/K24 | OP23, OP03 | 4/7/5/8/4/8/8 | 6.00 | 6.50 |
| S19 | Relay Rush | Subway Surfers meets a relay race | K14 | OP11, far (relay) | 6/5/6/6/6/6/6 | 5.88 | 5.90 |
| S20 | Grid Tycoon | AdVenture Capitalist meets Power Grid | K10 | OP16, OP13 (dynamic market) | 6/6/6/8/7/8/10 | 7.06 | 7.50 |
| S21 | Mahjong Run | Balatro meets mahjong | K16 | OP01, OP15 | 5/4/7/8/5/8/10 | 6.65 | 7.20 |
| S22 | Pantry Pack | Block puzzle meets a fridge that must stay fresh | K05/K04 | OP02 (relational), far (cooking) | 5/5/6/8/6/8/10 | 6.65 | 7.20 |
| S23 | Crop Rotation | Hay Day meets crop rotation | K12 | OP32, far (gardening) | 5/6/6/6/7/4/6 | 5.71 | 5.70 |
| S24 | Kintsugi | Jigsaw meets kintsugi | assembly puzzle | OP30, far (craft) | 4/6/6/6/4/6/6 | 5.41 | 5.60 |
| S25 | Last Stop | Mini Metro meets Slay the Spire | network puzzle | OP15 | 5/6/7/7/5/8/8 | 6.53 | 6.85 |

**Shortlist by agent_first total**: S16 Frame Blast (7.90), S03 Pebble Courier (7.80), S14 Fossil Survey (7.70), S05 Daily Breach (7.55), S20 Grid Tycoon (7.50). Note the pattern: deterministic 2D systemic chassis dominate under the agent_first preset; under `ua_led` or `premium_indie` the order changes. Run `analogy_score.py rank` with the batch's preset rather than reusing this list.

### 11.2 Seed details

**S01 Sourdough Club.** *Player*: cosy-game adults 25–45; design, completion. *Loop*: feed starter → leave → it rises while away → bake → collect loaves and recipes. *Hook*: you can gift a "split" of your starter to a friend, and every loaf records its lineage, so a friend group's breads share a family tree. *Gap hypothesis*: absence-driven cosy games are mostly animal-themed. *Kill*: fewer than 20% of a friends-test cohort gift a split in week one. *Main risk*: thin decisions; needs recipe discovery depth.

**S02 Snap Letters.** *Player*: adult word-game players; competition, strategy. *Loop*: play a word → opponent plays → optionally double the stake → concede or continue → five rounds. *Hook*: your hidden rack becomes a bargaining chip (worked example A in `references/analogy-method.md`). *Gap hypothesis*: async word duels are stable and old; no wager layer in the leaders (verify). *Kill*: abandoned-match rate not at least 5 points lower than control in an A/B. *Main risk*: gambling resemblance; stakes must be rank stars only.

**S03 Pebble Courier.** *Player*: older block-puzzle players; challenge, completion. *Loop*: place pieces → clear lines → each clear ships a van → orders fulfilled → town grows. *Hook*: orders ask for line compositions (colours), so placement serves a visible town. *Gap hypothesis*: adventure modes exist, logistics orders do not (verify). *Kill*: order mode shows no D7 lift over an endless-only cell. *Main risk*: novelty is modest; the creative must sell the town.

**S04 Hive Run.** *Player*: casual sim players; completion, discovery. *Loop*: send bees on a flight → push further for rarer nectar or return → weather may force a return and lose the flight's unbanked haul → hive grows idle. *Hook*: push-your-luck inside an idle loop; only in-flight gains are ever at risk. *Gap hypothesis*: push-your-luck is rare in idle. *Kill*: bot EV analysis finds a single dominant stop rule. *Main risk*: risk mechanic feels punishing to calm players.

**S05 Daily Breach.** *Player*: puzzle-literate adults; strategy, challenge. *Loop*: one 3-turn tactics snapshot per day → solve → share a spoiler-free survival grid → streak. *Hook*: perfect-information tactics as a newspaper-style daily. *Gap hypothesis*: daily logic is crowded, daily tactics less so (verify). *Kill*: day-2 return below 30% of day-1 players in a soft test, or the generator cannot produce 60 solver-verified puzzles at target difficulty. *Main risk*: low session count limits revenue; consider subscription or premium.

**S06 Swarm Lord.** *Player*: action fans 16–34; destruction, excitement. *Loop*: steer a swarm → absorb villagers to grow → overwhelm a hero boss who drafts upgrades against you. *Hook*: perspective flip of the survivor-like. *Gap hypothesis*: survivor-likes crowded; horde-control games fewer (verify carefully). *Kill*: toy test, 3 of 5 testers report "no control" of the swarm with one thumb; or low-tier devices below 30 fps with 300 units. *Main risk*: real-time feel and performance (AB 3).

**S07 Rush Hour Roguelite.** *Player*: time-management players wanting depth; challenge, strategy. *Loop*: serve a timed shift → draft one of three recipes or appliances → combos change how orders resolve → escalating shifts. *Hook*: each shift is a run with build-defining combos. *Gap hypothesis*: the genre is level-ladder based. *Kill*: median run longer than 12 minutes, or fewer than 3 viable build archetypes in bot sims. *Main risk*: timing input on phones (factor T).

**S08 Night Market.** *Player*: merge players; completion, design. *Loop*: merge goods by day → sell at a night market where each customer makes one counter-offer → reinvest. *Hook*: a two-phase day with a light bargaining decision. *Gap hypothesis*: merge-2 is crowded; phase structure differentiates (weakly). *Kill*: the night step adds more than 30 seconds per session without raising session satisfaction in tests. *Main risk*: item-art volume (scope M–L).

**S09 Tidepool.** *Player*: cosy and discovery players. *Loop*: add species to a rock pool → watch predator–prey cycles → keep the pool balanced → rare species appear only in balanced pools. *Hook*: success is a stable cycle, not a bigger number. *Gap hypothesis*: balance-focused casual sims are rare. *Kill*: after three sessions, 3 of 5 testers cannot predict the effect of adding a predator. *Main risk*: readability of an oscillating system.

**S10 Ghost Fleet.** *Player*: strategy-lite players; competition, strategy. *Loop*: hide your fleet layout as your base → raid others with limited sonar shots → loot → upgrade. *Hook*: deduction replaces troop micro in async raids. *Gap hypothesis*: async raid bases are visible to attackers. *Kill*: attack sessions longer than 3 minutes or deduction rated "random" by personas. *Main risk*: backend for async PvP (AB 3).

**S11 Paper Lantern.** *Player*: premium art-puzzle players; discovery, design. *Loop*: fold the diorama along creases → reconnect paths → guide a lantern-bearer. *Hook*: the level itself is folded; one unfold gesture rewinds. *Gap hypothesis*: folding puzzles exist but are few (verify). *Kill*: 2 of 5 testers fail the first fold without help. *Main risk*: authored 3D content cost.

**S12 Stitch Saga.** *Player*: crafts-interested casual players 35–60; completion, design. *Loop*: connect stitches row by row to match a pattern → each level knits a row → garments complete. *Hook*: the pattern is the level goal, and the garment grows visibly. *Gap hypothesis*: craft-themed puzzles are niche. *Kill*: the theme does not lift creative CTR over a generic theme. *Main risk*: pattern constraint narrows level variety (check bot difficulty variance).

**S13 Week of Wolves.** *Player*: friend groups 18–35; community, competition. *Loop*: one night action and one vote per day for a week, with daily clue drops. *Hook*: social deduction at group-chat cadence. *Gap hypothesis*: social deduction is mostly real-time. *Kill*: groups of 6 or more fail to form in over 70% of invites. *Main risk*: group formation; moderation.

**S14 Fossil Survey.** *Player*: logic-puzzle adults; challenge, completion. *Loop*: deduce fossil locations from clue numbers (solver-guaranteed, no guessing) → dig → assemble species in a museum. *Hook*: logic meets a collection meta. *Gap hypothesis*: pure logic apps rarely carry a collection meta (verify). *Kill*: the no-guess generator fails to produce 100 levels per difficulty band. *Main risk*: novelty is modest.

**S15 Peloton.** *Player*: sports-strategy fans; strategy, competition. *Loop*: turn-based stage race → ride in the slipstream to save stamina → attack (push-your-luck) → four jersey classifications. *Hook*: four ways to win each week. *Gap hypothesis*: cycling games are niche. *Kill*: fewer than 1 in 3 testers understand drafting after the tutorial. *Main risk*: small market.

**S16 Frame Blast.** Fully worked in section 10.

**S17 Swiss Weekend.** A live-ops feature seed for an existing puzzle game. *Loop*: seven async rounds over a weekend; each round pairs players with the same record; nobody is eliminated. *Hook*: everyone plays all rounds. *Kill*: fewer than 40% of entrants finish all seven rounds. *Main risk*: matchmaking at low concurrency.

**S18 Bonsai Days.** *Player*: calm-game adults; design. *Loop*: prune a procedurally growing tree once a day → growth responds deterministically → share the tree. *Hook*: same seed, comparable trees. *Gap hypothesis*: deterministic shared-seed pruning is rare (verify). *Kill*: D7 below the viability screen; players cannot predict prune effects after five days. *Main risk*: too few decisions.

**S19 Relay Rush.** *Player*: runner players; competition, community. *Loop*: run → your distance becomes a teammate's starting boost → weekly team relays. *Hook*: you never run alone. *Gap hypothesis*: runner social layers are leaderboards, not relays (verify). *Kill*: relay participation below 25% of weekly active users. *Main risk*: consolidated genre, low novelty.

**S20 Grid Tycoon.** *Player*: idle players; strategy, power. *Loop*: buy fuel in a market your purchases move → power cities → expand → prestige into renewables with permanent multipliers. *Hook*: market timing as the idle skill. *Gap hypothesis*: idle tycoons rarely model prices that respond to the player. *Kill*: economy sims show one dominant buying rule. *Main risk*: engagement shallow if timing is trivial.

**S21 Mahjong Run.** *Player*: mahjong and card players; strategy, challenge. *Loop*: build mahjong hands → charms bend scoring → beat escalating targets. *Hook*: a familiar ruleset with rule-bending modifiers. *Gap hypothesis*: likely already explored by Balatro-likes; the market check may kill it. *Kill*: 3 or more well-rated equivalents found. *Main risk*: novelty, regional rule familiarity.

**S22 Pantry Pack.** *Player*: casual puzzle players; design, completion. *Loop*: pack groceries into fridge shelves → oldest items must stay reachable → freshness bonuses. *Hook*: freshness turns fitting into ordering. *Gap hypothesis*: packing and sort games are crowded (verify). *Kill*: 3 of 5 testers ignore the freshness rule. *Main risk*: crowded space.

**S23 Crop Rotation.** *Player*: farming players wanting more thinking; strategy, completion. *Loop*: plan plots → rotate crops to restore soil → companion plantings boost yields → fulfil orders. *Hook*: planting becomes a planning puzzle. *Gap hypothesis*: farming is consolidated; a planning layer could differentiate. *Kill*: telemetry shows players ignore rotation because orders dominate. *Main risk*: scope L art.

**S24 Kintsugi.** *Player*: calm-puzzle adults; design. *Loop*: reassemble broken pottery → gild the seams → the seams form the final artwork. *Hook*: the damage becomes the beauty. *Gap hypothesis*: jigsaw is crowded; the craft framing differentiates (verify). *Kill*: rotation input unreadable on phones. *Main risk*: premium-only economics.

**S25 Last Stop.** *Player*: strategy-puzzle adults; strategy, challenge. *Loop*: route lines for growing demand → each week ends with one of three perks → perks combine into a network style. *Hook*: roguelite variety in a network puzzle. *Gap hypothesis*: network puzzles are mostly premium and run-less (verify). *Kill*: bot shows the same optimal network regardless of perks. *Main risk*: run length on phones.

---

## 12. Batch protocol for agents

1. **Constraint sheet** (step 0) and preset chosen before any generation.
2. **Generate 30 raw ideas** with the grid (section 5): at least 4 chassis, at least 6 operators, at least 5 far sources.
3. **Diversity constraints**: no more than 3 concepts per chassis; at least 5 concepts using a far source; at least 3 concepts with a core-layer operator (OP03, OP06, OP12).
4. **Filter to 10** with hook tests (≥ 7 of 10) and the expectation-budget rule.
5. **Full cards for 10**, scored with evidence caps; AFS for the main borrowed relation of each.
6. **Market-gap check for the top 6** (step 5); re-score market and novelty.
7. **Shortlist 3–5** with `analogy_score.py rank --preset <preset>`; `arcosian:critic` must attack each score above 7.
8. **Tournament**: `/arcosian:concept-tournament`; human checkpoint on taste and fun before any contract is written.

**Agent prompt skeleton**

```
ROLE: arcosian:game-designer, concept generation.
CONSTRAINTS: <step 0 sheet>. PRESET: <preset>.
SEGMENT: <step 1 card>.
TASK: Fill a chassis x operator grid (>=4 chassis, >=6 operators). Produce 30 one-line ideas.
For the best 10: write concept cards per concept.schema.json with hook, comparables (borrow/change),
risks, kill_criteria; apply evidence caps; compute AFS for the main borrowed relation
(analogy_score.py fitness) and the weighted total (analogy_score.py concept --preset <preset>).
Flag every claim about competitors as "unverified" until market-scan runs.
OUTPUT: .gamestudio/concepts/<id>.concept.json files + a ranked table.
```

---

## 13. Anti-patterns

| Anti-pattern | Detection | Fix |
|---|---|---|
| Concept from a theme | The line is "match-3 with pirates" | Find a relation; or call it OP02 and score novelty ≤ 4 |
| Two cores | Two verbs in the first minute | One chassis; demote the other to meta or mode |
| Score inflation | Fun 9 with no prototype | Apply evidence caps; critic review |
| Market by vibes | Market score without step 5 | Cap market at 6 until scanned |
| Novelty without fun | Novelty 8, fun 4 | Gates catch it; prototype the toy first |
| Clone blindness | Hook exists in three live titles | Clone rule (step 5.4) |
| Ethics afterthought | Wager or paid random packs added for monetization score | Ethics gate first; `legal-ethics` |
| Ignoring capacity | XL scope scored as 6 for production cost | Use the scope mapping (S 8–10, M 6–7, L 3–5, XL 1–2) |
| One preset for every context | Agent-first weights used for a UA-led publisher | Choose the preset in step 0 and record it |
| Batch monoculture | Ten concepts on one chassis | Diversity constraints (section 12) |

---

## 14. Volatile facts (as of Oct 2026 — verify before relying)

Use these only as context for the market step; replace them with a fresh scan for each batch.

- Mobile game IAP in 2025 was about $82B (+1%), a flat market in which growth came from retaining and monetizing existing players. Source: [Sensor Tower State of Gaming 2026](https://sensortower.com/press/press-release-sensor-tower-state-of-gaming-gaming-drove-52-billion-downloads-82b-iap-revenue-on-mobile-and-12b-premium-revenue-on-steam).
- Hybrid-casual spending grew 17.1% in 2025 ($3.5B → $4.2B). In H1 2026, mobile game IAP was about $40B (−2% YoY) and downloads about 24B (−12%); Block Blast! topped downloads; Last War, Honor of Kings and Whiteout Survival led grossing in Q1 2026. Source: [Mobilegamer.biz (Sensor Tower data digest)](https://mobilegamer.biz/data-digest-sensor-towers-h1-analysis-hay-days-comeback-julys-top-games-big-krafton-numbers-and-more/).
- Feb–Apr 2026: casual and hyper-casual each took about 40% of game ad revenue, hybrid 16%, mid-core 4%. Jan–May 2026: ads were 70.3% of game revenue in India versus 22.1% in the US. Sources: [GameDev Reports](https://gamedevreports.substack.com/p/sensor-tower-mobile-game-ad-monetization), [Sensor Tower](https://sensortower.com/blog/gaming-deep-dive-ad-monetization-report).
- Retention viability screens used in kill criteria (practitioner heuristic): about 25–30% D1, 10–15% D7, 3–6% D30. Sources: [Playio](https://blog.playio.co/d1-d7-d30-retention-benchmarks-2026), [Galaxy4Games](https://galaxy4games.com/en/knowledgebase/blog/mobile-game-retention-benchmarks-2026-d1-d7-d30-data-for-publishers).
- Agents and VLM testers do best in turn-based, puzzle and UI-heavy games; fast timing-critical play is a known weak spot, which is why the agent_first preset favours deterministic chassis. Sources: [modl.ai](https://modl.ai), [arXiv:2505.18134](https://arxiv.org/html/2505.18134v3).
