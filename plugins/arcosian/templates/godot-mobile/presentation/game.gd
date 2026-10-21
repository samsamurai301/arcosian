extends Control
## Gameplay scene: owns one Sim, feeds it swipes/keys, renders events through BoardView.

const Ui = preload("res://presentation/ui.gd")
const Sim = preload("res://core/sim.gd")
const BoardView = preload("res://presentation/board_view.gd")
const SwipeDetector = preload("res://presentation/swipe_detector.gd")
const ScreenShake = preload("res://presentation/screen_shake.gd")

const KEYS: Dictionary = {
	KEY_LEFT: "left", KEY_RIGHT: "right", KEY_UP: "up", KEY_DOWN: "down",
	KEY_A: "left", KEY_D: "right", KEY_W: "up", KEY_S: "down",
}

var sim: Sim
var board: BoardView
var _world: Control
var _shake: ScreenShake
var _score: Label
var _best: Label
var _menu_btn: Button
var _busy: bool = false


func _ready() -> void:
	sim = Sim.new(int(Time.get_unix_time_from_system()) & 0x7FFFFFFF)
	var run: Variant = SaveService.data.run
	if run is Dictionary:
		sim.load_dict(run)
	else:
		Analytics.log_event("game_start", {"seed": sim.state.seed_value})
	add_child(Ui.background())
	_world = Control.new()
	_world.mouse_filter = Control.MOUSE_FILTER_IGNORE
	Ui.full_rect(_world)
	add_child(_world)
	board = BoardView.new()
	board.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_world.add_child(board)
	_shake = ScreenShake.new()
	_shake.target = _world
	add_child(_shake)
	var swipe: SwipeDetector = SwipeDetector.new()
	swipe.swiped.connect(try_move)
	add_child(swipe)
	_score = Ui.label("", 80)
	_best = Ui.label("", 44, Ui.ACCENT)
	_menu_btn = Ui.button("Menu", _on_menu)
	_menu_btn.custom_minimum_size = Vector2(260, 100)
	for c in [_score, _best, _menu_btn]:
		add_child(c)
	EventBus.app_paused.connect(_stash_run)
	get_viewport().size_changed.connect(_layout)
	_layout()
	refresh()


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and KEYS.has(event.keycode):
		try_move(KEYS[event.keycode])


func try_move(dir: String) -> void:
	if _busy:
		return
	var events: Array = sim.apply({"type": "move", "dir": dir})
	var kind: String = events[0].type
	if kind == "invalid_move" or kind == "rejected":
		Haptics.light()
		return
	_busy = true
	EventBus.sim_events.emit(events)
	var biggest: int = 0
	for e in events:
		if e.type == "merge":
			biggest = maxi(biggest, int(e.value))
	if biggest >= 64:
		Haptics.heavy()
		_shake.add_trauma(0.5)
	elif biggest > 0:
		Haptics.light()
	await board.play(events, sim.state.grid)
	_busy = false
	refresh()
	_stash_run()
	if sim.state.status != "playing":
		_finish()


## Re-sync HUD and board from sim state (also used by tools/capture/screenshot_mode.gd).
func refresh() -> void:
	_score.text = str(sim.state.score)
	_best.text = "Best %d" % maxi(int(SaveService.data.profile.best_score), sim.state.score)
	board.sync(sim.state.grid)


func _finish() -> void:
	_busy = true
	var won: bool = sim.state.status == "won"
	SaveService.record_result(sim.state.score, won)
	Analytics.log_event("game_end", {"score": sim.state.score, "won": won, "moves": sim.state.moves})
	EventBus.game_over.emit(won, sim.state.score)
	await get_tree().create_timer(0.6).timeout
	get_tree().change_scene_to_file("res://presentation/results.tscn")


func _stash_run() -> void:
	if sim.state.status == "playing":
		SaveService.data.run = sim.to_dict()
		SaveService.mark_dirty()


func _on_menu() -> void:
	_stash_run()
	SaveService.flush()
	get_tree().change_scene_to_file("res://presentation/main_menu.tscn")


func _layout() -> void:
	var vp: Vector2 = get_viewport_rect().size
	var ins: Dictionary = SafeArea.insets()
	var side: float = minf(vp.x - 80.0, vp.y * 0.6)
	board.setup(sim.state.size, side)
	board.position = Vector2((vp.x - side) / 2.0, vp.y * 0.5 - side / 2.0 + 60.0)
	_score.position = Vector2(0, ins.top + 60.0)
	_score.size = Vector2(vp.x, 110)
	_best.position = Vector2(0, ins.top + 170.0)
	_best.size = Vector2(vp.x, 70)
	_menu_btn.position = Vector2((vp.x - 260.0) / 2.0, vp.y - ins.bottom - 180.0)
	board.sync(sim.state.grid)
