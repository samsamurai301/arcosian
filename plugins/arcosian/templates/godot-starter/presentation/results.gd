extends Control

const Ui = preload("res://presentation/ui.gd")


func _ready() -> void:
	add_child(Ui.background())
	var p: Dictionary = SaveService.data.profile
	var ins: Dictionary = SafeArea.insets()
	var box: VBoxContainer = VBoxContainer.new()
	Ui.full_rect(box)
	box.offset_top = ins.top
	box.offset_bottom = -ins.bottom
	box.alignment = BoxContainer.ALIGNMENT_CENTER
	box.add_theme_constant_override("separation", 40)
	add_child(box)
	box.add_child(Ui.label("YOU WIN" if p.last_won else "NO MOVES LEFT", 96, Ui.ACCENT))
	box.add_child(Ui.label("Score  %d" % int(p.last_score), 72))
	box.add_child(Ui.label("Best  %d" % int(p.best_score), 56))
	var buttons: Array = [
		Ui.button("Play Again", _go.bind("res://presentation/game.tscn")),
		Ui.button("Menu", _go.bind("res://presentation/main_menu.tscn")),
	]
	for b: Button in buttons:
		box.add_child(b)
	Ui.focus_first(buttons)


func _go(scene: String) -> void:
	get_tree().change_scene_to_file(scene)
