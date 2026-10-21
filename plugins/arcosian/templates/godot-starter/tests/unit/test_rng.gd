extends "res://tests/unit/test_case.gd"

const Rng = preload("res://core/rng.gd")


func test_matches_pcg32_reference_vector() -> void:
	var r: Rng = Rng.new(42, 54)  # pcg32_srandom(42, 54) from the PCG reference demo
	var want: Array[int] = [0xa15c02b7, 0x7b47f409, 0xba1d3330, 0x83d2f293, 0xbfa4784b, 0xcbed606e]
	for w in want:
		assert_eq(r.next_u32(), w, "reference output")


func test_same_seed_same_sequence() -> void:
	var a: Rng = Rng.new(7)
	var b: Rng = Rng.new(7)
	for i in 100:
		assert_eq(a.next_u32(), b.next_u32())


func test_different_seed_differs() -> void:
	assert_ne(Rng.new(1).next_u32(), Rng.new(2).next_u32())


func test_rand_int_in_range() -> void:
	var r: Rng = Rng.new(3)
	for i in 500:
		var v: int = r.rand_int(5)
		assert_true(v >= 0 and v < 5, "rand_int out of range: %d" % v)


func test_state_roundtrip_through_json() -> void:
	var a: Rng = Rng.new(99)
	for i in 10:
		a.next_u32()
	var b: Rng = Rng.new(1)
	b.from_dict(JSON.parse_string(JSON.stringify(a.to_dict())))
	for i in 20:
		assert_eq(a.next_u32(), b.next_u32(), "after restore")
