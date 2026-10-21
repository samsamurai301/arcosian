extends "res://tests/unit/test_case.gd"
## Input routing: every move must be reachable by touch or mouse drag, keyboard and gamepad.

const SwipeDetector = preload("res://presentation/swipe_detector.gd")
const MOVES: Array[String] = ["move_left", "move_right", "move_up", "move_down"]


func _mouse(pressed: bool, pos: Vector2) -> InputEventMouseButton:
	var e: InputEventMouseButton = InputEventMouseButton.new()
	e.button_index = MOUSE_BUTTON_LEFT
	e.pressed = pressed
	e.position = pos
	return e


func test_swipe_area_fills_its_parent_after_add_child() -> void:
	# Regression: set_anchors_preset() in _ready kept a 0x0 rect, so no drag or touch ever reached the detector.
	var parent: Control = Control.new()
	parent.size = Vector2(400, 300)
	(Engine.get_main_loop() as SceneTree).root.add_child(parent)
	var swipe: SwipeDetector = SwipeDetector.new()
	parent.add_child(swipe)
	assert_eq(swipe.size, Vector2(400, 300), "swipe area size")
	parent.free()


func test_mouse_drag_emits_one_swipe() -> void:
	var swipe: SwipeDetector = SwipeDetector.new()
	var got: Array = []
	swipe.swiped.connect(func(dir: String) -> void: got.append(dir))
	swipe._gui_input(_mouse(true, Vector2(100, 100)))
	swipe._gui_input(_mouse(false, Vector2(300, 130)))
	swipe._gui_input(_mouse(true, Vector2(100, 100)))
	swipe._gui_input(_mouse(false, Vector2(110, 105)))  # shorter than min_distance: not a swipe
	assert_eq(got.size(), 1, "swipes emitted")
	assert_eq(got[0] if got.size() > 0 else "", "right", "direction")
	swipe.free()


func test_every_move_has_keyboard_and_gamepad_bindings() -> void:
	for action: String in MOVES:
		assert_true(InputMap.has_action(action), action + " is defined in project.godot")
		if not InputMap.has_action(action):
			continue
		var kinds: Dictionary = {}
		for e: InputEvent in InputMap.action_get_events(action):
			kinds[e.get_class()] = true
		for kind: String in ["InputEventKey", "InputEventJoypadButton", "InputEventJoypadMotion"]:
			assert_true(kinds.has(kind), "%s has a %s binding" % [action, kind])


func test_pause_and_fullscreen_actions_exist() -> void:
	for action: String in ["pause", "toggle_fullscreen"]:
		assert_true(InputMap.has_action(action), action + " is defined in project.godot")
