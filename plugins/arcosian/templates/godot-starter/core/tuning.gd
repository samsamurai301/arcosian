extends RefCounted
## Loads gameplay tuning from JSON with safe defaults. Designers edit core/data/tuning.json only.

const PATH: String = "res://core/data/tuning.json"
const DEFAULTS: Dictionary = {"size": 5, "win_tile": 1024, "initial_tiles": 2, "spawn_four_chance": 0.1}


static func load_tuning(path: String = PATH) -> Dictionary:
	var out: Dictionary = DEFAULTS.duplicate()
	if not FileAccess.file_exists(path):
		return out
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if parsed is Dictionary:
		for k in DEFAULTS:
			if parsed.has(k):
				out[k] = parsed[k]
	return out
