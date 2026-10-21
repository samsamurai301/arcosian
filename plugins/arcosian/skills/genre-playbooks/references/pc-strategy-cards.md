# PC Strategy and Card Playbooks

PC and console strategy and card games reward depth: many systems, long sessions, readable information and opponents that play well. This file holds six playbooks in a shared 15-part template (the 14-part format used elsewhere, plus platform notes). It covers the PC and console side of strategy and cards. Mobile 4X/SLG, tower defence, real-time card battlers, auto-battlers and mobile tactics are in `skills/genre-playbooks/references/strategy.md`, and mobile collectible card games are in `skills/genre-playbooks/references/competitive-pvp.md` (§5). Read those for timer economies, Lanchester combat, async PvP and ladders, and do not repeat them here.

1. Real-time strategy (RTS)
2. Turn-based 4X (PC)
3. Grand strategy
4. Roguelike deckbuilder
5. Digital collectible / living card game
6. Tactics RPG (PC and console)

Five foundations come first: AI opponents, UI for deep complexity, card design maths, determinism and replays, and mod support. Single-player roguelike deckbuilders and tactics RPGs are deterministic, solver-friendly and the best first projects for an agent pipeline (4/5). Grand strategy and RTS depend on AI quality and balance over many hours, which makes them hard to verify (1–2/5). Market numbers live in the dated volatile-facts section.

## Contents

| § | Playbook | Session profile (estimate) | Primary monetisation | Agent-buildability | First project for an agent pipeline? |
|---|---|---|---|---|---|
| 0 | [Shared foundations](#0-shared-foundations) | — | — | — | Read first |
| 1 | [RTS](#1-real-time-strategy-rts) | 15–60 min matches, 6–12 h campaign | Premium, DLC, ranked ladder | 2/5 | No, a skirmish slice at most |
| 2 | [Turn-based 4X (PC)](#2-turn-based-4x-pc) | 2–6 h sittings, 30–100 h to master | Premium plus DLC expansions | 3/5 | Possible, with a small map and AI |
| 3 | [Grand strategy](#3-grand-strategy) | 2–5 h sittings, hundreds of hours | Premium plus large DLC | 1/5 | No |
| 4 | [Roguelike deckbuilder](#4-roguelike-deckbuilder) | 30–60 min runs | Premium, DLC | 4/5 | Yes |
| 5 | [Digital CCG / LCG](#5-digital-collectible--living-card-game) | 5–20 min matches | Free-to-play packs or fixed expansions | 2/5 | Only a fixed-set, bot-ladder slice |
| 6 | [Tactics RPG (PC/console)](#6-tactics-rpg-pcconsole) | 20–60 min missions, 20–60 h | Premium, DLC | 4/5 | Yes |
| — | [Volatile facts](#volatile-facts-as-of-oct-2026--verify-before-relying) | — | — | — | Check before quoting numbers |

## How to use these playbooks

- Copy the core loop into `contract.json → loops[]`. Set `meta.genre: "strategy"` or `"card"` and `meta.subgenre` to the playbook slug. Set `meta.platforms`, `meta.input` (`mouse_keyboard`, `gamepad`) and `technical.multiplayer` (`none`, `async` or `realtime`).
- Turn the starter feature list into P0 `features.json` entries with `gs.py feature add`. Each acceptance criterion maps to `unit`, `playthrough` or `replay` gate evidence (bots, simulations, solver runs).
- Mechanic category labels used here: combat, build-craft, collection & randomness, progression & upgrade, economy & resources, social & competition, exploration & traversal, puzzle & logic, UX automation. Resolve them with `gs.py kb "<mechanic>" --skill mechanics-codex`.
- For input, platform UX and performance tiers use `platform-targets`. For Steam and web release use `pc-web-release`. For console programmes and certification use `console-pathway`.
- KPI statements are qualitative unless sourced. Premium games track completion, review score, refund rate, hours played and DLC attach rate more than D1 and D30.

## 0. Shared foundations

### 0.1 AI opponents: utility AI, cheating and fair AI
The AI decides whether a strategy game is worth replaying. Build it in layers and test it by simulation.

```
Strategic layer   goals: expand, defend, attack, tech          (decides every N seconds or turns)
Operational       assigns units to goals, picks targets, routes  (every few seconds / every turn)
Tactical          unit actions, focus fire, retreat, ability use (every tick / every action)
```

**Utility AI.** Score each candidate action as a weighted sum of considerations, each shaped by a response curve, then pick the best (or sample among the top few).

```
score(action) = Π over considerations  curve_i(input_i)       (multiplicative: any zero vetoes)
              or Σ weight_i · curve_i(input_i)                 (additive: easier to tune)
Example: attack-score = 0.5·force_ratio + 0.3·target_value + 0.2·(1 − own_exposure)
         force_ratio = clamp(own_strength / enemy_strength, 0, 2) / 2
```

Rules:
1. Log every decision with its scores, so a human can read why the AI acted.
2. Add small random noise (for example ±5% on scores) so the AI is not predictable. Seed it so runs replay.
3. Use **influence maps** (a grid of threat and value) for positioning in RTS and tactics, and **behaviour trees or goal-oriented planning** for unit behaviour.
4. Test by AI-versus-AI matches (1,000 per build). Check win-rate by faction, game length distribution, and "AI does nothing" or "AI suicides" failure counts.

**Cheating versus fair AI.**

| Type | What it does | Effect |
|---|---|---|
| Fair AI | Same rules, same vision, same economy as the player | Respected. Strongest to build and slowest to tune |
| Handicapped AI | Fair but slower, noisier or less efficient (reaction delay, wasted resources) | Good for easy and medium modes |
| Resource cheating | Extra income or discounts at higher difficulties | Common and accepted if disclosed. Keep the bonus modest |
| Information cheating | AI sees through fog or knows build orders | Feels unfair when noticed. Avoid or disclose |
| Rule-breaking | AI ignores costs, limits or timers | Players call it out quickly. Avoid |

Procedure: build the fair AI first and make it as strong as you can. Then set difficulty tiers by handicaps (delay, error, efficiency) for easy modes, and by small, disclosed resource bonuses (for example +10%, +25%, +50%, estimates) for hard modes. Show the bonuses in the difficulty menu. Record AI win rate against a scripted "reference player" bot at each tier and aim for the contract's target band (for example 25% / 50% / 75%).

### 0.2 UI for deep complexity
Strategy games hold hundreds of numbers. The UI must let a player understand, decide and verify without a wiki.
- **Nested tooltips.** Any term in a tooltip is itself hoverable (hold a key to pin). Terms link to the encyclopaedia. Limit nesting to about three levels and show a breadcrumb. Tooltips must show the numbers behind a result: base value, each modifier and the total (for example `+12 = 8 base +3 tech +1 trait`).
- **Encyclopaedia.** A searchable in-game reference generated from the same data files as the game (units, buildings, techs, rules). Each entry shows stats, who unlocks it and where it is used. Generating it from data keeps it correct.
- **Information hierarchy.** Put the three things the player needs now on screen (resources, threats, next decision). Everything else is one click away. Use alerts with "go to" buttons.
- **Outliner and filters.** A list of cities, armies or units with sort and filter, and a count of items needing orders.
- **Map modes.** Overlays for terrain, ownership, supply, threat and trade. Switch with keys.
- **Preview before commit.** Show the predicted result of an action (combat odds, production time, trade income) before the player confirms. Explain with a breakdown.
- **Undo and confirm.** Allow undo within a turn when no hidden information was revealed.
- **Onboarding.** Teach in layers: a short guided scenario for core verbs, contextual hints on first encounter and a glossary. Do not front-load all systems.
- **Accessibility.** Scalable text (large text for dense tables), colour-blind-safe palettes with shape cues, and full keyboard and pad navigation. See `accessibility-localization`.
- **Controller UI.** On console use radial menus, cursor snapping and context panels. A pad-first UI is a separate design, not a re-skin of the mouse layout (`platform-targets`).

### 0.3 Card design maths: mana curves and card advantage
**Mana curve.** The distribution of card costs in a deck. A healthy curve gives a playable card every turn.

```
Example 40-card limited-style deck (my numbers): cost 1: 4 · 2: 8 · 3: 7 · 4: 5 · 5: 3 · 6+: 1 = 28 spells + 12 lands
Average cost  = (4·1 + 8·2 + 7·3 + 5·4 + 3·5 + 1·6) / 28 = 82 / 28 ≈ 2.9
Rule of thumb: most of the deck at 2–4 cost, few above 5.
```

**Resource curve rules:**
1. Resource per turn should grow at the pace of the average cost, so "play on curve" is possible but not forced.
2. Cheap cards (1–2) must be weaker per cost than expensive ones, or the expensive cards are never played. Check with "stats per mana" (for example, a vanilla creature gets about 2 stat points per mana plus or minus a premium, estimates), then add a tempo factor.
3. Include a mulligan or redraw rule to reduce non-games.

**Card advantage.** Count the net cards each side has after an exchange. A 2-for-1 trade (one card removes two enemy cards) is card advantage. A draw spell that costs a card and draws two is +1. Tempo (mana spent versus mana removed) trades off against card advantage. Design rule: every source of card advantage needs a tempo cost or a condition.

**Hypergeometric draw odds (my arithmetic).** Probability of drawing at least one copy of a card:
- 60-card deck, 4 copies, 7-card opening hand: 1 − C(56,7)/C(60,7) ≈ 40.0%.
- 40-card deck, 16 lands, 7-card hand: 2, 3 or 4 lands ≈ 79.0%; 0 or 1 lands ≈ 13.4%.
- 30-card deckbuilder deck, 2 copies of a card, draw 5: 1 − C(28,5)/C(30,5) ≈ 31.0%.

Use these to set deck sizes, copy limits and mulligans. Compute with a script rather than by hand (`balance`).

**Balance by simulation.**
1. Encode every card as data with a cost, stats and effects (no card-specific code where a keyword will do).
2. Build a rules engine that is deterministic with a seeded shuffle (§0.4).
3. Run bot-vs-bot matches with archetype decks (aggro, midrange, control, combo). Target: no archetype above about 55% (or the contract's band) against the field, and no card with a play rate far above the median.
4. Track "win rate when played" per card and flag outliers for review.
5. Plan a **keyword budget**: a small set of evergreen keywords that each new set uses, to limit rules text growth.

### 0.4 Determinism and replays
Link: `skills/genre-playbooks/references/strategy.md` §0.3 for the sim-core rules (fixed timestep, seeded PRNG, integer or fixed-point math, inputs logged as `(tick, action)`). Extras for PC and console:
- **Command-log replays.** Store the seed plus the ordered commands. A replay file is small and doubles as a bug report and a test fixture.
- **Lockstep RTS.** Each client simulates the same commands each tick. Send commands, not states. Check desync with a state hash every N ticks. Any float or hash-order difference across CPUs breaks it, so use fixed-point math and ordered containers.
- **Card games.** The server is the authority for shuffles and hidden information. The client animates the log of events. Never trust the client with the deck order.
- **Save compatibility.** Version the save format and the rules data. Replays from an older version need the older rules or a migration.
- **Autoplay tests.** A replay run through the build in CI catches regressions in rules (`qa-testing`).
- **Spectating and caster tools** use the same log. See `multiplayer-backend`.

### 0.5 Mod support
Mods extend a strategy game's life by years. Decide early how much to allow.

| Level | What players can do | Cost | Risk |
|---|---|---|---|
| Data mods | Edit data tables (units, cards, techs, text) | Low if the game is data-driven | Balance and save breaks |
| Script mods | Add logic through a scripting language (Lua or similar) | Medium. Needs an API and docs | Security, sandboxing, desync in multiplayer |
| Asset mods | Replace art, sound, models | Low | Rating and copyright issues |
| Total conversions | New game on your engine | High | Support load |

Rules:
1. Build the game data-driven from day one. Your own content should load the way mods do.
2. Version the mod API and warn on mismatch. Keep stable IDs.
3. Sandbox scripts. No file or network access beyond the declared API.
4. Multiplayer: hash the mod list and data at join. Mismatch blocks the match.
5. Use the store's workshop or mod hub if available (volatile facts; `pc-web-release`). Add a content policy and a report flow.
6. Keep ranked play on unmodded content.
7. Ship the same tools you used. Document the data schema.

## 1. Real-time strategy (RTS)

### Definition and player fantasy
Players gather resources, build bases, train armies and fight in real time on a map, often with asymmetric factions. The fantasy is *a commander under time pressure*: macro-management, scouting, tactical micro and the satisfaction of a well-executed plan.

### Core loop
```
gather resources → build economy and tech → produce units → scout and position
  → fight (micro, abilities, retreat) → win or lose map control → expand or end the game
```

### Meta loops
- **Campaigns and missions.** Story-led scenarios with objectives.
- **Skirmish against AI.** Difficulty tiers and custom games.
- **Ranked ladder and leagues.** Ratings, seasons (see `competitive-pvp.md` §0).
- **Co-op missions and commanders.**
- **Map editor and mods.**
- **Esports and replays.**

### Session profile
Estimate: 15–60 minute matches, 6–12 hour campaigns, and long sessions of custom play. Skill expression is high, so a large share of players avoid ranked and play campaign or co-op.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Resource gathering and expansion | economy & resources | Expansion timing is the strategic core |
| Build order and tech tree | progression & upgrade | A solved opening is a balance signal |
| Unit counters (rock-paper-scissors plus) | combat | Add upgrades and abilities for depth |
| Fog of war and scouting | exploration & traversal | Hides information. Needs a clear UI |
| Control groups, hotkeys, queues | UX automation | Lower the execution floor with smart cast and queues |
| Asymmetric factions | combat | Hard to balance. Needs mirror and cross tests |
| Pathfinding and formation movement | combat | Cost scales with unit count. Use flow fields |
| Replays and caster tools | UX automation | Required for community |

### Monetisation model and typical mix
Premium base game with expansions or DLC factions and commanders. Cosmetics and skins sold separately. Free-to-play models exist but are rare on PC. Avoid pay-to-win units. Campaign content is the casual draw, ranked is the competitive draw.

### KPI expectations
Qualitative. Premium: campaign completion, review score, concurrent players over time, ranked participation, co-op and custom-game share, DLC attach. The ranked audience is a minority, so a strong campaign and AI skirmish matter for sales.

### Retention drivers
Competitive ladder. Co-op missions. Custom games and mods. Replays and streamers. Balance patches. Seasons.

### Content pipeline and production scope (estimates)
Unit art and animation, maps, campaign missions, voice and cinematics. A small RTS slice is 2 factions of 8–10 units each, 3 maps and a skirmish AI. Pathfinding, netcode (lockstep) and AI are the engineering cost centre. A full commercial RTS is a multi-year, large-team effort.

### Reference titles
- *Dune II* (Westwood): an early template.
- *Command & Conquer* series (Westwood and successors).
- *Age of Empires* series (Ensemble, World's Edge): historical RTS with civilizations.
- *StarCraft* and *StarCraft II* (Blizzard): asymmetric competitive RTS.
- *Warcraft III* (Blizzard): hero-led RTS with strong modding.
- *Company of Heroes* series (Relic): cover and squad-based RTS.
- *Total War* series (Creative Assembly): real-time battles with a turn-based campaign.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| A strong campaign and a fair, readable AI | Only multiplayer content and a thin AI |
| Readable units and clear counters | Visual clutter in large fights |
| Fair balance and regular patches | A dominant faction for months |
| A lower execution floor (queues, smart cast) | Execution speed excludes most players |
| Stable lockstep with desync handling | Desyncs and lag ruin matches |

### Innovation vectors
- Co-op and commander-based modes.
- Slower, more tactical "RTT" formats with fewer units.
- Procedural skirmish scenarios and roguelite campaigns.
- AI coaching and replay analysis.
- Cross-platform pad-friendly RTS with radial control.
- Mod-friendly platforms with workshop maps.

### Agent-buildability: 2/5
**Why low:**
- Balance of asymmetric factions, AI quality and "feel" need long human playtests.
- Lockstep determinism and pathfinding are expert engineering, though testable.

**What agents do well:**
- Economy and build-order sims, unit stat tables, map generation with fairness checks, replay tooling, AI scripts at easy tiers, command-log tests.

### Starter feature list (P0 vertical slice: 2 factions, 1 map, skirmish vs AI)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Fixed-step deterministic sim with command log (tech) | Same seed and commands give the same state hash over 1,000 replays |
| 2 | Resource gathering and one expansion site (economy) | Income per worker matches the table. Depletion works |
| 3 | Build and tech tree with 12 structures (progression) | Prerequisites enforced. Unit tests per building |
| 4 | 8 unit types per faction with counters (combat) | A sim confirms each counter wins at equal cost by the contract margin |
| 5 | Pathfinding with formations (gameplay) | 200 units reach a target with no stuck units in 100 trials |
| 6 | Fog of war and scouting (gameplay) | Hidden units do not appear in client data until seen |
| 7 | Control groups, hotkeys, production queues (ux) | Hotkeys remap and persist. Queues respect limits |
| 8 | Skirmish AI with three tiers (gameplay) | Win rates against the reference bot fall in the target bands (§0.1) |
| 9 | Replay record and playback (tech) | Playback reproduces the final hash. Speed control works |
| 10 | Minimap, alerts and selection UI (ui) | Alerts jump to the event. Selection caps and group rules documented |
| 11 | Lockstep for two players with hash check (tech) | A desync is detected within N ticks in a fault-injection test |

### Platform notes
- **PC.** The home of RTS. Mouse and keyboard with hotkeys, edge scrolling, multi-monitor, ranked ladders and mod workshops. Scale simulation cost for large unit counts. Anti-cheat and replay integrity matter (`pc-web-release`).
- **Console.** Pad-based RTS needs radial menus, cursor snapping, group selection by stick and a lower unit count. Treat it as a separate UI. Cross-play with PC is hard because of input (`console-pathway`).
- **Web.** Small, light RTS and tower-defence hybrids run in the browser. Keep unit counts low and use a deterministic sim for any multiplayer.
- **Mobile.** Real-time card battlers and lighter RTS fit touch better (see `strategy.md` §4). PC and console are premium with expansions, mobile is free-to-play.

## 2. Turn-based 4X (PC)

### Definition and player fantasy
Explore, expand, exploit and exterminate (or out-culture) on a turn-based map. Build cities, research technologies, manage economy and diplomacy, and aim for victory through conquest, science, culture or other paths. The fantasy is *a ruler who builds a civilization across the ages*: the long arc, the "one more turn" pull and the stories that emerge.

### Core loop
```
take turn: found / grow cities, set production, research, move units, diplomacy
  → end turn → AI moves → events → new options → repeat toward a victory condition
```

### Meta loops
- **Faction or civilization choice.** Unique units, abilities and starts.
- **Victory paths.** Conquest, science, culture, diplomacy.
- **Scenarios and difficulty ladders.**
- **Multiplayer (hot-seat, simultaneous or play-by-mail).**
- **Mods and map packs.**
- **Expansions.** New mechanics, factions and systems.

### Session profile
Estimate: 2–6 hour sittings, a full game of 6–20 hours, 30–100 hours to master. "One more turn" sessions overrun plans. Late-game turn time is a known issue, so design for fast AI turns.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| City growth and tile yields | economy & resources | Compounding growth. Check snowball with a sim |
| Tech or civic tree | progression & upgrade | Branching choices, not a single line |
| Hex or square map with terrain | exploration & traversal | Map generator with fairness checks |
| Unit combat with strength and terrain | combat | Readable odds preview (§0.2) |
| Diplomacy and AI personalities | social & competition | Distinct personalities, explainable decisions |
| Multiple victory conditions | progression & upgrade | Keep each path viable and visible |
| Happiness, stability or war weariness | economy & resources | A brake on expansion and warfare |
| Fog of war and exploration | exploration & traversal | Early game discovery pays hooks |

### Monetisation model and typical mix
Premium base game plus expansion packs and DLC (factions, scenarios, systems). Sales over many years via discounts. Mods extend life. Free-to-play is rare. Review the cost of pay-to-win DLC factions, since balance disputes damage trust.

### KPI expectations
Qualitative. Premium: hours played, completion of a full game (many players do not finish), review score, expansion attach and mod usage. Launch reviews often hinge on AI quality, UI clarity and stability, and early patches matter.

### Retention drivers
"One more turn". Replay value from factions and map seeds. Victory paths and challenge modes. Mods and scenarios. Expansions that add systems. Community stories and streamed games.

### Content pipeline and production scope (estimates)
Systems and AI dominate: a tech tree of 60–100 nodes, 10–20 factions, 50–100 units and buildings, map generator, AI and diplomacy. A tight slice is one faction pair, 25 techs, 15 units and buildings and a small map. Art is mostly icons, tiles and unit models. Late-game performance work is significant.

### Reference titles
- *Civilization* series (MicroProse, Firaxis): the template.
- *Master of Orion* series: space 4X.
- *Endless Legend* and *Endless Space* series (Amplitude): asymmetric factions.
- *Humankind* (Amplitude): culture-switching across eras.
- *Old World* (Mohawk Games): characters, orders and dynastic play.
- *Stellaris* (Paradox): real-time-with-pause space 4X (a blend with grand strategy).
- *Civilization* modding scene: data-driven mods as a model for longevity.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Early turns hook and the mid-game keeps choices interesting | The mid-game turns into a checklist |
| AI is competent and explains diplomacy | AI is passive or exploitable |
| UI shows yields, odds and breakdowns | Hidden numbers and opaque rules |
| Late-game turns are fast | Turn time grows to minutes |
| Distinct factions with identity | Factions are reskins |

### Innovation vectors
- Fewer, more meaningful cities and smaller maps.
- Simultaneous turns and shorter multiplayer formats.
- Story-driven events and characters inside the 4X frame.
- Procedural scenarios and roguelite campaigns.
- Better diplomacy via explainable AI and negotiation UIs.
- Cross-platform with pad-first UI.

### Agent-buildability: 3/5
**Why mid:**
- Rules, data tables, yields, map generation and turn logic are deterministic and testable. AI-vs-AI sims check balance and snowball.
- Tech trees and unit data suit agents.

**Why not higher:**
- AI that plays well across many systems, UI clarity and late-game performance need long iteration and human taste.

### Starter feature list (P0 vertical slice: small map, two factions, one victory path)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Deterministic turn engine with seeded RNG (tech) | Same seed and orders give the same state hash over 1,000 replays |
| 2 | Hex map generator, 40×25, with fairness check (level) | Start positions within a yield tolerance. Each start reaches 3 resources in N tiles |
| 3 | Cities with growth, tile yields and production queue (economy) | Yields match the table. A sim of 100 turns matches the closed-form check |
| 4 | Tech tree, 25 nodes (progression) | Prerequisites enforced. Effects apply to the stats they name |
| 5 | 12 unit types with combat odds preview (combat) | Previewed odds equal computed odds. Terrain modifiers verified |
| 6 | Fog of war and exploration (gameplay) | Hidden tiles are not in client state until seen |
| 7 | Utility AI for expansion, production, war (gameplay) | AI-vs-AI report: no stuck turns, snowball within the contract band |
| 8 | Simple diplomacy: peace, war, trade (social) | AI explains each decision in the tooltip. Treaties persist across saves |
| 9 | One victory condition with progress UI (meta) | Victory triggers on the stated rule. Progress bar matches state |
| 10 | Nested tooltips and encyclopaedia from data (ui) | Every term in a tooltip links to an entry. Entries generated from data |
| 11 | Auto-explore, auto-end-turn warnings, fast AI turns (ux) | Late-game AI turn under the contract time on the reference machine |

### Platform notes
- **PC.** Mouse hover tooltips, keyboard shortcuts, large high-resolution UI with scalable text, and mod workshops. Plan turn-time optimisation (multithreaded AI) early.
- **Console.** Cursor snapping, radial menus and context panels replace hover. Tooltips become panels. Console 4X is feasible but UI work is large (`platform-targets`, `console-pathway`).
- **Web.** Simple 4X and Civ-lite games are possible. Heavy AI turns need worker threads.
- **Mobile.** Large touch targets, shorter turns and sometimes async multiplayer. See `strategy.md` for mobile 4X. PC is premium plus expansions; mobile skews to premium or timers and ads.

## 3. Grand strategy

### Definition and player fantasy
A long-horizon simulation of states, dynasties or empires across centuries, run in real time with pause or in turns, with interlocking systems for politics, economy, diplomacy, war and culture. The fantasy is *a historical or alternate-history storyteller*: steering a nation, living with consequences and creating emergent stories.

### Core loop
```
pause → review map, events, advisors → set policy, orders, diplomacy, war plans
  → unpause (time passes) → events and crises → adjust → repeat across years
```

### Meta loops
- **Starting nation or character choice.** Each start is its own challenge.
- **Achievements and ironman runs.**
- **Scenarios and historical flavour events.**
- **DLC cycles** adding systems and regions.
- **Mods and total conversions.**
- **Multiplayer** with groups across long sessions.

### Session profile
Estimate: 2–5 hour sittings, campaigns of 50–300+ hours, played over weeks. Time speed controls pace. Players also enjoy "observer" mode and storytelling.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Real-time with pause and speed control | UX automation | Pause must allow all orders |
| Many interlocking systems (economy, diplomacy, war, culture) | economy & resources | Each system needs a legible loop |
| Events and decision chains | narrative & dialogue | Large authored event pool with conditions |
| Character, dynasty or pop simulation | social & competition | Entities need clear stats and portraits |
| Warfare with supply, terrain, fronts | combat | Abstracted, with automation tools |
| Diplomacy and alliances | social & competition | Needs explainable AI |
| Map modes and outliners | UX automation | Core to playability (§0.2) |
| Automation of routine tasks | UX automation | Delegation reduces micromanagement |

### Monetisation model and typical mix
Premium base game plus a long stream of expansion DLC and cosmetic or flavour packs. Customer reaction to DLC volume is a known sensitivity, so make base-game updates free and DLC add clear systems. Mods and community content extend life.

### KPI expectations
Qualitative. Premium: hours per player (very high), DLC attach, review score (especially "recent reviews" after patches), concurrent players and mod subscriptions. The audience is dedicated and smaller than casual strategy, with strong lifetime spend.

### Retention drivers
Emergent stories and "what if" starts. System depth. Frequent content patches and expansions. Mods. Community writing (AARs) and streams. Ironman and challenge runs.

### Content pipeline and production scope (estimates)
The largest data and writing load in this file: thousands of events, a map with provinces, hundreds of nations or characters and systems. AI must handle all of it. A tight slice is one region, 5–8 nations, 3 systems (economy, diplomacy, war) and 50 events. Full products need very large teams and years.

### Reference titles
- *Europa Universalis* series (Paradox): early-modern world.
- *Crusader Kings* series (Paradox): dynasty and character-driven.
- *Hearts of Iron* series (Paradox): WWII.
- *Victoria* series (Paradox): industrial-era economy and society.
- *Stellaris* (Paradox): space grand strategy.
- *Total War* series (Creative Assembly): turn-based campaign with real-time battles.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Systems interlock and produce stories | Systems stand alone and feel like spreadsheets |
| UI explains numbers and lets players find problems | Opaque modifiers and hidden rules |
| Automation handles boring tasks | Endless micromanagement |
| AI behaves plausibly over decades | AI is passive or collapses the world |
| Regular updates and modding | Neglected after launch |

### Innovation vectors
- Narrative-first grand strategy (character-driven).
- Smaller, tighter scenarios with shorter campaigns.
- Explainable AI and advisors that surface problems.
- Natural-language or LLM-assisted advisors with strict rules (verify claims against the sim).
- Better onboarding with guided scenarios.
- Co-op campaigns.

### Agent-buildability: 1/5
**Why very low:**
- Interlocking systems across centuries are almost impossible to verify with short gates. Balance emerges only over long play.
- AI behaviour at world scale and content volume (events, art, historical research) need teams.

**What agents do well:**
- Event authoring and condition checks, data-table validation, tooltip and encyclopaedia generation, mod tooling, headless AI-vs-AI runs for crash and stability tests.

### Starter feature list (P0 vertical slice: one region, 6 nations, 1920–1930 style short scenario)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Date and tick system with pause and 5 speeds (tech) | Time advances by the speed table. All orders allowed while paused |
| 2 | Province map with ownership and map modes (ui) | Ownership matches the data. Modes switch by key |
| 3 | Economy: income, expenses, treasury (economy) | A 10-year headless run matches a reference spreadsheet within 1% |
| 4 | Diplomacy: alliance, war, peace, with AI acceptance rules (social) | AI acceptance explained in the tooltip. Treaties obey the rule table |
| 5 | War: armies, supply, battles, war score (combat) | Battle results follow the formula. Supply attrition verified |
| 6 | 50 events with conditions and options (narrative) | Event validator finds no dead conditions. Each option has an effect |
| 7 | Utility AI for 5 nations (gameplay) | A 30-year headless run has no crashes. Borders change within the contract band |
| 8 | Outliner, alerts and nested tooltips (ui) | Alerts jump to the cause. Tooltips show modifier breakdowns |
| 9 | Save, load and ironman option (tech) | Round-trip restores the hash. Ironman blocks manual reloads |
| 10 | Data-driven content for mods (tech) | A sample mod changes a nation and loads without code edits |

### Platform notes
- **PC.** The native platform: dense UI, hover tooltips, keyboard shortcuts, multi-monitor and mods. Memory and simulation speed at late dates are central. Steam workshop is a major channel (volatile facts; `pc-web-release`).
- **Console.** Possible with a redesigned pad UI and simplified systems. Tooltip-heavy UI is the hardest part (`platform-targets`, `console-pathway`).
- **Web.** Light scenarios only. Not suited to full simulations.
- **Mobile.** Rare. Simplified turn-based variants exist. PC is premium plus DLC; mobile is premium or ads.

## 4. Roguelike deckbuilder

### Definition and player fantasy
A run-based game where the player builds a deck by choosing cards, relics and upgrades between fights, then fights turn-based encounters with a hand of cards. The fantasy is *a clever builder finding a broken combo*: shaping a deck into a machine and winning with synergy.

### Core loop
```
choose a path on the map → fight (draw hand, play cards using energy, read enemy intent)
  → reward: add a card, upgrade, relic, shop, event → deck grows → next fight
  → boss → act ends → run ends in win or loss → unlock, restart
```

### Meta loops
- **Character classes.** Each with its own card pool and play style.
- **Unlocks.** Cards, relics, characters and starting options.
- **Ascension or difficulty ladder.** Added challenge modifiers.
- **Daily and seeded runs.** Leaderboards.
- **Co-op or versus modes** in some titles.
- **Mods and card creation.**

### Session profile
Estimate: 30–60 minute runs, sittings of 1–3 hours. Fast restarts and "one more run" loops. Seeded daily runs add a short, shareable challenge.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Deck building from reward picks | collection & randomness | Pick 1 of 3 with skip. Skipping must be viable |
| Energy and hand size | economy & resources | 3 energy and 5 cards is a common starting frame |
| Enemy intent display | combat | Shows the next action. Core to decision quality |
| Relics and passive modifiers | progression & upgrade | Build-defining. Avoid pure stat boosts |
| Map with branching paths | exploration & traversal | Risk versus reward routes (elites, shops, rests) |
| Card upgrades and removal | progression & upgrade | Thinning the deck is a core tactic |
| Status effects and keywords | combat | A small, clear keyword set (§0.3) |
| Seeded runs | UX automation | Deterministic RNG streams per system |

### Monetisation model and typical mix
Premium, often with early access, then DLC characters. Cosmetic packs are possible. Mods drive longevity. Avoid paid power. Mobile ports are usually premium.

### KPI expectations
Qualitative. Premium: runs per player, win rate, ascension reach, review score, wishlist conversion and DLC attach. Fast restarts and variety drive hours played.

### Retention drivers
Build variety and combos. Difficulty ladders. New characters and cards. Daily seeds. Mod communities. Streams and clips of "broken" runs.

### Content pipeline and production scope (estimates)
Card and relic content: a character needs 60–80 cards (estimate), 20–40 relics and 3–5 enemy sets per act. Art is mostly card illustrations, enemy sprites and effects. A tight slice is 1 character, 40 cards, 20 relics, 15 enemies and 1 act. Balance dominates the schedule.

### Reference titles
- *Slay the Spire* (Mega Crit): the template.
- *Slay the Spire 2* (Mega Crit): sequel in Early Access from March 2026 (volatile facts).
- *Monster Train* (Shiny Shoe): lane-based defence deckbuilder.
- *Griftlands* (Klei): negotiation and combat decks.
- *Balatro* (LocalThunk): poker-hand roguelike with jokers.
- *Inscryption* (Daniel Mullins Games): deckbuilding with a horror-puzzle wrapper.
- *Hand of Fate* series (Defiant Development): card-driven adventure.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Decisions each turn and between fights are meaningful | One dominant card or relic decides most runs |
| Enemy intent is legible | Hidden information punishes good play |
| Synergies are discoverable and varied | Few viable builds |
| Runs are quick to restart | Long fights with fixed outcomes |
| Difficulty ladder keeps veterans engaged | Difficulty is only bigger numbers |

### Innovation vectors
- Hybrids with tactics grids, auto-battlers and base building.
- Co-op decks and shared turns.
- Card-crafting and modifier systems.
- Narrative-driven runs and persistent worlds.
- Solver-assisted balance and AI "ghost" opponents.
- Portrait mobile versions with one-hand play.

### Agent-buildability: 4/5
**Why high:**
- The rules are deterministic given the seed. Cards are data. Simulations (bot decks versus enemy sets) give win rates, difficulty curves and outlier cards. The UI is structured.

**Why not 5:**
- Card art, effects, juice and the feel of a satisfying combo need human taste. Balance across thousands of builds needs long play.

### Starter feature list (P0 vertical slice: one class, one act)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Deterministic combat engine with seeded RNG streams (tech) | Same seed and plays give the same outcome over 1,000 replays |
| 2 | Energy, hand, draw and discard cycle (gameplay) | Draw pile reshuffle follows the rule. Hand size capped per rule |
| 3 | 40 cards as data with keyword effects (content) | Every card loads from data. Unit tests cover each keyword |
| 4 | Enemy intent system with 15 enemies (gameplay) | Displayed intent equals executed action in 10,000 simulated turns |
| 5 | Map with 12–15 nodes, elites, shop, rest (meta) | Map generator passes reachability check. Node odds from table |
| 6 | Rewards: pick 1 of 3 cards, skip, upgrade, remove (meta) | Offer odds match the rarity table within 1% in a 10,000-roll sim |
| 7 | 20 relics with passive effects (content) | Each relic unit tested. No relic breaks the engine |
| 8 | Bot player with three skill levels and a scripted archetype (qa) | Win rate bands per level. No card above the play-rate threshold |
| 9 | Seeded and daily runs with seed display (meta) | Same seed reproduces map, rewards and enemies |
| 10 | Run save and resume (tech) | Resume restores the exact state mid-fight |
| 11 | Undo within a turn when no hidden info is revealed (ux) | Undo restores the exact prior state |
| 12 | Card and keyword tooltips with glossary (ui) | Every keyword links to its definition. Numbers show modifier sources |

### Platform notes
- **PC.** Mouse hover and click suit the genre. Add keyboard shortcuts, fast-forward animations and mod support (card data and Lua or similar). Early Access with frequent patches is a common release plan (`pc-web-release`).
- **Console.** Pad navigation with a cursor-snap card fan, trigger shortcuts and clear focus states. Cross-save with PC is valued (`console-pathway`).
- **Web.** Small deckbuilders work well in the browser. Persist runs to local storage.
- **Mobile.** Touch drag-to-play works. Larger text and one-hand play are needed. Mobile ports are usually premium; PC and console are premium plus DLC.

## 5. Digital collectible / living card game

### Definition and player fantasy
A two-player card game with a large card pool, deck construction and ranked play, delivered digitally. Collectible versions sell random packs. Living card games (LCGs) sell fixed expansions with no randomness. The fantasy is *a deck-builder and duellist*: making a deck, mastering it and testing it against others.

### Core loop
```
build or pick a deck → queue a match (ranked, casual, event) → play 5–20 min
  → rank and rewards → earn or buy cards → refine deck → next match
```

### Meta loops
- **Ranked seasons and ladders** (see `competitive-pvp.md` §0 and §5).
- **Set releases and rotation.** New sets every few months, old sets rotate out of the main format.
- **Collection and crafting.** Dust or wildcards to build specific cards.
- **Events and drafts.** Arena or limited formats.
- **Single-player adventures** and puzzles.
- **Esports and creator programmes.**

### Session profile
Estimate: 5–20 minute matches, sittings of 30–120 minutes. Frequent short sessions plus longer deck-tuning sessions. Competitive players play many matches per day.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Deck construction with copy and size limits | collection & randomness | §0.3 maths |
| Resource system (mana, energy, lands) | economy & resources | Curve and mulligan rules |
| Card types and keywords | combat | Evergreen keyword budget |
| Rotation and formats | progression & upgrade | Keeps the environment fresh |
| Crafting and collection | collection & randomness | Sets the cost of competitive decks |
| Hidden information and server authority | social & competition | Shuffles on the server |
| Ranked matchmaking and anti-cheat | social & competition | See `competitive-pvp.md` §0 |
| Replays and spectating | UX automation | Command-log (§0.4) |

### Monetisation model and typical mix
Free-to-play with packs, bundles, battle passes and cosmetics, or premium with fixed expansions (LCG). Paid random packs fall under loot-box regimes (see `rpg-gacha.md` §0.3) and need odds disclosure and pity. A crafting system and a generous free path control the cost of a competitive deck. Disclose total cost to complete a set.

### KPI expectations
Qualitative. Free-to-play: conversion, ARPPU, set-launch spikes, ranked participation and retention by cohort. Premium: expansion attach and review score. The set cadence drives revenue and engagement peaks, so schedule operations around it (`liveops`).

### Retention drivers
Deck experimentation and new sets. Ranked seasons. Collection goals. Events and drafts. Community content and streamers. Esports.

### Content pipeline and production scope (estimates)
Each set is 100–300 cards (estimate) with art, effects and balance testing. A rules engine with hundreds of interactions needs a strong test suite. Server infrastructure, matchmaking, anti-cheat and customer support are a long-term cost. A fixed-set slice is 120 cards, one format and a bot ladder.

### Reference titles
- *Magic: The Gathering* and *Magic: The Gathering Arena* (Wizards of the Coast): the origin and its digital form.
- *Hearthstone* (Blizzard): accessible digital-first CCG.
- *Legends of Runeterra* (Riot): interactive turn structure.
- *Gwent* (CD Projekt Red): lane-based card game.
- *Marvel Snap* (Second Dinner): short matches, one-hand play.
- *Netrunner* (asymmetric LCG) and *Arkham Horror: The Card Game* (Fantasy Flight): living card game model.
- *Yu-Gi-Oh! Master Duel* (Konami).

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| A free path to a competitive deck | Paywalled meta and high cost to play |
| Clear rules UI and readable stack | Hidden triggers and unclear resolution |
| Regular, balanced sets and fast hotfixes | Power creep and stale metas |
| A strong rules engine with few bugs | Rules bugs that decide matches |
| Fair matchmaking and good onboarding | New players meet veterans |

### Innovation vectors
- Short-match formats and one-hand play.
- Fixed-set (LCG) digital models without packs.
- Co-op and campaign modes.
- Deck-sharing and creator tools.
- AI opponents for practice and deckbuilding.
- Cross-platform with mobile and PC.

### Agent-buildability: 2/5
**Why low:**
- A live CCG is a rules engine, a server, a content treadmill and a competitive balance process. Gates cannot verify metagame health.
- Art volume and set design need teams.

**What agents do well:**
- A rules engine for a fixed small set, card data validation, bot ladders for balance and win-rate tables (§0.3), deck-builder UI and tests.

### Starter feature list (P0 vertical slice: fixed set of 120 cards, bot ladder)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Deterministic rules engine with server-side shuffle (tech) | Same seed and actions reproduce the final state hash over 1,000 replays |
| 2 | 120 cards as data with 12 keywords (content) | Card validator passes. Unit tests per keyword |
| 3 | Resource system with mulligan (gameplay) | Mulligan odds match §0.3 numbers in a sim |
| 4 | Turn structure with priority and a stack or queue (gameplay) | Resolution order tested on 30 scripted interactions |
| 5 | Deck builder with limits and validation (ui) | Illegal decks are rejected. Saved decks reload |
| 6 | Four archetype bots (qa) | Bot ladder: no archetype outside the contract band across 10,000 matches |
| 7 | Per-card win-rate and play-rate report (qa) | Outliers flagged by threshold. Report in CI |
| 8 | Collection and crafting with disclosed odds (economy) | Pack odds shown before purchase. Pity matches the calculator |
| 9 | Ranked ladder with a rating system (social) | Rating updates follow the formula. Season reset rule tested |
| 10 | Match log and replay viewer (tech) | Replay reproduces the match. Log lists each event |
| 11 | Reconnect and timeouts (tech) | A dropped client resumes the match. Timers enforce the rule |

### Platform notes
- **PC.** Mouse and keyboard, large boards, hover card previews, deck import and export, and streamer tools. Anti-cheat is mostly server-side. Steam and standalone launchers are both common (`pc-web-release`).
- **Console.** Rare but possible, with a cursor and card-fan UI and platform rules for in-app purchases (`console-pathway`).
- **Web.** Browser clients are common for card games. Server authority makes this safe.
- **Mobile.** The largest card-game audience, with short matches and portrait layouts. See `competitive-pvp.md` §5. Cross-platform accounts, one rules engine and one economy are the usual goals.

## 6. Tactics RPG (PC/console)

### Definition and player fantasy
Turn-based battles on a grid with a party of characters who have classes, abilities and growth, wrapped in a story and a campaign. The fantasy is *a tactician with a growing squad*: positioning, abilities, terrain and the attachment to named characters. Mobile tactics are in `strategy.md` §6; this playbook covers the longer PC and console form.

### Core loop
```
choose squad and gear → enter mission → each turn: move, act, use abilities (read enemy intent)
  → win or lose mission → XP, loot, story → upgrade squad → next mission
```

### Meta loops
- **Class and job systems.** Promotion, class change, skill trees.
- **Gear and economy.** Weapons, armour, consumables, shops.
- **Base or camp.** Recruit, train, talk to characters.
- **Campaign map and story.** Branching missions.
- **Permadeath or ironman modes.**
- **Challenge, endless and modded content.**

### Session profile
Estimate: 20–60 minute missions, sittings of 1–3 hours, 20–60 hour campaigns. Players study the board and plan, so turn time is long and enemy-turn speed matters.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Grid movement and range | combat | Readable overlays for move and attack range |
| Hit chance with cover, flank, height | combat | Show the exact number. Clamp 1–99% |
| Action points or move-and-act | combat | Define clearly. Keep consistent across classes |
| Classes, abilities and cooldowns | progression & upgrade | Data-driven abilities with tests |
| Enemy intent and telegraphs | combat | Turn the fight into a puzzle |
| Permadeath option | progression & upgrade | Offer a mode choice |
| Mission objectives beyond "kill all" | exploration & traversal | Escort, defend, extract, timer |
| Squad progression and relationships | progression & upgrade | Attachment drives retention |

### Monetisation model and typical mix
Premium with DLC (missions, classes, characters). Free-to-play gacha versions exist on mobile (see `strategy.md` §6 and `rpg-gacha.md`). Avoid selling power on premium titles. Mods extend life on PC.

### KPI expectations
Qualitative. Premium: campaign completion, permadeath mode share, review score, DLC attach and mod activity. Completion is lower on long campaigns, so mission variety and pacing matter.

### Retention drivers
Squad attachment and growth. Mission variety. Hard modes and permadeath. Story branches. DLC campaigns and mods. Challenge runs and speed-runs.

### Content pipeline and production scope (estimates)
Class and ability design, maps and enemy sets, characters, story and music. A tight slice is 4 classes, 12 abilities, 6 missions and 3 enemy types. A full game is 30–50 missions and 10–20 classes. Maps need solver checks.

### Reference titles
- *Fire Emblem* series (Intelligent Systems): permadeath tactics with relationships.
- *Final Fantasy Tactics* (Square): job-based tactics RPG.
- *XCOM: Enemy Unknown* and *XCOM 2* (Firaxis): cover-based tactics with a strategic layer.
- *Into the Breach* (Subset Games): deterministic puzzle-tactics.
- *Tactics Ogre* series (Quest, Square Enix).
- *Triangle Strategy* (Square Enix, Artdink): branching story tactics.
- *Wargroove* (Chucklefish) and *Advance Wars* (Intelligent Systems): grid wars.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Every turn offers readable, meaningful options | Opaque RNG makes good plans fail randomly |
| Enemy intent is legible | Tiny tiles and unclear overlays |
| Missions vary objectives | "Kill all enemies" on every map |
| Fair difficulty modes and an undo option | Permadeath with no mode choice |
| Fast enemy turns and animation skip | Long enemy turns with no speed-up |

### Innovation vectors
- Deterministic puzzle-tactics with no hit RNG.
- Roguelite tactics runs and deckbuilding hybrids.
- Solver-validated procedural missions.
- Story-driven branching campaigns.
- Pad-first UI for couch play.
- Modding and map-making tools.

### Agent-buildability: 4/5
**Why high:**
- Grids, turns and determinism suit agents. Enemy AI by search or utility scoring. Solvers prove missions solvable and estimate difficulty. Map generators and rule tests are standard.

**Why not 5:**
- Ability animation, camera work, story and character writing need human iteration.

### Starter feature list (P0 vertical slice: 4 classes, 6 missions)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Grid sim-core with turns and action points (gameplay) | Deterministic. Same inputs give identical outcomes over 1,000 replays |
| 2 | Movement range, pathfinding and danger overlay (ui) | Reachable tiles match BFS. The overlay shows every telegraphed hit |
| 3 | Cover, flank and height hit model (gameplay) | Formula unit-tested. Displayed % equals computed %. Clamped 1–99 |
| 4 | 4 classes × 3 abilities from data (gameplay) | Each ability has tests for targeting and effect |
| 5 | Enemy intent display with 4 enemy types (gameplay) | Intent shown before the player turn matches the executed action |
| 6 | Utility AI for enemies (gameplay) | Beats a random policy at least 90% of the time and loses to the scripted solution |
| 7 | 6 missions with varied objectives (content) | Solver proves each solvable. Bot win rate within the difficulty band |
| 8 | XP, promotion and one gear slot (meta) | Curve from `progression_calc.py`. Promotion unlocks the listed ability |
| 9 | Move confirm and undo (ux) | Undo restores the exact prior state. No action fires without confirm |
| 10 | Permadeath option and ironman save (meta) | The mode persists. A casualty is removed only in permadeath |
| 11 | Enemy-turn speed-up and animation skip (ux) | The toggle keeps the sim result identical |
| 12 | Pad and mouse UI with cursor snapping (input) | All actions reachable by either input. Focus is always visible |

### Platform notes
- **PC.** Mouse hover, right-click context menus, keyboard shortcuts and mod support (maps, classes). Scalable text for dense stats.
- **Console.** The genre is strong on handheld and couch. Cursor snapping to units and tiles, quick toggles for overlays and fast enemy turns are essential. Cross-save and platform content rules (`console-pathway`, `platform-targets`).
- **Web.** Small grid tactics work in a browser. Persist missions and keep assets light.
- **Mobile.** Portrait layouts, tap-and-confirm and shorter missions. See `strategy.md` §6. Premium on PC and console, gacha or premium on mobile.

## Volatile facts (as of Oct 2026 — verify before relying)

- *Slay the Spire 2* entered Steam Early Access on 5 March 2026, PC only. Reports say console versions are expected with the 1.0 release and that Early Access is expected to last one to two years. Treat the timeline as unconfirmed — [Shacknews](https://www.shacknews.com/article/147940/slay-the-spire-2-early-access-release-date), [Outlook India](https://respawn.outlookindia.com/gaming/gaming-news/slay-the-spire-2-release-date-confirmed-early-access-in-march)
- Steam charges a US$100 submission fee per product (Valve's onboarding page). The 30/25/20% revenue-share tiers at US$10 million and US$50 million are reported by secondary sources and should be checked in Steamworks — [Steamworks onboarding](https://partner.steamgames.com/doc/gettingstarted/onboarding), [Neowin](https://www.neowin.net/news/valve-introduces-new-revenue-share-tiers-for-steam-promising-bigger-cuts-for-studios/)
- Loot-box and paid-random regimes apply to collectible card packs in every playbook here. Details and sources: `skills/genre-playbooks/references/rpg-gacha.md` volatile facts.
- Mobile strategy, tower defence, auto-battler and mobile CCG market figures are in `skills/genre-playbooks/references/strategy.md` and `skills/genre-playbooks/references/competitive-pvp.md` volatile facts.
- Workshop and mod-hub terms, console programme rules and cross-play policies change. Confirm in the vendor's current documentation before committing (`pc-web-release`, `console-pathway`).
- Session lengths, AI difficulty bonuses (+10/25/50%), card counts per set and content volumes in this file are design estimates, not sourced figures. The hypergeometric probabilities are the author's own arithmetic.

## Related skills
- `mechanics-codex`: cards for every mechanic named above.
- `balance`: card and unit win-rate tables, probability checks and sim runs.
- `economy-design`: resource curves, snowball and sinks.
- `game-architecture`: sim-core, determinism, command logs and mod loading.
- `gameplay-programming`: AI, pathfinding and rules engines.
- `multiplayer-backend`: lockstep, server authority, matchmaking and replays.
- `level-design`: tactics maps, 4X map generation and mission design.
- `procedural-generation`: solver-validated maps and runs.
- `qa-testing`: bots, replay tests and balance sims.
- `liveops`: set rotations, seasons and event calendars.
- `monetization`: pack and expansion models, ethical offers.
- `legal-ethics`: loot-box law and mod content policy.
- `accessibility-localization`: dense-UI text scaling, colour-blind support and string pipelines.
- `platform-targets`: input, performance tiers and saves.
- `pc-web-release`: Steam, workshop and web release steps.
- `console-pathway`: console programmes and certification.
