# Motivation Models

Why people start, keep and stop playing — the models a senior designer actually uses, what each one is good for, how to turn it into a design decision, and where it breaks. Covers self-determination theory and its game instrument PENS (plus the newer open BANGS scale), Bartle's types (and why not to use them as a personality test), Quantic Foundry's twelve motivations, Yee's MMO components, Lazzaro's four keys, the Fogg behaviour model, Eyal's Hook model and his manipulation matrix, flow and GameFlow, achievement-goal and social-comparison theory, a working set of mobile player segments, a model-selection table, a worked example against the studio's sample contract, and a limits table. Motivation *labels* written into `contract.meta.target_audience.motivations` should use Quantic Foundry names; the reasoning behind them comes from the rest of this file.

## Contents

1. Which model for which decision
2. Self-determination theory (SDT) and PENS
3. Bartle's player types (and the 8-type extension)
4. Quantic Foundry Gamer Motivation Model
5. Yee's motivation components
6. Lazzaro's four keys to emotion
7. Fogg behaviour model (B = MAP)
8. Hook model and the manipulation matrix
9. Flow, GameFlow and player-driven flow
10. Achievement goals and social comparison
11. Mobile player segments (studio working model)
12. Combining models: the motivation pass
13. Worked example: Pebble Keep
14. Limits of each model
15. Sources

---

## 1. Which model for which decision

No single model answers every question. Pick by the decision you are making, not by habit.

| Decision you are making | Best primary model | Secondary check | Why |
|---|---|---|---|
| Who is this game for? Which features matter? | Quantic Foundry (12 motivations) | Mobile segments (§11) | Empirically derived, game-agnostic vocabulary, works for feature triage |
| Will players keep playing for months, and feel good about it? | SDT / PENS / BANGS | Flow | Best evidence linking need satisfaction to enjoyment, wellbeing and continued play |
| What emotion should this moment produce? | Lazzaro's four keys | `emotion-and-cognition.md` | Maps mechanics to emotions (fiero, curiosity, amusement, relief) |
| Why don't players do the thing we want (open the pass, try the new mode)? | Fogg B = MAP | Hook model | Diagnoses motivation vs ability vs prompt failures precisely |
| How should the habit loop / return loop work? | Hook model | Manipulation matrix + SDT | Describes habit formation; the matrix and SDT keep it honest |
| Is the difficulty right second-to-second? | Flow / GameFlow | `progression-difficulty` | Challenge–skill balance, feedback, goals, control |
| How should leaderboards, leagues and PvP be framed? | Achievement goals + social comparison | SDT relatedness | Predicts who is motivated or demotivated by ranking |
| How do social systems interact in a persistent world? | Bartle (as a dynamics model) | Yee | Bartle's real value is population dynamics, not individual typing |
| Who are our players in research and personas? | Mobile segments + JTBD | `player-research-methods.md` | Behavioural, situational and testable |

**Rule.** Use one model's vocabulary per artefact. A contract that lists "achiever, hard fun, competence, strategy" mixes four models and becomes unfalsifiable. Labels go in Quantic Foundry terms; the SDT audit, the Lazzaro emotion map and the Fogg diagnosis are separate passes with their own outputs.

---

## 2. Self-determination theory (SDT) and PENS

### 2.1 The model in brief
Self-determination theory (Edward Deci and Richard Ryan, developed from the 1970s; summarised in Ryan & Deci 2017, *Self-Determination Theory*) proposes three universal psychological needs whose satisfaction predicts motivation quality and wellbeing:

| Need | What it feels like | Game expression |
|---|---|---|
| **Competence** | I am effective; I am getting better | Clear goals, readable feedback, fair challenge, visible growth |
| **Autonomy** | I chose this; it reflects me | Meaningful choices, opt-in goals, self-paced play, expression |
| **Relatedness** | I matter to others; they matter to me | Cooperation, recognition, gifting, belonging to a team |

Ryan, Rigby and Przybylski (2006, *Motivation and Emotion*) applied SDT to video games and found that need satisfaction predicted enjoyment, preference for future play and short-term wellbeing changes across several studies. Rigby and Ryan's *Glued to Games* (2011) popularised the **PENS** model (Player Experience of Need Satisfaction), which adds two game-specific factors:

- **Presence / immersion** — feeling inside the game world (physical, emotional, narrative presence).
- **Intuitive controls** — controls that get out of the way. Controls are a precondition: poor controls block competence and autonomy no matter how good the design.

### 2.2 The SDT sub-theories that matter to designers

**Cognitive evaluation theory (CET).** Rewards and feedback have two possible functional meanings:
- *Informational* — tells the player about their competence ("Perfect clear: 3 stars"). Supports intrinsic motivation.
- *Controlling* — pressures behaviour ("Log in tomorrow or lose your streak"). Tends to undermine intrinsic motivation for activities that were already enjoyable (the overjustification effect; Deci, Koestner & Ryan's 1999 meta-analysis found tangible, expected, contingent rewards reduced free-choice intrinsic motivation on interesting tasks, while positive verbal feedback tended to increase it).

**Organismic integration theory (OIT).** Extrinsic motivation is a continuum, not a single state:

| Regulation | Player's inner voice | Typical game source | Durability |
|---|---|---|---|
| External | "I do it for the reward / to avoid the penalty" | Daily login reward, streak loss | Lowest; collapses when the reward ends |
| Introjected | "I'd feel guilty or anxious if I didn't" | Team obligation guilt, FOMO | Low; corrodes wellbeing |
| Identified | "I value what this gets me" | Practising a mode because it makes me better at the main mode | Medium-high |
| Integrated | "This is part of who I am" | "I'm a collector; finishing sets is my thing" | High |
| Intrinsic | "I do it because it is fun in itself" | The core verb | Highest |

Design implication: move each extrinsic structure *rightwards*. A daily quest that says "Play 3 levels" is external; one that says "Try the new Frost Golem in 3 levels" invites exploration and is closer to identified/intrinsic.

**Basic psychological needs theory — satisfaction vs frustration.** Need *frustration* (feeling controlled, incompetent or rejected) is not just low satisfaction; it is an active negative state linked to ill-being and, in games, to toxic behaviour and quitting (see Vansteenkiste & Ryan 2013 on need frustration). A game can score high on satisfaction for some players and high on frustration for others (pay-to-win opponents, hostile chat). Audit both.

### 2.3 Using SDT in design decisions

**Need audit procedure (per feature).**
1. For each need, write how the feature *satisfies* it and how it could *frustrate* it.
2. Score each −2 … +2. A feature with any −2 needs a redesign or a mitigation before build.
3. Check the reward framing (CET): is every reward message informational? Rewrite controlling copy.
4. Place every extrinsic structure on the OIT continuum; move at least one step right where possible.
5. Re-run after playtests using a needs scale (PENS under licence, or BANGS — see `player-research-methods.md` §6).

| Feature | Competence | Autonomy | Relatedness | Frustration risk |
|---|---|---|---|---|
| Weekly league with promotion/relegation | +2 for skilled, −1 for bottom | 0 | +1 | Demotion; bracket mismatch |
| Mandatory daily quest list (5 tasks) | +1 | −2 (obligation) | 0 | Guilt, streak anxiety |
| Optional 3-star objectives | +2 | +2 (opt-in) | 0 | Low |
| Team chest requiring every member | 0 | −1 | +1 / −2 when let down | Social obligation, blame |
| Cosmetic editor with sharing | 0 | +2 | +1 | Low |

### 2.4 SDT on mobile
- Short sessions favour **competence microdoses**: a win or visible progress inside the first 30–60 seconds of every session.
- Autonomy on mobile is mostly **pacing autonomy**: play 1 minute or 30 without penalty. Energy systems and appointment mechanics trade autonomy for monetization; budget that cost explicitly.
- Relatedness on mobile is mostly **asynchronous and light** (gifting, visiting, team goals); synchronous obligation frustrates relatedness for players with fragmented time.

### 2.5 Limits
SDT says *what* needs matter, not *how much* of each your audience wants or which mechanic to build. Effect sizes in lab studies are modest and self-report-based. Needs are universal in theory, but their expression varies by culture and context. PENS is a proprietary instrument (owned by Immersyve; see `player-research-methods.md` §6 for licence notes).

---

## 3. Bartle's player types (and the 8-type extension)

### 3.1 The model
Richard Bartle (1996, "Hearts, Clubs, Diamonds, Spades: Players Who Suit MUDs") described four ways players enjoyed text MUDs, organised on two axes: **acting on vs interacting with**, and **players vs world**.

| | Acting on | Interacting with |
|---|---|---|
| **World** | Achievers (master the world's goals) | Explorers (discover how the world works) |
| **Players** | Killers (impose on other players) | Socialisers (relate to other players) |

The most useful and least quoted part of the paper is the **population dynamics**: the types affect each other. Killers drive away socialisers and achievers if unchecked; socialisers attract more socialisers; explorers are relatively stable. Changing the game's balance of support for each type shifts the population.

Bartle's later book *Designing Virtual Worlds* (2003) added an implicit/explicit axis, producing eight types (for example Achievers split into Planners and Opportunists; Explorers into Scientists and Hackers; Socialisers into Networkers and Friends; Killers into Politicians and Griefers) and proposed developmental paths players move along over time.

### 3.2 Using it today
- **As a dynamics lens for persistent social games:** if you add PvP raiding to a co-operative city builder, model what happens to the socialiser population. Bartle predicts losses unless griefing is contained (shields, opt-in PvP, matchmaking).
- **As a vocabulary for discussing toxicity:** the "Killer" quadrant covers both competitive play (beating others) and griefing (harming others). Design to channel the first and remove payoff from the second.
- **Not as a personality test.** The online "Bartle Test" questionnaire was written by others (Erwin Andreasen and Brandon Downey), not by Bartle, and Bartle has repeatedly cautioned against using his types outside the context they were derived from.

### 3.3 Limits
Derived from observation of a few dozen MUD veterans, not from statistical analysis; Yee's factor-analytic work (§5) found the components did not form four exclusive types. Single-player and casual mobile play fall largely outside it. Never write "our target audience is Achievers" in a contract — use Quantic Foundry labels.

---

## 4. Quantic Foundry Gamer Motivation Model

### 4.1 The model
Nick Yee and Nicolas Ducheneaut (Quantic Foundry) built a motivation model from large-scale online survey data (their published materials cite very large respondent counts) using factor analysis. It has **12 motivations in 6 pairs**, which cluster into 3 higher-order groups.

| Higher-order cluster | Pair | Motivation | Short definition |
|---|---|---|---|
| Action–Social | Action | Destruction | Guns, explosives, chaos, mayhem |
| | | Excitement | Fast-paced, surprising, thrilling |
| | Social | Competition | Duels, matches, rankings against others |
| | | Community | Being on a team, chatting, interacting |
| Mastery–Achievement | Mastery | Challenge | Practice, difficult challenges |
| | | Strategy | Thinking ahead, making decisions |
| | Achievement | Completion | Getting all collectibles, finishing missions |
| | | Power | Becoming powerful, powerful gear |
| Immersion–Creativity | Immersion | Fantasy | Being someone else, somewhere else |
| | | Story | Elaborate plots, interesting characters |
| | Creativity | Design | Expression, customisation |
| | | Discovery | Exploring, tinkering, experimenting |

Definitions above are paraphrased; see Quantic Foundry's own materials for theirs.

Patterns Quantic Foundry has reported publicly (treat as directional; verify against their current reports before quoting numbers): motivations within a cluster correlate (players high in Strategy tend to be high in Challenge); **Competition and Excitement decline with age** more than other motivations; gender differences are real on some motivations but smaller than stereotypes suggest, and within-gender variation dwarfs between-gender differences.

### 4.2 Using it in design decisions
1. **Audience definition.** Choose 3–4 primary motivations for the target segment. Write them into `contract.meta.target_audience.motivations` using these labels, lower-case.
2. **Feature triage.** Every feature must serve at least one primary motivation. Score each feature: 2 = serves a primary motivation strongly, 1 = weakly, 0 = only serves non-primary motivations. Features scoring 0 are cost centres unless they deliberately open a new segment.
3. **Conflict check.** Some motivation pairs pull features in opposite directions: Competition vs Community (zero-sum vs cooperative social), Excitement vs Strategy (time pressure vs thinking time), Completion vs Discovery (checklists vs mystery). If both are primary, separate them into modes.
4. **Comparable mapping.** When deconstructing a comparable, record which motivations each system serves; this is the cleanest way to explain why a borrowed feature will or will not transfer to your audience.

| Motivation | Mobile mechanics that serve it | Mechanics that alienate it |
|---|---|---|
| Destruction | Chain reactions, destructible boards, big-bomb boosters | Slow, careful, low-feedback play |
| Excitement | Time pressure, escalating waves, near-death recoveries | Long menus, idle waiting |
| Competition | Leagues, PvP, tournaments, leaderboards | Pure co-op, no comparison |
| Community | Teams, chat, gifting, co-op events | Forced PvP against friends |
| Challenge | Hard levels, mastery ranks, optional objectives | Pay-to-skip that trivialises difficulty |
| Strategy | Build choices, deck/loadout, planning puzzles | Twitch timers on planning decisions |
| Completion | Collections, albums, 100% markers | Infinite, uncloseable checklists; missing items behind paid randomness |
| Power | Upgrades, levels, gear, numbers going up | Hard resets without carry-over |
| Fantasy | Role, world, characters, cosmetics | Generic UI-first presentation |
| Story | Chapters, characters, cliffhangers | Story locked behind grind |
| Design | Decoration, avatar and base editors, sharing | Fixed visuals; customisation only via paid random boxes |
| Discovery | Hidden combos, secrets, unknown merge results | Everything spoiled in UI; wiki-required play |

### 4.3 Limits
Self-report of gamers who chose to take a motivation survey skews toward engaged core players; casual mobile players are under-represented relative to their share of the market. The full profile instrument and dataset are proprietary — use the labels as vocabulary, and do not claim to have "measured" motivations without your own validated instrument. Motivations describe preferences, not situational needs (a Strategy-motivated player on a crowded train may still want a 60-second relaxer).

---

## 5. Yee's motivation components

Nick Yee's earlier work on MMO players (2006, "Motivations for Play in Online Games", *CyberPsychology & Behavior*) used factor analysis on survey data and found **10 subcomponents grouped under 3 main components**:

| Component | Subcomponents |
|---|---|
| Achievement | Advancement, Mechanics, Competition |
| Social | Socialising, Relationship, Teamwork |
| Immersion | Discovery, Role-playing, Customisation, Escapism |

**Key insight for designers:** the components were relatively independent — a player can score high on Achievement *and* Social. This refuted the idea of mutually exclusive types and is the main reason to prefer dimensional models (Yee, Quantic Foundry) over typologies (Bartle).

**Escapism** deserves special attention: it is the subcomponent most often associated in later research with problematic play when it is avoidance-driven (escaping real-life problems) rather than enrichment-driven. Treat heavy escapism-oriented design (endless sessions, no stopping cues) as a wellbeing risk (see `ethics-and-dark-patterns.md` §9).

**Limits:** MMO-specific, self-report, mid-2000s population. Use for persistent online and social designs; prefer Quantic Foundry for broad audience work.

---

## 6. Lazzaro's four keys to emotion

### 6.1 The model
Nicole Lazzaro (XEODesign; "Why We Play Games: Four Keys to More Emotion Without Story", 2004) observed players and their facial expressions and grouped game emotions into four "keys":

| Key | Core emotion(s) | Produced by | Mobile example pattern |
|---|---|---|---|
| **Hard Fun** | Frustration → **fiero** (triumph over adversity) | Goals, obstacles, strategy, mastery | Beating a hard level after several attempts |
| **Easy Fun** | Curiosity, wonder, surprise | Exploration, ambiguity, novelty, role play | Merging two items to see what appears |
| **Serious Fun** (later called *Altered States*) | Relaxation, excitement, relief from boredom, a sense of value | Rhythm, repetition, collection, real-world benefit | A calm sorting game before sleep |
| **People Fun** | Amusement, schadenfreude, *naches* (pride in someone you helped) | Cooperation, competition, communication | Team events; sending a gift that unblocks a friend |

### 6.2 Using it in design decisions
- **Emotion map per loop.** For each loop step in `contract.loops[].steps`, name the intended emotion and its key. A loop where every step is Hard Fun exhausts casual players; a loop with no Hard Fun lacks peaks.
- **Balance the keys by segment.** Casual relaxers: Easy + Serious with a light Hard spike. Midcore competitors: Hard + People. Hybrid-casual: Easy entry, Hard spikes, Serious collection meta.
- **Fiero requires real frustration.** Removing all difficulty removes fiero. The design task is to keep frustration *short, attributable and recoverable* (see `emotion-and-cognition.md` §6).
- **Curiosity requires withheld information.** Do not reveal every merge result or reward in the UI if Discovery is a target motivation.

### 6.3 Limits
Observation-based, qualitative, and published as industry research rather than peer-reviewed theory. It names emotions and their sources well but gives no intensity, timing or dosage guidance; combine with interest curves and tension–release (`emotion-and-cognition.md`).

---

## 7. Fogg behaviour model (B = MAP)

### 7.1 The model
BJ Fogg (Stanford Behavior Design Lab; "A Behavior Model for Persuasive Design", 2009; *Tiny Habits*, 2019) proposes that a behaviour happens when **Motivation, Ability and a Prompt** converge at the same moment. Motivation and ability trade off along an "action line": a very easy action needs little motivation; a hard one needs a lot. Without a prompt, nothing happens regardless of motivation and ability. (The 2009 paper called prompts "triggers".)

**Ability factors** (Fogg's "simplicity" factors, paraphrased): time, money, physical effort, mental effort ("brain cycles"), social acceptability, and routine (how far it departs from what the person already does). Ability is limited by the *scarcest* factor for that person at that moment.

**Prompt types:** a *facilitator* (high motivation, low ability → make it easier), a *spark* (high ability, low motivation → give a reason), a *signal* (both high → just remind).

### 7.2 Using it to diagnose "players don't do X"

| Symptom | Diagnostic question | If yes, fix with |
|---|---|---|
| Players never see the feature | Is there a prompt at a moment they are able to act? | Contextual prompt at a natural break (results screen, not mid-level) |
| Players see it, tap away | Is ability low (too many steps, confusing, costs money or time now)? | Remove steps, pre-fill, defer cost, one-tap entry |
| Players can do it easily but don't care | Is motivation low? | Show the payoff concretely; tie to a primary motivation; better reward fit |
| Players start then abandon | Ability dropped mid-flow (new screen, unexpected cost, long load)? | Funnel each step in telemetry; remove the cliff |

**Procedure.**
1. Name the target behaviour precisely ("joins a team within the first 3 sessions"), not vaguely ("engages socially").
2. Instrument the funnel: prompt shown → prompt tapped → step 1 → … → behaviour completed (event names in `event-taxonomy.json`, category `ux` or `social`).
3. Locate the largest drop and classify it M, A or P.
4. Fix the cheapest factor first: prompts and ability are usually cheaper than motivation.
5. Re-test; one change per test (`ab_test.py`).

### 7.3 Ethical use
Fogg's model is neutral. The studio uses it to help players do what *they* want to do (finish the tutorial, find friends, use accessibility settings) and to remove friction from *quitting, cancelling and controlling spending*. We never raise ability for a purchase while lowering ability to understand its cost (hidden prices, one-tap premium spend without confirmation). See red lines in `ethics-and-dark-patterns.md` §6.

### 7.4 Limits
Descriptive rather than predictive — it does not quantify motivation or ability, and "motivation" is a black box that other models (SDT, Quantic Foundry) must fill. Best for single, discrete behaviours; weaker for long-term engagement.

---

## 8. Hook model and the manipulation matrix

### 8.1 The model
Nir Eyal (*Hooked*, 2014) describes habit-forming products as a four-step cycle:

1. **Trigger** — external (notification, icon badge) then, ideally, internal (an emotion or routine such as boredom or a commute).
2. **Action** — the simplest behaviour done in anticipation of reward (borrowing Fogg's model).
3. **Variable reward** — of three kinds: *tribe* (social validation), *hunt* (resources, information), *self* (mastery, completion).
4. **Investment** — the user puts something in (data, content, effort, reputation) that improves the next cycle and loads the next trigger.

Mapped to a mobile game: notification "Your crops are ready" (external trigger) → open and harvest (action) → random rare crop plus a friend's like (variable hunt + tribe reward) → plant again and decorate (investment, loads the next timer trigger).

### 8.2 The manipulation matrix (use this every time)
Eyal proposes two questions for anyone building habit loops: (1) **Would the maker use it themselves?** (2) **Does it materially improve the user's life?** Both yes: *facilitator*. Improves life but maker would not use it: *peddler*. Maker uses it but it does not improve life: *entertainer* (acceptable for games, with care). Neither: *dealer* — do not build.

Games are mostly "entertainers" by this test, which raises the bar: entertainment that players *endorse on reflection* is legitimate; entertainment that players report regretting is not. Pair the matrix with the studio's **reflective-endorsement test**: would players, thinking calmly the next day, be glad this loop exists and glad of the time and money they put into it?

### 8.3 Using it in design decisions
- Design the **internal trigger first**: which situation and feeling does the game resolve (a 3-minute wait, wanting to feel clever, wanting calm)? This becomes the job-to-be-done (`player-research-methods.md` §9).
- Prefer **self** rewards (mastery, completion) and **tribe** rewards with positive valence (thanks, help) over **hunt** rewards with high variance.
- **Investment** is the most ethical lever: decorated bases, built decks and mastered skills give players something genuinely theirs. Investment that only functions as a hostage (lose it if you stop) is a dark pattern (see §4.3 in `ethics-and-dark-patterns.md`).
- Notification triggers: opt-in, capped, timed to when the player can act, and each one must carry value to the player (crops ready, friend needs help) rather than pressure ("You are falling behind!").

### 8.4 Limits
A popular-business framework, not an empirical theory; it describes how habits *can* be built, not whether they *should* be. It is silent on wellbeing; that is what SDT and the ethics file are for.

---

## 9. Flow, GameFlow and player-driven flow

### 9.1 The model
Mihaly Csikszentmihalyi (*Flow: The Psychology of Optimal Experience*, 1990) described flow as deep, enjoyable absorption in an activity. Commonly listed conditions and characteristics (paraphrased): a balance between challenge and skill; clear goals; immediate, unambiguous feedback; concentration on the task; a sense of control; merging of action and awareness; loss of self-consciousness; altered sense of time; and the activity becoming rewarding in itself (autotelic).

Sweetser and Wyeth (2005, "GameFlow", *Computers in Entertainment*) translated this into eight game-evaluation elements: concentration, challenge, player skills, control, clear goals, feedback, immersion and social interaction — each with design criteria. Jenova Chen (2007, "Flow in Games", *Communications of the ACM*) argued that because players have different flow zones, the game should let players **steer difficulty themselves** through choices embedded in play rather than only adjusting silently.

### 9.2 Using it in design decisions
- **Flow channel check:** plot intended challenge vs expected skill over the first 30 levels. Challenge should oscillate inside a band that widens as skill grows (sawtooth), not climb in a straight line. Generate targets with `difficulty_curve.py generate` and verify with bots and telemetry (`difficulty_curve.py analyze`).
- **Feedback latency:** every input acknowledged within one frame visually and within roughly 100 ms in audio/haptics feel (see `game-feel`); unclear feedback breaks flow faster than difficulty does.
- **Goal clarity:** at any moment the player can answer "what am I trying to do right now?" — the HUD shows the current goal, not everything.
- **Player-driven difficulty:** optional objectives, risk/reward routes, hard-mode toggles. Use invisible dynamic difficulty only as a safety net and never in competitive modes; never make help depend on spending.
- **Interruptions:** phones interrupt; protect flow by making resumption instant and by never placing interstitials, rating prompts or offers inside a flow segment.

### 9.3 Limits
Flow is not the only good experience. Relaxed, social and narrative play often deliberately sit outside flow; idle and decoration games succeed with almost no challenge. Flow is also hard to measure in short mobile sessions; self-report scales are long and disruptive. Use flow as a diagnostic for skill-based segments, not as a universal target.

---

## 10. Achievement goals and social comparison

### 10.1 Achievement goal theory
Research on achievement goals (for example Andrew Elliot's work on approach and avoidance goals, from the late 1990s) distinguishes **mastery goals** (improve relative to my past self or the task) from **performance goals** (do better than others), each in an **approach** (seek success) or **avoidance** (avoid failure) form. Broadly, mastery-approach goals are associated with persistence and enjoyment; performance-avoidance goals with anxiety and disengagement.

**Design implications**
- Default to **mastery framing**: personal bests, improvement graphs, "you beat your record by 12%".
- Performance framing (ranks, leagues) suits Competition-motivated players; give everyone else an opt-out or a private mode.
- Avoid designs that convert play into **performance avoidance** — "don't get relegated" pressure for players who never chose competition.

### 10.2 Social comparison
Leon Festinger's social comparison theory (1954) holds that people evaluate themselves by comparing with others. **Upward comparison** (to someone better) can inspire if the gap feels closable and deflate if it does not; **downward comparison** comforts but teaches little.

**Leaderboard design rules derived from it**
| Rule | Why |
|---|---|
| Show players their neighbourhood (ranks ±5) or a small bracket (e.g. 20–50 players), not the global top 100 | Closable upward gaps motivate; huge gaps deflate |
| Bracket by skill or activity, not just by sign-up date | Mismatched brackets turn comparison into humiliation |
| Reset regularly (weekly) and show personal improvement too | Gives low-ranked players a fresh start |
| Friends leaderboards above global ones | Relatedness plus comparable peers |
| Never show bots or fake players as real people | Fake social comparison is deceptive (red line) |

---

## 11. Mobile player segments (studio working model)

This is the studio's **working segmentation** for mobile concepts and personas. It is not an industry standard; it combines Quantic Foundry motivations with the situational facts of phone play (where, when, how long, with what attention). Commercial segmentations exist (for example Newzoo publishes a gamer segmentation with several personas); use them for market sizing, use this table for design decisions, and validate both with your own research.

Players move between segments by **context** (morning commute vs Sunday afternoon). Design the primary segment's core experience and let others layer in.

| Segment | Situation | Top motivations (QF) | Session shape | What they need | What drives them away | Telemetry signature |
|---|---|---|---|---|---|---|
| **Time-filler** | Queues, commutes, ad breaks | Excitement, Challenge (light) | 1–4 min, many per day | Instant start, finish within the wait, no penalty for leaving | Long loads, unskippable FTUE, mandatory sessions | Many short sessions; high resume rate; low feature depth |
| **Unwinder** | Evening, in bed, after work | Fantasy, Design, Completion | 10–30 min, 1–2 per day | Calm, low stakes, no timers, satisfying routine | Time pressure, PvP, loud offers | Long sessions late in the day; low fail tolerance |
| **Brain-trainer** | Breaks, deliberate "me time" | Strategy, Challenge | 5–15 min | Clean puzzles, clear rules, fair difficulty, sense of getting smarter | Random failure, paywalled difficulty | High retries per level; sensitive to difficulty spikes |
| **Collector / completer** | Any; returns daily | Completion, Power | Daily check-ins plus bursts | Visible sets, progress bars, closure | Missing pieces only via paid randomness; uncloseable lists | High collection-screen visits; drop-off when sets stall |
| **Builder / decorator** | Relaxed sessions | Design, Fantasy | 10–20 min | Expression, sharing, steady unlocks | Forced combat to earn decor; layout resets | Time in edit mode; share/visit events |
| **Competitor** | Focused, often evenings | Competition, Challenge, Strategy | 5–20 min, bursty around events | Fair matchmaking, ranking, skill expression | Pay-to-win, bad matchmaking, cheaters | League participation; churn after losing streaks or demotion |
| **Team player** | Daily, social windows | Community, Competition | Regular, coordinated | Belonging, recognition, low-pressure contribution | Obligation guilt, kicked for inactivity, toxic chat | Team join, gifts, chat; retention lift vs solo |
| **Story-seeker** | Commutes, evenings | Story, Fantasy | 5–20 min | Chapters, characters, cliffhangers at session end | Story gated by grind; skip-only presentation | Story-beat completion; skip rate |
| **Optimiser** | Any; reads wikis | Strategy, Power, Completion | Long and frequent | Transparent numbers, deep systems, efficiency | Hidden odds, opaque formulas, power creep | High menu time; spreadsheet-style behaviour; early meta solving |
| **Spectacle-seeker** | Short, high-arousal windows | Destruction, Excitement | 2–8 min | Big feedback, chain reactions, juice | Slow pacing, low feedback | Combo/booster usage; high early D1, steeper decay |

**Spending behaviour is not a segment identity.** Payer tiers (non-payer, low, mid, high spender) are behaviours that cut across all segments. The studio does not use "whale/dolphin/minnow" language in design documents because it frames people as prey; use "payer tier" and spend bands. High-spend players are also where problematic spending concentrates — they get *more* protection, not more pressure (`ethics-and-dark-patterns.md` §8).

**Economy-model mapping.** Each segment becomes an `archetypes[]` entry in `economy-model.schema.json` with `share`, `sessions_per_day`, `session_minutes`, `skill`, `spend_propensity` and `ad_accept_rate`. Example starting points to *replace with soft-launch data*:

| Archetype id | share | sessions/day | minutes | skill | spend_propensity | ad_accept_rate |
|---|---|---|---|---|---|---|
| time_filler | 0.35 | 5 | 2.5 | 0.4 | 0.02 | 0.35 |
| unwinder | 0.25 | 1.5 | 18 | 0.5 | 0.05 | 0.25 |
| competitor | 0.10 | 3 | 10 | 0.8 | 0.08 | 0.20 |
| collector | 0.20 | 3 | 8 | 0.55 | 0.07 | 0.30 |
| optimiser | 0.10 | 4 | 15 | 0.85 | 0.06 | 0.15 |

These numbers are illustrative modelling inputs, not market benchmarks.

---

## 12. Combining models: the motivation pass

Run this pass at concept stage and again after the first human playtest. Output goes into the contract and a short motivation note in `.gamestudio/reports/`.

1. **Situation and job.** Write the primary segment's situation and job-to-be-done in one sentence (§11; `player-research-methods.md` §9).
2. **Motivations.** Pick 3–4 Quantic Foundry motivations; write them to `contract.meta.target_audience.motivations`.
3. **Feature triage.** Score every planned feature 0–2 against the primary motivations; challenge every 0.
4. **Emotion map.** For the core loop and each meta loop, name the intended emotion per step (Lazzaro key). Check at least one Hard Fun peak per session for challenge-seeking segments and at least one Easy or Serious Fun beat for relaxers.
5. **Need audit.** Score each feature for competence, autonomy, relatedness satisfaction and frustration (§2.3). Fix any −2.
6. **Reward framing.** Rewrite every reward and quest message to be informational, not controlling; move extrinsic structures rightward on the OIT continuum.
7. **Behaviour funnels.** For the three behaviours that matter most (finish FTUE, return on day 2, adopt the meta), write the M/A/P assumptions and the events that will test them.
8. **Habit loop honesty.** Draw the Hook cycle; run the manipulation matrix and the reflective-endorsement test. Remove any loop that only works through pressure.
9. **Flow check.** For skill segments: plot the challenge band, feedback latency, goal clarity and player-driven difficulty options.
10. **Comparison framing.** If any ranking exists: brackets, neighbourhood views, opt-outs.
11. **Record.** Update `contract.json` (motivations, `loops`, `monetization.ethics`), and write the open hypotheses into the playtest plan.

---

## 13. Worked example: Pebble Keep

The sample contract (`${CLAUDE_PLUGIN_ROOT}/scripts/schemas/examples/example.design-contract.json`) is a merge tower-defence game with a renovation meta, portrait one-thumb, ~4-minute sessions, ages 13+, motivations *strategy, completion, design, challenge*.

**Step 1 — situation/job.** "When I have a few minutes on the commute, I want a short tactical puzzle where my planning visibly pays off, and to make my keep a bit nicer each day."

**Step 2–3 — triage.**
| Feature | Strategy | Completion | Design | Challenge | Score | Verdict |
|---|---|---|---|---|---|---|
| Merge golems on the board | 2 | 0 | 0 | 2 | 2 | Core |
| Keep restoration with stars | 0 | 2 | 2 | 0 | 2 | Meta, keep |
| Golem family collection | 1 | 2 | 0 | 0 | 2 | Keep; must be completable without paid randomness |
| Weekly PvP leaderboard (proposed) | 1 | 0 | 0 | 1 | 1 | Weak fit; Competition not primary → opt-in side mode at most |
| Daily login calendar | 0 | 1 | 0 | 0 | 1 | Low value; redesign as "daily garden visit" with decor reward |

**Step 4 — emotion map (core loop).** Spawn (anticipation) → merge (small Easy Fun surprise when a new tier appears) → wave clears (relief) → final wave near the gate (tension) → win (fiero on hard levels, satisfaction on easy ones) → place a star in the keep (Serious Fun: calm completion). Gap found: no curiosity beat after day 3 once all tiers are known → add discoverable golem variants by merge combination (Discovery as a secondary motivation).

**Step 5 — need audit.** Competence +2 (readable waves, fail recap planned). Autonomy +1 (choices on the board; meta choice of which renovation task first: +1 more). Relatedness 0 — acceptable for this segment; a light "visit a friend's keep" layer could add +1 later. Frustration risk: revive offer at failure. Mitigation already in the contract ethics list: fixed revive price shown before the choice, no escalation within a run.

**Step 6 — framing.** Change "Complete 3 levels today to earn 50 coins" to "Try the Moss Golem in 3 runs" (exploration framing, identified regulation).

**Step 7 — funnel hypotheses.** FTUE completion ≥ 90% (ability risk: drag-merge gesture discovery; prompt = ghost-hand animation). D2 return driven by keep restoration (motivation risk: is the keep visible enough at session end?). Meta adoption: first renovation task within session 1 (prompt on results screen).

**Step 8 — hook honesty.** External trigger: optional "your garden has new sprouts" notification, max 1 per day, only if opted in. Investment: the keep. Reflective endorsement: likely positive; the risk is the piggy-bank offer — verify it shows exact contents and price and has no countdown.

---

## 14. Limits of each model

| Model | Strong at | Weak at / misuse | Evidence base |
|---|---|---|---|
| SDT / PENS | Explaining sustained, healthy engagement; reward framing | Choosing specific mechanics; dosage; PENS licensing | Large academic literature; game studies mostly self-report, modest effects |
| Bartle | Population dynamics in social worlds; toxicity discussions | Individual typing; casual or single-player games | Observational, MUD-era, not factor-analysed |
| Quantic Foundry | Audience definition and feature triage; shared vocabulary | Situational needs; casual under-representation; proprietary instrument | Large self-selected survey samples, factor analysis |
| Yee | Showing motivations are dimensions, not types; online games | Non-MMO genres; dated population | Factor analysis of MMO survey data |
| Lazzaro | Naming target emotions per mechanic | Intensity, timing, measurement | Industry observational research |
| Fogg | Diagnosing why a discrete behaviour fails | Long-term engagement; quantification | Practitioner model; limited formal testing |
| Hook | Describing habit loops and investment | Ethics (silent); causal evidence | Business book; illustrative cases |
| Flow / GameFlow | Moment-to-moment challenge, feedback, goals | Relaxed/social play; measurement in short sessions | Strong general literature; game-specific evidence mixed |
| Achievement goals / social comparison | Leaderboards, leagues, feedback framing | Predicting a specific player's response | Large educational and social-psychology literature |
| Mobile segments (studio) | Situational design and personas | Not externally validated; must be tested | Studio synthesis — validate with your own data |

**General warnings**
- Typologies invite stereotyping; dimensions and situations are more accurate.
- Self-reported motivations predict stated preference better than actual behaviour; triangulate with telemetry (`player-research-methods.md` §8).
- Cross-cultural differences exist in how motivations are expressed (for example comfort with competition, gifting norms); localise social design, not just text.
- Models describe averages. The studio designs for distributions: check what happens to the bottom quartile of skill, the most anxious players and the youngest permitted age.

---

## 15. Sources

All summaries above are paraphrased; consult originals for exact definitions.

- Bartle, R. (1996). "Hearts, Clubs, Diamonds, Spades: Players Who Suit MUDs." *Journal of MUD Research*. — and Bartle, R. (2003). *Designing Virtual Worlds*. New Riders.
- Chen, J. (2007). "Flow in Games (and Everything Else)." *Communications of the ACM*, 50(4).
- Csikszentmihalyi, M. (1990). *Flow: The Psychology of Optimal Experience*. Harper & Row.
- Deci, E. L., Koestner, R., & Ryan, R. M. (1999). "A meta-analytic review of experiments examining the effects of extrinsic rewards on intrinsic motivation." *Psychological Bulletin*, 125(6).
- Elliot, A. J. (1999). "Approach and avoidance motivation and achievement goals." *Educational Psychologist*, 34(3).
- Eyal, N. (2014). *Hooked: How to Build Habit-Forming Products*. Portfolio.
- Festinger, L. (1954). "A theory of social comparison processes." *Human Relations*, 7(2).
- Fogg, B. J. (2009). "A Behavior Model for Persuasive Design." *Persuasive '09*. — and Fogg, B. J. (2019). *Tiny Habits*. Houghton Mifflin Harcourt.
- Lazzaro, N. (2004). "Why We Play Games: Four Keys to More Emotion Without Story." XEODesign white paper.
- Quantic Foundry. Gamer Motivation Model and blog reports — https://quanticfoundry.com/
- Rigby, S., & Ryan, R. M. (2011). *Glued to Games*. Praeger.
- Ryan, R. M., Rigby, C. S., & Przybylski, A. (2006). "The Motivational Pull of Video Games: A Self-Determination Theory Approach." *Motivation and Emotion*, 30(4).
- Ryan, R. M., & Deci, E. L. (2017). *Self-Determination Theory*. Guilford Press.
- Sweetser, P., & Wyeth, P. (2005). "GameFlow: A Model for Evaluating Player Enjoyment in Games." *Computers in Entertainment*, 3(3).
- Vansteenkiste, M., & Ryan, R. M. (2013). "On psychological growth and vulnerability: Basic psychological need satisfaction and need frustration as a unifying principle." *Journal of Psychotherapy Integration*, 23(3).
- Yee, N. (2006). "Motivations for Play in Online Games." *CyberPsychology & Behavior*, 9(6).
