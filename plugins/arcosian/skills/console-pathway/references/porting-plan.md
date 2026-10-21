# Porting Plan Template

This file is a template for planning a console port: phases with exit criteria, staffing by route, performance targets, controller and TV UX conversion, a risk register, and a worked example for a 2D indie game. All numbers are planning estimates; replace them with the platform's documents (after approval) and partner quotes. It contains no NDA content: platform-specific limits are written as "from platform documents".

## Contents
1. How to use this template
2. Phases and exit criteria
3. Staffing by route
4. Performance targets
5. Controller conversion
6. TV and handheld UX conversion
7. Platform features checklist
8. Risk register
9. Schedule and budget template
10. Worked example: a 2D platformer to Switch and Xbox
11. Review cadence and reporting

## 1. How to use this template
1. Copy sections 2 to 9 into `.gamestudio/reports/console-<platform>-plan.md` (no NDA text).
2. Fill the blanks marked `<...>`; leave "from platform documents" until you have them.
3. Update weekly; any slip over one week goes to the risk register.
4. Human approves the plan, spending and each submission.

## 2. Phases and exit criteria
| Phase | Work | Exit criteria | Typical duration (estimate, 2D indie) |
|---|---|---|---|
| 0. Readiness | Fix PC-side debt: controller-only UI, saves, suspend-safe state machine, text fit | Readiness table all pass on PC | 2 to 6 weeks |
| 1. Access | Register, apply, agreements, kits | Documents and a working kit or partner kit access | 4 to 10 weeks (parallel with 0) |
| 2. Engine bring-up | Engine or middleware runs the game on the console | Game boots and plays one level at any speed | 2 to 6 weeks |
| 3. Platform services | Users, saves, achievements, suspend, controller handling, store hooks | All platform features pass internal tests | 3 to 6 weeks |
| 4. Performance | Hit target frame rate and memory | Targets in section 4 met on the weakest mode | 3 to 6 weeks |
| 5. UX conversion | TV and handheld UI, glyphs, text, accessibility | UX checklist (section 6) passes | 2 to 4 weeks (parallel with 4) |
| 6. Localisation and QA | Languages, soak tests, content audit | Test matrix in `certification-and-ratings.md` passes | 3 to 5 weeks |
| 7. Ratings and store | Questionnaire, store assets, pricing | Ratings issued; store page complete | 2 to 4 weeks (parallel with 6) |
| 8. Certification | Submit, fix, resubmit | Pass | 3 to 8 weeks |
| 9. Release | Date, announcement, day-one patch plan | Live; support rota running | 1 to 2 weeks |
Total for a prepared 2D game with a partner: about 4 to 7 months (estimate).

## 3. Staffing by route
| Role | Self-port | Porting partner | Publisher |
|---|---|---|---|
| Producer | 0.2 FTE (you) | 0.2 FTE | 0.1 FTE |
| Lead engineer | 1.0 FTE | 0.3 FTE (reviews, answers) | 0.3 FTE |
| Second engineer | 0.5 to 1.0 FTE | 0 | 0 |
| UI or UX artist | 0.3 FTE | 0.2 FTE | 0.2 FTE |
| QA | 0.5 to 1.0 FTE | partner QA plus 0.3 FTE yours | publisher QA |
| Audio, localisation | contractors | partner or yours | publisher |
| Legal and business | human lead | human lead | human lead |
FTE = full-time equivalent. Estimates; small teams overlap roles.
Use agents for: readiness audits, test-matrix generation, glossary of platform terms, store text drafts, schedule tracking (`arcosian:producer`). Humans: all agreements, identity, spending, submissions.

## 4. Performance targets
Targets are what you aim at; the platform documents give hard limits (from platform documents).
| Metric | Start target | Check |
|---|---|---|
| Frame rate | 60 fps for action games, 30 fps minimum for slower genres; stable frame pacing | Frame-time graph; 1 percent lows |
| Resolution | Docked (TV) and handheld modes each with a stable internal resolution; dynamic resolution allowed | Per-mode capture |
| Load time | Under 15 seconds to gameplay from boot, under 5 seconds between levels (estimates) | Stopwatch with the weakest storage |
| Memory | Below the platform budget (from platform documents) with 10 percent headroom | Peak over a soak test |
| Storage | Install size small enough for the target store tier; patches small | Build report |
| Battery (handheld) | No sustained max-power mode when idle; reasonable battery life | Handheld test |
| Hitches | No frame over 100 ms in normal play (estimate) | Frame-time log |
| Thermals | Stable after 2 hours | Soak test |
Method: profile on the console early (even with placeholder content); never optimise from PC numbers alone. Use `optimize` and `performance-engineer` for the approach.

## 5. Controller conversion
1. Map every action to the controller; list unmapped actions and fix them. No mouse-only actions.
2. Menus: focus-based navigation with a visible focus indicator; a default selected control on every screen; back button behaviour consistent (B or Circle per platform convention; from platform documents).
3. Glyphs: show the real button icons of the active controller; switch on controller change; never show keyboard keys.
4. Text entry: use the platform's system keyboard or an on-screen keyboard, not a physical keyboard.
5. Aim and cursor: replace pointer aiming with stick aiming, aim assist or a virtual cursor with an acceleration curve.
6. Dead zones, triggers and rumble: configurable dead zones; rumble can be turned off; analogue trigger thresholds.
7. Multiple controllers and players: assign players to controllers; handle join and leave.
8. Handheld controls: if the platform has touch or motion, decide whether to use them; never required.
9. Remapping: provide it, or a simple alternative layout.
10. Test: play the whole game with only a controller from a cold boot, without touching a keyboard or mouse, and record a video.

## 6. TV and handheld UX conversion
| Area | Rule of thumb (verify against platform documents) |
|---|---|
| Safe area | Keep HUD and text inside a margin; commonly 5 percent on each side; make it adjustable if the platform requires |
| Text size | Body text at least about 1/45 of screen height at TV distance; larger for handheld legibility needs a separate check |
| Contrast | High contrast against bright and dark scenes; avoid thin fonts |
| Layout | Large focus targets; no tiny hit areas; spacing for stick navigation |
| Handheld mode | Smaller physical screen at close range: verify that icons and text remain readable at handheld resolution |
| Resolution modes | Scale UI by resolution; test 720p, 1080p and 4K where relevant |
| Colour and HDR | Do not rely on colour alone; check HDR tone mapping if enabled |
| Loading and progress | Show progress; never a frozen screen |
| Pause and system overlays | Pause on system overlay or suspend; resume cleanly |
| Notifications | Prevent HUD clash with platform banners |
Use `mobile-ux` for touch layout lessons and `platform-targets` for TV and handheld input and UX.

## 7. Platform features checklist
1. User and profile: active user, user switching, guest users.
2. Saves: platform save API, size limits, backup and cloud saves, save migration from PC.
3. Achievements or trophies: map from PC; platform icons and descriptions.
4. Suspend and resume, background, app lifecycle events.
5. Controller, motion, touch, rumble, headphone and speaker handling.
6. Network: connection state, online privileges, matchmaking if used.
7. Store: DLC and in-game purchases using the platform's system (if any), demos, pre-orders.
8. Localisation: language selection and system language, region.
9. Platform branding: names, logos and terms (from platform documents).
10. Telemetry and crash reporting: allowed services and consent (see `player-analytics`, `legal-ethics`).

## 8. Risk register
| Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|
| Access delayed or declined | Medium | High | Apply early; strong pitch pack; keep a publisher or partner route | Producer |
| Engine or middleware incompatibility (plug-ins, web views) | Medium | High | Audit dependencies in phase 0; replace or drop | Lead engineer |
| Performance below target | Medium | High | Profile on console in phase 2; scope cuts; resolution scaling | Performance engineer |
| Save bugs after suspend or user switch | High | High | Atomic saves, test matrix, early soak | Lead engineer |
| Certification fails twice | Medium | Medium | Self-audit; hire QA with console experience | QA lead |
| Rating mismatch | Low | High | Content list and evidence; truthful questionnaire | Compliance officer |
| Cost overrun (kits, partner, QA) | Medium | Medium | Fixed-fee milestones; contingency 20 percent | Producer |
| Partner or publisher exits | Low | High | Contract exit terms; keep source and assets | Human lead |
| Schedule slip from PC patches | Medium | Medium | Freeze console branch; merge on a cadence | Producer |
| NDA material leaks into a public repository | Low | High | Private repo for platform material; pre-commit checks | Lead engineer |
| Localisation delay | Medium | Medium | Freeze text early; pseudo-localisation tests | Producer |
| Store page or date mismatch | Low | Medium | Coordinate with platform account manager | Human lead |
Review the register every week; add the cause of each slip.

## 9. Schedule and budget template
| Line | Estimate | Actual | Notes |
|---|---|---|---|
| Kits | <low to high> | | From programme |
| Porting partner or staff | <low to high> | | Quotes attached |
| UX and UI work | <low to high> | | |
| Localisation | <low to high> | | |
| QA and certification rounds | <low to high> | | At least two rounds |
| Ratings (digital free at some stores; physical fees) | <low to high> | | |
| Legal review | <low to high> | | Contracts |
| Marketing and trailers | <low to high> | | |
| Contingency 20 percent | | | |
Fill the schedule with dates per phase and a column "evidence" (video, log, email).

## 10. Worked example: a 2D platformer to Switch and Xbox
Game: Godot 4.x, 2D, 60 fps, 5 hours, keyboard and gamepad on PC, 14.99 USD, Steam launch done, 30 percent of wishlist requests ask for Switch (illustrative).
Route: porting partner for Switch (quote 20,000 to 40,000 USD, estimate), second platform later.
| Week | Work | Result |
|---|---|---|
| 1 | Readiness audit: fails suspend-mid-save, controller disconnect, glyph switching, text size at handheld | 3 fixes scoped |
| 2 | Human registers on the Nintendo Developer Portal; Switch access request with Steam page and trailer | Application filed |
| 2 to 6 | Fix audit failures on PC: atomic save with version; pause on controller loss; glyph system; UI scale | PC patch 1.2 released |
| 4 | Partner quote and contract (human reads and signs) | Agreement |
| 7 to 10 | Partner engine bring-up on kit; first playable level | Boots and runs |
| 11 to 14 | Platform services: user, saves, suspend, achievements | Internal tests pass |
| 13 to 16 | Performance: 60 fps docked, 60 fps handheld with a lower internal resolution | Targets met |
| 15 to 18 | UX conversion: safe area, glyphs, handheld text size | UX checklist passes |
| 17 to 20 | Localisation (6 languages), soak tests, ratings questionnaire (digital, no fee at Nintendo) | Test matrix passes; rating issued |
| 21 to 24 | Certification: round 1 finds a missing achievement unlock offline and an overflowing string; round 2 passes | Approved |
| 25 | Store page, price, release date; day-one patch plan | Scheduled |
| 26 | Release; support rota | Live |
Total: about 26 weeks (6 months), partner cost range as quoted, team effort about 0.6 FTE (estimates).
Next: Xbox via ID@Xbox concept (10 to 15 business days review) in parallel from week 8, using the same audit and an extended UX list. Decide the third platform after 30 days of Switch sales.

## 11. Review cadence and reporting
1. Weekly: status by phase, risk register changes, evidence links.
2. At each phase exit: a human confirms the criteria.
3. Before each submission: self-audit report and human approval.
4. After release: postmortem (`postmortem` skill) with the actual schedule and budget against the plan, to calibrate the next port.
