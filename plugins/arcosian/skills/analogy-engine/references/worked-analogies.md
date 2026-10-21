# Worked Analogies: 50 Documented Game Lineages

This file is the precedent library for the analogy engine: 50 lineages in which a game was built by transforming earlier games or non-game systems. Each entry records the lineage, what was preserved, what changed, why it worked or failed, the transformation operators involved (IDs from `references/transformation-operators.md`), and a transferable rule. Only well-documented lineages are included: developer statements, widely reported comparisons, or mechanics anyone can verify by playing. Every "why it worked" is labelled **interpretation**, because success has many causes (timing, UA spend, IP, distribution) that a design reading cannot isolate. Release years are given where well established; "verify" marks dates or details that should be checked before external use. No revenue figures are given. Deeper single-game deconstructions live in `game-case-studies`.

## Contents

1. How to read and use an entry
2. Index of the 50 lineages
3. Match, puzzle and word lineages (W01–W12)
4. Casual-social, farming, pet and idle lineages (W13–W18)
5. Action, arcade, roguelite and io lineages (W19–W27)
6. Strategy, card and PvP lineages (W28–W39)
7. Social deduction, location, real-world and cross-domain lineages (W40–W50)
8. Cross-lineage patterns
9. Failure lessons
10. Method: run a lineage study on any game
11. Volatile facts (as of Oct 2026 — verify before relying)

---

## 1. How to read and use an entry

| Field | Meaning |
|---|---|
| Lineage | Ancestors, with developer and year where well established |
| Preserved | Relations kept from the source (the chassis) |
| Changed | Relations added, removed or inverted (the twist) |
| Why (interpretation) | A design reading of why it worked or failed; not a causal proof |
| Operators | OP codes from `references/transformation-operators.md`; S/C/A/M/P/E/R are SCAMPER letters |
| Rule | A transferable statement at relation level, usable in `concept.comparables[].borrow/change` |

Use entries three ways: (1) as precedent for a proposed borrowing (find a lineage that made the same move); (2) as calibration for the AFS (did the historical mapping preserve the higher-order relations?); (3) as counterexamples (section 9) before committing to an IP or a fusion.

---

## 2. Index of the 50 lineages

| # | Result | Main sources | Key operators | Outcome |
|---|---|---|---|---|
| W01 | Candy Crush Saga | Bejeweled, King's saga format | OP14, OP11, A | Worked |
| W02 | Farm Heroes Saga | Candy Crush Saga | OP02 | Worked (sibling) |
| W03 | Toon Blast | Toy Blast, collapse puzzles | OP11, OP12 | Worked |
| W04 | Gardenscapes / Homescapes | Match-3, Playrix hidden-object brand | OP14, OP30 | Worked |
| W05 | Royal Match | Toon Blast / Homescapes chassis | OP08, OP30 (unwrap) | Worked |
| W06 | 1010! | Tetris | OP03, E | Worked |
| W07 | Block Blast! | 1010!, Woodoku-style grids | execution, OP28 | Worked |
| W08 | 2048 | Threes!, 1024 | OP08, OP02 | Worked (clone beat original commercially) |
| W09 | Merge Dragons! → Merge Mansion | Triple Town | OP31, OP14, OP30 | Worked |
| W10 | Puzzle & Dragons | Match-3, monster-collection RPG, gacha | OP07, OP12, OP32 | Worked |
| W11 | Wordle | Mastermind, Jotto, Lingo | OP23, OP11, OP09 | Worked |
| W12 | Monument Valley | Escher's impossible figures | far analogy, OP03 | Worked |
| W13 | Coin Master | Slot machines, village builders | OP13, OP11, OP29 | Worked (ethically contested) |
| W14 | Monopoly Go! | Coin Master, Monopoly IP | OP02, OP13, OP29 | Worked |
| W15 | Hay Day | FarmVille | OP13, OP11, OP10 | Worked |
| W16 | Stardew Valley | Harvest Moon | M (deepen), OP29 | Worked |
| W17 | Neko Atsume | Tamagotchi, virtual pets | OP16, OP29, OP03 | Worked |
| W18 | AdVenture Capitalist | Cookie Clicker | OP16, OP25 | Worked |
| W19 | Temple Run → Subway Surfers | Canabalt | OP10, OP02 (live-ops) | Worked |
| W20 | Crossy Road | Frogger | OP28, OP29 | Worked |
| W21 | Angry Birds | Crush the Castle | OP12, OP10 | Worked |
| W22 | Archero | Twin-stick roguelites | OP03, OP10, OP15 | Worked |
| W23 | Vampire Survivors | Bullet hell, Magic Survival | OP03, OP04, M | Worked |
| W24 | Survivor.io | Vampire Survivors, Archero meta | OP10, OP14 | Worked |
| W25 | Slay the Spire | Dominion-style deck-building, roguelikes | OP07, OP15, OP19 | Worked |
| W26 | Balatro | Poker, roguelite deck-builders | OP01, OP15, OP13 | Worked |
| W27 | slither.io → Hole.io | agar.io, Katamari Damacy | OP12, OP05 | Worked |
| W28 | Clash of Clans | Backyard Monsters | OP10, OP11 | Worked |
| W29 | Clash Royale | Tower defense, CCG, MOBA lanes | OP07, OP06, OP17 | Worked |
| W30 | Brawl Stars | MOBA, hero shooter, battle royale | OP08, OP17, OP10 | Worked (after a long soft launch) |
| W31 | Hearthstone | Magic: The Gathering | OP08, OP20 | Worked |
| W32 | Marvel Snap | Hearthstone-style CCG, poker | OP08, OP17, OP18 | Worked |
| W33 | Artifact | Dota 2 lanes, Magic-style CCG | OP07 | Failed |
| W34 | Pokémon TCG Pocket | Pokémon TCG | OP08, OP23, OP29 | Worked |
| W35 | Auto Chess → TFT | Dota 2 custom map, drafting, set merging | OP25, OP26 | Worked |
| W36 | Rush Royale | Random Dice, tower defense | OP31, OP07 | Worked |
| W37 | PUBG Mobile / Free Fire | PC battle royale | OP10, OP17 | Worked |
| W38 | Fall Guys → Stumble Guys | Game shows, battle royale | OP09, OP10 | Worked |
| W39 | DotA → the MOBA genre | Warcraft III custom map | OP26, OP27 | Worked (genre-defining) |
| W40 | Among Us | Mafia / Werewolf | OP22, OP10 | Worked |
| W41 | Pokémon GO | Ingress, Pokémon IP | OP02, OP24 | Worked |
| W42 | Wizards Unite, Minecraft Earth | Pokémon GO formula, IP swap | OP02 | Failed |
| W43 | Words With Friends | Scrabble | OP11, OP06 (async) | Worked |
| W44 | Duolingo streaks and leagues | Game leaderboards and leagues | OP09 (reverse), OP11 | Worked (games → non-game) |
| W45 | Zombies, Run! | Running, audio drama | OP24, OP30 | Worked (niche) |
| W46 | Pokémon Sleep | Sleep tracking, Pokémon IP | OP24, OP29 | Worked (niche, verify) |
| W47 | Plague Inc. | Epidemiology, Pandemic 2 | OP04, far analogy | Worked |
| W48 | Mini Metro | Transit maps, network logistics | far analogy, OP08 | Worked |
| W49 | Flight Control | Air traffic control | far analogy, OP12 | Worked |
| W50 | Hitman GO | Hitman stealth action, board-game dioramas | OP32, OP06 | Worked |

---

## 3. Match, puzzle and word lineages

### W01 Candy Crush Saga (King, 2012) ← Bejeweled + King's saga format
- **Lineage**: swap-to-match games such as Shariki (1994) → Bejeweled (PopCap, 2001) → King's web Candy Crush → Candy Crush Saga on Facebook (2012) and mobile (late 2012). The "Saga" map format appeared in earlier King titles (Bubble Witch Saga, 2011).
- **Preserved**: swap two adjacent tiles; 3+ in a line clear; cascades; special pieces from larger matches.
- **Changed**: endless score play became hundreds of authored levels with goals (score, jelly, ingredients) and move limits; a linear map with friends' avatars; lives that regenerate; episode gates; boosters and extra moves sold at the fail moment.
- **Why (interpretation)**: move limits turned a relaxed toy into short, tense, finishable episodes; the map made progress visible and social; lives created natural session ends that suited phones.
- **Operators**: OP14 (saga meta), OP11 (friends on map, gifting), A (saga format adapted from sibling games), OP17 (episodes).
- **Rule**: give an endless toy *discrete goals with a scarce action budget* and a visible path; the fail moment becomes both the tension peak and the spend moment (guard it ethically).

### W02 Farm Heroes Saga (King, 2013–14) ← Candy Crush Saga
- **Lineage**: King's own chassis re-themed.
- **Preserved**: swap match-3, saga map, lives, boosters, move limits.
- **Changed**: farm theme; the primary goal type became collecting target counts of specific crop pieces, which shifts attention from specials to colour management.
- **Why (interpretation)**: a sibling that reused a proven pipeline while giving a different goal emphasis, so it complemented rather than cannibalised the parent.
- **Operators**: OP02, with a small goal-type change.
- **Rule**: a theme swap inside your own portfolio needs at least one goal-level change to justify a second product.

### W03 Toon Blast (Peak, 2017) ← Toy Blast (Peak, 2015) ← collapse puzzles
- **Lineage**: SameGame-style "tap a group to collapse" puzzles → Toy Blast → Toon Blast.
- **Preserved**: tap a group of 2+ same-coloured cubes to clear; gravity refill; specials from large groups; level goals.
- **Changed**: from Toy Blast to Toon Blast, teams became central (team chat, lives requests, team events); cartoon characters and a brighter identity.
- **Why (interpretation)**: tapping a group is easier than swapping for a broad audience; teams added obligation and belonging, raising long-term retention.
- **Operators**: OP12 (tap instead of swap, inherited from the collapse family), OP11 (teams).
- **Rule**: lower the input skill floor first, then retain with a social layer that feeds the core economy (lives).

### W04 Gardenscapes: New Acres (2016) and Homescapes (2017) (Playrix) ← match-3 + Playrix's earlier "Scapes" brand
- **Lineage**: Playrix's Gardenscapes (2009) was a hidden-object game; the mobile titles reused the brand and butler character with a match-3 core.
- **Preserved**: swap match-3 levels with goals and move limits.
- **Changed**: stars from wins are spent on renovation tasks inside a story told through short dialogue; the house or garden visibly transforms.
- **Why (interpretation)**: a low-skill meta gave progress even after losses and gave the core a reason beyond the next level; the narrative supplied curiosity hooks. Playrix also became a cautionary example for ad creatives that did not show the real game (see `game-case-studies`).
- **Operators**: OP14 (renovation meta), OP30 (narrative wrap).
- **Rule**: a *bridge currency* (one star per win) that is the only input to visible permanent change ties every core session to the meta.

### W05 Royal Match (Dream Games, 2021) ← Toon Blast / Homescapes chassis
- **Lineage**: founders came from Peak Games (Toon Blast); the game combines a swap match-3 core with a renovation meta of the Homescapes type.
- **Preserved**: match-3 goals and specials; star-priced renovation tasks; lives; teams; events.
- **Changed**: a trimmed meta with a mascot (King Robert) and little dialogue; one tap from castle to level (no map to navigate); fast animations; coins as the single purchasable currency; a win-streak bonus (Butler's Gift).
- **Why (interpretation)**: it competed on execution in a consolidated genre: less friction between levels, legible single-currency pricing, and a streak that softened early failure. See `game-case-studies` (Royal Match) for detail.
- **Operators**: OP08 (subtraction of meta friction), OP30 (narrative unwrap), OP01 (streak bonus).
- **Rule**: in a consolidated genre, a second mover can win by *subtracting friction* from the leader's loop rather than adding features, if it has the production quality and UA budget to compete.

### W06 1010! (Gram Games, 2014) ← Tetris (Alexey Pajitnov, 1984)
- **Lineage**: falling polyomino puzzle → placement puzzle.
- **Preserved**: polyomino pieces; clearing full lines.
- **Changed**: no gravity and no falling timer; pieces are placed anywhere on a 10×10 grid; rows **and** columns clear; three pieces are offered at a time; the game ends when nothing fits.
- **Why (interpretation)**: removing time pressure turned a reflex game into a calm planning game that suits any moment and any age; three-piece trays create look-ahead decisions.
- **Operators**: OP03 (constraint inversion: remove gravity and timer), E (eliminate), OP20 (input randomness via the tray).
- **Rule**: removing the time constraint from a reflex game moves skill to planning and widens the audience; add look-ahead so planning has material.

### W07 Block Blast! (Hungry Studio, around 2022) ← 1010! and Woodoku-style grids
- **Lineage**: 1010! → Sudoku-grid variants (Woodoku, Blockudoku, late 2010s) → Block Blast!.
- **Preserved**: three-piece tray, free placement, row/column clears, no gravity.
- **Changed**: an 8×8 grid, heavy juice and combo feedback, an adventure mode with collection goals (verify current modes), and an ad-led model built on long calm sessions.
- **Why (interpretation)**: an execution-and-distribution winner, not a mechanical first (see `game-case-studies`). The systemic core needs no level authoring, so it scales cheaply. It topped worldwide downloads in H1 2026 (section 11).
- **Operators**: OP28 (systemic content), M (feedback magnified), OP14 (light adventure meta).
- **Rule**: a commodity mechanic can still win through tuning, feedback and distribution; the content cost of a systemic core is near zero.

### W08 2048 (Gabriele Cirulli, 2014) ← Threes! (Sirvo, 2014) via 1024
- **Lineage**: Threes! (Asher Vollmer, Greg Wohlwend and team, premium, early 2014) → 1024 (Veewo) → 2048 (free, open source, weeks later). The Threes! team publicly documented their long development and their reaction to the clones.
- **Preserved**: slide all tiles in a direction; merge to grow numbers on a 4×4 grid.
- **Changed**: simpler merge rule (equal powers of two); tiles slide fully; free on the web; no character art.
- **Why (interpretation)**: simplicity and zero price spread it virally. Many players and designers consider Threes! the deeper design, which shows that depth does not protect a premium game from a simpler free derivative.
- **Operators**: OP08 (subtraction), price change (premium → free).
- **Rule**: if a rule is easy to copy, plan distribution, price and platform reach as part of the design, not after it.

### W09 Merge Dragons! (Gram Games, 2017) → Merge Mansion (Metacore, 2020) ← Triple Town (Spry Fox, 2010)
- **Lineage**: Triple Town (match 3 adjacent items to evolve them on a small grid) → Merge Dragons! (merge 3, or 5 for a bonus, on an open map with dragons that harvest) → merge-2 games with orders and story (Merge Mansion, Travel Town).
- **Preserved**: identical items combine into the next tier; board space as the pressure.
- **Changed**: open boards, generators that produce tier-1 items, merge-2 for speed, order boards that turn merging into goals, a renovation mystery story, energy on generators.
- **Why (interpretation)**: merging is a satisfying toy with visible power growth; orders and story supplied direction and the IAP spend moment (energy).
- **Operators**: OP31 (merge), OP14 (orders, renovation), OP30 (story wrap).
- **Rule**: an open-ended toy needs an *order board* (explicit demand) to become a goal loop.

### W10 Puzzle & Dragons (GungHo, 2012) ← match-3 + monster-collection RPG + gacha
- **Lineage**: match-3 boards + party RPG + capsule-machine monetization.
- **Preserved**: colour matching; monster collection and evolution; dungeons.
- **Changed**: the verb became dragging one orb freely across the board for a few seconds, swapping with everything it passes; matches deal damage by colour through the team's monsters.
- **Why (interpretation)**: puzzle skill became combat power, and the collection meta added long-term goals and a gacha spend loop. It set the template for puzzle-RPG hybrids (Empires & Puzzles later).
- **Operators**: OP07 (fusion), OP12 (verb swap), OP32 (puzzle-ification of combat), OP29 (collection).
- **Rule**: when a puzzle resolves combat, map puzzle outputs to combat inputs one-to-one (colour → element → damage), and bound how much collected power overrides puzzle skill.

### W11 Wordle (Josh Wardle, 2021) ← Mastermind (1970), Jotto (1955), Lingo
- **Lineage**: code-breaking with per-position feedback (Mastermind), word guessing with letter feedback (Jotto, the Lingo game show) → Wordle. The New York Times acquired it in early 2022.
- **Preserved**: guess, receive feedback (right letter right place / right letter wrong place / absent), deduce.
- **Changed**: one puzzle per day, the same for everyone; six guesses; a spoiler-free emoji grid to share; a web page with no ads or accounts at launch.
- **Why (interpretation)**: shared daily scarcity created conversation; the grid was a social object that showed effort without spoiling the answer; the format suited non-gamers' daily habits.
- **Operators**: OP23 (ritualization), OP11 (share), OP09 (non-gamer audience).
- **Rule**: a *shared deterministic daily puzzle* plus a *spoiler-free result artefact* turns a solo puzzle into a social ritual.

### W12 Monument Valley (ustwo games, 2014) ← impossible figures in M. C. Escher's art
- **Lineage**: a far analogy from visual art (impossible architecture and perspective tricks) into an isometric puzzle.
- **Preserved**: the visual paradox: paths that connect only from a certain viewpoint.
- **Changed**: the paradox became the rule: rotate or slide the architecture until an impossible path connects, then walk the character through.
- **Why (interpretation)**: a far source produced a mechanic no genre competitor had; low failure pressure and short length suited a premium, art-led audience.
- **Operators**: far analogy (art → rules), OP03 (failure pressure largely removed).
- **Rule**: when a far source supplies a *rule* (not just a look), the result can be both novel and readable; keep the experience short and authored.

---

## 4. Casual-social, farming, pet and idle lineages

### W13 Coin Master (Moon Active; released 2016 per Wikipedia, mobile breakout in 2018–2019) ← slot machines + village builders + social raids
- **Lineage**: the slot reel as a chance device, a build-to-progress village meta, Facebook-era social attack loops.
- **Preserved**: spin → outcome table (coins, attacks, raids, shields); build sinks for coins.
- **Changed**: spins are the energy unit and regenerate over time; outcomes target friends' villages (attack a building, raid a stash); villages and themed card sets give long-term goals; events multiply rewards.
- **Why (interpretation)**: the loop is short, legible and social, with strong variable-ratio reinforcement. It is also a frequent example in debates about gambling-like design (see `game-case-studies` ethical-risk precedents).
- **Operators**: OP13 (slot as energy-to-outcome converter), OP11 (raids), OP29 (card sets).
- **Rule**: an energy-gated chance device whose outcomes are *social actions* creates reasons to return and to invite; it also inherits gambling scrutiny, so disclose odds and protect minors.

### W14 Monopoly Go! (Scopely, 2023) ← Coin Master + the Monopoly IP (Hasbro)
- **Lineage**: widely described as Coin Master's loop with a board-game IP and a dice board.
- **Preserved**: energy-gated chance device; attack and raid other players; build sinks per board; sticker albums with trading; frequent events and tournaments.
- **Changed**: slot spins → dice rolls and movement around a Monopoly board; tiles as the outcome table; landmarks per board as the build sink; railroad tiles trigger the attack and heist mini-games; roll multipliers act as a bet size.
- **Why (interpretation)**: the IP is itself a dice-and-board loop, so the blend is unusually coherent (the inputs share structure, not just a brand); the IP widened the audience beyond the source's.
- **Operators**: OP02 (IP theme), OP13 (economy re-skin), OP29 (albums), OP18 (multipliers; watch spending acceleration).
- **Rule**: choose an IP whose *own rules* express the borrowed loop (dice → movement → outcomes); the IP then teaches the loop for free.

### W15 Hay Day (Supercell, 2012) ← FarmVille (Zynga, 2009)
- **Lineage**: social farming on Facebook → mobile-first farming.
- **Preserved**: plant, wait, harvest; expanding a farm; decorating; friends.
- **Changed**: production chains (crops → feed → animal products → goods); truck and boat order boards that turn production into goals; a roadside shop where players buy from each other; crops that do not wither (commonly noted as a contrast with FarmVille); touch-native drag-to-plant.
- **Why (interpretation)**: orders gave the open sandbox direction; player trading created a social economy; removing withering removed punishment for absence, which suits phones.
- **Operators**: OP13 (economy re-skin with converters and orders), OP11 (trading), OP10 (mobile-native input), E (no withering).
- **Rule**: absence should cost opportunity, never destroy progress; order boards convert a production sandbox into a goal loop.

### W16 Stardew Valley (ConcernedApe, 2016; mobile 2018–19) ← Harvest Moon (1996)
- **Lineage**: the developer has cited Harvest Moon as the main inspiration.
- **Preserved**: inheriting a farm; seasons and days; crops and animals; villagers and relationships.
- **Changed**: much broader systems (mining with combat, fishing, crafting, foraging); the community centre's bundles as a set-collection goal structure; a museum collection; deep player expression.
- **Why (interpretation)**: it kept the comfort fantasy and added depth and goals across many systems; bundles gave players a checklist that ties every system together.
- **Operators**: M (magnify depth), OP29 (bundles and museum as collection graft).
- **Rule**: a cosy sandbox needs a *cross-system collection goal* that makes every activity count toward one visible target.

### W17 Neko Atsume (Hit-Point, 2014) ← Tamagotchi (Bandai, 1996) and virtual pets
- **Lineage**: care-for-a-creature toys → absence-driven collection.
- **Preserved**: caring for animals; checking in.
- **Changed**: no failure or neglect penalty; you place food and toys, close the app, and cats visit while you are away; a photo album collects visitors; rare cats like specific toys.
- **Why (interpretation)**: it turned the check-in ritual into pure anticipation with no guilt; collection and discovery supplied goals.
- **Operators**: OP16 (absence-driven accumulation), OP29 (album), OP03 (care failure removed).
- **Rule**: an absence loop works best when absence creates *surprise* (what came while I was away?) rather than *loss*.

### W18 AdVenture Capitalist (Hyper Hippo, 2014) ← Cookie Clicker (Orteil, 2013)
- **Lineage**: incremental games popularised on the web → mobile and Steam idle tycoon.
- **Preserved**: exponential cost growth; buildings that produce currency; big numbers.
- **Changed**: managers automate each business (the click becomes optional); angel investors are a prestige currency earned by resetting, giving a permanent multiplier; satirical capitalist theme; offline earnings.
- **Why (interpretation)**: automation made it phone-friendly (progress without tapping); prestige gave a reason to restart and a long tail.
- **Operators**: OP16 (idle-ification), OP25 (automation via managers).
- **Rule**: an idle loop needs a prestige reset that converts accumulated progress into a permanent multiplier, or it ends when the curve flattens.

---

## 5. Action, arcade, roguelite and io lineages

### W19 Temple Run (Imangi, 2011) → Subway Surfers (Kiloo and SYBO, 2012) ← Canabalt (2009)
- **Lineage**: one-button 2D endless runner → 3D behind-the-character runner with swipe controls → lane-based urban runner.
- **Preserved**: endless forward motion; obstacles; distance score; instant restart.
- **Changed**: swipe gestures (turn, jump, slide), tilt to collect coins, a 3D chase camera (Temple Run); three lanes, a hoverboard, characters and boards to collect, and "World Tour" updates that re-theme the city periodically (Subway Surfers).
- **Why (interpretation)**: swipes are native to touch and readable at a glance; periodic theme swaps renewed content without new mechanics.
- **Operators**: OP10 (touch-native gestures), OP02 (live-ops theme swap), OP29 (characters).
- **Rule**: a live game can refresh through rotating *themes* on a stable chassis when the core verb is evergreen.

### W20 Crossy Road (Hipster Whale, 2014) ← Frogger (Konami, 1981)
- **Lineage**: lane-crossing arcade game → endless mobile version.
- **Preserved**: cross lanes of traffic and rivers; timing.
- **Changed**: endless procedurally assembled lanes; voxel art; a large roster of collectible characters (some changing the world's look); opt-in rewarded ads at desire moments; a prize machine for characters.
- **Why (interpretation)**: an instantly legible verb (tap to hop) with collection on top; optional rewarded ads were widely praised as player-friendly.
- **Operators**: OP28 (procedural lanes), OP29 (characters), OP10 (one tap).
- **Rule**: place ads where the player *wants* something (opt-in reward), not where they are interrupted.

### W21 Angry Birds (Rovio, 2009) ← Crush the Castle (Armor Games, 2009) and projectile-physics games
- **Lineage**: a widely noted similarity to the Flash game Crush the Castle (launch projectiles to topple structures).
- **Preserved**: physics structures, projectile trajectory, destruction.
- **Changed**: a pull-and-release slingshot drag native to touch; characters with distinct abilities (split, speed, bomb); star ratings per level; strong character IP.
- **Why (interpretation)**: the slingshot is a perfect touch verb (the drag *is* the aim); bird types turned physics into choices; characters made it a brand.
- **Operators**: OP12 (verb swap to slingshot drag), OP10 (touch-native).
- **Rule**: when porting a mouse verb to touch, find a gesture whose physical metaphor *is* the action.

### W22 Archero (Habby, 2019) ← twin-stick roguelites (e.g. The Binding of Isaac, 2011)
- **Lineage**: room-based twin-stick shooters with item builds → one-thumb mobile.
- **Preserved**: rooms, enemies with bullet patterns, ability builds, bosses.
- **Changed**: one control: moving dodges; stopping auto-fires at the nearest enemy; a three-option ability draft on each level-up; permanent gear, talents and chapters; energy per run.
- **Why (interpretation)**: it compressed two sticks into one thumb by making "stop" the attack input, which keeps a dodge-or-attack decision; the draft gave run variety.
- **Operators**: OP03 (constraint inversion: no shooting while moving), OP10 (one thumb, portrait), OP15 (run drafts), OP14 (gear meta).
- **Rule**: when you remove an input, turn the remaining input's *absence* into a decision (move = defend, stop = attack).

### W23 Vampire Survivors (poncle, 2021–22) ← bullet hell (inverted) and Magic Survival
- **Lineage**: the developer has cited the mobile game Magic Survival as an inspiration; the design is widely read as an inversion of bullet hell.
- **Preserved**: dense screens of projectiles and enemies; dodging through crowds.
- **Changed**: the player never aims or shoots: weapons fire automatically; hundreds of enemies are the "bullets"; the only verbs are movement and the level-up draft; weapon evolutions reward combinations; low price on PC, and a free mobile version followed (verify details).
- **Why (interpretation)**: removing aiming freed attention for positioning and build-crafting; constant power escalation produced a strong power fantasy; it created the survivor-like genre.
- **Operators**: OP03 (remove aiming), OP04 (the player becomes the bullet source), M (magnify enemy count), OP15 (drafts).
- **Rule**: a constraint inversion can create a genre when the freed attention goes into a richer decision (positioning plus builds).

### W24 Survivor.io (Habby, 2022) ← Vampire Survivors + Archero's meta
- **Lineage**: survivor-like rules, mobile-ized by the studio behind Archero.
- **Preserved**: auto-attacks, hordes, level-up drafts, weapon evolutions.
- **Changed**: portrait one-thumb; chapter structure; energy; gear with rarities and merging; talents; idle patrol rewards; a free-to-play economy.
- **Why (interpretation)**: it fast-followed an emerging PC trend with mobile-native controls and a proven F2P meta from the same studio.
- **Operators**: OP10 (platform), OP14 (meta graft).
- **Rule**: an emerging PC/indie rule with no mobile incumbent is a fast-follow window; bring a proven meta with you (`game-case-studies` procedure D).

### W25 Slay the Spire (Mega Crit, 2017–19; mobile ports 2020–21) ← deck-building + roguelikes
- **Lineage**: deck-building popularised by the board game Dominion (Donald X. Vaccarino, 2008) combined with roguelike run structure.
- **Preserved**: start with a weak deck, add cards, thin the deck; permadeath runs.
- **Changed**: single-player combat against enemies whose **intents are shown**; a branching map with risk choices (elites, shops, events); relics that change rules.
- **Why (interpretation)**: intents turned each turn into a solvable puzzle with visible stakes; the map added macro decisions; runs gave replayability.
- **Operators**: OP07 (fusion), OP15 (roguelite), OP19 (information shift: intents).
- **Rule**: telegraphing the opponent's next move converts randomness into planning and makes losses feel fair.

### W26 Balatro (LocalThunk, published by Playstack, 2024; mobile later in 2024) ← poker + roguelite deck-builders
- **Lineage**: poker hand rankings and a standard deck, with roguelite structure. As reported on [Wikipedia's Balatro article](https://en.wikipedia.org/wiki/Balatro), the project began as an online version of the Cantonese card game Big Two and became a single-player roguelike deckbuilder after the developer watched Northernlion stream *Luck Be a Landlord*; he played *Slay the Spire* near the end of development to understand its controls. These are the developer's stated inspirations as relayed by that article (grade B), not a primary interview.
- **Preserved**: poker hands and their ranking; a 52-card deck.
- **Changed**: hands score chips × mult; jokers modify scoring rules; blinds are score targets that escalate by ante; a shop between rounds; deck modification (tarot, planet cards).
- **Why (interpretation)**: universally known rules lowered the learning cost to near zero while the joker system created explosive, discoverable combinations; it monetized as a premium game.
- **Operators**: OP01 (poker scoring transplanted), OP15 (roguelite), OP13 (multiplier economy).
- **Rule**: a *familiar ruleset* plus a rule-bending modifier system gives depth without a tutorial burden.

### W27 slither.io (2016) → Hole.io (Voodoo, 2018) ← agar.io (2015) and Katamari Damacy (2004)
- **Lineage**: browser "io" arenas where you grow by eating smaller players (agar.io) → snake variant (slither.io) → a hole that swallows a city, growing as it goes (Hole.io), widely compared to Katamari's grow-by-consumption.
- **Preserved**: grow by consuming; size as power and as vulnerability; short rounds.
- **Changed**: verbs and themes (snake trails that kill on contact; a hole that swallows objects); timed rounds of a couple of minutes; bots filling the arena (common in hyper-casual io games).
- **Why (interpretation)**: the growth fantasy is instantly readable in a 3-second ad; rounds are short and replayable.
- **Operators**: OP12 (verb swap), OP05 (scale growth as the loop), OP17 (short rounds).
- **Rule**: growth you can *see* (size on screen) is one of the most ad-legible progressions; pair it with a short fixed round.

---

## 6. Strategy, card and PvP lineages

### W28 Clash of Clans (Supercell, 2012) ← Backyard Monsters (Kixeye, 2011)
- **Lineage**: Facebook base-building with asynchronous raids; the similarity to Backyard Monsters is widely noted.
- **Preserved**: build a base; train troops; attack other players' AI-defended bases; loot resources.
- **Changed**: touch-native deployment (tap to drop troops); builder timers and gem speed-ups; shields after being attacked; clans with troop donation and later clan wars; high production polish.
- **Why (interpretation)**: async raids give PvP excitement without real-time netcode; clans added obligation and cooperation; timers fit phone check-in rhythms.
- **Operators**: OP10 (mobile-native), OP11 (clans, donation).
- **Rule**: asynchronous PvP against a player's *designed* defence gives social conflict with single-player latency tolerance.

### W29 Clash Royale (Supercell, 2016) ← tower defense + collectible card game + MOBA lanes
- **Lineage**: widely described as a fusion of the three.
- **Preserved**: towers that defend (TD); a deck of collectible cards with costs (CCG); two lanes and destructible towers with a king tower (MOBA).
- **Changed**: real-time deployment paid with regenerating elixir; an 8-card deck with a 4-card hand; 3-minute matches with overtime; chests on timers as the reward loop at launch (the reward system has since been reworked; verify current); card upgrades through duplicates.
- **Why (interpretation)**: each input contributes a relation: deck constraint (CCG), spatial counterplay (TD), lane pressure (MOBA). The elixir clock made card timing the skill. Short matches fit phones.
- **Operators**: OP07 (fusion), OP06 (turn-based cards → real-time), OP17 (session compression), OP29 (card collection).
- **Rule**: a three-way fusion can work when each input contributes a *distinct relation* to one core verb (deploy a card), not a separate mode.

### W30 Brawl Stars (Supercell; soft launch 2017, global 2018) ← MOBA, hero shooter and battle royale modes
- **Lineage**: hero-based team shooter with rotating modes (gem grab, showdown battle royale, others).
- **Preserved**: heroes with distinct roles and supers; team objectives; battle royale elimination in one mode.
- **Changed**: matches of a few minutes; simplified twin-stick controls with auto-aim tap; no item builds; rotating mode schedule. During its long soft launch, the game reportedly moved from portrait to landscape controls.
- **Why (interpretation)**: very short, varied matches; heroes as the collection meta. The long soft launch shows that a fusion can need many iterations before it fits phones.
- **Operators**: OP08 (subtraction), OP17 (compression), OP10 (platform; orientation decided by control scheme).
- **Rule**: orientation follows the control scheme; test it in soft launch, and be willing to change it.

### W31 Hearthstone (Blizzard, 2014) ← Magic: The Gathering (Richard Garfield, 1993)
- **Lineage**: physical collectible card game → digital-native CCG.
- **Preserved**: decks built from a collection; creatures and spells; mana costs; hero health as the win condition.
- **Changed**: mana grows automatically each turn (no land cards, so no mana screw from the deck); little interaction during the opponent's turn (secrets aside); hero powers; digital-only effects (random generation, discover, transformation); 30-card decks; free-to-play packs.
- **Why (interpretation)**: removing land and instant-speed responses cut complexity and dead turns; digital randomness added spectacle; the Warcraft IP brought an audience.
- **Operators**: OP08 (subtraction), OP20 (randomness relocation: removed mana randomness, added digital effect randomness).
- **Rule**: automate the *resource* step that causes non-games (mana screw), then spend the saved complexity on spectacle.

### W32 Marvel Snap (Second Dinner, 2022) ← Hearthstone-style CCG + poker-style raising
- **Lineage**: designed by a team led by a former Hearthstone game director; it adds a wager layer from poker.
- **Preserved**: collectible cards with costs and power; deck building.
- **Changed**: 12-card decks; 6 turns; 3 randomly revealed locations with rule-changing effects; simultaneous reveals; cube stakes that a player can double ("snap") and an option to retreat at the current stake; games of about 3 minutes.
- **Why (interpretation)**: very short games fit phones; locations created variety from a tiny deck; the snap made bluffing and risk management part of ranked play and cut the cost of bad matchups (retreat).
- **Operators**: OP08 (subtraction), OP17 (compression), OP18 (stakes injection), OP20 (random locations as input randomness).
- **Rule**: a wager layer on a short match turns *every* game into a decision about confidence; pair it with a cheap exit.

### W33 Artifact (Valve, 2018) — a failed fusion
- **Lineage**: a CCG co-designed by Richard Garfield, built on Dota 2's three lanes and heroes.
- **Preserved**: Dota's three lanes, heroes and items; CCG deck building.
- **Changed**: three simultaneous boards (one per lane); a paid entry price plus paid packs and a Steam market for cards.
- **Outcome**: the player base fell quickly after launch; Valve paused, attempted a rework, ended development in 2021 and made the game free.
- **Why it failed (interpretation)**: the fusion *multiplied* complexity (three boards at once) instead of subtracting it, and the monetization stacked a price, packs and a market in an era when free-to-play CCGs set expectations. Compare W31 and W32, which both subtracted.
- **Operators**: OP07 (fusion without subtraction).
- **Rule**: fusing a complex game into a complex genre needs aggressive subtraction; check that the business model matches genre expectations.

### W34 Pokémon TCG Pocket (Creatures and DeNA, 2024) ← the Pokémon Trading Card Game
- **Lineage**: physical TCG → mobile-first collection game.
- **Preserved**: Pokémon cards, types, evolutions, battles, pack opening.
- **Changed**: free packs every day on a timer; 20-card decks and a 3-point win (versus 60-card decks and 6 prize cards in the physical game); energy generated automatically instead of energy cards; "Wonder Pick" to pick from others' opened packs; emphasis on card art and the opening ritual.
- **Why (interpretation)**: it made pack opening a daily ritual and simplified battles the way Hearthstone simplified Magic (automating the resource). Collection, not competition, leads.
- **Operators**: OP08 (subtraction, resource automation), OP23 (daily ritual), OP29 (collection).
- **Rule**: if the audience loves the *ritual* of a physical hobby (opening packs), design the daily loop around the ritual and simplify the competitive layer.

### W35 Auto Chess (Drodo Studio, 2019) → Teamfight Tactics and Dota Underlords ← a Dota 2 custom map
- **Lineage**: a user-made Dota 2 mod → standalone games from Riot and Valve within months, plus a mobile Auto Chess.
- **Preserved**: heroes and synergies from the parent games' worlds.
- **Changed**: combat is automatic; decisions are drafting from a shared pool, combining three copies to upgrade, managing economy (interest) and positioning on a board.
- **Why (interpretation)**: automation moved skill to planning, making matches watchable and playable on phones; the shared pool created player interaction without direct control.
- **Operators**: OP25 (automation shift), OP26 (mode extraction from UGC), OP31 (three copies merge to upgrade).
- **Rule**: watch your community's custom modes; a mode that outperforms its host can be a genre.

### W36 Rush Royale (MY.GAMES studio, 2020) ← Random Dice (111%, 2019) and tower defense
- **Lineage**: widely compared to Random Dice's merge tower defense.
- **Preserved**: units spawn randomly on a grid; merging two identical units creates a stronger random unit; PvP and co-op waves.
- **Changed**: a fantasy theme with distinct unit roles, heroes and talents; deeper upgrade meta.
- **Why (interpretation)**: merging under random spawns creates constant small decisions; PvP pressure adds stakes.
- **Operators**: OP31 (merge-ification), OP07 (TD fusion), OP02 (theme).
- **Rule**: merge-under-randomness is a compact decision engine for lane defence; the theme and meta differentiate within the lineage.

### W37 PUBG Mobile (2018) and Free Fire (Garena, 2017) ← PC battle royale
- **Lineage**: the PC battle royale wave (PUBG: Battlegrounds, 2017) → mobile versions.
- **Preserved**: drop, loot, shrinking zone, last one standing.
- **Changed**: Free Fire reduced the lobby to 50 players and matches to about 10 minutes and targeted low-end Android devices; mobile versions added aim assists and simplified looting.
- **Why (interpretation)**: matching device reality and session length opened markets where high-end phones were rare.
- **Operators**: OP10 (platform translation), OP17 (session compression).
- **Rule**: size the design for the *device tier* of the target market, not for flagship phones.

### W38 Fall Guys (Mediatonic, 2020) → Stumble Guys (Kitka Games, 2020–21) ← game shows + battle royale
- **Lineage**: physical-comedy game shows (the developers cited shows such as Takeshi's Castle and Total Wipeout) with battle royale elimination → a mobile-first take (Stumble Guys, by Finland's Kitka Games; Scopely announced the acquisition in September 2022, [Scopely](https://scopely.com/blog/welcome-stumble-guys-to-the-scopely-portfolio/)).
- **Preserved**: rounds of obstacle courses and mini-games; elimination to one winner; slapstick physics.
- **Changed** (Fall Guys from its sources): a non-violent battle royale for a broad audience. (Stumble Guys from Fall Guys): phones first, simpler controls, free-to-play.
- **Why (interpretation)**: a violent genre's structure became family-friendly; a different studio captured mobile before the original arrived there.
- **Operators**: OP09 (audience shift), OP10 (platform).
- **Rule**: if a hit is not on phones, the mobile window belongs to whoever ships a credible mobile-native version first.

### W39 Defense of the Ancients → the MOBA genre ← a Warcraft III custom map
- **Lineage**: a user-made Warcraft III map (early 2000s) → League of Legends (Riot, 2009), Dota 2 (Valve, 2013) → mobile MOBAs (for example Honor of Kings, Mobile Legends: Bang Bang).
- **Preserved**: three lanes, towers, creeps, heroes with levels and items.
- **Changed**: standalone clients, free-to-play models, matchmaking; mobile versions shortened matches and simplified controls.
- **Why (interpretation)**: the mod proved the loop with real players before any studio invested.
- **Operators**: OP26 (mode extraction), OP27 (player creation as the origin).
- **Rule**: user-generated modes are free market research; mine them.

---

## 7. Social deduction, location, real-world and cross-domain lineages

### W40 Among Us (Innersloth, 2018; breakout 2020) ← Mafia (Dimitry Davidoff, 1986) and Werewolf
- **Lineage**: the parlour game Mafia, later popularised as Werewolf → online social deduction.
- **Preserved**: a hidden minority eliminates the majority; discussion and voting.
- **Changed**: crewmates do tasks on a map (which creates alibis and evidence); emergency meetings and body reports trigger discussion; sabotage and vents; a cheap price on PC and free on mobile; cross-platform lobbies. The 2020 surge came from streamers.
- **Why (interpretation)**: tasks gave everyone something to do between discussions and produced evidence to argue about; the game is readable for viewers, so streams spread it.
- **Operators**: OP22 (asymmetric hidden roles), OP10 (cross-platform, phones).
- **Rule**: social deduction needs an *activity that generates evidence* between votes; otherwise discussion has nothing to work with.

### W41 Pokémon GO (Niantic with The Pokémon Company, 2016) ← Ingress (Niantic, 2012–13) + Pokémon
- **Lineage**: Ingress's crowd-sourced location data became the basis for PokéStops and gyms; a 2014 Google Maps April Fools' Pokémon challenge is often cited as a seed of the idea.
- **Preserved**: real-world locations as game nodes; walking as the movement input; team territory (gyms).
- **Changed**: the Pokémon IP and its collection structure; catching as the core verb; eggs hatched by walking distance.
- **Why (interpretation)**: Pokémon's core relation is *collecting distinct creatures found in different habitats*, which maps directly onto location-based exploration. The IP and the structure are the same shape.
- **Operators**: OP02 (IP), OP24 (real-world anchoring), OP29 (collection).
- **Rule**: an IP works on a borrowed structure when the IP's *own core relation* is that structure.

### W42 Harry Potter: Wizards Unite (2019, closed 2022) and Minecraft Earth (2019, closed 2021) — failed IP swaps
- **Lineage**: the Pokémon GO formula (location-based play) with other major IPs.
- **Preserved**: real-world map, walking, location nodes, collection.
- **Changed**: the IP and the collection objects (wizarding artefacts, building blocks).
- **Outcome**: both closed within about three years of launch (Minecraft Earth's closure was announced during the COVID-19 period, which suppressed outdoor play).
- **Why it failed (interpretation)**: neither IP's core relation is "collect distinct creatures found in places". Harry Potter is narrative and character-led; Minecraft is building and creativity. The mapping preserved the structure but not the purpose (Holyoak and Thagard's purpose constraint). External factors (pandemic, competition with Pokémon GO) also mattered.
- **Operators**: OP02 (IP swap without relational fit).
- **Rule**: before swapping an IP onto a structure, write the IP's core relation; if it differs from the structure's, the IP will feel like a skin.

### W43 Words With Friends (Newtoy, 2009) ← Scrabble
- **Lineage**: the crossword board game → asynchronous mobile play (Zynga acquired Newtoy in 2010).
- **Preserved**: tiles with letter values, a premium-square board, word building.
- **Changed**: asynchronous turns with push notifications; many simultaneous games; chat; a different board layout and tile values.
- **Why (interpretation)**: async turns let a slow, social game fit into gaps in the day; parallel games kept one waiting on someone always.
- **Operators**: OP11 (social), OP06 (time shift: synchronous → asynchronous).
- **Rule**: a slow turn-based game becomes a habit when turns are async and the player always has another game waiting.

### W44 Duolingo streaks and leagues (Duolingo; leagues first tested in 2018 per [Duolingo's blog](https://blog.duolingo.com/duolingo-leagues-leaderboards/)) ← game leaderboards and ranked leagues
- **Lineage**: a reverse analogy: game structures (XP, streaks, ranked leagues with promotion and demotion) moved into learning.
- **Preserved**: weekly competition in small groups; promotion and demotion; XP as the score; streaks.
- **Changed**: the activity is a lesson; streak protection items soften loss.
- **Why (interpretation)**: small leagues make rank achievable and social; streaks build a daily habit.
- **Operators**: OP09 (audience shift, in reverse), OP11 (social competition), OP23 (daily habit).
- **Rule**: weekly leagues of small cohorts with promotion and demotion keep competition achievable; borrow them back into games where global leaderboards are hopeless.

### W45 Zombies, Run! (Six to Start with Naomi Alderman, 2012) ← running + audio drama
- **Lineage**: a far analogy from fitness routines and radio drama.
- **Preserved**: a normal run; story episodes.
- **Changed**: the run becomes a mission; zombie chases ask you to speed up; supplies collected while running build a base.
- **Why (interpretation)**: it gave an existing habit a narrative reason and moments of tension.
- **Operators**: OP24 (real-world anchoring), OP30 (narrative wrap).
- **Rule**: wrap an existing habit in a story whose beats match the habit's natural rhythm (intervals → chases).

### W46 Pokémon Sleep (The Pokémon Company and Select Button, 2023) ← sleep tracking + Pokémon
- **Lineage**: sleep-tracking apps + creature research.
- **Preserved**: sleep measurement; Pokémon collection.
- **Changed**: sleep types determine which Pokémon appear; sleeping well becomes the progression input.
- **Why (interpretation)**: it anchors a once-a-day ritual to a beloved collection IP. Long-term retention data is not public; treat it as a niche precedent.
- **Operators**: OP24 (real-world anchoring), OP29 (collection), OP23 (daily ritual).
- **Rule**: a daily real-world ritual can be the *input*; the game should reward consistency without punishing bad nights.

### W47 Plague Inc. (Ndemic Creations, 2012) ← epidemiology and the Flash game Pandemic 2
- **Lineage**: the developer has cited the Flash game Pandemic 2 and the film Contagion as inspirations (reported; verify); the model is a simplified infection-spread simulation.
- **Preserved**: transmission, symptoms, lethality, cure research as a race.
- **Changed**: the player is the pathogen; evolution points buy traits; the world fights back with a cure.
- **Why (interpretation)**: the perspective flip made a grim system a strategic puzzle with a clear race against the cure.
- **Operators**: OP04 (perspective flip), far analogy (epidemiology).
- **Rule**: a real system with a clear race condition (spread vs cure) makes a strong strategy loop when the player takes the less obvious side.

### W48 Mini Metro (Dinosaur Polo Club, 2015) ← transit maps and network logistics
- **Lineage**: the visual language of schematic metro maps (the London Underground diagram tradition) and the logistics of passenger flow.
- **Preserved**: lines, stations, trains, passengers with destinations.
- **Changed**: stations appear over time; limited lines, carriages and tunnels force trade-offs; failure when a station overcrowds.
- **Why (interpretation)**: a familiar visual language explained itself; the real problem (growing demand, limited resources) is a natural difficulty curve.
- **Operators**: far analogy (logistics), OP08 (subtraction to the schematic).
- **Rule**: real systems with *growing demand against limited capacity* produce natural difficulty curves.

### W49 Flight Control (Firemint, 2009) ← air traffic control
- **Lineage**: a real-world system translated into a touch verb.
- **Preserved**: aircraft must land safely on matching runways without colliding.
- **Changed**: draw a path with a finger to route each aircraft; traffic accelerates until a collision.
- **Why (interpretation)**: drawing a path is native to touch and maps directly onto the real task (routing); early touch-screen phones rewarded it.
- **Operators**: far analogy (ATC), OP12 (verb: draw a path).
- **Rule**: look for real jobs whose core action is a gesture you can do on glass (route, sort, pour, stack).

### W50 Hitman GO (Square Enix Montreal, 2014) ← the Hitman stealth-action series + board-game dioramas
- **Lineage**: a real-time stealth-action franchise → a turn-based diorama puzzle with board-game pieces.
- **Preserved**: the assassination fantasy; guards with patrol patterns; disguises and distractions.
- **Changed**: node-based movement; turn-based; deterministic enemy patterns; levels as puzzles with optional goals.
- **Why (interpretation)**: it kept the franchise fantasy while translating reflex play into planning that suits touch and short sessions; it spawned a "GO" series.
- **Operators**: OP32 (puzzle-ification), OP06 (real-time → turn-based).
- **Rule**: a real-time franchise can reach mobile by keeping its *fantasy* and translating its *verbs* into a deterministic puzzle.

---

## 8. Cross-lineage patterns

| Pattern | Lineages | Statement |
|---|---|---|
| P1 Mobile-ization recipe | W22, W24, W37, W38 | Platform translation + session compression + a meta graft (OP10 + OP17 + OP14) is the standard path from PC/indie to mobile F2P |
| P2 Execution second movers | W05, W07, W24, W38 | In a known loop, the winner is often the one that removes friction, tunes feel, and distributes best, not the inventor |
| P3 Automate the resource | W31, W34, W18 | Remove the resource step that causes dead turns (lands, energy cards, clicking) and spend the saved complexity elsewhere |
| P4 Inversion creates genres | W06, W22, W23 | Removing a sacred constraint (gravity, aiming, shooting while moving) produces a new genre when the freed attention goes into a richer decision |
| P5 IP must fit relations | W14, W41 vs W42 | An IP works on a borrowed structure when its own core relation matches the structure |
| P6 UGC as market research | W35, W39 | Custom modes that outperform their host signal a genre |
| P7 Ritual plus share | W11, W34, W44 | A shared daily unit plus a social artefact turns solo play into conversation |
| P8 Copyable rules are weak moats | W08, W07 | When the rule is easy to copy, price, platform reach and execution decide |
| P9 Order boards give sandboxes goals | W09, W15 | Explicit demand converts open production into a goal loop |
| P10 Telegraph to make randomness fair | W25, W50, W31 (contrast) | Showing intent turns chance into planning |

---

## 9. Failure lessons

| Failure | Lineage | Structural cause (interpretation) | Check that would have caught it |
|---|---|---|---|
| Complexity multiplied | W33 Artifact | Fusion added boards instead of subtracting systems; business model stacked costs | Subtraction audit (OP08); business-model fit vs genre norms |
| IP without relational fit | W42 Wizards Unite, Minecraft Earth | IP's core relation was not the structure's | AFS purpose check; write the IP's core relation |
| Premium depth vs free simplicity | W08 Threes! vs 2048 | Easily copied rule, premium price | Moat analysis at concept time (`market-intel`) |
| Clone floods | Flappy Bird clones (see `game-case-studies`) | No twist; commodity mechanic without distribution edge | Market-gap step; clone-and-improve table in `game-case-studies` procedure D |
| Long soft launch to find fit | W30 Brawl Stars (survived), several soft-launched titles discontinued by large studios (reported) | Fusion did not fit phones at first | Kill criteria written before soft launch; orientation and control tests early |
| Ethically contested loops | W13 Coin Master | Variable-ratio chance device at the centre | Removal test and reflective-endorsement test (`design-theory`), odds disclosure |

---

## 10. Method: run a lineage study on any game

Use this to produce a new entry for this file or for a deconstruction's `innovations` and `borrow_for_us`.

1. **Find ancestors (30 min).** Search developer interviews, postmortems and talks for stated inspirations (evidence grade A); then widely reported comparisons (grade B); then community comparisons (grade C, label them).
2. **Abstract both sides** with the ontology template in `references/analogy-method.md` section 7.
3. **Diff the relations.** List preserved, added, removed and inverted relations. Name the operators.
4. **Context filter.** Era, channel, IP, audience, platform, studio capability (`game-case-studies` Core model 4).
5. **Write the "why" as interpretation**, citing at least one structural reason and one contextual reason.
6. **Find a counterexample**: a game that made the same move and failed. If none can be found, say so.
7. **Write the rule** at relation level and add the entry here or to `deconstruction.innovations` / `borrow_for_us`.

Template:

```
### Wnn <Result> (<developer>, <year>) <- <sources>
- Lineage:
- Preserved:
- Changed:
- Why (interpretation):
- Operators:
- Rule:
```

---

## 11. Volatile facts (as of Oct 2026 — verify before relying)

- Block Blast! topped worldwide mobile game downloads in H1 2026, in a period when mobile game IAP was about $40B (−2% year on year) and downloads about 24B (−12%). Source: [Mobilegamer.biz data digest of Sensor Tower H1 2026](https://mobilegamer.biz/data-digest-sensor-towers-h1-analysis-hay-days-comeback-julys-top-games-big-krafton-numbers-and-more/).
- Hybrid-casual spending grew 17.1% in 2025 ($3.5B → $4.2B), which supports the meta-graft pattern (P1). Source: same digest.
- Checked on 2026-10-20: Stumble Guys' developer and acquisition date ([Scopely](https://scopely.com/blog/welcome-stumble-guys-to-the-scopely-portfolio/), [PocketGamer.biz](https://www.pocketgamer.biz/scopely-acquires-stumble-guys-from-kitka-games)); Balatro's stated inspirations ([Wikipedia](https://en.wikipedia.org/wiki/Balatro)); Duolingo leagues ([Duolingo blog](https://blog.duolingo.com/duolingo-leagues-leaderboards/)); Coin Master's release year ([Wikipedia](https://en.wikipedia.org/wiki/Coin_Master)).
- Ownership, acquisition and live-service status of the titles above (for example the New York Times' Wordle, closures and relaunches) change over time; verify before quoting in external documents.
