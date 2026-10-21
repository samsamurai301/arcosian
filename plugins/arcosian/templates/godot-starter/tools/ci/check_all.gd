extends SceneTree
## Static gate: load every .gd / .tscn / .json under res://, report parse errors. Exit 0 ok, 1 failed.
## godot --headless --path <project> -s res://tools/ci/check_all.gd -- --out=<abs>/static.log

const Cli = preload("res://tools/ci/cli.gd")
const ErrorCapture = preload("res://tools/ci/error_capture.gd")


func _initialize() -> void:
	var cap: ErrorCapture = ErrorCapture.new()
	OS.add_logger(cap)
	var lines: PackedStringArray = []
	var failed: int = 0
	var checked: int = 0
	for path in _collect("res://"):
		var before: int = cap.errors.size()
		var problem: String = _check(path)
		if problem == "" and cap.errors.size() > before:
			problem = cap.errors[before]
		checked += 1
		if problem == "":
			lines.append("OK   " + path)
		else:
			failed += 1
			lines.append("FAIL %s  %s" % [path, problem])
	OS.remove_logger(cap)
	lines.append("checked=%d failed=%d godot=%s" % [checked, failed, Engine.get_version_info().string])
	var text: String = "\n".join(lines) + "\n"
	print(text)
	Cli.write_text(Cli.args().get("out", ""), text)
	quit(1 if failed > 0 else 0)


func _check(path: String) -> String:
	match path.get_extension():
		"gd":
			var s: Variant = load(path)
			if not (s is GDScript):
				return "failed to load"
			if not s.can_instantiate() and not s.is_abstract():
				return "script has errors (cannot instantiate)"
		"tscn":
			if not (load(path) is PackedScene):
				return "failed to load scene"
		"json":
			if JSON.parse_string(FileAccess.get_file_as_string(path)) == null:
				return "invalid JSON"
	return ""


func _collect(dir: String) -> PackedStringArray:
	var out: PackedStringArray = []
	for f in DirAccess.get_files_at(dir):
		if f.get_extension() in ["gd", "tscn", "json"]:
			out.append(dir.path_join(f))
	for d in DirAccess.get_directories_at(dir):
		if not d.begins_with(".") and d != "addons":
			out.append_array(_collect(dir.path_join(d)))
	return out
