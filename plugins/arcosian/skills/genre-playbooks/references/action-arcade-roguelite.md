# Action, Arcade and Roguelite Playbooks

Real-time action games sell excitement, mastery and a power fantasy in short runs. On phones, the design problem is input: touch has no tactile feedback and the thumb hides part of the screen. Every genre in this file solves that through control choices: auto-run, auto-fire, one-axis swipes, drag-to-aim or a floating stick. Action games are also where agent pipelines are weakest. Black-box AI testers say fast, timing-critical gameplay is "not fully supported yet", and VLMs playing real-time games from raw frames made under 1% progress [V1][V2]. This file therefore pairs each playbook with a verification strategy: a deterministic simulation core, input record and replay, and scripted bots. This file covers eight playbooks in the 14-part format from `SKILL.md`: endless runner, arcade, platformer, survivor-like/bullet heaven, roguelite action, casual shooter, archery and top-down shooter. Sourced facts are tagged `[Vn]` and listed at the end. Team and time figures are labelled estimates.

## Contents

| # | Playbook | AB (1–5) | Orientation | Lead monetization |
|---|---|---|---|---|
| 0 | Shared action conventions: controls, feel, verification | — | — | — |
| 1 | Endless runner | 3 | Portrait | Ads + IAP |
| 2 | Arcade (score attack) | 4 | Portrait | Ads / premium |
| 3 | Platformer | 2 | Landscape (portrait for auto-run) | Premium / ads |
| 4 | Survivor-like / bullet heaven | 3 | Either | Premium or IAP + rewarded |
| 5 | Roguelite action | 2 | Landscape (portrait for auto-aim) | Premium or IAP |
| 6 | Casual shooter | 3 | Portrait | Ads + IAP |
| 7 | Archery | 4 | Either | IAP + ads |
| 8 | Top-down shooter / shmup | 3 | Portrait | IAP / premium |
| 9 | Volatile facts used in this file | — | — | — |

## 0. Shared action conventions: controls, feel, verification

**Touch control schemes**, from most forgiving to least.

| Scheme | Inputs | Best for | Notes |
|---|---|---|---|
| One-tap | Tap or hold | Arcade, stack, flap | Lowest barrier; skill comes from timing |
| Swipe lanes | 4-direction swipe | Endless runner | Discrete lanes forgive imprecision |
| Drag-relative | The object moves by the finger's delta | Shmups, io | Offset the ship above the finger; never centre it under the thumb |
| Drag-to-aim, release | Pull back, preview, release | Archery, shooters, slingshot | The aim preview length is a difficulty lever |
| Floating joystick | It appears where the thumb lands | Survivor-like, roguelite, arcade idle | Use a dead zone and clamp the radius |
| Virtual buttons | D-pad and jump buttons | Platformers | The hardest on touch; add auto-run or large zones |

**Feel parameters** (`game-feel`):
- Coyote time: allow a jump for about 0.1 s after leaving a ledge.
- Jump buffer: remember a jump press made shortly before landing.
- Forgive hitboxes: player hurtbox smaller than the sprite, pickups larger.
- Hit-stop on impacts (tens of ms) and screen shake capped by an accessibility setting.
- Input-to-response latency measured on low-end Android. Frame pacing matters: at 30 fps a late frame costs an extra 33 ms [V4].

**Verification strategy** (doctrine 3: verify by playing):
1. A simulation core on a fixed timestep with seeded RNG, separate from presentation, so runs are reproducible headlessly (`game-architecture`).
2. Input record and replay. A human or bot input log replays to an identical end state, which is the deterministic playthrough gate.
3. Scripted policy bots (greedy dodge, kite, lookahead) with tunable reaction delay and noise. Run hundreds of seeds to estimate clear rates and difficulty spikes.
4. RL agents are optional for complex balance. Unity ML-Agents is maintained [V5], but bots that call game logic directly are cheaper.
5. Device performance and soak tests. Many-entity scenes degrade with heat; frame rates often drop after 45–50 minutes [V3].
6. Human feel checkpoint. No automated gate replaces "does this feel good"; record it as a taste checkpoint.

## 1. Endless runner

**Definition and player fantasy.** Run forward forever through a procedurally assembled track. Swipe between three lanes, jump and slide to avoid obstacles while collecting coins and power-ups, and chase a high score until you crash. The fantasy is escape and speed: the thrill of near misses, outrunning the chaser, and a flow state.

**Core loop** (seconds). Run → read upcoming obstacles → swipe (lane, jump, roll) → collect coins and power-ups → speed rises → crash → revive offer → score and coins → spend → run again.

**Meta loops.**
- Characters and boards (each with perks) and power-up upgrades (longer magnet, more jetpack time).
- Mission sets that raise a score multiplier, giving a reason to vary play.
- Seasonal world tours (city themes), collections, events and a season pass.

**Session profile** (estimate). Runs of 1–4 minutes; sessions of 2–6 minutes; many a day.

**Signature mechanics** (`mechanics-codex`: movement-dodging, timing, collection, progression-unlocks).
- **Chunk-based track generation.** A library of authored chunks, each with a difficulty cost. A seeded selector fills a difficulty budget that grows with distance, so the generator is varied but every chunk is human-designed.
- **Reaction window.** For an obstacle first readable at distance d at speed v, the reaction time is t = d / v. Keep t at or above a tuned minimum (swipe reaction plus animation time) at all speeds, and raise view distance or cap speed to protect it.
- Power-ups as relief valves (magnet, jetpack, multiplier, shield). Near-miss feedback.

| Parameter | Starting value to tune (heuristic) | Effect |
|---|---|---|
| Start speed / ramp | Gentle start, logarithmic ramp to a cap | Run length |
| Minimum reaction window | Tuned from playtests; start around half a second | Fairness at top speed |
| Chunk difficulty budget | Grows with distance; occasional relief chunks | Sawtooth tension |
| Revive cost | Escalates per revive in a run | Monetization vs frustration |
| Coin density | High enough to pull players across lanes | Movement variety |

**Monetization model and typical mix.**
- Rewarded ads: revive, double coins, free boxes.
- IAP: characters, boards, revive tokens, a season pass, starter bundles.
- Interstitials light and capped.

**KPI expectations.** No sourced runner-specific range. A 2026 summary describes arcade titles as posting strong D1 but fading fast [V6]. Runners need meta and seasonal content to counter that (qualitative).

**Retention drivers.**
- High-score chasing and friend leaderboards.
- Mission multipliers.
- Seasonal world tours with new themes and characters.
- Collection.
- Pass.

**Content pipeline and production scope** (estimates).
- Per season: a new city theme (environment kit, chunk variants), characters and boards with run, jump and roll animations, and event rules.
- 3D low-poly art with animation is the main cost.
- Slice: 2–3 people plus agents, 6–10 weeks. Soft launch: 8–20 people, 9–15 months.

**Reference titles.** Subway Surfers (SYBO), Temple Run (Imangi Studios), Jetpack Joyride (Halfbrick), Minion Rush (Gameloft), Sonic Dash (SEGA).

**What makes it succeed / fail.**
- Succeeds: instantly readable obstacles at speed, buttery swipes, iconic characters and fresh seasonal themes.
- Succeeds: fair speed caps.
- Fails: unfair deaths when an obstacle appears too late, and swipe misreads.
- Fails: monotonous chunks, and power-ups that trivialize runs.

**Innovation vectors.**
- IP and character crossovers.
- Async ghost races and team events.
- Narrative world tours.
- Hybrid metas (base building, collections).
- Rhythm-synced tracks.

**Agent-buildability: 3/5.** Track generation and collision are deterministic on a fixed timestep. A lookahead bot with a reaction-delay model estimates survival distance per seed, and chunk libraries can be validated (every chunk passable at max speed). Points are lost for real-time feel, 3D character animation and seasonal art volume.

**Starter feature list (P0 vertical slice).**
1. Lane runner core — 3 lanes; swipe left and right, jump and roll; inputs buffered for a short window (tested with injected swipes).
2. Fixed-timestep sim — the same seed and input log give an identical run end state (replay test).
3. Chunk library — 20 authored chunks with difficulty costs; each passable at max speed (bot verification).
4. Seeded selector — fills the difficulty budget by distance and inserts relief chunks.
5. Speed ramp and reaction guard — the reaction window never drops below the configured minimum (asserted in sim).
6. Collision and crash — forgiving hurtbox; crash animation; run end.
7. Coins and two power-ups — magnet and shield with durations from upgrade data.
8. Revive — rewarded or token revive with escalating cost; never more than N per run.
9. Missions — 3 active missions; completing a set raises the score multiplier.
10. Character and upgrade shop — 2 characters and 2 upgrade tracks; persistent.
11. Perf — p95 frame time within budget on the low tier at top speed; a 30-minute soak with thermal logging.
12. Analytics — `run_end` (distance, score, cause, revives, power-ups) and `mission_complete`.

## 2. Arcade (score attack)

**Definition and player fantasy.** Short, skill-based runs around one elegant mechanic, with escalating difficulty and a high score. You die fast and restart instantly: flapping through pipes, hopping across roads, smashing glass on rails, falling down a well. The fantasy is pure mastery and "one more go": proving you can get further.

**Core loop** (seconds). Start instantly → apply the single verb under escalating pressure → die → see score versus best → restart in under a second.

**Meta loops.**
- High scores, friend leaderboards and daily challenges.
- Character or skin collection; Crossy Road made character collection the monetization hook.
- Unlockable modes and achievements.

**Session profile** (estimate). Runs of 10 seconds to 3 minutes; sessions of 1–5 minutes; many a day.

**Signature mechanics** (`mechanics-codex`: timing, movement-dodging, aiming-trajectory).
- One verb with deep timing nuance. The design is about subtraction.
- Escalation: speed, density or pattern complexity grows with score. Use stepped plateaus so players learn each phase.
- Instant restart and death clarity: the player must see what killed them.

| Parameter | Starting value to tune (heuristic) | Effect |
|---|---|---|
| First-death time for novices | Short but not instant | First-session hook |
| Escalation steps | Every N points, plateau then step | Learnable mastery curve |
| Restart latency | Under 1 s | Retry loop survival |
| Collision forgiveness | Hurtbox smaller than the sprite | Perceived fairness |
| Score feedback | Milestone sounds and colour shifts | Progress feel |

**Monetization model and typical mix.**
- Ads: an interstitial every N deaths and a rewarded continue.
- No-ads and character packs as IAP.
- Some arcade titles are premium.

**KPI expectations.** A 2026 summary describes arcade as strong at D1 but fading fast [V6]. That is qualitative, with no numbers given.

**Retention drivers.**
- Personal best.
- Friend rivalry.
- Daily challenges.
- Collection.
- Mastery plateaus that feel conquerable.

**Content pipeline and production scope** (estimates).
- Content is mostly procedural and systemic. Art is a strong, minimal style.
- Audio and juice carry the experience.
- Slice: 1 person plus agents, 1–3 weeks. Soft launch: 1–4 people, 1–4 months.

**Reference titles.** Flappy Bird (Dong Nguyen), Crossy Road (Hipster Whale), Smash Hit (Mediocre), Downwell (Moppin), Geometry Dash (RobTop Games, also a rhythm platformer).

**What makes it succeed / fail.**
- Succeeds: a crisp, novel verb, a distinctive art style and fair deaths.
- Succeeds: an instant retry, and an ad-readable concept.
- Fails: deaths that feel cheap, input lag, and too little depth after the first minutes.
- Fails: aggressive interstitials.

**Innovation vectors.**
- Roguelite layers on arcade cores (Downwell).
- Daily seeded runs shared by everyone.
- Async ghost multiplayer.
- Rhythm sync.

**Agent-buildability: 4/5.** It is small, deterministic and easy to replay-test. A noisy-timing bot estimates the score distribution per skill level, and the art scope is small. A point is lost because the whole value is feel and timing [V1], which needs human checkpoints.

**Starter feature list (P0 vertical slice).**
1. Core verb — a single input with documented timing windows; unit-tested physics or timing function.
2. Fixed-timestep sim and replay — input logs reproduce scores exactly.
3. Escalation — stepped difficulty by score from config.
4. Death and restart — a death reveal of about 0.5 s showing the cause; restart under 1 s.
5. Score and best — persisted; a "new best" celebration.
6. Skill bot — 1,000 runs at three noise levels give a monotonic score-versus-skill curve with no early wall.
7. Juice — milestone sounds, particles and haptics; screen shake toggle in settings.
8. Collectible characters — 6 cosmetic characters unlocked by coins or score.
9. Daily challenge — a seeded daily run with its own leaderboard stub.
10. Interstitial policy — every N deaths after the first session; rewarded continue once per run.
11. Latency check — tap-to-response within target on the low tier.
12. Analytics — `run_end` (score, duration, cause) and `continue_used`.

## 3. Platformer

**Definition and player fantasy.** Traverse handcrafted levels by running and jumping across gaps, hazards and enemies to reach a goal, often collecting secrets on the way. On mobile it usually takes the form of auto-runners (the game runs, you jump), one-touch designs, or careful virtual-button layouts. The fantasy is mastery of movement and skilful traversal through charming worlds.

**Core loop** (seconds). Move and jump → avoid hazards and enemies → collect coins and secrets → checkpoint → reach the goal → level results → next.

**Meta loops.**
- World maps with collectible gates (for example three special coins per level).
- Characters and abilities, and time trials.
- Level editors and UGC (Geometry Dash's community levels are a major retention engine).

**Session profile** (estimate). Levels of 1–5 minutes; sessions of 5–20 minutes; landscape is typical.

**Signature mechanics** (`mechanics-codex`: movement-dodging, timing, physics, progression-unlocks).
- Jump arcs with variable height (hold to jump higher), coyote time and jump buffering. These are mandatory on touch.
- Auto-run removes the horizontal input entirely and turns platforming into rhythm and timing (Super Mario Run).
- Checkpoints and generous respawn: the cost of death must be small on mobile.

| Parameter | Starting value to tune (heuristic) | Effect |
|---|---|---|
| Coyote time | About 0.1 s | Forgives late jumps |
| Jump buffer | About 0.1 s | Forgives early jumps |
| Button zones | Large, half-screen zones | Touch reliability |
| Checkpoint spacing | Every 20–40 s of play | Death cost |
| Level length | 1–3 min | Session fit |

**Monetization model and typical mix.**
- Premium or a "free to start, pay to unlock the full game" model (Super Mario Run).
- Alternatively ads and IAP for characters, cosmetics and level packs.

**KPI expectations.** No sourced range. Qualitatively, premium platformers are judged on conversion and reviews, not retention curves.

**Retention drivers.**
- Level variety and secrets.
- Collectible completion.
- Time trials.
- UGC levels where present.

**Content pipeline and production scope** (estimates).
- Levels are handcrafted and taste-driven, and they are the main cost. Tilesets, character animation sets and enemy behaviours come next.
- Verify completability with an input-search bot (A* or BFS over discretized inputs on the deterministic sim) to prove each level can be finished and to find unintended skips.
- Slice: 2–3 people plus agents, 6–10 weeks. Soft launch: 4–12 people, 9–18 months.

**Reference titles.** Super Mario Run (Nintendo), Leo's Fortune (1337 & Senri), Alto's Odyssey (Snowman; endless-runner crossover), Geometry Dash (RobTop Games), Dadish (Thomas K. Young).

**What makes it succeed / fail.**
- Succeeds: controls designed for touch rather than ported, tight forgiving feel, and charming characters.
- Succeeds: short levels with frequent checkpoints, and clever level ideas.
- Fails: virtual D-pads with no forgiveness, long levels without checkpoints, and imprecise collisions.
- Fails: content that runs out quickly.

**Innovation vectors.**
- One-touch and auto-run designs.
- Rhythm platformers.
- UGC with verification bots.
- Roguelite platformers with procedural rooms.
- Physics-based movement verbs (swing, grapple).

**Agent-buildability: 2/5.** The deterministic sim allows replay and input-search verification of completability. Points are lost for precise real-time input (factor T), level design that depends on taste, and feel tuning. Agents are weakest at fast timing-critical play [V1][V2].

**Starter feature list (P0 vertical slice).**
1. Character controller — run, variable jump, coyote time and jump buffer, all from config; unit-tested arcs.
2. Touch controls — two large zones (move or auto-run, jump); no missed inputs in a scripted 10-input/s test.
3. Tilemap levels — 5 levels in data; collision layers; one-way platforms.
4. Hazards and enemies — spikes and one patrolling enemy (stomp to defeat).
5. Checkpoints and respawn — respawn under 1 s at the last checkpoint.
6. Collectibles — 3 special coins per level; results screen shows them.
7. Input replay — a recorded completion replays to the same goal time (determinism gate).
8. Completability bot — input search proves each level finishable; flags unintended skips.
9. Camera — lookahead in the movement direction; no hazard off-screen when it becomes relevant.
10. Feel pass — squash and stretch, landing dust and jump SFX; human feel checkpoint signed.
11. Perf — 60 fps on the mid tier; 30 fps floor on the low tier.
12. Analytics — `level_end` (time, deaths, collectibles) and `death` (position, cause).

## 4. Survivor-like / bullet heaven

**Definition and player fantasy.** You control only movement. Weapons fire automatically. Hordes swarm in growing numbers, and XP from kills lets you pick upgrades that build a synergistic arsenal over a 15–30 minute run, until the screen fills with your own destruction. Unlocks between runs expand the pool. This playbook covers the deeper, often premium form. The F2P chapter-and-gear form is in `hyper-hybrid-casual.md` (playbook 9). The fantasy is going from fragile to god-like: a power fantasy built through clever build-crafting.

**Core loop** (seconds to minutes). Move → weapons auto-fire → kill → collect XP → level up → choose upgrades (weapon, passive, evolution) → survive escalating waves and elites → survive the timer or die → unlocks and meta currency.

**Meta loops.**
- Unlocks: characters, weapons and stages unlocked by achievements. Discovery is the long-term content.
- Permanent power upgrades bought with meta currency.
- Some designs use wave-based shops between waves (Brotato) instead of level-up choices.

**Session profile** (estimate). Runs of 15–30 minutes in the premium form; mobile players often prefer shorter modes. Sessions match run length.

**Signature mechanics** (`mechanics-codex`: auto-combat, build-crafting, movement-dodging, randomness-loot, collection).
- Auto-weapons with cooldown, area, projectile count and duration stats that passives multiply. Synergy math is the depth.
- Evolutions: a max-level weapon plus a specific passive triggers a transformed weapon. They are discovered goals.
- Escalating enemy waves with swarm, elite and boss mixes; screen-filling density as spectacle.

| Parameter | Starting value to tune (heuristic) | Effect |
|---|---|---|
| Run length | 15–30 min (premium), shorter mobile modes | Session fit |
| Weapon / passive slots | About 6 each | Build depth |
| XP curve | Fast early, slowing; level-ups every few seconds early | Power pacing |
| Enemy cap | Per device tier with pooling | Frame time |
| Choice count | 3–4 per level-up, plus reroll, skip or banish tools | Agency |

**Monetization model and typical mix.**
- Premium (low price, often with paid DLC) on mobile is proven by the genre's origin.
- Or F2P with rewarded ads (revive, double rewards) and cosmetic or character IAP.
- Paid random gear moves it towards the hybrid pattern; apply loot-box rules [V7].

**KPI expectations.** No sourced range. Qualitatively, premium titles succeed through word of mouth and reviews; F2P versions are measured like hybrid-casual.

**Retention drivers.**
- Unlock discovery.
- Build experimentation.
- Evolutions to find.
- Achievement lists.
- New stages and characters in updates.

**Content pipeline and production scope** (estimates).
- Weapons, passives, enemies and stages are the content. Each weapon needs VFX and balance.
- The run is headless-simulable with a kiting bot that applies an upgrade-choice policy. Simulate build win rates to detect dominant builds and dead upgrades.
- Slice: 1–3 people plus agents, 4–8 weeks. Soft launch: 3–10 people, 6–12 months.

**Reference titles.** Vampire Survivors (poncle), Brotato (Blobfish), 20 Minutes Till Dawn (flanne), Magic Survival, with Survivor!.io (Habby) as the F2P adaptation.

**What makes it succeed / fail.**
- Succeeds: escalating spectacle, discoverable synergies and readable danger amid chaos.
- Succeeds: a steady unlock drip, and a stable frame rate at peak density.
- Fails: unreadable enemy attacks under VFX, dominant builds, and frame drops at late-run density.
- Fails: unlocks that feel like grind.

**Innovation vectors.**
- New control twists (aiming, positioning puzzles).
- Co-op survival.
- Deckbuilding or dice hybrids.
- Theme and IP mashups.
- Shorter mobile-native run lengths with the same depth.

**Agent-buildability: 3/5.** The simulation is deterministic, bots can kite, and build-balance sweeps are straightforward. Points are lost for real-time readability judgment, many-entity performance work, VFX volume and feel.

**Starter feature list (P0 vertical slice).**
1. Movement — floating joystick (or keyboard for desktop testing); speed stat applied.
2. Auto-weapons — 4 weapons with cooldown, area, projectile and duration stats; DPS unit-tested.
3. Passives — 4 passives that multiply weapon stats (unit-tested formulas).
4. Evolution — 1 evolution recipe with a distinct transformed weapon.
5. Wave director — a 15-minute schedule of swarms, elites and a final boss from data; pooled enemies; per-tier cap.
6. XP and level-up choices — 3 random choices with reroll; the pause UI is readable on the smallest phone.
7. Unlock meta — 3 achievements unlock a new weapon or character; persistent.
8. Kiting-bot sim — 500 headless runs per build archetype; no build has a win rate above the dominance threshold.
9. Readability — enemy projectiles keep a contrast outline under all VFX (visual gate check).
10. Death, results and meta currency — summary of damage per weapon; currency awarded.
11. Perf — p95 frame time within budget at the enemy cap on the low tier; a 30-minute soak with thermal logging [V3].
12. Analytics — `run_end` (duration, level, build, cause, kills) and `unlock`.

## 5. Roguelite action

**Definition and player fantasy.** Fight through procedurally arranged rooms and floors with permanent death. Gather run-specific upgrades (weapons, boons, relics) that combine into builds, beat bosses, die, then spend meta currency on permanent unlocks and try again, stronger and wiser. Mobile forms run from twin-stick dungeon shooters to "move to dodge, stop to auto-shoot" designs and full premium ports. The fantasy is that every death teaches you something, and that you will eventually conquer this place.

**Core loop** (minutes). Enter a room → fight (dodge, attack, use skills) → clear → choose a reward (upgrade, currency, heal) → next room → boss → next floor, or die → meta currency → unlocks → new run.

**Meta loops.**
- Permanent upgrades (talent trees, a "mirror"), character and weapon unlocks, and narrative progress across deaths (Hades-style storytelling).
- Difficulty modifiers for mastery (heat or ascension systems).
- In F2P versions: gear, energy, events and a pass.

**Session profile** (estimate). Runs of 10–30 minutes, or chapter-based runs of 5–10 minutes on mobile F2P. Session length usually equals a run, so offer suspend and resume.

**Signature mechanics** (`mechanics-codex`: movement-dodging, build-crafting, randomness-loot, auto-combat, progression-unlocks).
- **Procedural floors.** A room graph (start, combat, reward, shop, elite, boss) from templates. Generate with BSP or graph grammars (`${CLAUDE_PLUGIN_ROOT}/scripts/pcg.py bsp|maze`, then validate connectivity).
- **Upgrade offers** drawn from pools with rarity and synergy tags. Pity rules prevent dead runs.
- **Combat readability.** Telegraphed enemy attacks, invulnerability frames on dodge, and hit-stop.
- **Control choice.** Twin-stick (two thumbs, landscape) or auto-aim (Archero: moving dodges, standing still shoots), which is better for portrait one-handed play.

| Parameter | Starting value to tune (heuristic) | Effect |
|---|---|---|
| Rooms per floor | 8–15 | Run length |
| Upgrade offers per room | 2–3 choices | Build agency |
| Meta power share | Small per unlock; skill dominates | Keeps runs meaningful |
| Dodge i-frames | A short window, generous on mobile | Touch fairness |
| Suspend and resume | Any room boundary | Mobile interruption safety |

**Monetization model and typical mix.**
- Premium ports sell at a one-time price, and some reach mobile through subscription services (Hades through Netflix).
- F2P versions use IAP for characters, skins and gear (gear chests count as paid random items; disclose odds [V7]) and rewarded ads for revives.

**KPI expectations.** No sourced range. Qualitatively, premium roguelites live on reviews and word of mouth; F2P ones are measured like hybrid-casual.

**Retention drivers.**
- "One more run" mastery.
- Build discovery.
- Narrative revealed across deaths.
- Unlocks.
- Difficulty ladders for experts.

**Content pipeline and production scope** (estimates).
- Enemies, bosses, weapons and upgrades with animation and VFX, plus room templates and biome tilesets.
- Balance by headless simulation: bots run seeded floors with build policies to find dominant builds, dead upgrades and spikes.
- Slice: 2–4 people plus agents, 8–12 weeks. Soft launch or premium release: 6–20 people, 12–24 months.

**Reference titles.** Soul Knight (ChillyRoom), Archero (Habby), Dead Cells (Motion Twin), Hades (Supergiant Games).

**What makes it succeed / fail.**
- Succeeds: tight combat feel on touch, telegraphed fair enemies and synergistic builds.
- Succeeds: meaningful meta between runs, and suspend and resume.
- Fails: touch controls ported from a gamepad, and runs that feel decided by bad offers.
- Fails: an unreadable bullet chaos, and 40-minute runs without a save.

**Innovation vectors.**
- Portrait one-thumb roguelites.
- Co-op runs.
- Deckbuilding and roguelite combat hybrids.
- Narrative roguelites.
- Daily seeded runs with shared leaderboards.

**Agent-buildability: 2/5.** Floors, rewards and combat can be simulated deterministically, and bots can sweep build balance. Points are lost for real-time combat feel and readability, animation and VFX volume, boss design taste, and touch-control tuning [V1].

**Starter feature list (P0 vertical slice).**
1. Controls — auto-aim scheme (moving dodges, standing still auto-fires) in portrait; a twin-stick option behind a flag.
2. Combat core — player HP, i-frame dodge and 2 weapon types; damage formula unit-tested.
3. Enemies — 4 archetypes (melee chaser, ranged, charger, summoner) with telegraphs of at least the minimum duration.
4. Room templates and floor graph — 1 biome, 10 room templates, generated floors with guaranteed connectivity (validator).
5. Rewards — choose 1 of 3 upgrades after each room from tagged pools; pity guarantees a weapon upgrade by room N.
6. Boss — 1 boss with 3 telegraphed patterns and a phase change.
7. Death and meta — meta currency on death; 4 permanent unlocks; persistent.
8. Suspend and resume — killing the app mid-run resumes at the last room boundary with an identical state.
9. Balance sim — 500 bot runs per build policy; no upgrade unpicked by every policy; floor clear rates within bands.
10. Readability gate — enemy attacks readable under VFX (visual review rubric).
11. Perf — 60 fps on the mid tier in the densest room; 30 fps floor on the low tier.
12. Analytics — `run_end` (floor, room, build, cause, duration), `upgrade_pick` and `unlock`.

## 6. Casual shooter

**Definition and player fantasy.** Aim-and-tap shooting in bite-size levels. Variants include sniper missions (pick the right target in a scene), slow-motion trick shots (time shots while the character flips) and ricochet puzzles (bank a bullet off walls to hit every enemy and spare the hostages). The fantasy is being a cool, precise marksman: action-movie moments without twitch demands.

**Core loop** (seconds). Survey the level → aim (drag) → shoot (release or tap) → the bullet resolves (slow-motion cam, ricochet path) → targets down or a fail (hostage hit, out of ammo) → coins → weapon upgrades or skins → next level.

**Meta loops.**
- Weapon collection and upgrades (damage, zoom, stability) in sniper variants.
- Skins and characters, level chapters and boss levels.
- Daily missions and events in deeper versions.

**Session profile** (estimate). Levels of 15–60 seconds; sessions of 2–8 minutes.

**Signature mechanics** (`mechanics-codex`: aiming-trajectory, timing, physics, deduction-constraint).
- **Aim assist and magnetism**, tuned per difficulty, so touch aiming feels accurate without being automatic.
- **Ricochet geometry.** Reflection r = d − 2(d·n)n. Analytic rays make the puzzles exactly solvable and verifiable.
- **Bullet time and kill cams** as the payoff moment. Keep them skippable after the first few.
- **Hostage and civilian rules** add decision weight.

| Parameter | Starting value to tune (heuristic) | Effect |
|---|---|---|
| Ammo per level | Minimum solution count plus slack | Puzzle tightness |
| Aim assist radius | Generous early, tighter later | Perceived skill |
| Slow-motion factor and window | Long enough to aim deliberately | Accessibility vs tension |
| Ricochet bounce limit | 1–4 | Solution complexity |
| Weapon upgrade effect | Visible, small steps | Meta value |

**Monetization model and typical mix.**
- Ads: interstitials between levels and rewarded skips, retries or coin multipliers.
- IAP: weapons and skins, no-ads.
- Sniper variants add energy or premium weapon systems.

**KPI expectations.** No sourced range; qualitatively, hypercasual-like for puzzle-shooters, with longer tails for sniper metas.

**Retention drivers.**
- Clever new level setups.
- Satisfying kill cams.
- Weapon progression.
- Boss levels.

**Content pipeline and production scope** (estimates).
- Levels: geometry, targets and hostages from data. Verify ricochet puzzles by enumerating shot angles (ray casting) to prove a solution exists within the ammo limit, and record the solution-angle measure as a difficulty proxy.
- Content rating: violence level affects age ratings and ad networks. Prefer stylized or cartoon violence for broad audiences (`store-release`, `legal-ethics`).
- Slice: 1–2 people plus agents, 2–5 weeks. Soft launch: 3–8 people, 3–9 months.

**Reference titles.** Hitman Sniper (Square Enix Montreal), Sniper 3D, Johnny Trigger (SayGames), ricochet-puzzle shooters.

**What makes it succeed / fail.**
- Succeeds: precise, assisted touch aiming, cinematic payoffs and puzzle-like levels with clever solutions.
- Succeeds: clear failure reasons.
- Fails: aiming that fights the thumb, and repetitive setups.
- Fails: violence beyond the target rating, and unskippable slow-motion.

**Innovation vectors.**
- Narrative mission chains.
- Physics-object interactions (explosive barrels, chain reactions).
- Async PvP score duels.
- Non-violent reskins (paint, foam) for younger ratings.

**Agent-buildability: 3/5.** Ricochet and trajectory math is analytic and solver-verifiable, and the levels are data. Points are lost for aiming feel, slow-motion cinematics and 3D scene assets in sniper variants. The puzzle variant alone scores 4.

**Starter feature list (P0 vertical slice).**
1. Aim input — drag to aim with a preview line (first bounce only); release to fire; aim assist from config.
2. Ray and ricochet solver — reflection math unit-tested; the bullet path matches the preview prefix.
3. Targets and hostages — hit detection; hitting a hostage fails the level immediately, with a clear reason.
4. Ammo and win rules — a win when all enemies are down within the ammo limit.
5. Slow-motion kill cam — plays on the final kill; skippable after the third time.
6. Level data — 20 levels in `level-spec` JSON (walls, targets, hostages, ammo).
7. Solver gate — angle enumeration proves each level solvable within its ammo limit and records the solution-angle measure.
8. Difficulty curve — the solution-angle measure decreases in a sawtooth across the 20 levels.
9. Coins and weapon skins — 4 skins; persistent.
10. Rewarded skip and retry — opt-in; capped.
11. Interstitial policy — after level N; minimum interval; never mid-aim.
12. Analytics — `level_end` (shots, result, fail reason, time).

## 7. Archery

**Definition and player fantasy.** Draw a bow, account for distance, gravity and wind, and release to hit targets or opponents. Formats include target competitions (scoring rings, often with PvP), turn-based duels (trade shots with a rival character), and hunting or puzzle shooting. The fantasy is calm precision under pressure: the perfect bullseye or the decisive headshot.

**Core loop** (seconds). Draw back (drag) → aim (preview arc partly visible) → read the wind → release → the arrow flies → score or damage → next shot or opponent's turn → match result → rewards → upgrades (bows, arrows) and cosmetics.

**Meta loops.**
- Equipment collection and upgrades (bow stability, arrow damage), characters with special shots (duel variants).
- Leagues and ranked PvP, tournaments, events and a pass.

**Session profile** (estimate). Matches of 1–4 minutes; sessions of 3–10 minutes.

**Signature mechanics** (`mechanics-codex`: aiming-trajectory, physics, competition, collection).
- **Projectile motion.** `y = x·tanθ − g·x² / (2·v²·cos²θ)`, plus wind as a horizontal acceleration. The trajectory is analytic, so outcomes are exactly reproducible and bots can compute ideal shots.
- **Aim preview length** (none, partial or full arc) is the main difficulty and upgrade lever.
- **Bow sway** adds a timing element; equipment stats reduce it.
- **Turn-based duels** remove real-time pressure. This is great for one-handed play and asynchronous PvP.

| Parameter | Starting value to tune (heuristic) | Effect |
|---|---|---|
| Preview arc fraction | Long early, short at high ranks | Skill ceiling |
| Wind range | None early; grows with league | Read-the-conditions depth |
| Sway amplitude | Reduced by gear | Meta value vs skill |
| Shot clock | 10–20 s | Pace and accessibility |
| Damage zones | Head / body / limb multipliers (duels) | Precision reward |

**Monetization model and typical mix.**
- IAP: bows, arrows, characters and skins, currency, and a pass.
- Ads: rewarded extra shots or chests; interstitials in more casual versions.
- Keep gear advantages small in PvP to avoid pay-to-win.

**KPI expectations.** No sourced range; qualitatively, PvP leagues drive the long tail.

**Retention drivers.**
- Ranked progression.
- Mastering wind.
- Rival duels.
- Equipment upgrades.
- Characters with personality (duels).

**Content pipeline and production scope** (estimates).
- Arenas or targets, bows and arrows as cosmetics and stat items, and characters with hit reactions (ragdolls in duels).
- An asynchronous or bot opponent with skill noise allows PvP-like play without real-time netcode. Label bots honestly.
- Slice: 1–2 people plus agents, 3–6 weeks. Soft launch: 3–10 people, 4–10 months.

**Reference titles.** Archery King (Miniclip), Bowmasters (Playgendary), stickman archer duel games.

**What makes it succeed / fail.**
- Succeeds: a satisfying draw and release, a readable trajectory and fair PvP matchmaking.
- Succeeds: funny or punchy hit reactions.
- Fails: pay-to-win gear in PvP, and unfair wind at low ranks.
- Fails: inconsistent physics, and opponents that feel scripted.

**Innovation vectors.**
- Archery with roguelite builds (special arrows as upgrades).
- Co-op boss hunts.
- AR target modes.
- Narrative duel tournaments.

**Agent-buildability: 4/5.** Trajectory physics is analytic and deterministic, so bots compute optimal shots with injected noise and give exact difficulty estimates per league. The art is modest and turn-based variants have high timing tolerance. A point is lost for the feel of the draw and release and for hit-reaction polish.

**Starter feature list (P0 vertical slice).**
1. Draw-and-release input — drag back to set power and angle; the release fires; cancel by dragging back to origin.
2. Trajectory model — analytic arc with wind; the simulated path matches the formula within tolerance (unit-tested).
3. Aim preview — a partial arc of configurable length.
4. Target scoring — rings 1–10 with an X bullseye; score per end of 3 arrows.
5. Bot opponent — computes the ideal shot plus skill noise; 5 skill tiers.
6. Match flow — alternating ends, a 3-round match, results and rewards.
7. Wind — a direction and strength indicator; per-match random within league bounds.
8. Bow sway — sinusoidal sway with amplitude from gear stats (tested).
9. League ladder — 3 leagues with wind and preview-length rules.
10. Gear — 3 bows with stat differences capped (max win-rate shift asserted by the bot sim).
11. Juice — string tension SFX, arrow whoosh, impact thud, slow-motion on a bullseye.
12. Analytics — `match_end` (league, score, opponent tier, result) and `gear_equip`.

## 8. Top-down shooter / shmup

**Definition and player fantasy.** Pilot a ship or hero through waves of enemies and bullet patterns, in vertical-scrolling shmups or top-down arena and stage shooters. On mobile, ships usually move by relative drag with auto-fire. Collect power-ups, dodge patterns and defeat bosses. The fantasy is threading through a storm of bullets, and a firepower fantasy that grows with every upgrade.

**Core loop** (seconds). Drag to move (auto-fire) → destroy waves → collect power-ups and currency → dodge patterns → boss → stage clear → upgrade the ship or weapons → next stage.

**Meta loops.**
- Ship and weapon upgrades with tiers, collection of ships, wingmen or drones.
- Stage medals and challenge modes (no-hit, speed), difficulty tiers.
- In F2P versions: energy, events and a pass.

**Session profile** (estimate). Stages of 2–5 minutes; sessions of 5–15 minutes; portrait for vertical shmups.

**Signature mechanics** (`mechanics-codex`: movement-dodging, aiming-trajectory, build-crafting, progression-unlocks).
- **Relative drag.** The ship moves by the finger's delta, rendered above the finger. The ship's real hitbox is tiny, which makes bullet-dense patterns fair.
- **Authored bullet patterns** as scripts (spiral, aimed, spread, wall with gap), parameterized by speed, density and gap width. Deterministic per seed.
- **Weapon tiers and power-up drops** that visibly grow firepower; bombs as panic buttons.
- **Grazing** (near misses) as an optional score-risk mechanic for experts.

| Parameter | Starting value to tune (heuristic) | Effect |
|---|---|---|
| Player hitbox | A few px core, shown on demand | Fairness in dense patterns |
| Bullet speed / density | Ramps per stage and difficulty | Core challenge |
| Minimum gap width | At least hitbox plus margin | Guarantees passable patterns |
| Weapon tier growth | Visible jump per tier | Upgrade satisfaction |
| Bombs per stage | 1–3 | Accessibility valve |

**Monetization model and typical mix.**
- Premium shmups sell at a one-time price, sometimes with a free-to-try first stages model.
- F2P versions use IAP for ships, upgrades and energy, a pass, and rewarded revives.
- Avoid pay-to-win in any competitive mode.

**KPI expectations.** No sourced range. Qualitatively, a niche, mastery-driven audience in premium; F2P ones depend on upgrade-meta pacing.

**Retention drivers.**
- Medal completion and challenge modes.
- Ship collection.
- Bosses.
- Upgrade progress.
- Difficulty tiers for mastery.

**Content pipeline and production scope** (estimates).
- Stages are wave scripts plus pattern scripts and bosses; ships, enemies and bullet VFX.
- **Verification.**
  - Pattern validity: a geometric check that every pattern frame leaves a passable gap of at least the minimum width, so no impossible walls.
  - Clear rates: a dodging bot (potential-field or lookahead search on the deterministic sim) estimates clear rates per upgrade tier.
- Slice: 2–3 people plus agents, 5–8 weeks. Soft launch: 4–12 people, 6–14 months.

**Reference titles.** Sky Force Reloaded (Infinite Dreams), F2P galaxy-shooter titles, Soul Knight (ChillyRoom; the top-down roguelite crossover), with Brawl Stars (Supercell) and Bullet Echo (ZeptoLab) as top-down PvP references (see `competitive-pvp.md`).

**What makes it succeed / fail.**
- Succeeds: relative-drag controls that feel precise, readable bullet colours against backgrounds and spectacular bosses.
- Succeeds: firepower growth you can feel.
- Fails: a thumb hiding the ship, and bullets that blend with backgrounds or VFX.
- Fails: impossible patterns, and upgrade walls requiring purchase.

**Innovation vectors.**
- Roguelite shmup runs with build choices.
- Co-op wingman modes.
- Rhythm-synced bullet patterns.
- Accessibility modes (bigger gaps, slowdown) that widen the audience.

**Agent-buildability: 3/5.** Patterns are deterministic and geometrically checkable for passability, and bots estimate clear rates. Points are lost for real-time dodge feel [V1], VFX and readability judgment, and boss design taste.

**Starter feature list (P0 vertical slice).**
1. Relative-drag movement — the ship follows the finger delta with an offset; clamped to safe bounds; no jump on touch-down.
2. Auto-fire and weapon tiers — 3 tiers with a visible change; DPS unit-tested.
3. Hitbox display — tiny core hitbox, shown while moving; collision uses the core only.
4. Pattern scripting — spiral, aimed, spread and gap-wall patterns from data, deterministic per seed.
5. Passability check — every pattern frame leaves a gap of at least the minimum width (geometric validator).
6. Wave director — 1 stage of 3 minutes with 8 waves and a boss.
7. Boss — 2 phases, 3 patterns, a health bar.
8. Power-ups and bomb — drops raise the weapon tier; a bomb clears bullets with i-frames.
9. Dodging-bot sim — 300 runs per upgrade tier; clear rate within target bands; no unclearable segment.
10. Readability — bullets keep an outline and contrast against all backgrounds (visual gate).
11. Perf — p95 within budget at peak bullet count on the low tier; bullets pooled.
12. Analytics — `stage_end` (result, hits taken, bombs, time, tier) and `death` (pattern id).

## 9. Volatile facts used in this file (as of Oct 2026 — verify before relying)

- [V1] modl.ai, a black-box AI QA service, states that very fast or timing-critical gameplay is "not fully supported yet". Source: [modl.ai](https://modl.ai).
- [V2] VideoGameBench (2025, revised May 2026): VLMs playing 1990s games from raw frames in real time reached under 1% average progress in the original results. Source: [arXiv:2505.18134](https://arxiv.org/html/2505.18134v3).
- [V3] Google's Android game optimization guide warns that frame rates often degrade after 45–50 minutes of play as devices heat up, and points to the Thermal API and ADPF for backing off workload. Source: [Android Developers](https://developer.android.com/games/optimize).
- [V4] The same guide notes that a late frame at 30 fps costs an extra 33 ms and recommends the Frame Pacing library. Source: [Android Developers](https://developer.android.com/games/optimize).
- [V5] Unity ML-Agents is maintained, not deprecated: release 4.0.3 (2026-04-17). Sources: [ML-Agents changelog](https://docs.unity3d.com/Packages/com.unity.ml-agents@4.0/changelog/CHANGELOG.html), [Unity Discussions](https://discussions.unity.com/t/is-ml-agents-being-deprecated/1643681/3).
- [V6] A 2026 summary describes arcade as posting strong D1 but fading fast. It is qualitative, with no numbers. Source: [Playio](https://blog.playio.co/d1-d7-d30-retention-benchmarks-2026).
- [V7] Brazil banned loot-box sales to under-18s from March 2026. Source: [Sheep Esports](https://www.sheepesports.com/articles/brazil-court-orders-riot-games-to-pay-eur2-5m-over-league-of-legends-loot-boxes/en).
- All-genre retention anchors are in `SKILL.md`, Core model 9.
