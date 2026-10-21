# RPG and Gacha Playbooks

RPGs with collectible characters bring in the most money per payer on mobile. They also cost the most to produce and face the most regulation. This file has five playbooks: hero collector / squad RPG, gacha action RPG / open world, idle RPG, turn-based JRPG and mobile MMORPG. Each follows the same 14-part template, so you can compare them side by side and copy them into a design contract. The shared foundations come first, because every playbook relies on them: banner probability math, power-curve rules and a compliance checklist for paid random items. Market numbers and laws are kept in a dated, sourced section, separate from the stable craft knowledge. Agent-buildability runs from 5/5 (idle RPG: pure math, deterministic, UI-heavy) down to 1/5 (open-world action and MMORPG: real-time 3D, rigging, servers, huge content volume). For an AI-agent pipeline, the practical rule is to start with an idle or turn-based squad RPG and earn the right to go real-time.

## Contents

| § | Playbook | Session profile | Primary monetization | Agent-buildability | First project for an agent pipeline? |
|---|---|---|---|---|---|
| 0 | [Shared foundations](#0-shared-foundations-gacha-math-power-curves-compliance) | — | — | — | Read first |
| 1 | [Hero collector / squad RPG](#1-hero-collector--squad-rpg) | 3–8 × 2–10 min/day | Banner gacha, monthly card, pass | 4/5 | Yes, turn-based or auto-battle |
| 2 | [Gacha ARPG / open world](#2-gacha-arpg--open-world) | 10–20 min daily + long patch-day sessions | Banner gacha, monthly card | 1/5 | No, prototype combat only |
| 3 | [Idle RPG](#3-idle-rpg) | 6–12 × 0.5–3 min/day | Hybrid: rewarded ads + IAP | 5/5 | Best first project |
| 4 | [Turn-based JRPG](#4-turn-based-jrpg) | 20–60 min (premium); 10–20 min daily (F2P) | Premium or F2P gacha | 3/5 | Yes, as a combat-first slice |
| 5 | [Mobile MMORPG](#5-mobile-mmorpg) | Hours of auto-play + check-ins | VIP, stat-bearing gacha, enhancement | 1/5 | No |
| — | [Volatile facts](#volatile-facts-as-of-oct-2026--verify-before-relying) | — | — | — | Check before quoting numbers |

Session figures in this table are practitioner estimates, not sourced benchmarks.

## How to use these playbooks

1. Choose the playbook that matches the concept. Copy its core loop into `contract.json → loops[]` (type `core`, period `minutes`). Copy its meta loops in as `meta`, `social` and `monetization` loops.
2. Set `meta.genre: "rpg"`, set `meta.subgenre` to the playbook slug, set `session_length_target_sec` from the session profile, and set `monetization_model` (`hybrid` or `iap` for gacha, `premium` for a paid JRPG).
3. Turn the **Starter feature list** into `features.json` entries (P0, `area` as noted) with `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py feature add ...`. Use the one-line acceptance criteria as written. Every "validated against a script" criterion maps to evidence for the `unit` or `playthrough` gate.
4. Model the economy before building it. Use `${CLAUDE_PLUGIN_ROOT}/scripts/gacha_calc.py` for banners, `progression_calc.py` for XP and power curves, and `economy_sim.py` for currency flows (the economy-model schema lists the archetypes).
5. Mechanic category labels below are descriptive: combat, build-craft, collection & randomness, progression & upgrade, economy & resources, time & energy, social & competition, exploration & traversal, narrative & relationship, live events, UX automation. The taxonomy in `mechanics-codex` is authoritative. To find the matching card, run `gs.py kb "<mechanic name>" --skill mechanics-codex`.
6. KPI statements are qualitative unless they cite a source. Genre-specific retention and ARPDAU ranges in public write-ups are inconsistent and often years old, so set targets from the anchors in the volatile-facts section, then replace them with soft-launch data (`retention_ltv.py fit`).

## 0. Shared foundations: gacha math, power curves, compliance

### 0.1 Banner probability math (memorize these)

```
P(at least one hit in n pulls)            = 1 − (1 − p)^n
Pulls for a 50% chance (no pity)          = ln(0.5) / ln(1 − p)
Expected pulls, no pity                   = 1 / p
Expected pulls, hard pity H only          = (1 − (1 − p)^H) / p
Soft pity ramp from pull s, step Δ        p(n) = p0                      for n < s
                                          p(n) = min(1, p0 + (n − s + 1)·Δ)  for s ≤ n < H
                                          p(H) = 1
Expected pulls, any schedule              E = Σ_{n=0}^{H−1} Π_{k=1}^{n} (1 − p(k))
Featured unit with 50/50 + guarantee      E_featured ≈ 1.5 × E   (worst case 2H)
```

Worked numbers (my arithmetic):

| Base rate p | 50% chance at | Expected pulls, no pity | Expected with hard pity 90 | Effective rate |
|---|---|---|---|---|
| 0.6% | 116 pulls | 167 | 69.7 | 1.43% |
| 1.0% | 69 pulls | 100 | 59.5 | 1.68% |
| 2.0% | 35 pulls | 50 | 41.9 | 2.39% |

Genshin Impact's in-game details page lists a 0.6% base rate, a 1.6% consolidated rate and a 90-pull guarantee for 5★ characters. A consolidated 1.6% means about 62.5 expected pulls, so the soft pity ramp is worth about 7 pulls beyond hard pity alone. Players' community measurements put the start of the ramp around pull 74. That figure is not official. A ramp of +6 percentage points per pull from pull 74 reproduces about 62.3 expected pulls, or 1.6% (my arithmetic). Check the current details page before quoting either number. To reproduce:

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gacha_calc.py --rate 0.006 --soft-pity-start 74 \
  --soft-pity-step 0.06 --hard-pity 90 --rate-up 0.5 --guarantee --pulls 180 --json
```

The output reports 62.30 expected pulls for any 5★ unit (`any_5star.expected_pulls`, consolidated rate 1.605%) and 93.45 for the featured unit (`featured.expected_pulls`, which includes the 50/50 guarantee). Drop `--rate-up` and `--guarantee` to see the any-5★ figures alone.

**F2P generosity check (hypothetical worked example).** Suppose F2P players earn F = 40 pulls per month and a featured banner runs every 3 weeks. Then about 28 pulls arrive per banner. With E_featured ≈ 94, a saving F2P player gets one featured unit roughly every 3.4 banners. Write the design target into the contract explicitly ("a committed F2P player can get one featured unit in N"), check it with `economy_sim.py`, and give the `critic` agent the result. If N > 5, F2P players feel shut out. If N < 2, there is too little scarcity to sell.

### 0.2 Power curves and dupes

- **Stat growth.** Level gives roughly linear stat growth. Ascension, stars and gear tiers give multiplicative steps. Keep the **power ratio** between a fully invested unit and a "just pulled" unit of the same rarity within a documented band. Players accept 3–5× for heavy investment. When it reaches 10×, new players stop competing. These are design heuristics, not sourced figures.
- **Dupe power.** Duplicates (constellations, eidolons, limit breaks) are the deepest monetization lever and the most common cause of pay-to-win backlash. Put most of a unit's *function* in copy 1. Later copies should add convenience, numbers or cosmetics. If copy 7 changes the unit's role, PvP becomes a spending contest.
- **Power creep budget.** Each release should raise the meta ceiling by a set percentage. Old units should get supporting kits or reworks, not abandonment. Track the ceiling as a progression track in `contract.json → progression.tracks`.
- **Stage power curve.** Recommended power per stage follows `progression_calc.py curve --formula exp` with soft walls every 10–20 stages (`difficulty_curve.py generate --pattern sawtooth`). Walls go just past a free daily reset, so the player always has a next step.

### 0.3 Paid random items: compliance and ethics checklist

Doctrine item 8 (ethical monetization) is not optional. Before any banner ships, the `compliance-officer` agent must sign off:

- [ ] Odds for every rarity and featured unit are shown **before** purchase and reachable in one tap from the banner. Pity rules are written in plain words. Apple and Google both require odds disclosure (see volatile facts).
- [ ] Every price is shown in real money, or with a visible conversion. Avoid multi-step currency chains that hide the price of a pull. The US FTC's 2025 action against Genshin's publisher alleged that players were misled about the odds and the cost of loot boxes.
- [ ] The pity counter is visible and carries over between banners of the same type. Any reset rule is disclosed.
- [ ] Age gate and parental consent before paid random items. Geo-rules: disable paid random items in Belgium and for under-18s in Brazil, and apply Australia's classification consequences (volatile facts).
- [ ] No "complete-the-set" gacha that pays out only when a full set is assembled from random draws. Japan's consumer regulator banned this pattern (kompu gacha) in 2012, and it is a dark pattern everywhere.
- [ ] A deterministic path exists: selector tickets, shop exchange for pull-currency remnants ("sparks"), or direct-purchase skins. This is now the default for minors and regulated storefronts, and it is good practice everywhere.
- [ ] Spending insights and optional monthly limits. No pressure timers on purchases of random items.

Load `legal-ethics` and `monetization` for full detail. Run `compliance_preflight.py --project DIR` before every store build.

## 1. Hero collector / squad RPG

### Definition and player fantasy
The player collects, raises and fields a roster of distinct heroes in squads of 3–6. Squads fight PvE stages and other players' defence teams, in turn-based or auto-resolved combat. The fantasy is being *the commander of a growing legendary roster*. The motivations are completion (collect them all), mastery (finding synergies, countering the meta), power (seeing a favourite hero carry a fight) and attachment (character fandom, IP love).

### Core loop
```
pick stage → set squad (formation, synergies, counters) → battle (auto or turn-based, 30–120 s)
  → rewards (gold, XP, gear, hero shards) → upgrade (level, gear, skills, stars)
  → stronger squad → harder stage / tower floor / arena rank → pick stage
```

### Meta loops
- **Summon loop.** Earn or buy premium currency, pull on the banner, receive new heroes or dupes, ascend.
- **Roster breadth.** Element or faction counters and mode-specific rules (campaign, tower, raid boss, arena, guild war) force players to build several teams. That is the reason to keep pulling after the first strong team.
- **Gear grind.** Stamina-gated dungeons drop gear with random substats, which players reroll and enhance. Summoners War's rune system is the archetype.
- **Social.** Guild boss, guild war, donations, async arena against snapshots of other players' defence teams controlled by the AI.
- **Live ops.** Limited and collab banners, story chapters, seasonal pass, rotating challenge modes.

### Session profile
Estimate: 3–8 sessions a day of 2–10 minutes each (collect idle loot, spend stamina, do arena attacks, clear dailies), plus occasional 20–60 minute planning or raid sessions. Engaged players clear the daily checklist in about 10–20 minutes. Portrait orientation and one-handed play dominate the newer titles.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Banner gacha with pity, rate-up, sparks | collection & randomness | §0.1 math. Show the pity counter |
| Element/faction counter wheel | combat | Modifiers around ±15–30% make counters matter without hard-locking outcomes (heuristic) |
| Speed / turn-meter initiative | combat | Speed becomes the dominant stat unless capped or given diminishing returns |
| Star ascension via dupes or fodder | progression & upgrade | Keep function in copy 1 (§0.2) |
| Gear with random substats + reroll | progression & upgrade; collection & randomness | The long-tail sink for stamina |
| Stamina for PvE | time & energy | Rewards may push stamina over the cap. Never waste a refill |
| Auto-battle, 2× speed, sweep tickets | UX automation | Mandatory once a stage is three-starred |
| Async arena against AI-controlled defence | social & competition | Defence teams are a second build-craft puzzle |
| Synergy/team bonuses | build-craft | Readable icons, preview before battle |

### Monetization model and typical mix
Hybrid, but IAP-dominant. The typical mix in rough descending order is qualitative and unsourced:
1. Premium-currency packs feeding limited banners.
2. Monthly card: a low price for daily currency over 30 days. Usually the best-value item and a common first purchase.
3. Battle pass.
4. Progression-triggered bundles (stage clear, player level).
5. Growth funds.
6. Skins.

Rewarded ads appear in lighter and hybrid titles (free summon, double idle loot) and rarely in premium-positioned ones. Revenue depends heavily on a small share of high spenders. Design the ceiling deliberately and protect F2P viability (§0.1 generosity check).

### KPI expectations
Qualitative, because no reliable genre-specific ranges were found in our sources. D1 is often at or below the overall median, because onboarding is heavy and art-led creatives draw broad audiences. D30 and later retention run well above casual, because roster investment creates goals and sunk cost. Some write-ups cite mid-core D30 around 10–12%, but the sources are inconsistent and possibly date from 2022. Payer conversion is moderate and ARPPU is among the highest in mobile. Watch the D7/D1 ratio: below 0.30 points to an FTUE problem.

### Retention drivers
Daily reset (quests, free pull, stamina refill). Published banner schedules that create anticipation. Guild obligations. Arena season rewards and rank decay. Story chapters. Character attachment. Visible next-power goals. Collection-log completion.

### Content pipeline and production scope (estimates)
One new hero needs concept art, a splash illustration, an in-battle model or sprite, 3–4 skill animations with VFX, voice barks, kit design, a balance simulation and localization. Rough scopes, all estimates:
- 2D vertical slice: 4–8 people, 6–9 months.
- Competitive global launch: 30–100+ people, 2–3+ years.
- Live cadence: 1–2 heroes plus one event every 2–3 weeks.

Bank at least 6 months of content before global launch. For an agent pipeline, use static portraits plus tweened "puppet" animation, or frame-based sprites. No vendor automates Spine or Live2D rigging (volatile facts).

### Reference titles
- *Summoners War: Sky Arena* (Com2uS, 2014): runes as the gear grind, deep PvP.
- *Star Wars: Galaxy of Heroes* (EA Capital Games, 2015): IP-driven squads.
- *Marvel Strike Force* (FoxNext, 2018): the same pattern with Marvel.
- *Raid: Shadow Legends* (Plarium): UA-scale roster depth.
- *Epic Seven* (Smilegate, 2018): anime production values.
- *Fire Emblem Heroes* (Intelligent Systems/Nintendo, 2017): tactics-grid squads.
- *AFK Arena* (Lilith, 2019): an idle hybrid, see §3.
- *Cookie Run: Kingdom* (Devsisters, 2021): a kingdom-building meta.
- *Blue Archive* (Nexon Games, 2021): story and character fandom.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Characters are memorable. Art direction is the UA engine | Power creep invalidates favourites and players quit with them |
| Combat has real team-building decisions | Combat is a stat check with no decisions |
| Early pulls feel generous and pity is fair and visible | Odds feel stingy or opaque, and the community revolts |
| Respect-for-time features (auto, sweep, skip) | Too many currencies, chores and stamina types |
| A whale chase that leaves F2P relevant | Content droughts, or launching without a content buffer |
| Years of steady live-ops cadence | Art inconsistency across heroes made by different pipelines |

### Innovation vectors
- Casual-core hybrids: idle hero RPGs and roguelite "survivor" action with hero collection.
- Cross-genre metas: city building, dating-sim bonds.
- Transparent monetization (selectors, sparks, direct purchase) as loot-box law spreads.
- Web shops for direct-to-consumer margin.
- PC cross-play.
- LLM-driven character companions, which need consent, report and disclosure flows under store rules (see `legal-ethics`).

### Agent-buildability: 4/5
**Why high:**
- Turn-based or auto combat runs as a deterministic sim-core, so thousands of headless battles can balance kits and stage curves.
- Screens are UI-heavy and pass structural checks.
- Economy and gacha are fully simulatable.

**Why not 5:**
- Character art volume and consistency need a locked style and a LoRA after 20–50 approved images.
- Skill animation and VFX are the weakest automated links.
- Gacha compliance and community management need humans.

### Starter feature list (P0 vertical slice)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Deterministic battle sim-core (gameplay) | Same seed and squads produce identical results over 1,000 headless replays. Median battle 30–90 s at 1× |
| 2 | Squad setup screen (ui) | 5 slots, tap-to-assign in portrait with one hand. Synergy preview updates on every change |
| 3 | Element counter wheel + 4 roles (gameplay) | Counter modifiers read from contract parameters. Sim shows the counter matchup moves win rate by the contract target |
| 4 | Campaign map, 30 stages (content) | Stage power from `progression_calc.py`. A bot with the recommended team clears stages 1–10 at least 95% of the time |
| 5 | Hero level-up + star ascension (meta) | Costs come from the tuning table. Caps enforced. Before/after stat preview |
| 6 | Gear drops with one random substat (meta) | Equip, unequip, compare. Sim finds no stat overflow after 10k drops |
| 7 | Banner summon with pity (monetization) | Simulated rates match `gacha_calc.py` within ±0.2 pp over 1M pulls. Odds screen one tap away. Pity counter visible |
| 8 | Wallet + ledger (tech) | Every grant and spend logged with a source/sink id. Balances never go negative. Ledger replays to the same totals |
| 9 | Stamina with regen (meta) | Regen interval from config. Correct across app background, kill and clock-change tests |
| 10 | Auto-battle, 2× speed, sweep (ux) | Sweep grants the same reward table as a won battle without loading combat |
| 11 | Daily quests + login reward (liveops) | Reset at server time. 5 quests completable within 10 min by the scripted playthrough |
| 12 | Async arena vs AI-controlled snapshots (meta) | Offers 3 opponents within ±10% power. Rank updates. Works with local fixtures offline |
| 13 | FTUE to first 10-pull (ux) | First summon reached in 3 min or less with a guaranteed starter. `ftue_step` events fire in order |

## 2. Gacha ARPG / open world

### Definition and player fantasy
Real-time action combat in 3D, either in an open world or in a hub with instanced zones. The player switches between members of a party of collected characters and pulls on separate character and weapon banners. The fantasy is being *an adventurer in a beautiful, living world with a cast I love*. It combines exploration, spectacle, character fandom and action mastery (elemental combos, dodge timing).

### Core loop
```
explore / take quest → real-time combat (party swap, elemental reactions, dodge)
  → loot (materials, chests, currency) → level characters / weapons / talents
  → unlock region or story chapter → explore
```

### Meta loops
- **Banners.** Separate character and weapon banners. Dupes (constellations/eidolons). Pity carries over within each banner type.
- **Stamina-gated material farming.** A "resin" refill is spent on domains for ascension and talent materials. This is the daily anchor.
- **Exploration completion.** Chests, puzzles and collectibles per region, with a completion percentage.
- **Rotating endgame challenge.** Floors or score attacks that reset on a fixed cycle and reward premium currency.
- **Version cadence.** A new region, characters, story and events on a regular cycle. HoYoverse titles have run roughly six-week versions (observed).

### Session profile
Hybrid, and these are estimates. A 10–20 minute daily check-in spends stamina and clears dailies. Long 1–3 hour exploration sessions come on patch days. Play is heavily cross-platform (PC/console), so mobile is often the "check-in" device. Thermal throttling is a real constraint: Google warns that frame rates often degrade after 45–50 minutes of play.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Party swap + elemental reaction matrix | combat; build-craft | Reactions turn the roster into combat depth and give a reason to pull |
| Traversal (climb, glide, swim) with stamina | exploration & traversal | The world is the content. Traversal must feel good with touch controls |
| Character + weapon split banners, 50/50 guarantee | collection & randomness | §0.1 E_featured ≈ 1.5 × E |
| Stamina-gated domains | time & energy | Daily cap on progression speed, which protects the content runway |
| Gear sets with random substats | progression & upgrade; collection & randomness | The endless optimization sink |
| Rotating endgame challenge | live events | Gives whales a reason to invest and F2P a monthly goal |
| Optional co-op world | social & competition | Low-pressure, mostly peer-to-host |

### Monetization model and typical mix
IAP only, no ads. Premium currency for banners is by far the largest line. A low-price monthly card (daily currency) is the volume product. Then battle pass, first-purchase double-currency bonuses, and a small share from skins. Revenue is **lumpy and banner-driven**: popular characters spike, and weak banners dip. Web-shop top-ups are increasingly offered where store rules allow (see `monetization`).

### KPI expectations
Qualitative only, because no sourced genre ranges were found. Launch is driven by massive pre-registration and UA. Long-term revenue tracks banner desirability more than install volume. Retention is strong in the core audience, and patches with weak content cause visible dips. Watch payer re-engagement per banner and the share of stamina used each day.

### Retention drivers
Version cadence (region, story, characters). Daily stamina. Endgame reset cycles. Exploration completionism. Events that give away a free character. Attachment to the cast. A large creator and social-media ecosystem.

### Content pipeline and production scope (estimates)
The largest scope on mobile. Each region is months of level art, quests and multi-language voice-over. A competitive title is reported to need hundreds of developers over several years (estimate). An indie-feasible version is a hub with instanced action dungeons and 4–8 characters: 6–12 people, 12–24 months (estimate). 3D rigging, animation and VFX are the weakest automated links. API rigging covers humanoids only, and no production AI VFX generator API exists (volatile facts).

### Reference titles
- *Genshin Impact* (miHoYo/HoYoverse, 2020): the template.
- *Honkai Impact 3rd* (miHoYo, 2016): stage-based predecessor.
- *Tower of Fantasy* (Hotta Studio; global 2022): MMO-flavoured variant.
- *Wuthering Waves* (Kuro Games, 2024): parry-heavy combat.
- *Zenless Zone Zero* (HoYoverse, 2024): instanced, style-led action.
- *Punishing: Gray Raven* (Kuro Games): instanced stages.
- *Infinity Nikki* (Infold, 2024): non-combat open-world gacha built on fashion.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Art direction and world are the moat, and every screenshot sells | It reads as a "Genshin-like" clone with no hook of its own |
| Combat depth comes from reactions and swaps, not stats | Content cadence slips, and empty patches drive churn |
| Graphics scale down to mid-tier phones | Phones overheat, frame pacing is poor, downloads are huge |
| Generous early exploration | Stamina gates the fun parts too early |
| Characters have personality and lore | Budget and timeline overrun before launch (common) |

### Innovation vectors
- Instanced, style-led action instead of an open world (cheaper, mobile-friendlier).
- Non-combat open worlds (fashion, photography, cozy).
- Urban settings.
- Cross-progression across PC, console and mobile.
- Cloud streaming for low-end devices.
- Parry-centric combat.
- UGC housing.
- AI-driven NPC conversation, subject to store consent and reporting rules.

### Agent-buildability: 1/5
**Why low:**
- 3D characters with rigging, animation and VFX are the weakest automated links.
- Real-time action can't be verified by vision models playing from pixels (under 1% progress in research). It needs a semantic action API and scripted inputs.
- Open-world content volume and art direction are far beyond an agent pipeline.
- Mobile 3D performance needs device farms.

**What an agent can do well:**
- Capsule-character combat prototypes and frame-data tuning.
- Damage-formula and reaction-matrix simulation.
- Gacha and economy modelling.
- One instanced dungeon as a vertical slice in Unity 6.3 LTS + URP (see `engine-unity`).

### Starter feature list (P0 vertical slice: one instanced zone, not an open world)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Third-person controller + virtual joystick + auto-follow camera (gameplay) | A scripted playthrough moves A→B through the corridor. Dead zone and sensitivity come from config |
| 2 | Attack chain, dodge with i-frames, skill, ultimate (gameplay) | Frame data from the tuning table. A unit test confirms the i-frame window to ±1 frame |
| 3 | Party of 3 with swap cooldown (gameplay) | Swap completes in under 0.3 s. Off-field HP, energy and cooldowns persist correctly |
| 4 | Element application + 3 reactions (gameplay) | Reaction matrix is data-driven. A unit test covers every element pair |
| 5 | Enemy AI: 2 archetypes + 1 elite (gameplay) | Every attack has a telegraph of at least 0.5 s. A scripted-input bot clears the room |
| 6 | Damage formula + floating numbers (gameplay) | Sim DPS per character is within ±10% of contract targets |
| 7 | Instanced domain: 3 waves + boss (content) | Median clear time 2–4 min for the playthrough bot. Reward chest grants the table |
| 8 | Stamina-gated reward claim (meta) | Claim costs N. Regen correct across suspend/resume and kill |
| 9 | Character + weapon level-up (meta) | Materials consumed per the table. Caps enforced. Stat preview |
| 10 | Character banner with pity + 50/50 guarantee (monetization) | Matches `gacha_calc.py` with `--guarantee`. Odds screen before purchase |
| 11 | Quality tiers + thermal guard (perf) | Low/medium/high presets. Low tier holds p95 frame time ≤ 33.3 ms over a 10-minute soak |
| 12 | Hit feedback: hit-stop, shake, VFX, SFX (vfx) | Passes the `game-feel` checklist and the visual-gate rubric |

## 3. Idle RPG

### Definition and player fantasy
Progress builds up automatically, both online and offline. The player's decisions are about allocation: which upgrades to buy, which heroes to raise, when to prestige. The genre includes AFK-style squad idlers, tap/idle incrementals, and the "idle + equipment-roll" hybrids that charted strongly in 2023–25. The fantasy is *watching my power explode with minimal time spent*: the joy of numbers going up, optimization, and a game that respects a busy life.

### Core loop
```
auto-battle advances stages (online + capped offline) → gold / XP / gear accumulate
  → spend on upgrades (heroes, gear, skills) → push to the wall stage → stall
  → prestige/rebirth for a permanent multiplier  OR  collect AFK rewards and return later
```

### Meta loops
- **Prestige layers.** A soft reset that grants a permanent multiplier. Mature games stack 2–3 layers, each unlocking a new system.
- **Hero collection** through gacha, as in §1, often lighter.
- **Equipment roll.** Open a chest, compare, equip or auto-sell. A short and highly repeatable dopamine loop.
- **Towers and trials.** Hard skill checks outside the idle flow that use the same roster.
- **Guild, async arena, events.** As in §1.

### Session profile
Estimate: 6–12 sessions a day of 30 seconds to 3 minutes for collect-and-spend, plus occasional 10–20 minute optimization sessions. The **offline cap sets the return cadence**. An 8-hour cap with a nightly sleep produces about 3 visits a day. A 2-hour cap produces many more but punishes casual players. Portrait and one-handed.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Offline progress with cap | time & energy | Compute in closed form from the server timestamp. Detect clock rollback |
| Exponential cost growth | progression & upgrade | `cost_n = base · r^n`. Cookie Clicker's 15% per purchase is the canonical example |
| Prestige / rebirth | progression & upgrade | Currency often scales sub-linearly (for example √lifetime earnings) so later prestiges come faster in real time |
| Stage walls | progression & upgrade | Put walls where a new system or a prestige is the answer |
| Equipment-roll chests with auto-compare | collection & randomness | Auto-sell filters avoid inventory chores |
| Time-skip items ("fast rewards") | time & energy | Grant N hours of offline income instantly. A natural rewarded-ad slot |
| Big-number notation | UX automation | K/M/B/T, then aa/ab or scientific. A player setting |

**Incremental pacing math.** Buying k levels from level n costs `base · r^n · (r^k − 1)/(r − 1)`. Use this for O(1) "buy max". Time to next upgrade = cost / income rate. Target a meaningful purchase every 5–30 seconds early and every few minutes in mid-game. Trigger prestige when time to the next meaningful upgrade passes a threshold (for example 10 minutes) **and** the prestige payoff takes the player back past the previous wall in under a third of the time. Check both with `economy_sim.py` (a `per_minute` source node and a `gate` node for the wall) and a greedy bot.

### Monetization model and typical mix
Hybrid. Rewarded ads cover double offline earnings, free chests and rush timers. IAP covers a VIP or monthly card, battle pass, growth funds, hero and gear gacha, time-skip bundles and ad removal. Lighter idle titles lean on ads early and IAP later. Hybrid-casual spending grew strongly in 2025 (volatile facts), and idle RPGs sit at the centre of that trend. Cap rewarded ads per day and never interrupt battle with interstitials.

### KPI expectations
Qualitative, because no idle-specific ranges were found in our sources. D1 tends to be strong relative to mid-core, because the skill barrier is low and the first minutes are full of rewards. Long-term retention depends on prestige and system unlock pacing. The classic failure is a mid-game plateau of "nothing to do but wait". Session counts are high and sessions are short. Use the D7/D1 ratio to diagnose first-session problems.

### Retention drivers
Return pull from the offline cap. Daily quests. Prestige moments. New systems unlocking on schedule. Hero banners and events. Guild contribution. Visibly accelerating number growth.

### Content pipeline and production scope (estimates)
Mostly systems and tuning. Content means heroes, stage reskins (procedural backgrounds and enemies), events and new systems. Rough scopes, all estimates:
- Soft-launch slice: 2–6 people, 3–6 months.
- Live operation: small teams can sustain an idle game if events are template-driven.

Art needs are moderate: 2D heroes with idle and attack frames, enemy sets and chest VFX.

### Reference titles
- *Cookie Clicker* (Orteil, 2013): the incremental template.
- *AdVenture Capitalist* (Hyper Hippo, 2014).
- *Tap Titans 2* (Game Hive, 2017).
- *AFK Arena* (Lilith, 2019): idle hero collector.
- *AFK Journey* (Farlight Games, 2024).
- *Idle Heroes* (DH Games).
- *Melvor Idle*: an idle take on a skilling MMO.
- The 2023–25 wave of "idle equipment-roll" RPGs led by *Legend of Mushroom*-style titles.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Exponential pacing has frequent "pop" moments | An early wall kills D1 before the first prestige |
| There is always a clear next goal, and prestige is a real decision | Offline gains are so generous there is no reason to return, or so stingy that waiting feels like punishment |
| Number growth has satisfying VFX and SFX | Numbers become unreadable or meaningless |
| Systems unlock steadily over weeks | Content runs out, then a plateau |
| Ads are optional and well placed | Forced interstitials and ad fatigue |

### Innovation vectors
- Idle combined with roguelite runs, merge or narrative.
- Co-op idle (shared guild progress).
- Widgets and Live Activities as a check-in surface.
- PC "desktop companion" idlers that live at the edge of the screen.
- Idle layers grafted onto other genres as a hybrid-casual meta.

### Agent-buildability: 5/5
This score is for the systems-first form of the genre. The hero-gacha AFK RPG in `idle-tycoon-sim.md` §2 scores 3/5 because hero art, animation and VFX volume dominate.

**Why highest:**
- The game is math. Offline progress has a closed form, the sim is deterministic, and a greedy bot plays it perfectly.
- `progression_calc.py` and `economy_sim.py` fit directly.
- UI-heavy screens pass structural checks.
- 2D art needs are light.

**Residual human checkpoints:**
- Pacing *feel* and the first-session aha (taste).
- Anti-cheat for clock manipulation, which needs server time.

### Starter feature list (P0 vertical slice)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Big-number type + formatter (tech) | Handles at least 1e300 (mantissa/exponent). Unit tests for formatting, rounding and comparison |
| 2 | Auto-battle stage progression (gameplay) | Waves auto-advance. A timed boss every 5 stages. Failure drops the player back to farm the previous stage |
| 3 | Hero upgrades with exponential cost (meta) | Cost follows `base · r^n` from the tuning table. Buy ×1/×10/max uses the closed-form sum |
| 4 | Offline earnings with cap (meta) | Computed from the last server timestamp and capped at N hours. A clock-rollback test grants nothing |
| 5 | Prestige/rebirth (meta) | Payout per formula. Sim: after prestige, the bot passes the previous wall in 30% or less of the original time |
| 6 | Equipment chest + auto-compare + auto-sell filter (meta) | Upgrade arrow correct for 1,000 random items. The filter never sells equipped items |
| 7 | Hero summon with pity (monetization) | Matches `gacha_calc.py`. Odds screen reachable before purchase |
| 8 | Daily quests + login streak (liveops) | Resets at server time. Streak grace rule unit-tested |
| 9 | Rewarded-ad placements (monetization) | Double offline income and free chest, capped per day. Never during battle. Mock ad SDK in tests |
| 10 | Greedy-bot progression sim (tech) | Time-to-wall curve within ±15% of the contract table across 200 runs |
| 11 | FTUE: first upgrade in 20 s or less, aha in 90 s or less (ux) | The scripted playthrough reaches the first "number explosion" within 90 s |
| 12 | Save/load + cloud backup (tech) | Corrupted-save recovery test passes. Save on background |

## 4. Turn-based JRPG

### Definition and player fantasy
A party-based, story-driven RPG with command-menu turn-based combat (ATB, conditional-turn or press-turn variants), towns and dungeons to explore, and character arcs. On mobile it takes three forms:
- **Premium ports and originals**: classic Final Fantasy and Dragon Quest, *Chrono Trigger*, and small-studio catalogues such as KEMCO's.
- **Subscription-platform titles.**
- **F2P gacha turn-based**: *Honkai: Star Rail*, *Octopath Traveler: Champions of the Continent*, *Another Eden*.

The fantasy is *living an epic story with a found family*: strategic battles, discovery and watching characters grow.

### Core loop
```
explore town/dungeon → encounter (visible or random) → turn-based battle
  (find and exploit weakness, manage MP/SP, break gauge) → XP / gold / items
  → level, equip, learn skills → story beat → next area
```
F2P variant: stamina-gated stages replace free exploration in part, and banners supply party members.

### Meta loops
- Story chapters and character side stories or bond events.
- Job/class systems and skill trees.
- Equipment upgrades, and in F2P, relic or gear sets with random substats.
- Optional superbosses, a post-game or New Game+.
- F2P: banners, rotating score-attack challenge modes, events.

### Session profile
Estimates. Premium: 20–60 minute sessions, with **suspend-anywhere** as a hard requirement. F2P: a 10–20 minute daily routine (stamina, dailies) plus story bursts on patch days. Classic JRPGs are often landscape. Portrait one-handed versions exist and widen the audience.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Weakness + break/toughness | combat | The single best way to give turn-based combat a readable decision every turn |
| Visible turn-order timeline | combat | Show the preview of how an action shifts the order. Strategy comes from it |
| Boost/resource banking | combat | Spend now or save: the core risk/reward tension |
| Job/class and skill trees | progression & upgrade; build-craft | Gives the long game build identity |
| Encounter-rate design | exploration & traversal | Visible encounters plus instant-win on weak enemies remove grind friction |
| Bond / affinity events | narrative & relationship | Character attachment drives F2P banner demand |
| Auto-battle, battle speed, repeat last commands | UX automation | Mandatory on mobile |
| Character banners (F2P) | collection & randomness | §0 applies in full |

### Monetization model and typical mix
Three models:
1. **Premium**: one up-front price, optional cosmetic DLC, no ads.
2. **Subscription platforms** (Apple Arcade, Netflix Games): a fee or revenue arrangement with the platform. Terms vary and are not public.
3. **F2P gacha**: as in §1, monthly card, banners and pass.

Premium JRPG is a small but steady long-tail niche on mobile. F2P turn-based gacha can reach the top-grossing charts with high production values. Do not mix models half-way: a premium game with heavy IAP gets review-bombed.

### KPI expectations
Premium: store-page conversion, rating, refunds and lifetime units. F2P: as in §1. Qualitative only, because no sourced genre ranges exist.

### Retention drivers
Chapter cliffhangers. New party members. Bond scenes. The soundtrack and world identity. Patch cadence in F2P. Mastery of the combat system.

### Content pipeline and production scope (estimates)
Content-heavy. A mid-size script can run past 100k words. Then come maps, battle animations per skill, enemy roster, music (a JRPG lives on its soundtrack) and localization. Rough scopes, all estimates:
- 2D pixel-art indie JRPG: 3–10 people, 2–4 years.
- F2P 3D turn-based title: 100+ people.
- Agent-friendly scope: one town, one 3-floor dungeon, one boss, 4 party members.

### Reference titles
- *Honkai: Star Rail* (HoYoverse, 2023): F2P turn-based benchmark.
- *Octopath Traveler: Champions of the Continent* (Square Enix, 2020 JP): Boost & Break.
- *Another Eden* (WFS, 2017 JP): premium-feeling F2P.
- *Pokémon Masters EX* (DeNA, 2019).
- *Chrono Trigger* (mobile port, 2011) and the *Final Fantasy Pixel Remaster* series (2021): premium ports.
- KEMCO's catalogue: a low-budget mobile JRPG niche.
- *Clair Obscur: Expedition 33* (Sandfall, 2025; PC/console): turn-based with real-time parry and dodge inputs.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Combat has one central, readable twist (break, boost, timeline) | Combat is "attack, attack, heal" and the grind gates story |
| Mobile UX: suspend-anywhere, auto-repeat, big targets | Menu-heavy UI with tiny fonts on a 6" screen |
| Strong character writing and a distinctive soundtrack | Generic plot and generic art, with no reason to choose it |
| Price and scope match (premium) | An expensive content treadmill against a low premium ceiling |
| F2P: story stays free | F2P puts story behind stamina or pay walls |

### Innovation vectors
- Timing inputs inside turn-based combat (parry, dodge, combo windows).
- Roguelite JRPG runs that make content reusable.
- Episodic release.
- Cross-platform saves.
- Portrait, one-thumb command design.
- AI-assisted *dialogue variants* under human editorial control. Never shipping unreviewed text, because of store and disclosure rules.

### Agent-buildability: 3/5
**Why mid:**
- The combat engine is ideal for agents: deterministic, data-driven, and a self-play bot can tune it.
- Menus and dialogue systems are testable.
- `pcg.py` maps and solver checks speed up dungeon layout.

**Why not higher:**
- Narrative quality needs human editorial.
- Battle animation and VFX per skill.
- Music identity is a taste checkpoint, and loop engineering is needed (see `ai-audio-pipeline`).
- Map and level art volume.

### Starter feature list (P0 vertical slice)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Conditional-turn battle engine (gameplay) | Deterministic. The timeline preview matches the actual order across 1,000 random battles |
| 2 | Weakness + break system (gameplay) | Hitting a weakness drains toughness. Break delays the turn and raises damage taken per contract parameters |
| 3 | Party of 4: basic attack, 3 skills, items (gameplay) | Every skill is data-driven. A unit test covers each targeting rule |
| 4 | Enemy AI with patterns and telegraphed big attacks (gameplay) | Big attacks are announced one turn ahead in the UI |
| 5 | Battle UI for phones (ui) | Touch targets at least 44 pt. Turn bar and numbers readable on a 5.5" screen. Passes structural UI checks |
| 6 | Exploration: 1 town + 3-floor dungeon with visible encounters (content) | `pcg.py` or hand layouts pass the reachability check. Encounters avoidable |
| 7 | Dialogue system: portraits, flags, branches, log, auto/skip (narrative) | Script is data (JSON, ink or Yarn). Branch coverage test reaches every node |
| 8 | XP and stat growth (meta) | Curve from `progression_calc.py`. Expected level at the boss within ±1 of target |
| 9 | Equipment + inventory (meta) | Equip and compare. Stat deltas correct |
| 10 | Save anywhere + suspend/resume (tech) | State survives an OS kill. Autosave on backgrounding |
| 11 | Auto-battle, 2×/3× speed, repeat last commands (ux) | Auto clears trash fights. Repeat reissues the previous command set |
| 12 | Two-phase boss (content) | A reasonable-policy bot at the expected level wins 40–70% (`difficulty_target`) |

## 5. Mobile MMORPG

### Definition and player fantasy
A persistent online world shared by many concurrent players. It has real-time combat (often auto-hunt and auto-quest), guild and territory warfare, open-world PvP and a player-driven economy (trading, auction house). The genre is led by Korean and Chinese titles (*Lineage M/W*, *Odin*, *Black Desert Mobile*). Western examples are sandbox-leaning (*Albion Online*, *Old School RuneScape*). The fantasy is *a life in a world with other people*: status, power, belonging, rivalry and wealth.

### Core loop
```
auto-hunt / quest → loot (gear, enhancement stones, currency) → enhance gear (success/fail)
  → power ↑ → stronger zones and bosses → guild and territory PvP → status, loot rights, taxes
```

### Meta loops
- Guild progression: sieges, castle ownership, world bosses with contribution-based loot.
- Open-world PvP with penalties (outlaw/"red name" systems).
- Crafting and life skills feeding the player economy.
- Auction house, trading and taxes as currency sinks.
- Class advancement, mounts, pets and collection codices that carry stat bonuses.
- Server lifecycle: new servers to reset competition, and merges when populations shrink.

### Session profile
Estimates. Korean-style auto-play keeps the client running for hours (auto-hunt), with active check-ins for bosses, sieges and trading. PC companion clients and emulators are common. Sandbox MMOs see 30–120 minute active sessions. Battery and heat matter: offer a low-power "screen dim" auto-hunt mode.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Auto-hunt / auto-quest | UX automation | Makes play compatible with mobile life. Needs server-side bot heuristics |
| Gear enhancement with fail/destroy risk | collection & randomness; progression & upgrade | Gambling-adjacent. Disclose rates and treat as a regulated random mechanic |
| Open-world PvP + penalties | social & competition | Creates stories and rivalry. Protect newcomers with safe zones and level bands |
| Guild sieges / territory control | social & competition | The main whale motivator. Schedule at fixed prime times per region |
| Auction house + transaction tax | economy & resources | The economy's main sink. Watch inflation and real-money-trading bots |
| World bosses with contribution loot | social & competition | Server-wide rendezvous moments |
| Stat-bearing collections (codex) | collection & randomness | A long-term sink. Easily becomes opaque pay-to-win |

### Monetization model and typical mix
The Asian model is IAP-heavy:
- VIP tiers.
- Gacha for stat-bearing appearances, cards, pets and mounts.
- Enhancement materials.
- Passes and "blessing" subscriptions.

Spending concentration is extreme, and the pay-to-win criticism is well known. Western sandbox titles use premium status or subscriptions, plus currency exchange between players. Ads are effectively absent. Stat-bearing random items are the riskiest monetization in this file. Apply §0.3 strictly.

### KPI expectations
Qualitative, because no sourced ranges were found. Install bases are smaller than casual, ARPPU is very high, launches spike on new servers, and server merges are a lagging churn signal. Critical mass matters: zones below a concurrency floor feel dead. Track CCU per shard, guild participation rate, and gold sources versus sinks per active player.

### Retention drivers
Guild bonds and obligations. Status and rankings. Territory ownership. Economic investment. Time already invested. Scheduled server-wide events. New-server resets.

### Content pipeline and production scope (estimates)
The largest scope on mobile alongside open-world action. It needs:
- **Backend**: sharded authoritative servers, persistence, anti-cheat, economy security.
- **Content**: zones, classes, bosses.
- **Operations**: game masters, customer service, community, localization.

Rough estimate: 100–500+ people over 3–5 years. Hosting is volatile: Unity Multiplay was deprecated and PlayFab's free tier shrank in 2026, so plan for self-hostable stacks (Nakama, Colyseus) or a stable third-party host (volatile facts). See `multiplayer-backend`.

### Reference titles
- *Lineage M* (NCSoft, 2017) and *Lineage W* (NCSoft, 2021): the Korean auto-play/siege model.
- *Black Desert Mobile* (Pearl Abyss, 2018 KR).
- *Odin: Valhalla Rising* (Kakao Games, 2021 KR).
- *MapleStory M* (Nexon, 2016 KR).
- *Ragnarok M: Eternal Love* (Gravity).
- *Albion Online* (Sandbox Interactive, 2017; cross-platform sandbox economy).
- *Old School RuneScape* mobile (Jagex, 2018): cross-platform parity.
- *Tarisland* (Tencent, 2024).

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Community and guild dynamics produce stories | Servers collapse at launch and the first impression is lost |
| Economy integrity: bot and real-money-trading control, healthy sinks | Bot farms inflate prices and legitimate players quit |
| Content and events arrive steadily | The world empties below critical mass |
| Cross-platform play keeps the world populated | Pay-to-win backlash, especially in Western markets |
| Responsive game masters and anti-cheat | Under-staffed operations |

### Innovation vectors
- Full PC/mobile parity and cross-progression.
- Sandbox player economies.
- Seasonal servers with fresh starts.
- "MMO-lite" social RPGs with shared hubs and instanced content.
- LLM agents as QA testers: TITAN reported 95% task completion on commercial MMORPGs (volatile facts).
- Carefully moderated AI NPCs.

Play-to-earn token economies largely collapsed after their 2021–22 peak. Treat them as a cautionary tale, not a vector.

### Agent-buildability: 1/5
**Why lowest:**
- Authoritative real-time servers, persistence, scaling, economy security and anti-cheat are operations problems beyond the plugin's verification gates.
- Content volume is enormous.
- Load tests need fleets of bot clients.
- Live operations need humans around the clock.

**Feasible scope:** a 50-CCU "MMO-lite" shard on Nakama or Colyseus, with bot clients for load tests and a deterministic combat core.

### Starter feature list (P0 vertical slice: 50-CCU shard)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Authoritative zone server (tech) | 50 bot clients for 30 min at the target tick rate with no tick overruns above the p99 budget |
| 2 | Auth, character creation, persistence (tech) | Reconnecting within 10 s restores position, inventory and buffs |
| 3 | Tap-to-move + auto-path + server movement validation (gameplay) | A speed-hack test client is corrected or rejected by the server |
| 4 | Auto-hunt toggle with stuck watchdog (gameplay) | Bot grinds 60 min with zero stuck states longer than 30 s |
| 5 | Combat: 4 skills, cooldowns, server-validated damage (gameplay) | A client-side damage tamper test is rejected |
| 6 | Loot + inventory with idempotent grants (tech) | Replaying a grant message never duplicates items |
| 7 | Gear enhancement with disclosed rates (monetization) | Rates shown before attempting. Outcomes logged to the ledger. No destruction in the slice |
| 8 | Party of 2–5 with shared XP (meta) | XP split per formula. Leaving or disconnecting is handled |
| 9 | Zone and guild chat with filter, report, block (ux) | Profanity filter. Report flow. Chat off by default for minors |
| 10 | Guild create/join + guild boss (meta) | Contribution tracking. Loot distributed per rule |
| 11 | Auction house with fixed-price listings and tax sink (meta) | Concurrent-buy race test produces no duplication or negative balances |
| 12 | Economy telemetry + anti-bot signals (analytics) | Gold sources and sinks per player per hour. Anomaly report flags scripted farming patterns |

## Cross-playbook decision table

| If the concept needs… | Prefer | Avoid |
|---|---|---|
| Fastest path to a verified, shippable slice | Idle RPG (§3) or auto-battle squad RPG (§1) | Open world (§2), MMORPG (§5) |
| Premium, no gacha | Turn-based JRPG (§4) | Stat-bearing random items anywhere |
| Revenue depth from character fandom | §1 or §4 F2P with strong art direction | Weak or inconsistent character art |
| Minors in the audience | Direct-purchase cosmetics, selectors, no paid random items | Banners without age gating (§0.3) |
| Real-time multiplayer | A shared-hub MMO-lite only after a single-player slice ships | Launching a persistent world as a first title |

## Volatile facts (as of Oct 2026 — verify before relying)

**Market**
- Global mobile game IAP revenue was about $40bn in H1 2026, down 2% YoY. Last War, Honor of Kings and Whiteout Survival led grossing in Q1 2026 — [Mobilegamer.biz (Sensor Tower)](https://mobilegamer.biz/data-digest-sensor-towers-h1-analysis-hay-days-comeback-julys-top-games-big-krafton-numbers-and-more/)
- Hybrid-casual had 2025's largest spending jump, +17.1% ($3.5B → $4.2B) — [Mobilegamer.biz](https://mobilegamer.biz/data-digest-sensor-towers-h1-analysis-hay-days-comeback-julys-top-games-big-krafton-numbers-and-more/)
- In mature markets (US, CA, KR, JP), IAP is 77–90% of game revenue. Mid-core took about 4% of game ad revenue (Feb–Apr 2026) — [Sensor Tower](https://sensortower.com/blog/gaming-deep-dive-ad-monetization-report); [GameDev Reports](https://gamedevreports.substack.com/p/sensor-tower-mobile-game-ad-monetization)

**Retention anchors**
- Across all genres, the median mobile game keeps about 22% at D1, under 4% at D7 and 0.7–0.8% at D30. The top 1% hold 64–68% D1 and 13–15% D30 — [Segwise (GameAnalytics)](https://segwise.ai/blog/mobile-gaming-app-user-retention-strategies); [Playio](https://blog.playio.co/d1-d7-d30-retention-benchmarks-2026)
- Mid-core D30 of about 10–12% is cited, but genre splits are inconsistent and some trace to 2022 data — [Segwise](https://segwise.ai/blog/mobile-gaming-app-user-retention-strategies); [AppAgent](https://appagent.com/blog/mobile-game-retention-benchmarks/)
- A D7/D1 ratio below 0.30 suggests a first-session problem (practitioner consensus) — [GameDev.net](https://gamedev.net/blogs/entry/2298160-the-d7d1-retention-ratio-for-mobile-games-a-complete-guide)

**Paid random items and minors**
- Belgium has banned paid loot boxes since 2018. Brazil's ECA Digital banned loot-box sales to under-18s from March 2026, and a court ordered Riot to pay damages in June 2026. Since Sep 22, 2024, Australia rates games with paid chance-based items at least M and simulated gambling R18+ — [Programming Insider](https://programminginsider.com/loot-boxes-regulation-and-where-the-line-sits-in-2026/); [Sheep Esports](https://www.sheepesports.com/articles/brazil-court-orders-riot-games-to-pay-eur2-5m-over-league-of-legends-loot-boxes/en); [PCWorld](https://www.pcworld.com/article/2464538/all-games-with-loot-boxes-will-be-rated-m-or-higher-in-australia.html)
- In January 2025, Genshin Impact's publisher (Cognosphere/HoYoverse) agreed to a $20M FTC settlement over COPPA and loot-box practices. Terms include blocking under-16s from in-game purchases without parental consent and disclosing odds — [PocketGamer.biz](https://www.pocketgamer.biz/hoyoverse-agrees-to-20-million-settlement-with-ftc-over-loot-boxes)
- Apple (guideline 3.1.1) and Google Play require odds disclosure for paid randomized items (background, long-standing) — [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
- China and South Korea also mandate probability disclosure (background; not re-verified this session, so check current rules before shipping there).
- The amended COPPA Rule's compliance deadline was Apr 22, 2026 — [Toy Association](https://toyassociation.org/PressRoom2/News/2026-News/updated-coppa-rule-requirements-take-effect-april-22.aspx)

**Production and tooling**
- No vendor automates Spine or Live2D rigging, and the only AI option is a non-commercial community skill. Meshy's API rigging is humanoid-only. No production AI VFX generator API exists — [GitHub spine-animation-ai](https://github.com/GenielabsOpenSource/spine-animation-ai); [Meshy rigging docs](https://docs.meshy.ai/en/api/rigging)
- Vision-language models playing real-time games from raw frames made under 1% progress — [arXiv 2505.18134](https://arxiv.org/html/2505.18134v3). The TITAN MMORPG QA agent reached 95% task completion — [arXiv 2509.22170](https://arxiv.org/abs/2509.22170)
- Unity deprecated Multiplay Game Server Hosting on Apr 1, 2026. PlayFab's Foundation Mode is free only up to 1,000 unique users — [Unity status](https://status.unity.com/info_notices/362941); [Microsoft Learn](https://learn.microsoft.com/en-za/xbox/playfab/pricing/development-mode)
- Google warns that frame rates often degrade after 45–50 minutes as devices heat up — [Android Developers](https://developer.android.com/games/optimize)

## Related skills
- `mechanics-codex`: mechanic cards for every category named above.
- `economy-design`: currency architecture, sinks and sources, gacha economy design.
- `progression-difficulty`: power curves, walls, DDA.
- `monetization`: banner cadence, monthly cards, passes, web shops, ethics.
- `legal-ethics`: loot-box law, COPPA, odds disclosure, consumer protection.
- `liveops`: banner and event calendars, version cadence.
- `multiplayer-backend`: arena snapshots, guild services, MMO shards.
- `narrative-design`: character arcs, bond events, JRPG scripts.
- `game-case-studies`: deconstructions of the reference titles.
- `player-psychology`: collection, sunk cost and ethical boundaries.
