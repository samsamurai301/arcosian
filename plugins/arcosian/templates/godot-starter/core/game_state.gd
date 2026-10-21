extends RefCounted
## Plain data for one run of the 5x5 merge game. Serialisable; no logic beyond queries.

const Rng = preload("res://core/rng.gd")

const PLAYING: String = "playing"
const WON: String = "won"
const LOST: String = "lost"

var size: int = 5
var grid: Array[int] = []
var score: int = 0
var moves: int = 0
var status: String = PLAYING
var seed_value: int = 1
var rng: Rng


func _init(p_size: int = 5, p_seed: int = 1) -> void:
	size = p_size
	seed_value = p_seed
	rng = Rng.new(p_seed)
	grid.resize(size * size)
	grid.fill(0)


func empty_cells() -> Array[int]:
	var out: Array[int] = []
	for i in grid.size():
		if grid[i] == 0:
			out.append(i)
	return out


func max_tile() -> int:
	var m: int = 0
	for v in grid:
		m = maxi(m, v)
	return m


## Resolves playthrough "expect" paths: score, moves, status, max_tile, empty_count, grid.<index>.
func lookup(path: String) -> Variant:
	match path:
		"score": return score
		"moves": return moves
		"status": return status
		"won": return status == WON
		"lost": return status == LOST
		"max_tile": return max_tile()
		"empty_count": return empty_cells().size()
		"grid_sum":
			var s: int = 0
			for v in grid:
				s += v
			return s
	if path.begins_with("grid."):
		var i: int = path.substr(5).to_int()
		return grid[i] if i >= 0 and i < grid.size() else null
	return null


func to_dict() -> Dictionary:
	return {
		"size": size, "grid": grid.duplicate(), "score": score, "moves": moves,
		"status": status, "seed": seed_value, "rng": rng.to_dict(),
	}


## Returns false (state untouched) when the dictionary is malformed.
func from_dict(d: Dictionary) -> bool:
	var g: Variant = d.get("grid")
	var n: int = int(d.get("size", 0))
	if not (g is Array) or n < 2 or g.size() != n * n:
		return false
	size = n
	grid.clear()
	for v in g:
		grid.append(int(v))
	score = int(d.get("score", 0))
	moves = int(d.get("moves", 0))
	status = String(d.get("status", PLAYING))
	seed_value = int(d.get("seed", 1))
	rng.from_dict(d.get("rng", {}))
	return true
