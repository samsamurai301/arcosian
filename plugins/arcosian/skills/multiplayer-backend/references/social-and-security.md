# Social systems and security

The social layer (leaderboards, skill rating with Elo, Glicko-2 and TrueSkill, guilds, chat and its moderation) and the security layer (server authority, receipt validation, tampering, bot detection) for mobile games. Social features create retention and also abuse; security decides whether your economy and rankings mean anything. The rule that connects them: the client is untrusted, the server decides outcomes, and every social surface needs a moderation and abuse plan before launch. Rating-system descriptions summarise published work by Arpad Elo, Mark Glickman and Microsoft Research (TrueSkill) in original wording; formulas are standard and given for implementation.

## Contents

1. Leaderboards
2. Rating systems: Elo
3. Glicko-2
4. TrueSkill and team games
5. Matchmaking quality and rating pitfalls
6. Guilds, clans and friends
7. Chat and moderation
8. Threat model
9. Server authority patterns
10. Receipt and purchase validation
11. Client tampering and integrity
12. Bot and cheat detection
13. Replay validation of scores
14. Privacy, minors and compliance touchpoints
15. Security checklist

## 1. Leaderboards

Design questions first: what is ranked (score, time, streak, rating), over what scope (global, friends, country, guild), over what window (all-time, daily, weekly, season), and how are ties and resets handled?

| Choice | Guidance |
|---|---|
| Scope | Friends and guild boards drive more engagement than a distant global top; show the player's neighbourhood (the 5 above and below), not just the top 100 |
| Windows | Daily and weekly boards give fresh chances; seasons give resets with rewards at the close; keep all-time for prestige |
| Score semantics | One best score per player per window, or cumulative; define tie-breaker (earlier timestamp wins) |
| Submission | Server-validated (section 13) or at least range-checked; never accept a raw client score for anything with rewards |
| Rewards | Tiered by percentile as well as rank so the middle gets something; pay out from a server snapshot taken at window close |
| Display | Rank, name, score, avatar; localise numbers; show "you" pinned; handle millions of entries via approximate ranks beyond the top |

Implementation options: platform boards (Game Center, Play Games Services) for free baseline and platform-native UX; backend boards (Nakama, PlayFab, UGS, custom). Custom approach: Redis sorted set or Postgres index on `(board_id, score desc, updated_at asc)`; rank query is `count(*) where score > mine`, cached; neighbourhood query uses rank offset. Shard by board and window; archive closed windows.

Abuse: obvious cheats (impossible scores) pollute boards and drive honest players away. Controls: server-side plausibility bounds per level or per time played; replay validation; shadow-banning flagged accounts (they see themselves, others do not); a manual removal tool and an audit log. Seasons let you wipe damage cleanly.

## 2. Rating systems: Elo

Elo (Arpad Elo, chess) tracks one number per player. Expected score of A against B: `E_A = 1 / (1 + 10^((R_B - R_A) / 400))`. After a game with outcome `S_A` (1 win, 0.5 draw, 0 loss): `R_A' = R_A + K * (S_A - E_A)`.

```gdscript
func expected(ra: float, rb: float) -> float:
	return 1.0 / (1.0 + pow(10.0, (rb - ra) / 400.0))

func update(ra: float, rb: float, score_a: float, k: float) -> float:
	return ra + k * (score_a - expected(ra, rb))
```

Parameters: `K` controls volatility; use a higher K for new players (fast placement) and lower for established ones (stability). Typical practice is a K that decays with games played; choose by simulation. Start rating is arbitrary (for example 1000 to 1500) but fixed.

Properties and caveats: zero-sum for two players with the same K; no uncertainty estimate (a new player and a veteran with the same number look identical); inactivity is not handled; draws and team games need extensions; rating inflation or deflation appears if players enter and leave unevenly.

Worked example: A is 1500, B is 1600, K = 32. `E_A = 1/(1+10^(100/400)) = 0.36`. If A wins, A gains `32 * (1 - 0.36) = 20.5`; if A loses, A loses `32 * 0.36 = 11.5`.

Use Elo when: 1v1, simple, transparent, and you can tolerate slow convergence. Keep a minimum-games placement phase and hide the number if volatility would discourage players (show tiers).

## 3. Glicko-2

Glicko (Mark Glickman) adds a rating deviation (RD) that models uncertainty; Glicko-2 adds a volatility `sigma` for how erratic a player's performance is. State per player: rating `r`, deviation `RD`, volatility `sigma`. Updates happen per rating period (a batch of games), with RD growing for inactive players so returning players move quickly.

Implementation notes (the full algorithm is in Glickman's public paper "Example of the Glicko-2 system"; follow it exactly rather than improvising):
- Work internally on the Glicko-2 scale: `mu = (r - 1500) / 173.7178`, `phi = RD / 173.7178`.
- Compute `g(phi) = 1 / sqrt(1 + 3 phi^2 / pi^2)` and expected score `E = 1 / (1 + exp(-g(phi_j) (mu - mu_j)))`.
- Estimated variance `v`, improvement `delta`, then solve for the new volatility with an iterative root find (Illinois-style iteration) using a system constant `tau` (commonly 0.3 to 1.2; lower reduces volatility changes).
- New `phi*` accounts for time passed; update `phi'` and `mu'` from the games; convert back.
- Defaults commonly used: initial rating 1500, RD 350, sigma 0.06.

Benefits: faster convergence for new players, confidence intervals (display `r +- 2RD`), inactivity handling. Use RD to drive matchmaking tolerance and the "provisional" label. Cost: more state and math; test against Glickman's published worked example to validate your implementation (include it as a unit test).

## 4. TrueSkill and team games

TrueSkill (Microsoft Research; Herbrich, Minka, Graepel) models skill as a Gaussian `N(mu, sigma^2)` per player and updates by Bayesian inference over match outcomes, supporting multi-team, multi-player and free-for-all results, partial play and draws. Rating shown is conservative: `mu - k*sigma` (commonly `k = 3`), so uncertain players rank lower until they prove themselves. TrueSkill 2 added more signals (for example performance stats); it has a published paper but details are more involved.

Notes: TrueSkill and its variants have patent and licensing history; check licensing before shipping an implementation (open-source implementations exist, verify their terms). Alternatives for teams: Elo or Glicko on a team's average with individual contribution weighting, or Open Skill style models (open-source Plackett-Luce variants).

Choose:

| Mode | System |
|---|---|
| 1v1, simple | Elo; Glicko-2 when uncertainty and inactivity matter |
| Team vs team, fixed rosters | Glicko-2 or Elo on team rating |
| Team vs team, shuffled players | TrueSkill-style or Open Skill |
| Free-for-all | TrueSkill-style or placement-based point systems |
| Async ghost PvP | Elo or trophy-style points tuned by simulation (often not true skill ratings) |

Trophy and ladder systems common in mobile games (points gained or lost per match with tiered leagues) are design systems, not skill estimators; calibrate with simulation: aim for a distribution where most players sit around the middle leagues and top leagues are demanding but reachable. See `progression-difficulty` for pacing.

## 5. Matchmaking quality and rating pitfalls

- Matchmaker objective: minimise a cost combining rating gap, wait time, latency and party constraints. Start strict, widen the acceptable rating window as wait time grows (for example expand by a fixed step every few seconds up to a cap); log the wait-versus-quality trade-off.
- Latency groups: do not match players across continents for real-time modes if it ruins feel; region queues with fallback.
- Backfill and bots: for small populations (day one, off-peak), fill with bots that mimic human behaviour; disclose if required by policy; never claim bots are humans for ranked rewards.
- Smurfing and boosting: new accounts with high skill distort ratings; detect fast rating gain and move to a faster-converging track; consider phone-number or platform-account friction for ranked.
- Win-streak anomalies and losing on purpose (deranking) are signals for abuse reviews.
- Rating resets per season: soft reset by compressing towards a mean (`r' = mean + alpha*(r - mean)`, `alpha` about 0.5 to 0.8) and widening RD.
- Test rating changes offline: replay historical matches (or synthetic) and compare predicted versus actual outcomes (log loss or calibration), plus distribution shape.
- Fairness perception: players accept losing to better players but resent unfair matches; show matchmaking info lightly ("similar skill").

## 6. Guilds, clans and friends

Model: `guild {id, name, tag, description, language, join_policy (open|request|invite), size_cap, created_at}`, `member {player_id, role (leader|officer|member), joined_at, contribution}`, plus guild-level state (chat, shared goals, treasury or perks, season score).

Design guidance:
- Social glue retains: shared goals (guild boss, collective event) and light obligations (donate cards, help timers) create return reasons; keep requirements optional enough that casual members are welcome.
- Sizes: a cap that keeps names and faces familiar (a few dozen is common practice); too small hurts the discovery of a fit, too large hurts belonging.
- Roles and permissions: leader transfer rules, inactive-leader succession (auto-promote the most active officer after N days), kick and ban limits, audit log of officer actions.
- Discovery: search and recommended guilds by language, activity level and join policy; show activity indicators (last active, weekly points).
- Anti-abuse: guild names and descriptions go through the same moderation as chat; cap daily joins and leaves per player; delay rewards after joining so players cannot hop for perks.
- Economy: shared treasuries and donations must be server-authoritative with transaction logs; cap daily donation amounts; watch for alt-account funnelling.
- Friends: invite codes and platform friends where permitted (Game Center, Play Games, Facebook-style graph deprecated in many places; verify current API availability); friend requests rate limited; block lists respected across all surfaces.
- Data model on backends: Nakama has groups and friends built in; PlayFab has friends and shared groups; Firebase and Supabase require your own tables (index by guild id and member id; denormalise member counts carefully with transactions).
- Privacy: do not expose real names or precise locations; allow hiding online status.

## 7. Chat and moderation

Decide whether you need free-text chat at all. Many successful mobile games ship with none or with preset phrases and emotes. Free-text chat is a safety, legal and cost commitment, especially with minors.

| Option | Risk | Cost | Use |
|---|---|---|---|
| No chat | none | none | default for young audiences and casual games |
| Preset phrases and emotes | very low | low | PvP and co-op where coordination matters |
| Friends-only text | low to medium | medium | social games with a known graph |
| Guild and global chat | high | high (moderation staff or tooling) | live-ops social games for 13 plus audiences |
| Voice | highest | high | only with strong moderation and reporting |

Moderation stack (layered):
1. Prevention: age gating, default-off or limited chat for minors, rate limits, link and contact-information blocking, new-account restrictions.
2. Automated filtering: word and pattern filters per language (with leetspeak and spacing evasions), toxicity classifiers via a moderation service, image moderation for uploaded avatars or screenshots; tune thresholds and keep human review for edge cases.
3. Reporting: in-line report on every message and profile, with categories; show confirmation; act on reports within a stated time.
4. Enforcement ladder: warning, mute for a duration, chat ban, account suspension; consistent rules published in a code of conduct; appeals process.
5. Evidence and logs: keep message logs for the retention window needed for review, minimise personal data, define retention and deletion.
6. Tools: moderator dashboard with search, context window around reported messages, bulk actions, shadow mute.
7. Metrics: reports per thousand messages, time to action, repeat offenders, false positive rate.

Legal and policy touchpoints: user-generated content policies of the stores require reporting, blocking and moderation mechanisms for apps with UGC; regional laws on child safety and online harms (varies by jurisdiction; see `legal-ethics`); never store or transmit contact details of minors beyond need. AI-generated content features carry additional store requirements (see `legal-ethics`).

Localised moderation: filters must cover the languages you ship; consult native speakers for slurs and context.

## 8. Threat model

Assume: the binary is decompiled, memory is edited, traffic is intercepted, requests are replayed and forged, devices are rooted or jailbroken, clocks are changed, accounts are farmed by bots, receipts are faked, and any client-side check can be removed.

| Asset | Threat | Primary control |
|---|---|---|
| Premium currency and entitlements | Fake receipts, replay, refund abuse | Server validation, idempotent grants, refund handling |
| Soft currency and progression | Memory editing, save editing | Server authority for value-bearing changes; sanity checks; cloud audit |
| Rankings and leaderboards | Forged scores, bots | Replay validation, plausibility checks |
| Matchmaking fairness | Smurfs, boosters, collusion | Detection and friction |
| Real-time matches | Aimbots, speed hacks, packet manipulation | Server authority, input validation, rate limits |
| Player data and accounts | Credential stuffing, token theft | Short-lived tokens, rate limits, platform sign-in |
| Backend | Abuse of APIs, scraping, DDoS | Auth on every call, quotas, rules, WAF |
| Ad revenue | Fake impressions, click farms | Mediation fraud tools, anomaly monitoring (see `monetization`) |

Proportionality: spend security effort where cheating hurts other players or revenue. A single-player offline game that is cheated only by the person who owns the phone does not need anti-tamper; a PvP game with ranked rewards does.

## 9. Server authority patterns

Principle: clients send intents; the server validates and decides.

| Concern | Pattern |
|---|---|
| Economy changes | Client requests `claim_reward(id)`; server checks eligibility, applies once (idempotency key), returns new balance |
| Currency spend | Server holds balances (or verifies a signed state), checks costs from its own catalogue, never from the client's claim |
| Progress | Server verifies plausibility (time since last level, max achievable score per level) or re-simulates via the shared core |
| Randomness with value (chests, gacha) | Server rolls and stores pity counters; client only animates the result |
| Timers with payout | Server stores start time; client display only; payout computed from server time |
| Real-time | Server simulates; clients send inputs with sequence numbers; clamp speeds and rates (see `references/networking-models.md`) |
| Daily and event windows | Server enforces start and end |

Hybrid approach for offline-capable games: client simulates and keeps state locally for play; periodically syncs; the server validates deltas against rules (earn rates, caps) and rejects or flags outliers rather than recomputing everything. Soft-currency honesty can be relaxed for single-player; premium currency and ranked rewards cannot.

Shared core for validation: because the sim core is deterministic and engine-free, the same rules can run in a server function (C# in .NET functions, GDScript is not server-runnable without Godot headless, so port rules or run Godot headless on a worker, or use a language-neutral rules definition for simple games). Plan this at design time: a core written in a portable style simplifies replay validation.

Idempotency: every state-changing endpoint takes a client-generated unique request id; the server stores results for a retention window and returns the stored result for repeats. Prevents double grants from network retries and replay attacks.

Rate limiting and quotas: per player and per IP; sensible daily maxima for actions; alerts on spikes.

## 10. Receipt and purchase validation

Flow: client buys through StoreKit or Play Billing; client sends the purchase proof to your server; server validates with the store; server grants the entitlement and records the transaction id; client acknowledges and finishes the transaction.

- **Apple**: use StoreKit 2 transaction data (signed JWS) and verify signatures server side, or use the App Store Server API to query transaction status; subscribe to App Store Server Notifications v2 for renewals, refunds and revocations. On-device validation alone is not enough for valuable grants. (Apple deprecated the original StoreKit IAP APIs in favour of StoreKit 2; see the volatile note in `references/backend-and-liveops-infra.md` section 14 and `monetization`.)
- **Google Play**: verify purchase tokens with the Google Play Developer API (purchases and, for newer one-time products, the monetization APIs), acknowledge purchases within the required window or they are refunded automatically, and consume consumables; use Real-Time Developer Notifications for refunds, voids and subscription state. Pending purchases (cash payments, slow methods) must not be granted until completed.
- **Aggregators** (for example RevenueCat) handle validation, entitlements and cross-platform state for a fee; weigh convenience against dependency (see `monetization`).
- Rules: grant exactly once per transaction id (unique constraint); store `transaction_id`, `product_id`, `purchase_time`, `environment` (sandbox or production), `state`; reject sandbox receipts in production; handle refunds by revoking or debiting (and flagging repeated abusers); never trust a client-sent price or product id; restore purchases by re-validating.
- Fraud patterns: fake receipts from tampered clients and emulator tools, replayed receipts across accounts (bind to account), chargebacks; monitor ratios of failed validations and refunds per player.
- Server clock: use store timestamps and your server time for subscription windows.
- Failure modes: store API down (queue and retry; grant provisional entitlements for low-value items only), timeouts (idempotent retry), duplicate delivery (unique key).

## 11. Client tampering and integrity

No client defence is unbreakable; aim to raise cost and detect cheaply.

| Measure | What it does | Limits |
|---|---|---|
| Platform attestation: Play Integrity API (Android), App Attest and DeviceCheck (iOS) | Server verifies request comes from a genuine app on a genuine device | Cost and quotas; rooted or custom devices are partly detectable; not a guarantee |
| Code obfuscation and IL2CPP/AOT builds | Slows reverse engineering | Does not stop memory edits |
| Memory value protection (obfuscated or encrypted counters) | Defeats naive memory scanners | Skilled cheaters bypass; use only for local score display |
| Save integrity (signed or HMAC saves) | Detects naive file edits | Key lives in the binary; extractable; combine with server checks |
| Certificate pinning | Resists casual traffic interception | Breakable on rooted devices; adds maintenance risk when certificates rotate |
| Server-side validation | Makes tampering irrelevant for validated values | Cost of building it; the real defence |
| Telemetry anomaly detection | Finds impossible patterns after the fact | Needs analytics and review capacity |
| Time checks | Detect clock changes by comparing server and device time | Offline play limits strictness |

Practical order: server authority first, attestation on sensitive calls (purchases, ranked results) second, obfuscation and basic integrity third. Do not ship secrets in the client; treat API keys in the app as public and restrict them by app identity and quotas.

Legal and policy: attestation and device checks collect device signals; disclose in the privacy policy and data safety forms; avoid blocking legitimate users on custom ROMs without recourse for non-competitive games.

## 12. Bot and cheat detection

Signals:
- Behavioural: inhuman input timing regularity, perfect accuracy, 24 hour play, identical action sequences, zero variance in reaction time.
- Progress velocity: levels or currency gained per hour far above the 99.9th percentile.
- Network: many accounts from one IP or device fingerprint, rapid account creation, impossible location jumps.
- Economy: accounts that only collect and transfer (gold farmers), circular transfers between accounts.
- Device: emulators, rooted devices running automation frameworks, accessibility-service abuse (verify current platform signals).
- Social: coordinated joins to guilds, boosted ratings, win trading.

Response ladder: flag, then add friction (captcha-like challenges that are not abusive, slower rewards), then shadow restrictions (leaderboard or matchmaking pools with other flagged accounts), then bans in waves (batch bans hide detection logic). Always keep a human review path to limit false positives, and an appeal route for ranked and paid accounts.

Data pipeline: log action events with server timestamps, compute per-player features daily, rank by anomaly score (z-score or isolation-style methods), review the top of the list. Version your rules and measure precision on reviewed samples.

Ad fraud and install fraud are covered in `marketing-ua` and `monetization`.

## 13. Replay validation of scores

For skill-based single-player scoring (puzzle, runner, daily challenge):

1. Client records `{rules_version, seed, actions[], claimed_score, duration}` (see `game-architecture` for the replay format).
2. Server (function or worker) runs the same deterministic core with the same seed and actions and compares the final score and state hash.
3. Accept only on exact match and plausible duration (time bounds derived from action count and minimum human reaction time); reject otherwise and record the reason.
4. Rate-limit submissions per player and per seed; store only the best.

Cost control: validate asynchronously and show "pending" for leaderboard entries above a threshold; validate synchronously only for rewarded boards; sample-check the rest. If the core cannot run server-side, validate by plausibility bounds plus statistical outlier review. Keep a cross-implementation test vector (seed, actions, expected hash) so core changes cannot silently invalidate server validation.

## 14. Privacy, minors and compliance touchpoints

- Collect the minimum: pseudonymous player ids, no real names, limited device identifiers; follow platform privacy labels and data safety forms (see `store-release`).
- Children: audiences under 13 (and parts of 13 to 17 depending on region) carry strict rules on data collection, chat, ads and purchases; design social features off by default for child audiences; see `legal-ethics`.
- Account deletion and data export: implement end-to-end (backend data, leaderboards, guild memberships, push tokens, analytics ids).
- Third-party SDK data sharing needs disclosure and, for AI services, explicit user consent under current Apple guidance (see the volatile notes in the research and `store-release`).
- Security incident readiness: breach notification obligations differ by jurisdiction; keep a contact path and a log of access to personal data.
- Region rules for online features and age verification are evolving; check at release time.

## 15. Security checklist

- [ ] Threat model written; value-bearing actions identified (premium currency, ranked rewards, trades).
- [ ] Server decides outcomes for everything of value; client sends intents with idempotency keys.
- [ ] Purchases validated server side with store APIs, notifications handled, grants exactly once, refunds handled.
- [ ] Attestation on sensitive endpoints (Play Integrity and App Attest) with graceful fallback.
- [ ] No secrets in client, repo or save; backend rules, quotas and rate limits in place.
- [ ] Leaderboards use replay or plausibility validation; manual removal tool and audit log exist.
- [ ] Rating system chosen with simulation, placement and season-reset plan; implementation tested against a published example.
- [ ] Chat decision made (none, presets, filtered); reporting, blocking, enforcement ladder and retention defined.
- [ ] Guild actions and shared economies server-authoritative and logged.
- [ ] Bot and cheat signals logged; review process and appeal path defined.
- [ ] Privacy disclosures, deletion flow and minors policy reviewed by `compliance-officer`.
