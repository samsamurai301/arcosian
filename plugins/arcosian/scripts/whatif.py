#!/usr/bin/env python3
"""What-if predictions: run the current version and a proposed change through the same bots or simulator on the
same seeds, then report the predicted difference with ranges and a verdict against the design contract's targets.

  whatif.py --set KEY=VALUE [--set ...] [--sim auto|godot|economy|match3] [--runs 100] [--seeds 5] [--seed 1]
            [--bot greedy] [--model ECONOMY.json] [--level LEVEL.json] [--label TEXT] [--root DIR] [--json] [--no-save]
  whatif.py --selftest

Simulators:
  godot    the project's own bots: tools/playtest/runner.gd --mode=bot --tuning=<overrides> (Godot templates; needs a
           Godot binary on GODOT_BIN or PATH). KEY is a tuning key from the project's tuning JSON.
  economy  scripts/economy_sim.py on an economy-model JSON. KEY is a dotted path into the model; a list item can be
           picked by its id or name (offers.starter_pack.price_usd) or by index (nodes.0.amount).
  match3   scripts/match3_sim.py on a match-3 level spec. KEY is a dotted path into the level.
VALUE is JSON (512, 0.2, true, "text") or a relative change: *1.25 (multiply) or +=10 (add).

Each seed runs the baseline and the variant with identical random streams, so the per-seed difference is paired.
Ranges are 90% intervals: Wilson over all runs for win rates (Newcombe for the change), Student t over seeds for
everything else (no interval with one seed). Results are saved to
.gamestudio/whatif/<time>-<label>.json, which the dashboard shows. Exit codes: 0 ran (any verdict), 1 the variant
breaks a hard rule (softlocks, crashes, errors, economy check), 2 usage error or the simulator could not run.
"""
import argparse
import copy
import json
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gslib as G  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent
HARD_METRICS = ("softlocks", "crashes", "errors", "economy_failed")
PROPORTIONS = ("win_rate",)  # per-run successes: Wilson intervals over all runs, Newcombe for the change
T90 = {1: 6.314, 2: 2.920, 3: 2.353, 4: 2.132, 5: 2.015, 6: 1.943, 7: 1.895, 8: 1.860, 9: 1.833, 10: 1.812,
       12: 1.782, 15: 1.753, 20: 1.725, 30: 1.697}


class WhatIfError(Exception):
    pass


# --------------------------------------------------------------------------
# changes
# --------------------------------------------------------------------------

def parse_set(item: str) -> Tuple[str, str]:
    if "=" not in item:
        raise WhatIfError("--set needs KEY=VALUE, got %r" % item)
    k, v = item.split("=", 1)
    if not k.strip():
        raise WhatIfError("--set needs a key, got %r" % item)
    return k.strip(), v.strip()


def apply_value(old: Any, raw: str) -> Any:
    """New value from the raw --set text: JSON, '*factor' or '+=delta' relative to old."""
    if raw.startswith("*") or raw.startswith("+="):
        if not isinstance(old, (int, float)) or isinstance(old, bool):
            raise WhatIfError("relative change %r needs a numeric current value, found %r" % (raw, old))
        try:
            n = float(raw[1:] if raw.startswith("*") else raw[2:])
        except ValueError:
            raise WhatIfError("bad relative change %r" % raw)
        new = old * n if raw.startswith("*") else old + n
        return int(round(new)) if isinstance(old, int) and float(new).is_integer() else new
    try:
        return json.loads(raw)
    except ValueError:
        return raw


def _step(node: Any, seg: str) -> Tuple[Any, Any]:
    """(container key, child) for one path segment; lists accept an index or an element's id/name."""
    if isinstance(node, dict):
        if seg not in node:
            raise KeyError(seg)
        return seg, node[seg]
    if isinstance(node, list):
        if re.fullmatch(r"-?\d+", seg):
            i = int(seg)
            return i, node[i]
        for i, el in enumerate(node):
            if isinstance(el, dict) and (el.get("id") == seg or el.get("name") == seg):
                return i, el
    raise KeyError(seg)


def get_path(doc: Any, path: str) -> Any:
    node = doc
    for seg in path.split("."):
        _, node = _step(node, seg)
    return node


def set_path(doc: Any, path: str, raw: str) -> Tuple[Any, Any]:
    """Set a dotted path in doc (in place). Returns (old, new)."""
    segs = path.split(".")
    node = doc
    for seg in segs[:-1]:
        _, node = _step(node, seg)
    key, old = _step(node, segs[-1])
    new = apply_value(old, raw)
    node[key] = new
    return old, new


# --------------------------------------------------------------------------
# statistics
# --------------------------------------------------------------------------

def t90(df: int) -> float:
    if df <= 0:
        return float("nan")
    for k in sorted(T90):
        if df <= k:
            return T90[k]
    return 1.645


def wilson(p: float, n: int, z: float = 1.645) -> Tuple[float, float]:
    """90% Wilson score interval for a proportion p observed over n runs."""
    if n <= 0:
        return p, p
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(max(p * (1 - p), 0.0) / n + z * z / (4 * n * n)) / den
    return max(0.0, centre - half), min(1.0, centre + half)


def summarise(xs: List[float]) -> Dict[str, Any]:
    n = len(xs)
    mean = sum(xs) / n
    out = {"mean": round(mean, 4), "min": round(min(xs), 4), "max": round(max(xs), 4), "n": n}
    if n >= 2:
        sd = math.sqrt(sum((x - mean) ** 2 for x in xs) / (n - 1))
        half = t90(n - 1) * sd / math.sqrt(n)
        out.update({"lo": round(mean - half, 4), "hi": round(mean + half, 4)})
    return out


# --------------------------------------------------------------------------
# simulators
# --------------------------------------------------------------------------

def find_godot() -> Optional[str]:
    for env in ("GODOT_BIN", "GODOT"):
        v = os.environ.get(env)
        if v and Path(v).exists():
            return v
    for name in ("godot", "godot4", "Godot"):
        w = shutil.which(name)
        if w:
            return w
    mac = Path("/Applications/Godot.app/Contents/MacOS/Godot")
    return str(mac) if mac.exists() else None


def tuning_file(eng_root: Path) -> Optional[Path]:
    for cand in (eng_root / "core" / "data" / "tuning.json", eng_root / "data" / "tuning.json"):
        if cand.is_file():
            return cand
    found = sorted(p for p in eng_root.rglob("tuning*.json") if ".godot" not in p.parts and ".gamestudio" not in p.parts)
    return found[0] if found else None


def run_godot(eng_root: Path, godot: str, runs: int, seed: int, bot: str, overrides: Optional[Dict[str, Any]],
              tmp: Path) -> Dict[str, float]:
    out = tmp / ("godot-%d-%s.json" % (seed, "v" if overrides else "b"))
    cmd = [godot, "--headless", "--path", str(eng_root), "-s", "res://tools/playtest/runner.gd", "--",
           "--mode=bot", "--bot=" + bot, "--runs=%d" % runs, "--seed=%d" % seed, "--out=" + str(out)]
    if overrides:
        ov = tmp / "overrides.json"
        ov.write_text(json.dumps(overrides), encoding="utf-8")
        cmd.append("--tuning=" + str(ov))
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise WhatIfError("could not run Godot: %s" % exc)
    if p.returncode not in (0, 1) or not out.is_file():
        raise WhatIfError("the bot runner failed (exit %d): %s" % (p.returncode, (p.stderr or p.stdout)[-400:]))
    m = json.loads(out.read_text(encoding="utf-8")).get("metrics", {})
    return {k: float(v) for k, v in m.items() if isinstance(v, (int, float)) and not isinstance(v, bool)}


def run_py(script: str, args: List[str]) -> Dict[str, Any]:
    cmd = [sys.executable, str(SCRIPTS / script)] + args + ["--json"]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    try:
        return json.loads(p.stdout)
    except ValueError:
        raise WhatIfError("%s failed (exit %d): %s" % (script, p.returncode, (p.stderr or p.stdout)[-400:]))


def economy_metrics(rep: Dict[str, Any]) -> Dict[str, float]:
    m: Dict[str, float] = {}
    for k, v in (rep.get("overall") or {}).items():
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            m[k] = float(v)
    for name, a in (rep.get("archetypes") or {}).items():
        content = a.get("content") or {}
        for k in ("days_to_finish_p50", "finished_pct"):
            if isinstance(content.get(k), (int, float)):
                m["%s.%s" % (name, k)] = float(content[k])
        for k in ("payer_pct", "spend_usd_per_user", "ad_views_per_user"):
            if isinstance(a.get(k), (int, float)) and not isinstance(a.get(k), bool):
                m["%s.%s" % (name, k)] = float(a[k])
    m["warnings"] = float(len(rep.get("warnings") or []))
    m["economy_failed"] = 0.0 if rep.get("ok", True) else 1.0
    return m


def match3_metrics(rep: Dict[str, Any]) -> Dict[str, float]:
    m = {k: float(v) for k, v in rep.items() if isinstance(v, (int, float)) and not isinstance(v, bool)}
    ml = rep.get("moves_left") or {}
    if isinstance(ml.get("mean"), (int, float)):
        m["moves_left_mean"] = float(ml["mean"])
    return m


# --------------------------------------------------------------------------
# targets and verdict
# --------------------------------------------------------------------------

def targets_for(sim: str, contract: Dict[str, Any], doc: Optional[Dict[str, Any]], tol: float) -> Dict[str, Tuple[float, float]]:
    """metric -> (low, high) band the design wants."""
    t: Dict[str, Tuple[float, float]] = {}
    diff = ((contract.get("progression") or {}).get("difficulty") or {})
    kpi = ((contract.get("analytics") or {}).get("kpi_targets") or {})
    if sim == "godot":
        w = diff.get("target_win_rate")
        if isinstance(w, (int, float)) and w > 0:
            t["win_rate"] = (max(0.0, w - tol), min(1.0, w + tol))
        s = kpi.get("session_len_sec")
        if isinstance(s, (int, float)) and s > 0:
            t["avg_session_sec"] = (s * 0.8, s * 1.2)
    elif sim == "match3" and doc:
        w = (doc.get("difficulty_target") or {}).get("win_rate")
        if isinstance(w, (int, float)) and w > 0:
            t["win_rate"] = (max(0.0, w - tol), min(1.0, w + tol))
    elif sim == "economy" and doc:
        mt = doc.get("targets") or {}
        if isinstance(mt.get("payer_conversion"), (int, float)):
            pc = float(mt["payer_conversion"])
            t["payer_conversion"] = (pc * 0.8, pc * 1.5)
        d = mt.get("days_to_complete_content")
        if isinstance(d, (int, float)):
            for a in (doc.get("archetypes") or []):
                name = a.get("id") or a.get("name") if isinstance(a, dict) else a
                if isinstance(name, str):
                    t["%s.days_to_finish_p50" % name] = (d * 0.8, d * 1.5)
        t["warnings"] = (0.0, 0.0)
    return t


def assess(metric: str, b: Dict[str, Any], v: Dict[str, Any], d: Dict[str, Any],
           band: Optional[Tuple[float, float]]) -> Tuple[str, str]:
    """(assessment, sentence) for one metric."""
    clear = "lo" in d and (d["lo"] > 0 or d["hi"] < 0)
    if "lo" not in d:
        clear = abs(d["mean"]) > 1e-9
    if metric in HARD_METRICS:
        if v["mean"] > b["mean"] + 1e-9:
            return "breaks", "%s rises from %g to %g" % (metric, b["mean"], v["mean"])
        return "ok", ""
    if not band:
        return ("changes" if clear else "no clear change"), ""
    lo, hi = band

    def dist(x: float) -> float:
        return 0.0 if lo <= x <= hi else (lo - x if x < lo else x - hi)
    db, dv = dist(b["mean"]), dist(v["mean"])
    inside = dv == 0.0
    if not clear:
        return "no clear change", ""
    if dv < db - 1e-9:
        return "closer", "%s moves %s the target band %g-%g" % (metric, "into" if inside else "toward", lo, hi)
    if dv > db + 1e-9:
        return "further", "%s moves %s the target band %g-%g" % (metric, "out of" if db == 0.0 else "away from", lo, hi)
    return "same", ""


def verdict(rows: Dict[str, Dict[str, Any]]) -> Tuple[str, List[str]]:
    reasons = [r["why"] for r in rows.values() if r.get("why")]
    a = [r["assessment"] for r in rows.values()]
    if "breaks" in a:
        return "reject", reasons
    closer, further = a.count("closer"), a.count("further")
    if closer and further:
        return "mixed", reasons
    if closer:
        return "improves", reasons
    if further:
        return "worsens", reasons
    if any(r.get("target") for r in rows.values()):
        return "no clear effect", reasons or ["no metric with a target changed beyond noise"]
    return "unknown", reasons or ["no targets to judge against: set progression.difficulty.target_win_rate and "
                                  "analytics.kpi_targets in the contract, or targets in the model"]


# --------------------------------------------------------------------------
# main flow
# --------------------------------------------------------------------------

def run(root: Path, sets: List[str], sim: str = "auto", runs: int = 100, seeds: int = 5, seed: int = 1,
        bot: str = "greedy", model: Optional[str] = None, level: Optional[str] = None, label: Optional[str] = None,
        tol: float = 0.05, save: bool = True) -> Dict[str, Any]:
    if not sets:
        raise WhatIfError("give at least one --set KEY=VALUE")
    if runs < 1 or seeds < 1:
        raise WhatIfError("--runs and --seeds must be at least 1")
    changes = [parse_set(s) for s in sets]
    state = G.load_state(root) if G.gs_dir(root).is_dir() else {}
    contract = state.get("contract") or {}
    engine, _ver, eng_rel = G.detect_engine(root)
    eng_root = (root / (eng_rel or ".")).resolve()
    doc: Optional[Dict[str, Any]] = None
    doc_path: Optional[Path] = None

    if sim == "auto":
        if model:
            sim = "economy"
        elif level:
            sim = "match3"
        elif engine == "godot" and (eng_root / "tools/playtest/runner.gd").is_file():
            sim = "godot"
        else:
            econ = sorted((G.gs_dir(root) / "economy").glob("*.json")) if G.gs_dir(root).is_dir() else []
            if len(econ) == 1:
                sim, model = "economy", str(econ[0])
            else:
                raise WhatIfError("cannot pick a simulator: pass --sim godot (Godot template bots), --model "
                                  "<economy model> or --level <match-3 level>")

    tmp = Path(tempfile.mkdtemp(prefix="gs-whatif-"))
    applied: Dict[str, Dict[str, Any]] = {}
    try:
        if sim == "godot":
            godot = find_godot()
            if not godot:
                raise WhatIfError("no Godot binary: set GODOT_BIN or put godot on PATH")
            if not (eng_root / "tools/playtest/runner.gd").is_file():
                raise WhatIfError("this project has no tools/playtest/runner.gd (copy it from the Godot template)")
            tf = tuning_file(eng_root)
            base = json.loads(tf.read_text(encoding="utf-8")) if tf else {}
            overrides: Dict[str, Any] = {}
            for k, raw in changes:
                if k not in base:
                    raise WhatIfError("%s is not a key in %s" % (k, tf.name if tf else "the tuning file"))
                old, new = base[k], apply_value(base[k], raw)
                overrides[k] = new
                applied[k] = {"from": old, "to": new}

            def one(s: int, variant: bool) -> Dict[str, float]:
                return run_godot(eng_root, godot, runs, s, bot, overrides if variant else None, tmp)
            sim_label = "godot bots (%s)" % bot
        elif sim in ("economy", "match3"):
            src = model if sim == "economy" else level
            if not src:
                raise WhatIfError("--sim %s needs --%s PATH" % (sim, "model" if sim == "economy" else "level"))
            doc_path = Path(src)
            if not doc_path.is_absolute():
                doc_path = (root / doc_path) if (root / doc_path).exists() else Path.cwd() / doc_path
            doc = json.loads(doc_path.read_text(encoding="utf-8"))
            variant = copy.deepcopy(doc)
            for k, raw in changes:
                try:
                    old, new = set_path(variant, k, raw)
                except (KeyError, IndexError):
                    raise WhatIfError("%s is not a path in %s" % (k, doc_path.name))
                applied[k] = {"from": old, "to": new}
            bpath, vpath = tmp / "baseline.json", tmp / "variant.json"
            bpath.write_text(json.dumps(doc), encoding="utf-8")
            vpath.write_text(json.dumps(variant), encoding="utf-8")

            def one(s: int, is_variant: bool) -> Dict[str, float]:
                p = str(vpath if is_variant else bpath)
                if sim == "economy":
                    return economy_metrics(run_py("economy_sim.py", ["--model", p, "--runs", str(runs), "--seed", str(s)]))
                return match3_metrics(run_py("match3_sim.py", ["--level", p, "--runs", str(runs), "--seed", str(s),
                                                               "--bot", bot]))
            sim_label = "economy_sim.py" if sim == "economy" else "match3_sim.py (%s)" % bot
        else:
            raise WhatIfError("unknown simulator %r" % sim)

        seed_list = [seed + i * 7919 for i in range(seeds)]
        base_runs, var_runs = [], []
        for s in seed_list:
            base_runs.append(one(s, False))
            var_runs.append(one(s, True))
    finally:
        shutil.rmtree(str(tmp), ignore_errors=True)

    bands = targets_for(sim, contract, doc, tol)
    metrics = sorted(set(base_runs[0]) & set(var_runs[0]))
    rows: Dict[str, Dict[str, Any]] = {}
    for m in metrics:
        b = summarise([r[m] for r in base_runs])
        v = summarise([r[m] for r in var_runs])
        d = summarise([vr[m] - br[m] for br, vr in zip(base_runs, var_runs)])
        if m in PROPORTIONS and sim in ("godot", "match3"):
            n = runs * len(seed_list)
            (bl, bh), (vl, vh) = wilson(b["mean"], n), wilson(v["mean"], n)
            dm = v["mean"] - b["mean"]
            b.update(lo=round(bl, 4), hi=round(bh, 4))
            v.update(lo=round(vl, 4), hi=round(vh, 4))
            d.update(lo=round(dm - math.sqrt((v["mean"] - vl) ** 2 + (bh - b["mean"]) ** 2), 4),
                     hi=round(dm + math.sqrt((vh - v["mean"]) ** 2 + (b["mean"] - bl) ** 2), 4))
        band = bands.get(m)
        a, why = assess(m, b, v, d, band)
        rows[m] = {"baseline": b, "variant": v, "diff": d, "target": list(band) if band else None,
                   "assessment": a, "why": why}
    final, reasons = verdict(rows)
    slug = G.slugify(label or "-".join("%s-%s" % (k, applied[k]["to"]) for k in applied))[:60] or "change"
    result = {
        "format": "arcosian-whatif/1", "created_at": datetime.now().isoformat(timespec="seconds"),
        "label": label or ", ".join("%s %s -> %s" % (k, applied[k]["from"], applied[k]["to"]) for k in applied),
        "sim": sim, "sim_label": sim_label, "changes": applied, "runs_per_seed": runs, "seeds": seed_list,
        "source": str(doc_path) if doc_path else None, "metrics": rows, "verdict": final, "reasons": reasons,
        "command": "gs.py whatif " + " ".join("--set %s=%s" % (k, r) for k, r in changes),
    }
    if save and G.gs_dir(root).is_dir():
        out = G.gs_dir(root) / "whatif" / ("%s-%s.json" % (datetime.now().strftime("%Y%m%d-%H%M%S"), slug))
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(result, indent=1) + "\n", encoding="utf-8")
        result["saved_to"] = G.rel_to_root(out, root)
    return result


def _fmt(s: Dict[str, Any], signed: bool = False) -> str:
    f = (lambda x: "%+.3g" % x) if signed else (lambda x: "%.3g" % x)
    if "lo" in s:
        return "%s [%s, %s]" % (f(s["mean"]), f(s["lo"]), f(s["hi"]))
    return f(s["mean"])


def render(res: Dict[str, Any]) -> str:
    lines = ["What-if: %s" % res["label"],
             "Simulator: %s, %d seeds x %d runs (paired; 90%% intervals: Wilson for rates, t over seeds otherwise)"
             % (res["sim_label"], len(res["seeds"]), res["runs_per_seed"]), ""]
    w = max([len(m) for m in res["metrics"]] + [6])
    lines.append("%-*s  %-24s %-24s %-24s %-12s %s" % (w, "metric", "baseline", "variant", "change", "target", "assessment"))
    for m, r in res["metrics"].items():
        tgt = "%g-%g" % tuple(r["target"]) if r["target"] else "-"
        lines.append("%-*s  %-24s %-24s %-24s %-12s %s" % (w, m, _fmt(r["baseline"]), _fmt(r["variant"]),
                                                           _fmt(r["diff"], True), tgt, r["assessment"]))
    lines += ["", "Verdict: %s" % res["verdict"].upper()]
    lines += ["  - " + r for r in res["reasons"]]
    if res.get("saved_to"):
        lines.append("Saved: %s (shown by gs.py dashboard)" % res["saved_to"])
    lines.append("A prediction from bots and models, not players: confirm with a playtest before shipping.")
    return "\n".join(lines)


def _root(arg: Optional[str]) -> Path:
    if arg:
        return Path(arg).expanduser().resolve()
    found = G.find_project_root(Path.cwd())
    return found if found else Path.cwd().resolve()


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE")
    ap.add_argument("--sim", choices=("auto", "godot", "economy", "match3"), default="auto")
    ap.add_argument("--runs", type=int, default=100, help="runs per seed (default 100)")
    ap.add_argument("--seeds", type=int, default=5, help="independent seeds (default 5)")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--bot", default="greedy")
    ap.add_argument("--model", help="economy-model JSON (economy simulator)")
    ap.add_argument("--level", help="match-3 level spec (match3 simulator)")
    ap.add_argument("--label")
    ap.add_argument("--tolerance", type=float, default=0.05, help="win-rate band half-width (default 0.05)")
    ap.add_argument("--root")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-save", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    try:
        res = run(_root(a.root), a.set, a.sim, a.runs, a.seeds, a.seed, a.bot, a.model, a.level, a.label,
                  a.tolerance, not a.no_save)
    except WhatIfError as exc:
        print("whatif: " + str(exc), file=sys.stderr)
        return 2
    print(json.dumps(res, indent=1) if a.json else render(res))
    return 1 if res["verdict"] == "reject" else 0


# --------------------------------------------------------------------------
# selftest
# --------------------------------------------------------------------------

def selftest() -> int:
    fails: List[str] = []

    def check(cond: bool, msg: str) -> None:
        if not cond:
            fails.append(msg)
            print("FAIL: " + msg)

    check(apply_value(10, "*1.5") == 15 and apply_value(10, "+=2") == 12 and apply_value(1, "0.5") == 0.5,
          "value parsing")
    doc = {"offers": [{"id": "pack", "price": 2.99}], "days": 30, "nodes": [{"amount": 5}]}
    check(set_path(doc, "offers.pack.price", "4.99") == (2.99, 4.99) and doc["offers"][0]["price"] == 4.99, "id path")
    check(set_path(doc, "nodes.0.amount", "*2") == (5, 10), "index path")
    try:
        set_path(doc, "offers.nope.price", "1")
        check(False, "missing path must raise")
    except KeyError:
        pass
    lo, hi = wilson(1.0, 120)
    check(0.97 < lo < 0.99 and hi == 1.0, "Wilson interval at p=1 (%.3f)" % lo)
    s = summarise([0.6, 0.62, 0.64, 0.61, 0.63])
    check(abs(s["mean"] - 0.62) < 1e-9 and s["lo"] < 0.62 < s["hi"], "t interval")
    b, v = summarise([0.5, 0.52, 0.51]), summarise([0.6, 0.61, 0.62])
    d = summarise([0.1, 0.09, 0.11])
    check(assess("win_rate", b, v, d, (0.55, 0.65))[0] == "closer", "moving into the band is closer")
    check(assess("win_rate", v, b, summarise([-0.1, -0.09, -0.11]), (0.55, 0.65))[0] == "further", "leaving is further")
    check(assess("softlocks", summarise([0, 0]), summarise([1, 0]), summarise([1, 0]), None)[0] == "breaks", "hard")
    check(verdict({"a": {"assessment": "closer", "why": "x"}, "b": {"assessment": "ok", "why": ""}})[0] == "improves",
          "verdict improves")
    check(verdict({"a": {"assessment": "breaks", "why": "y"}})[0] == "reject", "verdict reject")

    tmp = Path(tempfile.mkdtemp(prefix="gs-whatif-st-"))
    try:
        example = SCRIPTS / "schemas" / "examples" / "example.economy-model.json"
        if example.is_file():
            G.init_project(tmp, "Whatif Test", "other", "puzzle", platforms=["web"])
            (G.gs_dir(tmp) / "economy").mkdir(exist_ok=True)
            shutil.copy(str(example), str(G.gs_dir(tmp) / "economy" / "model.json"))
            res = run(tmp, ["days=*0.5"], runs=20, seeds=2)
            check(res["sim"] == "economy" and res["changes"]["days"]["to"] == res["changes"]["days"]["from"] * 0.5,
                  "auto-picks the only economy model")
            check(res["metrics"] and res["verdict"] in ("improves", "worsens", "mixed", "no clear effect", "reject"),
                  "economy what-if gives a verdict (%s)" % res.get("verdict"))
            check(res.get("saved_to", "").startswith(".gamestudio/whatif/"), "result saved")
            check("Verdict:" in render(res), "render")
            try:
                run(tmp, ["no_such_key=1"], runs=5, seeds=1)
                check(False, "unknown key must fail")
            except WhatIfError as exc:
                check("not a path" in str(exc), "unknown key message")
        else:
            check(False, "example economy model missing")
    finally:
        shutil.rmtree(str(tmp), ignore_errors=True)
    if fails:
        print("whatif selftest: %d FAILED" % len(fails))
        return 1
    print("whatif selftest: OK")
    return 0


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows pipes default to the ANSI code page; Claude Code reads UTF-8
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
