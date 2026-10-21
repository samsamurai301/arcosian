# Shooter Playbooks (PC and Console Depth)

Shooters are the genre where feel is the product. A shooter that is balanced on paper but feels wrong dies in the first minute. This file holds seven playbooks in the shared 14-part template, plus a 15th part, "Platform notes", for PC, console, web and mobile differences:

1. Single-player campaign FPS / TPS
2. Arena and boomer shooter
3. Hero shooter (PC / console)
4. Battle royale (PC / console)
5. Extraction shooter
6. Co-op PvE mission / horde shooter
7. Twin-stick / top-down shooter

Five foundations come first: weapon feel and time-to-kill maths, hitscan versus projectile, aim assist and input fairness across mouse and gamepad, encounter design, and netcode basics. Ratings, matchmaking and netcode internals live in `skills/genre-playbooks/references/competitive-pvp.md` (§0 and the hero shooter and battle royale playbooks). Mobile shooters, casual shooters and shmups live in `skills/genre-playbooks/references/action-arcade-roguelite.md` (§6 and §8). This file does not repeat them. It adds PC and console depth. The headline for an agent pipeline: single-player campaigns, arena shooters against bots and twin-stick games are testable with bots and sims (3–4/5). Anything with a live many-player server, such as hero shooters, battle royale and extraction, scores 1/5 and should start as a bot-filled slice.

## Contents

| § | Playbook | Session profile (estimate) | Primary monetisation | Agent-buildability | First project for an agent pipeline? |
|---|---|---|---|---|---|
| 0 | [Shared foundations](#0-shared-foundations) | — | — | — | Read first |
| 1 | [Campaign FPS / TPS](#1-single-player-campaign-fps--tps) | 5–12 h campaign, 30–90 min sittings | Premium, DLC | 3/5 | Yes, one chapter |
| 2 | [Arena / boomer shooter](#2-arena-and-boomer-shooter) | 10–20 min levels or 5–10 min matches | Premium, early access | 4/5 (single-player) | Yes |
| 3 | [Hero shooter](#3-hero-shooter-pc--console) | 8–15 min matches | Cosmetics, pass, premium + pass | 1/5 | No, bot slice only |
| 4 | [Battle royale](#4-battle-royale-pc--console) | 15–30 min matches | Cosmetics, pass | 1/5 | No |
| 5 | [Extraction shooter](#5-extraction-shooter) | 20–45 min raids | Premium, cosmetics, pass | 1/5 | No, PvE raid slice only |
| 6 | [Co-op PvE / horde](#6-co-op-pve-mission--horde-shooter) | 15–40 min missions | Premium, DLC, cosmetics | 3/5 | Yes, with AI squadmates |
| 7 | [Twin-stick / top-down](#7-twin-stick--top-down-shooter) | 2–15 min runs | Premium, F2P with ads (mobile) | 5/5 | Yes |
| — | [Volatile facts](#volatile-facts-as-of-oct-2026--verify-before-relying) | — | — | — | Check before quoting numbers |

## How to use these playbooks

- Copy the core loop into `contract.json → loops[]`. Set `meta.genre: "shooter"` and `meta.subgenre` to the playbook slug. Set `meta.platforms`, `meta.input` (`mouse_keyboard`, `gamepad` or both) and `technical.multiplayer` (`none`, `async`, `realtime`). Multiplayer and input decide cost and buildability more than anything else.
- Turn the starter feature list into P0 `features.json` entries with `gs.py feature add`. Each acceptance criterion maps to `unit` or `playthrough` gate evidence (bots, sims, replays).
- Mechanic category labels: combat, build-craft, collection & randomness, progression & upgrade, economy & resources, social & competition, exploration & traversal, live events, UX automation. Resolve them with `gs.py kb "<mechanic>" --skill mechanics-codex`.
- KPI statements are qualitative unless sourced. Use the volatile-facts anchors and fit real curves after a playtest or beta.
- Decide input first. A game shipped for mouse and gamepad needs both feel profiles (§0.3) before any content work.

## 0. Shared foundations

### 0.1 Weapon feel and time-to-kill (TTK) maths
Time-to-kill is the tuning variable that sets the pace of every shooter. Compute it from data, then test it against latency and reaction time.

```
Shots to kill      N = ceil(HP / damage_per_hit)
Fire interval      dt = 60 / RPM
TTK (first shot at t=0)   TTK = (N − 1) · dt          (add reload/charge if any)
Sustained DPS      DPS = damage · RPM / 60 · accuracy
Worked example: 100 HP, rifle 25 dmg body / 50 dmg head, 600 RPM (dt = 0.10 s)
  body only: N = 4 → TTK = 0.30 s     one head + two body: N = 3 → 0.20 s
  all head:  N = 2 → TTK = 0.10 s     (my arithmetic)
```

- **Reaction check.** A typical human visual reaction time is about 200–250 ms (estimate; varies by person and display). If TTK is below reaction time plus round-trip latency, the victim dies before they can respond. That suits twitch arena shooters and punishes tactical ones. For a tactical shooter aim for TTK of 0.4–1.0 s so a flank can be survived. For an arena shooter, 0.5–1.5 s with armour and movement is common. These ranges are design guidance, not measured data.
- **Latency budget.** Effective advantage lost to latency ≈ one-way delay. At 60 ms RTT a fast-TTK game gives the lagging player a visible disadvantage. Use the netcode models in `skills/genre-playbooks/references/competitive-pvp.md` §0.3.
- **Falloff and range bands.** Define three bands per weapon (close, mid, long). Each has damage multiplier and spread. A common pattern is full damage to range A, linear falloff to range B, minimum after. Test that every weapon wins in exactly one band by TTK. A weapon that wins every band is a balance bug.
- **Spread and recoil.** Use a seeded pattern (learnable) or random bloom (not learnable). Learnable recoil rewards mastery. Random bloom suits casual and gamepad audiences. Keep first-shot accuracy exact for tap-fire.
- **Headshot multiplier.** 1.5×–2× is typical (estimate). A high multiplier with low TTK makes headshots the only skill. Check "shots to kill with headshot" against "shots without".
- **Feel layers.** Muzzle flash, recoil kick on camera, hit marker, hit sound with a distinct kill sound, damage numbers or screen shake, enemy flinch, and a visible tracer. Hit feedback must arrive on the same frame as the input resolves. See `game-feel`.
- **Reload and ammo.** Reload time 1.5–3 s (estimate) plus an animation cancel for tactical reloads. A reload longer than TTK × 5 makes every mistake lethal.

### 0.2 Hitscan versus projectile
| Model | How it resolves | Best for | Cost |
|---|---|---|---|
| Hitscan | Ray cast on fire. Hit is instant | Precision rifles, pistols, arena railguns, anything needing exact aim | Cheap. Needs lag compensation online |
| Fast projectile | Entity travels at speed v. Collision each tick | Rockets, arrows, grenades, heavy weapons | Needs lead and drop tuning. Adds prediction work |
| Projectile with drop | Gravity applies (ballistics) | Tactical and sim shooters, bows | Hard for gamepad users without assist |

```
Lead distance   lead = v_target · (distance / v_projectile)
Worked example: target strafes at 5 m/s, 50 m away, projectile 200 m/s
  flight time 0.25 s → lead = 1.25 m (about 1.4° of arc at that range)
Gravity drop    drop = ½ · g · t²    at t = 0.25 s, g = 9.8 → 0.31 m
```

- **Rule.** If lead exceeds about 1 m at the engagement range, most players on gamepad will miss. Add splash, a larger hitbox, or aim assist (§0.3).
- **Hitbox design.** Use capsules or simple boxes for the body, a smaller sphere for the head. Keep hitboxes a little more generous than the art for gamepad play. Test with a headless sim: fire 10,000 shots at moving targets with a noisy aim model and compare hit rates by input type.
- **Lag compensation.** For online hitscan, the server rewinds target positions to the shooter's view time. Cap the rewind (commonly 150–250 ms, estimate) so high-ping players cannot shoot around corners. See `competitive-pvp.md` §0.3.

### 0.3 Aim assist and input fairness: mouse versus gamepad
A mouse is faster and finer. A stick is slower but comfortable on a sofa. Cross-play matches the two, so fairness is a design problem.

```
Sensitivity (cm per 360°)   cm360 = 360 · 2.54 / (dpi · sens · yaw)
  Example: yaw 0.022°/count (a common engine convention), 800 dpi, sens 1.0
  cm360 = 914.4 / 17.6 ≈ 52 cm.   Doubling sens halves cm360 (26 cm).
Stick response   output = sign(x) · ((|x| − dz) / (1 − dz))^k      dz = deadzone, k = curve
  Example: dz 0.10, k 1.5, raw 0.55 → ((0.45)/(0.90))^1.5 = 0.35 of max turn speed
```

- **Aim assist types.** Slowdown (reduce turn speed when the reticle is over a target), friction, magnetism or pull (nudge toward the target), and rotational assist (move the aim when the target moves). Gamepad players get these. Mouse players do not.
- **Tune it as a budget.** Define a target: gamepad with assist should reach about X% of the mouse hit rate in a standard bot test. Choose X per game and measure with simulated players. Set it from data, not feel alone.
- **Fairness rules.** Never apply assist to mouse input. Detect device by the last-used input. Scale assist down at high skill brackets only if you also publish that fact. Give gamepad players the option to disable it. Hide it from the player who does not use it, but state its existence in the settings screen.
- **Cross-play.** Offer input-based matchmaking (gamepad pool, mouse pool, or both opt-in) if population allows. Ranked play often separates them. Check population arithmetic with `competitive-pvp.md` §0.2 before splitting pools.
- **Mandatory settings.** Separate X/Y sensitivity, ADS multiplier, FOV slider (PC), invert, deadzone sliders, response curve choice, toggle versus hold for aim, sprint and crouch, remappable keys and buttons, and a sensitivity-per-zoom option. See `accessibility-localization`.

### 0.4 Encounter design
An encounter is a combat puzzle with a budget: enemies, ammo, health, space and time.

```
Encounter budget   B = Σ (enemy_cost_i)           set B per difficulty tier
Ammo needed        A = Σ (hits_to_kill_i) / accuracy
  Worked example: 8 grunts, 4 hits each, player accuracy 60% → A = 32 / 0.6 ≈ 53 rounds
  Ship pickups for about 120% of A at normal difficulty (estimate), 90% at hard
Arrival rate       enemies spawned per second ≤ player kill rate · (1 + pressure)
  If player kill rate is 0.5/s, a pressure factor of 0.3 → max sustained arrival 0.65/s
```

- **Role mix.** Use at least three roles per arena: a rusher (forces movement), a ranged suppressor (forces cover), a heavy or shielded unit (forces target choice or weapon swap), plus an occasional flanker or sniper to stop camping. Never spawn two unreadable enemies at once.
- **Pacing.** Alternate tension and release. A common ratio is 30–90 s combat, 30–60 s traversal or story, and a larger set piece every 15–20 minutes (estimates).
- **Readability.** Every enemy attack has a telegraph the player can see and hear. Silhouette and colour tell the role. Off-screen threats get a directional indicator.
- **Cover and flow.** In a cover shooter, space cover in chains so the player always has a next position. In an arena shooter, give vertical routes and loops (see `level-design`).
- **Difficulty.** Scale enemy HP, damage, accuracy and spawn count separately. Make accuracy and aggression adaptive, not HP only. A bullet sponge is a failure. See `progression-difficulty`.
- **Verification.** Run bot squads of three skill levels through each encounter 500 times. Gate on clear rate, average health at the end and time taken within the contract's band.

### 0.5 Netcode basics (link, not a repeat)
Use `skills/genre-playbooks/references/competitive-pvp.md` §0.3 for the netcode models (authoritative server, client prediction, lag compensation, lockstep and rollback), §0.1–0.2 for ratings and matchmaking, and §0.4 for anti-cheat. Shooter-specific reminders:
- Run authoritative servers for any competitive mode. Peer-hosted co-op is acceptable for PvE only if host advantage and cheating are accepted by design.
- Send inputs, not positions. Predict locally, reconcile on server correction.
- Tick rate is a design choice: higher tick helps fast-TTK games. Budget server cost per concurrent user before committing (`multiplayer-backend`).
- Test under packet loss and jitter (for example 2% loss and 40 ms jitter) before judging feel.

## 1. Single-player campaign FPS / TPS

### Definition and player fantasy
A scripted, authored campaign of set-piece fights, story and spectacle. The fantasy is being *the hero in an action film*: weapons that feel great, enemies that react, and a story worth finishing. First-person or third-person with cover.

### Core loop
```
enter encounter space → read enemies and cover → fight with weapon variety
  → scavenge ammo/health → clear → traversal or story beat → set piece
  → checkpoint → next chapter → upgrade or unlock
```

### Meta loops
- **Weapon and ability upgrades.** Mod slots, skill trees or collectible upgrades.
- **Difficulty ladder.** Higher modes, new-game-plus, challenge modifiers.
- **Collectibles and secrets.** Lore, weapon mods, hidden areas.
- **Post-launch.** DLC chapters, a horde or score-attack side mode, mod support on PC.

### Session profile
Estimate: 30–90 minute sittings across a 5–12 hour campaign. Players want to stop at a checkpoint. Replay value comes from difficulty modes and speedrun communities.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Weapon handling and TTK | combat | §0.1. The core of the game |
| Enemy archetypes and AI roles | combat | Roles in §0.4. AI must flank and use cover |
| Set pieces and scripted beats | exploration & traversal | Cost is high per minute. Budget them |
| Weapon upgrades or mods | progression & upgrade | Meaningful choices, not flat stat bumps |
| Cover and traversal (TPS) | exploration & traversal | Camera and snap-to-cover need tuning |
| Health model (regen, pickups, armour) | combat | Regen suits cover shooters. Pickups suit arena pacing |
| Difficulty modifiers | progression & upgrade | Scale several variables (§0.4) |

### Monetisation model and typical mix
Premium purchase, sometimes with a story DLC or a deluxe edition. Subscription catalogues (Game Pass and similar) trade upfront sales for a licence fee or guaranteed payment: check the deal terms. No in-game purchases is the norm and keeps reviews high. Live-service bolt-ons to a campaign usually hurt reception. Keep any cosmetic add-on out of the campaign path.

### KPI expectations
Qualitative. Premium success: store rating, completion rate (what share reach the final chapter), refund rate (often watched on Steam for the first two hours) and word of mouth. Track the chapter where most players drop. No sourced benchmark ranges found.

### Retention drivers
Story momentum, weapon satisfaction, spectacle, difficulty challenge, speedrun and mod communities, and DLC.

### Content pipeline and production scope (estimates)
Level geometry, scripted encounters, enemy and weapon animation, audio and a lot of polish. Rough estimates: AA scope 20–60 people over 2–4 years. A small team can do a 4–6 hour campaign in a stylised look in 1.5–3 years. Linear campaigns are cheaper per hour than open-world games.

### Reference titles
- *Half-Life 2* (Valve, 2004): scripted physics and pacing.
- *Doom (2016)* and *Doom Eternal* (id Software, 2016, 2020): fast combat with resource-driven pace.
- *Titanfall 2* (Respawn, 2016): short, inventive campaign.
- *Gears of War* (Epic, 2006): cover-based third-person template.
- *Metro Exodus* (4A Games, 2019): narrative with survival ammo.
- *Wolfenstein: The New Order* (MachineGames, 2014).

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Every weapon is fun to fire and kills read clearly | Guns feel floaty and enemies are bullet sponges |
| New ideas arrive through the whole campaign | The same arena repeats for 8 hours |
| Fair checkpoints and difficulty options | Long replays after each death |
| Strong pacing with quiet beats | Constant intensity with no rest |
| Short, tight campaign that respects time | Padded with collectibles and filler |

### Innovation vectors
- Adaptive AI squads that learn from the player's tactics.
- Roguelite structures over campaign levels.

### Agent-buildability: 3/5
**What agents do well:** weapon data tables, TTK and ammo economy sims, enemy AI behaviour trees, bot playthroughs of encounters, checkpoint logic, save systems, settings menus.
**Why not higher:** art, animation, audio mix, set-piece direction and the "feel" pass need human taste and iteration. Story and pacing need review.

### Starter feature list (P0 vertical slice: one chapter, 20 minutes)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Player controller: move, sprint, crouch, jump, mouse and gamepad look (gameplay) | Input responds within one frame. cm360 and stick curve match §0.3 formulas |
| 2 | 3 weapons with data-driven stats (gameplay) | TTK per weapon per range band matches the table within 5% in a sim |
| 3 | Hit feedback: marker, sound, flinch, kill confirm (feel) | Feedback fires the same frame the hit resolves. Verified by replay |
| 4 | 4 enemy types with roles and telegraphs (gameplay) | Each role is distinct. Telegraph lasts at least the contract's minimum |
| 5 | Enemy AI with cover use and flanking (gameplay) | A bot test shows at least 30% of enemies change position mid-fight |
| 6 | Ammo and health economy (economy) | Pickup total is 110–130% of §0.4 ammo need at normal difficulty |
| 7 | 3 encounters + 1 set piece (content) | Bots at three skill levels clear within the target win-rate band |
| 8 | Checkpoints and autosave (tech) | A kill-and-reload test resumes at the last checkpoint with state intact |
| 9 | Aim assist for gamepad with an off switch (input) | Assist off equals raw input. Mouse never receives assist |
| 10 | Difficulty modes, 3 tiers (progression) | Each tier changes at least HP, damage and accuracy. Documented |
| 11 | Settings: FOV, sensitivity, remap, subtitles (ux) | All options persist and apply without restart |
| 12 | Pause, quit and resume (tech) | State survives pause, alt-tab and console suspend |

### Platform notes
- **PC.** Mouse and keyboard first. Add FOV slider, uncapped frame rate, ultrawide support, key remapping, and graphics presets. Steam Deck Verified expects the default controller layout to reach all content (volatile facts).
- **Console.** Gamepad with aim assist, 60 fps performance mode and a quality mode, fast resume, trophy or achievement sets and certification rules (`console-pathway`). Autosave is expected.
- **Web.** Rare for full campaigns. Pointer lock needs a click. Download size and load time are the limit. Short slices work.
- **Mobile.** Full campaigns are uncommon. See `action-arcade-roguelite.md` §6 for casual shooters.
- **Business.** PC and console are premium-priced. Review score and wishlists drive sales. See `pc-web-release`.

## 2. Arena and boomer shooter

### Definition and player fantasy
Fast, movement-heavy shooters with big weapons, pickups on the map and no regenerating health. The player is *a force of nature*: strafing, rocket-jumping and chaining kills. "Boomer shooter" usually means a retro-styled single-player take on the 1990s FPS. Arena PvP means small maps and a fast TTK.

### Core loop
```
spawn → collect weapons, health and armour → fight (move constantly)
  → score kills or clear the level → find keys and secrets → exit
  → next level (single-player) or next match (PvP)
```

### Meta loops
- **Level and secret hunting.** Secrets, par times, key-door puzzles.
- **Weapon and enemy ladder.** A new weapon or enemy every few levels.
- **Score and speedrun.** Leaderboards, ghost replays.
- **Mod and map-editor community.** A long tail on PC.
- **PvP variants.** Ladders, duels, tournaments.

### Session profile
Estimate: 10–20 minute levels for single-player, 5–10 minute matches for PvP. High repeat play per level for score runs.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Fast movement (strafe, bunny hop, rocket jump) | exploration & traversal | Tune acceleration and air control. Speed is the skill |
| Pickup economy: health, armour, ammo, power-ups | economy & resources | On the map, not regenerating. Respawn timers shape the meta |
| Weapon swap and spread of roles | combat | Each weapon has a best situation (§0.1) |
| Key-and-door level structure | exploration & traversal | Simple gating (`level-design`) |
| Gib, pain and hit reactions | combat | Large feedback. Readable even at speed |
| Difficulty by enemy count and speed | progression & upgrade | Scale arrival (§0.4) |

### Monetisation model and typical mix
Premium, often cheaper than a campaign shooter. Early access is common for boomer shooters, with the community feeding map and weapon feedback. Cosmetics are rare. PvP arena games struggle to attract a population without a large publisher or a clear niche.

### KPI expectations
Qualitative. Single-player: completion rate, level drop-off and speedrun activity. PvP: concurrent players per bracket (population matters more than anything). No sourced benchmarks found.

### Retention drivers
Movement mastery, secrets, high difficulty, leaderboards, mods, new levels and community map contests.

### Content pipeline and production scope (estimates)
Levels and enemies in a stylised or low-poly look are cheap to make compared with realistic 3D. A solo developer or a team of 3–10 can ship in 1–3 years. Level editors and procedural generators lift the output (`procedural-generation`).

### Reference titles
- *Quake* and *Quake III Arena* (id Software, 1996 and 1999): the arena template.
- *Unreal Tournament* (Epic, 1999).
- *Doom* (id Software, 1993): the origin of the single-player template.
- *Ultrakill* (New Blood, early access from 2020): style-meter movement shooter.
- *Dusk* (David Szymanski, 2018) and *Amid Evil* (2019): modern boomer shooters.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Movement feels great at speed | Controls feel heavy or unresponsive |
| Weapons and enemies force different tactics | One weapon dominates |
| Levels reward exploration and replay | Levels are long mazes with no landmarks |
| Clear rewards for aggression (health from kills) | Defensive play is optimal |
| PvP ships with enough players or strong bots | PvP launches to an empty lobby |

### Innovation vectors
- Style meters and risk-reward health.
- Roguelite structure with arena fights.
- Procedurally assembled arenas with hand-tuned encounters.
- Reduced-speed accessibility modes.
- Single-player with strong PvP bots in place of a live population.

### Agent-buildability: 4/5 (single-player), 1/5 (live PvP)
**Why high:** simple geometry, data-driven weapons and enemies, solver-friendly key-door graphs, bot playthroughs and procedural level generation.
**Why not 5:** movement feel needs human tuning and art direction defines the audience.

### Starter feature list (P0 vertical slice: 3 levels, 6 weapons)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Movement: strafe acceleration, air control, jump, optional dash (gameplay) | Peak speed and acceleration match the tuning table within 2% in a sim |
| 2 | 6 weapons with distinct roles (gameplay) | Each weapon is best at one range band in the TTK sim (§0.1) |
| 3 | Pickups with respawn timers (economy) | Respawn follows the table. No pickup is unreachable |
| 4 | 6 enemy types (gameplay) | Each has a telegraph. Role mix per arena meets §0.4 |
| 5 | Key-door level graph (level) | Solver confirms every level is completable and every key is reachable |
| 6 | 3 levels with secrets and par times (content) | Bot clears each within the win-rate band. Par time is achievable |
| 7 | Hit feedback and pain reactions (feel) | Hit confirmation within one frame of damage |
| 8 | Score and ghost replay (meta) | Ghost replays deterministically from stored input |
| 9 | Difficulty tiers (progression) | Tiers change enemy count and speed, not only HP |
| 10 | Rebindable controls and FOV (ux) | Settings persist. Gamepad profile passes §0.3 curve tests |
| 11 | Bot opponent for a deathmatch map (gameplay) | A bot at three skill levels is beatable and distinguishable |
| 12 | Checkpoint and quick save (tech) | Quick load restores exact state |

### Platform notes
- **PC.** The natural home. Mouse feel, FOV slider, mod and workshop support, speedrun tooling. Demos in a Steam Next Fest style event help wishlists (`pc-web-release`).
- **Console.** Gamepad movement needs tuned acceleration and strong aim assist. Boomer shooters ported to console are common, with 60 fps as the bar.
- **Web.** Good fit for small arena demos in WebGL or WebGPU. Pointer lock and load size matter.
- **Mobile.** Poor fit for dual-analog arena movement. Prefer simplified or auto-fire variants (`action-arcade-roguelite.md` §6).
- **Business.** Low price and a niche audience. Wishlists, demos and streamer coverage drive discovery.

## 3. Hero shooter (PC / console)

### Definition and player fantasy
Team-based shooters where each player picks a character with a fixed kit of abilities. The fantasy is being *a specialist in a team of specialists*: your hero, your role, your counterplay. `skills/genre-playbooks/references/competitive-pvp.md` §3 covers the genre across platforms. This section adds PC and console depth.

### Core loop
```
pick hero (counter the enemy team) → objective fight (capture, escort, push)
  → use abilities + ultimate → win or lose round → swap heroes → next round
  → rating and rank progression → cosmetics unlock
```

### Meta loops
- **Ranked ladder.** Seasons, placement matches, rank rewards (ratings: `competitive-pvp.md` §0.1).
- **Hero roster releases.** New heroes on a cadence. Each needs balancing against the rest.
- **Battle pass and cosmetics.** Skins, emotes, sprays.
- **Esports.** A competitive scene and spectator tools.

### Session profile
Estimate: 8–15 minute matches, 2–5 matches in a sitting. Queue time is a large part of the session on low-population modes.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Hero kits (primary fire, 2–3 abilities, ultimate) | combat | Each hero has one clear job and a counter |
| Role system (tank, damage, support) | social & competition | Role queue controls composition. Costs queue time |
| Ultimate charge | combat | Charge rate sets how often match-turning moments occur |
| Objective modes | social & competition | Control, escort, push. Overtime rules matter |
| Counter-picking and hero swap | combat | Free swap invites counter-play but needs readable counters |
| Ranked and matchmaking | social & competition | `competitive-pvp.md` §0.1–0.2 |

### Monetisation model and typical mix
Cosmetic-only free-to-play with a battle pass is the common route. Some titles use premium purchase plus a pass. Do not sell heroes that change competitive power unless all heroes unlock free by play. Loot-box rules apply to any random cosmetic packs (see `skills/genre-playbooks/references/rpg-gacha.md`).

### KPI expectations
Qualitative. Key metrics: queue time per role and per rank, match quality (predicted win-probability spread), hero pick and win rates, new-player retention through the first 10 matches, and report rates. Population is the survival metric.

### Retention drivers
Rank progress, team play and friends, hero mastery, balance patches, seasonal content, cosmetics and esports.

### Content pipeline and production scope (estimates)
Maps, heroes (concept, model, rig, animation, VFX, audio, balance), cosmetic production, live operations, anti-cheat, server operations and a community team. Rough estimate: 100+ people, 3–5 years. Not indie-feasible at full scale.

### Reference titles
- *Team Fortress 2* (Valve, 2007): class-based template.
- *Overwatch* (Blizzard, 2016) and *Overwatch 2* (2022): the genre's reference.
- *Valorant* (Riot, 2020): agent-based tactical shooter.
- *Concord* (Firewalk/Sony, August 2024): shut down within about two weeks of launch. A cautionary example of a premium-priced entrant in a crowded field. This is a public record, not a volatile figure.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Distinct heroes with readable silhouettes and sounds | Heroes feel alike or kits are hard to read |
| A launch population big enough for short queues | Launch to empty lobbies, long queues |
| Fair monetisation that never sells power | Pay-to-win perception |
| Strong first 10 matches (bots, tutorials, low-rank pools) | New players meet veterans |
| Frequent, transparent balance patches | Slow or opaque balance |

### Innovation vectors

### Agent-buildability: 1/5
**Why low:** authoritative real-time servers, 3D animation per hero, balance across many heroes and a live population cannot be verified from client gates.
**What agents do well:** hero stat tables, TTK and ultimate-charge sims, bot logic for a 3v3 slice, matchmaking and rating simulations, balance spreadsheets.

### Starter feature list (P0 vertical slice: 3v3 vs bots, one control point, 4 heroes)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Hero kit system with data-driven abilities (gameplay) | Each ability has cooldown, cost and effect in data. Unit tests cover targeting |
| 2 | 4 heroes: tank, 2 damage, support (gameplay) | Each beats its intended counter in a sim at equal skill |
| 3 | Control-point objective with overtime (gameplay) | Capture rates match the table. Overtime ends correctly |
| 4 | Ultimate charge (gameplay) | Charge reaches full at the target time in a bot match (±10%) |
| 5 | Bot opponents at 3 skill levels (gameplay) | Win rates against each tier fall in the band |
| 6 | Hero select with counter hints (ui) | Selection locks per rules. Swap allowed in respawn |
| 7 | Hit feedback and kill feed (feel) | Feedback fires on the same frame. Kill feed lists the last 5 events |
| 8 | Rating simulation (meta) | A sim of 10,000 players converges to true skill within the contract error |
| 9 | Local server with client prediction (tech) | Two clients stay in sync at 60 ms RTT and 2% loss |
| 10 | Report and mute tools (safety) | Reports log with match ID. Muted players cannot be heard |

### Platform notes
- **PC.** Mouse aim with highest skill ceiling. Needs anti-cheat, spectator tools and a mod-resistant client. Steam is the main store (`pc-web-release`).
- **Console.** Gamepad with aim assist, platform-specific multiplayer entitlements (online subscription rules) and certification (`console-pathway`). Cross-play needs input matching (§0.3).
- **Web.** Not suitable for full hero shooters. Small browser arena games exist.
- **Mobile.** Different genre in practice. See `competitive-pvp.md` and `action-arcade-roguelite.md`.
- **Business.** F2P cosmetics and a pass dominate. A premium price is a launch risk without a guaranteed population.

## 4. Battle royale (PC / console)

### Definition and player fantasy
Many players drop into a shrinking arena and fight to be the last survivor. The fantasy is *survival against dozens*: the tension of the final circle and the story every match tells. `skills/genre-playbooks/references/competitive-pvp.md` §2 covers the genre. This section adds PC and console depth.

### Core loop
```
drop and land → loot weapons and armour → move with the circle
  → fight or avoid → rotate → final circle → win or die
  → XP, pass and cosmetics → queue again
```

### Meta loops
- **Seasons and map changes.** Map updates and limited-time modes.
- **Battle pass.** Tiered cosmetic rewards.
- **Ranked mode.** A skill ladder separate from casual.
- **Squads and friends.** Duo and squad queues that drive social play.
- **Creator tools.** Custom modes and maps (some platforms).

### Session profile
Estimate: 15–30 minutes a match. Early death means a quick requeue, so sessions are 1–4 hours for core players. Spectating after death is part of the loop.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Shrinking zone | exploration & traversal | Zone timing sets match length and fight density |
| Loot and gear tiers | collection & randomness | Randomness shapes each match. Keep tier gaps modest |
| Drop and landing choice | exploration & traversal | Hot drops versus safe drops is the first decision |
| Large-world netcode and interest management | social & competition | Server cost scales with players and map size |
| Downed state and revive (squads) | social & competition | Keeps squads in play. Adds tactical depth |
| Spectator and replay | UX automation | Retention tool for dead players |

### Monetisation model and typical mix
Free-to-play with cosmetics and a battle pass. No gameplay power for sale. Ads are not used in PC and console titles. Large servers and anti-cheat are a heavy fixed cost.

### KPI expectations
Qualitative. Track median time alive, bot-fill rate (if bots fill matches), queue time, fill rate at the match start, average squad size, per-region concurrent users and cheater report volume. See `competitive-pvp.md` for sourced anchors.

### Retention drivers
Match variety (every round differs), friends, seasonal content, ranked progress, creator events and streamer culture.

### Content pipeline and production scope (estimates)
A large map, loot tables, a weapon set, vehicles, anti-cheat, server infrastructure and constant live operations. Rough estimate: 100–300 people for a competitive launch. Smaller teams can ship a 20–40 player variant with a small map (estimate).

### Reference titles
- *PUBG: Battlegrounds* (Krafton, 2017): the PC breakout.
- *Fortnite* (Epic, 2017): building and a platform strategy.
- *Apex Legends* (Respawn, 2019): hero abilities and ping system.
- *Call of Duty: Warzone* (Activision, 2020).

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| A strong launch population and a clear identity | A late entrant with no hook |
| Short time-to-first-fight for new players | Long dead drops with nothing to do |
| Anti-cheat and fast reporting | Cheaters drive away the population |
| Balanced loot randomness | Loot luck decides most matches |
| Cross-platform play and party support | Friends cannot play together |

### Innovation vectors
- PvE-plus-PvP hybrids.
- Bots that fill lobbies and teach new players.

### Agent-buildability: 1/5
**Why low:** large authoritative server, interest management, anti-cheat, art-heavy map and a live population.
**What agents do well:** zone-timing sims, loot-table balance sims, bot logic for a 10-player slice, matchmaking sims.

### Starter feature list (P0 vertical slice: 10-player bot match on a 1 km² map)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Zone schedule with damage per phase (gameplay) | Zone radii and timers match the table. Damage applies outside |
| 2 | Loot tables by region and tier (economy) | Spawn distribution matches the table in a 1,000-match sim |
| 3 | 8 weapons and 3 armour tiers (gameplay) | TTK matrix (§0.1) has no weapon dominating all bands |
| 4 | Drop and parachute (gameplay) | Players land within the map bounds and can steer |
| 5 | Bot players at 3 skill levels (gameplay) | A full 10-bot match completes in the target time (±20%) |
| 6 | Downed and revive (gameplay) | Revive time and health follow the table |
| 7 | Spectator after death (ux) | Spectator follows the killer or a teammate. Can leave to the menu |
| 8 | Match result and XP (meta) | Placement awards XP per the table |
| 9 | Server tick and interest management (tech) | Bandwidth per client stays under the contract budget at 10 players |
| 10 | Replay file per match (tech) | Replay plays back deterministically to the final circle |

### Platform notes
- **PC.** Highest skill ceiling and the largest cheat problem. Needs kernel-level or server-side anti-cheat decisions, which affect Linux and Steam Deck support. State this in the plan.
- **Console.** Cross-play and aim assist balance are central. Platform holders set online subscription and certification rules (`console-pathway`).
- **Web.** Not suitable for 50+ player matches. Small-scale web battle royale (up to 10–20 players) exists.
- **Mobile.** Large population, different controls and device spread. See `competitive-pvp.md` §2.
- **Business.** F2P with cosmetics. Fixed server cost is high before any revenue.

## 5. Extraction shooter

### Definition and player fantasy
Players enter a map with gear and objectives, loot valuables, and must reach an exit alive to keep what they found. Death loses the gear carried. The fantasy is *high-stakes scavenging*: every item has weight because you can lose it.

### Core loop
```
prepare loadout (risk what you can afford) → enter the raid
  → loot, complete tasks, avoid or fight others and AI
  → decide when to leave → extract (or die and lose gear)
  → sell or stash loot → upgrade hideout → better loadout
```

### Meta loops
- **Stash and hideout.** Persistent inventory and crafting.
- **Trader and quest progression.** Task chains unlock gear and areas.
- **Skill and character progression.** Small, persistent improvements.
- **Seasons and wipes.** Some titles reset progress on a schedule.
- **Insurance and recovery.** Systems that soften losses to keep players returning.

### Session profile
Estimate: 20–45 minute raids with menu management between them. Sessions of 1–3 hours. Time in the stash is as significant as time in the raid.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Risk-reward gear loss | economy & resources | The core tension. See the EV model below |
| Extract points | exploration & traversal | Make exits contested, timed or conditional |
| Inventory and weight | economy & resources | Grid inventory or weight limit adds decisions and UI cost |
| AI enemies plus players (PvPvE) | combat | AI keeps the map alive when players are few |
| Ballistics and armour | combat | Armour tiers versus ammo tiers set TTK (§0.1) |
| Hideout and crafting | build-craft | The reason to come back after a loss |
| Proximity voice and sound design | social & competition | Audio is gameplay. Footstep clarity is key |

```
Raid risk model (estimate, for tuning)
  EV = p_extract · loot_value − (1 − p_extract) · gear_cost
Worked example: loadout cost 4,000; average loot on success 6,000; p_extract 0.6
  EV = 0.6·6,000 − 0.4·4,000 = 3,600 − 1,600 = +2,000 per raid
  If p_extract falls to 0.35 → EV = 2,100 − 2,600 = −500. Players will stop risking.
Keep EV positive for a mid-skill player at mid-tier loadouts, negative for over-gearing.
```

### Monetisation model and typical mix
Mostly premium purchase (one-off or tiered editions), with cosmetics and an optional pass. Avoid selling power or progress. Some entrants use F2P. Because stash and economy carry real value, any real-money shortcut gets scrutiny.

### KPI expectations
Qualitative plus anchors in volatile facts. Track raid survival rate by skill band, share of raids ending in a PvP kill versus an AI kill, loadout cost distribution, stash growth rate, time from install to first successful extraction and quit rate after a loss.

### Retention drivers
Stakes, stories from raids, hideout progress, task chains, seasonal content and friends in a squad. Fair loss recovery keeps players returning.

### Content pipeline and production scope (estimates)
Large, detailed maps, a gear and ammo catalogue, AI, a persistent backend for inventories, anti-cheat, an economy team and constant live updates. Rough estimate: 50–200 people. A PvE-only raid slice with AI is feasible for a small team.

### Reference titles
- *Escape from Tarkov* (Battlestate Games, 2017): the hardcore reference.
- *Hunt: Showdown* (Crytek, 2019): bounty-hunting variant.
- *ARC Raiders* (Embark Studios, October 2025): a mass-market PvPvE take. Sales figures in volatile facts.
- *Marathon* (Bungie): scheduled for 5 March 2026 on PC, PS5 and Xbox Series at a listed $39.99. Post-launch performance not verified here.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Losses feel fair and recoverable | Total loss with no way back |
| AI keeps raids interesting at low population | Empty raids, or a hostile new-player experience |
| Accessible entry (safe tutorial, low-tier lobbies) | Steep learning cliff and veteran predation |
| Strong sound and clear information design | Unreadable audio and UI |
| Strict anti-cheat and economy protection | Cheating and gold-selling ruin the economy |

### Innovation vectors
- PvE-first extraction with optional PvP.
- Casual-friendly loss rules (insured gear, free loadouts).

### Agent-buildability: 1/5
**Why low:** persistent economy, real-time servers, cheating risk, art-heavy maps.
**What agents do well:** economy and EV simulation (`economy_sim.py`), loot-table balance, a single-player PvE raid slice with AI, inventory UI and stash logic.

### Starter feature list (P0 vertical slice: single-player PvE raid on one map)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Loadout and grid inventory (ui) | Items snap to grid. Weight limit enforced. Save survives restart |
| 2 | One map with 3 extract points (level) | Every extract is reachable. Conditions evaluated per the rules |
| 3 | Loot tables and containers (economy) | Distribution matches the table over 1,000 raids |
| 4 | 6 weapons, 3 ammo tiers, 3 armour tiers (gameplay) | TTK matrix has no dominant option. Armour penetration formula tested |
| 5 | AI scavengers and a boss (gameplay) | AI uses cover and hears gunfire (sound propagation tested) |
| 6 | Death loses carried gear, with optional insurance (economy) | Loss rules match the table. Insurance returns items after a delay |
| 7 | Stash and one trader (meta) | Prices follow the table. Selling and buying update the stash atomically |
| 8 | Raid EV simulation (balance) | Bots at three skill levels show EV in the intended bands (§ above) |
| 9 | Hideout upgrade, 3 levels (meta) | Upgrade costs and effects follow the tuning table |
| 10 | Timer and raid end (gameplay) | Raid ends at the time limit with the stated penalty |

### Platform notes
- **PC.** Mouse, proximity voice, heavy anti-cheat. The audience is used to long, complex games and wipes.
- **Console.** Gamepad inventory management is a UI challenge. Cross-play and aim assist balance (§0.3). Certification applies (`console-pathway`).
- **Web.** Not suitable for the full genre. Simple PvE raid demos are possible.
- **Mobile.** Smaller-scale titles exist. Controls and screen size reduce complexity.
- **Business.** Premium price plus cosmetics. An economy that resets or is protected from real-money trade avoids pay-to-win concerns.

## 6. Co-op PvE mission / horde shooter

### Definition and player fantasy
Two to four (sometimes more) players team up against AI enemies across missions or waves. The fantasy is *a squad against the odds*: calling for backup, holding a position, and the stories of a close win.

### Core loop
```
choose mission and loadout → deploy → fight waves or advance objectives
  → use team abilities and stratagems → complete or extract
  → earn currency and unlocks → upgrade loadout → next mission
```

### Meta loops
- **Unlock trees.** Weapons, perks, stratagems or classes.
- **Difficulty ladder.** Harder tiers with higher rewards.
- **Seasonal and live events.** New enemies, missions and limited-time goals.
- **Social goals.** A shared community objective (some titles run a server-wide campaign).
- **Cosmetics.** Armour, emotes, weapon skins.

### Session profile
Estimate: 15–40 minute missions, 1–3 hour sittings with friends or matchmaking. Short enough for a weeknight and long enough for a story.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Enemy waves with a director | combat | Director adapts spawn rate to team stress (see below) |
| Class or loadout roles | combat | Roles complement. Avoid mandatory classes |
| Friendly fire and team abilities | social & competition | Friendly fire adds tension. Make it an option |
| Revive and downed state | social & competition | Keep teammates in play |
| Mission objectives | exploration & traversal | Escort, defend, retrieve, sabotage |
| Scaling by player count | progression & upgrade | Scale enemy HP and spawns per player |
| Shared resources | economy & resources | Ammo and supply drops shared across the squad |

```
Wave budget (horde)   B(w) = B0 · g^(w−1) · (1 + 0.25 · (players − 1))
Worked example: B0 = 100, g = 1.12, 4 players → wave 10: 100 · 2.77 · 1.75 ≈ 485 points
Director stress   S = recent damage taken / team max health (rolling 20 s)
  If S > 0.6 → pause spawns and drop supplies; if S < 0.2 → raise spawn rate by 20%
```

### Monetisation model and typical mix
Premium purchase with optional cosmetics, warbonds or passes, and paid DLC. Fair live-service models give gameplay free through play. Selling power in PvE reduces trust. PvE co-op needs a smaller server load than PvP.

### KPI expectations
Qualitative. Track mission completion rate by difficulty, wipe rate, time to first co-op session, share of solo versus squad play, friend invites per player and difficulty tier distribution. Aim to keep completion at a target band you set per tier. See `progression-difficulty`.

### Retention drivers
Friends, stories from missions, unlock progress, difficulty ladders, seasonal events and a developer who listens.

### Content pipeline and production scope (estimates)
Missions and maps (often procedural with set pieces), an enemy roster with distinct behaviours, weapons and gear, networking for 2–4 players (peer or dedicated), and cosmetic content. Rough estimate: 15–80 people over 2–4 years.

### Reference titles
- *Left 4 Dead 2* (Valve, 2009): the AI director template.
- *Deep Rock Galactic* (Ghost Ship, 2020): class co-op with procedural caves.
- *Helldivers 2* (Arrowhead, February 2024): third-person co-op with stratagems and a shared campaign. A May 2024 dispute over a required account link led to a Steam review backlash. A lesson on platform account requirements. Not a volatile figure.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Strong "friend stories" and team abilities | Players ignore each other |
| Matchmaking and drop-in play work | Lobbies fail. Players cannot join |
| Mission variety and enemy variety | The same mission repeats |
| Scaling that keeps solo and 4-player fun | Solo is unplayable or four-player is trivial |
| Fair progression | Grind for gear that changes balance |

### Innovation vectors
- AI squadmates for solo play.
- Persistent campaigns shared across a player base.
- Procedural missions with hand-built set pieces.

### Agent-buildability: 3/5
**Why mid:** missions, enemy AI, director logic and economy are simulatable. Bots can play missions at scale.
**Why not higher:** networking, friend-feel and art direction need live tests and human taste.

### Starter feature list (P0 vertical slice: 4-player mission vs AI, bots fill empty slots)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | 3 classes or loadouts with unique abilities (gameplay) | Each class wins a role test. No class is mandatory in 100 sims |
| 2 | Enemy roster of 6 with distinct roles (gameplay) | Role mix per wave meets §0.4 |
| 3 | AI director (gameplay) | Stress thresholds trigger pause and spawn changes as specified |
| 4 | Wave budget and scaling by player count (gameplay) | Budget formula implemented. Unit-tested for 1–4 players |
| 5 | Revive and downed (gameplay) | Revive time and health per the table. Cannot revive under fire if configured |
| 6 | Mission with 3 objectives and an extract (content) | Bots complete within the time band. Objectives cannot soft-lock |
| 7 | AI teammates (gameplay) | Bots follow, revive and use abilities. Do not block doors |
| 8 | Co-op networking, 4 players (tech) | Clients stay in sync at 60 ms RTT and 2% loss. Host migration or clear failure message |
| 9 | Loadout unlocks with currency (meta) | Costs follow the table. Persistence verified |
| 10 | Difficulty tiers (progression) | Tiers scale enemy count, HP and accuracy. Clear rate in band per tier |
| 11 | Friend invite and join in progress (ux) | A joining player receives correct state |

### Platform notes
- **PC.** Dedicated servers or peer hosting. Mod and workshop support extend life. Steam friends and invites (`pc-web-release`).
- **Console.** Crossplay, party systems, platform invites and certification (`console-pathway`). Split-screen is a selling point on console.
- **Web.** Small co-op browser games are possible with lobby-based networking.
- **Mobile.** Smaller squad co-op exists. See `action-arcade-roguelite.md` for casual shooters.
- **Business.** Premium plus cosmetics is typical. Community goodwill is an asset.

## 7. Twin-stick / top-down shooter

### Definition and player fantasy
The player moves with one stick (or keys) and aims with another (or the mouse). Top-down or isometric view, waves of enemies and a stream of upgrades. The fantasy is *tight control in chaos*: weaving through bullets while the screen fills. `skills/genre-playbooks/references/action-arcade-roguelite.md` §8 covers mobile top-down shooters and shmups. This section adds PC and console depth.

### Core loop
```
move and aim → shoot and dodge → collect drops → pick an upgrade
  → clear the wave or room → boss → next area or run end → meta unlocks
```

### Meta loops
- **Roguelite runs.** Procedural rooms, build variety, permanent unlocks.
- **Weapon and character unlocks.** New starting kits.
- **Score and daily challenge.** Leaderboards, seeds.
- **Co-op.** Local or online two- to four-player.
- **Mutators and challenge modes.**

### Session profile
Estimate: 2–15 minute runs for arcade style, 20–45 minutes for roguelite runs. Short enough to retry quickly.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Dual-stick movement and aim | combat | Aim and move are independent. Mouse variant uses cursor aim |
| Bullet patterns and dodging | combat | Telegraph and spacing (`action-arcade-roguelite.md` §8) |
| Weapon and upgrade synergy | progression & upgrade | Build variety drives replay |
| Room or wave structure | exploration & traversal | Generated rooms or fixed arenas |
| Drops and economy | economy & resources | Pickups feed upgrades and ammo |
| Dash or dodge with i-frames | combat | Gives a skill ceiling. Tune i-frame length in frames |
| Boss patterns | combat | Phased with readable telegraphs |

```
Dodge window   i-frames 12 at 60 fps = 0.20 s;  cooldown 1.0 s → vulnerable 80% of the time
Bullet density D = bullets on screen / playfield area. Tune so a safe path always exists:
  gap width ≥ player hitbox width + 2 × reaction distance (speed · 0.2 s)
  Example: speed 6 u/s, hitbox 0.5 u → gap ≥ 0.5 + 2 · 1.2 = 2.9 u
```

### Monetisation model and typical mix
Premium (PC and console) with cosmetic DLC is typical. Mobile versions use ads and IAP (see `action-arcade-roguelite.md`). Early access is common on PC. Free demos drive wishlists.

### KPI expectations
Qualitative. Run completion rate, deaths by room and by boss, number of builds used, daily challenge participation and leaderboard activity. Use the difficulty bands in `progression-difficulty`.

### Retention drivers
Build discovery, mastery, unlocks, daily seeds, co-op and short retries.

### Content pipeline and production scope (estimates)
Rooms (generated from hand-made pieces), enemy and boss patterns, weapons and upgrades (data-driven), 2D art and effects. Rough estimate: 1–6 people over 1–2.5 years for a small title.

### Reference titles
- *Robotron: 2084* (Williams, 1982): the twin-stick origin.
- *Geometry Wars* (Bizarre Creations, 2003).
- *The Binding of Isaac* (Edmund McMillen, 2011): roguelite twin-stick.
- *Enter the Gungeon* (Dodge Roll, 2016).

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Responsive input and fair hit-boxes | Input lag or unfair deaths |
| Build synergy and variety | One dominant build |
| Readable bullets and telegraphs | Visual noise hides danger |
| Fast retry | Slow loading between runs |
| Strong feel (screen shake, sound) | Weak feedback |

### Innovation vectors

### Agent-buildability: 5/5
**Why high:** 2D simulation, deterministic seeds, data-driven content, bot playthroughs, visible metrics and cheap assets.
**What needs humans:** feel, boss telegraphs and visual readability.

### Starter feature list (P0 vertical slice: 5 rooms, 1 boss, 8 upgrades)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Twin-stick controller with mouse variant (gameplay) | Aim angle error under 1° at rest. Stick curve per §0.3 |
| 2 | Dash with i-frames (gameplay) | i-frame count and cooldown match the table |
| 3 | 4 weapons with distinct patterns (gameplay) | DPS per weapon within 10% of target in a sim |
| 4 | 6 enemy types with telegraphs (gameplay) | Telegraph lasts at least 0.3 s |
| 5 | Room generator from 20 hand-made pieces (level) | 1,000 seeds all solvable and within budget |
| 6 | 8 upgrades with synergies (progression) | No upgrade pair breaks a damage cap in a sim |
| 7 | Boss with 3 phases (gameplay) | Bot clears within the target win-rate band |
| 8 | Run and meta save (tech) | State survives an app kill. Seed reproduces the run |
| 9 | Hit feedback and screen shake with a reduce-motion toggle (feel) | Toggle disables shake. Hit sound within one frame |
| 10 | Daily seed with leaderboard (meta) | The same seed gives the same layout on two machines |

### Platform notes
- **PC.** Mouse aim is precise. Local co-op with shared keyboard and gamepads. Steam leaderboards and workshop are easy to add.
- **Console.** Gamepad is native. Couch co-op is a strength. Performance targets are easy at 60 fps.
- **Web.** An excellent fit. Small download, instant start, keyboard and mouse. Web portals and itch.io (`pc-web-release`).
- **Mobile.** Dual virtual sticks have known problems (thumb occlusion, imprecision). Prefer auto-aim. See `action-arcade-roguelite.md` §6 and §8.
- **Business.** Cheap to build, crowded to sell. Hook, demo and streamer-friendliness drive discovery.

## Volatile facts (as of Oct 2026 — verify before relying)

- ARC Raiders (Embark Studios, Nexon) was reported by Nexon at about 960,000 peak concurrent players across platforms in January 2026 and about 6 million weekly active users sustained. Sales passed 12.4 million in about ten weeks and later reports cite 14 million (February 2026) and over 16 million (July 2026). The Steam peak was about 481,000 at launch, and the player count was reported as declining by July 2026. These are Nexon disclosures, not independently verified — [Push Square](https://www.pushsquare.com/news/2026/01/arc-raiders-now-a-huge-multiplayer-success-story-at-12-million-sales), [GamesMarket](https://www.gamesmarket.global/arc-raiders-sold-14-million-units-to-date/)
- Battlefield 6: EA said it sold over 7 million copies in its first three days (October 2025). An analyst estimate put Steam at about 57% of early sales, PS5 about 24%, Xbox about 20%, which suggests PC is a large share for a premium shooter — [GOSU Gamers](https://www.gosugamers.net/entertainment/news/77481-battlefield-6-flies-past-seven-million-sales-ea-calls-it-a-record-shattering-launch), [3DTested (Alinea Analytics)](https://www.3dtested.com/video-games/more-than-half-of-battlefield-6-sales-are-from-steam-claim-analysts-blockbuster-shooter-sells-6-5m-units-generating-an-estimated-usd350-million-in-revenue)
- Marathon (Bungie) was scheduled for 5 March 2026 on PC, PS5 and Xbox Series at $39.99 (standard). Post-launch player counts and reception were not verified for this file — [Video Games Chronicle](https://www.videogameschronicle.com/news/bungie-finally-confirms-a-marathon-release-date-and-40-price-point)
- Steam Deck Verified requires the default controller configuration to reach all content, on-screen glyphs that match Deck or Xbox buttons, and a controller-usable text entry method. Criteria may change: check Valve's page — [Steamworks docs](https://partner.steamgames.com/doc/steamdeck/compat)
- Steam's revenue share has been reported as 30% up to $10M, 25% from $10M to $50M and 20% above $50M per game (introduced October 2018). Confirm the current terms and fees in Steamworks before planning — [Fortune](https://fortune.com/2018/12/01/steam-valve-developer-revenue-agreement)
- Unity deprecated Multiplay Game Server Hosting on Apr 1, 2026. Matchmaker, Relay and Lobby continue with third-party hosts — [Unity status](https://status.unity.com/info_notices/362941)
- Loot-box regimes (Belgium, Brazil under-18 ban from March 2026, Australia M/R18+) apply to random cosmetic packs in any shooter here. Details are in `skills/genre-playbooks/references/rpg-gacha.md` volatile facts.
- Anti-cheat, ratings and netcode facts are in `skills/genre-playbooks/references/competitive-pvp.md` volatile facts.

## Related skills
- `game-feel`: recoil, hit feedback, screen shake, input latency.
- `level-design`: encounter spaces, arenas, flow, solver gates.
- `progression-difficulty`: difficulty curves, DDA, win-rate bands.
- `multiplayer-backend`: authoritative servers, lag compensation, matchmaking.
- `balance`: TTK matrices, weapon tuning, bot sims.
- `economy-design`: extraction economies, loot tables, sinks.
- `platform-targets`: input devices, performance tiers and settings per platform.
- `pc-web-release`: Steam, itch.io, demos and wishlists.
- `console-pathway`: console programmes, certification, ratings.
- `accessibility-localization`: aim, toggle and motion options.
- `qa-testing`: bot squads, replay tests, latency tests.
- `legal-ethics`: loot boxes, chat safety, minors in online play.
- `game-architecture`: sim-core, determinism, replays.

