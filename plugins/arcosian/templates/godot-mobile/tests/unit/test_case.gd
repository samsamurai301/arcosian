extends RefCounted
## Base class for unit tests. Methods named test_* run in a fresh instance; assertions record failures.

var failures: Array[String] = []


func before_each() -> void:
	pass


func assert_true(cond: bool, msg: String = "expected true") -> void:
	if not cond:
		failures.append(msg)


func assert_false(cond: bool, msg: String = "expected false") -> void:
	if cond:
		failures.append(msg)


func assert_eq(got: Variant, want: Variant, msg: String = "") -> void:
	if typeof(got) != typeof(want) or got != want:
		failures.append("%s expected %s, got %s" % [msg, str(want), str(got)])


func assert_ne(got: Variant, other: Variant, msg: String = "") -> void:
	if typeof(got) == typeof(other) and got == other:
		failures.append("%s expected values to differ, both %s" % [msg, str(got)])
