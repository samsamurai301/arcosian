# Store requirements (2026)

Summary: the App Store and Google Play impose two kinds of rules. Stable rules (what a privacy declaration is, why random-reward odds must be disclosed, why a reviewer needs a working demo path) change slowly and are written as ordinary guidance. Volatile rules (SDK floors, API levels, billing library versions, deadlines, enforcement regions) change yearly and live in a clearly labelled section with source URLs. Use the stable sections to design the game and the pipeline; recheck the volatile section on every release. Apple and Google sections are followed by a common-rejections table and a triage method.

## Contents
1. How to use this file
2. Apple: stable rules
3. Apple: privacy manifests and required-reason APIs
4. Apple: age rating, ATT, account deletion
5. Apple: key guidelines for games
6. Google Play: stable rules
7. Google Play: Data safety, families, content rating
8. Common rejections and fixes
9. Per-release requirements checklist
10. Volatile facts (as of Oct 2026 - verify)
11. Playbooks: IAP setup, SDK audit, policy change watch

## 1. How to use this file
- Before design: read sections 4, 5, 7 for constraints that shape features (account deletion, odds disclosure, children).
- Before each release: read section 10 and tick the checklist in section 9.
- After a rejection: section 8 first, then the guideline text itself.
- Never copy a deadline from memory into a plan; copy it from section 10 and re-verify the source.

## 2. Apple: stable rules
- The build SDK floor and the minimum deployment target are separate settings. A newer build SDK does not force you to drop older devices; the deployment target decides who can install.
- Every app needs: a privacy policy URL, an App Privacy ("nutrition label") declaration, an age rating, a support URL, screenshots at required device classes, and working review access (demo account if there is login).
- In-app purchases for digital goods and game currency use Apple's IAP unless a currently valid regional exception applies (see volatile facts). Misdescribing or hiding purchases is a rejection.
- Apps must be complete: placeholder content, broken links, "coming soon" features and crashes get rejected.
- Metadata must describe the actual app: screenshots from real gameplay, no competitor names in keywords, no unverifiable claims ("#1 game").
- TestFlight: internal builds skip beta review; the first external build of a version goes through beta review.
- Third-party SDK obligations flow to you: the app is rejected for an SDK's missing manifest or undeclared API use even if you never wrote that code.

## 3. Apple: privacy manifests and required-reason APIs
Concept, in plain terms:
- A **privacy manifest** (`PrivacyInfo.xcprivacy`) is a property list declaring four things: whether the app tracks, which domains it contacts for tracking, which data types it collects and why, and which "required reason" APIs it uses with an approved reason code.
- **Required-reason APIs** are system APIs that can be misused for fingerprinting; they fall into categories such as file timestamps, system boot time, disk space, active keyboards and user defaults. Using one without declaring an approved reason fails upload validation or review.
- **Third-party SDK rule**: SDKs on Apple's published list must ship their own manifest and, when distributed as binaries, be signed. This applies to new apps and to updates that add a listed SDK. Game-relevant entries reportedly include UnityFramework, Firebase components, Meta SDK kits and OneSignal; ad mediation SDKs may or may not be listed, so check the live list rather than assuming.

Procedure for engines:
1. Unity: use a recent Unity 6 version that ships its own manifest; add a project-level manifest through the Unity plugin or post-build script if packages require it.
2. Godot: the iOS export template includes a manifest in current versions; verify in the exported Xcode project that `PrivacyInfo.xcprivacy` exists and lists the APIs your plugins use.
3. After export, run an Xcode archive and use the privacy report feature (Product > Archive > Generate Privacy Report) to view the aggregate across SDKs, then compare with your App Privacy answers.
4. Re-run for every SDK addition or upgrade. `compliance_preflight.py` warns when no manifest is found in the project; it cannot prove the manifest is complete.

Do and don't:
- Do declare accurately; vague reason codes are rejected.
- Do not collect "just in case" data; each type adds declarations and legal exposure.
- Do not embed SDKs whose manifest you cannot obtain; replace or remove them.

## 4. Apple: age rating, ATT, account deletion
**Age rating.** Apple replaced its age rating system with a revised questionnaire and new tiers; developers had to answer the new questions in App Store Connect. Answer truthfully and conservatively: user-generated content, chat, unrestricted web access, simulated gambling, and paid random items all influence the rating. A wrong rating is a common reason for removal. If your game has loot-box style mechanics, state them where the questionnaire asks.

**App Tracking Transparency.**
- Required when you track users across apps and websites owned by other companies, or share identifiers (IDFA) with ad networks for that purpose.
- Need: `NSUserTrackingUsageDescription` text, a prompt shown at a sensible moment (after the player understands value, not at first frame), and graceful behaviour on denial.
- Do not gate gameplay on consent; do not pre-prompt with misleading screens.
- Reported opt-in rates conflict between sources; plan revenue for the pessimistic case.
- Without tracking, ads still run (contextual or non-personalized). Attribution relies on Apple's privacy-preserving frameworks.

**Account deletion.** If the app lets users create accounts, it must offer in-app account deletion (initiation within the app, not just email). Include game-progress data, purchases records handling statements, and a clear confirmation. Guest-only games with local saves do not need it; Game Center identity is handled by the platform. The pre-flight blocks when accounts exist but no deletion flow is declared.

**Sign in with Apple.** If you offer third-party social login for the primary account, check current rules about offering an equivalent privacy-preserving option; rules have exceptions, so verify the current guideline text.

**Kids category and children.** Strict: no third-party analytics or advertising beyond what the guidelines permit, no links out without a parental gate, no behavioural ads. Treat the Kids category as a separate product with its own SDK set. See `legal-ethics`.

## 5. Apple: key guidelines for games
| Area | What it means in practice |
|---|---|
| Payments (3.1.1) | Digital items through IAP; odds disclosed before purchase for random items |
| Loot boxes | Probability of each type must be shown before the purchase decision |
| Subscriptions | Clear price, period, renewal, free trial terms before the purchase button; easy restore |
| Reward-for-install, rewarded ads | Allowed with care; no deceptive ads, no ads covering controls |
| User-generated content | Filtering, reporting, blocking, and published contact if the game has chat or UGC |
| Performance | No crashes, no obvious placeholder content; reviewer runs on current hardware |
| Design | Not a copy of another app; minimum functionality; IAP restore button |
| Legal | Licences, trademarks, real-money gaming restrictions by region |
| Privacy | Policy URL, consent flows, data minimisation, deletion |
| Hidden features | Undisclosed features or remote content that changes the app's purpose after review are grounds for removal |

Remote config and live content: updating balance and events remotely is fine; shipping fundamentally different functionality after review is not. Keep a record of what remote content can change.

## 6. Google Play: stable rules
- New apps ship as Android App Bundles with Play App Signing.
- Target API level: Google requires recent targets for new apps and updates each year. Apps that fall behind lose visibility on newer devices and eventually cannot be updated.
- Play Billing Library: Google deprecates old library versions on a schedule; updates built with a deprecated version are blocked from publishing. Engine IAP plugins bundle a specific version, so check the plugin changelog, not just your Gradle files.
- 64-bit support is mandatory for native code; since 2025, native libraries must also work with 16 KB memory pages on 64-bit devices for apps targeting recent Android versions. Engine, NDK, AGP, and every native plugin must be built aligned.
- Large screens: newer target APIs remove opt-outs for orientation and aspect-ratio locking on big screens; games that assume portrait-only must handle resizable windows or letterbox deliberately.
- Edge-to-edge display is enforced by newer targets; check safe-area handling for notches and gesture bars.
- Permissions: request at the moment of need; sensitive permissions trigger declarations and reviews. Remove permissions pulled in by SDK manifests that you do not use (inspect the merged manifest).
- Distribution outside Play (website APK, alternative stores) has its own verification rules emerging (see volatile facts); Play distribution is the default plan.

## 7. Google Play: Data safety, families, content rating
**Data safety form.** Declares what data the app and its SDKs collect or share, why, whether it is encrypted in transit, and whether users can request deletion. Build it from the SDK manifest, not from memory: every analytics, ads, attribution, crash and auth SDK has published data-collection disclosures; merge them. Keep a spreadsheet mapping SDK -> data type -> purpose, regenerate on SDK change.

**Account deletion.** Apps with account creation need an in-app deletion path and a web URL for requesting deletion, both declared in the Console.

**Ads declaration and target audience.**
- Declare whether the app contains ads.
- If children are a target audience (even partially), the **Families policy** applies: only certified ad SDKs, no personalised ads, restricted data collection, stricter content. Choosing "children" accidentally in the target-audience form drags the app into these rules, so set the target age groups deliberately and consistently with store text and art.
- Mixed audience apps need a neutral age screen and routing.

**Content rating (IARC).** Answer the questionnaire per actual content; it generates regional ratings (ESRB, PEGI, USK, ClassInd, ACB and others). Chance-based paid items and simulated gambling affect ratings in several regions. Re-answer when content changes.

**Testing requirements.** New personal developer accounts (created after Nov 13, 2023) must complete a closed test with at least 12 testers opted in for 14 continuous days before applying for production (see volatile facts for the source and date checked). Whether organisation accounts are exempt was not stated on that page, so confirm in Play Console. Plan the calendar around it.

**Android vitals.** Play monitors crash rate and ANR rate against bad-behaviour thresholds, and high rates reduce store visibility. Set internal alerts below the published thresholds; check numbers in Play Console documentation.

**Developer verification.** Google is rolling out identity registration for developers whose apps install on certified Android devices, starting with specific countries and expanding (see volatile facts). Play-distributed apps are covered through the developer's Play account; it matters most for APK or alternative-store distribution.

## 8. Common rejections and fixes
| Store | Symptom / reason | Usual root cause | Fix |
|---|---|---|---|
| Apple | Missing purpose string | SDK touches camera, microphone, tracking, photos | Add string or remove API usage; audit SDKs |
| Apple | Invalid or missing privacy manifest | Old SDK, export template missing manifest | Update SDK, add manifest, regenerate privacy report |
| Apple | App Privacy answers do not match behaviour | Added analytics or ads SDK | Rebuild answers from SDK list, resubmit |
| Apple | Guideline 3.1.1 odds | Random rewards without disclosed probabilities | Show odds before purchase on the same screen |
| Apple | Account deletion missing | Login exists, no in-app delete | Add flow, document in review notes |
| Apple | Cannot reach gameplay | Login wall, region lock, server down | Demo credentials, review mode, check backend |
| Apple | Crash on launch on reviewer device | Untested on latest OS or missing entitlement | Test on current iOS betas and release, check profile |
| Apple | Misleading screenshots | Mockups, UI not in app | Capture from build |
| Apple | Kids category violations | Third-party analytics, ads, external links | Remove or re-scope the audience |
| Apple | Subscription terms unclear | Price/period not displayed near button | Add required disclosures and restore |
| Google | Target API too low | Engine default target | Set explicit target at current floor |
| Google | Billing library deprecated | IAP plugin bundles old library | Upgrade plugin or engine |
| Google | 16 KB incompatibility | Old engine or unaligned native lib | Upgrade engine and plugins, rebuild |
| Google | Data safety mismatch | SDK collects undeclared data | Update form from SDK disclosures |
| Google | Families policy violation | Uncertified ad SDK in child-directed app | Switch to certified networks, disable personalised ads |
| Google | Deceptive behaviour, impersonation | Name, icon or text resembling another brand | Rename, redraw, rewrite listing |
| Google | Closed test requirement unmet | New personal account, not enough testers or days | Complete the requirement before applying |
| Google | Intellectual property complaint | Unlicensed assets, trademark terms | See `legal-ethics`; remove, document licences |
| Both | Reviewer cannot test IAP | Products not approved or not attached | Attach products, test in sandbox |
| Both | Broken privacy policy link | Placeholder URL | Real, reachable, mentions the SDKs and rights |

Triage method: reproduce on a clean device from the exact uploaded build, read the full message, find the guideline, change one cause at a time, answer the reviewer with specifics and evidence.

## 9. Per-release requirements checklist
- [ ] Build SDK and deployment target meet current Apple floors (section 10).
- [ ] Target API, billing library and page-size alignment meet current Google floors.
- [ ] Privacy manifest present; privacy report reviewed against App Privacy answers.
- [ ] Data safety form matches SDK disclosures.
- [ ] Age rating and IARC answers reflect monetization and content as shipped.
- [ ] ATT string and prompt logic present if any IDFA use.
- [ ] Account deletion in-app and on web if accounts exist.
- [ ] Odds disclosure in the purchase flow for random items.
- [ ] Licences and AI-asset provenance records current (`legal-ethics`).
- [ ] Demo account and review notes ready.
- [ ] Screenshots and text from the current build.

## 10. Volatile facts (as of Oct 2026 - verify)
Apple
- Since Apr 28, 2026, apps must be built with Xcode 26 or later using the 26-series SDKs; this is the build SDK, not the minimum OS. Source: https://developer.apple.com/news/upcoming-requirements/
- Since Sep 9, 2026, iOS and iPadOS apps uploaded to App Store Connect must target iOS 13 or later (checked on the same page on 2026-10-20; the page's newest entry is dated Sep 9, 2026). Source: https://developer.apple.com/news/upcoming-requirements/
- New age-rating questionnaire: answers were due Jan 31, 2026; ratings for all apps and games were automatically updated. Source: https://developer.apple.com/news/upcoming-requirements/
- Third-party SDK privacy manifest and signature list: https://developer.apple.com/support/third-party-SDK-requirements/
- ATT opt-in rates reported at roughly 35 to 50 percent depending on source and year; treat as uncertain. Source: https://www.moburst.com/blog/idfa-att-update/
- EU child-safety rules for alternative payments and link-outs from Oct 1 (Apple's post dated Aug 18, 2026; checked 2026-10-20): no link-outs in Kids-category or under-13 apps, and a parental gate for under-18 apps using alternative payments or link-outs. Source: https://www.apple.com/newsroom/2026/08/apple-announces-changes-for-apps-in-the-european-union/
- US store-level age verification laws (Texas Jan 1, 2026; Utah May 7, 2026; Louisiana Jul 1, 2026) and Apple's age-range APIs. Source: https://9to5mac.com/2025/11/04/app-store-texas-sb2420-new-apis/
- Apple vs Epic litigation over link-outs and commissions is unresolved as reported in Sep 2026 (the Supreme Court granted review in No. 25-1311); monitor before designing external purchase flows. Sources: https://www.courthousenews.com/ninth-circuit-confirms-contempt-finding-against-apple-in-epic-games-battle/ (resolves) and the Ninth Circuit opinion at https://law.justia.com/cases/federal/appellate-courts/ca9/25-2935/25-2935-2025-12-11.html (the site blocks automated fetches, so the page was not re-read on 2026-10-20).

Google
- Target API 36 (Android 16) required for new apps and updates from Aug 31, 2026, with an extension request to Nov 1, 2026 available (Wear OS and Automotive apps need API 35; TV and XR apps need API 34); existing apps must target API 35 or higher to remain available to new users on devices running a higher Android version. Checked 2026-10-20; the page was last updated 2026-10-16. Source: https://developer.android.com/google/play/requirements/target-sdk
- Play Billing Library 8 or later required from Aug 31, 2026 (extension to Nov 1, 2026); a newer version is recommended. Source: https://www.revenuecat.com/blog/engineering/play-billing-8-migration
- 16 KB page size: apps targeting Android 15 or later must support it on 64-bit; enforcement began Nov 1, 2025, extension reported to May 31, 2026; needs NDK r28 or later and AGP 8.5.1 or later; Godot 4.5 contains the engine fix. Status of Unity 6 LTS builds not confirmed in the notes; check the Unity release notes. Source: https://www.freecodecamp.org/news/google-16-kb-page-size-requirement-what-to-do/
- Developer verification: registration enforced on certified devices in Brazil, Indonesia, Singapore and Thailand from Sep 30, 2026, global rollout reported for 2027. Source: https://www.androidauthority.com/p-3679204/ (blocks automated fetches; the claim was not re-checked on 2026-10-20, so confirm on Google's developer verification page).
- New personal accounts (created after Nov 13, 2023): a closed test with at least 12 testers opted in continuously for 14 days is required before applying for production access; testers who leave before 14 days do not count, and review usually takes seven days or less (checked 2026-10-20; the page does not say whether the number was ever different, so the earlier "reduced from" claim is unconfirmed). Source: https://support.google.com/googleplay/android-developer/answer/14151465
- One-time products API model (purchase options and offers) requires PBL 8. Source: https://android-developers.googleblog.com/2025/07/new-tools-to-help-drive-success-for-one-time-products.html
- IARC content ratings: https://support.google.com/googleplay/android-developer/answer/9898843

## 11. Playbooks: IAP setup, SDK audit, policy change watch

### IAP and subscription setup
1. Design the catalogue first (`monetization`): consumables, non-consumables, subscriptions, bundles. Product ids are permanent in practice; name them by purpose (`gems_small`, `no_ads`), not by price.
2. iOS: create products in App Store Connect, add localized names and descriptions, attach them to the app version, and submit them with the build for the first review. Missing attachment is a classic "cannot test IAP" rejection.
3. Android: create products in Play Console (new one-time products model for PBL 8), activate them, and publish the app to at least an internal track before testing real purchase flows with licence testers.
4. Restore purchases button for non-consumables and subscriptions on iOS; entitlement refresh on Android at startup.
5. Server-side receipt validation using the stores' server APIs; a client that trusts itself is both a fraud and a support problem.
6. Randomised purchases: show per-outcome probabilities on the purchase screen (or one tap away on a visible control), keep them identical to the server tables, and keep a changelog.
7. Subscriptions: display price, billing period, trial length, auto-renew statement, and terms links next to the purchase button; offer a manage-subscription link.
8. Sandbox test matrix: purchase, cancel, restore, refund, family sharing where relevant, interrupted purchase, offline, app killed mid-purchase.

### SDK audit (do this before adding any SDK, and before each release)
For each third-party SDK record: purpose, owner, version, privacy manifest present, signature present (iOS), data collected (for both store forms), permissions added (merged manifest), child-directed support flag, 16 KB alignment status, licence and attribution requirement, network domains contacted, kill switch. Put it in one table in the repo (`docs/sdk-register.md`). Reject an SDK if any column is unknown and unobtainable. Fewer SDKs means fewer forms, fewer rejections and a smaller attack surface; a typical small game needs analytics, crash reporting, IAP, and optionally ads and attribution.

### Reading the merged Android manifest
Build the AAB, then inspect the merged manifest from the Gradle output (or Android Studio's Merged Manifest view). Search for `uses-permission`, `exported="true"` components, `queryAllPackages`, advertising id permission, and any `tools:node="remove"` you need to add to strip unwanted permissions. Compare with the Data safety form line by line.

### Policy change watch
- Subscribe to Apple Developer News and the Play Console policy announcements; assign one human owner.
- Every quarter, rerun this file's volatile section against the live sources and update the date in the heading.
- Keep a "policy debt" list: items you are exempt from today because of an extension, with the date the extension ends, and the engineering task that removes the exemption.
- Treat extension deadlines as the real deadline for planning purposes; extensions are not guaranteed to be granted.

### Review notes template
```
Demo account: <email> / <password supplied in the review notes field, not in the repo>
How to reach gameplay: tap Play on the title screen; no login required.
Random rewards: odds are shown on the shop and on each pack's info button.
Account deletion: Settings > Account > Delete account.
Ads: rewarded video only, opt-in; ATT prompt appears after the tutorial.
Remote content: events and balance data are served remotely; they cannot add new app functionality.
Special hardware or regions: none.
Contact: <phone and email of a human who can answer within a day>
```
Never put credentials in the repository; paste them into the store form.

### Regional availability
Decide countries deliberately: loot-box rules, gambling-adjacent features, age-verification laws and tax setup differ by country (`legal-ethics`). A soft launch in a few countries is also a legal test; record which features are disabled where, and keep that matrix in the contract.
