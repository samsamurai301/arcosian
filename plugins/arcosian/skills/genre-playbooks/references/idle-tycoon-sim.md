# Idle, Tycoon and Simulation Playbooks

These genres reward players for coming back rather than for sitting in long sessions. Timers, production chains and offline progress turn absence into value. The appeal of the progression is either numbers going up (idle clicker, AFK RPG, tycoon) or a world that grows and expresses the player (farming, life sim, home design). Restaurant and time-management games are the action-flavoured member: short, frantic levels wrapped in an upgrade meta. As a family they are strongly economy-driven. Most of the design work is curves, sinks and pacing, which suits simulation (`economy_sim.py`, `progression_calc.py`). They differ sharply in content cost: an idle clicker is mostly math, while home design and life sim are mostly content. This file covers seven playbooks in the 14-part format from `SKILL.md`. Sourced figures are tagged `[Vn]` and listed at the end. Team and time figures are labelled estimates. The arcade-idle carry-and-unlock pattern is covered in `hyper-hybrid-casual.md` (playbooks 6 and 8).

## Contents

| # | Playbook | AB (1–5) | Lead monetization | Content cost |
|---|---|---|---|---|
| 0 | Shared idle math | — | — | — |
| 1 | Idle clicker (incremental) | 5 | Rewarded ads + IAP multipliers | Low |
| 2 | Idle / AFK RPG | 3 | IAP gacha + pass | High (heroes) |
| 3 | Tycoon | 4 | Rewarded + IAP | Medium |
| 4 | Farming | 3 | IAP premium currency | High |
| 5 | Life sim | 2 | IAP cosmetics and content | Very high |
| 6 | Home design | 2 | IAP items and currency | Very high (catalog) |
| 7 | Restaurant / time management | 4 | IAP upgrades + rewarded | Medium |
| 8 | Volatile facts used in this file | — | — | — |

## 0. Shared idle math

Use these formulas as the default model. Encode them in `economy-model.schema.json` and run them with `${CLAUDE_PLUGIN_ROOT}/scripts/economy_sim.py`.

```
cost(n)          = c0 * r^n                         # nth unit of a generator; r often 1.07–1.15 (heuristic)
cost(n..n+k-1)   = c0 * r^n * (r^k - 1) / (r - 1)   # bulk buy
max_affordable   = floor( log_r( 1 + M*(r-1) / (c0*r^n) ) )
production       = base * owned * Π(multipliers)    # milestone ×2 at 25/50/100… owned is a common pattern
offline_gain     = min(elapsed, cap) * rate * efficiency    # efficiency < 1 rewards active play
prestige_points  = floor( k * (lifetime_earnings / scale)^p )  # p ≈ 0.5 (sqrt) or log-based
prestige_bonus   = 1 + bonus_per_point * prestige_points
```

- **Pacing metric.** Track time-to-next-meaningful-purchase (TTNP). Keep it in seconds early, minutes in the middle game and hours late. When TTNP passes your threshold, the player should want to prestige. Plot TTNP over time for each archetype. Sawtooth TTNP curves feel good; monotonic walls cause churn.
- **Big numbers.** Doubles overflow at about 1e308. Use a mantissa-plus-exponent type well before then if your curves exceed it. Format with suffixes (K, M, B, T, then aa, ab …) and offer scientific notation as an option.
- **Time integrity.** Offline gains invite clock tampering. Clamp elapsed time with server or monotonic time where available, and cap offline gains.
- **Notifications.** "Your vault is full" style pushes should be opt-in, capped per day and tied to real value.

## 1. Idle clicker (incremental)

**Definition and player fantasy.** Tap to earn, then buy generators that earn automatically. Numbers grow exponentially. Prestige resets for permanent multipliers, and layers of new mechanics unfold over time. The fantasy is exponential growth and optimization: watching a lemonade stand become a galactic empire, and the satisfaction of a clever build order.

**Core loop** (seconds). Collect → buy or upgrade the best-value generator → production rises → wait or tap → repeat. **Prestige loop** (hours to days): reset → gain prestige currency → faster rerun → reach further.

**Meta loops.**
- Prestige layers (2–4 over a game's life), each unlocking new systems.
- Achievements and milestone multipliers.
- Managers or automation unlocks that remove the need to tap.
- Events with separate, short economies (a mini-game reset in a themed world).

**Session profile** (estimate). Check-ins of 1–5 minutes, many times a day, plus occasional longer optimization sessions. Offline progress carries the game.

**Signature mechanics** (`mechanics-codex`: generators-timers, economy-flow, progression-unlocks).
- Exponential cost against linear-times-multiplier production. The interplay creates "which buy is best?" decisions.
- Milestone multipliers that reward focusing on one generator.
- Prestige with a sub-linear formula, so each prestige takes less real time to recover from but gives diminishing absolute gains.
- Layered reveals: new currencies and systems unlock as the old ones plateau. These reveals are the content.

| Parameter | Starting value to tune (heuristic) | Effect |
|---|---|---|
| Cost growth r | 1.07–1.15 per generator tier | Purchase cadence |
| Milestone multipliers | ×2–×3 at owned thresholds | Focus vs spread strategies |
| First prestige timing | Within the first few days | Teaches the reset early |
| Offline cap | A few hours, extendable | Return cadence |
| Offline efficiency | Below active rate | Rewards check-ins |

**Monetization model and typical mix.**
- Rewarded ads: 2× income for N hours, instant cash, double offline earnings.
- IAP: permanent multipliers, premium managers, time warps, starter packs.
- Interstitials are rare in better-regarded titles (qualitative).

**KPI expectations.** No sourced idle-specific range. One 2026 summary groups idle with genres that often match or beat RPG-level D7/D30 [V1], qualitatively. Long tails are common.

**Retention drivers.**
- Offline gains waiting.
- The next unlock or layer reveal.
- Prestige "number go up faster".
- Achievements.
- Events.

**Content pipeline and production scope** (estimates).
- Most content is math and UI. Each generator tier needs an icon and an upgrade animation.
- Layers and events need system design more than art.
- Simulate 30, 90 and 180-day curves per archetype before launch.
- Slice: 1 person plus agents, 2–4 weeks. Soft launch: 2–6 people, 3–8 months.

**Reference titles.** Cookie Clicker (Orteil), AdVenture Capitalist (Hyper Hippo), Egg, Inc. (Auxbrain), Clicker Heroes (Playsaurus), Universal Paperclips (Frank Lantz), Melvor Idle (Games by Malcs).

**What makes it succeed / fail.**
- Succeeds: a charming theme, readable growth, satisfying milestone moments and layered reveals that surprise.
- Succeeds: a generous offline economy.
- Fails: a plateau with no new system, and opaque multipliers.
- Fails: ads gating basic progress, and number formatting that hides real progress.

**Innovation vectors.**
- Narrative incrementals (Universal Paperclips shows story through mechanics).
- Idle plus collection RPG.
- Social leagues and co-op contracts (Egg, Inc. co-ops).
- Real-time events with shared goals.

**Agent-buildability: 5/5.** It is almost pure math. A deterministic economy can be simulated end to end with `economy_sim.py`, and a bot that "buys the best ROI" verifies pacing. The art is small and timing does not matter. The human checkpoint is theme charm and the feel of milestone moments.

**Starter feature list (P0 vertical slice).**
1. Big-number type and formatting — values up to 1e100 with suffix formatting; unit-tested for rounding and comparison.
2. Tap income — tap yields an income amount with a floating number and haptic.
3. Five generators — data-driven c0, r and base; bulk buy (×1, ×10, ×max) uses the closed-form cost (unit-tested).
4. Production tick — the fixed-step income simulation is deterministic and independent of frame rate.
5. Milestone multipliers — ×2 at owned thresholds, with a visible next-milestone indicator.
6. Managers — automate each generator; purchase is persistent.
7. Offline earnings — guarded elapsed time, cap and efficiency; the return screen shows the amount with a rewarded 2× option.
8. Prestige — a reset with the documented formula; the confirmation explains what is kept and lost.
9. Economy sim — the best-ROI bot reaches the first prestige in the target time and shows TTNP within bands (`economy_sim.py`).
10. Rewarded 2× income — opt-in boost with a timer and daily cap.
11. Save integrity — autosave every N seconds and on pause; a corrupted save falls back to the last good backup.
12. Analytics — `purchase` (generator, count), `prestige` (points, time since last) and `offline_return`.

## 2. Idle / AFK RPG

**Definition and player fantasy.** Collect heroes and build a team that battles automatically through stages. Rewards accumulate while away (AFK loot) and are spent on levelling, ascension and gear. The player's skill is team composition and progression choices, not real-time play. The fantasy is a commander with a growing, glorious roster: progress without grind, and collection pride.

**Core loop** (minutes). Collect AFK rewards → level and upgrade heroes → attempt the next stage (an auto battle that is deterministic for a given team and seed) → win means progress and higher AFK rates; loss means re-optimizing the team → repeat.

**Meta loops.**
- Hero summoning (gacha), with factions and synergies.
- A campaign stage ladder, towers and dungeons with distinct rules.
- Guilds and guild bosses, arena (async PvP), events and season passes.
- Shared level systems (for example, a resonance that levels a whole team) that reduce feed-hero grind.

**Session profile** (estimate). 2–10 minutes several times a day (collect, upgrade, push), plus longer event sessions.

**Signature mechanics** (`mechanics-codex`: auto-combat, collection, randomness-loot, build-crafting, generators-timers).
- Deterministic auto-battle with formations, faction advantage and skill timers. Outcomes are reproducible per seed, which is excellent for verification.
- The AFK accumulator: `loot = min(elapsed, cap) × stage_rate`. The stage rate rises with progress, which drives stage pushing.
- Power gates: stage difficulty grows faster than casual upgrade rates. The gap is where monetization pressure lives, so tune it ethically.

| Parameter | Starting value to tune (heuristic) | Effect |
|---|---|---|
| AFK cap | About 12 hours is common; extendable | Daily check-in rhythm |
| Team size | 5 | Synergy depth |
| Faction advantage | Moderate damage bonus | Roster breadth pressure |
| Summon odds and pity | Disclosed, simulated (`gacha_calc.py`) | Fairness and compliance |
| Stage power growth | Slightly faster than F2P power growth after the early game | Push pacing and spend pressure |

**Monetization model and typical mix.**
- IAP-led: summons (disclosed odds, pity), a monthly card or subscription, a season pass, VIP tiers and progression bundles.
- Rewarded ads for extra AFK time or summons in some titles.
- Loot-box rules apply per country [V3] (`legal-ethics`).

**KPI expectations.** No sourced range. Qualitatively, a long tail with high payer depth; D1 depends on early generosity.

**Retention drivers.**
- AFK loot waiting.
- The next hero summon.
- Guild bosses.
- Events.
- Arena ranks.
- Visible stage-push milestones.

**Content pipeline and production scope** (estimates).
- Heroes are the main cost: art, animation (often 2D skeletal or VFX-heavy), skills, balance and lore. Live games release heroes regularly.
- Stages are data. Verify team-power requirements with headless battle sims across archetype rosters.
- Slice: 3–5 people plus agents, 8–12 weeks. Soft launch: 20–40 people, 12–24 months.

**Reference titles.** AFK Arena (Lilith Games), AFK Journey, Idle Heroes (DH Games), Legend of Slime-style idle RPGs.

**What makes it succeed / fail.**
- Succeeds: heroes with personality and spectacle, generous early pacing, and clear upgrade paths.
- Succeeds: anti-grind systems, and transparent gacha.
- Fails: hero art inconsistency, power walls that feel purely monetized, and confusing currencies (a common complaint in the genre).
- Fails: weak guild and social systems.

**Innovation vectors.**
- Open-world or exploration layers on the AFK core.
- Hybrid roguelite modes.
- Lower-currency, cleaner economies.
- Deterministic crafting alternatives to gacha.
- Narrative seasons.

**Agent-buildability: 3/5.** Battles are deterministic and headless-simulable, and the economy and gacha are checkable. Points are lost for content volume and consistency (heroes, animation, VFX) and for long-horizon balance judgment across a growing roster. `rpg-gacha.md` §3 scores the lighter, systems-first idle RPG (prestige layers, equipment rolls, fewer heroes) at 5/5; the gap is hero content volume.

**Starter feature list (P0 vertical slice).**
1. Battle simulation core — deterministic per seed; the same team and seed give an identical log in 100 runs (unit-tested).
2. Formation screen — place 5 heroes front and back; power is computed and displayed.
3. Eight heroes in two factions — distinct skills, faction advantage applied in the formula (unit-tested).
4. Battle presentation — auto battle with skip and 2× speed; skill VFX readable on the low tier.
5. Campaign — 30 stages with power requirements from the battle sim (archetype rosters).
6. AFK accumulator — loot from the guarded elapsed time, capped; the collect screen shows rates.
7. Hero levelling — XP and gold costs per `progression_calc.py` curve; stat growth tested.
8. Summon banner — disclosed rates and pity, verified by `gacha_calc.py`; odds reachable in one tap.
9. Economy sim — the day-1/7/30 progression bands per archetype are met (`economy_sim.py`).
10. Daily quests — 5 quests with a reward track.
11. Save and resume — server-authoritative stub or signed local save; reinstall restores via account link (stub).
12. Analytics — `stage_attempt` (team power, result), `summon` and `afk_collect`.

## 3. Tycoon

**Definition and player fantasy.** Build and manage a business or attraction: mines, factories, parks, studios or cities. Hire managers, upgrade stations, balance throughput and expand. Variants run from idle tycoons (production chains, managers, offline income) to simulation tycoons (theme parks, game studios, city builders) with more player decisions. The fantasy is the shrewd owner: watching a system you designed hum, then optimizing it.

**Core loop** (seconds to minutes). Inspect bottlenecks → upgrade or hire → throughput rises → income → expand to a new shaft, floor or area → repeat. Simulation tycoons add a build-placement and customer-satisfaction layer.

**Meta loops.**
- Several businesses or continents, each a prestige-like stage with higher multipliers.
- Managers with abilities (often collectible, sometimes gacha) and research trees.
- Events with temporary businesses, plus achievements.

**Session profile** (estimate). 3–10 minutes, several times a day for idle tycoons; 10–30 minutes for sim tycoons.

**Signature mechanics** (`mechanics-codex`: production-chains, economy-flow, generators-timers, customization).
- **Chain throughput.** The output of a chain is the minimum of its stages. Upgrading anything other than the bottleneck is wasted, and teaching that is the core skill. Example: a mine shaft produces 100/s, the elevator moves 60/s and the warehouse handles 80/s, so the chain outputs 60/s. Upgrade the elevator first.
- Manager abilities: timed boosts on cooldown that give active-play value.
- Sim tycoons: placement adjacency, customer needs and satisfaction, research unlocks.

| Parameter | Starting value to tune (heuristic) | Effect |
|---|---|---|
| Stage upgrade r | Geometric per level | Pacing |
| Bottleneck rotation | Bottleneck moves every few upgrades | Keeps decisions alive |
| Manager boost | Strong multiplier, short duration, long cooldown | Check-in reason |
| New business multiplier | Large jump in base income | Prestige satisfaction |
| Offline cap | A few hours | Return cadence |

**Monetization model and typical mix.** Rewarded ads (boosts, offline 2×), IAP (super managers, permanent multipliers, premium currency, passes). Sim tycoons on mobile are sometimes premium.

**KPI expectations.** No sourced range; qualitatively, idle-like long tails.

**Retention drivers.**
- The bottleneck puzzle.
- New-business reveals.
- Manager collection.
- Offline returns.
- Events.

**Content pipeline and production scope** (estimates).
- Each business is a station set, theme art and an economy table.
- Sim tycoons add building catalogs and customer agent simulation, so content and testing costs rise.
- Slice: 1–3 people plus agents, 3–6 weeks for an idle tycoon. Soft launch: 4–12 people, 6–12 months; more for a sim tycoon.

**Reference titles.** Idle Miner Tycoon (Kolibri Games), RollerCoaster Tycoon Touch (Atari), Game Dev Story (Kairosoft), Pocket City (Codebrew Games), SimCity BuildIt (EA).

**What makes it succeed / fail.**
- Succeeds: a readable bottleneck, satisfying automation, and an appealing miniature world.
- Succeeds: meaningful choices beyond "buy everything".
- Fails: obvious dominant strategies, opaque numbers, and walls without new systems.
- Fails: too many timers competing for attention.

**Innovation vectors.**
- Arcade-idle hands-on hybrids (`hyper-hybrid-casual.md`).
- Narrative tycoons with characters.
- Co-op contracts.
- Sim tycoons with UGC layouts and shareable parks.

**Agent-buildability: 4/5.** Chains and agents are deterministic and simulable, and bots can find bottlenecks. A point is lost for theme art per business and, for sim tycoons, placement UX and agent-behaviour polish.

**Starter feature list (P0 vertical slice).**
1. Chain model — 3 stages (produce, transport, sell) with throughput = the minimum of the stages (unit-tested).
2. Bottleneck indicator — the slowest stage is highlighted, with a recommended upgrade.
3. Stage upgrades — cost curve and rate gain per level from data; bulk buy.
4. Managers — one per stage; automates it and has a timed active boost on cooldown.
5. Expansion — unlock shaft 2 and 3 at income thresholds.
6. Offline income — guarded elapsed time; cap; return screen with a rewarded 2×.
7. Second business — completes the prestige loop with a base income multiplier.
8. Economy sim — a bot completes business 1 within the target hours for each archetype.
9. Rewarded boost — 2× income for N minutes; opt-in; daily cap.
10. Miniature world presentation — workers animate along routes; 60 fps on the mid tier.
11. Save integrity — autosave and kill-restore consistency (scripted).
12. Analytics — `upgrade` (stage, level), `business_unlocked` and `offline_return`.

## 4. Farming

**Definition and player fantasy.** Plant crops on timers and harvest them. Turn them into goods in production buildings, fill delivery orders (truck, boat, train), expand and decorate the farm, and trade or help neighbours. Adventure-farming variants add energy-gated exploration. The fantasy is a cosy, self-made pastoral life: tending something that grows, being productive without pressure, and having a place that is yours.

**Core loop** (minutes). Harvest what is ready → replant → collect finished goods and queue new production → fill orders → coins and XP → buy buildings, animals and decorations → expand land.

**Meta loops.**
- XP levels that unlock crops, buildings and recipes in a steady drip.
- Storage upgrades (barn, silo) and land expansion gated by materials that drop randomly. This creates scarcity and trading.
- Social: neighbourhoods or co-ops, help requests, a roadside shop or player trading, co-op events.
- Seasonal events, a pass, and decoration collections.

**Session profile** (estimate). 5–15 minutes, 3–6 check-ins a day, each aligned with timer lengths.

**Signature mechanics** (`mechanics-codex`: generators-timers, production-chains, economy-flow, social-coop, customization).
- **Timer ladder.** Mix short timers (minutes), medium (about an hour) and long (8+ hours, overnight) so every check-in interval has something ready. Design for check-in intervals of about 15 minutes, 2 hours and 8 hours. At each, at least one meaningful collection should exist.
- **Storage as a sink and gate.** A full barn forces choices: sell, fill orders, or upgrade with scarce materials.
- **Production chains**, for example wheat → feed → chickens → eggs → bakery. Long chains multiply value, and the value per hour of each building should be balanced so no single loop dominates.
- **Order boards** that turn production into goals, with a mix of easy and stretch orders.

| Parameter | Starting value to tune (heuristic) | Effect |
|---|---|---|
| Timer spectrum | Minutes to overnight, per item tier | Check-in fit |
| Production slots per building | 2–3, more via premium | IAP lever and parallelism |
| Storage capacity growth | Slower than production growth | Keeps the sink alive |
| Rare material drop rate | Low, tuned so trading is worthwhile | Social interdependence |
| Order value | Above market price for chained goods | Rewards long chains |

**Monetization model and typical mix.**
- IAP premium currency: skip timers, buy rare materials, add production slots, unlock premium decorations and passes.
- Ads are light: rewarded for small speed-ups or extra orders.

**KPI expectations.** No sourced range. Qualitatively: long tails with strong habit formation; social systems drive months-long retention.

**Retention drivers.**
- Something is always ready.
- The next unlock level.
- Neighbourhood obligation and help.
- Seasonal events.
- Decoration self-expression.

**Content pipeline and production scope** (estimates).
- Content volume is high: crops, animals, buildings, recipes, decorations and seasonal sets, all in one style.
- The economy needs a long-horizon simulation (90–365 days) across archetypes.
- Social trading needs backend services and anti-abuse.
- Slice: 2–4 people plus agents, 6–10 weeks. Soft launch: 15–30 people, 12–24 months.

**Reference titles.** Hay Day (Supercell), Township (Playrix), FarmVille 3 (Zynga), Stardew Valley (ConcernedApe; premium RPG-farming), Family Island and Klondike Adventures (adventure farming).

**What makes it succeed / fail.**
- Succeeds: a well-designed timer ladder, a charming, living farm and real social interdependence.
- Succeeds: generous early levels, and seasonal freshness.
- Fails: dead check-ins (nothing ready), and storage pain that feels like a paywall.
- Fails: a stagnant mid-game, and trading exploits.

**Innovation vectors.**
- Story and adventure layers (explore beyond the farm).
- Farming plus merge or puzzle cores.
- Cosy-game crossovers with life-sim relationships.
- Co-op farming with real-time presence.

**Agent-buildability: 3/5.** Timers, chains and orders are deterministic and simulable over long horizons. Points are lost for large consistent art catalogues, social backend and trading integrity, and long-horizon pacing judgment that needs live data.

**Starter feature list (P0 vertical slice).**
1. Farm grid — plots placed on an isometric grid; the tap-and-drag plant interaction works one-handed.
2. Crops and timers — 4 crops with timers from minutes to an hour; the guarded clock credits offline growth.
3. Harvest and storage — harvest to the barn; capacity enforced; full-barn messaging with clear options.
4. Production building — 1 building with 2 slots and 3 recipes using crops; queue persists across kills.
5. Order board — 6 orders generated from unlocked items; filling pays coins and XP.
6. XP levels — 10 levels unlock items per a data table; the level-up shows unlocks.
7. Storage upgrade — needs rare materials that drop from harvests (seeded rates).
8. Decoration — 5 decorations placeable and persistent.
9. Economy sim — 30-day archetype runs show check-in value at the 15 min, 2 h and 8 h intervals.
10. Notifications (opt-in) — "crops ready" for the longest timer only; respects quiet hours.
11. Premium speed-up — skips a timer for premium currency, with a confirmation above a threshold cost.
12. Analytics — `harvest`, `order_complete`, `storage_full` and `speedup_used`.

## 5. Life sim

**Definition and player fantasy.** Live a simulated life. Create an avatar, manage needs and careers, build relationships, furnish homes and experience life events. The forms range from 3D avatar sims to text-driven life-choice games (BitLife), cosy companion and pet lives, and open-ended dollhouse play aimed at children. The fantasy is living another life: self-expression, aspiration, nurturing, and harmless social drama.

**Core loop** (minutes). Check needs and goals → take actions (work, socialize, care, shop), often timed → earn money, XP or relationship points → buy items, clothes and homes → life events and choices → repeat. Text sims: age up → random event → choose → consequences → age up.

**Meta loops.**
- Career ladders, skills and relationship stages.
- Home ownership and decoration, with collections of outfits and furniture.
- Legacy and generations: a new life inheriting traits or wealth.
- Live events, seasonal content and social visits or sharing.

**Session profile** (estimate). 5–20 minutes. Text sims come in short bursts (one life per session or less); avatar sims run longer.

**Signature mechanics** (`mechanics-codex`: narrative-choice, customization, generators-timers, randomness-loot, social-coop).
- Needs that decay over time and timed actions that restore them. Tune the decay so neglect is recoverable, not punitive.
- Weighted random event tables with conditions (age, traits, stats). Their variety and wit are the text sim's content.
- Relationship meters with thresholds that unlock interactions.
- A customization catalogue of avatars, clothes and furniture: the main expression and monetization surface.

| Parameter | Starting value to tune (heuristic) | Effect |
|---|---|---|
| Need decay | Full to empty over many hours | Pressure vs cosiness |
| Event table size | Hundreds to thousands of events (text sims) | Replay variety |
| Event repeat suppression | Per life and per player | Freshness |
| Catalogue drop cadence | Regular themed sets | Live-ops and IAP rhythm |
| Action timers | Minutes to hours | Check-in rhythm |

**Monetization model and typical mix.**
- IAP: cosmetics and catalogue items, content packs or expansions, premium memberships (text sims sell unlocks such as god-mode style controls), time skips.
- Ads are common in text sims (rewarded for retries or extra choices).

**KPI expectations.** No sourced range. Qualitatively, retention rides on self-expression and fresh content; text sims rely on replay variety.

**Retention drivers.**
- Self-expression and collection.
- Aspirational goals (dream house, career top).
- Surprising life events.
- Seasonal catalogue drops.
- Social sharing.

**Content pipeline and production scope** (estimates).
- 3D avatar sims are among the most content-heavy mobile genres: avatar system, animations, catalogue items and agent behaviours.
- Text sims are writing-heavy but art-light. An LLM can draft events, but humans must edit for wit, sensitivity and age-appropriateness.
- Kids' dollhouse play falls under kids' regulation, including the amended COPPA Rule with an April 22, 2026 compliance deadline [V4]; see `narrative-rhythm-edu-kids.md` and `legal-ethics`.
- Slice: 1–2 people plus agents, 3–6 weeks for a text sim; 4–8 people, 10–16 weeks for an avatar sim. Soft launch: 3–8 people for text; 30+ people, 18–30 months for 3D.

**Reference titles.** The Sims FreePlay (EA), BitLife (Candywriter), My Talking Tom (Outfit7), Toca Life World (Toca Boca), Animal Crossing: Pocket Camp (Nintendo).

**What makes it succeed / fail.**
- Succeeds: deep self-expression, writing with personality (text sims) and cosy pacing.
- Succeeds: steady catalogue drops, and respect for player time.
- Fails: needs that nag, thin event pools that repeat, and catalogue inconsistency.
- Fails: aggressive monetization of basic expression, and insensitive event writing.

**Innovation vectors.**
- AI-driven characters and dialogue as a mechanic, with cost controls and the consent and reporting requirements of `legal-ethics`.
- Text plus light visuals.
- Social and co-living spaces.
- UGC catalogue items with moderation.

**Agent-buildability: 2/5** (avatar sim); **4/5** (text-driven life sim). The text form is systems plus writing. Event tables are verifiable for coverage, reachability and no dead ends, and the art is light. The avatar form loses points for a massive asset catalogue, animation, agent behaviour polish and taste-judged expression.

**Starter feature list (P0 vertical slice).** Example: a text-driven life sim.
1. Life state model — age, stats (health, happiness, smarts, looks), money, relationships and traits; serialisable.
2. Age-up loop — "age +1" triggers 1–3 events from the weighted, conditioned table (seeded, deterministic).
3. Event table — 150 events with conditions, choices and effects in JSON; the validator finds no unreachable events and no dead-end choices.
4. Choice UI — 2–4 choices with clear consequences shown; readable at 16 pt minimum.
5. Careers — 3 career ladders with requirements and salaries.
6. Relationships — family, friends and partners with meters and interactions that change them.
7. Death and legacy — a life ends with an obituary summary; start a new life with an optional inheritance.
8. Achievements — 20 achievements across lives (collection meta).
9. Repeat suppression — no event repeats within a life unless flagged repeatable (tested over 1,000 simulated lives).
10. Content review gate — all event text passes the sensitivity and age-rating review checklist (human checkpoint).
11. Rewarded retry — rewind the last choice once per life via a rewarded ad.
12. Analytics — `life_end` (age, cause, career, achievements) and `event_choice` (event id, choice).

## 6. Home design

**Definition and player fantasy.** Decorate rooms and homes to briefs. Choose furniture, finishes and decorations from a catalogue to fit a client's style and budget, then submit for a community vote or score and earn rewards to grow the catalogue. Related forms: renovation stories (often fused with a puzzle core) and house flipping. The fantasy is having taste and an aspirational lifestyle, with creative expression validated by others.

**Core loop** (minutes). Accept a design challenge (brief: style, room, required items) → fill slots (sofa, rug, lighting, wall) from the catalogue, spending soft or premium currency → submit → votes or score → rewards (currency, XP, items) → expand the catalogue → next challenge.

**Meta loops.**
- Catalogue collection: owned items persist and are reusable.
- Designer levels, unlockable styles and rooms, and events with themed catalogues.
- Clubs and teams, and a personal showcase home.

**Session profile** (estimate). 5–15 minutes; a challenge takes a few minutes; tickets or energy pace attempts.

**Signature mechanics** (`mechanics-codex`: customization, collection, competition, economy-flow).
- Slot-based room templates: each slot has curated alternatives, which keeps compositions coherent and render-safe.
- Scoring: community pairwise voting (Design Home-style) is fair at scale but needs a live player base. With no players, use a transparent tag-match rubric (style tags against the brief) and say so. Never fabricate "community" votes.
- Premium-item scarcity and catalogue drops as the economy's spine.

| Parameter | Starting value to tune (heuristic) | Effect |
|---|---|---|
| Slots per room | 6–12 | Effort per challenge |
| Alternatives per slot | 10+ shown, filtered by style | Choice without overload |
| Premium share of items | A minority, clearly marked | Fairness perception |
| Votes per submission | Enough for a stable rank | Score reliability |
| Challenge tickets | A few per session, regenerating | Pacing and IAP |

**Monetization model and typical mix.**
- IAP: premium currency for premium items, ticket refills, passes and event bundles.
- Real-brand catalogue partnerships appear in this genre (Design Home used real-brand furniture), which is a sponsorship revenue line with contract and IP implications (`legal-ethics`).

**KPI expectations.** No sourced range. Qualitatively, a niche, high-intent creative audience with strong payer depth when the catalogue is aspirational.

**Retention drivers.**
- New catalogue drops.
- Score and rank validation.
- Themed events.
- A personal showcase.
- Club competitions.

**Content pipeline and production scope** (estimates).
- **The catalogue is the game.** It needs hundreds to thousands of items rendered consistently (lighting, scale, perspective) for fixed camera angles, plus room templates.
- AI 3D and image generation can produce candidates, but scale, style and render consistency require a strict pipeline and art direction (`ai-asset-pipeline`, `technical-art`).
- Slice: 3–5 people plus agents, 8–12 weeks. Soft launch: 15–30 people, 12–24 months.

**Reference titles.** Design Home (Crowdstar), Redecor (Reworks), Property Brothers Home Design (Storm8). Homescapes (Playrix) is the renovation-meta crossover.

**What makes it succeed / fail.**
- Succeeds: an aspirational, coherent catalogue, fair and fast scoring, and briefs that inspire.
- Succeeds: respect for creative effort.
- Fails: an inconsistent item style or scale, and paywalled briefs (brief requires premium items).
- Fails: unfair or slow voting, and catalogue droughts.

**Innovation vectors.**
- AI-assisted styling suggestions.
- AR room previews.
- UGC and shoppable items (with clear disclosure).
- Co-design with friends.
- Fusions with puzzle or merge cores to earn items.

**Agent-buildability: 2/5.** The systems are simple. The catalogue volume and render consistency are taste-judged and heavy, voting needs a live community or an honest rubric, and visual verification dominates.

**Starter feature list (P0 vertical slice).**
1. Room template — one living room with 8 slots and fixed camera; items snap to slot anchors.
2. Catalogue — 80 items (10 per slot) with style tags, price and premium flag; render consistency passes the visual gate.
3. Slot picker UI — swipe through alternatives per slot; filter by style; preview in place within 100 ms.
4. Brief system — 6 briefs (style, required tags, budget); requirements are checked before submit.
5. Scoring (cold start) — a transparent tag-match rubric explained in the UI; no fake votes.
6. Rewards and economy — currency and XP per score band; economy sim shows a balanced catalogue unlock pace.
7. Ownership — bought items persist and are reusable in later challenges.
8. Tickets — challenges cost tickets with regeneration; refill offer.
9. Showcase — save and view your past designs in a gallery.
10. Voting stub — pairwise vote UI behind a feature flag for when a player base exists.
11. Accessibility — colour descriptions for items (alt text) and large touch targets.
12. Analytics — `challenge_submit` (brief, score, premium items used) and `item_purchase`.

## 7. Restaurant / time management

**Definition and player fantasy.** Serve customers in short, timed levels: take orders, cook, assemble and serve before patience runs out. Chain taps efficiently, upgrade the kitchen and decor between levels, and move through restaurants and cities. The fantasy is frantic competence: running a packed kitchen, getting into a flow of perfect service, and enjoying cosy food.

**Core loop** (seconds). A customer arrives with an order → tap ingredients and stations (cook, wait, assemble) → serve → coins and tips (bonus for speed or combos) → the level ends with stars for its goal → upgrade → next level.

**Meta loops.**
- Restaurants and cities in sequence, each with new dishes and mechanics.
- Kitchen equipment upgrades (speed, capacity, auto-cook) and decor (patience bonus).
- Story chapters with characters, boosters, events and tournaments.

**Session profile** (estimate). Levels of 1–2 minutes; sessions of 3–10 minutes; energy or level gating in some titles.

**Signature mechanics** (`mechanics-codex`: timing, production-chains, economy-flow, progression-unlocks).
- Order queues and patience timers, with visible patience states (happy, neutral, angry).
- An input buffer: queued tap sequences let skilled players plan ahead (tap tap tap) and keep the game fair on lower-end devices.
- Cooking states (raw, cooking, done, burnt), so attention is split across stations.
- Capacity planning: with customer arrival rate λ and effective service rate μ (which rises with upgrades), tune hard levels so λ approaches μ at the expected upgrade level. Above that, failure is guaranteed; far below, it is boring.

| Parameter | Starting value to tune (heuristic) | Effect |
|---|---|---|
| Level length | 60–120 s | Session fit |
| Arrival rate | Ramps within a level; peaks near the end | Tension arc |
| Patience | Seconds; extended by decor | Fail pressure |
| Burn window | A few seconds after done | Attention split |
| Upgrade effect | Shortens cook time or adds capacity | Long-term difficulty relief |

**Monetization model and typical mix.**
- IAP: gems for upgrades, boosters (auto-serve, instant cook, patience), energy in some titles, passes and bundles.
- Rewarded ads for double coins or retries.
- More casual versions carry interstitials between levels.

**KPI expectations.** No sourced range. Qualitatively, solid casual retention driven by restaurant variety; upgrade walls are the main churn risk.

**Retention drivers.**
- New restaurants and dishes.
- Three-star mastery.
- Story beats.
- Upgrade progress.
- Events and tournaments.

**Content pipeline and production scope** (estimates).
- Per restaurant: dish set (ingredient and state sprites), stations, customers, background and 40–80 levels from data templates.
- Verify levels with a tapping bot that has reaction-time and planning parameters, to estimate star rates per upgrade level.
- Slice: 1–3 people plus agents, 4–8 weeks. Soft launch: 5–15 people, 8–14 months.

**Reference titles.** Cooking Fever (Nordcurrent), Cooking Diary (MyTona), Diner Dash (PlayFirst), Good Pizza, Great Pizza (TapBlaze).

**What makes it succeed / fail.**
- Succeeds: readable states, responsive buffered input, satisfying service juice, varied restaurants and fair upgrade pacing.
- Fails: tiny targets, input lost under pressure, upgrade walls that force spending, and same-feeling restaurants.

**Innovation vectors.**
- Narrative-led cooking with characters.
- Co-op kitchens (async or real-time).
- Merge or management hybrids.
- Accessibility modes such as relaxed timers.

**Agent-buildability: 4/5.** The customer simulation is deterministic with seeded arrivals, and bots with reaction-delay distributions estimate star rates per upgrade state. The art per restaurant is moderate. A point is lost for timing feel, multi-station UX polish and per-restaurant art volume.

**Starter feature list (P0 vertical slice).**
1. Customer simulation — seeded arrivals per a level script; queue and patience states; leaving costs a customer.
2. Orders — 3 dishes with 2–3 ingredients each; order bubbles readable at a glance.
3. Stations and cook states — raw, cooking, done and burnt with timers; burnt items are discarded.
4. Tap input buffer — up to N queued taps execute in order; no lost taps at 5 taps/s (scripted test).
5. Serve and tips — serving pays coins plus a speed-based tip; consecutive serves show a combo.
6. Level goals and stars — "earn X coins" with 1–3 star thresholds; results screen.
7. 20 levels — from data templates; the tapping-bot star rate within target bands at expected upgrades.
8. Upgrades — 3 station upgrades with cost curves; the effect on cook time is unit-tested.
9. Decor — one decor item that extends patience (tested).
10. Booster — instant-cook booster with clear cost; fail offer of "+30 s" once.
11. Juice — sizzle, ding and coin pops; perf budget held at peak customers.
12. Analytics — `level_end` (stars, customers served and lost, coins) and `upgrade_bought`.

## 8. Volatile facts used in this file (as of Oct 2026 — verify before relying)

- [V1] A 2026 summary states that board, card, puzzle and idle games often match or beat RPG-level D7 and D30. It gives no numbers or attribution for this claim. Source: [Playio](https://blog.playio.co/d1-d7-d30-retention-benchmarks-2026).
- [V2] All-genre retention anchors (medians, viability screens, D7/D1 diagnostic, 90-second aha) are listed in `SKILL.md`, Core model 9, with sources.
- [V3] Brazil banned loot-box sales to under-18s from March 2026; a court ordered Riot to pay damages in June 2026. Source: [Sheep Esports](https://www.sheepesports.com/articles/brazil-court-orders-riot-games-to-pay-eur2-5m-over-league-of-legends-loot-boxes/en).
- [V4] The amended COPPA Rule's compliance deadline was April 22, 2026; biometric identifiers now count as personal data. Source: [Toy Association](https://toyassociation.org/PressRoom2/News/2026-News/updated-coppa-rule-requirements-take-effect-april-22.aspx).
