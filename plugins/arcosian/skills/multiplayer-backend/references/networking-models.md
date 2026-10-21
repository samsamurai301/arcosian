# Networking models for mobile games

How to choose and build the networking model for a phone game: asynchronous versus real-time play, who holds authority, deterministic lockstep, rollback, snapshot interpolation, client-side prediction with reconciliation, tick rates, and bandwidth and reliability on cellular links. The framing follows widely taught material (Glenn Fiedler's "Gaffer on Games" articles, Valve's Source networking documentation, the GGPO rollback writings by Tony Cannon, and Overwatch's GDC netcode talks), restated here in studio terms and tied to the sim-core architecture, where determinism and serialisable state are already assumed. Pick the weakest model that delivers the fantasy; every step towards real time multiplies cost.

## Contents

1. The model ladder and how to choose
2. Async play
3. Turn-based real-time sessions
4. Authority models
5. Deterministic lockstep
6. Rollback netcode
7. Snapshot interpolation (server authoritative)
8. Prediction and reconciliation
9. Lag compensation
10. Tick rates and update rates
11. Transport: TCP, UDP, WebSocket, QUIC
12. Mobile network realities and bandwidth budgets
13. Message design and serialisation
14. Sessions, matchmaking handoff and reconnection
15. Testing netcode
16. Decision checklist

## 1. The model ladder and how to choose

| Level | Model | Examples of fit | Server cost | Cheat surface |
|---|---|---|---|---|
| 0 | Single player with leaderboards (score submission) | Puzzle, runner | none to tiny | high unless replays validated |
| 1 | Async turn-based or async PvP (ghosts, attack-defend bases) | Word games, base raiders, auto-battlers | low (stateless functions plus DB) | low if server resolves |
| 2 | Real-time turn sessions (short turns, live opponent) | Card battlers, tactics | low to medium | low if server validates |
| 3 | Lockstep or rollback peer or relay | Fighting games, small-scale RTS | relay only | medium (desync, input cheats) |
| 4 | Server-authoritative real-time with snapshots | Shooters, arenas, io games, co-op action | high (game servers per match) | lowest |

Decision procedure:
1. Write the player fantasy: is simultaneous reaction between humans essential? If not, stay at levels 1 or 2.
2. Count players per match and the state size: tiny state and few players favours lockstep or rollback; large state favours snapshots.
3. Check determinism feasibility: a deterministic core (see `game-architecture`) makes levels 1 to 3 cheap; floats across devices make lockstep risky.
4. Check the cheating stakes: ranked and monetised play needs server authority for outcomes.
5. Estimate cost per concurrent user and per match; set a budget before choosing real-time server hosting.
6. Prototype with simulated bad networks (section 15) before committing.

Async play has the best ratio of retention to cost on mobile; most successful social mobile titles are level 1 or 2. Treat real-time as an exception that must earn its cost.

## 2. Async play

Patterns:
- Hot-seat style turns: player submits an action (or a whole turn), server validates by running the same core, stores the new state, notifies the opponent (push).
- Ghost or snapshot PvP: a player's defence or build is stored as data; attackers fight it later against AI or the recorded loadout. The "opponent" never needs to be online.
- Replay-validated scores: client submits `{seed, rules_version, actions}`; the server (or a cloud function) re-simulates with the same core and accepts the score only if the result matches.
- Co-op through shared persistent state (guild bosses, shared goals): server aggregates contributions.

Implementation notes: the core's `apply` plus serialisable state is the whole protocol. Use idempotency keys per action so retries cannot double-apply; store a monotonic `turn_index` and reject out-of-order submissions; push notifications for "your turn" with deep links; time limits per turn with server-side timeout rules; versioned rules so old clients play old matches or are forced to update.

## 3. Turn-based real-time sessions

Two players connected live, alternating turns. Latency tolerance is high (hundreds of milliseconds). Use a relay or a server that holds the match state and relays validated actions; both clients animate events from the authoritative result. Reconnect by fetching full state (`to_dict`) plus the action log tail. Timers: the server owns the clock; clients show countdowns derived from server deadlines. Handle both players acting at once (simultaneous reveal) with a server-side commit and reveal phase.

## 4. Authority models

| Model | Who decides | Pros | Cons | Use |
|---|---|---|---|---|
| Client authoritative | Each client for its own entities | No server logic; no latency for self | Trivial to cheat | Co-op with friends, casual, trust-based |
| Host authoritative (player host) | One player's device | Cheap, no servers | Host advantage, host quits kill the match, NAT traversal and relays needed | Casual party games, private matches |
| Dedicated server authoritative | Your server runs the sim | Cheat-resistant, consistent | Hosting cost, latency for the player's own actions without prediction | Competitive, ranked, monetised |
| Distributed authority | Ownership of entities moves between clients | Scales for co-op, lower server cost | Complex ownership rules; still trust-based | Co-op shared worlds (some engines offer it) |
| Deterministic peers | Everyone runs identical sim from inputs | Tiny bandwidth, no server sim | Desync risk, input delay, slowest peer pacing | RTS, fighting games |

Rule of thumb: authority must sit with whoever you do not trust least. Anything with money, ranking or other players' fun at stake belongs on a server you control. Never trust the client for outcomes (see `references/social-and-security.md`).

## 5. Deterministic lockstep

Peers exchange only inputs; each simulates the same state from the same inputs on the same tick. Bandwidth is tiny and independent of unit count (the classic RTS approach).

Requirements:
1. Fully deterministic core: seeded RNG, no unordered iteration, fixed timestep, integer or fixed-point maths if devices differ (floats across ARM and x86 and different compilers are the main risk).
2. Inputs scheduled for a future tick (input delay `d` ticks) so all peers have them in time.
3. A tick advances only when inputs from all players for that tick have arrived (stalls if one is late).
4. Desync detection: periodically exchange a state hash (for example every 30 ticks); on mismatch log both states, stop, and report.

Trade-offs: input delay is felt (about `d * tick` ms plus network); the slowest connection paces everyone; late joiners and reconnects need a full state snapshot plus catch-up; mid-game cheating by reading hidden state is possible since every peer has full state (fog-of-war hacks).

Mobile fit: works for small-scale RTS or tactical games over a relay server; the deterministic-core discipline is the same as the studio default. Test cross-device determinism with real devices, not only simulators.

## 6. Rollback netcode

Rollback (GGPO-style) runs the local player's input immediately, predicts remote inputs (usually "same as last frame"), and when the real remote input arrives and differs, rolls back to the snapshot at that tick, re-simulates forward with corrected inputs, and renders the result.

Requirements: deterministic core, fast snapshot save and restore (`to_dict` or a lean binary copy), and a sim fast enough to re-run several ticks in one frame (typically up to a limit such as 7 to 8 ticks of rollback; beyond that, stall). Presentation must tolerate corrections: separate cosmetic effects from sim events, delay irreversible effects (sounds, big explosions) by a few ticks or make them cancellable.

Parameters: tick rate fixed (often 60 Hz for action games); input delay of 1 to 3 ticks plus rollback for the rest; max rollback window; spectator and replay support fall out of the input log.

Fit: one-versus-one fighters and small-player-count action games with tiny state and low sim cost. Poor fit: large worlds, expensive sim steps, or many players (rollback frequency grows with players, since any player's mispredicted input forces a rollback).

## 7. Snapshot interpolation (server authoritative)

The server simulates and periodically sends world snapshots; clients render slightly in the past by interpolating between two snapshots.

Procedure:
- Server tick at `T` Hz (for example 20 to 30 Hz on mobile) and snapshot send rate `S` Hz (can be equal or lower).
- Each snapshot carries a tick number and the state of entities visible to that client.
- Client keeps a buffer; render time `= now_server_estimate - interp_delay`, with `interp_delay` typically 2 snapshot intervals (for 20 Hz, about 100 ms) to tolerate one lost packet.
- Interpolate positions linearly (rotations by slerp or shortest angle); extrapolate briefly (cap a few hundred ms) only when the buffer runs dry, then freeze.
- Remote entities are always seen about `interp_delay + one-way latency` in the past; the local player's own entity uses prediction (section 8).

Bandwidth reduction (the core craft): send deltas against the last acknowledged snapshot; quantise positions (for example fixed bits within level bounds); send only entities relevant to the client (interest management by distance, team or visibility); compress by priority (important entities more often); pack bits, not JSON; send events (hits, deaths) reliably on a separate channel, state unreliably.

Snapshot loss: since every snapshot is a full or delta against an acknowledged baseline, a lost packet just means the next one is bigger. Acknowledge with a sequence and ack bitfield on each packet.

## 8. Prediction and reconciliation

Problem: waiting for the server to confirm movement makes controls feel laggy. Solution: the client applies its own input immediately (prediction) and later corrects.

Algorithm:
1. Client stamps each input with a sequence number, applies it locally, stores `(seq, input, resulting_state)` in a buffer, and sends it.
2. Server applies inputs in order and sends back the authoritative state plus `last_processed_seq`.
3. Client discards buffered inputs up to that seq, resets to the authoritative state, and re-applies the remaining unacknowledged inputs.
4. If the replayed result differs from the predicted result, smooth the visual difference (blend the rendered position over about 100 ms) rather than snapping; snap only for large errors (teleports).

Requirements: the movement sim function is shared by client and server (the core again) and is deterministic given state and input; fixed timestep per input; server clamps input rates and magnitudes (speed hacks).

Predict only what you can undo cheaply: own movement, own weapon cooldowns. Do not predict kills or damage dealt (show hit markers tentatively, confirm on server). Other players' entities are not predicted beyond brief extrapolation.

Corrections feel worst with: collisions with other players, moving platforms and knockback. Design such interactions to be server-authoritative with generous smoothing.

## 9. Lag compensation

Players shoot at what they see (the past). To make hits feel fair, the server rewinds hitboxes to the time the shooter's client saw them: `rewind_time = server_now - (client_latency + interp_delay)`, clamped to a maximum (for example a few hundred ms) so high-latency players cannot abuse it. Process: server keeps a short history of entity positions per tick; on a hit request, evaluate the shot against historical positions; apply damage on the present state.

Side effect ("shot around the corner"): the victim may be hit after reaching cover. Accept and cap rewind; competitive designs sometimes favour the shooter, sometimes the target: pick one and tune the cap by testing. For melee and projectile games, favour projectile travel on the server with client-side cosmetic projectiles to avoid rewind complexity.

Mobile note: with 80 to 200 ms round trips common on cellular, design weapons and abilities that do not need frame-perfect precision (auto-aim assist, generous hit shapes, ability windup that hides latency).

## 10. Tick rates and update rates

| Genre | Typical server tick | Snapshot send | Notes |
|---|---|---|---|
| Turn-based, async | none | on action | Request and response |
| Casual real-time (io, party) | 10 to 20 Hz | 10 to 20 Hz | Interpolation hides coarse rate |
| Action arena (mobile) | 20 to 30 Hz | 15 to 30 Hz | Common compromise between feel and cost |
| Fighting (rollback) | 60 Hz | inputs each tick | Inputs only; tiny packets |
| High-end shooters (PC/console) | 60 to 128 Hz | 20 to 64 Hz | Usually too costly for mobile hosting |

These ranges are common practice, not rules; choose by the lowest rate that still feels right in tests. Cost scales roughly with tick rate times players times entities, and battery drain scales with radio wake-ups: batching sends at lower rates is cheaper for phones. Decouple client render rate from tick rate (interpolate). Keep the sim step equal to a clean divisor of the tick (for example 30 Hz sim, 15 Hz snapshots).

Heartbeats and idle: send keepalives at conservative intervals (tens of seconds) to keep NAT mappings alive without draining battery; drop idle connections server side.

## 11. Transport: TCP, UDP, WebSocket, QUIC

| Transport | Strengths | Weaknesses | Fit |
|---|---|---|---|
| TCP | Reliable, ordered, universal | Head-of-line blocking: one lost packet stalls everything behind it | Turn-based, chat, request/response |
| WebSocket (over TCP, TLS) | Works through proxies and firewalls, easy in every engine | Same head-of-line issue; framing overhead | Async and turn-based real-time; web games; Colyseus and many BaaS realtime APIs |
| UDP (custom reliability layer such as ENet, LiteNetLib, or engine transport) | Low latency; choose reliable or unreliable per message | NAT traversal, you build or adopt reliability; some networks block or throttle | Action games on dedicated servers |
| QUIC / WebTransport | UDP-based with streams, TLS built in, no head-of-line across streams, connection migration between Wi-Fi and cellular | Library and server ecosystem still maturing for games; verify engine support | Emerging option; evaluate case by case |
| WebRTC data channels | Peer-to-peer or relayed, unreliable mode, browser-native | Complex signalling and TURN costs | Browser or P2P casual games |

Practical guidance: choose the transport your networking library and hosting already support; do not hand-roll UDP reliability unless you must. Provide an unreliable channel for state and a reliable ordered channel for events. Always encrypt (TLS or DTLS or the library's authenticated encryption) and authenticate the session (token from your auth service, not a raw player id).

Connection migration: phones switch between Wi-Fi and cellular and change IPs; protocols that bind a session to an address drop. Use a session id and resume handshake so a new socket can rejoin the same match.

## 12. Mobile network realities and bandwidth budgets

- Latency varies by tens to hundreds of ms and spikes; jitter and bursty loss are common; handovers cause multi-second blackouts. Design every real-time feature to survive a 2 to 5 second gap (reconnect, resync).
- Packet size: keep payloads below a conservative MTU budget (around 1200 bytes) to avoid fragmentation.
- Budget in bytes per second per player, then compute server egress: `bytes_per_packet * rate * players`. Example: 150 byte snapshots at 20 Hz is 3 KB/s per player; with 10 players per match and every client receiving, server egress is `3 KB/s * 10 = 30 KB/s` per match. Compute your own numbers from measured packet sizes.
- Data caps and metering: keep session traffic modest (casual real-time games should be a small fraction of video streaming); offer low-data modes where relevant.
- Battery: radio wake-ups cost more than bytes; batch, avoid sub-100 ms chatter for non-critical data, close sockets when backgrounded (the OS will likely kill them anyway).
- Background and foreground: on suspend, treat the connection as lost; on resume run the reconnect flow (section 14).
- Test on real cellular networks and with throttled profiles; Wi-Fi in the office is not representative.

## 13. Message design and serialisation

- Message types as small integers; a versioned protocol number in the handshake; reject incompatible clients with an "update required" result.
- Binary formats for real-time (hand-packed bits, FlatBuffers, protobuf or MessagePack); JSON is fine for async and low-rate calls.
- Quantisation: positions in fixed-point within known bounds; angles as 8 to 16 bit integers; booleans as bits.
- Ordering and reliability per message class: input (unreliable, redundant: resend the last N inputs in each packet so loss does not drop actions), events (reliable ordered), state (unreliable, latest wins), chat (reliable).
- Idempotency and sequence numbers for any action that changes economy or progression.
- Size guard: server rejects oversized messages; per-connection rate limits.
- Schema evolution: add fields at the end, keep unknown-field tolerance, document breaking changes with a protocol bump.

## 14. Sessions, matchmaking handoff and reconnection

Lifecycle: authenticate (token) -> matchmaking ticket -> match assignment (server address plus join token) -> connect -> handshake (protocol version, join token) -> play -> result report -> persistence.

Reconnection flow:
1. Client detects loss (no packets for a timeout such as a few seconds).
2. Show a non-blocking "reconnecting" state; keep local prediction frozen or limited.
3. Retry with the same session id and exponential backoff with jitter (cap the delay).
4. Server holds the player's slot for a grace period (tens of seconds), then replaces with a bot or forfeits per mode rules.
5. On rejoin send full state snapshot and resume from the latest tick.

Match results are reported by the server (never by clients) to the backend, which updates ranking and rewards; make the report idempotent by match id. Anti-disconnect abuse: penalise rage-quits mildly in ranked modes; do not punish genuine network drops harshly (distinguish by pattern).

## 15. Testing netcode

- Network emulation: inject latency, jitter, loss and reordering locally (OS-level shaping tools, engine-provided simulators, or a proxy). Test profiles: good Wi-Fi, average LTE (for example 60 ms, 1 percent loss), poor (200 ms, 5 percent loss, bursts), handover blackout (3 s).
- Determinism tests: run two sims from the same inputs on different devices and compare state hashes every N ticks; fail CI on mismatch.
- Replay tests: record real matches as input logs; replay in CI.
- Soak tests: bots join, play and disconnect randomly against a staging server for hours; watch memory, CPU, tick time overruns.
- Metrics to watch: round-trip time distribution, packet loss, rollback counts, prediction error magnitude, snapshot size, server tick time (p99), rejoin success rate.
- Failure injection: kill the server mid-match, drop the client for various durations, duplicate packets, send malformed packets.
- Use `playtest` bots (see `qa-testing`) to play against the live server using the same action format as scripted playthroughs.

## 16. Decision checklist

- [ ] Is real-time between humans essential to the fantasy, or would async or turn-based sessions work?
- [ ] Authority decided per concern (movement, damage, economy, matchmaking, chat).
- [ ] Deterministic core available? Cross-device determinism tested (if lockstep or rollback)?
- [ ] Tick rate, snapshot rate and interpolation delay chosen and costed.
- [ ] Prediction scope limited to what can be corrected cheaply; smoothing defined.
- [ ] Transport and encryption chosen; session resume across IP changes supported.
- [ ] Bandwidth budget per player and server egress per match computed from measured sizes.
- [ ] Reconnect flow and grace period defined; results reported by server idempotently.
- [ ] Network emulation profiles in CI or a manual test pass; soak test scheduled.
- [ ] Cheat model reviewed (see `references/social-and-security.md`) and backend cost modelled (see `references/backend-and-liveops-infra.md`).
