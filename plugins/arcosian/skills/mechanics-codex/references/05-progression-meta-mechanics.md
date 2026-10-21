# Progression and Meta Mechanics

Progression mechanics turn play into visible, accumulating change: numbers that grow, maps that fill, trees that branch, collections that complete. They operate on longer horizons than the core loop (session → day → week → season) and are the main levers on D7–D90 retention, on how fast content is consumed, and on where monetization pressure lands. This file catalogues 20 progression and meta mechanics in the shared mechanic-card format. Each entry gives precise rules, tuning ranges, dynamics, failure modes, a mobile verdict, the monetization hook with its ethical limit, and an implementation sketch. Use it to pick a progression stack for a concept, to spec a track for `contract.json → progression.tracks`, and to audit an existing meta for pacing, power creep and dark patterns. Pacing maths lives in `progression-difficulty`; currency flows in `economy-design`.

**Entry format.** Every entry maps 1:1 onto `${CLAUDE_PLUGIN_ROOT}/scripts/schemas/mechanic-card.schema.json` (`id`, `name`, `category`, `player_fantasy`, `rules`, `parameters`, `dynamics`, `aesthetics`, `feedback`, `failure_modes`, `mobile_fit`, `references`, `combos`). Ids are kebab-case; ids from sibling files carry their file number, e.g. `pity-timers` (07). Aesthetic targets use the eight MDA aesthetics (Hunicke, LeBlanc and Zubek, 2004): Sensation, Fantasy, Narrative, Challenge, Fellowship, Discovery, Expression, Submission.

**Sibling overlaps.** `prestige` here covers the progression arc; the economy maths of resets is in `prestige-rebirth` (04). Set-completion economics also appear in `collection-log` (09) and `set-bonuses` (09).

## Contents

| # | Id | Mechanic | Primary job | Horizon |
|---|---|---|---|---|
| 05.01 | `xp-levels` | XP and levels | Make every action count toward visible growth | session → weeks |
| 05.02 | `account-level` | Account level / world level | One meta gate that throttles and unlocks everything | weeks → months |
| 05.03 | `unlock-schedule` | Unlock trees and feature gating | Layer complexity at a learnable rate | first 14 days |
| 05.04 | `talent-tree` | Skill and talent trees | Build expression and long-term choice | weeks |
| 05.05 | `star-ratings` | Star ratings | Mastery replay and a soft currency from skill | per level |
| 05.06 | `saga-map` | Saga map | Linear journey, social comparison, "one more level" | months |
| 05.07 | `chapters-worlds` | Chapters and worlds | Package novelty; natural pause and release beats | days → weeks |
| 05.08 | `renovation-meta` | Renovation / decoration meta | Give puzzle wins meaning and self-expression | weeks |
| 05.09 | `collections-albums` | Collections and albums | Completion drive, trading, seasonal resets | weeks |
| 05.10 | `achievements` | Achievements | Recognise breadth and skill; steer to unused features | lifetime |
| 05.11 | `mastery-tracks` | Mastery tracks | Per-hero/weapon depth and status | weeks |
| 05.12 | `hero-ascension` | Hero levelling, ascension, star-up | Multi-axis investment in a roster | months |
| 05.13 | `gear-rarity` | Gear rarity tiers and fusion | Loot chase, salvage economy | weeks |
| 05.14 | `research-trees` | Research trees | Planned long-term global upgrades | weeks → months |
| 05.15 | `prestige` | Prestige / rebirth | Reset-for-multiplier loops that renew early game | hours → weeks |
| 05.16 | `seasonal-ladder` | Seasonal ladders | Periodic climb with soft reset | season |
| 05.17 | `win-streaks` | Win-streak ladders | Momentum and loss aversion within a run of levels | session → days |
| 05.18 | `login-calendar` | Login calendars | Habit and DAU with low cognitive load | 7–28 days |
| 05.19 | `missions-quests` | Missions and quests | Direct attention; daily structure | daily / weekly |
| 05.20 | `pass-tracks` | Pass tracks (battle/season pass) | Season-long engagement with a premium tier | season |

## Choosing a progression stack

| Concept type | Spine (pick 1) | Layers (pick 2–4) | Avoid early |
|---|---|---|---|
| Casual puzzle (match-3, sort, merge) | `saga-map` | `star-ratings`, `renovation-meta` or `collections-albums`, `win-streaks`, `pass-tracks` | `talent-tree`, `research-trees` |
| Hybrid-casual runner / arcade | `xp-levels` | `unlock-schedule` (skins/modes), `missions-quests`, `chapters-worlds` | `hero-ascension` with dupes |
| Idle / incremental | `prestige` | `research-trees`, `collections-albums`, `achievements` | hard energy gates (08) |
| Squad RPG / gacha | `hero-ascension` | `account-level`, `gear-rarity`, `talent-tree`, `login-calendar`, `pass-tracks` | more than 6 material currencies at launch |
| Competitive PvP (card, arena) | `seasonal-ladder` | `mastery-tracks`, `collections-albums`, `pass-tracks` | power-granting mastery |
| Base builder / 4X | `research-trees` | `unlock-schedule`, `account-level` (HQ level), `missions-quests` | uncapped multi-day timers in week 1 |

Rule of thumb: one **spine** that answers "where am I in this game?", at most two **power** axes the player must actively manage before day 7, and every additional layer must either add a new decision or reuse an existing currency.

---

### 05.01 XP and levels — `xp-levels`

- **Category:** progression · vertical track (player or character)
- **Player fantasy:** "Everything I do counts, and I can see myself getting stronger."
- **Core rules:**
  - *State:* `level` (int), `xp` (int, progress within the level), `need(level)` from a data table, optional `cap`.
  - *Triggers:* XP grants on core actions (win, clear, kill, merge), quests, first-time bonuses, multipliers (rested, boosters).
  - *Effects:* while `xp ≥ need(level)` and `level < cap`: subtract, increment level, grant `level_rewards[level]` (stats, unlock, currency), emit `level_up`. Multi-level-ups resolve in one transaction.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Curve shape | poly `base·L^e`, e 1.5–2.5; exp `base·g^(L−1)`, g 1.05–1.20; piecewise | Poly feels steady; exp is fast early then walls hard; piecewise lets you place milestone levels deliberately |
| Time-to-level | L1–5: 1–3 min each; mid game: 1–2 sessions; late: 2–7 days | Early level-ups are FTUE rewards; late levels become weekly goals |
| Source mix | 60–80 % core loop, 20–40 % quests/bonuses | Quest-heavy XP turns play into chores |
| Stat gain per level | 3–10 % of base per level | High gains feel powerful but out-scale content, forcing level-scaled enemies |
| Cap policy | soft cap via curve, or hard cap raised per season | Hard caps periodically close the gap between veterans and newcomers |

  Worked example: poly with base 100, e 1.8 → L10 needs 6,310 XP, L30 needs 45,585; cumulative to L30 ≈ 511k XP. At 2,000 XP per minute of play that is about 4.3 h to L30 — check this against the content you have for those hours.
- **Dynamics:** players discover and farm the best XP/min source; save big XP actions for multiplier windows; level becomes a status signal.
- **Aesthetic targets (MDA):** Submission (steady growth), Challenge (competence), Fantasy (becoming powerful).
- **Feedback and juice:** XP orbs fly from source to bar; bar ticks up with rising pitch; level-up moment ≤ 2 s and skippable; at ~80 % bar show "next: unlocks X".
- **Failure modes and exploits:** XP farming of a cheap repeatable action (add per-source daily diminishing returns); over-levelling trivialises content; returning players get a 12-pop-up level-up cascade (batch into one summary); level as the only power source lets veterans crush PvP newcomers.
- **Mobile fit:** passive, one-hand safe. Show the bar on results screens, not in the in-level HUD.
- **Monetization hooks and the ethical limit:** XP boosters, pass XP. Boosters should count down in play time, not wall-clock time while offline; never sell levels that buy PvP advantage without power-based matchmaking.
- **Implementation notes:** keep `need()` as a generated data table, not code; store it in `contract.json → progression.tracks[].curve`. Generate and sanity-check with `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/progression_calc.py curve --formula poly --levels 50 --base 100 --exponent 1.8 --xp-per-min 2000 --json`.

```text
add_xp(p, amount):
  p.xp += amount * multiplier(p)
  while p.level < CAP and p.xp >= need[p.level]:
    p.xp -= need[p.level]; p.level += 1
    queue_reward(level_rewards[p.level]); emit("level_up", p.level)
  commit(p)                     # one atomic save for the whole cascade
```
- **Reference games:** Call of Duty: Mobile, Pokémon GO (trainer level), the Diablo series, World of Warcraft.
- **Combines well with:** `unlock-schedule`, `pass-tracks`, `mastery-tracks`, `rest-bonus` (08).

### 05.02 Account level / world level — `account-level`

- **Category:** progression · meta gate (account-wide)
- **Player fantasy:** "My whole history in this game is recognised, and the world grows with me."
- **Core rules:**
  - *State:* `account_xp`, `account_level`; derived caps: `hero_level_cap(account_level)`, `energy_cap(account_level)`, optional `world_level` (enemy level and reward quality tier).
  - *Triggers:* XP from every mode, often proportional to energy spent, quests and story completion.
  - *Effects:* raises caps, unlocks features, at thresholds raises world level (stronger enemies, better drops).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Hero cap per account level | cap = account level, or 10-level bands | Throttles hardcore players; keeps the roster spread realistic |
| XP per energy spent | fixed ratio, e.g. 1 XP per energy | Ties account progress to the daily energy budget (predictable pacing) |
| World-level thresholds | every 5–10 account levels | Each step is a difficulty jump; too frequent feels like the game fights back |
| Feature gates | 1 new system per 2–5 levels early | See `unlock-schedule` |
| Energy cap growth | +1–5 per level | Longer sessions for invested players |

- **Dynamics:** creates a pacing governor the designer controls; players sometimes delay levelling to avoid world-level jumps ("level-down" behaviour).
- **Aesthetic targets (MDA):** Submission, Discovery, Challenge.
- **Feedback and juice:** account badge on profile; level-up screen lists exactly which caps rose; world-level change gets its own warning and celebration.
- **Failure modes and exploits:** world-level jump outpaces gear → players feel punished for progressing (offer an opt-down: Genshin Impact lets players lower World Level by a step); cap walls with no alternative progress; alt accounts at low level farming easy content for trading.
- **Mobile fit:** invisible complexity, good for short sessions; one number explains "why can't I level this hero".
- **Monetization hooks and the ethical limit:** energy refills feed account XP. Do not sell account levels; do not let world-level difficulty rise faster than the free player's power curve.
- **Implementation notes:** all caps are pure functions of `account_level` in a data table; server-authoritative; difficulty scaling reads `world_level` only.

```text
caps(account_level) -> {hero_cap: table_hero[al], energy_cap: table_energy[al], world_level: wl_for[al]}
on_account_level_change(p): p.caps = caps(p.account_level); unlock_check(p); if wl changed: show_world_level_notice(p)
```
- **Reference games:** Genshin Impact (Adventure Rank, World Level), Clash Royale (King Level), Marvel Snap (Collection Level as an account-wide track).
- **Combines well with:** `hero-ascension`, `unlock-schedule`, `energy-stamina` (08).

### 05.03 Unlock trees and feature gating — `unlock-schedule`

- **Category:** progression · complexity layering
- **Player fantasy:** "The game keeps opening up; there's always something new around the corner."
- **Core rules:**
  - *State:* set of unlocked nodes; unlock graph `{id, requires{level|quest|building|stars}, reveal_at, tutorial}`.
  - *Triggers:* any change to a prerequisite stat.
  - *Effects:* node moves hidden → revealed (locked icon with requirement) → unlocked; queues a one-time tutorial.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Systems in first 10 minutes | 1–2 | More overloads; fewer bores the curious |
| Unlock spacing | week 1: one per 1–3 sessions; later: every 3–7 days | Sustains novelty through the D7 cliff |
| Reveal lead | show 1–2 upcoming unlocks with requirement | Creates goals; too many locked icons clutter the HUD |
| Gate type | level, content completion, or building | Content gates guarantee competence; level gates allow grind-around |
| Social unlock timing | D1–D3 | Guild/friends unlocking after D7 misses most players |

- **Dynamics:** layered learning (one system mastered before the next arrives); anticipation; long-tail goals.
- **Aesthetic targets (MDA):** Discovery, Challenge.
- **Feedback and juice:** unlock cinematic ≤ 3 s, spotlight on the new button, one-line value proposition, red dot cleared after first use.
- **Failure modes and exploits:** "feature dump" at one level (5 systems at once); key retention systems gated too late; locked-feature icons that look like ads for payment; red-dot inflation (every button always badged).
- **Mobile fit:** essential — progressive HUD keeps ≤ 5 top-level buttons in session one; thumb-zone placement for the newest unlock.
- **Monetization hooks and the ethical limit:** early purchase of cosmetic unlocks is fine; do not paywall accessibility options or fair-play QoL (auto-battle in PvE can be paid convenience; reading aids cannot).
- **Implementation notes:** data-driven graph, evaluated on events, idempotent, validated offline for cycles and reachability.

```text
unlocks: [{id:"guild", requires:{account_level:8}, reveal_at:{account_level:6}, tutorial:"tut_guild"}]
on_stat_change(p): for u in pending(p): if met(u.requires, p): unlock(p, u); queue_tutorial(u.tutorial)
               elif met(u.reveal_at, p): reveal(p, u)
```
- **Reference games:** Hay Day (buildings by level), Clash of Clans (Town Hall gating), Homescapes.
- **Combines well with:** `xp-levels`, `account-level`, `missions-quests`, `content-drip` (08).

### 05.04 Skill and talent trees — `talent-tree`

- **Category:** progression · horizontal choice / build expression
- **Player fantasy:** "I build my own version of this hero."
- **Core rules:**
  - *State:* DAG of nodes `{id, cost, prereqs, effect, max_rank}`; `points_available`; `allocations`.
  - *Triggers:* points from levels, quests or currency; respec action.
  - *Effects:* allocating applies modifiers through the stat pipeline; respec refunds points for a cost.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Nodes ÷ points at cap | 1.5–3× | Below 1.5 everyone gets everything (no choice); above 3 feels thin |
| Node power | minor +2–5 %; keystones transformative | All-minor trees are noise; keystones create builds |
| Branch exclusivity | soft (cost) or hard (choose 1 of 3) | Hard exclusivity forces identity |
| Respec cost | free / cheap / time-gated | Cheap respec encourages experimentation |
| Tree size on mobile | 15–40 nodes | Larger needs pan/zoom and kills readability |

- **Dynamics:** theorycrafting; build convergence on an optimum ("meta build"); community guides.
- **Aesthetic targets (MDA):** Expression, Challenge, Discovery.
- **Feedback and juice:** before/after stat diff on tap-hold; path highlights to the target node; keystone unlock gets a unique VFX and SFX.
- **Failure modes and exploits:** false choices (if a node has > 80 % pick rate among top players, fold it into the base kit); trap nodes; respec paywall punishing experimentation; stacking multiplicative nodes into runaway damage.
- **Mobile fit:** portrait needs vertical lanes rather than a sprawling web; tap to inspect, second tap to buy; never require precision drags.
- **Monetization hooks and the ethical limit:** respec tokens. Give at least one free respec per season and after any balance change that nerfs a node.
- **Implementation notes:** validate DAG (acyclic, every node reachable, point budget feasible); modifiers aggregate add → multiply → override; log allocations for pick-rate telemetry.

```text
can_allocate(p, n): p.points >= n.cost and all(p.rank[q] >= 1 for q in n.prereqs) and p.rank[n] < n.max_rank
stat(s) = (base[s] + Σ add[s]) * Π (1 + mult[s]) ; then apply overrides
```
- **Reference games:** Path of Exile (passive tree), Diablo IV, Vampire Survivors (flat, refundable PowerUp shop).
- **Combines well with:** `account-level`, `gear-rarity`, `prestige`.

### 05.05 Star ratings — `star-ratings`

- **Category:** progression · mastery grading
- **Player fantasy:** "I beat it — and I know I can beat it better."
- **Core rules:**
  - *State:* per level `best_stars ∈ {0..3}`, thresholds `[t1,t2,t3]` on score, moves left or time.
  - *Triggers:* level completion.
  - *Effects:* `best_stars = max(best_stars, stars_earned)`; only the delta is added to a star wallet or total used for gates/spending.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| 1★ | completion | Never block progress beyond completion |
| 2★ threshold | reached by 50–70 % of first wins | Mid bar signals "good" |
| 3★ threshold | reached by 10–30 % of first wins | Drives replay; too hard feels luck-based |
| Star usage | gates, spendable currency, or cosmetic | Spendable stars bind skill to meta progress |
| Star gate size | 70–85 % of available stars | Tight gates force replays of disliked levels |

- **Dynamics:** completionist replays; skill expression in a casual frame; meta currency that rewards quality, not just quantity.
- **Aesthetic targets (MDA):** Challenge, Submission.
- **Feedback and juice:** score bar with star pips filling in-level; stars slam in one by one on results with rising pitch; "new best" banner.
- **Failure modes and exploits:** 3★ dependent on RNG (players feel cheated); boosters trivialise 3★ (if boosters are paid, stars become bought); gates that demand 3★ on tedious levels.
- **Mobile fit:** excellent — glanceable, one-hand, fits 1–3 minute levels.
- **Monetization hooks and the ethical limit:** boosters and extra moves help reach thresholds. The main path must be clearable at about a 2★ average; never require 3★ to progress.
- **Implementation notes:** set thresholds from bot score distributions, not by hand: run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/match3_sim.py --level L.json --runs 500 --bot greedy --json` and place t2/t3 at roughly the p40 and p85 of winning scores, then confirm with human playtests.
- **Reference games:** Angry Birds, Cut the Rope, Candy Crush Saga.
- **Combines well with:** `chapters-worlds`, `saga-map`, `renovation-meta`.

### 05.06 Saga map — `saga-map`

- **Category:** progression · linear content spine
- **Player fantasy:** "I'm on a journey through a world, and I can see how far I've come."
- **Core rules:**
  - *State:* `current_level` index; episodes of N levels with theme and mechanic introductions; per-level difficulty label (normal / hard / super hard).
  - *Triggers:* winning the current level.
  - *Effects:* advance pointer, play node-unlock animation, show friends' avatars at their positions, grant episode rewards at boundaries.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Levels per episode | 10–20 | Shorter episodes give more frequent "chapter complete" beats |
| New element cadence | every 10–30 levels | Slower feels stale; faster overwhelms |
| Difficulty rhythm | sawtooth; hard level every 5–10, super hard every 20–40 | Hard spikes create spending moments and relief after |
| Win-rate floor | first-attempt win rate ≥ 20–30 % even on hard levels | Below this, churn concentrates on specific levels |
| Look-ahead | show next 5–15 nodes | Anticipation without spoilers |

- **Dynamics:** steady forward motion; social comparison; "one more level" sessions; churn clusters at spike levels.
- **Aesthetic targets (MDA):** Challenge, Narrative (light), Fellowship (comparison).
- **Feedback and juice:** path lights up node by node; avatar hops forward; episode gate with themed transition art.
- **Failure modes and exploits:** content treadmill (compare the p90 player's levels-per-week against your production rate; the gap is how long until your best players hit "new levels coming soon"); undiagnosed churn levels (track per-level attempts, wins and churn); late cohorts stuck at a single wall.
- **Mobile fit:** perfect — vertical scroll, single tap to play, 1–3 minute levels.
- **Monetization hooks and the ethical limit:** lives, pre-level boosters, extra moves at fail. Label hard levels honestly; never raise difficulty selectively for players who have paid.
- **Implementation notes:** each level is a level spec (`${CLAUDE_PLUGIN_ROOT}/scripts/schemas/level-spec.schema.json`) with a `teach` tag (teach / test / twist / reward). Generate the target win-rate curve with `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/difficulty_curve.py generate --levels 200 --pattern sawtooth --base 0.7 --floor 0.25 --period 10 --hard-every 5 --json`, then fit live data with `difficulty_curve.py analyze --data levels.csv`.
- **Reference games:** Candy Crush Saga, Royal Match, Toon Blast.
- **Combines well with:** `star-ratings`, `win-streaks`, `renovation-meta`, `lives` (08).

### 05.07 Chapters and worlds — `chapters-worlds`

- **Category:** progression · content packaging and gating
- **Player fantasy:** "A new place to conquer, with new rules to learn."
- **Core rules:**
  - *State:* ordered chapters `{id, theme, levels[], gate, finale, asset_bundle}`; current chapter.
  - *Triggers:* chapter completion or gate condition met (stars, keys, timer, purchase).
  - *Effects:* unlock next chapter, download its assets if needed, introduce a new mechanic, play a finale or boss.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Levels per chapter | 10–40 | Long chapters sag mid-way without a twist |
| Novelty per chapter | ≥ 1 new mechanic or twist | Re-skins alone do not reset boredom |
| Gate type | completion / star threshold / keys / time / payment | Each step to the right raises friction |
| Chapter duration | 3–7 days of normal play (casual) | Matches weekly release and marketing beats |
| Finale | boss, set-piece puzzle, narrative payoff | Gives an ending, not just a stop |

- **Dynamics:** natural pause points; anticipation for the next world; marketing and live-ops beats ("World 6 is live").
- **Aesthetic targets (MDA):** Discovery, Narrative, Challenge.
- **Feedback and juice:** world map reveal; palette and music change at chapter boundary; finale reward chest.
- **Failure modes and exploits:** gates as disguised paywalls; theme swap without mechanical change; chapter too long; download stall at the boundary (prefetch on Wi-Fi).
- **Mobile fit:** chapters are ideal session-end rewards; deliver assets per chapter via on-demand resources / Play Asset Delivery to keep install size small.
- **Monetization hooks and the ethical limit:** chapter unlock purchase or "unlock full game" (premium-lite). State the free/paid boundary on the store page and before the player commits.
- **Implementation notes:** content manifest per chapter; gate evaluation shared with `unlock-schedule`; asset bundle versioning.
- **Reference games:** Angry Birds, Cut the Rope (boxes unlocked by stars), Monument Valley, Super Mario Run (free opening, one-time unlock).
- **Combines well with:** `star-ratings`, `saga-map`, `content-drip` (08), `limited-time-events` (08).

### 05.08 Renovation / decoration meta — `renovation-meta`

- **Category:** progression · dual-loop meta (core puzzle → meta spend)
- **Player fantasy:** "I'm restoring something beautiful, and it reflects my taste."
- **Core rules:**
  - *State:* areas made of tasks `{id, cost_stars, prereqs, choices[2–3], story_beat}`; star wallet; area completion %.
  - *Triggers:* each core-level win grants stars (often 1 per win); player taps a task to spend.
  - *Effects:* task completes with an animated build, optional decor choice, story beat; area completion unlocks the next area.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Stars per task | early 1–2; later 3–6 | Higher costs stretch the meta relative to the puzzle cadence |
| Wins per task | 1–3 | More than ~3 wins between payoffs makes the meta feel stalled |
| Decor choices | 2–3 per visible item | Expression; more than 3 slows sessions |
| Tasks per area | 8–15 | Area completion every 3–7 days for a regular player |
| Story beat frequency | every 2–4 tasks | Narrative pull without cutscene fatigue |

- **Dynamics:** losses in the puzzle have context ("I need two more stars for the fountain"); session ends on a satisfying build; story cliffhangers drive returns.
- **Aesthetic targets (MDA):** Expression, Narrative, Fantasy.
- **Feedback and juice:** before/after transformation with sparkles and a camera move; character reaction lines; area-complete photo moment.
- **Failure modes and exploits:** meta disconnected from core (players skip it, retention gain vanishes); choices that change nothing visible; star costs inflating faster than win rate; writing that talks down to the audience.
- **Mobile fit:** strong — one tap per task; but large decorated scenes need atlasing and LODs to stay inside the low-end memory budget (see `mobile-performance`).
- **Monetization hooks and the ethical limit:** premium decor sets, story-skip offers. Never pre-select the paid variant in a choice; free variants must look finished, not deliberately ugly.
- **Implementation notes:** task graph per area as data; stars as a single currency in `economy.currencies`; cutscenes referenced by id so writers can iterate without code changes.

```text
spend(p, task): require p.stars >= task.cost and prereqs_done(p, task)
  p.stars -= task.cost; p.tasks.add(task.id); if task.choices: await choice -> p.decor[task.slot] = choice
  play(task.build_anim); if task.story_beat: play(task.story_beat); if area_done(p): unlock_next_area(p)
```
- **Reference games:** Gardenscapes, Homescapes, Royal Match (castle areas), Project Makeover.
- **Combines well with:** `star-ratings`, `saga-map`, `collections-albums`, `narrative-design` (skill).

### 05.09 Collections and albums — `collections-albums`

- **Category:** progression · set completion
- **Player fantasy:** "Complete the set — and show it off."
- **Core rules:**
  - *State:* album of sets; each set has items with rarity; `owned[item]` counts; album season id.
  - *Triggers:* item drops from packs, events, rewards; trades; duplicate conversion.
  - *Effects:* set completion grants a reward; album completion grants a grand prize; duplicates convert to a currency or trade stock; album resets at season end.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Set size | 6–12 items | Small sets give frequent completion beats |
| Album size | 50–200 items | Defines season length for the chase |
| Rarity tiers | 3–5 | Rare items create the "last card" chase |
| Duplicate handling | trade, convert to currency, or exchange shop | Determines whether completion is deterministic |
| Season length | 4–8 weeks | Long enough to finish with steady play |

  Maths: with n equally likely items, expected draws to complete is n·Hₙ (coupon collector): 20 items ≈ 72 draws, 50 ≈ 225, 100 ≈ 519. Rarity weighting makes the last rare item dominate — this is why a duplicate-exchange path is non-negotiable.
- **Dynamics:** completion drive; trading and gifting communities; "one missing card" frustration and social requests.
- **Aesthetic targets (MDA):** Discovery, Fellowship (trading), Submission.
- **Feedback and juice:** sticker flip reveal with rarity flare; set-complete fanfare; album page fills visibly.
- **Failure modes and exploits:** last-item scarcity engineered to drive spend; multi-account trading farms; expiry pressure on near-complete albums.
- **Mobile fit:** excellent — browsing albums and trading are short-session friendly.
- **Monetization hooks and the ethical limit:** paid packs are paid random items (odds disclosure required on both stores; see `07-randomness-chance-mechanics.md`). Always provide a deterministic completion path (duplicate exchange or wildcard). In Japan, "complete gacha" — paid random items that must be collected as a set to win a prize — has been treated as unlawful since 2012; check `legal-ethics` before any set-for-prize design.
- **Implementation notes:** Monte Carlo the time-to-complete per player archetype before launch (extend the economy model and run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/economy_sim.py --model econ.json --runs 500 --json`); rate-limit trades per day; server-side ownership.
- **Reference games:** Monopoly GO (sticker albums), Coin Master (card collections), Pokémon GO (Pokédex), Marvel Snap (card collection).
- **Combines well with:** `trading` (06), `mystery-boxes` (07), `duplicate-protection` (07), `limited-time-events` (08).

### 05.10 Achievements — `achievements`

- **Category:** progression · recognition layer
- **Player fantasy:** "The game noticed what I did."
- **Core rules:**
  - *State:* `achievements[] {id, stat, threshold, tier, hidden, reward}`; lifetime stat counters.
  - *Triggers:* gameplay events increment counters.
  - *Effects:* one-time unlock on threshold; optional reward; sync to Game Center / Google Play Games.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Count | 30–100 | Too few feels thin; too many becomes noise |
| Mix | progress ~40 %, skill ~30 %, exploration/secret ~20 %, social ~10 % | Breadth steers players to unused features |
| Tier multipliers | ×5–×10 per tier (10 → 100 → 1,000) | Long-tail goals without many entries |
| Reward | cosmetic, small currency, or none | Currency rewards get farmed; cosmetics signal status |
| Hidden share | 5–15 % | Surprise and discovery |

- **Dynamics:** completionist play; feature discovery; play-style variety.
- **Aesthetic targets (MDA):** Challenge, Discovery, Expression.
- **Feedback and juice:** non-blocking toast with a distinct sound; a trophy room or profile showcase; rarity percentage ("12 % of players have this").
- **Failure modes and exploits:** grind achievements with no texture; achievements that reward degenerate play (never reward losing PvP matches — it creates tanking); pop-up spam during gameplay.
- **Mobile fit:** good when toasts never cover the play area; batch reveals on the results screen.
- **Monetization hooks and the ethical limit:** none needed. Never create "spend X" achievements.
- **Implementation notes:** event subscription map from stat → achievements; idempotent unlock; offline queue for platform submission with retry; server validation for competitive ones.

```text
on_event(e): for a in subscribers[e.stat]:
  v = stats.inc(e.stat, e.amount)
  if not a.unlocked and v >= a.threshold: a.unlocked = true; grant(a.reward); toast(a); platform_queue.push(a.id)
```
- **Reference games:** Hearthstone (achievements), Pokémon GO (medals), platform achievement systems (Game Center, Google Play Games).
- **Combines well with:** `missions-quests`, `mastery-tracks`, `collections-albums`.

### 05.11 Mastery tracks — `mastery-tracks`

- **Category:** progression · per-entity depth
- **Player fantasy:** "I'm an expert with this hero / weapon / card, and others can see it."
- **Core rules:**
  - *State:* map `entity_id → {mastery_xp, tier}`; optional mastery tasks per entity.
  - *Triggers:* using the entity (match played, kills, wins), completing its tasks.
  - *Effects:* tier-ups grant cosmetics, badges, titles, or small currency; rarely minor stats.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Tiers | 5–10 | Early tiers fast to invite sampling; late tiers slow for mains |
| XP per use | win > loss, but both positive | Loss XP keeps it from feeling punitive |
| Reward type | cosmetic / currency / ≤ 2–5 % stats | Stats in PvP make it pay-to-win-by-time |
| Task specificity | generic ("play 10") vs specific ("win with 3 combos") | Specific tasks teach depth |
| Display | badge in match, profile emblem | Status signalling |

- **Dynamics:** encourages trying many entities early (cheap first tiers) and deepening a main later; mastery badges intimidate or inform opponents.
- **Aesthetic targets (MDA):** Expression, Challenge, Fellowship (status).
- **Feedback and juice:** emblem upgrade animation; mastery flourish at match start; progress shown on the entity's card.
- **Failure modes and exploits:** power-granting mastery; tasks that push off-meta picks into ranked and hurt teammates (keep tasks completable in casual modes); AFK farming of "games played".
- **Mobile fit:** good — passive accrual, visible on cards.
- **Monetization hooks and the ethical limit:** mastery XP boosts, cosmetic upgrades. Keep competitive power out of mastery.
- **Implementation notes:** reuse the `xp-levels` curve engine keyed by entity; one table per entity class.
- **Reference games:** League of Legends (champion mastery), Call of Duty (weapon levels and camos), Clash Royale (Card Mastery).
- **Combines well with:** `achievements`, `xp-levels`, `matchmaking-rating` (06).

### 05.12 Hero levelling, ascension and star-up — `hero-ascension`

- **Category:** progression · multi-axis roster investment
- **Player fantasy:** "I raise my favourite from recruit to legend."
- **Core rules:**
  - *State:* per hero `level`, `ascension` (raises the level cap), `star` (limit break from duplicates or shards), skill levels.
  - *Triggers:* spend XP items / soft currency (level), farmed materials at a cap (ascension), duplicates or shards (star-up).
  - *Effects:* each axis raises stats multiplicatively; ascension and star thresholds unlock passives.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Level-cap cadence | caps every 10–20 levels | Each cap is a farming objective |
| Materials per tier | ×1.5–2.5 per tier | Geometric growth stretches late game |
| Shards per star | e.g. 10/20/40/80/160 (310 total) | At 5 shards/day F2P that is 62 days to max — an intentional chase |
| Stat gain per star | +10–25 % | Large gains make dupes mandatory for competitive play |
| Material source spread | 3–6 distinct content sources | Forces content variety; too many becomes a chore map |

- **Dynamics:** sunk-cost attachment to invested heroes; "few stars vs wide bench" decisions; daily farming routes; power creep pressure on each new hero release.
- **Aesthetic targets (MDA):** Fantasy, Submission, Challenge.
- **Feedback and juice:** ascension transformation (new art frame, aura); star-up with stars slamming in; stat deltas in green.
- **Failure modes and exploits:** power creep makes old investments worthless (offer hero reset with ≥ 80–100 % refund, or resource transfer); duplicates as the only route to max (whale-only); 20+ material currencies overwhelm.
- **Mobile fit:** good with one-tap "level to max affordable" and "where to get" links on every material.
- **Monetization hooks and the ethical limit:** shard packs, gacha duplicates, material bundles. Every hero needs a free shard path; disclose before purchase that maximum power requires duplicates; refund materials on hero reset.
- **Implementation notes:** store each axis separately; compute stats on read; keep a deterministic reset refund function.

```text
can_level(h) = h.level < cap_for[h.ascension]
stat(h, s)   = base[s] * (1 + g_lvl * (h.level - 1)) * star_mult[h.star] + asc_flat[h.ascension][s]
reset(h)     = refund(materials_spent(h) * REFUND_RATE); h.level = 1; h.ascension = 0   # stars kept
```
- **Reference games:** Genshin Impact (ascension, constellations), AFK Arena (ascension tiers), Raid: Shadow Legends (rank-up with fodder), Clash Royale (card levels from duplicates).
- **Combines well with:** `gacha-banners` (07), `gear-rarity`, `account-level`, `energy-stamina` (08).

### 05.13 Gear rarity tiers and fusion — `gear-rarity`

- **Category:** progression · item power and loot chase
- **Player fantasy:** "That orange glow means something big just dropped."
- **Core rules:**
  - *State:* item `{base_id, rarity, level, affixes[]}`; rarity sets stat budget and affix count.
  - *Triggers:* drops, crafting, fusion (consume N identical items → next rarity), salvage.
  - *Effects:* equip modifies stats; fusion raises rarity; salvage returns materials.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Tier count | 4–7 | More tiers lengthen the chase but blur distinctions |
| Budget per tier | ×1.3–1.6 per tier | Steeper makes rarity dominate over level |
| Drop shares | e.g. 60 / 25 / 10 / 4 / 1 % | Top tier rarity sets the excitement frequency |
| Fusion ratio | 3:1 standard, 2:1 lenient | Deterministic path to rarity |
| Colour language | grey, green, blue, purple, orange (widely learned) | Instant read; pair with shape or label for colour-blind players |

- **Dynamics:** loot excitement; inventory management; salvage economy; build-around items.
- **Aesthetic targets (MDA):** Sensation, Discovery, Fantasy.
- **Feedback and juice:** beam of light in rarity colour on drop; distinct drop SFX per tier; slow-motion reveal for top tier only.
- **Failure modes and exploits:** inventory bloat (auto-salvage filters, stacking); tier inflation (adding a new top tier every update devalues all owned gear); colour-only encoding fails colour-blind players.
- **Mobile fit:** needs auto-equip best, batch salvage and an inventory cap with a clear overflow rule.
- **Monetization hooks and the ethical limit:** gear chests and bundles. Random paid chests need odds disclosure; keep fusion as a deterministic, free alternative.
- **Implementation notes:** `budget = base_budget[slot] * rarity_mult[r] * level_mult[l]`; fusion is a pure function, unit-test it; affix rolls in `procedural-affixes` (07).
- **Reference games:** the Diablo series, Archero (gear fusion), World of Warcraft (item quality colours).
- **Combines well with:** `procedural-affixes` (07), `loot-tables` (07), `hero-ascension`.

### 05.14 Research trees — `research-trees`

- **Category:** progression · timed global upgrades
- **Player fantasy:** "My civilisation advances while I plan the next breakthrough."
- **Core rules:**
  - *State:* DAG of nodes `{id, cost{res}, duration, prereqs, effect}`; `slots` (concurrent research); active jobs with absolute end timestamps.
  - *Triggers:* player starts research (pays cost); clock reaches end time; speed-up items.
  - *Effects:* permanent modifiers or unlocks; frees the slot.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Concurrent slots | 1–2 | Second slot is a common premium perk |
| Duration growth | minutes early → days late; ×1.3–1.6 per tier | Late multi-day timers create appointment returns and frustration |
| Effect per node | +2–10 % | Small nodes feel like chores; mix in a few unlock nodes |
| Branch width | 2–4 parallel branches | Real ordering decisions |
| Cost growth | ×1.2–1.5 per tier | Ties research to the soft-currency sink |

- **Dynamics:** long-horizon planning; optimal ordering puzzles; returns to the app when research completes.
- **Aesthetic targets (MDA):** Discovery, Submission, Challenge (planning).
- **Feedback and juice:** node completes with a satisfying stamp; tree visibly fills; push notification (opt-in) on completion.
- **Failure modes and exploits:** a tree everyone completes in the same order (no real choice); timers that exist only to sell skips; device-clock manipulation (server-authoritative end times).
- **Mobile fit:** fine for short sessions (start research, leave); keep the tree readable in portrait with branch tabs.
- **Monetization hooks and the ethical limit:** speed-ups and extra slots. Show skip cost transparently and proportional to time left; no fake "last chance" timers.
- **Implementation notes:** same DAG validator as `talent-tree`; jobs store `ends_at` (server UTC); completion resolved lazily on next read.
- **Reference games:** Clash of Clans (Laboratory), Civilization (tech tree), Rise of Kingdoms (Academy).
- **Combines well with:** `build-timers-and-skips` (08), `unlock-schedule`, `prestige`.

### 05.15 Prestige / rebirth — `prestige`

- **Category:** progression · voluntary reset loop
- **Player fantasy:** "Start over, but stronger — and blaze through what used to be hard."
- **Core rules:**
  - *State:* run progress (resources, generators, upgrades); `lifetime_earned`; permanent meta-currency `prestige_points`.
  - *Triggers:* player chooses to prestige.
  - *Effects:* run state resets; player gains points from a sublinear function of lifetime earnings; points grant permanent multipliers or unlocks.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Gain formula | `k·E^(1/3)` or `k·√E` of lifetime earnings | Cube root means 8× the earnings to double the points: natural reset rhythm |
| First prestige | 30–90 min of play (idle) | Earlier is confusing; later risks a wall before the twist |
| Bonus per point | +1–10 % production | Sets how dramatic each new run feels |
| Persistence | which upgrades survive the reset | Keeping too much removes the "fresh run" joy |
| Layers | 1–3 prestige layers | Each layer is a late-game novelty injection |

- **Dynamics:** optimal-reset-time problem (prestige when marginal point gain per minute falls below the run speed-up value); exhilarating replays of early game.
- **Aesthetic targets (MDA):** Submission, Challenge (optimisation), Discovery (new layers).
- **Feedback and juice:** show "prestige now for +N points (×M speed)" with a projected-time preview; a dramatic reset animation; first minute after reset visibly much faster.
- **Failure modes and exploits:** players don't understand what they keep (preview it); gains that feel negligible; floating-point overflow after 1e308.
- **Mobile fit:** excellent for idle sessions of 1–5 minutes and offline accrual.
- **Monetization hooks and the ethical limit:** permanent multipliers, prestige boosters. Do not sell resets that trivialise every layer; keep purchases additive, not mandatory.
- **Implementation notes:** use a big-number type (mantissa + exponent) once values exceed double range; Cookie Clicker derives prestige from a cube root of lifetime earnings, a widely copied pattern.

```text
claimable = floor(K * cbrt(lifetime_earned / UNIT)) - p.points_total
on_prestige(p): p.points_total += claimable; reset_run(p, keep=PERSISTENT); p.mult = 1 + BONUS * p.points_total
```
- **Reference games:** Cookie Clicker, AdVenture Capitalist, Egg, Inc., Tap Titans.
- **Combines well with:** `idle-accumulation` (08), `offline-progress` (08), `research-trees`.

### 05.16 Seasonal ladders — `seasonal-ladder`

- **Category:** progression · periodic competitive track
- **Player fantasy:** "Every season I climb again and prove where I belong."
- **Core rules:**
  - *State:* visible rank/tier with stars or points; rank floors; season id; hidden MMR (see `matchmaking-rating` (06)).
  - *Triggers:* match results; season end.
  - *Effects:* rank up/down; end-of-season rewards by peak or final rank; soft reset at season start.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Season length | 4–12 weeks | Short seasons keep ladders fresh; long ones reward consistency |
| Reset compression | `new = floor + α·(old − floor)`, α 0.3–0.7 | Low α = harsh reset grind; high α = stagnant ladder |
| Rank floors | every 3–5 ranks | Protect milestones and reduce tilt queuing |
| Streak bonus | extra star for 3+ wins at low ranks | Speeds deserving players out of low ranks |
| Inactivity decay | top tiers only | Keeps the top of the ladder live |

- **Dynamics:** fresh-start motivation; end-of-season rush; smurfing and boosting after resets.
- **Aesthetic targets (MDA):** Challenge, Fellowship (status).
- **Feedback and juice:** rank-up crest animation; demotion-protection shields shown explicitly; season-end reward reveal.
- **Failure modes and exploits:** reset fatigue (same climb every month); win-trading; smurf accounts farming low ranks (match on hidden MMR, not visible rank).
- **Mobile fit:** good when matches are 2–5 minutes.
- **Monetization hooks and the ethical limit:** cosmetic season rewards, pass synergies. Never sell rank or matchmaking advantage.
- **Implementation notes:** keep visible rank and hidden MMR separate; reset function is data-driven; audit win-trading by repeated opponent pairs.
- **Reference games:** Hearthstone (ranked with floors and streak bonuses at lower ranks), League of Legends (ranked seasons), Clash Royale (Path of Legends).
- **Combines well with:** `leagues-divisions` (06), `pass-tracks`, `matchmaking-rating` (06).

### 05.17 Win-streak ladders — `win-streaks`

- **Category:** progression · momentum with loss aversion
- **Player fantasy:** "I'm on fire — and I don't want it to end."
- **Core rules:**
  - *State:* `streak_tier` (0..N).
  - *Triggers:* level win → tier+1 (capped); level loss → tier reset to 0 (or −1 in lenient variants).
  - *Effects:* start-of-level bonus scales with tier (pre-placed boosters, reward multiplier).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Tiers | 3–5 | More tiers sharpen loss aversion |
| Bonus at max tier | 1–3 free boosters or ×1.5–2 rewards | Large bonuses distort the difficulty curve |
| Loss penalty | full reset vs drop one tier | Full reset raises tension and churn risk |
| Protection | none / earned shield | Shields soften frustration |

- **Dynamics:** winners keep winning (snowball); intense "continue" decisions when the streak is at stake.
- **Aesthetic targets (MDA):** Challenge, Sensation.
- **Feedback and juice:** streak banner at level start; flame intensity per tier; streak-lost moment that is honest but not humiliating.
- **Failure modes and exploits:** snowballing hides the true difficulty curve (segment level telemetry by streak tier); pay-to-keep-streak pressure.
- **Mobile fit:** good — one banner, no extra input.
- **Monetization hooks and the ethical limit:** continue offers carry more weight when a streak is at risk. Show plainly what will be lost; never raise the continue price because a streak is at stake; cap continues per level.
- **Implementation notes:** apply the bonus at level start from `streak_tier`; log `streak_tier` on every level event for analysis.
- **Reference games:** many top match-3 titles (a genre convention), Hearthstone (streak bonus stars at lower ranks).
- **Combines well with:** `saga-map`, `lives` (08), `daily-streaks` (08).

### 05.18 Login calendars — `login-calendar`

- **Category:** progression · habit / attendance reward
- **Player fantasy:** "Showing up is rewarded, and something big is coming on day 7."
- **Core rules:**
  - *State:* calendar `{days[N], rewards[]}`, `claimed_count`, `last_claim_day` (server day index).
  - *Triggers:* first session on a new reset day.
  - *Effects:* claim reward `claimed_count+1`; advance; finale reward at N; new calendar on completion or month change.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Counting | cumulative (recommended) vs consecutive | Consecutive punishes real life and causes churn on a miss |
| Length | 7 (new player), 28–30 (monthly) | 7-day hooks the first week; monthly sustains |
| Reward curve | flat with spikes on 7 / 14 / 28 | Spikes create anticipation |
| Catch-up | make-up claims for missed days | Reduces miss-and-quit |
| Variants | new-player, returning-player, event calendars | Targeted value without inflation |

- **Dynamics:** DAU lift; habit formation; risk of log-in-and-leave (DAU without engagement).
- **Aesthetic targets (MDA):** Submission.
- **Feedback and juice:** one-tap claim with a satisfying stamp; the finale reward previewed from day 1.
- **Failure modes and exploits:** boot-time pop-up stack (keep ≤ 2 boot pop-ups); reward inflation; device clock changes (server day index only).
- **Mobile fit:** good — one tap at boot.
- **Monetization hooks and the ethical limit:** paid "monthly card" variants (daily drip after purchase). Show total value, duration and that claims require logging in; no auto-renewal without clear store subscription terms.
- **Implementation notes:** `day_index = floor((server_now − reset_offset) / 86400)`; claim allowed when `day_index > last_claim_day`.
- **Reference games:** HoYoLAB daily check-in (HoYoverse titles); near-universal in gacha RPGs and social casino games.
- **Combines well with:** `reset-cadences` (08), `daily-streaks` (08), `comeback-bonus` (08).

### 05.19 Missions and quests — `missions-quests`

- **Category:** progression · directed goals
- **Player fantasy:** "Clear goals, tidy rewards, a reason to try something new."
- **Core rules:**
  - *State:* quest instances `{template_id, params, progress, target, reward, expires_at, slot}`.
  - *Triggers:* gameplay events; daily/weekly reset generates new quests; reroll action.
  - *Effects:* progress increments; claim grants reward; expiry removes unclaimed quests (auto-claim preferred).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Daily count | 3–6 | Total completion ≈ 10–20 min of natural play |
| Weekly count | 5–10 | Bigger goals for the core audience |
| Play-naturally share | ~70 % generic, ~30 % specific | Specific quests teach features; too many feel like chores |
| Rerolls | 1 free per day | Lets players dodge disliked objectives |
| Reward share | 20–40 % of daily soft-currency income | Higher makes quests mandatory |

- **Dynamics:** directs attention to features; daily structure; checklist play if over-weighted.
- **Aesthetic targets (MDA):** Submission, Discovery.
- **Feedback and juice:** in-run progress toast ("2/3 merges"); claim-all button; completion chime.
- **Failure modes and exploits:** quests forcing an unwanted mode into ranked (griefing teammates); objectives only completable by paying; stacking daily, weekly, event and pass quests into a second job.
- **Mobile fit:** good when progress is visible without opening a menu.
- **Monetization hooks and the ethical limit:** pass-exclusive quests. Never make purchase quests, except inside a clearly labelled offer.
- **Implementation notes:** templates with parameter ranges; deterministic generation per player per day with `seed = hash(player_id, day_index)` so support can reproduce quests; event-bus subscriptions.
- **Reference games:** Hearthstone (daily and weekly quests), Fortnite (quests), Pokémon GO (Field Research).
- **Combines well with:** `pass-tracks`, `achievements`, `reset-cadences` (08).

### 05.20 Pass tracks (battle pass / season pass) — `pass-tracks`

- **Category:** progression · seasonal track with a premium tier
- **Player fantasy:** "My season's journey — every match moves me toward rewards I can see."
- **Core rules:**
  - *State:* season `{start, end, tiers[]}`; `pass_xp`; `premium_owned`; claimed flags per tier per track.
  - *Triggers:* pass XP from play and quests; premium purchase; optional tier purchase.
  - *Effects:* tier advances; free-track rewards claimable; premium purchase unlocks premium rewards retroactively for all reached tiers.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Season length | 4–10 weeks | Shorter seasons create more purchase moments and more fatigue |
| Tiers | 30–100 | Flat XP per tier is easiest to read |
| Target completion | engaged median finishes by 75–90 % of the season | Requiring daily max play breeds burnout |
| Premium value | 5–10× the price in perceived value | Below this conversion drops; above it devalues the store |
| Free-track richness | 30–50 % of total reward value | A barren free track feels like an advert |

  Worked example: 50 tiers × 1,000 XP = 50,000 XP; an 8-week (56-day) season targeted for completion by day 45 needs ~1,110 XP/day, or about 25 minutes of play if the loop yields ~45 XP/min.
- **Dynamics:** sustained engagement across the season; purchase spikes on day 1 and in the last week; sunk-cost pull near the end.
- **Aesthetic targets (MDA):** Submission, Expression (cosmetics), Fantasy.
- **Feedback and juice:** a single scrollable track with the next reward always on screen; claim-all; premium preview with a "you'd already have unlocked N rewards" counter.
- **Failure modes and exploits:** power items on the premium track in PvP games; unclaimed rewards lost at season end (auto-grant instead); XP pacing that needs every day's maximum.
- **Mobile fit:** excellent — one screen, one-tap claims, works with any session length.
- **Monetization hooks and the ethical limit:** premium pass, premium-plus with tier skips, tier purchases. The median engaged player must be able to finish without buying tiers; auto-grant unclaimed rewards; show the end date clearly.
- **Implementation notes:** server-side entitlement per season (non-consumable product or server grant; see `monetization`); tier table as data; XP sources logged for pacing analysis.
- **Reference games:** Fortnite (Battle Pass), Clash Royale (Pass Royale), Brawl Stars (Brawl Pass), PUBG Mobile (Royale Pass).
- **Combines well with:** `missions-quests`, `seasonal-ladder`, `limited-time-events` (08).

---

## Pacing formulas

| Question | Formula | Notes |
|---|---|---|
| Time to reach level L | `T(L) = Σ need(i) for i < L ÷ XP_per_min` | Use `progression_calc.py time-to-level --table levels.json --xp-per-min X` |
| Days to finish a track | `D = total_cost ÷ (daily_income × engagement_share)` | Run per archetype (casual, core, whale) — not just the average |
| Reward density | rewards per session ≥ 1 visible progress event; ≥ 1 "big" moment per 3–5 sessions | Sparse density reads as "nothing happens" |
| Content runway | `runway_days = content_units ÷ p90_units_per_day` | When runway < release cadence, the best players hit the wall |
| Power creep budget | new top-tier power ≤ +5–10 % over previous top tier per season | Larger jumps invalidate investment and anger payers |

## Progression stack audit checklist

- [ ] One spine answers "where am I?" in a single glance from the home screen.
- [ ] At most two power axes the player must manage before D7; every other layer reuses existing currencies.
- [ ] Every track has a target time-to-complete per archetype, checked by simulation (`economy_sim.py`, `progression_calc.py`).
- [ ] At least one visible progress event per session for a player who loses every level that session.
- [ ] Every paid random source has a deterministic alternative (exchange, fusion, crafting, shards).
- [ ] Resets (seasons, prestige, albums) state what persists before the player commits.
- [ ] No consecutive-only attendance mechanics without a catch-up or protection.
- [ ] Power-granting progression is matchmaking-aware in any PvP mode.
- [ ] Telemetry: `level_up`, `track_progress`, `unlock`, `reward_claim` events exist in the taxonomy (`player-analytics`).

## Related skills

- `progression-difficulty` — curve maths, difficulty models, DDA.
- `economy-design` — sources, sinks, currency architecture, simulation.
- `monetization` — pass products, offers, ethics.
- `liveops` — season calendars and event cadence.
- `player-psychology` — motivation, loss aversion, habit.
