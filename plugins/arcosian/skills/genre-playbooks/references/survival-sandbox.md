# Survival and Sandbox Playbooks

Survival and sandbox games sell agency over a world: gather, craft, build, endure, and tell your own story. They are PC-first (Steam early access is the dominant route), strong on console, and weak on mobile except as simplified ports. This file holds five playbooks in a shared 14-part template plus a "Platform notes" part:

1. Open-world survival-crafting with base building
2. Co-op survival (2–8 players, host or dedicated server)
3. Creative / voxel sandbox
4. Colony sim
5. Survival roguelite

Seven foundations come first: needs-meter decay maths, crafting trees and tech gating, resource respawn, day-night and weather pressure, optional PvP raiding, procedural worlds, and save size with world streaming. Single-player survival with a deterministic world seed is a good agent target (3–4/5). Persistent PvP servers and large co-op worlds are not (1–2/5), because their product is netcode, server operations and moderation. Mobile versions of idle farming and life sims are already in `idle-tycoon-sim.md`; this file does not repeat them. Market numbers live in the dated volatile-facts section.

## Contents

| § | Playbook | Session profile (estimate) | Primary monetisation | Agent-buildability | First project for an agent pipeline? |
|---|---|---|---|---|---|
| 0 | [Shared foundations](#0-shared-foundations) | — | — | — | Read first |
| 1 | [Open-world survival-crafting](#1-open-world-survival-crafting) | 1–3 h sessions, 50–300 h total | Premium (early access), DLC, cosmetics | 3/5 (single-player) | Yes, as a one-biome single-player slice |
| 2 | [Co-op survival](#2-co-op-survival) | 2–4 h scheduled group sessions | Premium, DLC, server rental | 2/5 | Only with host-authoritative co-op and a bot client |
| 3 | [Creative / voxel sandbox](#3-creative--voxel-sandbox) | 30 min–3 h, open-ended | Premium, marketplace, cosmetics | 3/5 | Yes, but a voxel engine is the real cost |
| 4 | [Colony sim](#4-colony-sim) | 1–4 h sessions, 100–1,000 h total | Premium, DLC, mod ecosystem | 4/5 | Yes |
| 5 | [Survival roguelite](#5-survival-roguelite) | 20–60 min runs | Premium, DLC | 4/5 | Yes, the best first project here |
| — | [Volatile facts](#volatile-facts-as-of-oct-2026--verify-before-relying) | — | — | — | Check before quoting numbers |

## How to use these playbooks

- Copy the core loop into `contract.json → loops[]`. Set `meta.genre: "survival"` (or `"sandbox"` for playbooks 3 and 4) and `meta.subgenre` to the playbook slug. Set `meta.platforms` (usually `windows`, plus `linux`, `macos`, `playstation`, `xbox`, `switch`) and `meta.input` (`mouse_keyboard`, `gamepad`). Then set `technical.multiplayer` (`none`, `coop_host`, `coop_dedicated`, `pvp_dedicated`). That field drives cost and buildability more than anything else.
- Turn the starter feature list into P0 `features.json` entries with `gs.py feature add`. Each acceptance criterion maps to `unit` or `playthrough` gate evidence (bots, sims, save round-trips).
- Mechanic category labels: combat, build-craft, collection & randomness, progression & upgrade, economy & resources, time & energy, social & competition, exploration & traversal, live events, UX automation. Resolve them with `gs.py kb "<mechanic>" --skill mechanics-codex`.
- Platform differences (input, session, performance, business model) are in each playbook's "Platform notes" part. For the cross-genre treatment see `platform-targets`, `pc-web-release` and `console-pathway`.
- KPI statements are qualitative unless sourced. Early access titles are judged by wishlist-to-sale conversion, reviews and refund rate more than by D1 retention. Use the anchors in the volatile-facts section.

## 0. Shared foundations

### 0.1 Needs-meter decay maths
Each need (hunger, thirst, warmth, stamina, sanity) is a meter `M` in `[0, 100]` that falls at a base rate `r0` per real minute and is multiplied by modifiers.

```
Rate                 r = r0 · (1 + Σ modifiers)
Time to empty        t = M / r
Worked example: hunger r0 = 0.5/min, sprinting +0.5, cold +0.3
  r = 0.5 · (1 + 0.5 + 0.3) = 0.9/min      full meter lasts 100 / 0.9 ≈ 111 min
  Resting, warm:   100 / 0.5 = 200 min
Day length 20 min real → 10 hunger lost per day at rest (0.5 × 20)
Food item restores 25 → 0.4 items per in-game day at rest
```

- **Budget the chore.** Needs should take 10–20% of a session at default difficulty. Above that, players feel they are playing a spreadsheet. Below 5%, the meters are decoration.
- **Tiered penalties, not cliffs.** Use thresholds: above 50% no effect, 25–50% small penalty (slower stamina regeneration), 1–25% real penalty (health drain begins), 0% damage over time. Show each threshold on the meter.
- **Make the cure a decision.** Cooked food restores more than raw. Warm clothes trade weight for protection. If one item solves every need, the meter has no design value.
- **Logged-out decay.** In persistent or co-op worlds, pause needs when the player is away, or clamp to a floor (for example 25%). Never let a player return to a dead character from a 30-second disconnect.
- **Difficulty is a multiplier on `r0` and on penalties.** Expose it as presets (Relaxed 0.5×, Standard 1×, Hard 1.5×) and never change recipes between presets, so guides and saves stay portable.
- **Accessibility.** Offer "needs off" or a creative-style toggle. It widens the audience and costs one flag. See `accessibility-localization`.

### 0.2 Crafting trees and tech gating
A crafting tree is a directed acyclic graph from raw resources to tools, structures and consumables. Gating decides when each node becomes reachable.

```
Raw requirement of item i      R(i) = Σ over recipe inputs j of qty_j · R(j)      (R(raw) = 1)
Worked example: stone axe = 3 wood + 2 stone → R = 5 raw
                 forge = 20 stone + 6 iron ingots; ingot = 2 ore + 1 coal → R(ingot) = 3
                 R(forge) = 20 + 6·3 = 38 raw
Time to tier           T(k) ≈ T1 · q^(k−1)     default q ≈ 3–4
Defaults (estimates): T1 15 min · T2 1.5 h · T3 6 h · T4 20 h · T5 60 h
```

- **Gate by place and tool, not only by recipe.** A tier opens when the player owns a tool that can harvest the next material, or reaches a biome that holds it. That makes the world the tech tree.
- **Limit fan-in and depth.** At most 4 distinct inputs per recipe and 4 crafting steps from raw to final item. Deeper trees need a recipe browser with "what do I need" expansion.
- **Show the full tree early.** Let players pin a recipe and see the missing raw totals. Hidden recipes are a wiki-dependence trap, and the wiki will not exist at launch.
- **One bottleneck per tier.** Each tier needs one scarce input that forces exploration (a rare ore, a boss drop, a trader). Check with the sim: if 90% of players reach T3 inside the target time, add friction. If under 40% do, remove it.
- **Crafting time is a sink, not a gate.** Use 0–30 s for tools, minutes for machines. Long timers belong to idle games (see `idle-tycoon-sim.md` §0).
- **Repair and durability** are sinks that keep early materials relevant. Pair them with a repair recipe cheaper than a fresh craft (about 30–50% of the cost).
- Link the economics to `economy-design` (sources and sinks) and `balance`.

### 0.3 Resource respawn
Resources must renew faster than players consume them, or the world dies.

```
Supply per hour     S = N · y · (60 / T_r)       N nodes in the area, y yield per node, T_r respawn minutes
Demand per hour     D = P · d                    P active players, d per-player draw
Healthy if          S ≥ 1.5 · D at steady state
Worked example: 500 iron nodes, y = 4, T_r = 60 min → S = 2,000 iron/h
  40 players each drawing 300 iron/h → D = 12,000 iron/h → S/D = 0.17 (six times short)
  Fix: ×3 node count, T_r 20 min, or per-player instanced nodes
```

- **Respawn models.** Timer per node; wave respawn on a global day cycle; regrowth by neighbours (trees spread); finite nodes with a renewable alternative (farming, recycling); or per-player instancing. Pick one per resource class and document it.
- **Scale with population on shared servers.** Dedicated PvP servers tune `N` to the pop cap. A hard rule: respawn must not happen inside a radius of any player-built structure, or bases become farms.
- **Depletion creates travel.** Nearby wood runs out, so players push outward. That is exploration pressure, and it is intended on persistent worlds. In single-player, regrowth should outpace a careful player.
- **Avoid camping.** If a rare node respawns at a fixed spot, players will queue at it. Randomise within a pool of spawn points.
- Simulate with `economy_sim.py` (`per_session` sources, `gate` nodes) and add a "fastest possible farmer" bot to find exploits.

### 0.4 Day-night and weather pressure
The cycle sets rhythm: work by day, defend or shelter by night.

| Parameter | Default (estimate) | Note |
|---|---|---|
| Day length (real time) | 20–60 min | Shorter feels frantic, longer lets players ignore night |
| Night share of cycle | 25–40% | Higher on Hard presets |
| Night threat multiplier | 1.5–3× spawn rate | Pair with light as a counter (torches, base lighting) |
| Temperature swing | ±15 to ±30 °C-equivalent | Tie to warmth meter, shelter and clothing |
| Weather events | 1 per 2–4 in-game days | Rain (fire out, slip), storm (lightning), blizzard (visibility, cold) |

- **Pressure should create a plan.** The player prepares (fuel, shelter, a lit base), then enjoys a payoff (safe night, a good fire). A punishment with no counter is just attrition.
- **Readability.** Night must stay playable. Provide a gamma floor and an accessibility brightness option. Pure black fails on many monitors and on HDR TVs.
- **Weather as a modifier on systems, not just visuals.** Rain boosts crop growth and puts out fires. Storms disable ranged enemy spotting. This is cheap to build and adds emergent play.
- **Sleeping and time skip.** In single-player and small co-op, allow sleeping to skip the night when all players are in beds. On PvP servers, sleeping is a vulnerability and so the bed is a risk decision.
- **Seasons** (optional) add a long-horizon planning layer: crops by season, winter scarcity. They multiply content and balance work, so add them after the core loop is proven.

### 0.5 Optional PvP raiding
PvP raiding is the highest-engagement and highest-churn feature in the genre. Treat it as a server mode, not a default.

```
Raid cost ratio    R = attacker_cost_to_breach / defender_cost_to_build
Target band        0.3 ≤ R ≤ 1.0  (below 0.3 players stop building; above 1.0 raids stop happening)
Worked example: stone wall costs defender 300 stone-equivalents (about 20 min of gathering).
  Breach needs 4 explosive charges at 25 resource-equivalents each → attacker cost 100 → R = 0.33
```

- **Offline protection.** Players who are logged out take reduced structure damage (for example 0–50%), with a cap on protected hours per day. Without it, working adults lose bases overnight and leave.
- **Wipe cadence.** Servers reset every 1–4 weeks (or each season) so latecomers can compete. State the schedule on the server list.
- **Raid windows.** Optional: raids only allowed during set hours. This trades emergent play for fairness, and many communities prefer it.
- **Counterplay.** Every offensive tool needs a defence: wall tiers, trap placement, code locks, a raid alert. Pure griefing, such as destroying the spawn bed, is the main churn driver.
- **Matchmaking by clan size.** Cap team size (for example 4 or 8) to stop zerg domination. Enforce it in the server, not in a rules post.
- **Moderation.** Cheating (aim, ESP, speed hacks) kills PvP servers faster than any design flaw. Plan anti-cheat from week one. See `competitive-pvp.md` §0 and `mmo-live-service.md` §0.5.

### 0.6 Procedural worlds
Use `procedural-generation` for the generator (noise, biomes, structures, validation). Survival-specific rules:

- **Seed plus delta.** A world is `(seed, generator_version, player_edits)`. Store only the edits. Pin `generator_version` in the save so patches do not rearrange old worlds.
- **Determinism.** Chunk generation must depend only on seed and chunk coordinates, never on generation order or float-order. Test it: generate chunks in two different orders and diff.
- **Validation.** Check spawn safety (flat ground, water within 200 m, no hostile within 50 m), resource reachability (every tier's material within N minutes of the spawn along a walkable path) and biome adjacency rules. Fail the seed, not the player.
- **Handmade anchors.** Place a few authored landmarks (ruins, dungeons, bosses) on a procedural base. They give players memories and screenshots that pure noise cannot.
- **Seeds as a feature.** Display and share seeds. Some players will compete on "best seed" and that is free marketing.
- **World size.** Pick by travel time: a 10 km² map at 5 m/s walk speed takes about 10 minutes edge to edge. Add fast travel or vehicles after the first tier, not before.

### 0.7 Save size and world streaming
```
Chunk columns loaded    C = (2r + 1)²              r = view distance in chunks
Worked example: r = 8, chunk 16×16×256 voxels → C = 289 columns × 65,536 = 18.9 M voxels
  At 2 bytes per voxel in RAM ≈ 38 MB raw (before meshes)
Edit log      ≈ 6–8 bytes per changed block → 1 M edits ≈ 6–8 MB before compression
```

- **Stream by distance with a budget.** Load, generate, mesh and unload on worker threads with a per-frame time budget (for example 2 ms main-thread). Unload with hysteresis (radius +2 chunks) to avoid thrash.
- **Save only deltas.** Compress with a fast general-purpose codec, and write in the background to a temporary file, then atomically rename. Keep two rotating backups. A corrupted 300-hour save is the worst review you can earn.
- **Cap entity counts.** Placed pieces (walls, crates, machines) cost network, physics and save size. Default cap per base or per player (for example 5,000–10,000 pieces) and tell the player when they near it. Merge static pieces into a single mesh on load.
- **Autosave** every 3–5 minutes and on key events, with a visible but unobtrusive indicator. On consoles, follow the platform's save-data rules (see `console-pathway`).
- **Cloud saves.** Steam Cloud and platform cloud have size quotas. Keep a `save_size` budget in the contract (for example under 100 MB per world) and test the quota path.
- **Version and migrate.** Every save carries a format version. Ship a migration for each version and a test that loads every archived save from earlier builds.

### 0.8 Co-op and server architecture
- **Listen-server (host-authoritative)** is the cheapest. One player hosts, others join by invite. Host leaving ends the session unless you implement host migration. Good for 2–8 players.
- **Dedicated server** costs money and operations but supports persistent worlds, always-on bases and PvP. Offer a downloadable server build so the community pays for hosting (a strong precedent in the genre).
- **Rented official servers** are a business line (monthly fee) and a support burden.
- **Authority.** The server owns inventory, damage and world edits. Clients predict movement and placement. Cheating in co-op matters less than desync bugs, which are the top review complaint.
- **Tick and bandwidth.** 20–30 Hz server tick, delta-compressed state, interest management by chunk. Test with a "20 clients, 300 ms RTT, 3% loss" profile.
- Details in `multiplayer-backend` and `game-architecture`.

## 1. Open-world survival-crafting

### Definition and player fantasy
The player is dropped into a hostile or indifferent wilderness with nothing, gathers materials, crafts tools, builds a shelter and a base, learns the region, and eventually conquers its hardest threats. The fantasy is *self-reliance turned into mastery*: "I started with a stick and now I own this valley." Variants add exploration of a strange world, a story spine, or monster-taming.

### Core loop
```
gather (wood, stone, food) → craft tools / weapons / structures
  → survive threats and needs (hunger, night, weather) → build and fortify base
  → explore to the next biome for rarer resources → boss or milestone → next tech tier
```

### Meta loops
- **Tech tiers.** Each tier opens new materials and recipes (§0.2). The tier ladder is the campaign.
- **Base growth.** From lean-to to fortress, with storage, crafting stations, farms and defences.
- **Exploration and map knowledge.** Biomes, dungeons, points of interest, fast-travel anchors.
- **Boss ladder.** Milestone bosses gate biomes. Loot from them unlocks the next tier.
- **Seasonal worlds or wipes** (PvP and some co-op servers): fresh starts each cycle.
- **Mod and workshop ecosystem** on PC. It keeps a game alive for years.

### Session profile
Estimate: PC sessions of 1–3 hours. Total playtime 50–300 hours for engaged players. Co-op groups play scheduled evenings. Short sessions work if the game autosaves and gives a clear "next 20 minutes" goal. Streams and videos drive discovery, so the game must be watchable.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Needs meters (hunger, thirst, warmth) | time & energy | §0.1. Budget 10–20% of session time |
| Gather, craft, tier-gated recipes | build-craft; progression & upgrade | §0.2. World-as-tech-tree |
| Free-form base building with snapping | build-craft | Structural integrity optional. Entity cap (§0.7) |
| Day-night and weather pressure | time & energy; exploration & traversal | §0.4 |
| Resource nodes with respawn rules | economy & resources | §0.3 |
| Combat with melee, ranged and stamina | combat | Readable telegraphs matter more than numbers |
| Boss gating | combat; progression & upgrade | Each boss drops the next tier's key resource |
| Inventory weight or slot limits | economy & resources | A sink that creates storage and logistics play |
| Procedural world and map | exploration & traversal | §0.6. Seeds shareable |

### Monetisation model and typical mix
Premium priced purchase, often through early access. Typical mix (qualitative, unsourced):
- Full-price base game, with a launch discount and later seasonal sales.
- Paid expansions that add a biome, boss ladder and recipes (the strongest revenue line after launch).
- Optional cosmetic DLC or a soundtrack and artbook bundle.
- Official server rental (optional).

Avoid selling progression or power. **Ethics flags:** selling "boost" items in a PvP survival game is pay-to-win; paid wipe-skips on competitive servers split communities. Premium plus expansions is the safest model. Free-to-play with a shop is rare here and risky.

### KPI expectations
Qualitative. Judge early access by wishlists, wishlist-to-purchase conversion, review score (aim for Very Positive or better), refund rate (watch the first two hours) and the share of players reaching tier 2. Streamer-driven spikes are typical: a good launch week can be followed by a steep decline unless updates ship. Retention is measured in hours played and in return after a content patch, not in D1/D7.

### Retention drivers
Mastery of the world, base pride, boss milestones, co-op friends, content updates (new biomes and bosses), mods, seasonal wipes, streamer events and a roadmap the community trusts.

### Content pipeline and production scope (estimates)
Systems first: gathering, crafting, building, AI, survival meters, save and streaming. Then content: biomes (art-heavy), enemies, bosses, recipes, audio. Rough estimate: 5–15 people and 2–4 years for a polished early access launch; a solo or 2–3 person team can ship a small one-biome version in 12–18 months. Plan a 6–18 month early access period with monthly patches.

### Reference titles
- *Minecraft* (Mojang, 2011): the template for survival mode on a voxel base.
- *Don't Starve* (Klei, 2013): the stylish, difficult single-player survival template.
- *Rust* (Facepunch, 2018 full release): PvP survival with raiding and wipes.
- *ARK: Survival Evolved* (Studio Wildcard, 2017): taming and servers.
- *Subnautica* (Unknown Worlds, 2018): survival with a strong story and one dangerous biome type.
- *Valheim* (Iron Gate, 2021): co-op-first, boss-gated tiers and a Norse theme.
- *Palworld* (Pocketpair, 2024): creature collection fused with survival crafting.
- *Enshrouded* (Keen Games, 2024): voxel terrain plus action RPG combat.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| The first hour is clear: a visible goal, a safe place, tools within minutes | The first hour is hunger spam and unguided wandering |
| The tech ladder is visible and each tier feels like a new game | Tiers are the same loop with bigger numbers |
| Base building is expressive and stable (no wobble, no clipping) | Building is fiddly, buggy or too restricted |
| Combat is readable and bosses are memorable | Combat is a stat check |
| Co-op just works (invites, joins, saves) | Desync, lost saves or host-only progression |
| A content roadmap ships on time during early access | Updates stall and the community leaves |

### Innovation vectors
- Survival plus automation (conveyor and machine logistics) or plus creature-taming.
- Tighter story spines in a survival frame.
- Accessible modes: relaxed needs, builder modes, no-death.
- Seasonal and wipe formats for single-player (new run with a modifier).
- Cross-play and console-first designs.
- Smaller, authored worlds with more density rather than huge empty maps.

### Agent-buildability: 3/5
**Why 3:**
- The single-player core (meters, crafting, gathering, building, save) is data-driven, unit-testable and bot-verifiable.
- The economy and tier timings can be simulated (§0.1–0.3).

**Why not higher:**
- Combat feel, animation, world art and atmosphere need human taste.
- World streaming and large-world performance need profiling on real hardware.
- Multiplayer is a separate product (see §2).

**What agents do well:** recipe tables, tier-time sims, spawn and resource validation, save migration tests, bot playthroughs to tier N, UI for crafting and inventory.

### Starter feature list (P0 vertical slice: one biome, single-player, one boss)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Procedural 2 km² biome from a seed (world) | Same seed gives byte-identical chunks in two orders. Spawn validation passes on 1,000 seeds |
| 2 | Hunger, thirst and warmth meters (survival) | Decay follows §0.1. Time to empty matches the tuning table within 1% |
| 3 | Gather wood, stone, food with tool tiers (gameplay) | Yield and respawn match §0.3 table. A bot reaches tier 2 in the target time |
| 4 | 20 recipes across 3 tiers with a recipe browser (progression) | `R(i)` totals shown. No cycle in the graph. Every raw input reachable |
| 5 | Snap-based building, 6 piece types (build) | Placement validated. Entity cap enforced. Save and reload keeps every piece |
| 6 | Day-night cycle with night spawns (gameplay) | Cycle length and night multiplier from the tuning file. Light blocks spawns in radius |
| 7 | 3 enemy types and one boss (combat) | Telegraphs shown. Boss drops the tier-3 key item. Scripted bot defeats it at target power |
| 8 | Inventory with weight or slots (economy) | Limits enforced. Stack rules unit-tested |
| 9 | Autosave with atomic write and two backups (tech) | Kill the process mid-write: the previous save loads. A migration test loads a v1 save |
| 10 | Relaxed and Hard presets (ux) | Presets change multipliers only. Recipes identical across presets |
| 11 | Controller and keyboard bindings with rebind (ux) | Every action reachable on both. Rebinds persist |
| 12 | Performance gate: stream at view distance 8 (tech) | Frame time under budget on the target spec. No hitch above 33 ms in a 10-minute flight |

### Platform notes
| Aspect | PC | Console | Web | Mobile |
|---|---|---|---|---|
| Input | Mouse and keyboard, deep rebinding, build-mode precision | Gamepad: radial menus, aim assist, snapping essential for building | Mouse and keyboard, small worlds | Touch: simplified building, auto-gather |
| Session | 1–3 h, alt-tab, long saves | 1–2 h, suspend and resume required, quick resume | 10–30 min, no large saves | 5–15 min, background kills |
| Performance | Scalable settings, mods, big view distances | Fixed targets (30 or 60 fps), memory caps, load time rules | WASM memory limits, small worlds | Thermal limits, small view distance |
| Business | Early access, wishlists, Steam sales, mods | Premium, certification, ratings, usually later than PC | Free demo or ad-supported | F2P with ads and IAP (different design) |

- On console, building with a gamepad needs a purpose-built UI. Budget a full pass for it.
- Early access is a PC route. Console programmes generally expect a finished product, so ship PC first and port after 1.0 (verify current programme rules in `console-pathway`).
- For web, keep worlds under about 50 MB of save data and use IndexedDB. See `platform-targets`.

## 2. Co-op survival

### Definition and player fantasy
A small group (2–8) survives together, usually on one shared world hosted by a player or a dedicated server. The fantasy is *a team of friends against the wild*: dividing roles, building a base together, telling stories later. The social bond is the product, and the survival layer is the excuse.

### Core loop
```
group sets a goal for the evening (tier, boss, build) → roles split (gatherers, builders, fighters)
  → shared base grows → danger spike (night, boss, raid) is handled together
  → shared loot and progression → log off with a plan for next session
```

### Meta loops
- **Persistent shared world.** The base survives between sessions and anyone can contribute.
- **Role specialisation.** Builder, hunter, cook, explorer. Skill trees or tool specialities reinforce this.
- **Group progression.** Shared tech unlocks or personal unlocks gated by the group's boss kills.
- **Seasons and challenge modes.** New difficulty modifiers and time-limited worlds.
- **Community servers and mods.** Hosting is a social act.

### Session profile
Estimate: scheduled sessions of 2–4 hours, once or twice a week per group. The unit of retention is the group, not the player. If one member drops out, the group often dissolves. Drop-in and drop-out must be painless (late joiners catch up without breaking balance).

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Shared world and base | build-craft; social & competition | Permissions: who can build, open chests, remove pieces |
| Difficulty scaling by player count | combat; progression & upgrade | Enemy HP and spawn scale with players, with a sub-linear curve (for example HP × (1 + 0.6 · (n − 1))) |
| Resource sharing (shared chests, trading) | economy & resources | Prevent one player hoarding. Offer a team vault |
| Revive and respawn rules | combat; time & energy | Down-but-not-out state keeps teams playing. Corpse-run tension is optional |
| Voice and ping system | social & competition | Context pings reduce chat-dependence and help non-English groups |
| Host migration or dedicated server | UX automation | Host leaving must not wipe progress |
| Shared and personal progress | progression & upgrade | Decide per-player versus per-world progression and say so in the UI |
| Friendly-fire options | combat | Off by default, on as a hardcore toggle |

### Monetisation model and typical mix
Premium purchase, often discounted for group bundles ("buy 4"). Typical mix (qualitative):
- Base game, with Steam "friend pass" or share-key schemes only where the platform allows.
- Expansions and cosmetic DLC.
- Server rental or a hosted-server partner.
- No loot boxes, no pay-to-win.

**Ethics flags:** selling stat boosts breaks group fairness. Cosmetics and content packs are the safe lines.

### KPI expectations
Qualitative. Watch concurrent players against launch peak, average session length, share of sessions with two or more players, and the number of groups with a world older than 30 days. A good co-op game has long-tail Steam concurrents driven by sales and updates.

### Retention drivers
The group's shared story, a base worth protecting, a boss list to finish, seasonal modifiers, and a game that is fun even when only two of five friends are online.

### Content pipeline and production scope (estimates)
Same systems as §1 plus netcode, server tooling and permission systems. Netcode and desync fixing is often 20–30% of engineering time (estimate). Co-op multiplies test cases: join mid-fight, host leaves, inventory races, save of a world with four players. Rough estimate: 8–20 people for 2–4 years, or a small team with a mature middleware stack and a narrow scope.

### Reference titles
- *Valheim* (Iron Gate, 2021): 2–10 players, boss-gated tiers.
- *The Forest* and *Sons of the Forest* (Endnight, 2018 and 2024): horror survival for small groups.
- *Grounded* (Obsidian, 2022): backyard-scale survival, strong co-op.
- *Raft* (Redbeard, 2022): a simple loop with a strong group identity.
- *Project Zomboid* (The Indie Stone): deep simulation, co-op on servers.
- *Don't Starve Together* (Klei, 2016): the co-op follow-up to the single-player game.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Joining is two clicks and a friend code | Joining needs port-forwarding or a guide |
| Difficulty scales gently with group size | Four players trivialise content, or one player cannot progress alone |
| The host leaving or crashing loses nothing | World corruption on co-op saves |
| Roles feel distinct without being mandatory | Every player does the same thing, or one role carries the group |
| Updates ship regularly | A single content drop and then silence |

### Innovation vectors
- Asymmetric group goals and optional "team plan" cards.
- Cross-play between PC and console.
- Drop-in async co-op (a friend's base visited by others).
- Co-op campaigns with authored story beats.
- Better onboarding for groups of mixed skill (assist modes per player).

### Agent-buildability: 2/5
**Why low:**
- Netcode, latency and desync behaviour cannot be fully verified with client-only gates.
- Scale and edge cases (late join, host loss) need live testing with real network conditions.

**What agents do well:** permission tables, scaling formula sims, bot clients that join and play scripted routines, network soak tests with simulated loss, UI for lobby and invites.

### Starter feature list (P0 vertical slice: 2–4 players, listen server)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Host-authoritative world state (net) | A client cannot alter inventory or world without a server-validated action |
| 2 | Invite by friend code or platform invite (net) | Two clients join in under 15 s on a LAN test and survive a join during combat |
| 3 | Late-join snapshot (net) | A client joining mid-session sees identical world state to the host (hash check) |
| 4 | Difficulty scaling by player count (gameplay) | Boss HP follows the formula. Sim shows clear time within target band for 1–4 bots |
| 5 | Shared base with build permissions (build) | Permission tests: guest cannot remove owner pieces unless allowed |
| 6 | Revive and respawn rules (gameplay) | Downed state timer from tuning. A teammate revives with the listed cost |
| 7 | Ping wheel and text chat (ux) | Pings visible to all within 200 ms of the simulated link |
| 8 | Host leaves → save and return (tech) | Kill the host mid-session: the world loads intact on restart. Clients see a clear message |
| 9 | Network soak test (qa) | 4 bot clients for 30 min at 150 ms RTT and 3% loss: zero desync flags |
| 10 | Dedicated server build (net) | The same world runs headless. Saves load in both modes |

### Platform notes
| Aspect | PC | Console | Web | Mobile |
|---|---|---|---|---|
| Input | Keyboard and voice chat via a third-party app | Gamepad, platform party chat, text entry is awkward | Browser chat, shareable link joins | Touch with simple pings |
| Session | Scheduled evenings, Discord | Party-based, platform invites | Short, link-driven | Short rounds only |
| Performance | Host PC doubles as server: cap player count and entity count | Host console is weaker: lower caps or use dedicated hosting | Server needed (WebSocket or WebRTC) | Not recommended for 8+ players |
| Business | Server rental, friend bundles | Cross-play rules and platform online fees apply to players | Free with ads | F2P co-op, different design |

- Cross-play needs an account or ID layer and platform approval. Check current rules in `console-pathway`.
- Offer a text-chat filter and a report tool even in small co-op: public servers invite abuse. See `mmo-live-service.md` §0.4.

## 3. Creative / voxel sandbox

### Definition and player fantasy
A block or voxel world the player can reshape without limits. Creative mode removes survival pressure. Survival-lite modes add light goals. The fantasy is *infinite building*: a castle, a computer inside the game, a city, a map for others. User-generated worlds are the content engine.

### Core loop
```
pick a project idea → gather or conjure blocks → place, shape and detail
  → test (redstone-like logic, vehicles, gameplay) → show to others (screenshots, servers, marketplace)
  → next idea inspired by others
```

### Meta loops
- **Portfolio and sharing.** Worlds, builds and schematics shared via workshop or marketplace.
- **Logic and automation.** In-world circuits, scripting or visual blocks create a second game inside the first.
- **Challenge and survival layers.** Adventure maps, custom game modes, minigame servers.
- **Creator economy.** Marketplace content, server communities and sponsorships.
- **Seasonal themes and build contests.**

### Session profile
Estimate: 30 minutes to 3 hours, open-ended and personal. A project can span weeks. Social servers have scheduled events. The loop is intrinsically motivated, so the game must make creation fast and failure safe (undo, copy, paste).

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Place and break voxels | build-craft | Latency from input to change must feel instant (under 100 ms) |
| Creative inventory and palette | build-craft; UX automation | Search, favourites, hotbar presets |
| Undo, redo, copy, paste, mirror, fill | UX automation | The most-used tools by power builders. Bound by world edit cost |
| In-world logic (circuits, scripting) | build-craft; progression & upgrade | Gate complexity with a simulation tick budget |
| Fluids, gravity and light propagation | exploration & traversal; build-craft | Costly to simulate. Cap update rates per tick |
| Multiplayer building with permissions | social & competition | Region claims, roles, rollback |
| Mod, texture pack and marketplace support | economy & resources | See `economy-design` for creator revenue splits |
| Seeds and world generation presets | exploration & traversal | §0.6 |

### Monetisation model and typical mix
- Premium purchase for the base game.
- Marketplace for skins, maps and packs with a creator revenue share.
- Cosmetic bundles, seasonal packs and realms-style subscriptions for hosted worlds.
- Education editions sold to schools.

**Ethics and legal flags:** user-generated content needs moderation and a takedown process (see `legal-ethics`). Child-heavy audiences raise age and chat rules (COPPA and equivalents). Licence the use of marketplace content clearly.

### KPI expectations
Qualitative. Look at hours per player, creations per player, share of players who share a world, and marketplace conversion. Long-tail revenue is driven by the community. Churn is tied to age: young players grow up, so the funnel must keep refilling.

### Retention drivers
Creative autonomy, social display, mods and marketplace, servers and minigames, a very low skill floor with a very high ceiling, and regular content that expands the palette.

### Content pipeline and production scope (estimates)
The voxel engine, editing tools and multiplayer are the heavy parts. Content is block sets, biomes, mobs, textures and sounds. Rough estimate: 10–40 people for a competitive new entrant. A small team can build a niche sandbox (for example a 2D or low-poly one) in 18–24 months. A strong modding API multiplies content for free but adds support cost.

### Reference titles
- *Minecraft* (Mojang, 2011): the genre.
- *Terraria* (Re-Logic, 2011): a 2D sandbox with action progression.
- *Roblox* and *Fortnite Creative / UEFN*: platform-style sandboxes (see `mmo-live-service.md` §6).
- *Teardown* (Tuxedo Labs, 2022): destructible voxels as a puzzle-heist sandbox.
- *Core Keeper* (Pugstorm, 2022): 2D co-op sandbox with automation.
- *Space Engineers* (Keen Software House): sandbox with physics and building on blocks.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Building is fast, with strong tools and low friction | Tools are clumsy or the UI buries the palette |
| Worlds persist and share easily | Sharing needs file hunting |
| Performance holds with huge builds | Big builds crash the frame rate or the save |
| A modding API and community content thrive | The ecosystem is closed or legally tangled |
| Safe for children with moderation | Moderation lapses cause scandal and platform removal |

### Innovation vectors
- Destruction and physics as a first-class building tool.
- Natural-language or AI-assisted build helpers (with provenance and moderation controls).
- Cross-platform worlds with cloud saves.
- Voxel plus survival-lite goals for guided onboarding.
- Education and STEM modes with lesson packs.

### Agent-buildability: 3/5
**Why 3:**
- Voxel editing tools, undo stacks, save and world formats are testable.
- Chunk meshing and streaming have clear performance metrics.

**Why not higher:**
- The "feel" of building, art style and block design need taste.
- Community and marketplace are operational, not code.

**What agents do well:** edit-tool test suites (fuzz undo and redo), chunk-meshing benchmarks, save fuzzing, block data tables, UI for palette and tools.

### Starter feature list (P0 vertical slice)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Chunked voxel world with place and break (core) | Place latency under 100 ms. 100,000 random edits then reload gives an identical hash |
| 2 | 40-block palette with search and hotbar (ux) | Search finds each block by name. Hotbar persists |
| 3 | Undo and redo for 100 operations (tools) | Fuzz test: random edit sequences undo to the original hash |
| 4 | Fill, copy, paste, mirror tools (tools) | Operations on 1 M blocks complete under 2 s on the target spec |
| 5 | Creative flight and camera (gameplay) | Speed and collision follow the tuning table |
| 6 | World save format with versioning (tech) | Round-trip and migration tests pass. Size under budget |
| 7 | Greedy meshing with LOD (tech) | Frame time under budget at view distance 8 in the benchmark world |
| 8 | Simple logic blocks: switch, wire, lamp (build) | Truth table tests. Update rate capped per tick |
| 9 | Export and import a schematic file (tools) | Import preserves every block. Size limits enforced |
| 10 | Local multiplayer building with region claims (net) | A guest cannot edit outside a claimed region. Rollback restores state |

### Platform notes
| Aspect | PC | Console | Web | Mobile |
|---|---|---|---|---|
| Input | Mouse and keyboard is best for precision and tools | Gamepad needs snap, radial menus and a build assist | Mouse and keyboard, small worlds | Touch building is slow: simplified tools and a pencil mode on tablets |
| Session | Long project sessions | Couch play, split-screen is a plus | Quick shared builds | Short bursts |
| Performance | Mods and large view distances | Memory limits on world size | WASM memory limits, low draw distance | Thermal and battery limits |
| Business | Premium, workshop, marketplace | Marketplace and platform cut | Ads or free demo | Premium or F2P with marketplace |

- Cross-platform worlds raise differences in memory and input. Set a world-size cap that every target can load.
- Platform holders each have their own user-generated content rules. Check `console-pathway`.

## 4. Colony sim

### Definition and player fantasy
The player guides a small group of autonomous characters (colonists, settlers, dwarves) who survive and build a settlement. The player gives orders and priorities, not direct control, and the simulation tells stories out of needs, moods, accidents and conflict. The fantasy is *the storyteller*: "my colony's worst winter, the cook who went mad, the last-stand defence."

### Core loop
```
assess colony (needs, threats, stockpiles) → set work priorities and build orders
  → colonists haul, build, farm, craft → events (raid, weather, illness, mood break)
  → handle crisis, recover → grow the colony and tech → next crisis
```

### Meta loops
- **Tech research** unlocking buildings and gear.
- **Storyteller or event director.** A system that paces events (see §4 design note).
- **Colonist stories.** Traits, relationships, mental breaks, deaths.
- **Scenario and difficulty presets.** Fixed starts and challenge modes.
- **Mod workshop.** A big share of the long tail.

### Session profile
Estimate: 1–4 hours, with time controls (pause, 1×, 2×, 3×). Saves of 100–1,000 hours are common. Pause-and-plan makes it playable in short bursts. Content is dense, so the UI must handle information well (see `simulation-management.md` §0.4).

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Autonomous agents with needs and moods | economy & resources; time & energy | Agent cost grows with population (§0.3 in `simulation-management.md`) |
| Work priority and job assignment | UX automation; economy & resources | Priorities grid per colonist and per job type |
| Zone, stockpile and build designation | build-craft | Player orders rather than direct moves |
| Event director (storyteller) | live events; progression & upgrade | Paces threats by colony wealth and recent events |
| Mood and mental break system | social & competition; time & energy | Breaks are story generators. Provide readable causes |
| Pathfinding with terrain costs | exploration & traversal | Cache paths. Budget CPU per tick |
| Tech tree and research | progression & upgrade | §0.2 |
| Health, injury and medicine | combat; economy & resources | Body-part models add depth and cost |

**Event director rule of thumb:** target a threat "budget" that rises with colony wealth `W` and decays after each event: `budget(t+1) = budget(t) + k · W − spent`. Draw events whose cost fits the budget, space them by a minimum cooldown (for example 1–3 in-game days), and never fire two lethal events within the same cooldown. Test with bots that play a passive and an aggressive style.

### Monetisation model and typical mix
Premium purchase with expansions and DLC. A mod workshop supports the long tail. Typical mix (qualitative):
- Base game at a mid price.
- Large expansions adding systems (ideology, biotech and similar content packs).
- Soundtrack and small cosmetic DLC.

No monetisation of power. Ethics: do not gate the core experience behind multiple small paid expansions without clear labelling.

### KPI expectations
Qualitative. Hours played, review score, refund rate, expansion attach rate, mod count and the share of players with saves over 50 hours. Long-tail sales are stable because word of mouth and workshop content bring new players for years.

### Retention drivers
Emergent stories, depth of systems, mod ecosystem, scenarios and difficulty ladders, expansions that add new play styles.

### Content pipeline and production scope (estimates)
Simulation systems dominate, with a modest art budget (2D or low-poly). Content is items, buildings, events and traits. Rough estimate: 3–10 people, 2–4 years. Solo developers have shipped hits here, so the scope is feasible for small teams with strong simulation skills. The mod API is a design decision from day one.

### Reference titles
- *Dwarf Fortress* (Bay 12 Games; Kitfox and Tarn Adams' Steam release, 2022): the depth benchmark.
- *RimWorld* (Ludeon Studios, 2018): the storyteller model.
- *Oxygen Not Included* (Klei, 2019): physics-driven colony systems.
- *Banished* (Shining Rock Software, 2014): lean, harsh survival city.
- *Against the Storm* (Eremite Games, 2023): colony city roguelite.
- *Prison Architect* (Introversion, 2015): job and zone logic in a themed colony.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| The sim generates stories players retell | The sim is opaque and failure feels random |
| The UI explains why things happen (tooltips, logs, overlays) | Players cannot trace a death or breakdown to its cause |
| Pause and speed controls are fast and reliable | The game runs slowly at 3× with large colonies |
| Systems interlock without exploding | Feature creep produces unfixable balance and bugs |
| The mod API is stable | Mods break on each patch |

### Innovation vectors
- Colony sim with roguelite run structure.
- Narrative-driven event directors with authored arcs.
- Shared-world or asynchronous multiplayer colonies.
- AI-assisted storytellers (with deterministic fallback for saves).
- Console-first colony sims with controller-friendly priority UI.

### Agent-buildability: 4/5
**Why 4:**
- The simulation is deterministic with a fixed tick and a seed, so it is unit-testable and bot-playable.
- Balance sims run in headless mode and find exploits.
- The UI is mostly information display.

**Why not 5:**
- Making the stories feel good, UI clarity and art direction need human taste.
- Performance at 100+ agents needs profiling.

**What agents do well:** event director sims, job scheduling tests, pathfinding benchmarks, save and load fuzzing, headless fast-forward balance runs.

### Starter feature list (P0 vertical slice: 6 colonists, one map)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Deterministic tick with pause and 1×/2×/3× speeds (core) | Same seed and inputs produce identical state hashes after 10,000 ticks |
| 2 | 6 colonists with needs and mood (sim) | Need decay per tuning table. Mood threshold triggers a break as specified |
| 3 | Work priorities grid (ux) | Higher priority is picked first in 1,000 randomised cases |
| 4 | Build, haul and stockpile designations (build) | A bot builds a shelter from scratch within the target time |
| 5 | Farming and cooking chain (economy) | Ratios from the tuning table. No deadlock when a stockpile is full |
| 6 | Event director with budget (live) | No two lethal events inside cooldown across 1,000 simulated runs |
| 7 | Raid with simple combat and injuries (combat) | Colonists with equipment win at the specified win rate |
| 8 | Research tree, 12 nodes (progression) | Prerequisites enforced. Unlocks appear in the build menu |
| 9 | Overlay and tooltip explanations (ux) | Every need and mood effect lists its sources |
| 10 | Save and load of 10,000 entities (tech) | Round-trip hash identical. Save under 5 MB. Load under 3 s |
| 11 | Performance: 6 → 40 colonists (tech) | Tick time under budget at 40 colonists on the target spec |

### Platform notes
| Aspect | PC | Console | Web | Mobile |
|---|---|---|---|---|
| Input | Mouse and keyboard: drag zones, hotkeys, dense menus | Gamepad: cursor mode, radial menus, simplified priority UI | Mouse and keyboard, lighter sim | Touch: large controls, simplified tooltips |
| Session | Long, with pause and plan | Couch sessions, suspend and resume | Short | Short, offline-friendly |
| Performance | CPU-bound tick, multi-thread jobs | Fixed CPU budget, cap colonists | Single-thread limits in the browser | Cap entity counts |
| Business | Premium, expansions, workshop | Premium and expansions, mods are limited by platform rules | Free demo | Premium port or F2P (different design) |

- Console ports need a controller-first priority and zone UI. Budget this as a separate design pass.
- Mods on console are subject to platform policy. Verify before promising them.

## 5. Survival roguelite

### Definition and player fantasy
A run-based game: each run places the player in a generated world with a survival constraint (hunger, a closing storm, a wave timer), and death resets the run while permanent meta-progression carries over. The fantasy is *one more run*: a new build, a new route, a better understanding of the threat.

### Core loop
```
start a run with a small kit → gather, craft and fight under a pressure clock
  → make routing and build choices (what to carry, where to go)
  → survive a boss or a time limit, or die → bank meta currency or unlocks
  → spend on permanent upgrades → start another run
```

### Meta loops
- **Permanent unlocks.** Characters, recipes, starting kits, mutators.
- **Difficulty ladders.** Heat or ascension levels for mastery players.
- **Daily or weekly seeds.** Shared challenge runs with leaderboards.
- **Collections.** Item codex, achievements, cosmetics.
- **Co-op runs** (optional, small groups).

### Session profile
Estimate: 20–60 minute runs, with a few runs per session. Between runs, a short meta menu. Short runs fit PC, console and handheld play (including Steam Deck and Switch-class hardware). Sessions of 1–2 hours are typical.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Pressure clock (storm, hunger, waves) | time & energy | Sets run length. Tune with the decay maths of §0.1 |
| Procedural run layout | exploration & traversal | §0.6, with validation for fairness |
| Crafting under constraint | build-craft | Short tree (2 tiers), fast crafting |
| Build-defining finds | collection & randomness | Synergies, not just stat boosts |
| Permadeath with meta-progression | progression & upgrade | Balance meta power against skill. Keep the first win achievable without meta |
| Daily seed | live events | Same seed for everyone. Leaderboard of score or time |
| Risk-reward routing | exploration & traversal; economy & resources | Extra resources cost time or danger |
| Run summary and unlock reveal | UX automation | Death must teach: show what killed you |

### Monetisation model and typical mix
Premium at a lower price (typical of PC indie), with an optional DLC for new characters or biomes. Console ports follow. No loot boxes. Mobile versions can use ads with rewarded revives, but that changes the design.

### KPI expectations
Qualitative. Look at run completion, average runs per session, win rate by ascension, daily seed participation and review score. Retention depends on mastery depth and content cadence. A premium roguelite is judged by its Steam reviews more than by retention curves.

### Retention drivers
Mastery, build variety, meta unlocks, daily seeds, ascension ladders, new content drops, community challenges and streamer interest.

### Content pipeline and production scope (estimates)
Content-heavy but modular: items, enemies, biomes, events and bosses are data entries. Rough estimate: 2–8 people and 12–30 months. Procedural layout plus a bot-driven balance loop lets a small team reach large perceived content.

### Reference titles
- *Don't Starve* (Klei, 2013): survival with permadeath in the core game.
- *Dome Keeper* (Bippinbits, 2022): mining and defence in alternating phases.
- *Tribes of Midgard* (Norse Games, 2021): co-op roguelite with day-night defence.
- *Against the Storm* (Eremite, 2023): city-building roguelite with a closing threat.
- *Rogue-lite survival hybrids* in general: *Vampire Survivors*-style games share the pressure clock but are covered in `action-arcade-roguelite.md`.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Runs are 20–40 minutes and every run differs | Runs are long and repetitive |
| Death is informative and fast to restart | Death feels arbitrary |
| Meta unlocks add options, not just power | Meta power makes early runs trivial |
| The pressure clock creates choices | The clock is only a nuisance |
| Daily seeds create community moments | Seeds are unfair or unreproducible |

### Innovation vectors
- Colony or base management inside a roguelite run.
- Co-op roguelite survival with shared meta.
- Narrative layers across runs.
- Mutator systems made by the community.
- Seeded weekly competitions with prizes.

### Agent-buildability: 4/5
**Why 4:**
- The run is deterministic given a seed and fully botable.
- Balance and fairness are testable with solvers and large sims (`what-if`, `balance`).
- Data-driven content scales well.

**Why not 5:**
- Feel (combat, audio, art) and variety need human taste.
- Meta-progression tuning needs real players.

**What agents do well:** seed validators, bot runs for win-rate bands, item synergy checks, daily seed pipeline, run-summary UI.

### Starter feature list (P0 vertical slice: 3 biomes, one boss)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Seeded run generator (world) | Same seed gives an identical run. 1,000 seeds pass validation (reachable exit, resources present) |
| 2 | Pressure clock with a visible meter (core) | Clock length from the tuning table. Full run fits the target band for the bot |
| 3 | 2-tier crafting, 12 recipes (build) | Graph has no cycles. All inputs reachable in every seed |
| 4 | 8 enemy types and one boss (combat) | Telegraphs shown. Boss beatable by the scripted bot at target power |
| 5 | 30 finds with at least 6 synergies (progression) | Synergy table tested. No single find gives a guaranteed win in sim |
| 6 | Permadeath and run summary (ux) | Run state clears on death. Summary shows cause of death and unlocks |
| 7 | Meta unlock tree, 15 nodes (meta) | Currency ledger balances. First win possible with zero unlocks (bot check) |
| 8 | Daily seed with local leaderboard (live) | Seed derived from the date. Scores validated by replay |
| 9 | Save and resume mid-run (tech) | Kill the process: resume on the same tick. Run hash matches |
| 10 | Gamepad and keyboard support (ux) | Full run playable on both. Rebinds persist |

### Platform notes
| Aspect | PC | Console | Web | Mobile |
|---|---|---|---|---|
| Input | Keyboard and mouse or gamepad | Gamepad-first, aim assist | Keyboard and mouse | Touch: simplified controls, auto-aim |
| Session | 20–60 min runs, quick restart | Quick resume, suspend mid-run | 10–20 min runs | 5–15 min runs |
| Performance | Wide spec range, scalable | Fixed targets (60 fps expected), small load times | Small download, fast start | Battery and thermal limits |
| Business | Premium plus DLC, Steam Next Fest demo | Port after PC, platform sales | Free demo or portal ads | Ads with rewarded revive, or premium |

- A demo during a Steam Next Fest is the best discovery tool for a premium roguelite. Check dates in the volatile facts section.
- Steam Deck and Switch-class hardware favour short runs and readable UI at small sizes. See `platform-targets`.

## Volatile facts (as of Oct 2026 — verify before relying)

- Steam reached about 43.5 million concurrent logged-in users on 11 Oct 2026 (SteamDB figure reported by press), with about 14.5 million in a game. The earlier 2026 record was about 41.8 million in January. Valve's own page showed slightly different numbers. Concurrent users include people with the client open — [Notebookcheck](https://www.notebookcheck.net/Steam-sets-a-new-all-time-concurrent-player-record-after-surpassing-42-million-users-online.1201788.0.html), [Dot Esports](https://dotesports.com/general/news/steam-all-time-record-43-5-million-concurrent-users)
- Steam Next Fest ran 19–26 Oct 2026 (10 AM PDT start and end). Valve also ran a PvE Survival Crafting Fest on 31 Aug – 7 Sep 2026. Valve publishes its festival schedule through July 2027 — [God Is a Geek](https://godisageek.com/2026/10/steam-next-fest-october-2026/), [Digital Citizen](https://www.digitalcitizen.life/valve-reveals-full-steam-sale-and-festival-schedule-through-july-2027/)
- Steam store terms (revenue share tiers and the per-app fee) change rarely but are not verified in this session. Check the current figures at [Steamworks documentation](https://partner.steamgames.com/doc/gettingstarted) before budgeting.
- No sourced figures for survival-genre share of Steam releases or early-access conversion were found in the October 2026 research. Any such number in the wider ecosystem is unverified — treat it as an estimate.
- Console early access is not a standard route. Check each platform programme (`console-pathway`).

## Related skills
- `mechanics-codex`: cards for every mechanic named above.
- `procedural-generation`: world, biome and run generators with validators.
- `economy-design`: sinks, sources, respawn and recipe economics.
- `balance`: tier-time sims, win-rate bands, bot runs.
- `multiplayer-backend`: listen and dedicated servers, desync, saves.
- `game-architecture`: sim-core, ECS, chunk streaming.
- `qa-testing`: save fuzzing, bot soak tests.
- `platform-targets`, `pc-web-release`, `console-pathway`: input, release and certification differences.
- `idle-tycoon-sim.md`, `action-arcade-roguelite.md`: mobile farming, life sim and survivor-like playbooks, not repeated here.
- `simulation-management.md`, `mmo-live-service.md`: sibling playbooks for colony and automation depth and persistent worlds.
