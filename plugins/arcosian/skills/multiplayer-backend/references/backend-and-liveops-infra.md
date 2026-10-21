# Backend and live-ops infrastructure

How to choose and wire the services behind a mobile game: a selection matrix across Firebase, Nakama (Heroic Labs), PlayFab, Unity Gaming Services, Photon, Colyseus and Supabase, plus the building blocks every live game needs: auth and identity, cloud data, remote config and feature flags, CDN and asset bundles, push notifications and scheduling. Stable guidance (what each class of service is for, how to avoid lock-in, how to structure config and content delivery) is separated from a clearly labelled volatile section with the October 2026 changes and source links. When unsure about a price, limit or product status, treat it as unverified and check the vendor page before committing.

## Contents

1. Start from needs, not vendors
2. Service building blocks
3. Vendor profiles (stable characteristics)
4. Selection matrix
5. Recommended stacks by game type
6. Lock-in and exit strategy
7. Auth and identity
8. Remote config and feature flags
9. CDN, asset bundles and content updates
10. Push notifications
11. Scheduling and server-side jobs
12. Environments, secrets and cost control
13. Observability and operations
14. Volatile facts (as of Oct 2026 — verify)
15. Backend decision checklist

## 1. Start from needs, not vendors

Write the server-side needs list from the design contract before looking at products:

| Need | Question that decides it |
|---|---|
| Identity | Anonymous first, then link to Apple/Google/email? Cross-platform progress? |
| Cloud save | Single-player restore only, or cross-device with conflicts? |
| Economy authority | Does anything with real value (paid currency, ranking) need server validation? |
| Leaderboards and social | Global, friends, guild, seasonal? Moderation needs? |
| Real-time | Async, turn-based live, or action real-time (see `references/networking-models.md`)? |
| Live-ops | Remote config, events, A/B tests, segments, CRM? |
| Content delivery | Asset bundles, localisation, level packs beyond the store binary? |
| Compliance | Minors, account deletion, regional data residency, platform SDK privacy manifests |
| Team | Who operates it after launch? Self-host skills or managed only? |
| Budget | Cost per DAU target relative to ARPDAU (see `economy-design`, `player-analytics`) |

Default stance for indie and mid-size mobile: the fewest moving parts that meet the needs, no dedicated game server unless real-time play demands it, and a thin client-side abstraction (services behind interfaces, see `game-architecture`) so a vendor can be replaced.

## 2. Service building blocks

| Block | What it does | Typical implementations |
|---|---|---|
| Auth | Anonymous and linked identities, sessions, tokens | Firebase Auth, Nakama auth, PlayFab login, UGS Authentication, Supabase Auth |
| Player data | Profile, cloud save, inventory | Firestore, Nakama storage, PlayFab player data, UGS Cloud Save, Postgres |
| Server logic | Validated actions, purchase verification, rewards | Cloud Functions, Nakama runtime (Go, Lua, TypeScript), PlayFab CloudScript or Azure Functions, UGS Cloud Code, Supabase Edge Functions |
| Leaderboards | Ranked lists, seasons, friends | Nakama, PlayFab, UGS Leaderboards, platform services (Game Center, Play Games), Redis sorted sets |
| Matchmaking and sessions | Queues, tickets, lobbies | Nakama matchmaker, Photon rooms, UGS Matchmaker and Lobby, custom |
| Real-time | Authoritative or relay game servers | Photon (Fusion, Quantum), Colyseus, Nakama authoritative matches, UGS Relay and third-party hosts |
| Remote config and experiments | Tunables, flags, A/B | Firebase Remote Config and A/B Testing, UGS Remote Config, Satori, PlayFab experiments |
| Push | Notifications to devices | Firebase Cloud Messaging (APNs bridge), OneSignal, vendor-native |
| Analytics and crash | Telemetry, crashes | See `player-analytics`; Firebase, GameAnalytics and others |
| CDN and storage | Asset bundles, downloads | Cloud storage plus CDN, engine addressables/bundles |

## 3. Vendor profiles (stable characteristics)

**Firebase (Google).** Broad managed BaaS: Auth, Firestore and Realtime Database, Cloud Functions, Remote Config, A/B Testing, Cloud Messaging, Crashlytics, Analytics. Strong mobile SDKs and an official CLI plus MCP server that an agent can drive. Document database with security rules; per-operation billing means chatty clients cost money and security rules must be reviewed. Not game-specific: leaderboards and matchmaking are build-it-yourself (or use platform services). Good default for solo and small teams.

**Nakama (Heroic Labs).** Open-source game server (Go) with accounts, storage, leaderboards, groups and guilds, chat, matchmaking, tournaments, authoritative and relayed realtime matches, and a server runtime scripted in Go, Lua or TypeScript. Self-host on a VM or Kubernetes, or use the managed Heroic Cloud. Satori is the separate live-ops product (audiences, experiments, flags, live events). Strong fit for social and live-ops-heavy games and for teams that value ownership and portability. Requires operations skill if self-hosted (database, scaling, backups).

**PlayFab (Microsoft).** Game backend: login, player data, economy, catalog, leaderboards, matchmaking, party, multiplayer servers, CloudScript. Mature and feature-rich; pricing and plans have changed repeatedly (see volatile section). Fit for teams already in the Microsoft ecosystem; weigh the lock-in and plan changes.

**Unity Gaming Services (UGS).** Authentication, Cloud Save, Cloud Code, Leaderboards, Remote Config, Economy, Matchmaker, Lobby, Relay and more, tightly integrated with Unity. Convenient for Unity projects; product lines have been retired or restructured over time (see volatile section), so keep abstractions around each service.

**Photon (Exit Games).** The long-standing default for real-time multiplayer on mobile: Fusion (state replication, client-server or host modes), Quantum (deterministic with rollback), PUN (legacy), Realtime and Chat. Concurrent-user (CCU) based pricing; server compute for dedicated modes is extra. Not a full BaaS: pair it with an auth and data backend.

**Colyseus.** MIT-licensed open-source authoritative multiplayer framework (Node/TypeScript) with room-based state synchronisation and client SDKs for major engines; optional managed hosting. A good fit for room-based real-time with a JavaScript-capable team; scale-out and matchmaking at large scale need engineering.

**Supabase.** Open-source Postgres-based BaaS: auth, relational database, realtime subscriptions, storage and edge functions. Strong for relational data, admin tooling, SQL analytics and custom leaderboards; you build game-specific logic. Good for teams comfortable with SQL who want portability (Postgres can move).

## 4. Selection matrix

Qualitative ratings on capabilities (stable characteristics, not prices):

| Capability | Firebase | Nakama | PlayFab | UGS | Photon | Colyseus | Supabase |
|---|---|---|---|---|---|---|---|
| Auth and identity linking | strong | strong | strong | strong | basic | basic (BYO) | strong |
| Cloud save and player data | strong | strong | strong | strong | none | via custom | strong (SQL) |
| Server-side game logic | functions | runtime scripts | CloudScript | Cloud Code | in-engine | room code | edge functions |
| Leaderboards | build or platform | built-in | built-in | built-in | none | build | build (SQL) |
| Guilds, friends, chat | build | built-in | partial | partial (friends, chat via others) | chat product | build | build |
| Matchmaking and lobbies | build | built-in | built-in | built-in | rooms and lobbies | rooms | build |
| Real-time authoritative servers | no | yes | hosting product | relay plus partners | yes (core strength) | yes (core strength) | realtime channels only |
| Remote config and experiments | strong | via Satori | built-in | built-in | none | none | build |
| Push | strong (FCM) | via integration | built-in | via integration | none | none | via integration |
| Agent-drivable (CLI or MCP) | official MCP and CLI | API, console, code | API and CLI | CLI and API | limited | code and CLI | CLI and API |
| Self-host or portability | no | yes | no | no | no | yes | yes |
| Engine fit | any (SDKs for Unity, native, C++, Flutter) | Unity, Godot, others | Unity, Unreal, others | Unity | Unity, Unreal (varies) | Unity, Godot via SDKs, JS | any via REST |
| Ops burden | very low | medium (self-host) or low (cloud) | low | low | low | medium | low to medium |

Treat the table as a starting filter; verify current SDK support for your engine version and the vendor's current terms.

## 5. Recommended stacks by game type

| Game type | Stack | Why |
|---|---|---|
| Offline puzzle or casual with leaderboards | Platform saves, Game Center and Play Games for leaderboards and achievements, optional Firebase for config and push | No server to run; low cost |
| Hybrid-casual with IAP and ads | Firebase (Auth, Firestore saves, Remote Config, A/B Testing, FCM, Crashlytics) plus server-side receipt validation function | One vendor, free-tier friendly, agent-drivable |
| Social or live-ops-heavy (guilds, events, tournaments) | Nakama (self-hosted or Heroic Cloud), Satori if budget allows | Built-in social and live-ops; portable |
| Relational data or admin-heavy (collections, trading) | Supabase (Postgres) plus edge functions | SQL for economy audits and tooling |
| Real-time action or PvP | Photon Fusion or Quantum, or Colyseus, or Nakama authoritative matches, plus an auth and data backend | Real-time frameworks need a persistence partner |
| Unity-only small team wanting turnkey | UGS pieces behind interfaces | Fast to start; guard against product changes |

Always: server-side verification for purchases and anything paid; abstraction layer; a documented migration plan; cost model at 10x launch scale.

## 6. Lock-in and exit strategy

- Keep identity portable: store your own player id mapped to provider ids; allow linking multiple identity providers.
- Own the data model: save format and economy rules live in your core and schemas (see `game-architecture`); the backend stores versioned JSON blobs plus indexed fields, not proprietary object graphs.
- Wrap each vendor service behind an interface (`ICloudSave`, `IRemoteConfig`, `ILeaderboards`), with a null or local implementation.
- Avoid deep use of proprietary query languages in business logic; keep rules in code you can move (functions in TypeScript, Go, or C# you control).
- Export drills: once before launch, perform a full export of player data and restore into a staging environment.
- Prefer vendors with open-source or self-hostable options when the game is expected to run for years; prefer documented, stable pricing; be cautious about products in restructuring.
- Contract and policy reviews: data processing agreements, regional data residency, children's data handling (see `legal-ethics`).

## 7. Auth and identity

Flow: start anonymous (device-scoped account) so the player plays instantly; offer linking to Sign in with Apple, Google Play Games or Google sign-in, or email, once value exists (after a few sessions or before purchases that need restore).

Rules:
- Apple requires offering Sign in with Apple when a game offers other third-party social sign-in options (check current App Review guidelines; see `store-release`).
- Account deletion: both stores require an in-app deletion path for apps with accounts; the web deletion route is also needed for Play. Plan the data deletion job (player data, leaderboards, push tokens) at design time.
- Tokens: short-lived access tokens plus refresh; the game server verifies tokens on every request; never trust a client-supplied player id.
- Linking conflicts: when a player links an identity that already has a save, apply the cloud conflict policy (see `references/data-persistence-and-quality.md` in `game-architecture`).
- Minors: avoid collecting personal data from children; use age gates and platform age signals where required (see `legal-ethics`).
- Guest data retention: purge abandoned anonymous accounts after a documented period.

## 8. Remote config and feature flags

Layering and validation rules are in `game-architecture`; operational rules here.

- Treat config as code: store in version control or a config service with audit history; review changes; stage then promote (staging project, then production).
- Typed keys with ranges, schema-validated before publish; publish gates for risky keys (prices, drop rates) requiring a second approval.
- Rollout: percent rollouts and segment targeting for new features, with a kill switch flag per feature and a rollback procedure rehearsed once.
- Experiments: pre-register hypothesis, primary metric, minimum sample (`ab_test.py size`) and stopping rule; log experiment id on events; avoid overlapping experiments on the same surface.
- Client behaviour: cache last good config; apply at safe points; default to safe values offline; never block launch on a config fetch beyond a short timeout.
- Segments: by platform, country, app version, spend tier, tenure; keep a small stable set; document each.
- Server-validated config for economy: if clients can read prices, the server must still enforce the price it believes is current (never trust the client's claimed price).
- Tool support: Firebase Remote Config and A/B Testing (drivable via the official MCP and CLI), UGS Remote Config, Satori flags and experiments, or a homegrown JSON in a bucket behind a CDN for simple needs.

## 9. CDN, asset bundles and content updates

Why: store binaries have size limits and review latency; content that changes (events, levels, localisation, art packs) should update without a release.

| Technique | Notes |
|---|---|
| Asset bundles (Unity Addressables or AssetBundles) | Group by update frequency and by feature; build per platform; version with content hash; keep catalogue small |
| Godot resource packs (PCK/ZIP) | Load with the engine's resource pack loading at runtime; keep scripts out of downloaded packs unless you accept executing downloaded code (store policy risk) |
| Data-only updates (JSON levels, tuning) | Safest and smallest; validate against schema client-side before use |
| On-demand packs (install-time vs fast-follow vs on-demand) | Play Asset Delivery and Apple On-Demand Resources or Background Assets offer store-hosted options; verify current platform capabilities |
| CDN | Cache with long TTL and content-hash file names; invalidate by changing names, not purging; HTTPS only; regional edges |

Rules:
- Store policies restrict downloading executable code that changes app behaviour; keep downloaded content to assets and data (see `store-release` and the policy summaries in the research notes).
- Integrity: sign or hash a manifest; verify hashes after download; fall back to the bundled content on failure.
- Resumable downloads, Wi-Fi-only option for large packs, progress UI, and a size estimate before downloading; check free space.
- Version compatibility: manifest includes minimum client version; older clients ignore incompatible content rather than crash.
- Rollback: keep the previous manifest and files available; a bad content push must be revertible in minutes.
- Cost control: egress is the main cost; compress (Brotli or zstd where supported, texture compression formats for the target GPUs), dedupe shared assets, delta-update where tooling supports it.

## 10. Push notifications

- Channels: remote push via APNs (iOS) and FCM (Android; also commonly used as the iOS bridge), local notifications for timers the device can schedule itself (energy full, crafting done).
- Permission: iOS requires an explicit prompt; ask after the player has seen value, with a pre-prompt explaining benefits; on Android 13 and later a runtime permission is also required. A denied prompt cannot be re-asked in-app; link to settings.
- Content rules: useful and rare; honour quiet hours and time zones; cap frequency per day and per week; allow granular opt-out (events, offers, social); no deceptive or guilt-driven messages (see `player-psychology`, `legal-ethics`).
- Targeting: segment by lifecycle (new, active, lapsed), time zone, language; test copy via experiments; measure open rate and the downstream retention effect, plus opt-out rates as a guardrail.
- Token handling: store the push token on your backend keyed by player id; refresh on app start; remove invalid tokens on delivery errors; unlink on logout or deletion.
- Local-first: prefer local notifications for deterministic timers (no server cost, works offline) and reserve remote push for events and social triggers.
- Deep links: every notification opens the relevant screen; handle cold start and warm start.
- Privacy and consent: disclose notification use; children's apps have restrictions.

## 11. Scheduling and server-side jobs

Live games run on schedules: daily resets, season rollovers, event start and end, leaderboard snapshots, reward payouts, content publishing.

Principles:
- Server time is the clock. All schedule logic uses UTC with explicit offsets; document the reset time and show it to players in local time.
- Idempotent jobs: each run has a key (for example `season_close:2026-W44`); repeating a job is harmless; record completion.
- Event definitions as data: `{id, start, end, segments, config_overrides, rewards}` in a store the client reads (through remote config or an API); the server enforces the window when granting rewards, not the client.
- Phased job design: snapshot, compute, write results, then notify; keep each phase restartable.
- Tools: cron-style schedulers (cloud scheduler triggering functions), Nakama runtime or Satori live events, PlayFab scheduled tasks, UGS scheduler, or a plain cron and worker.
- Calendar tooling in the studio: see `liveops` for planning cadence, and `operate` for post-launch routines.
- Failure handling: alerts on missed jobs; manual re-run runbook; protective caps on reward payouts to limit blast radius of a bug.

## 12. Environments, secrets and cost control

- At least three environments: dev, staging, production, each its own project or namespace; test accounts and test purchase flows in staging only.
- Secrets (service accounts, API keys, signing keys) live in a secret manager or CI secrets, never in the repository, the client, or the save; keys reach code via environment variables (studio convention).
- Client-held keys (analytics, public API keys) are not secrets; protect the backend with auth, rules, quotas and App Check or attestation (see `references/social-and-security.md`).
- Cost model: estimate `cost per DAU per month` from reads, writes, function invocations, egress, and real-time hours; compare with ARPDAU; set budget alerts at 50, 80 and 100 percent of plan; simulate 10x traffic.
- Quotas and rate limiting on every endpoint; per-player write throttles; pagination; avoid unbounded listeners (a client subscribing to a growing collection is a classic bill shock).
- Data retention: expire logs and ephemeral data automatically.

## 13. Observability and operations

- Dashboards: DAU, concurrent users, error rate, p50 and p99 latency, function failures, database load, egress, cost per day.
- Alerts: on error spikes, login failure rate, purchase validation failures, job misses, and budget thresholds; route to an on-call channel.
- Release process: backend versions compatible with at least the previous two client versions; deprecation windows; feature flags for server behaviour.
- Incident readiness: runbooks for outage, data corruption, leaked key rotation, and rollback of config or content (see the `incident-response` practice in the engineering skills of your org if available).
- Backups: automated, tested restores; point-in-time recovery for the player database.
- Load tests before launch and before big events with a representative bot swarm (see `qa-testing`).

## 14. Volatile facts (as of Oct 2026 — verify)

Sources below come from the October 2026 research notes; each item cites its original URL. Items marked unverified were only found in secondary sources.

- **Unity Multiplay Game Server Hosting deprecated as of Apr 1, 2026**, except customers who committed to migrate to Multiplay by Rocket Science before Mar 31; Unity direct support ended Mar 31, 2026 and the software is licensed to Rocket Science Group. Matchmaker, Relay, Lobby, Distributed Authority and Netcode for GameObjects continue and work with third-party hosts (for example Edgegap, Gameye); alternatives are described by vendors with a bias. Source: https://status.unity.com/info_notices/362941 and https://docs.unity.com/en-us/multiplay-hosting/reference-landing
- **PlayFab Development Mode is being replaced by Foundation Mode as of Mar 11, 2026**, with no monthly bill up to 1,000 unique users per the docs; the playfab.com marketing page may still show an older larger free tier (conflict, verify). Paid tiers reported: Standard includes a monthly meter allowance then pay-as-you-go; Premium includes a larger one. Whether Foundation Mode eligibility is tied to Xbox shipping plans is unverified. Source: https://learn.microsoft.com/en-za/xbox/playfab/pricing/development-mode and https://devdocs.xbox.com/services/playfab/pricing/pricing-overview
- **Heroic Labs**: Nakama on Heroic Cloud is quote-based with no DAU/MAU/CCU limits on the managed tiers per the vendor; Satori is listed on the official page as starting from a monthly minimum with an included event volume and a per-event rate beyond it (a third-party listing disagrees, so verify current figures). Source: https://heroiclabs.com/pricing
- **Photon Fusion** pricing figures (free for one app up to 100 CCU, then paid CCU tiers) come only from a third-party source; primary pricing not retrieved. Verify at the vendor's site. Source (third party): https://crux.supercraft.host/blog/photon-fusion-pricing-2026/
- **Firebase** products used here (Analytics, Remote Config, A/B Testing, Crashlytics, Cloud Messaging) are generally described as no-cost, while Firestore, Functions and Auth are usage-billed; confirm current limits. An official Firebase MCP server runs locally via `npx -y firebase-tools@latest mcp` (stdio, Firebase CLI credentials or ADC). Source: https://firebase.google.com/docs/ai-assistance/mcp-server and https://firebase.google.com/pricing
- **Apple third-party SDK requirements**: SDKs on Apple's list, which includes Firebase components and UnityFramework, must ship a privacy manifest and, as binary dependencies, be signed; applies to new apps and updates that add a listed SDK. Source: https://developer.apple.com/support/third-party-SDK-requirements/
- **Supabase** pricing and 2026 plan details were not re-verified in the notes. Source: https://supabase.com/pricing
- **Colyseus** is described as MIT-licensed with optional managed cloud (not re-verified for 2026 pricing). Source: https://colyseus.io/
- **Gaps in the notes (do not assume)**: AccelByte pricing and status, Normcore pricing, Vivox status, 2026 pricing changes for UGS Cloud Save, Leaderboards and Remote Config.
- Cautionary signal from the notes: managed backends restructured in 2026 (Unity Multiplay, PlayFab plans), which favours open-source or self-hostable options and abstraction layers for long-lived games.

## 15. Backend decision checklist

- [ ] Needs list written from the design contract; real-time need justified.
- [ ] Stack chosen from section 5; each service behind an interface with a null implementation.
- [ ] Identity portable; linking and deletion flows designed.
- [ ] Server verifies purchases and anything paid; config cannot override server rules.
- [ ] Remote config schema, staging, kill switches and rollback rehearsed.
- [ ] Content delivery uses assets and data only, with hashes, fallbacks and rollback.
- [ ] Push permission strategy, frequency caps and opt-outs defined.
- [ ] Scheduled jobs idempotent and monitored; server time authoritative.
- [ ] Three environments; secrets managed; cost per DAU modelled at 10x.
- [ ] Volatile facts re-checked within 30 days of launch; export drill done.
