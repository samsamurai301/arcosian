extends "res://tests/unit/test_case.gd"
## The pure helpers of tools/perf/perf_probe.gd: percentiles, budget verdict, bot move choice.

const Probe = preload("res://tools/perf/perf_probe.gd")

const BUDGETS: Dictionary = {"fps_target": 60.0, "frame_ms_p95": 16.7, "memory_mb": 512.0}


func _series(values: Array) -> PackedFloat64Array:
	var a: PackedFloat64Array = PackedFloat64Array()
	for v in values:
		a.append(float(v))
	return a


func test_percentile_interpolates_like_perf_budget_py() -> void:
	assert_eq(Probe.percentile(_series([1, 2, 3, 4]), 50.0), 2.5)
	assert_eq(Probe.percentile(_series([1, 2, 3, 4]), 0.0), 1.0)
	assert_eq(Probe.percentile(_series([1, 2, 3, 4]), 100.0), 4.0)
	assert_eq(Probe.percentile(_series([7]), 95.0), 7.0)
	assert_eq(Probe.percentile(_series([]), 95.0), 0.0)


func test_summarize_unsorted_series() -> void:
	var s: Dictionary = Probe.summarize(_series([5, 1, 3, 2, 4]))
	assert_eq(s.frames, 5)
	assert_eq(s.mean, 3.0)
	assert_eq(s.p50, 3.0)
	assert_eq(s.max, 5.0)
	assert_eq(Probe.summarize(_series([])).frames, 0)


func test_judge_passes_within_budgets() -> void:
	assert_eq(Probe.judge(120.0, 12.0, 300.0, BUDGETS).size(), 0)


func test_judge_reports_each_violation() -> void:
	var v: Array[String] = Probe.judge(40.0, 20.0, 600.0, BUDGETS)
	assert_eq(v.size(), 3)
	assert_true(v[0].begins_with("fps.avg 40"), v[0])
	assert_true(v[1].begins_with("frame_ms.p95 20"), v[1])
	assert_true(v[2].begins_with("memory_mb.peak 600"), v[2])


func test_judge_fps_has_five_percent_tolerance() -> void:
	assert_eq(Probe.judge(57.0, 1.0, 1.0, BUDGETS).size(), 0, "57 fps is 95 percent of 60")
	assert_eq(Probe.judge(56.9, 1.0, 1.0, BUDGETS).size(), 1)


func test_judge_skips_unmeasured_memory_and_unset_budgets() -> void:
	assert_eq(Probe.judge(100.0, 1.0, -1.0, BUDGETS).size(), 0, "negative peak means not measured")
	assert_eq(Probe.judge(1.0, 999.0, 9999.0, {}).size(), 0, "no budgets, nothing to violate")


func test_greedy_move_prefers_merges_then_space() -> void:
	var g: Array[int] = []
	g.resize(25)
	g.fill(0)
	g[0] = 2
	g[1] = 2
	# left and right both merge the pair (gain 4); up/down only slide it. Left wins the tie by direction order.
	assert_eq(Probe.greedy_move(g, 5), "left")
	var stuck: Array[int] = []  # checkerboard of 2 and 4: no empty cell, no equal neighbours
	for i in 25:
		stuck.append(2 if ((i / 5) + (i % 5)) % 2 == 0 else 4)
	assert_eq(Probe.greedy_move(stuck, 5), "", "no legal move returns an empty string")
