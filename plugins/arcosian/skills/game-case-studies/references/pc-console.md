# PC and console case studies

Fifteen deconstructions of games built for PC and console first: a metroidvania, three systems sims, a survival sandbox, an open-world action RPG and a party-sized narrative RPG, a co-op shooter, a co-op horror game, a sports-style car game, a fighting game, a strategy game, a battle royale and platform, an MMO and an open-world racer. They span premium, early access, free-to-play, subscription and live-service models, and teams from one person to hundreds. Read them for what mobile cases rarely teach: **how a PC game grows in public** (early access, mods, free updates), **how one game ships on four platforms** (ports, certification, controllers, Steam Deck), and **how a long-lived service keeps a console-sized audience**. Each case uses the 16-lens format from `SKILL.md`, compressed to one line where a lens is thin, plus a **Platform notes** subsection. Where a game has no live economy, the Economy lens says so and the ontology uses `progression.tracks`. Sales, player counts and team sizes cite the source keys in section 17 ([V1]–[V15]); where only a press estimate exists it is labelled "estimate". Wikipedia figures are grade C unless they quote a company statement (see the grade table in `SKILL.md`). Anything marked "verify" was not confirmed.

**Contents.** Sections 1–15 are case studies (index below). Section 16 is a cross-case synthesis with decision tables and checklists. Section 17 lists volatile facts with sources.

| # | Game | Genre | Year | Model | Key lesson |
|---|---|---|---|---|---|
| 1 | Hollow Knight | metroidvania | 2017 | premium, free DLC | A small team can ship a huge, hand-made world if the map teaches itself and updates stay free |
| 2 | Factorio | factory sim | 2016 EA / 2020 | early access, then premium | A deterministic simulation, one rule of throughput and a mod API sell a decade of hours |
| 3 | RimWorld | colony sim | 2013 alpha / 2018 | funded, early access, premium + DLC | A story generator sitting on a needs sim makes the player the author |
| 4 | Valheim | survival sandbox | 2021 EA | early access, cheap | A tiny team, a fresh survival progression and co-op with friends can sell millions in a month |
| 5 | Baldur's Gate 3 | narrative CRPG | 2020 EA / 2023 | premium, early access first | Reactive authored content on a known ruleset beats feature count |
| 6 | Elden Ring | open-world soulslike | 2022 | premium + one big expansion | Optional, readable difficulty in an open world widens a hardcore audience |
| 7 | Helldivers 2 | co-op shooter, live service | 2024 | premium + earnable battle pass | Friendly fire, shared stakes and a community-wide war make co-op a story |
| 8 | Lethal Company | co-op horror | 2023 EA | early access, $10 | Proximity voice chat and a quota loop turn a solo dev's game into streamer content |
| 9 | Rocket League | car soccer | 2015 | premium, then free-to-play | One readable rule plus a physics skill ceiling; crossplay and cosmetics as the live model |
| 10 | Street Fighter 6 | fighting | 2023 | premium + season DLC | Layered control schemes and a big offline mode widen a genre that bleeds newcomers |
| 11 | Cities: Skylines | city builder | 2015 | premium + DLC + mods | Fill the gap a franchise leaves, and let mods carry the long tail |
| 12 | Civilization VI | 4X strategy | 2016 | premium + expansions | A long-running franchise's design bets (districts, boosts) and its ports |
| 13 | Fortnite | battle royale and platform | 2017 | free-to-play, battle pass, creator economy | A fast-follow on a trend plus builds, seasons and a platform pivot |
| 14 | Final Fantasy XIV | MMORPG | 2010 / 2013 relaunch | subscription | A failed launch rebuilt around a subscription, a producer-led roadmap and a free trial |
| 15 | Forza Horizon 5 | open-world racing | 2021 | premium + subscription catalogue | A catalogue-led first-party release; the PC and PS5 ports extend the tail |

---

## 1. Hollow Knight

**Snapshot**
- Developer: Team Cherry (Adelaide, Australia). The Wikipedia article names two directors (Ari Gibson, William Pellen), two programmers, and a composer; a small team throughout [V4].
- Funding and release: Kickstarter in late 2014 (goal A$35,000, raised more than A$57,000 from 2,158 backers). Windows 24 February 2017, Switch June 2018, PS4 and Xbox One September 2018, PS5 and Xbox Series X/S and Switch 2 in February 2026. Built in Unity [V4].
- Genre: metroidvania. Model: premium, with four free content updates (Hidden Dreams, The Grimm Troupe, Lifeblood, Godmaster) [V4].
- Scale: 2.8 million sold by February 2019 and about 15 million by August 2025, as told to Bloomberg (company statement, via press) [V4]. *Silksong* launched 4 September 2025 and Steam peak figures of roughly 535,000 to 587,000 concurrent were reported, depending on the source and time [V4].

**Core loop**
1. Explore an interconnected, unmarked map; fight with a nail strike and a small set of spells.
2. Striking enemies fills Soul, which powers Focus (healing) and spells, so offence funds defence.
3. Die and lose your Geo (currency) to a Shade you must recover.
4. Find a bench (save point), buy a map from a cartographer, equip charms.
5. New abilities open old areas; bosses gate story and abilities.

**Meta and progression**: ability gating (movement upgrades), charm slots (a build system with a notch budget), nail and mask upgrades. No levels or XP.
**Economy**: Geo is a soft currency with a death penalty (a recoverable Shade); charms cost notches (a fixed budget). No real-money economy.
**Monetization**: one premium price; free updates; later paid expansion in the sequel. **Live-ops**: free updates as the post-launch retention tool; no live service. **Retention hooks**: hidden secrets, optional bosses, a 112 per cent completion list, speedrunning. **Social layer**: none in-game; a large wiki, speedrun and fan-art community.

**UX and onboarding notables**: almost no tutorial text; signs are sparse and the world teaches by layout. Getting lost is part of the design, with map-buying as an in-fiction aid.
**Art and audio identity**: hand-drawn monochrome insects with a melancholy orchestral score; the style carried the marketing.
**Psychology principles used**: exploration drive; loss aversion (the Shade); competence from fair boss patterns; Zeigarnik effect from unreachable doors.
**Innovations**: the Soul-for-healing loop ties offence to survival; a recovery-on-death mechanic with narrative flavour; a huge hand-drawn map for a tiny team.
**Weaknesses and criticism**: a few areas are punishing and navigation can be obscure; some players lean on external maps; a long wait for the sequel shaped fan expectations.

**Lessons for designers**
1. Teach by space: put each new ability's lock early and its key late.
2. Free post-launch updates grow word of mouth for a premium game without a live team.
3. A small team can scope an authored metroidvania when art style is cheap to reuse (a limited palette, a hand-drawn look).
4. Give death a cost the player can undo (the Shade) so that failure creates a short mission.

**Analogy hooks**: Soul-for-healing → any action game where offence heals (health-on-hit tradeoffs). Charm notches → build budgets in roguelites. Locked-door map → open-world dungeon design.

**Platform notes**: PC first, then Switch (portable play suited the genre), then a combined PS4 and Xbox One edition, then 2026 current-generation and Switch 2 editions [V4]. Controller-first input in all versions. Steam Deck status: verify on the store page.

**Ontology encoding**
```json
{"loops": [
  {"id": "hk_core", "type": "core", "period": "seconds", "steps": [
    {"id": "c1", "action": "strike_enemies", "reward": "soul", "next": "c2"},
    {"id": "c2", "action": "focus_heal_or_cast", "reward": "survive_or_damage", "next": "c1"}]},
  {"id": "hk_meta", "type": "meta", "period": "session", "steps": [
    {"id": "m1", "action": "explore_new_area", "reward": "geo_and_unlock", "next": "m2"},
    {"id": "m2", "action": "gain_ability_open_old_gate", "reward": "new_route", "next": "m1"}]}],
 "progression": {"tracks": [{"id": "abilities", "gated_by": "bosses"}, {"id": "charms", "gated_by": "notch_budget"}]}}
```

## 2. Factorio

**Snapshot**
- Developer: Wube Software (Prague). Funded by a 2013 Indiegogo campaign (€21,626 raised against a €17,000 goal), early access on Steam 25 February 2016, 1.0 on 14 August 2020, expansion *Space Age* 21 October 2024 [V5].
- Scale: 3.5 million copies by December 2022 (developer statement); *Space Age* passed 400,000 copies shortly after launch with a Steam peak of 118,674 concurrent players (Wube Friday Facts, via GamingOnLinux) [V5]. Team of 31 as of February 2024 [V5].
- Genre: factory automation sim. Model: early access, then premium with a paid expansion; no microtransactions.

**Core loop**
1. Mine raw resources by hand, then place miners and furnaces.
2. Build belts and assemblers to turn ore into science packs.
3. Research technologies that unlock new recipes and machines.
4. Defend against enemy "biters" whose aggression grows with pollution.
5. Redesign the factory to hit a throughput target; scale until a launch or a megabase.

**Meta and progression**: a technology tree and planets (in *Space Age*); no player levels. Maps are seeds with map-gen settings.
**Economy**: a pure production economy (items per second); no currency. Resource patches deplete, which forces expansion.
**Monetization**: a single price with no discounts for years (reported by a Czech outlet; verify) and one paid expansion. **Live-ops**: weekly developer blog "Friday Facts" built a community; updates arrived on a patch cadence. **Retention hooks**: the "one more improvement" loop; modding; multiplayer factories. **Social layer**: co-op and servers (player-hosted and dedicated); strong mod community [V5].

**UX and onboarding notables**: a tutorial campaign plus an in-game hint system; a blueprint library, copy-paste and ghost building make large designs possible. Performance (updates per second) is treated as a feature.
**Art and audio identity**: dense, readable industrial pixel art and ambient music; clear silhouettes at zoom.
**Psychology principles used**: flow and the Zeigarnik effect (always something half-built); autonomy; mastery by optimisation.
**Innovations**: deterministic lockstep multiplayer for a heavy simulation; the throughput-per-second unit as the core metric; first-party mod support with a mod manager.
**Weaknesses and criticism**: a steep early curve and a time sink; late-game base size strains performance; the genre is hard to explain in a trailer.

**Lessons for designers**
1. Pick one number the player optimises (items per second) and make every system feed it.
2. Engineering quality (determinism, UPS) is a design feature, not back-end work.
3. Open a dev blog on a regular cadence; it converts early access into community.
4. Price once and hold it; a game with a long tail does not need discounts to sell.

**Analogy hooks**: throughput target → any logistics or restaurant sim. Pollution-driven enemy aggression → a growth-pressure clock in a builder. Blueprints → shareable level or build data.

**Platform notes**: PC first (Windows, macOS, Linux). Switch version 28 October 2022 without mods or *Space Age*; a Switch 2 edition followed 22 December 2025 with *Space Age* [V5]. Controller input is a major redesign for a mouse-driven game; the console editions are the cases to study.

**Ontology encoding**
```json
{"loops": [
  {"id": "fac_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "build_production_line", "reward": "items_per_second", "next": "c2"},
    {"id": "c2", "action": "feed_science_research", "reward": "new_tech", "next": "c3"},
    {"id": "c3", "action": "defend_and_expand", "reward": "new_resources", "next": "c1"}]}],
 "progression": {"tracks": [{"id": "tech_tree", "gated_by": "science_packs"}]}}
```

## 3. RimWorld

**Snapshot**
- Developer: Ludeon Studios; designer Tynan Sylvester. Kickstarter launched 2 October 2013 (raised CA$268,132), first alpha 4 November 2013, beta November 2017, 1.0 on 17 October 2018 [V6].
- DLC: *Royalty* (24 February 2020), *Ideology* (20 July 2021), *Biotech* (21 October 2022), *Anomaly* (11 April 2024), *Odyssey* (11 July 2025). Console edition on PS4 and Xbox One 29 July 2022 (by Double Eleven) [V6].
- Scale: over one million sold by February 2018; an estimate of over $100 million revenue by August 2020 (Wikipedia, citing estimates) [V6].
- Genre: colony sim with a story generator. Model: crowdfunded, early access, premium plus paid expansions.

**Core loop**
1. Manage a small colony of settlers with traits, needs and moods.
2. Assign work priorities; build, farm, research and fight.
3. A "storyteller" AI (presets such as Cassandra Classic, Phoebe Chillax, Randy Random) picks events based on a difficulty curve [V6].
4. Events (raids, weather, a wandering stranger) test the colony, and moods turn into stories (a mental break, a love affair, a feud).
5. Survive, escape on a ship or collapse; replay with a new scenario.

**Meta and progression**: no persistent meta; the colony is the run. DLC adds systems (factions, memes, genes, anomalies).
**Economy**: a resource and wealth economy; colony wealth raises raid strength, which acts as a built-in difficulty curve.
**Monetization**: premium base game plus four or five DLC priced as expansions; a modding community on the Steam Workshop is part of the product [V6]. **Live-ops**: patch updates and a few big DLC per cycle. **Retention hooks**: emergent stories players retell; mods; scenario variety. **Social layer**: none in the game; huge forum and video culture.

**UX and onboarding notables**: dense but legible UI of pawn cards and work-priority grids; the tutorial is short and the learning is by failure.
**Art and audio identity**: simple, readable top-down sprites and a spare Western-sci-fi score; the simple art lets mods add content cheaply.
**Psychology principles used**: narrative transportation; sunk-cost attachment to named characters; variable events (intermittent reinforcement).
**Innovations**: the storyteller as a design pattern (event director with difficulty personalities); a needs-and-mood simulation tuned to produce drama rather than efficiency.
**Weaknesses and criticism**: late-game slowdowns with large colonies and heavy mod lists; the UI can overwhelm new players; DLC bundling is debated.

**Lessons for designers**
1. A simulation produces stories when systems collide: name them, track them and show them.
2. An event director with named personalities lets players tune their own difficulty.
3. Early access with a funded alpha builds a base before launch.
4. Mod support multiplies content at no cost to the developer.

**Analogy hooks**: storyteller → director AI in any survival or roguelite. Wealth-scaled raids → rubber-band difficulty in a builder. Mood breaks → any sim where needs create plot.

**Platform notes**: PC (Windows, macOS, Linux) first. The console edition arrived four years after the 1.0 and was built by an outside studio; the PC mod ecosystem does not carry over, which narrows the console value [V6].

**Ontology encoding**
```json
{"loops": [
  {"id": "rw_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "assign_work_and_build", "reward": "colony_growth", "next": "c2"},
    {"id": "c2", "action": "respond_to_storyteller_event", "reward": "story_or_loss", "next": "c1"}]}],
 "progression": {"tracks": [{"id": "colony_wealth", "gated_by": "raid_scaling"}]}}
```

## 4. Valheim

**Snapshot**
- Developer: Iron Gate (Sweden), published by Coffee Stain Publishing. Early access 2 February 2021. A five-person team at launch [V7].
- Scale: over five million sold in about a month; more than ten million by April 2022; 12 million as of September 2023 (Embracer AGM, via Game Developer) [V7].
- Platforms: Windows and Linux first; Xbox early access 14 March 2023; macOS June 2024; Wikipedia lists a full release with PS5 and Switch 2 on 9 September 2026 (verify) [V7].
- Genre: Norse co-op survival sandbox. Model: early access with a low price (the price is not in the sources used; check the store).

**Core loop**
1. Gather wood, stone and food; build a base; defend against raids.
2. Craft better gear at stations that must be upgraded with nearby structures.
3. Sail or explore biomes for the materials of the next tier.
4. Defeat a boss to unlock the next biome's tier of gear.
5. Repeat for the next biome; each new biome resets the player to "new".

**Meta and progression**: a biome ladder with a boss per tier; skills that rise by use; a world seed shared by a group.
**Economy**: a materials-and-tiers economy; carry weight and durability act as friction; death loses gear until recovered. No currency.
**Monetization**: a single low price in early access; no microtransactions in the sources checked. **Live-ops**: content updates in named seasons (verify the cadence). **Retention hooks**: boss-gated tiers; building showcases; friend groups. **Social layer**: co-op for up to ten players (verify) on dedicated or hosted servers.

**UX and onboarding notables**: no tutorial; stations announce their requirements; the death-run (retrieve your corpse) is a deliberate tension spike.
**Art and audio identity**: a low-poly, lit look with strong atmospheric lighting and Nordic music; modest assets give a distinctive mood.
**Psychology principles used**: mastery by incremental tiers; social proof from friends' bases; loss aversion at death.
**Innovations**: the station-upgrade rule (build around the bench), a sailing system and a build system that rewards architecture, in a small team's scope.
**Weaknesses and criticism**: content ran out for many players after the launch wave; combat depth is modest; the release schedule is slow after a huge launch.

**Lessons for designers**
1. A familiar genre (survival) with a clear fresh frame (a Norse tier ladder) can launch big at a low price.
2. Bosses as unlock gates give co-op groups a shared goal.
3. In early access, plan the content roadmap before the sales spike, since the audience arrives first and expects more.
4. Price low enough to be a group purchase: friends buy together.

**Analogy hooks**: station requirements → crafting trees in any builder. Boss gates → tier unlocks in an MMO or roguelite. Group pricing → co-op games on Steam.

**Platform notes**: PC first; the Xbox early access came two years later with crossplay planned (final status: verify). Linux support was there from the first day, which Steam Deck players use [V7].

**Ontology encoding**
```json
{"loops": [
  {"id": "val_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "gather_and_build", "reward": "materials_and_base", "next": "c2"},
    {"id": "c2", "action": "defeat_biome_boss", "reward": "next_tier_unlock", "next": "c1"}]}],
 "progression": {"tracks": [{"id": "biome_tiers", "gated_by": "bosses"}]}}
```

## 5. Baldur's Gate 3

**Snapshot**
- Developer and publisher: Larian Studios. Early access in 2020 (act one; the article gives August and October inconsistently); full release on Windows 3 August 2023, PS5 6 September 2023, macOS 22 September 2023, Xbox Series X/S 7 December 2023, Linux 23 September 2025 [V3].
- Team and budget: Larian grew from about 140 people in 2017 to over 450 in 2023; about six years of development; budget not stated [V3].
- Scale: over 2.5 million players in early access; over 10 million by February 2024; about 15 million copies by a November 2024 report and over 20 million by the end of 2025 (press reports, not audited) [V3]. Won Game of the Year at the five major ceremonies (April 2024) [V3].
- Genre: narrative CRPG on Dungeons and Dragons 5e rules. Model: premium with an early access period.

**Core loop**
1. Explore a scene, talk to characters and choose how to solve a problem (fight, talk, sneak, throw).
2. Turn-based combat with positioning, terrain and elements (grease plus fire).
3. Rest at camp; party companions react and trigger personal quests.
4. Choices change later scenes, which are reactive to what you did.
5. Level up and re-spec; finish the act; repeat across three acts.

**Meta and progression**: character levels, subclasses and gear; companion approval and story arcs. A New Game Plus mode is not confirmed here.
**Economy**: a gold and loot economy with rest-limited resources (long rests, camp supplies). No live economy.
**Monetization**: one price; free patches and content updates; Hasbro reported a $90 million income from the game in a Q4 2023 call [V3]. **Live-ops**: eight patches, ending with a final patch in April 2025 that added subclasses, photo mode, crossplay and Xbox Series S split-screen [V3]. **Retention hooks**: replays with different classes and choices; mods (mod support added September 2023; mods disable achievements) [V3]. **Social layer**: online and local co-op; crossplay arrived in 2025 [V3].

**UX and onboarding notables**: a reactive world with many solutions; save anywhere and quick-load make experiments cheap. The dense rules UI is the main barrier.
**Art and audio identity**: motion-captured performances and a film-grade score; the characters sell the game.
**Psychology principles used**: autonomy through multiple solutions; relatedness with companions; consequence and regret that invite replay.
**Innovations**: systemic combat (surfaces and verticality) joined with authored reactivity at scale; four-player co-op through a story CRPG.
**Weaknesses and criticism**: the third act was reported as rushed or buggy in places; a heavy rules UI; the scale of authored branches cost years.

**Lessons for designers**
1. Reactive content is the product: budget for branches and test paths with a tool, not with hope.
2. Early access can fund and shape an authored game (two and a half million players).
3. Support every platform's co-op features: split-screen and crossplay were added later and welcomed.
4. Free post-launch patches, then a clear final patch, set expectations.

**Analogy hooks**: surface elements → any physics-driven combat. Companion approval → relationship systems in narrative games. Early-access acts → episodic release for authored content.

**Platform notes**: PC first, PS5 a month later, macOS, and Xbox Series X/S later (the Series S needed split-screen work, finished in April 2025) [V3]. A Linux build optimised for Steam Deck came in September 2025 [V3]. The long gap on Xbox shows the cost of the console split-screen requirement.

**Ontology encoding**
```json
{"loops": [
  {"id": "bg3_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "choose_solution_fight_talk_sneak", "reward": "consequence", "next": "c2"},
    {"id": "c2", "action": "tactical_turn_combat", "reward": "xp_and_loot", "next": "c3"},
    {"id": "c3", "action": "camp_and_companion_scene", "reward": "approval_and_quest", "next": "c1"}]}],
 "progression": {"tracks": [{"id": "character_level", "gated_by": "xp"}, {"id": "companion_arcs", "gated_by": "approval"}]}}
```

## 6. Elden Ring

**Snapshot**
- Developer: FromSoftware; published by Bandai Namco. Director Hidetaka Miyazaki; worldbuilding by George R. R. Martin [V2].
- Release: 25 February 2022 on PS4, PS5, Windows, Xbox One and Xbox Series X/S; *Shadow of the Erdtree* expansion 20 June 2024; Switch 2 version (*Tarnished Edition*) 28 August 2026 [V2].
- Scale: 12 million in 18 days (company statement); 13.4 million by March 2022; 30 million by April 2025; the expansion reportedly sold over 10 million [V2]. Steam concurrent peak 953,426 (SteamDB, via Automaton) [V2].
- Genre: open-world action RPG, soulslike. Model: premium plus one large paid expansion.

**Core loop**
1. Explore an open field with legacy dungeons, caves and bosses.
2. Fight with stamina-based melee, magic or ranged builds; dodge and parry.
3. Die, lose runes at the spot, retrieve them.
4. Spend runes at sites of grace to level; upgrade weapons.
5. Beat or skip bosses; the world allows many orders.

**Meta and progression**: levels (attribute points), gear upgrades, spirit summons, Ashes of War (weapon skills). Difficulty is controlled by build and by skipping areas.
**Economy**: runes (XP and currency in one); a death cost that can be reclaimed.
**Monetization**: one price plus a paid expansion. **Live-ops**: patches, no seasons. **Retention hooks**: builds, secrets, lore, challenge runs, co-op. **Social layer**: asynchronous messages and bloodstains, summon signs for co-op, duels and invasions [V2].

**UX and onboarding notables**: no quest log pointers; a golden trail suggests direction (a subtle guide); a horse and fast travel handle size.
**Art and audio identity**: a painterly high-fantasy decay and a cinematic orchestral score; large silhouettes make landmarks readable.
**Psychology principles used**: curiosity from the visible far landmark; mastery via learnable patterns; the rune-retrieval risk-reward loop.
**Innovations**: a Souls-like in a field where the player can leave a wall boss to return later; the horse and open world widen access without removing challenge.
**Weaknesses and criticism**: PC launch performance problems were widely reported [V2]; a late-game balance tail and some difficulty spikes in the expansion.

**Lessons for designers**
1. Optionality is the accessibility tool: let players walk away from a wall and return stronger.
2. A recoverable death cost keeps the tension and removes the fear.
3. Async multiplayer (messages and ghosts) adds social warmth with no matchmaking cost.
4. Ship a large paid expansion for the engaged core.

**Analogy hooks**: walk-away difficulty → open-world RPGs, metroidvanias. Rune retrieval → any run-based game with a death penalty. Message system → asynchronous hints in a puzzle or horror game.

**Platform notes**: launched on five platforms at once, with a mixed PC performance reception at launch [V2]. The game was reported as Steam Deck Verified at launch (NME); check the store page for the current status. The Switch 2 edition came four years later [V2].

**Ontology encoding**
```json
{"loops": [
  {"id": "er_core", "type": "core", "period": "seconds", "steps": [
    {"id": "c1", "action": "dodge_and_strike", "reward": "runes", "next": "c2"},
    {"id": "c2", "action": "die_or_win", "reward": "runes_kept_or_dropped", "next": "c1"}]},
  {"id": "er_meta", "type": "meta", "period": "session", "steps": [
    {"id": "m1", "action": "rest_at_grace_level_up", "reward": "stronger_build", "next": "m2"},
    {"id": "m2", "action": "explore_or_skip_boss", "reward": "new_area", "next": "m1"}]}],
 "economy": {"currencies": [{"id": "runes", "kind": "material", "sources": ["kills"], "sinks": ["levels", "upgrades"], "cap": null}]}}
```

## 7. Helldivers 2

**Snapshot**
- Developer: Arrowhead Game Studios (Sweden); publisher Sony Interactive Entertainment. Released 8 February 2024 on PS5 and Windows; Xbox Series X/S on 26 August 2025 (ported by Nixxes) [V1]. Team headcount: not sourced.
- Scale: about 1 million in three days, 12 million by 5 May 2024 (Sony: the fastest-selling PlayStation game to that point), over 15 million by November 2024, and over 19 million by October 2025 (12.6 million Steam, 5.4 million PS5, 1.4 million Xbox); Wikipedia reports over 20 million and over $700 million revenue by January 2026 [V1]. Steam peak about 450,000 concurrent in March 2024 [V1].
- Genre: co-op third-person shooter, live service. Model: premium plus an earnable battle pass.

**Core loop**
1. Pick a planet in the shared Galactic War and a mission difficulty.
2. Drop with up to three others; complete objectives against bugs, robots or Illuminate.
3. Call stratagems (airstrikes, supplies) by entering directional codes; friendly fire is on.
4. Extract; earn requisition, samples and XP.
5. Spend on stratagems and Warbonds; community Major Orders move the war.

**Meta and progression**: player level (cap 50 at launch, 150 from April 2024, 300 from August 2026 per Wikipedia), ship modules, stratagem unlocks, Warbonds [V1].
**Economy**: Super Credits (hard: earned in missions and sold) buy Warbonds, which never expire; requisition and samples are soft [V1].
**Monetization**: premium purchase plus Super Credits for Warbonds and store armour; Warbonds are priced as non-expiring battle passes [V1]. **Live-ops**: Major Orders (community-wide objectives), new enemy factions, Warbonds, balance patches. **Retention hooks**: the shared war narrative, unlock chase, difficulty ladder. **Social layer**: four-player co-op with friendly fire and quick matchmaking.

**UX and onboarding notables**: stratagem input codes are the central skill; matchmaking puts players into any open drop; the tone is satirical and the tutorial short.
**Art and audio identity**: a satirical militaristic propaganda mood with grim, gritty visuals; voice lines and music sell it.
**Psychology principles used**: shared threat and cooperation; humour from friendly-fire chaos; community goals that need group action.
**Innovations**: the Galactic War as a server-wide meta-game; the stratagem code input as a skill; non-expiring Warbonds in place of a seasonal battle pass.
**Weaknesses and criticism**: the PSN account requirement for Steam players (announced 3 May 2024, dropped on 5 May 2024 after review bombing, with sales blocked in 177 territories until 14 June 2025) [V1]; balance changes and server capacity in the launch weeks.

**Lessons for designers**
1. Platform politics can be a design risk: a forced account link caused a review-bombing within days.
2. A shared world state (the war) turns each session into a contribution to a story.
3. Non-expiring passes reduce FOMO and complaints compared with a seasonal pass.
4. Capacity planning for a viral launch decides the first-month reputation (verify specifics).

**Analogy hooks**: Galactic War → server-wide events in an MMO or a persistent co-op. Friendly fire → co-op comedy and tension. Code-input abilities → rhythm-like skill inputs.

**Platform notes**: PS5 and Windows launched together under a console publisher; the PSN-linking policy on PC was reversed within days [V1]. Xbox arrived 18 months later with a separate port studio [V1]. Controller-first input; Steam Deck compatibility: verify.

**Ontology encoding**
```json
{"loops": [
  {"id": "hd_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "drop_and_complete_objectives", "reward": "xp_samples_credits", "next": "c2"},
    {"id": "c2", "action": "call_stratagems_and_extract", "reward": "mission_complete", "next": "c1"}]},
  {"id": "hd_live", "type": "liveops", "period": "daily", "steps": [
    {"id": "l1", "action": "community_major_order", "reward": "war_progress", "next": "l1"}]}],
 "economy": {"currencies": [{"id": "super_credits", "kind": "hard", "sources": ["missions", "purchase"], "sinks": ["warbonds", "store"], "cap": null}]}}
```

## 8. Lethal Company

**Snapshot**
- Developer and publisher: Zeekerss, an individual developer who previously made games on Roblox [V8]. Early access on Windows 23 October 2023 at about $10 [V8].
- Scale: sales above 10 million by January 2024 (an estimate by Push To Talk, via Wikipedia) and a Game Developer headline estimating about 10 million; peaks reported by press between roughly 100,000 and 184,000 concurrent in November 2023 (sources disagree) [V8]. A later estimate site (Raijin) gave about 12.1 million copies and $102 million gross by July 2026 (medium confidence, estimate) [V8].
- Genre: co-op first-person survival horror for up to four. Model: early access, low price.

**Core loop**
1. Fly to a moon, enter a facility, and collect scrap while avoiding monsters.
2. Use proximity voice chat and walkie-talkies; sound draws enemies.
3. Return to the ship before time runs out; sell scrap to meet a rising quota.
4. Miss the quota in the given days and the crew is "fired" (the run ends).
5. Buy gear and unlock moons; repeat with higher risk.

**Meta and progression**: a ship and company credits; unlockable moons and items; no persistent power between runs beyond cosmetic unlocks (verify). Mods extend content (verify).
**Economy**: credits from scrap sales; a quota that rises each cycle; item prices on a terminal.
**Monetization**: one low price. **Live-ops**: free updates; no live service. **Retention hooks**: shared funny failures, mods, quota chase. **Social layer**: four-player co-op with proximity voice [V8].

**UX and onboarding notables**: a terminal as the in-world menu; little explanation, so friends teach each other; low-poly PS1-style visuals hide the budget.
**Art and audio identity**: a retro low-resolution look with a dread soundscape; monster sounds are the main alert.
**Psychology principles used**: shared fear and laughter; risk-reward at the "one more room" decision; social comparison of failures.
**Innovations**: proximity voice as a horror mechanic; a quota deadline that turns a horror room into an economic risk choice.
**Weaknesses and criticism**: content depth after a few hours; long-tail decline as the creator-driven trend ended (verify); solo-dev update pace.

**Lessons for designers**
1. Design for the clip: a game whose funniest moments are shareable markets itself through streamers.
2. A small asset budget is fine when the mechanic produces the drama (voice, sound, light).
3. A rising quota provides pacing without a story budget.
4. Early access at a low price lets a solo developer respond to a spike.

**Analogy hooks**: proximity voice → social deduction, other horror co-op. Quota loop → extraction and roguelite risk pacing. Streamer-first design → any party game.

**Platform notes**: Windows only in the sources checked; no console edition confirmed [V8]. Local mod support and a Steam Workshop-like scene (verify). Proximity voice needs a clear policy for moderation and reports on any platform that adds it.

**Ontology encoding**
```json
{"loops": [
  {"id": "lc_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "enter_facility_collect_scrap", "reward": "scrap", "next": "c2"},
    {"id": "c2", "action": "avoid_monsters_with_voice_and_sound", "reward": "survive", "next": "c3"},
    {"id": "c3", "action": "return_and_sell_for_quota", "reward": "credits", "next": "c1"}]}],
 "economy": {"currencies": [{"id": "credits", "kind": "soft", "sources": ["scrap_sales"], "sinks": ["terminal_items"], "cap": null}]}}
```

## 9. Rocket League

**Snapshot**
- Developer: Psyonix (acquired by Epic Games in May 2019). Sequel to the 2008 PS3 game *Supersonic Acrobatic Rocket-Powered Battle-Cars*. Released 7 July 2015 on PS4 and Windows; Xbox One February 2016; Switch November 2017 [V9]. Team size: not sourced.
- Model change: premium, then free-to-play on all platforms on 23 September 2020, when the Windows version moved from Steam to the Epic Games Store (existing Steam owners kept playing) [V9].
- Scale: over 5 million downloads by July 2015 (the PS Plus launch), 6.2 million sales by July 2016, 40 million players by early 2018, 50 million by September 2018, and over 1 million concurrent the day after going free [V9].

**Core loop**
1. Three-a-side car soccer: drive, jump, boost and air-dribble to hit a ball into a goal.
2. Matches last five minutes; overtime is sudden death.
3. Win or lose, earn XP and an item drop or blueprint progress.
4. Ranked playlists adjust rank; seasons reset.
5. Spend credits on cosmetics, or buy and trade items.

**Meta and progression**: ranks across playlists, a level ladder, and the Rocket Pass battle pass (September 2018). Loot crates (September 2016) were replaced by Blueprints in December 2019 amid regulatory attention [V9].
**Economy**: cosmetics only; no gameplay power for sale. Credits are a premium currency; items trade on some platforms with platform-bound limits.
**Monetization**: premium until 2020; then free-to-play with a battle pass and an item shop. **Live-ops**: seasons, limited modes, esports (RLCS since 2016). **Retention hooks**: rank ladders and a very high skill ceiling. **Social layer**: parties, voice, cross-platform friends via Epic accounts.

**UX and onboarding notables**: the goal is readable in one second; training packs and free play teach mechanics, but the skill ceiling is steep.
**Art and audio identity**: bright arena sports look with exaggerated cars; an upbeat electronic mood suited to short sessions.
**Psychology principles used**: competence and mastery; flow in short matches; the "one more game" effect from five-minute rounds.
**Innovations**: physics-driven sports as a mastery game; early crossplay; the 2019 switch from loot boxes to visible-content blueprints.
**Weaknesses and criticism**: a hard learning curve for newcomers; smurfing in ranked; the Steam exit annoyed some PC players.

**Lessons for designers**
1. One rule that a viewer understands in seconds sells a hard skill game.
2. Going free-to-play with crossplay and a cosmetics-only model can multiply the player base (over one million concurrent in a day).
3. Platform-holder politics shaped crossplay: Sony's reversal in 2018 enabled cross-platform play in 2019 [V9].
4. Replace paid randomness with visible contents if regulation or trust is a risk.

**Analogy hooks**: physics-sport mastery → racing, golf and skill-toy games. Blueprints → any cosmetics shop that wants disclosed contents. Platform exit → storefront choice as a business-model lever.

**Platform notes**: launched as a PS Plus game (reach) and on Steam (PC); crossplay between Windows and Xbox One came in May 2016, Switch joined at launch in 2017, and Sony allowed full crossplay with go-live in February 2019 [V9]. One account (Epic) links progress. Check the current policy on the Rocket League support site (volatile).

**Ontology encoding**
```json
{"loops": [
  {"id": "rl_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "drive_boost_hit_ball", "reward": "goal", "next": "c2"},
    {"id": "c2", "action": "finish_match", "reward": "xp_drop_rank", "next": "c1"}]}],
 "economy": {"currencies": [{"id": "credits", "kind": "premium", "sources": ["purchase"], "sinks": ["item_shop", "rocket_pass"], "cap": null}]}}
```

## 10. Street Fighter 6

**Snapshot**
- Developer and publisher: Capcom; built on the RE Engine. Released 2 June 2023 on PS4, PS5, Windows and Xbox Series X/S; a Switch 2 edition on 5 June 2025 as a launch title (a Game-Key Card edition) [V10].
- Scale: over 1 million in five days, over 5 million by June 2025 and 7 million as of June 2026 (Capcom, via Wikipedia and trade press); Capcom's stated lifetime goal was 10 million [V10].
- Genre: fighting. Model: premium plus paid season passes of characters.

**Core loop**
1. Neutral game: space, poke and read the opponent.
2. Drive Gauge: a shared resource for Drive Impact, Parry, Rush and Overdrive; running out leaves you "burned out".
3. Combo into a Super Art; manage meter.
4. Win rounds; ranked matches move league points.
5. Learn matchups in Training or World Tour.

**Meta and progression**: ranked leagues, a master rank and character levels. *World Tour* is a single-player, third-person avatar mode with an RPG layer; *Battle Hub* is a social lobby with arcade cabinets [V10].
**Economy**: Fighter Coins and Drive Tickets (soft) and Zenny in World Tour; DLC characters are bought as season passes or individually. Check the in-game store for current names (verify).
**Monetization**: base price, season passes of four to six characters, cosmetics. **Live-ops**: yearly character seasons and balance patches; events in the Battle Hub. **Retention hooks**: ranking, tournaments, learning characters. **Social layer**: online ranked and casual with rollback netcode and crossplay, an avatar lobby [V10].

**UX and onboarding notables**: three control types (Classic six-button, Modern four-button with one-key specials, and offline-only Dynamic); an on-screen input display and frame data tools reduce the knowledge barrier [V10].
**Art and audio identity**: a graffiti, street-style visual language and strong music; UI and effects make hits readable.
**Psychology principles used**: competence from understandable inputs; autonomy in avatar progression; identity through avatar and character mains.
**Innovations**: Modern controls give newcomers a lower execution bar in a ranked ladder; World Tour is a large single-player on-ramp; rollback netcode and crossplay modernise online play.
**Weaknesses and criticism**: Denuvo anti-tamper was added to the PC build just before launch and drew performance concerns (press report; verify); some players dislike DLC pricing; Modern controls are debated for balance.

**Lessons for designers**
1. Give execution-light and execution-heavy paths to the same game and keep both rankable.
2. A long single-player mode converts casual buyers into online players.
3. Rollback netcode and crossplay are baseline for a fighting game on PC and console.
4. A year-pass roadmap sets the revenue timeline for a premium fighter.

**Analogy hooks**: Modern controls → any skill game with an assist mode (racing assists, shooters' aim help). Battle Hub → social lobbies in sports and racing games. Resource shared between offence and defence → stamina systems in any action game.

**Platform notes**: four launch platforms at once, an arcade version, then Switch 2 in June 2025 with the Years 1-2 edition on a Game-Key Card [V10]. Hardware controller support (arcade sticks, hit boxes) is expected; Steam Deck compatibility: verify.

**Ontology encoding**
```json
{"loops": [
  {"id": "sf_core", "type": "core", "period": "seconds", "steps": [
    {"id": "c1", "action": "neutral_poke_and_read", "reward": "opening", "next": "c2"},
    {"id": "c2", "action": "spend_drive_gauge_combo", "reward": "damage_super_meter", "next": "c1"}]},
  {"id": "sf_meta", "type": "meta", "period": "daily", "steps": [
    {"id": "m1", "action": "play_ranked_or_world_tour", "reward": "league_points_or_levels", "next": "m1"}]}],
 "progression": {"tracks": [{"id": "ranked_league", "gated_by": "league_points"}]}}
```

## 11. Cities: Skylines

**Snapshot**
- Developer: Colossal Order (Finland), a 13-person studio at release; publisher Paradox Interactive. Released 10 March 2015 on Windows, macOS and Linux; Xbox One April 2017, PS4 August 2017, Switch September 2018, current-generation consoles February 2023 [V11].
- Scale: over 2 million in its first year; more than 12 million across all platforms as of June 2022 (the Wikipedia article, citing a company figure) [V11]. The sequel *Cities: Skylines II* sold over 1 million units by the end of 2023 (Paradox year-end report); Paradox apologised for performance, platform and feature gaps at launch [V11]. From 2024 the franchise development moved to Tantalus Media [V11].
- Genre: city builder. Model: premium plus paid expansions and free updates.

**Core loop**
1. Zone residential, commercial and industrial land and lay roads.
2. Provide services (power, water, education, health, police) and watch traffic.
3. Respond to demand bars and money flow; extend districts and policies.
4. Hit population milestones that unlock buildings.
5. Fix the traffic jam; grow again.

**Meta and progression**: milestone unlocks and unique buildings; no persistent meta. DLC adds new systems (transport, disasters, campus).
**Economy**: a city budget (taxes, loans, maintenance) is the core economy; no real-money economy.
**Monetization**: base game plus paid expansion packs and cosmetic packs, with free updates; console DLC lagged PC at first and later launched in parallel [V11]. **Live-ops**: DLC and patches. **Retention hooks**: mods, sandbox goals, "build a better city". **Social layer**: Steam Workshop with more than 200,000 user items as of February 2020 [V11].

**UX and onboarding notables**: the tools are a transport-first, drag-to-build interface; overlays make hidden systems legible; the game is open from minute one.
**Art and audio identity**: a clean, readable city view and a calm score, designed to show traffic and zoning at a glance.
**Psychology principles used**: autonomy; mastery of transport; ownership of "my city"; the tinkerer's flow.
**Innovations**: an easier road-building toolset and a mod-first approach where the player community built the content; the genre gap after SimCity's 2013 launch made the hit possible (context: market gap).
**Weaknesses and criticism**: the sequel's launch problems show how a prior success raises expectations; traffic AI limits; DLC volume.

**Lessons for designers**
1. A franchise can leave a gap; fill it with the missing core (here: traffic and freeform building).
2. Mod support is content you do not pay for, as long as the tools are open and stable.
3. A sequel inherits a promise: ship performance and parity before features.
4. Console ports need a reduced UI and a parallel DLC plan.

**Analogy hooks**: road tools → any grid builder with a flow overlay. Workshop → UGC for any simulation. Parity gaps → console ports of PC-first sims.

**Platform notes**: PC first; Xbox One and PS4 followed in 2017, Switch in 2018, remastered current-generation editions in 2023 and a Switch 2 expanded edition (28 October 2026, per Wikipedia; verify) [V11]. Mods do not carry to console in the same way (verify). The controller UI is the key port task.

**Ontology encoding**
```json
{"loops": [
  {"id": "cs_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "zone_and_build_roads", "reward": "population", "next": "c2"},
    {"id": "c2", "action": "provide_services_manage_traffic", "reward": "happiness_and_tax", "next": "c3"},
    {"id": "c3", "action": "unlock_milestone_buildings", "reward": "new_options", "next": "c1"}]}],
 "economy": {"currencies": [{"id": "budget", "kind": "soft", "sources": ["taxes"], "sinks": ["build", "maintenance"], "cap": null}]}}
```

## 12. Civilization VI

**Snapshot**
- Developer: Firaxis Games; publisher 2K. Released on PC in October 2016; iPad in December 2017 and Switch in November 2018 (ported by Aspyr), then other consoles later (verify exact dates) [V12]. Team size: not sourced.
- Scale: the 2K Switch release stated the franchise had sold in over 47 million units (sell-in, November 2018); a separate earlier Take-Two statement put *Civ VI* at more than 5.5 million (undated) [V12]. A later *Civilization VII* release in 2025 is outside this case (verify).
- Genre: turn-based 4X. Model: premium plus two large expansions (*Rise and Fall*, *Gathering Storm*) and DLC (dates: verify).

**Core loop**
1. Found cities; assign them districts (campus, theatre square and so on) on map tiles.
2. Research technologies and cultural civics; Eureka and Inspiration boosts reward doing the thing.
3. Build units and wonders; manage amenities, housing and loyalty.
4. Win by science, culture, domination, religion or score.
5. End turn; AI leaders react with agendas.

**Meta and progression**: era score and ages (in *Rise and Fall*), a persistent profile of unlocks (verify). The game is a self-contained run.
**Economy**: yields (food, production, gold, science, culture, faith) per city; district adjacency bonuses are the optimisation puzzle.
**Monetization**: base game, expansions and a "new frontier"-style pass of DLC civilisations (verify naming). **Live-ops**: patches and expansions. **Retention hooks**: "one more turn", multiple victory paths, asymmetric leaders. **Social layer**: hot-seat and online multiplayer; mods through the Workshop.

**UX and onboarding notables**: an advisor system and a Civilopedia; the lens overlays; turn-based play is naturally pause-safe, which suits phones and tablets.
**Art and audio identity**: a stylised, illustrative map look in place of realism; a musical score that changes by civilisation.
**Psychology principles used**: the "one more turn" effect (nested goals at every scale); goal-gradient; ownership of an empire.
**Innovations**: unstacked districts turn city layout into a puzzle; Eureka boosts link research to play; ports show a deep 4X can live on a tablet.
**Weaknesses and criticism**: late-game turn time; AI diplomacy; DLC volume.

**Lessons for designers**
1. Make each system feed the next: tiles, districts, adjacency, yields.
2. Reward doing (boosts) rather than only waiting for research timers.
3. A turn-based design ports to touch with a UI rebuild, not a redesign.
4. A franchise's ports are a long tail: tablets and handhelds sell to a different audience.

**Analogy hooks**: Eureka boosts → "learn by doing" in tech trees. Adjacency bonuses → any tile-placement optimisation. Pause-safe turns → mobile ports (see `premium-indie.md` §16.5).

**Platform notes**: PC first; iPad and Switch ports by Aspyr within about two years; the Switch version was reported as exceeding expectations by Take-Two [V12]. Check the current console availability and DLC parity before promising a port.

**Ontology encoding**
```json
{"loops": [
  {"id": "civ_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "place_district_and_build", "reward": "yields", "next": "c2"},
    {"id": "c2", "action": "research_with_boosts", "reward": "new_options", "next": "c3"},
    {"id": "c3", "action": "end_turn_and_react", "reward": "progress_to_victory", "next": "c1"}]}],
 "progression": {"tracks": [{"id": "tech_civics", "gated_by": "science_culture"}]}}
```

## 13. Fortnite

**Snapshot**
- Developer and publisher: Epic Games. *Save the World* entered paid early access on 25 July 2017; *Battle Royale* launched in September 2017 as a free game, built in about two months after *PUBG* showed demand [V13].
- Scale: over 10 million players in two weeks; 125 million by June 2018; revenue over $9 billion by the end of 2019 (Wikipedia, citing reports); live events with 14 million or more concurrent players were reported in 2024 by third-party trackers (estimate) [V13].
- Genre: battle royale and a creation platform. Model: free-to-play with a battle pass; V-Bucks for cosmetics; creator revenue share.

**Core loop**
1. Drop onto the island, loot and build; the storm shrinks the circle.
2. Fight, build structures and use the terrain.
3. Last team standing wins; earn XP and quests for the pass.
4. Complete the season's pass tiers for cosmetics.
5. Join limited-time modes, concerts and creator islands.

**Meta and progression**: a seasonal battle pass; chapters and seasons (seven chapters and 41 seasons as of September 2026, per Wikipedia) [V13].
**Economy**: V-Bucks (premium, bought) for the item shop and pass; cosmetics only. Epic's storefront sells V-Bucks at lower platform fees than mobile stores [V13].
**Monetization**: battle pass and shop; creators in Fortnite islands share an engagement pool (Epic's Creator Economy 2.0, March 2023: 40 per cent of net revenue from the item shop and most real-money purchases, split by engagement) [V13]. **Live-ops**: seasons with map changes, live events, collaborations. **Retention hooks**: pass tiers, events, friends. **Social layer**: parties, cross-platform play, and a creator ecosystem (Creative from December 2018, UEFN from March 2023) [V13].

**UX and onboarding notables**: the build system was a high-skill input; mobile and console touch aim assist and "no-build" modes widen access.
**Art and audio identity**: a bright, cartoon-like look that carries brand collaborations; creator islands change the look from island to island.
**Psychology principles used**: scarcity and FOMO from seasonal items; social proof; competence in short matches.
**Innovations**: seasonal map changes as a live service; the platform pivot to creator islands with revenue share; one account across all platforms.
**Weaknesses and criticism**: pass and shop FOMO; the Apple dispute removed the mobile client on 13 August 2020, and it returned to the US iPhone storefront on 20 May 2025 after a ruling [V13]; creator payout transparency (verify).

**Lessons for designers**
1. A fast-follow can beat the original if it adds one distinctive verb (building).
2. A platform that pays creators multiplies content without staff growth, if payouts are tied to retention.
3. One account across all platforms is the base of crossplay and cross-progression (see `web-and-crossplay.md` §9).
4. Store fees shape strategy: Epic's own storefront cuts platform cost.

**Analogy hooks**: seasons → live-ops in any shooter. Creator payouts → UGC platforms (Roblox: `casual-social-sim.md` §9). Map changes → event-driven worlds.

**Platform notes**: PC, consoles, Switch, mobile (with store removals and returns), and cloud play on Xbox since 5 May 2022 [V13]. The mobile dispute shows the risk of depending on a store the game competes with.

**Ontology encoding**
```json
{"loops": [
  {"id": "fn_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "loot_build_fight", "reward": "survival", "next": "c2"},
    {"id": "c2", "action": "reach_final_circle", "reward": "win_or_xp", "next": "c1"}]},
  {"id": "fn_season", "type": "liveops", "period": "daily", "steps": [
    {"id": "l1", "action": "complete_quests_for_pass", "reward": "pass_tiers", "next": "l1"}]}],
 "economy": {"currencies": [{"id": "vbucks", "kind": "premium", "sources": ["purchase"], "sinks": ["item_shop", "battle_pass"], "cap": null}]}}
```

## 14. Final Fantasy XIV

**Snapshot**
- Developer and publisher: Square Enix. The 2010 launch was received very negatively; the team was overhauled, monthly fees were suspended, and Naoki Yoshida became producer and director of a rebuilt game, *A Realm Reborn*, which launched on 27 August 2013 on PS3 and Windows [V14].
- Platforms: PS4 (April 2014), macOS (June 2015), PS5 (May 2021), Xbox Series X/S (March 2024), Switch 2 (4 August 2026, per Wikipedia) [V14].
- Scale: registered players of about 1.5 million (October 2013), 14 million (August 2018), 22 million (April 2021) and over 30 million (announced early 2024) [V14]. The *Dawntrail* expansion (2 July 2024) set a concurrent-player record, in Yoshida's words the highest since 2013 [V14].
- Genre: MMORPG. Model: subscription plus box purchases for expansions, with a free trial.

**Core loop**
1. Take a job (class) and run quests and duty finders (dungeons, trials, raids) with a role: tank, healer or damage.
2. Earn gear and tokens; unlock the next story step.
3. Weekly lockouts for raids and tomestones cap progress and set a weekly rhythm.
4. Level jobs on one character by switching weapons.
5. Expansions every two to three years add a story and a level cap.

**Meta and progression**: main story quests gate duties; level cap rises per expansion; weekly capped currencies.
**Economy**: gil, tomestones (capped weekly) and crafting; no real-money power.
**Monetization**: a monthly subscription, expansion purchases and a cosmetic store; Yoshida credits the subscription model for sustaining the game [V14]. **Live-ops**: patches every few months, a published roadmap, fan festivals. **Retention hooks**: story, weekly raid, a social "free company" guild. **Social layer**: parties, free companies, duty finder with automatic role matching.

**UX and onboarding notables**: the free trial grew from level 35 to 60 (2020), included *Stormblood* content up to level 70 (October 2023) and *Shadowbringers* content up to 80 (April 2026) [V14]. A long, story-gated start is a known barrier.
**Art and audio identity**: a high-fidelity fantasy style, an orchestral score with a recurring theme per expansion.
**Psychology principles used**: relatedness (guilds, story); goal-gradient; weekly cadence as habit.
**Innovations**: the relaunch itself, with the old world ended in an in-game event (the original shut down in November 2012) [V14]; a single character playing every job.
**Weaknesses and criticism**: *Dawntrail* drew mixed reviews for writing (about 63 per cent positive on Steam at one check, per a news report); the MMO's heavy story gate.

**Lessons for designers**
1. A failed launch can be rebuilt: be honest, suspend charges and rebuild the core.
2. A subscription works when it buys a constant stream of story and raids, not when it is a gate.
3. A generous free trial is the funnel; extend it as the content grows.
4. A visible producer-led roadmap builds trust.

**Analogy hooks**: weekly caps → pacing in any live service. Role queue → automatic matchmaking for team games. Relaunch event → the sunset and re-release plan.

**Platform notes**: PC and PlayStation first (crossplay across platforms with one subscription account), Xbox in 2024 (the Wikipedia article says online play needs Game Pass; verify), Switch 2 in 2026 with a separate subscription [V14]. An MMO's console UI is a big job: hotbars, cross-hotbar and chat.

**Ontology encoding**
```json
{"loops": [
  {"id": "ff_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "run_duty_with_role", "reward": "gear_tokens", "next": "c2"},
    {"id": "c2", "action": "advance_story_quest", "reward": "unlock_next_duty", "next": "c1"}]},
  {"id": "ff_meta", "type": "meta", "period": "daily", "steps": [
    {"id": "m1", "action": "weekly_raid_and_tomestones", "reward": "capped_gear_progress", "next": "m1"}]}],
 "economy": {"currencies": [{"id": "tomestones", "kind": "material", "sources": ["duties"], "sinks": ["gear"], "cap": "weekly"}]}}
```

## 15. Forza Horizon 5

**Snapshot**
- Developer: Playground Games; publisher Xbox Game Studios. Released 9 November 2021 on Windows, Xbox One and Xbox Series X/S, and available on Xbox Game Pass from day one; PS5 version (by Panic Button) on 29 April 2025, the first mainline Forza game on a non-Microsoft platform [V15]. Team size: not sourced.
- Scale (players, not sales): over 10 million players in the first week (a record for Xbox), 15 million by 9 January 2022, about 40 million by July 2024 (Microsoft's in-game tracker, via press); the PS5 version sold about 5.8 million units as of April 2026 (Wikipedia; press reports gave lower, earlier figures) [V15].
- Genre: open-world racing. Model: premium plus subscription catalogue, paid expansions (*Hot Wheels*, 19 July 2022; *Rally Adventure*, 29 March 2023) and car packs.

**Core loop**
1. Drive across a fictional Mexico, entering races and discovering events.
2. Earn credits and skill points for driving well; win cars in the festival.
3. Tune and paint cars; share designs.
4. Progress festival playlists and seasonal weekly challenges ("Forzathon").
5. Play online in co-op and "Eliminator" style events.

**Meta and progression**: car collection, festival fame and accolades; seasonal playlists keep the loop fresh (verify structure).
**Economy**: credits (soft) buy cars; car packs are premium; no gameplay pay-to-win in a racing sense (verify).
**Monetization**: a premium price, a Game Pass catalogue deal at launch and paid expansions; the later PS5 release reopened premium sales [V15]. **Live-ops**: weekly seasons and festival playlists. **Retention hooks**: car collection and weekly challenges. **Social layer**: shared open world, clubs, cross-play among Xbox and PC [V15].

**UX and onboarding notables**: assists and difficulty sliders (verify names); a clear mini-map; the map is about 50 per cent bigger than *Forza Horizon 4* [V15].
**Art and audio identity**: a vibrant, sunlit Mexico with an active volcano, jungle and desert; a radio-style soundtrack.
**Psychology principles used**: discovery in a dense open world; collection; low-friction flow with fast restarts.
**Innovations**: a festival structure that gives an open world a campaign; Game Pass day-one release as a reach strategy.
**Weaknesses and criticism**: car-pack monetisation (verify); repetition across event types; online progression frictions.

**Lessons for designers**
1. A subscription deal changes success metrics from units to players and engagement; plan the revenue model before the platform deal.
2. A late port to a rival platform can reopen premium sales (PS5, 2025).
3. A dense open world beats a large empty one: every minute has an event.
4. Racing assists widen the audience without removing the sim layer.

**Analogy hooks**: festival structure → open-world campaigns. Game Pass → subscription catalogues (Grindstone, `premium-indie.md` §15). Port later → a platform-exclusive window.

**Platform notes**: Xbox and PC at launch with crossplay and cloud streaming; PS5 delivered by a specialist port studio about three and a half years later [V15]. Steam Deck compatibility, performance modes (4K/60 and so on) and settings: verify on the store page.

**Ontology encoding**
```json
{"loops": [
  {"id": "fh_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "race_events_across_map", "reward": "credits_skill_points", "next": "c2"},
    {"id": "c2", "action": "buy_and_tune_cars", "reward": "collection", "next": "c1"}]},
  {"id": "fh_live", "type": "liveops", "period": "daily", "steps": [
    {"id": "l1", "action": "weekly_seasonal_challenges", "reward": "cars_and_credits", "next": "l1"}]}],
 "economy": {"currencies": [{"id": "credits", "kind": "soft", "sources": ["races", "challenges"], "sinks": ["cars", "upgrades"], "cap": null}]}}
```

## 16. Cross-case synthesis for PC and console

### 16.1 Business models compared

| Model | Cases | What pays | Main risk | Choose it when |
|---|---|---|---|---|
| Premium, one price | Hollow Knight, Baldur's Gate 3, Elden Ring, Street Fighter 6, Civilization VI | the first sale, then DLC and ports | one chance at launch reviews; a long tail only through ports and updates | a finished, authored or deep-systems game with a clear trailer moment |
| Early access, then premium | Factorio, RimWorld, Valheim, Lethal Company, BG3 | early buyers fund and shape the game | the audience arrives before the content; "abandoned" reputation | a systems game that benefits from feedback, and a plan for updates |
| Premium plus expansions and mods | RimWorld, Cities: Skylines, Factorio (*Space Age*) | engaged owners buy again | DLC fatigue; mod and DLC compatibility | a sandbox with a long tail |
| Subscription catalogue (platform deal) | Forza Horizon 5 | a deal up front and reach | metrics shift to engagement; sales may lag | a first-party or deal-funded title |
| Free-to-play, cosmetics | Fortnite, Rocket League | battle pass and shop | trust, FOMO and regulation; needs a live team | a competitive or social game where fairness matters |
| Premium plus earnable pass | Helldivers 2 | game sales plus optional passes | server load, community backlash | a co-op or service game with a premium floor |
| Subscription MMO | Final Fantasy XIV | monthly fees plus expansion sales | needs a constant content stream | a deep, long-lived world with a producer-led roadmap |

### 16.2 Ports and platforms: what each case teaches

| Question | Evidence | Default decision |
|---|---|---|
| PC first or all at once? | Hollow Knight and Factorio went PC first; Elden Ring, SF6 and BG3 (in stages) went wide | Solo or tiny team: PC first, console 6–18 months later. Large team: plan ports from the start. |
| Who ports? | Aspyr (Civ VI), Double Eleven (RimWorld), Nixxes (Helldivers 2 Xbox), Panic Button (FH5 PS5) | Use a specialist when your team has no console experience. |
| Do mods survive? | Factorio's Switch and RimWorld's console editions lacked the PC mod ecosystem | Tell players before launch; do not promise parity. |
| Split-screen and crossplay | BG3 added both late (April 2025) | Decide at the start: retrofits cost a year. |
| Account policy | Helldivers 2's forced PSN link (reversed in two days) | Do not require a platform-holder account on other platforms. |
| Handheld | Hollow Knight on Switch; Factorio and Civ VI ports; BG3 Linux for Steam Deck | Test on a Steam Deck and Switch-class hardware: 30 fps stability, text size, short sessions. |
| Late platform windows | FH5 PS5 (2025), Elden Ring Switch 2 (2026) | A port two to four years on reopens sales; plan the contract early. |

### 16.3 Team size and scope

| Team | Case | Content source | Scope lever |
|---|---|---|---|
| Solo | Lethal Company | systems and player-made moments | a low-poly look; proximity voice |
| 5 | Valheim | a tier ladder and a building system | co-op; biomes as unlocks |
| 13 (at launch) | Cities: Skylines | simulation systems | mods and Workshop |
| Small core | Hollow Knight | hand-drawn world | a limited palette; free updates |
| 31 (2024) | Factorio | simulation, mod API | one metric (items per second) |
| 140 to 450 | Baldur's Gate 3 | authored reactivity | early access to find the shape |
| Studio, size unsourced | Elden Ring, SF6, Helldivers 2, FH5, FFXIV | hand-built content and live ops | engine reuse, roadmap |

Decision rule: below ten people, choose systems that make content (colony, factory, co-op chaos). Above a hundred, choose authored reactivity or a live roadmap and budget for testing.

### 16.4 Four clocks, by case

| Case | Seconds | Minutes | Days | Months |
|---|---|---|---|---|
| Hollow Knight | strike and heal | explore a room | a boss | free updates (none after) |
| Factorio | place a belt | a build | a base | expansion |
| RimWorld | assign work | an event | a colony | DLC every year |
| Helldivers 2 | stratagem code | a mission | a Major Order | Warbonds |
| Rocket League | boost and hit | a match | ranked grind | seasons and pass |
| SF6 | a read | a round | ranked league | character seasons |
| FFXIV | a skill rotation | a duty | weekly lockout | expansion every 2–3 years |
| Fortnite | build and fight | a match | quests | chapter and season |

A premium game with no months clock is fine (Elden Ring); a live service without one fails.

### 16.5 Early-access decision table

| Signal | Go | Wait |
|---|---|---|
| Core loop fun in a grey box | yes (Valheim, Lethal Company) | no |
| Content for 10+ hours | yes | fewer: players leave when they finish |
| A roadmap you can name | yes (Factorio's blog, RimWorld) | no |
| Co-op or sandbox where players make content | yes | linear story (finish it first) |
| Budget for six months of patching | yes | no |

### 16.6 Checklist before building a PC or console game
- [ ] Name the depth source: systems, authored reactivity, skill mastery or a live service. Pick one primary.
- [ ] Choose the model with the table in 16.1 before the content plan.
- [ ] Write the platform plan: first platform, port partner, mod stance, split-screen and crossplay needs (16.2).
- [ ] Set controller-first input and a readable UI at handheld size; test on a Steam Deck.
- [ ] Decide the account policy early: one account across platforms, no forced platform-holder links.
- [ ] If the game is co-op, price for a group purchase and ship dedicated-server or host options.
- [ ] If the game is free-to-play, run the ethics screen in `cross-game-patterns.md` and publish drop rates or contents.
- [ ] Plan launch capacity (servers, support), because the first week sets the reputation.
- [ ] Record comparables in `contract.meta.comparables`; set `meta.platforms` and `meta.input` as in `platform-targets`; release steps are in `pc-web-release` and `console-pathway`.

## 17. Volatile facts (as of Oct 2026 — verify before relying)

Sources are Wikipedia (grade C, quoting company statements where noted) plus the press items searched on 21 October 2026. Check the live store pages and company filings before quoting any number.

- [V1] Helldivers 2: [Wikipedia](https://en.wikipedia.org/wiki/Helldivers_2) (release dates; sales to January 2026; PSN reversal dates; level cap changes); [Shacknews, 12 million](https://www.shacknews.com/article/139876/helldivers-2-12-million-copies-sold).
- [V2] Elden Ring: [Wikipedia](https://en.wikipedia.org/wiki/Elden_Ring) (dates, 30 million by April 2025, Switch 2 edition); [Automaton, Steam peak](https://automaton-media.com/en/news/20220307-10295/); [NME, Steam Deck Verified at launch](https://www.nme.com/news/elden-ring-is-steam-deck-verified-at-launch-3169585).
- [V3] Baldur's Gate 3: [Wikipedia](https://en.wikipedia.org/wiki/Baldur%27s_Gate_3) (dates, headcount, patches, awards); [WN Hub, 20 million](https://wnhub.io/news/finance/item-49589) (press report, not audited).
- [V4] Hollow Knight: [Wikipedia](https://en.wikipedia.org/wiki/Hollow_Knight) (Kickstarter, dates, DLC, sales); [Nintendo Life, 15 million by August 2025](https://www.nintendolife.com/news/2025/08/hollow-knight-has-now-sold-almost-15-million-copies); [Game World Observer, Silksong peak](https://gameworldobserver.com/2025/09/05/hollow-knight-silksong-entered-the-top-20-games-with-the-highest-concurrent-player-count-in-steam-history).
- [V5] Factorio: [Wikipedia](https://en.wikipedia.org/wiki/Factorio) (dates, 3.5 million, 31 staff, Switch editions); [GamingOnLinux, Space Age](https://gamingonlinux.com/2024/10/factorio-space-age-sold-over-400000-copies-and-sets-a-new-player-count-record).
- [V6] RimWorld: [Wikipedia](https://en.wikipedia.org/wiki/RimWorld) (Kickstarter, dates, DLC, revenue estimate).
- [V7] Valheim: [Wikipedia](https://en.wikipedia.org/wiki/Valheim) (dates, five-person team, platform dates); [Game Developer, 12 million](https://gamedeveloper.com/business/-i-valheim-i-has-crafted-12-million-sold-copies).
- [V8] Lethal Company: [Wikipedia](https://en.wikipedia.org/wiki/Lethal_Company); [Shacknews, 180k concurrent](https://shacknews.com/article/137893/lethal-company-180k-concurrent-players-steam); [Game Developer, estimate](https://gamedeveloper.com/business/lethal-company-sold-an-estimated-10-million-copies). Third-party estimates (Raijin, GameDiscoverCo, Gamalytic) disagree; treat all as estimates.
- [V9] Rocket League: [Wikipedia](https://en.wikipedia.org/wiki/Rocket_League); [Engadget, crossplay and progression](https://www.engadget.com/rocket-league-crossplatform-progression-053100104.html).
- [V10] Street Fighter 6: [Wikipedia](https://en.wikipedia.org/wiki/Street_Fighter_6); [Event Hubs, 6 million](https://eventhubs.com/news/2025/nov/20/street-fighter-6-million).
- [V11] Cities: Skylines: [Wikipedia](https://en.wikipedia.org/wiki/Cities:_Skylines); [Exputer, Cities: Skylines II 1 million](https://exputer.com/news/games/cities-skylines-2-1-million-copies/).
- [V12] Civilization VI: [2K newsroom, Switch release (47 million franchise)](https://newsroom.2k.com/news/sid-meiers-civilizationr-vi-now-available-for-nintendo-switch); [PCGamesN](https://www.pcgamesn.com/civilization-6/sales) (the 5.5 million figure is undated).
- [V13] Fortnite: [Wikipedia](https://en.wikipedia.org/wiki/Fortnite); [Fortnite news, UEFN and Creator Economy 2.0](https://www.fortnite.com/news/unreal-editor-for-fortnite-and-creator-economy-2-0-are-here-new-worlds-await); [Dexerto, peaks](https://www.dexerto.com/fortnite/is-fortnite-dying-how-many-players-in-2021-1666278/) (third-party tracker figures).
- [V14] Final Fantasy XIV: [Wikipedia](https://en.wikipedia.org/wiki/Final_Fantasy_XIV); [Game World Observer, Dawntrail concurrent record](https://gameworldobserver.com/2024/07/05/final-fantasy-14-record-concurrent-players-dawntrail).
- [V15] Forza Horizon 5: [Wikipedia](https://en.wikipedia.org/wiki/Forza_Horizon_5); [WN Hub, 40 million players](https://wnhub.io/news/stores-and-publishing/item-44192).
- Not verified for this file, check before quoting: Steam Deck status of every case except Elden Ring at launch; team sizes for Arrowhead, Psyonix, Playground Games, FromSoftware and Capcom; Valheim's price and 2026 release status; Lethal Company's console status and later sales; Civ VI platform dates and DLC list; Forza Horizon 5 Game Pass availability today; all current prices.
