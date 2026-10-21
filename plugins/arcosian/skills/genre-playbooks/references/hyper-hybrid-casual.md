# Hypercasual and Hybrid-Casual Playbooks

Hypercasual games put marketability first. A single verb has to be readable in a 3-second ad, monetization is almost entirely ads, the meta is minimal, and the business model works only if install cost stays below ad lifetime value. Hybrid-casual keeps that accessible core and adds a meta layer: persistent progression, collections, IAP and events, which add retention and spend. Money has followed that shift. Hybrid-casual spending grew 17.1% in 2025 [V1]. The archetypal hypercasual prototype factory has moved from testing about 1,000 prototypes a year to about four hybrid-casual launches a year [V3]. This file covers six hypercasual archetypes (stack, runner, io, cut/slice, draw, idle-arcade) and four hybrid-casual patterns (runner + meta, arcade idle, casual survivor-like, puzzle + RPG), in the 14-part format from `SKILL.md`. KPI ranges appear only where sourced, tagged `[Vn]` and listed at the end. Team and time figures are labelled estimates.

## Contents

| # | Playbook | Type | AB (1–5) | Lead monetization |
|---|---|---|---|---|
| 0 | Shared conventions: marketability tests and ad unit economics | — | — | — |
| 1 | Stack (one-tap timing) | Hypercasual | 4 | Ads |
| 2 | Runner (gates and crowds) | Hypercasual | 4 | Ads |
| 3 | io (arena growth) | Hypercasual | 3 | Ads + skins |
| 4 | Cut / slice | Hypercasual | 3 | Ads |
| 5 | Draw (draw-to-solve) | Hypercasual | 3 | Ads |
| 6 | Idle-arcade (carry and unlock) | Hypercasual | 4 | Ads |
| 7 | Runner + meta | Hybrid | 4 | Ads + IAP |
| 8 | Arcade idle (management) | Hybrid | 4 | Rewarded + IAP |
| 9 | Casual survivor-like | Hybrid | 3 | IAP + rewarded |
| 10 | Puzzle + RPG | Hybrid | 4 | IAP (heroes) |
| 11 | Volatile facts used in this file | — | — | — |

## 0. Shared conventions: marketability tests and ad unit economics

- **Test marketability before you build content.** Make 3–5 short gameplay videos or a playable ad of the core verb, run a small paid test, and compare click-through, installs per thousand impressions (IPM) and cost per install (CPI) against your own previous tests. A playable that wins the test becomes the slice. Commercial vendors now generate playable ads from performance data [V5]. `marketing-ua` holds the method.
- **Ad unit economics.**
  - `ARPDAU_ads = Σ_placements (impressions per DAU × eCPM / 1000)`.
  - `LTV ≈ ARPDAU × Σ_{d=0..H} retention(d)`, using `${CLAUDE_PLUGIN_ROOT}/scripts/retention_ltv.py ltv --points ... --arpdau A`.
  - The game is viable only if LTV is greater than CPI at scale.
  - *Illustrative arithmetic, not benchmarks:* with an ARPDAU of $0.05 and a fitted curve summing to 4 retained days over 180 days, LTV is $0.20, so CPI must stay under $0.20.
- **Ad placement rules** (`monetization`):
  - Rewarded ads are opt-in, always worth it, and offered at natural moments: continue, multiply the reward, speed boost.
  - Interstitials only at run end, after the first few runs, with a remote-config minimum interval.
  - Banners only where they do not cover the play area.
  - A "no ads" IAP is standard. It removes interstitials and banners but usually keeps rewarded ads as opt-in.
- **Mediation.** In 2025, AppLovin MAX held 55% of top-grossing ad-monetized games, LevelPlay 25% and AdMob 13.3% [V6]. Bidding is now the standard path [V7]. Treat the ad stack as config, not code.
- **Region.** Ads are 70.3% of game revenue in India but 22.1% in the US [V8]. An ad-led hypercasual game in mature markets competes against IAP-heavy hybrids for the same users.
- **Ethics.** Show only real gameplay in ads. Never fake a "real players" claim when the opponents are bots. Give a clear close button on every interstitial.

## 1. Stack (one-tap timing)

**Definition and player fantasy.** Tap at the right moment to place a moving block on a growing tower. Any overhang is trimmed, so misses shrink the next block. Variants include descending through a helix or smashing down a stack. The fantasy is rhythm and precision: a zen flow state that turns into a tall tower worth bragging about.

**Core loop** (seconds). A block slides in → tap → placement and trim → a perfect hit adds a streak and restores width → the next block arrives faster → a miss to zero width ends the run → score → restart, with an ad or continue offer.

**Meta loops.**
- High score and daily best, with an optional global or friends leaderboard.
- Unlockable skins and colour themes at score thresholds, which give a light collection goal.
- In some variants, a level mode with target heights. It gives a sense of progress that a pure endless mode lacks.

**Session profile** (estimate). Runs of 30 seconds to 2 minutes, many runs per session, many short sessions a day.

**Signature mechanics** (`mechanics-codex`: timing, progression-unlocks, customization).

| Parameter | Starting value to tune (heuristic) | Effect |
|---|---|---|
| Base speed | Comfortable for a first-time player | First-run success |
| Speed ramp | Small increase per block, capped | Run length |
| Perfect window | A generous number of ms around exact alignment | Streak frequency |
| Width restore on streak | Restore some width after N perfects | Comeback hope |
| Colour gradient | Shifts every N blocks | Sense of progress without UI |

- Input latency matters more here than almost anywhere else. Measure tap-to-response time on low-end Android.
- Trim geometry and falling offcuts are cheap physics that are disproportionately satisfying.

**Monetization model and typical mix.** Interstitials after every N runs (remote config), a rewarded continue (once per run), a no-ads IAP and skin packs.

**KPI expectations.** Hyper-casual D1 is cited at about 33% to 40%, but the sources disagree and may trace back to 2022 data [V4]. Use it only as a rough screen. Qualitatively, D7 and D30 are weak unless a meta is added.

**Retention drivers.**
- Beating your best score.
- Flow-state "one more run".
- Skin unlocks at score thresholds.
- Daily goals.

**Content pipeline and production scope** (estimates).
- Content is procedural. The art is minimal: shaders, gradients and particles matter more than assets.
- The audio needs a pitched note ladder plus impact and fail sounds, and it carries much of the feel.
- Slice: 1 person plus agents, 3–10 days. Soft-launch test build: 1–3 people, 2–6 weeks.
- Run the marketability test (section 0) before investing in the meta. A weak CPI kills the concept regardless of polish.

**Reference titles.** Stack (Ketchapp), Helix Jump (Voodoo), Stack Ball-style smashers.

**What makes it succeed / fail.**
- Succeeds: instant readability in an ad, tight input latency, and a satisfying sound ladder on perfects.
- Succeeds: a gorgeous minimal aesthetic.
- Fails: input lag on low-end devices, and difficulty that jumps rather than ramps.
- Fails: an interstitial after every run from the first session.

**Innovation vectors.**
- Rhythm-synced stacking (`narrative-rhythm-edu-kids.md`).
- Asynchronous ghost races.
- A hybrid meta: build a city from your towers.
- Haptic-led feel.

**Agent-buildability: 4/5.** The simulation is deterministic, with tap times injected in scripts, and the art is minimal. A bot that taps at the alignment time plus noise measures how run length depends on skill. A point is lost because the feel (latency, sound ladder) needs human and device checks, and timing tolerance is moderate [V9].

**Starter feature list (P0 vertical slice).**
1. Block slider — alternating-axis slide; position is a pure function of time, so it is testable.
2. Tap placement and trim — overhang is computed exactly; the offcut falls; the new block width equals the overlap (unit-tested).
3. Perfect detection — a hit within the window snaps and increments the streak; the streak restores width at the configured N.
4. Speed ramp — follows a config curve; capped.
5. Game over and restart — restart in under 1 s; best score persists across app kills.
6. Score and colour progression — the score shows; the gradient shifts every N blocks.
7. Sound ladder — pitch rises per perfect; resets on a miss.
8. Rewarded continue — once per run; restores the last width.
9. Interstitial policy — none in the first N runs; interval from remote config.
10. Skill bot — 1,000 runs at three noise levels produce a monotonic score-versus-skill curve.
11. Input latency check — tap-to-visual under the target on the low-tier device; perf report attached.
12. Analytics — `run_end` (score, perfects, continue_used) and `ad_impression`.

## 2. Runner (gates and crowds)

**Definition and player fantasy.** The character or crowd runs forward automatically. Swipe left and right to pass through arithmetic gates (+10, ×2, −5), collect followers, avoid obstacles, then face a final encounter or a multiplier staircase. The fantasy is growing from one to a hundred: power expressed as spectacle, with quick choices made in motion.

**Core loop** (seconds). Run → steer → choose the better gate → dodge obstacles → finale (battle, stairs, multiplier wall) → coins with a rewarded "×3" offer → next level.

**Meta loops.**
- Persistent upgrades such as starting crowd and income per level, bought with level coins.
- Skins for the leader and the crowd.
- A visible level counter: "Level 57" is itself a progress signal in hypercasual.
- The fuller hybrid version is playbook 7.

**Session profile** (estimate). Levels of 30–60 seconds; sessions of 3–10 minutes; many sessions a day.

**Signature mechanics** (`mechanics-codex`: movement-dodging, economy-flow, progression-unlocks).
- Arithmetic gates as split-second decisions. Pair a big add with a hidden trap to create tension.
- Crowd simulation: flocking or simple formation with GPU instancing. Cap the crowd per device tier.
- The finale converts crowd size into reward, so every gate choice matters at the end.

| Parameter | Starting value to tune (heuristic) | Effect |
|---|---|---|
| Level length | 20–45 s of running | Fits the hypercasual session |
| Gate pairs per level | 4–8 | Decision density |
| Crowd render cap | Per tier, e.g. 60 low, 200 high | Frame time |
| Finale conversion | Crowd → multiplier steps | Reward variance |
| Obstacle density | Low early | Fairness |

**Monetization model and typical mix.** Interstitials between levels after the first few, a rewarded end-of-level multiplier, a rewarded skip, and a no-ads IAP.

**KPI expectations.** The hyper-casual D1 range of about 33–40% is inconsistent across sources [V4]. Otherwise qualitative: strong marketability, weak D7 without meta.

**Retention drivers.**
- The "watch the crowd grow" spectacle.
- Upgrades that make the next level feel stronger.
- New finale types.
- Skins.

**Content pipeline and production scope** (estimates).
- Levels are assembled from track segments (gates, obstacles, finale), procedurally or with a light editor.
- Score every generated level with the optimal-path bot, and reject levels where a wrong gate cannot be recovered.
- Assets are low-poly: characters, gates and environment themes. One environment theme per 10–20 levels keeps the game visually fresh.
- A slice takes 1–2 people plus agents, 1–3 weeks. A test build takes 2–4 people, 4–8 weeks.

**Reference titles.** Count Masters, Join Clash 3D, Mob Control (Voodoo), Run Race 3D (Good Job Games, a race variant).

**What makes it succeed / fail.**
- Succeeds: a strong ad hook (huge crowds), readable gate math at speed, and a satisfying finale.
- Succeeds: a stable frame rate with big crowds.
- Fails: frame drops when the crowd grows, unreadable gates, and levels that blur together.
- Fails: an ad promising crowds that the device tier caps away.

**Innovation vectors.**
- Hybrid metas (playbook 7).
- Combat finales with unit types.
- Async PvP finales against other players' crowds.
- Cooperative events.

**Agent-buildability: 4/5.** The track simulation is deterministic, and an optimal-gate bot computes the best path exactly, so level difficulty can be scored. The 3D assets are low-poly. A point is lost for crowd performance on low-tier devices and the feel of the finale.

**Starter feature list (P0 vertical slice).**
1. Auto-run and steering — constant forward speed; drag steering clamped to the track; works one-handed in portrait.
2. Gate system — +, −, × and ÷ gates applied on crossing (unit-tested arithmetic, including floors).
3. Crowd model — the follower count drives formation; instancing; the per-tier cap comes from config.
4. Obstacles — remove followers on contact with feedback; run over when the count reaches 0.
5. Finale — a multiplier staircase converts the count to a reward multiplier.
6. Level assembly — 15 levels from segment data with a seeded generator.
7. Optimal-path bot — computes the max-crowd path per level; levels must allow at least X% of the optimum to win.
8. Coins and one upgrade — starting crowd +N per upgrade, cost curve from `progression_calc.py`.
9. Rewarded multiplier — "×3 coins" at level end; skippable; the base reward is always shown.
10. Interstitial policy — after level N, minimum interval, never mid-run.
11. Perf — p95 frame time within budget on the low tier with the crowd at its cap.
12. Analytics — `level_end` (crowd size, gates taken, multiplier) and `upgrade_bought`.

## 3. io (arena growth)

**Definition and player fantasy.** In an arena, grow by eating smaller entities or capturing territory while avoiding bigger rivals, in short timed or endless matches with a live leaderboard. The fantasy is going from tiny to dominant: predator-and-prey thrill and king-of-the-hill bragging.

**Core loop** (seconds). Move → consume pellets and smaller rivals, or claim territory → grow → avoid bigger rivals → die or time up → rank → restart.

**Meta loops.**
- Skins and unlocks, the main expression and IAP layer.
- Player level from match XP, with rewards at each level.
- Daily missions ("eat 50 rivals") that steer play towards variety.
- Rotating game modes (teams, battle royale shrink, speed) to refresh the arena.

**Session profile** (estimate). Matches of 1–3 minutes, sessions of 5–15 minutes.

**Signature mechanics** (`mechanics-codex`: movement-dodging, competition, spatial-packing).
- **Size-speed trade-off.** Bigger is slower, so small players can escape. **Consumption threshold.** You must be X% larger to eat another player.
- **Territory capture** (Paper.io-style). Polygon fill when the trail closes. Rivals can cut your trail.
- **Opponents.** Bots with personalities (aggressive, timid, farmer) fill lobbies. Real multiplayer is optional and costly.

| Parameter | Starting value to tune (heuristic) | Effect |
|---|---|---|
| Match length | 60–120 s (timed modes) | Session fit |
| Eat threshold | About 10–25% larger | Chase dynamics |
| Speed falloff | Decreasing in size | Comeback potential |
| Bot count and skill mix | Mostly beatable, a few threats | First-match win feeling |
| Pellet density | Higher early | Growth pacing |

**Monetization model and typical mix.** Interstitials between matches, a rewarded revive or "start bigger", a skins IAP and no-ads.

**KPI expectations.** No sourced io-specific range. Qualitatively, fun spikes early and retention depends on meta and social features.

**Retention drivers.**
- Leaderboard dominance moments.
- Skin collection.
- Mode variety.
- Real-friend matches when multiplayer exists.

**Content pipeline and production scope** (estimates).
- The art is minimal. The work is in bot AI and balance.
- Bot design: steering behaviours (seek, flee, wander) plus a utility score per personality. Tune by headless match simulation.
- Real-time multiplayer adds servers, netcode and anti-cheat (`multiplayer-backend`) and multiplies scope. Decide at concept time, not later.
- Slice: 1–2 people plus agents, 2–4 weeks with bots only. Real multiplayer: 4–8 people and several months.

**Reference titles.** Agar.io (Miniclip), Slither.io (Lowtech Studios), Paper.io and Hole.io (Voodoo).

**What makes it succeed / fail.**
- Succeeds: instant comprehension, a great growth curve, and bots that feel human but beatable.
- Succeeds: smooth movement.
- Fails: unfair deaths from off-screen threats, boring bots, and lag in real multiplayer.
- Fails: deceptive "real players" claims.

**Innovation vectors.**
- New consumption verbs (holes, territory, merging).
- Squad modes.
- Hybrid metas: persistent upgrades and seasons.
- Transparent bot-versus-human labelling as trust design.

**Agent-buildability: 3/5.** A bots-only version is fully headless-simulable: match outcome distributions can be checked across bot mixes. Points are lost for real-time action (timing), bot-AI feel tuning, and, if multiplayer is chosen, backend and netcode complexity.

**Starter feature list (P0 vertical slice).**
1. Arena and movement — floating joystick or drag-to-steer; speed is a function of size (config curve).
2. Consumption rule — eat pellets and smaller entities above the threshold; growth formula unit-tested.
3. Bots — three personalities with steering behaviours; 9 bots per match.
4. Timed match — a 90 s timer, a live top-5 leaderboard and a results screen with rank.
5. Death and respawn — a death screen with a rewarded revive (once) or restart.
6. Camera — zooms out with size; threats are always visible within N body-lengths.
7. Balance sim — 1,000 headless matches show a first-match top-3 rate for a novice-proxy bot in the target band.
8. Skins — 6 skins unlocked by XP, plus a skin IAP stub.
9. Interstitial policy — between matches after N matches; never on the death screen before the revive choice.
10. Perf — 10 entities plus pellets at 60 fps on the mid tier.
11. Analytics — `match_end` (rank, size, kills, duration, revive_used).

## 4. Cut / slice

**Definition and player fantasy.** Swipe or tap to cut objects: fruit, soap, wood, kinetic sand. Much of the satisfaction is ASMR-like visuals and sound. Variants include flipping a knife through a level (Slice It All!) and precision cutting along lines. The fantasy is tactile satisfaction and precision, with consequence-free destruction.

**Core loop** (seconds). Objects appear → swipe (or time a tap) → slice with split-mesh visuals and sound → score and combo → avoid hazards (bombs) → round or level end → restart or next.

**Meta loops.**
- Blades, trails and backgrounds as a collection.
- High score and daily challenges.
- Level progression in knife-flip variants: reach the end of a course, with multiplier targets at the finish.
- Mode variety (arcade, zen, timed) for different moods.

**Session profile** (estimate). Rounds of 30–90 seconds; sessions of 3–10 minutes.

**Signature mechanics** (`mechanics-codex`: timing, aiming-trajectory, physics).
- Swipe-trail capture with velocity thresholds: a slow swipe does not cut.
- Mesh splitting: runtime plane cuts, or pre-fractured halves swapped in on contact (cheaper and deterministic).
- Combo windows (several objects in one swipe) and hazards that punish wild swiping.

| Parameter | Starting value to tune (heuristic) | Effect |
|---|---|---|
| Swipe min velocity | Tuned on low-end touch sampling | Accidental vs missed cuts |
| Objects per wave | 1–6 | Intensity |
| Hazard ratio | Low early | Skill expression |
| Combo window | Objects cut within one stroke | Payoff |
| Juice | Particles, slow-motion on combos, layered SFX | The whole appeal |

**Monetization model and typical mix.** Interstitials between rounds, rewarded continues and blade unlocks, a no-ads IAP and cosmetic packs.

**KPI expectations.** No sourced range. Qualitatively: highly marketable visuals, short-lived without meta.

**Retention drivers.**
- Sensory satisfaction.
- Blade and skin collection.
- High-score chase.
- Novel materials in each update.

**Content pipeline and production scope** (estimates).
- Cuttable objects need clean meshes or sprites with interior textures. Prefer pre-fractured variants generated offline.
- Audio design is half the product (`audio-direction`): layered cut, squish and crunch sounds per material, with pitch randomization.
- Each new material (sand, jelly, ice) is a content drop that needs new VFX and SFX, not just new art.
- Slice: 1–2 people plus agents, 1–3 weeks. Test build: 2–4 people, 4–8 weeks.

**Reference titles.** Fruit Ninja (Halfbrick), Slice It All! (Voodoo), soap- and sand-cutting ASMR titles.

**What makes it succeed / fail.**
- Succeeds: impeccable feel (latency, slow-motion, sound layering), and readable hazards.
- Succeeds: satisfying interiors on cut objects.
- Fails: missed swipes on low-end touch sampling, and samey content.
- Fails: physics glitches in cut meshes.

**Innovation vectors.**
- Material simulation (sand, jelly).
- Rhythm-synced slicing.
- Hybrid metas: a kitchen or restaurant that consumes what you cut.
- Haptic design.

**Agent-buildability: 3/5.** Swipe detection and scoring can be tested with injected strokes, and pre-fractured meshes keep outcomes deterministic. Points are lost because the appeal depends almost entirely on feel and audio-visual polish, which need human review, and runtime mesh cutting is costly to verify.

**Starter feature list (P0 vertical slice).**
1. Swipe capture — trail rendering; segments over the velocity threshold count as cuts; tested with injected strokes.
2. Slice resolution — a cut swaps in pre-fractured halves with an impulse; deterministic for the same stroke.
3. Spawner — waves from a seeded pattern table; difficulty ramps per wave.
4. Hazard — a bomb ends the round with clear telegraphing.
5. Combo — several objects in one stroke shows a combo with a bonus and brief slow-motion.
6. Score and round end — a 60 s arcade round; best score persists.
7. Juice and audio — layered cut SFX with pitch variation; particles; haptics; human feel checkpoint.
8. Blade cosmetics — 4 blades unlocked by score; trail changes.
9. Rewarded continue — once per round after a bomb.
10. Interstitial policy — after round N; minimum interval.
11. Perf — 6 objects plus particles at 60 fps on the low tier.
12. Analytics — `round_end` (score, combos, cause).

## 5. Draw (draw-to-solve)

**Definition and player fantasy.** Draw a line or shape that becomes a physical object or a solution: a wall that protects a character, a path that guides water, legs for a climbing vehicle. Many levels have many valid answers. The fantasy is creative cleverness: "my weird drawing worked".

**Core loop** (seconds). See the level → draw a stroke → it becomes a rigid body or path → the simulation runs → pass or fail with stars for ink efficiency → next or retry.

**Meta loops.**
- Level packs or worlds gated by stars.
- Pen skins and ink colours, which change only cosmetics.
- Daily levels and a streak.
- A "best solutions" gallery of the player's own clever answers, which can be shared.

**Session profile** (estimate). Levels of 15–60 seconds; sessions of 3–10 minutes.

**Signature mechanics** (`mechanics-codex`: path-drawing, physics, deduction-constraint).
- Stroke capture → simplification (Ramer–Douglas–Peucker) → a collider (chain of capsules or a polygon).
- An ink budget is the main constraint and the source of star criteria.
- Deterministic physics: fixed timestep and frozen-until-release. As in the physics-puzzle playbook (`puzzle.md`), determinism is the risk.

| Parameter | Starting value to tune (heuristic) | Effect |
|---|---|---|
| Ink budget | Bot minimum × 1.5–3 | Difficulty and stars |
| Stroke simplification tolerance | A few px | Collider stability |
| Sim duration | 3–8 s survival or goal | Level tempo |
| Allowed strokes | 1 (pure) or several | Creativity vs puzzle |

**Monetization model and typical mix.** Interstitials between levels, rewarded hints (show a ghost stroke) and skips, a no-ads IAP and pen skins.

**KPI expectations.** No sourced range; qualitative, comparable to other hypercasual puzzles.

**Retention drivers.**
- Clever level ideas.
- Creative expression.
- Funny failure physics.
- Shareable solutions.

**Content pipeline and production scope** (estimates).
- Levels are handcrafted ideas, and ideas are the main cost. An LLM can brainstorm premises, but each premise must survive the sampler.
- Validate each level with a sampler that tries simplified stroke families (lines, arcs, cups, walls) in a headless simulation. Confirm at least one solution and estimate ink difficulty from the cheapest successful stroke.
- Assets are light: characters with simple reaction animations, hazards and backgrounds.
- Slice: 1–2 people plus agents, 2–4 weeks. Test build: 2–4 people, 1–3 months.

**Reference titles.** Happy Glass (Lion Studios), Draw Climber (Voodoo), "save the pet"-style draw-a-wall puzzles.

**What makes it succeed / fail.**
- Succeeds: generous solution spaces, funny physics, and clear goals.
- Succeeds: drawing that feels responsive (no lag at the stroke tip).
- Fails: physics that rejects reasonable drawings, and single-solution levels.
- Fails: non-deterministic results, and running out of level ideas.

**Innovation vectors.**
- UGC level sharing with simulator verification.
- Drawing plus narrative.
- Co-op draw.
- Rhythm-timed drawing.

**Agent-buildability: 3/5.** Stroke-family sampling can verify levels once physics is deterministic. Points are lost for level ideation (taste), feel, and physics determinism work.

**Starter feature list (P0 vertical slice).**
1. Stroke capture — smooth trail; points sampled at a fixed distance; ink meter decreases.
2. Simplify and collide — RDP simplification produces a stable collider with no self-intersection crash (fuzz-tested).
3. Deterministic sim — the same stroke data gives the same outcome over 100 headless runs.
4. Goal conditions — survive T seconds, or the object reaches its target.
5. Stars — ink efficiency thresholds per level.
6. 20 levels — each passes the stroke-family sampler with at least one solution.
7. Hint — a rewarded ghost stroke of a known solution.
8. Instant retry — under 1 s.
9. Fail comedy — a ragdoll or splash reaction plays on failure, within the perf budget.
10. Interstitial policy — after level N; never during drawing.
11. Analytics — `level_end` (ink used, attempts, result, hint_used).

## 6. Idle-arcade (carry and unlock)

**Definition and player fantasy.** Walk a character with a floating joystick. Pick up items from producers, which auto-stack on your back, deliver them to stations or customers, collect cash piles, and walk onto unlock pads to spend cash on new stations, areas and helpers. The hypercasual version is one compact map with roughly an hour of content. The fantasy is being a busy little entrepreneur: growth you can see and stacks you can touch.

**Core loop** (seconds). Walk to a producer → collect a stack → deliver → cash spawns → walk to a pad → it fills and unlocks → the expanded business produces more → repeat.

**Meta loops.**
- Unlock pads form a visible expansion tree across the map.
- Helpers (hired workers) automate a route; upgrades raise carry capacity and walk speed.
- A finished map leads to the next map in fuller versions (see playbook 8 for the hybrid management meta).

**Session profile** (estimate). 5–15 minutes; a full map of 30–90 minutes in the hypercasual form.

**Signature mechanics** (`mechanics-codex`: movement-dodging, production-chains, economy-flow, generators-timers).
- Proximity interactions with no buttons: standing in a zone triggers pickup, drop-off or spending. Pad fill rate is a feel parameter.
- Stack carry visuals with spring wobble. The height of the stack is the reward display.
- Helper AI on fixed routes, which converts active play into automation.

| Parameter | Starting value to tune (heuristic) | Effect |
|---|---|---|
| Carry capacity | 5–10 items, upgradable | Trip count per delivery cycle |
| Pad price curve | Geometric, about 1.3–1.6× per pad | Pacing of unlocks |
| Producer rate | 1 item per 1–3 s | Wait vs walk balance |
| Helper cost | About 3–6 pad-equivalents | Automation milestone timing |
| Walk speed | Comfortable thumb travel across the map in 5–8 s | Fatigue |

**Monetization model and typical mix.** Rewarded ads for speed boosts, cash injections and helper boosts. Interstitials only at natural breaks, because they interrupt flow badly in this genre. A no-ads IAP.

**KPI expectations.** No sourced range. Qualitatively, strong early engagement from visible growth, with a content cliff at map end unless a meta exists.

**Retention drivers.**
- The next pad is always visible and nearly affordable.
- Automation milestones ("my helpers run the café").
- The stack on your back as a tactile reward display.
- Map completion and a reveal of the next map.

**Content pipeline and production scope** (estimates).
- One map is a station graph with an economy table. Validate pacing with `economy_sim.py`, using a walker bot that follows a greedy "nearest affordable pad" policy.
- Assets are low-poly: character, items, stations and environment.
- Slice: 1–2 people plus agents, 2–4 weeks. Test build: 2–5 people, 1–3 months.

**Reference titles.** Carry-and-unlock games of the 2022–2024 wave; My Perfect Hotel (SayGames) as the bridge to hybrid (playbook 8).

**What makes it succeed / fail.**
- Succeeds: tactile stacks and pickups, short walks, and a pad always within reach.
- Succeeds: helpers that visibly take over.
- Fails: long walks, item clutter, and pathing bugs that block helpers.
- Fails: interstitials mid-flow, and a dead end after the first map.

**Innovation vectors.**
- Themed businesses with distinct mechanics per station.
- Light customer-satisfaction systems.
- Social visits to other players' maps.
- Merge or puzzle mini-tasks at stations.

**Agent-buildability: 4/5.** The agent simulation is deterministic and the economy can be checked with a walker bot. The assets are low-poly and timing tolerance is generous. A point is lost for carry-stack feel and helper pathfinding edge cases that need visual checks.

**Starter feature list (P0 vertical slice).**
1. Floating joystick — appears under the thumb anywhere in the bottom half; speed is clamped; works one-handed.
2. Producer and pickup — standing in a zone auto-collects up to capacity with a stack visual.
3. Delivery station — dropping items converts them to cash piles; pickup is magnetized.
4. Unlock pads — standing on a pad drains cash into it with a fill animation; completion spawns the station.
5. Expansion graph — 12 pads in data; prerequisites enforced; the next pad is highlighted.
6. Helper — a hireable worker runs a fixed route; never deadlocks (100 simulated minutes).
7. Upgrades — carry capacity and walk speed with cost curves from `progression_calc.py`.
8. Economy sim — the walker bot completes the map in the target minutes ±20%.
9. Rewarded boost — 2× speed for 60 s; opt-in button; daily cap from config.
10. Save and offline — the map state persists; a small offline income cap is shown on return.
11. Perf — 60 fps on the mid tier with 4 helpers and 50 items on screen.
12. Analytics — `pad_unlocked` (id, time since start), `helper_hired` and `session_end`.

## 7. Runner + meta (hybrid)

**Definition and player fantasy.** The gate-and-crowd or obstacle runner of playbook 2, wrapped in persistent progression: unit or character upgrades, a base or city that run rewards build, collections, events and a pass. The fantasy grows from "my crowd got huge" to "my army and kingdom keep getting stronger".

**Core loop** (seconds). Run level → coins, cards or materials by performance → back to the hub.

**Meta loops.**
- Upgrade tracks (starting units, unit types, income) on long, slow curves.
- Base building or collection: spend run rewards on buildings or cards that grant passive bonuses.
- Events: limited-time run modifiers, leaderboards, a season pass.
- Optional async PvP: attack others' bases with your crowd or defend against them.

**Session profile** (estimate). 5–15 minutes, 3–6 sessions a day. Runs stay at 30–60 seconds; hub time grows.

**Signature mechanics** (`mechanics-codex`: movement-dodging, progression-unlocks, build-crafting, collection, economy-flow).
- A bounded power bridge: meta upgrades shift run outcomes, but level difficulty is re-simulated with expected meta power, so skill still matters (fusion rule 3 in `SKILL.md`).
- Multiple soft currencies converge into one premium currency. Keep the total small (2–3 plus premium).
- Unit types (melee, ranged, tank) add rock-paper-scissors choices to the finale.

| Parameter | Starting value to tune (heuristic) | Effect |
|---|---|---|
| Meta power share | Meta adds at most +10–15 pts bot win rate | Keeps skill relevant |
| Upgrade curve | Polynomial or exponential, `progression_calc.py` | Long-tail pacing |
| Run reward split | Coins vs materials | Hub engagement |
| Event cadence | Weekly modifiers, monthly pass | Wrapper rhythm |
| Energy | Usually none, or generous | Hypercasual roots expect free play |

**Monetization model and typical mix.**
- Hybrid. Rewarded ads (multipliers, free chests) plus interstitials with frequency caps for non-payers.
- IAP: no-ads plus starter bundle, season pass, upgrade bundles.
- Hybrid-casual is the segment where IAP is growing [V1].

**KPI expectations.** No primary 2026 benchmark for hybrid-casual retention or ARPDAU was found. The research notes flag this as a gap. Treat the all-genre viability screens in `SKILL.md` as targets, and recalibrate in soft launch.

**Retention drivers.**
- Long upgrade tracks and base growth.
- Events and pass progression.
- Collection completion.
- Social or async PvP where present.

**Content pipeline and production scope** (estimates).
- Run levels come from segment generators, as in playbook 2. The hub is the new cost: buildings, upgrade UI, an economy model and event tooling.
- Simulate the economy (`economy_sim.py`) for 30, 60 and 90-day archetypes before soft launch.
- Slice: 2–3 people plus agents, 4–8 weeks. Soft launch: 6–15 people, 6–12 months.

**Reference titles.** Mob Control (Voodoo), Count Masters, Join Clash 3D. They show how hypercasual runners grow meta layers.

**What makes it succeed / fail.**
- Succeeds: the meta makes every run matter, upgrades are visible in the run, and events refresh the core.
- Succeeds: ad load is tuned per payer segment.
- Fails: a meta disconnected from the run, and a currency sprawl.
- Fails: a power bridge so strong that levels become trivial, or so weak that upgrades feel fake.

**Innovation vectors.**
- Async PvP with crowd armies.
- Squad-based co-op events.
- Narrative chapters per world.
- Playable-ad-driven feature testing [V5].

**Agent-buildability: 4/5.** Runs are deterministic and bot-scorable, and the meta economy is simulable. A point is lost for hub UI breadth, economy tuning judgment and live-ops tooling.

**Starter feature list (P0 vertical slice).**
1. Run core — playbook 2 features 1–6 pass their acceptance criteria.
2. Hub screen — a run button, upgrades and a base view; return to the hub within 2 s of a level ending.
3. Two upgrade tracks — starting crowd and income; costs from `progression_calc.py`; persistent.
4. Base building — 5 buildings purchasable with coins, each with a passive bonus applied to runs (unit-tested).
5. Power bridge check — bot win rate with expected day-7 upgrades stays within +15 pts of the base target.
6. Unit types — two unit types with distinct finale behaviour.
7. Economy sim — the 30-day archetype run shows no hoarding beyond `max_soft_currency_hoard_days`.
8. Rewarded multiplier and free chest — opt-in with daily caps.
9. Starter bundle IAP — a single offer after level N with the price shown in the local currency (store sandbox).
10. No-ads IAP — removes interstitials and banners and keeps rewarded ads optional.
11. Weekly event stub — a modifier from remote config changes the run rules (e.g. double gates).
12. Analytics — `level_end`, `upgrade_bought`, `building_bought`, `iap_purchase` and `ad_impression`.

## 8. Arcade idle (hybrid management)

**Definition and player fantasy.** The carry-and-unlock core of playbook 6, grown into a management game with several locations, managers, staff upgrades, customer flow and offline earnings, plus IAP and events. The fantasy is building an empire from one counter: hands-on at first, then managing and optimizing.

**Core loop** (seconds to minutes). Serve and carry by hand early on → earn → unlock stations and staff → staff automate → the player moves to bottlenecks and upgrades → the location completes → a new location with higher multipliers.

**Meta loops.**
- Multiple locations, each a themed map with its own station graph and a prestige-like reset with higher income.
- Managers and staff upgrades (speed, capacity, tips) and a VIP or premium staff layer.
- Offline earnings with a cap, extended by IAP or ads.
- Events: limited-time locations, a pass, collection cards.

**Session profile** (estimate). 5–15 minutes, 3–6 sessions a day; return driven by offline earnings.

**Signature mechanics** (`mechanics-codex`: production-chains, generators-timers, economy-flow, progression-unlocks).
- **Bottleneck management** is the depth: customer arrival rate versus station throughput versus staff speed. A queueing view helps: keep station utilization ρ = λ/μ below 1, or queues explode.
- Offline earnings: `offline = min(elapsed, cap) × rate × offline_efficiency`.
- Location prestige: the next location multiplies base income, so early stations of the new map pay out faster.

| Parameter | Starting value to tune (heuristic) | Effect |
|---|---|---|
| Offline cap | A few hours, extendable | Return cadence and an IAP or ad lever |
| Offline efficiency | Below 100% of active rate | Rewards active play |
| Location length | A few days per location | Long-term pacing |
| Customer patience | Seconds before leaving | Pressure and tips |
| Staff upgrade curve | Geometric | Optimization depth |

**Monetization model and typical mix.**
- Rewarded ads: double offline earnings, speed boosts, instant cash, free staff time.
- IAP: no-ads, VIP managers, permanent multipliers, a season pass, location bundles.
- Interstitials capped or removed for payers.

**KPI expectations.** No sourced range. Qualitatively, hybrid-casual retention depends on location pacing and offline loops; benchmark against the all-genre screens.

**Retention drivers.**
- Offline earnings waiting.
- The next location's reveal.
- Optimizing bottlenecks.
- Events and pass.
- Collection cards.

**Content pipeline and production scope** (estimates).
- Each location is a new station graph, theme art and economy table, validated by a walker or manager bot in `economy_sim.py`.
- Event locations reuse systems with new themes.
- Slice: 2–3 people plus agents, 4–8 weeks. Soft launch: 6–15 people, 6–12 months.

**Reference titles.** My Perfect Hotel (SayGames); restaurant and supermarket arcade-idle hybrids. See the tycoon and restaurant playbooks in `idle-tycoon-sim.md`.

**What makes it succeed / fail.**
- Succeeds: the shift from hands-on to manager feels earned, bottlenecks are readable, and offline returns are generous.
- Succeeds: locations feel distinct.
- Fails: walking-heavy late game, and opaque multipliers.
- Fails: an offline cap so stingy it feels like a chore, and economy inflation with nothing left to buy.

**Innovation vectors.**
- Customer stories and light narrative.
- Social visits and co-op events.
- Merge or puzzle station mini-games.
- Data-driven location pacing via remote config.

**Agent-buildability: 4/5.** Agents, queues and the economy are deterministic and simulable, and bots can play locations. A point is lost for UI breadth, many themed assets per location and pacing judgment.

**Starter feature list (P0 vertical slice).**
1. Carry core — playbook 6 features 1–5 pass their acceptance criteria.
2. Customer flow — customers arrive per a seeded Poisson process, queue, get served or leave after their patience runs out.
3. Stations and throughput — each station has a service time; utilization is displayed in the debug overlay.
4. Staff hire — staff automate the station routes; upgrades change speed and capacity (unit-tested).
5. Manager upgrades panel — 3 upgrade lines with cost curves; persistent.
6. Offline earnings — computed from a guarded elapsed time, capped; the return screen offers a rewarded 2×.
7. Location completion — completing all pads unlocks location 2 with a base income multiplier.
8. Economy sim — the location completes in the target days for the casual and engaged archetypes.
9. No-ads and VIP manager IAP — entitlements persist and restore on reinstall (sandbox).
10. Rewarded placements — speed boost and instant cash with daily caps; never forced.
11. Save robustness — kill-and-restore at random points keeps state consistent (100 scripted cycles).
12. Analytics — `location_complete`, `offline_return` (amount, doubled), `staff_hired` and `iap_purchase`.

## 9. Casual survivor-like

**Definition and player fantasy.** A one-finger, portrait, auto-attacking survival action game. Move to dodge hordes and collect XP, and at each level-up choose one of three skills to build combos within a run. Chapters are 10–15 minutes or shorter, followed by a deep meta of gear, talents, pets and events. The fantasy is to start weak, become an unstoppable power fantasy, and feel the meta make every run stronger.

**Core loop** (seconds to minutes). Move → auto-attack → kill → collect XP gems → level up → choose 1 of 3 skills (with evolutions when two skills combine) → survive waves and bosses → chapter clear or death → rewards (gear, materials, currency).

**Meta loops.**
- Gear in fixed slots with rarity tiers, often upgraded by merging duplicates or materials.
- Talent trees and character or pet unlocks.
- Chapter progression with energy per attempt, daily dungeons, events and a season pass.

**Session profile** (estimate). Runs of 5–15 minutes; 2–5 sessions a day; energy pacing.

**Signature mechanics** (`mechanics-codex`: movement-dodging, auto-combat, build-crafting, randomness-loot, progression-unlocks).
- The level-up choice draws 3 random skills weighted by owned skills (synergy bias). Evolution recipes combine a max-level skill with a passive.
- Horde density curves and boss waves are authored per chapter. Enemy count is capped per device tier.
- Meta power scales damage and HP. Chapter difficulty is tuned against expected meta power by archetype.

| Parameter | Starting value to tune (heuristic) | Effect |
|---|---|---|
| Run length | 8–15 min (casual, mobile) | Session fit |
| Level-ups per run | About 20–40 | Build depth |
| Choice count | 3 (+1 reroll) | Agency vs randomness |
| Enemy cap on screen | Per tier, e.g. 150 low, 400 high | Frame time |
| Energy per chapter | About 1/6 of the cap | Attempts per day |

**Monetization model and typical mix.**
- IAP: gear chests, which are paid random items. Disclose odds, add pity and check loot-box law: Brazil banned loot-box sales to under-18s from March 2026 [V10] (see `legal-ethics`).
- Also energy, a season pass and starter or growth bundles.
- Rewarded ads: revive, double rewards, free chest.

**KPI expectations.** No sourced range. Qualitatively, hybrid-casual titles in this pattern aim for midcore-like D30 with casual-like D1.

**Retention drivers.**
- Build experimentation.
- Gear progress and chapter gates.
- Daily dungeons and events.
- Pass.
- Near-miss deaths with a revive option.

**Content pipeline and production scope** (estimates).
- Per chapter: an enemy set, a wave script and a boss.
- Skills, evolutions and gear need VFX and balance. This is the heaviest balance load of the hybrid patterns.
- Run a headless sim with a kiting bot to estimate clear rates per meta-power level.
- Slice: 2–4 people plus agents, 6–10 weeks. Soft launch: 10–25 people, 9–15 months.

**Reference titles.** Survivor!.io (Habby), Archero (Habby, the "stop to shoot" precursor), Magic Survival. Vampire Survivors (poncle) is the premium origin; see `action-arcade-roguelite.md`.

**What makes it succeed / fail.**
- Succeeds: a readable screen even at peak density, satisfying evolution payoffs, and short, punchy chapters.
- Succeeds: a meta that is generous early.
- Fails: frame drops at peak density, and unreadable enemy projectiles.
- Fails: a paywall-feeling chapter wall, and opaque chest odds.

**Innovation vectors.**
- Theme and IP variants.
- Co-op runs.
- Roguelite card and dice hybrids.
- Lighter, ethical gear systems with deterministic crafting.

**Agent-buildability: 3/5.** The run logic can be simulated headlessly with a kiting bot, and the meta economy and chest odds can be checked with `economy_sim.py` and `gacha_calc.py`. Points are lost for real-time readability and feel, many-entity performance, VFX volume and balance across dozens of skills.

**Starter feature list (P0 vertical slice).**
1. One-finger movement — a floating joystick in portrait; the character stays clear of the thumb's occlusion zone.
2. Auto-attack — the default weapon targets the nearest enemy at a fixed cadence; DPS unit-tested.
3. Enemy spawner — a wave script for a 10-minute chapter; enemies are pooled; the per-tier cap is enforced.
4. XP and level-up — gems drop and magnetize; level thresholds follow a curve; the game pauses on level-up.
5. Skill choice — 3 random skills from a pool of 8 with synergy weighting; one free reroll.
6. Evolution — one evolution recipe (max skill + passive) with a distinct payoff VFX.
7. Boss — one boss with a telegraphed attack pattern at minute 10.
8. Death and revive — a rewarded revive once per run; results screen with rewards.
9. Gear meta — 2 gear slots with rarity; equipped stats apply to the run (unit-tested).
10. Kiting-bot sim — 500 headless runs: clear rate at zero meta and at day-3 meta within the target bands.
11. Perf — p95 frame time within budget on the low tier at the enemy cap with all VFX.
12. Analytics — `run_end` (duration, level, skills, cause, revive) and `gear_upgrade`.

## 10. Puzzle + RPG

**Definition and player fantasy.** Puzzle battles, usually match-3 on a board, where matches power a team of collected heroes who attack, heal and fire skills. Wrapped in hero collection, upgrades, PvE campaigns and often guild and PvP layers. The fantasy is being a tactician-collector: puzzle skill becomes battle power, and the roster grows into a dream team.

**Core loop** (seconds to minutes). Match tiles → the matching heroes charge or attack → enemy turn → fire hero skills at the right time → win the stage → rewards (hero XP, materials, summon currency).

**Meta loops.**
- Hero collection through summoning (gacha), with ascension and limit breaks.
- Campaign map, base or building production of upgrade materials.
- Guilds and alliances with raids or titans, asynchronous PvP raids, events and a season pass.

**Session profile** (estimate). 5–15 minutes, several sessions a day, plus guild-event spikes.

**Signature mechanics** (`mechanics-codex`: matching, auto-combat, collection, randomness-loot, build-crafting, social-coop).
- Colour or element affinity (rock-paper-scissors), so team composition matters per stage.
- Mana-charge skills: each hero's skill charges from matches of its colour. Timing a skill is the skill expression.
- Stage enemies with HP, attack timers and special rules, simulated deterministically per seed.

| Parameter | Starting value to tune (heuristic) | Effect |
|---|---|---|
| Board | 7×5 to 7×7, 5 colours | Readability on portrait screens |
| Team size | 3–5 heroes | Composition depth |
| Affinity multiplier | Strong vs weak, e.g. 2× / 0.5× | Roster pressure |
| Summon rates and pity | Disclosed; check with `gacha_calc.py` | Fairness and legal compliance |
| Stage energy | Tuned per archetype | Session count |

**Monetization model and typical mix.**
- IAP-led: summons (gacha) with disclosed odds and pity, energy, a season pass, and progression bundles.
- Rewarded ads are secondary.
- Apply `monetization` ethics and loot-box rules per storefront country.

**KPI expectations.** No sourced range. Qualitatively: midcore-like monetization depth, with retention driven by roster growth and guild obligations.

**Retention drivers.**
- Roster growth and the next summon.
- Guild raids with shared goals.
- Event heroes.
- Campaign chapters.
- PvP ladders.

**Content pipeline and production scope** (estimates).
- Heroes are the cost: illustrations, skill VFX, balance and lore for dozens to hundreds of heroes over a game's life.
- Stages are generated with bot verification. A greedy-match bot plus a skill-timing policy estimates the clear rate for each team power.
- Slice: 2–4 people plus agents, 6–10 weeks. Soft launch: 15–30 people, 12–24 months.

**Reference titles.** Puzzle & Dragons (GungHo Online Entertainment), Empires & Puzzles (Small Giant Games), Puzzle Quest (Infinite Interactive).

**What makes it succeed / fail.**
- Succeeds: puzzle decisions that matter beyond raw hero power, and heroes with distinct, readable skills.
- Succeeds: guild systems with real cooperation, and transparent gacha.
- Fails: power creep that makes the board irrelevant, and stage walls tuned only for payers.
- Fails: hero art inconsistency, and opaque odds.

**Innovation vectors.**
- Puzzle cores other than match-3 (merge, tile, blast).
- Roguelite puzzle runs.
- Co-op real-time raids.
- Deterministic crafting alternatives to gacha.

**Agent-buildability: 4/5.** The combat is turn-based, deterministic and bot-verifiable, and the gacha and economy math can be checked by script. A point is lost for hero art volume and consistency, skill VFX, and the long-term balance judgment across a growing roster.

**Starter feature list (P0 vertical slice).**
1. Match board — match-3 features 1–3 from `puzzle.md` pass on a 7×5 board.
2. Hero charge — matches add mana to heroes of that colour; the charge bar fills; skills fire on tap (unit-tested).
3. Damage model — attack, defence and affinity formula documented and unit-tested, including a 2×/0.5× affinity.
4. Enemy turns — enemies with HP and attack timers; turn order deterministic per seed.
5. Three heroes, two skills each — distinct skill effects (damage, heal, stun), each with VFX.
6. Stage flow — 10 campaign stages with win, lose and retry screens.
7. Bot verification — a greedy-match plus skill-timing bot gives a clear rate per stage within the target band at the expected team power.
8. Hero upgrade — XP from stages levels heroes; stats scale per curve (`progression_calc.py`).
9. Summon — a single summon banner with disclosed rates and pity, simulated with `gacha_calc.py`; odds screen reachable in one tap.
10. Energy — stages cost energy; regeneration and refill offer.
11. Save and resume — a battle in progress survives an app kill.
12. Analytics — `stage_end` (stage, team power, result, turns), `summon` and `hero_upgrade`.

## 11. Volatile facts used in this file (as of Oct 2026 — verify before relying)

- [V1] Hybrid-casual had the largest spending jump in 2025: +17.1%, from $3.5B to $4.2B (Sensor Tower data). Source: [Mobilegamer.biz](https://mobilegamer.biz/data-digest-sensor-towers-h1-analysis-hay-days-comeback-julys-top-games-big-krafton-numbers-and-more/).
- [V2] Feb–Apr 2026: casual and hyper-casual each took 40% of game ad revenue, hybrid 16%, mid-core 4%. Source: [GameDev Reports summary of Sensor Tower](https://gamedevreports.substack.com/p/sensor-tower-mobile-game-ad-monetization).
- [V3] Voodoo used to test about 1,000 prototypes a year (2024) and has pivoted to hybrid-casual with about 4 launches a year. Sources: [mobilegamer.biz](https://mobilegamer.biz/voodoo-to-launch-just-four-games-per-year-after-hard-hybridcasual-pivot/), [Voodoo](https://voodoo.io/news/voodoo-s-secret-sauce-from-0-to-250m-hybridcasual-revenue-in-3-years).
- [V4] Hyper-casual D1 is cited at about 33% to 40%. Genre splits are inconsistent across sources, and some trace back to AppsFlyer Q3 2022 data. Sources: [Segwise](https://segwise.ai/blog/mobile-gaming-app-user-retention-strategies), [AppAgent](https://appagent.com/blog/mobile-game-retention-benchmarks/).
- [V5] Sett raised a $30M Series B (Mar 30, 2026) for agents that generate video and playable ads, mini-games and events from performance data. Source: [SiliconANGLE](https://siliconangle.com/2026/03/30/sett-raises-30m-grow-agent-based-ai-platform-arcosians/).
- [V6] Among top-grossing ad-monetized games in 2025: AppLovin MAX 55%, LevelPlay 25%, AdMob 13.3%. Source: [PocketGamer.biz](https://www.pocketgamer.biz/nine-facts-about-the-mediation-space-in-2025).
- [V7] Unity LevelPlay ended waterfall-only support for Unity Ads in January 2026; bidding is the standard path. Source: [Segwise](https://segwise.ai/blog/applovin-publisher-monetization-guide).
- [V8] Jan–May 2026: ads were 70.3% of game revenue in India vs 22.1% in the US. Source: [GameDev Reports](https://gamedevreports.substack.com/p/sensor-tower-mobile-game-ad-monetization).
- [V9] modl.ai states that very fast or timing-critical gameplay is "not fully supported yet". Source: [modl.ai](https://modl.ai).
- [V10] Brazil banned loot-box sales to under-18s from March 2026. Source: [Sheep Esports](https://www.sheepesports.com/articles/brazil-court-orders-riot-games-to-pay-eur2-5m-over-league-of-legends-loot-boxes/en).
- No primary 2026 benchmark report on hybrid-casual ARPDAU, IAP/ad split or retention was found in the research. Only secondary summaries of Sensor Tower data exist. Figures for a hybrid-casual IAP growth of "37%" conflict on the year and are not used here.
