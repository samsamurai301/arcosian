#!/usr/bin/env python3
"""sprite_sheet.py - inspect, check and convert sprite-sheet JSON (art-tools skill).

Reads Aseprite JSON (hash and array forms) and TexturePacker-style JSON
(hash or array "frames", optional top-level "animations" name -> frame names).

    sprite_sheet.py inspect SHEET.json [--json]
    sprite_sheet.py check SHEET.json --platform {mobile,pc,web,console}
                          [--max-size N] [--strict] [--json]
    sprite_sheet.py godot SHEET.json --texture res://path/sheet.png --out frames.tres
                          [--fps N] [--once TAG,TAG] [--verify]
    sprite_sheet.py --selftest

Platform default maximum texture size (estimates, chosen to be safe on the
low end of each platform, not hard limits):
    mobile  2048  older and low-end GPUs; 4096 is common but not universal
    web     4096  WebGL2 only guarantees 2048; 4096 is near-universal
    pc      8192  any GPU from the last decade supports 8192 or more
    console 8192  current consoles support 8192 or more; check the SDK

Exit codes: 0 ok (warnings allowed), 1 check failed, 2 usage or input error.
Stdlib only, Python 3.9+.
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import re
import struct
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path
from typing import Any, Dict, List, Optional

PLATFORM_MAX = {"mobile": 2048, "web": 4096, "pc": 8192, "console": 8192}
DIRECTIONS = ("forward", "reverse", "pingpong", "pingpong_reverse")


class InputError(Exception):
    """Bad or unsupported input file (exit code 2)."""


# --------------------------------------------------------------------------- model

class Frame:
    def __init__(self, name: str, x: int, y: int, w: int, h: int, duration: Optional[int],
                 rotated: bool, trimmed: bool, src_x: int, src_y: int, src_w: int, src_h: int):
        self.name, self.x, self.y, self.w, self.h = name, x, y, w, h
        self.duration, self.rotated, self.trimmed = duration, rotated, trimmed
        self.src_x, self.src_y, self.src_w, self.src_h = src_x, src_y, src_w, src_h


class Tag:
    def __init__(self, name: str, indices: List[int], direction: str, repeat: Optional[int]):
        self.name, self.indices, self.direction, self.repeat = name, indices, direction, repeat


class Sheet:
    def __init__(self, size: Optional[tuple], image: str, frames: List[Frame], tags: List[Tag]):
        self.size, self.image, self.frames, self.tags = size, image, frames, tags


def _int(value: Any, what: str) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InputError(f"{what} is not a number: {value!r}")
    return int(round(value))


def _rect(obj: Any, what: str) -> Dict[str, int]:
    if not isinstance(obj, dict) or not all(k in obj for k in ("x", "y", "w", "h")):
        raise InputError(f"{what} needs x, y, w, h")
    return {k: _int(obj[k], f"{what}.{k}") for k in ("x", "y", "w", "h")}


def _frame(name: str, entry: Any) -> Frame:
    if not isinstance(entry, dict) or "frame" not in entry:
        raise InputError(f"frame {name!r} has no 'frame' rectangle")
    r = _rect(entry["frame"], f"frame {name!r}.frame")
    dur = entry.get("duration")
    dur = _int(dur, f"frame {name!r}.duration") if dur is not None else None
    rotated = bool(entry.get("rotated", False))
    trimmed = bool(entry.get("trimmed", False))
    ss = entry.get("spriteSourceSize")
    src = entry.get("sourceSize")
    sx = sy = 0
    sw, sh = (r["h"], r["w"]) if rotated else (r["w"], r["h"])
    if isinstance(ss, dict) and all(k in ss for k in ("x", "y")):
        sx, sy = _int(ss["x"], "spriteSourceSize.x"), _int(ss["y"], "spriteSourceSize.y")
    if isinstance(src, dict) and "w" in src and "h" in src:
        sw, sh = _int(src["w"], "sourceSize.w"), _int(src["h"], "sourceSize.h")
    return Frame(name, r["x"], r["y"], r["w"], r["h"], dur, rotated, trimmed, sx, sy, sw, sh)


def load_sheet(path: Path) -> Sheet:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise InputError(f"cannot read {path}: {exc}")
    if not isinstance(data, dict) or "frames" not in data:
        raise InputError("not a sprite-sheet JSON: no top-level 'frames'")
    raw = data["frames"]
    frames: List[Frame] = []
    if isinstance(raw, dict):
        for name, entry in raw.items():
            frames.append(_frame(str(name), entry))
    elif isinstance(raw, list):
        for i, entry in enumerate(raw):
            name = str(entry.get("filename", i)) if isinstance(entry, dict) else str(i)
            frames.append(_frame(name, entry))
    else:
        raise InputError("'frames' must be an object or an array")
    if not frames:
        raise InputError("sheet has no frames")
    meta = data.get("meta") if isinstance(data.get("meta"), dict) else {}
    size = None
    if isinstance(meta.get("size"), dict) and "w" in meta["size"] and "h" in meta["size"]:
        size = (_int(meta["size"]["w"], "meta.size.w"), _int(meta["size"]["h"], "meta.size.h"))
    tags: List[Tag] = []
    for t in meta.get("frameTags") or []:
        if not isinstance(t, dict) or "name" not in t or "from" not in t or "to" not in t:
            raise InputError("frameTags entry needs name, from, to")
        a, b = _int(t["from"], "tag.from"), _int(t["to"], "tag.to")
        if not (0 <= a <= b < len(frames)):
            raise InputError(f"tag {t['name']!r} range {a}-{b} outside 0-{len(frames) - 1}")
        direction = str(t.get("direction", "forward"))
        if direction not in DIRECTIONS:
            raise InputError(f"tag {t['name']!r} has unknown direction {direction!r}")
        rep = t.get("repeat")
        try:
            rep = int(rep) if rep is not None else None
        except (TypeError, ValueError):
            rep = None
        tags.append(Tag(str(t["name"]), list(range(a, b + 1)), direction, rep))
    anims = data.get("animations")
    if not tags and isinstance(anims, dict):
        by_name = {f.name: i for i, f in enumerate(frames)}
        for name, names in anims.items():
            if not isinstance(names, list):
                continue
            missing = [n for n in names if n not in by_name]
            if missing:
                raise InputError(f"animation {name!r} names unknown frames: {missing[:3]}")
            tags.append(Tag(str(name), [by_name[n] for n in names], "forward", None))
    return Sheet(size, str(meta.get("image", "")), frames, tags)


# --------------------------------------------------------------------------- inspect

def cmd_inspect(sheet: Sheet, as_json: bool) -> int:
    total = sum(f.duration or 0 for f in sheet.frames)
    if as_json:
        out = {
            "image": sheet.image, "size": list(sheet.size) if sheet.size else None,
            "frames": [{"index": i, "name": f.name, "x": f.x, "y": f.y, "w": f.w, "h": f.h,
                        "duration": f.duration, "trimmed": f.trimmed, "rotated": f.rotated}
                       for i, f in enumerate(sheet.frames)],
            "tags": [{"name": t.name, "frames": t.indices, "direction": t.direction,
                      "repeat": t.repeat} for t in sheet.tags],
        }
        print(json.dumps(out, indent=2))
        return 0
    size = f"{sheet.size[0]}x{sheet.size[1]}" if sheet.size else "unknown"
    print(f"image: {sheet.image or '(not stated)'}   sheet size: {size}   frames: {len(sheet.frames)}   "
          f"total duration: {total} ms")
    print("frames:")
    for i, f in enumerate(sheet.frames):
        dur = f"{f.duration} ms" if f.duration is not None else "no duration"
        extra = (" trimmed" if f.trimmed else "") + (" rotated" if f.rotated else "")
        print(f"  {i:3d}  {f.name:<28} at ({f.x},{f.y}) {f.w}x{f.h}  {dur}{extra}")
    print(f"tags: {len(sheet.tags)}")
    for t in sheet.tags:
        ds = [sheet.frames[i].duration for i in t.indices]
        span = (f"{sum(d or 0 for d in ds)} ms" if all(d is not None for d in ds) else "no durations")
        rng = f"{t.indices[0]}-{t.indices[-1]}" if t.indices == list(range(t.indices[0], t.indices[-1] + 1)) \
            else f"{len(t.indices)} named frames"
        rep = f" repeat={t.repeat}" if t.repeat is not None else ""
        print(f"  {t.name:<20} frames {rng} ({len(t.indices)})  {t.direction}{rep}  {span}")
    return 0


# --------------------------------------------------------------------------- check

def min_separation(frames: List[Frame]) -> Optional[int]:
    """Smallest gap (pixels) between any two distinct frame rectangles.

    0 means two frames touch; negative means they overlap. Identical rectangles
    (merged duplicate frames) are ignored. None when there is nothing to compare.
    """
    seen = {}
    for f in frames:
        seen[(f.x, f.y, f.w, f.h)] = f
    rects = list(seen)
    best: Optional[int] = None
    for i in range(len(rects)):
        ax, ay, aw, ah = rects[i]
        for j in range(i + 1, len(rects)):
            bx, by, bw, bh = rects[j]
            gx = max(ax - (bx + bw), bx - (ax + aw))
            gy = max(ay - (by + bh), by - (ay + ah))
            gap = max(gx, gy)
            if best is None or gap < best:
                best = gap
    return best


def run_checks(sheet: Sheet, platform: str, max_size: Optional[int], strict: bool) -> List[Dict[str, str]]:
    findings: List[Dict[str, str]] = []

    def add(sev: str, code: str, msg: str) -> None:
        findings.append({"severity": sev, "code": code, "message": msg})

    limit = max_size if max_size else PLATFORM_MAX[platform]
    sw, sh = sheet.size if sheet.size else (
        max(f.x + f.w for f in sheet.frames), max(f.y + f.h for f in sheet.frames))
    if max(sw, sh) > limit:
        add("error", "SIZE", f"sheet is {sw}x{sh}; {platform} safe maximum is {limit} "
            f"({'--max-size' if max_size else 'default'}). Split the sheet or lower the frame size.")
    if sheet.size is None:
        add("warning", "NO_SIZE", "meta.size missing; size taken from the frame extents")
    for f in sheet.frames:
        if f.x < 0 or f.y < 0 or f.x + f.w > sw or f.y + f.h > sh:
            add("error", "OUTSIDE", f"frame {f.name!r} lies outside the {sw}x{sh} sheet")
    gap = min_separation(sheet.frames)
    if gap is not None:
        if gap < 0:
            add("error", "OVERLAP", "two frames overlap in the sheet (not identical duplicates)")
        elif gap == 0:
            add("error" if strict else "warning", "NO_PADDING",
                "frames touch with no padding; filtering or mipmaps can bleed neighbours in. "
                "Use at least 1 px (2 px with mipmaps or compression) and extrude edges.")
    for t in sheet.tags:
        sizes = {(sheet.frames[i].src_w, sheet.frames[i].src_h) for i in t.indices}
        if len(sizes) > 1:
            listed = ", ".join(f"{w}x{h}" for w, h in sorted(sizes))
            add("error", "MIXED_SIZE", f"tag {t.name!r} mixes frame sizes ({listed}); "
                "the animation will jitter. Pad to one canvas size or export untrimmed.")
        missing = [i for i in t.indices if sheet.frames[i].duration is None]
        if missing:
            add("warning", "NO_DURATION", f"tag {t.name!r} has frames with no duration")
    for i, f in enumerate(sheet.frames):
        if f.duration is not None and f.duration <= 0:
            add("error", "ZERO_DURATION", f"frame {i} ({f.name!r}) has duration {f.duration}")
    return findings


def cmd_check(sheet: Sheet, platform: str, max_size: Optional[int], strict: bool, as_json: bool) -> int:
    findings = run_checks(sheet, platform, max_size, strict)
    errors = [f for f in findings if f["severity"] == "error"]
    if as_json:
        print(json.dumps({"ok": not errors, "findings": findings}, indent=2))
    else:
        for f in findings:
            print(f"{f['severity'].upper():<8} {f['code']:<14} {f['message']}")
        print(f"{len(errors)} error(s), {len(findings) - len(errors)} warning(s)")
    return 1 if errors else 0


# --------------------------------------------------------------------------- godot

def _gstr(text: str) -> str:
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def _num(value: float) -> str:
    text = f"{value:.4f}".rstrip("0")
    return text + "0" if text.endswith(".") else text


def tag_sequence(tag: Tag) -> List[int]:
    idx = list(tag.indices)
    if tag.direction == "reverse":
        return idx[::-1]
    if tag.direction == "pingpong":
        return idx + idx[-2:0:-1]
    if tag.direction == "pingpong_reverse":
        rev = idx[::-1]
        return rev + rev[-2:0:-1]
    return idx


def build_tres(sheet: Sheet, texture: str, fps_default: float, once: List[str]) -> str:
    for f in sheet.frames:
        if f.rotated:
            raise InputError("rotated frames are not supported; export without rotation")
    tags = sheet.tags or [Tag("default", list(range(len(sheet.frames))), "forward", None)]
    anims = []
    used: Dict[int, None] = {}
    for t in tags:
        seq = tag_sequence(t)
        durs = [sheet.frames[i].duration for i in seq]
        known = [d for d in durs if d is not None and d > 0]
        if known:
            base = float(min(known))
            fps = 1000.0 / base
            rel = [(d / base) if d else 1.0 for d in durs]
        else:
            fps, rel = fps_default, [1.0] * len(seq)
        loop = not (t.name in once or t.repeat == 1)
        anims.append((t.name, seq, rel, fps, loop))
        for i in seq:
            used[i] = None
    sub_id: Dict[tuple, str] = {}
    sub_lines: List[str] = []
    for i in used:
        f = sheet.frames[i]
        key = (f.x, f.y, f.w, f.h, f.src_x, f.src_y, f.src_w, f.src_h)
        if key in sub_id:
            continue
        sid = f"AtlasTexture_{len(sub_id)}"
        sub_id[key] = sid
        sub_lines.append(f'[sub_resource type="AtlasTexture" id="{sid}"]')
        sub_lines.append('atlas = ExtResource("1_sheet")')
        sub_lines.append(f"region = Rect2({f.x}, {f.y}, {f.w}, {f.h})")
        if f.src_x or f.src_y or f.src_w != f.w or f.src_h != f.h:
            sub_lines.append(f"margin = Rect2({f.src_x}, {f.src_y}, {f.src_w - f.w}, {f.src_h - f.h})")
        sub_lines.append("filter_clip = true")
        sub_lines.append("")
    out = [f'[gd_resource type="SpriteFrames" load_steps={len(sub_id) + 2} format=3]', "",
           f'[ext_resource type="Texture2D" path={_gstr(texture)} id="1_sheet"]', ""]
    out += sub_lines
    out.append("[resource]")
    blocks = []
    for name, seq, rel, fps, loop in anims:
        fr = []
        for i, d in zip(seq, rel):
            f = sheet.frames[i]
            sid = sub_id[(f.x, f.y, f.w, f.h, f.src_x, f.src_y, f.src_w, f.src_h)]
            fr.append(f'{{\n"duration": {_num(d)},\n"texture": SubResource("{sid}")\n}}')
        blocks.append('{\n"frames": [' + ", ".join(fr) + f'],\n"loop": {"true" if loop else "false"},\n'
                      f'"name": &{_gstr(name)},\n"speed": {_num(fps)}\n}}')
    out.append("animations = [" + ", ".join(blocks) + "]")
    return "\n".join(out) + "\n"


def _png(width: int, height: int) -> bytes:
    def chunk(kind: bytes, body: bytes) -> bytes:
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF)
    raw = b"".join(b"\x00" + b"\x00\x00\x00\x00" * width for _ in range(height))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


def verify_with_godot(sheet: Sheet, tres_text: str, texture: str) -> int:
    """Load the .tres in a throwaway project with GODOT_BIN (imports the placeholder texture first)."""
    godot = os.environ.get("GODOT_BIN")
    if not godot:
        print("verify skipped: GODOT_BIN is not set")
        return 0
    if not texture.startswith("res://"):
        print("verify skipped: texture is not a res:// path")
        return 0
    sw, sh = sheet.size or (64, 64)
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "project.godot").write_text('config_version=5\n[application]\nconfig/name="verify"\n',
                                            encoding="utf-8")
        tex = root / texture[len("res://"):]
        tex.parent.mkdir(parents=True, exist_ok=True)
        tex.write_bytes(_png(min(sw, 512), min(sh, 512)))
        (root / "frames.tres").write_text(tres_text, encoding="utf-8")
        (root / "check.gd").write_text(
            "extends SceneTree\nfunc _init():\n\tvar r = load(\"res://frames.tres\")\n"
            "\tif r == null or not (r is SpriteFrames):\n\t\tprint(\"VERIFY_FAIL\")\n\t\tquit(1)\n\t\treturn\n"
            "\tfor a in r.get_animation_names():\n\t\tprint(\"ANIM \", a, \" \", r.get_frame_count(a))\n"
            "\tquit(0)\n", encoding="utf-8")
        try:
            # a PNG only loads as Texture2D after Godot has imported it
            subprocess.run([godot, "--headless", "--path", str(root), "--import"], capture_output=True, text=True,
                           timeout=300)
            res = subprocess.run([godot, "--headless", "--path", str(root), "--script", "res://check.gd"],
                                 capture_output=True, text=True, timeout=120)
        except (OSError, subprocess.TimeoutExpired) as exc:
            print(f"verify failed to run: {exc}")
            return 1
        print(res.stdout.strip())
        if res.returncode != 0 or "VERIFY_FAIL" in res.stdout:
            print(res.stderr.strip())
            print("verify: Godot could not load the file")
            return 1
    print("verify: Godot loaded the SpriteFrames resource")
    return 0


def cmd_godot(sheet: Sheet, texture: str, out: Path, fps: float, once: List[str], verify: bool) -> int:
    text = build_tres(sheet, texture, fps, once)
    out.write_text(text, encoding="utf-8")
    n = len(sheet.tags) or 1
    print(f"wrote {out} ({n} animation(s), {len(sheet.frames)} frame(s))")
    return verify_with_godot(sheet, text, texture) if verify else 0


# --------------------------------------------------------------------------- selftest

HASH_FIXTURE = {
    "frames": {
        "hero 0.aseprite": {"frame": {"x": 1, "y": 1, "w": 16, "h": 16}, "rotated": False, "trimmed": False,
                            "spriteSourceSize": {"x": 0, "y": 0, "w": 16, "h": 16},
                            "sourceSize": {"w": 16, "h": 16}, "duration": 100},
        "hero 1.aseprite": {"frame": {"x": 19, "y": 1, "w": 16, "h": 16}, "rotated": False, "trimmed": False,
                            "spriteSourceSize": {"x": 0, "y": 0, "w": 16, "h": 16},
                            "sourceSize": {"w": 16, "h": 16}, "duration": 200},
        "hero 2.aseprite": {"frame": {"x": 37, "y": 1, "w": 16, "h": 16}, "rotated": False, "trimmed": False,
                            "spriteSourceSize": {"x": 0, "y": 0, "w": 16, "h": 16},
                            "sourceSize": {"w": 16, "h": 16}, "duration": 100},
    },
    "meta": {"image": "hero.png", "size": {"w": 64, "h": 32},
             "frameTags": [{"name": "idle", "from": 0, "to": 1, "direction": "forward"},
                           {"name": "bounce", "from": 0, "to": 2, "direction": "pingpong"},
                           {"name": "hit", "from": 2, "to": 2, "direction": "forward", "repeat": "1"}]},
}


def _array_form(fixture: Dict[str, Any]) -> Dict[str, Any]:
    arr = [dict(v, filename=k) for k, v in fixture["frames"].items()]
    return {"frames": arr, "meta": fixture["meta"]}


def selftest() -> int:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        return _selftest()


def _selftest() -> int:
    failures: List[str] = []

    def expect(cond: bool, msg: str) -> None:
        if not cond:
            failures.append(msg)

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)

        def write(name: str, data: Any) -> Path:
            p = root / name
            p.write_text(json.dumps(data), encoding="utf-8")
            return p

        h = load_sheet(write("hash.json", HASH_FIXTURE))
        a = load_sheet(write("array.json", _array_form(HASH_FIXTURE)))
        expect(len(h.frames) == 3 and len(a.frames) == 3, "hash and array frame counts")
        expect([t.name for t in h.tags] == [t.name for t in a.tags], "tags match across forms")
        expect(h.size == (64, 32), "sheet size parsed")
        expect(tag_sequence(h.tags[1]) == [0, 1, 2, 1], "pingpong sequence")
        expect(tag_sequence(Tag("x", [0, 1, 2], "pingpong_reverse", None)) == [2, 1, 0, 1], "pingpong_reverse")
        expect(tag_sequence(Tag("x", [0, 1, 2], "reverse", None)) == [2, 1, 0], "reverse sequence")
        expect(cmd_inspect(h, False) == 0 and cmd_inspect(h, True) == 0, "inspect runs")

        # texturepacker style with animations map and no durations
        tp = {"frames": [{"filename": "a", "frame": {"x": 0, "y": 0, "w": 8, "h": 8}},
                         {"filename": "b", "frame": {"x": 10, "y": 0, "w": 8, "h": 8}}],
              "animations": {"walk": ["a", "b"]}, "meta": {"image": "tp.png", "size": {"w": 32, "h": 32}}}
        t = load_sheet(write("tp.json", tp))
        expect(t.tags and t.tags[0].indices == [0, 1], "TexturePacker animations map")

        codes = lambda s, p="pc", m=None, strict=False: {f["code"] for f in run_checks(s, p, m, strict)}
        expect(codes(h) == set(), f"clean sheet has no findings, got {codes(h)}")
        big = json.loads(json.dumps(HASH_FIXTURE))
        big["meta"]["size"] = {"w": 4096, "h": 64}
        expect("SIZE" in codes(load_sheet(write("big.json", big)), "mobile"), "mobile oversize flagged")
        expect("SIZE" not in codes(load_sheet(write("big2.json", big)), "pc"), "same sheet fine on pc")
        expect("SIZE" in codes(h, "pc", 32), "--max-size honoured")
        tight = json.loads(json.dumps(HASH_FIXTURE))
        tight["frames"]["hero 1.aseprite"]["frame"]["x"] = 17
        ts = load_sheet(write("tight.json", tight))
        expect("NO_PADDING" in codes(ts), "touching frames flagged")
        expect(run_checks(ts, "pc", None, True)[0]["severity"] == "error" or
               any(f["severity"] == "error" for f in run_checks(ts, "pc", None, True)), "strict promotes padding")
        mixed = json.loads(json.dumps(HASH_FIXTURE))
        mixed["frames"]["hero 1.aseprite"]["sourceSize"] = {"w": 20, "h": 16}
        expect("MIXED_SIZE" in codes(load_sheet(write("mixed.json", mixed))), "mixed sizes in a tag flagged")
        zero = json.loads(json.dumps(HASH_FIXTURE))
        zero["frames"]["hero 0.aseprite"]["duration"] = 0
        zs = load_sheet(write("zero.json", zero))
        expect("ZERO_DURATION" in codes(zs), "zero duration flagged")
        expect(cmd_check(zs, "pc", None, False, False) == 1, "check exits 1 on error")
        expect(cmd_check(h, "pc", None, False, False) == 0, "check exits 0 when clean")

        tres = build_tres(h, "res://art/hero.png", 10.0, [])
        expect(tres.startswith('[gd_resource type="SpriteFrames" load_steps=5 format=3]'), "header and load_steps")
        expect('path="res://art/hero.png"' in tres and 'ExtResource("1_sheet")' in tres, "ext resource")
        expect(tres.count("[sub_resource") == 3, "three atlas textures (frames reused)")
        expect('"name": &"idle"' in tres and '"speed": 10.0' in tres, "idle animation at 10 fps")
        expect('"duration": 2.0' in tres, "relative duration 200/100 = 2.0")
        expect('"loop": false' in tres and '"name": &"hit"' in tres, "repeat=1 tag does not loop")
        expect(build_tres(h, "res://a.png", 10.0, ["idle"]).count('"loop": false') == 2, "--once forces no loop")
        expect(tres.count("{\n\"duration\"") >= 4 + 2 + 1, "pingpong expanded to four frames")
        out = root / "frames.tres"
        expect(cmd_godot(h, "res://art/hero.png", out, 10.0, [], False) == 0 and out.exists(), "godot writes file")
        trim = json.loads(json.dumps(HASH_FIXTURE))
        f0 = trim["frames"]["hero 0.aseprite"]
        f0.update(trimmed=True, spriteSourceSize={"x": 2, "y": 3, "w": 16, "h": 16}, sourceSize={"w": 20, "h": 24})
        expect("margin = Rect2(2, 3, 4, 8)" in build_tres(load_sheet(write("trim.json", trim)), "res://a.png", 10.0, []),
               "trim margin written")
        rot = json.loads(json.dumps(HASH_FIXTURE))
        rot["frames"]["hero 0.aseprite"]["rotated"] = True
        try:
            build_tres(load_sheet(write("rot.json", rot)), "res://a.png", 10.0, [])
            expect(False, "rotated frames rejected")
        except InputError:
            pass
        try:
            load_sheet(write("bad.json", {"nope": 1}))
            expect(False, "bad json rejected")
        except InputError:
            pass
        expect(_png(2, 2)[:8] == b"\x89PNG\r\n\x1a\n", "png helper")
    if failures:
        for m in failures:
            sys.__stdout__.write(f"FAIL: {m}\n")
        return 1
    sys.__stdout__.write("selftest ok\n")
    return 0


# --------------------------------------------------------------------------- main

def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Inspect, check and convert sprite-sheet JSON.")
    ap.add_argument("--selftest", action="store_true", help="run offline self-test")
    sub = ap.add_subparsers(dest="cmd")
    p = sub.add_parser("inspect", help="print frames, tags, durations, sheet size")
    p.add_argument("sheet")
    p.add_argument("--json", action="store_true")
    p = sub.add_parser("check", help="check a sheet against a platform")
    p.add_argument("sheet")
    p.add_argument("--platform", required=True, choices=sorted(PLATFORM_MAX))
    p.add_argument("--max-size", type=int, default=None)
    p.add_argument("--strict", action="store_true", help="treat warnings about padding as errors")
    p.add_argument("--json", action="store_true")
    p = sub.add_parser("godot", help="write a Godot 4 SpriteFrames .tres")
    p.add_argument("sheet")
    p.add_argument("--texture", required=True, help="res:// path of the sheet image in the Godot project")
    p.add_argument("--out", required=True)
    p.add_argument("--fps", type=float, default=10.0, help="speed when the sheet has no durations")
    p.add_argument("--once", default="", help="comma list of tags that must not loop")
    p.add_argument("--verify", action="store_true", help="load the result with GODOT_BIN if set")
    try:
        args = ap.parse_args(argv)
    except SystemExit as exc:
        return 0 if exc.code in (0, None) else 2
    if args.selftest:
        return selftest()
    if not args.cmd:
        ap.print_usage(sys.stderr)
        return 2
    try:
        sheet = load_sheet(Path(args.sheet))
        if args.cmd == "inspect":
            return cmd_inspect(sheet, args.json)
        if args.cmd == "check":
            if args.max_size is not None and args.max_size < 1:
                raise InputError("--max-size must be positive")
            return cmd_check(sheet, args.platform, args.max_size, args.strict, args.json)
        if not args.texture.startswith("res://"):
            raise InputError("--texture must be a res:// path")
        once = [s.strip() for s in args.once.split(",") if s.strip()]
        return cmd_godot(sheet, args.texture, Path(args.out), args.fps, once, args.verify)
    except InputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows pipes default to the ANSI code page; Claude Code reads UTF-8
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
