# 02 — Combat and Action Mechanics

Combat is a set of rules about who can hurt whom, when, how much, and how the player reads it. On mobile it splits into two families: **automated combat**, where the player's skill is positioning, build choice and timing of a few abilities (survivors, Archero-likes, idle squads, tower defense), and **manual combat**, where inputs are judged frame-by-frame (combos, parry, dodge, bullet patterns). This file catalogues 23 combat mechanics with precise rules, tuning ranges, damage maths, failure modes and implementation sketches, from auto-attack to bosses and the hit-stop/hurtbox layer that makes hits read as hits. Numbers are starting points for tuning, not facts about any one game unless a game is named. For difficulty curves and dynamic difficulty see `progression-difficulty`; for the feel layer see `game-feel`; for movement verbs (dash, jump) see `references/01-verbs-movement-physics.md`.

## Contents

1. Combat model and shared formulas
2. Index of mechanics
3. Automated and aim-assisted combat (entries 1–5)
4. Manual skill combat (entries 6–10)
5. Build and system combat (entries 11–16)
6. Defense, waves and encounters (entries 17–21)
7. Hit resolution layer (entries 22–23)
8. Combat balance checklist

## 1. Combat model and shared formulas

Model every combat system as a deterministic simulation with these components, so that it can be unit tested, bot-tested and balanced with spreadsheets or `${CLAUDE_PLUGIN_ROOT}/scripts/economy_sim.py`-style Monte Carlo runs:

- **Entities** with `hp`, `max_hp`, `armor`/`resist`, `team`, `position`, `hurtboxes`, `status[]`, `cooldowns{}`.
- **Attacks** as data: `{damage, type/element, hitbox shape, startup, active, recovery, knockback, hitstop, status_on_hit[], targeting}`.
- **Events**: `HitEvent(attacker, target, attack, crit, final_damage)` produced by the sim, consumed by the presentation layer for juice.

Core formulas used throughout:

| Quantity | Formula | Notes |
|---|---|---|
| DPS | `damage × attacks_per_sec × (1 + crit_rate × (crit_mult − 1))` | Expected value including crits |
| Armor mitigation (diminishing) | `taken = raw × 100 / (100 + armor)` | Each point of armor adds the same % of effective HP; popularised by MOBAs |
| Effective HP | `EHP = hp × (100 + armor) / 100` | Compare defensive options in one unit |
| Time to kill | `TTK = target_EHP / attacker_DPS` | The central pacing number of any combat game |
| Flat reduction (avoid at scale) | `taken = max(raw − armor, min_dmg)` | Makes weak hits useless; use only with a floor |
| Damage variance | `raw × U(0.9, 1.1)` | ±10 % hides breakpoints; keep 0 for puzzle-like combat |

**TTK targets.** Fodder: 0.2–1 s (one to three hits). Elites: 3–8 s. Bosses: 45–180 s on mobile sessions. Player TTK (how long the player survives under focus fire) is usually 3–10× longer than enemy TTK in PvE, so mistakes are punished without instant death.

## 2. Index of mechanics

| # | Mechanic | ID | Category | One-line essence | Typical home genres |
|---|---|---|---|---|---|
| 1 | Auto-attack | `auto-attack` | automated | Attacks fire on a timer at a chosen target | idle RPG, MOBA, survivors |
| 2 | Auto-aim survivors (horde) | `auto-aim-survivors` | automated | Move only; weapons fire themselves at a horde | survivors-like, roguelite |
| 3 | Stop-to-shoot | `stop-to-shoot` | automated | Moving dodges, standing still attacks | Archero-like |
| 4 | Twin-stick with aim assist | `twin-stick-aim-assist` | aim | Left stick moves, right stick aims, assist bends shots | shooter, hero brawler |
| 5 | Auto-battle squad composition | `auto-battle-squad` | automated | Pick team and positions; battle resolves itself | idle RPG, auto-battler |
| 6 | Cooldown abilities and ultimates | `cooldown-abilities` | manual | Few strong skills gated by time or charge | MOBA, action RPG |
| 7 | Combos and cancel windows | `combos` | manual | Input strings chain into bigger payoffs | brawler, fighting, ARPG |
| 8 | Parry and perfect block | `parry` | manual | Precise defensive timing converts threat to opening | action, fighting |
| 9 | Dodge and i-frames | `dodge-iframes` | manual | Short invulnerable evasion | action, roguelite |
| 10 | Bullet patterns | `bullet-patterns` | manual | Readable projectile geometry as the challenge | shmup, bullet hell, bosses |
| 11 | Projectile upgrades | `projectile-upgrades` | build | Multishot, pierce, ricochet and friends | Archero-like, survivors |
| 12 | Crowd and mob combat (count armies) | `crowd-mob-combat` | build | Army size is HP and damage; gates multiply | crowd runner, mob shooter |
| 13 | Elemental reactions | `elemental-reactions` | system | Element pairs trigger reactions | action RPG, puzzle RPG |
| 14 | Status effects | `status-effects` | system | Timed modifiers with stacking rules | all |
| 15 | Damage model, crits and armor | `damage-model` | system | The arithmetic of hurting | all |
| 16 | Aggro and threat | `aggro-threat` | system | Who enemies attack, and how to control it | RPG, squad, MMO-lite |
| 17 | Tower targeting | `tower-targeting` | defense | Priority rules choose what each tower shoots | tower defense |
| 18 | Lane defense | `lane-defense` | defense | Place defenders in lanes against marching waves | lane TD |
| 19 | Wave spawning and director | `wave-director` | encounter | Budgeted spawns shaped into tension curves | survivors, TD, shooters |
| 20 | Boss encounters | `boss-encounters` | encounter | Phased, telegraphed set pieces | all action |
| 21 | Hordes, elites and affixes | `elite-affixes` | encounter | Modifiers create variety from few enemy types | ARPG, roguelite |
| 22 | Hit-stop, hitboxes and hurtboxes | `hitstop-hitboxes` | hit resolution | Geometry and freeze frames that make hits real | all action |
| 23 | Knockback, stagger and poise | `knockback-poise` | hit resolution | Hits move and interrupt bodies | brawler, ARPG |

## 3. Automated and aim-assisted combat

### 02.01 Auto-attack — `auto-attack`

- **ID:** `auto-attack` · **Category:** automated combat · **Player fantasy:** "My hero fights on their own; I make the smart calls."
- **Core rules:**
  - Each attacker has `attack_interval = 1 / attack_speed` and `range`. When a valid target is in range and the attack timer ≤ 0, start an attack (wind-up `t_windup`), apply damage at the hit frame, reset timer.
  - Target selection by rule: nearest, lowest HP, highest threat, "current target until dead" (sticky). Re-evaluate on target death or every `retarget_interval`.
  - Movement interrupts or does not interrupt the attack depending on design (MOBA: move cancels wind-up; idle: no movement).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Attack speed | 0.5–3 attacks/s | Faster feels responsive, multiplies on-hit effects |
| Wind-up | 0.1–0.4 s | Longer allows animation cancelling skill |
| Range | melee 1–2 wu, ranged 5–10 wu | Positioning depth |
| Retarget interval | 0.2–1.0 s | Short = smart, long = predictable |
| Sticky targeting | on/off | On reduces damage spread, aids focus fire |

- **Dynamics:** player attention shifts to positioning, builds and ability timing; attack-speed scaling interacts multiplicatively with on-hit effects (watch for exponential builds).
- **Aesthetics (MDA):** Submission, Challenge (build), Fantasy (power).
- **Feedback and juice:** wind-up anticipation pose, hit flash on target (1–2 frames white), damage numbers, light screen shake only for crits.
- **Failure modes and exploits:** kiting AI that never closes distance; targeting ping-pong between two equidistant enemies (add hysteresis: switch only if new target is ≥ 10–20 % closer); idle combat with zero decisions (add at least one active ability).
- **Mobile fit:** perfect one-handed; works with screen off in idle variants (offline simulation).
- **Monetization hooks and ethical limit:** attack-speed boosts, hero upgrades; in PvP, cap the gap paid upgrades can create or use matchmaking by power.
- **Implementation notes:** timers in sim ticks; spatial hash for target queries (grid cell ≈ max range).

```text
for a in attackers: a.timer -= dt
  if a.target invalid or a.retarget_t <= 0: a.target = select(a, rule, hysteresis=0.15); a.retarget_t = RETARGET
  if a.target in range and a.timer <= 0: a.timer = 1/a.attack_speed; schedule_hit(a, a.target, at=now+a.windup)
```

- **Reference games:** AFK Arena, Vampire Survivors (weapons), League of Legends: Wild Rift (basic attacks), Clash Royale (unit attacks).
- **Combines well with:** `auto-battle-squad`, `status-effects`, `aggro-threat`, `projectile-upgrades`, idle generators (`references/04-economy-resource-mechanics.md`).

### 02.02 Auto-aim survivors (horde) — `auto-aim-survivors`

- **ID:** `auto-aim-survivors` · **Category:** automated combat (horde) · **Player fantasy:** "Alone against thousands — and I become an unstoppable storm."
- **Core rules:**
  - Player controls movement only. Each owned weapon fires on its own cooldown with its own targeting (nearest, random, facing, orbit, area around player).
  - Enemies spawn continuously from off-screen around the player, pathing straight toward them; contact deals damage.
  - Killed enemies drop XP gems; level-ups pause the game and offer 3–4 random choices (new weapon, weapon level, passive). Weapons have max levels; specific weapon + passive pairs "evolve" into stronger forms (in Vampire Survivors, evolution comes from a chest once the weapon is maxed and its paired passive is owned).
  - Run ends on death or at the time limit (classic: a fixed ~15–30 min run with a final boss or reaper).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Run length | 10–30 min (mobile chapters often shorter) | Session fit |
| Weapon slots / passive slots | 4–6 each | Build depth and choice pressure |
| XP curve per level | +5–15 % per level | Pace of power growth |
| Choices per level-up | 3–4, plus reroll/banish charges | Agency vs randomness |
| Enemy density at peak | 200–600 on screen (device-limited) | Spectacle and perf |
| Magnet/pickup radius | 1–3 wu base | Movement incentive and QoL |

- **Dynamics:** early fragility → late screen-clearing power fantasy; route-planning through hordes; build synergies discovered across runs (meta progression).
- **Aesthetics (MDA):** Fantasy (power), Discovery (builds), Submission, Challenge in late waves.
- **Feedback and juice:** gem vacuum with pitch ladder, level-up freeze with radial burst, kill counter, minimal per-hit shake (thousands of hits) — juice the totals, not each hit.
- **Failure modes and exploits:** perf collapse from entity counts (pool everything, GPU instancing, simple circle collision, spatial hashing); "corner camping" or circular kiting trivialising waves (spawn ring adapts to velocity; add ranged enemies); unreadable screen (cap VFX alpha and particle count).
- **Mobile fit:** floating joystick anywhere on screen, one-handed portrait works; pause on interruption is mandatory.
- **Monetization hooks and ethical limit:** meta upgrades, characters, revives, rewarded-ad rerolls. Avoid selling the only path past a hard difficulty wall; keep runs winnable with skill and free meta progress.
- **Implementation notes:** enemies as struct-of-arrays (positions, velocities, hp) updated in tight loops; separation by grid buckets; damage via area queries per weapon tick, not per-bullet physics bodies.
- **Reference games:** Vampire Survivors, Survivor.io, Brotato, Magic Survival.
- **Combines well with:** `projectile-upgrades`, `wave-director`, `elite-affixes`, meta progression (`references/05-progression-meta-mechanics.md`), random draft (`references/07-randomness-chance-mechanics.md`).

### 02.03 Stop-to-shoot — `stop-to-shoot`

- **ID:** `stop-to-shoot` · **Category:** automated combat (move/attack split) · **Player fantasy:** "A dance — slip through danger, plant my feet, unload."
- **Core rules:**
  - While the movement input is active, the hero moves and does not attack. When the joystick is released, the hero auto-targets (nearest, or the last target) and fires continuously.
  - Rooms or stages are cleared of enemies to proceed; level-ups or room clears offer ability draft choices.
  - Enemies telegraph attacks; stillness is the vulnerability window.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Fire start delay after stop | 0–150 ms | Lower is snappier; higher punishes micro-stops |
| Move speed vs projectile speed | enemy shots 0.6–1.2× hero speed | Dodgeability |
| Room size | 1–1.5 screens | Positioning complexity |
| Enemy telegraph time | 0.4–1.0 s | Fairness and reading |
| Rooms per chapter | 10–50 with mid and final bosses | Session length |

- **Dynamics:** rhythmic move/stop cadence; risk calculus on when to stand; build choice transforms the cadence (e.g., more projectiles shorten needed stand time).
- **Aesthetics (MDA):** Challenge, Fantasy, Discovery (builds).
- **Feedback and juice:** clear stance change (hero plants, bow draws), damage numbers, enemy hit flashes, room-clear chime and door open.
- **Failure modes and exploits:** standing still in safe corners where enemies cannot reach (path-aware spawns, ranged enemies); unreadable bullets on busy floors.
- **Mobile fit:** single thumb joystick; designed for portrait one-hand play.
- **Monetization hooks and ethical limit:** gear, talents, energy per run; watch for power gating that makes chapters unwinnable without spend.
- **Implementation notes:** the "stopped" state is derived from input magnitude < dead zone for ≥ 1 tick; keep firing logic in sim; draft choices seeded per run for reproducibility.
- **Reference games:** Archero, Archero 2, Soul Knight (manual-aim contrast).
- **Combines well with:** `projectile-upgrades`, `bullet-patterns`, `boss-encounters`, `status-effects`.

### 02.04 Twin-stick with aim assist — `twin-stick-aim-assist`

- **ID:** `twin-stick-aim-assist` · **Category:** aim-assisted combat · **Player fantasy:** "I move and shoot with precision, and the game has my back."
- **Core rules:**
  - Left virtual stick moves; right stick aims (drag direction) and fires while held, or fires on release (skill shots). Quick tap on the right stick = auto-aimed attack at the best target.
  - Aim assist: within a cone of `assist_angle` and range, bend the aim direction toward the highest-scoring target by `assist_strength`; optional bullet magnetism (projectile homes slightly).
  - Skill shots show an aim indicator (line, cone, circle) while dragging; release fires; drag back to centre cancels.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Stick dead zone | 8–15 % of radius | Prevents drift |
| Floating vs fixed stick | floating for move, fixed for aim | Floating fits any thumb position |
| Assist cone | 10–30° | Wider helps touch imprecision |
| Assist strength | 20–60 % angular pull | Too strong removes skill |
| Tap-to-auto-aim | on/off | Big accessibility gain on glass |
| Cancel zone | inner 15–25 % of stick | Prevents wasted skill shots |

- **Dynamics:** split attention (dodge with left, aim with right); prediction shots versus auto-aim taps creates a skill gradient between casual and expert players.
- **Aesthetics (MDA):** Challenge, Sensation, Fellowship (team modes).
- **Feedback and juice:** aim indicator turns red when a target is in line, muzzle flash, impact sparks, hit markers, short controller-style haptic on hits.
- **Failure modes and exploits:** thumbs covering the action (keep the camera offset toward aim direction); assist pulling to the wrong target in crowds (score targets by angle first, distance second); PvP assist imbalance between input types.
- **Mobile fit:** landscape, two thumbs; sessions of 2–3 min per match work well.
- **Monetization hooks and ethical limit:** heroes and skins; aim assist must never be a paid advantage.
- **Implementation notes:** target score `= w_a·(1 − angle/cone) + w_d·(1 − dist/range) + w_t·is_current_target`; aim `= slerp(input_dir, dir_to_best, assist_strength)`.
- **Reference games:** Brawl Stars, Soul Knight, PUBG Mobile and Call of Duty: Mobile (assisted aiming), League of Legends: Wild Rift (skill-shot sticks).
- **Combines well with:** `dodge-iframes`, `cooldown-abilities`, `bullet-patterns`, `status-effects`.

### 02.05 Auto-battle squad composition — `auto-battle-squad`

- **ID:** `auto-battle-squad` · **Category:** automated combat (team) · **Player fantasy:** "I'm the commander; my roster and formation win the war."
- **Core rules:**
  - Before battle, choose N units (typically 5) and their positions (front/back rows or hex grid). Battle then runs without input (optionally one manual input: ultimate timing).
  - Units have roles (tank, damage, support, control), factions/classes, and synergy bonuses for fielding k units of a tag (e.g., 2/4/6 thresholds).
  - Energy/ultimate meter fills from attacking and taking damage; full meter → ultimate (auto or player-triggered).
  - Outcome: deterministic given seed and stats, which allows instant simulation, replays and offline "idle" battles.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Team size | 3–6 | Composition depth |
| Synergy thresholds | 2/4/6 or 3/5 | Encourages focused vs flexible teams |
| Synergy bonus size | +10–40 % stat or new effect | Must beat raw-power stacking sometimes |
| Ultimate meter gain | full in 6–15 s of combat | Pacing of spikes |
| Battle duration cap | 60–90 s, then defender wins or sudden death | Prevents stalls |
| Power gap tolerance | win rate ~50 % at equal power; 5–10 % power ≈ ±10–20 % win rate | How much stats dominate composition |

- **Dynamics:** composition puzzles and counter-picking; roster collection drives long-term goals; "power score" comparisons.
- **Aesthetics (MDA):** Expression (team building), Discovery, Fantasy, Submission.
- **Feedback and juice:** formation preview with synergy highlights, ultimate cut-ins, speed toggle (1×/2×/4×), win/loss breakdown screen with damage dealt per unit (essential for learning).
- **Failure modes and exploits:** one dominant composition (track pick rates; rebalance or add counters); stats overwhelm strategy (keep composition advantage worth ≥ 10–20 % power); fights end too fast to read.
- **Mobile fit:** excellent — decisions out of combat, battle is watchable and skippable; interruption-proof.
- **Monetization hooks and ethical limit:** hero collection (gacha, see `references/07-randomness-chance-mechanics.md` and `references/12-monetization-linked-mechanics.md`), upgrades; disclose odds; offer deterministic paths (shards/pity) to target units.
- **Implementation notes:** pure deterministic battle function `simulate(team_a, team_b, seed) -> BattleLog`; render from the log. Enables server validation, skip button and bot balance sweeps across all compositions.
- **Reference games:** AFK Arena, RAID: Shadow Legends, Teamfight Tactics (mobile), Hero Wars.
- **Combines well with:** `aggro-threat`, `elemental-reactions`, `status-effects`, collection (`references/09-collection-crafting-building.md`), idle rewards (`references/08-time-energy-session-mechanics.md`).

## 4. Manual skill combat

### 02.06 Cooldown abilities and ultimates — `cooldown-abilities`

- **ID:** `cooldown-abilities` · **Category:** manual combat · **Player fantasy:** "I hold the right tool for the moment — and I choose the moment."
- **Core rules:**
  - Each ability: `{cooldown, cost?, cast_time, effect, targeting}`. Usable when `cd_remaining == 0` and costs are payable. Using it sets `cd_remaining = cooldown × (1 − cdr)`.
  - Ultimates use a charge meter instead of time: gain from damage dealt, damage taken, time, or kills; full meter enables the ability.
  - Charges variant: ability stores up to N uses, one charge per `cooldown`.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Basic ability cooldown | 3–12 s | Frequency of decisions |
| Ultimate cooldown / charge time | 30–90 s | Number of peak moments per fight |
| Cooldown reduction cap | 30–45 % | Prevents permanent uptime |
| Cast time | 0–0.5 s | Commitment and interrupt windows |
| Charges | 1–3 | Burst vs sustain |
| Ability count on screen | 2–4 (mobile) | Thumb reach and cognitive load |

- **Dynamics:** resource timing, combo sequencing between abilities, baiting enemy abilities in PvP, "power spikes" when ultimates align.
- **Aesthetics (MDA):** Challenge, Fantasy, Fellowship (team ult combos).
- **Feedback and juice:** radial cooldown sweep, "ready" pulse and sound, ultimate full-screen accent; disabled-state clarity.
- **Failure modes and exploits:** CDR stacking to near-zero cooldowns; abilities so strong basic attacks become irrelevant (or vice versa); too many buttons for thumbs.
- **Mobile fit:** 2–4 ability buttons in a right-thumb arc around the attack button; drag-to-aim on the button itself.
- **Monetization hooks and ethical limit:** heroes with distinct kits; avoid selling raw cooldown reduction in PvP.
- **Implementation notes:** cooldowns as absolute "ready at tick" values rather than decrementing floats — simpler, deterministic, pause-safe.
- **Reference games:** League of Legends: Wild Rift, Mobile Legends: Bang Bang, Brawl Stars (supers), Diablo Immortal.
- **Combines well with:** `combos`, `status-effects`, `elemental-reactions`, `twin-stick-aim-assist`.

### 02.07 Combos and cancel windows — `combos`

- **ID:** `combos` · **Category:** manual combat · **Player fantasy:** "I chain moves into a flowing, devastating sequence."
- **Core rules:**
  - Attacks have frame data: `startup`, `active`, `recovery`. A combo string advances when the next input arrives within the `chain_window` of the current attack (usually during late active or early recovery).
  - Cancels: certain moves can be cancelled into others (attack → dash, attack → special) during `cancel_window`, skipping recovery.
  - Combo counter tracks consecutive hits without the target recovering; damage scaling reduces each later hit (e.g., ×0.9 per hit, floor 30–50 %) to prevent infinite damage.
  - Input buffer stores the next input for 100–200 ms so early presses still chain.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Chain window | 100–300 ms | Tight = execution skill; loose = button-mash friendly |
| Input buffer | 100–200 ms | Smoothness |
| String length | 3–5 hits | Learnability |
| Damage scaling per hit | 0.85–0.95×, floor 30–50 % | Keeps combos from deleting bosses |
| Hitstun per hit | ≥ next hit's startup to stay "true" | Whether combos are escapable |
| Finisher multiplier | 1.5–3× | Rewards completing strings |

- **Dynamics:** practice and mastery; rhythm; combo routes discovered by players; risk of committing to long strings.
- **Aesthetics (MDA):** Challenge, Expression, Sensation.
- **Feedback and juice:** combo counter growing and shaking, escalating hit sounds, hit-stop longer on finishers, camera push-in on the last hit.
- **Failure modes and exploits:** infinites (hitstun ≥ full loop time); mashing reaching the same result as skill (tighten windows or add directional inputs); touch latency making tight windows unfair (keep windows ≥ 100 ms on mobile).
- **Mobile fit:** tap-to-string on a single attack button works one-thumb; complex directional inputs do not — use button + swipe direction or context sensitivity.
- **Monetization hooks and ethical limit:** new move sets per character; do not sell longer chain windows.
- **Implementation notes:** each attack is a state with timeline; transitions table `(state, input, frame_range) → next_state`.

```text
on_input(btn): buffer = (btn, now)
step(): if buffer and now - buffer.t <= BUFFER and state.frame in state.chain_window[buffer.btn]:
          enter(state.next[buffer.btn]); buffer = null
        elif state.frame >= state.total_frames: enter(IDLE)
```

- **Reference games:** Marvel Contest of Champions, Shadow Fight 3, Mortal Kombat Mobile, Genshin Impact (normal-attack strings).
- **Combines well with:** `hitstop-hitboxes`, `knockback-poise`, `parry`, `dodge-iframes`, `cooldown-abilities`.

### 02.08 Parry and perfect block — `parry`

- **ID:** `parry` · **Category:** manual combat (defensive timing) · **Player fantasy:** "I read their strike and turn it against them."
- **Core rules:**
  - Block: holding block reduces damage by `block_mitigation` and may drain stamina/guard.
  - Parry: pressing block within `parry_window` before an incoming hit's active frame negates damage and triggers a reward: enemy stagger, counterattack window, resource gain.
  - Enemy attacks carry tags: parryable, unblockable (must dodge), feint (delayed timing).
  - Whiffed parry has recovery `parry_recovery` to punish spamming.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Parry window | 100–250 ms (mobile ≥ 150 ms recommended) | Primary difficulty |
| Whiff recovery | 200–500 ms | Anti-spam |
| Reward | stagger 1–2 s, counter ×1.5–3 | How central parrying is |
| Block mitigation | 50–100 % | Safety of turtling |
| Telegraph lead time | 300–800 ms visible wind-up | Readability |

- **Dynamics:** reading enemy animations; high-risk high-reward defensive play; mastery of specific enemies' rhythms.
- **Aesthetics (MDA):** Challenge, Sensation, Fantasy (master duelist).
- **Feedback and juice:** bright flash and distinctive metallic sound on parry, 80–150 ms hit-stop, slow-motion (0.3–0.5× for 0.2–0.4 s) on perfect parry, enemy stagger pose.
- **Failure modes and exploits:** inconsistent telegraphs across animations (author the parry timing from the hit frame, not from animation start); input latency on low-end devices; parry beating everything (add unblockables).
- **Mobile fit:** dedicated button or swipe-back gesture; works in landscape two-thumb layouts.
- **Monetization hooks and ethical limit:** none intrinsic; avoid selling wider parry windows.
- **Implementation notes:** store `parry_pressed_at`; on hit check `hit_t - parry_pressed_at <= PARRY_WINDOW`. Expose an assist option that widens windows for accessibility.
- **Reference games:** Shadow Fight 3, Marvel Contest of Champions (parry), Infinity Blade (swipe-to-parry, now delisted).
- **Combines well with:** `combos`, `knockback-poise`, `boss-encounters`, `rhythm-timing` (`references/01-verbs-movement-physics.md`).

### 02.09 Dodge and i-frames — `dodge-iframes`

- **ID:** `dodge-iframes` · **Category:** manual combat (evasion) · **Player fantasy:** "Untouchable — I slip through attacks at the last moment."
- **Core rules:**
  - Dodge input triggers a movement burst (see `dash`) with an invulnerability window `[i_start, i_end]` in which hurtboxes are disabled.
  - Recovery after the dodge during which the player is vulnerable. Optional stamina or charge cost.
  - Perfect dodge: dodging within `perfect_window` of an incoming hit grants a bonus (slow-time, counter buff).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Dodge total duration | 0.3–0.6 s | Commitment |
| I-frame span | 30–60 % of duration | Forgiveness |
| Recovery | 0.1–0.3 s | Punishes spam |
| Cost | stamina 20–35 % or 1–3 charges | Rate limit |
| Perfect-dodge window | 100–200 ms | Expert reward |

- **Dynamics:** threat timing and spacing; aggressive play enabled by reliable escape.
- **Aesthetics (MDA):** Challenge, Sensation.
- **Feedback and juice:** afterimage, translucency during i-frames, distinct "whiff" sound when an attack passes through, slow-time tint on perfect dodge.
- **Failure modes and exploits:** spam-dodging through all content (costs, recovery); i-frames invisible so deaths feel random (make the invulnerable state visible); AoE lingering longer than i-frames without clear indication.
- **Mobile fit:** swipe-to-dodge or a button near the attack button.
- **Monetization hooks and ethical limit:** none intrinsic.
- **Implementation notes:** i-frames toggle hurtbox `enabled` in the sim based on dodge frame; damage over time zones should check per tick so long hazards still hit after i-frames end.
- **Reference games:** Genshin Impact, Diablo Immortal, Dead Cells (mobile), Punishing: Gray Raven.
- **Combines well with:** `dash` (`references/01-verbs-movement-physics.md`), `bullet-patterns`, `boss-encounters`, `parry`.

### 02.10 Bullet patterns — `bullet-patterns`

- **ID:** `bullet-patterns` · **Category:** manual combat (projectile geometry) · **Player fantasy:** "I weave through a storm of beautiful, deadly geometry."
- **Core rules:**
  - Emitters spawn projectiles by pattern primitives: ring (n bullets at 360/n° steps), spread/fan (n bullets across an arc), aimed (toward player), spiral (ring with rotating offset per volley), stream (rapid aimed line), random scatter, laser (telegraphed line).
  - Each bullet: `{pos, vel, accel, angular_vel, lifetime, radius}`. Patterns layer and sequence on a timeline.
  - Player hitbox is much smaller than the sprite (often 15–30 % of sprite width), making dense patterns fair.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Bullet speed | 0.3–1.0 × player speed | Reaction time |
| Density (bullets on screen) | 20–300 | Readability and difficulty |
| Gap width in patterns | ≥ 2–3 × player hitbox | Fairness |
| Aimed vs static ratio | 20–60 % aimed | Aimed forces movement, static forces reading |
| Player hitbox size | 15–30 % of sprite | Forgiveness |
| Telegraph for lasers | 0.5–1.0 s | Fairness |

- **Dynamics:** micro-dodging; route reading; "streaming" aimed bullets by moving slowly in one direction.
- **Aesthetics (MDA):** Challenge, Sensation.
- **Feedback and juice:** high-contrast bullets with outlines against backgrounds, graze sparks for near misses (graze scoring), bullet cancel into score items on boss phase end.
- **Failure modes and exploits:** unreadable bullets on busy art (bullets must be the highest-contrast layer); finger occluding the player (use relative drag movement with offset); safe spots that trivialise patterns.
- **Mobile fit:** relative-drag control (ship moves by finger delta, not to finger position) is the standard; portrait fits vertical shmups.
- **Monetization hooks and ethical limit:** ships and options; continues; avoid selling hitbox reductions.
- **Implementation notes:** pools of struct-of-arrays bullets; circle-vs-circle collision with the player only (not bullet-vs-bullet); pattern scripts as data (`{t, emitter, primitive, n, speed, spread, rotate}`).

```text
ring(n, speed, offset): for i in 0..n-1: a = offset + i*2π/n; spawn(pos, vel=speed*(cos a, sin a))
spiral(volleys, n, speed, step_deg): for v in 0..volleys-1: at(t0 + v*dt): ring(n, speed, v*step_deg)
```

- **Reference games:** Sky Force Reloaded, Danmaku Unlimited, Archero (enemy patterns), boss patterns in Soul Knight.
- **Combines well with:** `dodge-iframes`, `boss-encounters`, `stop-to-shoot`, `projectile-upgrades`.

## 5. Build and system combat

### 02.11 Projectile upgrades — `projectile-upgrades`

- **ID:** `projectile-upgrades` · **Category:** build combat · **Player fantasy:** "Every pick makes my shots crazier — arrows split, bounce and pierce."
- **Core rules:** a base projectile `{damage, speed, count, spread, pierce, bounces, size, on_hit[]}` modified by stackable upgrades:
  - **Multishot** (+1 parallel/sequential projectile), **Front/Spread** (+n in a fan), **Diagonal/Side/Rear** (new directions), **Pierce** (+1 enemies passed), **Ricochet** (bounce to nearest enemy within r), **Wall bounce**, **Split on hit** (spawns k children), **Homing**, **Size**, **Elemental on-hit** (applies status).
  - Each extra projectile usually carries a damage penalty so count upgrades are not strictly dominant.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Per-extra-projectile damage penalty | 10–30 % | Balances count vs damage picks |
| Ricochet range / count | 3–6 wu, 1–3 bounces | Crowd clearing power |
| Pierce | +1 to +3 | Line clearing |
| Split children | 2–4 at 30–50 % damage | Exponential risk — cap generations at 1 |
| Homing turn rate | 90–360°/s | Accuracy forgiveness |
| Upgrade offer weights | rarity tiers 60/30/10 | Build variety per run |

- **Dynamics:** multiplicative synergies (count × pierce × on-hit chance); players seek "broken" combinations — design a few deliberately.
- **Aesthetics (MDA):** Fantasy (power), Discovery, Expression.
- **Feedback and juice:** each upgrade visibly changes the projectile (colour, trail, size); the player must see the build.
- **Failure modes and exploits:** exponential projectile counts killing performance (cap total live projectiles, e.g., 200–400 on mid devices, merge visuals); one upgrade strictly dominating; unreadable screens.
- **Mobile fit:** passive decision-making between fights; perfect for 1–5 min runs.
- **Monetization hooks and ethical limit:** starting upgrades or extra rerolls via rewarded ads are acceptable; avoid paid upgrades that make leaderboards meaningless.
- **Implementation notes:** compute the projectile spec by folding modifiers in a defined order (additive count first, then multipliers) and cache it on upgrade, not per shot.

```text
spec = base.copy(); for m in sorted(upgrades, key=order): spec = m.apply(spec)
fire(): for i in 0..spec.count-1: angle = aim + (i - (spec.count-1)/2) * spec.spread
          spawn(proj(spec, angle, damage = spec.damage * (1 - PENALTY)^(spec.count-1)))
```

- **Reference games:** Archero (Multishot, Front Arrow, Ricochet, Piercing, Diagonal Arrows), Vampire Survivors (weapon levels), Brotato.
- **Combines well with:** `stop-to-shoot`, `auto-aim-survivors`, `status-effects`, `elemental-reactions`.

### 02.12 Crowd and mob combat (count armies) — `crowd-mob-combat`

- **ID:** `crowd-mob-combat` · **Category:** build combat (numbers as power) · **Player fantasy:** "My army swells into a stampede that crushes everything."
- **Core rules:**
  - The player's force is an integer `N` of identical units (crowd). HP and damage are `N` itself: when crowds collide, both lose units one-for-one until one side is zero.
  - **Gates** modify `N` arithmetically (`+k`, `−k`, `×k`, `÷k`); the player steers left/right to pick gates. Obstacles (saws, pits) remove units on contact.
  - End-of-level battle: final crowd vs boss/army or climb a "tower" scored by how far `N` reaches.
  - Shooter variant (mob control): a cannon fires units; units passing through multiplier gates multiply; units reach the enemy base.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Gate values | +5 to +50, ×2 to ×5, −10 to −50, ÷2 | Big-number thrill vs penalty |
| Good-vs-bad gate pairing | choose 1 of 2, ~60–80 % levels have a "trap" pair | Decision content |
| Obstacle kill rate | 5–30 % of crowd per obstacle | Steering skill |
| Final battle size | tuned so optimal path wins with 20–50 % margin | Win rate |
| Crowd render cap | 100–300 visible units; show a number beyond | Performance |

- **Dynamics:** quick arithmetic decisions under motion; "multiplier first, then addition" optimisation; crowd shape squeezing past obstacles.
- **Aesthetics (MDA):** Sensation (swarm), Fantasy (power), Challenge (light).
- **Feedback and juice:** crowd count above the blob with pop on change, units visibly spawning, satisfying collision "absorption" with poofs.
- **Failure modes and exploits:** trivial choices (always one obvious gate); unreadable numbers at speed (big font, 1–2 s reading time per gate); performance with hundreds of skinned meshes (GPU instancing, vertex animation textures).
- **Mobile fit:** one-thumb drag steering in portrait; 30–60 s levels; core hybrid-casual pattern.
- **Monetization hooks and ethical limit:** starting crowd upgrades, skins, rewarded ads for multipliers; misleading ads showing gameplay that does not exist in the game are a known reputational and store-policy risk.
- **Implementation notes:** simulate `N` as an integer; spawn visual units as a flocking crowd (boids-lite: cohesion to the leader, separation by grid) capped at render limit. Collision battle resolves numerically over 0.5–2 s for drama.
- **Reference games:** Count Masters, Mob Control, Crowd City (absorption variant).
- **Combines well with:** `auto-run-lanes` (`references/01-verbs-movement-physics.md`), upgrade economies (`references/04-economy-resource-mechanics.md`), `wave-director`.

### 02.13 Elemental reactions — `elemental-reactions`

- **ID:** `elemental-reactions` · **Category:** combat system · **Player fantasy:** "I combine forces of nature — fire meets water and the battlefield transforms."
- **Core rules:**
  - Attacks carry an element. Hitting a target applies an **aura** (element + gauge amount, decaying over time).
  - Hitting an aura'd target with a different element triggers a **reaction** from an interaction table, consuming some or all of the gauge. Reaction families: **amplify** (multiply the trigger hit), **transform** (separate burst damage or effect), **control** (freeze, root), **spread** (copies auras to nearby enemies), **shield** (grants protection).
  - Environmental elements: wet ground conducts electricity, fire burns grass, ice freezes water.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Number of elements | 3–7 | Combinatorial depth: n(n−1)/2 pairs |
| Aura duration | 3–12 s | How long a setup stays available |
| Amplify multiplier | 1.5–2× | Payoff for ordering |
| Transform reaction damage | scales with level, not attack | Lets support characters contribute |
| Reaction internal cooldown | 0.5–2.5 s per target | Prevents reaction spam |

- **Dynamics:** team composition around reaction pairs; ordering matters (who applies the aura vs who triggers); environmental puzzles in combat.
- **Aesthetics (MDA):** Discovery, Expression, Fantasy.
- **Feedback and juice:** element icon over enemy heads showing current aura, reaction name text burst, distinctive colour per reaction, environmental VFX (steam, sparks).
- **Failure modes and exploits:** too many elements to read (start with 3–4); one reaction dominating; aura stacking ambiguity (define clear rules: one aura at a time or explicit co-existence).
- **Mobile fit:** works with auto and manual combat; reaction icons must be legible on 6" screens.
- **Monetization hooks and ethical limit:** characters of each element drive collection; ensure free/fixed options cover every element so reactions are not paywalled.
- **Implementation notes:** reaction table as data `{(aura, trigger): {type, multiplier|effect, gauge_cost}}`; resolve in the hit pipeline after crit and before mitigation (or per your damage order — document it).
- **Reference games:** Genshin Impact (Vaporize and Melt amplify, Overloaded and Swirl transform, Freeze control), Honkai: Star Rail (weakness breaks, related idea), Magicka (spell element combination).
- **Combines well with:** `status-effects`, `auto-battle-squad`, `cooldown-abilities`, puzzle grids (`references/03-puzzle-mechanics.md`).

### 02.14 Status effects — `status-effects`

- **ID:** `status-effects` · **Category:** combat system · **Player fantasy:** "I don't just hit harder — I poison, freeze and weaken."
- **Core rules:**
  - A status is `{id, source, magnitude, duration, tick_interval?, stacks, max_stacks, stack_rule, tags}`.
  - Families: **damage over time** (burn, poison, bleed), **crowd control** (stun, freeze, root, slow, silence, knock-up), **stat modifiers** (armor break, vulnerability +x % damage taken, attack up), **special** (mark, taunt, cleanse-immune).
  - Stack rules must be explicit: `refresh` (reset duration), `extend` (add duration up to cap), `intensity` (add magnitude per stack), `independent` (each application tracks its own timer), `strongest-wins`.
  - Diminishing returns for CC: repeated CC on the same target within `dr_window` lasts ×0.5, ×0.25, then immune.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| DoT total as % of hit | 50–150 % over 3–6 s | Value of DoT builds |
| Tick interval | 0.5–1 s | Readability of numbers |
| Hard CC duration | 0.5–2 s (PvP), up to 4 s (PvE) | Frustration vs control |
| CC diminishing returns | ×0.5 per repeat in 10–15 s | Prevents CC lock |
| Max stacks | 5–10 for intensity stacks | Ceiling of stacking builds |
| Boss CC resistance | immune or ×0.25–0.5 duration | Keeps bosses dangerous |

- **Dynamics:** setup-and-payoff (apply vulnerability then burst), cleanse vs apply tug-of-war, DoT kiting.
- **Aesthetics (MDA):** Challenge, Discovery, Expression.
- **Feedback and juice:** status icons with radial timers and stack counts on health bars, colour tint on afflicted units, distinct number colours for DoT ticks.
- **Failure modes and exploits:** perma-stun chains; unclear stack rules causing bug reports; too many icons (show top 3, collapse rest); DoT on bosses dominating all builds.
- **Mobile fit:** passive and readable; icons ≥ 16–20 dp.
- **Monetization hooks and ethical limit:** none intrinsic; avoid paid CC immunity in PvP.
- **Implementation notes:** keep statuses in a per-entity list processed each tick in a fixed order (expire → tick → recompute stats). Recompute derived stats from base + modifiers each change, never mutate base stats.

```text
apply(target, s): ex = target.find(s.id, s.source if s.independent else any)
  match s.stack_rule: refresh → ex.duration = s.duration | extend → ex.duration = min(ex.duration + s.duration, CAP)
                      intensity → ex.stacks = min(ex.stacks + 1, s.max_stacks); ex.duration = s.duration
  if ex is null: target.add(s); if s.is_cc: s.duration *= dr_factor(target, s.cc_family)
```

- **Reference games:** RAID: Shadow Legends (buff/debuff-heavy turn combat), Diablo Immortal, Slay the Spire mobile (Vulnerable, Weak, Poison), Genshin Impact.
- **Combines well with:** `elemental-reactions`, `projectile-upgrades`, `auto-battle-squad`, `aggro-threat`.

### 02.15 Damage model, crits and armor — `damage-model`

- **ID:** `damage-model` · **Category:** combat system · **Player fantasy:** "My choices show up in the numbers — big, satisfying numbers."
- **Core rules:** a documented damage pipeline, applied in fixed order:
  1. Base = attack stat × skill multiplier (+ flat bonuses).
  2. Additive bonus bucket (all "+x % damage" summed), then separate multiplicative buckets (crit, elemental amplify, vulnerability).
  3. Crit: with probability `crit_rate`, multiply by `crit_mult`.
  4. Mitigation: `× 100 / (100 + armor_after_penetration)`, then resistances.
  5. Variance, floor (`min 1`), shields absorb before HP.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Crit rate (base → cap) | 5 % → 50–75 % | Burstiness and build identity |
| Crit multiplier | 1.5–2.5× | Size of spikes |
| Armor value at which mitigation = 50 % | 100 (with the 100/(100+a) form) | Scale of defensive stats |
| Penetration | flat and % | Counter to armor stacking |
| Bucket separation | additive vs multiplicative per source | Prevents runaway scaling |
| Damage number abbreviation | 1.2K, 3.4M, 5.6B | Readability at idle scales |

- **Dynamics:** build optimisation; balanced crit rate × crit damage maximises expected DPS when both share a budget; stat breakpoints (one-shot thresholds) become goals.
- **Aesthetics (MDA):** Challenge (build), Fantasy (power), Discovery.
- **Feedback and juice:** crit numbers larger, different colour, with shake; "weak/resisted" text; DPS meters in results screens.
- **Failure modes and exploits:** multiplicative stacking of everything (exponential power, impossible to balance); flat armor making early units useless; hidden formulas causing distrust (show tooltips with effective values).
- **Mobile fit:** neutral; keep numbers short and legible.
- **Monetization hooks and ethical limit:** stat upgrades are the classic sink; publish the formula basics so players can make informed purchases.
- **Implementation notes:** the pipeline is one pure function with unit tests per bucket; log every hit's breakdown in debug builds for balance work.

```text
dmg = atk * skill_mult + flat
dmg *= (1 + sum(additive_bonuses)); for m in multiplicative: dmg *= m
if rng.chance(crit_rate): dmg *= crit_mult; crit = true
dmg *= 100 / (100 + max(armor * (1 - pen_pct) - pen_flat, 0)); dmg = max(round(dmg), 1)
```

- **Reference games:** Diablo Immortal, League of Legends: Wild Rift (armor formula family), Clash of Clans (flat DPS clarity as a contrast), idle RPGs with abbreviated numbers such as Tap Titans 2.
- **Combines well with:** `status-effects`, `elemental-reactions`, upgrade economies (`references/04-economy-resource-mechanics.md`), progression (`references/05-progression-meta-mechanics.md`).

### 02.16 Aggro and threat — `aggro-threat`

- **ID:** `aggro-threat` · **Category:** combat system (AI targeting) · **Player fantasy:** "My tank holds the line so my damage dealers can shine."
- **Core rules:**
  - Each enemy keeps a threat table `{entity: threat}`. Threat accrues from damage (×1), healing (×0.5 split across enemies), and taunt abilities (set to top + margin, or force-target for `t`).
  - Enemy targets the highest threat; switches only if a new entity exceeds current target's threat by `switch_margin` (e.g., 10 % melee, 30 % ranged).
  - Simpler mobile alternatives: position-based (front row is attacked first), role-based (assassins jump to back row), or random weighted.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Taunt duration | 2–5 s | Control strength |
| Switch margin | 10–30 % | Stability of targeting |
| Threat decay | 0–5 %/s | How quickly mistakes are forgiven |
| Healing threat factor | 0.3–0.6 | Healer risk |
| Front-row targeting share | 60–90 % (formation model) | Tank importance |

- **Dynamics:** role differentiation (tank, damage, healer); protection puzzles; enemies with "ignore aggro" abilities as counters.
- **Aesthetics (MDA):** Fellowship (roles), Challenge, Expression.
- **Feedback and juice:** target lines or icons over the attacked unit, taunt shout VFX, warning when a squishy is targeted.
- **Failure modes and exploits:** ping-pong targeting (add margin); invisible rules causing "AI is dumb" complaints; tanks irrelevant because enemies ignore threat too often.
- **Mobile fit:** automated systems hide complexity well; show only the result (who is being attacked).
- **Monetization hooks and ethical limit:** none intrinsic.
- **Implementation notes:** threat tables are small (≤ 10 entries); update on hit events; choose target on a decision tick (0.25–0.5 s) for stability and performance.
- **Reference games:** AFK Arena (formation-based targeting), RAID: Shadow Legends (taunt), World of Warcraft (threat model origin for many designers).
- **Combines well with:** `auto-battle-squad`, `status-effects`, `boss-encounters`.

## 6. Defense, waves and encounters

### 02.17 Tower targeting — `tower-targeting`

- **ID:** `tower-targeting` · **Category:** defense · **Player fantasy:** "I build a perfect killing machine and watch it work."
- **Core rules:**
  - Each tower has `{range, fire_rate, damage, projectile/instant, splash, effects, targeting_priority}`.
  - Valid targets: enemies within range and line-of-fire. Priority rules: **First** (furthest along the path), **Last**, **Strong** (highest HP or threat), **Weak**, **Close**, plus camo/flying rules requiring detection.
  - Path progress is computed as distance travelled along the path, not straight-line distance to the exit.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Range | 2–6 tiles | Placement importance |
| Fire rate | 0.3–5 shots/s | Feel; on-hit effect scaling |
| Splash radius | 0–1.5 tiles | Crowd handling |
| Projectile travel time | instant – 0.5 s | Misses against fast enemies (lead targeting) |
| Player-selectable priority | on/off | Strategic depth vs simplicity |
| Upgrade paths | 2–3 branches × 3–5 tiers | Long-term choices |

- **Dynamics:** chokepoint placement; complementary roles (slow + splash, detect + damage); efficiency maths per coin.
- **Aesthetics (MDA):** Challenge, Expression, Submission.
- **Feedback and juice:** range circle on placement, tower turning to track, muzzle flashes, overkill numbers suppressed (only show kills), wave-cleared fanfare.
- **Failure modes and exploits:** overkill waste (multiple towers firing at a nearly dead enemy — reserve predicted damage per target); one dominant tower; maze exploits in free-placement maps (ensure a path always exists; validate on placement).
- **Mobile fit:** tap to place, tap tower to upgrade; perfect for portrait or landscape; pause and 2× speed controls.
- **Monetization hooks and ethical limit:** premium towers and heroes; in PvE that is acceptable if levels are beatable with free towers.
- **Implementation notes:** precompute path distance per waypoint segment; enemy `progress` = segment base distance + offset. Overkill guard: `pending_damage[target]` incremented on fire, decremented on hit.

```text
candidates = enemies_in_range(tower) filtered by detection and (hp - pending_damage) > 0
target = max(candidates, key = {FIRST: progress, LAST: -progress, STRONG: hp, CLOSE: -dist})
fire(target); pending_damage[target] += expected_damage
```

- **Reference games:** Bloons TD 6 (First/Last/Close/Strong priorities), Kingdom Rush, Plants vs. Zombies (lane variant).
- **Combines well with:** `wave-director`, `lane-defense`, `status-effects`, build-and-upgrade economies (`references/04-economy-resource-mechanics.md`).

### 02.18 Lane defense — `lane-defense`

- **ID:** `lane-defense` · **Category:** defense · **Player fantasy:** "Hold the line — every lane counts."
- **Core rules:**
  - Grid of `rows × columns`; enemies enter from one side along a row and walk to the other. Defenders are placed in cells, attacking along their row (or adjacent rows).
  - A placement resource accrues over time and from producer units; each defender has a cost and a placement cooldown.
  - Enemy reaching the end = lose (or lose a life/lawnmower once per lane as a safety).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Grid size | 5 rows × 9 columns is the classic | Spatial complexity |
| Resource income | producers + passive drip | Economy vs defense tension |
| Defender costs | 50–300 resource units | Build order pacing |
| Placement cooldown | 5–30 s per type | Prevents spam of best unit |
| Per-lane safety | one-use clear per lane | Forgiveness |

- **Dynamics:** economy-vs-defense opening (invest in producers early, survive first waves); lane prioritisation; unit counters by enemy type.
- **Aesthetics (MDA):** Challenge, Expression, Fantasy (charm).
- **Feedback and juice:** resource pickups with tap-to-collect, defender idle animations, enemy hit reactions, flag/wave progress bar.
- **Failure modes and exploits:** one solved layout for every level (vary lane count, hazards, enemy mixes); too-slow openings (shorten pre-wave time).
- **Mobile fit:** tap-select then tap-place; portrait or landscape; short levels (3–6 min).
- **Monetization hooks and ethical limit:** premium plants/heroes, boosters; keep main path beatable with earned units.
- **Implementation notes:** per-row enemy lists sorted by x; defenders query only their row (cheap); seeded wave scripts per level for deterministic playthrough tests.
- **Reference games:** Plants vs. Zombies, Plants vs. Zombies 2, Clash Royale (lane-based duel, real-time PvP).
- **Combines well with:** `tower-targeting`, `wave-director`, generators (`references/04-economy-resource-mechanics.md`).

### 02.19 Wave spawning and director — `wave-director`

- **ID:** `wave-director` · **Category:** encounter pacing · **Player fantasy:** "The pressure builds and breaks like a story — and I survive it."
- **Core rules:**
  - **Scripted waves:** a list of `{t, enemy_type, count, spawn_point, interval}` per level (TD, lane defense).
  - **Budget director:** every tick the director earns `budget += rate(t)`; it buys spawns from a weighted enemy menu (`cost`, `weight`, `min_time`) at valid spawn points, respecting caps (`max_alive`, per-type caps).
  - **Intensity tracking (adaptive):** an intensity estimate rises with damage taken and nearby enemies, decays over time; when it exceeds a peak threshold, the director enters a relax phase (no spawns for `relax_t`), creating build-up → peak → relax cycles.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Budget rate curve | linear or stepped +10–25 % per minute | Overall ramp |
| Max alive enemies | 30–600 (device-bound) | Pressure and perf |
| Relax duration | 3–15 s | Breathing room, loot pickup |
| Spawn distance | just off-screen (1.1–1.3× screen radius) | Fairness and surprise |
| Elite/boss insertion | every 1–3 min or on budget threshold | Peaks and set pieces |
| Wave preview | none / next-wave icons | Planning depth in TD |

- **Dynamics:** tension curves; players learn to exploit relax windows; spawn pressure shapes movement routes.
- **Aesthetics (MDA):** Challenge, Sensation, Narrative (rhythm of a level).
- **Feedback and juice:** wave banners, warning arrows at screen edges for incoming elites, music intensity layers tied to director state.
- **Failure modes and exploits:** spawns on top of the player (minimum spawn distance + visibility check); unbounded budgets (cap); death spirals when players fall behind (adaptive budget if the design allows DDA — see `progression-difficulty`).
- **Mobile fit:** waves sized to 1–5 min sessions; pause-safe.
- **Monetization hooks and ethical limit:** revives at failure points; never increase spawn pressure for payers' opponents or secretly against non-payers.
- **Implementation notes:** the director is a deterministic system seeded per run; log its state each second for balance graphs.

```text
step(dt): budget += rate(t) * dt; intensity = intensity*decay + damage_taken*k1 + nearby*k2
  if phase == BUILD and intensity > PEAK: phase = RELAX; relax_until = t + RELAX_T
  if phase == RELAX and t > relax_until: phase = BUILD
  while phase == BUILD and alive < MAX_ALIVE and (e := pick_affordable(menu, budget, t)): budget -= e.cost; spawn(e)
```

- **Reference games:** Vampire Survivors (time-scripted waves), Kingdom Rush (scripted waves with previews), Left 4 Dead (the AI Director as the canonical adaptive model; not mobile).
- **Combines well with:** `auto-aim-survivors`, `tower-targeting`, `lane-defense`, `elite-affixes`, `boss-encounters`.

### 02.20 Boss encounters — `boss-encounters`

- **ID:** `boss-encounters` · **Category:** encounter design · **Player fantasy:** "A towering challenge I learn, then conquer."
- **Core rules:**
  - Boss = state machine of **phases** gated by HP thresholds (e.g., 70 %, 40 %, 15 %) or time. Each phase has an attack pool with weights and cooldowns.
  - Every attack has a **telegraph** (wind-up animation, ground marker, sound) of `t_tell` before the active frames, and a **punish window** after.
  - Optional mechanics: adds (summoned minions), weak points, enrage timer (damage up after `t_enrage`), invulnerable transitions (cinematic, not damage sponges).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Fight length | 45–180 s on mobile | Session fit and fatigue |
| Phases | 2–4 | Escalation |
| Telegraph time | 0.5–1.5 s (shorter in later phases) | Fairness |
| Punish window | 1–3 s after big attacks | Rhythm of offense/defense |
| Attack repetition guard | no same attack > 2× in a row | Variety |
| Enrage timer | 2–4× expected kill time | Prevents stalling |

- **Dynamics:** pattern learning across attempts; build checks (DPS, mobility); spectacle peaks.
- **Aesthetics (MDA):** Challenge, Fantasy, Narrative.
- **Feedback and juice:** boss HP bar with phase notches, phase-change cinematic of 1–2 s, screen shake on slams, music change per phase, huge death sequence and loot shower.
- **Failure modes and exploits:** HP sponges (raise threat, not HP); unreadable telegraphs on small screens (use ground markers with high contrast); safe spots; boss stuck on geometry; difficulty spikes far above surrounding content (check win rates per attempt).
- **Mobile fit:** shorter fights, clear telegraphs, generous punish windows; boss rushes as a separate mode.
- **Monetization hooks and ethical limit:** revives and boss-specific boosts; do not tune bosses as hidden paywalls — publish recommended power and offer free paths.
- **Implementation notes:** attack selection = weighted random over the phase pool excluding attacks on cooldown and the last-used attack if repeated twice; seed per attempt for reproducible playthrough tests.
- **Reference games:** Archero (chapter bosses), Shadow Fight 3, Genshin Impact (weekly bosses), Infinity Blade.
- **Combines well with:** `bullet-patterns`, `parry`, `dodge-iframes`, `wave-director`, `cooldown-abilities`.

### 02.21 Hordes, elites and affixes — `elite-affixes`

- **ID:** `elite-affixes` · **Category:** encounter variety · **Player fantasy:** "Every fight is a little different — and some enemies are terrifying."
- **Core rules:**
  - Base enemy archetypes (5–8: chaser, ranged, tank, swarm, exploder, healer/buffer, charger, summoner) cover tactical roles.
  - **Elites** = base archetype + 1–3 **affixes** drawn from a pool (fast, shielded, vampiric, explodes on death, splits, teleports, reflects, frenzied allies).
  - Affix rules state stacking and exclusions (e.g., "reflect" excluded with "splits").
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Elite frequency | 1 per 20–60 normal enemies or per wave | Pacing peaks |
| Affixes per elite | 1–3 (scaling with depth) | Threat complexity |
| Elite HP multiplier | 3–10× base | Fight length |
| Affix exclusion pairs | design-specified | Avoids unfair combos |
| Reward multiplier | 3–5× base drops | Risk-reward |

- **Dynamics:** threat prioritisation, adaptive builds; combinatorial variety from small content (8 archetypes × 12 affixes × pairs ≈ hundreds of variants).
- **Aesthetics (MDA):** Challenge, Discovery.
- **Feedback and juice:** coloured outline or aura per elite, affix icons above HP bar, unique spawn sound.
- **Failure modes and exploits:** unfair combinations (fast + ranged + reflect); unreadable affix icons; affixes hard-countering certain builds with no counterplay.
- **Mobile fit:** variety without content cost, ideal for small teams.
- **Monetization hooks and ethical limit:** none intrinsic.
- **Implementation notes:** affixes as composable components (`on_spawn`, `on_hit`, `on_damaged`, `on_death`, `stat_mods`) attached to the base entity; generate elites by seeded draw with exclusion checks.
- **Reference games:** Diablo Immortal (champion and elite affixes), Hades (Elite armor and modifiers), Brotato (elite waves).
- **Combines well with:** `wave-director`, `auto-aim-survivors`, `status-effects`, randomness (`references/07-randomness-chance-mechanics.md`).

## 7. Hit resolution layer

### 02.22 Hit-stop, hitboxes and hurtboxes — `hitstop-hitboxes`

- **ID:** `hitstop-hitboxes` · **Category:** hit resolution (mechanical layer) · **Player fantasy:** "When I hit, it lands — I feel it, and it's fair."
- **Core rules:**
  - **Hitboxes** are active shapes attached to attacks, enabled only during active frames. **Hurtboxes** are vulnerable shapes on characters (can differ per state: smaller while dodging, larger on wind-up). A hit occurs when a hitbox overlaps a hurtbox of an opposing team and that pair has not already hit during this attack instance.
  - **Hit-stop (freeze frames):** on a successful hit, both attacker and target pause their animation and simulation for `t_stop` (scaled by damage); the world may continue or also pause.
  - Hit priority: when two hitboxes collide (clash), resolve by priority value or cancel both.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Hit-stop, light hit | 2–4 frames (33–67 ms) | Impact without sluggishness |
| Hit-stop, heavy/finisher | 6–12 frames (100–200 ms) | Weight |
| Hit-stop scaling | `t = base + k × damage/max_hp`, capped | Proportional feel |
| Player hurtbox vs sprite | 60–90 % in action, 15–30 % in bullet hell | Forgiveness |
| Enemy hurtbox vs sprite | 100–120 % | Hits feel generous |
| Multi-hit rehit interval | 0.1–0.5 s for persistent hitboxes | DPS of lingering attacks |

- **Dynamics:** precise spacing; trust in the rules (players learn true ranges); hit-stop also creates input-buffer room for combos.
- **Aesthetics (MDA):** Sensation, Challenge.
- **Feedback and juice:** hit-stop + 1–2 frame white flash + directional particles + sound with layered transient. (The sensory side is in `game-feel`; here it is a rule of the simulation.)
- **Failure modes and exploits:** hitboxes larger than visuals (feels cheap); hurtboxes lagging animation; hit-stop on every tiny hit in hordes (disable for DoT and small hits); multi-hit bugs when the same attack hits twice.
- **Mobile fit:** generous hitboxes compensate for small screens and touch imprecision.
- **Monetization hooks and ethical limit:** none.
- **Implementation notes:** keep a `hit_registry[attack_instance_id]` set of struck targets. Implement hit-stop as a per-entity `frozen_until` tick in the sim (deterministic), not a global time-scale hack, unless the whole game should freeze.

```text
for hb in active_hitboxes: for hu in query_overlaps(hb.shape, layer=enemy_hurt):
  if hu.owner in hit_registry[hb.attack_id]: continue
  hit_registry[hb.attack_id].add(hu.owner); apply_hit(hb, hu)
  stop = min(BASE + K * dmg / hu.owner.max_hp, MAX); hb.owner.frozen_until = hu.owner.frozen_until = tick + stop
```

- **Reference games:** Shadow Fight 3, Marvel Contest of Champions, Dead Cells (mobile), Street Fighter-lineage fighting games as the source of frame-data vocabulary.
- **Combines well with:** `combos`, `knockback-poise`, `parry`, `dodge-iframes`.

### 02.23 Knockback, stagger and poise — `knockback-poise`

- **ID:** `knockback-poise` · **Category:** hit resolution · **Player fantasy:** "My blows send them flying; their big hits rock me."
- **Core rules:**
  - Each attack has `knockback` (impulse vector or distance) and `poise_damage`. Each entity has `poise` (stagger threshold) that regenerates after `poise_regen_delay`.
  - When accumulated poise damage exceeds poise → **stagger** (interrupt current action, stun for `t_stagger`), then poise resets. Super-armor states ignore stagger (but still take damage).
  - Knockback applies as velocity with friction or as a fixed-distance displacement; wall impacts can add bonus damage ("wall splat").
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Knockback distance | 0.5–3 wu (light to heavy) | Spacing control, crowd management |
| Poise (enemy) | fodder 1 hit, elite 3–6 hits, boss break bar | Interruptibility |
| Stagger duration | 0.3–1.5 s (boss break 3–6 s) | Reward size |
| Poise regen delay | 1–3 s | Need for sustained pressure |
| Knockback resistance (heavy units) | 0–100 % | Unit identity |

- **Dynamics:** crowd control by positioning (knock enemies into hazards, off ledges); break-bar windows on bosses as damage phases; trading hits based on poise.
- **Aesthetics (MDA):** Sensation, Challenge, Fantasy.
- **Feedback and juice:** directional hit reaction animations, dust trails on slide-back, stagger stars or "BREAK" text, slow-motion on boss break.
- **Failure modes and exploits:** infinite stagger-lock (poise immunity window after stagger); knocking enemies out of reach (prefer short knockback, or tether); knockback pushing through walls (sweep test).
- **Mobile fit:** knockback makes melee readable on small screens; break bars give clear goals.
- **Monetization hooks and ethical limit:** none intrinsic.
- **Implementation notes:** resolve knockback in the movement phase after hits, using the same collision sweep as player movement; poise as float with regen tick.
- **Reference games:** Genshin Impact (poise/interruption), Honkai: Star Rail (toughness break, turn-based variant), Diablo Immortal, Punishing: Gray Raven.
- **Combines well with:** `hitstop-hitboxes`, `combos`, `boss-encounters`, `ragdoll` (`references/01-verbs-movement-physics.md`).

## 8. Combat balance checklist

Use before any combat feature passes design review:

- [ ] TTK table written for fodder, elite, boss, and player-under-pressure, with the formulas above.
- [ ] Damage pipeline order documented and unit tested; every multiplicative bucket justified.
- [ ] Every enemy attack has a telegraph ≥ 0.4 s (mobile) unless it is trivial chip damage.
- [ ] Status stacking rules and CC diminishing returns specified per status.
- [ ] Spawn director logs exported per second; bot runs show the intended build-up/peak/relax shape.
- [ ] Projectile and enemy caps set per device tier, verified in `mobile-performance` profiling.
- [ ] Monetized power has an explicit ceiling relative to skill (document it in the contract `monetization.ethics`).
- [ ] Deterministic seeds for all combat randomness so the playthrough gate can replay fights.
