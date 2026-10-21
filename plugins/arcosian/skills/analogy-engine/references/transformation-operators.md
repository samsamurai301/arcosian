# Transformation Operators: A Grammar for Generating Designs from Existing Ones

This file is the studio's catalogue of transformation operators: repeatable moves that turn an existing game, genre or system into a new design. It opens with SCAMPER adapted for games (7 operators), then gives 32 named operators (OP01–OP32), each with its move, a step-by-step procedure, real examples, risks and the ontology fields it changes. It closes with selection matrices (which operator for which goal), compatibility rules for stacking operators, and a worksheet. Operators are applied **after** the abstraction step in `references/analogy-method.md`: transform relations and loops, not screenshots. The default stacking rule is one or two operators per concept, which keeps the concept inside the genre's expectation budget (`genre-playbooks` Core model 2).

## Contents

1. How to use operators
2. SCAMPER for games (S, C, A, M, P, E, R)
3. Structural operators OP01–OP08 (transplant, theme, inversion, perspective, scale, time, fusion, subtraction)
4. Market operators OP09–OP11 (audience, platform, social)
5. Mechanical and economic operators OP12–OP16 (verb, economy, meta graft, roguelite, idle)
6. Shape operators OP17–OP24 (session, stakes, information, randomness, co-op/competitive, asymmetry, ritual, real-world)
7. Production operators OP25–OP32 (automation, mode extraction, creation, generator, collection, narrative, merge, puzzle)
8. Selection matrix: operator by goal
9. Stacking and compatibility rules
10. Operator worksheet and ontology delta summary

---

## 1. How to use operators

1. **Abstract first.** Write the source as verbs, mechanics, loops, flows and aesthetics (`references/analogy-method.md` section 7).
2. **Pick by goal.** Use the matrix in section 8 (lower CPI, deeper retention, novelty, cheaper production, a new audience).
3. **Apply one operator; check the loop still closes.** Every operator must leave a core loop that can be written as act → reward → invest in one sentence.
4. **Apply at most one more.** A second operator should touch a different layer (core vs meta vs wrapper).
5. **Name the emergent structure.** If the result has nothing that neither the source nor the operator implies, it is a re-skin, not a design.
6. **Score.** Run the AFS for any borrowed relation and the concept rubric (`references/concept-generation-playbook.md` step 6).

Operator notation used in concept cards: `chassis ⊕ OPxx [⊕ OPyy]`, for example `Coin Master loop ⊕ OP02 (Monopoly IP) ⊕ OP13 (dice economy)`.

---

## 2. SCAMPER for games

SCAMPER is Bob Eberle's 1971 mnemonic, built on Alex Osborn's idea-spurring questions (*Applied Imagination*, 1953). Below, each letter is restated as a game-design operator with prompts aimed at the ontology layers. Use it as a fast divergent pass (10 minutes per letter) before the named operators.

| Letter | Game operator | Prompts (apply to verbs, rules, loops, flows, wrapper) | Example |
|---|---|---|---|
| **S** Substitute | Replace one element with another of the same role | Another verb with the same goal? Another resource as the gate? Another chance device (dice for slot)? Another opponent (time, self, ghost, friend)? | Dice replace slot spins as the energy-to-outcome device (Coin Master → Monopoly Go!) |
| **C** Combine | Merge two elements, loops or genres | Which two loops share an output? Which two verbs could be one gesture? Which genre's meta consumes this core's output? | Tower defense + card collection + lanes (Clash Royale) |
| **A** Adapt | Take a solution from elsewhere and fit it | What other game or domain already solved this player problem? | Saga map adapted from earlier King titles into match-3 (Candy Crush Saga) |
| **M** Modify / Magnify / Minify | Change a parameter radically | 10× enemies? 1/10 the deck size? A 30-second match? A board of 4×4? | Hundreds of enemies (Vampire Survivors); 12-card decks (Marvel Snap) |
| **P** Put to other use | Use a mechanic, asset or mode for another purpose | Could the tutorial be the game? Could an ad mini-game be a mode? Could leaderboards teach? | Location data from one game reused as the map of another (Ingress portals → Pokémon GO stops) |
| **E** Eliminate | Remove a rule, step or system | What happens with no aiming, no timer, no fail state, no energy, no text? | No gravity and no timer (Tetris → 1010!) |
| **R** Reverse / Rearrange | Invert roles, order or direction | Play the other side? Reward before effort? Build then defend vs defend then build? Turn order inverted? | Player is the disease (Plague Inc.) |

**Output of a SCAMPER pass**: 14–21 raw variants (2–3 per letter). Keep the 3–5 that change a **relation** and pass the one-sentence loop test; send them through the named operators below for procedure and risks.

---

## 3. Structural operators

### OP01 Mechanic transplant
**Move.** Lift one mechanic (a rule system with its relations) from a source game into a target chassis where the same player need exists.
**Procedure.**
1. Climb the source mechanic to relation level (`analogy-method.md` section 6). State its essential relations and the support it needs.
2. Confirm the target has the player need the mechanic serves (MDA aesthetic or motivation).
3. Map roles one-to-one; list missing support (discrete attempts, a sink, hidden information, a stake).
4. Build or substitute the missing support; compute AFS (≥ 70 to proceed).
5. Re-tune parameters in the target's units; simulate if the mechanic touches the economy.
**Examples.** Poker's raise-and-fold into a CCG as snap and retreat (Marvel Snap). Poker hand rankings as the scoring rule of a roguelite deck-builder (Balatro). Album-style set collection into a dice-and-board loop (Monopoly Go! sticker albums, after Coin Master's card sets).
**Risks.** Cargo cult (feature without support); added cognitive load in the FTUE; balance shock when the mechanic multiplies an existing reward.
**Ontology delta.** New `contract.mechanics[]` entry with `references` in its mechanic card; possibly a new `economy.currencies[]`; new loop step.

### OP02 Theme swap
**Move.** Keep the rules and loops; change the fiction, art and audio, and adjust only what the new theme demands.
**Procedure.**
1. List every rule and check whether the new theme *explains* it (theme–mechanic resonance). Rules the theme cannot explain become friction.
2. Change goal names, obstacle names and feedback to fit the theme; re-tune only where the fiction changes expectations (a farm theme suggests growth over time).
3. Check audience fit: the theme changes who clicks the ad (`marketing-ua`).
4. Check legal distance: mechanics are generally not protected, but close copying of trade dress and art can be (`legal-ethics`).
**Examples.** Candy Crush chassis in a farm world with collection goals (Farm Heroes Saga, King). Coin Master's loop re-themed with the Monopoly IP (Monopoly Go!). Rotating city themes as a live-ops device (Subway Surfers World Tour). IP re-themes of a hit chassis (Angry Birds Star Wars, Rovio, 2012).
**Risks.** No differentiation in a consolidated genre; IP whose relations do not match the loop (see the location-AR failures in `references/worked-analogies.md`); art cost rises with theme complexity.
**Ontology delta.** `art_direction`, `audio_direction`, `meta.title`, `meta.logline`, `player_fantasy`; ideally nothing in `mechanics` (if mechanics change, it is a different operator).

### OP03 Constraint inversion
**Move.** Remove or invert a constraint that the genre treats as sacred, and find the new decision that fills the gap.
**Procedure.**
1. List the genre's sacred constraints: aiming, shooting, timer, gravity, fail state, energy, turn order, fog of war, inventory limit, permadeath, free movement.
2. Remove or invert one. Ask: what decision did that constraint create, and what replaces it?
3. If nothing replaces it, add one decision elsewhere (a draft, positioning, planning).
4. Prototype the toy version (verb only) to test that the inverted constraint feels good.
**Examples.** Remove aiming and shooting from a shooter so that only movement and level-up drafts remain (Vampire Survivors). Remove shooting while moving: stop to fire, move to dodge (Archero). Remove gravity and the timer from falling blocks; clear rows and columns (Tetris → 1010!). Remove fail pressure and keep perception puzzles (Monument Valley). Time moves only when the player moves (Superhot, 2016, PC).
**Risks.** Removing the constraint removes the skill expression; players of the source genre reject it ("not a real shooter"). Mitigate by moving skill to a new place and marketing to a different segment.
**Ontology delta.** `verbs[]`, `mechanics[].rules`, `ux.hud`; often `meta.session_length_target_sec`.

### OP04 Perspective flip
**Move.** Play the other side of a known conflict or system: the attacker instead of the defender, the disease instead of the doctor, the nuisance instead of the hero.
**Procedure.**
1. Identify the actors in the source system and their goals.
2. Choose the actor whose goals are least explored; list what they control and what they suffer.
3. Rebuild the core loop around that actor's verbs; keep the source's world rules so players' knowledge transfers (blending's "web" principle).
4. Check fantasy and ethics: the flipped role must be fun to inhabit and acceptable for the audience.
**Examples.** Play the pathogen in an epidemiology simulation (Plague Inc., Ndemic Creations, 2012). Tower offense instead of tower defense (Anomaly: Warzone Earth, 11 bit studios, 2011). Be the dungeon lord defending against heroes (Dungeon Keeper, Bullfrog, 1997). Be the nuisance goose (Untitled Goose Game, House House, 2019). The impostor role in social deduction (Among Us).
**Risks.** The flipped side may have fewer interesting decisions; the novelty wears off once the joke is understood; tone and taste issues.
**Ontology delta.** `player_fantasy`, `verbs[]`, `loops[]`; sometimes `legal-ethics` review of themes.

### OP05 Scale shift
**Move.** Move the play to a radically different scale (microscopic ↔ cosmic, one unit ↔ thousands), or let scale change during play.
**Procedure.**
1. Pick the scale axis: physical size, number of entities, time span, organisational level (cell → organism → species → planet).
2. Decide whether the scale is fixed (different but static) or progressive (growth is the loop).
3. For progressive scale, design the camera, the readability and the performance budget at each step; this is where most scale-shift projects fail on phones.
4. Map progression tracks to scale steps (`progression.tracks[]`).
**Examples.** Growing from tiny to enormous as the core fantasy (Katamari Damacy, Namco, 2004; Hole.io, Voodoo, 2018). From cell to galaxy across stages (Spore, Maxis, 2008). Hundreds of enemies instead of a few (Vampire Survivors, a magnify move).
**Risks.** Entity counts break low-end performance budgets (`mobile-performance`); camera zoom makes touch targets unreadable; each scale stage costs content.
**Ontology delta.** `progression.tracks[]`, `technical.perf_budgets`, `content`.

### OP06 Time shift
**Move.** Convert real-time play to turn-based, turn-based to real-time, or to a hybrid (time moves when you act; time synced to music; active time bars).
**Procedure.**
1. Identify where the source's skill lives: reaction (real-time) or planning (turn-based).
2. Decide which skill the target segment prefers and which the platform supports (touch latency penalises precise real-time input; see `game-feel`).
3. Real-time → turn-based: telegraph enemy intent, add undo or preview, make outcomes deterministic.
4. Turn-based → real-time: add a regenerating resource as the pacing device (elixir, mana over time), shorten decision options to 2–4.
5. Hybrids: tie time to input, beat or a meter.
**Examples.** A turn-based tactics game with fully telegraphed enemy moves, so play is a perfect-information puzzle (Into the Breach, Subset Games, 2018). A turn-based CCG structure made real-time with a regenerating elixir resource (Hearthstone-style cards → Clash Royale's deployment). A roguelike made real-time to the beat (Crypt of the NecroDancer, Brace Yourself Games, 2015). Time moves when you move (Superhot).
**Risks.** Real-time increases agent-build risk (lower timing tolerance, factor T in `genre-playbooks` Core model 7); turn-based can feel slow in short sessions unless turns are fast.
**Ontology delta.** `mechanics[]`, `progression.difficulty`, `technical.deterministic`, `multiplayer`.

### OP07 Genre fusion
**Move.** Combine two genres so that one owns the core verb and the other supplies the meta, wrapper or a clearly separate mode.
**Procedure.** Follow the eight fusion rules in `genre-playbooks` procedure C (one genre owns the core verb, bridge currency, bounded power bridge, session alignment, cognitive-load alternation, audience overlap, FTUE order, one art direction). Then:
1. Write the bridge: which core output does the second genre consume?
2. Write the emergent sentence: what is true only in the fusion?
3. Run the fusion red flags (meta lets players skip the core; different orientation; separate currencies; best players differ).
**Examples.** Tower defense + CCG + lanes (Clash Royale, Supercell, 2016). Match-3 + monster-team RPG + gacha (Puzzle & Dragons, GungHo, 2012). Poker scoring + roguelite deck-building (Balatro, 2024). Match-3 + renovation story (Homescapes, Playrix, 2017). Merge + tower defense (Random Dice, Rush Royale).
**Risks.** Collage (two cores); doubled FTUE; audiences that do not overlap; doubled content cost.
**Ontology delta.** `meta.genre`/`subgenre`, `loops[]` (new meta or mode loop), `economy.currencies[]` (bridge).

### OP08 Subtraction (midcore → casual)
**Move.** Remove systems from a deep genre until the core experience fits casual sessions and a single thumb, keeping the moments players remember.
**Procedure.**
1. List every system in the source with its cognitive cost and its contribution to the target aesthetic.
2. Mark the "remembered moments" (highlight clips, community stories). Protect the systems that produce them.
3. Remove or automate the rest in order of cost-to-value; replace removed depth with a light meta.
4. Cap the FTUE complexity budget (one new concept per step).
5. Test that experienced source players still recognise the fantasy (unpacking test).
**Examples.** Magic → Hearthstone: no land cards (mana grows automatically), little interaction on the opponent's turn. Hearthstone → Marvel Snap: 12-card decks, 6 turns, about 3-minute games. MOBA → Brawl Stars and Clash Royale: no last-hitting or item builds, short matches. Pokémon TCG → Pokémon TCG Pocket (2024): 20-card decks and a 3-point win instead of 60-card decks and 6 prize cards.
**Risks.** Removing the system that created depth (solved metas, low mastery horizon); veterans dismiss it; casuals still find it too complex.
**Ontology delta.** Fewer `mechanics[]`; `ftue.steps[]`; `meta.session_length_target_sec`; `scope.wont` (record what was cut).

---

## 4. Market operators

### OP09 Audience shift
**Move.** Re-aim a proven structure at a different segment (age, gender, region, gamer vs non-gamer, motivation profile), changing tone, difficulty, session and monetization to match.
**Procedure.**
1. Define the new segment and its top two motivations (Quantic Foundry model, see `genre-playbooks` procedure A).
2. List the source's assumptions about players (skill, reading, time, spend, social habits) and invert those that do not hold.
3. Change entry points: where the segment already spends attention (newspaper habit, fitness routine, learning goal).
4. Adjust monetization ethics for the segment (minors, older players, non-gamers).
**Examples.** A Mastermind-style deduction puzzle aimed at newspaper readers as a daily habit (Wordle). Game structures aimed at language learners (Duolingo streaks and leagues). Collection play aimed at walkers and families via location (Pokémon GO). Solitaire players brought into a farming economy (Solitaire Grand Harvest; see `genre-playbooks` pairings).
**Risks.** The new segment has no habit of installing games; the old segment dislikes the changes; UA targeting for non-gamers is expensive.
**Ontology delta.** `meta.target_audience`, `ux.accessibility`, `monetization.ethics`, `analytics.kpi_targets`.

### OP10 Platform translation (PC/console → mobile)
**Move.** Re-engineer a design proven on PC or console for phones: portrait one-thumb play where possible, short sessions, interruptions, low-end devices, free-to-play economics.
**Procedure (checklist).**

| Axis | Source assumption | Mobile translation |
|---|---|---|
| Orientation | Landscape | Portrait unless two-stick control is essential |
| Input | Mouse aim, keyboard, two sticks | One thumb in the bottom 40% of the screen; auto-aim; tap, drag, swipe |
| Session | 30–90 minutes | 1–5 minute units with natural stops; runs ≤ 10–15 minutes |
| Interruptions | Rare | Autosave each action; pause on focus loss; resume in one tap |
| Devices | Mid/high GPUs | Low-end Android tier caps (entities, particles, memory) |
| Business model | Premium | Premium port, or F2P with a meta graft (OP14) and a defined spend moment |
| Readability | 24-inch screen | 6-inch screen; silhouettes, contrast, larger hit areas |
| Text | Long tooltips | Icons, numbers, one-line labels |

**Examples.** Vampire Survivors rules in portrait with an Archero-style gear meta (Survivor.io, Habby, 2022). Battle royale cut to 50 players and about 10-minute matches for low-end phones (Free Fire, Garena, 2017). The Fall Guys format released on phones first by a different studio (Stumble Guys). Brawl Stars switched from portrait to landscape during soft launch (reported), a reminder that orientation is decided by the control scheme, not by habit.
**Risks.** Losing the feel that made the source special; a monetization graft that turns a premium joy into a grind; performance collapse in entity-heavy genres.
**Ontology delta.** `meta.orientation`, `verbs[].input`, `technical.perf_budgets`, `technical.min_spec`, `meta.monetization_model`.

### OP11 Social-layer addition
**Move.** Add other people to a solo structure: teams, gifting, async competition, sharing, trading, co-op events.
**Procedure.**
1. Choose the social relation: cooperation (help, gift, donate), competition (leaderboard, league, raid), expression (share, show off), exchange (trade).
2. Make the social action feed the core loop's economy (lives gifting refills attempts; troop donation adds power).
3. Provide a solo fallback; never make progress depend on recruiting friends.
4. Size the backend need (async leaderboards are cheap; real-time is expensive, `multiplayer-backend`).
5. Moderate any free text; prefer emotes and preset messages for broad or young audiences.
**Examples.** Teams and team chests added to a collapse puzzle (Toy Blast → Toon Blast). Friends' faces on the saga map and lives gifting (Candy Crush Saga). Clans with troop donation (Clash of Clans). A roadside shop where players buy each other's goods (Hay Day). A spoiler-free share grid (Wordle). Weekly leagues with promotion and demotion (Duolingo).
**Risks.** Obligation fatigue; toxic interactions; empty social spaces in small launches (seed with bots honestly labelled, or design for small groups).
**Ontology delta.** New `loops[]` of `type: social`; `technical.backend`; `analytics` events in category `social`.

---

## 5. Mechanical and economic operators

### OP12 Verb swap
**Move.** Keep the board, goals and meta; replace the primary input verb with another gesture that creates a different skill.
**Procedure.**
1. Write the current verb and the decision it creates.
2. List alternative gestures with their natural decision: tap (selection), swipe (direction), drag (path or placement), hold (charge, timing), pour (sequencing), pull-and-release (trajectory), draw (route).
3. Re-check the board rules: some rules only make sense with the old verb.
4. Re-tune difficulty with bots (`match3_sim.py`, `puzzle_solver.py`).
**Examples.** Swap to tap-a-group (Toy Blast, collapse lineage). Swap to connect a line of same-coloured dots (Two Dots). Swap to free-drag an orb across the board for a few seconds (Puzzle & Dragons). Draw paths for aircraft (Flight Control, Firemint, 2009). Pull and release a slingshot (Angry Birds).
**Risks.** The new verb may be less satisfying on touch (precision drags); difficulty models no longer apply.
**Ontology delta.** `verbs[]`, `mechanics[].rules`, `level-spec.schema.json` difficulty knobs.

### OP13 Economy re-skin
**Move.** Keep the topology of a proven economy (sources, sinks, converters, gates, pools) and rename and re-parameterise it to fit a new fiction or chance device.
**Procedure.**
1. Draw the source economy as an `economy-model.schema.json` graph.
2. Keep the topology; map each node to a target node with the same role (energy gate, chance converter, build sink).
3. Re-parameterise: earn rates, caps, regeneration, prices.
4. Simulate with `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/economy_sim.py --model PATH --runs 200 --seed 1` and compare hoard days and days-to-content against the source.
5. Audit every chance converter that touches purchasable currency for odds disclosure and minors (`legal-ethics`).
**Examples.** Slot spins → dice rolls; villages → board landmarks; card sets → sticker albums (Coin Master → Monopoly Go!). Withering crops removed and production chains with order boards added (FarmVille → Hay Day, commonly noted). Score as chips × mult (Balatro), which turns a poker hand into an economy of multipliers.
**Risks.** Copying an aggressive economy also copies its ethical problems; re-parameterising without simulation breaks pacing.
**Ontology delta.** `economy.currencies[]`, `economy.model_ref`, economy model nodes.

### OP14 Meta-layer graft
**Move.** Attach a slower progression loop (renovation, base, collection, gear, story) to a fast core so that every core session moves a long-term goal.
**Procedure.**
1. Choose the meta that serves the segment's second motivation (completion, design, power, story).
2. Define the bridge currency: one core output is the meta's main input.
3. Bound the power bridge: meta power may shift bot win rate by at most 10–15 points (`genre-playbooks` fusion rule 3).
4. Fit the meta action inside the core session (30–60 seconds after a 2–3 minute level).
5. Reveal the meta in the first session, before the first fail.
**Examples.** Renovation on match-3 (Gardenscapes, Homescapes, Royal Match). Archero-style gear and chapters on a survivor-like core (Survivor.io). Story and orders on merge-2 (Merge Mansion). A farm meta on solitaire (Solitaire Grand Harvest). A 4X wrapper on an action mini-game front end (Last War: Survival, widely discussed; verify the current build).
**Risks.** Meta that lets players skip the core; meta art cost; disconnected meta (no anchor back to the core).
**Ontology delta.** New `loops[]` (`type: meta`), `economy.currencies[]` (bridge), `progression.tracks[]`, `content`.

### OP15 Roguelite-ification
**Move.** Wrap a ruleset in runs: escalating targets, drafted upgrades between encounters, a run end, and (optionally) light permanent progression.
**Procedure.**
1. Define the run: length (mobile: 5–15 minutes or interruptible), number of encounters, escalation curve (antes, floors, waves).
2. Define drafts: after each encounter offer 3 options (mobile default); build-defining items are rarer.
3. Define synergies: at least 3 build archetypes so runs differ.
4. Decide permanent progression: none (pure skill), unlocks (variety), or power (meta). Power meta must be bounded.
5. Seed runs for reproducibility; add a daily seed (OP23).
**Examples.** Poker hands with jokers and escalating blinds (Balatro). Deck-building with a branching map (Slay the Spire, Mega Crit; Dominion-style deck-building plus roguelike runs). Pachinko-style aiming with relics, widely described as "Peggle meets Slay the Spire" (Peglin, Red Nexus Games). Slot-machine deck-building (Luck be a Landlord). Dice-allocation combat (Dicey Dungeons, Terry Cavanagh, 2019).
**Risks.** Runs too long for phones; one dominant build; permanent power undermining skill; heavy content needs for synergy variety.
**Ontology delta.** `loops[]` (run loop, `period: session`), `mechanics[]` (draft, relics), `progression.tracks[]`, `technical.deterministic: true` for seeds.

### OP16 Idle-ification
**Move.** Automate a core output so that it accumulates over time and while away; the player's decisions move to investment, upgrades and prestige.
**Procedure.**
1. Identify the core output (coins, ore, research) and the manual verb that produced it.
2. Add automation (managers, workers, drones) purchased with that output.
3. Add offline earnings with a cap (e.g. 2–8 hours) and a return moment.
4. Use exponential cost growth versus multiplicative income boosts; plan the prestige reset with a permanent multiplier.
5. Check with `progression_calc.py` and `economy_sim.py`; format big numbers readably.
**Examples.** Clicking automated by managers, with angel investors as the prestige currency (AdVenture Capitalist, Hyper Hippo, 2014, after the incremental genre popularised by Cookie Clicker, 2013). Evolution as an idle progression (Cell to Singularity). An MMO skilling loop made idle (Melvor Idle, widely described as RuneScape-inspired).
**Risks.** Hollow engagement ("number goes up") without decisions; a prestige wall too early; reliance on rewarded ads for multipliers.
**Ontology delta.** Economy nodes with `trigger: per_minute`; `progression.tracks[]` (prestige); `loops[]` (`period: daily`).

---

## 6. Shape operators

### OP17 Session compression
**Move.** Cut a long session format to a short, fixed one while keeping its peak moments.
**Procedure.**
1. Measure the source session and mark its peaks (fights, reveals, comebacks) and its dead time (travel, setup, waiting, menus).
2. Cut dead time first: smaller maps, instant spawn, pre-built decks, auto-travel.
3. Fix the length (a timer or a turn cap) and add an endgame accelerator (sudden death, double resource, shrinking zone).
4. Re-tune comeback mechanics: short matches need fewer, sharper swings.
5. Target 2–4 minutes for mobile PvP matches and 1–3 minutes for puzzle levels (`game-case-studies` mobile specifics).
**Examples.** MOBA lanes and towers in a 3-minute match with overtime (Clash Royale). Hero-shooter modes in roughly 2–3-minute rounds (Brawl Stars). A CCG in 6 turns (Marvel Snap). Battle royale with 50 players and about 10-minute matches (Free Fire).
**Risks.** Loss of strategic depth and comeback arcs; matches decided by the opening; less room for social bonding.
**Ontology delta.** `meta.session_length_target_sec`, `loops[].period`, `mechanics[].parameters` (timers, caps).

### OP18 Stakes injection (wager layer)
**Move.** Add an optional, public escalation of what a match or attempt is worth, with an exit at the current stake.
**Procedure.**
1. Confirm the target has uncertainty that resolves over time and some hidden or private information (otherwise there is nothing to bet on).
2. Choose the stake currency: rank points, trophies, event points. **Never** paid currency on a chance outcome, and nothing at stake for minors that could resemble gambling (`legal-ethics`).
3. Define raise rules (who may raise, how often, multiplier) and exit rules (concede at current stake).
4. Simulate expected value per decision so raising is neither always right nor always wrong (`decision_math.py ev`).
**Examples.** Snap and retreat (Marvel Snap). The doubling cube (backgammon). Raise and fold (poker). Roll multipliers that scale both cost and reward (Monopoly Go!; note the spending-acceleration risk).
**Risks.** Gambling resemblance and regulation; tilt; the stake system dominating the game.
**Ontology delta.** `mechanics[]` (raise, concede), `progression.tracks[]` (rank), `monetization.ethics` rule.

### OP19 Information shift
**Move.** Change who knows what: reveal hidden information (telegraphs, intents, open hands) or hide open information (fog, hidden roles, hidden layers).
**Procedure.**
1. Map the information state: what each player knows at each decision.
2. To deepen planning, reveal (show enemy intent, the next pieces, the deck order).
3. To create tension, deduction or bluffing, hide (fog of war, face-down cards, hidden layers in sort puzzles).
4. Re-balance: revealed information demands harder puzzles; hidden information demands fair odds and readable inference.
**Examples.** Enemy moves fully telegraphed (Into the Breach). Enemy intents shown above their heads (Slay the Spire). You see everyone's cards except your own (Hanabi, Antoine Bauza, 2010). Locations revealed one per turn (Marvel Snap). Hidden layers in sort puzzles (Magic Sort!, see `game-case-studies`).
**Risks.** Too much information produces analysis paralysis; too little produces luck-driven outcomes and blame.
**Ontology delta.** `mechanics[].rules`, `ux.hud`, level-spec knobs.

### OP20 Randomness relocation
**Move.** Move randomness from output (after the decision) to input (before it), make outcomes deterministic, or add bounded randomness where play is solved.
**Procedure.**
1. List every random element and whether it is input or output randomness (design-theory Core model 8).
2. Move high-stakes output randomness to input (random draws, random offers, then deterministic resolution).
3. Bound remaining randomness: bags (shuffle without replacement), pity, pseudo-random distribution.
4. If play is solved and stale, add input randomness (random modifiers, daily rules).
**Examples.** Deterministic combat with random enemy spawns as the input (Into the Breach). A three-piece random tray with deterministic placement (1010!, Block Blast!). The "bag" randomiser in modern Tetris, which deals each of the seven pieces once per bag. Digital-only random card effects that physical CCGs cannot do easily (Hearthstone), an *addition* of output randomness for spectacle.
**Risks.** Determinism makes content solvable and shareable (spoilers); randomness without bounds makes losses feel unfair.
**Ontology delta.** `mechanics[].rules`, `technical.deterministic`, level-spec `solver`.

### OP21 Co-op ↔ competitive flip
**Move.** Turn a competitive structure cooperative (players versus the system) or a cooperative one competitive.
**Procedure.**
1. Identify the conflict's source: other players or the system.
2. For co-op: replace the opponent with a system adversary that escalates; add limited communication so cooperation is a puzzle, not one player directing.
3. For competitive: split shared goals into zero-sum or race goals; add interaction (blocking, stealing).
4. Check for quarterbacking (one expert plays for everyone) and kingmaking.
**Examples.** Trick-taking made cooperative with communication limits (The Crew, Thomas Sing, 2019). Cooperative board play against an escalating outbreak (Pandemic, Matt Leacock, 2008). Team events and team chests in solo puzzle games (Toon Blast, Royal Match). 2v2 modes in a 1v1 game (Clash Royale).
**Risks.** Co-op needs matchmaking or friends; competition drives away casual segments.
**Ontology delta.** `loops[]` (`type: social`), `technical.multiplayer`, `analytics` social events.

### OP22 Asymmetry injection
**Move.** Give players different roles, powers or information so that the same match contains different games.
**Procedure.**
1. Define roles by verbs and goals (hunter/hunted, impostor/crew, builder/raider).
2. Balance by win rate per role, not by symmetry; target 45–55% per role over large samples.
3. Give the minority role a strong fantasy and the majority role cooperative tools.
4. Plan the matchmaking cost (role queues).
**Examples.** Impostors versus crew (Among Us). One killer versus four survivors (Dead by Daylight, Behaviour Interactive, 2016). Asymmetric factions with different rules (Root, Cole Wehrle, 2018). Hidden roles in Mafia and Werewolf.
**Risks.** Balance is hard and slow to tune; queue times; one role becomes unpopular.
**Ontology delta.** `mechanics[]` per role, `technical.multiplayer`, `analytics` per-role win rates.

### OP23 Ritualization (daily-ification)
**Move.** Turn play into a once-a-day ritual: one shared puzzle, one free pack, one challenge, the same for everyone, with a shareable result.
**Procedure.**
1. Choose the daily unit (a puzzle, a seed, a draw) and make it identical for all players that day (deterministic seed).
2. Limit it (one per day) so scarcity creates anticipation and conversation.
3. Make the result shareable without spoilers.
4. Add a streak with a forgiving rule (a freeze, a grace day), never a punitive one.
5. Keep an archive or practice mode for players who want more, if the business model allows.
**Examples.** One word puzzle per day with a spoiler-free emoji grid (Wordle). Daily puzzle families from newspapers (for example NYT Connections, 2023). Daily seeded challenge runs (Spelunky's daily challenge). Free daily card packs (Pokémon TCG Pocket). Streaks as a habit device (Duolingo).
**Risks.** Low session counts limit ad revenue; streak pressure can become anxiety; one bad daily puzzle hurts everyone at once.
**Ontology delta.** `loops[]` (`period: daily`), `liveops.cadence`, `content.levels.generation`.

### OP24 Real-world anchoring
**Move.** Tie the game to a real-world signal: location, steps, sleep, time of day, weather, learning progress.
**Procedure.**
1. Choose the signal and the habit it supports (walking, sleeping, studying).
2. Map the signal to a game input or resource without making progress impossible for people who cannot produce it (accessibility, safety).
3. Plan privacy and consent (location and health data are sensitive; `legal-ethics`).
4. Design for the real activity's rhythm (a walk is 20–40 minutes; sleep is once a day).
**Examples.** Real-world locations as game nodes (Ingress, then Pokémon GO reusing its location data). Running as the input of an audio story with chases (Zombies, Run!, Six to Start, 2012). Sleep tracking turned into creature research (Pokémon Sleep, 2023). Habits as RPG quests (Habitica).
**Risks.** Safety, privacy and accessibility; dependence on sensors and platform permissions; weak retention when the novelty fades.
**Ontology delta.** `verbs[]` (non-touch inputs), `technical.backend`, `legal-ethics` review, `ux.accessibility`.

---

## 7. Production operators

### OP25 Automation shift
**Move.** Move the player from doing to planning or delegating: combat becomes automatic; the skill becomes drafting, positioning or programming.
**Procedure.**
1. Decide which decisions remain human (team composition, placement, timing of abilities).
2. Automate execution deterministically; show a readable replay or fast-forward.
3. Increase decision quality: synergies, counters, positioning matter visibly.
4. Provide a speed control and skip for repeated content.
**Examples.** Draft and positioning with automatic combat (Auto Chess, a Dota 2 custom map, 2019, then Teamfight Tactics and Dota Underlords). Automatic attacks with only movement and drafts (Vampire Survivors). Automatic battles in idle RPGs (AFK Arena).
**Risks.** Players feel like spectators; outcomes look random when the simulation is opaque.
**Ontology delta.** `verbs[]`, `mechanics[]` (auto-resolution), `technical.deterministic`.

### OP26 Mode extraction
**Move.** Pull a mode, mini-game or user-made map out of a larger game and make it the whole game, or the reverse: compress a game into a mode or event.
**Procedure.**
1. Look for modes, custom maps, events or ad mini-games that outperform their parent in play time or creative tests.
2. Check the extracted mode stands alone: core loop closes, meta can be grafted.
3. Rebuild it with its own FTUE and economy.
4. Honour honesty: if ads show a mini-game, ship it as a real, prominent mode (`genre-playbooks` anti-patterns).
**Examples.** A battle royale mode spun out of a co-op game into its own product (Fortnite Battle Royale from Fortnite: Save the World, 2017). A custom map that became a genre (Defense of the Ancients from Warcraft III → the MOBA; Auto Chess from Dota 2). Action mini-games advertised and then built into a 4X game (Last War: Survival, widely discussed; verify).
**Risks.** The extracted mode depended on the parent's audience or economy; fake-ad backlash if the mode is token.
**Ontology delta.** New `loops[]`; `scope`; marketing creatives must match `contract`.

### OP27 Creation flip
**Move.** Let players make the content (levels, rooms, cards, decks), turning consumers into creators and the content treadmill into a community.
**Procedure.**
1. Expose the level format (`level-spec.schema.json`) in a constrained editor with templates.
2. Require a clear check: creators must beat their own level before publishing.
3. Add curation: ratings, featured lists, difficulty tags, reporting.
4. Moderate names, text and images; plan for minors.
5. Reward creators with visibility and cosmetics, not pay-to-win.
**Examples.** Course creation with a mandatory clear before upload (Super Mario Maker, Nintendo, 2015). User levels as a long tail for a one-tap rhythm platformer (Geometry Dash, RobTop Games, 2013). Whole platforms of user-made games (Roblox).
**Risks.** Moderation cost and liability; low-quality floods; discoverability problems.
**Ontology delta.** `content.levels.generation: hybrid`, `technical.backend`, `legal-ethics`.

### OP28 Content generator swap
**Move.** Replace handmade content with procedural or systemic content (or the reverse for authored peaks), gated by solvers or bots.
**Procedure.**
1. Write the content grammar (pieces, rules, difficulty knobs).
2. Build a generator (`pcg.py`) plus a verifier (`puzzle_solver.py`, `match3_sim.py`, bots) that rejects unsolvable or off-target levels.
3. Target difficulty per slot in a curve (`difficulty_curve.py generate ...`).
4. Keep a handmade layer for teach and twist levels; generate the rest.
5. Seed everything for reproducibility and daily challenges.
**Examples.** Procedural levels with handmade chunks (Spelunky, Derek Yu, 2008). Systemic endless play with no level authoring (Block Blast!). Candy Crush's large handmade level ladder, with King's human-like bots estimating difficulty (see `game-case-studies` volatile facts).
**Risks.** Sameness; difficulty spikes from generator edge cases; loss of authored surprise.
**Ontology delta.** `content.levels.generation`, `level-spec.schema.json` `solver`, scripts.

### OP29 Collection graft
**Move.** Add a set of collectible items whose completion is a long-term goal: characters, stickers, cards, photos, museum pieces.
**Procedure.**
1. Define sets (8–12 items per set is a common readable size), rarities and completion rewards.
2. Decide duplicate handling: trade, convert to dust or currency, or upgrade.
3. Decide acquisition: earned through play, events, or random packs. Random packs need odds disclosure and age rules (`legal-ethics`, `gacha_calc.py`).
4. Show the album prominently; completion bars use the goal-gradient effect honestly.
**Examples.** Characters from a prize machine (Crossy Road). Sticker albums with trading (Monopoly Go!) after card sets (Coin Master). A photo album of visiting cats (Neko Atsume, Hit-Point, 2014). Museum donations and community-centre bundles (Stardew Valley).
**Risks.** Paid randomness regulation; the last-item grind; collections that do nothing for the core.
**Ontology delta.** `economy.currencies[]` (duplicates), `loops[]` (`type: meta`), `monetization` odds disclosure.

### OP30 Narrative wrap / unwrap
**Move.** Wrap an abstract loop in a story that gives sinks meaning (wrap), or strip story to cut friction and cost (unwrap).
**Procedure.**
1. Wrap: attach story beats to meta milestones (each renovation area = a chapter); keep dialogue skippable and short; end chapters on hooks.
2. Unwrap: measure skip rates and time-to-core; remove dialogue that delays play; keep the progress fantasy visual.
3. Budget narrative content against the content treadmill (`genre-playbooks` Core model 5).
**Examples.** Story wrap around match-3 renovation (Homescapes, Gardenscapes). Mystery story wrapping merge-2 (Merge Mansion). Royal Match's trimmed, mascot-led meta with little dialogue (an interpretation of its "unwrap"; see `references/worked-analogies.md`).
**Risks.** Story cost outpaces production; players skip it all; tone mismatches the ads.
**Ontology delta.** `narrative-design` assets, `progression.tracks[].unlocks`, `content.worlds`.

### OP31 Merge-ification
**Move.** Replace "buy an upgrade" with "combine identical items to get the next tier", using board space as the constraint.
**Procedure.**
1. Define tier chains (5–10 tiers per chain) and generators that produce tier-1 items.
2. Use board space as the pressure: full boards force decisions.
3. Connect top tiers to orders, defence power or meta progress.
4. Decide merge rule: 2 → 1 (merge-2, fast) or 3 → 1 with a 5 → 2 bonus (Triple Town and Merge Dragons tradition).
**Examples.** Adjacent-match evolution on a grid (Triple Town, Spry Fox, 2010) → open-board merging (Merge Dragons!, Gram Games, 2017) → merge-2 with orders and story (Merge Mansion, Metacore). Merging towers in a lane defence (Random Dice, Rush Royale). Number merging (Threes!, 2048).
**Risks.** Board clutter on small screens; energy-gated generators becoming the main frustration.
**Ontology delta.** `mechanics[]` (merge), `economy` nodes (generator source, merge converter), `ux.hud`.

### OP32 Puzzle-ification
**Move.** Resolve a genre's action or combat through a puzzle (match-3, sliding, turn-based board), turning reflex skill into pattern skill.
**Procedure.**
1. Identify the source genre's conflict (combat, stealth, heist).
2. Choose a puzzle whose outcome maps to conflict outputs (matches → damage by colour; moves → stealth turns).
3. Keep the source fantasy in the meta (heroes, gear, levels).
4. Verify the puzzle layer with solvers or bots; keep the RPG power bridge bounded.
**Examples.** Monster-team combat resolved by orb matching (Puzzle & Dragons). Match-3 combat with hero collection and a base (Empires & Puzzles, Small Giant Games, 2017). An RPG with match-3 battles (Puzzle Quest, Infinite Interactive, 2007). A stealth-action franchise turned into a turn-based diorama puzzle (Hitman GO, Square Enix Montreal, 2014).
**Risks.** Fans of the source genre want the reflex fantasy; puzzle skill and RPG power fight for control.
**Ontology delta.** `verbs[]`, `mechanics[]`, `progression` power bridge, level-spec solvers.

---

## 8. Selection matrix: operator by goal

| Goal | First-choice operators | Second-choice | Avoid |
|---|---|---|---|
| Novelty in a consolidated genre | OP03 constraint inversion, OP04 perspective flip, OP12 verb swap | OP18 stakes, OP19 information | OP02 alone (re-skin) |
| Lower CPI / readable ads | OP03, OP05 magnify, OP12 | OP02 with a strong theme, OP26 | OP07 with two cores |
| Deeper retention (D7+) | OP14 meta graft, OP29 collection, OP11 social | OP23 ritual, OP15 roguelite | OP17 without a meta |
| Better monetization (ethical) | OP14, OP29 with disclosed odds, OP11 teams | OP16 idle multipliers | OP18 with paid currency |
| Cheaper production | OP28 generator, OP08 subtraction, OP23 ritual | OP25 automation | OP30 wrap, OP05 progressive scale |
| Agent buildability | OP06 to turn-based, OP20 determinism, OP28, OP32 | OP25 | Real-time OP21/OP22 multiplayer |
| New audience | OP09 audience, OP24 real-world, OP02 theme | OP08 | OP07 with midcore meta |
| Port a PC/console hit | OP10 platform, OP17 session, OP14 meta | OP08 | Keeping landscape twin-stick by habit |
| Refresh a live game | OP02 seasonal theme, OP26 event mode, OP21 co-op event | OP23 daily | Core verb changes for live players |
| Turn a toy into a game | OP15 roguelite, OP23 ritual, OP29 collection | OP11 | Heavy meta before the toy is fun |

---

## 9. Stacking and compatibility rules

1. **Maximum two operators per concept**, on different layers (core vs meta vs wrapper). A third operator needs a written reason and a check against the expectation budget.
2. **One broken expectation.** Count the genre expectations the stack breaks; more than one makes the ad and the store page hard to read.
3. **Core first.** Apply core-layer operators (OP03, OP06, OP12) before meta operators (OP14, OP29), and test the core toy before adding the meta.
4. **Check the bridge after every meta operator.** Every meta must consume a core output.
5. **Ethics gate after OP13, OP18, OP29.** These are the operators most likely to import pressure mechanics.

**Good pairs** (precedent-backed)

| Pair | Why it works | Precedent |
|---|---|---|
| OP10 platform + OP14 meta | Mobile session plus F2P depth | Survivor.io |
| OP08 subtraction + OP17 compression | Fewer systems, shorter matches | Marvel Snap, Clash Royale |
| OP03 inversion + OP15 roguelite | The inverted constraint needs drafts to create decisions | Vampire Survivors |
| OP02 theme + OP13 economy re-skin | IP and chance device swapped together | Monopoly Go! |
| OP23 ritual + OP11 social (share) | Shared daily scarcity fuels conversation | Wordle |
| OP31 merge + OP14 meta (orders) | Orders turn open merging into goals | Merge Mansion |
| OP32 puzzle + OP29 collection | Puzzle skill plus hero collection | Puzzle & Dragons, Empires & Puzzles |

**Risky pairs**

| Pair | Failure pattern |
|---|---|
| OP07 fusion + OP07 fusion | Three genres; no owner of the core verb |
| OP18 stakes + OP29 random packs | Gambling resemblance stacked twice |
| OP05 progressive scale + OP10 low-end mobile | Performance and readability collapse |
| OP24 real-world + OP22 asymmetric real-time | Safety, matchmaking and backend costs multiply |
| OP16 idle + OP15 roguelite without a clear run end | Neither the idle nor the run loop closes |

---

## 10. Operator worksheet and ontology delta summary

### 10.1 Worksheet (copy into `.gamestudio/concepts/<id>.ops.md` or into the concept rationale)

```
Source / chassis:            <game or genre>; core loop: "<act -> reward -> invest>"
Target segment & motivations: <segment>; <top 2 motivations>
Goal of the transformation:  <novelty | CPI | retention | cost | audience | port | refresh>
Operator 1:                  OPxx <name>  -> what changed: <relation-level change>
Operator 2 (optional):       OPyy <name>  -> what changed: <...>
Loop after transformation:   "<one sentence>"
Emergent structure (hook):   "<true in the result, false in the source>"
Broken expectation (one):    <...>
Ethics gate (OP13/18/29):    <pass | issue>
AFS for borrowed relations:  <score> (<GO | ADAPT | DROP>)
Ontology fields touched:     <list>
Cheapest test:               <toy | paper | bot sim | greybox | creative test> with pass/kill thresholds
```

### 10.2 Ontology delta summary

| Operator | Main contract fields touched |
|---|---|
| OP01 transplant | `mechanics[]`, `loops[].steps`, mechanic card `references` |
| OP02 theme | `art_direction`, `audio_direction`, `player_fantasy`, `meta.logline` |
| OP03 inversion | `verbs[]`, `mechanics[].rules`, `ux.hud` |
| OP04 perspective | `player_fantasy`, `verbs[]`, `loops[]` |
| OP05 scale | `progression.tracks[]`, `technical.perf_budgets` |
| OP06 time | `mechanics[]`, `technical.deterministic`, `technical.multiplayer` |
| OP07 fusion | `meta.genre`/`subgenre`, `loops[]`, `economy.currencies[]` |
| OP08 subtraction | `mechanics[]` (fewer), `ftue.steps[]`, `scope.wont` |
| OP09 audience | `meta.target_audience`, `monetization.ethics`, `analytics.kpi_targets` |
| OP10 platform | `meta.orientation`, `verbs[].input`, `technical.min_spec`, `perf_budgets` |
| OP11 social | `loops[]` (social), `technical.backend` |
| OP12 verb | `verbs[]`, `mechanics[].rules`, level-spec knobs |
| OP13 economy | `economy.currencies[]`, `economy.model_ref` |
| OP14 meta | `loops[]` (meta), `progression.tracks[]`, `content` |
| OP15 roguelite | `loops[]` (run), `mechanics[]` (draft), `technical.deterministic` |
| OP16 idle | economy nodes (`per_minute`), `progression.tracks[]` (prestige) |
| OP17 session | `meta.session_length_target_sec`, timers in `parameters` |
| OP18 stakes | `mechanics[]`, `progression.tracks[]` (rank), `monetization.ethics` |
| OP19 information | `mechanics[].rules`, `ux.hud` |
| OP20 randomness | `mechanics[].rules`, `technical.deterministic`, level-spec `solver` |
| OP21 co-op/competitive | `loops[]` (social), `technical.multiplayer` |
| OP22 asymmetry | per-role `mechanics[]`, `technical.multiplayer` |
| OP23 ritual | `loops[]` (daily), `liveops.cadence` |
| OP24 real-world | `verbs[]`, `technical.backend`, `ux.accessibility` |
| OP25 automation | `verbs[]`, `mechanics[]`, `technical.deterministic` |
| OP26 mode extraction | `loops[]`, `scope` |
| OP27 creation | `content.levels.generation`, `technical.backend` |
| OP28 generator | `content.levels.generation`, level-spec `solver` |
| OP29 collection | `economy.currencies[]`, `loops[]` (meta), `monetization` |
| OP30 narrative | `progression.tracks[].unlocks`, `content.worlds` |
| OP31 merge | `mechanics[]`, economy nodes (generator, converter) |
| OP32 puzzle | `verbs[]`, `mechanics[]`, progression power bridge |
