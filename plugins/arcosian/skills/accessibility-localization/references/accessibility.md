# Accessibility for mobile games

Summary: this file turns accessibility guidance into build decisions for phone games. It summarises, in my own words, the structure of the Game Accessibility Guidelines (a community resource organised into basic, intermediate and advanced tiers across motor, cognitive, vision, hearing, speech and general areas) and the Xbox Accessibility Guidelines (Microsoft's numbered guidance for studios), then covers what iOS and Android already provide and what they do not, followed by concrete design rules for colour vision, motor, cognitive, hearing and photosensitivity needs, recipes for Godot 4 and Unity 6, and a test plan. Numbers such as contrast ratios come from WCAG and are stable; platform feature availability is volatile and marked.

## Contents
1. Frameworks and how to use them
2. Mobile OS capabilities and limits
3. Vision: text, contrast, scale
4. Colour vision deficiency
5. Blind and low-vision play
6. Motor and input
7. Cognitive and learning
8. Hearing
9. Photosensitivity and motion
10. Speech and social features
11. Godot 4 recipes
12. Unity 6 recipes
13. Testing
14. Prioritised backlog and costs
15. Volatile facts (as of Oct 2026 - verify)

## 1. Frameworks and how to use them
**Game Accessibility Guidelines (gameaccessibilityguidelines.com).** A set of checks grouped by tier. Basic tier: items that cost little and help many, such as adjustable text size, no reliance on colour alone, subtitles on by default for speech, allow remapping or alternatives to hard inputs, avoid flashing, offer a way to pause, clear tutorials. Intermediate: difficulty or assist options, adjustable timing, separate volume controls, simplified controls, highlight of interactive elements. Advanced: full screen-reader support in-game, audio description, customizable controls across all inputs, extensive difficulty tuning, sign-language content.
**Xbox Accessibility Guidelines.** Numbered guidelines covering areas such as text display, input, audio, UI navigation, difficulty and assist, communication and photosensitivity. Their value for a studio is the phrasing of testable requirements and the idea of "accessibility feature" documentation for players. Where they refer to console features, translate to touch.
**WCAG.** Written for web, but its contrast and target size numbers are the common yardstick: text contrast of at least 4.5:1 for normal text and 3:1 for large text and UI components; touch targets of at least 44 by 44 points on Apple platforms and 48 by 48 dp on Android are the platform recommendations.
How to use them: take the baseline in section 14, mark each item as done, planned, or not applicable with a reason, publish the status in a short accessibility statement, and revisit every major release. Treat guideline items as hypotheses to test with players, not as law.

## 2. Mobile OS capabilities and limits
| Capability | iOS | Android | Game implication |
|---|---|---|---|
| Screen reader | VoiceOver | TalkBack | Works on native UI; custom-drawn game views are invisible unless you expose accessibility nodes or build a native overlay for menus |
| Text scaling | Dynamic Type | Font scale setting | Engines ignore it by default; read the scale and apply to your UI theme |
| Reduce motion | Reduce Motion setting | Remove animations setting | Read it at boot; map to your reduced-motion option |
| Contrast | Increase Contrast, Bold Text | High contrast text, colour correction | Colour correction is system-wide at the compositor on both OSes, but your art still needs redundancy |
| Colour filters | Colour filters | Colour correction | Good as a safety net; do not rely on it |
| Switch input | Switch Control | Switch Access | Needs focusable, sequential UI; real-time play is mostly out of reach |
| Captions | System caption styles | Captions preferences | Games render their own captions; offer style options |
| Haptics | Core Haptics | Vibrator and haptics APIs | Provide intensity control and an off switch |
| Touch accommodations | Assistive Touch, hold duration, tap assistance | Touch and hold delay, similar | Respect that long-press timing may be altered; avoid precision multi-touch |
| Voice control | Voice Control | Voice Access | Needs labelled controls; custom UI without labels cannot be addressed |
| Guided access / app pinning | yes | yes | Useful for supervised play |
Practical stance: menus, shops, settings and story screens can be made screen-reader-friendly with moderate effort; moment-to-moment action games usually cannot, so spend effort on assist options, audio cues, haptics and difficulty design instead. Be honest in store text about what is and is not supported.

## 3. Vision: text, contrast, scale
- Body text: design for a readable minimum size on the smallest supported phone, then offer at least three scale steps (default, large, extra large) and let the layout reflow; panels scroll rather than clip.
- Avoid text on busy backgrounds: add a solid or semi-opaque plate behind text, or an outline of sufficient contrast.
- Contrast: aim for 4.5:1 for body text, 3:1 for large headings and icons that carry meaning. Check in the style bible with an automated contrast calculator.
- Fonts: choose forms with clear letter distinction (I, l, 1; O, 0); avoid ultra-thin and decorative faces for body text; keep decorative fonts for titles.
- Bold or high-contrast UI mode: a toggle that swaps to a palette with stronger contrast and thicker outlines.
- Numbers matter in games: damage, currency, timers must be legible during motion; keep them stationary or give a stable readout.
- Sunlight: test in bright light; low-contrast pastel UI fails outdoors, a situational impairment.
- Zoom: allow pinch-zoom or a magnifier where maps and boards are dense.
- Text in images: never; it blocks scaling and translation.
- Icon plus label: icons alone are ambiguous; provide labels at least in menus and on first use.

## 4. Colour vision deficiency
Roughly speaking, red-green deficiencies are the most common forms of colour blindness, and blue-yellow and total forms are rarer; precise prevalence varies by population, so use "common" rather than quoting a number.
Rules:
1. Redundant coding: every colour-coded meaning also has shape, pattern, icon, position or text. Examples: gem types differ in silhouette; team colours carry an emblem; health bars have a numeric readout and a low-health icon.
2. Palette choice: use the lightness channel for the main distinction (dark vs light), and hue only as secondary. Verify pairs with simulation filters for protan, deutan and tritan types.
3. Avoid pairs: red vs green, green vs brown, blue vs purple, and orange vs green at similar lightness as sole carriers.
4. Provide a preset colour-blind palette setting if your art relies on hue; also let players recolour critical elements (enemy outlines, friendly/enemy tint).
5. State feedback (correct/wrong): add a symbol (check, cross) and a distinct sound.
6. Match-3 and puzzle games: distinct silhouettes per tile type, optional symbols overlay, high-contrast outlines.
7. Test in simulation on actual screenshots of each key screen; run the check in art review (`art-direction`).
8. Do not depend on the OS colour filter; it changes colours globally but cannot fix missing redundancy.

## 5. Blind and low-vision play
- Fully blind play of a visual mobile game is rare; target low-vision support (scaling, contrast, simplification) first and screen-reader support for menus second.
- Menus: label every control with a short accessible name, expose role and state (button, toggle on/off), order focus logically, announce screen changes and popups, and make dialogs dismissible.
- Gameplay for turn-based and text-driven games can be made accessible with a parallel text representation (board described in text, focus navigation among options). Puzzle games with grids are feasible with a coordinate-based focus model.
- Audio-first design: positional cues, distinct earcons for events, speech output of state on demand ("read status" button).
- Haptic patterns for events, with a documented pattern legend.
- Offer assist modes: slower speed, auto-aim, highlight targets, simplified visuals (reduced clutter, no particle effects).

## 6. Motor and input
- Touch targets: at least 44 pt (iOS) or 48 dp (Android) with spacing; for core buttons, larger, and allow user scaling of controls.
- Gestures: provide alternatives to swipes, pinches and drags (tap-to-select then tap-to-place). Multi-finger gestures need a single-finger option.
- Holds: any hold action gets a toggle mode; adjustable hold durations.
- Timing: no required rapid tapping for progress; accept slower input; offer slow mode or auto-repeat; avoid reaction-time gating for rewards in non-competitive modes.
- Layout: one-handed play, both orientations, left- and right-hand mirror, controls within thumb reach (`mobile-ux`); avoid placing controls at screen edges where system gestures trigger.
- Accidental input: confirmation for destructive or paid actions; undo for puzzle moves; cooldown on purchase buttons; protect against palm touches by ignoring input outside defined zones.
- Switch and external input: support controllers (Bluetooth gamepads) where the engine allows; sequential focus order for menus.
- Fatigue: avoid long sessions requiring constant tapping; allow rest and auto-save.
- Remapping: for any button layout on-screen, allow repositioning and resizing of virtual controls.

## 7. Cognitive and learning
- Clear goals: state the current objective in one visible line; allow re-reading.
- Tutorials: short, interactive, replayable from settings; no forced long text; show, then ask the player to try.
- Complexity management: introduce mechanics one at a time (`progression-difficulty`); allow hiding of advanced HUD elements.
- Reading load: plain language, short sentences, avoid jargon and idioms, consistent terminology; offer larger text and dyslexia-friendly typography choices (spacing, left aligned, avoid italics blocks).
- Memory: show last action and next step, keep hints one tap away, save at all times, resume exactly where the player left off.
- Attention: allow pausing everywhere, remove distracting animation on request, avoid flashing prompts, limit simultaneous notifications.
- Time pressure: optional timers; no penalties for slow decisions in single-player.
- Difficulty and assists: a visible, non-shaming way to lower difficulty; assists named by function ("more time", "show hints"), no achievements lockout without disclosure.
- Predictability: consistent navigation, no moving buttons, no surprise ads over controls.
- Anxiety and sensory overload: option to mute loud sounds, calm mode, no jump scares unless warned.
- Content warnings where relevant (violence, gambling-like content, flashing).

## 8. Hearing
- Captions: for all speech and for sound cues that carry gameplay information (offscreen threat, low-time warning). Caption background plate, size and colour options; speaker names; sound descriptions in brackets ("[alarm rings]") when the cue matters.
- Subtitles on by default for speech; ask in first run.
- Redundancy: every critical audio cue has a visual or haptic twin; check by muting the build and playing.
- Mix: separate sliders for music, effects, speech, ambience; consider a mono option; avoid speech masked by music (ducking).
- Voice chat: provide text chat alternative and speech-to-text if you offer voice; moderation implications (`legal-ethics`).
- Rhythm games: visual-only and haptic-only modes.
- Sign-language and written summaries for cinematics are an advanced-tier addition.

## 9. Photosensitivity and motion
- Flashing: avoid content that flashes more than three times in any one second, or where the flash is large and high-contrast; broadcast and web standards give the numeric thresholds (the WCAG three-flash threshold is a widely used baseline). Treat saturated red flashes and high-contrast patterns (stripes, spirals) as high risk.
- Test: run recorded gameplay through an analyser tool (the Harding-style tests used in broadcast are commercial; free approximate analysers exist); keep reports.
- Provide a "Reduce flashes" option that replaces flashes with fades, and a general "Reduce motion" option that disables screen shake, camera bob, parallax, zoom transitions and spinning UI.
- Warnings: a first-run photosensitivity notice is common practice; it does not replace safe design.
- Vestibular sensitivity: large field-of-view motion, forced camera movement and scrolling backgrounds cause discomfort; avoid, or provide static background and reduced camera motion.
- Game feel (`game-feel`): juice must scale down; define for each effect a reduced variant; juice budgets include a motion-reduced profile.
- Respect OS Reduce Motion by default on first launch.

## 10. Speech and social features
- Do not require speech to progress; offer text and quick-chat alternatives.
- Provide mute, block and report features and per-player volume.
- Pre-set phrases and emotes reduce text-entry burden and translate easily.
- Moderation, children's rules and consent for voice (biometrics) in `legal-ethics`.

## 11. Godot 4 recipes
UI scaling and text
- Use `Control` nodes with containers (`VBoxContainer`, `MarginContainer`, `ScrollContainer`) so panels reflow; avoid absolute positions.
- Central theme resource; set font sizes through theme overrides and apply a user scale factor via `get_tree().root.content_scale_factor` for the whole UI or by scaling theme font sizes.
- Read the OS text scale where the platform exposes it (through a platform plugin or `DisplayServer` queries where available); otherwise provide in-game steps.
- Labels with `autowrap_mode` and `custom_minimum_size` so text wraps instead of overflowing.
Colour-blind safety
- Store palette tokens in a `Resource` with a `palette_mode` setting; apply via theme overrides and shader parameter.
- Optional full-screen colour-blind simulation shader (for testing in-editor) on a `CanvasLayer`: matrices for protan, deutan, tritan applied to the final colour; keep it behind a debug toggle for QA, not as a player feature.
Reduced motion and flashes
- A global `Accessibility` autoload exposing booleans (`reduce_motion`, `reduce_flashes`, `subtitles`, `haptics_scale`); tweens and shake code read them. Example pattern:
```gdscript
extends Node
class_name AccessibilitySettings
signal changed
var reduce_motion: bool = false
var reduce_flashes: bool = false
var text_scale: float = 1.0
func set_text_scale(v: float) -> void:
    text_scale = clampf(v, 0.8, 1.6)
    changed.emit()
```
- Wrap screen shake: `if not Accessibility.reduce_motion: shake(amount)`.
Screen reader
- Godot 4.5 and later includes accessibility support through AccessKit for built-in `Control` nodes in recent versions; check the release notes of the engine version you ship for platform coverage and set accessible names and descriptions on controls. Verify on device with VoiceOver and TalkBack because support differs by platform and version.
Input
- Use the `InputMap` and expose rebinding for gamepad and keyboard; for touch, make virtual joystick and buttons repositionable and scalable and store layout in a user config file.
- Touch targets: `custom_minimum_size` at least 48 by 48 logical pixels adjusted for the stretch mode; check on device density.
Haptics
- `Input.vibrate_handheld(duration_ms)`, wrapped in a service that applies the user intensity or off setting.
Captions
- A `CaptionService` autoload driven by sound events: each `AudioStreamPlayer` event has a caption key; show a `PanelContainer` with a background and size options.

## 12. Unity 6 recipes
UI scaling and text
- Use UI Toolkit or uGUI with Canvas Scaler (scale with screen size, match width or height tuned for portrait), layout groups and content size fitters; TextMeshPro with auto-size min and max as a safety net, not a substitute for layout design.
- Read `Screen.safeArea` for notches; apply to a root container.
- A `UserSettings` ScriptableObject with text scale, palette mode, reduce motion, haptics; a `SettingsChanged` event refreshes UI.
Colour-blind safety
- Palette ScriptableObjects per mode; material property blocks or shared shader globals (`Shader.SetGlobalColor`) to switch.
- Testing: a full-screen post-process or Camera effect with colour-blind matrices in editor-only builds.
Reduced motion
- Central `MotionPolicy` static class: `MotionPolicy.Shake(amount)` returns zero when reduced; Cinemachine impulse and animation speeds read it.
Screen reader
- Unity provides a mobile accessibility package that integrates with VoiceOver and TalkBack for UI Toolkit and uGUI elements in recent Unity 6 versions; verify package availability and supported controls in the release notes of your Unity version, then label nodes and test on device.
Input
- Input System package with rebindable actions; on-screen controls (`OnScreenStick`, `OnScreenButton`) in a user-adjustable layout saved to JSON.
- `Handheld.Vibrate()` is coarse; use a vendor-neutral haptics plugin for intensity control, and wrap it behind an interface with a user scale.
Captions
- `CaptionManager` driven by an `AudioEvent` ScriptableObject with a caption string key from the Localization package.
Testing hooks
- An editor menu that applies large text, colour-blind simulation and reduced motion to the current scene for screenshot capture.

## 13. Testing
Automated
- Contrast checks on the theme palette in CI (compute ratios for text/background pairs).
- Pseudo-localization and large-text screenshot diffs to catch clipping.
- Colour-blind simulation screenshots of key screens, reviewed by art direction.
- Flash analysis on recorded cutscenes and effect-heavy sequences.
Manual per release
- Mute test (play with sound off), grayscale test (screen in grayscale), one-hand test, largest-text test, reduced-motion test, airplane-mode interruption test, screen-reader pass on menus.
- Checklist from sections 3 to 9, signed by `ux-designer`.
Player testing
- Recruit players with relevant needs (disability organisations, community forums, paid testers); pay them; test early prototypes rather than only final builds; observe real tasks (finish tutorial, change a setting, buy an item).
- Capture feedback in a structured form: barrier, severity, suggested change.
Metrics
- Setting usage rates and drop-off on the tutorial by settings group (privacy-safe, aggregate), crash-free rate under large text, support tickets mentioning accessibility.
Documentation
- A short Accessibility section in the store listing and in-game: what is supported, what is not, how to give feedback.

## 14. Prioritised backlog and costs
| Item | Tier | Effort | Priority |
|---|---|---|---|
| No colour-only meaning | Basic | Low if done in design; medium retrofit | P0 |
| Text scale and contrast | Basic | Low to medium | P0 |
| Pause anywhere, adjustable timing | Basic | Low | P0 |
| Captions and separate volumes | Basic | Medium | P0 |
| Reduce motion and flashes | Basic | Low if effects centralised | P0 |
| Touch target and control scaling | Basic | Low | P0 |
| Tutorial replay | Basic | Low | P1 |
| Assist and difficulty options | Intermediate | Medium | P1 |
| Control repositioning, one-hand mirror | Intermediate | Medium | P1 |
| Haptic twins for audio cues | Intermediate | Medium | P1 |
| Screen-reader menus | Advanced | Medium to high | P2 |
| Full game screen-reader or audio-only mode | Advanced | High | P3, genre dependent |
| Sign-language or audio description for narrative | Advanced | High | P3 |
Effort depends heavily on whether the UI toolkit, theme and effects are centralised: build centralisation first (`game-architecture`).

## 15. Volatile facts (as of Oct 2026 - verify)
- Game Accessibility Guidelines (tiered checklist): https://gameaccessibilityguidelines.com/
- Xbox Accessibility Guidelines: https://learn.microsoft.com/en-us/gaming/accessibility/guidelines
- WCAG contrast and flash thresholds: https://www.w3.org/WAI/standards-guidelines/wcag/
- Apple Human Interface Guidelines on accessibility and touch targets: https://developer.apple.com/design/human-interface-guidelines/accessibility
- Android accessibility developer guidance: https://developer.android.com/guide/topics/ui/accessibility
- Godot accessibility (AccessKit) support level by version: check the release notes at https://godotengine.org/ for the version you ship.
- Unity mobile accessibility package availability: check https://docs.unity3d.com/ for your Unity 6 version.
- Store accessibility labels (Apple accessibility nutrition labels, Play accessibility information): confirm current availability in App Store Connect and Play Console before claiming features.
