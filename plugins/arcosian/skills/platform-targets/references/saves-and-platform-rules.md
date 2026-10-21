# Saves and platform rules

This reference says where saves and settings go on each OS and engine, how the web stores data and loses it, how cloud saves work (Steam Cloud, iCloud, Google Play Games, and consoles at a public level), how to version saves, what Steam Deck Verified checks, which platform rules shape design, and how to handle localisation and font coverage. Store and programme mechanics are not repeated: see `pc-web-release`, `store-release` and `console-pathway`.

## Contents

1. Save and config locations
2. Web storage: IndexedDB, quota and eviction
3. Cloud saves
4. Save design: atomic writes, slots, corruption
5. Save versioning and migration
6. Steam Deck compatibility criteria
7. Platform rules that shape design
8. Localisation and font coverage
9. Checklist

## 1. Save and config locations

Separate three kinds of data:

| Kind | Content | Sync to cloud? | Location rule |
|---|---|---|---|
| Save data | Progress, inventory, unlocks, profile | Yes | Per user, in the user data folder |
| Settings | Resolution, graphics, audio, keybinds | No for machine-specific (video); yes only for portable ones (language, accessibility) if at all | Per user, user config folder |
| Cache and logs | Shader caches, downloaded content, logs, crash dumps | No | Cache or temp folder; safe to delete |

Valve's Steam Cloud guidance advises against syncing machine-specific settings such as video settings (source: https://partner.steamgames.com/doc/features/cloud), so keep `settings.cfg` and `profile.sav` separate.

### Engine paths

| Engine | API | Resolves to |
|---|---|---|
| Godot 4 | `user://` | Windows `%APPDATA%\Godot\app_userdata\[project_name]`; macOS `~/Library/Application Support/Godot/app_userdata/[project_name]`; Linux `~/.local/share/godot/app_userdata/[project_name]`; web: a virtual filesystem stored in the browser (IndexedDB); Android and iOS: a folder private to the app (source: https://docs.godotengine.org/en/stable/tutorials/io/data_paths.html) |
| Godot custom user dir | Project setting `application/config/use_custom_user_dir` with a custom name | Windows `%APPDATA%\[name]`; use it so the folder carries your game's name instead of "Godot/app_userdata" |
| Unity | `Application.persistentDataPath` | Per platform, a folder in the user's data area, with company and product name from Player Settings; on Windows under `AppData\LocalLow\<company>\<product>`, on macOS under `~/Library/Application Support/<company>/<product>`, on Linux under `~/.config/unity3d/<company>/<product>`; on Android the app's external or internal files folder; on iOS the app Documents-adjacent folder (verify exact paths for your Unity version) |
| Unity | `PlayerPrefs` | Registry on Windows, plist on macOS, small key-value; suitable only for tiny settings, not saves |
| Unreal | `FPaths::ProjectSavedDir()` and the SaveGame system | Under the user's local app data on Windows; per-platform equivalents (verify for your version) |
| Native or custom | Platform APIs | See below |

### Native conventions per OS

| OS | Save and config convention |
|---|---|
| Windows | `%APPDATA%` (Roaming) for portable settings, `%LOCALAPPDATA%` for machine-bound data and caches, and the Saved Games folder (`%USERPROFILE%\Saved Games`) for saves in the Windows convention. Do not write into the install directory (Program Files is read-only for standard users). Steam Auto-Cloud has a `WinSavedGames` root and `WinAppDataRoaming` and other roots (source: Steam Cloud page above). |
| macOS | `~/Library/Application Support/<bundle or game name>` for saves and configs; `~/Library/Caches/<id>` for caches; `~/Library/Preferences` for plist preferences. Sandboxed apps get a container path. Steam Auto-Cloud root `MacAppSupport`. |
| Linux | XDG base directories: `$XDG_DATA_HOME` (default `~/.local/share/<game>`) for saves, `$XDG_CONFIG_HOME` (default `~/.config/<game>`) for config, `$XDG_CACHE_HOME` (default `~/.cache/<game>`) for caches. Steam Auto-Cloud root `LinuxXdgDataHome`. Under Proton on Steam Deck, Windows paths live inside a per-game Wine prefix (`compatdata/<appid>/pfx`), so Windows-style paths still work but sit in a different place; Steam Cloud handles that when set up with Windows roots. |
| iOS | App sandbox: Documents (backed up, user-visible via Files if enabled), Library/Application Support (backed up, hidden), Library/Caches (not backed up, purgeable), tmp. Saves go in Application Support or Documents. Mark large re-downloadable files as excluded from backup. |
| Android | Internal app-private storage (`filesDir`), external app-specific storage, and cache; scoped storage means no free access to shared folders; backup via Auto Backup (rules in the manifest) and Play Games saved games. Uninstall removes app-private data. |
| Web | Browser storage per origin (section 2). |
| Switch, PlayStation, Xbox | Platform save data APIs with platform-managed storage and sizes; the SDKs define it. No raw filesystem path (`console-pathway`). |

### Rules

1. Never write saves to the install folder or the working directory.
2. Use the engine API (`user://`, `persistentDataPath`) unless you need a specific root for cloud sync (Steam Auto-Cloud roots are chosen to match where the engine writes; check the actual path after a build).
3. Use the game's name in the folder, not "Godot" or "unity3d" defaults, because players and support look for it (set Godot's custom user dir; set Unity's company and product name).
4. Write text or well-documented formats (JSON with a version field, or a binary container with a header). Text helps support and mod-friendly games; binary helps size and tamper resistance (anti-cheat is a different matter).
5. Handle path length, Unicode user names and spaces on Windows (a user name with accented characters broke many games).
6. Handle read-only and full disks: catch write errors, show a message, never delete the previous good save before the new one is confirmed (section 4).
7. Do not store secrets or tokens in plain saves; use the OS credential store for tokens.
8. Handle multiple OS users, and on consoles and Steam, multiple profiles: scope saves per user.

## 2. Web storage: IndexedDB, quota and eviction

Source: MDN storage quotas and eviction criteria (https://developer.mozilla.org/en-US/docs/Web/API/Storage_API/Storage_quotas_and_eviction_criteria), checked Oct 2026.

| Storage | Limit | Use |
|---|---|---|
| `localStorage`, `sessionStorage` | About 5 MiB per origin each, up to 10 MiB max across browsers | Tiny settings only; synchronous, blocks the main thread |
| IndexedDB | Per-browser quota (below) | Saves, cache of assets; the default for engines (Godot's `user://` on web) |
| Cache API | Same quota pool | Service worker cached files |
| Origin Private File System | Same quota pool | Files for wasm engines; check engine support |
| Cookies | Small | Do not use for saves |

Per-origin quotas (best effort, unless persistent):

| Browser | Limit |
|---|---|
| Chrome and Chromium browsers | Up to 60 percent of total disk |
| Firefox | Smaller of 10 percent of disk or a 10 GiB group limit shared by origins of the same site; persistent origins up to 50 percent of disk |
| Safari (macOS 14 and iOS 17 and later) | About 60 percent for browser apps; about 15 percent for embedded web views |

Quotas derive from total disk size, not free space, so you may not be able to reach the stated quota.

### Eviction risks

1. **Storage pressure**: the browser deletes the least recently used best-effort origins first when the device is low on space. All data for the origin goes at once.
2. **User actions**: clearing site data, "clear history", private browsing (usually deleted at the end of the session), uninstalling a browser.
3. **Safari proactive deletion**: with cross-site tracking prevention, an origin without user interaction for seven days can have its script-created data deleted. A game opened less than weekly in Safari, including iOS, can lose saves. Installing as a home screen web app changes this; verify current behaviour.
4. **Embedding**: a game in an iframe on a portal is a different origin from your own site, and storage may be partitioned (third-party storage partitioning), so a player's save on the portal copy may not appear in your own site's copy. Portals may offer their own cloud save API (`pc-web-release`).
5. **Different browser or device**: no sync at all.

### What to do

- Call `navigator.storage.persist()` after the player has played and shown intent. Firefox prompts; Safari and Chromium decide automatically from engagement; check the result with `navigator.storage.persisted()`.
- Check `navigator.storage.estimate()` for usage and quota; warn below a threshold.
- Catch `QuotaExceededError` on writes and show a message.
- Provide **export and import** of saves (a downloadable file or a copy-paste code) and tell the player where progress lives. Offer account-based cloud save when you have a backend (`multiplayer-backend`).
- Write small, frequent, atomic transactions; IndexedDB transactions are atomic per transaction; commit complete save objects, not partial.
- Autosave on `visibilitychange` to hidden and on the pagehide event (they fire on mobile browsers when the tab is backgrounded); `beforeunload` is unreliable on mobile.
- Test: clear site data, run in private mode, run in Safari with the seven-day rule in mind, fill the quota.
- Engine notes: Godot web persists `user://` to IndexedDB after file writes; call `JavaScriptBridge` or let the engine sync, and test that a reload restores the data (the sync is asynchronous, so a close right after saving can lose it). Unity WebGL `persistentDataPath` maps to an IndexedDB-backed filesystem; call the sync function (`FS.syncfs` through a JS plugin) after saves; verify for your version.

## 3. Cloud saves

### Steam Cloud

Source: https://partner.steamgames.com/doc/features/cloud (checked Oct 2026).

- Two options: the **Cloud API** (`ISteamRemoteStorage`) for direct control, and **Auto-Cloud**, which needs no code and syncs file groups defined in the Steamworks settings at launch and exit.
- Auto-Cloud root paths: a predefined root (App Install Directory, SteamCloudDocuments, WinSavedGames, MacAppSupport, LinuxXdgDataHome and others), a subdirectory (supports `{64BitSteamID}` and `{Steam3AccountID}` placeholders), a file pattern with `*` wildcards, an OS restriction (default Cross-Platform, strongly recommended even for single-OS games) and a recursive flag. Root overrides map a root to a different location on another OS.
- Developer-set quotas: bytes per user and files per user, on the Steam Cloud settings page. Each single write call is limited to 100 MB; files above 256 MB may get a slower storage endpoint.
- Practices from the page: keep files small and split by change frequency so unchanged data is not re-uploaded; use unique save paths per Steam user; keep machine-specific settings out of the cloud; test with developer-only mode before enabling for everyone; debug with the Steam cloud log (`logs/cloud_log.txt` in the Steam install folder) and allow time for changes to propagate.
- Design for **conflicts**: Steam asks the player which save to keep when it detects a conflict (the local file and the cloud file diverged), but only if your files carry enough information to tell them apart. Include a save timestamp, play time and a monotonically increasing save counter in the save header, and show those in your own slot UI.
- Steam Deck Verified expects the game to work well with Steam Cloud in practice because Deck players move between devices; also set it up for Linux and Windows roots.

### iCloud (Apple platforms)

- Options: CloudKit (record-based, private database per user), iCloud Key-Value Store (small, about 1 MB total, for settings), and iCloud Drive document storage. Games often use CloudKit or Game Center saved games (Game Center is the identity and has a saved game API; verify current API names).
- Needs an Apple Developer account and entitlements (`store-release`); the player must be signed into iCloud and may disable it, so the game must work without it.
- Conflicts: handle by timestamp or by letting the player choose. Never merge silently without a rule.
- Engines: Unity and Godot need native plugins or a small Swift or Objective-C bridge. Check plugin maintenance before relying on one.
- Privacy: declare data use in store forms (`store-release`, `legal-ethics`).

### Google Play Games (Android)

- Play Games Services offers **Saved Games** (a snapshot API with a conflict-resolution callback) tied to the player's Google Play Games profile. The service and API versions have changed over time (the older Saved Games API is being moved to newer Play Games Services v2 flows; verify the current status in the Android developer documentation before building).
- Alternative: Android Auto Backup of app data (simple, uses the user's Google backup, restores on reinstall and device change, not real-time, limited size per app; verify limits).
- Alternative: your own account backend (`multiplayer-backend`) for cross-platform progress between iOS and Android, which neither platform service provides.

### Consoles (public level)

- Each console has a platform save data API managed by the OS; saves follow the user account and the title, with platform cloud backup through the platform subscription in some cases (for example a first-party online subscription may enable cloud saves on some consoles; terms vary and change; verify).
- Rules shown in public documentation and developer talks: size limits per title, no raw file paths, save on suspend, avoid saving at times that risk corruption (the platform may warn the player not to switch off), clear "saving" indicator, handle full storage and user switching. Specifics are under NDA in the programme (`console-pathway`).
- Cross-save between platforms (a console and PC) needs your own account system and sometimes platform approval.

### Cross-platform progression (any platforms)

| Need | Approach |
|---|---|
| Same player on iOS and Android | Own account (email, Apple, Google sign-in) plus a backend save blob (`multiplayer-backend`) |
| Same player on PC and mobile | Same; Steam Cloud alone cannot reach phones |
| Same player on consoles | Platform account linking and platform approval required |
| Offline-first game | Local save is the truth; cloud is a backup; resolve conflicts by last-write or a player prompt |

Rules for every cloud system:

1. The game must fully work offline and when cloud sync is disabled.
2. Never sync settings that depend on the machine.
3. Conflicts: compare a save counter and timestamp; offer "keep local" or "keep cloud" showing playtime, progress and date.
4. Upload after meaningful events (checkpoint, level end, exit), not each frame.
5. Do not delete the cloud copy when the local save is deleted without a confirmation that says so.
6. Respect privacy and age rules for children's data (`legal-ethics`).

## 4. Save design: atomic writes, slots, corruption

1. **Atomic write**: write to `save.tmp`, flush, rename over `save.dat` (rename is atomic on the same volume). Keep `save.bak` as the previous good file. On load: try `save.dat`; on failure, try `save.bak`; if that fails, show a recovery message.
2. **Checksum or hash** in the header to detect truncation. Use a plain CRC32 or SHA-256 of the payload; this is not security.
3. **Slots**: for games with branching or replay, provide multiple slots plus an autosave slot. Show playtime, location and date. For short mobile games a single auto-managed save is enough.
4. **Autosave**: at checkpoints, on pause and on background (mobile), and after major transactions (purchases). Show a small non-blocking indicator. Do not autosave in the middle of a scripted sequence that cannot resume.
5. **Size**: keep saves small (tens of KB to a few MB). Large saves slow cloud sync and web storage.
6. **Determinism**: store the minimum (state, seed, inputs) not derived data, so versions can regenerate derived data.
7. **Threading**: serialise on the main thread, write on a worker, so the frame does not hitch. On consoles, follow platform guidance.
8. **Security**: assume saves can be edited. Do not trust them in competitive or paid-currency contexts; validate on a server (`multiplayer-backend`, `economy-design`).
9. **IAP and entitlements** live with the store receipts and server, not only in the save (`monetization`, `store-release`).
10. **Corruption testing**: kill the process mid-save, fill the disk, delete half the file, write a save from a newer version; the game must not crash and must not lose the last good state.

## 5. Save versioning and migration

Every save has a header:

```json
{ "format": "mygame.save", "version": 7, "build": "1.4.2", "saved_at": "2026-10-18T12:00:00Z", "counter": 1342, "playtime_s": 40213, "payload": { } }
```

Rules:

1. **Integer schema version**, incremented on any change to the payload shape. Keep it separate from the app version.
2. **Migrations are a chain**: `migrate_1_to_2`, `migrate_2_to_3`, and so on. Load runs all steps from the file's version to current. Never skip a version.
3. **Forward compatibility**: if the file's version is newer than the game knows (player downgraded or shared a save), refuse to load with a clear message and keep the file untouched. Do not try to partly read it.
4. **Defaults for new fields**: loading an older save fills new fields with defaults, never nulls.
5. **Unknown fields**: preserve them when re-saving if you support mixed versions across devices (cloud play between a patched and unpatched device).
6. **Back up before migrating**: copy the old file to `save.v6.bak` before writing the migrated file.
7. **Test with fixtures**: keep a save from every released version in the repo (`tests/saves/v1.json` ... ) and run a unit test that loads each and checks key invariants. Add a fixture each release (`qa-testing`).
8. **Economy-safe migrations**: if currencies or balance change, migrations must not create or destroy value players paid for (`economy-design`, `liveops`).
9. **Settings** follow the same rule but are less critical; on failure reset to defaults.
10. **Cloud**: the version header decides whether another device's save can be loaded.

Pseudo-code:

```
load(path):
    data = read_json(path)
    if data.version > CURRENT: error("newer save")
    backup(path, "v" + data.version)
    while data.version < CURRENT:
        data = MIGRATIONS[data.version](data)
        data.version += 1
    validate(data)
    return data
```

## 6. Steam Deck compatibility criteria

Source: Steam Deck Verified requirements, https://partner.steamgames.com/doc/steamdeck/compat (checked Oct 2026). Valve's review is the only way to get a Verified badge; the process and submission are covered by `pc-web-release`. This is what to build for.

| Category | Requirement (paraphrased) |
|---|---|
| Input: controller support | The game supports the Deck's physical controls and the default configuration gives access to all content without changing in-game settings |
| Input: glyphs | On-screen button glyphs match the active input (Deck, Steam Controller or Xbox) and mouse or keyboard glyphs do not show when they are not active; Valve recommends the Steam Input API |
| Input: text entry | Text entry must use the Steam on-screen keyboard through a Steamworks API, or a built-in controller-usable text entry |
| Display: resolution | Supports a resolution the Deck supports; 1280x800 (preferred) or 1280x720 |
| Display: text legibility | Text readable at 12 inches (30 cm); smallest on-screen font height at least 9 px at 1280x800, 12 px recommended |
| Seamlessness: no warnings | No warnings that the Linux distribution or hardware (such as the GPU) is unsupported |
| Seamlessness: launchers | Launchers meet the same requirements, including full controller navigation; Valve strongly recommends against requiring launcher navigation at all |
| System support: Proton | Games without native Linux builds run through Proton; blocking Proton bugs or performance problems cause Unsupported |
| Performance | Default configuration reaches a playable 30 fps at 800p on Steam Deck |

Other statuses exist (Playable, Unsupported, Unknown); the page describes the badge meanings. Valve says Verified display criteria apply to the Deck and are not tested on Steam Machine; verify the current text, since Valve has added newer hardware and updated the page.

Build checklist for Deck readiness:

1. Play the whole game with the Deck controls or a pad only; no mouse or keyboard needed, including launcher, settings, text fields, purchases, social features.
2. All text meets the 9 px minimum at 1280x800 (aim for 12 px); check inventory numbers, tooltips, subtitles, store and chat overlays.
3. Glyphs follow the active device; detect the Deck (`IsSteamRunningOnSteamDeck` or Steam Input glyph APIs; verify names in Steamworks docs).
4. Remove first-run launcher dialogs, EULA popups that need a mouse, anti-cheat warnings that say Linux is unsupported, and "your GPU is not supported" messages.
5. Default settings run at 30 fps or better at 800p; add a Deck preset.
6. Test suspend and resume, network loss, and the Steam overlay and Quick Access menu.
7. Save and cloud sync work under Proton paths.
8. Anti-cheat and DRM: some middleware blocks Linux or Proton; check vendor support early (`multiplayer-backend`, `pc-web-release`).
9. Test with the Steam Deck in Game Mode, not desktop mode.
10. Do not claim Verified until Valve's page shows it.

## 7. Platform rules that shape design

These affect design decisions early. Details and current text are owned by `store-release` (mobile stores), `pc-web-release` (Steam, itch.io, portals) and `console-pathway` (consoles). Treat this table as "things to plan for", not a requirements list.

| Rule area | Why it shapes design | Where to read |
|---|---|---|
| Payments and IAP | Mobile stores require their own billing for digital goods (with regional exceptions that change); this shapes shops, currencies and web links; Steam has its own wallet and rules; consoles use platform stores | `store-release`, `pc-web-release`, `monetization` |
| Age ratings | Content (violence, gambling-like mechanics, user content) affects ratings and where the game can sell; some regions require ratings before release; loot boxes and random-reward paid items face rules in some regions | `legal-ethics`, `console-pathway`, `store-release` |
| Privacy and consent | Tracking permission, data safety forms, children's data rules (COPPA, GDPR-K) shape analytics and ads | `legal-ethics`, `player-analytics`, `store-release` |
| Accessibility | Required or expected: Xbox publishes guidelines; the EU accessibility act affects some digital services from mid 2025 (check applicability for games); stores display accessibility features | `accessibility-localization`, section 8 of platform-ux |
| Account and sign-in | Platform account linking, Sign in with Apple when other social logins are offered on iOS (as of the rule's last known text; verify), platform requirement to use platform achievements and friends on consoles | `store-release`, `console-pathway` |
| Online play and cross-play | Consoles require platform online services and approvals for cross-play and cross-progression; matchmaking and chat need moderation and reporting | `console-pathway`, `multiplayer-backend` |
| Content and user-generated content | Moderation, reporting and blocking are expected on all stores | `legal-ethics`, `community-ops` guidance in the community adapter if installed |
| Save and suspend | Consoles and mobile require clean suspend and resume and save behaviour; no data loss on power loss | section 4, `console-pathway` |
| Performance and stability | Consoles certify frame rate stability, load times, crash rate; mobile stores penalise crashes and ANRs in ranking and sometimes visibility (verify) | `console-pathway`, `store-release`, `optimize` |
| Binary and runtime | Android 16 KB page size, target API levels, 64-bit requirement; iOS minimum SDK; Apple notarisation for macOS; code signing for Windows reduces SmartScreen warnings | `store-release`, `pc-web-release` |
| Distribution size | Store size limits and cellular warnings influence asset streaming | `store-release` |
| Branding and terminology | Consoles dictate button names, logos and wording; stores restrict mentioning other platforms in listings | `console-pathway`, `store-release` |
| Third-party SDKs | Ads, analytics and anti-cheat must support the platform; some do not run on consoles, web or Linux | `monetization`, `player-analytics` |
| Web | Portals and hosts require size limits, SDK integration (ads, saves), iframe compatibility and sometimes no external links | `pc-web-release` |
| Regional | Some regions require local legal entities, ratings or approvals (for example mainland China, South Korea), which changes release plans | `legal-ethics`, `console-pathway`, `store-release` |

Design consequences to write into the contract early:

- If you plan consoles: no raw file I/O, an event-driven suspend and resume, a pad-only UI, no "quit" item, and a plan for ratings.
- If you plan mobile with purchases: a store-compatible shop with restore purchases and parental controls where needed.
- If you plan web: no assumptions about threads or storage.
- If you plan PC multiplayer: anti-cheat, account system and moderation tools chosen before content is built.

## 8. Localisation and font coverage

Full localisation workflow, text expansion and accessibility are in `accessibility-localization`. Platform-specific points:

| Point | Detail |
|---|---|
| Language list | Choose by audience and market data (`market-intel`). Common first wave for PC: English, French, Italian, German, Spanish (Spain and Latin America), Brazilian Portuguese, Russian, Simplified Chinese, Traditional Chinese, Japanese, Korean, Polish, Turkish. Steam shows supported languages on the store page; consoles and mobile stores also have language settings and sometimes required languages for a region (verify per programme) |
| Default language | Detect from the OS locale on first run; allow a change in settings; do not tie it to the store region |
| Font coverage | Latin fonts rarely cover Cyrillic, Greek, CJK, Thai, Arabic, Hebrew or Devanagari; use a font per script or a fallback chain. Check the licence allows embedding and redistribution in games (`legal-ethics`). Noto fonts are a common fallback family under an open licence; verify the specific licence of the files you ship |
| CJK size | CJK fonts are large (several MB per font): subset them to used characters for mobile and web, or load per language on demand |
| Pixel fonts | Pixel-art fonts rarely cover CJK; plan a different treatment for those languages |
| Right-to-left | Arabic and Hebrew need text shaping, right-to-left layout and mirrored UI where appropriate; Godot 4 supports RTL and text shaping through its text server; Unity needs a package or plugin (verify); test early because late retrofits are expensive |
| Text expansion | Allow 30 to 40 percent growth over English for German and Russian; shorter for CJK but taller line height; test the longest strings at the minimum UI size |
| Numbers, dates, currency | Use locale formatting; decimal commas; 24-hour clocks; time zones for events |
| Plurals and grammar | Use a library or format that supports plural rules per language (ICU style); never concatenate strings |
| Controller prompts in text | Use placeholders resolved at run time (`references/input-and-controls.md` section 7) |
| Input methods | IME for CJK text input on PC, mobile and consoles; the on-screen keyboard supports the language; test that text fields accept IME composition |
| Voice and audio | Plan which languages get voice; subtitles for all |
| Store assets | Screenshots and descriptions per language; store pages have limits and review rules (`store-release`, `pc-web-release`) |
| Platform terms | Use each platform's own terms for buttons, menus and the store; consoles provide required terminology lists in the programme |
| Testing | A pseudo-localisation pass (accented and padded strings) catches layout and hard-coded text early; a linguistic QA pass in context catches the rest (`qa-testing`) |
| Legal | Some regions restrict content or require local text for age ratings and legal notices (`legal-ethics`) |

## 9. Checklist

- [ ] Saves, settings and caches are in separate files in the correct per-OS folders; none in the install folder.
- [ ] Folder uses the game's name; engine company and product names set.
- [ ] Atomic writes with a backup; corruption tests passed.
- [ ] Save header has a format id, integer version, counter and timestamp; migration chain and fixture saves exist.
- [ ] Newer-version saves are refused safely.
- [ ] Cloud: Steam Auto-Cloud roots, Cross-Platform setting and quotas set; iCloud and Play Games handled or deliberately skipped; own account if cross-platform.
- [ ] Machine-specific settings are not cloud-synced.
- [ ] Web: persistence requested, quota checked, export and import offered, autosave on hidden, tested in private mode and Safari.
- [ ] Steam Deck criteria checked (glyphs, text 9 px at 1280x800, controller-only, no warnings, 30 fps at 800p) before submitting to Valve.
- [ ] Platform rule table reviewed for each platform and linked to the owning skill; risks recorded in the contract.
- [ ] Localisation: fonts cover every shipped language, layout tested at the longest string, IME and RTL tested if shipped.
