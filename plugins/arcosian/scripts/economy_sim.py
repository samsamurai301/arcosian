#!/usr/bin/env python3
"""Seeded Monte Carlo agent-based simulation of an economy-model document.

  economy_sim.py --model PATH [--runs N=200] [--seed S=1] [--days D] [--json] [--out PATH]
  economy_sim.py --selftest

Model: scripts/schemas/economy-model.schema.json. --runs = simulated players PER archetype (shares only weight
overall figures); --days overrides model.days (default 30); --out always writes the full JSON report.

Per player/day/session (sessions/day = floor + Bernoulli(fraction); length jittered 0.7-1.3x): daily fires on a
day's first session, weekly on days 1, 8, 15..., per_session at each session start. Play is attempts of
levels.minutes_per_attempt (default 1.5) while levels remain; per_minute fires per whole minute played. Win chance =
the level's curve rate (difficulty_curve.gen_curve) shifted in logit space by 4*(skill-0.5), +0.15 per consecutive
fail. A win advances `level`; per_level_attempt fires, then win/loss; after a win a rewarded ad is watched with
ad_accept_rate (on_ad). Nodes: `probability` gates a firing; `condition` is a validated boolean expression over
resource ids, level, day, session. source/pool create, sink destroys inputs when affordable, converter/gate need
affordable inputs, a true condition and a non-capped output (gate blocks are counted); converters/gates on
per_session/daily/weekly repeat while affordable (max 20). Caps clamp; overflow is lost and reported.
Offers: spend_propensity is read as the chance a player is a spender at all (the example's values sum to about its
payer_conversion target); a spender rolls PAY_ROLL (5%) per offer per day when its trigger fires (a trigger name, or
a condition checked at session start). Condition-triggered offers buy once unless `repeatable: true`; `once: true`
works on any offer. A purchase fires on_purchase. No churn: everyone plays every day (engaged-player economy).

Warnings (exit 1) vs targets: days_to_complete_content (archetype id containing "engaged", else the heaviest;
+-25%), max_soft_currency_hoard_days (soft = kind "soft" or id with coin/gold/soft/cash; median peak balance /
average daily income), payer_conversion (outside 0.5x-2x). Notes: overflow > 20% of income, sink/source < 0.3.

Exit codes: 0 ok, 1 target warnings, 2 usage or model error.
"""
from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import math
import random
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

TRIGGERS = ("per_session", "per_minute", "per_level_attempt", "per_level_win", "per_level_loss",
            "daily", "weekly", "on_purchase", "on_ad")
REPEAT_TRIGGERS = ("per_session", "daily", "weekly")
MAX_REPEAT = 20
PAY_ROLL = 0.05
LEARN = 0.15
SKILL_LOGIT = 4.0
CHECKPOINTS = (1, 2, 3, 5, 7, 10, 14, 21, 30, 45, 60, 90, 120, 180, 365)
ALLOWED = (ast.Expression, ast.BoolOp, ast.And, ast.Or, ast.UnaryOp, ast.Not, ast.USub, ast.Compare, ast.Lt,
           ast.LtE, ast.Gt, ast.GtE, ast.Eq, ast.NotEq, ast.BinOp, ast.Add, ast.Sub, ast.Mult, ast.Div,
           ast.Name, ast.Load, ast.Constant)


class ModelError(Exception): """Bad model document or arguments (exit 2)."""


_spec = importlib.util.spec_from_file_location("difficulty_curve", str(Path(__file__).resolve().parent / "difficulty_curve.py"))
DC = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(DC)

def compile_cond(text: str, names: Sequence[str], where: str):
    try:
        tree = ast.parse(str(text).strip(), mode="eval")
    except SyntaxError:
        raise ModelError("%s: cannot parse condition %r" % (where, text))
    for n in ast.walk(tree):
        if not isinstance(n, ALLOWED):
            raise ModelError("%s: unsupported syntax %s in condition %r" % (where, type(n).__name__, text))
        if isinstance(n, ast.Name) and n.id not in names:
            raise ModelError("%s: unknown name %r in condition %r" % (where, n.id, text))
        if isinstance(n, ast.Constant) and not isinstance(n.value, (int, float)):
            raise ModelError("%s: only numeric constants allowed in %r" % (where, text))
    return compile(tree, "<condition>", "eval")

def pct(v: Sequence[float], q: float) -> float:
    return float(v[min(len(v) - 1, max(0, int(math.ceil(q * len(v))) - 1))]) if v else float("nan")

def amounts(d: Optional[Dict], res: Dict, where: str) -> Dict[str, float]:
    bad = [r for r in (d or {}) if r not in res]
    if bad:
        raise ModelError("%s uses unknown resource %r" % (where, bad[0]))
    return {r: float(a) for r, a in (d or {}).items()}


class Node:
    def __init__(self, d: Dict, res: Dict, names: Sequence[str]):
        self.id, self.kind, self.trigger = d["id"], d["kind"], d["trigger"]
        self.inputs = amounts(d.get("inputs"), res, "node " + self.id)
        self.outputs = amounts(d.get("outputs"), res, "node " + self.id)
        self.prob = float(d.get("probability", 1.0))
        self.cond = compile_cond(d["condition"], names, "node " + self.id) if d.get("condition") else None
        self.flow = self.kind in ("converter", "gate") or (self.kind == "pool" and bool(self.inputs))
        self.repeat = self.flow and bool(self.inputs) and self.trigger in REPEAT_TRIGGERS


class Offer:
    def __init__(self, d: Dict, res: Dict, names: Sequence[str]):
        self.id, self.price = d["id"], float(d["price_usd"])
        self.contents = amounts(d.get("contents"), res, "offer " + self.id)
        t = d.get("trigger")
        self.trig = t if t in TRIGGERS else None
        self.cond = compile_cond(t, names, "offer " + self.id) if t and t not in TRIGGERS else None
        self.once = bool(d.get("once")) or (self.cond is not None and not d.get("repeatable"))


class Model:
    def __init__(self, doc: Dict, days: Optional[int]):
        raw_nodes = doc.get("nodes") or []
        self.res = {r["id"]: r for r in doc.get("resources") or []}
        self.res_ids = list(self.res)
        if not self.res or not raw_nodes or not doc.get("archetypes"):
            raise ModelError("model needs resources, nodes and archetypes")
        if {"level", "day", "session"} & set(self.res):
            raise ModelError("resource ids level/day/session are reserved")
        names = self.res_ids + ["level", "day", "session"]
        self.caps = {r: self.res[r].get("cap") for r in self.res_ids}
        self.initial = {r: float(self.res[r].get("initial") or 0) for r in self.res_ids}
        self.by_trigger = {t: [] for t in TRIGGERS}  # type: Dict[str, List[Node]]
        for d in raw_nodes:
            n = Node(d, self.res, names)
            self.by_trigger[n.trigger].append(n)
        self.offers = [Offer(d, self.res, names) for d in doc.get("offers") or []]
        self.archetypes = doc["archetypes"]
        self.days = int(days or doc.get("days") or 30)
        lv = doc.get("levels") or {}
        self.count, self.attempt_min = int(lv.get("count") or 0), float(lv.get("minutes_per_attempt") or 1.5)
        self.rates = self._rates(lv)
        self.targets, self.name = doc.get("targets") or {}, doc.get("name", "")

    def _rates(self, lv: Dict) -> List[float]:
        if self.count < 1:
            return []
        base_wr = float(lv.get("base_win_rate", 0.8))
        dc = lv.get("difficulty_curve") or {}
        typ, p = dc.get("type"), dc.get("params") or {}
        try:
            if typ in ("linear", "sawtooth", "stepped"):
                base = float(p.get("base", base_wr))
                floor = min(base, float(p.get("floor", max(0.05, base * 0.5))))
                return DC.gen_curve(self.count, typ, base, floor, int(p.get("period", 10)), int(p.get("hard_every", 0)))
            if typ == "custom":
                wr = [float(x) for x in p["win_rates"]]
                return [wr[min(i, len(wr) - 1)] for i in range(self.count)]
        except (DC.InputError, KeyError, TypeError, ValueError, IndexError) as e:
            raise ModelError("difficulty_curve: %s" % e)
        return [base_wr] * self.count

    def win_prob(self, level: int, skill: float, fails: int) -> float:
        c = min(0.99, max(0.01, self.rates[min(level, self.count) - 1]))
        x = math.log(c / (1.0 - c)) + SKILL_LOGIT * (skill - 0.5) + LEARN * fails
        return min(0.995, max(0.005, 1.0 / (1.0 + math.exp(-x))))


class Player:
    def __init__(self, m: Model, arch: Dict, rng: random.Random):
        self.m, self.rng, self.arch = m, rng, arch
        self.s = {r: min(v, m.caps[r]) if m.caps[r] is not None else v for r, v in m.initial.items()}  # type: Dict[str, float]
        self.s.update(level=1, day=1, session=0)
        self.src, self.snk, self.over = ({r: 0.0 for r in m.res_ids} for _ in range(3))
        self.peak = dict(self.s)
        self.buys = {o.id: 0 for o in m.offers}
        self.gate_blocked = {}  # type: Dict[str, int]
        self.ads = self.fails = 0
        self.spend = 0.0
        self.finished = None  # type: Optional[int]
        self.rolled = set()  # type: set
        self.spender = rng.random() < float(arch.get("spend_propensity", 0))

    def test(self, code) -> bool:
        try:
            return bool(eval(code, {"__builtins__": {}}, self.s))
        except ZeroDivisionError:
            return False

    def add(self, r: str, amt: float) -> None:
        cap, cur = self.m.caps[r], self.s[r]
        if cap is not None and cur + amt > cap:
            self.over[r] += cur + amt - cap
            amt = cap - cur
        self.s[r] = cur + amt
        self.src[r] += amt

    def fire(self, n: Node) -> None:
        if n.prob < 1.0 and self.rng.random() >= n.prob:
            return
        s, times = self.s, 0
        while True:
            full = n.flow and n.outputs and all(self.m.caps[r] is not None and s[r] >= self.m.caps[r] for r in n.outputs)
            if full or (n.cond is not None and not self.test(n.cond)) or any(s[r] + 1e-9 < a for r, a in n.inputs.items()):
                if times == 0 and n.kind == "gate":
                    self.gate_blocked[n.id] = self.gate_blocked.get(n.id, 0) + 1
                return
            for r, a in n.inputs.items():
                s[r] -= a
                self.snk[r] += a
            for r, a in n.outputs.items():
                self.add(r, a)
            times += 1
            if not n.repeat or times >= MAX_REPEAT:
                return

    def event(self, trigger: str) -> None:
        for n in self.m.by_trigger[trigger]:
            self.fire(n)
        if not self.spender:
            return
        for o in self.m.offers:
            if (o.trig if o.trig is not None else "per_session") != trigger or o.id in self.rolled:
                continue
            if (o.once and self.buys[o.id]) or (o.cond is not None and not self.test(o.cond)):
                continue
            self.rolled.add(o.id)
            if self.rng.random() < PAY_ROLL:
                self.buys[o.id] += 1
                self.spend += o.price
                for r, a in o.contents.items():
                    self.add(r, a)
                self.event("on_purchase")

    def attempt(self) -> None:
        m, s = self.m, self.s
        win = self.rng.random() < m.win_prob(int(s["level"]), float(self.arch.get("skill", 0.5)), self.fails)
        self.event("per_level_attempt")
        if win:
            s["level"] += 1
            self.fails = 0
            self.event("per_level_win")
            if m.by_trigger["on_ad"] and self.rng.random() < float(self.arch.get("ad_accept_rate", 0)):
                self.ads += 1
                self.event("on_ad")
            if s["level"] > m.count and self.finished is None:
                self.finished = int(s["day"])
        else:
            self.fails += 1
            self.event("per_level_loss")

    def session(self, day: int, first: bool) -> None:
        m, s = self.m, self.s
        s["session"] += 1
        for trig in (("daily",) + (("weekly",) if (day - 1) % 7 == 0 else ())) if first else ():
            self.event(trig)
        self.event("per_session")
        carry = 0.0
        minutes = float(self.arch.get("session_minutes", 5)) * self.rng.uniform(0.7, 1.3)
        for _ in range(int(minutes / m.attempt_min)):
            if s["level"] <= m.count:
                self.attempt()
            carry += m.attempt_min
            for _ in range(int(carry)):
                self.event("per_minute")
            carry %= 1.0
        for r in m.res_ids:
            self.peak[r] = max(self.peak[r], s[r])

    def run(self, days: int, checkpoints: Sequence[int]) -> Dict[int, Dict[str, float]]:
        snaps = {}  # type: Dict[int, Dict[str, float]]
        spd = float(self.arch.get("sessions_per_day", 1))
        for day in range(1, days + 1):
            self.s["day"] = day
            self.rolled.clear()
            n = int(spd) + (1 if self.rng.random() < spd - int(spd) else 0)
            for k in range(n):
                self.session(day, k == 0)
            if day in checkpoints:
                snaps[day] = dict(self.s)
        return snaps

def q3(rows: List[List[float]], nd: int = 2) -> Dict[str, List[float]]:
    return {k: [round(pct(v, q), nd) for v in rows] for k, q in (("p10", .1), ("p50", .5), ("p90", .9))}

def aggregate(m: Model, arch: Dict, players: List[Player], snaps: List[Dict], cps: List[int], notes: List[str]) -> Dict:
    n, D, aid = len(players), m.days, arch["id"]
    fin = sorted(p.finished if p.finished is not None else D + 1 for p in players)
    flows, hoard = {}, {}
    for r in m.res_ids:
        src, snk, over = (sum(getattr(p, k)[r] for p in players) for k in ("src", "snk", "over"))
        flows[r] = {"sourced_per_user": round(src / n, 2), "sunk_per_user": round(snk / n, 2),
                    "overflow_per_user": round(over / n, 2), "sink_source_ratio": round(snk / src, 3) if src > 0 else None}
        idx = sorted(p.peak[r] / (p.src[r] / D) for p in players if p.src[r] > 0)
        hoard[r] = {"p50": round(pct(idx, .5), 2), "p90": round(pct(idx, .9), 2)} if idx else None
        if src > 0 and over > 0.2 * (src + over):
            notes.append("%s/%s: over 20%% of income is lost to the cap" % (aid, r))
        if src > 0 and snk / src < 0.3 and m.caps[r] is None:
            notes.append("%s/%s: sink/source %.2f (weak sinks, inflation risk)" % (aid, r, snk / src))
    gates = {}  # type: Dict[str, float]
    for p in players:
        for k, v in p.gate_blocked.items():
            gates[k] = round(gates.get(k, 0.0) + v / n, 2)
    fday = lambda q: pct(fin, q) if pct(fin, q) <= D else None
    return {"players": n, "balances": {r: q3([sorted(sn[d][r] for sn in snaps) for d in cps]) for r in m.res_ids},
            "level": q3([sorted(sn[d]["level"] for sn in snaps) for d in cps], 1),
            "content": {"finished_pct": round(100.0 * sum(1 for p in players if p.finished) / n, 1),
                        "days_to_finish_p50": fday(.5), "days_to_finish_p90": fday(.9)},
            "hoarding_index_days": hoard, "flows": flows, "gate_blocked_per_user": gates,
            "purchases_per_user": {o.id: round(sum(p.buys[o.id] for p in players) / n, 3) for o in m.offers},
            "ad_views_per_user": round(sum(p.ads for p in players) / n, 2),
            "spend_usd_per_user": round(sum(p.spend for p in players) / n, 2),
            "payer_pct": round(100.0 * sum(1 for p in players if sum(p.buys.values())) / n, 2)}

def check_targets(m: Model, rep: Dict) -> List[str]:
    w, t, A, ov = [], m.targets, rep["archetypes"], rep["overall"]
    ref = next((a for a in m.archetypes if "engaged" in a["id"]), None) or max(
        m.archetypes, key=lambda a: float(a.get("sessions_per_day", 1)) * float(a.get("session_minutes", 5)))
    tgt, got = t.get("days_to_complete_content"), A[ref["id"]]["content"]["days_to_finish_p50"]
    if tgt and m.count > 0:
        if got is None and m.days >= tgt * 1.25:
            w.append("content: %s median does not finish %d levels in %d days (target %s)" % (ref["id"], m.count, m.days, tgt))
        elif got is not None and got < tgt * 0.75:
            w.append("content: %s median finishes in %s days, target %s: content runs out too fast" % (ref["id"], got, tgt))
        elif got is not None and got > tgt * 1.25:
            w.append("content: %s median needs %s days, target %s: progression too slow" % (ref["id"], got, tgt))
    soft = [r for r in m.res_ids if m.res[r].get("kind") == "soft" or any(k in r for k in ("coin", "gold", "soft", "cash"))]
    lim = t.get("max_soft_currency_hoard_days")
    for aid, a in A.items():
        for r in soft:
            h = a["hoarding_index_days"][r]
            if lim is not None and h and h["p50"] > lim:
                w.append("hoarding: %s/%s median peak balance is %.1f days of income (max %s): sinks too weak" % (aid, r, h["p50"], lim))
    pc = t.get("payer_conversion")
    if pc and m.offers and not (0.5 * pc <= ov["payer_conversion"] <= 2.0 * pc):
        w.append("monetization: payer conversion %.2f%% vs target %.2f%%" % (100 * ov["payer_conversion"], 100 * pc))
    return w

def simulate(m: Model, runs: int, seed: int) -> Dict:
    cps = ([d for d in CHECKPOINTS if d < m.days] + [m.days])[-10:]
    rep = {"model": m.name, "seed": seed, "runs_per_archetype": runs, "days": m.days, "checkpoints": cps,
           "archetypes": {}, "notes": []}  # type: Dict[str, Any]
    tot = sum(float(a.get("share", 0)) for a in m.archetypes) or 1.0
    if abs(tot - 1.0) > 0.01 or m.count < 1:
        rep["notes"].append("archetype shares sum to %.3f (normalised); levels.count %d" % (tot, m.count))
    conv = arpdau = 0.0
    for ai, arch in enumerate(m.archetypes):
        players = [Player(m, arch, random.Random("%s:%d:%d" % (seed, ai, i))) for i in range(runs)]
        snaps = [p.run(m.days, cps) for p in players]
        a = rep["archetypes"][arch["id"]] = aggregate(m, arch, players, snaps, cps, rep["notes"])
        a["share"] = round(float(arch.get("share", 0)) / tot, 4)
        conv += a["share"] * a["payer_pct"] / 100.0
        arpdau += a["share"] * a["spend_usd_per_user"] / m.days
    rep["overall"] = {"payer_conversion": round(conv, 4), "arpdau_usd": round(arpdau, 4)}
    rep["warnings"] = check_targets(m, rep)
    rep["ok"] = not rep["warnings"]
    return rep

def fmt(v: float) -> str:
    return "%.1fM" % (v / 1e6) if abs(v) >= 1e6 else ("%.1fk" % (v / 1e3) if abs(v) >= 1e4 else "%.0f" % v)

def text_report(rep: Dict) -> str:
    out = ["Economy simulation: %s | %d days, %d players per archetype, seed %s" % (
        rep["model"] or "(unnamed)", rep["days"], rep["runs_per_archetype"], rep["seed"])]
    row = lambda label, vals: "%-18s" % label + "".join("%9s" % fmt(v) for v in vals)
    for aid, a in rep["archetypes"].items():
        c, D = a["content"], rep["days"]
        out += ["", "== %s (share %.0f%%) ==" % (aid, 100 * a["share"]), row("day", rep["checkpoints"])]
        out += [row("level " + k, v) for k, v in a["level"].items()]
        out += [row("%s %s" % (r[:11], k), v) for r, b in a["balances"].items() for k, v in b.items()]
        out.append("content: %s%% finish all levels; days to finish p50 %s, p90 %s" % (
            c["finished_pct"], c["days_to_finish_p50"] or ">%d" % D, c["days_to_finish_p90"] or ">%d" % D))
        out.append("%-14s %11s %11s %9s %11s %9s" % ("resource", "sourced/usr", "sunk/usr", "sink/src", "overflow", "hoard d50"))
        for r, f in a["flows"].items():
            h, ratio = a["hoarding_index_days"][r], f["sink_source_ratio"]
            out.append("%-14s %11s %11s %9s %11s %9s" % (
                r[:14], fmt(f["sourced_per_user"]), fmt(f["sunk_per_user"]), "-" if ratio is None else "%.2f" % ratio,
                fmt(f["overflow_per_user"]), "-" if not h else "%.1f" % h["p50"]))
        out.append("ads/user %.1f | purchases/user: %s | spend/user $%.2f | payers %.1f%%" % (
            a["ad_views_per_user"], ", ".join("%s %.2f" % kv for kv in a["purchases_per_user"].items()) or "none",
            a["spend_usd_per_user"], a["payer_pct"]))
        out += ["gate blocks/user: %s" % a["gate_blocked_per_user"]] * bool(a["gate_blocked_per_user"])
    o = rep["overall"]
    out += ["", "Overall: payer conversion %.2f%%, ARPDAU $%.3f" % (100 * o["payer_conversion"], o["arpdau_usd"])]
    out += ["note: " + n for n in rep["notes"]]
    return "\n".join(out + (["WARNING: " + w for w in rep["warnings"]] or ["OK: no target warnings"]))

def load_model(path: str, days: Optional[int]) -> Model:
    p = Path(path)
    if not p.is_file():
        raise ModelError("model not found: %s" % path)
    try:
        doc = json.loads(p.read_text(encoding="utf-8"))
    except ValueError as e:
        raise ModelError("invalid JSON: %s" % e)
    return Model(doc, days)

def selftest() -> int:
    for bad in ("__import__('os')", "coins.real > 1", "coins >= 1 if 1 else 2", "nope > 1"):
        try:
            compile_cond(bad, ["coins", "level"], "t")
        except ModelError:
            continue
        raise AssertionError("accepted %r" % bad)
    doc = {
        "schema_version": "1.0", "days": 10,
        "archetypes": [{"id": "a", "share": 1.0, "sessions_per_day": 2, "session_minutes": 6, "skill": 0.5}],
        "resources": [{"id": "coins", "initial": 0, "cap": 100}, {"id": "gems", "initial": 0}, {"id": "stars"}],
        "nodes": [
            {"id": "inc", "kind": "source", "trigger": "per_session", "outputs": {"coins": 40}},
            {"id": "conv", "kind": "converter", "trigger": "per_session", "inputs": {"coins": 50},
             "outputs": {"gems": 1}, "condition": "coins >= 50"},
            {"id": "win", "kind": "source", "trigger": "per_level_win", "outputs": {"stars": 1}},
            {"id": "never", "kind": "gate", "trigger": "per_session", "inputs": {"gems": 999}, "outputs": {"stars": 1}}],
        "levels": {"count": 5, "base_win_rate": 0.7}}
    m = Model(doc, None)
    a, b = simulate(m, 30, 7), simulate(Model(doc, None), 30, 7)
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True), "not deterministic"
    arch = a["archetypes"]["a"]
    assert max(arch["balances"]["coins"]["p90"]) <= 100, "cap violated"
    assert arch["balances"]["gems"]["p50"][-1] > 0, "converter never fired"
    assert arch["flows"]["stars"]["sink_source_ratio"] == 0.0 and arch["gate_blocked_per_user"]["never"] > 10
    assert arch["level"]["p50"][-1] == 6 and arch["content"]["finished_pct"] == 100.0, arch["level"]
    doc["targets"] = {"days_to_complete_content": 30, "payer_conversion": 0.1}
    assert any("content runs out" in w for w in simulate(Model(doc, None), 30, 7)["warnings"])
    ex = Path(__file__).resolve().parent / "schemas" / "examples" / "example.economy-model.json"
    if ex.is_file():
        assert "casual_free" in text_report(simulate(load_model(str(ex), 14), 10, 1))
    print("selftest ok")
    return 0

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Monte Carlo agent-based economy simulation.")
    p.add_argument("--selftest", action="store_true", help="run built-in checks and exit")
    p.add_argument("--model", help="economy-model JSON document")
    p.add_argument("--runs", type=int, default=200, help="simulated players per archetype (default 200)")
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--days", type=int, default=None, help="override model days")
    p.add_argument("--json", action="store_true", help="print the JSON report")
    p.add_argument("--out", help="write the JSON report to this path")
    return p

def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    if args.selftest:
        return selftest()
    try:
        if not args.model or args.runs < 1 or (args.days is not None and args.days < 1):
            raise ModelError("--model is required; --runs and --days must be >= 1")
        rep = simulate(load_model(args.model, args.days), args.runs, args.seed)
    except (ModelError, KeyError, TypeError, ValueError) as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    if args.out:
        op = Path(args.out)
        op.parent.mkdir(parents=True, exist_ok=True)
        op.write_text(json.dumps(rep, indent=2), encoding="utf-8")
    print(json.dumps(rep, indent=2) if args.json else text_report(rep))
    return 0 if rep["ok"] else 1


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows pipes default to the ANSI code page; Claude Code reads UTF-8
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
