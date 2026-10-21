# Mobile Interaction: Hands, Targets, Gestures, Safe Areas, Orientation and Interruptions

A phone game is played by a thumb on a small sheet of glass, held in a hand that is often also holding a coffee or a train strap, by someone who will be interrupted within minutes. This file turns that physical reality into rules you can check: the units and physical sizes that matter, how people hold phones and what that means for placement (thumb zones), touch-target sizing for menus and for game boards, a gesture vocabulary with recognition parameters and conflicts, safe areas around notches, islands, cutouts and the home indicator, orientation choice and rotation handling (including tablets and foldables), and the full interruption-and-resume contract. Each section ends in rules, a checklist, or engine-level code. Thresholds are platform minimums or studio starting points; confirm on the smallest and largest phones you support. The control-scheme layer (virtual sticks, skill clusters, swipe vocabularies) lives in `skills/mechanics-codex/references/11-mobile-input-control-schemes.md`; this file covers the interaction layer every screen shares.

## Contents

1. Units, densities and the physical finger
2. Holding postures and thumb zones
3. Touch targets: menus, HUDs and game boards
4. Gestures: vocabulary, recognition and conflicts
5. Safe areas, notches, cutouts and system gestures
6. Orientation, rotation, tablets and foldables
7. Interruptions and resumption
8. Feedback at the point of touch
9. One-hand play audit (procedure and checklist)
10. Volatile facts (as of Oct 2026, verify before relying)

---

## 1. Units, densities and the physical finger

### 1.1 Logical units

| Platform | Logical unit | Pixels per unit | Notes |
|---|---|---|---|
| iOS / iPadOS | point (pt) | scale factor 2 or 3 (`@2x`, `@3x`) | Physical size of 1 pt varies a little by device (pixel density ÷ scale) |
| Android | density-independent pixel (dp) | density ÷ 160: mdpi 1.0, hdpi 1.5, xhdpi 2.0, xxhdpi 3.0, xxxhdpi 4.0 | Text uses `sp`, which also scales with the user's font-size setting |
| Godot | viewport pixels of the base resolution, scaled by the stretch settings | depends on `display/window/stretch/*` and `content_scale_factor` | See `layout-typography-and-review.md` §6 |
| Unity uGUI / UI Toolkit | reference-resolution pixels | depends on Canvas Scaler / Panel Settings | See `layout-typography-and-review.md` §7 |

Treat pt ≈ dp ≈ 1/160 inch for planning (so 1 mm ≈ 6.3 pt). When you know the device exactly, compute the real size:

```
physical_mm = logical_units × scale / ppi × 25.4
example: 44 pt on a 460 ppi @3x phone → 44 × 3 / 460 × 25.4 ≈ 7.3 mm
```

`scripts/ui_audit.py units --px 132 --scale 3 --ppi 460` does this arithmetic and reports whether the size clears 44 pt and 48 dp.

**The engine trap.** Game engines lay out in a design resolution (for example 1080×1920) and scale to the screen. A button that is 120 design pixels tall is about 40 pt on a 393-pt-wide phone if the 1080-pixel width maps to 393 pt (120 × 393 / 1080 ≈ 44). Always convert design pixels to points on the narrowest supported phone before you sign off a size. Formula:

```
pt_on_device = design_px × (device_width_pt / design_width_px)      # width-matched scaling
```

### 1.2 The finger

- Fingertip contact patches are commonly cited at roughly 8–10 mm for a deliberate tap, larger for a thumb pad and for fast, imprecise taps. Treat these as order-of-magnitude planning numbers, not measurements of your audience.
- **Occlusion.** The finger hides what it touches. Feedback that matters (a selected tile, a drag ghost, a value being set) must appear outside the finger: above it in portrait, and towards the screen centre near edges.
- **Touch offset.** People aim slightly below the visual centre of small targets, and their perceived touch point differs from the sensor's contact centroid. Expand hit areas downward slightly for small top-of-screen targets, and test with real hands.
- **Edges and corners are less accurate.** Steven Hoober's observational work on touch accuracy (UXmatters, 2013 onward) reports that taps are most accurate in the centre of the screen and less accurate near the top and bottom edges, so edge targets need more size or more spacing. Treat any single millimetre figure as approximate.

### 1.3 Fitts's law, applied

Movement time to hit a target grows with distance and shrinks with target size. A common formulation (MacKenzie's Shannon form, 1992) is:

```
MT = a + b × log2(D / W + 1)
D = distance from the thumb's resting point to the target centre
W = target width along the axis of motion
a, b = empirical constants per device and posture
```

What it means for games:

- Halving the distance helps exactly as much as doubling the width. Put the most frequent actions near where the thumb rests (bottom centre in portrait, bottom corners in landscape).
- Screen edges are "infinitely deep" for a mouse but **not** for touch. A finger overshoots the glass edge and lands on the bezel or the OS gesture zone. Never rely on edge-pinning on phones.
- Repeated actions (spawn, attack, merge-tap) are hit hundreds of times per session. A 20% cut in movement time on a repeated action is worth more than any menu redesign.

---

## 2. Holding postures and thumb zones

### 2.1 Postures

Hoober's observational study of 1,333 people using phones in public ("How Do Users Really Hold Mobile Devices?", UXmatters, 2013) reported roughly 49% one-handed use, 36% cradled (held in one hand, tapped with the other hand's thumb or finger) and 15% two-handed. People switch grip constantly, often within one session, depending on what they are doing and where they are. Phones have grown since then, which makes the one-handed top of the screen harder still.

Game implications:

| Posture | When it happens in games | Design for it |
|---|---|---|
| One-handed portrait | Commute, queue, lying down, casual and puzzle games, idle check-ins | All core actions in the bottom ~40%; nothing frequent in the top corners |
| Cradled | Careful puzzle play, menus, shop browsing | Whole screen reachable; precision higher; still keep primaries low |
| Two thumbs, landscape | Shooters, MOBA, racing, action RPG | Bottom-left = movement, bottom-right = actions; top centre = information only |
| Two thumbs, portrait | Fast arcade, some runners, typing | Bottom corners easy, centre top hard |
| Phone on a table | Idle, auto-battlers, long strategy sessions | Precision taps anywhere; larger text helps at arm's length |

### 2.2 Zone maps

The zone maps popularised by Hoober (2013) and by Josh Clark (*Designing for Touch*, 2015) divide the screen into easy, stretch and hard regions. A practical heuristic version for a right-handed one-thumb grip in portrait (mirror it for left hands):

```
 ┌─────────────────────────┐
 │ HARD        HARD  STRETCH│  top 25%: information only (currencies, timers, progress)
 │ HARD       STRETCH STRETCH│  25–45%: secondary actions on the grip side only
 │ STRETCH   STRETCH  STRETCH│  45–60%: occasional actions
 │ EASY       EASY     EASY │  bottom 40%: primary and frequent actions
 │ EASY       EASY  stretch │  the corner right under the thumb base is cramped
 └─────────────────────────┘
```

Landscape, two thumbs:

```
 ┌───────────────────────────────────────────┐
 │ hard          HARD (info only)        hard │
 │ STRETCH                            STRETCH │
 │ EASY (move)                   EASY (act)   │
 └───────────────────────────────────────────┘
```

`scripts/ui_audit.py layout` encodes these maps (hands `right`, `left`, `either`, `two`, `cradle`) and flags primary or high-frequency controls placed in stretch or hard zones. Use `either` when you do not know the player's hand; it takes the worse of the two one-hand maps, which keeps primaries centred and low.

### 2.3 Placement rules

| Element | Zone (portrait, one hand) | Rationale |
|---|---|---|
| Primary call to action ("Play", "Battle", "Claim") | Bottom centre, easy | Hit most often; must work for either hand |
| Repeated in-game action (spawn, jump, fire) | Bottom centre or bottom grip-side, easy; 60–90 pt | Hundreds of hits per session |
| Navigation tab bar | Bottom edge, above the home-indicator inset | Platform convention; reachable |
| Currencies, timers, level progress | Top, hard zone is fine | Read, rarely tapped; the "+" opens the shop |
| Settings, mail, profile | Top corners | Rare; hard reach discourages accidental taps |
| Event and offer rails | Side edges in the stretch zone | Visible, secondary; keep away from primaries |
| Destructive actions (sell, delete, spend premium) | Not in the easiest spot; behind a confirm | Slips must not cost anything |
| Close / dismiss on pop-ups | Top-right *and* a clear bottom "Close"/"Not now" button, or tap-outside | The top-right X is a stretch for right-handers and a hard reach for left-handers |

**Reachability is not your fix.** iOS Reachability and Android one-handed modes exist, but few players use them while gaming. Design so they are never needed.

### 2.4 Worked example: is the top-left "Back" button a problem?

A 6.7-inch phone, 430×932 pt logical. A right-handed one-thumb player taps "Back" in a top-left corner 16 pt from each edge, about 20 times a session while moving between the meta screens.

- Zone: top 25% and far side → hard. Each tap needs a grip shift or a second hand.
- Fix: add the platform back gesture or button (Android system back; an edge swipe on iOS where it does not conflict with gameplay), make the bottom tab bar the main navigation, and keep "Back" top-left only as a secondary affordance that matches platform convention.
- Check: `ui_audit.py layout --spec home.json` with `hand: "either"`. The only top-corner touch targets should be low-frequency (settings, profile).

---

## 3. Touch targets: menus, HUDs and game boards

### 3.1 Minimums and starting points

| Control | Minimum | Studio starting point | Source |
|---|---|---|---|
| Any tappable control | 44×44 pt (iOS), 48×48 dp (Android) | Use the larger (48) for cross-platform UI | Apple HIG; Material Design |
| Web-style UI (WCAG) | 24×24 CSS px (2.5.8, AA); 44×44 (2.5.5, AAA) | Treat the AAA figure as your baseline | WCAG 2.2 |
| Primary in-game action | — | 60–90 pt diameter | Studio heuristic (struck blind, mid-motion) |
| Gap between adjacent targets | 8 pt / 8 dp | 8–12 pt; 16 pt between a spend/destroy control and anything else | Material spacing guidance; studio heuristic |
| Close button on a modal | 44 pt | 44 pt plus a text button or tap-outside | Anti-dark-pattern rule |
| Slider thumb | 44 pt | 44 pt, with the track inset from the screen edge by ≥ 16 pt | Edge gestures |
| List rows (inventory, mail) | 44 pt tall | 56–72 pt with icon + text | Readability and fat-finger tolerance |

The visual can be smaller than the hit area. A 24-pt icon can sit in a 48-pt hit rectangle. In Godot, give the `Control` a `custom_minimum_size` larger than its texture (or wrap the icon in a larger transparent `Button`/`TextureButton`). In Unity uGUI, enlarge the raycast area with a transparent raycast-target `Image` parent, or use the `Image`'s raycast padding where your uGUI version supports it (verify the property in your version).

### 3.2 Game boards and grids

Boards rarely hit 44 pt per cell on narrow phones. Compute the cell size first, then choose an input model that tolerates it.

```
cell_pt = (safe_width_pt − 2 × board_margin_pt − (cols − 1) × gutter_pt) / cols

375-pt phone, 9 columns, 12-pt margins, 2-pt gutters:
cell = (375 − 24 − 16) / 9 ≈ 37.2 pt          → below 44
393-pt phone, 8 columns, 12-pt margins, 2-pt gutters:
cell = (393 − 24 − 14) / 8 ≈ 44.4 pt          → OK
```

| Cell size | What to do |
|---|---|
| ≥ 44 pt | Direct tap and drag are fine |
| 36–44 pt | Swipe input that reads the swipe direction rather than the exact end cell (match-3 standard); nearest-centre hit testing; slop ≥ 8 pt; highlight the cell under the finger, offset above it |
| 28–36 pt | Tap to select then tap to act; zoom or "magnifier" on press; reduce columns or add a landscape/tablet layout |
| < 28 pt | Redesign: fewer columns, scrolling board, or pinch-zoom with a minimum zoom that keeps cells ≥ 36 pt |

Hit testing for dense grids: resolve the touch to the cell whose centre is nearest, not the cell whose rectangle contains the raw point. Bias towards the cell the player last interacted with when the touch lands within 20% of a boundary.

### 3.3 Crowding and the "danger neighbour" rule

- Never put a spending or destructive control within 16 pt of a primary or close control. A slip must never buy, sell, or delete. `ui_audit.py layout` flags this as `DANGER_ADJACENT`.
- Premium-currency purchases from the HUD (for example "+5 moves for 900 coins") need a second tap or a hold-to-confirm, *unless* the cost is soft currency, the action is reversible, and the price is shown on the button.
- Two primary buttons side by side ("Claim" and "Claim ×2 with ad") must be visually distinct and spaced. The free option must be a real button, not grey link text.

---

## 4. Gestures: vocabulary, recognition and conflicts

### 4.1 Vocabulary

| Gesture | Discoverability | Typical game use | Recognition starting values | Main conflicts |
|---|---|---|---|---|
| Tap | Obvious | Select, confirm, fire, spawn | Fire on touch-down for timing-critical actions, on touch-up for menus (allows cancel by sliding off) | Double-tap delays single-tap |
| Double-tap | Hidden | Zoom, special move | ≈ 300 ms window | Adds ~300 ms latency to every single tap on that element |
| Long-press | Hidden | Inspect, tooltip, drag start, charge | 250–500 ms; show progress after ~150 ms | Scrolling lists |
| Swipe (directional) | Medium with a hint | Match-3 swap, runner lanes, card throw | Distance ≥ 20–40 pt or velocity threshold; direction by dominant axis; tolerance cone ±30–40° | OS edge gestures; scroll views |
| Drag | Medium | Merge, place, aim, slingshot | Slop 6–12 pt before a drag starts | Scroll, pan camera |
| Pinch | Learned | Zoom map or board | Two pointers; scale from distance ratio; clamp | Two-finger swipes |
| Two-finger rotate | Hidden | Rotate camera or piece | Angle threshold ≈ 10° before rotating | Pinch |
| Hold-and-release | Medium | Charge shots, timing games | Show the charge meter on the finger's side, not under it | Long-press menus |
| Edge swipe | Reserved | **Do not use for gameplay** | — | iOS home/back, Android back/home |
| Tilt / gyro | Hidden | Steering, aim fine-tuning | Always optional, with a calibration and an off switch | Lying down, motion sickness |

Rules:

1. **Every hidden gesture has a visible alternative.** Long-press to inspect also has an info button. Double-tap to zoom also has a zoom control or pinch.
2. **Teach gestures by doing**, with an animated hand at the exact spot, the first time they are needed (`onboarding-ftue-ux.md` §3).
3. **One gesture, one meaning per context.** If swipe means "swap" on the board, it cannot also mean "open the side menu" near the board.
4. **Cancel is a gesture too.** Dragging back to the origin, or off the target, cancels; show a cancel zone for aim and skill-drag schemes.
5. **Multi-touch ownership.** Each control owns the pointer id that started on it. Lifting one finger must never release another control.
6. **Accessibility.** Provide tap alternatives for swipe/drag core verbs (tap-tap swap in match-3, for example) and hold-to-toggle for holds (`accessibility-localization`).

### 4.2 Drag-and-drop anatomy (merge, inventory, placement)

| Phase | Feedback | Timing |
|---|---|---|
| Press | Item scales up 5–10%, haptic tick | Immediately on touch-down |
| Drag start (past slop) | Item lifts, shadow appears, ghost drawn ~40–60 pt above the finger so it stays visible | Within 1 frame of passing slop |
| Hover valid target | Target highlights; merge preview shows the result tier | Within 1 frame |
| Hover invalid target | Neutral, or a soft red outline; never a sound per frame | — |
| Drop valid | Snap with an ease-out (80–150 ms), haptic, result VFX | — |
| Drop invalid / cancel | Item flies back to origin (150–250 ms) | — |
| Auto-scroll | When dragging within ~48 pt of a scroll edge, scroll at a speed proportional to depth | — |

### 4.3 Camera gestures (maps, bases, boards)

- One-finger drag pans; two-finger pinch zooms; rotation only if the game needs it (most mobile strategy games lock rotation).
- Clamp the camera so the playfield cannot be lost; rubber-band at the limits; add inertia with friction (decay to rest over about 300–600 ms).
- Distinguish tap from pan with slop; a pan that started on a building must not also tap it on release.
- Provide a "re-centre" button whenever the player can scroll away from the main object.

---

## 5. Safe areas, notches, cutouts and system gestures

### 5.1 Anatomy

| Intrusion | Where | Behaviour |
|---|---|---|
| Status bar | Top (portrait) | Hidden in most full-screen games; still part of the top inset on some devices |
| Notch or Dynamic Island (iOS) | Top centre in portrait; left or right side in landscape | Content behind it is invisible; the island also shows live activities |
| Punch-hole and notch cutouts (Android) | Top (centre, left or right), sometimes corners | Reported through the display-cutout API |
| Rounded display corners | All four corners | Corners clip content; a square HUD element in the corner loses pixels |
| Home indicator (iOS) | Bottom strip | Swipes from it go home or switch apps |
| Gesture navigation bar (Android) | Bottom strip; back gestures from both side edges | Swipes go home/back; side-edge swipes trigger back |
| Foldable hinge / fold | Middle of the screen | Posture-dependent; see §6.4 |

Typical portrait insets on recent iPhones are on the order of 47–62 pt at the top and 34 pt at the bottom, and they differ per model and orientation. **Read insets at runtime; never hardcode them.**

### 5.2 Rules

1. **Backgrounds bleed, content respects.** Art, colour fields and the playfield background extend under every inset. Interactive controls and critical information (score, timer, moves) stay inside the safe area.
2. **Add a margin inside the safe area.** 8–16 pt between the safe-area edge and any control, more in corners because of rounded displays.
3. **Landscape insets are asymmetric.** The notch moves to one side and flips when the player rotates the phone 180°. Re-layout on every orientation change, and support both landscape directions.
4. **Keep the home-indicator strip free of controls.** On iOS you can ask the system to defer edge gestures (`preferredScreenEdgesDeferringSystemGestures`), so the first swipe only reveals the indicator. Use that for action games where accidental exits hurt, not as a licence to put buttons there.
5. **Respect Android gesture navigation.** Do not start game gestures within about 16–24 pt of the left and right edges. If gameplay must use edges (a vertical slider at the screen edge), request system-gesture exclusion rectangles; the system caps how much it honours per edge (see `mechanics-codex` input notes).
6. **Immersive mode is a choice.** Hiding system bars gives space but adds swipe-to-reveal behaviour; test that revealing them does not pause or break input.
7. **Design at the extremes.** The tallest-narrowest phone, the shortest-widest phone, a tablet, and a device with a corner punch-hole.

### 5.3 Engine implementation

Godot 4 (statically typed GDScript): a container that pads its children to the safe area. Attach to a full-rect `MarginContainer` at the root of each UI scene.

```gdscript
extends MarginContainer
class_name SafeAreaMargin

@export var extra_margin: int = 12   # inner margin in viewport units

func _ready() -> void:
	get_viewport().size_changed.connect(_apply)
	_apply()

func _apply() -> void:
	var window_size: Vector2 = Vector2(DisplayServer.window_get_size())
	var safe: Rect2i = DisplayServer.get_display_safe_area()
	var vp_size: Vector2 = get_viewport_rect().size
	if window_size.x <= 0.0 or window_size.y <= 0.0:
		return
	# Convert screen pixels to viewport units (the stretch mode may scale the UI).
	var sx: float = vp_size.x / window_size.x
	var sy: float = vp_size.y / window_size.y
	var left: int = int(safe.position.x * sx) + extra_margin
	var top: int = int(safe.position.y * sy) + extra_margin
	var right: int = int((window_size.x - safe.end.x) * sx) + extra_margin
	var bottom: int = int((window_size.y - safe.end.y) * sy) + extra_margin
	add_theme_constant_override("margin_left", left)
	add_theme_constant_override("margin_top", top)
	add_theme_constant_override("margin_right", right)
	add_theme_constant_override("margin_bottom", bottom)
```

Notes: `get_display_safe_area()` reports in screen coordinates; on some platforms and window modes the window origin is not the screen origin, so verify on device. `DisplayServer.get_display_cutouts()` returns the cutout rectangles when you need to avoid a specific punch-hole rather than the whole inset band.

Unity (C#): a component on a full-stretch `RectTransform` under the canvas.

```csharp
using UnityEngine;

[RequireComponent(typeof(RectTransform))]
public sealed class SafeAreaFitter : MonoBehaviour
{
    private RectTransform _rect = null!;
    private Rect _lastSafe;
    private Vector2Int _lastSize;
    private ScreenOrientation _lastOrientation;

    private void Awake() { _rect = GetComponent<RectTransform>(); Apply(); }

    private void Update()
    {
        if (Screen.safeArea != _lastSafe || Screen.width != _lastSize.x ||
            Screen.height != _lastSize.y || Screen.orientation != _lastOrientation)
            Apply();
    }

    private void Apply()
    {
        Rect safe = Screen.safeArea;
        _lastSafe = safe;
        _lastSize = new Vector2Int(Screen.width, Screen.height);
        _lastOrientation = Screen.orientation;
        if (Screen.width <= 0 || Screen.height <= 0) return;
        Vector2 min = safe.position;
        Vector2 max = safe.position + safe.size;
        min.x /= Screen.width;  min.y /= Screen.height;
        max.x /= Screen.width;  max.y /= Screen.height;
        _rect.anchorMin = min;
        _rect.anchorMax = max;
        _rect.offsetMin = Vector2.zero;
        _rect.offsetMax = Vector2.zero;
    }
}
```

Unity also exposes `Screen.cutouts`. In the Device Simulator you can preview safe areas for many phones; still test on hardware.

### 5.4 Safe-area test matrix (minimum)

| Device class | Why |
|---|---|
| Small iPhone without notch (home button era, if supported) | Smallest logical width; no insets |
| Notch or Dynamic Island iPhone, portrait and both landscapes | Asymmetric landscape insets |
| Android with centre punch-hole, gesture navigation on | Back-gesture edges, bottom gesture bar |
| Android with corner punch-hole | Corner HUD collisions |
| Tall 20:9 or 21:9 Android | Vertical stretch of layouts |
| Tablet (iPad and Android 600dp+) | Wide layouts, letterboxing choices |
| Foldable, folded and unfolded | Aspect change at runtime |

---

## 6. Orientation, rotation, tablets and foldables

### 6.1 Choosing orientation

| Factor | Portrait | Landscape |
|---|---|---|
| Hands | One hand works | Two thumbs |
| Sessions | Micro-sessions, commute, multitasking | Longer, deliberate sessions |
| Genres (market pattern) | Puzzle, match-3, merge, idle, hybrid-casual, card battlers, many RPG metas | Shooters, MOBA, racing, fighting, many action RPGs |
| Readability | Tall boards, vertical lists, chat | Wide fields of view, side-by-side panels |
| Marketing | Matches vertical video ad formats | Needs letterboxed or re-cut creatives |
| Tablet fit | Leaves wide empty sides unless you design a wide layout | Natural on tablets |

Decide with the core verb: if the core action can be done with one thumb, ship portrait. If it needs two simultaneous inputs (move and aim), ship landscape. "Both" doubles UI layout and QA cost; choose it only when the audience demands it (tablet-heavy kids' games, some strategy games).

Record the decision in `config.orientation` and `contract.meta.orientation` (`portrait|landscape|both`).

### 6.2 Rotation handling

- Portrait games: lock to portrait (and usually allow upside-down on tablets only).
- Landscape games: support landscape-left **and** landscape-right; the notch side flips, so re-apply safe areas.
- "Both": re-layout from scratch on rotation (anchors and containers, not hand-placed coordinates), preserve scroll positions and selection, pause action gameplay during the rotation, and never rotate mid-gesture.

### 6.3 Tablets and large screens

- **Do not just scale up.** Scaling a phone layout to a 12.9-inch tablet makes buttons huge and wastes space. Cap UI element growth (for example, buttons stop growing past 1.3–1.5× phone size) and use the extra area for content (bigger board, side panels, more visible inventory).
- **Letterbox deliberately.** If gameplay must keep a fixed aspect, fill the bars with art that matches the scene, never flat black, and keep HUD elements anchored to the safe area of the *screen*, not the letterboxed play area, unless the HUD belongs to the board.
- **Platform rules are changing (volatile).** Android 16 changes how orientation and resizability restrictions apply on large screens for apps targeting API 36, with an exemption for apps that declare themselves games (see §10). iPadOS window management also changed in recent releases. Verify current behaviour before relying on a locked orientation on tablets.

### 6.4 Foldables

- Treat unfold/fold as a runtime resolution change: re-layout, re-apply safe areas, keep game state.
- Avoid putting critical UI or the main gameplay focus on the fold line in half-folded postures.
- Test both the cover screen (often narrow) and the inner screen (near-square).

---

## 7. Interruptions and resumption

### 7.1 What interrupts a mobile game

| Interruption | Frequency | What the OS does | What the game must do |
|---|---|---|---|
| Notification banner | Very high | Usually nothing (app keeps focus) | Nothing, but avoid controls where banners land if a tap on the banner would cost the player |
| Notification shade / Control Center pull | High | Focus lost (resign active) | Pause real-time play |
| App switch / home | High | Background; may be killed later | Pause, save state, stop audio |
| Incoming call / alarm / Siri / voice assistant | Medium | Audio interruption, focus lost | Pause, release held inputs, resume audio only after the interruption ends |
| Screen lock / auto-lock | Medium | Background | As app switch; keep the screen awake only during active real-time play |
| OS permission dialog | Low (you cause it) | Focus lost | Never show one during action; pause beforehand |
| Low battery / thermal warning | Low | Overlay or throttling | Pause; offer a battery-saver mode (`mobile-performance`) |
| Process killed in background | Common on low-RAM Android | Cold start on return | Restore to a sensible state (§7.4) |
| Network loss | Common | — | Offline-tolerant core loop; queue server calls; never block single-player on network |
| Headphones disconnected | Low | Audio route change | Pause media-heavy moments; lower volume |

### 7.2 Lifecycle hooks by platform

| Layer | Focus lost / regained | Background / foreground | Back button |
|---|---|---|---|
| iOS (UIKit scenes) | `sceneWillResignActive` / `sceneDidBecomeActive` | `sceneDidEnterBackground` / `sceneWillEnterForeground` | No hardware back; edge swipe in navigation contexts |
| Android | `onPause` / `onResume` (multi-window: focus callbacks) | `onStop` / `onStart`; process may die after `onStop` | System back (button or gesture); predictive back on recent versions |
| Godot 4 | `NOTIFICATION_APPLICATION_FOCUS_OUT` / `_IN` | `NOTIFICATION_APPLICATION_PAUSED` / `_RESUMED` (mobile) | `NOTIFICATION_WM_GO_BACK_REQUEST`; set `application/config/quit_on_go_back` to false and handle it yourself |
| Unity | `OnApplicationFocus(bool)` | `OnApplicationPause(bool)`; `OnApplicationQuit` is unreliable on mobile | Android back arrives as Escape (legacy `KeyCode.Escape`, or the Input System's escape/back binding) |

iOS gives an app only a short window of background execution after it leaves the foreground, and Android may kill a stopped process at any time. **Save on focus loss, not on quit.**

### 7.3 The resume contract (rules)

1. **Auto-pause real-time play on focus loss.** Show a pause screen on return, with a large "Resume" button in the easy zone. For action games, resume with a 3-2-1 countdown (about 2–3 s total).
2. **Never punish an interruption.** No lost life, failed level, broken streak, expired booster or forfeited PvP match because a phone rang. For real-time PvP, give a reconnect grace window and a bot takeover rather than an instant loss.
3. **Save atomically on every focus loss.** Write to a temp file and rename; keep the previous save as a backup. Include mid-level state if levels last longer than about 60–120 s.
4. **Release all held inputs.** A held fire button or an in-progress drag is cancelled cleanly (the dragged item returns home).
5. **Timers use trusted time.** Energy, build timers and events use server time where available, otherwise wall-clock with monotonic sanity checks. Backgrounding must neither stop nor accelerate timers unfairly.
6. **Audio follows the OS.** Pause or duck on audio interruptions; resume music only after the interruption ends. Choose the iOS audio session category on purpose: `ambient` mixes with the player's own music and obeys the silent switch; `soloAmbient` (the default) stops other audio; `playback` ignores the silent switch, which is rarely right for a game. On iOS, `secondaryAudioShouldBeSilencedHint` tells you when another app's audio is playing, so you can mute your music and keep SFX. On Android, request audio focus and handle transient loss by ducking or pausing.
7. **Purchases survive interruption.** A purchase interrupted by an app switch (very common when the store sheet or a bank app opens) must complete on return, through the store's transaction listener (`monetization`).
8. **Turn-based and puzzle games need no countdown.** Return to exactly where the player was, with the board visible, no modal.
9. **Respect the 'come back later' moment.** If the player was away longer than a threshold (for example 30 minutes), show a short "welcome back" summary of what changed (timers finished, rewards ready) instead of dropping them into a paused fight.

### 7.4 Restore policy after process death

| State at kill | Restore to | Why |
|---|---|---|
| Meta screens (home, shop, inventory) | Home screen | Cheap; players expect it |
| Short level (< 60–120 s) in progress | Level start, attempt not charged | Restoring is costly; free retry is fair |
| Long level or run (> 2 minutes) | Exact mid-level state from the last checkpoint/snapshot | Losing minutes of play feels like a bug |
| Roguelite run between rooms | Start of the current room | Standard expectation |
| Purchase in flight | Home, then process pending transactions and grant | Store rules and trust |
| Async PvP turn being composed | Draft of the turn | Prevents accidental forfeits |
| Real-time PvP | Reconnect if the match is alive; otherwise a result screen that explains | Fairness |

### 7.5 Pause service sketch (engine-agnostic)

```
on focus_lost or app_paused:
    if state.realtime_active: sim.pause(); ui.show_pause(); input.release_all()
    audio.pause_or_duck()
    save.write_atomic(state.snapshot())          # include mid-level state if level_len > 90 s
    analytics.log("app_background", {screen, level_id, elapsed_sec})

on focus_regained or app_resumed:
    away = clock.now() - state.backgrounded_at
    timers.reconcile(trusted_now())
    purchases.process_pending()
    if away > WELCOME_BACK_SEC: ui.show_welcome_back(summary())
    elif state.realtime_active: ui.show_pause(countdown_on_resume=True)
    audio.resume_if_no_other_audio()
```

### 7.6 Worked example: a call during a 3-minute match-3 level

A player is 2 minutes into a level with 6 moves left and a booster active. A call comes in and lasts 4 minutes.

- Focus lost → board input released, music paused, snapshot saved (board, moves, booster state, RNG state), `app_background` logged.
- If the OS kills the app during the call, the cold start restores the level from the snapshot. A 2-minute level is long enough that restarting it would feel like a loss.
- Return → no countdown (turn-based), board visible, booster still active, moves unchanged. No "Are you sure you want to quit?" dialog.
- Playthrough test: inject a focus-loss event mid-level in the deterministic runner and assert the state is identical after resume (`qa-testing`).

---

## 8. Feedback at the point of touch

Every touch deserves an answer within one frame. The details of juice belong to `game-feel`; the interaction-level rules are:

| Rule | Starting value |
|---|---|
| Visual response to touch-down | Same frame (press state, scale 0.92–0.96, darken 10–15%) |
| Button release animation | 80–150 ms ease-out |
| Haptic on meaningful actions only | Light tick for selection; medium for confirm; heavy or a pattern for big rewards; none on scrolling |
| Disabled controls | Look disabled *and* explain on tap ("Unlocks at level 8") instead of doing nothing |
| Long operations | Spinner after ~300 ms; progress after ~1 s; never block the whole screen for a background save |
| Error on tap | Shake (2–3 cycles, ~200 ms) plus a reason; never a silent failure |
| Sound on UI | Short, quiet, varied (2–4 variants); respect separate music/SFX volumes |

Haptics and sound must have settings toggles (`game-ui-patterns.md` §9).

---

## 9. One-hand play audit (procedure and checklist)

### 9.1 Procedure

1. List every screen in `contract.ux.screens` and the five most frequent actions on each (from design intent, later from telemetry).
2. For each screen, write a layout spec (`ui_audit.py template --platform ios --hand either > home.json`, then edit rects to match the design).
3. Run `ui_audit.py layout --spec home.json` for iOS (393×852 pt and 375×667 pt) and Android (412×915 dp and a 360-dp-wide device). Fix every `major`.
4. Hold a real phone one-handed (both hands, in turn) and play the first 10 minutes without changing grip. Note every grip change.
5. Repeat in landscape for landscape games with two thumbs, and check that no control sits under a resting palm or in an edge-gesture zone.
6. Record findings as `playtest-report` findings (`severity`: blocker/major/minor/polish) and attach the screenshots as visual-gate evidence.

### 9.2 Checklist

- [ ] All touch targets ≥ 44 pt (iOS) / 48 dp (Android) on the smallest supported phone, measured in device units, not design pixels.
- [ ] Primary and repeated actions in the bottom 40% (portrait) or bottom corners (landscape); `ui_audit.py` shows no `THUMB_ZONE` majors.
- [ ] No spending or destructive control within 16 pt of a primary or close control.
- [ ] Every modal can be closed with a ≥ 44-pt control and a clear text option or tap-outside.
- [ ] Interactive and critical content is inside the runtime safe area in every supported orientation; backgrounds bleed.
- [ ] No game gesture starts in OS edge-gesture zones; the home-indicator strip is free of controls.
- [ ] Every hidden gesture has a visible alternative; core verbs have tap alternatives.
- [ ] Focus loss pauses real-time play, releases inputs, saves atomically; resume never costs lives, streaks or matches.
- [ ] Process death restores per the restore policy; purchases complete after interruption.
- [ ] Audio session and focus handling follow the OS; the player's own music can play if the design allows it.
- [ ] Tested on the device matrix in §5.4, including a foldable or tablet if supported.

---

## 10. Volatile facts (as of Oct 2026, verify before relying)

| Fact | Source |
|---|---|
| Apple HIG: give tappable controls a hit region of at least 44×44 pt. | https://developer.apple.com/design/human-interface-guidelines/accessibility |
| Material Design: touch targets at least 48×48 dp, separated by at least 8 dp. | https://m3.material.io/foundations/designing/structure (and Android accessibility docs: https://developer.android.com/guide/topics/ui/accessibility/apps) |
| WCAG 2.2: 2.5.8 Target Size (Minimum) 24×24 CSS px (AA); 2.5.5 Target Size (Enhanced) 44×44 CSS px (AAA). | https://www.w3.org/TR/WCAG22/ |
| Android: apps targeting API 35 are drawn edge-to-edge by default; targeting API 36 removes the edge-to-edge opt-out and ignores orientation/aspect-ratio restrictions on large screens (≥ 600 dp). | Android 15/16 behaviour changes: https://developer.android.com/about/versions/16/behavior-changes-16 ; summary: https://ecorpit.com/android-target-api-36-play-store-deadline-migration-2026/ |
| Apps that declare `android:appCategory="game"` are reported to be exempt from the Android 16 large-screen orientation and resizability override. (Background knowledge in the research notes; verify.) | https://developer.android.com/about/versions/16/behavior-changes-16 |
| From Aug 31, 2026, new Play apps and updates must target API 36 (extensions to Nov 1, 2026). | https://developer.android.com/google/play/requirements/target-sdk |
| Android system-gesture exclusion: `View.setSystemGestureExclusionRects`, with a capped amount honoured per vertical edge. | https://developer.android.com/reference/android/view/View |
| iOS: `preferredScreenEdgesDeferringSystemGestures` defers system edge gestures. | https://developer.apple.com/documentation/uikit/uiviewcontroller/preferredscreenedgesdeferringsystemgestures |
| Godot: `DisplayServer.get_display_safe_area()` and `get_display_cutouts()`. | https://docs.godotengine.org/en/stable/classes/class_displayserver.html |
| Unity: `Screen.safeArea`, `Screen.cutouts`. | https://docs.unity3d.com/ScriptReference/Screen-safeArea.html |
