#!/usr/bin/env python3
"""Match-3 level simulator: real engine plus bots, to estimate win rate and difficulty band.

  match3_sim.py --level PATH [--runs N=500] [--bot greedy|random|cascade] [--seed S] [--json]

PATH is a level-spec JSON with layout.type "match3" (width/height, rows or grid, colors, legend).
Layout codes: '.' random tile, '#' hole, '0'-'7' fixed colour, legend letters for obstacles:
"box ... (N hp)" blocks a cell and is hit by adjacent clears; "ice ... (N hp)" sits under a tile and is hit
when that cell is cleared. `obstacles` objects {"type":"ice|box","cells":[[r,c]],"hp":n} work too.
Goals: collect (target = colour index, count), clear (target = "box"|"ice", count optional = all), score.
Engine: swap two adjacent tiles, valid only if it matches 3+ (or involves a colour bomb / two specials);
runs of 3+ clear; cascades with gravity and seeded refill (spawns above each column segment);
specials: 4-run = line clearer (horizontal run clears its column, vertical its row), L/T = 3x3 bomb,
5-run = colour bomb (clears the colour it is swapped with, or its own when matched). 10 points per tile.
Bots: random (any valid move), greedy (best immediate clear, goal-weighted), cascade (greedy top 5, then
a rollout of each with an unseen random refill). Each run uses a fresh random fill for '.' cells.
Exit 0 ok, 1 selftest failure or the bot never won (check the level), 2 usage/input error.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

HERE = Path(__file__).resolve().parent


def _load(rel: str, name: str):
    spec = importlib.util.spec_from_file_location(name, str(HERE.parent / rel))
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    sys.modules[name] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


_pk = _load("skills/procedural-generation/scripts/pcgkit.py", "pcgkit_mod")
PCG32, mix64 = _pk.PCG32, _pk.mix64


class InputError(Exception):
    pass


BOX, HOLE, EMPTY, PAD = -3, -1, -2, -9
LINE_ROW, LINE_COL, BOMB, CBOMB = 1, 2, 3, 4


class Board:
    """Flat padded board (2 cells of PAD around) so neighbour tests need no bounds checks."""

    def __init__(self, W: int, H: int, ncol: int) -> None:
        self.W, self.H, self.S, self.ncol = W, H, W + 4, ncol
        n = self.S * (H + 4)
        self.t, self.sp, self.ice, self.bhp = [PAD] * n, [0] * n, [0] * n, [0] * n
        self.cells = [(r + 2) * self.S + c + 2 for r in range(H) for c in range(W)]

    def clone(self) -> "Board":
        b = Board.__new__(Board)
        b.W, b.H, b.S, b.ncol, b.cells = self.W, self.H, self.S, self.ncol, self.cells
        b.t, b.sp, b.ice, b.bhp = self.t[:], self.sp[:], self.ice[:], self.bhp[:]
        return b

    def idx(self, r: int, c: int) -> int:
        return (r + 2) * self.S + c + 2

    def match_at(self, p: int) -> bool:
        t, S = self.t, self.S
        c = t[p]
        if c < 0:
            return False
        return bool((t[p - 1] == c and (t[p - 2] == c or t[p + 1] == c)) or (t[p + 1] == c and t[p + 2] == c)
                    or (t[p - S] == c and (t[p - 2 * S] == c or t[p + S] == c)) or (t[p + S] == c and t[p + 2 * S] == c))

    def moves(self) -> List[Tuple[int, int]]:
        out, t, sp, S = [], self.t, self.sp, self.S
        for p in self.cells:
            if t[p] < 0:
                continue
            for q in (p + 1, p + S):
                if t[q] < 0:
                    continue
                if sp[p] == CBOMB or sp[q] == CBOMB or (sp[p] and sp[q]):
                    out.append((p, q))
                elif t[p] != t[q]:
                    t[p], t[q] = t[q], t[p]
                    if self.match_at(p) or self.match_at(q):
                        out.append((p, q))
                    t[p], t[q] = t[q], t[p]
        return out

    def runs(self) -> List[Tuple[List[int], str]]:
        out, t, S = [], self.t, self.S
        for step, d in ((1, "h"), (S, "v")):
            for p in self.cells:
                c = t[p]
                if c >= 0 and t[p - step] != c and t[p + step] == c and t[p + 2 * step] == c:
                    run, q = [p], p + step
                    while t[q] == c:
                        run.append(q)
                        q += step
                    out.append((run, d))
        return out

    def settle(self, rng: Any) -> None:
        t, sp = self.t, self.sp
        for c in range(self.W):
            r = self.H - 1
            while r >= 0:
                if t[self.idx(r, c)] in (HOLE, BOX):
                    r -= 1
                    continue
                top = r
                while top >= 0 and t[self.idx(top, c)] not in (HOLE, BOX):
                    top -= 1
                keep = [(t[self.idx(k, c)], sp[self.idx(k, c)]) for k in range(r, top, -1) if t[self.idx(k, c)] >= 0]
                for n, k in enumerate(range(r, top, -1)):
                    p = self.idx(k, c)
                    if n < len(keep):
                        t[p], sp[p] = keep[n]
                    else:
                        t[p], sp[p] = rng.bounded(self.ncol), 0
                r = top

    def area(self, x: int, colour: Optional[int]) -> Set[int]:
        typ, S = self.sp[x], self.S
        if typ == LINE_ROW:
            return {self.idx(x // S - 2, c) for c in range(self.W)}
        if typ == LINE_COL:
            return {self.idx(r, x % S - 2) for r in range(self.H)}
        if typ == BOMB:
            return {x + dr * S + dc for dr in (-1, 0, 1) for dc in (-1, 0, 1)}
        col = self.t[x] if colour is None else colour
        return {p for p in self.cells if self.t[p] == col or p == x}

    def play(self, a: int, b: int, rng: Any, st: Dict[str, Any]) -> None:
        t, sp = self.t, self.sp
        t[a], t[b] = t[b], t[a]
        sp[a], sp[b] = sp[b], sp[a]
        trig: List[Tuple[int, Optional[int]]] = []
        if sp[a] == CBOMB or sp[b] == CBOMB or (sp[a] and sp[b]):
            for x, y in ((a, b), (b, a)):
                if sp[x]:
                    trig.append((x, t[y] if sp[x] == CBOMB else None))
        swapped = {a, b}
        for _ in range(60):
            runs = self.runs()
            if not runs and not trig:
                break
            clear: Set[int] = set()
            spawn: Dict[int, int] = {}
            groups: List[List[Tuple[List[int], str]]] = []
            for run in runs:  # merge runs that share a cell
                hit = [g for g in groups if any(set(run[0]) & set(r[0]) for r in g)]
                merged = [run] + [r for g in hit for r in g]
                groups = [g for g in groups if g not in hit] + [merged]
            for g in groups:
                cells = {p for r, _ in g for p in r}
                hset = {p for r, d in g if d == "h" for p in r}
                vset = {p for r, d in g if d == "v" for p in r}
                longest = max(g, key=lambda r: len(r[0]))
                typ, pos = 0, None
                if len(longest[0]) >= 5:
                    typ = CBOMB
                elif hset & vset:
                    typ, pos = BOMB, min(hset & vset)
                elif len(longest[0]) == 4:
                    typ = LINE_COL if longest[1] == "h" else LINE_ROW
                if typ:
                    if pos is None:
                        sw = [p for p in longest[0] if p in swapped]
                        pos = sw[0] if sw else longest[0][len(longest[0]) // 2]
                    spawn[pos] = typ
                    st["specials"][typ] = st["specials"].get(typ, 0) + 1
                clear |= cells
            for pos in spawn:
                if sp[pos]:
                    trig.append((pos, None))  # a matched special fires before being replaced
            clear -= set(spawn)
            seen: Set[int] = set()
            queue = list(trig) + [(x, None) for x in clear if sp[x]]
            clear |= {x for x, _ in trig if x not in spawn}
            while queue:
                x, col = queue.pop()
                if x in seen:
                    continue
                seen.add(x)
                for y in self.area(x, col):
                    if t[y] >= 0 or t[y] == BOX:
                        if y not in spawn:
                            clear.add(y)
                        if t[y] >= 0 and sp[y] and y not in seen and y not in spawn:
                            queue.append((y, None))
            S = self.S
            boxhit = {y for y in clear if t[y] == BOX}
            for y in clear:
                if t[y] >= 0:
                    boxhit |= {n for n in (y - 1, y + 1, y - S, y + S) if t[n] == BOX}
            tiles = 0
            for y in clear | set(spawn):
                if t[y] >= 0 and self.ice[y]:
                    self.ice[y] -= 1
                    st["ice"] += 0 if self.ice[y] else 1
            for y in clear:
                if t[y] >= 0:
                    st["col"][t[y]] = st["col"].get(t[y], 0) + 1
                    tiles += 1
                    t[y], sp[y] = EMPTY, 0
            for y in boxhit:
                self.bhp[y] -= 1
                if self.bhp[y] <= 0:
                    t[y] = EMPTY
                    st["box"] += 1
            for pos, typ in spawn.items():
                sp[pos] = typ
            st["score"] += 10 * tiles
            st["steps"] += 1
            self.settle(rng)
            trig, swapped = [], set()

    def reshuffle(self, rng: Any) -> None:
        pos = [p for p in self.cells if self.t[p] >= 0]
        items = [(self.t[p], self.sp[p]) for p in pos]
        for _ in range(100):
            for i in range(len(items) - 1, 0, -1):
                j = rng.bounded(i + 1)
                items[i], items[j] = items[j], items[i]
            for p, (c, s) in zip(pos, items):
                self.t[p], self.sp[p] = c, s
            if not self.runs() and self.moves():
                return


def fresh_stats() -> Dict[str, Any]:
    return {"col": {}, "box": 0, "ice": 0, "score": 0, "steps": 0, "specials": {}}


class Level:
    def __init__(self, spec: Dict[str, Any]) -> None:
        lay = spec.get("layout")
        if not isinstance(lay, dict) or lay.get("type") != "match3":
            raise InputError("layout.type must be match3")
        rows = lay.get("rows")
        if rows is None and lay.get("grid") is not None:
            rows = ["".join(str(x) for x in r) for r in lay["grid"]]
        if rows is None:
            if not (lay.get("width") and lay.get("height")):
                raise InputError("match3 layout needs rows, grid or width+height")
            rows = ["." * int(lay["width"]) for _ in range(int(lay["height"]))]
        if len({len(r) for r in rows}) != 1:
            raise InputError("match3 rows must all have the same length")
        self.rows, self.H, self.W = rows, len(rows), len(rows[0])
        self.ncol = int(lay.get("colors", 5))
        if not 3 <= self.ncol <= 8:
            raise InputError("colors must be 3..8")
        self.legend: Dict[str, Tuple[str, int]] = {}
        for k, v in (lay.get("legend") or {}).items():
            low = str(v).lower()
            m = re.search(r"(\d+)\s*hp", low)
            hp = int(m.group(1)) if m else 1
            kind = "box" if re.search(r"box|crate|block", low) else "ice" if re.search(r"ice|jelly", low) else ""
            if kind:
                self.legend[k] = (kind, hp)
        self.extra = [o for o in spec.get("obstacles", []) if isinstance(o, dict) and o.get("type") in ("ice", "box")]
        lim = spec.get("moves_or_time_limit")
        lim = lim.get("moves") if isinstance(lim, dict) else lim
        self.moves = int(lim) if isinstance(lim, int) and lim > 0 else 20
        self.limit_defaulted = not (isinstance(lim, int) and lim > 0)
        self.target = (spec.get("difficulty_target") or {}).get("win_rate")
        probe = self.new_board(PCG32(1))
        n_box = sum(1 for p in probe.cells if probe.t[p] == BOX)
        n_ice = sum(1 for p in probe.cells if probe.ice[p])
        self.goals: List[Dict[str, Any]] = []
        for g in spec.get("goals", []):
            if not isinstance(g, dict):
                raise InputError("goals must be objects: collect, clear or score")
            kind, tgt = g.get("type"), str(g.get("target") or "").lower()
            cnt = g.get("count") or 0
            if kind in ("collect", "clear") and tgt in ("box", "ice"):
                self.goals.append({"k": tgt, "n": int(cnt) or (n_box if tgt == "box" else n_ice)})
            elif kind == "collect":
                m = re.search(r"\d+", tgt)
                if not m or int(m.group()) >= self.ncol or not cnt:
                    raise InputError("collect needs target = colour index < colors and a count")
                self.goals.append({"k": "col", "c": int(m.group()), "n": int(cnt)})
            elif kind == "score" and cnt:
                self.goals.append({"k": "score", "n": int(cnt)})
            else:
                raise InputError("unsupported goal %r (use collect, clear box|ice, score)" % g)
        if not self.goals:
            raise InputError("level needs at least one goal")

    def new_board(self, rng: Any) -> Board:
        for _ in range(60):
            b = Board(self.W, self.H, self.ncol)
            rand: List[int] = []
            for r, line in enumerate(self.rows):
                for c, ch in enumerate(line):
                    p = b.idx(r, c)
                    if ch == "#":
                        b.t[p] = HOLE
                    elif ch == ".":
                        b.t[p] = EMPTY
                        rand.append(p)
                    elif ch.isdigit() and int(ch) < self.ncol:
                        b.t[p] = int(ch)
                    elif ch in self.legend:
                        kind, hp = self.legend[ch]
                        if kind == "box":
                            b.t[p], b.bhp[p] = BOX, hp
                        else:
                            b.t[p], b.ice[p] = EMPTY, hp
                            rand.append(p)
                    else:
                        raise InputError("unknown layout code %r (define it in layout.legend)" % ch)
            for o in self.extra:
                for r, c in o.get("cells", []):
                    p = b.idx(r, c)
                    if o["type"] == "box":
                        b.t[p], b.bhp[p] = BOX, int(o.get("hp", 1))
                    else:
                        b.ice[p] = int(o.get("hp", 1))
            S, t = b.S, b.t
            for p in sorted(set(rand) | {q for q in b.cells if t[q] == EMPTY}):
                ban = set()
                if t[p - 1] == t[p - 2] >= 0:
                    ban.add(t[p - 1])
                if t[p - S] == t[p - 2 * S] >= 0:
                    ban.add(t[p - S])
                opts = [c for c in range(self.ncol) if c not in ban]
                t[p] = opts[rng.bounded(len(opts))]
            if not b.runs() and b.moves():
                return b
        raise InputError("could not build a valid starting board from this layout")

    def won(self, st: Dict[str, Any]) -> bool:
        for g in self.goals:
            have = st["col"].get(g.get("c"), 0) if g["k"] == "col" else st["score"] if g["k"] == "score" else st[g["k"]]
            if have < g["n"]:
                return False
        return True


# ---------------------------------------------------------------- bots

def greedy_value(b: Board, p: int, q: int, need: Set[int]) -> float:
    """Value of swapping p,q (called with the swap applied): goal-weighted tiles in runs through p and q."""
    t, sp, S = b.t, b.sp, b.S
    cells: Set[int] = set()
    bonus = 0.0
    for x in (p, q):
        c = t[x]
        for step in (1, S):
            run = [x]
            for sgn in (-1, 1):
                y = x + sgn * step
                while t[y] == c >= 0:
                    run.append(y)
                    y += sgn * step
            if len(run) >= 3:
                cells |= set(run)
                bonus += {3: 0, 4: 3}.get(len(run), 6)
    if not cells:
        return 6.0 + (sp[p] == CBOMB or sp[q] == CBOMB) * 6.0  # special-only swap
    val = bonus + (4.0 if len({x // S for x in cells}) > 1 and len({x % S for x in cells}) > 1 else 0.0)
    for x in cells:
        val += 3.0 if t[x] in need else 1.0
        val += 3.0 * (b.ice[x] > 0) + 4.0 * (sp[x] > 0)
        val += 3.0 * sum(1 for n in (x - 1, x + 1, x - S, x + S) if t[n] == BOX)
    return val


def choose(bot: str, b: Board, level: Level, st: Dict[str, Any], rng: Any) -> Tuple[int, int]:
    mv = b.moves()
    if bot == "random":
        return mv[rng.bounded(len(mv))]
    need = {g["c"] for g in level.goals if g["k"] == "col" and st["col"].get(g["c"], 0) < g["n"]}
    scored = []
    for p, q in mv:
        b.t[p], b.t[q] = b.t[q], b.t[p]
        b.sp[p], b.sp[q] = b.sp[q], b.sp[p]
        scored.append((greedy_value(b, p, q, need), rng.bounded(1 << 16), (p, q)))
        b.t[p], b.t[q] = b.t[q], b.t[p]
        b.sp[p], b.sp[q] = b.sp[q], b.sp[p]
    scored.sort(reverse=True)
    if bot == "greedy":
        return scored[0][2]
    best, best_v = scored[0][2], -1.0
    for _, _, (p, q) in scored[:5]:  # rollout with an unseen refill
        c, s2 = b.clone(), fresh_stats()
        c.play(p, q, PCG32(rng.next_u32()), s2)
        v = sum(s2["col"].get(k, 0) * (3 if k in need else 1) for k in range(b.ncol)) + 5 * s2["steps"] + 4 * s2["box"] + 3 * s2["ice"]
        if v > best_v:
            best, best_v = (p, q), v
    return best


def run_once(level: Level, bot: str, seed: int) -> Dict[str, Any]:
    rng, brng = PCG32(seed), PCG32(seed ^ 0xA5A5A5A5)
    b, st = level.new_board(rng), fresh_stats()
    for used in range(1, level.moves + 1):
        if not b.moves():
            b.reshuffle(rng)
            if not b.moves():
                break
        a, c = choose(bot, b, level, st, brng)
        b.play(a, c, rng, st)
        if level.won(st):
            return {"win": True, "left": level.moves - used, "used": used, "st": st}
    return {"win": False, "left": 0, "used": level.moves, "st": st}


def simulate(level: Level, runs: int, bot: str, seed: int) -> Dict[str, Any]:
    res = [run_once(level, bot, mix64(seed * 0x9E3779B97F4A7C15 + r) & 0xFFFFFFFF) for r in range(runs)]
    wins = [r for r in res if r["win"]]
    w = len(wins) / runs
    hist: Dict[int, int] = {}
    for r in wins:
        hist[r["left"]] = hist.get(r["left"], 0) + 1
    lefts = sorted(r["left"] for r in wins)

    def pct(q: float) -> Optional[float]:
        return lefts[min(len(lefts) - 1, int(q * len(lefts)))] if lefts else None
    band = ("very easy" if w >= 0.85 else "easy" if w >= 0.65 else "medium" if w >= 0.45 else "hard" if w >= 0.25
            else "very hard" if w >= 0.1 else "brutal")
    spec_cnt: Dict[int, int] = {}
    for r in res:
        for k, v in r["st"]["specials"].items():
            spec_cnt[k] = spec_cnt.get(k, 0) + v
    names = {LINE_ROW: "line_row", LINE_COL: "line_col", BOMB: "bomb", CBOMB: "color_bomb"}
    p = 1 - w
    return {
        "bot": bot, "runs": runs, "seed": seed, "move_limit": level.moves,
        "win_rate": round(w, 4), "win_rate_ci95": [round(max(0, w - 1.96 * math.sqrt(w * p / runs)), 4),
                                                   round(min(1, w + 1.96 * math.sqrt(w * p / runs)), 4)],
        "moves_left": {"mean": round(sum(lefts) / len(lefts), 2) if lefts else None, "p10": pct(0.1), "p50": pct(0.5),
                       "p90": pct(0.9), "histogram": {str(k): hist[k] for k in sorted(hist)}},
        "avg_moves_used": round(sum(r["used"] for r in res) / runs, 2),
        "avg_score": round(sum(r["st"]["score"] for r in res) / runs, 1),
        "avg_cascade_steps_per_move": round(sum(r["st"]["steps"] for r in res) / max(1, sum(r["used"] for r in res)), 3),
        "specials_created_per_run": {names[k]: round(v / runs, 2) for k, v in sorted(spec_cnt.items())},
        "attempts_to_win": {"mean": round(1 / w, 2) if w else None,
                            "p50": math.ceil(math.log(0.5) / math.log(1 - w)) if 0 < w < 1 else (1 if w else None)},
        "difficulty_band": band, "target_win_rate": level.target,
        "target_gap": round(w - level.target, 4) if isinstance(level.target, (int, float)) else None,
        "notes": ["bot win rate is not human win rate: calibrate against playtests",
                  "no moves_or_time_limit found: assumed 20 moves"] if level.limit_defaulted else
                 ["bot win rate is not human win rate: calibrate against playtests"],
    }


# ---------------------------------------------------------------- selftest

def _board(rows: List[List[int]], ncol: int = 6) -> Board:
    b = Board(len(rows[0]), len(rows), ncol)
    for r, row in enumerate(rows):
        for c, v in enumerate(row):
            b.t[b.idx(r, c)] = v
    return b


def _pattern(W: int, H: int) -> List[List[int]]:
    return [[(r + c) % 5 for c in range(W)] for r in range(H)]


def selftest() -> int:
    fails: List[str] = []

    def play(b: Board, r1: int, c1: int, r2: int, c2: int, seed: int = 3) -> Dict[str, Any]:
        st = fresh_stats()
        b.play(b.idx(r1, c1), b.idx(r2, c2), PCG32(seed), st)
        return st

    g = _pattern(6, 6)
    b = _board(g)
    if b.runs() or b.moves():
        fails.append("diagonal pattern should have no runs and no moves")
    # 3-run: row 2 gets 4 4 4 after swapping a 4 down from row 1
    g = _pattern(6, 6)
    g[2][0] = g[2][1] = 4
    g[1][2], g[2][2] = 4, 0
    b = _board(g)
    if (b.idx(1, 2), b.idx(2, 2)) not in b.moves():
        fails.append("expected swap not listed as a valid move")
    c = b.clone()
    st = play(c, 1, 2, 2, 2)
    if st["col"].get(4, 0) < 3 or st["score"] < 30 or st["specials"]:
        fails.append("3-run: %s" % st)
    # 4-run -> line clearer; L -> bomb; 5-run -> colour bomb
    g = _pattern(7, 6)
    g[2][0] = g[2][1] = g[2][3] = 4
    g[1][2], g[2][2] = 4, 0
    st = play(_board(g), 1, 2, 2, 2)
    if st["specials"].get(LINE_COL) != 1:
        fails.append("4-run special: %s" % st["specials"])
    g = _pattern(7, 6)
    g[2][0] = g[2][1] = g[2][3] = g[2][4] = 4
    g[1][2], g[2][2] = 4, 0
    st = play(_board(g), 1, 2, 2, 2)
    if st["specials"].get(CBOMB) != 1:
        fails.append("5-run special: %s" % st["specials"])
    g = _pattern(7, 6)
    g[2][0] = g[2][1] = g[3][2] = g[4][2] = 4
    g[1][2], g[2][2] = 4, 0
    st = play(_board(g), 1, 2, 2, 2)
    if st["specials"].get(BOMB) != 1:
        fails.append("L-shape bomb: %s" % st["specials"])
    # determinism of seeded refill
    g = _pattern(6, 6)
    g[2][0] = g[2][1] = 4
    g[1][2], g[2][2] = 4, 0
    b1, b2 = _board(g), _board(g)
    play(b1, 1, 2, 2, 2, 9)
    play(b2, 1, 2, 2, 2, 9)
    if b1.t != b2.t:
        fails.append("same seed gave different boards")
    if b1.runs():
        fails.append("board left with unresolved runs")
    # box takes damage from an adjacent clear and is removed
    g = _pattern(6, 6)
    g[2][0] = g[2][1] = 4
    g[1][2], g[2][2] = 4, 0
    b = _board(g)
    b.t[b.idx(2, 3)], b.bhp[b.idx(2, 3)] = BOX, 1
    st = play(b, 1, 2, 2, 2)
    if st["box"] != 1:
        fails.append("box not cleared: %s" % st)
    # fast move generator agrees with brute force
    rng = PCG32(5)
    for _ in range(40):
        b = _board([[rng.bounded(4) for _ in range(7)] for _ in range(7)], 4)
        brute = []
        for p in b.cells:
            for q in (p + 1, p + b.S):
                if b.t[q] >= 0:
                    b.t[p], b.t[q] = b.t[q], b.t[p]
                    hit = {x for run, _ in b.runs() for x in run}
                    if p in hit or q in hit:
                        brute.append((p, q))
                    b.t[p], b.t[q] = b.t[q], b.t[p]
        if sorted(brute) != sorted(b.moves()) and not b.runs():
            fails.append("move generator mismatch")
            break
    # end to end
    easy = {"layout": {"type": "match3", "width": 7, "height": 7, "colors": 5}, "goals": [{"type": "score", "count": 100}],
            "moves_or_time_limit": 10}
    r = simulate(Level(easy), 20, "greedy", 1)
    if r["win_rate"] < 0.95:
        fails.append("easy level win rate %s" % r["win_rate"])
    hard = dict(easy, goals=[{"type": "score", "count": 100000}], moves_or_time_limit=3)
    if simulate(Level(hard), 10, "greedy", 1)["win_rate"] != 0:
        fails.append("impossible level was won")
    col = {"layout": {"type": "match3", "width": 7, "height": 7, "colors": 5}, "goals": [{"type": "collect", "target": "0", "count": 18}],
           "moves_or_time_limit": 12}
    rg, rr = simulate(Level(col), 60, "greedy", 2), simulate(Level(col), 60, "random", 2)
    if rg["win_rate"] <= rr["win_rate"]:
        fails.append("greedy (%s) should beat random (%s)" % (rg["win_rate"], rr["win_rate"]))
    if simulate(Level(col), 60, "greedy", 2) != rg:
        fails.append("simulation not reproducible")
    obs = {"layout": {"type": "match3", "rows": ["......", "......", "..B...", "..I...", "......", "......"], "colors": 5,
                      "legend": {"B": "box (1 hp)", "I": "ice (1 hp)"}},
           "goals": [{"type": "clear", "target": "box"}, {"type": "clear", "target": "ice"}], "moves_or_time_limit": 25}
    ro = simulate(Level(obs), 15, "cascade", 3)
    if ro["win_rate"] < 0.5:
        fails.append("obstacle level win rate %s" % ro["win_rate"])
    for f in fails:
        print("FAIL", f)
    print("match3_sim selftest: %s" % ("FAILED" if fails else "ok"))
    return 1 if fails else 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--selftest" in argv:
        return selftest()
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--selftest", action="store_true")
    p.add_argument("--level", required=True)
    p.add_argument("--runs", type=int, default=500)
    p.add_argument("--bot", choices=("greedy", "random", "cascade"), default="greedy")
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--json", action="store_true")
    a = p.parse_args(argv)
    try:
        if a.runs < 1:
            raise InputError("--runs must be >= 1")
        try:
            spec = json.loads(Path(a.level).read_text(encoding="utf-8"))
        except (OSError, ValueError) as e:
            raise InputError("cannot read %s: %s" % (a.level, e))
        res = simulate(Level(spec), a.runs, a.bot, a.seed)
    except InputError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    res["level_id"] = spec.get("level_id")
    if a.json:
        print(json.dumps(res, indent=2))
    else:
        print("%s: bot=%s runs=%d  win_rate=%.1f%% (95%% CI %s)  band=%s" % (
            res["level_id"], a.bot, a.runs, res["win_rate"] * 100, res["win_rate_ci95"], res["difficulty_band"]))
        print("moves left on wins: %s   attempts to win: %s   avg score: %s" % (
            res["moves_left"], res["attempts_to_win"], res["avg_score"]))
        for n in res["notes"]:
            print("note:", n)
    return 0 if res["win_rate"] > 0 else 1


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows pipes default to the ANSI code page; Claude Code reads UTF-8
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
