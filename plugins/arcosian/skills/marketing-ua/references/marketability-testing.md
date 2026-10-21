# Marketability Testing

This file explains how to test whether a game concept can find an audience before you build it: pre-production CPI tests, fake-door tests, landing pages, playable and video prototypes, and how to read the resulting numbers without fooling yourself. It includes procedures, a test design template, sample-size guidance, decision rules and worked examples. Read it during concept selection, before committing production budget, or when a prototype needs a reality check on appeal.

## Table of contents
1. What marketability testing answers and does not
2. Test types
3. Designing a CPI test
4. Creative for concept tests
5. Fake-door tests
6. Landing pages
7. Playable and prototype tests
8. Sample size and noise
9. Reading the numbers
10. Decision rules
11. Worked example: three concepts, one budget
12. Ethics and disclosure
13. Test plan template
14. Common mistakes
15. Volatile facts (as of Oct 2026 - verify)

## 1. What marketability testing answers and does not
Answers:
- Is there interest in the promise (hook, fantasy, genre twist), relative to alternatives?
- Which framing or art style attracts more clicks?
- Roughly how expensive is the audience to reach?
Does not answer:
- Whether the game is fun enough to retain players (that needs a playable core loop and retention data).
- Whether players will pay (that needs monetization tests in soft launch).
- Absolute CPI at scale; test CPIs are only comparative signals.
Rule: a concept can pass marketability and fail retention; both gates are required (see `concept-lab`, `liveops`).

## 2. Test types
| Test | What you show | What you measure | Cost and speed |
|---|---|---|---|
| Creative CPI test | Video or image ads of the concept | CTR, CPC, CPI-like cost for clicks to a store-like page | Low cost, days |
| Fake door | A store-like page with a call to action that leads to "coming soon" and a sign-up | Click-to-sign-up rate | Low cost, days |
| Landing page | A page with the pitch and email sign-up | Visit-to-sign-up conversion | Very low cost |
| Playable test | Interactive demo of the core mechanic | Engagement, completion, IPM-like measures | Medium effort |
| Prototype test | Real prototype with analytics | D1 and session behavior in a small group | Higher effort |
| Survey or interview | Concept description and mockups | Stated interest and reasons | Cheap, weak predictor |
Stated interest is weaker than behavior; prefer behavioral tests (clicks, sign-ups, plays).

## 3. Designing a CPI test
Procedure:
1. Define the hypothesis (for example "concept A's hook attracts a cheaper click than B and C").
2. Build comparable creatives per concept: same format, same length, same quality level, so concept is the only variable.
3. Choose one channel and one geography to reduce noise; use a market with an affordable CPI similar enough to your target audience.
4. Set equal budgets and run simultaneously with the same targeting and bidding objective.
5. Choose the metric: for ads that lead to a store page where the app does not exist yet, measure cost per click and click-to-sign-up on a fake door; for concepts with a playable, measure cost per play and completion.
6. Define the stop rule in advance: a minimum number of clicks or impressions per concept.
7. Run for a short fixed window (a few days) to avoid creative fatigue and budget drift.
8. Analyze with intervals, then decide using the rules in section 10.
Notes:
- Some networks allow tests with pre-launch pages or with an existing placeholder app; follow network policies and do not deceive users into thinking the game is released unless the page makes clear it is a test or sign-up.
- Avoid optimizing delivery for install events that cannot occur; use click or sign-up objectives where permitted.

## 4. Creative for concept tests
- Produce quick mockups: concept art, a short gameplay mock using prototype capture, motion graphics of the core mechanic.
- Keep the promise honest: depict what the game will plausibly deliver. If a visual is aspirational, label it as concept art in the landing page copy.
- Variables to test one at a time: genre framing, fantasy or theme, art style, hook moment, title, character.
- Create two or three executions per concept so you can separate concept appeal from execution quality.
- Keep a consistent call to action across concepts.
- Record all assets and parameters in the creative log (see `references/ua-and-creatives.md`).

## 5. Fake-door tests
- A fake door is a page or button that implies a feature or game exists and records interest, then reveals it is not yet available and invites sign-up.
- Use for: feature interest inside an existing game (a menu item for a mode that is not built), or concept interest pre-production.
- Ethics: reveal promptly and politely; never take payment; never collect more data than needed; give a clear reason and an incentive to sign up (early access).
- Measure: click-through to the door, sign-up conversion after reveal, bounce.
- In-game fake doors: limit to a small share of players, remove after the test, and state "coming soon" clearly; do not over-use, since repeated teasers harm trust.
- Interpretation: clicks on a fake door measure curiosity; sign-ups measure stronger intent; neither measures willingness to pay.

## 6. Landing pages
Elements: headline stating the promise, a short video or animated GIF of the hook, three bullets, social proof if real, a single sign-up form, privacy notice and consent for email.
Testing: run two or three versions with the same traffic source; vary headline and hero media; compare visit-to-sign-up.
Instrumentation: page analytics with consent, UTM parameters (no personal data in URLs), source tracking by creative.
Benchmarks: conversion rates depend heavily on traffic quality and offer; treat them as relative measures between your variants, not as targets from outside sources.
Post-test: keep the list for community and pre-registration; honor unsubscribes and data-deletion requests (see `legal-ethics`).

## 7. Playable and prototype tests
- Build the smallest interactive slice that shows the core mechanic and its "juice" (`game-feel`).
- Distribute as a playable ad, a web build, or a TestFlight/internal test build to a small recruited group.
- Metrics: percentage who start playing, first-minute completion, repeat plays in the session, return the next day (for prototypes), plus qualitative notes from sessions.
- Compare two or three variants of the mechanic (control scheme, difficulty ramp, art direction) with a small randomized split.
- Watch rather than ask: observing where players hesitate gives better data than surveys.
- Playable-ad tests double as creative tests; see playables in the UA file.
- For retention signals you need real returning behavior; a few hundred players give only rough direction (see section 8).

## 8. Sample size and noise
- Click-based rates are proportions; uncertainty shrinks with the square root of the sample.
- Rule of thumb for a proportion p with n observations: standard error is about `sqrt(p(1-p)/n)`; the 95 percent interval is roughly p plus or minus 1.96 times that.
- To tell two concepts apart you need intervals that do not overlap or, better, a proper two-proportion test; use `${CLAUDE_PLUGIN_ROOT}/scripts/ab_test.py` for sample sizes and significance.
- Small differences need large samples; do not chase a few percent difference with a tiny budget; look for big gaps.
- Sequential peeking inflates false positives; fix the sample size or use a sequential method.
- Testing many concepts at once increases the chance that one looks good by luck (multiple comparisons); confirm the winner in a second round.
- Traffic quality varies by time and placement; run concepts in parallel, not sequentially.
- Creative execution confounds concept; use multiple executions per concept.

## 9. Reading the numbers
Order of reading:
1. Sanity: delivery was even, spend matched, no tracking failures.
2. Top funnel: CTR and cost per click by concept.
3. Mid funnel: landing page or fake-door conversion; sign-up rate.
4. Depth: playable engagement or prototype behavior.
5. Cost: cost per sign-up or per engaged player.
Interpretation guidance:
| Pattern | Likely reading | Action |
|---|---|---|
| High CTR, low sign-up | Curiosity without belief in the promise | Fix the page or the promise match |
| Low CTR, high sign-up | Narrow but interested audience | Niche concept; consider organic and community |
| High CTR and sign-up, weak playable engagement | Promise stronger than mechanic | Improve mechanic or scale back claims |
| All concepts weak | Genre fatigue or poor execution | Revisit positioning and creative quality |
| One concept far ahead | Strong hook signal | Proceed to prototype and retention tests |
Compare relative to a baseline: include an existing successful game's style as a control creative if available (your own or a reference) so you can see whether concepts beat or trail a known performer.
Never convert a test cost per click directly to a production CPI forecast; the relationship depends on the store page, game quality and audience.

## 10. Decision rules
Define before the test:
- Advance a concept if its cost per sign-up (or engaged player) beats the median of the field by a stated margin and the interval supports it.
- Kill concepts at the bottom of the field unless there is a specific, fixable execution flaw.
- Tie: pick by team passion, production cost and fit with strategy.
- Combine with other gates: feasibility, scope, economy viability, market size (`market-intel`, `design-review`).
- Record the decision and the evidence in the concept card and project state (`gs.py`).
- A weak result with a strong hypothesis for why can justify one repeat with improved creative, but only once.

## 11. Worked example: three concepts, one budget
Concepts: A (cozy gardening puzzle), B (tower defense with a twist), C (idle merge with a story).
1. Produce two short video executions per concept, same length and format.
2. Run on one channel and one country, equal budgets, three days, objective click to landing page.
3. Landing pages are identical except for the hero video and headline; each has an email sign-up with a clear "game in development" notice.
4. Results (hypothetical): A has the highest sign-up rate with moderate CTR; B has the highest CTR but low sign-up; C has low engagement.
5. Reading: B's hook is attention-grabbing but the promise does not convert; A attracts a smaller but more committed audience. C is dropped.
6. Next: build a playable of A's core mechanic and test engagement; revisit B's framing in a second round with new executions.
7. Gate: A proceeds to prototype only if the playable's engagement also holds.
8. Document the budget used, interval estimates and the decisions.

## 12. Ethics and disclosure
- Never imply a game is available when it is not, unless the page clearly states it is in development and collects interest.
- Do not collect data beyond what is needed; use consent for email, honor deletion.
- No payments or pre-orders for products you may not build, unless a platform pre-order mechanism with refunds is used.
- Do not use stolen or misattributed art in concept tests; follow asset rights (`ai-asset-pipeline` provenance rules when using generated art; disclose per store and network rules).
- Do not target minors with tests that collect personal data.
- If a concept test uses a real brand or IP, get permission.

## 13. Test plan template
```yaml
test_id: concept_cpi_01
hypothesis: "Concept A attracts cheaper qualified sign-ups than B and C"
concepts: [A, B, C]
executions_per_concept: 2
channel: one_network
geography: one_country
budget_per_concept: equal
duration_days: 3
objective: click_to_landing
primary_metric: cost_per_signup
secondary: [ctr, cost_per_click, landing_conversion, playable_engagement]
stop_rule: "min clicks per concept reached"
analysis: "intervals; two-proportion test via ab_test.py"
decision_rule: "advance if cost_per_signup beats field median by margin and interval supports it"
ethics_check: "landing page states game in development; consent for email"
owner: market-analyst
```

## 14. Common mistakes
- Judging on tiny samples and declaring winners from noise.
- Comparing concepts with unequal creative quality.
- Testing too many concepts with too little budget.
- Treating test CPI as a forecast of launch CPI.
- Ignoring the product gate: a hot hook with a dull loop only moves cost to later.
- Confusing curiosity clicks with intent to play regularly.
- Misleading test pages that damage trust.
- Not recording results, so the same test repeats.

## 15. Volatile facts (as of Oct 2026 - verify)
- Ad network policies on pre-launch campaigns, placeholder apps and click-to-landing objectives change; check the current policy of the channel you use before spending.
- Store pre-registration and pre-order mechanics change; verify in current developer documentation: https://developer.apple.com/app-store/ and https://developer.android.com/distribute
- Privacy rules for email collection and consent differ by region; see https://gdpr-info.eu/art-8-gdpr/ for the baseline on children's consent and confirm with counsel for others.
- Measurement on iOS is aggregated and delayed; see `references/ua-and-creatives.md` section 18 for attribution sources.

## 16. Interpreting results for different genres
| Genre family | What the hook usually is | Test emphasis |
|---|---|---|
| Hyper-casual and puzzle | A single satisfying mechanic visible in seconds | Playable ads and short clips; IPM-like measures |
| Hybrid-casual | Core mechanic plus meta fantasy | Test the meta promise separately from the mechanic |
| Mid-core strategy and RPG | Fantasy, power progression, art style | Landing page and trailer sign-up; cost per sign-up |
| Narrative | Premise and characters | Community and sign-up depth over clicks |
| Social and party | Shared moments | Test with groups; viral potential via invites |
Use `genre-playbooks` to calibrate what a plausible result looks like for the genre, and treat any outside benchmark as a hypothesis to record with its source and date.

## 17. After the test
1. Archive creatives, parameters, spend, results and the decision in the concept card.
2. Keep the sign-up list for community and pre-registration, under the consent given.
3. Share learnings with design: which framing resonated becomes the pitch line and the store-page headline.
4. Schedule the next gate (prototype retention test) with its own pass criteria.
5. Close the loop: if the game later launches, compare launch CPI and retention with the test signals to learn how predictive your tests were; keep that calibration record.

## 18. Quick reference
- Test behavior, not opinions; compare concepts in parallel with equal budgets.
- Decide thresholds before seeing data; record them in the test plan.
- A marketability pass is one gate; retention and monetization gates follow.
