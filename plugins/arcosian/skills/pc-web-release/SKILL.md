---
name: pc-web-release
description: Release knowledge for PC and web games - Steam (Steamworks, store page, wishlists, Next Fest, Playtest, SteamPipe, Deck review), itch.io and butler, web portals, self-hosted web builds, Epic, GOG, Microsoft Store, Mac App Store, and code signing for macOS, Windows and Linux. Use for "put my game on Steam", "butler push", "web export headers", "notarise my Mac build", "which store first".
---

# PC and Web Release

## What this skill gives you
- A decision procedure for where to release a PC or web game, when to open the store page, how to price, and whether to ship a demo, playtest or early access.
- A release checklist with exact steps, from account onboarding to release day, and the rule that every upload is approved by a human.
- Exact upload recipes: SteamPipe (`steamcmd +run_app_build`), `butler push`, web hosting headers, macOS notarisation, Windows signing.
- Store facts (fees, revenue share, asset sizes, deadlines) isolated at the end with source URLs, so they can be rechecked.

Mobile stores are covered by `store-release`. Consoles are covered by `console-pathway`. This skill does not repeat either.

## Core models
**1. The store page is the product's first release.** On Steam the page must be public for at least two weeks before launch, and wishlists collected during that time drive launch-day visibility. Open the page early; ship the build late.

**2. Two clocks again.** The account clock (identity, bank and tax checks take days to weeks; Steam also enforces a waiting period between paying the app fee and release for first titles) runs before you have a build. Start it in week one of production, not in launch month.

**3. Build, depot, branch, live.** On Steam a build is uploaded to depots, then assigned to a branch, and the default branch is what players get. Uploading is reversible; setting the default branch live is the public event. The same split exists on itch.io (channels) and the web (a staging URL before the production URL).

**4. Cheap distribution first, curated distribution later.** itch.io and web portals need no review of the business, so use them to test the game and the pitch. Steam needs a fee and a page. Curated stores (GOG, console programmes) want proof of traction. Sequence by cost of failure.

**5. Trust is a deliverable.** An unsigned Windows or macOS build triggers warnings that cost installs. Signing, notarisation and reputation are release work, with lead time (identity validation, certificate issue, SmartScreen reputation).

**6. Web is a different runtime.** A web build is limited by download size, browser memory, audio unlock rules, headers (compression, cross-origin isolation) and portal SDKs. Decide the web target before the art budget, not after.

**7. Every upload is human-approved.** Agents prepare builds, scripts and checklists. A human approves each upload, each "set live", each store submission and each price or page change. The core hooks ask before `steamcmd ... +run_app_build`, `butler push` and store submissions; never bypass them and never put credentials in files.

## Decision procedures

### A. Which stores, in what order
| Situation | Release plan | Why |
|---|---|---|
| Game jam, prototype, under 1 month of work | itch.io (HTML5 or desktop), pay-what-you-want | Zero friction, feedback |
| Casual or hyper-casual, runs in a browser, ad-funded | Poki, CrazyGames, others via portal SDK, plus itch.io | Portals bring traffic; ads pay |
| Premium PC game, 5 or more hours | Steam first; itch.io demo or page for community | Largest PC audience, wishlist tools |
| Premium game with Mac or Linux audience | Steam plus signed macOS build, Linux native or Proton | See `references/signing-and-packaging.md` |
| DRM-free, narrative or classic-style game | Steam plus GOG (invite or curation; apply after Steam page is live) | GOG audience values DRM-free |
| Xbox or Windows Store audience, controller game | Microsoft Store, ID@Xbox later | See `references/other-pc-stores.md` |
| Already have traction (10k+ wishlists, press) | Add Epic Games Store | Revenue terms are favourable; storefront reach is smaller |
Default: itch.io page and a demo, Steam Coming Soon page, Steam launch, then secondary stores 1 to 3 months later if sales justify the support cost. Never exclusive-launch without a contract that pays for it.

### B. When to open the store page
1. Do not open a page before there is a trailer that shows real gameplay and 5 or more real screenshots. A weak page converts badly and cannot be un-seen.
2. Target: page public 6 to 12 months before release for a premium game (estimate; Valve's minimum is two weeks).
3. Start Steamworks onboarding at least 90 days before the earliest release date (bank and tax verification up to 30 days; first-title waiting period; store review 1 to 5 days).
4. Page copy and capsules must match the game; mismatched art is a review and refund problem.

### C. Pricing
1. Start from comparable titles: list 5 to 10 games with similar genre, length and review count on Steam; read their prices (steam page, SteamDB).
2. Price by hours of content: a starting point of 1 to 2 USD per hour for a premium indie game, rounded to a price point ending .99 (estimate, validate against comparables).
3. Set regional prices deliberately in all offered currencies; do not leave the conversion tool default unreviewed. Missing a currency makes the game unavailable to that region.
4. Plan discounts: Steam restricts discounts near release and after price rises (see `references/steam.md`). Launch discount of 10 to 20 percent is typical; do not exceed what you will repeat.
5. Raise prices rarely. A price increase triggers a 30-day discount lockout on Steam.
6. Free-to-play on PC follows `monetization` and `economy-design`; Steam requires an in-game store and compliant item declarations.

### D. Demo, playtest, or early access
| Goal | Use | Notes |
|---|---|---|
| Collect bug and balance feedback before the page is public | Steam Playtest (free, separate child app, limited or open signup) | Not confidential; playtests must be free |
| Convert wishlists and join Next Fest | Public demo (a demo app attached to the base game) | Needs public page, trailer, demo live before the fest |
| Fund and shape a game that is playable but unfinished | Early Access | Read the Early Access rules; price must not exceed other stores |
| Private build for testers, press, partners | Beta branch with access keys, or itch.io restricted pages | Confidential by default |
| Full launch with no pre-release | Only if the audience is small and the game is tiny | Skips the wishlist engine |
Rule: a demo should show the best 20 to 45 minutes and end on a hook. Do not demo a build you would not release.

### E. Release checklist (all PC and web releases)
1. Contract: platforms, price, age rating, languages, supported inputs in `.gamestudio/contract.json` (see Using the ontology).
2. Accounts started: Steamworks, itch.io, any portal or store. Human completes identity, bank, tax and agreements.
3. Build pipeline: clean export from CI; version string visible in game; crash and log reporting off by default or consented (see `legal-ethics`).
4. Platform builds: Windows x64 (and ARM64 if supported), Linux, macOS universal, web where relevant.
5. Signing: Windows Authenticode, macOS Developer ID plus notarisation. See `references/signing-and-packaging.md`.
6. Store integrations: achievements, cloud saves, Steam Input glyphs; test with the real App ID using a test account.
7. Store page: assets at the exact sizes in `references/steam.md`; trailer; tags; age rating answers; system requirements measured on real hardware.
8. Steam Deck: run the review checklist; request the compatibility review if available (see `references/steam.md`).
9. Smoke test: install from the store on a clean machine (not the dev machine) for each OS; launch, save, reload, update.
10. Human approval: present the exact list (store, branch or channel, build id, version, price) and wait for a yes. Then upload.
11. Upload: `steamcmd +run_app_build` to a non-default branch first; `butler push` to a channel; web deploy to a staging URL.
12. Verify from the store: install the uploaded build from the beta branch or channel, run the smoke test again.
13. Human approval of "set live" or promotion. Then release; keep the previous build id for rollback.
14. Release day: follow the release-day list in `references/steam.md`; watch reviews, crash reports and forum for 48 hours.
15. Record build ids, store links and dates in `.gamestudio/reports/release-<version>-<date>.md`.

### F. Web release procedure (own hosting or portal)
1. Choose the target: portal (follow its rules), itch.io embed, or own domain. A portal build is not the same file as an own-domain build (portals ban external requests, own branding and some SDKs).
2. Engine export settings: Godot single-threaded unless you control headers (`references/itch-and-web-portals.md`); Unity gzip or Brotli with matching `Content-Encoding`.
3. Size budget: portals care about the initial download (Poki wants fast load; CrazyGames states 50 MB initial, 20 MB for the mobile homepage). Test on a throttled connection.
4. Test in Chrome, Firefox and Safari, desktop and mobile; handle audio unlock on first input and storage failures in private mode.
5. Human approves the upload; upload to staging first; verify headers with `curl -I`.

### G. Worked example: a 2D Godot premium game, solo developer
Contract: Windows, Linux, macOS; keyboard and gamepad; 6 hours; price 14.99 USD.
1. Month 0: Steamworks onboarding started (human); fee 100 USD per app, bank and tax checks begin.
2. Month 1: Steam page assets built (header 920x430, main capsule 1232x706, vertical 748x896, small 462x174, library assets), 5 screenshots at 1920x1080, trailer. Human publishes "Coming Soon".
3. Month 3: Playtest app created; 200 players invited in batches; feedback goes to `playtest` skill.
4. Month 6: Demo built, passes build review; Next Fest registered 5 weeks before the fest, demo submitted 3 weeks before.
5. Month 8: Release candidate. macOS build signed with Developer ID and notarised; Windows build signed through a cloud signing service; Linux build tested under the Steam Linux Runtime.
6. Release week: human approves `steamcmd +run_app_build` to branch `staging`; QA installs from it; human sets default branch live; launch discount 15 percent for 7 days (allowed because it takes effect at release).
7. Week after: patch via a new build to `staging`, promote after smoke test; secondary stores (itch.io page, GOG application) considered from sales data.

## Platform specifics
- **Windows**: the largest audience; sign builds; ship x64; test on integrated GPUs and 8 GB RAM machines. SmartScreen warnings fall as reputation builds.
- **macOS**: requires Developer ID signing and notarisation for direct distribution; Steam builds should also be signed and notarised. Apple Silicon is the default Mac; ship a universal binary or arm64 plus x86_64.
- **Linux**: Steam is the main store; native build plus Steam Linux Runtime or Proton. Steam Deck is a Linux device and a distinct review.
- **Web**: browser memory and download size limit scope; threads need cross-origin isolation; portals add rules and SDKs.
- **Input**: PC players use mouse and keyboard, gamepad, or both; Steam Deck verification requires full controller support (see `platform-targets` for input and UX).

## Anti-patterns
- Putting Steam or butler credentials in scripts, repos or chat. Use a dedicated build account, an environment variable or a stored login done by a human.
- Pushing straight to the default branch without testing from a beta branch.
- Opening the Steam page with placeholder art and then not changing it.
- Treating Steam Coming Soon as optional; skipping the two-week minimum, or starting onboarding in launch week.
- Uploading a web build with default server headers and discovering the wasm file loads uncompressed (3x to 4x larger) or threads fail.
- Shipping an unsigned macOS app and telling players to right-click Open.
- Launching on every store the same day; you cannot support every launch.
- Early Access to "pre-sell" an unfinished game with no plan.
- Raising price just before a planned sale (a price rise blocks discounts for 30 days on Steam).
- Quoting a revenue share or fee from memory instead of the store's page.

## Using the ontology
- Release data lives in `.gamestudio/contract.json` (`meta.platforms` includes windows, macos, linux, web; `meta.input` lists mouse_keyboard and gamepad) and features in `.gamestudio/features.json`. All features must be `done` with five gates before the release checklist starts.
- Store page copy and asset lists should be derived from the contract (title, genre, price, age rating, languages). `store_metadata.py` handles mobile limits; for Steam, keep a `store/steam-page.md` in the project and review it with the `critic` agent.
- Process skills: `ship` runs this pipeline with human checkpoints; workflow `/arcosian:release-candidate` prepares a candidate; agents `arcosian:release-manager` and `arcosian:compliance-officer` apply checks.
- Input and platform UX: `platform-targets`. Console follow-on: `console-pathway`.

## Reference library
| File | What it contains | When to read |
|---|---|---|
| `references/steam.md` | Steamworks onboarding, fee, store assets and sizes, Coming Soon, Next Fest, Playtest, SteamPipe recipes, Deck review, achievements, cloud, Steam Input, pricing, release-day list | Anything on Steam |
| `references/itch-and-web-portals.md` | itch.io and butler, web portals, own web hosting headers, Godot and Unity web export | Web or itch.io release |
| `references/other-pc-stores.md` | Epic, GOG, Microsoft Store and Game Pass, Mac App Store: requirements, fees, revenue share | Adding a second store |
| `references/signing-and-packaging.md` | macOS signing and notarisation, Windows signing and SmartScreen, Linux packaging | Before any public build |

## Volatile facts (as of Oct 2026 - verify)
- Steam Direct fee 100 USD per app, recoupable after 1,000 USD adjusted gross revenue; first-title waiting period (the Steam Direct page says 30 days; the onboarding page text read as 21 days in one fetch: check both); coming-soon page public at least two weeks: https://partner.steamgames.com/steamdirect and https://partner.steamgames.com/doc/gettingstarted/onboarding
- Steam store and library asset sizes: https://partner.steamgames.com/doc/store/assets/standard and https://partner.steamgames.com/doc/store/assets/libraryassets
- Steam Next Fest rules and the editions (October 2026, February 2027, June 2027): https://partner.steamgames.com/doc/marketing/upcoming_events/nextfest
- Steam Playtest: https://partner.steamgames.com/doc/features/playtest
- Steam pricing, regional pricing, discount lockouts: https://partner.steamgames.com/doc/store/pricing
- SteamPipe upload: https://partner.steamgames.com/doc/sdk/uploading
- Steam Deck and Steam Machine compatibility: https://partner.steamgames.com/doc/steamdeck/compat
- itch.io revenue share default 10 percent: https://itch.io/docs/creators/payments ; butler: https://itch.io/docs/butler/pushing
- Portal rules (Poki, CrazyGames): https://developers.poki.com/guide/requirements-quality and https://docs.crazygames.com/requirements/technical
- Epic revenue share terms: https://store.epicgames.com/en-US/news/epic-games-store-updates-revenue-share-keep-100-of-the-first-1m-per-product-per-year
- Microsoft Store account fees (none via the new flow): https://learn.microsoft.com/en-us/windows/apps/publish/partner-center/open-a-developer-account
- Artifact Signing (Microsoft's cloud signing, formerly Trusted Signing): https://learn.microsoft.com/en-us/azure/artifact-signing/overview
- Godot web and macOS export: https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_web.html and https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_macos.html
- Unity web compression: https://docs.unity3d.com/Manual/webgl-deploying.html

## Related skills
- `store-release`: mobile stores, fastlane, ASO; shares the pipeline model.
- `console-pathway`: consoles after PC.
- `ship`: human-gated release process.
- `engine-godot`, `engine-unity`: engine export settings.
- `marketing-ua`: wishlist and trailer strategy.
- `legal-ethics`: privacy, licences, age ratings.
- `platform-targets`: input, UX and performance tiers per platform.
- `qa-testing`: install and smoke tests on clean machines.
