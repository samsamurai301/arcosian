#!/usr/bin/env python3
"""Exact gacha odds by dynamic programming over the pity state.

  gacha_calc.py --rate R [--soft-pity-start N] [--soft-pity-step S] [--hard-pity N]
                [--rate-up P] [--guarantee] [--pulls N] [--json]
  gacha_calc.py --selftest

Model (top-rarity "5-star" pulls; one pull = one roll):
  rate(n)  chance that the n-th pull since the last 5-star is a 5-star (n = 1, 2, ...):
           R before the soft pity start; R + S*(n - start + 1) from the soft pity start (capped at 1);
           exactly 1 at the hard pity pull. Without --soft-pity-start there is no ramp; without
           --hard-pity there is no hard cap. --soft-pity-step defaults to 0.06 when a start is given.
  --rate-up P  probability that a 5-star is the featured unit (default 1: any 5-star counts).
  --guarantee  after a 5-star that was NOT featured, the next 5-star is featured for sure (50/50 + guarantee).
The state is (pulls since last 5-star, guarantee flag); pity counters are merged once the rate stops
changing, so the DP is exact and cheap. Distributions are exact up to float precision; the expectation
sums the exact distribution until the remaining mass is below 1e-12.

Reports P(any 5-star) and P(featured) within N pulls (default 180), expected pulls, percentiles
(10/25/50/75/90/99), the consolidated 5-star rate (1 / expected pulls per 5-star, the single figure
many storefronts and regulators ask studios to disclose) and an odds-disclosure table.

Exit codes: 0 ok, 2 usage or input error.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import Dict, List, Optional, Sequence, Tuple

MAX_STEPS = 400000
TAIL = 1e-12
PCTS = (0.10, 0.25, 0.50, 0.75, 0.90, 0.99)


class InputError(Exception):
    pass


class Pity:
    def __init__(self, rate: float, soft_start: int = 0, soft_step: float = 0.0, hard: int = 0):
        if not (0.0 < rate <= 1.0):
            raise InputError("--rate must be in (0, 1]")
        if soft_start < 0 or hard < 0:
            raise InputError("pity values must be >= 0")
        if soft_start and soft_step <= 0:
            raise InputError("--soft-pity-step must be > 0 when a soft pity start is set")
        if hard and soft_start and soft_start > hard:
            raise InputError("soft pity start must be <= hard pity")
        self.rate, self.soft_start, self.soft_step, self.hard = rate, soft_start, soft_step, hard

    def at(self, n: int) -> float:
        """5-star probability on the n-th pull since the last 5-star (n >= 1)."""
        if self.hard and n >= self.hard:
            return 1.0
        if self.soft_start and n >= self.soft_start:
            return min(1.0, self.rate + self.soft_step * (n - self.soft_start + 1))
        return self.rate

    def counter_cap(self) -> int:
        """Largest pull index after which the rate no longer changes (counter can be merged beyond it)."""
        if self.hard:
            return self.hard
        if self.soft_start:
            ramp = int((1.0 - self.rate) / self.soft_step) + 2
            return self.soft_start + ramp
        return 1


def first_hit_pmf(p: Pity, rate_up: float, guarantee: bool, horizon: int) -> Tuple[List[float], float]:
    """pmf[t] = P(target first obtained on pull t) for t = 0..max(horizon, until tail<TAIL); returns (pmf, tail).

    With rate_up == 1 and no guarantee the target is 'any 5-star'.
    """
    cap = p.counter_cap()
    state = {(0, 0): 1.0}  # (pulls since last 5-star, guarantee flag) -> P(alive, target not yet obtained)
    pmf = [0.0]
    alive = 1.0
    t = 0
    while t < MAX_STEPS and (t < horizon or alive > TAIL):
        t += 1
        nxt = {}  # type: Dict[Tuple[int, int], float]
        got = 0.0
        for (k, g), pr in state.items():
            r = p.at(k + 1)
            f = 1.0 if (g and guarantee) else rate_up
            got += pr * r * f
            miss_target = pr * r * (1.0 - f)
            if miss_target:
                key = (0, 1 if guarantee else 0)
                nxt[key] = nxt.get(key, 0.0) + miss_target
            stay = pr * (1.0 - r)
            if stay:
                key = (min(k + 1, cap), g)
                nxt[key] = nxt.get(key, 0.0) + stay
        pmf.append(got)
        alive -= got
        state = nxt
        if not state:
            alive = 0.0
            break
    return pmf, max(alive, 0.0)


def summarize(pmf: List[float], tail: float, pulls: int) -> Dict:
    cdf = []  # type: List[float]
    acc = 0.0
    for x in pmf:
        acc += x
        cdf.append(acc)
    pct = {}  # type: Dict[str, Optional[int]]
    for q in PCTS:
        pct["p%d" % round(q * 100)] = next((t for t, c in enumerate(cdf) if c >= q), None)
    exp = sum(t * x for t, x in enumerate(pmf))
    return {"p_within": cdf[min(pulls, len(cdf) - 1)], "expected_pulls": exp, "tail_mass": tail,
            "percentiles": pct, "cdf": cdf}


def analyze(p: Pity, rate_up: float, guarantee: bool, pulls: int) -> Dict:
    any_pmf, any_tail = first_hit_pmf(p, 1.0, False, pulls)
    ft_pmf, ft_tail = first_hit_pmf(p, rate_up, guarantee, pulls)
    a = summarize(any_pmf, any_tail, pulls)
    f = summarize(ft_pmf, ft_tail, pulls)
    marks = sorted({n for n in (1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 120, 140, 160, 180, 200, 300, pulls,
                                p.hard, p.soft_start, 2 * p.hard if p.hard else 0) if n and n <= len(a["cdf"]) - 1})
    table = []
    for n in marks:
        table.append({"pull": n, "pull_rate": round(p.at(n), 6),
                      "cum_any": round(a["cdf"][n], 6), "cum_featured": round(f["cdf"][min(n, len(f["cdf"]) - 1)], 6)})
    return {
        "inputs": {"rate": p.rate, "soft_pity_start": p.soft_start, "soft_pity_step": p.soft_step,
                   "hard_pity": p.hard, "rate_up": rate_up, "guarantee": guarantee, "pulls": pulls},
        "any_5star": {"p_within_pulls": round(a["p_within"], 6), "expected_pulls": round(a["expected_pulls"], 4),
                      "percentiles": a["percentiles"]},
        "featured": {"p_within_pulls": round(f["p_within"], 6), "expected_pulls": round(f["expected_pulls"], 4),
                     "percentiles": f["percentiles"], "tail_mass": f["tail_mass"]},
        "consolidated_5star_rate": round(1.0 / a["expected_pulls"], 6),
        "disclosure_table": table,
    }


def cmd_run(a: argparse.Namespace) -> int:
    if not (0.0 < a.rate_up <= 1.0):
        raise InputError("--rate-up must be in (0, 1]")
    if a.pulls < 1:
        raise InputError("--pulls must be >= 1")
    if a.guarantee and a.rate_up >= 1.0:
        print("note: --guarantee has no effect when --rate-up is 1", file=sys.stderr)
    step = a.soft_pity_step if a.soft_pity_step is not None else (0.06 if a.soft_pity_start else 0.0)
    res = analyze(Pity(a.rate, a.soft_pity_start, step, a.hard_pity), a.rate_up, a.guarantee, a.pulls)
    if a.json:
        print(json.dumps(res, indent=2))
        return 0
    i, an, ft = res["inputs"], res["any_5star"], res["featured"]
    print("Gacha odds: base %.4f%%, soft pity %s (+%.3f/pull), hard pity %s, rate-up %.0f%%%s" % (
        i["rate"] * 100, i["soft_pity_start"] or "none", i["soft_pity_step"], i["hard_pity"] or "none",
        i["rate_up"] * 100, ", guarantee after a miss" if i["guarantee"] else ""))
    print("Any 5-star : P(within %d) = %.2f%%, expected %.2f pulls, pcts %s" % (
        i["pulls"], an["p_within_pulls"] * 100, an["expected_pulls"], an["percentiles"]))
    print("Featured   : P(within %d) = %.2f%%, expected %.2f pulls, pcts %s" % (
        i["pulls"], ft["p_within_pulls"] * 100, ft["expected_pulls"], ft["percentiles"]))
    print("Consolidated 5-star rate (1 / expected pulls): %.4f%%" % (res["consolidated_5star_rate"] * 100))
    print("\nOdds disclosure table")
    print(" pull  this-pull rate  P(any 5-star by)  P(featured by)")
    for r in res["disclosure_table"]:
        print("%5d  %13.4f%%  %15.2f%%  %13.2f%%" % (r["pull"], r["pull_rate"] * 100, r["cum_any"] * 100,
                                                    r["cum_featured"] * 100))
    if ft["tail_mass"] > 1e-9:
        print("note: %.2e of the featured distribution lies beyond the computed range" % ft["tail_mass"])
    return 0


def selftest() -> int:
    def close(x: float, y: float, tol: float = 1e-6) -> bool:
        return abs(x - y) <= tol

    r = analyze(Pity(1.0 / 6.0), 1.0, False, 6)  # plain geometric
    assert close(r["any_5star"]["expected_pulls"], 6.0, 1e-4), r["any_5star"]
    assert close(r["any_5star"]["p_within_pulls"], 1 - (5.0 / 6.0) ** 6), r["any_5star"]
    r = analyze(Pity(1.0), 0.5, False, 10)  # every pull is a 5-star, 50% featured: geometric(0.5)
    assert close(r["featured"]["expected_pulls"], 2.0), r["featured"]
    r = analyze(Pity(1.0), 0.5, True, 10)  # 50/50 with guarantee: 1.5 expected
    assert close(r["featured"]["expected_pulls"], 1.5), r["featured"]
    assert close(r["featured"]["p_within_pulls"], 1.0), r["featured"]
    r = analyze(Pity(0.006, 74, 0.06, 90), 0.5, True, 180)  # Genshin-like shape
    assert close(r["any_5star"]["p_within_pulls"], 1.0), r["any_5star"]
    assert close(r["featured"]["p_within_pulls"], 1.0), r["featured"]  # worst case 180 with guarantee
    assert 60 < r["any_5star"]["expected_pulls"] < 70, r["any_5star"]["expected_pulls"]
    assert r["featured"]["expected_pulls"] > r["any_5star"]["expected_pulls"] * 1.3
    p = Pity(0.006, 74, 0.06, 90)
    assert close(p.at(73), 0.006) and close(p.at(74), 0.066) and p.at(90) == 1.0
    # hard-pity-only: mass at pull 90 equals (1-rate)^89
    pmf, _ = first_hit_pmf(Pity(0.01, hard=90), 1.0, False, 90)
    assert close(pmf[90], 0.99 ** 89 * 1.0) and close(sum(pmf), 1.0)
    for bad in (lambda: Pity(0.0), lambda: Pity(0.5, 74, 0.0), lambda: Pity(0.5, 100, 0.1, 90)):
        try:
            bad()
            raise AssertionError("expected InputError")
        except InputError:
            pass
    print("selftest ok")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Exact gacha odds with soft/hard pity and 50/50 guarantee.")
    p.add_argument("--selftest", action="store_true", help="run built-in checks and exit")
    p.add_argument("--rate", type=float, help="base 5-star rate per pull, e.g. 0.006")
    p.add_argument("--soft-pity-start", type=int, default=0, help="pull where the rate starts ramping")
    p.add_argument("--soft-pity-step", type=float, default=None, help="rate added per pull from soft pity (default 0.06)")
    p.add_argument("--hard-pity", type=int, default=0, help="pull that is a guaranteed 5-star")
    p.add_argument("--rate-up", type=float, default=1.0, help="P(a 5-star is the featured unit), default 1")
    p.add_argument("--guarantee", action="store_true", help="featured guaranteed after losing the rate-up roll")
    p.add_argument("--pulls", type=int, default=180, help="pull budget for P(within N) (default 180)")
    p.add_argument("--json", action="store_true")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    if args.selftest:
        return selftest()
    if args.rate is None:
        print("error: --rate is required (or --selftest)", file=sys.stderr)
        return 2
    try:
        return cmd_run(args)
    except InputError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows pipes default to the ANSI code page; Claude Code reads UTF-8
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
