# Steam Release Guide

This file covers releasing on Steam: onboarding and the app fee, store page assets, Coming Soon and wishlists, Next Fest and Playtest, SteamPipe uploads, Steam Deck review, achievements, cloud saves, Steam Input, pricing and the release-day list. Steam facts here were read from Valve's Steamworks documentation in Oct 2026; items marked "unverified" were not confirmed on an official page. Every upload and every "set live" is approved by a human.

## Contents
1. Onboarding and the Steam Direct fee
2. Store page assets and sizes
3. Coming Soon and wishlists
4. Steam Playtest
5. Demos and Steam Next Fest
6. Early Access
7. SteamPipe: depots, branches, build scripts
8. Setting a build live
9. Steam Deck and Steam Machine compatibility
10. Achievements, cloud saves and Steam Input through engine bindings
11. Pricing and regional pricing
12. Release-day checklist

## 1. Onboarding and the Steam Direct fee
Steps as Valve lists them (https://partner.steamgames.com/doc/gettingstarted/onboarding):
1. Sign the digital paperwork (NDA and Steam Distribution Agreement).
2. Pay the app fee: 100 USD (or equivalent) per product, not refundable, recoupable after the product reaches 1,000 USD adjusted gross revenue (https://partner.steamgames.com/steamdirect). The fee cannot be paid with Steam Wallet funds.
3. Complete bank, tax and identity verification. Tax and bank verification takes 15 to 30 days; tax details cannot be changed until verification completes.
4. Prepare the title, store page, builds and pricing in Steamworks.
5. Pass review of the store page and build (1 to 5 days).
6. For your first few titles there is a waiting period between paying the fee and releasing. The Steam Direct page states 30 days; one fetch of the onboarding page showed 21 days. Plan for 30 and recheck.
7. Keep a public Coming Soon page for at least two weeks before release.

What you need ready: legal name of the entity (not a nickname), bank routing and account number where the account holder name matches the legal name, and a tax questionnaire (W-9 style for US entities, W-8BEN style for treaty countries).

Human-only steps: all of the above. An agent can prepare a document pack and a timetable; it must not enter bank, tax or identity data.

Planning rule: pay the fee and start verification at least 90 days before the earliest release date. One fee covers one app; a demo and a playtest are separate apps linked to the base game (check whether further fees apply on the Steam App Fee page: unverified for demos).

## 2. Store page assets and sizes
Required store assets (https://partner.steamgames.com/doc/store/assets/standard):
| Asset | Size (px) | Notes |
|---|---|---|
| Header capsule | 920 x 430 | Required |
| Small capsule | 462 x 174 | Required; 184x69 and 120x45 are generated |
| Main capsule | 1232 x 706 | Required |
| Vertical capsule | 748 x 896 | Required |
| Screenshots | 1920 x 1080 minimum, 16:9 | At least 5 |
| Page background | 1438 x 810 | Optional |
| Bundle header | 707 x 232 | Bundles only |

Library assets (https://partner.steamgames.com/doc/store/assets/libraryassets):
| Asset | Size (px) | Notes |
|---|---|---|
| Library capsule | 600 x 900 | Half-size 300x450 generated |
| Library header | 920 x 430 | Falls back to the header capsule |
| Library hero | 3840 x 1240 | Keep key art in the central 860 x 380 area |
| Library logo | 1280 wide and/or 720 tall, transparent PNG | Half-size generated |

Trailer, icon, community assets and logo formats: see Valve's asset pages (not re-verified in this session). Capsule rules: no review quotes or awards text on capsules, and capsule text should be the game's logo only (Valve's graphical asset rules; unverified here, read them before producing art).

Page content checklist:
1. Short description (one or two sentences, the hook).
2. Long description with feature bullets and a few GIFs or screenshots.
3. 5 or more screenshots from the real game; the first three carry the sale.
4. Trailer first 10 seconds show gameplay, not a logo.
5. Tags: choose accurate tags; Steam uses them for placement.
6. System requirements from measured hardware (minimum: lowest machine that holds 30 fps).
7. Languages with correct support levels (interface, audio, subtitles).
8. Content survey and age rating answers (see `legal-ethics`).
9. Controller support declared correctly (see section 9).
10. AI-generated content disclosure if applicable: the Steam content survey asks; read the current rules before answering (unverified details).

## 3. Coming Soon and wishlists
1. A Coming Soon page needs the store assets, description and at least a trailer or screenshots; it goes through store review.
2. Publish it as soon as it represents the game honestly. The two-week minimum is a floor.
3. Wishlists are the main pre-launch signal. Track daily adds in Steamworks; record the source of spikes (trailer, festival, press).
4. Rule of thumb (estimate, not Valve data): a premium indie game wants several thousand wishlists at launch to appear in launch visibility surfaces, and tens of thousands to be comfortable. Treat these as targets to test, not guarantees.
5. A Coming Soon page can be paired with a Playtest signup button and a demo.
6. The release date can be set to a date or left as a season ("Q2 2027"); a wrong date announced early costs trust, so use a range until the build is certain.

## 4. Steam Playtest
Source: https://partner.steamgames.com/doc/features/playtest
1. Playtest is a free feature: a child app linked to your main game, with no separate store page. Signups appear on the main page.
2. Create the Playtest app from Associated Packages and DLC of your game. Provide library capsule and community assets; the customer-facing name cannot change after release.
3. It goes through a simplified store review plus build review.
4. Enable signups in Special Settings of the Edit Store Page tools.
5. Upload depots and builds as for any app. Add players in groups once the build is live.
6. Signup types: Limited (you grant access in batches; Steam picks randomly and can filter by country) or Open.
7. Keys for a playtest can be requested in large quantities; Valve reviews requests above 50,000.
8. Constraints: playtests must be free (no selling keys or paid bundles); signups are not under NDA, so for confidential testing use the main app with branch access keys instead; playtest data (playtime, reviews, wishlists, achievements) is separate from the main game.
9. When finished, set the playtest to Not Playable and warn testers first.
Use: balance, bugs, onboarding feedback. Feed results into `playtest` and `player-analytics`.

## 5. Demos and Steam Next Fest
Source: https://partner.steamgames.com/doc/marketing/upcoming_events/nextfest
1. A demo is a separate demo-type app attached to the base game. It must pass build review.
2. Next Fest is held three times a year (the Steamworks page lists October 2026, February 2027 and June 2027). The October 2026 edition ran 19 to 26 October 2026 (per press coverage; the next editions' dates must be read from Steamworks).
3. Eligibility: the base game has not joined a previous Next Fest; account in good standing; base game store page public; a publicly playable demo live by the start; the game must not release before the event ends; prologues and short versions of released games are ineligible.
4. Register through the base game, not the demo.
5. Deadlines relative to the start: demo submitted for build review 5 weeks before if you want it live before Press Preview; 3 weeks before if it only goes live for the festival. Press Preview starts 11 days before; the festival trailer launches 4 days before; the event runs for 7 days.
6. The base page needs at least one public trailer; choose primary categories and accurate tags at registration.
7. Release the demo at least 30 minutes before the start (Valve's recommendation) and leave it up afterwards.
8. Demo quality: end on a hook, add a wishlist button reminder, avoid save-breaking updates after review (post-review updates are not reviewed).
9. The October 2026 registration closed 31 August 2026 (press coverage); the pattern suggests registration closes roughly 7 weeks before an edition (inference). Read the next edition's page and calendar the date.

## 6. Early Access
Source: https://partner.steamgames.com/doc/store/earlyaccess
- Playable game at launch; a gameplay trailer is the minimum.
- Not for nearly finished games; not a pre-purchase; not crowdfunding.
- Early Access price must not exceed the price anywhere else; Early Access must not be sold elsewhere before Steam.
- Be clear about the current state; avoid promises of dates or features; disclose save-breaking updates.
- No permanent discounts; a price rise blocks discounts for 30 days (including the launch discount at full release).
- Keep the page current; a notice appears if there is no default-branch build or update event in 12 months.
- Once released, a game cannot return to Coming Soon or Early Access.
Decision: use Early Access only with a content roadmap, a plan for at least 6 months of updates, and a community channel that someone will run.

## 7. SteamPipe: depots, branches, build scripts
Source: https://partner.steamgames.com/doc/sdk/uploading
Concepts:
- Depot: a set of files with a depot id (one per OS or content pack; a game commonly has a Windows depot, a macOS depot and a Linux depot).
- Build: an upload of depot content, with a BuildID assigned by Steam.
- Branch: a named channel; the default branch is what customers get. A build is "live" on the branch it is set to.
- The app build script (VDF) names the depots; the depot build scripts name the files.

Example app build script `scripts/app_build_<AppID>.vdf` (field names from Valve's docs):
```
"AppBuild"
{
	"AppID" "<YOUR_APP_ID>"
	"Desc" "v0.9.3 release candidate"
	"BuildOutput" "..\output\"
	"ContentRoot" "..\content\"
	"SetLive" "staging"
	"Depots"
	{
		"<WIN_DEPOT_ID>" "depot_build_<WIN_DEPOT_ID>.vdf"
		"<MAC_DEPOT_ID>" "depot_build_<MAC_DEPOT_ID>.vdf"
		"<LINUX_DEPOT_ID>" "depot_build_<LINUX_DEPOT_ID>.vdf"
	}
}
```
Example depot build script `scripts/depot_build_<WIN_DEPOT_ID>.vdf`:
```
"DepotBuildConfig"
{
	"DepotID" "<WIN_DEPOT_ID>"
	"ContentRoot" "..\content\windows"
	"FileMapping"
	{
		"LocalPath" "*"
		"DepotPath" "."
		"Recursive" "1"
	}
	"FileExclusion" "*.pdb"
}
```
Field notes: `Preview "1"` writes logs and manifests without uploading (use it to test scripts); `Local` targets a SteamPipe Local Content Server for local tests; `SetLive` names a branch to set live after a successful build; `InstallScript` marks an install script; `FileProperties` with `userconfig` or `versionedconfig` controls overwrite behaviour. Do not put the default branch name in `SetLive`: Valve states the default branch cannot be set live by script.

Upload command (Valve's documented form):
```
steamcmd +login <build_account_name> +run_app_build ../scripts/app_build_<AppID>.vdf +quit
```
Recipe (human approves step 4):
1. Create a dedicated build account in Steamworks users and permissions with only the permissions needed: Edit App Metadata and Publish App Changes To Steam if scripted live-setting is used.
2. A human logs in once to steamcmd interactively (handles Steam Guard); never place the password in a script or the repo. For CI, use the account's stored login on a secured runner or the CI's secret store, as the studio's security policy allows.
3. Run a `Preview "1"` build and read the manifest: check file counts and sizes per depot.
4. Human approves the upload. Run the command. Steam updates steamcmd, logs in, chunks and uploads, and assigns a BuildID.
5. Verify: opt a test account into the branch (Steam client, game properties, Betas) and run the smoke test.
Branch plan: `staging` (QA and human approval), `beta` (optional public test, password protected), `default` (customers), `previous` (last known good for rollback). Branch names and passwords are set in Steamworks, Builds.

## 8. Setting a build live
1. Uploading does not change what customers receive until a build is set live on the default branch.
2. A scripted `SetLive` can target non-default branches only. Setting the default branch live is done by a human in the App Admin panel (Builds page) after the smoke test passes.
3. For a released app, setting a build live requires confirmation via a phone number or the Steam Mobile App. After security changes to the account (email or phone), there is a 3-day wait before a build can be set live for a released app.
4. Rollback: set the previous build id live again on the default branch; keep its id in the release report.
5. Review: first release and major changes go through Valve's build review; leave 1 to 5 days.

## 9. Steam Deck and Steam Machine compatibility
Source: https://partner.steamgames.com/doc/steamdeck/compat
Ratings: Verified, Playable, Unsupported, Unknown. They affect presentation, not whether the game can be bought or run.
Verified requirements:
| Area | Requirement |
|---|---|
| Input | Full controller support with the default configuration; glyphs match the active device (Steam Input handles it); on-screen keyboard for text entry |
| Performance | Default settings reach a playable frame rate: 30 fps at 800p on Deck (1080p on Steam Machine) |
| Seamlessness | No warnings that the device is unsupported; launchers must be controller navigable (avoid launchers) |
| Proton | Windows games run through Proton; blocking Proton bugs mean Unsupported |
| Display (Deck) | Text legible at 30 cm; smallest font at least 9 px tall at 1280x800 |
A game Verified on Deck is guaranteed Verified on Steam Machine. Request the review from the Technical Tools section on the app page if offered (not available to all partners yet); the game must have passed standard build review first. Re-review by support ticket after updating.
Test plan: run a native Linux build or Proton build on a Deck or Linux PC; first-launch with no keyboard; test text entry; read the smallest text at 1280x800; run 30 minutes; sleep and resume; remove the network and relaunch.

## 10. Achievements, cloud saves and Steam Input through engine bindings
Bindings (verify the current repository and release for your engine version):
| Engine | Binding | Notes |
|---|---|---|
| Godot | GodotSteam (GDExtension or custom build) | Download the Steamworks SDK yourself; do not commit it |
| Unity | Steamworks.NET | Also a Unity-oriented package that wraps it |
| Unity, .NET, Godot C# | Facepunch.Steamworks | C# wrapper with a simpler API |
Common steps:
1. Steamworks SDK is redistributable only as Valve licenses; keep it out of public repositories unless the licence allows.
2. For development, a `steam_appid.txt` next to the executable (or the test App ID 480 for experiments) lets the game run outside Steam; remove `steam_appid.txt` from release builds (the Steam client supplies the id).
3. Initialise the Steam API at start; if it fails when launched outside Steam, run in offline mode or exit with a clear message according to your DRM policy.
4. Call the binding's callbacks pump every frame (Godot: GodotSteam run-callbacks function; Unity Steamworks.NET: `SteamAPI.RunCallbacks()`).

Achievements:
1. Define achievements in Steamworks (id, name, description, icon). Publish the changes.
2. In code: set an achievement by its API name, then store stats. Test with a clean account; use reset stats only in development builds.
3. Cap at a sane count; avoid missable-only achievements without a hint; hidden achievements only for spoilers.
Cloud saves (https://partner.steamgames.com/doc/features/cloud):
1. Choose Auto-Cloud (no code; define root path, subdirectory, pattern in Steamworks) or the Steam Cloud API (code, finer control).
2. Set byte quota and file count per user; publish. Use Cross-Platform OS setting even for a single-platform game.
3. Keep save files small; do not sync video settings or machine-specific data; use per-user paths.
4. Test: save on machine A, launch on machine B, resolve a conflict, check `cloud_log.txt` in the Steam logs folder.
Steam Input (https://partner.steamgames.com/doc/features/steam_input):
1. Use the ISteamInput API with an in-game actions file (actions, action sets, layers) instead of reading raw gamepad buttons, so Steam can remap and supply correct glyphs.
2. Upload the in-game actions file to Steamworks and set controller support level (full, partial, none) honestly.
3. Alternative: use the engine's gamepad API and declare "partial" or "full" support if it works on every controller; Verified for Deck needs correct glyphs and a default layout that works with no setup.

## 11. Pricing and regional pricing
Source: https://partner.steamgames.com/doc/store/pricing
- Steam supports 37 currencies across 4 region groups. Conversion tools: exchange rate only, purchasing power only, or multi-variable. You can set each currency by hand. A missing currency makes the game unavailable to those who rely on it.
- Valve reviews initial prices and changes (usually 1 to 2 business days). Price changes generally wait until 30 days after release.
- Discount rules: none within 30 days of release or of the end of a launch discount (a launch discount that takes effect at release is allowed); none for 30 days after a price increase.
- Minimum base price: the multi-variable conversion of the 0.99 USD tier; lowest transaction price is 50 percent off that.
- Free-to-paid or paid-to-free switches need a support request with at least a week's notice.
- Revenue share tiers (commonly cited as 30 percent standard, falling at 10 million and 50 million USD revenue per game): unverified in this session; read the Steam Distribution Agreement.
Recipe: set the base USD price; apply the multi-variable tool; inspect Brazil, Turkey, Argentina, India, China, Russia/CIS (if allowed), Eurozone, UK, Japan, Australia; override odd rounding; get the human to approve before submitting.

## 12. Release-day checklist
T minus 14 days:
1. Store page public at least two weeks (hard minimum).
2. Release build set on the `staging` branch, passed the install smoke test on Windows, macOS, Linux and Deck.
3. Build review passed; achievements and cloud published; price approved.
T minus 1 day:
4. Press keys and influencer keys distributed (human sends; see `marketing-ua`).
5. Launch discount set to start with the release (allowed).
6. Community announcement and social posts drafted (human posts).
7. Support and bug triage rota for 48 hours.
Release day:
8. Human sets the build live on the default branch and presses the release button.
9. Install from the store on a clean machine; first launch, save, cloud sync, achievement.
10. Watch: crash reports, review tone, forum, refund rate, wishlist-to-sale conversion.
11. Hotfix path: fix, upload to `staging`, smoke test, human promotes. Keep the previous build id ready.
After: patch notes within the first week; read reviews and tag themes; plan the first discount no sooner than the 30-day lockout allows.
