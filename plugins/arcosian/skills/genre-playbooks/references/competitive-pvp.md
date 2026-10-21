# Competitive PvP Playbooks

In competitive PvP genres, players face other players and the outcome must feel earned. Competitive integrity, matchmaking population and netcode matter more here than content volume or offer design. This file has seven playbooks in the shared 14-part template: MOBA, battle royale, hero shooter, brawler, CCG/card games, competitive sports and racing. Section 0 covers the infrastructure every playbook relies on: rating systems (Elo, Glicko-2, TrueSkill-family), matchmaking under thin populations, netcode models, anti-cheat, ranked-season design, and keeping monetization from buying wins. The headline for an agent pipeline: turn-based card games score 4/5, because their rules engines are deterministic and self-play can balance them. Every real-time shooter, MOBA and battle royale scores 1/5. They need authoritative real-time servers, 3D character animation, and fun that can't be verified from pixels. Start real-time PvP ideas as bot-filled, deterministic slices.

## Contents

| § | Playbook | Match length (estimate) | Primary monetization | Agent-buildability | First project for an agent pipeline? |
|---|---|---|---|---|---|
| 0 | [Shared foundations](#0-shared-foundations-ratings-matchmaking-netcode-integrity) | — | — | — | Read first |
| 1 | [MOBA](#1-moba) | 10–20 min | Skins, heroes, pass | 1/5 | No |
| 2 | [Battle royale](#2-battle-royale) | 10–30 min | Pass, cosmetics, crates | 1/5 | No |
| 3 | [Hero shooter](#3-hero-shooter) | 3–10 min | Heroes, skins, pass (often upgrades) | 1/5 | No |
| 4 | [Brawler](#4-brawler) | 2–3 min | Pass, skins, unlock acceleration | 2/5 | Only as a bot-filled slice |
| 5 | [CCG / card games](#5-ccg--card-games) | 3–10 min | Packs or variants, pass | 4/5 | Yes |
| 6 | [Competitive sports](#6-competitive-sports) | 2–10 min | Ultimate-team packs, pass | 2/5 (arcade 1v1: 3/5) | Arcade 1v1 only |
| 7 | [Racing](#7-racing) | 1–3 min races | Car packs, upgrades, pass | 3/5 (ghost racing) | Yes, with ghosts |
| — | [Volatile facts](#volatile-facts-as-of-oct-2026--verify-before-relying) | — | — | — | Check before quoting numbers |

## How to use these playbooks

- Set `meta.genre: "pvp"` (or the closest genre), `meta.subgenre` to the playbook slug, and `technical.multiplayer` to `async` or `realtime`. Set `technical.backend` deliberately: real-time PvP rules out `none`.
- Copy the core loop into `contract.json → loops[]`, and turn the starter list into P0 `features.json` entries. The "two-client sync" and "bot match" criteria provide `playthrough` gate evidence.
- Mechanic category labels used here (combat, build-craft, collection & randomness, progression & upgrade, economy & resources, social & competition, UX automation, live events) map to the `mechanics-codex` taxonomy via `gs.py kb "<mechanic>" --skill mechanics-codex`.
- KPIs are qualitative unless sourced. Real-time PvP lives or dies on **concurrent population per matchmaking bracket**, so model it before anything else (§0.2).

## 0. Shared foundations: ratings, matchmaking, netcode, integrity

### 0.1 Rating systems
```
Elo expected score   E_A = 1 / (1 + 10^((R_B − R_A) / 400))
Elo update           R_A' = R_A + K · (S_A − E_A)        S = 1 win, 0.5 draw, 0 loss
Worked example       R_A 1500 vs R_B 1700 → E_A ≈ 0.24; win with K = 32 → +24.3; loss → −7.7
```
- **K-factor.** Use a high K while a rating is new (fast placement) and a lower K once it settles. FIDE chess uses 40 → 20 → 10 as players mature.
- **Glicko-2** (Mark Glickman) adds rating deviation and volatility. Uncertainty shrinks with play and grows with inactivity. Good for 1v1 games (CCG, sports, racing duels).
- **TrueSkill** (Microsoft Research) and the open **Weng–Lin / OpenSkill** family handle teams and free-for-all placements. Each player has a mean μ and an uncertainty σ. Match on μ, display a conservative μ − kσ. Use these for MOBA, BR and team shooters.
- **Hidden MMR vs visible rank.** Matchmake on hidden MMR and show a rank ladder (tiers, stars, points) with loss protection and seasonal soft resets. Visible ranks motivate players. MMR keeps matches fair.
- **Smurf and boosting control.** Fast-track MMR for anomalous win rates. Device and account linkage. Duo-queue MMR spread limits.

### 0.2 Matchmaking under real populations
- **Quality vs queue time.** Start with a tight MMR window and widen it with wait time (for example ±50 → ±300 over 30 s). Log match quality (predicted win-probability spread) next to wait time.
- **Population math.** Expected wait ≈ players needed per match ÷ arrival rate into the bracket. A 10-player MOBA in a bracket that receives 2 players/s waits about 5 s. At 0.1 players/s it waits about 100 s, and that region is dead. Multiply brackets (region × mode × rank × party size) carefully. Each split divides the arrival rate.
- **Bots.** Filling early matches and thin brackets with bots is widespread in mobile PvP. Use bots for onboarding and low-population hours, label AI teammates where they replace humans, and never put undisclosed bots in matches with prizes or real stakes. Policy decisions belong to `legal-ethics`.
- **Parties.** Aggregate party MMR toward the strongest member and match parties against parties where possible.

### 0.3 Netcode models
| Model | How it works | Fits | Mobile cautions |
|---|---|---|---|
| Deterministic lockstep (frame sync) | Clients exchange inputs. Every client runs the same deterministic sim | RTS-lite, MOBA (widely reported in Chinese MOBAs), fighting-lite | Needs bit-exact determinism across ARM devices (fixed-point). One slow client stalls everyone unless the server relays and drops late input |
| Server-authoritative + client prediction + reconciliation + lag compensation | Server owns the truth. Clients predict their own movement and the server rewinds for hit checks | Shooters, BR, brawlers, sports | Server cost per match. Tick-rate vs bandwidth trade-offs on cellular |
| Rollback | Predict remote input, then roll back and resimulate on mismatch | 1v1 fighting and duel games | CPU spikes during resimulation on low-end phones |
| Async (turn or ghost) | No live connection. Moves or recorded runs are exchanged | CCG (async), racing ghosts, golf/pool, raids | Players must tolerate latency between turns. Validate on the server |

Mobile networks force design choices: reconnection within seconds (with AI takeover), input buffering, small packets, and graceful handling of app backgrounding. Load `multiplayer-backend`.

### 0.4 Integrity: anti-cheat and fair monetization
- **Server authority** over damage, economy and results. Clients send *intents*, not outcomes.
- **Device and app attestation**: Play Integrity on Android, App Attest/DeviceCheck on iOS. Detect emulators where they give unfair input advantages, and match them separately rather than banning them.
- **Report → replay → review pipeline.** Store the input logs needed to replay any reported match.
- **Monetization rule.** In ranked play, money buys *expression* (skins, emotes) and *convenience* (unlock speed), never *power*. Paid power is tolerable only in casual or PvE modes and still damages reviews. Card-level gaps in PvP need normalization in ranked.
- **Voice and text chat** create the highest child-safety and moderation exposure. Default chat off for minors (the FTC's 2022 Epic order required exactly that), apply filters, and add report/mute/block. The amended COPPA rule treats voice as a potential biometric identifier (volatile facts).

### 0.5 Ranked season design
- Seasons of about 1–3 months, with a soft MMR reset (compress toward the mean) and season rewards by peak tier.
- Rank-loss protection at tier boundaries for motivation, but none at the top tiers.
- Activity decay only at the top, so elite ladders stay meaningful without punishing casual players.
- Track **season completion funnels** (placement → first promotion → target tier) as retention KPIs.

## 1. MOBA

### Definition and player fantasy
Team battles, usually 5v5 (some 3v3), on a lane map. Each player controls one hero with 3–4 abilities, farms minions, takes objectives and destroys towers to reach the enemy base. Mobile MOBAs shortened matches and simplified controls compared with PC: virtual joystick, auto-targeting assistance, recommended builds. The fantasy is *hero mastery and team triumph*: the outplay, the comeback, the clutch teamfight.

### Core loop
```
queue → draft / ban → laning (farm, trade, last-hit) → objectives (towers, epic monsters)
  → teamfights → push base → victory/defeat → rank points + rewards → queue
```

### Meta loops
- **Hero roster** unlocked by direct purchase with soft or hard currency. Usually not gacha.
- **Skins**, the dominant revenue line, with rarity tiers and limited releases.
- **Ranked seasons** (§0.5), plus mastery titles per hero.
- **Battle pass and events.** IP collaborations.
- **Pre-match loadouts** (emblems, runes, spells) as light build-craft.
- **Social**: friends, duo/five-stack, clubs, esports viewing rewards.

### Session profile
Estimate: matches of about 10–20 minutes (*Pokémon UNITE* fixes 10 minutes; most 5v5 mobile MOBAs land around 15–20), 1–4 matches per session, mostly evenings and weekends with friends. Landscape, two thumbs.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Joystick + skill buttons with drag-to-aim and cancel zone | combat; UX automation | The touch-control standard. Aim assist settings per skill |
| Lanes, minions, towers, jungle | combat; economy & resources | Gold and XP from farm create the macro game |
| Draft/ban phase | build-craft; social & competition | Strategy before the match. Skip it in casual modes |
| In-match item shop with auto-buy recommendations | build-craft; UX automation | Removes menu friction on phones |
| Epic objectives with team buffs | combat | Creates the timing hubs where teamfights happen |
| Surrender, reconnection with AI takeover | UX automation | Mobile networks and interruptions make these mandatory |
| Fog of war and vision | combat | Simplify for mobile readability |

### Monetization model and typical mix
Skins and cosmetic tiers dominate, followed by hero purchases, battle pass, event bundles and "lucky draw" skin gachas. The draws carry loot-box exposure: in June 2026 a Brazilian court ordered Riot to pay damages over loot boxes (volatile facts). The model is power-neutral by convention, and breaking it is fatal to competitive credibility.

### KPI expectations
Partly sourced. *Honor of Kings* was among the top-grossing mobile games in Q1 2026 (volatile facts). Otherwise qualitative: winners have enormous DAU sustained by network effects, and new entrants struggle to reach queue-viable populations. Track queue time by bracket, match completion rate, AFK/leaver rate and friend-party share.

### Retention drivers
Friends and five-stacks (the strongest). Ranked climb. Hero mastery. Skin collection. Esports and creators. Seasonal events. Habitual evening play.

### Content pipeline and production scope (estimates)
Heroes (kit design, 3D model, rigging, animation set, VFX, voice), premium skins at high volume, maps and modes, frequent balance patches, esports operations, anti-toxicity systems. Rough estimate: 100–300+ developers, 3+ years, regional servers.

### Reference titles
- *Vainglory* (Super Evil Megacorp, 2014): early premium-feel mobile MOBA.
- *Honor of Kings* (TiMi/Tencent, 2015) and its international variant *Arena of Valor*.
- *Mobile Legends: Bang Bang* (Moonton, 2016): South-East Asia dominance, low-end device reach.
- *League of Legends: Wild Rift* (Riot, 2020).
- *Pokémon UNITE* (TiMi/The Pokémon Company, 2021): 10-minute score-based format.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Queue times stay short at fair match quality (population) | Entry against entrenched incumbents with no distinct hook |
| Touch controls feel precise on low-end phones | Frame drops and input lag on mid-tier Android |
| Behaviour systems curb toxicity and AFKs | Toxicity and leavers drive newcomers out |
| Monetization stays cosmetic-first | Any hint of paid power |
| Regional servers and esports build culture | Small regions fragment into dead queues |

### Innovation vectors
- Shorter formats (8–10 minutes) and score-based objectives.
- 3v3 and 2v2 modes.
- IP-driven MOBAs.
- AI teammates for AFK replacement and practice.
- Cross-play PC/mobile.
- MOBA-lite hybrids folded into brawlers.

### Agent-buildability: 1/5
**Why lowest:**
- 10-player real-time netcode (lockstep or authoritative).
- A large hero roster with rigged 3D animation and VFX.
- Live balance.
- Moderation.
- Fun can't be verified by vision agents.

**Feasible scope:** a 3v3 bot match on a deterministic sim-core, which helps balance hero kits but is not a product.

### Starter feature list (P0 vertical slice: 3v3 vs bots, one lane plus jungle)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Deterministic fixed-tick sim-core (tech) | Identical state hashes across 2 clients over 500 replayed matches |
| 2 | Joystick + 3 skills + basic attack with drag-aim and cancel (gameplay) | Scripted inputs hit test dummies at the expected ranges. Cancel zone works |
| 3 | 4 heroes in 3 roles (content) | Kits data-driven. Each ability unit-tested |
| 4 | Minion waves, towers, base core (gameplay) | Waves spawn on the timer. Tower aggro rules unit-tested |
| 5 | Gold/XP economy + 6-item shop with auto-buy (economy) | Ledger reconciles. Auto-buy follows the recommended path |
| 6 | Bot AI for laning and teamfight (gameplay) | Bot team beats random at least 90%. Mirror bots give 45–55% win rate per side |
| 7 | Epic objective with team buff (gameplay) | Buff applies to the killing team only. Respawn timer from config |
| 8 | Reconnection with AI takeover (tech) | Disconnecting for 20 s hands the hero to AI. Reconnecting restores control |
| 9 | Match end, surrender vote, results screen (ux) | All end states reachable in scripted playthroughs |
| 10 | TrueSkill/OpenSkill rating for teams (meta) | Ratings update per formula. Placement uses high uncertainty |
| 11 | Low-end performance budget (perf) | Low tier holds p95 frame time ≤ 33.3 ms in a 6-hero teamfight scenario |
| 12 | Report + replay capture (tech) | Input log replays any match to an identical outcome |

## 2. Battle royale

### Definition and player fantasy
Large lobbies (50–100 players) drop onto a map, scavenge weapons and gear, and fight as a shrinking safe zone forces encounters. The last player or squad standing wins. Mobile examples range from 100-player military sims (*PUBG Mobile*) to fast 50-player, roughly 10-minute matches tuned for low-end phones (*Free Fire*). Party BRs use elimination rounds (*Stumble Guys*). The fantasy is *survival against everyone*: the clutch final circle, squad loyalty and the dramatic win.

### Core loop
```
queue (solo/duo/squad) → choose landing → loot → rotate with zone → fight / third-party / hide
  → knocked, revived or eliminated → placement → rewards, rank points → queue
```

### Meta loops
- **Battle pass**, genre-defining, with tiered cosmetic rewards.
- **Cosmetics**: outfits, weapon skins, vehicles, emotes, parachutes.
- **Crates and lucky spins**: high revenue, high regulatory exposure.
- **Ranked tiers** per season, plus arcade, TDM and limited-time modes.
- **Collab events** with IP partners.
- **Friends, clans and squads.**

### Session profile
Estimate: 10–30 minute matches (fast 50-player modes about 10–15 minutes, 100-player classic modes about 25–30), several matches per session. Landscape. Thermal load is high: Google warns frame rates often degrade after 45–50 minutes.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Shrinking zone with escalating damage | combat; exploration & traversal | The pacing engine. Tune phase timings to the target match length |
| Loot rarity tiers + inventory | collection & randomness; UX automation | Auto-pickup and auto-equip-better are essential on touch |
| Aim assist, auto-fire option, gyro aiming | combat; UX automation | Touch aiming needs help. Offer gyro for skilled players |
| Knock/revive in squads | social & competition | Creates team moments and second chances |
| Ping/quick-chat system | social & competition | Communication without voice. Safer for minors |
| Vehicles and rotation | exploration & traversal | Map scale management |
| Bots in early and low-population matches | social & competition | Common practice. See §0.2 for disclosure policy |
| Spectate after death + replays | UX automation | Keeps eliminated players watching and learning |

### Monetization model and typical mix
Battle pass plus cosmetics (direct and in rotating stores), lucky spins and crates, collab bundles, and in some titles character abilities sold separately. Random items are the main legal exposure (Belgium, Brazil under-18, Australia ratings, odds disclosure). Prefer direct-purchase stores and pass rewards.

### KPI expectations
Qualitative, because no sourced genre ranges were found. Incumbents run very large DAU in emerging markets, where low-end optimization was decisive. New entrants face extreme population thresholds: a 100-player lobby needs a deep queue. Track time to fill a lobby, the bot share by bracket, and match completion rate.

### Retention drivers
Squads of friends. Pass progression. Ranked seasons. Collab events. New maps and modes. Winning moments that players share socially.

### Content pipeline and production scope (estimates)
Large maps or modular map pieces, a weapon roster with ballistics, vehicles, a very high-volume cosmetics pipeline, massive anti-cheat operations, regional servers, esports. Rough estimate: 200+ people at incumbent scale. Cautionary tale: *Apex Legends Mobile* launched in 2022 and was shut down in 2023.

### Reference titles
- *Garena Free Fire* (111dots/Garena, 2017): 50 players, short matches, low-end reach.
- *PUBG Mobile* (LightSpeed & Quantum/Tencent with Krafton, 2018): the 100-player template.
- *Call of Duty: Mobile* (TiMi/Activision, 2019): BR plus multiplayer modes.
- *Fortnite* (Epic): building BR, with mobile availability shaped by platform disputes.
- *Farlight 84*: hero BR.
- *Stumble Guys* (Kitka Games, 2021): party elimination BR.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Runs smoothly on the target market's median phone | Download size and heat exclude the mass market |
| Lobbies fill fast (population plus bots) | Thin queues mean long waits and empty matches |
| Touch aiming feels fair (assist, gyro) | PC-style controls frustrate touch players |
| Anti-cheat keeps the top ladders credible | Cheaters dominate high ranks |
| Collabs and pass content arrive steadily | Late entry with no differentiation (the market is saturated) |

### Innovation vectors
- Smaller, faster BRs (20–40 players, under 10 minutes).
- Party BRs with mini-game rounds.
- Hero abilities.
- Extraction-shooter formats on mobile.
- UGC modes (*Eggy Party*-style AIGC level creation reported strong engagement; volatile facts).
- AI teammates.
- Cross-play.

### Agent-buildability: 1/5
**Why lowest:**
- 50–100-player authoritative servers.
- Large 3D maps and weapons.
- Animation sets, ballistics and hit registration.
- An anti-cheat operation.
- Real-time fun that can't be verified from pixels.

**Feasible scope:** a 10-player bot BR on a small map to prototype zone pacing and loot tables. Zone and loot balance can be simulated headlessly.

### Starter feature list (P0 vertical slice: 10-player bot match on a 1 km² map)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Server-authoritative movement with client prediction (tech) | 2 clients at 120 ms RTT. Reconciliation error under 0.2 m p95 |
| 2 | Drop/landing phase (gameplay) | Players choose a landing spot. All land within 60 s |
| 3 | Loot spawner with rarity tables (economy) | Empirical rarity matches the table within ±1 pp over 10k spawns |
| 4 | Inventory with auto-pickup and auto-equip-better (ux) | Rules unit-tested. No inventory overflow |
| 5 | 3 weapons with hit-scan or projectile, server hit validation (gameplay) | Lag-compensated hits verified at 0/100/200 ms in tests |
| 6 | Shrinking zone with phases and damage (gameplay) | Phase timings from config. Sim median match within ±15% of target length |
| 7 | Knock/revive (gameplay) | State machine unit-tested. Revive interrupt rules |
| 8 | Bots with loot/rotate/fight behaviour (gameplay) | A bot-only match completes without stuck bots over 50 runs |
| 9 | Aim assist + optional gyro (ux) | Assist strength from config. Gyro toggle persists |
| 10 | Ping/quick-chat (ux) | Pings visible to squad. No free-text chat for minors |
| 11 | Spectate after elimination + results with placement (ux) | End states reachable in scripted playthroughs |
| 12 | Perf on low tier (perf) | p95 frame time ≤ 33.3 ms with 10 players in view. 20-minute soak with no thermal-critical state |

## 3. Hero shooter

### Definition and player fantasy
A team-based shooter, third- or first-person, where distinct heroes have abilities and roles (tank, damage, support), played over objective modes: control, payload, team deathmatch. Mobile variants favour third-person cameras, larger hitboxes (mechs, robots) and short matches. The fantasy is *being a hero with a unique toolkit*: team synergy, skill expression and clutch ultimates.

### Core loop
```
queue → pick hero (role) → objective match (3–10 min) → eliminate, assist, capture
  → result → hero XP / rank → unlock or upgrade heroes → queue
```

### Meta loops
- Hero roster unlocks and, in many mobile shooters, **power upgrades** (levels, modules, cards). This is the genre's fairness flashpoint.
- Ranked seasons. Battle pass and skins. Clans and squads. Limited-time modes.

### Session profile
Estimate: 3–10 minute matches, 3–8 per session. Landscape, two thumbs. Gyro aiming optional.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Abilities with cooldowns + charged ultimate | combat | The hero identity layer. Ultimates create swing moments |
| Role composition | build-craft; social & competition | Role queue avoids five-DPS teams |
| Aim assist / auto-fire / lock-on | combat; UX automation | Essential on touch. Tune per weapon class |
| Objective modes (control, payload) | combat | Forces teamplay beyond kills |
| Lag compensation and hit registration | combat | Felt fairness depends on it. Server-authoritative (§0.3) |
| Respawn timers and spawn protection | combat | Short respawns suit mobile pacing |
| Mechs and vehicles with big hitboxes | combat | Touch-friendly. Slower, more tactical combat |

### Monetization model and typical mix
Hero unlocks, skins, pass, and in many mobile titles upgrade currencies or materials that raise hero or weapon power. That last one brings high revenue per payer and high review and churn risk. Keep ranked power-neutral or level-normalized (§0.4).

### KPI expectations
Qualitative, because no sourced ranges were found. Shooter audiences are large but shared with BR incumbents. Track ranked participation, role-queue wait times, hero pick-rate concentration and the reasons behind each upgrade purchase.

### Retention drivers
Hero mastery. New hero releases. Ranked. Squads. Limited modes. Cosmetic expression.

### Content pipeline and production scope (estimates)
Heroes (3D rigged models, full animation sets, weapons, VFX, voice), maps built for multiple modes, netcode, anti-cheat, balance patches. Rough estimate: 40–150 people over 2–4 years.

### Reference titles
- *War Robots* (Pixonic, 2014): mech shooter with an upgrade economy.
- *Frag Pro Shooter* (Oh BiBi, 2019): card-collected heroes, third-person.
- *Mech Arena* (Plarium, 2021).
- *Blood Strike* (NetEase).
- *Farlight 84*: hero BR.
- *Arena Breakout*: an extraction-shooter cousin.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Aiming feels good on touch (assist plus camera) | PC-style precision demands frustrate players |
| Heroes are readable at a glance (silhouette, colour) | Visual clutter in teamfights |
| Short matches with quick requeue | Long queues from too many modes or regions |
| Upgrades never decide ranked | Paid power ruins top ranks and reviews |
| Stable servers and hit registration | Rubber-banding on cellular networks |

### Innovation vectors
- Hero BR hybrids.
- Extraction formats.
- Mech and vehicle combat suited to touch.
- PvE co-op hero modes.
- Gyro and controller support.
- Cross-play.
- AI squadmates.

### Agent-buildability: 1/5
**Why lowest:**
- Real-time authoritative netcode with lag compensation.
- Rigged 3D hero animation and VFX.
- Weapon feel and aim-assist tuning need human hands on devices.
- Vision agents can't judge real-time fights.

**Feasible scope:** a 3v3 bot slice on one map to prototype hero kits. Kit damage math can be simulated.

### Starter feature list (P0 vertical slice: 3v3 vs bots, one control point)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Third-person controller + camera for touch (gameplay) | Scripted traversal of the map loop. Camera never clips into geometry in 5 test paths |
| 2 | Server-authoritative shooting with lag compensation (tech) | Hits validated at 0/100/200 ms RTT in automated tests |
| 3 | 3 heroes with ability, cooldown and ultimate (content) | Data-driven kits. Unit tests per ability |
| 4 | Aim assist + auto-fire option (ux) | Assist cone and strength from config. Toggle persists |
| 5 | Control-point mode with scoring and overtime (gameplay) | All end states reachable in scripted playthroughs |
| 6 | Bots with role behaviour (gameplay) | Mirror bot match gives 45–55% win rate per side over 200 runs |
| 7 | Respawn + spawn protection (gameplay) | Timers from config. No spawn-kill within the protection window |
| 8 | Hero select with role guidance (ui) | Role counts shown. Lock-in rules enforced |
| 9 | Hit and kill feedback (vfx) | Hit markers, kill feed and audio cues pass the `game-feel` checklist |
| 10 | Rating + ranked toggle with level normalization (meta) | Ranked ignores upgrade levels (unit test) |
| 11 | Reconnect within 15 s (tech) | Player resumes the same hero and match state |
| 12 | Perf budget on mid tier (perf) | p95 frame time ≤ 16.6 ms at 60 fps target on mid tier during a 6-player fight |

## 4. Brawler

### Definition and player fantasy
Short top-down arena matches (3v3 objectives, or free-for-all "showdown" survival). Each player controls a collectible brawler with a basic attack, a charged super and gadgets. Several modes rotate on one shared combat core. The fantasy is *quick, chaotic, skilful fun with friends*: 2–3 minutes of action, a favourite character, visible mastery.

### Core loop
```
pick brawler → 2–3 min match (rotating mode) → trophies per brawler
  → progression (unlocks, power levels, gadgets) → new mode in rotation → next match
```

### Meta loops
- **Brawler collection** through progression tracks and pass rewards. The market moved from loot boxes toward pass- and track-based unlocks. Check the current state of any reference title before copying its model.
- **Per-brawler trophies** plus account trophy road. Ranked mode with level normalization.
- **Clubs** (social), pass, skins, events with special modes.
- **Map maker / UGC maps** feeding mode rotation.

### Session profile
Estimate: 2–3 minute matches, 3–15 per session, multiple sessions a day. Twin-stick in landscape. Fast requeue is critical.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Twin-stick: move + aim, tap to auto-aim, drag for manual | combat; UX automation | Auto-aim tap sets the skill floor, manual aim the ceiling |
| Super charged by landing hits | combat | Rewards aggression, creates comebacks |
| Bushes / stealth zones | combat | Cheap readable depth on top-down maps |
| Rotating modes on one core | live events | Content volume without new combat systems |
| Per-character trophies | social & competition; progression & upgrade | Encourages playing many brawlers. Matchmaking per brawler |
| Power levels with ranked normalization | progression & upgrade | Progression for casual play, fairness in ranked |
| Short respawn, no permanent elimination (most modes) | combat | Keeps everyone playing all 2–3 minutes |

### Monetization model and typical mix
Battle pass (core), skins (large catalogue), unlock and progression acceleration, offers. Some power-level progression ("pay-to-progress") is common. Keep it out of ranked. Avoid paid random drops for minors (§0.4, loot-box law).

### KPI expectations
Qualitative, because no sourced ranges were found. Short matches support high session counts. Long-term health depends on brawler release cadence and mode rotation. Track matches per DAU, the share of brawlers played, and party share.

### Retention drivers
Collection (new brawlers). Mode rotation. Friends and clubs. Per-brawler mastery. Ranked. Pass seasons.

### Content pipeline and production scope (estimates)
Brawlers (low-poly 3D or 2D model, animation set, kit, VFX, voice barks), skins at volume, maps (designer and UGC), modes. Rough estimate: 20–60 people over 2–3 years, with server-authoritative netcode for 6–10 players.

### Reference titles
- *Brawl Stars* (Supercell, 2018 global): the template.
- *Zooba* (Wildlife Studios): animal showdown BR.
- *Smash Legends* (5minlab): platform-fighter brawler.
- *Bullet Echo* (ZeptoLab): top-down tactical with vision cones.
- *Stumble Guys*: party elimination cousin.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Characters have instantly readable silhouettes and kits | Look-alike brawlers and visual noise |
| 2–3 minute matches with constant action | Long downtime (respawn waits, long queues) |
| Modes rotate on a solid core | One mode only. Stale |
| Ranked is fair (normalized) | Power gaps decide matches |
| Fast requeue and party flow | Clunky lobby and party UX |

### Innovation vectors
- Hero-collection brawlers with roguelite PvE.
- Co-op boss modes.
- UGC map makers with AI assistance.
- Short esports formats.
- Cross-IP brawlers.
- Mobile-first party brawlers with social deduction twists.

### Agent-buildability: 2/5
**Why low-mid:**
- Top-down views and low-poly or 2D art keep the asset load manageable.
- A deterministic core lets bots play via a semantic API to balance kits.
- Matches are short, so playthrough scripts are cheap.

**Why not higher:**
- Real-time server-authoritative netcode for 6–10 players.
- Animation sets per brawler.
- Twitch-feel tuning needs devices and human taste.

### Starter feature list (P0 vertical slice: 3v3 one mode vs bots)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Twin-stick controls with tap auto-aim and drag manual aim (gameplay) | Scripted inputs hit stationary and moving dummies at the expected rates |
| 2 | 4 brawlers: attack, super, gadget (content) | Kits data-driven. Unit tests per ability |
| 3 | Super charge from hits (gameplay) | Charge per hit from config. UI meter matches sim |
| 4 | Bush stealth + reveal rules (gameplay) | Visibility rules unit-tested for every case |
| 5 | One objective mode with win and overtime (gameplay) | All end states reachable in scripted playthroughs |
| 6 | Bots with mode-aware behaviour (gameplay) | Mirror bots give 45–55% per side over 300 runs |
| 7 | Server-authoritative netcode with prediction (tech) | 6 clients at 150 ms RTT. No desync. Reconciliation error under budget |
| 8 | Per-brawler trophies + matchmaking (meta) | Trophy delta per formula. Bracket matching by brawler trophies |
| 9 | Fast requeue + party invite (ux) | Results to next match in 3 taps or fewer. Party persists |
| 10 | Juice: hit flash, knockback, screen shake budget (vfx) | Passes the `game-feel` checklist. Shake respects the accessibility setting |
| 11 | Ranked toggle with power normalization (meta) | Normalized stats applied in ranked (unit test) |
| 12 | Perf on low tier (perf) | p95 frame time ≤ 33.3 ms with 6 brawlers plus VFX on screen |

## 5. CCG / card games

### Definition and player fantasy
Collect cards, build decks, and play turn-based matches against other players, synchronously or asynchronously, using a resource system (mana, energy). Mobile has pushed toward shorter, simpler formats:
- *Marvel Snap*: 12-card decks, 6 turns, 3 locations, about 3-minute games.
- *Pokémon TCG Pocket*: 20-card decks, daily free packs.

The fantasy is *the strategist-collector*: the perfect combo, a deck that expresses identity, outplaying an opponent.

### Core loop
```
build / tune deck → match (turn-based, 3–15 min) → win/lose → rewards (currency, pass XP, packs)
  → open packs / craft / upgrade collection → build / tune deck
```

### Meta loops
- **Collection.** Packs or reward tracks. Duplicates convert to a crafting currency for targeted crafting, the main fairness valve.
- **Ranked ladder seasons** (§0.5) and limited formats (draft/arena, events).
- **Expansions** every few months, the core content beat, with rotating formats in some games.
- **Cosmetics.** Card variants and alt-arts, frames, card backs, avatars. Collector value without power.
- **Pass.** Daily and weekly quests.

### Session profile
Estimate: matches of about 3 minutes (*Marvel Snap*) to about 10 minutes (traditional CCG), 2–6 per session, plus pack-opening and deckbuilding sessions. Portrait-friendly. Async play fits commutes.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Resource curve (+1 per turn) | economy & resources; combat | Sets tempo. The curve is the first deckbuilding lesson |
| Draw RNG + mulligan | collection & randomness | Variance creates drama. Mulligans keep it from deciding games |
| Keywords and triggered effects | combat; build-craft | Depth through combinations. Every keyword needs rules-engine tests |
| Location/lane modifiers (*Snap*) | combat | Variety per match without new cards |
| Stakes doubling ("snap") and retreat | social & competition | Bluffing and loss limiting. Adds poker-like depth |
| Crafting from duplicates | economy & resources | Deterministic path to the cards players want. Pairs well with loot-box compliance |
| Turn timer (rope) + concede | UX automation | Required for synchronous PvP on mobile |
| Async play (*Pocket*-style quick modes) | social & competition | Removes the need to be online at the same time |

**Draw math (hypergeometric).** P(at least one of K copies among n cards drawn from N) = 1 − C(N−K, n)/C(N, n). Worked examples:
- 2 copies in a 30-card deck, 6 cards seen: 1 − (24·23)/(30·29) ≈ 36.6%.
- *Marvel Snap*-style 12-card deck: by turn 3 you have seen 6 cards, a 50% chance for any specific card. By turn 6 you have seen 9, a 75% chance.

Smaller decks make games more consistent and easier to read, which suits mobile.

### Monetization model and typical mix
Packs (randomized, so odds disclosure and pity apply), or progression-based collection without packs (*Snap* markets this), plus cosmetic variants, pass, bundles, and draft or event entries. Loot-box law applies to packs. Crafting and direct purchase are the compliance hedge. Card art is the product, so player-facing AI art risks disclosure stigma (see `legal-ethics`).

### KPI expectations
Qualitative, because no sourced ranges were found. Expansion launches drive reactivation and spend spikes. Healthy games keep ranked participation through each season. Track deck diversity (top-deck share), games per DAU and collection completion curves for F2P players.

### Retention drivers
Expansion cadence. Meta shifts from balance patches. Daily quests and pass. Ranked season resets. Collection completion. Creator and community content.

### Content pipeline and production scope (estimates)
Expansions of dozens to 100+ cards, each needing design, illustration, effects and balance. A rules engine with exhaustive interaction tests. AI opponents for PvE and tutorials. Rough estimate: 20–80 people over 2–3 years, with a live design and balance team.

### Reference titles
- *Hearthstone* (Blizzard, 2014): the mobile CCG template.
- *Shadowverse* (Cygames, 2016).
- *Yu-Gi-Oh! Duel Links* (Konami, 2017): shortened format.
- *Legends of Runeterra* (Riot, 2020).
- *Magic: The Gathering Arena* (Wizards; mobile 2021).
- *Marvel Snap* (Second Dinner, 2022): 3-minute games, no packs.
- *Pokémon TCG Pocket* (Creatures/DeNA, 2024): simplified rules, collection-first.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Rules are short to learn, with deep combinations | Rules text walls and stack-timing confusion on a phone |
| Fast matches with readable board states | 15-minute matches with long opponent turns |
| A fair collection path (crafting, generous F2P) | Pack-only acquisition with heavy pay walls |
| Steady expansions and balance patches | A stale meta and a single dominant deck |
| Collector cosmetics with real appeal | Weak or inconsistent card art |

### Innovation vectors
- Shorter formats and smaller decks.
- Async modes.
- Location or board modifiers.
- Roguelite deckbuilding PvE (*Slay the Spire*-style) alongside PvP.
- Social collection: trading with limits, showcases.
- LLM self-play for balance search.
- Hybrid auto-battler and card designs.

### Agent-buildability: 4/5
**Why high:**
- A deterministic turn-based rules engine.
- AI opponents via MCTS or heuristics.
- Self-play leagues to balance cards before release.
- Async PvP without real-time netcode.
- UI- and data-heavy, which agents handle well.

**Why not 5:**
- Exhaustive keyword-interaction testing (rules-engine bugs are the genre's top defect class).
- Card art volume and quality under disclosure stigma.
- Expansion design needs human taste.

### Starter feature list (P0 vertical slice)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Deterministic rules engine with event queue (tech) | 1,000 random self-play games with no illegal state. Replays identical |
| 2 | 40 cards, 6 keywords (content) | Each keyword has unit tests for all interactions with every other keyword |
| 3 | Resource curve + turn structure + turn timer (gameplay) | Timer from config. Timeout auto-ends turn |
| 4 | Draw, mulligan, deck validation (gameplay) | Empirical draw odds match the hypergeometric formula within ±1 pp |
| 5 | Board UI readable on a 5.5" screen (ui) | Structural checks: no text overflow, card zoom on long-press |
| 6 | AI opponent (MCTS or heuristic, 2 levels) (gameplay) | Level 2 beats level 1 at least 65% over 500 games |
| 7 | Async or synchronous PvP over the backend (tech) | Two-client match completes. Reconnect restores state. Server validates every move |
| 8 | Deck builder with curve view (ui) | Valid deck rules enforced. Curve chart matches deck contents |
| 9 | Collection + crafting from duplicates (economy) | Crafting rates from config. Ledger reconciles |
| 10 | Pack opening with odds disclosure + pity (monetization) | Odds one tap away. Pity per `gacha_calc.py` |
| 11 | Glicko-2 rating + ranked tiers (meta) | Rating updates per formula. Tier protection rules unit-tested |
| 12 | Self-play balance report (tech) | Card win-rate and deck diversity report from 10k bot games |

## 6. Competitive sports

### Definition and player fantasy
Sports matches against other players, in real time or async. There are three families:
- **Licensed sims with "ultimate team" card collection**: football, basketball, baseball, cricket.
- **Arcade 1v1 physics sports** with simple controls (head-ball style, car soccer).
- **Management games** that compete indirectly.

Casual turn-based sports (golf, pool) live in `skills/genre-playbooks/references/social-casino-party.md`. The fantasy is *sporting glory*: building a dream team, out-thinking or out-skilling a rival, living the real season.

### Core loop
```
build team (player cards, chemistry) → match (2–10 min, simplified controls or sim)
  → rewards → packs / upgrades / transfers → events tied to the real-world calendar → next match
```

### Meta loops
- **Ultimate-team collection**: packs of player cards, ratings, chemistry. Major loot-box exposure. EA stopped selling FIFA Points in Belgium in 2019 after the Belgian ruling.
- **Divisions and leagues** with promotion and relegation by season.
- **Live events synced to real competitions**: weekly fixtures, tournaments.
- **Clubs**, co-op events, pass.

### Session profile
Estimate: 2–10 minute matches (shortened halves) or 1–3 minute arcade duels, several per session. Spikes around real-world events. Landscape for sims, portrait possible for arcade.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Simplified controls (swipe to shoot, tap to pass, auto-run) | combat; UX automation | Touch-native inputs. Keep a skill ceiling through timing and direction |
| Physics-driven ball and characters (arcade) | combat | Deterministic physics enables replays and server validation |
| Player ratings + chemistry/links | build-craft; collection & randomness | Team-building depth. Readable stat cards |
| Stamina or contract consumables | time & energy; economy & resources | Paces play and spend. Handle carefully |
| Real-world calendar events | live events | Free relevance, at the cost of licences and data feeds |
| Divisions with promotion and relegation | social & competition | Fair-feeling progression ladder |

### Monetization model and typical mix
Ultimate-team packs (randomized, so odds disclosure applies and they are restricted in some jurisdictions), pass, event offers, energy and contracts, cosmetics (kits, stadiums, celebrations). Licences for leagues, clubs and player associations are a major fixed cost that shapes everything else.

### KPI expectations
Qualitative, because no sourced ranges were found. Expect strong seasonality around major tournaments, and retention tied to the real sports calendar. Track event participation, division progression and pack-to-pitch usage (do bought players actually get played?).

### Retention drivers
The real-world sports calendar. Team building. Divisions and rivals. Clubs. New card drops and team-of-the-week style content.

### Content pipeline and production scope (estimates)
- **Licensed sims**: annual roster and data updates, motion-captured animation, commentary, stadiums, a live events team. 100+ people.
- **Arcade 1v1 physics**: original characters, a few arenas, physics tuning. 8–25 people over 12–24 months.

All estimates.

### Reference titles
- *EA Sports FC Mobile* (EA): licensed ultimate team.
- *eFootball* (Konami).
- *MLB 9 Innings* (Com2uS).
- *Top Eleven* (Nordeus): football management.
- *Score! Match* (First Touch Games): swipe-football PvP.
- *Head Ball 2* (Masomo): arcade 1v1 physics.
- *Rocket League Sideswipe* (Psyonix, 2021): mobile car soccer.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Controls feel native to touch, with real skill expression | Console controls squeezed onto a phone |
| Short matches with highlight moments | Long matches with dead time |
| Licences or a strong original identity | Generic unlicensed knock-off with no hook |
| Fair matchmaking by skill and team rating | Pack-bought teams crush skill |
| Events follow the real calendar | Late or stale event content |

### Innovation vectors
- Arcade physics 1v1 formats.
- Sports plus party mini-games.
- Creator- or athlete-led brands.
- Async "challenge a friend" duels.
- Sim-management hybrids.
- AI commentary (disclosure rules apply).
- Women's leagues and underserved sports.

### Agent-buildability: 2/5 (arcade 1v1 physics: 3/5)
**Why low (licensed sims):**
- Licences.
- Motion-captured animation sets.
- Teammate AI.
- Physics feel.

**Arcade 1v1 is more feasible:**
- 2D or low-poly art.
- Deterministic physics with replay validation.
- Bots can play through a semantic API.

The feel of shots and collisions remains a human checkpoint.

### Starter feature list (P0 vertical slice: arcade 1v1 physics football)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Deterministic 2D physics step, fixed-point (tech) | Identical replays across 2 devices for 500 recorded matches |
| 2 | Move/jump/kick controls (gameplay) | Scripted inputs score from 3 set positions. Input-to-action latency ≤ 100 ms |
| 3 | 90-second match with goals, timer, sudden death (gameplay) | All end states reachable in scripted playthroughs |
| 4 | 3 characters with stats and one special power (content) | Data-driven. Unit tests per power |
| 5 | Bot opponent, 3 levels (gameplay) | Level win-rate ladder within the contract bands over 300 matches |
| 6 | Async or real-time PvP with server replay validation (tech) | Server re-sim matches the client result. Tamper test rejected |
| 7 | Glicko-2 rating + leagues (meta) | Updates per formula. Promotion and relegation thresholds unit-tested |
| 8 | Character upgrades with ranked normalization (meta) | Ranked uses normalized stats (unit test) |
| 9 | Goal celebration + replay highlight (vfx) | Replay generated from the input log. Passes visual gate |
| 10 | Card/pack or direct-purchase shop with odds disclosure (monetization) | Odds one tap away. Ledger reconciles |
| 11 | Event calendar driven by remote config (liveops) | Event toggles without a client update. Schedule honours time zones |
| 12 | Perf on low tier (perf) | p95 frame time ≤ 16.6 ms at 60 fps target in a match scenario |

## 7. Racing

### Definition and player fantasy
Race against other players (real-time or recorded ghosts) or AI on tracks with collectible vehicles. Sub-styles:
- Arcade (nitro, stunts, takedowns)
- Sim-lite (racing lines, braking points)
- Drag (shift timing)
- Physics climb (*Hill Climb Racing*)
- Kart (items)

The fantasy is *speed and mastery*: nailing the perfect line, collecting dream cars, beating rivals by a hair.

### Core loop
```
pick car → race (1–3 min) → placement + rewards → upgrade / tune car
  → unlock event, track or tier → pick car
```

### Meta loops
- **Car collection** through blueprints or cards (often randomized), with tiers and rarity.
- **Upgrades and tuning**: top speed, acceleration, handling, nitro.
- **Career and seasons**, live events with exclusive cars, ranked multiplayer seasons.
- **Clubs and crews.** Pass. Garage cosmetics (paint, decals).

### Session profile
Estimate: 1–3 minute races, 5–20 minute sessions, often fuel- or energy-paced. Landscape. One-touch auto-steer modes widen the audience.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Control schemes: tilt, tap-steer, auto-accelerate, assisted steer | UX automation; combat | *Asphalt*'s TouchDrive auto-steers on the racing line. Offer assists plus a manual mode |
| Nitro / boost management | economy & resources; combat | The core in-race decision in arcade racing |
| Drift and racing line | combat | The skill ceiling. Feedback through sound and trails |
| Ghost racing (async) | social & competition | Real-opponent feel with no netcode. Validate ghosts on the server |
| AI rubber-banding | combat; progression & upgrade | Keeps races tense. Disclose it or keep it subtle. Never in ranked |
| Vehicle stats + upgrade tiers | progression & upgrade | Car rating gates events. Power-matching in PvP |
| Drag-race shift timing | combat | Rhythm-like timing skill. Perfect-shift windows from config |

### Monetization model and typical mix
Car blueprint packs (randomized, so loot-box rules apply), upgrade materials, fuel/energy refills, VIP, pass, exclusive event cars, cosmetics. Real car brands require manufacturer licences and approvals, which constrain damage and customization.

### KPI expectations
Qualitative, because no sourced ranges were found. The car chase drives payer behaviour, and live events with exclusive cars drive reactivation. Track races per session, event completion, and how car rating distributions spread within PvP brackets.

### Retention drivers
Dream-car chase. Live events. Ranked seasons. Clubs. Personal-best and ghost rivalry with friends. Collection completion.

### Content pipeline and production scope (estimates)
- **3D arcade racing**: high-detail car models (rigid bodies; wheels separated for rotation, no skeletal rigging), tracks with environments, physics tuning, engine audio. 60–200 people at AAA-mobile quality.
- **2D physics racer**: 3–15 people over 9–18 months.

All estimates.

### Reference titles
- *Real Racing 3* (Firemonkeys/EA, 2013): sim-lite.
- *CSR Racing 2* (NaturalMotion, 2016): drag.
- *Hill Climb Racing 2* (Fingersoft, 2016): physics climb, async.
- *Asphalt 9: Legends* (Gameloft, 2018), later relaunched as *Asphalt Legends Unite*: arcade, TouchDrive.
- *Mario Kart Tour* (Nintendo/DeNA, 2019): kart.
- *Beach Buggy Racing 2* (Vector Unit): kart-arcade.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| A powerful sense of speed (camera, FOV, audio, VFX) | Floaty handling and weak speed feel |
| Control options from one-touch to manual | One control scheme that excludes most players |
| A fair PvP bracket by car rating | Pay-to-win cars decide multiplayer |
| A steady stream of event cars | Upgrade walls with fuel gates |
| Optimized for mid-tier devices | Overheating and huge downloads |

### Innovation vectors
- Async ghost leagues with friends.
- Short "one-lap" formats.
- Physics-sandbox racers.
- Racing plus collection-RPG hybrids.
- Creator-made tracks (UGC) validated by bots.
- Combat racing.
- Cross-play.

### Agent-buildability: 3/5 (2D physics racer 4/5; real-time multiplayer 3D 2/5)
**Why mid:**
- Vehicles are rigid bodies, so no skeletal rigging, which makes 3D generation plus Blender cleanup workable.
- Spline-following bots and ghost replays make every race verifiable.
- Async ghosts avoid netcode.
- Track layouts can be generated and validated.

**Why not higher:**
- Handling feel and sense of speed need human tuning on devices.
- Detailed car assets, licensing and engine audio.

### Starter feature list (P0 vertical slice: arcade racer with ghosts)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Deterministic vehicle physics at fixed timestep (tech) | Recorded inputs replay to the same lap time ±0 ms |
| 2 | Control schemes: tap-steer, tilt, assisted line (ux) | Each scheme completes the scripted lap. Setting persists |
| 3 | Nitro + drift-charge system (gameplay) | Charge rates from config. Unit tests for gain and spend |
| 4 | 2 tracks with checkpoints + anti-shortcut (content) | Bot completes both tracks. Skipping a checkpoint invalidates the lap |
| 5 | AI racers on splines with 3 skill levels (gameplay) | Lap-time distribution per level within the contract bands |
| 6 | Ghost record/upload/race (meta) | Ghost replays match the original. Server validates lap times |
| 7 | 4 cars with stats + upgrade tiers (meta) | Stat changes match the tuning table. Car rating computed per formula |
| 8 | Results, rewards, rating update (meta) | Glicko-2 update per formula. Rewards per placement table |
| 9 | Speed feel: FOV, camera shake, motion lines, engine pitch (vfx) | Passes `game-feel` checklist and visual gate. Motion effects respect the reduce-motion setting |
| 10 | Garage UI with compare (ui) | Stat deltas correct. Structural UI checks pass |
| 11 | Event from remote config with an exclusive car (liveops) | Toggled without a client update |
| 12 | Perf: 8 cars on track at 60 fps target, mid tier (perf) | p95 frame time ≤ 16.6 ms. 15-minute soak with no thermal throttling to critical |

## Volatile facts (as of Oct 2026 — verify before relying)

- *Honor of Kings* was among the top-grossing mobile games in Q1 2026 (with *Last War* and *Whiteout Survival*). H1 2026 mobile game IAP was about $40bn, −2% YoY — [Mobilegamer.biz (Sensor Tower)](https://mobilegamer.biz/data-digest-sensor-towers-h1-analysis-hay-days-comeback-julys-top-games-big-krafton-numbers-and-more/)
- Retention anchors (all genres): median D1 about 22%, D7 under 4%, D30 0.7–0.8%. Top 1% D1 64–68% — [Segwise (GameAnalytics)](https://segwise.ai/blog/mobile-gaming-app-user-retention-strategies)
- A Brazilian court ordered Riot to pay damages over *League of Legends* loot boxes and add age verification and probability disclosure (June 9, 2026; amount reported variously as €2.5M or $3M). Brazil's ECA Digital bans loot-box sales to under-18s from March 2026 — [Sheep Esports](https://www.sheepesports.com/articles/brazil-court-orders-riot-games-to-pay-eur2-5m-over-league-of-legends-loot-boxes/en)
- FTC v. Epic (Dec 19, 2022): $275M COPPA penalty plus $245M refunds over dark patterns. Voice and text chat must be off by default for children and teens — [FTC](https://www.ftc.gov/news-events/news/press-releases/2022/12/fortnite-video-game-maker-epic-games-pay-more-half-billion-dollars-over-ftc-allegations). The amended COPPA rule (compliance by Apr 22, 2026) adds biometric identifiers to personal information — [Toy Association](https://toyassociation.org/PressRoom2/News/2026-News/updated-coppa-rule-requirements-take-effect-april-22.aspx)
- Unity deprecated Multiplay Game Server Hosting on Apr 1, 2026 — [Unity status](https://status.unity.com/info_notices/362941). Photon Fusion is about free to 100 CCU and about $250/mo at 1,000 CCU (third-party figures) — [Crux](https://crux.supercraft.host/blog/photon-fusion-pricing-2026/)
- AI teammates and bots at scale (aggregator data, unverified): Tencent's *Peacekeeper Elite* AI Teammate (110M players covered) and Giant Network's *Paranormal Task Force* AI bots (25M+ AI matches in two months). *Eggy Party*'s AIGC tools reportedly produced 1M+ player-made items — [NexWorld panorama](https://nexworld.wiki/en/ai-games/ai-games-panorama-2026/)
- Play Integrity (Android) and App Attest/DeviceCheck (iOS) for attestation (background) — [Play Integrity](https://developer.android.com/google/play/integrity); [App Attest](https://developer.apple.com/documentation/devicecheck)

## Related skills
- `multiplayer-backend`: netcode models, matchmaking, ratings, servers.
- `game-architecture`: deterministic sim-core for replays and bots.
- `mechanics-codex`: combat, ranking and collection mechanic cards.
- `game-feel`: aim, hit feedback, speed feel.
- `mobile-ux`: touch controls, HUD layout for PvP.
- `monetization`: cosmetic-first PvP models, passes.
- `legal-ethics`: loot boxes, chat safety, bots disclosure.
- `qa-testing`: two-client sync tests, bot leagues, replay validation.
- `mobile-performance`: frame budgets and thermal soaks.
- `player-analytics`: queue health, match quality, churn after losses.
