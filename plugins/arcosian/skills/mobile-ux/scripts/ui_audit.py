#!/usr/bin/env python3
"""ui_audit.py - structural mobile UI checks for the arcosian `mobile-ux` skill.

Stdlib only, Python 3.9+. Subcommands:

  contrast  --fg HEX --bg HEX [--large] [--nontext] [--json]
      WCAG 2.x contrast ratio and AA/AAA verdicts. Exit 1 if the pair fails AA
      for the stated use (normal text by default, --large for large text,
      --nontext for icons/UI component boundaries).

  units     (--pt N | --dp N | --px N | --mm N) [--scale S] [--ppi P] [--json]
      Convert between iOS points, Android dp, device pixels and millimetres.
      pt/dp are treated as 1/160 inch unless --ppi and --scale give the exact
      device geometry. Reports whether the size clears 44 pt / 48 dp.

  expansion (--text STR | --chars N) [--max-chars M] [--json]
      Expected translated length of an English UI string using the length-band
      expansion table IBM published and W3C reproduces ("Text size in
      translation"). Exit 1 if --max-chars cannot fit the low end of the band.

  layout    --spec PATH [--min-target N] [--json]
      Audit one screen described in a small JSON layout spec (see `template`):
      touch-target size, safe-area intrusion, off-screen elements, overlapping
      or crowded targets, thumb-zone placement of primary and frequent actions,
      destructive/purchase controls next to primary/close controls, text
      expansion headroom, minimum font size and primary-CTA count.
      Exit 1 if any blocker or major finding.

      Spec fields: name, platform (ios|android), hand (right|left|either|two|
      cradle), screen {w, h, unit (pt|dp|px), scale (px only), safe {top,
      bottom, left, right}}, elements [{id, rect [x, y, w, h], role (primary|
      action|secondary|nav|close|purchase|destructive|info|decor), touch,
      frequency (high|medium|low), group (targets in one group, e.g. a tab
      bar, may abut), confirm, text, max_chars, translatable, font_pt,
      critical, decor}]. Coordinates are top-left origin in the screen unit.

  template  [--platform ios|android] [--hand right|left|either|two|cradle] [--out PATH]
      Print (or write) an example layout spec to start from.

Global: --selftest runs built-in fixtures and exits 0 on success.
Exit codes: 0 ok, 1 check failed, 2 usage/input error.

All thresholds are platform minimums or studio starting points, not
guarantees of usability. Confirm with device playtests (`qa-testing`).
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# --------------------------------------------------------------------------
# Constants (platform minimums and studio heuristics; see SKILL.md)
# --------------------------------------------------------------------------
MIN_TARGET = {"ios": 44.0, "android": 48.0}  # Apple HIG 44x44 pt, Material 48x48 dp
PRIMARY_ACTION_MIN = 60.0  # studio heuristic for repeatedly struck in-game buttons
MIN_GAP = 8.0  # gap between adjacent touch targets (pt/dp)
DANGER_GAP = 16.0  # minimum gap between destructive/purchase and primary/close controls
MIN_FONT = 11.0  # Apple HIG minimum text size (pt); Material smallest type-scale role is 11 sp
CRITICAL_FONT = 13.0  # studio floor for gameplay-critical text at default text scale
SEVERITIES = ("blocker", "major", "minor", "polish")
ZONE_RANK = {"easy": 0, "stretch": 1, "hard": 2}

# IBM length-band expansion ratios as reproduced by W3C "Text size in translation".
# (max source chars inclusive, low multiplier, high multiplier)
EXPANSION_BANDS: Tuple[Tuple[int, float, float], ...] = (
    (10, 2.0, 3.0),
    (20, 1.8, 2.0),
    (30, 1.6, 1.8),
    (50, 1.4, 1.6),
    (70, 1.51, 1.7),
    (10 ** 9, 1.3, 1.3),
)


class UsageError(Exception):
    """Raised for invalid input (exit code 2)."""


# --------------------------------------------------------------------------
# Contrast (WCAG 2.x)
# --------------------------------------------------------------------------
def parse_hex(value: str) -> Tuple[int, int, int]:
    s = value.strip().lstrip("#")
    if len(s) == 3:
        s = "".join(ch * 2 for ch in s)
    if len(s) != 6:
        raise UsageError("colour must be #RGB or #RRGGBB, got %r" % value)
    try:
        return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)
    except ValueError:
        raise UsageError("colour must be hexadecimal, got %r" % value)


def relative_luminance(rgb: Tuple[int, int, int]) -> float:
    def channel(c: int) -> float:
        x = c / 255.0
        return x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4

    r, g, b = (channel(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(fg: str, bg: str) -> float:
    l1 = relative_luminance(parse_hex(fg))
    l2 = relative_luminance(parse_hex(bg))
    hi, lo = max(l1, l2), min(l1, l2)
    return (hi + 0.05) / (lo + 0.05)


def contrast_report(fg: str, bg: str, large: bool = False, nontext: bool = False) -> Dict[str, Any]:
    ratio = contrast_ratio(fg, bg)
    rounded = math.floor(ratio * 100) / 100.0  # never round up into a pass
    verdicts = {
        "normal_text_AA_4.5": rounded >= 4.5,
        "normal_text_AAA_7": rounded >= 7.0,
        "large_text_AA_3": rounded >= 3.0,
        "large_text_AAA_4.5": rounded >= 4.5,
        "non_text_AA_3": rounded >= 3.0,
    }
    if nontext:
        use, ok = "non-text (icons, component boundaries, focus indicators)", verdicts["non_text_AA_3"]
    elif large:
        use, ok = "large text (>= 18 pt regular or >= 14 pt bold equivalent)", verdicts["large_text_AA_3"]
    else:
        use, ok = "normal text", verdicts["normal_text_AA_4.5"]
    return {"fg": fg, "bg": bg, "ratio": rounded, "use": use, "pass_AA": ok, "verdicts": verdicts}


# --------------------------------------------------------------------------
# Units
# --------------------------------------------------------------------------
def convert_units(pt: Optional[float] = None, dp: Optional[float] = None, px: Optional[float] = None,
                  mm: Optional[float] = None, scale: Optional[float] = None,
                  ppi: Optional[float] = None) -> Dict[str, Any]:
    given = [v for v in (pt, dp, px, mm) if v is not None]
    if len(given) != 1:
        raise UsageError("give exactly one of --pt, --dp, --px, --mm")
    if scale is not None and scale <= 0:
        raise UsageError("--scale must be > 0")
    if ppi is not None and ppi <= 0:
        raise UsageError("--ppi must be > 0")
    # logical units per inch: exact if ppi and scale known, else nominal 160
    lpi = (ppi / scale) if (ppi and scale) else 160.0
    if px is not None:
        if not scale:
            raise UsageError("--px needs --scale (pixels per point/dp, e.g. 3 for @3x or xxhdpi)")
        logical = px / scale
    elif mm is not None:
        logical = mm / 25.4 * lpi
    else:
        logical = pt if pt is not None else dp  # type: ignore[assignment]
    out: Dict[str, Any] = {
        "logical": round(logical, 2),
        "mm": round(logical / lpi * 25.4, 2),
        "inch": round(logical / lpi, 4),
        "logical_per_inch": round(lpi, 2),
        "exact_geometry": bool(ppi and scale),
        "clears_ios_44pt": logical >= MIN_TARGET["ios"],
        "clears_android_48dp": logical >= MIN_TARGET["android"],
    }
    if scale:
        out["px"] = round(logical * scale, 1)
    return out


# --------------------------------------------------------------------------
# Expansion
# --------------------------------------------------------------------------
def expansion_band(chars: int) -> Tuple[float, float]:
    if chars < 0:
        raise UsageError("character count must be >= 0")
    for limit, lo, hi in EXPANSION_BANDS:
        if chars <= limit:
            return lo, hi
    return EXPANSION_BANDS[-1][1], EXPANSION_BANDS[-1][2]


def expansion_report(chars: int, max_chars: Optional[int] = None) -> Dict[str, Any]:
    lo, hi = expansion_band(chars)
    low_len, high_len = int(math.ceil(chars * lo)), int(math.ceil(chars * hi))
    rep: Dict[str, Any] = {
        "source_chars": chars,
        "ratio_low": lo,
        "ratio_high": hi,
        "expected_len_low": low_len,
        "expected_len_high": high_len,
        "note": "European-language averages (IBM via W3C); CJK is often shorter in characters but wider "
                "per glyph and taller; Thai/Arabic/Devanagari need extra line height.",
    }
    if max_chars is not None:
        if max_chars < low_len:
            rep["verdict"], rep["severity"] = "fail", "major"
        elif max_chars < high_len:
            rep["verdict"], rep["severity"] = "risk", "minor"
        else:
            rep["verdict"], rep["severity"] = "pass", None
        rep["max_chars"] = max_chars
    return rep


# --------------------------------------------------------------------------
# Layout audit
# --------------------------------------------------------------------------
Rect = Tuple[float, float, float, float]


def _rect(el: Dict[str, Any]) -> Rect:
    r = el.get("rect")
    if not isinstance(r, list) or len(r) != 4 or not all(isinstance(v, (int, float)) for v in r):
        raise UsageError("element %r needs rect [x, y, w, h] with numbers" % el.get("id"))
    x, y, w, h = (float(v) for v in r)
    if w <= 0 or h <= 0:
        raise UsageError("element %r has non-positive size" % el.get("id"))
    return x, y, w, h


def _gap(a: Rect, b: Rect) -> float:
    """Separation between two rects; negative when they overlap."""
    ax2, ay2, bx2, by2 = a[0] + a[2], a[1] + a[3], b[0] + b[2], b[1] + b[3]
    dx = max(b[0] - ax2, a[0] - bx2)
    dy = max(b[1] - ay2, a[1] - by2)
    if dx < 0 and dy < 0:
        return max(dx, dy)  # overlapping: negative depth (closest to zero)
    return max(dx, dy, 0.0) if (dx < 0 or dy < 0) else math.hypot(dx, dy)


def _one_hand_zone(u: float, v: float, grip: str) -> str:
    """Heuristic thumb-reach map for one-handed portrait use.

    u: 0 = left edge .. 1 = right edge; v: 0 = top .. 1 = bottom.
    Mirrors the qualitative zone maps popularised by Hoober (2013) and
    Clark ("Designing for Touch", 2015): bottom band easy, top band hard,
    the top corner opposite the gripping hand hardest, and the corner
    directly under the thumb base cramped. Tune per device with playtests.
    """
    far = u if grip == "left" else 1.0 - u  # 0 at the grip edge, 1 at the far edge
    if v < 0.25:
        return "hard"
    if v < 0.45:
        return "hard" if far > 0.6 else "stretch"
    if v < 0.60:
        return "stretch"
    if v > 0.94 and far < 0.12:
        return "stretch"
    return "easy"


def thumb_zone(cx: float, cy: float, w: float, h: float, hand: str) -> str:
    u, v = cx / w, cy / h
    if hand in ("right", "left"):
        return _one_hand_zone(u, v, hand)
    if hand == "either":
        a, b = _one_hand_zone(u, v, "left"), _one_hand_zone(u, v, "right")
        return a if ZONE_RANK[a] >= ZONE_RANK[b] else b
    if hand == "two":  # two thumbs, usually landscape grip
        side = min(u, 1.0 - u)
        if v >= 0.45 and side <= 0.30:
            return "easy"
        if v >= 0.25 and side <= 0.45:
            return "stretch"
        return "hard"
    if hand == "cradle":  # held in one hand, tapped with the other hand
        return "stretch" if v < 0.08 else "easy"
    raise UsageError("hand must be right|left|either|two|cradle")


def audit_layout(spec: Dict[str, Any], min_target: Optional[float] = None) -> Dict[str, Any]:
    if not isinstance(spec, dict):
        raise UsageError("layout spec must be a JSON object")
    screen = spec.get("screen")
    if not isinstance(screen, dict):
        raise UsageError("spec.screen is required")
    platform = spec.get("platform", "ios")
    if platform not in MIN_TARGET:
        raise UsageError("platform must be ios or android")
    unit = screen.get("unit", "pt" if platform == "ios" else "dp")
    factor = 1.0
    if unit == "px":
        scale = float(screen.get("scale", 0) or 0)
        if scale <= 0:
            raise UsageError("screen.unit px needs screen.scale (pixels per pt/dp)")
        factor = 1.0 / scale
    elif unit not in ("pt", "dp"):
        raise UsageError("screen.unit must be pt, dp or px")
    try:
        sw, sh = float(screen["w"]) * factor, float(screen["h"]) * factor
    except (KeyError, TypeError, ValueError):
        raise UsageError("screen.w and screen.h are required numbers")
    safe = screen.get("safe", {}) or {}
    st, sb = float(safe.get("top", 0)) * factor, float(safe.get("bottom", 0)) * factor
    sl, sr = float(safe.get("left", 0)) * factor, float(safe.get("right", 0)) * factor
    hand = spec.get("hand", "either")
    mt = float(min_target) if min_target else MIN_TARGET[platform]
    elements = spec.get("elements")
    if not isinstance(elements, list) or not elements:
        raise UsageError("spec.elements must be a non-empty list")

    findings: List[Dict[str, Any]] = []

    def add(sev: str, code: str, el_id: str, msg: str) -> None:
        findings.append({"severity": sev, "code": code, "element": el_id, "message": msg})

    els = []
    for i, el in enumerate(elements):
        if not isinstance(el, dict):
            raise UsageError("element %d must be an object" % i)
        x, y, w, h = _rect(el)
        els.append((el, (x * factor, y * factor, w * factor, h * factor)))

    primaries = 0
    for el, (x, y, w, h) in els:
        eid = str(el.get("id", "?"))
        role = el.get("role", "info")
        touch = bool(el.get("touch", role not in ("info", "decor")))
        decor = bool(el.get("decor", role == "decor"))
        if role == "primary":
            primaries += 1
        # off-screen
        if x < 0 or y < 0 or x + w > sw + 0.01 or y + h > sh + 0.01:
            add("blocker" if touch else "major", "OFFSCREEN", eid, "element extends outside the screen")
        # safe area
        if not decor:
            intrudes = y < st or y + h > sh - sb or x < sl or x + w > sw - sr
            if intrudes:
                add("major" if touch else "minor", "SAFE_AREA", eid,
                    "element intrudes into the unsafe inset (notch, island, cutout, rounded corner or "
                    "home-indicator strip); keep interactive and critical content inside the safe area")
        if touch:
            small = min(w, h)
            if small < mt:
                code = "CLOSE_TOO_SMALL" if role == "close" else "TARGET_SIZE"
                extra = " (a tiny dismiss control is a dark pattern)" if role == "close" else ""
                add("major", code, eid, "touch target %.0fx%.0f is below the %.0f %s minimum%s"
                    % (w, h, mt, "pt" if platform == "ios" else "dp", extra))
            if role == "action" and small < PRIMARY_ACTION_MIN:
                add("minor", "ACTION_SIZE", eid, "repeatedly struck in-game action is %.0f; start at %.0f-90"
                    % (small, PRIMARY_ACTION_MIN))
            zone = thumb_zone(x + w / 2.0, y + h / 2.0, sw, sh, hand)
            frequent = el.get("frequency") == "high" or role in ("primary", "action")
            if frequent and zone == "hard":
                add("major", "THUMB_ZONE", eid, "primary/frequent control sits in the hard-reach zone for hand=%s"
                    % hand)
            elif frequent and zone == "stretch":
                add("minor", "THUMB_ZONE", eid, "primary/frequent control sits in the stretch zone for hand=%s"
                    % hand)
            if role in ("destructive", "purchase") and zone == "easy" and el.get("confirm") is not True:
                add("minor", "DANGER_EASY", eid, "irreversible or spending control in the easiest zone without "
                    "a confirm step; add a confirm or hold-to-confirm")
        # text checks
        text = el.get("text")
        if isinstance(text, str) and el.get("max_chars") is not None and el.get("translatable", True):
            rep = expansion_report(len(text), int(el["max_chars"]))
            if rep["severity"]:
                add(rep["severity"], "TEXT_EXPANSION", eid,
                    "%r (%d chars) may translate to %d-%d chars; container fits %d"
                    % (text, len(text), rep["expected_len_low"], rep["expected_len_high"], rep["max_chars"]))
        font = el.get("font_pt")
        if isinstance(font, (int, float)):
            if font < MIN_FONT:
                add("major", "FONT_SIZE", eid, "font %.1f is below the %.0f pt/sp floor" % (font, MIN_FONT))
            elif el.get("critical") and font < CRITICAL_FONT:
                add("minor", "FONT_SIZE", eid, "gameplay-critical text at %.1f; start at >= %.0f"
                    % (font, CRITICAL_FONT))

    # pairwise checks between touch elements
    touch_els = [(el, r) for el, r in els
                 if bool(el.get("touch", el.get("role", "info") not in ("info", "decor")))]
    for i in range(len(touch_els)):
        for j in range(i + 1, len(touch_els)):
            (ea, ra), (eb, rb) = touch_els[i], touch_els[j]
            ida, idb = str(ea.get("id", "?")), str(eb.get("id", "?"))
            gap = _gap(ra, rb)
            roles = {ea.get("role", "info"), eb.get("role", "info")}
            same_group = ea.get("group") is not None and ea.get("group") == eb.get("group")
            if gap < -0.5:
                add("major", "OVERLAP", "%s+%s" % (ida, idb), "touch targets overlap")
            elif gap < MIN_GAP and not same_group:
                add("minor", "CROWDED", "%s+%s" % (ida, idb), "touch targets are %.1f apart (< %.0f)"
                    % (gap, MIN_GAP))
            danger = roles & {"destructive", "purchase"}
            safe_roles = roles & {"primary", "close", "action"}
            if danger and safe_roles and gap < DANGER_GAP and len(roles) > 1:
                add("major", "DANGER_ADJACENT", "%s+%s" % (ida, idb),
                    "spending/destructive control is %.1f from a primary/close control (< %.0f); "
                    "a slip becomes a purchase or loss" % (max(gap, 0.0), DANGER_GAP))
    if primaries > 1:
        add("minor", "MULTI_PRIMARY", "*", "%d elements marked primary; one primary call to action per screen"
            % primaries)

    counts = {s: sum(1 for f in findings if f["severity"] == s) for s in SEVERITIES}
    order = {s: i for i, s in enumerate(SEVERITIES)}
    findings.sort(key=lambda f: (order[f["severity"]], f["code"], f["element"]))
    verdict = "fail" if counts["blocker"] or counts["major"] else "pass"
    return {
        "screen": spec.get("name", "screen"),
        "platform": platform,
        "hand": hand,
        "logical_size": [round(sw, 1), round(sh, 1)],
        "min_target": mt,
        "counts": counts,
        "findings": findings,
        "verdict": verdict,
    }


def template_spec(platform: str = "ios", hand: str = "either") -> Dict[str, Any]:
    if platform == "android":
        screen = {"w": 412, "h": 915, "unit": "dp", "safe": {"top": 32, "bottom": 24, "left": 0, "right": 0}}
    else:
        screen = {"w": 393, "h": 852, "unit": "pt", "safe": {"top": 59, "bottom": 34, "left": 0, "right": 0}}
    w, h = screen["w"], screen["h"]
    t = MIN_TARGET[platform]
    bar = h - screen["safe"]["bottom"] - 64
    return {
        "name": "home_hub",
        "platform": platform,
        "orientation": "portrait",
        "hand": hand,
        "screen": screen,
        "elements": [
            {"id": "currency_soft", "role": "info", "rect": [16, screen["safe"]["top"] + 8, 110, 36],
             "text": "12,450", "translatable": False, "font_pt": 15},
            {"id": "currency_hard_plus", "role": "secondary", "rect": [w - 140, screen["safe"]["top"] + 6, 124, t],
             "text": "350 +", "translatable": False, "font_pt": 15},
            {"id": "settings", "role": "nav", "rect": [16, screen["safe"]["top"] + 60, t, t]},
            {"id": "event_rail_1", "role": "secondary", "rect": [w - 76, screen["safe"]["top"] + 120, 60, 60]},
            {"id": "play", "role": "primary", "rect": [w / 2 - 110, bar - 92, 220, 76], "text": "Level 12",
             "max_chars": 24, "font_pt": 24},
            {"id": "tab_shop", "role": "nav", "group": "tabbar", "rect": [0, bar, w / 5, 64]},
            {"id": "tab_collection", "role": "nav", "group": "tabbar", "rect": [w / 5, bar, w / 5, 64]},
            {"id": "tab_home", "role": "nav", "group": "tabbar", "rect": [2 * w / 5, bar, w / 5, 64]},
            {"id": "tab_team", "role": "nav", "group": "tabbar", "rect": [3 * w / 5, bar, w / 5, 64]},
            {"id": "tab_events", "role": "nav", "group": "tabbar", "rect": [4 * w / 5, bar, w / 5, 64]},
        ],
    }


# --------------------------------------------------------------------------
# Output helpers
# --------------------------------------------------------------------------
def emit(data: Dict[str, Any], as_json: bool, text_lines: List[str]) -> None:
    if as_json:
        print(json.dumps(data, indent=2, sort_keys=False))
    else:
        print("\n".join(text_lines))


def cmd_contrast(a: argparse.Namespace) -> int:
    rep = contrast_report(a.fg, a.bg, a.large, a.nontext)
    lines = ["contrast %s on %s = %.2f:1" % (a.fg, a.bg, rep["ratio"]),
             "use: %s -> %s" % (rep["use"], "PASS AA" if rep["pass_AA"] else "FAIL AA")]
    lines += ["  %-20s %s" % (k, "pass" if v else "fail") for k, v in rep["verdicts"].items()]
    emit(rep, a.json, lines)
    return 0 if rep["pass_AA"] else 1


def cmd_units(a: argparse.Namespace) -> int:
    rep = convert_units(a.pt, a.dp, a.px, a.mm, a.scale, a.ppi)
    lines = ["%.2f pt/dp = %.2f mm (%s geometry, %.1f logical units/inch)%s"
             % (rep["logical"], rep["mm"], "exact" if rep["exact_geometry"] else "nominal",
                rep["logical_per_inch"], (", %.1f px" % rep["px"]) if "px" in rep else ""),
             "clears iOS 44 pt: %s; clears Android 48 dp: %s"
             % (rep["clears_ios_44pt"], rep["clears_android_48dp"])]
    emit(rep, a.json, lines)
    return 0


def cmd_expansion(a: argparse.Namespace) -> int:
    if a.text is None and a.chars is None:
        raise UsageError("give --text or --chars")
    n = len(a.text) if a.text is not None else int(a.chars)
    rep = expansion_report(n, a.max_chars)
    lines = ["%d source chars -> expect %d-%d chars translated (x%.2f-x%.2f)"
             % (n, rep["expected_len_low"], rep["expected_len_high"], rep["ratio_low"], rep["ratio_high"])]
    if "verdict" in rep:
        lines.append("container %d chars: %s" % (rep["max_chars"], rep["verdict"].upper()))
    lines.append(rep["note"])
    emit(rep, a.json, lines)
    return 1 if rep.get("verdict") == "fail" else 0


def cmd_layout(a: argparse.Namespace) -> int:
    path = Path(a.spec)
    if not path.is_file():
        raise UsageError("spec not found: %s" % path)
    try:
        spec = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise UsageError("spec is not valid JSON: %s" % exc)
    rep = audit_layout(spec, a.min_target)
    lines = ["layout %s (%s, hand=%s, %sx%s): %s" % (rep["screen"], rep["platform"], rep["hand"],
                                                      rep["logical_size"][0], rep["logical_size"][1],
                                                      rep["verdict"].upper()),
             "counts: " + ", ".join("%s=%d" % (k, v) for k, v in rep["counts"].items())]
    for f in rep["findings"]:
        lines.append("  [%s] %s %s: %s" % (f["severity"], f["code"], f["element"], f["message"]))
    emit(rep, a.json, lines)
    return 1 if rep["verdict"] == "fail" else 0


def cmd_template(a: argparse.Namespace) -> int:
    spec = template_spec(a.platform, a.hand)
    text = json.dumps(spec, indent=2) + "\n"
    if a.out:
        Path(a.out).write_text(text, encoding="utf-8")
        print("wrote %s" % a.out)
    else:
        sys.stdout.write(text)
    return 0


# --------------------------------------------------------------------------
# Self-test
# --------------------------------------------------------------------------
def selftest() -> int:
    failures: List[str] = []

    def check(cond: bool, label: str) -> None:
        if not cond:
            failures.append(label)

    # contrast
    check(abs(contrast_ratio("#000000", "#ffffff") - 21.0) < 1e-6, "black/white = 21")
    check(abs(contrast_ratio("#fff", "#fff") - 1.0) < 1e-9, "same colour = 1")
    grey = contrast_report("#777777", "#ffffff")
    check(4.4 < grey["ratio"] < 4.5 and not grey["pass_AA"], "#777 on white fails AA normal")
    check(contrast_report("#777777", "#ffffff", large=True)["pass_AA"], "#777 on white passes AA large")
    check(contrast_report("#767676", "#ffffff")["pass_AA"], "#767676 on white passes AA normal")
    try:
        parse_hex("#12345")
        failures.append("bad hex accepted")
    except UsageError:
        pass
    # units
    u = convert_units(pt=44)
    check(abs(u["mm"] - 6.98) < 0.01 and u["clears_ios_44pt"] and not u["clears_android_48dp"], "44 pt nominal")
    u = convert_units(px=132, scale=3, ppi=460)
    check(abs(u["logical"] - 44) < 1e-9 and u["exact_geometry"] and abs(u["mm"] - 7.29) < 0.01, "132 px @3x 460 ppi")
    u = convert_units(mm=9)
    check(abs(u["logical"] - 56.69) < 0.01, "9 mm nominal")
    try:
        convert_units(px=100)
        failures.append("px without scale accepted")
    except UsageError:
        pass
    # expansion
    check(expansion_band(4) == (2.0, 3.0), "band <=10")
    check(expansion_band(25) == (1.6, 1.8), "band 21-30")
    check(expansion_band(200) == (1.3, 1.3), "band >70")
    r = expansion_report(4, 6)
    check(r["verdict"] == "fail" and r["severity"] == "major", "PLAY in 6 chars fails")
    r = expansion_report(4, 10)
    check(r["verdict"] == "risk", "PLAY in 10 chars risky")
    r = expansion_report(4, 12)
    check(r["verdict"] == "pass", "PLAY in 12 chars passes")
    # zones
    check(thumb_zone(200, 800, 400, 860, "right") == "easy", "bottom centre easy")
    check(thumb_zone(30, 60, 400, 860, "right") == "hard", "top-left hard for right hand")
    check(thumb_zone(360, 300, 400, 860, "right") == "stretch", "upper-right stretch for right hand")
    check(thumb_zone(40, 300, 400, 860, "either") == "hard", "upper-left hard for either")
    check(thumb_zone(60, 300, 860, 400, "two") == "easy", "landscape lower-left easy for two thumbs")
    check(thumb_zone(430, 40, 860, 400, "two") == "hard", "landscape top-centre hard for two thumbs")
    # clean template passes
    clean = audit_layout(template_spec("ios", "either"))
    check(clean["verdict"] == "pass", "ios template passes: %s" % clean["findings"])
    clean_a = audit_layout(template_spec("android", "either"))
    check(clean_a["verdict"] == "pass", "android template passes: %s" % clean_a["findings"])
    # bad fixture
    bad = {
        "name": "bad_reward", "platform": "ios", "hand": "right",
        "screen": {"w": 393, "h": 852, "unit": "pt", "safe": {"top": 59, "bottom": 34}},
        "elements": [
            {"id": "close_x", "role": "close", "rect": [350, 20, 24, 24]},
            {"id": "claim_x2_ad", "role": "primary", "rect": [96, 300, 200, 60], "text": "Claim x2", "max_chars": 9},
            {"id": "claim", "role": "primary", "rect": [96, 364, 200, 30], "font_pt": 9},
            {"id": "buy_gems", "role": "purchase", "rect": [96, 400, 200, 50]},
            {"id": "offscreen", "role": "secondary", "rect": [380, 700, 60, 60]},
        ],
    }
    rep = audit_layout(bad)
    codes = {f["code"] for f in rep["findings"]}
    for needed in ("CLOSE_TOO_SMALL", "SAFE_AREA", "TARGET_SIZE", "THUMB_ZONE", "TEXT_EXPANSION",
                   "FONT_SIZE", "CROWDED", "DANGER_ADJACENT", "MULTI_PRIMARY", "OFFSCREEN"):
        check(needed in codes, "bad fixture flags %s (got %s)" % (needed, sorted(codes)))
    check(rep["verdict"] == "fail", "bad fixture fails")
    # px unit conversion in layout
    px_spec = template_spec("ios", "either")
    px_spec["screen"] = {"w": 1179, "h": 2556, "unit": "px", "scale": 3,
                         "safe": {"top": 177, "bottom": 102, "left": 0, "right": 0}}
    for el in px_spec["elements"]:
        el["rect"] = [v * 3 for v in el["rect"]]
    check(audit_layout(px_spec)["verdict"] == "pass", "px spec at @3x passes")
    try:
        audit_layout({"screen": {"w": 10, "h": 10}, "elements": []})
        failures.append("empty elements accepted")
    except UsageError:
        pass

    if failures:
        for f in failures:
            print("SELFTEST FAIL: %s" % f, file=sys.stderr)
        return 1
    print("ui_audit selftest: ok")
    return 0


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Structural mobile UI checks (mobile-ux skill).")
    p.add_argument("--selftest", action="store_true", help="run built-in fixtures and exit")
    sub = p.add_subparsers(dest="cmd")

    c = sub.add_parser("contrast", help="WCAG contrast ratio")
    c.add_argument("--fg", required=True)
    c.add_argument("--bg", required=True)
    c.add_argument("--large", action="store_true", help="judge as large text (AA 3:1)")
    c.add_argument("--nontext", action="store_true", help="judge as icon/UI boundary (AA 3:1)")
    c.add_argument("--json", action="store_true")
    c.set_defaults(func=cmd_contrast)

    u = sub.add_parser("units", help="pt/dp/px/mm conversion")
    u.add_argument("--pt", type=float)
    u.add_argument("--dp", type=float)
    u.add_argument("--px", type=float)
    u.add_argument("--mm", type=float)
    u.add_argument("--scale", type=float, help="pixels per pt/dp (iOS @2x/@3x; Android density/160)")
    u.add_argument("--ppi", type=float, help="physical pixels per inch of the device")
    u.add_argument("--json", action="store_true")
    u.set_defaults(func=cmd_units)

    e = sub.add_parser("expansion", help="translation length budget")
    e.add_argument("--text")
    e.add_argument("--chars", type=int)
    e.add_argument("--max-chars", type=int, dest="max_chars")
    e.add_argument("--json", action="store_true")
    e.set_defaults(func=cmd_expansion)

    l_ = sub.add_parser("layout", help="audit one screen layout spec")
    l_.add_argument("--spec", required=True)
    l_.add_argument("--min-target", type=float, dest="min_target", help="override the platform minimum")
    l_.add_argument("--json", action="store_true")
    l_.set_defaults(func=cmd_layout)

    t = sub.add_parser("template", help="print an example layout spec")
    t.add_argument("--platform", choices=("ios", "android"), default="ios")
    t.add_argument("--hand", choices=("right", "left", "either", "two", "cradle"), default="either")
    t.add_argument("--out")
    t.set_defaults(func=cmd_template)
    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    if not getattr(args, "func", None):
        parser.print_help(sys.stderr)
        return 2
    try:
        return int(args.func(args))
    except UsageError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows pipes default to the ANSI code page; Claude Code reads UTF-8
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
