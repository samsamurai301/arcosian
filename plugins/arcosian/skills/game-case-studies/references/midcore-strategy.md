# Midcore, strategy and competitive case studies

Sixteen deconstructions of games built on conflict, mastery and group obligation. They cover six families: asynchronous base-builders (Clash of Clans, Boom Beach), short real-time PvP (Clash Royale, Brawl Stars), 4X or "SLG" kingdom-war games (Rise of Kingdoms, Lords Mobile, Whiteout Survival, Last War: Survival), tower defense in both premium and free-to-play forms (Plants vs. Zombies 2, Bloons TD 6, Kingdom Rush), MOBAs (Mobile Legends: Bang Bang, Honor of Kings) and shooters (PUBG Mobile, Free Fire, Call of Duty: Mobile). One question connects them: what keeps a player engaged for years once the first-week novelty is gone? The cases give three answers, usually combined: a power curve the player is always climbing, other people who depend on them (clans, alliances, squads), and a skill ladder that never tops out. Each answer also implies a monetization ceiling and a fairness risk. Selling power makes money in a 4X game but breaks a ranked shooter, while selling cosmetics keeps a MOBA fair but needs very large audiences. Each case uses the 16-lens format from `SKILL.md` and ends with an ontology encoding in contract field names (`loops[].steps[]`, `economy.currencies[]`). Mechanics are described as publicly observable in shipped builds. Live games change often, so details that are uncertain or frequently retuned are marked "verify". Revenue figures are omitted. Volatile market facts are in section 18.

**Contents.** Sections 1–16 are case studies (index below). Section 17 is a cross-case synthesis with decision tables and worked examples. Section 18 lists volatile facts with sources.

| # | Game | Genre | Year | Key lesson |
|---|---|---|---|---|
| 1 | Clash of Clans | base-builder, async PvP | 2012 | Storage caps, builder queues and clan donations make a timer economy feel social and fair |
| 2 | Clash Royale | real-time card battler | 2016 | A 3-minute duel with an elixir clock compresses RTS decisions into a phone session |
| 3 | Brawl Stars | team hero shooter | 2018 | Tap-to-auto-aim and drag-to-aim on one button split the skill floor from the skill ceiling |
| 4 | Rise of Kingdoms | 4X / SLG | 2018 | Free marching on a shared map makes strategy visible; seasons keep servers competitive |
| 5 | Last War: Survival | 4X / SLG + casual mini-games | 2023 | A hybrid-casual top of funnel can feed a deep 4X, if the game honours what the ad shows |
| 6 | Whiteout Survival | survival-themed 4X / SLG | 2023 | A survival-colony framing teaches 4X systems through needs the player can feel |
| 7 | Lords Mobile | 4X + hero RPG | 2016 | A PvE hero campaign gives a war game a safe, solo on-ramp |
| 8 | Boom Beach | base-builder, PvE/PvP + co-op | 2014 | One win condition and directed troops simplify raids; co-op operations add a weekly ritual |
| 9 | Plants vs. Zombies 2 | lane tower defense | 2013 | Every world needs one environmental rule; the premium-to-F2P sequel trade-offs |
| 10 | Bloons TD 6 | path tower defense | 2018 | Premium price plus years of free updates; one crosspath rule creates a huge build space |
| 11 | Kingdom Rush | plot-based tower defense | 2011 | Fixed build plots and blocking barracks turn TD into authored tactical puzzles |
| 12 | Mobile Legends: Bang Bang | 5v5 MOBA | 2016 | Fit the MOBA to the region's phones, networks and match-length tolerance |
| 13 | Honor of Kings | 5v5 MOBA | 2015 | A competitive game can become a mass social habit when wired into the social graph |
| 14 | PUBG Mobile | battle royale | 2018 | Console-grade design survives on phones only with aggressive device scaling and new-player bots |
| 15 | Free Fire | battle royale (short) | 2017 | Design for the real device market: 50 players, 10 minutes, low-end Android |
| 16 | Call of Duty: Mobile | multimode shooter | 2019 | Translate an IP's maps and modes, and offer auto-fire so touch is not a handicap |

---

## 1. Clash of Clans

**Snapshot**
- Developer: Supercell (Helsinki, Finland). A Tencent-led consortium (Halti S.A., 50% Tencent) bought about 81% in June 2016, and Tencent raised its stake in the consortium to 51.2% in October 2019 ([Wikipedia: Supercell](https://en.wikipedia.org/wiki/Supercell_%28company%29)). Release: iOS in August 2012, Android in October 2013.
- Genre: base-builder with asynchronous PvP raids. Business model: free-to-play with IAP (gems) and, since 2019, a monthly season pass (Gold Pass).
- Scale: a top-grossing mobile game for over a decade by store-intelligence rankings (figures omitted). Its 2015 Super Bowl commercial starring Liam Neeson was widely covered.

**Core loop**
1. Collect gold and elixir from mines and collectors (dark elixir from drills at higher Town Hall levels).
2. Spend resources on buildings, walls, troops and research. Each building upgrade occupies one builder for a timer.
3. Train an army whose size is capped by army-camp capacity.
4. Find an opponent near your trophy count, scout the base, and deploy troops from outside its edge during a 3-minute battle.
5. Score stars: one for 50% destruction, one for destroying the Town Hall, one for 100%. Take a share of the defender's stored loot and win or lose trophies.
6. Get raided while offline. A shield protects the village for a while after a heavy defeat. Read the defence log, adjust the layout, take revenge.
7. Return to step 1 with a slightly stronger village.

**Meta and progression**
- Town Hall (TH) level is the master gate. It caps every building, troop, hero and wall level, so each new TH level is a content drop.
- Builders set how many upgrades run in parallel. The player starts with few, buys more with gems, and choosing what occupies each builder is the central planning decision. The laboratory researches one troop or spell level at a time.
- Heroes (Barbarian King, Archer Queen, Grand Warden, Royal Champion) cannot fight while upgrading, which creates a deliberate tension between progress and readiness. Hero equipment arrived in 2023 (verify the current hero roster).
- Further layers: trophy leagues, a second village (Builder Base, 2017, reworked in 2023) and a shared clan village (Clan Capital, 2022).

**Economy**

| Currency | Kind | Sources | Sinks | Cap |
|---|---|---|---|---|
| Gold | soft | mines, raid loot, rewards | buildings, defences, walls | storage capacity |
| Elixir | soft | collectors, raid loot | troops, spells, research, some buildings | storage capacity |
| Dark elixir | soft | drills, raid loot | dark troops, most hero upgrades | storage capacity |
| Gems | hard | IAP, clearing obstacles, achievements, events | builders, timer skips, resources, magic items | none |
| Magic items (books, hammers, potions, runes) | material | Clan Games, Gold Pass, war league medals, events | instant upgrades, boosts | per-item caps |
| Capital gold and raid medals | event | Clan Capital contributions and raid weekends | clan village upgrades, trader | verify |
| Trophies | xp | wins | losses | none |

- **Storage caps are the inflation brake.** A full storage stops production and is exposed to raids, so the player spends rather than hoards.
- **Loot scales with Town Hall difference**, so attacking much weaker villages pays less (verify current penalties). This protects newer players from farming.

**Monetization**
- Gem packs on a price ladder. Gems skip timers, buy resources and unlock extra builders.
- Gold Pass: a monthly pass with challenges, rewards and perks such as faster or cheaper upgrades (perks vary by season; verify).
- One-time and event offers that bundle resources, magic items and skins.
- No third-party ads in the core experience (verify).
- **Worked example: sublinear skip pricing.** The community wiki documents gem costs for remaining time at roughly 1 gem for 1 minute, 20 for 1 hour, 260 for 1 day and 1,000 for 1 week (grade C; verify). The price per hour falls from 20 to about 11 to about 6 gems. Short skips are cheap enough to try, and the best value per gem sits on the longest timers, which are exactly the moments of greatest impatience.

**Live-ops**
- A monthly season (Gold Pass, Clan War League for one week a month, Clan Games), plus seasonal events with temporary troops, obstacles and skins.
- Large Town Hall updates, historically about once a year (verify cadence), and an annual esports championship (verify format).

**Retention hooks**
- Builder and lab timers finishing (push notifications), and full storages that raiders will empty.
- The defence log and revenge attacks; clan war attacks that the clan is counting on.
- Daily star bonus and monthly Clan Games targets.

**Social layer**
- Clans of up to 50 with chat, troop donations (a member requests, clanmates fill the request) and friendly challenges.
- Clan Wars (2014), Clan War Leagues (2018) and Clan Capital raid weekends (2022). Shareable base-layout links feed a large creator ecosystem.

**UX and onboarding notables**
- A single-player goblin campaign is a safe sandbox for learning attacks, and early timers last seconds.
- Raids are legible to spectators (replays, the star rule, a live percentage bar). Base editing is a toy in itself. Buildings visibly change with each upgrade, so progress is on display.

**Art and audio identity**: chunky, exaggerated cartoon troops (Barbarian, Archer, Giant, Goblin) with silhouettes readable at small sizes, warm medieval-fantasy colours and character barks. This "Clash universe" was later reused across Supercell titles.

**Psychology principles used**
- Loss aversion (stored resources at risk push players to spend and log in); endowment and the IKEA effect (a self-designed base).
- Reciprocity: troop donations create small debts between clanmates.
- Goal-gradient: upgrade bars and the checklist of everything a TH level unlocks.
- Ethical line: impatience is sold, including to minors, but the core offers are direct purchases rather than paid random loot.

**Innovations**
- Brought base-raid async PvP (Kixeye's Facebook game Backyard Monsters preceded it) to touch, with 3-minute raids and a one-sentence star rule.
- Made troop donation a social verb that transfers value, not just chat, and showed that builder-slot timers can be the main monetization lever while the game's tone stays generous.

**Weaknesses and criticism**
- Late-game timers stretch to days. Supercell has cut times and costs in several updates (verify current values).
- "Rushing" Town Hall levels leaves weak, frustrated players. A December 2015 update that changed shields and loot drew a widely reported ratings backlash: removing a perceived protection hurts more than adding a feature helps.
- Extra modes (Builder Base, Clan Capital) fragment attention. Paying buys faster power, visible in matchmaking and war line-ups.

**Lessons for designers**
1. Cap storage to control inflation and create urgency to spend, and pair the cap with protection (shields).
2. Make parallel queues (builders) the main planning decision. Each extra queue is a premium product.
3. A scoring rule should fit in one sentence (50%, Town Hall, 100%).
4. Give groups a verb that transfers value (donations). Social glue beats chat.
5. Test perceived fairness before changing protections. Losses register more strongly than gains.

**Analogy hooks**
- Builder slots → any upgrade queue (farm sims, idle tycoons, hero training).
- Donations → co-op card requests (Clash Royale), material gifting in puzzle teams.
- Shield after a loss → any PvP with offline vulnerability. The three-star rule with a percentage bar → score-attack levels in puzzle and TD games.

**Ontology encoding**
```json
{"loops": [
  {"id": "coc_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "train_army", "reward": "army_ready", "next": "c2"},
    {"id": "c2", "action": "scout_and_raid_base_3min", "reward": "loot_stars_trophies", "next": "c3"},
    {"id": "c3", "action": "assign_builders_to_upgrades", "reward": "upgrade_timers_started", "next": "c1"}]},
  {"id": "coc_meta", "type": "meta", "period": "daily", "steps": [
    {"id": "m1", "action": "collect_resources_and_finished_upgrades", "reward": "stronger_village", "next": "m2"},
    {"id": "m2", "action": "defend_offline_review_log", "reward": "shield_or_revenge_target", "next": "m3"},
    {"id": "m3", "action": "donate_troops_and_war_attack", "reward": "clan_standing_magic_items", "next": "m1"}]}],
 "economy": {"currencies": [
  {"id": "gold", "kind": "soft", "sources": ["mines", "raid_loot"], "sinks": ["buildings", "walls"], "cap": null, "note": "capped by storage level"},
  {"id": "elixir", "kind": "soft", "sources": ["collectors", "raid_loot"], "sinks": ["troops", "research"], "cap": null, "note": "capped by storage level"},
  {"id": "dark_elixir", "kind": "soft", "sources": ["drills", "raid_loot"], "sinks": ["dark_troops", "heroes"], "cap": null, "note": "capped by storage level"},
  {"id": "gems", "kind": "hard", "sources": ["iap", "obstacles", "achievements"], "sinks": ["builders", "timer_skips", "resources"], "cap": null},
  {"id": "magic_items", "kind": "material", "sources": ["clan_games", "gold_pass", "war_league"], "sinks": ["instant_upgrades"], "cap": null},
  {"id": "trophies", "kind": "xp", "sources": ["raid_wins"], "sinks": ["raid_losses", "defence_losses"], "cap": null}]}}
```

## 2. Clash Royale

**Snapshot**
- Developer: Supercell.
- Release: soft launch in January 2016, global release in March 2016.
- Genre: real-time 1v1 card battler (often described as a collectible-card game crossed with tower defense and MOBA lane pushing). Business model: free-to-play with IAP and a season pass (Pass Royale, 2020).
- Scale: one of the most successful mobile launches of its year by widely reported rankings (figures omitted). It supported a franchised esports league from 2018 (verify).

**Core loop**
1. Build an 8-card deck from your collection. Four cards are in hand at a time, and playing one cycles in the next.
2. Queue into a match against a player of similar trophy count (or rank in the ranked mode).
3. Spend elixir, which regenerates at a fixed rate up to a cap of 10, to deploy troops, buildings and spells on your side of the arena (or deeper after taking a tower).
4. Destroy the opponent's two princess towers (one crown each) or king tower (three crowns) within 3 minutes. Elixir speeds up near the end, and a tied match goes to sudden-death overtime (verify current timings).
5. Win trophies or rank and match rewards. Lose trophies on a loss.
6. Upgrade cards with gold plus duplicate cards, then return to step 1.

**Meta and progression**
- Arenas along a trophy road unlock new cards and new reward tiers.
- Card levels and the player's King Tower level determine raw stats. Rarities are Common, Rare, Epic, Legendary and Champion (added in 2021). Card Evolutions (2023) add upgraded forms.
- A ranked mode (Path of Legends, 2022) normalises card levels to cap their effect (verify the current rule).
- The reward system has been reworked several times. The original game used four chest slots with unlock timers, and later versions replaced chests with other reward systems (verify the current design).

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Gold | soft | matches, chests or drops, pass, shop | card upgrades, shop card purchases |
| Gems | hard | IAP, small free grants, pass | chest unlocks or skips, offers, challenge entry |
| Cards (duplicates) | material | rewards, donations, shop, trades | card level-ups |
| Wild cards | material | pass, events, shop | substitute for any card of a rarity |
| Trophies and rank | xp | wins | losses |

**Monetization**
- Pass Royale: a season pass with free and paid tracks and convenience perks.
- Gem packs, special offers and bundles, and cosmetics (emote packs, tower skins).
- Randomised rewards with published odds, which sit under loot-box rules in some countries (see section 18).
- Paid challenges historically used gem entry fees and ended at three losses (verify current formats).

**Live-ops**
- Monthly seasons with an arena theme and a balance pass. New cards ship every few months.
- Rotating special-rule events (draft, triple elixir, mirror, 2v2), global tournaments and clan wars (reworked in 2020).

**Retention hooks**
- The original chest timers were appointments: the four slots filled up, so players returned before winnings were wasted.
- Daily quests, season-pass progress and the trophy-road chase.
- Clan card requests and donations.

**Social layer**
- Clans of up to 50 share card requests and donations (the Clash of Clans donation idea, transplanted), clan chat and friendly battles.
- 2v2 battles, clan wars, spectating top players' replays (TV Royale), and a strong creator and esports scene.

**UX and onboarding notables**
- Portrait, one hand: drag a card onto the arena. Valid deployment zones light up while dragging.
- Training matches against AI teach elixir and towers before PvP.
- A whole match is readable in 3 minutes: three tower health bars and an elixir bar.
- Emotes are the only communication. The taunting laugh emote became infamous, and players got a mute option.

**Art and audio identity**: it reuses Clash of Clans characters, giving immediate recognition. Each card has a distinct silhouette and a deploy sound or voice, so players can read the opponent's play by ear and eye.

**Psychology principles used**
- Variable reward from chests (later from other random reward systems).
- Appointment mechanics from chest timers.
- Competence and mastery: deck building plus elixir counting (the "elixir trade").
- Loss aversion on trophies, which also feeds tilt and "one more match".
- Social comparison through ladders and clans.

**Innovations**
- Compressed RTS and MOBA decisions (lanes, towers, counters, tempo) into a 3-minute portrait duel.
- Used elixir as both resource and pacing clock, with acceleration at the end to force a finish.
- Turned timer-locked chests into the reward cadence. Many "Royale-likes" copied the format.

**Weaknesses and criticism**
- Card levels decide close matches, so players blame their wallets for losses. Ranked level caps were the response.
- Meta stagnation and balance complaints between monthly patches.
- Several economy and progression changes drew strong community backlash and partial reversals (verify specifics).
- Randomised paid rewards attract loot-box scrutiny.

**Lessons for designers**
1. Separate skill rating from power level, or players attribute every loss to spending. Offer a level-normalised competitive mode.
2. A short match needs a clock that forces a resolution (elixir acceleration plus overtime).
3. Keep deck size small (8) and hand smaller (4), so card cycling is countable by humans.
4. Give players a communication channel that cannot be abused, and a mute.

**Analogy hooks**
- Regenerating elixir with a cap → any real-time card or autobattler game, or real-time puzzle PvP.
- Crown towers (partial wins) → any three-objective scoring system.
- An 8-card deck with a 4-card hand → action roguelites with ability decks.
- Timer-locked reward slots → appointment rewards in any session-based game (use with care; see weaknesses).

**Ontology encoding**
```json
{"loops": [
  {"id": "cr_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "queue_with_8_card_deck", "reward": "matched_opponent", "next": "c2"},
    {"id": "c2", "action": "spend_elixir_deploy_cards", "reward": "tower_damage_and_trades", "next": "c3"},
    {"id": "c3", "action": "take_crowns_before_timer", "reward": "win_trophies_rewards", "next": "c4"},
    {"id": "c4", "action": "upgrade_cards_with_gold_and_duplicates", "reward": "stronger_deck", "next": "c1"}]},
  {"id": "cr_season", "type": "liveops", "period": "season", "steps": [
    {"id": "s1", "action": "play_matches_and_quests", "reward": "pass_progress", "next": "s2"},
    {"id": "s2", "action": "claim_pass_tiers", "reward": "gold_wild_cards_cosmetics", "next": "s1"}]}],
 "economy": {"currencies": [
  {"id": "elixir", "kind": "energy", "sources": ["in_match_regeneration"], "sinks": ["card_deploys"], "cap": 10},
  {"id": "gold", "kind": "soft", "sources": ["match_rewards", "pass", "shop"], "sinks": ["card_upgrades"], "cap": null},
  {"id": "gems", "kind": "hard", "sources": ["iap", "free_grants"], "sinks": ["reward_skips", "offers", "challenges"], "cap": null},
  {"id": "cards", "kind": "material", "sources": ["rewards", "donations", "shop"], "sinks": ["card_level_ups"], "cap": null},
  {"id": "trophies", "kind": "xp", "sources": ["wins"], "sinks": ["losses"], "cap": null}]}}
```

## 3. Brawl Stars

**Snapshot**
- Developer: Supercell.
- Release: soft launch in June 2017, global release in December 2018. During the long soft launch the team switched the controls from portrait to landscape, a widely reported example of changing the game itself in soft launch rather than only tuning it.
- Genre: top-down team hero shooter (mostly 3v3 modes plus a battle-royale mode, Showdown). Business model: free-to-play with IAP and a season pass (Brawl Pass, 2020).
- Scale: after a slower period, a strong resurgence in 2024 was widely reported in trade press (figures omitted; verify).

**Core loop**
1. Choose a Brawler and a mode and map from the current rotation.
2. Play a match of about 2–3 minutes. Move with the left stick and attack with the right: tap to auto-aim at the nearest target, or drag to aim manually.
3. Land hits to charge a Super ability, then use it to swing a fight.
4. Win the mode's objective: hold 10 gems for a countdown (Gem Grab), score goals (Brawl Ball), destroy the safe (Heist), win rounds (Knockout), or be the last standing (Showdown).
5. Earn trophies for that Brawler plus rewards.
6. Upgrade Brawlers' power levels with coins and power points, and unlock gadgets, star powers, gears and hypercharges. Return to step 1.

**Meta and progression**
- A roster of Brawlers with rarities, each with its own trophy count. Per-Brawler trophies give every character its own ladder.
- Power levels (up to 11) plus unlockable abilities: gadgets (limited-use actives), star powers (passives), gears and hypercharges (2023; verify current set).
- A ranked mode with draft for competitive players (format changed over time; verify).
- Loot boxes ("Brawl Boxes") were removed in December 2022 and replaced by direct progression (a Brawler unlock path and the pass). Random "Starr Drops" rewards were added in 2023 (verify current odds and sources).

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Coins | soft | pass, drops, events, trophy road | power-level upgrades, abilities |
| Power points | material | pass, drops, shop | power-level upgrades |
| Gems | hard | IAP, pass (small amounts) | pass, skins, offers |
| Bling | soft (cosmetic) | pass, drops | skins, pins |
| Credits | material | pass, drops, trophies | Brawler unlocks along a path |
| Trophies (per Brawler) | xp | wins | losses above thresholds |

**Monetization**
- Brawl Pass (free and paid tiers, plus a premium upsell tier; verify current structure).
- Skins, often in themed collections and collaborations, bought with gems or bling.
- Offers bundling power points, coins and new Brawlers. No ads.

**Live-ops**
- Seasons with a theme, new Brawlers on a regular cadence and balance changes. Maps and modes rotate on timers, including community maps from the map maker.
- Limited events (boss and co-op modes), IP collaborations and an annual championship circuit.

**Retention hooks**
- Per-Brawler trophy roads (always something close to a milestone).
- Daily and seasonal quests, pass progress, the next Brawler unlock, and mode rotation as a reason to check in.

**Social layer**
- Clubs (chat, club events), team codes for playing with friends, friendly games and spectating.
- 3v3 objectives make team play matter even with strangers.
- A strong creator scene and esports.

**UX and onboarding notables**
- Fast matchmaking gets a new player into a first match within minutes of install (verify). One button, two meanings: tap auto-aims (low skill floor), drag aims and shows the attack's range and spread before release (high skill ceiling).
- Bushes hide players, creating ambush play that stays readable from a top-down camera.

**Art and audio identity**: stylised 3D characters with exaggerated personalities and silhouettes that read on a small screen, bold team colours (blue vs red), voice lines for every Brawler, and punchy hit feedback.

**Psychology principles used**
- Competence: short matches with frequent, attributable successes.
- Collection and completion: the roster, skins and abilities.
- Variable reward: boxes originally, Starr Drops later.
- Relatedness: clubs and friends' teams.
- Goal-gradient: per-Brawler trophy thresholds.

**Innovations**
- A touch control scheme where one button covers both auto-aim and manual aim, adopted widely by later mobile shooters.
- Short rotating objective modes as a variety engine for one roster.
- A long soft launch used to change fundamentals (orientation, controls).
- A high-profile removal of paid loot boxes in 2022.

**Weaknesses and criticism**
- Power levels and abilities give unlocked players an edge in casual modes.
- New Brawlers that launch strong and are nerfed later (a recurring community complaint).
- Monetization changes and the return of random rewards after box removal drew criticism (verify specifics).
- Low-trophy matches have been reported to include bots (verify current disclosure).

**Lessons for designers**
1. Split skill floor and ceiling on the same input. Auto-aim by tap, precision by drag.
2. For mobile PvP, keep matches at 3 minutes or less and queues under 30 seconds. Many short modes beat one long one.
3. Give each character its own ladder so the roster stays relevant.
4. Use soft launch to change the game, not just tune numbers.

**Analogy hooks**
- Tap-auto and drag-manual aim → any mobile action game (twin-stick roguelites, sports shooting).
- A super meter charged by landing hits → fighting games, roguelite ultimates, card games (energy from damage).
- Timed mode rotation → daily puzzle modes, event maps in racing games.
- Per-character trophies → per-deck or per-class ladders.

**Ontology encoding**
```json
{"loops": [
  {"id": "bs_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "pick_brawler_and_rotating_mode", "reward": "match_start", "next": "c2"},
    {"id": "c2", "action": "move_and_aim_attack_charge_super", "reward": "eliminations_objective_progress", "next": "c3"},
    {"id": "c3", "action": "win_objective", "reward": "brawler_trophies_rewards", "next": "c4"},
    {"id": "c4", "action": "upgrade_power_level_unlock_abilities", "reward": "stronger_brawler", "next": "c1"}]},
  {"id": "bs_season", "type": "liveops", "period": "season", "steps": [
    {"id": "s1", "action": "complete_quests", "reward": "pass_tokens", "next": "s2"},
    {"id": "s2", "action": "claim_pass_tiers", "reward": "coins_power_points_skins", "next": "s1"}]}],
 "economy": {"currencies": [
  {"id": "coins", "kind": "soft", "sources": ["pass", "drops", "trophy_road"], "sinks": ["power_levels", "abilities"], "cap": null},
  {"id": "power_points", "kind": "material", "sources": ["pass", "drops", "shop"], "sinks": ["power_levels"], "cap": null},
  {"id": "gems", "kind": "hard", "sources": ["iap", "pass"], "sinks": ["pass", "skins", "offers"], "cap": null},
  {"id": "bling", "kind": "soft", "sources": ["pass", "drops"], "sinks": ["skins", "pins"], "cap": null},
  {"id": "credits", "kind": "material", "sources": ["pass", "drops"], "sinks": ["brawler_unlocks"], "cap": null},
  {"id": "brawler_trophies", "kind": "xp", "sources": ["wins"], "sinks": ["losses"], "cap": null}]}}
```

## 4. Rise of Kingdoms

**Snapshot**
- Developer: Lilith Games (Shanghai).
- Release: 2018. It first appeared under the name Rise of Civilizations (verify the regional launch sequence).
- Genre: 4X kingdom war, known in the Chinese industry as "SLG" (simulation game). Business model: free-to-play with IAP (gem packs, event bundles, VIP progression).
- Scale: a long-running top-grossing strategy title by store-intelligence rankings (figures omitted).

**Core loop**
1. In the city, upgrade buildings (the City Hall gates the rest), research technology and train troops: infantry, cavalry, archers and siege.
2. On the shared world map, send armies led by commanders to gather resources, fight barbarians, or attack forts and other players.
3. Armies march visibly across the map. Marches can be redirected mid-route, intercepted, or joined by allies in rallies.
4. Commanders gain experience and talent points from battles. Loot and gathered resources return to the city.
5. Spend everything on the next upgrades and return to step 1.

**Meta and progression**
- City Hall levels (up to 25) gate buildings and troop tiers.
- Commanders based on historical figures, each with a talent tree and skills levelled by duplicate tokens ("sculptures"). Commander pairs are the main build decision.
- Civilisations (Rome, China, Japan and others) give special units, architecture and bonuses.
- VIP levels grant permanent bonuses and are raised by spending or by daily VIP points.
- Seasonal "Kingdom versus Kingdom" (KvK) conflicts move matched kingdoms onto a separate contested map, and alliance battlegrounds run on a fixed schedule.

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Food, wood, stone, gold | soft | gathering, production buildings, barbarians, events | buildings, research, troops, healing |
| Gems | hard | IAP, gathering gem deposits, events | speedups, resources, VIP, chests |
| Speedups (building, research, training, healing) | material | events, packs, daily tasks | timer reduction |
| Action points | energy | regeneration, items | barbarian attacks |
| Commander sculptures | material | keys and chests, events, shops | commander skill upgrades |
| Alliance credits and event tokens | event | alliance activity, events | alliance shop, event shops |

**Monetization**
- Bundles tied to event goals ("spend speedups to score points" events, paired with packs of speedups).
- Gem packs, monthly cards and VIP progression.
- Random chest and wheel-style events for top commanders (odds disclosed in-game; verify).
- Spending concentrates around KvK, when power differences decide who controls the map.

**Live-ops**
- A dense rotating calendar of point events (build, train, kill), commander releases and themed festivals.
- KvK seasons and scheduled alliance battlegrounds. New commanders are paced to the kingdom's age.

**Retention hooks**
- Building, research and training queues finishing, and gathering marches that complete on a timer.
- Alliance help: members tap to shave time off each other's timers.
- Scheduled war events that the alliance plans for.

**Social layer**
- Alliances with territory (flags and forts), rallies (several players launch one attack), shared research, chat with translation, and leadership roles.
- Kingdom politics: diplomacy between top alliances is a large part of the endgame.
- KvK makes the alliance's survival depend on everyone showing up.

**UX and onboarding notables**
- A seamless zoom from city to world map with no loading screen.
- Free marching: armies are visible and steerable, so players can read the map like a strategy board.
- A heavily guided tutorial with quest chains. The UI is dense, as is typical of the genre.

**Art and audio identity**: stylised-realistic historical civilisations, each with distinct architecture and special units. An orchestral, historical score and a map rich with landmarks.

**Psychology principles used**
- Social obligation and reciprocity: alliance help and rallies.
- Status and competence (power rankings, kill points); loss aversion (troops die or need healing, cities can be burned).
- Sunk cost: years of investment in one account.
- Territoriality: owning map space with your group.

**Innovations**
- Free marching and real-time map combat with interceptions, replacing the more rigid point-to-point marches of earlier mobile SLGs.
- A civilisation theme with commanders as a broader, history-flavoured appeal.
- A seamless city-to-world map.

**Weaknesses and criticism**
- Pay-to-win: the highest spenders decide KvK outcomes.
- Heavy time demands: coordinated war at fixed hours across time zones.
- Farm accounts and bots, server consolidation, and the onboarding difficulty for late joiners.
- Ethical criticism of event-pack pressure and VIP spending loops in a game with a strong social obligation.

**Lessons for designers**
1. A 4X lives on its alliances. Design the help, rally and territory verbs first.
2. Seasonal conflict with matched kingdoms keeps servers competitive, and it needs a catch-up path for late joiners.
3. Visible movement on a shared map makes strategy legible and creates stories.
4. Pace commander releases to server age to manage power creep.

**Analogy hooks**
- Alliance "help" taps → any timer game with teams (puzzle teams, farming co-ops).
- Matched seasonal maps → MMO seasons, roguelite leagues.
- Rallies (several owners, one attack) → co-op raids in RPGs.
- Free marching → real-time map layers in any strategy game.

**Ontology encoding**
```json
{"loops": [
  {"id": "rok_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "march_commander_army_on_world_map", "reward": "gathered_resources_or_battle_loot", "next": "c2"},
    {"id": "c2", "action": "fight_barbarians_forts_or_players", "reward": "commander_xp_kill_points", "next": "c3"},
    {"id": "c3", "action": "spend_on_buildings_research_troops", "reward": "power_growth", "next": "c1"}]},
  {"id": "rok_social", "type": "social", "period": "daily", "steps": [
    {"id": "s1", "action": "send_alliance_help_and_join_rallies", "reward": "faster_timers_shared_wins", "next": "s2"},
    {"id": "s2", "action": "hold_alliance_territory", "reward": "territory_bonuses", "next": "s1"}]},
  {"id": "rok_kvk", "type": "liveops", "period": "season", "steps": [
    {"id": "k1", "action": "prepare_for_kingdom_vs_kingdom", "reward": "event_points", "next": "k2"},
    {"id": "k2", "action": "fight_kvk_for_map_control", "reward": "kingdom_rewards_titles", "next": "k1"}]}],
 "economy": {"currencies": [
  {"id": "food_wood_stone_gold", "kind": "soft", "sources": ["gathering", "production", "barbarians"], "sinks": ["buildings", "research", "troops", "healing"], "cap": null},
  {"id": "gems", "kind": "hard", "sources": ["iap", "gem_deposits", "events"], "sinks": ["speedups", "vip", "chests"], "cap": null},
  {"id": "speedups", "kind": "material", "sources": ["events", "packs"], "sinks": ["timers"], "cap": null},
  {"id": "action_points", "kind": "energy", "sources": ["regeneration", "items"], "sinks": ["barbarian_attacks"], "cap": null},
  {"id": "sculptures", "kind": "material", "sources": ["chests", "events", "shops"], "sinks": ["commander_skills"], "cap": null}]}}
```

## 5. Last War: Survival

**Snapshot**
- Developer: First Fun (First Fun HK Ltd, per Wikipedia). The App Store seller and publisher is FUNFLY PTE. LTD., a Singapore company incorporated in February 2024, which took over development and publishing from First Fun ([App Store listing](https://apps.apple.com/us/app/-/id6448786147); [Wikipedia: Last War: Survival Game](https://en.wikipedia.org/wiki/Last_War:_Survival_Game), which carries a quality banner, so treat its corporate history as provisional).
- Release: 2023.
- Genre: zombie-apocalypse 4X/SLG with a casual mini-game layer. Business model: free-to-play with IAP.
- Scale: listed among the top-grossing mobile games of Q1 2026 by Sensor Tower data (section 18, [V1]).

**Core loop**
1. Early levels are short casual mini-games of the kind its ads show: steer a squad down a lane, pick multiplier gates and shoot oncoming zombies. These introduce heroes and power before the base layer opens.
2. Build and upgrade the headquarters and production buildings, research and train troops.
3. Level, promote and equip heroes, who lead squads into PvE (zombie stages, map targets) and PvP.
4. Do the day's tasks on the world map (missions, zombie hunts, cargo runs that can be raided) for resources and power.
5. Contribute to your alliance's daily score against a matched rival alliance, then return to step 2.

**Meta and progression**
- Headquarters level gates everything, as in all SLGs.
- Hero collection, levelling and promotion; squad composition and formations.
- Seasons on the world map with server-wide objectives and contested capital control (verify season structure).
- Mini-game levels remain as a side progression track (verify how much of the experience they occupy in current builds).

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Food, iron, coins (resource set; verify names) | soft | production, map tasks, events | buildings, research, troops |
| Diamonds | hard | IAP, events, achievements | speedups, items, offers |
| Speedups | material | events, packs | timers |
| Hero shards and upgrade materials | material | recruitment, events, packs | hero levels and promotions |
| Stamina | energy | regeneration, items | map attacks |
| Alliance and event points | event | daily themed activities | rewards, rankings |

**Monetization**
- Event-linked bundles and value packs, recruitment (hero summons, with odds disclosed; verify), monthly cards and passes.
- The daily themed alliance competition and rotating "do X now for points" windows (widely described by players as Alliance Duel and Arms Race; verify current names) create recurring spend moments tied to specific resources.

**Live-ops**
- A dense daily and weekly calendar: themed alliance competitions, rotating time-boxed point themes, zombie events and server seasons.
- New heroes and seasons paced to server age (verify).

**Retention hooks**
- Daily alliance competition (your score is your team's score).
- Time-boxed theme windows during the day.
- Timers, map tasks and stamina regeneration.

**Social layer**
- Alliances with shared objectives, rallies, territory and leadership roles.
- Server-level politics and capital wars.
- Matched daily competition against another alliance.

**UX and onboarding notables**
- The first minutes play like a hybrid-casual runner: one thumb, instant readability, arithmetic gates. The game then hands over to the 4X layer.
- Short daily tasks are listed in a checklist for players with only minutes to spare.

**Art and audio identity**: bright, clean military-apocalypse styling with readable 3D heroes and a casual tone in the mini-games that softens a war theme.

**Psychology principles used**
- A low-friction casual hook (competence in seconds) before the complexity arrives.
- Social obligation: alliance daily points.
- Time-boxed goals and scarcity: theme windows.
- Status: power ranking and server titles.

**Innovations**
- At scale, it showed that a hybrid-casual mini-game funnel (cheap installs, broad appeal) can feed a deep, high-spend 4X. Earlier 4X games had used puzzle mini-game ads, and this one put the mini-game inside the product as its opening.
- Daily alliance-vs-alliance themes that turn ordinary progression into team competition.

**Weaknesses and criticism**
- Ad-to-game mismatch: many players arrive for the mini-game and find a 4X. This is a recurring theme in low-star reviews (grade C; verify current state).
- Pay-to-win and very high spending ceilings.
- Time and coordination pressure from the alliance calendar.

**Lessons for designers**
1. A casual top of funnel works only if it is honest. The advertised mode must be in the game, and the transition to the deeper game must be explained.
2. Theme windows ("this hour, training scores double") coordinate a whole server's activity and spending. Use them for focus, not pressure.
3. Turn solo progression into team score to make every daily action social.

**Analogy hooks**
- A mini-game opening that hands over to a deep meta → narrative games, sims, RPGs with a hybrid-casual hook.
- Rotating time-boxed point themes → any game with many progression systems that need attention spread across them.
- Daily matched team competition → puzzle teams, sports clubs.

**Ontology encoding**
```json
{"loops": [
  {"id": "lw_hook", "type": "core", "period": "seconds", "steps": [
    {"id": "h1", "action": "steer_squad_pick_multiplier_gates", "reward": "squad_size_and_firepower", "next": "h2"},
    {"id": "h2", "action": "shoot_zombie_wave", "reward": "level_clear_resources", "next": "h1"}]},
  {"id": "lw_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "upgrade_hq_research_train", "reward": "power_growth", "next": "c2"},
    {"id": "c2", "action": "level_and_promote_heroes", "reward": "squad_strength", "next": "c3"},
    {"id": "c3", "action": "run_map_tasks_and_attacks", "reward": "resources_points", "next": "c1"}]},
  {"id": "lw_social", "type": "social", "period": "daily", "steps": [
    {"id": "s1", "action": "score_in_daily_alliance_theme", "reward": "alliance_points", "next": "s2"},
    {"id": "s2", "action": "beat_matched_rival_alliance", "reward": "alliance_rewards", "next": "s1"}]}],
 "economy": {"currencies": [
  {"id": "base_resources", "kind": "soft", "sources": ["production", "map_tasks", "events"], "sinks": ["buildings", "research", "troops"], "cap": null},
  {"id": "diamonds", "kind": "hard", "sources": ["iap", "events"], "sinks": ["speedups", "items", "offers"], "cap": null},
  {"id": "hero_shards", "kind": "material", "sources": ["recruitment", "events", "packs"], "sinks": ["hero_promotion"], "cap": null},
  {"id": "stamina", "kind": "energy", "sources": ["regeneration", "items"], "sinks": ["map_attacks"], "cap": null},
  {"id": "alliance_points", "kind": "event", "sources": ["themed_daily_activity"], "sinks": [], "cap": null}]}}
```

## 6. Whiteout Survival

**Snapshot**
- Developer and publisher: Century Games (Century Games PTE. LTD. on the Google Play listing).
- Release: 2023.
- Genre: survival-themed 4X/SLG set in a frozen apocalypse. Business model: free-to-play with IAP.
- Scale: listed among the top-grossing mobile games of Q1 2026 by Sensor Tower data (section 18, [V1]).

**Core loop**
1. Keep the city's central furnace burning and the survivors warm. Assign survivors to jobs (gathering, cooking, hunting) and watch their status: cold, hungry, sick.
2. Upgrade the furnace, which gates every other building, then build and upgrade production, troop and research buildings.
3. Explore with heroes in PvE stages and on the world map: gather, hunt beasts, and fight other players.
4. Join alliance events such as scheduled rallies against a boss.
5. Spend the gains on the next upgrades and return to step 1.

**Meta and progression**
- Furnace level as the master gate, with further high-end tiers after the base cap (verify current structure).
- Hero collection released in generations: new hero sets unlock as the server ("state") ages (verify intervals).
- Chief gear and other account-wide power layers.
- State-vs-state seasonal conflict, alliance battlegrounds and scheduled alliance bosses (verify current event names and timing).

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Meat, wood, coal, iron (verify set) | soft | survivor jobs, gathering, events | buildings, troops, research, furnace fuel |
| Gems | hard | IAP, events | speedups, items, offers |
| Speedups | material | events, packs | timers |
| Hero shards and gear materials | material | recruitment, events, packs | hero stars, gear |
| Stamina | energy | regeneration, items | beast hunts, map actions |

**Monetization**
- Event bundles and value packs, hero recruitment with disclosed odds (verify), monthly cards and passes.
- Spending peaks around new hero generations and state-vs-state events.

**Live-ops**
- Daily and weekly alliance events, state-vs-state seasons, and hero generations paced to server age.
- Holiday and themed events on a dense calendar.

**Retention hooks**
- Survivor needs and furnace fuel (the city visibly suffers if neglected early on).
- Building and research queues, alliance event schedules and stamina regeneration.

**Social layer**
- Alliances with rallies, territory, shared boss events and leadership roles.
- State-level politics and state-vs-state wars.

**UX and onboarding notables**
- The early game reads as a survival colony sim, and the player learns production chains by keeping visible people alive. The cold, the furnace and the rescued survivors give each early upgrade an emotional reason.
- The 4X layers (map, alliances, PvP) open gradually after that framing.

**Art and audio identity**: a cold blue-white palette with the warm orange of the furnace at the centre of the screen, readable small survivors with status icons, and a sombre but not grim tone.

**Psychology principles used**
- Care and responsibility: needs-based framing (players protect visible survivors).
- Goal-gradient: furnace levels.
- Social obligation in alliance events.
- Novelty and power-chase from hero generations.

**Innovations**
- Used a survival city-builder fantasy (often compared with the PC game Frostpunk) as the onboarding and theme for a mass-market 4X. Systems are taught through needs rather than menus.
- Server-age-gated hero generations as a structured arc for each new server.

**Weaknesses and criticism**
- Pay-to-win and power creep with each hero generation, which makes older heroes obsolete.
- Time demands of the alliance event calendar.
- The survival framing fades as the game becomes a standard 4X, a gap between the promised and the actual long-term fantasy.

**Lessons for designers**
1. Theme can carry onboarding: teach production through needs the player can see and feel.
2. Gate content generations by server age to give every server a fresh, legible power arc.
3. Keep the opening fantasy alive in the late game, or expect players to feel the bait-and-switch.

**Analogy hooks**
- A central heat source that gates the city → any "core building" progression (farm sims, colony builders).
- Visible needs as a tutorial → idle tycoon and pet games.
- Server-age content generations → seasonal MMOs, live roguelites.

**Ontology encoding**
```json
{"loops": [
  {"id": "ws_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "assign_survivors_keep_furnace_fuelled", "reward": "resources_and_healthy_city", "next": "c2"},
    {"id": "c2", "action": "upgrade_furnace_and_buildings", "reward": "unlocks_and_power", "next": "c3"},
    {"id": "c3", "action": "explore_and_hunt_with_heroes", "reward": "materials_hero_xp", "next": "c1"}]},
  {"id": "ws_social", "type": "social", "period": "daily", "steps": [
    {"id": "s1", "action": "join_scheduled_alliance_rally", "reward": "alliance_event_rewards", "next": "s2"},
    {"id": "s2", "action": "fight_state_vs_state", "reward": "state_rewards", "next": "s1"}]}],
 "economy": {"currencies": [
  {"id": "survival_resources", "kind": "soft", "sources": ["survivor_jobs", "gathering"], "sinks": ["buildings", "troops", "furnace_fuel"], "cap": null},
  {"id": "gems", "kind": "hard", "sources": ["iap", "events"], "sinks": ["speedups", "items", "offers"], "cap": null},
  {"id": "hero_shards", "kind": "material", "sources": ["recruitment", "events"], "sinks": ["hero_stars"], "cap": null},
  {"id": "stamina", "kind": "energy", "sources": ["regeneration", "items"], "sinks": ["beast_hunts"], "cap": null}]}}
```

## 7. Lords Mobile

**Snapshot**
- Developer and publisher: IGG.
- Release: 2016.
- Genre: 4X kingdom war combined with a hero-collection RPG. Business model: free-to-play with IAP (gems, packs, VIP).
- Scale: a long-running grossing title in Western and Southeast Asian markets by store-intelligence rankings (figures omitted).

**Core loop**
1. Play Hero Stages: a PvE campaign where a team of five heroes auto-battles and the player triggers ultimates. Stages give hero experience, gear materials and hero shards, and are scored by stars.
2. Build the castle, research and train troops (infantry, ranged, cavalry, siege) in increasing tiers.
3. Gather on the kingdom map, hunt monsters with energy for materials, and attack or rally against other players.
4. Forge gear for the account's leader and upgrade heroes.
5. Join guild events and return to step 1.

**Meta and progression**
- Castle level gates buildings and troop tiers.
- Heroes with ranks, gear and skills fight in Hero Stages and in an asynchronous arena (Colosseum).
- Leader gear forged from monster-hunt materials, plus companion creatures and talent trees (verify current layers).
- Guild competitions, solo "points" events and kingdom-vs-kingdom events.

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Food, stone, timber, ore, gold | soft | production, gathering, events | buildings, research, troops |
| Gems | hard | IAP, events, gathering gem mines | speedups, shields, items, VIP |
| Speedups | material | events, guild gifts, packs | timers |
| Hero shards and gear materials | material | Hero Stages, monster hunts, events | hero ranks, gear forging |
| Stage energy and hunt energy | energy | regeneration, items | Hero Stages, monster hunts |
| Guild coins | soft | guild activity | guild shop |

**Monetization**
- Value packs with escalating price tiers, gem packs, monthly cards and VIP.
- Guild gifts: when a member buys certain packs, guildmates receive gift chests. Spending becomes a visible, reciprocal social act.
- Shields, troop-protection items and instant speedups around war events.

**Live-ops**
- Rotating solo points events, guild festivals, kingdom-vs-kingdom events and themed holiday events.
- New heroes and gear tiers released over time.

**Retention hooks**
- Hero Stage energy, monster-hunt energy and timers.
- Guild help and guild gifts.
- Scheduled guild and kingdom events.

**Social layer**
- Guilds with help, gifts, rallies, shared territory and guild-vs-guild events.
- Kingdom politics and kingdom-vs-kingdom conflicts.

**UX and onboarding notables**
- The hero campaign gives a solo, PvP-free on-ramp with clear 3-star goals before the player meets kingdom war.
- Defensive tools (shelters to hide troops, peace shields) let players protect themselves while offline.

**Art and audio identity**: colourful high-fantasy cartoon style for heroes and monsters, a brighter, less militaristic tone than many 4X games, and readable hero silhouettes in auto-battles.

**Psychology principles used**
- Competence from the RPG campaign.
- Reciprocity and social proof through guild gifts.
- Loss aversion: troops die in battle when the infirmary is full, and accounts can be "zeroed".
- Status: power and might rankings.

**Innovations**
- Combined a full hero-collection RPG campaign with kingdom war in one product, giving two parallel motivations and a solo on-ramp.
- Popularised purchase-triggered guild gifts that spread a payer's spend across the group.

**Weaknesses and criticism**
- Zeroing: losing an army that took months to build can end a player's engagement.
- Whale dominance and escalating pack pricing.
- Guild-gift pressure (a social nudge to spend) is ethically ambiguous.

**Lessons for designers**
1. Give a war game a solo PvE track so new players build competence before facing other people.
2. Offline protection (shelters, shields) is essential when losses are permanent.
3. If purchases benefit the group, keep the benefit modest and never reveal who did not pay.

**Analogy hooks**
- A PvE hero campaign beside a PvP layer → any competitive game needing an on-ramp.
- Purchase-triggered team gifts → team chests in puzzle games, guild perks in RPGs.
- A shelter that hides some troops → partial protection in raid games.

**Ontology encoding**
```json
{"loops": [
  {"id": "lm_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "clear_hero_stage_with_five_heroes", "reward": "hero_xp_materials_stars", "next": "c2"},
    {"id": "c2", "action": "build_research_train", "reward": "castle_power", "next": "c3"},
    {"id": "c3", "action": "hunt_monsters_and_gather", "reward": "gear_materials_resources", "next": "c4"},
    {"id": "c4", "action": "forge_gear_upgrade_heroes", "reward": "account_power", "next": "c1"}]},
  {"id": "lm_social", "type": "social", "period": "daily", "steps": [
    {"id": "s1", "action": "help_guildmates_open_guild_gifts", "reward": "speedups_items", "next": "s2"},
    {"id": "s2", "action": "rally_and_guild_events", "reward": "guild_coins_rankings", "next": "s1"}]}],
 "economy": {"currencies": [
  {"id": "kingdom_resources", "kind": "soft", "sources": ["production", "gathering"], "sinks": ["buildings", "research", "troops"], "cap": null},
  {"id": "gems", "kind": "hard", "sources": ["iap", "events", "gem_mines"], "sinks": ["speedups", "shields", "vip"], "cap": null},
  {"id": "hero_shards", "kind": "material", "sources": ["hero_stages", "events"], "sinks": ["hero_ranks"], "cap": null},
  {"id": "stage_energy", "kind": "energy", "sources": ["regeneration", "items"], "sinks": ["hero_stages"], "cap": null},
  {"id": "guild_coins", "kind": "soft", "sources": ["guild_activity"], "sinks": ["guild_shop"], "cap": null}]}}
```

## 8. Boom Beach

**Snapshot**
- Developer: Supercell.
- Release: soft launch in 2013, global release in March 2014.
- Genre: base-builder with island raids against AI and player bases, plus co-op operations. Business model: free-to-play with IAP (diamonds).
- Scale: successful but smaller than Clash of Clans (rankings only; figures omitted). It is often studied as Supercell's "different take" on the base-builder.

**Core loop**
1. Explore an archipelago map with the radar, revealing AI-controlled and player-controlled bases.
2. Attack a base: troops land from landing craft on the beach, and the gunboat spends energy on abilities.
3. Direct the troops with a flare (they move to where it lands) and support them with artillery, barrages, medkits, smoke screens and shock bombs.
4. Win by destroying the enemy headquarters. Nothing else counts.
5. Take loot and victory points. Captured resource bases produce resources over time.
6. Upgrade buildings, defences and troops, then return to step 1.

**Meta and progression**
- Headquarters level gates buildings and defences. The armory upgrades troops and gunboat abilities.
- Victory points (the trophy equivalent) raise the output of captured resource bases.
- Statues built from power stones give permanent percentage boosts. Heroes were added in 2017 (verify current state).
- Task Force membership unlocks weekly co-op operations.

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Gold, wood, stone, iron | soft | raids, captured resource bases, production | buildings, defences, troops, research |
| Diamonds | hard | IAP, exploration rewards, achievements | timer skips, resources, builders |
| Power stones (pieces, crystals, idols) | material | raids, special targets, events | statues |
| Intel | event | Task Force contributions and operations | Task Force rewards |
| Gunboat energy | energy | in-battle, refilled by destroying buildings | flares, barrages, medkits and other abilities |
| Victory points | xp | wins | none (drives resource-base output) |

**Monetization**
- Diamonds for skips, resources and builders, sold on a price ladder with offers.
- No paid random loot in the core design (verify current offers). No ads.

**Live-ops**
- Weekly operations for task forces.
- Recurring special enemies and event bases with escalating difficulty, run on a weekly rhythm.
- Seasonal events and periodic large updates.

**Retention hooks**
- Resource-base production, upgrade timers and weekly operations that the task force schedules.
- Escalating special targets that reset on a cadence.

**Social layer**
- Task forces (cooperative groups) that attack a shared operation map together and earn rewards based on group progress.
- Chat and shared intel. Less PvP-centric than Clash of Clans.

**UX and onboarding notables**
- A single win condition (the headquarters) makes every battle's goal obvious.
- The flare gives players control over troop movement without micromanaging each unit, and works well on touch.
- PvE targets throughout the map reduce the stress of being attacked by stronger players.

**Art and audio identity**: a sunny tropical setting, a cartoon military style with chunky vehicles and soldiers, bright water and sand that make bases readable from above, and comic villains.

**Psychology principles used**
- Competence and planning: choosing landing points and timing abilities.
- Curiosity: map exploration with fog.
- Cooperation and shared goals: operations.
- Endowment: base layout and resource bases.

**Innovations**
- Ability-directed troops (the flare plus energy-based support powers) as a touch-friendly tactical layer on top of a base raid.
- Weekly co-op PvE operations as a group ritual in a base-builder.
- A single-objective win condition that simplified raid evaluation.

**Weaknesses and criticism**
- Long-term progression felt slow and some players described content droughts between updates (grade C).
- PvP raid losses on captured resource bases frustrated less active players.
- Smaller audience than its sibling, so fewer resources for live content.

**Lessons for designers**
1. One clear win condition reduces cognitive load and speeds up evaluation.
2. Indirect control (a flare) is often better on touch than per-unit commands.
3. Weekly co-op PvE gives a group a reason to meet without PvP toxicity.
4. A second title in the same genre needs a clearly different fantasy, not just new art.

**Analogy hooks**
- The flare (direct a crowd by marking a point) → crowd games, RTS-lite, survival mode commands.
- A battle-energy pool refilled by destruction → ability economies in action roguelites.
- Weekly co-op operations → raid bosses in RPGs, puzzle team events.

**Ontology encoding**
```json
{"loops": [
  {"id": "bb_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "explore_map_pick_target", "reward": "target_selected", "next": "c2"},
    {"id": "c2", "action": "land_troops_direct_with_flare_and_abilities", "reward": "defences_destroyed_energy_gained", "next": "c3"},
    {"id": "c3", "action": "destroy_headquarters", "reward": "loot_victory_points", "next": "c4"},
    {"id": "c4", "action": "upgrade_base_and_troops", "reward": "power_growth", "next": "c1"}]},
  {"id": "bb_social", "type": "social", "period": "weekly", "steps": [
    {"id": "s1", "action": "attack_shared_operation_map", "reward": "intel_contribution", "next": "s2"},
    {"id": "s2", "action": "complete_operation_with_task_force", "reward": "group_rewards", "next": "s1"}]}],
 "economy": {"currencies": [
  {"id": "gold_wood_stone_iron", "kind": "soft", "sources": ["raids", "resource_bases"], "sinks": ["buildings", "troops"], "cap": null},
  {"id": "diamonds", "kind": "hard", "sources": ["iap", "exploration", "achievements"], "sinks": ["timer_skips", "resources", "builders"], "cap": null},
  {"id": "power_stones", "kind": "material", "sources": ["raids", "special_targets"], "sinks": ["statues"], "cap": null},
  {"id": "intel", "kind": "event", "sources": ["operations"], "sinks": ["task_force_rewards"], "cap": null},
  {"id": "gunboat_energy", "kind": "energy", "sources": ["battle_start", "buildings_destroyed"], "sinks": ["abilities"], "cap": null},
  {"id": "victory_points", "kind": "xp", "sources": ["wins"], "sinks": [], "cap": null}]}}
```

## 9. Plants vs. Zombies 2

**Snapshot**
- Developer: PopCap Games (owned by Electronic Arts since 2011).
- Release: 2013 (subtitled "It's About Time"). The original Plants vs. Zombies (2009) was a premium game on PC and later mobile.
- Genre: lane tower defense. Business model: free-to-play with IAP; some builds and regions include ads (verify current placements).
- Scale: a widely played sequel (figures omitted). It is mainly studied as the premium-to-F2P conversion of a famous IP.

**Core loop**
1. Choose a loadout of seed packets (plants) for the level.
2. Collect sun, which falls from the sky and is produced by sunflowers, and spend it to plant on a 5-row grid.
3. Defend each lane against zombie waves. Each plant has a role: produce, attack, block, or area damage.
4. Feed a plant Plant Food (dropped by glowing zombies or bought) to trigger its super ability.
5. Survive the final wave. Earn coins, seed packets and progress on the world map, then return to step 1.

**Meta and progression**
- Worlds set in different time periods, each with environmental rules: minecart rails, tides that change the grid, ice that freezes plants, and others (verify world list in current builds).
- Plant levels raised with seed packets and coins (a leveling system added in a later update; verify date), plus families and boosts.
- An arena mode with weekly competition and side quest lines (verify current modes).

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Sun | energy (in-level) | sunflowers, falling sun | planting |
| Coins | soft | levels, quests | plant upgrades, power-ups, Plant Food |
| Gems | hard | IAP, quests, events | premium plants, packs, upgrades |
| Seed packets | material | levels, rewards, packs | plant levels |
| Plant Food | material | glowing zombies, purchases | plant super abilities |

**Monetization**
- Premium plants sold directly or through packs.
- Gems and coins for power-ups (direct touch powers such as pinch, flick and zap), plant upgrades and bundles.
- Randomised reward containers in some modes (verify current odds and presence).

**Live-ops**
- New worlds and plants over the years, then seasonal events, arena seasons and quest lines (verify current cadence).

**Retention hooks**
- The next world and its new mechanic, plant collection and levels, and arena weekly results.

**Social layer**
- Light: arena leaderboards. The design is primarily single-player.

**UX and onboarding notables**
- The 5-row lawn is readable at a glance on a phone. Each lane is a separate small problem.
- New plants are introduced one at a time with a level that teaches them.
- Plant Food is a big, satisfying "super" moment the player controls.

**Art and audio identity**: a cartoon art style with expressive plants and comedic zombies, catchy music, and humorous almanac entries. Each world re-themes both art and music.

**Psychology principles used**
- Competence and mastery: lane management.
- Curiosity: the next world and its rule.
- Collection: plants.
- Humour as emotional reward.

**Innovations**
- Time-travel worlds, each with an environmental rule layered on the classic lane grid.
- A super ability for every plant via one shared resource (Plant Food).
- One of the most visible conversions of a premium franchise to free-to-play.

**Weaknesses and criticism**
- Paywalled premium plants created a perceived advantage in a game that used to be complete for a one-time price.
- The plant-leveling system added grind and was criticised by long-time players (grade C).
- Difficulty spikes that sell power-ups, and some reports that regional versions monetize more aggressively (verify).

**Lessons for designers**
1. A 5-lane grid is the most readable TD layout for phones: one decision space per lane.
2. Give each world one new environmental rule, not just new art.
3. A single shared "super" resource makes every unit exciting and creates a spend-or-save choice.
4. Converting a premium IP to F2P costs goodwill. Keep the core content complete and sell breadth or convenience, not walls.

**Analogy hooks**
- A lane grid with roles (produce, attack, block) → card battlers, auto-battlers, rhythm games with lanes.
- Plant Food as a universal super → any unit-based game with an ultimate meter.
- World rules → level packs in puzzle games (ice, tides, conveyors).

**Ontology encoding**
```json
{"loops": [
  {"id": "pvz2_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "choose_seed_packet_loadout", "reward": "plan", "next": "c2"},
    {"id": "c2", "action": "collect_sun_and_plant_in_lanes", "reward": "defence_line", "next": "c3"},
    {"id": "c3", "action": "use_plant_food_on_key_plant", "reward": "super_ability_burst", "next": "c4"},
    {"id": "c4", "action": "survive_final_wave", "reward": "coins_seed_packets_map_progress", "next": "c1"}]},
  {"id": "pvz2_meta", "type": "meta", "period": "session", "steps": [
    {"id": "m1", "action": "level_up_plants", "reward": "stronger_plants", "next": "m2"},
    {"id": "m2", "action": "unlock_next_world_rule", "reward": "new_mechanic", "next": "m1"}]}],
 "economy": {"currencies": [
  {"id": "sun", "kind": "energy", "sources": ["sunflowers", "falling_sun"], "sinks": ["planting"], "cap": null},
  {"id": "coins", "kind": "soft", "sources": ["levels", "quests"], "sinks": ["upgrades", "power_ups"], "cap": null},
  {"id": "gems", "kind": "hard", "sources": ["iap", "quests"], "sinks": ["premium_plants", "packs"], "cap": null},
  {"id": "seed_packets", "kind": "material", "sources": ["levels", "packs"], "sinks": ["plant_levels"], "cap": null},
  {"id": "plant_food", "kind": "material", "sources": ["glowing_zombies", "purchase"], "sinks": ["super_abilities"], "cap": null}]}}
```

## 10. Bloons TD 6

**Snapshot**
- Developer: Ninja Kiwi (New Zealand).
- Release: 2018.
- Genre: path-based tower defense. Business model: premium (paid upfront) with optional IAP and no ads. Versions have also been offered through subscription catalogues such as Apple Arcade (as Bloons TD 6+) and Netflix (verify current availability).
- Scale: a long-running best-seller on mobile and Steam by chart rankings (figures omitted).

**Core loop**
1. Choose a map, difficulty (Easy, Medium, Hard, Impoppable) and mode.
2. Place monkey towers beside the track. Bloons travel along it in rounds.
3. Pop bloons for in-match cash and spend it on new towers or upgrades.
4. Upgrade each tower along three paths of five tiers, under a crosspath rule: one path may reach tier 5 while a second path reaches at most tier 2.
5. Counter bloon properties (camo, lead, regrow, fortified, armoured blimps), which forces composition rather than spamming one tower.
6. Survive the final round. Earn Monkey Money, experience and medals, then return to step 1.

**Meta and progression**
- Per-tower experience unlocks upgrades. Monkey Knowledge is a perk tree bought with points from levelling.
- Heroes (one per match) level up during the match.
- Medals for each map, difficulty and mode combination; a cosmetic trophy store.
- Paragons (2021) add a sixth tier that merges a tower's three paths when the requirements are met.

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| In-match cash | energy (in-match) | popping bloons, income towers | towers, upgrades |
| Monkey Money | soft | completing maps, events, IAP | heroes, powers, insta monkeys, unlocks |
| Monkey Knowledge points | material | player levels | perk tree |
| Trophies | event | events, races, bosses | cosmetic store |
| Insta Monkeys and powers | material | rewards, Monkey Money, IAP | one-off placements and boosts |

**Monetization**
- The upfront price buys the complete core game.
- Optional IAP: Monkey Money packs, heroes, convenience (double cash in match), powers and cosmetics. Paid DLC expansions have been added (verify current DLC list).
- No energy, no ads.

**Live-ops**
- Regular free content updates adding towers, heroes, maps and modes (verify cadence).
- Daily challenges, weekly races (time-attack leaderboards), boss events, odysseys and team competitions.
- Four-player co-op and a content browser for player-made challenges and maps.

**Retention hooks**
- Medal completion, new maps and towers from each update, and weekly races and bosses.
- The challenge browser provides user-generated content.

**Social layer**
- Co-op (up to four players), team-based territory events, races and boss leaderboards, and sharing challenges.

**UX and onboarding notables**
- Tower ranges and the crosspath rule are shown on the upgrade panel, so the build space is legible.
- Fast-forward and free play after victory respect players' time.
- Difficulty and modes multiply content from the same maps.

**Art and audio identity**: bright, clean cartoon art where bloon colour encodes its layers and properties, satisfying popping sounds and visual feedback, and readable towers even when the screen is full.

**Psychology principles used**
- Mastery and experimentation: build combinatorics.
- Completion: medals across difficulties.
- Competence: visible popping counts.
- Fairness: purchases do not block content.

**Innovations**
- The crosspath rule as a compact depth engine. Per tower there are 64 valid upgrade states (including the empty one) and 6 "maximum" builds of the 5-2-0 shape. Multiplied across the roster, this gives a huge composition space from a small UI (counts derived from the stated rule).
- A sustained premium plus free-updates model in a market dominated by free-to-play.

**Weaknesses and criticism**
- IAP in a paid game draws criticism from some players, though it is widely considered fair.
- Monkey Money grind for heroes without IAP.
- Late rounds can strain lower-end devices (grade C; verify).
- Several versions (store, subscription catalogues) fragment saves and progress (verify).

**Lessons for designers**
1. One clear constraint on an upgrade tree (one path to 5, one path to 2) produces depth without UI clutter.
2. Enemy properties that require specific counters teach composition.
3. A premium game with steady free updates can sustain a long tail and strong word of mouth.
4. Multiply content with difficulty and modes before building new maps.

**Analogy hooks**
- A three-path tree with a crosspath cap → roguelite skill trees, idle-game upgrades, hero builds.
- Property counters (camo, lead) → armour types in any combat game.
- Weekly races → async speed leaderboards in puzzle or runner games.

**Ontology encoding**
```json
{"loops": [
  {"id": "btd6_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "place_monkey_towers_along_track", "reward": "pops_and_cash", "next": "c2"},
    {"id": "c2", "action": "upgrade_paths_under_crosspath_rule", "reward": "counters_for_bloon_properties", "next": "c3"},
    {"id": "c3", "action": "survive_round_set", "reward": "monkey_money_xp_medal", "next": "c1"}]},
  {"id": "btd6_meta", "type": "meta", "period": "session", "steps": [
    {"id": "m1", "action": "spend_knowledge_and_unlock_upgrades", "reward": "stronger_options", "next": "m2"},
    {"id": "m2", "action": "attempt_harder_difficulty_or_mode", "reward": "new_medals", "next": "m1"}]},
  {"id": "btd6_live", "type": "liveops", "period": "weekly", "steps": [
    {"id": "l1", "action": "play_race_or_boss_event", "reward": "trophies_leaderboard_rank", "next": "l1"}]}],
 "economy": {"currencies": [
  {"id": "match_cash", "kind": "energy", "sources": ["pops", "income_towers"], "sinks": ["towers", "upgrades"], "cap": null},
  {"id": "monkey_money", "kind": "soft", "sources": ["map_completion", "events", "iap"], "sinks": ["heroes", "powers", "insta_monkeys"], "cap": null},
  {"id": "knowledge_points", "kind": "material", "sources": ["player_levels"], "sinks": ["perk_tree"], "cap": null},
  {"id": "trophies", "kind": "event", "sources": ["races", "bosses"], "sinks": ["cosmetic_store"], "cap": null}]}}
```

## 11. Kingdom Rush

**Snapshot**
- Developer: Ironhide Game Studio (Montevideo, Uruguay).
- Release: 2011, first as a Flash browser game, then on iOS and later Android and PC (verify exact platform dates). Sequels include Frontiers (2013), Origins (2014), Vengeance (2018) and Alliance (2024).
- Genre: tower defense with fixed build plots. Business model: premium, with optional IAP for heroes and consumables in later versions and sequels (verify per platform).
- Scale: a long-running premium TD series (figures omitted).

**Core loop**
1. Study the level's path and the fixed build plots along it.
2. Build one of four tower types on each plot: archers, barracks (soldiers), mages or artillery.
3. Upgrade towers through basic tiers, then choose one of two specialised final towers per type, each with purchasable skills.
4. Set barracks rally points so soldiers block enemies at chokepoints, and position the hero.
5. Use two cooldown spells (a meteor strike and summoned reinforcements). Call waves early for bonus gold.
6. Survive all waves without losing your lives to leaking enemies. Earn 1–3 stars, then return to step 1.

**Meta and progression**
- Stars are spent in an upgrade tree that improves each tower type and spell.
- Each level has extra challenge modes (Heroic and Iron) that restrict tools and award more stars.
- Heroes with level-ups became central from the second game onwards. An in-game encyclopedia catalogues enemies and towers.

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Gold (in-level) | energy | kills, early wave calls, starting gold | towers, upgrades, skills |
| Stars | material | level completion and challenge modes | upgrade tree |
| Gems (where present) | hard | IAP, levels | consumable items, heroes |
| Lives (in-level) | energy | level start | enemies that reach the exit |

**Monetization**
- The upfront price buys the campaign.
- Optional purchases of heroes and consumables in some versions and sequels. Paid heroes and towers in later sequels drew criticism (verify specifics).

**Live-ops**: minimal. Content arrives as level packs, expansions and sequels rather than as live events.

**Retention hooks**
- Three-star mastery, challenge modes, new heroes and the next level on the campaign map.

**Social layer**: none to speak of beyond achievements and leaderboards (verify per platform).

**UX and onboarding notables**
- Fixed plots remove placement fiddliness on touch screens and make each level an authored puzzle.
- Each new enemy and tower is introduced with an encyclopedia card.
- Calling the next wave early is a clear, optional risk-for-reward button.

**Art and audio identity**: chunky, humorous fantasy cartoon art with readable enemy silhouettes, comic voice lines on towers and units, and a lively orchestral-style score.

**Psychology principles used**
- Competence and mastery: three stars and challenge modes.
- Risk/reward: early wave calls.
- Curiosity: the encyclopedia and new enemies.
- Humour as reward.

**Innovations**
- Barracks soldiers that physically block enemies, which turns TD into a tactics game about where fights happen.
- Fixed plots plus branching final towers: a small, deep decision set per level.
- An active hero unit within TD, more central in later games.

**Weaknesses and criticism**
- Paid heroes and items in a premium product (strongest criticism around later sequels).
- Formula repetition across sequels. Limited replay once all stars are earned.

**Lessons for designers**
1. Fixed build plots make TD levels authored puzzles and suit touch controls.
2. Blocking units add a second dimension (where to fight) to the usual question of what to build.
3. "Call early for gold" is an elegant optional risk dial for advanced players.
4. Challenge modes multiply the content of each level.

**Analogy hooks**
- Fixed plots with branching final upgrades → base-building puzzles, merge-defense hybrids.
- Blocking soldiers with rally points → lane battlers, RTS-lite.
- The early-wave bonus → speed bonuses in puzzles, early-exit bonuses in roguelites.

**Ontology encoding**
```json
{"loops": [
  {"id": "kr_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "build_tower_on_fixed_plot", "reward": "defence", "next": "c2"},
    {"id": "c2", "action": "set_rally_points_and_cast_spells", "reward": "enemies_blocked_and_killed", "next": "c3"},
    {"id": "c3", "action": "call_next_wave_early", "reward": "bonus_gold", "next": "c4"},
    {"id": "c4", "action": "finish_level_without_leaks", "reward": "one_to_three_stars", "next": "c1"}]},
  {"id": "kr_meta", "type": "meta", "period": "session", "steps": [
    {"id": "m1", "action": "spend_stars_in_upgrade_tree", "reward": "stronger_towers_and_spells", "next": "m2"},
    {"id": "m2", "action": "attempt_heroic_and_iron_challenges", "reward": "extra_stars", "next": "m1"}]}],
 "economy": {"currencies": [
  {"id": "level_gold", "kind": "energy", "sources": ["kills", "early_wave_calls"], "sinks": ["towers", "upgrades"], "cap": null},
  {"id": "stars", "kind": "material", "sources": ["level_completion", "challenges"], "sinks": ["upgrade_tree"], "cap": null},
  {"id": "gems", "kind": "hard", "sources": ["iap", "levels"], "sinks": ["consumables", "heroes"], "cap": null},
  {"id": "lives", "kind": "energy", "sources": ["level_start"], "sinks": ["enemy_leaks"], "cap": null}]}}
```

## 12. Mobile Legends: Bang Bang

**Snapshot**
- Developer: Moonton (Shanghai). ByteDance acquired Moonton in 2021 (widely reported).
- Release: 2016.
- Genre: 5v5 MOBA. Business model: free-to-play with IAP (skins, heroes, passes).
- Scale: the dominant MOBA in much of Southeast Asia (notably Indonesia and the Philippines) by widely reported rankings. It was a medal event at the 2019 Southeast Asian Games (figures omitted).

**Core loop**
1. Queue (classic, ranked with picks and bans, or a single-lane brawl mode).
2. Pick a hero by role: tank, fighter, assassin, mage, marksman, support.
3. Play three lanes plus a jungle with a virtual joystick and skill buttons. Last-hit minions and jungle monsters for gold and experience.
4. Buy items (recommended builds can auto-purchase), level skills and fight over neutral objectives such as the Turtle and the Lord.
5. Destroy the enemy base. Matches are typically shorter than PC MOBAs (verify typical duration).
6. Gain rank stars and battle points, then return to step 1.

**Meta and progression**
- Hero collection bought with battle points (soft) or diamonds (premium).
- Emblems (talent sets) levelled over time. A rank ladder with seasons.
- Additional modes, including an autobattler mode (verify current modes).

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Battle points | soft | matches, quests | heroes, emblems |
| Diamonds | hard | IAP, events | skins, heroes, passes, draws |
| Tickets and fragments | material | events, quests, draws | heroes, skins, items |
| Rank stars | xp | wins | losses |

**Monetization**
- Skins at many price tiers, including high-tier skins obtained through random draw events (criticised for cost).
- A monthly membership pass with skins and rewards, hero purchases and event bundles.

**Live-ops**
- New heroes and skins on a regular cadence, ranked seasons, themed events and IP collaborations.
- A large esports ecosystem with regional leagues and world championships.

**Retention hooks**
- Rank seasons and rewards, daily quests, events and squad play with friends.

**Social layer**
- Friends, squads, mentoring and relationship systems, guild-like groups, spectating, and esports viewing.
- Locally themed heroes based on regional folklore and history (for example, Indonesian and Filipino figures) build national pride and identity.

**UX and onboarding notables**
- A smaller download and modest device requirements suited to emerging-market phones.
- Auto-targeting with priority options, recommended item builds and a simplified ruleset shorten the learning curve.
- AI takes over for disconnected players, softening the damage from unstable networks (verify current behaviour).

**Art and audio identity**: bright, saturated fantasy art with highly readable skills, a large and varied hero cast, and premium skins with distinctive effects and voices.

**Psychology principles used**
- Competence and mastery: hero skill and the rank ladder.
- Relatedness: playing with friends, national heroes and esports fandom.
- Status: skins and rank.
- Variable reward: draw events.

**Innovations**
- Fitted the MOBA to the market: short matches, low device and data requirements, simplified controls and local content. It became the leading MOBA in Southeast Asia even though other MOBAs were available there.

**Weaknesses and criticism**
- Similarity to League of Legends led to legal action by Riot and Tencent. A US case was dismissed on jurisdictional grounds and a Chinese court ruled against Moonton's founder in 2018 (reported; verify details).
- Toxicity, matchmaking and smurfing complaints common to the genre.
- Expensive random skin draws.

**Lessons for designers**
1. Design for the target region's devices, networks and match-length tolerance before polishing features.
2. Local heroes and themes are a strong lever for national markets.
3. Auto-buy and recommended builds remove the knowledge wall without removing depth.
4. Originality matters: close imitation brings legal and reputational risk (see `legal-ethics`).

**Analogy hooks**
- Region-first device targeting → any game aimed at emerging markets.
- Locally themed characters → sports games, collectors, puzzles with regional events.
- Recommended builds with auto-buy → RPG gear systems, deckbuilders (suggested decks).

**Ontology encoding**
```json
{"loops": [
  {"id": "mlbb_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "queue_and_pick_hero", "reward": "match_start", "next": "c2"},
    {"id": "c2", "action": "farm_lane_or_jungle", "reward": "gold_and_xp", "next": "c3"},
    {"id": "c3", "action": "buy_items_and_fight_objectives", "reward": "team_advantage", "next": "c4"},
    {"id": "c4", "action": "destroy_enemy_base", "reward": "rank_stars_battle_points", "next": "c1"}]},
  {"id": "mlbb_season", "type": "liveops", "period": "season", "steps": [
    {"id": "s1", "action": "climb_rank_ladder", "reward": "season_rewards", "next": "s2"},
    {"id": "s2", "action": "buy_or_draw_new_skins", "reward": "status_cosmetics", "next": "s1"}]}],
 "economy": {"currencies": [
  {"id": "battle_points", "kind": "soft", "sources": ["matches", "quests"], "sinks": ["heroes", "emblems"], "cap": null},
  {"id": "diamonds", "kind": "hard", "sources": ["iap", "events"], "sinks": ["skins", "heroes", "passes", "draws"], "cap": null},
  {"id": "fragments", "kind": "material", "sources": ["events", "draws"], "sinks": ["heroes", "skins"], "cap": null},
  {"id": "rank_stars", "kind": "xp", "sources": ["wins"], "sinks": ["losses"], "cap": null}]}}
```

## 13. Honor of Kings

**Snapshot**
- Developer: TiMi Studio Group (Tencent).
- Release: November 2015 in China. An internationally adapted version, Arena of Valor, launched in 2016–17. A dedicated global release of Honor of Kings rolled out from 2024 (verify markets).
- Genre: 5v5 MOBA. Business model: free-to-play with IAP (skins, heroes, passes).
- Scale: one of the highest-grossing mobile games in the world. It was listed among the top grossers of Q1 2026 by Sensor Tower data (section 18, [V1]).

**Core loop**
1. Log in with a social account and form a team with friends, or queue solo.
2. Pick a hero, many drawn from Chinese history and mythology.
3. Lane, farm, fight over objectives and teamfight in a match of about 15–20 minutes (verify typical duration).
4. Destroy the enemy crystal. Gain rank stars, rewards and relationship points with friends.
5. Return to step 1, often in the same friend group.

**Meta and progression**
- Rank tiers by season, hero mastery and proficiency titles (including regional leaderboards for hero proficiency; verify).
- Hero collection and a large skin catalogue. Battle passes and events.

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Gold (soft, name varies) | soft | matches, quests | heroes, inscriptions |
| Premium currency (vouchers or tokens; name varies by version) | premium | IAP | skins, heroes, pass, draws |
| Fragments and event tokens | material | events, draws | skins, heroes |
| Rank stars | xp | wins | losses |

**Monetization**
- Skins (the main revenue driver), including limited and high-tier skins through draw events.
- Battle passes, hero purchases and event bundles.

**Live-ops**
- Seasons, new heroes and skins, festival events tied to Chinese holidays and culture, and a large professional league with international events.

**Retention hooks**
- Playing with friends (the main hook), season ranks, events, and hero mastery leaderboards.

**Social layer**
- Login with and invites through the major Chinese social platforms (WeChat and QQ), so friends lists import automatically.
- Relationship systems between friends, teams and in-game social spaces. The game functions as a social habit among friends and colleagues.

**UX and onboarding notables**
- Short matches by MOBA standards, a simplified control scheme and readable skill effects.
- Minor protection systems: real-name registration, play-time limits for minors and identity checks such as facial recognition, introduced in stages from 2017 and tightened under Chinese regulations in 2021 that limited minors' online gaming to one hour on Fridays, weekends and holidays (widely reported; verify current rules).

**Art and audio identity**: polished art rooted in Chinese culture and mythology, premium skins designed as fashion statements, and culturally themed collaborations.

**Psychology principles used**
- Relatedness: the friend graph.
- Status and identity: skins and rank.
- Competence: mastery leaderboards.
- Social obligation: friends waiting in a lobby.

**Innovations**
- Turned a competitive MOBA into a mass social habit by wiring it into the dominant social graph, so the game spreads and retains through existing relationships.
- A large-scale, regulation-driven minor-protection stack (real-name, time limits, identity checks) designed into the live product.

**Weaknesses and criticism**
- State media criticised the game in 2017 over addiction concerns and its portrayal of historical figures (widely reported).
- Minors' spending and play time led to regulatory limits. The first international adaptation (Arena of Valor) did not reach comparable success outside Asia.
- Random skin draws and high spending ceilings for cosmetics.

**Lessons for designers**
1. Social-graph integration is the strongest retention multiplier: make inviting friends the default path.
2. Compliance can reshape design. Build age and time controls in from day one if you target regulated markets (see `legal-ethics`).
3. Cultural authenticity sells at home. Exporting it needs adaptation, not just translation.

**Analogy hooks**
- Social-graph login with friend-first matchmaking → any session-based multiplayer game.
- Mastery leaderboards per hero per region → per-character ladders in shooters or fighting games.
- Holiday-themed skin festivals → cosmetics calendars in any live game.

**Ontology encoding**
```json
{"loops": [
  {"id": "hok_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "invite_friends_form_team", "reward": "team_ready", "next": "c2"},
    {"id": "c2", "action": "pick_hero_lane_and_teamfight", "reward": "objectives_and_kills", "next": "c3"},
    {"id": "c3", "action": "destroy_enemy_crystal", "reward": "rank_stars_relationship_points", "next": "c1"}]},
  {"id": "hok_social", "type": "social", "period": "daily", "steps": [
    {"id": "s1", "action": "play_sessions_with_friend_group", "reward": "relationship_level", "next": "s2"},
    {"id": "s2", "action": "show_skins_and_mastery_titles", "reward": "status", "next": "s1"}]}],
 "economy": {"currencies": [
  {"id": "gold", "kind": "soft", "sources": ["matches", "quests"], "sinks": ["heroes", "inscriptions"], "cap": null},
  {"id": "premium_tokens", "kind": "premium", "sources": ["iap"], "sinks": ["skins", "heroes", "pass", "draws"], "cap": null},
  {"id": "fragments", "kind": "material", "sources": ["events", "draws"], "sinks": ["skins"], "cap": null},
  {"id": "rank_stars", "kind": "xp", "sources": ["wins"], "sinks": ["losses"], "cap": null}]}}
```

## 14. PUBG Mobile

**Snapshot**
- Developer: Lightspeed & Quantum Studio (Tencent), under licence from PUBG Corporation (Krafton).
- Release: 2018 globally. In China, the test version was replaced in 2019 by a separately branded game (Game for Peace). In India the game was banned in 2020, and Krafton launched a separate Indian version (Battlegrounds Mobile India, BGMI) in 2021, which was itself blocked in 2022 and restored in 2023 (all widely reported; verify details).
- Genre: battle royale shooter, plus quicker modes. Business model: free-to-play with IAP (season pass, cosmetics).
- Scale: one of the most-played mobile shooters globally (figures omitted). A lighter variant targets low-end devices (see section 18, [V3]).

**Core loop**
1. Queue solo or with a squad of up to four; matches hold up to 100 players.
2. Parachute from a plane onto a large map, choosing where to land (a risk choice).
3. Loot weapons, attachments, armour and healing items.
4. Move with the shrinking safe zone, fight other squads, knock and revive teammates, and grab airdrops.
5. Win by being the last squad standing (a classic BR match runs about half an hour on the largest maps; verify). Earn rank points, battle points and pass experience.
6. Return to step 1, or play a shorter mode such as 4v4 team deathmatch.

**Meta and progression**
- Ranked tiers by season, a season pass (Royale Pass) with free and paid tracks, achievements and a large cosmetic collection.
- Rotating themed modes and collaborations layered onto the BR maps (verify current modes).

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| UC (premium) | premium | IAP | pass, crates and draws, cosmetics |
| BP (battle points) | soft | matches, missions | classic crates, some items |
| Pass points | xp | missions, matches | pass tiers |
| Event tokens and fragments | event | events, draws | exchange shops |
| Rank points | xp | placements, kills | losses |

**Monetization**
- The season pass (Royale Pass), often credited with popularising season passes in mobile shooters.
- Cosmetic crates and draw events with disclosed odds, direct-purchase cosmetics and collaboration skins. No pay-to-win weapons in the core design (cosmetic monetization), though some cosmetic weapon skins add effects (verify).

**Live-ops**
- Regular content updates with themed modes, new maps and collaborations; monthly pass cycles and ranked seasons (verify cadence); a global esports circuit.

**Retention hooks**
- Pass progress and missions, ranked seasons, squad sessions with friends, and limited-time modes.

**Social layer**
- Squads with voice chat, friends, clans and crews, spectating and a large creator and esports scene.

**UX and onboarding notables**
- A deep device-scaling system: graphics presets and frame-rate options from low-end to high-end hardware, plus a separate light version for very low-end phones.
- Customisable HUD layouts, optional gyroscope aiming, auto-pickup and auto-open doors. Aim assist reduces the touch handicap.
- New players meet AI bots in early matches, easing the first wins (widely acknowledged; verify current disclosure).

**Art and audio identity**: grounded military realism, with audio as a gameplay channel (footsteps, gunshot direction). Cosmetics are often deliberately loud, in contrast to the realistic base art.

**Psychology principles used**
- Variable outcome and tension: each match is a new story with a single winner.
- Competence: kills and placements.
- Relatedness: squads with voice.
- Collection and status: cosmetics.
- Near-miss: placing second.

**Innovations**
- Proved that a console/PC-grade battle royale could run on phones at scale through device scaling, touch controls with assists and bots for onboarding.
- Helped make the season pass standard on mobile.

**Weaknesses and criticism**
- Cheating and the arms race of anti-cheat.
- National bans and regulatory action (India among others), and reported addiction concerns.
- Bots that blur perceived skill, random cosmetic draws, and long matches for a mobile session.

**Lessons for designers**
1. If you port a demanding genre to phones, build device scaling, assist systems and a light build into the plan, not as afterthoughts.
2. Bots for new players protect first-session competence. Decide your disclosure policy deliberately.
3. Offer a short mode (team deathmatch) for players who only have 5 minutes.
4. Cosmetic-only monetization protects competitive integrity, but needs a huge audience.

**Analogy hooks**
- A shrinking safe zone → any arena game that needs a forced conclusion (party games, io games).
- Landing-spot risk choice → roguelite map nodes, run starts.
- Knock-and-revive → co-op action, survival games.

**Ontology encoding**
```json
{"loops": [
  {"id": "pubgm_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "choose_landing_spot_and_drop", "reward": "start_position", "next": "c2"},
    {"id": "c2", "action": "loot_weapons_armour_meds", "reward": "loadout", "next": "c3"},
    {"id": "c3", "action": "rotate_with_safe_zone_and_fight", "reward": "eliminations_survival", "next": "c4"},
    {"id": "c4", "action": "finish_as_last_squad_or_die", "reward": "rank_points_bp_pass_xp", "next": "c1"}]},
  {"id": "pubgm_pass", "type": "monetization", "period": "season", "steps": [
    {"id": "p1", "action": "complete_missions", "reward": "pass_points", "next": "p2"},
    {"id": "p2", "action": "claim_pass_tiers_buy_premium_track", "reward": "cosmetics", "next": "p1"}]}],
 "economy": {"currencies": [
  {"id": "uc", "kind": "premium", "sources": ["iap"], "sinks": ["pass", "draws", "cosmetics"], "cap": null},
  {"id": "bp", "kind": "soft", "sources": ["matches", "missions"], "sinks": ["classic_crates"], "cap": null},
  {"id": "pass_points", "kind": "xp", "sources": ["missions", "matches"], "sinks": [], "cap": null},
  {"id": "rank_points", "kind": "xp", "sources": ["placement", "kills"], "sinks": ["losses"], "cap": null}]}}
```

## 15. Free Fire

**Snapshot**
- Developer: 111dots Studio. Publisher: Garena (Sea Ltd, Singapore).
- Release: 2017. A higher-fidelity edition, Free Fire MAX, followed in 2021. Free Fire was among apps blocked in India in 2022 (widely reported; verify current status).
- Genre: battle royale with short matches, plus round-based team modes. Business model: free-to-play with IAP.
- Scale: one of the most downloaded mobile games globally in several years, with particular strength in Brazil, Southeast Asia, India (before the block) and Latin America (widely reported; figures omitted).

**Core loop**
1. Queue for a battle royale of up to 50 players (solo, duo or squad) or a 4v4 round-based mode.
2. Choose a character (with an ability) and a pet, then drop onto a compact map.
3. Loot quickly, fight, and use deployable cover walls (the "Gloo Wall") to build instant protection.
4. Survive the shrinking zone. Matches run about 10 minutes (verify typical duration).
5. Earn rank points, gold and pass progress, then return to step 1.

**Meta and progression**
- Characters with active and passive skills, levelled and combined; pets with skills. Ranked seasons, pass tiers and a very large cosmetic catalogue.

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Diamonds | premium | IAP (including local top-up channels) | pass, draws, characters, cosmetics |
| Gold | soft | matches, missions | characters, some items |
| Event tokens | event | events | exchange shops |
| Rank points | xp | placements, kills | losses |

**Monetization**
- A monthly elite-style pass, random draw systems for cosmetics with disclosed odds, character and bundle sales, and celebrity characters.
- Payment reach: top-up through local vouchers, carriers and web shops makes spending possible for players without credit cards (verify current channels per market).

**Live-ops**
- A dense calendar of events, new characters, collaborations (including celebrity characters based on public figures such as a Brazilian DJ and a famous footballer), ranked seasons and large esports events.

**Retention hooks**
- Ranked seasons, daily missions, events with exchange shops, and squads with friends.

**Social layer**
- Squads, guilds, friends and voice chat, plus creator content and esports with large regional audiences.

**UX and onboarding notables**
- Built for low-end Android phones with modest RAM and storage, and fast load times. The small map and 50-player cap keep performance stable.
- Matches short enough for mobile sessions. Auto-aim assists and simple controls.

**Art and audio identity**: stylised, bright and less realistic than PUBG Mobile, with flamboyant cosmetics, emotes and characters with strong personalities. Cheaper rendering suits weaker hardware.

**Psychology principles used**
- Competence in short cycles: 10-minute matches.
- Identity and status: cosmetics and celebrity characters.
- Variable reward: draws.
- Relatedness: squads.

**Innovations**
- Designed the battle royale for the actual device market of emerging economies rather than downscaling a console game.
- The Gloo Wall: instant deployable cover as a skill-expression tool on touch (a simpler alternative to full building).
- Payment and distribution channels adapted to markets with low card penetration.

**Weaknesses and criticism**
- Character abilities and pets create a pay-to-win perception.
- Cheating, spending by minors through vouchers, and the 2022 block in a top market.
- Heavy reliance on random cosmetic draws.

**Lessons for designers**
1. Start from the target device floor and session length, then size the design (player count, map, match time) to fit.
2. Give touch players a simple, powerful defensive verb (instant cover) instead of complex building.
3. Plan payments around how your audience actually pays.

**Analogy hooks**
- Instant cover walls → arena shooters, survival games, MOBAs (terrain creation).
- Fewer players on a smaller map → any multiplayer design for low-end hardware.
- Celebrity characters with abilities → sports and music collaborations in casual games.

**Ontology encoding**
```json
{"loops": [
  {"id": "ff_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "pick_character_and_pet", "reward": "ability_loadout", "next": "c2"},
    {"id": "c2", "action": "drop_loot_fast", "reward": "weapons_items", "next": "c3"},
    {"id": "c3", "action": "fight_and_deploy_cover_walls", "reward": "eliminations_survival", "next": "c4"},
    {"id": "c4", "action": "survive_ten_minute_zone", "reward": "rank_points_gold_pass_xp", "next": "c1"}]}],
 "economy": {"currencies": [
  {"id": "diamonds", "kind": "premium", "sources": ["iap", "top_up_vouchers"], "sinks": ["pass", "draws", "characters", "cosmetics"], "cap": null},
  {"id": "gold", "kind": "soft", "sources": ["matches", "missions"], "sinks": ["characters", "items"], "cap": null},
  {"id": "event_tokens", "kind": "event", "sources": ["events"], "sinks": ["exchange_shop"], "cap": null},
  {"id": "rank_points", "kind": "xp", "sources": ["placement", "kills"], "sinks": ["losses"], "cap": null}]}}
```

## 16. Call of Duty: Mobile

**Snapshot**
- Developer: TiMi Studio Group (Tencent), with publisher Activision.
- Release: October 2019.
- Genre: first-person shooter with several modes: 5v5 multiplayer, a battle royale and rotating special modes. Business model: free-to-play with IAP (battle pass, cosmetics, draws).
- Scale: a widely reported record-breaking launch (figures omitted).

**Core loop**
1. Build a loadout: primary and secondary weapons, attachments (the "Gunsmith"), perks, scorestreaks and an operator skill.
2. Play a 5v5 match on maps drawn from the franchise's history (for example Nuketown), lasting a few minutes.
3. Earn scorestreaks and operator skill charges through kills and objectives.
4. Win or lose. Gain player experience, weapon experience (unlocking attachments) and pass progress.
5. Return to step 1, or switch to battle royale or a seasonal mode.

**Meta and progression**
- Player level, per-weapon levels unlocking attachments, ranked seasons, and a battle pass each season.
- A large collection of weapon blueprints and operators. Top-tier cosmetic weapons come from draw events.

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| COD Points (CP) | hard | IAP, small pass amounts | battle pass, draws, bundles |
| Credits | soft | matches, pass, events | credit store items, crates |
| Battle pass XP | xp | matches, missions | pass tiers |
| Weapon XP | xp | matches with the weapon | attachment unlocks |

**Monetization**
- A seasonal battle pass with free and premium tracks.
- Draw events ("lucky draws") for premium weapon blueprints and operators, including high-tier weapons whose total draw cost is widely criticised. Direct bundles and collaborations.

**Live-ops**
- Seasons with new maps, modes, weapons and passes; ranked seasons; themed events; and a world championship (verify cadence).

**Retention hooks**
- Weapon levels, pass tiers, ranked seasons, daily and seasonal missions, and new maps or modes each season.

**Social layer**
- Friends, clans, voice chat, private matches and esports.

**UX and onboarding notables**
- A "simple mode" fires automatically when the crosshair rests on an enemy, while an advanced mode uses a fire button and custom layouts. This lets touch players choose their control complexity.
- Aim assist, gyroscope options, controller support and a fully customisable HUD.
- Short multiplayer matches and familiar maps give franchise fans instant recognition.

**Art and audio identity**: franchise-faithful military visuals and audio, with recognisable maps, weapons and operators, scaled for mobile hardware.

**Psychology principles used**
- Competence: kill feedback and scorestreak escalation.
- Familiarity: franchise nostalgia.
- Collection and status: blueprints and operators.
- Variable reward: draws.

**Innovations**
- Translated a console FPS franchise to touch with optional auto-fire, without splitting the audience by control style.
- Packaged several modes (MP, BR, seasonal) in one mobile app, each fitting a different session length.

**Weaknesses and criticism**
- Expensive draw events for top cosmetic weapons.
- Cheating, balance complaints and a large install size.
- Mode dilution: rotating modes can split queues.

**Lessons for designers**
1. Offer an auto-fire or assisted control mode so the touch handicap does not decide matches.
2. When translating an IP, carry over the signature maps and systems, and let mobile set the session length.
3. Price draw events transparently. Total cost to complete a set should be visible and reasonable.

**Analogy hooks**
- Auto-fire on crosshair → any mobile shooter or aiming game.
- Per-weapon XP unlocking attachments → per-item mastery in RPGs and roguelites.
- Scorestreaks → escalating rewards for combos in arcade and puzzle games.

**Ontology encoding**
```json
{"loops": [
  {"id": "codm_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "build_loadout_in_gunsmith", "reward": "plan", "next": "c2"},
    {"id": "c2", "action": "play_5v5_match_on_classic_map", "reward": "kills_scorestreaks", "next": "c3"},
    {"id": "c3", "action": "finish_match", "reward": "player_xp_weapon_xp_pass_xp", "next": "c4"},
    {"id": "c4", "action": "unlock_attachments", "reward": "stronger_loadout_options", "next": "c1"}]},
  {"id": "codm_season", "type": "liveops", "period": "season", "steps": [
    {"id": "s1", "action": "play_new_maps_and_modes", "reward": "pass_progress", "next": "s2"},
    {"id": "s2", "action": "claim_pass_or_draw_cosmetics", "reward": "blueprints_operators", "next": "s1"}]}],
 "economy": {"currencies": [
  {"id": "cod_points", "kind": "hard", "sources": ["iap", "pass"], "sinks": ["pass", "draws", "bundles"], "cap": null},
  {"id": "credits", "kind": "soft", "sources": ["matches", "pass", "events"], "sinks": ["credit_store", "crates"], "cap": null},
  {"id": "pass_xp", "kind": "xp", "sources": ["matches", "missions"], "sinks": [], "cap": null},
  {"id": "weapon_xp", "kind": "xp", "sources": ["matches"], "sinks": [], "cap": null}]}}
```

## 17. Cross-case synthesis for midcore and strategy

### 17.1 The six families compared

| Family | Cases | Session shape | Main retention engine | Monetization depth | Fairness model | Content cost | Key risk |
|---|---|---|---|---|---|---|---|
| Async base-builder | 1, 8 | 5–15 min, several check-ins a day | Timers, raids, clans | Medium–high (skips, builders, pass) | Convenience; matchmaking by trophies | Medium (levels of everything) | Late-game timer walls |
| Short real-time PvP | 2, 3 | 2–3 min matches in 10–20 min sessions | Ladder, collection, clubs | Medium–high (levels, pass, cosmetics) | Power-light; normalised ranked modes | Medium (cards or heroes, balance) | Pay-to-win perception |
| 4X / SLG | 4, 5, 6, 7 | Many short check-ins plus scheduled war hours | Alliances, seasons, power ranking | Very high (packs, VIP, events) | Power sold openly; segmented by server age | High (heroes, events, seasons) | Whale dependence, time demands |
| Tower defense | 9, 10, 11 | 5–20 min levels | Content ladder, mastery, medals | Low–medium (premium, IAP, power-ups) | Mostly PvE, so power sales hurt less | High per level (authored) | Content runs out |
| MOBA | 12, 13 | 10–20 min matches | Friends, rank, mastery | High via cosmetics at huge scale | Cosmetic; heroes buyable with soft currency | High (heroes, skins, balance, esports) | Toxicity, onboarding cliff |
| Shooter / BR | 14, 15, 16 | 5–30 min matches by mode | Squads, rank, pass | High via cosmetics and pass at scale | Cosmetic (with debated exceptions) | High (maps, modes, anti-cheat) | Cheating, device floor |

### 17.2 The fairness spectrum: what you sell decides where players can compete

| What is sold | Cases | Works when | Required protection |
|---|---|---|---|
| Cosmetics and pass only | MLBB, HoK, PUBG Mobile, Free Fire, CoD Mobile | Very large audience; symmetric ranked PvP | Odds disclosure on draws; total-cost transparency |
| Time (skips, queues) | Clash of Clans, Boom Beach | Async PvP where wins are not head-to-head reflex tests | Shields, loot penalties against weaker targets, trophy matchmaking |
| Power in PvP | Clash Royale (levels), 4X games | Players accept the "investment" fantasy; spend is public status | Level-normalised modes, server-age content, matched seasons, offline protection |
| Premium plus optional IAP | Bloons TD 6, Kingdom Rush | The core content is complete for the price | Never gate the campaign behind IAP |
| F2P conversion of a premium IP | Plants vs. Zombies 2 | Brand pull outweighs the goodwill cost | Keep the core beatable for free; sell breadth |

**Rule:** the more symmetric and real-time your PvP, the closer you must stay to cosmetics. Asynchronous, asymmetric or PvE-first designs can sell power, but only with the protections in the right column.

### 17.3 Worked example: builder queues and skip pricing

Assume a Town Hall level (or HQ level) contains upgrades that total `T` builder-hours.

```
days_to_finish = T / (builders × 24 × uptime)
value_of_extra_builder_days = T/(24·u)·(1/b − 1/(b+1))
```

- With `T = 600` builder-hours and 100% uptime: 4 builders take 6.25 days, 5 builders take 5.0 days. The fifth builder saves 1.25 days at this level and more at every later level. This is why extra builders are among the most valuable purchases in the genre.
- Uptime is the hidden variable. A player who checks in twice a day leaves builders idle for hours, so effective uptime may be 60–70% (illustrative). Notifications and longer timers raise uptime. This is an argument for timer lengths that match check-in rhythms, rather than for squeezing more time into them.
- Skip pricing: interpolate between breakpoints so short skips are cheap and the price per hour falls with length.

```python
# piecewise-linear skip price (illustrative breakpoints, after the Clash of Clans wiki values)
BREAKS = [(60, 1), (3600, 20), (86400, 260), (604800, 1000)]   # (seconds, gems)
def skip_cost(sec):
    if sec <= 0: return 0
    prev_s, prev_g = 0, 0
    for s, g in BREAKS:
        if sec <= s:
            return max(1, round(prev_g + (g - prev_g) * (sec - prev_s) / (s - prev_s)))
        prev_s, prev_g = s, g
    return round(BREAKS[-1][1] * sec / BREAKS[-1][0])
```

Model the queue economy before tuning it: write builder time as a `gate` node and skips as an `on_purchase` converter in `economy-model.schema.json`, then run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/economy_sim.py --model .gamestudio/economy/model.json --runs 200 --seed 1 --json`. Check `targets.days_to_complete_content` for a non-payer archetype.

### 17.4 The 4X server lifecycle (a pattern inferred from cases 4–7)

| Phase (illustrative timing) | What happens | Design levers seen in the cases |
|---|---|---|
| Land rush (days 0–7) | Many new players, fast progress, alliances form | New-server events, rapid early timers, guided quests |
| Consolidation (weeks 2–4) | Top alliances absorb smaller ones; first big wars | Alliance help and rallies, scheduled alliance events, protection for small players |
| First seasonal war | Matched servers fight (KvK, SvS) | Matchmaking by server power; season rewards; transfer windows |
| Mature server | Power gaps widen; activity falls | Hero and content generations paced by server age; catch-up mechanics |
| Merge or migrate | Low-population servers are combined or players transfer | Server merges, migration items, fresh-server invitations |

**Implications.** Content in a 4X is released per server, not per calendar. A new player in an old server is a different product, so design a catch-up path or route new players to new servers.

### 17.5 Real-time PvP session and audience numbers

| Game | Format | Typical match | Players per match | Note |
|---|---|---|---|---|
| Clash Royale | 1v1 | about 3 min plus overtime | 2 | Portrait, one hand |
| Brawl Stars | 3v3, BR | about 2–3 min | 6–10 | Landscape twin-stick |
| Mobile Legends, Honor of Kings | 5v5 | about 10–20 min (verify) | 10 | Friend parties drive retention |
| Call of Duty: Mobile | 5v5, BR | a few minutes (MP) | 10 (MP), up to 100 (BR) | Several session shapes in one app |
| Free Fire | BR | about 10 min | up to 50 | Low-end Android first |
| PUBG Mobile | BR | up to about 30 min on large maps | up to 100 | Shorter modes added |

All durations are approximate and vary by mode and patch. Every case that ships a long format also offers a short one (team deathmatch, brawl modes). Fill lobbies with bots only under an explicit disclosure policy (`legal-ethics`).

### 17.6 Top-of-funnel strategies for deep games

| Strategy | Case | How it works | Watch out for |
|---|---|---|---|
| Casual mini-game opening | Last War | Hybrid-casual levels in ads and in the first minutes, then a 4X | Ad honesty; explain the transition |
| Theme-as-tutorial | Whiteout Survival | Survival needs teach production chains | Keep the theme alive later |
| Solo PvE on-ramp | Lords Mobile, Boom Beach | Campaign or AI bases before PvP | PvE must lead into the real game |
| IP recognition | Call of Duty: Mobile, Plants vs. Zombies 2 | Maps, characters and modes fans know | IP fans judge faithfulness and fairness |
| Regional fit | Mobile Legends, Free Fire | Device floor, match length, local heroes, local payments | Imitation risk; regulatory exposure |
| Social graph | Honor of Kings | Friends imported at login | Requires platform access; minors' rules |

### 17.7 Decision procedure: choosing a midcore model

1. **Pick the conflict type.** Async (base raids), real-time symmetric (duels, MOBA, shooters), territorial (4X) or PvE (TD). Write it in `contract.meta.subgenre` and `contract.technical.multiplayer` (`async` or `realtime`).
2. **Choose the fairness model** from 17.2 and record it in `contract.monetization.ethics`. If PvP is real-time and symmetric, power sales are out.
3. **Set the session shape** from 17.5. Mobile midcore wants a 3-minute unit or shorter (`contract.meta.session_length_target_sec`), even if a longer mode exists.
4. **Design the group unit first** (clan, alliance, squad, task force) with at least one verb that transfers value (donations, help, rallies, gifts). Encode it as a `social` loop.
5. **Pick a top-of-funnel strategy** from 17.6 and test it with creatives before full production (`marketing-ua`).
6. **Plan the months clock.** Seasons, server age or content updates. 4X games need per-server pacing (17.4).
7. **Write kill criteria** before soft launch, for example D1, D7 and payer conversion below target after two iterations (`contract.kill_criteria`).

### 17.8 Tower-defense sub-models

| Sub-model | Case | Placement | Depth source | Mobile fit |
|---|---|---|---|---|
| Lane grid | Plants vs. Zombies 2 | 5 rows, any free tile | Unit roles per lane, world rules | Excellent: one decision space per lane |
| Free placement along a path | Bloons TD 6 | Anywhere off the track | Upgrade crosspaths, enemy properties | Good; needs zoom on small phones |
| Fixed plots with blockers | Kingdom Rush | Predefined plots | Branching final towers, rally points | Excellent: no fiddly placement |
| Operator TD with gacha | Arknights (see `references/rpg-gacha-cards.md`) | Grid tiles, melee vs ranged | Character collection, deployment cost | Good; landscape |

### 17.9 Where to go deeper

- Genre norms: `skills/genre-playbooks/references/strategy.md` and `skills/genre-playbooks/references/competitive-pvp.md` (`genre-playbooks`).
- Matchmaking, servers, anti-cheat and bots: `multiplayer-backend`. Timer, queue and sink tuning: `economy-design` and `progression-difficulty`.
- Passes, offers and fairness: `monetization`. Seasons and event calendars: `liveops`. Loot boxes, minors and imitation risk: `legal-ethics`.
- Turning a rule from these cases into your genre: `analogy-engine` and procedure B in `SKILL.md`.

## 18. Volatile facts (as of Oct 2026 — verify before relying)

- [V1] Last War: Survival, Honor of Kings and Whiteout Survival led worldwide mobile game grossing in Q1 2026 (Sensor Tower data). Source: [Mobilegamer.biz data digest](https://mobilegamer.biz/data-digest-sensor-towers-h1-analysis-hay-days-comeback-julys-top-games-big-krafton-numbers-and-more/).
- [V2] Strategy (4X) was described as 2025's hot genre, with winners combining accessible hooks, heavy social loops and deep monetization. This is a secondary summary of Sensor Tower's State of Mobile 2026. Source: [LinkedIn summary](https://fi.linkedin.com/in/teemu-tuulari-aa094028).
- [V3] Krafton's BGMI Lite opened pre-registration on Aug 25, 2026, with a stated minimum of 1.5 GB RAM and an Adreno 306-class GPU (single pre-release source). Source: [TalkEsport](https://www.talkesport.com/mobile-gaming/bgmi-lite-minimum-requirements-revealed-check-ram-gpu-and-other-details/).
- [V4] Mid-core took about 4% of mobile game ad revenue from February to April 2026, versus about 40% each for casual and hyper-casual. Midcore remains IAP-led. Source: [GameDev Reports summary of Sensor Tower](https://gamedevreports.substack.com/p/sensor-tower-mobile-game-ad-monetization).
- [V5] Mid-core D30 retention is cited at about 10–12% in secondary sources, partly traced to 2022 data. Treat it as order-of-magnitude only. Sources: [Segwise](https://segwise.ai/blog/mobile-gaming-app-user-retention-strategies), [AppAgent](https://appagent.com/blog/mobile-game-retention-benchmarks/).
- [V6] Mobile game IAP revenue grew about 1% to about $82B in 2025, with growth attributed to retaining and monetizing existing players through live-ops, events and IP collaborations. Source: [Sensor Tower press release](https://sensortower.com/press/press-release-sensor-tower-state-of-gaming-gaming-drove-52-billion-downloads-82b-iap-revenue-on-mobile-and-12b-premium-revenue-on-steam).
- [V7] Loot-box rules that apply to the random rewards in several cases: Belgium banned paid loot boxes under gambling law in 2018; Australia rates games with paid chance-based items at least M (classified after Sep 22, 2024); Brazil's ECA Digital bans loot-box sales to under-18s from March 2026; Apple and Google require odds disclosure before purchase. Sources: [Programming Insider](https://programminginsider.com/loot-boxes-regulation-and-where-the-line-sits-in-2026/), [PCWorld](https://www.pcworld.com/article/2464538/all-games-with-loot-boxes-will-be-rated-m-or-higher-in-australia.html), [Sheep Esports](https://www.sheepesports.com/articles/brazil-court-orders-riot-games-to-pay-eur2-5m-over-league-of-legends-loot-boxes/en), [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/).
- [V8] Tencent's Chinese battle royale Peacekeeper Elite (Game for Peace) reportedly offers an AI teammate feature covering about 110M players, with 17.7M DAU cited (aggregator source, grade C). Source: [NexWorld panorama](https://nexworld.wiki/en/ai-games/ai-games-panorama-2026/).
- [V9] Checked on 2026-10-20: Supercell's 2016 ownership structure and its list of cancelled or closed games ([Wikipedia: Supercell](https://en.wikipedia.org/wiki/Supercell_%28company%29)); Last War: Survival Game's publisher entity (App Store seller FUNFLY PTE. LTD.: [App Store listing](https://apps.apple.com/us/app/-/id6448786147)); Whiteout Survival's developer (Century Games PTE. LTD. on Google Play).
- Other historical facts in this file (release years, ownership changes, national bans, regulatory limits on minors) come from widely circulated press coverage and were not re-checked. Verify against primary sources before quoting them externally.
