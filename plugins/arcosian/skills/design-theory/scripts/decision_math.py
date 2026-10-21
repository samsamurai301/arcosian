#!/usr/bin/env python3
"""decision_math.py - design-side decision maths for the design-theory skill.

Subcommands
  matrix  Dominance, iterated elimination, pure Nash equilibria, and mixed
          strategies for small payoff matrices (zero-sum or general 2-player).
  prd     Pseudo-random distribution constant C for a nominal proc chance.
  elo     Elo win probability <-> rating difference, best-of-N series odds.
  ev      Expected value / variance / SD of a risky option.

Payoff syntax for `matrix`: rows separated by ';', cells by ','.
  "0,-3,1;3,0,-2;-1,2,0"     zero-sum (row player's payoff; column gets negative)
  "3/3,0/5;5/0,1/1"          general game (row payoff / column payoff)

Exit codes: 0 ok, 1 check failed (--fail-on-dominated), 2 usage/input error.
Stdlib only; Python 3.9+.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from typing import Dict, List, Optional, Sequence, Tuple

Matrix = List[List[float]]
EPS = 1e-9


class InputError(ValueError):
    """Raised for malformed user input (maps to exit code 2)."""


# --------------------------------------------------------------------------- parsing

def parse_payoff(text: str) -> Tuple[Matrix, Matrix, bool]:
    """Parse payoff text into (A, B, zero_sum). A = row payoffs, B = column payoffs."""
    rows = [r.strip() for r in text.split(";") if r.strip()]
    if not rows:
        raise InputError("empty payoff matrix")
    cells = [[c.strip() for c in r.split(",")] for r in rows]
    width = len(cells[0])
    if width == 0 or any(len(r) != width for r in cells):
        raise InputError("payoff matrix must be rectangular (same number of cells per row)")
    has_pairs = any("/" in c for r in cells for c in r)
    A: Matrix = []
    B: Matrix = []
    try:
        for r in cells:
            arow: List[float] = []
            brow: List[float] = []
            for c in r:
                if has_pairs:
                    if "/" not in c:
                        raise InputError("mixed cell formats: use 'a/b' in every cell for general games")
                    a_txt, b_txt = c.split("/", 1)
                    arow.append(float(a_txt))
                    brow.append(float(b_txt))
                else:
                    v = float(c)
                    arow.append(v)
                    brow.append(-v)
            A.append(arow)
            B.append(brow)
    except ValueError as exc:
        if isinstance(exc, InputError):
            raise
        raise InputError("non-numeric payoff cell: %s" % exc) from exc
    return A, B, not has_pairs


def parse_labels(text: Optional[str], n: int, prefix: str) -> List[str]:
    if not text:
        return ["%s%d" % (prefix, i + 1) for i in range(n)]
    labels = [x.strip() for x in text.split(",")]
    if len(labels) != n:
        raise InputError("expected %d labels, got %d" % (n, len(labels)))
    return labels


def parse_weights(text: Optional[str], n: int) -> Optional[List[float]]:
    if not text:
        return None
    try:
        w = [float(x) for x in text.split(",")]
    except ValueError as exc:
        raise InputError("non-numeric column weight") from exc
    if len(w) != n:
        raise InputError("expected %d column weights, got %d" % (n, len(w)))
    if any(x < 0 for x in w) or sum(w) <= 0:
        raise InputError("column weights must be non-negative and sum to > 0")
    s = sum(w)
    return [x / s for x in w]


# --------------------------------------------------------------------------- matrix analysis

def transpose(M: Matrix) -> Matrix:
    return [list(col) for col in zip(*M)]


def dominance_pairs(vectors: Matrix, idx: Sequence[int]) -> List[Tuple[int, int, str]]:
    """Return (dominator, dominated, kind) among the given strategy indices.

    vectors[i] is the payoff vector of strategy i (higher is better)."""
    out: List[Tuple[int, int, str]] = []
    for i in idx:
        for k in idx:
            if i == k:
                continue
            vi, vk = vectors[i], vectors[k]
            ge = all(a >= b - EPS for a, b in zip(vi, vk))
            gt_all = all(a > b + EPS for a, b in zip(vi, vk))
            gt_any = any(a > b + EPS for a, b in zip(vi, vk))
            if gt_all:
                out.append((i, k, "strict"))
            elif ge and gt_any:
                out.append((i, k, "weak"))
    return out


def iesds(A: Matrix, B: Matrix, columns_are_players: bool = True) -> Dict[str, object]:
    """Iterated elimination of strictly dominated strategies."""
    rows = list(range(len(A)))
    cols = list(range(len(A[0])))
    order: List[Tuple[str, int, int]] = []
    changed = True
    while changed:
        changed = False
        row_vecs = [[A[i][j] for j in cols] for i in range(len(A))]
        for dom, sub, kind in dominance_pairs(row_vecs, rows):
            if kind == "strict" and sub in rows:
                rows.remove(sub)
                order.append(("row", sub, dom))
                changed = True
                break
        if changed or not columns_are_players:
            continue
        col_vecs = [[B[i][j] for i in rows] for j in range(len(A[0]))]
        for dom, sub, kind in dominance_pairs(col_vecs, cols):
            if kind == "strict" and sub in cols:
                cols.remove(sub)
                order.append(("col", sub, dom))
                changed = True
                break
    return {"rows": rows, "cols": cols, "order": order}


def pure_nash(A: Matrix, B: Matrix) -> List[Tuple[int, int]]:
    m, n = len(A), len(A[0])
    eq: List[Tuple[int, int]] = []
    for i in range(m):
        for j in range(n):
            best_row = max(A[k][j] for k in range(m))
            best_col = max(B[i][k] for k in range(n))
            if A[i][j] >= best_row - EPS and B[i][j] >= best_col - EPS:
                eq.append((i, j))
    return eq


def fictitious_play(A: Matrix, iters: int = 100000) -> Dict[str, object]:
    """Approximate mixed equilibrium of a zero-sum game (row maximises A)."""
    m, n = len(A), len(A[0])
    row_counts = [0] * m
    col_counts = [0] * n
    row_cum = [0.0] * m  # payoff of each row vs column's empirical play
    col_cum = [0.0] * n  # payoff (to row) of each column vs row's empirical play
    r = 0
    c = 0
    for _ in range(max(1, iters)):
        row_counts[r] += 1
        col_counts[c] += 1
        for i in range(m):
            row_cum[i] += A[i][c]
        for j in range(n):
            col_cum[j] += A[r][j]
        r = max(range(m), key=lambda i: row_cum[i])
        c = min(range(n), key=lambda j: col_cum[j])
    t = float(sum(row_counts))
    upper = max(row_cum) / t
    lower = min(col_cum) / t
    return {
        "row_mix": [x / t for x in row_counts],
        "col_mix": [x / t for x in col_counts],
        "value_bounds": [lower, upper],
        "iters": int(t),
    }


def mixed_2x2(A: Matrix, B: Matrix) -> Optional[Dict[str, float]]:
    """Fully mixed equilibrium of a 2x2 general game, if one exists."""
    if len(A) != 2 or len(A[0]) != 2:
        return None
    dq = A[0][0] - A[0][1] - A[1][0] + A[1][1]
    dp = B[0][0] - B[1][0] - B[0][1] + B[1][1]
    if abs(dq) < EPS or abs(dp) < EPS:
        return None
    q = (A[1][1] - A[0][1]) / dq  # P(column plays col 0)
    p = (B[1][1] - B[1][0]) / dp  # P(row plays row 0)
    if not (EPS < p < 1 - EPS and EPS < q < 1 - EPS):
        return None
    return {"p_row0": p, "q_col0": q}


def analyse_matrix(A: Matrix, B: Matrix, zero_sum: bool, situations: bool,
                   weights: Optional[List[float]], iters: int) -> Dict[str, object]:
    m, n = len(A), len(A[0])
    result: Dict[str, object] = {"rows": m, "cols": n, "zero_sum": zero_sum, "situations": situations}
    result["row_dominance"] = dominance_pairs(A, list(range(m)))
    if not situations:
        result["col_dominance"] = dominance_pairs(transpose(B), list(range(n)))
    result["iesds"] = iesds(A, B, columns_are_players=not situations)
    if weights is not None:
        exp = [sum(A[i][j] * weights[j] for j in range(n)) for i in range(m)]
        result["expected_row_payoff"] = exp
        result["best_row_for_weights"] = max(range(m), key=lambda i: exp[i])
    if not situations:
        result["pure_nash"] = pure_nash(A, B)
        if zero_sum:
            result["mixed"] = fictitious_play(A, iters)
        else:
            result["mixed_2x2"] = mixed_2x2(A, B)
    return result


def has_strict_domination(res: Dict[str, object]) -> bool:
    pairs = list(res.get("row_dominance", [])) + list(res.get("col_dominance", []))
    return any(kind == "strict" for _, _, kind in pairs)


def format_matrix_report(res: Dict[str, object], rl: List[str], cl: List[str]) -> str:
    lines: List[str] = []
    kind = "zero-sum" if res["zero_sum"] else "general 2-player"
    if res["situations"]:
        kind = "options vs situations"
    lines.append("Payoff matrix: %dx%d (%s)" % (res["rows"], res["cols"], kind))
    rd = res.get("row_dominance", [])
    if rd:
        for dom, sub, k in rd:
            lines.append("  ROW %s: %s dominates %s" % (k.upper(), rl[dom], rl[sub]))
    else:
        lines.append("  No row option is dominated.")
    for dom, sub, k in res.get("col_dominance", []):
        lines.append("  COL %s: %s dominates %s" % (k.upper(), cl[dom], cl[sub]))
    it = res["iesds"]
    lines.append("  Survive iterated strict elimination: rows=%s cols=%s" % (
        [rl[i] for i in it["rows"]], [cl[j] for j in it["cols"]]))
    if "expected_row_payoff" in res:
        exp = res["expected_row_payoff"]
        lines.append("  Expected payoff for column weights: " + ", ".join(
            "%s=%.3f" % (rl[i], exp[i]) for i in range(len(exp))))
        lines.append("  Best option for that mix: %s" % rl[res["best_row_for_weights"]])
    if "pure_nash" in res:
        pn = res["pure_nash"]
        if pn:
            lines.append("  Pure Nash equilibria: " + ", ".join("(%s, %s)" % (rl[i], cl[j]) for i, j in pn))
        else:
            lines.append("  No pure Nash equilibrium.")
    if res.get("mixed"):
        mx = res["mixed"]
        lines.append("  Mixed (fictitious play, %d iters): row " % mx["iters"] + ", ".join(
            "%s=%.3f" % (rl[i], v) for i, v in enumerate(mx["row_mix"])))
        lines.append("                                 col " + ", ".join(
            "%s=%.3f" % (cl[j], v) for j, v in enumerate(mx["col_mix"])))
        lo, hi = mx["value_bounds"]
        lines.append("  Game value (row player) between %.3f and %.3f" % (lo, hi))
    if "mixed_2x2" in res:
        m2 = res["mixed_2x2"]
        if m2:
            lines.append("  Mixed 2x2 equilibrium: P(%s)=%.3f, P(%s)=%.3f" % (rl[0], m2["p_row0"], cl[0], m2["q_col0"]))
        else:
            lines.append("  No fully mixed 2x2 equilibrium (or matrix not 2x2).")
    return "\n".join(lines)


# --------------------------------------------------------------------------- PRD

def prd_rate(c: float) -> float:
    """Long-run proc rate for PRD constant c (chance = n*c on the n-th attempt since last proc)."""
    if c <= 0:
        return 0.0
    expected = 0.0
    survive = 1.0
    n = 1
    while True:
        q = min(1.0, n * c)
        expected += n * survive * q
        survive *= (1.0 - q)
        if q >= 1.0 or survive <= 0.0:
            break
        n += 1
    return 1.0 / expected


def prd_constant(p: float) -> float:
    if not (0.0 < p < 1.0):
        raise InputError("--p must be strictly between 0 and 1")
    lo, hi = 0.0, p
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if prd_rate(mid) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


# --------------------------------------------------------------------------- Elo / series

def elo_p(diff: float) -> float:
    return 1.0 / (1.0 + 10.0 ** (-diff / 400.0))


def elo_diff(p: float) -> float:
    if not (0.0 < p < 1.0):
        raise InputError("--p must be strictly between 0 and 1")
    return 400.0 * math.log10(p / (1.0 - p))


def series_p(p: float, n: int) -> float:
    if n < 1 or n % 2 == 0:
        raise InputError("--best-of must be a positive odd integer")
    need = n // 2 + 1
    return sum(math.comb(n, k) * p ** k * (1 - p) ** (n - k) for k in range(need, n + 1))


# --------------------------------------------------------------------------- EV

def parse_outcomes(text: str) -> List[Tuple[float, float]]:
    out: List[Tuple[float, float]] = []
    for part in text.split(","):
        part = part.strip()
        if not part:
            continue
        if ":" not in part:
            raise InputError("outcome '%s' must be 'probability:value'" % part)
        p_txt, x_txt = part.split(":", 1)
        try:
            out.append((float(p_txt), float(x_txt)))
        except ValueError as exc:
            raise InputError("non-numeric outcome '%s'" % part) from exc
    if not out:
        raise InputError("no outcomes given")
    if any(p < 0 for p, _ in out):
        raise InputError("probabilities must be non-negative")
    total = sum(p for p, _ in out)
    if abs(total - 1.0) > 1e-6:
        raise InputError("probabilities sum to %.6f, expected 1" % total)
    return out


def ev_stats(outcomes: List[Tuple[float, float]]) -> Dict[str, float]:
    ev = sum(p * x for p, x in outcomes)
    var = sum(p * (x - ev) ** 2 for p, x in outcomes)
    return {
        "ev": ev,
        "variance": var,
        "sd": math.sqrt(var),
        "p_negative": sum(p for p, x in outcomes if x < 0),
        "min": min(x for _, x in outcomes),
        "max": max(x for _, x in outcomes),
    }


# --------------------------------------------------------------------------- selftest

def selftest() -> int:
    failures: List[str] = []
    counter = [0]

    def check(name: str, cond: bool) -> None:
        counter[0] += 1
        if not cond:
            failures.append(name)

    # Weighted RPS: t:m:s = b:a:c with a=1, b=2, c=3 -> 1/3, 1/6, 1/2
    A, B, zs = parse_payoff("0,-3,1;3,0,-2;-1,2,0")
    res = analyse_matrix(A, B, zs, False, None, 60000)
    mix = res["mixed"]["row_mix"]
    check("weighted RPS mix", all(abs(a - b) < 0.01 for a, b in zip(mix, [1 / 3, 1 / 6, 1 / 2])))
    check("weighted RPS no pure NE", res["pure_nash"] == [])
    check("weighted RPS no dominance", not has_strict_domination(res))

    # Prisoner's dilemma
    A, B, zs = parse_payoff("3/3,0/5;5/0,1/1")
    res = analyse_matrix(A, B, zs, False, None, 1000)
    check("PD row dominance", (1, 0, "strict") in res["row_dominance"])
    check("PD pure NE", res["pure_nash"] == [(1, 1)])
    check("PD iesds", res["iesds"]["rows"] == [1] and res["iesds"]["cols"] == [1])

    # Matching pennies 2x2 mixed
    A, B, zs = parse_payoff("1/-1,-1/1;-1/1,1/-1")
    res = analyse_matrix(A, B, zs, False, None, 1000)
    m2 = res["mixed_2x2"]
    check("pennies mixed", m2 is not None and abs(m2["p_row0"] - 0.5) < 1e-9 and abs(m2["q_col0"] - 0.5) < 1e-9)

    # Options vs situations with weights; Sword dominates Shield
    A, B, zs = parse_payoff("3,2,4;1,1,2;2,3,1")
    res = analyse_matrix(A, B, zs, True, [0.5, 0.3, 0.2], 1000)
    check("sword dominates shield", (0, 1, "strict") in res["row_dominance"])
    check("situations skip NE", "pure_nash" not in res)
    check("weighted best = sword", res["best_row_for_weights"] == 0)

    # PRD
    check("PRD 25%", abs(prd_constant(0.25) - 0.08474) < 1e-4)
    check("PRD 10%", abs(prd_constant(0.10) - 0.01475) < 1e-4)

    # Elo and series
    check("elo 200", abs(elo_p(200) - 0.7597) < 1e-3)
    check("elo diff 0.75", abs(elo_diff(0.75) - 190.85) < 0.01)
    check("bo7 p=0.6", abs(series_p(0.6, 7) - 0.7102) < 1e-3)

    # EV
    st = ev_stats(parse_outcomes("0.6:25,0.4:-5"))
    check("ev", abs(st["ev"] - 13) < 1e-9 and abs(st["variance"] - 216) < 1e-9)

    # Input validation
    for bad_name, bad_call in (("ragged matrix", lambda: parse_payoff("1,2;3")),
                               ("bad probability sum", lambda: parse_outcomes("0.5:1,0.4:2")),
                               ("even best-of", lambda: series_p(0.6, 4))):
        try:
            bad_call()
            check(bad_name + " rejected", False)
        except InputError:
            check(bad_name + " rejected", True)

    if failures:
        print("SELFTEST FAILED: " + "; ".join(failures))
        return 1
    print("selftest ok (%d checks)" % counter[0])
    return 0


# --------------------------------------------------------------------------- CLI

def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Decision maths for game design (dominance, equilibria, PRD, Elo, EV).")
    ap.add_argument("--selftest", action="store_true", help="run built-in fixtures and exit")
    sub = ap.add_subparsers(dest="cmd")

    m = sub.add_parser("matrix", help="analyse a payoff matrix")
    m.add_argument("--payoff", required=True, help="rows ';' cells ','; 'a/b' cells for general games")
    m.add_argument("--labels", help="comma-separated row labels")
    m.add_argument("--col-labels", help="comma-separated column labels (default: same as rows if square)")
    m.add_argument("--col-weights", help="situation/opponent frequencies for expected payoff per row")
    m.add_argument("--situations", action="store_true", help="columns are situations, not an opponent")
    m.add_argument("--iters", type=int, default=100000, help="fictitious-play iterations (zero-sum)")
    m.add_argument("--fail-on-dominated", action="store_true", help="exit 1 if any strategy is strictly dominated")
    m.add_argument("--json", action="store_true")

    p = sub.add_parser("prd", help="pseudo-random distribution constant")
    p.add_argument("--p", type=float, required=True, help="nominal chance per attempt (0-1)")
    p.add_argument("--json", action="store_true")

    e = sub.add_parser("elo", help="Elo odds and best-of-N series odds")
    g = e.add_mutually_exclusive_group(required=True)
    g.add_argument("--diff", type=float, help="rating difference")
    g.add_argument("--p", type=float, help="single-game win probability")
    e.add_argument("--best-of", type=int, help="odd series length")
    e.add_argument("--json", action="store_true")

    v = sub.add_parser("ev", help="expected value and variance of outcomes")
    v.add_argument("--outcomes", required=True, help="'p:x,p:x,...' probabilities summing to 1")
    v.add_argument("--json", action="store_true")
    return ap


def emit(data: Dict[str, object], as_json: bool, text: str) -> None:
    if as_json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print(text)


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = build_parser()
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.cmd:
        ap.print_help()
        return 2
    try:
        if args.cmd == "matrix":
            A, B, zs = parse_payoff(args.payoff)
            m, n = len(A), len(A[0])
            rl = parse_labels(args.labels, m, "R")
            if args.col_labels:
                cl = parse_labels(args.col_labels, n, "C")
            elif args.labels and m == n and not args.situations:
                cl = list(rl)
            else:
                cl = parse_labels(None, n, "C")
            weights = parse_weights(args.col_weights, n)
            res = analyse_matrix(A, B, zs, args.situations, weights, args.iters)
            res["row_labels"] = rl
            res["col_labels"] = cl
            emit(res, args.json, format_matrix_report(res, rl, cl))
            if args.fail_on_dominated and has_strict_domination(res):
                return 1
            return 0
        if args.cmd == "prd":
            c = prd_constant(args.p)
            max_attempts = int(math.ceil(1.0 / c))
            data = {"p": args.p, "C": c, "expected_attempts": 1.0 / args.p,
                    "max_attempts_to_guaranteed_proc": max_attempts}
            emit(data, args.json, "PRD for nominal p=%.4f: C=%.5f (%.3f%%); expected attempts %.2f; "
                                  "proc guaranteed by attempt %d" % (args.p, c, c * 100, 1.0 / args.p, max_attempts))
            return 0
        if args.cmd == "elo":
            if args.diff is not None:
                p = elo_p(args.diff)
                diff = args.diff
            else:
                p = args.p
                diff = elo_diff(p)
            data: Dict[str, object] = {"diff": diff, "p": p, "tiers_per_1000_points": 1000.0 / elo_diff(0.75)}
            text = "Rating diff %.1f <-> single-game win probability %.4f" % (diff, p)
            if args.best_of:
                sp = series_p(p, args.best_of)
                data["best_of"] = args.best_of
                data["series_p"] = sp
                text += "; best-of-%d series win probability %.4f" % (args.best_of, sp)
            emit(data, args.json, text)
            return 0
        if args.cmd == "ev":
            st = ev_stats(parse_outcomes(args.outcomes))
            emit(st, args.json, "EV=%.4f  variance=%.4f  SD=%.4f  P(negative)=%.4f  range=[%.4g, %.4g]" % (
                st["ev"], st["variance"], st["sd"], st["p_negative"], st["min"], st["max"]))
            return 0
    except InputError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    ap.print_help()
    return 2


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows pipes default to the ANSI code page; Claude Code reads UTF-8
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
