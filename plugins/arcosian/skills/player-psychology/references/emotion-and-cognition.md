# Emotion and Cognition

How players feel and think moment to moment, and how to design for it on a phone. The first half covers emotion: a working emotion model (valence, arousal and appraisal), emotional arcs at every time scale, fiero, the curiosity gap, surprise and prediction error, tension and release, awe, and frustration management with a catalogue of rage-quit triggers and their telemetry signatures. The second half covers cognition: cognitive load, attention, working memory, learning curves and skill acquisition, decision and motor time (Hick–Hyman, Fitts), and Gestalt perception applied to game UI and readability. It ends with a per-screen and per-level checklist. Pair with `game-feel` for feedback polish, `mobile-ux` for flows and layouts, and `progression-difficulty` for curves.

## Contents

1. A working emotion model: valence, arousal, appraisal
2. Emotional arcs
3. Fiero (triumph)
4. Curiosity and the information gap
5. Surprise, prediction error, wanting vs liking
6. Tension and release
7. Awe and wonder
8. Frustration management and rage-quit triggers
9. Cognitive load
10. Attention
11. Working memory and information design
12. Learning curves and skill acquisition
13. Decision time and motor time on touch screens
14. Gestalt perception for game UI
15. Readability and colour
16. Checklists: per level, per screen, per session
17. Sources

---

## 1. A working emotion model: valence, arousal, appraisal

Two complementary tools cover most design needs.

**Core affect (circumplex).** James Russell (1980) placed affective states on two axes: **valence** (unpleasant ↔ pleasant) and **arousal** (calm ↔ activated). Excitement is pleasant–high, contentment pleasant–low, anxiety unpleasant–high, boredom unpleasant–low. Useful for plotting arcs (§2) and for matching audio/visual intensity to gameplay.

**Appraisal.** Appraisal theories (for example Richard Lazarus 1991; Klaus Scherer's component process model) explain *which* emotion arises from how a person evaluates an event: Is it relevant to my goals? Does it help or hurt them? Who caused it? Can I cope with it? Appraisal is the designer's recipe book, because each appraisal maps to something the game controls.

| Emotion | Appraisal recipe | What the game controls |
|---|---|---|
| Fiero (triumph) | Important goal achieved + I caused it + it was hard / I had doubted I could | Difficulty, attributable feedback, prior failure, celebration |
| Frustration | Goal blocked + cause unclear or outside my control + I can't see how to cope | Clarity of failure cause, fairness, retry cost, hints |
| Anger | Goal blocked + someone else is to blame + unfair | Opponent behaviour, perceived P2W, matchmaking |
| Relief | Threat to goal removed | Tension build-up, then safe resolution |
| Curiosity | Noticed gap in knowledge + gap feels closable | Partial reveals, unknown outcomes, mysteries |
| Surprise | Event violates expectation | Prediction and its violation |
| Pride (naches, for others) | Someone I helped succeeded | Mentoring, gifting, co-op support |
| Amusement | Benign violation, playful incongruity | Physics comedy, character reactions |
| Boredom | Nothing relevant to goals happening; no challenge | Pacing, novelty schedule |
| Anxiety | Goal threatened + uncertain coping | Time pressure, stakes, unclear rules |
| Shame / embarrassment | Failure visible to others + attributed to self | Public failure displays, leaderboards |

**Design rule.** When an emotion is wrong, change the *appraisal input*, not the emotion's surface. Frustration from unclear failure is fixed by explaining the cause (coping, attribution), not by adding a cheerful sound.

---

## 2. Emotional arcs

An emotional arc is the planned shape of valence and arousal over time. Jesse Schell's "interest curve" (*The Art of Game Design*, 2008) is the most used version: a hook, rising peaks and valleys, a climax near the end and a short resolution. Plan arcs at every time scale.

| Scale | Typical length (mobile) | Shape | Key beats |
|---|---|---|---|
| Interaction | 0.1–2 s | Anticipation → impact → settle | Input, response, feedback (see `game-feel`) |
| Encounter / turn | 5–30 s | Small tension → release | Threat appears, player acts, outcome |
| Level / run | 1–5 min | Warm-up → escalation → climax → payoff | Easy opening, mid challenge, final wave/goal, results celebration |
| Session | 2–20 min | Hook → core block → peak → exit hook | Quick win, main play, best moment, closure + next goal |
| FTUE | 3–15 min | Wonder → competence → first fiero → meta reveal | Aha moment, first real choice, first win against odds, long-term goal shown |
| Chapter / world | days | Introduce → develop → twist → master | Teach–test–twist–reward across levels |
| Season / event | 1–6 weeks | Launch excitement → steady → finale | Kick-off, mid-season twist, final push, reward reveal |

### 2.1 Plotting an arc (procedure)
1. List beats with timestamps (seconds for a level, days for a season).
2. For each beat estimate valence (−2 … +2) and arousal (0 … 4).
3. Check: arousal rises overall with dips (no flat plateaus longer than ~30% of the span); valence never stays negative for more than one beat in a row for casual segments; the end beat is positive (peak-end, see `behavioral-economics-in-games.md` §15).
4. Check that monetization or ad beats do not sit at a high-arousal negative point (frustration peak).
5. Validate with playtest observation (facial expression, verbalisations, posture) and a one-tap end-of-level feeling rating.

### 2.2 Worked example: a 4-minute merge-defence level
| t (s) | Beat | Valence | Arousal |
|---|---|---|---|
| 0–15 | Board appears, first spawns; easy wave | +1 | 1 |
| 15–60 | Merges climb tiers; first new-tier reveal | +2 | 2 |
| 60–120 | Wave 3 adds a fast enemy; small scramble | 0 | 3 |
| 120–150 | Breather wave; player reorganises | +1 | 1 |
| 150–210 | Final wave + mini-boss; gate HP drops | −1 | 4 |
| 210–225 | Boss pops; last enemies cleared | +2 | 3 |
| 225–240 | Results: stars, coins, renovation reveal | +2 | 2 |

The breather at 120–150 s is a deliberate valley; without it the final wave arrives on top of fatigue and failure rates rise. The −1 beat is followed immediately by resolution.

---

## 3. Fiero (triumph)

Lazzaro's term for the triumphant feeling of overcoming adversity (see `motivation-models.md` §6). It is the strongest positive emotion games routinely produce, and it has prerequisites.

**Fiero recipe.**
1. **Perceived difficulty** — the player must believe it was hard. Prior failure is the most reliable signal; a visibly threatening boss or a low success indicator also works.
2. **Self-attribution** — the player must believe *they* did it. Wins that come from luck, auto-play or paid power produce relief at best.
3. **Clear, immediate confirmation** — a big, legible success moment within ~0.5 s of the decisive action.
4. **Proportionate celebration** — scale celebration to achievement. Over-celebrating trivial wins inflates feedback until it stops carrying information.

**Rule of thumb for celebration tiers.**
| Tier | When | Celebration |
|---|---|---|
| Micro | Every successful action | Crisp hit/merge feedback, small particle, sound |
| Minor | Normal level win | Results screen with stars and a short fanfare (~1–2 s) |
| Major | Hard level after ≥ 3 attempts, boss, personal best | Slow-motion finish, screen-wide effect, bespoke sting, shareable moment |
| Epic | Chapter end, rare mastery achievement | Unique animation, persistent trophy, social share option |

**Anti-patterns.** Fiero stolen by a post-victory popup offer; fiero diluted by identical celebration for every win; fiero blocked by a win the player did not understand ("why did I win?").

---

## 4. Curiosity and the information gap

**Model.** George Loewenstein (1994, "The Psychology of Curiosity") proposed that curiosity arises when attention is drawn to a gap between what we know and what we want to know. Curiosity is strongest when the gap is **salient and feels closable** — knowing a little about something makes people more curious than knowing nothing. Daniel Berlyne's earlier work identified *collative* properties that drive exploration: novelty, complexity, surprisingness and incongruity, with an inverted-U relationship between these and preference (too little is dull, too much is aversive).

**Design tactics.**
| Tactic | Example | Notes |
|---|---|---|
| Silhouettes and "?" slots | Unknown merge tier shown as a dark silhouette | Gap is visible and specific |
| Partial reveals | Map fog that lifts in pieces; half-visible area behind a door | Closable gap |
| Incongruity | An item that doesn't belong; a strange NPC | Raises questions |
| Unknown combinations | Merge chains with undiscovered results | Discovery motivation |
| Cliffhangers at session end | Story beat cut before the reveal | Pairs with the Ovsiankina effect |
| Collection gaps with known contents | Album pages showing what's missing | Completion motivation; keep it completable by play |

**Rules.**
- Every opened gap must be closable through play in a reasonable time; unanswered curiosity turns into frustration.
- Do not monetise curiosity through paid random reveals ("What's inside? Pay to find out"); curiosity is easily exploited by mystery boxes, which is why paid randomness is graded in `behavioral-economics-in-games.md` §2.
- Spoiler control: do not show every reward and recipe in the UI if Discovery is a target motivation; do show enough to make the gap visible.

---

## 5. Surprise, prediction error, wanting vs liking

**Prediction error.** Wolfram Schultz and colleagues (Schultz, Dayan & Montague 1997) showed that midbrain dopamine neurons signal *reward prediction error*: activity rises for better-than-expected outcomes, stays flat for fully expected ones and dips for worse-than-expected ones. Fully predictable rewards lose their motivational punch; that is why variable rewards are powerful (and why they are risky).

**Wanting vs liking.** Kent Berridge and Terry Robinson's research distinguishes *wanting* (incentive salience, the urge to pursue) from *liking* (the hedonic pleasure of consumption). They can come apart: compulsive patterns can involve intense wanting without matching liking. **This is the core ethical distinction for loop design**: a healthy loop produces both wanting and liking; a compulsion loop keeps wanting high while liking falls. Detect it in research when players describe continuing "even though I'm not enjoying it" (see `player-research-methods.md` §6 on regret and endorsement questions).

Popular "dopamine hit" language is a simplification; avoid it in design docs. Talk about prediction, expectation and reward instead.

**Designing surprise.**
- **Positive surprises**: unexpected bonus chests for exploration, rare animations, a character doing something funny. Keep them free and occasional (a novelty schedule: something new roughly every few sessions in the first week).
- **Negative surprises**: an ambush, a twist rule. They must be *explicable in hindsight* — the player should be able to say "I should have seen that coming". Unexplained negative surprises feel unfair.
- **Surprise decays**: the second time is less surprising. Rotate surprise content; use procedural variation for repeatable surprises.

---

## 6. Tension and release

Tension is sustained arousal from uncertain outcomes with stakes; release is its resolution. Suspense needs three ingredients: **stakes** (something the player cares about), **uncertainty** (outcome genuinely open), and **time** (the outcome unfolds rather than being instant).

**Patterns.**
| Pattern | Structure | Example |
|---|---|---|
| Sawtooth | Build → release → slightly higher build | Wave-based defence; level difficulty curves |
| Ticking clock | Rising pressure with a visible limit | Moves counter turning red; final 10 seconds |
| Push-your-luck | Player chooses to keep risking for more | Cash-out decisions in roguelite runs |
| Calm before the storm | Deliberate quiet before a peak | Breather wave before the boss |
| Reprieve | Last-moment rescue | Final blocker cleared with the last move |

**Excitation transfer.** Dolf Zillmann's excitation-transfer work (from the early 1970s) suggests residual arousal from one event can intensify the emotion felt at the next. Practical use: a high-arousal climax makes the following success feel bigger — put the celebration right after the climax, not after a loading screen.

**Rules.**
- Release must be complete: clear the screen, change the music, give the player a beat to breathe (0.5–2 s).
- Mobile arousal is context-dependent (commute vs bed). Offer calm modes or no-timer variants for relaxer segments.
- Never use real-money decisions as the tension device ("pay before the timer ends") — red line.

---

## 7. Awe and wonder

Dacher Keltner and Jonathan Haidt (2003) described awe as a response to **perceived vastness** (physical, conceptual or social) that creates a **need for accommodation** — updating one's mental model. Awe is rare in mobile games because screens are small, but it can be designed.

**Mobile awe toolkit.**
- **Scale contrast**: pull the camera back to show the tiny board inside a huge world; reveal a structure much larger than the player's units.
- **Accumulation reveals**: show the whole map of everything the player has built or restored ("look how far you've come").
- **Slowdown**: decelerate time and audio at reveals; silence before a swell.
- **Systemic awe**: a cascade or chain reaction far larger than expected (combo across the whole board).
- **Use sparingly**: awe depends on contrast. One deliberate awe moment per chapter is plenty.

Accessibility: sweeping camera moves and flashes can trigger motion sickness or photosensitivity; respect reduced-motion OS settings and avoid high-frequency flashing (see `accessibility-localization`).

---

## 8. Frustration management and rage-quit triggers

Frustration is not the enemy; *unproductive* frustration is. Hard Fun needs frustration as the setup for fiero. The design goal is to keep frustration **attributable, short, recoverable and informative**.

### 8.1 Productive vs destructive frustration
Kiel Gilleade and Alan Dix (2004) discuss a useful distinction between frustration *at* the game (fighting the interface, controls, bugs) and frustration *in* the game (the challenge itself). The first is always a defect; the second is a tool.

| Productive frustration | Destructive frustration |
|---|---|
| Player knows why they failed | Player cannot explain the failure |
| Can see what to try differently | Sees no path forward |
| Retry is instant and cheap | Retry is slow, costly or gated by energy/payment |
| Failure feels fair (same rules for everyone) | Failure feels rigged (randomness, P2W, opaque DDA) |
| Progress kept or knowledge gained | Progress lost |
| Player chose the difficulty | Difficulty imposed, unexpected spike |

### 8.2 Rage-quit triggers: catalogue with telemetry signatures

| Trigger | Typical cause | Telemetry signature | Fix |
|---|---|---|---|
| Unclear failure cause | Hidden rules, off-screen threats, ambiguous feedback | Quit within 10 s of a fail screen; low retry rate | Fail recap ("Defeated by X — try Y"); telegraph threats; replay last 3 s |
| Input not registering / misreads | Small targets, gesture conflicts, latency | High rate of repeated taps on same spot; mis-taps near edges | Bigger hit areas; input buffering; remove gesture conflicts (`mobile-ux`) |
| Difficulty spike | Curve jump, new mechanic + higher difficulty together | Attempts per level jumps; churn concentrated at one level | Smooth curve; never teach and test hard in the same level; `difficulty_curve.py analyze` |
| Output randomness at high stakes | Random loss after a long run | Quits right after a random event; complaints about "luck" | Move randomness to input; cap variance; pity (`design-theory`) |
| Losing progress | Long run lost to one mistake; streak reset | Session end immediately after loss of banked progress | Checkpoints; partial keep; decay instead of reset |
| Long retry loop | Loading screens, energy waits, ad before retry | Time fail→next attempt > 10 s correlates with quit | One-tap retry in < 3 s; no ads between fail and retry |
| Perceived pay-to-win | Opponents with purchased power | PvP churn after losses against high-spend opponents | Matchmake by power; cap paid power; skill-first balance |
| Repeated identical failure | Player stuck on same obstacle | ≥ 4 consecutive fails at same point | Contextual hint after 3 fails; optional skip earned by play |
| Social humiliation | Public failure, toxic chat, kicked from team | Churn after chat reports or team kicks | Mute by default for new players; private failure; gentle team rules |
| Interrupted flow | Interstitial or popup during play | Quit within seconds of an ad or popup | Ads only at natural breaks; popup queue with caps |
| Unfair AI | AI that sees hidden info or cheats visibly | Complaints, quits after specific AI moves | Honest AI constraints; rubber-banding disclosed or subtle and bounded |

### 8.3 The frustration budget (studio starting points — tune with data)
- **Fail → retry time** under 3 s; nothing between the fail screen and the next attempt except one tap.
- **Consecutive fails before help**: offer a free, non-monetised hint or a lighter variant after the 3rd consecutive fail at the same level; offer an earned skip (via play, not payment) after the 5th–7th for non-competitive content.
- **Difficulty valleys**: after every hard level, at least one easier level (sawtooth).
- **Progress loss** on failure: none in the first session; never more than the current attempt in casual games.
- **Time pressure**: avoid timers on planning decisions; offer a no-timer option for relaxer segments.

### 8.4 Mercy mechanics and their honesty
Many games quietly help struggling players: item distributions that favour trailing racers (the *Mario Kart* series is the well-known example), adaptive difficulty that eases enemies after repeated deaths (widely discussed for *Resident Evil 4*), and explicit options such as *Celeste*'s Assist Mode, which lets players slow the game or become invincible without judgement.

| Approach | Strength | Risk | Studio stance |
|---|---|---|---|
| Explicit assist options (player chooses) | Respects autonomy; transparent | Some players feel stigma; design copy matters | Preferred |
| Invisible DDA (system adjusts) | Smooth, no stigma | Discovery feels like betrayal; undermines fiero if large | Allowed as a bounded safety net in single-player; never in competitive modes |
| Spend-dependent difficulty (harder unless you pay, or easier after paying) | — | Deceptive; destroys trust | Red line |

---

## 9. Cognitive load

John Sweller's cognitive load theory (1988 onward) distinguishes:
- **Intrinsic load** — inherent complexity of what must be understood (the rules).
- **Extraneous load** — load imposed by poor presentation (cluttered HUD, inconsistent icons, reading walls of text).
- **Germane load** — effort devoted to building understanding (schemas). In later formulations this is folded into intrinsic load, but the design point holds: spend the player's capacity on learning the game, not on decoding the interface.

**Design rules.**
- Cut extraneous load first; it buys capacity for intrinsic depth.
- Introduce one new concept at a time and let it become automatic before adding another (the early-game rule of thumb in `design-theory`: ≤ 1 new element per 3–5 levels).
- Prefer showing over telling: a ghost hand demonstrating a drag beats a sentence explaining it.
- Use consistent mappings: the same colour, icon and sound always mean the same thing.

**Complexity budget for an FTUE step (studio heuristic).** Count new elements the player must attend to (a new verb, a new UI element, a new rule, a new currency). Budget per FTUE step: **1 new element**, **≤ 2 on screen competing for attention**, **≤ 12 words of instruction**. Steps that exceed the budget are split.

---

## 10. Attention

Attention is selective and limited. Key findings designers rely on:

- **Inattentional blindness** — people focused on a task can miss obvious unexpected objects (Simons & Chabris 1999, the "gorilla" study). Players focused on the board miss HUD changes, banners and new buttons.
- **Change blindness** — changes during a visual disruption (screen transition, flash) often go unnoticed. Never rely on players noticing a counter that changed during a transition.
- **Pre-attentive features** — some properties are detected in parallel, almost instantly: colour, size, orientation, motion, onset (Anne Treisman's feature-integration theory, Treisman & Gelade 1980). A single red item among blue ones pops out; an item defined by a *combination* of features (red *and* square among red circles and blue squares) needs serial search.
- **Motion and onset capture attention** — a newly appearing or moving element grabs attention involuntarily. This is powerful and must be rationed.
- **Banner blindness** — users learn to ignore areas that usually contain ads or promotions. Important information must not look like an offer.

**Mobile attention rules.**
| Rule | Why |
|---|---|
| One animated attention-grabber on screen at a time | Multiple motions compete and all lose |
| Critical gameplay information near the point of focus (the board), not at screen edges | Inattentional blindness during play |
| Use pre-attentive pop-out (colour + size + motion) for threats and goals only | Reserve the channel for what matters |
| Hands occlude the screen: keep critical info out of the thumb's shadow (lower-centre in portrait for right-thumb play) | Physical occlusion |
| Promotions visually distinct from gameplay UI and never placed where gameplay buttons usually are | Prevents misclicks and banner blindness on real information |
| Audio and haptics as redundant channels for critical events, but the game must be fully playable muted | Many players play without sound |

---

## 11. Working memory and information design

Working memory holds only a few items at once. George Miller's (1956) famous "seven, plus or minus two" has been revised downward; Nelson Cowan (2001) argued capacity is about **four chunks** for most adults when rehearsal is prevented. Under time pressure and distraction (typical on mobile), assume less.

**Design implications.**
- **Externalise memory**: show the information the current decision needs instead of requiring recall (enemy intents visible, next pieces previewed, cooldowns displayed on the button).
- **Recognition over recall** (also one of Jakob Nielsen's usability heuristics): icons with labels on first exposure; recipes visible where crafting happens.
- **Chunk information**: group stats into 3–4 meaningful clusters; break long numbers (12,400 not 12400).
- **Limit hidden state**: every hidden rule is a working-memory tax and a source of "unfair" failures.
- **Interruption recovery**: phones interrupt. On resume, show a 1-line recap of the current goal and state; never assume the player remembers what they were doing after a call.

---

## 12. Learning curves and skill acquisition

### 12.1 Power law of practice
Performance time on a task typically falls as a power function of practice (Newell & Rosenbloom 1981): `T_N = T_1 · N^(−α)`, where *T₁* is the first-trial time, *N* the trial number and *α* a task-specific learning rate (fit it from your data rather than assuming).

**Worked example.** If a puzzle type takes 60 s on first encounter and α = 0.4: trial 10 takes `60 × 10^−0.4 ≈ 24 s`; trial 50 takes `60 × 50^−0.4 ≈ 13 s`. Gains flatten quickly — after ~20 encounters a pattern is largely mastered, so plan a twist or a new pattern before then (Koster's and Cook's mastery-horizon ideas in `design-theory`).

### 12.2 Learning principles that transfer to game onboarding
| Principle | Source | Game application |
|---|---|---|
| Learning by doing beats instruction | Broad educational research; applied to games by Celia Hodent (*The Gamer's Brain*, 2017) | Teach each verb in a safe, playable moment |
| Scaffolding within the zone of proximal development | Vygotsky; Wood, Bruner & Ross (1976) on scaffolding | Support early, then fade the support (hints that disappear) |
| Spacing effect | Ebbinghaus (1885) and much later research | Reintroduce mechanics across sessions, not all in one level |
| Retrieval practice (testing effect) | Roediger & Karpicke (2006) | Teach → test later without reminders → twist |
| Forgetting curve | Ebbinghaus (1885) | Re-onboard lapsed players: short refresher after ~7+ days away |
| Transfer and interference | General learning research | Keep controls consistent with genre conventions unless the twist is the point |

### 12.3 Teach → test → twist → reward
The level-spec `teach` field (`teach|test|twist|reward`) encodes this sequence. Introduce a mechanic in a low-risk level (teach), require it with moderate stakes (test), combine it with something known or change a rule (twist), then give an easier, generous level (reward). Never introduce a mechanic in the same level as a difficulty spike.

### 12.4 Measuring learning
- Attempts to first clear per level and their trend for each new mechanic.
- Time-per-action on repeat encounters (should follow a declining power curve).
- Error types: if errors persist after 5+ encounters, the mechanic is unclear, not hard.

---

## 13. Decision time and motor time on touch screens

**Hick–Hyman law.** Choice reaction time grows with the logarithm of the number of equally likely options: `RT = a + b · log₂(n + 1)` (Hick 1952; Hyman 1953). Going from 2 to 8 options roughly doubles the log term (log₂3 ≈ 1.58 → log₂9 ≈ 3.17). This is why mobile decision sets should be 2–4 options for time-pressured choices.

**Fitts's law.** Time to hit a target grows with distance and shrinks with size: `MT = a + b · log₂(D / W + 1)` (Fitts 1954; this is the common Shannon formulation by MacKenzie). On touch, small distant targets are slow and error-prone; the thumb's reach adds a physical cost (see thumb zones in `mobile-ux`).

**Touch target minimums (platform guidelines).** Apple's Human Interface Guidelines recommend tappable controls of at least 44 × 44 points; Google's Material Design recommends at least 48 × 48 dp. Gameplay targets under time pressure should be larger than these minimums.

**Reaction time and latency.** Simple visual reaction times for young adults are commonly cited around 200–250 ms and slow with age and choice complexity; device touch-to-display latency adds tens of milliseconds or more and varies by device (verify on target hardware). Studio starting point: telegraph any threat the player must react to by ≥ 500 ms on mobile, longer for casual audiences, and give windows rather than frame-perfect timings.

---

## 14. Gestalt perception for game UI

The Gestalt principles (from early 20th-century German psychology: Wertheimer, Köhler, Koffka; later extensions such as common region and uniform connectedness by Stephen Palmer and Irvin Rock in the 1990s) describe how people group visual elements into wholes. They are the cheapest way to make a dense mobile screen readable.

| Principle | Perception | Game UI application | Common failure |
|---|---|---|---|
| **Proximity** | Close items are seen as a group | Group a currency icon with its amount and its "+" button; keep ability buttons together | Spacing that groups the wrong things (price closer to the neighbouring item than to its own) |
| **Similarity** | Items sharing colour, shape or size are grouped | All interactable objects share one visual language (outline, bounce); all enemies share a palette distinct from allies | Decorative elements that look interactable; offers styled like gameplay buttons |
| **Common region** | Items inside a shared boundary are grouped | Card frames, panels for each shop item, team zones | Boundaries that split related info |
| **Closure** | The mind completes incomplete shapes | Simplified icons and silhouettes; progress rings | Over-simplified icons that close into the wrong shape |
| **Continuity** | Elements on a line or curve are seen as related | Paths, conveyor belts, guide arrows, enemy lanes | Paths that visually merge where they do not connect in the rules |
| **Common fate** | Things moving together are grouped | Enemy waves moving in formation; UI elements that animate in together | Unrelated elements animating in sync and appearing linked |
| **Figure–ground** | We separate a figure from its background | Characters and interactables contrast strongly with the board; darken background under popups | Busy backgrounds with values similar to the units; "muddy" boards |
| **Prägnanz (simplicity)** | We perceive the simplest interpretation | Readable silhouettes for every unit at thumbnail size | Detail-rich sprites indistinguishable at phone scale |
| **Symmetry and order** | Symmetric arrangements read as stable wholes | Balanced result screens; symmetric reward layouts | Asymmetric layouts that imply a hierarchy that isn't there |
| **Uniform connectedness** | Connected elements read as one unit | Lines joining skill-tree nodes; tethers between linked units | Decorative lines that imply connections |

**Readability procedure (screen review).**
1. **Squint/blur test**: blur the screenshot; the three most important elements must still be identifiable by value contrast and shape.
2. **Greyscale test**: convert to greyscale; threats, goals and interactables must remain distinguishable (catches colour-only coding).
3. **Silhouette test**: fill every unit/enemy black; each must be identifiable by silhouette at the actual on-device size.
4. **Grouping test**: ask a tester (or reason explicitly) which elements belong together; compare with the intended grouping.
5. **Offer separation test**: every monetisation element is distinguishable from gameplay UI by region and style.

---

## 15. Readability and colour

- **Colour vision deficiency** is common: figures typically cited are about 8% of men and 0.5% of women of Northern European ancestry, mostly red–green deficiencies. Never encode critical information by hue alone; add shape, icon, pattern or position (redundant coding). Test with colour-blindness simulation filters.
- **Contrast**: WCAG 2.1 asks for at least 4.5:1 for normal text and 3:1 for large text and essential UI component boundaries (success criteria 1.4.3 and 1.4.11). These are web standards, but they are a good floor for game UI text and HUD elements (see `accessibility-localization`).
- **Value before hue**: readability on small screens depends mostly on light–dark (value) contrast. Design the board in greyscale first, then add hue.
- **Text on phones**: short labels, large type, no essential information in body text during play.
- **Outdoor and low-brightness play**: phones are used in sunlight and in dark bedrooms; test both. Avoid low-contrast pastel-on-pastel for critical info.

---

## 16. Checklists: per level, per screen, per session

### Per level
- [ ] Arc plotted: warm-up, escalation, breather, climax, payoff; end beat positive.
- [ ] One new element at most; teach/test/twist/reward role recorded in the level spec.
- [ ] Every failure cause visible and attributable; fail recap available.
- [ ] Retry in one tap, < 3 s.
- [ ] Threat telegraphs ≥ 500 ms; no frame-perfect windows for casual audiences.
- [ ] Celebration tier proportionate to difficulty (major celebration only after real difficulty).
- [ ] Randomness placed on input, not on decisive output, at high stakes.

### Per screen
- [ ] Passes blur, greyscale, silhouette, grouping and offer-separation tests.
- [ ] At most one animated attention-grabber.
- [ ] Information needed for the current decision visible (no recall required).
- [ ] Touch targets ≥ platform minimums; critical buttons in thumb reach.
- [ ] Text ≤ 12 words for instructions; contrast meets the WCAG floor.
- [ ] No colour-only encoding.

### Per session
- [ ] Quick win within 30–60 s of session start.
- [ ] At least one peak (fiero or awe) for challenge segments, one calm beat for relaxers.
- [ ] Natural stopping point with closure plus one optional open goal.
- [ ] No ads, offers or rating prompts at frustration peaks or inside flow segments.
- [ ] Resume after interruption restores state and shows a one-line goal recap.

---

## 17. Sources

Paraphrased; consult originals.

- Berlyne, D. E. (1960). *Conflict, Arousal, and Curiosity*. McGraw-Hill.
- Berridge, K. C., & Robinson, T. E. (1998). "What is the role of dopamine in reward: hedonic impact, reward learning, or incentive salience?" *Brain Research Reviews*, 28(3).
- Cowan, N. (2001). "The magical number 4 in short-term memory." *Behavioral and Brain Sciences*, 24(1).
- Ebbinghaus, H. (1885). *Über das Gedächtnis* (*Memory: A Contribution to Experimental Psychology*).
- Fitts, P. M. (1954). "The information capacity of the human motor system in controlling the amplitude of movement." *Journal of Experimental Psychology*, 47(6).
- Gilleade, K. M., & Dix, A. (2004). "Using frustration in the design of adaptive videogames." *Proceedings of ACE 2004*.
- Hick, W. E. (1952). "On the rate of gain of information." *Quarterly Journal of Experimental Psychology*, 4(1). — Hyman, R. (1953). "Stimulus information as a determinant of reaction time." *Journal of Experimental Psychology*, 45(3).
- Hodent, C. (2017). *The Gamer's Brain: How Neuroscience and UX Can Impact Video Game Design*. CRC Press.
- Keltner, D., & Haidt, J. (2003). "Approaching awe, a moral, spiritual, and aesthetic emotion." *Cognition and Emotion*, 17(2).
- Lazarus, R. S. (1991). *Emotion and Adaptation*. Oxford University Press.
- Loewenstein, G. (1994). "The psychology of curiosity: A review and reinterpretation." *Psychological Bulletin*, 116(1).
- MacKenzie, I. S. (1992). "Fitts' law as a research and design tool in human-computer interaction." *Human-Computer Interaction*, 7(1).
- Miller, G. A. (1956). "The magical number seven, plus or minus two." *Psychological Review*, 63(2).
- Newell, A., & Rosenbloom, P. S. (1981). "Mechanisms of skill acquisition and the law of practice." In J. R. Anderson (Ed.), *Cognitive Skills and Their Acquisition*.
- Palmer, S., & Rock, I. (1994). "Rethinking perceptual organization: The role of uniform connectedness." *Psychonomic Bulletin & Review*, 1(1).
- Roediger, H. L., & Karpicke, J. D. (2006). "Test-enhanced learning." *Psychological Science*, 17(3).
- Russell, J. A. (1980). "A circumplex model of affect." *Journal of Personality and Social Psychology*, 39(6).
- Schell, J. (2008). *The Art of Game Design: A Book of Lenses*. Morgan Kaufmann.
- Schultz, W., Dayan, P., & Montague, P. R. (1997). "A neural substrate of prediction and reward." *Science*, 275(5306).
- Simons, D. J., & Chabris, C. F. (1999). "Gorillas in our midst." *Perception*, 28(9).
- Sweller, J. (1988). "Cognitive load during problem solving: Effects on learning." *Cognitive Science*, 12(2).
- Treisman, A. M., & Gelade, G. (1980). "A feature-integration theory of attention." *Cognitive Psychology*, 12(1).
- W3C (2018). *Web Content Accessibility Guidelines (WCAG) 2.1* — https://www.w3.org/TR/WCAG21/
- Wood, D., Bruner, J. S., & Ross, G. (1976). "The role of tutoring in problem solving." *Journal of Child Psychology and Psychiatry*, 17(2).
- Zillmann, D. (1971). "Excitation transfer in communication-mediated aggressive behavior." *Journal of Experimental Social Psychology*, 7(4).
- Platform guidelines: Apple Human Interface Guidelines (https://developer.apple.com/design/human-interface-guidelines/) and Material Design (https://m3.material.io/) — touch-target minimums.
