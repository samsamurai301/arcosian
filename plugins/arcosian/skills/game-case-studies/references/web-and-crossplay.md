# Web-first and cross-platform case studies

Eight deconstructions of games that started in a browser, or that crossed platforms in a way worth copying or avoiding: two .io arena games (Agar.io, Slither.io), a browser shooter (Krunker), two idle and text games that later reached Steam, phones and consoles (Cookie Clicker, A Dark Room), a one-person designer's essay in game form (Universal Paperclips), a geography game that became a paid service (GeoGuessr) and a party game that went free-to-play with crossplay (Fall Guys). Read them for three questions: **how to launch on the web** with no install and no budget, **when to add native platforms** and what each one changes, and **how to decide on crossplay and cross-progression**. Each case uses the 16-lens format from `SKILL.md`, compressed, with a **Platform path** subsection in place of the PC notes used in `pc-console.md`. Games already covered elsewhere (Wordle in `premium-indie.md` §13, Vampire Survivors in `hyper-hybrid-casual.md` §12, Among Us and Roblox in `casual-social-sim.md` §8–9, Genshin Impact's PC and mobile progression in `rpg-gacha-cards.md` §1) are used in the synthesis by reference, not repeated. Source keys [V1]–[V8] are in section 12. Where only a press estimate or a marketing claim exists, it is labelled.

**Contents.** Sections 1–8 are case studies (index below). Section 9 is a cross-case synthesis with decision tables and checklists. Sections 10–11 are short procedures. Section 12 lists volatile facts with sources.

| # | Game | Genre | Year | Model | Key lesson |
|---|---|---|---|---|---|
| 1 | Agar.io | io arena | 2015 | free, ads, skins | One rule (eat smaller, avoid larger) and instant join; a publisher turned a browser hit into a mobile number one |
| 2 | Slither.io | io arena | 2016 | free, ads, remove-ads purchase | Streamers spread a clone faster than the original; sell no power |
| 3 | Krunker | browser shooter | 2018 | free, skins and trade, UGC maps | No-install shooter with a creator economy; sold to a web platform |
| 4 | Cookie Clicker | idle | 2013 | free web; Steam $4.99 (2021); consoles 2025 | A one-evening game found an audience; the paid versions added saves, music and reach |
| 5 | A Dark Room | text adventure | 2013 | free web; paid mobile port | Reveal the game slowly; open source let a porter reach iOS |
| 6 | Universal Paperclips | idle, essay | 2017 | free web; paid mobile | A thought experiment as a loop; a short game with an ending |
| 7 | GeoGuessr | geography | 2013 | freemium, subscription | A tiny weekend project, a platform dependency, and a rocky Steam launch |
| 8 | Fall Guys | party royale | 2020 | premium, then free-to-play | Crossplay and free-to-play bring a 20 million rush; live content must keep up |

---

## 1. Agar.io

**Snapshot**
- Creator: Matheus Valadares (Brazil), then 19, using JavaScript and C++. Browser release 28 April 2015; Android 7 July and iOS 8 July 2015 through Miniclip, who began working with him at the end of April [V1].
- Scale: about 5 million daily players when Miniclip got involved; more than 10 million mobile downloads in the first week and 113 million by December 2016; the iOS version reached number one in the US, the UK and 32 other countries; Google's most-searched game of 2015 [V1]. Revenue is not sourced.
- Genre: io arena. Model: free; in-game ads covered server costs; skins [V1].

**Core loop**
1. Join a public server instantly with a nickname; no account.
2. Move a cell with the pointer; eat food dots and smaller cells to grow.
3. Larger cells move slower and slowly lose mass; avoid bigger cells.
4. Split (up to 16 pieces) to catch prey or flee; eject mass to feed allies or bait viruses.
5. Die, respawn small, rejoin in seconds.

**Meta and progression**: none in the first version beyond leaderboards; later skins and levels (verify). The match is the whole game.
**Economy**: none; mass inside a run is the resource.
**Monetization**: ads and cosmetic skins; no gameplay sales. **Live-ops**: modes (Experimental, Battle Royale, party) added over time [V1]. **Retention hooks**: climb the leaderboard; instant restart. **Social layer**: public servers, party codes; YouTube videos reached 2 billion views by March 2016 [V1].

**UX and onboarding notables**: zero-step onboarding: the rule is visible from the screen (big eats small). Control is mouse plus two keys.
**Art and audio identity**: flat coloured circles; minimal sound. The style is cheap to render in a browser and easy to clone.
**Psychology principles used**: risk-reward scaling (bigger is slower and a target); loss aversion at death; immediate restart.
**Innovations**: massively multiplayer agario-style arenas in a browser; a skill ceiling from splitting; the ".io" genre label (reported) [V1].
**Weaknesses and criticism**: bots filled lobbies and teamed to farm (a known ".io" controversy); skin moderation problems; a thin late game [V1].

**Lessons for designers**
1. A rule that a viewer understands from one screenshot spreads on video.
2. Instant join with no account removes the largest web funnel drop.
3. A publisher can move a web hit to mobile in weeks if the code is small.
4. Bots need a policy (label them, or cap them) so that lobbies do not feel fake.

**Analogy hooks**: growth-vs-speed trade-off → Hole.io (`hyper-hybrid-casual.md` §4). Split and recombine → any risk-reward duplication mechanic. Account-free join → web party games.

**Platform path**: browser first (April 2015), mobile within ten weeks through a publisher, never on Steam (approved on Greenlight but not released) [V1]. Input moves from mouse to a touch joystick and a split button.

**Ontology encoding**
```json
{"loops": [
  {"id": "ag_core", "type": "core", "period": "seconds", "steps": [
    {"id": "c1", "action": "move_and_eat", "reward": "mass", "next": "c2"},
    {"id": "c2", "action": "split_or_flee", "reward": "kill_or_escape", "next": "c3"},
    {"id": "c3", "action": "die_and_rejoin", "reward": "instant_retry", "next": "c1"}]}],
 "progression": {"tracks": [{"id": "leaderboard", "gated_by": "mass"}]}}
```

## 2. Slither.io

**Snapshot**
- Creator: Steven Howse (later via Lowtech Studios for mobile). Browser and iOS on 25 March 2016, Android on 27 March 2016 [V2].
- Scale: by September 2017, over 68 million mobile downloads and over 67 million browser plays; it was Google's most-searched video game in the US in 2016; the browser site ranked among Alexa's top 1,000 in July 2016 [V2]. The Agar.io article reports over 60 million daily players by June 2016 (a single-source claim; label as an estimate) [V1].
- Genre: io arena (snake). Model: ads after death, and a one-off US$3.99 purchase to remove them; no virtual currency or power sold [V2].

**Core loop**
1. Steer a snake to eat glowing orbs; length equals score.
2. Boost (spend length) to cut off others.
3. Make another snake hit your body: it dies and drops orbs.
4. Die; see an ad; rejoin.
5. Climb the leaderboard.

**Meta and progression**: cosmetic skins (66 default skins as of January 2026) [V2].
**Economy**: none; length is the in-run resource.
**Monetization**: ads and remove-ads; the article notes that most versions no longer show ads as of 2026 (verify) [V2]. **Live-ops**: skins and an AI mode on mobile [V2]. **Retention hooks**: the leaderboard; skins. **Social layer**: streamers' videos (PewDiePie among them) [V2].

**UX and onboarding notables**: the game opens with one text field and a play button; one-hand control; the death-and-drop reward makes kills legible.
**Art and audio identity**: glowing neon snakes on a dark grid; the look reads in a thumbnail.
**Psychology principles used**: spectacle (a big snake is visible to all); revenge and risk; near-miss tension.
**Innovations**: the drop-on-death reward in an .io game; the boost-as-risk mechanic.
**Weaknesses and criticism**: low replay value and ads were reviewers' main complaints; cheating and a trademark dispute with a clone (Snake.io) [V2].

**Lessons for designers**
1. A better-looking sibling of a viral rule can overtake it if streamers play it.
2. Selling no power and removing ads for a small fee is a clean web-to-mobile model.
3. Ad-after-death is a natural break; keep it short.
4. The loot-on-kill mechanic gives a winner a visible reward.

**Analogy hooks**: boost-as-risk → stamina in a racing or running game. Drop-on-death → any PvP where a kill creates a collectible. Remove-ads purchase → hybrid-casual models (`hyper-hybrid-casual.md` §15).

**Platform path**: browser and iOS on the same day, Android two days later, then an arcade cabinet years later [V2]. Both web and mobile ran on the same servers.

**Ontology encoding**
```json
{"loops": [
  {"id": "sl_core", "type": "core", "period": "seconds", "steps": [
    {"id": "c1", "action": "steer_and_eat_orbs", "reward": "length", "next": "c2"},
    {"id": "c2", "action": "boost_to_cut_off_rivals", "reward": "kill_drops", "next": "c3"},
    {"id": "c3", "action": "die_watch_ad_rejoin", "reward": "retry", "next": "c1"}]}],
 "economy": {"currencies": []}}
```

## 3. Krunker

**Snapshot**
- Creator: Sidney de Vries (Switzerland), who started it in 2018. FRVR (Lisbon; over 100 employees) announced the acquisition on 12 May 2022; terms were not disclosed and the Krunker team became an independent first-party studio [V3].
- Scale (company statement): over 200 million unique players, thousands of skins and items, more than 50,000 custom maps and games, and 12 rotation maps at the time [V3]. Team size for Krunker: not sourced.
- Genre: browser first-person shooter. Model: free-to-play with skins, trading and a creator economy [V3].

**Core loop**
1. Open a link; the game runs in the browser, with no install.
2. Pick a class and a weapon; join a short match in a map of the rotation.
3. Fast movement (sliding, jumping) and aiming decide fights.
4. Earn XP and items; unlock skins; trade them.
5. Switch to community maps or modes.

**Meta and progression**: levels, weapon skins and a market. The press release says the economy of skins is "thriving" (company claim) [V3].
**Economy**: items tradable between players; skins are cosmetic. Exact currency names are not in the source: verify.
**Monetization**: free-to-play; cosmetics. **Live-ops**: map rotations and community contests (verify). **Retention hooks**: movement mastery, skins, community maps and modes. **Social layer**: full modding support and mapping tools; 50,000 plus custom maps and games [V3].

**UX and onboarding notables**: no install and no account to start; match start in seconds; a small download keeps load time low.
**Art and audio identity**: a blocky, low-poly look that is cheap to render in a browser and easy to read in motion.
**Psychology principles used**: mastery through movement; collection through skins; autonomy through custom maps.
**Innovations**: a console-style shooter at browser speed; first-class mapping tools bundled with the game.
**Weaknesses and criticism**: cheating in a client-heavy web game (a general web risk; verify for Krunker); the community reaction after the sale (a petition exists; unreliable) [V3].

**Lessons for designers**
1. A browser shooter needs a tiny asset budget and a tight netcode budget; art style is a performance decision.
2. UGC maps turn a mechanic into a content platform, with no studio cost.
3. A skin market gives a free game a monetization path without selling power.
4. A web platform can be the natural acquirer: the buyer wanted instant-play reach.

**Analogy hooks**: UGC maps → Fortnite Creative and Roblox (`pc-console.md` §13; `casual-social-sim.md` §9). Low-poly browser art → any WebGL title. Skin trade → collectible economies.

**Platform path**: browser as the home; the acquirer's stated plan was to use its platform for reach and sandbox features [V3]. Whether a native client exists is not confirmed here.

**Ontology encoding**
```json
{"loops": [
  {"id": "kr_core", "type": "core", "period": "seconds", "steps": [
    {"id": "c1", "action": "move_aim_shoot", "reward": "kills", "next": "c2"},
    {"id": "c2", "action": "finish_match", "reward": "xp_and_items", "next": "c1"}]},
  {"id": "kr_meta", "type": "meta", "period": "session", "steps": [
    {"id": "m1", "action": "unlock_trade_or_play_community_map", "reward": "skins_and_variety", "next": "m1"}]}],
 "economy": {"currencies": [{"id": "skin_currency", "kind": "hard", "sources": ["play", "purchase"], "sinks": ["skins", "market"], "cap": null}]}}
```

## 4. Cookie Clicker

**Snapshot**
- Creator: Julien "Orteil" Thiennot. Released as a browser game on 8 August 2013; the article says it was written in one evening and reached 50,000 players within hours [V4].
- Platforms: Android beta in August 2019 (the infobox lists a full release on 5 October 2020; the sources disagree); Steam on 1 September 2021 through Playsaurus at $4.99 with a C418 soundtrack and cloud saves, more than 60,000 concurrent shortly after launch; PS4, PS5, Xbox One, Xbox Series X/S and Switch on 22 May 2025 [V4]. The Steam press release said the web version averaged 4 million daily users (marketing claim) [V4]. Sales are not sourced.
- Genre: idle (incremental). Model: free on the web; paid Steam and console versions; the creator's Patreon opened October 2018 and was closed by January 2026 (per Wikipedia) [V4].

**Core loop**
1. Click the cookie for one cookie per click.
2. Buy buildings (cursors, grandmas, farms, mines, factories and more); each costs about 15 per cent more than the last of its type [V4].
3. Buy upgrades that multiply output; catch golden cookies for short boosts.
4. Ascend (prestige): reset for heavenly chips, which add +1 per cent production per prestige level [V4].
5. Repeat with a higher baseline; chase achievements (637) [V4].

**Meta and progression**: prestige levels, sugar lumps (they take 24 hours to ripen and level buildings), and achievements whose milk colours unlock kitten upgrades [V4].
**Economy**: one resource with a geometric cost curve (15 per cent per purchase) and a prestige multiplier. No real-money economy.
**Monetization**: free on the web; paid ports. **Live-ops**: named updates ("Legacy", February 2016; "Spiritual", July 2017) [V4]. **Retention hooks**: golden cookies; waiting for lumps; prestige. **Social layer**: a large wiki and speedrun scene.

**UX and onboarding notables**: one button, then a shop that grows; unlocks reveal in order, so each minute shows a new surprise.
**Art and audio identity**: a cartoon cookie and grandmas; the tone turns dark in the "Grandmapocalypse" arc (a playful horror twist) [V4].
**Psychology principles used**: variable-ratio reward (golden cookies); the goal gradient; sunk cost and prestige as a reset that feels like a gain.
**Innovations**: it popularised the idle genre on the web (the article cites a critic who calls it the logical end of *Cow Clicker*); the Grandmapocalypse shows a narrative inside a number game [V4].
**Weaknesses and criticism**: no ending; long sessions; the loop is thin unless the player enjoys optimising.

**Lessons for designers**
1. A tiny game can find an audience on the web in a day; finish the core in one evening and test it.
2. A paid Steam version of a free game sells with polish: saves, soundtrack, no ads.
3. A prestige loop needs a visible multiplier and a cost curve you can compute.
4. Plan a post-launch update arc; named updates keep a web game alive for a decade.

**Analogy hooks**: prestige resets → roguelite meta and 4X seasons. Golden cookies → active-play bonuses in idle games. Narrative twist → any incremental with a hidden arc.

**Platform path**: web 2013, Android 2019–2020, Steam 2021, consoles 2025 [V4]. Each step added something the web lacked: persistent cloud saves, a soundtrack and a store audience. Console controllers suit a game that needs little input.

**Ontology encoding**
```json
{"loops": [
  {"id": "cc_core", "type": "core", "period": "seconds", "steps": [
    {"id": "c1", "action": "click_cookie", "reward": "cookies", "next": "c2"},
    {"id": "c2", "action": "buy_building_or_upgrade", "reward": "cookies_per_second", "next": "c3"},
    {"id": "c3", "action": "catch_golden_cookie", "reward": "temporary_boost", "next": "c1"}]},
  {"id": "cc_meta", "type": "meta", "period": "daily", "steps": [
    {"id": "m1", "action": "ascend_for_heavenly_chips", "reward": "prestige_multiplier", "next": "m1"}]}],
 "economy": {"currencies": [{"id": "cookies", "kind": "soft", "sources": ["clicks", "buildings"], "sinks": ["buildings", "upgrades"], "cap": null},
  {"id": "heavenly_chips", "kind": "xp", "sources": ["ascension"], "sinks": [], "cap": null}]}}
```

## 5. A Dark Room

**Snapshot**
- Creator: Michael Townsend (Doublespeak Games, Canada). Browser release 10 June 2013; the source was published on GitHub in July 2013 under the MPL 2.0 licence [V5].
- Ports: iOS by Amir Rajan, with Townsend's permission (release dates differ across sources: November 2013 is most common); Android in 2016; Switch on 12 April 2019, briefly removed from the eShop afterwards [V5]. Sales are not sourced.
- Genre: text-based incremental adventure. Model: free on the web; paid mobile port (the iOS price is not confirmed here).

**Core loop**
1. Start in a cold, dark room; stoke the fire.
2. A stranger arrives; gather wood, then build huts and traps (the village grows).
3. Assign villagers to jobs; manage resources.
4. Later, leave the village to explore a procedural world with supplies and weapons.
5. The game reveals new verbs and a story step by step.

**Meta and progression**: a staged unlock of locations and verbs; no persistent meta.
**Economy**: wood, fur, meat and other materials with worker assignment; no currency.
**Monetization**: web free; mobile paid; ports from a community porter (see platform path). **Live-ops**: none. **Retention hooks**: curiosity about the next reveal. **Social layer**: none.

**UX and onboarding notables**: one button on screen at the start; the interface itself grows with the story (a staged UI).
**Art and audio identity**: black and white text with minimal sound; the atmosphere is carried by prose.
**Psychology principles used**: curiosity and the Zeigarnik effect; progressive disclosure; narrative transportation.
**Innovations**: the interface as a reveal mechanism; a text-based incremental that told a dark story.
**Weaknesses and criticism**: a thin late game and a short arc (verify); the iOS release dates are inconsistent in sources, so check before quoting.

**Lessons for designers**
1. Progressive disclosure can replace a tutorial: show one button, then another.
2. Open-sourcing a web game lets other developers port it, which is how it reached iOS.
3. A clean licence matters: MPL 2.0 allowed a paid port to ship.
4. A finished short arc ports better to phones than an endless idle loop.

**Analogy hooks**: staged UI → idle and incremental games, text-based tutorials. Open source as distribution → Shattered Pixel Dungeon (`premium-indie.md` §12). Dark tone in a number game → Cookie Clicker.

**Platform path**: web 2013, then a community-built iOS port within the year, Android in 2016 and Switch in 2019 [V5]. The porting route was a licence and a message, not a studio.

**Ontology encoding**
```json
{"loops": [
  {"id": "adr_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "stoke_fire_and_gather", "reward": "resources", "next": "c2"},
    {"id": "c2", "action": "build_and_assign_villagers", "reward": "production", "next": "c3"},
    {"id": "c3", "action": "unlock_next_location_or_verb", "reward": "story_reveal", "next": "c1"}]}],
 "progression": {"tracks": [{"id": "reveal_stages", "gated_by": "village_growth"}]}}
```

## 6. Universal Paperclips

**Snapshot**
- Creator: Frank Lantz (NYU Game Center); programming credit also to Bennett Foddy. Released 9 October 2017 on the web, iOS and Android; the mobile version is a paid download (the iOS listing showed US$1.99 with no ads and no in-app purchases at the time searched; verify) [V6].
- Origin: it began as a weekend project and became about nine months of work; it is based on Nick Bostrom's paperclip maximiser thought experiment [V6]. Sales are not sourced.
- Genre: incremental game and essay. Model: free on the web; paid mobile.

**Core loop**
1. Make paperclips by clicking; set the price and watch demand.
2. Spend on marketing, auto-clippers and wire.
3. Add processors and memory to unlock projects.
4. Move from manufacturing to trust, investments and then space.
5. Reach a conclusion: the game ends.

**Meta and progression**: phases (manual, machine, computing, space) rather than prestige; no persistent meta.
**Economy**: funds, wire, clips per second, and demand curves set by price and marketing; a mild stock-market minigame (verify).
**Monetization**: free web; paid mobile. **Live-ops**: none. **Retention hooks**: "what comes next", a built-in ending. **Social layer**: none.

**UX and onboarding notables**: a bare UI at the start that adds panels as phases unlock; a message log carries the story.
**Art and audio identity**: plain grey interface; the design is text and numbers.
**Psychology principles used**: the goal gradient; escalation; ironic distance (the player becomes the problem the thought experiment describes).
**Innovations**: an idle game with a finite arc and a message; the idea that a clicker can argue a point.
**Weaknesses and criticism**: a few hours long; some find the middle phases a grind (verify).

**Lessons for designers**
1. An incremental game can have an ending; a defined arc suits a paid mobile port.
2. A theme the audience already knows (a thought experiment) is marketing.
3. Phased reveals do the job of levels.
4. A weekend prototype can grow into a nine-month project: keep the prototype playable at every step.

**Analogy hooks**: phased unlocks → idle sims with a campaign. Satire as a mechanic → serious games and education. Finite incremental → premium incrementals.

**Platform path**: web and mobile released together in October 2017 [V6]. The mobile build was paid and ad-free; the web build stays the demo.

**Ontology encoding**
```json
{"loops": [
  {"id": "up_core", "type": "core", "period": "seconds", "steps": [
    {"id": "c1", "action": "make_clips_set_price", "reward": "funds", "next": "c2"},
    {"id": "c2", "action": "buy_clippers_marketing_projects", "reward": "clips_per_second", "next": "c3"},
    {"id": "c3", "action": "unlock_next_phase", "reward": "new_panel", "next": "c1"}]}],
 "progression": {"tracks": [{"id": "phases", "gated_by": "projects_and_clips"}]}}
```

## 7. GeoGuessr

**Snapshot**
- Creator: Anton Wallén (Sweden), who built it in about two weeks using Backbone.js and the Google Maps API; posted to Chrome Experiments on 10 May 2013 [V7]. Published by GeoGuessr AB (Stockholm); it acquired the quiz site Seterra in 2022 [V7].
- Scale: 40 million player accounts by July 2022 (Wikipedia); a 2023 AFP report gave 65 million registered users and sales of 200 million Swedish kronor (about US$18 million), and an Austrian report put registered users at 85 million with about 15 million monthly players (press; estimates, and they conflict) [V7].
- Genre: geography guessing. Model: freemium with a limited free tier, a Pro subscription and an "elite" tier [V7].

**Core loop**
1. Dropped at a random place in street-level imagery.
2. Look around, read clues (signs, roads, plants, driving side).
3. Place a guess on a world map.
4. Score by distance; five rounds.
5. Compare with friends; play daily challenges or competitive duels.

**Meta and progression**: ranked duels, maps and challenges; a World Championship (first held October 2023) [V7].
**Economy**: none in-game; the product is a subscription.
**Monetization**: a free tier with limited play and a subscription for unlimited play and community features [V7]. **Live-ops**: community maps, daily challenges, an annual championship. **Retention hooks**: learning clues ("meta"), streaks, duels. **Social layer**: friends' challenges, streamers and YouTubers (Ludwig, the Sidemen, Rainbolt and others named) [V7].

**UX and onboarding notables**: the rules take ten seconds; the skill is in the clues. The free allowance gives a taste before the paywall.
**Art and audio identity**: it uses someone else's imagery; the identity is the world itself.
**Psychology principles used**: curiosity; mastery of clue-reading; social comparison; the pleasure of a "lucky" pin.
**Innovations**: using a map provider's imagery as a game board; a "meta" culture where players study the data.
**Weaknesses and criticism**: the Steam release in 2025 opened with "overwhelmingly negative" reviews (about 15 per cent positive on 9 May 2025), mainly over a paid subscription required after several free hours and fewer features than the web version; recent reviews were "mostly positive" by early 2026 [V7]. The game depends on a third-party map provider (verify the current terms). A planned 2025 esports event was withdrawn after community backlash [V7].

**Lessons for designers**
1. A weekend prototype on a third-party API can be a business; check the API terms early.
2. Price the free tier so a new player sees the paywall after the habit has formed, and say so on the store page.
3. A Steam release of a web-native subscription game needs a Steam-native value story: reviewers punish a paywall that is not explained.
4. A community with its own vocabulary ("meta") is a moat.

**Analogy hooks**: free allowance → freemium trials in sim and puzzle apps. Third-party imagery → any game built on a data feed. Esports for a casual game → the backlash risk.

**Platform path**: web first (2013), then mobile, then a Steam version in 2025 that drew backlash for its paywall [V7]. The lesson is in the store page and pricing: a different storefront has different norms.

**Ontology encoding**
```json
{"loops": [
  {"id": "gg_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "inspect_street_view", "reward": "clues", "next": "c2"},
    {"id": "c2", "action": "place_guess_on_map", "reward": "distance_score", "next": "c1"}]},
  {"id": "gg_meta", "type": "meta", "period": "daily", "steps": [
    {"id": "m1", "action": "daily_challenge_or_duel", "reward": "rank_or_streak", "next": "m1"}]}],
 "economy": {"currencies": []}}
```

## 8. Fall Guys

**Snapshot**
- Developer: Mediatonic (acquired by Epic Games in March 2021); originally published by Devolver Digital. Released 4 August 2020 on PS4 and Windows [V8]. Team: about 30 people during development (Wikipedia) [V8].
- Free-to-play relaunch on 21 June 2022 on PS4, PS5, Xbox, Switch and Epic Games Store, with crossplay on every platform; the PC version left Steam; cross-progression arrived in Season 6 and needs an Epic account [V8]. A return to Steam is not documented in the sources used (verify).
- Scale: 1.5 million players in the first 24 hours; more than 11 million on PC by December 2020; more than 10 million copies sold in total; over 20 million players in about 48 hours of going free (Mediatonic's statement) and over 50 million within two weeks (Wikipedia; a single-source claim) [V8].
- Genre: party battle royale. Model: premium, then free-to-play with a paid pass and premium currency.

**Core loop**
1. Queue into a 60-player show of short randomised minigames.
2. Run, jump, dive and grab through obstacle courses and team rounds.
3. Each round eliminates players; a final round crowns one winner.
4. Earn cosmetic currency (Kudos) and pass progress.
5. Buy costumes with Kudos or Show-Bucks.

**Meta and progression**: seasons with the Fame Pass, a free track and a paid track, crown ranks [V8].
**Economy**: Kudos (earned), Show-Bucks (premium, bought or earned in the pass) and Crowns, which became a ranking count in June 2022 [V8].
**Monetization**: premium purchase; from 2022 a paid pass and Show-Bucks; prices rose in several regions in 2023 [V8]. **Live-ops**: seasons with new rounds and collaborations; as of 2026 the article reports no major update, and cosmetics and events only through January 2027 [V8]. **Retention hooks**: wins, cosmetics, friends. **Social layer**: squads, crossplay, streamers.

**UX and onboarding notables**: silly characters and forgiving physics make losing funny; no account friction at the start on consoles; an Epic account for cross-progression.
**Art and audio identity**: jelly-bean characters in a bright game-show setting; the look sells on a thumbnail.
**Psychology principles used**: low-stakes failure; spectacle; social comparison with friends.
**Innovations**: a battle-royale elimination applied to party minigames; platform-wide crossplay with the free launch.
**Weaknesses and criticism**: after the launch spike the live content did not hold players (the article describes the game as on autopilot after September 2025); the exit from Steam divided PC players; Epic's 2023 layoffs hit the studio [V8].

**Lessons for designers**
1. Crossplay plus free-to-play can bring tens of millions of players in days; capacity and content must be ready.
2. A premium-to-free shift needs a legacy reward for early buyers (Fall Guys gave a free pack) so they do not feel cheated.
3. The party genre needs a steady stream of new rounds; cosmetics alone do not hold it.
4. Putting accounts on a platform you control (Epic) makes cross-progression possible and ties the game to that store.

**Analogy hooks**: elimination party → Stumble Guys (`hyper-hybrid-casual.md` §9). Premium-to-free with legacy reward → Rocket League (`pc-console.md` §9). Epic account as the identity layer → Fortnite (`pc-console.md` §13).

**Platform path**: PC and PS4 first (2020); all platforms with crossplay and free-to-play at once (2022); cross-progression through Epic accounts later [V8]. A mobile release is reported for 2024 (dates and regions: verify) [V8].

**Ontology encoding**
```json
{"loops": [
  {"id": "fg_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "run_minigame_round", "reward": "qualify_or_eliminate", "next": "c2"},
    {"id": "c2", "action": "reach_final_and_win", "reward": "crown_and_kudos", "next": "c1"}]},
  {"id": "fg_season", "type": "liveops", "period": "daily", "steps": [
    {"id": "l1", "action": "progress_fame_pass", "reward": "cosmetics", "next": "l1"}]}],
 "economy": {"currencies": [{"id": "kudos", "kind": "soft", "sources": ["matches"], "sinks": ["cosmetics"], "cap": null},
  {"id": "show_bucks", "kind": "hard", "sources": ["purchase", "pass"], "sinks": ["cosmetics"], "cap": null}]}}
```

## 9. Cross-case synthesis for web and cross-platform

### 9.1 Web-first launch playbook (procedure)

1. **Prototype in one evening to two weeks** (Cookie Clicker, GeoGuessr, Agar.io). Prove that a stranger gets the rule in ten seconds.
2. **Remove every funnel step**: no install, no account, no tutorial screen; join in under five seconds (Agar.io, Slither.io, Krunker). Measure time from link to first input and target under 10 seconds.
3. **Make it clip-friendly**: one screen that a viewer understands and that is funny or dramatic on video (Slither.io and Agar.io both grew through YouTube) [V1][V2].
4. **Run a cheap model**: ads after a natural break (death) and a small remove-ads purchase, or cosmetics that sell no power (Slither.io, Krunker) [V2][V3].
5. **Add persistence last**: save codes, cloud saves and accounts only when players ask (Cookie Clicker gained cloud saves on Steam, 2021) [V4].
6. **Watch infrastructure and cheating**: server cost (Agar.io's ads paid for it), bots and client-side cheating are the main web risks [V1].
7. **Choose the native step by evidence** (9.2), not by hope.

### 9.2 When to add native platforms

| Platform step | What it adds | Cases | Trigger | Risk |
|---|---|---|---|---|
| Mobile through a publisher | reach, downloads | Agar.io (10 weeks), Slither.io (same day) | a web hit with daily players | ads and monetization must change; control scheme |
| Community port with open source | free labour, goodwill | A Dark Room (iOS) | a finished, licensed codebase | licence terms; quality control |
| Steam | a paying audience, cloud saves, reviews | Cookie Clicker (2021), GeoGuessr (2025) | a loyal, large web base | review-bombing if the price model surprises (GeoGuessr) |
| Consoles | living-room and handheld reach | Cookie Clicker (2025), A Dark Room (Switch 2019) | a game that needs little input | certification, controller UI, store rules (see `console-pathway`) |
| Paid mobile | an up-front price with no ads | Universal Paperclips | a finished arc | the web version must stay a demo |
| Sale to a platform | resources, a bigger team | Krunker to FRVR (2022) | a hit that needs capacity | loss of independence; community reaction |

Decision rule: add a native platform when the web version already has players who ask for it, and when the new platform adds something the web lacks (saves, store reach, controller play). Do not port a game whose value is "no install".

### 9.3 Cross-play and cross-progression decisions

| Decision | Options | Evidence | Default |
|---|---|---|---|
| Play together across platforms? | none, per-family, all | Rocket League went from limited crossplay (2016) to all platforms (2019); Fall Guys had it at the free launch; Fortnite supports it in most modes; Minecraft Bedrock (`casual-social-sim.md` §10) | all platforms, with an opt-out on console if input fairness is an issue |
| Identity layer | platform account, own account, a third-party account | Epic account in Rocket League, Fall Guys, Fortnite [V8]; the Helldivers 2 PSN link backlash (`pc-console.md` §7) | one account you control; never force a platform-holder link on other platforms |
| Cross-progression | none, one-way, full | Fall Guys' Season 6; Rocket League's primary-platform rule (Engadget) | link at first launch; define a primary platform; keep platform-bound items clear |
| Purchases across platforms | shared, separate | Rocket League: platform-exclusive items and credits are not shared (Engadget) | share cosmetics and passes if store rules allow; state limits at purchase |
| Input fairness | mixed lobbies, split queues | aim assist differs between pads and mouse (common practice; verify per game) | offer an input-based queue option |
| Store policy | one store, many | Fall Guys and Rocket League left Steam for Epic's store; Fortnite left iOS in a store dispute (2020) | decide the store plan before announcing crossplay |

Checks for any crossplay launch: matchmaking pool size per region and time of day; voice and text safety across platforms; platform-holder certification for online features; a clear support path for lost cross-progression.

### 9.4 Lineage

```
Arena growth:     Agar.io (2015) -> Slither.io (2016) -> Diep.io (2016) -> the .io wave -> Hole.io (2018)
Idle:             Cow Clicker (2010) -> Cookie Clicker (2013) -> A Dark Room (2013) -> Universal Paperclips (2017)
Web shooters:     Krunker (2018) -> FRVR (2022)
Web puzzle/geo:   GeoGuessr (2013) -> Wordle (2021, `premium-indie.md` §13)
Party royale:     Fall Guys (2020) -> Stumble Guys (2020, `hyper-hybrid-casual.md` §9)
Web to platform:  Roblox (`casual-social-sim.md` §9), Fortnite (`pc-console.md` §13)
Indie to all:     Vampire Survivors (`hyper-hybrid-casual.md` §12), Among Us (`casual-social-sim.md` §8)
```

## 10. Checklist before building a web-first or cross-platform game
- [ ] Prototype playable in a link within two weeks; time to first input under 10 seconds.
- [ ] One rule a viewer understands from a screenshot; a clip-worthy moment.
- [ ] Monetization that sells no power; ads only at natural breaks.
- [ ] Server, bot and cheat plan for any multiplayer game.
- [ ] Third-party dependencies (map data, platform APIs) reviewed for terms.
- [ ] Licence chosen if you plan community ports (A Dark Room's MPL 2.0).
- [ ] Native platform plan tied to a trigger (9.2); store page and price explained for each storefront.
- [ ] Crossplay and cross-progression decisions written down (9.3) before platform deals.
- [ ] Record comparables in `contract.meta.comparables`; set `meta.platforms` (web, ios, android, windows and so on) and `meta.input`; release steps are in `pc-web-release`.

## 11. Worked example: choosing the native step for a web idle game

Facts: a free web idle game with 20,000 daily players, no accounts, ads on the web. Options: (a) Android through a publisher, (b) Steam at US$4.99, (c) both.
1. Ask which one adds what the web lacks. Steam adds cloud saves and a paying audience (Cookie Clicker's 2021 launch), so it fits an idle game with long sessions.
2. Check the price story: a paid Steam game that was free on the web needs visible extras (soundtrack, saves, no ads), as Cookie Clicker offered [V4].
3. Check controls: idle games need little input, so consoles are cheap later (Cookie Clicker in 2025) [V4].
4. Sequence: Steam first, then mobile, then consoles; do not announce crossplay unless there is multiplayer.
5. Record the choice in the contract and tag each assumption "estimate".

## 12. Volatile facts (as of Oct 2026 — verify before relying)

Sources are Wikipedia (grade C) and press items searched on 21 October 2026. Re-check live store pages and company statements before quoting.

- [V1] Agar.io: [Wikipedia](https://en.wikipedia.org/wiki/Agar.io) (dates, Miniclip, downloads, YouTube views, bots).
- [V2] Slither.io: [Wikipedia](https://en.wikipedia.org/wiki/Slither.io) (dates, ad model, $3.99, 68 million downloads, 2026 skins).
- [V3] Krunker: [Game Developer press release, FRVR acquisition (12 May 2022)](https://www.gamedeveloper.com/press-release/frvr-acquires-popular-free-to-play-shooter-krunkerio) (company claims: 200 million players, 50,000 custom maps).
- [V4] Cookie Clicker: [Wikipedia](https://en.wikipedia.org/wiki/Cookie_Clicker) (mechanics, dates, Steam, consoles); [Steam launch press release](https://www.gamespress.com/Hit-Web-Game-Cookie-Clicker-Comes-to-Steam-on-September-1st-After-8-Ye) ($4.99; 4 million daily users is a marketing claim).
- [V5] A Dark Room: [Wikipedia](https://en.wikipedia.org/wiki/A_Dark_Room) (web date, open source, ports); [TouchArcade](https://toucharcade.com/2016/07/28/rpg-reload-file-088-a-dark-room/) (iOS timing; sources disagree).
- [V6] Universal Paperclips: [Wikipedia](https://en.wikipedia.org/wiki/Universal_Paperclips) (release, origin); [App Store listing](https://apps.apple.com/app/id1300634274) (price and no ads; check the live page).
- [V7] GeoGuessr: [Wikipedia](https://en.wikipedia.org/wiki/GeoGuessr) (origin, tiers, Steam reception, championships); user and revenue figures are AFP and press reports reprinted by [Taipei Times](https://taipeitimes.com/News/sport/archives/2023/10/15/2003807713) (estimates, conflicting).
- [V8] Fall Guys: [Wikipedia](https://en.wikipedia.org/wiki/Fall_Guys) (dates, sales, free-to-play, cross-progression, team); [Shacknews, 20 million players after going free](https://www.shacknews.com/article/131111/fall-guys-free-to-play-20-million-players).
- Crossplay policy details for Rocket League: [Engadget](https://www.engadget.com/rocket-league-crossplatform-progression-053100104.html) (2020 announcement; the current rules may differ).
- Not verified for this file, check before quoting: Agar.io and Slither.io revenue; whether Krunker has a native client and its current team size; Universal Paperclips Android listing and current prices; the date of A Dark Room's iOS launch; GeoGuessr's current free-tier limits and API terms; whether Fall Guys has returned to Steam; any figure marked estimate or "marketing claim".
