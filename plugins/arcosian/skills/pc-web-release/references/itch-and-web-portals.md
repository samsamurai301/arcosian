# itch.io, Web Portals and Web Hosting

This file covers releasing on itch.io (butler, channels, HTML5 settings, pricing), web game portals (Poki, CrazyGames and others), hosting your own web build (compression headers, cross-origin isolation, caching), and the Godot and Unity web export choices that decide what hosts will work. Official itch.io pages blocked automated fetches in this session, so itch.io details come from search summaries of the official docs and are marked "verify". Every `butler push` and every portal submission is approved by a human.

## Contents
1. itch.io: account, project page and pricing
2. butler: install, login, push, channels, versions
3. itch.io HTML5 settings
4. Web portals: what they want
5. Poki
6. CrazyGames
7. Newgrounds, GameDistribution and others
8. Hosting your own web build
9. Godot web export
10. Unity Web/WebGL
11. Web release checklist

## 1. itch.io: account, project page and pricing
1. Create an account and a project (human). The project URL is `<user>.itch.io/<game-slug>`; the slug is used by butler.
2. Kind of project: Downloadable (Windows, Linux, macOS, Android files) or HTML (playable in the browser). A page can hold both.
3. Pricing options: free, paid (minimum price), pay-what-you-want with a suggested price, or "no payments" with a donation option. A free demo plus a paid full game is a common pattern.
4. Revenue share: itch.io lets the seller choose the percentage that goes to itch.io, from 0 to 100; the default is 10 percent. Payment processor fees are separate (generally about 30 cents plus 2.9 percent in the official example). Source: https://itch.io/docs/creators/payments (verify).
5. Page content: cover image, screenshots, a GIF, a short description, tags, genre, platforms, an accessibility note, a devlog. Keep the first 100 characters of the description as the hook.
6. Visibility: set the page to Draft, Restricted (password or access list) or Public. Use Restricted for testers and press.
7. Add the game to an itch.io Steam page link and wishlist button once the Steam page exists.
8. Dev log posts and updates feed the followers; one post per milestone.

## 2. butler: install, login, push, channels, versions
Source: https://itch.io/docs/butler/pushing (summarised from search results; verify with `butler push --help`).
1. Install butler from itch.io (human downloads; verify the checksum or signature from the official page). Do not install it with a package of unknown origin.
2. Login: run `butler login` once (human, interactive; it stores credentials locally). For CI, use the API-key environment variable butler documents; store the key in the CI secret store, never in the repo.
3. Push syntax:
```
butler push <directory-or-zip> <user>/<game>:<channel>
butler push build/windows myuser/mygame:windows
butler push build/linux myuser/mygame:linux --userversion 1.2.0
```
4. Channels: a channel is an upload slot; names such as `windows`, `linux`, `osx`, `html5`, `windows-beta`, `soundtrack` are conventions, and the name sets the initial tags (the platform tag comes from words in the name). Each channel has its own build history.
5. Versions: by default itch.io assigns an auto-incrementing number per channel. `--userversion 1.2.0` sets your own string; `--userversion-file <file>` reads it from a file.
6. Updates: push to the same channel name for each update, so players on the itch app get a patch (butler uploads only the diff).
7. Status: `butler status <user>/<game>` lists channels and builds (verify the command in `butler --help`).
8. A recipe, human approved:
   1. Build to `build/<platform>`; run the smoke test.
   2. Write the exact commands to the release report; show them to the human.
   3. Human approves; run the pushes; wait for itch.io processing.
   4. Open the page in Restricted mode; download or play each channel; then human switches the page to Public if it was a draft.
9. Use separate channels for beta builds (`windows-beta`) so the main channel stays stable; hide or restrict the beta upload in the page's upload settings.
10. Do not push a build folder that contains secrets, `.env` files, editor caches or debug symbols. List the folder first: `ls -R build/<platform>` and have it reviewed.

## 3. itch.io HTML5 settings
Source: https://itch.io/docs/creators/html5 (blocked; limits taken from forum posts quoting the docs and marked "verify").
1. Upload a zip (or push the folder with butler to an `html5` channel) with `index.html` at the root; tick "This file will be played in the browser".
2. Limits quoted by itch.io staff in forum posts: up to about 1,000 files after extraction, total extracted size up to about 500 MB, and no single file above about 200 MB. Verify before relying on these numbers; older posts show lower limits.
3. Embed options: set viewport size (fixed or "automatic" if the engine supports resize), enable the fullscreen button, mobile-friendly option, and "click to launch in fullscreen" for mobile.
4. SharedArrayBuffer: for multithreaded engine builds, tick "SharedArrayBuffer support" under Embed options, Frame options (an experimental opt-in). The announcement notes that local-storage saves made before enabling it become inaccessible because the embed domain changes. Treat this as a one-way decision once players have saves: decide before launch. Verify the option still exists and whether it is still labelled experimental.
5. Use a single-threaded export when possible; it avoids the option entirely and works on portals too.
6. Compression: itch.io does not compress for you in the Godot docs' description; ship a build that works without server-side Content-Encoding or precompress per the engine's guidance (see sections 9 and 10).
7. Test the zip locally in a clean browser profile and a private window before upload.
8. Saves: localStorage and IndexedDB are per-origin; a new embed domain loses them. Do not change embed settings after launch without a migration plan.

## 4. Web portals: what they want
Portal model: the portal hosts your build inside its own page and monetises with ads; you integrate its SDK, which handles ad breaks, gameplay events and sometimes saves and user accounts. You earn a share of ad revenue (or a one-off licence fee). In return you give up branding, external links, your own ads and in-app purchases.
| Requirement | Typical portal rule |
|---|---|
| Load | Small initial download, playable in seconds, no external requests |
| Controls | Mouse, keyboard and touch; desktop and mobile if listed |
| SDK | Mandatory events (gameplay start and stop) and ad calls |
| Ads | Only the portal's ads; mute audio during ads; rewarded ads optional but strict about UI |
| Monetisation | No IAP in some portals; no outgoing links |
| Quality | Human review; "fit" tests with real players before wide release |
Decision: use portals for casual, short-session, instant-play games. A premium narrative game rarely fits.
Process: build a portal-specific export; test with the portal's debug or QA tool; submit through the developer portal (human); iterate on review feedback; plan 2 to 6 weeks (estimate) for the review funnel.

## 5. Poki
Sources: https://developers.poki.com/guide/requirements-quality and https://sdk.poki.com (official).
Official requirements (read Oct 2026):
1. Keep the download small; Poki states that players tend to leave if loading takes more than 10 seconds. A third-party guide states an 8 MB initial limit; this is not on the official page I read: unverified.
2. SDK events: `gameplayStart()` on the player's first input, not on load; `gameplayStop()` on any interruption (pause, menu, level end, cutscene); never twice in a row; none during midroll or rewarded ads.
3. Ads: use `commercialBreak()` and `rewardedBreak()`; mute audio during ads; no own ad timers (Poki controls frequency); one video per reward; always offer a standard continue button at least as large as the reward button; rewarded buttons must not be green and must show a clear video icon; no rewards when an ad blocker is detected.
4. Display: 16:9, scale to cover the canvas (reference sizes 640x360, 836x470, 1031x580); prevent the game scrolling the parent page.
5. Devices: desktop, mobile and tablet; mobile fills the screen; wrap localStorage in try/catch so private mode works.
6. Must not contain: external requests (unless allowed), branding or splash screens, outgoing links (use `PokiSDK.openExternalLink('URL')`), third-party ad systems, IAP or currency purchase UI, development tools or debug code.
7. Revenue: for exclusive deals the developer keeps 100 percent from players who find the game on their own and 50 percent from players Poki brings; non-exclusive licences with a one-off fee exist (https://sdk.poki.com/deals; verify).
8. Review funnel (third-party description, unverified): player-fit test, then a web-fit test, then final review.

## 6. CrazyGames
Source: https://docs.crazygames.com/requirements/technical (official).
1. Size: total at most 250 MB and 1,500 files; initial download at most 50 MB, or 20 MB to be eligible for the mobile homepage. With the SDK, initial size is measured until the first `Gameplay start` event; without it, total size. Externally hosted files are judged by time to gameplay (20 seconds or less).
2. Use relative paths only.
3. Browsers: Chrome and Edge; Safari failures disable the game on Safari; Chromebook target 4 GB RAM. Mouse and keyboard, plus touch if the game supports mobile.
4. Mobile: add `user-select: none` to the body; the site handles rotation prompts; Unity games are disabled on iOS by default because of memory crashes; handle safe areas; iOS AudioContext must be resumed inside a user gesture.
5. SDK: Basic launch (limited audience, about two weeks, ads disabled) needs the basic implementation; Full launch needs the full SDK events (gameplay start and stop, data and user modules where applicable) and starts the revenue share.
6. Revenue share percentage: not stated in the docs read; third-party figures conflict: unverified. Ask in the developer portal.
7. If the game collects personal data beyond SDK events, show a privacy notice, preferably non-blocking.

## 7. Newgrounds, GameDistribution and others
These were not verified from official pages in this session; treat every number as unverified and read the official docs first.
| Portal | What is known (unverified) | Check at |
|---|---|---|
| Newgrounds | Open upload of HTML5 and Flash-style games, community voting, optional Newgrounds.io API (medals, leaderboards, cloud saves); a forum post mentions a 250 MB limit | newgrounds.com and its wiki |
| GameDistribution | Publisher SDK and ads for distribution to partner sites; revenue share terms not found | gamedistribution.com developer pages |
| itch.io | See sections 1 to 3 | itch.io |
Others (Kongregate, Armor Games, Y8 and similar) change frequently; verify that they still accept submissions before investing in an SDK integration.
Rule: integrate one portal SDK behind an engine-side adapter, so switching or adding portals is a config change, not a rewrite (see `game-architecture`).

## 8. Hosting your own web build
1. Choose static hosting (any CDN, object storage with a CDN, a static site host). The game is static files: `index.html`, JS loader, `.wasm`, `.pck` or `.data`, audio.
2. Always HTTPS; some browser features (SharedArrayBuffer, service workers) require a secure context (localhost excepted).
3. Content types: `.wasm` as `application/wasm` (streaming compile needs it); `.js` as `application/javascript`; Godot's `.pck` as `application/octet-stream`.
4. Compression, two choices:
   - Server compresses on the fly (gzip or Brotli) for text, `.js`, `.wasm`, `.pck` or `.data`. Most CDNs do this for known MIME types; check that `application/wasm` and `application/octet-stream` are on the list.
   - Precompressed files (`.br`, `.gz`) served with `Content-Encoding: br` or `gzip` and the original `Content-Type`. Unity's compressed builds need exactly this; a wrong or missing header leaves the browser with an unreadable file.
5. Check: `curl -sI -H "Accept-Encoding: br, gzip" https://example.com/game/Build/game.wasm` and read `content-type`, `content-encoding` and `content-length`.
6. Cross-origin isolation for threads (Godot with thread support, some Unity setups): send on the HTML and the loader responses
   `Cross-Origin-Opener-Policy: same-origin` and `Cross-Origin-Embedder-Policy: require-corp`.
   Consequences: every cross-origin subresource (fonts, ads, analytics, iframes) must opt in with CORS or `Cross-Origin-Resource-Policy`, which breaks most third-party ad scripts. So threaded builds and ad-funded portals do not mix.
   If you cannot set headers, Godot's Progressive Web App option installs a service worker that adds them (see section 9); first load may need a reload.
7. Caching: filenames with content hashes or a version query; `Cache-Control: public, max-age=31536000, immutable` for hashed files; `Cache-Control: no-cache` (revalidate) for `index.html` so players get new builds. Unversioned `.pck` with a year-long cache is a classic stale-build bug.
8. Headers for security: `X-Content-Type-Options: nosniff`; a Content-Security-Policy that allows `wasm-unsafe-eval` if you use a CSP.
9. Embedding in an iframe on another site: add `allow="fullscreen; gamepad"` (and `cross-origin-isolated` if needed) to the iframe, and permit framing only from domains you choose.
10. Analytics and crash reporting must follow `legal-ethics` consent rules; in the EU show consent before non-essential tracking.
11. Rollout: deploy to a staging path, test with `curl -I`, then switch the production pointer (human approval).

## 9. Godot web export
Source: https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_web.html
1. Export needs WebAssembly and WebGL 2.0; only the Compatibility renderer works on the web.
2. Since Godot 4.3 the default export is single-threaded: no special headers, works on itch.io, Poki and CrazyGames. A multi-threaded export (Thread Support) performs better and allows low-latency stream audio but needs cross-origin isolation and rules out third-party ads or integrations on the host.
3. If you must use threads and cannot set headers, enable Progressive Web App, Enable (the service worker simulates the headers). Without headers or this workaround a threaded project will not run.
4. GDExtension on web also needs the isolation headers and extensions compiled for web.
5. `.wasm` compresses to roughly a quarter with gzip; serve `.pck` and `.wasm` compressed. GitHub Pages compresses on the fly; itch.io is described as not doing so in Godot's docs (verify). A custom export template with unused modules removed shrinks the wasm.
6. Safari has WebGL 2.0 quirks; test Safari separately. Audio autoplay is blocked until first input: show a click-to-start screen.
7. Default Sample audio mode lacks some effects; Stream mode has them at the cost of latency.
8. Export from the command line for CI (headless): `godot --headless --export-release "Web" build/web/index.html` (the preset must exist in `export_presets.cfg`); then zip and review.
9. Decision: single-threaded for portals and itch.io; threads only on your own host with isolation and no third-party ad scripts.

## 10. Unity Web/WebGL
Source: https://docs.unity3d.com/Manual/webgl-deploying.html
1. Compression format (Project Settings, Player, Web, Publishing Settings): gzip (default; works everywhere over HTTP and HTTPS), Brotli (smaller, slower to build, supported natively by Chrome and Firefox only over HTTPS) or Disabled (you or the host compress). Compression applies to release builds only.
2. Server header must match: `.gz` files need `Content-Encoding: gzip`; `.br` files need `Content-Encoding: br`; `.wasm` needs `Content-Type: application/wasm`; JS needs `application/javascript`.
3. Decompression Fallback embeds a JavaScript decompressor for hosts you cannot configure; it adds a `.unityweb` extension, increases loader size and load time, and disables WebAssembly streaming. Use it for itch.io-style hosts that cannot set Content-Encoding, accepting the cost.
4. Portals: CrazyGames disables Unity games on iOS by default (memory); Poki has Unity optimisation guidelines. Keep memory low, avoid large textures, use Addressables or streamed assets for progressive load.
5. Unity does not support threads in the browser by default; follow the current manual before enabling anything experimental.
6. Test: build, serve locally with a server that sets the headers (not by opening `index.html` from disk), run in Chrome, Firefox and Safari.

## 11. Web release checklist
1. Target chosen (portal, itch.io, own host) and its rules saved in the project notes.
2. Export settings per section 9 or 10; initial download measured on a throttled connection (10 seconds to first interaction on a mid-tier phone is a good target; estimate).
3. Input: mouse, touch, keyboard; audio unlock on first input; pause on tab hidden.
4. Storage wrapped in try/catch; save format versioned.
5. Mobile browsers tested on one iPhone and one mid-tier Android.
6. No debug code, no console spam, no external requests (portals).
7. Headers checked with `curl -I` (own host).
8. Human approves the upload or submission; deploy to staging first; verify; then production.
9. Record the URL, build id, date and headers snapshot in the release report.
