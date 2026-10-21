# Time, Energy and Session Mechanics

Time mechanics decide when, how often and for how long people play. On mobile they are the session architecture: energy and lives size each session, timers and appointments schedule the next one, resets and streaks build daily habits, offline progress and rest bonuses make leaving safe, events create peaks, and interruption-safe design keeps a phone call from destroying a run. Used well they respect players' lives and spread content over weeks; used badly they become the core of most dark-pattern complaints (punitive timers, streak anxiety, FOMO, nagging). This file catalogues 20 mechanics in the shared mechanic-card format with exact rules, tuning ranges, dynamics, failure modes, mobile verdict, the monetization hook with its ethical limit, and implementation sketches that are clock-safe. Retention and session KPIs live in `player-analytics`; event calendars in `liveops`.

**Entry format.** Every entry maps onto `${CLAUDE_PLUGIN_ROOT}/scripts/schemas/mechanic-card.schema.json`. Ids are kebab-case; ids from sibling files carry their file number, e.g. `pass-tracks` (05). Aesthetic targets use the eight MDA aesthetics (Hunicke, LeBlanc and Zubek, 2004). The **Clock** column says which clock the mechanic runs on: wall (real elapsed time, server-trusted), play (simulation ticks while playing), or reset (calendar boundaries such as daily reset).

**Sibling overlaps.** The economy side of several mechanics here — `energy` (04), `lives-pool` (04), `offline-earnings` (04), `idle-generators` (04), `build-queues` (04) — covers sources, sinks and currency flow; this file covers their clocks, session shaping and interruption behaviour.

## Contents

| # | Id | Mechanic | Primary job | Clock |
|---|---|---|---|---|
| 08.01 | `energy-stamina` | Energy / stamina | Size sessions; pace content consumption | wall |
| 08.02 | `lives` | Lives | Charge failure, not success | wall |
| 08.03 | `build-timers-and-skips` | Build timers and skips | Schedule returns; sell impatience honestly | wall |
| 08.04 | `appointment-mechanics` | Appointment mechanics | Reward returning at a chosen time | wall |
| 08.05 | `offline-progress` | Offline progress | Make leaving safe and returning rewarding | wall |
| 08.06 | `idle-accumulation` | Idle accumulation | Continuous exponential growth | wall + play |
| 08.07 | `reset-cadences` | Daily and weekly resets | The rhythm of dailies, limits and shops | reset |
| 08.08 | `daily-streaks` | Daily streaks | Habit through consecutive days | reset |
| 08.09 | `streak-protection` | Streak protection | Remove the streak cliff | reset |
| 08.10 | `comeback-bonus` | Comeback bonuses | Reactivate lapsed players | reset |
| 08.11 | `limited-time-events` | Limited-time events | Peaks, novelty, live-ops rhythm | wall |
| 08.12 | `session-caps` | Session caps | Spread rewards across days | reset |
| 08.13 | `rest-bonus` | Rest bonuses | Reward breaks instead of punishing them | wall |
| 08.14 | `cooldowns-charges` | Cooldowns and charges | Timing decisions inside play | play |
| 08.15 | `level-limits` | Move limits vs level timers | Per-level pressure and failure moments | play |
| 08.16 | `content-drip` | Content drip | Time-gated release of content | reset |
| 08.17 | `realtime-vs-turn` | Real-time vs turn-based | Pick the time model of the core loop | play |
| 08.18 | `interruption-safe` | Interruption-safe design | Survive calls, locks and process kills | play |
| 08.19 | `notification-hooks` | Notification hooks | Bring players back when it helps them | wall |
| 08.20 | `real-world-clock` | Real-world clock | A world that lives on real time | wall |

## Session architecture by target length

Use `contract.json → meta.session_length_target_sec` to pick the stack.

| Target session | Core time model | Session governors | Return drivers | Avoid |
|---|---|---|---|---|
| 30–90 s (hyper-casual, idle check-in) | real-time bursts or idle | none, or `offline-progress` cap | `offline-progress`, `notification-hooks` | energy walls |
| 2–5 min (casual puzzle, arena) | turn-based or 2–3 min real-time matches | `lives` or light `energy-stamina` | `daily-streaks`, `limited-time-events`, `reset-cadences` | long uninterruptible levels |
| 5–15 min (mid-core RPG, builder) | auto-battle or turn-based | `energy-stamina`, `session-caps` | `build-timers-and-skips`, `appointment-mechanics`, events | more than ~20 min of daily chores |
| 15–40 min (roguelike runs, strategy) | turn-based with save-anywhere | none (runs are the governor) | `content-drip`, daily seeds | real-time without pause |

Rule of thumb: one governor (energy, lives, caps or none), one or two return drivers, and every timer must answer "what interesting thing does the player do while it runs?"

---

### 08.01 Energy / stamina — `energy-stamina`

- **Category:** time · regenerating action budget
- **Player fantasy:** "I have fuel for a satisfying session, and it refills while I'm away."
- **Core rules:**
  - *State:* `value`, `cap`, `last_tick_at` (server time), `interval`.
  - *Triggers:* actions cost energy; time passes; refills (level-up, ad, purchase, gift, event).
  - *Effects:* `value = min(cap, value + floor(elapsed / interval))`; rewards may push above cap (overcap), but regeneration pauses while at or above cap.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Actions per full bar | `cap ÷ cost` = 8–30 actions | Sets the length of a "full" session |
| Regen interval | 3–10 min per point | Shorter intervals reward frequent check-ins |
| Full-bar time | `cap × interval` = 2–8 h | Determines natural sessions per day (waking hours ÷ full-bar time) |
| Overcap | allowed from rewards / purchases | Prevents level-up refills being wasted |
| FTUE grace | no energy cost for the first 1–3 days of content | Never gate the first session |

  Worked example: cap 60, 1 point per 5 min, 6 per level → 10 levels per full bar, full in 5 h, ~3 full sessions in a 16-hour day; a perfectly attentive player gets 1,440 ÷ 5 = 288 energy (48 levels) per day. That ceiling is your content-consumption rate: compare it to production.
- **Dynamics:** sessions-per-day shaping; waste aversion (return before the bar is full); hoarding for events.
- **Aesthetic targets (MDA):** Submission.
- **Feedback and juice:** bar with "+1 in 3:42" and "full in 2 h 10 min"; refill burst animation; opt-in "energy full" notification.
- **Failure modes and exploits:** energy blocks during FTUE; wasted regeneration at cap feels punitive; device-clock manipulation (server time); energy costs on learning content (charge for rewards, not for practice).
- **Mobile fit:** the defining mobile session governor; one-hand irrelevant.
- **Monetization hooks and the ethical limit:** refills, cap increases, regeneration subscriptions. Always show the free wait time beside any paid refill; never interrupt mid-flow with a paid-only prompt.
- **Implementation notes:** lazy regeneration from timestamps; no server-side ticking.

```text
regen(e, now): if e.value >= e.cap: e.last = now; return
  ticks = floor((now - e.last) / e.interval)
  e.value = min(e.cap, e.value + ticks); e.last += ticks * e.interval
  if e.value >= e.cap: e.last = now
```
- **Reference games:** Genshin Impact (Original Resin), Honkai: Star Rail (Trailblaze Power), Summoners War (energy).
- **Combines well with:** `account-level` (05), `limited-time-events`, `notification-hooks`.

### 08.02 Lives — `lives`

- **Category:** time · failure-charged budget
- **Player fantasy:** "Winning is free; losing costs me — so I play carefully."
- **Core rules:**
  - *State:* `lives`, `cap`, regen timestamps, `unlimited_until`.
  - *Triggers:* level start deducts a life; a win refunds it; failure or quitting keeps it spent; time regenerates; gifts and rewards add lives.
  - *Effects:* at zero lives the player waits, asks friends, watches an ad, or pays.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Cap | 5 | Five failures per session before a wall |
| Regen | 20–30 min per life | 5 × 30 min = 2.5 h to refill |
| Unlimited-lives rewards | 15 min – 24 h | Powerful reward and offer item |
| Social lives | 1 per friend/team request, capped daily | Drives clan and friend engagement |
| Charge model | deduct at start, refund on win | Prevents the kill-the-app exploit |

- **Dynamics:** skilled players play longer; losing streaks at hard levels end sessions; strong link to continue offers.
- **Aesthetic targets (MDA):** Challenge, Submission.
- **Feedback and juice:** heart pops and cracks on loss; refill timer on the map; team-gift toast.
- **Failure modes and exploits:** zero lives at a spike level → churn (rescue with an ad life or team request); charging a life for an OS interruption (resume instead); clock manipulation.
- **Mobile fit:** excellent — matches 1–3 minute levels.
- **Monetization hooks and the ethical limit:** refills, unlimited-lives bundles, continue offers. Show the free wait; no forced ads; never charge a life for a crash or an interruption.
- **Implementation notes:** reuse the `energy-stamina` regen; the deduction is part of the level-start transaction and the refund part of the win transaction.
- **Reference games:** Candy Crush Saga, Royal Match, Toon Blast.
- **Combines well with:** `gifting-help` (06), `level-limits`, `win-streaks` (05).

### 08.03 Build timers and skips — `build-timers-and-skips`

- **Category:** time · delayed completion with optional acceleration
- **Player fantasy:** "My city grows while I'm away; I plan what to build next."
- **Core rules:**
  - *State:* jobs `{id, type, started_at, ends_at}`; builder slots; premium currency.
  - *Triggers:* start job (cost paid); time reaches `ends_at`; skip; help from clanmates.
  - *Effects:* completion applies the upgrade; skip completes now for `skip_cost(remaining)`; help reduces remaining time.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Duration curve | seconds early → hours or days late | Long early timers kill FTUE |
| Skip cost | sublinear, e.g. `A·minutes^0.75` (A = 1: 1 min ≈ 1, 1 h ≈ 22, 4 h ≈ 61, 24 h ≈ 234) | Sublinear makes skipping long timers feel like a better deal |
| Free-finish window | last 1–5 min free | Removes trivial waits |
| Builder slots | 1–5 | A second slot is a classic premium purchase |
| Help reduction | 1–5 % or a fixed minute amount per helper | Ties timers to social play |

- **Dynamics:** queue planning around sleep and work; appointment returns; impatience as a monetization lever.
- **Aesthetic targets (MDA):** Submission, Expression (planning), Fellowship (help).
- **Feedback and juice:** scaffolding and progress bars on buildings; completion "ta-da" with confetti; push on completion (opt-in).
- **Failure modes and exploits:** timers with no decision attached; multi-hour timers in week 1; clock manipulation (server `ends_at`); accidental premium skips (confirm large spends).
- **Mobile fit:** excellent — start jobs, leave, return.
- **Monetization hooks and the ethical limit:** skips, builder slots. Show the exact skip cost, keep it proportional, confirm spends above a threshold, and never invent artificial urgency.
- **Implementation notes:** jobs resolve lazily on read; skip cost is a published table, not hidden logic.

```text
skip_cost(remaining_s) = 0 if remaining_s <= FREE_FINISH_S else ceil(A * (remaining_s / 60) ** EXP)
resolve(jobs, now): for j in jobs: if now >= j.ends_at and not j.done: apply(j); j.done = true
```
- **Reference games:** Clash of Clans, Hay Day, Boom Beach.
- **Combines well with:** `research-trees` (05), `gifting-help` (06), `notification-hooks`.

### 08.04 Appointment mechanics — `appointment-mechanics`

- **Category:** time · scheduled return windows
- **Player fantasy:** "I'll be back at lunch — my harvest will be ready."
- **Core rules:**
  - *State:* scheduled items `{ready_at, expires_at?, reward, penalty?}`.
  - *Triggers:* player schedules (plants, sends expedition) or the game schedules (boss appears at 18:00).
  - *Effects:* collecting inside the window grants the reward; missing it either does nothing, decays the reward, or loses it (punitive).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Window length | 1–8 h, or no expiry | Short windows force schedules on players |
| Miss penalty | none → decay → loss | Loss maximises returns and anxiety |
| Concurrent appointments | 1–5 | More creates a dense return rhythm |
| Player choice of duration | short / medium / long options | Lets players fit the game to their day |
| Alignment | morning, lunch, evening, bedtime | Matches real routines |

- **Dynamics:** habit; scheduling around the game; with penalties, anxiety and churn after a miss.
- **Aesthetic targets (MDA):** Submission, Expression (planning).
- **Feedback and juice:** "ready" sparkle; satisfying bulk-collect; schedule overview screen.
- **Failure modes and exploits:** punitive loss (withering) creating dread; windows that fall during sleep in key time zones; clock manipulation.
- **Mobile fit:** natural fit for check-in play.
- **Monetization hooks and the ethical limit:** extra slots, instant-ready. Prefer "bonus for returning" over "loss for missing"; nothing expires overnight; respect quiet hours.
- **Implementation notes:** server timestamps; let the player pick durations so appointments fit their day; notifications scheduled in local time.
- **Reference games:** FarmVille (crops that wither — the classic punitive version), Hay Day (crops that wait), Neko Atsume (visitors while away).
- **Combines well with:** `build-timers-and-skips`, `notification-hooks`, `offline-progress`.

### 08.05 Offline progress — `offline-progress`

- **Category:** time · production while away
- **Player fantasy:** "I came back richer than I left."
- **Core rules:**
  - *State:* production rates, `last_seen` (server time), offline cap, efficiency.
  - *Triggers:* session start after absence.
  - *Effects:* `earned = rate × min(elapsed, cap) × efficiency`; a "while you were away" summary; optional multiplied claim.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Offline cap | 2–12 h; upgradeable | Sets the ideal return interval |
| Efficiency | 25–100 % of online rate | Below 100 % keeps active play worthwhile |
| Claim multiplier | ad ×2, premium ×2–3 | Strong rewarded-ad placement |
| Fast-forward items | grant 1–8 h of production instantly | Reward and offer item |
| Simulation method | closed form vs stepped | Complex economies need stepped simulation |

  Worked example: 1,000 coins/min, 8 h cap, 50 % efficiency → 240,000 coins on return after 8 h or more.
- **Dynamics:** players return near the cap; cap upgrades feel valuable; play happens around life, not instead of it.
- **Aesthetic targets (MDA):** Submission.
- **Feedback and juice:** summary card with counting-up numbers; chest-burst claim; "cap reached" indicator.
- **Failure modes and exploits:** device-clock manipulation; uncapped accrual breaking the economy; returning to so much currency that choices disappear.
- **Mobile fit:** core — it respects that players leave.
- **Monetization hooks and the ethical limit:** cap extensions, claim multipliers, fast-forwards. Base earnings never require watching an ad.
- **Implementation notes:** server validates elapsed time; closed form where rates are constant; otherwise step-simulate in coarse ticks with a time budget.

```text
elapsed = clamp(server_now - p.last_seen, 0, p.offline_cap)
earned  = Σ g.rate * elapsed * OFFLINE_EFF for g in p.generators   # closed form
# variable rates: for t in range(0, elapsed, 60): step(p, 60) under a CPU budget
```
- **Reference games:** AFK Arena (idle rewards), Idle Miner Tycoon, Egg, Inc., Melvor Idle.
- **Combines well with:** `idle-accumulation`, `prestige` (05), `rest-bonus`.

### 08.06 Idle accumulation — `idle-accumulation`

- **Category:** time · continuous exponential production
- **Player fantasy:** "Number go up — and I'm the one making it go up faster."
- **Core rules:**
  - *State:* generators `{owned, base_rate, base_cost, growth}`, multipliers, managers (automation).
  - *Triggers:* time passes; purchases; milestone counts.
  - *Effects:* production per second; costs grow geometrically (`cost_n = base × r^n`); milestones multiply output.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Cost growth r | 1.07–1.15 (Cookie Clicker buildings: ×1.15) | At 1.15 the 10th unit costs ~4× the first; the 100th ~1.2 million × |
| Milestone multipliers | ×2–×3 at 25 / 50 / 100 owned | Creates targets within a generator |
| Automation unlock | first 5–15 min | Removes tapping chores |
| Generator count | 6–15 | Each new tier refreshes the curve |
| Number notation | suffixes or scientific | Unreadable numbers break the fantasy |

- **Dynamics:** buy-order optimisation by payback time (`cost ÷ Δrate`); walls as growth flattens (cue prestige).
- **Aesthetic targets (MDA):** Submission, Challenge (optimisation).
- **Feedback and juice:** rate ticker; milestone flash; satisfying buy-max button.
- **Failure modes and exploits:** flat mid-game walls; floating-point overflow; buy-max lag with naive loops.
- **Mobile fit:** perfect for short check-ins.
- **Monetization hooks and the ethical limit:** permanent multipliers, time warps. Keep the game completable without them.
- **Implementation notes:** closed-form geometric series for buy-max; big-number type beyond 1e308.

```text
cost(k units from n owned) = base * r**n * (r**k - 1) / (r - 1)
max_affordable(money, n)   = floor(log(money * (r - 1) / (base * r**n) + 1) / log(r))
```
- **Reference games:** Cookie Clicker, AdVenture Capitalist, Egg, Inc.
- **Combines well with:** `offline-progress`, `prestige` (05), `research-trees` (05).

### 08.07 Daily and weekly resets — `reset-cadences`

- **Category:** time · calendar boundaries
- **Player fantasy:** "A new day — fresh quests, fresh deals, fresh chances."
- **Core rules:**
  - *State:* `day_index`, `week_index` from a reset hour and time-zone policy.
  - *Triggers:* crossing the boundary.
  - *Effects:* refresh quests, limits, shops, attempt counters, login claims.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Time policy | fixed server time per region vs player-local midnight | Fixed time keeps shared events fair |
| Reset hour | early morning (e.g. 04:00 server time in Genshin Impact) | Night owls do not lose "their" day at midnight |
| Weekly day | Monday or a mid-week day | Weekend players get full weeks |
| Daily obligation | ≤ 15–20 min of dailies | More becomes a second job |
| Grace | late claim within 1–2 h | Smooths edge cases |

- **Dynamics:** routines; pre-reset rushes; concurrency spikes at reset.
- **Aesthetic targets (MDA):** Submission.
- **Feedback and juice:** "resets in 3 h 12 min" timers; a fresh-day banner; refreshed red dots.
- **Failure modes and exploits:** local-time resets abused by changing the time zone; server load spikes at a single global moment (stagger regional resets or spread jobs); a reset hour in a key market's prime time.
- **Mobile fit:** good — dailies fit short sessions.
- **Monetization hooks and the ethical limit:** daily deals. Keep the daily chore load small; don't punish one missed day.
- **Implementation notes:** one shared day-index function used by every system.

```text
day_index(now_utc, region) = floor((now_utc + TZ_OFFSET[region] - RESET_HOUR * 3600) / 86400)
week_index(now_utc, region) = floor((day_index(now_utc, region) - WEEK_ANCHOR_DAY) / 7)
```
- **Reference games:** Genshin Impact (04:00 server-time reset), Hearthstone (daily quests).
- **Combines well with:** `missions-quests` (05), `login-calendar` (05), `session-caps`.

### 08.08 Daily streaks — `daily-streaks`

- **Category:** time · consecutive-day habit
- **Player fantasy:** "Day 47 — I'm not breaking it now."
- **Core rules:**
  - *State:* `streak`, `last_qualified_day`, milestone table.
  - *Triggers:* first qualifying action on a new `day_index`.
  - *Effects:* consecutive day → streak + 1 and milestone rewards; a gap → streak resets (unless protected, see `streak-protection`).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Qualifying action | one meaningful action (a level, a lesson), not just a login | Login-only streaks inflate DAU without engagement |
| Milestones | 3 / 7 / 14 / 30 / 100 / 365 | Early milestones hook; late ones are status |
| Reward escalation | small daily + spikes at milestones | Spikes create goals |
| Visibility | flame + number on home screen | The number itself is the motivator |

  Maths: if a player returns on any given day with probability 0.9, P(30 consecutive days) = 0.9²⁹ ≈ 4.7 %; at 0.95 ≈ 22.6 %. Allowing a single missed day lifts the 0.9 case to ≈ 20 %. Long streaks without protection are rare by design — the cliff hits your most loyal players.
- **Dynamics:** strong habit formation; loss aversion that grows with streak length; streak anxiety.
- **Aesthetic targets (MDA):** Submission, Expression (status).
- **Feedback and juice:** flame grows with length; milestone celebration; calendar view of the streak.
- **Failure modes and exploits:** break → quit (the longer the streak, the larger the cliff); time-zone hopping; guilt-based reminders.
- **Mobile fit:** excellent — a single short action keeps it alive.
- **Monetization hooks and the ethical limit:** protection items (next entry). Never design so that a missed day destroys months of investment with no recourse; avoid targeting minors with streak pressure.
- **Implementation notes:** use the shared `day_index`; evaluate on the first qualifying action; store history for repair windows.
- **Reference games:** Duolingo (daily streak), Pokémon GO (7-day catch and spin streaks), Snapchat (Snapstreaks, non-game).
- **Combines well with:** `streak-protection`, `login-calendar` (05), `notification-hooks`.

### 08.09 Streak protection — `streak-protection`

- **Category:** time · safety net for streaks
- **Player fantasy:** "Life happened, but my streak survived."
- **Core rules:**
  - *State:* `freezes` (equipped, capped), repair window `{broken_at, repair_until, prev_streak}`.
  - *Triggers:* a missed day (auto-consume freezes); repair action within the window.
  - *Effects:* each freeze covers one missed day; repair restores the previous streak for a cost or task.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Freeze capacity | 1–3 equipped | More capacity covers weekends and travel |
| Freeze sources | earned weekly in play; purchasable | At least one free path |
| Repair window | 24–72 h | Long enough to notice the break |
| Repair cost | fixed, modest; or a catch-up task | Escalating prices exploit loss aversion |
| Auto-use | always automatic | Manual use fails exactly when needed |

- **Dynamics:** reduces cliff churn; protection becomes an asset players want to hold.
- **Aesthetic targets (MDA):** Submission.
- **Feedback and juice:** "your freeze saved your 63-day streak" message; ice visual on the calendar day.
- **Failure modes and exploits:** escalating repair prices; rules too complex to trust; freezes stacked to fake a streak indefinitely (cap capacity).
- **Mobile fit:** invisible until needed — good.
- **Monetization hooks and the ethical limit:** freezes and repairs for sale. Keep a free earn path, fixed prices, and no night-time pressure messaging.
- **Implementation notes:**

```text
on_qualified(s, d): gap = d - s.last_day
  if gap == 1: s.streak += 1
  elif gap > 1 and s.freezes >= gap - 1: s.freezes -= gap - 1; s.streak += 1
  elif gap > 1: s.prev = s.streak; s.repair_until = d + REPAIR_DAYS; s.streak = 1
  s.last_day = d
repair(s, d): require d <= s.repair_until and paid_or_task_done(s); s.streak = s.prev + 1
```
- **Reference games:** Duolingo (Streak Freeze and streak repair); Pokémon GO (streaks with no protection — a useful contrast).
- **Combines well with:** `daily-streaks`, `comeback-bonus`, `win-streaks` (05).

### 08.10 Comeback bonuses — `comeback-bonus`

- **Category:** time · reactivation
- **Player fantasy:** "Welcome back — here's a boost so I can catch up with my friends."
- **Core rules:**
  - *State:* `last_active_day`, returner state, cooldown.
  - *Triggers:* login after ≥ X inactive days, once per cooldown.
  - *Effects:* welcome package scaled to absence and progress; temporary catch-up multipliers; "what's new" recap; returner calendar; softer matchmaking for a few matches.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Inactivity threshold | 3–14 days (light), 30+ days (veteran return) | Tiered packages by absence |
| Catch-up boost | ×1.5–3 XP/resources for 3–14 days | Closes the gap to friends |
| Package size | scaled to player level | Flat packages are meaningless to veterans |
| Cooldown | 30–90 days | Prevents churn-and-return farming |
| Recap | 3–5 screens max | Re-onboards to systems added while away |

- **Dynamics:** reactivation; social reintegration; risk of farming the bonus by lapsing deliberately.
- **Aesthetic targets (MDA):** Submission, Fellowship.
- **Feedback and juice:** personal welcome screen ("you were away 23 days — here's what's new"); boost timer badge.
- **Failure modes and exploits:** returning to an overwhelming UI full of red dots; a dead clan (suggest an active one); bonus farming.
- **Mobile fit:** good; pairs with push/CRM campaigns for opted-in players.
- **Monetization hooks and the ethical limit:** returner offers. Lead with free value; frequency-cap offers; do not single out lapsed heavy spenders with aggressive offers.
- **Implementation notes:** server computes `days_absent` at login; segment-driven remote config; idempotent grant with cooldown.
- **Reference games:** Hearthstone (catch-up packs that help players rejoin the current card sets), World of Warcraft (rested XP softens absence; see `rest-bonus`).
- **Combines well with:** `login-calendar` (05), `clans-guilds` (06), `rest-bonus`.

### 08.11 Limited-time events — `limited-time-events`

- **Category:** time · windowed content and rewards
- **Player fantasy:** "Something special is happening right now."
- **Core rules:**
  - *State:* event `{id, start, end, rules, currency, track, shop, leaderboard?}` from remote config.
  - *Triggers:* window opens; play earns event points or currency; window closes.
  - *Effects:* event track and shop rewards; leaderboards settle; leftover currency converts or expires.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Duration | 24–72 h (short), 7–14 days (major) | Short = intense, excludes casual players |
| Concurrency | 1–3 overlapping | More overlaps cause fatigue |
| Novelty | modifier, new mechanic, or full mode | Re-skins alone wear out fast |
| Final-reward reachability | engaged F2P reaches the top free reward | Unreachable tops are a FOMO dark pattern |
| End-of-event currency | converts to a permanent currency | Expiry punishes partial participation |

- **Dynamics:** engagement and revenue peaks; FOMO; variety; community buzz.
- **Aesthetic targets (MDA):** Discovery, Fellowship, Challenge.
- **Feedback and juice:** themed UI skin and music; countdown that is visible but not alarmist; event-complete celebration.
- **Failure modes and exploits:** fatigue from back-to-back events; paid-only final rewards; time-zone-unfriendly windows; clients trusting local time for start/end.
- **Mobile fit:** the backbone of mobile live-ops.
- **Monetization hooks and the ethical limit:** event passes and bundles. Show the end time plainly, make the headline reward reachable without paying, convert leftovers.
- **Implementation notes:** server-time windows from remote config; rules behind feature flags; content downloadable ahead of start; see `liveops` for calendars.
- **Reference games:** Pokémon GO (Community Days), Fortnite (live events), Clash Royale (special event modes).
- **Combines well with:** `pass-tracks` (05), `co-op-events` (06), `content-drip`.

### 08.12 Session caps — `session-caps`

- **Category:** time · per-period limits on attempts or rewards
- **Player fantasy:** "I've done today's big runs; tomorrow there's more." (Done badly: "Why won't it let me play?")
- **Core rules:**
  - *State:* counters per period (attempts, reward units, slots); optional carry-over bank.
  - *Triggers:* attempt or reward claim; reset boundary.
  - *Effects:* beyond the cap, rewards stop or diminish (soft cap), or attempts are blocked (hard cap).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| What is capped | rewards (preferred) vs play itself | Capping play blocks fun; capping rewards protects the economy |
| Attempts per period | 3–10 daily, or weekly limits on top rewards | Spreads high-value content |
| Soft-cap curve | rewards ×0.5 then ×0.1 beyond threshold | Keeps playing possible without breaking pacing |
| Carry-over | bank up to 2–7 days of unused attempts | Forgives missed days |
| Slots | 3–5 reward slots with unlock timers | Full slots waste wins — frustrating |

- **Dynamics:** engagement spread across days; protects the economy from binge players; full-slot waste aversion.
- **Aesthetic targets (MDA):** Submission.
- **Feedback and juice:** clear "3/3 used — resets in 6 h"; banked attempts shown as tokens.
- **Failure modes and exploits:** capping play outright; wasted rewards when slots are full; alt accounts bypassing caps.
- **Mobile fit:** good — sizes daily play to short sessions.
- **Monetization hooks and the ethical limit:** extra attempts, slot unlocks. Prefer reward caps over play caps; offer optional self-set play reminders; some jurisdictions restrict minors' play time — check `legal-ethics`.
- **Implementation notes:** counters keyed by `(player, cap_id, period_index)`; carry-over computed at reset.
- **Reference games:** Clash Royale (its original four-slot chest timers), Genshin Impact (weekly limits on discounted boss rewards).
- **Combines well with:** `reset-cadences`, `energy-stamina`, `pass-tracks` (05).

### 08.13 Rest bonuses — `rest-bonus`

- **Category:** time · accrued boost for breaks
- **Player fantasy:** "Taking a break doesn't put me behind — I come back boosted."
- **Core rules:**
  - *State:* `rest_pool` (capped).
  - *Triggers:* time away accrues the pool; gaining XP or rewards consumes it.
  - *Effects:* rewards are multiplied (e.g. ×2) until the pool is spent.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Accrual rate | full pool after 1–3 days away | Faster accrual favours frequent short breaks |
| Pool cap | 1–2 levels' worth of XP or 1–3 days of rewards | Caps catch-up so it can't skip content |
| Multiplier | ×1.5–2 | Small multipliers go unnoticed |
| Applies to | XP only, or currencies too | Currency rest bonuses affect the economy |

- **Dynamics:** casual players keep pace with hardcore; breaks framed positively.
- **Aesthetic targets (MDA):** Submission.
- **Feedback and juice:** a distinct colour segment on the XP bar showing the rested portion; "rested" icon.
- **Failure modes and exploits:** players feeling they must "use it up"; multipliers too small to notice; stacking with other boosts into runaway pacing.
- **Mobile fit:** excellent and respectful of real life.
- **Monetization hooks and the ethical limit:** rarely monetized; if premium raises the multiplier, keep the free version meaningful.
- **Implementation notes:**

```text
on_return(p, elapsed): p.rest = min(REST_CAP, p.rest + ACCRUAL * elapsed)
grant_xp(p, xp): bonus = min(p.rest, xp * (MULT - 1)); p.rest -= bonus; add_xp(p, xp + bonus)
```
- **Reference games:** World of Warcraft (rested XP), Final Fantasy XIV (rested EXP).
- **Combines well with:** `xp-levels` (05), `comeback-bonus`, `offline-progress`.

### 08.14 Cooldowns and charges — `cooldowns-charges`

- **Category:** time · in-play timing resource
- **Player fantasy:** "Wait for it… now!"
- **Core rules:**
  - *State:* per ability `charges`, `max_charges`, `cooldown`, `recharge_at` (in simulation ticks).
  - *Triggers:* use; tick.
  - *Effects:* use consumes a charge and starts recharge if idle; recharges complete one at a time (sequential model).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Cooldown | 1–60 s in combat; hours for daily abilities | Long cooldowns create big moments |
| Max charges | 1–3 | Charges allow bursts and forgive mistiming |
| Recharge model | sequential vs parallel | Sequential is easier to read |
| Cooldown reduction cap | 30–40 % | Uncapped CDR leads to spam |
| Shared / global cooldown | 0.5–1.5 s | Prevents instant ability chains |

- **Dynamics:** timing decisions; burst windows; reading opponents' cooldowns.
- **Aesthetic targets (MDA):** Challenge, Sensation.
- **Feedback and juice:** radial sweep on the button; ready flash and haptic tick; charge pips.
- **Failure modes and exploits:** CDR stacking; hidden cooldown state; wall-clock cooldowns that keep ticking while paused (use simulation ticks).
- **Mobile fit:** excellent with large buttons in the thumb zone and clear radial timers.
- **Monetization hooks and the ethical limit:** none in competitive modes; cooldown-reduction items in PvE only.
- **Implementation notes:**

```text
use(a, tick): require a.charges > 0; a.charges -= 1; if a.recharge_at is None: a.recharge_at = tick + a.cd
on_tick(a, tick): while a.recharge_at is not None and tick >= a.recharge_at:
  a.charges += 1; a.recharge_at = a.recharge_at + a.cd if a.charges < a.max else None
```
- **Reference games:** Brawl Stars (ammo bars), League of Legends: Wild Rift (cooldowns), Overwatch (charged abilities).
- **Combines well with:** `realtime-vs-turn`, `crits` (07), `interruption-safe`.

### 08.15 Move limits vs level timers — `level-limits`

- **Category:** time · per-level pressure
- **Player fantasy:** "One move left — can I pull it off?"
- **Core rules:**
  - *State:* `moves_left` and/or `time_left`; level goals.
  - *Triggers:* each move decrements; time ticks in simulation time; budget hits zero with goals unmet.
  - *Effects:* fail screen with a continue offer (+3 to +5 moves or +15–30 s); otherwise lose (and spend a life if `lives` is used).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Move budget | bot median moves-to-win × 1.1–1.4 | Primary difficulty lever in move-limited puzzles |
| Time budget | median clear time × 1.2–1.5 | Raises arousal; punishes interruptions |
| Continue size | +3 to +5 moves | Large enough to feel winnable |
| Continue pricing | first continue cheap, then rising, hard cap per attempt | Uncapped escalation becomes a spend trap |
| Near-win framing | "only 2 jellies left!" | Truthful framing converts; fabricated closeness is manipulative |

- **Dynamics:** move limits make planning puzzles (calm, interruptible); timers make action puzzles (tense); the fail screen is the highest-intent purchase moment in casual games.
- **Aesthetic targets (MDA):** Challenge, Sensation.
- **Feedback and juice:** move counter pulses red at 5 moves left; tense music layer in the last moves or seconds; big "+5" on continue.
- **Failure modes and exploits:** timers without auto-pause on interruption; budgets so tight that wins depend on refill luck; escalating continue prices with no cap.
- **Mobile fit:** move limits are ideal (interruption-proof); timers require auto-pause.
- **Monetization hooks and the ethical limit:** continues and extra-move boosters. Cap continues per attempt; never lie about how close the player is.
- **Implementation notes:** derive budgets from simulation: run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/match3_sim.py --level L.json --runs 500 --bot greedy --json` and set the budget at the percentile of bot moves-to-win that matches the level's `difficulty_target.win_rate`; record it in the level spec's `moves_or_time_limit`.
- **Reference games:** Candy Crush Saga (move and timed levels), Royal Match, Two Dots.
- **Combines well with:** `lives`, `assisted-refill` (07), `star-ratings` (05).

### 08.16 Content drip — `content-drip`

- **Category:** time · time-gated content release
- **Player fantasy:** "Tomorrow there's a new one — and everyone will be talking about it."
- **Core rules:**
  - *State:* content schedule (global release dates or per-player day unlocks); archive.
  - *Triggers:* reset boundary or release date.
  - *Effects:* new puzzle, chapter or episode unlocks; older content stays in an archive (optional).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Cadence | daily puzzle, weekly chapter, version-based story | Daily builds ritual; weekly builds anticipation |
| Scope | global (everyone same day) vs per-player | Global creates shared conversation |
| Archive | catch-up access to missed content | Prevents permanent loss |
| Binge allowance | none vs paid early access | Paid early access splits the community |
| Shared puzzle | identical for all players that day | Comparable results, shareable |

- **Dynamics:** synchronised community discussion; stretches production; blocks bingers.
- **Aesthetic targets (MDA):** Discovery, Fellowship.
- **Feedback and juice:** "new today" badge; shareable result card; countdown to the next release.
- **Failure modes and exploits:** bingers blocked and churning; paid early access resented; missed days lost forever; clients unlocking from local time.
- **Mobile fit:** excellent — a daily 2–5 minute ritual.
- **Monetization hooks and the ethical limit:** archive subscriptions, optional early access. Keep a free archive path for recent missed content.
- **Implementation notes:** schedule in remote config keyed by `day_index`; same seed or content id for all players on a shared day.
- **Reference games:** Wordle (one shared puzzle per day), Genshin Impact (version-based story releases).
- **Combines well with:** `reset-cadences`, `chapters-worlds` (05), `limited-time-events`.

### 08.17 Real-time vs turn-based — `realtime-vs-turn`

- **Category:** time · core-loop time model (design decision)
- **Player fantasy:** real-time: "Fast hands, fast decisions." Turn-based: "Take a breath, find the best move."
- **Core rules:**
  - *Real-time:* fixed-step simulation (30–60 Hz) advances continuously; inputs apply on the next tick.
  - *Turn-based:* state changes only on committed actions; optional turn timer.
  - *Hybrids:* real-time with pause, simultaneous turns, short real-time matches, auto-battle with interventions.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Match / level length | 1–3 min real-time; unlimited turn-based | Short real-time bursts suit mobile |
| Turn timer (PvP) | 15–90 s, with a visible warning | Stops stalling |
| Pause | always in single-player real-time | Interruptions otherwise cause losses |
| Auto-battle speed | 1×–3× | Respects repeat-content time |
| Simultaneous resolution | both players commit, then resolve | Removes waiting on the opponent's turn |

  Decision table:

| Constraint | Prefer |
|---|---|
| Frequent interruptions, one-hand play, commuting | turn-based or auto-battle |
| Arousal and dexterity are the fantasy | real-time in short bursts (≤ 3 min) |
| Async multiplayer | turn-based or simultaneous turns |
| Accessibility (motor) | turn-based, or real-time with adjustable speed |

- **Dynamics:** real-time rewards reflexes and produces spectacle; turn-based rewards planning and suits accessibility and interruption.
- **Aesthetic targets (MDA):** Sensation and Challenge (real-time); Challenge and Expression (turn-based).
- **Feedback and juice:** real-time: hit-stop, screen shake, audio sync; turn-based: preview of outcomes, satisfying commit animation.
- **Failure modes and exploits:** real-time single-player without pause; turn-based PvP stalling (timers); real-time PvP on poor mobile networks without reconnect.
- **Mobile fit:** both work; the hybrid sweet spots are short real-time matches and turn-based with auto.
- **Monetization hooks and the ethical limit:** speed-ups for auto-battle are acceptable in PvE; never in PvP.
- **Implementation notes:** both models run on a deterministic fixed-step sim-core (see `game-architecture`); turn-based uses a command queue, real-time an input buffer per tick.
- **Reference games:** Clash Royale (3-minute real-time matches), Hearthstone (turn timer with a visible "rope"), Marvel Snap (simultaneous turns), Into the Breach (turn-based).
- **Combines well with:** `interruption-safe`, `cooldowns-charges`, `async-turn-matches` (06).

### 08.18 Interruption-safe design — `interruption-safe`

- **Category:** time · resilience to the mobile environment
- **Player fantasy:** "A call came in, and when I came back everything was exactly as I left it."
- **Core rules:**
  - *State:* atomic snapshots of game state; resume tokens for online matches.
  - *Triggers:* app loses focus or is backgrounded (calls, notifications, lock screen), process killed by the OS, network drop.
  - *Effects:* auto-pause and save; resume to the exact state; online: reconnect window, then bot takeover or a graceful result.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Autosave frequency | every committed action/turn; every 5–15 s in real-time | More frequent = less loss on a kill |
| Resume countdown | 3-2-1 for real-time | Prevents instant death on resume |
| Reconnect grace (online) | 30–120 s | Survives a tunnel or elevator |
| Level resume after kill | resume, no life charged | Fairness and trust |
| Purchase recovery | re-verify pending transactions at startup | No lost purchases |

- **Dynamics:** trust; enables play in any spare minute.
- **Aesthetic targets (MDA):** Submission (comfort).
- **Feedback and juice:** "paused" overlay with a single big resume button; reconnecting indicator with countdown.
- **Failure modes and exploits:** state loss on process kill; double-charging energy or lives; pause abuse in timed puzzles (allow, but hide or blur the board while paused); half-saved files (atomic write: temp file then rename).
- **Mobile fit:** mandatory.
- **Monetization hooks and the ethical limit:** none. Never charge for an interruption the OS caused.
- **Implementation notes:** handle focus and pause hooks (Godot: `NOTIFICATION_APPLICATION_FOCUS_OUT`, `NOTIFICATION_APPLICATION_PAUSED`; Unity: `OnApplicationPause`, `OnApplicationFocus`); treat every background as possible termination.

```text
on_focus_out():  sim.paused = true; snapshot_atomic(sim.state)        # write tmp, fsync, rename
on_focus_in():   if realtime: show_countdown(3) then sim.paused = false
on_cold_start(): if exists(level_snapshot): offer_resume()            # no life or energy charged
on_net_drop():   hold_seat(RECONNECT_GRACE_S); else: bot_takeover_or_resolve()
```
- **Reference games:** Hearthstone (reconnect into an ongoing match), Clash Royale (reconnect into an ongoing battle).
- **Combines well with:** `realtime-vs-turn`, `lives`, `level-limits`.

### 08.19 Notification hooks — `notification-hooks`

- **Category:** time · re-engagement triggers
- **Player fantasy:** "It reminded me when something good was ready" — not "it nags me".
- **Core rules:**
  - *State:* per-category opt-ins; quiet hours; daily cap; scheduled local notifications; server push tokens.
  - *Triggers:* state changes that produce future ready times (energy full, build complete, your turn, event start, streak at risk).
  - *Effects:* local notifications scheduled or rescheduled; server pushes for social and live-ops events.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Permission ask timing | after the first value moment, with a pre-prompt | Asking at first launch lowers opt-in |
| Daily cap | 1–3 | More drives uninstalls and opt-outs |
| Quiet hours | e.g. 22:00–08:00 local | Respects sleep; mandatory for younger audiences |
| Categories | per-type toggles in settings | Players keep the useful ones on |
| Copy tone | informative, never guilt | Guilt copy erodes trust |

- **Dynamics:** return driver; annoyance and churn if overused.
- **Aesthetic targets (MDA):** Submission, Fellowship (social pings).
- **Feedback and juice:** deep link straight to the relevant screen; rich notification art for events.
- **Failure modes and exploits:** spam; guilt messaging ("your crops are dying!"); notifications after uninstall intent; night-time pings to minors.
- **Mobile fit:** platform-native: iOS requires user permission, and Android 13 (API 33) and later require the `POST_NOTIFICATIONS` runtime permission.
- **Monetization hooks and the ethical limit:** offer pushes only to opted-in players and within caps; never manipulative copy.
- **Implementation notes:** reschedule all local notifications on every relevant state change; server pushes via APNs/FCM; log `notification_sent` and `notification_open` for CRM analysis.

```text
on_state_change(p): cancel_all_local()
  for (type, t) in [("energy_full", p.energy_full_at), ("build_done", p.next_build_at)]:
    if p.optin[type] and sent_today(p) < CAP: schedule(type, shift_out_of_quiet_hours(t, p.tz))
```
- **Reference games:** Clash of Clans (upgrade-complete notifications), Words With Friends ("your turn"), Duolingo (streak reminders).
- **Combines well with:** `energy-stamina`, `build-timers-and-skips`, `async-turn-matches` (06).

### 08.20 Real-world clock — `real-world-clock`

- **Category:** time · world state bound to real time and date
- **Player fantasy:** "The world lives alongside mine — it's night there when it's night here."
- **Core rules:**
  - *State:* trusted current time (server-synchronised), local time zone, calendar.
  - *Triggers:* time of day, date, season, holidays.
  - *Effects:* day/night visuals, time-of-day spawns or shops, seasonal content, date events.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Time source | server time vs device clock | Device clocks invite time travel |
| Time-travel policy | ignore gains / allow with penalty / allow freely (single-player) | Harsh penalties punish travellers and DST |
| Granularity | hourly, day-part, daily, seasonal | Finer granularity = more reasons to return |
| Hemisphere / locale | north/south seasons, local holidays | Global audiences notice wrong seasons |
| Offline tolerance | monotonic deltas since last sync | Keeps offline play working |

- **Dynamics:** living-world feeling; daily rituals; time-travel communities (in single-player, often harmless).
- **Aesthetic targets (MDA):** Fantasy, Discovery.
- **Feedback and juice:** lighting and music shift with time of day; seasonal decorations.
- **Failure modes and exploits:** clock manipulation for timers and rewards; DST and time-zone travel bugs; wrong-hemisphere seasons.
- **Mobile fit:** natural on a device that always knows the time.
- **Monetization hooks and the ethical limit:** seasonal cosmetics. Do not punish time-zone travel with lost progress.
- **Implementation notes:** combine last server time with a monotonic clock; flag (don't destroy) suspicious forward jumps.

```text
trusted_now = last_server_time + (monotonic_now() - monotonic_at_sync)
if abs(device_now() - trusted_now) > SKEW_MAX: flag_time_skew()     # ignore resulting gains; resync when online
```
- **Reference games:** Animal Crossing: New Horizons (real-time clock and seasons), Pokémon GO (day/night), Neko Atsume.
- **Combines well with:** `appointment-mechanics`, `limited-time-events`, `offline-progress`.

---

## Session and energy design equations

| Question | Formula | Example |
|---|---|---|
| Actions per full bar | `cap ÷ cost_per_action` | 60 ÷ 6 = 10 levels |
| Full-bar time | `cap × regen_interval` | 60 × 5 min = 5 h |
| Natural sessions per day | `waking_hours ÷ full_bar_hours` (capped by intent) | 16 ÷ 5 ≈ 3 |
| Daily action ceiling | `(1440 ÷ interval_min) + bonus_energy` ÷ cost | (288 + 40) ÷ 6 ≈ 54 levels |
| Content runway | `content_levels ÷ daily_levels_p90` | 600 ÷ 54 ≈ 11 days for the most active players |
| Offline payout | `rate × min(elapsed, cap) × efficiency` | 1,000 × 480 × 0.5 = 240,000 |
| Streak survival | `q^(days−1)` for daily return probability q | 0.9²⁹ ≈ 4.7 % |

Feed these into `contract.json → analytics.kpi_targets.sessions_per_day` and `session_len_sec`, and verify against simulated archetypes with `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/economy_sim.py --model econ.json --runs 200 --json`.

## Time-trust and respect checklist

- [ ] All wall-clock mechanics use server time (or last server time + monotonic delta offline); device time is never trusted for rewards.
- [ ] Every timer has a visible end time and a free path (wait, help, ad) shown next to any paid skip.
- [ ] Nothing valuable expires or decays overnight; appointments reward returning rather than punishing absence.
- [ ] Streaks have automatic protection and a fair repair path; login calendars are cumulative.
- [ ] OS interruptions never cost lives, energy, streaks or match results; snapshots are atomic.
- [ ] Total daily obligations (dailies + event tasks + pass quests) stay within ~15–20 minutes.
- [ ] Notifications: opt-in after a value moment, per-category toggles, ≤ 3 per day, quiet hours, no guilt copy.
- [ ] Events convert leftover currency; their headline free reward is reachable by an engaged non-payer.
- [ ] Telemetry: `session_start`, `session_end` (length), `energy_depleted`, `timer_skip`, `streak_broken`, `streak_saved`, `notification_open`.

## Related skills

- `liveops` — event calendars, reset policies, segmentation.
- `player-analytics` — session, retention and streak cohort analysis.
- `mobile-ux` — interruption handling, notification permission flows, thumb-zone timers.
- `economy-design` — energy as a currency, timer sinks, offline income balance.
- `legal-ethics` — minors' play-time rules, notification and dark-pattern regulation.
