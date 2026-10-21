# Input and controls

This reference explains how to map one set of game actions onto touch, mouse and keyboard, and gamepad, and how to set it up in Godot and Unity. It covers gamepad layouts and conventions, glyph swapping, dead zones, aim assist, rumble, rebinding, hold versus toggle, switching between devices, Steam Input, and the web Gamepad API and Pointer Lock. It ends with a worked action map that serves all three input families. Engine API names are given as of Godot 4.x and Unity Input System 1.x; verify against your installed version.

## Contents

1. The model: actions, not keys
2. Touch
3. Mouse and keyboard
4. Gamepad layouts and conventions
5. Dead zones, aim assist and rumble
6. Rebinding, hold versus toggle and input options
7. Last-used-device switching and glyphs
8. Steam Input
9. Web: Gamepad API, Pointer Lock, Fullscreen and keyboard
10. Godot setup
11. Unity setup
12. Worked example: one action map for touch, keyboard and gamepad
13. Input test checklist

## 1. The model: actions, not keys

Never read a physical key or button from gameplay code. Gameplay reads actions. A binding layer maps devices to actions.

```
device events -> bindings (rebindable, per control scheme) -> actions -> gameplay
                                                          -> UI navigation actions
                                                          -> glyph lookup (action -> icon for active device)
```

Rules:

1. Name actions after intent, not device: `move`, `aim`, `fire`, `jump`, `interact`, `pause`, not `space_pressed`.
2. Each action has a type: button (pressed, held, released), axis (one float), vector (two floats), or pointer (screen position).
3. UI has its own small action set: `ui_accept`, `ui_cancel`, `ui_up`, `ui_down`, `ui_left`, `ui_right`, `ui_page_prev`, `ui_page_next`, `ui_menu`. Gameplay and UI action sets are enabled and disabled as the game changes state.
4. Gameplay code reads processed values (dead zones applied, sensitivity applied). It never sees raw device values.
5. Keep sim and input separate. The sim consumes a per-tick command struct (`move: Vector2, aim: Vector2, buttons: bitmask`). Touch, mouse and gamepad all fill the same struct. This also makes replays and bots (`what-if`, `qa-testing`) possible.
6. Write the verb table first (from the contract, `verbs[].input`), then fill one column per input family. A verb with an empty cell is a design problem, not an implementation task.

Verb table template:

| Verb | Touch | Mouse and keyboard | Gamepad |
|---|---|---|---|
| move | left virtual stick or tap-to-move | WASD or arrows | left stick, d-pad |
| aim | right stick area or tap target | mouse position | right stick |
| primary action | right button, or tap | left mouse | right trigger or south face button |
| secondary | second button | right mouse | left trigger or west face button |
| interact | tap object | E | north or west face button (pick one and keep it) |
| pause | top-corner icon | Esc | Start or Menu |

## 2. Touch

Mobile layout, thumb zones and target sizes are owned by `mobile-ux`. This section covers the input layer only.

### Gesture vocabulary

| Gesture | Use | Notes |
|---|---|---|
| Tap | Select, confirm, fire | Accept if lift is within a slop radius (about 10 dp, an estimate) and shorter than about 300 ms |
| Long press | Context, hold-to-confirm | Show progress; 400 to 600 ms is a common range (estimate); never the only path to an action |
| Drag | Move, aim, scroll, drag-and-drop | Start drag after slop distance, so taps are not stolen |
| Swipe | Direction input, page change | Use velocity as well as distance; avoid conflict with OS edge gestures (back, home) |
| Pinch and rotate | Camera zoom | Optional; always provide a button alternative |
| Multi-touch | Move and aim at once | Track by touch index; two thumbs, no more than three active pointers in practice |

### Virtual controls

- **Floating stick**: appears where the thumb lands in the left half. Better than a fixed stick because thumbs vary. Use a dead zone of 10 to 15 percent of the radius (estimate) and a maximum radius of about 50 to 70 dp.
- **Fixed buttons**: place on the right edge within reach. Make touch areas larger than the drawn icon.
- **Release rules**: a touch that begins on a button belongs to that button until lift, even if it slides off. A touch that begins elsewhere must not trigger the button.
- **Show or hide** virtual controls automatically when a physical gamepad is used (section 7).
- **Auto-fire or auto-aim** reduces the need for precision; state it in the contract if you rely on it.
- **Cancel**: provide a way to cancel an aimed action (drag back to the origin, or drop on a cancel zone).
- **Haptics**: use short taps for confirmation, not continuous buzzing. Provide a settings toggle.

### Tap-to-act versus virtual stick

| Design | Use when | Avoid when |
|---|---|---|
| Direct manipulation (tap or drag the object) | Puzzle, strategy, card, builder | Fast action needing simultaneous move and fire |
| Virtual stick plus buttons | Action, platformer, shooter | Games needing pixel-precise aim |
| One-touch (tap or hold anywhere) | Endless runners, rhythm | Many verbs |
| Tilt or motion | Short novelty modes | Anything long; always offer an alternative |

## 3. Mouse and keyboard

Defaults to ship:

- Movement WASD plus arrow keys as an alternate. Support non-QWERTY layouts: bind by physical key position (scancode) for movement and by the typed character for text and shortcuts. Godot offers `physical_keycode`; Unity Input System binds to the physical key by default for `<Keyboard>/w` (layout-aware path syntax is available as `<Keyboard>/#(w)`; verify).
- Esc opens pause or backs out. Enter or Space confirm. Tab for menus or inventory if conventional.
- Mouse look: sensitivity slider, invert Y, raw input (no OS acceleration). Mouse wheel for zoom or weapon cycle. Provide side buttons as extra bindings.
- Never rely on right-click alone for a vital action (laptop trackpads), or on hover for essential information (touch and gamepad have no hover).
- Modifier keys: Shift, Ctrl, Alt must be rebindable; avoid Alt+Tab, Win and Cmd combinations the OS owns.
- Do not require number-row or keypad keys for key actions; French and other layouts place digits behind Shift.
- Support held-key repeat for menus (initial delay about 400 ms, repeat about 60 to 100 ms; estimates).
- macOS: use Cmd where players expect it (Cmd+Q, Cmd+, for settings), and the Ctrl-click right click.

Cursor behaviour:

| State | Cursor |
|---|---|
| Menu | Visible, free |
| Gameplay with mouse aim (third-person, FPS) | Hidden and captured (Pointer Lock on web) |
| Gameplay with mouse pointer (RTS, strategy) | Visible, confined to the window on fullscreen and multi-monitor |
| Pause | Released and visible |
| Focus loss | Released, game paused |

Always release the cursor on pause, on focus loss and when a text field takes focus.

## 4. Gamepad layouts and conventions

### Position naming

Name buttons by position, so one binding works on all pads: south, east, west, north (face buttons); left and right shoulder (bumpers); left and right trigger; left and right stick click; d-pad; start and select (menu and view/create/minus). Godot and SDL name buttons by position, with `JOY_BUTTON_A` meaning the south button. Unity gives `buttonSouth`, `buttonEast`, `buttonWest`, `buttonNorth`.

| Position | Xbox | PlayStation | Nintendo Switch |
|---|---|---|---|
| South | A | Cross | B |
| East | B | Circle | A |
| West | X | Square | Y |
| North | Y | Triangle | X |
| Left shoulder, trigger | LB, LT | L1, L2 | L, ZL |
| Right shoulder, trigger | RB, RT | R1, R2 | R, ZR |
| Stick clicks | LS, RS | L3, R3 | L stick click, R stick click |
| Menu | Menu (Start) | Options | Plus |
| View | View (Back) | Create (Share), touchpad | Minus |

### Confirm and cancel

- Xbox and PlayStation (Western release): confirm on south (A, Cross), cancel on east (B, Circle). Many Japanese releases on PlayStation use Circle to confirm and Cross to cancel, so PlayStation consoles let the player pick. On consoles, follow the platform setting where the SDK exposes it.
- Nintendo: confirm on the east button (A), cancel on the south button (B). Showing the Nintendo glyph at the right physical position is the point: the glyph says "A" but the button is on the right.
- Decide by the **platform the player is on**, not by the controller brand alone: Switch players expect A to confirm. On PC, default to the Xbox convention and show glyphs matching the connected pad. Provide a "swap confirm and cancel" option.
- Never put a destructive action on the same button as confirm in the same dialogue. Default focus on the safe choice.

### Layout conventions that players expect (action games)

| Control | Convention |
|---|---|
| Left stick | Move |
| Right stick | Camera or aim |
| South | Jump or confirm |
| East | Dodge, back, cancel |
| West | Interact, reload, secondary attack |
| North | Switch weapon, item, inventory |
| Right trigger | Fire, accelerate, primary attack |
| Left trigger | Aim, brake, block |
| Shoulders | Abilities, cycle |
| Stick clicks | Sprint (left), melee or crouch (right) |
| Menu | Pause |
| View | Map, scoreboard |
| D-pad | Quick items, emotes, menu navigation |

Two or three alternative presets (for example "Default", "Southpaw", "Legacy") are a low-cost accessibility win. Reserve Menu and View for system functions; do not bind gameplay to them.

### Other pad features

- **Touchpad, light bar, adaptive triggers, gyro (PlayStation)**; **gyro and HD rumble (Switch)**; **trigger rumble (Xbox)**. Treat them as optional extras. Gyro aiming as a fine-aim aid is widely liked on Steam Deck, Switch and PlayStation, with a toggle and sensitivity setting.
- Detect the number of players and the controller assigned to each. Handle disconnect by pausing and showing a reconnect prompt.
- Wireless pads can drop; do not treat disconnect as a quit.

## 5. Dead zones, aim assist and rumble

### Dead zones

Sticks rest slightly off zero and wear over time. Apply a dead zone to every stick.

| Type | Behaviour | Use |
|---|---|---|
| Axial | Each axis cut separately | Simple; causes sticky diagonals |
| Radial | Cut by vector length | Good for movement |
| Scaled radial | Radial cut, then rescale so output starts at 0 right after the zone | Default choice |

Scaled radial formula, with input vector `v`, inner dead zone `d_in`, outer zone `d_out`:

```
m = length(v)
if m < d_in: out = (0, 0)
else:
    m2 = clamp((m - d_in) / (d_out - d_in), 0, 1)
    out = normalize(v) * m2
```

Defaults (estimates): `d_in` 0.15 to 0.20 for gameplay, 0.25 for menus; `d_out` 0.95. Unity's Input System defaults to a stick dead zone of 0.125 minimum and 0.925 maximum in its settings. Expose a slider (0 to 0.5) because worn pads need a larger zone. Apply a response curve for aim: `out = normalize(v) * pow(m2, 1.5)` gives fine control near centre.

Trigger dead zone: 0.05 to 0.1 on analogue triggers; treat above about 0.5 as "pressed" for digital actions.

### Aim assist (gamepad shooters and action games)

Sticks are less precise than a mouse. Common assists, in order of increasing strength:

1. **Slowdown (friction)**: reduce look sensitivity when the reticle is over or near a target; 0.5 to 0.8 of normal speed (estimate).
2. **Stickiness**: keep the reticle on a target during small movement.
3. **Aim snap or soft lock** on trigger or aim-down-sights: pull aim toward the target's centre within a cone.
4. **Auto-aim** (hard lock) for casual or accessibility modes.

Rules: apply only for gamepad input, not mouse; keep the strength a setting (off, low, standard, high); in competitive multiplayer decide the policy deliberately, because cross-play between mouse and pad needs fairness (`multiplayer-backend`). Show a setting description so players understand it.

### Rumble and haptics

- Use two motors: low-frequency (heavy) and high-frequency (light). Short pulses (50 to 200 ms) for hits; avoid continuous rumble; battery and fatigue costs are real.
- Add intensity settings (off, low, medium, high) and an off switch. Rumble is not accessibility-neutral: some players find it painful. Do not rely on rumble as the only signal for any event.
- Phones: haptic engines vary widely on Android; use platform haptic APIs and test; fall back to nothing.

## 6. Rebinding, hold versus toggle and input options

### Rebinding

Ship rebinding on every platform where players use keyboards or pads; PC players expect it. Requirements:

- Per-action bindings for each device family (keyboard, mouse, gamepad); at least two slots per action on keyboard.
- Conflict handling: when a key is already used, offer swap or cancel; never silently steal. Allow conflicts across different action sets (menu and gameplay).
- Reserved keys: Esc and pause cannot be unbound; always keep a way to reset.
- "Reset to default" per action and for everything.
- Rebinding UI must itself work with the keyboard, mouse and pad. Press-to-listen with a timeout and an Esc cancel.
- Save bindings in the config (not the cloud saves; or in a separate cloud-safe file per control scheme, as keyboard bindings are portable but pad bindings are not).
- Show glyphs from the live bindings, not from a fixed image.

Godot: `InputMap.action_erase_events`, `InputMap.action_add_event`, serialise events to a config file. Unity: `InputAction.PerformInteractiveRebinding()`, `SaveBindingOverridesAsJson` and `LoadBindingOverridesFromJson`.

### Hold versus toggle

Provide a setting for every action that needs the finger held down for a long time: sprint, aim-down-sights, crouch, block, charge, cover. Both modes:

| Mode | Behaviour |
|---|---|
| Hold | Active while held |
| Toggle | Press once to start, again to stop |

Default to hold for brief actions, toggle for sustained ones when targeting accessibility. Also offer: "hold to confirm" duration adjustable or off; "press and hold" alternatives for button-mash prompts (auto-repeat); sticky modifiers; adjustable double-tap speed. Quick-time events and rapid presses need a "hold" or "skip" alternative (Game Accessibility Guidelines section in `references/platform-ux.md`).

### Other options worth shipping

Sensitivity (separate X and Y), invert Y, camera shake amount, stick swap, left-handed layout (touch), gyro toggle, vibration level, button size and opacity (touch controls), controls scheme presets, and an input test screen (shows live values, useful for support).

## 7. Last-used-device switching and glyphs

The game should show prompts for the device the player last used, and switch instantly when they touch another.

State machine:

```
active_scheme = KEYBOARD_MOUSE | GAMEPAD(kind) | TOUCH
on any key or mouse button/motion beyond a threshold -> KEYBOARD_MOUSE
on any gamepad button or stick beyond dead zone      -> GAMEPAD(kind of that device)
on any touch                                          -> TOUCH
emit scheme_changed(active_scheme) when it changes
```

Details:

- Ignore tiny mouse motion (under about 2 px per frame) and stick drift so a resting pad does not steal focus. Ignore device events that happen while the window is unfocused.
- On touch-capable laptops and phones with pads attached, last-used still wins.
- Show or hide virtual touch controls and mouse cursor by the active scheme.
- Menus: with a gamepad or keyboard, there must always be a focused element; with a mouse, hover focuses. Do not leave focus empty when switching to pad.
- Glyph lookup: `glyph(action, scheme)` returns an icon (or text) from the current binding. Maintain glyph sets for: keyboard keys, mouse buttons, Xbox, PlayStation, Nintendo, Steam Deck, and generic. Detect the pad kind from the device name or layout (Unity: `DualShockGamepad`, `XInputController` layouts, and the device `description.product`; Godot: `Input.get_joy_name(device)`; SDL naming is the fallback). If unsure, use Xbox glyphs on PC and text labels ("Confirm").
- Use icon fonts or SVG atlases, not text with brand logos. Controller glyph artwork has licences: Valve's Steam Input glyph sets can be used through the Steam Input API on Steam; Xbox, PlayStation and Nintendo glyphs are controlled by each platform holder on their consoles, and free glyph packs on PC vary in licence, so check before shipping (`legal-ethics`).
- Text strings must not hard-code a button name: use a placeholder such as `{action:interact}` resolved at run time, and localise the label.
- Console builds must use that console's own glyphs and terminology (for example the Switch calls clicks "press the A Button"); the platform manual lists requirements (`console-pathway`).

## 8. Steam Input

Steam Input lets Steam map any supported controller to your game and lets players share configurations. It matters most for Steam Deck, because Deck's own controls are exposed through it.

- **Do nothing** and Steam presents the pad as an XInput gamepad via its default layout. Games with proper gamepad support work out of the box.
- **Use the Steam Input API** (through Steamworks; Godot and Unity have community integrations, verify) to define actions and action sets in a game-actions file and get glyphs matching what the player sees. Valve recommends it for glyphs on Deck (`references/saves-and-platform-rules.md` section 6).
- Define a controller configuration in Steamworks: default layout for Xbox, PlayStation, Switch and Deck, plus the touch menu and gyro options. Test on real hardware or through Steam's controller configurator.
- The Deck verification review checks that the default configuration gives access to all content, glyphs match the active input, and text entry works with the controller (the on-screen keyboard through the Steamworks API).
- Do not stack your own rebinding UI on top without testing: two remapping layers confuse players. Provide in-game remap only for what Steam does not cover.
- Steam Input can emit keyboard and mouse events (desktop configuration). If you support pad natively, ship a pad default, not the keyboard emulation.
- Rumble and gyro pass through Steam Input; test them with the Steam overlay open and closed.

Store and release mechanics (Steamworks setup, builds) are in `pc-web-release`.

## 9. Web: Gamepad API, Pointer Lock, Fullscreen and keyboard

### Gamepad API

- `navigator.getGamepads()` returns a snapshot array; poll every frame (`requestAnimationFrame`). Events: `gamepadconnected` and `gamepaddisconnected`.
- Browsers expose a gamepad only after the user presses a button on it; a fresh page load may show none until then. Prompt: "Press any button on your controller".
- `gamepad.mapping === "standard"` means the standard layout: buttons 0 to 3 are south, east, west, north; 4 and 5 shoulders; 6 and 7 triggers; 8 view; 9 menu; 10 and 11 stick clicks; 12 to 15 d-pad (up, down, left, right); 16 home. Axes 0 and 1 are the left stick, 2 and 3 the right stick. Non-standard devices return empty mapping; provide a fallback or rely on the engine.
- Rumble: `gamepad.vibrationActuator?.playEffect("dual-rumble", { duration, strongMagnitude, weakMagnitude })`. Support varies; feature-detect.
- Identify the controller kind from `gamepad.id` for glyphs; it is a free-form string, so treat it as a hint.
- Gamepad input needs the page focused. iOS Safari and Android Chrome support external pads; test.
- Engines wrap this: Godot's web export maps pads through the same joypad API; Unity WebGL support for the Input System gamepads is limited, verify on the target browser.

### Pointer Lock

- `element.requestPointerLock()` must be called from a user gesture (click or key). Use `{ unadjustedMovement: true }` where supported for raw mouse motion.
- Listen to `pointerlockchange` and `pointerlockerror`. The browser always lets the player exit with Esc; treat exit as pause.
- While locked, read `movementX` and `movementY` from `mousemove`, not the position.
- Re-request after the player re-enters through a click, with a visible "Click to play" overlay.
- Not available on iOS Safari for iPhone; touch only there.

### Fullscreen and keyboard

- `element.requestFullscreen()` needs a user gesture; iPhone Safari does not offer element fullscreen (iPad does), so design for a browser-chrome viewport and use the PWA "add to home screen" option if you need it.
- Keyboard Lock (`navigator.keyboard.lock()`) is Chromium only and works in fullscreen; without it, Esc and OS shortcuts are not capturable.
- Prevent browser default on game keys (arrows, Space, Tab) with `preventDefault`, but only while the game canvas has focus, so form fields and accessibility tools still work.
- Audio is blocked until the first user gesture; use the first click or tap as an "unlock" and as the entry to fullscreen and pointer lock.
- Use pointer events (`pointerdown`, `pointermove`) for touch and mouse alike; set CSS `touch-action: none` on the canvas to stop scrolling and zoom gestures.
- Embedded in an iframe (portals): add `allow="fullscreen; gamepad"` attributes where the portal controls them (`pc-web-release`), and keep focus when the player clicks outside.

## 10. Godot setup

Actions live in Project Settings, Input Map, or are created in code.

```gdscript
# input_setup.gd  (autoload)  Godot 4.x
extends Node

enum Scheme { KEYBOARD_MOUSE, GAMEPAD, TOUCH }
signal scheme_changed(scheme: Scheme)
var scheme: Scheme = Scheme.KEYBOARD_MOUSE
var pad_kind: String = "generic"   # "xbox", "playstation", "nintendo", "generic"

func _ready() -> void:
    Input.joy_connection_changed.connect(_on_joy_changed)

func _input(event: InputEvent) -> void:
    if event is InputEventKey or (event is InputEventMouseButton):
        _set_scheme(Scheme.KEYBOARD_MOUSE)
    elif event is InputEventMouseMotion and event.relative.length() > 2.0:
        _set_scheme(Scheme.KEYBOARD_MOUSE)
    elif event is InputEventJoypadButton or (event is InputEventJoypadMotion and abs(event.axis_value) > 0.5):
        pad_kind = _kind_for(event.device)
        _set_scheme(Scheme.GAMEPAD)
    elif event is InputEventScreenTouch:
        _set_scheme(Scheme.TOUCH)

func _set_scheme(s: Scheme) -> void:
    if s != scheme:
        scheme = s
        scheme_changed.emit(s)

func _kind_for(device: int) -> String:
    var n := Input.get_joy_name(device).to_lower()
    if "playstation" in n or "ps5" in n or "ps4" in n or "dualsense" in n or "dualshock" in n: return "playstation"
    if "nintendo" in n or "switch" in n: return "nintendo"
    if "xbox" in n or "xinput" in n: return "xbox"
    return "generic"

func _on_joy_changed(_device: int, _connected: bool) -> void:
    pass  # show or hide a "controller disconnected" prompt here
```

Key API (Godot 4): `Input.get_vector("left", "right", "up", "down")` returns a vector with the action dead zones applied (a circular dead zone); `Input.get_axis`, `Input.is_action_pressed`, `Input.is_action_just_pressed`; `Input.start_joy_vibration(device, weak, strong, duration)` and `stop_joy_vibration`; `Input.vibrate_handheld(ms)` for phones; `Input.get_connected_joypads()`; `Input.mouse_mode = Input.MOUSE_MODE_CAPTURED` (also on web, as Pointer Lock) and `MOUSE_MODE_VISIBLE`. Per-action dead zone is a property in the Input Map (default 0.5, lower it to 0.2 for gameplay movement; verify default in your version). `InputEventScreenTouch` and `InputEventScreenDrag` carry the touch index. Project setting "Emulate Mouse From Touch" and "Emulate Touch From Mouse" help test touch on desktop. UI navigation uses the built-in `ui_*` actions and `Control.grab_focus()`; give every menu an initial focus target.

Gamepad button position constants: `JOY_BUTTON_A` is south on all pads (so on a Nintendo pad it is the physical bottom button, labelled B). If you want Nintendo-style confirm on Switch, bind `ui_accept` to `JOY_BUTTON_B` for that scheme (an option to swap is cheaper than detection).

Rebinding sketch:

```gdscript
func rebind(action: StringName, new_event: InputEvent, slot: int = 0) -> void:
    var events := InputMap.action_get_events(action)
    InputMap.action_erase_events(action)
    for i in events.size():
        InputMap.action_add_event(action, new_event if i == slot else events[i])
    if slot >= events.size():
        InputMap.action_add_event(action, new_event)
```

Save the event list (`event.as_text()` for display; serialise with `var_to_str(event)`) in the config file with `ConfigFile`.

## 11. Unity setup

Use the Input System package (not the legacy Input Manager) for new projects.

1. Create an Input Actions asset. Add action maps: `Gameplay`, `UI`. Add actions with types: `Move` (Value, Vector2), `Look` (Value, Vector2), `Fire` (Button), `Jump` (Button), `Interact` (Button), `Pause` (Button).
2. Add control schemes: `Keyboard&Mouse` (requires Keyboard and Mouse), `Gamepad` (requires Gamepad), `Touch` (requires Touchscreen). Add bindings under each action and assign each binding to schemes.
3. Add processors: `Stick Deadzone` on gamepad `Move` and `Look` bindings; `Scale Vector2` for sensitivity; `Invert Vector2` for invert Y.
4. Add interactions as needed: `Hold`, `Tap`, `MultiTap`, `Press` (press point and release behaviour).
5. Use `PlayerInput` (Behaviour: Invoke Unity Events, Send Messages or Invoke C Sharp Events) for simple projects and local multiplayer (`PlayerInputManager` joins players), or the generated C# class for code control.
6. Detect device changes: `PlayerInput.onControlsChanged`, with `playerInput.currentControlScheme` giving the active scheme name (auto-switch is on by default and flips when another device is used). For glyphs, `InputAction.GetBindingDisplayString(...)` and the control path give per-binding names.
7. UI: use `InputSystemUIInputModule` on the EventSystem and assign the UI action map. Set `firstSelected` on the EventSystem so pad navigation has focus.
8. Touch: on-screen controls (`OnScreenStick`, `OnScreenButton`) feed a virtual device so touch uses the same actions. `EnhancedTouch` (`EnhancedTouchSupport.Enable()`) gives raw touches for gestures.
9. Rumble: `Gamepad.current.SetMotorSpeeds(low, high)` and `ResetHaptics()`; stop on pause and focus loss. Gyro, touchpad and adaptive triggers need platform-specific code or packages.
10. Rebinding: `action.PerformInteractiveRebinding().WithControlsExcluding("<Mouse>/position").OnComplete(...).Start()`; save with `SaveBindingOverridesAsJson()` and load with `LoadBindingOverridesFromJson()`.
11. Mouse capture: `Cursor.lockState = CursorLockMode.Locked` and `Cursor.visible = false`; set back on pause.
12. Web (WebGL): check that the Input System version supports the target browser pads; test (verify).

Disable the map not in use: `playerInput.SwitchCurrentActionMap("UI")` when a menu opens, so gameplay does not fire under it.

## 12. Worked example: one action map for touch, keyboard and gamepad

Game: a top-down dungeon crawler that must play on phones (touch), PC (keyboard and mouse) and Steam Deck or consoles (gamepad). Verbs from the contract: move, aim-and-attack, dodge, use-potion, interact, pause.

### Step 1: verb table

| Action | Type | Touch | Keyboard and mouse | Gamepad |
|---|---|---|---|---|
| `move` | Vector2 | floating left stick | WASD, arrows | left stick |
| `aim` | Vector2 | right stick area (aims and fires while held) | mouse position relative to player | right stick |
| `attack` | Button | held with right stick; plus tap-to-attack button | left mouse | right trigger |
| `dodge` | Button | button, lower right | Space | east face button |
| `potion` | Button | button, above dodge | Q | west face button |
| `interact` | Button | tap on the object or button | E | north face button |
| `pause` | Button | top-right icon | Esc | Menu |
| `ui_*` | Buttons | tap | mouse click, arrows, Enter, Esc | d-pad, left stick, south, east |

Design choices: touch auto-fires while the right stick is held (precision is lower), so `attack` and `aim` merge there. Interact on touch is a tap on the world object plus a context button, so no extra button is permanent.

### Step 2: command struct

```
struct PlayerCommand { Vector2 move; Vector2 aim; bool attack; bool dodge_pressed; bool potion_pressed; bool interact_pressed; }
```

The sim reads only this. Each scheme's adapter fills it every tick.

### Step 3: engine mapping

Godot `project.godot` Input Map (names are the actions): `move_left` (A, Left, joypad axis -X), `move_right`, `move_up`, `move_down`, `aim_left` and so on (right stick), `attack` (left mouse, joypad axis 5 right trigger), `dodge` (Space, joypad button B which is east in the Godot naming used for the position, check labels), `potion` (Q, joypad X), `interact` (E, joypad Y), `pause` (Esc, joypad Start). Read: `var move := Input.get_vector("move_left","move_right","move_up","move_down")`. Touch: a `VirtualStick` Control script writes into the same action with `Input.action_press("move_left", strength)` or, cleaner, sets the command struct directly when `scheme == TOUCH`.

Unity: Input Actions asset with map `Gameplay` and schemes `Keyboard&Mouse`, `Gamepad`, `Touch`. `Move` (Value, Vector2): composite 2D Vector (WASD) in `Keyboard&Mouse`, `<Gamepad>/leftStick` with Stick Deadzone in `Gamepad`, `<Gamepad>/leftStick` bound by an `OnScreenStick` in `Touch`. `Attack` (Button): `<Mouse>/leftButton`, `<Gamepad>/rightTrigger` (Press point 0.5), `<Gamepad>/rightStick` as an `OnScreenStick` area's button counterpart. Read with `playerInput.actions["Move"].ReadValue<Vector2>()`.

### Step 4: scheme switching behaviours

| On switch to | Show | Hide | Focus |
|---|---|---|---|
| Touch | virtual stick, buttons; tap prompts | cursor, key glyphs | none (touch) |
| Keyboard and mouse | cursor, key and mouse glyphs | virtual controls | hover focus |
| Gamepad | pad glyphs (kind from device) | cursor, virtual controls | restore last focused menu item |

Aim: on mouse, aim is the vector from the player to the cursor; on pad, the right stick; if the right stick is idle for 0.5 s keep the last direction (do not snap to zero).

### Step 5: acceptance tests

1. Play a full level with each scheme alone. Record in the playtest report (`qa-testing`).
2. Swap devices mid-level: glyphs change within one frame; no stuck input (a held key or a stick direction continues after switch is the common bug; release all actions on switch).
3. Unplug the pad during play: game pauses and shows a prompt. Re-plug: focus returns.
4. Rebind `dodge` on keyboard to a mouse side button, restart, confirm persistence.
5. Hold versus toggle for `attack`: both pass the same tests.
6. Dead zone slider at 0.5: character can still be moved at full stick.

## 13. Input test checklist

- [ ] Every verb has a binding for every input family in `meta.input`.
- [ ] No gameplay code reads physical keys directly (grep).
- [ ] Menus fully navigable with each family; initial focus set; Esc or east button backs out.
- [ ] Glyphs and prompts follow the active device; no text says "Press E" on a pad.
- [ ] Rebinding works, persists, handles conflicts, has reset.
- [ ] Hold and toggle options exist for sustained inputs.
- [ ] Dead zones applied; stick drift does not move the character at rest or steal focus.
- [ ] Rumble and gyro have off switches; nothing depends on them.
- [ ] Focus loss, minimise and alt-tab release all keys and stop rumble.
- [ ] Cursor captured and released correctly; Pointer Lock exits cleanly on Esc (web).
- [ ] Touch: multi-touch works; touches that start on a button stay with it; no conflict with OS edge gestures.
- [ ] Steam Deck: default config reaches all content with no mouse; text input opens the on-screen keyboard.
- [ ] Console: every flow including purchase and text entry works with the pad alone.
