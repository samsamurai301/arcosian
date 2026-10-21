extends Node
## log_event(name, params) fans out to registered backends. The debug backend prints and keeps a ring buffer.
## Add a real SDK by calling add_backend(Callable(my_sdk, "log")) with signature (name: String, params: Dictionary).
## Event names must match .gamestudio/analytics/event-taxonomy.json (snake_case).

const MAX_BUFFER: int = 200

var events: Array[Dictionary] = []
var debug_print: bool = false
var _backends: Array[Callable] = []


func _ready() -> void:
	add_backend(_debug_backend)


func add_backend(cb: Callable) -> void:
	_backends.append(cb)


func log_event(event_name: String, params: Dictionary = {}) -> void:
	for cb in _backends:
		cb.call(event_name, params)


func _debug_backend(event_name: String, params: Dictionary) -> void:
	events.append({"name": event_name, "params": params, "ts": Time.get_unix_time_from_system()})
	if events.size() > MAX_BUFFER:
		events.pop_front()
	if debug_print:
		print("[analytics] %s %s" % [event_name, JSON.stringify(params)])
