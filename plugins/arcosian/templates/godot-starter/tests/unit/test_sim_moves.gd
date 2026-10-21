extends "res://tests/unit/test_case.gd"

const Sim = preload("res://core/sim.gd")


func _grid(rows: Array) -> Array[int]:
	var g: Array[int] = []
	for row in rows:
		for v in row:
			g.append(v)
	return g


func test_merge_left_once_per_tile() -> void:
	var g: Array[int] = _grid([[2, 2, 2, 2, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]])
	var r: Dictionary = Sim.slide_grid(g, 5, "left")
	assert_eq(r.grid.slice(0, 5), [4, 4, 0, 0, 0], "2,2,2,2 -> 4,4")
	assert_eq(r.gain, 8)


func test_three_equal_merges_leading_pair() -> void:
	var g: Array[int] = _grid([[0, 4, 4, 4, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]])
	assert_eq(Sim.slide_grid(g, 5, "left").grid.slice(0, 5), [8, 4, 0, 0, 0])
	assert_eq(Sim.slide_grid(g, 5, "right").grid.slice(0, 5), [0, 0, 0, 4, 8])


func test_all_directions() -> void:
	var g: Array[int] = _grid([[2, 0, 0, 0, 2], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [2, 0, 0, 0, 2]])
	assert_eq(Sim.slide_grid(g, 5, "up").grid[0], 4, "up merges column 0")
	assert_eq(Sim.slide_grid(g, 5, "down").grid[20], 4, "down merges column 0 at bottom")
	assert_eq(Sim.slide_grid(g, 5, "right").grid[4], 4, "right merges row 0")


func test_no_change_is_invalid_move() -> void:
	var sim: Sim = Sim.new(1)
	sim.set_grid(_grid([[2, 4, 2, 4, 2], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]]))
	var ev: Array = sim.apply({"type": "move", "dir": "left"})
	assert_eq(ev[0].type, "invalid_move")
	assert_eq(sim.state.moves, 0, "invalid move does not count")


func test_spawn_after_move_is_seeded() -> void:
	var a: Sim = Sim.new(5)
	var b: Sim = Sim.new(5)
	for d in ["left", "down", "right", "up", "left", "down"]:
		assert_eq(a.apply({"type": "move", "dir": d}), b.apply({"type": "move", "dir": d}), "events for " + d)
	assert_eq(a.state.grid, b.state.grid)


func test_new_game_spawns_initial_tiles() -> void:
	var sim: Sim = Sim.new(11)
	assert_eq(sim.state.empty_cells().size(), 25 - 2)
	for v in sim.state.grid:
		assert_true(v == 0 or v == 2 or v == 4, "spawn values are 2 or 4")


func test_spawn_lands_on_empty_cell_only() -> void:
	var sim: Sim = Sim.new(2)
	var before: int = sim.state.empty_cells().size()
	var ev: Array = sim.apply({"type": "move", "dir": "left"})
	if ev[0].type == "slide":
		var spawn: Dictionary = ev[ev.size() - 1]
		assert_eq(spawn.type, "spawn")
		assert_true(sim.state.grid[spawn.at] == spawn.value)
		assert_true(sim.state.empty_cells().size() <= before, "one more tile than before merges")


func test_state_roundtrip_continues_identically() -> void:
	var a: Sim = Sim.new(21)
	a.apply({"type": "move", "dir": "left"})
	a.apply({"type": "move", "dir": "down"})
	var b: Sim = Sim.new(1)
	assert_true(b.load_dict(JSON.parse_string(JSON.stringify(a.to_dict()))))
	for d in ["right", "up", "left"]:
		assert_eq(a.apply({"type": "move", "dir": d}), b.apply({"type": "move", "dir": d}))
	assert_eq(a.state.grid, b.state.grid)
