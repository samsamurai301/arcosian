extends Control
## Emits swiped("left"|"right"|"up"|"down") for touch or mouse drags longer than min_distance.
## Touch and emulated-mouse events for the same gesture are de-duplicated by tracking the source.

signal swiped(dir: String)

@export var min_distance: float = 60.0

var _active: bool = false
var _source: String = ""
var _start: Vector2 = Vector2.ZERO


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_STOP
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)  # set_anchors_preset keeps the zero size after add_child


func _gui_input(event: InputEvent) -> void:
	if event is InputEventScreenTouch:
		_handle("touch", event.pressed, event.position)
	elif event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
		_handle("mouse", event.pressed, event.position)


func _handle(source: String, pressed: bool, pos: Vector2) -> void:
	if pressed:
		if not _active:
			_active = true
			_source = source
			_start = pos
	elif _active and _source == source:
		_active = false
		var d: Vector2 = pos - _start
		if d.length() >= min_distance:
			swiped.emit(direction_of(d))


static func direction_of(d: Vector2) -> String:
	if absf(d.x) >= absf(d.y):
		return "right" if d.x > 0.0 else "left"
	return "down" if d.y > 0.0 else "up"
