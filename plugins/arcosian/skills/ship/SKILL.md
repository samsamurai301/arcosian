---
name: ship
description: Release pipeline for mobile games - compliance pre-flight, version bump, signed builds via CI templates and fastlane, store metadata and screenshots, upload to TestFlight or Play internal testing, release report, and the human-only steps. Never submits to production review without explicit human approval. Use when the user says "ship it", "build a release", "upload to TestFlight", "Play internal", "store listing" or "release candidate".
argument-hint: "[ios|android|all] [internal|beta]"
---

# Ship

## When to use
When a build should leave the developer machine: internal testing, beta, or (with approval) production. Load `store-release`, `legal-ethics` and `mobile-performance`. Delegate to `arcosian:release-manager` (builds, signing, metadata) and `arcosian:compliance-officer` (policy, privacy, age, AI disclosure). The full gate run is `/arcosian:release-candidate`.

## Inputs
`$ARGUMENTS`: platform `ios`, `android` or `all` (default `all` from `config.platforms`), and track `internal` (default) or `beta`. A request for a production release is handled in step 11 only.

## Procedure
1. **State check.** `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py status` and `gs.py validate`. Every feature in scope must be `done` with all five gates passing; otherwise stop and route to `build-feature`. Check `config.tier`: store builds below `slice` are rarely worth the review overhead.
2. **Compliance pre-flight.** `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/compliance_preflight.py --project . --platform <p> --json`. Exit 1 blocks the release; fix every blocker (privacy manifest, permission strings, target API level, ATT/consent flows, age rating inputs, loot-box and AI-disclosure notes, licences). Warnings need a written decision in the release report.
3. **Perf and licence gates.** Latest `perf-report` must pass `perf_budget.py --report <path> --contract .gamestudio/contract.json`; run `licence_check {}` on the manifest. A fail here blocks the build.
4. **Version bump.** Semantic marketing version plus monotonically increasing build number (iOS build, Android versionCode). Update the engine's project settings, commit with a clear message and tag only when the user approves committing. Never reuse a build number a store has already seen.
5. **Build.** Use the CI templates in `${CLAUDE_PLUGIN_ROOT}/templates/ci/` (GitHub Actions for Godot or Unity, fastlane, Codemagic). Local equivalents are in the engine commands (BLUEPRINT section 13): Godot `--export-release "Android" <out>.aab` and `"iOS"` to an Xcode project; Unity `BuildScript.BuildAndroid` / `BuildIOS`. Android ships an AAB, not an APK. iOS archives need a Mac runner and signing. Keystores and certificates live in CI secrets or the user's keychain; never in the repo, never in `.gamestudio/`.
6. **Fastlane lanes.** Typical lanes: `ios beta` (match/signing, build, `pilot` upload to TestFlight), `android internal` (`supply` upload to the internal track), `metadata` (deliver/supply metadata only), `screenshots`. Read the lanes in `templates/ci/fastlane/` and adapt IDs; credentials arrive from environment variables, never typed into files.
7. **Store metadata.** `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/store_metadata.py --contract .gamestudio/contract.json --out store/ --locales en-US[,de-DE] --json` drafts title, subtitle, short and long descriptions, keywords, what's-new text and category. Review for claims you cannot back, trademark use, and character limits. `arcosian:art-director` reviews the icon and screenshot captions. Localisation depth: see `accessibility-localization`.
8. **Screenshots.** Use the engine's screenshot mode (Godot: `screenshot_mode.gd --screens=menu,game,results`; Unity: its capture tool) at each required device size, on a real renderer. Show real gameplay first; no mock UI that does not exist.
9. **Upload to internal testing only.** TestFlight (internal group) and Play internal testing are the automated ceiling. Run the lane, record build id and track in the release report. Install on at least one low-tier and one current device and run the smoke playthrough.
10. **Release report.** Write `.gamestudio/reports/release-<version>-<date>.md`: version/build, gates with evidence paths, preflight output summary, warnings and decisions, known issues, rollback plan, metadata summary, who approved what. Log with `gs.py progress`.
11. **Production submission: human approval only.** Submitting for store review, promoting a track to production, or staged rollout changes are actions only the user may authorise in chat. The PreToolUse hook asks before such commands; do not try to route around it (no alternative scripts, no API calls that achieve the same). Prepare everything, present the report, and wait.

## Human-only steps
| Step | Why |
|---|---|
| Create the app record (App Store Connect, Play Console) | Legal identity, agreements, payments |
| First Play upload of a new app | Must be done in the console before automation works |
| Closed testing for new personal Play developer accounts (created after Nov 13, 2023) | Google requires at least 12 testers opted in to a closed test for 14 continuous days before you can apply for production access (checked 2026-10-20 at the Play Console Help page linked under Volatile facts); plan the calendar around it |
| Unity licence activation on CI | Account-bound |
| Accepting agreements, tax and banking forms | Legal |
| Declaring age ratings and data-safety answers | Accuracy is the developer's liability |

## Track ladder

| Track | Audience | Gate to enter | Automation |
|---|---|---|---|
| Internal (TestFlight internal / Play internal) | Team | Steps 1-8 | Full |
| Beta (TestFlight external / Play closed or open) | Invited testers | Internal smoke pass, privacy and metadata ready | Upload automated; external review is a store action, ask the user |
| Production | Public | Beta feedback triaged, human approval | Manual, human-approved |

External TestFlight groups and open/closed Play tracks may trigger store review or tester-count rules; treat promotion past internal as needing a go-ahead from the user.

## Release-day checklist
- [ ] Preflight, perf and licence gates green, evidence paths in the report
- [ ] Version/build bumped once, tag planned
- [ ] Crash reporting and analytics enabled in the release config, debug menus off
- [ ] Test purchase and restore flow verified in sandbox (see `monetization`)
- [ ] Consent and privacy flows verified on a clean install
- [ ] Remote config defaults safe if the server is unreachable
- [ ] Rollback plan: previous build kept, kill switch via remote config
- [ ] Release report written, user has the link

## Worked example: first beta of a Godot puzzle game
User runs `ship android internal`. Gate check passes, preflight reports one warning (no privacy policy URL in metadata): the officer drafts text, the user supplies the URL. Version 0.3.0 build 14 is exported as an AAB through the CI template, uploaded to Play internal with the fastlane lane, installed on a low-tier phone, smoke playthrough passes. The report lists the warning decision and notes that the Play app record already exists. Nothing is promoted further; the user decides when.

## Go / no-go rubric
| Signal | Go | No-go |
|---|---|---|
| Crash-free sessions in internal test | At or above the target in the contract | Below target or unexplained crashes |
| FTUE on a clean install | Reaches first reward within `ftue.aha_seconds_target` | Dead ends, softlocks |
| Store assets | Real screenshots, reviewed text | Placeholder art, unverifiable claims |
| Privacy and consent | Flows verified, policy URL live | Missing or untested |
| Rollback | Previous build and kill switch ready | None |

## Outputs
Version commits, build artifacts (outside the repo), `store/` metadata, screenshots, `.gamestudio/reports/release-<version>-<date>.md`, preflight JSON in evidence.

## Quality gates
- Preflight exit 0, perf gate pass, licences clean, all five gates on in-scope features.
- Build installs and passes the smoke playthrough on the lowest device tier.
- Version and build number unique; secrets not in the working tree.
- Metadata contains no unverifiable claims; AI-generated content is disclosed where a store requires it.
- Production submission had explicit human approval in chat, recorded in the report.

## Failure modes and recovery
| Symptom | Recovery |
|---|---|
| Preflight blocker | Fix, rerun; do not suppress |
| Signing or provisioning error | Re-run match/sync, check bundle id and team; human may need to renew certificates |
| Rejected upload (duplicate build number) | Bump the build number, rebuild |
| Review rejection | Read the cited guideline, fix, document in report, resubmit only with human approval |
| Crash only on release build | Compare stripping/IL2CPP/minify settings; symbolicate with uploaded symbols |
| AAB too large | Run `optimize`; use asset packs or texture compression changes |

## Volatile facts (as of Oct 2026 - verify)
Store rules (target API level, SDK minimums, privacy manifests, tester requirements, AI-disclosure, age-rating questionnaires) change each year. Check before every release: https://developer.apple.com/app-store/review/guidelines/ , https://developer.android.com/google/play/requirements/target-sdk , https://support.google.com/googleplay/android-developer/answer/14151465 .

## Related skills
`store-release`, `legal-ethics`, `mobile-performance`, `qa-testing`, `marketing-ua`, `operate`.
