extends SceneTree
## Unit gate: runs res://tests/unit/test_*.gd (extends tests/unit/test_case.gd), writes JUnit XML. Exit 0 ok, 1 failed.
## godot --headless --path <project> -s res://tools/ci/run_tests.gd -- --out=<abs>/unit.xml

const Cli = preload("res://tools/ci/cli.gd")
const ErrorCapture = preload("res://tools/ci/error_capture.gd")
const DIR: String = "res://tests/unit"


var _started: bool = false


## Tests run on the first frame, not in _initialize(): the root joins the tree only when the main loop
## starts, and tests that add nodes need _ready() and layout to run.
func _process(_delta: float) -> bool:
	if not _started:
		_started = true
		_run()
	return false


func _run() -> void:
	var cap: ErrorCapture = ErrorCapture.new()
	OS.add_logger(cap)
	var suites: PackedStringArray = []
	var total: int = 0
	var failed: int = 0
	var files: PackedStringArray = DirAccess.get_files_at(DIR)
	files.sort()
	for f in files:
		if not (f.begins_with("test_") and f.ends_with(".gd")) or f == "test_case.gd":
			continue
		var script: GDScript = load(DIR.path_join(f))
		var cases: PackedStringArray = []
		var suite_fail: int = 0
		var n: int = 0
		if script == null or not script.can_instantiate():
			cases.append('<testcase classname="%s" name="load"><failure message="script failed to load"/></testcase>' % f)
			suite_fail += 1
			n += 1
		else:
			for m in script.get_script_method_list():
				if not String(m.name).begins_with("test_"):
					continue
				var inst: RefCounted = script.new()
				var before: int = cap.errors.size()
				inst.call("before_each")
				inst.call(m.name)
				var msgs: Array[String] = inst.failures.duplicate()
				for e in cap.errors.slice(before):
					msgs.append("engine error: " + e)
				n += 1
				if msgs.is_empty():
					cases.append('<testcase classname="%s" name="%s"/>' % [f, m.name])
				else:
					suite_fail += 1
					cases.append('<testcase classname="%s" name="%s"><failure message="%s"/></testcase>' % [f, m.name, _esc("; ".join(msgs))])
					printerr("FAIL %s::%s  %s" % [f, m.name, "; ".join(msgs)])
		total += n
		failed += suite_fail
		suites.append('<testsuite name="%s" tests="%d" failures="%d">%s</testsuite>' % [f, n, suite_fail, "".join(cases)])
	OS.remove_logger(cap)
	var xml: String = '<?xml version="1.0" encoding="UTF-8"?>\n<testsuites tests="%d" failures="%d">%s</testsuites>\n' % [total, failed, "".join(suites)]
	Cli.write_text(Cli.args().get("out", ""), xml)
	print("tests=%d failures=%d" % [total, failed])
	quit(1 if failed > 0 or total == 0 else 0)


func _esc(s: String) -> String:
	return s.xml_escape(true)
