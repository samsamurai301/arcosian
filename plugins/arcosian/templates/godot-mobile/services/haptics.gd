extends Node
## Thin wrapper over Input.vibrate_handheld. No-op on desktop and when disabled in settings.

var enabled: bool = true


func light() -> void:
	_buzz(15, 0.3)


func medium() -> void:
	_buzz(30, 0.6)


func heavy() -> void:
	_buzz(60, 1.0)


func _buzz(ms: int, amplitude: float) -> void:
	if enabled and (OS.has_feature("android") or OS.has_feature("ios")):
		Input.vibrate_handheld(ms, amplitude)
