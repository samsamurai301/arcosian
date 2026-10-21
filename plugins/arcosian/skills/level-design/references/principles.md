# Level Design Principles

The genre-independent craft of level design, written as rules you can apply and check. A level is an argument about a mechanic: it sets up a situation, lets the player discover something about the rules, then asks them to prove it. This file covers the teaching rhythm (teach, test, twist, reward and kishōtenketsu), guidance (signposting, affordances, landmarks), structure (gating, pacing, risk/reward routes), the experiential target (flow), the constraints a phone imposes (mobile readability), and the numbers that keep levels consistent (level metrics). Genre files apply these: `puzzle-level-design.md`, `casual-level-production.md`, `action-level-design.md`. The data and tooling side is in `level-pipeline.md`.

## Contents

1. The level brief: one idea per level
2. Teach, test, twist, reward
3. Kishōtenketsu as a level structure
4. Signposting and guidance
5. Affordances and signifiers
6. Gating
7. Pacing and intensity
8. Landmarks and wayfinding
9. Risk/reward routes
10. Flow in levels
11. Mobile readability
12. Level metrics
13. One-page principles review

---

## 1. The level brief: one idea per level

Before laying a single tile, write a five-line brief. If you cannot fill it in, the level has no reason to exist.

```
level_id:        w2_l014
idea:            "Ice must be cleared from the side; you cannot swap into it."   (one sentence)
role:            teach | test | twist | reward          (level-spec `teach` field)
feeling:         "relief after the w2_l013 spike; quick, generous"   (target aesthetic)
target metrics:  first-try win rate 0.85, attempts_p50 1, length 60–120 s
```

Rules:
- **One new idea per level, at most.** A level may *combine* known ideas (twist) but may introduce only one unknown element. The level-spec `mechanic_refs` makes this checkable: the first level where a mechanic id appears should contain no other first appearance (`scripts/level_audit.py` flags violations).
- **The idea is a sentence about the rules, not about the layout.** "A spiral of boxes" is a layout; "boxes protect the tiles behind them until hit twice" is an idea.
- **Every element must serve the idea or the feeling.** Delete anything else. Clutter is the most common reason a level reads badly on a phone.
- **Write the intended solution or path in `notes`.** Reviewers and the critic compare play traces against it; a level whose intended path nobody can state cannot be tuned.

## 2. Teach, test, twist, reward

A four-role rhythm for introducing anything new: a mechanic, an enemy, an obstacle, a goal type. It is the default sequencing model in the ontology (`level-spec.teach`). It has no single canonical author; it is an industry pattern that formalises what well-paced Nintendo-style and puzzle games do.

| Role | Purpose | Failure possible? | Danger / pressure | Target first-try win rate (heuristic) | Typical length vs average |
|---|---|---|---|---|---|
| **teach** | Show the new element in isolation; the player discovers its rule by doing | Ideally no; if yes, failure cost is trivial | None or minimal; no timer pressure | 0.95–1.00 | 0.5–0.8× |
| **test** | Check the player understood: use the element in a slightly demanding context, alone or with well-known elements | Yes | Moderate | 0.6–0.85 (tier-dependent) | 1.0× |
| **twist** | Combine the element with another, or subvert its first reading (use it backwards, in a new context) | Yes | Moderate to high | 0.4–0.7 | 1.0–1.3× |
| **reward** | Breather: generous, showy, lets the player feel the mastery they just earned | Rarely | Low | 0.9–1.0 | 0.6–1.0× |

The win-rate ranges are starting heuristics for a broad casual audience; set the real numbers per game in the contract's `progression.difficulty` and recalibrate on telemetry (`level-pipeline.md` section 12).

### Rules for each role

**Teach**
- The first encounter must be **impossible to miss and very hard to fail**. Place the element on the critical path, in the centre of the screen, with nothing else competing.
- **Show, don't tell.** Prefer geometry that forces the discovery (a box in the only path; a single legal move that triggers the new behaviour) over text. If text is needed, it should be under 10 words and appear at the moment of use, not before the level.
- Let the player **see cause and effect within about one second** (the box cracks visibly on first hit; the ice shatters with a distinct sound).
- Do not combine teaching with a difficulty spike, a new goal type, or a time limit.

**Test**
- Same rule, slightly more demanding: more instances, less slack, or needing correct timing.
- Use only elements the player already knows well. A test that fails because of an *unrelated* unknown teaches the wrong lesson.
- Verify the test actually requires the new understanding: a solver or bot that ignores the element should do noticeably worse (`puzzle-level-design.md` section 8).

**Twist**
- Combine with one earlier element, or change the context so the obvious reading fails. Good twists reveal something that was always true of the rule but not yet needed.
- The twist should be explainable afterwards in one sentence ("ice also blocks gravity, so tiles above it don't fall").
- Twists are the most fragile levels: check for unintended shortcuts with a solver.

**Reward**
- Generous limits, many specials or power-ups, short. Often a showcase of the new element at scale.
- A reward level is not filler: it consolidates learning and resets tension before the next ramp.

### Cadence across a world

```
Level:   1     2     3     4     5     6     7     8     9     10
Role:    teach test  test  twist reward teach test  twist test  twist(hard)  -> reward
Element: A     A     A     A+B   A     C     C     C+A   C     A+B+C
```

- Introduce a new element roughly every 3–6 levels in early game, slowing to every 10–20 levels in a long live game (puzzle playbook convention; adjust to content budget).
- Never place a **teach** immediately after a hard spike unless the teach level doubles as the relief.
- Each element should get at least one test before it appears in a twist.
- With n distinct elements there are n(n−1)/2 pairwise combinations. That is the twist budget: 6 elements give 15 pairs, enough raw material for a long world, but only pairs that create a *new behaviour* are worth a level.

### Worked example: introducing "spring pads" in a portrait platformer

| Level | Role | Layout intent | Why |
|---|---|---|---|
| 3-1 | teach | Pit too wide to jump; a single spring pad in the run path before it; landing platform clearly visible above | The only way forward is to step on it; the result is visible within 0.5 s |
| 3-2 | test | Three springs over three pits with gentle timing; one spring offset so the player must aim | Proves they can use it intentionally |
| 3-3 | test | Spring leads to a coin arc; missing the arc is safe | Introduces aiming for reward without punishment |
| 3-4 | twist | Spring under a low ceiling: bouncing kills momentum, so the player must *avoid* it | The subversion: a known helper is now an obstacle |
| 3-5 | reward | Chain of 8 springs over a scenic gap with a coin shower | Mastery made visible |

## 3. Kishōtenketsu as a level structure

Kishōtenketsu is a four-part structure from classical Chinese and Japanese composition: **ki** (introduction), **shō** (development), **ten** (twist), **ketsu** (conclusion). It does not require conflict; the drama comes from the twist recontextualising what came before. Nintendo's Koichi Hayashida described applying it to stage design for *Super Mario 3D Land* (2011) in press interviews around its release: introduce a gimmick safely, develop it, twist it, then conclude, often within a single short stage.

**How it differs from teach-test-twist-reward:** TTTR usually spans several levels; kishōtenketsu usually fits inside one level, which makes it ideal for 60–180 second mobile levels.

| Beat | Share of level time (heuristic) | Design job | Example (moving platforms level, 120 s) |
|---|---|---|---|
| Ki — introduce | ~15–20% | Safe, isolated first contact | One slow platform over a short, safe drop |
| Shō — develop | ~30–35% | Same rule, more demand | Two platforms in sequence, a longer gap, a coin line |
| Ten — twist | ~30–35% | Recontextualise | Platforms now move vertically through a crusher; or the player rides one *through* enemies |
| Ketsu — conclude | ~15–20% | Brief victory lap or final exam, then exit | A long ride with a view of the goal flag |

Rules:
- **Retire the gimmick at the end of the level.** The next level gets a new one, or a combination. This is how a 60-level game avoids repetition with a small mechanic set.
- **The twist must be legible in hindsight.** Players should feel "of course", not "that was unfair".
- On mobile, keep ki very short (under about 15 seconds); players open the game for a quick session and the first seconds decide whether they stay.

## 4. Signposting and guidance

Signposting is everything that tells the player where to go and what to do without stopping play. The best guidance is invisible: players feel they chose the route.

### Guidance hierarchy (use the highest tier that works)

| Tier | Tool | Notes |
|---|---|---|
| 1 | **Geometry and composition**: the path is the open, wide, lit space; leading lines (rails, edges, roads, cable runs) point at the goal | Strongest and cheapest; costs no UI |
| 2 | **Light and contrast**: the goal is the brightest or most saturated region | Players move toward light in dark scenes and toward contrast generally |
| 3 | **Colour language**: one reserved colour for interactable or climbable surfaces | Consistency matters more than the hue; never reuse the reserved colour decoratively |
| 4 | **Motion**: animated objects pull the eye (a swaying flag, a fluttering bird, a pulsing gem) | Use sparingly; too much motion becomes noise |
| 5 | **Breadcrumbs**: coins, pickups, footprints along the intended path | Doubles as reward; in runners, coin trails show the safe lane |
| 6 | **Sound**: a positional cue from the goal | Weak on mobile: many players play muted |
| 7 | **Characters**: an NPC looking or running toward the goal | Good for narrative games |
| 8 | **UI markers**: arrows, waypoints, highlight pulses | Last resort and for accessibility; overuse trains players to stop reading the world |

### Rules
- **Readable in one screenshot.** On a phone the whole decision space of a moment should be visible: the goal or the next sub-goal, the hazard, the tool. If a reviewer cannot point to "where next" in a paused screenshot within 5 seconds, the guidance has failed.
- **Squint and greyscale tests.** Blur the screenshot (or squint): the path and hazards should still read. Desaturate it: nothing important should rely on hue alone.
- **Reserve a visual language and never break it.** Whatever colour, shape or texture marks "interactive", "breakable", "deadly" or "collectable" must mean that everywhere.
- **Signpost the exit at the start.** Show the goal early (camera pan, a visible landmark, a progress bar) so players can plan.
- **Idle hints.** If a player is idle or stuck for a set time (often 5–10 s in casual games; tune by telemetry), pulse the suggested move or path. Make the delay configurable and turn it off for advanced players.

## 5. Affordances and signifiers

Don Norman (*The Design of Everyday Things*, 1988; revised 2013) distinguishes the **affordance** (what an object lets you do) from the **signifier** (the perceivable cue that tells you so). Level designers mostly manage signifiers: the crack that says "breakable", the ledge lip that says "grab here", the shadow under a tile that says "draggable".

### The affordance contract
Once something looks interactive, **every** object that looks the same must behave the same. Breaking this contract once teaches players to distrust the whole world, and they start tapping everything.

| Contract violation | Symptom in telemetry or playtests | Fix |
|---|---|---|
| Decorative crates that look like breakable crates | Players waste attacks or moves on scenery | Make decorative props visually distinct (different material, no crack decal) |
| Some ledges grabbable, some identical ones not | Deaths at ledges; players stop exploring | Mark grabbable edges consistently (lip, colour strip) |
| A tile that looks swappable but is locked | Repeated failed swaps on the same cell | Overlay (chain, lock) that changes the silhouette, plus a reject animation |
| Hazards that look like floor | "Unfair" deaths, early quits | Hazard colour and motion; edge outlines |

### Mobile signifiers
- **Draggable**: drop shadow, slight lift on touch, idle wiggle on first appearance.
- **Tappable**: a pulse or glint every few seconds on first appearance only; then stop.
- **Blocked**: the item rejects with a shake and a short sound, never silently.
- **Touch feedback within one frame or two** on press, even if the action resolves later (`game-feel`).

### False affordances you may use deliberately
A puzzle may use a convincing but false affordance as a twist only if it is consistent with rules the player already knows ("the door looked like an exit but only opens from the other side"). In casual games, avoid deliberate false affordances: the audience reads them as bugs.

## 6. Gating

A gate controls when content becomes available. Choose the gate type by what you want the player to do before passing.

| Gate type | Mechanism | Makes the player... | Strengths | Risks | Mobile use |
|---|---|---|---|---|---|
| Hard lock (key, switch) | Physical lock in the level | Explore the level to find the key | Clear goal, enables backtracking | Backtracking is tedious on small screens | Short in-level loops only |
| Ability gate | Area needs a capability (double jump, dash) | Return later with a new tool | Metroidvania-style reward for growth | Long-term memory load | Show the unreachable area before the ability |
| Skill gate | A challenge the player must beat | Practise | Feels earned | Hard stop for low-skill players | Pair with optional assists or skip |
| Soft (difficulty) gate | Content is reachable but punishing | Choose when they are ready | Player autonomy | Players can wander into frustration | Signal difficulty clearly (skulls, stars) |
| Resource gate | Spend currency or items | Engage the economy | Ties levels to meta | Feels like a paywall if tight | Tune with `economy-design`; never gate the core path behind premium only |
| Star / score gate | Need N stars or points total | Replay earlier levels for better results | Adds replay depth | Grind if thresholds are high | Keep requirement ≤ about 70–80% of available stars so 3-starring everything is never mandatory |
| Time gate | Unlocks after real time | Return later | Pacing and habit | Feels arbitrary | Use for events and daily content, not the main path |
| Social gate | Need friends or a team | Invite or join | Virality | Excludes solo players | Always offer a solo alternative |

### Star-gate arithmetic
If a world has L levels with up to 3 stars each and a gate needs S stars, the required average is S / L per level. A gate of 0.75 × 3L means an average of 2.25 stars per level, which a casual player who mostly earns 2 stars cannot reach without replays. Check the gate against the bot's star distribution: the share of simulated players below the gate is the share forced to replay.

### Gate rules
- **Show the locked thing first.** The player should see what they are working toward.
- **One gate type per gate.** A door needing a key *and* 30 stars *and* level 20 confuses.
- **No dead ends.** Every gate needs a reachable way through without spending premium currency.

## 7. Pacing and intensity

Pacing is the arrangement of intensity over time. Good pacing alternates tension and release, with peaks generally rising toward the end.

### Intensity curves
Plot intensity (threat, demand, density or difficulty) per beat. Jesse Schell's *interest curve* (*The Art of Game Design*, 2008) captures the classic shape: a hook early, rising peaks and valleys, a climax near the end, a short resolution.

Valve's AI Director in *Left 4 Dead* (described by Michael Booth, "The AI Systems of Left 4 Dead", AIIDE 2009) paces dynamically: it estimates player intensity from damage taken and threats faced, builds up, sustains a peak briefly, then deliberately enforces a relax period before building again. The lesson for handmade levels: **relief is designed, not leftover**.

### Pacing rules of thumb (heuristics; tune per game)
- **Alternate demand.** After a peak, give a valley of at least 30–50% of the peak's duration.
- **Rising peaks, flat-ish valleys.** Each peak a little higher than the last; valleys do not drop below the previous valley.
- **Vary the demand type.** Alternate precision, speed, planning and observation so one skill does not fatigue.
- **Front-load the hook.** The first 10–20 seconds of a level contain the most interesting moment of the opening, not a corridor.
- **End on a high.** The last beat is a peak or a satisfying payoff, then a fast exit; on mobile, the results screen arrives within a second or two.
- **Across levels: sawtooth.** Ramp difficulty over roughly 5–10 levels, spike, then relieve (puzzle playbook convention). Generate targets with `${CLAUDE_PLUGIN_ROOT}/scripts/difficulty_curve.py generate --levels 60 --pattern sawtooth --base 0.9 --floor 0.45 --period 6 --hard-every 10`.

### Beat chart template

| Beat | t (s) | Intensity 1–5 | Demand type | Content | New info? |
|---|---|---|---|---|---|
| 1 | 0–10 | 2 | observation | Goal shown; easy first action | no |
| 2 | 10–35 | 3 | precision | Development of gimmick | no |
| 3 | 35–45 | 1 | none | Safe ledge, coin shower | no |
| 4 | 45–80 | 4 | planning | Twist | yes (combination) |
| 5 | 80–95 | 5 | speed | Final run to goal | no |
| 6 | 95–100 | 1 | none | Exit and reward | no |

## 8. Landmarks and wayfinding

Kevin Lynch (*The Image of the City*, 1960) found people build mental maps from five elements: **paths, edges, districts, nodes and landmarks**. Christopher Totten (*An Architectural Approach to Level Design*, 2014; 2nd ed. 2019) brought these, and related architectural ideas, into level design.

| Lynch element | Level design use | Mobile note |
|---|---|---|
| Path | The critical route; make it visually continuous | Prefer one dominant path per screen |
| Edge | Boundaries: walls, water, cliffs, board borders | Board edges in puzzles define the play space; keep them crisp |
| District | Areas with a shared identity (ice zone, factory) | Worlds on the saga map; tint and music per world |
| Node | Junctions and decision points | Place where the player has a breather to decide |
| Landmark | A unique, visible object used for orientation | A big goal object visible from the start |

**Weenies.** Walt Disney's term for a tall, visible attraction (the castle at the end of Main Street) that pulls visitors forward. Put a weenie at the end of every route: the boss tower, the flag, the glowing exit.

**Prospect and refuge.** Jay Appleton (*The Experience of Landscape*, 1975) argued people prefer places where they can see without being seen. In levels: give vantage points (prospect) before dangerous areas and safe pockets (refuge) to rest. In combat arenas these become cover positions with sightlines.

**Wayfinding rules**
- The goal, or the direction to it, is visible from the start or within the first screen of scrolling.
- Every junction offers at most 2–3 options, and the main path is visually dominant.
- Re-use a landmark across a level so players can triangulate.
- On a saga map, the next level and the next reward are always on screen when the map opens.

## 9. Risk/reward routes

Optional routes give players autonomy: they can choose the challenge they want. A route is worth taking when its expected value is positive *for some players*, and its risk is visible.

### Expected-value check
For an optional route with success probability p, reward R, and failure cost C (time lost, life lost, progress lost), versus the safe route with reward R₀:

```
EV(risky) = p·R − (1 − p)·C
Take it when EV(risky) > R₀
```

Design the route so that `EV(risky) > R₀` for skilled players (high p) and `EV(risky) < R₀` for unskilled players (low p). Then the choice sorts players by skill without anyone being forced into the hard route.

**Worked example (runner).** The high rail carries 30 coins and has a 0.6 success rate for a mid-skill player; a fall costs the run's remaining expected income of about 40 coins. The safe lane carries 10 coins. EV(risky) = 0.6×30 − 0.4×40 = 2 coins, which is below 10: mid-skill players should stay low. For a skilled player with p = 0.9, EV = 27 − 4 = 23, above 10: they take the rail. That is the intended sorting.

### Route design rules
- **Visible reward, readable risk.** The player must see what they gain and judge what they risk before committing.
- **Rejoin the main path.** Optional routes reconnect quickly; on mobile, no optional route should lead the player away for more than about 15–20% of the level's length.
- **Cap the downside.** A failed optional route should cost less than a failed main-path attempt; otherwise players stop taking risks.
- **Puzzle equivalent: bonus objectives.** Star thresholds, "finish under N moves", hidden collectibles. They add depth for experts without blocking casual players.
- **Match-3 equivalent:** a special near a cluster of blockers; using it now versus saving it is a risk/reward choice.

## 10. Flow in levels

Csikszentmihalyi (*Flow*, 1990) described flow as deep absorption when challenge matches skill, goals are clear and feedback is immediate. Jenova Chen ("Flow in Games", MFA thesis, 2006) argued that games should let players adjust their own challenge, because flow zones differ between players.

| Flow condition | Level design lever | Failure signal |
|---|---|---|
| Clear goals | Goal shown at level start and in the HUD; sub-goals visible | Players ask "what do I do?"; aimless movement in traces |
| Immediate feedback | Every action produces visible and audible response within ~100 ms | Repeated inputs on the same target |
| Challenge matches skill | Sawtooth curve; optional objectives; assists | Fail streaks of 3+ or perfect streaks with no tension |
| Sense of control | Deterministic rules; randomness before decisions, not after | "The game cheated me" in feedback |
| No interruption | No modal popups mid-level; ads only between levels | Session ends mid-level after a popup |
| Concentration | Low visual noise; one focal point at a time | Misreads; missed hazards |

**Player-driven difficulty first, system DDA second.** Optional routes, bonus objectives, boosters chosen before the level and assist modes keep the player in control. Hidden dynamic difficulty adjustment is a safety net only, never something that changes outcomes after a choice (`progression-difficulty`). Never use hidden adjustment to make players fail so they buy something; that breaks doctrine 8 (`legal-ethics`).

## 11. Mobile readability

A phone screen is small, partly covered by a thumb, and played in bright light, on a bus, one-handed, with interruptions. Design for the worst case.

### Screen geometry (derive, do not guess)
- Common portrait phone widths are roughly 360–440 points (iOS) or dp (Android). Design for the narrowest you support.
- Apple's Human Interface Guidelines recommend tap targets of at least 44×44 pt; Material Design recommends at least 48×48 dp. Treat these as minimums for *tap* targets.
- **Grid sizing formula:** `cell = (screen_width − 2·margin) / columns`. At 375 pt with 12 pt margins: 9 columns → 39 pt cells; 8 columns → 44 pt; 7 columns → 50 pt. This is one reason portrait match-3 boards usually stop at about 9 columns: swipe gestures tolerate slightly smaller cells than taps, but not much smaller. For tap-to-select puzzles, keep cells at or above the 44 pt / 48 dp minimum.

### Readability rules
| Rule | Starting value (heuristic) | Why |
|---|---|---|
| Distinct colours on screen at once | ≤ 6 | Beyond this, colours blur at small size; also a colour-blindness hazard |
| Every colour-coded element also has a shape or icon | Always | Colour-blind safety (`accessibility-localization`) |
| Thumb occlusion | Keep the critical area out of the bottom ~20% when the player is dragging; offset dragged items above the finger | The thumb hides what it touches |
| Safe areas | No gameplay-critical elements under notches, rounded corners or the home indicator | They are clipped or unreachable |
| Telegraph time for threats | ≥ 0.5 s for simple dodges; ≥ 1 s when the response needs a decision (tune by playtest) | Simple human reaction time is around 0.2–0.25 s; choice reactions and touch input add more |
| Text in levels | ≤ 10 words, ≥ the platform's body text size | Players skip text; small text is unreadable on low-end screens |
| Simultaneous moving threats | Few enough that each is trackable; test on the smallest supported screen | Small screens make dense scenes unreadable |
| Contrast of interactables vs background | High; check in sunlight or at low brightness | Outdoor play |

### Interruption-tolerant levels
- Levels of about **1–3 minutes** fit mobile sessions; any longer level needs checkpoints.
- Auto-pause on focus loss, and resume with a short countdown in real-time games.
- Turn-based puzzles should restore exactly on resume (persist the state every move).
- One-handed portrait: primary inputs in the bottom two thirds of the screen; the top third is for reading (goals, counters).

## 12. Level metrics

"Metrics" means two things in level design; keep both in writing.

### 12.1 Capability metrics (design-time)
The player's physical capabilities expressed in world units, plus the geometry rules that follow. Every level designer and generator must use the same numbers.

| Metric | Example value (2D platformer, 1 tile = 1 unit) | Derived rule |
|---|---|---|
| Run speed | 6 tiles/s | Corridor timing; enemy patrol speed ≤ 0.7× run speed so players can escape |
| Max jump height | 3.0 tiles | Easy ledges ≤ 2 tiles; hard ≤ 2.8 tiles |
| Max jump distance (running) | 5.0 tiles | Easy gaps ≤ 3 tiles (60%); medium ≤ 4 (80%); hard ≤ 4.5 (90%); never 5.0 |
| Coyote time | 0.1 s | Effective gap tolerance grows by speed × 0.1 = 0.6 tiles |
| Character width | 0.8 tiles | Minimum passage width 1 tile; comfortable 2 tiles |
| Camera view (portrait) | 9 × 16 tiles | Hazards must appear ≥ (reaction time × speed) ahead of the player |

The rule "never design at 100% of a capability" matters: input latency, touch imprecision and frame-rate variation on low-end phones eat the margin. Generators should read these numbers from one shared metrics file so procedural and handmade levels agree (`action-level-design.md` section 5).

### 12.2 Performance metrics (play-time)
What happens when people (or bots) play the level. These are the levels' health indicators; definitions and formulas are in `level-pipeline.md` section 12.

| Metric | Definition | Use |
|---|---|---|
| First-try win rate | Wins on first attempt ÷ first attempts | Compare with `difficulty_target.win_rate` |
| Overall win rate | Wins ÷ attempts | Difficulty per attempt |
| Attempts p50 / p90 | Median and 90th percentile attempts to win | Compare with `difficulty_target.attempts_p50` |
| Level churn | Players whose last session ended at this level (no return within N days) ÷ players who reached it | The most important health signal |
| Moves/time left on win | Distribution of slack at success | Near-miss tuning; many wins with 0–2 moves left feels exciting, too many feels rigged |
| Assist and booster use | Share of attempts using a hint, booster or continue | Hidden difficulty; monetization pressure |
| Duration | Seconds per attempt | Session fit |

### 12.3 Converting win rate to attempts
If each attempt succeeds independently with probability p (an approximation, since players learn), attempts to the first win follow a geometric distribution:

```
P(win within k attempts) = 1 − (1 − p)^k
median attempts = ceil( ln 0.5 / ln(1 − p) )
p90 attempts    = ceil( ln 0.1 / ln(1 − p) )
expected        = 1 / p
```

| Per-attempt win rate p | Median attempts | p90 attempts | P(3 fails in a row) |
|---|---|---|---|
| 0.90 | 1 | 1 | 0.1% |
| 0.70 | 1 | 2 | 2.7% |
| 0.50 | 1 | 4 | 12.5% |
| 0.35 | 2 | 6 | 27.5% |
| 0.25 | 3 | 9 | 42.2% |
| 0.15 | 5 | 15 | 61.4% |

Use this to reason about frustration: at p = 0.25, about 42% of players fail three times in a row. If lives are 5 and each fail costs one, that level will empty many players' lives. `python3 ${CLAUDE_PLUGIN_ROOT}/skills/level-design/scripts/level_audit.py odds --win-rate 0.25 --attempts 5` prints these figures for any p.

## 13. One-page principles review

Run this on any level before it enters the pipeline. A "no" needs a fix or a written reason in `notes`.

**Purpose**
- [ ] The brief states one idea, one role (teach/test/twist/reward) and target metrics.
- [ ] At most one element is new to the player; the rest are known.
- [ ] The intended solution or path is written in `notes`.

**Teaching and structure**
- [ ] A teach level's first contact is impossible to miss and very hard to fail.
- [ ] A test level uses only known elements and needs the new understanding.
- [ ] A twist level's surprise is explainable in one sentence afterwards.
- [ ] Inside the level, beats follow ki–shō–ten–ketsu or a deliberate alternative.

**Guidance**
- [ ] "Where next" is identifiable in a paused screenshot within 5 seconds.
- [ ] Interactive, deadly and collectable elements follow the reserved visual language.
- [ ] The goal or a landmark is visible from the start.

**Structure**
- [ ] Gates show what they lock; no gate requires premium currency to pass.
- [ ] Intensity alternates; the relief after a peak is designed.
- [ ] Optional routes show their reward and risk and rejoin quickly.

**Mobile**
- [ ] Cells and tap targets meet the size formula for the smallest supported screen.
- [ ] ≤ 6 colours at once; every colour cue has a shape cue.
- [ ] Nothing critical sits under the thumb, notch or home indicator.
- [ ] Level length fits the session target; state survives interruption.

**Verification**
- [ ] Solver or bot results are recorded in `solver` and agree with `difficulty_target` within tolerance.
- [ ] The level passes schema validation and `level_audit.py` in context with its neighbours.
