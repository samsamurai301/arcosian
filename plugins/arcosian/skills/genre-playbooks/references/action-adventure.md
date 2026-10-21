# Action-Adventure Playbooks

Action-adventure is the broadest premium genre on PC and console: a character, a world, a combat or stealth system and a chain of obstacles that open as the player grows. This file holds five playbooks in the shared 14-part template, plus a 15th part, "Platform notes", for PC, console, web and mobile differences:

1. Zelda-like and open-world action-adventure
2. Character action (combo systems)
3. Soulslike
4. Immersive sim
5. Stealth

Five foundations come first because most playbooks rely on them: combat frame data (startup, active, recovery), stamina and poise, enemy telegraphs, gating and keys, and camera. Shooters, platformers and metroidvanias have their own files: `skills/genre-playbooks/references/shooters.md` for aim, TTK and hitscan, and `skills/genre-playbooks/references/platformer-metroidvania.md` for jump physics and ability-gating graphs. Mobile action and roguelite combat is in `skills/genre-playbooks/references/action-arcade-roguelite.md`. This file does not repeat them. The headline for an agent pipeline: combat systems, gating graphs and enemy behaviour are data and state machines, so they test well with bots and solvers. Camera, animation timing and level art need human taste. Single-room combat slices score 3–4/5. Whole open worlds score 1–2/5 because of content volume.

## Contents

| § | Playbook | Session profile (estimate) | Primary monetisation | Agent-buildability | First project for an agent pipeline? |
|---|---|---|---|---|---|
| 0 | [Shared foundations](#0-shared-foundations) | — | — | — | Read first |
| 1 | [Zelda-like / open-world](#1-zelda-like-and-open-world-action-adventure) | 40–120 min sittings, 15–60 h total | Premium, DLC; F2P gacha in China-led titles | 2/5 (Zelda-like dungeon slice: 3/5) | Yes, one dungeon plus hub |
| 2 | [Character action](#2-character-action-combo-systems) | 20–40 min missions, 8–15 h | Premium, DLC | 3/5 | Yes, one arena with combo tests |
| 3 | [Soulslike](#3-soulslike) | 45–120 min sittings, 30–80 h | Premium, DLC | 3/5 | Yes, one boss slice |
| 4 | [Immersive sim](#4-immersive-sim) | 60–180 min sittings, 15–40 h | Premium, DLC | 2/5 | One-level slice with a systems sandbox |
| 5 | [Stealth](#5-stealth) | 30–60 min missions, 8–20 h | Premium, DLC | 3/5 | Yes, one level with AI perception |
| — | [Volatile facts](#volatile-facts-as-of-oct-2026--verify-before-relying) | — | — | — | Check before quoting numbers |

## How to use these playbooks

- Copy the core loop into `contract.json → loops[]`. Set `meta.genre: "action_adventure"` and `meta.subgenre` to the playbook slug. Set `meta.platforms`, `meta.input` and `technical.multiplayer` (usually `none`).
- Turn the starter feature list into P0 `features.json` entries with `gs.py feature add`. Each acceptance criterion maps to `unit` or `playthrough` gate evidence (bots, replays, solvers on gating graphs).
- Mechanic category labels: combat, build-craft, collection & randomness, progression & upgrade, economy & resources, exploration & traversal, narrative, UX automation. Resolve them with `gs.py kb "<mechanic>" --skill mechanics-codex`.
- KPI statements are qualitative unless sourced. Premium action-adventure is judged on review scores, completion rate and word of mouth. Fit curves after a playtest.
- Decide the camera (§0.5) and the input set before building combat. They set frame-data and telegraph budgets.

## 0. Shared foundations

### 0.1 Combat frame data
Every action in a melee or ability system has three phases. Measure them in frames at a fixed rate (60 fps unless the contract says otherwise). One frame is 16.67 ms at 60 fps.

```
Startup    frames from input to first damaging frame (can be cancelled in some systems)
Active     frames in which the hitbox is live
Recovery   frames after the active window before the next action is allowed
Total      T = startup + active + recovery        Seconds = frames / 60
Worked example: light sword attack   startup 12 · active 3 · recovery 20 → 35 frames = 0.58 s
                heavy attack         startup 24 · active 4 · recovery 36 → 64 frames = 1.07 s
Frame advantage on block/hit   advantage = defender_stun − attacker_recovery_remaining
Punish window                  punish = enemy_recovery − player_startup
   Enemy swing recovery 40 frames, player light startup 12 → 28 frames of free punish (0.47 s)
```

- **Rule: commitment equals risk.** The longer the recovery, the more damage or reach the move needs. If a heavy move has recovery 36 and the enemy punish window is 28, the player must read the enemy: the move cannot be spammed.
- **Cancels.** Allow cancel windows (dodge cancels attack recovery, attack cancels dodge recovery) when you want fluid combat. Disallow them when you want weighty commitment. Record the choice in the contract.
- **Input buffering.** Queue the next input for about 6–10 frames (100–170 ms, estimate) before the current action ends. Without it the game feels unresponsive. Too long and inputs fire by accident.
- **Hit stop.** Freeze both parties for 2–6 frames on a hit to sell impact. Longer for heavy hits.
- **Invincibility frames (i-frames).** Dodge i-frames of 8–14 frames (estimate; 12 is common) at 60 fps give a forgiving roll. Fewer frames make dodging a precise skill. Tune with the recovery length: a roll with 12 i-frames and 20 recovery frames leaves 8 frames of vulnerability at the end.
- **Verification.** Store move data in JSON. A unit test confirms every move has positive startup, active and recovery, and that no combo loop is infinite without a cost. A replay test confirms the same inputs give the same hits.

### 0.2 Stamina and poise
Stamina limits how much the player can do. Poise (also called stagger or posture) limits how much damage an enemy or player can absorb before being interrupted.

```
Stamina regen model   S(t+dt) = min(S_max, S + r · dt)   after a delay d with no spend
Worked example: S_max 100, light attack 15, heavy 30, dodge 20, regen r = 40/s after delay 0.8 s
  Chain: 3 lights (45) + dodge (20) = 65 → 35 left. Full refill needs (65 / 40) + 0.8 ≈ 2.4 s
Poise meter    P decreases by hit_poise_damage; at P ≤ 0 → stagger for T_stagger, then P resets
  Boss P_max 100, light hit 12, heavy hit 35 → 9 lights or 3 heavies to stagger (my arithmetic)
  Poise regen starts after 4–6 s without a hit (estimate). Tune so staggers happen about every 20–30 s.
```

- **Stamina design choices.** Does blocking cost stamina? Does running? Stamina that empties often creates a "wait and counter" game. Stamina that rarely empties creates a "button mash" game. Pick on purpose.
- **Poise lets weight matter.** Heavy weapons stagger more. Heavy armour resists. Give the player a legible way to know an enemy is about to stagger.
- **Posture systems.** Some games (Sekiro-style) replace stamina with a posture meter that fills when you block and breaks, tied to attack rhythm.
- **Verification.** A sim runs scripted combos until stamina empties and compares time-to-empty with the table. A second sim hits a dummy to confirm stagger thresholds.

### 0.3 Enemy telegraphs and attack design
An enemy attack is a promise the player can learn. The telegraph is the learnable part.

```
Minimum startup  startup_min ≥ reaction + input + animation lead
   Estimated: reaction 12–15 frames (200–250 ms) + input 3–5 frames = 15–20 frames
   Fast enemies: 16–20 frame startup is a "reaction" attack. 25+ is "readable". 40+ is "easy".
Attack speed tiers (guidance, 60 fps): light 16–22 · medium 24–36 · heavy 36–60+
```

- **Visual and audio.** A distinct wind-up pose, a sound cue, and an optional light flash. Colour-code unblockable or special attacks (for example a distinct glow) and keep it consistent.
- **Delay and fake-outs.** Delayed swings and fakes make bosses feel alive. Introduce them after the player has learned baseline timing. Give a lower-difficulty option that removes delays.
- **Attack mix.** Each enemy has 3–6 attacks. Use a weighted random choice with a minimum gap between repeats and a rule that forces a different move after N repeats. Seed the choice so replays are deterministic.
- **Aggression budget.** Never let more than 2–3 enemies attack at once (a token system). The others circle. This keeps groups fair.
- **Boss phases.** Phase changes alter the move set and tempo. Signal each with an animation and sound. A fight with 2–3 phases suits most games.
- **Verification.** A test lists each attack's startup frames and fails if any attack below the "reaction" tier has no tell flag. A bot with scripted reaction delay (200 ms) confirms the fight is beatable by a model with normal reaction time.

### 0.4 Gating and keys
Progress in action-adventure is a graph of obstacles and keys. A key is anything that opens a gate: an item, an ability, a story flag or a skill the player learns.

```
Gate graph G = (areas, gates, keys); edge A→B requires key set K(A→B).
Reachability  R = BFS from the start with keys collected so far. Soft-lock if the player
   can reach a state where no key is reachable and required gates remain closed.
Worked example: hub H, dungeon D1 needs Hookshot (found in D0), D1 gives Bomb Bag,
   D2 needs Bomb Bag. Graph H→D0 free; D0→Hookshot; H→D1 [Hookshot]; D1→Bomb Bag;
   H→D2 [Bomb Bag]. Solver confirms a path exists and the order is forced. 
```

- **Hard versus soft gates.** A hard gate is a locked door or an invulnerable enemy. A soft gate is a power check: the area is open, but the enemies are too strong. Soft gates keep the world feeling open. Use signposts (enemy warning, NPC hint) so players do not mistake a soft gate for a bug.
- **Key variety.** Mix item keys, ability keys, knowledge keys (a code or lore hint) and narrative keys (a story flag). A world with only item keys feels like a chore list.
- **Safety nets.** Never allow a state where a required key can be lost or consumed without a way to get another. Run a solver on the gating graph in CI. For metroidvanias see `platformer-metroidvania.md` §0.2.
- **Pacing the loop.** Reward the player with a new ability or area every 20–40 minutes (estimate) and give a map marker or hint for the next step after N minutes of no progress.
- **Verification.** Export the graph to JSON and run the solver (`level-design`). Gate on: every key reachable, no soft-locks, and the minimum path length within the contract's band.

### 0.5 Camera
Camera is a combat system. A camera that hides enemies is a design bug.

- **Types.** Fixed (classic), top-down or isometric, over-the-shoulder third-person with free look, and first-person. Each needs different telegraph and lock-on rules.
- **Lock-on (third-person).** Choose the nearest target in the view cone. Allow switching with the right stick or a button. Show an on-screen marker. Disengage on distance or line-of-sight loss. Free-aim and lock-on should both work.
- **Collision.** Pull the camera in when geometry blocks it, and fade or cut away walls. Raycast from the player's head to the camera with a small radius. Use a smoothing time of 0.1–0.25 s (estimate) so it does not jitter.
- **Framing.** Keep the player and the locked target in frame. Zoom out when several enemies are near. Never let a heavy-attack wind-up leave the screen.
- **Field of view.** Third-person 60–75° is common. Give a slider on PC. A narrow FOV makes dodging harder to read. First-person needs a FOV slider for comfort.
- **Motion comfort.** Provide camera-shake and head-bob toggles. See `accessibility-localization`.
- **Verification.** A sim places 3–5 enemies around the player and checks that every attacking enemy is on screen or has an indicator at least N frames before the hit.

## 1. Zelda-like and open-world action-adventure

### Definition and player fantasy
An adventurer explores a world, solves puzzles, fights enemies and uses tools to reach new places. A Zelda-like has a hub and set-piece dungeons, each yielding an item that opens new paths. Open-world variants give a large map with points of interest. The fantasy is *discovery and growing power*: seeing something far away and finding a way there.

### Core loop
```
explore → find a gate or point of interest → solve a puzzle or fight
  → earn an item, ability or resource → open new gates → explore
  → dungeon or story boss → new region or tool
```

### Meta loops
- **Dungeon and tool chain.** Each dungeon introduces a tool and tests it.
- **Collectibles.** Heart pieces, upgrades and map secrets.
- **Crafting and gear.** Weapon upgrades, potions, outfits.
- **Side quests and NPCs.** Characters with small arcs.
- **Map activities.** Camps, towers, shrines or similar. Keep them distinct. Repeating a template for 100 icons is a known fatigue source.

### Session profile
Estimate: 40–120 minute sittings over 15–60 hours. Players follow curiosity and drift off the critical path. Save points and quick resume matter.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Item-gated progression | exploration & traversal | Gating graph (§0.4). Each item has at least three uses |
| Lock-on combat with shield and dodge | combat | Frame data (§0.1). Simple, readable |
| Environmental puzzles | exploration & traversal | Teach, test, twist. See `level-design` |
| Traversal tools (climb, glide, hook) | exploration & traversal | Define the movement budget early |
| Health and stamina | combat | Hearts or a bar. Stamina gates climbing and gliding |
| Sandbox physics or systemic rules | exploration & traversal | Fire, water, wind, magnetism. Fewer rules, more interactions |
| Map and markers | UX automation | Let the player place pins. Do not auto-fill the map with icons |

### Monetisation model and typical mix
Premium purchase with DLC or an expansion pass. Console-first titles have a long tail from full-price sales. Some China-led open-world action-adventures use free-to-play with a gacha (character pulls). That model is covered by `skills/genre-playbooks/references/rpg-gacha.md` and requires loot-box compliance. Do not sell progress in a premium game.

### KPI expectations
Qualitative. Completion rate of the main path, the point where players quit, share of players who finish the first dungeon, time to first tool, and percentage who find optional content. Review scores and word of mouth carry sales. No sourced benchmark ranges found.

### Retention drivers
Discovery, tool mastery, world reactivity, characters, side content with rewards, and clear next goals.

### Content pipeline and production scope (estimates)
World art, dungeons, enemy and boss designs, animation, NPCs and writing, audio and a lot of QA. Rough estimates: a small hand-built Zelda-like 8–20 people over 2–4 years. A large open world needs 100–1,000+ people.

### Reference titles
- *The Legend of Zelda: A Link to the Past* (Nintendo, 1991): the dungeon and item template.
- *The Legend of Zelda: Ocarina of Time* (1998): 3D lock-on.
- *The Legend of Zelda: Breath of the Wild* (2017) and *Tears of the Kingdom* (2023): systemic open world.
- *Tunic* (Andrew Shouldice, 2022): small-team Zelda-like.
- *Genshin Impact* (miHoYo, 2020): F2P open-world action RPG.
- *Death Stranding* (Kojima Productions, 2019): traversal-focused open world.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| The player has several things to try at any moment | Map icons replace curiosity |
| Tools have many uses and surprising interactions | Each tool opens one door |
| Dungeons are varied and memorable | Dungeons repeat the same pattern |
| The world rewards looking around | Content is padding |
| Combat is simple and readable | Combat is the weak link |

### Innovation vectors
- Systemic rules that create emergent solutions.
- Smaller, dense worlds in place of vast empty ones.
- Procedurally linked dungeons from hand-made rooms.
- Co-op exploration.
- Accessibility-first puzzle and combat options.

### Agent-buildability: 2/5 (one dungeon plus hub slice: 3/5)
**Why low:** world art, animation and sheer content volume. 
**What agents do well:** the gating graph and solver, puzzle logic, enemy state machines, inventory and save systems, quest state, procedural room assembly.

### Starter feature list (P0 vertical slice: hub + 1 dungeon + 1 boss)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Player controller: move, roll, attack, shield, lock-on (gameplay) | Frame data matches the table. Lock-on switches targets in the view cone |
| 2 | Camera with collision and framing (camera) | The 3–5 enemy sim shows no attacker off screen without an indicator (§0.5) |
| 3 | Health and stamina (gameplay) | Regen matches §0.2 table |
| 4 | 5 enemy types with telegraphs (gameplay) | Startup and tell flags pass the §0.3 test |
| 5 | Item chain: 2 tools, each with 3 uses (gameplay) | Each tool is required by at least one gate and optional in two places |
| 6 | Gating graph for hub and dungeon (level) | Solver finds a path. No soft-locks. Key order is as specified |
| 7 | Dungeon with 6 rooms, a mini-boss and a boss (content) | A bot completes it within the time band |
| 8 | Boss with 3 phases (gameplay) | Bot with 200 ms reaction clears in the target win-rate band |
| 9 | Map, pins and fast travel (ux) | Pins persist. Fast travel only to discovered nodes |
| 10 | Save and load (tech) | State survives a kill. Save during a boss resumes at the arena door |
| 11 | Collectible and upgrade (progression) | Collected count persists. Upgrade changes stats as in the table |
| 12 | Pause, settings and remap (ux) | Controls remap and persist. Subtitle and camera-shake toggles present |

### Platform notes
- **PC.** Support mouse and keyboard and gamepad. Camera control with a mouse needs separate sensitivity and lock-on tuning. Steam Deck Verified needs full controller access (`pc-web-release`).
- **Console.** Gamepad-first. Performance and quality modes, suspend and resume, and certification (`console-pathway`). Hand-held hardware reaches a wide audience.
- **Web.** Small Zelda-likes in a stylised 2D look are feasible. Keep the download small and save to local storage or cloud.
- **Mobile.** Touch combat is hard. Free-to-play open-world titles exist with virtual sticks and auto-lock. Business is gacha-led.
- **Business.** Premium on PC and console. Pricing for a small title is $15–30 (estimate). Wishlists and a demo matter.

## 2. Character action (combo systems)

### Definition and player fantasy
Fast, stylish melee and ranged combat with deep combo systems, mobility and a ranking for performance. The fantasy is *virtuosity*: chaining attacks, dodging at the last moment and looking great while doing it.

### Core loop
```
enter arena → read enemies → chain combos, dodge and counter
  → fill style meter → clear arena → rank → upgrade moves
  → next mission or boss
```

### Meta loops
- **Move shop.** Spend currency on new moves and weapons.
- **Ranking and replay.** Mission grades, style ratings and leaderboards.
- **Difficulty ladders.** Higher modes with new enemy behaviour.
- **Challenge modes.** Bloody-palace style survival, time attacks.

### Session profile
Estimate: 20–40 minute missions with 5–10 minute arenas. Replays for a higher grade are normal. Combat is the content.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Combo trees and cancels | combat | Frame data and cancel windows (§0.1). Moves cancel into others by rules |
| Dodge and parry with generous timing | combat | A timed reward (slow-motion, damage bonus) |
| Style meter | progression & upgrade | Rewards variety, not only speed |
| Launchers and air combat | combat | Camera and lock-on need extra care (§0.5) |
| Multiple weapons or stances | combat | Swap without delay. Each has a distinct role |
| Enemy token system | combat | 2–3 attackers at once (§0.3) |
| Mission grading | UX automation | Time, damage, style. Show breakdown |

### Monetisation model and typical mix
Premium purchase, sometimes with DLC characters or costumes. Cosmetic DLC is common and low-risk. Don't sell move unlocks that gate depth.

### KPI expectations
Qualitative. Completion rate, replay rate for grades, share of players using higher difficulties and time per arena. Community metrics (speedrun and combo videos) indicate depth.

### Retention drivers
Mastery, grades, higher difficulties, challenge modes, community clips and DLC.

### Content pipeline and production scope (estimates)
Animation dominates: each move needs polished animation, hit effects and sound. Enemy variety is another large item. Rough estimate: 20–100 people for AA and AAA. Indie examples use stylised 2D or low-poly to cut the cost, with 3–15 people over 2–4 years.

### Reference titles
- *Devil May Cry* (Capcom, 2001) and *Devil May Cry 5* (2019): style and combos.
- *Bayonetta* (PlatinumGames, 2009): witch time and dodge-offset.
- *Metal Gear Rising: Revengeance* (PlatinumGames, 2013): blade-mode precision.
- *Ninja Gaiden* (Team Ninja, 2004).
- *Hi-Fi Rush* (Tango Gameworks, 2023): rhythm-synced character action.
- *Sifu* (Sloclap, 2022): martial-arts combat with an ageing mechanic.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Moves feel snappy with clear cancel rules | Input lag and unreadable cancels |
| Depth available but not required | Only expert players can enjoy it |
| Enemies pressure and reward variety | Enemies are bags of HP |
| Camera keeps the action in frame | Camera hides attackers |
| Clear feedback on grades | Opaque scoring |

### Innovation vectors
- Rhythm-integrated combat.
- Weapon-swap chains with shared resources.
- Roguelite structures around combo builds.
- Assist modes that lower execution cost but keep spectacle.
- Online ghost and replay sharing.

### Agent-buildability: 3/5
**Why:** move data, cancel graphs and enemy state machines suit agents. Combo graphs can be searched for infinite loops and dominant strategies.
**Why not higher:** animation, hit feel and camera need artists and playtests.

### Starter feature list (P0 vertical slice: 1 arena, 12 moves, 4 enemy types)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Move data with frame data and cancel rules (gameplay) | JSON schema passes. Every move has startup, active, recovery |
| 2 | Combo graph with 12 moves (gameplay) | Graph search finds no infinite loop without a resource cost |
| 3 | Dodge with i-frames and a reward on perfect dodge (gameplay) | Window and reward per table. Verified in a frame-stepped replay |
| 4 | Input buffer (input) | A 6-frame early input fires on the first legal frame |
| 5 | Hit stop and hit effects (feel) | Hit stop frames per move class as in the table |
| 6 | Lock-on and camera (camera) | The §0.5 framing sim passes |
| 7 | 4 enemy types with tokens (gameplay) | At most 3 enemies attack together in a 100-run sim |
| 8 | Style meter and grading (meta) | Grade formula documented. Repeating one move lowers style |
| 9 | Move shop (progression) | Costs follow the table. Moves unlock correctly |
| 10 | Training room with frame display (ux) | Shows startup, active and recovery of the last move |
| 11 | Assist mode (accessibility) | Auto-dodge or timing widening toggles persist |

### Platform notes
- **PC.** Keyboard play is possible but hard. Gamepad is the expected input. Uncapped frame rate needs a fixed-step combat clock so frame data holds.
- **Console.** Native fit. 60 fps is the bar: frame data assumes it. Performance mode matters more than resolution.
- **Web.** Frame-accurate play is hard with variable browser timing. A fixed timestep and input timestamps help.
- **Mobile.** Touch combos are simplified (swipes, taps, auto-chain). Different design target.
- **Business.** Premium, with replay value measured in grades. Speedrun community support helps.

## 3. Soulslike

### Definition and player fantasy
A hard, stamina-based melee game with deliberate combat, a bleak world, checkpoints that respawn enemies, and a currency lost on death. The fantasy is *earned mastery*: the boss that beat you ten times finally falls.

### Core loop
```
leave checkpoint → explore carefully → fight enemies (stamina, dodge, punish)
  → gain souls (currency) → find shortcut → reach checkpoint or boss
  → die and retrieve lost currency → level up and upgrade gear
```

### Meta loops
- **Level-up and build.** Spend currency on stats and gear for builds.
- **Shortcuts and loops.** The world loops back to checkpoints.
- **Boss ladder.** Each boss teaches a lesson.
- **Online messages and summons.** Optional asynchronous and co-op elements.
- **New game plus.** Harder loops with carried gear.

### Session profile
Estimate: 45–120 minute sittings over 30–80 hours. A single boss may take 30 minutes. Players stop after a win or a frustrating loss, so checkpoint spacing matters.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Stamina-based combat | combat | §0.2. Every action spends stamina |
| Telegraphed enemy attacks with real punish windows | combat | §0.1 and §0.3 |
| Lock-on and dodge | combat | Camera (§0.5). Roll with i-frames |
| Death currency and corpse run | economy & resources | Recover lost currency by reaching the spot once |
| Checkpoint with respawn | economy & resources | Resting heals and respawns enemies |
| Shortcut loops | exploration & traversal | Unlock doors from the far side |
| Gear stats and weight | progression & upgrade | Equip load affects roll speed |
| Minimal story and environmental narrative | narrative | Items and place tell the story |

```
Checkpoint spacing: target a death-run length of 2–5 minutes between a checkpoint and a boss
  (estimate). If a boss attempt costs 4 minutes of travel plus 2 minutes of fight, 60% of the time is
  waste; add a shortcut or a checkpoint at the boss door.
Damage scaling: boss damage kills in 3–5 hits at the expected level (estimate). Fewer than 3 feels cheap.
```

### Monetisation model and typical mix
Premium purchase with DLC expansions. Some mobile and F2P attempts exist but lose the tension. Do not sell revive or difficulty skips as microtransactions.

### KPI expectations
Qualitative. Deaths per boss, share of players who beat each boss, area where players quit, time to first boss, and attempts before success. A target is a band where most players beat the first boss within 5–15 attempts (estimate, set in the contract). Review scores and communities (wikis, guides) matter.

### Retention drivers
Mastery, build variety, discovery, boss fights, community knowledge and new game plus.

### Content pipeline and production scope (estimates)
Bosses and enemies with polished animations, handcrafted interconnected levels, gear catalogues and balance. Rough estimate: 15–100+ people over 2–5 years. Indie soulslikes with 2D or low-poly scope fit 3–15 people.

### Reference titles
- *Demon's Souls* (FromSoftware, 2009), *Dark Souls* (2011) and *Elden Ring* (2022).
- *Bloodborne* (FromSoftware, 2015): aggression-oriented.
- *Sekiro: Shadows Die Twice* (FromSoftware, 2019): posture system.
- *Hollow Knight* (Team Cherry, 2017): a 2D soulslike-metroidvania blend.
- *Nioh* (Team Ninja, 2017).
- *Lies of P* (Neowiz, 2023).

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Every death teaches something visible | Deaths feel random or unfair |
| Telegraphs are readable and consistent | Delays and camera hide attacks |
| A world that loops and rewards exploration | Long corridors between checkpoints |
| Build variety with viable options | One dominant weapon |
| Difficulty by design plus optional help items | Difficulty from bugs, input lag or bad hitboxes |

### Innovation vectors
- Accessibility options that preserve the challenge (assist items, adjustable timing).
- Non-melee soulslikes (ranged, magic, stealth).
- Shorter runs and roguelite structure.
- Co-op summons and asynchronous ghosts.
- Smaller worlds with denser design.

### Agent-buildability: 3/5
**Why:** deterministic frame data, bot-testable boss fights, build math and gating graphs.
**Why not higher:** boss design, animation, environmental storytelling and feel.

### Starter feature list (P0 vertical slice: 1 area loop + 1 boss)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Stamina and combat actions (gameplay) | Table in §0.2 satisfied. Regen delay respected |
| 2 | Move data for 2 weapons (gameplay) | Frame data validated. Weight affects roll speed |
| 3 | Lock-on and roll i-frames (gameplay) | Roll i-frames per table. Lock-on switch works |
| 4 | Poise and stagger (gameplay) | A dummy staggers at the thresholds in the table |
| 5 | 5 enemy types, each with 3–5 attacks (gameplay) | Telegraph test passes. Attack selection is seeded |
| 6 | Checkpoint with respawn and heal charges (meta) | Resting respawns enemies and refills the charges |
| 7 | Death currency drop and retrieval (economy) | Dies once: currency drops. Dies again before retrieval: lost |
| 8 | Loop with a shortcut (level) | Solver confirms the shortcut connects the checkpoint and the boss gate |
| 9 | Boss with 2 phases (gameplay) | Bot at 200 ms reaction wins at the target rate within 5–15 attempts |
| 10 | Level-up screen and 2 stats (progression) | Stat points change damage and health per formula |
| 11 | Gear and equip load (progression) | Equip load thresholds change roll type |
| 12 | Save on quit (tech) | The game saves at safe times. A forced kill never loses the last checkpoint |

### Platform notes
- **PC.** Gamepad is the common choice. Frame data must hold with uncapped frame rates, so decouple the combat clock. Mouse lock-on needs care. Online features need anti-cheat decisions.
- **Console.** Native fit, 60 fps preferred. Remember suspend and resume during a boss fight.
- **Web.** Input latency and frame timing limit precision. Choose a slower tempo if you target web.
- **Mobile.** Rare and hard. Touch controls and stamina management strain precision.
- **Business.** Premium with a loyal base. Easy-mode debate: offer assist options without changing the default.

## 4. Immersive sim

### Definition and player fantasy
A first-person (or similar) simulation where interacting systems let players solve problems in many ways: stealth, combat, hacking, talking or exploiting physics. The fantasy is *emergent problem-solving*: "I wonder if I can do this" and the game says yes.

### Core loop
```
enter a space with an objective → observe (guards, security, routes)
  → choose an approach (stealth, combat, social, systemic)
  → act and adapt to consequences → complete the objective
  → earn upgrades or resources → next space
```

### Meta loops
- **Character build.** Skills, augmentations or perks that favour approaches.
- **Reactive world.** Consequences carried across missions.
- **Exploration rewards.** Notes, codes, shortcuts and optional objectives.
- **Replay.** Different approaches or difficulty modifiers.

### Session profile
Estimate: 60–180 minute sittings over 15–40 hours. Players save often and reload to experiment. Quick save and quick load are expected.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Multiple solutions per objective | exploration & traversal | Design at least 3 routes per major obstacle |
| Systemic simulation (light, sound, physics, fire, AI senses) | combat | Systems must interact predictably. Test combos |
| Inventory and resource tension | economy & resources | Scarcity shapes choices |
| Hacking, lockpicking and puzzles | exploration & traversal | Short, skippable with cost |
| Reactive AI and world state | narrative | Consequences stored in flags |
| Environmental storytelling and logs | narrative | Notes, audio logs, set dressing |
| Build specialisation | progression & upgrade | Allow hybrids, avoid dead builds |

### Monetisation model and typical mix
Premium purchase with DLC or expansion. Rare cosmetic add-ons. Avoid anything that sells advantages. Many studios rely on word of mouth and a long tail.

### KPI expectations
Qualitative. Completion rate, share using each approach, number of quick loads per mission, optional objective completion, time per level and where players report being stuck. Not suited to heavy telemetry-driven balance.

### Retention drivers
Player expression, discovery, replay with different builds and world reactivity.

### Content pipeline and production scope (estimates)
Levels are dense and hand-built, with systems tested in every space. High QA cost because of system interactions. Rough estimate: 30–150 people over 3–5 years for a full title. A solo or tiny-team slice (one level, a few systems) is feasible.

### Reference titles
- *System Shock 2* (Looking Glass and Irrational, 1999).
- *Deus Ex* (Ion Storm, 2000).
- *Thief: The Dark Project* (Looking Glass, 1998): light and sound stealth.
- *Dishonored* (Arkane, 2012) and *Dishonored 2* (2016).
- *Prey* (Arkane, 2017).
- *Deus Ex: Human Revolution* (Eidos Montréal, 2011).

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Systems interact in consistent, learnable ways | Rules are inconsistent or hidden |
| Levels give many routes with clues | One intended path is obvious |
| Player choice has consequences | Choice is cosmetic |
| Combat, stealth and social routes are all viable | One approach dominates |
| Good tools to test and undo (quick save) | Autosave punishes experimenting |

### Innovation vectors
- LLM-driven NPC conversation within strict rules (unverified in shipped titles here).
- Procedural immersive-sim levels with systemic rules.
- Systemic multiplayer or co-op heist modes.
- Small-scale immersive sims with a single location.
- Better tools for authored consequence tracking.

### Agent-buildability: 2/5
**Why low:** the value is in system interactions across hand-built spaces. Testing every interaction is a combinatorial task, and the player's creativity defines the game.
**What agents do well:** AI perception logic, flag and consequence tracking, inventory systems, hacking minigames, and system-interaction test harnesses (fire plus oil, noise plus guards).

### Starter feature list (P0 vertical slice: one level, 3 approaches)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | First-person controller with lean, crouch and interact (gameplay) | Lean peeks without clipping. Interact range per table |
| 2 | Physics objects: carry, throw, stack (gameplay) | Objects obey mass. Thrown objects make noise per table |
| 3 | AI perception: sight cone, light level, sound (gameplay) | Detection matches the formula. Unit-tested for light and noise |
| 4 | 3 solution routes to the objective (level) | Solver or bot confirms each route completes. Routes use different skills |
| 5 | Inventory with limited slots (economy) | Capacity enforced. Item use effects tested |
| 6 | Lockpick or hacking minigame (gameplay) | Completes in under 15 s for a normal player. Can be skipped with a consumable |
| 7 | Systemic interaction pair (fire plus oil, water plus electricity) (gameplay) | A test confirms the effect chain triggers and stops |
| 8 | Reactive flags (narrative) | Killing, sparing or ignoring an NPC changes the outcome as in the table |
| 9 | Quick save and load (tech) | Restores the exact state. Disabled only in marked scripted moments |
| 10 | 4 skills or augmentations (progression) | Each skill favours one route and has a partial use in another |
| 11 | Optional objective with a notes trail (content) | Clue chain leads to a code. No guesswork needed |

### Platform notes
- **PC.** Mouse and keyboard suit precise interaction and quick save. Mod support extends life. Needs many keybinds.
- **Console.** Gamepad needs radial menus and a clear interact prompt. Quick save becomes a menu option. Console ports of the genre exist but need tuned UI.
- **Web.** Small prototypes only. Physics and AI cost frame time.
- **Mobile.** Rarely suitable due to the control load.
- **Business.** Premium niche audience with a strong reputation. Wishlists, critic reviews and demos are the funnel.

## 5. Stealth

### Definition and player fantasy
The player avoids detection, uses shadows and sound, and removes or bypasses guards. The fantasy is *the perfect ghost*: moving unseen, planning and executing a clean run.

### Core loop
```
observe patrols → plan a route → move and manipulate (distract, hide, take down)
  → reach the objective undetected (or recover if spotted) → exit
  → rank and rewards → upgrade tools → next mission
```

### Meta loops
- **Tool and gadget upgrades.** Distraction items, non-lethal options, movement tools.
- **Mission ranks.** Ghost, non-lethal, speed.
- **Challenge modes.** No kills, no alerts, time attacks.
- **Branching routes.** Different outcomes based on detection.

### Session profile
Estimate: 30–60 minute missions over 8–20 hours. Quick reloads after failure are part of the loop. Short missions suit weeknight play.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Guard perception (vision, hearing) | combat | Formula below. Readable indicators |
| Light and shadow, noise and surfaces | exploration & traversal | Visible meter for the player |
| Distraction tools | combat | Thrown objects, whistles, gadgets |
| Takedowns and non-lethal options | combat | Risk during the animation. Bodies must be hidden or noticed |
| Alert states (unaware, suspicious, alert, search) | combat | Clear transitions with timers and audio cues |
| Hiding spots and vents | exploration & traversal | Provide a safe route with a trade-off |
| Mission rating | UX automation | Shows detection counts and kills |

```
Detection meter   D(t+dt) = clamp(D + rate · dt, 0, 1)   rate = base · distance_factor · light_factor · speed_factor
Worked example: base 1.0/s, distance 10 m (factor 0.5), full light (1.0), crouch-walk (0.5)
  rate = 1.0 · 0.5 · 1.0 · 0.5 = 0.25/s → 4 s to full detection (estimate for tuning)
Same guard at 3 m, sprinting (1.5): rate = 1.0 · 1.0 · 1.0 · 1.5 = 1.5/s → 0.67 s
Alert decay: suspicious state falls back to unaware after 8–15 s with no new stimulus (estimate)
```

### Monetisation model and typical mix
Premium purchase with DLC missions. Cosmetic outfits are low risk. Mobile stealth-puzzle games use ads and IAP, which are covered by hybrid-casual patterns.

### KPI expectations
Qualitative. Mission completion rate, share completing undetected, number of reloads per mission, time per mission, drop-off mission, and how players use non-lethal tools. A target is a band for detection frequency: most first-time players are spotted at least once but recover (estimate, set per mission).

### Retention drivers
Mastery of AI behaviour, challenge ranks, mission variety, tools and replay for ghost runs.

### Content pipeline and production scope (estimates)
Levels with multiple routes, guard patrol logic, animation for takedowns and stealth movement, audio design. Rough estimate: 10–50 people over 2–4 years. Small stealth-puzzle games with a top-down or isometric view cost less, with 2–8 people over 1–2 years.

### Reference titles
- *Metal Gear Solid* (Konami, 1998).
- *Thief* (Looking Glass, 1998).
- *Splinter Cell* (Ubisoft, 2002).
- *Hitman* (IO Interactive, 2016): social stealth sandboxes.
- *Dishonored* (Arkane, 2012).
- *Mark of the Ninja* (Klei, 2012): 2D stealth with clear sound visuals.
- *Aragami* and *Desperados III* (2016, 2020): shadow stealth and real-time tactics.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| AI behaviour is consistent and readable | AI sees through walls or reacts unfairly |
| Clear feedback on visibility and noise | The player cannot tell why they were spotted |
| Failure is recoverable, with fun alerts | Any detection means a restart |
| Multiple tools and routes | One optimal route |
| Quick retry loop | Long loading or replay of the level |

### Innovation vectors
- Systemic stealth (AI reacts to systems, not scripts).
- Social stealth and disguise.
- Co-op stealth.
- Real-time tactics with stealth.
- Accessibility options for detection feedback (audio cues, visual indicators).

### Agent-buildability: 3/5
**Why:** AI perception, alert state machines and route validation suit agents. Bots can test route solvability and detection tuning.
**Why not higher:** readable level design, animation, and feel for tension need human iteration.

### Starter feature list (P0 vertical slice: one level, 4 guards, 3 routes)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Player movement: walk, crouch, sprint, peek (gameplay) | Speed and noise values per table |
| 2 | Guard vision cone and hearing (gameplay) | Detection formula unit-tested. Cones respect walls and light |
| 3 | Alert state machine (gameplay) | States, timers and transitions match the diagram |
| 4 | Patrol routes with waits (gameplay) | Patrols loop. No guard stands idle forever. Routes deterministic by seed |
| 5 | Distraction tool (gameplay) | A thrown object draws guards within radius per table |
| 6 | Takedown and body discovery (gameplay) | Takedown takes N frames. Found bodies raise alert in one step |
| 7 | Detection UI: meter and indicators (ux) | Meter matches internal D within 5%. Off-screen guards indicated |
| 8 | Level with 3 routes (level) | Bot completes each route undetected at the target rate |
| 9 | Hiding spots (gameplay) | Hidden players are not detected unless searched |
| 10 | Mission rating (meta) | Counts detections, kills, time. Rank thresholds from table |
| 11 | Quick retry (ux) | Reload to last checkpoint in under 3 s |

### Platform notes
- **PC.** Mouse and keyboard allow precise peeking and fast reaction. Quick save is expected. Mod and level editors extend life.
- **Console.** Gamepad movement needs a walk-speed slider (analogue) and a clear crouch toggle. Autosave at safe points for certification.
- **Web.** 2D and top-down stealth are feasible and cheap. Short missions suit web portals.
- **Mobile.** Stealth puzzles with tap-to-move suit touch. Ads and IAP business models. See hybrid-casual patterns in `skills/genre-playbooks/references/hyper-hybrid-casual.md`.
- **Business.** Premium on PC and console. Mission DLC and cosmetic packs extend revenue.

## Volatile facts (as of Oct 2026 — verify before relying)

- Hollow Knight: Silksong (Team Cherry, launched 4 September 2025) passed 7 million copies in about three months, a figure that excludes Xbox Game Pass players. About 4.2 million sold in the first weeks, with Steam about 3.2 million. A third-party estimate put Steam revenue near $50 million at a $20 price (estimate). Useful as a scale anchor for a premium action-adventure, though it is a metroidvania — [TweakTown](https://tweaktown.com/news/109417/hollow-knight-silksong-sells-7-million-copies-since-launch-with-millions-of-game-pass-players/index.html), [WN Hub](https://wnhub.io/news/investment/item-49578)
- Steam Deck Verified requires the default controller configuration to reach all content, on-screen glyphs matching Deck or Xbox buttons, and controller-usable text entry. Criteria may change — [Steamworks docs](https://partner.steamgames.com/doc/steamdeck/compat)
- Steam's revenue share has been reported as 30% up to $10M, 25% from $10M to $50M and 20% above $50M per game (since October 2018). Confirm the current terms in Steamworks — [Fortune](https://fortune.com/2018/12/01/steam-valve-developer-revenue-agreement)
- Loot-box regimes (Belgium, Brazil under-18 ban from March 2026, Australia M/R18+) apply to F2P open-world action-adventure gacha pulls. Details and sources are in `skills/genre-playbooks/references/rpg-gacha.md` volatile facts.
- Unity deprecated Multiplay Game Server Hosting on Apr 1, 2026. This matters only for online soulslike or co-op features — [Unity status](https://status.unity.com/info_notices/362941)
- Console certification and age-rating processes are covered by `console-pathway` and should be checked against the platform holder's current documents.

## Related skills
- `game-feel`: hit stop, screen shake, input latency, animation timing.
- `level-design`: gating graphs, dungeon structure, teach-test-twist, solver gates.
- `progression-difficulty`: boss difficulty, win-rate bands, assist options.
- `balance`: stamina, poise, damage and build sims.
- `gameplay-programming`: state machines, input buffering, AI perception.
- `narrative-design`: environmental storytelling, quests and consequence flags.
- `platform-targets`: input, camera sensitivity and performance tiers per platform.
- `pc-web-release`: Steam, demos and wishlists.
- `console-pathway`: console certification and ratings.
- `accessibility-localization`: assist modes, camera comfort, remapping.
- `qa-testing`: bot boss fights, replay tests, soft-lock solvers.
- `procedural-generation`: room assembly and validation.
