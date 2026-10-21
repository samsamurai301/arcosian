# Mobile Game "Ship and Operate" Stack: Build, CI/CD, Store Deployment, Monetization, Analytics, Backend/LiveOps, Compliance (state as of Oct 18, 2026)

Notes conventions for the report writer:
- Every claim carries an inline source. Most were fetched or searched this session (Oct 18, 2026).
- Items marked **[background]** are long-standing, widely documented facts I did not re-verify this session (the web-search budget ran out before I could). The URL given is the canonical doc page, but I did not re-fetch it. Treat these as "very likely still true, verify before quoting precisely."
- **[NEW 2025–26]** marks recent policy changes. **[OLDER]** marks information that predates 2026 and may be stale.

---

## 1. Build & CI/CD: which tools, how code signing is automated, and the most reliable fully automated path to TestFlight and Google Play internal testing

### Takeaway
The most reliable fully automated, agent-drivable path in Oct 2026 is: build the engine export headlessly on Linux (GameCI for Unity, godot-ci for Godot), then finish iOS on a macOS runner with **fastlane** (match + gym + pilot) authenticated *only* via an App Store Connect **Team API key**, and push Android AABs with fastlane `supply` (or the Play Developer API) using a service-account JSON. Codemagic, GitHub Actions macOS runners, Unity Build Automation and Xcode Cloud are all viable hosts. The "last mile" gotchas are human one-time steps: creating the app record, the first Play upload, Unity license activation, and Play's closed-testing gate for new personal accounts.

### Cited Findings

**fastlane (open-source CLI, still the de facto glue)**
- fastlane is actively maintained. The latest release is 2.241.1 (Oct 15, 2026), 2.240.0 (Sep 14, 2026) changed how API keys are read, and CI now tests against Xcode 26.5 — [fastlane GitHub releases](https://github.com/fastlane/fastlane/releases)
- App Store Connect API key auth is **fully supported** by `pilot` (TestFlight), `deliver` (metadata/screenshots/submission), `sigh`, `cert`, `match`, `download_dsyms` and `app_store_build_number`. `produce` (creating the app record) is **not supported with an API key**, and `pem` (push certs) is Apple-ID-only. `precheck` excludes IAP checks — [fastlane docs: App Store Connect API](https://docs.fastlane.tools/app-store-connect-api/)
- Gotcha: "Individual keys aren't able to use Provisioning endpoints, access Sales and Finance, or notaryTool". fastlane says it is "highly recommended to create a Team Key, as it is required for any provisioning-related API access." The API also cannot tell App Store teams from Enterprise teams, so match/sigh may need the `in_house` option — [fastlane docs: App Store Connect API](https://docs.fastlane.tools/app-store-connect-api/)
- `match` stores encrypted certificates and provisioning profiles in a git repo, S3 or Google Cloud Storage and syncs them across machines and CI — **[background]** [fastlane match docs](https://docs.fastlane.tools/actions/match/)
- `supply` uploads APK/AABs, metadata and screenshots to Google Play tracks via a Google Cloud service-account JSON — **[background]** [fastlane supply docs](https://docs.fastlane.tools/actions/supply/)

**Apple's own build-upload automation [NEW 2025–26]**
- At WWDC25 Apple added a **Build Upload API** (builds uploadable directly via the App Store Connect API, with structured errors and build-number reuse after a failed delivery). It also added **Webhooks** (build upload state, build beta state, app version state, TestFlight feedback, background-asset state, HMAC-signed with a shared secret) and a **Feedback API** (TestFlight screenshots and crash feedback) — [WWDC25 session 324](https://developer.apple.com/videos/play/wwdc2025/324/); [WWDC Notes summary](https://wwdcnotes.com/documentation/wwdc25-324-automate-your-development-process-with-the-app-store-connect-api/); [DEV write-up](https://dev.to/arshtechpro/wwdc-2025-automate-dev-process-with-app-store-connect-api-22f7)
- The webhook signature header (`X-Apple-SIGNATURE`, HMAC-SHA256) is reported only by a third-party write-up and is unconfirmed against Apple docs — [DEV write-up](https://dev.to/arshtechpro/wwdc-2025-automate-dev-process-with-app-store-connect-api-22f7)

**Hosted CI options and pricing**
- **Codemagic**: free tier gives 500 macOS M2 minutes/month (1 concurrency). Pay-as-you-go rates are Mac mini M2 $0.095/min, M4 $0.114/min, Linux/Windows $0.045/min, and extra concurrency $49. Fixed team plans: M2 $3,990/yr (3 concurrent builds, unlimited minutes), M4 $5,400/yr, M4 Max $9,000/yr. Enterprise from $12,000/yr. The pricing page has no Unity-specific pricing (it links to unitycicd.com) — [Codemagic pricing](https://codemagic.io/pricing/)
- **GitHub Actions** cut hosted-runner prices by up to 39% on Jan 1, 2026 **[NEW 2025–26]**. macOS went from $0.080 to $0.062/min, Linux 2-core from $0.008 to $0.006, and Windows 2-core from $0.016 to $0.010. A planned $0.002/min fee for self-hosted runners on private repos (from March 2026) was **postponed** after backlash and had no new timeline as of mid-2026. These figures come from third-party sources; check GitHub billing docs — [IT Brief](https://itbrief.co.uk/story/github-cuts-actions-runner-prices-adds-new-usage-fee); [cicdcalculator](https://cicdcalculator.com/github-actions-pricing-changes-2026); [WarpBuild](https://www.warpbuild.com/blog/github-actions-price-change)
- **Xcode Cloud**: Apple Developer Program membership includes 25 compute hours/month. Paid add-ons are 100 h for $49.99/mo, 250 h for $99.99, 1,000 h for $399.99 and 10,000 h for $3,999.99. Third-party sites listing $14.99/$44.99 tiers are outdated — [Apple Xcode Cloud page via search](https://developer.apple.com/xcode-cloud/get-started); [ITPro (older)](https://itpro.com/development/software-development/368930/apple-expands-xcode-cloud-platform-with-launch-of-paid-subscriptions)
- **Unity Build Automation (UBA, formerly Cloud Build)** moved to pay-as-you-go **on March 1, 2026** **[NEW 2025–26]**. Free monthly minutes are 200 Windows, 100 Mac and 100 Linux. The first two concurrent machines are free, and storage overage is $0.10/GB. Sources conflict on free storage: Unity's 2026 notes say the first 100 GB is free, while an older support article says 5 GB and a forum summary says 25 GB. Per-minute overage rates were not found. Unity staff say free usage renews monthly — [Unity DevOps updates in 2026](https://discussions.unity.com/t/unity-devops-updates-in-2026/1711090); [Understanding Unity DevOps charges](https://support.unity.com/hc/en-us/articles/34748492914964-Understanding-Unity-DevOps-charges); [Unity forum on 100 free Mac minutes](https://discussions.unity.com/t/is-mac-build-100-free-minutes-for-unity-build-after-q1-of-2026-every-month-or-only-once/1696004); [older UBA pricing article [OLDER]](https://support.unity.com/hc/en-us/articles/6093104438932-How-does-the-pricing-for-Unity-Build-Automation-work)
- **Expo EAS (React Native)**: Starter plan is $19/mo with $45 of build credit, usage-based beyond that. An older pricing snapshot shows Free (30 builds/mo), Production $99/mo and Enterprise $999/mo; check current figures — [Expo billing plans](https://docs.expo.dev/billing/plans/); [Expo usage-based pricing](https://docs.expo.dev/billing/usage-based-pricing/)

**Unity: GameCI (GitHub Actions)**
- GameCI license activation works three ways. **Personal**: activate in Unity Hub to produce a `.ulf`, then store `UNITY_LICENSE`, `UNITY_EMAIL` and `UNITY_PASSWORD` secrets. **Pro/Plus**: `UNITY_SERIAL` plus email and password. **License server**: `unityLicensingServer` (floating license acquired and returned per build). The docs warn that a license showing in Hub does not guarantee a `.ulf` file was created — [GameCI activation docs](https://game.ci/docs/github/activation)
- Unity stopped supporting *manual* activation (.alf to .ulf) for Personal licenses, which broke the older GameCI flow. The Hub-generated `.ulf` route above is the workaround — [Unity forum](https://discussions.unity.com/t/unity-no-longer-supports-manual-activation-of-personal-licenses/926760)
- GameCI iOS builds produce an Xcode project on Ubuntu. Compiling and signing need a separate macOS job — [mackysoft example](https://github.com/mackysoft/unity-githubactions-build-example); [Virtual Maker iOS/visionOS guide](https://dev.to/virtualmaker/automating-unity-builds-to-ios-macos-and-visionos-14km)
- The alternative `buildalon/activate-unity-license@v2` action activates a Personal license with email and password on macOS runners (current status not verified) — [Virtual Maker guide](https://dev.to/virtualmaker/automating-unity-builds-to-ios-macos-and-visionos-14km)

**Godot**
- `barichello/godot-ci` Docker images (version-tagged; the Marketplace showed 4.7.2-stable as latest) automate headless exports with `godot --headless --export-release`. Android signing uses keystore secrets from environment variables. No iOS export path was documented, because iOS needs macOS and Xcode — [godot-ci Docker Hub](https://hub.docker.com/r/barichello/godot-ci); [godot-ci GitHub Marketplace](https://github.com/marketplace/actions/godot-ci); [Godot export skill example](https://skills.cat/skills/thedivergentai/gd-agentic-skills/godot-export-builds)
- Godot 4.5 contains the fix for Google Play's 16 KB page-size requirement. Projects on 4.4.x must upgrade and re-export — [Godot forum](https://forum.godotengine.org/t/godot-and-google-play-policy-warning-about-16-kb-memory-page-size/120934)

**Android signing and Play gates**
- New apps must use AAB + **Play App Signing** (Google holds the app-signing key; CI holds only the *upload* key, which can be reset if lost) — **[background]** [Play App Signing docs](https://support.google.com/googleplay/android-developer/answer/9842756)
- The first AAB for a brand-new app generally has to be uploaded through the Play Console UI before API or fastlane uploads work (a common `supply` "package not found" gotcha) — **[background]** [fastlane supply docs](https://docs.fastlane.tools/actions/supply/)
- New *personal* Play developer accounts (created after Nov 2023) must run a closed test (12 testers for 14 days, reduced from 20 in late 2024) before getting production access. Internal testing is not gated — **[background]** [Play Console Help: testing requirements for new personal accounts](https://support.google.com/googleplay/android-developer/answer/14151465)

### Inferences
- **Recommended reference pipeline (agent-automatable):**
  1. **Unity**: GameCI `unity-builder` on `ubuntu-latest`, `targetPlatform: Android` (AAB) and `iOS` (Xcode project). **Godot**: godot-ci image pinned to the exact engine tag. For Android, sign with the upload keystore from secrets.
  2. **iOS finish** on a macOS runner (GitHub Actions at $0.062/min, or Codemagic M2/M4): `fastlane match` (readonly, Team API key) → `gym` → `pilot upload` (internal testers get the build without Beta App Review; external testers need it **[background]**). The ASC Build Upload API plus webhooks can replace `pilot` polling for agents that prefer raw REST.
  3. **Android finish**: `fastlane supply --track internal` (or Gradle Play Publisher, or the raw Android Publisher API `edits.bundles.upload` → `edits.tracks.update` → `edits.commit`).
  4. **Agent-facing control**: subscribe to ASC webhooks (build processed, beta state) and use the Play Developer API's track status, so the agent reacts to events instead of polling.
- Use **only API keys (ASC .p8 Team key, Play service account JSON)**, never Apple-ID passwords or 2FA sessions. That makes the pipeline fully headless. The steps that still need a human Apple ID session (`produce` app-record creation, `pem` push certs) can be avoided: create the app once by hand, and use APNs auth keys (.p8) instead of certificates.
- Unity licensing is the biggest fragility for fully unattended Unity CI. A Pro serial or a license server is more robust than a Personal `.ulf` (which is machine-bound). UBA avoids licensing entirely but is weaker for custom fastlane-based signing and store pushes.
- Codemagic is the lowest-friction hosted option for a small studio (500 free M2 minutes, built-in signing UI, Unity support). GitHub Actions plus fastlane is the most transparent and portable, which suits agents best because everything is YAML and CLI.

### Gaps
- No current per-minute overage price for Unity Build Automation after the March 2026 change. Free-storage figures conflict (100 GB vs 25 GB vs 5 GB).
- Bitrise 2026 pricing and capabilities were not researched (search budget exhausted).
- Fastlane governance (e.g., Mobile Native Foundation stewardship) was not confirmed. Releases show the project is active.
- The exact App Store Connect REST paths for the Build Upload API (e.g., `buildUploads`) were not verified against Apple docs.
- Whether GameCI's docs now officially cover Unity 6 Personal activation changes was not confirmed (the docs page doesn't mention Unity 6).

---

## 2. Store deployment: App Store Connect API, Google Play Developer API, and 2025–2026 Apple/Google policy requirements, plus screenshot automation and ASO tools

### Takeaway
Both stores now expose nearly the whole release lifecycle via API (builds, metadata, screenshots, IAPs/subscriptions, review submission, Game Center on iOS, one-time products and subscriptions on Play). The Oct 2026 compliance gates to encode in any agent are:
- **iOS**: Xcode 26 / iOS 26 SDK (since Apr 28, 2026), minimum target iOS 13 (since Sep 9, 2026), the new age-rating questionnaire (Jan 31, 2026), and the privacy-manifest and required-reason APIs.
- **Android**: target API 36 by Aug 31, 2026 (extension to Nov 1, 2026), Play Billing Library 8+ by Aug 31, 2026 (extension to Nov 1), and 16 KB page-size support.
- **Age assurance**: the US state laws (Texas, Utah, Louisiana) and Apple's Declared Age Range API.

### Cited Findings

**Apple requirements (from Apple's Upcoming Requirements page)**
- **[NEW 2025–26] Since Sep 9, 2026**: "iOS and iPadOS apps uploaded to App Store Connect must target iOS 13 or later" — [Apple Upcoming Requirements](https://developer.apple.com/news/upcoming-requirements/)
- **[NEW 2025–26] Since Apr 28, 2026**: apps must be built with **Xcode 26 or later using an iOS/iPadOS/tvOS/visionOS/watchOS 26 SDK**. This changes the build SDK, not the user's minimum OS — [Apple Upcoming Requirements](https://developer.apple.com/news/upcoming-requirements/); [Prism News / 9to5Mac](https://www.prismnews.com/hobbies/mobile-gaming/apple-mandates-ios-26-sdk-and-xcode-26-for-app-store-submissions)
- **[NEW 2025–26] Age ratings**: all ratings were auto-migrated to Apple's new age rating system, which shows on OS 26 devices. Developers had to answer the updated questions in App Store Connect (App Information) by **Jan 31, 2026** "to avoid an interruption when submitting your app updates" — [Apple Upcoming Requirements](https://developer.apple.com/news/upcoming-requirements/)
- The new tiers are 4+, 9+, 13+, 16+ and 18+ (announced July 2025) — **[background]** [Apple Developer news](https://developer.apple.com/news/)
- **Required-reason APIs** (since May 1, 2024): uploads must declare approved reasons for listed APIs used by the app's code, including third-party SDKs — [Apple Upcoming Requirements](https://developer.apple.com/news/upcoming-requirements/)
- **Third-party SDK privacy manifests and signatures**: SDKs on Apple's list must include a `PrivacyInfo.xcprivacy` manifest, and must be signed when used as binary dependencies. This applies to new apps and to updates that *add* a listed SDK. Game-relevant SDKs on the list include **UnityFramework**, Firebase (Core, Crashlytics, RemoteConfig, Messaging, ABTesting, Firestore, Auth…), the Meta FBSDK kits, OneSignal, Flutter and Capacitor. AppLovin and GoogleMobileAds are **not** on the list — [Apple third-party SDK requirements](https://developer.apple.com/support/third-party-SDK-requirements/)
- Older but still relevant: DSA trader status required for EU distribution (updates since Oct 16, 2024; new apps removed from the EU App Store without it since Feb 17, 2025). Game Center can no longer be managed via the XML feed, so use the App Store Connect REST API. The XML feed also no longer supports IAPs, subscriptions, metadata or pricing, which are REST-API only — [Apple Upcoming Requirements](https://developer.apple.com/news/upcoming-requirements/)
- **[NEW 2025–26] Guideline 5.1.2(i)** (Nov 2025): apps must disclose, and get explicit user consent, before sharing personal data with third-party AI services. A June 8, 2026 guidelines update reportedly touched AI, safety, Kids Category data collection and App Privacy labels covering updates and SDK data. The June details come from secondary trackers — [Radom](https://www.radom.com/insights/apple-updates-app-review-guidelines-to-strengthen-privacy-protections-against-third-party-ai-data-sharing); [QAwerk](https://qawerk.com/blog/apple-app-store-ai-data-sharing-guidelines/); [ConductAtlas tracker](https://conductatlas.com/change/2026-06-09-apple-apple-app-store-review-guidelines-2759/); [The App Launchpad](https://theapplaunchpad.com/blog/app-store-review-guidelines)
- **[NEW 2025–26] Age assurance (US states)**:
  - **Texas SB 2420** took effect Jan 1, 2026. New Apple Accounts must confirm 18+, under-18 accounts must join Family Sharing, and parental consent is needed for downloads and IAP.
  - Apple shipped the **Declared Age Range API** (returns an age *category*), consent-revocation notifications and sandbox testing. It also plans APIs to re-request parental consent after "significant changes."
  - **Utah** (May 7, 2026) and **Louisiana** (July 1, 2026) get the same guardrails — [9to5Mac](https://9to5mac.com/2025/11/04/app-store-texas-sb2420-new-apis/); [PocketGamer.biz](https://www.pocketgamer.biz/texas-enforces-new-age-verification-law-for-app-stores-and-developers); [Apple age-assurance FAQ (LA)](https://developer.apple.com/la/support/age-assurance/)
  - A later secondary summary says a federal judge enjoined the Texas law, the Fifth Circuit stayed that injunction, and Apple began enforcing on June 4, 2026. This is **unverified** against primary sources — [ppc.land](https://ppc.land/apple-activates-texas-sb-2420-age-rules-for-app-store-after-injunction-lifted/); [CyberInsider](https://cyberinsider.com/apple-warns-of-privacy-risks-as-texas-age-verification-law-takes-effect/)
- **App Tracking Transparency**: the ATT prompt is required before accessing IDFA or tracking across apps. Reported opt-in rates conflict: about 50% global (AppsFlyer data via Moburst) vs about 35% (Adjust 2025 figure) — [Moburst IDFA in 2026](https://www.moburst.com/blog/idfa-att-update/); [Moburst attribution 2026](https://www.moburst.com/blog/mobile-attribution-in-2026-what-marketers-actually-need-to-know/)

**Google Play requirements**
- **[NEW 2025–26] Target API**: from **Aug 31, 2026**, new apps and updates must target **Android 16 (API 36)**. Extensions are available to **Nov 1, 2026**. Existing apps must target ≥API 35 to stay visible to new users on newer Android versions. Wear OS and Automotive need API 35, and TV and XR need API 34 — [Android Developers: target SDK](https://developer.android.com/google/play/requirements/target-sdk); [Play Console Help](https://support.google.com/googleplay/android-developer/answer/11926878)
- API 36 removes orientation and aspect-ratio locking on large screens (≥600dp) and the edge-to-edge opt-out — [Ecorpit](https://ecorpit.com/android-target-api-36-play-store-deadline-migration-2026/)
  - Games declaring `android:appCategory="game"` are exempt from the large-screen orientation and resizability override — **[background]** [Android 16 behavior changes](https://developer.android.com/about/versions/16/behavior-changes-16)
- **[NEW 2025–26] Play Billing Library**: new apps and updates must use **PBL 8+** from **Aug 31, 2026** (extension request to Nov 1, 2026). This is a publish gate, not a runtime shutoff. PBL 9 is recommended, and the PBL 8 deadline is Aug 31, 2027 — [RevenueCat PBL 8 migration](https://www.revenuecat.com/blog/engineering/play-billing-8-migration); [Foresight Mobile](https://foresightmobile.com/blog/google-play-billing-library-8-migration); [Android Developers](https://developer.android.com/google/play/billing/query-purchase-history)
- **16 KB page size**: apps targeting Android 15+ must support 16 KB pages on 64-bit devices. Enforcement began Nov 1, 2025, with a Play Console extension to May 31, 2026. The fix needs NDK r28+ / AGP 8.5.1+, and engine upgrades (Godot 4.5) — [Median](https://median.co/blog/how-to-prepare-android-apps-google-play-16-kb-page-size-requirement); [Adalo forum](https://forum.adalo.com/t/important-republish-your-android-apps-by-november-1-2025/59040); [freeCodeCamp](https://www.freecodecamp.org/news/google-16-kb-page-size-requirement-what-to-do/)
- **[NEW 2025–26] Android developer verification (sideloading)**: app registration is enforced on certified devices in **Brazil, Indonesia, Singapore and Thailand from Sep 30, 2026**, with global rollout in 2027. ADB and an "advanced" flow remain for unregistered apps. This matters for any off-Play (web/APK) distribution — [Android Authority](https://www.androidauthority.com/p-3679204/); [Stora blog](https://stora.sh/blog/2026-04-02-android-developer-verification-what-indie-devs-need-to-know); [BleepingComputer](https://www.bleepingcomputer.com/news/security/google-to-verify-all-android-devs-to-protect-users-from-malware/)
- **AI-generated content policy** (2023–24) **[OLDER but in force]**: generative-AI apps need in-app reporting/flagging of offensive AI output and must prevent restricted content. The developer is responsible for AI output — [9to5Google](https://9to5google.com/2023/10/25/google-play-gen-ai-policy/); [TechCrunch](https://techcrunch.com/2024/06/06/google-play-cracks-down-on-ai-apps-after-circulation-of-apps-for-making-deepfake-nudes); [Revera Legal](https://www.revera.legal/?p=3557)
  - Google reportedly added an AI data-sharing obligation for Android in July 2026, matching Apple 5.1.2(i). This comes from a single secondary source and is unverified — [Radom](https://www.radom.com/insights/apple-updates-app-review-guidelines-to-strengthen-privacy-protections-against-third-party-ai-data-sharing)
- Data safety form (mandatory), account-deletion requirement (apps with accounts must offer in-app *and* web deletion), and the IARC questionnaire for ratings — **[background]** [Play Console Help: Data safety](https://support.google.com/googleplay/android-developer/answer/10787469); [Play Console Help: account deletion](https://support.google.com/googleplay/android-developer/answer/13327111)

**Store APIs: capabilities relevant to automation**
- **App Store Connect API**: Build Upload, Webhooks and Feedback APIs (WWDC25, above). IAPs, subscriptions, metadata and pricing are REST-only (the XML feed was retired). Game Center config uses REST — [WWDC25 324](https://developer.apple.com/videos/play/wwdc2025/324/); [Apple Upcoming Requirements](https://developer.apple.com/news/upcoming-requirements/)
- Creating app records still isn't possible with API-key auth in fastlane (`produce` unsupported with API key) — [fastlane docs](https://docs.fastlane.tools/app-store-connect-api/)
- One community MCP claims all 1,216 operations in App Store Connect API v4.4, an indication of the API's breadth — [Glama listing](https://glama.ai/mcp/servers/z6z1opona3)
- **Google Play Developer API (Android Publisher v3)**: the **new one-time products model** (July 2025) works as one-time product → purchase options (buy/rent) → offers (discounts, pre-orders in EAP). It is managed via the `monetization.onetimeproducts` service and needs PBL 8. Legacy `inappproducts` items must be converted in the Console first — [Android Developers Blog, July 2025](https://android-developers.googleblog.com/2025/07/new-tools-to-help-drive-success-for-one-time-products.html); [API ref: purchaseOptions](https://developers.google.com/android-publisher/api-ref/rest/v3/monetization.onetimeproducts.purchaseOptions)
- Community MCPs wrap the Publisher API's edits, tracks, staged rollout, testers and Android Vitals (see section 6) — [Glama: GooglePlayConsoleMcp](https://glama.ai/mcp/servers/AgiMaulana/GooglePlayConsoleMcp/tools/upload_artifact)

**Screenshots / ASO**
- fastlane `snapshot` (iOS, XCUITest), `screengrab` (Android) and `frameit` automate screenshot capture and device framing for UI-test-drivable apps, and `deliver`/`supply` upload them — **[background]** [fastlane snapshot docs](https://docs.fastlane.tools/actions/snapshot/)
- Expo's MCP can fetch App Store and Google Play reviews and crash data and reply to reviews — [Expo MCP docs](https://docs.expo.dev/eas/ai/mcp/)

### Inferences
- An agent should run a **pre-flight compliance check** before every store push:
  - Xcode version ≥26 and deployment target ≥iOS 13
  - `targetSdkVersion` ≥36, PBL ≥8 (Unity IAP / RevenueCat SDK versions bundle PBL), 16 KB-aligned native libs
  - `PrivacyInfo.xcprivacy` present for UnityFramework and Firebase
  - ATT string present if any ad SDK uses IDFA
  - `android:appCategory="game"`
  - Age-rating answers and Data safety form consistent with the SDKs actually linked
- For engine games, XCUITest-based `snapshot` rarely works (it can't see Unity or Godot UI). A practical approach is to add an in-engine "screenshot mode" scene that renders marketing frames at required resolutions, then composite with `frameit` or ImageMagick and upload via `deliver`/`supply`. This is an inference; no source compares approaches.
- ASO tool APIs (AppTweak, Sensor Tower, Appfigures) are useful for keyword and competitor data but are enterprise or credit-priced. For agent automation, the stores' own APIs plus review-reply tools cover most operational needs.

### Gaps
- AppTweak, Sensor Tower and Appfigures API pricing and capabilities were not researched (search budget exhausted). Treat as unknown.
- Automated App Preview *video* generation tools were not found.
- Primary-source status of the Texas SB 2420 injunction and stay (June 2026 enforcement date) is unverified.
- Exact text of Apple's June 8, 2026 App Review Guidelines changes is unverified (secondary trackers only).
- The current state of the Google Play 16 KB extension after May 31, 2026, and whether Unity 6 LTS versions are compliant, were not confirmed.

---

## 3. Monetization: ad mediation, IAP (StoreKit 2 / Play Billing / RevenueCat / Unity IAP), web shops and alternative payments after the 2025–26 rulings, hybrid-casual benchmarks

### Takeaway
Mediation is a three-way market (AppLovin MAX, Unity LevelPlay, AdMob) with MAX dominant in games. For IAP, RevenueCat is the most agent-friendly layer (official hosted MCP that can even edit store products). The biggest 2025–26 shift is payments:
- **US**: Apple link-outs are allowed. The Ninth Circuit (Dec 2025) upheld contempt but allows only a cost-based fee on remand, and the Supreme Court took the case (No. 25-1311, briefing Sep 2026).
- **US Google Play**: alternative billing and links are allowed under the Epic injunction.
- **EU**: Apple's new single business model took effect **Oct 1, 2026**: IAP 26%/15%, alternative PSP 20%/10%, link-out 15%/10%, and a 5% Core Technology Commission for apps distributed outside the App Store.

Web shops are now standard practice for mid and large games.

### Cited Findings

**Ad mediation**
- In 2025, MAX, LevelPlay and AdMob together held >90% of mediation, with MAX >50%. In a PocketGamer.biz sample, 128/175 games (≈73%) used MAX. Among top-grossing ad-monetized games, MAX had 55%, LevelPlay 25% and AdMob 13.3%. AdMob's share in *top-downloaded* games was more than twice LevelPlay's — [PocketGamer.biz: nine facts about mediation 2025](https://www.pocketgamer.biz/nine-facts-about-the-mediation-space-in-2025); [Segwise AppLovin guide](https://segwise.ai/blog/applovin-publisher-monetization-guide)
- A broader estimate puts MAX at 60–80% of mobile-game mediation — [DeepResearchGlobal SWOT](https://www.deepresearchglobal.com/p/applovin-swot-analysis-report)
- **[NEW 2025–26]** Unity LevelPlay ended waterfall-only support for Unity Ads in January 2026, so bidding is now the standard path — [Segwise](https://segwise.ai/blog/applovin-publisher-monetization-guide)
- Sensor Tower: from Feb to Apr 2026, casual and hyper-casual each took 40% of game ad revenue, hybrid 16% and mid-core 4%. Ads were 70.3% of game revenue in India vs 22.1% in the US (Jan–May 2026). In mature markets (US, CA, KR, JP), IAP is 77–90% of revenue — [GameDev Reports summary of Sensor Tower](https://gamedevreports.substack.com/p/sensor-tower-mobile-game-ad-monetization); [Sensor Tower ad monetization deep dive](https://sensortower.com/blog/gaming-deep-dive-ad-monetization-report)
- Global mobile game IAP revenue was **$40bn in H1 2026, down 2% YoY** (Sensor Tower) — [MobileGamer.biz data digest](https://mobilegamer.biz/data-digest-sensor-towers-h1-analysis-hay-days-comeback-julys-top-games-big-krafton-numbers-and-more/)
- Hybrid-casual IAP growth of "37%" is cited, but sources conflict on whether it is a 2024 or 2026 figure — [Airflux](https://airflux.ai/blog/beyond-ads-hybrid-meta-systems-iap-growth-2026); [AppSamurai playbook](https://playbook.appsamurai.com/monetization-playbook); [Playio](https://blog.playio.co/hybrid-casual-games-monetization)

**IAP / subscriptions**
- **RevenueCat MCP** (official, hosted at `https://mcp.revenuecat.ai/mcp`, auth via API v2 bearer key or OAuth) manages projects and apps, products, entitlements, offerings and packages, and **store product state in App Store Connect and Google Play Console** (prices, availability, review metadata). It also covers analytics charts and experiment results. Paywall generation runs through "Rico". For Claude Code and Cursor, RevenueCat recommends its "AI Toolkit" (MCP plus workflow skills) — [RevenueCat MCP docs](https://www.revenuecat.com/docs/tools/mcp)
- RevenueCat has a free tier (aggregator source) — [agentdeals](https://agentdeals.dev/vendor/revenuecat)
  - Commonly cited pricing is free up to $2.5k monthly tracked revenue, then 1% of MTR — **[background]** [RevenueCat pricing](https://www.revenuecat.com/pricing)
- Google Play one-time products now support multiple purchase options (buy/rent) and offers (discounts, pre-orders) via PBL 8 and `monetization.onetimeproducts` — [Android Developers Blog](https://android-developers.googleblog.com/2025/07/new-tools-to-help-drive-success-for-one-time-products.html)
- Apple deprecated the original StoreKit IAP APIs in favor of StoreKit 2 (WWDC24). Server-side validation should use the App Store Server API and App Store Server Notifications v2. On-device receipt validation needs SHA-256 support, or AppTransaction/Transaction APIs — the receipt part is cited at [Apple Upcoming Requirements (Jan 24, 2025 SHA-1 expiry)](https://developer.apple.com/news/upcoming-requirements/); the StoreKit deprecation is **[background]** [StoreKit docs](https://developer.apple.com/documentation/storekit)

**Alternative payments and web shops**
- **US / Apple [NEW 2025–26]**:
  - The **Ninth Circuit affirmed** that Apple's 27% commission on linked-out purchases violated the 2021 injunction (contempt), but **rejected the zero-commission bar**. Apple may charge only a fee based on costs "genuinely and reasonably necessary" for coordinating external links, with the rate remanded to the district court (opinion dated Dec 11, 2025).
  - The **Supreme Court granted review** (No. 25-1311), and Apple filed its merits brief on Sep 14, 2026, arguing the injunction never covered commissions. No SCOTUS decision yet. The remand on the fee rate is reported stalled — [Justia: 9th Cir. No. 25-2935](https://law.justia.com/cases/federal/appellate-courts/ca9/25-2935/25-2935-2025-12-11.html); [Courthouse News](https://www.courthousenews.com/ninth-circuit-confirms-contempt-finding-against-apple-in-epic-games-battle/); [SCOTUS docket brief](https://www.supremecourt.gov/DocketPDF/25/25-1311/424150/20260914154510009_2026-09-14%20No.%2025-1311%20Apple-Epic%20Merits%20Opening%20Brief.pdf); [Sigma Law Group](https://sigmalawgroup.com/blog/2026-07-02-apple-epic-scotus-contempt/); [TechTimes](https://www.techtimes.com/articles/327527/20260915/app-store-commission-limbo-enters-new-phase-apples-epic-merits-brief-opens-scotus-fight.htm)
- **EU / Apple [NEW 2025–26]**: effective **Oct 1, 2026**, all EU developers move to one business model:
  - App Store + Apple IAP: 26% (15% for Small Business Program and other programs, and for subscriptions after year one)
  - App Store + alternative payment processing: 20% (10%)
  - App Store + link-out: 15% (10%)
  - Apps distributed via alternative marketplaces or the web: **5% Core Technology Commission** (replaces the per-install Core Technology Fee; the initial acquisition and store services fees are removed)
  - Developers must keep their payment-option choice for 12 months, and IAP can sit alongside alternative payments.
  - Kids-category apps can't link out, under-13 apps can't link out, and under-18 apps using alternative payments or link-outs need a **parental gate** — [Apple Newsroom, Aug 2026](https://www.apple.com/newsroom/2026/08/apple-announces-changes-for-apps-in-the-european-union/); [Apple: Changes for apps in the EU](https://developer.apple.com/support/apps-in-the-eu/)
  - The European Commission welcomed the terms, and Epic called them "junk fees" — [iGeeksBlog](https://www.igeeksblog.com/eu-welcomes-apple-new-app-store-terms/)
- **US / Google Play [NEW 2025–26, status partly unclear]**:
  - Under the Oct 2024 Epic permanent injunction, Google no longer requires Play Billing and permits alternative payments and external links in the US. Third-party stores get access to the Play catalog from July 22, 2026.
  - Proposed US fees (Dec 2025) were 10% on auto-renewing subs and 25% on other IAP for alternative billing, and 10%/20% for external links. A March 2026 analysis says the signed Epic–Google settlement doesn't fix these rates.
  - Reports describe a redesigned fee structure effective June 30, 2026 in the US, UK and EEA (standard ≤20%, subs 10%).
  - As of June 2026 the Epic–Google settlement was **not yet approved**, with Judge Donato holding a summer 2026 hearing. Separately, a ~$700M states/consumer settlement got final approval in Aug 2026.
  - Sources: [Neonpay (Dec 2025)](https://www.neonpay.com/blog/google-plays-new-u.s.-billing-linking-policies-what-game-developers-need-to-know); [Stash (Apr 2026)](https://www.stash.gg/blog/blog-epic-v-google-settlement-update-april-2026); [Tech-Insider](https://tech-insider.org/epic-google-play-store-changes-2026/); [Thurrott](https://www.thurrott.com/?p=337913); [PYMNTS](https://www.pymnts.com/cpi-posts/judge-approves-googles-700-million-play-store-settlement/); [VGC](https://www.videogameschronicle.com/news/judge-postpones-approval-of-epic-vs-google-settlement-wonders-why-theyre-suddenly-bffs)
- Web-shop / direct-to-consumer vendors that serve games include Neonpay and Stash. Their blogs are the main trackers of these rules — [Neonpay](https://www.neonpay.com/blog/the-latest-on-alternative-payments-for-android-in-the-u-s); [Stash](https://www.stash.gg/blog/epic-v-google-january-hearing-injunction-android-developers)
  - Xsolla, Appcharge and Aghanim are other common game web-shop vendors — **[background]**, not researched this session

### Inferences
- **Default stack for an agent-built hybrid-casual game:**
  - AppLovin MAX (or LevelPlay) mediation with bidding: AdMob, Unity Ads, Liftoff/Vungle, Mintegral, Moloco, Pangle, Meta
  - RevenueCat over StoreKit 2 / PBL 8+ for IAP, subscriptions and battle-pass entitlements
  - Remote Config / A/B testing to tune ad frequency and IAP offers
  - A web shop (US link-out) once DAU justifies it
- Battle passes are best modeled as non-consumable or auto-renewing products plus server-side entitlement, using RevenueCat entitlements or the store server notifications. This is an inference; no 2026 source was specifically researched.
- Payment rules now differ by jurisdiction (US, EU, rest of world). An agent should treat "storefront country" as a config dimension. That covers which payment buttons and links are shown, the parental-gate logic for under-18s, and the 12-month lock on EU payment-option choice.
- The US Apple link-out fee is legally unsettled until SCOTUS rules (expected in the 2026–27 term). Plans should not assume zero commission is permanent.

### Gaps
- Whether Apple is currently charging *any* US link-out fee (Oct 2026) after the Ninth Circuit remand was not confirmed.
- Final outcome of the Epic–Google settlement hearing (summer 2026) and the current authoritative Google US fee schedule are unconfirmed.
- No primary 2026 benchmark report on hybrid-casual ARPDAU, IAP/ad split, or retention was found. Only secondary summaries of Sensor Tower data.
- 2026 changes to Unity IAP, Liftoff/Vungle, Mintegral and Moloco as mediation networks were not researched.

---

## 4. Analytics & attribution: Firebase/GA4, GameAnalytics, Unity Analytics, Amplitude, Mixpanel, AppsFlyer/Adjust/Singular, SKAN/AdAttributionKit, Privacy Sandbox on Android

### Takeaway
iOS attribution has moved from SKAdNetwork to **AdAttributionKit (AAK)**, which every major MMP supports. On Android, **Google retired Privacy Sandbox in Oct 2025** (Attribution Reporting, Protected Audience, Topics and SDK Runtime on Android included), so GAID-based measurement continues for now. For agent-drivable analytics, Firebase (official MCP via firebase-tools) is the strongest low-cost default. Adjust has an official MCP, and AppsFlyer has community MCPs over its Pull API.

### Cited Findings
- **[NEW 2025–26] Privacy Sandbox retired**: in Oct 2025 Google (VP Anthony Chavez, "Update on Plans for Privacy Sandbox Technologies") announced retirement of the Attribution Reporting API (Chrome and **Android**), Protected Audience (Chrome and **Android**), Protected App Signals, On-Device Personalization, **SDK Runtime**, Topics (Chrome and **Android**) and others, citing low adoption. This followed the UK CMA releasing Google from its commitments on Oct 17, 2025. Learnings will feed an interoperable attribution standard at the W3C Private Advertising Technology WG — [BetaNews](https://betanews.com/2025/10/20/google-is-retiring-privacy-sandbox/); [Freevacy/Engadget](https://www.freevacy.com/news/engadget/google-officially-retires-its-privacy-sandbox-initiative/6843)
- **AdAttributionKit** is Apple's successor to SKAN. There was no SKAN 5. AAK keeps SKAN 4's three postback windows and crowd-anonymity tiers, and adds configurable attribution windows and re-engagement — [Moburst](https://www.moburst.com/mobile-attribution-in-2026-what-marketers-actually-need-to-know/); [MWM glossary](https://mwm.ai/glossary/skadnetwork)
  - Sources disagree on the launch: "introduced at WWDC 2024" vs "replaces SKAN starting iOS 17.4". (Background: AAK first shipped in iOS 17.4 for alternative marketplaces and was expanded at WWDC24.) A vendor claim that SKAN endpoints are deprecated by late 2026 is **unverified**.
- The MMP market (AppsFlyer, Adjust, Singular, Branch, Tenjin, Airbridge) is concentrated, and all major players support AAK. AppsFlyer is the largest by share — [Adapty 2026 services guide](https://adapty.io/blog/which-services-your-app-needs)
- **Firebase MCP server** (official, local, `npx -y firebase-tools@latest mcp`, stdio, uses Firebase CLI credentials or ADC). Feature groups:
  - **Remote Config**: get, publish, roll back templates
  - **Crashlytics**: issues, events, notes, reports, issue state
  - **Auth**, **Firestore**, **Cloud Messaging** (send to token or topic)
  - Realtime Database, Storage, Functions, App Hosting, Data Connect
  - **App Distribution is not listed.** `--only` limits tool groups. Supported clients include Claude Code and Claude Desktop — [Firebase MCP docs](https://firebase.google.com/docs/ai-assistance/mcp-server)
- **Adjust** publishes an official MCP that connects Adjust data to AI assistants. A community `mcp-adjust` (bitscorp) also exists — [Adjust blog](https://www.adjust.com/blog/adjust-mcp/); [Glama: mcp-adjust](https://glama.ai/mcp/servers/bitscorp-mcp/mcp-adjust)
- **AppsFlyer**: no official MCP found. The community `ysntony/appsflyer-mcp` (MIT) wraps the Pull API aggregate reports, and MCPBundles offers a hosted bundle — [Glama: appsflyer-mcp](https://glama.ai/mcp/servers/@ysntony/appsflyer-mcp); [MCPBundles](https://www.mcpbundles.com/providers/appsflyer-mcp)
- Tenjin published a 2026 comparison of MMP MCP servers (Tenjin, AppsFlyer, Singular, Adjust, Airbridge). Its content was not retrieved — [Tenjin](https://tenjin.com/tr/?p=14)
- Firebase Analytics (GA4 for apps), Remote Config, A/B Testing, Crashlytics and FCM are no-cost products — **[background]** [Firebase pricing](https://firebase.google.com/pricing)

### Inferences
- **Recommended default**:
  - Firebase (Analytics + Crashlytics + Remote Config + A/B Testing + FCM) as the free core, driven via the Firebase MCP and CLI
  - Either GameAnalytics (game-specific dashboards) or Amplitude/Mixpanel for product analytics
  - One MMP (AppsFlyer, Adjust or Singular) once paid UA starts; Adjust's official MCP gives the most agent-native access
- On Android, plan for **GAID plus consent** (no Sandbox migration needed). On iOS, plan for **ATT prompt → IDFA where granted, plus AAK/SKAN postbacks**, with conversion-value schemas managed in the MMP.
- An Amplitude MCP connector appears in this Claude environment's plugin catalog (observed in session tooling, not web-verified). Treat this as a signal that Amplitude offers an official remote MCP.

### Gaps
- GameAnalytics, Unity Analytics, Mixpanel and Amplitude 2026 pricing and MCP status were not researched (search budget exhausted).
- Singular MCP status and AppsFlyer official MCP plans are unknown.
- Apple primary-source confirmation of any SKAN deprecation date was not found.
- Android GAID deprecation plans post-Sandbox are unknown (no primary source found).

---

## 5. Backend & LiveOps: Firebase, Nakama, PlayFab, Unity Gaming Services, AccelByte, Supabase, Photon/Normcore/Colyseus, remote config/A-B, push, live events, leaderboards, cloud saves, anti-cheat

### Takeaway
2026 has been turbulent for managed game backends:
- **Unity deprecated Multiplay Game Server Hosting (Apr 1, 2026)**, licensing it to Rocket Science Group.
- **PlayFab replaced its generous free "Development Mode" with "Foundation Mode" (Mar 11, 2026)**, with only 1,000 free unique users per the docs.

For agent-driven indie and mid-size mobile games, Firebase (official MCP), Nakama (open source, self-hostable, Heroic Cloud managed) and Supabase are the most controllable. Photon remains the default for real-time multiplayer, with Colyseus as the open-source option.

### Cited Findings
- **[NEW 2025–26] Unity Multiplay**: deprecated as of **Apr 1, 2026**, except for customers who committed to migrate to "Multiplay by Rocket Science" before Mar 31. Unity's direct support ended Mar 31, 2026, and the software is licensed to Rocket Science Group — [Unity status notice](https://status.unity.com/info_notices/362941); [Unity docs](https://docs.unity.com/en-us/multiplay-hosting/reference-landing)
  - Matchmaker, Relay, Lobby, Distributed Authority and Netcode for GameObjects continue and work with third-party hosts (Edgegap, Gameye, Crux). These alternatives are vendor sources with a bias — [Gameye](https://gameye.com/blog/unity-multiplay-shutdown-migration-options/); [Crux](https://crux.supercraft.host/blog/unity-multiplay-shutdown-where-studios-actually-went-2026/)
- **[NEW 2025–26] PlayFab**: Development Mode is being replaced by **Foundation Mode as of Mar 11, 2026**, with no monthly bill up to **1,000 unique users**. A third-party blog says Foundation Mode eligibility is tied to Xbox shipping plans; unverified. PlayFab's marketing page still shows the older "100k players per title" free tier, which conflicts with the docs. Paid tiers: **Standard** includes $400/mo of meters then pay-as-you-go, and **Premium** includes $8,000/mo of meters — [Microsoft Learn: Development mode](https://learn.microsoft.com/en-za/xbox/playfab/pricing/development-mode); [Xbox devdocs pricing overview](https://devdocs.xbox.com/services/playfab/pricing/pricing-overview); [playfab.com pricing (possibly stale)](https://playfab.com/pricing/); [Crux blog](https://crux.supercraft.host/blog/playfab-cut-free-tier-99-percent-foundation-mode-fix-2026/)
- **Heroic Labs**:
  - **Nakama** on Heroic Cloud has no DAU/MAU/CCU limits, dedicated managed DBs and backups. Pricing is quote-based (Development, Production 1–2 cores, Enterprise 4–64+ cores).
  - **Satori** (LiveOps: events, audiences, experiments, feature flags, live events) starts **from $1,800/month with 25M events, plus $0.018 per 1,000 events** (official page; Toolradar's $600 figure conflicts).
  - Support packages are separate (≈$2k–$6k/mo per Toolradar) — [Heroic Labs pricing](https://heroiclabs.com/pricing); [Toolradar](https://toolradar.com/tools/nakama/pricing); [apis.io](https://apis.io/plans/heroiclabs/heroiclabs-plans-pricing/)
- **Photon Fusion** (third-party figures): free for 1 app up to 100 CCU, about $125/mo at 500 CCU, $250 at 1,000 CCU and $500 at 2,000 CCU. Server compute for Server Mode is extra — [Crux: Photon Fusion pricing 2026](https://crux.supercraft.host/blog/photon-fusion-pricing-2026/)
- UGS overview and alternatives (2026) — [Crux UGS guide](https://crux.supercraft.host/blog/unity-gaming-services-alternatives/)
- **Firebase** covers remote config and A/B testing, push (FCM), Firestore cloud saves, Auth and Functions, all controllable via the official MCP (section 4) — [Firebase MCP docs](https://firebase.google.com/docs/ai-assistance/mcp-server)
- Anti-cheat basics: Play Integrity API (Android) and App Attest/DeviceCheck (iOS) for device and app attestation, plus server-authoritative economy and receipt validation via App Store Server API and Play Developer API purchase verification with Real-Time Developer Notifications — **[background]** [Play Integrity docs](https://developer.android.com/google/play/integrity); [App Attest docs](https://developer.apple.com/documentation/devicecheck)
- Supabase (Postgres BaaS with auth, realtime and edge functions; free tier and Pro plan) and Colyseus (MIT open-source authoritative multiplayer framework with optional Colyseus Cloud) — **[background]** [Supabase pricing](https://supabase.com/pricing); [Colyseus](https://colyseus.io/)

### Inferences
- **Recommended tiers:**
  - **Solo/indie hybrid-casual**: Firebase (Remote Config + A/B + FCM + Firestore saves + Auth), with Google Play Games Services / Game Center for leaderboards and achievements. No dedicated game server.
  - **Live-ops-heavy or social**: Nakama (self-host on a VM or Kubernetes for cost control, or Heroic Cloud), with Satori if budget allows ($1.8k/mo+).
  - **Real-time multiplayer**: Photon Fusion/Quantum (managed CCU pricing), or Colyseus (open source) on a cheap VM or Edgegap.
- PlayFab's free-tier change and Unity's Multiplay exit are cautionary signals. Agents should favor backends that are open source or self-hostable (Nakama, Colyseus, Supabase) or whose pricing is stable and documented (Firebase), and avoid deep lock-in to vendors still restructuring.

### Gaps
- AccelByte (AGS) pricing and 2026 status; Normcore pricing; Vivox status; UGS Cloud Save/Leaderboards/Remote Config pricing changes in 2026; Supabase 2026 pricing (not re-verified).
- Primary Photon pricing (only a third-party source found).
- Whether PlayFab Foundation Mode is truly gated on Xbox shipping is unverified.

---

## 6. Which of these have MCP servers or strong CLIs/APIs an agent can drive?

### Takeaway
As of Oct 2026, **official** MCP servers exist for:
- **Firebase** (local, via firebase-tools)
- **RevenueCat** (hosted; can also edit App Store Connect and Play products)
- **Expo/EAS** (hosted; builds, store submission, TestFlight crashes and feedback, store reviews)
- **Unity** (beta, May 2026; Editor control, Unity 6+, requires a Unity AI subscription or trial)
- **Adjust**

**App Store Connect and Google Play have no first-party MCPs**, but there are many community MCPs (some with 100–1,200 tools) and very complete REST APIs. fastlane remains the most battle-tested CLI layer.

### Cited Findings

**App Store Connect (community MCPs only; no Apple-official server found)**
- `forgeopslabs/appstore-mcp` (Rust, 101 tools plus generic JSON:API passthrough; in the MCP Registry as `io.github.forgeopslabs/appstore-mcp`) — [mcpservers.org](https://mcpservers.org/servers/forgeopslabs/appstore-mcp)
- `zelentsov-dev/asc-mcp` (208 tools: apps, builds, TestFlight, subscriptions; MIT; updated 2026-05-30; ~38 stars) — [EnterpriseDNA directory](https://enterprisedna.co/directories/mcp/zelentsov-dev-asc-mcp)
- `TrialAndErrorAI/appstore-connect-mcp` (analytics, finance, beta data) — [Glama PRFAQ](https://glama.ai/mcp/servers/@TrialAndErrorAI/appstore-connect-mcp/blob/bfdc3544ea1a7521d43586754dbe48fc4d94a6e3/docs/PRFAQ.md)
- A server claiming all 1,216 operations of App Store Connect API v4.4 (stdio + HTTP) — [Glama](https://glama.ai/mcp/servers/z6z1opona3)
- `yuraist/appstoreconnect-mcp` — [Glama](https://glama.ai/mcp/servers/yuraist/appstoreconnect-mcp)
- `@ryaker/appstore-connect-mcp` (OAuth) — [getdrio](https://www.getdrio.com/mcp/io-github-ryaker-appstore-connect-mcp/md)
- All use an ASC API key (issuer ID, key ID, .p8)

**Google Play (community MCPs only)**
- `appeeky/google-play-store-cli` (CLI + MCP, MIT; AAB deploys, tracks) — [Glama](https://glama.ai/mcp/servers/appeeky/google-play-store-cli)
- A Python Play Developer API MCP (`deploy_internal`, promote track) — [Glama](https://glama.ai/mcp/servers/adyqmsu5ms)
- `petropentsak/play-store-mcp` (23 tools, staged rollout) — [Glama](https://glama.ai/mcp/servers/qog3eflcmn)
- `AgiMaulana/GooglePlayConsoleMcp` (tracks, testers, rollout, Android Vitals; uploads default to draft on internal) — [Glama](https://glama.ai/mcp/servers/AgiMaulana/GooglePlayConsoleMcp/tools/upload_artifact)
- `mikusnuz/app-publish-mcp` (unified ASC + Play; `google_upload_bundle`) — [Glama](https://glama.ai/mcp/servers/mikusnuz/app-publish-mcp/tools/google_upload_bundle); [Socket](https://socket.dev/npm/package/app-publish-mcp)

**Official MCPs**
- **Firebase MCP** (official): Remote Config, Crashlytics, Auth, Firestore, FCM, Functions, Storage, Hosting. No App Distribution tools listed — [Firebase docs](https://firebase.google.com/docs/ai-assistance/mcp-server)
- **RevenueCat MCP** (official, hosted): products, entitlements, offerings, store-product state in ASC and Play, charts and experiments — [RevenueCat docs](https://www.revenuecat.com/docs/tools/mcp)
- **Expo MCP** (official, hosted at `https://mcp.expo.dev/mcp`, OAuth; available as a Claude connector):
  - EAS build list/trigger/logs, **submit to stores**, workflows
  - TestFlight crashes and feedback, App Store and Play reviews (with replies)
  - Local simulator automation (SDK 54+, macOS for iOS)
  - Some tools need a paid EAS plan or a connected GitHub repo — [Expo MCP docs](https://docs.expo.dev/eas/ai/mcp/)
- **[NEW 2025–26] Unity official MCP Server** (open beta, announced May 11, 2026): bundled with the AI Assistant package. Requires Unity 6 (6000.0)+, a Unity Cloud-connected project and a Unity AI trial or subscription. It reads scene, component, console and build settings, edits scripts, triggers Editor actions, and supports custom C# tools. Clients include Claude Code, Cursor, Windsurf, Claude Desktop and VS Code Copilot. Unity says the feature set is still in flux — [Unity blog](https://unity.com/en/blog/unity-ai-mcp-how-to-get-started); [GameDev.net](https://gamedev.net/news/4376-unity-ai-open-beta-how-to-get-started-with-mcp/)
- **Adjust MCP** (official) — [Adjust blog](https://www.adjust.com/blog/adjust-mcp/)

**Strong CLIs**
- fastlane (iOS and Android release; API-key auth table in section 1), firebase-tools, `eas-cli`, Unity batchmode/GameCI, `godot --headless` — [fastlane docs](https://docs.fastlane.tools/app-store-connect-api/); [Firebase docs](https://firebase.google.com/docs/ai-assistance/mcp-server); [godot-ci](https://hub.docker.com/r/barichello/godot-ci)

### Inferences
- **Synthesized "ship and operate" stack for an AI agent (Oct 2026):**

| Layer | Primary pick | Agent interface | Notes / gotchas |
|---|---|---|---|
| Engine build | Unity 6 via GameCI (or Godot 4.5+ via godot-ci) | CLI/YAML; Unity MCP (beta) for Editor work | Unity Personal license `.ulf` fragility; pin engine image tags |
| CI host | GitHub Actions (Linux for export, macOS $0.062/min for iOS) or Codemagic | YAML + `gh` CLI | Self-hosted fee postponed, not cancelled |
| iOS signing/release | fastlane match + gym + pilot/deliver with ASC **Team** API key; or the ASC Build Upload API + webhooks | CLI; community ASC MCP for metadata, TestFlight, IAP | App record creation and first submission setup remain manual; Xcode 26 SDK; iOS 13+ target |
| Android release | fastlane supply / Android Publisher API to internal track | CLI; community Play MCP | First AAB manual; Play App Signing; API 36; PBL 8; 16 KB; closed-test gate for new personal accounts |
| IAP/subs | StoreKit 2 + PBL 8 via RevenueCat | RevenueCat official MCP (also edits store products) | Unity IAP is an alternative if staying all-Unity |
| Ads | AppLovin MAX (bidding) or LevelPlay | Dashboard and reporting APIs (no MCP found) | ATT prompt; SDK privacy manifests |
| Analytics/crash/RC/AB/push | Firebase | Official Firebase MCP + CLI | App Distribution not in the MCP |
| Attribution | Adjust (official MCP) or AppsFlyer (community MCP) | MCP / Pull API | AAK + SKAN on iOS; GAID on Android (Sandbox retired) |
| Backend/LiveOps | Firebase → Nakama/Satori when live-ops grows; Photon/Colyseus for real-time | Nakama REST/gRPC + console; Firebase MCP | Avoid UGS Multiplay; PlayFab free tier now 1k users |
| Store feedback | Expo MCP (if RN) or ASC Feedback API + Play reviews API | MCP/REST | — |

- Community store MCPs vary widely in quality and security. An agent plugin should either vendor a vetted one (e.g., forgeopslabs, published in the MCP Registry) or wrap fastlane plus direct REST calls itself. Scope API keys narrowly (ASC "App Manager" or "Developer" role; Play service account limited to specific apps and release permissions).

### Gaps
- No official Apple or Google MCP servers for App Store Connect or Play Console were found (as of the searches run).
- Codemagic, Bitrise, AppLovin, Unity LevelPlay, GameAnalytics, Mixpanel, Singular, PlayFab and Nakama MCP availability was not checked (search budget exhausted).

---

## 7. Compliance: COPPA/GDPR-K, loot-box regulations, age ratings (IARC)

### Takeaway
Three 2025–26 compliance shifts matter most for mobile games:
1. The **amended COPPA Rule** (compliance deadline **Apr 22, 2026**; biometrics now count as personal information; tighter third-party and mixed-audience rules).
2. **US state app-store age-verification laws** (Texas Jan 1, 2026, Utah May 7, 2026, Louisiana Jul 1, 2026), which in practice route through Apple's Declared Age Range API and parental-consent flows.
3. **Brazil's ECA Digital** banning loot-box sales to under-18s (in force March 2026, already enforced against Riot).

Belgium's 2018 ban stands, the Netherlands' enforcement was reversed by courts, and Australia rates paid loot boxes M and simulated gambling R18+ (since Sep 22, 2024).

### Cited Findings
- **[NEW 2025–26] COPPA amendments**: the FTC final rule was published Apr 22, 2025 and became effective about June 21–23, 2025, with a **compliance deadline of Apr 22, 2026**. Key changes:
  - Expanded definition of personal information, including **biometric identifiers** (relevant to voice chat)
  - Mixed-audience standards
  - Tightened notice, consent, retention and security duties
  - Operators responsible for third-party integrations touching children's data
  - Sources: [Toy Association](https://toyassociation.org/PressRoom2/News/2026-News/updated-coppa-rule-requirements-take-effect-april-22.aspx); [GGWP](https://www.ggwp.com/blog/coppa-compliance-for-game-companies/); [Loeb & Loeb](https://www.loeb.com/fr/insights/publications/2025/05/childrens-online-privacy-in-2025-the-amended-coppa-rule); [Hunton](https://www.hunton.com/privacy-and-cybersecurity-law-blog/tag/coppa)
  - The amended rule requires separate verifiable parental consent before disclosing children's data to third parties (e.g., for targeted advertising) — **[background]**
- **[NEW 2025–26] Apple EU child-safety rules for payments** (Oct 1, 2026): no link-outs in Kids-category or under-13 apps, and a parental gate for under-18 apps that use alternative payments or link-outs — [Apple Newsroom](https://www.apple.com/newsroom/2026/08/apple-announces-changes-for-apps-in-the-european-union/)
- **[NEW 2025–26] US age assurance**: Texas SB 2420 (Jan 1, 2026), Utah (May 7, 2026) and Louisiana (Jul 1, 2026). Apple provides the Declared Age Range API and consent-revocation and re-consent APIs (see section 2) — [9to5Mac](https://9to5mac.com/2025/11/04/app-store-texas-sb2420-new-apis/); [PocketGamer.biz](https://www.pocketgamer.biz/texas-enforces-new-age-verification-law-for-app-stores-and-developers)
- **Apple age ratings** moved to a new system (questionnaire answers were due Jan 31, 2026) — [Apple Upcoming Requirements](https://developer.apple.com/news/upcoming-requirements/)
  - Google Play uses the IARC questionnaire, which also yields regional ratings (ESRB, PEGI, USK, ClassInd, ACB) — **[background]** [Play Console Help: content ratings](https://support.google.com/googleplay/android-developer/answer/9898843)
- **Loot boxes**:
  - **Brazil [NEW 2025–26]**: the ECA Digital law (signed Sep 2025) bans selling loot boxes to under-18s, effective March 2026. On June 9, 2026 a Brazilian court ordered Riot Games to pay damages (reported as €2.5M or $3M; figures conflict) and to add age verification and probability disclosure — [Sheep Esports](https://www.sheepesports.com/articles/brazil-court-orders-riot-games-to-pay-eur2-5m-over-league-of-legends-loot-boxes/en); [KuCoin news](https://www.kucoin.com/news/flash/brazilian-court-orders-riot-games-to-pay-3m-for-loot-box-damages); [Programming Insider](https://programminginsider.com/loot-boxes-regulation-and-where-the-line-sits-in-2026/)
  - **Belgium**: banned paid loot boxes under gambling law in 2018. Fines run up to €800k and 5 years' prison, doubled if minors are involved — [Programming Insider](https://programminginsider.com/loot-boxes-regulation-and-where-the-line-sits-in-2026/)
  - **Netherlands**: sources conflict. One says courts reversed the regulator's approach — [Programming Insider](https://programminginsider.com/loot-boxes-regulation-and-where-the-line-sits-in-2026/). (Background: in March 2022 the Dutch Council of State overturned the EA FIFA fine, finding packs were not a separate game of chance, so there is no effective Dutch ban today.)
  - **Australia**: games classified after **Sep 22, 2024** with paid chance-based items are rated at least **M** (advisory). Games with simulated gambling are rated **R18+** (legally restricted) — [PCWorld](https://www.pcworld.com/article/2464538/all-games-with-loot-boxes-will-be-rated-m-or-higher-in-australia.html); [TechRadar](https://www.techradar.com/gaming/new-australian-video-game-classifications-aim-to-restrict-kids-exposure-to-loot-boxes); [PocketGamer.biz](https://www.pocketgamer.biz/australia-sets-new-rules-for-video-games-with-gambling-like-content)
  - **EU**: the Digital Fairness Act could bring an EU-wide approach, reportedly not before 2028 — [Programming Insider](https://programminginsider.com/loot-boxes-regulation-and-where-the-line-sits-in-2026/)
  - **Platform rules**: Apple (guideline 3.1.1) and Google Play both require disclosure of the odds for randomized paid items before purchase — **[background]** [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
- **GDPR-K**: GDPR Article 8 sets the digital-consent age at 16 by default, and member states can lower it to 13. Parental consent is needed below it, and the UK Age-Appropriate Design Code also applies — **[background]** [GDPR Art. 8](https://gdpr-info.eu/art-8-gdpr/)

### Inferences
- An agent-run compliance layer should generate and maintain these from one config:
  - Age-gate / neutral age screen → Declared Age Range on iOS → feature flags that disable personalized ads (AdMob/MAX child-directed and under-age flags), chat, link-outs and loot-box purchases for minors
  - Per-country loot-box behavior: disable paid random items in Belgium and for under-18s in Brazil; always show odds
  - Store questionnaires (Apple age rating, IARC, Data safety, App Privacy labels) generated from the actual SDK manifest. App Privacy labels now reportedly cover SDK collection on updates.
- Designing monetization around **direct-purchase or "transparent" mechanics** (battle passes, fixed-content bundles) instead of paid random loot avoids most loot-box exposure across the Belgium, Brazil and Australia regimes. This is an inference.

### Gaps
- **China** probability-disclosure rules and the status of the Dec 2023 NPPA draft online-game measures could not be researched (search budget exhausted). Background: China has required public disclosure of random-item odds since a 2017 Ministry of Culture notice. Verify before reporting.
- Primary text of Brazil's ECA Digital (Law 15.211/2025) loot-box article was not retrieved.
- Post-deadline COPPA enforcement actions involving games (2026) were not found.
- UK, Spain and Japan (kompu gacha) loot-box positions were not researched.
