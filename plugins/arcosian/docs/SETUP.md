# Setup

Every account and access the suite can use, why you would want it, and where the credential goes. Nothing here is mandatory: with no keys the studio runs on placeholders and local tools. Add accounts as the project reaches the stage that needs them. For costs the rule is simple: where this document gives no number, check vendor pricing.

## 1. Where each secret goes

| Kind | Used for | Where it goes | Never |
|---|---|---|---|
| Plugin user configuration (sensitive) | Generation keys read by `studio-gateway` | Prompted at plugin install or via the plugin config; stored as sensitive values and passed to the gateway as env vars | In `.gamestudio/`, in git, in chat |
| Adapter plugin user configuration | Keys for vendor MCP bridges (PixelLab token, Meshy key), Godot binary path | Prompted when the adapter is installed | Reused from another service |
| Adapter OAuth or login | Remote MCP servers (ElevenLabs, RevenueCat) and CLI logins (Firebase) | The server's own sign-in flow or the vendor CLI | Pasted into prompts |
| CI secrets | Signing keys, store API keys, certificate repo access | GitHub repository secrets or Codemagic groups | On the dev machine if avoidable; the hooks deny reading them |
| Human-only | Store account creation, agreements, tax and banking, final submission | The vendor's website, by you | Automated |

Core plugin keys (all optional): `gemini_api_key`, `openai_api_key`, `recraft_api_key`, `fal_key`, `tripo_api_key`, `meshy_api_key`, `elevenlabs_api_key`, `stability_api_key`, and `asset_budget_usd` (default 50, a spending cap in USD). Per-project override: `.gamestudio/config.json`.

## 2. Accounts and access, and why

### Stores and build (needed to ship)

| Account | Why | Notes |
|---|---|---|
| Apple Developer Program | TestFlight, App Store, signing, App Store Connect API | Paid yearly membership; check Apple for current fee and enrolment time. Create the app record by hand; fastlane `produce` does not work with an API key. Create a Team API key (`.p8`) for CI; individual keys cannot reach provisioning |
| Google Play Console | Internal testing, closed testing, production | One-time registration fee; check Google. New personal accounts face testing requirements before production; read the current rules in Play Console help. Create a service account for fastlane `supply` and grant release permissions |
| GitHub | Repo, Actions CI, secrets | Mac runners are needed for iOS; check GitHub pricing for minutes |
| Codemagic | Hosted macOS builds for Godot or Unity if you do not want to use GitHub macOS runners | Template: `templates/ci/codemagic/codemagic.yaml`; check vendor pricing |
| Device farms (Firebase Test Lab, BrowserStack, AWS Device Farm or similar) | Real-device perf and compatibility, low-end tier checks | Optional; a few owned low-end devices usually beat a farm for perf gates |

### Operations (needed from soft launch)

| Account | Why | Adapter |
|---|---|---|
| Firebase | Analytics, Crashlytics, Remote Config, Test Lab | `arcosian-commerce` (Firebase MCP via `firebase-tools`; log in with the Firebase CLI) |
| RevenueCat | IAP products, entitlements, offerings, experiments | `arcosian-commerce` (remote MCP, sign in via its flow) |
| AppLovin (MAX) | Ad mediation if the monetization model uses ads | No adapter; SDK integration is guided by the `monetization` skill. Check the vendor for current SDK and consent requirements |
| Attribution (Adjust or similar) | Install attribution for paid UA | Adjust's official MCP is registered by `arcosian-commerce` (`https://mcp.adjust.com/mcpo`); sign in through `/mcp`. Aggregated data only |

### Generation (optional, production quality)

| Vendor | Why | Where the key goes |
|---|---|---|
| Google AI (Gemini) | Image generation, Lyria music, Gemini TTS | Core `gemini_api_key` |
| OpenAI | GPT Image for hero art, key art, store screenshots | Core `openai_api_key` |
| Recraft | Vector icons and UI, background removal, vectorize | Core `recraft_api_key` |
| fal | Hosted open-weight image models, LoRA training, upscaling | Core `fal_key` |
| Tripo | Low-poly 3D, rigging | Core `tripo_api_key` |
| Meshy | 3D generation, remesh, rigging, animation | Core `meshy_api_key`; also `arcosian-vendors` `meshy_api_key` if you use its direct MCP |
| ElevenLabs | Music, SFX, voice design, dialogue | Core `elevenlabs_api_key`; the vendors adapter also offers a remote MCP with its own sign-in |
| Stability AI | Stable Audio ambiences (optional) | Core `stability_api_key` |
| Scenario | Game-art models trained on your style | Registered by `arcosian-vendors` (`https://mcp.scenario.com/mcp`); authorize through `/mcp`, then register outputs with `manifest_update` |
| PixelLab | Pixel art, animation, tilesets | `arcosian-vendors` `pixellab_api_key` |
| Blockade Labs | 360 skyboxes | Not integrated; use their site or API manually |
| Blender (local, free) | Mesh cleanup, rigging, export | `arcosian-blender` adapter, no account |

Licence reminder: output rights differ by vendor and plan, and free tiers are often restricted. The gateway records provenance and warns, but you read the terms.

### Engines (local)

| Tool | Why | Config |
|---|---|---|
| Godot 4.x | Default engine | `arcosian-godot` userConfig `godot_bin` (path to the executable; pin to your project's version). The adapter's GDScript language server uses the same binary (or `GODOT_BIN`, PATH, `/Applications/Godot.app`) and needs Node 18+ |
| Unity 6 and Unity Hub | Alternative engine | The template pins Unity 6.3 LTS (6000.3.26f1). `arcosian-unity` expects the `unity` CLI on PATH; CI builds need a Unity licence, but the core tests also run licence-free on the .NET SDK (`templates/unity-starter/tools/dotnet-harness/`) |
| .NET 10 SDK and csharp-ls | C# language server for Unity projects | `dotnet tool install --global csharp-ls` (tested 0.28.0). Covers `Game.Core` without Unity; every script once Unity has written its project files (see the `arcosian-unity` README) |
| Xcode | iOS export and signing | macOS only |
| Android SDK, JDK | Android export | Install through Android Studio or `sdkmanager` (you accept Google's SDK licence yourself). For Godot 4.7.2: JDK 17, platform 36, build-tools 36.1.0, NDK 29.0.14206865 (verified with a real signed AAB export, 2026-10-21). The Godot CI uses `--install-android-build-template` because the preset builds with Gradle |
| Godot export templates | Desktop and web builds of the Godot template, `gs.py whatif` with the Godot bots | Editor > Manage Export Templates for your exact version (or unzip the official `.tpz` into the editor's `export_templates/<version>.stable/`). `gs.py whatif` and `sprite_sheet.py --verify` find Godot through `GODOT_BIN`, then PATH, then `/Applications/Godot.app` |
| Node, Python 3 | Gateway and scripts | Python stdlib only; no pip installs |

### Windows

The plugins run on Windows 10 and 11. Install these first:

| Tool | Why | Notes |
|---|---|---|
| Git for Windows | Claude Code runs shell commands in its Git Bash | Without it Claude Code falls back to PowerShell; the hooks work either way |
| Node.js 18+ | Gateway, language-server bridges, hook launcher | The Windows installer puts `node` on PATH |
| Python 3 (python.org) | Scripts and hooks | Windows has no `python3`. The default install adds the `py` launcher; ticking "Add python.exe to PATH" also gives `python`. Hooks start through `hooks/scripts/run-python.mjs`, which uses whichever of `python3`, `python` or `py -3` works and skips the Microsoft Store placeholders; at session start Claude is told which command to use where the docs say `python3` |
| Godot 4 | Engine, parse check, GDScript language server | The download is `Godot_v4.x-stable_win64.exe` plus `Godot_v4.x-stable_win64_console.exe`. Point the Godot adapter's `godot_bin` (or the `GODOT_BIN` environment variable) at either file or their folder: the `_console.exe` build is used when present, because only it reliably prints to a pipe. The parse-check hook reads the same option |
| JDK 17, Android SDK | Android export | Same versions as on macOS (see the table above); set the paths in Godot's Editor Settings |
| .NET 10 SDK, csharp-ls | C# language server for Unity | `dotnet tool install --global csharp-ls` installs to `%USERPROFILE%\.dotnet\tools`, which the launcher checks even when it is not on PATH |

iOS builds and signing need a Mac. From Windows, use the CI templates (GitHub Actions macOS runners or Codemagic) for iOS; Android builds run locally.

Install the marketplace from the folder you unpacked. Forward slashes work in PowerShell, Command Prompt and Git Bash alike; quote paths that contain spaces:

```
claude plugin marketplace add C:/dev/arcosian/arcosian
claude plugin install arcosian@arcosian
claude plugin install arcosian-godot@arcosian
```

Claude Code's PowerShell tool gets the same guards as Bash: store submission asks first; reading keystores, `.p12`, `.p8` or `.env` files (`Get-Content`, `type`, `[IO.File]::ReadAllBytes` and similar) is denied; `Remove-Item -Recurse` or `rd /s` on project state asks first. When you copy a template into a git repository, rename its `gitattributes.example` to `.gitattributes` so line endings stay LF on Windows.

Verified on macOS with Windows-like setups (no `python3`, a Store placeholder, only `py`, versioned Godot file names); not yet run on a Windows PC.

## 3. CI secrets table

From `templates/ci/README.md` (authoritative; read it before wiring CI):

| Secret | Used by |
|---|---|
| `ASC_KEY_ID`, `ASC_ISSUER_ID`, `ASC_KEY_CONTENT` | fastlane iOS (App Store Connect Team API key) |
| `MATCH_PASSWORD`, `MATCH_GIT_URL`, `MATCH_GIT_BASIC_AUTHORIZATION` | fastlane match (private certs repo) |
| `ANDROID_KEYSTORE_BASE64`, `ANDROID_KEYSTORE_PASSWORD`, `ANDROID_KEY_ALIAS`, `ANDROID_KEY_PASSWORD` | Android signing |
| `PLAY_JSON_KEY_DATA` | fastlane supply |
| `UNITY_LICENSE`, `UNITY_EMAIL`, `UNITY_PASSWORD` (and `UNITY_SERIAL` for Pro) | Unity CI |
| Variables `APP_IDENTIFIER`, `APPLE_TEAM_ID` | Not secret |
| `CONFIRM_RELEASE` | Set by a human per run, never stored |

## 4. First-run checklist

1. Install the marketplace and `arcosian`; install adapters you need.
2. Verify the install:
   ```
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/gs.py" --selftest
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/audit_plugin.py" --root "${CLAUDE_PLUGIN_ROOT}"
   ```
3. Open your game folder and run `/arcosian:studio`. Confirm it identifies the state correctly.
4. New project: `/arcosian:new-game "<one-line brief>"`, or `python3 .../gs.py init --title "..." --engine godot`.
5. Set the budget: `python3 .../gs.py budget` shows spend against the cap; change `.gamestudio/config.json` for the project.
6. Test the gateway for free: ask for an image with `GS_MOCK=1` (or `dry_run`) and confirm a manifest entry at cost 0.
7. Add one real key (for example Gemini) and check it costs-first with the gateway's live smoke test: `node "${CLAUDE_PLUGIN_ROOT}/mcp/studio-gateway/test/live-smoke.mjs" --provider gemini` prints the exact request and estimated cost (dry run); add `--yes` to make one capped, billed call into a temp project. Then generate one asset in your project and confirm the cost is recorded.
8. Copy the CI template for your engine, add secrets in the order given in `templates/ci/README.md`, push a branch, confirm validation is green before enabling build jobs.
9. Create store app records by hand; do the first TestFlight and Play internal upload manually or via CI with `CONFIRM_RELEASE` unset.
10. Enable the Stop-gate habit: run `gs.py validate --all` before ending a session.

## 5. Volatile facts (as of Oct 2026 — verify)

These change without notice. The suite stores sources in the relevant skills' references; verify before acting.

| Topic | Why it matters | Source |
|---|---|---|
| Apple upcoming requirements (SDK and Xcode minimums) | Uploads are rejected below the minimum | https://developer.apple.com/news/upcoming-requirements/ |
| Apple App Review Guidelines | Rejection reasons, IAP and privacy rules | https://developer.apple.com/app-store/review/guidelines/ |
| Apple third-party SDK requirements | Privacy manifests and signatures | https://developer.apple.com/support/third-party-SDK-requirements/ |
| Google Play target API level | Updates are blocked below the required target | https://developer.android.com/google/play/requirements/target-sdk |
| Google Play Console help (account testing rules, policies) | New developer account requirements | https://support.google.com/googleplay/android-developer/ |
| Codemagic pricing | Build minute costs | https://codemagic.io/pricing/ |
| fastlane releases | API-key and match behaviour | https://github.com/fastlane/fastlane/releases |
| Godot CI image tags | Engine version pinning in CI | https://hub.docker.com/r/barichello/godot-ci |
| Scenario MCP | Endpoint and auth (`https://mcp.scenario.com/mcp`, checked 2026-10-20) | https://help.scenario.com/articles/2664328768-getting-started-with-the-scenario-mcp-server |
| Adjust MCP | Endpoint and auth (`https://mcp.adjust.com/mcpo`, checked 2026-10-20) | https://help.adjust.com/en/article/adjust-mcp |
| Gemini image API | Interactions endpoint and model ids (`gemini-nano-banana-2.1`, checked 2026-10-20) | https://ai.google.dev/gemini-api/docs/image-generation |
| iOS export | Godot needs your App Store team ID; CI injects `APPLE_TEAM_ID` into the preset before exporting | `templates/ci/README.md` |

Prices for Apple, Google, Firebase, RevenueCat, AppLovin, generation vendors and device farms are intentionally not listed here: check vendor pricing.

## 6. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Gateway tools missing | Node not on PATH, or plugin not reloaded | `node --version`; restart the session or `/plugin` reload |
| Images are flat placeholders | No key for that provider, or mock mode | Add the key; unset `GS_MOCK` |
| "budget exceeded" | Project cap reached | `gs.py budget`; raise the cap deliberately in `.gamestudio/config.json` |
| Feature will not go to done | A gate is missing evidence | `gs.py feature show F001`; record the gate with `--evidence` |
| Stop is blocked | A feature is marked done but fails gates | Fix the evidence, or set the feature back to in progress |
| Write to `features.json` denied | Same five-gate rule in the PreToolUse hook | Use `gs.py feature gate` and `gs.py feature pass`, not hand edits |
| fastlane command asks for confirmation | Store-submission guard working as designed | Confirm only after the human approval checklist |
| iOS build cannot sign in CI | match repo empty or not seeded | Run `fastlane match appstore` locally once, then CI readonly |
| Play upload rejected | Package or app record not created, or service account lacks permission | Create the app in Play Console; grant release permission |
| Godot bridge cannot find engine | `godot_bin` unset | Set it in the godot adapter configuration |
| No `LSP` tool, or "language server unavailable" in `/plugin` Errors | Godot or csharp-ls not found, or no project near the session folder | The message names the cause; run the adapter's `lsp/lsp-selftest.mjs` (command in its README) |
| "no Python 3 found" hook errors (Windows) | Python not installed, or only the Microsoft Store placeholder | Install Python 3 from python.org and start a new session; the launcher retries automatically |
| `LSP server "<name>" is not used for .cs files` | Anthropic's `csharp-lsp` plugin enabled alongside `arcosian-unity` | Disable one; each extension gets one server |
| `audit_plugin.py` reports errors | Skill references not matching files on disk | Read the message; fix the listed path. See CHANGELOG, Known issues |
| A hook prints "failed open" on stderr | Internal hook error; the session is not blocked | Run `python3 hooks/tests/test_hooks.py` and report the failure |
