---
name: store-release
description: Store release knowledge for mobile games - headless builds, signing, fastlane, TestFlight and Play tracks, CI choices, versioning, App Store and Google Play requirements (SDK floors, privacy manifests, PBL, 16 KB pages, Data safety), ASO, and the pre-flight checklist. Use when asked "how do I ship to the App Store", "Play rejected my build", "set up fastlane", "write store listing", "why was I rejected" or "release checklist".
---

# Store Release

## What this skill gives you
- A repeatable release pipeline: engine export, signing, upload to TestFlight or Play internal testing, promotion, rollback, and which steps only a human can do.
- The current store gates (Apple and Google) as a checklist, with the volatile numbers isolated and sourced.
- A rejection triage table: symptom, usual cause, fix.
- ASO and listing craft, including store experiments, and how listing text maps to `store_metadata.py` limits.
- A pre-flight checklist that mirrors what `compliance_preflight.py` automates and what it cannot see.

## Core models
**1. Release is a pipeline of gates, not an event.** Every build passes the same ordered gates: content gates (five gates of the studio), compliance gates (policy, privacy, licences), packaging gates (signing, SDK floor, bitness, page size), distribution gates (internal, closed or beta, production). A failure at a later gate that could have been detected earlier is a process bug; move the check left into CI.

**2. Two clocks.** The store clock (review latency, staged rollout, processing time) and the policy clock (SDK floors and deadlines that change every year). Plan releases with slack on the store clock; recheck the policy clock at every minor release because a deadline can turn a routine update into a blocked one.

**3. The binary is cheap, the metadata is expensive.** Rejections are far more often about metadata, privacy declarations, payments and age rating than about crashes. Treat the App Privacy answers, Data safety form, age questionnaire and review notes as code: generated from the actual SDK manifest, reviewed, versioned.

**4. API keys, never passwords.** A headless pipeline authenticates with an App Store Connect Team API key and a Play service account. If a step needs an Apple ID session, that step is human-only and should be done once, by hand, and documented.

**5. Reversibility ladder.** Internal test (instant, reversible) < closed/beta (reversible) < production staged rollout (halt, but cannot recall installs) < full rollout. Nothing past the first rung happens without explicit human approval (`ship` skill, step 11).

**6. Version identity.** Marketing version (semver-like, human) and build number (integer, monotonic, per store). Never reuse a build number. Unity or Godot project settings are the single source; CI computes the next build number from the store (latest TestFlight build +1; Play versionCode strictly above the highest uploaded).

## Decision procedures

### A. First release of a new game (one-time setup)
1. Developer accounts: Apple Developer Program and Google Play Console (human, paid, identity checks; allow days to weeks).
2. Create the app record by hand in App Store Connect and Play Console (fastlane `produce` does not work with API keys).
3. Choose the bundle id / package name now; it cannot change after release.
4. Create credentials: ASC Team API key (.p8), Play service account JSON, Android upload keystore. Store in CI secrets and a password manager, never in the repo.
5. Upload the first AAB through the Play Console UI (API uploads often fail until one exists), enrol in Play App Signing.
6. Fill App Privacy, Data safety, age rating (Apple questionnaire, IARC), content declarations, ads declaration, target audience.
7. If the developer account is a new personal Play account, read the closed-testing requirement in `references/store-requirements-2026.md` and start the clock early.
8. Run `compliance_preflight.py` and fix blockers. Then ship an internal build and install it on real devices.

### B. Routine update
1. Bump build number automatically; bump marketing version if user-visible.
2. `compliance_preflight.py --project . --platform all --json`; blockers stop the line.
3. CI build (Linux for Android, macOS for iOS), upload to internal tracks.
4. Smoke playthrough on one low-tier and one current device.
5. Human approves promotion; start with staged rollout on Play and phased release on iOS.
6. Watch crash-free rate and ANR/crash vitals for the first day; halt if regressions exceed the contract thresholds.

### C. Choosing the CI host
| Situation | Pick | Why |
|---|---|---|
| Godot, small team, agent-driven | GitHub Actions + godot-ci image + macOS job for iOS | YAML and CLI are transparent for agents |
| Unity, small team | GameCI unity-builder + fastlane on macOS | Licence activation is the fragile part; plan for it |
| Little DevOps appetite | Codemagic | Built-in signing UI and Unity support |
| Already Xcode-only | Xcode Cloud | Fewer moving parts for iOS only |
Prices change; see volatile facts in `references/release-pipeline.md`.

### D. Triage a rejection
1. Read the exact guideline number and reviewer message; do not guess.
2. Match to the common rejection table in `references/store-requirements-2026.md`.
3. Fix the cause, not just the symptom (e.g. a missing purpose string usually means an SDK you did not audit).
4. Reply in Resolution Center with specifics and a demo account if login is involved; never argue in generalities.
5. Record the rejection and fix in the postmortem log and add a pre-flight check so it cannot recur.

### E. Hotfix
Skip nothing except waiting: run pre-flight, internal smoke, then request expedited review only when a genuine crash or legal issue exists (Apple offers expedite requests; use sparingly). Prepare rollback: keep the previous build promotable, and use remote config kill switches for features.

### F. Gate table (what blocks what)
| Gate | Evidence | Automated by | Blocks |
|---|---|---|---|
| Five studio gates | `gs.py validate` shows feature `done` | `gs.py` | any store build |
| Perf budget | perf report passes | `perf_budget.py` | any store build |
| Licence and provenance | licence check clean | `licence_check` tool | any store build |
| SDK floor, bitness, page size | pre-flight blockers empty | `compliance_preflight.py` | upload |
| Privacy and age declarations | forms match SDK manifest | human + compliance-officer | review submission |
| Smoke on real devices | release report entry | human or `playtest` | promotion |
| Human approval | chat approval recorded | human | production |

### G. Worked example: Godot game, first Android internal build
1. Pre-flight reports `godot.16kb` blocker because project is on 4.4.x; upgrade to 4.5 or later and re-export (the engine fix for 16 KB pages landed in 4.5).
2. Pre-flight reports `android.target_sdk` blocker; set gradle target_sdk to 36, enable Gradle build and AAB format, keep arm64-v8a.
3. Set version code 1, sign with the upload keystore from CI secrets, upload via Play Console once, then use the `internal` lane afterwards.
4. Record build id and track in `.gamestudio/reports/release-<version>-<date>.md`; stop and ask the human before any promotion.

### H. When in doubt about a policy
Quote the official page, note its retrieval date in the release report, and mark the item as "verify". A remembered rule that is wrong costs a rejection cycle; a rechecked rule costs a minute.

## Mobile specifics
- iOS archives need macOS and signing; Android builds run anywhere. Split the pipeline: Linux export, macOS finish.
- Android ships AAB through Play App Signing; sideload APKs only for testers.
- Device matrix: test on at least one low RAM Android, one current iPhone, one tablet if the game supports tablets (Android large-screen behaviour changes with newer target APIs).
- Review is human: the reviewer must reach gameplay in under a minute. Provide demo credentials, disable region locks, and list any hidden settings in review notes.
- In-app purchases must be reviewable: sandbox products approved and attached to the version.
- Soft launch is a store-listing exercise too: country-limited availability on both stores before global release.

## Anti-patterns
- Typing credentials into fastlane files or the repo (use environment variables).
- Shipping with `target_sdk` "automatic" so the result depends on the build machine.
- Reusing marketing screenshots with UI that does not exist in the game (a common metadata rejection).
- Treating the privacy form as a one-time task; adding an SDK without updating it.
- Promoting to production from CI without a human gate.
- One giant release containing a new SDK, a new monetization model and a new engine version; split them so a rejection is attributable.
- Ignoring the closed-test gate on new personal Play accounts until launch week.
- Relying on remembered deadlines instead of rereading the volatile facts.

## Using the ontology
- Release readiness is derived from `.gamestudio/features.json` (check it with `gs.py status --json`): all features `done` with five gates, then the `release-candidate` workflow.
- `.gamestudio/contract.json` supplies title, category, audience (`age_min`), monetization flags (ads, random rewards) consumed by `store_metadata.py` and `compliance_preflight.py`.
- Scripts: `${CLAUDE_PLUGIN_ROOT}/scripts/compliance_preflight.py` (`--project`, `--platform ios|android|all`, `--json`), `${CLAUDE_PLUGIN_ROOT}/scripts/store_metadata.py` (`--contract`, `--out`, `--locales`), `${CLAUDE_PLUGIN_ROOT}/scripts/perf_budget.py` for the perf gate. CI templates live in `templates/ci/` (GitHub, Codemagic, fastlane).
- Process skill: `ship`; workflow: `/arcosian:release-candidate`; agents: `arcosian:release-manager`, `arcosian:compliance-officer`.

## Reference library
| File | What it contains | When to read |
|---|---|---|
| `references/release-pipeline.md` | Headless builds, signing, fastlane lanes, TestFlight, Play tracks, CI options, versioning, human-only steps | Setting up or debugging the pipeline |
| `references/store-requirements-2026.md` | Apple and Google gates, privacy manifests, age ratings, Data safety, common rejections; volatile facts with sources | Before any submission, after any rejection |
| `references/aso-and-submission.md` | ASO, store experiments, metadata limits, pre-flight checklist mapped to the scripts, review notes | Writing the listing, final submission prep |

## Related skills
- `ship`: the process skill that runs this knowledge as a pipeline with human checkpoints.
- `legal-ethics`: privacy, children, loot-box and licence rules behind the store forms.
- `monetization`: IAP and ad setup that must match store declarations.
- `marketing-ua`: user acquisition that depends on store listing conversion.
- `mobile-performance`: perf budgets and device tiers used in the release gate.
- `qa-testing`: smoke playthroughs and device matrix.
- `accessibility-localization`: store localization and accessibility declarations.
