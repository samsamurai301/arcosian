# Social and Competitive Mechanics

Social and competitive mechanics put other people into the loop: as opponents, teammates, benefactors, audiences or rivals. They produce the strongest long-term retention a mobile game can have (obligation to a team, rivalry, status, belonging) and also the most expensive failures: dead clans, unfair matchmaking, toxic chat, cheating, collusion and legal exposure around minors and prizes. This file catalogues 20 mechanics in the shared mechanic-card format, from asynchronous PvP that needs only a database to raids, guild wars and tournaments that need a real backend. Each entry states precise rules, tuning ranges, dynamics, failure modes, mobile verdict, the monetization hook with its ethical limit, and an implementation sketch. Backend choices live in `multiplayer-backend`; safety, minors and prize law in `legal-ethics`.

**Entry format.** Every entry maps onto `${CLAUDE_PLUGIN_ROOT}/scripts/schemas/mechanic-card.schema.json`. Ids are kebab-case; ids from sibling files carry their file number, e.g. `pass-tracks` (05). Aesthetic targets use the eight MDA aesthetics (Hunicke, LeBlanc and Zubek, 2004). The **Net** tag in the index maps to `contract.json → technical.multiplayer` (`none | async | realtime`).

**Sibling overlaps.** `trading` here covers the social and integrity side; price formation and auction houses are in `player-trading` (04) and `markets-auctions` (04). Base layout design for raids is in `base-defense-layout` (09).

## Contents

| # | Id | Mechanic | Primary job | Net |
|---|---|---|---|---|
| 06.01 | `async-base-raid` | Async base raids | PvP against a stored defence; rivalry while offline | async |
| 06.02 | `async-arena` | Async arena (AI-piloted snapshots) | Low-friction ranked power checks | async |
| 06.03 | `async-turn-matches` | Async turn-based matches | Play friends at your own pace | async |
| 06.04 | `leaderboards` | Leaderboards | Status and near-rival motivation | async |
| 06.05 | `leagues-divisions` | Leagues and divisions | Small-cohort competition with promotion/demotion | async |
| 06.06 | `matchmaking-rating` | Matchmaking ratings | Fair, close matches | async / realtime |
| 06.07 | `tournaments` | Tournaments and challenges | High-stakes peaks; spectacle | async / realtime |
| 06.08 | `clans-guilds` | Clans and guilds | Belonging and obligation | async |
| 06.09 | `guild-wars` | Guild wars | Coordinated team-vs-team conflict | async |
| 06.10 | `co-op-events` | Co-op events / community goals | Positive-sum shared targets | async |
| 06.11 | `team-races` | Team races | Short competitive team sprints | async |
| 06.12 | `team-chests` | Team chests | Shared reward meter filled by group activity | async |
| 06.13 | `gifting-help` | Gifting and help requests | Reciprocity loops | async |
| 06.14 | `friends-graph` | Friends and follows | Social graph that powers everything else | async |
| 06.15 | `chat-emotes` | Chat, quick chat and emotes | Communication with safety | async / realtime |
| 06.16 | `spectating-replays` | Spectating and replays | Learning, sharing, verification | async / realtime |
| 06.17 | `trading` | Trading | Player-to-player exchange | async |
| 06.18 | `raids` | Raids (co-op bosses) | Group challenge against shared HP | async / realtime |
| 06.19 | `ghosts` | Ghosts | Asynchronous racing against recorded runs | async |
| 06.20 | `referrals` | Referrals and invites | Growth loop with two-sided rewards | none |

## Choosing a social layer

| Situation | Start with | Add when healthy | Defer |
|---|---|---|---|
| Solo-first casual, no backend yet (`backend: none`) | `ghosts` (local), platform `leaderboards` | `friends-graph`, `referrals` | chat, trading |
| Casual puzzle with live-ops | `leagues-divisions`, `gifting-help` | `clans-guilds`, `team-chests`, `team-races` | `guild-wars` |
| Squad RPG / gacha | `async-arena`, `clans-guilds` | `raids`, `guild-wars`, `co-op-events` | open trading of power items |
| Base builder | `async-base-raid`, `clans-guilds` | `guild-wars`, `spectating-replays` | real-time PvP |
| Competitive real-time | `matchmaking-rating`, `seasonal-ladder` (05) | `tournaments`, `spectating-replays`, `chat-emotes` (quick chat only) | free-text chat with strangers |

Population rule: any feature that needs matchmaking needs liquidity. Estimate concurrent players per matchmaking bucket before shipping; under roughly a few hundred concurrent players per region, prefer async formats, wider rating windows or clearly disclosed bots.

---

### 06.01 Async base raids — `async-base-raid`

- **Category:** social · asynchronous PvP against a stored defence
- **Player fantasy:** "I outwit another player's fortress — and my own fortress fights back while I sleep."
- **Core rules:**
  - *State:* defender layout snapshot and defensive unit levels; defender's unprotected storage; shield timer; attacker army.
  - *Triggers:* attacker searches (matched by trophies and HQ level), deploys units within a time limit; defence simulated by AI.
  - *Effects:* destruction % and stars → trophies ±; loot transferred (capped); defender gets a shield scaled to damage; replay stored for both.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Loot share | 10–20 % of unprotected storage, capped by HQ difference | High loot makes raids lucrative and losses painful |
| Storage protection | 20–50 % of storage unraidable | Limits the sting of offline losses |
| Shield after heavy loss | many hours (scaled to damage) | Prevents repeated farming of one victim |
| Attack time limit | 2–3 min | Tight limits reward planning over improvisation |
| Search cost | small soft-currency fee | Stops infinite shopping for weak bases |

- **Dynamics:** base-layout meta; revenge attacks; spend-before-logout habits; trophy dropping to farm weaker bases.
- **Aesthetic targets (MDA):** Challenge, Expression (base design), Fellowship (rivalry).
- **Feedback and juice:** defence log with replays; loot counters draining in real time; star slam at 50 % and 100 %.
- **Failure modes and exploits:** offline losses feel like theft (cap daily losses, protect a share); sandbagging trophies to raid weaker bases (loot penalties for large level gaps); client-side cheats (server re-simulation).
- **Mobile fit:** excellent — a 2–3 minute attack; defending needs no presence.
- **Monetization hooks and the ethical limit:** army refills, builder time, shields. Shields must not be the only defence against farming; loss caps apply to everyone, payer or not.
- **Implementation notes:** deterministic simulation (fixed-point maths, seeded RNG) shared by client and server; server replays the input log to verify the result.

```text
result = simulate(defense_snapshot, attacker_inputs, seed)        # identical code client & server
server: if simulate(...) != client_claim: reject(); flag(player)
loot   = min(unprotected(defender) * LOOT_PCT * result.damage_pct, LOOT_CAP[hq_diff])
shield = SHIELD_HOURS[result.damage_band]
```
- **Reference games:** Clash of Clans, Boom Beach.
- **Combines well with:** `matchmaking-rating`, `spectating-replays`, `guild-wars`, `build-timers-and-skips` (08).

### 06.02 Async arena (AI-piloted snapshots) — `async-arena`

- **Category:** competitive · asynchronous ranked power check
- **Player fantasy:** "My team against yours — and I climb the arena ranks."
- **Core rules:**
  - *State:* each player's saved defence team; arena rating; daily tickets.
  - *Triggers:* attacker chooses from 3–5 opponents near their rating, spends a ticket; battle auto-resolves or is player-controlled against AI.
  - *Effects:* winner gains rating, defender loses a smaller amount; rank-based daily and season rewards.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Opponent choices | 3–5 | More choice = more "weakest-opponent shopping" |
| Tickets per day | 5–10 free | Caps time spent; extra tickets are a common sink |
| Defender loss factor | 0.3–0.7× attacker gain | Softens offline losses |
| Refresh cost | free once, then small fee | Controls shopping |
| Reward steepness | top 1 % vs median ratio 3–10× | Steep tops drive whale competition |

- **Dynamics:** defence-team composition meta; daily ritual; rank sniping just before the reward snapshot.
- **Aesthetic targets (MDA):** Challenge, Fellowship (status).
- **Feedback and juice:** power comparison before fight; rank-change ticker; defence log ("you were attacked 6 times, won 4").
- **Failure modes and exploits:** pure power comparison reads as pay-to-win; collusion and win-trading between alts; reward snapshot sniping (snapshot at a randomised minute or average rank over the day).
- **Mobile fit:** excellent — auto-battle fits 30–60 second interactions.
- **Monetization hooks and the ethical limit:** extra tickets, refreshes. Show the power gap honestly before the player commits a ticket.
- **Implementation notes:** snapshot defence team at save time; deterministic auto-battle; asymmetric Elo update; detect repeated attacker→defender pairs.
- **Reference games:** AFK Arena (arena), Summoners War (arena), Raid: Shadow Legends (classic arena).
- **Combines well with:** `hero-ascension` (05), `leaderboards`, `seasonal-ladder` (05).

### 06.03 Async turn-based matches — `async-turn-matches`

- **Category:** social · correspondence play
- **Player fantasy:** "I play my friends at my own pace, a move at a time."
- **Core rules:**
  - *State:* server-held game state, `to_move`, `turn_no`, `deadline`.
  - *Triggers:* move submission; deadline expiry; nudges.
  - *Effects:* validate and apply move, advance turn, notify opponent; on expiry forfeit or bot takeover.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Turn deadline | 24–72 h | Short deadlines raise forfeits; long ones stall games |
| Concurrent games | 10–30 cap | Enough parallel games that someone always owes you a move |
| Turn size | one move vs a full round | Rounds suit 1–3 minute sessions |
| Nudge policy | 1 reminder per opponent per day | More becomes spam |
| Rematch flow | one-tap rematch | Keeps rivalries going |

- **Dynamics:** parallel slow-burn games; ritual check-ins; social rivalry.
- **Aesthetic targets (MDA):** Fellowship, Challenge.
- **Feedback and juice:** "your turn" badges ordered by deadline; move replay of the opponent's last turn; end-of-game summary.
- **Failure modes and exploits:** abandoned games (forfeit or bot takeover with notice); nothing to do while waiting (offer solo puzzles); solver/cheat tools in word and board games.
- **Mobile fit:** ideal — perfectly interruptible, one-hand.
- **Monetization hooks and the ethical limit:** interstitials between turns, hint items. No paid hints in rated play.
- **Implementation notes:** idempotent move submission keyed by `turn_no`; server-side legality; push via APNs/FCM.

```text
submit_move(g, player, move, turn_no):
  require g.turn_no == turn_no and g.to_move == player and legal(g, move)
  apply(g, move); g.turn_no += 1; g.to_move = other(player); g.deadline = now() + DEADLINE; notify(g.to_move)
```
- **Reference games:** Words With Friends, Draw Something, Chess.com (daily games).
- **Combines well with:** `friends-graph`, `chat-emotes`, `matchmaking-rating`, `notification-hooks` (08).

### 06.04 Leaderboards — `leaderboards`

- **Category:** competitive · ranked comparison
- **Player fantasy:** "My name is up there — and I just passed my friend."
- **Core rules:**
  - *State:* boards keyed by scope (global, regional, friends, cohort) and period (all-time, weekly, event); metric (best score or cumulative points).
  - *Triggers:* validated score submission; period end.
  - *Effects:* rank update; period-end rewards by band; archive and reset.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Scope | friends + cohort (50–100) for motivation; global top 100 for show | Global boards motivate only the very top |
| Period | weekly or per event | All-time boards freeze and exclude newcomers |
| Displayed window | your rank ± 3–5 neighbours | Near rivals are the motivating unit |
| Reward bands | top 1 / 10 / 25 / 50 % | Percentile bands let everyone aim for something |
| Tie-break | earliest achieved | Deterministic and fair |

- **Dynamics:** near-rival chasing; last-minute sniping; status display; for most players a global rank is demotivating.
- **Aesthetic targets (MDA):** Challenge, Fellowship.
- **Feedback and juice:** animated rank climb ("↑ 12"); "you passed Alex" callout; profile badge for top bands.
- **Failure modes and exploits:** forged scores (server validation, plausibility bounds, replay verification); paid boosters deciding the board; abandoned all-time boards.
- **Mobile fit:** results screen shows the ± neighbours; platform boards (Game Center, Google Play Games) are a zero-backend option.
- **Monetization hooks and the ethical limit:** event score boosters. Cap their effect or separate boosted and unboosted boards; never sell rank.
- **Implementation notes:** sorted sets (Redis `ZADD … GT`, `ZREVRANK`) or a backend leaderboard service; shard cohorts; store proof (seed + input log) for top scores.

```text
submit(player, score, proof): if not plausible(score, proof): flag(player); return
  ZADD board:{event}:{cohort} GT score player
neighbours(player): r = ZREVRANK(...); return ZREVRANGE(..., max(0, r-5), r+5)
```
- **Reference games:** Clash of Clans and Clash Royale (global and local boards), Duolingo (league boards), Geometry Dash.
- **Combines well with:** `leagues-divisions`, `tournaments`, `ghosts`.

### 06.05 Leagues and divisions — `leagues-divisions`

- **Category:** competitive · cohort competition with promotion and demotion
- **Player fantasy:** "Win my group this week and move up a league."
- **Core rules:**
  - *State:* tier ladder; weekly cohorts of N players per tier; points per player.
  - *Triggers:* points from normal play during the period; period end.
  - *Effects:* top K promote, bottom M demote (none in the lowest tiers), placement rewards, new cohorts formed.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Cohort size | 20–50 (Duolingo uses roughly 30) | Small enough that anyone can win their group |
| Promotion share | top 15–33 % | Higher feels generous, inflates top tiers |
| Demotion share | bottom 10–25 %; zero in bottom 2–3 tiers | Demotion adds stakes and anxiety |
| Tier count | 5–10+ | Enough runway for months of climbing |
| Cohort matching | by activity level and join time in the week | Prevents no-lifers crushing casuals |

  Worked example: cohort 30, promote 7 (23 %), demote 5 (17 %), 10 tiers — a consistently top-quartile player climbs about one tier per week, reaching the top tier in roughly ten weeks.
- **Dynamics:** local competition everyone can win; final-day pushes; "safe zone" coasting.
- **Aesthetic targets (MDA):** Challenge, Fellowship.
- **Feedback and juice:** coloured promotion and demotion zones; tier crest upgrade animation; end-of-week summary.
- **Failure modes and exploits:** hyperactive players dominate (activity-based matching); thin cohorts (fill with clearly marked bots or merge cohorts); demotion anxiety churn.
- **Mobile fit:** excellent — weekly rhythm with zero extra input.
- **Monetization hooks and the ethical limit:** point boosters. Cap booster impact so promotion is not purchasable.
- **Implementation notes:** assign cohorts on first activity in the period (late joiners grouped together); settlement job is idempotent and replayable.
- **Reference games:** Duolingo (weekly leagues), Rocket League (ranks with divisions), EA Sports FC (Division Rivals).
- **Combines well with:** `leaderboards`, `seasonal-ladder` (05), `pass-tracks` (05).

### 06.06 Matchmaking ratings — `matchmaking-rating`

- **Category:** competitive · skill estimation and pairing
- **Player fantasy:** "My matches are close and fair; when I improve, I face better players."
- **Core rules:**
  - *State:* hidden rating per player (Elo, Glicko-2 or TrueSkill), uncertainty, queue entries with wait time.
  - *Triggers:* match end (update); queue tick (search).
  - *Effects:* rating update proportional to surprise; pairing within a rating window that widens with wait time.
  - *Elo:* `E_A = 1 / (1 + 10^((R_B − R_A)/400))`, `R'_A = R_A + K·(S_A − E_A)`. Example: 1600 vs 1400 → E = 0.76; with K = 32 a win gains +7.7, a loss costs −24.3.
  - *Glicko-2* (Glickman) adds rating deviation and volatility so new and returning players move fast. *TrueSkill* (Herbrich, Minka and Graepel, Microsoft Research, 2006) handles teams with mean μ and uncertainty σ; leaderboards often show μ − 3σ.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| K-factor | provisional 32–64 for first 10–30 games; settled 10–24 | High K = volatile ratings, fast placement |
| Initial window | ± 50–100 rating | Tight = fair but slow queues |
| Window growth | + 25–50 every 5–10 s | Trades fairness for wait time |
| Max wait | 20–60 s before widening fully or bot fill | Mobile players abandon long queues |
| Power factor | blend card/hero level into the match score | Pure skill MMR fails in power-progression games |

- **Dynamics:** win rates converge toward 50 % (players feel "stuck"); smurfing; deliberate tanking to farm easier opponents.
- **Aesthetic targets (MDA):** Challenge.
- **Feedback and juice:** show rank or trophies, not raw MMR; post-match stats that explain the result.
- **Failure modes and exploits:** low population (long queues → wider windows or disclosed bots); new players stomped (separate new-player pool, high uncertainty); outcome manipulation to drive purchases is a dark pattern — never ship it.
- **Mobile fit:** target queue ≤ 10–20 s; reconnect support for network drops.
- **Monetization hooks and the ethical limit:** none. Never pair players to engineer losses or reward payers with weaker opponents.
- **Implementation notes:** rating service on the server only; log expected vs actual results to calibrate (a well-calibrated system's 70 % favourites should win about 70 %).

```text
expected(ra, rb) = 1 / (1 + 10 ** ((rb - ra) / 400))
update(ra, rb, s, k) = ra + k * (s - expected(ra, rb))
window(wait_s)       = min(W0 + GROW * floor(wait_s / STEP), WMAX)
```
- **Reference games:** chess (Elo, FIDE), League of Legends (hidden MMR), the Halo series (TrueSkill).
- **Combines well with:** `seasonal-ladder` (05), `leagues-divisions`, `tournaments`.

### 06.07 Tournaments and challenges — `tournaments`

- **Category:** competitive · time-boxed high-stakes events
- **Player fantasy:** "Prove it under pressure for a big prize."
- **Core rules:**
  - *State:* format (score attack, single/double elimination bracket, Swiss, run-until-N-losses), entry requirement, prize table, participant records.
  - *Triggers:* entry, match results, deadlines.
  - *Effects:* advance or eliminate; final placement → prizes.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Format | score attack / bracket / Swiss / "12 wins or 3 losses" run | Brackets need scheduling; runs and score attacks are async-friendly |
| Duration | 1 h – 7 days | Short = intense; long = accessible across time zones |
| Losses allowed | 1–3 | More losses widen the skill spread at the top |
| Prize curve | flat vs top-heavy | Top-heavy rewards elite; flat keeps the median entering |
| Entry | free / ticket / currency | Paid entry plus prizes raises legal questions |

  Worked example (12-win / 3-loss run): a player with a 50 % match win rate averages about 3 wins and reaches 12 wins only ~0.65 % of the time; at 60 % → 4.4 wins and ~4 %; at 70 % → 6.4 wins and ~16 %. Set the prize table against this distribution, not against what you hope players achieve.
- **Dynamics:** peak-intensity play; meta experimentation; content for streamers and spectators.
- **Aesthetic targets (MDA):** Challenge, Fellowship.
- **Feedback and juice:** run tracker with win pips and loss hearts; bracket animation; prize reveal.
- **Failure modes and exploits:** real-money prizes and paid entry fall under skill-gaming and gambling law that varies by jurisdiction (legal review required); collusion and soft-play; bracket no-shows (async brackets with deadlines).
- **Mobile fit:** run-based and score-attack formats fit; synchronous brackets struggle with mobile scheduling.
- **Monetization hooks and the ethical limit:** entry tickets, retries. Publish the prize structure; avoid unlimited paid retries in prize events (a spend loop that resembles wagering).
- **Implementation notes:** server state machine per tournament; Swiss pairing by score then rating; collusion heuristics (repeated pairings, abnormal concessions).
- **Reference games:** Hearthstone (Arena: runs end at 12 wins or 3 losses), Clash Royale (Challenges and Global Tournaments).
- **Combines well with:** `matchmaking-rating`, `spectating-replays`, `leaderboards`.

### 06.08 Clans and guilds — `clans-guilds`

- **Category:** social · persistent group membership
- **Player fantasy:** "I belong to a crew that counts on me."
- **Core rules:**
  - *State:* group `{id, name, badge, members[], roles, join_policy, requirements, level, activity_score}`.
  - *Triggers:* create, join (open / request / invite), promote, kick, leave; leader inactivity.
  - *Effects:* access to group chat, group events, donations, perks; obligations (war attacks, contributions).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Capacity | 20–50 | Larger = more activity, weaker ties |
| Roles | leader, co-leader, elder, member | Distributes moderation work |
| Join gate | none / trophies / level / approval | Gates preserve clan identity |
| Unlock timing | D1–D3 | Later unlocks miss most of the players who would benefit |
| Leader auto-transfer | after 7–30 days of inactivity | Prevents dead clans locked by an absent leader |

- **Dynamics:** social obligation; mentoring; leadership burnout; clan-hopping for event rewards; dead clans.
- **Aesthetic targets (MDA):** Fellowship.
- **Feedback and juice:** clan badge on profile and in matches; clan level-up celebration; member activity indicators.
- **Failure modes and exploits:** dead clans (recommend clans by recent activity, merge tools); toxic leadership (report flows, auto-transfer); mercenary hopping (cooldown on event rewards after joining).
- **Mobile fit:** good — async by design; clan search must be filterable by language, activity and requirements.
- **Monetization hooks and the ethical limit:** clan perks, gift purchases for members. Do not display member spending, and avoid designs where clan success visibly depends on someone paying.
- **Implementation notes:** backend group primitives (Nakama groups, PlayFab groups or custom); role ACL checked server-side; nightly job for activity scores and leader transfer.

```text
nightly(): for c in clans: c.activity = Σ member_activity(7d)
  if days_inactive(c.leader) > LEADER_TIMEOUT: c.leader = most_active(c.co_leaders or c.members)
recommend(player): top_k(clans where c.activity > MIN and fits(player, c.requirements), by=lang_match, activity)
```
- **Reference games:** Clash of Clans, Clash Royale, Brawl Stars (clubs), Rise of Kingdoms (alliances).
- **Combines well with:** `guild-wars`, `team-chests`, `gifting-help`, `chat-emotes`, `raids`.

### 06.09 Guild wars — `guild-wars`

- **Category:** competitive · team-vs-team structured conflict
- **Player fantasy:** "Our clan against theirs — every attack matters."
- **Core rules:**
  - *State:* matched pair (or bracket of 8) of clans; war roster; phase (preparation → battle → settlement); attacks remaining per member.
  - *Triggers:* scheduled phase transitions; member attacks during battle.
  - *Effects:* stars/damage accumulate per side; winner by total; rewards to participants; league standings across a season.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Attacks per member | 1–3 (Clash of Clans: two per war) | Fewer attacks raise the stakes of each |
| Roster | opt-in, 5–50 | Opt-in protects casuals and avoids dead weight |
| Phase lengths | prep and battle ~24 h each | Long phases suit time-zone spread |
| Matching metric | war weight / roster power | Inflated-weight exploits if computed naively |
| Reward split | participation vs performance | Pure performance rewards breed resentment |

- **Dynamics:** target calling, coordination, strategy talk, peer pressure, "mirror" attacks.
- **Aesthetic targets (MDA):** Fellowship, Challenge.
- **Feedback and juice:** war map with live star counts; MVP highlights; victory banner for the whole clan.
- **Failure modes and exploits:** sandbagging war weight; non-participants dragging the team (opt-in rosters); burnout from back-to-back wars (built-in rest periods).
- **Mobile fit:** async attacks fit; coordination happens in chat.
- **Monetization hooks and the ethical limit:** war boosts, extra attacks. Avoid paid power that decides wars; keep the social pressure from turning into spending pressure.
- **Implementation notes:** scheduled state machine; snapshot defences at the end of preparation; idempotent settlement; anomaly checks on war weight.
- **Reference games:** Clash of Clans (Clan Wars, Clan War Leagues), Clash Royale (Clan Wars), Rise of Kingdoms (Kingdom vs Kingdom).
- **Combines well with:** `clans-guilds`, `async-base-raid`, `matchmaking-rating`.

### 06.10 Co-op events / community goals — `co-op-events`

- **Category:** social · positive-sum collective target
- **Player fantasy:** "Together we unlock something none of us could alone."
- **Core rules:**
  - *State:* collective counter for a scope (clan or whole player base); reward tiers at thresholds; per-player contribution and cap.
  - *Triggers:* qualifying actions during the event window.
  - *Effects:* counter increments; tiers unlock for qualifying contributors; final rewards at event end.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Scope | clan or global | Global builds spectacle; clan builds obligation |
| Tier thresholds | mid tier reached by 60–80 % of active clans | Unreachable goals deflate everyone |
| Personal cap | 10–25 % of a tier per player | Prevents one player carrying |
| Minimum contribution | small, reachable in 1–2 sessions | Blocks free riders |
| Duration | 3–7 days | Fits weekly live-ops |

- **Dynamics:** cooperation; chatter about progress; free-riding pressure.
- **Aesthetic targets (MDA):** Fellowship.
- **Feedback and juice:** shared progress bar with tier markers; contributor list; global milestone announcements.
- **Failure modes and exploits:** free riders; whales carrying (cap); global goals set too high (set reachable targets, or adjust thresholds early in the event and say so).
- **Mobile fit:** ideal — contribution happens through normal play.
- **Monetization hooks and the ethical limit:** contribution boosters. Goals must be reachable without spending.
- **Implementation notes:** sharded counters to avoid a hot key (write to one of N shards, sum periodically); idempotent increments keyed by event id.

```text
contribute(scope, player, amount, event_id):
  if seen(event_id): return
  amount = min(amount, CAP - contributed[player]); shard = hash(event_id) % N; INCRBY counter:{scope}:{shard} amount
total(scope) = Σ GET counter:{scope}:{i} for i in 0..N-1          # cached every few seconds
```
- **Reference games:** Clash of Clans (Clan Games), Pokémon GO (global challenges), Fortnite (community events).
- **Combines well with:** `clans-guilds`, `team-chests`, `limited-time-events` (08).

### 06.11 Team races — `team-races`

- **Category:** competitive · short team sprint
- **Player fantasy:** "My team just beat four others to the finish."
- **Core rules:**
  - *State:* race instance with K teams (each 3–5 players, or whole clans); target score; scores per team.
  - *Triggers:* points from normal play (level wins) during a short window.
  - *Effects:* first team to the target, or highest at window end, wins; placement rewards for all members.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Teams per race | 4–10 | More teams = longer odds and more drama |
| Team size | 3–5 or whole clan | Small teams make each member matter |
| Window | 1–24 h | Short windows reward simultaneous play |
| Target | reachable by an average team in 50–80 % of the window | Too high and races end at the deadline, not the finish |
| Reward spread | all placements rewarded, top gets most | Rewards losers enough to try again |

- **Dynamics:** bursts of coordinated play; "carry" heroes; social nudges.
- **Aesthetic targets (MDA):** Fellowship, Challenge.
- **Feedback and juice:** live race track with team avatars; overtaking callouts; finish-line celebration.
- **Failure modes and exploits:** inactive team members (matchmake by recent activity); time-zone unfairness (regional pools); pay-to-win boosters deciding races.
- **Mobile fit:** good — normal play feeds the race; no extra input.
- **Monetization hooks and the ethical limit:** boosters, extra moves. Cap booster contribution; do not show "buy to win the race" prompts.
- **Implementation notes:** race matchmaking at join time by team activity; server-side score aggregation; settlement idempotent.
- **Reference games:** team events in leading casual puzzle games (e.g. Toon Blast, Royal Match).
- **Combines well with:** `clans-guilds`, `team-chests`, `win-streaks` (05).

### 06.12 Team chests — `team-chests`

- **Category:** social · shared reward meter
- **Player fantasy:** "Everyone's play fills the chest, and we all get paid."
- **Core rules:**
  - *State:* team meter with tiers; period; contributors.
  - *Triggers:* members earn meter points through normal play (wins, stars, crowns).
  - *Effects:* at period end (or when tiers fill) every qualifying member receives the reward for the highest tier reached.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Tiers | 5–10 | More tiers mean more frequent "we hit the next one" moments |
| Top tier difficulty | reached by the top 10–20 % of teams | Aspirational without being mythical |
| Qualification | ≥ 1 contribution, or a small minimum | Low bar keeps casuals included |
| Period | weekly | Matches clan cadence |
| Reward scaling | geometric by tier | Big jumps at the top motivate a final push |

- **Dynamics:** collective motivation; gentle peer pressure; recruitment of active members.
- **Aesthetic targets (MDA):** Fellowship, Submission.
- **Feedback and juice:** chest visibly glowing and upgrading by tier; contributor ranking (activity, not spend).
- **Failure modes and exploits:** free riders; clans kicking low contributors (expected — give leaders contribution data, not spend data); meter filled by paid boosts.
- **Mobile fit:** excellent — passive.
- **Monetization hooks and the ethical limit:** none needed; if boosts apply, cap them.
- **Implementation notes:** same sharded counter as `co-op-events`; reward claim is per member and idempotent.
- **Reference games:** Clash Royale (the former Clan Chest), Toon Blast (team chest).
- **Combines well with:** `clans-guilds`, `co-op-events`, `team-races`.

### 06.13 Gifting and help requests — `gifting-help`

- **Category:** social · reciprocity loop
- **Player fantasy:** "I help my friends and they help me."
- **Core rules:**
  - *State:* request `{requester, type, amount, expires_at, fulfilled}`; daily give/receive limits.
  - *Triggers:* requester posts (cooldown-gated); donors fulfil from their own inventory or from a free daily allowance.
  - *Effects:* requester receives items, lives or timer reductions; donor earns XP or currency.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Request cooldown | 4–8 h | Shorter makes requests noise |
| Give limit per day | 5–20 | Caps exploitation by alt accounts |
| Donor reward | small XP/gold per gift | Makes giving self-interested enough to happen |
| Source | donor's own items vs generated free | Own items create real reciprocity; free gifts create volume |
| Rarity limits | commons freely, rares limited | Protects the rare economy |

- **Dynamics:** reciprocity norms; clan health signal; gentle obligation.
- **Aesthetic targets (MDA):** Fellowship.
- **Feedback and juice:** "Sam sent you 5 cards" toast; thank-you emote; donor leaderboard in clan.
- **Failure modes and exploits:** alt-account farms feeding a main (link limits to account age and level); request spam; gifting as a back-channel for trading.
- **Mobile fit:** excellent — one tap to give.
- **Monetization hooks and the ethical limit:** gift purchases for others. No social messages that guilt players into buying gifts.
- **Implementation notes:** server-side limits; idempotent fulfilment; expiry job.

```text
fulfil(req, donor, n): require not req.fulfilled and donor.gives_today + n <= GIVE_LIMIT and owns(donor, req.type, n)
  move(req.type, n, donor -> req.requester); donor.gives_today += n; grant(donor, DONOR_REWARD * n)
```
- **Reference games:** Clash Royale (card donations), Clash of Clans (troop donations), Candy Crush Saga (life gifting), Hay Day (help).
- **Combines well with:** `clans-guilds`, `friends-graph`, `lives` (08).

### 06.14 Friends and follows — `friends-graph`

- **Category:** social · social graph
- **Player fantasy:** "My friends are here; I can see them and play with them."
- **Core rules:**
  - *State:* friend edges (mutual) or follows (one-way); sources (platform friends, contacts, codes, recent opponents); friendship levels.
  - *Triggers:* add/accept/remove; interactions raise friendship level.
  - *Effects:* friends appear on maps and boards; enable gifting, trading, co-op invites, ghosts.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Friend cap | 100–400 | Caps spam and gift farming |
| Discovery sources | codes, recent players, clan members, platform friends | Platform import gives fastest density |
| Friendship levels | 3–5 tiers by interaction days | Unlock perks (better trades, bonuses) |
| Privacy defaults | friends-only visibility, no contacts upload by default | Required for minors; good practice for all |
| Removal | silent | Avoids conflict |

- **Dynamics:** network effects; players with in-game friends commonly retain better (verify in your own cohort data via `player-analytics`); invite pressure.
- **Aesthetic targets (MDA):** Fellowship.
- **Feedback and juice:** friend avatars on maps and boards; friendship-level-up moments.
- **Failure modes and exploits:** empty friend lists (seed with recent opponents and clanmates); stranger-danger with minors; gift farming via mass-adding.
- **Mobile fit:** good; platform friends (Game Center) work on iOS; cross-platform needs your own graph.
- **Monetization hooks and the ethical limit:** none directly. Never upload contacts without explicit opt-in.
- **Implementation notes:** graph stored as edge table `(a, b, created_at, level)`; friend codes; block lists checked on every social action.
- **Reference games:** Pokémon GO (friendship levels), Candy Crush Saga (friends on the map), Marvel Snap (friend battles).
- **Combines well with:** `gifting-help`, `trading`, `ghosts`, `referrals`.

### 06.15 Chat, quick chat and emotes — `chat-emotes`

- **Category:** social · communication with safety controls
- **Player fantasy:** "I can talk to my team, celebrate, and taunt a little."
- **Core rules:**
  - *State:* channels (clan, match, direct); message types (free text, canned phrases, emotes/stickers); per-user mute/block lists; age and safety flags.
  - *Triggers:* send; report; mute; block; moderation action.
  - *Effects:* filtered delivery; rate limiting; sanctions (mute, chat ban, account review).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Free text vs canned | canned only with strangers and in real-time matches; free text in clans | Canned removes most toxicity and grooming risk |
| Rate limit | 1 message per 2–5 s; emote cooldown 3–5 s | Stops spam and emote-taunt loops |
| Filter strictness | by age band and region | Under-13 defaults to canned only |
| Default mute | opponent emotes mutable in one tap (some games default-mute) | BM tolerance varies by audience |
| Log retention | long enough for report review | Needed for moderation evidence |

- **Dynamics:** expression, community, bad-manners taunting, scams and links.
- **Aesthetic targets (MDA):** Fellowship, Expression.
- **Feedback and juice:** animated emotes with sound; typing indicators in clan chat; quick-chat wheel on long-press.
- **Failure modes and exploits:** toxicity and harassment; grooming risk with minors; phishing links; moderation cost that scales with users.
- **Mobile fit:** typing is costly mid-game — a quick-chat wheel is the right default; one-tap mute must be reachable mid-match.
- **Monetization hooks and the ethical limit:** cosmetic emote packs. Safety tools (mute, block, report) are always free and never gated.
- **Implementation notes:** client → server → filter (blocklist plus a moderation classifier service) → deliver; age flags disable free text and voice for under-13 by default; reports capture surrounding context automatically.
- **Reference games:** Clash Royale (emotes, one-tap mute), Hearthstone (emotes with squelch), Rocket League (quick chat).
- **Combines well with:** `clans-guilds`, `guild-wars`, `spectating-replays`.

### 06.16 Spectating and replays — `spectating-replays`

- **Category:** social · watch, learn, share, verify
- **Player fantasy:** "I can watch the best players, relive my best moments, and see how they beat my base."
- **Core rules:**
  - *State:* replay `{build, seed, initial_state_hash, inputs[(tick, player, action)], checksums[]}`; live spectate stream with delay.
  - *Triggers:* match end (store); share action; live spectate join.
  - *Effects:* replay re-simulates deterministically; live spectators see a delayed feed.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Live delay | 30 s – 3 min | Prevents ghosting (spectator relaying info) |
| Retention | 7–30 days; featured replays longer | Storage cost vs value |
| Playback speed | 1×, 2×, 4× | Mobile viewers want speed |
| Share scope | clan, link, video export | Video export reaches social platforms |
| Version policy | replays tied to build id | Old builds need old sim code or pre-rendered video |

- **Dynamics:** learning from top players; base-defence analysis; social sharing; cheat verification.
- **Aesthetic targets (MDA):** Fellowship, Discovery.
- **Feedback and juice:** timeline with event markers (crowns, kills); highlight auto-detection; share card with result.
- **Failure modes and exploits:** version drift breaks replays; desync from hidden nondeterminism (floats, unordered iteration); ghosting during live view.
- **Mobile fit:** good — portrait playback at 2×, short highlight clips.
- **Monetization hooks and the ethical limit:** none needed; featured replays can surface cosmetics.
- **Implementation notes:** store inputs, not frames (a few KB per match); checksum every N ticks; this same log is the anti-cheat proof for `leaderboards` and `async-base-raid`.

```text
play(replay): assert compatible(replay.build); sim = Sim(replay.seed, replay.initial_state)
  for tick in 0..end: sim.apply(inputs_at(tick)); sim.step()
    if tick in replay.checksums: assert hash(sim.state) == replay.checksums[tick]   # desync detector
```
- **Reference games:** Clash Royale (TV Royale and replays), Clash of Clans (attack and defence replays), Rocket League (replays).
- **Combines well with:** `tournaments`, `async-base-raid`, `leaderboards`.

### 06.17 Trading — `trading`

- **Category:** social · player-to-player exchange
- **Player fantasy:** "I swap what I don't need for what I want, and complete my collection with my friends' help."
- **Core rules:**
  - *State:* tradability flags per item class; trade offers `{from, to, give[], get[], status}`; limits; marketplace listings (variant).
  - *Triggers:* propose, counter, accept, cancel; listing purchase.
  - *Effects:* atomic swap; fees (marketplace); limits decremented; audit log.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Tradable classes | duplicates / cosmetics only vs everything | Open power trading creates an RMT economy |
| Marketplace fee | 5–15 % | A currency sink that slows inflation |
| Daily limits | 1–10 trades; fewer for rares | Restricts farming and laundering |
| Requirements | account age, level, friendship level | Blocks fresh alt accounts |
| Rarity matching | like-for-like rarity, or star-value matching | Prevents lopsided "gift" laundering |

- **Dynamics:** emergent prices; collection completion through others; community; scams; real-money trading markets.
- **Aesthetic targets (MDA):** Fellowship, Discovery.
- **Feedback and juice:** two-panel trade screen; hold-to-confirm; satisfying swap animation; special reveal for rare trades.
- **Failure modes and exploits:** duplication bugs (atomic, server-side swaps only); scams via last-second offer edits (lock offers before confirmation); RMT and account selling; bot farms.
- **Mobile fit:** good when the trade UI is two panels and one confirmation gesture.
- **Monetization hooks and the ethical limit:** fees and trade tokens. Keep economies closed-loop (no cash-out): when random paid items can be traded for real money, gambling-law exposure rises sharply.
- **Implementation notes:** single database transaction with locks in id order to avoid deadlocks; append-only audit log; anomaly detection on value flow.

```text
trade(a, b, give_a, give_b):
  BEGIN; lock(min(a,b), max(a,b))
  require owns(a, give_a) and owns(b, give_b) and tradable(give_a + give_b) and limits_ok(a, b)
  transfer(give_a, a -> b); transfer(give_b, b -> a); audit(a, b, give_a, give_b); COMMIT
```
- **Reference games:** Pokémon GO (trading with stardust costs that fall with friendship level), Monopoly GO (sticker trading), Hay Day (roadside shop), EVE Online (player market, PC).
- **Combines well with:** `collections-albums` (05), `friends-graph`, `gifting-help`.

### 06.18 Raids (co-op bosses) — `raids`

- **Category:** social · group challenge against shared HP
- **Player fantasy:** "Together we bring down a monster no one could beat alone."
- **Core rules:**
  - *State:* boss `{hp, phase, window_end}`; participants; per-player damage; attempt keys.
  - *Triggers:* participants attack (real-time lobby or async attempts); window expiry.
  - *Effects:* HP decreases; phases change; on defeat or expiry rewards by participation floor plus damage tier.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| HP scaling | `base × n^0.8–0.9` for n participants | Exponent < 1 makes bigger groups more efficient (rewarding recruitment) |
| Window | real-time 3–5 min; async clan boss 24 h – 7 days | Async suits time-zone spread |
| Attempts per day | 1–3 keys | Keys pace daily engagement |
| Reward split | participation floor + damage tiers | Pure top-damage rewards breed resentment |
| Difficulty tiers | 3–6 | Lets weaker groups still win something |

  Worked example: base 1,000 with exponent 0.85 → 5 players face 3,928 HP, 10 players 7,079 HP — each additional player adds less HP than they contribute in damage.
- **Dynamics:** coordination; team-building for specific bosses; daily routine; recruitment pressure.
- **Aesthetic targets (MDA):** Fellowship, Challenge, Sensation.
- **Feedback and juice:** shared HP bar with chunks falling; damage numbers per player; group victory screen.
- **Failure modes and exploits:** leechers (minimum damage to qualify); real-time lobbies fail at low population (async or remote-join fallback); paid damage boosts decide outcomes.
- **Mobile fit:** async clan bosses fit perfectly; real-time raids need a fast lobby and 3–5 minute fights.
- **Monetization hooks and the ethical limit:** extra raid keys or passes. A free daily key must exist; core rewards cannot require paid keys.
- **Implementation notes:** server-side HP with atomic decrements; damage validated by simulation or plausibility bounds; last-hit race resolved by server order.
- **Reference games:** Pokémon GO (raids of up to 20 trainers), Raid: Shadow Legends (Clan Boss), Destiny 2 (raids, console/PC).
- **Combines well with:** `clans-guilds`, `co-op-events`, `hero-ascension` (05).

### 06.19 Ghosts — `ghosts`

- **Category:** competitive · asynchronous racing against recorded runs
- **Player fantasy:** "I'm racing my friend — or my own best — right now."
- **Core rules:**
  - *State:* ghost recording (input log or sampled transforms) with metadata (player, time, build).
  - *Triggers:* run start (choose ghost); run end (save if personal best).
  - *Effects:* non-colliding replay renders alongside the player; split-time comparisons.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Ghost choice | personal best, friend, or a player 3–10 % faster | Slightly faster ghosts are the best motivator |
| Fidelity | transforms at 10–30 Hz vs input log | Transforms survive version changes; inputs are smaller but need determinism |
| Count shown | 1–5 | More becomes visual noise on small screens |
| Splits | per checkpoint delta | Pinpoints where to improve |
| Labelling | always shown as recorded | Honest framing |

- **Dynamics:** "live" racing feel without networking; self-improvement loops; friend rivalry.
- **Aesthetic targets (MDA):** Challenge, Fellowship.
- **Feedback and juice:** translucent ghost; split deltas in green/red at checkpoints; "beat your friend by 0.3 s" share card.
- **Failure modes and exploits:** presenting ghosts or bots as live humans (deceptive — label them); cheated ghost times (validate on submit); input ghosts desyncing after balance patches.
- **Mobile fit:** excellent — zero real-time networking, fully interruptible.
- **Monetization hooks and the ethical limit:** cosmetic only. Disclose recorded opponents.
- **Implementation notes:** sample transforms at fixed intervals and interpolate on playback.

```text
record(dt): if t - last >= 1/HZ: samples.push((t, pos, rot, anim)); last = t
ghost_at(t): (a, b) = bracket(samples, t); u = (t - a.t) / (b.t - a.t)
             return lerp(a.pos, b.pos, u), slerp(a.rot, b.rot, u), a.anim
```
- **Reference games:** the Mario Kart series (Time Trial ghosts), Trackmania.
- **Combines well with:** `leaderboards`, `friends-graph`, `spectating-replays`.

### 06.20 Referrals and invites — `referrals`

- **Category:** social · growth loop
- **Player fantasy:** "My friends join, and we both get something good."
- **Core rules:**
  - *State:* referral code or link per player; attributions `{inviter, invitee, installed_at, qualified}`; tier progress.
  - *Triggers:* invitee installs through the link; invitee reaches a qualifying milestone.
  - *Effects:* both receive rewards; inviter tier rewards at 1 / 3 / 5 / 10 qualified referrals.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Qualifying milestone | reach level 5–10 or play on 3+ days | Higher bars cut fraud and reward real friends |
| Reward symmetry | two-sided | Invitees convert better when they also benefit |
| Reward size | cosmetic or moderate currency | Big rewards attract fraud farms |
| Inviter cap | 10–50 | Limits farming |
| Attribution window | 7–30 days | Longer windows credit slow converters |

  Viral maths: k = invites sent per user × conversion. With 5 invites and 10 % conversion, k = 0.5, so every 100 organic users eventually bring about 100 more (total = 1 ÷ (1 − k)). Below k = 1 referrals amplify acquisition; they do not replace it.
- **Dynamics:** growth; friends who join together tend to play together; spammy sharing if over-rewarded.
- **Aesthetic targets (MDA):** Fellowship.
- **Feedback and juice:** "Your friend Sam reached level 5 — reward unlocked"; inviter tier track.
- **Failure modes and exploits:** device farms and emulators (milestone gating, device checks); share-prompt spam; contact scraping.
- **Mobile fit:** native share sheet; deferred deep links via your attribution provider (Firebase Dynamic Links is deprecated — verify current options in `marketing-ua`).
- **Monetization hooks and the ethical limit:** none. Never reward ratings or reviews (both stores prohibit manipulating ratings); never import contacts without explicit opt-in; no referral prompts aimed at children.
- **Implementation notes:** code → attribution on first open; qualification evaluated server-side; idempotent reward grants.
- **Reference games:** Pokémon GO (referral program), Dropbox (non-game; the canonical two-sided referral design).
- **Combines well with:** `friends-graph`, `gifting-help`, `clans-guilds`.

---

## Integrity and safety checklist for any social feature

- [ ] Server-authoritative outcomes for anything that affects other players (scores, loot, trades, damage).
- [ ] Deterministic simulation + input log for every async competitive mode; replays double as cheat proofs.
- [ ] Rate limits and daily caps on every give/receive/trade action; alt-account heuristics (account age, device, IP clusters).
- [ ] Mute, block and report reachable in one tap, free, and available before chat is.
- [ ] Age-aware defaults: canned chat only and no voice for under-13s; no contact import; friends-only visibility (see `legal-ethics`).
- [ ] Bots and ghosts are labelled; no presenting AI opponents as live humans.
- [ ] No spend data shown to other players; no clan or team goal that requires spending.
- [ ] Paid entry + prizes, or tradable random paid items, are reviewed by `compliance-officer` before design lock.
- [ ] Telemetry: `social_join_group`, `social_gift_sent`, `social_trade`, `match_end` (with rating delta) in the event taxonomy.

## Liquidity and population quick maths

| Need | Formula / rule | Use |
|---|---|---|
| Players per matchmaking bucket | `CCU_region × share_in_mode ÷ buckets` | Below a few dozen per bucket, widen windows or go async |
| Expected queue time | ≈ `1 ÷ (arrival_rate_in_window)` | Target ≤ 10–20 s on mobile |
| Cohort fill time (leagues) | `cohort_size ÷ joins_per_minute_in_tier` | Fill cohorts by join time; merge thin tiers |
| Clan health | active members (7 d) ≥ 40–60 % of capacity | Below this, recommend merges |

## Volatile facts (as of Oct 2026 — verify before relying)

- The amended US COPPA Rule (FTC final rule published Apr 22, 2025) has a compliance deadline of **Apr 22, 2026**; it expands personal information to include biometric identifiers (relevant to voice chat) and makes operators responsible for third-party integrations that touch children's data — [Toy Association](https://toyassociation.org/PressRoom2/News/2026-News/updated-coppa-rule-requirements-take-effect-april-22.aspx); [Loeb & Loeb](https://www.loeb.com/fr/insights/publications/2025/05/childrens-online-privacy-in-2025-the-amended-coppa-rule).
- US state app-store age-verification laws: Texas SB 2420 (Jan 1, 2026), Utah (May 7, 2026), Louisiana (Jul 1, 2026); Apple provides a Declared Age Range API to support them — [9to5Mac](https://9to5mac.com/2025/11/04/app-store-texas-sb2420-new-apis/); [PocketGamer.biz](https://www.pocketgamer.biz/texas-enforces-new-age-verification-law-for-app-stores-and-developers).
- Use these to drive feature flags (chat, voice, trading, referrals) per age band; details in `legal-ethics` and `accessibility-localization`.

## Related skills

- `multiplayer-backend` — backends, authority models, leaderboards, groups, realtime vs async.
- `liveops` — event calendars for team races, co-op events and tournaments.
- `player-psychology` — reciprocity, status, obligation and their limits.
- `legal-ethics` — minors, chat safety, prize law, loot boxes in trading.
- `player-analytics` — social KPIs, cohort retention by friend count and clan membership.
