# Analogy Method: From Source Game to Target Design

This file is the theory and the procedure behind every "X meets Y" in the studio. It summarises the cognitive science that explains why some analogies produce great games and others produce shallow clones: Gentner's structure-mapping theory, Fauconnier and Turner's conceptual blending, analogical retrieval and encoding research, design fixation, and Boden's types of creativity. It then turns them into a design-by-analogy procedure that works on the studio ontology (verbs, mechanics, loops, flows, aesthetics). The procedure ends in a scored mapping table, the Analogy Fitness Score (AFS), and a tested pitch line. All frameworks are summarised in our own words with attribution. The AFS and the pitch tests are house heuristics, not published instruments.

## Contents

1. Why analogy is the main generator of commercial game design
2. Structure-mapping theory (Gentner) and what it means for designers
3. Retrieval, encoding and fixation: the research that shapes the procedure
4. Conceptual blending (Fauconnier and Turner): where the hook comes from
5. Boden's three kinds of creativity, and TRIZ as analogy at the principle level
6. The abstraction ladder: feature → rule → relation → need
7. Abstracting a source into the ontology (template)
8. The design-by-analogy procedure (9 steps)
9. Evaluating systematicity: the Analogy Fitness Score
10. Surface versus deep analogies (diagnostic table)
11. The "X meets Y" pitch formula and seven tests
12. Worked example A: Marvel Snap's stakes → an async word duel
13. Worked example B: a real-world system → a puzzle meta (short)
14. Failure modes and red flags
15. Checklists and agent templates

---

## 1. Why analogy is the main generator of commercial game design

Most successful mobile games keep a proven **chassis** and change one or two things (see `game-case-studies`, Core model 1, and `references/worked-analogies.md`). That is analogy at work: the designer maps a known structure (a loop, an economy, a social contract) onto a new context and predicts that the experience will transfer.

Analogy wins in this market for four reasons:

| Reason | Mechanism | Consequence for us |
|---|---|---|
| Players arrive with schemas | A familiar chassis cuts learning cost; time-to-fun drops | Choose X so that the target segment already knows it |
| Ads must read in 3 seconds | A recognisable verb plus one visible twist is legible in a muted clip | The hook must be *visible*, not explained |
| Risk is concentrated | Borrowed structures carry evidence of retention and monetization | Borrow the parts with evidence; invent where the evidence is weak |
| Production is finite | Reusing a loop frees budget for the twist and the polish | Spend novelty budget on one place only |

The danger is the mirror image: borrowing the **look** of a hit without the **relations** that made it work. The rest of this file is a defence against that.

---

## 2. Structure-mapping theory (Gentner) and what it means for designers

Dedre Gentner's structure-mapping theory (Gentner, "Structure-mapping: A theoretical framework for analogy", *Cognitive Science*, 1983; later computational form in the Structure-Mapping Engine, Falkenhainer, Forbus and Gentner, 1989) describes analogy as an alignment between a **base** (source) and a **target**.

### 2.1 The vocabulary

| Term | Meaning | Game example |
|---|---|---|
| Object | An entity in a domain | a tile, a hero, a player, a currency |
| Attribute | A one-place property of an object | "red", "cute", "candy-shaped", "medieval" |
| First-order relation | A relation between objects | `MATCHES(tile_a, tile_b)`, `COSTS(booster, coins)`, `BLOCKS(wall, path)` |
| Higher-order relation | A relation between relations | `CAUSES(MATCHES(..), CLEARS(..))`, `ENABLES(hidden_hand, bluff)`, `PREVENTS(shield, raid)` |
| Mapping | A set of correspondences between base and target elements | level win → run win; star → renovation material |
| Candidate inference | Base structure carried into the target where nothing yet exists | "Royal Match has a win-streak bonus, so our roguelite should have one too" |

### 2.2 The principles that matter

1. **Relational focus.** Analogy maps relations, not attributes. Shared attributes are irrelevant (or misleading) to whether an analogy is sound.
2. **Structural consistency.** Mappings are one-to-one (one base element maps to one target element) and have *parallel connectivity*: if two relations correspond, their arguments must correspond too.
3. **Systematicity.** People prefer mappings that preserve a connected system of relations, especially ones governed by higher-order relations such as cause, enable and prevent. Isolated facts are rarely carried over. A mappable *system* is what makes a candidate inference credible.

### 2.3 Four kinds of comparison (Gentner's taxonomy, paraphrased)

| Comparison | Attributes shared | Relations shared | Game-design reading |
|---|---|---|---|
| Literal similarity | many | many | A clone or a sequel. Low risk, low differentiation |
| Analogy | few | many | The productive zone: a different-looking game with the same working structure |
| Mere appearance | many | few | The trap: "it's like Pokémon because it has creatures" |
| Abstraction | none (abstract objects) | many | A design pattern or schema: "act → reward → invest" |

### 2.4 What this means in practice

- Write every borrowed element as a **relation** (a verb with arguments), never as a noun.
- Find the **higher-order relations** in the source, because they carry the experience: "a loss *causes* the streak to reset, which *causes* each attempt to feel weightier".
- A borrowed feature with no supporting structure in the target is a *candidate inference without a system*. Drop it or build the system first.

---

## 3. Retrieval, encoding and fixation: the research that shapes the procedure

| Finding | Source (summarised) | Procedure rule it produces |
|---|---|---|
| Retrieval is driven by surface similarity; judgements of soundness are driven by structure | Gentner, Rattermann and Forbus, "The roles of similarity in transfer", *Cognitive Psychology*, 1993 | Do not trust what comes to mind first. Query sources by **relation** ("games where a loss resets a growing bonus") instead of by theme |
| People rarely apply a known analogy spontaneously; a hint that the cases are related makes transfer far more likely | Gick and Holyoak, analogical problem solving studies, 1980 and 1983 | Retrieval must be an explicit step with a checklist, not left to inspiration |
| Comparing two cases side by side produces a better abstract schema and better transfer than studying one | Gentner, Loewenstein and Thompson, "Learning and transfer: A general role for analogical encoding", 2003 | Always abstract from **two or more** source games that share the relation; the shared part is the transferable schema |
| Analogical reasoning is shaped by similarity, structure and purpose together | Holyoak and Thagard, *Mental Leaps*, 1995 (multiconstraint theory) | Score the mapping on structure **and** on purpose: does it serve our player fantasy? |
| Showing designers an example makes them reproduce its features, including its flaws | Jansson and Smith, "Design fixation", *Design Studies*, 1991 | Generate first, look at references second; and list the source's known weaknesses before mapping |
| Far-field and less common examples tend to raise the novelty of ideas, at some cost in feasibility | Reported in engineering-design studies, e.g. Chan and colleagues, *Journal of Mechanical Design*, 2011 | Use near sources for the chassis and far sources for the hook |

---

## 4. Conceptual blending (Fauconnier and Turner): where the hook comes from

Gilles Fauconnier and Mark Turner (*The Way We Think: Conceptual Blending and the Mind's Hidden Complexities*, 2002) describe how people combine mental spaces into a new one. Structure mapping explains *transfer*; blending explains *emergence*, which is what a hook is.

### 4.1 The four-space network

| Space | Content | Game reading |
|---|---|---|
| Input 1 | One source frame | Coin Master's loop: energy-gated spins, raids, village building |
| Input 2 | Another source frame | Monopoly: dice, a looping board, properties, landing events |
| Generic space | The abstract structure both inputs share | "a chance device moves the player through outcomes that pay resources or trigger interactions" |
| Blend | Selectively projected elements of both, plus **emergent structure** found in neither input | Monopoly Go!: dice rolls as the energy unit, board tiles as outcome table, landmarks as the build sink, railroads as raid triggers |

### 4.2 How emergent structure arises (their three operations, paraphrased)

1. **Composition**: putting elements from both inputs together creates relations neither had (dice + raid: *where you land* decides whom you attack).
2. **Completion**: familiar background frames fill in the blend automatically (players already know how a Monopoly board loops, so they need no tutorial for movement).
3. **Elaboration ("running the blend")**: simulating the blend reveals new behaviours (multipliers on dice rolls appear naturally as a "bet size" on the board).

### 4.3 Their governing principles as design checks

Fauconnier and Turner list optimality principles for good blends. Five translate directly into design checks:

| Principle (paraphrased) | Design check |
|---|---|
| Integration: the blend should feel like one coherent scene | Can the core loop be described as one activity, not two modes glued together? |
| Topology: keep the inner relations of inputs where possible | Do borrowed elements keep their original relations (dice still mean chance, a board still loops)? |
| Unpacking: one should be able to reconstruct the inputs from the blend | Can a player name both inputs from a screenshot or ad? If yes, the pitch line will work |
| Web: links back to the inputs stay live | Does knowledge of input games still help players in the blend (transfer of skill and expectations)? |
| Good reason: every element has a meaning in the blend | Does each borrowed element do a job? Remove decoration that only signals the source |

### 4.4 Design rule
The hook of a concept should be stated as the **emergent structure** of the blend: something that is true in the blend and false in both inputs. If you cannot name it, you have a collage, not a blend.

---

## 5. Boden's three kinds of creativity, and TRIZ as analogy at the principle level

Margaret Boden (*The Creative Mind*, 1990) distinguishes three ways to be creative. They map onto the operator families in `references/transformation-operators.md`:

| Boden type | Meaning | Operator families | Risk profile |
|---|---|---|---|
| Combinational | Unfamiliar combinations of familiar ideas | Genre fusion, mechanic transplant, meta-layer graft, collection graft | Low–medium; fails when the combination is a collage |
| Exploratory | Exploring the possibilities of an existing conceptual space | Scale shift, session compression, theme swap, parameter extremes | Low; differentiation may be thin |
| Transformational | Changing a rule of the space so that new ideas become possible | Constraint inversion, perspective flip, time shift, automation shift | High; when it works it creates genres (Vampire Survivors removing aiming) |

**TRIZ** (Genrich Altshuller's theory of inventive problem solving) is analogy at the level of solution principles. Altshuller abstracted patents into 40 inventive principles that recur across industries. Several translate into game operators: *inversion* ("do it the other way round") → perspective flip; *segmentation* → session compression and modes; *prior action* → planning phases; *dynamics* → adaptive difficulty; *nested doll* → meta loops inside loops; *periodic action* → daily rituals; *self-service* → automation and idle. The lesson is methodological: abstract from many concrete cases to a principle, then descend into your own domain.

---

## 6. The abstraction ladder: feature → rule → relation → need

The single most useful habit. Never transplant a feature; climb, cross, and descend.

```
Level 4  NEED / AESTHETIC   competence, loss aversion smoothing, anticipation      ← cross domains here
Level 3  RELATION SYSTEM    CAUSES(win, bonus_grows); CAUSES(loss, bonus_resets)   ← map here
Level 2  RULE               "start bonus grows with consecutive wins, resets on loss"
Level 1  FEATURE            "Butler's Gift" (Royal Match)                           ← never copy at this level
```

Procedure: climb from feature to rule (state the rule without names), from rule to relation system (write predicates and the higher-order links), from relations to the need (MDA aesthetic or motivation served). Cross into the target at level 3 or 4. Descend in the target's own vocabulary and constraints. The level at which you cross decides the kind of result:

| Crossing level | Typical result | Example |
|---|---|---|
| Feature (1) | Clone or cargo cult | A match-3 "butler" mascot added to a shooter |
| Rule (2) | Competent transplant inside a near genre | Win-streak boosters across match-3 titles |
| Relation (3) | Fresh but readable design in a different genre | Streak → starting relic in a roguelite |
| Need (4) | Transformational ideas from far domains | "Anticipation of a growing reward" → sourdough starter that rises while you are away |

---

## 7. Abstracting a source into the ontology (template)

Abstract every source game into the same structure before mapping. Field names follow the contract and the schemas (`game-ontology`).

```yaml
source: "<game title> (<developer>, <year>)"
evidence: [deconstruction path or URLs, with grade A–D per game-case-studies]
player_fantasy: "I get to ..."
verbs:            # contract.verbs[]
  - {id: swap, input: "swipe between adjacent tiles", description: "exchange two tiles"}
mechanics:        # contract.mechanics[] (rules + parameters)
  - {id: match3, rules: ["3+ in line clear"], parameters: [{key: moves, value: 25}]}
dynamics:         # emergent behaviours (mechanic-card.dynamics)
  - "cascades create unplanned chains"
aesthetics:       # MDA targets (LeBlanc vocabulary)
  - challenge
  - sensation
loops:            # contract.loops[] with period
  core: "play level -> win star -> spend star on renovation task -> next level"   # minutes
  meta: "area completion -> new area reveal"                                      # days
flows:            # economy-model nodes: source | sink | converter | gate | pool
  - {node: level_win, kind: source, outputs: {stars: 1, coins: 50}}
  - {node: renovation_task, kind: sink, inputs: {stars: 2}}
  - {node: lives, kind: gate}
session: {length_sec: 180, stop_points: "level end"}
monetization_moment: "near-miss continue (+moves)"
social: "teams, lives gifting"
relations:        # the part you will map
  first_order:
    - R1: "COSTS(renovation_task, stars)"
    - R2: "GRANTS(level_win, star)"
  higher_order:
    - H1: "CAUSES(level_win, visible_progress_in_meta)"
    - H2: "ENABLES(meta_progress, play_without_skill_dependence)"
supporting_structure:   # what the target must have for the relations to hold
  - "discrete attempts with win/lose outcome"
  - "a sink that turns a core output into visible, permanent change"
known_weaknesses: ["meta becomes a chore when star prices inflate"]
```

The `relations` and `supporting_structure` blocks are the inputs to the AFS (section 9) and to `scripts/analogy_score.py fitness`.

---

## 8. The design-by-analogy procedure (9 steps)

Run this whenever someone proposes a borrowing ("let's add X's feature") or generates a concept from a source ("Y but Z").

| Step | Action | Output | Time box |
|---|---|---|---|
| 1. Frame | State the **target problem** as a player-experience gap: "our runs feel weightless after day 3" or "our puzzle has no reason to return tomorrow". Name the target segment and top motivations | Problem statement | 15 min |
| 2. Retrieve | Query sources by **relation**, not by theme. Use three channels: near (same genre), mid (adjacent genres), far (`references/cross-domain-sources.md`). Run `gs.py kb "<relation words>"` across `game-case-studies` and `mechanics-codex` | 6–10 candidate sources | 30 min |
| 3. Abstract | Fill the section 7 template for the 2–3 best sources. Compare them pairwise; keep the relations they **share** (analogical encoding) | Abstracted sources + shared schema | 45 min |
| 4. Identify structure | Mark the essential first-order relations and the higher-order relations (cause, enable, prevent, trade-off) that carry the target aesthetic. List supporting structure the relations need | Relation list with `essential` flags | 20 min |
| 5. Map | Build a role-mapping table: source element → target element, one-to-one, with parallel connectivity. Mark each row `mapped`, `partial` or `unmapped`, and `surface_only` where only an attribute is shared | Mapping table | 30 min |
| 6. Evaluate | Score systematicity and fit with the AFS (section 9). Check hard constraints: session, input, platform, ethics, economy | AFS + verdict (GO / ADAPT / DROP) | 15 min |
| 7. Adapt | For each partial or unmapped essential relation: build the missing support, substitute an equivalent relation, or drop the borrowing. Re-score | Adapted mapping, AFS ≥ 70 | 30–60 min |
| 8. State the blend | Write the emergent structure (hook) and the pitch line; run the section 11 tests | Hook + "X meets Y" line | 20 min |
| 9. Test cheaply | Turn the key prediction into a metric and the cheapest test: paper prototype, bot simulation, greybox, creative test, or A/B | Test plan with pass/kill thresholds | 20 min |

**Outputs to record**: the mapping in `concept.comparables[]` (`title`, `borrow`, `change`) or `contract.meta.comparables[]`; the line in `analogy`; the hook in `hook`; mechanic cards with `references` listing the source titles; a `gs.py progress` entry with the AFS and verdict.

### 8.1 Mapping table format

| # | Source element (relation) | Target element (relation) | Order | Essential | Status | Surface-only | Note |
|---|---|---|---|---|---|---|---|
| R1 | `GRANTS(level_win, star)` | `GRANTS(run_win, ember)` | 1 | yes | mapped | no | |
| H1 | `CAUSES(win, visible_meta_progress)` | `CAUSES(run_win, camp_upgrade_visible)` | 2 | yes | mapped | no | |
| A1 | "castle theme" | "camp theme" | attr | no | mapped | **yes** | decoration only; excluded from AFS coverage |

### 8.2 Role-mapping heuristics

- Map **roles**, not things: "the scarce input to the build sink" maps to whatever is scarce in your target, even if it looks nothing like the source.
- Every higher-order relation needs both of its arguments mapped. If `CAUSES(A, B)` is essential and B has no counterpart, the relation is unmapped.
- One-to-one: if two source elements collapse into one target element, at least one relation will break. Find it.
- If the best mapping needs a **new** target system (a currency, a mode), price it in production scope before accepting.

---

## 9. Evaluating systematicity: the Analogy Fitness Score

A house heuristic that turns sections 2–4 into a number a team can argue about. It is not a validated psychometric instrument; it is a structured way to expose missing structure.

### 9.1 Inputs

| Symbol | Definition | Range |
|---|---|---|
| RC | Relational coverage: mapped essential first-order relations ÷ essential first-order relations (partial counts 0.5) | 0–1 |
| HC | Higher-order coverage: mapped essential higher-order relations ÷ essential higher-order relations (partial 0.5) | 0–1 |
| SF | Support fit: target-side supporting structures present ÷ required | 0–1 |
| V | Count of constraint violations (session, input, platform, economy, audience). Any **ethics or legal** violation is a hard stop | integer |
| L | Surface leakage: surface-only mapped rows ÷ all mapped rows | 0–1 |

### 9.2 Formula and bands

```
AFS = clamp(0, 100, 100 × (0.35·RC + 0.35·HC + 0.30·SF) − 15·V − 20·L)

GO     AFS ≥ 70  and no hard violation   → prototype or simulate
ADAPT  50 ≤ AFS < 70                      → run step 7, re-score (max two adapt cycles)
DROP   AFS < 50  or any hard violation    → choose another source or another relation
```

Weights put structure first (RC + HC = 70%) and context fit second (SF = 30%), then penalise broken constraints and cosmetic borrowing. Compute it with:

```
python3 ${CLAUDE_PLUGIN_ROOT}/skills/analogy-engine/scripts/analogy_score.py fitness --rc 1 --hc 0.67 --sf 0.75 --violations 0 --leakage 0
python3 ${CLAUDE_PLUGIN_ROOT}/skills/analogy-engine/scripts/analogy_score.py fitness --mapping .gamestudio/concepts/snap-letters.mapping.json --json
```

### 9.3 Interpreting partial scores

| Pattern | Meaning | Move |
|---|---|---|
| High RC, low HC | The parts transfer but not the reason they matter | Rebuild the causal link (often a missing sink, stake or visible consequence) |
| High HC, low SF | The idea is sound but the target cannot host it (session too short, no discrete attempts) | Change the target structure or choose another target genre |
| High L | Theme carries the analogy | Strip theme words from the mapping and re-score |
| V ≥ 2 | The borrowing fights mobile constraints | Run the platform translation operator (OP10) first |

---

## 10. Surface versus deep analogies (diagnostic table)

| Claim heard in a meeting | Surface or deep? | Why | Deep restatement |
|---|---|---|---|
| "It's like Pokémon because it has cute creatures" | Surface | Attribute only | "Collection of distinct units whose acquisition is spread across contexts, with trading and type counters" |
| "Candy theme worked for King, so candy" | Surface | Theme is not the engine | "Bright, edible-looking pieces raise readability and appeal for a broad adult audience" (a DDE claim, test it) |
| "Royal Match is match-3 plus a castle" | Half-deep | Names both inputs, misses the bridge | "Each level win yields one material that is the only input to visible permanent change" (bridge currency) |
| "Vampire Survivors is a bullet hell" | Surface (and wrong) | Shares the screen density, inverts the relation | "Player emits the bullet field automatically; the only decision is position and the level-up draft" |
| "Monopoly Go! is Monopoly on phones" | Surface | The board game's trading and bankruptcy are absent | "Coin Master's energy → chance → raid/build loop, with dice and a board as the chance device and the IP as the audience bridge" |
| "Clash Royale is a card game" | Partial | Misses the spatial and real-time relations | "Deck-constrained real-time unit deployment against lane towers, gated by a regenerating resource" |
| "Wordle is a word game" | Partial | Misses the social and temporal structure | "One shared deterministic puzzle per day with a spoiler-free shareable result" |

Rule: if a sentence can be made true by changing only art, it is a surface claim.

---

## 11. The "X meets Y" pitch formula and seven tests

### 11.1 Forms of the line

| Form | When to use | Example shape |
|---|---|---|
| X meets Y | Two recognisable inputs; the blend is legible | "Coin Master meets Monopoly" |
| X, but Z | One chassis plus one rule change (constraint inversion) | "Bullet hell, but you never aim" |
| X where you are the Y | Perspective flip | "Tower defense where you are the attackers" |
| X for Y (audience) | Audience shift | "A tactics game for people who play Wordle" |
| X in a Y world | Theme swap with a structural reason | "Farming in a deep-sea research station" |
| X, every day | Ritualization | "A logic puzzle, the same for everyone, once a day" |

**Composition rules**
1. **X is the chassis** (the input that owns the core verb). **Y is the hook source.** Saying them in this order sets expectations correctly.
2. Both inputs must be known to the **target segment**, not to the team. Run the recognition test (11.2 test 1) with segment players.
3. No third input. "X meets Y meets Z" signals a collage and usually breaks the expectation budget.
4. Y must contribute a **relation**, not a look. "Match-3 meets pirates" is a theme swap; say it as "match-3 in a pirate world" or find the relation.
5. The line must imply the hook. If the hook needs another sentence, the line is wrong or the hook is not emergent.

### 11.2 Seven tests (run them in order; stop at the first failure)

| # | Test | How | Pass threshold (house default) |
|---|---|---|---|
| 1 | Recognition | Show the line to 5 target-segment players; ask if they know both titles | ≥ 4/5 know X; ≥ 3/5 know Y |
| 2 | Prediction | Ask them: "What would you do in the first minute?" Compare with the design's first minute | ≥ 3/5 describe the core verb correctly |
| 3 | Emergence ("so what") | Write what the blend has that neither input has, in one sentence | Sentence exists and is not a theme |
| 4 | Expectation budget | List the expectations a player of X brings; count how many the concept breaks | Exactly one deliberate break (see `genre-playbooks` Core model 2) |
| 5 | 3-second ad | Storyboard three 3–6-second muted creatives showing the hook in gameplay | At least 2 of 3 show the hook without text |
| 6 | Unpacking | Show a greybox screenshot without the line; ask what games it resembles | Players name X (and ideally Y) |
| 7 | Market | Search stores and ad libraries for the same blend (`references/concept-generation-playbook.md` step 5) | Fewer than 3 live, well-rated titles with the same blend, or a clear quality or audience gap |

Tests 1, 2 and 6 use people. In early ideation, a `arcosian:player-simulator` persona pass may stand in as a rough filter, but record it as a proxy and re-run with humans before committing.

### 11.3 Common line failures

| Failure | Symptom | Fix |
|---|---|---|
| Obscure input | Team loves the reference; the segment never heard of it | Replace Y with a mainstream equivalent, or describe the relation directly |
| Inverted order | "Monopoly meets Coin Master" sets the wrong core expectation | Put the core-verb owner first |
| Two cores | Each input owns a different verb | Make one the meta (fusion rule 1 in `genre-playbooks` procedure C) |
| Theme as Y | "Merge meets vampires" | Find a relation from the theme world or re-phrase as "X in a Y world" |
| Overclaiming | "Clash Royale meets Stardew Valley" for a merge game with farm art | Pick inputs whose relations are actually present |

---

## 12. Worked example A: Marvel Snap's stakes → an async word duel

**Step 1 — Frame.** Target: a 1v1 async word game in the tradition of Scrabble-style play (Words With Friends lineage). Problem: matches are long and the outcome feels settled early, so players abandon losing matches and the ranked ladder feels flat. Segment: adult word-game players; motivations *competition*, *strategy*.

**Step 2 — Retrieve by relation.** Query: "games where a player can raise the stakes mid-match and the opponent can concede cheaply". Candidates: Marvel Snap (snap and retreat), poker (raise and fold), backgammon (the doubling cube). Three sources share the relation, which is a strong sign the schema is real.

**Step 3 — Abstract and compare.** Shared schema across all three: *hidden or uncertain information + a public, optional escalation of stakes + an option to exit at the current stake*. Marvel Snap adds short fixed match length; backgammon adds the doubling cube's ownership (only the player who did not last double may redouble).

**Step 4 — Identify structure.**

| ID | Relation | Order | Essential |
|---|---|---|---|
| R1 | `HIDDEN(opponent_resources)` | 1 | yes |
| R2 | `UNCERTAIN(outcome)` until late in the match | 1 | yes |
| R3 | `CAN_RAISE(player, stake) → DOUBLES(stake)` | 1 | yes |
| R4 | `CAN_RETREAT(player) → PAYS(current_stake)` | 1 | yes |
| H1 | `ENABLES(R1 ∧ R3, bluff)` | 2 | yes |
| H2 | `PREVENTS(R4, catastrophic_loss_from_bad_matchups)` | 2 | yes |
| H3 | `CAUSES(R3, time_pressure_on_opponent_decision)` | 2 | yes |

Supporting structure the target needs: (S1) a multi-turn match with progressive reveal; (S2) a readable mid-match win estimate; (S3) a non-purchasable stake currency (rank points), never money or paid currency; (S4) short matches so a raise lands while the match is hot.

**Step 5 — Map.**

| Source | Target | Status |
|---|---|---|
| Hidden hand (R1) | Hidden letter rack | mapped |
| Uncertain outcome (R2) | Five-round match; scores visible, racks hidden | mapped |
| Snap doubles cubes (R3) | "Double" button doubles rank stars at stake; one double per player | mapped |
| Retreat (R4) | Concede before your turn: pay the current stake | mapped |
| Bluff (H1) | A double with a weak rack | mapped |
| Retreat limits losses (H2) | Concede at 1 star instead of losing 2 | mapped |
| Time pressure (H3) | Async play removes real-time pressure | **unmapped** |
| S1, S2, S3 | present | present |
| S4 short matches | Async matches last hours | **absent** |

**Step 6 — Evaluate.** RC = 4/4 = 1.0; HC = 2/3 = 0.67; SF = 3/4 = 0.75; V = 0; L = 0.

AFS = 100 × (0.35 × 1.0 + 0.35 × 0.667 + 0.30 × 0.75) − 0 − 0 ≈ 81 → **GO**, with the H3 gap noted.

**Step 7 — Adapt.** Rebuild H3 and S4 without adding a real-time timer that punishes busy adults: compress matches to five rounds; a double is shown at the start of the opponent's next turn and must be answered (accept or concede) before they can play. Pressure now comes from the decision blocking their move. Re-score: H3 partial (0.5) → HC = 0.83; S4 partial (shorter matches) → SF = 0.875. AFS ≈ 100 × (0.35 + 0.29 + 0.26) ≈ 90.

**Step 8 — Blend and line.** Emergent structure: *the rack you hide becomes a bargaining chip*, which neither Scrabble-style play (no wager) nor Marvel Snap (no word-building) has. Line: "Words With Friends meets Marvel Snap". Expectation budget: one break (stakes on a word game).

**Step 9 — Test.** Prediction: doubling raises the share of matches played to completion or conceded cleanly, versus abandoned. Metric: abandoned-match rate. Cheapest test: a bot-vs-bot simulation to tune the double's expected value, then a 2-cell A/B in soft launch (`ab_test.py size --baseline 0.30 --mde 0.05`). Ethics guard: stakes are rank stars only; no purchasable currency is ever at stake (`legal-ethics`, `monetization`).

---

## 13. Worked example B: a real-world system → a puzzle meta (short)

Target problem: a block-puzzle game (1010! lineage) with no reason to return tomorrow. Far source: a **parcel logistics hub** (see `references/cross-domain-sources.md`, real-world systems).

| Source relation | Target relation | Status |
|---|---|---|
| `FILLS(parcels, van)`; `DEPARTS(full_van)` | `FILLS(pieces, row)`; `CLEARS(full_row)` | mapped (the core already has it) |
| `REQUIRES(order, parcel_mix)` | Daily orders ask for lines that contain specific piece colours | mapped |
| `CAUSES(on_time_delivery, town_growth)` | Orders delivered grow a visible town map | mapped |
| `PENALISES(late_delivery)` | None (no fail pressure wanted) | dropped deliberately; not essential |
| Support: discrete deliveries, a visible map | present after adding the map | present |

RC 1.0, HC 1.0, SF 1.0 → AFS 100 before production cost. The analogy is clean; the risk moves to novelty (several block puzzles already add adventure maps), which the market-gap step must check. This is the seed "Pebble Courier" in `references/concept-generation-playbook.md`.

---

## 14. Failure modes and red flags

| Failure | Red flag | Diagnosis | Fix |
|---|---|---|---|
| Cargo cult | A borrowed feature is described by its source name ("our Butler's Gift") | Crossed at feature level | Climb the ladder (section 6) |
| Mere-appearance analogy | Mapping table is mostly attributes | High L | Rewrite in predicates; drop rows that change only art |
| Missing support | "It worked there" with no discrete attempts, sinks or stakes in the target | Low SF | Build the support or abandon |
| Collage | Two modes, two verbs, no emergent sentence | No blend | Choose one chassis; demote the other to meta or cut |
| IP mismatch | A strong IP mapped onto a structure the IP does not express | Purpose constraint violated | Map the IP's **relations** (collection, rivalry, building) to the loop, not just its characters |
| Era transfer | A 2012 viral loop copied into a post-2021 paid-UA world | Context filter ignored | Re-run the economics (`game-case-studies` Core model 4) |
| Fixation | The concept repeats the source's flaws (energy walls, ad spam) | Saw the example first | List source weaknesses before mapping; generate before looking |
| Dark-pattern import | The borrowed relation is a pressure mechanic (fake scarcity, loss framing for minors) | Ethics violation | Hard stop; see `legal-ethics` |

---

## 15. Checklists and agent templates

### 15.1 Pre-mapping checklist
- [ ] The target problem is written as a player-experience gap, with segment and motivations.
- [ ] At least one near, one mid and one far source were retrieved by relation.
- [ ] Two or more sources were compared and their shared relations extracted.
- [ ] The source's known weaknesses are listed.

### 15.2 Mapping checklist
- [ ] Every row is a relation with mapped arguments; attributes are flagged `surface_only`.
- [ ] Essential higher-order relations are identified and mapped or explained.
- [ ] Supporting structure is checked in the target.
- [ ] Constraints checked: session, one-thumb input, orientation, low-end device, monetization moment, minors and ethics.
- [ ] AFS computed; verdict recorded; adapt cycles ≤ 2.

### 15.3 Pitch checklist
- [ ] Chassis first, hook source second; no third input.
- [ ] Emergent sentence written.
- [ ] Exactly one broken expectation.
- [ ] Recognition, prediction and unpacking tests scheduled with segment players.

### 15.4 Agent prompt template (for `arcosian:game-designer` or a concept-tournament agent)

```
TASK: Design-by-analogy pass.
TARGET PROBLEM: <player-experience gap>; SEGMENT: <...>; MOTIVATIONS: <...>
CONSTRAINTS: portrait one-thumb; session <N> s; monetization <model>; age_min <N>.
1. Retrieve 8 sources by RELATION (3 near, 3 mid, 2 far). For each: one-line relation it offers.
2. Abstract the best 3 using the analogy-method section 7 template.
3. Extract shared relations (analogical encoding).
4. Build the mapping table (section 8.1) for the best source; flag essential, order, status, surface_only.
5. Compute AFS with scripts/analogy_score.py fitness; adapt up to twice.
6. State the emergent structure and an "X meets Y" line; run tests 3, 4 and 5 yourself; list tests 1, 2, 6 and 7 as TODO with owners.
OUTPUT: mapping JSON (for analogy_score.py), concept.comparables entries, analogy line, hook, test plan.
```

### 15.5 Mapping JSON format (input to `analogy_score.py fitness --mapping`)

The fragment below shows the format only (three relations, one surface row, one soft violation; it scores ADAPT). Worked example A's full mapping (R1–R4, H1–H3, S1–S4) scores about 81 before adaptation. Save mappings as `.gamestudio/concepts/<id>.mapping.json` next to the concept card; `analogy_score.py rank --dir` skips them.

```json
{
  "source": "Marvel Snap",
  "target": "async word duel",
  "relations": [
    {"id": "R1", "order": 1, "essential": true, "status": "mapped"},
    {"id": "H3", "order": 2, "essential": true, "status": "partial"},
    {"id": "A1", "order": 0, "essential": false, "status": "mapped", "surface_only": true}
  ],
  "support": [
    {"id": "S1", "present": true},
    {"id": "S4", "present": "partial"}
  ],
  "violations": [
    {"id": "V1", "kind": "session", "hard": false, "note": "matches span hours"}
  ]
}
```

`order` 1 = first-order relation, 2 = higher-order relation, 0 = attribute. `status` ∈ `mapped | partial | unmapped`. `present` ∈ `true | false | "partial"`. A violation with `"hard": true` (ethics, legal, platform policy) forces DROP.
