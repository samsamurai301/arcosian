#!/usr/bin/env python3
"""balance_math.py - pacing, difficulty and balance calculators for the
progression-difficulty skill. Complements (does not replace) the plugin-level
progression_calc.py (XP/cost curves) and difficulty_curve.py (level win-rate
curves and telemetry analysis).

Subcommands
  attempts    Win rate -> attempts distribution (mean, p50, p90, p99), clear
              probability within N tries, expected losses and failure cost.
  mix         Population heterogeneity: mixed per-segment win rates -> average
              first-attempt win rate vs real mean attempts (Jensen gap).
  funnel      Step counts or step rates -> step conversion, cumulative
              conversion, share of total loss, biggest leak.
  dda-sim     Monte Carlo of a bounded streak-based assist on one level versus
              no assist, using common random numbers (same dice for both).
  damage      Compare subtractive, divisive and hyperbolic armour formulas over
              a range of defence values; effective-HP multipliers.
  ttk         Hits and time to kill, expected DPS, crit-variance percentiles.
  costcurve   Robust (Theil-Sen) fit of power ~ cost across units; residuals
              flag over/under-costed units and give a fair cost for each.
  lanchester  Lanchester linear or square law outcome for two forces.
  softcap     Diminishing-returns curves (hyperbolic, exponential, piecewise):
              output and marginal value per point.

Exit codes: 0 ok, 1 check failed (--min-step / --fail-on-outlier), 2 usage or
input error. Stdlib only; Python 3.9+. Every subcommand supports --json.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
from typing import Dict, List, Optional, Sequence, Tuple


class InputError(ValueError):
    """Malformed user input (exit code 2)."""


# --------------------------------------------------------------------------- helpers

def logit(p: float) -> float:
    return math.log(p / (1.0 - p))


def sigmoid(x: float) -> float:
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


def check_ratio(name: str, p: float, open_interval: bool = True) -> None:
    if open_interval and not (0.0 < p < 1.0):
        raise InputError(f"{name} must be strictly between 0 and 1 (got {p})")
    if not open_interval and not (0.0 < p <= 1.0):
        raise InputError(f"{name} must be in (0, 1] (got {p})")


def geometric_quantile(p: float, q: float) -> int:
    """Smallest n with P(first success <= n) >= q, for per-attempt success p."""
    if p >= 1.0:
        return 1
    return max(1, math.ceil(math.log(1.0 - q) / math.log(1.0 - p) - 1e-12))


def percentile(sorted_vals: Sequence[float], q: float) -> float:
    if not sorted_vals:
        return float("nan")
    idx = min(len(sorted_vals) - 1, max(0, int(math.ceil(q * len(sorted_vals))) - 1))
    return float(sorted_vals[idx])


def parse_pairs(text: str, label: str) -> List[Tuple[str, float]]:
    out: List[Tuple[str, float]] = []
    for part in [p.strip() for p in text.split(",") if p.strip()]:
        if ":" not in part:
            raise InputError(f"{label}: expected name:value items, got '{part}'")
        name, val = part.rsplit(":", 1)
        try:
            out.append((name.strip(), float(val)))
        except ValueError:
            raise InputError(f"{label}: '{val}' is not a number")
    if not out:
        raise InputError(f"{label}: no items")
    return out


def parse_floats(text: str, label: str) -> List[float]:
    try:
        vals = [float(v) for v in text.split(",") if v.strip()]
    except ValueError:
        raise InputError(f"{label}: expected comma-separated numbers")
    if not vals:
        raise InputError(f"{label}: no values")
    return vals


def emit(result: Dict, as_json: bool, lines: List[str]) -> None:
    if as_json:
        print(json.dumps(result, indent=2, sort_keys=False))
    else:
        print("\n".join(lines))


# --------------------------------------------------------------------------- attempts

def calc_attempts(p: float, cost_per_loss: float = 0.0, cost_per_attempt: float = 0.0) -> Dict:
    check_ratio("win rate", p, open_interval=False)
    mean = 1.0 / p
    losses = mean - 1.0
    within = {str(n): round(1.0 - (1.0 - p) ** n, 4) for n in (1, 3, 5, 10, 20)}
    return {
        "win_rate": p,
        "mean_attempts": round(mean, 3),
        "p50_attempts": geometric_quantile(p, 0.5),
        "p90_attempts": geometric_quantile(p, 0.9),
        "p99_attempts": geometric_quantile(p, 0.99),
        "p_clear_within": within,
        "expected_losses": round(losses, 3),
        "expected_cost": round(losses * cost_per_loss + mean * cost_per_attempt, 3),
        "assumption": "constant per-attempt win rate (no learning, no assists); real players improve, "
                      "so treat as a pessimistic bound for an individual and see `mix` for populations",
    }


def cmd_attempts(a: argparse.Namespace) -> int:
    r = calc_attempts(a.win_rate, a.cost_per_loss, a.cost_per_attempt)
    lines = [
        f"win rate {r['win_rate']:.3f}: mean attempts {r['mean_attempts']}, p50 {r['p50_attempts']}, "
        f"p90 {r['p90_attempts']}, p99 {r['p99_attempts']}",
        "P(clear within N): " + ", ".join(f"{k}: {v:.3f}" for k, v in r["p_clear_within"].items()),
        f"expected losses {r['expected_losses']}, expected cost {r['expected_cost']}",
        "note: " + r["assumption"],
    ]
    emit(r, a.json, lines)
    return 0


# --------------------------------------------------------------------------- mix

def calc_mix(segments: List[Tuple[float, float]], stuck_after: int = 10) -> Dict:
    total_share = sum(s for _, s in segments)
    if total_share <= 0:
        raise InputError("shares must sum to a positive number")
    fawr = 0.0
    mean_attempts = 0.0
    stuck = 0.0
    for p, share in segments:
        check_ratio("segment win rate", p, open_interval=False)
        w = share / total_share
        fawr += w * p
        mean_attempts += w / p
        stuck += w * (1.0 - p) ** stuck_after
    naive = 1.0 / fawr
    return {
        "population_first_attempt_win_rate": round(fawr, 4),
        "naive_mean_attempts": round(naive, 3),
        "true_mean_attempts": round(mean_attempts, 3),
        "jensen_gap_ratio": round(mean_attempts / naive, 3),
        f"share_still_stuck_after_{stuck_after}": round(stuck, 4),
        "segments": [{"win_rate": p, "share": round(s / total_share, 4)} for p, s in segments],
    }


def cmd_mix(a: argparse.Namespace) -> int:
    pairs = parse_pairs(a.rates, "--rates")
    segments = [(float(name), share) for name, share in pairs]
    r = calc_mix(segments, a.stuck_after)
    key = f"share_still_stuck_after_{a.stuck_after}"
    lines = [
        f"population first-attempt win rate {r['population_first_attempt_win_rate']:.3f}",
        f"naive mean attempts (1/avg) {r['naive_mean_attempts']} vs true mean attempts {r['true_mean_attempts']} "
        f"(x{r['jensen_gap_ratio']})",
        f"share of players still stuck after {a.stuck_after} attempts: {r[key]:.3f}",
    ]
    emit(r, a.json, lines)
    return 0


# --------------------------------------------------------------------------- funnel

def calc_funnel(steps: List[Tuple[str, float]]) -> Dict:
    values = [v for _, v in steps]
    if any(v < 0 for v in values):
        raise InputError("funnel values must be non-negative")
    as_rates = all(v <= 1.0 for v in values)
    rows = []
    if as_rates:
        cum = 1.0
        for name, rate in steps:
            cum *= rate
            rows.append({"step": name, "step_conversion": round(rate, 4), "cumulative": round(cum, 4)})
        total_loss = 1.0 - cum
        prev = 1.0
        for row in rows:
            lost = prev - row["cumulative"]
            row["share_of_total_loss"] = round(lost / total_loss, 4) if total_loss > 0 else 0.0
            prev = row["cumulative"]
    else:
        if values[0] <= 0:
            raise InputError("first funnel count must be positive")
        top = values[0]
        prev_v = top
        for i, (name, v) in enumerate(steps):
            conv = 1.0 if i == 0 else (v / prev_v if prev_v > 0 else 0.0)
            rows.append({"step": name, "count": v, "step_conversion": round(conv, 4),
                         "cumulative": round(v / top, 4)})
            prev_v = v
        total_loss = top - values[-1]
        for i, row in enumerate(rows):
            lost = 0.0 if i == 0 else values[i - 1] - values[i]
            row["share_of_total_loss"] = round(lost / total_loss, 4) if total_loss > 0 else 0.0
    worst = max(rows, key=lambda r: r["share_of_total_loss"])
    return {"mode": "rates" if as_rates else "counts", "steps": rows,
            "end_to_end": rows[-1]["cumulative"], "biggest_leak": worst["step"]}


def cmd_funnel(a: argparse.Namespace) -> int:
    r = calc_funnel(parse_pairs(a.steps, "--steps"))
    failing = []
    if a.min_step is not None:
        failing = [row["step"] for row in r["steps"] if row["step_conversion"] < a.min_step]
        r["below_min_step"] = failing
    lines = [f"{'step':<24}{'conv':>8}{'cum':>8}{'loss%':>8}"]
    for row in r["steps"]:
        lines.append(f"{row['step']:<24}{row['step_conversion']:>8.3f}{row['cumulative']:>8.3f}"
                     f"{100 * row['share_of_total_loss']:>7.1f}%")
    lines.append(f"end-to-end {r['end_to_end']:.3f}; biggest leak: {r['biggest_leak']}")
    if a.min_step is not None:
        lines.append(f"steps below {a.min_step}: {', '.join(failing) if failing else 'none'}")
    emit(r, a.json, lines)
    return 1 if failing else 0


# --------------------------------------------------------------------------- dda-sim

def _run_policy(base_logit: float, skills: List[float], dice: List[List[float]], quit_dice: List[List[float]],
                trigger: int, step: float, max_assist: float, quit_after_loss: float, use_dda: bool) -> Dict:
    attempts_to_clear: List[int] = []
    longest_streaks: List[int] = []
    assisted_clears = 0
    quits = 0
    unresolved = 0
    for s, rolls, qrolls in zip(skills, dice, quit_dice):
        assist = 0.0
        streak = 0
        longest = 0
        cleared = False
        for i, u in enumerate(rolls):
            p = sigmoid(base_logit + s + (assist if use_dda else 0.0))
            if u < p:
                attempts_to_clear.append(i + 1)
                if use_dda and assist > 0:
                    assisted_clears += 1
                cleared = True
                break
            streak += 1
            longest = max(longest, streak)
            if quit_after_loss > 0 and qrolls[i] < quit_after_loss:
                quits += 1
                break
            if use_dda and streak % trigger == 0:
                assist = min(max_assist, assist + step)
        if not cleared:
            unresolved += 1
        longest_streaks.append(longest)
    n = len(skills)
    attempts_sorted = sorted(attempts_to_clear)
    streak_sorted = sorted(longest_streaks)
    clears = len(attempts_to_clear)
    return {
        "clear_rate": round(clears / n, 4),
        "quit_rate": round(quits / n, 4),
        "mean_attempts_among_clears": round(sum(attempts_to_clear) / clears, 3) if clears else None,
        "p50_attempts": percentile(attempts_sorted, 0.5) if clears else None,
        "p90_attempts": percentile(attempts_sorted, 0.9) if clears else None,
        "p95_longest_losing_streak": percentile(streak_sorted, 0.95),
        "share_of_clears_assisted": round(assisted_clears / clears, 4) if clears else 0.0,
        "unresolved_rate": round(unresolved / n, 4),
    }


def calc_dda(base: float, skill_sd: float, trigger: int, step: float, max_assist: float, players: int,
             max_attempts: int, quit_after_loss: float, seed: int) -> Dict:
    check_ratio("--base", base)
    if trigger < 1 or players < 1 or max_attempts < 1:
        raise InputError("--trigger, --players and --max-attempts must be >= 1")
    if step < 0 or max_assist < 0 or skill_sd < 0:
        raise InputError("--step, --max-assist and --skill-sd must be >= 0")
    if not (0.0 <= quit_after_loss < 1.0):
        raise InputError("--quit-after-loss must be in [0, 1)")
    rng = random.Random(seed)
    skills = [rng.gauss(0.0, skill_sd) for _ in range(players)]
    dice = [[rng.random() for _ in range(max_attempts)] for _ in range(players)]
    quit_dice = [[rng.random() for _ in range(max_attempts)] for _ in range(players)]
    b = logit(base)
    first_attempt = sum(1 for s, r in zip(skills, dice) if r[0] < sigmoid(b + s)) / players
    none = _run_policy(b, skills, dice, quit_dice, trigger, step, max_assist, quit_after_loss, False)
    dda = _run_policy(b, skills, dice, quit_dice, trigger, step, max_assist, quit_after_loss, True)
    return {
        "model": "p = sigmoid(logit(base) + skill + assist); skill ~ Normal(0, skill_sd) in logit units; "
                 f"assist += step after every {trigger} consecutive losses, capped at max_assist",
        "params": {"base": base, "skill_sd": skill_sd, "trigger": trigger, "step": step,
                   "max_assist": max_assist, "players": players, "max_attempts": max_attempts,
                   "quit_after_loss": quit_after_loss, "seed": seed},
        "first_attempt_win_rate": round(first_attempt, 4),
        "max_assist_as_win_rate_at_median_skill": round(sigmoid(b + max_assist), 4),
        "no_dda": none,
        "dda": dda,
    }


def cmd_dda(a: argparse.Namespace) -> int:
    r = calc_dda(a.base, a.skill_sd, a.trigger, a.step, a.max_assist, a.players, a.max_attempts,
                 a.quit_after_loss, a.seed)
    lines = [r["model"],
             f"first-attempt win rate (unchanged by DDA): {r['first_attempt_win_rate']:.3f}; "
             f"max assist lifts a median player to {r['max_assist_as_win_rate_at_median_skill']:.3f}",
             f"{'metric':<30}{'no DDA':>10}{'DDA':>10}"]
    for k in ("clear_rate", "quit_rate", "mean_attempts_among_clears", "p50_attempts", "p90_attempts",
              "p95_longest_losing_streak", "share_of_clears_assisted"):
        lines.append(f"{k:<30}{str(r['no_dda'][k]):>10}{str(r['dda'][k]):>10}")
    emit(r, a.json, lines)
    return 0


# --------------------------------------------------------------------------- damage

def calc_damage(atk: float, defs: List[float], k: float, min_frac: float) -> Dict:
    if atk <= 0 or k <= 0:
        raise InputError("--atk and --k must be positive")
    if not (0.0 <= min_frac <= 1.0):
        raise InputError("--min-frac must be in [0, 1]")
    rows = []
    for d in defs:
        if d < 0:
            raise InputError("defence values must be >= 0 (negative armour needs a separate rule)")
        sub = max(atk - d, atk * min_frac)
        div = atk * atk / (atk + d)
        hyp = atk * k / (k + d)
        rows.append({"def": d, "subtractive": round(sub, 2), "divisive_atk_over_atk_plus_def": round(div, 2),
                     "hyperbolic_k": round(hyp, 2), "hyperbolic_ehp_multiplier": round((k + d) / k, 3)})
    return {"atk": atk, "k": k, "min_frac": min_frac, "rows": rows,
            "formulas": {"subtractive": "max(atk - def, min_frac * atk)",
                         "divisive": "atk * atk / (atk + def)",
                         "hyperbolic": "atk * k / (k + def); EHP = HP * (k + def) / k"}}


def cmd_damage(a: argparse.Namespace) -> int:
    r = calc_damage(a.atk, parse_floats(a.def_values, "--def-values"), a.k, a.min_frac)
    lines = [f"atk {a.atk}, k {a.k}, subtractive floor {a.min_frac:.0%} of atk",
             f"{'def':>8}{'subtr':>10}{'divis':>10}{'hyperb':>10}{'EHPx':>8}"]
    for row in r["rows"]:
        lines.append(f"{row['def']:>8g}{row['subtractive']:>10g}{row['divisive_atk_over_atk_plus_def']:>10g}"
                     f"{row['hyperbolic_k']:>10g}{row['hyperbolic_ehp_multiplier']:>8g}")
    emit(r, a.json, lines)
    return 0


# --------------------------------------------------------------------------- ttk

def calc_ttk(hp: float, damage: float, rate: float, crit_chance: float, crit_mult: float, mitigation: float,
             runs: int, seed: int) -> Dict:
    if hp <= 0 or damage <= 0 or rate <= 0:
        raise InputError("--hp, --damage and --rate must be positive")
    if not (0.0 <= crit_chance <= 1.0) or crit_mult < 1.0 or not (0.0 < mitigation <= 1.0):
        raise InputError("crit chance in [0,1], crit mult >= 1, damage multiplier in (0,1]")
    per_hit = damage * mitigation
    expected = per_hit * (1.0 + crit_chance * (crit_mult - 1.0))
    hits_expected = math.ceil(hp / expected - 1e-12)
    rng = random.Random(seed)
    samples: List[int] = []
    for _ in range(runs):
        left = hp
        hits = 0
        while left > 1e-9:
            hits += 1
            left -= per_hit * (crit_mult if rng.random() < crit_chance else 1.0)
        samples.append(hits)
    samples.sort()
    return {
        "damage_per_hit_after_mitigation": round(per_hit, 3),
        "expected_damage_per_hit": round(expected, 3),
        "expected_dps": round(expected * rate, 3),
        "hits_to_kill_from_expected": hits_expected,
        "ttk_sec_from_expected": round(hits_expected / rate, 3),
        "hits_p10_p50_p90": [percentile(samples, 0.1), percentile(samples, 0.5), percentile(samples, 0.9)],
        "ttk_sec_p10_p50_p90": [round(percentile(samples, q) / rate, 3) for q in (0.1, 0.5, 0.9)],
        "convention": "first hit lands at t = 1/rate; TTK = hits / rate",
    }


def cmd_ttk(a: argparse.Namespace) -> int:
    r = calc_ttk(a.hp, a.damage, a.rate, a.crit_chance, a.crit_mult, a.mitigation, a.runs, a.seed)
    lines = [f"per hit {r['damage_per_hit_after_mitigation']} (expected {r['expected_damage_per_hit']} with crits), "
             f"DPS {r['expected_dps']}",
             f"hits to kill (expected) {r['hits_to_kill_from_expected']}, TTK {r['ttk_sec_from_expected']} s",
             f"hits p10/p50/p90 {r['hits_p10_p50_p90']}, TTK s {r['ttk_sec_p10_p50_p90']}",
             r["convention"]]
    emit(r, a.json, lines)
    return 0


# --------------------------------------------------------------------------- costcurve

def _fit(xs: List[float], ys: List[float], through_origin: bool) -> Tuple[float, float]:
    n = len(xs)
    if through_origin:
        sxx = sum(x * x for x in xs)
        if sxx == 0:
            raise InputError("all costs are zero")
        return 0.0, sum(x * y for x, y in zip(xs, ys)) / sxx
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        raise InputError("costs must not all be equal for an intercept fit; use --through-origin")
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    return my - b * mx, b


def _median(vals: List[float]) -> float:
    v = sorted(vals)
    n = len(v)
    mid = n // 2
    return v[mid] if n % 2 else 0.5 * (v[mid - 1] + v[mid])


def _robust_fit(xs: List[float], ys: List[float], through_origin: bool) -> Tuple[float, float]:
    """Theil-Sen: median pairwise slope (or median y/x through the origin). One bad unit cannot drag the line."""
    if through_origin:
        ratios = [y / x for x, y in zip(xs, ys) if x != 0]
        if not ratios:
            raise InputError("all costs are zero")
        return 0.0, _median(ratios)
    slopes = [(ys[j] - ys[i]) / (xs[j] - xs[i])
              for i in range(len(xs)) for j in range(i + 1, len(xs)) if xs[j] != xs[i]]
    if not slopes:
        raise InputError("costs must not all be equal for an intercept fit; use --through-origin")
    b = _median(slopes)
    a = _median([y - b * x for x, y in zip(xs, ys)])
    return a, b


def calc_costcurve(units: List[Tuple[str, float, float]], tolerance: float, through_origin: bool) -> Dict:
    if len(units) < 3:
        raise InputError("need at least 3 units")
    xs = [c for _, c, _ in units]
    ys = [p for _, _, p in units]
    a_ols, b_ols = _fit(xs, ys, through_origin)
    a, b = _robust_fit(xs, ys, through_origin)
    rows = []
    for name, cost, power in units:
        pred = a + b * cost
        resid = (power - pred) / pred if pred > 0 else float("inf")
        verdict = "ok"
        if resid > tolerance:
            verdict = "over-powered for cost (or under-costed)"
        elif resid < -tolerance:
            verdict = "under-powered for cost (or over-costed)"
        fair_cost = (power - a) / b if b > 0 else None
        rows.append({"unit": name, "cost": cost, "power": power, "predicted_power": round(pred, 3),
                     "residual": round(resid, 4) if math.isfinite(resid) else None,
                     "fair_cost": round(fair_cost, 3) if fair_cost is not None else None,
                     "verdict": verdict})
    return {"robust_fit": {"intercept": round(a, 4), "slope": round(b, 4), "method": "Theil-Sen"},
            "ols_fit": {"intercept": round(a_ols, 4), "slope": round(b_ols, 4)},
            "through_origin": through_origin, "tolerance": tolerance, "rows": rows,
            "outliers": [r["unit"] for r in rows if r["verdict"] != "ok"]}


def cmd_costcurve(a: argparse.Namespace) -> int:
    units: List[Tuple[str, float, float]] = []
    for part in [p.strip() for p in a.units.split(",") if p.strip()]:
        bits = part.split(":")
        if len(bits) != 3:
            raise InputError(f"--units item '{part}' must be name:cost:power")
        try:
            units.append((bits[0], float(bits[1]), float(bits[2])))
        except ValueError:
            raise InputError(f"--units item '{part}' has a non-numeric cost or power")
    r = calc_costcurve(units, a.tolerance, a.through_origin)
    lines = [f"robust fit: power = {r['robust_fit']['intercept']} + {r['robust_fit']['slope']} * cost "
             f"(OLS for reference: {r['ols_fit']['intercept']} + {r['ols_fit']['slope']} * cost); "
             f"tolerance +/-{a.tolerance:.0%}",
             f"{'unit':<14}{'cost':>7}{'power':>9}{'pred':>9}{'resid':>8}{'fair cost':>11}  verdict"]
    for row in r["rows"]:
        fc = "-" if row["fair_cost"] is None else f"{row['fair_cost']:g}"
        rs = "   n/a" if row["residual"] is None else f"{100 * row['residual']:>7.1f}%"
        lines.append(f"{row['unit']:<14}{row['cost']:>7g}{row['power']:>9g}{row['predicted_power']:>9g}"
                     f"{rs:>8}{fc:>11}  {row['verdict']}")
    emit(r, a.json, lines)
    return 1 if (a.fail_on_outlier and r["outliers"]) else 0


# --------------------------------------------------------------------------- lanchester

def calc_lanchester(a_n: float, b_n: float, a_eff: float, b_eff: float, law: str) -> Dict:
    if a_n < 0 or b_n < 0 or a_eff <= 0 or b_eff <= 0:
        raise InputError("counts must be >= 0 and effectiveness > 0")
    if law == "square":
        sa, sb = a_eff * a_n ** 2, b_eff * b_n ** 2
        if sa > sb:
            winner, surv = "A", math.sqrt(a_n ** 2 - (b_eff / a_eff) * b_n ** 2)
        elif sb > sa:
            winner, surv = "B", math.sqrt(b_n ** 2 - (a_eff / b_eff) * a_n ** 2)
        else:
            winner, surv = "draw", 0.0
    else:
        sa, sb = a_eff * a_n, b_eff * b_n
        if sa > sb:
            winner, surv = "A", a_n - (b_eff / a_eff) * b_n
        elif sb > sa:
            winner, surv = "B", b_n - (a_eff / b_eff) * a_n
        else:
            winner, surv = "draw", 0.0
    return {"law": law, "strength_a": round(sa, 4), "strength_b": round(sb, 4), "winner": winner,
            "survivors": round(surv, 3),
            "note": "effectiveness = per-unit kill rate (e.g. own DPS / enemy HP); square law = everyone can "
                    "target anyone (ranged, aimed fire); linear law = fixed frontage or one-on-one duels"}


def cmd_lanchester(a: argparse.Namespace) -> int:
    a_eff, b_eff = a.a_eff, a.b_eff
    if a.a_dps is not None and a.b_hp is not None and a.b_dps is not None and a.a_hp is not None:
        a_eff = a.a_dps / a.b_hp
        b_eff = a.b_dps / a.a_hp
    if a_eff is None or b_eff is None:
        raise InputError("give --a-eff/--b-eff, or all of --a-dps --a-hp --b-dps --b-hp")
    r = calc_lanchester(a.a, a.b, a_eff, b_eff, a.law)
    lines = [f"{r['law']} law: strength A {r['strength_a']} vs B {r['strength_b']} -> winner {r['winner']}, "
             f"survivors {r['survivors']}", r["note"]]
    emit(r, a.json, lines)
    return 0


# --------------------------------------------------------------------------- softcap

def calc_softcap(formula: str, k: float, values: List[float], cap: float, rate: float) -> Dict:
    if k <= 0:
        raise InputError("--k must be positive")
    rows = []

    def f(x: float) -> float:
        if formula == "hyperbolic":
            return cap * x / (x + k)
        if formula == "exponential":
            return cap * (1.0 - math.exp(-x / k))
        # piecewise: full value up to k, then `rate` per point, clipped at cap
        raw = x if x <= k else k + (x - k) * rate
        return min(raw, cap)

    for x in values:
        if x < 0:
            raise InputError("stat values must be >= 0")
        y = f(x)
        marginal = f(x + 1.0) - y
        rows.append({"value": x, "output": round(y, 4), "marginal_per_point": round(marginal, 5)})
    return {"formula": formula, "k": k, "cap": cap, "rate": rate, "rows": rows,
            "definitions": {"hyperbolic": "cap * x / (x + k)  (half of cap at x = k)",
                            "exponential": "cap * (1 - exp(-x / k))  (63% of cap at x = k)",
                            "piecewise": "x up to k, then k + (x - k) * rate, clipped at cap"}}


def cmd_softcap(a: argparse.Namespace) -> int:
    r = calc_softcap(a.formula, a.k, parse_floats(a.values, "--values"), a.cap, a.rate)
    lines = [f"{a.formula}: {r['definitions'][a.formula]}", f"{'value':>10}{'output':>12}{'marginal':>12}"]
    for row in r["rows"]:
        lines.append(f"{row['value']:>10g}{row['output']:>12g}{row['marginal_per_point']:>12g}")
    emit(r, a.json, lines)
    return 0


# --------------------------------------------------------------------------- selftest

def selftest() -> int:
    def close(x: float, y: float, tol: float = 1e-3) -> bool:
        return abs(x - y) <= tol

    checks: List[Tuple[str, bool]] = []
    r = calc_attempts(0.5)
    checks.append(("attempts mean p=0.5", close(r["mean_attempts"], 2.0)))
    checks.append(("attempts p50 p=0.5", r["p50_attempts"] == 1))
    checks.append(("attempts p90 p=0.5", r["p90_attempts"] == 4))
    checks.append(("attempts p90 p=0.2", calc_attempts(0.2)["p90_attempts"] == 11))
    checks.append(("attempts within 5 p=0.3", close(calc_attempts(0.3)["p_clear_within"]["5"], 0.8319)))
    m = calc_mix([(0.8, 0.5), (0.2, 0.5)])
    checks.append(("mix fawr", close(m["population_first_attempt_win_rate"], 0.5)))
    checks.append(("mix true attempts", close(m["true_mean_attempts"], 3.125)))
    fr = calc_funnel([("a", 1000), ("b", 900), ("c", 450)])
    checks.append(("funnel cumulative", close(fr["end_to_end"], 0.45)))
    checks.append(("funnel leak", fr["biggest_leak"] == "c"))
    fr2 = calc_funnel([("s1", 0.9), ("s2", 0.5)])
    checks.append(("funnel rates", close(fr2["end_to_end"], 0.45)))
    d = calc_dda(0.4, 1.0, 2, 0.3, 0.9, 400, 25, 0.0, 7)
    checks.append(("dda first attempt equal", 0.25 < d["first_attempt_win_rate"] < 0.55))
    checks.append(("dda reduces mean attempts",
                   d["dda"]["mean_attempts_among_clears"] <= d["no_dda"]["mean_attempts_among_clears"]))
    checks.append(("dda reduces long streaks",
                   d["dda"]["p95_longest_losing_streak"] <= d["no_dda"]["p95_longest_losing_streak"]))
    dq = calc_dda(0.4, 1.0, 2, 0.3, 0.9, 400, 25, 0.15, 7)
    checks.append(("dda quit model lowers quits", dq["dda"]["quit_rate"] <= dq["no_dda"]["quit_rate"]))
    dm = calc_damage(100, [0, 100], 100, 0.1)
    checks.append(("damage hyperbolic", close(dm["rows"][1]["hyperbolic_k"], 50.0)))
    checks.append(("damage subtractive floor", close(dm["rows"][1]["subtractive"], 10.0)))
    checks.append(("damage ehp", close(dm["rows"][1]["hyperbolic_ehp_multiplier"], 2.0)))
    t = calc_ttk(1000, 100, 2.0, 0.0, 2.0, 1.0, 200, 1)
    checks.append(("ttk hits", t["hits_to_kill_from_expected"] == 10))
    checks.append(("ttk sec", close(t["ttk_sec_from_expected"], 5.0)))
    checks.append(("ttk mc no crit", t["hits_p10_p50_p90"] == [10.0, 10.0, 10.0]))
    cc = calc_costcurve([("a", 1, 10), ("b", 2, 20), ("c", 3, 30), ("d", 4, 40), ("e", 5, 75)], 0.15, False)
    checks.append(("costcurve outlier", cc["outliers"] == ["e"]))
    cc2 = calc_costcurve([("a", 1, 10), ("b", 2, 20), ("c", 3, 30), ("d", 4, 40)], 0.15, True)
    checks.append(("costcurve clean", cc2["outliers"] == []))
    l1 = calc_lanchester(20, 10, 1, 3, "square")
    checks.append(("lanchester square", l1["winner"] == "A" and close(l1["survivors"], 10.0)))
    l2 = calc_lanchester(20, 10, 1, 3, "linear")
    checks.append(("lanchester linear", l2["winner"] == "B" and close(l2["survivors"], 3.333)))
    s = calc_softcap("hyperbolic", 100, [100], 100, 0.5)
    checks.append(("softcap hyperbolic", close(s["rows"][0]["output"], 50.0)))
    s2 = calc_softcap("piecewise", 50, [80], 1e9, 0.5)
    checks.append(("softcap piecewise", close(s2["rows"][0]["output"], 65.0)))
    try:
        calc_attempts(0.0)
        checks.append(("input error raised", False))
    except InputError:
        checks.append(("input error raised", True))

    failed = [name for name, ok in checks if not ok]
    for name, ok in checks:
        print(f"[{'ok' if ok else 'FAIL'}] {name}")
    print(f"selftest: {len(checks) - len(failed)}/{len(checks)} passed")
    return 0 if not failed else 1


# --------------------------------------------------------------------------- cli

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Pacing, difficulty and balance calculators "
                                            "(progression-difficulty skill).")
    p.add_argument("--selftest", action="store_true", help="run built-in checks and exit")
    sub = p.add_subparsers(dest="cmd")

    s = sub.add_parser("attempts", help="win rate -> attempts distribution and failure cost")
    s.add_argument("--win-rate", type=float, required=True)
    s.add_argument("--cost-per-loss", type=float, default=0.0, help="e.g. lives or energy lost per failed attempt")
    s.add_argument("--cost-per-attempt", type=float, default=0.0, help="e.g. energy spent on every attempt")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_attempts)

    s = sub.add_parser("mix", help="segment win rates -> population average vs true mean attempts")
    s.add_argument("--rates", required=True, help='"winrate:share,..." e.g. "0.8:0.5,0.2:0.5"')
    s.add_argument("--stuck-after", type=int, default=10)
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_mix)

    s = sub.add_parser("funnel", help="onboarding or level funnel analysis")
    s.add_argument("--steps", required=True, help='"name:count,..." or "name:rate,..." (all values <= 1 = rates)')
    s.add_argument("--min-step", type=float, default=None, help="exit 1 if any step conversion is below this")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_funnel)

    s = sub.add_parser("dda-sim", help="bounded streak-based assist vs none (Monte Carlo)")
    s.add_argument("--base", type=float, required=True, help="first-attempt win rate of a median-skill player")
    s.add_argument("--skill-sd", type=float, default=1.0, help="player skill spread in logit units")
    s.add_argument("--trigger", type=int, default=2, help="consecutive losses per assist step")
    s.add_argument("--step", type=float, default=0.25, help="assist per step in logit units")
    s.add_argument("--max-assist", type=float, default=0.75, help="assist cap in logit units")
    s.add_argument("--players", type=int, default=2000)
    s.add_argument("--max-attempts", type=int, default=30)
    s.add_argument("--quit-after-loss", type=float, default=0.0,
                   help="optional constant probability a player quits after any loss (churn proxy)")
    s.add_argument("--seed", type=int, default=1)
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_dda)

    s = sub.add_parser("damage", help="armour formula comparison")
    s.add_argument("--atk", type=float, required=True)
    s.add_argument("--def-values", default="0,25,50,100,200,400")
    s.add_argument("--k", type=float, default=100.0, help="hyperbolic constant (defence giving 50%% reduction)")
    s.add_argument("--min-frac", type=float, default=0.1, help="subtractive floor as a fraction of atk")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_damage)

    s = sub.add_parser("ttk", help="hits and time to kill")
    s.add_argument("--hp", type=float, required=True)
    s.add_argument("--damage", type=float, required=True, help="damage per hit before mitigation")
    s.add_argument("--rate", type=float, required=True, help="hits per second")
    s.add_argument("--crit-chance", type=float, default=0.0)
    s.add_argument("--crit-mult", type=float, default=2.0)
    s.add_argument("--mitigation", type=float, default=1.0, help="damage multiplier after armour, (0,1]")
    s.add_argument("--runs", type=int, default=2000)
    s.add_argument("--seed", type=int, default=1)
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_ttk)

    s = sub.add_parser("costcurve", help="fit power vs cost and flag outliers")
    s.add_argument("--units", required=True, help='"name:cost:power,..."')
    s.add_argument("--tolerance", type=float, default=0.15, help="relative residual that flags a unit")
    s.add_argument("--through-origin", action="store_true", help="fit power = slope * cost")
    s.add_argument("--fail-on-outlier", action="store_true", help="exit 1 if any unit is flagged")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_costcurve)

    s = sub.add_parser("lanchester", help="Lanchester linear/square law battle outcome")
    s.add_argument("--a", type=float, required=True, help="force A unit count")
    s.add_argument("--b", type=float, required=True, help="force B unit count")
    s.add_argument("--a-eff", type=float, default=None)
    s.add_argument("--b-eff", type=float, default=None)
    s.add_argument("--a-dps", type=float, default=None)
    s.add_argument("--a-hp", type=float, default=None)
    s.add_argument("--b-dps", type=float, default=None)
    s.add_argument("--b-hp", type=float, default=None)
    s.add_argument("--law", choices=["square", "linear"], default="square")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_lanchester)

    s = sub.add_parser("softcap", help="diminishing returns curves")
    s.add_argument("--formula", choices=["hyperbolic", "exponential", "piecewise"], required=True)
    s.add_argument("--k", type=float, required=True)
    s.add_argument("--values", default="0,10,25,50,100,200,400")
    s.add_argument("--cap", type=float, default=100.0)
    s.add_argument("--rate", type=float, default=0.5, help="piecewise: value per point beyond k")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_softcap)
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as e:
        return 0 if e.code == 0 else 2
    if args.selftest:
        return selftest()
    if not getattr(args, "func", None):
        parser.print_help()
        return 2
    try:
        return int(args.func(args))
    except InputError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows pipes default to the ANSI code page; Claude Code reads UTF-8
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
