# Player Research Methods

How the studio learns what players actually experience: choosing the right method for the question, running playtests (moderated, think-aloud, RITE, unmoderated, diary, FTUE and persona-agent tests), sample sizes with the formulas behind them, survey design and validated scales (PENS, BANGS, GEQ, PXI, IMI and others, with licence notes), interviews, heuristic evaluation (general and game-specific sets plus the studio's own mobile set), triangulating qualitative findings with telemetry, evidence-based personas, jobs-to-be-done for games, reporting into `playtest-report.schema.json`, and research ethics including minors. Doctrine item 4 — data-informed, not data-driven — is practised here: hypotheses first, then the cheapest method that can falsify them. `skills/player-psychology/scripts/psych_check.py` computes problem-discovery sample sizes, survey margins of error and scale reliability (Cronbach's alpha).

## Contents

1. Choosing a method
2. Planning a study: questions, recruitment, consent
3. Playtest protocols
4. Sample sizes
5. Survey design
6. Validated scales and licences
7. Interviews
8. Heuristic evaluation
9. Telemetry triangulation
10. Personas
11. Jobs-to-be-done for games
12. Biometrics and lab methods (when they are worth it)
13. Reporting findings into the ontology
14. Research ethics and minors
15. Sources

---

## 1. Choosing a method

Two axes organise research methods (a framing popularised by Christian Rohrer at Nielsen Norman Group): **attitudinal vs behavioural** (what people say vs what they do) and **qualitative vs quantitative** (why/how vs how many/how much). Behaviour beats opinion for questions about fun and usability; attitudes matter for motivation, perception of fairness and willingness to recommend.

| Question | Best method | Typical n | Turnaround | Output |
|---|---|---|---|---|
| Can players understand and operate this? | Moderated usability playtest with think-aloud | 5–8 per segment per round | Days | Usability issues with severity |
| Is the FTUE teaching the core loop? | FTUE playtest + funnel telemetry | 6–10 per round; funnel at scale | Days | Drop points, misconceptions |
| Is this fun / do they want to keep playing? | Observation of voluntary continuation + retrospective interview | 8–15 | 1–2 weeks | Engagement signals, quotes |
| Which of two versions performs better? | A/B test | From power analysis (`ab_test.py size`) | Weeks | Effect size with CI |
| Why do players churn at day 3? | Telemetry cohort analysis → churned-player interviews or survey | Telemetry at scale; 8–12 interviews | 1–3 weeks | Causal hypotheses |
| What motivates our players? | Validated motivation/needs scale + interviews | 100–300+ for a scale; 8–12 interviews | 2–4 weeks | Motivation profile per segment |
| How do players perceive our monetisation? | Survey with fairness/endorsement items + interviews | 200+ for segment comparisons | 2–3 weeks | Perception scores, verbatims |
| What should we build next? | JTBD interviews + market-intel | 10–20 | 2–4 weeks | Job map, opportunities |
| Is the UI obviously broken before we test with people? | Heuristic evaluation | 3–5 evaluators | Hours–days | Heuristic violations with severity |
| Is the experience consistent over weeks? | Diary study | 10–20 | 2–4 weeks | Longitudinal patterns |
| Rough friction scan of a build, cheaply | Persona-agent playtest (`arcosian:player-simulator`) | 5–20 agent runs | Hours | Friction hypotheses (not fun evidence) |

**Rules.**
- Write the decision the research will inform before choosing the method. Research without a decision is a report nobody reads.
- Prefer behaviour over stated preference for fun, usability and willingness to pay. Never ask "would you pay for this?" and treat the answer as data.
- Use the cheapest method that can falsify the hypothesis. Heuristic review before playtest; playtest before A/B test.

---

## 2. Planning a study: questions, recruitment, consent

### 2.1 Research plan (one page)
1. **Decision** this study informs (e.g. "ship FTUE v2 or iterate").
2. **Research questions** (3–5), each answerable by observation or measurement.
3. **Hypotheses** with what would falsify them.
4. **Method and protocol**; tasks and free-play segments.
5. **Participants**: segment, screener criteria, n, exclusions.
6. **Metrics**: behavioural (completion, time, errors, retries, voluntary continuation), attitudinal (scales, ratings).
7. **Schedule, roles** (moderator, note-taker), **materials** (build version, devices).
8. **Ethics**: consent form, recording, data retention, incentives, minors.

### 2.2 Recruitment
- Recruit from the **target segment** defined in `contract.meta.target_audience` — play habits, genres played in the last month, device type, session context — not from colleagues, friends or developers.
- Screener questions should not reveal the "right" answer (ask "Which of these games have you played in the past month?" with a list including decoys, not "Do you like puzzle games?").
- Include **device realism**: test on mid- and low-tier devices in the target market, in portrait/landscape as shipped.
- Over-recruit by ~20% for no-shows.
- Exclude professional testers and people who have played earlier builds (unless the study is longitudinal).
- Compensation should be fair and not tied to giving positive feedback.

### 2.3 Consent essentials
Informed consent covering purpose, recording, data use and retention, right to stop at any time without losing compensation, and confidentiality obligations (NDA) if any. Minors: see §14.

---

## 3. Playtest protocols

### 3.1 Moderated usability playtest (one-on-one)
**Use for:** comprehension, controls, FTUE, UI flows, early fun signals. 45–60 minutes.

| Phase | Time | What happens |
|---|---|---|
| Welcome and consent | 5 min | Explain that the game is being tested, not the participant; consent; recording on |
| Background | 5 min | Play habits, context of mobile play (where, when, how long) |
| First impression | 2–3 min | Store page or icon shown; "What do you expect this game to be?" |
| Cold start | 10–15 min | Fresh install; play from launch with no instruction; think-aloud on |
| Tasks | 10–15 min | Specific goals ("Find a way to upgrade your golem"), observe success/failure/time |
| Free play | 10 min | "Play as you would at home"; observe whether they choose to continue |
| Debrief | 5–10 min | Retrospective questions; optional scale |

**Moderator rules.**
- Do not help, explain or defend. If asked, reflect: "What would you try?" Intervene only if stuck for > 2–3 minutes on something irrelevant to the research question, and log the intervention.
- Neutral prompts: "What are you thinking?", "What do you expect to happen?", "Tell me more about that."
- Never ask leading questions ("Was that fun?"). Ask "How would you describe that level to a friend?"
- Note behaviour first, quotes second: hesitation, repeated taps, wrong taps, facial expressions, posture shifts, sighs, smiles, leaning in.

**Observation log format** (one row per event; becomes `findings[]`):
`timestamp | screen | behaviour observed | participant quote | interpretation | severity`

### 3.2 Think-aloud
Concurrent verbal reporting (Ericsson & Simon, *Protocol Analysis*, 1984/1993) asks participants to say what they are thinking as they play.

| Variant | Strength | Weakness | Use for |
|---|---|---|---|
| Concurrent think-aloud | Captures expectations and confusion in the moment | Slows play; disrupts fast action; some participants go silent | Puzzle, strategy, menus, FTUE |
| Retrospective think-aloud (cued by replay video) | Natural play; good for action | Memory reconstruction; rationalisation | Action, timing-critical, competitive play |
| Co-discovery (two players together) | Natural conversation | Dominant partner effect | Social and co-op games; children |

Keep prompts minimal ("Keep talking") so the method stays close to pure verbalisation. Do not interpret think-aloud speech as a measure of fun; it measures comprehension and expectation.

### 3.3 RITE (Rapid Iterative Testing and Evaluation)
Developed at Microsoft Game Studios (Medlock, Wixon, Terrano, Romero & Fulton 2002, describing work on the *Age of Empires II* tutorial). The team **changes the build between participants** as soon as an issue's cause and fix are clear, rather than waiting until all sessions finish.

**Procedure.**
1. Decision-makers (designer, engineer who can change the build) watch every session.
2. After each participant, review issues: if the cause is clear and the fix cheap, fix before the next participant.
3. Track each issue: first seen, fix applied, whether it recurred after the fix.
4. Continue until a set number of consecutive participants (e.g. 3) complete the target flow without critical issues.

| Issue | P1 | P2 | P3 | Fix after | P4 | P5 | P6 | Status |
|---|---|---|---|---|---|---|---|---|
| Doesn't discover drag-to-merge | ✗ | ✗ | — | P2: ghost-hand animation | ✓ | ✓ | ✓ | Fixed |
| Misreads star cost in the keep | ✗ | ✓ | ✗ | P3: larger cost label | ✓ | ✗ | ✓ | Monitoring |

**When to use:** FTUE, tutorials, UI flows — anywhere fixes are cheap and the goal is to *remove* problems, not to measure them. **Not for** measuring prevalence or comparing versions.

### 3.4 Unmoderated remote playtests
Participants play on their own devices while screen (and optionally face and voice) are recorded, following written prompts. Cheaper and more natural context; less control and no follow-up questions. Use for FTUE comprehension at larger n (10–30), first-impression and store-page tests. Write prompts as goals, never instructions ("Try to make your keep look nicer" not "Tap the hammer icon").

### 3.5 FTUE test (studio protocol)
1. Fresh install, no instruction, on a target-tier device.
2. Measure: time to first meaningful action, time to aha (target: `contract.ftue.aha_seconds_target`), time per FTUE step vs `max_seconds`, errors per step, skips.
3. At the end of the FTUE, ask the participant to **explain the game's goal and core loop in their own words**. Score: correct / partial / wrong. Target: ≥ 80% correct.
4. Ask "What would you do next?" — tests whether the meta goal is visible.
5. Offer a natural stop: "You can stop here or keep playing for a few minutes, it's up to you." Record whether they continue (voluntary continuation is the strongest early fun signal).

### 3.6 Diary and longitudinal studies
10–20 participants play at home for 1–4 weeks and log short entries (when they played, why they opened the game, how they felt, why they stopped). Pair with telemetry for the same players (with consent). Best for retention reasons, notification perception, monetisation perception over time and habit formation.

### 3.7 Group playtests
Large sessions with surveys after play give scale quickly but suffer from social influence (people react to others' reactions) and limited observation. Use for quick preference reads and balancing feedback; never as a substitute for one-on-one usability observation. Avoid focus groups for usability questions.

### 3.8 Persona-agent playtests (`arcosian:player-simulator`)
LLM-driven agents play builds as defined personas and report friction. They are useful for:
- Finding broken flows, unclear text, dead ends and missing feedback quickly and repeatedly.
- Regression checks on FTUE comprehension against written rules.

They are **not** evidence of fun, motivation, emotional response or willingness to pay, and they do not replace human playtests at the human checkpoints (doctrine item 10). Report agent findings as hypotheses with `mode: "persona"` in the playtest report; confirm the important ones with humans.

---

## 4. Sample sizes

### 4.1 Problem discovery (qualitative usability)
The probability that a problem affecting a proportion *p* of users is seen at least once with *n* participants is `1 − (1 − p)^n` (Nielsen & Landauer 1993; Virzi 1992). Nielsen and Landauer's average *p* across projects was about 0.31, which gives the famous "five users find about 85% of problems". The catch: **that only holds for problems that affect ~31% of users**. Rarer problems need more participants, and *p* varies widely between products and participants (Faulkner 2003 showed large variation across random samples of five).

**Participants needed** to see a problem at least once (`n = ln(1 − D) / ln(1 − p)`):

| Problem frequency p | 80% chance | 85% | 90% | 95% |
|---|---|---|---|---|
| 0.31 | 5 | 6 | 7 | 9 |
| 0.15 | 10 | 12 | 15 | 19 |
| 0.10 | 16 | 19 | 22 | 29 |
| 0.05 | 32 | 37 | 45 | 59 |

Compute with `python3 ${CLAUDE_PLUGIN_ROOT}/skills/player-psychology/scripts/psych_check.py discovery --p 0.1 --target 0.85`.

**Studio rules.**
- **5–8 participants per distinct segment per round**, then fix and run another round. Three rounds of 5 beat one round of 15 for finding and fixing problems.
- Segments that play differently (e.g. puzzle veterans vs genre newcomers) each need their own participants.
- Qualitative studies estimate *which* problems exist, not *how many* players have them. Do not report "40% of players were confused" from 5 people; report "2 of 5".

### 4.2 Surveys (estimating a proportion)
Margin of error at 95% confidence for a proportion: `e = 1.96 · √(p(1 − p) / n)`. Required n for a target margin: `n = 1.96² · p(1 − p) / e²`. With the worst case *p* = 0.5:

| Margin of error (±) | n needed |
|---|---|
| 10 points | 97 |
| 5 points | 385 |
| 3 points | 1,068 |
| 2 points | 2,401 |

Finite population correction when sampling a small player base of size *N*: `n_adj = n / (1 + (n − 1) / N)` — e.g. 385 becomes ~323 for a 2,000-player soft-launch cohort. Margins apply **per subgroup**: comparing 4 segments at ±10 points needs ~97 *each*.

Command: `psych_check.py moe --n 200` or `psych_check.py moe --margin 0.05 --population 2000`.

**Non-response bias matters more than n.** In-game surveys over-represent engaged players; churned players rarely answer. Weight by segment or survey churned players separately (email or store-review analysis), and always report the response rate.

### 4.3 Comparing groups and A/B tests
Use power analysis, not rules of thumb: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ab_test.py size --baseline 0.30 --mde 0.02` for proportions (e.g. D1 retention), `ab_test.py mean ...` for continuous metrics, `ab_test.py sequential ...` if you will peek. Decide primary metric, minimum detectable effect and stopping rule before starting (`player-analytics`).

### 4.4 Other rules of thumb (verify for your study)
| Method | Typical n | Basis |
|---|---|---|
| Semi-structured interviews (homogeneous group, focused question) | 9–17 to reach thematic saturation; plan ~12 | Guest, Bunce & Johnson 2006; Hennink & Kaiser 2022 review |
| Heuristic evaluation | 3–5 evaluators | Nielsen (1990s): single evaluators miss most issues; five find roughly three quarters |
| Card sorting (menu/shop IA) | ~15+ | Tullis & Wood 2004 |
| Scale reliability check (Cronbach's α) | 30+ pilot; 100+ for stable estimates | General psychometric practice |
| Validating a new scale (factor analysis) | 200–300+ | General psychometric practice |
| Diary study | 10–20 | Practitioner norm, allowing dropout |

---

## 5. Survey design

### 5.1 Item-writing rules
- One idea per item (no "The game is fun and easy to learn").
- Neutral wording; no leading or loaded terms ("How much did you enjoy..." presumes enjoyment; use "How would you rate...").
- Balanced response scales with labelled anchors; 5- or 7-point Likert scales are standard; keep the same direction throughout a block.
- Ask about specific, recent behaviour ("In the past 7 days, how many days did you play?") rather than habits in general.
- Avoid hypotheticals about future behaviour and prices.
- Put sensitive questions (spending, demographics) late; make them optional.
- Include an attention check in long surveys and remove straight-liners.
- Randomise item order within blocks when order effects are plausible.
- Pilot with 5 people and ask them to think aloud while answering.

### 5.2 In-game micro-surveys
- One question, one tap, at a natural break (after a results screen, after an event ends), sampled (e.g. 5–10% of eligible sessions), and never more than once per week per player.
- Good micro-survey items: end-of-level feeling (5 faces), "How fair did that level feel?", "Glad you spent?" after purchases (sampled), "How likely are you to play tomorrow?" (weak predictor; use for trend only).
- Never reward survey answers with currency proportional to positive answers; a flat token thank-you is acceptable but biases toward engaged players — note it.

### 5.3 About NPS
Net Promoter Score (one "likelihood to recommend" item) is widely used for executive reporting but has been criticised for poor diagnostic value and statistical noise at small n. If used, report the full distribution and confidence interval, and pair it with diagnostic items.

---

## 6. Validated scales and licences

Validated scales let results be compared across builds and with published research. Use them **unchanged** (wording, order, scale points); changing items breaks validity. Translations require forward–back translation and ideally re-validation.

**Licence notes are best-effort and change; confirm terms with the scale owner before commercial use.**

| Scale | Measures | Size | Origin | Licence / access notes |
|---|---|---|---|---|
| **PENS** (Player Experience of Need Satisfaction) | Competence, autonomy, relatedness, presence/immersion, intuitive controls | ~21 items (verify current version) | Ryan, Rigby & Przybylski 2006; Immersyve | Proprietary (Immersyve); commercial use reportedly requires a licence — verify |
| **BANGS** (Basic Needs in Games Scale) | Satisfaction *and* frustration of autonomy, competence, relatedness in games | Multi-item, with subscales for satisfaction and frustration | Ballou, Denisova, Ryan, Rigby & Deterding, CHI 2024 | Published openly with the paper; check stated licence before commercial use |
| **GEQ** (Game Experience Questionnaire) | Competence, immersion, flow, tension, challenge, negative and positive affect; in-game and post-game modules | Core module 33 items; short in-game version | IJsselsteijn, de Kort & Poels (Eindhoven University of Technology; published 2013, circulated earlier) | Widely distributed for research; **psychometric problems reported** (Law, Brühlmann & Mekler 2018 found its factor structure did not replicate) — use with caution, prefer PXI or BANGS for new studies |
| **PXI** (Player Experience Inventory) | Functional consequences (e.g. ease of control, goals and rules, challenge, progress feedback, audiovisual appeal) and psychosocial consequences (mastery, curiosity, immersion, autonomy, meaning), plus enjoyment | 30 items + enjoyment; mini-PXI (one item per construct) exists | Abeele, Spiel, Nacke, Johnson & Gerling 2020 (*IJHCS*); mini-PXI by Haider et al. 2022 | Published openly; check licence on the official PXI materials |
| **IMI** (Intrinsic Motivation Inventory) | Interest/enjoyment, perceived competence, effort, pressure/tension, choice, value | Flexible subsets | SDT research tradition (selfdeterminationtheory.org) | Available for academic research via the SDT site; check commercial terms |
| **UEQ** (User Experience Questionnaire) | Attractiveness, perspicuity, efficiency, dependability, stimulation, novelty | 26 items; UEQ-S 8 items | Laugwitz, Held & Schrepp 2008 | Free to use per the UEQ site; verify |
| **SUS** (System Usability Scale) | Perceived usability (single score 0–100) | 10 items | Brooke 1996 | Free with attribution; better for menus/tools than for gameplay |
| **NASA-TLX** | Workload: mental, physical, temporal demand, performance, effort, frustration | 6 subscales | Hart & Staveland 1988 | Freely available from NASA |
| **IEQ** (Immersive Experience Questionnaire) | Immersion (cognitive and emotional involvement, real-world dissociation, challenge, control) | 31 items | Jennett et al. 2008 | Academic; check access terms |
| **Flow State Scale (FSS-2)** and short forms | Flow dimensions | 36 items; short forms exist | Jackson & Marsh 1996; Jackson & Eklund 2002 | Commercially distributed — verify licence |
| **WHO-5 Well-Being Index** | General wellbeing | 5 items | World Health Organization | Reportedly free to use; verify current terms |

**Studio endorsement items (original; free to use within the studio).** 7-point agreement, administered after ≥ 1 week of play:
1. I feel good about the time I spend playing this game.
2. I feel good about the money I have spent in this game. *(payers only)*
3. I sometimes keep playing when I would rather be doing something else. *(reverse-scored)*
4. The game respects my time.
5. I trust this game to treat me fairly.

These are not validated; treat them as monitoring items and check internal consistency with `psych_check.py alpha`.

### 6.1 Scoring and reliability
- Compute subscale means per participant after reverse-scoring reversed items: `reversed = (scale_min + scale_max) − raw`.
- Report mean, SD, n and 95% CI per build and segment; compare builds with the same scale only.
- Cronbach's α: `α = (k / (k − 1)) · (1 − Σσᵢ² / σ_total²)` for *k* items. Conventional floor ≈ 0.70 for research use (higher for individual decisions). Very high α (> 0.95) suggests redundant items.
- Command: `psych_check.py alpha --csv responses.csv --reverse 3 --scale-min 1 --scale-max 7`.

---

## 7. Interviews

### 7.1 Structure of a semi-structured guide (45 minutes)
| Block | Time | Purpose |
|---|---|---|
| Warm-up | 5 min | Rapport; their gaming life in general |
| Context | 10 min | When, where and why they play on mobile; what else competes for that time |
| Critical incidents | 15 min | "Tell me about the last time you..." (started a session, stopped playing, spent money, felt frustrated, felt proud) |
| Motivations and meaning | 10 min | What they value; what they would miss if the game disappeared |
| Close | 5 min | Anything we didn't ask; thanks |

### 7.2 Technique
- Ask about **specific past events**, not generalities or futures. "Tell me about the last time you stopped playing a game for good" yields truth; "Why do you stop playing games?" yields theories.
- Open questions, then follow-ups: "What happened next?", "How did that feel?", "Why was that important?" (laddering toward values).
- Tolerate silence; people fill it with substance.
- Do not pitch, defend or correct. Do not show the build during the interview unless it is a concept test.
- Separate observation from interpretation in notes.
- Avoid questions about price willingness; ask about past purchases and how they felt afterwards.

### 7.3 Analysis
1. Transcribe or write detailed notes within 24 hours.
2. Code segments with descriptive labels (open coding).
3. Group codes into themes (affinity mapping on a board); thematic analysis following Braun & Clarke (2006) is a widely used method.
4. For each theme: how many participants (x of n), representative quotes, counter-examples, implication for design.
5. Link themes to telemetry questions to test at scale (§9).

---

## 8. Heuristic evaluation

Expert review against a set of principles. Fast and cheap; finds obvious problems before players do. It predicts problems, it does not prove them — confirm the important ones with playtests.

### 8.1 Published heuristic sets (summarised; consult originals)
| Set | Focus | Notes |
|---|---|---|
| Nielsen's 10 usability heuristics (1994) | General interface usability: system status visibility, match with the real world, user control, consistency, error prevention, recognition over recall, flexibility, minimalist design, error recovery, help | Use for menus, shop, settings, onboarding UI |
| Federoff (2002) | Game interface, mechanics and play heuristics compiled from literature and a game company's practice | Early game-specific set |
| Desurvire, Caplan & Toth (2004) HEP; Desurvire & Wiberg (2009) PLAY | Gameplay, game story, mechanics, usability; PLAY extends to broader playability | Widely cited game heuristics |
| Pinelle, Wong & Stach (2008) | Ten usability heuristics derived from analysing problems in game reviews | Good for usability-in-play issues |
| Korhonen & Koivisto (2006) | Playability heuristics for mobile games (game usability, mobility, gameplay) | Mobile-specific; dated in places but the mobility issues still hold |

### 8.2 Studio mobile game heuristics (original set)
Rate each 0 (no problem) to 4 (catastrophe) using Nielsen's severity scale (0 not a problem, 1 cosmetic, 2 minor, 3 major, 4 catastrophe).

| # | Heuristic | Typical violation |
|---|---|---|
| H1 | The player can tell within 3 seconds what they can touch and what will happen | Decorative elements that look interactive |
| H2 | Every action gets immediate, proportionate feedback | Silent taps; delayed responses |
| H3 | The current goal is always visible or one tap away | Goal buried in a menu |
| H4 | Failure explains itself and offers a one-tap retry | Generic "Level failed" screen with ads before retry |
| H5 | New concepts arrive one at a time, taught by doing | Text walls; three new systems in one level |
| H6 | Critical controls sit in thumb reach and meet touch-target minimums | Top-corner buttons for frequent actions |
| H7 | The game survives interruption without loss | Progress lost after a call |
| H8 | The game is fully playable muted and in one hand (if portrait) | Audio-only cues; two-hand gestures |
| H9 | Information needed for the current decision is visible; no recall required | Hidden cooldowns; unseen enemy intents |
| H10 | Visual language is consistent (same colour/icon/sound = same meaning) | Two meanings for red |
| H11 | Monetisation UI is distinct from gameplay UI and never interrupts play | Offer buttons in gameplay positions |
| H12 | Prices, odds and contents are clear in real money before any purchase | Gem-only prices; odds hidden |
| H13 | Players can stop at a natural point with closure, and return without penalty | Endless chains; decay while away |
| H14 | Difficulty feels fair and recoverable; randomness never decides high-stakes outcomes alone | Random loss after a long run |
| H15 | Readability holds at real device size, in greyscale and for colour-vision deficiency | Muddy boards; red/green coding |
| H16 | Settings respect the player (accessibility, notifications, privacy) and defaults favour them | Notifications on by default; tiny text |

**Procedure.** 3–5 evaluators review independently (each plays the FTUE and two core loops on a target device), log violations with screen, heuristic and severity, then merge and de-duplicate; average severity across evaluators; fix severity ≥ 3 before human playtests.

---

## 9. Telemetry triangulation

Telemetry tells you **what** and **how many**; qualitative research tells you **why**; surveys tell you **how players perceive it**. Any one alone misleads. (For the analytics practice itself see `player-analytics`; a standard reference is Seif El-Nasr, Drachen & Canossa, *Game Analytics*, 2013.)

### 9.1 What each source can and cannot tell you
| Source | Good at | Blind to |
|---|---|---|
| Telemetry | Real behaviour at scale; funnels, cohorts, retention, economy flows | Intent, emotion, misunderstanding, what players wanted to do but couldn't |
| Playtest observation | Confusion, expectations, emotional reactions, workarounds | Prevalence; long-term behaviour; natural context |
| Interviews | Motivations, meaning, context, reasons for churn | Accurate recall of behaviour; prevalence |
| Surveys | Perception and attitudes at scale; segment comparisons | Behaviour (say–do gap); churned players |
| Store reviews and support tickets | Strong pain points, monetisation perception | Representativeness (extremes over-represented) |

### 9.2 Mixed-methods patterns
- **Explanatory sequential (quant → qual):** telemetry shows a problem, research explains it. *Example:* 38% of new players quit at level 7 → playtests show players don't notice the new blocker's weakness → fix the teach level → A/B test.
- **Exploratory sequential (qual → quant):** interviews generate hypotheses, telemetry or surveys size them. *Example:* interviews suggest players stop when daily tasks feel like chores → survey item on obligation + telemetry on dailies completion vs churn.
- **Convergent:** run both in parallel on the same question and compare.

### 9.3 Triangulation procedure
1. **Observe** the anomaly in telemetry with a cohort definition (install week, segment, device tier).
2. **Locate** it precisely (level, screen, event, time since install).
3. **Explain** with the cheapest qualitative method: session replays where available, 5–8 targeted playtests at that point, or 8–12 interviews with affected players.
4. **Hypothesise** the mechanism using this skill's models (motivation, M/A/P, frustration trigger, cognitive load).
5. **Test** a fix with an A/B test or a staged rollout, primary metric and guardrails defined in advance.
6. **Close the loop**: record the finding, evidence and result in `.gamestudio/reports/` and the decision log.

### 9.4 Instrumentation for psychology questions
Add these to the event taxonomy (`event_taxonomy.py generate --contract ...`, categories `ux`, `ftue`, `progression`, `monetization`):
- `level_fail` with `cause`, `progress_pct`, `attempt_index`, `time_in_level_sec`.
- `retry_start` with `seconds_since_fail` (frustration budget).
- `offer_shown` with `trigger` and `context` (lets you verify RL-05: no failure-triggered offers).
- `session_end` with `end_reason` (`natural_stop|background|force_quit|timeout`).
- `survey_answer` with `survey_id`, `item_id`, `value` (sampled micro-surveys).
- `hint_used`, `assist_toggled`, `skip_used` (mercy usage).
- `notification_open` with `notification_type` (value-bearing vs reminder).

### 9.5 Say–do gap examples
| Players say | Players do | Resolution |
|---|---|---|
| "I hate ads" | High rewarded-ad engagement | Dislike is for forced ads; keep rewarded opt-in, remove forced |
| "The game is too easy" (in surveys) | Churn concentrates at hard levels | Vocal engaged players differ from churners; segment the analysis |
| "I'd never pay for cosmetics" | Cosmetic sales grow with expression tools | Stated price intent is unreliable; test with real offers ethically |

---

## 10. Personas

A persona is a compact, evidence-based description of a key player group that keeps a team designing for real people. Alan Cooper popularised personas in *The Inmates Are Running the Asylum* (1999). In games, Canossa & Drachen (2009) proposed **play-personas** — clusters of play behaviour rather than demographics.

### 10.1 Types
| Type | Built from | Use |
|---|---|---|
| Proto-persona | Team assumptions, market-intel | Concept stage only; label as assumptions; replace with data |
| Qualitative persona | Interviews and playtests (8–20 players) | Design and FTUE decisions |
| Data-driven / play-persona | Telemetry clustering + survey | Live game; economy archetypes; live-ops targeting |
| Agent persona | Persona spec for `arcosian:player-simulator` | Automated friction scans |

### 10.2 Studio persona template
```
id: commuter-strategist
segment: Brain-trainer / Time-filler (motivation-models.md §11)
evidence: 9 interviews (2026-10), soft-launch cohort cluster C3 (n=4,120)
situation: plays on the train, 2-3 sessions of 3-6 min on weekdays, one-handed, often muted
job: "When I have a few minutes, I want a short puzzle where planning pays off,
      so I feel sharp before work."
motivations (QF): strategy, challenge, completion
needs: instant resume; fair difficulty; visible progress; no timers on planning
frustrations: random losses; ads between fail and retry; long FTUE
spend pattern: occasional small purchases; values remove-ads; dislikes random packs
signature metrics: high retries/level, low ad views, 70% sessions < 6 min
design implications: one-tap retry; fail recap; daily puzzle; no energy
economy archetype: archetypes[].id = "optimiser"-like (share 0.12, skill 0.75, spend 0.05)
agent persona prompt notes: impatient with text; quits after 2 unexplained losses
```

### 10.3 Persona anti-patterns
- Demographic-only personas ("Sarah, 34, likes yoga") with no behaviour or situation.
- Invented detail that looks like evidence; every claim should cite its source.
- Too many personas: keep 3–5 primary, one of which is the design target for the core loop.
- Personas never updated after launch data arrives.
- Using personas to stereotype by gender or age instead of motivation and situation.

---

## 11. Jobs-to-be-done for games

Jobs-to-be-done (JTBD) frames products as things people "hire" to make progress in a particular situation (Clayton Christensen et al., *Competing Against Luck*, 2016; Anthony Ulwick's outcome-driven innovation; Bob Moesta's switch interviews). For games it explains **what a game competes with** — not only other games but social media feeds, podcasts, messaging and sleep.

### 11.1 Job statement format
"When **[situation]**, I want to **[motivation/progress]**, so I can **[desired outcome/feeling]**."

| Situation | Job | Hired solutions (competitors) | Design implication |
|---|---|---|---|
| Waiting 5 minutes for a bus | Fill dead time with something that doesn't need setup | Social feed, messaging, any snack game | Instant start; complete loop under 3 min; safe to abandon |
| In bed, winding down | Switch off from the day without stress | Streaming, calm puzzle games | No timers or PvP; soft audio; low brightness readability |
| Lunch with colleagues who play | Share a common topic and light rivalry | Office chat, sports | Friends leaderboard; shareable moments; team events |
| Weekend afternoon | Get absorbed in a long strategic session | Console/PC games, books | Deep systems; long sessions supported with checkpoints |
| Feeling stuck in real life | Feel competent and in control | Exercise, hobbies, games | Clear progression; fair challenge (watch escapism risk, `motivation-models.md` §5) |

### 11.2 Functional, emotional and social dimensions
Every job has a functional side (fill 5 minutes), an emotional side (feel clever, feel calm) and a social side (have something to talk about, be seen as good). Concepts usually fail on the emotional side — they fill the time but don't deliver the feeling.

### 11.3 Switch interview (forces of progress)
Interview players who recently started (or quit) a game about the moment they switched, and map four forces:
- **Push** of the current situation ("my old game got grindy").
- **Pull** of the new solution ("my friend's keep looked cool").
- **Anxiety** about the new solution ("will it be pay-to-win?").
- **Habit** of the present ("I already have progress in my old game").

Design to strengthen push/pull messages in marketing (`marketing-ua`), reduce anxiety in the store page and FTUE (transparent monetisation, short tutorial), and lower habit cost (fast early progress).

### 11.4 Using JTBD in the pipeline
- `concept-lab`: write the job statement for each concept card's target audience; reject concepts whose job is already well served unless the hook is a clear improvement.
- Design contract: put the job in `player_fantasy` context notes and use it to justify session length (`meta.session_length_target_sec`).
- Research: switch interviews with churned players explain churn better than satisfaction surveys.

---

## 12. Biometrics and lab methods (when they are worth it)

| Method | Measures | Cost | Worth it when |
|---|---|---|---|
| Eye tracking (mobile sleds or glasses) | Where attention goes; missed UI | Medium–high | HUD and FTUE redesigns where "they didn't see it" is the hypothesis |
| Skin conductance (EDA/GSR) | Arousal (not valence) | Medium | Tension/release tuning in action or horror games |
| Heart rate / HRV | Arousal, stress | Low–medium | Coarse arousal arcs over sessions |
| Facial expression coding | Valence cues | Medium; accuracy debated | Supplement to observation, never alone |
| EEG | Cognitive load proxies | High; noisy | Research partnerships only |

Physiological signals are ambiguous (high arousal can be fun or fear); always pair them with observation and self-report. For most mobile studios, careful observation plus telemetry gives more value per dollar.

---

## 13. Reporting findings into the ontology

Playtest results are recorded with `${CLAUDE_PLUGIN_ROOT}/scripts/schemas/playtest-report.schema.json`:

| Field | Human playtest usage |
|---|---|
| `mode` | `"human"` for people, `"persona"` for agent personas |
| `build`, `runs`, `seed` | Build id; number of participants (runs); seed `null` or the deterministic seed if applicable |
| `metrics.time_to_first_reward_sec` | Median across participants |
| `metrics.avg_session_sec` | Mean free-play length |
| `metrics.win_rate` | Share of attempts won at tested levels |
| `findings[]` | `severity` (`blocker|major|minor|polish`), `title`, `detail` (behaviour + "x of n" + quotes), `repro` (step and screen) |
| `verdict` | `pass` if no blocker/major remains for the research question |

**Severity mapping.** Blocker = participant could not continue or abandoned (Nielsen severity 4); major = significant delay, error or frustration in ≥ 2 participants (3); minor = brief hesitation or recoverable error (2); polish = cosmetic or preference (1).

**Finding format.** "**[Behaviour]** — 4 of 6 participants dragged golems onto non-matching golems and waited for a merge that never came (levels 1–2). Quotes: 'Why won't these combine?' **Interpretation:** merge eligibility is not readable. **Recommendation:** highlight valid merge targets on drag. **Owner:** ux-designer. **Severity:** major."

Validate after writing: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py validate .gamestudio/playtests/<file>.json`.

---

## 14. Research ethics and minors

- **Informed consent**, written in plain language, before any recording.
- **Minimise data**: collect only what the research question needs; pseudonymise; set a retention period; restrict access.
- **Recording**: separate consent for video/face/voice; blur bystanders; store securely.
- **Right to withdraw** at any time, keeping the incentive.
- **No deception** about the purpose unless essential and approved, with debrief afterwards.
- **Vulnerable topics** (spending regret, problematic play) asked gently, optional, with signposting to support resources where appropriate.
- **Minors**: verifiable consent from a parent or guardian *and* the child's own assent in age-appropriate language; a guardian present or nearby for in-person sessions; shorter sessions; no collection of contact details from the child; no in-game purchases during sessions; follow children's-privacy law in the participant's country (see `legal-ethics`).
- **Incentives** neutral to the answers; avoid paying in the game's own currency for studies about monetisation perception.
- **Telemetry research** follows the game's privacy policy and consent choices; analytics on minors follows the protections matrix in `ethics-and-dark-patterns.md` §8.

---

## 15. Sources

Paraphrased; consult originals.

- Abeele, V. V., Spiel, K., Nacke, L., Johnson, D., & Gerling, K. (2020). "Development and validation of the Player Experience Inventory." *International Journal of Human-Computer Studies*, 135.
- Ballou, N., Denisova, A., Ryan, R. M., Rigby, C. S., & Deterding, S. (2024). "The Basic Needs in Games Scale (BANGS)." *CHI 2024*.
- Braun, V., & Clarke, V. (2006). "Using thematic analysis in psychology." *Qualitative Research in Psychology*, 3(2).
- Brooke, J. (1996). "SUS: A 'quick and dirty' usability scale." In *Usability Evaluation in Industry*.
- Canossa, A., & Drachen, A. (2009). "Play-personas: Behaviours and belief systems in user-centred game design." *INTERACT 2009*.
- Christensen, C. M., Hall, T., Dillon, K., & Duncan, D. S. (2016). *Competing Against Luck*. Harper Business.
- Cooper, A. (1999). *The Inmates Are Running the Asylum*. Sams.
- Desurvire, H., Caplan, M., & Toth, J. A. (2004). "Using heuristics to evaluate the playability of games." *CHI 2004 Extended Abstracts*. — Desurvire, H., & Wiberg, C. (2009). "Game usability heuristics (PLAY) for evaluating and designing better games." *HCII 2009*.
- Ericsson, K. A., & Simon, H. A. (1993). *Protocol Analysis: Verbal Reports as Data* (rev. ed.). MIT Press.
- Faulkner, L. (2003). "Beyond the five-user assumption." *Behavior Research Methods, Instruments, & Computers*, 35(3).
- Federoff, M. (2002). *Heuristics and Usability Guidelines for the Creation and Evaluation of Fun in Video Games*. Master's thesis, Indiana University.
- Guest, G., Bunce, A., & Johnson, L. (2006). "How many interviews are enough?" *Field Methods*, 18(1).
- Haider, A., et al. (2022). "miniPXI: Development and validation of an eleven-item measure of the Player Experience Inventory." *Proceedings of the ACM on Human-Computer Interaction (CHI PLAY)*.
- Hart, S. G., & Staveland, L. E. (1988). "Development of NASA-TLX." In *Human Mental Workload*.
- Hennink, M., & Kaiser, B. N. (2022). "Sample sizes for saturation in qualitative research: A systematic review of empirical tests." *Social Science & Medicine*, 292.
- IJsselsteijn, W. A., de Kort, Y. A. W., & Poels, K. (2013). *The Game Experience Questionnaire*. Technische Universiteit Eindhoven.
- Jackson, S. A., & Marsh, H. W. (1996). "Development and validation of a scale to measure optimal experience: The Flow State Scale." *Journal of Sport and Exercise Psychology*, 18(1).
- Jennett, C., Cox, A. L., Cairns, P., et al. (2008). "Measuring and defining the experience of immersion in games." *International Journal of Human-Computer Studies*, 66(9).
- Korhonen, H., & Koivisto, E. M. I. (2006). "Playability heuristics for mobile games." *MobileHCI 2006*.
- Laugwitz, B., Held, T., & Schrepp, M. (2008). "Construction and evaluation of a user experience questionnaire." *USAB 2008*.
- Law, E. L.-C., Brühlmann, F., & Mekler, E. D. (2018). "Systematic review and validation of the Game Experience Questionnaire (GEQ)." *CHI PLAY 2018*.
- Medlock, M. C., Wixon, D., Terrano, M., Romero, R., & Fulton, B. (2002). "Using the RITE method to improve products." *Usability Professionals' Association Conference*.
- Nielsen, J. (1994). "Enhancing the explanatory power of usability heuristics." *CHI 1994*. — and Nielsen Norman Group articles on heuristics and severity ratings, https://www.nngroup.com/
- Nielsen, J., & Landauer, T. K. (1993). "A mathematical model of the finding of usability problems." *INTERCHI 1993*.
- Pinelle, D., Wong, N., & Stach, T. (2008). "Heuristic evaluation for games: Usability principles for video game design." *CHI 2008*.
- Seif El-Nasr, M., Drachen, A., & Canossa, A. (Eds.) (2013). *Game Analytics: Maximizing the Value of Player Data*. Springer.
- Tullis, T., & Wood, L. (2004). "How many users are enough for a card-sorting study?" *UPA 2004*.
- Virzi, R. A. (1992). "Refining the test phase of usability evaluation: How many subjects is enough?" *Human Factors*, 34(4).
