# addons/

Nothing is vendored here. The template runs with zero add-ons (built-in test runner, mock ads and IAP).
Add what you need, pin versions, and commit them. Verify the current release of each before relying on it.

## GdUnit4 (optional unit-test framework)

The built-in runner (`tools/ci/run_tests.gd`) covers `tests/unit/test_*.gd`. Use GdUnit4 for scene tests,
mocking and richer assertions.

1. AssetLib (Godot editor) > search "GdUnit4" > Download > Install, or download a release zip from the
   GdUnit4 GitHub releases page and copy `addons/gdUnit4/` into this folder.
2. Project > Project Settings > Plugins > enable "gdUnit4".
3. Keep GdUnit4 tests in `tests/gdunit/` so the built-in runner does not pick them up.
4. CLI: `godot --headless --path <project> -s -d res://addons/gdUnit4/bin/GdUnitCmdTool.gd --add res://tests/gdunit`
   (check the GdUnit4 docs for the flags of the release you installed; point its JUnit output at
   `.gamestudio/evidence/<FEATURE-ID>/unit.xml`).

## Google Play Billing (Android IAP)

1. Install the official Godot Google Play Billing plugin that matches your Godot version (Godot docs:
   "Android in-app purchases"), then install the Android build template (Project > Install Android Build Template).
2. Enable the plugin in the Android export preset (`export_presets.cfg` > Plugins).
3. Write `services/iap_play.gd` implementing `purchase(product_id)` and `restore()`; emit
   `Iap.purchase_result` / `Iap.restore_done`; call `Iap.set_backend(instance)` at boot on Android.
4. Verify purchases server-side before granting premium items; acknowledge purchases within the Play window.

## StoreKit 2 (iOS IAP)

1. Use a maintained StoreKit 2 Godot plugin (iOS plugins are built as xcframeworks); copy its `.gdip` and
   frameworks into `ios/plugins/` and enable it in the iOS export preset.
2. Implement the same `purchase` / `restore` backend as above in `services/iap_storekit.gd`.
3. Required by App Store review: a visible "Restore Purchases" control wired to `Iap.restore()`.

## AppLovin MAX (ads mediation)

1. Install the AppLovin MAX Godot plugin for Android and iOS (see AppLovin's integration docs); put your SDK
   key in an untracked file or environment variable, never in `project.godot`.
2. Write `services/ads_max.gd` with `show_rewarded(placement)` and `show_interstitial(placement)`; emit
   `Ads.rewarded_result(placement, granted)` / `Ads.interstitial_closed(placement)`; `Ads.set_backend(instance)`.
3. Gate by consent (UMP / ATT) before initialising; respect the contract's `monetization.ads.interstitial` pacing.

Add-ons live under `res://addons/`; `tools/ci/check_all.gd` skips this folder so third-party code never fails the static gate.
