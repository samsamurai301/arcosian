# Cross-Domain Sources: Analogy Material Outside Video Games

Far analogies are where hooks come from (`references/analogy-method.md` section 3). This file is the studio's catalogue of non-video-game sources, each reduced to its **core relation** so it can be mapped with the design-by-analogy procedure. It covers 50 board-game mechanisms in seven families, then sports, toys, real-world systems (gardening, cooking, logistics, ecosystems and more), rituals and crafts. Every entry gives a mobile transplant idea, and where a well-known game already made the move, that precedent is named. A reverse index (relation → where to find it) and a far-analogy retrieval procedure close the file. Board-game designers and years are given where well established; mechanism names follow common hobby usage (for example the BoardGameGeek mechanism taxonomy). Transplant ideas are seeds, not validated designs: run them through the AFS and the market-gap check before use.

## Contents

1. How to use this catalogue
2. Board-game mechanisms (50), in seven families
   - 2.1 Action selection
   - 2.2 Cards, decks and bags
   - 2.3 Spatial and placement
   - 2.4 Chance and risk
   - 2.5 Economic
   - 2.6 Social and information
   - 2.7 Structure and meta
3. Sports and competition formats
4. Toys
5. Real-world systems: gardening, cooking, logistics, ecosystems and more
6. Rituals and habits
7. Crafts
8. Reverse index: relation → where to find it
9. Far-analogy retrieval procedure
10. Pitfalls specific to far sources

---

## 1. How to use this catalogue

1. Start from the **relation you need** (section 8), not from a domain you like.
2. Read the entry's core relation and confirm the target can host its supporting structure.
3. Map with the table format in `references/analogy-method.md` section 8.1; compute AFS.
4. Use one far source per concept, normally for the **hook** or the **meta**, while a near source supplies the chassis.
5. Record the source in `concept.comparables[]` with `title` = the source (for example "Can't Stop (board game)") and `borrow`/`change`.

Column key: **Core relation** is the predicate structure to map. **Transplant idea** is a mobile seed. **Precedent** names an existing digital game that made a similar move (— when none is cited).

---

## 2. Board-game mechanisms (50)

### 2.1 Action selection

| # | Mechanism | Core relation | Canonical examples | Mobile transplant idea | Precedent | Watch-outs |
|---|---|---|---|---|---|---|
| B01 | Worker placement | Limited workers claim exclusive action spaces; claimed spaces block others | Caylus (William Attia, 2005); Agricola (Uwe Rosenberg, 2007) | Idle base where you assign a few workers to rooms; daily "blocked" slots create choices; async rivals claim shared spots in events | Fallout Shelter assigns dwellers to rooms | Blocking needs other players or an AI claimant to matter |
| B02 | Role selection | Each round a player picks a role; everyone performs it, the picker gets a bonus | Puerto Rico (Andreas Seyfarth, 2002) | Team events where the captain's daily pick sets the team's bonus action | — | Requires synchronous or daily group cadence |
| B03 | Rondel | Actions sit on a wheel; moving further costs more; you cannot repeat immediately | Imperial (Mac Gerdts, 2006) | A wheel of upgrade actions in a roguelite camp; skipping ahead costs a resource | — | Readability on small screens |
| B04 | Action points | A budget of points spent across any actions per turn | Many tactics games | Turn-based puzzle tactics with 3 AP per turn and visible costs | Turn-based tactics games (e.g. Into the Breach uses per-unit actions) | Analysis paralysis; keep options to 2–4 |
| B05 | Programmed movement | Players commit a sequence of moves secretly, then all execute | RoboRally (Richard Garfield, 1994) | Plan 3 moves, then watch the bot run; a puzzle of prediction; async duels | — | Frustration when collisions are opaque; show a preview |
| B06 | Simultaneous action selection | Everyone chooses secretly; reveal resolves together | Diplomacy (Allan Calhamer, 1959) orders; rock-paper-scissors | Async 1v1 where both commit a move per round; reveal animates | Marvel Snap's simultaneous reveal | Needs readable counters |
| B07 | Dice placement / dice drafting | Rolled dice are resources placed on actions; value matters | Sagrada (2017); Troyes (2010) | Daily dice roll for all players; place on a board to build; compare results | — | Low agency if rolls dominate; allow re-roll tokens |

### 2.2 Cards, decks and bags

| # | Mechanism | Core relation | Canonical examples | Mobile transplant idea | Precedent | Watch-outs |
|---|---|---|---|---|---|---|
| B08 | Deck building | Buy cards into your deck during play; the deck you build is what you draw | Dominion (Donald X. Vaccarino, 2008) | Run-based deck building with 3-option drafts | Slay the Spire (mobile port) | Card text length on phones |
| B09 | Bag building | Draw tokens blind from a bag you curate | Orléans (Reiner Stockhausen, 2014); The Quacks of Quedlinburg (Wolfgang Warsch, 2018) | A curated loot pool: players add and remove items from their own "bag" that determines drops | — | Must be transparent about contents |
| B10 | Hand management | Choose what to play now versus keep for later | Most card games | Hold-and-play mechanic in a puzzle (keep up to 2 pieces in reserve) | Block puzzles with a hold slot | Extra UI slot |
| B11 | Card drafting | Pick one card from a set, pass the rest | 7 Wonders (Antoine Bauza, 2010); Sushi Go! (Phil Walker-Harding, 2013) | Async draft against ghosts of other players' picks; level-up "pick 1 of 3" | Archero and survivor-like level-up drafts | Needs build diversity |
| B12 | Trick taking | Each player plays one card; highest of the led suit wins the trick | Bridge, Hearts, Spades; The Crew (Thomas Sing, 2019, cooperative) | Cooperative daily trick-taking puzzle with a fixed deal and communication limits | Card apps for Hearts and Spades | Rules unfamiliar outside some regions |
| B13 | Set collection | Value grows with complete or larger sets | Rummy; Ticket to Ride (Alan R. Moon, 2004) | Albums of themed sets with trading of duplicates | Monopoly Go! albums; Coin Master card sets | Last-item grind; odds disclosure |
| B14 | Tableau / engine building | Cards played in front of you produce more each turn; compounding | Race for the Galaxy (Tom Lehmann, 2007); Splendor (Marc André, 2014); Wingspan (Elizabeth Hargrave, 2019); Terraforming Mars (Jacob Fryxelius, 2016) | A short "engine" run: 10 turns to build a compounding garden; score the final engine | — | Engines need time; compress turns |
| B15 | Card-driven events | Cards can be played for event or for points/actions | Twilight Struggle (Ananda Gupta, Jason Matthews, 2005) | Dual-use cards in a light strategy game (play for effect or burn for energy) | — | Complexity |
| B16 | Shedding / climbing | Get rid of your hand by beating the last play | Uno (1971); Big Two | Quick async climbing duels | Mobile Uno and Big Two apps | Luck-heavy; short matches help |

### 2.3 Spatial and placement

| # | Mechanism | Core relation | Canonical examples | Mobile transplant idea | Precedent | Watch-outs |
|---|---|---|---|---|---|---|
| B17 | Tile laying | Place a tile so its edges match neighbours; features grow and score on completion | Carcassonne (Klaus-Jürgen Wrede, 2000) | Calm landscape builder; each placed tile completes features for quests | Dorfromantik (PC, 2021) | Scoring readability |
| B18 | Polyomino placement | Fit shaped pieces into a grid; covered area or completed lines score | Patchwork (Uwe Rosenberg, 2014); Blokus (Bernard Tavitian, 2000) | Packing puzzles: fridges, vans, suitcases | Block puzzles (1010!, Block Blast!) | Thumb occlusion on drag |
| B19 | Pattern building | Place items to complete a target pattern; leftovers penalise | Azul (Michael Kiesling, 2017) | Pattern drafting from a shared market each round, with overflow penalties | — | Visual clutter |
| B20 | Tile drafting | Choose a tile from a market; the choice also sets turn order or costs | Kingdomino (Bruno Cathala, 2016); Cascadia (Randy Flynn, 2021) | Draft one of four tiles per turn into a small kingdom; daily shared seed | — | Needs clear scoring preview |
| B21 | Area majority / control | Most presence in a region wins its points | El Grande (Wolfgang Kramer, Richard Ulrich, 1995); Risk (1957) | Async territory events: teams contest map regions weekly | paper.io (area capture) | Snowballing; add catch-up |
| B22 | Network / route building | Connect points with routes; completed connections score | Ticket to Ride; Power Grid (Friedemann Friese, 2004) | Draw routes between growing towns with limited track | Mini Metro (transit networks) | Line drawing precision |
| B23 | Path laying | Place tiles that extend paths; players follow paths | Tsuro (Tom McMurchie, 2004) | One-thumb path-tile puzzle where your character walks the path you lay | Pipe-connection puzzles | Overlapping paths readability |
| B24 | Grid movement / abstract positioning | Movement and adjacency rules on a grid decide captures | Chess; Hive (John Yianni, 2001); Santorini (Gordon Hamilton) | Bite-size tactics puzzles: mate-in-N style for a fantasy theme | Hitman GO's node movement | Steep skill floor |
| B25 | Modular board | The board is assembled from tiles, differently each game | Catan (Klaus Teuber, 1995); Betrayal at House on the Hill (2004) | Daily procedurally assembled maps from authored chunks | Roguelite map generation | Balance across layouts |
| B26 | Stacking and dexterity | Physical skill places or removes pieces without collapse | Jenga (Leslie Scott, 1983); Crokinole | Physics stacking towers with one-tap drops | Stack-style hyper-casual games | Physics determinism for replays |

### 2.4 Chance and risk

| # | Mechanism | Core relation | Canonical examples | Mobile transplant idea | Precedent | Watch-outs |
|---|---|---|---|---|---|---|
| B27 | Push-your-luck | Continue for more gain or stop to bank; a bust loses the unbanked gain | Can't Stop (Sid Sackson, 1980); Incan Gold / Diamant (Bruno Faidutti, Alan R. Moon, 2005); Quacks | Expedition runs: dig deeper for rarer finds or return to bank; a cave-in loses the trip's haul | — | Keep stakes to in-run gains; never paid currency |
| B28 | Dice rolling with re-rolls | Roll, keep some, re-roll the rest toward combinations | Yahtzee (1956); King of Tokyo (Richard Garfield, 2011) | Combat where you lock dice faces to build combos | Dicey Dungeons (dice allocation) | Output randomness feel |
| B29 | Roll-and-write | Everyone uses the same roll or flip and writes choices on a personal sheet | Qwixx (Steffen Benndorf, 2012); Railroad Ink (2018); Welcome To... (Benoit Turpin, 2018) | Shared daily seed: everyone gets the same 12 rolls; compare sheets; share score | Wordle-style shared daily structure | Needs readable sheet on a phone |
| B30 | Wagering / betting | Stake a value on an uncertain outcome; raise and fold | Poker; backgammon's doubling cube | Rank-point stakes in async duels (OP18) | Marvel Snap's snap | Gambling resemblance; never paid currency |
| B31 | Bust limit | Draw toward a target; exceeding it loses | Blackjack | A merge or cooking mini-game where overfilling ruins the dish | — | Casino association for minors |

### 2.5 Economic

| # | Mechanism | Core relation | Canonical examples | Mobile transplant idea | Precedent | Watch-outs |
|---|---|---|---|---|---|---|
| B32 | Auctions (open, once-around, sealed, fixed price, Dutch) | Players bid for items; the format changes the psychology | Modern Art (Reiner Knizia, 1992); Ra (Reiner Knizia, 1999); Power Grid | Weekly async sealed-bid event for decorative rarities using earned currency | — | Hard currency auctions invite whales; use earned currency only |
| B33 | Dynamic market | Prices rise as a resource is bought, fall as it is unused | Power Grid's resource market | Idle tycoon where your purchases move prices; arbitrage over the day | — | Players feel punished; show the curve |
| B34 | Trading and negotiation | Players exchange resources by agreement | Catan; Diplomacy | Team-internal trading boards; preset offers instead of free chat | Hay Day roadside shop | Scams, bots, and minors |
| B35 | Stock holding | Players invest in entities others also grow | Acquire (Sid Sackson, 1964) | Invest in other players' farms or towns; dividends when they grow | — | Real-money resemblance |
| B36 | Pick-up and deliver | Carry goods from producers to demand points | Train games (e.g. Age of Steam tradition) | Delivery runs in a town builder; route efficiency puzzles | Order-board farming (Hay Day trucks) | Travel time is dead time; compress |
| B37 | Contracts / orders | Public or private goals pay on completion | Ticket to Ride destination tickets | Order boards in merge and farming games | Merge Mansion orders; Hay Day orders | Order RNG frustration; allow rerolls |
| B38 | Income and upkeep | Assets pay income but cost upkeep each round | Many economic euros | Idle base where expansion raises upkeep; a soft sink | — | Death spirals; floor the economy |

### 2.6 Social and information

| # | Mechanism | Core relation | Canonical examples | Mobile transplant idea | Precedent | Watch-outs |
|---|---|---|---|---|---|---|
| B39 | Hidden roles / traitor | A secret minority with opposed goals; deduction through behaviour | Mafia (1986); Werewolf; The Resistance (Don Eskridge, 2009); Secret Hitler (2016) | Daily async deduction in friend groups: one vote per day for a week | Among Us | Needs a group; moderation |
| B40 | Bluffing | Claims may be false; challenges risk loss | Coup (Rikki Tahta, 2012); Skull (Hervé Marly, 2011); Liar's Dice | Bluff-and-call layer in async duels | Marvel Snap snap bluffs | Async weakens bluff pressure |
| B41 | Deduction | Infer hidden information from structured feedback | Clue / Cluedo (Anthony E. Pratt, 1949); Mastermind (1970); Cryptid (2018) | Daily deduction puzzles with structured clues | Wordle; Minesweeper-style logic | Solvability guarantees (solver) |
| B42 | Cooperative against the system | All players win or lose together against an escalating game | Pandemic (Matt Leacock, 2008); Forbidden Island (2010); Spirit Island (R. Eric Reuss, 2017) | Team raid events against a scripted escalating boss | Team events in puzzle games | Quarterbacking |
| B43 | Limited communication | Cooperation where talking is restricted | Hanabi (Antoine Bauza, 2010); The Mind (Wolfgang Warsch, 2018) | Emote-only co-op puzzles; signals as the puzzle | Clash Royale's emote-only in-match communication | Frustration if signals are ambiguous |
| B44 | Association / storytelling | Score by matching others' interpretations | Dixit (Jean-Louis Roubira, 2008); Codenames (Vlaada Chvátil, 2015) | Async picture-clue party game with friends | — | Localization per language |
| B45 | Real-time simultaneous play | Everyone acts at once under time pressure | Galaxy Trucker (Vlaada Chvátil, 2007); Captain Sonar (2016) | Short synchronous co-op build rounds (60–90 seconds) | — | Real-time backend cost |

### 2.7 Structure and meta

| # | Mechanism | Core relation | Canonical examples | Mobile transplant idea | Precedent | Watch-outs |
|---|---|---|---|---|---|---|
| B46 | Legacy | Permanent, irreversible changes to the game across sessions | Risk Legacy (Rob Daviau, 2011); Pandemic Legacy (Rob Daviau, Matt Leacock, 2015) | A season where choices permanently reshape a shared world map; revealed sealed "envelopes" | — | Content cost; late joiners |
| B47 | Campaign with branching | Scenarios link; outcomes unlock branches | Gloomhaven (Isaac Childres, 2017) | Chapter map with branches unlocked by optional goals | Saga maps with side paths | Content cost |
| B48 | Variable player powers / asymmetric factions | Each player has unique rules | Cosmic Encounter (1977); Root (Cole Wehrle, 2018) | Hero kits that break one rule each | Hero shooters, CCG classes | Balance |
| B49 | King of the hill | Holding a central spot pays but exposes you | King of Tokyo | Hold-the-zone event mode | Brawl Stars hot-zone-style modes | Snowball |
| B50 | Sowing / mancala | Pick up a pile and distribute one per pit; the last landing triggers effects | Mancala family (traditional) | Sowing-based puzzle: distribute seeds around a garden ring to trigger chains | — | Unfamiliar outside some regions; teach visually |

**Extra mechanisms to consider** (one line each): *memory* (Concentration) → recall puzzles; *I divide, you choose* (the classic fair-division procedure) → async loot splitting between friends; *catch-up mechanisms* (last place picks first) → comeback design; *tech trees* → meta unlocks; *race* (backgammon) → dual-track runs; *same tiles for all* (Karuba, Rüdiger Dorn, 2015) → shared-seed solitaire competition.

---

## 3. Sports and competition formats

| # | Source | Core relation | Mobile transplant idea | Precedent / note |
|---|---|---|---|---|
| S01 | Golf: par and handicap | A target score per hole; handicaps normalise skill so unequal players can compete | Puzzle levels with "par moves"; handicapped async duels between friends of different skill | Golf scoring is widely used in puzzle star ratings |
| S02 | Bowling: strike and spare lookahead | Perfect frames add the next rolls' pins as bonus | 10-frame block-puzzle runs where a full-board clear carries a bonus into the next two frames | — |
| S03 | Tennis: win by two; nested sets | Close games must be won by a margin; points → games → sets → match | Async duels decided by a two-point margin; nested scoring for tension | Nested loops mirror the time-scale ladder (`design-theory`) |
| S04 | Cricket: Test → Twenty20 | A days-long format compressed into about three hours (Twenty20, introduced in England in 2003) | A sport's own precedent for session compression (OP17): keep the duel, cap the overs | Strong argument for OP17 from outside games |
| S05 | Darts 501: exact checkout | Count down to zero, finishing exactly (traditionally on a double) | End-game precision: finish a level with an exact count, not "at least" | — |
| S06 | Curling: the hammer | Last-stone advantage alternates by rule | Turn-order asymmetry with compensation in async duels | — |
| S07 | Motor racing: qualifying and pit strategy | Qualifying sets grid order; tyres degrade and force pit decisions | A run's equipment degrades; when to "pit" (repair) is the decision | — |
| S08 | Cycling Grand Tours: parallel classifications and drafting | Several leaderboards (overall, points, mountains, youth); riders cooperate in the slipstream while competing | Multiple event leaderboards so different players can win something; cooperative drafting bonuses in team races | — |
| S09 | League promotion and relegation | Tiers; top finishers move up, bottom move down each season | Weekly leagues in small cohorts | Duolingo leagues (W44) |
| S10 | Swiss-system tournaments | Players with equal records are paired; nobody is eliminated | Weekend puzzle tournaments where everyone plays all rounds | Chess tournaments |
| S11 | Fantasy sports | Draft a roster; points come from real-world performance | Draft heroes whose weekly score comes from aggregate community play stats | Backend and fairness heavy |
| S12 | Decathlon points tables | Different events converted to one points scale | Multi-mode events summed on one scale | — |
| S13 | Poker tournaments: rising blinds | Escalating forced costs guarantee the game ends | Escalating per-turn cost in roguelite runs (antes) | Balatro's antes and blinds |
| S14 | Chess clocks and increments | A time bank plus a per-move increment | Async-with-a-clock duels; a time bank per match | — |
| S15 | Relay races | A baton passes between teammates; each leg adds | Async team relays: your run's result is a friend's starting boost | — |
| S16 | Skating and freestyle scoring | Difficulty × execution; repeated elements score less | Combo systems that penalise repetition to reward variety | — |
| S17 | Sumo ranking | A winning record in a tournament promotes, a losing record demotes | Simple promotion rules for rank tiers (majority wins in a set) | — |
| S18 | Salary caps and drafts | Team-building under a budget; weakest teams pick first | Deck-cost caps; catch-up picks in seasonal drafts | — |

---

## 4. Toys

| # | Toy | Core relation | Mobile transplant idea | Precedent / note |
|---|---|---|---|---|
| T01 | Construction bricks | Standard connectors let any part attach to any other; instructions versus free build | Modular builder with blueprint challenges and a free mode | UGC builders |
| T02 | Rubik's Cube (Ernő Rubik, 1974) | Permutation puzzle; learnable move sequences (algorithms) | Puzzles where players discover and save macros | — |
| T03 | Jigsaw puzzles | Edges first, sort by colour; satisfying assembly | Calm assembly puzzles with a daily image | Jigsaw apps |
| T04 | Domino toppling | Set up a chain, then trigger it | Setup-then-release chain-reaction puzzles | Physics puzzle genre |
| T05 | Marble runs | Build a path; release and watch | Build-a-track puzzles with a release button | — |
| T06 | Virtual pets (Tamagotchi, 1996) | Care on a schedule keeps a creature well | Absence-driven care without punishment | Neko Atsume (W17), My Talking Tom |
| T07 | Kendama and yo-yo | Trick ladders of increasing difficulty | Skill trick ladders with a practice mode | — |
| T08 | Spinning-top battles | Customise parts, launch, then watch | Build-then-release battles (OP25) | — |
| T09 | Dress-up dolls | Outfit combinations; self-expression | Fashion and style games with themed challenges | Dress-up genre |
| T10 | Dollhouses and miniature worlds | Arranging a small world | Diorama decoration metas | Renovation metas |
| T11 | Sticker albums | Sets, duplicates and swapping | Collection grafts with trading (OP29) | Monopoly Go! albums |
| T12 | Trading cards | Rarity, trading, display | Card collection metas | Pokémon TCG Pocket (W34) |
| T13 | Snow globes and kaleidoscopes | Shake or turn to see a changing pattern | Ambient "toy" screens; generative art modes | — |
| T14 | Nesting dolls | Containers within containers | Nested levels; recursive puzzles | — |
| T15 | Tangram | Fixed pieces fill a silhouette | Shape-fill puzzles | — |
| T16 | Modelling clay | Push, pull and shape freely | Sculpting toys with gesture input | — |
| T17 | Toy train tracks | Build track, run the train | Path-building puzzles | — |
| T18 | Kites | Wind and line tension | One-touch flight with physics | — |

---

## 5. Real-world systems: gardening, cooking, logistics, ecosystems and more

### 5.1 Gardening

| Source relation | Explanation | Transplant idea |
|---|---|---|
| Growth over real time | Plants grow while you are away | Absence-driven growth (OP16), harvest on return |
| Pruning shapes growth | Removing parts redirects growth | Subtraction puzzles: prune branches to reach light targets |
| Companion planting | Neighbours help or hinder each other | Adjacency bonus puzzles on a garden grid |
| Crop rotation | Repeating a crop depletes soil; rotation restores | Farming with soil-nutrient constraints (a puzzle-ified farm) |
| Seasons | Some actions only work in some seasons | Seasonal live-ops with season-specific crops |
| Weeding | Maintenance competes with growth | A soft sink that rewards regular short sessions |

### 5.2 Cooking

| Source relation | Explanation | Transplant idea |
|---|---|---|
| Recipes as converters | Inputs combine into outputs | Converter nodes in the economy (`economy-model.schema.json` node kind `converter`) |
| Mise en place | Prepare first, then execute fast | Two-phase loop: calm prep, then a timed service |
| Parallel timing | Several dishes finish together | Time-management queues (the Diner Dash lineage, 2004) |
| Heat control | Too little or too much ruins the dish | Bust-limit mini-games (B31) |
| Tasting and seasoning | Small adjustments toward a target | Slider-based target matching puzzles |

### 5.3 Logistics

| Source relation | Explanation | Transplant idea |
|---|---|---|
| Bin packing | Fit items into containers efficiently | Van, fridge or suitcase packing puzzles (polyomino) |
| Routing | Visit points in an efficient order | Route-drawing puzzles; delivery runs |
| Warehousing and slotting | Frequent items near the exit | Sort and storage puzzles |
| Queues and throughput | Bottlenecks decide capacity | Factory or transit puzzles with visible bottlenecks |
| Order fulfilment | Orders demand specific mixes | Order boards (B37) |
| Last-mile delivery | Final step is the most costly | Mini-game end steps that reward precision |

### 5.4 Ecosystems

| Source relation | Explanation | Transplant idea |
|---|---|---|
| Predator–prey cycles (Lotka–Volterra model) | Populations oscillate as predators and prey grow and crash | A balancing sim: keep a rock pool or meadow cycling, not maximised |
| Food webs | Removing one species cascades | Puzzle where removing a node reshapes the network |
| Carrying capacity | Growth slows near a limit | Soft caps that feel natural: model the capped quantity (power, income, population) as logistic growth toward the limit, `value = cap / (1 + e^(-k(t - t0)))`. Note that `progression_calc.py --formula logistic` applies the sigmoid to XP cost per level (rising from the base to about 10× and then flattening), a different use; its exact formula is in `progression-difficulty` |
| Succession after disturbance | Ecosystems rebuild in stages | Restoration metas with staged recovery |
| Keystone species | One species holds the system together | A rare collectible that unlocks a whole biome |

### 5.5 Other systems

| System | Core relation | Transplant idea | Precedent |
|---|---|---|---|
| Plumbing and water flow | Connected pipes carry flow from source to sink | Pipe-connection puzzles | Pipe Mania (1989) |
| Electric circuits and logic gates | Signals combine through gates | Logic puzzles with visible signals | — |
| Traffic signals | Timing reduces congestion | Junction-timing puzzles | — |
| Epidemiology (SIR models) | Susceptible → infected → recovered, with transmission rates | Spread strategy | Plague Inc. (W47) |
| Air traffic control | Separate and sequence arrivals | Path drawing | Flight Control (W49) |
| Transit networks | Lines serve growing demand | Network puzzles | Mini Metro (W48) |
| Markets | Supply and demand set prices | Dynamic pricing in tycoons (B33) | — |
| Beekeeping | Colony health, foraging radius, seasonal honey | Push-your-luck foraging (B27) with an idle hive | — |
| Aquariums | A hidden nitrogen cycle decides fish health | Hidden-state management with readable indicators | — |
| Wildfire spread | Fire spreads by fuel, wind and slope | Cellular-automaton containment puzzles (`pcg.py` grids) | — |
| Restaurants | Seat, serve, clear, under time | Time management | Diner Dash lineage |
| Postal sorting | Sort items into destinations quickly | Sort puzzles | Sort genre (`game-case-studies`) |
| Fermentation (sourdough starters) | A living culture needs feeding on a schedule; it can be split and shared | Care loop with gifting of "splits" to friends | — |

---

## 6. Rituals and habits

| # | Ritual | Core relation | Transplant idea | Precedent |
|---|---|---|---|---|
| R01 | Advent calendars | One door per day toward a date | Daily unlock countdowns for seasonal events | Event calendars |
| R02 | The newspaper puzzle | One puzzle per day, shared by all readers | Daily shared puzzles (OP23) | Wordle (W11) |
| R03 | Streak habits | Consecutive days build identity | Forgiving streaks with freezes | Duolingo (W44) |
| R04 | Tea ceremony | A precise sequence performed mindfully | Calm sequencing puzzles; no timers | — |
| R05 | Journaling | Daily reflection, small entries | Reflective prompts in narrative or wellness games | — |
| R06 | Gift exchanges | Anonymous giving within a group | Secret gifting events within teams | — |
| R07 | Stamp rallies | Collect a stamp at each location | Location check-ins or in-game district stamps | Location games |
| R08 | Bird-watching life lists | Lifetime record of species seen | Lifetime collection lists with rarity by place and season | Pokémon GO's regional creatures |
| R09 | Weekly game night | An appointment with friends | Weekly synchronous event windows | — |
| R10 | Seasonal festivals | The calendar marks shared celebrations | Seasonal live-ops beats | Live-ops calendars (`liveops`) |
| R11 | Fortune cookies and horoscopes | A small, random daily message | Daily random modifiers or messages | — |
| R12 | Morning routines | A sequence at a fixed time | Short morning check-in loops (60 s) | — |

---

## 7. Crafts

| # | Craft | Core relation | Transplant idea | Precedent |
|---|---|---|---|---|
| C01 | Knitting | Patterns repeat; stitch counts must match per row | Pattern-matching row puzzles; cosy garment collection | — |
| C02 | Quilting | Patchwork squares assembled into a pattern | Polyomino pattern puzzles | Patchwork (B18) |
| C03 | Pottery | Centre, shape, fire; glaze outcomes are partly unpredictable | Craft loop with a reveal moment (kiln) and transparent odds | — |
| C04 | Woodworking | Measure twice, cut once: irreversible actions need planning | Puzzles with irreversible cuts and a preview | — |
| C05 | Origami | Folding sequences create form | Folding puzzles | — |
| C06 | Calligraphy | Stroke order and pressure | Gesture-skill tracing games | — |
| C07 | Cross-stitch and embroidery | Grid colouring by pattern | Colour-by-number relaxation | Colour-by-number apps |
| C08 | Bonsai | Slow shaping over long times | Long-horizon care with rare, meaningful decisions | — |
| C09 | Kintsugi | Repair breaks with gold, making repair visible | Repair puzzles: reassemble and gild | — |
| C10 | Mosaic and stained glass | Fit pieces into a design | Tile-fitting puzzles | — |
| C11 | Blacksmithing | Heat, hammer, quench with timing | Rhythm crafting mini-games | — |
| C12 | Weaving | Warp and weft interlace on a grid | Grid logic (nonogram-like) puzzles | — |

---

## 8. Reverse index: relation → where to find it

| Relation you need | Look at | Entries |
|---|---|---|
| Choice under scarcity of action slots | Worker placement, action points, rondel | B01, B03, B04 |
| Compounding growth | Engine building, idle, gardening | B14, 5.1, OP16 |
| Tension from voluntary risk | Push-your-luck, wagering, bust limits | B27, B30, B31 |
| Fair randomness | Bags, shared seeds, roll-and-write | B09, B29, OP20 |
| Shared daily conversation | Newspaper puzzles, roll-and-write, advent calendars | R02, B29, R01 |
| Planning over reflex | Programmed movement, simultaneous selection | B05, B06 |
| Cooperation without a leader | Limited communication | B43 |
| Social deduction | Hidden roles, bluffing, deduction | B39, B40, B41 |
| Natural difficulty growth | Transit, logistics, ecosystems | 5.3, 5.4, W48 |
| Readable spatial puzzles | Polyomino, tile laying, path laying | B18, B17, B23 |
| Goals for a sandbox | Contracts and orders, set collection | B37, B13 |
| Comeback and catch-up | Draft lotteries, catch-up rules, handicaps | S18, S01 |
| Session compression | Twenty20 cricket, rising blinds | S04, S13 |
| Multiple ways to win | Parallel classifications | S08 |
| Achievable competition | Leagues with promotion and relegation | S09, W44 |
| Care without guilt | Virtual pets (without punishment), fermentation | T06, 5.5 |
| Reveal moments | Pottery kilns, pack opening | C03, T12 |
| Irreversibility and planning | Woodworking, legacy | C04, B46 |

---

## 9. Far-analogy retrieval procedure

1. **Name the relation.** Write the target need as a predicate without game words: "voluntary escalation of risk with a safe exit", "growth that continues while I am away".
2. **Query by relation.** Search section 8 and this file; then `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py kb "<relation words>" --skill analogy-engine --limit 10`.
3. **Random entry (optional).** Edward de Bono's random-entry technique (*Lateral Thinking*, 1970): pick a random domain from sections 3–7, force a connection to the target, and keep only connections that survive the relation test.
4. **Pick two far sources** that share the relation and abstract both (analogical encoding). The shared part is the schema.
5. **Map one** into the target with the AFS; prefer the source whose supporting structure the target already has.
6. **Check readability**: will the segment recognise the source (unpacking test)? If not, the source is a design tool, not a pitch input; keep it out of the "X meets Y" line and describe the relation directly.

---

## 10. Pitfalls specific to far sources

| Pitfall | Symptom | Fix |
|---|---|---|
| Theme tourism | The source contributes only art ("a cooking theme") | Find the source's relation (mise en place, parallel timing) or treat it as OP02 |
| Unfamiliar rules | Players do not know trick-taking or mancala | Teach by doing in the first minute; or pick a familiar source |
| Real-world baggage | Gambling, medical, or tragic systems | Check tone and law (`legal-ethics`); for minors, avoid wager mechanics entirely |
| Fidelity trap | Simulating the real system in detail | Keep 2–3 relations that create decisions; cut the rest (OP08) |
| Pace mismatch | A slow real-world rhythm in a fast mobile session | Compress time, or make the slow rhythm an absence loop |
| Untested pairing | Far source chosen for novelty only | Score novelty and fun separately; prototype the toy first |
