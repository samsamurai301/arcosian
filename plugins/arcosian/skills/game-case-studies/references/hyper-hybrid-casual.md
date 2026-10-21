# Hyper-casual and hybrid-casual case studies

Fourteen deconstructions of games with instantly readable cores. They run from the premium-era touch arcade hits (Angry Birds, Fruit Ninja, Temple Run), through the viral and ad-funded hyper-casual wave (Flappy Bird, Helix Jump, Hole.io, Paper.io 2, Count Masters), to the hybrid-casual model that bolts a free-to-play meta onto a hyper-casual core (Archero, Survivor.io), and the premium indie that founded a subgenre (Vampire Survivors). One question connects them: how much depth can sit behind a verb a player understands from a 3-second ad? The cases show the answer moving over time. Hyper-casual monetized pure attention with ads. When ad targeting and installs got more expensive, studios added gear, upgrades and passes to raise lifetime value. Each case uses the 16-lens format from `SKILL.md` and ends with an ontology encoding in contract field names. Mechanics are described as publicly observable in the shipped games. Uncertain or frequently changing details are marked "verify", and revenue figures are omitted unless they were widely reported, in which case they are labelled approximate. Volatile market facts are in section 16.

**Contents.** Sections 1–14 are case studies (index below). Section 15 covers the hyper-casual to hybrid-casual economics and a design recipe. Section 16 lists volatile facts with sources.

| # | Game | Genre | Year | Key lesson |
|---|---|---|---|---|
| 1 | Flappy Bird | one-button arcade (proto-hypercasual) | 2013 | Instant retry makes brutal difficulty shareable; virality is not a plan |
| 2 | Crossy Road | endless hopper | 2014 | Opt-in rewarded video plus cosmetic collection builds goodwill and revenue |
| 3 | Helix Jump | hypercasual, one gesture | 2018 | Readable in 3 seconds; the prototype-and-test factory model |
| 4 | Hole.io | io, hypercasual | 2018 | Grow-to-eat escalation compresses a power fantasy into 2 minutes |
| 5 | Subway Surfers | endless runner | 2012 | A rotating "World Tour" turns a finite runner into a live service |
| 6 | Temple Run | endless runner | 2011 | A swipe-native 3D runner with a chase fantasy; the free-to-play switch |
| 7 | Fruit Ninja | touch-native arcade | 2010 | Juice the verb; give each motivation its own mode |
| 8 | Angry Birds | physics puzzle | 2009 | Readable physics plus characters plus 3 stars; a brand beyond the app |
| 9 | Stumble Guys | party royale | 2020 | Fast-follow a platform trend onto mobile; fill lobbies reliably |
| 10 | Archero | roguelite action, hybrid-casual | 2019 | Stop-to-shoot, run skills and persistent gear: the hybrid-casual template |
| 11 | Survivor.io | survivor-like, hybrid-casual | 2022 | Premium-indie rules plus a free-to-play gear meta, in portrait |
| 12 | Vampire Survivors | survivor-like (bullet heaven) | 2021–22 | Invert the shooter; evolution recipes; fair mobile monetization |
| 13 | Count Masters | crowd runner | 2021 | Arithmetic gates as a choice mechanic; the crowd is the health bar |
| 14 | Paper.io 2 | io territory | 2018 | Risk grows with reward: the loop-to-capture territory mechanic |

---

## 1. Flappy Bird

**Snapshot**
- Developer: Dong Nguyen (.GEARS Studios, Vietnam).
- Release: iOS on 24 May 2013 and Android on 30 January 2014. It went viral in January–February 2014, and the creator announced on 8 February that he would take it down and removed it from the stores on 10 February 2014 ([Wikipedia: Flappy Bird](https://en.wikipedia.org/wiki/Flappy_Bird)).
- Genre: one-button arcade (hyper-casual before the term existed). Business model: free with ads.
- Scale: The Verge (Ellis Hamburger, 5 February 2014) reported Nguyen saying the game was "earning around $50,000 a day in revenue through its in-game advertising". This is a developer claim, not audited revenue (cited through [Wikipedia: Flappy Bird](https://en.wikipedia.org/wiki/Flappy_Bird); The Verge article itself was not retrievable in this review).

**Core loop**
1. Tap to flap. Each tap gives a fixed upward impulse, and gravity pulls the bird down continuously.
2. Fly through the gap between pipe pairs that scroll in at a constant speed.
3. Each pipe passed scores +1.
4. Any collision ends the run. The result screen shows the score, best score and medal.
5. Restart in about a second.

**Meta and progression**: best score and medals (bronze, silver, gold, platinum at 10, 20, 30 and 40 points). There is nothing else.

**Economy**: none. Score is `xp`-like status.

**Monetization**: banner and interstitial-style ads (verify the exact formats in the original build). There was no IAP.

**Live-ops**: none.

**Retention hooks**: the high-score chase, "just one more" instant retries, and social bragging and complaining.

**Social layer**
- Organic virality through memes, reaction videos and word of mouth, plus Game Center leaderboards.
- No paid user acquisition is documented as the driver.

**UX and onboarding notables**
- A one-frame tutorial (a tap icon), a pre-start hover so the player chooses when to begin, and near-zero time from death to retry.
- The hitboxes are tight, so the game feels unforgiving.

**Art and audio identity**: retro pixel art with pipes reminiscent of classic platformers (some called it derivative), and three or four SFX (flap, point, hit, swoosh).

**Psychology principles used**
- Frustration, then competence: tiny measurable improvements feel big.
- Near-miss and variable outcome on very short trials.
- Social proof and shareable suffering.
- Commitment: restarting is effortless, so continuing never feels like a decision.

**Innovations**: no new mechanic (helicopter-style one-button games predate it). It demonstrated that extreme difficulty, zero friction and the social media of its moment can produce organic virality without paid acquisition.

**Weaknesses and criticism**
- No retention or monetization depth beyond ads.
- The creator cited the game's addictive nature and the personal pressure of its sudden fame when he removed it.
- A flood of clones followed, and the stores reportedly began rejecting new "Flappy" titles.
- In January 2024 the Flappy Bird trademark was terminated and passed to Gametech Holdings, which announced an unofficial reboot ("The Flappy Bird Foundation") in September 2024. Nguyen said he has no connection with it ([Wikipedia: Flappy Bird](https://en.wikipedia.org/wiki/Flappy_Bird)).

**Lessons for designers**
1. Difficulty is a feature only when failure is instant, legible and fair, and retry costs under 2 seconds.
2. The whole game is five tuning parameters: gravity, flap impulse, scroll speed, gap height and pipe spacing. Expose them in `contract.mechanics[].parameters` and tune them with recorded playtests.
3. Do not plan around virality. Plan the systems that retain the players virality brings.
4. Medal thresholds turn a raw score into goals.

**Analogy hooks**
- One-button impulse control → rhythm games, lane-swap runners, golf power meters.
- Instant retry → every skill game, including roguelites (the quick-restart button).
- Medal thresholds → any score-attack mode.

**Ontology encoding**
```json
{"loops": [
  {"id": "fb_core", "type": "core", "period": "seconds", "steps": [
    {"id": "c1", "action": "tap_to_flap", "reward": "altitude_control", "next": "c2"},
    {"id": "c2", "action": "pass_pipe_gap", "reward": "plus_one_score", "next": "c3"},
    {"id": "c3", "action": "collide_and_die", "reward": "score_best_medal_screen", "next": "c4"},
    {"id": "c4", "action": "instant_restart", "reward": "new_attempt", "next": "c1"}]}],
 "economy": {"currencies": [
  {"id": "score", "kind": "xp", "sources": ["pipes_passed"], "sinks": [], "cap": null}]}}
```

## 2. Crossy Road

**Snapshot**
- Developer: Hipster Whale (Melbourne; Matt Hall and Andy Sum).
- Release: iOS on 20 November 2014 and Android on 23 December 2014. Spin-offs followed, including Disney Crossy Road (2016) and Crossy Road Castle (Apple Arcade).
- Genre: endless hopper (a "Frogger"-style crossing game made endless). Business model: free, with opt-in rewarded video ads and IAP for characters.
- Scale: Polygon (Dave Tach, 3 March 2015, "They wanted to make a video game phenomenon. They made $10 million. The story of Crossy Road.") reported that the game earned over $10M and passed 50 million downloads within three months of release (cited through [Wikipedia: Crossy Road](https://en.wikipedia.org/wiki/Crossy_Road); the Polygon article itself was not retrieved). Treat it as a reported figure.

**Core loop**
1. Tap to hop forward. Swipe to hop sideways or back.
2. Cross procedurally generated strips of roads, rivers (ride logs and lily pads) and railways.
3. Collect coins along the way.
4. Die from a vehicle, the water, or the eagle, which grabs players who idle too long or retreat too far.
5. The score is the furthest row reached. Restart at once.

**Meta and progression**: a large collection of characters, many with unique worlds, music or visual themes, and secret characters unlocked by special actions.

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Coins | soft | in-run pickups, periodic free gifts, opt-in rewarded videos, milestone rewards | prize machine (100 coins = one random character) |
| Characters | material | prize machine, direct IAP, secret unlocks | none (collection) |

**Monetization**
- Opt-in rewarded videos for coins, with no forced interstitials in the original design as widely described.
- Direct purchase of specific characters at low price tiers.
- The model was frequently cited as a "player-friendly" benchmark.

**Live-ops**: character packs and themed updates, plus seasonal or licensed characters (verify cadence).

**Retention hooks**: periodic free-gift timers (appointments), the next prize-machine pull, completing the collection, and secret-character discovery.

**Social layer**: leaderboards and score sharing. Characters work as social currency ("did you find X?").

**UX and onboarding notables**
- A one-tap start, and the camera's forward drift adds gentle pressure.
- The eagle mechanic stops players from camping or farming safely, keeping runs tense.

**Art and audio identity**: voxel art with crisp, readable silhouettes, a bright palette, and per-character audio and visual themes that make collection feel substantive.

**Psychology principles used**
- Variable reward from the prize machine: a random character, cosmetic only.
- Collection completion and endowment.
- Curiosity from secret characters (Loewenstein).
- Reciprocity: generous free gifts build goodwill (Cialdini).

**Innovations**
- Popularised opt-in rewarded video as a primary mobile monetization tool.
- Paired an endless arcade core with a deep cosmetic collection that changes the experience (worlds and sound), not just the skin.

**Weaknesses and criticism**
- Shallow long-term progression, since cosmetics do not change mechanics.
- Spawned many voxel hopper clones.
- Revenue per user is lower than in IAP-heavy designs.

**Lessons for designers**
1. Rewarded ads work best when they are optional, generous and placed at moments of desire (the prize machine), not frustration.
2. Make cosmetics transform the experience (music, environment) so the collection feels like content.
3. Add an anti-stalling rule (the eagle) to any game where safe idling kills tension.
4. Secret unlocks create community conversation for free.

**Analogy hooks**
- A cosmetic prize machine with no power → any game with a non-competitive cosmetic economy (puzzle themes, golf balls).
- The eagle as an anti-camping rule → shrinking zones in battle royales, timers in idle-prone action games.
- Characters that re-theme worlds → runner skins, puzzle board themes.

**Ontology encoding**
```json
{"loops": [
  {"id": "cr_core", "type": "core", "period": "seconds", "steps": [
    {"id": "c1", "action": "tap_to_hop_forward", "reward": "row_progress", "next": "c2"},
    {"id": "c2", "action": "time_crossings_collect_coins", "reward": "coins", "next": "c3"},
    {"id": "c3", "action": "die_or_eagle_grab", "reward": "score_screen", "next": "c1"}]},
  {"id": "cr_meta", "type": "monetization", "period": "session", "steps": [
    {"id": "m1", "action": "watch_optional_video_or_claim_gift", "reward": "coins", "next": "m2"},
    {"id": "m2", "action": "spend_100_coins_on_prize_machine", "reward": "random_character", "next": "m3"},
    {"id": "m3", "action": "play_with_new_character_world", "reward": "novelty", "next": "m1"}]}],
 "economy": {"currencies": [
  {"id": "coins", "kind": "soft", "sources": ["run_pickups", "free_gift_timer", "rewarded_video"], "sinks": ["prize_machine"], "cap": null},
  {"id": "characters", "kind": "material", "sources": ["prize_machine", "iap", "secret_unlock"], "sinks": [], "cap": null}]}}
```

## 3. Helix Jump

**Snapshot**
- Publisher: Voodoo (Paris), the archetypal hyper-casual publisher (verify the original developer credit).
- Release: 2018.
- Genre: one-gesture hyper-casual. Business model: ad-led (interstitials between levels, rewarded continues) with light IAP (ad removal, skins).
- Scale: one of the most downloaded mobile games of its year by widely reported store-intelligence rankings (figures omitted).

**Core loop**
1. The ball bounces automatically on a platform of a helix tower.
2. Drag horizontally to rotate the tower so that a gap lines up under the ball.
3. Fall through gaps and avoid the coloured danger segments.
4. Falling through several platforms without touching one charges a "smash" state that breaks the next platform, danger segments included.
5. Reach the bottom to finish the level. Hitting a danger segment ends the run, with a rewarded-continue offer.

**Meta and progression**: numbered levels with a progress bar, score combos, and unlockable ball and visual skins.

**Economy**: minimal. Score is `xp`; skins come from progress or ads.

**Monetization**: interstitials paced by level completion and time, rewarded "second chance", and ad removal.

**Live-ops**: none of note. A typical hyper-casual "launch, scale, decline" life cycle.

**Retention hooks**: the next level number, beating the best score, and very short levels.

**Social layer**: none.

**UX and onboarding notables**
- The rule is understood from the first second of a video ad. That readability is the selection criterion for hyper-casual concepts.
- No menus: the game starts on touch.
- The progress bar shows how close the bottom is (goal-gradient).

**Art and audio identity**: solid-colour minimalism, a high-contrast ball against the tower, glossy smash effects and haptics.

**Psychology principles used**: goal-gradient (the progress bar), flow from continuous control, and the near-miss of a gap just missed. A risk/reward choice whether to fall through fast and charge the smash, or play safe.

**Innovations**: not deep. It is representative of the hyper-casual production model:
- Test a concept's marketability (cost per install from video creatives) before full production.
- Ship fast.
- Fund user acquisition with ad revenue as long as lifetime value exceeds cost per install.

**Weaknesses and criticism**
- Low retention and no depth.
- Ad load that players dislike.
- Easy to clone.
- The business model relied on cheap installs and ad targeting, which weakened later (section 15).

**Lessons for designers**
1. The 3-second readability test: if a stranger cannot state the rule from a muted 3-second clip, the concept fails as hyper-casual.
2. One continuous gesture (drag to rotate) beats discrete taps for flow.
3. Build a risk/reward choice into a single gesture (the fast smash versus a safe fall).
4. Run marketability tests before building more than a prototype (`marketing-ua`).

**Analogy hooks**
- Rotate-the-world-not-the-avatar → maze tilt puzzles, rotating-planet runners.
- A smash charged by streaks → any momentum mechanic (combo breakers in runners, drift boosts).
- A progress bar on short levels → all level-based casual games.

**Ontology encoding**
```json
{"loops": [
  {"id": "hj_core", "type": "core", "period": "seconds", "steps": [
    {"id": "c1", "action": "drag_to_rotate_tower", "reward": "gap_alignment", "next": "c2"},
    {"id": "c2", "action": "fall_through_platforms", "reward": "score_and_smash_charge", "next": "c3"},
    {"id": "c3", "action": "reach_bottom_or_hit_danger", "reward": "level_complete_or_continue_offer", "next": "c1"}]}],
 "economy": {"currencies": [
  {"id": "score", "kind": "xp", "sources": ["platforms_passed", "combos"], "sinks": [], "cap": null}]}}
```

## 4. Hole.io

**Snapshot**
- Publisher: Voodoo.
- Release: 2018.
- Genre: io-style arena with a "black hole" avatar. Business model: ad-led (interstitials, rewarded) with skins.
- Context: Ben Esposito, developer of the long-in-development Donut County (also 2018), publicly criticised Hole.io's similarity to his game.

**Core loop**
1. Drag to steer a hole through a city.
2. Swallow objects smaller than the hole's opening: cones, people, cars and, eventually, buildings.
3. Grow as you swallow, and bigger objects become edible.
4. Swallow smaller rival holes, and avoid bigger ones.
5. A round lasts about two minutes and ends with a size or score ranking.
- Modes include classic (biggest at the end), battle (last hole standing) and solo (eat a share of the city in time) (verify the current modes).

**Meta and progression**: skins and nicknames, and level-ups between rounds (verify).

**Economy**: score/size is `xp`. Skins come from progress or ads.

**Monetization**: interstitials between rounds, rewarded ads for skins or boosts, and ad removal.

**Live-ops**: none of note.

**Retention hooks**: short rounds, the escalation fantasy of "eat the city", and beating your best rank.

**Social layer**: io framing with named rivals. Opponents in many io-style mobile games are bots filling rounds, so verify any claim of real multiplayer.

**UX and onboarding notables**: a single drag, an instantly clear rule (small things fall in), and visible growth thresholds as objects that were too big become edible.

**Art and audio identity**: low-poly city, satisfying "fall-in" physics, and size-up pops.

**Psychology principles used**
- Escalating power fantasy and competence.
- Size thresholds as a goal-gradient.
- Social comparison on the ranking.
- Risk and avoidance against bigger rivals.

**Innovations**: compressed the "grow by eating" io fantasy (the Agar.io lineage) into a tactile 3D physics toy with a city as the food source.

**Weaknesses and criticism**
- Accusations of copying Donut County's core idea.
- Shallow.
- Players feel misled when "online" rivals are bots.

**Lessons for designers**
1. Escalation within a single round (eat cones, then cars, then towers) gives a 2-minute session a full arc.
2. Physics "fall-in" feedback sells the fantasy more than particles do.
3. Be honest about bots. Label practice or bot modes where it matters to players.
4. Check for prior art before shipping a concept that mirrors a known indie project in development. The reputational cost is real.

**Analogy hooks**
- A size-gated food chain → snake games, katamari-likes, fish-eat-fish, idle growth.
- In-round escalation → survivor-likes, tower defense waves, merge sprints.
- City as consumable environment → destruction toys, cleanup sims.

**Ontology encoding**
```json
{"loops": [
  {"id": "ho_core", "type": "core", "period": "seconds", "steps": [
    {"id": "c1", "action": "steer_hole", "reward": "positioning", "next": "c2"},
    {"id": "c2", "action": "swallow_smaller_objects", "reward": "growth", "next": "c3"},
    {"id": "c3", "action": "eat_smaller_rivals_avoid_larger", "reward": "rank_gain", "next": "c4"},
    {"id": "c4", "action": "round_timer_ends", "reward": "ranking_screen", "next": "c1"}]}],
 "economy": {"currencies": [
  {"id": "size_score", "kind": "xp", "sources": ["objects_swallowed", "rivals_swallowed"], "sinks": [], "cap": null}]}}
```

## 5. Subway Surfers

**Snapshot**
- Developer: SYBO (Copenhagen), co-developed with Kiloo at launch. Kiloo published it until February 2020, when SYBO took over publishing. Miniclip's acquisition of SYBO was reported by VentureBeat on 24 June 2022 ([Wikipedia: Subway Surfers](https://en.wikipedia.org/wiki/Subway_Surfers) cites the report; closing details were not checked).
- Release: 24 May 2012.
- Genre: three-lane endless runner. Business model: free-to-play hybrid. IAP (keys, coins, characters, boards) and rewarded ads.
- Scale: it passed one billion downloads on Google Play in March 2018, described as a first for that store, and two billion by May 2018 ([Wikipedia: Subway Surfers](https://en.wikipedia.org/wiki/Subway_Surfers)).

**Core loop**
1. Run automatically down train tracks, chased by an inspector and his dog.
2. Swipe left or right to change lane, up to jump, down to roll.
3. Collect coins and power-ups: jetpack, super sneakers, coin magnet, score multiplier.
4. Activate a hoverboard (double-tap) to survive one crash for a limited time.
5. Crash: pay keys to continue (the cost escalates within a run) or end the run. The score converts to progress on missions and other goals.

**Meta and progression**
- Mission sets that permanently raise the score multiplier (up to a high cap, ×30 in long-standing builds; verify).
- Characters and hoverboards with abilities, power-up upgrades bought with coins, and Mystery Boxes.

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Coins | soft | in-run pickups, boxes, daily rewards, rewarded ads | power-up upgrades, hoverboards, boxes, characters |
| Keys | hard | rare pickups, daily challenges, hunts, IAP, ads | revives (escalating), event items |
| Hunt tokens (seasonal) | event | in-run pickups during a season | season rewards |

**Monetization**: key and coin packs, characters and boards, a season pass in modern builds (verify), and rewarded ads for doubled rewards or free keys.

**Live-ops**
- **World Tour**: the run's city setting rotates every few weeks with new visuals, characters, boards and a seasonal token hunt.
- Daily challenges (for example, collect letters to spell a word) and weekly hunts.

**Retention hooks**: the next World Tour city (a visible content clock), daily word challenges, mission-set multiplier growth, and seasonal hunts.

**Social layer**: friend leaderboards and score beating (verify the current social features).

**UX and onboarding notables**
- A first-run tutorial teaches the four swipes in context, and failure in the tutorial costs nothing.
- Readable lanes and obstacle silhouettes at speed: jump-over versus roll-under obstacles are visually distinct.

**Art and audio identity**: bright, saturated, cartoony street-art style, graffiti-culture theming, and an energetic recurring theme.

**Psychology principles used**
- Flow from rising speed.
- Goal-gradient on mission sets.
- Novelty and curiosity from the city rotation.
- Loss aversion at the revive prompt.
- Collection completion.

**Innovations**: the World Tour relocation was an early, highly visible live-ops pattern for a runner: periodic re-theming that refreshes a finite core without changing its rules.

**Weaknesses and criticism**
- The core has barely changed in over a decade, so long-term players depend on cosmetic novelty.
- Escalating revive costs pressure spending.
- The runner genre has saturated.

**Lessons for designers**
1. Re-theming on a fixed clock is a cheap, powerful live-ops tool for systemic cores. Budget art for it.
2. Permanent meta multipliers turn every run into account progress.
3. Make the obstacle silhouette encode the required action (jump or roll) for readability at speed.
4. Escalating revive pricing needs a per-run cap, for both ethics and goodwill.

**Analogy hooks**
- World Tour → puzzle seasonal worlds, idle-game seasonal maps, battle-royale map rotations.
- Mission sets raising a permanent multiplier → any score game (golf, arcade, rhythm).
- Spell-a-word daily challenge → letter pickups in any collection loop.

**Ontology encoding**
```json
{"loops": [
  {"id": "ss_core", "type": "core", "period": "seconds", "steps": [
    {"id": "c1", "action": "swipe_lane_jump_roll", "reward": "survival_and_coins", "next": "c2"},
    {"id": "c2", "action": "use_powerups_or_hoverboard", "reward": "score_burst_or_crash_shield", "next": "c3"},
    {"id": "c3", "action": "crash_then_revive_with_keys_or_end", "reward": "continue_or_score", "next": "c1"}]},
  {"id": "ss_liveops", "type": "liveops", "period": "season", "steps": [
    {"id": "l1", "action": "enter_new_world_tour_city", "reward": "new_theme_characters", "next": "l2"},
    {"id": "l2", "action": "collect_season_hunt_tokens", "reward": "season_rewards", "next": "l1"}]}],
 "economy": {"currencies": [
  {"id": "coins", "kind": "soft", "sources": ["run_pickups", "boxes", "daily", "rewarded_ad"], "sinks": ["powerup_upgrades", "boards", "characters"], "cap": null},
  {"id": "keys", "kind": "hard", "sources": ["rare_pickups", "challenges", "iap", "rewarded_ad"], "sinks": ["revive"], "cap": null},
  {"id": "hunt_tokens", "kind": "event", "sources": ["season_pickups"], "sinks": ["season_rewards"], "cap": null}]}}
```

## 6. Temple Run

**Snapshot**
- Developer: Imangi Studios (Keith Shepherd and Natalia Luckyanova).
- Release: 2011 on iOS. It launched as a paid app and moved to free-to-play within months. Its rise to the top of the charts followed the switch (widely reported).
- Genre: third-person 3D endless runner. Business model: free-to-play with IAP (coins, gems) after the switch.
- Follow-ups: Temple Run 2 (2013) and Disney licence spin-offs (Brave, Oz).

**Core loop**
1. Run automatically along a temple path, chased by demon monkeys.
2. Swipe left or right to turn at junctions, up to jump, down to slide.
3. Tilt the phone to drift sideways and collect coins.
4. Grab power-ups (coin magnet, invisibility, speed boost).
5. Die on an obstacle, a missed turn or a fall. In later versions, revive with gems at an escalating cost. The run's distance and coins feed progress.

**Meta and progression**: objectives (achievement-style tasks) that track mastery, power-up upgrades, and unlockable characters (verify the current objective system).

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Coins | soft | in-run pickups, IAP | power-up upgrades, characters |
| Gems (later versions) | hard | rare pickups, IAP | revives, premium unlocks |

**Monetization**: coin packs and doublers, character unlocks, and gem-priced revives (later versions).

**Live-ops**: limited in the original. Later versions added maps, events and themed content (verify).

**Retention hooks**: objectives, upgrade goals, and the chase fantasy's tension.

**Social layer**: Game Center leaderboards and score sharing.

**UX and onboarding notables**
- Turning at corners by swipe was the key touch-native insight: the swipe direction matches the path direction.
- Tilt is a secondary input for optional coins, so missing it never kills the player.

**Art and audio identity**: jungle temple adventure aesthetic (pulp-adventure homage), pursuing monkeys with audible growls behind you, and rising tension through speed.

**Psychology principles used**: the chase as arousal (threat behind you), flow from rising speed, competence through objectives, and loss aversion at the revive.

**Innovations**
- Popularised the 3D third-person endless runner with swipe-to-turn controls and a pursuer, a template that Subway Surfers and many others followed.
- An early showcase of the paid-to-free switch unlocking scale.

**Weaknesses and criticism**
- Repetitive. The original's progression was thin.
- Later gem revives drew pay-to-continue criticism.
- Licence spin-offs diluted the brand.

**Lessons for designers**
1. Map the gesture to the world: swipe in the direction the avatar should go.
2. Primary input should be fatal, secondary input optional (tilt for coins). Never make a secondary input mandatory.
3. A visible pursuer turns speed into story.
4. Price tests matter: the same game can fail paid and win free-to-play, or the reverse (see `references/premium-indie.md` for premium successes).

**Analogy hooks**
- A pursuer behind the player → survival games (closing storm), roguelites (a timer monster), puzzles (a rising-water timer).
- Swipe-to-turn → tunnel and racing games, maze runners.
- Optional tilt bonus → secondary skill layers in casual games.

**Ontology encoding**
```json
{"loops": [
  {"id": "tr_core", "type": "core", "period": "seconds", "steps": [
    {"id": "c1", "action": "swipe_turn_jump_slide", "reward": "survival", "next": "c2"},
    {"id": "c2", "action": "tilt_to_collect_coins", "reward": "coins", "next": "c3"},
    {"id": "c3", "action": "die_then_revive_or_end", "reward": "distance_score", "next": "c4"},
    {"id": "c4", "action": "spend_coins_on_upgrades", "reward": "stronger_powerups", "next": "c1"}]}],
 "economy": {"currencies": [
  {"id": "coins", "kind": "soft", "sources": ["run_pickups", "iap"], "sinks": ["powerup_upgrades", "characters"], "cap": null},
  {"id": "gems", "kind": "hard", "sources": ["rare_pickups", "iap"], "sinks": ["revive"], "cap": null}]}}
```

## 7. Fruit Ninja

**Snapshot**
- Developer: Halfbrick Studios (Brisbane).
- Release: 2010 on iOS as a paid app. Free editions, sequels (Fruit Ninja 2, 2019–20) and platform versions (Kinect) followed.
- Genre: touch-native arcade. Business model: paid at launch. Later editions are free-to-play with currencies and ads (verify per edition).

**Core loop**
1. Fruit is tossed up from the bottom of the screen.
2. Swipe to slice it. Slicing three or more fruits in one swipe scores a combo, and critical hits occur randomly.
3. Avoid bombs: in Classic a bomb ends the game. Missed fruit counts as strikes, and three strikes end the game.
4. The game-over screen shows the score and best score. Retry at once.
- Modes:
  - Classic: strikes and bombs.
  - Zen: 90 seconds, no bombs.
  - Arcade: 60 seconds, with bonus bananas (frenzy, double score, freeze) and a pomegranate finale.

**Meta and progression**: best scores per mode, achievements, unlockable blades and dojo backgrounds, and a sensei character who dispenses fruit-themed wisdom (verify the current content).

**Economy (later free editions)**: an earnable currency (starfruit in some editions) for blades, dojos and power-ups (verify). The paid original had no currency.

**Monetization**: paid at launch. Free editions use ads and IAP for cosmetics and power-ups (verify).

**Live-ops**: limited in the original. Later editions add events (verify).

**Retention hooks**: score mastery per mode, cosmetic unlocks, and very short sessions.

**Social layer**: Game Center leaderboards, and local multiplayer in some versions.

**UX and onboarding notables**
- Slice a fruit to start: the main menu items are themselves fruits, which teaches the verb before the first game.
- The swipe trail visualises the input.

**Art and audio identity**
- Juicy splatter, slow-motion criticals, wood-grain dojo, and crisp slicing SFX.
- The juice *is* the reward. It is a canonical "game feel" example (`game-feel`).

**Psychology principles used**: sensory reward and juice, competence via combos, variable reward from criticals, and modes that match motivation (challenge, relaxation, score attack).

**Innovations**
- One of the first hits built entirely on the capacitive multi-touch swipe: a verb impossible with buttons.
- Menus that use the core verb as navigation.

**Weaknesses and criticism**
- A shallow long-term meta.
- Later free-to-play editions added monetization that some original fans disliked.
- Clone-heavy.

**Lessons for designers**
1. Design around a verb the platform makes uniquely good: swiping on glass.
2. Spend production on the feedback of the single verb (splatter, sound, slow motion) before content.
3. Give each motivation its own mode: tension (Classic), relaxation (Zen), score frenzy (Arcade).
4. Use the core verb to navigate menus and teach it before the first game.

**Analogy hooks**
- Slice-to-act → cutting mechanics in cooking, puzzle (rope cutting) and combat games.
- Menus as gameplay → any game with a one-verb core.
- Three modes for three motivations → puzzle (timed, zen, daily), runners (endless, challenge).

**Ontology encoding**
```json
{"loops": [
  {"id": "fn_core", "type": "core", "period": "seconds", "steps": [
    {"id": "c1", "action": "swipe_to_slice_fruit", "reward": "juice_and_points", "next": "c2"},
    {"id": "c2", "action": "slice_multiple_in_one_swipe", "reward": "combo_bonus", "next": "c3"},
    {"id": "c3", "action": "avoid_bombs_and_misses", "reward": "survival", "next": "c4"},
    {"id": "c4", "action": "game_over_retry", "reward": "best_score", "next": "c1"}]}],
 "economy": {"currencies": [
  {"id": "score", "kind": "xp", "sources": ["slices", "combos", "criticals"], "sinks": [], "cap": null}]}}
```

## 8. Angry Birds

**Snapshot**
- Developer: Rovio Entertainment (Espoo, Finland). Chillingo published the original iOS release.
- Release: 2009. Sega acquired Rovio in 2023.
- Genre: slingshot physics puzzle. Business model: premium at launch, plus a later IAP (Mighty Eagle, a level-skip purchase). Later titles such as Angry Birds 2 (2015) are free-to-play with lives, gems and power-ups.
- Scale: became a global brand with films (2016, 2019), merchandise and many spin-offs. Figures are omitted.

**Core loop**
1. Pull back the slingshot and aim. Trajectory and power are set by the drag.
2. Release the bird, and tap mid-flight to trigger its ability: speed (yellow), split (blue), bomb (black), egg drop (white).
3. Physics collapses the structures. Defeat every pig with the birds available.
4. The score depends on destruction plus unused birds. Earn 1–3 stars.
5. Retry instantly, or advance to the next level in the episode.

**Meta and progression**: episodes and level packs with themed materials and birds, star totals, hidden golden eggs, and Mighty Eagle mastery challenges in the original (verify the details).

**Economy (original)**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Stars | xp | level performance | unlock gating (not spent) |
| Mighty Eagle (one-time purchase) | premium | IAP | skip or clear a level (cooldown) |

**Monetization**: a paid app with free level updates, and the Mighty Eagle IAP. Free-to-play sequels use lives, gems and power-ups.

**Live-ops**: free episode updates in the premium era, seasonal spin-offs (Seasons), and events in later free-to-play titles.

**Retention hooks**: 3-star completion, new episodes, golden-egg secrets, and character attachment.

**Social layer**: Game Center, and enormous offline cultural reach (merchandise, film) that brought players back.

**UX and onboarding notables**
- The slingshot is a touch-native drag that is understood at a glance.
- The trajectory trail from the previous shot shows where it landed, an affordance for learning.
- Pig "laughter" taunts the player on failure, which motivates retry.

**Art and audio identity**: bold cartoon characters with a single readable trait each, satisfying wood, glass and stone break sounds, and a memorable theme.

**Psychology principles used**
- Experimentation and mastery: physics variance makes each shot slightly different.
- Completion via stars.
- Character emotion: the birds' anger and the pigs' smugness give a reason to act.

**Innovations**
- Made physics destruction readable and repeatable on a phone. The commonly cited predecessor is the browser game Crush the Castle.
- Helped standardise the 3-star level system and episode updates on mobile.
- Proved a mobile game could become a mass-market character brand.

**Weaknesses and criticism**
- Brand overextension and spin-off fatigue.
- Free-to-play sequels drew criticism for lives and pay-to-progress pressure (verify specific titles).
- The studio faced turbulent business cycles after peak popularity (widely reported).

**Lessons for designers**
1. Show the last trajectory: feedback for learning is as important as juice.
2. Give each unit one ability that changes the physics problem, so composition becomes strategy.
3. Characters with a simple motive (anger at egg thieves) turn a toy into a story.
4. A level-skip purchase can help stuck players without selling power. Use it only where skipping does not break progression.

**Analogy hooks**
- Slingshot aim with a previous-shot trail → golf, basketball, tower demolition, artillery games.
- Per-unit special abilities → puzzle units in sort or merge games, roguelite characters.
- A skip purchase for stuck players → any level-based game (puzzle hints).

**Ontology encoding**
```json
{"loops": [
  {"id": "ab_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "drag_slingshot_aim_release", "reward": "trajectory", "next": "c2"},
    {"id": "c2", "action": "tap_to_trigger_bird_ability", "reward": "physics_destruction", "next": "c3"},
    {"id": "c3", "action": "defeat_all_pigs_or_run_out_of_birds", "reward": "stars_or_retry", "next": "c1"}]},
  {"id": "ab_meta", "type": "meta", "period": "session", "steps": [
    {"id": "m1", "action": "accumulate_stars", "reward": "episode_unlock", "next": "m2"},
    {"id": "m2", "action": "find_golden_eggs", "reward": "secret_content", "next": "m1"}]}],
 "economy": {"currencies": [
  {"id": "stars", "kind": "xp", "sources": ["level_performance"], "sinks": [], "cap": null},
  {"id": "mighty_eagle", "kind": "premium", "sources": ["iap_one_time"], "sinks": ["level_skip"], "cap": 1}]}}
```

## 9. Stumble Guys

**Snapshot**
- Developer: Kitka Games, a small studio in Kajaani, Finland. Scopely announced the acquisition of the game in September 2022 ([Scopely](https://scopely.com/blog/welcome-stumble-guys-to-the-scopely-portfolio/); [PocketGamer.biz](https://www.pocketgamer.biz/scopely-acquires-stumble-guys-from-kitka-games)). Scopely is owned by Savvy Games Group.
- Release: 2020 on mobile, later on PC and consoles.
- Genre: party battle royale, the obstacle-course elimination format popularised by Fall Guys (Mediatonic, PC and console, 2020). Business model: free-to-play. IAP (gems), cosmetics and a pass.

**Core loop**
1. Queue into a lobby of up to 32 players (bots fill lobbies where needed; verify).
2. Play successive elimination rounds: races, survival and team rounds. Only the top finishers advance.
3. Win the final round to take the crown, or spectate and requeue after elimination.
4. Earn currency and pass progress, then unlock cosmetics (skins, emotes, animations, footsteps).

**Meta and progression**: the pass (Stumble Pass), cosmetic rarity tiers, events, and user-made levels in later builds (verify the editor's availability).

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Gems | hard | IAP, pass, events | cosmetics, pass premium track |
| Soft currency (name varies by version) | soft | match rewards | cosmetics, spins (verify) |
| Pass XP | xp | matches, quests | pass tiers |

**Monetization**: a premium pass, gem packs, cosmetic bundles, and rotating shop offers.

**Live-ops**: seasonal passes, rotating map playlists, events and collaborations (verify the current calendar).

**Retention hooks**: short matches (minutes), the chance to win any match, slapstick moments, and pass progress.

**Social layer**: party play with friends, spectating, and a large creator and streamer presence. User-generated levels add social content (verify).

**UX and onboarding notables**
- Joystick plus jump and dive buttons, with a camera that follows automatically.
- Elimination is soft: you spectate, then requeue in one tap.

**Art and audio identity**: bright, rounded, toy-like characters, physics ragdoll humour, and upbeat music.

**Psychology principles used**
- Chaos and humour: losing is funny rather than humiliating.
- Uncertainty of outcome (variable reward).
- Social play and relatedness.
- Collection of cosmetics.

**Innovations**: a mobile-first fast follower that brought a PC and console trend to phones before the original had a mobile version, with mobile-tuned controls and scale.

**Weaknesses and criticism**
- Seen as derivative.
- Network latency and cheating complaints.
- Cosmetic pricing criticism.
- Content treadmill pressure to keep map playlists fresh.

**Lessons for designers**
1. Watch platform trends on PC and console for formats with no mobile incumbent. Speed to market matters.
2. Fill lobbies with bots so matches start in seconds, and disclose or tune them fairly.
3. Ragdoll physics makes failure funny, which lowers the frustration cost of competition.
4. User-made levels are a content multiplier for a map-hungry format (`liveops`).

**Analogy hooks**
- The elimination round structure → puzzle royale, trivia royale, racing.
- Ragdoll failure humour → any physics game with high fail rates.
- Spectate-then-requeue → any session-based PvP.

**Ontology encoding**
```json
{"loops": [
  {"id": "sg_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "queue_into_32_player_lobby", "reward": "match_start", "next": "c2"},
    {"id": "c2", "action": "survive_elimination_rounds", "reward": "advance_or_spectate", "next": "c3"},
    {"id": "c3", "action": "win_final_round", "reward": "crown_currency_pass_xp", "next": "c1"}]},
  {"id": "sg_monetization", "type": "monetization", "period": "season", "steps": [
    {"id": "p1", "action": "progress_stumble_pass", "reward": "cosmetics", "next": "p2"},
    {"id": "p2", "action": "buy_premium_track_or_bundle", "reward": "exclusive_cosmetics", "next": "p1"}]}],
 "economy": {"currencies": [
  {"id": "gems", "kind": "hard", "sources": ["iap", "pass", "events"], "sinks": ["cosmetics", "premium_pass"], "cap": null},
  {"id": "pass_xp", "kind": "xp", "sources": ["matches", "quests"], "sinks": [], "cap": null}]}}
```

## 10. Archero

**Snapshot**
- Developer: Habby.
- Release: 2019.
- Genre: roguelite action in portrait, the reference title of hybrid-casual. Business model: free-to-play hybrid. IAP (gems, energy, chests, heroes, passes) plus rewarded ads.
- Scale: widely cited as the game that defined "hybrid-casual" (figures omitted).

**Core loop**
1. Spend energy to start a chapter run (5 energy per run in long-standing builds; verify).
2. Move with a one-thumb virtual joystick to dodge. **Stop moving, and the hero auto-shoots the nearest enemy.**
3. Clear a room, collect XP and coins, then walk through the door to the next room.
4. On level-up, choose 1 of 3 random abilities (multishot, ricochet, diagonal arrows, elemental effects and similar). Special rooms offer an angel (heal or ability) or a devil (trade max HP for an ability).
5. Beat periodic bosses. Death ends the run, with a revive offer (gems or rewarded ad).
6. Bank the run's coins and equipment, and upgrade gear and talents for the next attempt.

**Meta and progression**
- Equipment slots (weapon, armour, rings, pets and later more), with fusion of duplicates to raise rarity.
- Talents (random upgrades bought with coins), heroes with passives, and chapter unlocks.

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Energy | energy | timed regen, gems, rewarded ads | starting runs |
| Coins | soft | runs, idle and patrol-style rewards (verify), chests | gear levels, talents |
| Gems | hard | IAP, achievements, events | chests, energy, revives, heroes |
| Gear scrolls / materials | material | runs, chests | gear upgrades |
| Equipment | material | chests, runs | fusion into higher rarity |

**Monetization**: gem packs, chests (random equipment, with odds disclosure required by store rules), hero purchases, energy, passes and starter packs. Rewarded ads for revives, extra ability rerolls and doubled rewards.

**Live-ops**: events and limited modes, new chapters and heroes, and seasonal passes (verify the current calendar).

**Retention hooks**: the energy cadence (appointments), the gear power curve, unlocking the next chapter, and run variety from random abilities.

**Social layer**: light. Leaderboards and some cooperative or event modes in later builds (verify).

**UX and onboarding notables**
- **Stop-to-shoot** resolves the twin-stick problem on a phone: one thumb, two meanings (move to dodge, stand still to attack), and a constant risk/reward decision.
- Portrait orientation keeps one-handed play, and the vertical rooms fit the screen.
- The level-up choice screen pauses the action, which suits interruptions.

**Art and audio identity**: clean cartoony fantasy, readable projectiles and telegraphs, and satisfying hit sparks.

**Psychology principles used**
- Variable reward from random ability drafts.
- Competence from skill-based dodging.
- Endowed progress from persistent gear (SDT).
- Loss aversion at death and revive.
- Sunk cost on gear investment.

**Innovations**
- The one-input stop-to-shoot control.
- Grafting a free-to-play gear and energy meta onto a hyper-casual-readable roguelite core. That template defined hybrid-casual and spread across many later games.

**Weaknesses and criticism**
- Gear walls in later chapters push toward spending (pay-to-progress).
- Energy gates binge play.
- Random equipment chests raise loot-box regulation concerns in some markets (`legal-ethics`).

**Lessons for designers**
1. One thumb, two meanings: a context-sensitive input (move versus stand still) can replace a second stick.
2. A run-level draft (1 of 3) plus account-level gear is the hybrid-casual backbone. Tune both with `economy_sim.py` and `progression_calc.py`.
3. Rewarded-ad rerolls and revives give non-payers agency and still produce revenue.
4. Watch gear walls: chart the expected days-to-next-chapter for non-payers (`targets.days_to_complete_content`).

**Analogy hooks**
- Stop-to-act → puzzle (stop to aim), rhythm (hold still to charge), stealth (freeze to hide).
- Draft 1 of 3 on level-up → tower defense waves, puzzle boosters, idle game milestones.
- Angel and devil rooms → risk-trade choices in any run-based game.

**Ontology encoding**
```json
{"loops": [
  {"id": "ar_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "move_to_dodge_stop_to_autoshoot", "reward": "room_cleared_xp_coins", "next": "c2"},
    {"id": "c2", "action": "draft_one_of_three_abilities", "reward": "run_power_spike", "next": "c3"},
    {"id": "c3", "action": "beat_boss_or_die", "reward": "chapter_progress_or_revive_offer", "next": "c1"}]},
  {"id": "ar_meta", "type": "meta", "period": "daily", "steps": [
    {"id": "m1", "action": "spend_energy_on_runs", "reward": "coins_gear_scrolls", "next": "m2"},
    {"id": "m2", "action": "upgrade_and_fuse_gear_talents", "reward": "account_power", "next": "m3"},
    {"id": "m3", "action": "attempt_next_chapter", "reward": "new_content", "next": "m1"}]}],
 "economy": {"currencies": [
  {"id": "energy", "kind": "energy", "sources": ["regen", "gems", "rewarded_ad"], "sinks": ["run_start"], "cap": 20},
  {"id": "coins", "kind": "soft", "sources": ["runs", "chests"], "sinks": ["gear_levels", "talents"], "cap": null},
  {"id": "gems", "kind": "hard", "sources": ["iap", "achievements", "events"], "sinks": ["chests", "energy", "revive", "heroes"], "cap": null},
  {"id": "gear_scrolls", "kind": "material", "sources": ["runs", "chests"], "sinks": ["gear_upgrades"], "cap": null}]}}
```
Note: the energy `cap` of 20 is illustrative. Verify it in the current build before using it as a benchmark.

## 11. Survivor.io

**Snapshot**
- Developer: Habby.
- Release: 2022 worldwide (after testing in 2021; verify).
- Genre: survivor-like ("bullet heaven") in portrait with a hybrid-casual meta. Business model: free-to-play hybrid. IAP (gems, passes, chests, energy, monthly cards) plus rewarded ads.
- Lineage: rules adapted from Vampire Survivors (section 12) and meta structure from Archero (section 10).

**Core loop**
1. Spend energy to start a chapter run.
2. Move with a joystick. Weapons fire automatically.
3. Kill swarms, collect XP gems, and level up.
4. On level-up, choose 1 of 3: a new weapon, a weapon upgrade, or a passive.
5. A weapon at max level plus its matching passive evolves into a stronger form, a recipe-discovery rule borrowed from Vampire Survivors.
6. Survive the chapter's timer and boss waves to clear it. Death ends the run, with a revive offer.
7. Bank coins, equipment and materials, and upgrade the account.

**Meta and progression**
- Six equipment slots with merge-to-upgrade rarity, talents, unlockable survivors (characters), and chapter progression.
- Idle "patrol" rewards that accrue while away (verify the naming).

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Energy | energy | timed regen, purchases, ads | run start |
| Gold | soft | runs, patrol and idle rewards, events | equipment levels, talents |
| Gems | hard | IAP, events, achievements | chests, energy, revives, passes |
| Design and material items | material | runs, chests, events | equipment upgrades and merges |

**Monetization**: battle passes, monthly cards, gem packs, equipment chests (odds disclosure), starter packs, and rewarded ads for revives and doubled rewards.

**Live-ops**: dense event cadence (limited modes, collaborations, seasonal passes) (verify the current calendar).

**Retention hooks**: idle rewards (absence converted into value), energy appointments, gear progression, and chapter unlocks.

**Social layer**: guild or club features and leaderboards in later builds (verify).

**UX and onboarding notables**
- The one-thumb joystick is the only input, so portrait one-handed play is natural.
- The level-up choice pauses the action, so interruptions are safe.
- Evolution recipes are taught by in-game hints, which turns discovery into guided learning.

**Art and audio identity**: cartoony zombie-apocalypse theme, very readable XP gems and threat colours, and heavy hit feedback.

**Psychology principles used**
- Power fantasy through escalation (weak to god-like within a run).
- Variable reward from drafts.
- Endowed progress and sunk cost from gear.
- Absence reward from idle patrol.

**Innovations**
- Translated a premium-indie subgenre into a free-to-play portrait game within roughly a year of the original's breakout.
- Paired that run structure with an Archero-style gear meta and idle rewards. This became the template for many survivor-like hybrid-casual games.

**Weaknesses and criticism**
- Pay-to-progress gear walls in later chapters.
- Heavy monetization surface (passes, cards, chests).
- Derivative of Vampire Survivors' rules.
- Late-run screen clutter on small displays.

**Lessons for designers**
1. A premium-indie subgenre's rules are portable to free-to-play. The work is in the meta, the session length and portrait readability.
2. Fixed-length runs fit mobile sessions better than open-ended survival.
3. Idle rewards answer "why open the app today" without demanding play.
4. Model the gear economy before launch: hoard days, days-to-chapter for non-payers, and payer conversion (`economy-model.schema.json` targets).

**Analogy hooks**
- The weapon + passive evolution recipe → crafting discovery in any roguelite, card synergies, merge discoveries.
- Idle patrol → any action game's offline reward.
- Portrait one-thumb survival → defence games, twin-stick-lite shooters.

**Ontology encoding**
```json
{"loops": [
  {"id": "sio_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "move_while_weapons_autofire", "reward": "kills_xp_gems", "next": "c2"},
    {"id": "c2", "action": "draft_weapon_or_passive", "reward": "build_growth", "next": "c3"},
    {"id": "c3", "action": "evolve_max_weapon_with_matching_passive", "reward": "power_spike", "next": "c4"},
    {"id": "c4", "action": "survive_timer_and_bosses_or_die", "reward": "chapter_clear_or_revive_offer", "next": "c1"}]},
  {"id": "sio_meta", "type": "meta", "period": "daily", "steps": [
    {"id": "m1", "action": "collect_idle_patrol_rewards", "reward": "gold_materials", "next": "m2"},
    {"id": "m2", "action": "merge_and_level_equipment", "reward": "account_power", "next": "m3"},
    {"id": "m3", "action": "spend_energy_on_next_chapter", "reward": "progress", "next": "m1"}]}],
 "economy": {"currencies": [
  {"id": "energy", "kind": "energy", "sources": ["regen", "iap", "rewarded_ad"], "sinks": ["run_start"], "cap": null},
  {"id": "gold", "kind": "soft", "sources": ["runs", "idle_patrol", "events"], "sinks": ["equipment_levels", "talents"], "cap": null},
  {"id": "gems", "kind": "hard", "sources": ["iap", "events", "achievements"], "sinks": ["chests", "energy", "revive", "pass"], "cap": null},
  {"id": "designs", "kind": "material", "sources": ["runs", "chests"], "sinks": ["equipment_upgrades"], "cap": null}]}}
```

## 12. Vampire Survivors

**Snapshot**
- Developer: poncle (Luca Galante).
- Release: Steam Early Access in December 2021, version 1.0 in 2022. Mobile (free) and console versions followed from 2022.
- Genre: survivor-like, the game that named and popularised the "bullet heaven" subgenre. Business model: low-priced premium on PC and console, with paid DLC. Mobile is free with optional ads (rewarded for in-game gold) (verify the current ad-free option).
- Recognition: won Best Game at the 2023 BAFTA Games Awards.

**Core loop**
1. Pick a character (each with a starting weapon and passive bonus) and a stage.
2. Move. That is the only input. Weapons attack automatically on their own patterns.
3. Kill growing hordes, collect XP gems, and level up. Choose from offered weapons and passives.
4. Open treasure chests dropped by elites. Once a weapon is maxed and its paired passive is owned, a chest can evolve it (the evolution recipes).
5. Survive to the 30-minute mark, when Death arrives. Bank gold and unlocks either way.
6. Spend gold on permanent PowerUps. Unlock characters, stages, relics and Arcanas through achievements and secrets.

**Meta and progression**: a large achievement-driven unlock grid of characters, weapons, stages and modifiers, plus permanent PowerUps. DLC packs add characters, stages and weapons, including crossovers (Among Us, Contra, Castlevania) (verify the current list).

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Gold | soft | runs, pickups, (mobile) optional rewarded ads | PowerUps, character purchases |
| Unlocks | xp | achievements, secrets | none (gates content) |

**Monetization**: a premium base price and DLC on PC and console. On mobile, free with optional rewarded ads for gold and paid DLC. There are no energy systems or loot boxes.

**Live-ops**: free content updates and paid DLC drops, with no event calendar.

**Retention hooks**: the unlock grid (what is behind the next secret), evolution recipe discovery, build experimentation, and community knowledge sharing.

**Social layer**: local co-op was added later (verify the platforms). A strong community wiki and recipe-sharing culture.

**UX and onboarding notables**
- One input lets anyone play. Depth lives in the build choices.
- Pausing level-up choices suit interruptions.
- Late-game visual density challenges readability, especially on phones.

**Art and audio identity**: pixel art with gothic-horror homage (Castlevania-inspired), chiptune-flavoured gothic music, and escalating screen-filling effects as the power-fantasy payoff.

**Psychology principles used**
- Power fantasy inversion: the player is the overwhelming force.
- Variable reward from drafts and chests.
- Discovery and curiosity from recipes and secrets.
- Competence through build mastery.
- Completionism through the unlock grid.

**Innovations**
- Inverted the shoot 'em up: the bullets are yours, and the threat is density rather than projectiles.
- Reduced input to movement only.
- Evolution recipes as discoverable synergies.
- Proved that a tiny-budget, low-price game can create a genre that big studios then adapt (see Survivor.io).

**Weaknesses and criticism**
- "The game plays itself" critiques.
- Late-run visual noise and performance load on low-end devices.
- Its rules are easy to copy and were rapidly adapted by free-to-play games.

**Lessons for designers**
1. Remove inputs until the decision layer is all that remains. Then make the decisions meaningful.
2. Synergy recipes create community discovery for free. Hide some, hint at others.
3. A fixed run length (30 minutes) gives a clear arc. Mobile adaptations shorten it.
4. Fair monetization (premium plus optional ads, no energy) is a brand asset with a core audience.
5. Budget performance for particle density on low-end devices (`mobile-performance`).

**Analogy hooks**
- Movement-only control plus auto-attack → defence games, idle-action hybrids, "bullet heaven" puzzles.
- Evolution recipes → card combos, merge chains, crafting.
- An unlock grid of secrets → any game with a large content catalogue.

**Ontology encoding**
```json
{"loops": [
  {"id": "vs_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "move_only_weapons_autoattack", "reward": "kills_xp_gems", "next": "c2"},
    {"id": "c2", "action": "choose_weapon_or_passive_on_levelup", "reward": "build_growth", "next": "c3"},
    {"id": "c3", "action": "open_chest_for_evolution", "reward": "evolved_weapon", "next": "c4"},
    {"id": "c4", "action": "survive_to_30_minutes_or_die", "reward": "gold_unlocks", "next": "c1"}]},
  {"id": "vs_meta", "type": "meta", "period": "session", "steps": [
    {"id": "m1", "action": "spend_gold_on_powerups", "reward": "permanent_stats", "next": "m2"},
    {"id": "m2", "action": "pursue_achievement_unlocks", "reward": "new_characters_stages", "next": "m1"}]}],
 "economy": {"currencies": [
  {"id": "gold", "kind": "soft", "sources": ["runs", "pickups", "optional_rewarded_ad_mobile"], "sinks": ["powerups", "characters"], "cap": null},
  {"id": "unlocks", "kind": "xp", "sources": ["achievements", "secrets"], "sinks": [], "cap": null}]}}
```

## 13. Count Masters

**Snapshot**
- Developer and publisher: Freeplay LLC (the App Store seller and developer name for "Count Masters: Crowd Runner 3D", bundle `freeplay.crowdrun.com`). Other apps use near-identical names, so check the seller.
- Release: first released on the iOS App Store on 19 May 2021 (App Store listing metadata, read through Apple's iTunes Search API: [source](https://itunes.apple.com/search?term=count+masters&entity=software&country=us&limit=6)).
- Genre: crowd runner (hyper-casual, later hybrid features). Business model: ad-led (interstitials, rewarded) with light IAP.
- Context: the "math gate" crowd runner became one of the most imitated hyper-casual formats, and it appears widely in user-acquisition creatives for other genres, including 4X (see Last War: Survival in `references/midcore-strategy.md`).

**Core loop**
1. Drag left and right to steer a crowd of stick figures running forward.
2. Choose between gates that modify the crowd: +N, ×N, −N, ÷N.
3. Avoid obstacles (saws, hammers) that remove members.
4. Clash with enemy crowds, where numbers subtract one-for-one.
5. At the finish, fight a boss or climb a multiplier staircase or castle with the remaining crowd. Earn coins in proportion.
6. Upgrade starting crowd size and income, then play the next level.

**Meta and progression**: upgrades (starting crowd, coin income), skins, and level numbers. Some variants add base or collection metas (verify).

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Coins | soft | level-end multipliers, rewarded ads (multiply reward) | starting-crowd and income upgrades, skins |

**Monetization**: interstitials between levels, rewarded "multiply your reward" at level end, and ad removal.

**Live-ops**: minimal.

**Retention hooks**: upgrade goals, numbered levels, and a visible crowd as instant power feedback.

**Social layer**: none.

**UX and onboarding notables**
- Arithmetic is readable at a glance. The crowd's size is the score, the health bar and the power display at once.
- Gate choices are binary and fast (left or right), so decisions happen at running speed.

**Art and audio identity**: simple coloured stick figures, bright gates with large numerals, and swelling crowd audio and visuals.

**Psychology principles used**
- Instant feedback from numerical growth.
- Quick risk/reward choices (×2 versus +30).
- The power fantasy of a growing army.
- Endowed progress via starting-crowd upgrades.

**Innovations**
- Arithmetic as a real-time choice mechanic.
- Representing a number as bodies, so the game state is perfectly legible in a 3-second ad.

**Weaknesses and criticism**
- Shallow and endlessly cloned.
- Ad-heavy.
- The format is widely used in user-acquisition creatives for games that do not contain it, a misleading-ad risk (`marketing-ua`).

**Lessons for designers**
1. Make the key number visible as the avatar itself (crowd size, stack height, snake length).
2. Binary choices at speed work when the outcome is legible in under 300 ms.
3. "Multiply your reward" rewarded ads at level end are a high-acceptance placement. Cap the frequency.
4. If you use this format in ads, include it as real gameplay.

**Analogy hooks**
- Math gates → army builders, idle games (multiplier choices), the 4X UA mini-games that later became in-game modes.
- Crowd as health bar → snake games, stack runners, swarm defence.
- A multiplier staircase finale → any level-end bonus moment.

**Ontology encoding**
```json
{"loops": [
  {"id": "cm_core", "type": "core", "period": "seconds", "steps": [
    {"id": "c1", "action": "steer_crowd_through_gate", "reward": "crowd_size_change", "next": "c2"},
    {"id": "c2", "action": "avoid_obstacles_clash_enemy_crowds", "reward": "survivors_remaining", "next": "c3"},
    {"id": "c3", "action": "finale_boss_or_multiplier_stairs", "reward": "coins", "next": "c4"},
    {"id": "c4", "action": "upgrade_starting_crowd_or_income", "reward": "stronger_next_run", "next": "c1"}]}],
 "economy": {"currencies": [
  {"id": "coins", "kind": "soft", "sources": ["level_end_multiplier", "rewarded_ad_multiplier"], "sinks": ["starting_crowd_upgrade", "income_upgrade", "skins"], "cap": null}]}}
```

## 14. Paper.io 2

**Snapshot**
- Publisher: Voodoo.
- Release: 2018 (following the original Paper.io).
- Genre: io-style territory capture. Business model: ad-led (interstitials, rewarded continues) with skins.
- Lineage: browser io games (Agar.io, 2015; Slither.io, 2016) and earlier light-cycle and territory games.

**Core loop**
1. Start with a small patch of territory.
2. Steer out of it. While outside, you leave a trail.
3. Return to your territory to close the loop. All enclosed area becomes yours.
4. If any rival touches your trail while you are outside, you die. Cut rivals' trails to eliminate them.
5. The round ends at death or when the map is dominated. The ranking is the percentage of map owned. A rewarded continue is offered on death.

**Meta and progression**: skins and levels, and a campaign or level mode in some builds (verify).

**Economy**: score (territory %) is `xp`. Skins come from progress or ads.

**Monetization**: interstitials between rounds, rewarded continues, and ad removal or skins.

**Live-ops**: minimal.

**Retention hooks**: escalating greed (bigger loops, bigger gains, bigger risk), short rounds, and beating your best percentage.

**Social layer**: io framing with named rivals. As in section 4, verify whether rivals are bots before making claims.

**UX and onboarding notables**
- A single steering input. The rule is clear from watching one loop close.
- The territory colour fill gives large, satisfying visual feedback.

**Art and audio identity**: flat colours, a top-down map, and bold area fills with a pop on capture.

**Psychology principles used**
- Risk-reward escalation (greed versus safety).
- Loss aversion: the trail is a visible exposure.
- Completion and closure when a loop closes.
- Social comparison on the percentage ranking.

**Innovations**: popularised the trail-and-enclose territory loop as a mobile hyper-casual format, packaged from the browser io genre with bots and ads.

**Weaknesses and criticism**
- Shallow, and bot-filled "multiplayer" can feel misleading.
- Ad load.
- Easily cloned.

**Lessons for designers**
1. Make exposure visible: a trail that shows how much you are risking creates tension without a timer.
2. Let the player choose the size of the bet in every loop.
3. Closure (filling the enclosed area) is a strong reward. Make it big and fast.

**Analogy hooks**
- Enclosure capture → Two Dots-style loop clears (see `references/puzzle-casual.md`), city-builder zoning, farming land claims.
- A visible exposure trail → stealth games, risk mechanics in runners.
- Greed-sized bets → push-your-luck systems in roguelites and casino-adjacent games.

**Ontology encoding**
```json
{"loops": [
  {"id": "pio_core", "type": "core", "period": "seconds", "steps": [
    {"id": "c1", "action": "leave_territory_drawing_trail", "reward": "exposure_and_potential_area", "next": "c2"},
    {"id": "c2", "action": "return_to_close_loop", "reward": "territory_capture", "next": "c3"},
    {"id": "c3", "action": "cut_rival_trails_or_get_cut", "reward": "eliminations_or_death", "next": "c4"},
    {"id": "c4", "action": "round_end_ranking", "reward": "territory_percent_rank", "next": "c1"}]}],
 "economy": {"currencies": [
  {"id": "territory_percent", "kind": "xp", "sources": ["loop_captures", "eliminations"], "sinks": [], "cap": 100}]}}
```

## 15. Cross-case synthesis: from hyper-casual to hybrid-casual

### 15.1 The unit-economics model behind the shift

```
LTV(horizon)    = Σ_{d=0..H} retention(d) × ARPDAU(d)          # expected active days × revenue per active day
ARPDAU_ads      = impressions_per_DAU × eCPM / 1000
ARPDAU_iap      = daily_payer_rate × ARPPU_per_paying_day
UA is viable when LTV(payback window) ≥ CPI × (1 + target margin)
```

- **Hyper-casual (2016 to around 2021)** lived on ads. Lifetimes were short, so it only worked with very cheap installs (high creative click-through from a rule readable in 3 seconds) and good ad yields. Helix Jump, Hole.io, Paper.io 2 and Count Masters are the canonical cases.
- **The squeeze.** Apple's App Tracking Transparency (from iOS 14.5, 2021) reduced access to the advertising identifier and weakened targeting and attribution. That pushed ad yields down and made installs harder to buy efficiently (directionally widely reported; see [V5] for current opt-in estimates). Rising saturation added creative fatigue.
- **Hybrid-casual** raises LTV without losing marketability. Keep the readable core, then add a meta and IAP (gear, upgrades, passes) plus rewarded ads, so ARPDAU and active days both rise (Archero, Survivor.io). Voodoo, the archetypal hyper-casual publisher, publicly pivoted to fewer, deeper hybrid-casual launches [V1][V2].
- **Illustrative arithmetic (not a benchmark).**
  - Pure ads: 8 expected active days in the payback window × $0.05 ARPDAU = $0.40 LTV, which loses money at a $0.50 CPI.
  - With a meta: 10 days × $0.09 (ads plus IAP) = $0.90 LTV, which is viable at the same CPI.
  - Reproduce with real curves: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/retention_ltv.py ltv --points "1:0.40,7:0.15,30:0.05" --arpdau 0.09 --horizon 90`.

### 15.2 Model comparison

| Dimension | Hyper-casual | Hybrid-casual | Casual (IAP puzzle/sim) |
|---|---|---|---|
| Core readability | 3-second rule, one gesture | Same, with a decision layer (drafts) | Learnable in a level or two |
| Session | 30 s – 3 min, many per day | 3–10 min runs | 5–20 min |
| Retention driver | Novelty, high score | Account power, run variety, energy or idle rewards | Content ladder, meta, teams |
| Monetization | Interstitials, rewarded | Rewarded + IAP (starter, pass, gear) | IAP-led (continues, boosters, lives) |
| Live-ops | None | Events reusing the core, passes | Dense event calendars, teams |
| Content cost | Very low | Medium (chapters, gear, heroes) | High (levels, meta art) |
| Cases | 3, 4, 13, 14 (and 1 as precursor) | 10, 11 (and 5 as a live runner) | `references/puzzle-casual.md` |

### 15.3 Hybrid-casual recipe (procedure)

1. **Core.** Pass the 3-second muted-clip test, keep one-thumb portrait play, and keep retry under 2 seconds.
2. **Run variance.** Add a pause-safe draft (1 of 3) or a gate choice, so each run differs (cases 10–13).
3. **Account progression.** Add gear, upgrades or characters that multiply run results, with a visible power curve. Model it with `progression_calc.py curve` and check non-payer days-to-content in `economy_sim.py`.
4. **One appointment system.** Choose energy (Archero) or idle rewards (Survivor.io), and avoid stacking both with heavy interstitials.
5. **Monetization ladder.**
   - Rewarded ads (revive, double, reroll), then a starter pack, then a pass, then gear chests (with odds disclosure), then limited offers.
   - Set interstitial pacing in `contract.monetization.ads.interstitial` (`first_after_sec`, `min_interval_sec`).
6. **Live-ops.** Run events that reuse the core with modifiers (new enemies, limited heroes) rather than new games.
7. **Validation.**
   - Creative CPI test before production (`marketing-ua`).
   - D1, D7 and payer-conversion targets in `contract.analytics.kpi_targets`.
   - Kill criteria written before soft launch.

**Pitfalls**:
- A meta that never changes how the core plays.
- Gear walls without a non-payer path.
- Energy plus forced ads double-gating.
- Ad creatives showing modes that the game does not contain (Count Masters, section 13; Homescapes in `references/puzzle-casual.md`).

### 15.4 Verb table: the one-thumb inputs that worked

| Verb | Cases | Mobile fit | Design note |
|---|---|---|---|
| Tap (impulse/hop) | Flappy Bird, Crossy Road | Excellent | Tune impulse and gravity; instant retry |
| Swipe (lanes/turns) | Subway Surfers, Temple Run | Excellent | Swipe direction must match world direction |
| Swipe (slice) | Fruit Ninja | Excellent | Juice is the reward; menus use the verb |
| Continuous drag (rotate/steer) | Helix Jump, Hole.io, Paper.io 2, Count Masters | Excellent | Analog control gives flow; keep the thumb off key information |
| Drag-and-release (aim) | Angry Birds | Very good | Show the last trajectory |
| Joystick + context (stop to act) | Archero | Very good | One thumb, two meanings |
| Joystick + auto-attack | Survivor.io, Vampire Survivors | Very good | Depth moves to drafts; watch late-run readability |
| Joystick + buttons | Stumble Guys | Good | Needs two thumbs, so landscape or careful portrait layout |

### 15.5 Timeline

```
2009–2012  Premium touch arcade: Angry Birds, Fruit Ninja, Temple Run (paid → F2P switch), Subway Surfers (F2P + live re-theming)
2013–2014  Viral and opt-in-ad era: Flappy Bird (organic virality), Crossy Road (rewarded video + cosmetics)
2016–2021  Hyper-casual publisher model: Helix Jump, Hole.io, Paper.io 2, Count Masters (test creatives → ship → arbitrage)
2019–now   Hybrid-casual: Archero (stop-to-shoot + gear), Survivor.io (survivor-like + gear + idle)
2020–now   Trend fast-follows and indie-born subgenres: Stumble Guys (party royale), Vampire Survivors (bullet heaven)
```

## 16. Volatile facts (as of Oct 2026 — verify before relying)

- [V1] Voodoo used to test about 1,000 prototypes a year (2024). It has pivoted to hybrid-casual with about four launches a year. Source: [mobilegamer.biz](https://mobilegamer.biz/voodoo-to-launch-just-four-games-per-year-after-hard-hybridcasual-pivot/).
- [V2] Voodoo describes growing hybrid-casual revenue from zero to $250M in three years (company claim). Source: [Voodoo](https://voodoo.io/news/voodoo-s-secret-sauce-from-0-to-250m-hybridcasual-revenue-in-3-years).
- [V3] Hybrid-casual spending grew 17.1% in 2025 ($3.5B → $4.2B). Source: [Mobilegamer.biz (Sensor Tower)](https://mobilegamer.biz/data-digest-sensor-towers-h1-analysis-hay-days-comeback-julys-top-games-big-krafton-numbers-and-more/).
- [V4] Feb–Apr 2026: casual and hyper-casual each took about 40% of mobile game ad revenue, hybrid 16%, mid-core 4%. In Jan–May 2026, ads were 70.3% of game revenue in India vs 22.1% in the US. Sources: [GameDev Reports (Sensor Tower summary)](https://gamedevreports.substack.com/p/sensor-tower-mobile-game-ad-monetization), [Sensor Tower](https://sensortower.com/blog/gaming-deep-dive-ad-monetization-report).
- [V5] Reported ATT opt-in rates conflict: about 50% globally (AppsFlyer data, via Moburst) versus about 35% (an Adjust 2025 figure). Source: [Moburst](https://www.moburst.com/blog/idfa-att-update/).
- [V6] Hyper-casual D1 retention is cited at roughly 33–40% in secondary sources. The figures are inconsistent and partly trace back to 2022 data, so treat them as order-of-magnitude only. Sources: [Segwise](https://segwise.ai/blog/mobile-gaming-app-user-retention-strategies), [AppAgent](https://appagent.com/blog/mobile-game-retention-benchmarks/).
- [V7] Checked on 2026-10-20 through Wikipedia pages that cite the original coverage: Flappy Bird's $50,000-a-day ad claim (The Verge, 5 February 2014; a developer claim), Crossy Road's $10M and 50M downloads within three months (Polygon, 3 March 2015) and Subway Surfers' one billion Google Play downloads (March 2018). Sources: [Flappy Bird](https://en.wikipedia.org/wiki/Flappy_Bird), [Crossy Road](https://en.wikipedia.org/wiki/Crossy_Road), [Subway Surfers](https://en.wikipedia.org/wiki/Subway_Surfers). The original articles were not retrieved, so quote them as "reported" and read the originals before external use. Stumble Guys: [Scopely announcement](https://scopely.com/blog/welcome-stumble-guys-to-the-scopely-portfolio/). Count Masters: [App Store metadata](https://itunes.apple.com/search?term=count+masters&entity=software&country=us&limit=6).
