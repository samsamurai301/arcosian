extends Control
## Entry scene: services are already up (autoloads). Hand over to the menu after one frame.

func _ready() -> void:
	add_child(preload("res://presentation/ui.gd").background())
	Analytics.log_event("app_open", {"version": ProjectSettings.get_setting("application/config/version", "0.1.0")})
	await get_tree().process_frame
	get_tree().change_scene_to_file("res://presentation/main_menu.tscn")
