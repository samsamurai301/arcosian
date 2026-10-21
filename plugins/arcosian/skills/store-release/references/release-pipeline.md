# Release pipeline

Summary: this file describes how a mobile game binary gets from a repository to TestFlight and Google Play testing tracks without a human at a keyboard, and which steps remain human. The shape is: headless engine export (Linux where possible), iOS finish on macOS with fastlane and an App Store Connect Team API key, Android finish with fastlane `supply` or the Play Developer API and a service account, version numbers computed from the store, and an explicit human gate before production. Volatile numbers (CI prices, tool versions) are collected at the end with sources.

## Contents
1. Pipeline overview
2. Headless builds: Godot
3. Headless builds: Unity
4. Signing: Android
5. Signing: iOS
6. fastlane lanes
7. TestFlight
8. Google Play tracks
9. CI options
10. Versioning
11. Secrets handling
12. Human-only steps
13. Failure modes
14. Volatile facts (as of Oct 2026 - verify)
15. Pipeline acceptance test and rollback drill

## 1. Pipeline overview
```
commit/tag -> gates (tests, perf, licences, preflight)
          -> export (Linux) -> AAB (signed with upload key)
          -> export (Linux or macOS) -> Xcode project
          -> macOS runner: match -> gym -> pilot (TestFlight internal)
          -> supply (Play internal)
          -> release report -> HUMAN: promote / submit for review
```
Principles:
- Idempotent lanes: rerunning a lane must not corrupt state (build numbers come from the store, not a local counter).
- One command per outcome: `fastlane ios beta`, `fastlane android internal`. Agents call lanes; they do not improvise store API calls.
- Artifacts are kept: AAB, IPA, dSYMs, mapping files, symbols. Crash triage needs them for the life of the version.
- Every lane has a dry mode or an obvious earlier stage that can be run without uploading.

## 2. Headless builds: Godot
- Use an export container pinned to the exact engine tag (the godot-ci image family is the common choice). Never use a floating `latest`.
- Export templates must match the editor version exactly.
- Android export, release AAB: `godot --headless --path . --export-release "Android" build/game.aab`. Requires a custom Gradle build enabled in the preset, AAB format, arm64-v8a, target SDK per the store floor, Android SDK and JDK in the image.
- iOS export produces an Xcode project (`--export-release "iOS" build/ios/Game.xcodeproj`); archiving requires macOS and Xcode, so the export may run on Linux but the archive step runs on macOS. Many teams export on the macOS runner to avoid copying large trees.
- Pin plugin versions (billing, ads, analytics) in the repo; export fails mysteriously when an addon is missing, so run an import step first (`godot --headless --import`).
- Check the preset for `version/code`, `version/name` and signing keys supplied by environment variables, not literals.
- Engine floor for Google's 16 KB page requirement: Godot 4.5 or later (see requirements file).

## 3. Headless builds: Unity
- GameCI `unity-builder` (Docker-based, Linux) can build Android AAB and an iOS Xcode project; archive on macOS.
- A `BuildScript` with static entry points (`BuildAndroid`, `BuildIOS`) invoked through `-executeMethod` keeps settings in code and out of CI YAML. Read version and build number from environment variables.
- Licensing is the fragile part of unattended Unity CI. A Personal activation file is machine bound; a Pro serial or licence server is more robust. Decide before building the pipeline, not after.
- Android: IL2CPP scripting backend, ARM64 enabled, target API at the store floor, AAB output, Gradle caches mounted between runs for speed.
- iOS: set the signing team and manual or automatic signing consistently with fastlane `match`; mixing them is the top cause of "no signing certificate" errors.
- Library caching is the biggest speed-up; hash `Packages/manifest.json` and `ProjectSettings` for the cache key.

## 4. Signing: Android
| Item | Rule |
|---|---|
| App signing | Use Play App Signing. Google holds the app signing key. |
| Upload key | You hold it in CI secrets; it can be reset through Play support if lost. |
| Format | AAB for Play. APK only for direct tester installs. |
| Keystore storage | Base64 in a CI secret, decoded into a temp file at job time, deleted after. |
| Debug vs release | Never publish debug-signed builds; the pre-flight should detect debug flags. |
| Rotation | Keep a documented upload-key reset procedure; test it on a throwaway app once. |

Backup the upload keystore and its passwords in a password manager owned by a human. A pipeline whose only key copy lives in a CI secret store is a single point of failure.

## 5. Signing: iOS
- Prefer `fastlane match` in readonly mode on CI: certificates and profiles are stored encrypted in a private repo or bucket, created once by a human on a trusted machine.
- Use an App Store Connect Team API key (not an individual key; individual keys cannot use provisioning endpoints, per fastlane docs).
- Distribution certificate count is limited per account; do not mint a new one per CI run. `match` exists to prevent that.
- Entitlements: add capabilities (In-App Purchase, Push, Sign in with Apple, Game Center) in the developer portal first, then regenerate profiles. A profile that lacks a capability fails at archive or at upload validation.
- Export method `app-store` for TestFlight and store builds; `ad-hoc` only for registered device testing.
- Push: use APNs auth keys (.p8) rather than certificates; certificates expire yearly and need human renewal.

## 6. fastlane lanes
The repo template lives at `templates/ci/fastlane/` (`Fastfile`, `Appfile`, `Matchfile`, `Gemfile`). Typical lanes:

| Lane | Does | Never does |
|---|---|---|
| `ios beta` | `match` readonly, next build number from TestFlight, `gym`, `pilot` to internal testers | submit for review, distribute externally |
| `ios metadata` | `deliver` with `skip_binary_upload`, `submit_for_review: false` | touch the binary |
| `ios release` (human-triggered) | prepares a version with an existing build | submit without explicit approval |
| `android internal` | `supply` AAB to the internal track | promote |
| `android metadata` | `supply` listing text and images only | upload a binary |
| `android promote` (human-triggered) | moves a build between tracks | roll out to 100% by default |

Lane design rules:
1. Read credentials from environment (`ASC_KEY_ID`, `ASC_ISSUER_ID`, key content, `SUPPLY_JSON_KEY_DATA`); the lane fails fast if one is missing.
2. Compute the build number from the store inside the lane; do not accept it as an argument from an agent.
3. Keep `submit_for_review` false in committed lanes; the production lane is a separate, manually dispatched workflow.
4. Add `ensure_git_status_clean` before version bumps in local use; in CI, commit bumps back only when the human wants a tag.
5. Cache Ruby gems with a pinned `Gemfile.lock`.

Known limits (fastlane docs, summarized): `produce` cannot create app records with an API key, `pem` needs an Apple ID, and `precheck` does not verify in-app purchase metadata. Plan one-time manual steps accordingly. A 2026 fastlane release changed how API keys are read, so pin the fastlane version and read its changelog before bumping.

Sketch of a safe beta lane (Ruby):
```ruby
lane :beta do
  key = app_store_connect_api_key(key_id: ENV["ASC_KEY_ID"], issuer_id: ENV["ASC_ISSUER_ID"], key_content: ENV["ASC_KEY_CONTENT"])
  match(type: "appstore", readonly: true, api_key: key)
  n = latest_testflight_build_number(api_key: key) + 1
  increment_build_number(build_number: n)
  gym(export_method: "app-store")
  pilot(api_key: key, distribute_external: false, submit_beta_review: false)
end
```

## 7. TestFlight
- Internal testers (members of your team, limited count) receive builds after processing without beta review; external groups need Beta App Review for the first build of each version.
- Apple also offers a Build Upload API and webhooks (introduced in 2025) so an agent can react to "build processed" events rather than poll. Webhook signatures use a shared secret; verify them against Apple documentation before trusting a third-party description.
- Typical processing time varies; build the pipeline to wait on state, not on a fixed sleep.
- Export compliance: declare encryption use (`ITSAppUsesNonExemptEncryption` in Info.plist) so every build does not stall on a question.
- Builds expire after a period; keep release candidates fresh.
- Collect TestFlight crash and screenshot feedback; the feedback API exists but triage is still human or `qa-lead`.

## 8. Google Play tracks
| Track | Use | Notes |
|---|---|---|
| Internal testing | Fast loops, up to a small tester list | No review gating of the kind production has; available quickly |
| Closed testing | Wider alpha/beta groups, required step for some new accounts | New personal accounts must meet a closed-test requirement before production access (see volatile facts) |
| Open testing | Public beta | Visible in store; listing must be ready |
| Production | Everyone | Use staged rollout |

Procedures:
1. Upload the first AAB through the Console UI for a new app, then automate.
2. Service account: create in Google Cloud, grant it release permissions in Play Console, and store the JSON as a secret.
3. Use `supply --track internal` for CI; use `--rollout 0.05`-style staged values for production only through the human-triggered lane.
4. Edits are transactional in the Android Publisher API: `edits.insert`, upload bundle, update track, `edits.commit`. A failed commit leaves nothing half-published.
5. Check Play Console pre-launch report and Android vitals after each upload; Play can surface device-specific crashes you never saw.
6. Declare Data safety, ads, content rating, target audience and app access before the first review.

## 9. CI options
| Option | Strengths | Weaknesses | Best for |
|---|---|---|---|
| GitHub Actions + fastlane | Transparent YAML, portable, agent-friendly | You manage Mac runner cost and signing setup | Default choice |
| Codemagic | Signing UI, Unity/Godot friendly, generous small free tier | Hosted lock-in of config style | Small teams, low ops |
| Unity Build Automation | Integrated with Unity | Weaker for custom fastlane-style steps | Unity-only shops |
| Xcode Cloud | Native Apple integration | iOS only, less flexible | Native iOS |
| Self-hosted Mac mini | Cost control, fast caches | You patch and secure it | High volume |

Templates available in this plugin: `templates/ci/github/godot-ci.yml`, `templates/ci/github/unity-ci.yml`, `templates/ci/codemagic/codemagic.yaml`.

Cost control: build iOS only on release branches or tags; cache engine imports; skip the macOS runner on pull requests; run unit tests and pre-flight on Linux.

## 10. Versioning
- Marketing version: `MAJOR.MINOR.PATCH`; bump MINOR for content drops, PATCH for fixes. Keep it identical on iOS and Android unless a platform-only fix demands otherwise.
- Build number: iOS `CFBundleVersion` unique and increasing within a marketing version (best to keep it increasing globally); Android `versionCode` a positive integer that must increase on every upload and has a maximum value set by the platform.
- Derive both from CI: `BUILD_NUMBER = max(store latest) + 1`. Do not tie to the git commit count if history can be rewritten.
- Tags: `v1.4.0` on the commit that produced the approved build; tag only with user approval.
- Data-driven rollbacks: store the git SHA and build number in crash reports and analytics, so a bad version is traceable.
- Save-file and server-API versions are separate from store versions; keep a minimum supported client version in remote config to force upgrades safely.

## 11. Secrets handling
- Secrets arrive as environment variables from CI secret stores (or plugin `userConfig` locally). Nothing sensitive goes into `.gamestudio/`, fastlane files, logs or release reports.
- Mask secrets in logs; fastlane hides some values but custom shell steps do not.
- Principle of least privilege: the Play service account can release but not manage users; the ASC key has the lowest role that permits upload (App Manager is typical for pilot and deliver; check current role docs).
- Rotate on staff changes and after any suspected leak; document how.
- Pull request builds from forks never receive secrets.

## 12. Human-only steps
| Step | Why a human |
|---|---|
| Developer account creation, payment, identity verification | Legal identity and money |
| Creating the app record in App Store Connect | Not available via API key in fastlane |
| First Play AAB through the Console | Common prerequisite for API uploads |
| Accepting store agreements and tax/bank forms | Legal acceptance |
| Privacy, Data safety, age rating, ads and audience declarations | Legal accuracy; sign-off by the owner |
| Unity licence activation for unattended CI | Account-bound |
| Creating signing assets the first time (`match` init, upload key) | Key custody |
| Submitting for review, promoting to production, changing rollout percentage | Irreversible and public |
| Responding to rejections that involve judgement or policy appeals | Accountability |
| Responding to legal notices, takedowns, trademark disputes | Accountability |

## 13. Failure modes
| Symptom | Likely cause | Fix |
|---|---|---|
| "Package not found" from `supply` | No first manual upload, or wrong package id | Upload first AAB in Console; check `Appfile` |
| Upload rejected: version code already used | Build number not monotonic | Compute from store |
| "No signing certificate" in `gym` | `match` not run, wrong team, mixed manual/automatic signing | Run `match` readonly, align project signing |
| Upload fails with missing icon or alpha channel | iOS icon with transparency | Flatten the 1024 icon, no alpha |
| Build processes but never appears | Export compliance or privacy manifest problem emailed to the account | Read the email; fix; upload a new build number |
| Godot Android export fails at Gradle | Missing template install or SDK path | Reinstall templates; set SDK path via environment |
| Unity licence error in CI | Activation expired or machine-bound | Use serial or licence server |
| Play warns about 16 KB | Old engine or native plugin | Upgrade engine, rebuild native libraries aligned |
| Rejected upload: debuggable | Debug build type | Use release config |

## 14. Volatile facts (as of Oct 2026 - verify)
- fastlane was reported at version 2.241.1 on Oct 15, 2026, with CI against Xcode 26.5; 2.240.0 changed how API keys are read. Source: https://github.com/fastlane/fastlane/releases
- ASC API key support by fastlane actions and the limits of `produce` and `pem`: https://docs.fastlane.tools/app-store-connect-api/
- Apple Build Upload API, webhooks and Feedback API announced at WWDC25: https://developer.apple.com/videos/play/wwdc2025/324/
- Codemagic reported pricing (free tier of M2 minutes, per-minute and annual plans): https://codemagic.io/pricing/
- GitHub Actions hosted-runner price cuts effective Jan 1, 2026 and the postponed self-hosted runner fee are reported by third parties; confirm in GitHub billing docs. Sources: https://itbrief.co.uk/story/github-cuts-actions-runner-prices-adds-new-usage-fee ; https://www.warpbuild.com/blog/github-actions-price-change
- godot-ci image tags are version-specific: https://hub.docker.com/r/barichello/godot-ci
- New personal Play accounts and the closed-testing requirement (tester count and duration have changed before): https://support.google.com/googleplay/android-developer/answer/14151465
- Play App Signing: https://support.google.com/googleplay/android-developer/answer/9842756

## 15. Pipeline acceptance test and rollback drill
Run this once per new game and after any large pipeline change. It proves the pipeline works before a launch deadline depends on it.

Acceptance test:
1. Fresh clone on a clean runner, no cached state. Build succeeds from the repo and secrets alone.
2. `compliance_preflight.py --project . --platform all --json` exits 0 or lists only accepted warnings.
3. Android: internal-track upload succeeds, a tester installs from the Play link, the game reaches the main menu and completes the first level.
4. iOS: TestFlight internal build appears, installs, completes the first level.
5. Build numbers on both stores are strictly greater than the previous upload; running the lane twice produces two distinct numbers.
6. Crash symbolication works: force a test crash in an internal build and confirm the stack is readable in the crash tool.
7. Logs contain no secret values (search for key id, issuer id and the first characters of tokens).
8. A pull request from a fork cannot reach secrets.

Rollback drill:
1. Keep the previous production build identifiable (build number, git SHA, artifact location).
2. Android: practise halting a staged rollout in the Console and releasing a hotfix with a higher version code that contains the old code. Play cannot reinstall an older version code over a newer one on devices.
3. iOS: practise pausing a phased release and submitting a fixed build; you cannot downgrade installed users.
4. Remote config: verify a kill switch can disable a feature (shop offer, event, new mode) without a binary release.
5. Server compatibility: confirm old clients still work against the current backend for the supported window, and that the minimum-version prompt displays correctly.
6. Write the drill result into the release report template so future releases inherit the procedure.

Metrics worth tracking for the pipeline itself: time from merge to internal build, percentage of lane runs that fail for infrastructure reasons, and number of human interventions per release. A pipeline that needs a human fix every release is not finished.
