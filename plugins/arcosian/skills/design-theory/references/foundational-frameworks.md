# Foundational Design Frameworks — A Working Practitioner's Digest

The field's canonical frameworks, each restated in plain terms and turned into a design tool you can run on a concept, a feature spec or a live game. For every framework you get: the core idea (paraphrased, with author, work and year), how to apply it as a procedure, a mobile example, and where it breaks. Nothing here replaces the original works; it is a working digest so a designer or agent can pick the right lens for the question at hand and avoid misusing it. Read the selection matrix first, then jump to the framework you need. Frameworks are tools for asking better questions — none of them generates a game on its own, and several contradict each other on purpose.

## Contents

1. Selection matrix: which framework answers which question
2. MDA (Hunicke, LeBlanc, Zubek 2004) and its critiques
3. DDE (Walk, Görlich, Barrett 2017)
4. LeBlanc's eight kinds of fun
5. Caillois: agon, alea, mimicry, ilinx; paidia–ludus
6. Huizinga and the magic circle
7. Salen & Zimmerman: meaningful play
8. Juul: emergence vs progression; half-real
9. Koster: theory of fun and the grammar of gameplay
10. Schell: the lens method
11. Fullerton: formal and dramatic elements
12. Adams & Dormans: internal economies and Machinations
13. Sylvester: elegance and depth
14. Swink: game feel
15. Dan Cook: skill atoms, skill chains, loops and arcs
16. Sid Meier: interesting decisions
17. Flow (Csikszentmihalyi) and flow in games (Chen)
18. Lazzaro: four keys to emotion
19. Bartle's player types
20. Quantic Foundry's Gamer Motivation Model
21. Self-determination theory and PENS
22. Hodent: game UX and the gamer's brain
23. Bonus tools: Church's formal abstract design tools; the elemental tetrad
24. Running several frameworks together: one worked pass
25. Sources and further reading

---

## 1. Selection matrix

| Question you are trying to answer | Primary framework | Secondary | Output you should produce |
|---|---|---|---|
| "What experience are we building and which rules produce it?" | MDA | DDE, Schell tetrad | Aesthetic targets → dynamics → mechanics table |
| "Why does this feel flat even though the rules work?" | DDE | Swink, Hodent | List of non-mechanical design levers (interface, art, audio, fiction) |
| "Which kinds of fun are we offering?" | LeBlanc 8 kinds | Lazzaro, Caillois | Ranked aesthetic profile (top 2–3) |
| "Is the play mode competitive, chance, role-play or sensation?" | Caillois | LeBlanc | Mix of agon/alea/mimicry/ilinx with intensity |
| "How does the game handle interruptions and the real world leaking in?" | Huizinga (magic circle) | Consalvo critique | Entry/exit and boundary rules |
| "Do player actions actually matter?" | Salen & Zimmerman | Sid Meier | Action → discernable result → integrated consequence map |
| "Handmade content or systemic play?" | Juul (emergence/progression) | Cook (loops/arcs) | Content strategy and cost model |
| "Will people stay interested once they get it?" | Koster | Cook skill chains | Pattern inventory with mastery horizon per pattern |
| "Have we looked at this from every angle?" | Schell lenses | Diagnostic checklist | Question deck for reviews |
| "Is the spec complete?" | Fullerton formal elements | Ontology contract | Formal-element checklist filled in |
| "Will the economy snowball or stall?" | Adams & Dormans | `economy-design` | Machinations-style resource graph |
| "Is this deep or just complicated?" | Sylvester | `decisions-and-depth.md` | Depth/complexity ledger |
| "Does touching it feel good?" | Swink | `game-feel` | Input → response → polish spec |
| "Is the FTUE teaching the right things in the right order?" | Cook skill atoms | Hodent | Skill chain diagram with teach points |
| "Are the decisions interesting?" | Sid Meier | Sylvester | Decision audit table |
| "Is difficulty matched to skill?" | Flow / Chen | `progression-difficulty` | Challenge/skill curve and DDA policy |
| "What emotions does play produce?" | Lazzaro | LeBlanc | Emotion map per loop |
| "Who is this for?" | Quantic Foundry | Bartle, SDT | Motivation profile of target segment |
| "Will players feel competent, free and connected?" | SDT / PENS | Hodent | Need-satisfaction audit |
| "Can players perceive, understand and remember it?" | Hodent | `mobile-ux` | Usability + engage-ability audit |

Rule of thumb: start every concept with MDA (aesthetics first), check the target player with Quantic Foundry or SDT, then test the core loop with Cook and Meier. Use the rest as diagnostic lenses when something feels wrong.

---

## 2. MDA — Mechanics, Dynamics, Aesthetics

**Source.** Robin Hunicke, Marc LeBlanc, Robert Zubek, "MDA: A Formal Approach to Game Design and Game Research", AAAI Workshop on Challenges in Game AI, 2004. Developed from the Game Design and Tuning Workshop run at GDC in the early 2000s.

**Core idea.** A game is an artifact that is *consumed* rather than watched, and it breaks into three causally linked layers:
- **Mechanics** — the rules, data and algorithms (what the designer directly writes).
- **Dynamics** — the run-time behaviour that emerges when mechanics meet player input over time (bluffing, hoarding, rushing, cascades).
- **Aesthetics** — the emotional responses the player has (the paper's sense of "aesthetics", not visual style).

The designer works M → D → A: they can only touch mechanics, and must predict dynamics and aesthetics. The player experiences A → D → M: they feel the aesthetics first and may never consciously see the mechanics. The paper's central discipline is to state the target aesthetics explicitly and then reason backwards to the mechanics most likely to produce them, verifying by play.

**Apply it as a design tool.**
1. Write the top 2–3 target aesthetics as a ranked list (use LeBlanc's eight kinds, section 4, as vocabulary).
2. For each aesthetic, write the dynamics that would produce it ("Challenge" → "late-level move scarcity forces planning").
3. For each dynamic, list the mechanics and parameters that drive it ("move limit 20–30; special pieces from 4-matches").
4. Fill the table below and store mechanics in the contract (`mechanics[]`) and aesthetics in mechanic cards (`aesthetics`).
5. Playtest and work forward: observe dynamics, ask players what they felt, compare with targets, adjust mechanics only.

| Target aesthetic | Required dynamic | Mechanics and parameters | Evidence it works |
|---|---|---|---|
| Challenge (rank 1) | Planning under scarcity in the last 5 moves | `moves_limit` per level; blockers that need 2 hits | Attempts p50 per level within target; players pause before final moves |
| Sensation (rank 2) | Frequent multi-step cascades | Gravity refill, combo multiplier, haptic on chain ≥ 3 | Cascades per move ≥ target; session telemetry |
| Submission (rank 3) | Low cognitive load between hard moments | Easy "breather" levels every 3–5 levels | Session length stable; no rage-quit spikes |

**Mobile example.** A match-3 targets Challenge + Sensation + Submission (pastime). The move limit creates a tension dynamic at the end of each level; random refills create surprise cascades (sensation); breather levels and unlimited-feeling early boards serve the "pastime" mode a commuter wants. When a level tests badly, the designer changes blocker counts or move limits (mechanics), never "adds more fun".

**Critiques and limits.**
- *The word "aesthetics" collides with visual aesthetics*, causing confused conversations; many teams say "experience" or "player emotion" instead.
- *Mechanics-centric.* MDA treats art, sound, narrative and interface as secondary, even though they shape experience directly (a horror game's audio is not a mechanic but is central). DDE (section 3) and Schell's tetrad (section 23) respond to this.
- *Linear causality.* Real play loops back: aesthetics change player behaviour, which changes dynamics. Players bring culture, mood and context the designer does not control.
- *The aesthetic taxonomy is incomplete.* The eight kinds omit, for example, social status, nostalgia, collection, creative ownership and relaxation as distinct targets; treat the list as a starting vocabulary.
- *It predicts nothing quantitatively.* MDA structures the reasoning; simulation and playtests supply the evidence.

---

## 3. DDE — Design, Dynamics, Experience

**Source.** Wolfgang Walk, Daniel Görlich, Mark Barrett, "Design, Dynamics, Experience (DDE): An Advancement of the MDA Framework for Game Design", in *Game Dynamics* (Springer, 2017).

**Core idea (paraphrased).** DDE keeps MDA's three-layer chain but widens both ends. "Mechanics" becomes **Design**, which explicitly includes the *blueprint* (concept, world, characters, narrative frame), the *mechanics* (rules and code) and the *interface* (everything the player sees, hears and touches). "Aesthetics" becomes **Experience**, which centres the player as a subject whose sensory, emotional and intellectual responses are the true product. Dynamics remains the run-time layer in between. The practical upshot: art, sound, writing and UI are first-class design layers, not decoration applied after the rules.

**Apply it as a design tool.**
1. When a mechanic tests "correct but joyless", run a DDE pass: list every *interface* and *blueprint* lever touching that moment (camera, timing, sound, animation, fiction, copy).
2. For each lever, state the intended experience change and a cheap test (swap SFX, add 80 ms hit-stop, rename the resource).
3. Assign owners across disciplines: interface → `arcosian:ux-designer` with the `game-feel` and `mobile-ux` skills; blueprint → `arcosian:narrative-designer` and `arcosian:art-director`.
4. Re-test the moment with the mechanic unchanged; if the experience moves, the problem was never the rules.

**Mobile example.** A merge game's core merge feels flat. Mechanics are fine (merge 3 → next tier). DDE pass: add a squash-and-stretch on the result item, a rising pitch per merge tier, a short particle burst and a one-word praise label; reframe items from "Level 4 Item" to a named object in a story chain. Same rules, different experience.

**Limits.** DDE is less widely adopted and less operationalised than MDA; its terms are broad, so teams still need concrete checklists (Swink for feel, Hodent for UX, `art-direction` for visuals) to act on it.

---

## 4. LeBlanc's eight kinds of fun

**Source.** Marc LeBlanc's taxonomy, published within the MDA paper (2004) and taught in his GDC tutorials.

**Core idea.** Replace the useless word "fun" with a vocabulary of distinct aesthetic targets:

| Kind | Player's experience in plain terms | Typical mobile carriers |
|---|---|---|
| Sensation | Game as sense-pleasure | Juicy slicing, haptics, satisfying physics, ASMR-like sorting |
| Fantasy | Game as make-believe | Becoming a chef, a mayor, a hero; cosmetic identity |
| Narrative | Game as drama | Episodic story meta in decorate-and-match games |
| Challenge | Game as obstacle course | Hard levels, PvP ladders, speedruns |
| Fellowship | Game as social framework | Clans, co-op events, gifting lives |
| Discovery | Game as uncharted territory | New biomes, secret recipes, unknown merge results |
| Expression | Game as self-discovery and self-display | Base/room decoration, avatar creation, deck building |
| Submission | Game as pastime | Low-stakes, repetitive, relaxing play during a commute |

**Apply it as a design tool.**
1. Rank the eight for your concept; keep the top three. A game that claims all eight has no focus.
2. Check each top-three aesthetic has at least one loop that delivers it every session (see `core-loops-and-structure.md`).
3. Check the bottom-ranked kinds are not accidentally undermined (e.g., heavy story popups wrecking Submission players).
4. Use the ranking to settle disputes: a proposed feature that serves only a bottom-ranked kind needs a strong case.

**Mobile example.** Idle tycoon games rank Submission, Fantasy (owning an empire) and Discovery (next business unlock) highest; Challenge is deliberately minimal. Adding a hard skill-based minigame to such a game typically serves a kind its audience did not come for.

**Limits.** Kinds overlap; the list is not exhaustive (see MDA critiques); and ranking is a judgment, so validate with target-player interviews or motivation surveys (section 20).

---

## 5. Caillois — agon, alea, mimicry, ilinx; paidia and ludus

**Source.** Roger Caillois, *Les Jeux et les Hommes* (1958), English translation *Man, Play and Games* (1961).

**Core idea.** Play falls into four fundamental categories, which combine:
- **Agon** — competition where skill decides the winner under equal conditions.
- **Alea** — chance, where the player surrenders to fate.
- **Mimicry** — simulation, role-play, becoming someone else.
- **Ilinx** — vertigo, the pleasure of disorienting perception (speed, spinning, falling).

Cross-cutting these is a continuum from **paidia** (free, improvised, tumultuous play) to **ludus** (play disciplined by rules, conventions and deliberate difficulty).

**Apply it as a design tool.**
1. Score your core loop 0–3 on each of agon, alea, mimicry, ilinx, and place it on the paidia–ludus axis.
2. Check the alea/agon balance against the audience: high agon with high alea frustrates competitive players ("I lost to a dice roll"); high agon with no alea can scare casual players who fear being judged.
3. Use the paidia–ludus position to decide structure: paidia-leaning games need toys, sandboxes and few fail states; ludus-leaning games need clear goals, ranks and difficulty curves.

| Mobile game type | Agon | Alea | Mimicry | Ilinx | Paidia ↔ Ludus |
|---|---|---|---|---|---|
| PvP card arena (Clash Royale-like) | 3 | 1 (card cycle order) | 1 | 0 | Ludus |
| Dice-board social casino-adjacent (Monopoly GO!-like) | 0–1 | 3 | 1 | 1 | Ludus (shallow) |
| Dollhouse role-play (Toca Life-like) | 0 | 0 | 3 | 0 | Paidia |
| Endless runner (Subway Surfers-like) | 2 (score) | 1 | 1 | 2 | Middle |
| Snowboarding flow (Alto's Odyssey-like) | 1 | 0 | 1 | 3 | Middle |

**Limits.** Written about play broadly, not digital design; categories describe flavour, not structure; Caillois also discussed "corruptions" of each category (e.g., alea sliding into superstition and gambling), which is directly relevant to chance-based monetization — see `legal-ethics` and `monetization`.

---

## 6. Huizinga and the magic circle

**Source.** Johan Huizinga, *Homo Ludens* (1938). Huizinga lists the "magic circle" among several images of play-grounds (the arena, the card table, the stage); Katie Salen and Eric Zimmerman made it a central design concept in *Rules of Play* (2003).

**Core idea.** Play happens in a bounded space and time with its own rules and meanings, separate from ordinary life: a pawn is "just wood" outside the game, a powerful piece inside it. Entering the circle means accepting arbitrary rules voluntarily. Huizinga also stresses that play is free, not tied to material gain, and creates its own order.

**Apply it as a design tool.** Treat the boundary as something you design:
1. **Entry** — how fast does a player cross into play from the home screen? Target one tap to resume the core loop.
2. **Integrity** — what breaks the circle mid-play? (Interstitial ads, permission prompts, store popups, lag spikes.) Move them to natural boundaries.
3. **Exit** — can the player leave at any moment without punishment, and re-enter with context restored?
4. **Leakage by design** — which real-world elements do you deliberately import (location, friends, real time, real money)? Each one weakens the protective frame and needs ethical review.

**Mobile example.** On phones the circle is porous: notifications, calls and a bus stop end sessions unpredictably. Good mobile design auto-saves every action, resumes mid-level, and places interstitials only between levels. Location-based games (Pokémon GO) intentionally dissolve the circle into the street, which creates both their magic and their safety obligations.

**Limits.** Critics, notably Mia Consalvo ("There is No Magic Circle", *Games and Culture*, 2009), argue that the boundary is always permeable: real money, reputations, cheating and social relationships flow across it. In F2P with real-money purchases, assume the circle is broken by default and design consumer protections accordingly.

---

## 7. Salen & Zimmerman — meaningful play

**Source.** Katie Salen and Eric Zimmerman, *Rules of Play: Game Design Fundamentals* (MIT Press, 2003).

**Core idea.** Meaningful play arises from the relationship between a player's action and the system's outcome. It needs two properties:
- **Discernable** — the player can perceive the immediate result of the action.
- **Integrated** — the action matters to the larger arc of the game, not just the moment.
The book also offers a game definition built on a rule-bound, artificial conflict with a measurable outcome, and three lenses (they call them schemas) for studying games: rules (formal), play (experiential) and culture (contextual).

**Apply it as a design tool.** Build an action–outcome map for each verb:

| Verb | Immediate, discernable result | Integrated consequence (later) | Gap? |
|---|---|---|---|
| Swap tiles | Tiles clear, sound, score tick | Stars → map progress → new world | OK |
| Tap "collect" in idle | Coins counter ticks | Upgrades purchasable | Weak if the tap amount is negligible vs. passive income |
| Choose upgrade card | Card highlight | Build identity for rest of run | OK if the effect is visible within 10–20 s |
| Daily login | Reward popup | Streak meter | Weak: no decision, little meaning |

Flag any verb missing either column. Undiscernable actions feel like pressing a dead button; unintegrated actions feel pointless after the first few minutes.

**Mobile example.** Roguelite shooters that let players choose one of three upgrades on level-up (Archero-like) make the choice discernable through immediate visual changes (extra projectiles) and integrated through the build it creates.

**Limits.** "Meaningful" is not the same as "fun": a highly meaningful choice can still be tedious. The definition of "game" excludes sandbox and toy experiences that are commercially vital on mobile.

---

## 8. Juul — emergence vs progression; half-real

**Sources.** Jesper Juul, "The Open and the Closed: Games of Emergence and Games of Progression" (Computer Games and Digital Cultures conference, 2002); *Half-Real: Video Games between Real Rules and Fictional Worlds* (MIT Press, 2005). Also relevant: *A Casual Revolution* (2010) and *The Art of Failure* (2013).

**Core idea.**
- **Games of emergence**: a small number of rules combine into large variation; replayable; strategy guides describe principles (chess, card battlers, physics sandboxes).
- **Games of progression**: the designer sequences challenges; content is consumed once; guides are walkthroughs (adventure games, handcrafted puzzle campaigns).
- Most modern games mix both: emergent mechanics inside a progression structure.
- **Half-real**: games are *real* rules (you really win or lose) plus a *fictional* world (you are not really a knight). The fiction can be incomplete or incoherent and players happily fill gaps ("why do I have three lives?"). Fiction cues rules ("fire probably burns"), and rules give the fiction its texture.

**Apply it as a design tool.**
1. Decide the emergence/progression ratio up front, because it determines production cost: progression requires a content treadmill; emergence requires systemic depth and balance work.
2. For live games, estimate content burn: if players consume a handmade level in ~2 minutes and you ship 50 per fortnight, that is ~100 minutes of progression content per update — compare with your engaged players' playtime.
3. Use fiction to teach rules for free: shape, colour and theme should predict behaviour; audit every rule that contradicts its fiction.

**Mobile example.** Match-3 sagas are progression structures (hundreds of handmade levels) wrapped around an emergent core (cascades from random refills). Card battlers are emergence-first; their "progression" is the collection, not a level list.

**Limits.** The dichotomy is a spectrum; emergent systems can still need tutorials sequenced like progression; half-real does not tell you *how much* fiction coherence your audience needs (narrative-driven players need far more).

---

## 9. Koster — theory of fun and the grammar of gameplay

**Sources.** Raph Koster, *A Theory of Fun for Game Design* (2004; 10th anniversary edition 2013); his talk "A Grammar of Gameplay (Game Atoms: Can Games Be Diagrammed?)", GDC 2005, and later talks on game grammar ("Game Grammar", PAXDev 2015; "Tabletop Game Grammar", 2018), listed on [Koster's presentations page](https://www.raphkoster.com/games/presentations/), plus his blog writing on game atoms.

**Core idea.** Fun is the feeling of the brain learning patterns. A game is a puzzle-like system the player models; enjoyment comes from making progress on understanding it. Two failure modes follow: when the pattern is fully absorbed ("grokked"), the game becomes boring; when the signal looks like noise (no learnable pattern), it is frustrating. Koster's grammar work proposes diagramming games as nested "atoms": the player acts, a hidden model updates, feedback returns, and the player learns — larger games are compositions of these atoms.

**Apply it as a design tool.**
1. Make a **pattern inventory**: list each pattern players must learn (e.g., "4-in-a-row makes a striped piece", "enemy telegraph then lunge").
2. For each, estimate its **mastery horizon** (sessions until grokked) and what **replaces** it (new variant, new combination, new opponent).
3. Check the **noise floor**: can a novice tell why they failed? If not, the pattern reads as noise.
4. Diagram each atom (input → model → feedback → what is learned). An atom that teaches nothing new after session 3 needs a twist, a combination, or removal.

**Mobile example.** Sliding-number games (Threes!/2048-likes) have a dominant pattern (keep the big tile in a corner). Once players grok it, many churn — unless the game layers new patterns (special tiles, goals, daily puzzles). Live-ops events in match-3 games work partly because each event introduces a fresh pattern.

**Limits.** Learning is not the only pleasure: sensation, social status, collection and relaxation also retain players. Grind-heavy games retain players long after patterns are learned through extrinsic structures, which Koster's model treats as a warning sign rather than a target.

---

## 10. Schell — the lens method

**Source.** Jesse Schell, *The Art of Game Design: A Book of Lenses* (2008; later editions 2014 and 2019).

**Core idea (summarised method, not the lenses themselves).** Design is improved by looking at the same game from many perspectives, each defined by a short set of probing questions. A "lens" is a reusable viewpoint — on the player, the experience, a mechanic, the story, the business — that forces the designer to notice what they would otherwise skip. Schell also organises the game into four elements (mechanics, story, aesthetics, technology — the "elemental tetrad", section 23) and uses interest curves to reason about pacing (see `core-loops-and-structure.md`). The book contains over a hundred lenses; this skill does not reproduce them.

**Apply the method.**
1. Build your *own* lens deck for your project: 15–30 cards, each with a name, a one-line perspective and 2–4 questions specific to your genre. The diagnostic checklist in `design-diagnostic-checklist.md` is an original starting deck.
2. In design reviews, draw 5–7 lenses at random plus 3 mandatory ones (player fantasy, core loop, mobile session fit). Randomness surfaces blind spots.
3. Record each lens's verdict as a one-line finding with severity; route findings to owners.
4. Retire lenses that never produce findings; add lenses after each postmortem.

**Mobile example.** A team building a commute game writes a custom lens "The One-Station Session": *Can a player start, achieve something meaningful, and stop within the 2 minutes between two metro stations? What do they think about after closing the app?*

**Limits.** Lenses do not prioritise themselves; applying all of them paralyses teams. Use severity ranking and the doctrine's priority order (player first, find the fun fast) to decide what to act on.

---

## 11. Fullerton — formal and dramatic elements

**Source.** Tracy Fullerton, *Game Design Workshop: A Playcentric Approach to Creating Innovative Games* (first edition 2004 with Christopher Swain and Steven Hoffman; fourth edition 2018).

**Core idea.** Games share a set of **formal elements** — the structure that makes them games — and **dramatic elements** that make players emotionally engaged. Paraphrased:
- Formal: players (number and roles, interaction pattern), objectives, procedures (the actions and how they are performed), rules, resources, conflict (obstacles, opponents, dilemmas), boundaries, outcome.
- Dramatic: challenge, play (types of play and players), premise, character, story, world-building.
Fullerton also catalogues player interaction patterns (single player vs game, multiple individuals vs game, player vs player, unilateral and multilateral competition, cooperative, team competition) and champions a playcentric, prototype-and-playtest process.

**Apply it as a design tool: the formal-element completeness check.** Before writing a feature spec, fill this table; every blank is an unmade decision.

| Element | Wordle-style daily puzzle (worked example) |
|---|---|
| Players and pattern | 1 player vs game; social comparison via share grid (indirect) |
| Objective | Identify a hidden 5-letter word |
| Procedures | Type a word, submit, read colour feedback |
| Rules | Guess must be a valid word; feedback marks right letter/right spot, right letter/wrong spot, absent |
| Resources | 6 guesses |
| Conflict | Hidden information plus a narrowing search space |
| Boundaries | One puzzle per day, shared by all players |
| Outcome | Win/loss plus guess count; streak |
| Dramatic: premise | Minimal; the drama is the shrinking set of candidates |
| Dramatic: challenge | Vocabulary and deduction under a strict budget |

The worked example shows how few elements a hit needs when each one is sharp — and why "boundaries" (one per day) can be the most important design decision.

**Limits.** A checklist of what exists, not a theory of what is good; dramatic elements are thin for systemic or abstract games.

---

## 12. Adams & Dormans — internal economies and Machinations

**Source.** Ernest Adams and Joris Dormans, *Game Mechanics: Advanced Game Design* (New Riders, 2012). Machinations diagrams originate in Dormans' research (his PhD work on engineering emergence); the commercial tool lives at machinations.io.

**Core idea.** Many game mechanics form an **internal economy**: resources produced by sources, stored in pools, transformed by converters, consumed by drains (sinks), gated and traded, connected by flows. Feedback loops in this graph determine the game's long-term shape: positive feedback amplifies differences (snowballing), negative feedback dampens them (catch-up). The book names recurring structural patterns — engines (static, dynamic, converter, engine-building), friction (static, dynamic), escalation, attrition, stopping mechanisms, arms races, among others — that predict dynamics from structure.

**Apply it as a design tool.**
1. Draw every resource as a node; draw every action as a flow with a rate. Use the shared ontology's node kinds: `source`, `sink`, `converter`, `gate`, `pool` (`${CLAUDE_PLUGIN_ROOT}/scripts/schemas/economy-model.schema.json`).
2. Mark each loop as positive (+) or negative (−) feedback. Ask: what stops the + loops? (Stopping mechanisms: diminishing returns, rising costs, caps.)
3. Simulate rather than eyeball: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/economy_sim.py --model .gamestudio/economy/model.json --runs 200`.
4. Check the snowball window: in competitive modes, how many minutes after an early lead is the outcome effectively decided? If the answer is "almost immediately", add negative feedback or comeback mechanisms.

| Pattern | Structure | Mobile example | Risk |
|---|---|---|---|
| Dynamic engine | Output can be reinvested to raise output | Idle games: buy generators that buy generators | Exponential runaway → needs prestige/reset |
| Converter engine | Resource A → B → A with gain | Crafting chains in farm games | Arbitrage exploits |
| Static friction | Fixed drain on resources | Upkeep, repair costs | Feels like a tax if invisible |
| Dynamic friction | Drain scales with player power | Enemy scaling in roguelites | Progress feels meaningless if scaling matches power exactly |
| Stopping mechanism | Effect weakens with repetition | Diminishing returns on stacked buffs | Under-tuned → dominant stacking |

**Limits.** Machinations models flows well but models spatial, dexterity and social play poorly; outputs are only as good as the rate assumptions. Validate against telemetry after launch (`player-analytics`).

---

## 13. Sylvester — elegance and depth

**Source.** Tynan Sylvester, *Designing Games: A Guide to Engineering Experiences* (O'Reilly, 2013).

**Core idea (paraphrased).** Games are engines for producing emotional experiences through events. **Depth** is the range of play the system supports before players exhaust it — often visible as a long skill ladder where better play keeps winning. **Complexity** is the burden of rules and exceptions the player must learn. **Elegance** is achieving a lot of depth from a little complexity: mechanics that interact with many others, so each rule pays for itself many times. Sylvester also emphasises that mechanics must generate *decisions* and *emotional events*, and that fiction and mechanics should support each other.

**Apply it as a design tool: the depth/complexity ledger.**
1. List every rule, exception, unit ability and UI concept the player must learn. Give each a complexity cost (1 = intuitive, 3 = needs a tutorial step, 5 = needs repeated explanation).
2. For each, list the decisions and interactions it creates (how many other elements does it combine with?).
3. Compute an informal elegance ratio = interactions created / complexity cost. Cut or rework anything with ratio < 1.
4. Prefer rules that reuse existing knowledge (fiction, genre conventions) over novel exceptions.

**Mobile example.** Clash Royale-style elixir is elegant: one regenerating resource governs pacing, card value, timing trades and comeback potential. By contrast, a mobile RPG with six currencies for six upgrade tracks adds complexity with few new decisions.

**Limits.** "Depth" is hard to measure directly; use proxies (skill rating spread, win-rate gap between expert and novice bots — see `decisions-and-depth.md`). Some audiences actively *want* complexity (simulation fans), so elegance is a goal, not a law.

---

## 14. Swink — game feel

**Source.** Steve Swink, *Game Feel: A Game Designer's Guide to Virtual Sensation* (Morgan Kaufmann, 2008).

**Core idea.** Game feel is the tactile, kinesthetic sense of controlling a virtual object in real time. Swink defines it through three building blocks — **real-time control**, **simulated space** (the object interacts with a world) and **polish** (effects that emphasise interactions without changing the simulation) — and analyses feel through components: input, response, context (the spaces and obstacles that give movement meaning), polish, metaphor (what the fiction leads players to expect) and rules. He draws on human-processor models from human–computer interaction research to argue that responses within roughly a tenth of a second read as instantaneous, while longer delays break the sense of direct control.

**Apply it as a design tool.**
1. For each touch interaction, specify: input (gesture), response curve (acceleration, max speed, damping), context (what the movement is for), polish (animation, particles, sound, haptics, camera), metaphor (what it should feel like: "heavy", "snappy").
2. Measure input-to-visible-response latency on a low-end device; aim to keep it as low as the platform allows and investigate anything that feels laggy (touch sampling, frame pacing and rendering all add delay).
3. Tune in isolation first (a "feel toy" scene with no goals); if moving around is fun with no objective, the core will carry.

**Mobile example.** One-thumb flicking in archery or golf games: the drag distance maps to power with a visible trajectory preview (response + polish), a slight slow-motion on release (polish), and a haptic tick at max power (feedback). See `game-feel` for parameter tables.

**Limits.** Swink focuses on real-time avatar control; turn-based and menu-driven mobile games need the broader "juice" and feedback practices in `game-feel` and `mobile-ux`. Touchscreens remove the tactile button travel that much of the original analysis assumes.

---

## 15. Dan Cook — skill atoms, skill chains, loops and arcs

**Sources.** Daniel Cook, "The Chemistry of Game Design" (Gamasutra, 2007); "Loops and Arcs" (Lost Garden blog, 2012); other Lost Garden essays.

**Core idea.**
- **Skill atom**: the smallest learning loop — the player takes an *action*, the game *simulates* a result, gives *feedback*, and the player updates their *mental model*. When the model is complete, the atom is mastered and stops producing pleasure ("burnout" of that atom).
- **Skill chain**: atoms depend on each other (you must learn "jump" before "jump over pit"); diagramming the dependency graph shows the order players must learn things and where they get stuck.
- **Loops and arcs**: a *loop* is a repeatable system that players can keep mastering; an *arc* is a piece of content consumed once (a story beat, a handcrafted level) — effectively a loop the player exits after one pass. Loops are cheap per hour of play but need depth; arcs are expensive per hour but give clear novelty.

**Apply it as a design tool.**
1. Draw the skill chain for the first 30 minutes as a DAG: nodes = atoms, edges = prerequisites.
2. Mark each atom with where it is taught, tested, and how you detect mastery (telemetry event).
3. Instrument each atom: if many players fail an atom repeatedly, the chain is broken upstream (an earlier atom was not learned).
4. For live games, compute the loop/arc mix: what fraction of weekly playtime comes from repeatable loops vs consumed arcs? Arc-heavy live games need a content pipeline that can keep up.

```
[tap tile] → [match 3] → [match 4 = striped] → [match 5 = colour bomb]
                    ↘ [clear blocker] → [plan around blockers] → [combine specials near blockers]
```

**Mobile example.** Match-3 FTUEs teach exactly one atom per level for the first several levels, each level designed so the new atom is the obvious solution. Telemetry on level-fail rates maps directly to atoms.

**Limits.** Atoms model skill learning, not social, aesthetic or collection motivations; designers sometimes over-tutorialise by atomising everything. Good games also let players discover atoms on their own.

---

## 16. Sid Meier — interesting decisions

**Source.** Sid Meier's widely quoted description of a game as "a series of interesting decisions"; elaborated in his GDC 2012 talk "Interesting Decisions".

**Core idea (paraphrased).** A decision is interesting when there is no obviously correct answer and the choice matters. Common restatements of the properties of interesting decisions include: real trade-offs between competing goods; the right answer depends on the situation; choices let players express personal style; consequences persist and shape later play; and the player has enough information to reason about the choice (but not so much that it becomes arithmetic). Uninteresting decisions are obvious, random, inconsequential, or blind.

**Apply it as a design tool: the decision audit.**

| Decision point | Trade-off present? | Situational? | Style-expressive? | Persistent? | Enough info? | Verdict |
|---|---|---|---|---|---|---|
| Which upgrade of 3 on level-up | Yes (damage vs survivability) | Yes (depends on build) | Yes | Run-long | Yes (icons + numbers) | Interesting |
| Claim daily reward | No | No | No | No | n/a | Not a decision — make it automatic or make it a choice |
| Spend gems to refill energy | Weak (money vs time) | Somewhat | No | Short | Yes | Monetization choice, not a gameplay decision |
| Pick a lane in a runner | Yes (coins vs safety) | Yes | Some | Seconds | Yes | Interesting at micro scale |

Remove or automate non-decisions; deepen weak ones by adding a second competing value.

**Mobile example.** Marvel Snap's "Snap" mechanic converts each match into a stakes decision (raise or retreat) layered on top of card-placement decisions — the retreat option makes losing a strategic choice rather than only a defeat.

**Limits.** Not all play is decision-making: dexterity, rhythm, sensation and social play can be deeply enjoyable with few decisions. On mobile, too many interesting decisions per minute exhausts commuting players; pace them (see `fun-and-motivation-design.md` on arousal).

---

## 17. Flow (Csikszentmihalyi) and flow in games (Chen)

**Sources.** Mihaly Csikszentmihalyi, *Flow: The Psychology of Optimal Experience* (1990), building on his 1970s research; Jenova Chen, "Flow in Games" (MFA thesis, USC, 2006) and "Flow in Games (and Everything Else)" (*Communications of the ACM*, 2007).

**Core idea.** Flow is a state of deep absorption in an activity, associated with clear goals, immediate feedback, and a balance between perceived challenge and skill. When challenge outruns skill the person drifts toward anxiety; when skill outruns challenge, toward boredom. Characteristic experiences include intense concentration, a sense of control, loss of self-consciousness and altered time perception. Chen adds two game-specific points: (1) different players have different flow zones, so one fixed difficulty curve fails many of them; (2) the best dynamic difficulty adjustment is often *embedded in player choice* — let players steer their own challenge (go deeper, take the optional harder path) rather than silently changing the game underneath them.

**Apply it as a design tool.**
1. Plot intended challenge vs expected skill across the first sessions; a good curve oscillates within the channel (tension, then release) rather than climbing linearly.
2. Give **player-driven difficulty levers**: optional objectives (3 stars), risk/reward paths, self-selected modifiers.
3. Use **system-driven DDA** sparingly and invisibly for safety nets only (e.g., after repeated failures), and never in competitive modes where fairness matters. Generate curves with `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/difficulty_curve.py generate --levels 60 --pattern sawtooth --base 0.85 --floor 0.45 --period 5` and analyse live data with `difficulty_curve.py analyze`.
4. Protect flow from interruptions: no popups during play; short sessions mean flow must be reached quickly (seconds, not minutes).

**Mobile example.** Puzzle sagas use sawtooth difficulty: a run of easier levels followed by a hard spike, then a breather. Optional star objectives let skilled players chase extra challenge while others just clear levels.

**Limits.** Flow is one desirable state among several; relaxation and social play need not be flow. Very short mobile sessions may not allow deep flow at all — aim for "micro-flow" in each level. Self-report measurement is unreliable; use behavioural proxies (retries, quit points).

---

## 18. Lazzaro — four keys to emotion

**Source.** Nicole Lazzaro (XEODesign), "Why We Play Games: Four Keys to More Emotion Without Story" (2004), based on observational studies of players.

**Core idea (paraphrased).** Player emotions cluster around four sources of fun:
- **Hard Fun** — meaningful challenge, strategy and mastery; signature emotion is *fiero* (triumph after struggle), with frustration along the way.
- **Easy Fun** — curiosity, exploration, role-play, playful toy-like interaction; emotions include wonder, awe and surprise.
- **Serious Fun** (originally framed around altered states) — play that changes how the player feels or achieves something real: relaxation, excitement, focus, value beyond the game.
- **People Fun** — emotions from interacting with others: amusement, schadenfreude, pride in others' success, belonging.

**Apply it as a design tool.**
1. Map each loop to the key it primarily serves; a game strong in two keys tends to retain more broadly than one strong in a single key.
2. For each key, list the "emotion beat" and the mechanic that produces it.
3. Watch for key conflicts: Hard Fun players resent interruptions; Easy Fun players resent fail states.

| Key | Emotion beat | Mobile mechanic example |
|---|---|---|
| Hard | Fiero after a narrow level win | Last-move victory with celebratory slow-motion |
| Easy | Surprise at an unknown merge result | Silhouetted "?" items in a merge chain |
| Serious | Calm, tidy satisfaction | Sorting/organising puzzles with soft audio |
| People | Laughing with friends | Emotes in PvP; co-op events |

**Limits.** Based on commercial research with limited published methodology; emotions in practice blend; does not specify quantities or tuning.

---

## 19. Bartle's player types

**Source.** Richard Bartle, "Hearts, Clubs, Diamonds, Spades: Players Who Suit MUDs" (*Journal of MUD Research*, 1996); extended in *Designing Virtual Worlds* (2003).

**Core idea.** In multi-user virtual worlds, players' interests sit on two axes: *acting on* vs *interacting with*, and *the world* vs *other players*. The four quadrants: **Achievers** (act on the world: points, levels), **Explorers** (interact with the world: discovery, understanding the system), **Socializers** (interact with players: relationships, conversation), **Killers** (act on players: domination, imposing on others). Bartle argued that the populations interact like an ecosystem: changing the balance of one affects the others.

**Apply it as a design tool (carefully).**
1. For *multiplayer persistent* mobile games only, check each quadrant has a home or is deliberately excluded.
2. Model ecosystem effects: adding unrestricted PvP raids (killers) can drive off socializers and explorers; protection shields and revenge mechanics are ecosystem management.
3. Do not use Bartle to segment single-player mobile audiences; use Quantic Foundry (section 20) or SDT instead.

**Mobile example.** Base-building strategy games serve Achievers (trophies, levels), Killers (raids, leaderboards), Socializers (clans, chat, donations) and, more weakly, Explorers (new troop combinations, base layouts). Shields after being raided are an explicit ecosystem balance mechanism.

**Limits.** Derived from 1990s text MUDs, not validated as a psychometric instrument; players are mixtures, not types; online "Bartle Test" quizzes were created by others and are frequently over-interpreted. Nick Yee's later empirical work found motivation components (achievement, social, immersion) that do not map neatly onto exclusive types.

---

## 20. Quantic Foundry's Gamer Motivation Model

**Source.** Nick Yee and Nicolas Ducheneaut, Quantic Foundry, Gamer Motivation Profile (launched mid-2010s), built from large-sample survey data and factor analysis.

**Core idea.** Twelve motivations grouped into six pairs, which further cluster into three high-level groups:

| Pair | Motivations | Plain meaning |
|---|---|---|
| Action | Destruction, Excitement | Guns, explosions, chaos; fast pace, surprise, thrills |
| Social | Competition, Community | Duels, rankings; being on a team, chatting, grouping |
| Mastery | Challenge, Strategy | Practice, difficult challenges; thinking ahead, decisions |
| Achievement | Completion, Power | Collecting everything, finishing missions; getting powerful gear and characters |
| Immersion | Fantasy, Story | Being someone else, somewhere else; elaborate plots, characters |
| Creativity | Design, Discovery | Expression, customization; exploring, tinkering, experimenting |

The three clusters are roughly Action–Social, Mastery–Achievement and Immersion–Creativity. Quantic Foundry has published analyses of how motivations vary with age, gender and genre preferences — for example, reporting that competition motivation tends to decline with age — consult their published reports for current figures rather than quoting from memory.

**Apply it as a design tool.**
1. Pick the 3–4 motivations your target segment scores highest on; store them in `contract.json` → `meta.target_audience.motivations`.
2. Map each to a loop and a feature; a feature serving none of them needs strong justification.
3. Watch for motivation conflicts: Competition-heavy features can alienate Completion/Design players; Excitement-heavy pacing alienates Strategy players.
4. Use the model to write persona definitions for `arcosian:player-simulator` playtests.

**Mobile example.** A decorate-and-match game for a broad, often older casual audience targets Completion (finish the room), Design (choose décor), Challenge (levels) and Story (light narrative), and deliberately avoids head-to-head Competition, offering soft social comparison instead.

**Limits.** Self-report survey; respondents self-select (skewing toward engaged gamers); motivation is not behaviour (people may say they dislike competition but respond to leaderboards). Combine with telemetry (`player-analytics`).

---

## 21. Self-determination theory and PENS

**Sources.** Edward Deci and Richard Ryan, self-determination theory (*Intrinsic Motivation and Self-Determination in Human Behavior*, 1985, and later work); Richard Ryan, C. Scott Rigby and Andrew Przybylski, "The Motivational Pull of Video Games: A Self-Determination Theory Approach" (*Motivation and Emotion*, 2006); Scott Rigby and Richard Ryan, *Glued to Games* (2011).

**Core idea.** Sustained, high-quality motivation comes from satisfying three basic psychological needs:
- **Competence** — feeling effective and growing in skill.
- **Autonomy** — feeling that actions are self-chosen and meaningful, not coerced.
- **Relatedness** — feeling connected to others.
The **PENS** (Player Experience of Need Satisfaction) model applies this to games, adding measures of presence/immersion and intuitive controls, and links need satisfaction to enjoyment, preference for future play and sustained engagement. A related part of SDT (cognitive evaluation theory) predicts that rewards experienced as *controlling* undermine intrinsic motivation, while rewards experienced as *informational* (feedback on competence) can support it — see the overjustification section in `fun-and-motivation-design.md`.

**Apply it as a design tool: the need-satisfaction audit.**

| Need | Supported by | Thwarted by | Mobile checks |
|---|---|---|---|
| Competence | Clear feedback, fair difficulty, visible mastery | Opaque failure, pay-to-win walls, random losses | Can players explain why they lost? |
| Autonomy | Meaningful choices, multiple paths, opt-in goals | Forced tutorials, nagging popups, FOMO pressure, mandatory ads | Can a player ignore events without being punished? |
| Relatedness | Co-op, gifting, guild goals, shared moments | Toxic chat, solitary play only, exploitative referral spam | Is there a positive reason to involve friends? |

**Mobile example.** Pokémon GO's community raid events support relatedness (physical co-play), competence (catching rare Pokémon) and autonomy (choose when and where to play). Aggressive limited-time pressure in other games often scores high on short-term engagement but low on autonomy.

**Limits.** Needs are broad and can be "satisfied" in shallow ways; PENS is a measurement instrument for research and testing, not a generator; self-report again.

---

## 22. Hodent — game UX and the gamer's brain

**Source.** Celia Hodent, *The Gamer's Brain: How Neuroscience and UX Can Impact Video Game Design* (CRC Press, 2017) and *The Psychology of Video Games* (2020). Hodent previously led UX at Epic Games, including on Fortnite.

**Core idea (paraphrased).** Players' experience is filtered by the brain's limits in **perception** (what we see is interpreted, not recorded), **attention** (scarce, easily overloaded, selective) and **memory** (working memory holds little; long-term memory needs repetition and meaning). Good game UX therefore has two pillars:
- **Usability** — can players perceive, understand and operate the game? Principles include clear signs and feedback, clarity, form that communicates function, consistency, minimal cognitive and physical workload, error prevention and recovery, and flexibility.
- **Engage-ability** — does the game sustain motivation (intrinsic and extrinsic, competence, autonomy, relatedness), produce emotion (feel, presence, surprise), and maintain game flow (difficulty and learning curves, pacing)?
Testing with real players, observing rather than asking, is central.

**Apply it as a design tool.**
1. Per screen: list what the player must perceive, attend to and remember; cut anything beyond what is needed for the next decision.
2. Teach by doing, in context, one concept at a time; space repetitions over sessions rather than front-loading text.
3. Run a usability test with 5–8 target players per round; record where they hesitate, misread or tap wrong; fix and repeat.
4. Separate usability findings (fix always) from engage-ability findings (fix if they conflict with pillars).

**Mobile example.** On small screens, attention is the binding constraint: a HUD showing six currencies, three timers and a battle pass meter during play competes with the board itself. Hodent-style analysis moves everything not needed for the current move off the play screen.

**Limits.** More an evaluation discipline than a source of game ideas; cognitive-science findings are averages, and individual and cultural differences matter (see `accessibility-localization`).

---

## 23. Bonus tools

### Doug Church — formal abstract design tools (1999)
Church's *Game Developer* article "Formal Abstract Design Tools" called for a shared design vocabulary and offered examples such as **intention** (players can form their own plans), **perceivable consequence** (the game reacts clearly to what the player did) and **story** (the narrative thread, designer-driven or player-driven). Use: when a mechanic feels random, check perceivable consequence; when players feel railroaded, check intention.

### Schell's elemental tetrad
Schell divides a game into **mechanics, story, aesthetics** (the look, sound and feel) and **technology**, arranged so that aesthetics are most visible to players and technology least. Use: in a design review, check that all four elements reinforce the same theme and experience; a mismatch (e.g., a cosy story with a punishing, grindy mechanic) shows up as player confusion about what the game is.

---

## 24. Running several frameworks together: one worked pass

**Concept:** "A one-thumb cosy fishing game for commuters: cast, reel, collect fish for an aquarium, decorate it, visit friends' aquariums."

| Step | Framework | Finding | Design response |
|---|---|---|---|
| 1 | MDA / LeBlanc | Top aesthetics: Submission, Discovery, Expression | Keep Challenge low; rare fish are about discovery not difficulty |
| 2 | Quantic Foundry | Target: Completion, Design, Discovery; low Competition | No PvP; friend visits instead of leaderboards |
| 3 | Caillois | Alea (which fish bites) + light agon (reel timing) + mimicry (angler fantasy) | Make luck transparent: show fish odds per location |
| 4 | Cook skill atoms | Atoms: cast distance, reel tension, bait choice, location reading | Teach cast and reel in session 1; bait and location in sessions 2–3 |
| 5 | Meier | Bait choice is the main decision; is it interesting? | Make bait trade rarity vs bite speed vs cost |
| 6 | Koster | Mastery horizon of reeling is short (~1–2 sessions) | Add fish behaviours (darting, diving) as new patterns per region |
| 7 | Swink | Reel feel is the core sensation | Haptic pulse on bite; rod bend; line tension sound rising in pitch |
| 8 | Adams & Dormans | Coins → bait → fish → coins converter loop could run away | Cap aquarium income per day; decorations as sinks |
| 9 | Huizinga | Sessions end at the next stop | Every cast is self-contained (≤ 30 s); auto-save after each catch |
| 10 | SDT | Relatedness weak | Gift a duplicate fish to a friend; joint aquarium goals |
| 11 | Hodent | HUD clutter risk | Play screen shows only rod, water, tension meter |

Result: a contract draft with pillars ("cosy discovery", "one-thumb anywhere", "my aquarium, my style"), a core loop, and three prototype questions (is reeling satisfying for 30 s? does bait choice create a decision? do players care about decorating?).

---

## 25. Sources and further reading

All works below are summarised in this file in my own words; consult the originals for full arguments.

- Hunicke, LeBlanc, Zubek (2004), "MDA: A Formal Approach to Game Design and Game Research".
- Walk, Görlich, Barrett (2017), "Design, Dynamics, Experience (DDE)", in *Game Dynamics*, Springer.
- Caillois (1958/1961), *Man, Play and Games*.
- Huizinga (1938), *Homo Ludens*. Consalvo (2009), "There is No Magic Circle".
- Salen & Zimmerman (2003), *Rules of Play*.
- Juul (2002) "The Open and the Closed"; (2005) *Half-Real*; (2010) *A Casual Revolution*; (2013) *The Art of Failure*.
- Koster (2004/2013), *A Theory of Fun for Game Design*.
- Schell (2008/2014/2019), *The Art of Game Design: A Book of Lenses*.
- Fullerton (2004–2018), *Game Design Workshop*.
- Adams & Dormans (2012), *Game Mechanics: Advanced Game Design*.
- Sylvester (2013), *Designing Games*.
- Swink (2008), *Game Feel*.
- Cook (2007) "The Chemistry of Game Design"; (2012) "Loops and Arcs" (Lost Garden).
- Meier (2012), "Interesting Decisions", GDC talk.
- Csikszentmihalyi (1990), *Flow*; Chen (2006 thesis; 2007 CACM), "Flow in Games".
- Lazzaro (2004), "Why We Play Games: Four Keys to More Emotion Without Story".
- Bartle (1996), "Hearts, Clubs, Diamonds, Spades"; (2003) *Designing Virtual Worlds*.
- Yee & Ducheneaut, Quantic Foundry Gamer Motivation Model (quanticfoundry.com).
- Deci & Ryan (1985); Ryan, Rigby, Przybylski (2006); Rigby & Ryan (2011), *Glued to Games*.
- Hodent (2017), *The Gamer's Brain*; (2020) *The Psychology of Video Games*.
- Church (1999), "Formal Abstract Design Tools", *Game Developer*.
