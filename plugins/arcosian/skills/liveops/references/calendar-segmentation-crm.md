# Calendar, Segmentation and CRM

This file explains how to build a live-ops calendar (seasons, holidays, weekly rhythm, freeze windows), how to segment players, how to personalize offers and messages responsibly, how to run push and in-game messaging, and how to design win-back. It includes procedures, tables and templates. Read it when you plan a quarter, set up CRM tooling, or review whether messaging is helping or annoying players.

## Table of contents
1. Calendar principles
2. Building a quarter
3. Seasons
4. Holidays and cultural moments
5. Calendar template
6. Segmentation models
7. Segment definitions and data needs
8. Personalized offers
9. Push notifications
10. In-game messaging and mail
11. Win-back
12. Lifecycle journeys
13. Measuring CRM
14. Consent, privacy and ethics
15. Tooling notes
16. Worked example: day-7 lapse journey

## 1. Calendar principles
- The calendar is a constraint solver: fixed dates, team capacity, economy budget and player fatigue.
- Plan three horizons: next two weeks (committed), next quarter (planned), next year (themes and big beats).
- Keep a fixed weekly rhythm (see fundamentals file) and move specials around it.
- Every item on the calendar has an owner, a goal, a dependency list and a ready-by date that precedes the start by a safe buffer (build, QA, localization, store review if needed).
- Freeze windows: before major releases and holidays when support is thin, only low-risk config changes.
- Keep a contingency slot: a prebuilt evergreen event that can replace a slipped item.

## 2. Building a quarter
Procedure:
1. Collect constraints: content roadmap, app release train, marketing beats, platform featuring, holidays for main markets, team vacations.
2. Define the quarter theme and its seasons.
3. Place the season boundaries; place the biggest content drops at season starts.
4. Fill weekly rhythm slots with templates.
5. Insert specials at gaps with a minimum spacing.
6. Run an economy check: cumulative injected rewards vs sinks by week (see `economy_sim.py`).
7. Run a fatigue check: concurrent obligations per day; make quiet days explicit.
8. Check dependencies: art, localization (translation lead times), legal approvals for IP collaborations.
9. Review with design, art, engineering, support, community, marketing.
10. Publish and commit; allow weekly re-plans for the next two weeks only.

## 3. Seasons
- A season is a multi-week arc with a theme, pass, missions, content additions and a store refresh.
- Season length: set by how fast you can make fresh content without quality loss; do not shorten seasons just to hit revenue.
- Inside a season: a beginning (hook), middle (rhythm with mini-milestones), end (finale event, countdown).
- Between seasons: a recovery period, a retrospective, a preview of the next season.
- Theming: choose themes that give visual identity and a story hook (see `narrative-design`).
- Carry-over: permanent items earned stay; seasonal-only items are cosmetic or convertible; avoid invalidating players' progress.
- Announce the schedule in advance so players can plan.

## 4. Holidays and cultural moments
- Choose holidays by where your players are (data), not by Western default.
- Examples to consider by region: new-year festivals, harvest and religious festivals, national days, school holidays, seasonal weather changes, major sports and shopping events.
- Respect: avoid trivializing religious or cultural elements; consult native speakers; some holidays are solemn and unsuitable for sales.
- Behavior shifts: engagement and spending patterns vary around holidays; use history rather than assumptions. During long holidays players may have more time but less routine.
- Timing: floating-date holidays need a verified date source each year; do not hard-code dates in the calendar template.
- Support and ops capacity around holidays: plan staffing and freeze windows.

## 5. Calendar template
| Week | Evergreen layer | Weekly layer | Special | Season beat | Economy check | Risks |
|---|---|---|---|---|---|---|
| 1 | Daily login, quests | Weekly challenge A | Season launch | Pass opens | Baseline | Launch load |
| 2 | same | Challenge B | none | Mid-season mission | Injection ok? | - |
| 3 | same | Limited-time mode | Collab teaser | - | - | QA load |
| 4 | same | Challenge C | Tournament weekend | - | Currency drift? | Cheating |
| 5 | same | Challenge D | none (rest) | - | - | - |
| 6 | same | Bonus week | Finale event | Pass ends | Sink push | Fatigue |
Keep the template in a repository and generate config from it; avoid hand-edited spreadsheets that diverge from the config.

## 6. Segmentation models
Use a few meaningful segments rather than dozens.
| Dimension | Values | Use |
|---|---|---|
| Lifecycle | New (day 0-3), early (4-14), established, veteran, lapsed | Onboarding, protection, win-back |
| Engagement | Casual, core, hardcore (sessions and minutes per week) | Event difficulty tiers |
| Payer state | Non-payer, first-time, repeat, lapsed payer, subscriber | Offers, suppression |
| Progress | Stage in game; blocked or not | Contextual help and offers |
| Preference | Modes, genres, social vs solo | Event relevance |
| Platform and device | OS, device tier, region | Delivery, localization, pricing tiers |
| Acquisition | Organic vs paid, channel | Expectations, quality analysis |
| Risk | Churn probability, suspicion of fraud, minor flag | Retention actions, safeguards |
Rules:
- Segments must be computable from available data, stable enough not to flip daily, and acted on differently.
- Version the definitions and log segment membership at exposure time for analysis.
- Do not segment on sensitive attributes or inferred vulnerability for targeting offers.

## 7. Segment definitions and data needs
| Segment | Rule example (tunable) | Data |
|---|---|---|
| New | Days since install at most 3 | Install date |
| Lapsed | No session for a set number of days (for example 7 to 14, tune per game) | Last session |
| Core | Sessions per week above a threshold derived from the median | Session log |
| Non-payer | Lifetime spend zero | Purchase ledger |
| Lapsed payer | Spent before, none recently | Ledger |
| Stuck | Repeated fails on the same level | Level telemetry |
| Churn-risk | Model score above threshold or declining sessions | Model or heuristic |
Churn model options: start with heuristics (session decline over last days), then logistic regression or gradient boosting on engineered features; validate on holdout; beware of using the model's output to push aggressive monetization.

## 8. Personalized offers
- Personalization options: which offer, when, which price tier within allowed ladder, which content bundle, which message.
- Start rule-based: for stuck players offer help (a free hint or an affordable boost), for engaged non-payers a starter pack, for payers a value pack aligned to their usage.
- Personalized pricing (different prices for similar players) raises fairness and legal concerns; prefer personalized content or timing instead of price discrimination; if testing price, do so as a randomized experiment with clear regional price tiers and avoid targeting based on inferred vulnerability.
- Frequency and fatigue: cap offer impressions; suppress after purchase; rotate.
- Ethics: no exploitation of frustration or loss; see `monetization` offers file.
- Explainability: you must be able to explain why a player saw an offer.

## 9. Push notifications
Principles:
- Push is permissioned attention; spend it carefully.
- Value test: would the player thank you for this message?
Types:
| Type | Example | Rule |
|---|---|---|
| Transactional | Timer complete, queue ready | Highest value; honor user settings |
| Event | Event starts, last day to claim | Limit frequency |
| Social | Friend action, guild call | Respect social preferences |
| Win-back | You have unclaimed rewards | Few, stop after repeated non-response |
| Promotional | Sale | Rare; opt-in category |
Practices:
- Ask for permission after value is evident, with a pre-prompt explaining what notifications will be sent.
- Offer categories with toggles; link to settings.
- Quiet hours by local time; frequency caps per day and week.
- Personalize send time using local time and the player's usual play window.
- Deep link to the relevant screen; broken deep links waste the opportunity.
- Copy: clear, specific, no deceptive urgency, no guilt tone; localize.
- Measure open rate, session start within a window, opt-out rate, uninstall signals; the opt-out rate is a guardrail.
- Platforms: handle token refresh, delivery failure, and platform limits on background activity. Firebase Cloud Messaging is a common free-tier service (verify current terms: https://firebase.google.com/pricing).
- Rich notifications and images: keep light; test across OS versions.

## 10. In-game messaging and mail
- Inbox for rewards, announcements and compensation: persistent, with expiry and claim states.
- Announcement banners: one at a time, dismissible, linked to details.
- Pop-up discipline: at most one interruption per session beyond core flows; none in tutorial.
- Targeting: same segments, same suppression rules.
- Content management: messages as config with localization keys, start and end times, client version gates.
- Read receipts and analytics: shown, clicked, dismissed.

## 11. Win-back
Define lapsed by inactivity thresholds suited to the game's natural frequency (a daily game lapses sooner than a weekly one).
Journey ideas:
1. Soft reminders using useful transactional pushes (timers, rewards waiting).
2. After a longer gap, a welcome-back message highlighting what is new.
3. On return: a gentle re-onboarding, a welcome-back reward track that does not penalize loyal players, and a catch-up path.
4. Pause outreach after several non-responses; respect the player.
Win-back by cause:
| Cause of lapse | Lever |
|---|---|
| Stuck or frustrated | Help, difficulty relief, tips |
| Bored (ran out of content) | New content announcement |
| Life gap | Low-pressure return, catch-up |
| Better alternative | Differentiating content, community |
| Technical problem | Fix communications |
Measure reactivation rate, D7 retention of reactivated players (a reactivation that does not stick is cost without value), and cost of rewards.

## 12. Lifecycle journeys
- Day 0: onboarding, no monetization interruptions, ask permission for notifications after first value.
- Days 1 to 3: reinforce habit (timers, daily reward), gentle intro to the first meta features.
- Days 4 to 14: introduce events and social features; first offer for engaged non-payers.
- Established: seasons, tiered events, passes.
- At risk: stuck help or content hooks.
- Lapsed: win-back journey.
- Veteran: community roles, endgame events, feedback invitations.
Document each journey as a state machine with triggers, messages, caps and exit conditions.

## 13. Measuring CRM
- Always use a holdout group that receives no CRM messages of the tested type.
- Primary metrics: incremental retention or revenue, not clicks.
- Guardrails: opt-out rates, uninstall, sentiment, support tickets.
- Interference: multiple concurrent campaigns confound; maintain a campaign registry and a global frequency cap.
- Reporting: weekly CRM dashboard by segment; archived learnings.
- Use `ab_test.py` for sample sizing; use `retention_ltv.py` to translate retention lift to LTV.

## 14. Consent, privacy and ethics
- Obtain valid consent for notifications and marketing communications as required in each region; honor unsubscribe at once.
- Do not use personal data beyond the declared purposes; document data uses in the privacy policy.
- For minors: no marketing push; limit to transactional messages; follow regional child-privacy laws (see `legal-ethics`).
- Avoid dark patterns: fake countdowns, guilt copy, hidden opt-outs.
- Data minimization: store only the attributes segments need; set retention periods.
- Right to delete: segment and CRM data deleted with the account.

## 15. Tooling notes
- Remote config and messaging can run on Firebase (Remote Config, Cloud Messaging, A/B Testing); the Firebase MCP can read and publish Remote Config templates and send messages (verify current capabilities: https://firebase.google.com/docs/ai-assistance/mcp-server).
- Alternatives include PlayFab, Unity Gaming Services, Nakama and dedicated CRM vendors; evaluate on segmentation, API quality, cost and data export (see `multiplayer-backend`).
- Keep segment logic in your own code or warehouse when possible, so vendor changes do not lose definitions.
- Everything that sends to players needs a kill switch.

## 16. Worked example: day-7 lapse journey
Context: puzzle game, daily habit. A player with no session for several days.
1. Day 2 inactivity: transactional push about a finished timer or waiting daily chest (if the player enabled push).
2. Day 5: event push if a relevant event is live, deep link to the event screen.
3. Day 9: one message summarizing new content; no discounts.
4. Day 14 or later: welcome-back track available on return; no more push after two non-responses.
5. On return: banner explains the welcome-back track; a catch-up quest series gives a short path to rejoin the current event.
Measurement: holdout receives no lapse pushes; compare reactivation within 14 days and D7 retention post-return; track push opt-out; success if reactivation rises and opt-out stays flat.
Guardrails: cap total push per week; stop sequences after opt-out; suppress for minors.

## 17. Quarterly planning checklist
- [ ] Fixed dates collected (holidays by market, releases, platform events).
- [ ] Seasons placed; boundaries match content readiness.
- [ ] Weekly rhythm filled from templates; quiet days marked.
- [ ] Economy injection by week simulated and reviewed.
- [ ] Localization lead times respected.
- [ ] Freeze windows and contingency event defined.
- [ ] Segments and CRM journeys updated for the new quarter.
- [ ] Holdout design agreed for each major test.
- [ ] Owners and ready-by dates assigned.
