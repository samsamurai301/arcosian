extends Control

const Ui = preload("res://presentation/ui.gd")


func _ready() -> void:
	add_child(Ui.background())
	var ins: Dictionary = SafeArea.insets()
	var box: VBoxContainer = VBoxContainer.new()
	Ui.full_rect(box)
	box.offset_top = ins.top
	box.offset_bottom = -ins.bottom
	box.alignment = BoxContainer.ALIGNMENT_CENTER
	box.add_theme_constant_override("separation", 40)
	add_child(box)
	box.add_child(Ui.label("MERGE FIVE", 120, Ui.ACCENT))
	box.add_child(Ui.label("Best  %d" % int(SaveService.data.profile.best_score), 56))
	if SaveService.data.run != null:
		box.add_child(Ui.button("Continue", _start.bind(true)))
	box.add_child(Ui.button("New Game", _start.bind(false)))


func _start(resume: bool) -> void:
	if not resume:
		SaveService.data.run = null
	get_tree().change_scene_to_file("res://presentation/game.tscn")
