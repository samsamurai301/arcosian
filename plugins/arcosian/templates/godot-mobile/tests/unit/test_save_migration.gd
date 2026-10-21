extends "res://tests/unit/test_case.gd"

const SaveData = preload("res://core/save_data.gd")


func test_v1_migrates_to_current() -> void:
	var d: Dictionary = SaveData.migrate({"version": 1, "best_score": 1234, "games": 7})
	assert_eq(d.version, SaveData.CURRENT)
	assert_eq(d.profile.best_score, 1234)
	assert_eq(d.profile.games_played, 7)
	assert_true(d.settings.sound, "new settings get defaults")


func test_missing_version_is_treated_as_v1() -> void:
	assert_eq(SaveData.migrate({"best_score": 5}).profile.best_score, 5)


func test_current_version_is_unchanged() -> void:
	var d: Dictionary = SaveData.default_save()
	d.profile.best_score = 99
	assert_eq(SaveData.migrate(d), d)


func test_newer_or_invalid_version_is_rejected() -> void:
	assert_true(SaveData.migrate({"version": SaveData.CURRENT + 1}).is_empty(), "future version")
	assert_true(SaveData.migrate({"version": 0}).is_empty(), "invalid version")


func test_migration_does_not_mutate_input() -> void:
	var src: Dictionary = {"version": 1, "best_score": 3}
	SaveData.migrate(src)
	assert_eq(src, {"version": 1, "best_score": 3})
