#!/usr/bin/env python3
"""pcgkit.py - determinism and evaluation helpers for procedural generation.

Companion to the plugin-level generator CLI (scripts/pcg.py). This tool does
not generate levels; it gives you the pieces around a generator:

  prng   Reference outputs of portable PRNGs (PCG32, SplitMix64, xorshift32,
         xorshift64*, xoshiro128**) so an engine port can be checked bit-for-bit.
  seed   Seed utilities: per-system stream derivation, daily/weekly seeds,
         human-shareable seed codes (Crockford base32, optional check symbol).
  era    Expressive range analysis over a batch of generated grid levels
         (or a CSV/JSONL of metric rows): metric summaries, 2D histogram,
         coverage, duplicates, and a keep-filter with acceptance rate.

Stdlib only, Python 3.9+. Exit codes: 0 ok, 1 check failed, 2 usage/input error.

Examples
  pcgkit.py prng --algo pcg32 --seed 42 --seq 54 --n 6
  pcgkit.py prng --algo splitmix64 --seed 1234567 --n 5 --json
  pcgkit.py prng --algo pcg32 --seed 7 --bound 6 --n 10      # unbiased dice
  pcgkit.py seed derive --root 123456789 --stream loot
  pcgkit.py seed daily --date 2026-10-19 --salt mygame-v1
  pcgkit.py seed encode --value 123456789 --check
  pcgkit.py seed decode --code 3nqk-8nu --check     # case- and O/0-forgiving
  pcgkit.py era --in out/levels/ --x linearity --y density --bins 8
  pcgkit.py era --in batch.json --keep "connectivity>=0.95,density<=0.55" --json
  pcgkit.py --selftest
"""
from __future__ import annotations

import argparse
import csv
import datetime as _dt
import hashlib
import json
import math
import statistics
import sys
from collections import deque
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional, Sequence, Tuple

M32 = 0xFFFFFFFF
M64 = 0xFFFFFFFFFFFFFFFF

# --------------------------------------------------------------------------
# PRNGs (all integer arithmetic, masked; outputs are identical on every platform)
# --------------------------------------------------------------------------


class PCG32:
    """PCG-XSH-RR 64/32 (O'Neill 2014), seeding as in the minimal C library."""

    MULT = 6364136223846793005

    def __init__(self, seed: int, seq: int = 0xDA3E39CB94B95BDB) -> None:
        self.state = 0
        self.inc = ((seq << 1) | 1) & M64
        self.next_u32()
        self.state = (self.state + (seed & M64)) & M64
        self.next_u32()

    def next_u32(self) -> int:
        old = self.state
        self.state = (old * self.MULT + self.inc) & M64
        xorshifted = (((old >> 18) ^ old) >> 27) & M32
        rot = old >> 59
        return ((xorshifted >> rot) | (xorshifted << ((-rot) & 31))) & M32

    def bounded(self, bound: int) -> int:
        return bounded_u32(self.next_u32, bound)


class SplitMix64:
    """SplitMix64 (Steele, Lea, Flood 2014); Vigna's public-domain C form."""

    GAMMA = 0x9E3779B97F4A7C15

    def __init__(self, seed: int) -> None:
        self.x = seed & M64

    def next_u64(self) -> int:
        self.x = (self.x + self.GAMMA) & M64
        return mix64(self.x)


def mix64(z: int) -> int:
    """SplitMix64 finalizer: a strong 64-bit integer hash (bijective)."""
    z &= M64
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & M64
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & M64
    return z ^ (z >> 31)


class Xorshift32:
    """Marsaglia (2003) xorshift32 with shifts (13, 17, 5). Seed must be non-zero."""

    def __init__(self, seed: int) -> None:
        self.x = (seed & M32) or 0x9E3779B9

    def next_u32(self) -> int:
        x = self.x
        x ^= (x << 13) & M32
        x ^= x >> 17
        x ^= (x << 5) & M32
        self.x = x & M32
        return self.x


class Xorshift64Star:
    """xorshift64* (Vigna 2014): shifts (12, 25, 27), multiplier 0x2545F4914F6CDD1D."""

    def __init__(self, seed: int) -> None:
        self.x = (seed & M64) or 0x9E3779B97F4A7C15

    def next_u64(self) -> int:
        x = self.x
        x ^= x >> 12
        x ^= (x << 25) & M64
        x ^= x >> 27
        self.x = x & M64
        return (self.x * 0x2545F4914F6CDD1D) & M64


def _rotl32(x: int, k: int) -> int:
    return ((x << k) | (x >> (32 - k))) & M32


class Xoshiro128SS:
    """xoshiro128** (Blackman & Vigna 2018). State seeded from SplitMix64(seed):
    two 64-bit outputs split low word first -> s0..s3 (pcgkit convention)."""

    def __init__(self, seed: int) -> None:
        sm = SplitMix64(seed)
        a, b = sm.next_u64(), sm.next_u64()
        self.s = [a & M32, a >> 32, b & M32, b >> 32]
        if not any(self.s):
            self.s[0] = 1

    def next_u32(self) -> int:
        s = self.s
        result = (_rotl32((s[1] * 5) & M32, 7) * 9) & M32
        t = (s[1] << 9) & M32
        s[2] ^= s[0]
        s[3] ^= s[1]
        s[1] ^= s[2]
        s[0] ^= s[3]
        s[2] ^= t
        s[3] = _rotl32(s[3], 11)
        return result


def bounded_u32(next_u32: Callable[[], int], bound: int) -> int:
    """Unbiased integer in [0, bound) by rejection (same method as PCG's
    pcg32_boundedrand_r). Port this exactly; never use `next() % bound` raw."""
    if bound <= 0 or bound > M32:
        raise ValueError("bound must be in 1..2^32-1")
    threshold = ((1 << 32) - bound) % bound
    while True:
        r = next_u32()
        if r >= threshold:
            return r % bound


ALGOS = ("pcg32", "splitmix64", "xorshift32", "xorshift64star", "xoshiro128ss")
WIDTH = {"pcg32": 32, "splitmix64": 64, "xorshift32": 32, "xorshift64star": 64, "xoshiro128ss": 32}


def make_rng(algo: str, seed: int, seq: Optional[int] = None) -> Tuple[Callable[[], int], int]:
    if algo == "pcg32":
        g = PCG32(seed, seq) if seq is not None else PCG32(seed)
        return g.next_u32, 32
    if algo == "splitmix64":
        return SplitMix64(seed).next_u64, 64
    if algo == "xorshift32":
        return Xorshift32(seed).next_u32, 32
    if algo == "xorshift64star":
        return Xorshift64Star(seed).next_u64, 64
    if algo == "xoshiro128ss":
        return Xoshiro128SS(seed).next_u32, 32
    raise ValueError("unknown algo %r" % algo)


def to_unit_float(value: int, width: int) -> float:
    """Map an integer output to [0, 1). 64-bit: top 53 bits (exact double).
    32-bit: top 24 bits (exactly representable in float32 as well)."""
    if width == 64:
        return (value >> 11) * (1.0 / (1 << 53))
    return (value >> 8) * (1.0 / (1 << 24))


# --------------------------------------------------------------------------
# Seeds
# --------------------------------------------------------------------------


def fnv1a64(text: str) -> int:
    h = 0xCBF29CE484222325
    for byte in text.encode("utf-8"):
        h ^= byte
        h = (h * 0x100000001B3) & M64
    return h


def derive_seed(root: int, stream: str) -> int:
    """Independent child seed for a named subsystem: mix64(root XOR fnv1a64(name)).
    Adding draws in one stream never shifts another stream."""
    return mix64((root & M64) ^ fnv1a64(stream))


def daily_seed(date_iso: str, salt: str, period: str = "daily") -> Tuple[int, str]:
    """Seed for a calendar period. date_iso is a UTC date (YYYY-MM-DD).
    period 'weekly' keys on the ISO year-week so all 7 days share a seed."""
    d = _dt.date.fromisoformat(date_iso)
    if period == "weekly":
        iso = d.isocalendar()
        key = "weekly:%04d-W%02d" % (iso[0], iso[1])
    elif period == "daily":
        key = "daily:" + d.isoformat()
    else:
        raise ValueError("period must be daily or weekly")
    return derive_seed(fnv1a64(salt), key), key


CROCKFORD = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
CROCKFORD_CHECK = CROCKFORD + "*~$=U"
_DECODE_MAP = {c: i for i, c in enumerate(CROCKFORD)}
_DECODE_MAP.update({"O": 0, "I": 1, "L": 1})


def encode_seed(value: int, check: bool = False, group: int = 4) -> str:
    if value < 0:
        raise ValueError("seed must be non-negative")
    digits = []
    v = value
    while True:
        digits.append(CROCKFORD[v & 31])
        v >>= 5
        if v == 0:
            break
    s = "".join(reversed(digits))
    if check:
        s += CROCKFORD_CHECK[value % 37]
    if group > 0:
        s = "-".join(s[i:i + group] for i in range(0, len(s), group))
    return s


def decode_seed(code: str, check: bool = False) -> int:
    s = code.strip().upper().replace("-", "").replace(" ", "")
    if not s:
        raise ValueError("empty seed code")
    chk = None
    if check:
        chk, s = s[-1], s[:-1]
        if not s:
            raise ValueError("seed code too short for a check symbol")
    v = 0
    for c in s:
        if c not in _DECODE_MAP:
            raise ValueError("invalid seed character %r" % c)
        v = (v << 5) | _DECODE_MAP[c]
    if check and CROCKFORD_CHECK[v % 37] != chk:
        raise ValueError("check symbol mismatch (typo in seed code?)")
    return v


# --------------------------------------------------------------------------
# Expressive range analysis
# --------------------------------------------------------------------------

Grid = List[List[str]]
GRID_METRICS = ("density", "openness", "connectivity", "components", "linearity",
                "dead_ends", "leniency", "hazards")
RATIO_METRICS = {"density", "openness", "connectivity", "linearity", "dead_ends", "leniency"}


def _is_scalar(v: Any) -> bool:
    return v is None or isinstance(v, (str, int, float, bool))


def as_grid(value: Any) -> Optional[Grid]:
    """Return a rectangular grid of string cells if value looks like one."""
    if not isinstance(value, list) or len(value) < 2:
        return None
    if all(isinstance(r, str) for r in value):
        w = len(value[0])
        if w >= 2 and all(len(r) == w for r in value):
            return [list(r) for r in value]
        return None
    if all(isinstance(r, list) for r in value):
        w = len(value[0])
        if w >= 2 and all(len(r) == w and all(_is_scalar(c) for c in r) for r in value):
            return [["" if c is None else (str(int(c)) if isinstance(c, bool) else str(c)) for c in r]
                    for r in value]
    return None


def find_grids(doc: Any, depth: int = 0) -> List[Grid]:
    """Extract grids from: a bare grid, a level-spec (layout / layout.rows /
    layout.grid), a list of grids or docs, or any nested object (depth <= 6)."""
    if depth > 6:
        return []
    g = as_grid(doc)
    if g is not None:
        return [g]
    out: List[Grid] = []
    if isinstance(doc, dict):
        for key in ("grid", "rows", "layout", "map", "tiles", "cells"):
            if key in doc:
                found = find_grids(doc[key], depth + 1)
                if found:
                    return found
        for v in doc.values():
            if isinstance(v, (dict, list)):
                out.extend(find_grids(v, depth + 1))
    elif isinstance(doc, list):
        for v in doc:
            if isinstance(v, (dict, list)):
                out.extend(find_grids(v, depth + 1))
    return out


def grid_metrics(grid: Grid, walls: Sequence[str], hazards: Sequence[str]) -> Dict[str, float]:
    """Top-down adaptations of common ERA metrics (see generate-and-test.md):
    density      wall cells / all cells
    openness     floor cells / all cells (hazards count as floor)
    connectivity largest 4-connected floor region / floor cells
    components   number of 4-connected floor regions
    linearity    cells on the main path (approx. diameter of the largest region,
                 double BFS) / cells in that region; 1.0 = a single corridor
    dead_ends    floor cells with exactly one floor neighbour / floor cells
    leniency     1 - hazard cells / floor cells (1.0 = no hazards)
    hazards      hazard cell count
    """
    wall_set = set(walls) | {""}
    hazard_set = set(hazards)
    h, w = len(grid), len(grid[0])
    total = h * w
    floor = [[grid[y][x] not in wall_set for x in range(w)] for y in range(h)]
    n_floor = sum(row.count(True) for row in floor)
    n_haz = sum(1 for y in range(h) for x in range(w) if floor[y][x] and grid[y][x] in hazard_set)

    def nbrs(x: int, y: int) -> Iterator[Tuple[int, int]]:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and floor[ny][nx]:
                yield nx, ny

    def bfs(sx: int, sy: int) -> Dict[Tuple[int, int], int]:
        dist = {(sx, sy): 0}
        q = deque([(sx, sy)])
        while q:
            cx, cy = q.popleft()
            for n in nbrs(cx, cy):
                if n not in dist:
                    dist[n] = dist[(cx, cy)] + 1
                    q.append(n)
        return dist

    seen = set()
    comps: List[Dict[Tuple[int, int], int]] = []
    for y in range(h):
        for x in range(w):
            if floor[y][x] and (x, y) not in seen:
                d = bfs(x, y)
                seen.update(d.keys())
                comps.append(d)
    dead = sum(1 for y in range(h) for x in range(w)
               if floor[y][x] and sum(1 for _ in nbrs(x, y)) == 1)
    largest = max(comps, key=len) if comps else {}
    if largest:
        start = next(iter(largest))
        d1 = bfs(*start)
        far = max(d1, key=lambda k: d1[k])
        d2 = bfs(*far)
        diameter_cells = max(d2.values()) + 1
        linearity = diameter_cells / len(largest)
    else:
        linearity = 0.0
    return {
        "density": round((total - n_floor) / total, 4),
        "openness": round(n_floor / total, 4),
        "connectivity": round(len(largest) / n_floor, 4) if n_floor else 0.0,
        "components": float(len(comps)),
        "linearity": round(linearity, 4),
        "dead_ends": round(dead / n_floor, 4) if n_floor else 0.0,
        "leniency": round(1.0 - n_haz / n_floor, 4) if n_floor else 0.0,
        "hazards": float(n_haz),
    }


def grid_hash(grid: Grid) -> str:
    return hashlib.sha1("\n".join("\x1f".join(r) for r in grid).encode("utf-8")).hexdigest()[:16]


def load_items(paths: Sequence[str]) -> List[Dict[str, Any]]:
    """Return items {source, grid?, metrics?}. Files: .json (grids/level-specs),
    .jsonl (one grid doc or metric dict per line), .csv (metric rows)."""
    files: List[Path] = []
    for p in paths:
        pp = Path(p)
        if pp.is_dir():
            files.extend(sorted(q for q in pp.rglob("*") if q.suffix.lower() in (".json", ".jsonl", ".csv")))
        elif pp.is_file():
            files.append(pp)
        else:
            raise FileNotFoundError(p)
    items: List[Dict[str, Any]] = []
    for f in files:
        suffix = f.suffix.lower()
        if suffix == ".csv":
            with f.open(newline="", encoding="utf-8") as fh:
                for i, row in enumerate(csv.DictReader(fh)):
                    m = _numeric_row(row)
                    if m:
                        items.append({"source": "%s:%d" % (f.name, i + 2), "metrics": m})
        elif suffix == ".jsonl":
            for i, line in enumerate(f.read_text(encoding="utf-8").splitlines()):
                if line.strip():
                    items.extend(_items_from_doc(json.loads(line), "%s:%d" % (f.name, i + 1)))
        else:
            items.extend(_items_from_doc(json.loads(f.read_text(encoding="utf-8")), f.name))
    return items


def _numeric_row(row: Dict[str, Any]) -> Dict[str, float]:
    out: Dict[str, float] = {}
    for k, v in row.items():
        if isinstance(v, bool) or k is None:
            continue
        try:
            fv = float(v)
        except (TypeError, ValueError):
            continue
        if math.isfinite(fv):
            out[str(k)] = fv
    return out


def _items_from_doc(doc: Any, source: str) -> List[Dict[str, Any]]:
    grids = find_grids(doc)
    if grids:
        if len(grids) == 1:
            return [{"source": source, "grid": grids[0]}]
        return [{"source": "%s#%d" % (source, i), "grid": g} for i, g in enumerate(grids)]
    if isinstance(doc, dict):
        m = _numeric_row(doc)
        if m:
            return [{"source": source, "metrics": m}]
    if isinstance(doc, list) and doc and all(isinstance(d, dict) for d in doc):
        return [{"source": "%s#%d" % (source, i), "metrics": _numeric_row(d)} for i, d in enumerate(doc)]
    return []


_OPS = {">=": lambda a, b: a >= b, "<=": lambda a, b: a <= b, "==": lambda a, b: a == b,
        "!=": lambda a, b: a != b, ">": lambda a, b: a > b, "<": lambda a, b: a < b}


def parse_keep(expr: str) -> List[Tuple[str, str, float]]:
    rules = []
    for part in [p.strip() for p in expr.split(",") if p.strip()]:
        for op in (">=", "<=", "==", "!=", ">", "<"):
            if op in part:
                k, v = part.split(op, 1)
                rules.append((k.strip(), op, float(v)))
                break
        else:
            raise ValueError("bad keep rule %r (use metric>=value, comma-separated)" % part)
    return rules


def percentile(sorted_vals: List[float], q: float) -> float:
    if not sorted_vals:
        return float("nan")
    idx = (len(sorted_vals) - 1) * q
    lo, hi = int(math.floor(idx)), int(math.ceil(idx))
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (idx - lo)


def analyze(items: List[Dict[str, Any]], x: str, y: str, bins: int,
            walls: Sequence[str], hazards: Sequence[str], keep: Optional[str],
            range_x: Optional[Tuple[float, float]] = None,
            range_y: Optional[Tuple[float, float]] = None) -> Dict[str, Any]:
    if not items:
        raise ValueError("no grids or metric rows found in input")
    hashes: Dict[str, int] = {}
    rows: List[Dict[str, float]] = []
    for it in items:
        if "grid" in it:
            m = grid_metrics(it["grid"], walls, hazards)
            hsh = grid_hash(it["grid"])
            hashes[hsh] = hashes.get(hsh, 0) + 1
        else:
            m = dict(it["metrics"])
        rows.append(m)
    for axis in (x, y):
        if not any(axis in r for r in rows):
            raise ValueError("metric %r not present (available: %s)" % (axis, ", ".join(sorted(rows[0]))))
    names = sorted({k for r in rows for k in r})
    summary = {}
    for k in names:
        vals = sorted(r[k] for r in rows if k in r)
        summary[k] = {
            "mean": round(statistics.fmean(vals), 4),
            "sd": round(statistics.pstdev(vals), 4) if len(vals) > 1 else 0.0,
            "min": round(vals[0], 4), "p10": round(percentile(vals, 0.1), 4),
            "p50": round(percentile(vals, 0.5), 4), "p90": round(percentile(vals, 0.9), 4),
            "max": round(vals[-1], 4),
        }

    def axis_range(k: str, given: Optional[Tuple[float, float]]) -> Tuple[float, float]:
        if given:
            return given
        if k in RATIO_METRICS:
            return (0.0, 1.0)
        lo, hi = summary[k]["min"], summary[k]["max"]
        return (lo, hi if hi > lo else lo + 1.0)

    rx, ry = axis_range(x, range_x), axis_range(y, range_y)
    hist = [[0] * bins for _ in range(bins)]
    placed = 0
    for r in rows:
        if x not in r or y not in r:
            continue
        bx = min(bins - 1, max(0, int((r[x] - rx[0]) / (rx[1] - rx[0]) * bins)))
        by = min(bins - 1, max(0, int((r[y] - ry[0]) / (ry[1] - ry[0]) * bins)))
        hist[by][bx] += 1
        placed += 1
    nonempty = sum(1 for row in hist for c in row if c)
    peak = max(c for row in hist for c in row)
    dup_count = sum(c - 1 for c in hashes.values() if c > 1)
    result: Dict[str, Any] = {
        "n": len(rows),
        "x": x, "y": y, "bins": bins, "range_x": list(rx), "range_y": list(ry),
        "coverage": round(nonempty / (bins * bins), 4),
        "peak_bin_share": round(peak / placed, 4) if placed else 0.0,
        "duplicates": dup_count,
        "summary": summary,
        "histogram": hist,
        "metrics": [dict(source=items[i]["source"], **rows[i]) for i in range(len(rows))],
    }
    if keep:
        rules = parse_keep(keep)
        kept = [i for i, r in enumerate(rows)
                if all(k in r and _OPS[op](r[k], v) for k, op, v in rules)]
        result["keep"] = {"rules": keep, "kept": len(kept),
                          "acceptance": round(len(kept) / len(rows), 4),
                          "kept_sources": [items[i]["source"] for i in kept]}
    return result


def render_heatmap(res: Dict[str, Any]) -> str:
    shades = " .:-=+*#%@"
    hist = res["histogram"]
    peak = max(max(r) for r in hist) or 1
    lines = ["%s (rows, top = high) vs %s (columns, left = low)" % (res["y"], res["x"])]
    for row in reversed(hist):
        cells = []
        for c in row:
            cells.append(" " if c == 0 else shades[max(1, int(round(c / peak * (len(shades) - 1))))])
        lines.append("|" + "".join(ch * 2 for ch in cells) + "|")
    return "\n".join(lines)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def cmd_prng(a: argparse.Namespace) -> int:
    nxt, width = make_rng(a.algo, a.seed, a.seq)
    if a.bound:
        if width == 64:
            nxt32 = lambda: nxt() >> 32  # noqa: E731  (high bits are the best bits)
        else:
            nxt32 = nxt
        values = [bounded_u32(nxt32, a.bound) for _ in range(a.n)]
        out = {"algo": a.algo, "seed": a.seed, "seq": a.seq, "bound": a.bound, "values": values}
        if a.json:
            print(json.dumps(out))
        else:
            print("%s seed=%d bound=%d: %s" % (a.algo, a.seed, a.bound, " ".join(map(str, values))))
        return 0
    raw = [nxt() for _ in range(a.n)]
    out = {"algo": a.algo, "seed": a.seed, "seq": a.seq, "width": width,
           "values": raw, "hex": ["0x%0*x" % (width // 4, v) for v in raw],
           "unit_floats": [to_unit_float(v, width) for v in raw]}
    if a.json:
        print(json.dumps(out))
    else:
        print("%s seed=%d%s (%d-bit)" % (a.algo, a.seed, "" if a.seq is None else " seq=%d" % a.seq, width))
        for i, v in enumerate(raw):
            print("  %2d  %-20d %s  %.9f" % (i, v, out["hex"][i], out["unit_floats"][i]))
    return 0


def cmd_seed(a: argparse.Namespace) -> int:
    if a.action == "derive":
        if a.root is None or not a.stream:
            raise ValueError("derive needs --root and --stream")
        res = {"root": a.root, "streams": {s: derive_seed(a.root, s) for s in a.stream}}
    elif a.action in ("daily", "weekly"):
        date = a.date or _dt.datetime.now(_dt.timezone.utc).date().isoformat()
        if not a.salt:
            raise ValueError("%s needs --salt (a per-game, per-version constant)" % a.action)
        seed, key = daily_seed(date, a.salt, a.action)
        res = {"date_utc": date, "key": key, "seed": seed, "code": encode_seed(seed & M32 if a.short else seed)}
    elif a.action == "encode":
        if a.value is None:
            raise ValueError("encode needs --value")
        res = {"value": a.value, "code": encode_seed(a.value, a.check)}
    elif a.action == "decode":
        if not a.code:
            raise ValueError("decode needs --code")
        res = {"code": a.code, "value": decode_seed(a.code, a.check)}
    else:
        raise ValueError("unknown seed action")
    if a.json:
        print(json.dumps(res))
    else:
        for k, v in res.items():
            if isinstance(v, dict):
                for sk, sv in v.items():
                    print("%s.%s = %s" % (k, sk, sv))
            else:
                print("%s = %s" % (k, v))
    return 0


def _parse_range(s: Optional[str]) -> Optional[Tuple[float, float]]:
    if not s:
        return None
    lo, hi = (float(v) for v in s.split(","))
    if hi <= lo:
        raise ValueError("range must be lo,hi with hi > lo")
    return (lo, hi)


def cmd_era(a: argparse.Namespace) -> int:
    items = load_items(a.inputs)
    res = analyze(items, a.x, a.y, a.bins, [w for w in a.wall.split(",") if w],
                  [h for h in a.hazard.split(",") if h], a.keep,
                  _parse_range(a.range_x), _parse_range(a.range_y))
    failures = []
    if a.min_coverage is not None and res["coverage"] < a.min_coverage:
        failures.append("coverage %.3f < %.3f" % (res["coverage"], a.min_coverage))
    if a.max_duplicates is not None and res["duplicates"] > a.max_duplicates:
        failures.append("duplicates %d > %d" % (res["duplicates"], a.max_duplicates))
    if a.min_accept is not None:
        acc = res.get("keep", {}).get("acceptance")
        if acc is None:
            failures.append("--min-accept needs --keep")
        elif acc < a.min_accept:
            failures.append("acceptance %.3f < %.3f" % (acc, a.min_accept))
    res["failures"] = failures
    if not a.per_level:
        res.pop("metrics", None)
    if a.out:
        Path(a.out).write_text(json.dumps(res, indent=2) + "\n", encoding="utf-8")
    if a.json:
        print(json.dumps(res, indent=2))
    else:
        print("levels: %d   coverage: %.1f%% of %dx%d bins   peak bin: %.1f%%   duplicates: %d"
              % (res["n"], res["coverage"] * 100, a.bins, a.bins, res["peak_bin_share"] * 100, res["duplicates"]))
        print("%-13s %8s %7s %7s %7s %7s %7s %7s" % ("metric", "mean", "sd", "min", "p10", "p50", "p90", "max"))
        for k, s in res["summary"].items():
            print("%-13s %8.3f %7.3f %7.3f %7.3f %7.3f %7.3f %7.3f"
                  % (k, s["mean"], s["sd"], s["min"], s["p10"], s["p50"], s["p90"], s["max"]))
        print(render_heatmap(res))
        if "keep" in res:
            print("keep %s -> %d/%d accepted (%.1f%%)" % (res["keep"]["rules"], res["keep"]["kept"],
                                                         res["n"], res["keep"]["acceptance"] * 100))
        for f in failures:
            print("CHECK FAILED: " + f)
    return 1 if failures else 0


# --------------------------------------------------------------------------
# Self-test
# --------------------------------------------------------------------------


def selftest() -> int:
    checks: List[Tuple[str, bool]] = []

    def ok(name: str, cond: bool) -> None:
        checks.append((name, bool(cond)))

    # PCG32 reference: pcg32-demo, seed 42, sequence 54.
    g = PCG32(42, 54)
    ok("pcg32 demo vector", [g.next_u32() for _ in range(6)] ==
       [0xA15C02B7, 0x7B47F409, 0xBA1D3330, 0x83D2F293, 0xBFA4784B, 0xCBED606E])
    sm = SplitMix64(1234567)
    ok("splitmix64 vector", [sm.next_u64() for _ in range(3)] ==
       [6457827717110365317, 3203168211198807973, 9817491932198370423])
    ok("xorshift32 first output from 1", Xorshift32(1).next_u32() == 270369)
    xs = Xorshift64Star(1)
    first = xs.next_u64()
    ok("xorshift64* deterministic", first == Xorshift64Star(1).next_u64() and first != 0)
    xo = Xoshiro128SS(1)
    ok("xoshiro128** deterministic", [xo.next_u32() for _ in range(4)] ==
       [Xoshiro128SS(1).next_u32() for _ in range(1)] + [v for v in _skip(Xoshiro128SS(1), 1, 3)])
    # Bounded: unbiased and in range; distribution roughly uniform.
    g2 = PCG32(7)
    counts = [0] * 6
    for _ in range(60000):
        counts[g2.bounded(6)] += 1
    ok("bounded in range and ~uniform", all(9500 < c < 10500 for c in counts))
    ok("unit float in [0,1)", all(0.0 <= to_unit_float(v, w) < 1.0 for v, w in
                                  ((0, 32), (M32, 32), (0, 64), (M64, 64))))
    # Hashes and seeds.
    ok("fnv1a64 empty", fnv1a64("") == 0xCBF29CE484222325)
    ok("fnv1a64 'a'", fnv1a64("a") == 0xAF63DC4C8601EC8C)
    ok("streams differ", derive_seed(99, "loot") != derive_seed(99, "level"))
    ok("streams stable", derive_seed(99, "loot") == derive_seed(99, "loot"))
    s1, k1 = daily_seed("2026-10-19", "salt")
    s2, _ = daily_seed("2026-10-20", "salt")
    w1, wk1 = daily_seed("2026-10-19", "salt", "weekly")
    w2, _ = daily_seed("2026-10-25", "salt", "weekly")  # same ISO week (Sunday)
    ok("daily seeds differ by day", s1 != s2 and k1 == "daily:2026-10-19")
    ok("weekly seed shared within ISO week", w1 == w2 and wk1 == "weekly:2026-W43")
    for v in (0, 31, 32, 123456789, M64):
        ok("base32 roundtrip %d" % v, decode_seed(encode_seed(v)) == v and
           decode_seed(encode_seed(v, check=True), check=True) == v)
    ok("base32 forgiving decode", decode_seed("o1-il") == decode_seed("0111"))
    try:
        bad = encode_seed(123456789, check=True)
        decode_seed(bad[:-2] + ("Z" if bad[-2] != "Z" else "Y") + bad[-1], check=True)
        ok("check symbol catches typo", False)
    except ValueError:
        ok("check symbol catches typo", True)
    # ERA metrics on fixtures.
    corridor = as_grid(["#####", "#...#", "###.#", "#...#", "#####"])
    room = as_grid(["#######", "#.....#", "#.....#", "#.....#", "#######"])
    split = as_grid(["#####", "#.#.#", "#####"])
    hazard = as_grid(["#####", "#.^.#", "#####"])
    mc = grid_metrics(corridor, ["#"], ["^"])
    mr = grid_metrics(room, ["#"], ["^"])
    ms = grid_metrics(split, ["#"], ["^"])
    mh = grid_metrics(hazard, ["#"], ["^"])
    ok("corridor linearity 1.0", mc["linearity"] == 1.0 and mc["dead_ends"] > 0)
    ok("room less linear", mr["linearity"] < 0.6)
    ok("split connectivity 0.5", ms["connectivity"] == 0.5 and ms["components"] == 2)
    ok("hazard leniency", abs(mh["leniency"] - (1 - 1 / 3)) < 1e-3 and mh["hazards"] == 1)
    ok("numeric grid", grid_metrics(as_grid([[1, 1, 1], [1, 0, 0], [1, 1, 1]]), ["1"], [])["openness"] == round(2 / 9, 4))
    spec = {"schema_version": "1.0", "level_id": "l1", "layout": {"type": "grid", "rows": ["#..", "..#"]}}
    ok("level-spec grid found", len(find_grids(spec)) == 1)
    items = [{"source": "c", "grid": corridor}, {"source": "r", "grid": room}, {"source": "r2", "grid": room}]
    res = analyze(items, "linearity", "density", 4, ["#"], [], "linearity>=0.9")
    ok("era duplicates", res["duplicates"] == 1)
    ok("era keep", res["keep"]["kept"] == 1 and res["keep"]["acceptance"] == round(1 / 3, 4))
    ok("era coverage", 0 < res["coverage"] <= 1)
    ok("heatmap renders", "|" in render_heatmap(res))
    mrows = [{"source": "m%d" % i, "metrics": {"a": float(i), "b": float(i % 3)}} for i in range(9)]
    res2 = analyze(mrows, "a", "b", 3, [], [], None)
    ok("metric-row era", res2["n"] == 9 and res2["coverage"] > 0)

    failed = [n for n, c in checks if not c]
    for n, c in checks:
        print(("PASS " if c else "FAIL ") + n)
    print("%d/%d checks passed" % (len(checks) - len(failed), len(checks)))
    return 0 if not failed else 1


def _skip(rng: Xoshiro128SS, skip: int, take: int) -> List[int]:
    for _ in range(skip):
        rng.next_u32()
    return [rng.next_u32() for _ in range(take)]


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="PCG determinism and expressive-range helpers.",
                                formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    p.add_argument("--selftest", action="store_true", help="run built-in tests and exit")
    sub = p.add_subparsers(dest="cmd")

    pr = sub.add_parser("prng", help="print reference outputs of a portable PRNG")
    pr.add_argument("--algo", choices=ALGOS, default="pcg32")
    pr.add_argument("--seed", type=int, required=True)
    pr.add_argument("--seq", type=int, default=None, help="PCG32 stream selector (default library constant)")
    pr.add_argument("--n", type=int, default=8)
    pr.add_argument("--bound", type=int, default=0, help="emit unbiased ints in [0, bound) instead")
    pr.add_argument("--json", action="store_true")

    sd = sub.add_parser("seed", help="derive, date-key, encode or decode seeds")
    sd.add_argument("action", choices=("derive", "daily", "weekly", "encode", "decode"))
    sd.add_argument("--root", type=int, help="root/run seed for derive")
    sd.add_argument("--stream", action="append", help="stream name for derive (repeatable)")
    sd.add_argument("--date", help="UTC date YYYY-MM-DD for daily/weekly (default: today UTC)")
    sd.add_argument("--salt", help="per-game constant for daily/weekly; change it to reshuffle all dates")
    sd.add_argument("--short", action="store_true", help="daily/weekly: encode only the low 32 bits")
    sd.add_argument("--value", type=int, help="integer to encode")
    sd.add_argument("--code", help="code to decode")
    sd.add_argument("--check", action="store_true", help="append/verify a Crockford mod-37 check symbol")
    sd.add_argument("--json", action="store_true")

    er = sub.add_parser("era", help="expressive range analysis over generated levels")
    er.add_argument("--in", dest="inputs", action="append", required=True,
                    help="file or directory (.json grids/level-specs, .jsonl, .csv metric rows); repeatable")
    er.add_argument("--x", default="linearity", help="metric on the x axis")
    er.add_argument("--y", default="density", help="metric on the y axis")
    er.add_argument("--bins", type=int, default=10)
    er.add_argument("--range-x", help="lo,hi for x (default 0,1 for ratio metrics, else data range)")
    er.add_argument("--range-y", help="lo,hi for y")
    er.add_argument("--wall", default="#,1,W", help="comma list of wall/solid cell codes")
    er.add_argument("--hazard", default="^,X", help="comma list of hazard cell codes (passable)")
    er.add_argument("--keep", help='filter, e.g. "connectivity>=0.95,density<=0.55"')
    er.add_argument("--min-coverage", type=float, help="exit 1 if histogram coverage is below this")
    er.add_argument("--max-duplicates", type=int, help="exit 1 if more duplicate grids than this")
    er.add_argument("--min-accept", type=float, help="exit 1 if --keep acceptance is below this")
    er.add_argument("--per-level", action="store_true", help="include per-level metrics in output")
    er.add_argument("--out", help="write the JSON result to this path")
    er.add_argument("--json", action="store_true")
    return p


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    a = parser.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.cmd:
        parser.print_help()
        return 2
    try:
        if a.cmd == "prng":
            if a.n < 1 or a.n > 100000:
                raise ValueError("--n must be 1..100000")
            return cmd_prng(a)
        if a.cmd == "seed":
            return cmd_seed(a)
        if a.bins < 1 or a.bins > 50:
            raise ValueError("--bins must be 1..50")
        return cmd_era(a)
    except (ValueError, FileNotFoundError, json.JSONDecodeError) as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows pipes default to the ANSI code page; Claude Code reads UTF-8
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
