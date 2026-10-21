extends SceneTree
## Playtest runner -> playtest-report JSON (schema_version 1.0). Exit 0 verdict pass, 1 fail, 2 usage error.
##   -- --mode=script --script=res://tests/playthroughs/smoke.json --out=<abs>.json [--seed=1]
##   -- --mode=bot --bot=greedy|random --runs=200 --seed=1 --out=<abs>.json
## Time metrics are estimates: SEC_PER_MOVE seconds per accepted move.

const Cli = preload("res://tools/ci/cli.gd")
const Sim = preload("res://core/sim.gd")
const Rng = preload("res://core/rng.gd")

const SEC_PER_MOVE: float = 0.8
const MAX_MOVES: int = 5000  # a run longer than this without ending counts as a softlock


func _initialize() -> void:
	var a: Dictionary = Cli.args()
	var report: Dictionary
	match String(a.get("mode", "")):
		"script": report = _run_script(a)
		"bot": report = _run_bots(a)
		_:
			printerr("usage: --mode=script|bot (see header of tools/playtest/runner.gd)")
			quit(2)
			return
	if report.is_empty():
		quit(2)
		return
	var text: String = JSON.stringify(report, "  ")
	if not Cli.write_text(String(a.get("out", "")), text + "\n"):
		quit(2)
		return
	print("%s verdict=%s metrics=%s" % [report.mode, report.verdict, JSON.stringify(report.metrics)])
	quit(0 if report.verdict == "pass" else 1)


func _base(mode: String, runs: int, seed_value: int) -> Dictionary:
	return {
		"schema_version": "1.0", "build": "godot-mobile-template", "mode": mode, "runs": runs,
		"seed": seed_value, "steps": [], "screenshots": [], "findings": [],
		"metrics": {"win_rate": 0.0, "avg_session_sec": 0.0, "time_to_first_reward_sec": 0.0,
			"softlocks": 0, "crashes": 0, "errors": 0},
		"verdict": "pass",
	}


func _run_script(a: Dictionary) -> Dictionary:
	var path: String = String(a.get("script", ""))
	var spec: Variant = JSON.parse_string(FileAccess.get_file_as_string(path)) if path != "" else null
	if not (spec is Dictionary) or not (spec.get("steps") is Array):
		printerr("cannot read playthrough script: '%s'" % path)
		return {}
	var seed_value: int = int(a.get("seed", spec.get("seed", 1)))
	var report: Dictionary = _base("deterministic_script", 1, seed_value)
	var sim: Sim = Sim.new(seed_value)
	var ok_all: bool = true
	var t: int = 0
	for step in spec.steps:
		sim.apply(step.get("action", {}))
		var expect: Dictionary = step.get("expect", {})
		var observed: Dictionary = {}
		var ok: bool = true
		for key in expect:
			var got: Variant = sim.state.lookup(String(key))
			observed[key] = got
			ok = ok and _matches(got, expect[key])
		report.steps.append({"t": t, "action": step.get("action", {}), "expect": expect, "observed": observed, "ok": ok})
		if not ok:
			ok_all = false
			report.findings.append({"severity": "major", "title": "expectation failed at step %d" % t,
				"detail": "expected %s, observed %s" % [JSON.stringify(expect), JSON.stringify(observed)],
				"repro": "seed=%d, steps 0..%d of %s" % [seed_value, t, path]})
		t += 1
	report.metrics.win_rate = 1.0 if sim.state.status == "won" else 0.0
	report.metrics.avg_session_sec = sim.state.moves * SEC_PER_MOVE
	report.metrics.errors = report.findings.size()
	report.verdict = "pass" if ok_all else "fail"
	return report


func _matches(got: Variant, want: Variant) -> bool:
	if want is Dictionary:
		var v: Variant = want.get("value")
		match String(want.get("op", "==")):
			">=": return got != null and float(got) >= float(v)
			"<=": return got != null and float(got) <= float(v)
			">": return got != null and float(got) > float(v)
			"<": return got != null and float(got) < float(v)
			"!=": return got != v
			_: return got == v
	if (got is int or got is float) and (want is int or want is float):
		return is_equal_approx(float(got), float(want))
	return got == want


func _run_bots(a: Dictionary) -> Dictionary:
	var bot: String = String(a.get("bot", "greedy"))
	var runs: int = int(a.get("runs", 200))
	var seed_value: int = int(a.get("seed", 1))
	if not (bot in ["greedy", "random"]) or runs < 1:
		printerr("usage: --bot=greedy|random --runs=N (N >= 1)")
		return {}
	var report: Dictionary = _base("bot", runs, seed_value)
	var wins: int = 0
	var softlocks: int = 0
	var total_moves: int = 0
	var first_reward_moves: int = 0
	for r in runs:
		var sim: Sim = Sim.new(seed_value + r)
		var chooser: Rng = Rng.new(seed_value * 7919 + r)
		var first_reward: int = -1
		while sim.state.status == "playing" and sim.state.moves < MAX_MOVES:
			var dir: String = _pick(sim, bot, chooser)
			if dir == "":
				break
			var events: Array = sim.apply({"type": "move", "dir": dir})
			if first_reward < 0 and sim.state.score > 0:
				first_reward = sim.state.moves
			if events[0].type == "rejected":
				break
		if sim.state.status == "won":
			wins += 1
		elif sim.state.status == "playing":
			softlocks += 1
		total_moves += sim.state.moves
		first_reward_moves += maxi(first_reward, 0)
	var m: Dictionary = report.metrics
	m.win_rate = float(wins) / runs
	m.avg_session_sec = float(total_moves) / runs * SEC_PER_MOVE
	m.time_to_first_reward_sec = float(first_reward_moves) / runs * SEC_PER_MOVE
	m.softlocks = softlocks
	if softlocks > 0:
		report.findings.append({"severity": "blocker", "title": "softlock",
			"detail": "%d of %d runs neither ended nor had a move available" % [softlocks, runs],
			"repro": "--mode=bot --bot=%s --seed=%d --runs=%d" % [bot, seed_value, runs]})
	report.verdict = "pass" if softlocks == 0 and m.crashes == 0 else "fail"
	return report


## Greedy: maximise (score gain, empty cells) over legal moves without spawning. Random: any legal move.
func _pick(sim: Sim, bot: String, chooser: Rng) -> String:
	var best: String = ""
	var best_key: float = -1.0
	var legal: Array[String] = []
	for d in Sim.DIRS:
		var r: Dictionary = Sim.slide_grid(sim.state.grid, sim.state.size, d)
		if not r.moved:
			continue
		legal.append(d)
		var empties: int = r.grid.count(0)
		var key: float = float(r.gain) * 100.0 + empties
		if key > best_key:
			best_key = key
			best = d
	if legal.is_empty():
		return ""
	return best if bot == "greedy" else legal[chooser.rand_int(legal.size())]
