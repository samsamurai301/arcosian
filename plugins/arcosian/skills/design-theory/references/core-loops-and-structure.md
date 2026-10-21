# Core Loops and Game Structure

How games are built out of nested, repeating cycles (loops) and one-time content (arcs), and how those cycles are paced across seconds, sessions, days and seasons. This file gives definitions that match the shared ontology (`contract.json` → `loops[]` with `type` and `period`), procedures for designing a loop stack from scratch, session design rules for phones, pacing tools (interest curves, tension–release, kishōtenketsu, teach–test–twist–reward), the line between engagement loops and compulsion loops, and nested loop diagrams for six mobile archetypes with tuning notes and failure modes. Use it when drafting a design contract, deconstructing a game, or diagnosing retention problems that trace back to structure rather than content.

## Contents

1. Vocabulary and the loop-as-graph model
2. The core loop: definition, tests and templates
3. Meta loops: what they must give back to the core
4. Social loops
5. Monetization and live-ops loops (pointers)
6. Loops vs arcs and content burn
7. The time-scale ladder
8. Engagement loops vs compulsion loops
9. Session design for phones
10. Interest curves
11. Pacing and tension–release
12. Kishōtenketsu and teach–test–twist–reward
13. "30 seconds of fun" and the micro-loop test
14. Nested loop diagrams: six mobile archetypes
15. Loop health telemetry
16. Procedure: designing a loop stack from scratch
17. Volatile facts (as of Oct 2026 — verify before relying)

---

## 1. Vocabulary and the loop-as-graph model

| Term | Definition used in this plugin | Ontology field |
|---|---|---|
| Verb | An atomic player input with meaning (swap, aim, merge, deploy) | `contract.verbs[]` |
| Mechanic | Rules + parameters that turn verbs into state changes | `contract.mechanics[]` |
| Loop | A repeating cycle of steps where the output of the last step feeds the first | `contract.loops[]` |
| Loop type | `core`, `meta`, `social`, `monetization`, `liveops` | `loops[].type` |
| Loop period | Natural cycle time: `seconds`, `minutes`, `session`, `daily`, `weekly`, `season` | `loops[].period` |
| Step | One node of a loop: an action and the reward/state change it yields | `loops[].steps[]` {`id`, `action`, `reward`, `next`} |
| Arc | Content consumed once (story beat, handcrafted level, one-off event) | `content.*`, `liveops.events` |
| Gate | A condition that blocks a step until satisfied (level, time, currency, item) | economy `nodes[].kind = gate` |
| Anchor | The step where a slower loop feeds a faster one (meta → core) | (documented in step `reward`/`next`) |

A loop is a directed cycle in a graph. A game is a set of loops linked at anchors: the core loop produces resources consumed by the meta loop, and the meta loop returns power, variety, goals or meaning to the core loop. If any loop has no link back, it is decoration.

Minimal loop object (contract format):

```json
{
  "id": "L_core_match",
  "type": "core",
  "period": "seconds",
  "steps": [
    {"id": "s1", "action": "Swap two adjacent tiles", "reward": "Match clears, cascade chance", "next": "s2"},
    {"id": "s2", "action": "Read new board state", "reward": "Spot specials and goal progress", "next": "s3"},
    {"id": "s3", "action": "Plan next swap under move budget", "reward": "Goal meter advances", "next": "s1"}
  ]
}
```

---

## 2. The core loop

**Definition.** The core loop is the smallest cycle of play that the player repeats most often and that carries the game's main aesthetic. Everything else exists to give that cycle context, variety and stakes.

**Three-beat template.** Most mobile core loops can be written as **act → get feedback/reward → invest**:
- *Act*: a verb with skill or choice in it.
- *Reward*: discernable, immediate result (points, resources, spectacle, information).
- *Invest*: the reward changes what the next *act* can be (new options, stronger state, a goal closer).

**The one-sentence test.** Write: "The player [verb] to [immediate goal], which earns [reward], which lets them [next, better verb]." If you need "and" more than once, you probably have two loops tangled together.

**Core loop quality tests.**

| Test | Pass condition | How to check |
|---|---|---|
| Toy test | The verb is pleasant with no goals attached | Greybox the verb alone; do testers keep fiddling for > 60 s? |
| Repetition test | Still engaging on the 50th repetition | Watch a 10-minute session; count signs of boredom (looking away, fast-tapping through) |
| Variation test | Each repetition differs meaningfully (board state, enemy mix, choice set) | Count distinct situations per 10 repetitions |
| Decision/skill test | Better play produces better results | Expert bot vs random bot win rate gap (see `decisions-and-depth.md`) |
| Feedback test | Player can say what happened and why within 1 s | Usability test think-aloud |
| Stakes test | Something is at risk or to be gained each cycle | List what changes on success vs failure |
| Mobile test | One cycle completes in ≤ 30–60 s and survives interruption | Timer + forced-pause test |

**Common core-loop failures.**
- *No invest step*: rewards accumulate with nothing to spend them on → "why am I collecting this?"
- *Invest without act*: menus and upgrades dominate the session; the verb is a formality (common in weak idle hybrids).
- *Reward detached from act*: rewards arrive on timers regardless of play quality → competence need unmet.
- *Single situation*: the same board/enemy every time → mastery horizon of minutes.

---

## 3. Meta loops: what they must give back

A meta loop runs on a slower clock (session, daily, weekly) and consumes outputs of the core loop. It must return at least one of four things to the core:

| Return type | What it does to the core | Mobile examples | Failure mode |
|---|---|---|---|
| **Power** | Makes the core easier or opens new tactics | Gear upgrades in roguelites, troop levels in strategy games | Power creep trivialises core skill; pay-to-win perception |
| **Variety** | Changes what the core asks of the player | New boosters, new heroes, new board elements | Variety without depth → novelty decays quickly |
| **Goals** | Gives the core a reason beyond the moment | Decorating a room, completing a collection | Goals feel arbitrary if not tied to fantasy |
| **Meaning** | Gives fiction, identity or social stakes | Story chapters, guild rank, base appearance | Story that interrupts sessions; meaning that costs time |

**Anchor design rule.** For each meta loop, name the anchor step: "Stars from levels (core) are spent on renovation tasks (meta), which unlock the next story beat and new level area (meaning + goals)." If you cannot name it, the meta loop is disconnected.

**Meta loop types (non-exhaustive):** progression track (levels, chapters), collection (cards, heroes, stickers), customization (rooms, avatars, bases), crafting/converter chains, narrative, mastery tracks (ranks, achievements), prestige/reset loops (idle games). Pick 1–2 at launch; each one adds UI, economy and live-ops cost.

---

## 4. Social loops

| Social loop | Mechanism | Benefit | Risk |
|---|---|---|---|
| Cooperative goal | Team contributes to a shared target (team chest, guild boss) | Relatedness, accountability → retention | Free-rider resentment; guilt pressure |
| Reciprocity | Gift/request lives, donate troops | Daily reasons to return; warm social ties | Spam; feels like obligation |
| Competitive | Leaderboards, leagues, PvP ladders | Status, mastery signals | Demotivates the bottom half; toxicity |
| Expressive | Visit/like others' bases or rooms | Expression is witnessed | Low engagement if nobody visits |
| Asynchronous rivalry | Raid others' bases, beat friends' scores | Drama without scheduling | Revenge spirals; churn of victims |
| Viral/referral | Invite rewards, share cards | Lower acquisition cost | Spammy; platform policy limits |

**Design rule.** Every social loop needs a solo fallback: a player with zero friends must still be able to progress, or you will churn your largest segment. Use matched "bot-like" teams or open guild matchmaking for players without friends in the game.

---

## 5. Monetization and live-ops loops (pointers)

- **Monetization loops** attach offers to points of friction or desire (out of moves, new hero, event pass). Design them *after* the core and meta loops are fun without spending; see `monetization` and the ethics rules in `legal-ethics`.
- **Live-ops loops** run on calendars (events, seasons, passes) and supply arcs and variety. Their cadence must match content production capacity; see `liveops` and `production`.
- Rule: a monetization or live-ops loop that disrupts the core loop's flow (popups mid-level, mandatory ads during play) costs more in retention than it earns in most designs; test it with A/B (`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ab_test.py size --baseline 0.30 --mde 0.02`).

---

## 6. Loops vs arcs and content burn

Following Dan Cook's distinction ("Loops and Arcs", 2012): loops are repeatable systems players keep mastering; arcs are consumed once.

| Property | Loop-heavy design | Arc-heavy design |
|---|---|---|
| Cost per hour of play | Low after the system is built | High and linear with content |
| Novelty | Must come from emergence, opponents, randomness | Comes from new content |
| Live-ops need | Balance patches, new system elements | Steady content pipeline |
| Examples | PvP card battlers, roguelites, sandbox builders | Story-driven puzzle sagas, narrative games |
| Main risk | Shallow system → boredom | Content runs out → churn spikes after each update |

**Content burn calculation (arcs).**

```
weekly_arc_minutes_needed = engaged_weekly_minutes × arc_share
units_needed_per_week     = weekly_arc_minutes_needed / minutes_per_unit
```

Worked example: engaged players play 25 sessions/week × 4 min = 100 min/week; 70% of that is spent on handmade levels (arc share); a level takes ~2.5 min including retries → 100 × 0.7 / 2.5 = **28 levels per week** to keep the engaged cohort from running dry. If the team can ship 15 per week, extend levels (more attempts, harder levels), add loop-based modes (events, daily challenges, PvP), or gate progress — and accept the trade-offs of each. Procedural generation (`procedural-generation`) and solver-validated level pipelines (`level-design`) change this equation.

---

## 7. The time-scale ladder

Design a loop for each relevant period. Not every game needs every rung.

| Period | Typical loop | Player question it answers | Mobile example |
|---|---|---|---|
| Seconds | Core interaction | "What do I do right now?" | Swap, aim, merge, dodge |
| Minutes | Level, match, run segment | "Can I win this one?" | 1 level / 1 match / 1 wave |
| Session | Progress chunk + spend | "What did I achieve today?" | Clear 3–5 levels, upgrade, story beat |
| Daily | Dailies, energy, login, streak | "Why come back tomorrow?" | Daily challenge, daily quest set |
| Weekly | Events, leagues, team goals | "What's this week about?" | Team tournament, weekly league |
| Season | Pass, chapter, ladder reset | "What's the long goal?" | New area, season pass, meta shift |

**Rule of nesting:** each slower loop should complete roughly 3–10 cycles of the faster loop beneath it. A session that contains one level is fragile (one bad level = bad session); a session that requires 40 levels to achieve anything feels like a grind.

---

## 8. Engagement loops vs compulsion loops

Both are loops that bring players back. The distinction is about **whose interests the loop serves and whether the player would endorse it on reflection.**

| Dimension | Engagement loop | Compulsion loop |
|---|---|---|
| Core driver | Intrinsic: mastery, curiosity, expression, connection | Extrinsic: unpredictable payouts, loss avoidance, social obligation |
| Reward predictability | Mostly understandable; randomness adds spice | Variable-ratio payouts are the main hook |
| Player state after session | Satisfied, "good tired" | Restless, "one more spin", regret |
| Stopping | Natural stopping points exist | Stopping points removed or penalised |
| Spending | Optional; value is clear | Prompted at moments of frustration or near-miss |
| Reflective endorsement | "I'm glad I played" | "I wish I hadn't spent that time/money" |

**Practical test (run it on every loop).**
1. Remove the random reward from the loop. Is the loop still worth doing? If not, the loop is a slot machine with a theme.
2. Add a clear "stop here" point. Does retention modelling say revenue collapses? If yes, you depend on players who cannot stop.
3. Would you be comfortable explaining the loop's design intent to a regulator, a journalist and the player's parent? (See `legal-ethics`.)

Variable rewards are not banned by this doctrine — they are a legitimate source of surprise — but they must be transparent (odds disclosed where required), bounded (pity systems, caps) and never the only reason the loop exists. Details and ethics in `fun-and-motivation-design.md`.

---

## 9. Session design for phones

### 9.1 Session anatomy

```
[entry ≤ 5 s] → [warm-up win ≤ 30 s] → [core block] → [peak moment] → [exit hook] → (gone)
```

| Phase | Purpose | Design rules |
|---|---|---|
| Entry | Return to play fast | Cold start fast (perf budget `cold_start_sec`); resume last context; one tap to play; at most one popup on entry, never a chain |
| Warm-up win | Re-establish competence | An easy win or collectable within the first 30 s (offline earnings, a quick level, a daily reward with a choice) |
| Core block | Main value | 3–10 core cycles; difficulty can rise here |
| Peak | Emotional high point | Boss, hard level, story beat, big unlock; put the peak near the end (peak–end rule from Kahneman et al.) |
| Exit hook | Reason to return | Something started but not finished (timer, chest, story question, event progress) shown clearly at exit |

### 9.2 Session length

The doctrine targets 1–5 minute sessions (`contract.meta.session_length_target_sec`), with several sessions per day. Design for the *distribution*, not the average: some players will play 60 seconds at a bus stop, others 40 minutes on a sofa. Rules:
- The **minimum meaningful session** (start → something achieved → stop) should be ≤ 60–90 s.
- A **natural stopping point** should appear every 2–5 minutes (level end, run end, task done).
- **Long-session support** should exist (chained levels, extended runs) without requiring it.

### 9.3 Session limiters: options and trade-offs

| Limiter | How it works | Pros | Cons | Use when |
|---|---|---|---|---|
| Lives/energy | Failure or play costs a regenerating resource | Paces content consumption, creates return appointments, monetizable | Feels punitive; blocks motivated players; ethically sensitive when aggressive | Arc-heavy content you cannot produce fast enough |
| Timers on rewards | Rewards unlock after real time | Appointment mechanics; anticipation | Waiting is not play; easy to abuse | Meta rewards, not core play |
| Daily cap on progress | Limited daily attempts or quests | Clear stopping point; fairness | Frustrates binge players | Competitive or daily-puzzle designs |
| Natural content cap | Daily puzzle, weekly event | Scarcity creates ritual (Wordle-style) | Thin daily playtime | Ritual/social share games |
| No limiter | Unlimited play | Respectful, binge-friendly | Content burn; less return structure | Loop-heavy designs (PvP, roguelite, emergent puzzles) |

Example lives tuning to analyse (not a recommendation): 5 lives, one regenerating every ~30 minutes, a loss costs a life. A player who fails 5 times in a row is locked out for up to 2.5 hours. Ask: what fraction of players hit zero lives in session 1? (If more than a small minority, the early curve is too hard or the limiter too tight.)

### 9.4 Interruption resilience checklist
- Every action persists immediately; force-kill and reopen restores the exact state.
- Real-time PvP: define reconnection windows and AFK handling; prefer asynchronous or very short matches on mobile.
- Pause anywhere in single-player; no penalty for backgrounding.
- Audio ducks and resumes correctly; the game respects silent mode.

---

## 10. Interest curves

Jesse Schell (*The Art of Game Design*) uses interest curves — plots of audience interest over time — to reason about pacing. A typical good curve: a **hook** spike at the start, a dip as context is set, a series of **rising peaks and valleys**, a **climax** near the end, and a short **resolution**. The same shape works fractally: per level, per session, per FTUE, per season.

**Procedure: plot and fix an interest curve.**
1. Pick a unit (first session, a level, a season).
2. List beats in order with timestamps (or level numbers).
3. Score expected interest 1–10 per beat (team estimate), then replace estimates with telemetry proxies (quit rate per beat, time spent, retries) once data exists.
4. Look for: flat stretches > 2 minutes, a weak hook (interest < 6 in the first 30 s), no rest after peaks, a climax that is not near the end.
5. Fix by reordering beats, cutting flat ones, inserting a novelty or a breather.

```
interest
10 |   *                                  *
 8 | *   *          *        *         *     
 6 |       *     *     *   *   *    *         *
 4 |         * *         *       **
 2 |
   +--------------------------------------------- time
     hook  setup    rising peaks/valleys   climax  resolution
```

**Mobile FTUE curve rules.** Hook in the first 10–30 s (play, not cutscene); first real win and the "aha" moment as early as possible (see volatile facts on time-to-fun); first meta reveal (what you are building toward) within the first session; first exit hook before the player is likely to leave.

---

## 11. Pacing and tension–release

Pacing is the rhythm of intensity. Constant high intensity numbs players; constant low intensity bores them. Alternate.

**Pacing levers.**

| Lever | Raises intensity | Lowers intensity |
|---|---|---|
| Difficulty | Fewer moves, stronger enemies | Breather level, generous limits |
| Density | More enemies/obstacles per second | Empty space, exploration |
| Time pressure | Timers, chasing threats | Turn-based, no clock |
| Stakes | Streaks at risk, rare reward at stake | Free retries, no loss |
| Novelty | New mechanic, new enemy | Familiar content |
| Audio/visual | Faster tempo, darker palette, shake | Calm music, soft colours |
| Information | Hidden threats | Full information |

**Difficulty pattern catalogue (levels).**

| Pattern | Shape | Use | Generate |
|---|---|---|---|
| Linear ramp | Steady rise | Short games, tutorials | `difficulty_curve.py generate --pattern linear` |
| Sawtooth | Rise then drop, repeating | Sagas: hard spike then breathers | `--pattern sawtooth --period 5` |
| Stepped | Plateaus with jumps at new mechanics | Mechanic introductions | `--pattern stepped` |
| Hard-every-K | Baseline with a hard level every K levels | Monetization-sensitive sagas (use ethically) | `--hard-every 10` |

Example: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/difficulty_curve.py generate --levels 40 --pattern sawtooth --base 0.90 --floor 0.40 --period 6 --hard-every 12 --json` produces target win rates per level to store in level specs (`difficulty_target.win_rate`).

**Intensity director.** For real-time action, a director can track a player-stress estimate and cycle through phases — build up, sustain a peak, fade, relax — before building again. Valve's Michael Booth described an approach of this kind for Left 4 Dead's AI Director in "The AI Systems of Left 4 Dead" (2009; the slides are hosted by Valve at https://steamcdn-a.akamaihd.net/apps/valve/2009/ai_systems_of_l4d_mike_booth.pdf). The slides describe estimating each Survivor's "emotional intensity", tracking the maximum across the team, removing major threats when it peaks, and creating "peaks and valleys" of intensity. On mobile, simple versions work well in survivor-likes and runners: if no damage has been taken for N seconds, raise spawn density; after a near-death, open a short relief window.

---

## 12. Kishōtenketsu and teach–test–twist–reward

**Kishōtenketsu** is a four-part structure from Chinese and Japanese poetry and storytelling: **ki** (introduction), **shō** (development), **ten** (twist — an unexpected turn), **ketsu** (conclusion that reconciles). Nintendo designer Koichi Hayashida described applying a similar structure to platformer levels (in a 2012 interview about Super Mario 3D Land; see Game Developer's interview, [The secret to Mario level design](https://www.gamedeveloper.com/design/the-secret-to-i-mario-i-level-design), and Nintendo Life's [April 2012 report](https://www.nintendolife.com/news/2012/04/super_mario_3d_land_director_shares_level_design_inspirations); the explicit "kishōtenketsu" label comes from secondary summaries of that interview and later video essays, so check the interview text before quoting him on the term): introduce a gimmick safely, develop it with more demanding uses, twist it in a surprising way, then conclude — then move on before it gets stale.

The plugin's level-spec schema encodes a game-design version of this as `teach | test | twist | reward` (`${CLAUDE_PLUGIN_ROOT}/scripts/schemas/level-spec.schema.json`, field `teach`).

| Beat | Purpose | Design rules | Example: "ice blocker" in a match-3 |
|---|---|---|---|
| Teach | Introduce one new element safely | No failure pressure; the new element is the obvious solution | Level with 6 ice tiles, generous moves, ice next to easy matches |
| Test | Require the player to use it under mild pressure | Combine with known elements; normal limits | Ice behind other blockers; moves tighter |
| Twist | Change the context so the element is seen anew | Combine with another mechanic or invert its role | Ice that spreads each turn unless cleared |
| Reward | Let the player feel powerful with it | Generous, spectacular, short | Board full of ice and a pre-placed colour bomb — mass shatter |

**Sequencing rule.** Introduce at most one new element per 3–5 levels in the early game; never introduce a new element in a level that is also a difficulty spike. Track each element's first appearance in the content plan.

---

## 13. "30 seconds of fun" and the micro-loop test

"30 seconds of fun" comes from Bungie's Halo team and is credited to designer Jaime Griesemer, who in a 2011 Engadget interview called it "probably the most famous thing I ever said" ([Half-Minute Halo: An Interview with Jaime Griesemer](https://www.engadget.com/2011-07-14-half-minute-halo-an-interview-with-jaime-griesemer.html); the line also appears in Halo 2 making-of material). It means that the game's combat was a short encounter loop — roughly half a minute of reading the situation, choosing an approach, executing and recovering — repeated in endlessly varied contexts. Griesemer has said the phrase is often misread as "any 30 seconds of fun repeated makes a game"; the point he stresses is varying that moment across environments, weapons, vehicles and enemy combinations. The lesson generalises: if the shortest complete cycle of play is enjoyable and varies each time, the game can be built outward from it; if it is not, no amount of meta will fix it.

**Micro-loop test (mobile version).**
1. Define the micro-loop: the shortest cycle with a beginning, a decision or skill moment, and a payoff. Target 10–30 s for most mobile genres.
2. Build it in greybox with placeholder art (see `prototyping-and-iteration.md`).
3. Have 5+ target players play it 20 times in a row with no meta, no rewards, no progression.
4. Pass if: most voluntarily continue past the requested 20; they describe different things happening in different cycles; they can name what they did better or worse.
5. Fail if: interest collapses before cycle 10, or players cannot tell good play from bad. Rework the verb, the situation generator or the feedback before adding anything else.

---

## 14. Nested loop diagrams: six mobile archetypes

Each diagram reads innermost (fastest) to outermost (slowest). Arrows show what each loop feeds into the next. Tuning notes name the parameters that most often break the structure. Treat these as structural archetypes, not prescriptions; comparables are named only to orient the reader.

### 14.1 Match-3 with decorate/story meta (Royal Match / Homescapes-style)

```
SECONDS   swap → match → cascade → board update ──┐
            ↑                                     │
            └─────────── read board ←─────────────┘
MINUTES   level start → use moves on goals → WIN: stars+coins | LOSE: retry (life) / booster / extra moves offer
SESSION   play 3–5 levels → spend stars on renovation tasks → story beat / room changes → new area preview
DAILY     daily reward, lives regen, streak events, gift lives to team
WEEKLY    team tournament, leagues, collection events
SEASON    new chapter areas, season pass, themed live-ops
```
- **Anchor**: stars (core output) → renovation task (meta goal) → narrative and visible transformation (meaning).
- **Tuning watch**: attempts p50 per level; hard-level frequency; star cost per task (sets levels per story beat); lives regen.
- **Failure mode**: content burn outruns production; difficulty spikes used as monetization walls feel unfair (`progression-difficulty`, `monetization`).

### 14.2 Hybrid-casual arcade (runner / crowd-gate / stacker with upgrades)

```
SECONDS   steer → hit gates/collect/avoid → instant number/crowd feedback
MINUTES   30–60 s level → end-of-level multiplier → coins (optional rewarded x-multiplier)
SESSION   spend coins on stat upgrades (income, start size, speed) → next levels → skin unlock
DAILY     daily reward, offline earnings, spin/wheel
WEEKLY    skin collections, light events
```
- **Anchor**: coins → permanent stat upgrades that make the next level visibly better.
- **Tuning watch**: upgrade cost curve vs coin income (`progression_calc.py curve --formula exp --levels 50 --base 100 --growth 1.15`); level length; interstitial frequency (`monetization.ads.interstitial.min_interval_sec`).
- **Failure mode**: shallow core with a mastery horizon of a few sessions; upgrades become the only progression and players churn when cost curves outpace income.

### 14.3 Idle / incremental tycoon

```
SECONDS   tap/collect → number goes up
MINUTES   buy generator/upgrade → income rate rises → next unlock threshold
SESSION   return → collect offline earnings → reinvest → hit cost wall → leave with timers running
MULTI-DAY prestige/reset → permanent multiplier → faster replay of earlier stages
WEEKLY    limited events with separate economies
```
- **Anchor**: income → generators (dynamic engine) → wall → prestige (stopping mechanism + meta reset).
- **Tuning watch**: generator cost growth vs output growth (cost ratio per purchase often in the ~1.07–1.15 range in the genre; derive yours by simulation), prestige formula, offline earnings cap.
- **Failure mode**: walls arrive before the player understands prestige; numbers inflate without new decisions (`economy-design`).

### 14.4 Roguelite action (Archero / survivor-like)

```
SECONDS   move/dodge (one thumb) → auto-attack → enemies die → XP gems
MINUTES   level-up → choose 1 of 3 skills → wave/room → boss → run ends (win or death)
SESSION   run rewards (gear, currency) → upgrade gear/talents → try next chapter
DAILY     energy per run, daily quests, idle "patrol" rewards
WEEKLY    events, challenge modes
SEASON    pass, new heroes/weapons
```
- **Anchor**: run rewards → permanent power (meta) → deeper chapter progress (goal).
- **Tuning watch**: run length (often 5–15 min; check against session target), skill-choice synergy density, meta power vs skill contribution to clear rate.
- **Failure mode**: meta power dominates skill (runs feel predetermined); energy blocks motivated players; skill choices with a dominant pick (`decisions-and-depth.md`).

### 14.5 PvP card / arena battler (Clash Royale / Marvel Snap-style)

```
SECONDS   resource ticks (elixir/energy) → play card/unit → counters and interactions
MINUTES   ~3 min match (or ~6 turns) → win: rank points + rewards | lose: rank points lost
SESSION   several matches → tweak deck → upgrade/collect cards
DAILY     quests, free rewards, daily deals
WEEKLY    clan wars / tournaments / special modes
SEASON    ladder reset, season pass, new cards → meta shift
```
- **Anchor**: matches → collection growth → new deck options → new decisions in matches.
- **Tuning watch**: matchmaking quality (rating spread), card power vs rarity (pay-to-win perception), win-rate band for each archetype deck, match length.
- **Failure mode**: stale meta (one dominant deck), collection gaps that feel unwinnable, toxic losses; balance with `balance-pass` workflow and dominant-strategy detection.

### 14.6 4X / base builder (Clash of Clans / Whiteout Survival-style)

```
SECONDS   tap to collect, deploy troops in raids
MINUTES   queue builds/research/training → raid or gather → loot
SESSION   spend resources on queues → help alliance → attack/defend → set long timers
DAILY     alliance tasks, daily events, resource caps refill
WEEKLY    alliance wars, server events, leaderboards
SEASON    server seasons / migrations, new heroes, power resets for events
```
- **Anchor**: resources → buildings/research (power) → bigger raids and alliance contribution (status, relatedness).
- **Tuning watch**: timer lengths by level (long timers create appointments and monetization pressure), loot rates, protection shields, alliance size.
- **Failure mode**: whales dominate free players in shared spaces (ecosystem collapse per Bartle's ecosystem view); timer walls replace play (`monetization`, `liveops`).

---

## 15. Loop health telemetry

Instrument every loop with at least one event at its start and end (`event_taxonomy.py generate --contract .gamestudio/contract.json --out .gamestudio/analytics/taxonomy.json`).

| Loop | Health signal | Problem signal |
|---|---|---|
| Core | Retries per failure, cycle time stable, voluntary continuation | Rapid quit after failure, cycle time shrinking (button-mashing) |
| Meta | Share of earned currency spent within N sessions | Hoarding (nothing worth buying) or zero balance (too stingy) |
| Social | Share of players in a team; gifts sent per DAU | Team churn after a loss; requests ignored |
| Session | Sessions/day stable, session length within target band | One long session then churn (binge-and-burn) |
| Daily | Day-over-day return; streak continuation | Streak breaks followed by churn (punitive streaks) |
| Season | Pass progression distribution | Most players far behind the expected curve at mid-season |

Diagnose with `player-analytics`; fit retention with `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/retention_ltv.py fit --points "1:0.40,7:0.15,30:0.06"`.

---

## 16. Procedure: designing a loop stack from scratch

1. **Fantasy and aesthetics first.** Write the player fantasy and top three aesthetics (`foundational-frameworks.md`, MDA).
2. **Pick the verb.** One primary verb that embodies the fantasy and works with one thumb (`mobile-ux`).
3. **Write the core loop** with the three-beat template and the one-sentence test. Store it as a `core` loop with `period: seconds` or `minutes`.
4. **Prototype the micro-loop** (section 13) before designing anything else. Kill or pivot if it fails twice.
5. **Choose one meta loop** that returns power, variety, goals or meaning (section 3). Name the anchor.
6. **Set the session shape**: minimum meaningful session, stopping points, exit hook (section 9).
7. **Add daily and weekly loops** only if you have content or systems to feed them (section 6 burn maths).
8. **Add social loops** with a solo fallback (section 4).
9. **Add monetization and live-ops loops** last; run the compulsion test (section 8) on each.
10. **Draw the full nested diagram** (section 14 style) and check each slower loop contains 3–10 cycles of the faster one.
11. **Instrument** every loop (section 15) and write kill criteria for the structure (`prototyping-and-iteration.md`).
12. **Review** with the diagnostic checklist (`design-diagnostic-checklist.md`, loop section) and the `design-review` workflow.

---

## 17. Volatile facts (as of Oct 2026 — verify before relying)

Market benchmarks shift every year and differ by genre, platform and source. Use them as screening heuristics, not targets you must hit.

| Fact | Value reported | Source |
|---|---|---|
| Median mobile game retention (GameAnalytics data, via secondary write-ups) | About 22% D1, just under 4% D7, about 0.7–0.8% D30; top 1% about 64–68% D1 | [Segwise](https://segwise.ai/blog/mobile-gaming-app-user-retention-strategies); [Playio](https://blog.playio.co/d1-d7-d30-retention-benchmarks-2026) |
| Practitioner "viability screen" for marketed titles | 25–30% D1, 10–15% D7, 3–6% D30 (a working heuristic, not a published median) | [Playio](https://blog.playio.co/d1-d7-d30-retention-benchmarks-2026); [Galaxy4Games](https://galaxy4games.com/en/knowledgebase/blog/mobile-game-retention-benchmarks-2026-d1-d7-d30-data-for-publishers) |
| D7/D1 ratio diagnostic | Below ~0.30 suggests a first-session/FTUE problem; ~0.30–0.44 suggests weak engagement on days 2–5 (practitioner consensus) | [GameDev.net](https://gamedev.net/blogs/entry/2298160-the-d7d1-retention-ratio-for-mobile-games-a-complete-guide) |
| Time to fun | If the "aha" moment takes longer than about 90 seconds, a significant share of users reportedly never return | [Playio](https://blog.playio.co/mobile-game-onboarding-retention) |
| Market context | 2025 mobile game IAP about $82B (+1%); growth came mainly from retaining and monetizing existing players via live-ops | [Sensor Tower](https://sensortower.com/press/press-release-sensor-tower-state-of-gaming-gaming-drove-52-billion-downloads-82b-iap-revenue-on-mobile-and-12b-premium-revenue-on-steam) |

Implication for structure: before launch you can only proxy these numbers (bot time-to-first-reward, first-session length, FTUE completion in playtests); after soft launch they become acceptance thresholds in `contract.analytics.kpi_targets`.
