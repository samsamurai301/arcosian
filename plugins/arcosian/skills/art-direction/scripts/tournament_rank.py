#!/usr/bin/env python3
"""tournament_rank.py - comparative (pairwise) judging for art candidates.

Absolute 1-10 scores from a critic or VLM drift and cluster; "which of these two
better fits the style bible?" is a more reliable question. This tool schedules
pairwise comparisons, controls position bias (every pair shown in both orders),
and turns the votes into a ranking with a Bradley-Terry model.

Subcommands
  schedule  --items a,b,c [--mode roundrobin|sample] [--per-item K] [--seed S] [--single-order]
            Prints comparison jobs. roundrobin = every pair; sample = each item meets
            about K random opponents (use for 12+ candidates). Default: both orders.
  next      --items a,b,c --votes PATH [--seed S]
            Swiss-style next round: fit the votes so far, pair neighbours in the
            current ranking that have not met yet (both orders).
  rank      --votes PATH [--bootstrap N] [--seed S] [--min-margin P]
            Bradley-Terry strengths, Elo-scale ratings, win rates, the position-bias
            rate, and (with --bootstrap) how often each item ranks first.

Votes file: CSV with header left,right,winner[,judge][,criterion] or a JSON list
of objects with those keys. winner is the left id, the right id, or "tie".
A pair judged in both orders by the same judge with position-following verdicts
(each order picked whichever was shown on the left, or each picked the right)
is scored as a tie and counted in the position-bias rate.

rank exits 1 when --min-margin is given and the top item's modelled win
probability over the runner-up is below it (no clear winner: judge more pairs
or escalate to the human checkpoint).
Exit codes: 0 ok, 1 check failed, 2 usage/input error. Stdlib only; Python 3.9+.
"""
from __future__ import annotations

import argparse
import csv
import io
import itertools
import json
import math
import random
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

Vote = Dict[str, str]


class InputError(ValueError):
    """Malformed input (exit code 2)."""


# --------------------------------------------------------------------------- io

def load_votes(path: str) -> List[Vote]:
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise InputError("cannot read votes %s: %s" % (path, exc))
    stripped = text.lstrip()
    if stripped.startswith("[") or stripped.startswith("{"):
        try:
            doc = json.loads(text)
        except ValueError as exc:
            raise InputError("bad JSON in %s: %s" % (path, exc))
        rows = doc.get("votes", []) if isinstance(doc, dict) else doc
    else:
        rows = list(csv.DictReader(io.StringIO(text)))
    votes: List[Vote] = []
    for i, r in enumerate(rows):
        try:
            left, right, winner = str(r["left"]).strip(), str(r["right"]).strip(), str(r["winner"]).strip()
        except (KeyError, TypeError):
            raise InputError("vote %d needs left, right and winner" % (i + 1))
        if left == right:
            raise InputError("vote %d compares %s with itself" % (i + 1, left))
        if winner not in (left, right, "tie"):
            raise InputError("vote %d: winner %r is neither %s, %s nor 'tie'" % (i + 1, winner, left, right))
        votes.append({"left": left, "right": right, "winner": winner,
                      "judge": str(r.get("judge", "") or ""), "criterion": str(r.get("criterion", "") or "")})
    if not votes:
        raise InputError("no votes in %s" % path)
    return votes


def parse_items(text: str) -> List[str]:
    items = [s.strip() for s in text.split(",") if s.strip()]
    if len(items) < 2:
        raise InputError("need at least two items")
    if len(set(items)) != len(items):
        raise InputError("duplicate item ids")
    return items


# --------------------------------------------------------------------------- scoring

def outcomes(votes: Sequence[Vote]) -> Tuple[List[Tuple[str, str, float]], Dict[str, float]]:
    """Collapse votes to (a, b, score_a) results, neutralising position-following pairs."""
    groups: Dict[Tuple[str, str, str, str], List[Vote]] = defaultdict(list)
    for v in votes:
        a, b = sorted((v["left"], v["right"]))
        groups[(a, b, v["judge"], v["criterion"])].append(v)
    results: List[Tuple[str, str, float]] = []
    both_orders = 0
    biased = 0
    left_wins = sum(1 for v in votes if v["winner"] == v["left"])
    decided = sum(1 for v in votes if v["winner"] != "tie")
    for (a, b, _j, _c), vs in groups.items():
        ab = [v for v in vs if v["left"] == a]
        ba = [v for v in vs if v["left"] == b]
        paired = min(len(ab), len(ba))
        for k in range(paired):
            both_orders += 1
            v1, v2 = ab[k], ba[k]
            pos1 = "L" if v1["winner"] == v1["left"] else ("R" if v1["winner"] == v1["right"] else "T")
            pos2 = "L" if v2["winner"] == v2["left"] else ("R" if v2["winner"] == v2["right"] else "T")
            if pos1 == pos2 and pos1 != "T":
                biased += 1
                results.append((a, b, 0.5))
            else:
                s = sum(1.0 if v["winner"] == a else (0.5 if v["winner"] == "tie" else 0.0) for v in (v1, v2)) / 2.0
                results.append((a, b, s))
        for v in ab[paired:] + ba[paired:]:
            results.append((a, b, 1.0 if v["winner"] == a else (0.5 if v["winner"] == "tie" else 0.0)))
    stats = {
        "votes": float(len(votes)),
        "comparisons": float(len(results)),
        "both_order_pairs": float(both_orders),
        "position_bias_rate": round(biased / both_orders, 3) if both_orders else 0.0,
        "left_win_share": round(left_wins / decided, 3) if decided else 0.0,
    }
    return results, stats


def bradley_terry(items: Sequence[str], results: Sequence[Tuple[str, str, float]],
                  prior: float = 0.5, iters: int = 2000, tol: float = 1e-10) -> Dict[str, float]:
    """MM algorithm (Hunter 2004). Each item also plays `prior` win + `prior` loss against a
    virtual reference of strength 1, which keeps undefeated/winless items finite."""
    p = {i: 1.0 for i in items}
    wins = defaultdict(float)
    games: Dict[Tuple[str, str], float] = defaultdict(float)
    for a, b, s in results:
        wins[a] += s
        wins[b] += 1.0 - s
        games[(a, b)] += 1.0
        games[(b, a)] += 1.0
    opponents: Dict[str, List[Tuple[str, float]]] = defaultdict(list)
    for (a, b), n in games.items():
        opponents[a].append((b, n))
    for _ in range(iters):
        new = {}
        for i in items:
            denom = sum(n / (p[i] + p[j]) for j, n in opponents[i]) + 2 * prior / (p[i] + 1.0)
            new[i] = (wins[i] + prior) / denom if denom > 0 else p[i]
        g = math.exp(sum(math.log(v) for v in new.values()) / len(new))
        new = {k: v / g for k, v in new.items()}
        delta = max(abs(new[i] - p[i]) for i in items)
        p = new
        if delta < tol:
            break
    return p


def rank(items: Sequence[str], votes: Sequence[Vote], bootstrap: int = 0, seed: int = 1) -> Dict[str, object]:
    results, stats = outcomes(votes)
    p = bradley_terry(items, results)
    order = sorted(items, key=lambda i: -p[i])
    played = defaultdict(float)
    score = defaultdict(float)
    for a, b, s in results:
        played[a] += 1
        played[b] += 1
        score[a] += s
        score[b] += 1 - s
    table = []
    for pos, i in enumerate(order, 1):
        table.append({
            "rank": pos, "item": i, "strength": round(p[i], 4),
            "elo": round(1500 + 400 * math.log10(p[i]), 0),
            "comparisons": int(played[i]),
            "win_rate": round(score[i] / played[i], 3) if played[i] else None,
        })
    out: Dict[str, object] = {"stats": stats, "ranking": table}
    if len(order) >= 2:
        a, b = order[0], order[1]
        out["top_vs_runner_up"] = {"top": a, "runner_up": b, "p_top_wins": round(p[a] / (p[a] + p[b]), 3)}
    if bootstrap > 0:
        rng = random.Random(seed)
        firsts = defaultdict(int)
        ranks: Dict[str, List[int]] = defaultdict(list)
        n = len(results)
        for _ in range(bootstrap):
            sample = [results[rng.randrange(n)] for _ in range(n)]
            q = bradley_terry(items, sample, iters=300, tol=1e-7)
            o = sorted(items, key=lambda i: -q[i])
            firsts[o[0]] += 1
            for pos, i in enumerate(o, 1):
                ranks[i].append(pos)
        for row in table:
            rs = sorted(ranks[row["item"]])
            row["p_first"] = round(firsts[row["item"]] / bootstrap, 3)
            row["rank_90ci"] = [rs[int(0.05 * (len(rs) - 1))], rs[int(0.95 * (len(rs) - 1))]]
    return out


# --------------------------------------------------------------------------- scheduling

def schedule(items: Sequence[str], mode: str, per_item: int, seed: int, both: bool) -> List[Dict[str, str]]:
    rng = random.Random(seed)
    if mode == "roundrobin":
        pairs = list(itertools.combinations(items, 2))
    elif mode == "sample":
        if per_item < 1:
            raise InputError("--per-item must be >= 1")
        pairs_set = set()
        need = {i: per_item for i in items}
        attempts = 0
        while any(v > 0 for v in need.values()) and attempts < 100 * len(items) * per_item:
            attempts += 1
            pool = sorted((i for i in items if need[i] > 0), key=lambda i: (-need[i], rng.random()))
            a = pool[0]
            cands = [j for j in items if j != a and tuple(sorted((a, j))) not in pairs_set]
            if not cands:
                need[a] = 0
                continue
            cands.sort(key=lambda j: (-need[j], rng.random()))
            b = cands[0]
            pairs_set.add(tuple(sorted((a, b))))
            need[a] -= 1
            need[b] -= 1
        pairs = sorted(pairs_set)
    else:
        raise InputError("unknown mode %r" % mode)
    rng.shuffle(pairs)
    jobs = []
    for a, b in pairs:
        if rng.random() < 0.5:
            a, b = b, a
        jobs.append({"left": a, "right": b})
        if both:
            jobs.append({"left": b, "right": a})
    return jobs


def next_round(items: Sequence[str], votes: Sequence[Vote]) -> List[Dict[str, str]]:
    results, _ = outcomes(votes)
    p = bradley_terry(items, results)
    met = {tuple(sorted((a, b))) for a, b, _ in results}
    order = sorted(items, key=lambda i: -p[i])
    unpaired = list(order)
    jobs = []
    while len(unpaired) >= 2:
        a = unpaired.pop(0)
        partner = next((b for b in unpaired if tuple(sorted((a, b))) not in met), None)
        if partner is None:
            continue
        unpaired.remove(partner)
        jobs.append({"left": a, "right": partner})
        jobs.append({"left": partner, "right": a})
    return jobs


# --------------------------------------------------------------------------- selftest

def selftest() -> int:
    checks = []
    rng = random.Random(7)
    true = {"A": 4.0, "B": 2.0, "C": 1.0, "D": 0.5}
    votes = []
    for _ in range(60):
        for a, b in itertools.permutations(true, 2):
            pa = true[a] / (true[a] + true[b])
            votes.append({"left": a, "right": b, "winner": a if rng.random() < pa else b, "judge": "", "criterion": ""})
    out = rank(list(true), votes)
    order = [r["item"] for r in out["ranking"]]
    checks.append(("recovers true order", order == ["A", "B", "C", "D"]))
    s = {r["item"]: r["strength"] for r in out["ranking"]}
    checks.append(("strength ratio A/D ~ 8", 5.0 < s["A"] / s["D"] < 12.0))
    # Position-biased judge: always picks left -> every both-order pair becomes a tie.
    biased = [{"left": a, "right": b, "winner": a, "judge": "j", "criterion": ""}
              for a, b in itertools.permutations(["x", "y", "z"], 2)]
    res, stats = outcomes(biased)
    checks.append(("bias rate 1.0", stats["position_bias_rate"] == 1.0))
    checks.append(("biased votes neutralised", all(sc == 0.5 for _, _, sc in res)))
    # Undefeated item stays finite.
    unb = [{"left": "w", "right": "l", "winner": "w", "judge": "", "criterion": ""}] * 3
    p = bradley_terry(["w", "l"], outcomes(unb)[0])
    checks.append(("undefeated finite", math.isfinite(p["w"]) and p["w"] > p["l"]))
    jobs = schedule(["a", "b", "c", "d"], "roundrobin", 0, 1, True)
    checks.append(("roundrobin both orders = 12 jobs", len(jobs) == 12))
    jobs = schedule([str(i) for i in range(16)], "sample", 4, 1, False)
    counts = defaultdict(int)
    for j in jobs:
        counts[j["left"]] += 1
        counts[j["right"]] += 1
    checks.append(("sample ~4 per item", min(counts.values()) >= 3 and max(counts.values()) <= 5))
    partial = [v for v in votes if {v["left"], v["right"]} in ({"A", "B"}, {"C", "D"})]
    nr = next_round(list(true), partial)
    fresh = all({j["left"], j["right"]} not in ({"A", "B"}, {"C", "D"}) for j in nr)
    checks.append(("next round: new pairs, both orders", len(nr) == 4 and fresh))
    boot = rank(list(true), votes, bootstrap=50, seed=3)
    checks.append(("bootstrap p_first A highest", boot["ranking"][0]["item"] == "A" and boot["ranking"][0]["p_first"] >= 0.5))
    ok = True
    for name, passed in checks:
        print("%-36s %s" % (name, "ok" if passed else "FAIL"))
        ok = ok and passed
    print("selftest: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    p.add_argument("--selftest", action="store_true", help="run built-in checks")
    sub = p.add_subparsers(dest="cmd")
    s = sub.add_parser("schedule", help="generate comparison jobs")
    s.add_argument("--items", required=True)
    s.add_argument("--mode", choices=["roundrobin", "sample"], default="roundrobin")
    s.add_argument("--per-item", type=int, default=4)
    s.add_argument("--seed", type=int, default=1)
    s.add_argument("--single-order", action="store_true", help="do not add the swapped-order job")
    s.add_argument("--json", action="store_true")
    n = sub.add_parser("next", help="Swiss-style next round from votes so far")
    n.add_argument("--items", required=True)
    n.add_argument("--votes", required=True)
    n.add_argument("--json", action="store_true")
    r = sub.add_parser("rank", help="Bradley-Terry ranking from votes")
    r.add_argument("--votes", required=True)
    r.add_argument("--items", help="optional full item list (items with no votes rank by prior)")
    r.add_argument("--bootstrap", type=int, default=0)
    r.add_argument("--seed", type=int, default=1)
    r.add_argument("--min-margin", type=float, default=None,
                   help="fail (exit 1) if P(top beats runner-up) is below this, e.g. 0.65")
    r.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.cmd:
        p.print_help()
        return 2
    try:
        if args.cmd == "schedule":
            jobs = schedule(parse_items(args.items), args.mode, args.per_item, args.seed, not args.single_order)
            if args.json:
                print(json.dumps({"jobs": jobs}, indent=2))
            else:
                print("left,right")
                for j in jobs:
                    print("%s,%s" % (j["left"], j["right"]))
            return 0
        votes = load_votes(args.votes)
        seen = sorted({v["left"] for v in votes} | {v["right"] for v in votes})
        if args.cmd == "next":
            items = parse_items(args.items)
            jobs = next_round(items, votes)
            print(json.dumps({"jobs": jobs}, indent=2) if args.json else
                  "left,right\n" + "\n".join("%s,%s" % (j["left"], j["right"]) for j in jobs))
            return 0
        items = parse_items(args.items) if args.items else seen
        missing = set(seen) - set(items)
        if missing:
            raise InputError("votes mention items not in --items: %s" % ", ".join(sorted(missing)))
        out = rank(items, votes, args.bootstrap, args.seed)
    except InputError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    verdict_ok = True
    if args.min_margin is not None and "top_vs_runner_up" in out:
        verdict_ok = out["top_vs_runner_up"]["p_top_wins"] >= args.min_margin  # type: ignore[index]
        out["clear_winner"] = verdict_ok
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        st = out["stats"]
        print("votes %d, comparisons %d, both-order pairs %d, position-bias rate %.2f, left-win share %.2f" % (
            st["votes"], st["comparisons"], st["both_order_pairs"], st["position_bias_rate"], st["left_win_share"]))  # type: ignore[index]
        for row in out["ranking"]:  # type: ignore[union-attr]
            extra = ""
            if "p_first" in row:
                extra = "  P(first) %.2f  rank 90%% CI %s" % (row["p_first"], row["rank_90ci"])
            wr = "-" if row["win_rate"] is None else "%.2f" % row["win_rate"]
            print("%2d. %-20s strength %.3f  elo %5.0f  n=%d  win %s%s" % (
                row["rank"], row["item"], row["strength"], row["elo"], row["comparisons"], wr, extra))
        if "top_vs_runner_up" in out:
            t = out["top_vs_runner_up"]
            print("P(%s beats %s) = %.2f" % (t["top"], t["runner_up"], t["p_top_wins"]))  # type: ignore[index]
        if args.min_margin is not None:
            print("clear winner: %s" % ("yes" if verdict_ok else "no - judge more pairs or escalate to a human"))
    return 0 if verdict_ok else 1


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows pipes default to the ANSI code page; Claude Code reads UTF-8
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
