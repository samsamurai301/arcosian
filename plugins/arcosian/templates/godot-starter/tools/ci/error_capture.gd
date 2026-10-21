extends Logger
## Collects engine errors (script errors, failed loads) so tools can fail on them. Warnings are ignored.

var errors: Array[String] = []


func _log_error(function: String, file: String, line: int, code: String, rationale: String,
		_editor_notify: bool, error_type: int, _script_backtraces: Array[ScriptBacktrace]) -> void:
	if error_type == ERROR_TYPE_WARNING:
		return
	errors.append("%s:%d (%s): %s" % [file, line, function, rationale if rationale != "" else code])
