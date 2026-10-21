extends Node
## Notch / cutout / gesture-bar insets in viewport (canvas) pixels. Zero on desktop unless debug_insets is set.

var debug_insets: Dictionary = {}  # e.g. {"top": 90, "bottom": 60, "left": 0, "right": 0}


func insets() -> Dictionary:
	var zero: Dictionary = {"top": 0.0, "bottom": 0.0, "left": 0.0, "right": 0.0}
	if not debug_insets.is_empty():
		return debug_insets
	if not (OS.has_feature("android") or OS.has_feature("ios")):
		return zero
	var screen: Vector2i = DisplayServer.screen_get_size()
	var safe: Rect2i = DisplayServer.get_display_safe_area()
	if screen.x <= 0 or screen.y <= 0 or safe.size.x <= 0:
		return zero
	var vp: Vector2 = get_viewport().get_visible_rect().size
	var sx: float = vp.x / float(screen.x)
	var sy: float = vp.y / float(screen.y)
	return {
		"top": safe.position.y * sy,
		"bottom": (screen.y - safe.end.y) * sy,
		"left": safe.position.x * sx,
		"right": (screen.x - safe.end.x) * sx,
	}
