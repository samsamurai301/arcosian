# Privacy, children and gambling-adjacent rules

Summary: three regulatory areas shape mobile game design more than any others. Privacy law governs what data you collect and how (GDPR, CCPA/CPRA, platform tracking rules). Children's rules (GDPR Article 8 and the UK children's code, the amended COPPA Rule in the US, store family policies, and new age-assurance laws) change which features and SDKs you may use. Gambling-adjacent rules govern paid random rewards (loot boxes, gacha), simulated gambling and social casino. This is a triage guide, not legal advice. It explains the stable principles, gives implementation checklists, then a region matrix. Dated and enforcement-sensitive facts are in the last section with sources.

## Contents
1. Principles
2. GDPR essentials for games
3. GDPR-K and children in Europe and the UK
4. Amended COPPA (US)
5. CCPA/CPRA and US state privacy laws
6. Age assurance laws and platform signals
7. ATT and platform tracking rules
8. Implementation checklist: data, consent, SDKs
9. Loot boxes: concepts and design options
10. Loot boxes by jurisdiction
11. Odds disclosure and pity systems
12. Social casino and simulated gambling
13. Ethical floor beyond the law
14. Region configuration pattern
15. Volatile facts (as of Oct 2026 - verify)
16. Worked examples and templates

## 1. Principles
1. Collect the least data that lets the game work; every field creates a duty.
2. Know your audience: general, mixed or child-directed changes everything; decide in the contract.
3. SDKs are processors or independent controllers of your players' data; you answer for them.
4. Consent must be informed, specific, freely given and as easy to withdraw as to give, wherever consent is the legal basis.
5. Design for deletion: players can ask for their data and its erasure; build the pipeline early.
6. Treat minors with higher defaults: no personalisation, no chat, no random paid items, spending limits.
7. Keep records: data map, SDK register, consent logs, odds tables with change history.

## 2. GDPR essentials for games
Applies when you offer services to people in the EU/EEA (and the UK has an equivalent regime), wherever you are based.
- **Legal bases.** For games, usually: contract (to run the account and the game), legitimate interests (security, basic analytics, with balancing), and consent (advertising identifiers, personalised ads, non-essential tracking, marketing). Pick per purpose, document.
- **Principles.** Lawfulness, fairness, transparency, purpose limitation, data minimisation, accuracy, storage limitation, integrity and confidentiality, accountability.
- **Rights.** Access, rectification, erasure, restriction, portability, objection, and rights relating to automated decisions. Build: export (JSON), delete (in-game and via web form), and a documented response time (a month is the usual legal period; check extensions).
- **Transparency.** Privacy policy in plain language: what, why, who receives data, retention, transfers outside the EU, contact, rights, children's section.
- **Processors.** Contracts (data processing agreements) with analytics, cloud, crash, attribution vendors; track sub-processors.
- **International transfers.** Use recognised mechanisms (adequacy, standard clauses); vendors typically provide these.
- **DPIA.** A data protection impact assessment is needed for high-risk processing (large-scale profiling, systematic monitoring, children at scale); do one when personalisation or behavioural segmentation is central, and especially for child audiences.
- **Breaches.** Notify the authority within the legal window (72 hours is the usual benchmark) when there is risk; keep an incident runbook.
- **ePrivacy and consent for device access.** Reading or writing identifiers on devices generally needs consent in the EU unless strictly necessary; implement a consent management flow (CMP) at first launch for EU users when using ads or attribution. Use a Google-certified CMP if using Google ad products where required.
- **Dark patterns in consent.** No pre-ticked boxes, no hiding "reject", equal prominence for accept and reject.

## 3. GDPR-K and children in Europe and the UK
- GDPR Article 8: where consent is the basis for an online service offered directly to a child, the child must be at least 16, unless the member state sets a lower age (down to 13). Below that age, consent must come from the holder of parental responsibility, with reasonable efforts to verify. Ages vary by country; maintain a country table.
- Recital-level guidance: children merit specific protection regarding marketing, profiling and data collection.
- **UK Age Appropriate Design Code** (Children's Code): 15 standards for services likely to be accessed by children, including best interests of the child, high privacy by default, no nudge techniques to weaken privacy, geolocation off by default, profiling off by default, data minimisation, parental controls transparency. Applies to games likely to be used by under-18s, not only child-directed ones.
- Other EU developments: authorities have focused on dark patterns and in-game currencies obscuring real cost; consumer authorities published principles on virtual currencies (2025) urging pricing in real currency alongside virtual, clear information, and no pressure on children. Verify the current status.
- Practical design consequences:
  1. Neutral age screen (ask for birth year without hinting the "right" answer).
  2. Restricted mode for minors: no personalised ads, chat off or pre-moderated, no personalised offers, no push marketing, spending limits, no random paid items.
  3. Parental dashboard where available (platform family features).
  4. Simplified, readable privacy notice for the young audience.

## 4. Amended COPPA (US)
Applies to operators of services directed to children under 13 and to operators with actual knowledge that they collect personal information from a child under 13.
- Core duties: notice, verifiable parental consent before collecting personal information, parental access and deletion rights, data minimisation and retention limits, security, no conditioning participation on unnecessary data.
- **Personal information** includes persistent identifiers used for tracking or advertising (IDFA, GAID, device IDs), geolocation, photos, audio and video of the child, and (after the amendment) biometric identifiers; voice chat touches this.
- The amended rule (published 2025, compliance deadline reported as Apr 22, 2026) tightened: written information security programme, retention policy and deletion, separate verifiable parental consent for disclosing children's data to third parties (for example targeted advertising), and stricter handling in mixed-audience services. Verify exact obligations against the FTC text.
- **Directed to children** is a facts-and-circumstances test: subject matter, visual content, animated characters, child-oriented activities, music, age of models, ads directed to children, evidence of actual audience. Cute art and cartoon characters count even if your terms say 13+.
- **Mixed audience**: you may use a neutral age screen and treat under-13s differently (no collection without consent). Do not encourage false ages.
- **Safe harbor programmes** exist; they are optional, approved industry codes.
- Penalties are substantial per violation; settlements involving games and children have occurred. Treat this as a high-severity area.
- Design consequences:
  1. Decide early: either a true kids product (separate SKU, certified SDKs, no behavioural ads, parental gate) or a general-audience product with an under-13 exclusion and an age screen.
  2. Ads: use child-directed treatment flags on every ad SDK (AdMob and mediation platforms provide them) and only certified networks.
  3. Analytics: use SDK settings that disable advertising identifiers, or avoid persistent identifiers.
  4. Chat and UGC: off for under-13s unless you have a full consent and moderation stack.
  5. IAP: parental gate before any purchase; platform parental approval features.
  6. Deletion and retention: automated.

## 5. CCPA/CPRA and US state privacy laws
- California consumer privacy law (CCPA as amended by CPRA) gives residents rights to know, delete, correct, opt out of sale or sharing of personal information (including for cross-context behavioural advertising), and limit use of sensitive data. Thresholds for applicability depend on revenue, volume of records, or share of revenue from data sales; check whether you qualify.
- Requirements in practice: privacy notice at collection, "Do Not Sell or Share My Personal Information" link where applicable, honour opt-out preference signals, contracts with service providers, special rules for minors (opt-in required for selling or sharing data of consumers under 16, parental opt-in under 13).
- Many other US states have comprehensive privacy laws with similar rights and various thresholds; a single privacy-rights flow (access, delete, opt-out) serves all of them.
- Washington and some states have health or biometric data laws that matter if you scan faces or voices.
- The universal approach: build one "Privacy and data" screen with consent toggles, data export, deletion, and ad personalisation controls; show region-appropriate text.

## 6. Age assurance laws and platform signals
- Several US states passed laws placing age-verification and parental-consent duties on app stores and/or developers; effective dates reported for Texas (Jan 1, 2026), Utah (May 7, 2026) and Louisiana (Jul 1, 2026). Platform responses include Apple's Declared Age Range API and consent revocation and re-consent signals. Litigation and amendments are likely; verify the current state of each law.
- Outside the US, regulators (UK, EU members, Australia and others) are pushing age assurance for online services; the specifics evolve rapidly and often target social features and adult content rather than games per se, but games with chat, UGC or gambling-like features can fall within scope.
- Developer pattern: consume the platform's age signal when available, otherwise use a neutral age screen; map the signal to a feature profile (see section 14); never rely on self-declared age alone for gambling-adjacent features.
- Keep age data minimal: store the age band, not the birthdate, when possible.
- Verification methods (ID checks, facial age estimation) involve sensitive biometric data; prefer platform-provided signals over rolling your own.

## 7. ATT and platform tracking rules
- iOS App Tracking Transparency: tracking means linking user data from your app with third-party data for advertising or sharing it with data brokers. If you do, show the system prompt before accessing IDFA, with an honest purpose string.
- Denial must not degrade the core experience unfairly; offer the same game.
- Fingerprinting to bypass ATT is prohibited; privacy manifests and required-reason APIs make misuse detectable.
- Android: advertising ID (GAID) usage declared in Data safety and governed by Play policy; users can delete the ID; apps for children must not transmit it.
- Attribution on iOS uses Apple's privacy-preserving attribution frameworks with conversion value schemas; on Android, advertising ID based measurement continues.
- Opt-in rates reported in sources conflict; assume low and plan UA accordingly (`marketing-ua`).

## 8. Implementation checklist: data, consent, SDKs
- [ ] Data map: every field, purpose, legal basis, retention, recipient.
- [ ] SDK register with each SDK's data collection and child-directed support.
- [ ] Privacy policy: plain language, regional addenda, children's section, contact, reachable URL.
- [ ] First-run flow: age screen, regional consent (CMP in EU/UK), ATT prompt timing.
- [ ] Settings: privacy hub with consent toggles, data export, delete account, ad personalisation off.
- [ ] Backend: delete and export jobs, retention schedules, audit logs.
- [ ] Network audit: run the game through an intercepting proxy in each configuration (adult, minor, denied consent) and compare to claims.
- [ ] Logging: no personal data in crash logs or analytics events (see `event_taxonomy.py` for event naming; keep PII out of event properties).
- [ ] Vendor contracts and transfer mechanisms.
- [ ] Incident runbook and contact.
- [ ] Store forms updated from the register (`store-release`).
- [ ] Re-review whenever an SDK changes or a new feature collects data.

## 9. Loot boxes: concepts and design options
Definition used here: a purchasable item whose contents are determined by chance and which the player pays for directly or via paid virtual currency. Gacha, crates, card packs, and random-reward bundles all qualify.
Legal question is usually whether the random item is a game of chance with a thing of value, which depends on whether items can be cashed out, traded or have real-world value, and on the jurisdiction's gambling definitions. Regulators also consider consumer protection and minors.

Design options, from least to most exposure (inference, not legal guarantees):
1. Direct purchase of known items, battle passes with fixed rewards, fixed-content bundles.
2. Earn-only randomness (no purchase link, e.g. random drops from play).
3. Random items obtainable for premium currency that is also earnable free, with odds disclosed and pity guarantees.
4. Paid random items with disclosed odds, spending caps, minor restrictions.
5. Paid random items with tradeable or cash-out value: highest exposure; avoid.
Jurisdiction-specific switch: per-country flag disables or replaces paid random items (replace with direct purchase of the same set at a published price).

## 10. Loot boxes by jurisdiction
Summaries based on reported positions; confirm with counsel before launch (Oct 2026 context).
| Jurisdiction | Position (summary) | Design response |
|---|---|---|
| Belgium | Paid loot boxes treated as gambling under its gambling law since 2018; fines and criminal penalties reported, higher when minors involved | Disable paid random items; offer direct purchase |
| Netherlands | An attempted enforcement against a major publisher was overturned in 2022; no effective ban reported, but consumer-protection scrutiny continues | Disclose odds; watch consumer authority action |
| Brazil | ECA Digital law (children's online protection) bans selling loot boxes to under-18s, effective March 2026; a court reportedly ordered Riot Games to pay damages and to add age verification and probability disclosure | Disable for minors in Brazil; age verification; odds shown |
| China | A Ministry of Culture notice effective May 1, 2017 requires public disclosure of the content and draw probability of randomly drawn paid items, and of draw results; the NPPA's December 2023 draft measures (including limits on spending incentives) were pulled from its website in January 2024 and their status is unclear; operating requires local licensing and a local entity | Publish odds; verify the current rules; use a licensed local publisher |
| Japan | "Kompu gacha" (complete-the-set mechanics, where collecting a full set triggers a reward): in May 2012 the Consumer Affairs Agency said it violated the premiums and representations law (enforced from July 2012) and operators withdrew it; the industry self-regulates on rate display (guidelines not re-checked) | Do not ship complete-set gacha; disclose odds |
| South Korea | Probability disclosure for chance-based items became mandatory in March 2024 (Game Industry Promotion Act amendment, date from reporting on Nexon's appeal); the consumer regulator fined Nexon Korea 11.6 billion won in January 2024 for undisclosed odds changes; penalties under the new law were not checked | Publish accurate odds; keep an audit trail |
| Australia | Games classified after Sep 22, 2024 that contain paid chance-based items are rated at least M; simulated gambling content is R18+ | Expect higher rating; avoid simulated gambling |
| United Kingdom | Government chose industry self-regulation over legislation (July 2022); the games industry published 11 principles on paid loot boxes in July 2023 (odds disclosure, parental controls, spending controls); independent research reported weak compliance; check for later legislation | Follow industry principles; use platform parental tools |
| European Union | No EU-wide ban; consumer law applies (unfair practices, price transparency); possible further legislation reportedly not before 2028 | Odds, clear pricing, no pressure on minors |
| United States | No federal ban; litigation and state attorney attention exist; FTC acts on unfair practices involving kids and unclear charges (HoYoverse, January 2025: $20 million penalty and parental consent for loot-box purchases under 16; Epic Games, December 2022) | Odds, parental controls, refund handling |
| Platforms (global) | Apple and Google require odds to be disclosed before purchase for randomised paid items | Show odds on the purchase screen |
Maintain the matrix in `.gamestudio/contract.json` or a docs file; changes need compliance-officer review.

## 11. Odds disclosure and pity systems
- Show the probability of each outcome category, and for systems with pity, rising rates or guarantees, describe them accurately including how counters reset.
- Odds shown must match the server tables exactly; test it. Compute effective rates with `${CLAUDE_PLUGIN_ROOT}/scripts/gacha_calc.py` (including expected pulls to a target item) and publish rounding that does not overstate chances.
- Show cost-to-guarantee in real currency or clearly convertible terms where possible; regulators dislike obscured costs via virtual currencies.
- Keep a change log of odds and publish updates before they take effect when the law or platform requires.
- Do not use dynamic or personalised odds that vary by player spending without legal advice; many regimes treat this as unfair.
- Provide purchase history, spending limits for adults, and refund information.
- Accessibility: odds must be readable text, not only images (`accessibility-localization`).

## 12. Social casino and simulated gambling
- Social casino games simulate slots, poker or roulette with virtual chips that have no cash value. They are usually not regulated as real-money gambling but face: platform rules (age restrictions, ratings, and Apple and Google policies on simulated gambling and real-money gambling), consumer-protection and class-action scrutiny in some US states, and age ratings (for example R18+ in Australia for simulated gambling).
- Compliance pattern: 18+ gating, clear statement that play does not imply real-money success, no prizes of real-world value that make it a sweepstakes unless properly structured, responsible-play tools (time and spending limits), and no targeting of minors.
- Real-money gambling, sweepstakes, prize draws and skill contests are separate regulated areas needing licences and counsel in each jurisdiction; stores impose their own approval processes for real-money gambling apps. Out of scope for the default studio flow: stop and escalate.
- Crypto, tokens and NFTs in games raise financial-regulation and platform-policy issues; escalate before any such design.
- Rewarded ads for chips and "free spin" marketing to children are especially problematic.

## 13. Ethical floor beyond the law
- No countdown pressure and shame messages directed at minors.
- Spending limits and a visible spend summary; easy parental controls.
- Do not obscure real cost behind multi-layer currencies; show a price reference.
- Do not exploit sunk cost and fear of loss against vulnerable players; cap aggressive offers after repeated spending (whale protection, a cooling-off prompt after unusual spend).
- Do not hide the off button for notifications, ads and data collection.
- Do not run dark-pattern consent or cancellation flows.
- Provide a way to report and get help for gambling-like behaviour.
- Review with `player-psychology` and `monetization`: ethical monetization is doctrine item 8.

## 14. Region configuration pattern
Define profiles consumed by the game at runtime (remote config), selected from country, age signal and consent state:
| Profile | Ads | Chat/UGC | Paid random items | Push marketing | Analytics IDs |
|---|---|---|---|---|---|
| adult-default | personalised if consented | on | on with odds | opt-in | per consent |
| adult-strict-region (e.g. Belgium) | per consent | on | off, direct purchase instead | opt-in | per consent |
| minor-general | non-personalised or off | off or restricted | off | off | none or non-advertising |
| child-directed | certified, non-behavioural only | off | off | off | none |
Implementation notes: default to the strictest profile until the signal arrives; log the profile with each purchase event; unit-test profile resolution; run the proxy audit for each profile.

## 15. Volatile facts (as of Oct 2026 - verify)
- Amended COPPA Rule: published Apr 22, 2025; compliance deadline Apr 22, 2026; biometrics counted as personal information. Sources: https://toyassociation.org/PressRoom2/News/2026-News/updated-coppa-rule-requirements-take-effect-april-22.aspx ; https://www.ggwp.com/blog/coppa-compliance-for-game-companies/ ; https://www.loeb.com/fr/insights/publications/2025/05/childrens-online-privacy-in-2025-the-amended-coppa-rule
- US app-store age laws and Apple APIs: Texas SB 2420 (Jan 1, 2026), Utah (May 7, 2026), Louisiana (Jul 1, 2026). Sources: https://9to5mac.com/2025/11/04/app-store-texas-sb2420-new-apis/ ; https://www.pocketgamer.biz/texas-enforces-new-age-verification-law-for-app-stores-and-developers
- Apple EU child-safety rules for payments from Oct 1, 2026: https://www.apple.com/newsroom/2026/08/apple-announces-changes-for-apps-in-the-european-union/
- Brazil ECA Digital and the Riot Games ruling (damages figures reported inconsistently): https://www.sheepesports.com/articles/brazil-court-orders-riot-games-to-pay-eur2-5m-over-league-of-legends-loot-boxes/en ; https://programminginsider.com/loot-boxes-regulation-and-where-the-line-sits-in-2026/
- Belgium, Netherlands, EU Digital Fairness Act outlook: https://programminginsider.com/loot-boxes-regulation-and-where-the-line-sits-in-2026/
- Australia classification of loot boxes (Sep 22, 2024): https://www.pcworld.com/article/2464538/all-games-with-loot-boxes-will-be-rated-m-or-higher-in-australia.html ; https://www.pocketgamer.biz/australia-sets-new-rules-for-video-games-with-gambling-like-content
- GDPR Article 8 text: https://gdpr-info.eu/art-8-gdpr/
- Platform odds disclosure rule: https://developer.apple.com/app-store/review/guidelines/
- Loot-box regimes checked on 2026-10-20 (unofficial translations or press reports unless noted): China's notice effective May 1, 2017 ([China Law Translate](https://www.chinalawtranslate.com/en/ministry-of-culture-notice-regarding-strengthening-regulation-online-gaming-operations/), [Mondaq](https://www.mondaq.com/china/gaming/558200/china-ministry-of-culture-released-new-regulation-on-online-game-operation)) and the NPPA's draft of December 22, 2023, removed from its site in January 2024 ([DT Next](https://www.dtnext.in/lifestyle/technology/china-regulator-removes-draft-video-game-rules-from-website-shares-jump-763035), [Insider Gaming](https://insider-gaming.com/chinese-gaming-rules-tencent/)); Japan's 2012 kompu gacha position ([Bloomberg](https://www.bloomberg.com/news/articles/2012-05-18/japan-consumer-agency-says-complete-gacha-game-feature-illegal), [Game Developer](https://www.gamedeveloper.com/business/why-quot-kompu-gacha-quot-was-banned)); South Korea's March 2024 disclosure duty and the Nexon fine ([Anime News Network](https://www.animenewsnetwork.com/news/2024-01-05/korean-ftc-fines-nexon-usd8.8-million-for-allegedly-manipulating-draw-odds-in-maplestory-game/.206181), [Inven Global](https://www.invenglobal.com/articles/20319/nexons-maplestory-appeals-fine-as-seoul-high-court-resumes-hearing-in-april)); the UK's 2022 decision and 2023 principles ([Lewis Silkin](https://www.lewissilkin.com/insights/2023/07/24/new-uk-principles-and-guidance-on-loot-boxes-published-102ik8a), [5Rights Foundation](https://5rightsfoundation.com/research-reveals-non-existent-enforcement-of-industry-led-standards-on-loot-boxes)); and the FTC's HoYoverse settlement of January 17, 2025 ([FTC press release](https://www.ftc.gov/news-events/news/press-releases/2025/01/genshin-impact-game-developer-will-be-banned-selling-lootboxes-teens-under-16-without-parental)). Still unconfirmed: the statute texts, any post-2024 changes in China, Korea and Japan's current rate-display guidelines, and post-deadline COPPA enforcement in games. Verify each with counsel or official sources before relying on them.

## 16. Worked examples and templates

### Neutral age screen spec
1. Ask "What year were you born?" with a year picker that does not default to an adult year.
2. Compute the age band (under 13, 13 to 15, 16 to 17, adult); store the band and the country, not the birthdate.
3. If under the threshold for the profile, do not allow retry-by-back-button loops: store a local flag for a cooling period, so a child cannot simply enter a different year immediately.
4. Do not display "you must be 13 or older" before the answer; that coaches false answers.
5. If the platform provides a declared age range, use it and skip your own screen where the platform's signal is trusted.
6. Re-evaluate when the age signal changes (consent revoked, age band crossed).

### Worked example: casual puzzle game with rewarded ads and a gem shop
- Audience decision: general audience, 13+ recommended, cute art style. Cute art raises the "directed to children" risk, so the contract sets `age_min: 13`, includes an age screen, and treats under-13 answers as a restricted profile.
- SDKs: analytics (configure to avoid advertising identifiers in minor profile), ads mediation (child-directed flags enabled in minor profile, personalised ads off), IAP, crash reporting. Each is listed in the SDK register with data types.
- Monetization: gems purchasable directly in packs with fixed content; a "lucky chest" paid with gems has disclosed odds and is disabled in Belgium and for minors in Brazil.
- Privacy hub: consent toggles, export, delete account, ad personalisation control.
- Store forms: Data safety and App Privacy generated from the register; IARC and Apple age answers mention chance-based items.
- Verification: proxy audit for adult consented, adult denied, minor profiles; check that the minor profile sends no advertising ids and does not load personalised ads.

### Worked example: deciding between "kids game" and "general game"
| Question | If yes | If no |
|---|---|---|
| Is the primary audience under 13 by theme, art, music, characters, marketing? | Build as a kids product: certified SDKs only, no behavioural ads, parental gate, no random paid items, consent flows | Continue |
| Do you want behavioural ads or attribution with advertising ids? | Not compatible with a kids product; choose general audience and exclude under-13 | Kids product feasible |
| Do you want chat, UGC or social features? | Heavy moderation and consent obligations; probably omit for kids | Fine |
| Is revenue plan dependent on ad personalisation? | Do not target children | Kids product feasible |
Record the answer in the contract so `compliance_preflight.py` can enforce the right checks.

### Data request runbook
1. Intake via in-app form or web page; verify identity against the account (login or emailed code).
2. Export job collects account, progress, purchase history, consent logs, and analytics identifiers held by you; vendor data is requested from vendors where you are the controller.
3. Deletion job removes or anonymises personal data, informs processors, keeps what the law requires (purchase and tax records) with a stated retention.
4. Respond within the legal period, log the request and its outcome.
5. Test the whole runbook quarterly with a test account.

### Odds table template
```
Pack: Lucky Chest
Cost: 100 gems (price reference: 100 gems = see shop pack prices)
Outcome   Probability   Notes
Common    70.0%
Rare      25.0%
Epic       4.5%         Guaranteed at least one Epic in every 20 chests (counter resets on Epic)
Legendary  0.5%         Rate stated before pity; no rate increase
```
Generate the numbers from the server table, not by hand; add a CI check that the published table equals the server table.
