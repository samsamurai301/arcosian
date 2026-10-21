extends Node
## Versioned JSON save with atomic writes (temp file + rename) and a .bak fallback.

const SaveData = preload("res://core/save_data.gd")

var path: String = "user://save.json"
var data: Dictionary = SaveData.default_save()
var _dirty: bool = false


func _ready() -> void:
	load_save()


func load_save() -> void:
	for p in [path, path + ".bak"]:
		if not FileAccess.file_exists(p):
			continue
		var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(p))
		if parsed is Dictionary:
			var migrated: Dictionary = SaveData.migrate(parsed)
			if not migrated.is_empty():
				data = migrated
				return
	data = SaveData.default_save()


func mark_dirty() -> void:
	_dirty = true


## Writes only when something changed.
func flush() -> void:
	if _dirty:
		save()


func save() -> bool:
	var tmp: String = path + ".tmp"
	var f: FileAccess = FileAccess.open(tmp, FileAccess.WRITE)
	if f == null:
		push_warning("SaveService: cannot open %s (error %d)" % [tmp, FileAccess.get_open_error()])
		return false
	f.store_string(JSON.stringify(data))
	f.flush()
	f.close()
	if FileAccess.file_exists(path):
		DirAccess.copy_absolute(ProjectSettings.globalize_path(path), ProjectSettings.globalize_path(path + ".bak"))
	var err: int = DirAccess.rename_absolute(ProjectSettings.globalize_path(tmp), ProjectSettings.globalize_path(path))
	_dirty = err != OK
	return err == OK


func record_result(score: int, won: bool) -> void:
	var p: Dictionary = data.profile
	p.best_score = maxi(int(p.best_score), score)
	p.games_played = int(p.games_played) + 1
	p.last_score = score
	p.last_won = won
	data.run = null
	_dirty = true
	flush()
