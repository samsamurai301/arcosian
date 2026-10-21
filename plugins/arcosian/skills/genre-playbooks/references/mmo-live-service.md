# MMO and Live-Service Playbooks

MMO and live-service games sell a place and a calendar: a persistent world or a continuously updated game that players return to for years. They are the highest-revenue and highest-risk family on PC and console. The product is not a build but an operation: servers, seasons, moderation, anti-cheat and a team that ships on a schedule. This file holds five playbooks in a shared 14-part template plus a "Platform notes" part:

1. MMORPG (theme-park and sandbox)
2. Survival MMO
3. Live-service looter shooter / ARPG
4. Creator platforms (Roblox experiences, Fortnite UEFN islands)
5. Seasonal live games

Six foundations come first: concurrent-user and server cost maths, content cadence and seasons, player-trading economies, community and moderation, anti-cheat, and end-of-service planning. The pattern for an agent pipeline is stark. Agents can build and verify the client slice, the economy sims, the content pipeline and the tooling (1–3/5). They cannot run the live operation, so most full-scale MMO projects score 1–2/5. Creator-platform islands and seasonal single-slice games score highest (3–4/5), because the platform carries the servers. Mobile MMORPGs and gacha live games are in `rpg-gacha.md`, and mobile live-ops fundamentals are in `liveops`; this file does not repeat them. Market numbers live in the dated volatile-facts section.

## Contents

| § | Playbook | Session profile (estimate) | Primary monetisation | Agent-buildability | First project for an agent pipeline? |
|---|---|---|---|---|---|
| 0 | [Shared foundations](#0-shared-foundations) | — | — | — | Read first |
| 1 | [MMORPG](#1-mmorpg-theme-park-and-sandbox) | 2–4 h sessions, daily and weekly raid cycles | Subscription or buy-to-play plus expansions, cosmetics | 1/5 | No, single-zone vertical slice only |
| 2 | [Survival MMO](#2-survival-mmo) | 1–4 h sessions, persistent bases | Premium or subscription, cosmetics, server rental | 1/5 | No, single-player or co-op slice first |
| 3 | [Looter shooter / ARPG](#3-live-service-looter-shooter--arpg) | 20–60 min activities, weekly resets | Premium plus expansions, season pass, cosmetics | 2/5 | Possible, as a single-player loot loop |
| 4 | [Creator platforms](#4-creator-platforms-roblox-experiences-fortnite-uefn-islands) | 10–40 min rounds | Platform engagement payouts, in-experience purchases | 3/5 | Yes, a single experience |
| 5 | [Seasonal live games](#5-seasonal-live-games) | 20–90 min sessions, 8–13 week seasons | Season pass, cosmetics, premium | 3/5 | Yes, with a season content pipeline |
| — | [Volatile facts](#volatile-facts-as-of-oct-2026--verify-before-relying) | — | — | — | Check before quoting numbers |

## How to use these playbooks

- Copy the core loop into `contract.json → loops[]`. Set `meta.genre: "mmo"` or `"live_service"` and `meta.subgenre` to the playbook slug. Set `meta.platforms` and `meta.input`, then set `technical.multiplayer` (`realtime` is the usual value). That field and the expected peak concurrent users drive cost more than anything else.
- Turn the starter feature list into P0 `features.json` entries with `gs.py feature add`. Each acceptance criterion maps to `unit`, `playthrough` or `load_test` gate evidence (bots, simulated clients, soak tests).
- Mechanic category labels: combat, build-craft, collection & randomness, progression & upgrade, economy & resources, time & energy, social & competition, exploration & traversal, live events, UX automation. Resolve them with `gs.py kb "<mechanic>" --skill mechanics-codex`.
- Platform differences (input, session, performance, business model) are in each playbook's "Platform notes" part. See also `platform-targets`, `pc-web-release` and `console-pathway`.
- Before any greenlight, answer three questions in writing: who runs the servers, who runs the calendar, and who answers players at 3 a.m. If the answer is "nobody", pick a smaller playbook or a creator platform.
- KPI statements are qualitative unless sourced. Use the anchors in the volatile-facts section.

## 0. Shared foundations

### 0.1 Concurrent users and server cost maths
Plan servers from peak concurrency, not from sales.

```
Daily actives            DAU = MAU · (DAU/MAU)             stickiness 0.2–0.4 is a typical planning range (estimate)
Average concurrency      CCU_avg = DAU · h / 24            h = average hours played per active day
Peak concurrency         CCU_peak = CCU_avg · p            p = peaking factor, 2–3 (estimate; check your region mix)
Worked example: MAU 500,000 · DAU/MAU 0.30 → DAU 150,000 · h = 2 → CCU_avg = 12,500 · p = 3 → CCU_peak = 37,500
```

```
Cost per player-hour     c = server_cost_per_hour / players_per_server
Worked example (illustrative prices): a 64-player instance costs $0.30/hour → c = $0.0047
  150,000 DAU × 2 h = 300,000 player-hours/day → $1,406/day ≈ $42,000/month
  Required server revenue per DAU = 1,406 / 150,000 = $0.0094 (about one US cent of ARPDAU)
```

- **Servers are one cost line.** Add bandwidth, databases, matchmaking, anti-cheat, customer support, moderation and live-ops staff. People cost more than machines for most live games.
- **Headroom.** Provision for peak plus 30%. Launch day is typically 3–10× the steady state (estimate). Use autoscaling where the world allows it and queues where it does not.
- **Sharding versus a single world.** Sharded realms are simple but fragment the community and the economy. A single logical world needs interest management and cross-server services. Instanced activities (dungeons, raids, matches) scale horizontally and are the cheapest content to serve.
- **Login queue.** A queue is better than a crash. Show position and an estimate, and keep a small reserve for returning players.
- **Load test early.** Build a simulated-client harness (bots that log in, move, fight, trade) in the first month. Test at 2× the planned peak. Measure tick time, database writes per second and the 99th percentile latency.
- **Per-region deployment.** Latency above about 150 ms hurts action combat, while tab-target MMO combat tolerates more (estimate). Pick regions from the wishlist or marketing data.
- Details of backends, matchmaking and persistence are in `multiplayer-backend`. Pricing and ARPDAU modelling are in `monetization` and `economy-design`.

### 0.2 Content cadence and seasons
Players consume content faster than teams make it. Cadence is the plan that bridges the gap.

```
Consumption time          t_c = hours of new content / hours played per week by the target player
Worked example: 40 hours of new content in a 12-week season, committed players play 15 h/week
  t_c = 40 / 15 = 2.7 weeks → the remaining 9.3 weeks need repeatable systems (weekly resets, challenges, events)
Production ratio          ρ = dev weeks per week of content   (target below 6 for a sustainable live team, estimate)
```

- **Layer the calendar.** Daily (quests, login), weekly (reset, raid lockout, challenge set), seasonal (8–13 weeks, new theme, pass, ladder reset), yearly (expansion or major release). The structure and templates are in `liveops`.
- **Repeatable versus new content.** Aim for roughly 70% repeatable systems (random activities, procedural dungeons, ladders) and 30% handmade content in a season (estimate, tune to the team).
- **Season design.** Each season needs a theme, a new reward track, a fresh meta-shift (balance changes, new mechanics) and a clear start and end. Publish the roadmap 4–8 weeks ahead and hit the dates.
- **Content freeze and hotfix lanes.** Keep a lane for emergency fixes and a branch policy so a hotfix never carries half-finished content.
- **Tuning windows.** Changes to power need a public test realm or at least a week of telemetry before a season ends.
- **Do not let the calendar eat the game.** Fear of missing out (FOMO) mechanics that punish absence create burnout. Offer catch-up and "evergreen" paths. See `player-psychology` and `legal-ethics`.

### 0.3 Player-trading economies
Trading lets players create value, and also lets exploiters create inflation.

```
Money supply change per day   ΔM = faucets − sinks
Worked example: faucets 10 M/day, sinks 8 M/day → ΔM = +2 M/day on M = 500 M → +0.4%/day
  After 30 days: 1.004^30 ≈ 1.127 → about 12.7% more currency chasing the same goods
```

- **Track faucets and sinks by source.** Log every creation and destruction of currency and items with a reason code. Build a daily dashboard (`player-analytics`, `economy-design`).
- **Sinks that players accept.** Transaction taxes (auction house fees of about 5–10%, estimate), repair costs, crafting fees, cosmetic upgrades, land rent. Avoid sinks that feel like punishment.
- **Bind rules.** Bind-on-pickup protects raid rewards. Bind-on-equip allows trade. Choose per item class and state it in the tooltip.
- **RMT and gold selling.** Real-money trading harms the economy and draws bots. Provide a legal trade path (a cash-shop currency that can be sold in-game, or a cosmetic marketplace) or enforce hard bans and detection. Pick one policy and publish it.
- **Duplication exploits.** Every trade is a transaction in a ledger with idempotency keys and server-side validation. Keep rollback tools and the ability to freeze trading quickly.
- **Market tools.** Search, price history, sell-through rate, and regional markets. A good market UI improves liquidity.
- **Regulation.** Items or currency that can be cashed out for real money raise legal and tax issues. Take advice before building such features. See `legal-ethics`.

### 0.4 Community and moderation
- **Report and review pipeline.** In-game report with context (chat log, recent actions), a queue, a human review tier and an appeal. Track median time to action. Aim for hours, not days, for severe reports (estimate).
- **Chat and voice.** Filters for slurs and personal data, mute and block, text-only or limited chat options for younger players. Voice needs recording or moderation policy, consent and local-law review.
- **Age and child safety.** Under-13 audiences trigger COPPA-like rules and similar laws elsewhere. Check requirements for your markets (UK and EU online-safety and digital-services regimes apply to many live games, verify the current details with counsel).
- **Community team.** Community managers, moderators and volunteer moderators need tools, guidelines and support. Burnout is real.
- **Player-created content** needs scanning, a takedown process and a repeat-offender policy (see §4).
- **Communication.** A status page, patch notes written for players, a known-issues list and honest post-mortems after outages. Trust is the asset.
- **Esports and creators.** Provide creator tools and codes only after you have a moderation baseline.
- Community tooling is in the `arcosian-community` adapter plugin where installed. Any post to a community channel is human-approved.

### 0.5 Anti-cheat
- **Server authority first.** The server owns position limits, damage, cooldowns, loot rolls and economy. Anti-cheat software is a second layer. If the client can grant itself loot, no software will help.
- **Detection layers.** Server-side anomaly detection (impossible speed, damage, aim statistics), client integrity checks, third-party anti-cheat services, and player reports. Combine signals before banning.
- **Third-party services.** Commercial anti-cheat products exist. Kernel-level drivers raise privacy and stability concerns and may not work on Linux, Steam Deck or some consoles. Check each vendor's platform support and licence terms before choosing.
- **Ban policy.** Wave bans (batch, to hide detection methods), graduated penalties, hardware or account-level bans for serious cheats, and a clear appeal path. Publish the rules.
- **Economy cheats.** Bots and dupers hurt PvE games as much as aimbots hurt PvP. Add behavioural checks (route repetition, inhuman uptime).
- **Privacy.** Anti-cheat collects data. Disclose it in the privacy policy and keep to the minimum needed. See `legal-ethics`.
- **Console.** The platform holds a closed environment, which reduces some classes of cheats. Cross-play with PC brings them back, so plan for it.
- More in `competitive-pvp.md` §0 (integrity) and `multiplayer-backend`.

### 0.6 End-of-service planning
Every live game ends. Plan it at launch.

- **Set a sunset trigger.** Define the revenue, concurrency and cost thresholds below which the game is reviewed (for example, three consecutive months with revenue under 1.3× operating cost). Review quarterly.
- **Cost of keeping it alive.** Servers, platform fees, a minimum live team, customer support and legal compliance. Estimate the monthly floor now.
- **Sunset steps.** Announce with at least 90 days notice (estimate, and longer for games with paid content), stop new sales first, offer refunds or compensation where law or goodwill requires, disable real-money purchases, keep the game playable as long as possible, and provide a data export.
- **Offline or private-server path.** Design the client so that a community or official offline mode is possible: do not hard-wire all logic to proprietary services. Publish a server build or a single-player fallback if you can.
- **Short-lived failures.** A heavily marketed live-service shooter was withdrawn within weeks of its 2024 launch and refunded (Concord, Firewalk Studios and Sony). A long-running online racing game's servers were shut down in 2024 (The Crew, Ubisoft), which fuelled consumer campaigns for playable-after-shutdown rules. Check the current status of those campaigns and any consumer-protection rules in your markets.
- **Platform obligations.** Console and store rules cover delisting and refunds. See `console-pathway` and `pc-web-release`.
- **Postmortem.** Run a blameless review (`postmortem`) and archive design docs and data.

## 1. MMORPG (theme-park and sandbox)

### Definition and player fantasy
A shared persistent world with character classes, quests, dungeons, raids and a social layer of guilds and trade. Theme-park MMORPGs lead players along authored content (zones, story, instances). Sandbox MMORPGs hand players tools (crafting, land, player-driven economy, open PvP) and let the community write the story. The fantasy is *a life in another world*: a character that grows, friends who matter and a place that remembers you. Mobile MMORPGs with gacha mechanics are in `rpg-gacha.md`.

### Core loop
```
log in → pick activities (quests, dungeons, crafting, trade, PvP)
  → earn XP, gear and currency → progress character power and social standing
  → group content (dungeon, raid, guild event) → loot and reputation → next expansion tier
```

### Meta loops
- **Level and gear treadmill.** Leveling, then gear tiers, then expansions that reset the ceiling.
- **Guilds and raiding.** Scheduled group content with progression races.
- **Crafting and economy.** Professions, markets, rare materials.
- **Reputation, housing and cosmetics.** Long-term collection goals.
- **PvP ladders and wars** (sandbox and many theme-parks).

### Session profile
Estimate: 2–4 hours per session, 3–5 sessions a week for committed players. Raid nights are scheduled. Casual players log in for short sessions. A very high tail of hours: thousands per player over years.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Classes, roles (tank, healer, damage) | combat | Role clarity helps group finding |
| Quests and zone progression | progression & upgrade; exploration & traversal | Authored arcs. Guide the first 10 hours carefully |
| Dungeons and raids | combat; social & competition | Instanced. Lockouts and loot rules |
| Crafting and gathering professions | build-craft; economy & resources | Tie to the trading economy (§0.3) |
| Auction house or player market | economy & resources | Fees as sinks. Anti-fraud measures |
| Guilds, chat, friends | social & competition | Tools for officers, calendars, banks |
| Housing and cosmetics | build-craft; collection & randomness | Long-term sinks and expression |
| Open-world PvP or wars (sandbox) | social & competition; combat | §0.5 integrity. Rules of engagement |

### Monetisation model and typical mix
Three families: subscription (monthly fee, often plus expansions), buy-to-play (box plus expansions plus cash shop), and free-to-play with a shop. Qualitative mix:
- Expansions as the major revenue event (every 1–3 years).
- Subscriptions, token or membership with convenience perks.
- Cosmetics, mounts, housing items, character services.
- A game-time token or player-tradable currency in some models.

**Ethics flags:** avoid selling raw power in PvP, loot boxes need compliance (see `rpg-gacha.md` §0.3), and convenience boosts can harm leveling design.

### KPI expectations
Qualitative. Watch concurrent peak versus launch, subscriber or paying-user counts, returning-player rate after expansions, guild retention and server population balance. Retention after the first week decides the first year. Churn spikes after content droughts.

### Retention drivers
Friends and guilds, long-term character investment, raid progression, economy and crafting identity, housing, regular content and expansions, and a world with its own culture.

### Content pipeline and production scope (estimates)
The largest scope in games. Zones, quests, dungeons, art, audio, animation, systems and a live team. Rough estimate: 100–500 people and 4–7 years for a flagship launch. Not an indie-scale genre at full size. Small teams ship niche MMO-likes (single-zone, instanced, or text and 2D) with a sharply limited scope.

### Reference titles
- *World of Warcraft* (Blizzard, 2004): the theme-park benchmark.
- *Final Fantasy XIV* (Square Enix, 2010, relaunched 2013): story-led theme-park with steady expansions.
- *Guild Wars 2* (ArenaNet, 2012): buy-to-play with dynamic events.
- *Old School RuneScape* (Jagex): a sandbox-flavoured long-running game with player polls.
- *EVE Online* (CCP Games, 2003): a sandbox with a single shared universe and a player-driven economy.
- *Albion Online* (Sandbox Interactive, 2017): sandbox economy with full-loot PvP.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| The first 10 hours are polished and social | Launch servers crash and queues last hours |
| A living calendar and expansions arrive on time | Content droughts of many months |
| The economy is healthy and transparent | Gold sellers and dupes dominate |
| Group finding is easy and kind | Social friction: toxic chat, hard to find groups |
| The world has identity | A generic fantasy clone with no hook |

### Innovation vectors
- Lower-commitment MMOs: shorter sessions, smaller worlds, more instanced play.
- Stronger story in live services.
- Cross-play and cross-progression.
- Player-run governance and community voting.
- AI-assisted NPC dialogue with strict moderation and seed control.

### Agent-buildability: 1/5
**Why low:**
- The money is in a persistent world, a live team, community management and server operations, none of which are verifiable by client gates.
- Authored content volume is huge.

**What agents do well:**
- Economy sims (faucets and sinks), loot tables, quest data validation.
- Simulated-client load tests.
- Tooling: dashboards, content pipelines, localisation checks.
- A single-zone vertical slice for a pitch.

### Starter feature list (P0 vertical slice: one zone, 3 classes, one dungeon, local server)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Authoritative server with a 50-player zone (net) | Bot clients cannot move or damage beyond limits. Tick time under 33 ms at 50 players |
| 2 | Account, character create and persistence (tech) | Character state survives restart. Atomic writes. Idempotent save |
| 3 | 3 classes × 6 abilities with roles (combat) | Ability data tables validated. DPS-per-role targets met in sim |
| 4 | 15 quests with a tracker (content) | Quest graph has no dead ends. A bot completes all |
| 5 | One 5-player instanced dungeon with a boss (content) | Instance spins up and down. Lockout enforced. Boss beatable by scripted bots at target gear |
| 6 | Loot table with bind rules (economy) | Drop rates from the table within statistical tolerance over 100,000 rolls |
| 7 | Market with fee sink (economy) | Ledger balances. Idempotent buy and sell. Duplicate attempts rejected |
| 8 | Group finder and party chat (social) | Queue time and role balance tested with bots |
| 9 | Report button and chat filter (ops) | Report stores context. Filter blocks the test word list |
| 10 | Load test harness (qa) | 500 bots for 30 minutes: no desync, no crash, p99 latency under target |
| 11 | Metrics dashboard: CCU, faucets, sinks (ops) | Values match logs within 1% |

### Platform notes
| Aspect | PC | Console | Web | Mobile |
|---|---|---|---|---|
| Input | Mouse and keyboard, many hotkeys, add-ons, macros | Gamepad: hotbar sets, radial menus, text chat is awkward | Click-to-move, light action | Touch auto-battle (see `rpg-gacha.md` mobile MMORPG) |
| Session | Long sessions, raid nights | Couch sessions, party chat via platform | Short | Short, auto-play |
| Performance | Wide spec range, crowds in cities are the hard case | Fixed targets, crowd caps, memory limits | Low-poly or 2D | Thermal limits, battery |
| Business | Subscription, box and expansions, cash shop | Platform online rules, certification for each patch (see `console-pathway`) | Ad-supported or subscription | F2P with IAP |

- Console patches go through platform certification. Plan patch cadence and emergency fixes around it.
- Cross-play needs account linking and matching rules.

## 2. Survival MMO

### Definition and player fantasy
A persistent, large-scale survival world with hundreds of players per shard. Players gather, craft, build bases, trade, form clans and fight for territory. Rules vary: full-loot PvP, safe zones, seasonal wipes. The fantasy is *a society built from scratch*: alliances, betrayals, trade routes and territory wars. Single-player and small-group survival foundations are in `survival-sandbox.md`.

### Core loop
```
gather and craft → build and defend a base → trade and ally with clans
  → contest territory and resources → raid or defend → wipe or season ends → start again, wiser
```

### Meta loops
- **Clans and territory control.** Persistent ownership with taxes and wars.
- **Economy and trade.** Player markets, trade posts, rare resources.
- **Seasonal wipes.** A fresh server every 4–12 weeks, with carry-over cosmetics.
- **Tech and crafting ladders.**
- **Events.** Airdrops, bosses, wipe-day launches.

### Session profile
Estimate: 1–4 hours. Players schedule around raids and wars and may check in briefly to maintain bases (upkeep timers). Heavy sessions on wipe day. Offline vulnerability drives anxiety, so offline protection and upkeep rules matter (`survival-sandbox.md` §0.5).

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Needs and survival pressure | time & energy | Light at scale, so that servers feel social |
| Base building with ownership and upkeep | build-craft; economy & resources | Upkeep prevents abandoned-base sprawl |
| Territory and clan wars | social & competition | Rules of engagement, time windows |
| Full-loot or partial-loot death | economy & resources | Risk drives trade. Insurance mechanics |
| Player markets and trade routes | economy & resources | §0.3. Anti-fraud |
| Resource respawn at server scale | economy & resources | `survival-sandbox.md` §0.3 scaled by pop |
| Anti-grief and anti-cheat | social & competition | §0.5. Central to survival of the game |
| Wipe cadence | live events | Publish the schedule |

### Monetisation model and typical mix
Buy-to-play with cosmetics, or subscription, plus optional paid servers. Free-to-play versions rely on cosmetics and convenience. Typical mix (qualitative): box price, cosmetic shop, battle pass, server rental. **Ethics flags:** pay-to-win items and loot boxes in full-loot PvP damage trust and draw regulatory attention.

### KPI expectations
Qualitative. Server population at wipe, retention after wipe week, percentage of players who build a base, clan counts, report-to-ban latency, and cheat rate. Population balance across servers matters, because empty servers feel dead and full ones queue.

### Retention drivers
Social bonds and rivalry, territory ownership, trading, the wipe-day ritual, streaming culture, and evolving rules.

### Content pipeline and production scope (estimates)
Engineering-heavy: large-world networking, persistence, economy, anti-cheat and admin tools. Content is smaller than a theme-park MMORPG but art and systems scale with the world. Rough estimate: 30–150 people and 3–5 years for a flagship, and small studios have shipped narrower versions (single large map, fewer players per shard) in 2–3 years.

### Reference titles
- *Rust* (Facepunch, 2018): wipe-based PvP survival on community and official servers.
- *ARK: Survival Evolved* (Studio Wildcard, 2017): tribes and taming on servers.
- *Conan Exiles* (Funcom, 2018): survival with persistent clan building.
- *Albion Online* (Sandbox Interactive, 2017): sandbox MMORPG with territory.
- *DayZ* (Bohemia Interactive, 2018 full release): large-scale survival with mod origins.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Servers stay populated and balanced | Population collapses a month after launch |
| Offline protection and upkeep are fair | Players lose bases while asleep |
| Cheating is rare and visible bans occur | Cheaters ruin the ladder and drive trust down |
| The wipe cadence refreshes competition | Veteran clans lock out newcomers for months |
| Server tools are good for admins | Operations are a manual burden |

### Innovation vectors
- Smaller shards (50–150 players) with strong social density.
- Safe-zone economies with optional PvP frontiers.
- Seasonal rule sets (rotating modifiers).
- Cross-play with anti-cheat parity.
- Player-run servers with official ranking.

### Agent-buildability: 1/5
**Why low:**
- Population dynamics, cheating and moderation need real players.
- Server operations are continuous.

**What agents do well:** economy and respawn sims, load tests with bot clients, raid-cost ratio sims, admin tooling, wipe schedulers.

### Starter feature list (P0 vertical slice: 100 bots on one server)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Authoritative survival server for 100 players (net) | Tick under 33 ms at 100 bot clients. No client-authoritative actions |
| 2 | Persistent bases with ownership and upkeep (build) | Upkeep decay per tuning. Abandoned bases decay on schedule |
| 3 | Clan system with permissions (social) | Permission tests: roles and invites. Audit log |
| 4 | Respawn tuned for 100 players (economy) | Supply over demand ratio above 1.5 in sim (`survival-sandbox.md` §0.3) |
| 5 | Raid rules and offline protection (combat) | Raid cost ratio within 0.3–1.0 in sim. Protection timers enforced |
| 6 | Player market with a fee sink (economy) | Ledger balanced. Dupe attempts rejected |
| 7 | Wipe scheduler (ops) | Wipe resets world and keeps cosmetics. Dry run restores a backup |
| 8 | Cheat detection signals (anti-cheat) | Speed, damage and aim anomalies flagged on injected cheat bots |
| 9 | Report tool and admin console (ops) | Reports with evidence. Admin can mute, kick, ban and roll back |
| 10 | Soak test: 100 bots for 6 hours (qa) | No memory growth over target. No save corruption |

### Platform notes
| Aspect | PC | Console | Web | Mobile |
|---|---|---|---|---|
| Input | Mouse and keyboard, aim precision | Gamepad with aim assist and build snaps | Not typical | Simplified, auto-aim |
| Session | Long, scheduled raids | Couch, party-based | Short | Short, defence-focused |
| Performance | Servers hold large worlds, clients stream | Memory caps limit base density | Small worlds | Small worlds, battery |
| Business | Premium plus cosmetics, community servers | Platform rules for user-run servers vary | Ad-supported | F2P (different design) |

- Community-hosted servers are popular on PC and limited on console. Check platform rules (`console-pathway`).

## 3. Live-service looter shooter / ARPG

### Definition and player fantasy
A shooter or action RPG where the core fantasy is the chase for better gear, with activities that repeat on a weekly and seasonal rhythm. Players run missions, dungeons or maps, collect loot, build a character, and grind harder tiers. The fantasy is *the build coming together*: the drop that changes everything, the build that melts a boss.

### Core loop
```
choose activity (mission, dungeon, map, raid) → fight → loot drops
  → compare and equip gear → tune build → attempt a harder tier → seasonal reset or expansion
```

### Meta loops
- **Gear and build crafting.** Affixes, sets, crafting and rerolling.
- **Endgame ladders.** Difficulty tiers, timed runs, leaderboards.
- **Weekly resets and seasons.** New rules, league mechanics or story chapters.
- **Raids and group content.**
- **Trading or solo-self-found.** Either a trade economy (§0.3) or a self-found loop that avoids it.

### Session profile
Estimate: 20–60 minute activities, 1–3 hours per session. Weekly reset rituals. Seasons reset the economy or ladders, which refreshes the player base every 3–4 months.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Loot with rarity, affixes and sets | collection & randomness | Drop-rate maths, pity or smart loot |
| Build crafting and skill trees | progression & upgrade | Build diversity is the endgame |
| Difficulty tiers and scaling | progression & upgrade | Keep the power curve readable |
| Mission and map variety | exploration & traversal | Procedural maps with rotating modifiers (`procedural-generation`) |
| Boss and raid mechanics | combat | Telegraphs, mechanics checks |
| Seasonal leagues and ladders | live events; social & competition | New rules each season |
| Trading or self-found rules | economy & resources | §0.3 |
| Loadouts and stash | UX automation | Quality-of-life drives retention |

**Loot maths.** For a drop with chance `p` per kill, expected kills are `1/p` and the probability of at least one drop in `n` kills is `1 − (1 − p)^n`. Worked example: `p = 0.5%` → expected 200 kills; P(≥1 in 200) = 1 − 0.995^200 ≈ 63%, so 37% of players are still empty-handed at the average. Use a pity counter or bad-luck protection to cap the tail (see `rpg-gacha.md` §0.1 for pity maths).

### Monetisation model and typical mix
Premium launch (box) with paid expansions and a season pass, or free-to-play with cosmetics. Typical mix (qualitative): box price, expansions, battle pass, cosmetics, stash or convenience items. **Ethics flags:** selling power in a game with a trading economy, paid loot boxes, and pay-to-skip in progression need compliance review (`rpg-gacha.md` §0.3 and `legal-ethics`).

### KPI expectations
Qualitative. Launch spikes are steep, and retention is tied to season starts, so plan returning-player campaigns. Watch season-start concurrency, day-14 retention within a season, build diversity, loot satisfaction surveys and trading volume. Launch quality (bugs, server stability) heavily shapes long-term reviews.

### Retention drivers
Loot chase, build theorycrafting, season resets, difficulty ladders, group content, creator and community culture, and a fair economy.

### Content pipeline and production scope (estimates)
Systems-heavy: loot, affixes, skills and balance, plus mission, map and boss content and a live-service back end. Rough estimate: 50–300 people and 3–5 years for a flagship. Smaller teams ship ARPGs with strong core combat and procedural content. Balance and data pipelines are major workstreams (`balance`).

### Reference titles
- *Diablo II* (Blizzard, 2000) and *Diablo IV* (Blizzard, 2023): the ARPG benchmark and its seasonal modern form.
- *Path of Exile* (Grinding Gear Games, 2013): leagues, deep build crafting and a trade economy.
- *Destiny 2* (Bungie, 2017): looter shooter with seasons and raids.
- *Warframe* (Digital Extremes, 2013): free-to-play looter shooter with an in-game trade economy.
- *The Division 2* (Massive Entertainment, 2019): cover-based looter shooter.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Core combat is deeply satisfying | The loot is exciting but the combat is not |
| Seasons bring real rule changes | Seasons are numbers-up resets |
| Build diversity survives balance patches | One build dominates, the rest fade |
| The economy is protected from dupes and bots | Inflation and duplication wreck trust |
| Launch is stable | Server failures at launch define the reviews |

### Innovation vectors
- Looter shooters with lower time commitment and solo-friendly loops.
- Self-found modes alongside trading modes.
- Cross-play and cross-progression.
- Procedural story or mission generation.
- Seasonal rule-mutation systems.

### Agent-buildability: 2/5
**Why 2:**
- Loot, affix and balance systems are data and can be simulated.
- A single-player loot loop can be tested with bots.

**Why not higher:**
- Combat feel, art, audio and the live team are human.
- Meta health depends on live telemetry and player behaviour.

**What agents do well:** loot-table sims, build-power calculators, balance reports, procedural-map validators, content pipelines.

### Starter feature list (P0 vertical slice: single-player loot loop)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Core combat with 4 skills (combat) | Hit detection and cooldowns match the data table. Feel pass signed by a human |
| 2 | Loot drops with 4 rarities and 20 affixes (economy) | 1 M simulated drops match the table within 1%. No impossible affix combinations |
| 3 | Pity or bad-luck protection (economy) | Cap the tail: 99th percentile drop count within the target |
| 4 | Stash, compare and equip UI (ux) | Comparison shows deltas. Full controller and keyboard support |
| 5 | Skill tree with build presets (progression) | Respec cost per table. Build calculator matches in-game numbers |
| 6 | 5 procedural maps with modifiers (content) | Validator: reachable exit, spawn fairness. 1,000 seeds pass |
| 7 | Difficulty tiers 1–10 (progression) | Enemy scaling from the curve. Bot clear times within band |
| 8 | One boss with phases (combat) | Telegraphs. Scripted bot clears at target gear and fails below the threshold |
| 9 | Seasonal ladder with a rule modifier (live) | Season data-driven. Ladder reset keeps account items |
| 10 | Save and migration (tech) | Archived saves load. Version check on startup |
| 11 | Telemetry events for drops and deaths (ops) | Events logged with schema. Dashboard matches counts |

### Platform notes
| Aspect | PC | Console | Web | Mobile |
|---|---|---|---|---|
| Input | Mouse and keyboard for ARPG clicks, many hotkeys | Gamepad: skills on face and bumpers, aim assist, inventory UI needs a rebuild | Click-to-play, light ARPG | Touch ARPG with auto-aim (see `rpg-gacha.md`) |
| Session | 20–60 min activities | Couch sessions | Short | Short |
| Performance | Particle-heavy combat, wide spec range | Fixed 60 fps target, crossplay | Light visuals | Thermal limits |
| Business | Premium plus expansion, battle pass, cosmetics | Platform store, certification each season | Free with ads | F2P gacha ARPG |

- Inventory and stash UI is the main console redesign task. Plan it from the start.
- Season launches need console certification slots. Book them early.

## 4. Creator platforms (Roblox experiences, Fortnite UEFN islands)

### Definition and player fantasy
The platform provides the engine, servers, social layer, payment and discovery. Developers build experiences or islands inside the platform's rules and earn a share of revenue or engagement payouts. Players hop between experiences with a persistent avatar and friends list. The fantasy for players is *a universe of games with my friends*. For developers it is *low-cost access to an enormous audience*.

### Core loop
```
(developer) build an experience → publish → platform surfaces it to players → players try it and friends join
  → engagement and purchases → payouts → iterate with analytics → (player) find, play and share
```

### Meta loops
- **Discovery.** Ranking by engagement, retention and recommendation. Thumbnails, titles and update recency matter.
- **Update cadence.** Frequent updates, seasonal events and collaborations.
- **Creator economy.** Marketplace, asset sales, group ownership, studio teams.
- **Social graph.** Friends, parties, voice and avatars.
- **Platform-run events and ecosystems.**

### Session profile
Estimate: 10–40 minute rounds in an experience, with sessions that hop between several. Strong social and young-skewing audience on some platforms. Developers see spikes when featured and steep drops when a trend ends.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Short round or session loops | progression & upgrade | Be fun in the first 60 seconds. The platform measures it |
| Avatar, cosmetics and emotes | collection & randomness | Platform-wide currency or per-experience items |
| In-experience purchases and passes | economy & resources | Platform rules on what you can sell |
| Social play (parties, friends) | social & competition | Join-friend flow drives virality |
| Update and event cadence | live events | Weekly or biweekly updates |
| Analytics dashboards | UX automation | Use platform analytics. Read retention and session length |
| Moderation and safety tools | social & competition | Platform rules are strict. Follow them |
| Cross-experience progression | progression & upgrade | Usually limited, so design around it |

### Monetisation model and typical mix
Developers earn from platform engagement payouts (Fortnite creator programmes), from in-experience purchases and passes (both platforms), and sometimes from premium access or sponsorships. The platform takes a share and sets the rules. Exact rates and rules change often, so check the current documentation (see volatile facts). Typical mix (qualitative):
- Engagement payouts tied to time spent, retention and new players.
- In-experience items: passes, boosts, cosmetics.
- Sponsored or branded experiences.

**Ethics flags:** young audiences make loot boxes, time-limited pressure and manipulative offers high-risk. Follow the platform's rules on paid random items and on child safety, and see `legal-ethics`.

### KPI expectations
Qualitative. Look at day-1 and day-7 retention, average session length, concurrent players, play sessions per user, conversion to purchase and, on engagement-pay platforms, payout per thousand hours. Frontloaded featuring leads to spikes. Concurrency is a cost the platform carries, so the developer risk is reach, not hosting.

### Retention drivers
A clear 60-second hook, friend invites, frequent updates, events, cosmetics, a shared meta (clans, trading where allowed), and a place in platform trends.

### Content pipeline and production scope (estimates)
Small teams and solo developers succeed. Typical scope: 1–15 people, 1–6 months for a first experience, then continuous updates. Tooling is the platform's: Roblox Studio and Luau scripting, Unreal Editor for Fortnite with Verse and Blueprint-like tools. Use the platform's templates and asset libraries. The main risk is platform dependency and rule changes.

### Reference titles
- *Roblox* (Roblox Corporation): a platform of many popular experiences across genres.
- *Fortnite Creative and UEFN* (Epic Games): creator islands inside Fortnite.
- *Rec Room* (Rec Room Inc.): a social creation platform.
- *Garry's Mod* (Facepunch): a sandbox with a mod-driven game-mode culture, as a historical reference.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| The first minute is clear and fun | Players leave during loading or tutorial |
| Updates are frequent and tied to trends | The experience goes stale |
| Friend-invite flow is smooth | Solo-only design on a social platform |
| The developer reads analytics and iterates | Guesswork and no testing |
| Compliance with platform policy | A policy strike or removal destroys the business |

### Innovation vectors
- Genre mashups inside the platform (survival, tycoon, battle, social).
- Cross-platform presence: a platform experience that feeds a standalone game.
- AI-assisted creation tools (check platform rules on generated content).
- Brand and IP collaborations.
- Education and non-gaming experiences.

### Agent-buildability: 3/5
**Why 3:**
- Scripts, data tables and round logic are testable offline where the tools allow.
- The platform carries servers, matchmaking and payments.

**Why not higher:**
- Platform-specific toolchains, review processes and discovery are outside agent control.
- Playtesting inside the platform editor often needs a human session.

**What agents do well:** game logic scripts, economy tables, UI scripting, test harnesses for pure logic, update-plan and analytics reports.

### Starter feature list (P0 vertical slice: one round-based experience)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | 3-minute round loop with lobby (core) | Round state machine unit-tested. Players join and leave mid-round without errors |
| 2 | Core mechanic with 60-second hook (gameplay) | Playtest: a new player scores or progresses within 60 seconds |
| 3 | Player data save and load (tech) | Data persists across sessions. Failure falls back safely |
| 4 | Progression with 10 levels and rewards (progression) | Curve from the tuning table. Bot reaches level 10 in the target time |
| 5 | In-experience pass or cosmetic item (monetisation) | Purchase flow follows the platform rules. Receipt handled idempotently |
| 6 | Friend join and party flow (social) | Joining a friend places the player in the same server |
| 7 | Server-side validation of actions (security) | Client cannot grant itself currency or items in an exploit test |
| 8 | Analytics events for funnel and retention (ops) | Events cover join, first action, round end, purchase |
| 9 | Report and moderation hooks (safety) | Uses the platform's tools. Chat follows platform filters |
| 10 | Mobile, PC and console input support (ux) | Works with touch, mouse and keyboard, and gamepad as the platform allows |
| 11 | Weekly update plan (liveops) | Roadmap with content for four weeks in the update file |

### Platform notes
| Aspect | PC | Console | Web | Mobile |
|---|---|---|---|---|
| Input | Mouse and keyboard, full UI | Gamepad: platform UI conventions apply | Browser clients on some platforms | Touch is the main input on many platforms: test first on a phone |
| Session | Short rounds, hop between experiences | Couch sessions | Short | Short, on the go |
| Performance | Wide range: test on low-end devices | Fixed targets set by the platform | Streaming and download limits | Low-end phones dominate: budget memory and draw calls |
| Business | Payouts and purchases through the platform | Platform terms and fees | Platform-dependent | Mobile store fees can affect currency prices (platform-set) |

- Design for the weakest device the platform supports. A large part of the audience is on phones or low-end hardware.
- Rules about payments, chat, ratings, user-generated content and AI use change often. Re-read the platform's policies each quarter.

## 5. Seasonal live games

### Definition and player fantasy
A game built around a repeating season: a new theme, a new reward track and a reset of ladders or content, usually every 8–13 weeks. Genres vary (battle royale, hero shooter, racing, co-op shooter, survival), but the live-service wrapper is the same. The fantasy is *a game that is always fresh*: a reason to come back every few weeks and a shared moment with the community on each launch day.

### Core loop
```
season starts (new theme, rules, pass) → play core mode(s) → progress the pass and challenges
  → events and limited-time modes → ladder or story climax → season ends → next season
```

### Meta loops
- **Season pass.** Free and premium tracks, tiers and challenges.
- **Ladders and ranks.** Seasonal resets with rewards.
- **Events.** Limited-time modes, collaborations, community goals.
- **Cosmetics and collections.** Shop rotations and unlocks.
- **Story beats and world events** that unfold over the season.

### Session profile
Estimate: 20–90 minutes, with several sessions a week. Peaks on season launch week and event days. Returning players arrive at season start, so the first hour of each season must welcome them.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Season pass with tiers | progression & upgrade; time & energy | Use fair tier pacing. See `liveops` and `monetization` |
| Weekly and daily challenges | live events | Catch-up for latecomers |
| Seasonal ladder or rank reset | social & competition | Soft resets avoid shock |
| Limited-time modes | live events | Rotating variety reduces fatigue |
| Shop rotation and cosmetics | collection & randomness; economy & resources | Show prices clearly. Avoid false urgency |
| Balance and meta shifts | combat | Patch cadence tied to the season |
| Story or world events | exploration & traversal | A narrative reason to log in |
| Return-player flow | UX automation | Recap, catch-up rewards, loadout reset |

**Pass pacing check.** For a premium pass with `T` tiers and `H` hours needed per tier, total hours = `T · H`. Worked example: 100 tiers at 0.6 hours per tier = 60 hours. If the target player plays 6 h/week over 10 weeks (60 h), the pass fits only a fully committed player. Aim for 70–80% of the target player reaching the end (estimate) by pairing weekly challenges with a catch-up XP bonus. Never sell tier skips as the only path to completion.

### Monetisation model and typical mix
Premium or free-to-play core with a season pass and cosmetics. Typical mix (qualitative): pass (free and paid tracks), cosmetic shop bundles, collaborations, and in some games expansions. **Ethics flags:** FOMO expiry on paid content, manipulative countdowns and pressure on children. See `legal-ethics` and `liveops` for fair-pass patterns.

### KPI expectations
Qualitative. Watch season-start spikes (returning players), pass attach rate, tier completion, day-14 retention inside a season, event participation, and shop conversion. Compare seasons: a season that retains fewer players than the last is an early warning.

### Retention drivers
Fresh content on a predictable date, social moments (launch day, events), rewards worth earning, fair catch-up, a strong core loop, and creator and esports ecosystems for competitive titles.

### Content pipeline and production scope (estimates)
Requires a season factory: a repeatable pipeline of themes, maps, skins, challenges, balance changes and marketing assets on a fixed calendar. Rough estimate: a standing live team of 30–150 for a major title, smaller for niche games. Content lead time is 3–6 months, so plan the next two seasons while shipping the current one. Tools for fast iteration and automated testing are vital (`qa-testing`, `build-feature`).

### Reference titles
- *Fortnite* (Epic Games, 2017): season structure with map changes and live events.
- *Apex Legends* (Respawn, 2019): seasonal battle royale with legends and ladder resets.
- *Overwatch 2* (Blizzard, 2022): seasonal hero shooter.
- *Rainbow Six Siege* (Ubisoft, 2015): long-running seasonal operator releases.
- *Helldivers 2* (Arrowhead Game Studios, 2024): co-op shooter with an ongoing narrative and warbonds.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Seasons ship on time with something new | Delays and thin seasons |
| The pass is fair and completable | The pass feels like a second job |
| Balance changes respect the player base | Frequent unpopular nerfs |
| Returning players are welcomed | Catch-up is impossible |
| Communication is honest | Silence during problems |

### Innovation vectors
- Narrative-driven seasons with real consequences from community actions.
- Player-selectable season rules.
- Cross-play seasons with shared progression.
- Shorter, lighter seasons for smaller teams.
- Season content co-created with creators.

### Agent-buildability: 3/5
**Why 3:**
- A season is a structured, data-driven package: challenges, rewards, schedules.
- Pass pacing, shop rotation and balance can be simulated.

**Why not higher:**
- Core game quality and creative direction are human.
- Live operations depend on real players and a team.

**What agents do well:** season calendars, pass pacing sims, challenge generators, patch-note drafts (human reviewed), regression tests for season switchovers, telemetry reports.

### Starter feature list (P0 vertical slice: one core mode plus a 10-week season)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Season data schema and loader (live) | A season is one data file: theme, dates, tracks, challenges. Loading a new season needs no client update where the platform allows |
| 2 | Pass with 60 tiers (progression) | Pacing sim: 75% of target players finish. Tier XP table validated |
| 3 | 12 weekly challenges with catch-up (live) | Challenge set rotates on the schedule. Missed weeks can be completed later |
| 4 | Ladder with soft reset (social) | Reset formula keeps rank order. Rewards by final rank |
| 5 | Shop rotation with clear prices (economy) | Rotation schedule from data. Prices shown in all currencies with no hidden conversion |
| 6 | Limited-time mode (content) | Mode toggles by date. Results do not affect the main ladder |
| 7 | Return-player flow (ux) | Players absent over 30 days see a recap and receive catch-up XP |
| 8 | Season switchover test (qa) | Simulate the end and start times with clock mocking: pass, ladder and shop update cleanly |
| 9 | Balance patch pipeline (ops) | Patch data separate from code. A rollback restores the previous values |
| 10 | Telemetry for season KPIs (ops) | Dashboard shows season-start concurrency, pass attach and tier completion |
| 11 | Roadmap and patch-notes template (liveops) | Roadmap published 4 weeks ahead in the template |

### Platform notes
| Aspect | PC | Console | Web | Mobile |
|---|---|---|---|---|
| Input | Mouse and keyboard or gamepad | Gamepad with aim assist and a clear UI | Browser, light | Touch (see `liveops` for mobile season patterns) |
| Session | Evening play, events | Couch and party play | Short | Short, daily |
| Performance | Wide specs, download size matters for each season | Patch size and certification slots are limits | Small download | Large updates cost players data and storage |
| Business | Store fees, pass, cosmetics | Platform storefront and sometimes platform currency | Ads | IAP and pass |

- Season launches should not need a full client download where possible. Keep content data-driven.
- Console season launches need certification lead time. Schedule it in the production plan.

## Volatile facts (as of Oct 2026 — verify before relying)

- Steam reached about 43.5 million concurrent logged-in users on 11 Oct 2026 (SteamDB figure reported by press), about 14.5 million of them in a game. Valve's own page showed slightly different numbers. Concurrent users include people with the client open — [Notebookcheck](https://www.notebookcheck.net/Steam-sets-a-new-all-time-concurrent-player-record-after-surpassing-42-million-users-online.1201788.0.html), [Dot Esports](https://dotesports.com/general/news/steam-all-time-record-43-5-million-concurrent-users)
- Epic reported (June 2026, press coverage of Unreal Fest remarks) that UEFN creators have been paid over $1 billion since 2023, that creator-made islands account for about 47% of Fortnite playtime (up from 38% a year earlier), that in-island transactions were added in January 2026 and that over 3,000 islands earn more from them than from engagement payouts — [PocketGamer.biz](https://www.pocketgamer.biz/unreal-engine-for-fortnite-creator-payouts-surpass-1bn/), [Outlook Respawn](https://respawn.outlookindia.com/gaming/gaming-news/epics-uefn-payouts-reached-1-billion-since-launch)
- UEFN payout percentages (for example the 40% Item Shop and real-money share, a Sponsored Row share, a bonus for new or returning players and a $100 withdrawal threshold) come from third-party guides and are unverified. Check Epic's current creator-programme documentation — [UEFN Central (third party)](https://uefncentral.com/uk/blog/make-money-uefn-creator-payouts-2026), [Esports.gg (third party)](https://esports.gg/guides/fortnite/how-do-fortnite-creators-make-money/)
- Roblox DevEx: most third-party sources give about $0.0035 per Robux with a 30,000 Robux minimum, Premium and age requirements, and a 30% platform fee on item and pass sales. One site claims higher rates for some US earnings since June 2026, uncorroborated. All unverified. Check Roblox's official DevEx page before modelling revenue — [RoWatcher (third party)](https://rowatcher.com/news/roblox-devex-math-what-you-actually-take-home-in-2026)
- Concord (Firewalk Studios, Sony, 2024) was withdrawn within weeks of launch, and The Crew (Ubisoft) servers were shut down in 2024. The status of consumer-protection campaigns about playable-after-shutdown rules and any new law is not verified here. Check current rules in each market.
- I found no sourced MMO concurrency, subscription or server-cost benchmarks this session. All cost and CCU figures above are illustrative formulas and estimates, not statistics.
- Console and store policies on certification slots, user-run servers and delisting change. Check `console-pathway` and the platform holder's documentation.

## Related skills
- `mechanics-codex`: cards for every mechanic named above.
- `liveops`: calendars, events, seasons, pass pacing and content templates.
- `economy-design`: faucets and sinks, trading, inflation, market fees.
- `multiplayer-backend`: servers, sharding, matchmaking, persistence, load tests.
- `player-analytics`: telemetry, retention and economy dashboards.
- `monetization`: passes, cosmetics, ethical offers.
- `legal-ethics`: loot boxes, child safety, moderation duties, sunset obligations.
- `balance`: loot tables, build power, season balance passes.
- `procedural-generation`: procedural maps and missions with validators.
- `platform-targets`, `pc-web-release`, `console-pathway`: input, release and certification differences.
- `rpg-gacha.md`: mobile MMORPG, gacha live games and paid-random compliance, not repeated here.
- `survival-sandbox.md`, `simulation-management.md`: sibling playbooks for survival depth and management systems.
