extends SceneTree
## Visual gate: renders screens to PNG. Needs a real renderer; on CI wrap in `xvfb-run -a`.
## godot --path <project> -s res://tools/capture/screenshot_mode.gd -- --out=<abs dir> --screens=menu,game,results
## Exit 0 ok, 2 when it cannot render (headless) or on bad arguments.

const Cli = preload("res://tools/ci/cli.gd")
const DIRS: Array[String] = ["left", "down", "right", "up"]
## Captures play the real scenes; keep their writes out of the player's real save file.
const CAPTURE_SAVE: String = "user://screenshot_capture_save.json"
const SCENES: Dictionary = {
	"menu": "res://presentation/main_menu.tscn",
	"game": "res://presentation/game.tscn",
	"results": "res://presentation/results.tscn",
}


func _initialize() -> void:
	if DisplayServer.get_name() == "headless":
		printerr("screenshot_mode: no renderer under --headless. Run without --headless (CI: xvfb-run -a godot --path <project> -s res://tools/capture/screenshot_mode.gd -- --out=<dir>).")
		quit(2)
		return
	var a: Dictionary = Cli.args()
	var out: String = String(a.get("out", ""))
	if out == "":
		printerr("usage: --out=<abs dir> [--screens=menu,game,results]")
		quit(2)
		return
	DirAccess.make_dir_recursive_absolute(out)
	_capture(out, String(a.get("screens", "menu,game,results")).split(","))


func _capture(out: String, screens: PackedStringArray) -> void:
	# Let the tree finish its first frame: autoloads are then in place and scenes get _ready() before we drive them.
	await process_frame
	# Point SaveService at a throwaway file before any scene can write (moves, focus-out and close all flush).
	var save: Node = root.get_node_or_null("SaveService")
	if save != null:
		save.set("path", CAPTURE_SAVE)
		save.call("load_save")
	else:
		printerr("screenshot_mode: SaveService autoload not found; captures may write the real save file.")
	var code: int = 0
	for s in screens:
		if not SCENES.has(s):
			printerr("unknown screen '%s' (menu|game|results)" % s)
			code = 2
			continue
		var node: Node = (load(SCENES[s]) as PackedScene).instantiate()
		root.add_child(node)
		if s == "game":
			for i in 8:
				node.sim.apply({"type": "move", "dir": DIRS[i % 4]})
			node.refresh()
		for i in 5:
			await process_frame
		var img: Image = root.get_texture().get_image()
		var path: String = out.path_join(s + ".png")
		if img == null or img.save_png(path) != OK:
			printerr("failed to save " + path)
			code = 2
		else:
			print("saved ", path, " ", img.get_size())
		node.queue_free()
		await process_frame
	for suffix in ["", ".bak", ".tmp"]:
		if FileAccess.file_exists(CAPTURE_SAVE + suffix):
			DirAccess.remove_absolute(ProjectSettings.globalize_path(CAPTURE_SAVE + suffix))
	quit(code)

