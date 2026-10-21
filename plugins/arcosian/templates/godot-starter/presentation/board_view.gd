extends Control
## Renders GameState.grid as tile Panels. sync() snaps to a state; play() animates sim events then syncs.

const Ui = preload("res://presentation/ui.gd")

const GAP: float = 14.0
const SLIDE_SEC: float = 0.1

var n: int = 5
var _cell: float = 100.0
var _tiles: Dictionary = {}  # cell index -> Panel


func setup(grid_size: int, side: float) -> void:
	n = grid_size
	custom_minimum_size = Vector2(side, side)
	size = Vector2(side, side)
	_cell = (side - GAP * (n + 1)) / float(n)
	queue_redraw()


func _draw() -> void:
	draw_rect(Rect2(Vector2.ZERO, size), Ui.BOARD)
	for i in n * n:
		draw_rect(Rect2(_cell_pos(i), Vector2(_cell, _cell)), Ui.CELL)


func sync(grid: Array[int]) -> void:
	for t in _tiles.values():
		t.queue_free()
	_tiles.clear()
	for i in grid.size():
		if grid[i] > 0:
			_tiles[i] = _make_tile(i, grid[i])


## Animate the slide of `events`, then snap to `grid` and play merge pops and spawn pops.
func play(events: Array, grid: Array[int]) -> void:
	var tw: Tween = create_tween().set_parallel(true)
	var any: bool = false
	for e in events:
		if e.type == "slide":
			for m in e.moves:
				var t: Control = _tiles.get(m.from)
				if t != null and m.from != m.to:
					tw.tween_property(t, "position", _cell_pos(m.to), SLIDE_SEC)
					any = true
	if any:
		await tw.finished
	else:
		tw.kill()
	sync(grid)
	for e in events:
		if e.type == "merge":
			_pop(e.at, 1.0, 1.18)
		elif e.type == "spawn":
			_pop(e.at, 0.0, 1.0)


func _pop(idx: int, from_scale: float, peak: float) -> void:
	var t: Control = _tiles.get(idx)
	if t == null:
		return
	t.scale = Vector2.ONE * from_scale
	var tw: Tween = create_tween()
	tw.tween_property(t, "scale", Vector2.ONE * peak, 0.08)
	if peak != 1.0:
		tw.tween_property(t, "scale", Vector2.ONE, 0.08)


func _cell_pos(i: int) -> Vector2:
	return Vector2(GAP + (i % n) * (_cell + GAP), GAP + (i / n) * (_cell + GAP))


func _make_tile(idx: int, value: int) -> Panel:
	var p: Panel = Panel.new()
	var sb: StyleBoxFlat = StyleBoxFlat.new()
	sb.bg_color = Ui.tile_color(value)
	sb.set_corner_radius_all(14)
	p.add_theme_stylebox_override("panel", sb)
	p.size = Vector2(_cell, _cell)
	p.pivot_offset = p.size / 2.0
	p.position = _cell_pos(idx)
	p.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var l: Label = Ui.label(str(value), int(_cell * (0.42 if value < 100 else 0.32)), Color("#3c3a32") if value <= 4 else Color.WHITE)
	Ui.full_rect(l)
	p.add_child(l)
	add_child(p)
	return p
