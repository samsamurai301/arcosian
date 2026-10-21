extends RefCounted
## Deterministic simulation of the merge game. No Node dependencies.
## apply(action) -> Array of event Dictionaries. Same seed + same actions => same events.
##
## Actions: {"type":"move","dir":"left|right|up|down"}, {"type":"new_game","seed":int}
## Events:  new_game, slide{dir,moves[{from,to,value,merged}]}, merge{at,value}, score{delta,total},
##          spawn{at,value}, win, lose, invalid_move{dir}, rejected{reason}

const GameState = preload("res://core/game_state.gd")
const Tuning = preload("res://core/tuning.gd")

const DIRS: Array[String] = ["left", "right", "up", "down"]

var state: GameState
var tuning: Dictionary


func _init(seed_value: int = 1, tuning_override: Dictionary = {}) -> void:
	tuning = Tuning.load_tuning()
	tuning.merge(tuning_override, true)
	new_game(seed_value)


func new_game(seed_value: int) -> Array:
	state = GameState.new(int(tuning.size), seed_value)
	var events: Array = [{"type": "new_game", "seed": seed_value}]
	for i in int(tuning.initial_tiles):
		var e: Dictionary = _spawn()
		if not e.is_empty():
			events.append(e)
	return events


func apply(action: Dictionary) -> Array:
	match String(action.get("type", "")):
		"move":
			return _move(String(action.get("dir", "")))
		"new_game":
			return new_game(int(action.get("seed", state.seed_value)))
	return [{"type": "rejected", "reason": "unknown_action"}]


func to_dict() -> Dictionary:
	return state.to_dict()


func load_dict(d: Dictionary) -> bool:
	return state.from_dict(d)


## Test helper: replace the grid (row-major) and re-evaluate status.
func set_grid(values: Array) -> void:
	state.grid.clear()
	for v in values:
		state.grid.append(int(v))
	state.status = GameState.PLAYING if can_move(state.grid, state.size) else GameState.LOST


func _move(dir: String) -> Array:
	if state.status != GameState.PLAYING:
		return [{"type": "rejected", "reason": "game_over"}]
	if not DIRS.has(dir):
		return [{"type": "rejected", "reason": "bad_direction"}]
	var r: Dictionary = slide_grid(state.grid, state.size, dir)
	if not r.moved:
		return [{"type": "invalid_move", "dir": dir}]
	state.grid = r.grid
	state.moves += 1
	state.score += int(r.gain)
	var events: Array = [{"type": "slide", "dir": dir, "moves": r.moves}]
	var reached_win: bool = false
	for m in r.merges:
		events.append({"type": "merge", "at": m.at, "value": m.value})
		if int(m.value) >= int(tuning.win_tile):
			reached_win = true
	if int(r.gain) > 0:
		events.append({"type": "score", "delta": r.gain, "total": state.score})
	var spawned: Dictionary = _spawn()
	if not spawned.is_empty():
		events.append(spawned)
	if reached_win:
		state.status = GameState.WON
		events.append({"type": "win", "score": state.score})
	elif not can_move(state.grid, state.size):
		state.status = GameState.LOST
		events.append({"type": "lose", "score": state.score})
	return events


func _spawn() -> Dictionary:
	var empties: Array[int] = state.empty_cells()
	if empties.is_empty():
		return {}
	var at: int = empties[state.rng.rand_int(empties.size())]
	var value: int = 4 if state.rng.rand_float() < float(tuning.spawn_four_chance) else 2
	state.grid[at] = value
	return {"type": "spawn", "at": at, "value": value}


## Pure slide+merge of a row-major grid. Each tile merges at most once per move.
## Returns {grid, moved, gain, moves[{from,to,value,merged}], merges[{at,value}]}.
static func slide_grid(grid: Array[int], size: int, dir: String) -> Dictionary:
	var out: Array[int] = grid.duplicate()
	out.fill(0)
	var gain: int = 0
	var moves: Array = []
	var merges: Array = []
	for a in size:
		var line: Array[int] = _line(size, dir, a)
		var write: int = 0
		var last_val: int = 0
		var last_pos: int = -1
		var last_merged: bool = false
		for i in size:
			var v: int = grid[line[i]]
			if v == 0:
				continue
			if v == last_val and not last_merged:
				var dst: int = line[last_pos]
				out[dst] = v * 2
				gain += v * 2
				moves.append({"from": line[i], "to": dst, "value": v, "merged": true})
				merges.append({"at": dst, "value": v * 2})
				last_merged = true
			else:
				var dst2: int = line[write]
				out[dst2] = v
				moves.append({"from": line[i], "to": dst2, "value": v, "merged": false})
				last_val = v
				last_pos = write
				last_merged = false
				write += 1
	return {"grid": out, "moved": out != grid, "gain": gain, "moves": moves, "merges": merges}


static func can_move(grid: Array[int], size: int) -> bool:
	for i in grid.size():
		if grid[i] == 0:
			return true
		if (i % size) < size - 1 and grid[i] == grid[i + 1]:
			return true
		if i + size < grid.size() and grid[i] == grid[i + size]:
			return true
	return false


## Cell indices of line `a`, ordered from the edge tiles slide toward.
static func _line(size: int, dir: String, a: int) -> Array[int]:
	var line: Array[int] = []
	for b in size:
		match dir:
			"left": line.append(a * size + b)
			"right": line.append(a * size + (size - 1 - b))
			"up": line.append(b * size + a)
			_: line.append((size - 1 - b) * size + a)
	return line
