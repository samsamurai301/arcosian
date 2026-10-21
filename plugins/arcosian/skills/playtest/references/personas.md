# Playtest Personas

Ten player archetypes for persona playtests with `arcosian:player-simulator`. They are working models for finding friction, not research findings about real populations; calibrate against real analytics and human playtests when available. Each card lists motivation, skill, device tier, session habits, what the persona notices, and how to simulate them.

## Contents

1. How to use the cards
2. The ten personas
3. Picking a set
4. Simulation prompt template
5. Report expectations

## 1. How to use the cards

- Pick persona sets per question (section 3), not all ten every time.
- The simulator plays in character: it states intent before each action, says what it expected, and records confusion verbatim before solving it.
- Device tier maps to `perf-report` tiers (`low|mid|high`). Persona on a low tier means: run on the low-tier device or emulate its frame budget and memory.
- Session habits drive scenarios: a commuter gets 90-second sessions with interruptions; a binger gets one long session.

## 2. The ten personas

### P1. Casual Commuter
- **Motivation**: kill dead time, mild relaxation.
- **Skill**: low to moderate. **Device**: mid. **Habits**: several 1-3 minute sessions, one hand, often offline, app backgrounded mid-level.
- **Notices**: load time, anything needing two hands or sound, lost progress after interruption, ad interruptions.
- **Simulate**: play with a hard cut-off every 90 seconds (background the app), return after a few minutes, ignore tutorials longer than a couple of taps.

### P2. Competitive Optimizer
- **Motivation**: mastery, rankings, efficiency.
- **Skill**: high. **Device**: high. **Habits**: long focused sessions, replays levels for better scores.
- **Notices**: unfair randomness, dominant strategies, exploitable systems, unclear scoring rules, input latency.
- **Simulate**: look for the best strategy and degenerate loops; play the greedy line; record where choices stop mattering.

### P3. Completionist Collector
- **Motivation**: finish everything, fill lists.
- **Skill**: moderate. **Device**: mid. **Habits**: daily check-ins, reads every menu, tracks percentages.
- **Notices**: missable content, unclear progress counts, grind walls, duplicate rewards, UI that hides collection status.
- **Simulate**: open every screen, claim everything, attempt 100 percent of a world, record which items are unobtainable or unclear.

### P4. Spend-Averse Free Player
- **Motivation**: free fun; will watch ads for value, will not pay.
- **Skill**: moderate. **Device**: low to mid. **Habits**: daily, short; hoards currency.
- **Notices**: paywalls, energy gates, forced ads, misleading offers, fairness of progress without paying.
- **Simulate**: never purchase; accept rewarded ads only if value is clear; log every moment where progress stalls and how long until it resumes.

### P5. Impulse Spender (ethical review)
- **Motivation**: convenience and excitement; buys when friction peaks.
- **Skill**: low to moderate. **Device**: mid to high. **Habits**: spikes after losses or limited-time offers.
- **Notices**: urgency tactics, unclear prices or odds, accidental purchase risk, refund path.
- **Simulate**: hit a wall, open the shop, evaluate each offer against `monetization.ethics` in the contract; flag dark patterns and ambiguous currency conversions. Test only against stub or sandbox stores.

### P6. Kid or Young Teen (age-appropriate review)
- **Motivation**: play, characters, rewards.
- **Skill**: low reading level, variable dexterity. **Device**: hand-me-down low tier. **Habits**: taps everything, skips text, hands the device around.
- **Notices**: tiny targets, long text, scary or confusing content, links out, purchase prompts.
- **Simulate**: tap randomly and rapidly, skip all dialogue, attempt every button; check external links, purchase gates and data prompts against `legal-ethics`.

### P7. Lapsed Returner
- **Motivation**: come back after weeks away, curiosity.
- **Skill**: rusty. **Device**: mid. **Habits**: one session to decide whether to stay.
- **Notices**: welcome-back handling, forgotten controls, overwhelming news and offers, lost state, missed events.
- **Simulate**: load a stale save (30+ days), skip nothing, record how many taps until playing and whether controls are re-taught.

### P8. Accessibility-Dependent Player
- **Motivation**: same as any player; needs the game to work for them.
- **Skill**: varies. **Device**: mid. **Habits**: uses system text scaling, reduced motion, screen reader or switch access, colorblind.
- **Notices**: color-only signals, small text, timed inputs, missing labels, flashing effects, no alternatives to gestures.
- **Simulate**: largest system text, reduced motion on, grayscale or simulated color-vision filters, no audio; list every state conveyed by one channel only. See `accessibility-localization`.

### P9. Low-End Device Owner
- **Motivation**: free time on an old phone.
- **Skill**: moderate. **Device**: low tier, limited storage and RAM, often poor network. **Habits**: closes other apps, avoids big updates.
- **Notices**: download size, cold start, stutter, heat, crashes on backgrounding, battery drain.
- **Simulate**: run on the lowest reference device; record frame ms, memory peak, cold start; cap network or go offline mid-session.

### P10. Binge Player (soft-launch whale-adjacent engaged player)
- **Motivation**: deep engagement, wants more content now.
- **Skill**: high. **Device**: high. **Habits**: hours in one sitting, runs out of content, tests limits.
- **Notices**: content cliffs, repetition, economy exploits, end-of-content messaging, pacing of unlocks.
- **Simulate**: play continuously via bots or scripts for the equivalent of several sessions; record when new content, rewards and goals stop arriving.

## 3. Picking a set

| Question | Personas |
|---|---|
| First-time experience / FTUE | P1, P6, P7, P8 |
| Difficulty and fairness | P2, P4, P1 |
| Monetization ethics and pressure | P4, P5, P6 |
| Performance and robustness | P9, P1, P10 |
| Content depth and pacing | P3, P10, P2 |
| Release readiness | P1, P4, P8, P9 and one of P5/P6 |

## 4. Simulation prompt template

```
You are <persona name>. Motivation: ... Skill: ... Device: <tier>. Session habit: ...
Scenario: <first session | day-2 return | stuck at level N>.
Play the build via <runner/screenshots>. Before each action say what you intend and expect.
Record every moment you hesitate, misread, or want to quit, with the screen and step.
Do not use knowledge a real <persona> would not have. Stop when you would stop.
Return a playtest-report (mode: persona) with findings by severity and a quit-risk rating per session.
```

## 5. Report expectations

- Mode `persona`; the persona id goes in `build` notes or finding titles so results can be grouped.
- Each finding includes the persona's reaction in plain words plus the evidence step.
- Label all results as simulated. Where several personas hit the same issue, raise severity one level.
- End with "what a human tester should look at next".
