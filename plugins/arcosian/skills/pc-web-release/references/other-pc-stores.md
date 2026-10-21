# Other PC Stores: Epic, GOG, Microsoft Store and Game Pass, Mac App Store

This file covers the PC stores beyond Steam and itch.io: Epic Games Store self-publishing, GOG, the Microsoft Store and the route to PC Game Pass through ID@Xbox, and the Mac App Store. For each it gives who can publish, what is required, fees and revenue share, and when the store is worth the support cost. Several pages blocked automated fetches, so each item carries a confidence label: "verified" means read on an official page in Oct 2026, "reported" means secondary source, "unverified" means not confirmed. Every submission is approved by a human.

## Contents
1. Choosing a second store
2. Epic Games Store
3. GOG
4. Microsoft Store
5. ID@Xbox and PC Game Pass
6. Mac App Store
7. Comparison table
8. Second-store checklist
9. Store adapter pattern
10. Worked example: adding a second store
11. Terms a human must read before signing

## 1. Choosing a second store
1. A second store adds support work: another build upload, another set of achievements and cloud saves, another store page, another set of rules and payouts.
2. Add one only if its audience or terms beat that cost. Evidence to use: sales share by store from your own data after launch, wishlist requests ("is it on GOG?"), or a deal.
3. Keep game code store-agnostic: an adapter interface for achievements, saves, overlay and user id, with one implementation per store (see `game-architecture`).
4. Do not sell the same keys across stores in conflict with their terms: Steam keys have rules for use outside Steam (read Valve's key policy before giving Steam keys to other storefronts).
5. Keep prices aligned across stores; Steam Early Access, for example, forbids pricing above other stores.

## 2. Epic Games Store
Official starting points: https://store.epicgames.com/distribution and https://dev.epicgames.com/docs (the docs page returned 404 in this session).
- Revenue share (verified from Epic's June 2025 announcement via search result): developers keep 100 percent of the first 1 million USD net revenue per product per year, then the standard 88/12 split; the threshold resets each 1 January from 2026; it applies on the platforms where Epic's payment processing is used. Verify the current terms page.
- Separate "Epic First Run" opt-in programme: 100 percent for the first 6 months (reported; check terms and the exclusivity required).
- Access: self-publishing through the Epic Games Store developer portal; historically applicants were reviewed and invited (reported from the 2023 launch coverage). Onboarding includes legal, tax and bank verification, a configuration review before launch.
- Requirements reported at self-publishing launch: multiplayer games must support crossplay across PC storefronts (your own solution, Epic Online Services, or a third-party system not tied to one store); games with achievements on other PC stores must enable Epic achievements; an age rating is needed (Epic offers IARC through the developer portal at no extra cost); prohibited content is not allowed. Verify each against the developer portal.
- Fee: a 100 USD per-game fee was reported in 2018-era articles; unverified now.
- Tech: Epic Online Services (EOS) provide achievements, friends and crossplay and are optional; the Epic launcher integration is lighter than Steamworks. Epic uses its own build upload tool (BuildPatch Tool) and branches called sandboxes and artifacts: check the docs for names and commands before scripting.
- When worth it: you have wishlist traction elsewhere, want the better revenue terms, or an Epic deal pays an advance. The store audience skews toward free-game claimers, so expect lower conversion per visit than Steam.
- Human steps: account, agreements, tax, rating questionnaire, store page submission, release date approval.

## 3. GOG
Official starting point: GOG's developer submission page and support FAQ (https://support.gog.com/hc/en-us/articles/11382878039197-Releasing-your-game-on-GOG-FAQ returned 403; contents unverified).
- Model: curated storefront centred on DRM-free games. Reported: submission through a form, GOG reviews and may invite you to its developer portal; there is a command-line tool for uploading builds (reported as Pipeline Builder; verify the name).
- Revenue share: a 70/30 developer/store split was the launch-era figure (2013 coverage); current terms unverified. Ask GOG.
- Requirements (reported or inferred from GOG's DRM-free stance; verify): the game must run without a launcher or online check; offline installers are produced from your build; GOG Galaxy integration (achievements, cloud saves) is optional; content rules exclude unlabelled explicit material, IP infringement and malware.
- Fit: classic-style, narrative, strategy and RPG games with older or adult audiences; games with strong reviews elsewhere. Pitch with a finished game or a public Steam page plus reviews.
- Work for you: a Windows installer-ready build; no Steamworks calls in the GOG build (compile flag or runtime store adapter); a separate achievement and cloud-save path if you want them.

## 4. Microsoft Store
Source: https://learn.microsoft.com/en-us/windows/apps/publish/partner-center/open-a-developer-account (verified).
- Accounts: Individual or Company. Through the new onboarding flow at storedeveloper.microsoft.com there are no registration fees for either type. Individual: government ID and selfie verification on mobile. Company: DUNS number (recommended) or business documents, a work email on the company domain; manual review typically 2 to 5 business days (3 appeals per verification type).
- Individual accounts are for hobby or non-business distribution; if the game is part of a business or trade, use a Company account. You cannot convert Individual to Company; make a new account.
- Revenue share: Microsoft's current games share is reported at 12 percent for PC games and 15 percent for apps; confirm on Microsoft's agreement before relying on it (unverified here).
- Packaging: MSIX is the usual package; the Store signs packages on submission, so you do not need your own code-signing certificate for Store distribution (verify in the Partner Center docs). Sideloaded `.exe` outside the Store still needs your own signing (see `signing-and-packaging.md`).
- Game specifics: Xbox features on PC (achievements, cloud saves, Play Anywhere, Game Pass) need the Xbox Live and GDK services and the ID@Xbox programme (section 5). A plain Store listing of a game needs a Partner Center account, age rating (IARC), screenshots, description and package.
- When worth it: you want Windows discoverability, Xbox app presence, controller-heavy games, Game Pass eligibility or Xbox console release later.
- Human steps: ID verification, agreements, submission, certification review.

## 5. ID@Xbox and PC Game Pass
Source: https://learn.microsoft.com/en-us/gaming/game-publishing/onboarding/onboarding-join-id-at-xbox (verified, page dated 2026).
1. Prerequisites: register as an Xbox partner and sign the NDA; accept the App Developer Agreement; enrol in Partner Center. Requirements reported: age 18 or over (or a guardian), signed NDA, a country where Microsoft can do business; no cost to join (reported by the docs search summary).
2. Apply: in the Xbox Partner Dashboard select Apply to ID@Xbox; give contact details, a shipping address for dev kit hardware, a registered business number, developer and/or publisher role, studio presence (website, public trailers).
3. Submit a game concept (up to 10 at once): developer and publisher, key features, target release date, platforms, markets and pricing, Xbox network features and user-generated content. Review typically 10 to 15 business days, up to 3 weeks.
4. If approved, sign the Title Licensing Agreement and the GDK License Agreement; then you receive full Xbox development and publishing features, and onboarding continues for dev kit hardware and payouts.
5. After joining you can pitch the game for strategic funding including Game Pass and the Developer Acceleration Programme.
6. ID@Xbox covers Xbox consoles and Xbox on PC. Whether and how a title enters PC Game Pass is a business decision by Microsoft, not an automatic outcome: unverified rules. See `console-pathway` for the console side.

## 6. Mac App Store
Sources (not fetched in this session; verify): https://developer.apple.com/programs/ and https://developer.apple.com/app-store/small-business-program/
- Needs the paid Apple Developer Program (reported 99 USD per year) and App Store Connect; the same account used for iOS (`store-release`).
- Revenue share: Apple's standard commission is 30 percent, 15 percent under the Small Business Program (reported; verify).
- Requirements: App Sandbox is required for App Store distribution (Godot's macOS export docs list it; https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_macos.html); sign with App Store certificates (distinct from Developer ID); upload a package through Xcode, Transporter or `xcrun altool` successors (check Apple's current tool); age rating questionnaire and privacy declarations as for iOS.
- Constraints: sandbox limits file access and helper processes; some Steamworks integrations and launcher patterns do not work in the sandbox. Games that ship Steamworks cannot sell the same binary in both places unchanged; use a separate build configuration.
- When worth it: a Mac-first audience, a game that already ships on iOS from the same codebase (Apple platforms share Metal, StoreKit and controllers), or Apple Arcade pitches (a separate invitation programme; unverified).
- Direct distribution alternative: Developer ID signing and notarisation, used for Steam and itch.io (see `signing-and-packaging.md`).

## 7. Comparison table
| Store | Access | Fee | Revenue share | Confidence |
|---|---|---|---|---|
| Steam | Open; onboarding checks | 100 USD per app | Standard tiers: verify Distribution Agreement | Fee verified; share unverified |
| itch.io | Open | None | Default 10 percent, seller chosen 0 to 100 | Reported from official docs |
| Epic Games Store | Self-publishing, reviewed | 100 USD per game reported (2018): unverified | 100 percent of first 1M USD per product per year, then 88/12 | Share verified (2025 news); fee unverified |
| GOG | Curated, invite after submission | Unverified | 70/30 launch-era: unverified | Unverified |
| Microsoft Store | Open with verification | None via new flow | Reported 12 percent (PC games): unverified | Fee verified |
| ID@Xbox | Concept approval | None reported | Per Title Licensing Agreement (NDA) | Process verified |
| Mac App Store | Apple Developer Program | 99 USD per year reported | 30 or 15 percent reported | Unverified |

## 8. Second-store checklist
1. Reason recorded: which audience or term justifies the work.
2. Terms read by a human: fees, exclusivity, key rules, price parity, tax.
3. Store adapter implemented and tested; Steamworks calls compiled out of that build.
4. Age rating and privacy answers consistent with the Steam page.
5. Build signed or packaged as the store requires.
6. Store page assets resized to the store's specification.
7. Human approves submission; record store, version, date and build id in the release report.
8. Support rota extended: where do bug reports from this store arrive?

## 9. Store adapter pattern
Goal: one game binary logic, many storefront integrations.
1. Define an interface with these calls: `init()`, `shutdown()`, `user_id()`, `unlock_achievement(id)`, `set_stat(id, value)`, `save_cloud(name, bytes)`, `load_cloud(name)`, `open_overlay_store_page()`, `is_online()`, `input_glyph(action)`.
2. Implement it per store: Steam (GodotSteam, Steamworks.NET or Facepunch.Steamworks), Epic (Epic Online Services), GOG (Galaxy SDK, optional), Microsoft (GDK services), and a no-op "standalone" implementation for itch.io and direct downloads.
3. Select the implementation at build time (a build flag or export preset feature tag) so that store SDK binaries are absent from builds that do not use them. This also keeps store SDK licences out of the wrong packages.
4. Keep save data in one local format with a version number; cloud sync is a layer on top. Never let a store SDK own the only copy.
5. Test the standalone implementation in CI on every commit; test each store implementation on a release candidate with a real test account.
6. Achievement ids should be identical across stores where possible; keep a table in the project (`achievements.csv`) used to generate each store's config.

## 10. Worked example: adding a second store
Game: a 2D premium game, 14.99 USD, launched on Steam 60 days ago with 1,800 sales and an average of 12 sales per day now.
1. Question: GOG, Epic or the Microsoft Store?
2. Evidence: 40 forum posts asking for a DRM-free version; no Windows Store requests; Epic would need a store adapter plus crossplay (not applicable, single-player).
3. Estimate: GOG work is about 3 to 5 days (build flavour, installer-ready layout, a no-Steam audit, page assets); expected extra sales are small and uncertain; a rough planning guess is 5 to 15 percent of Steam units (an estimate, not data).
4. Decision: submit to GOG with the Steam page, review count and a polished build; do not start Epic or Microsoft until GOG's answer and the first month of its sales are known.
5. Human approves the application text, the terms and the build upload; the agent prepares the build, the checklist and the asset resizes.
6. Record the outcome and the units sold after 30 days in `.gamestudio/reports/`, so the next decision uses real numbers.

## 11. Terms a human must read before signing
An agent can summarise a contract; only a human signs it. Check these clauses on every store and publisher agreement:
| Clause | Question to answer |
|---|---|
| Exclusivity | Is the game barred from other stores, for how long, and does a window apply to price or content? |
| Price parity | Must the price match other stores in every currency? |
| Revenue share | What is the percentage, what thresholds change it, and is it gross or net of taxes and refunds? |
| Payment terms | Days to payout, minimum payout, currencies, withholding tax forms |
| Refunds and chargebacks | Who bears them; how are they netted from later payouts? |
| Keys | Can you sell or give away store keys, and where? |
| Termination | What happens to existing owners if the store or the game is removed? |
| Data and privacy | Which player data is shared with you; whose privacy policy applies? |
| Content rules | AI-generated content disclosure, adult content, user-generated content |
Save the answers in the project's release notes. If a clause is unclear, ask the store's partner support in writing and record the reply.
