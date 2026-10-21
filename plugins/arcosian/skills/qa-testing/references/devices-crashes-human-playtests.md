# Devices, Crashes and Human Playtests

This file covers the parts of QA that need the real world: designing a device matrix and using device farms, symbolicating and triaging crashes and ANRs against Android vitals thresholds, running human playtests that produce usable evidence, and the bug template and severity definitions that keep every finding comparable. Pricing and threshold numbers are volatile and collected at the end with sources; everything else is stable practice. The through-line: hardware and humans find different bugs than code does, so budget time for both and make their output machine-readable.

## Contents
1. Device matrix design
2. Device farms and what they give you
3. Crash capture and symbolication
4. Crash triage procedure
5. ANRs and Android vitals
6. Store-driven technical checks
7. Human playtests: types and protocols
8. Playtest report format
9. Bug template
10. Severity and priority definitions
11. Interruption and compatibility test list
12. Worked examples
13. Checklists
14. Volatile facts (as of Oct 2026 — verify)

## 1. Device matrix design

Build the matrix in layers; stop when marginal coverage per device is small.

| Layer | Contents | Why |
|---|---|---|
| Reference tiers | Low, mid, high devices owned physically (see `mobile-performance`) | Perf budgets, soak, daily testing |
| Floor | Oldest supported OS and the lowest RAM device you promise | Memory kills, missing APIs |
| Ceiling | Latest OS beta or release, newest flagship | Behaviour changes, new gesture and permission models |
| OEM spread | At least three Android OEM skins (aggressive background killing, custom keyboards, notch handling differ) | OEM-specific crashes |
| GPU spread | Adreno, Mali and one other family (for example PowerVR or Xclipse class) | Driver and shader bugs |
| Form factors | Short, standard and tall aspect ratios, tablet if supported, foldable if you claim support | Layout and safe areas |
| Data-driven additions | Top models by active users and by crash share from live analytics | Real-world risk |

Procedure:
1. Collect distributions: RAM, chipset, OS version, screen size from store console or analytics (soft-launch data before launch).
2. Choose floor and tier devices first, then fill OEM, GPU and form-factor gaps.
3. Record the matrix as a table in the project (device, OS, RAM, GPU, tier, owner, farm availability) and treat changes as a decision.
4. Re-evaluate every release cycle against live crash share: add the models that crash, drop those that never differ.
5. Define test depth per tier: full regression and soak on tier devices; smoke plus crash and performance scenario on others.

Android versus iOS: iOS has a small, predictable device set; test the oldest supported iPhone and a current one, one iPad if supported, and the latest iOS beta early in the cycle. Android needs the wider spread above.

## 2. Device farms and what they give you

| Capability | Firebase Test Lab | AWS Device Farm | BrowserStack App Automate | Sauce Labs |
|---|---|---|---|---|
| Real devices | Yes (physical and virtual) | Yes | Yes | Yes |
| Game-oriented mode | Game Loop tests (Android, iOS): scripted demo loop, collect logs and crashes | Appium and instrumentation; custom | Appium based | AltTester and Appium on real devices |
| Best use | Wide crash sweep for a Unity or custom-engine build with a built-in demo loop | Pay-per-minute or unmetered slot automation | Parallel functional sessions | In-scene automation via AltTester |

What to run on a farm: install and launch, smoke playthrough, cold start, the worst-case perf scenario, and a long idle plus resume. What not to rely on: thermal truth, touch feel, audio device routing, real network conditions, battery drain.

Game Loop pattern: the app has a built-in automated mode launched by an intent (Android) or URL scheme (iOS); the farm runs it on each device and collects logs, video, screenshots and crashes. It needs no external driver, so it works for engines that Appium cannot see inside. Design the loop to exercise start, a level, a shop open and close, and an exit, then write a results file the farm retrieves.

Farm hygiene:
1. Upload the release build (and the matching symbol files separately).
2. Fix device list per run; record the device model, OS build and farm run ID in the report.
3. Fail the job on any crash or ANR detected.
4. Compare against per-device baselines; farm devices differ from your own in thermal and background state.
5. Costs: estimate cost per run as devices x minutes x rate; keep the PR path to a few devices and run the large sweep per release candidate. Verify current pricing (section 14).

## 3. Crash capture and symbolication

Capture:
- Crash reporter SDK (Firebase Crashlytics or an equivalent) initialised early, with breadcrumbs: scene or screen, last actions, memory warnings, seed, build id, device tier, thermal state.
- Native crashes (engine, plugins) and managed exceptions are separate streams; capture both.
- Store consoles (Play Console, App Store Connect) give crash and ANR data without an SDK; use them to cross-check SDK data.

Symbolication:
| Platform | What you need | Notes |
|---|---|---|
| iOS | dSYM files for every released build (bitcode-less builds produce them at archive time) | Upload dSYMs to the crash service in the release pipeline; keep them archived per build |
| Android native | Unstripped `.so` or NDK symbol files per build | Strip for shipping but archive symbols; match by build ID |
| Android managed (Java/Kotlin) | R8/ProGuard mapping file per build | Upload with the release |
| Unity IL2CPP | IL2CPP symbol files and, for managed stacks, the line-mapping files from the build | Unity generates symbol packages; archive per build (verify file names for your Unity version) |
| Godot | Export templates with debug symbols for native frames; GDScript errors are readable in logs | Keep the matching template build |

Rule: the release pipeline must archive, per build ID, all symbol and mapping files; an unsymbolicated crash is a lost bug. Add a CI check that fails the release if symbols are missing.

## 4. Crash triage procedure

1. Group by signature (top app frames after symbolication), then split by device model, OS version, app version, tier.
2. Rank by affected users, then by session impact (crash on launch beats crash in a rare screen), then by trend (new in this build).
3. Check whether the crash correlates with memory pressure (out-of-memory kills often show as abrupt exits without a stack), a specific device family (driver bug), or an SDK (ads, analytics, store).
4. Reproduce: the same device model if possible, the logged seed and breadcrumbs, on the farm if you do not own it.
5. Fix; add a regression test at the lowest layer; verify on the devices where it appeared.
6. Gate release on crash-free targets and vitals thresholds (below). Classify: launch crash or data-loss crash is a blocker.

Out-of-memory kills deserve a dedicated approach: they leave no crash report on iOS and look like a clean exit on Android. Detect them with a "previous session did not end cleanly" flag set at start and cleared on normal exit or background, combined with last-known memory and breadcrumbs.

## 5. ANRs and Android vitals

ANR (application not responding): Android flags an app whose main thread blocks long enough (input not processed in time, broadcast or service delays). For games the usual causes are blocking the UI/Activity thread with disk or network I/O, heavy SDK initialization, lock contention, and long native calls on the activity thread.

Triage: pull ANR traces (Play Console and `/data/anr` on debug devices), find the main-thread stack, identify the blocking call, move work off the thread or defer it.

Android vitals thresholds (volatile; section 14): the published bad-behaviour thresholds for user-perceived crash rate and ANR rate are applied overall and per phone model; exceeding them can reduce Play visibility or add listing warnings. Operating policy:
- Set internal targets with margin: for instance alarm at half of the threshold, block release at about 70%.
- Track per-model rates, since a single popular model can breach the per-model threshold while the overall rate looks healthy.
- Project rates before launch from farm and soft-launch data; during staged rollout watch vitals daily and halt rollout on trend.

## 6. Store-driven technical checks

- Android 16 KB page-size compliance: check native libraries with APK Analyzer; outdated plugins can ship 4 KB-aligned `.so` files even on a compliant engine version.
- Target API level and permission declarations match current store rules (see `store-release`).
- Release build is signed, debuggable off, logging reduced, test ads and test keys removed.
- Data safety and privacy declarations match SDK behaviour (see `legal-ethics`).

## 7. Human playtests: types and protocols

| Type | Purpose | Participants | When |
|---|---|---|---|
| Friends-and-family smoke | Find crashes and obvious confusion | 3-5 | Every milestone |
| Moderated FTUE test | Watch first-session behaviour and confusion | 5-8 from the target audience | Prototype, alpha, before soft launch |
| Unmoderated remote test | Breadth: devices and contexts | 15-50 | Beta |
| Soft-launch cohort | Real retention and monetization data | Thousands, a live market | Pre-launch (see `liveops` and `player-analytics`) |
| Expert review | Heuristics: UX, economy, ethics | 2-3 specialists | Design review gates |

Protocol for a moderated session (20-30 minutes):
1. Recruit from the target audience, not colleagues; screen for genre familiarity.
2. Brief minimally: "play as you normally would"; no hints about controls.
3. Think-aloud optional; observe silently; record screen and touches if possible.
4. Note timestamps of: first confusion, first smile or frustration, first quit-intent, time to first reward, and any softlock.
5. Post-session questions: what was the goal, what would you do next, what confused you, would you play again (and why); avoid leading questions.
6. Do not explain or defend the design in the session.
7. Synthesize: count how many of N participants hit each issue; issues hit by two or more in five are usually systemic.

Five users rule of thumb: small samples find the most frequent usability problems quickly (a long-standing usability-testing heuristic attributed to Nielsen's work); they do not measure rates. Use larger samples or telemetry for rates.

Persona playtests by the `player-simulator` agent are cheap pre-checks (they role-play defined personas and report friction) and write `mode: "persona"` reports; they do not replace real humans for fun judgments.

## 8. Playtest report format

Human and persona sessions write the same playtest-report JSON used for scripted and bot runs: `mode: "human"` (or `"persona"`), `persona` description, `runs` equal to participants, `metrics` (average session seconds, time to first reward, softlocks, crashes), `findings` with severity, `repro`, and `screenshots`. Add qualitative notes under `notes`. Schema: `${CLAUDE_PLUGIN_ROOT}/scripts/schemas/playtest-report.schema.json`. A report with any crash or blocker finding must carry verdict `fail`.

Summarize per session in a table: participant profile, device, duration, goal completion, top three friction points, quotes (short), and recommended changes tied to findings.

## 9. Bug template

```
Title: <component> - <symptom> (one line, searchable)
Severity: blocker | major | minor | polish     Priority: P0-P3
Build: <version+commit, release|dev>     Device: <model, OS, RAM, tier>
Seed / save: <seed, step index, or attached save file>
Frequency: always | often (x of y) | rare
Steps to reproduce:
  1. ...
Expected: ...
Actual: ...
Evidence: <screenshot, video, log excerpt, crash group link, playtest-report path>
Suspected area / first bad build: <if known from bisect>
Player impact: <who is affected, how badly, workaround?>
```

Rules: one bug per report; reproducible steps or a seed; attach evidence; state frequency honestly; do not diagnose in the title.

## 10. Severity and priority definitions

| Severity | Definition (player impact) | Examples | Release rule |
|---|---|---|---|
| Blocker | Cannot ship: crash on launch or in the core loop, data or purchase loss, progression blocked, legal or store-policy violation | Save corrupts on update; softlock in a mandatory level; purchase not delivered | Must fix; gate fails |
| Major | Hurts the experience of many players, no good workaround | Frequent crash on a popular device; broken daily reward; severe layout break on common aspect ratio | Fix before release unless explicitly waived by producer and principal |
| Minor | Noticeable, workaround exists, limited reach | Misaligned label in one locale; rare visual glitch | Fix as capacity allows; track |
| Polish | Nice to fix, no gameplay or comprehension impact | Slight animation roughness | Backlog |

Priority is a scheduling decision (P0 now, P1 this milestone, P2 next, P3 backlog) set by severity, reach, frequency and cost to fix; severity itself never depends on effort. Severity matches the playtest-report schema: blocker, major, minor, polish.

## 11. Interruption and compatibility test list

- Incoming call, alarm, notification shade pull, volume buttons, silent switch, headphones plugged and unplugged, Bluetooth audio latency.
- Background for 10 seconds, 10 minutes, hours; return after memory kill; return after OS update of the webview or a store SDK.
- Airplane mode on and off during a purchase, ad load, cloud sync, asset download.
- Low storage during update or asset download; low battery mode; battery saver limits.
- System clock changed forward and back; time zone change; daylight saving boundary.
- Device rotation if supported; split screen or multi-window if enabled; foldable posture changes.
- Accessibility: large font, bold text, reduced motion, screen reader basics for menus, color-blind modes.
- Permissions: deny, deny and do not ask again, grant then revoke in settings.
- Locale switch mid-session; right-to-left language; long strings.
- Input: multi-touch, palm contact, gesture-navigation edge swipes, stylus.

## 12. Worked examples

**A. Crash cluster on one model.** Crash service shows 6% of sessions crash on a single mid-range model, overall rate low. Symbolicated stack points into a GPU driver call in a shader prewarm routine. The farm reproduces it on that model. Fix: skip prewarm for that GPU family via the tier config override, plus a remote-config switch; verify on the farm; add the model to the matrix. Per-model threshold avoided.

**B. ANR at startup.** Play Console shows ANRs at cold start on low-RAM devices. Main thread stack shows synchronous analytics SDK init plus asset index load. Fix: defer SDK init until after the first frame and load the asset index asynchronously; cold start improves, ANR rate falls on the next staged rollout step.

**C. Human playtest finds the real FTUE bug.** Four of five participants tap the wrong area of the first screen because the primary action sits at the thumb-unreachable top of a tall screen. Bots and scripted tests all passed since they invoke actions directly. Fix is a layout change; the lesson is logged in the playtest report as a major finding.

## 13. Checklists

Release device sweep:
- [ ] Matrix current; farm run on all matrix devices for the release candidate.
- [ ] Zero new crashes or ANRs; per-model rates projected under thresholds with margin.
- [ ] Symbols and mappings archived and uploaded for this build.
- [ ] Interruption list executed on tier devices.
- [ ] Soak done on low and mid devices (see `mobile-performance`).

Human playtest:
- [ ] Target-audience participants, device and context recorded.
- [ ] Protocol followed, no coaching; timestamps captured.
- [ ] Findings counted across participants; severities assigned by the definitions above.
- [ ] Report written in playtest-report format; blockers filed as bugs with the template.

## 14. Volatile facts (as of Oct 2026 — verify)

| Fact | Source |
|---|---|
| Android vitals bad-behaviour thresholds: user-perceived crash rate 1.09% and ANR rate 0.47% overall; 8% per phone model; exceeding them can reduce Play visibility or add listing warnings | https://developer.android.com/games/optimize/vitals ; https://android-developers.googleblog.com/2022/10/raising-bar-on-technical-quality-on-google-play.html |
| Firebase Test Lab supports Game Loop, instrumentation and Robo tests; third-party pricing about $1 per virtual-device-hour and $5 per physical-device-hour on Blaze, free tier 10 virtual and 5 physical tests per day | https://blog.back4app.com/firebase-test-lab/ ; https://www.drizz.dev/post/firebase-test-lab-guide |
| AWS Device Farm reported at $0.17 per device-minute or $250 per slot per month unmetered | Verify on the AWS Device Farm pricing page |
| BrowserStack App Automate from about $199 per month per parallel (third-party) | Verify on BrowserStack pricing |
| Sauce Labs runs AltTester tests on real devices; iOS sessions use Appium WebDriverAgent | https://docs.saucelabs.com/mobile-apps/automated-testing/alttester/unity/ |
| Google Play 16 KB page-size requirement; Unity support from 6000.0.38f1 and 6000.1+; stale plugin libraries may be flagged | https://discussions.unity.com/t/info-unity-engine-support-for-16-kb-memory-page-sizes-android-15/1589588 |
