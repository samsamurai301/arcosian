# Designer Philosophies

The working philosophies of notable game designers, summarized in our own words with attribution, each turned into **one practical rule** and **one worked application** for mobile game design. The point is not to collect quotes but to give agents a set of tested lenses: when a design decision stalls, ask what Meier, Koster or Rosewater would check, then apply the rule. Ideas are attributed to the person most associated with them; many were developed with collaborators or built on earlier work. Short quotes are avoided on purpose: designers' words are paraphrased, and anything we could not pin to a source is flagged **verify**. Numbers inside the "Applied" examples are our own illustrative tuning values, not the designer's.

## Contents

1. How to use this file
2. The Nintendo school: Shigeru Miyamoto, Gunpei Yokoi, Masahiro Sakurai
3. Systems and simulation: Will Wright, Sid Meier, Tynan Sylvester, Warren Spector
4. Meaning through mechanics: Jonathan Blow, Brenda Romero, Lucas Pope, Jenova Chen
5. Theory builders: Raph Koster, Eric Zimmerman and Katie Salen, Jesse Schell, Daniel Cook
6. Tabletop and card masters: Richard Garfield, Reiner Knizia, Mark Rosewater
7. Indie craft and difficulty: Derek Yu, Eric Barone, Hidetaka Miyazaki, Rami Ismail and Jan Willem Nijman
8. Further voices (short entries)
9. Where they disagree, and how to choose
10. Rules index: every derived rule and where the plugin checks it

---

## 1. How to use this file

- **As a critique lens.** In a design review, pick three to five designers whose concerns match the decision (for an economy decision: Meier, Knizia, Garfield, Cook). Apply each rule and record pass/fail with a reason. Procedure D in `SKILL.md` gives the full lens review.
- **As a tie-breaker.** When two agents disagree, find the designer whose rule addresses the disagreement directly and test the rule on the build, not in argument.
- **Not as authority.** "Miyamoto would do it" is not a justification. The doctrine (player first) is the justification; the designer's rule is a way to check it.

---

## 2. The Nintendo school

### Shigeru Miyamoto — *Donkey Kong*, *Super Mario Bros.*, *The Legend of Zelda*, *Pikmin*

**Key ideas.**
- Design starts from a physical pleasure: the feel of a verb under the thumb. The toy comes before the game.
- Teach by arrangement, not instruction: the first screen of *Super Mario Bros.* places a slow enemy and a power-up so that the player learns by doing (Miyamoto has discussed this level in interviews).
- Draw on real experience: he has described childhood exploration of the countryside around Kyoto as a root of *Zelda*'s sense of discovery (widely reported).
- Watch people who are not gamers play, and fix what confuses them.
- The contained playground: a small, dense space full of things to poke ("miniature garden", *hakoniwa*, is a term often used for this Nintendo approach).

**Practical rule.** *A verb must be enjoyable in an empty room before it earns a level.*

**Applied.** A grappling-hook mobile game: build only tap-to-attach, hold-to-swing, release-to-fly, with one anchor point on a blank screen. Tune rope length, gravity and release boost until a playtester keeps swinging with no goal. Only then build level 1, whose single gap can be crossed only by releasing at the bottom of the arc, teaching the key skill without text. In the plugin this is the first build of any concept, and it is what the human signs off at the fun checkpoint.

### Gunpei Yokoi — Game & Watch, Game Boy, the cross-shaped D-pad

**Key ideas.**
- *Lateral thinking with withered technology*: use mature, cheap, reliable components in a new way. Players do not care about specifications; they care about the experience.
- Durability, battery life and price are design features.
- When you cannot win on power, win on the idea.
- The Game & Watch cross-shaped directional pad (credited to Yokoi's team) solved a real input problem with a simple part.

**Practical rule.** *Spend novelty on one dimension only; make everything else proven and boring.*

**Applied.** A concept whose hook is a new tilt-based mechanic uses the phone's accelerometer (mature, universal), a stable engine release, standard 2D rendering and the plugin's sim-core template. All risk sits in the hook, so the prototype answers one question: is tilting fun? A concept that needs a new engine feature, a novel network model *and* a new input scheme fails this rule and should be split or killed.

### Masahiro Sakurai — *Kirby*, *Super Smash Bros.*, *Kid Icarus: Uprising*

**Key ideas.**
- Games are built on risk and return: the player takes a risk and expects a proportional reward. Sakurai has made this a recurring theme of his long-running video series on creating games (from 2022).
- Design for beginners without boring experts: *Kirby's Dream Land* (1992) was made so newcomers could finish it, with an extra mode for skilled players.
- Feel and clarity: brief freeze frames on impact ("hit-stop") sell weight; distinct silhouettes and clear telegraphs make the action readable at a glance.
- Careful specification and planning before production (widely reported about his working style).

**Practical rule.** *Every attack, purchase or move should carry a visible risk proportional to its reward.*

**Applied.** In a one-thumb auto-battler, a charged shot roots the player for 0.6 s with a visible wind-up glow and deals 2.5× damage; a dash is free but has a 3 s cooldown shown on the button. Heavier hits get longer hit-stop (a few frames; tune by feel). If playtests show players never use the charge shot, the risk is too high for the return: adjust one side by doubling or halving (see Meier).

---

## 3. Systems and simulation

### Will Wright — *SimCity*, *The Sims*, *Spore*

**Key ideas.**
- Games are models of systems; the player learns the model by experimenting with it.
- "Software toys": *SimCity* (1989) had no win condition. Players set their own goals inside a possibility space.
- Abstraction invites projection: players fill in detail with imagination (the gibberish speech of the Sims is a well-known example), which often works better than literal detail.
- Design the mental model you want players to build, and make the simulation's outputs teach it.

**Practical rule.** *Make the rules learnable from their visible outputs; abstract anything the player will imagine better than you can render.*

**Applied.** An idle city builder: traffic is shown as visibly slowing cars on a congested road, and placing a second road visibly clears it within seconds. Players infer "roads carry capacity" without a tooltip. Citizens are shown as simple tokens with one mood icon rather than detailed animated people, which saves art budget and invites projection.

### Sid Meier — *Civilization*, *Pirates!*, *Railroad Tycoon*

**Key ideas.**
- A game is a series of interesting decisions (a widely attributed definition he expanded in a 2012 GDC talk).
- The player should be the one having fun, not the designer or the computer.
- Tune boldly: when a value feels wrong, double it or cut it in half rather than nudging it, then narrow down.
- Players misjudge probability: in a 2010 GDC keynote he described adjusting how odds work in a *Civilization* game because players felt cheated by mathematically fair results (reported).

**What makes a decision interesting (our synthesis of his criteria):** no option dominates; the player has enough information to reason; the right answer depends on the situation; consequences are visible; the choice persists long enough to matter.

**Practical rules.** *Tune by doubling or halving until you have bracketed the sweet spot.* *A choice with a dominant answer is not a decision: remove it or rebalance it.*

**Applied.** A tower-defence prototype where a tower at 100 coins is never bought: run `economy_sim.py` with the tower at 50 and at 200 instead of 90 and 110, find the region where it gets bought without dominating (say 60–80), then fine-tune. For upgrade picks, log pick rates; any option picked over 70% of the time in a three-way choice is a dominance candidate (heuristic).

### Tynan Sylvester — *RimWorld*; author of *Designing Games* (2013)

**Key ideas.**
- Games are engines of experience: mechanics exist to produce emotions and stories.
- In his essay "The Simulation Dream" (2013) he warned against simulating complex systems that players never perceive: the cost is real and the experience gain is zero.
- Players see patterns and stories in randomness (apophenia); a light simulation plus good event framing yields rich stories.
- *RimWorld*'s AI "storytellers" pace events (calm, rising tension, crisis) rather than leaving them purely random.
- Elegance: simple rules with deep consequences beat complex rules with shallow ones.

**Practical rule.** *Only simulate what the player can perceive and what can generate a story; fake the rest.*

**Applied.** A merge-town game with villagers: give each villager two visible traits that change outcomes the player sees (Lazy: −20% production; Brave: better expedition loot), and an event director that schedules one crisis per session after minute 2. Do not model hunger, sleep and relationships invisibly; the economy simulator cannot even test what the player cannot see.

### Warren Spector — *Deus Ex*, *System Shock* lineage, *Epic Mickey*

**Key ideas.**
- Player expression and shared authorship: the player co-writes the experience through choices the designer enables but does not script.
- Consistent systems let players plan; multiple solutions emerge from systems interacting rather than from hand-built branches.
- The world should acknowledge what the player did.
- Immersive-sim practice frames obstacles as problems with many solutions rather than puzzles with one (a framing associated with Spector and the Looking Glass lineage).

**Practical rule.** *Every major obstacle should have at least two solutions through different systems, and the game should acknowledge the one chosen.*

**Applied.** A mobile heist puzzle: a guard can be passed by distraction (noise system), timing (patrol system) or a bought gadget (economy). Each route is telegraphed in the level. The results screen names the approach ("Ghost", "Gadgeteer"), and the next level briefing references it. Record the intended routes in the level spec's `notes`; where the layout type is supported, confirm solvability with `puzzle_solver.py`, then block one route at a time and re-solve to prove the others still work.

---

## 4. Meaning through mechanics

### Jonathan Blow — *Braid*, *The Witness*

**Key ideas.**
- A good mechanic contains truths to discover; the designer's job is to find its most interesting implications and present them in order.
- No filler: each puzzle should express one idea, and puzzles that repeat an idea waste the player's time.
- Teach non-verbally through careful sequencing.
- He has publicly criticized designs built around reward schedules as manipulating players rather than respecting them (in talks and interviews from the late 2000s onward).

**Practical rule.** *Each level must teach, test or combine a distinct idea; if two levels do the same job, cut one.*

**Applied.** A 60-level sliding-block pack is audited by tagging each level spec with the idea it introduces or combines. Twelve core ideas, each run through teach, test, twist and combine, give 48 purposeful levels; the remaining 12 are either reward levels (deliberately easy, tagged `reward`) or are cut. Duplicates show up as two levels with the same idea and the same `teach` tag.

### Brenda Romero — *Wizardry* series, *Train*; co-author of *Challenges for Game Designers* (2008, as Brenda Brathwaite, with Ian Schreiber)

**Key ideas.**
- The mechanic is the message: systems carry meaning on their own. Her board game *Train* (2009) has players efficiently loading figures onto boxcars before revealing what the system represents, making players feel complicit in following rules.
- Prototype on paper and with physical pieces; many design problems can be solved before code exists.
- Design exercises and constraints build designer skill.

**Practical rule.** *Write your core loop as a sentence about what the player is rewarded for valuing; if the sentence contradicts your pillars, change the mechanic, not the pillars.*

**Applied.** A cozy forest game with the pillar "care for nature" whose optimal strategy is clear-cutting for coins reads as "the player is rewarded for destroying the forest". Fix: make regrowth and biodiversity yield more over three days than cutting yields today, so the dominant strategy matches the pillar. Add the loop-sentence check to every design review and compare it against `meta.pillars` in the contract.

### Lucas Pope — *Papers, Please*, *Return of the Obra Dinn*

**Key ideas.**
- Mundane mechanics can carry moral weight: in *Papers, Please* (2013) document inspection under economic pressure forces choices between rules, compassion and survival.
- Deduction design needs anti-guessing protection: *Return of the Obra Dinn* (2018) confirms the player's conclusions only when three fates are correct at once, which defeats brute force.
- A hard technical constraint can become the style (Obra Dinn's 1-bit dithered look).
- Open development through public devlogs.

**Practical rule.** *Verify deductions in batches so guessing does not pay; let pressure come from systemic trade-offs, not only from timers.*

**Applied.** A mobile detective game confirms suspect, motive and method only when three cases are solved correctly together; hints cost a soft currency earned by play, never premium currency. Pressure comes from limited interrogation actions per day, which forces prioritization.

### Jenova Chen — *flOw*, *Flower*, *Journey*, *Sky: Children of the Light*

**Key ideas.**
- Flow (Mihaly Csikszentmihalyi's concept) applied to games: keep challenge matched to skill. His MFA thesis (*Flow in Games*, 2006) argued for letting the player steer difficulty through in-game choices rather than only through hidden adjustment.
- Games can and should evoke a wider range of emotions than excitement.
- Design for people who do not see themselves as gamers.
- Communication constraints can make strangers kind (*Journey*'s chirp-only interaction).

**Practical rule.** *Give players a voluntary, in-play way to raise or lower challenge, and use hidden adjustment only as a safety net.*

**Applied.** An endless runner adds a risky lane with doubled coins and faster hazards; players dip into it when confident and leave when stressed. Hidden adjustment (a slight hazard slowdown after three quick deaths) stays as a backstop and is logged as an analytics event so its effect can be measured (`player-analytics`).

---

## 5. Theory builders

### Raph Koster — *Ultima Online*, *Star Wars Galaxies*; author of *A Theory of Fun for Game Design* (2004)

**Key ideas.**
- Fun is the feeling of learning: the brain enjoys recognizing and mastering patterns. Once a pattern is fully absorbed ("grokked"), the game becomes boring.
- Games are formal systems that train skills; the theme makes them approachable but the pattern is what is learned.
- Later work describes a "grammar" of game design built from small loops of input, model and feedback.
- From online worlds: community and social structure are designed, not accidental.

**Practical rule.** *When players have mastered the current pattern, introduce a new pattern, raise the stakes, or let the game end gracefully.*

**Applied.** Track per-mechanic mastery signals from playthrough and analytics data: median solve time and error rate per level. When both stop improving for about five consecutive levels (heuristic), the pattern is grokked; schedule a new mechanic or a twist in the next level batch. In a puzzle game this typically lands a new element every 10–20 levels (typical of the genre, not a rule).

### Eric Zimmerman and Katie Salen — *Rules of Play* (2003); Zimmerman co-founded Gamelab

**Key ideas.**
- Meaningful play arises when the relationship between an action and its outcome is both *discernable* (the player can perceive what happened) and *integrated* (the outcome matters to the larger game).
- A game can be understood as rules (formal system), play (experience) and culture (context).
- The magic circle: play creates a bounded space with its own meanings.
- Iterative design: prototype, playtest, evaluate, refine — design is a research process.
- Zimmerman's later essay "Manifesto for a Ludic Century" (2013) argues that systems literacy and play will define culture.

**Practical rule.** *Every player action needs immediate perceivable feedback (discernable) and a later consequence (integrated).*

**Applied.** A verb audit table for the contract: for each entry in `verbs`, list the feedback within about 100 ms (sound, flash, number) and the downstream consequence (score, unlock, resource). A "tap the mascot" verb that animates but changes nothing later fails integration; either connect it (petting fills a small happiness meter that boosts the next level's coins) or label it explicitly as a toy.

### Jesse Schell — *The Art of Game Design: A Book of Lenses* (2008; later editions)

**Key ideas.**
- The game is not the experience: the experience happens in the player, and that is the real product.
- Design improves when the same design is examined from many perspectives ("lenses"), each framed as questions.
- The elemental tetrad: mechanics, story, aesthetics and technology must support one another, and the weakest element limits the whole.
- Listening — to the team, the client, the players and the game itself — is the designer's core skill.

**Practical rule.** *Before approving a design decision, examine it from at least five distinct perspectives chosen for that decision, and write down what each reveals.*

**Applied.** The plugin's design reviews already use perspective-based passes (design, economy, UX, monetization ethics, technical feasibility, market, scope). For a single decision such as "add an energy system", choose perspectives explicitly: player time, novice experience, economy flow, monetization ethics and session fit. Use Schell's book for the full set of lenses; do not paste its question lists into project files.

### Daniel Cook — Lost Garden essays; Spry Fox (*Triple Town*, *Alphabear*, *Cozy Grove*)

**Key ideas.**
- Skill atoms ("The Chemistry of Game Design", 2007): a player action feeds a simulation, which produces feedback, which updates the player's mental model. Atoms chain into skill chains; boredom or burnout appears when an atom is mastered or when a chain breaks.
- Loops and arcs (2012 essay): loops are repeatable systems that build mastery; arcs are content consumed once (story, set pieces). Most games mix them and should know which is which.
- Prosocial and cozy design: games can be built to foster trust, cooperation and community health, not just engagement.
- Strong criticism of manipulative monetization; respect for players as people.

**Practical rule.** *Map every mechanic as a skill atom in a chain; any atom with no feedback step, or no downstream atom, is a dead end to fix or cut.*

**Applied.** A merge game's chain: drag two items (action) → merged tier (simulation) → pop, sound and tier number (feedback) → player learns tier rules (model) → feeds "plan board space" → feeds "set up chain merges for bonus". If playtests show players never learn chain merges, the feedback for chains is too weak: add a combo counter and a distinct sound, then re-test with fresh personas.

---

## 6. Tabletop and card masters

### Richard Garfield — *Magic: The Gathering*; co-author of *Characteristics of Games* (2012, with George Skaff Elias and K. Robert Gutschera)

**Key ideas.**
- Created the collectible card game format: a shared rule core plus a variable, player-assembled card pool, so the metagame (what players bring) is part of the game.
- Luck and skill are not opposites. Luck lets weaker players win individual games and keeps strong players humble; skill shows over many games. Games sit on a spectrum, and the right point depends on the audience.
- Games have properties (length, player interaction, rules complexity, luck, skill) that can be analyzed and deliberately tuned.

**Practical rule.** *Tune variance so a weaker player sometimes wins a single match while a stronger player wins a clear majority over many.*

**Applied.** A mobile PvP card battler: simulate a strong bot against a medium bot over 1,000 games. If the strong bot wins 95%, newcomers will feel there is no hope; if it wins 52%, skill feels irrelevant. Many competitive casual designs aim somewhere around 60–75% for a clearly stronger player (our heuristic, not Garfield's number). Adjust draw variance, hand size or comeback mechanics until the result lands in the band you chose.

### Reiner Knizia — *Tigris & Euphrates*, *Ingenious*, *Lost Cities*, *Ra*, *Modern Art*

**Key ideas.**
- Elegant, minimal rules that create hard choices; trained as a mathematician, he builds tension from simple arithmetic structures.
- Score the weakest: in *Tigris & Euphrates* and *Ingenious*, a player's final score is their lowest category, which forces balanced development.
- Auctions and valuation games (*Ra*, *Modern Art*) where the players set the prices.
- Commitment under uncertainty: *Lost Cities* asks when to commit to an expedition, trading early investment against information.

**Practical rule.** *To force breadth, score the minimum across tracks instead of the sum.*

**Applied.** A mobile town builder's star rating = min(housing, happiness, industry) on a 1–5 scale. Players cannot stack one category to win; a weekly event leaderboard uses the same rule. In `economy_sim.py` archetypes that over-invest in one track will show slow rating growth, which is the intended signal.

### Mark Rosewater — Head designer of *Magic: The Gathering*

**Key ideas.**
- Player psychographics *Timmy*, *Johnny* and *Spike*: players who seek big experiences and power, players who seek creative expression and combos, and players who seek proof of skill and winning.
- *New World Order*: limit complexity at the commonest rarity so new players are not overwhelmed, while depth lives elsewhere.
- *Lenticular design*: content that looks simple to beginners and reveals depth to experts.
- From his GDC 2016 talk "Twenty Years, Twenty Lessons" (summarized, not exhaustive): make the fun part also the correct strategy; restrictions breed creativity; your audience is good at recognizing problems and bad at solving them; be more afraid of boring players than of challenging them; resonance with things players already know is powerful; piggyback on existing knowledge to cut learning cost.

**Practical rules.** *Treat player complaints as accurate problem reports and their proposed fixes as hypotheses.* *If the optimal strategy is not the fun strategy, change the rules until it is.*

**Applied.** Playtest and review triage: the `player-simulator` and human feedback produce problem statements ("level 14 feels unfair"); the `game-designer` proposes fixes; the fix is tested, not the suggestion. And if bots show the optimal play in a runner is to stand still in the safe lane, the design is broken even if players never complain: make the safe lane progressively narrower.

---

## 7. Indie craft and difficulty

### Derek Yu — *Spelunky*, *Spelunky 2*, *UFO 50* (with Mossmouth collaborators)

**Key ideas.**
- Spelunky's levels combine hand-made room templates on a small grid with a guaranteed path from entrance to exit, then randomize contents. Authored quality plus procedural variety.
- Deep systemic interactions (shopkeepers, items, physics, enemies) create emergent stories players retell.
- In his book *Spelunky* (Boss Fight Books, 2016) and his blog writing about finishing games, he stresses keeping scope achievable and actually finishing (summary; verify specific advice before quoting).

**Practical rule.** *Generate and guarantee the critical path first; decorate and randomize around it.*

**Applied.** A mobile roguelite dungeon: `pcg.py bsp --w 48 --h 32 --seed S` produces rooms; the critical path from start to exit is computed and locked; side rooms receive random loot and hazards; a solver or bot run confirms reachability. Reject any seed where the path is longer than a target (for example 90 seconds of movement) to protect session length.

### Eric Barone (ConcernedApe) — *Stardew Valley*

**Key ideas.**
- Make the game you want to play and keep creative control; patience over pressure.
- Many simple systems overlapping (farming, foraging, fishing, mining, relationships, community bundles), each with a different time scale.
- Generosity builds lasting goodwill: large free updates and no microtransactions.

**Practical rule.** *Each session should end with at least one goal almost done, preferably on a different track from the one just completed.*

**Applied.** A farming-lite mobile game uses crops on 1-, 3- and 7-day timers, a friendship track that advances once per day per character, and a mine whose next floor needs one more upgrade. When the player finishes a crop cycle, a friendship heart and a mine floor are both one step from done. Lay the track timers out in a day-by-day table (use `progression_calc.py time-to-level` for any XP-based track) and check that no day ends with every track idle.

### Hidetaka Miyazaki — *Demon's Souls*, *Dark Souls*, *Bloodborne*, *Sekiro*, *Elden Ring*

**Key ideas.**
- Accomplishment comes from overcoming real difficulty; the difficulty must be fair and learnable.
- Fragmentary, environmental storytelling that invites interpretation.
- Asynchronous co-presence: other players' messages and ghosts make a single-player world feel shared.
- Interconnected worlds where shortcuts reward exploration and relieve tension.

**Practical rule.** *After every death the player should be able to name the cause; if they cannot, treat the death as a bug.*

**Applied.** A mobile action game logs each death with its cause (enemy, attack id, telegraph shown or not). Deaths from attacks without a visible wind-up, or from off-screen sources, are filed as `major` findings in playtest reports. A checkpoint follows every difficulty spike, and runs are short enough that a death costs at most about a minute of progress.

### Rami Ismail and Jan Willem Nijman — Vlambeer (*Super Crate Box*, *Ridiculous Fishing*, *Nuclear Throne*)

**Key ideas.**
- Short, intense, replayable arcade design; feel above all. Nijman's 2013 talk "The Art of Screenshake" demonstrated how layers of feedback (screen shake, knockback, hit pauses, bigger muzzle flashes, impact effects) transform a bland shooter.
- Build in public: *Nuclear Throne* was developed with regular livestreams and an early-access release.
- Make it easy to talk about your game: Ismail created *presskit()*, a free tool for building press kits.
- Ismail's advocacy: game development as a sustainable, global craft; Vlambeer also spoke publicly about being cloned before *Ridiculous Fishing* launched.

**Practical rule.** *Build in public and make your game effortless to describe, show and share.*

**Applied.** During soft launch, publish a short devlog per update, keep a press-kit folder of screenshots and a 30-second clip, and generate store text with `store_metadata.py --contract PATH --out DIR`. On the feel side, run a "screenshake pass" on every touched interaction before declaring the `visual` gate passed (`game-feel`).

---

## 8. Further voices (short entries)

| Designer / thinker | Key idea (our summary, with attribution) | Practical rule | Mobile application |
|---|---|---|---|
| Nolan Bushnell (Atari) | "Easy to learn, difficult to master" (Bushnell's law) | First meaningful input within seconds; leave mastery headroom | First tap does something satisfying before any menu |
| Satoru Iwata (Nintendo) | Expand the player population; his "Iwata Asks" interviews made cross-discipline reasoning public | Design one entry path for someone who has never played a game | A one-finger mode or first level a non-gamer can clear |
| Tracy Fullerton (*Game Design Workshop*) | Playcentric design: set player-experience goals first and playtest from day one | Write experience goals before features | Contract `player_fantasy` and pillars written before mechanics |
| Steve Swink (*Game Feel*, 2008) | Feel = real-time control + simulated space + polish | Tune input response before content | Measure input-to-feedback latency; target one frame where possible |
| Martin Jonasson and Petri Purho ("Juice it or lose it", 2012 talk) | The same simple game becomes compelling as feedback layers are added | Juice the touched surface, in layers, testing each | Particle, sound, squash and number pop on every tap |
| Nicole Lazzaro ("Four Keys to Fun", 2004) | Hard fun (challenge), easy fun (curiosity), serious fun (meaningful change), people fun (social) | Name which keys your game serves; do not chase all four | Cozy game: easy plus people fun; puzzle: hard fun |
| Celia Hodent (*The Gamer's Brain*, 2017) | Game UX through cognitive science: perception, attention, memory, motivation, emotion | One new concept at a time; reduce memory load | FTUE introduces one mechanic per step (`ftue.steps[].teaches`) |
| Amy Jo Kim (*Game Thinking*, 2018) | Build for early superfans first; learn with rapid, minimal prototypes | Test with your most passionate target players before the mass market | Soft launch to a narrow, high-fit audience first |
| Zach Gage (*SpellTower*, *Really Bad Chess*, *Good Sudoku* with Jack Schlesinger) | Reinvent classic games for phones, remove friction, respect the player | Start from a classic with proven depth; change one thing deeply | A sudoku that teaches techniques instead of brute force |
| Asher Vollmer and Greg Wohlwend (*Threes!*, 2014) | Long iteration on a tiny rule set; the game was quickly cloned (*2048*) | Simplify until the only depth left is the real depth; plan for clones | Ship the polished version fast; build a brand players remember |
| Edmund McMillen (*The Binding of Isaac*) | Items that change how you play, not only your numbers; synergy discovery | Every item should alter behaviour, not just stats | Upgrade pool where half the items change attack patterns |
| Toby Fox (*Undertale*) | Mechanics carry narrative and moral weight (sparing enemies, a game that remembers) | Let systems express the story's choices | Boss fights winnable by mercy actions with different outcomes |
| Frank Lantz (*Universal Paperclips*) | Games as an aesthetic form of thinking; incremental systems can surprise and mean | Incremental games need phase changes, not only bigger numbers | Idle game with two or three rule changes over a run |
| Ian Bogost (*Persuasive Games*, 2007) | Procedural rhetoric: rules make arguments | Audit what your rules argue | Check what your economy rewards morally |
| Greg Costikyan (*Uncertainty in Games*, 2013) | Uncertainty has many sources: randomness, hidden information, opponent behaviour, performance, solving | Choose uncertainty sources deliberately | Puzzle: solver uncertainty; runner: performance uncertainty |
| Clint Hocking (2007 essay) | Ludonarrative dissonance: story says one thing, mechanics reward another | Align story claims with what is rewarded | A "pacifist" hero should not earn most XP from kills |
| Richard Bartle (1996 paper) | Player types: achievers, explorers, socializers, killers | Use types as a conversation aid, then validate with data | Compare with empirical motivation models (`player-psychology`) |
| Keita Takahashi (*Katamari Damacy*) | One joyful, absurd toy can carry a whole game | Find the toy that makes people laugh | A single physics toy as the core of a casual game |

---

## 9. Where they disagree, and how to choose

| Disagreement | One side | Other side | How to decide for a project |
|---|---|---|---|
| Reward schedules | Blow and Cook criticize designs built on compulsion and manipulation | F2P practice treats schedules (dailies, streaks, timers) as retention tools | Doctrine 8 decides: schedules are allowed only if they serve play the player values; no loss-aversion traps, no punishment for missing a day without a recovery path |
| Difficulty and access | Miyazaki: fixed, demanding difficulty is the point | Accessibility advocates: barriers that are not the intended challenge must go; options widen the audience | Separate *challenge intent* from *access barriers*. Keep the intended challenge; remove the barriers (input, readability, timing windows that only fail certain bodies). See `accessibility-localization` |
| Goals or toys | Wright: toys with open goals | Meier: a structured sequence of decisions | Complementary. Build the toy first (Wright, Miyamoto), then give it decisions (Meier). Mobile needs short-term goals inside the toy |
| Authored or emergent | Blow, Pope, Playdead: precise authored puzzles | Spector, Sylvester, Yu: systems and emergence | Use authored content when the experience depends on exact sequence (teaching, reveals); use systems for replayability and stories |
| What fun is | Koster: fun is learning patterns | Lazzaro: four kinds of fun; Chen: emotions beyond fun | Use Koster for skill games and progression pacing; Lazzaro and Chen for social, cozy and emotional games |
| Luck | Garfield: luck widens who can win | Skill purists: randomness dilutes mastery | Pick the audience. Casual and social audiences need more variance; competitive audiences less. Make luck visible and recoverable |
| Fast-follow | Tencent, NetEase, Riot (TFT): fast-follow with execution | Vollmer and Wohlwend, Vlambeer: clones hurt originators | Follow a *genre*, never a specific game's assets or exact design; add a real hook and credit influences |

---

## 10. Rules index: every derived rule and where the plugin checks it

| # | Rule | Source designer | Where it is checked |
|---|---|---|---|
| 1 | A verb must be enjoyable in an empty room before it earns a level | Miyamoto | Grey-box build at the fun checkpoint (`concept-lab`, `build-feature`) |
| 2 | Spend novelty on one dimension; make the rest proven | Yokoi | Concept `hook` vs `risks`; `lead-engineer` feasibility review |
| 3 | Visible risk proportional to reward for every action | Sakurai | `game-designer` mechanic cards; playtest usage data |
| 4 | Rules learnable from visible outputs | Wright | Persona playtests without hints (`player-simulator`) |
| 5 | Double or halve to bracket; no dominant choices | Meier | `economy_sim.py` bracket runs; pick-rate analysis (`player-analytics`) |
| 6 | Simulate only what is perceived and generates story | Sylvester | `lead-engineer` and `systems-designer` scope check |
| 7 | Two solutions per major obstacle, acknowledged | Spector | Level specs; `puzzle_solver.py` with routes blocked in turn |
| 8 | Each level teaches, tests or combines a distinct idea | Blow | Level-spec `teach` tags; duplicate-idea audit (`level-design`) |
| 9 | Loop sentence must match the pillars | Romero | Design review against `meta.pillars` |
| 10 | Verify deductions in batches; pressure from trade-offs | Pope | Mechanic card `failure_modes` (brute force) |
| 11 | Voluntary in-play difficulty choice; hidden DDA as safety net | Chen | `progression.difficulty.dda`; analytics event for DDA activations |
| 12 | New pattern when the old one is mastered | Koster | Solve-time and error-rate trends per mechanic |
| 13 | Discernable and integrated outcome for every verb | Zimmerman and Salen | Verb audit in the contract |
| 14 | Five or more perspectives per major decision | Schell | `/arcosian:design-review` workflow |
| 15 | Every mechanic is a skill atom in a chain; no dead ends | Cook | Mechanic cards `feedback` and `combos` fields |
| 16 | Variance tuned to the chosen win-rate band | Garfield | Bot-versus-bot simulations |
| 17 | Score the minimum to force breadth | Knizia | Economy model review (`economy-design`) |
| 18 | Complaints are accurate problems; fixes are hypotheses | Rosewater | Playtest triage (`qa-lead`, `game-designer`) |
| 19 | Fun strategy must be the optimal strategy | Rosewater | Bot strategy analysis vs intended play |
| 20 | Guarantee the critical path, then randomize | Yu | `pcg.py` output plus solver verification |
| 21 | End each session with a goal almost done on another track | Barone | Progression timeline review (`progression-difficulty`) |
| 22 | Every death has a nameable cause | Miyazaki | Playtest finding category; telegraph checks |
| 23 | Build in public; easy to describe and share | Ismail | Soft-launch plan; `store_metadata.py`; press-kit folder |
