# RPG, gacha, idle and card-game case studies

Fifteen deconstructions of games that sell characters, cards or collection progress, again and again, to the same players. They cover five families: gacha RPGs (Genshin Impact, Honkai: Star Rail, Raid: Shadow Legends, Summoners War, Fate/Grand Order, Puzzle & Dragons, Monster Strike, Arknights), idle RPGs (AFK Arena, Legend of Mushroom), collectible card games (Hearthstone, Marvel Snap, Pokémon TCG Pocket), a training sim (Uma Musume: Pretty Derby) and a location-based collector (Pokémon GO). One question connects them: how do you keep selling new content to people who already own a lot of it, while they still feel the game is fair and worth their time? The cases trace an arc. Early Japanese gacha (2012–2015) ran on low rates with no guarantees. Pity systems then became the norm and were standardised globally by the HoYoverse games, followed by time-respect features (auto-battle, auto-replay, skip), cosmetic-only upgrades (Marvel Snap) and finally the pack-opening ritual itself as the core loop (Pokémon TCG Pocket). Each case uses the 16-lens format from `SKILL.md` and ends with an ontology encoding in contract field names (`loops[].steps[]`, `economy.currencies[]`). Gacha rates and pity values are as publicly disclosed in-game or documented by player communities. They change between banners and versions, so treat every number as "verify in the current in-game disclosure". Revenue figures are omitted. Volatile facts are in section 17.

**Contents.** Sections 1–15 are case studies (index below). Section 16 is a cross-case synthesis covering gacha maths, pity design, stamina economies, what to sell, an ethics checklist and a design procedure. Section 17 lists volatile facts with sources.

| # | Game | Genre | Year | Key lesson |
|---|---|---|---|---|
| 1 | Genshin Impact | open-world action RPG, gacha | 2020 | Console-grade content plus a legible pity system plus a fixed version cadence |
| 2 | Honkai: Star Rail | turn-based RPG, gacha | 2023 | Turn-based combat suits phones; respecting time is a feature, not a cost |
| 3 | AFK Arena | idle RPG, hero collector | 2019 | Offline accrual plus premium art; shared levelling removes grind |
| 4 | Raid: Shadow Legends | turn-based hero collector | 2018–19 | Collection breadth gates and a huge gear sink; the cost of saturation UA |
| 5 | Summoners War | turn-based monster collector | 2014 | Rune substats create a near-infinite optimisation chase |
| 6 | Fate/Grand Order | story-led gacha RPG | 2015 | Narrative and IP sell characters; pity became non-negotiable |
| 7 | Puzzle & Dragons | puzzle RPG, gacha | 2012 | Free-drag orb combos merge skill with collection; friend helpers drive virality |
| 8 | Monster Strike | physics co-op RPG, gacha | 2013 | Local co-op on phones turns a game into a social activity |
| 9 | Pokémon GO | location-based collector | 2016 | Real-world movement as the core loop; community days as real appointments |
| 10 | Marvel Snap | collectible card game | 2022 | Six turns, twelve cards, a stakes bet, and cosmetic-only card upgrades |
| 11 | Hearthstone | collectible card game | 2014 | Digital-native rules and crafting as an anti-frustration valve |
| 12 | Uma Musume: Pretty Derby | training sim, gacha | 2021 (global 2025) | A roguelite training run with a support-card deck and inheritance |
| 13 | Arknights | tower defense, gacha | 2019 | Each character is a unique tower; auto-replay after a 3-star clear respects time |
| 14 | Pokémon TCG Pocket | collection-first card game | 2024 | The daily pack-opening ritual is the core loop |
| 15 | Legend of Mushroom (idle-RPG exemplar) | gear-draw idle RPG | 2023–24 | The loot-compare decision as a one-button core loop |

---

## 1. Genshin Impact

**Snapshot**
- Developer: miHoYo (Shanghai), which has published internationally under the HoYoverse brand since 2022.
- Release: September 2020 on PC, PlayStation 4, iOS and Android, with later releases on other consoles (verify platform dates).
- Genre: open-world action RPG with gacha character collection. Business model: free-to-play with IAP (gacha, monthly card, battle pass). No ads.
- Scale: widely reported as one of the highest-grossing mobile launches of its era (figures omitted).

**Core loop**
1. Explore the open world (climb, glide, swim) for chests, collectibles, puzzles and materials.
2. Fight with a party of four, switching characters so their elements combine into reactions (for example Vaporize, Melt, Freeze, Overloaded) that multiply damage or add control.
3. Spend Original Resin, a regenerating stamina, on domains, ley lines and bosses for upgrade materials, artifacts and weapon materials.
4. Level characters, talents and weapons. Farm artifacts, whose main stats and substats are random.
5. Earn Primogems from exploration, quests, events and the endgame, and "wish" on banners for new characters and weapons.
6. A new character opens new team compositions. Return to step 1 with harder content.

**Meta and progression**
- Adventure Rank and World Level raise enemy levels and drop quality as the account grows.
- Main story quests per region; new regions arrive over versions, each with distinct culture-inspired art, music and mechanics.
- Duplicates unlock Constellations (C1–C6) and weapon refinements (R1–R5), which sell extra power through copies.
- Endgame combat modes reset on a fixed schedule (verify current modes and reset cadence).

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Genesis Crystals | premium | IAP | convert to Primogems, cosmetics |
| Primogems | hard | exploration, quests, events, endgame, login, monthly card | Fates (160 per pull), resin refills |
| Fates (wish tickets) | material | Primogems, battle pass, shop | banner pulls |
| Mora | soft | almost everything | levels, talents, weapons, artifacts |
| Original Resin | energy | regeneration of 1 per 8 minutes (verify cap) | domains, bosses, ley lines |
| Starglitter, Stardust | material | duplicates and pulls | exchange shop (Fates, older items) |
| Battle pass XP | xp | dailies, weeklies | pass tiers |

**Monetization**
- Character and weapon banners with a disclosed pity system:
  - Character event wishes: 5-star base rate 0.6%, guaranteed within 90 pulls. Community data shows the rate rising steeply from about the 74th pull ("soft pity").
  - Each 5-star has a 50% chance to be the featured character. Losing makes the next 5-star the featured one. A later update added a mechanism that reduces repeated losses (verify mechanics).
  - The weapon banner has its own rates, an 80-pull guarantee and a target-selection mechanism (verify).
- A 30-day monthly card (daily Primogems), a battle pass, first-purchase double crystals and bundles.
- **Worked example.** Using the community soft-pity model, about 62 pulls per 5-star on average and about 93 per guaranteed featured character, with a worst case of 180 pulls (28,800 Primogems at 160 per pull). Reproduce: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gacha_calc.py --rate 0.006 --soft-pity-start 74 --soft-pity-step 0.06 --hard-pity 90 --rate-up 0.5 --guarantee --pulls 180 --json`.

**Live-ops**
- Versions on a roughly six-week cadence, each with two banner phases, a flagship event and story or region content, previewed in a livestream with redeemable codes. Reruns of limited characters, anniversaries and collaborations.

**Retention hooks**
- Daily commissions and resin (a cap sized so one daily check-in wastes little), the banner calendar and leaks, new story chapters, and endgame resets.

**Social layer**
- Up to four-player co-op for exploration, domains and bosses, but the game is mostly single-player. The real social layer is outside the game: theorycrafting, fan art, guides and a very large creator ecosystem.

**UX and onboarding notables**
- A companion character (Paimon) narrates the onboarding. Stamina-limited climbing and gliding teach exploration.
- Wish animations cue rarity early by colour (blue, purple, gold), managing anticipation.
- Cross-progression between PC and mobile; console linking arrived later (verify).

**Art and audio identity**: anime cel-shaded characters with high-end lighting, regional music recorded with major orchestras (widely reported), and full voice acting in several languages.

**Psychology principles used**
- Variable-ratio reinforcement on wishes, with pity converting the tail into a visible goal-gradient.
- Scarcity and FOMO from limited banners.
- Collection and endowment: characters as an owned cast.
- Curiosity: exploration and the next region.
- Ethical line: limited-time pressure, opaque soft pity and spending by minors.

**Innovations**
- Console-quality open-world content as the vehicle for a gacha, launched globally and simultaneously across platforms.
- The elemental-reaction system sells characters through synergy demand ("my team needs a Hydro unit"), not just raw power.
- Made pity and the 50/50 guarantee widely understood by a global audience.

**Weaknesses and criticism**
- Low 5-star rates, Constellations that sell power through duplicates, and artifact RNG grind gated by resin. An endgame thin relative to exploration; comparisons with The Legend of Zelda: Breath of the Wild at reveal.
- Ethical criticism of gacha pressure on young players.

**Lessons for designers**
1. Publish the pity rules. Players accept low rates when the worst case is known.
2. The release cadence is the business: plan a fixed version rhythm with two banner windows.
3. Design team synergy (reactions) so new characters create demand without having to be strictly stronger.
4. Size the stamina cap so a once-a-day player loses little (section 16.4).

**Analogy hooks**
- Elemental reactions → combo systems in party games, card games and roguelites.
- Version livestreams with codes → reveal rituals for any live game.
- Resin-gated material farming → crafting and gear grinds in RPGs and sims.

**Ontology encoding**
```json
{"loops": [
  {"id": "gi_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "explore_open_world", "reward": "chests_materials_primogems", "next": "c2"},
    {"id": "c2", "action": "fight_with_party_trigger_reactions", "reward": "kills_drops", "next": "c3"},
    {"id": "c3", "action": "spend_resin_on_domains_bosses", "reward": "upgrade_materials_artifacts", "next": "c4"},
    {"id": "c4", "action": "level_characters_weapons_artifacts", "reward": "account_power", "next": "c1"}]},
  {"id": "gi_gacha", "type": "monetization", "period": "weekly", "steps": [
    {"id": "g1", "action": "accumulate_primogems_toward_pity", "reward": "pull_budget", "next": "g2"},
    {"id": "g2", "action": "wish_on_limited_banner", "reward": "character_or_weapon", "next": "g3"},
    {"id": "g3", "action": "build_new_team_composition", "reward": "new_play_options", "next": "g1"}]},
  {"id": "gi_version", "type": "liveops", "period": "season", "steps": [
    {"id": "v1", "action": "watch_version_reveal_redeem_codes", "reward": "primogems_anticipation", "next": "v2"},
    {"id": "v2", "action": "play_flagship_event_and_story", "reward": "primogems_event_weapon", "next": "v1"}]}],
 "economy": {"currencies": [
  {"id": "genesis_crystals", "kind": "premium", "sources": ["iap"], "sinks": ["primogem_conversion", "cosmetics"], "cap": null},
  {"id": "primogems", "kind": "hard", "sources": ["exploration", "quests", "events", "monthly_card"], "sinks": ["fates", "resin_refills"], "cap": null},
  {"id": "fates", "kind": "material", "sources": ["primogems", "battle_pass", "shop"], "sinks": ["banner_pulls"], "cap": null},
  {"id": "mora", "kind": "soft", "sources": ["domains", "exploration", "quests"], "sinks": ["levels", "talents", "artifacts"], "cap": null},
  {"id": "original_resin", "kind": "energy", "sources": ["regeneration_1_per_8_min"], "sinks": ["domains", "bosses", "ley_lines"], "cap": null, "note": "cap disclosed in-game; verify current value"},
  {"id": "starglitter", "kind": "material", "sources": ["duplicates"], "sinks": ["exchange_shop"], "cap": null}]}}
```

## 2. Honkai: Star Rail

**Snapshot**
- Developer: HoYoverse (miHoYo).
- Release: April 2023 on PC, iOS and Android, with console releases later (verify).
- Genre: turn-based sci-fi RPG with gacha. Business model: free-to-play with IAP (gacha, monthly card, battle pass). No ads.
- Scale: one of the largest gacha launches of 2023 by widely reported rankings (figures omitted).

**Core loop**
1. Explore a map and hit an enemy in the overworld (or use a character's Technique) to start a battle with an advantage.
2. Fight turn-based battles with a party of four. Turn order follows each unit's Speed and is shown on a timeline.
3. Basic attacks generate shared Skill Points (a team pool with a small cap), and Skills spend them, so the team shares one tactical budget.
4. Hit enemy elemental weaknesses to deplete their Toughness bar and trigger a Weakness Break (damage and turn delay).
5. Fire Ultimates when charged, even outside the normal turn order.
6. Win materials and relics. Spend Trailblaze Power (stamina) on farming stages, then pull on Warps for characters and Light Cones (equipment).

**Meta and progression**
- Account level and an equilibrium level that scales enemies and rewards.
- Character traces (skill trees), Eidolons from duplicates, Light Cone superimposition from duplicates, and relic sets with random substats.
- A roguelite mode (Simulated Universe) with run-based blessings, plus rotating endgame challenge modes (verify current set).

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Oneiric Shards | premium | IAP | convert to Stellar Jade, cosmetics |
| Stellar Jade | hard | exploration, quests, events, endgame, monthly card | passes (160 per pull), refills |
| Star Rail passes | material | Stellar Jade, battle pass, shop | Warp pulls |
| Credits | soft | most activities | levels, traces, relics |
| Trailblaze Power | energy | regeneration (verify rate and cap), fuel items | farming stages |
| Relics and upgrade materials | material | farming stages | character power |

**Monetization**
- Character and Light Cone banners with Genshin-style pity: a 0.6% 5-star base rate and a 90-pull guarantee on character banners, with a 50/50 on the featured character and a guarantee after a loss. Light Cone banners have their own terms (verify).
- A discounted starter banner for new players with a guaranteed 5-star within its first 50 pulls (verify).
- Monthly card, battle pass and bundles.

**Live-ops**: versions on a roughly six-week cadence with two banner phases, new story arcs and areas, events and endgame rotations.

**Retention hooks**
- Daily training targets that take a few minutes, idle assignments (dispatches), stamina with overflow storage, endgame resets and story.

**Social layer**
- Light: friends can lend support characters, plus messages and community content. Combat is single-player.

**UX and onboarding notables**
- Auto-battle and double speed are available early and remembered between fights. Respect for the player's time is a stated pillar, and later versions added further farming conveniences (verify).
- Turn-based combat survives interruptions, so the game suits short and broken mobile sessions.
- The turn-order timeline, weakness icons and Toughness bars make every decision readable.

**Art and audio identity**: anime sci-fi with high-production cutscenes, a humorous tone (recurring visual gags), an eclectic soundtrack and full voice acting.

**Psychology principles used**
- Competence: planning turn order and the shared skill-point budget.
- Collection and endowment; FOMO from limited banners.
- Humour as relief from grind. Burnout avoidance through time-respect features.

**Innovations**
- Modern, high-production turn-based gacha combat with interrupting Ultimates and a team-shared skill-point economy.
- Positioned time-respect features (auto, speed, short dailies) as a selling point.
- A roguelite mode that reuses the roster for replayable endgame.

**Weaknesses and criticism**
- Fast power creep: new limited characters can make endgame modes feel built for the latest releases.
- Relic RNG grind, and criticism of story verbosity and pacing.
- Low difficulty in story content, with challenge concentrated in endgame modes.

**Lessons for designers**
1. Turn-based combat is a natural fit for interruptible phone sessions.
2. A shared team resource (skill points) creates party-level decisions rather than four independent rotations.
3. Respecting time (auto, speed-up, short dailies) supports long-term retention. Its success here is consistent with that, though causality is inferred (grade D).
4. A roguelite mode extends the value of an owned roster.

**Analogy hooks**
- Shared skill points → deckbuilders (shared energy), co-op tactics games.
- Toughness break → stagger systems in action games, shield-break puzzles.
- Out-of-turn ultimates → reaction cards and interrupt mechanics.

**Ontology encoding**
```json
{"loops": [
  {"id": "hsr_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "strike_enemy_in_overworld", "reward": "battle_advantage", "next": "c2"},
    {"id": "c2", "action": "manage_shared_skill_points_and_turn_order", "reward": "weakness_breaks", "next": "c3"},
    {"id": "c3", "action": "cast_ultimates_and_win", "reward": "materials_relics", "next": "c4"},
    {"id": "c4", "action": "spend_trailblaze_power_and_upgrade", "reward": "account_power", "next": "c1"}]},
  {"id": "hsr_daily", "type": "meta", "period": "daily", "steps": [
    {"id": "d1", "action": "complete_daily_training", "reward": "stellar_jade", "next": "d2"},
    {"id": "d2", "action": "collect_assignments_spend_stamina", "reward": "materials", "next": "d1"}]}],
 "economy": {"currencies": [
  {"id": "oneiric_shards", "kind": "premium", "sources": ["iap"], "sinks": ["stellar_jade_conversion"], "cap": null},
  {"id": "stellar_jade", "kind": "hard", "sources": ["exploration", "events", "monthly_card"], "sinks": ["star_rail_passes"], "cap": null},
  {"id": "star_rail_pass", "kind": "material", "sources": ["stellar_jade", "battle_pass"], "sinks": ["warp_pulls"], "cap": null},
  {"id": "credits", "kind": "soft", "sources": ["battles", "quests"], "sinks": ["levels", "traces"], "cap": null},
  {"id": "trailblaze_power", "kind": "energy", "sources": ["regeneration", "fuel"], "sinks": ["farming_stages"], "cap": null}]}}
```

## 3. AFK Arena

**Snapshot**
- Developer and publisher: Lilith Games (Shanghai).
- Release: 2019 globally. A sequel, AFK Journey, followed in 2024.
- Genre: idle RPG with hero collection. Business model: free-to-play with IAP (VIP, monthly cards, bundles, summons).
- Scale: one of the defining idle RPGs in Western markets (rankings only; figures omitted).

**Core loop**
1. Arrange five heroes in a front and back row and auto-battle a campaign stage. The player may trigger Ultimates manually.
2. Each cleared stage raises the idle reward rate (gold, hero experience, essence, gear).
3. Rewards accumulate while offline up to a cap (verify the cap).
4. Collect idle rewards and "Fast Rewards" (a number free per day, more for diamonds).
5. Level heroes, ascend them by merging copies into higher tiers, and equip gear.
6. Hit a wall, then wait for accrual or progress other modes (a tower climb, a roguelite labyrinth, puzzle-exploration maps), and return to step 1.

**Meta and progression**
- Ascension tiers that consume duplicate and "fodder" copies.
- A shared-level system (the Resonating Crystal) sets other heroes' levels from the top five, so players stop levelling every hero by hand.
- Factions with an advantage wheel plus two rare factions.
- Many side modes: tower, labyrinth, exploration puzzles, dispatch board, guild bosses, arena.

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Gold | soft | idle rewards, stages, modes | levels, gear |
| Diamonds | hard | IAP, events, modes, achievements | summons, fast rewards, shops |
| Hero experience and essence | material | idle rewards | levels, resets |
| Summon scrolls | material | diamonds, events, shops | hero summons |
| Mode tokens (labyrinth, guild) | soft | specific modes | mode shops |

**Monetization**
- VIP levels raised by spending (with convenience perks), monthly cards, growth funds and limited bundles.
- Hero summons with disclosed odds. A wishlist feature lets players narrow which heroes they can pull (verify mechanics).

**Live-ops**: new heroes, limited events, themed modes and periodic structural updates (verify cadence).

**Retention hooks**
- The idle cap: return before it fills. Daily quests, dispatch timers, weekly mode resets and guild bosses.

**Social layer**
- Guilds with shared bosses, arena PvP, friends lending heroes for some content (verify).

**UX and onboarding notables**
- Designed for sessions of a few minutes: collect, upgrade, push a stage, leave.
- A "welcome back" summary of offline gains turns absence into a reward rather than a loss.
- Drag-and-drop formation and auto-battle keep input minimal.

**Art and audio identity**: hand-painted, storybook fantasy illustration widely praised for its quality, with clear hero silhouettes and faction colours.

**Psychology principles used**
- Gifts on return (endowed progress): idle accrual.
- Goal-gradient: stage numbers.
- Collection: heroes and factions.
- Low effort, low guilt: progress happens while away.

**Innovations**
- Brought premium-looking art and multiple side modes (roguelite, puzzle exploration) to the idle RPG, widening its audience.
- Shared levelling removed one of the genre's worst grinds.

**Weaknesses and criticism**
- Long walls in later chapters, heavy duplicate requirements for ascension, and pay-to-progress pressure through VIP.
- Feature bloat over time makes the game harder to learn for new players.

**Lessons for designers**
1. Offline accrual with a cap creates a gentle appointment. Present returning as a gift.
2. Remove grinds that add no decisions (shared levelling).
3. Give idle players occasional active, skill-based modes to break the waiting.
4. Watch duplicate requirements: they turn collection into fodder management.

**Analogy hooks**
- Idle accrual with a cap → farming sims, base-builders, any game with a "welcome back" screen.
- Shared level for a roster → team-based games with many characters.
- Faction advantage wheel → rock-paper-scissors in any roster game.

**Ontology encoding**
```json
{"loops": [
  {"id": "afk_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "arrange_formation_auto_battle_stage", "reward": "stage_clear", "next": "c2"},
    {"id": "c2", "action": "raise_idle_reward_rate", "reward": "higher_accrual", "next": "c3"},
    {"id": "c3", "action": "level_and_ascend_heroes", "reward": "team_power", "next": "c1"}]},
  {"id": "afk_idle", "type": "meta", "period": "daily", "steps": [
    {"id": "i1", "action": "return_and_collect_idle_rewards", "reward": "gold_xp_gear", "next": "i2"},
    {"id": "i2", "action": "use_fast_rewards_and_side_modes", "reward": "materials", "next": "i1"}]}],
 "economy": {"currencies": [
  {"id": "gold", "kind": "soft", "sources": ["idle_rewards", "stages"], "sinks": ["levels", "gear"], "cap": null},
  {"id": "diamonds", "kind": "hard", "sources": ["iap", "events", "modes"], "sinks": ["summons", "fast_rewards", "shops"], "cap": null},
  {"id": "hero_xp", "kind": "material", "sources": ["idle_rewards"], "sinks": ["levels"], "cap": null},
  {"id": "summon_scrolls", "kind": "material", "sources": ["diamonds", "events"], "sinks": ["summons"], "cap": null}]}}
```

## 4. Raid: Shadow Legends

**Snapshot**
- Developer and publisher: Plarium (Israel), owned by Aristocrat Leisure since 2017 (widely reported).
- Release: soft launch in 2018, wide release in 2019 (verify dates).
- Genre: turn-based hero collector RPG. Business model: free-to-play with IAP.
- Scale: a long-running grossing title (figures omitted). Known for one of the most visible influencer sponsorship campaigns in games around 2019–2021.

**Core loop**
1. Build a team of champions and battle campaign stages and dungeons, manually or on auto. A turn meter driven by Speed decides who acts.
2. Farm stages for experience to level champions, including low-rarity "food" champions.
3. Rank champions up by consuming champions of the same rank.
4. Farm dungeons for gear sets and enhance gear with silver.
5. Open shards to summon new champions.
6. Take the team into harder content (clan boss, dungeons, faction-based crypts, arena PvP, a tower), then return to step 1.

**Meta and progression**
- Rarities from Common to Legendary, with a rarer tier added later (verify). Six-star ranks, ascension, masteries and skill books.
- Faction-specific content that requires champions from each of many factions: collection breadth becomes a gate.
- A daily clan boss with limited keys as a team ritual.

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Silver | soft | battles, selling gear | gear enhancement, ranks, masteries |
| Gems | hard | IAP, quests, events | energy refills, shops, gear slots |
| Energy | energy | regeneration, refills | campaign and dungeons |
| Shards (several tiers) | material | events, quests, packs | champion summons |
| Skill books and potions | material | dungeons, events | skills, ascension |

**Monetization**
- Very large catalogue of packs with "value" framing, summon events (boosted rates) and tournaments that reward heavy summoning.
- Published shard rates (for example, a low single-digit or sub-1% chance of the top rarity from standard shards; verify per shard type). A "mercy" system that raises rates after long dry streaks was documented by players and later acknowledged by the developer (verify).
- Time-limited "fusion" events that combine champions earned from events, often with spending pressure.

**Live-ops**: a dense calendar of summon events, tournaments, fusions, new champions and game modes.

**Retention hooks**
- Energy, the daily clan-boss keys, event chains and a gear-optimisation chase.

**Social layer**
- Clans with a shared boss, clan quests and clan-vs-clan events; arena PvP.

**UX and onboarding notables**
- Auto-battle and multi-battle repeat for farming.
- A guided early game with generous starter champions. The UI becomes very dense in late game.

**Art and audio identity**: highly detailed, near-realistic 3D dark-fantasy champion models, unusual for mobile collectors at launch, with cinematic skill animations.

**Psychology principles used**
- Variable reward: shards.
- Collection pressure: faction gates.
- Sunk cost and endowment: gear and ranked champions.
- Competition: tournament leaderboards that reward spending.

**Innovations**
- Console-like 3D champion models in a mobile collector.
- A massive gear and silver sink that sustains a long optimisation chase.
- Saturation-level influencer marketing at a scale that became a meme.

**Weaknesses and criticism**
- Widely criticised as aggressively monetized: tournaments around summoning, fusions under time pressure, and pack pricing.
- Marketing saturation led to audience fatigue and parody.
- Pay-to-win perception in PvP, and loot-box regulatory exposure.

**Lessons for designers**
1. Collection-breadth gates (one champion per faction) create demand for the whole roster. Make them achievable without paying.
2. A soft currency sink on gear (silver) can carry a mid- and late-game economy.
3. Marketing saturation is not free: memes cut both ways for brand trust.
4. Do not reward spending directly in competitive events. It reads as pay-to-win.

**Analogy hooks**
- Faction-gated content → any collection game needing roster breadth (sticker albums, card sets).
- Champions as level-up fodder → crafting by consumption in merge or card games.
- Daily clan-boss keys → team rituals in puzzle and idle games.

**Ontology encoding**
```json
{"loops": [
  {"id": "raid_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "battle_stage_or_dungeon_on_auto", "reward": "xp_gear_silver", "next": "c2"},
    {"id": "c2", "action": "rank_up_by_feeding_food_champions", "reward": "higher_rank_champion", "next": "c3"},
    {"id": "c3", "action": "enhance_gear_with_silver", "reward": "team_power", "next": "c1"}]},
  {"id": "raid_gacha", "type": "monetization", "period": "weekly", "steps": [
    {"id": "g1", "action": "join_summon_event_or_tournament", "reward": "boosted_rates_points", "next": "g2"},
    {"id": "g2", "action": "open_shards", "reward": "champions", "next": "g1"}]},
  {"id": "raid_clan", "type": "social", "period": "daily", "steps": [
    {"id": "s1", "action": "spend_clan_boss_keys", "reward": "clan_boss_chests", "next": "s1"}]}],
 "economy": {"currencies": [
  {"id": "silver", "kind": "soft", "sources": ["battles", "gear_sales"], "sinks": ["gear_enhancement", "masteries"], "cap": null},
  {"id": "gems", "kind": "hard", "sources": ["iap", "quests"], "sinks": ["energy_refills", "shops"], "cap": null},
  {"id": "energy", "kind": "energy", "sources": ["regeneration", "refills"], "sinks": ["campaign", "dungeons"], "cap": null},
  {"id": "shards", "kind": "material", "sources": ["events", "quests", "packs"], "sinks": ["summons"], "cap": null}]}}
```

## 5. Summoners War: Sky Arena

**Snapshot**
- Developer and publisher: Com2uS (South Korea).
- Release: June 2014.
- Genre: turn-based monster-collection RPG. Business model: free-to-play with IAP.
- Scale: one of the most successful Korean mobile RPGs globally (rankings only; figures omitted). It runs a world championship esports event (verify history).

**Core loop**
1. Build a team of monsters across five elements (Fire, Water and Wind in a triangle; Light and Dark strong against each other).
2. Fight turn-based battles where an attack bar driven by Speed decides turns. Skills have cooldowns and leaders give team bonuses.
3. Farm dungeons for runes.
4. Equip runes in six slots: set bonuses, a main stat and random substats that grow as the rune is upgraded.
5. Evolve monsters to higher star grades by feeding monsters of the same grade, and awaken them with elemental essences.
6. Test the team in arena (attacking AI-controlled defences of other players), guild content and real-time draft PvP, then return to step 3.

**Meta and progression**
- Monster star grades up to 6, awakening and second awakenings, and skill-ups from duplicate or special materials.
- Runes as the main endgame. A strong rune set is valued more than any single monster.
- Each monster family exists in all five elements with different skills, multiplying the roster from one model.

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Mana | soft | battles, buildings | rune upgrades, evolutions, shop |
| Crystals | hard | IAP, achievements, events | energy refills, arena wings, shop |
| Energy | energy | regeneration, refills | dungeons and scenarios |
| Summoning scrolls (several types) | material | dungeons, events, packs | monster summons |
| Runes | material | dungeons | monster power |
| Essences | material | elemental dungeons | awakening |

**Monetization**
- Summon packs and scrolls, crystal packs (used heavily for energy refills to farm runes), monthly and event packs.
- Scroll rates are published; the chance of a natural 5-star from the standard premium scroll is very low (about 0.5%, verify).

**Live-ops**: events, new monsters and second awakenings, balance patches, guild and arena seasons, esports.

**Retention hooks**
- Energy, the rune optimisation chase, arena attack regeneration and guild war schedules.

**Social layer**
- Guilds, guild wars and multi-guild siege battles, plus real-time PvP with picks and bans.

**UX and onboarding notables**
- Repeat battles and auto-play for farming. The rune management interface is dense but deep.
- Elemental advantage is colour-coded for readability.

**Art and audio identity**: colourful fantasy monsters whose elemental variants share silhouettes with different palettes.

**Psychology principles used**
- Double variable reward: summons and rune substats.
- Optimisation and competence: rune theorycrafting.
- Status: arena rank and rare monsters. Collection: elemental variants.

**Innovations**
- The rune system: a near-infinite optimisation chase that keeps late-game players farming long after the roster is complete.
- Elemental variants as a cheap content multiplier.
- Draft-based real-time PvP in a gacha RPG, supporting esports.

**Weaknesses and criticism**
- Double RNG (summons and rune rolls) can feel punishing.
- Fodder grind for evolution and repetitive farming.
- Power concentrated in a few rare monsters; an ageing UI.

**Lessons for designers**
1. Random gear substats create a long chase, but give players ways to reroll or target them.
2. Elemental variants of one model multiply the roster cheaply.
3. A draft (picks and bans) makes PvP in a collector depend on knowledge as well as collection.

**Analogy hooks**
- Rune substats → loot systems in ARPGs, idle games, roguelites.
- Elemental variants → skins with mechanics, card variants.
- Draft PvP → card battlers and autobattlers.

**Ontology encoding**
```json
{"loops": [
  {"id": "sw_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "farm_rune_dungeon", "reward": "runes_mana", "next": "c2"},
    {"id": "c2", "action": "upgrade_and_equip_runes", "reward": "monster_power", "next": "c3"},
    {"id": "c3", "action": "evolve_and_awaken_monsters", "reward": "higher_grade_monster", "next": "c4"},
    {"id": "c4", "action": "fight_arena_or_guild_battles", "reward": "glory_points_rank", "next": "c1"}]}],
 "economy": {"currencies": [
  {"id": "mana", "kind": "soft", "sources": ["battles", "buildings"], "sinks": ["rune_upgrades", "evolutions"], "cap": null},
  {"id": "crystals", "kind": "hard", "sources": ["iap", "achievements", "events"], "sinks": ["energy_refills", "shop"], "cap": null},
  {"id": "energy", "kind": "energy", "sources": ["regeneration", "refills"], "sinks": ["dungeons"], "cap": null},
  {"id": "scrolls", "kind": "material", "sources": ["dungeons", "events", "packs"], "sinks": ["summons"], "cap": null},
  {"id": "runes", "kind": "material", "sources": ["dungeons"], "sinks": ["monster_power"], "cap": null}]}}
```

## 6. Fate/Grand Order

**Snapshot**
- Developer: Delightworks; development later moved to Lasengle, an Aniplex company (verify the 2021 transition). Publisher: Aniplex.
- Release: July 2015 in Japan, 2017 in English (North America), with other regional versions.
- Genre: story-led turn-based RPG with gacha, based on Type-Moon's Fate franchise (which began with the 2004 visual novel Fate/stay night). Business model: free-to-play with IAP.
- Scale: one of Japan's highest-grossing mobile games for years (widely reported; figures omitted).

**Core loop**
1. Form a party: three front-line and three reserve servants plus one support servant borrowed from a friend, each with an equipped Craft Essence (an equipment card).
2. Each turn, five command cards are dealt from the front-line servants' decks: Buster (damage), Arts (charge) and Quick (critical stars). Pick three.
3. Chain cards: three cards from one servant add an extra attack, and three of one colour add a chain bonus.
4. Charge each servant's Noble Phantasm gauge and fire its cinematic ultimate.
5. Clear the waves for materials, QP (soft currency) and bond points.
6. Spend AP (stamina) on further quests and Saint Quartz on summons, then return to step 1.

**Meta and progression**
- Ascension in four stages (materials), skill levels, and Noble Phantasm levels raised by duplicates.
- Bond levels with each servant unlock profile and story text plus a unique Craft Essence at the top bond level.
- A long main story in chapters and arcs, and frequent limited events with farmable currencies and event Craft Essences.

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Saint Quartz | hard | IAP, story clears, login, events | summons, AP refills, continues |
| AP | energy | regeneration (verify rate), apples | quests |
| QP | soft | quests, events | skill levels, ascension |
| Friend points | soft | lending and borrowing supports | friend summons |
| Ascension and skill materials | material | quests, events, shops | servant growth |
| Event currencies | event | event quests | event shops |

**Monetization**
- Servant summons with low rates: about 1% for any 5-star and roughly 0.7–0.8% for a featured one (verify per banner).
- For years there was no pity. The Japanese version later added a guarantee of the featured 5-star within 330 summons on a banner (2021; verify, including whether other regions followed).
- Paid "lucky bags" guaranteeing a 5-star from a pool at anniversaries and New Year, and banners timed with story chapters, so narrative moments drive demand.

**Live-ops**
- An event roughly every couple of weeks, story chapter releases, anniversary campaigns and collaborations.
- The English version runs on a delay of roughly two years behind Japan, so players can plan with knowledge of future banners (verify current gap).

**Retention hooks**
- Daily login Saint Quartz, AP regeneration, events, story cliffhangers and bond levels.

**Social layer**
- The support system: borrowing friends' servants is central to clearing hard content and earns both players friend points.
- A strong fandom with real-world events, cafés and cross-media.

**UX and onboarding notables**
- Card selection is fast and readable. Long Noble Phantasm animations and an older UI were long-standing complaints, partly addressed over time (verify).
- The story is text-heavy, a deliberate choice for its audience.

**Art and audio identity**: each servant is illustrated by a different well-known artist, voiced by popular voice actors and written into a large shared narrative. The art is itself the product.

**Psychology principles used**
- Character attachment (parasocial bonds) and collection.
- The Zeigarnik effect in story cliffhangers.
- FOMO from limited servants and rare reruns. Reciprocity in support lending.
- Ethical line: low rates without pity for years drove reports of extreme spending.

**Innovations**
- A story- and IP-led gacha where narrative beats sell characters, and each character's artist is part of the appeal.
- Support borrowing as a core mechanic that keeps every player's collection useful to others.
- Regional servers deliberately trailing the original, giving later regions a predictable future.

**Weaknesses and criticism**
- Low rates and the long absence of pity; grind for materials.
- A dated interface and long animations.
- Power concentrated in a few support servants.

**Lessons for designers**
1. Narrative plus a beloved IP can sell characters on emotional value rather than power.
2. Borrowing friends' units gives collections social value and helps players without the meta characters.
3. Pity is now table stakes. A long tail without a guarantee damages trust.

**Analogy hooks**
- Card dealing from units' decks → deckbuilders where each character contributes cards.
- Bond levels unlocking story → dating sims, companion systems, pet games.
- Friend support lending → co-op puzzle helpers, racing ghosts.

**Ontology encoding**
```json
{"loops": [
  {"id": "fgo_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "pick_three_of_five_command_cards", "reward": "chains_and_np_charge", "next": "c2"},
    {"id": "c2", "action": "fire_noble_phantasm", "reward": "wave_clear", "next": "c3"},
    {"id": "c3", "action": "clear_quest_with_friend_support", "reward": "materials_qp_bond_friend_points", "next": "c1"}]},
  {"id": "fgo_story", "type": "liveops", "period": "weekly", "steps": [
    {"id": "s1", "action": "read_story_chapter_or_event", "reward": "saint_quartz_event_currency", "next": "s2"},
    {"id": "s2", "action": "summon_on_story_timed_banner", "reward": "servant", "next": "s1"}]}],
 "economy": {"currencies": [
  {"id": "saint_quartz", "kind": "hard", "sources": ["iap", "story", "login"], "sinks": ["summons", "ap_refills"], "cap": null},
  {"id": "ap", "kind": "energy", "sources": ["regeneration", "apples"], "sinks": ["quests"], "cap": null},
  {"id": "qp", "kind": "soft", "sources": ["quests", "events"], "sinks": ["skills", "ascension"], "cap": null},
  {"id": "friend_points", "kind": "soft", "sources": ["support_lending"], "sinks": ["friend_summons"], "cap": null},
  {"id": "event_currency", "kind": "event", "sources": ["event_quests"], "sinks": ["event_shop"], "cap": null}]}}
```

## 7. Puzzle & Dragons

**Snapshot**
- Developer and publisher: GungHo Online Entertainment (Japan).
- Release: February 2012 in Japan, with later Western releases.
- Genre: puzzle RPG with monster collection and gacha. Business model: free-to-play with IAP.
- Scale: one of the defining hits of Japan's early smartphone era (widely reported; figures omitted).

**Core loop**
1. Form a team of five monsters plus a helper monster borrowed from a friend or stranger, whose leader skill also applies.
2. On each dungeon floor, pick up one orb on a 6×5 board and drag it freely for a few seconds. Every orb it passes swaps places with it.
3. Release: lines of three or more same-coloured orbs clear, and falling orbs can cascade into further combos.
4. Monsters attack in the colours that were cleared. More combos multiply damage, and heart orbs heal.
5. Leader skills (yours and the helper's) multiply damage under conditions, which is the main team-building puzzle.
6. Clear the floors and the boss for monster eggs, coins and experience. Spend Magic Stones on summons, stamina or a continue after defeat.

**Meta and progression**
- Feeding monsters to level them, evolving with materials, skill-ups from duplicates, and later layers (awakenings, inherited assists).
- Player rank raises stamina and team cost limits.
- A huge and growing monster catalogue, much of it from collaborations.

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Magic Stones | hard | IAP, events, first clears, login | summons, continues, stamina refills, box space |
| Coins | soft | dungeons, selling monsters | feeding, evolutions |
| Stamina | energy | regeneration, rank-ups | dungeons |
| Pal points | soft | using and lending helpers | friend summons |
| Monster eggs | material | dungeon drops | collection and fodder |

**Monetization**
- Summons on the rare egg machine with Magic Stones, with boosted "festival" events.
- Continues after a team wipe (a near-miss spend moment), stamina refills and monster box expansion (collection storage).
- Frequent IP collaborations with exclusive monsters.

**Live-ops**: rotating daily and weekly special dungeons, collaborations, festivals, ranking dungeons and seasonal events.

**Retention hooks**
- Rotating daily dungeons, stamina, helper reciprocity and collaboration windows.

**Social layer**
- The helper system: borrowing another player's leader and lending yours earns pal points for both, spreading the game socially. Co-op play was added later (verify).

**UX and onboarding notables**
- One-finger dragging in portrait with the board in the lower half, under the thumb, and the battle in the upper half.
- The timed drag creates real-time tension inside a turn-based structure.

**Art and audio identity**: a large catalogue of cute and cool monster art with evolution lines, and escalating audio and visual feedback as combos chain.

**Psychology principles used**
- Skill and competence: combo planning.
- Variable reward: summons and egg drops.
- Near-miss at continue prompts. Reciprocity in helpers. Scarcity in collaborations.

**Innovations**
- Free-drag orb movement instead of adjacent swaps, making match-3 a planning and dexterity puzzle.
- Merged puzzle combat with monster-collection RPG team building and gacha.
- The friend-helper leader as a growth and retention mechanic, later standard in Japanese gacha RPGs.

**Weaknesses and criticism**
- Power creep and complexity bloat over many years.
- Monetized collection storage, low summon rates, and weaker success in Western markets.

**Lessons for designers**
1. A familiar puzzle verb with a single twist (free drag) can carry an RPG.
2. Borrowing other players' leaders turns every player into a helper and a recruiter.
3. Collaborations are a powerful live-ops engine but accelerate power creep.

**Analogy hooks**
- Free-drag swapping → any grid puzzle needing more depth than swaps.
- Helper leaders → racing ghosts, co-op card helpers, async raid support.
- Colour-coded team attacks → match-3 combat in any RPG or roguelite.

**Ontology encoding**
```json
{"loops": [
  {"id": "pad_core", "type": "core", "period": "seconds", "steps": [
    {"id": "c1", "action": "drag_one_orb_freely_under_timer", "reward": "orb_arrangement", "next": "c2"},
    {"id": "c2", "action": "release_to_clear_combos", "reward": "colour_attacks_heals", "next": "c3"},
    {"id": "c3", "action": "clear_floor_or_boss", "reward": "eggs_coins_xp", "next": "c1"}]},
  {"id": "pad_meta", "type": "meta", "period": "session", "steps": [
    {"id": "m1", "action": "pick_friend_helper_leader", "reward": "leader_multiplier_pal_points", "next": "m2"},
    {"id": "m2", "action": "feed_evolve_monsters", "reward": "team_power", "next": "m1"}]}],
 "economy": {"currencies": [
  {"id": "magic_stones", "kind": "hard", "sources": ["iap", "events", "login"], "sinks": ["summons", "continues", "stamina", "box_space"], "cap": null},
  {"id": "coins", "kind": "soft", "sources": ["dungeons", "monster_sales"], "sinks": ["feeding", "evolutions"], "cap": null},
  {"id": "stamina", "kind": "energy", "sources": ["regeneration", "rank_ups"], "sinks": ["dungeons"], "cap": null},
  {"id": "pal_points", "kind": "soft", "sources": ["helper_use"], "sinks": ["friend_summons"], "cap": null}]}}
```

## 8. Monster Strike

**Snapshot**
- Developer and publisher: mixi (Japan), under its XFLAG brand for several years (verify brand history).
- Release: October 2013 in Japan. Some international versions launched and later closed (verify).
- Genre: physics-based co-op RPG with gacha. Business model: free-to-play with IAP.
- Scale: a long-running top grosser in Japan (widely reported; figures omitted).

**Core loop**
1. Bring up to four monsters into a quest: your own team, or one monster each from co-op partners.
2. On your turn, pull back and release a monster like a slingshot marble. It bounces around the arena, damaging enemies it hits.
3. Choose between bounce-type monsters (which rebound off enemies) and pierce-type monsters (which pass through) depending on enemy layout.
4. Touch your allies' marbles during your shot to trigger their friendship combos, extra attacks that reward positioning.
5. Fire a special Strike Shot when it has charged over several turns.
6. Clear stages and the boss for drops and experience. Spend Orbs (premium) on summons, continues or stamina.

**Meta and progression**
- Evolution and further awakening forms, plus a luck stat raised by fusing duplicates that improves rewards (verify mechanics).
- Collaboration monsters and event quests with high-difficulty tiers.

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Orbs | hard | IAP, events, login, quest clears | summons, continues, stamina |
| Gold | soft | quests | fusion, evolution |
| Stamina | energy | regeneration, rank-ups | quests |
| Evolution materials | material | quests, events | evolution, awakening |

**Monetization**: summons with Orbs, frequent collaboration banners, continues and stamina.

**Live-ops**: frequent IP collaborations, event quests, high-difficulty challenge quests, plus anime and cross-media.

**Retention hooks**: daily quests, events, friends to play with, and collection.

**Social layer**
- Co-op multiplayer is the core design. Friends in the same place can join one quest from their own phones, and remote invites through messaging apps extend this (verify connection methods).
- It became a playground and classroom social activity in Japan.

**UX and onboarding notables**
- A single drag-and-release gesture in portrait, readable physics, and short turn-based play that fits breaks.
- Players see each other's shots, so co-op is spectator-friendly.

**Art and audio identity**: cute, colourful monsters with clear bounce or pierce identities and satisfying impact sounds and effects.

**Psychology principles used**
- Relatedness: physical co-presence.
- Competence: aiming and angles.
- Variable reward: summons. Social proof: friends playing nearby.

**Innovations**
- Local co-op on phones as the defining feature, turning a mobile RPG into a group activity.
- A slingshot physics verb (familiar from Angry Birds) given RPG depth through bounce and pierce types and friendship combos.

**Weaknesses and criticism**
- Limited success outside Japan, where the social context differed.
- Gacha rates and collaboration-driven power creep.

**Lessons for designers**
1. In-person co-op spreads through dense social settings (schools, workplaces). Make joining a friend's game one tap.
2. A simple aim gesture can carry depth when positioning creates combos with allies.
3. A social hit is context-dependent. Test the social habit, not just the game, in each market.

**Analogy hooks**
- Slingshot marbles with bounce and pierce types → billiards, pinball, physics puzzles.
- Friendship combos by touching allies → co-op action games, party games.
- Same-room co-op from separate phones → party and board-game adaptations.

**Ontology encoding**
```json
{"loops": [
  {"id": "ms_core", "type": "core", "period": "seconds", "steps": [
    {"id": "c1", "action": "pull_and_release_monster_marble", "reward": "bounces_and_hits", "next": "c2"},
    {"id": "c2", "action": "touch_allies_trigger_friendship_combos", "reward": "extra_attacks", "next": "c3"},
    {"id": "c3", "action": "clear_stage_or_boss", "reward": "drops_xp", "next": "c1"}]},
  {"id": "ms_social", "type": "social", "period": "session", "steps": [
    {"id": "s1", "action": "invite_nearby_friends_to_quest", "reward": "shared_clear", "next": "s2"},
    {"id": "s2", "action": "compare_and_plan_teams", "reward": "social_status", "next": "s1"}]}],
 "economy": {"currencies": [
  {"id": "orbs", "kind": "hard", "sources": ["iap", "events", "login"], "sinks": ["summons", "continues", "stamina"], "cap": null},
  {"id": "gold", "kind": "soft", "sources": ["quests"], "sinks": ["fusion", "evolution"], "cap": null},
  {"id": "stamina", "kind": "energy", "sources": ["regeneration"], "sinks": ["quests"], "cap": null},
  {"id": "evolution_materials", "kind": "material", "sources": ["quests", "events"], "sinks": ["evolution"], "cap": null}]}}
```

## 9. Pokémon GO

**Snapshot**
- Developer: Niantic, with The Pokémon Company. In 2025 Niantic sold its games business, including Pokémon GO, to Scopely (announced 12 March 2025 at $3.5B: [Savvy Games Group announcement](https://savvygames.com/news/scopely-to-acquire-niantics-games-business); reported as closed on 29 May 2025).
- Release: July 2016.
- Genre: location-based collection game with optional AR. Business model: free-to-play with IAP (PokéCoins, event tickets).
- Scale: a record-setting launch that became a cultural phenomenon (widely reported; figures omitted).

**Core loop**
1. Walk in the real world. Pokémon appear on a map of your surroundings.
2. Tap to encounter and swipe to throw Poké Balls. A shrinking ring rewards accurate (Nice, Great, Excellent) and curved throws, and berries help.
3. Catching gives Stardust, species Candy and experience.
4. Spin PokéStops at real-world landmarks for items.
5. Power up Pokémon with Stardust and Candy, and evolve them with Candy.
6. Battle in Gyms, co-op Raids and the PvP league. Walk to hatch eggs at set distances. Return to step 1.

**Meta and progression**
- Trainer levels, the Pokédex (including regional exclusives and shiny variants), research tasks, buddies, PvP ranks and successive generations of Pokémon.

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| PokéCoins | hard | IAP, a small daily allowance from defending Gyms | storage upgrades, items, passes, tickets |
| Stardust | soft | catches, hatches, raids, research | power-ups, trades |
| Candy (and XL Candy) | material | catches, transfers, buddy walking, hatches | power-ups, evolutions |
| Items (balls, berries, incense, lures) | material | PokéStops, gifts, rewards, shop | encounters, spawns |
| Raid passes | energy | one free daily, shop | raids |

**Monetization**
- Storage upgrades for Pokémon and items, a quiet but significant sink.
- Incubators, raid passes (including remote passes), incense and lures, event and festival tickets, and avatar items.

**Live-ops**
- A monthly Community Day (a featured Pokémon for a few hours with bonuses), weekly spotlight and raid hours, seasonal events.
- A large annual festival with in-person and global ticketed editions, plus new-generation releases.

**Retention hooks**
- Daily first catch and first spin with streak rewards. Buddies, walking goals and egg hatching. Collection.
- Scheduled community events.

**Social layer**
- Three teams compete for Gyms. Co-op raids with many players, friends with gifts and friendship levels, trading (Stardust costs, friendship requirements), remote raids, and in-person community events.

**UX and onboarding notables**
- A real-world map as the interface. The throw gesture is learned in one encounter. AR is optional.
- Background step tracking credits walking while the app is closed.
- Battery and data use are concerns on long outings.

**Art and audio identity**: Pokémon IP with a stylised real-world map and remixed series music, instantly familiar to a multi-generational audience.

**Psychology principles used**
- Collection completion and variable reward (spawns, shinies).
- Social proof and relatedness: public gatherings.
- Streaks and loss aversion. Curiosity about what is nearby. Reciprocity through gifts.
- Health benefits from walking as a positive side effect.

**Innovations**
- Physical movement in the real world as the core loop at mass scale.
- Real landmarks as game objects (building on Niantic's earlier game Ingress), and co-op raids and Community Days that create real-world gatherings.

**Weaknesses and criticism**
- Safety incidents and trespassing concerns at launch, and an early account-permission scope problem that was quickly fixed (widely reported).
- Location spoofing and cheating; rural players are disadvantaged.
- Rolling back pandemic-era accessibility bonuses (2021) and later remote-raid price and limit changes (2023) drew organised player backlash (widely reported).

**Lessons for designers**
1. A real-world verb (walking) can be the core loop if every walk yields something.
2. Scheduled community events create real appointments and social proof.
3. Removing a convenience players have adapted to costs more goodwill than never adding it.

**Analogy hooks**
- Step-based egg hatching → fitness apps, walking-based idle rewards.
- Community Day → limited windows in any collection game.
- Landmark-based stops → location features in social and travel apps.

**Ontology encoding**
```json
{"loops": [
  {"id": "pgo_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "walk_to_find_spawns_and_stops", "reward": "encounters_items", "next": "c2"},
    {"id": "c2", "action": "throw_balls_to_catch", "reward": "stardust_candy_xp", "next": "c3"},
    {"id": "c3", "action": "power_up_and_evolve", "reward": "stronger_pokemon_dex_entries", "next": "c1"}]},
  {"id": "pgo_event", "type": "liveops", "period": "season", "steps": [
    {"id": "e1", "action": "attend_community_day_window", "reward": "featured_spawns_bonuses", "next": "e2"},
    {"id": "e2", "action": "raid_with_local_group", "reward": "rare_pokemon", "next": "e1"}]}],
 "economy": {"currencies": [
  {"id": "pokecoins", "kind": "hard", "sources": ["iap", "gym_defence"], "sinks": ["storage", "items", "passes", "tickets"], "cap": null},
  {"id": "stardust", "kind": "soft", "sources": ["catches", "hatches", "raids"], "sinks": ["power_ups", "trades"], "cap": null},
  {"id": "candy", "kind": "material", "sources": ["catches", "transfers", "buddy_walking"], "sinks": ["power_ups", "evolutions"], "cap": null},
  {"id": "raid_passes", "kind": "energy", "sources": ["daily_free", "shop"], "sinks": ["raids"], "cap": null}]}}
```

## 10. Marvel Snap

**Snapshot**
- Developer: Second Dinner, a studio co-founded by Ben Brode, formerly game director of Hearthstone. Publisher at launch: Nuverse (ByteDance).
- Release: October 2022 on mobile and PC. In January 2025 the game briefly went offline in the US alongside ByteDance apps during the TikTok ban, after which Second Dinner announced a change of publishing arrangements (widely reported; verify current publisher).
- Genre: collectible card game. Business model: free-to-play with IAP (season pass, cosmetics, card acquisition offers).
- Scale: a widely awarded and widely played launch (figures omitted).

**Core loop**
1. Build a 12-card deck.
2. Play a match of six turns. Energy equals the turn number, rising from 1 to 6.
3. Three locations are revealed, one per turn over the first three turns, and each has a random rule.
4. Both players commit cards at the same time, and reveals resolve in order.
5. Win two of the three locations by total power.
6. Either player can "snap" to double the stakes in Cosmic Cubes (the rank currency), and the stakes double again on the final turn. A player who expects to lose can retreat early to cut losses.
7. Earn or lose cubes and earn credits and boosters to upgrade card variants. Upgrades raise Collection Level, which unlocks new cards. Return to step 1.

**Meta and progression**
- Collection Level is the main progression: cosmetic upgrades to card art (frames, effects) raise it and unlock cards along a track.
- Cards are grouped into pools or series by rarity. The scarcest series are acquired through tokens, caches with a featured card, or offers (systems have changed several times; verify).
- A monthly season pass that includes a new card, ranked seasons, a separate competitive mode (verify) and player groups.

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Gold | hard | IAP, missions, pass | pass, bundles, variants |
| Credits | soft | missions, pass, Collection Level rewards | card upgrades |
| Boosters (per card) | material | playing the card, rewards | card upgrades |
| Collector's tokens and cache keys | material | Collection Level rewards, pass, offers | specific or featured new cards |
| Cosmic Cubes | xp | snapped wins | snapped losses |

**Monetization**
- The season pass (with its monthly card), gold bundles, card variant bundles and featured-card acquisition offers.
- Card upgrades are cosmetic. They never change a card's power, a deliberate split between progression and competitive balance.

**Live-ops**
- Monthly seasons with a theme and pass card, new cards on a regular cadence, frequent balance changes, temporary game modes and featured locations.

**Retention hooks**
- Daily and weekly missions, rank climbing, and the next Collection Level reward. New cards and seasonal themes.

**Social layer**
- Friendly battles, player alliances or groups with shared missions (verify), and a strong creator community around deck building.

**UX and onboarding notables**
- A full match takes about three minutes. Simultaneous turns remove waiting.
- Only 12 cards and 6 turns, so a deck and a game are easy to hold in mind.
- The snap and retreat buttons turn uncertainty into a decision rather than a frustration.

**Art and audio identity**: comic-book art for the Marvel IP with many variant styles by different artists, animated upgrade effects and satisfying reveal sounds.

**Psychology principles used**
- Competence and quick mastery: short games.
- Risk and bluffing: the snap, borrowed from poker's raise.
- Collection and cosmetic identity: variants. Loss mitigation: retreat.

**Innovations**
- A very short CCG format (12 cards, 6 turns, simultaneous turns) with random locations for variety.
- A stakes mechanic (snap) that adds a poker-like meta-game to every match.
- Cosmetic upgrades as the progression engine, decoupling spending from card power.

**Weaknesses and criticism**
- New cards are scarce and strong, so acquiring them quickly costs money. Changes to acquisition systems drew criticism (verify specifics).
- Randomness in locations and collection unlocks, no trading, and debate over competitive depth.

**Lessons for designers**
1. Shrink the format until a match fits a mobile session, then add variance (locations) to keep it fresh.
2. Add a stakes bet so players manage risk, not just cards.
3. Decouple cosmetic progression from power, so spending feels good without breaking matches.
4. Be transparent and stable with card acquisition. Repeated system changes erode trust.

**Analogy hooks**
- Snap (doubling stakes) → any PvP with ranked currency (puzzle duels, trivia, racing).
- Random location rules → board modifiers in puzzle PvP and autobattlers.
- Cosmetic upgrades unlocking content → collection games, sports card apps.

**Ontology encoding**
```json
{"loops": [
  {"id": "snap_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "play_cards_simultaneously_per_turn", "reward": "location_power", "next": "c2"},
    {"id": "c2", "action": "decide_snap_or_retreat", "reward": "stakes_adjusted", "next": "c3"},
    {"id": "c3", "action": "win_two_of_three_locations", "reward": "cosmic_cubes_boosters", "next": "c4"},
    {"id": "c4", "action": "upgrade_card_variants", "reward": "collection_level_new_cards", "next": "c1"}]},
  {"id": "snap_season", "type": "liveops", "period": "season", "steps": [
    {"id": "s1", "action": "complete_missions", "reward": "pass_progress", "next": "s2"},
    {"id": "s2", "action": "claim_pass_card_and_variants", "reward": "new_card_cosmetics", "next": "s1"}]}],
 "economy": {"currencies": [
  {"id": "gold", "kind": "hard", "sources": ["iap", "missions", "pass"], "sinks": ["pass", "bundles", "variants"], "cap": null},
  {"id": "credits", "kind": "soft", "sources": ["missions", "pass"], "sinks": ["card_upgrades"], "cap": null},
  {"id": "boosters", "kind": "material", "sources": ["playing_card", "rewards"], "sinks": ["card_upgrades"], "cap": null},
  {"id": "collector_tokens", "kind": "material", "sources": ["collection_level", "pass"], "sinks": ["specific_cards"], "cap": null},
  {"id": "cosmic_cubes", "kind": "xp", "sources": ["wins"], "sinks": ["losses"], "cap": null}]}}
```

## 11. Hearthstone

**Snapshot**
- Developer and publisher: Blizzard Entertainment (part of Microsoft since the 2023 Activision Blizzard acquisition, widely reported).
- Release: March 2014 on PC, followed by tablets and phones later in 2014 (verify dates).
- Genre: digital collectible card game with several modes. Business model: free-to-play with IAP (packs, expansion bundles, pass, cosmetics).
- Scale: one of the most influential digital CCGs (figures omitted).

**Core loop**
1. Choose a class hero, each with a two-mana hero power, and a 30-card deck.
2. Take turns. Mana crystals grow by one per turn up to 10, and you draw a card each turn.
3. Play minions, spells and weapons. Minions usually attack from the next turn, and keywords (taunt, divine shield, charge or rush) change the rules.
4. Reduce the enemy hero from 30 health to zero.
5. Win rank progress and rewards. Open packs of five cards, disenchant duplicates into dust, and craft the specific cards you want. Return to step 1.

**Meta and progression**
- Standard and Wild formats (2016) with yearly rotation of older sets out of Standard.
- Arena (draft with an entry fee), Battlegrounds (an autobattler mode added in 2019), weekly rule-twist brawls, and other modes added and retired over time (verify current set).
- A rewards track with free and paid tiers.

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Gold | soft | quests, rewards track, wins | packs, Arena, cosmetics |
| Dust | material | disenchanting cards | crafting specific cards |
| Card packs | material | gold, rewards, IAP | collection |
| Premium currency (purchase-only; verify name) | premium | IAP | bundles, cosmetics |
| Rank stars | xp | wins | losses |

**Monetization**
- Card packs and expansion pre-order bundles, a paid rewards-track tier, cosmetics (hero skins, card backs) and Battlegrounds perks.
- Pack protections: Blizzard announced a guarantee of a Legendary card within the first 40 packs of a set (2017, widely reported) and later guarantees on early Legendaries in new expansions and duplicate protection (verify current rules).

**Live-ops**
- About three expansions a year, plus mini-sets, balance patches, yearly Standard rotation, weekly brawls and Battlegrounds seasons.

**Retention hooks**
- Daily and weekly quests, the rewards track, new expansions, and monthly ranked seasons.

**Social layer**
- Friends, spectating, friendly challenges, a big streaming and esports scene, and fixed emotes only, preventing chat abuse.

**UX and onboarding notables**
- A tactile board: cards with weight, interactive board corners, crisp feedback and juicy animations.
- Simplified rules versus paper CCGs: almost no interaction during the opponent's turn (except pre-set secrets), which keeps turns fast and the game readable.
- A guided single-player tutorial against class heroes.

**Art and audio identity**: Warcraft-universe characters in a warm tavern frame, an innkeeper narrator, iconic sound design and card voice lines.

**Psychology principles used**
- Variable reward from packs, with crafting as deterministic agency.
- Competence and mastery; collection; social comparison through rank.
- Novelty: expansions and rotation.

**Innovations**
- Digital-native CCG design: rules impossible on paper (random generation, transforming cards), and removal of the interrupt stack to fit online play.
- Crafting and dust as an anti-frustration valve for random packs.
- Fixed emotes as a non-toxic communication system. Battlegrounds showed a CCG platform can host a new genre mode.

**Weaknesses and criticism**
- Cost to keep up with three expansions a year; RNG frustration; power creep.
- A 2019 controversy, when Blizzard penalised a professional player for voicing support for the Hong Kong protests in a post-match interview, drew wide ethical criticism. Penalties were later reduced (widely reported).
- Modes launched and later retired (verify).

**Lessons for designers**
1. Translate genre rules for the medium. Remove complexity that only made sense on paper.
2. Pair random packs with a deterministic path (crafting) and a published pity.
3. Fixed emotes give expression without toxicity.
4. Rotation keeps the format fresh but raises the cost of staying current. Offer a format that does not rotate.

**Analogy hooks**
- Dust crafting → any random-drop game (gear salvage, sticker duplicates).
- Fixed emotes → any PvP with strangers.
- A CCG platform hosting an autobattler → adding a new genre mode to a live roster game.

**Ontology encoding**
```json
{"loops": [
  {"id": "hs_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "play_cards_with_growing_mana", "reward": "board_advantage", "next": "c2"},
    {"id": "c2", "action": "attack_and_trade_minions", "reward": "enemy_hero_damage", "next": "c3"},
    {"id": "c3", "action": "win_match", "reward": "rank_progress_gold", "next": "c1"}]},
  {"id": "hs_collection", "type": "meta", "period": "weekly", "steps": [
    {"id": "m1", "action": "open_packs", "reward": "random_cards", "next": "m2"},
    {"id": "m2", "action": "disenchant_duplicates_craft_targets", "reward": "deck_completion", "next": "m1"}]}],
 "economy": {"currencies": [
  {"id": "gold", "kind": "soft", "sources": ["quests", "rewards_track"], "sinks": ["packs", "arena"], "cap": null},
  {"id": "dust", "kind": "material", "sources": ["disenchant"], "sinks": ["crafting"], "cap": null},
  {"id": "packs", "kind": "material", "sources": ["gold", "rewards", "iap"], "sinks": ["collection"], "cap": null},
  {"id": "rank_stars", "kind": "xp", "sources": ["wins"], "sinks": ["losses"], "cap": null}]}}
```

## 12. Uma Musume: Pretty Derby

**Snapshot**
- Developer and publisher: Cygames (Japan).
- Release: 24 February 2021 in Japan on iOS and Android, with a Windows version on DMM Games on 10 March 2021. The worldwide (English-language) release followed on 26 June 2025 for iOS, Android and Windows, including Steam ([Wikipedia: Umamusume: Pretty Derby](https://en.wikipedia.org/wiki/Umamusume:_Pretty_Derby)). Regional publishers (Kakao Games in Korea, Komoe in Taiwan and Hong Kong, Bilibili in China) run their own versions.
- Genre: training simulation with gacha, part of a multimedia franchise (anime, manga) whose characters are named after real racehorses, used under arrangements with their owners (widely reported). Business model: free-to-play with IAP.
- Scale: one of Japan's highest-grossing games in 2021 (widely reported; figures omitted).

**Core loop** (the training career run)
1. Pick a trainee character, a deck of up to six support cards (one may be borrowed from a friend) and two parent characters whose inherited traits boost the run.
2. Play an in-game career of about three years in turns. Each turn, choose to train one of five stats (Speed, Stamina, Power, Guts, Wit), rest, go out (mood), visit the infirmary, or race.
3. Support cards appear at training facilities. Training with them gives bonuses, and high bond triggers stronger "friendship" training and story events.
4. Random events offer choices with stat and skill outcomes. Manage energy (low energy risks failed training) and mood.
5. Meet objective races by their deadlines, or the run ends.
6. At the end, the trainee becomes a graded veteran with skills (bought with skill points) and inheritable traits.
7. Use veterans in PvP events and as parents for future runs. Return to step 1 with a better legacy.

**Meta and progression**
- Trainee awakening levels, support card limit breaks from duplicates (up to four extra copies for the maximum level), skills and a legacy chain where better parents produce better runs.
- New training scenarios added periodically, each with its own mechanics (verify list).

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Carats | hard (paid and free balances may be tracked separately) | IAP, missions, events | summons, refills |
| Money | soft | runs, missions | upgrades, shop |
| Training points | energy | regeneration, items | career runs |
| Support cards and trainees | material | summons, exchange | runs, limit breaks |
| Exchange points | material | each summon | the featured card after enough pulls |

**Monetization**
- Two summon banners (trainees and support cards). Each pull earns exchange points, and after 200 points the featured card can be exchanged ("spark"; verify current value).
- Support card limit breaks make duplicates valuable, which is the main spending driver for competitive players.
- Daily-carat packs and bundles.

**Live-ops**: new trainees and support cards, new training scenarios, story events, and recurring PvP championship events (verify cadence).

**Retention hooks**
- The run-based structure (each run is different), training-point regeneration, the legacy chain, PvP events and story.

**Social layer**
- Clubs, borrowing a friend's support card for a run (a central social exchange), PvP team trials and championship events.

**UX and onboarding notables**
- A career run is a self-contained roguelite with authored events, playable in tens of minutes.
- Races play out in 3D, and winning triggers a live concert performance by the characters.

**Art and audio identity**: polished 3D anime characters with idol-style stage performances, original songs and full voice acting. Racing and idol fantasies are combined.

**Psychology principles used**
- Run variance and mastery: roguelite structure.
- Endowment: raised characters. Idol fandom (parasocial attachment). Collection.
- Near-miss: failing an objective race. Sunk cost in the legacy chain.

**Innovations**
- Brought the "success mode" training-run structure (associated with Konami's Power Pro baseball series) into a gacha character game, with support cards as a deck.
- An inheritance system that links runs into a long-term breeding chase.
- Licensed real racehorse names into idol fiction.

**Weaknesses and criticism**
- Support-card duplicates make competitive play expensive.
- RNG run failures, complex systems for newcomers, and a grind for legacy parents.
- Licensing constraints mean some famous horses are absent.

**Lessons for designers**
1. A roguelite run fits gacha: collected cards become the run's deck and the run's outcome becomes a collectible.
2. Inheritance links runs into a long arc and makes failed runs partly useful.
3. Borrowing a friend's best card per run adds social value to every collection.

**Analogy hooks**
- Turn-limited training runs → sports management, idol sims, pet raising.
- A support-card deck that triggers events → deckbuilders with narrative events.
- Parent inheritance → breeding games, roguelite meta-progression.

**Ontology encoding**
```json
{"loops": [
  {"id": "uma_run", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "choose_training_rest_or_race_each_turn", "reward": "stats_bond_events", "next": "c2"},
    {"id": "c2", "action": "resolve_random_events_and_objective_races", "reward": "skills_or_run_end", "next": "c3"},
    {"id": "c3", "action": "finish_career", "reward": "graded_veteran_inheritable_traits", "next": "c1"}]},
  {"id": "uma_legacy", "type": "meta", "period": "daily", "steps": [
    {"id": "m1", "action": "pick_parents_and_support_deck", "reward": "stronger_next_run", "next": "m2"},
    {"id": "m2", "action": "enter_veteran_in_pvp_event", "reward": "rank_rewards", "next": "m1"}]}],
 "economy": {"currencies": [
  {"id": "carats", "kind": "hard", "sources": ["iap", "missions", "events"], "sinks": ["summons", "refills"], "cap": null},
  {"id": "money", "kind": "soft", "sources": ["runs", "missions"], "sinks": ["upgrades", "shop"], "cap": null},
  {"id": "training_points", "kind": "energy", "sources": ["regeneration", "items"], "sinks": ["career_runs"], "cap": null},
  {"id": "exchange_points", "kind": "material", "sources": ["each_summon"], "sinks": ["featured_card_exchange"], "cap": null}]}}
```

## 13. Arknights

**Snapshot**
- Developer: Hypergryph (Shanghai). Global publisher: Yostar.
- Release: May 2019 in China, January 2020 globally.
- Genre: tower defense with gacha character collection ("operators"). Business model: free-to-play with IAP (gacha, monthly card, skins).
- Scale: a long-running hit with a reputation for a generous economy (figures omitted).

**Core loop**
1. Bring a squad of operators (plus one support operator from a friend) into a stage: a tile grid with enemy paths.
2. Deployment points regenerate over time. Spend them to deploy operators: melee operators on ground tiles, ranged ones on high ground. Choose each operator's facing.
3. Each operator blocks a set number of enemies and has skills that charge and fire, automatically or manually. Retreating refunds part of the cost, and redeploying has a cooldown.
4. Stop enemies reaching the protected exit.
5. After a perfect (3-star) clear, the game records your run and can replay it automatically ("proxy" or auto-deploy) for farming.
6. Spend Sanity (stamina) to farm materials. Promote operators, raise skill levels and pull on headhunting banners. Return to step 1.

**Meta and progression**
- Operator promotion tiers, skill levels and masteries, potential from duplicates (minor bonuses) and modules.
- A base that produces resources idly; tag-based recruitment that lets players target operators without gacha.
- A roguelite mode, a self-selected difficulty-modifier mode where players stack risk for score, and weekly capped premium-currency stages (verify current modes).

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Originite Prime | hard | IAP, first clears | Orundum, sanity refills, skins |
| Orundum | hard | weekly missions, events, capped weekly stages, conversion | headhunting (600 per pull) |
| Headhunting permits | material | events, shops | pulls |
| LMD | soft | stages, base | levels, promotions |
| Sanity | energy | regeneration (verify rate) | stages |
| Certificates | material | duplicates, recruitment | exchange shops (including specific operators) |

**Monetization**
- Headhunting with a 2% base rate for the top rarity. After 50 pulls without one, the rate rises by 2% per pull until one is obtained, so it is guaranteed by about pull 99 (verify per banner).
- Monthly card, packs and popular skins. Certificate shops let duplicates and recruitment buy specific operators.

**Live-ops**: story events every few weeks with new operators, reruns, roguelite seasons and difficulty-modifier seasons, plus anime and cross-media.

**Retention hooks**
- Sanity, base production, daily and weekly missions, events and the weekly capped stage.

**Social layer**: friend support operators and base visits that exchange clue items (verify). The game is mostly single-player.

**UX and onboarding notables**
- 3-star auto-replay removes the grind of re-playing solved stages, a signature respect-for-time feature.
- Double speed. Landscape layout. A dense UI with distinctive, highly praised graphic design.
- The difficulty curve rises steeply. New players often need guides.

**Art and audio identity**: a dystopian sci-fi setting with a strong graphic-design language in UI and illustrations by many artists.

**Psychology principles used**
- Mastery and competence: puzzle-like stages.
- Collection, curiosity (dense lore) and FOMO.
- Reciprocity: a generous economy builds trust.

**Innovations**
- Every gacha character is a unique tower with its own skills, block count and role, uniting collection and TD.
- Auto-replay unlocked by a perfect clear.
- Tag-based recruitment and certificate exchanges alongside the gacha.
- A self-selected risk-modifier mode for scalable challenge.

**Weaknesses and criticism**
- Steep difficulty for newcomers, material grind, and text-heavy story with translation demands.
- Landscape only; operator power creep.

**Lessons for designers**
1. Make each collectible a distinct mechanic, not a stat stick. That keeps old units relevant.
2. Reward mastery with automation: once solved, let the player skip the grind.
3. Offer deterministic acquisition paths (recruitment, exchange shops) beside the gacha to build trust.
4. Let players choose their own difficulty modifiers for score.

**Analogy hooks**
- Collectible towers with roles → any TD or lane battler with a roster.
- Auto-replay after mastery → puzzle levels (replay solved), farming in any RPG.
- Stacked risk modifiers → roguelite ascension, puzzle challenge modes.

**Ontology encoding**
```json
{"loops": [
  {"id": "ak_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "spend_deployment_points_place_operators", "reward": "blocked_lanes", "next": "c2"},
    {"id": "c2", "action": "fire_skills_retreat_redeploy", "reward": "enemies_stopped", "next": "c3"},
    {"id": "c3", "action": "clear_stage_three_stars", "reward": "materials_auto_replay_unlock", "next": "c4"},
    {"id": "c4", "action": "promote_and_skill_up_operators", "reward": "squad_power", "next": "c1"}]},
  {"id": "ak_gacha", "type": "monetization", "period": "weekly", "steps": [
    {"id": "g1", "action": "earn_orundum_weekly", "reward": "pull_budget", "next": "g2"},
    {"id": "g2", "action": "headhunt_with_rising_rate_after_50", "reward": "operators_certificates", "next": "g1"}]}],
 "economy": {"currencies": [
  {"id": "originite_prime", "kind": "hard", "sources": ["iap", "first_clears"], "sinks": ["orundum", "sanity_refills", "skins"], "cap": null},
  {"id": "orundum", "kind": "hard", "sources": ["missions", "events", "weekly_capped_stage", "originite_prime_conversion"], "sinks": ["headhunting"], "cap": null},
  {"id": "lmd", "kind": "soft", "sources": ["stages", "base"], "sinks": ["levels", "promotions"], "cap": null},
  {"id": "sanity", "kind": "energy", "sources": ["regeneration", "refills"], "sinks": ["stages"], "cap": null},
  {"id": "certificates", "kind": "material", "sources": ["duplicates", "recruitment"], "sinks": ["exchange_shop"], "cap": null}]}}
```

## 14. Pokémon TCG Pocket

**Snapshot**
- Developers: Creatures Inc. and DeNA. Publisher: The Pokémon Company.
- Release: October 2024.
- Genre: collection-first digital card game with simplified battles. Business model: free-to-play with IAP (premium currency, a monthly subscription pass, cosmetics).
- Scale: a very strong launch by widely reported store rankings (figures omitted).

**Core loop**
1. Open free booster packs on a timer: pack stamina refills over time, allowing about two free packs a day (verify), and hourglass items shorten the wait.
2. Tear the pack with a swipe and reveal five cards one by one. Rare cards include animated "immersive" art.
3. Use Wonder Pick: choose a pack recently opened by a friend or another player and pick one of its cards at random, face down (costs a separate stamina).
4. Build 20-card decks and battle. Energy is generated automatically each turn (no energy cards), the bench holds three, and the first to three points wins (some powerful cards give two points when knocked out).
5. Earn rewards from missions and battles: hourglasses, shop tickets and pack points, which can be exchanged for specific cards from a set (a deterministic pity).
6. Complete sets and return to step 1 the next day.

**Meta and progression**
- Set completion across rarity tiers; new expansions and mini-sets; events with emblems; a card trading system added in early 2025 with its own currency and rarity limits (verify current rules).

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Poké Gold | premium | IAP | hourglasses, cosmetics |
| Pack stamina | energy | regeneration, hourglasses | free pack openings |
| Wonder stamina | energy | regeneration, hourglasses | Wonder Picks |
| Pack and Wonder hourglasses | material | missions, events, shop, Poké Gold | skipping waits |
| Pack points | material | each pack opened | exchanging for specific cards |
| Trade currency (verify name) | material | trading-related sources (verify) | trades |
| Shop tickets | soft | missions | cosmetics, items |

**Monetization**
- Poké Gold to skip pack timers, a monthly Premium Pass subscription (an extra daily pack and cosmetics; verify perks), and cosmetics such as binders, sleeves and display items.

**Live-ops**: new sets and mini-sets on a regular cadence, events with drop bonuses, missions and emblems, and battle events.

**Retention hooks**
- The daily pack ritual, the pack timer, set completion, and Wonder Picks from friends' openings.

**Social layer**
- Friends, Wonder Pick (others' luck becomes your chance), trading with restrictions, card display binders and simple PvP.

**UX and onboarding notables**
- The pack-tearing gesture and one-by-one reveal turn opening into a short ceremony.
- Battles are short and simplified, so the collection matters more than tournament-level rules mastery.
- Portrait, with sessions of a few minutes.

**Art and audio identity**: Pokémon card art by many illustrators, as in the physical TCG, plus immersive animated cards and nostalgic first-generation themes in the first set.

**Psychology principles used**
- Daily ritual and appointment; variable reward with anticipation built by staged reveals.
- Collection completion; nostalgia; social luck (Wonder Pick).
- Ethical line: paid timer skips for random packs in a franchise popular with children.

**Innovations**
- Made pack opening itself the core loop, instead of a reward for playing battles.
- Wonder Pick turns other players' openings into a social chance mechanic.
- Animated immersive cards as a digital-only rarity, and pack points as a deterministic pity.

**Weaknesses and criticism**
- The 2025 trading system drew strong backlash over its cost and restrictions, with later adjustments (widely reported; verify).
- Rare-card scarcity. Limited battle depth. Random packs sold to a young audience raise loot-box and minors concerns (see section 17).

**Lessons for designers**
1. A tactile, well-paced reveal is content. Design the opening ceremony as carefully as gameplay.
2. A free daily ration builds a ritual. Paid skips should accelerate, never gate.
3. Add a deterministic path (pack points) to any random pack system.
4. Design trading carefully before launch. Restrictions added later feel like takeaways.

**Analogy hooks**
- A daily free pack with a ceremony → sticker albums, cosmetic collections, card-based roguelites.
- Wonder Pick → social lotteries in casual games (pick from a friend's reward chest).
- Simplified battles serving the collection → collection apps with light gameplay.

**Ontology encoding**
```json
{"loops": [
  {"id": "tcgp_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "open_free_pack_with_swipe_reveal", "reward": "five_cards_pack_points", "next": "c2"},
    {"id": "c2", "action": "wonder_pick_from_friend_pack", "reward": "random_card", "next": "c3"},
    {"id": "c3", "action": "build_deck_and_battle", "reward": "mission_rewards_hourglasses", "next": "c1"}]},
  {"id": "tcgp_ritual", "type": "meta", "period": "daily", "steps": [
    {"id": "m1", "action": "return_when_pack_stamina_refills", "reward": "free_pack", "next": "m2"},
    {"id": "m2", "action": "exchange_pack_points_for_target_card", "reward": "set_completion", "next": "m1"}]}],
 "economy": {"currencies": [
  {"id": "poke_gold", "kind": "premium", "sources": ["iap"], "sinks": ["hourglasses", "cosmetics"], "cap": null},
  {"id": "pack_stamina", "kind": "energy", "sources": ["regeneration", "hourglasses"], "sinks": ["free_packs"], "cap": null},
  {"id": "wonder_stamina", "kind": "energy", "sources": ["regeneration", "hourglasses"], "sinks": ["wonder_picks"], "cap": null},
  {"id": "pack_points", "kind": "material", "sources": ["pack_openings"], "sinks": ["specific_card_exchange"], "cap": null},
  {"id": "shop_tickets", "kind": "soft", "sources": ["missions"], "sinks": ["cosmetics"], "cap": null}]}}
```

## 15. Legend of Mushroom (idle-RPG exemplar)

**Snapshot**
- Developer and publisher: the App Store listing shows the seller as JOY MOBILE NETWORK PTE. LTD. and the developer name as "Joy Net Games" (bundle `com.us.mxdzz.ios`). Other store listings may name a different publisher entity, so check the listing you cite ([App Store metadata](https://itunes.apple.com/search?term=legend+of+mushroom&entity=software&country=us&limit=5)).
- Release: first released on the US iOS App Store on 7 March 2024 (listing metadata). Earlier releases in some Asian markets are possible but were not verified here.
- Genre: idle RPG of the "gear-draw" type, where drawing random equipment is the main input. Business model: free-to-play with IAP; check current builds for ad placements.
- Scale: reported among the top-grossing mobile games in several markets in 2024 (trade-press rankings; figures omitted, verify).
- Evidence note: this case describes the publicly visible design pattern of the game and its subgenre (grade C). Verify system names and numbers against a current build.

**Core loop**
1. The hero (a mushroom character) auto-battles through side-scrolling stages of waves and a boss.
2. Spend a draw token to pull equipment from the central item source. Each draw yields a random piece for one of several gear slots.
3. The UI compares the new piece with the equipped one (stat arrows up or down). Equip it, or sell or break it down for soft currency and experience.
4. Power rises, so the auto-battle pushes further and bosses drop more tokens.
5. Level up the draw source itself, shifting the odds toward higher rarity tiers.
6. Unlock further layers (class evolutions, skills, companions, mounts, arena PvP) and return to step 2.

**Meta and progression**
- Account level and class evolution paths, plus several collection layers (skills, companions, mounts, relics), each with its own draw or upgrade system (verify current layers).
- Daily dungeons with keys, idle accrual and a guild.

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Coins | soft | stages, selling gear | upgrades, draw-source levels |
| Draw tokens | material | stages, bosses, idle accrual, events | gear draws |
| Gems | hard | IAP, events, achievements | summons, packs, speedups |
| Dungeon keys | energy | daily refresh | daily dungeons |
| Summon tickets (skills, companions) | material | events, gems, packs | collection draws |

**Monetization**
- Starter packs, monthly privileges, growth funds and passes attached to several progression systems.
- Summons for skills and companions with disclosed odds (verify). Gem bundles. Ad placements, if any, should be checked in current builds.

**Live-ops**: events, new collection items, server-based competitions and seasonal content (verify cadence).

**Retention hooks**
- Draw tokens accumulating while away, daily dungeon keys, stage numbers and many parallel upgrade bars.

**Social layer**: guilds, arena PvP and server rankings.

**UX and onboarding notables**
- The whole core is one button plus a binary decision (equip or sell), readable in a 3-second ad.
- Constant visible number growth: damage numbers, power score, stage counter.
- A humorous protagonist softens a dense progression stack.

**Art and audio identity**: cute, comedic 2D fantasy art with a mushroom hero, bright effects and loot-rarity colours.

**Psychology principles used**
- Very high-frequency variable reward: every draw is a micro-lottery with an immediate compare decision.
- Endowed progress and goal-gradient: many bars filling. Low skill barrier: competence without dexterity.
- Ethical line: many stacked random systems and paid acceleration.

**Innovations**
- Made the loot draw the primary verb, compressing an action-RPG loot loop (find, compare, equip, salvage) into a single button.
- A levelling draw source that progresses the loot table itself.

**Weaknesses and criticism**
- Shallow agency and repetition. Many parallel gacha and upgrade systems create complexity and spending fatigue.
- Pay-to-progress pressure; easily cloned.

**Lessons for designers**
1. The compare-and-decide moment (keep or sell) is a satisfying micro-decision. It can carry a core loop if feedback is instant.
2. Letting players upgrade the loot source gives meta progression without new content.
3. Every extra random system adds friction and ethical exposure. Cap the count.

**Analogy hooks**
- Draw-and-compare as the core verb → hybrid-casual survivor-likes (gear drops), merge games.
- An upgradable loot source → chest-upgrade systems, crafting stations in sims.
- Idle auto-battle with one active decision → idle games needing a tactile verb.

**Ontology encoding**
```json
{"loops": [
  {"id": "lom_core", "type": "core", "period": "seconds", "steps": [
    {"id": "c1", "action": "spend_token_draw_gear", "reward": "random_gear_piece", "next": "c2"},
    {"id": "c2", "action": "compare_then_equip_or_sell", "reward": "power_or_coins_xp", "next": "c3"},
    {"id": "c3", "action": "auto_battle_further_stages", "reward": "draw_tokens_boss_drops", "next": "c1"}]},
  {"id": "lom_meta", "type": "meta", "period": "daily", "steps": [
    {"id": "m1", "action": "level_draw_source", "reward": "better_rarity_odds", "next": "m2"},
    {"id": "m2", "action": "run_daily_dungeons_and_summons", "reward": "skills_companions", "next": "m1"}]}],
 "economy": {"currencies": [
  {"id": "coins", "kind": "soft", "sources": ["stages", "gear_sales"], "sinks": ["upgrades", "draw_source_levels"], "cap": null},
  {"id": "draw_tokens", "kind": "material", "sources": ["stages", "bosses", "idle_accrual"], "sinks": ["gear_draws"], "cap": null},
  {"id": "gems", "kind": "hard", "sources": ["iap", "events"], "sinks": ["summons", "packs"], "cap": null},
  {"id": "dungeon_keys", "kind": "energy", "sources": ["daily_refresh"], "sinks": ["daily_dungeons"], "cap": null}]}}
```

## 16. Cross-case synthesis for RPG, gacha, idle and cards

### 16.1 The five families compared

| Family | Cases | What the player buys | Session shape | Retention engine | Main risk |
|---|---|---|---|---|---|
| Gacha RPG (PvE-led) | 1, 2, 6, 13 | Characters and their duplicates | 10–30 min daily plus version events | Story, versions, endgame resets, stamina | Power creep, gacha pressure |
| Gacha RPG (PvP-heavy) | 4, 5, 7, 8 | Characters, gear chase, refills | 10–30 min plus farming | Gear optimisation, arena, guild content | Pay-to-win perception |
| Idle RPG | 3, 15 | Acceleration, privileges, summons | Many 1–5 min check-ins | Offline accrual, number growth | Shallow agency, stacked gachas |
| Collectible card games | 10, 11, 14 | Collection access, cosmetics, pass | 3–10 min matches or a daily ritual | New sets, ladders, completion | Cost of keeping up, scarcity anger |
| Trainer and location hybrids | 9, 12 | Convenience, storage, events, support cards | Runs of tens of minutes; walks | Runs and legacy; real-world events | Licensing, safety, regional fit |

### 16.2 Pity and guarantee systems (verify every value in the current in-game disclosure)

| Case | Base top-rarity rate | Guarantee mechanism | Featured-unit rule | Deterministic alternative |
|---|---|---|---|---|
| Genshin Impact, Honkai: Star Rail | 0.6% (character banners) | Hard pity at 90; community data shows soft pity from about pull 74 | 50/50, then guaranteed after a loss | Exchange shops from duplicates |
| Arknights | 2% | +2% per pull after 50 dry pulls (guaranteed by about 99) | Banner-specific rules | Tag recruitment, certificate shops |
| Fate/Grand Order | about 1% (featured about 0.7–0.8%) | None for years; later a featured guarantee at 330 summons on JP | Featured share of the 5-star rate | Paid lucky bags (guaranteed 5-star from a pool) |
| Uma Musume | low single digits for the top rarity (verify) | Exchange ("spark") after 200 pulls on a banner | Exchange picks the featured unit | The exchange itself |
| Hearthstone | per-pack rarity guarantees | A Legendary within 40 packs of a set (announced 2017) | n/a | Dust crafting |
| Raid: Shadow Legends | published per shard type | "Mercy" increments after dry streaks (verify) | Event-boosted rates | Fusions, event champions |
| Pokémon TCG Pocket | per-slot rarity odds (published in-game) | Pack points exchangeable for specific cards | n/a | Pack points, trading (restricted) |
| Marvel Snap | n/a (no random packs; unlock systems vary) | Collection track, tokens, featured caches | Featured card in caches | Token shop |

### 16.3 Gacha maths with worked examples

```
No pity, rate p:            E[pulls] = 1/p          P(≥1 in n) = 1 − (1 − p)^n
Hard pity at N:             E[pulls] = (1 − (1 − p)^N) / p
Featured with 50/50 + guarantee:   E[featured] ≈ 1.5 × E[pulls per top-rarity]   worst case = 2N
Rising-rate pity:           simulate: p_k = base for k ≤ K, then min(1, base + step·(k − K)), with K = soft-pity-start − 1
```

| Example | Result | How to reproduce |
|---|---|---|
| Fixed 0.8% featured rate, no pity (FGO-like) | E = 125 pulls. P(within 100) = 55%. P(within 330) = 93%. A 330 guarantee touches only the unluckiest ~7% but removes the unbounded tail. | `gacha_calc.py --rate 0.008 --pulls 330 --json` |
| 0.6% with hard pity 90 only | E ≈ 69.7 pulls | `gacha_calc.py --rate 0.006 --hard-pity 90 --json` |
| 0.6% with soft pity from 74 (+6%/pull, community model) | E ≈ 62 pulls. Only about 36% of top-rarity results arrive before pull 74. Featured ≈ 93 pulls on average, 180 worst case. | `gacha_calc.py --rate 0.006 --soft-pity-start 74 --soft-pity-step 0.06 --hard-pity 90 --rate-up 0.5 --guarantee --json` |
| 2% with +2% per pull after 50 (Arknights-like) | E ≈ 34.6 pulls. About 64% arrive within the first 50. | `gacha_calc.py --rate 0.02 --soft-pity-start 51 --soft-pity-step 0.02 --hard-pity 99 --json` |
| Spark exchange at 200 (Uma-like) | A hard ceiling of 200 pulls for a specific featured unit, whatever the rates | Model as `--hard-pity 200` for the featured unit |

All scripts are `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gacha_calc.py ...` (flags as in the shared CLI contract). Results above were computed for this file under the stated models. They describe the models, not guaranteed live behaviour.

**Cost of the worst case.** `worst_case_cost = worst_case_pulls × currency_per_pull ÷ currency_per_dollar_at_your_price_tier`. Publish this number to yourself before launch. If it would embarrass you in a press article, change the rates or the pity.

### 16.4 Stamina economies: size the cap to the check-in rhythm

```
daily_regen = 1440 / minutes_per_point
hours_to_cap = cap × minutes_per_point / 60
waste_fraction(check-in interval I hours) = max(0, I − hours_to_cap) / I
```

| Case | Regeneration (verify) | Daily regen | Note |
|---|---|---|---|
| Genshin Impact (resin) | 1 per 8 min | 180 | At the original 160 cap, the cap fills in about 21.3 h, so a once-a-day player wastes about 11% |
| Arknights (sanity) | 1 per 6 min | 240 | Cap grows with player level |
| Fate/Grand Order (AP) | 1 per 5 min | 288 | Cap grows with master level |

**Rule of thumb.** Size the cap to about 20–24 hours of regeneration so a daily player loses little, and add overflow storage (as Honkai: Star Rail does) if you want to forgive missed days. Record it as an `energy` currency with a numeric `cap` in `contract.economy.currencies`, and test hoarding with `economy_sim.py`.

### 16.5 What you sell, and what it costs you

| What is sold | Cases | Revenue depth | Fairness and ethics cost | Required protection |
|---|---|---|---|---|
| Power in PvE | Genshin, Star Rail, FGO, Arknights | High | Low in PvE; power creep risk | Endgame rotation; content beatable without the newest unit |
| Power in PvP | Raid, Summoners War, AFK Arena (arena) | High | Pay-to-win perception | Brackets, draft modes, level normalisation |
| Collection access | Hearthstone, Marvel Snap, TCG Pocket | Medium–high | Scarcity anger, cost of keeping up | Crafting or token paths; published pity |
| Cosmetics | Marvel Snap upgrades, skins everywhere | Medium | Low | Avoid random-only cosmetics for minors |
| Time and convenience | Stamina refills, fast rewards, timer skips | Medium | Moderate (sells impatience) | Caps that suit daily play; free daily ration |
| Storage | Pokémon GO, Puzzle & Dragons | Low–medium | Low but irritating | Generous base storage |

### 16.6 Ethics and regulation checklist for any random-reward system

- [ ] Odds for every tier shown before purchase (an Apple and Google requirement), with the pity and guarantee rules in plain language and a visible pity counter.
- [ ] The worst-case cost to guarantee a featured item is computed and acceptable (16.3).
- [ ] A deterministic path exists (exchange, crafting, pack points, spark).
- [ ] Paid random items are disabled or age-gated where the law requires it (for example Belgium, and under-18s in Brazil from March 2026). Australian ratings (M or above for paid chance items) are planned for. See section 17.
- [ ] No "complete the set of random items to win a prize" mechanics. Japan ruled this "kompu gacha" pattern unlawful under its premiums law in 2012 (widely reported; verify).
- [ ] Spending limits and parental controls for minors; no countdown or streak pressure aimed at minors.
- [ ] No fake scarcity: rerun policy for limited units published or consistent.
- [ ] Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/compliance_preflight.py --project . --platform all --json` and review with `arcosian:compliance-officer`. Depth lives in `legal-ethics` and `monetization`.

### 16.7 Procedure: designing a collection and gacha system

1. **Decide what is sold** (16.5) and in which context (PvE, PvP, collection). Write it in `contract.monetization.ethics`.
2. **Choose the acquisition mix**: a free daily ration, a deterministic path and a random path. Every case that kept player trust had at least two.
3. **Set rates and pity.** Compute the mean and worst case (16.3) and the cost of the worst case.
4. **Compute free-player income per content cycle.** Illustrative: earning 100 premium units a day plus 1,200 from events in a 42-day version, at 160 units per pull, gives (100 × 42 + 1,200) / 160 ≈ 34 pulls per version. With an average of about 93 pulls per featured unit, a free player gets a featured unit roughly every three versions. Decide whether that is the experience you want.
5. **Define duplicate value**: power (Constellations, limit breaks), exchange currency (Starglitter, certificates) or cosmetics (Snap upgrades). Duplicate rules decide how deep the whales go.
6. **Size stamina** (16.4) and choose auto or skip features for solved content (Arknights auto-replay, Star Rail auto-battle).
7. **Set a power-creep policy**: rotate endgame modes, keep older units relevant through unique mechanics (Arknights) or synergy (Genshin).
8. **Run the ethics checklist** (16.6).
9. **Encode and simulate**: currencies in `contract.economy.currencies`, offers in `contract.monetization.iap`, an economy model in `economy-model.schema.json`, then `economy_sim.py --model PATH --runs 200 --seed 1 --json`.

### 16.8 Lineage timeline

```
2012  Puzzle & Dragons: puzzle combat + monster gacha + friend helpers. Japan rules against "kompu gacha".
2013  Monster Strike: physics slingshot + local co-op on phones.
2014  Summoners War: rune optimisation chase.  Hearthstone: digital-native CCG + crafting.
2015  Fate/Grand Order: story- and IP-led gacha with friend supports.
2016  Pokémon GO: real-world movement as the core loop.
2018–19  Raid: Shadow Legends (3D collector, saturation UA); AFK Arena (premium-art idle RPG); Arknights (TD gacha).
2020  Genshin Impact: open-world gacha; pity and the 50/50 understood globally.
2021  Uma Musume: roguelite training run + support-card deck.
2022  Marvel Snap: 3-minute CCG with a stakes bet and cosmetic upgrades.
2023  Honkai: Star Rail: turn-based gacha with time respect as a feature.
2023–24  Legend of Mushroom: gear-draw idle RPG.
2024  Pokémon TCG Pocket: pack opening as the core ritual.
```

### 16.9 Where to go deeper

- Genre norms: `skills/genre-playbooks/references/rpg-gacha.md` and `skills/genre-playbooks/references/idle-tycoon-sim.md` (`genre-playbooks`).
- Random-reward mechanics and pity patterns as mechanic cards: `skills/mechanics-codex/references/07-randomness-chance-mechanics.md` (`mechanics-codex`).
- Currency architecture and sinks: `economy-design`. Offers, banners and ethics: `monetization`. Version cadence and events: `liveops`.
- Attachment, FOMO and their limits: `player-psychology`. Loot-box law, minors and odds disclosure: `legal-ethics`.

## 17. Volatile facts (as of Oct 2026 — verify before relying)

- [V1] Loot-box rules: Belgium banned paid loot boxes under gambling law in 2018 (fines up to €800k); Dutch enforcement was reversed by the courts; Australia rates games with paid chance-based items classified after Sep 22, 2024 at least M, and simulated gambling R18+; Brazil's ECA Digital bans loot-box sales to under-18s from March 2026, and a Brazilian court ordered Riot Games to pay damages and add age verification and odds disclosure in June 2026; an EU-wide approach under a Digital Fairness Act is reportedly not expected before 2028. Sources: [Programming Insider](https://programminginsider.com/loot-boxes-regulation-and-where-the-line-sits-in-2026/), [PCWorld](https://www.pcworld.com/article/2464538/all-games-with-loot-boxes-will-be-rated-m-or-higher-in-australia.html), [Sheep Esports](https://www.sheepesports.com/articles/brazil-court-orders-riot-games-to-pay-eur2-5m-over-league-of-legends-loot-boxes/en).
- [V2] Apple (App Review Guideline 3.1.1) and Google Play require disclosure of the odds for randomized paid items before purchase. Source: [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/).
- [V3] The amended US COPPA Rule had a compliance deadline of Apr 22, 2026, expanding personal information (including biometrics) and tightening third-party and mixed-audience duties. This matters for collection games with young audiences. Sources: [Toy Association](https://toyassociation.org/PressRoom2/News/2026-News/updated-coppa-rule-requirements-take-effect-april-22.aspx), [Loeb & Loeb](https://www.loeb.com/fr/insights/publications/2025/05/childrens-online-privacy-in-2025-the-amended-coppa-rule).
- [V4] US state app-store age-verification laws took effect in Texas (Jan 1, 2026), Utah (May 7, 2026) and Louisiana (Jul 1, 2026). Apple provides a Declared Age Range API. Sources: [9to5Mac](https://9to5mac.com/2025/11/04/app-store-texas-sb2420-new-apis/), [PocketGamer.biz](https://www.pocketgamer.biz/texas-enforces-new-age-verification-law-for-app-stores-and-developers).
- [V5] From Oct 1, 2026, Apple's EU rules bar link-outs in Kids-category and under-13 apps and require a parental gate for under-18 apps using alternative payments or link-outs. Source: [Apple Newsroom](https://www.apple.com/newsroom/2026/08/apple-announces-changes-for-apps-in-the-european-union/).
- [V6] Mobile game IAP revenue was about $82B in 2025 (+1%), with growth attributed to live-ops, events and IP collaborations. H1 2026 IAP was $40B (−2% year on year). Sources: [Sensor Tower press release](https://sensortower.com/press/press-release-sensor-tower-state-of-gaming-gaming-drove-52-billion-downloads-82b-iap-revenue-on-mobile-and-12b-premium-revenue-on-steam), [Mobilegamer.biz data digest](https://mobilegamer.biz/data-digest-sensor-towers-h1-analysis-hay-days-comeback-julys-top-games-big-krafton-numbers-and-more/).
- [V7] In mature markets (US, Canada, Korea, Japan), IAP is reported at 77–90% of mobile game revenue, which is why the cases here are IAP-led. Source: [GameDev Reports summary of Sensor Tower](https://gamedevreports.substack.com/p/sensor-tower-mobile-game-ad-monetization).
- [V8] Retention benchmarks (GameAnalytics data via secondary write-ups): median D1 about 22%, D7 just under 4%, D30 about 0.7–0.8%, top 1% at 64–68% D1. Use these as context, not as targets for a gacha RPG. Sources: [Segwise](https://segwise.ai/blog/mobile-gaming-app-user-retention-strategies), [Playio](https://blog.playio.co/d1-d7-d30-retention-benchmarks-2026).
- [V9] Checked on 2026-10-20: Uma Musume's Japan and global release dates ([Wikipedia](https://en.wikipedia.org/wiki/Umamusume:_Pretty_Derby)); Legend of Mushroom's publisher entity and first App Store release ([App Store metadata](https://itunes.apple.com/search?term=legend+of+mushroom&entity=software&country=us&limit=5)); the Niantic-to-Scopely deal ([Savvy Games Group](https://savvygames.com/news/scopely-to-acquire-niantics-games-business)); the FTC settlement with HoYoverse (Genshin Impact) of January 2025: a $20 million civil penalty, a bar on selling loot boxes to under-16s without a parent's affirmative express consent, and required disclosure of odds and virtual-currency exchange rates ([FTC press release](https://www.ftc.gov/news-events/news/press-releases/2025/01/genshin-impact-game-developer-will-be-banned-selling-lootboxes-teens-under-16-without-parental)).
- Gacha rates, pity values, stamina regeneration and caps quoted in this file come from in-game disclosures and community documentation and are retuned between versions. Publishing changes at Marvel Snap and other regional release dates come from widely circulated press coverage and were not re-checked. Verify all of them before external use.
