# Cross-game patterns

Fifty-nine recurring success patterns distilled from the roughly 90 case studies in this skill and from a few widely documented landmark games outside it. A pattern here is a **rule that recurs across genres and keeps working for the same reason**, not a feature. Each card gives a definition, the mechanism (why it works, in terms of player psychology or system dynamics), the games that use it, its risks (design, business and ethical), ontology tags that map it onto the shared schemas, and when to apply or avoid it. Patterns are grouped by layer (core loop, run structure, meta, economy, social, live-ops, identity), and sections 10–13 show how they combine into proven stacks, where they conflict, how to select them for a concept, and how to screen them ethically. The format follows the pattern-language tradition (Christopher Alexander, *A Pattern Language*, 1977), applied to games by Staffan Björk and Jussi Holopainen (*Patterns in Game Design*, 2005); the patterns themselves are this skill's synthesis of the cases. Psychology terms follow the vocabulary table in `SKILL.md`, with attribution there.

**Contents.**
1. How to read a pattern card (fields and tag grammar)
2. Pattern index
3. Core-loop and feel patterns (P01–P10)
4. Run and challenge structure patterns (P11–P20)
5. Meta and progression patterns (P21–P30)
6. Economy and randomness patterns (P31–P38)
7. Social patterns (P39–P49)
8. Live-ops and time patterns (P50–P56)
9. Identity and positioning patterns (P57–P59)
10. Pattern stacks: proven combinations by archetype
11. Conflicts and interactions
12. Procedure: selecting patterns for a concept (with worked example)
13. Ethics screen

## 1. How to read a pattern card

| Field | Meaning |
|---|---|
| Definition | The rule in one or two sentences, stated so it can transfer across genres |
| Mechanism | Why it works: the player need or system dynamic behind it (the "need" rung of the feature → rule → need ladder in `SKILL.md`) |
| Games | Cases that use it. File references point to this skill's case files; titles without a reference are widely documented landmark games outside the case files |
| Risks | How it fails, who it can harm, and the guardrail |
| Tags | Ontology tags (grammar below) used to find the pattern with `gs.py kb` and to encode it in a contract |
| Apply / avoid | Conditions under which the pattern fits, and when it does not |

**Tag grammar.** Every tag points at a field in the shared schemas (BLUEPRINT section 5), so a chosen pattern converts directly into contract or model entries.

| Tag | Maps to | Allowed values |
|---|---|---|
| `loop:<type>/<period>` | `contract.loops[].type`, `.period` | type: core, meta, social, monetization, liveops; period: seconds, minutes, session, daily, weekly, season |
| `cur:<kind>` | `contract.economy.currencies[].kind` | soft, hard, premium, energy, event, xp, material |
| `node:<kind>` | `economy-model.nodes[].kind` | source, sink, converter, gate, pool |
| `trig:<trigger>` | `economy-model.nodes[].trigger` | per_session, per_minute, per_level_attempt, per_level_win, per_level_loss, daily, weekly, on_purchase, on_ad |
| `mech:<category>` | `mechanic-card.category` | movement, aiming, timing, placement, merge, match, sort, physics, combat, resource, construction, chance, collection, progression, social, narrative, puzzle, economy |
| `aes:<aesthetic>` | `mechanic-card.aesthetics` (MDA) | sensation, fantasy, narrative, challenge, fellowship, discovery, expression, submission |
| `prog:<field>` | `contract.progression` | tracks, difficulty.model, difficulty.target_win_rate, difficulty.dda |
| `mon:<field>` | `contract.monetization` | iap, ads.rewarded, ads.interstitial, pass, ethics |
| `ops:<field>` | `contract.liveops` | cadence, events |
| `kpi:<key>` | `contract.analytics.kpi_targets` | d1, d7, d30, session_len_sec, sessions_per_day, arpdau_usd, payer_conversion |
| `ftue`, `ux:<field>` | `contract.ftue`, `contract.ux` | hud, screens, accessibility |
| `mp:<mode>` | `contract.technical.multiplayer` | none, async, realtime |
| `field:<path>` | any other contract field, by dotted path | e.g. `field:technical.backend`, `field:art_direction`, `field:meta.pillars` |
| `psy:<principle>` | `SKILL.md` psychology vocabulary | variable_ratio, loss_aversion, near_miss, goal_gradient, endowed_progress, zeigarnik, flow, competence, autonomy, relatedness, ikea_effect, social_proof, reciprocity, scarcity, curiosity, peak_end (plus fresh_start, Dai, Milkman and Riis, 2014; illusion_of_control, Langer, 1975; social_comparison, Festinger, 1954) |

**Ethics risk rating** (used in the index): **low** (no special guardrail), **medium** (needs a design guardrail), **high** (needs guardrails plus a legal check in `legal-ethics`; see section 13).

## 2. Pattern index

| # | Pattern | Layer | Clock | Ethics risk | Anchor cases |
|---|---|---|---|---|---|
| P01 | One-more-turn loop closure | core | minutes | medium | Balatro, Slay the Spire, Stardew Valley, Candy Crush |
| P02 | Instant retry | core | seconds | low | Flappy Bird, Downwell, Alto's Odyssey |
| P03 | One input, two meanings | core | seconds | low | Archero, Downwell, Alto's Odyssey |
| P04 | Touch-native verb | core | seconds | low | Fruit Ninja, Reigns, Grindstone, Mini Metro |
| P05 | Juice the verb | core | seconds | low | Candy Crush, Balatro, Royal Match |
| P06 | Multiplicative build scoring | core | minutes | low | Balatro, Vampire Survivors, Downwell |
| P07 | Telegraphed intent | core | seconds | low | Slay the Spire, Grindstone |
| P08 | Mechanics as metaphor | core | minutes | low | Florence, Reigns, Monument Valley |
| P09 | Abstraction to decisions | core | minutes | low | Mini Metro, Threes!, Reigns, Wordle |
| P10 | Authored "aha", solver-verified | core | minutes | low | Monument Valley, Cut the Rope, water sort |
| P11 | Run draft + permanent meta | run | session | medium | Slay the Spire, Dead Cells, Archero |
| P12 | Pick one of three, or skip | run | minutes | low | Slay the Spire, Archero, Vampire Survivors |
| P13 | Pressure that only grows | run | minutes | low | Mini Metro, Tetris, Block Blast! |
| P14 | Push-your-luck | run | minutes | medium | Balatro, Paper.io 2, Downwell |
| P15 | Cumulative difficulty ladder | run | months | low | Slay the Spire, Balatro, Dead Cells |
| P16 | Daily seed for everyone | run | days | low | Wordle, Slay the Spire, Shattered Pixel Dungeon |
| P17 | Failure as continuation | run | session | low | Reigns, Dead Cells |
| P18 | Bank-or-risk checkpoint | run | minutes | low | Dead Cells, Paper.io 2 |
| P19 | Short synchronous duels | run | minutes | medium | Golf Clash, 8 Ball Pool, Clash Royale |
| P20 | Short-session async PvP | run | days | medium | Words With Friends, Clash of Clans, Coin Master |
| P21 | Meta-renovation over a puzzle core | meta | days | low | Homescapes, Royal Match, Merge Mansion, Monopoly Go! |
| P22 | Production chains with order boards | meta | days | low | Hay Day, Township, Travel Town |
| P23 | Merge-to-upgrade generators | meta | minutes | medium | Merge Mansion, Travel Town, Threes! |
| P24 | Near-complete collections | meta | months | high | Monopoly Go!, Coin Master, Stardew Valley |
| P25 | Goal triplets | meta | days | low | Alto's Odyssey, Subway Surfers, Duolingo |
| P26 | Unlocks that widen options, not power | meta | months | low | Slay the Spire, Balatro, Downwell |
| P27 | Keys that reopen space | meta | days | low | Dead Cells, Stardew Valley |
| P28 | Labelled spikes on a sawtooth | meta | days | medium | Royal Match, Candy Crush |
| P29 | Streak with forgiveness | meta | days | medium | Duolingo, Royal Match, Wordle |
| P30 | Bounded day as the planning unit | meta | minutes | low | Stardew Valley, Mini Metro, Balatro |
| P31 | Pity-protected randomness | economy | months | medium | Genshin Impact, Hearthstone, Tetris |
| P32 | Windfall core with a meta destination | economy | seconds | high | Coin Master, Monopoly Go!, Candy Crush |
| P33 | Stake multiplier | economy | seconds | high | Coin Master, Monopoly Go! |
| P34 | Stakes-ladder matchmaking | economy | days | medium | 8 Ball Pool, Golf Clash |
| P35 | Single legible currency | economy | days | low | Royal Match, Monopoly Go! |
| P36 | Forgiving absence | economy | days | low | Hay Day, Pocket City, Sky |
| P37 | Timers as appointments | economy | days | medium | Hay Day, The Sims FreePlay, Golf Clash |
| P38 | Converters that add value over time | economy | days | low | Stardew Valley, Hay Day, Township |
| P39 | Social obligation loop | social | days | medium | Words With Friends, Hay Day, Toon Blast |
| P40 | Reciprocity gifting | social | days | low | Candy Crush, Coin Master, Sky |
| P41 | Revenge loop | social | days | medium | Coin Master, Monopoly Go!, Clash of Clans |
| P42 | Small-cohort leagues | social | days | low | Duolingo, Royal Match, Golf Clash |
| P43 | Fixed small-group co-op project | social | days | low | Monopoly Go!, Hay Day, Township |
| P44 | Player market | social | days | medium | Hay Day, Roblox |
| P45 | Creator economy (UGC) | social | months | high | Roblox, Minecraft, Episode |
| P46 | Hidden-role deduction | social | minutes | low | Among Us |
| P47 | Spoiler-free shareable artefact | social | days | low | Wordle, Monument Valley |
| P48 | Consent-gated communication | social | days | low | Sky, Among Us, Golf Clash |
| P49 | Light-touch presence | social | minutes | low | Sky, Candy Crush, Among Us |
| P50 | Seasonal resets | live-ops | months | low | Monopoly Go!, Sky, Duolingo |
| P51 | Season pass (free + paid tracks) | live-ops | months | medium | Royal Match, 8 Ball Pool, Sky |
| P52 | Overlapping event cadence | live-ops | days | medium | Monopoly Go!, Royal Match, Coin Master |
| P53 | Rotating returns of limited content | live-ops | months | low | Sky, Genshin Impact |
| P54 | Re-theming on a stable core | live-ops | months | low | Subway Surfers, Monopoly Go! |
| P55 | Free major updates for a premium tail | live-ops | months | low | Stardew Valley, Slay the Spire, Minecraft |
| P56 | Graceful service sunset | live-ops | months | low | Animal Crossing: Pocket Camp |
| P57 | Atmosphere-first identity | identity | seconds | low | Alto's Odyssey, Monument Valley, Sky, Mini Metro |
| P58 | Failure-optional mode | identity | session | low | Alto's Odyssey, Minecraft, Mini Metro |
| P59 | Positioning by refusal | identity | months | low | Pocket City, Wordle, Shattered Pixel Dungeon |

## 3. Core-loop and feel patterns

### P01. One-more-turn loop closure
- **Definition.** Every loop iteration ends by revealing the next goal and offering to start it with one tap, so the natural stopping point falls inside a loop rather than between loops.
- **Mechanism.** An open goal (Zeigarnik) that is visibly close (goal-gradient) plus near-zero restart cost. Stopping now feels like abandoning progress.
- **Games.** Balatro and Slay the Spire (a new run in one tap; `premium-indie.md` §4, §6), Stardew Valley (sleep, then plan tomorrow), Candy Crush (next level from the win screen; `puzzle-casual.md` §1), Civilization (the namesake).
- **Risks.** Lost time and sleep; compulsion when combined with paid energy refills. Guardrail: clean exit points (end-of-run summary, end of day) and no "continue" offers sold at the exit point.
- **Tags.** `loop:core/minutes`, `psy:zeigarnik`, `psy:goal_gradient`, `kpi:session_len_sec`.
- **Apply** when sessions are discrete runs, levels or days. **Avoid** stacking with aggressive energy sales; it then becomes a spend trap.

### P02. Instant retry
- **Definition.** Restart after failure in under two seconds, with no menu between death and the next attempt.
- **Mechanism.** Failure costs only seconds, so the player stays in flow (Csikszentmihalyi) and attributes failure to skill, which motivates mastery (competence).
- **Games.** Flappy Bird, Helix Jump (`hyper-hybrid-casual.md`), Downwell, Alto's Odyssey (`premium-indie.md` §1, §10); Super Meat Boy is the canonical PC example.
- **Risks.** An interstitial on every retry destroys the pattern; extremely punishing games can become frustration loops.
- **Tags.** `loop:core/seconds`, `psy:flow`, `psy:competence`, `mon:ads.interstitial` (pace it), `kpi:sessions_per_day`.
- **Apply** to skill-based short attempts. **Avoid** in authored levels where a retry needs a rethink; there, show the failure reason first.

### P03. One input, two meanings
- **Definition.** A single input means different actions by context (move versus stand still, ground versus air, tap versus hold).
- **Mechanism.** Depth without UI: one thumb carries two verbs, and the switching itself becomes a risk-and-reward decision.
- **Games.** Archero's stop-to-shoot (`hyper-hybrid-casual.md` §10), Downwell's jump/shoot button, Alto's tap-to-jump and hold-to-flip.
- **Risks.** Ambiguous contexts cause misfires; the meaning must be readable from the state (on the ground, airborne, moving).
- **Tags.** `mech:movement`, `mech:combat`, `ux:hud`, `aes:challenge`.
- **Apply** to one-thumb portrait games that need a second verb. **Avoid** when both actions are needed at the same time.

### P04. Touch-native verb
- **Definition.** The core verb is a gesture that only feels right on a touchscreen: swipe, draw a chain, drag a line, drag across many targets.
- **Mechanism.** Direct manipulation makes the body part of the feedback loop (sensation); the verb is learned without instruction.
- **Games.** Fruit Ninja (swipe), Reigns (swipe choice), Two Dots and Grindstone (draw a chain), Mini Metro (draw a line), Hay Day (drag to harvest many fields), Block Blast! (drag with an offset).
- **Risks.** Thumb occlusion; fatigue on long drags; accessibility for players with motor impairments (offer tap alternatives).
- **Tags.** `mech:placement`, `aes:sensation`, `ux:accessibility`, `ftue`.
- **Apply** whenever the platform is mobile-first. **Avoid** porting mouse-precision verbs unchanged; redesign them.

### P05. Juice the verb
- **Definition.** Amplify feedback for every action the player touches (particles, sound, pitch rise, screen shake, escalating celebration) in proportion to the action's value.
- **Mechanism.** Feedback intensity signals value and makes success sensory (sensation, peak-end). Escalation tracks the combo, which keeps attention.
- **Games.** Candy Crush's escalating announcer, Royal Match celebrations (`puzzle-casual.md`), Balatro's fire effect when a score beats the target, Fruit Ninja; Peggle's finale is the classic example.
- **Risks.** Noise that hides information; motion sickness; juice that disguises an empty loop. Offer reduced-motion options.
- **Tags.** `aes:sensation`, `psy:peak_end`, `ux:accessibility`.
- **Apply** to every core verb, scaled to its importance. **Avoid** juicing losses as if they were wins (the "losses disguised as wins" problem from slot design).

### P06. Multiplicative build scoring
- **Definition.** Outcomes are computed as products (base × multipliers), so combining the right modifiers produces exponential growth.
- **Mechanism.** The build fantasy: discovering a synergy multiplies power, which feels like cleverness (competence, discovery). Products make small choices matter.
- **Games.** Balatro (chips × mult; `premium-indie.md` §4), Vampire Survivors evolutions (`hyper-hybrid-casual.md` §12), Downwell and Alto combos; Tony Hawk's Pro Skater combo multipliers.
- **Risks.** Power creep, numbers too large to read, balance blow-ups. Guardrail: separate additive and multiplicative modifiers and show the arithmetic step by step.
- **Tags.** `mech:progression`, `aes:discovery`, `aes:challenge`, `psy:competence`.
- **Apply** to run-based builds where breaking the game is the reward. **Avoid** in competitive PvP, where exponential builds wreck fairness.

### P07. Telegraphed intent
- **Definition.** Show what the opposition will do next (attack and amount, countdown, target) before the player commits.
- **Mechanism.** Turns randomness into planning: the player solves a visible problem rather than guessing (competence, autonomy).
- **Games.** Slay the Spire intents (`premium-indie.md` §6), Grindstone countdowns (§15), boss telegraphs in Archero; Into the Breach is the extreme case (every enemy action shown).
- **Risks.** Too much information makes play mechanical; balance requires harder puzzles in exchange.
- **Tags.** `mech:combat`, `aes:challenge`, `ux:hud`, `psy:competence`.
- **Apply** to turn-based and tactical combat, and to boss fights in action games. **Avoid** hiding critical threats behind randomness in any game sold on fairness.

### P08. Mechanics as metaphor
- **Definition.** The verb itself means what the scene means (assembling a speech bubble is finding words; balancing meters is ruling).
- **Mechanism.** Embodied cognition: doing the action produces the feeling, so emotion is felt rather than told.
- **Games.** Florence (`premium-indie.md` §3), Reigns (§9), Monument Valley (§2); Papers, Please is the widely cited PC example.
- **Risks.** Low interactivity; short length; metaphors that players miss.
- **Tags.** `mech:narrative`, `aes:narrative`, `aes:expression`.
- **Apply** to narrative and premium games, tutorials and emotional beats. **Avoid** forcing metaphor on systemic games whose verbs must stay neutral.

### P09. Abstraction to decisions
- **Definition.** Strip a system to the minimum representation that keeps every meaningful decision (shapes for destinations, four meters for a kingdom, three colours for feedback).
- **Mechanism.** Lower perceptual load frees attention for decisions; the game reads instantly on small screens and in short clips.
- **Games.** Mini Metro (shapes), Threes! (`puzzle-casual.md` §12), Reigns (four meters), Wordle (three colours), Pocket City (touch-simplified simulation).
- **Risks.** Too abstract and the theme disappears; depth may plateau for experts.
- **Tags.** `aes:challenge`, `ux:hud`, `ftue`, `mech:puzzle`.
- **Apply** to systemic games for small screens and short sessions. **Avoid** when the fantasy depends on detail (a life sim's furniture).

### P10. Authored "aha", solver-verified
- **Definition.** Each level contains one designed insight; deterministic rules let a solver prove solvability and measure difficulty before release.
- **Mechanism.** Insight problem-solving is one of the most satisfying puzzle experiences; verification removes unfair or unsolvable levels.
- **Games.** Monument Valley (one perceptual insight per level), Cut the Rope and water sort (`puzzle-casual.md` §9, §11).
- **Risks.** Authoring cost per level; solvers measure solvability, not fun. Pair bots with playtests.
- **Tags.** `mech:puzzle`, `aes:discovery`, `prog:difficulty.target_win_rate`. Tools: `puzzle_solver.py --level PATH --algo bfs --json`.
- **Apply** to level-based puzzles. **Avoid** promising handcrafted levels at a content cadence your team cannot sustain.

## 4. Run and challenge structure patterns

### P11. Run draft + permanent meta
- **Definition.** Short runs with in-run power choices that reset on death, wrapped in a persistent meta (unlocks, gear, characters) that changes future runs.
- **Mechanism.** Runs give variety and fresh starts; the meta gives a reason to keep running after failure (endowed progress). The ratio of run power to meta power decides whether skill or investment wins.
- **Games.** Slay the Spire, Dead Cells, Balatro (`premium-indie.md`), Archero, Survivor.io, Vampire Survivors (`hyper-hybrid-casual.md`).
- **Risks.** Free-to-play versions turn the meta into a gear wall (pay to progress). Guardrail: chart non-payer days to the next chapter.
- **Tags.** `loop:core/minutes`, `loop:meta/session`, `prog:tracks`, `psy:endowed_progress`. Tools: `progression_calc.py`, `economy_sim.py`.
- **Apply** to any action or strategy core that supports 3–30 minute attempts. **Avoid** a heavy power meta in premium games (see P26).

### P12. Pick one of three, or skip
- **Definition.** Rewards are offered as a small choice set (usually three), including the option to take nothing.
- **Mechanism.** Autonomy and build identity with low cognitive load; "skip" makes the build's focus a resource.
- **Games.** Slay the Spire card rewards, Archero and Vampire Survivors level-ups, Downwell upgrades, Balatro's shop, Mini Metro's weekly choice of two.
- **Risks.** Choices that are obviously dominant; reroll monetization that becomes pay-to-win.
- **Tags.** `mech:progression`, `psy:autonomy`, `aes:challenge`, `mon:ads.rewarded` (rerolls, if used).
- **Apply** to level-ups, shops and post-fight rewards. **Avoid** more than four options on a phone screen; readability drops.

### P13. Pressure that only grows
- **Definition.** Demand rises continuously until the system breaks; the score measures how long the player kept up.
- **Mechanism.** Flow under escalating challenge; every run ends at the player's skill limit, so the result feels earned.
- **Games.** Mini Metro (§8 of `premium-indie.md`), Tetris, survivor-likes' waves, Block Blast! (`puzzle-casual.md` §5).
- **Risks.** Inevitable failure frustrates some players; interruptions on mobile can be fatal. Guardrail: pause and replan at any time.
- **Tags.** `loop:core/minutes`, `prog:difficulty.model`, `aes:challenge`, `psy:flow`.
- **Apply** to endless and systemic games. **Avoid** in content-led games where players expect to finish.

### P14. Push-your-luck
- **Definition.** The player chooses how much to risk for a bigger payoff: keep money for interest or spend it, stay airborne for a combo, extend a trail away from safety.
- **Mechanism.** Self-chosen risk creates tension and ownership of the outcome (autonomy); variance becomes the player's decision rather than the game's.
- **Games.** Balatro (interest versus spending), Paper.io 2 (exposed trail; `hyper-hybrid-casual.md` §14), Downwell (airborne combos), Monopoly Go! (multiplier timing; see P33 for its risks).
- **Risks.** When the stake is purchasable, push-your-luck becomes gambling-like. Keep the stake in earned, in-run resources.
- **Tags.** `mech:chance`, `aes:challenge`, `psy:autonomy`.
- **Apply** when the stake is earned in play. **Avoid** when the stake can be bought, especially for minors.

### P15. Cumulative difficulty ladder
- **Definition.** After the first win, unlock a sequence of harder modes, each adding one more modifier on top of the previous ones.
- **Mechanism.** Extends a finished game with mastery goals; each level adds one rule to learn (competence).
- **Games.** Slay the Spire Ascension, Balatro stakes, Dead Cells Boss Cells, Shattered Pixel Dungeon challenges; Hades' Heat system.
- **Risks.** Steep late levels lose all but experts; modifiers that are just bigger numbers feel cheap.
- **Tags.** `prog:tracks`, `prog:difficulty.model`, `aes:challenge`.
- **Apply** to any premium game with a replayable core. **Avoid** making the ladder the only endgame for casual audiences.

### P16. Daily seed for everyone
- **Definition.** Once a day, every player gets the same puzzle or run seed.
- **Mechanism.** A shared reference point creates conversation and comparison (social comparison); daily scarcity creates an appointment.
- **Games.** Wordle (`premium-indie.md` §13), Slay the Spire's daily climb, Shattered Pixel Dungeon's daily runs; Spelunky's daily challenge.
- **Risks.** Content exhaustion (needs a generator or a curated list); spoilers (pair with P47).
- **Tags.** `loop:liveops/daily`, `trig:daily`, `psy:scarcity`, `kpi:d30`.
- **Apply** to any deterministic or seeded game. **Avoid** when outcomes depend heavily on purchased power; comparison becomes unfair.

### P17. Failure as continuation
- **Definition.** Death or failure advances something: a dynasty, a story, unlocks, knowledge.
- **Mechanism.** Reframes loss so players do not quit at the moment of failure; failure becomes a beat rather than a wall.
- **Games.** Reigns (the next monarch), Dead Cells (keep unlocks and runes); Rogue Legacy (heirs) and Hades (story advances on death) are the widely cited examples.
- **Risks.** If failure always helps, tension disappears.
- **Tags.** `loop:meta/session`, `mech:narrative`, `aes:narrative`.
- **Apply** to roguelites and narrative games with frequent failure. **Avoid** when failure should carry real stakes (competitive ladders).

### P18. Bank-or-risk checkpoint
- **Definition.** Resources earned in a run are at risk until banked at specific points; death loses what was not banked.
- **Mechanism.** Loss aversion creates tension; checkpoints create pacing and decisions ("push on or go back to bank").
- **Games.** Dead Cells' cells, spent at the Collector between biomes; Paper.io 2's trail, safe only when it closes; Dark Souls' souls are the classic PC case.
- **Risks.** Large losses cause rage-quits; scale the at-risk amount to session length.
- **Tags.** `node:pool`, `node:gate`, `psy:loss_aversion`, `aes:challenge`.
- **Apply** to runs longer than a few minutes. **Avoid** in 30-second hyper-casual runs; there is nothing to bank.

### P19. Short synchronous duels
- **Definition.** Real-time 1v1 matches of a few minutes, with dead time removed (simultaneous turns, shot timers).
- **Mechanism.** The intensity of live competition in a mobile-sized session (competence, social comparison).
- **Games.** Golf Clash (simultaneous play of the same hole; `casual-social-sim.md` §15), 8 Ball Pool (shot timers; §14), Clash Royale (short matches; `midcore-strategy.md`).
- **Risks.** Needs enough concurrent players for fair matchmaking; disconnections; stat-based pay-to-win.
- **Tags.** `mp:realtime`, `loop:core/minutes`, `aes:challenge`, `psy:social_comparison`.
- **Apply** when you can sustain matchmaking liquidity (or fill with clearly labelled bots). **Avoid** at small scale; prefer P20.

### P20. Short-session async PvP
- **Definition.** Players act against each other at different times: turns, raids on stored bases, ghost runs.
- **Mechanism.** Social stakes without scheduling; each session is a few minutes, and the opponent's next move is a reason to return.
- **Games.** Words With Friends (`casual-social-sim.md` §13), Clash of Clans raids (`midcore-strategy.md`), Coin Master attacks and Monopoly Go! heists (`casual-social-sim.md` §1–2).
- **Risks.** Abandoned games; toxic revenge spirals (P41). Guardrails: forfeit timers, shields, loss caps.
- **Tags.** `mp:async`, `loop:social/daily`, `psy:reciprocity`, `kpi:d7`.
- **Apply** to small or early-stage audiences and to slow-paced games. **Avoid** when the fun depends on reacting to the opponent in real time.

## 5. Meta and progression patterns

### P21. Meta-renovation over a puzzle core
- **Definition.** Wins in a short puzzle core earn a currency that the player spends restoring or building a visible place, often with a story.
- **Mechanism.** Gives each level a "why", turns abstract wins into visible change (IKEA effect, endowed progress) and adds a narrative hook for ads.
- **Games.** Homescapes, Royal Match, Royal Kingdom (`puzzle-casual.md`), Merge Mansion, Township, Monopoly Go! landmarks, Coin Master villages (`casual-social-sim.md`).
- **Risks.** Meta art is expensive; a meta that never changes how the core plays is decoration; ad creatives must not show content the game lacks.
- **Tags.** `loop:meta/daily`, `cur:material` (stars, build progress), `psy:ikea_effect`, `psy:endowed_progress`, `mech:construction`.
- **Apply** to casual puzzle and merge games aimed at adults. **Avoid** in skill-led games whose audience wants mastery, not décor.

### P22. Production chains with order boards
- **Definition.** Raw resources are processed through chains of buildings into goods that fill visible orders.
- **Mechanism.** Self-generated goals ("I need cheese, so milk, so feed, so corn") and a constant list of next actions (Zeigarnik).
- **Games.** Hay Day, Township, Travel Town (`casual-social-sim.md` §3, §4, §6), Stardew Valley's artisan goods.
- **Risks.** Late-game chains become long and tedious; storage pressure frustrates.
- **Tags.** `node:converter`, `node:pool`, `cur:material`, `loop:core/minutes`. Tools: `economy_sim.py`.
- **Apply** to sims and tycoon metas. **Avoid** more than three or four steps in a chain for casual audiences.

### P23. Merge-to-upgrade generators
- **Definition.** Combine identical items to create the next tier; some items are generators that produce more items.
- **Mechanism.** Constant small wins, a readable tier ladder, and board space as a planning puzzle.
- **Games.** Merge Mansion, Travel Town (`casual-social-sim.md`), Threes! and 2048 (number merge), Merge Dragons! and Triple Town (merge-3).
- **Risks.** Energy cost grows exponentially (merge-2 needs 2^(n−1) base items for tier n), which pushes spending late; board clutter.
- **Tags.** `mech:merge`, `cur:energy`, `node:converter`, `psy:goal_gradient`.
- **Apply** to casual games that need a tactile core with a long tail. **Avoid** pricing energy without modelling the exponential curve.

### P24. Near-complete collections
- **Definition.** Items belong to sets, and completing a set pays a reward; the last few items are the scarcest.
- **Mechanism.** Goal-gradient and Zeigarnik intensify as the set nears completion; duplicates create trading and gifting.
- **Games.** Monopoly Go! sticker albums, Coin Master cards (`casual-social-sim.md`), Stardew Valley bundles, Pocket Camp furniture, Pokémon GO's Pokédex (`rpg-gacha-cards.md`).
- **Risks.** **High.** Paid random packs for the last items is the most exploitative pattern in casual games; grey markets. Guardrails: odds disclosure, duplicate protection, trading windows, direct-purchase paths, no paid randomness for minors (section 13).
- **Tags.** `mech:collection`, `cur:material`, `psy:goal_gradient`, `psy:zeigarnik`, `mon:iap`, `mon:ethics`.
- **Apply** with earned or deterministic sources (Stardew's bundles). **Avoid** selling random packs aimed at the final missing items.

### P25. Goal triplets
- **Definition.** Three small, varied goals are active at a time; completing a set levels up the player and refreshes the goals.
- **Mechanism.** Short-term structure inside an endless loop; variety nudges players to try different techniques (goal-gradient, competence).
- **Games.** Alto's Odyssey goals (`premium-indie.md` §1), Subway Surfers missions (`hyper-hybrid-casual.md`), Duolingo daily quests; Jetpack Joyride's missions are the classic example.
- **Risks.** Chore lists; goals that conflict with fun play.
- **Tags.** `loop:meta/daily`, `prog:tracks`, `psy:goal_gradient`.
- **Apply** to endless and arcade games. **Avoid** goals that require spending or ads.

### P26. Unlocks that widen options, not power
- **Definition.** Persistent progression adds variety (new cards, characters, rules, styles) rather than raw strength.
- **Mechanism.** Keeps every run fair and skill-based while still rewarding time (discovery, autonomy).
- **Games.** Slay the Spire, Balatro, Downwell, Shattered Pixel Dungeon (`premium-indie.md` §16.3).
- **Risks.** Less to sell in free-to-play; options that are strictly better become hidden power.
- **Tags.** `prog:tracks`, `aes:discovery`, `psy:autonomy`.
- **Apply** to premium and skill-led games. **Avoid** in free-to-play only if you have an honest alternative to sell (cosmetics, content).

### P27. Keys that reopen space
- **Definition.** A permanent ability or unlock opens new paths through content the player has already seen.
- **Mechanism.** Re-reading familiar space with new eyes (discovery); progress felt as new access, not just bigger numbers.
- **Games.** Dead Cells runes (`premium-indie.md` §7), Stardew Valley's Community Center unlocks; Hollow Knight and the metroidvania genre generally; Outer Wilds uses knowledge as the key.
- **Risks.** Backtracking tedium; players lost without guidance.
- **Tags.** `node:gate`, `prog:tracks`, `aes:discovery`, `psy:curiosity`.
- **Apply** to exploration, roguelite and sim metas. **Avoid** when the world is procedurally regenerated each run and keys have nothing to reopen.

### P28. Labelled spikes on a sawtooth
- **Definition.** Difficulty rises in waves, with periodic hard levels explicitly labelled and better rewarded, followed by relief levels.
- **Mechanism.** Labels turn spikes into challenges rather than walls; relief restores competence (flow).
- **Games.** Royal Match "hard" and "super hard" levels, Candy Crush, Toon Blast (`puzzle-casual.md`).
- **Risks.** Spikes timed to monetization moments read as paywalls; keep spikes beatable without spending.
- **Tags.** `prog:difficulty.model`, `prog:difficulty.target_win_rate`, `trig:per_level_loss`. Tools: `difficulty_curve.py generate --levels 60 --pattern sawtooth --base 0.85 --floor 0.35 --period 10 --json`.
- **Apply** to level ladders. **Avoid** unlabelled spikes; players attribute them to the game, not to themselves.

### P29. Streak with forgiveness
- **Definition.** Consecutive days or wins build a visible streak with a reward, plus a protection mechanic (freeze, repair, grace).
- **Mechanism.** Each day carries a stake (loss aversion, endowed progress); forgiveness prevents the first broken streak from becoming the churn moment.
- **Games.** Duolingo streaks and freezes (`casual-social-sim.md` §16), Royal Match's win-streak boosters (`puzzle-casual.md` §2), Wordle's streak; Snapchat streaks outside games.
- **Risks.** Anxiety and compulsive checking; selling repairs aggressively. Guardrails: free freezes, quiet notifications, generous repair.
- **Tags.** `loop:meta/daily`, `cur:material` (freezes), `psy:loss_aversion`, `psy:endowed_progress`, `kpi:d7`, `kpi:d30`.
- **Apply** to daily-habit games. **Avoid** win streaks without a cap; snowballing advantage makes matches one-sided.

### P30. Bounded day as the planning unit
- **Definition.** Play is divided into short bounded units (a day, a week, an ante) with a fixed budget of time or energy, and planning happens per unit.
- **Mechanism.** Each unit is a small optimisation puzzle with a natural stopping point; the next unit is a fresh start.
- **Games.** Stardew Valley (an energy bar and a roughly 14-minute day), Mini Metro (weekly upgrades), Balatro (antes and blinds), Reigns (years).
- **Risks.** Time pressure stresses relaxed players; offer slower modes.
- **Tags.** `loop:core/minutes`, `cur:energy`, `psy:fresh_start`, `aes:challenge`.
- **Apply** to sims and strategy games needing session shape. **Avoid** real-time clocks that keep running while the player is away unless they are forgiving (P36).

## 6. Economy and randomness patterns

### P31. Pity-protected randomness
- **Definition.** Random outcomes are bounded so bad luck cannot run indefinitely: a guarantee after N failures (hard pity), rising odds as failures accumulate (soft pity), or shuffled "bags" that deal every outcome once per cycle.
- **Mechanism.** Keeps the excitement of variable reward while capping worst-case frustration; players can plan around a ceiling.
- **Games.** Genshin Impact (published base rate and a hard pity on character banners; `rpg-gacha-cards.md`), Hearthstone (official guarantees for legendary cards early in a new set; verify current terms), Tetris (the Guideline "7-bag" randomiser deals each of the seven pieces once per bag), Slay the Spire (a community-documented offset that raises the chance of a rare card after common ones).
- **Risks.** Pity can be used to justify paid randomness ("you are guaranteed eventually"). Still disclose odds and the pity rule; still restrict paid randomness for minors and in Belgium and Brazil (section 13).
- **Tags.** `mech:chance`, `psy:variable_ratio`, `mon:ethics`. Tool: `gacha_calc.py --rate 0.006 --hard-pity 90 --pulls 90 --json` (Genshin's published base rate and hard pity, used here as an illustrative input; verify current banner rules).
- **Apply** to any repeated random reward, paid or not, and to piece generators. **Avoid** hiding the pity rule; undisclosed protection invites distrust.

### P32. Windfall core with a meta destination
- **Definition.** A highly random core (spins, dice, cascades, loot) whose results feed a persistent meta (villages, boards, collections).
- **Mechanism.** Variable-ratio reinforcement produces excitement; the meta gives each windfall a purpose and turns randomness into progress.
- **Games.** Coin Master and Monopoly Go! (`casual-social-sim.md` §1–2), Candy Crush's random refills and cascades; Diablo's loot is the action-RPG archetype.
- **Risks.** **High.** With paid energy, it approaches simulated gambling; Australia rates simulated gambling R18+ (`casual-social-sim.md` §18). Guardrails: no cash-like payouts, spend limits, age gating, odds disclosure.
- **Tags.** `mech:chance`, `psy:variable_ratio`, `cur:energy`, `mon:iap`, `mon:ethics`.
- **Apply** carefully, to adult audiences, with spend controls. **Avoid** for children's products entirely.

### P33. Stake multiplier
- **Definition.** The player chooses a multiplier that scales both the cost and the payout of each random action.
- **Mechanism.** Illusion of control (Langer, 1975) plus bigger peaks; timing the multiplier before high-value outcomes adds a pseudo-skill layer.
- **Games.** Coin Master's bet, Monopoly Go!'s roll multiplier (`casual-social-sim.md` §1–2).
- **Risks.** **High.** It is a bet in all but name and accelerates spending; press coverage of very large spending by minors attaches to this pattern. Guardrails: cap multipliers, disable for minors, show expected cost, add cool-downs.
- **Tags.** `mech:chance`, `psy:illusion_of_control`, `mon:ethics`, `cur:energy`.
- **Apply** only with the guardrails above and a `legal-ethics` review. **Avoid** in any game rated for under-18s.

### P34. Stakes-ladder matchmaking
- **Definition.** Venues or tours with rising entry fees and pots act at once as rank, matchmaking bracket and economy sink.
- **Mechanism.** One rule gives progression (prestige venues), drama (loss aversion on the entry fee) and a sink. Design arithmetic: with entry fee *f*, pot *p* and win rate *w*, expected value per match is `w·p − f`. If `p = 2f(1 − r)` with rake *r*, then a player at `w = 0.5` loses `f·r` per match on average, which is a steady sink (illustrative: *f* = 100, *r* = 0.1 gives −10 coins per match).
- **Games.** 8 Ball Pool venues, Golf Clash tours (`casual-social-sim.md` §14–15); poker apps use the same structure.
- **Risks.** Gambling-like vocabulary; broke players locked out. Guardrails: daily free coins, a bottom venue with no fee, no real-money cash-out.
- **Tags.** `node:sink`, `node:source`, `trig:per_level_win`, `trig:per_level_loss`, `psy:loss_aversion`, `mp:realtime`.
- **Apply** to 1v1 skill games. **Avoid** combining with pay-to-win equipment; the ladder then rewards spending, not skill.

### P35. Single legible currency
- **Definition.** One currency that is both earned and bought (a `hard` currency), or direct real-money pricing, instead of layered gems, tokens and shards.
- **Mechanism.** Lower cognitive load and legible prices; trust rises when players can compute value.
- **Games.** Royal Match's coins (`puzzle-casual.md` §2); Monopoly Go! and Coin Master sell dice or spins directly rather than through gems (verify current builds).
- **Risks.** Less room for price segmentation and event economies; every price is visible and comparable.
- **Tags.** `cur:hard`, `mon:iap`, `mon:ethics`.
- **Apply** to casual audiences and new studios. **Avoid** adding currencies without a sink map; each new currency needs a reason the player can state.

### P36. Forgiving absence
- **Definition.** Being away costs opportunity, never assets: crops do not wither, cities do not decay, progress waits.
- **Mechanism.** Removes the guilt and dread that cause permanent churn after a break; returning feels welcoming.
- **Games.** Hay Day's no-withering crops (versus FarmVille's withering; `casual-social-sim.md` §3), Pocket City's absence of timers, Sky's lack of loss outside Eden; idle games that accrue rewards while offline.
- **Risks.** Weaker daily pull; pair with gentle appointments (P37) or social reasons (P39).
- **Tags.** `node:pool`, `psy:loss_aversion` (deliberately not exploited), `kpi:d30`.
- **Apply** by default. **Avoid** decay mechanics unless the fiction demands them and the loss is small and recoverable.

### P37. Timers as appointments
- **Definition.** Real-time production, regeneration or unlock timers that finish while the player is away.
- **Mechanism.** Absence becomes anticipation; sessions get a natural end ("come back when it is ready") and a reason to return (commitment).
- **Games.** Hay Day production, The Sims FreePlay actions, Golf Clash and Clash Royale chest slots, Clash of Clans builders, energy in Merge Mansion and Coin Master.
- **Risks.** Waits without decisions feel like tolls; speed-ups monetize impatience. Guardrail: let players queue work before leaving; never punish absence (P36).
- **Tags.** `node:gate`, `cur:energy`, `trig:per_minute`, `loop:meta/daily`, `kpi:sessions_per_day`.
- **Apply** to sims and metas with 2–10 minute check-ins. **Avoid** timers on the core verb of skill games.

### P38. Converters that add value over time
- **Definition.** Machines or processes turn raw resources into more valuable goods after a delay.
- **Mechanism.** Investment decisions (what to convert, when) and a sense of growing wealth; converters link the core to the economy.
- **Games.** Stardew Valley's kegs and preserves jars (`premium-indie.md` §5), Hay Day and Township production buildings; idle tycoons generally.
- **Risks.** Runaway compounding inflates the economy; model sinks alongside.
- **Tags.** `node:converter`, `cur:material`, `trig:per_minute`. Tool: `economy_sim.py --model PATH --runs 200 --seed 1 --json`.
- **Apply** to sims, idle games and RPG crafting. **Avoid** converters whose output has no sink.

## 7. Social patterns

### P39. Social obligation loop
- **Definition.** Another player is waiting on you: your turn, a help request, a team contribution, a game night.
- **Mechanism.** Reciprocity and relatedness are stronger return triggers than any reward; the obligation is to a person, not the game.
- **Games.** Words With Friends ("your turn"; `casual-social-sim.md` §13), Hay Day boat help and Derby (§3), Toon Blast team lives (`puzzle-casual.md` §4), Monopoly Go! partner events, Among Us game nights.
- **Risks.** Guilt and burnout; groups collapse when key players leave. Guardrails: easy opt-out, forfeit timers, no penalty for leaving a team.
- **Tags.** `loop:social/daily`, `mp:async`, `psy:reciprocity`, `psy:relatedness`, `kpi:d30`.
- **Apply** once the core is fun solo. **Avoid** making progress impossible without friends.

### P40. Reciprocity gifting
- **Definition.** Players send each other small resources (lives, spins, hearts) at little or no cost to themselves.
- **Mechanism.** Cialdini's reciprocity: a gift creates an urge to return it; each gift is also a re-engagement message.
- **Games.** Candy Crush lives, Coin Master spins (`casual-social-sim.md` §2), Sky's hearts and candles (`premium-indie.md` §11); FarmVille's gifts defined the pattern on social networks.
- **Risks.** Notification spam; invite spam to grow the graph. Cap requests and gifts per day.
- **Tags.** `loop:social/daily`, `psy:reciprocity`, `node:source`.
- **Apply** to any game with friends lists. **Avoid** rewarding mass invitations of contacts.

### P41. Revenge loop
- **Definition.** When another player attacks, robs or beats you, the game offers a direct way to hit back.
- **Mechanism.** Loss aversion plus provocation produce a strong return trigger and a sense of justice.
- **Games.** Coin Master, Monopoly Go! (`casual-social-sim.md` §1–2), Clash of Clans (`midcore-strategy.md`).
- **Risks.** Toxicity and spirals; friendships soured. Guardrails: shields, loss caps, cool-downs, cooperative alternatives (P43).
- **Tags.** `loop:social/daily`, `mp:async`, `psy:loss_aversion`.
- **Apply** to adversarial async metas. **Avoid** targeting real friends by default; let players opt in.

### P42. Small-cohort leagues
- **Definition.** Weekly or short leaderboards among small groups of similar players (about 30), with promotion and demotion between tiers.
- **Mechanism.** A winnable race for most players (social comparison) and a weekly fresh start (Dai, Milkman and Riis, 2014).
- **Games.** Duolingo leagues (`casual-social-sim.md` §16), Royal Match's competitions (`puzzle-casual.md` §2), Golf Clash's weekly tournaments with divisions.
- **Risks.** Burnout when leagues demand grinding; bots or cheaters at the top.
- **Tags.** `loop:social/weekly`, `trig:weekly`, `psy:social_comparison`, `psy:fresh_start`, `kpi:d7`.
- **Apply** to any game with a measurable weekly activity. **Avoid** global leaderboards as the only competition; most players never place.

### P43. Fixed small-group co-op project
- **Definition.** A small, fixed group (about 2–30 players) works toward a shared goal on a timer, each contributing from their own play.
- **Mechanism.** Positive-sum relatedness and mild accountability; it balances adversarial loops.
- **Games.** Monopoly Go! partner events, Hay Day's Derby, Township's Regattas (`casual-social-sim.md`), Royal Match team battles; Clash of Clans clan wars.
- **Risks.** Freeloaders; pressure on casual members. Guardrails: personal milestones alongside group goals; no penalty for low contribution.
- **Tags.** `loop:social/weekly`, `aes:fellowship`, `psy:relatedness`, `ops:events`.
- **Apply** to any game with teams or friends. **Avoid** making the group goal impossible for small or inactive groups.

### P44. Player market
- **Definition.** Players sell goods to each other at prices they set, within limits.
- **Mechanism.** Other players become sources and sinks; trading creates specialisation and social contact.
- **Games.** Hay Day's roadside shop (`casual-social-sim.md` §3), Roblox's avatar marketplace (§9); EVE Online and the Steam Community Market at larger scale.
- **Risks.** Inflation, bots, real-money trading and scams. Guardrails: price caps, listing limits, fees as sinks, trade cool-downs.
- **Tags.** `node:source`, `node:sink`, `mech:economy`, `mp:async`.
- **Apply** to sims and collection games with many goods. **Avoid** markets in games with paid randomness; they become real-money trading hubs.

### P45. Creator economy (UGC)
- **Definition.** Players create content (experiences, levels, stories, skins) that other players consume, with tools, discovery and payouts.
- **Mechanism.** Content scales with the community; creators get status and income; players get endless novelty.
- **Games.** Roblox, Minecraft's Marketplace (`casual-social-sim.md` §9–10), Episode's writers (§12); Super Mario Maker and Fortnite's creative modes.
- **Risks.** **High.** Child safety, moderation cost, exploitation of young creators, IP infringement. Guardrails: age assurance, moderation SLAs, clear payout terms, rights checks.
- **Tags.** `loop:meta/weekly`, `aes:expression`, `mp:async`, `mon:ethics`.
- **Apply** when tools can be made simple and moderation funded. **Avoid** opening UGC to minors without a safety plan.

### P46. Hidden-role deduction
- **Definition.** Some players secretly have opposing goals; the group must deduce who they are through observation and discussion.
- **Mechanism.** Theory-of-mind play, deception and accusation create stories and humour; players generate the content.
- **Games.** Among Us (`casual-social-sim.md` §8); the Mafia (1986) and Werewolf party games.
- **Risks.** Needs groups; public lobbies attract toxicity and cheating; typing on phones is slow.
- **Tags.** `mp:realtime`, `aes:fellowship`, `mech:social`.
- **Apply** to party games with friends and streamers. **Avoid** relying on public matchmaking without moderation and quick chat.

### P47. Spoiler-free shareable artefact
- **Definition.** The game produces an image or summary that shows how the player did without spoiling the content.
- **Mechanism.** Social proof and curiosity; each share is free distribution.
- **Games.** Wordle's coloured grid (`premium-indie.md` §13), Monument Valley's screenshot-worthy screens, Among Us clips, Minecraft builds.
- **Risks.** Sharing prompts that nag; artefacts that leak answers.
- **Tags.** `ux:screens`, `psy:social_proof`, `psy:curiosity`.
- **Apply** to daily puzzles, runs and level results. **Avoid** forcing sharing for rewards; it reads as spam.

### P48. Consent-gated communication
- **Definition.** Free communication unlocks only through mutual consent (friendship, age checks); before that, players use emotes or preset phrases.
- **Mechanism.** Safety and progression at once: communication becomes something earned together.
- **Games.** Sky's friendship trees (`premium-indie.md` §11), Among Us quick chat, Golf Clash's emoji-only chat, Roblox's age-gated chat; Journey had no chat at all.
- **Risks.** Frustrates groups of real friends; needs fast paths for verified friends.
- **Tags.** `mp:async`, `mp:realtime`, `ux:accessibility`, `aes:fellowship`.
- **Apply** to any game with strangers and young players. **Avoid** open text chat by default for mixed-age audiences.

### P49. Light-touch presence
- **Definition.** Other players are visible without demanding interaction: avatars on a map, anonymous strangers, ghosts, traces.
- **Mechanism.** A sense of shared world (relatedness, social proof) without coordination costs or social pressure.
- **Games.** Sky's anonymous strangers, Candy Crush's friend avatars on the saga map (`puzzle-casual.md` §1), Among Us ghosts; Journey and Dark Souls' messages are the classic examples.
- **Risks.** Feels empty at low population; fake presence (bots disguised as players) erodes trust.
- **Tags.** `mp:async`, `aes:fellowship`, `psy:social_proof`.
- **Apply** to single-player-first games that want warmth. **Avoid** presenting bots as real players.

## 8. Live-ops and time patterns

### P50. Seasonal resets
- **Definition.** Some progress (albums, leagues, passes, ladders) resets on a fixed cycle, while permanent progress persists.
- **Mechanism.** Fresh starts for lapsed and losing players, renewed goals for veterans, and a calendar heartbeat for the studio.
- **Games.** Monopoly Go! album seasons, Sky's seasons, Duolingo's weekly leagues (`casual-social-sim.md`, `premium-indie.md`); Clash Royale and Fortnite seasons.
- **Risks.** Resets that wipe purchased value feel like theft; keep paid items permanent.
- **Tags.** `loop:liveops/season`, `ops:cadence`, `psy:fresh_start`, `kpi:d30`.
- **Apply** to any live game with competitive or collection layers. **Avoid** resetting core progression.

### P51. Season pass (free + paid tracks)
- **Definition.** A time-limited reward track advanced by play, with a free lane and a paid lane.
- **Mechanism.** Transparent, non-random value (players see every reward before buying); goal-gradient across the season; a strong price anchor.
- **Games.** Royal Match's pass (`puzzle-casual.md` §2), 8 Ball Pool's Pool Pass (`casual-social-sim.md` §14), Sky's season passes; Fortnite popularised the model.
- **Risks.** FOMO pressure; passes that need near-daily play to finish. Guardrails: completable with moderate play; catch-up mechanics.
- **Tags.** `mon:pass`, `loop:monetization/season`, `psy:goal_gradient`, `kpi:payer_conversion`.
- **Apply** to any live game; it is the safest mainstream paid product regarding loot-box rules. **Avoid** stacking several passes at once.

### P52. Overlapping event cadence
- **Definition.** Several events with staggered timers run at once, so one is always close to paying out.
- **Mechanism.** Constant near-term goals (goal-gradient) and urgency; each session has a "why now".
- **Games.** Monopoly Go!, Coin Master (`casual-social-sim.md` §1–2), Royal Match (`puzzle-casual.md` §2), Township.
- **Risks.** Urgency fatigue, cluttered UI, FOMO. Guardrail: cap concurrent events (three or four), use a calm visual hierarchy.
- **Tags.** `ops:events`, `ops:cadence`, `loop:liveops/daily`, `psy:scarcity`.
- **Apply** to mature live games with a content pipeline. **Avoid** before the core and meta retain on their own.

### P53. Rotating returns of limited content
- **Definition.** Limited items or characters return on a rotation instead of disappearing forever.
- **Mechanism.** Keeps desirability while softening fear of missing out; returning content is cheap live-ops.
- **Games.** Sky's Traveling Spirits (`premium-indie.md` §11); banner reruns in Genshin Impact (`rpg-gacha-cards.md`); Fortnite's rotating item shop.
- **Risks.** Unpredictable rotations recreate FOMO; publish schedules where possible.
- **Tags.** `ops:events`, `psy:scarcity` (softened), `mon:iap`.
- **Apply** to cosmetic and collection catalogues. **Avoid** "never again" exclusivity on paid items.

### P54. Re-theming on a stable core
- **Definition.** Live-ops refresh the setting (cities, seasons, boards) while keeping the core verb unchanged.
- **Mechanism.** Novelty at low production cost; returning players feel change without relearning.
- **Games.** Subway Surfers' World Tour (`hyper-hybrid-casual.md` §5), Monopoly Go!'s themed boards, Pokémon GO's event themes (`rpg-gacha-cards.md`).
- **Risks.** Theme fatigue if mechanics never evolve; add small rule twists periodically.
- **Tags.** `ops:events`, `ops:cadence`, `aes:discovery`.
- **Apply** to any game whose art pipeline can produce themes on a cadence. **Avoid** themes that change readability (new palettes that hide hazards).

### P55. Free major updates for a premium tail
- **Definition.** A premium game receives substantial free updates over years.
- **Mechanism.** Each update renews press coverage, store featuring and sales, and builds goodwill that drives word of mouth.
- **Games.** Stardew Valley, Slay the Spire (`premium-indie.md`), Minecraft (`casual-social-sim.md` §10); Terraria is the widely cited PC example.
- **Risks.** No direct revenue per update; developer burnout. Pair with paid DLC or new platforms where appropriate (Dead Cells).
- **Tags.** `ops:cadence`, `mon:ethics`, `kpi:d30`.
- **Apply** to premium games with an engaged community. **Avoid** promising updates the team cannot deliver.

### P56. Graceful service sunset
- **Definition.** When a live game ends, players keep their investment: an offline edition, save export, or released server code.
- **Mechanism.** Protects trust in the studio and brand; reduces the reputational cost of ending a service.
- **Games.** Animal Crossing: Pocket Camp's offline *Complete* edition (`casual-social-sim.md` §7); Shattered Pixel Dungeon's open source means it cannot be switched off.
- **Risks.** Engineering cost of an offline mode; licensing constraints on server code.
- **Tags.** `ops:cadence`, `mon:ethics`, `field:technical.backend` (plan an offline-capable architecture).
- **Apply** to any game with server dependence. **Avoid** designs that make an offline mode impossible (all logic on the server) unless you accept a hard shutdown.

## 9. Identity and positioning patterns

### P57. Atmosphere-first identity
- **Definition.** Art, audio and mood are the core value, and the mechanic serves the atmosphere.
- **Mechanism.** Sensation and awe create memorable, shareable experiences that marketing alone cannot buy.
- **Games.** Alto's Odyssey, Monument Valley, Sky, Mini Metro (generative audio), Florence (`premium-indie.md`).
- **Risks.** Beauty without depth wears off; high art cost per minute of play.
- **Tags.** `aes:sensation`, `aes:submission`, `field:art_direction`, `field:audio_direction`.
- **Apply** to premium and relaxing games. **Avoid** in games sold on depth, where atmosphere should support rather than lead.

### P58. Failure-optional mode
- **Definition.** A mode that removes failure, score or timers so players can simply enjoy the activity.
- **Mechanism.** Serves a different motivation (relaxation, expression) at almost no cost and widens accessibility.
- **Games.** Alto's Zen Mode, Minecraft's creative mode, Mini Metro's creative mode, Monument Valley's fail-free design; Celeste's assist mode is the widely praised accessibility example.
- **Risks.** Undermines challenge-based rewards if unlocks are shared; keep progression separate.
- **Tags.** `ux:accessibility`, `aes:submission`, `aes:expression`.
- **Apply** to arcade, sim and puzzle games. **Avoid** only in competitive modes.

### P59. Positioning by refusal
- **Definition.** Publicly not doing what the genre norm does (no timers, no IAP, no ads, no monetization at all) and making that the message.
- **Mechanism.** Trust and differentiation for players tired of free-to-play norms; word of mouth from goodwill.
- **Games.** Pocket City (no timers, no IAP; `premium-indie.md` §14), Wordle (no monetization at launch), Shattered Pixel Dungeon (free, open source, supporter purchases only); Royal Match launched without forced ads (`puzzle-casual.md` §2).
- **Risks.** Smaller revenue per player; the promise is hard to reverse later.
- **Tags.** `mon:ethics`, `field:meta.pillars` (state it as a pillar).
- **Apply** when competitors' monetization is a known pain point. **Avoid** if you may need to add the refused mechanic later; broken promises cost more than the revenue.

## 10. Pattern stacks: proven combinations by archetype

| Archetype | Stack | Anchor cases | Watch |
|---|---|---|---|
| Social-casino-adjacent | P32 + P33 + P41 + P24 + P52 + P40 + P43 | Coin Master, Monopoly Go! | Every high-risk pattern at once; full ethics screen |
| Renovation puzzle | P10 + P05 + P21 + P28 + P29 + P42 + P51 + P37 (lives) | Royal Match, Homescapes | Spikes at spend moments |
| Merge | P23 + P22 + P21 + P37 + narrative hook | Merge Mansion, Travel Town | Exponential energy cost |
| Farming / production | P22 + P38 + P36 + P37 + P43 + P44 | Hay Day, Township | Late-chain tedium, storage walls |
| Hybrid-casual | P03 + P02 + P11 + P12 + P37 (energy) + P51 | Archero, Survivor.io | Gear walls |
| Premium roguelite | P11 + P12 + P06 + P07 + P15 + P16 + P26 + P01 | Slay the Spire, Balatro, Dead Cells | Keep power meta small |
| Premium authored | P10 + P08 + P57 + P58 + P47 | Monument Valley, Florence, Alto's Odyssey | Length versus price |
| Daily ritual | P16 + P47 + P29 + P09 | Wordle, Duolingo | Streak anxiety |
| Short PvP | P19 or P20 + P34 + P37 (chests) + P42 + P51 | Golf Clash, 8 Ball Pool | Pay-to-win stats |
| UGC sandbox | P45 + P44 + P48 + P47 + P49 | Roblox, Minecraft | Safety and moderation |
| Gentle social service | P48 + P40 + P49 + P53 + P50 + P57 | Sky | Currency sprawl |

Use a stack as a starting hypothesis, then change one or two patterns (the "twist" from Core model 1 in `SKILL.md`).

## 11. Conflicts and interactions

| Pattern A | Pattern B | Conflict | Resolution |
|---|---|---|---|
| P37 Timers as appointments | P01 One-more-turn | Timers end sessions; one-more-turn extends them | Pick one per layer: timers on the meta, one-more-turn on the core; never sell energy to extend a binge |
| P29 Streak | P36 Forgiving absence | Streaks punish absence | Freezes, repair, grace days |
| P11 Run + meta (power) | P26 Options, not power | A power meta breaks fair runs | Premium: options; free-to-play: cap power per chapter and show non-payer timelines |
| P19 Synchronous duels | Small audience | Matchmaking needs concurrency | Start with P20 (async) or labelled bots |
| P52 Overlapping events | P09 Abstraction | Event clutter destroys readability | Cap concurrent events; one event surface |
| P45 Creator economy | P48 Consent-gated communication | UGC spaces need communication; safety needs gating | Age assurance plus experience-level chat rules |
| P06 Multiplicative scoring | Readability | Huge numbers become noise | Step-by-step scoring animation; notation for large numbers |
| P13 Growing pressure | Mobile interruptions | A phone call can end a run | Pause anywhere; auto-pause on background |
| P24 Collections | P31 Pity | Pity can be used to justify paid packs | Pity plus earned sources plus direct purchase; no paid randomness for minors |
| P33 Stake multiplier | P59 Positioning by refusal | Incompatible promises | Choose one; a stake multiplier rules out an "ethical" positioning |

## 12. Procedure: selecting patterns for a concept

1. **Frame.** Write the player fantasy, target audience and session shape (`contract.meta.player_fantasy`, `meta.target_audience`, `meta.session_length_target_sec`).
2. **One or two patterns per clock.** From the index, choose for seconds (feel), minutes (core), days (meta) and months (live-ops). A missing clock is a gap to justify, not to ignore.
3. **Start from a stack** (section 10) if one fits; note which pattern is your twist.
4. **Check conflicts** (section 11) and resolve each in writing.
5. **Run the ethics screen** (section 13). Any high-risk pattern needs a guardrail entry in `contract.monetization.ethics` and a `legal-ethics` review.
6. **Encode.** Convert each pattern's tags into contract entries (loops, currencies, KPIs). Search the knowledge base with `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py kb "streak forgiveness" --skill game-case-studies --limit 5`.
7. **Hypothesis per pattern.** For each pattern, write the KPI it should move and by how much, then size the test (`ab_test.py size --baseline 0.20 --mde 0.02`).
8. **Record precedents** in `contract.meta.comparables` as `{title, borrow, change}`.

**Worked example: "Tidekeeper", a daily light-routing puzzle with a harbour-restoration meta (illustrative concept).**

| Clock | Pattern chosen | Why |
|---|---|---|
| seconds | P04 Touch-native verb (drag mirrors to route a beam), P05 Juice the verb | Mobile-first feel; the beam lighting the target is the payoff |
| minutes | P10 Authored "aha", solver-verified; P28 Labelled spikes | Deterministic optics puzzles can be verified with a solver |
| days | P21 Meta-renovation (restore the harbour); P16 Daily seed + P47 Share grid; P29 Streak with forgiveness | A "why" for levels; a daily shared puzzle for organic reach |
| months | P50 Seasonal resets (tide seasons with new mechanics); P51 Season pass | Calendar heartbeat; transparent paid product |
| ethics | P36 Forgiving absence (no energy); P59 Positioning by refusal (no paid randomness) | Fits an older casual audience that distrusts timers |

Conflict check: P29 versus P36 resolved with free weekly streak freezes. Contract fragment:

```json
{"loops": [
  {"id": "tk_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "drag_mirrors_to_route_beam", "reward": "beam_feedback", "next": "c2"},
    {"id": "c2", "action": "light_all_targets", "reward": "stars", "next": "c3"},
    {"id": "c3", "action": "spend_stars_on_harbour_task", "reward": "harbour_restoration", "next": "c1"}]},
  {"id": "tk_daily", "type": "liveops", "period": "daily", "steps": [
    {"id": "l1", "action": "solve_daily_tide_puzzle", "reward": "streak_plus_one", "next": "l2"},
    {"id": "l2", "action": "share_spoiler_free_grid", "reward": "social_reach", "next": "l1"}]}],
 "economy": {"currencies": [
  {"id": "stars", "kind": "material", "sources": ["level_win"], "sinks": ["harbour_tasks"], "cap": null},
  {"id": "hints", "kind": "hard", "sources": ["iap", "daily_gift"], "sinks": ["reveal_mirror"], "cap": null},
  {"id": "streak_freezes", "kind": "material", "sources": ["weekly_grant"], "sinks": ["missed_day_protection"], "cap": 2}]},
 "analytics": {"kpi_targets": {"d1": null, "d7": null, "d30": null}}}
```
KPI targets stay `null` until benchmarks are chosen with `market-intel` and `player-analytics`; never copy a number from another game without context.

## 13. Ethics screen

Run this screen for every concept. Patterns rated **high** or **medium** in the index need the listed guardrail recorded in `contract.monetization.ethics`.

| Pattern | Risk | Required guardrail | Check |
|---|---|---|---|
| P32 Windfall core, P33 Stake multiplier | Simulated gambling; minors' spending | Age gating, spend limits, multiplier caps, no cash-like payouts | Australia's R18+ simulated-gambling rule (`casual-social-sim.md` §18); `legal-ethics` |
| P24 Collections with paid random packs, P31 Pity | Loot-box law; pressure at the last item | Odds and pity disclosure, duplicate protection, direct-purchase path, no paid randomness for minors | Belgium (paid loot boxes treated as gambling), Brazil (under-18 ban from March 2026), store odds-disclosure rules |
| P29 Streaks, P39 Obligation, P52 Events | Anxiety, compulsive checking, FOMO | Forgiveness, notification caps and quiet hours, capped concurrent events | `liveops` CRM rules |
| P41 Revenge, P20 Async PvP | Toxicity, harassment | Shields, loss caps, opt-in targeting of friends, reporting | `multiplayer-backend` moderation |
| P45 UGC, P46 Hidden roles, P44 Market | Child safety, scams, real-money trading | Age assurance, consent-gated chat (P48), moderation, trade limits | Amended COPPA Rule (compliance from April 2026); store rules |
| P34 Stakes ladder, P19 Duels | Pay-to-win, gambling vocabulary | Stat caps per tier, free daily entry, no cash-out | `monetization` fairness rules |
| P28 Spikes, P01 One-more-turn | Spend traps at frustration peaks | Spikes beatable without spending; no offers at exit points | `difficulty_curve.py analyze` on telemetry |

Then run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/compliance_preflight.py --project DIR --platform all --json` before soft launch, and have `arcosian:compliance-officer` review any concept that uses three or more high-risk patterns. Regulatory details change; the dated facts and sources are in `casual-social-sim.md` §18 and in `legal-ethics`.
