# Studio Doctrines

How influential studios think, summarized in our own words with attribution, and translated into rules an AI-driven mobile studio can actually run. Each entry has the same five parts: **beliefs** (what the studio holds to be true about making games), **practices** (what it does differently day to day), **evidence and outcomes** (only widely reported results; uncertain points are flagged), **apply it here** (how the `arcosian` plugin borrows the idea through its agents, gates, scripts and contract fields), and **verify** (claims you should check before quoting them to anyone). Studio cultures change and public accounts are partial: treat this as a map of ideas, not as a factual history or a ranking. Market numbers and recent events live in the labelled volatile section at the end.

## Contents

1. How to use this file
2. Synthesis: where great studios agree and where they split
3. Platform holders and craft houses: Nintendo, Valve, Blizzard, Riot, Mojang
4. Mobile free-to-play leaders: Supercell, King, Rovio, Dream Games, Playrix, Moon Active, Scopely
5. Asian majors and gacha: HoYoverse, Tencent (TiMi, Lightspeed), NetEase
6. Hybrid-casual and hypercasual: Habby; Voodoo, Homa and SayGames
7. Cautionary case: Zynga
8. Auteur and indie craft: FromSoftware, thatgamecompany, Playdead, Klei, Supergiant, Mega Crit, LocalThunk, Team Cherry, ConcernedApe
9. Studio rituals worth stealing
10. Failure gallery: what went wrong and which guard prevents it
11. Borrowing matrix: which studio to study for which project
12. Volatile facts (as of Oct 2026 — verify before relying)

---

## 1. How to use this file

- **Borrow mechanisms, not outcomes.** Supercell kills games because its bar is "a hit that lasts a decade" and because it can afford to; the transferable part is *pre-committed kill criteria*, not "kill everything".
- **Check the transfer conditions.** Before copying a practice, write down the two or three conditions that made it work for the source studio (budget, IP, audience, team size, platform era) and tick which ones you share. Fewer than half shared means borrow only the principle. Use the transfer test in `SKILL.md` (Procedure C).
- **Prefer convergent beliefs.** A belief held by studios with opposite business models (for example, "play the build early and often" at Nintendo, Valve, Supercell and Mega Crit) is close to a law. A belief held by one business model only (for example, "test the ad before the game") is a strategy that depends on market conditions.
- **Use the cautionary entries as much as the heroic ones.** Zynga, the hypercasual collapse, and late Blizzard monetization episodes teach as much as the hits.

---

## 2. Synthesis: where great studios agree and where they split

### 2.1 Convergent beliefs (treat as near-laws)

| Belief | Studios that hold it in very different contexts | Plugin mechanism |
|---|---|---|
| The build is the truth; play it constantly | Nintendo (play first), Valve (silent playtests), Supercell (cells play daily), Mega Crit (run metrics), FromSoftware | `playthrough` gate; `/arcosian:playtest-sweep`; `player-simulator` personas |
| Small teams with full ownership ship better games | Supercell cells, Blizzard's small Hearthstone team (reported), Supergiant, Team Cherry, ConcernedApe, LocalThunk | One owner per feature in `features.json`; single `principal` for vision |
| Cancel or cut what is not great, early | Supercell kills, Blizzard cancellations, Miyamoto's "upending the tea table" (reported) | `kill_criteria` in the contract; `concept-tournament`; `critic` veto at the fun checkpoint |
| Teach through play, not text | Nintendo World 1-1, Valve's Portal test chambers, Playdead's wordless design | `ftue.steps[].teaches`; level-spec `teach` field (`teach`, `test`, `twist`, `reward`) |
| Readability and feel are product quality, not decoration | Blizzard silhouettes, Dream Games speed, Klei's visualized stealth information, LocalThunk's juiced scoring | `visual` gate rubric; `game-feel` and `art-direction` skills |
| Long-term player trust is an asset | Riot (player-focused mission), ConcernedApe (free updates), thatgamecompany (prosocial design), Klei (open early access) | Doctrine 8; `monetization.ethics`; `compliance-officer` |
| Instrument, then decide | King (difficulty funnels and bots), Mega Crit (pick-rate vs win-rate), Valve (experimental psychology), Supercell (soft-launch KPIs) | `analytics.taxonomy_ref`; `ab_test.py`; `difficulty_curve.py analyze` |

### 2.2 Genuine splits (context decides)

| Axis | Pole A (exemplars) | Pole B (exemplars) | Choose A when | Choose B when |
|---|---|---|---|---|
| Throughput vs craft | Voodoo-era hypercasual: hundreds of prototypes a year | Team Cherry, Playdead: years of polish on one game | Market signal is cheap and fast to read; content is shallow | Differentiation is the craft itself; premium price; word of mouth |
| Data-led vs vision-led | King, Zynga, Scopely | FromSoftware, Playdead, thatgamecompany | Mature genre with known levers; large live audience | New aesthetic or emotion; audience does not know it wants it yet |
| Product vs service | Playdead, Team Cherry, LocalThunk (premium, finished) | Supercell, HoYoverse, Riot (years of live ops) | Small team; finite content; strong single-session experience | Repeatable core loop; social layer; content cadence affordable |
| Authored vs systemic | Nintendo levels, Playdead, Naughty Dog-style linearity | Mojang, Klei (Oxygen Not Included), RimWorld | Precise emotional beats; puzzle intent | Replayability from rules; player stories; long tail |
| Premium vs F2P | ConcernedApe, LocalThunk, Mega Crit | Supercell, HoYoverse, Moon Active | Defined content and audience that pays up front (PC, console, Apple Arcade) | Mobile mass market, long retention, live content economics |
| Central vision vs autonomous teams | Nintendo producers/directors, FromSoftware (Miyazaki directs) | Supercell cells, Valve's flat structure | Coherent auteur aesthetic | Portfolio of independent bets; speed |

**House reading for an AI-driven mobile studio.** Agents make throughput cheap, so the plugin can prototype like a hypercasual publisher while finishing like a craft studio: many concepts die in `concept-tournament`, few survive to the contract, and the survivors must clear all five gates. Vision is centralized in the `principal` agent and the human taste checkpoints; execution is distributed to specialist agents with explicit ownership.

---

## 3. Platform holders and craft houses

### Nintendo

**Beliefs.**
- *Lateral thinking with withered technology* (Gunpei Yokoi): mature, cheap, well-understood components used in a surprising way beat cutting-edge parts. Novelty belongs in how the technology is used, not in its spec sheet.
- *Play first* (Shigeru Miyamoto): a game begins from a pleasant feeling in the hands. The verb (run, jump, swing) is tuned until it is enjoyable in an empty space, and the world is built around it.
- *Teach through the level.* Miyamoto has explained in interviews (notably a widely shared 2015 video interview about World 1-1 of *Super Mario Bros.*) how the opening screen teaches direction, jumping, enemies and power-ups without a word of text.
- *Kishōtenketsu level structure.* Koichi Hayashida, director on *Super Mario 3D Land* and *3D World*, described in a 2012 interview ([Game Developer](https://www.gamedeveloper.com/design/the-secret-to-i-mario-i-level-design); [Nintendo Life, April 2012](https://www.nintendolife.com/news/2012/04/super_mario_3d_land_director_shares_level_design_inspirations)) building stages like the four-part East Asian narrative form (the "kishōtenketsu" label comes from secondary summaries; check the interview wording): introduce one gimmick in safety, develop it under pressure, twist it, then conclude. One idea per level, explored fully, then discarded.
- *Expand the player population.* Under Satoru Iwata the DS and Wii targeted lapsed and non-players rather than competing on raw power (often described as a "blue ocean" strategy).
- *Quality over schedule.* Miyamoto is reported to "upend the tea table" (chabudai gaeshi): overturn near-finished work when the core is not right.

**Practices.** Prototype the verb in a bare test room (reported for *Super Mario 64*'s camera and movement work); co-design hardware and software; give each level or world a gimmick and retire it before it bores; long internal iteration with cross-discipline teams (the "Iwata Asks" interview series documents many examples).

**Evidence and outcomes.** Game & Watch (1980) reused calculator-style LCD technology; the Game Boy (1989) chose a monochrome reflective screen and outlasted colour rivals (Atari Lynx, Sega Game Gear) on battery life, price and *Tetris*. DS and Wii were mass-market successes. Counter-example: the Virtual Boy (1995) failed, often read as using technology that was *not* yet withered. On mobile, *Super Mario Run* (2016) used a one-time unlock and was widely reported to convert below expectations, while *Fire Emblem Heroes* (2017, gacha) performed strongly; *Dr. Mario World* closed in 2021.

**Apply it here.**
- Withered technology = stable engine versions, the deterministic sim-core + presentation architecture, proven libraries, and min-spec targets that include low-end Android (`technical.min_spec`). Spend the novelty budget on the design hook (`concept.hook`), not on exotic tech.
- Play first = the first build of any concept is the verb alone, in a grey box, judged at the fun checkpoint before any content or art.
- Teach through play = every FTUE step declares what it `teaches`; first-run personas from `player-simulator` get no hints; text tutorials are a smell.
- Kishōtenketsu = sequence levels as `teach → test → twist → reward` in level specs; `level-designer` owns the rhythm.

**Verify.** The exact wording of Miyamoto and Iwata remarks; the "a delayed game is eventually good" line is widely attributed to Miyamoto but its origin is disputed — do not quote it as his.

### Valve

**Beliefs.** A flat organization lets the best people choose the most valuable work (the public *Valve Handbook for New Employees*, 2012). Players do not read and do not do what designers expect, so the only reliable design tool is watching them. Ship when it is ready ("Valve Time"). Experimental methods (Valve has employed experimental psychologists, e.g. Mike Ambinder, who has given conference talks on playtesting and biometrics) belong inside game design.

**Practices.** Cross-discipline "cabal" groups designed *Half-Life* (reported); frequent playtests where designers watch silently and do not help; heatmaps and telemetry of deaths and stalls; the *Left 4 Dead* "AI Director" adjusts pacing (build-up, peak, relief) from player state; *Portal* grew out of a hired student team's project (*Narbacular Drop*), with its test-chamber teaching sequence shaped by playtests; developer-commentary tracks that explain decisions.

**Evidence and outcomes.** *Half-Life*, *Portal*, *Left 4 Dead*, *Dota 2* and Steam. Former employees have described the flat structure as creating informal hierarchies and many unfinished projects; release gaps can stretch for years.

**Apply it here.** `/arcosian:playtest-sweep` runs personas that receive no hints, and their stall points become findings with `repro` steps. Use a Director-style pacing controller for any session-based mode (see `progression-difficulty`). Valve's critics point to hidden hierarchy, so the plugin makes authority explicit: `gs.py feature next` picks work by priority and dependencies, and the `principal` arbitrates.

**Verify.** Anything about current internal structure; accounts are anecdotal.

### Blizzard Entertainment

**Beliefs.** "Gameplay first" and "commit to quality" (long-standing company values, as publicly displayed). *Easy to learn, difficult to master* (a restatement of Nolan Bushnell's arcade maxim). Take an existing genre and refine it until it is the definitive version (RTS with *Warcraft* and *StarCraft*, the MMO with *World of Warcraft*, the digital card game with *Hearthstone*). Release "when it's done".

**Practices.** Long internal iteration and a willingness to cancel late (*StarCraft: Ghost*, *Warcraft Adventures*, and *Titan*, whose cancellation led to *Overwatch*); small strike teams (*Hearthstone* was reported to start with a small team); obsessive readability (unit silhouettes, faction colours, clear spell effects); polish passes on every touched surface.

**Evidence and outcomes.** Decades of genre-defining hits. Cautionary later episodes: *Warcraft III: Reforged* (2020) backlash, and *Diablo Immortal* (2022), whose monetization drew heavy criticism and which was not released in Belgium and the Netherlands over loot-box rules (widely reported).

**Apply it here.** "Easy to learn" maps to `ftue.aha_seconds_target`; "hard to master" maps to a measurable skill ceiling (compare bot strategies in `match3_sim.py --bot greedy|random|cascade` or engine bot runs; a large spread means skill matters). Polish the touched surface (doctrine 7) before adding features. The cautionary episodes are why doctrine 8 outranks short-term revenue: a quality brand did not protect against monetization backlash.

**Verify.** Exact current value statements; internal team sizes.

### Riot Games

**Beliefs.** Be the most player-focused game company (Riot's stated aspiration); take play seriously; a competitive game is a decade-long service; community health is a design problem, not only a moderation problem.

**Practices.** A player-behaviour research group studied toxicity and built systems such as the Tribunal and honor rewards; its public talks reported that most negative incidents come from ordinary players on a bad day rather than from a small group of persistent offenders, which pushed the design toward reform and positive reinforcement, not just bans. Frequent balance patches; cosmetics-led monetization; transmedia (*Arcane*, 2021). Fast-follow capacity: *Teamfight Tactics* (2019) shipped quickly after the auto-battler trend began, then went to mobile. *Wild Rift* rebuilt League for phones with shorter matches and twin-stick controls rather than porting it.

**Evidence and outcomes.** *League of Legends* has operated since 2009; *Valorant* (2020). *Legends of Runeterra* was scaled back in 2023–24. Reported culture problems led to a 2021 class-action settlement. A Brazilian court ordered damages over League loot boxes in 2026 (see volatile facts).

**Apply it here.** For any social feature, design reporting, cooldowns and positive reinforcement up front (`multiplayer-backend`, `legal-ethics`). For genre translation to mobile, redesign session length and controls rather than porting (`mobile-ux`). Fast-follow is legitimate when the team adds a real twist (`analogy-engine`).

**Verify.** Behaviour-research percentages (often quoted, rarely sourced); match-length figures.

### Mojang

**Beliefs.** A small set of composable systemic primitives (blocks, crafting, day/night, mobs) produces endless player-made experiences. Develop in public with the community.

**Practices.** *Minecraft* was sold during its alpha (2009), effectively early access before the term existed; public development logs; tolerance of modding; later, cross-platform Bedrock edition and a mobile edition from 2011.

**Evidence and outcomes.** Microsoft acquired Mojang in 2014 for a widely reported $2.5B; *Minecraft* is one of the best-selling games ever (hundreds of millions of copies reported).

**Apply it here.** When a concept is systemic, spend the effort on a few rules that combine (`mechanics-codex` combos field) and on creation tools, not on hand-made content. Expect a long support tail; only choose this path if live-ops capacity exists (`liveops`).

**Verify.** Sales figures change; cite the latest official number.

---

## 4. Mobile free-to-play leaders

### Supercell

**Beliefs.** The best people make the best games, so organize into small, independent "cells" that own their game end to end and make their own go/kill calls; leadership's job is to support, not to direct (CEO Ilkka Paananen has described aiming to be the "least powerful CEO"). Put players first: make games that as many people as possible play for years and remember. Failure is information: most projects should die before global launch because the bar is a long-lived hit.

**Practices.** Team-level decisions on soft launch and kill; strict soft-launch metrics; publicly celebrating what was learned from killed games (the champagne-for-failures ritual is widely reported); long soft launches with radical redesigns (*Brawl Stars* soft-launched in 2017 and changed orientation and controls before its global launch in December 2018); company-wide postmortems; heavy reinvestment in live ops of existing titles.

**Evidence and outcomes.** *Hay Day* (2012), *Clash of Clans* (2012), *Boom Beach* (2014), *Clash Royale* (2016), *Brawl Stars* (2018). Cancelled or closed titles, with dates from [Wikipedia's Supercell article](https://en.wikipedia.org/wiki/Supercell_%28company%29): *Spooky Pop* (soft-launched December 2014, closed March 2015), *Smash Land* (April 2015, removed September 2015), *Rush Wars* (beta August 2019, shutdown announced November 2019), *Hay Day Pop* (beta March 2020, closed February 2021), *Clash Quest* (April 2021, closed September 2022), *Everdale* (beta August 2021, closed October 2022), *Boom Beach: Frontlines* (soft launch October 2021, closed January 2023), *Flood Rush* (beta May 2023, cancelled August 2023), *Clash Mini* (November 2021, shut down April 2024) and *Clash Heroes* (cancelled June 2024). *Squad Busters* launched globally in May 2024 and its closure was announced on 30 October 2025, with the shutdown scheduled for 2026; it was described as having mixed performance despite strong early revenue. A Tencent-led consortium bought about 81% of Supercell in June 2016, and Tencent raised its stake in that consortium to 51.2% in October 2019.

**Apply it here.**
- Every concept gets explicit `kill_criteria` before work starts; the kill decision then needs no debate.
- Agents make prototypes cheap, so the plugin can be *more* aggressive than Supercell: run `concept-tournament`, kill most concepts at the fun checkpoint, and record each kill with `/arcosian:postmortem` so the knowledge compounds.
- Cell = one feature owner plus the specialist agents it calls; the `producer` tracks ownership.

**Verify.** The killed-game dates above come from one secondary source (Wikipedia) and shutdown dates for 2026 are "scheduled"; confirm current portfolio status with Supercell's own announcements. The champagne ritual and the "least powerful CEO" remark are widely repeated in press interviews but were not found in the Wikipedia article.

### King

**Beliefs.** Casual players are the majority audience; simple rules can carry thousands of levels if each level varies the puzzle; data informs tuning at massive scale; the game is an episodic service.

**Practices.** Historically, King tested many simple games on its web portal and scaled the winners to Facebook and mobile (widely reported). The saga map shows progress and the next goal at a glance. A lives system (historically five lives refilling over time) paces sessions and creates a soft monetization point; boosters assist hard levels. Levels are tuned against pass-rate and churn funnels, with "hard" and "super hard" levels interleaved among easier ones. King has published research on human-like bots that predict level difficulty (see volatile facts) and releases new level episodes regularly.

**Evidence and outcomes.** *Candy Crush Saga* (2012) has been among top-grossing mobile games for over a decade; Activision Blizzard acquired King in 2016 for a widely reported $5.9B; King moved into Microsoft with the 2023 Activision Blizzard acquisition.

**Apply it here.** Level pipeline: generate (`procedural-generation`), verify (`puzzle_solver.py`, `match3_sim.py`), set a `difficulty_target`, then place levels in a sawtooth (`difficulty_curve.py generate --pattern sawtooth`). After launch, `difficulty_curve.py analyze` on level/attempts/wins/churned data finds churn walls. Lives and post-failure offers need the ethics checks in doctrine 8: never target post-loss offers at minors, and cap offer frequency.

**Verify.** Current lives rules and episode cadence.

### Rovio

**Beliefs and practices.** Persistence plus a strong toy: *Angry Birds* was widely reported to be Rovio's 52nd game. The core is a physics toy that is fun to fiddle with, a one-gesture input, levels lasting tens of seconds, and a three-star mastery layer for completionists. Characters became an IP.

**Evidence and outcomes.** *Angry Birds* (2009) became a global hit at a low premium price; Rovio expanded into merchandise and film, went through layoffs, listed in 2017, shifted to free-to-play sequels and spin-offs, and was acquired by Sega in 2023.

**Apply it here.** Test whether the core is a *toy* (enjoyable without goals) before adding goals. Use optional star ratings as a mastery layer that does not block progress. Lesson: an IP and merchandise do not replace a repeatable loop, and one hit is not a pipeline — build a process (`concept-lab`, `concept-tournament`) instead of betting on a brand.

### Dream Games

**Beliefs.** Casual players deserve console-grade polish and speed; ship few games and make each excellent.

**Practices.** *Royal Match* (2021), from a team with Peak Games (*Toon Blast*) heritage, emphasized fast animations, minimal friction between levels, a simple area-restoration meta, a dense calendar of events and team competitions, and heavy user-acquisition spend (reported).

**Evidence and outcomes.** Widely reported to have challenged *Candy Crush Saga* at the top of the US grossing charts in some periods of 2023–24; a large valuation was reported in 2024; follow-up *Royal Kingdom* (2024).

**Apply it here.** Treat speed as polish: measure and cut animation and transition time per move (`game-feel`, `mobile-performance`). In a saturated genre, feel and friction removal can be the differentiator; that is something an agent pipeline can measure precisely from playthrough timings.

**Verify.** Revenue rankings and valuation.

### Playrix

**Beliefs and practices.** Match-3 for a broad audience, wrapped in a narrative and decoration meta (*Gardenscapes*, *Homescapes*, also *Township* and *Fishdom*) that gives players a story reason to keep progressing; high production values; heavy user acquisition.

**Evidence and outcomes.** Long-running top-grossing casual titles. Some ads showed "pull-the-pin" puzzles that were not in the games; the UK Advertising Standards Authority ruled certain ads misleading (reported, 2020), and Playrix later added such mini-games to the products.

**Apply it here.** A meta wrapper can carry a simple core to a wider audience (`narrative-design`, `economy-design`). Ad creatives are useful product research — if a mechanic wins in creative tests, consider building it — but marketing must show the real game (doctrine 1 and doctrine 8; `marketing-ua`).

### Moon Active

**Beliefs and practices.** *Coin Master*: a slot-machine spin as the core action, village building as the main sink, attacking and raiding friends as the social hook, card collections as the long goal, regenerating spins as energy, and celebrity-led marketing.

**Evidence and outcomes.** One of the highest-grossing casual games from the late 2010s onward; it has also drawn criticism and regulatory attention in several countries for gambling-like mechanics accessible to children (reported).

**Apply it here.** Deconstruct this profile to understand social-casino-adjacent loops (`deconstruct`), but do not adopt a chance-based paid core in a game that minors can play. Doctrine 8 and `legal-ethics` govern: age gate, odds disclosure, and no paid randomness for under-18s in the jurisdictions that restrict it.

**Verify.** Specific regulatory actions by country.

### Scopely

**Beliefs and practices.** Live-ops excellence, licensed IP and a shared technology platform; growth through acquisition. *Monopoly Go!* (2023) executed a dice-roll, board, collection-album and social-event loop proven by predecessors, with a famous IP and very large marketing spend (reported).

**Evidence and outcomes.** *Monopoly Go!* was widely reported to pass $1B in revenue within its first year; Scopely acquired Niantic's games business, including *Pokémon GO*, in 2025 (reported at $3.5B); Savvy Games Group has owned Scopely since 2023.

**Apply it here.** Borrow the live-ops structure: layered events, collection albums with trading, team events (`liveops`). Do not borrow the bet: an AI studio rarely has the IP and the acquisition budget that made this execution play work.

**Verify.** Revenue milestones and deal values.

---

## 5. Asian majors and gacha

### HoYoverse (miHoYo)

**Beliefs.** Its motto is "Tech Otakus Save the World". Players on phones will embrace console-grade, anime-styled worlds if the content keeps coming; one account should follow the player across mobile, PC and console.

**Practices.** *Genshin Impact* (2020) shipped an open world on mobile, PC and console with cross-save. Its character gacha publishes odds and pity rules in game (published figures: a 0.6% base rate for the top rarity, a 1.6% consolidated rate including the guarantee, and a hard guarantee at 90 pulls; the "soft pity" ramp from roughly pull 74 is community-measured, not officially specified). Content arrives in versions on a regular multi-week cadence, with heavy investment in characters, music and multi-language voice. Follow-ups: *Honkai: Star Rail* (2023) and *Zenless Zone Zero* (2024).

**Evidence and outcomes.** Widely reported multi-billion-dollar lifetime revenue and a template many Chinese studios have since followed.

**Apply it here.** Model any pity system with `gacha_calc.py --rate R --soft-pity-start N --soft-pity-step S --hard-pity N` and publish the odds (stores require disclosure of randomized paid items; see `monetization` and `legal-ethics`). Borrow cadence discipline and transparency. Do not borrow the content scope: the production volume behind a version update is far beyond an agent-run studio.

**Verify.** Current published rates per banner type; cadence length.

### Tencent (TiMi Studio Group, Lightspeed Studios)

**Beliefs.** Proven PC and console genres can become mobile-native mass-market games if controls, session length and matchmaking are rebuilt for touch. Internal competition between studios produces the best version (often described as a "horse race" between teams, reported).

**Practices.** Genre translation: MOBA to *Honor of Kings* (TiMi, 2015); battle royale to *PUBG Mobile* (Lightspeed, 2018); *Call of Duty: Mobile* (TiMi with Activision, 2019). Large investment in touch controls (virtual sticks, contextual buttons, auto-aim and smart targeting), anti-cheat, and matchmaking that eases new players in (bot opponents in early matches are widely reported across mobile shooters). In China, regulated playtime limits and real-name checks for minors.

**Evidence and outcomes.** *Honor of Kings* has been among the top-grossing mobile games for years (see volatile facts). Tencent also embeds AI teammates in shooters such as *Peacekeeper Elite* (volatile facts).

**Apply it here.** Use the genre-translation checklist when adapting any PC/console idea: session length (cut to 1–5 minute units or make matches resumable), input count (count simultaneous touches; aim for one thumb where possible), aim assist, auto-actions, and onboarding against easier opponents (`mobile-ux`, `genre-playbooks`). If early opponents are bots, do not sell power against them, and follow store and local rules on disclosure (`legal-ethics`).

**Verify.** Internal-competition descriptions are second-hand.

### NetEase

**Beliefs and practices.** Fast-follow popular genres with high production quality and deep localization: *Onmyoji* (2016), *Knives Out* (2017) and *Identity V* (2018, asymmetric horror) found large audiences in Japan as well as China. *Eggy Party* (2022) combined a party game with user-generated levels. NetEase has added player-facing generative-AI creation tools to live games (see volatile facts).

**Apply it here.** Localization is a design decision, not a translation pass: target-market art, humour and events (`accessibility-localization`). UGC and creation tools can extend content life cheaply if moderation exists. Player-facing AI features are a differentiator only with cost, latency and safety controls (`legal-ethics`, `multiplayer-backend`).

**Verify.** AIGC usage figures come from aggregators.

---

## 6. Hybrid-casual and hypercasual

### Habby

**Beliefs.** Hypercasual-simple controls can carry midcore depth if the meta is strong: the hybrid-casual synthesis.

**Practices.** *Archero* (2019): one-thumb input where moving dodges and standing still auto-fires, plus a three-option skill pick on every level-up and a gear meta. *Survivor.io* (2022): the auto-attacking horde-survival formula adapted to portrait phones and short sessions, with heavy meta progression. *Capybara Go!* (2024): an even lower-input roguelite with auto-battles. Monetization blends IAP (gear, passes, energy) with rewarded ads.

**Evidence and outcomes.** Repeated chart hits across several years; widely studied as the reference hybrid-casual publisher. Habby Pte. Ltd. is registered in Singapore (incorporated January 2018; PitchBook lists its corporate office there), and PocketGamer.biz reported that it was formed by a core team from China's Cheetah Mobile ([PitchBook](https://pitchbook.com/profiles/company/433005-58); [Singapore registry listing](https://companieshouse.sg/habby-201801517k); [PocketGamer.biz](https://www.pocketgamer.biz/asia/profile/67777/new-mobile-publisher-habby-on-the-hunt-for-indie-games/)). Where its studios sit was not confirmed.

**Apply it here.** This is the most agent-buildable profile: one-thumb controls, three-choice upgrade picks, run lengths of 3–10 minutes, and a meta that the economy simulator can model. Start from `genre-playbooks` and check the economy with `economy_sim.py --model PATH`. Watch the ethics of energy and gear-chest monetization (doctrine 8).

### Voodoo, Homa and SayGames (the hypercasual test machine)

**Beliefs.** Marketability first: if people do not click the ad, the game does not matter. A game is a hypothesis to be tested cheaply and killed quickly.

**Practices.** Make a short video creative (sometimes before the game exists) and a minimal build; run cost-per-install (CPI) tests on social ad networks; move to retention and playtime tests only if CPI passes; iterate in days or weeks; monetize mostly with ads; publish at volume. Publishers gave external studios dashboards and SDKs to read these metrics.

**Evidence and outcomes.** Many top-download hits around 2017–2020 (for Voodoo: *Helix Jump*, *Paper.io 2*, *Hole.io*, *Aquapark.io*, *Crowd City*). After Apple's App Tracking Transparency (iOS 14.5, 2021) ad targeting and ad revenue weakened while CPIs rose, and ad-only lifetime value struggled to cover acquisition. Voodoo has publicly pivoted to hybrid-casual with a handful of launches a year (see volatile facts).

**Apply it here.** Agents can make marketability tests cheap (concept art, mock gameplay video, store-page copy from `store_metadata.py`), so use CPI-style signals as an *appeal* check in `concept-tournament`. Do not treat CPI as the whole thesis: post-2021 economics need retention depth and IAP, so every concept also needs a meta loop and a D1/D7 hypothesis in `analytics.kpi_targets`. See `schools-of-thought.md` sections 10 and 11.

**Verify.** Publisher thresholds (CPI, D1, playtime) varied by publisher and year and are not stable; do not quote old numbers as current.

---

## 7. Cautionary case: Zynga

**Beliefs and practices (as widely reported).** Measure everything and let metrics decide; grow through social-platform virality (wall posts, gift requests, notifications); move fast by following proven designs.

**Evidence and outcomes.** *FarmVille* (2009) reached enormous audiences on Facebook. Zynga was criticized for cloning; NimbleBit's 2011 open letter about *Dream Heights* and *Tiny Tower* became a well-known example. When Facebook curtailed viral channels, growth fell; the stock fell after the 2011 IPO; the 2012 acquisition of OMGPOP (*Draw Something*) was followed by a fast decline in that game's popularity. Zynga later recovered through mobile acquisitions and was acquired by Take-Two in 2022.

**Lessons for this plugin.**
1. *Channel dependence kills.* A growth loop that depends on one platform's rules is a risk (`risks` in the contract).
2. *Data without craft finds local maxima.* Metric optimization without a player-experience hypothesis drifts toward exploitation (doctrine 4).
3. *Spam destroys trust.* Social features that push players to nag friends burn the network they rely on.
4. *Cloning has a reputational cost.* Fast-follow only with a real twist and visible respect for the source (`analogy-engine`).
5. *Buying a hit is not buying retention.* A viral spike is not a loop.

---

## 8. Auteur and indie craft

### FromSoftware

**Beliefs.** Hidetaka Miyazaki's games treat difficulty as the route to accomplishment: hard but fair, with patterns that can be learned and deaths the player can attribute to their own mistakes. Story is fragmentary and environmental, so players piece it together. Miyazaki has described in interviews reading books as a child that were beyond his comprehension and filling the gaps with imagination, which he links to his ambiguous storytelling.

**Practices.** Telegraphed enemy attacks with consistent rules; checkpoints (bonfires, sites of grace) plus unlockable shortcuts that loop back after hard stretches; bounded death penalties (dropped currency can be recovered once); asynchronous social systems (player-written messages, bloodstains replaying others' deaths, summonable phantoms); interconnected level layouts.

**Evidence and outcomes.** *Demon's Souls* (2009), *Dark Souls* (2011), *Bloodborne*, *Sekiro*, *Elden Ring* (2022, reported tens of millions of copies sold) — a design lineage widely imitated ("Soulslike").

**Apply it here.** Mobile-friendly lessons: asynchronous social layers (ghost data, hints from other players) need no real-time servers (`multiplayer-backend`); every death should be attributable and teach something (`playtest` finding category); open a shortcut or checkpoint after each difficulty spike (`level-design`). Keep the death cost bounded for 1–5 minute sessions.

### thatgamecompany

**Beliefs.** Games can evoke emotions beyond "fun" (awe, tenderness, belonging) and can reach people who do not play games. Jenova Chen's graduate thesis (*Flow in Games*, USC, 2006) argued for letting players adjust challenge themselves to stay in flow.

**Practices.** *flOw* lets players dive deeper or retreat, which is player-chosen dynamic difficulty. *Journey* (2012) paired anonymous strangers with no text chat, only a musical chirp, so cooperation emerged without toxicity. *Sky: Children of the Light* (2019) brought the approach to mobile as a free-to-play social game monetized mainly through cosmetics and seasonal passes, with communication unlocked gradually through friendship (reported).

**Apply it here.** Write an emotional target into the pillars (for example "wonder within 60 seconds"). Design prosocial communication by constraint: emotes before chat, chat after mutual friendship (`multiplayer-backend`, `player-psychology`). Cosmetic-led monetization is viable for social games with strong identity expression (`monetization`).

### Playdead

**Beliefs.** Subtract until only the essential remains: no text, few verbs (move, jump, grab), one coherent aesthetic, a world that explains itself.

**Practices.** *Limbo* (2010) and *Inside* (2016): "trial and death" puzzles with checkpoints seconds apart, physics puzzles whose solutions are read from the environment, and a years-long polish of animation and transitions.

**Apply it here.** Wordless FTUE: if a step needs a text box, redesign the step (`mobile-ux`). Instant retry with checkpoints seconds apart makes failure cheap. One coherent style locked in the art bible beats rich but inconsistent assets (`art-direction`, `ai-asset-pipeline`). Borrow the restraint, not the multi-year polish schedule.

### Klei Entertainment

**Beliefs.** Players are co-designers during development; hidden information must be made visible to be fair.

**Practices.** Early access with frequent updates and public roadmaps (*Don't Starve*, *Oxygen Not Included*); *Mark of the Ninja* (2012) visualizes sound as rings and vision as cones so stealth is readable; the studio leadership has publicly discussed sustainable working hours (reported). Tencent took a majority stake in 2021, with Klei reported to keep creative independence.

**Apply it here.** Readability of hidden state (timers, threat ranges, odds) is a fairness requirement: show it (`game-feel`, `mobile-ux`). Treat soft launch as early access: publish a change log, respond visibly (`liveops`).

### Supergiant Games

**Beliefs.** A small, stable team (reported around twenty people) can make genre-leading games; narrative and systems should be one thing; sustainable work produces better work.

**Practices.** A reactive narrator in *Bastion*; in *Hades* (early access 2018, full release 2020), every death returns the player to a hub where characters react, so failure advances the story; early access used as a development partner; studio practices reported to avoid crunch. *Hades II* followed through early access to a full release in 2025.

**Apply it here.** Make failure progress something: narrative beats, meta currency, or new dialogue on each return (`narrative-design`, `progression-difficulty`). Use soft launch as a structured early access with planned content drops. Doctrine 10's human checkpoints exist partly to keep humans out of crunch: agents absorb the volume.

### Mega Crit

**Beliefs.** Good decisions need good information; balance comes from data on real runs; tools and engines should not be able to hold the studio hostage.

**Practices.** *Slay the Spire* (early access 2017, full release 2019) shows each enemy's intent for the next turn, turning combat into planning. Co-founder Anthony Giovannetti presented at GDC (2019) on metrics-driven balancing with early-access run data such as card pick and win rates. Ascension levels add stacking difficulty modifiers for players who have mastered the base game; a daily challenge provides shared seeds. After the 2023 Unity runtime-fee controversy, Mega Crit publicly moved its sequel to Godot (widely reported).

**Apply it here.** Telegraph intent wherever a decision depends on what the system will do next. Track pick rate against win rate per card, item or upgrade: a high-pick, low-win option is a trap, and a low-pick, high-win option is undervalued (`player-analytics`, `balance`). Ascension-style ladders give post-mastery depth cheaply (`progression-difficulty`). Engine and tool independence is doctrine 9.

### LocalThunk (Balatro)

**Beliefs.** One developer can make a genre-defining game by building on rules players already know and letting combinatorics do the work.

**Practices.** *Balatro* (2024, published by Playstack, built with the LÖVE framework) uses familiar poker hands, then adds jokers and modifiers whose effects multiply, so the score formula (chips × mult) produces escalating, exponential "numbers go up" moments. Heavy juice is tied to scoring: cards shake, numbers pop, sound escalates as the score climbs. Monetization is a premium price only, including on mobile (released 2024, with an Apple Arcade edition).

**Evidence and outcomes.** Multi-million sales (reported) and many awards; a widely cited example of solo-developer success.

**Apply it here.** Piggyback on known rules to cut onboarding (Rosewater's piggybacking idea; see `designer-philosophies.md`). Prefer multiplicative interactions between a modest set of modifiers to large hand-made content sets: combinatorial depth is cheap for agents to build and test (`mechanics-codex`, `economy-design`). Tie juice to the moment of growth (`game-feel`).

**Verify.** Sales numbers; joker counts.

### Team Cherry

**Beliefs.** A tiny team can reach exceptional craft if scope serves the world and movement feels perfect.

**Practices.** *Hollow Knight* (2017, a small Adelaide team, Kickstarter-funded in 2014): hand-drawn art, precise movement, and maps that must be bought from a cartographer and filled in at rest points, which makes exploration tense. *Hollow Knight: Silksong* launched in September 2025 after a long development.

**Apply it here.** Make exploration rewarding by withholding information and selling it back (`level-design`). Tight movement first (play-first again). The long development is a warning for agent studios too: craft without scope discipline expands (doctrine 5).

### ConcernedApe (Eric Barone)

**Beliefs.** Make the game you want to play, keep control, and treat players generously.

**Practices.** *Stardew Valley* (2016) was built solo over roughly four years, drawing on the *Harvest Moon* lineage. Each in-game day is a budget of time and energy spread across overlapping goal tracks (crops, friendships, mines, community bundles). Large free updates (including 1.6 in 2024) and no microtransactions; mobile ports in 2018–19.

**Evidence and outcomes.** Tens of millions of copies sold (reported) and a lasting community.

**Apply it here.** Daily loop design: three or more overlapping goal tracks with different periods so every session ends with something half-done (`progression-difficulty`, `player-psychology`). Goodwill compounds: free updates and honest monetization are a long-term growth strategy, not charity.

---

## 9. Studio rituals worth stealing

Rituals are how a doctrine survives contact with deadlines. Each row names the source, what the ritual protects, and the agent-studio equivalent with the artifact it leaves behind.

| Ritual | Source | What it protects | Agent-studio equivalent | Artifact |
|---|---|---|---|---|
| Celebrate kills and share the lessons | Supercell (widely reported) | Removes the stigma of stopping; knowledge compounds | `/arcosian:postmortem` on every killed concept or feature | Postmortem under `.gamestudio/reports/` |
| Late veto when the core is wrong ("upending the tea table") | Miyamoto (reported) | Quality of the core over schedule | `critic` may block at the fun checkpoint with written reasons; the human decides | `gs.py progress` entry |
| Silent-observer playtest | Valve | Real behaviour instead of designer assumptions | Persona runs with no hints; every stall becomes a finding with `repro` | `playtest-report.schema.json` report |
| Cross-discipline interviews | Nintendo's "Iwata Asks" | Shared reasoning across disciplines | `/arcosian:design-review` with each discipline's agent writing its rationale | Review report |
| Developer commentary | Valve | The "why" behind decisions survives staff (or session) turnover | Rationale in `comparables[].change`, feature `notes` and the concept `rationale` | `contract.json`, `features.json` |
| Grey-box verb room | Nintendo | Feel before content | Feel prototype as the first feature of any concept | Feature evidence folder |
| Run-metrics balance review | Mega Crit | Balance from real decisions, not opinions | `/arcosian:balance-pass` on pick rate vs win rate | Balance report |
| Level funnel review | King | Churn walls found per level | `difficulty_curve.py analyze --data CSV` after each content drop | Analysis report |
| Shared daily seed | Mega Crit, Spelunky | Community comparison and cheap content | Deterministic seeds from the sim-core template exposed as a daily event | Live-ops event definition |
| Public roadmap and patch notes | Klei | Trust with early players | Change log per soft-launch update; "what's new" text from `store_metadata.py` | Release notes |
| Long soft launch with a redesign budget | Supercell (*Brawl Stars*) | Learning before scale | Soft-launch tier with KPI bars and a dated kill criterion | `contract.kill_criteria` |
| Strike team for a crisis | Blizzard (reported practice) | Focus on one blocking problem | A feature with a single owner and a dedicated agent pair (for example `performance-engineer` plus `technical-artist`) | Feature entry and evidence |

---

## 10. Failure gallery: what went wrong and which guard prevents it

Outcomes below are widely reported; root causes are our reading and are labelled as such. Use the gallery to stress-test a plan: for each row, ask whether the project has the guard.

| Failure | What happened | Root cause (our reading) | Plugin guard |
|---|---|---|---|
| Virtual Boy (Nintendo, 1995) | Commercial failure | The technology was not yet mature ("withered") enough for comfort and display quality | Yokoi rule: novelty in one dimension; `lead-engineer` feasibility review; `technical.min_spec` |
| *Super Mario Run* (2016) one-time unlock | Conversion reported below expectations | Premium unlock clashed with mobile free-download expectations | Premium vs F2P table (`schools-of-thought.md` section 6); explicit `monetization_model` |
| Zynga after 2011 | Growth fell when Facebook curtailed viral channels | Dependence on one channel; spammy virality | `risks` entry for channel dependence; anti-spam social design |
| *Draw Something* (2012) | Viral spike, fast fade after acquisition | Novelty without a long-term loop | Retention hypothesis and D7 target before scaling spend |
| Hypercasual after ATT (2021 onward) | Ad-only economics stopped working for most titles | Short retention and ad-only lifetime value | Hybrid-casual synthesis: meta loop and IAP required |
| Rovio's expansion | Layoffs after rapid diversification | An IP is not a repeatable loop | Process over brand: `concept-lab`, `concept-tournament` |
| *Diablo Immortal* (2022) | Monetization backlash; not released in Belgium and the Netherlands | Monetization pressure outweighed trust; loot-box law | Doctrine 8 red lines; `compliance_preflight.py`; storefront-aware behaviour |
| Playrix ad rulings (2020, reported) | UK regulator found some ads misleading | Creatives promised a different game | Ads must show the real game (`marketing-ua`) |
| *Legends of Runeterra* | Scaled back in 2023–24 | Riot said a player-generous model did not cover its costs (reported) | Service break-even check (`schools-of-thought.md` section 5) |
| *Concord* (Sony, 2024) | Shut down within weeks of launch | Commonly cited: premium-priced hero shooter in a crowded genre without a clear hook | Earn the right to be a service; a concept `hook` is mandatory; `market-scan` |
| *Squad Busters* (Supercell, 2024) | Reported below expectations | Even the best studios miss; the cause is not public in detail | Kill criteria apply to every project, whatever the pedigree |
| Valve's flat structure (former employees' accounts) | Informal hierarchies; unfinished projects | Authority hidden rather than absent | Explicit authority: the `principal` arbitrates; `gs.py feature next` orders work |

---

## 11. Borrowing matrix: which studio to study for which project

### 11.1 By project type

| Project type | Study first | Borrow | Do not borrow |
|---|---|---|---|
| Match-3 / tile puzzle | King, Dream Games, Playrix | Level funnels and sawtooth difficulty; speed as polish; meta wrapper | Misleading creatives; post-loss offer pressure on minors |
| Hybrid-casual action roguelite | Habby, Mega Crit, Supergiant | One-thumb input; three-choice picks; intent telegraphing; failure that progresses | Gear-chest randomness sold to minors; energy walls in the first sessions |
| Hypercasual / arcade one-verb | Voodoo-era publishers, Rovio, Vlambeer (see designer file) | Marketability tests; toy-first core; 30-second levels | Ad-only economics without retention depth |
| Cozy / life-sim | ConcernedApe, thatgamecompany, Nintendo | Overlapping daily goals; prosocial constraint; teach through play | Grind disguised as coziness |
| Competitive real-time | Riot, Tencent, Supercell (*Clash Royale*, *Brawl Stars*) | Behaviour systems; genre translation to touch; long soft launch | Hidden bots sold as humans; pay-to-win |
| Collection / gacha RPG | HoYoverse, Scopely (events) | Published odds and pity; content cadence; collection albums | Content scope you cannot sustain; opaque rates |
| Premium puzzle / narrative | Playdead, Nintendo, Lucas Pope (designer file) | Wordless teaching; subtraction; one idea per level | Multi-year polish without a scope plan |
| Systemic sandbox | Mojang, Klei, RimWorld (designer file) | Composable primitives; early access with roadmap; visible hidden state | Simulating what players cannot perceive |
| Social casino-adjacent casual | Moon Active, Scopely | Event layering, collection, team events | Chance-based paid core for minors; spammy social |

### 11.2 One-line doctrine cards

| Studio | Doctrine in one line (our summary) | Rule it gives this plugin |
|---|---|---|
| Nintendo | Mature tech, fresh use; the verb must feel good alone; levels teach | Grey-box the verb first; teach, test, twist, reward level rhythm |
| Valve | Watch players silently; data and psychology inside design | Hint-free persona playtests; Director-style pacing |
| Blizzard | Gameplay first; easy to learn, hard to master; polish or cancel | Measure aha time and skill ceiling; polish touched surfaces |
| Riot | Player-focused; community health is design | Behaviour systems before social launch |
| Mojang | Few composable primitives; build in public | Systemic concepts need live-ops capacity |
| Supercell | Small cells, long-lived hits, kill most games | Pre-committed `kill_criteria`; postmortem every kill |
| King | Simple rules, endless tuned levels, data at scale | Solver plus bot plus sawtooth for every level batch |
| Rovio | Toy first; persistence; IP is not a loop | Toy test before goals |
| Dream Games | Speed and polish as differentiation | Time-per-move budget |
| Playrix | Meta wrapper widens audience | Ads must show the real game |
| Moon Active | Social-casino loops monetize strongly | Profile to deconstruct, not to copy for minors |
| Scopely | Execution, live ops and IP | Borrow event structure, not the IP bet |
| HoYoverse | Console-grade content on mobile, transparent pity | `gacha_calc.py` plus published odds |
| Tencent | Translate proven genres to touch | Genre-translation checklist |
| NetEase | Fast-follow plus deep localization plus UGC | Localization as design |
| Habby | Hypercasual controls, midcore meta | Most agent-buildable template |
| Voodoo/Homa/SayGames | Test the ad before the game | CPI as appeal signal only |
| Zynga | Metrics and virality without craft | Channel risk, anti-spam, anti-clone |
| FromSoftware | Learnable difficulty, environmental story | Every death attributable; shortcut after spikes |
| thatgamecompany | Emotion targets; prosocial constraint | Emotional pillar; emotes before chat |
| Playdead | Subtract until essential | Wordless FTUE |
| Klei | Players as co-designers; make hidden state visible | Readable timers, ranges, odds |
| Supergiant | Failure advances story; sustainable team | Make failure progress something |
| Mega Crit | Information for decisions; balance from run data | Intent telegraphing; pick rate vs win rate |
| LocalThunk | Known rules plus multiplicative combos | Piggyback rules; combinatorial depth |
| Team Cherry | Tiny team, deep craft | Exploration by withheld information; watch scope |
| ConcernedApe | Generosity and overlapping goals | Three goal tracks with different periods |

---

## 12. Volatile facts (as of Oct 2026 — verify before relying)

These are current-state facts relevant to the doctrines above. Each has a source; re-check before using them in a pitch, review or public text.

| Fact | Why it matters here | Source |
|---|---|---|
| Voodoo, the archetypal hypercasual prototype factory, tested about 1,000 prototypes a year (2024) and has pivoted to hybrid-casual with about four launches a year. | The hypercasual test-machine doctrine has been largely replaced by the hybrid-casual synthesis. | [mobilegamer.biz](https://mobilegamer.biz/voodoo-to-launch-just-four-games-per-year-after-hard-hybridcasual-pivot/); [Voodoo](https://voodoo.io/news/voodoo-s-secret-sauce-from-0-to-250m-hybridcasual-revenue-in-3-years) |
| Hybrid-casual had the largest spending jump of any mobile segment in 2025 (+17.1%, about $3.5B to $4.2B, Sensor Tower via Mobilegamer.biz). | Supports the Habby-style profile as the default for agent-built games. | [Mobilegamer.biz data digest](https://mobilegamer.biz/data-digest-sensor-towers-h1-analysis-hay-days-comeback-julys-top-games-big-krafton-numbers-and-more/) |
| Mobile game IAP grew about 1% to about $82B in 2025; in H1 2026 IAP fell about 2% and downloads about 12%. | A flat market rewards retention, live ops and craft over volume. | [Sensor Tower](https://sensortower.com/press/press-release-sensor-tower-state-of-gaming-gaming-drove-52-billion-downloads-82b-iap-revenue-on-mobile-and-12b-premium-revenue-on-steam); [Mobilegamer.biz](https://mobilegamer.biz/data-digest-sensor-towers-h1-analysis-hay-days-comeback-julys-top-games-big-krafton-numbers-and-more/) |
| *Last War*, *Honor of Kings* and *Whiteout Survival* led mobile grossing in Q1 2026; *Block Blast!* topped downloads in H1 2026. | Strategy/4X and Tencent's genre translations remain at the top; simple block puzzles dominate installs. | [Mobilegamer.biz](https://mobilegamer.biz/data-digest-sensor-towers-h1-analysis-hay-days-comeback-julys-top-games-big-krafton-numbers-and-more/) |
| King used a CNN trained on player data to predict human-like moves and estimate level difficulty for more than 1,000 new *Candy Crush Saga* levels (2018 paper); follow-up work reports estimates in under a minute versus days of human playtesting per episode. | Evidence for the King doctrine of bot-verified difficulty, which the plugin's solvers and simulators imitate. | [Gudmundsson et al. 2018](https://www.Gwern.net/doc/reinforcement-learning/imitation-learning/2018-gudmundsson.pdf); [Politecnico di Milano thesis](https://www.politesi.polimi.it/handle/10589/141799) |
| On 9 June 2026 a Brazilian court ordered Riot Games to pay damages over *League of Legends* loot boxes and to add age verification and odds disclosure (reported amounts conflict); Brazil's ECA Digital law bans loot-box sales to under-18s from March 2026. | Even player-focused studios face loot-box liability; reinforces doctrine 8. | [Sheep Esports](https://www.sheepesports.com/articles/brazil-court-orders-riot-games-to-pay-eur2-5m-over-league-of-legends-loot-boxes/en) |
| Tencent's *Peacekeeper Elite* AI Teammate is reported to cover 110M players; NetEase's *Eggy Party* AIGC tools reportedly produced 1M+ player-made items, and *Justice* added a text/voice "Dreamweaver" creation mode (April 2026). Aggregator data. | Asian majors are shipping player-facing AI features; treat figures as indicative. | [NexWorld panorama](https://nexworld.wiki/en/ai-games/ai-games-panorama-2026/) |
