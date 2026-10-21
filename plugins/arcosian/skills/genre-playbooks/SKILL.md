---
name: genre-playbooks
description: "Genre playbooks for games on any platform: loops, session profile, signature mechanics, monetization, KPIs, production scope, agent-buildability and P0 features per subgenre - mobile genres plus shooters, action-adventure, platformers, survival, simulation, MMO and live service, racing, sports, fighting, horror, narrative, PC strategy and deckbuilders. Use when choosing or fusing a genre or scoping a slice."
when_to_use: Picking or fusing a genre, writing contract.meta.genre/subgenre, sizing a slice, or sanity-checking a concept against genre norms.
---

# Genre Playbooks

A genre is a contract with the player. It sets which verbs they expect, how long a session lasts, how the game makes money and what "good" feels like in the first 90 seconds. This skill holds one playbook per subgenre, from mobile casual to PC and console shooters, sims, MMOs and strategy, all in the same 14-part format (PC and console files add platform notes), plus the procedures a principal designer uses to pick a genre, fuse two of them and turn the result into a scoped vertical slice.

## What this skill gives you

- **Playbooks for dozens of subgenres** in a fixed format: definition and player fantasy, core loop, meta loops, session profile, signature mechanics, monetization mix, KPI expectations, retention drivers, production scope, reference titles, success and failure factors, innovation vectors, an **agent-buildability score (1–5)** and a **P0 starter feature list** with acceptance criteria.
- **A genre selection procedure** that scores candidates on audience motivation, monetization fit, team and agent capacity, and market saturation, with a worked example.
- **A comparison table of every genre** covering session length, monetization, production scope and agent-buildability.
- **Genre-fusion guidance**: proven pairings, a compatibility checklist and the failure patterns to watch for.
- **Direct mappings into the ontology**: `contract.json` fields, the `concept.schema.json` scores, `features.json` seeds, and the simulators that verify each genre.

## Core models

**1. Three-layer anatomy.** Every playbook breaks a game into three layers. The core loop runs in seconds and is the verb the player repeats. The meta loop runs from a session to a few days and gives the core a reason (progress, collection, decoration, power). The wrapper runs weekly or seasonally and covers live-ops, social systems and events. Genres mostly differ in their core. Commercial success mostly differs in the meta and the wrapper. Copying a winner's meta without a core that earns it is the most common way a clone fails.

**2. Expectation budget.** Players of a genre arrive with fixed expectations about controls, orientation, session length, fail states and monetization. Break **one** expectation on purpose: that is the hook. Breaking three makes the game unreadable in the store and in ads. Write the broken expectation into `concept.hook`.

**3. Session economics.** Daily minutes = session length × sessions per day. Monetization capacity follows from this:
- Ad-led games need many sessions with natural breaks, because breaks give ad slots.
- IAP-led games need a fail state or timer at a high-intent moment, such as "+5 moves" or "finish now".
- Idle games convert absence into value through offline earnings, so a short session is not a weakness for them.

Choose the session shape first, then the monetization model that fits it.

**4. The marketability, retention, monetization triangle.** Most genres are strong on two corners at best.
- Hypercasual is marketability-first: cheap installs, ad revenue, weak retention.
- Puzzle and solitaire are retention-first: long tails and older audiences.
- 4X and gacha RPG are monetization-first: deep spenders, but very expensive installs.

Hybrid-casual tries to keep hypercasual's marketability and add retention and IAP depth through a meta layer. Hybrid-casual spending grew 17.1% in 2025 [V3].

**5. Content treadmill ratio.** Let R = content produced per week ÷ content consumed per week by your most engaged decile. If R < 1 for a level-based game, the best players hit the end and churn. Three things raise R: procedural or systemic depth (roguelites, logic puzzles with generators), user-generated content, and solver- or bot-verified generators. Hand-authored-only genres such as hidden object, narrative and home design have R < 1 by default and need large content teams.

**6. Genre lifecycle.** A genre moves through four stages. Emergence is a hypercasual or indie prototype; hybridization adds a meta; consolidation sets in once incumbents have years of live-ops and content; renewal comes from a new core twist or platform shift. Enter at emergence with speed. Enter at consolidation only with a sharp hook plus a cheaper production method, never by matching the incumbent feature by feature.

**7. Agent-buildability model.** This is how well an AI-agent pipeline can build **and verify** a genre to the five-gate standard (see `qa-testing`). Score six factors from 1 to 5, then combine them:

| Factor | 5 means | 1 means | Weight |
|---|---|---|---|
| V: verifiability | Deterministic, discrete state; solvers or bots can verify win rates and softlocks headlessly | Outcome depends on feel, human judgment or emergent multiplayer | 0.30 |
| T: timing tolerance | Turn-based or untimed input | Frame-precise real-time input | 0.20 |
| A: asset scope | Few, small 2D assets that style-lock well | Many hero characters, rigs, 3D scenes, bespoke animation | 0.15 |
| C: content verifiability | Content can be generated and checked by a solver or simulator | Handcrafted content judged by taste | 0.15 |
| B: backend | Offline or single-player | Real-time multiplayer and server authority | 0.10 |
| F: feel dependence | Satisfaction comes from systems | Satisfaction comes from moment-to-moment feel | 0.10 |

`AB = round(0.30V + 0.20T + 0.15A + 0.15C + 0.10B + 0.10F)`; `concept.scores.agent_buildability` (1–10) = 2 × AB.

Two pieces of evidence anchor the scale. Agents and VLM testers do best in turn-based, puzzle and UI-heavy games, and fast timing-critical play is a known weak spot [V8]. On a 140-task Godot benchmark the best agent scored 41.46% [V9], so content completeness and feedback are where agent builds fall short.

**8. Region changes the monetization answer.** In Jan–May 2026, ads were 70.3% of game revenue in India but 22.1% in the US. In mature markets such as the US, Canada, Korea and Japan, IAP was 77–90% of revenue [V4]. Choose the genre and the storefront list together.

**9. Retention anchors (all genres).**
- Per-game medians from GameAnalytics data, via secondary sources: about 22% D1, under 4% D7 and 0.7–0.8% D30. The top 1% reach 64–68% D1 and 13–15% D30 [V1].
- Practitioner viability screens: 25–30% D1, 10–15% D7, 3–6% D30 [V2].
- D7/D1 below 0.30 points to an FTUE problem; 0.30–0.44 points to weak engagement on days 2–5 [V5].
- If the aha moment takes longer than about 90 seconds, a significant share of players never return [V6].

Genre-specific benchmarks are thin and often contradict each other. The playbooks quote ranges only where a source exists and otherwise say "qualitative".

## Decision procedures

### A. Genre selection procedure

Run this before `concept-lab` generates concepts, or use it to audit a genre the user has already chosen.

1. **Fix the hard constraints** and write them down:
   - Minimum audience age. Under 13 forces the kids rules in `legal-ethics`: no behavioural ads and no paid random items.
   - Platforms and orientation.
   - Storefront countries (they set the ads vs IAP mix [V4]).
   - Team size, calendar time and art capability (2D only? 3D? rigging?).
   - Backend appetite (offline, async or real-time).
   - Paid UA budget, if any.
2. **Map audience motivations.** Use Quantic Foundry's Gamer Motivation Model (Nick Yee and colleagues). Its six clusters are Action, Social, Mastery, Achievement, Immersion and Creativity, each split into two motivations. Pick the top two motivations for the target segment and list the genres that serve them:

| Top motivations | Genres that serve them |
|---|---|
| Mastery: challenge + strategy | logic, block, match-3 hard modes, roguelite, tower defense, 4X, PvP |
| Achievement: completion + power | merge-2, idle and AFK RPG, collection RPG, survivor-like meta, farming |
| Creativity: design + discovery | home design, life sim, sandbox and tycoon, physics puzzles, merge discovery |
| Immersion: story + fantasy | narrative and visual novel, hidden object, renovation metas, RPG |
| Social: community + competition | PvP, party, social casino, word and trivia async PvP, team events |
| Action: excitement + destruction | arcade, runner, survivor-like, shooters, io games |

3. **Check monetization fit.**
   - Ad-led genres (hypercasual, block, sort, logic, solitaire, trivia, arcade) need high volume and many natural breaks.
   - IAP-led genres (match-3, merge, RPG, strategy, farming, casino) need a high-intent spend moment and a long-lived economy.
   - Hybrid genres need both.
   - Eliminate any genre whose spend moment clashes with your ethics rules (`monetization`, `legal-ethics`).
4. **Check capacity fit.**
   - Compute AB (Core model 7) and read off production scope from the comparison table.
   - Reject a genre if scope × 1.5 is more than your calendar. First projects always slip.
   - Reject a genre if its AB is 2 or lower and you have no human specialist for the factor that drags it down (feel, 3D, netcode).
5. **Check market saturation** with `market-scan` / `market-intel`. Score 1 to 5 where 5 is wide open:
   - Top-chart concentration: are the top 10 in this subgenre more than 3 years old with deep live-ops? Lower the score.
   - Rising new entrants in the last 6–12 months: raise the score.
   - Creative fatigue in ad libraries: lower the score.
   - An open innovation vector from the playbook: raise the score.
6. **Score and rank.** Score each candidate from 1 to 5 on each criterion:

   `Fit = 0.25 × motivation + 0.20 × monetization + 0.20 × capacity (AB, scope) + 0.20 × market (saturation, growth) + 0.15 × innovation headroom`

   Keep the top 2–3 candidates for `concept-lab`.
7. **Validate before you commit.**
   - Ad-led genres: run a marketability test with ad creatives or playables before full production.
   - All genres: build the core loop and prove aha within 90 seconds in a bot-measured FTUE [V6].
   - Puzzle genres: prove the bots or solvers can generate and verify 20 levels.
   - Write kill criteria into `contract.kill_criteria`.

**Worked example.** The team is a solo developer plus agents, with 6 months to soft launch. Scope values come from the comparison table in section B. Applying the 1.5× rule from step 4 to the low end of each playbook's calendar, merge-2 (9 months) and match-3 (12 months) fail it and stay in the table only to show the scoring, while screw/sort jam (3–4 months) and tile-match (4 months) pass. The audience is women aged 30–55 in the US and EU. Motivations are completion and challenge. Monetization is hybrid with an IAP lean. The art capability is 2D only.

| Candidate | Motivation | Monetization | Capacity | Market | Innovation | Fit |
|---|---|---|---|---|---|---|
| Merge-2 + renovation story | 5 | 5 | 3 (AB 4, scope M–L at 9–15 months, many item sprites) | 2 (consolidated) | 3 | 3.70 |
| Screw/sort jam + light decor meta | 4 | 4 | 4 (AB 4, scope S–M at 3–6 months) | 3 | 3 | 3.65 |
| Tile-match (triple) + collection album | 4 | 4 | 5 (AB 5, scope M at 4–12 months, so the low end) | 3 | 3 | 3.85 |
| Match-3 + renovation | 5 | 5 | 2 (scope L) | 1 | 2 | 3.15 |

The pick is tile-match plus a collection album, with screw jam as the fallback. Kill criterion: if the bot-verified 30-level slice cannot reach a 90-second aha and D1 ≥ 30% in a soft test, switch to the fallback.

### B. Genre comparison table

Every row quotes its playbook file's own per-subgenre session profile, soft-launch scope estimate and agent-buildability score (AB), so the table and the files cannot disagree. When a file gives variants (a text and an avatar life sim, a PvE and a PvP tower defense) the row shows both, and when one row stands for several subgenres it shows the range. Session and scope figures are **estimates from practitioner judgment, not sourced benchmarks**. Scope scale (people × time to soft launch):
- **S**: 1–3 people (plus agents), 2–6 months
- **M**: 4–10 people, 6–12 months
- **L**: 10–30 people, 12–24 months
- **XL**: 30+ people, 24+ months

The letter in each Scope cell bands the playbook's own estimate, quoted in brackets, by person-months (people × months): S below 24, M 24–120, L 120–720, XL above 720. The midpoint of the playbook's team and month ranges is banded, and two letters appear when it lies within 25 % of a boundary. Where a file quotes no months the letter uses team size alone. Re-band the bracketed figures if your team differs.

| Genre / subgenre | File | Session (playbook estimate) | Primary monetization | Scope: soft-launch team and calendar (playbook estimate) | AB |
|---|---|---|---|---|---|
| Match-3 (swap) | puzzle | 3–10 min, 3–6×/day (levels 1–3 min) | IAP (moves, boosters, pass) + rewarded | L (10–25 people, 12–18 mo) | 5 |
| Blast / collapse | puzzle | 3–10 min, 3–6×/day (levels shorter than match-3) | IAP + rewarded | L (same team as match-3) | 5 |
| Merge-2 (board + orders) | puzzle | 5–15 min, 3–8×/day (energy-gated) | IAP (energy, bundles) | M–L (6–15 people, 9–15 mo) | 4 |
| Sort / jam | puzzle | levels 1–3 min, several per session, many short sessions a day | Ads + no-ads IAP, light IAP | S (2–5 people, 3–6 mo) | 5 |
| Block puzzle | puzzle | endless runs 3–15 min, adventure levels 1–3 min, many sessions a day | Ads (interstitial + rewarded) | S (2–5 people, 3–6 mo) | 5 |
| Screw / pin puzzles | puzzle | levels 1–3 min, many short sessions | Ads + light IAP | S–M (3–6 people, 4–8 mo) | 3 |
| Word | puzzle | 5–15 min, 2–4×/day | Ads + hints IAP | S–M (2–6 people, 4–8 mo, plus about 1 linguist per extra locale) | 4 |
| Trivia | puzzle | 3–10 min, several sessions a day | Ads + IAP (lives, cosmetics) | S–M (3–8 people incl. editors, 4–9 mo) | 3 |
| Solitaire / mahjong / tile-match | puzzle | 5–20 min | Ads + IAP (levels mode) | M (3–10 people, 4–12 mo) | 5 |
| Hidden object | puzzle | 5–15 min, 2–5×/day (energy-gated) | IAP (energy, hints) | L (10–25 people, 12–18 mo) | 2 |
| Physics puzzle | puzzle | 2–10 min (levels 30–120 s, many retries) | Ads / premium | M (4–10 people, 6–12 mo) | 3 |
| Logic (nonogram, sudoku …) | puzzle | 5–20 min per puzzle, daily ritual | Ads + premium or subscription | S (2–5 people, 3–6 mo) | 5 |
| Hypercasual archetypes (stack, runner, io, cut/slice, draw, idle-arcade) | hyper-hybrid-casual | runs, rounds or matches of 15 s–3 min; sessions 3–15 min, many a day | Ads (interstitial, rewarded, banner; io adds skins) | S (test build 1–5 people, 2 weeks–3 mo; io with real multiplayer 4–8 people, several months) | 3–4 (stack, runner, idle-arcade 4; io, cut/slice, draw 3) |
| Runner + meta | hyper-hybrid-casual | 5–15 min, 3–6×/day (runs 30–60 s) | Ads + IAP (upgrades, no-ads, pass) | M (6–15 people, 6–12 mo) | 4 |
| Arcade idle | hyper-hybrid-casual | 5–15 min, 3–6×/day (offline earnings drive returns) | Rewarded ads + IAP | M (6–15 people, 6–12 mo) | 4 |
| Casual survivor-like | hyper-hybrid-casual | runs 5–15 min, 2–5×/day (energy-paced) | IAP (gear, energy, pass) + rewarded | L (10–25 people, 9–15 mo) | 3 |
| Puzzle + RPG | hyper-hybrid-casual | 5–15 min, several sessions a day, guild-event spikes | IAP (heroes, gacha) + pass | L (15–30 people, 12–24 mo) | 4 |
| Idle clicker | idle-tycoon-sim | 1–5 min check-ins, many a day, plus offline progress | Rewarded ads + IAP (multipliers) | S (2–6 people, 3–8 mo) | 5 |
| Idle / AFK RPG (hero-gacha) | idle-tycoon-sim | 2–10 min several times a day, plus longer event sessions | IAP (gacha, pass) + rewarded | L (20–40 people, 12–24 mo) | 3 |
| Tycoon | idle-tycoon-sim | 3–10 min several times a day (idle tycoon); 10–30 min (sim tycoon) | Rewarded + IAP | M (4–12 people, 6–12 mo; more for a sim tycoon) | 4 |
| Farming | idle-tycoon-sim | 5–15 min, 3–6 check-ins a day | IAP (premium currency, speed-ups) | L (15–30 people, 12–24 mo) | 3 |
| Life sim | idle-tycoon-sim | 5–20 min (text sims: short bursts) | IAP (cosmetics, content) | text sim: S–M (3–8 people); 3D avatar sim: L–XL (30+ people, 18–30 mo) | 2 (avatar sim); 4 (text sim) |
| Home design | idle-tycoon-sim | 5–15 min | IAP (items, currency) | L (15–30 people, 12–24 mo) | 2 |
| Restaurant / time management | idle-tycoon-sim | levels 1–2 min, sessions 3–10 min | IAP (upgrades, boosters) + rewarded | M (5–15 people, 8–14 mo) | 4 |
| Endless runner | action-arcade-roguelite | runs 1–4 min, sessions 2–6 min, many a day | Ads + IAP (characters, pass) | M–L (8–20 people, 9–15 mo) | 3 |
| Arcade (score attack) | action-arcade-roguelite | runs 10 s–3 min, sessions 1–5 min, many a day | Ads / premium | S (1–4 people, 1–4 mo) | 4 |
| Platformer | action-arcade-roguelite | levels 1–5 min, sessions 5–20 min | Premium / ads | M (4–12 people, 9–18 mo) | 2 |
| Survivor-like / bullet heaven | action-arcade-roguelite | runs 15–30 min in the premium form (shorter modes on mobile) | Premium or IAP + rewarded | M (3–10 people, 6–12 mo) | 3 |
| Roguelite action | action-arcade-roguelite | runs 10–30 min (chapter runs 5–10 min) | Premium or IAP | L (6–20 people, 12–24 mo) | 2 |
| Casual shooter | action-arcade-roguelite | levels 15–60 s, sessions 2–8 min | Ads + IAP (weapons) | S–M (3–8 people, 3–9 mo) | 3 |
| Archery | action-arcade-roguelite | matches 1–4 min, sessions 3–10 min | IAP + ads (bows, cosmetics) | M (3–10 people, 4–10 mo) | 4 |
| Top-down shooter / shmup | action-arcade-roguelite | stages 2–5 min, sessions 5–15 min | IAP / premium | M (4–12 people, 6–14 mo) | 3 |
| Hero collector / squad RPG | rpg-gacha | 3–8 sessions a day of 2–10 min, plus 20–60 min planning or raid sessions | Banner gacha, monthly card, pass | XL (global launch 30–100+ people, 2–3+ years; 2D slice 4–8 people, 6–9 mo) | 4 |
| Gacha ARPG / open world | rpg-gacha | 10–20 min daily check-in, 1–3 h on patch days | Banner gacha, monthly card | M–L for an indie hub (6–12 people, 12–24 mo); competitive titles need hundreds of people, so XL | 1 |
| Idle RPG (systems-first: prestige, equipment rolls) | rpg-gacha | 6–12 sessions a day of 0.5–3 min, plus 10–20 min optimization | Rewarded ads + IAP | S (soft-launch slice 2–6 people, 3–6 mo) | 5 |
| Turn-based JRPG | rpg-gacha | premium 20–60 min; F2P 10–20 min daily | Premium or F2P gacha | L (indie pixel-art 3–10 people, 2–4 years); F2P 3D with 100+ people is XL | 3 |
| Mobile MMORPG | rpg-gacha | hours of auto-play plus check-ins | VIP, stat-bearing gacha, enhancement | XL (100–500+ people, 3–5 years) | 1 |
| 4X / SLG | strategy | 8–20 check-ins a day of 1–5 min, plus war windows | Deep IAP, VIP, bundles, speed-ups | XL (50–200+ people, 2–3 years) | 2 |
| Base-builder with async raiding | strategy | 4–10 sessions a day of 2–6 min | Builders, speed-ups, season pass | L (10–40 people, 18–36 mo) | 3 |
| Tower defense | strategy | 3–10 min levels (premium 20–40 min; PvP merge-TD 2–5 min) | Premium or F2P hybrid | M–L (3–15 people, 9–24 mo) | 5 (PvE); 4 (PvP merge-TD) |
| Real-time card battler / RTS-lite | strategy | 3–4 min matches, 3–10 per session | Card progression, pass, cosmetics | L–XL (15–50 people, 2–3 years) | 3 |
| Auto-battler | strategy | async ghosts 10–20 min; real-time 8-player lobbies 25–40 min | Cosmetics, packs, pass | indie async: M (2–6 people, 9–18 mo); large live title: L–XL (20–60+ people) | 4 |
| Turn-based tactics | strategy | 5–20 min missions (premium 30–60 min) | Premium or F2P gacha | L (indie 3–12 people, 1.5–3 years) | 4 |
| MOBA | competitive-pvp | 10–20 min matches, 1–4 per session | Skins, heroes, pass | XL (100–300+ people, 3+ years) | 1 |
| Battle royale | competitive-pvp | 10–30 min matches | Pass, cosmetics, crates | XL (200+ people at incumbent scale) | 1 |
| Hero shooter | competitive-pvp | 3–10 min matches, 3–8 per session | Heroes, skins, pass | XL (40–150 people, 2–4 years) | 1 |
| Brawler | competitive-pvp | 2–3 min matches, 3–15 per session | Pass, skins, unlock acceleration | XL (20–60 people, 2–3 years) | 2 |
| CCG / card games | competitive-pvp | 3–10 min matches, 2–6 per session, plus pack and deckbuilding sessions | Packs or variants, pass | XL (20–80 people, 2–3 years) | 4 |
| Competitive sports | competitive-pvp | 2–10 min matches, or 1–3 min arcade duels | Ultimate-team packs, pass | arcade 1v1 physics: L (8–25 people, 12–24 mo); licensed sims: XL (100+ people) | 2 (arcade 1v1 physics 3) |
| Racing | competitive-pvp | 1–3 min races, 5–20 min sessions | Car packs, upgrades, pass | 2D physics racer: M (3–15 people, 9–18 mo); 3D arcade racing: XL (60–200 people) | 3 for ghost racing (2D physics racer 4; real-time 3D multiplayer 2) |
| Social casino / slots | social-casino-party | 5–20 min sessions, several times a day | Coin packs, VIP, piggy bank | L–XL at operator scale (30–150+ people); a small team's 5–10 machine slice takes 6–12 mo | 4 |
| Coin Master-likes | social-casino-party | 2–5 min bursts, several times a day | Spins, chests, event offers | L–XL (20–80 people); a small team's slice with 3 villages takes 6–9 mo | 4 |
| Board-game casual (Monopoly Go-style) | social-casino-party | 2–10 min bursts, several times a day | Dice, event and album offers | XL at top scale (50–200 people); a small team's slice with 2 boards takes 6–9 mo | 4 |
| Party / social deduction | social-casino-party | 10–20 min lobbies made of 1–5 min rounds | Cosmetics, pass, ads | M for a small team (3–10 people, 9–18 mo); UGC party collections need 30+ people | 2 |
| Bingo | social-casino-party | 2–5 min rounds, several per session | Credits and power-ups, VIP | L–XL (10–40 people); a 3-room slice takes 4–8 mo | 4 |
| Casual sports (golf, pool) | social-casino-party | 1–5 min matches, 3–10 per session | Chests, equipment, coins | pool: M (3–10 people, 6–12 mo); golf: L (10–30 people, 12–24 mo) | 3 (2D pool 4) |
| Interactive story / visual novel | narrative-rhythm-edu-kids | 5–15 min chapters, 1–3 a day when ticket-gated | Premium choices, tickets, VIP, premium | M–L (small studio of 5–30 people runs several series; premium narrative game 3–10 people, 1–3 years) | 4 |
| Rhythm | narrative-rhythm-edu-kids | songs 1.5–3 min, sessions 10–30 min | Song packs, subscription, ads, idol gacha | indie: S–M (2–8 people); idol rhythm gacha: XL (50+ people) | 3 |
| Educational | narrative-rhythm-edu-kids | 5–15 min a day (classroom blocks 20–40 min) | Subscription, school licences, premium | M (3–15 people, 9–18 mo) | 3 |
| Kids (COPPA constraints) | narrative-rhythm-edu-kids | 5–20 min, parent-managed, often offline | Premium, subscription, unlock packs (no behavioural ads for kids) | M–L (4–20 people, 9–18 mo) | 3 |
| Fitness / location-based | narrative-rhythm-edu-kids | outdoor sessions 5–60 min plus passive tracking | Items, event tickets, subscription, sponsored places | L–XL (20–100+ people); fitness audio-story games 5–15 people | 2 |
| Cozy | narrative-rhythm-edu-kids | 5–20 min daily ritual, plus optional long creative sessions | Premium, subscription platforms, cosmetics | M–L (3–20 people, 12–24 mo) | 4 |

AB ranges by file: puzzle 2–5; hyper-hybrid-casual 3–4; idle-tycoon-sim 2–5; action-arcade-roguelite 2–4; rpg-gacha 1–5; strategy 2–5; competitive-pvp 1–4; social-casino-party 2–4; narrative-rhythm-edu-kids 2–4. Each file's own Contents table is the authority for its rows.

Notes on rows where two playbooks overlap or the tooling has limits:
- **Idle RPGs appear twice on purpose.** `idle-tycoon-sim.md` §2 scores the hero-gacha AFK RPG at 3 because hero art, animation and VFX volume dominate. `rpg-gacha.md` §3 scores the systems-first idle RPG (prestige layers, equipment rolls, lighter hero collection) at 5.
- **Blast / collapse is not covered by `match3_sim.py`.** The simulator implements swap rules only and rejects any layout type other than `match3`. A blast level needs its own simulator and bots (`references/puzzle.md` §2).

### C. Genre fusion procedure

Most mobile hits of the last decade are fusions. A proven core is paired with a meta from another genre. The rules:

1. **One genre owns the core verb.** The second genre provides the meta, the wrapper or a mode. Two competing cores ("half a match-3 and half a 4X") work only when they alternate as clearly separate modes and each mode stands on its own.
2. **Bridge currency.** The meta must consume what the core produces (stars, coins, materials) so every core session moves the meta forward.
3. **Bounded power bridge.** If meta progress makes the core easier (hero power, upgrades), cap the effect. For example, upgrades can shift the bot win rate by at most 10–15 points, and level difficulty is re-simulated with expected meta power. Otherwise skill stops mattering, or the curve has to spike to compensate.
4. **Session alignment.** The meta action must fit inside the core's session (a 30-second decorate step after a 2-minute level). It must not demand a different kind of session.
5. **Cognitive-load alternation.** Pair a high-load core with a low-load meta, or the other way round. A puzzle core with a decorate meta works. A puzzle core with a 4X meta loads the player twice and fits mostly deep-spending audiences.
6. **Audience overlap.** Both genres' audiences should overlap on at least one top motivation. Otherwise the ads attract players the meta repels.
7. **FTUE order.** Teach the core first. Reveal the meta within the first session, ideally before the first fail.
8. **One art direction.** Both layers use one style bible (`art-direction`).

**Proven pairings.**

| Core | + Meta / wrapper | Examples | Why it works |
|---|---|---|---|
| Match-3 / blast | Renovation + narrative | Homescapes, Gardenscapes, Royal Match | Low-load meta gives a progress fantasy that does not depend on skill |
| Match-3 | Hero collection RPG battles | Puzzle & Dragons, Empires & Puzzles, Puzzle Quest | Puzzle skill becomes combat power; adds gacha depth |
| Merge-2 | Renovation story + orders | Merge Mansion, Travel Town | Order boards turn open-ended merging into goals |
| Solitaire (TriPeaks) | Farming / collection meta | Solitaire Grand Harvest | Brings an older audience into a long-lived economy |
| Survivor-like | Gear, talents, chapters | Survivor!.io | Short runs plus permanent power growth |
| Runner (crowd, gates) | Upgrades + base building | Hybrid runner pattern | Hypercasual CPI with an IAP tail |
| Idle arcade | Tycoon expansion + managers | My Perfect Hotel | The walk-and-carry verb, then automation |
| Poker hands | Roguelike deckbuilding | Balatro | A familiar rule set made exciting by build-crafting |
| Match-3 | 4X base and alliances | puzzle-plus-4X hybrids | A low-friction entry into a high-ARPU wrapper |

**Fusion red flags.** The meta lets players skip the core (for example, buying through levels). The meta needs a different orientation or control scheme. The two layers use different currencies with no exchange. The meta's best players are not the core's best players. The meta adds more than 30 seconds of UI before the first core action.

### D. From playbook to contract and slice

1. Copy the playbook's core and meta loops into `contract.loops` (with `type` and `period`) and its session profile into `meta.session_length_target_sec`.
2. Turn the signature mechanics into `contract.mechanics[]` with `category` taken from the mapping table below, and add parameters from the playbook tables.
3. Set `meta.monetization_model` and the `monetization` block from the typical mix, then apply the `monetization` ethics rules.
4. Set `analytics.kpi_targets` from Core model 9. Use genre ranges only where the playbook cites them.
5. Seed `features.json` from the starter feature list, using one `gs.py feature add` call per item:
   ```
   python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py feature add --id F001 --title "Swap and match resolution" --area gameplay --priority P0 --accept "Only swaps that create a match are accepted"
   ```
6. Put every item outside the starter list into `scope.should` or `scope.wont`. The slice is the core loop, one meta step, the fail and retry flow, one monetization touchpoint, analytics and perf. Nothing more.

**Mechanic labels used in the playbooks, mapped to `mechanics-codex`.** The playbooks tag signature mechanics with descriptive labels. They are not schema values. The puzzle, hyper-hybrid-casual, idle-tycoon-sim and action-arcade-roguelite files use 26 hyphenated labels (for example `cascade-gravity`), and the five companion files (rpg-gacha, strategy, competitive-pvp, social-casino-party, narrative-rhythm-edu-kids) use shorter labels joined by `&` (for example `collection & randomness`). Both vocabularies appear in the first column. The `category` column is the vocabulary that `mechanic-card.schema.json` and `contract.mechanics[].category` suggest (see `mechanics-codex`, procedure E); the last column gives the codex file number and example entry IDs. If a label has no matching entry, write a project card. If the codex and this table disagree, the codex wins.

| Playbook label | `category` | Codex file and example IDs |
|---|---|---|
| matching, cascade-gravity | `match` | 03 `match3-swap`, `blast-collapse`, `special-pieces`, `triple-match-tray`; 07 `assisted-refill` |
| merging | `merge` | 03 `merge`; 09 `merge-board`, `merge-world` |
| sorting | `sort` | 03 `sort-puzzle`, `screw-out` |
| spatial-packing | `placement` | 03 `block-placement`, `line-clear`, `packing-puzzle` |
| deduction-constraint, search-observation, word-language, knowledge | `puzzle` | 03 `sokoban`, `nonogram`, `sudoku-variants`, `hidden-object`, `word-formation`; 10 `deduction`. Trivia has no codex entry: write a project card |
| physics, path-drawing | `physics` | 01 `physics-stacking`, `ragdoll`, `physics-vehicle`, `draw-a-path`; 03 `physics-puzzle` |
| timing, rhythm & timing | `timing` | 01 `rhythm-timing`, `hold-release`, `one-tap-impulse`; 02 `parry` |
| aiming-trajectory | `aiming` | 01 `slingshot-aim-release`, `trajectory-ballistics`, `flick`; 11 `aim-stick`, `drag-aim-scheme` |
| movement-dodging, exploration & traversal | `movement` | 01 `jump`, `dash`, `slide`, `auto-run-lanes`; 02 `dodge-iframes`. For exploration (the codex labels it separately, and the suggested vocabulary has no exploration value) see 10 `fog-of-war`, `map-reveal`, `ability-gating` |
| auto-combat, combat | `combat` | 02 `auto-attack`, `auto-aim-survivors`, `auto-battle-squad`, `damage-model`, `boss-encounters` |
| build-crafting, build-craft | `construction` for building and crafting; `progression` for character builds | 09 `recipe-crafting`, `hq-gated-building`, `city-zoning`; 05 `talent-tree`; 02 `projectile-upgrades` |
| customization | `construction` | 09 `free-placement-decor`, `design-challenge`; 12 `cosmetic-shop` |
| collection, collection & randomness | `collection`, plus `chance` for the random part | 09 `collection-log`, `creature-collection`, `set-bonuses`; 05 `collections-albums`; 07 `duplicate-protection` |
| generators-timers, production-chains, time & energy | `resource` | 04 `idle-generators`, `crafting-chains`, `production-bottlenecks`; 08 `energy-stamina`, `build-timers-and-skips`, `offline-progress` |
| economy-flow, economy & resources | `economy` | 04 `currency-architecture`, `gold-sinks`, `converters-exchange`, `storage-caps` |
| progression-unlocks, progression & upgrade, learning & mastery | `progression` | 05 `unlock-schedule`, `xp-levels`, `hero-ascension`, `gear-rarity`, `mastery-tracks`; 08 `content-drip` |
| randomness-loot, chance & randomness | `chance` | 07 `weighted-rng`, `loot-tables`, `pity-timers`, `gacha-banners`, `dice`, `slot-spin` |
| social-coop, competition, social & competition | `social` | 06 `clans-guilds`, `co-op-events`, `gifting-help`, `leaderboards`, `matchmaking-rating`, `leagues-divisions` |
| narrative-choice, narrative & relationship | `narrative` | 10 `dialogue-choice`, `branching-narrative`, `storylets`, `relationship-meters` |
| live events | `progression` | 08 `limited-time-events`, `appointment-mechanics`; 05 `seasonal-ladder`, `pass-tracks`; 06 `tournaments`, `co-op-events` |
| UX automation | `combat` for auto-battle, otherwise a project value such as `control` | 11 `auto-play`, `idle-input`; 02 `auto-battle-squad` |

## Mobile specifics

- **Orientation follows the genre.** Puzzle, idle, merge, word, solitaire and most hybrid-casual games are portrait and one-handed: controls sit in the bottom 40% of the screen and taps are the main input. Platformers, top-down shooters and many RPG battles are landscape and two-handed. Make the choice early. It changes every UI asset.
- **Interruptibility.** A good mobile genre survives a phone call mid-level. Puzzle and idle games auto-save every move. Real-time action needs pause on focus loss and a resume countdown. Real-time PvP cannot pause, which is one reason it suits fewer mobile play contexts.
- **Session fit.** Give players a natural stopping point every 1–5 minutes (level end, timer, run end). Without stopping points there are no interstitial slots, and players feel guilty about long sessions.
- **Input fidelity.** Swipe and tap tolerate latency well. Precise timing and virtual sticks do not, and they degrade on low-end Android. Genres with low timing tolerance (factor T) need input buffering, coyote time and generous hitboxes (`game-feel`).
- **Low-end devices.** Many-entity genres (survivor-like, io, crowd runners) need pooling, GPU instancing and a per-tier enemy cap. Budget them against the contract's `perf_budgets` (`mobile-performance`).
- **Offline.** Puzzle, idle, solitaire and logic games are expected to work offline. Design save, timer and anti-cheat logic for device-clock tampering.
- **Notifications.** Timer genres (farming, idle, merge energy) live on well-timed opt-in notifications. Action and puzzle-saga games use them only for lives refilled or events. Respect platform rules and consent.

## Anti-patterns

| Anti-pattern | Detection signal | Fix |
|---|---|---|
| Picking a genre from the top-grossing chart | Every comparable is 3+ years old with deep live-ops; no hook in `concept.hook` | Pick a genre in emergence or hybridization, or bring a production advantage the incumbents lack |
| Meta without a core | The design doc is mostly meta; the core prototype is not fun in a 5-minute bot or human run | Find the fun in the core first (doctrine 2); add the meta only after the core retains |
| Treating benchmarks as targets | KPI targets copied from a single blog; genre and platform not stated | Use Core model 9 anchors, label the source, recalibrate after soft launch |
| Content treadmill blindness | R < 1 and no generator or solver plan | Add a generator with a solver or bot gate, endless or daily modes, or UGC |
| Scope beyond agent capacity | AB ≤ 2 factors with no human owner (netcode, 3D animation, feel) | Change subgenre or cut the factor (bots instead of real-time PvP) |
| Too many fused genres | Three or more distinct verbs in the FTUE; the ad creative cannot show the game in 3 seconds | One core plus one meta (fusion rule 1) |
| Fake-gameplay ads | Ads show a mode that is not in the game (classic pin-pull bait) | Ads show real gameplay; if a mini-game is advertised, ship it as a real mode |
| Ignoring locale | A word or trivia game planned for 10 locales with one dictionary | Budget per-locale content (`accessibility-localization`) |
| Ad load from day one | Interstitials before the first win; D1 below the viability screen | No interstitials until the core habit forms; rewarded ads first |
| Copying obstacles without a twist | New levels re-use mechanics with no teach, test, twist cycle | Introduce a new element every N levels with teach, test and twist levels (`level-design`) |

## Using the ontology

- **`contract.meta.genre`** uses these genre slugs: `puzzle`, `hypercasual`, `hybrid-casual`, `idle`, `tycoon-sim`, `action-arcade`, `roguelite`, `rpg`, `strategy`, `pvp`, `social-casino`, `casual` (board casual, bingo, casual sports), `party`, `narrative`, `rhythm`, `educational`, `kids`, `fitness-location`, `cozy`. The schema treats the field as free text, so these slugs are a convention that keeps the playbooks, concepts and contracts searchable under one name.
- **`contract.meta.subgenre`** is the kebab-case playbook heading, for example `match-3`, `merge-2`, `screw-pin`, `arcade-idle`, `survivor-like`, `time-management`. The same rule applies to the companion files.
- **`contract.loops`** comes from the core and meta loop lines. `contract.mechanics[].category` comes from the `category` column of the label mapping table in procedure D.
- **`concept.scores`**:
  - `agent_buildability` = 2 × AB.
  - `production_cost` is the inverse of scope: S → 8–10, M → 6–7, L → 3–5, XL → 1–2.
  - `market` comes from the saturation score in procedure A, step 5.
- **Verification scripts by genre:**
  - Match-3 (swap rules): `${CLAUDE_PLUGIN_ROOT}/scripts/match3_sim.py` (needs `layout.type: "match3"`; bots `random`, `greedy`, `cascade`). It does not implement blast / collapse rules (tap a connected group), so blast levels need a project-owned simulator and bots, with results written to `solver.bot_win_rate` and `solver.runs` (`references/puzzle.md` §2).
  - Sort, sliding, sokoban and lights-out levels: `${CLAUDE_PLUGIN_ROOT}/scripts/puzzle_solver.py`.
  - Level-based genres: `${CLAUDE_PLUGIN_ROOT}/scripts/difficulty_curve.py`.
  - Idle, merge, farming and tycoon economies: `${CLAUDE_PLUGIN_ROOT}/scripts/economy_sim.py` with `economy-model.schema.json`.
  - XP and upgrade curves: `${CLAUDE_PLUGIN_ROOT}/scripts/progression_calc.py`.
  - Gacha-based fusions: `${CLAUDE_PLUGIN_ROOT}/scripts/gacha_calc.py`.
  - Procedural layouts: `${CLAUDE_PLUGIN_ROOT}/scripts/pcg.py`.
  - Soft-launch projections from the retention anchors: `${CLAUDE_PLUGIN_ROOT}/scripts/retention_ltv.py`.
- **Levels** are written to `.gamestudio/levels/` per `level-spec.schema.json`, with `teach` set to `teach|test|twist|reward` and `solver` filled from the script output.
- **Reference titles** become `deconstruction.schema.json` documents via `/arcosian:deconstruct` before you borrow from them. List them in `contract.meta.comparables` with `borrow` and `change`.

## Reference library

| File | Contains | Read when |
|---|---|---|
| `references/puzzle.md` | Match-3, blast/collapse, merge-2, sort/jam, block puzzle, screw/pin, word, trivia, solitaire/mahjong/tile-match, hidden object, physics puzzle, logic | Any puzzle or casual-puzzle concept; level-based design; older and mass-market audiences |
| `references/hyper-hybrid-casual.md` | Hypercasual archetypes (stack, runner, io, cut/slice, draw, idle-arcade) and hybrid-casual patterns (runner + meta, arcade idle, casual survivor-like, puzzle + RPG) | Ad-led or marketability-first concepts; adding a meta to a hypercasual core |
| `references/idle-tycoon-sim.md` | Idle clicker, idle/AFK RPG, tycoon, farming, life sim, home design, restaurant/time management | Timer, economy and absence-driven designs; management and creativity audiences |
| `references/action-arcade-roguelite.md` | Endless runner, arcade, platformer, survivor-like/bullet heaven, roguelite action, casual shooter, archery, top-down shooter | Real-time action concepts; skill and excitement audiences; run-based structures |
| `references/rpg-gacha.md` | Hero collector / squad RPG, gacha ARPG / open world, idle RPG, turn-based JRPG, mobile MMORPG; shared banner math, power curves and the paid-random compliance checklist | Collection, hero and gacha designs; RPG metas for fusions |
| `references/strategy.md` | 4X / SLG, base-builder with async raiding, tower defense, real-time card battler / RTS-lite, auto-battler, turn-based tactics; shared time-as-currency, Lanchester and deterministic-sim foundations | 4X, tower defense, card, auto-battler and tactics concepts |
| `references/competitive-pvp.md` | MOBA, battle royale, hero shooter, brawler, CCG / card games, competitive sports, racing; shared ratings, matchmaking, netcode and integrity | Any synchronous or asynchronous PvP |
| `references/social-casino-party.md` | Social casino / slots, Coin Master-likes, board-game casual, party and social deduction, bingo, casual sports (golf, pool); shared simulated-gambling law and chance math | Casino, board, party and social-deduction concepts; compliance-heavy designs |
| `references/narrative-rhythm-edu-kids.md` | Interactive stories / visual novels, rhythm, educational, kids (COPPA), fitness and location-based, cozy; shared branching-narrative, audio-latency, child-compliance and location-data foundations | Story-led, music-led, learning, under-13, outdoor or comfort-led concepts |
| `references/shooters.md` | Campaign FPS/TPS, arena/boomer shooter, hero shooter (PC/console), battle royale (PC/console), extraction shooter, co-op PvE/horde, twin-stick/top-down; shared TTK maths, hitscan vs projectile, aim assist and input fairness, encounter design | Shooter concepts on PC/console; weapon feel and TTK tuning; mouse/gamepad fairness |
| `references/action-adventure.md` | Zelda-like/open-world action-adventure, character action, soulslike, immersive sim, stealth; shared frame data, stamina and poise, telegraphs, gating and keys, camera | Melee/combo, boss, exploration-gating or stealth concepts; premium PC/console action |
| `references/platformer-metroidvania.md` | Precision 2D platformer, 3D collectathon, metroidvania, puzzle platformer, roguelite platformer; shared jump physics formulas, ability-gating graph, map and backtracking design | Platformer or metroidvania concepts; jump tuning; world-graph solvability |
| `references/racing-sports-fighting.md` | Arcade racing, sim racing, kart racing, team sports simulation, extreme sports / skate, fighting games (2D, 3D, platform fighter); shared vehicle handling, catch-up fairness, sports AI, frame data and rollback netcode, input buffers | PC or console racing, sports or fighting concepts; feel-driven, frame-exact or physics-led designs |
| `references/horror-narrative.md` | Survival horror, psychological horror / walking sim, co-op horror with proximity voice, visual novel, narrative adventure / point-and-click, choice-based interactive fiction (Ink, Twine, Yarn Spinner); shared tension pacing, sound for fear, branching and state tracking, text localisation | Horror, story-led or text-heavy concepts on PC, console or web; premium narrative scoping |
| `references/pc-strategy-cards.md` | RTS, turn-based 4X (PC), grand strategy, roguelike deckbuilder, digital CCG / LCG, tactics RPG (PC/console); shared AI opponents, deep-complexity UI, card maths, determinism and replays, mod support | PC or console strategy and card concepts; deckbuilders and tactics as agent-friendly first projects |
| `references/survival-sandbox.md` | Open-world survival-crafting, co-op survival, creative / voxel sandbox, colony sim, survival roguelite; shared needs-meter decay, crafting-tree gating, resource respawn, day-night and weather, PvP raiding, procedural worlds, save size and streaming | Survival, crafting, base-building and sandbox concepts; PC and console depth; early-access scoping |
| `references/simulation-management.md` | City builder, PC management / tycoon, factory and automation, life sim and farming (PC/console), job and vehicle sims, god games, sports management; shared production ratios, throughput and queues, agent-sim cost, dense UI, large-state saves | Management, automation, simulation and cosy-sim concepts; PC and console depth |
| `references/mmo-live-service.md` | MMORPG, survival MMO, live-service looter shooter / ARPG, creator platforms (Roblox, UEFN), seasonal live games; shared CCU and server cost maths, content cadence, trading economies, moderation, anti-cheat, end-of-service planning | Persistent-world and live-service concepts; any game whose product is an ongoing operation |

## Related skills

- `mechanics-codex`: canonical mechanic cards and categories behind every "signature mechanics" list.
- `game-case-studies`: deep deconstructions of the reference titles named here.
- `analogy-engine`: "X meets Y" fusions; pair it with fusion procedure C.
- `player-psychology`: motivation models and the ethics of the retention drivers used here.
- `market-intel`: saturation, chart and trend evidence for procedure A, step 5.
- `economy-design`: currency architecture for merge, idle, farming and RPG metas.
- `progression-difficulty`: difficulty curves, DDA and win-rate targets for level-based genres.
- `level-design`: teach, test and twist sequencing, level tooling and solver gates.
- `procedural-generation`: generators that raise the content treadmill ratio.
- `monetization`: offer design, ad placement and ethical limits per genre.
- `liveops`: event calendars and team features named in the meta loops.
- `game-feel`: juice and input tolerance for high feel-dependence genres.
- `mobile-ux`: orientation, thumb zones and HUD patterns per genre.
- `qa-testing`: the five gates and bot or solver verification that set the AB score.
- `production`: turning starter features into milestones and estimates.

## Volatile facts (as of Oct 2026 — verify before relying)

- [V1] GameAnalytics-based medians: D1 about 22%, D7 under 4%, D30 0.7–0.8%; top 1% D1 64–68%, D30 13–15%. Another 2026 summary gives higher medians (D1 about 26%, D7 about 10%, D30 3–4%) without attributing a source, so treat medians as order-of-magnitude only. Sources: [Segwise](https://segwise.ai/blog/mobile-gaming-app-user-retention-strategies), [Playio](https://blog.playio.co/d1-d7-d30-retention-benchmarks-2026).
- [V2] Viability screen 25–30% D1, 10–15% D7, 3–6% D30; top tier 45%+, 25%+, 12%+. This is a practitioner heuristic. Sources: [Playio](https://blog.playio.co/d1-d7-d30-retention-benchmarks-2026), [Galaxy4Games](https://galaxy4games.com/en/knowledgebase/blog/mobile-game-retention-benchmarks-2026-d1-d7-d30-data-for-publishers).
- [V3] Hybrid-casual spending rose 17.1% in 2025 ($3.5B → $4.2B). In H1 2026, mobile game IAP was $40B (−2% YoY) and downloads 24B (−12%); Block Blast! topped downloads; Last War, Honor of Kings and Whiteout Survival led grossing in Q1 2026. Source: [Mobilegamer.biz (Sensor Tower)](https://mobilegamer.biz/data-digest-sensor-towers-h1-analysis-hay-days-comeback-julys-top-games-big-krafton-numbers-and-more/).
- [V4] Feb–Apr 2026: casual and hyper-casual each took 40% of game ad revenue, hybrid 16%, mid-core 4%. Jan–May 2026: ads were 70.3% of game revenue in India vs 22.1% in the US; IAP was 77–90% in the US, Canada, Korea and Japan. Sources: [GameDev Reports](https://gamedevreports.substack.com/p/sensor-tower-mobile-game-ad-monetization), [Sensor Tower](https://sensortower.com/blog/gaming-deep-dive-ad-monetization-report).
- [V5] D7/D1 below 0.30 means an FTUE problem; 0.30–0.44 means weak days 2–5. This is practitioner consensus. Source: [GameDev.net](https://gamedev.net/blogs/entry/2298160-the-d7d1-retention-ratio-for-mobile-games-a-complete-guide).
- [V6] Aha later than about 90 seconds and a significant share of users never return. Source: [Playio](https://blog.playio.co/mobile-game-onboarding-retention).
- [V7] Mobile game IAP 2025 was about $82B (+1%). Strategy (4X) was the hot genre of 2025. Sources: [Sensor Tower](https://sensortower.com/press/press-release-sensor-tower-state-of-gaming-gaming-drove-52-billion-downloads-82b-iap-revenue-on-mobile-and-12b-premium-revenue-on-steam), [LinkedIn summary (secondary)](https://fi.linkedin.com/in/teemu-tuulari-aa094028).
- [V8] modl.ai says very fast or timing-critical gameplay is "not fully supported yet". VLMs playing real-time games from raw frames made under 1% progress. Sources: [modl.ai](https://modl.ai), [arXiv:2505.18134](https://arxiv.org/html/2505.18134v3).
- [V9] GameCraft-Bench: the best agent scored 41.46% on 140 Godot tasks. Source: [arXiv:2606.17861](https://arxiv.org/abs/2606.17861).
