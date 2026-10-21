#!/usr/bin/env python3
"""Exact solver for level-spec puzzles: sliding, sokoban, sort, lights_out.

  puzzle_solver.py --level PATH [--algo bfs|astar] [--max-nodes N] [--json]

PATH is a level-spec JSON (scripts/schemas/level-spec.schema.json) whose layout.type is one of the four
types. Reports solvable, min_moves (optimal for bfs and for the admissible A* heuristics used here),
a move path, nodes expanded and difficulty signals. The move limit (moves_or_time_limit) is checked too.
Moves: sliding = tile + direction, sokoban = u/d/l/r (capital = push), sort = "i->j" (1-based tubes),
lights_out = "row,col" presses (solved by GF(2) elimination; --algo is ignored there).
Exit 0 solvable within the move limit, 1 unsolvable / over limit / search truncated, 2 usage or input error.
"""
from __future__ import annotations

import argparse
import heapq
import json
import math
import sys
from collections import deque
from pathlib import Path
from typing import Any, Callable, Dict, Hashable, Iterable, List, Optional, Sequence, Tuple

Move = Tuple[str, Any]  # (label, next_state)


class InputError(Exception):
    pass


def search(start: Any, is_goal: Callable[[Any], bool], neighbors: Callable[[Any], Iterable[Move]],
           key: Callable[[Any], Hashable], algo: str, h: Callable[[Any], int], max_nodes: int) -> Dict[str, Any]:
    """BFS or A* (unit costs). Returns found, path, nodes, truncated, branching."""
    k0 = key(start)
    parent: Dict[Hashable, Tuple[Optional[Hashable], str]] = {k0: (None, "")}
    nodes = edges = 0
    goal_key: Optional[Hashable] = None

    def build(gk: Hashable) -> List[str]:
        out: List[str] = []
        while parent[gk][0] is not None:
            out.append(parent[gk][1])
            gk = parent[gk][0]  # type: ignore[assignment]
        return out[::-1]

    if is_goal(start):
        return {"found": True, "path": [], "nodes": 0, "truncated": False, "branching": 0.0}
    if algo == "bfs":
        q = deque([(start, 0)])
        while q:
            s, d = q.popleft()
            nodes += 1
            if nodes > max_nodes:
                break
            for label, n in neighbors(s):
                edges += 1
                kn = key(n)
                if kn in parent:
                    continue
                parent[kn] = (key(s), label)
                if is_goal(n):
                    return {"found": True, "path": build(kn), "nodes": nodes, "truncated": False,
                            "branching": round(edges / nodes, 3)}
                q.append((n, d + 1))
    else:
        best = {k0: 0}
        tie = 0
        heap = [(h(start), 0, tie, start)]
        closed = set()
        while heap:
            f, g, _, s = heapq.heappop(heap)
            ks = key(s)
            if ks in closed or g > best.get(ks, g):
                continue
            closed.add(ks)
            nodes += 1
            if is_goal(s):
                return {"found": True, "path": build(ks), "nodes": nodes, "truncated": False,
                        "branching": round(edges / max(nodes, 1), 3)}
            if nodes > max_nodes:
                break
            for label, n in neighbors(s):
                edges += 1
                kn = key(n)
                if g + 1 < best.get(kn, 1 << 60):
                    best[kn] = g + 1
                    parent[kn] = (ks, label)
                    tie += 1
                    heapq.heappush(heap, (g + 1 + h(n), g + 1, tie, n))
    truncated = nodes > max_nodes
    return {"found": False, "path": None, "nodes": min(nodes, max_nodes) if truncated else nodes,
            "truncated": truncated, "branching": round(edges / max(nodes, 1), 3)}


# ---------------------------------------------------------------- sliding

def sliding_problem(layout: Dict[str, Any]) -> Dict[str, Any]:
    grid = layout.get("grid")
    if not grid or len({len(r) for r in grid}) != 1:
        raise InputError("sliding: grid must be a rectangular matrix")
    R, C = len(grid), len(grid[0])
    start = tuple(v for r in grid for v in r)
    goal = layout.get("goal")
    if goal:
        goal_t = tuple(v for r in goal for v in r)
    else:
        goal_t = tuple(list(range(1, R * C)) + [0])
    if sorted(start) != sorted(goal_t) or len(set(start)) != len(start):
        raise InputError("sliding: start and goal must hold the same distinct tiles (0 = blank)")
    gpos = {v: i for i, v in enumerate(goal_t)}
    dirs = ((-1, 0, "up"), (1, 0, "down"), (0, -1, "left"), (0, 1, "right"))

    def neighbors(s: Tuple[int, ...]) -> Iterable[Move]:
        b = s.index(0)
        br, bc = divmod(b, C)
        for dr, dc, name in dirs:
            r, c = br + dr, bc + dc
            if 0 <= r < R and 0 <= c < C:
                t = r * C + c
                lst = list(s)
                lst[b], lst[t] = lst[t], 0
                yield "%d %s" % (s[t], {"up": "down", "down": "up", "left": "right", "right": "left"}[name]), tuple(lst)

    def h(s: Tuple[int, ...]) -> int:
        tot = 0
        for i, v in enumerate(s):
            if v:
                g = gpos[v]
                tot += abs(i // C - g // C) + abs(i % C - g % C)
        return tot

    # parity: each move is a transposition involving the blank, which also moves one cell
    perm = [gpos[v] for v in start]
    seen = [False] * len(perm)
    parity = 0
    for i in range(len(perm)):
        if not seen[i]:
            j, ln = i, 0
            while not seen[j]:
                seen[j] = True
                j = perm[j]
                ln += 1
            parity += ln - 1
    b0, b1 = start.index(0), goal_t.index(0)
    dist = abs(b0 // C - b1 // C) + abs(b0 % C - b1 % C)
    impossible = (parity - dist) % 2 != 0
    return {"start": start, "is_goal": lambda s: s == goal_t, "neighbors": neighbors, "key": lambda s: s, "h": h,
            "impossible": "parity: this arrangement cannot reach the goal" if impossible else None,
            "info": {"size": "%dx%d" % (R, C)}}


# ---------------------------------------------------------------- sokoban

def sokoban_problem(layout: Dict[str, Any]) -> Dict[str, Any]:
    rows = layout.get("rows")
    if not rows:
        raise InputError("sokoban: layout.rows required")
    W = max(len(r) for r in rows)
    walls, goals, boxes, player = set(), set(), set(), None
    for r, line in enumerate(rows):
        for c, ch in enumerate(line.ljust(W)):
            p = (r, c)
            if ch == "#":
                walls.add(p)
            if ch in ".+*":
                goals.add(p)
            if ch in "$*":
                boxes.add(p)
            if ch in "@+":
                if player is not None:
                    raise InputError("sokoban: more than one player")
                player = p
    if player is None or len(boxes) != len(goals) or not boxes:
        raise InputError("sokoban: need one player and as many boxes as goals (>= 1)")
    H = len(rows)

    def free(p: Tuple[int, int]) -> bool:
        return 0 <= p[0] < H and 0 <= p[1] < W and p not in walls

    # dead squares: cells from which a box can never be pushed to any goal (reverse "pull" flood)
    live = set(goals)
    stack = list(goals)
    D = ((-1, 0), (1, 0), (0, -1), (0, 1))
    while stack:
        r, c = stack.pop()
        for dr, dc in D:
            src, plr = (r + dr, c + dc), (r + 2 * dr, c + 2 * dc)
            if free(src) and free(plr) and src not in live:
                live.add(src)
                stack.append(src)
    names = {(-1, 0): "u", (1, 0): "d", (0, -1): "l", (0, 1): "r"}

    def neighbors(s: Tuple[Tuple[int, int], frozenset]) -> Iterable[Move]:
        p, bx = s
        for dr, dc in D:
            n = (p[0] + dr, p[1] + dc)
            if not free(n):
                continue
            if n in bx:
                bn = (n[0] + dr, n[1] + dc)
                if not free(bn) or bn in bx or bn not in live:
                    continue
                yield names[(dr, dc)].upper(), (n, (bx - {n}) | {bn})
            else:
                yield names[(dr, dc)], (n, bx)

    gl = sorted(goals)

    def h(s: Tuple[Tuple[int, int], frozenset]) -> int:
        return sum(min(abs(b[0] - g[0]) + abs(b[1] - g[1]) for g in gl) for b in s[1] if b not in goals)

    return {"start": (player, frozenset(boxes)), "is_goal": lambda s: s[1] == frozenset(goals),
            "neighbors": neighbors, "key": lambda s: s, "h": h,
            "impossible": "a box starts on a dead square" if any(b not in live for b in boxes) else None,
            "info": {"boxes": len(boxes), "size": "%dx%d" % (H, W)}}


# ---------------------------------------------------------------- sort

def sort_problem(layout: Dict[str, Any]) -> Dict[str, Any]:
    cap = layout.get("capacity")
    tubes = layout.get("tubes")
    if not isinstance(cap, int) or not tubes:
        raise InputError("sort: capacity and tubes required")
    single = layout.get("pour", "max") == "single"
    start = tuple(tuple(t) for t in tubes)
    if any(len(t) > cap for t in start):
        raise InputError("sort: a tube holds more than capacity")
    counts: Dict[str, int] = {}
    for t in start:
        for x in t:
            counts[x] = counts.get(x, 0) + 1
    if any(n != cap for n in counts.values()):
        raise InputError("sort: every colour must appear exactly capacity (%d) times: %s" % (cap, counts))
    ncol = len(counts)

    def solved(s: Tuple[Tuple[str, ...], ...]) -> bool:
        return all(not t or (len(t) == cap and len(set(t)) == 1) for t in s)

    def neighbors(s: Tuple[Tuple[str, ...], ...]) -> Iterable[Move]:
        for i, a in enumerate(s):
            if not a:
                continue
            col = a[-1]
            run = 1
            while run < len(a) and a[-1 - run] == col:
                run += 1
            uniform = run == len(a)
            for j, b in enumerate(s):
                if i == j or len(b) >= cap:
                    continue
                if b and b[-1] != col:
                    continue
                if not b and uniform:
                    continue  # moving a whole uniform stack into an empty tube achieves nothing
                n = 1 if single else min(run, cap - len(b))
                lst = list(s)
                lst[i], lst[j] = a[:-n], b + (col,) * n
                yield "%d->%d" % (i + 1, j + 1), tuple(lst)

    def key(s: Tuple[Tuple[str, ...], ...]) -> Hashable:
        return tuple(sorted(s))

    def h(s: Tuple[Tuple[str, ...], ...]) -> int:
        runs = sum(1 + sum(1 for k in range(1, len(t)) if t[k] != t[k - 1]) for t in s if t)
        return max(0, runs - ncol)  # a move removes at most one colour run

    return {"start": start, "is_goal": solved, "neighbors": neighbors, "key": key, "h": h, "impossible": None,
            "info": {"tubes": len(start), "colors": ncol, "capacity": cap, "empty_tubes": sum(1 for t in start if not t)}}


# ---------------------------------------------------------------- lights out (GF(2))

def lights_out_solve(grid: List[List[int]]) -> Dict[str, Any]:
    R, C = len(grid), len(grid[0])
    n = R * C
    # equation per cell: sum of presses on cell and neighbours = state, as bitmask rows with rhs in bit n
    rows = []
    for r in range(R):
        for c in range(C):
            m = 0
            for rr, cc in ((r, c), (r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
                if 0 <= rr < R and 0 <= cc < C:
                    m |= 1 << (rr * C + cc)
            if grid[r][c]:
                m |= 1 << n
            rows.append(m)
    piv: List[int] = []
    rank = 0
    for col in range(n):
        sel = next((i for i in range(rank, n) if rows[i] >> col & 1), None)
        if sel is None:
            continue
        rows[rank], rows[sel] = rows[sel], rows[rank]
        for i in range(n):
            if i != rank and rows[i] >> col & 1:
                rows[i] ^= rows[rank]
        piv.append(col)
        rank += 1
    if any(rows[i] == 1 << n for i in range(rank, n)):
        return {"found": False, "path": None, "nodes": 0, "truncated": False, "branching": float(n),
                "null_dim": n - rank}
    free = [c for c in range(n) if c not in piv]
    if len(free) > 20:
        raise InputError("lights_out: %d free variables, too many to enumerate" % len(free))
    best: Optional[int] = None
    for combo in range(1 << len(free)):
        x = 0
        for k, f in enumerate(free):
            if combo >> k & 1:
                x |= 1 << f
        for i, pc in enumerate(piv):
            v = rows[i] >> n & 1
            for f in free:
                if x >> f & 1 and rows[i] >> f & 1:
                    v ^= 1
            if v:
                x |= 1 << pc
        if best is None or bin(x).count("1") < bin(best).count("1"):
            best = x
    path = ["%d,%d" % (i // C + 1, i % C + 1) for i in range(n) if best >> i & 1]  # type: ignore[operator]
    return {"found": True, "path": path, "nodes": 1 << len(free), "truncated": False, "branching": float(n),
            "null_dim": len(free)}


# ---------------------------------------------------------------- driver

def band(nodes: int, moves: int) -> str:
    score = math.log10(nodes + 1) + moves / 30.0
    return "trivial" if score < 1.5 else "easy" if score < 2.5 else "medium" if score < 3.5 else "hard" if score < 4.5 else "expert"


def move_limit(spec: Dict[str, Any]) -> Optional[int]:
    lim = spec.get("moves_or_time_limit")
    if isinstance(lim, dict):
        lim = lim.get("moves")
    return lim if isinstance(lim, int) and lim > 0 else None


def solve_spec(spec: Dict[str, Any], algo: str = "bfs", max_nodes: int = 2_000_000) -> Dict[str, Any]:
    layout = spec.get("layout")
    if not isinstance(layout, dict) or layout.get("type") not in ("sliding", "sokoban", "sort", "lights_out"):
        raise InputError("layout.type must be sliding, sokoban, sort or lights_out")
    typ = layout["type"]
    if typ == "lights_out":
        g = layout.get("grid")
        if not g or len({len(r) for r in g}) != 1:
            raise InputError("lights_out: grid must be a rectangular 0/1 matrix")
        r = lights_out_solve(g)
        info: Dict[str, Any] = {"size": "%dx%d" % (len(g), len(g[0])), "null_space_dim": r.pop("null_dim")}
        impossible = None
    else:
        prob = {"sliding": sliding_problem, "sokoban": sokoban_problem, "sort": sort_problem}[typ](layout)
        info, impossible = prob["info"], prob["impossible"]
        if impossible:
            r = {"found": False, "path": None, "nodes": 0, "truncated": False, "branching": 0.0}
        else:
            r = search(prob["start"], prob["is_goal"], prob["neighbors"], prob["key"], algo, prob["h"], max_nodes)
    limit = move_limit(spec)
    mm = len(r["path"]) if r["found"] else None
    within = None if mm is None else (limit is None or mm <= limit)
    sig = dict(info)
    sig.update({"branching_factor": r["branching"], "move_limit": limit,
                "limit_slack": round(limit / mm, 2) if (limit and mm) else None})
    if mm is not None:
        sig["difficulty_band"] = band(r["nodes"], mm)
    return {"level_id": spec.get("level_id"), "type": typ, "algo": "algebra" if typ == "lights_out" else algo,
            "solvable": bool(r["found"]), "within_limit": within, "min_moves": mm,
            "path": r["path"], "nodes": r["nodes"], "truncated": r["truncated"],
            "reason": impossible or ("search truncated at max-nodes: result unknown" if r["truncated"] else
                                     (None if r["found"] else "state space exhausted: no solution")),
            "signals": sig,
            "solver": {"solvable": bool(r["found"]) and bool(within in (True, None)), "min_moves": mm,
                       "algo": "algebra" if typ == "lights_out" else algo, "states_visited": r["nodes"]}}


def selftest() -> int:
    fails: List[str] = []

    def spec(layout: Dict[str, Any], limit: Any = None) -> Dict[str, Any]:
        return {"level_id": "t", "layout": layout, "moves_or_time_limit": limit}

    # sliding: one move from solved, and the classic unsolvable swap
    r = solve_spec(spec({"type": "sliding", "grid": [[1, 2, 3], [4, 5, 6], [7, 0, 8]]}))
    if not (r["solvable"] and r["min_moves"] == 1):
        fails.append("sliding 1 move %s" % r)
    r = solve_spec(spec({"type": "sliding", "grid": [[1, 2, 3], [4, 5, 6], [8, 7, 0]]}))
    if r["solvable"]:
        fails.append("sliding parity swap must be unsolvable")
    hard = {"type": "sliding", "grid": [[8, 6, 7], [2, 5, 4], [3, 0, 1]]}  # known optimum: 31 moves
    a = solve_spec(spec(hard), "bfs")
    b = solve_spec(spec(hard), "astar")
    if a["min_moves"] != 31 or b["min_moves"] != 31:
        fails.append("8-puzzle hardest: bfs %s astar %s" % (a["min_moves"], b["min_moves"]))
    if b["nodes"] >= a["nodes"]:
        fails.append("astar should expand fewer nodes than bfs")
    # sokoban: push right twice -> 1 box, minimal 2 pushes? start @$ . with one gap
    r = solve_spec(spec({"type": "sokoban", "rows": ["#######", "#@$ . #", "#######"]}))
    if not (r["solvable"] and r["min_moves"] == 2 and r["path"] == ["R", "R"]):
        fails.append("sokoban %s" % r)
    r = solve_spec(spec({"type": "sokoban", "rows": ["#####", "#.$@#", "#####"]}), "astar")
    if not (r["solvable"] and r["min_moves"] == 1):
        fails.append("sokoban pull-side %s" % r)
    r = solve_spec(spec({"type": "sokoban", "rows": ["######", "#$ @.#", "######"]}))
    if r["solvable"]:
        fails.append("sokoban dead box must be unsolvable")
    # sort
    sortl = {"type": "sort", "capacity": 2, "tubes": [["a", "b"], ["b", "a"], []]}
    a = solve_spec(spec(sortl), "bfs")
    b = solve_spec(spec(sortl), "astar")
    if not (a["solvable"] and a["min_moves"] == 3 and b["min_moves"] == 3):
        fails.append("sort 3 moves: %s / %s" % (a["min_moves"], b["min_moves"]))
    r = solve_spec(spec(sortl, 2))
    if r["within_limit"] is not False:
        fails.append("move limit not enforced")
    r = solve_spec(spec({"type": "sort", "capacity": 2, "tubes": [["a", "b"], ["b", "a"]]}))
    if r["solvable"]:
        fails.append("sort without empty tube must be unsolvable")
    # lights out: 3x3 centre press, and an unsolvable-free 5x5 corner check
    r = solve_spec(spec({"type": "lights_out", "grid": [[0, 1, 0], [1, 1, 1], [0, 1, 0]]}))
    if not (r["solvable"] and r["min_moves"] == 1 and r["path"] == ["2,2"]):
        fails.append("lights_out centre %s" % r)
    r = solve_spec(spec({"type": "lights_out", "grid": [[1, 1, 0, 0, 0], [1, 0, 0, 0, 0]] + [[0] * 5] * 3}))
    if not r["solvable"] or r["min_moves"] != 1:
        fails.append("lights_out 5x5 corner %s" % r)
    r = solve_spec(spec({"type": "lights_out", "grid": [[1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]}))
    if r["solvable"]:
        fails.append("4x4 single lit corner is unsolvable")
    for f in fails:
        print("FAIL", f)
    print("puzzle_solver selftest: %s" % ("FAILED" if fails else "ok"))
    return 1 if fails else 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--selftest" in argv:
        return selftest()
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--selftest", action="store_true")
    p.add_argument("--level", required=True, help="level-spec JSON")
    p.add_argument("--algo", choices=("bfs", "astar"), default="bfs")
    p.add_argument("--max-nodes", type=int, default=2_000_000)
    p.add_argument("--json", action="store_true")
    a = p.parse_args(argv)
    try:
        try:
            spec = json.loads(Path(a.level).read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            raise InputError("cannot read %s: %s" % (a.level, e))
        if a.max_nodes < 1:
            raise InputError("--max-nodes must be >= 1")
        res = solve_spec(spec, a.algo, a.max_nodes)
    except InputError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    ok = res["solvable"] and res["within_limit"] is not False
    if a.json:
        print(json.dumps(res, indent=2))
    else:
        print("%s [%s] %s  min_moves=%s  nodes=%d  within_limit=%s" % (
            res["level_id"], res["type"], "SOLVABLE" if res["solvable"] else "NOT SOLVED", res["min_moves"],
            res["nodes"], res["within_limit"]))
        if res["reason"]:
            print("reason:", res["reason"])
        if res["path"]:
            print("path:", " ".join(res["path"][:60]) + (" ..." if len(res["path"]) > 60 else ""))
        print("signals:", json.dumps(res["signals"]))
    return 0 if ok else 1


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows pipes default to the ANSI code page; Claude Code reads UTF-8
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
