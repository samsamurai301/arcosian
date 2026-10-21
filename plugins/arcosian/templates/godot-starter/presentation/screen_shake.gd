extends Node
## Trauma-model screen shake: offset = max_offset * trauma^2, trauma decays linearly.
## Add trauma on impact (0..1); the target Control is displaced and returns to its origin.

@export var max_offset: float = 28.0
@export var decay: float = 1.6

var target: Control
var trauma: float = 0.0


func add_trauma(amount: float) -> void:
	trauma = clampf(trauma + amount, 0.0, 1.0)


func _process(delta: float) -> void:
	if target == null:
		return
	if trauma <= 0.0:
		target.position = Vector2.ZERO
		return
	trauma = maxf(0.0, trauma - decay * delta)
	var s: float = trauma * trauma * max_offset
	target.position = Vector2(randf_range(-1.0, 1.0), randf_range(-1.0, 1.0)) * s
