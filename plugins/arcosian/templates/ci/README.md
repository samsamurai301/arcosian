# CI and release templates

Copy these into a game project. Layout assumed: `.github/workflows/*.yml` from `github/`, `fastlane/` at the repo root, `codemagic.yaml` at the root if you use Codemagic. Every template follows one rule: CI uploads builds to TestFlight and Play **internal**; a human promotes to review and production.

## Files

| File | Purpose |
|---|---|
| `github/godot-ci.yml` | Headless Godot 4.7.2: `check_all`, `run_tests`, runner script mode; Windows, macOS, Linux and Web exports, each desktop build launched with `--smoke` on its own OS; signed Android AAB; macOS job exports the iOS Xcode project then `fastlane ios beta` |
| `github/unity-ci.yml` | GameCI test runner and builder; Windows, macOS, Linux and Web players; Android AAB, iOS Xcode project (built on Linux), fastlane on macOS |
| `github/plugin-quality.yml` | `gs.py validate --all` and compliance pre-flight on PRs |
| `fastlane/Fastfile` | Lanes: `ios beta`, `ios metadata`, `ios release` (guarded), `android internal`, `android metadata`, `android promote` (guarded) |
| `fastlane/Appfile`, `Matchfile`, `Gemfile` | Identity, signing storage, pinned fastlane (`~>`) |
| `codemagic/codemagic.yaml` | Godot iOS and Android workflows on Codemagic |

## Secrets and variables

Set these in repo Settings > Secrets (or Codemagic groups). Never commit values; never print them.

| Name | Used by | Notes |
|---|---|---|
| `ASC_KEY_ID`, `ASC_ISSUER_ID`, `ASC_KEY_CONTENT` | fastlane iOS | App Store Connect **Team** API key (.p8 content). Individual keys cannot reach provisioning endpoints |
| `MATCH_PASSWORD`, `MATCH_GIT_URL`, `MATCH_GIT_BASIC_AUTHORIZATION` | match | Private certs repo; basic auth is `base64(user:token)` |
| `ANDROID_KEYSTORE_BASE64`, `ANDROID_KEYSTORE_PASSWORD`, `ANDROID_KEY_ALIAS`, `ANDROID_KEY_PASSWORD` | Android build | Upload keystore, base64-encoded |
| `PLAY_JSON_KEY_DATA` | fastlane supply | Service-account JSON content; grant release permissions in Play Console |
| `UNITY_LICENSE`, `UNITY_EMAIL`, `UNITY_PASSWORD` | Unity CI | See Unity activation below. Pro: add `UNITY_SERIAL` |
| Variables `APP_IDENTIFIER`, `APPLE_TEAM_ID` | fastlane | Not secret |
| `CONFIRM_RELEASE` | `release`, `promote` lanes | Never stored in CI; a human sets it per run |

## Setup order

1. Create the app records by hand (below). Then create the ASC Team key and the Play service account.
2. Create the certs repo and run `bundle exec fastlane match appstore` once **locally** (writable) to seed it. CI runs readonly.
3. Run `bundle install` in `fastlane/` and commit `Gemfile.lock`.
4. Add secrets, copy the workflow, push a branch, confirm `validate` is green before enabling the build jobs.
5. First iOS run: confirm the Xcode scheme name (`XCODE_SCHEME`) and that the exported project signs with the match profile (export presets must set the team id and use manual signing).

## Human-only steps (do not automate)

- **Create the app record** in App Store Connect. fastlane `produce` is not supported with an API key.
- **First Play upload** through the Play Console UI. Until then, `supply` typically fails with "package not found".
- **Closed testing requirement.** New personal developer accounts have been subject to a closed-testing gate before production access; check the current Play rules before planning dates.
- **Unity licence activation.** Personal: activate in Unity Hub to produce a `.ulf`, store its content as `UNITY_LICENSE`. Manual `.alf` activation is no longer available for Personal. A Pro serial or a licence server is more robust than a machine-bound `.ulf`.
- **Review submission and production rollout.** Lanes `release` and `promote` refuse to run without `CONFIRM_RELEASE=yes-i-approve`. The `ship` skill never sets it.
- Store questionnaires, privacy labels, age rating, data safety form.

## Decision table

| Situation | Choose |
|---|---|
| Godot, want transparency and portability | GitHub Actions + fastlane |
| Small team, no Mac wrangling, accept hosted pricing | Codemagic |
| Unity unattended builds | GameCI with Pro serial or licence server; Personal `.ulf` is fragile |
| iOS build time matters | Keep engine work on Linux, macOS only for gym and pilot |

## Troubleshooting

- `match` fails readonly: profile missing for the bundle id; seed it locally with a writable run.
- `gym` cannot find scheme: list schemes with `xcodebuild -list -project <path>`.
- Godot export fails with missing templates: the template folder must be named `<version>.stable` and match the pinned engine exactly.
- AAB export error about Gradle build: the Android export preset needs "Use Gradle Build" and the SDK path; reuse the template's export presets.
- Release lane refuses: this is intended.

## Pipeline at a glance

```
PR:   validate (static gate, unit tests, scripted playthrough) + studio-quality
main: validate -> Android AAB (signed) -> Play internal
             \-> iOS Xcode project -> match(readonly) -> gym -> pilot (TestFlight, no review)
human: promote / submit with CONFIRM_RELEASE after the `ship` checklist
```

## Pre-release checklist

1. Validate job green on the exact commit being shipped; reports attached as artifacts.
2. `compliance_preflight.py` clean (privacy, age rating, ads/IAP disclosure, AI disclosure).
3. Version name bumped by hand; build numbers are automatic (TestFlight lookup + 1; Play needs a higher versionCode in the export preset).
4. Internal testers installed the build on a real low-tier device and ran the first-session flow.
5. Metadata lanes dry-run reviewed by a human; screenshots match the current build.
6. Rollback plan written: previous build number, remote-config kill switches, staged rollout percentage.

## Volatile facts (as of Oct 2026 — verify)

- Godot 4.7.2-stable is the pinned engine; godot-ci image tags track engine versions. Source: https://hub.docker.com/r/barichello/godot-ci
- fastlane was actively released in Oct 2026; a 2.240 change altered how API keys are read, so re-test auth after bumping. Source: https://github.com/fastlane/fastlane/releases
- App Store Connect API key support per fastlane action. Source: https://docs.fastlane.tools/app-store-connect-api/
- GameCI activation options (Personal `.ulf`, Pro serial, licence server). Source: https://game.ci/docs/github/activation
- Codemagic pricing and free minutes change often. Source: https://codemagic.io/pricing/
- GitHub Marketplace godot-ci. Source: https://github.com/marketplace/actions/godot-ci
