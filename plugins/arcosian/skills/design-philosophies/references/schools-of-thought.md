# Schools of Thought

The recurring debates of game design and production, each laid out as **the question**, **the positions** (with who holds them), **the evidence** (what is actually known, with uncertainty flagged), **when each position is right**, and **the house position** that the `arcosian` plugin defaults to. Most of these debates are not won by one side: they are settled per project by audience, platform, team and business model. The value of this file is in the "when each is right" tables, which turn a philosophical argument into a project decision. Market data and regulatory facts that change quickly are collected in the labelled volatile section at the end.

## Contents

1. How to use this file
2. Ludology vs narratology
3. Systems vs content
4. Emergent vs authored
5. Product vs service
6. Premium vs free-to-play, and F2P ethics
7. Data-informed vs intuition-led
8. Juice it or lose it
9. Minimum viable game
10. The hypercasual testing doctrine and its decline
11. The hybrid-casual synthesis
12. Cozy games
13. Roguelite doctrine
14. Respect the player's time
15. Accessibility-first
16. Ethical design movements
17. Anti-crunch production
18. AI in the pipeline vs AI in the product
19. Fast-follow vs originality
20. Quick decision matrix
21. Volatile facts (as of Oct 2026 — verify before relying)

---

## 1. How to use this file

- When a design argument repeats, find its school here, read "when each is right", and write the project's choice into the contract (pillars, `scope.wont`, `monetization.ethics`, `kill_criteria`). A choice written down stops the argument from recurring.
- When you deviate from the house position, record why in the contract's `risks` or in a design-review report under `.gamestudio/reports/`.
- Numbers marked *illustrative* are worked examples to show the arithmetic; replace them with project data.

---

## 2. Ludology vs narratology

**The question.** Are games fundamentally systems of rules and play (ludology) or a medium for stories (narratology)? Practically: should design start from mechanics or from narrative?

**Positions.**

| Position | Associated with | Core argument |
|---|---|---|
| Ludology | Gonzalo Frasca (popularized the term in game studies around 1999), Espen Aarseth (*Cybertext*, 1997), Markku Eskelinen ("The Gaming Situation", 2001) | Games are configurative systems; applying literary and film theory misses what is unique about them |
| Narratology | Janet Murray (*Hamlet on the Holodeck*, 1997) | Games are a new medium for interactive storytelling and procedural authorship |
| Synthesis | Jesper Juul (*Half-Real*, 2005): games combine real rules with fictional worlds; Henry Jenkins ("Game Design as Narrative Architecture", 2004): environmental and emergent storytelling | Rules and fiction work together; the question is how, not which |

**Evidence.** Within game studies the debate is now widely seen as overstated; Frasca himself argued in a 2003 paper that ludologists also value stories and that the "debate" was partly a misunderstanding. The design-practice legacy is useful vocabulary: embedded vs emergent narrative (Salen and Zimmerman), environmental storytelling (Jenkins), and ludonarrative dissonance (Clint Hocking, 2007), the conflict between what a story claims and what the mechanics reward.

**When each is right.**

| Situation | Lead with | Why |
|---|---|---|
| Core loop repeated thousands of times (puzzle, arcade, competitive) | Rules | Story cannot survive repetition; mechanics carry the experience |
| Experience consumed once (narrative adventure, visual novel, premium story game) | Narrative | Mechanics serve beats; replay is not the goal |
| Simple core with a progression wrapper (decoration-story match-3) | Rules core, narrative meta | Narrative supplies motivation and widens the audience; the core stays pure |
| Systemic sandbox | Rules, with emergent narrative tools | Players author stories from events (see section 4) |

**House position.** For mobile F2P, rules first: the core loop must be fun with placeholder fiction. Narrative is a wrapper, a motivation layer and a tone. Every design review checks for ludonarrative dissonance: write what the story claims and what the economy rewards side by side (`narrative-design`).

---

## 3. Systems vs content

**The question.** Should the game's longevity come from rules that generate variety (systems) or from hand-made units such as levels, quests and stories (content)?

**Positions.**

| Position | Exemplars | Strengths | Costs |
|---|---|---|---|
| Systems-first | Mojang, Klei, RimWorld, *Dwarf Fortress*, roguelites | Replayability, long tail, emergent stories, low marginal content cost | High upfront design and testing cost; balance is hard; experience less controllable |
| Content-first | King's level catalogue, Nintendo levels, narrative games | Predictable quality, precise teaching and pacing, marketing beats | Cost scales linearly with hours of play; players consume faster than teams produce |
| Hybrid | *Spelunky* (templates plus generation), King-style bot-verified, designer-tuned level pipelines | Variety with guardrails | Needs a generator *and* a verifier |

**The content treadmill (arithmetic).**

```
content_runway_days = units_in_stock / units_consumed_per_day_by_p90_players
weekly_production_needed = 7 × units_consumed_per_day_by_p90_players × share_of_players_at_frontier
```

*Illustrative:* engaged players clear 12 levels a day and 20% of the active base sits at the content frontier. Those players need 7 × 12 = 84 new levels a week to never run out. No small team hand-makes 84 tuned levels a week, which is why content-led mobile games use procedural generation with verification, difficulty spikes, lives, and events that reuse content. Gating consumption is legitimate pacing only when it does not punish the player (see section 14).

**When each is right.**

| Choose | When |
|---|---|
| Systems | Replayability is the product; simulators and bots can test the rules; the team can support a long tail |
| Content | Emotional precision, teaching sequences, puzzle intent or a narrative arc matter most |
| Hybrid | You need volume *and* quality: generate, verify with a solver or bot, curate, then tune |

**House position.** Systems for the core loop, content for the arcs, and procedural generation with verification for volume (`procedural-generation`, `level-design`). Agents reduce the cost of making content, so the bottleneck moves to verification: every generated unit passes `puzzle_solver.py` or `match3_sim.py` (or an engine bot run) and a `difficulty_target` before it ships.

---

## 4. Emergent vs authored

**The question.** Should the experience (moment to moment and as a story) be designed precisely, or arise from systems interacting?

**Positions.**
- *Authored:* Playdead, Lucas Pope, Jonathan Blow, linear narrative action games. Control over pacing, guaranteed beats, precise teaching.
- *Emergent:* Warren Spector's immersive sims, Tynan Sylvester's *RimWorld*, *Crusader Kings*, *Minecraft*. Player-authored stories, replay, word of mouth from retold anecdotes.
- *Directed emergence (the middle):* a system that shapes emergent events toward a desired arc. Examples: the *Left 4 Dead* AI Director (pacing by player stress), *RimWorld*'s storytellers (event scheduling), *Hades*' state-aware dialogue (authored lines selected by systemic state).

**Evidence.** Mostly qualitative: emergent games generate large volumes of player-told stories, and authored games score well on critical consistency. There is no clean data showing one retains better in general.

**When each is right.**

| Phase or content | Default | Reason |
|---|---|---|
| First 10 minutes (FTUE) | Authored | Teaching needs a guaranteed sequence; the aha moment must land on schedule |
| Mid-game core loops | Directed emergence | Variety with pacing control |
| Long tail and endgame | Emergent | Replay and community stories |
| Narrative reveals and set pieces | Authored | Timing is the experience |

**House position.** Author the FTUE and key beats (`ftue.steps`); direct the emergence of the core loop with a pacing controller (`progression-difficulty`); let the long tail be systemic.

---

## 5. Product vs service

**The question.** Ship a finished product (premium, maybe expansions or a sequel) or run a game as a live service for years?

**Positions.**
- *Product:* Playdead, Team Cherry, LocalThunk. A finished, coherent work; small teams; no ongoing operational cost; revenue front-loaded.
- *Service:* Supercell, Riot, HoYoverse. A repeatable loop plus continuous content, events and social systems; revenue spread over years; ongoing cost.
- On mobile, F2P makes service the default, but plenty of premium and subscription games (Apple Arcade, Netflix Games) are products.

**Evidence.** Live-service outcomes are highly skewed: a few titles earn most of the revenue, and high-profile failures are common (for example, Sony's *Concord* was shut down within weeks of its 2024 launch; many mobile games are sunset after soft launch). Recent mobile market growth has come from retaining and monetizing existing players through live ops rather than from new downloads (see volatile facts).

**Break-even check before committing to a service (illustrative).**

```
monthly_liveops_cost = content + servers + community + analytics + retention marketing
break_even_DAU = monthly_liveops_cost / (ARPDAU × 30)
```

*Illustrative:* $40,000 per month of live-ops cost at an ARPDAU of $0.08 gives 40,000 / 2.4 ≈ 16,700 DAU just to break even, before any acquisition spend. If the soft launch cannot plausibly reach that DAU at the measured retention, ship as a product.

**When each is right.**

| Choose | When |
|---|---|
| Product | Finite experience; small team; premium-friendly channel (Apple Arcade, Steam, Switch); appeal comes from completion |
| Service | Repeatable core loop; social or competitive layer; affordable content cadence; monetization depth; retention data proves demand |

**House position.** Earn the right to be a service. Ship a complete game first with service hooks in place (remote config, event framework, analytics taxonomy), and switch on a live-ops cadence only after D1/D7 targets in `analytics.kpi_targets` are met in soft launch (`liveops`, `operate`).

---

## 6. Premium vs free-to-play, and F2P ethics

**The question.** Charge up front, or give the game away and monetize inside it? And if F2P, where is the ethical line?

**Positions.**

| Position | Argument | Associated voices |
|---|---|---|
| Pro-F2P | Access for everyone; players pay what they value; most never pay; supports long-term development | Mainstream mobile industry practice |
| F2P critics | Revenue concentrates in a small share of payers, so design can drift toward extracting from heavy spenders, some of whom may be vulnerable; manipulative techniques are common | Ramin Shokrizade ("The Top F2P Monetization Tricks", 2013, describing "coercive monetization"); José Zagal, Staffan Björk and Chris Lewis ("Dark Patterns in the Design of Games", 2013) |
| Premium | One price, no conflict between fun and revenue | Indie premium developers; Apple Arcade and Netflix Games as subscription variants |

**Evidence.** Regulators have acted on the most chance-based mechanics: Belgium treated paid loot boxes as gambling in 2018; the ESRB and PEGI added "In-Game Purchases (Includes Random Items)" labelling in 2020; Apple and Google require odds disclosure for randomized paid items; more recent rules in Brazil and Australia are listed in volatile facts. Premium on mobile faces strong user expectation of free downloads; Nintendo's *Super Mario Run* one-time unlock was widely reported to convert below expectations, while premium successes such as *Monument Valley* show it can work with distinct quality and press.

**Ethical F2P checklist (the house minimum).**
1. Prices shown in real money next to any premium-currency price; no bundle maths designed to confuse.
2. Published odds and pity for any randomized paid item; no paid randomness for minors where restricted.
3. No pay-to-win against other humans in competitive modes; PvE power sales capped and disclosed.
4. Ads never interrupt active play; rewarded ads are opt-in; interstitial caps respected (`monetization.ads.interstitial.min_interval_sec`, `first_after_sec`).
5. No fake urgency (timers that reset, false scarcity); real deadlines only.
6. No streaks that wipe large progress on one missed day without a recovery path.
7. Spending awareness: purchase history visible; no targeting of post-loss offers at minors.
8. Easy cancellation for subscriptions; no hidden auto-renew.

**When each is right.**

| Choose | When |
|---|---|
| Premium | Finite content; enthusiast audience; PC, console or subscription channels; no live team |
| F2P IAP | Mass reach; long loops; content cadence; audience in IAP-heavy markets |
| Ads + IAP hybrid | Casual and hybrid-casual audiences, including markets where ads dominate revenue |
| Subscription | Content library or platform deals (Apple Arcade) |

**House position.** F2P is allowed; manipulation is not. The checklist above goes into `monetization.ethics`, and the `monetization-designer` and `compliance-officer` both review it (`monetization`, `legal-ethics`).

---

## 7. Data-informed vs intuition-led

**The question.** Should decisions follow metrics, or the designer's taste?

**Positions.**
- *Data-driven:* the Zynga-era approach and large-scale A/B testing; metrics decide.
- *Intuition-led:* auteurs such as Miyamoto, Miyazaki and many indie developers; taste decides, and players cannot ask for what they have not seen.
- *Data-informed (synthesis):* write a hypothesis from intuition and theory, predict the direction and size of the effect, then use data to confirm or refute.

**Evidence and pitfalls.** Pure metric optimization finds local maxima and can drift into exploitation (Zynga). Common analytic errors: peeking at A/B tests before the planned sample (use sequential designs), novelty effects, optimizing D1 at the expense of D30 or trust, Simpson's paradox across segments, and running tests too small to detect anything.

**Sample-size reality check (illustrative).** Detecting a 2-percentage-point lift on a 40% D1 retention baseline at α = 0.05 and 80% power needs roughly 9,500 users per arm by the standard two-proportion formula. A soft launch with 3,000 installs a week cannot run that test meaningfully. Compute yours with `ab_test.py size --baseline 0.40 --mde 0.02` (check the script's MDE convention) and `ab_test.py sequential` for planned interim looks.

**When each is right.**

| Situation | Lean |
|---|---|
| New aesthetic, new emotion, early prototype with no data | Intuition and theory, tested by playtest |
| Tuning known levers (prices, difficulty, ad frequency) with a large audience | Data |
| Ethics, brand and long-term trust | Principle; data does not overrule doctrine 8 |
| Small audience | Qualitative playtests and large effects only |

**House position.** Doctrine 4: hypotheses first, written into the feature or test plan with expected direction and size; telemetry confirms (`player-analytics`, `data-analyst`).

---

## 8. Juice it or lose it

**The question.** How much audiovisual feedback ("juice") should interactions have, and can juice make a game good?

**Positions.**
- *Juice advocates:* Martin Jonasson and Petri Purho's 2012 talk "Juice it or lose it" rebuilt a plain block-breaker with layer after layer of feedback; Jan Willem Nijman's 2013 talk "The Art of Screenshake" did the same for a shooter; Steve Swink's *Game Feel* (2008) gave the vocabulary (real-time control, simulated space, polish).
- *Qualifiers:* juice cannot rescue a weak core; heavy effects hurt readability in puzzle and strategy games; screen shake and flashing harm players with motion sensitivity or photosensitivity; particles, post-processing and haptics cost frame time, battery and heat on low-end phones. Academic studies of "juicy" design (Kieran Hicks and colleagues) include "Good Game Feel: An Empirically Grounded Framework for Juicy Design" (Hicks, Dickinson, Holopainen and Gerling, DiGRA 2018, built from a survey of 17 developers: [DiGRA library](https://dl.digra.org/index.php/dl/article/view/936)) and "Juicy Game Design: Understanding the Impact of Visual Embellishments on Player Experience" (CHI PLAY 2019, DOI 10.1145/3311350.3347171). The CHI PLAY abstract says the industry and academia both assume juiciness improves player experience while empirical evidence is lacking. Our claim that effects depend on the game and the player rather than a simple "more is better" is a reading of that literature, not a result checked against the papers' findings in this review, so read the papers before citing a specific effect.

**Juice budget by event importance (illustrative starting values; tune by feel).**

| Tier | Example events | Feedback layers | Starting values |
|---|---|---|---|
| 1 Touch | Tap, drag start, button press | Sound tick, scale pulse | Pulse to 1.05× over ~80 ms; sound within one frame |
| 2 Success | Match, merge, hit, coin pickup | Tier 1 + particles + floating number + light haptic | Particle burst under ~0.4 s; number rises and fades |
| 3 Big moment | Combo, level clear, rare drop | Tier 2 + short screen shake or zoom + music sting | Shake a few pixels for ~150 ms; respect reduce-motion |
| 4 Milestone | Boss kill, chapter end, first win | Tier 3 + slow motion or freeze + celebration screen | Hit-stop a few frames; celebration skippable after ~1 s |

**When each is right.** Juice every touched surface in proportion to its importance; use restraint where the player must read a board state (puzzle, tactics); always provide reduce-motion and shake toggles; fit effects inside the frame-time budget for the low tier.

**House position.** Doctrine 7: readability over detail, juice everything the player touches. The `visual` gate checks both: feedback present on touched elements, and the board still readable. Perf cost is checked against `technical.perf_budgets` (`game-feel`, `mobile-performance`).

---

## 9. Minimum viable game

**The question.** How small can the first testable version of a game be? Does the lean-startup minimum viable product apply to an experience good like a game?

**Positions.**
- *Lean approach:* Eric Ries' *The Lean Startup* (2011) applied to games: build the smallest thing that tests a hypothesis. Amy Jo Kim's *Game Thinking* (2018) adapts this for games with an emphasis on early superfans. Soft launch at Supercell and King works as a staged MVP.
- *Critics:* games are hit-driven experience goods; a crude build tests crudeness, not the idea; players judge on feel and polish. Hence "minimum lovable product" and the *vertical slice* (one small piece at near-final quality).
- *Synthesis:* there is no single MVP. There is a minimum viable *question*, and each question has its cheapest valid test.

**Minimum viable question table.**

| Question | Cheapest valid test | Pass signal (set before testing) | Typical cost with agents |
|---|---|---|---|
| Is the verb fun? | Feel prototype: one verb, grey box | Testers keep playing with no goal; human fun sign-off | Hours |
| Is the core loop compelling? | Loop prototype: 5–15 minutes of loop, placeholder art | Players start another loop unprompted; bot runs show no softlocks | A day or two |
| Does the meta hold over weeks? | Economy model plus simulation | `economy_sim.py` meets `targets` (days to complete content, hoard days) | Hours |
| Will people click on it? | Appeal test: key art, short video, store-page copy | Click-through or CPI against a comparable baseline | A day plus ad spend |
| Can we hit quality? | Vertical slice: one level at ship quality | Visual gate passes; human style sign-off | Days |
| Will they stay and pay? | Soft launch | D1, D7, D30 and conversion vs `analytics.kpi_targets` | Weeks |

**House position.** Doctrine 2: find the fun fast, core loop before content, content before polish. Every build states the one question it answers and its pass bar in the feature's `acceptance` list.

---

## 10. The hypercasual testing doctrine and its decline

**The doctrine (peak roughly 2017–2020).** Marketability first: make a short video creative and a minimal build, run cost-per-install tests on social ad networks, and only then test retention and playtime. One verb, instant understanding, 30-second rounds, ad monetization, publish at volume and kill fast. Voodoo, Homa, SayGames, Kwalee and others built publishing machines around it, giving external studios dashboards and SDKs.

**Why it declined.**
1. Apple's App Tracking Transparency (iOS 14.5, 2021) weakened ad targeting and attribution, which hurt both acquisition efficiency and ad revenue per user.
2. Rising acquisition costs and market saturation squeezed ad-only lifetime value below acquisition cost for most titles.
3. Very short retention: games designed to be understood in seconds were often exhausted in days.
4. Publishers shifted to hybrid-casual and fewer, deeper launches (see volatile facts).

**What survived.** Rapid creative testing; marketability checked before heavy production; one-verb clarity in the first seconds; metric dashboards; the habit of killing quickly.

**When CPI-style testing is still right.**

| Use | Right? |
|---|---|
| Comparing appeal of 3–5 concepts or art directions | Yes, as one signal among several |
| Store-page optimization (Apple product page optimization, Google Play store listing experiments) | Yes |
| Deciding a whole project on CPI alone | No: appeal is not retention or monetization |
| Testing with creatives that show gameplay the game does not have | No: misleading and, in some cases, ruled against by ad regulators |

**House position.** Appeal tests feed the `market` score in `concept-tournament`; they are never the only gate. Creatives must show the real game (`marketing-ua`).

---

## 11. The hybrid-casual synthesis

**Definition.** A hypercasual-accessible core (one-thumb, instant understanding, short runs) plus a casual or midcore meta (upgrades, collections, progression), monetized by both rewarded ads and IAP (remove-ads, passes, bundles). Exemplars: Habby's *Archero* and *Survivor.io*; Voodoo's post-pivot portfolio.

**Evidence.** Hybrid-casual was the fastest-growing mobile spending segment in 2025 (volatile facts). It is also the genre family where automated players and simulators work best, which suits an agent-built pipeline.

**Design rules (illustrative defaults).**

| Element | Default | Contract field |
|---|---|---|
| Run length | 1–3 minutes, interruptible | `session_length_target_sec` |
| First meaningful action | Under 5 seconds from launch screen | `ftue.aha_seconds_target` (aha later, action first) |
| Meta unlock | After about 3–5 runs, not at first launch | `ftue.steps` |
| Rewarded ads | Opt-in at value moments (double reward, revive) | `monetization.ads.rewarded` |
| Interstitials | Not in the first sessions; minimum interval enforced | `monetization.ads.interstitial` |
| Remove-ads IAP | Offered early and priced simply | `monetization.iap` |
| Economy | Simulated before build | `economy.model_ref` → `economy_sim.py` |

**Risks.** Meta bloat burying a simple core; aggressive monetization dressed as casual; ads cannibalizing IAP or IAP-only players seeing ads they paid to remove.

**House position.** The default genre family for agent-built games, through `genre-playbooks` and `economy-design`, with doctrine 8 limits on energy and gear-chest monetization.

---

## 12. Cozy games

**The question.** What makes a game "cozy", and is coziness a genre, a tone or a marketing label?

**Positions.**
- *Coziness as design:* a 2017 Project Horseshoe group report on coziness (contributors included Daniel Cook) described it in terms of safety (low threat), abundance (needs met, little scarcity) and softness (gentle sensory input). Exemplars include *Animal Crossing* (whose *New Horizons* became a phenomenon in 2020), *Stardew Valley*, *A Short Hike*, *Unpacking* and *Cozy Grove*; showcases such as Wholesome Direct (from 2020) built a market around the label.
- *Critiques:* "cozy" can mask grind, daily chores and fear of missing out (real-time gating, absence penalties); the label is saturated; coziness does not have to mean zero challenge.

**Coziness checklist.**
1. Failure is cheap or absent; no loss of hard-earned progress.
2. No time pressure inside the core loop.
3. Early abundance: resources are not scarce in the first sessions.
4. Soft visuals and audio; no harsh alarms.
5. Player-paced goals; nothing is missed forever.
6. Gentle social: gifting and visiting, not raiding or ranking.
7. Absence is not punished (or only mildly and recoverably).

**When it is right.** Audiences seeking relaxation and self-expression; strong mobile fit (short sessions, decor monetization). Wrong when the core needs tension to work.

**House position.** If a pillar promises coziness, the contract's `scope.wont` must list the stress mechanics it rules out (loss timers, PvP raids, punishing streaks), and the `critic` checks the economy for hidden grind.

---

## 13. Roguelite doctrine

**Background.** The 2008 "Berlin Interpretation", drafted at the International Roguelike Development Conference, listed high-value features of roguelikes: random environment generation, permadeath, turn-based and grid-based play, non-modal interface, complexity, resource management, hack-and-slash combat, exploration and discovery. *Roguelites* keep procedural runs and permadeath but relax the rest, often adding real-time action and persistent meta-progression (*Rogue Legacy*, 2013; *Hades*).

**Positions.**
- *Skill-pure:* minimal meta-progression; unlocks widen options rather than adding power; difficulty ladders for experts (*Slay the Spire*'s ascension levels).
- *Meta-heavy:* persistent upgrades make each run stronger; accessible to less skilled players; in mobile F2P (*Archero*, *Survivor.io*) the meta is also the monetization surface.
- *Critique of meta-heavy:* it can replace skill with grind, and when power is sold, PvE challenge becomes a paywall.

**Design parameters (illustrative mobile defaults).**

| Parameter | Default | Note |
|---|---|---|
| Run length | 3–15 minutes | Interruptible saves for longer runs |
| Upgrade choices | 3 options per pick | One reroll per run is a common pressure valve |
| Pick frequency | Every 30–90 seconds of play | Keeps decisions dense |
| Meta-power share | Meta bonuses well under half of end-of-run power | Keeps the run decisive (heuristic) |
| Synergy discovery | Each archetype has 2–3 discoverable combos | Track pick rate vs win rate per item |

**When each is right.** Skill-pure for premium and enthusiast audiences; meta-heavy for casual F2P, provided the run stays decisive and purchased power is disclosed and capped.

**House position.** Meta-progression must not make runs trivial. Check with bots: a no-meta bot should still be able to win some runs at the base difficulty, and a max-meta bot should still lose some at the top difficulty (`progression-difficulty`, `balance`).

---

## 14. Respect the player's time

**The question.** Is the player's time something to fill (engagement, retention) or something to honour (efficiency, no padding)?

**Positions.**
- *Respect:* skippable cutscenes, fast restarts, short tutorials, no chores, offline progress, honest session ends.
- *Engagement:* time sinks, daily logins, streaks, energy, battle passes that require regular play; justified as pacing and retention.
- *Synthesis:* time spent should be time the player would choose to spend. Pacing is fine; padding and punishment are not.

**Evidence.** Practitioner sources treat time-to-fun and the first session as the largest D1 lever (volatile facts); complaints about chores and fear of missing out are common in reviews of live games (qualitative).

**Tests to apply to any time-consuming element.**
1. Would the player do this if it gave no reward? If not, can it be shortened or automated?
2. Does skipping it cost anything besides the reward itself?
3. Time to first meaningful decision from cold start (target: seconds, not minutes).
4. Share of session time spent on meaningful decisions versus waiting, loading and confirming (aim for a large majority; measure from playthrough step timings).
5. Can a daily routine be completed in a few minutes?
6. Does missing a day cost a little (fine) or a lot (not fine)?

**House position.** Doctrines 1 and 6: dailies completable in a few minutes; streaks with recovery; skip and fast-forward for anything seen twice; cold start within `technical.perf_budgets.cold_start_sec`; interruption-safe saves.

---

## 15. Accessibility-first

**The question.** Is accessibility a late compliance pass, or a design principle from day one? And does accessibility conflict with intended difficulty?

**Positions.**
- *Accessibility-first:* the Game Accessibility Guidelines (first published 2012, organized into basic, intermediate and advanced tiers), Microsoft's Xbox Accessibility Guidelines (published 2020), the charity AbleGamers, and games such as *The Last of Us Part II* (2020, widely reported to ship with more than 60 accessibility options) show that broad options are feasible and widen the audience. Retrofitting is far more expensive than planning.
- *Difficulty as authorial intent:* the 2019 debate around *Sekiro* and "easy modes" argued that fixed difficulty is part of some games' meaning.
- *Resolution most designers now accept:* separate the intended challenge from incidental barriers. Input, readability, timing windows that only fail certain bodies, colour-only information and missing captions are barriers, not challenge.

**Mobile accessibility checklist (house minimum).**
1. Touch targets at least 44 × 44 pt on iOS (Apple Human Interface Guidelines) and 48 × 48 dp on Android (Material Design guidance).
2. Primary actions in the thumb zone; a one-handed mode where the genre allows it.
3. Never rely on colour alone; test with colour-blindness simulation.
4. Text that scales with system settings, or an in-game size option; sufficient contrast.
5. Captions for voice and important sounds; visual cues for audio-only signals.
6. Toggles for screen shake, flashing, haptics and camera motion; respect the OS reduce-motion setting.
7. Pause anywhere; no input that requires rapid repeated tapping without an alternative.
8. Timing assists (wider windows, slower mode) that do not lock out achievements unless the design truly depends on them.

**House position.** Accessibility is written into `ux.accessibility` at contract time and checked in the `visual` gate rubric (`accessibility-localization`, `mobile-ux`, `ux-designer`).

---

## 16. Ethical design movements

**The question.** Can the industry self-regulate harmful design (manipulative monetization, toxic communities, exploitation of minors), or is regulation needed?

**Movements and instruments.**

| Initiative | What it is | Notes |
|---|---|---|
| Fair Play Alliance | A coalition of game companies working on healthy player communities and disruptive behaviour; became public around GDC 2018 | Published, with the Anti-Defamation League, a framework on disruption and harms in online games (around 2020; verify title and date before citing) |
| Dark patterns research | Zagal, Björk and Lewis, "Dark Patterns in the Design of Games" (2013), classify temporal, monetary and social dark patterns; community catalogues of dark patterns in mobile games exist online | Use as a review checklist source |
| Ratings labels | ESRB and PEGI "In-Game Purchases (Includes Random Items)" descriptors (2020) | Disclosure, not prohibition |
| Platform rules | Apple and Google require disclosure of odds for randomized paid items | Store review enforces |
| Child-focused design codes and privacy law | UK Age Appropriate Design Code (in force 2021); US COPPA (amended rule; see volatile facts); GDPR Article 8 consent ages | Drive age gates and data minimization |
| Loot-box law | Belgium (2018 interpretation as gambling); Brazil and Australia (see volatile facts) | Jurisdiction-specific behaviour required |

**Positions.** Self-regulation advocates point to ratings labels, odds disclosure and industry principles; critics argue the incentive to extract revenue makes voluntary restraint unreliable, and regulators are increasingly acting.

**House position.** Do not wait for the law. Doctrine 8 rules are enforced at design time (`monetization.ethics`), checked by `compliance-officer` and by `compliance_preflight.py --project DIR --platform all`, with jurisdiction-specific behaviour driven by `config.storefronts` (`legal-ethics`).

---

## 17. Anti-crunch production

**The question.** Is crunch (sustained overtime before milestones) a necessary part of making games, or a management failure?

**Positions.**
- *Crunch as necessity or passion:* still defended implicitly by schedules that assume it.
- *Crunch as failure:* Evan Robinson's IGDA essay "Why Crunch Mode Doesn't Work" (2005) summarized productivity research showing that sustained long hours reduce output after a short period and raise error rates. High-profile crunch reports around major releases in 2018–2020 (for example around *Red Dead Redemption 2* and *Cyberpunk 2077*) and a wave of organizing (Game Workers Unite from 2018, and later unions at several large studios) moved the debate. Studios such as Supergiant and Klei have been reported as working without crunch.

**What replaces crunch.** Scope cuts decided early; fixed milestones with explicit must/should/won't lists; work-in-progress limits; quality gates that cannot be skipped; sustainable review cadence.

**The agent-studio twist.** Agents do not burn out, but the humans at the taste checkpoints do, and the agent equivalent of crunch is *quality crunch*: skipping gates, faking evidence or marking features done to hit a date. That is prohibited by design: the `stop_gate.py` and `pre_tool_guard.py` hooks block features marked done without passing gates.

**House position.** When the schedule slips, move items from `scope.should` to `scope.wont`; never relax gates. Keep human checkpoints few, batched and predictable (`production`, `producer`).

---

## 18. AI in the pipeline vs AI in the product

**The question.** Should generative AI stay behind the scenes (code, tests, drafts, tools), produce player-visible content (art, voice, text), or be the gameplay itself?

**Positions.**
- *Pipeline accelerator:* AI speeds engineering, QA and iteration while human-directed design and a consistent art direction keep the quality bar. Some studios publicly promise players will not see generative AI content while using it heavily internally (see volatile facts).
- *Visible generated content:* cheaper assets at scale; faces disclosure requirements and documented player backlash, and disclosed-AI releases are associated with fewer reviews (correlation, not proven cause).
- *AI as mechanic:* LLM characters, judge games and player creation tools; viable when cost, latency and safety are controlled.

**When each is right.**

| Choose | When |
|---|---|
| Pipeline accelerator | Default for any commercial game: it improves speed without player-facing risk |
| Visible generated assets | Only under a locked style bible, human approval, provenance and licence checks, and disclosure where required |
| AI as mechanic | The AI interaction *is* the fun, and costs per session fit the business model |

**House position.** Doctrine 9 and 10: every generated asset is recorded in `assets/manifest.json` with provider, model, prompt, licence and approval; `licence_check` runs before release; humans sign off the style. Disclosure-ready metadata is kept from day one (`ai-asset-pipeline`, `ai-audio-pipeline`, `legal-ethics`).

---

## 19. Fast-follow vs originality

**The question.** Follow a proven design quickly, or invent?

**Positions.**
- *Fast-follow:* Tencent and NetEase translated proven genres; Riot's *Teamfight Tactics* followed the auto-battler wave; *Monopoly Go!* executed a proven loop with an IP. Lower market risk, faster validation.
- *Originality:* *Threes!*, *Papers, Please*, *Balatro* created new spaces; originators are often cloned (*Threes!* by *2048*; Vlambeer's experience before *Ridiculous Fishing*). Higher risk, stronger differentiation and press.
- *Legal backdrop (not legal advice):* game mechanics are generally treated as unprotectable ideas under US copyright law, but expression is protected; *Tetris Holding v. Xio Interactive* (2012) found a close visual clone infringing, and *Spry Fox v. 6waves* (2012, over *Triple Town*) settled. See `legal-ethics`.

**House rule: genre yes, game no.** Borrow genre conventions; change at least one pillar-level element (the `hook`); never copy assets, names, text or level layouts; record what you borrow and what you change in `meta.comparables[]` (`borrow`, `change`) and credit influences publicly where appropriate (`analogy-engine`).

---

## 20. Quick decision matrix

| If the project is... | Ludo/narr. | Systems/content | Product/service | Monetization | Data stance | Juice | Time stance |
|---|---|---|---|---|---|---|---|
| Hybrid-casual action | Rules first | Systems core + PCG | Product, earn service | Ads + IAP, ethics list | Data-informed, large effects | High, readable | Short runs, no chores |
| Match-3 / tile puzzle | Rules + narrative meta | Content via PCG + solver | Service after soft launch | IAP + rewarded ads | Data at scale | Medium, board readable | Lives only if recoverable |
| Premium puzzle | Rules, light story | Authored content | Product | Premium | Intuition + playtest | Restrained | Every level purposeful |
| Cozy life-sim | Rules + emergent story | Systems + seasonal content | Product with updates | Premium or cosmetics | Intuition + qualitative | Soft | No absence penalties |
| Roguelite | Rules | Systems | Product or light service | Premium or capped meta IAP | Run metrics | High | Short runs, quick restart |
| Competitive PvP | Rules | Systems + roster content | Service | Cosmetics, no pay-to-win | Data | High, readable | Short matches |

---

## 21. Volatile facts (as of Oct 2026 — verify before relying)

| Fact | Relevance | Source |
|---|---|---|
| Hybrid-casual had the largest spending jump of any mobile segment in 2025 (+17.1%, about $3.5B → $4.2B). | Supports section 11 as the default genre family. | [Mobilegamer.biz (Sensor Tower data)](https://mobilegamer.biz/data-digest-sensor-towers-h1-analysis-hay-days-comeback-julys-top-games-big-krafton-numbers-and-more/) |
| Voodoo tested about 1,000 prototypes a year (2024) and pivoted to about four hybrid-casual launches a year. | Section 10: the test machine gave way to fewer, deeper launches. | [mobilegamer.biz](https://mobilegamer.biz/voodoo-to-launch-just-four-games-per-year-after-hard-hybridcasual-pivot/) |
| 2025 mobile game IAP rose about 1% to about $82B; growth came from retaining and monetizing existing players through live ops, events and collaborations. H1 2026 IAP fell about 2%, downloads about 12%. | Section 5: services win by retention, not downloads. | [Sensor Tower](https://sensortower.com/press/press-release-sensor-tower-state-of-gaming-gaming-drove-52-billion-downloads-82b-iap-revenue-on-mobile-and-12b-premium-revenue-on-steam); [Mobilegamer.biz](https://mobilegamer.biz/data-digest-sensor-towers-h1-analysis-hay-days-comeback-julys-top-games-big-krafton-numbers-and-more/) |
| GameAnalytics-based benchmarks (via secondary write-ups): median D1 about 22%, D7 just under 4%, D30 about 0.7–0.8%; top 1% about 64–68% D1. | Calibrates `analytics.kpi_targets`. | [Segwise](https://segwise.ai/blog/mobile-gaming-app-user-retention-strategies); [Playio](https://blog.playio.co/d1-d7-d30-retention-benchmarks-2026) |
| Practitioner diagnostic: D7/D1 below about 0.30 points to a first-session/FTUE problem; 0.30–0.44 to weak days 2–5 engagement (consensus heuristic, not a rule). | Section 14 and soft-launch triage. | [GameDev.net](https://gamedev.net/blogs/entry/2298160-the-d7d1-retention-ratio-for-mobile-games-a-complete-guide) |
| Claim: if the aha moment takes more than about 90 seconds, a significant share of users never return (practitioner blog; treat with caution). | Section 14 time-to-fun. | [Playio](https://blog.playio.co/mobile-game-onboarding-retention) |
| Valve's January 2026 policy exempts efficiency tools (code assistants, build, QA) from AI disclosure but requires disclosure of player-visible generated art, voice and text; a study of 2025 Steam releases found AI-disclosing games got about 53% fewer reviews (median score 84.6% vs 88.3%), with causation not established. One studio promises players "will not see generative AI" while using it internally. | Section 18. | [Recognizing Patterns](https://recognizingpatterns.substack.com/p/use-ai-to-build-your-game-just-keep) |
| Brazil's ECA Digital bans loot-box sales to under-18s from March 2026; a June 2026 court order against Riot Games required damages, age verification and odds disclosure. | Sections 6 and 16. | [Sheep Esports](https://www.sheepesports.com/articles/brazil-court-orders-riot-games-to-pay-eur2-5m-over-league-of-legends-loot-boxes/en) |
| Australia: games classified after 22 Sep 2024 with paid chance-based items are rated at least M; simulated gambling is R18+. | Sections 6 and 16. | [PCWorld](https://www.pcworld.com/article/2464538/all-games-with-loot-boxes-will-be-rated-m-or-higher-in-australia.html) |
| Amended US COPPA Rule compliance deadline was 22 Apr 2026 (expanded personal information including biometrics; third-party disclosure consent). | Section 16. | [Loeb & Loeb](https://www.loeb.com/fr/insights/publications/2025/05/childrens-online-privacy-in-2025-the-amended-coppa-rule) |
| From 1 Oct 2026 in the EU, Apple requires a parental gate for under-18 apps using alternative payments or link-outs, and bars link-outs in Kids-category and under-13 apps. | Section 16. | [Apple Newsroom](https://www.apple.com/newsroom/2026/08/apple-announces-changes-for-apps-in-the-european-union/) |
