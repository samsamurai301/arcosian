#!/usr/bin/env python3
"""Seeded procedural generators with ASCII preview: wfc, bsp, cave, noise, poisson, maze.

  pcg.py wfc|bsp|cave|noise|poisson|maze --w W --h H [--seed S] [--json] [--out PATH]

Output is deterministic per (algorithm, w, h, seed, options) on every platform: all randomness comes from
the portable PCG32 in skills/procedural-generation/scripts/pcgkit.py (the same generator the engine ports use).
  wfc      wave function collapse over a 5-tile terrain set (water ~ sand , grass T forest ^ mountain), with
           adjacency rules between neighbouring tile ranks; restarts with a derived seed on contradiction
  bsp      binary space partition dungeon: rooms in leaves joined by L-shaped corridors
  cave     cellular automaton cave, keeping only the largest connected region (--fill, --steps)
  noise    fBm gradient (Perlin) noise normalised to 0..1, ASCII height ramp (--scale, --octaves)
  poisson  Bridson Poisson-disc points with minimum distance --radius (default min(w,h)/8)
  maze     perfect maze (recursive backtracker); even sizes get a wall row/column on the far side
Each result carries `checks` (e.g. connected, adjacency_ok, min_distance_ok). --json prints the full result,
--out writes it to PATH. Exit 0 ok, 1 a check failed (try another seed), 2 usage/input error.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from collections import deque
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Set, Tuple

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


class Rng:
    def __init__(self, seed: int) -> None:
        self.g = PCG32(seed)

    def below(self, n: int) -> int:
        return self.g.bounded(n)

    def between(self, lo: int, hi: int) -> int:  # inclusive
        return lo + self.g.bounded(hi - lo + 1)

    def unit(self) -> float:
        return self.g.next_u32() / 4294967296.0

    def shuffle(self, xs: List[Any]) -> None:
        for i in range(len(xs) - 1, 0, -1):
            j = self.g.bounded(i + 1)
            xs[i], xs[j] = xs[j], xs[i]


def sub_seed(seed: int, attempt: int) -> int:
    return seed if attempt == 0 else mix64(seed * 0x9E3779B97F4A7C15 + attempt) & 0xFFFFFFFF


def flood(grid: List[List[str]], start: Tuple[int, int], open_ch: str = ".") -> Set[Tuple[int, int]]:
    H, W = len(grid), len(grid[0])
    seen, q = {start}, deque([start])
    while q:
        r, c = q.popleft()
        for n in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
            if 0 <= n[0] < H and 0 <= n[1] < W and n not in seen and grid[n[0]][n[1]] == open_ch:
                seen.add(n)
                q.append(n)
    return seen


def floors(grid: List[List[str]]) -> List[Tuple[int, int]]:
    return [(r, c) for r, row in enumerate(grid) for c, ch in enumerate(row) if ch == "."]


def result(algo: str, W: int, H: int, seed: int, grid: List[List[str]], checks: Dict[str, bool],
           stats: Dict[str, Any], legend: Dict[str, str], **extra: Any) -> Dict[str, Any]:
    d: Dict[str, Any] = {"algo": algo, "w": W, "h": H, "seed": seed, "legend": legend, "grid": ["".join(r) for r in grid],
                         "stats": stats, "checks": checks, "ok": all(checks.values())}
    d.update(extra)
    return d


# ---------------------------------------------------------------- maze

def gen_maze(W: int, H: int, seed: int, **_: Any) -> Dict[str, Any]:
    if W < 5 or H < 5:
        raise InputError("maze needs w, h >= 5")
    rng = Rng(seed)
    cw, ch = (W - 1) // 2, (H - 1) // 2
    grid = [["#"] * W for _ in range(H)]
    start = (rng.below(ch), rng.below(cw))
    seen, stack, edges = {start}, [start], 0
    grid[2 * start[0] + 1][2 * start[1] + 1] = "."
    while stack:
        r, c = stack[-1]
        opts = [n for n in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1))
                if 0 <= n[0] < ch and 0 <= n[1] < cw and n not in seen]
        if not opts:
            stack.pop()
            continue
        n = opts[rng.below(len(opts))]
        grid[r + n[0] + 1][c + n[1] + 1] = "."
        grid[2 * n[0] + 1][2 * n[1] + 1] = "."
        seen.add(n)
        stack.append(n)
        edges += 1
    fl = floors(grid)
    dead = sum(1 for r, c in fl if sum(grid[a][b] == "." for a, b in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1))) == 1)
    # longest shortest path (tree diameter) by two BFS passes
    def far(src: Tuple[int, int]) -> Tuple[Tuple[int, int], int]:
        dist, q, last = {src: 0}, deque([src]), src
        while q:
            last = q.popleft()
            for n in ((last[0] - 1, last[1]), (last[0] + 1, last[1]), (last[0], last[1] - 1), (last[0], last[1] + 1)):
                if n not in dist and 0 <= n[0] < H and 0 <= n[1] < W and grid[n[0]][n[1]] == ".":
                    dist[n] = dist[last] + 1
                    q.append(n)
        return last, dist[last]
    a, _ = far(fl[0])
    b, diam = far(a)
    checks = {"connected": len(flood(grid, fl[0])) == len(fl), "perfect_tree": edges == cw * ch - 1}
    return result("maze", W, H, seed, grid, checks, {"cells": cw * ch, "dead_ends": dead, "longest_path": diam},
                  {"#": "wall", ".": "floor"}, entrance=list(a), exit=list(b))


# ---------------------------------------------------------------- cave

def gen_cave(W: int, H: int, seed: int, fill: float = 0.45, steps: int = 4, **_: Any) -> Dict[str, Any]:
    if W < 8 or H < 8:
        raise InputError("cave needs w, h >= 8")
    if not 0.2 <= fill <= 0.7:
        raise InputError("--fill must be 0.2..0.7")
    for attempt in range(10):
        rng = Rng(sub_seed(seed, attempt))
        g = [["#" if r in (0, H - 1) or c in (0, W - 1) or rng.unit() < fill else "." for c in range(W)] for r in range(H)]
        for _ in range(steps):
            n = [row[:] for row in g]
            for r in range(H):
                for c in range(W):
                    walls = sum(1 for dr in (-1, 0, 1) for dc in (-1, 0, 1) if (dr or dc) and
                                (not (0 <= r + dr < H and 0 <= c + dc < W) or g[r + dr][c + dc] == "#"))
                    n[r][c] = "#" if walls >= 5 or r in (0, H - 1) or c in (0, W - 1) else "."
            g = n
        regions, left = [], set(floors(g))
        while left:
            reg = flood(g, next(iter(left)))
            regions.append(reg)
            left -= reg
        if not regions:
            continue
        big = max(regions, key=len)
        for reg in regions:
            if reg is not big:
                for r, c in reg:
                    g[r][c] = "#"
        pct = len(big) / (W * H)
        if pct >= 0.15:
            return result("cave", W, H, seed, g, {"connected": True, "floor_ratio_ok": pct >= 0.15},
                          {"floor_ratio": round(pct, 3), "regions_filled": len(regions) - 1, "attempt": attempt},
                          {"#": "wall", ".": "floor"})
    return result("cave", W, H, seed, [["#"] * W for _ in range(H)], {"connected": False, "floor_ratio_ok": False},
                  {"floor_ratio": 0.0}, {"#": "wall", ".": "floor"})


# ---------------------------------------------------------------- bsp

def gen_bsp(W: int, H: int, seed: int, min_room: int = 4, **_: Any) -> Dict[str, Any]:
    if W < 16 or H < 16:
        raise InputError("bsp needs w, h >= 16")
    rng = Rng(seed)
    grid = [["#"] * W for _ in range(H)]
    leaf_min = min_room + 3
    rooms: List[Tuple[int, int, int, int]] = []

    def split(x: int, y: int, w: int, h: int) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        horiz = h > w if abs(h - w) > 3 else rng.below(2) == 0
        if (w if not horiz else h) < 2 * leaf_min:
            horiz = not horiz
            if (w if not horiz else h) < 2 * leaf_min:
                carve_room(x, y, w, h)
                return room_center(rooms[-1])
        if horiz:
            cut = rng.between(leaf_min, h - leaf_min)
            a, b = split(x, y, w, cut), split(x, y + cut, w, h - cut)
        else:
            cut = rng.between(leaf_min, w - leaf_min)
            a, b = split(x, y, cut, h), split(x + cut, y, w - cut, h)
        corridor(a, b)  # type: ignore[arg-type]
        return a if rng.below(2) else b

    def carve_room(x: int, y: int, w: int, h: int) -> None:
        rw, rh = rng.between(min_room, w - 2), rng.between(min_room, h - 2)
        rx, ry = x + rng.between(1, w - rw - 1), y + rng.between(1, h - rh - 1)
        rooms.append((rx, ry, rw, rh))
        for r in range(ry, ry + rh):
            for c in range(rx, rx + rw):
                grid[r][c] = "."

    def room_center(rm: Tuple[int, int, int, int]) -> Tuple[int, int]:
        return rm[1] + rm[3] // 2, rm[0] + rm[2] // 2

    def corridor(a: Tuple[int, int], b: Tuple[int, int]) -> None:
        (r1, c1), (r2, c2) = a, b
        for c in range(min(c1, c2), max(c1, c2) + 1):
            grid[r1][c] = "."
        for r in range(min(r1, r2), max(r1, r2) + 1):
            grid[r][c2] = "."

    split(1, 1, W - 2, H - 2)
    fl = floors(grid)
    overlap = sum(1 for i, a in enumerate(rooms) for b in rooms[i + 1:]
                  if a[0] < b[0] + b[2] and b[0] < a[0] + a[2] and a[1] < b[1] + b[3] and b[1] < a[1] + a[3])
    checks = {"connected": len(flood(grid, fl[0])) == len(fl), "rooms_disjoint": overlap == 0}
    return result("bsp", W, H, seed, grid, checks, {"rooms": len(rooms), "floor_ratio": round(len(fl) / (W * H), 3)},
                  {"#": "wall", ".": "floor"}, rooms=[{"x": r[0], "y": r[1], "w": r[2], "h": r[3]} for r in rooms])


# ---------------------------------------------------------------- noise

RAMP = " .:-=+*#%@"


def gen_noise(W: int, H: int, seed: int, scale: float = 8.0, octaves: int = 4, **_: Any) -> Dict[str, Any]:
    if scale <= 0 or not 1 <= octaves <= 8:
        raise InputError("--scale must be > 0 and --octaves 1..8")
    rng = Rng(seed)
    perm = list(range(256))
    rng.shuffle(perm)
    perm += perm
    grads = [(math.cos(i * math.pi / 8), math.sin(i * math.pi / 8)) for i in range(16)]

    def fade(t: float) -> float:
        return t * t * t * (t * (t * 6 - 15) + 10)

    def perlin(x: float, y: float) -> float:
        x0, y0 = math.floor(x), math.floor(y)
        fx, fy = x - x0, y - y0
        xi, yi = x0 & 255, y0 & 255

        def dot(ix: int, iy: int, dx: float, dy: float) -> float:
            g = grads[perm[perm[(xi + ix) & 255] + ((yi + iy) & 255)] & 15]
            return g[0] * dx + g[1] * dy
        u, v = fade(fx), fade(fy)
        a = dot(0, 0, fx, fy) + u * (dot(1, 0, fx - 1, fy) - dot(0, 0, fx, fy))
        b = dot(0, 1, fx, fy - 1) + u * (dot(1, 1, fx - 1, fy - 1) - dot(0, 1, fx, fy - 1))
        return a + v * (b - a)

    raw = []
    for r in range(H):
        row = []
        for c in range(W):
            amp, freq, tot, norm = 1.0, 1.0 / scale, 0.0, 0.0
            for o in range(octaves):
                tot += amp * perlin(c * freq + 17.3 * o, r * freq + 31.7 * o)
                norm += amp
                amp, freq = amp * 0.5, freq * 2
            row.append(tot / norm)
        raw.append(row)
    lo, hi = min(map(min, raw)), max(map(max, raw))
    vals = [[(v - lo) / (hi - lo) if hi > lo else 0.5 for v in row] for row in raw]
    grid = [[RAMP[min(len(RAMP) - 1, int(v * len(RAMP)))] for v in row] for row in vals]
    flat = [v for row in vals for v in row]
    checks = {"range_0_1": min(flat) >= 0.0 and max(flat) <= 1.0, "has_variation": hi - lo > 1e-6}
    return result("noise", W, H, seed, grid, checks, {"mean": round(sum(flat) / len(flat), 3), "scale": scale, "octaves": octaves},
                  {ch: "height %.1f-%.1f" % (i / len(RAMP), (i + 1) / len(RAMP)) for i, ch in enumerate(RAMP)},
                  values=[[round(v, 3) for v in row] for row in vals])


# ---------------------------------------------------------------- poisson

def gen_poisson(W: int, H: int, seed: int, radius: Optional[float] = None, k: int = 30, **_: Any) -> Dict[str, Any]:
    r = radius if radius else max(2.0, min(W, H) / 8.0)
    if r <= 0 or r > min(W, H):
        raise InputError("--radius must be in (0, min(w,h)]")
    rng = Rng(seed)
    cell = r / math.sqrt(2)
    gw, gh = int(math.ceil(W / cell)), int(math.ceil(H / cell))
    grid: List[List[int]] = [[-1] * gw for _ in range(gh)]
    pts: List[Tuple[float, float]] = []

    def fits(x: float, y: float) -> bool:
        cx, cy = int(x / cell), int(y / cell)
        for j in range(max(0, cy - 2), min(gh, cy + 3)):
            for i in range(max(0, cx - 2), min(gw, cx + 3)):
                n = grid[j][i]
                if n >= 0 and (pts[n][0] - x) ** 2 + (pts[n][1] - y) ** 2 < r * r:
                    return False
        return True

    def add(x: float, y: float) -> None:
        grid[int(y / cell)][int(x / cell)] = len(pts)
        pts.append((x, y))
        active.append(len(pts) - 1)

    active: List[int] = []
    add(rng.unit() * W, rng.unit() * H)
    while active:
        i = rng.below(len(active))
        px, py = pts[active[i]]
        for _ in range(k):
            ang, dist = rng.unit() * 2 * math.pi, r * (1 + rng.unit())
            x, y = px + dist * math.cos(ang), py + dist * math.sin(ang)
            if 0 <= x < W and 0 <= y < H and fits(x, y):
                add(x, y)
                break
        else:
            active.pop(i)
    mind = min((math.hypot(a[0] - b[0], a[1] - b[1]) for i, a in enumerate(pts) for b in pts[i + 1:]), default=r)
    ascii_g = [["."] * W for _ in range(H)]
    for x, y in pts:
        ascii_g[int(y)][int(x)] = "o"
    checks = {"min_distance_ok": mind >= r - 1e-9, "in_bounds": all(0 <= x < W and 0 <= y < H for x, y in pts)}
    return result("poisson", W, H, seed, ascii_g, checks, {"points": len(pts), "radius": round(r, 3),
                  "min_distance": round(mind, 3), "density_per_100_cells": round(100 * len(pts) / (W * H), 2)},
                  {".": "empty", "o": "point (cell containing a sample)"},
                  points=[[round(x, 3), round(y, 3)] for x, y in pts])


# ---------------------------------------------------------------- wfc

TILES = "~,.T^"  # water, sand, grass, forest, mountain
WEIGHTS = [2, 1, 4, 3, 1]
ALLOWED = {(a, b) for a in range(5) for b in range(5) if abs(a - b) <= 1}


def gen_wfc(W: int, H: int, seed: int, **_: Any) -> Dict[str, Any]:
    if W < 3 or H < 3:
        raise InputError("wfc needs w, h >= 3")
    full = (1 << 5) - 1
    compat = [sum(1 << b for b in range(5) if (a, b) in ALLOWED) for a in range(5)]
    for attempt in range(60):
        rng = Rng(sub_seed(seed, attempt))
        cells = [full] * (W * H)

        def options(m: int) -> List[int]:
            return [i for i in range(5) if m >> i & 1]

        def propagate(start: int) -> bool:
            stack = [start]
            while stack:
                p = stack.pop()
                allow = 0
                for t in options(cells[p]):
                    allow |= compat[t]
                r, c = divmod(p, W)
                for n in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
                    if 0 <= n[0] < H and 0 <= n[1] < W:
                        q = n[0] * W + n[1]
                        new = cells[q] & allow
                        if new != cells[q]:
                            if not new:
                                return False
                            cells[q] = new
                            stack.append(q)
            return True

        ok = True
        while True:
            open_cells = [(bin(m).count("1"), rng.unit(), i) for i, m in enumerate(cells) if bin(m).count("1") > 1]
            if not open_cells:
                break
            _, _, p = min(open_cells)
            opts = options(cells[p])
            pick = rng.unit() * sum(WEIGHTS[t] for t in opts)
            for t in opts:
                pick -= WEIGHTS[t]
                if pick <= 0:
                    break
            cells[p] = 1 << t
            if not propagate(p):
                ok = False
                break
        if ok:
            idx = [cells[i].bit_length() - 1 for i in range(W * H)]
            g = [[TILES[idx[r * W + c]] for c in range(W)] for r in range(H)]
            bad = sum(1 for r in range(H) for c in range(W) for n in ((r, c + 1), (r + 1, c))
                      if n[0] < H and n[1] < W and (idx[r * W + c], idx[n[0] * W + n[1]]) not in ALLOWED)
            counts = {TILES[i]: idx.count(i) for i in range(5)}
            return result("wfc", W, H, seed, g, {"adjacency_ok": bad == 0, "no_contradiction": True},
                          {"restarts": attempt, "tile_counts": counts},
                          {"~": "water", ",": "sand", ".": "grass", "T": "forest", "^": "mountain"})
    return result("wfc", W, H, seed, [["?"] * W for _ in range(H)], {"adjacency_ok": False, "no_contradiction": False},
                  {"restarts": 60}, {})


GENS: Dict[str, Callable[..., Dict[str, Any]]] = {"wfc": gen_wfc, "bsp": gen_bsp, "cave": gen_cave,
                                                    "noise": gen_noise, "poisson": gen_poisson, "maze": gen_maze}


def selftest() -> int:
    fails: List[str] = []
    sizes = {"wfc": (24, 12), "bsp": (48, 28), "cave": (40, 22), "noise": (30, 14), "poisson": (50, 30), "maze": (31, 21)}
    for name, (w, h) in sizes.items():
        for seed in (1, 2, 3, 42):
            r = GENS[name](w, h, seed)
            if not r["ok"]:
                fails.append("%s seed %d failed checks %s" % (name, seed, r["checks"]))
            if len(r["grid"]) != h or any(len(row) != w for row in r["grid"]):
                fails.append("%s wrong grid size" % name)
        a, b, c = GENS[name](w, h, 7), GENS[name](w, h, 7), GENS[name](w, h, 8)
        if a != b:
            fails.append("%s not deterministic" % name)
        if a["grid"] == c["grid"]:
            fails.append("%s ignores the seed" % name)
    m = gen_maze(21, 21, 5)
    if m["stats"]["cells"] != 100 or not m["checks"]["perfect_tree"]:
        fails.append("maze cell count %s" % m["stats"])
    p = gen_poisson(60, 40, 3, radius=5.0)
    if p["stats"]["points"] < 60 or p["stats"]["min_distance"] < 5.0:
        fails.append("poisson density/min distance %s" % p["stats"])
    if gen_wfc(10, 10, 4)["stats"]["restarts"] > 59:
        fails.append("wfc did not converge")
    for bad, args in (("maze", (3, 3)), ("cave", (4, 4)), ("bsp", (8, 8))):
        try:
            GENS[bad](*args, 1)
            fails.append("%s accepted a tiny size" % bad)
        except InputError:
            pass
    for f in fails:
        print("FAIL", f)
    print("pcg selftest: %s" % ("FAILED" if fails else "ok"))
    return 1 if fails else 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--selftest" in argv:
        return selftest()
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--selftest", action="store_true")
    sub = p.add_subparsers(dest="algo")
    for name in GENS:
        s = sub.add_parser(name)
        s.add_argument("--w", type=int, required=True)
        s.add_argument("--h", type=int, required=True)
        s.add_argument("--seed", type=int, default=1)
        s.add_argument("--json", action="store_true")
        s.add_argument("--out")
        if name == "cave":
            s.add_argument("--fill", type=float, default=0.45)
            s.add_argument("--steps", type=int, default=4)
        if name == "noise":
            s.add_argument("--scale", type=float, default=8.0)
            s.add_argument("--octaves", type=int, default=4)
        if name == "poisson":
            s.add_argument("--radius", type=float)
        if name == "bsp":
            s.add_argument("--min-room", type=int, default=4, dest="min_room")
    a = p.parse_args(argv)
    if not a.algo:
        p.print_usage(sys.stderr)
        return 2
    try:
        if not (3 <= a.w <= 300 and 3 <= a.h <= 300):
            raise InputError("--w and --h must be 3..300")
        opts = {k: v for k, v in vars(a).items() if k in ("fill", "steps", "scale", "octaves", "radius", "min_room")}
        res = GENS[a.algo](a.w, a.h, a.seed, **opts)
    except InputError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    if a.out:
        Path(a.out).parent.mkdir(parents=True, exist_ok=True)
        Path(a.out).write_text(json.dumps(res, indent=2) + "\n", encoding="utf-8")
    if a.json:
        print(json.dumps(res, indent=2))
    else:
        print("\n".join(res["grid"]))
        print("%s seed=%d stats=%s checks=%s" % (res["algo"], res["seed"], json.dumps(res["stats"]), json.dumps(res["checks"])))
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows pipes default to the ANSI code page; Claude Code reads UTF-8
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
