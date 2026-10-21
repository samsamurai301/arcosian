# Fun and Motivation Design

How to turn player motivations into mechanics, and how to do it without burning out intrinsic motivation or crossing into manipulation. This file maps motivations (Quantic Foundry's model, self-determination theory, Lazzaro's keys) to concrete mechanics and metrics; gives design patterns for mastery, autonomy and relatedness; explains intrinsic versus extrinsic rewards and the overjustification effect with design rules; treats variable rewards with the maths (drop odds, expected attempts, pity) and an explicit ethics framework; covers novelty and curiosity, arousal and the Yerkes–Dodson relationship, failure design (fail forward, cost of failure, retry speed), and designing for different player segments on mobile. Use it when choosing reward structures, writing FTUE and retention features, or reviewing monetization-adjacent loops.

## Contents

1. Motivation → mechanic map
2. Designing for competence and mastery
3. Designing for autonomy
4. Designing for relatedness
5. Intrinsic vs extrinsic rewards and overjustification
6. Variable rewards: schedules, maths and ethics
7. Novelty and curiosity
8. Arousal and the Yerkes–Dodson relationship
9. Failure design
10. Behavioural effects toolbox (use and abuse)
11. Designing for different player segments on mobile
12. Procedure: motivation design pass
13. Ethics guardrails (non-negotiable)

---

## 1. Motivation → mechanic map

Use the target segment's top motivations (`contract.meta.target_audience.motivations`) to select mechanics. Motivation labels follow Quantic Foundry's Gamer Motivation Model (see `foundational-frameworks.md` section 20); SDT needs and Lazzaro keys are noted where they apply.

| Motivation | Core desire | Mechanics that serve it | Mobile example pattern | Metric to watch |
|---|---|---|---|---|
| Destruction | Chaos, spectacle | Destructible objects, big explosions, chain reactions | Physics demolition puzzles; colour-bomb combos | Combo frequency; replay of spectacle moments |
| Excitement | Pace, surprise | Time pressure, escalating waves, near-death moments | Survivor-likes; runners | Session intensity curve; retry rate |
| Competition | Beating others | Ladders, leagues, PvP, leaderboards | Weekly leagues with promotion/relegation | League participation; churn after demotion |
| Community | Belonging | Teams, chat, co-op goals, gifting | Team events; life-gifting | Team join rate; retention lift for team members |
| Challenge | Overcoming difficulty | Hard levels, optional objectives, mastery ranks | 3-star objectives; hard-mode levels | Attempts per level; voluntary hard-mode play |
| Strategy | Planning, decisions | Resource trade-offs, build choices, deck building | Card battlers; tactics; base layouts | Decision time; strategy diversity |
| Completion | Finishing everything | Collections, checklists, 100% markers, albums | Sticker albums; collection books | Collection completion distribution |
| Power | Growing stronger | Levels, upgrades, gear, stat growth | Hero upgrade trees | Upgrade spend rate; power vs content pace |
| Fantasy | Being someone else | Role, identity, cosmetic self-expression | Chef/mayor/hero fantasies | Cosmetic engagement |
| Story | Narrative | Chapters, characters, cliffhangers | Story-driven renovation meta | Story beat completion; skip rate |
| Design | Self-expression | Customization, decoration, creation tools | Room/base decoration; avatar editors | Time in customization; share/visit rate |
| Discovery | Exploring, tinkering | Hidden content, experimentation, emergent combos | Merge chains with unknown results; secret levels | Exploration actions; discovery rate |

**SDT overlay.** Competence ↔ Challenge, Strategy, Power; autonomy ↔ Design, Discovery, Strategy; relatedness ↔ Community, Competition (positive forms).

**Lazzaro overlay.** Hard Fun ↔ Challenge/Strategy/Competition; Easy Fun ↔ Discovery/Fantasy/Design; Serious Fun ↔ relaxation and real-world value; People Fun ↔ Community/Competition.

**Rule.** A feature must serve at least one of the top three motivations of the target segment. If it serves only a motivation the segment scores low on, it is a cost centre unless it opens a deliberate new segment.

---

## 2. Designing for competence and mastery

Competence is the feeling of being effective and growing. It requires: **clear goals**, **discernable feedback**, **fair challenge**, and **visible growth**.

### 2.1 Two kinds of growth

| Growth type | What grows | Strength | Risk |
|---|---|---|---|
| Skill growth | The player's ability | Intrinsic, durable, transferable | Plateaus; frustrates low-skill players |
| Power growth | The character's numbers | Reliable progress feeling for everyone | Hollow if skill does not matter; pay-to-win perception |

Healthy games blend both: power growth smooths difficulty for less skilled players; skill growth gives depth for the engaged. Check the blend by measuring how much of clear-rate variance is explained by power level vs player skill (bot experiments with fixed power and varied skill, and vice versa).

### 2.2 Competence feedback patterns

| Pattern | Purpose | Example |
|---|---|---|
| Performance grade | Show quality, not just pass/fail | 1–3 stars; S/A/B ranks |
| Personal best | Self-comparison is safer than social comparison | "New best!" on score |
| Mastery markers | Recognise milestones in skill | Combo counters, perfect-run badges |
| Death/fail recap | Explain why the player failed | "Defeated by: Poison Bomber — tip: Freeze counters it" |
| Progress made visible | Show cumulative growth | Skill tree fill, collection percentage |
| Near-miss framing (honest) | Show how close the player came | "2 blockers left" at failure — informational, not manipulative, if accurate |

### 2.3 Competence killers

- Failure the player cannot explain (hidden rules, random losses at high stakes).
- Difficulty spikes used as purchase prompts.
- Power walls that skill cannot overcome.
- Feedback that praises everything (inflated praise stops carrying information).

---

## 3. Designing for autonomy

Autonomy is the feeling that actions are self-chosen and meaningful.

**Autonomy supports.**
- **Meaningful choices** in the core loop (see `decisions-and-depth.md`).
- **Opt-in goals**: optional objectives, side quests, multiple paths to the same reward.
- **Self-set pacing**: play as long or as briefly as you like; no penalty for absence.
- **Expression**: customization that others can see.
- **Choice of challenge**: difficulty modes, risk/reward paths (Chen's player-driven flow; `foundational-frameworks.md` section 17).

**Autonomy killers (detect in reviews).**

| Killer | Detection | Fix |
|---|---|---|
| Forced tutorials that block exploration | Many taps on locked UI during FTUE | Teach in context; allow skipping for returning players |
| Popup chains | > 1 popup on session entry | Queue and cap; show in a non-blocking inbox |
| FOMO pressure | Countdown timers on most screens; event rewards unobtainable without daily play | Catch-up mechanics; generous windows; return-player bonuses |
| Punitive streaks | Losing a long streak wipes progress | Streak freezes, decay instead of reset, grace days |
| Obligatory dailies | Daily task lists that take longer than a session | Cap daily obligations to one session; let tasks bank |
| Mandatory ads | Ads unrelated to player choice | Rewarded ads only, opt-in (`monetization`) |

---

## 4. Designing for relatedness

Relatedness is feeling connected to others. On mobile, most players want **light-touch** social: low commitment, positive, asynchronous.

| Intensity | Mechanics | Fit |
|---|---|---|
| Ambient | See others' progress, likes, visits | Broad casual |
| Reciprocal | Gift and request (lives, energy, items) | Casual to midcore |
| Cooperative | Team goals, co-op events, shared bosses | Midcore |
| Competitive | Leagues, PvP | Players with Competition motivation |
| Deep | Guild management, real-time co-op raids, voice | Hardcore |

**Rules.**
- Always provide a **solo path** to all core progress.
- Make social actions **net positive** for the receiver (gifts, help) — avoid designs where others' actions mostly hurt you, unless the audience is explicitly competitive and protections exist.
- Prevent **guilt loops** (team penalties for missing a day).
- Moderate chat and protect minors (`legal-ethics`).
- **Pseudo-relatedness** (named NPC companions who react to your progress) works for solo-leaning audiences and has no moderation cost.

---

## 5. Intrinsic vs extrinsic rewards and overjustification

**Intrinsic motivation**: doing something because it is inherently satisfying. **Extrinsic motivation**: doing it for a separable outcome (points, currency, prizes, approval).

**The overjustification effect.** Classic experiments found that giving people expected, tangible rewards for an activity they already enjoyed could reduce their later free-choice engagement with it:
- Edward Deci (1971): participants paid to solve puzzles spent less free time on the puzzles afterward than unpaid participants.
- Lepper, Greene & Nisbett (1973): preschoolers who *expected* a certificate for drawing later drew less in free play; children who received the same reward *unexpectedly* did not show the drop.
- A 1999 meta-analysis by Deci, Koestner and Ryan concluded that expected, tangible, task-contingent rewards tend to undermine intrinsic motivation, while positive verbal feedback tends to enhance it. Other researchers (e.g., Cameron and Pierce) argued the undermining effect is narrower than claimed — treat it as a real risk under specific conditions, not a universal law.

**Cognitive evaluation theory (SDT) explanation.** Rewards perceived as **controlling** ("you must do this to get that") shift the reason for acting from inside to outside; rewards perceived as **informational** ("you did this well") support competence.

**Design rules.**

| Do | Don't |
|---|---|
| Reward *how well* players played (informational) | Pay players to do the thing that is already fun ("play 10 matches for 50 gems") as the main motivator |
| Use rewards that feed back into play (new tools, new options) | Use rewards disconnected from play (abstract points that buy nothing meaningful) |
| Surprise rewards occasionally (unexpected bonuses) | Make every action a contract with a payout |
| Frame quests as invitations to explore ("try a deck with a Mage") | Frame quests as chores ("log in 7 days") |
| Let intrinsic loops carry the core; use extrinsic structures to scaffold onboarding and long-term goals | Bolt extrinsic structures onto a core that is not fun on its own |

**Worked example: daily quest redesign.**
- Before: "Win 5 matches" (extrinsic, controlling, rewards grinding; frustrates low-skill players).
- After: rotating quests that invite variety and skill expression — "Win a match using a card you've never played", "Deal the final blow with a spell", "Complete a level with 5+ moves left". Rewards include a cosmetic tied to the quest's theme. Quests bank up to 3 so missing a day is not a loss.

**Diagnostic.** If players stop playing a mode the day its extrinsic rewards end (event over, pass complete), the mode was being played for the rewards. That may be acceptable for side modes; it is a red flag for the core loop.

---

## 6. Variable rewards: schedules, maths and ethics

### 6.1 Reinforcement schedules

From operant conditioning research (Ferster & Skinner, *Schedules of Reinforcement*, 1957):

| Schedule | Rule | Behaviour pattern (lab findings, simplified) | Game examples |
|---|---|---|---|
| Fixed ratio | Reward every N actions | High rate, pause after reward | "Every 10 wins earns a chest" |
| Variable ratio | Reward after an unpredictable number of actions (average N) | High, steady rate; persists longest when rewards stop | Random drops, loot boxes, gacha |
| Fixed interval | Reward available after fixed time | Activity clusters near the time | Daily rewards; timed chests |
| Variable interval | Reward available after unpredictable time | Steady checking behaviour | Random world events; surprise spawns |

Variable-ratio schedules are the most compelling and the most dangerous. They are the core of slot machines.

### 6.2 Drop-odds maths

For a reward with independent chance *p* per attempt:

```
Expected attempts to first success = 1 / p
P(at least one success in n attempts) = 1 − (1 − p)^n
Attempts needed for confidence c: n = ln(1 − c) / ln(1 − p)
```

Worked example, p = 1%:
- Expected attempts = **100**.
- 50% of players have it by attempt **69**; 90% by **230**; 95% by **299** (rounding up).
- So 5% of players need *more than three times* the average — this tail is where frustration and overspending concentrate.

Mitigations: **pity/guarantee** at N attempts caps the tail (use `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gacha_calc.py --rate 0.01 --hard-pity 90 --pulls 200 --json`); **pseudo-random distribution** narrows streaks (`decisions-and-depth.md` section 11); **duplicate protection** prevents receiving the same item repeatedly.

### 6.3 Ethical framework for variable rewards

Variable rewards can add delight (a surprise rare drop in a free chest) or exploit (paid random boxes designed around near-misses). Apply all of these:

1. **Transparency**: disclose odds wherever paid randomness exists — and in many jurisdictions and storefronts this is required (see `legal-ethics` and `store-release` for current rules).
2. **Bounded tails**: pity timers or guarantees on any paid random reward.
3. **No money at the moment of maximum arousal**: no purchase prompts immediately after a near-miss or a loss streak.
4. **No fake near-misses**: never display "almost won" outcomes more often than the true odds produce them. Gambling research (e.g., Reid, 1986; Clark and colleagues, 2009) suggests near-misses increase the urge to continue, which is exactly why manufacturing them is manipulative.
5. **Minors**: no paid random rewards for players identified as minors; follow age-rating and regional rules (`legal-ethics`).
6. **Spending visibility**: show players their spend history; offer limits.
7. **The removal test** (from `core-loops-and-structure.md` section 8): remove the random reward; if the loop collapses, the loop is the slot machine.
8. **Prefer deterministic paths**: offer a direct-purchase or earnable path to every item in a random pool.

---

## 7. Novelty and curiosity

**Curiosity theory, briefly.**
- Daniel Berlyne (*Conflict, Arousal, and Curiosity*, 1960) identified "collative" properties that drive exploration: **novelty, complexity, uncertainty and conflict**. Interest tends to peak at moderate levels — too familiar is boring, too strange is aversive (often drawn as an inverted-U "Wundt curve" of pleasure vs stimulus intensity).
- George Loewenstein ("The Psychology of Curiosity", 1994) proposed the **information-gap** account: curiosity arises when attention is drawn to a specific gap in knowledge — and it is strongest when the gap feels small enough to close.

**Curiosity mechanics.**

| Mechanic | Gap it opens | Example |
|---|---|---|
| Silhouettes / "?" slots | What is this item? | Merge chains showing the next item as a silhouette |
| Partial maps / fog | What is over there? | Map areas greyed with visible landmarks |
| Teasers | What happens next? | Story cliffhanger at session end |
| Locked-but-visible content | What does this unlock? | Next world visible on the map |
| Combination systems | What if I combine X and Y? | Alchemy/merge discovery games |
| Mystery rewards (free) | What's inside? | Free daily mystery box with disclosed odds |

**Novelty schedule.** Players habituate: a new element's novelty value decays over repetitions. Plan a novelty cadence:
- **Early game**: something new every session (new element, area, feature unlock).
- **Mid game**: something new every few sessions (new mechanic twists, events).
- **Live game**: rotating events and seasonal content (`liveops`).
Track novelty in the content plan: list each new element and the session/level it first appears. Gaps longer than your engaged players' weekly playtime indicate a novelty drought.

**Novelty vs mastery.** Too much novelty prevents mastery (nothing gets learned well); too little produces boredom. Pair each new element with teach–test–twist–reward sequencing (`core-loops-and-structure.md` section 12).

---

## 8. Arousal and the Yerkes–Dodson relationship

**Origin and caveat.** Robert Yerkes and John Dodson (1908) studied how the strength of an electric stimulus affected how quickly mice learned a discrimination task; later writers generalised their findings into the "Yerkes–Dodson law": performance rises with arousal up to an optimum, then falls (an inverted U), and the optimum is lower for more complex tasks. The generalised version is a useful design heuristic, not a precise law.

**Design implications.**

| Task type | Optimal arousal | Design consequence |
|---|---|---|
| Simple, well-learned (tap rhythm, dodge) | Higher | Timers, speed and intensity can be pushed |
| Complex, novel (puzzle planning, deck building) | Lower | Avoid timers during planning; calm audio; allow undo |
| Social / competitive | Varies by player | Offer both casual and ranked modes |

**Practical rules.**
- Do not add time pressure to tasks that require planning unless the design goal is chaos (e.g., party games).
- Teach new mechanics in low-arousal contexts; test them in higher-arousal contexts once learned (teach → test → twist).
- Alternate arousal levels across a session (`core-loops-and-structure.md` section 11).
- On phones, ambient arousal is already variable (a crowded train vs a quiet bed); give players control (calm/relax modes, sound toggles).

---

## 9. Failure design

Jesper Juul (*The Art of Failure*, 2013) describes a "paradox of failure": people generally avoid failing, yet seek out games where they fail repeatedly — because failure in games signals there is something to improve and makes eventual success meaningful. Failure must therefore be designed, not merely tolerated.

### 9.1 The cost-of-failure scale

| Level | What is lost on failure | Emotional effect | Fits |
|---|---|---|---|
| 0 — None | Nothing; instant retry | Experimentation encouraged; low stakes | Puzzles, creative modes, FTUE |
| 1 — Time | The attempt's duration | Mild sting | Short levels |
| 2 — Attempt resource | A life/energy/ticket | Real stakes; pacing | Sagas (use carefully) |
| 3 — Progress | Run progress (roguelite) | Strong tension; meta progress must soften it | Roguelites |
| 4 — Earned assets | Items, rank, currency | High stakes; anxiety | Ranked PvP, hardcore modes |
| 5 — Everything | Permanent loss | Extreme; niche | Hardcore niche only |

**Rule.** Match failure cost to session length and audience. A 2-minute mobile session cannot absorb a level-4 loss without churn risk; FTUE should sit at level 0–1.

### 9.2 Fail forward

"Fail forward" (a term popular in tabletop role-playing design) means a failure still moves the player forward in some way: knowledge, partial progress, meta currency, or a new situation, instead of a dead stop.

| Technique | How | Example |
|---|---|---|
| Partial progress | Keep some progress from a failed attempt | Destroyed blockers stay destroyed on retry (if fits design) |
| Meta progression | Failure grants permanent currency or unlocks | Roguelite meta upgrades after each run |
| Knowledge gain | Failure reveals information | Boss patterns revealed; death recap with tips |
| Branching | Failure leads to a different, not worse, path | Narrative branches on failure |
| Consolation | Small reward scaled by performance | Coins earned per blocker cleared even on loss |

### 9.3 Retry speed

Time-to-retry is one of the strongest levers on failure tolerance. Design target: the player should be back in control within a few seconds of failing, with the cause of failure understood. Measure `fail → next attempt start` time in telemetry; long gaps followed by session end indicate failure friction.

### 9.4 Failure screens: honest vs exploitative

| Honest | Exploitative |
|---|---|
| Shows why the player failed and how close they were, accurately | Inflates "so close!" framing beyond reality |
| Offers retry first, purchase second | Leads with a purchase and hides retry |
| Offers an extra-moves purchase at a fair, transparent price | Escalating prices on repeated "continue" offers within one attempt |
| Respects "no" (one offer per failure) | Chains multiple offers |

### 9.5 Worked example: roguelite run failure

- Cost: level 3 (run progress lost).
- Softeners: meta currency earned per room cleared (fail forward); death recap naming the killer and a counter tip (knowledge); "new best depth" marker (competence).
- Retry: one tap to start a new run, with a reminder of meta upgrades now affordable.
- Telemetry: run-end → next-run-start time; share of players who start another run within the same session; churn after first death.

---

## 10. Behavioural effects toolbox (use and abuse)

These effects are documented in psychology and behavioural economics research; their size and reliability vary. See `player-psychology` for depth.

| Effect | Short description | Ethical use | Abuse to avoid |
|---|---|---|---|
| Goal gradient (Hull, 1932; Kivetz et al., 2006) | Effort increases as a goal nears | Show progress bars near completion | Artificially slowing the last steps to sell skips |
| Endowed progress (Nunes & Drèze, 2006) | People given a head start are more likely to finish | Start collections with a few items filled | Fake head starts on paid tracks |
| Zeigarnik-type effect (Zeigarnik, 1927) | Unfinished tasks stay on the mind (replications are mixed) | Exit hooks: show what is in progress | Never letting anything feel complete |
| Peak–end rule (Kahneman et al., 1993) | Experiences are judged by their peak and their end | End sessions on a high (celebration, reward) | Hiding losses by forcing an upbeat end screen before a purchase prompt |
| Loss aversion (Kahneman & Tversky, 1979) | Losses loom larger than gains | Avoid punitive design; frame progress positively | Streaks and "your rewards will expire" pressure |
| Sunk cost | Past investment drives continued investment | — (no ethical use as a lever) | Escalating spend prompts based on past spend |
| Social proof | People follow what others do | Show popular strategies, community achievements | Fake "X players just bought this" |
| Scarcity | Rare/limited things feel more valuable | Seasonal cosmetics announced well in advance | Fake countdowns that reset |

---

## 11. Designing for different player segments on mobile

Mobile audiences are broad. Segment by **motivation and commitment**, not by stereotype or demographic assumption.

| Segment (working labels) | Typical commitment | Top motivations (likely) | Design levers | Pitfalls |
|---|---|---|---|---|
| Relaxers | Short sessions, many days | Completion, Design, Fantasy, low Challenge | Calm pacing, low failure cost, collections, decoration | Difficulty spikes; social obligations |
| Puzzlers | Short-to-medium sessions | Challenge, Strategy, Completion | Clean levels, fair difficulty, stars, daily puzzles | Random losses; monetized walls |
| Thrill-seekers | Short, intense sessions | Excitement, Destruction, Power | Juice, speed, escalating waves, power growth | Slow onboarding; text-heavy menus |
| Collectors | Medium sessions, long tenure | Completion, Power, Fantasy | Albums, sets, upgrade trees, visible growth | Unbounded random tails; duplicate floods |
| Competitors | Medium sessions, high skill investment | Competition, Challenge, Strategy | Fair matchmaking, ranked seasons, replays | Pay-to-win; matchmaking abuse |
| Socialisers | Daily, community-anchored | Community, Design | Teams, gifting, chat, co-op events | Toxicity; guilt mechanics |

**Designing for several segments at once (onion layering).**
1. **Core layer** serves the primary segment and must be fun alone.
2. **Optional layers** add depth for secondary segments (ranked mode for competitors, collection book for collectors, decoration for designers) without being required.
3. **Opt-in visibility**: optional layers unlock after the core is established (not in the FTUE) and can be ignored without penalty.
4. **Check conflicts**: a competitive mode's rewards must not become mandatory for relaxers' progress.

**Personas for simulated playtests.** Turn each target segment into a persona file for `arcosian:player-simulator`: goal, patience (seconds before frustration), skill (0–1), spend propensity, social propensity, and stop rules ("stops after 3 consecutive fails", "stops when a popup chain exceeds 2"). Align numbers with the archetypes in `economy-model.schema.json` (`skill`, `spend_propensity`, `ad_accept_rate`, `sessions_per_day`, `session_minutes`).

---

## 12. Procedure: motivation design pass

1. **Name the segment** and its top 3–4 motivations; record in the contract.
2. **Map** each motivation to at least one mechanic and one loop (section 1 table).
3. **Audit needs**: competence (section 2), autonomy (section 3), relatedness (section 4). List supports and killers.
4. **Classify every reward** as informational or controlling; fix controlling rewards on intrinsically fun activities (section 5).
5. **Inventory randomness**: for every variable reward, compute the tail (section 6.2) and apply the ethics checklist (section 6.3).
6. **Plan novelty** and curiosity gaps across the first 7 days of play (section 7).
7. **Check arousal**: no time pressure on planning tasks; arousal alternates (section 8).
8. **Design failure** for each mode: cost level, fail-forward technique, retry speed, honest failure screen (section 9).
9. **Write personas** for the segments and schedule a `playtest` run with `arcosian:player-simulator`.
10. **Record** findings in the contract (`mechanics[].feedback`, `monetization.ethics`, `risks`) and route ethics questions to `arcosian:compliance-officer`.

---

## 13. Ethics guardrails (non-negotiable)

Derived from the plugin doctrine (ethical monetization; respect for minors):
- Disclose odds for any paid randomness; cap tails with pity.
- No purchase prompts timed to near-misses, loss streaks or emotional peaks.
- No fake scarcity, fake social proof, or resetting countdowns.
- No punitive streak or absence mechanics that remove earned progress.
- No paid random rewards for minors; age-appropriate defaults.
- A solo, free path to all core gameplay progress.
- Every retention mechanic passes the "reflective endorsement" test: would players, thinking calmly afterward, be glad it was there?
See `legal-ethics` for regional law and `monetization` for compliant offer design.
