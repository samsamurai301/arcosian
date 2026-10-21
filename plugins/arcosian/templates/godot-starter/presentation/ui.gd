extends RefCounted
## Shared look: colours and small widget factories. Swap for a Theme resource when art arrives.

const BG: Color = Color("#1b1d2a")
const BOARD: Color = Color("#2b2e42")
const CELL: Color = Color("#3a3e57")
const TEXT: Color = Color("#f4f1ea")
const ACCENT: Color = Color("#edc22e")

const TILE_COLORS: Array[Color] = [
	Color("#eee4da"), Color("#ede0c8"), Color("#f2b179"), Color("#f59563"), Color("#f67c5f"),
	Color("#f65e3b"), Color("#edcf72"), Color("#edcc61"), Color("#edc850"), Color("#edc53f"),
]


static func tile_color(value: int) -> Color:
	var idx: int = clampi(int(log(float(maxi(value, 2))) / log(2.0)) - 1, 0, TILE_COLORS.size() - 1)
	return TILE_COLORS[idx]


static func full_rect(c: Control) -> void:
	c.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)  # also correct after add_child, unlike set_anchors_preset


static func label(text: String, font_size: int, color: Color = TEXT) -> Label:
	var l: Label = Label.new()
	l.text = text
	l.add_theme_font_size_override("font_size", font_size)
	l.add_theme_color_override("font_color", color)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	return l


static func button(text: String, on_press: Callable) -> Button:
	var b: Button = Button.new()
	b.text = text
	b.custom_minimum_size = Vector2(520, 130)  # >= 48dp touch target at any density
	b.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	b.add_theme_font_size_override("font_size", 48)
	b.pressed.connect(on_press)
	return b


static func background() -> ColorRect:
	var bg: ColorRect = ColorRect.new()
	bg.color = BG
	bg.mouse_filter = Control.MOUSE_FILTER_IGNORE
	full_rect(bg)
	return bg


## Keyboard and gamepad players need a focused button; touch players do not want the focus ring.
static func focus_first(buttons: Array) -> void:
	if buttons.is_empty() or DisplayServer.is_touchscreen_available():
		return
	(buttons[0] as Button).call_deferred("grab_focus")
