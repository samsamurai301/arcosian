#!/usr/bin/env python3
"""palette_audit.py - readability and accessibility audit of a game palette.

For every colour: relative luminance, CIELAB L*/C*/hue, value band (0-10).
For every pair: CIEDE2000 colour difference under normal vision and under
simulated protanopia, deuteranopia and tritanopia (Machado, Oliveira and
Fernandes 2009, severity 1.0, applied in linear sRGB), plus the lightness
difference dL* (the grayscale / squint test).
Checks:
  critical pairs  gameplay-critical distinctions (team, rarity, danger vs safe)
                  must keep dE00 >= --min-de (normal) and >= --min-de-cvd under
                  every simulated deficiency; dL* < --min-dl is a warning.
  text pairs      WCAG 2.x contrast ratio >= --min-text (default 4.5:1).
  ui pairs        WCAG 2.x non-text contrast >= --min-ui (default 3:1).
  value structure lightness range of the palette (warn when < 50 L*).

Inputs (one of):
  --colors "#2E4A3F,#7FB069,..." [--names bg,leaf,...]
  --palette PATH   JSON {"colors": {"name": "#RRGGBB"}, "critical_pairs": [["a","b"]],
                         "text_pairs": [["fg","bg"]], "ui_pairs": [["fg","bg"]]}
  --contract PATH  reads contract.json art_direction.palette when it is a hex list
Pairs on the command line: --critical "a:b,c:d"  --text "fg:bg"  --ui "fg:bg"
  (names, or hex values, or 1-based indices). --all-critical treats every pair as critical.

Thresholds are studio heuristics, not standards (except the WCAG ratios).
Exit codes: 0 ok, 1 a check failed, 2 usage/input error. Stdlib only; Python 3.9+.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

RGB = Tuple[float, float, float]
LAB = Tuple[float, float, float]

HEX_RE = re.compile(r"^#?([0-9A-Fa-f]{6})([0-9A-Fa-f]{2})?$")

# Machado et al. (2009) simulation matrices, severity 1.0, linear RGB.
CVD_MATRICES: Dict[str, Tuple[RGB, RGB, RGB]] = {
    "protan": ((0.152286, 1.052583, -0.204868),
               (0.114503, 0.786281, 0.099216),
               (-0.003882, -0.048116, 1.051998)),
    "deutan": ((0.367322, 0.860646, -0.227968),
               (0.280085, 0.672501, 0.047413),
               (-0.011820, 0.042940, 0.968881)),
    "tritan": ((1.255528, -0.076749, -0.178779),
               (-0.078411, 0.930809, 0.147602),
               (0.004733, 0.691367, 0.303900)),
}
WHITE_D65 = (0.95047, 1.0, 1.08883)


class InputError(ValueError):
    """Malformed input (exit code 2)."""


# --------------------------------------------------------------------------- colour maths

def parse_hex(text: str) -> RGB:
    m = HEX_RE.match(text.strip())
    if not m:
        raise InputError("not a #RRGGBB colour: %r" % text)
    h = m.group(1)
    return (int(h[0:2], 16) / 255.0, int(h[2:4], 16) / 255.0, int(h[4:6], 16) / 255.0)


def to_hex(rgb: RGB) -> str:
    return "#" + "".join("%02X" % int(round(max(0.0, min(1.0, c)) * 255)) for c in rgb)


def srgb_to_linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def linear_to_srgb(c: float) -> float:
    c = max(0.0, min(1.0, c))
    return 12.92 * c if c <= 0.0031308 else 1.055 * (c ** (1 / 2.4)) - 0.055


def relative_luminance(rgb: RGB) -> float:
    r, g, b = (srgb_to_linear(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(a: RGB, b: RGB) -> float:
    la, lb = relative_luminance(a), relative_luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def rgb_to_lab(rgb: RGB) -> LAB:
    r, g, b = (srgb_to_linear(c) for c in rgb)
    x = 0.4124564 * r + 0.3575761 * g + 0.1804375 * b
    y = 0.2126729 * r + 0.7151522 * g + 0.0721750 * b
    z = 0.0193339 * r + 0.1191920 * g + 0.9503041 * b
    d = 6.0 / 29.0

    def f(t: float) -> float:
        return t ** (1.0 / 3.0) if t > d ** 3 else t / (3 * d * d) + 4.0 / 29.0

    fx, fy, fz = f(x / WHITE_D65[0]), f(y / WHITE_D65[1]), f(z / WHITE_D65[2])
    return (116.0 * fy - 16.0, 500.0 * (fx - fy), 200.0 * (fy - fz))


def simulate_cvd(rgb: RGB, kind: str) -> RGB:
    m = CVD_MATRICES[kind]
    lin = [srgb_to_linear(c) for c in rgb]
    out = []
    for row in m:
        out.append(linear_to_srgb(row[0] * lin[0] + row[1] * lin[1] + row[2] * lin[2]))
    return (out[0], out[1], out[2])


def ciede2000(lab1: LAB, lab2: LAB) -> float:
    """CIEDE2000 colour difference (Sharma, Wu, Dalal 2005 formulation), kL=kC=kH=1."""
    L1, a1, b1 = lab1
    L2, a2, b2 = lab2
    c1 = math.hypot(a1, b1)
    c2 = math.hypot(a2, b2)
    cbar = (c1 + c2) / 2.0
    g = 0.5 * (1 - math.sqrt(cbar ** 7 / (cbar ** 7 + 25.0 ** 7)))
    a1p, a2p = (1 + g) * a1, (1 + g) * a2
    c1p, c2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    h1p = math.degrees(math.atan2(b1, a1p)) % 360.0 if c1p else 0.0
    h2p = math.degrees(math.atan2(b2, a2p)) % 360.0 if c2p else 0.0
    dLp = L2 - L1
    dCp = c2p - c1p
    if c1p * c2p == 0:
        dhp = 0.0
    else:
        dhp = h2p - h1p
        if dhp > 180:
            dhp -= 360
        elif dhp < -180:
            dhp += 360
    dHp = 2 * math.sqrt(c1p * c2p) * math.sin(math.radians(dhp / 2.0))
    Lbp = (L1 + L2) / 2.0
    Cbp = (c1p + c2p) / 2.0
    if c1p * c2p == 0:
        hbp = h1p + h2p
    elif abs(h1p - h2p) <= 180:
        hbp = (h1p + h2p) / 2.0
    elif h1p + h2p < 360:
        hbp = (h1p + h2p + 360) / 2.0
    else:
        hbp = (h1p + h2p - 360) / 2.0
    t = (1 - 0.17 * math.cos(math.radians(hbp - 30)) + 0.24 * math.cos(math.radians(2 * hbp))
         + 0.32 * math.cos(math.radians(3 * hbp + 6)) - 0.20 * math.cos(math.radians(4 * hbp - 63)))
    d_theta = 30 * math.exp(-(((hbp - 275) / 25.0) ** 2))
    rc = 2 * math.sqrt(Cbp ** 7 / (Cbp ** 7 + 25.0 ** 7))
    sl = 1 + (0.015 * (Lbp - 50) ** 2) / math.sqrt(20 + (Lbp - 50) ** 2)
    sc = 1 + 0.045 * Cbp
    sh = 1 + 0.015 * Cbp * t
    rt = -math.sin(math.radians(2 * d_theta)) * rc
    return math.sqrt((dLp / sl) ** 2 + (dCp / sc) ** 2 + (dHp / sh) ** 2
                     + rt * (dCp / sc) * (dHp / sh))


# --------------------------------------------------------------------------- audit

def describe(name: str, rgb: RGB) -> Dict[str, object]:
    L, a, b = rgb_to_lab(rgb)
    return {
        "name": name,
        "hex": to_hex(rgb),
        "luminance": round(relative_luminance(rgb), 4),
        "L": round(L, 1),
        "chroma": round(math.hypot(a, b), 1),
        "hue_deg": round(math.degrees(math.atan2(b, a)) % 360.0, 0),
        "value_band": int(round(L / 10.0)),
        "grey_hex": to_hex((linear_to_srgb(relative_luminance(rgb)),) * 3),
    }


def pair_metrics(a: RGB, b: RGB) -> Dict[str, float]:
    la, lb = rgb_to_lab(a), rgb_to_lab(b)
    out = {"dE00": ciede2000(la, lb), "dL": abs(la[0] - lb[0]), "contrast": contrast_ratio(a, b)}
    for kind in CVD_MATRICES:
        out["dE00_" + kind] = ciede2000(rgb_to_lab(simulate_cvd(a, kind)), rgb_to_lab(simulate_cvd(b, kind)))
    out["dE00_cvd_min"] = min(out["dE00_" + k] for k in CVD_MATRICES)
    return {k: round(v, 2) for k, v in out.items()}


def resolve(token: str, names: List[str], colours: Dict[str, RGB]) -> str:
    t = token.strip()
    if t in colours:
        return t
    if t.isdigit() and 1 <= int(t) <= len(names):
        return names[int(t) - 1]
    if HEX_RE.match(t):
        want = to_hex(parse_hex(t))
        for n in names:
            if to_hex(colours[n]) == want:
                return n
    raise InputError("unknown colour reference %r (use a name, a palette hex, or a 1-based index)" % token)


def parse_pairs(text: Optional[str], names: List[str], colours: Dict[str, RGB]) -> List[Tuple[str, str]]:
    if not text:
        return []
    pairs = []
    for chunk in text.split(","):
        if not chunk.strip():
            continue
        if ":" not in chunk:
            raise InputError("pair %r must be written a:b" % chunk)
        x, y = chunk.split(":", 1)
        pairs.append((resolve(x, names, colours), resolve(y, names, colours)))
    return pairs


def audit(colours: Dict[str, RGB], critical: Sequence[Tuple[str, str]], text: Sequence[Tuple[str, str]],
          ui: Sequence[Tuple[str, str]], th: Dict[str, float], all_critical: bool = False) -> Dict[str, object]:
    names = list(colours)
    report: Dict[str, object] = {"thresholds": th, "colours": [describe(n, colours[n]) for n in names]}
    pairs = []
    for x, y in itertools.combinations(names, 2):
        m = pair_metrics(colours[x], colours[y])
        m.update({"a": x, "b": y})
        pairs.append(m)
    report["closest_pairs"] = sorted(pairs, key=lambda p: p["dE00_cvd_min"])[:5]
    failures: List[str] = []
    warnings: List[str] = []
    crit = list(critical) or (list(itertools.combinations(names, 2)) if all_critical else [])
    crit_rows = []
    for x, y in crit:
        m = pair_metrics(colours[x], colours[y])
        ok = m["dE00"] >= th["min_de"] and m["dE00_cvd_min"] >= th["min_de_cvd"]
        row = {"a": x, "b": y, "ok": ok, **m}
        crit_rows.append(row)
        if not ok:
            worst = min(CVD_MATRICES, key=lambda k: m["dE00_" + k])
            failures.append("critical pair %s/%s: dE00 %.1f (min %.0f), worst CVD %s %.1f (min %.0f)" % (
                x, y, m["dE00"], th["min_de"], worst, m["dE00_" + worst], th["min_de_cvd"]))
        if m["dL"] < th["min_dl"]:
            warnings.append("critical pair %s/%s: dL* %.1f < %.0f - the distinction disappears in grayscale; "
                            "add shape/icon/pattern coding" % (x, y, m["dL"], th["min_dl"]))
    report["critical_pairs"] = crit_rows
    for label, plist, key in (("text", text, "min_text"), ("ui", ui, "min_ui")):
        rows = []
        for fg, bg in plist:
            cr = round(contrast_ratio(colours[fg], colours[bg]), 2)
            ok = cr >= th[key]
            rows.append({"fg": fg, "bg": bg, "contrast": cr, "ok": ok})
            if not ok:
                failures.append("%s pair %s on %s: contrast %.2f:1 < %.1f:1" % (label, fg, bg, cr, th[key]))
        report[label + "_pairs"] = rows
    Ls = sorted(c["L"] for c in report["colours"])  # type: ignore[index]
    bands = sorted({c["value_band"] for c in report["colours"]})  # type: ignore[index]
    vs = {"L_min": Ls[0], "L_max": Ls[-1], "L_range": round(Ls[-1] - Ls[0], 1), "value_bands": bands}
    report["value_structure"] = vs
    if len(Ls) > 1 and vs["L_range"] < 50:
        warnings.append("palette lightness range %.0f L* < 50: weak value structure; add a darker dark "
                        "or lighter light" % vs["L_range"])
    report["failures"] = failures
    report["warnings"] = warnings
    report["verdict"] = "fail" if failures else "pass"
    return report


# --------------------------------------------------------------------------- io

def load_inputs(args: argparse.Namespace) -> Tuple[Dict[str, RGB], dict]:
    extra: dict = {}
    colours: Dict[str, RGB] = {}
    if args.palette:
        try:
            doc = json.loads(Path(args.palette).read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise InputError("cannot read palette %s: %s" % (args.palette, exc))
        raw = doc.get("colors") or doc.get("colours")
        if isinstance(raw, dict):
            colours = {str(k): parse_hex(str(v)) for k, v in raw.items()}
        elif isinstance(raw, list):
            colours = {"c%d" % (i + 1): parse_hex(str(v)) for i, v in enumerate(raw)}
        else:
            raise InputError("palette JSON needs a 'colors' object or list")
        extra = doc
    elif args.contract:
        try:
            doc = json.loads(Path(args.contract).read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise InputError("cannot read contract %s: %s" % (args.contract, exc))
        pal = (doc.get("art_direction") or {}).get("palette")
        if not isinstance(pal, list) or not pal:
            raise InputError("contract art_direction.palette is not a hex list")
        colours = {"c%d" % (i + 1): parse_hex(str(v)) for i, v in enumerate(pal)}
    elif args.colors:
        hexes = [h for h in args.colors.split(",") if h.strip()]
        names = [n.strip() for n in args.names.split(",")] if args.names else []
        if names and len(names) != len(hexes):
            raise InputError("--names has %d entries for %d colours" % (len(names), len(hexes)))
        names = names or ["c%d" % (i + 1) for i in range(len(hexes))]
        colours = {n: parse_hex(h) for n, h in zip(names, hexes)}
    else:
        raise InputError("give --colors, --palette or --contract (or --selftest)")
    if len(colours) < 1:
        raise InputError("no colours given")
    return colours, extra


def render_text(r: Dict[str, object]) -> str:
    lines = ["Colours (L* = perceived lightness 0-100; band = L*/10):"]
    for c in r["colours"]:  # type: ignore[union-attr]
        lines.append("  %-12s %s  L*%5.1f  C*%5.1f  hue %3.0f  band %2d  grey %s" % (
            c["name"], c["hex"], c["L"], c["chroma"], c["hue_deg"], c["value_band"], c["grey_hex"]))
    vs = r["value_structure"]
    lines.append("Value structure: L* %.1f-%.1f (range %.1f), bands %s" % (
        vs["L_min"], vs["L_max"], vs["L_range"], vs["value_bands"]))  # type: ignore[index]
    lines.append("Closest pairs (by worst-case dE00 across normal + 3 CVD simulations):")
    for p in r["closest_pairs"]:  # type: ignore[union-attr]
        lines.append("  %s/%s: dE00 %.1f | protan %.1f deutan %.1f tritan %.1f | dL* %.1f | contrast %.2f:1" % (
            p["a"], p["b"], p["dE00"], p["dE00_protan"], p["dE00_deutan"], p["dE00_tritan"], p["dL"], p["contrast"]))
    for key in ("critical_pairs", "text_pairs", "ui_pairs"):
        rows = r.get(key) or []
        if rows:
            lines.append(key.replace("_", " ").capitalize() + ":")
            for row in rows:  # type: ignore[union-attr]
                if key == "critical_pairs":
                    lines.append("  [%s] %s/%s dE00 %.1f, CVD min %.1f, dL* %.1f" % (
                        "ok" if row["ok"] else "FAIL", row["a"], row["b"], row["dE00"], row["dE00_cvd_min"], row["dL"]))
                else:
                    lines.append("  [%s] %s on %s %.2f:1" % ("ok" if row["ok"] else "FAIL", row["fg"], row["bg"], row["contrast"]))
    for w in r["warnings"]:  # type: ignore[union-attr]
        lines.append("WARN " + w)
    for f in r["failures"]:  # type: ignore[union-attr]
        lines.append("FAIL " + f)
    lines.append("Verdict: %s" % r["verdict"])
    return "\n".join(lines)


# --------------------------------------------------------------------------- selftest

def selftest() -> int:
    checks = []
    # Sharma et al. (2005) test pair 1: expected dE00 = 2.0425
    d = ciede2000((50.0, 2.6772, -79.7751), (50.0, 0.0, -82.7485))
    checks.append(("ciede2000 sharma pair 1", abs(d - 2.0425) < 1e-3))
    # Sharma pair 17 (large difference): (50, 2.5, 0) vs (73, 25, -18) -> 27.1492
    d = ciede2000((50.0, 2.5, 0.0), (73.0, 25.0, -18.0))
    checks.append(("ciede2000 sharma pair 17", abs(d - 27.1492) < 1e-3))
    checks.append(("contrast black/white = 21", abs(contrast_ratio((0, 0, 0), (1, 1, 1)) - 21.0) < 1e-9))
    checks.append(("contrast #777 on white ~ 4.48", abs(contrast_ratio(parse_hex("#777777"), (1, 1, 1)) - 4.48) < 0.01))
    L, a, b = rgb_to_lab((1.0, 1.0, 1.0))
    checks.append(("white L*=100", abs(L - 100) < 0.01 and abs(a) < 0.05 and abs(b) < 0.05))
    # Red vs green: distinct for normal vision, collapses under deuteranopia.
    red, green = parse_hex("#D33F3F"), parse_hex("#4FA34F")
    m = pair_metrics(red, green)
    checks.append(("red/green distinct normally", m["dE00"] > 30))
    checks.append(("red/green collapse for deutan", m["dE00_deutan"] < m["dE00"] / 2))
    # Grey stays grey under simulation.
    g = simulate_cvd((0.5, 0.5, 0.5), "protan")
    checks.append(("grey invariant", all(abs(c - 0.5) < 0.01 for c in g)))
    # End-to-end audit with a failing critical pair and a failing text pair.
    cols = {"bg": parse_hex("#2E4A3F"), "red": red, "green": green, "cream": parse_hex("#F4F1DE"),
            "mid": parse_hex("#5A6B60")}
    rep = audit(cols, [("red", "green")], [("cream", "bg"), ("mid", "bg")], [],
                {"min_de": 20, "min_de_cvd": 12, "min_dl": 10, "min_text": 4.5, "min_ui": 3.0})
    checks.append(("audit flags red/green", rep["verdict"] == "fail" and any("red/green" in f for f in rep["failures"])))
    checks.append(("cream on bg passes text", rep["text_pairs"][0]["ok"] is True))
    checks.append(("mid on bg fails text", rep["text_pairs"][1]["ok"] is False))
    ok = True
    for name, passed in checks:
        print("%-36s %s" % (name, "ok" if passed else "FAIL"))
        ok = ok and passed
    print("selftest: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0],
                                formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    p.add_argument("--colors", help="comma-separated #RRGGBB list")
    p.add_argument("--names", help="comma-separated names matching --colors")
    p.add_argument("--palette", help="palette JSON file")
    p.add_argument("--contract", help="contract.json; uses art_direction.palette")
    p.add_argument("--critical", help="gameplay-critical pairs a:b,c:d")
    p.add_argument("--text", help="text-on-background pairs fg:bg")
    p.add_argument("--ui", help="non-text UI pairs fg:bg (icons, outlines, bars)")
    p.add_argument("--all-critical", action="store_true", help="treat every pair as gameplay-critical")
    p.add_argument("--min-de", type=float, default=20.0, help="min dE00, normal vision (default 20)")
    p.add_argument("--min-de-cvd", type=float, default=12.0, help="min dE00 under each CVD simulation (default 12)")
    p.add_argument("--min-dl", type=float, default=10.0, help="warn when critical dL* is below this (default 10)")
    p.add_argument("--min-text", type=float, default=4.5, help="min WCAG text contrast (default 4.5)")
    p.add_argument("--min-ui", type=float, default=3.0, help="min WCAG non-text contrast (default 3.0)")
    p.add_argument("--json", action="store_true", help="machine-readable output")
    p.add_argument("--selftest", action="store_true", help="run built-in checks")
    args = p.parse_args(argv)
    if args.selftest:
        return selftest()
    try:
        colours, extra = load_inputs(args)
        names = list(colours)
        th = {"min_de": args.min_de, "min_de_cvd": args.min_de_cvd, "min_dl": args.min_dl,
              "min_text": args.min_text, "min_ui": args.min_ui}
        th.update({k: float(v) for k, v in (extra.get("thresholds") or {}).items() if k in th})

        def from_doc(key: str) -> List[Tuple[str, str]]:
            return [(resolve(str(a), names, colours), resolve(str(b), names, colours)) for a, b in extra.get(key, [])]

        critical = parse_pairs(args.critical, names, colours) + from_doc("critical_pairs")
        text = parse_pairs(args.text, names, colours) + from_doc("text_pairs")
        ui = parse_pairs(args.ui, names, colours) + from_doc("ui_pairs")
    except (InputError, TypeError, ValueError) as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    rep = audit(colours, critical, text, ui, th, all_critical=args.all_critical)
    if args.json:
        print(json.dumps(rep, indent=2))
    else:
        print(render_text(rep))
    return 1 if rep["failures"] else 0


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows pipes default to the ANSI code page; Claude Code reads UTF-8
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
