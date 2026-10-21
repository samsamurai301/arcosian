# Signing and Packaging: macOS, Windows, Linux

This file explains how to make desktop builds that operating systems trust: Developer ID signing, the hardened runtime, notarisation and stapling on macOS; Authenticode signing, certificate types, SmartScreen reputation and Microsoft's cloud signing service on Windows; and Linux options (native build, Proton, Steam Linux Runtime, AppImage, Flatpak). Commands are those in Apple's and Microsoft's documentation or standard tooling; flags that were not confirmed on an official page this session are marked "verify". Credentials (certificates, app-specific passwords, API keys) are entered by a human or injected from a CI secret store, never written to files or chat. Signing and notarising is not an upload, but submitting to Apple's notary service sends the build to Apple, so a human approves it.

## Contents
1. Do you need to sign?
2. macOS: accounts and certificates
3. macOS: hardened runtime and entitlements
4. macOS: sign, notarise, staple
5. macOS: universal binaries
6. macOS: what Godot and Unity do for you
7. Windows: signing options
8. Windows: Artifact Signing (Microsoft's cloud signing service)
9. Windows: traditional certificates, OV and EV
10. Windows: SmartScreen reputation
11. Windows: signtool recipes
12. Linux: native, Proton and the Steam Linux Runtime
13. Linux outside Steam: AppImage and Flatpak
14. Packaging and signing checklist

## 1. Do you need to sign?
| Channel | macOS | Windows | Linux |
|---|---|---|---|
| Steam | Sign and notarise (Gatekeeper still checks downloaded apps) | Sign recommended; Steam launches the game, but antivirus and SmartScreen can still react | No signing; test under the Steam Linux Runtime |
| itch.io or own site download | Developer ID plus notarisation required for a smooth install | Sign to reduce SmartScreen warnings | AppImage or tarball; optional detached signatures |
| Microsoft Store | n/a | Store signs MSIX packages on submission (verify) | n/a |
| Mac App Store | App Store signing and sandbox | n/a | n/a |
| Web | n/a | n/a | n/a |
Default: sign everything you distribute directly. Unsigned macOS apps need the user to override Gatekeeper; unsigned Windows installers show an "unknown publisher" warning.

## 2. macOS: accounts and certificates
1. Join the Apple Developer Program (human; paid, annual; identity checks). Needed for Developer ID.
2. Create a "Developer ID Application" certificate (signs apps and DMGs) and a "Developer ID Installer" certificate if you ship a `.pkg`. Use Xcode (Settings, Accounts, Manage Certificates) or the developer website. Keep the private key in the login keychain or a CI keychain; back it up in a password manager.
3. For notarisation create authentication for `notarytool`: an App Store Connect API key (preferred for CI) or an app-specific password for an Apple ID.
4. Store credentials once in the keychain (human runs this; replace the placeholders):
```
xcrun notarytool store-credentials "notary-profile" --apple-id "<APPLE_ID>" --team-id "<TEAM_ID>" --password "<APP_SPECIFIC_PASSWORD>"
```
   CI alternative: `--key <path-to-AuthKey.p8> --key-id <KEY_ID> --issuer <ISSUER_ID>` (verify against `xcrun notarytool --help`).

## 3. macOS: hardened runtime and entitlements
1. Notarisation requires the hardened runtime (`--options runtime`) and a secure timestamp (`--timestamp`).
2. The hardened runtime blocks things games sometimes do. Grant entitlements only for what you need. Typical:
| Need | Entitlement key |
|---|---|
| JIT or runtime code generation (Mono, some scripting) | `com.apple.security.cs.allow-jit` |
| Writable and executable memory | `com.apple.security.cs.allow-unsigned-executable-memory` |
| Loading unsigned or differently signed libraries (GDExtension, plug-ins, Steam overlay library) | `com.apple.security.cs.disable-library-validation` |
| DYLD environment variables | `com.apple.security.cs.allow-dyld-environment-variables` |
| Microphone | `com.apple.security.device.audio-input` plus `NSMicrophoneUsageDescription` in Info.plist |
| Camera | `com.apple.security.device.camera` plus `NSCameraUsageDescription` |
3. Never ship with `com.apple.security.get-task-allow` (the "Debugging" entitlement); notarisation rejects it.
4. Example `entitlements.plist` for a Mono-based Unity or Godot C# game:
```
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>com.apple.security.cs.allow-jit</key><true/>
  <key>com.apple.security.cs.allow-unsigned-executable-memory</key><true/>
  <key>com.apple.security.cs.allow-dyld-environment-variables</key><true/>
  <key>com.apple.security.cs.disable-library-validation</key><true/>
</dict>
</plist>
```
5. Add the Steam overlay: Steam injects a library; if the overlay does not appear after notarisation, test with `disable-library-validation` (verify with Valve's current notes).
6. Mac App Store builds use a different set: App Sandbox (`com.apple.security.app-sandbox`) and sandbox permissions, no Developer ID.

## 4. macOS: sign, notarise, staple
Source: Apple's notarisation documentation, https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution (page returned only a title in this session; the commands below are Apple's standard workflow, verify flags with `man codesign` and `xcrun notarytool --help`).
1. Sign inside-out: sign nested frameworks, dylibs and helper executables first, then the app bundle. Do not use `--deep` as the only method for complex bundles; sign each nested code item explicitly.
```
codesign --force --options runtime --timestamp --entitlements entitlements.plist \
  --sign "Developer ID Application: <NAME> (<TEAM_ID>)" MyGame.app/Contents/Frameworks/<lib>.dylib
codesign --force --options runtime --timestamp --entitlements entitlements.plist \
  --sign "Developer ID Application: <NAME> (<TEAM_ID>)" MyGame.app
```
2. Verify the signature locally:
```
codesign --verify --deep --strict --verbose=2 MyGame.app
codesign -dv --verbose=4 MyGame.app
```
3. Create a ZIP for submission (a notary submission may be a zip, dmg or pkg):
```
ditto -c -k --keepParent MyGame.app MyGame.zip
```
4. Human approves the submission (it uploads the build to Apple). Submit and wait:
```
xcrun notarytool submit MyGame.zip --keychain-profile "notary-profile" --wait
```
5. On "Invalid", read the log; the log names the file and the problem (unsigned library, missing timestamp, missing hardened runtime, debugging entitlement):
```
xcrun notarytool log <SUBMISSION_ID> --keychain-profile "notary-profile"
```
   History: `xcrun notarytool history --keychain-profile "notary-profile"`.
6. Staple the ticket to the app so it works offline (stapling works on `.app`, `.dmg`, `.pkg`, not `.zip`):
```
xcrun stapler staple MyGame.app
xcrun stapler validate MyGame.app
```
7. Ship as a DMG: build the DMG from the stapled app, sign the DMG, notarise and staple the DMG too.
```
hdiutil create -volname "MyGame" -srcfolder MyGame.app -ov -format UDZO MyGame.dmg
codesign --force --timestamp --sign "Developer ID Application: <NAME> (<TEAM_ID>)" MyGame.dmg
xcrun notarytool submit MyGame.dmg --keychain-profile "notary-profile" --wait
xcrun stapler staple MyGame.dmg
```
8. Gatekeeper test on a clean Mac (or a fresh user account) after downloading through a browser, so the quarantine flag is set: `spctl --assess --type execute -vv MyGame.app` and open it normally.
9. For Steam: upload the signed and notarised `.app` as the macOS depot content. Steam downloads do not carry the browser quarantine flag in the same way, but notarise anyway so players who copy the app are safe.
Failure causes seen most often: a nested binary not signed; hardened runtime missing on a helper tool; the Debugging entitlement left on; a third-party `.dylib` signed by someone else needing library validation off; timestamp missing; old SDK build tools flagged by Apple (read the log).

## 5. macOS: universal binaries
1. Apple Silicon is the current Mac platform; Intel Macs remain in use, so ship a universal binary (arm64 plus x86_64) unless your audience data shows otherwise.
2. Check: `lipo -archs MyGame.app/Contents/MacOS/<executable>` should print `x86_64 arm64`. Create one from two builds: `lipo -create -output <out> <x86_64-binary> <arm64-binary>`.
3. Every native plug-in and dylib inside the bundle must also be universal; a single Intel-only library breaks native arm64 launch. Check each with `lipo -archs`.
4. If a dependency is Intel-only, either drop Intel support (set the minimum system requirements honestly) or run under Rosetta (document it and test performance).
5. Declare the minimum macOS version (`LSMinimumSystemVersion` in Info.plist) from your engine's current minimum.

## 6. macOS: what Godot and Unity do for you
Godot (https://docs.godotengine.org/en/stable/tutorials/export/exporting_for_macos.html, verified):
- Exports a Universal 2 `.app` (Intel and Apple Silicon) and can package a ZIP or DMG (DMG creation needs macOS).
- Signing: on macOS uses Xcode `codesign` with a Developer ID identity; on Linux or Windows uses `rcodesign` with a PKCS #12 certificate. With no certificate you can choose ad-hoc signing and disabled notarisation (Gatekeeper may still block).
- Notarisation: set in the export preset using Xcode `notarytool` (Apple ID plus app-specific password, or App Store Connect API key) or `rcodesign` with API credentials. Godot does not staple for you: staple yourself afterwards (`xcrun stapler staple` or `rcodesign staple`). Disable the Debugging entitlement.
- Hardened runtime entitlements are toggles in the preset (JIT, unsigned memory, DYLD variables, disable library validation for GDExtensions, camera, microphone, and so on); Mono exports always enable JIT, unsigned memory and DYLD entitlements. A custom entitlements file overrides all toggles.
- Environment variables such as `GODOT_MACOS_CODESIGN_CERTIFICATE_FILE` and `GODOT_MACOS_NOTARIZATION_API_KEY` override the preset at export time, which suits CI (store the values as CI secrets).
Unity (not fetched; verify in Unity's macOS build documentation): the Player settings can build a macOS app with Intel, Apple Silicon or universal architecture, and recent versions have a notarisation and signing helper in the Mac build settings in some versions; otherwise run the codesign and notarytool steps in section 4 on the built app. Check the current Unity manual before assuming either.
Rule: whichever engine, verify the result with `codesign --verify`, `spctl --assess` and a clean-Mac test.

## 7. Windows: signing options
| Option | Cost model | Reputation | Effort |
|---|---|---|---|
| Artifact Signing (Microsoft cloud service) | Azure subscription with a monthly SKU | Public Trust certificate; reputation builds with file history | Azure setup plus identity validation |
| OV code-signing certificate from a CA | Annual fee | Reputation builds gradually | Buy, validate, store key on hardware or a cloud HSM |
| EV code-signing certificate from a CA | Higher annual fee | Same reputation system now (check Microsoft's SmartScreen page) | Hardware token or cloud key |
| No signature | Free | Warnings | None |
Default for a small team: Artifact Signing if your country and entity type are supported, otherwise an OV certificate with a cloud key service.

## 8. Windows: Artifact Signing (Microsoft's cloud signing service)
Name: Artifact Signing (formerly called Trusted Signing and, in some early materials, Azure Code Signing). Docs: https://learn.microsoft.com/en-us/azure/artifact-signing/overview (verified; pages dated 2026).
1. What it is: a fully managed signing service; keys live in FIPS 140-3 Level 3 HSMs; you never receive the certificate; the file never leaves your machine because it signs digests. It supports Public Trust, Private Trust and test signing; you can sign all file types SignTool supports.
2. Needs: a paid Azure subscription (free, trial and sponsored subscriptions are not supported); register the `Microsoft.CodeSigning` resource provider; create an Artifact Signing account (Basic or Premium SKU: Basic includes 5,000 signatures a month and one certificate profile of each type, Premium 100,000 and ten; prices are on the Azure pricing page, which showed no figures when fetched, so check the calculator).
3. Identity validation: Organisation or Individual. Organisation validation emails a link that expires after 7 days; failures allow limited attempts; Individual validation uses a government ID, face check and a Verified ID in Microsoft Authenticator. Supported countries and regions are listed under the quickstart prerequisites: check that yours is supported before planning around it. Validation cannot be expedited and expires; renew before the date.
4. Create a certificate profile (Public Trust) linked to the validated identity. The certificate subject is your validated legal name; no custom CN or O is allowed.
5. Roles: the identity that signs needs the "Artifact Signing Certificate Profile Signer" role.
6. Sign with SignTool, the Artifact Signing dlib and a metadata file (paths are placeholders; install the dlib per the docs):
```
signtool sign /v /debug /fd SHA256 /tr "http://timestamp.acs.microsoft.com" /td SHA256 ^
  /dlib "<path>\Azure.CodeSigning.Dlib.dll" /dmdf "<path>\metadata.json" MyGame.exe
```
   `metadata.json` holds the Endpoint, the CodeSigningAccountName and the CertificateProfileName for your account (field names per Microsoft's docs; verify). Authentication uses your Azure sign-in (interactive), a managed identity, or an environment credential (service principal) in CI: keep the secret in the CI secret store.
7. Timestamp: use the service's timestamp server (`http://timestamp.acs.microsoft.com`; check health with `curl http://timestamp.acs.microsoft.com`, status 200 means healthy). Always timestamp, so signatures stay valid after the short-lived certificate expires.
8. Verify: `signtool verify /v /debug /pa MyGame.exe`. Not every file type shows a Signature tab in Properties; use the command.
9. It does not issue EV certificates and there is no plan to (Microsoft FAQ). Resources cannot be moved across subscriptions or tenants; recreate if those change.
10. Other integrations: GitHub Actions, Azure DevOps task, PowerShell and an SDK exist (see the "signing integrations" page in the docs). CI approval: a human approves the release job; the signing step runs inside it.

## 9. Windows: traditional certificates, OV and EV
1. OV (Organisation Validated) and EV (Extended Validation) code-signing certificates come from commercial certificate authorities. The private key must be stored on certified hardware or a cloud HSM under current CA/Browser Forum rules (verify with the CA; so you cannot download a plain `.pfx` for a new certificate).
2. EV used to give immediate SmartScreen trust; Microsoft's current SmartScreen documentation should be read before paying for EV for that reason (section 10).
3. Individuals may struggle to buy OV or EV certificates; Artifact Signing's Individual validation is an alternative where supported.
4. Use a timestamp server so signatures remain valid after the certificate expires (`/tr <url> /td SHA256`).
5. Rotate: certificate validity is limited (about a year or up to three; verify); calendar renewal 60 days before expiry; keep the same publisher name to preserve reputation where the rules allow.

## 10. Windows: SmartScreen reputation
Source: https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/smartscreen-reputation (linked from Microsoft's FAQ; read in full before relying on it).
1. SmartScreen reputation builds automatically as the signed file or certificate is downloaded without reports. The prompt stops once the file hash has enough history (Artifact Signing FAQ).
2. If prompts persist on a signed file, submit it to Microsoft Security Intelligence (https://www.microsoft.com/wdsi) for review.
3. Each new build hash starts afresh unless the certificate carries the reputation: sign every file (the exe, the installer and the DLLs you own), not just the installer.
4. Practical steps: sign consistently with the same identity; avoid packers and obfuscators that look like malware; avoid frequent re-signing of the same version; ship through Steam where the Steam client launches the game (the SmartScreen prompt mostly matters for direct downloads).
5. Antivirus false positives: scan your final build with Microsoft Defender and submit false positives to the vendor; engines using custom launchers or self-extracting installers trigger more.

## 11. Windows: signtool recipes
1. `signtool` ships with the Windows SDK; find it under `C:\Program Files (x86)\Windows Kits\10\bin\<version>\x64\`.
2. Sign with a certificate in the store (`/a` picks the best certificate) and a timestamp:
```
signtool sign /fd SHA256 /tr <TIMESTAMP_URL> /td SHA256 /a MyGame.exe
```
3. Sign the installer last, after signing the files inside it; sign MSIX packages with a certificate whose subject matches the manifest Publisher (a mismatch gives error 0x8007000B in Microsoft's table).
4. Verify: `signtool verify /pa /v MyGame.exe`.
5. Godot: Windows export presets have code-signing options (signtool or osslsigncode with identity and timestamp settings; verify the option names in the version you use). Unity: sign the built exe in a post-build step; Unity does not hold your certificate.
6. Cross-platform CI: signing from Linux is possible with `osslsigncode` and a key file or HSM; for Artifact Signing use a Windows runner.
7. Installer choice: Steam needs no installer (depots hold loose files); direct download uses a zip or an installer (Inno Setup, WiX or MSIX); sign the installer and the game executable.

## 12. Linux: native, Proton and the Steam Linux Runtime
1. Options on Steam: a native Linux build, or none (Windows build through Proton). Steam Deck runs both; Verified needs no manual config (see `steam.md` section 9).
2. Proton-only is the cheapest: test the Windows build on Linux with Proton and fix blockers; the Steam Deck compatibility review judges Proton bugs.
3. Native builds: build on an older distribution (or in a container) so the glibc version is low enough for most users; ship your own copies of non-system libraries; use the Steam Linux Runtime container so libraries match across distributions (read Valve's current guidance and runtime names in the Steamworks Linux documentation).
4. Native Linux needs more testing: Wayland and X11, Mesa and proprietary GPU drivers, gamepads, fractional scaling. Decide native only if you can test on at least two distributions and one Deck.
5. Godot: Linux export templates are supported; the engine's own docs treat Steam Deck as the officially supported console-like target. Unity: Linux standalone build target; check supported distributions in the manual.
6. Architecture: x86_64 is the default; arm64 Linux is niche.

## 13. Linux outside Steam: AppImage and Flatpak
1. AppImage: a single executable file that runs on most distributions without installation. Build the app directory (AppDir) with the game, a `.desktop` file and an icon, then run `appimagetool` (download it from the project's releases, verify the checksum). Tell users to mark it executable (`chmod +x`). Updates are manual unless you add zsync metadata.
2. Flatpak and Flathub: create a manifest, build with `flatpak-builder`, test with `flatpak run`, then submit the manifest to Flathub (a pull request to the Flathub repository; Flathub's current policy on proprietary games applies: read its submission guidelines). Flatpak sandboxes file, device and network access; declare permissions (`--device=dri`, `--socket=pulseaudio`, `--share=network`, and so on) in the manifest.
3. Tarball: simplest; unpack and run; include a start script and a `README`.
4. Sign releases with a detached GPG signature and publish the checksum if you distribute from your own site.
5. itch.io's app can launch Linux builds; set `linux` in the butler channel name (see `itch-and-web-portals.md`).

## 14. Packaging and signing checklist
1. Version and build number embedded in the executable and the store.
2. Windows: all owned executables and DLLs signed and timestamped; installer signed; Defender scan clean.
3. macOS: nested code signed, hardened runtime on, no debugging entitlement, universal binary, notarised and stapled; Gatekeeper test on a clean Mac.
4. Linux: tested on one Deck or Linux PC; no unexpected library dependencies (`ldd` on the executable).
5. Debug symbols stored privately (not shipped); crash symbolication files archived with the build id.
6. Secrets: certificates, API keys and passwords only in the CI secret store or a password manager; none in the repo or logs.
7. Human approval recorded before notarisation submission and before any store upload.
8. Release report lists the signing identity, the timestamp server and the verification outputs.
