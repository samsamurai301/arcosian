# Platform UX

This reference covers the parts of UI that change with the platform: resolutions and aspect ratios, DPI and scaling, safe areas and TV 10-foot design, the settings menu PC players expect, focus loss and pause, window modes, platform conventions, minimum text sizes, and two accessibility checklists (Xbox Accessibility Guidelines and Game Accessibility Guidelines). Mobile-only layout rules are in `mobile-ux`; this file shows how to extend a UI beyond phones. Sizes are defaults and estimates unless a source is named.

## Contents

1. Resolutions and aspect ratios
2. DPI and UI scaling
3. Safe areas and the TV 10-foot UI
4. The PC settings menu players expect
5. Focus loss, pause and interruptions
6. Window modes and display handling
7. Platform conventions
8. Minimum text and target sizes
9. Xbox Accessibility Guidelines as a checklist
10. Game Accessibility Guidelines as a checklist
11. UX test matrix

## 1. Resolutions and aspect ratios

### Targets to support

| Aspect | Typical resolutions | Where you meet it |
|---|---|---|
| 16:9 | 1280x720, 1920x1080, 2560x1440, 3840x2160 | TVs, most monitors, laptops, consoles, web |
| 16:10 | 1280x800 (Steam Deck), 1920x1200, 2560x1600, 2880x1800 | Steam Deck, MacBooks, some laptops |
| 21:9 and 32:9 | 2560x1080, 3440x1440, 5120x1440 | Ultrawide monitors (a small but vocal share) |
| 4:3 and 5:4 | 1024x768, 1280x1024 | Older monitors, iPads (about 4:3), windowed play |
| Phones, landscape | 19.5:9 to 20:9 and taller (about 2.1:1 to 2.2:1) | Modern iPhones and Android phones |
| Phones, portrait | the same, rotated (about 9:19.5) | Portrait games |
| Tablets | 4:3, 3:2, 16:10 | iPad, Android tablets |
| Foldables | Near square when open, tall when closed; aspect changes at run time | Android foldables |

Steam Hardware Survey, Sept 2026: the primary display is 1920x1080 for 47.91 percent of players and 2560x1440 for 27.04 percent, with 2560x1600 and 3840x2160 each about 5 percent (`references/performance-tiers.md` section 7). So 16:9 at 1080p is the baseline and 1440p is common; 4K is a minority.

### Policy by game type

| Game type | Policy |
|---|---|
| 2D pixel art | Integer scale of a fixed base resolution (for example 320x180 scaled by 6 at 1080p). Show extra background beyond the playfield on wider screens, or letterbox with a border. Never blur-scale non-integer unless the player chooses. |
| 2D high-resolution | Design the playfield for 16:9 and extend backgrounds to cover 21:9 and 4:3. Anchor HUD to screen edges, not the playfield. |
| 3D | Horizontal FOV adapts to aspect (Hor+). Fixed vertical FOV on 21:9 crops less but shows more sides; fixed horizontal FOV crops the top and bottom on 4:3. Provide a FOV slider (section 4). |
| UI-heavy (strategy, builder) | Layout containers that reflow; avoid fixed pixel coordinates. Minimum supported window size (for example 1280x720). |
| Competitive | Do not let wider aspect give a view advantage: clamp the visible world or document the behaviour. |
| Cutscenes | Pre-rendered 16:9 video letterboxes on ultrawide; real-time cutscenes should handle the extra width or add bars. |

Rule: decide a **design resolution** (for example 1920x1080), a **safe region** (for example the central 16:9) that always holds every essential element, and an **extension region** beyond it that is allowed to be cropped.

### Test set

Test at least: 1280x720, 1280x800, 1920x1080, 1920x1200, 2560x1080, 3440x1440, 1024x768, a phone landscape (2400x1080), a phone portrait (1080x2400), and a resized window. The common failure is a HUD element clipped or overlapping at 21:9 or 4:3.

### Engine recipes

- **Godot**: Project Settings, Display, Window, Stretch: mode `canvas_items` for 2D UI and `viewport` for pixel art; aspect `expand` to extend the view beyond the design aspect (anchors then pin the HUD), `keep` for letterbox, `keep_width` or `keep_height` for fixed axes. Use `Control` anchors and containers (`MarginContainer`, `HBoxContainer`, `GridContainer`). For 3D, `Camera3D.keep_aspect` set to keep width or height (Hor+ is `KEEP_HEIGHT`).
- **Unity**: Canvas Scaler, Scale With Screen Size, reference resolution 1920x1080, match width or height slider between 0 and 1 (0.5 balances; use 1 for portrait-first at a portrait reference, 0 for landscape on wide). Use Anchors, Layout Groups and the safe area helper (section 3). For 3D, set camera FOV by aspect in a script or use Cinemachine.
- **Web**: CSS flex and grid layout, `devicePixelRatio`, `ResizeObserver` on the canvas container; resize the drawing buffer to `clientWidth * dpr` (cap dpr at 2 to 3 for performance).

## 2. DPI and UI scaling

Two separate ideas:

- **Resolution scaling (3D render scale)**: how many pixels the 3D scene renders (see performance).
- **UI scaling**: how large controls and text are, independent of render resolution. UI should stay crisp at native resolution while the 3D scene is scaled.

Rules:

1. Define UI sizes in density-independent units (dp or points) or in fractions of screen height. A button that is 48 px tall at 1080p and 24 px at 4K is a bug.
2. Offer a **UI scale slider** (for example 75 to 150 percent in steps of 5; allow up to 200 percent if layout permits). Default by screen: 1080p 100 percent, 4K desktop 150 percent or the OS scale, Steam Deck 100 percent (see section 8 for text minimums), TV 125 percent (section 3).
3. Respect OS scaling on desktop: Windows display scaling (100 to 200 percent or more), macOS Retina (2x), Linux fractional scaling. On Windows, mark the executable DPI-aware or the OS will bitmap-stretch the window and blur it; both Godot and Unity export DPI-aware by default but verify with a screenshot at 150 percent.
4. Use vector or high-resolution art for UI (SVG, signed-distance-field fonts, nine-slice panels); provide 2x and 3x raster atlases for mobile.
5. Fonts scale with the UI scale. Use SDF or dynamic fonts so 4K stays sharp. Keep line height at about 1.2 to 1.5 times the font size.
6. Test pairs: 1080p at 100 percent, 1440p at 125 percent, 4K at 150 and 200 percent, a 7-inch 1280x800 handheld at 100 percent.

Physical size check. For a given PPI, size in mm is `px / ppi * 25.4`. Steam Deck's 7-inch 1280x800 screen is about 216 PPI. A 9 px font there is about 1.06 mm tall (the minimum Valve allows) and 12 px is 1.41 mm (recommended); compare a typical 27-inch 1440p monitor at about 109 PPI viewed from 60 to 70 cm, where 18 to 20 px text is comfortable.

## 3. Safe areas and the TV 10-foot UI

### Safe areas

| Platform | What intrudes | Handling |
|---|---|---|
| iPhone | Notch or Dynamic Island, rounded corners, home indicator | Use the OS safe area insets; background art may extend to the edges, controls may not |
| Android | Cutouts, display punch holes, system bars, gesture navigation, rounded corners; edge-to-edge is enforced for apps targeting recent API levels | Use window insets (`WindowInsets`, `DisplayCutout`) and keep controls out of gesture zones at the edges |
| TV (consoles, Steam Big Picture on TV) | Overscan on some TVs | Provide a safe-margin setting; the console SDKs define title-safe regions; defaults of 3 to 5 percent margin on each side are a reasonable estimate for PC games on TV |
| Steam Deck | None, the screen is rectangular | Full screen, but keep UI out of the extreme 1 to 2 percent where the bezel can clip the view when held |
| Desktop windowed | Title bar, taskbar, notch on MacBooks | Use the work area; avoid putting UI under the Mac notch in fullscreen |

Godot: `DisplayServer.get_display_safe_area()` returns a `Rect2i`; apply to a root `MarginContainer`. Unity: `Screen.safeArea` (pixels) converted to anchors on a safe-area panel. Web: CSS `env(safe-area-inset-top)` and the others, with `viewport-fit=cover` in the meta viewport tag. Mobile detail: `mobile-ux`.

### The 10-foot UI (TV, consoles, couch PC)

Players sit about 2.5 to 3 metres from a TV and use a controller.

| Rule | Value |
|---|---|
| Minimum text height at 1080p | About 28 to 32 px for body (estimate); 24 px is a floor for secondary text; scale up for 720p handheld modes is not needed because the screen is small but close |
| Contrast | At least 4.5:1 for text, 3:1 for icons; TVs vary, so prefer more |
| Navigation | Every element focusable; clear focus highlight (not colour alone); focus moves in the direction pressed; wrap-around only where expected |
| Cursor | None. Do not need a mouse for any flow |
| Density | Fewer items per screen; larger rows; no hover tooltips (show details on focus) |
| Text entry | Use the platform on-screen keyboard (Steam: the Steamworks keyboard API; consoles: system keyboard) |
| Text length | Short; avoid paragraphs; subtitles on by default for story games |
| Confirmation | Large buttons; avoid timed prompts |
| Background | Keep HUD within title-safe region; do not rely on corners |

Test on a real TV at distance, not on a monitor. A fast check: view a screenshot at 1920x1080 from across the room.

### Handheld

Handheld modes (Switch, Steam Deck, ROG Ally-style PCs) are close-up on a small screen: text size minimums in section 8 apply. A UI that is perfect at 10 feet is often too sparse for handheld, and vice versa. Switch has two modes and display resolutions; plan layouts for both (Switch 1: 720p handheld, 1080p docked; Switch 2: 1080p handheld with higher TV output; `references/performance-tiers.md` section 6).

## 4. The PC settings menu players expect

PC players judge a game by its options menu. Ship these. A console release uses the same list minus window options, and consoles often expose fewer graphics choices.

### Display

| Setting | Detail |
|---|---|
| Window mode | Fullscreen (exclusive or borderless), borderless windowed, windowed (section 6) |
| Resolution | List native resolutions from the monitor; default to the desktop resolution; apply with a 15 second revert prompt if the player does not confirm |
| Monitor | Choose display; remember per display |
| Aspect handling | Show the supported aspect ratios; allow ultrawide where you can |
| Render scale | 50 to 150 percent slider, or a scaler list (see upscaling) |
| Upscaling | Offer a scaler such as bilinear, FSR, DLSS or XeSS where the engine supports them (check licence and engine integration, `technical-art`); show it as quality modes |
| Frame cap | Off, 30, 60, 90, 120, 144, 165, 240, and "match display"; capping saves battery and heat |
| V-Sync | On, off, adaptive; separate from the frame cap; note about input latency |
| FOV | 3D first and third person: slider about 60 to 120 degrees with default near 90 for first person (estimate); show the value |
| Brightness and gamma | A calibration screen for dark games; HDR options if supported |
| UI scale | Slider (section 2) |
| Safe area or margin | TV and handheld modes |

### Graphics

Presets: Low, Medium, High, Ultra (or Custom). Each preset sets individual options. Show a short description and a performance note. Auto-detect on first run from the GPU and VRAM; always let the player change it.

| Option | Typical choices |
|---|---|
| Texture quality | By VRAM; show a VRAM estimate bar |
| Shadows | Off to ultra; resolution and distance |
| Anti-aliasing | Off, FXAA, TAA, MSAA (engine dependent) |
| Effects, post-processing | Level; separate toggles for motion blur, depth of field, film grain, chromatic aberration, lens flare; each should have an off switch (also accessibility) |
| View distance and level of detail | Slider |
| Ambient occlusion, reflections, global illumination, ray tracing | Off to high; mark ray tracing as high-end |
| Particles | Level |

Include a **benchmark or preview**: a pause menu that applies the setting live, or a built-in benchmark scene that outputs average and 1 percent low frame rate. This also serves as test evidence (`optimize`).

### Controls

Bindings per device, sensitivity, invert, dead zones, hold or toggle, vibration, gyro (`references/input-and-controls.md` section 6).

### Audio

Master, music, effects, voice, ambient; mute when unfocused (default on); output device; dynamic range (night mode or compressed mix); subtitle and caption options; speaker or headphone mode if the mix supports it (`audio-direction`).

### Gameplay and accessibility

Difficulty, assist options, camera shake, screen flash reduction, subtitles with size, background and speaker names, colour-blind modes, text size, reduce motion, skip or hold alternatives for timed input, language, auto-save (frequency), tutorials and hints on or off.

### Other

Language, telemetry opt in or out (`legal-ethics` for consent), credits, reset settings, "apply" and "revert", controller test, credits, support links, version and build number (for bug reports), and save management (delete, copy, cloud status).

### Behaviour rules

1. Settings apply immediately where possible; heavy ones (resolution, renderer) show "Apply" with revert.
2. Settings persist locally per machine (not in cloud saves; section 5 in the saves reference).
3. The first-run experience selects sensible defaults: preset from hardware, language from OS, colour-blind setting from nothing (do not guess).
4. Every setting is reachable with keyboard, mouse and gamepad.
5. In-game pause menu exposes the settings, because players adjust while playing.
6. Do not require a restart to change language or the quality preset where avoidable; if a restart is needed, say so before and offer "restart now".

## 5. Focus loss, pause and interruptions

| Event | Desktop PC | Web | Mobile | Console |
|---|---|---|---|---|
| Window loses focus (alt-tab) | Pause single-player; mute or lower audio; release cursor and keys; throttle to about 30 fps or less in the background | `visibilitychange`, `blur`: pause; browsers throttle timers in background tabs to at least 1 s and may suspend; do not rely on timers | App background: autosave, pause, release audio focus | Platform suspend: save state; the system will terminate you if you do not respond in time |
| Minimise | As above | Tab hidden | Home or app switcher | Home button, suspend |
| Disconnect controller | Pause and prompt | Same | Same for external pads | Required by the platform: pause and prompt |
| Resume | Do not resume automatically on single-player; require a button to un-pause | Same | Same | Platform-defined; show pause menu |
| Sleep and wake | Pause, reconnect network, check clock changes | Same | Handle time jumps (timers, daily rewards) | Suspend and resume |
| Monitor change or resolution change | Re-apply safe area and layout, move window onto a visible display | Resize event | Rotation | Docked and undocked change (Switch) must rescale UI |
| Network loss | Pause online play or retry gracefully | Same | Same | Required handling on consoles |

Rules:

1. Pause on focus loss for single-player games; for multiplayer, do not pause but reduce load and show an away state.
2. Use the engine hook: Godot `NOTIFICATION_APPLICATION_FOCUS_OUT` and `_IN`, `NOTIFICATION_WM_WINDOW_FOCUS_OUT`, and `get_tree().paused`; Unity `OnApplicationFocus(bool)` and `OnApplicationPause(bool)`; web `document.visibilityState`.
3. On focus loss: stop rumble, release all inputs, lower audio (or pause it), release Pointer Lock, and stop time-based game logic. Keep rendering minimal.
4. Save on pause where a loss is plausible (mobile always; PC when idle for long).
5. Do not unpause automatically when focus returns on single-player; the player may have returned mid-sentence.
6. Handle clock changes: use monotonic time for gameplay, server time for rewards.

## 6. Window modes and display handling

| Mode | Behaviour | Pros | Cons |
|---|---|---|---|
| Exclusive fullscreen | Changes the display mode | Lowest latency on some systems; changes resolution | Slow alt-tab, monitor flicker, issues with overlays and multi-monitor |
| Borderless fullscreen (windowed fullscreen) | A borderless window at desktop resolution | Fast alt-tab, overlays work | Resolution is the desktop's unless you render scaled |
| Windowed | Normal window | Multitasking, dev | Needs a resizable layout and minimum size |

Default to borderless fullscreen on the primary monitor at the desktop resolution, with a render-scale option. On macOS, native fullscreen creates a Space and handles the notch; honour the OS setting. On Linux, support Wayland and X11 and test the Steam Deck's gamescope compositor (borderless full screen at 1280x800, handled by Steam).

Rules:

- Remember window position and size, and validate them against the connected monitors on start (a monitor may have been unplugged).
- Enforce a minimum window size; show a scrollable or scaled UI below that.
- Handle high-refresh displays: render at the display refresh (up to the frame cap), keep simulation on a fixed time step independent of frame rate (`game-architecture`). Many gameplay bugs appear at 144 Hz and 240 Hz when physics is frame-tied.
- Handle HDR and wide-gamut displays only if you tune for them; otherwise tone-map to sRGB.
- Multi-monitor: let the player choose the display; confine the cursor in fullscreen if the game uses edge scrolling.

## 7. Platform conventions

| Platform | Conventions players expect |
|---|---|
| iOS | Swipe from the left edge goes back in apps; games usually own gestures, so provide in-app back; respect silent switch for audio; Dynamic Type is optional for games; restore purchases button required for IAP (`store-release`); haptic taps; share sheet |
| Android | System back button or gesture closes or goes back, handle it (never ignore); status and navigation bars; notifications permission prompt; variety of aspect and densities; Play Games sign-in optional |
| Windows | Alt+Enter toggles fullscreen; Alt+F4 quits; the Windows key and overlay (Xbox Game Bar) must not break the game; tray and taskbar behaviours; Esc opens the pause menu; mouse cursor visible in menus |
| macOS | Cmd+Q quits; Cmd+, opens Settings (a convention); menu bar items (About, Settings, Quit, Window); Retina scaling; trackpad users (no right click assumed); notarisation prompts |
| Linux | Respect XDG paths; work in Wayland and X11; gamepad via SDL; Steam Runtime and Proton; do not assume a particular desktop |
| Steam Deck | Steam and Quick Access buttons are system-reserved; game must handle suspend and resume cleanly; touchscreen works as a mouse; gyro; back grips can be mapped; no mouse-only flows |
| Web | Back button and refresh can lose progress: warn or autosave; fullscreen via button; keyboard focus on the canvas; do not break browser shortcuts unless necessary; share links |
| Switch family | Home button and sleep; handheld versus docked resolution change; Joy-Con detach and reattach; touch screen in handheld; platform terminology and button names; no "Exit game" menu item (consoles typically suspend rather than quit); platform manual wins |
| PlayStation | System-level trophies, activities and PS button; consistent Circle or Cross preference; Create button for capture; terminology; no Exit item |
| Xbox | Achievements, Quick Resume (state survives suspend, so handle time jumps), Smart Delivery, View and Menu buttons; Series S as a floor; Xbox Accessibility Guidelines |

Console convention details and requirements belong to the platform holder; see `console-pathway`. Do not copy third-party requirement lists into a design; read the platform's own documentation under its agreement.

## 8. Minimum text and target sizes

| Context | Body text | Secondary or caption | Source or basis |
|---|---|---|---|
| Steam Deck (1280x800) | 12 px recommended | 9 px absolute minimum | Valve's Steam Deck Verified criteria (https://partner.steamgames.com/doc/steamdeck/compat) |
| PC at 1080p, monitor distance | 18 to 22 px | 14 to 16 px | Estimate from common practice |
| PC at 4K | Scale by the UI scale (about 150 percent) | | |
| TV at 1080p, 10 feet | 28 to 32 px | 24 px | Estimate |
| Phone | 14 to 16 pt for body, 12 pt minimum | | `mobile-ux` |
| Web | 16 CSS px for body | 12 CSS px floor | Common browser default |
| Touch targets | 44 pt (iOS), 48 dp (Android) | | Platform guidance (`mobile-ux`) |
| Mouse targets | At least 24 CSS px (WCAG 2.2 target size minimum for web pages); game UI usually larger | | https://www.w3.org/TR/WCAG22/ |
| Gamepad focus targets | Large rows; the focus highlight must be at least 2 px thick and 3:1 contrast against its neighbour | | Estimate |

Text contrast: at least 4.5:1 for normal text and 3:1 for large text and icons (WCAG 2.x). Do not use colour alone to convey state.

Text-fit rules: leave 30 to 40 percent extra width for translation (`accessibility-localization`); allow wrapping; avoid text baked into images; test the longest language (often German or Russian) and tall scripts (Thai, Arabic diacritics) at the minimum size.

## 9. Xbox Accessibility Guidelines as a checklist

Source: Microsoft's Xbox Accessibility Guidelines (XAG), https://learn.microsoft.com/en-us/gaming/accessibility/guidelines. The set is organised into numbered guidelines covering areas such as text display, contrast, input, difficulty, audio, communication and narration. Wording and numbering have changed between versions; read the current page before claiming conformance. The checklist below paraphrases the common areas in my own words. It is not a substitute for the original.

- [ ] Text: size is adjustable or large enough; has high contrast; has a background where it overlays art; does not rely on colour alone.
- [ ] Contrast: UI and gameplay-critical elements pass contrast; offer a high-contrast option or colour-blind support.
- [ ] Input: every action can be remapped; no input requires simultaneous multi-button chords without an alternative; hold and toggle options; timing tolerances adjustable; supports adaptive controllers and alternative input devices where the platform allows.
- [ ] Navigation: menus work with a single input method; focus is visible; no timed menu interactions.
- [ ] Difficulty: adjustable difficulty or assists; the player can change it during play without penalty.
- [ ] Audio: independent volume channels; captions for speech and meaningful sound effects with speaker names; visual or haptic equivalents for audio cues.
- [ ] Narration and screen reader: menus and key UI are read aloud where practical (use platform text-to-speech) and in-game text can be spoken.
- [ ] Motion and flashing: avoid flashing above safe thresholds; offer reduce motion and reduce flash options.
- [ ] Communication: text and voice chat have accessible alternatives, speech-to-text and text-to-speech where chat exists.
- [ ] Clarity: tutorials can be repeated; reminders and objectives are available on demand; settings are described.
- [ ] Testing: involve disabled players in playtests (`playtest`).

## 10. Game Accessibility Guidelines as a checklist

Source: https://gameaccessibilityguidelines.com/ (a community-maintained set with Basic, Intermediate and Advanced levels across motor, cognitive, vision, hearing, speech and general). The list below paraphrases the Basic-level themes; check the site for current wording.

**Motor**
- [ ] Allow controls to be remapped or reconfigured.
- [ ] Offer an alternative to hold, rapid repeat or simultaneous inputs.
- [ ] Do not make precise timing the only way to succeed; allow adjustable timing or an assist.
- [ ] Make interactive targets large enough and spaced.
- [ ] Support more than one input method (for example keyboard and gamepad).

**Cognitive**
- [ ] Offer a tutorial or practice; allow it to be repeated.
- [ ] Provide clear goals, a way to review them, and a hint system.
- [ ] Avoid sudden, unannounced changes of control or camera.
- [ ] Allow the player to save progress or to continue without penalty.
- [ ] Use plain language and consistent terminology.
- [ ] Provide an option to turn off or reduce time pressure.

**Vision**
- [ ] Use legible text size and offer larger text; high contrast with the background.
- [ ] Do not rely on colour alone; add shape, icon or text; offer colour-blind-safe palettes.
- [ ] Allow HUD scale and visibility options.
- [ ] Provide audio cues for important visual events where reasonable.

**Hearing**
- [ ] Subtitles for all speech, on by default for story-critical dialogue, with size and background options.
- [ ] Ensure no essential information is conveyed by sound alone; add a visual cue.
- [ ] Separate volume controls.

**Speech**
- [ ] Do not require voice input; provide a text or button alternative.

**General**
- [ ] Offer a sufficient difficulty or assist range.
- [ ] Avoid flashing and strobing; warn when unavoidable.
- [ ] Keep accessibility options in the first-run flow or easy to find from the start screen.
- [ ] Document the options on the store page and in the settings.

Scale of effort: the basic items cost little when planned at design time (a settings menu, subtitle system, remap layer, colour-independent UI) and a lot to retrofit. Treat the three as separate: legal and store requirements (varies by region; `accessibility-localization`, `legal-ethics`), platform guidelines (XAG), and community guidelines.

## 11. UX test matrix

| Check | Mobile phone | Tablet | PC desktop | Ultrawide | Steam Deck | TV console | Web |
|---|---|---|---|---|---|---|---|
| Layout at the target resolution | yes | yes | yes | yes | yes | yes | yes |
| Safe area honoured | yes | yes | n/a | n/a | n/a | yes | yes (mobile) |
| All text above the minimum | yes | yes | yes | yes | 9 px at 1280x800 | 10-foot test | yes |
| Navigation with the primary input | touch | touch | mouse and keyboard | mouse and keyboard | gamepad | gamepad | mouse and touch |
| Alternate input works | optional pad | optional pad | gamepad | gamepad | touch | none needed | gamepad optional |
| Focus loss and resume | yes | yes | yes | yes | suspend and resume | suspend and resume | tab hidden |
| Settings menu complete | reduced | reduced | full | full | full | reduced | reduced |
| Accessibility basics | yes | yes | yes | yes | yes | yes | yes |

Record the results in a playtest or UX report (`qa-testing`, `design-review`) and attach screenshots to `evidence/<FEATURE-ID>/`.
