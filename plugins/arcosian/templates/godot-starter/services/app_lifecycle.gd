extends Node
## App lifecycle on every platform: autosave when the app is paused, loses focus or is asked to close;
## F11 or Alt+Enter toggles fullscreen on desktop and web.

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	if "--smoke" in OS.get_cmdline_user_args():
		_smoke.call_deferred()


func _unhandled_input(event: InputEvent) -> void:
	if not event.is_action_pressed("toggle_fullscreen", false, true):
		return
	if not (OS.has_feature("pc") or OS.has_feature("web")):
		return
	var w: Window = get_window()
	w.mode = Window.MODE_WINDOWED if w.mode == Window.MODE_FULLSCREEN else Window.MODE_FULLSCREEN
	get_viewport().set_input_as_handled()


func _notification(what: int) -> void:
	match what:
		NOTIFICATION_APPLICATION_PAUSED, NOTIFICATION_APPLICATION_FOCUS_OUT, NOTIFICATION_WM_WINDOW_FOCUS_OUT:
			EventBus.app_paused.emit()
			SaveService.mark_dirty()
			SaveService.flush()
		NOTIFICATION_APPLICATION_RESUMED, NOTIFICATION_APPLICATION_FOCUS_IN, NOTIFICATION_WM_WINDOW_FOCUS_IN:
			EventBus.app_resumed.emit()
		NOTIFICATION_WM_CLOSE_REQUEST:
			EventBus.app_paused.emit()
			SaveService.mark_dirty()
			SaveService.flush()


## Exported-build check: `<build> --headless -- --smoke` loads the menu and the game scene, plays moves until one
## is accepted, prints "SMOKE OK" and exits 0; on any failure it prints "SMOKE FAIL" and exits 1.
## CI runs it on every desktop export, where the editor-only tools/ folder is not available.
func _smoke() -> void:
	var tree: SceneTree = get_tree()
	for path: String in ["res://presentation/main_menu.tscn", "res://presentation/game.tscn"]:
		for i in 5:
			await tree.process_frame
		if tree.change_scene_to_file(path) != OK:
			_smoke_end(false, "cannot load " + path)
			return
	for i in 5:
		await tree.process_frame
	var game: Node = tree.current_scene
	if game == null or not game.has_method("try_move"):
		_smoke_end(false, "the game scene did not start")
		return
	for dir: String in ["left", "up", "right", "down"]:
		game.try_move(dir)
		for i in 90:  # the board animation takes well under 90 frames
			await tree.process_frame
		if game.sim.state.moves > 0:
			_smoke_end(true, "moves=%d" % game.sim.state.moves)
			return
	_smoke_end(false, "no move was accepted")


func _smoke_end(ok: bool, detail: String) -> void:
	print("SMOKE %s %s (%s)" % ["OK" if ok else "FAIL", detail, OS.get_name()])
	get_tree().quit(0 if ok else 1)
