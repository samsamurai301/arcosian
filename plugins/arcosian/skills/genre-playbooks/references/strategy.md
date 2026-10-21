# Strategy Playbooks

Strategy is the top-grossing category on mobile, and it varies more than any other in how agent-buildable it is. This file holds six playbooks in a shared 14-part template:

1. 4X / SLG on persistent servers (*Rise of Kingdoms*, *Last War*, *Whiteout Survival* style)
2. Base-builder with async raiding (*Clash of Clans*)
3. Tower defense
4. Real-time card battler / RTS-lite (*Clash Royale*)
5. Auto-battler
6. Turn-based tactics

Four foundations come first because several playbooks rely on them: time-as-currency math, combat resolution (Lanchester's laws), deterministic simulation for async PvP, and persistent-server structure. The pattern for an agent pipeline is clear. Single-player tower defense, auto-battlers with async ghost opponents, and grid tactics are deterministic, solver-verifiable and fit bots well (4–5/5). 4X/SLG makes the most money but scores 2/5, because its product is a live, many-player server world plus a UA machine, not client code. Market numbers live in the dated volatile-facts section.

## Contents

| § | Playbook | Session profile (estimate) | Primary monetization | Agent-buildability | First project for an agent pipeline? |
|---|---|---|---|---|---|
| 0 | [Shared foundations](#0-shared-foundations) | — | — | — | Read first |
| 1 | [4X / SLG](#1-4x--slg-persistent-server-strategy) | 8–20 check-ins × 1–5 min + war windows | Deep IAP, VIP, bundles, speedups | 2/5 | No, single-player city slice only |
| 2 | [Base-builder raiding](#2-base-builder-with-async-raiding) | 4–10 × 2–6 min | Builders, speedups, season pass | 3/5 | Possible, with async replays |
| 3 | [Tower defense](#3-tower-defense) | 3–10 min levels | Premium or F2P hybrid | 5/5 (PvE) | Yes |
| 4 | [Card battler / RTS-lite](#4-real-time-card-battler--rts-lite) | 3–4 min matches | Card progression, pass, cosmetics | 3/5 | Only with deterministic lockstep and a bot ladder |
| 5 | [Auto-battler](#5-auto-battler) | 10–40 min runs | Cosmetics, packs, pass | 4/5 | Yes, async ghosts |
| 6 | [Tactics](#6-turn-based-tactics) | 5–20 min missions | Premium or F2P gacha | 4/5 | Yes |
| — | [Volatile facts](#volatile-facts-as-of-oct-2026--verify-before-relying) | — | — | — | Check before quoting numbers |

## How to use these playbooks

- Copy the core loop into `contract.json → loops[]`. Set `meta.genre: "strategy"` and `meta.subgenre` to the playbook slug, then set `technical.multiplayer` (`none`, `async` or `realtime`). That field drives cost and agent-buildability more than anything else.
- Turn the starter feature list into P0 `features.json` entries with `gs.py feature add`. The acceptance criteria are written so each maps to `unit` or `playthrough` gate evidence (bots, sims, replays).
- Mechanic category labels used here: combat, build-craft, collection & randomness, progression & upgrade, economy & resources, time & energy, social & competition, exploration & traversal, live events, UX automation. Resolve them against the `mechanics-codex` taxonomy with `gs.py kb "<mechanic>" --skill mechanics-codex`.
- KPI statements are qualitative unless sourced. Use the anchors in the volatile-facts section, then fit real curves after soft launch with `retention_ltv.py fit`.

## 0. Shared foundations

### 0.1 Time as currency (builds, research, training)
Timer-driven strategy sells *time*. Use a geometric timer curve and price speedups against it.

```
Timer for level L        T(L) = T0 · g^(L−1)
Total time to reach L    S(L) = T0 · (g^L − 1) / (g − 1)
Worked example (T0 = 60 s, g = 1.35):  L10 ≈ 15 min · L20 ≈ 5.0 h · L25 ≈ 22.4 h · L30 ≈ 100 h
                                        S(25) ≈ 3.6 days · S(30) ≈ 16.1 days   (one queue, my arithmetic)
```

- **Queues multiply the clock.** Two build queues halve the calendar time, which is why a second builder or queue is a classic first purchase. Model queue count as a resource in `economy_sim.py`.
- **Social speedups.** Alliance "help" taps each cut the remaining time, often by a percentage with a floor in minutes. This turns the alliance into a time-production engine and an obligation network. Cap helps per timer so whales can't buy alliance time.
- **"Free finish" threshold.** Letting timers under N minutes complete instantly removes the most irritating micro-waits. Pick N so the first 10 minutes of play have no visible waiting.
- **Speedup pricing.** Price per minute should fall with bulk, but never so low that premium currency makes the timer curve irrelevant for mid spenders. Check the real-money cost of a full max-out against the contract's spend ceilings.

### 0.2 Combat resolution: Lanchester's laws
For army-versus-army resolution (SLG marches, base raids, auto-battles with many units), Lanchester's models predict how size and quality trade off:

```
Aimed fire (square law):  dA/dt = −b·B,  dB/dt = −a·A   →  strength ∝ a · A²
Worked example: A = 100 units (a = 1.0) vs B = 70 units (b = 1.5)
  A strength 10,000 vs B 7,350 → A wins with √(100² − 1.5·70²/1.0) ≈ 51 survivors
Melee one-on-one (linear law): strength ∝ a · A   (numbers matter far less)
```

Design implications: concentration of force (rallies) becomes optimal under square-law resolution, and troop *tier* multipliers compound with numbers. That is fine for SLG, where whales leading rallies is part of the fantasy, and dangerous in fair PvP. Always produce a battle report that explains the outcome (counter bonus, tier gap, hero buffs). Players forgive losses they can understand.

### 0.3 Deterministic simulation for async PvP and bots
Async raids, ghost opponents and replays all need **a deterministic sim-core**:
- Fixed timestep.
- Seeded PRNG.
- Integer or fixed-point math for anything replayed across devices.
- No float-order dependence.
- Inputs logged as `(tick, action)`.

The server re-simulates attacks for validation (anti-cheat) and the defender watches the replay. The same core powers bot balance runs and the `playthrough` gate. See `game-architecture` (sim-core plus presentation) and `gameplay-programming`.

### 0.4 Persistent-server structure (SLG and some base-builders)
A "kingdom" or server holds a capped population (often thousands) and opens on a cadence. Server age unlocks content in stages (season gates). Cross-server wars (KvK) recycle competition, and migration or merges rebalance populations. This is backend and live-ops work: world-map simulation server-side, march timing, rally scheduling, event calendars by time zone. Load `multiplayer-backend` and `liveops`.

## 1. 4X / SLG (persistent-server strategy)

### Definition and player fantasy
Each player builds a city, trains troops, gathers on a shared world map, joins an alliance, and fights over territory in seasonal wars on a persistent server. The 2023-era leaders (*Last War*, *Whiteout Survival*) put a **casual front door** in front of the deep game: a survivor-style lane shooter, a rescue puzzle or a squad-merge mini-game. These front doors match the UA creatives and smooth the first session. The fantasy is being *a ruler rising among real rivals*: power, status, alliance belonging, politics and revenge.

### Core loop
```
collect resources → queue builds / research / training (timers)
  → speed up (alliance help, items, premium currency) → power ↑
  → gather, hunt, rally on world map → rewards → daily themed events
  → alliance war / KvK → status, territory buffs → collect resources
```

### Meta loops
- **Heroes.** Gacha-recruited commanders with skill trees lead marches. This is a second monetization axis.
- **Alliance.** Help taps, alliance tech, territory, rallies, gifts from members' purchases (a social pressure lever, so use it responsibly).
- **Server lifecycle.** Season gates by server age, KvK, migration, merges.
- **Event calendar.** Rotating daily themed point events (build day, train day, research day) that reward specific spending of time and resources. Weekly and monthly tournaments sit on top.
- **VIP levels.** Permanent perks bought with spend. This is the whale progression track.

### Session profile
Estimate: very high frequency, 8–20 check-ins a day of 1–5 minutes to collect, queue and help, plus synchronized prime-time windows for rallies and wars. Late-game and high-spend players play for hours. Push notifications (timer done, under attack, rally starting) are core UX, so they need careful consent and frequency caps.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Build/research/training queues with timers | time & energy | §0.1. The queue count is a key purchase |
| Speedups (items, premium currency, alliance help) | time & energy; social & competition | The core monetization primitive |
| World-map marches, gathering, scouting, rallies | social & competition; exploration & traversal | March time = distance / speed. Rallies concentrate force (§0.2) |
| Troop tiers + counter triangle + hospital | combat; economy & resources | Wounded troops (healing costs resources) soften losses |
| Peace shield / new-player protection | social & competition | Protects onboarding. A purchasable shield is a known pain point |
| Hero gacha + skill levels | collection & randomness | Apply loot-box compliance (see `skills/genre-playbooks/references/rpg-gacha.md` §0.3) |
| Power score | social & competition | Status signal and matchmaking proxy |
| Casual front-door mini-game | UX automation; progression & upgrade | Feeds resources into the city. Must not be a bait-and-switch |

### Monetization model and typical mix
Deep IAP with the longest spend ladder on mobile. The typical mix is qualitative and unsourced:
- Value bundles with progression triggers.
- Speedups and resource packs.
- Hero shards.
- VIP points.
- Monthly cards and a battle pass.
- Event-tier packs.
- Cosmetic city skins and march skins.

Ads are minimal. **Ethics flags:**
- Inflated "value %" anchors ("5000% value!").
- Alliance-gift social pressure.
- Purchasable shields that let whales attack and then turtle.
- Endless pop-up offers.

Doctrine item 8 applies. Have the `critic` agent audit the offer cadence.

### KPI expectations
Partly sourced. SLG titles led grossing in Q1 2026 (*Last War*, *Whiteout Survival*), and secondary summaries call 4X 2025's hot genre (volatile facts). Everything else here is qualitative. D1 tends to sit below casual because of complexity, though the casual front doors aim to fix this. Long-term retention among alliance-active players is high. UA costs and payback windows are among the longest in mobile. No sourced CPI or ROAS figures were found.

### Retention drivers
Alliance obligation and friendship. Server-wide events and KvK seasons. Revenge and rivalry. Power progression with visible status. The daily event calendar. Sunk investment. Season resets that give mid spenders a fresh shot.

### Content pipeline and production scope (estimates)
Systems and live operations dominate: event templates, seasonal map rule sets, hero releases, balance, anti-cheat, customer service and multilingual community management. A creative factory for UA produces hundreds of video and playable ads. Rough estimate: 50–200+ people and 2–3 years to global launch, plus a large UA budget. Not an indie-feasible genre at full scale.

### Reference titles
- *Game of War: Fire Age* (Machine Zone, 2013): an early 4X spend ladder.
- *Clash of Kings* (Elex, 2014).
- *Lords Mobile* (IGG, 2016).
- *Rise of Kingdoms* (Lilith, 2018): civilization flavour, open-field marches.
- *State of Survival* (FunPlus).
- *Call of Dragons* (Farlight, 2023).
- *Whiteout Survival* (Century Games, 2023): survival theme with a casual front door.
- *Last War: Survival Game* (FirstFun, 2023): a lane-shooter front door.
- *Top War* (RiverGame): merge front door.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| An accessible front door plus deep social war | Onboarding dumps 10 systems in the first hour |
| Alliances get real tools: rally timers, translation, roles | Whales crush a young server and it dies |
| A server lifecycle that refreshes competition (KvK, seasons, migration) | Server populations become imbalanced with no merge or migration plan |
| A UA creative machine with sustainable payback | UA is underfunded, so the server never reaches critical mass |
| F2P players have roles: gatherers, rally fillers, scouts | Offer spam and deceptive value claims drive reviews down |

### Innovation vectors
- Casual and hybrid-casual front doors converging with deep SLG.
- Seasonal formats with full or partial resets.
- Co-operative PvE alliance content alongside war.
- Built-in machine translation of multinational alliance chat.
- Cross-platform PC clients.
- Calmer, more casual SLG variants with lower conflict.

### Agent-buildability: 2/5
**Why low:**
- The money is in a persistent many-player server world, alliance systems, a staffed live-ops calendar and a UA engine. None of that is verifiable by client gates.
- Multi-thousand-player dynamics can only be approximated with agent simulations.

**What agents do well:**
- Timer economies (`economy_sim.py` with `per_session` sources and `gate` nodes).
- Battle formula sims.
- City UI, the casual front-door mini-game.
- A single-player city plus world map against AI rivals as a slice.

### Starter feature list (P0 vertical slice: city + mini world map vs AI)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | City grid with 6 building types and upgrade timers (meta) | Timers follow `T0 · g^(L−1)` from the tuning table. Unit tests check levels 1–25 |
| 2 | Two build queues + speedups + free-finish threshold (meta) | Queue logic is correct across backgrounding. Timers under N minutes finish free |
| 3 | Resource production, storage caps, offline accrual (economy) | Accrual is closed-form from the server timestamp. Caps enforced |
| 4 | Research tree, 10 nodes (meta) | Prerequisites enforced. Buffs apply to the sim stats they name |
| 5 | Troops: 3 types × 2 tiers + counter triangle (gameplay) | A sim confirms each counter wins at equal power by the contract margin |
| 6 | World map 100×100: resource nodes, AI camps, march timing (gameplay) | March ETA = distance / speed, verified. Gathering yields the table |
| 7 | Battle resolution + readable battle report (gameplay) | Lanchester-based resolver is deterministic. The report lists the top 3 outcome factors |
| 8 | Hospital / wounded troops (economy) | A loss returns wounded per formula. Healing consumes resources |
| 9 | Hero recruit with pity + 1 skill per hero (monetization) | Matches `gacha_calc.py`. Odds disclosed before purchase |
| 10 | Mock alliance with bot members: help reduces timers (meta) | Each help cuts per the rule. Helps per timer capped |
| 11 | Daily themed point event (liveops) | Points awarded for the themed actions only. Tiers pay out at reset |
| 12 | Casual front-door mini-game, one lane-shooter level (gameplay) | The scripted playthrough clears it. The reward lands in the city wallet |
| 13 | New-player peace shield (meta) | AI raiders cannot target a protected city. Expiry warning shown |

## 2. Base-builder with async raiding

### Definition and player fantasy
The player builds and fortifies a base, then raids other players' bases asynchronously: the defender is offline and the AI runs their defences. Loot comes from the defender's storage. The fantasy is being *the chief, the architect and the raider*: designing an unbreakable base and pulling off the perfect three-star attack.

### Core loop
```
collect resources → upgrade buildings / defenses (builders are the scarce worker)
  → train army + spells → attack (≈3 min raid: deploy, funnel, spell timing)
  → loot + trophies → upgrade → collect resources
```

### Meta loops
- **Town-hall tiers.** Each tier unlocks new buildings and caps. A major tier ships about once a year (observed in *Clash of Clans*).
- **Clan.** Troop donations, clan wars on a fixed schedule, war leagues, clan games.
- **Trophies and leagues.** Ladder matchmaking with seasonal resets.
- **Heroes.** Long upgrade timers. Often the longest pole in progression.
- **Secondary village or mode.** A second base with different rules to refresh the loop.
- **Season pass and events.** Temporary troops, event challenges.

### Session profile
Estimate: 4–10 sessions a day of 2–6 minutes (collect, start upgrades, one or two attacks). Clan-war attacks are scheduled. Raids last about 3 minutes in *Clash of Clans*. Base design sessions can run long.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Builders as the worker constraint | time & energy | Parallel upgrade slots. Selling builders is a classic, generous-feeling premium purchase |
| Async raid vs AI-run defences | combat; social & competition | Requires a deterministic sim and server re-simulation (§0.3) |
| Star scoring (destruction %, core destroyed) | combat | Partial success always pays something, so losses feel productive |
| Loot as a % of storage + loot cart | economy & resources | Protect part of storage so defenders aren't wiped |
| Shield after being raided | social & competition | Prevents revenge-farming |
| Trophy matchmaking with town-hall weighting | social & competition | Prevents seal-clubbing |
| Layout editor + shareable base links | build-craft | UGC: base design is a hobby inside the game |
| Troop donation | social & competition | The cheapest strong clan glue |

### Monetization model and typical mix
Premium currency for extra builders, speedups and resource top-ups. A season pass. Cosmetic hero skins and scenery. Event offers. The Supercell model is generous, uses little randomness and is tuned for very long lifetimes. Ads are rare. Keep paid speedups from deciding war outcomes.

### KPI expectations
Qualitative, because no sourced ranges were found. *Clash of Clans* has been live since 2012, which shows how long a raiding base-builder can last. D30+ retention is strong among clan members. Clan participation rate is the leading indicator to track.

### Retention drivers
Something always finishing (builder timers). The clan war schedule. Trophy seasons. Base-design mastery. Annual town-hall tiers. Events with temporary troops. Revenge.

### Content pipeline and production scope (estimates)
Content is buildings, troops, heroes and defences at multiple levels, each with art and animation in 2.5D or 3D. Balance runs across town-hall tiers. Server attack validation and replays. Rough estimate: 10–40 people in the core team over 18–36 months. Supercell is known for small "cell" teams and for publicly killing spin-offs in soft launch.

### Reference titles
- *Clash of Clans* (Supercell, 2012): the template.
- *Boom Beach* (Supercell, 2014): a PvE map plus raiding.
- *Castle Clash* (IGG, 2013).
- *DomiNations* (Big Huge Games, 2015): historical eras.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| A raid is a 3-minute skill expression with clear feedback | Raids are pure stat checks |
| Defence feels meaningful even while offline (replays, shields) | Defenders lose everything and churn |
| Clan systems carry retention | Clan tools are shallow |
| Generous builder and timer pacing with clear goals | Timer walls stack up with nothing to do |
| Annual big tiers plus steady events | Content gaps and stale metas |

### Innovation vectors
- Co-op raids.
- Roguelite attack modes using your army.
- Base-layout UGC and creator tournaments.
- Esports-style replay sharing.
- Hybrid PvE campaigns.
- Calmer variants that remove resource loss.

### Agent-buildability: 3/5
**Why mid:**
- Async raids on a deterministic core suit agents well. Bots attack layouts thousands of times to estimate three-star rates and defence strength.
- Replay validation doubles as the `playthrough` gate.

**Why not higher:**
- 2.5D/3D building and unit art plus animation at many levels.
- Server-side validation and a clan backend.
- Balance across tiers is broad.

### Starter feature list (P0 vertical slice)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Base grid with placement rules and a layout editor (meta) | Invalid placements rejected. Layout saved and loaded |
| 2 | 8 buildings: storage, collectors, 4 defences, walls, town hall (meta) | Stats from the tuning table. Town-hall caps enforced |
| 3 | Builders (2) + upgrade timers (meta) | Parallel upgrades limited to the builder count. Timer math unit-tested |
| 4 | Deterministic raid sim-core (gameplay) | Same inputs reproduce identical destruction % over 1,000 replays |
| 5 | Troop deployment + 4 troop types + 1 spell (gameplay) | Deploy zones enforced. Unit targeting priorities unit-tested |
| 6 | Defence AI targeting (gameplay) | Each defence's target rule is unit-tested |
| 7 | Star scoring + loot calculation (economy) | Loot = storage % per rule. Protected portion never lost |
| 8 | Async opponent finder against bot-generated bases (meta) | Returns a base within ±1 town-hall level and ±10% trophies |
| 9 | Replay viewer for the defender (ui) | Replays from the input log match the server result |
| 10 | Shield after defence (meta) | Shield length scales with destruction %. Cannot be attacked while shielded |
| 11 | Trophy gain/loss (meta) | Elo-style delta by trophy difference (see `skills/genre-playbooks/references/competitive-pvp.md` §0) |
| 12 | Bot raid balance report (tech) | Greedy and heuristic bots produce three-star rates per layout within contract bands |

## 3. Tower defense

### Definition and player fantasy
The player places and upgrades towers along enemy paths, or builds the maze themselves, to stop escalating waves, using a per-run currency. Variants:
- Classic lane TD (*Kingdom Rush*)
- Mazing TD
- Hero TD
- Merge/dice PvP TD (*Random Dice*, *Rush Royale*)
- Gacha TD with collectible operators (*Arknights*)

The fantasy is being *a master strategist watching a defensive machine shred a horde*, with the classic "just one more wave" pull.

### Core loop
```
preview wave → place / upgrade / sell towers (run gold) → wave plays out (auto)
  → kill gold → adjust build → boss wave → stars → permanent upgrades → next level
```

### Meta loops
- **Level map with stars.** Gates unlock, and harder modes reuse maps (iron or heroic challenges).
- **Permanent upgrade trees** per tower family, plus hero levelling.
- **Collection.** New towers or operators. In F2P, gacha or card packs.
- **Endless and daily challenge modes** with leaderboards.
- **PvP ladder** for merge-TD variants (simultaneous solo boards racing the same waves, with interaction through sent enemies or effects).

### Session profile
Estimate: 3–10 minute levels and longer endless runs. Premium titles see 20–40 minute sessions. PvP merge-TD matches run about 2–5 minutes. Orientation follows the variant: landscape for lane maps, portrait for vertical merge boards.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Tower archetypes: single-target, splash, slow, support, anti-air | combat; build-craft | Every wave composition should demand at least two archetypes |
| Armour types / damage types | combat | Physical vs magic forces a mixed build. Keep it to 2–3 types |
| Targeting priority (first, strong, last, close) | UX automation; combat | A cheap depth lever. Default to "first" |
| Early-call bonus | economy & resources | Risk-for-gold. Rewards confident players |
| Sell refund (partial) | economy & resources | Makes experimenting cheap. Common refunds sit around 60–80% (heuristic) |
| Hero unit with active skill | combat | Gives the player something to do during a wave |
| Merge/dice upgrading (PvP TD) | progression & upgrade; collection & randomness | RNG in the run plus permanent card levels. Watch pay-to-win |

**Wave math.** For a tower with range r over a straight path through its centre, time in range = 2r / v (path length inside the circle ÷ enemy speed). Per-enemy damage = DPS × time in range, as long as the tower isn't saturated. Throughput limit: no leaks requires total effective DPS ≥ HP per enemy × arrival rate. Worked example: r = 3 tiles, v = 1.5 tiles/s gives 4 s in range. A 25 DPS tower deals 100 damage to each enemy alone. A wave of 80 HP enemies arriving 2 per second needs 160 effective DPS across the defence, so one tower leaks however long it can shoot. Grow wave HP budgets geometrically (`HP(w) = HP0 · r^w`) and income linearly-plus-bonus. Then tune with a placement bot so the 3-star threshold needs near-optimal play and a 1-star clear allows mistakes (`difficulty_curve.py`, `level-spec.schema.json` field `solver.bot_win_rate`).

### Monetization model and typical mix
- **Premium**: one-time price plus optional heroes or IAP, as with *Kingdom Rush* and *Bloons TD 6*.
- **F2P hybrid**: premium currency for heroes and towers, rewarded ads (revive, double rewards, extra wave gold), energy, and a pass.
- **PvP merge-TD**: card upgrades, chests and packs (loot-box rules apply), pass, cosmetics.

Prefer premium or cosmetic models for single-player TD. Paid power in PvP TD drives the genre's typical review complaints.

### KPI expectations
Qualitative, because no sourced genre ranges were found. Premium TD lives on ratings, word of mouth and long tails. F2P TD shows decent D1 thanks to instantly readable gameplay. Long-term retention depends on challenge modes and PvP.

### Retention drivers
Stars and completion. New towers and heroes. Daily and endless challenges. Leaderboards. PvP ladder seasons. Mastery of hard modes.

### Content pipeline and production scope (estimates)
Content is handmade maps (path design is the craft), enemy types (each needs a counter), tower families with 3–4 upgrade tiers, art and animation. Rough estimate: 3–15 people over 9–24 months. Ironhide and Ninja Kiwi show mid-size studios sustaining TD franchises for years.

### Reference titles
- *Fieldrunners* (Subatomic Studios, 2008): early iPhone TD.
- *Plants vs. Zombies* (PopCap, 2009): lane TD for the mass market.
- *Kingdom Rush* (Ironhide, 2011): the hero and barracks template.
- *Bloons TD 6* (Ninja Kiwi, 2018): premium with deep upgrade paths and co-op.
- *Random Dice* (111%, 2019) and *Rush Royale* (IT Territory/MY.GAMES, 2020): PvP merge TD.
- *Arknights* (Hypergryph, 2019 CN): gacha operator TD.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Waves have readable composition and counter-play | Optimal builds are trivially solved, or one tower dominates |
| Maps offer distinct path puzzles | Maps are reskins with no new constraint |
| Juicy feedback: hits, deaths, upgrades | Visual clutter hides enemies and projectiles |
| Premium price matches content depth | Energy walls in a single-player TD |
| PvP rewards skill | PvP is decided by card levels |

### Innovation vectors
- Roguelite TD with draft choices between waves.
- TD plus deckbuilding.
- Co-op TD.
- TD plus base-building metas.
- Vertical portrait formats for hybrid-casual.
- Asymmetric PvP (one builds, one sends waves).
- Procedural maps validated by solvers.

### Agent-buildability: 5/5 (single-player PvE; PvP merge-TD 4/5)
**Why highest:**
- Waves and towers are deterministic.
- Placement bots and search can prove every level beatable and calibrate star thresholds.
- 2D art with frame animation is within the asset pipeline.
- Readability can be checked structurally (projectile counts, overlap).

**Residual human checkpoints:**
- Map "puzzle" quality.
- Feel of hits.

PvP merge-TD adds matchmaking and real-time sync, which is simpler than full RTS because the boards are independent.

### Starter feature list (P0 vertical slice)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Path + build-slot map loader from level spec (content) | Loads `level-spec.schema.json` layouts. Path is continuous (unit test) |
| 2 | Deterministic wave spawner (gameplay) | Wave tables from config. Same seed gives identical spawns |
| 3 | 4 tower archetypes with 3 upgrade tiers (gameplay) | Stats from the tuning table. DPS unit-tested against the formula |
| 4 | 2 damage/armour types (gameplay) | Matrix-driven multipliers. Unit tests per pair |
| 5 | Targeting priorities (gameplay) | First/strong/last/close each select correctly in unit scenarios |
| 6 | Run economy: kill gold, early call, sell refund (economy) | Gold ledger reconciles each wave |
| 7 | Hero unit with tap-to-move and an active skill (gameplay) | Pathing on the walkable layer. Skill cooldown from config |
| 8 | 10 levels + boss (content) | Placement bot clears all. 3-star threshold needs at least 90% optimal score |
| 9 | Star rating + level map unlocks (meta) | Stars persist. Gates unlock per rule |
| 10 | Permanent upgrade tree (meta) | Upgrades apply to the run stats they name. Respec works |
| 11 | Speed controls 1×/2× + pause with full HUD (ux) | Sim output is identical at 1× and 2× |
| 12 | Readability pass: enemy HP bars, range preview, placement ghost (ui) | Structural check finds no overlapping critical UI. Visual gate passes |

## 4. Real-time card battler / RTS-lite

### Definition and player fantasy
Real-time 1v1 lane battles. The player deploys units and spells from an 8-card deck by spending a regenerating resource, aiming to destroy the opponent's towers within about 3 minutes. The fantasy is being *a tactical duellist*: outplaying the opponent with timing, placement and counters, and winning the resource trade.

### Core loop
```
matchmake → 3-min battle (deploy, defend, counter-push, tower damage, overtime)
  → trophies + rewards → upgrade cards / unlock new → refine deck → matchmake
```

### Meta loops
- **Card collection and levels.** A progression lever and the main pay-to-progress risk.
- **Trophy road** with arenas that unlock new cards.
- **Clans**: card requests and donations, clan wars.
- **Ranked seasons** at the top, with level normalization for fairness.
- **Rotating events** with special rules (draft, double elixir, mirror decks).
- **Pass and cosmetics**: tower skins, emotes.

### Session profile
Estimate: 3–4 minute matches, 3–10 matches per session, several sessions a day. Portrait, one-handed, drag-to-deploy.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Regenerating resource (elixir) with cap | economy & resources; time & energy | *Clash Royale*: about 1 elixir per 2.8 s, double speed in the final minute, cap 10 (widely documented; verify) |
| 8-card deck, 4-card hand, cycle | build-craft; collection & randomness | Deck cycling is a skill dimension. Show the next card |
| Lanes, bridges, towers | combat | Two lanes create split-push decisions |
| Counter units and resource trades | combat | Win trades by neutralizing a push with fewer resources |
| Deploy anywhere on your side (own half) | combat | Placement as micro-skill |
| Sudden-death overtime | combat | Prevents draws. Raises tension |
| Card levels vs level-normalized modes | progression & upgrade | Offer a normalized ranked mode to protect competitive integrity |

**Trade math.** The value of a defence = opponent's resources spent − your resources spent to neutralize. A deck's average cost sets its tempo: low-cost "cycle" decks get back to their win condition faster, and heavy "beatdown" decks build one big push. Balance from data: card win rate, use rate and win rate when mirrored. Run bot-vs-bot self-play on the deterministic core to flag outliers before players find them. Research on multi-agent LLM self-play plus Bayesian optimization (RuleSmith) suggests a path to automated rule tuning (volatile facts).

### Monetization model and typical mix
Card progression (gold plus duplicate cards), pass, cosmetics (tower skins, emotes), event entries and offers. Randomized chests or drops are subject to loot-box law, and the trend is toward direct-purchase or transparent drops. Paid card levels in ranked are the genre's central fairness tension. Normalize levels in ranked or tournament modes.

### KPI expectations
Qualitative, because no sourced genre ranges were found. Top titles have shown multi-year longevity. Ladder engagement (matches per day) and clan participation are the health metrics to watch, along with card-level spread at each trophy band.

### Retention drivers
Ladder and seasons. New card releases. Balance-patch metas. Clan obligations. Events. The pull to master a deck.

### Content pipeline and production scope (estimates)
Steady new cards, each with design, art, animation, VFX and balance work. Monthly balance patches. Netcode, matchmaking, anti-cheat, replays and spectating. Rough estimate: 15–50 people over 2–3 years. Live balance needs dedicated designers and analysts.

### Reference titles
- *Clash Royale* (Supercell, 2016): the template.
- *Warcraft Rumble* (Blizzard, 2023): a PvE-heavy variant.
- *Minion Masters* (BetaDwarf): PC cousin.
- *Stormbound*: a turn-based lane cousin.
- *Rush Royale*: PvP TD hybrid (§3).

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Each card has a clear role and counters | Strategy collapses to a single dominant deck |
| Matches are short and tense with comeback potential | Snowballing makes the outcome obvious by minute 1 |
| Ranked integrity (normalization, fair matchmaking) | Pay-to-progress card gaps decide matches |
| Responsive netcode on mobile networks | Desyncs and lag on 4G |
| A steady patch rhythm | Stale metas between rare patches |

### Innovation vectors
- PvE campaigns using PvP units.
- 2v2 and co-op.
- Roguelite draft modes.
- Level normalization by default.
- Cross-IP card universes.
- Shorter 90-second formats.
- Bot-driven balance pipelines.

### Agent-buildability: 3/5
**Why mid:**
- The deterministic core and semantic action API let bots self-play millions of matches for balance.
- Card data is fully tabular.
- 2D or low-poly units are within the pipeline.

**Why not higher:**
- Real-time PvP needs deterministic lockstep or a server-authoritative sim, latency hiding, reconnection and anti-cheat.
- Vision agents can't play real-time from pixels.
- Live balance and animation volume.

### Starter feature list (P0 vertical slice)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Deterministic fixed-tick battle sim (tech) | State hash identical on two clients over 1,000 replayed matches |
| 2 | Resource regen with cap + double-speed phase (gameplay) | Regen timings from config, verified by unit test to ±1 tick |
| 3 | 12 cards: 8 units, 3 spells, 1 building (gameplay) | All data-driven. Targeting and aggro rules unit-tested |
| 4 | Deck builder (8) + hand of 4 with next-card preview (ui) | Valid deck enforcement. Cycle order correct |
| 5 | Drag-to-deploy with placement validation (gameplay) | Invalid zones rejected with feedback. One-handed reach verified in portrait |
| 6 | Towers, king activation, win/draw/overtime rules (gameplay) | All end states reachable in scripted playthroughs |
| 7 | Bot opponent with 3 difficulty tiers (gameplay) | Win rate of tier-2 bot vs tier-1 within the contract band over 500 matches |
| 8 | Lockstep netcode over relay with input delay + reconnect (tech) | Two-client test at 150 ms RTT and 2% loss stays in sync. Reconnect under 10 s |
| 9 | Trophy matchmaking + ladder (meta) | Elo/trophy delta per formula. Matches within the configured band |
| 10 | Card upgrades + level-normalized ranked toggle (meta) | Normalized mode ignores levels (unit test) |
| 11 | Replay recording from the input log (tech) | Replays reproduce the outcome exactly |
| 12 | Balance telemetry: card use/win rates (analytics) | Events populate a per-card win-rate report from bot runs |

## 5. Auto-battler

### Definition and player fantasy
Each round the player buys units from a shop, positions them on a board and watches combat resolve automatically, building toward trait synergies. There are two formats: real-time 8-player elimination lobbies (*Teamfight Tactics*) and async play against ghost teams (*Super Auto Pets*). The fantasy is being *the clever drafter and economist* who makes a composition come online at exactly the right moment.

### Core loop
```
shop phase (buy / sell / reroll / level) → position units → auto-combat
  → win or lose HP → income (base + interest + streak) → next round … until first place or eliminated
```

### Meta loops
- Ranked ladder and seasons.
- Rotating sets: new units, traits and mechanics every few months, which keeps discovery alive.
- Cosmetics: avatars, arenas, effects.
- Battle pass.
- Friends lobbies and casual modes.

### Session profile
Estimate. Real-time 8-player lobbies run about 25–40 minutes per game, which is long for mobile and needs robust reconnection. Async ghost formats run 10–20 minutes, can be paused, and fit mobile better. Portrait works for async. Landscape is common for 8-player boards.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Shared unit pool with finite copies | collection & randomness; social & competition | Contesting the same units creates hidden-information reads |
| Shop odds by player level | collection & randomness; progression & upgrade | Levelling trades gold now for better odds later |
| Interest on banked gold | economy & resources | *TFT*: +1 per 10 gold held, max +5. Creates the "econ vs roll" decision |
| Win/loss streak bonuses | economy & resources | Makes deliberate loss-streaking a valid strategy. Watch degeneracy |
| 3 copies merge into a star-up | progression & upgrade | Clear, satisfying power spikes |
| Trait thresholds (2/4/6) | build-craft | The heart of the genre. Show partial progress clearly |
| Items or augments | build-craft; collection & randomness | Per-game variety. Balance with sims |
| Async ghost opponents | social & competition | Removes netcode. Match by round and rank |

**Shop probability.** P(a slot shows unit u) ≈ odds(tier, level) × copies_left(u) / copies_left(tier). P(at least one u in a 5-slot shop) ≈ 1 − (1 − P)^5. Show players enough information to make this computable (pool counts, odds table). Fairness comes from transparency.

### Monetization model and typical mix
Cosmetics and passes are the healthiest pattern (*TFT* sells avatars, arenas and effects with no power). Expansion packs work for premium-leaning async titles. Paid gameplay advantages, such as extra hero choices, have drawn pay-to-win criticism in some titles. Ads fit casual async variants (rewarded rerolls in PvE only).

### KPI expectations
Qualitative, because no sourced ranges were found. Set launches drive reactivation spikes. Ranked participation and games per day are the health metrics. Long real-time sessions depress mobile session counts compared with async formats.

### Retention drivers
Set rotation novelty. Ranked climb. Experimenting with compositions. Friends lobbies. Patch metas. Short async games that fit a commute.

### Content pipeline and production scope (estimates)
Each set brings dozens of units with abilities, art and animation, plus traits and items. Balance patches follow every couple of weeks (observed for *TFT*). Rough estimates:
- Large live title: 20–60+ people.
- Indie async auto-battler: 2–6 people over 9–18 months. *Super Auto Pets* came from a very small team.

### Reference titles
- *Dota Auto Chess* (Drodo Studio, 2019 mod): the origin.
- *Auto Chess* (Drodo/Dragonest, 2019).
- *Teamfight Tactics* (Riot, 2019; mobile 2020).
- *Hearthstone Battlegrounds* (Blizzard, 2019).
- *Super Auto Pets* (Team Wood Games, 2021): async ghosts, cute and readable.
- Moonton's *Magic Chess*: the Mobile Legends universe.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Synergies are readable at a glance | Trait text walls. Players can't see why they lost |
| Every round has a meaningful econ/roll/level decision | One forced composition dominates (balance) |
| Combat is short and legible, with key moments highlighted | Combat is visual soup with no cause and effect |
| Async options for mobile | 40-minute lobbies with no reconnection |
| Sets rotate regularly | Stale unit pool for many months |

### Innovation vectors
- Async ghost formats as the mobile default.
- Roguelite PvE auto-battlers (single-player runs).
- Duo and co-op modes.
- Hybrids with deckbuilders.
- Shorter "turbo" modes.
- LLM self-play for balance exploration across huge combination spaces.

### Agent-buildability: 4/5
**Why high:**
- Combat is automatic and deterministic, the ideal case for headless sims.
- Bots can play the shop phase, and self-play estimates every trait's win rate.
- Async ghosts avoid real-time netcode.
- 2D unit art suits a style-locked pipeline.

**Why not 5:**
- The combinatorial balance space needs large sim budgets plus human taste.
- Real-time 8-player lobbies need a backend.

### Starter feature list (P0 vertical slice: async ghosts)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Deterministic auto-combat sim (gameplay) | Same boards and seed give identical results over 10k replays |
| 2 | 20 units across 3 cost tiers with abilities (content) | Data-driven. Each ability unit-tested |
| 3 | 6 traits with 2/4 thresholds (gameplay) | Trait bonuses apply exactly at thresholds. UI shows partial progress |
| 4 | Shop: buy/sell/reroll/freeze + level-based odds (gameplay) | Empirical shop odds match the table within ±1 pp over 100k rolls |
| 5 | Finite shared pool (gameplay) | Copies taken reduce odds. Pool counts visible |
| 6 | Economy: base, interest, streaks (economy) | Ledger matches the formula each round |
| 7 | 3-copy merge to star-up (gameplay) | Auto-merge on the board and bench. Stats per tier |
| 8 | Board positioning with drag + bench (ui) | Drag works one-handed. Invalid drops snap back |
| 9 | Async ghost matchmaking by round and rank (meta) | Opponent snapshot from the same round. Bot snapshots seed an empty ladder |
| 10 | HP/lives and victory condition (gameplay) | Scripted playthrough reaches both win and loss end states |
| 11 | Combat readability: ability callouts, damage meter after combat (ui) | Post-combat meter sums equal the sim damage log |
| 12 | Self-play balance report (tech) | Bot league of 1,000 runs. No trait above the contract's dominance threshold |

## 6. Turn-based tactics

### Definition and player fantasy
Turn-based squad combat on a grid, built on positioning, cover, line of sight, terrain and high stakes (optional permadeath), set inside a campaign with roster and base management. The fantasy is being *a commander who makes the smart move with limited means*. Perfect play feels like solving a puzzle.

### Core loop
```
mission briefing → deploy squad → player turn (move + act, cover, flank, abilities)
  → enemy turn (telegraphed or hidden intent) → objectives met → XP, loot, casualties
  → promote, equip, research → next mission
```

### Meta loops
- Campaign map with mission choice and consequences.
- Class promotions and skill trees.
- Base research and engineering.
- Roster management with injuries or permadeath.
- In F2P, unit gacha plus stamina (*Fire Emblem Heroes*) and rotating challenge maps.

### Session profile
Estimate: 5–20 minute missions. Mid-mission suspend and resume is mandatory. Premium players run 30–60 minute sessions. Portrait works for compact grids (8×8). Larger maps want landscape plus pinch-zoom.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Grid movement with action points (move + act) | combat | Show the reachable tiles and the danger overlay |
| Cover, flanking, elevation | combat | XCOM-family games use roughly 20/40 defence for half/full cover (illustrative) |
| Displayed hit % | combat; collection & randomness | Players perceive 90% misses as betrayal. Consider deterministic damage or "streak protection" |
| Telegraphed enemy intent | combat | *Into the Breach* shows every enemy action, so each turn is a solvable puzzle |
| Overwatch / reaction fire | combat | Area denial. Creates tempo decisions |
| Push/pull, environmental hazards | combat | Cheap depth without stat bloat |
| Permadeath + roster | progression & upgrade | Raises stakes. Offer it as a mode for broader audiences |
| Fog of war | exploration & traversal | Tension. Expensive to render readably on small screens |

**Hit-chance design.** `hit% = clamp(aim − cover_defense ± elevation ± flank, 1, 99)`. Expected damage = hit% × damage. Players feel extremes as unfair, so some games bias rolls on lower difficulties (Firaxis' XCOM games are documented by players to add hidden aim assistance there). A deterministic alternative is damage ranges with guaranteed hits. Enemy AI: utility scoring or shallow minimax/MCTS over a semantic action API. Validate puzzle missions with search (`puzzle_solver.py` patterns, or a custom solver in the sim-core).

### Monetization model and typical mix
- **Premium**: one-time price, as with the *XCOM 2 Collection* and *Into the Breach*.
- **Subscription platforms**: *Into the Breach* mobile shipped via Netflix Games in 2022.
- **F2P gacha**: *Fire Emblem Heroes*, with heroes, stamina and a pass. Apply `skills/genre-playbooks/references/rpg-gacha.md` §0.

Mid-mission ads would wreck tension. Don't use them.

### KPI expectations
Qualitative, because no sourced ranges were found. Premium: ratings, completion rate and word of mouth. F2P: as for squad RPGs. Mission abandonment rate per map is the key design metric.

### Retention drivers
Campaign stakes and roster attachment. The mastery and puzzle satisfaction loop. New maps and challenge rotations. Unlockable squads and classes. Runs in roguelite variants.

### Content pipeline and production scope (estimates)
Missions and maps (handcrafted or procedural with validation), enemy archetypes, classes, ability animations, a camera system and narrative. Rough estimate: indie 3–12 people over 1.5–3 years. *Into the Breach* came from Subset Games, a very small core team. 3D tactics with cinematic cameras costs far more.

### Reference titles
- *Final Fantasy Tactics: The War of the Lions* (mobile, 2011).
- *Fire Emblem Heroes* (Intelligent Systems/Nintendo, 2017): F2P gacha tactics.
- *Into the Breach* (Subset Games, 2018; mobile 2022): deterministic, telegraphed puzzles.
- *XCOM 2 Collection* (Feral Interactive port, 2022 iOS): premium 3D tactics.
- *Hoplite*: a one-unit tactical roguelike built for phones.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Every turn offers readable, meaningful options | Opaque RNG makes good plans fail randomly |
| Enemy intent is legible (telegraphs, danger overlays) | Tiny tiles and mis-taps on phones (no confirm step) |
| Missions vary objectives (escort, defend, extract) | "Kill all enemies" on every map |
| Undo or confirm for moves on touch | Long enemy turns with no speed-up |
| Fair difficulty modes | Permadeath without a mode choice for new players |

### Innovation vectors
- Deterministic puzzle-tactics (no to-hit RNG).
- Roguelite tactics runs.
- Tactics plus deckbuilding.
- Portrait one-thumb tactics.
- Async PvP tactics (play-by-turn).
- Solver-validated procedural missions.
- Short "daily puzzle" modes.

### Agent-buildability: 4/5
**Why high:**
- Grid, turns and determinism suit agents perfectly.
- Enemy AI via search.
- Solvers can prove missions solvable and estimate difficulty.
- `pcg.py` generates candidate maps.
- The UI is testable structurally.

**Why not 5:**
- Ability animations, camera work and telegraph readability on small screens need visual iteration and human taste.
- Narrative wrapper.

### Starter feature list (P0 vertical slice)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Grid sim-core with turns and action points (gameplay) | Deterministic. Same inputs give identical outcomes over 1,000 replays |
| 2 | Movement range + pathfinding + danger overlay (ui) | Reachable tiles match BFS. Overlay shows every telegraphed hit |
| 3 | Cover, flank, elevation hit model (gameplay) | Formula unit-tested. Displayed % equals the computed %. Clamped 1–99 |
| 4 | 4 classes × 3 abilities (gameplay) | Data-driven. Each ability has unit tests for targeting and effect |
| 5 | Telegraphed enemy intent + 3 enemy types (gameplay) | Intent shown before the player turn matches the executed action |
| 6 | Enemy AI via utility scoring (gameplay) | Beats a random policy at least 90% of the time and loses to the scripted optimal solution |
| 7 | Move confirm + undo last move (ux) | Undo restores the exact prior state. No action fires without a confirm tap |
| 8 | 6 missions with varied objectives (content) | Solver proves each solvable. `difficulty_target.win_rate` within band for the heuristic bot |
| 9 | XP, promotion, one gear slot (meta) | Curve from `progression_calc.py`. Promotion unlocks the listed ability |
| 10 | Suspend/resume mid-mission (tech) | State survives an OS kill. Resumes on the same turn |
| 11 | Enemy-turn speed-up and skip animations (ux) | Toggle keeps the sim result identical |
| 12 | Permadeath optional mode (meta) | The mode choice persists. A casualty is removed only in permadeath mode |

## Volatile facts (as of Oct 2026 — verify before relying)

- Last War, Honor of Kings and Whiteout Survival led mobile grossing in Q1 2026. H1 2026 mobile game IAP was about $40bn (−2% YoY) and downloads about 24B (−12%) — [Mobilegamer.biz (Sensor Tower)](https://mobilegamer.biz/data-digest-sensor-towers-h1-analysis-hay-days-comeback-julys-top-games-big-krafton-numbers-and-more/)
- Strategy (4X) was described as 2025's hot genre, with winners combining accessible hooks, heavy social loops and deep monetization. This is a secondary summary of Sensor Tower's State of Mobile 2026 — [LinkedIn summary](https://fi.linkedin.com/in/teemu-tuulari-aa094028)
- Mid-core took about 4% of game ad revenue (Feb–Apr 2026), and IAP is 77–90% of game revenue in the US, CA, KR and JP — [Sensor Tower](https://sensortower.com/blog/gaming-deep-dive-ad-monetization-report)
- Retention anchors (all genres): median D1 about 22%, D7 under 4%, D30 0.7–0.8%. Top 1% D1 64–68%. Mid-core D30 of about 10–12% is cited but inconsistent across sources — [Segwise (GameAnalytics)](https://segwise.ai/blog/mobile-gaming-app-user-retention-strategies)
- Unity deprecated Multiplay Game Server Hosting on Apr 1, 2026. Matchmaker, Relay and Lobby continue with third-party hosts — [Unity status](https://status.unity.com/info_notices/362941). Photon Fusion is about free to 100 CCU and about $125/mo at 500 CCU (third-party figures) — [Crux](https://crux.supercraft.host/blog/photon-fusion-pricing-2026/)
- RuleSmith combines multi-agent LLM self-play with Bayesian optimization to converge on balanced rules — [arXiv 2602.06232](https://arxiv.org/abs/2602.06232). Vision-language models playing real-time games from raw frames made under 1% progress — [arXiv 2505.18134](https://arxiv.org/html/2505.18134v3)
- Loot-box regimes (Belgium, Brazil under-18 ban from March 2026, Australia M/R18+) apply to chests, card packs and hero gacha in every playbook here. Details and sources are in `skills/genre-playbooks/references/rpg-gacha.md` volatile facts.

## Related skills
- `mechanics-codex`: cards for every mechanic named above.
- `economy-design`: timer economies, speedup pricing, sinks.
- `multiplayer-backend`: lockstep, async replays, persistent servers, matchmaking.
- `game-architecture`: sim-core plus presentation, determinism.
- `level-design`: TD paths, tactics maps, raid layouts.
- `procedural-generation`: solver-validated maps.
- `qa-testing`: bots, replay tests, balance sims.
- `liveops`: SLG event calendars, set rotations, seasons.
- `monetization`: speedups, passes, ethical bundles.
- `market-intel`: SLG UA economics and competitor scans.
