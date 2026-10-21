#!/usr/bin/env python3
"""Project dashboard: one self-contained HTML page that shows the state of a game project at a glance.

Sections: features and their five gates, core and meta loops as diagrams, the economy as a flow, bot win-rate and
frame-time trends, what-if results, the code dependency graph (from the project map), the asset gallery with
licences and provenance, and the asset budget. The page works offline: no external scripts, fonts or images; it
follows the viewer's light or dark setting and has a theme toggle.

  dashboard.py [--root DIR] [--out PATH] [--no-map]
  dashboard.py --selftest

Default output: .gamestudio/reports/dashboard.html. Exit codes: 0 written, 2 usage error or no project.
"""
import argparse
import base64
import html
import json
import math
import os
import shutil
import sys
import tempfile
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gslib as G  # noqa: E402

EMBED_MAX_BYTES = 200 * 1024     # thumbnails above this are not embedded
EMBED_TOTAL_BYTES = 4 * 1024 * 1024
IMAGE_MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp",
              ".svg": "image/svg+xml", ".gif": "image/gif"}
GATE_ICON = {"pass": ("good", "✓", "pass"), "fail": ("critical", "✕", "fail"),
             "n/a": ("muted", "–", "n/a"), None: ("muted", "·", "to do")}
ASSET_STATUS = {"approved": ("good", "✓"), "final": ("good", "✓"), "candidate": ("warning", "●"),
                "placeholder": ("muted", "◌"), "rejected": ("critical", "✕")}
VERDICT_STATUS = {"improves": ("good", "✓"), "no clear effect": ("muted", "–"), "unknown": ("muted", "?"),
                  "mixed": ("warning", "◐"), "worsens": ("serious", "↘"), "reject": ("critical", "✕")}

CSS = """
.viz-root{color-scheme:light;--plane:#f9f9f7;--surface:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--muted:#898781;
--grid:#e1e0d9;--axis:#c3c2b7;--ring:rgba(11,11,11,.10);--s1:#2a78d6;--s1wash:rgba(42,120,214,.12);--base:#898781;
--good:#0ca30c;--warning:#fab219;--serious:#ec835a;--critical:#d03b3b;--node:#f0efec}
@media (prefers-color-scheme:dark){:root:where(:not([data-theme="light"])) .viz-root{color-scheme:dark;--plane:#0d0d0d;
--surface:#1a1a19;--ink:#f0efec;--ink2:#c3c2b7;--muted:#898781;--grid:#2c2c2a;--axis:#383835;--ring:rgba(255,255,255,.10);
--s1:#3987e5;--s1wash:rgba(57,135,229,.16);--node:#262624}}
:root[data-theme="dark"] .viz-root{color-scheme:dark;--plane:#0d0d0d;--surface:#1a1a19;--ink:#f0efec;--ink2:#c3c2b7;
--muted:#898781;--grid:#2c2c2a;--axis:#383835;--ring:rgba(255,255,255,.10);--s1:#3987e5;--s1wash:rgba(57,135,229,.16);--node:#262624}
*{box-sizing:border-box}
html,body{margin:0}
body.viz-root{background:var(--plane);color:var(--ink);font:14px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif}
.wrap{max-width:1200px;margin:0 auto;padding:24px 16px 48px}
header{display:flex;flex-wrap:wrap;gap:16px;align-items:flex-end;justify-content:space-between;margin-bottom:16px}
h1{font-size:24px;margin:0 0 4px;font-weight:650}
h2{font-size:16px;margin:0 0 4px;font-weight:620}
p{margin:0}
.sub{color:var(--ink2);max-width:720px}
.muted{color:var(--muted);font-size:12px}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}
.chip{border:1px solid var(--ring);border-radius:999px;padding:2px 10px;font-size:12px;color:var(--ink2);background:var(--surface)}
.hero{text-align:right}
.hero .v{font-size:48px;font-weight:650;line-height:1}
nav{display:flex;flex-wrap:wrap;gap:4px 14px;margin:8px 0 16px;font-size:13px}
nav a{color:var(--ink2);text-decoration:none;border-bottom:1px solid var(--axis)}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin-bottom:16px}
.card{background:var(--surface);border:1px solid var(--ring);border-radius:10px;padding:16px;min-width:0}
.tile .l{color:var(--ink2);font-size:13px}
.tile .v{font-size:26px;font-weight:620;margin-top:2px}
.tile .d{color:var(--muted);font-size:12px}
section.card{margin-bottom:16px}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,520px),1fr));gap:16px}
.scroll{overflow-x:auto;max-width:100%}
.scroll svg{max-width:none}
table{border-collapse:collapse;width:100%;font-size:13px}
th,td{text-align:left;padding:6px 8px;border-bottom:1px solid var(--grid);vertical-align:top}
th{color:var(--ink2);font-weight:600;white-space:nowrap}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
.st{white-space:nowrap}
.st i{font-style:normal;font-weight:700;margin-right:4px}
.good i{color:var(--good)}.warning i{color:var(--warning)}.serious i{color:var(--serious)}
.critical i{color:var(--critical)}.muted i{color:var(--muted)}
.meter{height:8px;border-radius:4px;background:var(--s1wash);overflow:hidden;margin-top:8px}
.meter>span{display:block;height:100%;border-radius:4px;background:var(--s1)}
.meter.warn>span{background:var(--warning)}.meter.over>span{background:var(--critical)}
svg{display:block;max-width:100%;height:auto;overflow:visible}
svg text{fill:var(--ink2);font:12px system-ui,-apple-system,"Segoe UI",sans-serif}
svg .t-muted{fill:var(--muted);font-size:11px}
svg .t-ink{fill:var(--ink)}
.gridline{stroke:var(--grid);stroke-width:1}
.axis{stroke:var(--axis);stroke-width:1}
.series{fill:none;stroke:var(--s1);stroke-width:2;stroke-linejoin:round;stroke-linecap:round}
.dot{fill:var(--s1);stroke:var(--surface);stroke-width:2}
.band{fill:var(--s1wash)}
.ref{stroke:var(--muted);stroke-width:1}
.slot .hit{fill:transparent}
.slot .cross{stroke:var(--axis);stroke-width:1;opacity:0}
.slot:hover .cross{opacity:1}
.node{fill:var(--node);stroke:var(--ring);stroke-width:1}
.edge{fill:none;stroke:var(--muted);stroke-opacity:.55}
.edge:hover{stroke:var(--s1);stroke-opacity:1}
.arrow{fill:var(--muted)}
.rb-base{fill:var(--base)}.rb-var{fill:var(--s1)}
.gallery{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:12px}
.asset{border:1px solid var(--ring);border-radius:8px;overflow:hidden;background:var(--plane)}
.asset .th{height:110px;display:flex;align-items:center;justify-content:center;background:var(--node)}
.asset .th img{max-width:100%;max-height:110px;object-fit:contain;image-rendering:auto}
.asset .meta{padding:8px;font-size:12px;color:var(--ink2)}
.asset .meta b{color:var(--ink);font-weight:600;word-break:break-all}
.legend{display:flex;flex-wrap:wrap;gap:12px;font-size:12px;color:var(--ink2);margin:6px 0}
.key{display:inline-block;width:14px;height:8px;border-radius:2px;margin-right:6px;vertical-align:middle}
details{margin-top:8px}summary{cursor:pointer;color:var(--ink2);font-size:12px}
.tip{position:fixed;z-index:10;pointer-events:none;background:var(--ink);color:var(--surface);font-size:12px;
padding:6px 8px;border-radius:6px;max-width:320px;white-space:pre-line}
button.theme{font:inherit;font-size:12px;color:var(--ink2);background:var(--surface);border:1px solid var(--ring);
border-radius:999px;padding:4px 12px;cursor:pointer}
.empty{color:var(--muted);font-size:13px;padding:8px 0}
"""

JS = """
(function(){
var tip=document.createElement('div');tip.className='tip';tip.hidden=true;document.body.appendChild(tip);
function show(t,x,y){tip.textContent=t.getAttribute('data-tip');tip.hidden=false;place(x,y);}
function place(x,y){var w=tip.offsetWidth,h=tip.offsetHeight,X=x+14,Y=y+14;
if(X+w>innerWidth-8)X=x-w-14;if(Y+h>innerHeight-8)Y=y-h-14;tip.style.left=Math.max(8,X)+'px';tip.style.top=Math.max(8,Y)+'px';}
document.addEventListener('mouseover',function(e){var t=e.target.closest&&e.target.closest('[data-tip]');
if(t)show(t,e.clientX,e.clientY);else tip.hidden=true;});
document.addEventListener('mousemove',function(e){if(!tip.hidden)place(e.clientX,e.clientY);});
document.addEventListener('focusin',function(e){var t=e.target.closest&&e.target.closest('[data-tip]');
if(t){var r=t.getBoundingClientRect();show(t,r.right,r.top);}});
document.addEventListener('focusout',function(){tip.hidden=true;});
var b=document.getElementById('theme');if(b)b.addEventListener('click',function(){var r=document.documentElement;
var cur=r.getAttribute('data-theme')||(matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light');
r.setAttribute('data-theme',cur==='dark'?'light':'dark');});
})();
"""


def esc(x: Any) -> str:
    return html.escape("" if x is None else str(x), quote=True)


def compact(v: Any, digits: int = 3) -> str:
    if not isinstance(v, (int, float)) or isinstance(v, bool):
        return esc(v)
    a = abs(v)
    if a >= 1e6:
        return "%.3gM" % (v / 1e6)
    if a >= 1e4:
        return "%.3gK" % (v / 1e3)
    if float(v).is_integer():
        return "{:,}".format(int(v))
    return ("%." + str(digits) + "g") % v


def status(kind: str, icon: str, label: str) -> str:
    return '<span class="st %s"><i aria-hidden="true">%s</i>%s</span>' % (kind, icon, esc(label))


def _mtime(p: Path) -> str:
    return datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d %H:%M")


def _load(p: Path) -> Any:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


# --------------------------------------------------------------------------
# data
# --------------------------------------------------------------------------

def collect(root: Path, with_map: bool = True) -> Dict[str, Any]:
    gsd = G.gs_dir(root)
    d: Dict[str, Any] = {"root": root, "generated": datetime.now().strftime("%Y-%m-%d %H:%M")}
    d["config"] = _load(gsd / "config.json") or {}
    d["contract"] = _load(gsd / "contract.json") or {}
    d["features"] = (_load(gsd / "features.json") or {}).get("features", [])
    d["budget"] = _load(gsd / "budget.json") or {}
    d["assets"] = (_load(gsd / "assets" / "manifest.json") or {}).get("assets", [])
    bots, perf = [], []
    cands = list(gsd.glob("playtests/*.json")) + list(gsd.glob("evidence/*/*.json")) + list(gsd.glob("reports/*.json"))
    for p in sorted(cands, key=lambda q: q.stat().st_mtime):
        doc = _load(p)
        if not isinstance(doc, dict):
            continue
        m = doc.get("metrics")
        if isinstance(m, dict) and doc.get("mode") == "bot" and isinstance(m.get("win_rate"), (int, float)):
            bots.append({"t": _mtime(p), "win_rate": m["win_rate"], "session": m.get("avg_session_sec"),
                         "file": G.rel_to_root(p, root), "feature": doc.get("feature_id")})
        fm = doc.get("frame_ms")
        if isinstance(fm, dict) and isinstance(fm.get("p95"), (int, float)):
            budget = (doc.get("budgets") or {}).get("frame_ms_p95") if isinstance(doc.get("budgets"), dict) else None
            perf.append({"t": _mtime(p), "p95": fm["p95"], "budget": budget, "file": G.rel_to_root(p, root),
                         "headless": "headless" in json.dumps(doc.get("device", "")) or "headless" in p.name})
    d["bots"], d["perf"] = bots, perf
    runs = []
    for p in sorted(gsd.glob("whatif/*.json"), key=lambda q: q.stat().st_mtime, reverse=True)[:10]:
        doc = _load(p)
        if isinstance(doc, dict) and isinstance(doc.get("metrics"), dict):
            doc["_file"] = G.rel_to_root(p, root)
            runs.append(doc)
    d["whatif"] = runs
    model = None
    ref = ((d["contract"].get("economy") or {}).get("model_ref") or "")
    for p in ([root / ref] if ref else []) + sorted(gsd.glob("economy/*.json")):
        doc = _load(p)
        if isinstance(doc, dict) and isinstance(doc.get("nodes"), list):
            model = doc
            break
    d["economy"] = model
    d["map"] = None
    if with_map:
        try:
            import project_map
            d["map"] = project_map.load(root, refresh=True)
        except Exception as exc:  # noqa: BLE001 - the dashboard must render without a map
            d["map_error"] = str(exc)
    return d


# --------------------------------------------------------------------------
# charts
# --------------------------------------------------------------------------

def nice_max(v: float) -> float:
    if v <= 0:
        return 1.0
    e = 10 ** math.floor(math.log10(v))
    for m in (1, 2, 2.5, 5, 10):
        if v <= m * e:
            return m * e
    return 10 * e


def line_chart(points: List[Tuple[str, float, str]], ymax: Optional[float], fmt: str, band: Optional[Tuple[float, float]] = None,
               ref: Optional[Tuple[float, str]] = None, w: int = 560, h: int = 220) -> str:
    """points: (x label, value, tooltip). One series, so no legend: the card title names it."""
    pl, pr, pt, pb = 44, 16, 12, 28
    iw, ih = w - pl - pr, h - pt - pb
    vals = [p[1] for p in points]
    top = ymax if ymax is not None else nice_max(max(vals + [ref[0] if ref else 0, band[1] if band else 0]) * 1.1)
    n = len(points)

    def x(i: int) -> float:
        return pl + (iw * (i / (n - 1)) if n > 1 else iw / 2)

    def y(v: float) -> float:
        return pt + ih - ih * (min(max(v, 0), top) / top)
    out = ['<svg viewBox="0 0 %d %d" role="img" aria-label="line chart">' % (w, h)]
    if band:
        out.append('<rect class="band" x="%d" y="%.1f" width="%d" height="%.1f"/>' % (pl, y(band[1]), iw, y(band[0]) - y(band[1])))
        out.append('<text class="t-muted" x="%d" y="%.1f" text-anchor="end">target</text>' % (w - pr, y(band[1]) - 4))
    for k in range(5):
        v = top * k / 4
        out.append('<line class="gridline" x1="%d" x2="%d" y1="%.1f" y2="%.1f"/>' % (pl, w - pr, y(v), y(v)))
        out.append('<text class="t-muted" x="%d" y="%.1f" text-anchor="end">%s</text>' % (pl - 6, y(v) + 4, fmt % v))
    out.append('<line class="axis" x1="%d" x2="%d" y1="%.1f" y2="%.1f"/>' % (pl, w - pr, y(0), y(0)))
    if ref:
        out.append('<line class="ref" x1="%d" x2="%d" y1="%.1f" y2="%.1f"/>' % (pl, w - pr, y(ref[0]), y(ref[0])))
        out.append('<text class="t-muted" x="%d" y="%.1f">%s</text>' % (pl + 4, y(ref[0]) - 4, esc(ref[1])))
    step = max(1, n // 6)
    for i, p in enumerate(points):
        if i % step == 0 or i == n - 1:
            out.append('<text class="t-muted" x="%.1f" y="%d" text-anchor="middle">%s</text>' % (x(i), h - 8, esc(p[0][5:10])))
    slot_w = iw / max(1, n - 1) if n > 1 else iw
    for i, p in enumerate(points):
        out.append('<g class="slot"><line class="cross" x1="%.1f" x2="%.1f" y1="%d" y2="%.1f"/>'
                   '<rect class="hit" x="%.1f" y="%d" width="%.1f" height="%d" data-tip="%s" tabindex="0"/></g>'
                   % (x(i), x(i), pt, y(0), x(i) - slot_w / 2, pt, slot_w, ih, esc(p[2])))
    if n > 1:
        out.append('<polyline class="series" points="%s"/>' % " ".join("%.1f,%.1f" % (x(i), y(p[1])) for i, p in enumerate(points)))
    for i, p in enumerate(points):
        out.append('<circle class="dot" cx="%.1f" cy="%.1f" r="4" pointer-events="none"/>' % (x(i), y(p[1])))
    last = points[-1]
    out.append('<text class="t-ink" x="%.1f" y="%.1f" text-anchor="end">%s</text>' % (x(n - 1), y(last[1]) - 10, fmt % last[1]))
    out.append("</svg>")
    return "".join(out)


def range_bar(b: Dict[str, Any], v: Dict[str, Any], target: Optional[List[float]], w: int = 240, h: int = 30) -> str:
    """Current (gray) and proposed (blue) values with their intervals over a shaded target band."""
    vals = [b["mean"], v["mean"], b.get("lo", b["mean"]), b.get("hi", b["mean"]), v.get("lo", v["mean"]), v.get("hi", v["mean"])]
    if target:
        vals += list(target)
    lo, hi = min(vals), max(vals)
    if hi - lo < 1e-9:
        lo, hi = lo - 1, hi + 1
    pad = (hi - lo) * 0.08
    lo, hi = lo - pad, hi + pad

    def x(val: float) -> float:
        return 6 + (w - 12) * (val - lo) / (hi - lo)
    out = ['<svg viewBox="0 0 %d %d" width="%d" height="%d" role="img" aria-label="current vs proposed">' % (w, h, w, h)]
    if target:
        out.append('<rect class="band" x="%.1f" y="2" width="%.1f" height="%d" rx="3"/>' % (x(target[0]), max(2, x(target[1]) - x(target[0])), h - 4))
    for s, cls, yy in ((b, "rb-base", 10), (v, "rb-var", 21)):
        a, z = x(s.get("lo", s["mean"])), x(s.get("hi", s["mean"]))
        out.append('<rect class="%s" x="%.1f" y="%d" width="%.1f" height="2" rx="1" opacity=".6"/>' % (cls, a, yy - 1, max(1.5, z - a)))
        out.append('<circle class="%s" cx="%.1f" cy="%d" r="4" stroke="var(--surface)" stroke-width="2"/>' % (cls, x(s["mean"]), yy))
    out.append("</svg>")
    return "".join(out)


def _wrap(text: str, width: int, lines: int) -> List[str]:
    words, out, cur = str(text).split(), [], ""
    for wd in words:
        if len(cur) + len(wd) + 1 > width and cur:
            out.append(cur)
            cur = wd
        else:
            cur = (cur + " " + wd).strip()
    if cur:
        out.append(cur)
    if len(out) > lines:
        out = out[:lines]
        out[-1] = out[-1][: max(0, width - 1)].rstrip() + "…"
    return out


def loop_svg(loop: Dict[str, Any]) -> str:
    steps = [s for s in loop.get("steps", []) if isinstance(s, dict) and s.get("id")][:10]
    if not steps:
        return '<p class="empty">No steps.</p>'
    n = len(steps)
    bw, bh = 176, 58
    # adjacent boxes need their centres at least a box width plus a gap apart on the circle
    r = 0 if n == 1 else (bh + 50) / 2 + 20 if n == 2 else max(100.0, (bw + 50) / (2 * math.sin(math.pi / n)))
    w, h = 2 * r + bw + 140, 2 * r + bh + 40
    cx, cy = w / 2, h / 2
    pos = {}
    for i, s in enumerate(steps):
        a = -math.pi / 2 + 2 * math.pi * i / n
        pos[s["id"]] = (cx + r * math.cos(a), cy + r * math.sin(a))
    w, h = int(w), int(h)
    out = ['<svg viewBox="0 0 %d %d" width="%d" role="img" aria-label="%s">' % (w, h, w, esc(loop.get("name") or loop.get("id"))),
           '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
           '<path class="arrow" d="M0,0 L10,5 L0,10 z"/></marker></defs>']
    exits = []
    for s in steps:
        nxt = s.get("next")
        targets = nxt if isinstance(nxt, list) else ([nxt] if nxt else [])
        x1, y1 = pos[s["id"]]
        for t in targets:
            t = str(t)
            if t in pos:
                x2, y2 = pos[t]
                dx, dy = x2 - x1, y2 - y1
                dist = math.hypot(dx, dy) or 1
                kx = min((bw / 2 + 6) / abs(dx) if dx else 1e9, (bh / 2 + 6) / abs(dy) if dy else 1e9)
                sx, sy = x1 + dx * min(kx, 0.45), y1 + dy * min(kx, 0.45)
                ex, ey = x2 - dx * min(kx, 0.45), y2 - dy * min(kx, 0.45)
                mx, my = (sx + ex) / 2 + (-dy / dist) * 18, (sy + ey) / 2 + (dx / dist) * 18
                out.append('<path class="edge" stroke-width="1.5" d="M%.1f,%.1f Q%.1f,%.1f %.1f,%.1f" marker-end="url(#ah)"/>'
                           % (sx, sy, mx, my, ex, ey))
            else:
                exits.append((s["id"], t))
    for s in steps:
        x0, y0 = pos[s["id"]]
        reward = s.get("reward")
        rtxt = "" if reward in (None, "", {}) else (", ".join("%s %s" % (k, v) for k, v in reward.items())
                                                    if isinstance(reward, dict) else str(reward))
        tip = "%s: %s%s" % (s["id"], s.get("action", ""), ("\nreward: " + rtxt) if rtxt else "")
        out.append('<g data-tip="%s" tabindex="0"><rect class="node" x="%.1f" y="%.1f" width="%d" height="%d" rx="8"/>'
                   % (esc(tip), x0 - bw / 2, y0 - bh / 2, bw, bh))
        lines = _wrap(s.get("action", ""), 26, 2)
        for j, ln in enumerate(lines):
            out.append('<text class="t-ink" x="%.1f" y="%.1f" text-anchor="middle">%s</text>' % (x0, y0 - 8 + j * 15, esc(ln)))
        if rtxt:
            out.append('<text class="t-muted" x="%.1f" y="%.1f" text-anchor="middle">%s</text>'
                       % (x0, y0 + 22, esc(_wrap("+ " + rtxt, 30, 1)[0])))
        out.append("</g>")
    for k, (sid, t) in enumerate(exits[:4]):
        x0, y0 = pos[sid]
        out.append('<text class="t-muted" x="%.1f" y="%.1f" text-anchor="middle">→ %s</text>'
                   % (x0, y0 + bh / 2 + 14, esc(t.replace("loop:", "loop "))))
    out.append("</svg>")
    return "".join(out)


def economy_svg(model: Dict[str, Any]) -> str:
    nodes = [n for n in model.get("nodes", []) if isinstance(n, dict) and n.get("id")]
    res = [r.get("id") for r in model.get("resources", []) if isinstance(r, dict) and r.get("id")]
    srcs = [n for n in nodes if n.get("kind") == "source"][:24]
    right = [n for n in nodes if n.get("kind") in ("sink", "converter", "gate")][:24]
    res += [n["id"] for n in nodes if n.get("kind") == "pool" and n["id"] not in res]
    res = res[:24]
    if not res:
        return '<p class="empty">The economy model has no resources.</p>'
    bw, bh, gap = 170, 26, 8
    cols = [srcs, res, right]
    hmax = max(len(c) for c in cols) * (bh + gap) + 40
    w = 3 * bw + 2 * 150 + 80  # room for the kind label beside the right column
    xs = [0, bw + 150, 2 * (bw + 150)]

    def ys(col: List[Any]) -> Dict[str, float]:
        total = len(col) * (bh + gap)
        y0 = 30 + (hmax - 30 - total) / 2
        return {(c if isinstance(c, str) else c["id"]): y0 + i * (bh + gap) for i, c in enumerate(col)}
    y_src, y_res, y_right = ys(srcs), ys(res), ys(right)
    out = ['<svg viewBox="0 0 %d %d" width="%d" role="img" aria-label="economy flow">' % (w, hmax, w),
           '<text class="t-muted" x="0" y="14">sources</text><text class="t-muted" x="%d" y="14">resources</text>'
           '<text class="t-muted" x="%d" y="14">sinks, converters, gates</text>' % (xs[1], xs[2])]
    for s in srcs:
        for r, amt in (s.get("outputs") or {}).items():
            if r in y_res:
                x1, y1, x2, y2 = xs[0] + bw, y_src[s["id"]] + bh / 2, xs[1], y_res[r] + bh / 2
                out.append('<path class="edge" stroke-width="1.5" d="M%.1f,%.1f C%.1f,%.1f %.1f,%.1f %.1f,%.1f" data-tip="%s"/>'
                           % (x1, y1, x1 + 70, y1, x2 - 70, y2, x2, y2, esc("%s → %s: %s (%s)" % (s["id"], r, amt, s.get("trigger", "")))))
    for k in right:
        for r, amt in (k.get("inputs") or k.get("requires") or {}).items():
            if r in y_res and isinstance(amt, (int, float)):
                x1, y1, x2, y2 = xs[1] + bw, y_res[r] + bh / 2, xs[2], y_right[k["id"]] + bh / 2
                out.append('<path class="edge" stroke-width="1.5" d="M%.1f,%.1f C%.1f,%.1f %.1f,%.1f %.1f,%.1f" data-tip="%s"/>'
                           % (x1, y1, x1 + 70, y1, x2 - 70, y2, x2, y2, esc("%s → %s: %s (%s)" % (r, k["id"], amt, k.get("trigger", "")))))
    for col, x0, ymap, kind in ((srcs, xs[0], y_src, "source"), (res, xs[1], y_res, "resource"), (right, xs[2], y_right, "")):
        for c in col:
            cid = c if isinstance(c, str) else c["id"]
            label = cid
            kind_txt = "" if isinstance(c, str) or c.get("kind") in ("source", "sink") else c.get("kind", "")
            tip = cid if isinstance(c, str) else json.dumps({k: v for k, v in c.items() if k != "note"})[:300]
            out.append('<g data-tip="%s" tabindex="0"><rect class="node" x="%d" y="%.1f" width="%d" height="%d" rx="6"/>'
                       '<text class="t-ink" x="%d" y="%.1f">%s</text>%s</g>'
                       % (esc(tip), x0, ymap[cid], bw, bh, x0 + 8, ymap[cid] + 17, esc(label[:24]),
                          ('<text class="t-muted" x="%d" y="%.1f">%s</text>' % (x0 + bw + 6, ymap[cid] + 17, esc(kind_txt))) if kind_txt else ""))
    out.append("</svg>")
    return "".join(out)


def deps_svg(mapdoc: Dict[str, Any]) -> Tuple[str, List[Tuple[int, str]]]:
    files = mapdoc.get("files", {})
    code = ("script", "scene", "resource", "shader", "test", "tool", "data")

    def group(rel: str) -> str:
        parts = rel.split("/")[:-1]
        if not parts:
            return "(root)"
        if parts[0] == "Assets" and len(parts) > 2 and parts[1].startswith("_"):
            return "/".join(parts[:3])
        if parts[0] in ("Assets", "tests", "tools", "src", "addons", "Source") and len(parts) > 1:
            return "/".join(parts[:2])
        return parts[0]
    counts = Counter(group(r) for r, i in files.items() if i.get("kind") in code and not r.endswith(".meta"))
    if len(counts) > 22:
        keep = {g for g, _ in counts.most_common(21)}
        merged = Counter()
        for g, c in counts.items():
            merged[g if g in keep else "(other)"] += c
        counts = merged
    else:
        keep = set(counts)

    def grp(rel: str) -> str:
        g = group(rel)
        return g if g in keep else "(other)"
    gedges: Counter = Counter()
    rdeps: Counter = Counter()
    for a, b, k in mapdoc.get("edges", []):
        if a.startswith("file:") and b.startswith("file:"):
            rdeps[b[5:]] += 1
            ga, gb = grp(a[5:]), grp(b[5:])
            if ga != gb and ga in counts and gb in counts:
                gedges[(ga, gb)] += 1
    hot = sorted(((n, r) for r, n in rdeps.items()), reverse=True)[:10]
    if not counts:
        return '<p class="empty">No code files in the map.</p>', hot
    groups = sorted(counts)
    outs: Dict[str, List[str]] = {g: [] for g in groups}
    for (a, b) in gedges:
        outs[a].append(b)
    layer: Dict[str, int] = {}

    def depth(g: str, stack: set) -> int:
        if g in layer:
            return layer[g]
        if g in stack:
            return 0
        stack.add(g)
        dd = max([depth(h, stack) + 1 for h in outs[g]] + [0])
        stack.discard(g)
        layer[g] = dd
        return dd
    for g in groups:
        depth(g, set())
    cols: Dict[int, List[str]] = {}
    for g in groups:
        cols.setdefault(layer[g], []).append(g)
    bw, bh, cgap, rgap = 168, 40, 70, 14
    ncol = max(cols) + 1
    maxrows = max(len(v) for v in cols.values())
    w, h = ncol * bw + (ncol - 1) * cgap, maxrows * (bh + rgap) + 10
    pos = {}
    for c, gs in cols.items():
        off = (h - len(gs) * (bh + rgap)) / 2
        for i, g in enumerate(gs):
            pos[g] = (c * (bw + cgap), off + i * (bh + rgap))
    w, h = int(w), int(h)
    out = ['<svg viewBox="0 0 %d %d" width="%d" role="img" aria-label="dependency graph by folder">' % (w, h, w),
           '<defs><marker id="dh" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">'
           '<path class="arrow" d="M0,0 L10,5 L0,10 z"/></marker></defs>']
    for (a, b), n in gedges.most_common(80):
        xa, ya = pos[a]
        xb, yb = pos[b]
        if xa > xb:
            x1, y1, x2, y2 = xa, ya + bh / 2, xb + bw, yb + bh / 2
        else:
            x1, y1, x2, y2 = xa + bw, ya + bh / 2, xb + (0 if xb > xa else bw), yb + bh / 2
        sw = 1 + math.log2(n)
        mx = (x1 + x2) / 2
        out.append('<path class="edge" stroke-width="%.1f" d="M%.1f,%.1f C%.1f,%.1f %.1f,%.1f %.1f,%.1f" marker-end="url(#dh)" '
                   'data-tip="%s"/>' % (sw, x1, y1, mx, y1, mx, y2, x2, y2, esc("%s uses %s: %d reference%s" % (a, b, n, "" if n == 1 else "s"))))
    for g, (x0, y0) in pos.items():
        out.append('<g data-tip="%s" tabindex="0"><rect class="node" x="%.1f" y="%.1f" width="%d" height="%d" rx="8"/>'
                   '<text class="t-ink" x="%.1f" y="%.1f">%s</text><text class="t-muted" x="%.1f" y="%.1f">%d file%s</text></g>'
                   % (esc("%s: %d files" % (g, counts[g])), x0, y0, bw, bh, x0 + 10, y0 + 17, esc(g[-24:]), x0 + 10,
                      y0 + 32, counts[g], "" if counts[g] == 1 else "s"))
    out.append("</svg>")
    return "".join(out), hot


# --------------------------------------------------------------------------
# page
# --------------------------------------------------------------------------

def render(d: Dict[str, Any]) -> str:
    cfg, con = d["config"], d["contract"]
    meta = con.get("meta") or {}
    title = meta.get("title") or (cfg.get("project") or {}).get("title") or d["root"].name
    feats = d["features"]
    done = sum(1 for f in feats if f.get("status") == "done")
    gate_total = len(feats) * len(G.GATES)
    gate_ok = sum(1 for f in feats for g in G.GATES if (f.get("gates") or {}).get(g) in ("pass", "n/a"))
    bud = d["budget"]
    cap = bud.get("cap_usd") or (cfg.get("budgets") or {}).get("asset_usd_cap") or 0
    spent = bud.get("spent_usd") or 0
    chips = [cfg.get("engine") or meta.get("engine"), ", ".join(cfg.get("platforms") or meta.get("platforms") or []),
             ", ".join((cfg.get("input") or meta.get("input") or [])), cfg.get("orientation") or meta.get("orientation"),
             "tier " + str(cfg.get("tier")) if cfg.get("tier") else None,
             None if str(meta.get("genre", "")).startswith("TBD") else meta.get("genre")]
    p = ['<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
         "<title>%s dashboard</title><style>%s</style></head>" % (esc(title), CSS),
         '<body class="viz-root"><div class="wrap"><header><div><h1>%s</h1><p class="sub">%s</p><div class="chips">%s</div></div>'
         % (esc(title), esc(meta.get("logline") if meta.get("logline", "").find("TBD") != 0 else ""),
            "".join('<span class="chip">%s</span>' % esc(c) for c in chips if c)),
         '<div class="hero"><div class="muted">Features done</div><div class="v">%d<span class="muted" style="font-size:20px"> / %d</span></div>'
         '<div class="muted">generated %s · <button class="theme" id="theme" type="button">Theme</button></div></div></header>'
         % (done, len(feats), esc(d["generated"]))]
    sections = [("features", "Features"), ("loops", "Loops"), ("economy", "Economy"), ("trends", "Trends"),
                ("whatif", "What-if"), ("deps", "Dependencies"), ("assets", "Assets"), ("budget", "Budget")]
    p.append("<nav>%s</nav>" % "".join('<a href="#%s">%s</a>' % s for s in sections))
    bots, perf = d["bots"], d["perf"]
    tiles = [("Gates passing", "%d%%" % round(100 * gate_ok / gate_total) if gate_total else "–",
              "%d of %d gate results pass or n/a" % (gate_ok, gate_total)),
             ("Asset budget", "$%s" % compact(spent), "of $%s cap" % compact(cap)),
             ("Bot win rate", "%.0f%%" % (100 * bots[-1]["win_rate"]) if bots else "–",
              ("latest of %d runs" % len(bots)) if bots else "no bot runs yet"),
             ("Frame time p95", "%s ms" % compact(perf[-1]["p95"]) if perf else "–",
              ("latest of %d probes" % len(perf)) if perf else "no perf reports yet"),
             ("What-if runs", str(len(d["whatif"])), (d["whatif"][0]["verdict"] + " (latest)") if d["whatif"] else "none yet")]
    p.append('<div class="tiles">%s</div>' % "".join(
        '<div class="card tile"><div class="l">%s</div><div class="v">%s</div><div class="d">%s</div>%s</div>'
        % (esc(l), esc(v), esc(dd), _meter(spent, cap) if l == "Asset budget" else "") for l, v, dd in tiles))

    # features
    rows = []
    for f in feats:
        gates = f.get("gates") or {}
        cells = "".join("<td>%s</td>" % status(*GATE_ICON.get(gates.get(g), GATE_ICON[None])) for g in G.GATES)
        st = f.get("status", "todo")
        sk = {"done": ("good", "✓"), "in_progress": ("warning", "◐"), "blocked": ("critical", "✕")}.get(st, ("muted", "·"))
        rows.append("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td>%s</tr>"
                    % (esc(f.get("id")), esc(f.get("title")), esc(f.get("priority", "")), status(sk[0], sk[1], st.replace("_", " ")), cells))
    p.append('<section class="card" id="features"><h2>Features and the five gates</h2><p class="muted">A feature is done only '
             'when every gate passes with evidence on disk, or is n/a with a note.</p>')
    if rows:
        p.append('<div class="scroll"><table><thead><tr><th>ID</th><th>Feature</th><th>Priority</th><th>Status</th>%s</tr></thead>'
                 '<tbody>%s</tbody></table></div>' % ("".join("<th>%s</th>" % g for g in G.GATES), "".join(rows)))
    else:
        p.append('<p class="empty">No features yet: gs.py feature add.</p>')
    p.append("</section>")

    # loops
    loops = [lp for lp in (con.get("loops") or []) if isinstance(lp, dict)]
    p.append('<section class="card" id="loops"><h2>Loops</h2>')
    if loops:
        p.append('<div class="grid2">%s</div>' % "".join(
            '<div><p><b>%s</b> <span class="muted">%s · %s</span></p>%s</div>'
            % (esc(lp.get("name") or lp.get("id")), esc(lp.get("type", "")), esc(lp.get("period", "")), loop_svg(lp))
            for lp in loops[:4]))
    else:
        p.append('<p class="empty">The contract has no loops yet (contract.json "loops").</p>')
    p.append("</section>")

    # economy
    p.append('<section class="card" id="economy"><h2>Economy</h2>')
    if d["economy"]:
        p.append('<p class="muted">%s. Hover a line for amounts and triggers.</p><div class="scroll">%s</div>'
                 % (esc(d["economy"].get("name", "economy model")), economy_svg(d["economy"])))
    else:
        p.append('<p class="empty">No economy model (.gamestudio/economy/*.json or contract economy.model_ref).</p>')
    p.append("</section>")

    # trends
    p.append('<section class="card" id="trends"><h2>Trends</h2><div class="grid2">')
    diff = ((con.get("progression") or {}).get("difficulty") or {}).get("target_win_rate")
    band = (max(0.0, diff - 0.05), min(1.0, diff + 0.05)) if isinstance(diff, (int, float)) and diff > 0 else None
    if len(bots) >= 1:
        pts = [(b["t"], 100 * b["win_rate"], "%s\nwin rate %.0f%%\n%s" % (b["t"], 100 * b["win_rate"], b["file"])) for b in bots[-30:]]
        pband = (100 * band[0], 100 * band[1]) if band else None
        p.append('<div><p><b>Bot win rate</b> <span class="muted">per bot report, oldest to newest</span></p>%s%s</div>'
                 % (line_chart(pts, 100.0, "%.0f%%", pband),
                    "<details><summary>Table</summary>%s</details>" % _table(["time", "win rate", "file"], [(b["t"], "%.1f%%" % (100 * b["win_rate"]), b["file"]) for b in bots[-30:]])))
    else:
        p.append('<div><p><b>Bot win rate</b></p><p class="empty">No bot reports yet (runner.gd --mode=bot writes them).</p></div>')
    budget_ms = ((con.get("technical") or {}).get("perf_budgets") or {}).get("frame_ms_p95")
    if perf:
        pts = [(q["t"], q["p95"], "%s\np95 %s ms%s\n%s" % (q["t"], compact(q["p95"]), " (headless)" if q["headless"] else "", q["file"])) for q in perf[-30:]]
        ref = (float(budget_ms), "budget %s ms" % compact(budget_ms)) if isinstance(budget_ms, (int, float)) and budget_ms > 0 else None
        p.append('<div><p><b>Frame time p95</b> <span class="muted">milliseconds, lower is better</span></p>%s%s</div>'
                 % (line_chart(pts, None, "%.0f", None, ref),
                    "<details><summary>Table</summary>%s</details>" % _table(["time", "p95 ms", "file"], [(q["t"], compact(q["p95"]), q["file"]) for q in perf[-30:]])))
    else:
        p.append('<div><p><b>Frame time p95</b></p><p class="empty">No perf reports yet (the perf gate writes them).</p></div>')
    p.append("</div></section>")

    # what-if
    p.append('<section class="card" id="whatif"><h2>What-if predictions</h2>'
             '<div class="legend"><span><span class="key" style="background:var(--base)"></span>current</span>'
             '<span><span class="key" style="background:var(--s1)"></span>proposed</span>'
             '<span><span class="key" style="background:var(--s1wash)"></span>target band</span>'
             '<span>dots are means, bars are 90% intervals</span></div>')
    if d["whatif"]:
        for run in d["whatif"]:
            vk = VERDICT_STATUS.get(run.get("verdict"), ("muted", "?"))
            p.append('<details%s><summary>%s %s <span class="muted">%s · %s</span></summary>'
                     % (" open" if run is d["whatif"][0] else "", status(vk[0], vk[1], run.get("verdict", "")),
                        esc(run.get("label")), esc(run.get("sim_label", run.get("sim"))), esc(str(run.get("created_at", ""))[:16])))
            mrows = []
            for m, r in run["metrics"].items():
                if r.get("assessment") in ("ok",) and not r.get("target"):
                    continue
                tg = r.get("target")
                mrows.append("<tr><td>%s</td><td class=\"num\">%s</td><td class=\"num\">%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
                             % (esc(m), compact(r["baseline"]["mean"]), compact(r["variant"]["mean"]),
                                range_bar(r["baseline"], r["variant"], tg), esc("%s–%s" % (compact(tg[0]), compact(tg[1])) if tg else "–"),
                                esc(r.get("assessment"))))
            p.append('<div class="scroll"><table><thead><tr><th>Metric</th><th class="num">Current</th><th class="num">Proposed</th>'
                     '<th>Range</th><th>Target</th><th>Assessment</th></tr></thead><tbody>%s</tbody></table></div>'
                     '<p class="muted">%s · %s</p></details>' % ("".join(mrows), esc("; ".join(run.get("reasons", []))), esc(run.get("_file"))))
    else:
        p.append('<p class="empty">No predictions yet: gs.py whatif --set KEY=VALUE.</p>')
    p.append("</section>")

    # dependencies
    p.append('<section class="card" id="deps"><h2>Dependencies</h2>')
    if d.get("map"):
        svg, hot = deps_svg(d["map"])
        st = d["map"].get("stats", {})
        p.append('<p class="muted">Folders by dependency depth: foundations on the left, their users to the right. %d files, '
                 '%d references. Full detail: .gamestudio/map/MAP.md; what a change touches: gs.py impact &lt;file&gt;.</p>'
                 % (st.get("files", 0), st.get("edges", 0)))
        p.append('<div class="scroll">%s</div>' % svg)
        if hot:
            p.append("<details><summary>Most depended-on files</summary>%s</details>" % _table(["file", "references"], [(r, n) for n, r in hot]))
    else:
        p.append('<p class="empty">No project map%s.</p>' % (": " + esc(d.get("map_error")) if d.get("map_error") else " (run gs.py map)"))
    p.append("</section>")

    # assets
    p.append('<section class="card" id="assets"><h2>Assets</h2>')
    if d["assets"]:
        budget_left = [EMBED_TOTAL_BYTES]
        cards = []
        for a in d["assets"][:60]:
            sk = ASSET_STATUS.get(a.get("status"), ("muted", "·"))
            lic = a.get("licence") or {}
            ltxt = lic.get("terms") if isinstance(lic, dict) else str(lic)
            prov = " · ".join(x for x in (a.get("provider"), a.get("model")) if x) or "handmade or imported"
            cards.append('<div class="asset"><div class="th">%s</div><div class="meta"><b>%s</b><br>%s %s<br>%s<br>%s%s</div></div>'
                         % (_thumb(d["root"], a, budget_left), esc(a.get("id")), esc(a.get("kind", "")),
                            status(sk[0], sk[1], a.get("status", "")), esc(prov), esc(ltxt or "licence not recorded"),
                            (" · $%s" % compact(a.get("cost_usd"))) if a.get("cost_usd") else ""))
        p.append('<div class="gallery">%s</div>' % "".join(cards))
        if len(d["assets"]) > 60:
            p.append('<p class="muted">+%d more in .gamestudio/assets/manifest.json</p>' % (len(d["assets"]) - 60))
    else:
        p.append('<p class="empty">No assets in the manifest yet.</p>')
    p.append("</section>")

    # budget
    led = bud.get("ledger") or []
    p.append('<section class="card" id="budget"><h2>Budget</h2><p>$%s spent of $%s%s</p>%s'
             % (compact(spent), compact(cap), "" if not cap else " (%d%%)" % round(100 * spent / cap), _meter(spent, cap)))
    if led:
        p.append("<details open><summary>Latest spend</summary>%s</details>" % _table(
            ["time", "tool", "provider", "cost", "note"],
            [(str(e.get("ts", ""))[:16], e.get("tool", ""), e.get("provider", ""), "$" + compact(e.get("cost_usd", 0)), e.get("note", ""))
             for e in list(reversed(led))[:20]]))
    p.append("</section>")
    p.append('<p class="muted">Generated by gs.py dashboard from .gamestudio/. Works offline; nothing is fetched. '
             'Predictions and bot results are estimates; confirm with playtests.</p></div><script>%s</script></body></html>' % JS)
    return "".join(p)


def _meter(spent: float, cap: float) -> str:
    if not cap:
        return ""
    frac = spent / cap
    cls = "over" if frac > 1 else "warn" if frac >= 0.8 else ""
    return '<div class="meter %s" role="meter" aria-valuenow="%.0f" aria-valuemin="0" aria-valuemax="100"><span style="width:%.1f%%"></span></div>' % (
        cls, 100 * frac, min(100.0, 100 * frac))


def _table(head: List[str], rows: List[Tuple[Any, ...]]) -> str:
    return '<div class="scroll"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (
        "".join("<th>%s</th>" % esc(h) for h in head),
        "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % esc(c) for c in r) for r in rows))


def _thumb(root: Path, a: Dict[str, Any], left: List[int]) -> str:
    path = a.get("path") or ""
    p = (root / path) if path else None
    ext = Path(path).suffix.lower()
    if p and p.is_file() and ext in IMAGE_MIME:
        size = p.stat().st_size
        if size <= EMBED_MAX_BYTES and size <= left[0]:
            left[0] -= size
            data = base64.b64encode(p.read_bytes()).decode("ascii")
            return '<img alt="%s" src="data:%s;base64,%s">' % (esc(a.get("id")), IMAGE_MIME[ext], data)
    return '<span class="muted">%s</span>' % esc(a.get("kind", "asset"))


def write(root: Path, out: Optional[Path] = None, with_map: bool = True) -> Path:
    if not G.gs_dir(root).is_dir():
        raise FileNotFoundError("no .gamestudio/ in %s (run gs.py init)" % root)
    target = out or (G.gs_dir(root) / "reports" / "dashboard.html")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render(collect(root, with_map)), encoding="utf-8")
    return target


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--root")
    ap.add_argument("--out")
    ap.add_argument("--no-map", action="store_true", help="skip the dependency graph (no project map refresh)")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    root = Path(a.root).expanduser().resolve() if a.root else (G.find_project_root(Path.cwd()) or Path.cwd().resolve())
    try:
        path = write(root, Path(a.out).resolve() if a.out else None, not a.no_map)
    except FileNotFoundError as exc:
        print("dashboard: %s" % exc, file=sys.stderr)
        return 2
    print("Dashboard written: %s (open it in a browser; it works offline)" % path)
    return 0


def selftest() -> int:
    fails: List[str] = []

    def check(cond: bool, msg: str) -> None:
        if not cond:
            fails.append(msg)
            print("FAIL: " + msg)

    tmp = Path(tempfile.mkdtemp(prefix="gs-dash-"))
    try:
        G.init_project(tmp, "Dash <Test>", "godot", "puzzle", platforms=["windows", "web"])
        g = G.gs_dir(tmp)
        con = G.load_json(g / "contract.json")
        con["loops"] = [{"id": "core", "name": "Merge loop", "type": "core", "period": "seconds", "steps": [
            {"id": "s1", "action": "swipe to slide every tile", "reward": None, "next": "s2"},
            {"id": "s2", "action": "merge equal tiles", "reward": {"score": 4}, "next": ["s1", "loop:meta"]}]}]
        con["progression"]["difficulty"]["target_win_rate"] = 0.6
        con["technical"]["perf_budgets"]["frame_ms_p95"] = 16.7
        G.save_json(g / "contract.json", con)
        G.save_json(g / "features.json", {"schema_version": "1.0", "features": [
            {"id": "F001", "title": "Core <loop>", "area": "gameplay", "priority": "P0", "status": "done",
             "gates": {"static": "pass", "unit": "pass", "playthrough": "pass", "visual": "n/a", "perf": "pass"}},
            {"id": "F002", "title": "Menu", "area": "ui", "priority": "P1", "status": "todo", "gates": {}}]})
        (g / "playtests").mkdir(exist_ok=True)
        for i, w in enumerate((0.5, 0.58, 0.63)):
            f = g / "playtests" / ("bots-%d.json" % i)
            G.save_json(f, {"mode": "bot", "metrics": {"win_rate": w, "avg_session_sec": 100}})
            os.utime(str(f), (1_700_000_000 + i * 86400, 1_700_000_000 + i * 86400))
        (g / "evidence" / "F001").mkdir(parents=True, exist_ok=True)
        G.save_json(g / "evidence" / "F001" / "perf.json", {"frame_ms": {"p50": 9, "p95": 14.2}, "budgets": {"frame_ms_p95": 16.7}})
        G.save_json(g / "economy" / "model.json", {"name": "Test economy", "resources": [{"id": "coins"}], "nodes": [
            {"id": "win", "kind": "source", "outputs": {"coins": 10}}, {"id": "shop", "kind": "sink", "inputs": {"coins": 5}}]})
        (g / "whatif").mkdir(exist_ok=True)
        G.save_json(g / "whatif" / "r1.json", {"label": "win_tile 1024 -> 512", "sim": "godot", "verdict": "mixed", "reasons": ["x"],
                                               "metrics": {"win_rate": {"baseline": {"mean": 0.6, "lo": 0.55, "hi": 0.65},
                                                                        "variant": {"mean": 0.9, "lo": 0.86, "hi": 0.94},
                                                                        "diff": {"mean": 0.3}, "target": [0.55, 0.65], "assessment": "further"}}})
        (tmp / "art").mkdir()
        (tmp / "art" / "a.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" width="8" height="8"></svg>', encoding="utf-8")
        man = G.load_json(g / "assets" / "manifest.json")
        man["assets"] = [{"id": "a", "path": "art/a.svg", "kind": "icon", "status": "approved", "licence": {"terms": "CC0"}}]
        G.save_json(g / "assets" / "manifest.json", man)
        (tmp / "core").mkdir()
        (tmp / "core" / "x.gd").write_text("extends Node\n", encoding="utf-8")
        (tmp / "ui").mkdir()
        (tmp / "ui" / "y.gd").write_text('const X = preload("res://core/x.gd")\n', encoding="utf-8")
        (tmp / "project.godot").write_text("config_version=5\n", encoding="utf-8")
        out = write(tmp)
        page = out.read_text(encoding="utf-8")
        for sid in ("features", "loops", "economy", "trends", "whatif", "deps", "assets", "budget"):
            check('id="%s"' % sid in page, "section %s present" % sid)
        check("Dash &lt;Test&gt;" in page and "Core &lt;loop&gt;" in page and "<loop>" not in page, "text is escaped")
        check(page.count("<svg") == page.count("</svg>") and page.count("<svg") >= 5, "svg tags balanced")
        check("<script src" not in page and "<link" not in page and "url(http" not in page, "no external resources")
        check("data:image/svg+xml;base64," in page, "thumbnail embedded")
        check("mixed" in page and "Frame time p95" in page and "budget 16.7 ms" in page, "what-if and perf shown")
        check("ui uses core" in page or "ui uses core: 1 reference" in page, "dependency edge drawn")
        check(">1<" in page and "/ 2" in page, "hero shows features done")
    finally:
        shutil.rmtree(str(tmp), ignore_errors=True)
    if fails:
        print("dashboard selftest: %d FAILED" % len(fails))
        return 1
    print("dashboard selftest: OK")
    return 0


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows pipes default to the ANSI code page; Claude Code reads UTF-8
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
