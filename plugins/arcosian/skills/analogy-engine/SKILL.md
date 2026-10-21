---
name: analogy-engine
description: 'Analogy and transformation codex for game concepts: structure mapping and conceptual blending, a scored design-by-analogy procedure, 39 transformation operators (SCAMPER, transplant, constraint inversion, fusion, idle-ification...), 50 game lineages, 100+ cross-domain sources and a concept generator scored with concept.schema.json. Use when asked "X meets Y", "give me game ideas", "twist this genre", "why did X work" or "borrow this mechanic".'
when_to_use: 'Concept ideation, testing an "X meets Y" pitch, moving a mechanic between games, lineage studies, or filling analogy, hook and comparables in concept and contract files.'
---

# Analogy Engine

Most hit games are made by transforming earlier ones. This skill turns that habit into a method. It covers how to pick a source, how to abstract it into the studio ontology, how to map its *relations* (not its looks) onto a target, how to measure whether the mapping holds, and how to turn the result into a hook, an "X meets Y" line and a scored concept card. It holds the theory (Gentner's structure mapping, Fauconnier and Turner's conceptual blending, Boden, TRIZ), a grammar of 39 transformation operators, 50 documented game lineages with interpretations kept separate from facts, a catalogue of non-video-game sources, and a concept generator that feeds the `concept-tournament` workflow.

## What this skill gives you

- **A design-by-analogy procedure** with a mapping table and the **Analogy Fitness Score (AFS)**, a house heuristic that measures relational coverage, higher-order coverage, support fit, constraint violations and surface leakage. It returns GO, ADAPT or DROP (`references/analogy-method.md`, `scripts/analogy_score.py fitness`).
- **39 transformation operators**: SCAMPER adapted for games plus OP01–OP32 (mechanic transplant, theme swap, constraint inversion, perspective flip, scale and time shift, fusion, subtraction, audience and platform shifts, social layer, verb swap, economy re-skin, meta graft, roguelite- and idle-ification, stakes, information, ritual, automation, merge, puzzle-ification and more). Each comes with a procedure, examples, risks and the contract fields it touches (`references/transformation-operators.md`).
- **50 lineages**: what was preserved, what changed, why it worked or failed (labelled interpretation), the operators used and a transferable rule. Examples include Candy Crush, Royal Match, Block Blast!, Monopoly Go!, Balatro, Vampire Survivors, Clash Royale, Marvel Snap, Pokémon GO and Among Us, plus failures such as Artifact and the location-AR IP swaps (`references/worked-analogies.md`).
- **Cross-domain sources**: 50 board-game mechanisms, plus sports formats, toys, real-world systems, rituals and crafts. Each is reduced to a core relation and comes with a mobile transplant idea and a relation → source reverse index (`references/cross-domain-sources.md`).
- **A concept generator**: player and motivation → chassis → operators → hook → market-gap check → scores with anchors, evidence caps, weight presets and gates. It includes a worked card and 25 seeds (`references/concept-generation-playbook.md`, `scripts/analogy_score.py concept|rank`).

## Core models

### 1. Chassis + twist is the commercial default
Keep a proven core loop (the chassis) and change one or two relations (the twist). The chassis buys learnability and evidence. The twist buys differentiation and the 3-second ad. Name both explicitly in `comparables[].borrow` and `comparables[].change`. A concept with no chassis is a research project. A concept with no twist is a clone.

### 2. Map relations, not looks (structure mapping)
Following Gentner (1983), a sound analogy shares **relations** (who does what to whom, what causes what) rather than **attributes** (colour, theme, character type). Write every borrowed element as a predicate: `CAUSES(level_win, visible_meta_progress)`, not "renovation". Prefer mappings with connected **higher-order relations** (cause, enable, prevent), because those carry the experience. A feature borrowed without the structure that supports it is a cargo cult.

### 3. The hook is the blend's emergent structure (conceptual blending)
Following Fauconnier and Turner (2002), combining two inputs yields a blend with structure that neither input has. State the hook as something **true in the blend and false in both inputs**. Monopoly Go! is the classic case: where your dice land decides whom you raid. If no such sentence exists, you have a collage of two games, not a design.

### 4. Climb, cross, descend
Feature → rule → relation system → player need. Never cross between games at the feature level. Cross at the relation level for near genres and at the need level for far domains. Then descend in the target's own vocabulary and constraints (`references/analogy-method.md` section 6).

### 5. Systematicity is measurable
```
AFS = clamp(0, 100, 100 × (0.35·RC + 0.35·HC + 0.30·SF) − 15·V − 20·L)
GO ≥ 70 · ADAPT 50–69 · DROP < 50 or any hard (ethics/legal/policy) violation
```
RC is relational coverage, HC is higher-order coverage, SF is support fit, V counts constraint violations and L is surface leakage. Use it to expose missing structure, not as a substitute for a prototype.

### 6. Compare two sources before you borrow
Memory retrieves analogies by surface similarity, but soundness depends on structure (Gentner, Rattermann and Forbus, 1993). Comparing two cases side by side yields a better transferable schema (Gentner, Loewenstein and Thompson, 2003). So query sources **by relation**, abstract at least two that share it, and borrow the shared part.

### 7. Near sources for the chassis, far sources for the hook
Near sources (same or adjacent genres) carry evidence and learnability. Far sources (board games, sports, crafts, real systems) carry novelty. Engineering-design studies report that far examples raise novelty at some cost in feasibility. Use far sources for one layer only, usually the hook or the meta.

### 8. Operators are a grammar; use at most two
Every concept can be written as `chassis ⊕ OPxx [⊕ OPyy]`. Apply core-layer operators (inversion, time shift, verb swap) before meta-layer ones (meta graft, collection). Break **one** genre expectation, not three (`genre-playbooks` Core model 2). Boden's distinction helps when choosing: combinational operators are low risk, exploratory ones refine a known space, and transformational ones (constraint inversion, perspective flip) can create genres but fail more often.

### 9. The pitch line is a test, not a slogan
"X meets Y" puts the chassis first and the hook source second. Both must be known to the **segment**, not just the team, and there is never a third input. Test the line for recognition, prediction (can players guess the first minute?), emergence, expectation budget, 3-second ad readability, unpacking from a screenshot, and market existence.

### 10. Purpose and context decide transfer
A structurally sound mapping can still fail if it does not serve the IP's or the player's purpose. Pokémon's core relation is collecting creatures found in places, which is exactly location play. The Harry Potter and Minecraft location games swapped the IP without that fit, and both closed. Also apply the context filter from `game-case-studies` (era, channel, audience, platform, studio capability).

### 11. Copy moves, never expression or dark patterns
Mechanics and structures are the material of analogy. Art, trade dress, names and level layouts are not (`legal-ethics`). A pressure mechanic does not become acceptable because a top-grosser uses it. Run the ethics gate after economy re-skins, stakes and collection grafts.

### Rules of thumb

| Topic | Rule | Where |
|---|---|---|
| Operators per concept | ≤ 2, on different layers | `transformation-operators.md` §9 |
| Broken expectations | Exactly 1 | `analogy-method.md` §11 |
| Inputs in a pitch line | 2 (chassis first) | `analogy-method.md` §11.1 |
| Sources compared before borrowing | ≥ 2 sharing the relation | `analogy-method.md` §3 |
| AFS to prototype | ≥ 70, no hard violation | `analogy-method.md` §9 |
| Adapt cycles before dropping | ≤ 2 | `analogy-method.md` §8 |
| Hook test score | ≥ 7 of 10 | `concept-generation-playbook.md` §6.2 |
| Fun score with no prototype | ≤ 7 | `concept-generation-playbook.md` §8.2 |
| Market score without a scan | ≤ 6 | `concept-generation-playbook.md` §8.2 |
| Clone rule | ≥ 3 live, well-rated, recently updated titles with the same blend → not a gap | `concept-generation-playbook.md` §7 |
| Meta power bridge | Shifts bot win rate by ≤ 10–15 points | `genre-playbooks` procedure C |
| Raw ideas per batch | 30 → 10 cards → 3–5 shortlisted | `concept-generation-playbook.md` §12 |

## Decision procedures

### A. Design-by-analogy (any borrowing or "Y but Z" idea)
1. **Frame** the target problem as a player-experience gap; name the segment and its top two motivations.
2. **Retrieve by relation**: 3 near, 3 mid, 2 far sources (`gs.py kb "<relation words>"`; `references/cross-domain-sources.md` §8).
3. **Abstract** the best 2–3 with the ontology template (verbs, mechanics, dynamics, aesthetics, loops, flows, relations, supporting structure, known weaknesses).
4. **Identify structure**: mark the essential first-order and higher-order relations and the support they need.
5. **Map** one-to-one in a mapping table; flag `surface_only` rows.
6. **Evaluate** with the AFS: `python3 ${CLAUDE_PLUGIN_ROOT}/skills/analogy-engine/scripts/analogy_score.py fitness --mapping <file>.json`.
7. **Adapt** missing relations or support (up to two cycles), or drop.
8. **State the blend**: write the emergent sentence and the "X meets Y" line.
9. **Test cheaply**: turn the prediction into a metric with pass and kill thresholds (bot sim, greybox, persona pass, creative test, A/B).

### B. Generate a concept batch
1. Step 0 constraint sheet and scoring preset (`default`, `agent_first`, `ua_led`, `premium_indie`).
2. Segment card with two motivations (Quantic Foundry model).
3. Pick 4–6 chassis from the library (K01–K24).
4. Fill a chassis × operator grid (≥ 6 operators, ≥ 5 far sources) with 30 one-liners.
5. Filter with hook tests and the expectation budget to 10; write full cards.
6. Run the market-gap check on the top 6 (`/arcosian:market-scan` or `arcosian:market-analyst`); re-score.
7. Rank with `analogy_score.py rank --dir .gamestudio/concepts --preset <preset>`. The critic attacks every score above 7. Hand off to `/arcosian:concept-tournament`. A human checks taste and fun before any contract is written.

### C. Test an "X meets Y" line

| # | Test | Pass (house default) |
|---|---|---|
| 1 | Recognition by 5 segment players | ≥ 4/5 know X, ≥ 3/5 know Y |
| 2 | Prediction of the first minute | ≥ 3/5 describe the core verb |
| 3 | Emergent sentence | Exists and is not a theme |
| 4 | Expectation budget | Exactly one break |
| 5 | 3-second muted creative | 2 of 3 storyboards show the hook without text |
| 6 | Unpacking from a greybox screenshot | Players name X |
| 7 | Market existence | < 3 equivalent live titles, or a named edge |

### D. Pick operators by goal (short form; full matrix in `references/transformation-operators.md` §8)

| Goal | Start with | Avoid |
|---|---|---|
| Novelty in a consolidated genre | OP03 inversion, OP04 perspective, OP12 verb swap | OP02 theme swap alone |
| Retention | OP14 meta graft, OP29 collection, OP11 social, OP23 ritual | OP17 compression without a meta |
| Lower production cost | OP28 generator, OP08 subtraction, OP23 ritual | OP30 narrative wrap |
| Agent buildability | OP06 → turn-based, OP20 determinism, OP32 puzzle-ification | Real-time multiplayer operators |
| Port a PC or console hit | OP10 platform + OP17 session + OP14 meta | Keeping landscape twin-stick by habit |
| New audience | OP09 audience, OP24 real-world, OP02 theme | Midcore meta on a casual core |

### E. Five-minute vet of a proposed borrowing (in a review)
1. Say the borrowed thing as a relation. If it can only be said as a feature name, stop and climb the ladder.
2. Name the higher-order relation it serves. What does it cause or prevent for the player?
3. Check support. Does our game have the structure the relation needs (discrete attempts, a sink, hidden information, a stake)?
4. Check constraints: session length, one thumb, low-end devices, monetization moment, minors and ethics.
5. Verdict: GO (prototype it), ADAPT (name the missing support) or DROP. Record it in `gs.py progress`.

### F. Lineage study of a hit (for decks, deconstructions and calibration)
Find stated inspirations (grade A), then widely reported comparisons (grade B). Abstract both sides, diff the relations (preserved, added, removed, inverted) and name the operators. Apply the context filter, write the "why" as interpretation, find one counterexample, and state the rule. Template: `references/worked-analogies.md` §10.

### G. Transform, refine or invent?

| Situation | Move | Precedent |
|---|---|---|
| Consolidated genre, strong execution and UA budget | Refine the chassis: subtract friction (OP08, OP30 unwrap) | Royal Match (W05) |
| Consolidated genre, small budget | Transform: a core-layer operator plus a niche audience | Vampire Survivors (W23) |
| PC or indie rule with no mobile incumbent | Fast-follow with OP10 + OP14 | Survivor.io (W24), Stumble Guys (W38) |
| Commodity mechanic, ads-led | Win on tuning, feedback and distribution | Block Blast! (W07) |
| A familiar ruleset with untapped depth | OP01 + OP15 on the familiar rules | Balatro (W26) |
| Strong IP available | Map the IP's core relation to a structure that expresses it | Pokémon GO (W41), Monopoly Go! (W14) |

## Mobile specifics

- **Translate the verb, not just the screen.** Most PC-to-mobile analogies succeed by turning the input into a touch-native gesture whose physical metaphor *is* the action: slingshot drag, path drawing, stop-to-shoot. Run the OP10 checklist for orientation, input, session, interruptions, device tier, business model, readability and text.
- **Session shape is part of the analogy.** Borrow the source's session shape or deliberately compress it (OP17). Mobile defaults are 1–3 minute puzzle levels, 2–4 minute PvP matches and 5–15 minute runs, with natural stops every few minutes.
- **The hook must survive a muted 3-second clip.** Store pages and ads are where the analogy is first read, so a hook that needs text is a weak hook on phones.
- **Low-end devices bound scale operators.** Magnified entity counts (OP05) and real-time operators need per-tier caps (`mobile-performance`).
- **Monetization moments travel with the borrowed loop.** Copying a loop copies its spend moment (near-miss continue, energy, stakes). Decide whether you want that moment, and guard it (`monetization`, `legal-ethics`).
- **One-thumb portrait is the default.** Choose landscape only when the control scheme demands it, and test orientation early (Brawl Stars changed during soft launch, W30).
- **Interruptions are normal.** Borrowed real-time structures need pause on focus loss and resume in one tap. Async conversions (OP06) often fit phones better than the original synchronous form (Words With Friends, W43).

## Anti-patterns

| Anti-pattern | How to detect | Fix |
|---|---|---|
| Surface analogy | Mapping rows are themes, art or character types | Rewrite as predicates; compute L; drop attribute rows |
| Cargo-cult feature | The borrowed feature is named by its source brand ("our Butler's Gift") | Climb to rule and relation; check support |
| Collage | Two verbs in the first minute; no emergent sentence | One chassis; demote the other input to meta or mode |
| Three-input pitch | "X meets Y meets Z" | Cut to two; the third becomes a detail |
| Obscure reference | The team loves Y; the segment never heard of it | Recognition test; use Y as a design tool, not in the line |
| IP without fit | The IP's core relation differs from the loop's | Write the IP's core relation first (W41 vs W42) |
| Fixation on the source | The concept copies the source's flaws | List source weaknesses before mapping; generate before browsing |
| Operator pile-up | Three or more operators; several broken expectations | Two operators maximum on different layers |
| Score inflation | Fun 9 with no prototype; market 8 with no scan | Evidence caps; critic review |
| Clone blindness | The same blend exists in three live titles | Clone rule in the market-gap step |
| Dark-pattern import | A borrowed relation is a pressure mechanic | Ethics gate; hard violation → DROP |
| Era transfer | A 2012 viral loop copied into a paid-UA market unchanged | Context filter; re-run the economics |

## Using the ontology

| Analogy concept | Where it lives | Notes |
|---|---|---|
| "X meets Y" line | `concept.analogy`, `contract.meta.analogy` | Chassis first |
| Borrowed and changed relations | `concept.comparables[]`, `contract.meta.comparables[]` (`title`, `borrow`, `change`) | Write `borrow` and `change` at relation level; far sources count as comparables (e.g. "Can't Stop (board game)") |
| Hook (emergent structure) | `concept.hook` | Must pass the hook tests |
| Chassis loop | `concept.core_loop` (string or loop graph), `contract.loops[]` | One sentence: act → reward → invest |
| Operators used | Optional top-level `operators` in the concept card (extra keys are allowed) or `rationale` | Codes OP01–OP32, SCAMPER letters |
| AFS of the main borrowing | Optional top-level `analogy_fitness` or `rationale` | Keep the mapping JSON next to the card |
| Scores | `concept.scores` (seven criteria, 1–10, higher is better), `weighted_total` | Anchors and presets in the playbook |
| Kill criteria | `concept.kill_criteria`, `contract.kill_criteria` | Behavioural and time-boxed |
| Transplanted mechanic | `mechanic-card.schema.json` (`references` = source titles, `combos`) | One card per transplanted mechanic (`mechanics-codex`) |
| Lineage findings for a competitor | `deconstruction.schema.json` (`innovations`, `lessons`, `borrow_for_us`) | Use the lineage-study method |
| Economy borrowed by re-skin | `economy-model.schema.json` nodes | Simulate before accepting |

**Tools**

| Task | Command |
|---|---|
| AFS from numbers | `python3 ${CLAUDE_PLUGIN_ROOT}/skills/analogy-engine/scripts/analogy_score.py fitness --rc 1 --hc 0.67 --sf 0.75` |
| AFS from a mapping file | `analogy_score.py fitness --mapping .gamestudio/concepts/<id>.mapping.json --json` |
| Score a concept card | `analogy_score.py concept --card .gamestudio/concepts/<id>.concept.json --preset agent_first --evidence none --write` |
| Rank a batch | `analogy_score.py rank --dir .gamestudio/concepts --preset agent_first` |
| Validate a card | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py validate .gamestudio/concepts/<id>.concept.json` |
| Search precedents by relation | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py kb "streak bonus resets on loss" --limit 10` |
| Simulate a re-skinned economy | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/economy_sim.py --model .gamestudio/economy/model.json --runs 200 --seed 1` |
| Check an EV-based stake rule | `python3 ${CLAUDE_PLUGIN_ROOT}/skills/design-theory/scripts/decision_math.py ev --outcomes "0.55:2,0.45:-2"` |
| Size an A/B test for a borrowed feature | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ab_test.py size --baseline 0.30 --mde 0.05` |

`analogy_score.py` uses only the standard library (Python 3.9+), supports `--json` and passes `--selftest`. It exits 1 on a DROP verdict or a gate failure and 2 on input errors.

**Agents and workflows.** `arcosian:game-designer` runs procedures A and B. `arcosian:market-analyst` runs the market-gap step. `arcosian:critic` attacks scores and claims. `arcosian:principal` owns the final pick below the human taste checkpoint. Batches go through the `concept-lab` process skill and the `/arcosian:concept-tournament` workflow, and the winner seeds `new-game`.

## Reference library

| File | What it contains | Read it when |
|---|---|---|
| `references/analogy-method.md` | Structure mapping, retrieval and encoding research, design fixation, conceptual blending, Boden and TRIZ, the abstraction ladder, the ontology abstraction template, the 9-step procedure, the AFS, surface vs deep diagnostics, the "X meets Y" formula and seven tests, two worked examples, failure modes, checklists, the mapping JSON format | Before any borrowing, pitch line or analogy review; when computing AFS |
| `references/transformation-operators.md` | SCAMPER for games and OP01–OP32 with procedure, examples, risks and ontology delta; selection matrix by goal; stacking rules; worksheet | Generating variants, choosing how to transform a source, reviewing what a concept changed |
| `references/worked-analogies.md` | 50 lineages (preserved, changed, why, operators, rule), cross-lineage patterns, failure lessons, lineage-study method, volatile facts | Looking for precedent, calibrating AFS judgements, preparing pitch or deconstruction material |
| `references/cross-domain-sources.md` | 50 board-game mechanisms in seven families, sports formats, toys, real-world systems (gardening, cooking, logistics, ecosystems and more), rituals, crafts, a relation → source reverse index, the far-analogy retrieval procedure | Hunting for a hook or meta outside video games; when near sources only yield clones |
| `references/concept-generation-playbook.md` | Constraints, segment cards, motivation → chassis map, a 24-chassis library, the generation grid, hook types and tests, the market-gap check, scoring anchors, evidence caps, weight presets, gates, card template, worked example, 25 seeds, batch protocol, volatile facts | Running ideation, scoring concepts, preparing a concept tournament |
| `scripts/analogy_score.py` | AFS (`fitness`), concept weighted totals with presets, gates and evidence caps (`concept`), batch ranking (`rank`) | Whenever a mapping or a concept needs a number |

## Related skills

- `game-case-studies`: deep deconstructions of the games behind the lineages; precedent search and the clone-or-innovate table.
- `genre-playbooks`: chassis loops, agent-buildability and scope scores, genre selection and fusion rules.
- `mechanics-codex`: mechanic cards to instantiate transplanted mechanics.
- `design-theory`: MDA, loops, decision quality and prototype discipline for testing analogies.
- `design-philosophies`: studio doctrines that decide which transformations fit the house style.
- `game-ontology`: the formal vocabulary and schemas the abstraction template uses.
- `player-psychology`: motivation models behind segment cards and hook appeal.
- `market-intel`: saturation evidence and sources for the market-gap check.
- `marketing-ua`: creative tests for the 3-second hook and the pitch line.
- `economy-design`: simulation of re-skinned economies and bridge currencies.
- `monetization`: spend moments that travel with borrowed loops, kept ethical.
- `legal-ethics`: loot-box, wager and minors rules; the expression-versus-mechanics line on copying.
- `production`: scope and capacity that set the production_cost score.
