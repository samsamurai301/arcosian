extends SceneTree
## Perf probe -> perf-report JSON (schema_version 1.0, scripts/schemas/perf-report.schema.json).
## Exit 0 verdict pass, 1 budget violated, 2 usage or runtime error.
##
##   godot --path <project> -s res://tools/perf/perf_probe.gd -- --out=<abs>/perf.json [--seconds=20]
##   godot --headless --path <project> -s res://tools/perf/perf_probe.gd -- --out=<abs>/perf.json [--seconds=20]
##
## Plays the real game scene (presentation/game.tscn) with a greedy bot that drives the Sim through the scene's
## own input path (Game.try_move), restarting after each finished game, and samples every frame.
##
##   frame_ms  CPU work per frame on the main thread, excluding vsync/present waits and idle sleeping:
##             windowed = scene processing (frame start to frame_pre_draw) + render CPU + frame setup, or the
##             driver's GPU time when that is longer; headless = scene processing only (no rendering at all).
##   fps       derived from frame_ms (1000 / mean, 1000 / p99): what the measured cost would sustain, the same
##             definition scripts/perf_budget.py uses. fps.engine_avg / engine_min are the engine's delivered rate.
##   memory_mb process RSS sampled once a second where the OS allows it (basis "rss"), else the engine's own
##             accounting (static + video memory, basis "engine"); engine_peak is the per-frame engine figure.
##
## Windowed runs keep the project's own pacing (vsync, max_fps). Headless has no display, so the engine would
## sleep ~7 ms per frame and hide the real cost: the probe disables that sleep and paces frames itself, spinning
## rather than sleeping so the core stays hot (--pace-fps, default 60; work is measured before the pacing wait).
## With the engine flag `--fixed-fps 60` plus `--pace-fps=0` a headless run needs no real time at all and is
## deterministic (20 s of game time in well under a second).
##
## Options (all --key=value): out (required, abs path), seconds (measured window in game time, default 20),
##   warmup (seconds discarded first, default 1), seed (default 1), budget-frame-ms (16.7), budget-memory-mb (512),
##   budget-fps (60), pace-fps (headless pacing, default 60, 0 = unpaced), tier (low|mid|high), device-name,
##   build, scenario, feature (F012), frames (embed the raw frames_ms series), help.
## Desktop numbers are a proxy: headless is CPU-only and is flagged as such in the report; neither is a device capture.

const Cli = preload("res://tools/ci/cli.gd")
const Sim = preload("res://core/sim.gd")

const GAME_SCENE: String = "res://presentation/game.tscn"
const PROBE_SAVE: String = "user://perf_probe_save.json"
const DEFAULT_BUDGETS: Dictionary = {"fps_target": 60.0, "frame_ms_p95": 16.7, "memory_mb": 512.0}  # = gslib.DEFAULT_PERF_BUDGETS
const FPS_TOLERANCE: float = 0.95  # same 5 percent tolerance as scripts/perf_budget.py
const RESTART_DELAY_SEC: float = 0.5
const MIN_FRAMES: int = 10
const USAGE: String = "usage: -- --out=<abs>.json [--seconds=20] [--warmup=1] [--seed=1] [--budget-frame-ms=16.7] [--budget-memory-mb=512] [--budget-fps=60] [--pace-fps=60] [--tier=low|mid|high] [--device-name=T] [--build=T] [--scenario=T] [--feature=F012] [--frames] (see header of tools/perf/perf_probe.gd)"

var _out: String = ""
var _seconds: float = 20.0
var _warmup: float = 1.0
var _seed: int = 1
var _pace_us: int = 0
var _keep_frames: bool = false
var _opts: Dictionary = {}
var _budgets: Dictionary = {}

var _headless: bool = false
var _done: bool = false
var _wall_start_us: int = 0
var _wall_limit_us: int = 0

var _game: Node = null
var _save: Node = null
var _vp: RID
var _episodes: int = 0
var _moves: int = 0
var _restart_at: float = -1.0

var _work_start_us: int = 0  # when this frame's game work began (after probe bookkeeping and any pacing wait)
var _pre_draw_us: int = 0
var _drew: bool = false
var _game_time: float = 0.0
var _window_sec: float = 0.0
var _frame_in_window: bool = false
var _cold_start_sec: float = -1.0
var _next_slow_time: float = 0.0
var _frame_due_us: int = 0  # headless pacing: when the next frame's work should start

var _frame_ms: PackedFloat64Array = PackedFloat64Array()
var _warm_max: float = 0.0
var _cpu_sum: float = 0.0
var _gpu_sum: float = 0.0
var _gpu_seen: bool = false
var _draw_sum: float = 0.0
var _mem_n: int = 0
var _mem_sum: float = 0.0
var _mem_peak: float = 0.0
var _mem_first: float = -1.0
var _mem_last: float = 0.0
var _rss: PackedFloat64Array = PackedFloat64Array()
var _engine_fps: PackedFloat64Array = PackedFloat64Array()


func _initialize() -> void:
	var a: Dictionary = Cli.args()
	_opts = a
	if a.has("help"):
		print(USAGE)
		_quit_early(0)
		return
	if not _parse_options():
		_quit_early(2)
		return
	_headless = DisplayServer.get_name() == "headless"
	_wall_start_us = Time.get_ticks_usec()
	_wall_limit_us = int((_warmup + _seconds) * 3.0 + 30.0) * 1000000
	if _headless:
		# No display: the engine sleeps ~7 ms between frames, which would hide the real cost. Pace by hand.
		OS.low_processor_usage_mode_sleep_usec = 0
		Engine.max_fps = 0
	else:
		_pace_us = 0  # the display paces a windowed run
		_vp = root.get_viewport_rid()
		RenderingServer.viewport_set_measure_render_time(_vp, true)
		RenderingServer.frame_pre_draw.connect(_on_pre_draw)
	# This script is compiled before the autoloads exist, so reach SaveService by node name. Keep the bot's
	# games out of the player's real save file.
	_save = root.get_node_or_null("SaveService")
	if _save != null:
		_save.set("path", PROBE_SAVE)
		_save.call("load_save")
	var packed: PackedScene = load(GAME_SCENE) as PackedScene
	if packed == null:
		_fail("cannot load %s" % GAME_SCENE)
		return
	var inst: Node = packed.instantiate()
	root.add_child(inst)
	current_scene = inst  # its _ready runs when the tree starts; _decide() adopts it on the first frame


## Leave before the first frame (quit() only takes effect once the current iteration ends).
func _quit_early(code: int) -> void:
	_done = true
	quit(code)


func _on_pre_draw() -> void:
	_pre_draw_us = Time.get_ticks_usec()
	_drew = true


func _process(delta: float) -> bool:
	if _done:
		return true
	var now: int = Time.get_ticks_usec()
	if _work_start_us > 0:
		_record_frame(now, delta)
	elif _cold_start_sec < 0.0:
		_cold_start_sec = float(Time.get_ticks_msec()) / 1000.0  # engine start to the first game frame
	if now - _wall_start_us > _wall_limit_us:
		_fail("timed out: %.1f s of game time not reached after %d s of wall time (is the window hidden?)" % [_warmup + _seconds, _wall_limit_us / 1000000])
		return true
	if _window_sec >= _seconds:
		_finish()
		return true
	if not _headless and _game_time > _warmup + 5.0 and _frame_ms.is_empty():
		_fail("the window was never drawn (hidden or occluded?); run with --headless for CPU-only metrics")
		return true
	_game_time += delta
	_frame_in_window = _game_time >= _warmup
	if _game_time >= _next_slow_time:
		_next_slow_time = _game_time + 1.0
		_slow_sample()
	var dir: String = _decide()
	if _pace_us > 0:
		# Spin instead of sleeping: a sleeping core clocks down, which inflates the next frame's work 3 to 4 times.
		var due: int = _frame_due_us
		while due > 0 and Time.get_ticks_usec() < due:
			pass
		var t: int = Time.get_ticks_usec()
		_frame_due_us = (due if due > 0 and t - due < _pace_us else t) + _pace_us
	_work_start_us = Time.get_ticks_usec()
	_drew = false
	if dir != "":
		_game.call("try_move", dir)
		_moves += 1
	return false


## Finalise the previous frame: its work time, then memory and draw calls.
func _record_frame(now: int, delta: float) -> void:
	var cpu_ms: float = 0.0
	var gpu_ms: float = 0.0
	if _headless:
		cpu_ms = float(now - _work_start_us) / 1000.0
	else:
		if not _drew:
			return  # window not drawn this frame (hidden or occluded): nothing to measure
		cpu_ms = float(_pre_draw_us - _work_start_us) / 1000.0 \
				+ RenderingServer.viewport_get_measured_render_time_cpu(_vp) + RenderingServer.get_frame_setup_time_cpu()
		gpu_ms = RenderingServer.viewport_get_measured_render_time_gpu(_vp)
	var ms: float = maxf(cpu_ms, gpu_ms)
	if not _frame_in_window:
		_warm_max = maxf(_warm_max, ms)
		return
	_window_sec += delta
	_frame_ms.append(ms)
	_cpu_sum += cpu_ms
	if gpu_ms > 0.0:
		_gpu_seen = true
		_gpu_sum += gpu_ms
	_draw_sum += Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)
	var mem: float = (Performance.get_monitor(Performance.MEMORY_STATIC) + Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED)) / 1048576.0
	if _mem_first < 0.0:
		_mem_first = mem
	_mem_last = mem
	_mem_peak = maxf(_mem_peak, mem)
	_mem_sum += mem
	_mem_n += 1


## Once-a-second readings: process RSS and the engine's own fps counter. Cheap enough, but `ps` blocks for ~10 ms,
## which is why this runs before the frame's work window starts.
func _slow_sample() -> void:
	if not _frame_in_window:
		return
	var rss: float = rss_mb()
	if rss > 0.0:
		_rss.append(rss)
	# The engine refreshes its fps counter once per real second; before that it still reads its initial value.
	if Time.get_ticks_usec() - _wall_start_us > 1500000:
		_engine_fps.append(Engine.get_frames_per_second())


## Bot: keep a game running, restart after each finished one. Returns the move to send this frame, or "".
func _decide() -> String:
	var scene: Node = current_scene
	if scene == null or scene.scene_file_path != GAME_SCENE:
		# Results or menu screen after a finished game: go back to the game scene after a short pause.
		if _restart_at < 0.0:
			_restart_at = _game_time + RESTART_DELAY_SEC
		elif _game_time >= _restart_at:
			_restart_at = _game_time + 10.0  # do not ask again while the (deferred) switch is pending
			change_scene_to_file(GAME_SCENE)
		return ""
	_restart_at = -1.0
	if scene != _game:
		_adopt(scene)
	var state: Variant = _game.get("sim").state
	if state.status != "playing" or bool(_game.get("_busy")):
		return ""
	return greedy_move(state.grid, state.size)


## A fresh game scene instance: reseed it so the move sequence depends on --seed, not on the clock.
func _adopt(scene: Node) -> void:
	_game = scene
	_episodes += 1
	scene.sim.apply({"type": "new_game", "seed": _seed + _episodes - 1})
	scene.refresh()


func _parse_options() -> bool:
	_out = String(_opts.get("out", ""))
	if _out == "":
		printerr("perf_probe: --out=<abs path>.json is required. " + USAGE)
		return false
	_seconds = _num("seconds", 20.0)
	_warmup = _num("warmup", 1.0)
	_seed = int(_num("seed", 1.0))
	var pace_fps: float = _num("pace-fps", 60.0)
	_budgets = {
		"fps_target": _num("budget-fps", DEFAULT_BUDGETS.fps_target),
		"frame_ms_p95": _num("budget-frame-ms", DEFAULT_BUDGETS.frame_ms_p95),
		"memory_mb": _num("budget-memory-mb", DEFAULT_BUDGETS.memory_mb),
	}
	_keep_frames = _opts.has("frames")
	if is_nan(_seconds) or is_nan(_warmup) or is_nan(pace_fps) or _budgets.values().any(func(v: float) -> bool: return is_nan(v)):
		return false
	if _seconds <= 0.0 or _warmup < 0.0 or pace_fps < 0.0:
		printerr("perf_probe: --seconds must be > 0, --warmup and --pace-fps >= 0. " + USAGE)
		return false
	if _budgets.values().any(func(v: float) -> bool: return v <= 0.0):
		printerr("perf_probe: budgets must be > 0. " + USAGE)
		return false
	if _opts.has("tier") and not (String(_opts.tier) in ["low", "mid", "high"]):
		printerr("perf_probe: --tier must be low, mid or high")
		return false
	if _opts.has("feature") and not RegEx.create_from_string("^F\\d{3,4}$").search(String(_opts.feature)):
		printerr("perf_probe: --feature must look like F012")
		return false
	_pace_us = int(1000000.0 / pace_fps) if pace_fps > 0.0 else 0
	return true


## Numeric option; NaN (after printing the problem) when it is not a number.
func _num(key: String, fallback: float) -> float:
	if not _opts.has(key):
		return fallback
	var s: String = String(_opts[key])
	if not s.is_valid_float():
		printerr("perf_probe: --%s=%s is not a number. %s" % [key, s, USAGE])
		return NAN
	return s.to_float()


func _fail(message: String) -> void:
	printerr("perf_probe: " + message)
	_done = true
	_cleanup()
	quit(2)


func _finish() -> void:
	_done = true
	_cleanup()
	var end_rss: float = rss_mb()  # also covers windows too short for the once-a-second sample
	if end_rss > 0.0:
		_rss.append(end_rss)
	if _frame_ms.size() < MIN_FRAMES:
		printerr("perf_probe: only %d frames measured in %.1f s of game time; need at least %d (a windowed run needs a visible window; try --headless for CPU-only metrics)" % [_frame_ms.size(), _window_sec, MIN_FRAMES])
		quit(2)
		return
	var report: Dictionary = _build_report()
	if not Cli.write_text(_out, JSON.stringify(report, "  ") + "\n"):
		quit(2)
		return
	var f: Dictionary = report.frame_ms
	print("perf %s verdict=%s frames=%d fps.avg=%s frame_ms.p95=%s max=%s memory_mb.peak=%s violations=%s" % [
		"headless (CPU-only)" if _headless else "windowed", report.verdict, _frame_ms.size(), report.fps.avg, f.p95, f.max,
		report.memory_mb.peak if report.has("memory_mb") else "n/a", JSON.stringify(report.violations)])
	if _headless:
		printerr("perf_probe: headless run, CPU-only metrics (no rendering, draw_calls and gpu_ms are null); not valid perf-gate evidence for a device.")
	quit(0 if report.verdict == "pass" else 1)


func _build_report() -> Dictionary:
	var stats: Dictionary = summarize(_frame_ms)
	var fps_avg: float = 1000.0 / maxf(stats.mean, 0.0001)
	var fps_p1: float = 1000.0 / maxf(stats.p99, 0.0001)
	var n: int = _frame_ms.size()
	var report: Dictionary = {
		"schema_version": "1.0",
		"build": String(_opts.get("build", _default_build())),
		"device": _device(),
		"scenario": String(_opts.get("scenario", "bot-driven game scene (greedy bot, seed %d, %d game(s), %d moves), %s" % [
			_seed, _episodes, _moves, "headless, CPU-only" if _headless else "windowed"])),
		"duration_sec": _r(_window_sec, 0.001),
		"fps": {"avg": _r(fps_avg, 0.1), "p1_low": _r(fps_p1, 0.1)},
		"frame_ms": {"p50": _r(stats.p50), "p95": _r(stats.p95), "p99": _r(stats.p99), "mean": _r(stats.mean),
			"max": _r(stats.max), "warmup_max": _r(_warm_max)},
		"draw_calls": null if _headless else _r(_draw_sum / n, 0.1),
		"cpu_ms": _r(_cpu_sum / n),
		"gpu_ms": _r(_gpu_sum / n) if _gpu_seen else null,
		"budgets": _budgets,
		"headless": _headless,
		"frames": n,
		"frames_over_budget": _count_over(_frame_ms, float(_budgets.frame_ms_p95)),
		"games": _episodes,
		"moves": _moves,
		"seed": _seed,
		"debug_build": OS.is_debug_build(),
		"godot": Engine.get_version_info().string,
		"renderer": "none (headless)" if _headless else "%s (%s)" % [RenderingServer.get_current_rendering_method(), RenderingServer.get_current_rendering_driver_name()],
	}
	if _engine_fps.size() > 0:
		var lo: float = _engine_fps[0]
		var total: float = 0.0
		for v in _engine_fps:
			lo = minf(lo, v)
			total += v
		report.fps.engine_avg = _r(total / _engine_fps.size(), 0.1)
		report.fps.engine_min = _r(lo, 0.1)
	var mem: Dictionary = _memory_report()
	if not mem.is_empty():
		report.memory_mb = mem
	if _cold_start_sec >= 0.0:
		report.cold_start_sec = _r(_cold_start_sec, 0.001)
	if _opts.has("feature"):
		report.feature_id = String(_opts.feature)
	if _keep_frames:
		var series: Array = []
		for v in _frame_ms:
			series.append(_r(v))
		report.frames_ms = series
	var peak_mb: float = report.memory_mb.peak if report.has("memory_mb") else -1.0
	report.violations = judge(fps_avg, stats.p95, peak_mb, _budgets)
	report.verdict = "pass" if report.violations.is_empty() else "fail"
	report.notes = _notes(report)
	return report


func _memory_report() -> Dictionary:
	if _rss.size() > 0:
		var peak: float = 0.0
		var total: float = 0.0
		for v in _rss:
			peak = maxf(peak, v)
			total += v
		return {"peak": _r(peak, 0.1), "avg": _r(total / _rss.size(), 0.1), "start": _r(_rss[0], 0.1), "end": _r(_rss[_rss.size() - 1], 0.1),
			"basis": "rss", "engine_peak": _r(_mem_peak, 0.1)}
	if _mem_peak > 0.0:
		return {"peak": _r(_mem_peak, 0.1), "avg": _r(_mem_sum / _mem_n, 0.1), "start": _r(_mem_first, 0.1), "end": _r(_mem_last, 0.1),
			"basis": "engine"}
	return {}  # nothing measurable (release build without monitors, no RSS source): the memory budget is skipped


func _device() -> Dictionary:
	var gpu: String = RenderingServer.get_video_adapter_name()
	var dev_name: String = "desktop-headless" if _headless else "desktop (%s%s)" % [OS.get_processor_name(), (", GPU " + gpu) if gpu != "" else ""]
	var dev: Dictionary = {"name": String(_opts.get("device-name", dev_name)), "os": "%s %s" % [OS.get_name(), OS.get_version()]}
	if _opts.has("tier"):
		dev.tier = String(_opts.tier)
	return dev


func _default_build() -> String:
	return "%s %s (godot %s%s)" % [ProjectSettings.get_setting("application/config/name", "game"),
		ProjectSettings.get_setting("application/config/version", "0.1.0"), Engine.get_version_info().string,
		", editor/debug binary" if OS.is_debug_build() else ""]


func _notes(report: Dictionary) -> String:
	var parts: PackedStringArray = []
	if _headless:
		parts.append("HEADLESS RUN (CPU-only): there is no renderer, so draw_calls and gpu_ms are null and frame_ms covers script and scene-tree work only, not rendering. Frames were %s; work time is measured before any pacing wait." % (
			"unpaced (stepped by the engine, e.g. --fixed-fps)" if _pace_us == 0 else "paced at %s fps by the probe" % snappedf(1000000.0 / _pace_us, 0.1)))
	else:
		parts.append("Desktop proxy, not a device capture. The window ran at the project's own pacing; frame_ms is per-frame CPU work (scene processing + render CPU + frame setup) without vsync or present waits.%s" % (
			" GPU time came from the driver." if _gpu_seen else " The driver reports no GPU timing, so gpu_ms is null and frame_ms is CPU-only."))
	parts.append("Bot: greedy, %d game(s), %d moves, seed %d; measured window %s s after %s s warm-up (warm-up frames are excluded; frame_ms.warmup_max is the worst of them)." % [_episodes, _moves, _seed, report.duration_sec, str(_warmup)])
	parts.append("fps.avg and fps.p1_low derive from frame_ms (capacity); fps.engine_avg and fps.engine_min are the engine's delivered rate.")
	if report.has("memory_mb"):
		if report.memory_mb.basis == "rss":
			parts.append("memory_mb is process RSS sampled once a second; memory_mb.engine_peak is the engine's per-frame static + video memory.")
		else:
			parts.append("memory_mb is the engine's own accounting (static + video memory) because the OS offers no RSS reading here; it excludes the engine baseline.")
	else:
		parts.append("Memory could not be measured in this build, so the memory budget was not checked.")
	if OS.is_debug_build():
		parts.append("Editor/debug binary: re-measure on the target device with a release export before using this as perf-gate evidence.")
	return " ".join(parts)


func _cleanup() -> void:
	if _save != null:
		for suffix in ["", ".bak", ".tmp"]:
			var p: String = ProjectSettings.globalize_path(PROBE_SAVE + suffix)
			if FileAccess.file_exists(PROBE_SAVE + suffix):
				DirAccess.remove_absolute(p)


static func _r(v: float, step: float = 0.0001) -> float:
	return snappedf(v, step)


## How many frames took longer than limit_ms (hitches beyond the frame budget).
static func _count_over(frames_ms: PackedFloat64Array, limit_ms: float) -> int:
	var count: int = 0
	for v in frames_ms:
		if v > limit_ms:
			count += 1
	return count


## Linear-interpolated percentile of an ascending array (same method as scripts/perf_budget.py).
static func percentile(sorted_vals: PackedFloat64Array, p: float) -> float:
	var n: int = sorted_vals.size()
	if n == 0:
		return 0.0
	var k: float = float(n - 1) * p / 100.0
	var lo: int = int(k)
	var hi: int = mini(lo + 1, n - 1)
	return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (k - float(lo))


## {frames, mean, p50, p95, p99, max} of a frame-time series in ms.
static func summarize(frames_ms: PackedFloat64Array) -> Dictionary:
	var s: PackedFloat64Array = frames_ms.duplicate()
	s.sort()
	var n: int = s.size()
	if n == 0:
		return {"frames": 0, "mean": 0.0, "p50": 0.0, "p95": 0.0, "p99": 0.0, "max": 0.0}
	var total: float = 0.0
	for v in s:
		total += v
	return {"frames": n, "mean": total / n, "p50": percentile(s, 50.0), "p95": percentile(s, 95.0), "p99": percentile(s, 99.0), "max": s[n - 1]}


## Budget violations as human-readable strings (empty = pass). A negative peak_mb means memory was not measured.
## Budgets: fps_target (avg fps must reach 95 percent of it), frame_ms_p95, memory_mb.
static func judge(avg_fps: float, p95_ms: float, peak_mb: float, budgets: Dictionary) -> Array[String]:
	var out: Array[String] = []
	if budgets.has("fps_target") and avg_fps < FPS_TOLERANCE * float(budgets.fps_target):
		out.append("fps.avg %s < %s (95%% of fps_target %s)" % [snappedf(avg_fps, 0.1), snappedf(FPS_TOLERANCE * float(budgets.fps_target), 0.1), budgets.fps_target])
	if budgets.has("frame_ms_p95") and p95_ms > float(budgets.frame_ms_p95):
		out.append("frame_ms.p95 %s > budget %s" % [snappedf(p95_ms, 0.0001), budgets.frame_ms_p95])
	if budgets.has("memory_mb") and peak_mb >= 0.0 and peak_mb > float(budgets.memory_mb):
		out.append("memory_mb.peak %s > budget %s" % [snappedf(peak_mb, 0.1), budgets.memory_mb])
	return out


## Greedy bot (same policy as tools/playtest/runner.gd): maximise (score gain, empty cells) over legal moves.
static func greedy_move(grid: Array[int], size: int) -> String:
	var best: String = ""
	var best_key: float = -1.0
	for d in Sim.DIRS:
		var r: Dictionary = Sim.slide_grid(grid, size, d)
		if not r.moved:
			continue
		var empties: int = r.grid.count(0)
		var key: float = float(r.gain) * 100.0 + float(empties)
		if key > best_key:
			best_key = key
			best = d
	return best


## Resident set size of this process in MB, or -1.0 when the OS offers no cheap reading (Windows, restricted shells).
static func rss_mb() -> float:
	if FileAccess.file_exists("/proc/self/status"):  # Linux, Android
		for line in FileAccess.get_file_as_string("/proc/self/status").split("\n"):
			if line.begins_with("VmRSS:"):
				return line.get_slice(":", 1).strip_edges().get_slice(" ", 0).to_float() / 1024.0
		return -1.0
	if OS.get_name() in ["macOS", "FreeBSD", "NetBSD", "OpenBSD"]:
		var out: Array = []
		if OS.execute("ps", ["-o", "rss=", "-p", str(OS.get_process_id())], out) == 0 and out.size() > 0:
			return String(out[0]).strip_edges().to_float() / 1024.0
	return -1.0
