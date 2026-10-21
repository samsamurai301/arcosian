extends RefCounted
## Versioned save schema and migrations (pure functions, unit-testable).
## v1: {version, best_score, games}
## v2: {version, profile{best_score, games_played, last_score, last_won}, settings{sound, haptics}, run}
## To change the schema: bump CURRENT, add a `_v<N>_to_<N+1>` step, add a test in test_save_migration.gd.

const CURRENT: int = 2


static func default_save() -> Dictionary:
	return {
		"version": CURRENT,
		"profile": {"best_score": 0, "games_played": 0, "last_score": 0, "last_won": false},
		"settings": {"sound": true, "haptics": true},
		"run": null,
	}


## Returns the migrated dictionary, or {} when the data is unreadable or from a newer build.
static func migrate(data: Dictionary) -> Dictionary:
	var v: int = int(data.get("version", 1))
	if v < 1 or v > CURRENT:
		return {}
	var d: Dictionary = data.duplicate(true)
	while v < CURRENT:
		match v:
			1: d = _v1_to_v2(d)
			_: return {}
		v = int(d.get("version", v + 1))
	return d


static func _v1_to_v2(d: Dictionary) -> Dictionary:
	var out: Dictionary = default_save()
	out.profile.best_score = int(d.get("best_score", 0))
	out.profile.games_played = int(d.get("games", 0))
	return out
