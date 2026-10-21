#!/usr/bin/env python3
"""image_post.py - image checks (stdlib) and post-processing (optional Pillow).

  check    --in FILE... [--max-kb N] [--max-dim N] [--pot] [--no-alpha]
           Reads PNG/JPEG headers only: size, alpha, power-of-two, file-size budget.
           Non-power-of-two is a warning, or a failure with --pot. --no-alpha fails on alpha
           (e.g. iOS app icons). Exit 1 when any file fails.
  palette  --in FILE [--colors 16] [--out FILE]   extract/quantize to N colours (prints hex list)
  resize   --in FILE --out FILE (--width W [--height H] | --scale S) [--resample nearest|lanczos]
  pixelate --in FILE --out FILE [--block 4]       block-average then nearest-neighbour upscale
  atlas    --in FILE... --out ATLAS.png [--packer maxrects|shelf] [--max-size 2048] [--padding 1] [--pot]
           Packs sprites into a PNG plus ATLAS.json {image,size,frames{name:{x,y,w,h}}}.

palette/resize/pixelate/atlas need Pillow (pip install pillow, or uv run --with pillow python3 ...).
Exit codes: 0 ok, 1 check failed / atlas does not fit, 2 usage/input error (incl. Pillow missing).
"""
from __future__ import annotations

import argparse
import json
import math
import struct
import sys
import tempfile
import zlib
from pathlib import Path

PNG_SIG = b"\x89PNG\r\n\x1a\n"


class ImageError(Exception):
    pass


# ----------------------------------------------------------------------------- headers
def parse_header(data: bytes) -> dict:
    if data[:8] == PNG_SIG:
        w, h, depth, ctype = struct.unpack(">IIBB", data[16:26])
        alpha, pos = ctype in (4, 6), 8
        while pos + 8 <= len(data):
            ln, kind = struct.unpack(">I4s", data[pos:pos + 8])
            if kind == b"tRNS":
                alpha = True
            if kind in (b"IDAT", b"IEND"):
                break
            pos += 12 + ln
        return {"format": "png", "width": w, "height": h, "alpha": alpha, "bit_depth": depth}
    if data[:2] == b"\xff\xd8":
        pos = 2
        while pos + 9 < len(data):
            if data[pos] != 0xFF:
                pos += 1
                continue
            marker = data[pos + 1]
            if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7 or marker == 0xFF:
                pos += 1 if marker == 0xFF else 2
                continue
            ln = struct.unpack(">H", data[pos + 2:pos + 4])[0]
            if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                h, w = struct.unpack(">HH", data[pos + 5:pos + 9])
                return {"format": "jpeg", "width": w, "height": h, "alpha": False, "bit_depth": data[pos + 4]}
            pos += 2 + ln
        raise ImageError("JPEG without frame header")
    raise ImageError("not a PNG or JPEG file")


def is_pot(n: int) -> bool:
    return n > 0 and n & (n - 1) == 0


def check_file(path: Path, max_kb=None, max_dim=None, need_pot=False, no_alpha=False) -> dict:
    try:
        data = path.read_bytes()
        info = parse_header(data)
    except (OSError, ImageError, struct.error) as e:
        return {"path": str(path), "ok": False, "issues": [{"severity": "error", "message": str(e)}]}
    info.update({"path": str(path), "bytes": len(data), "pot": is_pot(info["width"]) and is_pot(info["height"])})
    issues = []

    def add(sev: str, msg: str) -> None:
        issues.append({"severity": sev, "message": msg})
    if not info["pot"]:
        add("error" if need_pot else "warning", "%dx%d is not power-of-two (mipmaps/compression/atlasing)" % (info["width"], info["height"]))
    if max_dim and max(info["width"], info["height"]) > max_dim:
        add("error", "dimension %dx%d exceeds max %d" % (info["width"], info["height"], max_dim))
    if max_kb and len(data) > max_kb * 1024:
        add("error", "file is %.1f KB, budget %s KB" % (len(data) / 1024, max_kb))
    if no_alpha and info["alpha"]:
        add("error", "has an alpha channel/transparency (not allowed)")
    info["issues"] = issues
    info["ok"] = not any(i["severity"] == "error" for i in issues)
    return info


# ----------------------------------------------------------------------------- packing
def pack_shelf(sizes: list[tuple], bw: int, bh: int):
    order = sorted(range(len(sizes)), key=lambda i: (-sizes[i][1], -sizes[i][0]))
    pos: list = [None] * len(sizes)
    x = y = row_h = 0
    for i in order:
        w, h = sizes[i]
        if w > bw:
            return None
        if x + w > bw:
            x, y, row_h = 0, y + row_h, 0
        if y + h > bh:
            return None
        pos[i] = (x, y)
        x += w
        row_h = max(row_h, h)
    return pos


def pack_maxrects(sizes: list[tuple], bw: int, bh: int):
    free = [(0, 0, bw, bh)]
    pos: list = [None] * len(sizes)
    for i in sorted(range(len(sizes)), key=lambda i: -max(sizes[i])):
        w, h = sizes[i]
        best = None  # best short side fit, then long side
        for fx, fy, fw, fh in free:
            if w <= fw and h <= fh:
                score = (min(fw - w, fh - h), max(fw - w, fh - h))
                if best is None or score < best[0]:
                    best = (score, fx, fy)
        if best is None:
            return None
        _, px, py = best
        pos[i] = (px, py)
        nxt = []
        for fx, fy, fw, fh in free:
            if px >= fx + fw or px + w <= fx or py >= fy + fh or py + h <= fy:
                nxt.append((fx, fy, fw, fh))
                continue
            if px > fx:
                nxt.append((fx, fy, px - fx, fh))
            if px + w < fx + fw:
                nxt.append((px + w, fy, fx + fw - px - w, fh))
            if py > fy:
                nxt.append((fx, fy, fw, py - fy))
            if py + h < fy + fh:
                nxt.append((fx, py + h, fw, fy + fh - py - h))
        free = [r for r in nxt if not any(o is not r and o[0] <= r[0] and o[1] <= r[1] and
                                           o[0] + o[2] >= r[0] + r[2] and o[1] + o[3] >= r[1] + r[3] for o in nxt)]
    return pos


def pack(sizes: list[tuple], packer: str, max_size: int, force_pot: bool):
    """Return (positions, atlas_w, atlas_h) trying growing power-of-two bins; None if it never fits."""
    area = sum(w * h for w, h in sizes)
    side = 1 << max(5, math.ceil(math.log2(max(1, math.sqrt(area)))))
    fn = pack_maxrects if packer == "maxrects" else pack_shelf
    tries = []
    while side <= max_size:
        tries += [(side, side), (side * 2, side)] if side * 2 <= max_size else [(side, side)]
        side *= 2
    for bw, bh in tries:
        pos = fn(sizes, bw, bh)
        if pos is not None:
            uw = max(p[0] + s[0] for p, s in zip(pos, sizes))
            uh = max(p[1] + s[1] for p, s in zip(pos, sizes))
            if force_pot:
                uw, uh = 1 << (uw - 1).bit_length(), 1 << (uh - 1).bit_length()
            return pos, uw, uh
    return None


# ----------------------------------------------------------------------------- Pillow ops
def pillow():
    try:
        from PIL import Image
        return Image
    except ImportError:
        raise ImageError("Pillow is required for this command: pip install pillow  (or: uv run --with pillow python3 image_post.py ...)")


def op_palette(src: Path, colors: int, out) -> dict:
    Image = pillow()
    im = Image.open(src).convert("RGBA")
    q = im.convert("RGB").quantize(colors=colors, method=Image.MEDIANCUT)
    pal = q.getpalette()[:colors * 3]
    counts = dict((i, c) for c, i in q.getcolors())
    hexes = ["#%02X%02X%02X" % tuple(pal[i * 3:i * 3 + 3]) for i in sorted(counts, key=lambda i: -counts[i])]
    if out:
        res = q.convert("RGBA")
        res.putalpha(im.getchannel("A"))
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        res.save(out)
    return {"in": str(src), "out": str(out) if out else None, "colors": len(hexes), "palette": hexes, "ok": True}


def op_resize(src: Path, out: Path, width, height, scale, resample: str) -> dict:
    Image = pillow()
    im = Image.open(src)
    if scale:
        w, h = max(1, round(im.width * scale)), max(1, round(im.height * scale))
    elif width:
        w, h = width, height or max(1, round(im.height * width / im.width))
    else:
        raise ValueError("resize needs --width or --scale")
    filt = Image.NEAREST if resample == "nearest" else Image.LANCZOS
    out.parent.mkdir(parents=True, exist_ok=True)
    im.resize((w, h), filt).save(out)
    return {"in": str(src), "out": str(out), "from": [im.width, im.height], "to": [w, h], "ok": True}


def op_pixelate(src: Path, out: Path, block: int) -> dict:
    Image = pillow()
    im = Image.open(src).convert("RGBA")
    small = im.resize((max(1, im.width // block), max(1, im.height // block)), Image.BOX)
    out.parent.mkdir(parents=True, exist_ok=True)
    small.resize(im.size, Image.NEAREST).save(out)
    return {"in": str(src), "out": str(out), "block": block, "size": [im.width, im.height], "ok": True}


def op_atlas(srcs: list[Path], out: Path, packer: str, max_size: int, padding: int, force_pot: bool) -> dict:
    Image = pillow()
    ims = [Image.open(p).convert("RGBA") for p in srcs]
    sizes = [(im.width + padding, im.height + padding) for im in ims]
    res = pack(sizes, packer, max_size, force_pot)
    if res is None:
        return {"ok": False, "error": "%d sprites do not fit in %dx%d" % (len(ims), max_size, max_size)}
    pos, aw, ah = res
    sheet = Image.new("RGBA", (aw, ah), (0, 0, 0, 0))
    frames = {}
    for p, im, (x, y) in zip(srcs, ims, pos):
        sheet.paste(im, (x, y))
        name, n = p.stem, 2
        while name in frames:
            name, n = "%s_%d" % (p.stem, n), n + 1
        frames[name] = {"x": x, "y": y, "w": im.width, "h": im.height}
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    meta = {"image": out.name, "size": [aw, ah], "packer": packer, "padding": padding, "frames": frames}
    out.with_suffix(".json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    used = sum(w * h for w, h in sizes)
    return {"out": str(out), "json": str(out.with_suffix(".json")), "size": [aw, ah], "sprites": len(ims),
            "fill_ratio": round(used / (aw * ah), 3), "ok": True}


# ----------------------------------------------------------------------------- selftest
def make_png(w: int, h: int, ctype: int = 6, trns: bool = False) -> bytes:
    def chunk(k: bytes, d: bytes) -> bytes:
        return struct.pack(">I", len(d)) + k + d + struct.pack(">I", zlib.crc32(k + d) & 0xFFFFFFFF)
    ch = {0: 1, 2: 3, 4: 2, 6: 4}[ctype]
    raw = b"".join(b"\x00" + bytes([(x * 7) % 256 for x in range(w * ch)]) for _ in range(h))
    return PNG_SIG + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, ctype, 0, 0, 0)) + \
        (chunk(b"tRNS", b"\x00\x00") if trns else b"") + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")


def selftest() -> int:
    assert parse_header(make_png(4, 8)) == {"format": "png", "width": 4, "height": 8, "alpha": True, "bit_depth": 8}
    assert parse_header(make_png(5, 3, 2))["alpha"] is False
    assert parse_header(make_png(5, 3, 0, trns=True))["alpha"] is True
    jpeg = b"\xff\xd8\xff\xe0\x00\x04ab\xff\xc0\x00\x11\x08\x01\x00\x02\x00\x03\x01\x22\x00\x02\x11\x01\x03\x11\x01"
    j = parse_header(jpeg)
    assert (j["format"], j["width"], j["height"], j["alpha"]) == ("jpeg", 512, 256, False), j
    try:
        parse_header(b"GIF89a....")
        raise SystemExit("expected ImageError")
    except ImageError:
        pass
    import random
    rnd = random.Random(3)
    sizes = [(rnd.randint(8, 60), rnd.randint(8, 60)) for _ in range(40)]
    for packer in ("maxrects", "shelf"):
        r = pack(sizes, packer, 512, False)
        assert r is not None, packer
        pos, aw, ah = r
        rects = [(x, y, x + w, y + h) for (x, y), (w, h) in zip(pos, sizes)]
        assert all(0 <= a and 0 <= b and c <= aw and d <= ah for a, b, c, d in rects)
        for i in range(len(rects)):
            for j in range(i + 1, len(rects)):
                a, b = rects[i], rects[j]
                assert a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1], (packer, i, j)
    assert pack([(300, 300)] * 4, "maxrects", 256, False) is None
    with tempfile.TemporaryDirectory() as td:
        t = Path(td)
        (t / "a.png").write_bytes(make_png(16, 16))
        (t / "b.png").write_bytes(make_png(20, 10, 2))
        (t / "junk.png").write_bytes(b"nope")
        assert check_file(t / "a.png", need_pot=True)["ok"]
        r = check_file(t / "b.png")
        assert r["ok"] and r["issues"][0]["severity"] == "warning"
        assert not check_file(t / "b.png", need_pot=True)["ok"]
        assert not check_file(t / "a.png", no_alpha=True)["ok"]
        assert not check_file(t / "a.png", max_kb=0.01)["ok"] and not check_file(t / "a.png", max_dim=8)["ok"]
        assert not check_file(t / "junk.png")["ok"] and not check_file(t / "missing.png")["ok"]
        try:
            pillow()
        except ImageError:
            print("selftest ok (Pillow missing: palette/resize/pixelate/atlas skipped)")
            return 0
        from PIL import Image
        assert op_resize(t / "a.png", t / "r.png", None, None, 0.5, "nearest")["to"] == [8, 8]
        assert Image.open(t / "r.png").size == (8, 8)
        assert op_resize(t / "b.png", t / "r2.png", 40, None, None, "lanczos")["to"] == [40, 20]
        assert Image.open(op_pixelate(t / "a.png", t / "p.png", 4) and t / "p.png").size == (16, 16)
        pal = op_palette(t / "a.png", 4, t / "q.png")
        assert 1 <= pal["colors"] <= 4 and pal["palette"][0].startswith("#")
        r = op_atlas([t / "a.png", t / "b.png"], t / "out" / "atlas.png", "maxrects", 256, 1, True)
        meta = json.loads((t / "out" / "atlas.json").read_text(encoding="utf-8"))
        assert r["ok"] and set(meta["frames"]) == {"a", "b"} and is_pot(meta["size"][0]) and is_pot(meta["size"][1]), meta
        assert Image.open(t / "out" / "atlas.png").size == tuple(meta["size"])
        assert op_atlas([t / "a.png"] * 3, t / "x.png", "shelf", 16, 0, False)["ok"] is False
    print("selftest ok")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Image checks (stdlib) and post-processing (optional Pillow).")
    ap.add_argument("command", nargs="?", choices=["check", "palette", "resize", "atlas", "pixelate"])
    ap.add_argument("--in", dest="inputs", nargs="+", metavar="PATH")
    ap.add_argument("--out")
    ap.add_argument("--max-kb", type=float)
    ap.add_argument("--max-dim", type=int)
    ap.add_argument("--pot", action="store_true", help="check: require power-of-two; atlas: round atlas size up to power-of-two")
    ap.add_argument("--no-alpha", action="store_true")
    ap.add_argument("--colors", type=int, default=16)
    ap.add_argument("--width", type=int)
    ap.add_argument("--height", type=int)
    ap.add_argument("--scale", type=float)
    ap.add_argument("--resample", choices=["nearest", "lanczos"], default="nearest")
    ap.add_argument("--block", type=int, default=4)
    ap.add_argument("--packer", choices=["maxrects", "shelf"], default="maxrects")
    ap.add_argument("--max-size", type=int, default=2048)
    ap.add_argument("--padding", type=int, default=1)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    try:
        a = ap.parse_args(argv)
    except SystemExit as e:
        return 2 if e.code else 0
    if a.selftest:
        return selftest()
    if not a.command or not a.inputs:
        print("error: command and --in are required", file=sys.stderr)
        return 2
    paths = [Path(p) for p in a.inputs]
    missing = [str(p) for p in paths if not p.is_file()]
    if missing and a.command != "check":
        print("error: input not found: %s" % ", ".join(missing), file=sys.stderr)
        return 2
    if a.command in ("resize", "pixelate", "atlas") and not a.out:
        print("error: --out is required for %s" % a.command, file=sys.stderr)
        return 2
    try:
        if a.command == "check":
            files = [check_file(p, a.max_kb, a.max_dim, a.pot, a.no_alpha) for p in paths]
            res = {"files": files, "ok": all(f["ok"] for f in files)}
        elif a.command == "palette":
            res = op_palette(paths[0], a.colors, a.out)
        elif a.command == "resize":
            res = op_resize(paths[0], Path(a.out), a.width, a.height, a.scale, a.resample)
        elif a.command == "pixelate":
            res = op_pixelate(paths[0], Path(a.out), max(1, a.block))
        else:
            res = op_atlas(paths, Path(a.out), a.packer, a.max_size, a.padding, a.pot)
    except ValueError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    except ImageError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    except OSError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    if a.json:
        print(json.dumps(res, indent=2))
    elif a.command == "check":
        for f in res["files"]:
            print("%s %s" % ("PASS" if f["ok"] else "FAIL", f["path"]) +
                  ("" if "width" not in f else "  %s %dx%d alpha=%s pot=%s %d bytes" % (f["format"], f["width"], f["height"], f["alpha"], f["pot"], f["bytes"])))
            for i in f["issues"]:
                print("    [%s] %s" % (i["severity"], i["message"]))
    else:
        print(json.dumps({k: v for k, v in res.items() if k != "ok"}) if res.get("ok") else "error: " + res.get("error", "failed"))
    return 0 if res.get("ok") else 1


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows pipes default to the ANSI code page; Claude Code reads UTF-8
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
