extends "res://tests/unit/test_case.gd"

const Sim = preload("res://core/sim.gd")


func _sim_with(cells: Dictionary, tuning: Dictionary = {}) -> Sim:
	var sim: Sim = Sim.new(1, tuning)
	var g: Array[int] = []
	g.resize(25)
	g.fill(0)
	for k in cells:
		g[int(k)] = int(cells[k])
	sim.set_grid(g)
	return sim


func test_win_when_target_tile_created() -> void:
	var sim: Sim = _sim_with({0: 512, 1: 512})  # win_tile 1024
	var ev: Array = sim.apply({"type": "move", "dir": "left"})
	assert_eq(sim.state.status, "won")
	assert_eq(ev[ev.size() - 1].type, "win")
	assert_eq(sim.apply({"type": "move", "dir": "left"})[0].type, "rejected", "no moves after the game ends")


func test_win_target_comes_from_tuning() -> void:
	var sim: Sim = _sim_with({0: 8, 1: 8}, {"win_tile": 16})
	sim.apply({"type": "move", "dir": "left"})
	assert_eq(sim.state.status, "won")


func test_lose_when_board_full_and_no_merge() -> void:
	var g: Array[int] = []
	for i in 25:
		g.append(2 if (i % 5 + i / 5) % 2 == 0 else 4)  # checkerboard: no equal neighbours
	assert_false(Sim.can_move(g, 5))
	var sim: Sim = Sim.new(1)
	sim.set_grid(g)
	assert_eq(sim.state.status, "lost")


func test_lose_event_after_last_merge_fills_board() -> void:
	var sim: Sim = Sim.new(1)
	var g: Array[int] = []
	for i in 25:
		g.append(2 if (i % 5 + i / 5) % 2 == 0 else 4)
	g[0] = 8
	g[1] = 8
	g[2] = 2
	g[3] = 4
	g[4] = 2
	sim.set_grid(g)
	var ev: Array = sim.apply({"type": "move", "dir": "left"})
	assert_true(ev[0].type == "slide", "move accepted")
	# a merge freed a cell and the spawn refilled it; outcome must be consistent with can_move
	assert_eq(sim.state.status == "lost", not Sim.can_move(sim.state.grid, 5))


func test_can_move_with_empty_or_pair() -> void:
	var g: Array[int] = []
	g.resize(25)
	g.fill(0)
	assert_true(Sim.can_move(g, 5))
