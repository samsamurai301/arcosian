# Puzzle and casual case studies

Fourteen deconstructions of puzzle-led casual games. They run from the saga-map match-3 that set free-to-play puzzle economics (Candy Crush Saga), through the renovation and team metas of the late 2010s (Homescapes, Toon Blast, Royal Match), to the ad-funded "satisfying" puzzles of the 2020s (block, sort, triple-match, screw-pin). Read them as one lineage. Almost every winner kept a proven chassis and changed one or two things: a simpler verb, faster feel, a meta that gives levels meaning, or a different monetization channel. Each case uses the 16-lens format from `SKILL.md` and ends with an ontology encoding that uses the contract field names (`loops[].steps[]`, `economy.currencies[]`). Revenue figures are left out unless publicly confirmed. Mechanics are described as publicly observable in the shipped games. Where a detail is uncertain, or changes often in live builds, the text says "verify". Volatile market facts are collected in section 16 with sources.

**Contents.** Sections 1–14 are case studies (index below). Section 15 is a cross-case synthesis with decision tables. Section 16 lists volatile facts with sources.

| # | Game | Genre | Year | Key lesson |
|---|---|---|---|---|
| 1 | Candy Crush Saga | match-3, saga map | 2012 | The product is a level-content machine; the purchase sits at the near-miss |
| 2 | Royal Match | match-3, renovation meta | 2021 | In a mature genre, speed, polish and one simple currency beat novelty |
| 3 | Homescapes | match-3, renovation + story | 2017 | A narrative meta gives each level a "why"; ad creatives must match the game |
| 4 | Toon Blast | tap-blast (collapse) | 2017 | A simpler verb plus team competition widens the funnel |
| 5 | Block Blast! | block puzzle | c. 2022 (breakout 2024–26) | An evergreen mechanic plus juice plus ad monetization scales to the top of the charts |
| 6 | Wordscapes | word (anagram + crossword) | 2017 | Audience-first aesthetics and a fair hint economy |
| 7 | Two Dots | connect-the-dots | 2014 | Derive the power move from the core gesture; design restraint as brand |
| 8 | Triple-match (Triple Match 3D genre) | tile/object triple-match | c. 2021–22 | A bounded buffer turns "find pairs" into a planning puzzle |
| 9 | Magic Sort! / water sort | sort puzzle | c. 2020 genre; 2020s exemplar | Deterministic levels can be solver-verified before shipping |
| 10 | Screw and pin puzzles (genre) | screw-pin, physics sort | 2019–2025 waves | Ad-creative testing as concept discovery, but ship what the ad shows |
| 11 | Cut the Rope | physics puzzle | 2010 | A puzzle can found a character IP; 3-star mastery adds depth for free |
| 12 | Threes! and 2048 | number sliding | 2014 | Depth vs accessibility; mechanics cannot be protected, so execution and reach win |
| 13 | Tetris (mobile) | falling block | 1984 (mobile 2000s–) | Translating precise controls to touch; licence-bound evolution |
| 14 | Royal Kingdom | match-3, kingdom meta | 2024 | The second-hit problem: same chassis, new meta, managed cannibalization |

---

## 1. Candy Crush Saga

**Snapshot**
- Developer: King (Stockholm and London studios). Activision Blizzard acquired King in 2016, and Microsoft acquired Activision Blizzard in 2023.
- Release: 2012 on Facebook, iOS and Android later in 2012.
- Genre: swap match-3 with move-limited levels on a linear "saga" map. Business model: free-to-play, IAP-led (gold bars, boosters, lives, extra moves).
- Scale: among the longest-running top-grossing mobile games. New level episodes ship on a regular cadence, and the level count reached five figures by the mid-2020s (verify the current count in-game). Revenue figures are omitted.

**Core loop**
1. Pick the next node on the saga map. A failed attempt costs one life.
2. Optionally equip pre-level boosters.
3. Swap adjacent candies to make lines of 3+ within a move limit.
4. Build specials and combine them. Four in a line makes a striped candy (clears a row or column). An L or T of five makes a wrapped candy (a double area blast). Five in a line makes a colour bomb (clears one colour). Special + special makes a larger effect.
5. Meet the objective: a score target, clearing all jelly, bringing ingredients down, or collecting a candy order.
6. Win: leftover moves turn into specials in the end-of-level "Sugar Crush" payoff, then 1–3 stars and the map advances. Lose: a life is spent and an extra-moves offer appears.

**Meta and progression**
- A linear map split into episodes (15 levels each in the classic structure) with themed worlds. Stars per level form a completionist layer.
- Early versions gated each new episode: ask three Facebook friends for tickets, pay, or (later) complete quests. These gates were softened over time (verify the current design).
- Modern builds visibly flag harder levels, so a spike reads as an event rather than a wall (verify the labels in the current build).

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Gold bars | hard | IAP, occasional event rewards | extra moves, lives refill, boosters |
| Lives | energy | regenerate one per ~30 min up to 5; friend gifts | one per failed or abandoned attempt |
| Boosters | material | daily booster wheel, events, IAP bundles | pre-level and in-level use |

**Monetization**
- The highest-intent offer is extra moves on the fail screen. It appears at the near-miss, when the remaining objective is visibly small.
- Lives refills, booster bundles and limited-time offers. King's portfolio has added advertising over the years, so check the current build for placements before citing it.

**Live-ops**
- New episodes on a cadence of weeks, recurring time-limited events (streaks, collections, competitions), seasonal themes, and a daily booster wheel.
- Difficulty tuning backed by data: King trained human-like bots on player moves to predict level difficulty before release (Gudmundsson et al., 2018). Follow-up work cut estimates to under a minute per level, against days of human playtesting per episode (see section 16).

**Retention hooks**: lives timers create appointments, the daily wheel is a login reward, an unfinished level pulls the player back (Zeigarnik), friends sit ahead on the map, and the difficulty sawtooth follows hard levels with relief levels.

**Social layer**: Facebook-linked friend avatars on the map, per-level friend leaderboards, life gifting and help requests, and cross-device progress through Facebook or a King account. All social play is asynchronous and there is no chat.

**UX and onboarding notables**
- Hands-on tutorial levels with forced first swaps, then one new concept per level. The objective and move counter are always visible, and a hint animation plays after a few idle seconds.
- A level-start popup restates the objective and offers boosters, so the player commits before starting.

**Art and audio identity**: glossy candy with saturated colours, and each candy type differs in shape as well as colour (a dual code that helps readability and colour-blind players). A deep announcer voice escalates with cascade size ("Sweet!", "Divine!"). SFX pitch rises through combos.

**Psychology principles used**: variable-ratio reinforcement from random refills and windfall cascades (Skinner). The near-miss effect at the fail screen (Reid, 1986) combines with loss aversion (Kahneman and Tversky, 1979) to price the continue. Goal-gradient on the map (Hull; Kivetz et al., 2006). Social comparison with friends' positions (Festinger, 1954). The peak-end rule (Kahneman) makes "Sugar Crush" the peak and the end at once.

**Innovations (at the time)**
- Proved the free-to-play "saga" model for puzzles: thousands of authored levels on a linear map, plus the social graph, lives and paid boosters. It built on King's earlier saga titles and web match-3 heritage.
- Early large-scale cross-platform sync between Facebook and mobile.
- Industrialised level production with telemetry and, later, AI playtesting bots.

**Weaknesses and criticism**
- Difficulty spikes read as paywalls, and the energy cap frustrates binge players.
- Ethical: the purchase is concentrated at frustration moments. Critics frame fail-screen offers as "pay to avoid loss", which matters most for minors and vulnerable spenders (`legal-ethics`).
- In 2014, King's attempts to trademark "Candy" and its opposition to "The Banner Saga" drew wide criticism. King reportedly dropped the US "Candy" application.
- The saga-only meta looks thin next to renovation metas (sections 2–3).

**Lessons for designers**
1. Content cadence is the product. Build the level pipeline (editor, bot difficulty estimate, telemetry) before the 50th level.
2. Put the one must-buy moment where intent is highest, and keep it optional and fairly priced. Never manufacture a fake near-miss.
3. Dual-code tiles (shape + colour) for small screens and colour-blind players.
4. Turn leftover resources into an end-of-level spectacle (peak-end).
5. Use a sawtooth difficulty curve with relief levels (`difficulty_curve.py generate --pattern sawtooth`).

**Analogy hooks**
- Saga map with friend markers → any level-based game (golf, rhythm, physics, word).
- The "+5 moves" continue → runner revive, roguelite second wind, golf mulligan.
- Leftover-to-bonus payoff → tower defense (remaining lives become gold), racing (unused boost becomes score).
- Bot-estimated difficulty → any deterministic puzzle (`match3_sim.py`, `puzzle_solver.py`).

**Ontology encoding**
```json
{"loops": [
  {"id": "ccs_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "select_level_on_saga_map", "reward": "objective_preview", "next": "c2"},
    {"id": "c2", "action": "swap_match_within_move_limit", "reward": "cascades_specials_score", "next": "c3"},
    {"id": "c3", "action": "meet_objective_or_run_out_of_moves", "reward": "stars_map_progress_or_life_loss", "next": "c4"},
    {"id": "c4", "action": "accept_extra_moves_offer_or_retry", "reward": "second_chance", "next": "c1"}]},
  {"id": "ccs_meta", "type": "meta", "period": "daily", "steps": [
    {"id": "m1", "action": "spin_daily_booster_wheel", "reward": "booster", "next": "m2"},
    {"id": "m2", "action": "play_until_lives_empty", "reward": "map_progress", "next": "m3"},
    {"id": "m3", "action": "wait_or_request_lives", "reward": "lives", "next": "m1"}]}],
 "economy": {"currencies": [
  {"id": "gold_bars", "kind": "hard", "sources": ["iap", "events"], "sinks": ["extra_moves", "lives_refill", "boosters"], "cap": null},
  {"id": "lives", "kind": "energy", "sources": ["regen_30min", "friend_gifts", "gold_bars"], "sinks": ["failed_attempt"], "cap": 5},
  {"id": "boosters", "kind": "material", "sources": ["daily_wheel", "events", "iap_bundles"], "sinks": ["pre_level", "in_level"], "cap": null}]}}
```

## 2. Royal Match

**Snapshot**
- Developer: Dream Games (Istanbul, founded 2019 by former Peak Games staff).
- Release: global release on 25 February 2021, after a limited test from July 2020 in Canada, Turkey and the UK ([Wikipedia: Dream Games](https://en.wikipedia.org/wiki/Dream_Games)).
- Genre: swap match-3 with a castle-renovation meta. Business model: free-to-play, IAP-led. Coins are the single currency that is both earned and bought (`hard`). The launch build had no forced ads (verify the current build).
- Scale: widely reported as one of the top-grossing puzzle games of the mid-2020s. A deal between Dream Games and Savvy Games Group has been reported, but its date and terms could not be confirmed in this review (the Dream Games Wikipedia article does not mention it), so verify before quoting. Revenue figures are omitted.

**Core loop**
1. Tap the single "Level N" button on the castle screen. There is no map to navigate.
2. Optionally pick pre-level boosters, and receive any win-streak boosters ("Butler's Gift").
3. Swap to match within a move limit. Four in a line makes a rocket. A 2×2 square makes a propeller, which flies to a goal tile. An L or T makes TNT. Five in a line makes a light ball, which clears a colour. Specials combine.
4. Clear the goal counters (collect pieces, break obstacles).
5. Win: one star plus coins, and the streak advances. Lose: a life is spent, an offer of extra moves for coins appears, and the streak resets.
6. Spend stars on renovation tasks in the current castle area. A completed area pays a reward and opens the next one.

**Meta and progression**
- Castle areas made of star-priced tasks, each completion a visible makeover. The meta is light on story (King Robert as mascot) and heavy on progress feedback.
- Harder levels carry explicit "hard" and "super hard" labels with better rewards, which frames a spike as a challenge.

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Coins | hard | level wins, area and event chests, IAP | extra moves, boosters, lives refill |
| Stars | material | one per level win | renovation tasks |
| Lives | energy | timed regen up to 5; team gifts; time-limited unlimited-lives grants | failed attempts |
| Boosters | material | streaks, chests, events, bundles | pre-level and in-level use |

**Monetization**: coin packs, bundles that mix coins, boosters and timed unlimited lives, the extra-moves continue, and a season pass ("Royal Pass") with free and paid tracks. With only one currency, every price is legible.

**Live-ops**: a dense rotating calendar of competitions and collection events. Names seen in-game around 2023–2025 include King's Cup (a level-race leaderboard), Lightning Rush, Sky Race, Star Tournament, team chests and team battles. Names rotate, so verify before citing.

**Retention hooks**: the Butler's Gift streak, event leaderboards that reset on short cycles, area-completion bars (goal-gradient), lives timers, and team obligations.

**Social layer**: teams with chat and life requests, team events, and leaderboards. Social play is asynchronous and competitive rather than cooperative.

**UX and onboarding notables**
- Time-to-gameplay is minimal: one tap from launch to board, fast animations, and instant retry.
- The quit dialog lists what the player loses (a life, the streak boosters), which is loss-aversion framing.
- Objective-seeking specials (the propeller) keep the end of a level from becoming a hunt for one last tile.

**Art and audio identity**: bright, clean 3D-rendered pieces with strong silhouettes, a comic king mascot, punchy SFX, and short, crisp celebrations. User-acquisition creatives were known for putting the king in comic peril.

**Psychology principles used**: loss aversion on streaks and quit dialogs. The endowed-progress effect from partly filled area bars (Nunes and Drèze, 2006). Competence from fast, readable cascades (SDT, Deci and Ryan). Social comparison in short leaderboard races.

**Innovations**
- Not mechanically new. It refined the Toon Blast and Homescapes lineage to a high polish: the fastest loop in its class, and a single-currency economy.
- Popularised the win-streak start bonus (Butler's Gift) as both a retention device and a smoother for early-level difficulty.
- Normalised labelled hard levels as a positive event.

**Weaknesses and criticism**
- A derivative core and a shallow meta narrative.
- Difficulty walls appear late in the level ladder, and offers on fail and quit are frequent.
- The streak-loss framing pressures purchases at failure.
- Its success depended on very large user-acquisition spend, which is a barrier for any imitator.

**Lessons for designers**
1. In a consolidated genre, compete on time-to-fun and feel, not on features.
2. One currency reduces cognitive load and makes prices legible. It also forces discipline in economy design.
3. A win-streak bonus rewards skill, smooths difficulty, and creates a reason to come back. Cap it and make it visible.
4. Specials that seek the objective remove the worst part of match-3, the end-of-level hunt.
5. Measure taps-to-board and seconds-to-first-match as KPIs.

**Analogy hooks**
- Butler's Gift → golf (a start-of-hole power-up after consecutive pars), runners (head start), roguelites (a starting relic after a win streak).
- Labelled hard levels → any curve with spikes (rhythm, physics, tower defense).
- Short leaderboard races (King's Cup) → any level-based game with fast completions.

**Ontology encoding**
```json
{"loops": [
  {"id": "rm_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "tap_level_button", "reward": "board_with_streak_boosters", "next": "c2"},
    {"id": "c2", "action": "swap_match_build_specials", "reward": "goal_progress", "next": "c3"},
    {"id": "c3", "action": "clear_goals_or_fail", "reward": "star_coins_streak_or_life_loss", "next": "c4"},
    {"id": "c4", "action": "spend_stars_on_area_task", "reward": "castle_makeover", "next": "c1"}]},
  {"id": "rm_liveops", "type": "liveops", "period": "daily", "steps": [
    {"id": "l1", "action": "join_timed_competition", "reward": "leaderboard_slot", "next": "l2"},
    {"id": "l2", "action": "win_levels_fast", "reward": "rank_progress", "next": "l3"},
    {"id": "l3", "action": "claim_event_chest", "reward": "coins_boosters", "next": "l1"}]}],
 "economy": {"currencies": [
  {"id": "coins", "kind": "hard", "sources": ["level_win", "chests", "iap"], "sinks": ["extra_moves", "boosters", "lives_refill"], "cap": null},
  {"id": "stars", "kind": "material", "sources": ["level_win"], "sinks": ["area_tasks"], "cap": null},
  {"id": "lives", "kind": "energy", "sources": ["regen", "team_gifts", "unlimited_lives_grants"], "sinks": ["failed_attempt"], "cap": 5}]}}
```

## 3. Homescapes

**Snapshot**
- Developer: Playrix (founded by Igor and Dmitry Bukhman; headquartered in Dublin, Ireland).
- Release: 2017. It followed Gardenscapes: New Acres (2016), which introduced the formula, and shares that game's butler mascot, Austin.
- Genre: swap match-3 with home renovation and a serialized comic story. Business model: free-to-play, IAP-led (coins, boosters, lives).
- Scale: one of the defining casual hits of the late 2010s. Revenue figures are omitted.

**Core loop**
1. A story task asks for stars, for example "fix the staircase" for one star.
2. Play a match-3 level. A win gives one star plus coins.
3. Spend stars to complete the task. Some tasks let the player choose one of three décor styles.
4. A short scripted dialogue advances the story and unlocks the next task. A finished room ends a "day" or chapter and opens a new area.
- Specials: four in a line makes a rocket, an L or T makes a bomb, a 2×2 square makes a paper plane (which flies to a goal), and five in a line makes a rainbow ball.

**Meta and progression**: rooms and areas of the mansion, story chapters, and décor choices that persist. The story gives every level a narrative purpose.

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Coins | hard | level wins, events, IAP | extra moves, boosters, lives refill |
| Stars | material | one per level win | story and renovation tasks |
| Lives | energy | timed regen up to 5; team gifts | failed attempts |

**Monetization**: coin packs, booster bundles, timed unlimited lives, the extra-moves continue, and event or season offers (verify the current lineup).

**Live-ops**: time-limited events, team competitions, seasonal festivals, collection events, and new rooms and story chapters delivered through updates.

**Retention hooks**: story cliffhangers and curiosity about the next room (Loewenstein's information gap). Persistent self-expression through décor choices. Team obligations and lives timers.

**Social layer**: teams with chat and life sharing, team events, and Facebook connect.

**UX and onboarding notables**
- The game opens on a story situation before the first puzzle (the run-down mansion), so the player understands why they are playing.
- An early "choose your style" décor moment creates ownership.
- The task list shows star costs, so the next goal is always one tap away.

**Art and audio identity**: cosy, warm, illustrated 3D interiors, cartoon characters with comedic dialogue, and before/after makeover reveals as the main visual reward.

**Psychology principles used**: the IKEA effect and endowment from chosen décor (Norton, Mochon and Ariely, 2012; Thaler). Narrative transportation. The Zeigarnik effect from open story threads. Goal-gradient through room completion.

**Innovations**
- Gardenscapes (2016) and Homescapes (2017) established "match-3 + renovation + story" as the dominant casual-puzzle meta. Lily's Garden, Matchington Mansion and Royal Match all adopted it.
- Popularised objective-seeking specials (the paper plane).
- Proved that a casual audience values story and decoration as reasons to solve puzzles.

**Weaknesses and criticism**
- Advertising: user-acquisition ads showed pin-pull and rescue scenes that were not in the game. The UK ASA ruled in 2020 that certain Homescapes and Gardenscapes ads were misleading (verify the details). Playrix later added comparable mini-games to the games.
- Décor choices are cosmetic only, and the story does not branch.
- Star gating forces level play even when the player only wants the story.
- The renovation art pipeline is expensive: every task needs bespoke art.

**Lessons for designers**
1. A meta that gives levels a reason (story, décor) raises retention more than another special piece.
2. Build ad creatives from the game's real content, or bring the advertised content into the game before scaling user acquisition. Misleading ads are a regulatory and reputational risk (`marketing-ua`, `legal-ethics`).
3. Self-expression choices, even cosmetic ones, create ownership. Offer them early.
4. Budget art for the meta: renovation games are art-production businesses.

**Analogy hooks**
- "Spend earned stars on story tasks" → any puzzle (sort, word, solitaire, block), or a runner with distance converted into tasks.
- Before/after makeover reveals → restoration sims, island builders, base cleanup.
- The ad-to-game pipeline: test which mini-game the ads sell, then build it in.

**Ontology encoding**
```json
{"loops": [
  {"id": "hs_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "play_match3_level", "reward": "star_and_coins", "next": "c2"},
    {"id": "c2", "action": "spend_star_on_story_task", "reward": "renovation_and_dialogue", "next": "c3"},
    {"id": "c3", "action": "choose_decor_style", "reward": "self_expression", "next": "c1"}]},
  {"id": "hs_meta", "type": "meta", "period": "session", "steps": [
    {"id": "m1", "action": "complete_room_task_list", "reward": "room_reveal", "next": "m2"},
    {"id": "m2", "action": "unlock_next_chapter", "reward": "new_story_beats", "next": "m1"}]}],
 "economy": {"currencies": [
  {"id": "coins", "kind": "hard", "sources": ["level_win", "events", "iap"], "sinks": ["extra_moves", "boosters", "lives_refill"], "cap": null},
  {"id": "stars", "kind": "material", "sources": ["level_win"], "sinks": ["story_tasks"], "cap": null},
  {"id": "lives", "kind": "energy", "sources": ["regen", "team_gifts"], "sinks": ["failed_attempt"], "cap": 5}]}}
```

## 4. Toon Blast

**Snapshot**
- Developer: Peak Games (Istanbul). Zynga acquired Peak in 2020, and Take-Two acquired Zynga in 2022.
- Release: 2017. It succeeded the studio's Toy Blast (2015).
- Genre: tap-to-blast ("collapse") puzzle with move-limited levels on a map. Business model: free-to-play, IAP-led (coins).
- Scale: a top-grossing casual puzzle for years after launch. Revenue figures are omitted.

**Core loop**
1. Enter the next level on the map. A failed attempt costs a life.
2. Tap any group of 2+ adjacent same-colour cubes to blast it. No swap is needed and there are no invalid moves.
3. Larger groups create specials. The in-game tutorial uses thresholds of about 5 cubes for a rocket, 7 for a bomb and 9 for a disco ball. Specials combine into bigger effects.
4. Clear the goal counters (cubes of a colour, balloons, crates, ducks and similar) within the moves.
5. Win: coins and map progress. Lose: a life is spent and an extra-moves offer appears.

**Meta and progression**: an episodic map, cartoon mascots (Cooper the cat, Wally the wolf, Bruno the bear), star or level chests, and steadily added obstacle types.

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Coins | hard | level wins, chests, team rewards, IAP | extra moves, boosters, lives |
| Lives | energy | timed regen up to 5; teammates' gifts | failed attempts |
| Boosters | material | chests, events, bundles | pre-level and in-level use |

**Monetization**: coin packs, bundles, timed unlimited lives, and the extra-moves continue.

**Live-ops**: team tournaments, individual events and seasonal themes. Team-versus-team competition is the backbone of the calendar.

**Retention hooks**: team membership is the anchor (obligations, life requests, rank). Then lives timers, map progress, and recurring tournaments.

**Social layer**
- Teams (on the order of 50 members; verify the cap) with chat, life requests and gifts, team chests, and team tournaments with rewards.
- Many casual players experience their first real community here.

**UX and onboarding notables**
- The tap verb removes the two hardest parts of swap match-3 for novices: finding a valid move and two-cell planning.
- Bigger groups visibly preview the special they will create, which teaches planning without a tutorial wall.

**Art and audio identity**: Saturday-morning cartoon characters, bright primary colours, and chunky cubes. Cascades are loud and comic.

**Psychology principles used**: low effort per action raises session flow (Csikszentmihalyi). Relatedness and reciprocity in teams (SDT; Cialdini, 1984). Social comparison in team ranks. Variable reward from refills.

**Innovations**
- Took the collapse mechanic of older "SameGame"-style puzzles mainstream in modern free-to-play form: lower cognitive load, faster pacing.
- Made team tournaments a central casual retention system, a template that later match-3s adopted.

**Weaknesses and criticism**
- More outcome variance than swap match-3, so skill expression is lower and players complain about "luck levels".
- Repetitive in long sessions. Difficulty spikes are paired with offers.
- Collapse-only boards limit level-design variety compared with swap mechanics.

**Lessons for designers**
1. Removing an invalid-move state widens the audience. Check whether your verb has dead inputs.
2. Teams retain casual players, so design team goals that a 2-minute session can still contribute to.
3. Preview what an action will create (the special icon on large groups) to teach planning implicitly.
4. When variance rises, provide counter-variance tools (boosters, specials that target goals) so outcomes feel earned.

**Analogy hooks**
- Tap-collapse → RPG skill charging (blast groups to power heroes), merge-battlers, tower-defense resource generation.
- Team tournaments → any asynchronous single-player loop (golf, word, solitaire).
- A "group size → special tier" threshold table → crafting systems (bigger batches make better items).

**Ontology encoding**
```json
{"loops": [
  {"id": "tb_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "tap_same_colour_group", "reward": "blast_and_refill", "next": "c2"},
    {"id": "c2", "action": "build_special_from_large_group", "reward": "rocket_bomb_disco", "next": "c3"},
    {"id": "c3", "action": "clear_goals_within_moves", "reward": "coins_map_progress_or_life_loss", "next": "c1"}]},
  {"id": "tb_social", "type": "social", "period": "weekly", "steps": [
    {"id": "s1", "action": "contribute_wins_to_team_tournament", "reward": "team_rank", "next": "s2"},
    {"id": "s2", "action": "request_and_gift_lives", "reward": "lives", "next": "s3"},
    {"id": "s3", "action": "claim_team_chest", "reward": "coins_boosters", "next": "s1"}]}],
 "economy": {"currencies": [
  {"id": "coins", "kind": "hard", "sources": ["level_win", "team_chest", "iap"], "sinks": ["extra_moves", "boosters", "lives_refill"], "cap": null},
  {"id": "lives", "kind": "energy", "sources": ["regen", "team_gifts"], "sinks": ["failed_attempt"], "cap": 5}]}}
```

## 5. Block Blast!

**Snapshot**
- Developer: Hungry Studio (the developer name on the App Store listing; the seller of record is Aretis Limited). The studio is reported to be China-based, which was not confirmed here.
- Release: first released on the iOS App Store on 3 April 2022 (App Store listing metadata, read through Apple's iTunes Search API). It broke out globally in 2024 and topped worldwide downloads in H1 2026 (section 16, [V1]).
- Genre: block puzzle (polyomino placement and line clearing, no gravity). Business model: ad-led hybrid with interstitial and rewarded ads, plus IAP such as ad removal (verify the current offers).
- Lineage: 1010! (Gram Games, 2014) and the Sudoku-grid variants Woodoku and Blockudoku (late 2010s). Block Blast! is an execution-and-distribution winner, not a mechanical first.

**Core loop**
1. Receive a tray of three random block pieces.
2. Drag each piece onto the 8×8 grid in any order.
3. Full rows and columns clear. Clearing several lines at once, or clearing on consecutive placements, builds combo multipliers.
4. When all three pieces are placed, a new tray appears.
5. The game ends when none of the remaining pieces fit. The player chases their high score and restarts in seconds.
- Modes: endless classic for high score, plus a level-based adventure mode with collection goals (verify the current modes).

**Meta and progression**: the personal best is the main meta. Adventure levels add a light ladder. There is no energy system.

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Score / high score | xp | line clears, combos | none (status only) |
| Adventure progress | xp | level completion | none |

**Monetization**
- Ads carry the business. Long, calm sessions with natural breaks (game over, between levels) give many interstitial slots. Rewarded placements offer continues or bonuses (verify the placements).
- Ad removal and small IAP exist (verify).

**Live-ops**: light. Novelty comes from modes, themes and adventure levels rather than event calendars (verify).

**Retention hooks**: self-competition against the high score, zero-friction restart, no timers or energy, and a ritual "relaxing" habit.

**Social layer**: minimal; high scores can be shared.

**UX and onboarding notables**
- The dragged piece floats above the finger so the thumb never hides the drop target. This offset is essential in any drag-placement game.
- A ghost preview shows where the piece will land and which lines will clear.
- Almost no tutorial is needed, because the rule is visible in the first placement.

**Art and audio identity**: bright, gem-like bevelled blocks on a dark board, chunky clear bursts with combo callouts, and haptics on clears.

**Psychology principles used**
- Gestalt closure: completing a line is intrinsically satisfying.
- Flow from self-paced challenge (Csikszentmihalyi).
- Variable reward from combos, and near-miss game overs ("one more piece would have fit").
- Low cognitive load supports mood repair.

**Innovations**: no new rule. The edge was tuning (piece mix, combo feel), juice, an ad-monetized long-session model, and very large-scale user acquisition across a wide demographic.

**Weaknesses and criticism**
- Ad load complaints.
- Shallow progression.
- Players speculate about whether piece generation is fair or adaptive. Any adaptive generator must be tested for perceived fairness and disclosed where appropriate.
- Low defensibility: the mechanic is a commodity, and clones are trivial.

**Lessons for designers**
1. Evergreen mechanics plus execution plus the right monetization channel can top the charts. Novelty is not required, but the user-acquisition and ad-mediation engine is.
2. The piece generator *is* the difficulty curve. Decide between pure random, weighted random, bag-style and "guarantee at least one fit" rules, and verify them with bots.
3. Drag offset and ghost preview are mandatory.
4. In ad-led games, pace ads to natural breaks and protect the first sessions (interstitial `first_after_sec` and `min_interval_sec` in the contract).

**Analogy hooks**
- Place-and-clear as combat: clearing lines deals damage, in the spirit of puzzle-RPG hybrids.
- Tray-of-three drafting → deckbuilders and tactics (three offered actions per turn).
- Combo streak multiplier → any score-attack game.

**Ontology encoding**
```json
{"loops": [
  {"id": "bb_core", "type": "core", "period": "seconds", "steps": [
    {"id": "c1", "action": "receive_tray_of_three_pieces", "reward": "planning_options", "next": "c2"},
    {"id": "c2", "action": "drag_piece_onto_grid", "reward": "placement", "next": "c3"},
    {"id": "c3", "action": "complete_rows_or_columns", "reward": "clear_combo_score", "next": "c4"},
    {"id": "c4", "action": "check_any_piece_fits", "reward": "continue_or_game_over", "next": "c1"}]},
  {"id": "bb_session", "type": "meta", "period": "session", "steps": [
    {"id": "m1", "action": "chase_high_score", "reward": "new_best", "next": "m2"},
    {"id": "m2", "action": "restart_after_game_over", "reward": "fresh_board", "next": "m1"}]}],
 "economy": {"currencies": [
  {"id": "score", "kind": "xp", "sources": ["line_clear", "combo"], "sinks": [], "cap": null}]}}
```

## 6. Wordscapes

**Snapshot**
- Developer: PeopleFun (Texas).
- Release: 2017.
- Genre: word puzzle that combines an anagram letter wheel with a small crossword grid. Business model: hybrid. Interstitial and rewarded ads, IAP coin packs, and ad removal.
- Audience: skews adult, with a relaxation and "brain exercise" positioning.

**Core loop**
1. A level shows a small crossword and a wheel of about 5–7 letters.
2. Swipe across the letters to form a word. Words that fit the grid fill in. Other valid words count as bonus words.
3. When stuck, shuffle the wheel for free, or spend coins on hints (for example, reveal a letter).
4. Complete the grid to earn coins and move to the next level. Levels are grouped into themed packs with a scenic background.

**Meta and progression**: thousands of levels in packs with nature-photo backgrounds, a daily puzzle with streak or calendar rewards, and events added over time (verify the current lineup).

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Coins | soft (purchasable) | level completion, a bonus-word meter, daily puzzle, rewarded ads, IAP | hints |

**Monetization**: interstitials between levels, rewarded ads for coins, coin packs, and an ad-removal purchase. Hints are the only real sink, so stuck-ness is the spend moment.

**Live-ops**: daily puzzles, seasonal or weekly events, and tournaments or team features in later builds (verify).

**Retention hooks**: the daily puzzle ritual, a long level ladder, new background scenery as a reward, and vocabulary mastery as part of identity.

**Social layer**: light (Facebook connect; later community or team features — verify).

**UX and onboarding notables**
- Large letters and high contrast suit older eyes, and the swipe path is drawn as the finger moves.
- A free shuffle unblocks perception without spending.
- Bonus words reward exploration, so no swipe feels wasted.

**Art and audio identity**: high-resolution landscape photography, soft UI, gentle music and chimes. The positioning is "calm" rather than "exciting".

**Psychology principles used**: competence (SDT). Mood repair and relaxation. A variable reward when a bonus word is found. Curiosity about the next scene. The commitment of a daily streak (Cialdini).

**Innovations**: it combined two familiar formats, the anagram wheel and the crossword, and tuned the result for adults with a spa-like aesthetic. Similar wheel-word games appeared around the same time, so its edge was execution and audience fit rather than a new rule.

**Weaknesses and criticism**
- Interstitials break the calm the game sells.
- Dictionary disputes over valid or invalid words.
- Repetitive in long play, with a thin meta.

**Lessons for designers**
1. Choose the aesthetic for the audience, not for the genre's defaults.
2. A hint economy works when free tools (shuffle) solve most blocks, and paid hints solve the rest.
3. Reward discovery beyond the required solution with a bonus meter.
4. In a "calm" game, ad placement is part of the experience design. Test interstitial frequency against D7.

**Analogy hooks**
- The bonus-discovery meter → any puzzle with multiple solutions (alternate routes, extra combos).
- Background-as-reward → solitaire, sort and block puzzles.
- The daily puzzle → every level-based game (see Wordle in `references/premium-indie.md`).

**Ontology encoding**
```json
{"loops": [
  {"id": "ws_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "swipe_letters_to_form_word", "reward": "grid_fill_or_bonus_word", "next": "c2"},
    {"id": "c2", "action": "shuffle_or_buy_hint_when_stuck", "reward": "unblock", "next": "c3"},
    {"id": "c3", "action": "complete_grid", "reward": "coins_next_level", "next": "c1"}]},
  {"id": "ws_daily", "type": "meta", "period": "daily", "steps": [
    {"id": "d1", "action": "solve_daily_puzzle", "reward": "streak_progress", "next": "d2"},
    {"id": "d2", "action": "claim_calendar_reward", "reward": "coins", "next": "d1"}]}],
 "economy": {"currencies": [
  {"id": "coins", "kind": "soft", "sources": ["level_complete", "bonus_word_meter", "daily_puzzle", "rewarded_ad", "iap"], "sinks": ["hints"], "cap": null}]}}
```

## 7. Two Dots

**Snapshot**
- Developer: Playdots (New York). Take-Two acquired Playdots in 2020.
- Release: 2014. It was the level-based sequel to the score-attack game Dots (2013).
- Genre: connect-the-dots puzzle with move-limited levels. Business model: free-to-play with lives and boosters (verify the current ad placements).

**Core loop**
1. Enter a level, which costs a life on failure.
2. Draw a line through 2+ adjacent same-colour dots (horizontal and vertical only). Releasing the line clears those dots.
3. Close a loop (a square) to clear every dot of that colour on the board. This is the power move.
4. Meet the goals (collect counts of colours, drop anchors to the bottom, clear obstacles such as ice) within the moves.
5. Win: advance on the map. Lose: a life is spent, with continue offers.

**Meta and progression**: a travel-themed "expedition" map of locations, steady new obstacles, and themed events (verify the event names).

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Premium currency (coins/gems by version) | hard | IAP, events | boosters, extra moves, lives |
| Lives | energy | timed regen | failed attempts |
| Boosters | material | events, purchase | in-level use |

**Monetization**: boosters, extra moves and lives refills (verify the current ads).

**Live-ops**: seasonal and themed events, new expedition chapters, and periodic collection or exploration features (verify the names).

**Retention hooks**: the next location on the map, lives timers, events, and an aesthetic pleasure that players return to.

**Social layer**: light (friend leaderboards and connect features; verify).

**UX and onboarding notables**
- One gesture (draw) teaches everything. The square rule is discoverable by play and then confirmed by the tutorial.
- The line drawing is continuous and reversible: backtracking along the path un-selects dots.

**Art and audio identity**
- Flat, minimalist geometry with a restrained palette, and a design-led brand that stood out from glossy candy competitors.
- Rising tones play as the chain grows, so sound doubles as feedback on chain length.

**Psychology principles used**: competence through an elegant rule. Aesthetic pleasure and mood. A discovery "aha" when the player finds the square trick. Variable reward from refills.

**Innovations**
- A power move derived from the core gesture (closing a loop) instead of separate special pieces created by geometry.
- A minimalist design language and musical feedback in a genre dominated by maximalist candy.

**Weaknesses and criticism**
- Fewer special interactions mean variety had to come from a growing list of obstacles.
- Lives gating and difficulty spikes are typical of the genre.
- The minimalism limits the narrative and decoration hooks that later metas exploit.

**Lessons for designers**
1. Look for the power move inside the verb (a closed loop, a long chain, a perfect timing) before adding power-up items.
2. Make chain length audible: pitch-stepped tones are cheap and effective feedback.
3. Visual restraint is a differentiator when a genre is visually loud.

**Analogy hooks**
- Loop closure as a power move → territory games (see Paper.io 2 in `references/hyper-hybrid-casual.md`), spell drawing, rhythm path games.
- Line-drawing combat → chain-draw puzzles (see Grindstone in `references/premium-indie.md`).
- Pitch-stepped chain audio → any combo system.

**Ontology encoding**
```json
{"loops": [
  {"id": "td_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "draw_line_through_same_colour_dots", "reward": "clear_and_rising_tones", "next": "c2"},
    {"id": "c2", "action": "close_square_loop", "reward": "clear_all_of_colour", "next": "c3"},
    {"id": "c3", "action": "meet_goals_within_moves", "reward": "map_progress_or_life_loss", "next": "c1"}]}],
 "economy": {"currencies": [
  {"id": "premium_currency", "kind": "hard", "sources": ["iap", "events"], "sinks": ["boosters", "extra_moves", "lives_refill"], "cap": null},
  {"id": "lives", "kind": "energy", "sources": ["regen"], "sinks": ["failed_attempt"], "cap": 5}]}}
```

## 8. Triple-match (Triple Match 3D and tile-tray games)

**Snapshot**
- Developer: this is a genre case. Several publishers ship near-identical apps under the title "Triple Match 3D" and similar names, so check the specific listing before citing one. Related 2D variants (tile-tray games such as Tile Busters-style titles) use the same tray rule.
- Lineage:
  - Mahjong solitaire (computer versions from the 1980s): match uncovered pairs.
  - "Sheep a Sheep" (China, 2022): a viral mini-game known for a near-impossible second level.
  - 3D-object "Match 3D" variants (early 2020s).
- Year: the tray format surged around 2021–22.
- Business model: hybrid. Ads (interstitial and rewarded continues) plus IAP (coins, boosters, lives).

**Core loop**
1. A level spawns a heap of 3D objects (tile variants: layered tiles where only uncovered ones are tappable) and usually a timer.
2. Tap an item to send it to a tray with a fixed number of slots (7 is common).
3. Three identical items in the tray clear automatically.
4. Clear the board before time runs out. If the tray fills with no triple, the level fails.
5. Win: coins or stars plus chest progress. Fail: a continue offer (extra time, an extra slot, an undo) for coins or an ad.
- Boosters (vary by app): undo, magnet (auto-collect a triple), shuffle, freeze the timer, extra tray slot, hint.

**Meta and progression**: level ladders with star chests, collection albums, and in some apps a renovation or decoration meta (verify per app).

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Coins | soft (purchasable) | level wins, chests, rewarded ads, IAP | continues, boosters |
| Stars | material | level wins | chests, meta tasks |
| Lives | energy | timed regen (app-dependent) | failed attempts |

**Monetization**: rewarded continues at the tray-full or time-out moment, interstitials between levels, booster and coin packs, and ad removal.

**Live-ops**: collection events, leaderboards and seasonal themes in the more developed apps. Many smaller apps run no live-ops at all.

**Retention hooks**: level ladders, chest progress, and a "messy to tidy" ritual that rewards each clear.

**Social layer**: usually minimal, with occasional leaderboards and teams in larger apps.

**UX and onboarding notables**
- The tray is the whole rule set, and it is visible from the first tap.
- Readability is the main UX risk: objects must have distinct silhouettes and colours at phone size. A pinch or zoom option helps.
- Highlighting pieces that already have pairs in the tray reduces search fatigue.

**Art and audio identity**: toy-like 3D objects (food, toys, tools) in a physics heap, satisfying "pop" clears, tidy tray animations, and haptics.

**Psychology principles used**
- Visual search and pop-out, the hidden-object pleasure.
- Working-memory pressure from the bounded tray.
- Completion and closure when a triple clears.
- Arousal from time pressure, and loss aversion at tray-full.

**Innovations**
- The bounded tray turns unbounded pair-finding into a planning puzzle with a fail state.
- 3D physics heaps add tactile toy-ness and natural occlusion as a source of difficulty.

**Weaknesses and criticism**
- Clutter on small screens, and occlusion luck: needed items buried in the heap.
- Timers punish slower or older players.
- Ad-heavy.
- Ethical: "Sheep a Sheep" was criticised for a second level widely seen as engineered to be almost unwinnable, which drove shares and ad views. Do not design rigged levels.

**Lessons for designers**
1. Buffer size is the main difficulty knob. Seven versus six tray slots changes win rate dramatically, so tune it with bots, not by feel.
2. Generate levels with a solver that guarantees a solution under the tray constraint. Reject unsolvable heaps.
3. Distinct silhouettes plus colour-coded families keep search fair.
4. Offer a timer-free mode or generous timers for older audiences.

**Analogy hooks**
- A bounded buffer with auto-craft on three → inventory-pressure crafting in RPGs, kitchen and order games.
- Triple auto-merge → merge-2 boards, auto-battler unit upgrades (three copies make a star-up).
- Heap occlusion → hidden-object and cleaning sims.

**Ontology encoding**
```json
{"loops": [
  {"id": "tm_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "scan_heap_and_tap_item", "reward": "item_to_tray", "next": "c2"},
    {"id": "c2", "action": "form_triple_in_tray", "reward": "auto_clear", "next": "c3"},
    {"id": "c3", "action": "clear_board_before_timer_or_tray_full", "reward": "coins_stars_or_continue_offer", "next": "c1"}]}],
 "economy": {"currencies": [
  {"id": "coins", "kind": "soft", "sources": ["level_win", "chests", "rewarded_ad", "iap"], "sinks": ["continues", "boosters"], "cap": null},
  {"id": "stars", "kind": "material", "sources": ["level_win"], "sinks": ["chests", "meta_tasks"], "cap": null},
  {"id": "lives", "kind": "energy", "sources": ["regen"], "sinks": ["failed_attempt"], "cap": 5}]}}
```

## 9. Magic Sort! and the water-sort genre

**Snapshot**
- Developer: the exemplar is Magic Sort!, from Grand Games (Grand Games A.Ş.; the App Store seller and developer name, bundle `com.grandgames.magicsort`). The genre comes from the "Water Sort Puzzle" and ball-sort apps of around 2020, published by many small studios. Several unrelated apps share the name "Magic Sort" (check the seller before citing).
- Release: the genre broke out around 2020. Magic Sort! is a later, more polished entrant, first released on the iOS App Store on 28 May 2024 (App Store listing metadata, read through Apple's iTunes Search API).
- Genre: sort puzzle with deterministic, discrete state. Business model: ad-led hybrid (interstitials, rewarded "extra tube" or undo) plus IAP (ad removal, packs).

**Core loop**
1. A level shows N tubes, each holding up to 4 layers of coloured liquid, plus 1–2 empty tubes.
2. Tap a source tube, then a target. The top contiguous run of one colour pours across if the target is empty or its top colour matches, and it has space.
3. Plan the order: empty tubes are buffers, and wasting them causes deadlock.
4. When stuck, use undo (limited), add an extra tube (booster or rewarded ad), or restart.
5. Win when every tube holds a single colour. Then the next level (and any meta reward).
- Exemplar twists (verify in-game): hidden layers revealed when uncovered, more colours and tubes, special obstacles, and a light collection or decoration meta.

**Meta and progression**: a level counter and, in polished entrants, collections or themed rewards. The genre is mostly meta-light.

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Coins (in polished entrants) | soft | level wins, rewarded ads | extra tube, undo, cosmetic themes |
| Extra tubes / undos | material | starting stock, ads, purchase | stuck states |

**Monetization**: the stuck moment is the monetization moment (watch an ad for an extra tube). Interstitials between levels and ad removal.

**Live-ops**: minimal in most apps. Polished entrants add events and themes (verify).

**Retention hooks**: no timers or energy in most apps, quick wins, and a calm "tidying" ritual.

**Social layer**: none to minimal.

**UX and onboarding notables**
- Two-tap interaction (source, then target) with an invalid-pour wiggle as feedback.
- The pour animation must be short (around 0.3–0.6 s) or long levels drag.
- Colour-blind support needs pattern or symbol overlays, since colour is the only identity in the base genre.

**Art and audio identity**: glossy tubes, liquid shaders, soft pour and bubble sounds (ASMR-like), and clean backgrounds.

**Psychology principles used**: order from chaos and closure. Planning competence. Low-pressure flow without a timer. The small-win cadence (Amabile and Kramer's progress principle, 2011).

**Innovations**
- A minimal rule set with deep planning, and (rare for ad-led games) ads that honestly show the gameplay.
- Polished entrants differentiate with hidden information (unrevealed layers) that adds uncertainty while staying fair, because reveals follow deterministic rules.

**Weaknesses and criticism**
- Repetitive: difficulty comes from more colours and tubes rather than new ideas.
- Heavy cloning, ad load, and colour-only identity accessibility issues.

**Lessons for designers**
1. Deterministic puzzles can be verified offline: solvability, minimum moves, and dead-end density. Use `puzzle_solver.py` with `layout.type: "sort"` and record `solver.solvable` and `solver.min_moves` in the level spec.
2. The difficulty knobs are colours C, tube capacity K, empty tubes E, and the undo budget. Reducing E is usually the biggest single jump. Verify that with the solver rather than assuming it.
3. Add one fair source of uncertainty (hidden layers) to keep the genre fresh.
4. Make the stuck state monetizable but never mandatory: always offer restart and undo.

**Analogy hooks**
- The pour-sort rule → potion mixing in RPGs, cargo and logistics sims, laundry or kitchen sorting.
- The "empty buffer" concept → inventory-slot puzzles, train-yard shunting puzzles.
- Hidden layers → fog-of-war in puzzle form.

**Ontology encoding**
```json
{"loops": [
  {"id": "ms_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "select_source_tube", "reward": "selection", "next": "c2"},
    {"id": "c2", "action": "pour_into_matching_or_empty_tube", "reward": "progress_toward_single_colour", "next": "c3"},
    {"id": "c3", "action": "undo_or_add_tube_if_stuck", "reward": "unblock", "next": "c4"},
    {"id": "c4", "action": "complete_all_tubes", "reward": "next_level", "next": "c1"}]}],
 "economy": {"currencies": [
  {"id": "coins", "kind": "soft", "sources": ["level_win", "rewarded_ad"], "sinks": ["extra_tube", "undo", "themes"], "cap": null},
  {"id": "extra_tubes", "kind": "material", "sources": ["starting_stock", "rewarded_ad", "iap"], "sinks": ["stuck_state"], "cap": null}]}}
```

## 10. Screw and pin puzzles (genre case)

**Snapshot**
- Developer: this is a genre case.
  - Screw ("nuts and bolts") wave, 2023–2025: many near-identical apps. A representative listing is "Screw Jam", published by Rollic Games (App Store seller Rollic Games Oyun Yazilim ve Pazarlama Anonim Sirketi; first App Store release 8 December 2023, per the listing metadata).
  - Pin-pull, from around 2019: "Pull the Pin"-style apps.
- Year: pin-pull around 2019–2020, screw-sort around 2023–2025.
- Genre: physics-revealed sort puzzle and gravity-routing puzzle. Business model: ad-led hybrid (interstitials, rewarded slot or undo) with light IAP.
- Origin note: pin-pull scenes were famous as advertising creatives for unrelated games before they became games in their own right (see Homescapes, section 3).

**Core loop (screw-sort variant)**
1. The board shows layered plates held by coloured screws. Colour boxes at the top each take 3 screws of their colour, and a small holding tray takes misfits.
2. Tap any screw not covered by a plate above it. It flies to its matching box, or to the holding tray if no box matches.
3. A plate with no screws left falls away under physics and reveals more screws.
4. A filled box leaves and the next colour box arrives.
5. Win when every plate is cleared. Lose when the holding tray overflows. Rewarded ads offer an extra slot.

**Core loop (pin-pull variant)**: pull pins in sequence so that gravity routes balls, water or treasure to a goal while hazards (lava, enemies) are kept apart. Mistakes are visible at once and restarts take a second.

**Meta and progression**: level ladders, cosmetic themes for boards and screws, and in some apps a decoration or collection meta.

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Coins | soft | level wins, rewarded ads | extra slot, drill/remove-screw booster, themes |
| Boosters | material | stock, ads, IAP | stuck states |

**Monetization**: rewarded "extra slot" and booster placements at the overflow moment, interstitials, and ad removal.

**Live-ops**: minimal in most apps.

**Retention hooks**: quick levels, satisfying physics drops, and a tactile "unscrewing" fantasy.

**Social layer**: none to minimal.

**UX and onboarding notables**
- The covered/uncovered state must be readable. Highlight tappable screws, or dim covered ones.
- Physics drops must not create unfair states (plates landing on top of needed screws). Many apps despawn fallen plates.

**Art and audio identity**: wood and metal textures, chunky screws, mechanical ratchet SFX, and a satisfying clatter when plates fall.

**Psychology principles used**: tactile and ASMR satisfaction. Order from chaos. Planning under a bounded buffer (the same structure as section 8). Curiosity about what each falling plate will reveal.

**Innovations**
- Physics as a reveal mechanic, combined with a bounded-buffer sort.
- Market validation through advertising: mechanics that first won click-through as creatives were later built as real games.

**Weaknesses and criticism**
- Shallow and clone-saturated. Physics non-determinism can create unfair states.
- Ad-heavy.
- The genre's origin is tied to misleading-ad history (section 3).

**Lessons for designers**
1. Use ad-creative tests (CTR, CPI) as cheap concept discovery before production (`marketing-ua`). Then deliver what the ad shows.
2. Make outcomes deterministic: fixed physics seeds or scripted drops, so the solver and the player see the same puzzle.
3. Reuse the bounded-buffer pattern deliberately: it is the shared core of the triple-match, screw and sort genres.

**Analogy hooks**
- Disassembly as play → repair and restoration sims, crafting tutorials.
- Pin ordering → environmental logic puzzles inside adventure games, and dungeon trap sequencing.
- Colour boxes that arrive in sequence → order-fulfilment games (deliver in the requested order).

**Ontology encoding**
```json
{"loops": [
  {"id": "sp_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "tap_uncovered_screw", "reward": "screw_to_box_or_holding_tray", "next": "c2"},
    {"id": "c2", "action": "free_plate_of_all_screws", "reward": "plate_falls_reveals_screws", "next": "c3"},
    {"id": "c3", "action": "fill_colour_box", "reward": "next_box_arrives", "next": "c4"},
    {"id": "c4", "action": "clear_board_or_overflow", "reward": "next_level_or_rewarded_slot_offer", "next": "c1"}]}],
 "economy": {"currencies": [
  {"id": "coins", "kind": "soft", "sources": ["level_win", "rewarded_ad"], "sinks": ["extra_slot", "boosters", "themes"], "cap": null}]}}
```

## 11. Cut the Rope

**Snapshot**
- Developer: ZeptoLab (founded by Semyon and Efim Voinov). The original iOS release was published by Chillingo.
- Release: 2010.
- Genre: physics puzzle. Business model: premium at launch, later free and ad-supported editions, plus sequels and subscription-service versions (verify each edition's model).
- Scale: became a durable character franchise (Om Nom) with sequels, spin-offs and animated shorts.

**Core loop**
1. A level shows candy hanging from ropes, three stars, and Om Nom waiting.
2. Swipe to cut ropes, and tap tools (bubbles that float the candy, air cushions that push it) to steer the candy's swing and fall.
3. Collect stars along the path. Avoid spikes and other hazards.
4. Feed Om Nom to win, scoring 1–3 stars. Restart instantly on failure.
5. Collect stars to unlock the next themed level box.

**Meta and progression**: themed boxes of levels unlocked by star thresholds, new physics elements introduced per box, and optional mastery through 3-star completion.

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Stars | xp | collected in levels | unlock thresholds (not spent) |
| Hints/boosters (later free editions) | material | IAP, ads | hints, power-ups |

**Monetization**: originally a one-time purchase plus level-pack updates. Later editions added IAP hints and boosters and ads (verify per edition).

**Live-ops**: content updates with new boxes in the premium era. There was no event calendar.

**Retention hooks**: star thresholds (completion), the next box's new mechanic (curiosity), and attachment to the character.

**Social layer**: Game Center leaderboards and achievements, and organic word of mouth.

**UX and onboarding notables**
- Each box teaches one new element through a short sequence of levels: teach, test, twist (`level-design`).
- The swipe-to-cut gesture is touch-native and instantly understood.
- Instant restart, no failure screen friction.

**Art and audio identity**: a hand-drawn cardboard aesthetic, and Om Nom's expressive reactions (eager, chewing, sad when the candy is lost). A light, playful score.

**Psychology principles used**: an emotional response from a character turns success into caring (anthropomorphism). Mastery and completion via stars. Physics experimentation as curiosity.

**Innovations**
- A character-centred physics puzzle: the "client" reacts emotionally to the player's outcomes.
- With Angry Birds (see `references/hyper-hybrid-casual.md`), it helped establish the 3-star level convention on mobile.
- Built a lasting IP from a puzzle mechanic.

**Weaknesses and criticism**
- Premium-era content was finite, and the move to free-to-play editions added monetization that some players disliked.
- The franchise relied on sequels for new mechanics.

**Lessons for designers**
1. Give the goal a face: a reacting character makes failure and success emotional at near-zero cost.
2. Stars as optional mastery let casual players progress while experts replay. Use unlock thresholds below 100% stars.
3. Introduce one new physics element per pack and sequence levels teach → test → twist → reward.

**Analogy hooks**
- A reactive "client" character → delivery, cooking and rescue puzzles, sort games (the recipient reacts).
- Star-threshold pack unlocks → any level-based game wanting gentle gating without energy.
- Cut and swing physics → rope-based platformers, grappling runners.

**Ontology encoding**
```json
{"loops": [
  {"id": "ctr_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "cut_ropes_and_trigger_tools", "reward": "candy_trajectory", "next": "c2"},
    {"id": "c2", "action": "collect_stars_avoid_hazards", "reward": "star_count", "next": "c3"},
    {"id": "c3", "action": "feed_om_nom_or_retry", "reward": "character_reaction_level_complete", "next": "c1"}]},
  {"id": "ctr_meta", "type": "meta", "period": "session", "steps": [
    {"id": "m1", "action": "reach_star_threshold", "reward": "unlock_next_box", "next": "m2"},
    {"id": "m2", "action": "learn_new_physics_element", "reward": "fresh_puzzles", "next": "m1"}]}],
 "economy": {"currencies": [
  {"id": "stars", "kind": "xp", "sources": ["level_collectibles"], "sinks": [], "cap": null}]}}
```

## 12. Threes! and 2048

**Snapshot**
- Threes!: developed by Sirvo (Asher Vollmer and Greg Wohlwend, music by Jimmy Hinson). Released in 2014 as premium iOS, with an ad-supported free version later (verify the editions).
- 2048: Gabriele Cirulli, 2014. A free, open-source web game built in a weekend. It was derived from earlier clones (Veewo's "1024" and Saming's "2048"), which were themselves derived from Threes!, and Cirulli credited them.
- Genre: number-merge sliding puzzle on a 4×4 grid.
- Scale: 2048 spread virally through the web and countless forks. Threes! won critical acclaim. Figures are omitted.

**Core loop (Threes!)**
1. Swipe in a direction. Every tile that can move shifts one cell.
2. A 1 and a 2 combine into a 3. Equal tiles of 3 or more combine (3+3=6, 6+6=12, and so on).
3. A new tile enters from the edge you swiped away from. A "next" indicator previews its value or colour.
4. The game ends when no swipe changes the board. The score counts each tile of 3 or more as 3^k, where the tile equals 3·2^(k−1).

**Core loop (2048)**
1. Swipe. All tiles slide fully to the edge.
2. Equal powers of two merge once per move.
3. A 2 (sometimes a 4) spawns in a random empty cell.
4. The goal is to make the 2048 tile, and play can continue past it. The game ends when no merge or move is possible.

**Meta and progression**: high score only. Threes! adds personality: tiles have faces and voices, and new tiles are "met" as you reach them.

**Economy**: none in the core. Encode score as `xp`.

**Monetization**
- Threes!: a premium price, with a later ad-supported free edition (verify).
- 2048: none in the original. Countless monetized clones appeared on the app stores.

**Live-ops**: none.

**Retention hooks**: the high score, the next milestone tile, and short sessions that fit any break.

**Social layer**: score sharing. 2048's open-source code invited themed forks, which spread it as a meme.

**UX and onboarding notables**: four-direction swipes, a learn-by-doing rule, and an instant restart. The next-tile preview in Threes! is what makes deep planning possible.

**Art and audio identity**: Threes! has pastel tiles with characters, a jazzy soundtrack, and tile voices. 2048 has a flat beige palette with a colour ramp by value, deliberately plain.

**Psychology principles used**: planning competence and flow. Exponential milestones (each new tile a goal-gradient step). In 2048's case, low frustration from forgiving sliding.

**Innovations**
- Threes!: a distinctive one-step-shift merge rule with an asymmetric 1+2 pairing, refined over a long design process. After the clones appeared, Sirvo published a detailed public account of that process (more than a year of development).
- 2048: showed that a free, open web version with simplified rules can out-spread a premium original within weeks.

**Weaknesses and criticism**
- Threes! was harder to learn, and its paid model limited reach against free clones.
- 2048 is shallower: a "corner strategy" trivialises much of the game.
- The episode became the standard example of how fast mechanics are cloned.

**Lessons for designers**
1. Depth versus accessibility is a dial. Forgiving rules (full slides) spread faster. Constrained rules (one-step shifts, asymmetric pairs) reward mastery. Choose deliberately for your audience.
2. Mechanics are not protectable in practice. Defence lies in reach (free, cross-platform), speed, personality and brand.
3. Information design (the next-tile preview) is the main depth lever in deterministic-feeling puzzles.
4. Publishing your design history builds goodwill, but it does not stop clones. Launch broad and fast.

**Analogy hooks**
- Merge-on-collision sliding → merge-2 boards, inventory puzzles, idle merge.
- Exponential tile milestones → idle-game number goals.
- A next-item preview → block puzzles (tray), match-3 (next refill hints), roguelite draft queues.

**Ontology encoding**
```json
{"loops": [
  {"id": "t2048_core", "type": "core", "period": "seconds", "steps": [
    {"id": "c1", "action": "swipe_direction", "reward": "tiles_shift_and_merge", "next": "c2"},
    {"id": "c2", "action": "read_spawned_or_next_tile", "reward": "planning_information", "next": "c3"},
    {"id": "c3", "action": "reach_next_milestone_tile", "reward": "score_and_new_tile_type", "next": "c1"}]}],
 "economy": {"currencies": [
  {"id": "score", "kind": "xp", "sources": ["merges"], "sinks": [], "cap": null}]}}
```

## 13. Tetris (mobile)

**Snapshot**
- Creator: Alexey Pajitnov (1984). Licensing is controlled by The Tetris Company.
- Mobile publishers: the mobile licence has changed hands several times. EA Mobile published Tetris apps for many years (they were delisted around 2020). N3TWORK took the mobile rights from EA in 2019 and released a new Tetris app in early 2020. In November 2021 PLAYSTUDIOS agreed with N3TWORK and The Tetris Company to take over the exclusive global mobile rights (excluding China), with an initial term running to August 2024 ([PLAYSTUDIOS press release](https://ir.playstudios.com/news-events/press-releases/detail/37/playstudios-secures-exclusive-rights-to-tetris-franchise); [SEC exhibit](https://www.sec.gov/Archives/edgar/data/1823878/000182387821000047/myps-11292021xex991.htm)). Whether the licence was extended past 2024 was not confirmed here: check the current store listing for the publisher before citing.
- Genre: falling-block puzzle. Business model: varies by licensee and era. Premium in the feature-phone era; later free with ads and optional purchases (verify the current app).

**Core loop**
1. A tetromino falls into a 10-wide matrix. Move, rotate, soft-drop or hard-drop it.
2. Lock it in place. Complete horizontal lines clear, and multi-line clears score more (four lines at once is a "Tetris").
3. The next-piece queue and the hold slot support planning.
4. Speed rises with level. The game ends when pieces stack out of the top.

**Meta and progression**: levels and score, marathon and sprint-style modes, and in modern licensed apps daily challenges, battle modes and cosmetic themes (verify per app).

**Economy**: score and level as `xp`. Licensed free-to-play versions add cosmetic or convenience currencies (verify).

**Monetization**: has ranged from premium purchase to ads with IAP for themes, ad removal or extra features, depending on licensee.

**Live-ops**: in modern apps, daily challenges, tournaments and battle or "royale" modes (verify the current set).

**Retention hooks**: mastery, high scores, sprint times, daily challenges, and the hypnotic "Tetris effect" flow state.

**Social layer**: leaderboards and competitive modes. The battle-royale reinterpretation (Tetris 99 on Nintendo Switch, 2019) showed how attacks (sending garbage lines) turn a solo puzzle into PvP.

**UX and onboarding notables: the touch-control problem**
- Virtual buttons are precise but cramped, and the thumbs cover the board.
- Gestures (drag to move, tap to rotate, swipe down to drop) are fluid, but risk mis-taps at speed.
- Target placement (tap where the piece should go, with the game routing it) is accessible, but it removes dexterity skill. Some licensed versions offered such a "one-touch" mode (verify).
- Most players are best served by offering two schemes and tuning delayed-auto-shift (DAS) and auto-repeat rate (ARR) equivalents for touch.

**Art and audio identity**: seven colour-coded tetrominoes and the "Korobeiniki" theme, plus the long tradition of rising tempo with level.

**Psychology principles used**: flow (Csikszentmihalyi), closure, the Zeigarnik effect (an incomplete stack demands resolution), and mastery through speed.

**Innovations (on mobile)**: the original's innovations predate mobile. Mobile adds control translation, short-session modes, and live features. The community-documented Tetris Guideline standardises modern play: the 7-bag randomiser, hold, ghost piece, hard drop, and SRS rotation with wall kicks. The Guideline document itself is confidential to licensees.

**Weaknesses and criticism**
- Touch controls are a perennial complaint from experienced players.
- Licence changes have repeatedly wiped out players' apps and progress (for example, the 2020 delisting of the EA versions).
- Monetization layered on a classic is often resented.

**Legal note**: in *Tetris Holding v. Xio Interactive* (US District Court, New Jersey, 2012), a close visual clone was found to infringe. Mechanics are generally treated as unprotectable ideas, but copying visual expression carries legal risk (`legal-ethics`).

**Lessons for designers**
1. When porting a precision game to touch, design the control scheme first and test it with real thumbs on a 6-inch screen.
2. Randomiser design is fairness design. A bag randomiser (each of the 7 pieces once per bag) prevents droughts, so consider the same idea for any random piece stream.
3. Licence-free descendants (1010!, Block Blast!) removed gravity and timers to reach a calmer mass audience. The same rule set suits different audiences depending on time pressure.
4. Protect players' progress across platform or licence transitions.

**Analogy hooks**
- The 7-bag randomiser → card shuffles, enemy spawn queues, match-3 refill pools.
- Garbage-line attacks → async puzzle PvP (word, block, match-3 duels).
- Hold slot → one-item reserve in any piece-stream game.

**Ontology encoding**
```json
{"loops": [
  {"id": "tet_core", "type": "core", "period": "seconds", "steps": [
    {"id": "c1", "action": "move_rotate_drop_tetromino", "reward": "placement", "next": "c2"},
    {"id": "c2", "action": "complete_lines", "reward": "clear_score_level_up", "next": "c3"},
    {"id": "c3", "action": "use_hold_and_next_queue", "reward": "planning_control", "next": "c1"}]}],
 "economy": {"currencies": [
  {"id": "score", "kind": "xp", "sources": ["line_clears"], "sinks": [], "cap": null}]}}
```

## 14. Royal Kingdom

**Snapshot**
- Developer: Dream Games (the Royal Match studio).
- Release: soft launch from April 2023, then global launch on 21 November 2024 on iOS and Android, a soft launch of about 19 months ([Wikipedia: Dream Games](https://en.wikipedia.org/wiki/Dream_Games); [PocketGamer.biz](https://www.pocketgamer.biz/dream-games-launches-royal-kingdom-worldwide-as-royal-match-nears-4-billion)).
- Genre: swap match-3 with a kingdom-building meta, set in the Royal Match universe. The protagonist is King Richard (the younger brother of Royal Match's King Robert), with Princess Bella and the Wizard, against the "Dark King" antagonist ([Mobidictum](https://mobidictum.com/royal-kingdom-launched-globally/); [Naavik](https://naavik.co/digest/royal-kingdom-and-expanding-the-royal-universe/)).
- Business model: free-to-play, IAP-led, expected to mirror Royal Match's single-currency approach (verify in-game).
- Note: this case covers strategy more than mechanics. Confirm board specifics in a play session before relying on them.

**Core loop (as observed in launch builds; verify)**
1. Tap into the next level from the kingdom screen.
2. Play a move-limited match-3 board with familiar specials, plus new obstacles and pieces.
3. A win earns progress resources and coins. A loss costs a life and offers a continue.
4. Spend progress on kingdom construction, which advances the story against the antagonist.

**Meta and progression**: a kingdom-construction and story-conflict framing replaces castle renovation. The aim is the same goal-gradient, wrapped in a building and "reclaim the land" fantasy rather than redecorating.

**Economy (expected structure; verify)**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Coins | hard | wins, chests, IAP | continues, boosters, lives |
| Build progress (stars or equivalent) | material | level wins | kingdom construction |
| Lives | energy | timed regen, team gifts | failed attempts |

**Monetization**: same family as Royal Match (coin packs, bundles, continues, pass). Verify any new offer types.

**Live-ops**: expect the Royal Match calendar architecture (competitions, team events, pass). Watch which events are new.

**Retention hooks**: construction completion bars, story conflict, streak-style bonuses and teams (verify).

**Social layer**: teams and competitive events, as in the parent title (verify).

**UX and onboarding notables**: the parent's frictionless one-tap-to-board UX and fast animations are expected. The new meta must be legible within the first session.

**Art and audio identity**: Royal Match's bright, comic royal style extended to a kingdom map, with a villain to give the meta narrative tension.

**Psychology principles used**: goal-gradient through construction, narrative conflict (an antagonist gives progress a direction), and the same loss-aversion and streak mechanics as the parent.

**Innovations**: not a new core. The strategic novelty is reframing the meta from renovation to construction and conflict while keeping a proven board feel. Whether new board mechanics are meaningful should be judged from play data, not marketing.

**Weaknesses and criticism (risks)**
- Cannibalization: the same audience may split time and spend between the two games.
- Novelty fatigue: players may see "the same game, different skin".
- Studio capacity: two live-ops calendars compete for the same team.

**The second-hit problem: comparables**

| Studio | First hit | Sibling | What changed | Read |
|---|---|---|---|---|
| King | Candy Crush Saga (2012) | Candy Crush Soda Saga (2014), Jelly Saga (2016) | New board mechanics (rising soda, spreading jelly) on the same brand | A brand family can hold several siblings |
| Playrix | Gardenscapes (2016) | Homescapes (2017) | The same formula moved from garden to house | Setting change was enough while the formula was new |
| Peak | Toy Blast (2015) | Toon Blast (2017) | Characters and polish on the same collapse core | The sibling overtook the original |
| Dream Games | Royal Match (2021) | Royal Kingdom (2024) | Meta reframed as construction and conflict | AppMagic reported about $301M in its first 12 months (grade B, [Outlook Respawn](https://respawn.outlookindia.com/gaming/gaming-guides/royal-kingdom-hits-300-million-in-year-one)), so the sibling did not stall; effects on the parent were not verified here |

**Lessons for designers**
1. Keep what players love (board feel, speed, economy legibility), and change the fantasy enough to justify a new install.
2. Decide up front whether the sibling must beat the parent's KPIs or only add incremental revenue. Write it into `kill_criteria`.
3. Plan cross-promotion and staffing: siblings fail more often from split live-ops capacity than from design.

**Analogy hooks**
- The "same chassis, new meta fantasy" playbook → any studio's second game (runner + different meta, merge + different story).
- An antagonist as meta motivation → idle and merge games that lack narrative tension.

**Ontology encoding**
```json
{"loops": [
  {"id": "rk_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "play_match3_level", "reward": "build_progress_and_coins", "next": "c2"},
    {"id": "c2", "action": "spend_progress_on_kingdom_construction", "reward": "kingdom_growth_story_beat", "next": "c3"},
    {"id": "c3", "action": "advance_against_antagonist", "reward": "new_area", "next": "c1"}]}],
 "economy": {"currencies": [
  {"id": "coins", "kind": "hard", "sources": ["level_win", "chests", "iap"], "sinks": ["continues", "boosters", "lives_refill"], "cap": null},
  {"id": "build_progress", "kind": "material", "sources": ["level_win"], "sinks": ["construction"], "cap": null},
  {"id": "lives", "kind": "energy", "sources": ["regen", "team_gifts"], "sinks": ["failed_attempt"], "cap": 5}]}}
```

## 15. Cross-case synthesis for puzzle and casual

### 15.1 Lineages (read these as evolution, not as a list)

```
Swap match-3:  Bejeweled (PopCap, 2001) → Candy Crush Saga (saga map, lives, fail offer, 2012)
               → Gardenscapes/Homescapes (renovation + story, 2016–17) → Royal Match (speed, one currency, streak, 2021)
               → Royal Kingdom (construction + antagonist meta, 2024)
Collapse:      SameGame-style puzzles → Toy Blast (2015) → Toon Blast (teams, 2017)
Connect:       Dots (2013) → Two Dots (levels, expeditions, 2014)
Block:         Tetris (1984) → 1010! (no gravity, 2014) → Woodoku/Blockudoku (Sudoku grid) → Block Blast! (juice + ad scale)
Buffer/triple: Mahjong solitaire → tile-tray triples → 3D object triples → screw sort (physics reveal)
Sort:          ball sort / water sort (c. 2020) → Magic Sort! (hidden layers, polish)
Number:        Threes! (2014) → 1024 / 2048 clones (2014) → merge-number descendants
```

### 15.2 Archetype decision table

| Archetype | Monetization fit | Content cost | Verifiability | Typical audience | Cases |
|---|---|---|---|---|---|
| Swap match-3 + renovation | IAP (continues, boosters, lives) | Very high (levels + meta art) | High (`match3_sim.py`) | Adults 25–55, broad | 1, 2, 3, 14 |
| Collapse / blast | IAP | High | High (`match3_sim.py` with a blast rule) | Broad, lower skill floor | 4 |
| Block puzzle | Ads (long sessions) | Very low (systemic) | High (bots) | Very broad, older-skewing | 5, 13 |
| Word | Hybrid (hints + ads) | Medium (generated grids + dictionary QA) | High (dictionary solver) | Adults, older-skewing | 6 |
| Triple / buffer | Hybrid (continues) | Medium (item sets, generated heaps) | Medium (solver with occlusion) | Broad casual | 8, 10 |
| Sort | Ads (stuck moment) | Low (generated) | Very high (`puzzle_solver.py` sort) | Broad casual | 9 |
| Physics puzzle | Premium or IAP hints | High (handcrafted levels) | Medium (physics sims) | Broad, younger-skewing | 11 |

### 15.3 Where each game places its spend moment

| Moment | Example | Ethical guardrail |
|---|---|---|
| Near-miss continue | Candy Crush, Royal Match, Toon Blast (+moves) | Show the real remaining objective; never fabricate near-misses; cap continues per level |
| Stuck state | Water sort (extra tube), screw (extra slot) | Always offer free undo or restart |
| Search fatigue | Wordscapes (hints) | Keep free tools (shuffle) that solve most blocks |
| Buffer overflow | Triple-match (extra slot) | Guarantee solvable levels without purchase |
| Absence | Lives timers (all IAP match-3s) | Keep lives generous at launch; no energy in ad-led puzzles |

### 15.4 Difficulty knobs by archetype (tune with bots, record in `level-spec.schema.json` documents)

| Archetype | Primary knobs | Secondary knobs |
|---|---|---|
| Swap match-3 | moves, number of colours, blocker layers | spawn weights, goal counts, special-creation opportunities |
| Collapse | colours, minimum group size, special thresholds | refill bias, obstacle density |
| Block | piece-mix weights, grid size | "guarantee a fit" rule, combo windows |
| Triple | tray slots, item types per level, timer | occlusion depth, duplicates per type |
| Sort | colours C, capacity K, empty tubes E | undo budget, hidden layers |
| Screw | holding slots, box colour sequence | plate layering, screw count per colour |
| Word | letters on wheel, grid words, dictionary breadth | bonus-word density |

### 15.5 Before you clone a puzzle hit: checklist
- [ ] Name the chassis you are keeping and the one or two things you are changing. Write them in `contract.meta.comparables` as `borrow` and `change`.
- [ ] Prove the level pipeline: an editor or generator plus a solver or bot, with 20 verified levels, before art production.
- [ ] Choose the spend moment and its guardrail from 15.3.
- [ ] Check readability on a low-end 6-inch phone: silhouettes, colour-blind mode, thumb occlusion (drag offset).
- [ ] Decide energy or no energy from the monetization model, not from habit.
- [ ] Plan the meta (renovation, construction, collection, story) and budget its art.
- [ ] Make sure your ad creatives show your real game.

## 16. Volatile facts (as of Oct 2026 — verify before relying)

- [V1] Block Blast! topped worldwide game downloads in H1 2026. In the same period mobile game IAP was about $40B (−2% YoY) and downloads about 24B (−12%). Source: [Mobilegamer.biz data digest of Sensor Tower H1 2026](https://mobilegamer.biz/data-digest-sensor-towers-h1-analysis-hay-days-comeback-julys-top-games-big-krafton-numbers-and-more/).
- [V2] King's human-like playtesting bot (a CNN trained on player moves) predicted difficulty and had been in use for more than a year across more than 1,000 new Candy Crush Saga levels. Source: [Gudmundsson et al., 2018 (King)](https://gwern.net/doc/reinforcement-learning/imitation-learning/2018-gudmundsson.pdf).
- [V3] Follow-up work with King: difficulty estimates in under a minute, versus 7 days of human playtesting per 15-level episode. Simulating several player strategies improved error (MAE about 13% better). Source: [Politecnico di Milano thesis](https://www.politesi.polimi.it/handle/10589/141799).
- [V4] King AI Labs (2024) described a bot that automatically adjusts levels designers flag, against set criteria, with designers reviewing the best solutions. Source: [WN Hub, June 2024](https://wnhub.io/news/Generative_AI/item-43934).
- [V5] Hybrid-casual spending grew 17.1% in 2025 ($3.5B → $4.2B), which pushes puzzle games toward deeper metas. Source: [Mobilegamer.biz (Sensor Tower)](https://mobilegamer.biz/data-digest-sensor-towers-h1-analysis-hay-days-comeback-julys-top-games-big-krafton-numbers-and-more/).
- [V6] Mobile game IAP in 2025 was about $82B (+1%), a flat market that rewards retention-led puzzle designs. Source: [Sensor Tower State of Gaming 2026](https://sensortower.com/press/press-release-sensor-tower-state-of-gaming-gaming-drove-52-billion-downloads-82b-iap-revenue-on-mobile-and-12b-premium-revenue-on-steam).
- [V7] Checked on 2026-10-20. App Store listing metadata (seller, developer name, first release date) read through Apple's iTunes Search API: Magic Sort! (Grand Games A.Ş., 28 May 2024), Screw Jam (Rollic Games, 8 December 2023), Block Blast! (Hungry Studio, seller Aretis Limited, 3 April 2022). Sources: [Magic Sort!](https://itunes.apple.com/search?term=magic+sort&entity=software&country=us&limit=6), [Screw Jam](https://itunes.apple.com/search?term=screw+jam&entity=software&country=us&limit=8), [Block Blast!](https://itunes.apple.com/search?term=block+blast&entity=software&country=us&limit=6). Royal Kingdom dates and cast: [PocketGamer.biz](https://www.pocketgamer.biz/dream-games-launches-royal-kingdom-worldwide-as-royal-match-nears-4-billion), [Wikipedia: Dream Games](https://en.wikipedia.org/wiki/Dream_Games). Tetris mobile licence: [PLAYSTUDIOS](https://ir.playstudios.com/news-events/press-releases/detail/37/playstudios-secures-exclusive-rights-to-tetris-franchise).
- Ownership and event names (Microsoft–Activision 2023, Take-Two–Zynga 2022, Royal Match event names) are widely reported but change. A Savvy Games Group transaction involving Dream Games could not be confirmed in this review. Verify before quoting any of these in external documents.
