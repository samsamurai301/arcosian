---
name: multiplayer-backend
description: 'Multiplayer and backend codex: async vs real-time, authority, lockstep, rollback, snapshot interpolation, prediction, tick rates; backend selection (Firebase, Nakama, PlayFab, UGS, Photon, Colyseus, Supabase), remote config, CDN, push; leaderboards, Elo/Glicko-2, guilds, chat moderation, server authority, receipt validation, bot detection. Use when planning online features, picking a backend, or hardening against cheating.'
when_to_use: 'Adding multiplayer, leaderboards, cloud saves, guilds or chat; choosing a backend vendor; designing server validation, purchase verification or anti-cheat.'
---

# Multiplayer and Backend

Everything between the phone and the server: which networking model fits the fantasy, which backend to rent or run, how social systems work, and how to stop the client from lying. The studio default is the weakest model that delivers the design: async before real-time, managed before self-hosted, server authority for anything of value.

## What this skill gives you

- A model ladder from async play to server-authoritative real-time, with the cost and cheat surface of each step, plus lockstep, rollback, snapshot interpolation, prediction and tick-rate guidance.
- A backend selection matrix and stack recommendations by game type, with lock-in controls and a labelled section of volatile 2026 vendor facts with sources.
- Operational patterns: remote config and flags, CDN and asset bundles, push, scheduling, environments, cost control.
- Social systems: leaderboards, Elo, Glicko-2, TrueSkill, matchmaking quality, guilds, chat and moderation.
- Security: threat model, server authority patterns, receipt validation, integrity, bot detection, replay-validated scores.

## Core models

**1. Climb the ladder only as far as the fantasy requires.** Single player with leaderboards, then async, then live turns, then lockstep or rollback, then server-authoritative real-time. Each step multiplies server cost, test burden and cheat surface.

**2. Authority follows trust.** Anything involving money, rank or other players' enjoyment is decided on a server you control. The client sends intents with idempotency keys and animates results.

**3. The deterministic core is your network protocol.** Actions in, events out, serialisable state (see `game-architecture`) gives async turns, replay-validated scores, lockstep and rollback cheaply. Without determinism, real-time costs far more.

**4. Hide latency, do not fight it.** Interpolate remote entities about two snapshot intervals in the past, predict only your own cheap-to-correct state, smooth corrections, design abilities tolerant of 100 to 200 ms.

**5. Mobile networks are hostile.** Handovers cause multi-second blackouts, loss is bursty, sockets die in the background. Every real-time feature needs a reconnect path and every payload a size budget.

**6. Abstract the vendor.** Keep identity portable, wrap every service behind an interface with a null implementation, store versioned JSON you own. 2026 showed managed backends restructure under you.

**7. Config is code.** Typed, schema-validated, staged, audited, with kill switches and safe defaults. Server rules never trust client-read values.

**8. Social features need an abuse plan before launch.** Chat, names, guilds and leaderboards are all attack surfaces; decide moderation, reporting and enforcement first, or ship without free text.

## Decision procedures

### Choose the networking model

1. Is simultaneous reaction between humans essential? If no: async or live turns.
2. Players per match and state size: small both favours lockstep or rollback; large state favours snapshots.
3. Determinism feasible across devices? If not, avoid lockstep and rollback.
4. Stakes (ranked, paid, competitive): need server authority for outcomes.
5. Budget per concurrent user versus ARPDAU: if hosting does not fit, redesign towards async.
6. Prototype under emulated bad networks before committing.

Details and parameters in `references/networking-models.md`.

### Choose a backend

| Game | Start with |
|---|---|
| Offline with leaderboards | Platform services (Game Center, Play Games), optional Firebase for config and push |
| Hybrid-casual with IAP and ads | Firebase plus server-side receipt validation |
| Social, guild and event heavy | Nakama (self-hosted or managed), Satori if the budget fits |
| Relational or admin heavy | Supabase with edge functions |
| Real-time action | Photon, Colyseus or Nakama matches, plus an auth and data backend |
| Unity-only, turnkey | UGS behind interfaces |

Then: write the needs list, model cost per DAU at 10x, run an export drill, re-check the volatile facts section. See `references/backend-and-liveops-infra.md`.

### Add leaderboards safely

1. Define scope (global, friends, guild), window (daily, weekly, season) and tie-breaks.
2. Prefer replay-validated or plausibility-checked submissions; never accept raw scores for rewards.
3. Pay rewards from a server snapshot at window close, by percentile as well as rank.
4. Build the removal tool and audit log before launch.

### Add ranked matchmaking

1. Pick the rating system: Elo for simple 1v1, Glicko-2 where uncertainty and inactivity matter, TrueSkill-style for shuffled teams.
2. Simulate the rating on synthetic or historical matches; check calibration and distribution.
3. Set placement games, season reset compression, matchmaker widening by wait time, and region queues.
4. Add smurf and boosting signals.

### Validate a purchase

1. Client buys via the store SDK and sends proof.
2. Server verifies with the store API (Apple server APIs and notifications; Google Play Developer API and real-time notifications).
3. Grant once per transaction id; store environment and state.
4. Handle refunds, pending purchases and retries idempotently.

### Reconnect flow for real-time

1. Detect loss by timeout; show a non-blocking state.
2. Retry with the same session id, exponential backoff with jitter.
3. Server holds the slot for a grace period.
4. Resend full state, resume at latest tick; match results come from the server only.

## Mobile specifics

- Background suspends sockets: treat resume as reconnect; save and sync on pause.
- Wi-Fi to cellular changes IPs: use session ids and resumable handshakes, consider QUIC-style migration where supported.
- Radio wake-ups cost battery: batch updates, lower tick rates for casual play, prefer local notifications for deterministic timers.
- Data caps: offer low-data modes and Wi-Fi-only for large downloads.
- Store rules: account deletion paths, Sign in with Apple where other social sign-in exists, UGC moderation, privacy manifests for listed SDKs, no downloaded executable code.
- Push permission needs an earned pre-prompt; iOS prompts cannot be re-asked in app.
- Minors: social and chat features off by default; see `legal-ethics`.

## Anti-patterns

| Anti-pattern | Detect | Fix |
|---|---|---|
| Real-time because it sounds modern | No design reason for simultaneity | Async or live turns |
| Trusting client scores or prices | Endpoints take values, not intents | Server-side rules and validation |
| Granting purchases from on-device checks | No server verification | Store API validation, unique transaction ids |
| No idempotency | Retries double-grant | Request ids and stored results |
| Wall-clock timers for payouts | Time edits give rewards | Server time |
| Chatty clients on usage-billed databases | Bill spikes | Batching, pagination, rate limits |
| Single vendor deeply embedded | Vendor logic in gameplay code | Interfaces, portable ids and data |
| Global-only leaderboards | Players see rank 4,000,000 | Friends, guild, neighbourhood views |
| Free chat with no moderation | No report button, no logs | Presets or full moderation stack |
| Config pushed without schema | Remote value crashes or breaks economy | Validate, stage, kill switch |
| Rollback or lockstep without determinism tests | Silent desyncs | Hash exchange, cross-device CI |
| Ban waves immediately after detection | Cheaters learn the rules | Batch bans, shadow restrictions first |

## Using the ontology

- Player models from the ontology include social graph and rating fields; the backend stores them as versioned profile data.
- Resources that have real value (premium currency, entitlements) are flagged server-authoritative in the economy model; soft resources may be client-simulated with server sanity checks.
- Loops with multiplayer verbs (trade, gift, compete, cooperate) map to actions validated by server rules; run them through the shared core where possible.
- Telemetry events for sessions, matches, purchases and moderation flow through `event_taxonomy.py generate --contract PATH --out PATH`; define server-side events alongside client events.
- Rating, pity and economy parameters are tuned with `economy_sim.py` and `gacha_calc.py`; experiment sizing with `ab_test.py size`.
- Compliance flags (minors, chat, loot boxes, data) feed `compliance_preflight.py --project DIR` and the design contract's risk list.
- Remote config keys map to tuning data validated by `validate_json.py`; liveops calendars live in `liveops`.

## Reference library

| File | What it contains | When to read it |
|---|---|---|
| `references/networking-models.md` | Model ladder and chooser; async and live turns; authority models; lockstep; rollback; snapshot interpolation; prediction and reconciliation; lag compensation; tick rates; transports; mobile bandwidth; message design; reconnection; netcode testing | Planning any online play; designing real-time netcode; budgeting bandwidth and server cost |
| `references/backend-and-liveops-infra.md` | Needs checklist; service blocks; vendor profiles; selection matrix; stacks by game type; lock-in and exit; auth; remote config and flags; CDN and bundles; push; scheduling; environments and cost; volatile 2026 facts with sources | Choosing or reviewing a backend; setting up live-ops infrastructure; before launch re-check |
| `references/social-and-security.md` | Leaderboards; Elo, Glicko-2, TrueSkill; matchmaking quality; guilds and friends; chat moderation; threat model; server authority patterns; receipt validation; integrity and attestation; bot detection; replay validation; privacy touchpoints; checklist | Adding social features or ranked play; hardening economy and rankings; reviewing anti-cheat |

## Related skills

- `game-architecture` — deterministic core, saves, remote config layering that these services plug into.
- `gameplay-programming` — RNG, pity and system recipes that the server must reproduce or validate.
- `liveops` — event calendars, segmentation and experiments that run on this infrastructure.
- `monetization` — store products, IAP strategy and ad stack tied to receipt validation.
- `player-analytics` — event design, retention and experiment analysis.
- `legal-ethics` — minors, chat, loot boxes, data protection and moderation duties.
- `store-release` — store requirements for accounts, UGC, privacy and SDK manifests.
- `mobile-performance` — network, battery and thermal budgets on devices.
- `qa-testing` — bots, soak tests and network emulation passes.
- `economy-design` — server-authoritative value, pity and offer design.
- `engine-godot` / `engine-unity` — engine networking APIs and SDK integration.
- `mobile-ux` — connection state, reconnect and permission prompts in the UI.
