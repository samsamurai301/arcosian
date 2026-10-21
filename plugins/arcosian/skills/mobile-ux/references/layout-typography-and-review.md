# Layout, Typography and UX Review

This file turns visual layout into checkable rules: type sizes and fonts for small screens, icon design and sizing, contrast and colour use, responsive layout across aspect ratios and tablets, engine recipes for UI scaling in Godot and Unity, and the two tools used at the end of design work: a heuristic UX review checklist and a set of UX acceptance criteria. Sizes are starting points in logical units (pt on iOS, dp and sp on Android, base-resolution pixels in engines); confirm on your smallest and largest supported devices with `scripts/ui_audit.py`. Interaction rules are in `references/mobile-interaction.md`; screen patterns are in `references/game-ui-patterns-and-onboarding.md`.

## Contents

1. Typography
2. Iconography
3. Contrast and colour
4. Responsive layout principles
5. Aspect ratios and tablets
6. UI scaling in Godot
7. UI scaling in Unity
8. Heuristic UX review checklist
9. UX acceptance criteria
10. Worked example: auditing a hub screen

---

## 1. Typography

### 1.1 Starting sizes (logical units)

| Role | Starting size | Notes |
|---|---|---|
| Body, descriptions, tooltips | 14 to 16 | Do not go below 12 for anything the player must read |
| Button labels | 16 to 18 | Semibold; centred; single line |
| Numeric readouts (currency, score) | 16 to 20 | Tabular (fixed-width) numerals avoid jitter while counting |
| Screen titles | 20 to 28 | One per screen |
| Display (reward, victory) | 32 and above | Short strings only |
| Legal and fine print | 11 to 12 | Still checked for contrast; keep necessary text out of fine print |

Check the physical result with `python3 scripts/ui_audit.py units --pt 14 --scale 3` and confirm on a real device at arm's length: a type size that looks fine on a monitor mockup is often too small in hand.

### 1.2 Rules

- **Fewer type styles.** A scale of five or six styles (display, title, body, label, caption, number) covers most games. Define them as tokens used by every screen.
- **Respect system text scaling** where the platform offers it (iOS Dynamic Type, Android `sp`). For game HUDs that cannot grow freely, provide an in-game text-size option and design containers that tolerate larger text on menus.
- **Line length:** keep paragraphs short; for body text a line of roughly 30 to 45 characters on a phone is comfortable. Break content into short blocks.
- **Line height:** around 1.2 to 1.4 times the font size for body; tighter for display.
- **Weights over sizes:** use weight and colour for hierarchy before adding sizes; limit to two or three weights.
- **Outline or shadow** for text over busy scenes. Prefer an outline or a scrim to relying on contrast against moving backgrounds.
- **Numbers:** group digits and abbreviate large numbers with a documented rule (for example thousands and millions suffixes) in one function, shared everywhere; localise separators.
- **Never bake text into images.** All text from string tables so it can be localised and scaled.

### 1.3 Font selection

| Need | Guidance |
|---|---|
| Body legibility | A humanist or neutral sans with open counters and good small-size rendering |
| Brand or display | A distinctive face for titles only; test every glyph you need, including digits and punctuation |
| Language coverage | Check glyph coverage for every shipped language (Latin extended, Cyrillic, Greek, CJK, Arabic, Hebrew, Thai, Devanagari) before choosing; plan fallback fonts per script |
| Licensing | Confirm the licence permits embedding in an app and in each shipped language; keep licence records |
| Size on disk | CJK fonts are large; subset to needed glyphs or use system fonts where quality allows; measure build size |
| Right-to-left | Mirror layouts, keep numerals and embedded Latin handled by the bidi algorithm; test with real strings |

### 1.4 Text expansion and fitting

- Translations often grow relative to English, with short strings growing proportionally more. Use `python3 scripts/ui_audit.py expansion --text "Collect reward" --max-chars 20` to see the budget a source string has.
- Design buttons and labels for the longest expected string, with one of: shrink-to-fit down to a minimum size, two-line wrapping, or an icon plus a short label.
- Mark strings `translatable: true/false` in layout specs so the audit knows what to expand.
- Pseudo-localise early (padded and accented strings) to find overflow before translators do.

### 1.5 Accessibility of text

- Meet contrast (section 3) at every size.
- Do not convey meaning by colour alone.
- Avoid all-caps for long strings; avoid italics for body text.
- Dynamic or scrolling text should be pausable; story text should not auto-advance faster than a comfortable reading pace (reading-speed notes in `skills/narrative-design/references/dialogue-and-branching.md` section 11).

## 2. Iconography

### 2.1 Design rules

- **One grid, one style.** Pick a stroke weight or fill style and corner radius and keep it. Mixed styles read as unfinished.
- **Silhouette first.** An icon must be recognisable as a solid shape; test at small size and in greyscale.
- **Size:** design on a base grid (for example 24 logical units for UI glyphs, larger for HUD and currency icons) with consistent padding; the touch target is bigger than the glyph (see targets below).
- **Pair icons with labels** for anything not universally understood. Universal set: close, back, settings gear, play, pause, sound on and off, share. Everything else, label it or test it.
- **States:** default, pressed, disabled, selected, badged, locked. Define all six for every interactive icon.
- **Currency and resource icons** must be unique in silhouette, not just colour (soft vs premium currency should never be mistaken).
- **Cultural care:** avoid gestures, symbols or colours with unintended meanings in target markets; check with native reviewers before launch.
- **Vector or multi-density raster:** deliver icons as vectors or at multiple densities; check sharpness at 2x and 3x.

### 2.2 Target vs glyph

The hit area comes from the minimum target (`references/mobile-interaction.md` section 3). A 24-unit glyph sits inside a 44 pt (iOS) or 48 dp (Android) hit region with padding. In engines, enlarge the clickable control rather than the art.

## 3. Contrast and colour

### 3.1 Contrast targets (WCAG 2.x)

| Element | Minimum ratio |
|---|---|
| Body text | 4.5:1 |
| Large text (about 18.66 px bold or 24 px regular and above in CSS terms) | 3:1 |
| Icons, input borders and key UI boundaries | 3:1 |

Check any pair with `python3 scripts/ui_audit.py contrast --fg "#FFFFFF" --bg "#2A6FDB"` (add `--large` or `--nontext` for the 3:1 judgements). Game art over moving backgrounds should be tested on the worst frame, or given a scrim or outline.

### 3.2 Colour rules

- **Do not use colour alone.** Add shape, icon, text or pattern. Test with a greyscale screenshot and a colour-vision-deficiency simulator.
- **Semantic palette:** a small fixed set (primary, positive, negative, warning, disabled, neutral) used consistently; reserve red and green for meanings that also carry icons.
- **Hierarchy through value (lightness)**, not only hue; the primary button has the highest contrast against its surroundings.
- **Disabled is not invisible:** disabled controls still show what they are; explain why on tap.
- **Dark and light surfaces:** if offering themes, check every token pair in both.
- **Rarity and tier colours** carry a second cue (frame, shape or label).

### 3.3 Backgrounds and legibility

- Overlay text on photos or scenes with a gradient scrim or panel, not on raw art.
- Keep HUD contrast stable across levels with different backgrounds: design the HUD for the brightest and darkest levels.
- Sunlight and low-brightness play: test on a device at low brightness and in daylight.

## 4. Responsive layout principles

1. **Anchor to edges and the safe area, not to pixel positions.** Pin top bars to the safe top, bottom bars to the safe bottom, and centre content in the remaining space.
2. **Use containers, not coordinates.** Stacks, grids and flexible spacers re-flow with content; fixed positions break with longer text and different ratios.
3. **Separate background from interface.** Backgrounds fill the full screen and extend past the safe area; interface lives inside it.
4. **Design for the extremes.** Narrowest and tallest phone, widest tablet, and the shortest landscape height.
5. **Set minimum and maximum sizes.** A button grows to fill a narrow screen up to a maximum, then stops; text containers have maximum widths on tablets.
6. **Play field scales by fit, UI by layout.** The board scales to fit the free area (keeping cell size above the target minimum) while UI elements keep physical size.
7. **Spacing scale.** A small set of spacings (for example 4, 8, 12, 16, 24, 32) used everywhere; the 16 unit page gutter is common on phones.
8. **Scroll rather than shrink.** When content overflows, scroll with a clear affordance rather than reducing sizes below minimums.
9. **Test live resize.** Rotation, split-screen, foldable posture changes and font-size changes should re-layout without losing state.

### 4.1 Layout-spec audit

`python3 scripts/ui_audit.py template --platform ios --hand either --out screen.json` prints a spec with screen size, safe insets and elements. Fill `rect` as `[x, y, w, h]`, `role` (primary, secondary, info and so on), `text`, `translatable` and `font_pt`. Then run `python3 scripts/ui_audit.py layout --spec screen.json`. Typical findings: target below the platform minimum, element inside an unsafe inset, overlap, primary action outside the reach zone, text too small, label that overflows after expansion. Use `--min-target` to apply a stricter project minimum.

## 5. Aspect ratios and tablets

### 5.1 The range to test

| Class | Examples of shape | What breaks |
|---|---|---|
| Compact phone | Shorter, closer to 16:9 | Vertical space: stacked bars crowd the play field |
| Tall phone | About 19.5:9 to 21:9 | Top and bottom insets, reach to the top; unused height |
| Tablet portrait | About 4:3 | Stretched layouts, tiny content in a huge frame |
| Tablet landscape | About 4:3 or 16:10 | Wide empty margins, controls far from thumbs |
| Foldable cover | Narrow and tall | Very small width |
| Foldable inner | Near square | Neither portrait nor landscape layouts fit |

Create a device matrix with one device or emulator per class, plus extreme font-size and display-size settings.

### 5.2 Handling extra height and width

- **Extra height (tall phones):** give extra space to the play field or to breathing room; do not stretch UI bars. Keep primary actions near the bottom anchor, not at a fixed fraction of height.
- **Extra width (tablets, landscape):** cap content width (a centred column or a two-panel layout); scale the play field to fit; avoid stretching buttons across the screen.
- **Two-panel layouts on tablets:** list and detail side by side (inventory and item detail), reducing navigation depth.
- **Controls on tablets:** keep them near the corners or edges where hands rest, not floating mid-screen; consider an option to scale or reposition touch controls.
- **Backgrounds:** extend art with safe margins so any ratio fills without letterbox bars or stretching; keep important art inside a central safe composition area.
- **Orientation policy:** decide per genre; platform rules for large screens are changing (check the volatile facts in `references/mobile-interaction.md` section 10 and section 6.3).

## 6. UI scaling in Godot

Godot 4 scales UI through window stretch settings and Control layout. Verify names in the version you ship.

### 6.1 Project settings

| Setting | Recommended starting point |
|---|---|
| `display/window/stretch/mode` | `canvas_items` for 2D and UI games, so UI renders sharply at the device resolution while using base-resolution coordinates |
| `display/window/stretch/aspect` | `expand` for most mobile games, so the viewport grows to the device ratio and anchors do the work; `keep_height` or `keep_width` when you want to fix one axis |
| Base size (`display/window/size/viewport_width` and `viewport_height`) | A common base such as 1080x1920 for portrait, or the size your art was authored at |
| Orientation | Set in the project display settings and in the export preset, consistently |

### 6.2 Layout practice

- Build screens with `Control` nodes and containers (`VBoxContainer`, `HBoxContainer`, `GridContainer`, `MarginContainer`, `PanelContainer`, `ScrollContainer`, `CenterContainer`, `AspectRatioContainer`) rather than manual positions.
- Set anchors and offsets or use anchor presets; use size flags (`expand`, `fill`) so children share space.
- Define fonts, sizes and colours in a `Theme` resource; use theme type variations for styles (primary, secondary, danger) so one change updates the project.
- Keep text in `Label` nodes with `autowrap_mode`; for buttons set `custom_minimum_size` to the target minimum and use `clip_text` or shrink logic where needed.
- Provide a content scale option for accessibility via `content_scale_factor` on the window when an in-game UI scale slider is offered.

### 6.3 Safe area

```gdscript
# Pseudocode shape; apply to a MarginContainer that wraps the interface.
func apply_safe_area(root: MarginContainer) -> void:
	var safe: Rect2i = DisplayServer.get_display_safe_area()
	var screen: Vector2i = DisplayServer.screen_get_size()
	var win: Vector2i = DisplayServer.window_get_size()
	if screen.x <= 0 or screen.y <= 0:
		return
	var sx: float = float(win.x) / float(screen.x)
	var sy: float = float(win.y) / float(screen.y)
	root.add_theme_constant_override("margin_left", int(safe.position.x * sx))
	root.add_theme_constant_override("margin_top", int(safe.position.y * sy))
	root.add_theme_constant_override("margin_right", int((screen.x - safe.end.x) * sx))
	root.add_theme_constant_override("margin_bottom", int((screen.y - safe.end.y) * sy))
```

Convert from screen pixels to the viewport scale carefully and re-apply on size changes (connect to the viewport `size_changed` signal). More engine detail is in `references/mobile-interaction.md` section 5.3 and in `engine-godot`.

## 7. UI scaling in Unity

### 7.1 uGUI (Canvas)

| Setting | Recommended starting point |
|---|---|
| Canvas Render Mode | Screen Space Overlay for pure UI; Screen Space Camera if UI needs the camera's effects |
| Canvas Scaler UI Scale Mode | Scale With Screen Size |
| Reference Resolution | The authoring size, such as 1080x1920 in portrait |
| Screen Match Mode | Match Width Or Height with a match value chosen by orientation: lean to width in portrait so UI never overflows horizontally, lean to height in landscape; or Expand to keep everything visible |
| Reference Pixels Per Unit | Match your sprite import settings |

Use anchors and pivots, Layout Groups (Horizontal, Vertical, Grid), Content Size Fitter and Layout Element for flexible layouts. Build a safe-area panel that drives its anchors from `Screen.safeArea`:

```csharp
// Shape: attach to a RectTransform that parents the interface.
void Apply(RectTransform panel)
{
    Rect safe = Screen.safeArea;
    Vector2 min = safe.position;
    Vector2 max = safe.position + safe.size;
    min.x /= Screen.width;  min.y /= Screen.height;
    max.x /= Screen.width;  max.y /= Screen.height;
    panel.anchorMin = min;
    panel.anchorMax = max;
    panel.offsetMin = Vector2.zero;
    panel.offsetMax = Vector2.zero;
}
```

Re-apply when `Screen.safeArea`, `Screen.width`, `Screen.height` or orientation changes (check each frame cheaply, or on a resolution-change callback).

### 7.2 UI Toolkit

- Use flexbox-style layout in UXML and USS; set `PanelSettings` scale mode to Scale With Screen Size with a reference resolution, and tune the match setting as above.
- Define styles in USS variables for colours, sizes and spacing so tokens are shared.
- Use the platform safe area through the panel's safe-area support or by reading `Screen.safeArea` and applying padding to a root element.

### 7.3 Common problems

| Symptom | Cause | Fix |
|---|---|---|
| UI too small on tablets | Match set to width on a wide screen | Cap scale or switch match by aspect ratio |
| Buttons cut off on tall phones | Positioned absolutely, no safe area | Anchor and use safe-area panel |
| Blurry text | Canvas scaled non-integer without proper font settings | Use dynamic font or TextMeshPro with correct settings; check scale |
| Layout rebuild spikes | Frequent Layout Group changes on large lists | Pool items, avoid per-frame layout changes (`mobile-performance`) |
| Touch targets differ across devices | Pixel sizes used | Specify sizes from a dp/pt table scaled by DPI (`units` command) |

More engine detail in `engine-unity`.

## 8. Heuristic UX review checklist

Use per screen and per flow. Mark pass, fail or not applicable, and record evidence (a screenshot or a device note). The checklist is adapted from widely used usability heuristics (Nielsen's ten heuristics) and mobile guidance, rephrased for games.

### 8.1 Clarity

- [ ] The screen's purpose is clear within a second; one dominant action
- [ ] Labels use player language, not internal terms
- [ ] Icons are understood without explanation, or are labelled
- [ ] Current state is visible (selected, locked, loading, progress, balance)
- [ ] Numbers and currencies are unambiguous

### 8.2 Control and recovery

- [ ] Every action can be undone or backed out, or is confirmed when it cannot
- [ ] Back behaviour is consistent (gesture, button, tab)
- [ ] Accidental taps have low cost; destructive actions are away from common ones
- [ ] Interruption and resume work (call, lock, kill)
- [ ] Offline and error states explain what happened and what to do next

### 8.3 Consistency

- [ ] Same action looks and sits the same across screens
- [ ] Type, spacing, icons and colours come from tokens
- [ ] Platform conventions respected (system back, share sheets, permission dialogs)
- [ ] Terminology consistent between UI, tutorials and store text

### 8.4 Ergonomics

- [ ] Primary actions in the thumb arc; one-hand audit done (`references/mobile-interaction.md` section 9)
- [ ] Touch targets meet minimums with adequate spacing
- [ ] Edge gestures and system areas are not used for critical taps
- [ ] Gestures have tap alternatives
- [ ] Feedback appears at the point of touch

### 8.5 Information load

- [ ] Persistent HUD items are justified by tier
- [ ] Text is short; long text is chunked and skippable
- [ ] Pop-ups pass through the queue and respect caps
- [ ] Permission requests are in context and primed
- [ ] No fabricated urgency or hidden costs

### 8.6 Visual and accessibility

- [ ] Contrast meets targets; no colour-only meaning
- [ ] Text at minimum size is readable on the smallest device; scales with settings where possible
- [ ] Layouts survive the aspect-ratio and font-size matrix
- [ ] Motion can be reduced; flashing content is avoided or limited (see `accessibility-localization`)
- [ ] Audio is not required for understanding; captions available for spoken content

### 8.7 Severity scale for findings

| Severity | Meaning | Action |
|---|---|---|
| 4 Blocker | Prevents completing a core task, loses progress or money, or breaks a store or legal rule | Fix before release |
| 3 Major | Frequent confusion or error, likely to drive churn | Fix this milestone |
| 2 Minor | Friction with a workaround | Backlog with owner |
| 1 Polish | Cosmetic | Opportunistic |

## 9. UX acceptance criteria

Write criteria as pass/fail statements tied to a test method. Adopt the ones that apply, set the numeric thresholds from your own baselines and platform minimums, and record them in the design contract.

| Area | Criterion | Test |
|---|---|---|
| Targets | Every interactive element meets the platform minimum (44 pt iOS, 48 dp Android) and has adequate spacing | `ui_audit.py layout` on each screen spec; device spot check |
| Reach | Primary actions of core screens are in the reach zone for the declared hand | One-hand audit |
| Safe areas | No interactive element or essential text inside unsafe insets on the device matrix | Device matrix screenshots |
| Contrast | Text 4.5:1 (3:1 large); icons and boundaries 3:1 | `ui_audit.py contrast` on every token pair |
| Colour independence | All state information has a non-colour cue | Greyscale pass |
| Text | No overflow or truncation at maximum supported system font size and in the longest shipped language | Pseudo-localisation and `expansion` |
| Aspect ratios | Layouts correct on every class in the matrix, in portrait (and landscape if supported) | Matrix run |
| Interruptions | Resume to the same screen and state after call, lock, background and process death | Lifecycle test script |
| Pop-ups | At most one modal at a time; none in the first-session blocklist; counts within budget | Queue logs, first-session playthrough |
| Permissions | No system prompt before the priming screen; none on first frame | Fresh-install run |
| Onboarding | First-session funnel steps logged with stable ids; first win reachable within the budgeted time and taps | Playthrough with analytics check |
| Tutorial | Every step completes with one action, resumes after interruption, and is skippable for returning players | Step-by-step test |
| Shops | Prices and currency unambiguous; insufficient-funds and offline states exist; restore control present where required | Walkthrough and policy checklist |
| Feedback | Press state and feedback within the frame budget for all buttons | Slow-motion video capture |
| Accessibility | Options present as scoped in the design contract (text size, reduced motion, colour assist, haptics) | Accessibility checklist in `accessibility-localization` |
| Performance | UI does not exceed frame-time budget on the target low-end device | Profile (`mobile-performance`) |

Sign-off rule: no blocker findings open, all major findings have owners and dates, and every applicable criterion has recorded evidence.

## 10. Worked example: auditing a hub screen

Context: a portrait hub with a Play button, a currency bar, a four-item nav bar and an event banner.

1. **Spec it.** `python3 scripts/ui_audit.py template --platform ios --hand either --out hub.json`; replace the sample elements with the real rects, roles, texts and font sizes.
2. **Run the audit.** `python3 scripts/ui_audit.py layout --spec hub.json`. Suppose it reports a nav icon at 36 x 36 pt, the event banner's close icon inside the top inset, and a label that overflows after expansion.
3. **Fix targets.** Pad the nav icons to a hit region of at least 44 x 44 pt without changing the art; space the destructive "reset" control away from "Play".
4. **Fix the inset.** Move the banner's close control inside the safe top and enlarge its hit area.
5. **Fix text.** Shorten the source string, or allow a two-line label; re-run `expansion` with the real maximum character count.
6. **Check contrast.** `ui_audit.py contrast` for the label colour on the button fill; if it fails, darken the fill or change the label colour, not the size.
7. **Run the matrix.** Open the hub on the compact phone, tall phone and tablet; confirm the Play button stays anchored in the bottom third and the nav bar keeps its width cap on the tablet.
8. **Apply the checklist** in section 8, record findings with severities, and attach the evidence to the review.
9. **Record acceptance** in section 9 terms and note remaining minor items with owners.

The same loop applies to any screen: spec, audit, fix, matrix, checklist, sign-off.
