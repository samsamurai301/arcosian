#!/usr/bin/env python3
"""level_import.py - turn Tiled and LDtk levels into one normalised JSON, then check them.

The level editors store maps in their own formats. This tool reads them with the
standard library only, writes one engine-neutral file (format "arcosian-level/1"),
and runs structural checks on it: can the player get from the spawn to every exit,
are pickups and enemies reachable, where are the dead ends, and how are entities
paced along the shortest route. It builds on the core `level_audit.py`: `convert
--audit-out` writes a level-spec file (grid layout) that the audit can read.

    level_import.py convert MAP.tmj|MAP.tmx|PROJECT.ldtk --out level.json
                    [--level NAME] [--solid-layer NAME ...] [--solid-values 1,wall]
                    [--solid-property KEY] [--role TYPE=ROLE ...]
                    [--audit-out spec.level.json] [--level-id ID] [--omit-layer-data]
    level_import.py check level.json [--mode topdown|platformer] [--preset PRESET]
                    [--jump-height N --jump-distance N] [--diagonal] [--screen-tiles N]
                    [--strict] [--out report.json]
    level_import.py --selftest

Formats read: Tiled TMJ (JSON) and TMX (XML), tile data as CSV or base64 (none, zlib,
gzip; zstd is refused with a message), finite and infinite (chunked) maps, embedded and
external tilesets. LDtk: single-file projects and projects with separate level files.
Only orthogonal Tiled maps are supported.

Exit codes: 0 ok (warnings allowed), 1 check failed (unreachable exit, no spawn, errors),
2 usage or input error. Stdlib only, Python 3.9+.
"""
from __future__ import annotations

import argparse
import base64
import bisect
import gzip
import heapq
import json
import math
import re
import struct
import sys
import tempfile
import xml.etree.ElementTree as ET
import zlib
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

FORMAT = "arcosian-level/1"
GID_MASK = 0x1FFFFFFF  # clears the four flip flags in bits 29-32
ROLES = ("spawn", "exit", "enemy", "pickup", "hazard", "other")

AUTO_SOLID_LAYER_NAMES = {"collision", "collisions", "solid", "solids", "wall", "walls",
                          "ground", "blocking", "blocked", "collider", "colliders"}
AUTO_SOLID_PROPS = ("solid", "collision", "collides", "blocked", "blocks")
AUTO_SOLID_VALUE_NAMES = {"wall", "walls", "solid", "ground", "block", "blocked", "collision"}

ROLE_TOKENS = (  # order matters: the first role with a matching token wins
    ("enemy", {"enemy", "enemies", "mob", "monster", "foe", "hostile", "boss"}),
    ("hazard", {"hazard", "spike", "spikes", "lava", "trap"}),
    ("pickup", {"pickup", "coin", "coins", "gem", "item", "key", "collectible", "health",
                "heart", "ammo", "powerup", "star"}),
    ("exit", {"exit", "goal", "finish", "levelend", "endpoint"}),
    ("spawn", {"spawn", "playerstart", "start", "player", "hero"}),
)


class ConvertError(Exception):
    """Input that cannot be converted; reported as a usage/input error (exit 2)."""


# --------------------------------------------------------------------------- small helpers

def truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() not in ("", "false", "0", "no")
    return bool(value)


def _tokens(text: str) -> List[str]:
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", text or "")
    return [t for t in re.split(r"[^A-Za-z0-9]+", text.lower()) if t]


def classify(etype: str, name: str, props: Dict[str, Any], tags: Sequence[str],
             role_map: Dict[str, str]) -> str:
    """Pick a role. Precedence: --role map, `role` property, boolean property, tags, type, name."""
    for key in (etype, name):
        if key and key.lower() in role_map:
            return role_map[key.lower()]
    explicit = props.get("role")
    if isinstance(explicit, str) and explicit.strip().lower() in ROLES:
        return explicit.strip().lower()
    for role in ("spawn", "exit", "enemy", "pickup", "hazard"):
        if truthy(props.get(role)) and role in props:
            return role
    for source in (list(tags), [etype], [name]):
        for item in source:
            toks = set(_tokens(item))
            joined = "".join(_tokens(item))
            for role, words in ROLE_TOKENS:
                if toks & words or joined in words:
                    return role
    return "other"


def norm_props(raw: Any) -> Dict[str, Any]:
    """Tiled properties (list of {name,type,value}, or a plain dict) -> dict."""
    if raw is None:
        return {}
    if isinstance(raw, dict):
        return dict(raw)
    out: Dict[str, Any] = {}
    if isinstance(raw, list):
        for p in raw:
            if isinstance(p, dict) and "name" in p:
                out[str(p["name"])] = p.get("value")
    return out


def _coerce(typ: str, val: str) -> Any:
    try:
        if typ == "int":
            return int(val)
        if typ == "float":
            return float(val)
        if typ == "bool":
            return val.strip().lower() == "true"
    except ValueError:
        return val
    return val


def _r(value: float) -> float:
    return round(value + 0.0, 4)


# --------------------------------------------------------------------------- Tiled: parsing

def _xml_props(el: ET.Element) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    box = el.find("properties")
    if box is None:
        return out
    for p in box.findall("property"):
        name = p.get("name")
        if name is None:
            continue
        typ = p.get("type", "string")
        if typ == "class":
            out[name] = _xml_props(p)
            continue
        val = p.get("value")
        if val is None:
            val = p.text or ""
        out[name] = _coerce(typ, val)
    return out


def _xml_data(node: ET.Element, enc: Optional[str]) -> Tuple[Any, str]:
    if enc == "base64":
        return (node.text or "").strip(), "base64"
    if enc == "csv":
        text = (node.text or "").strip()
        return [int(v) for v in re.split(r"[\s,]+", text) if v], "csv"
    return [int(t.get("gid", "0")) for t in node.findall("tile")], "csv"


def _xml_layers(parent: ET.Element) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for el in parent:
        if el.tag == "layer":
            lay: Dict[str, Any] = {
                "type": "tilelayer", "name": el.get("name", ""), "width": int(el.get("width", "0")),
                "height": int(el.get("height", "0")), "properties": _xml_props(el),
                "visible": el.get("visible", "1") != "0"}
            d = el.find("data")
            if d is not None:
                enc, comp = d.get("encoding"), d.get("compression") or ""
                chunks = d.findall("chunk")
                if chunks:
                    lay["chunks"] = []
                    for c in chunks:
                        raw, e = _xml_data(c, enc)
                        lay["chunks"].append({"x": int(c.get("x", "0")), "y": int(c.get("y", "0")),
                                              "width": int(c.get("width", "0")),
                                              "height": int(c.get("height", "0")),
                                              "data": raw, "encoding": e, "compression": comp})
                else:
                    raw, e = _xml_data(d, enc)
                    lay.update({"data": raw, "encoding": e, "compression": comp})
            out.append(lay)
        elif el.tag == "objectgroup":
            objs = []
            for o in el.findall("object"):
                obj: Dict[str, Any] = {
                    "id": int(o.get("id", "0")), "name": o.get("name", ""),
                    "type": o.get("type") or o.get("class") or "",
                    "x": float(o.get("x", "0")), "y": float(o.get("y", "0")),
                    "width": float(o.get("width", "0")), "height": float(o.get("height", "0")),
                    "rotation": float(o.get("rotation", "0")), "properties": _xml_props(o)}
                if o.get("gid") is not None:
                    obj["gid"] = int(o.get("gid", "0"))
                if o.get("template"):
                    obj["template"] = o.get("template")
                if o.find("point") is not None:
                    obj["point"] = True
                if o.find("ellipse") is not None:
                    obj["ellipse"] = True
                for shape in ("polygon", "polyline"):
                    sh = o.find(shape)
                    if sh is not None:
                        pts = []
                        for pair in (sh.get("points") or "").split():
                            px, _, py = pair.partition(",")
                            pts.append({"x": float(px), "y": float(py)})
                        obj[shape] = pts
                objs.append(obj)
            out.append({"type": "objectgroup", "name": el.get("name", ""),
                        "properties": _xml_props(el), "objects": objs,
                        "visible": el.get("visible", "1") != "0"})
        elif el.tag == "group":
            out.append({"type": "group", "name": el.get("name", ""), "properties": _xml_props(el),
                        "layers": _xml_layers(el)})
    return out


def _tileset_from_xml(el: ET.Element) -> Dict[str, Any]:
    tiles: Dict[int, Dict[str, Any]] = {}
    for t in el.findall("tile"):
        tiles[int(t.get("id", "0"))] = _xml_props(t)
    return {"name": el.get("name", ""), "tiles": tiles}


def _tileset_from_json(d: Dict[str, Any]) -> Dict[str, Any]:
    tiles: Dict[int, Dict[str, Any]] = {}
    for t in d.get("tiles", []) or []:
        if isinstance(t, dict) and "id" in t:
            tiles[int(t["id"])] = norm_props(t.get("properties"))
    return {"name": d.get("name", ""), "tiles": tiles}


def _load_external_tileset(base: Path, source: str, warnings: List[str]) -> Dict[str, Any]:
    path = (base / source)
    try:
        if path.suffix.lower() in (".tsj", ".json"):
            return _tileset_from_json(json.loads(path.read_text(encoding="utf-8")))
        root = ET.fromstring(path.read_text(encoding="utf-8"))
        return _tileset_from_xml(root)
    except (OSError, ValueError, ET.ParseError) as exc:
        warnings.append("external tileset %s could not be read (%s); tile properties from it are ignored"
                        % (source, exc))
        return {"name": source, "tiles": {}}


def read_tiled(path: Path, warnings: List[str]) -> Dict[str, Any]:
    """Read TMJ or TMX into one TMJ-like dict (properties as dicts, tilesets resolved)."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ConvertError("cannot read %s: %s" % (path, exc))
    try:
        if path.suffix.lower() in (".tmj", ".json"):
            m = json.loads(text)
            m["properties"] = norm_props(m.get("properties"))
            raw_tilesets = m.get("tilesets", []) or []
            tilesets = []
            for ts in raw_tilesets:
                if "source" in ts and "tiles" not in ts:
                    t = _load_external_tileset(path.parent, ts["source"], warnings)
                else:
                    t = _tileset_from_json(ts)
                t["firstgid"] = int(ts.get("firstgid", 1))
                tilesets.append(t)
            m["tilesets"] = tilesets
            _normalise_json_layers(m.get("layers", []))
            return m
        root = ET.fromstring(text)
    except (ValueError, ET.ParseError) as exc:
        raise ConvertError("cannot parse %s: %s" % (path.name, exc))
    if root.tag != "map":
        raise ConvertError("%s is not a Tiled map (root element is <%s>)" % (path.name, root.tag))
    m = {"orientation": root.get("orientation", "orthogonal"), "width": int(root.get("width", "0")),
         "height": int(root.get("height", "0")), "tilewidth": int(root.get("tilewidth", "0")),
         "tileheight": int(root.get("tileheight", "0")),
         "infinite": root.get("infinite", "0") == "1", "tiledversion": root.get("tiledversion"),
         "version": root.get("version"), "properties": _xml_props(root)}
    tilesets = []
    for ts in root.findall("tileset"):
        if ts.get("source") and ts.find("tile") is None:
            t = _load_external_tileset(path.parent, ts.get("source", ""), warnings)
        else:
            t = _tileset_from_xml(ts)
        t["firstgid"] = int(ts.get("firstgid", "1"))
        tilesets.append(t)
    m["tilesets"] = tilesets
    m["layers"] = _xml_layers(root)
    return m


def _normalise_json_layers(layers: List[Dict[str, Any]]) -> None:
    for lay in layers:
        lay["properties"] = norm_props(lay.get("properties"))
        for o in lay.get("objects", []) or []:
            o["properties"] = norm_props(o.get("properties"))
        if lay.get("type") == "group":
            _normalise_json_layers(lay.get("layers", []))


def decode_tiles(raw: Any, encoding: Optional[str], compression: Optional[str], count: int) -> List[int]:
    """Decode one data block (a whole layer or one chunk) to `count` raw GIDs."""
    if isinstance(raw, list):
        vals = [int(v) for v in raw]
    elif isinstance(raw, str) and (encoding or "csv") == "csv":
        vals = [int(v) for v in re.split(r"[\s,]+", raw.strip()) if v]
    elif isinstance(raw, str) and encoding == "base64":
        blob = base64.b64decode(raw)
        comp = (compression or "").lower()
        if comp == "zstd":
            raise ConvertError(
                "zstd-compressed tile data is not supported (standard library only). In Tiled set "
                "the map's Tile Layer Format to CSV, Base64 (zlib) or Base64 (gzip), or re-export "
                "the map as .tmj with CSV data")
        try:
            # cap the output at the expected size (+1 to detect excess), so a crafted file cannot exhaust memory
            if comp == "zlib":
                blob = zlib.decompressobj().decompress(blob, 4 * count + 1)
            elif comp == "gzip":
                blob = zlib.decompressobj(16 + zlib.MAX_WBITS).decompress(blob, 4 * count + 1)
            elif comp:
                raise ConvertError("unknown tile data compression %r" % comp)
        except zlib.error as exc:
            raise ConvertError("tile data could not be decompressed (%s)" % exc)
        if len(blob) != 4 * count:
            raise ConvertError("tile data holds %d bytes, expected %d" % (len(blob), 4 * count))
        vals = list(struct.unpack("<%dI" % count, blob))
    else:
        raise ConvertError("unsupported tile data encoding %r" % encoding)
    if len(vals) != count:
        raise ConvertError("tile data holds %d tiles, expected %d" % (len(vals), count))
    return vals


def _layer_cells(lay: Dict[str, Any]) -> Dict[Tuple[int, int], int]:
    """Sparse {(x, y): gid without flip flags} in the map's own coordinates (may be negative)."""
    cells: Dict[Tuple[int, int], int] = {}
    if lay.get("chunks"):
        for ch in lay["chunks"]:
            w, h = int(ch["width"]), int(ch["height"])
            vals = decode_tiles(ch.get("data"), ch.get("encoding") or lay.get("encoding"),
                                ch.get("compression", lay.get("compression")), w * h)
            for i, v in enumerate(vals):
                g = v & GID_MASK
                if g:
                    cells[(int(ch["x"]) + i % w, int(ch["y"]) + i // w)] = g
    elif lay.get("data") is not None:
        w, h = int(lay.get("width", 0)), int(lay.get("height", 0))
        vals = decode_tiles(lay["data"], lay.get("encoding"), lay.get("compression"), w * h)
        for i, v in enumerate(vals):
            g = v & GID_MASK
            if g:
                cells[(int(lay.get("x", 0)) + i % w, int(lay.get("y", 0)) + i // w)] = g
    return cells


def _flatten(layers: List[Dict[str, Any]], prefix: str = "") -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for lay in layers:
        full = prefix + lay.get("name", "")
        if lay.get("type") == "group":
            out.extend(_flatten(lay.get("layers", []), full + "/"))
        else:
            lay = dict(lay)
            lay["_path"] = full
            out.append(lay)
    return out


def _poly_contains(pts: List[Tuple[float, float]], x: float, y: float) -> bool:
    inside = False
    j = len(pts) - 1
    for i in range(len(pts)):
        xi, yi = pts[i]
        xj, yj = pts[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def _object_box(o: Dict[str, Any], tw: int, th: int) -> Tuple[float, float, float, float]:
    """(left, top, width, height) in pixels."""
    x, y = float(o.get("x", 0)), float(o.get("y", 0))
    w, h = float(o.get("width", 0)), float(o.get("height", 0))
    if o.get("gid") is not None:
        w = w or tw
        h = h or th
        return x, y - h, w, h  # tile objects are anchored bottom-left
    for shape in ("polygon", "polyline"):
        pts = o.get(shape)
        if pts:
            xs = [x + float(p["x"]) for p in pts]
            ys = [y + float(p["y"]) for p in pts]
            return min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)
    return x, y, w, h


def _solid_from_object(o: Dict[str, Any], tw: int, th: int, ox: int, oy: int,
                       solid: List[List[bool]], warnings: List[str]) -> None:
    H, W = len(solid), len(solid[0]) if solid else 0
    if o.get("rotation"):
        warnings.append("collision object %s is rotated; rotation ignored" % o.get("id"))
    left, top, w, h = _object_box(o, tw, th)
    poly = o.get("polygon")
    ell = bool(o.get("ellipse"))
    if o.get("point") or o.get("polyline") or (w <= 0 and h <= 0 and not poly):
        return
    pts = [(float(o.get("x", 0)) + float(p["x"]), float(o.get("y", 0)) + float(p["y"]))
           for p in poly] if poly else None
    for cy in range(max(0, int(top // th) - oy), min(H, int((top + h) // th) - oy + 1)):
        for cx in range(max(0, int(left // tw) - ox), min(W, int((left + w) // tw) - ox + 1)):
            px, py = (cx + ox + 0.5) * tw, (cy + oy + 0.5) * th
            if pts is not None:
                hit = _poly_contains(pts, px, py)
            elif ell:
                rx, ry = max(w / 2, 1e-9), max(h / 2, 1e-9)
                hit = ((px - left - rx) / rx) ** 2 + ((py - top - ry) / ry) ** 2 <= 1.0
            else:
                hit = left <= px <= left + w and top <= py <= top + h
            if hit:
                solid[cy][cx] = True


def _name_matches(layer_path: str, wanted: str) -> bool:
    wanted = wanted.lower()
    return layer_path.lower() == wanted or layer_path.lower().rsplit("/", 1)[-1] == wanted


def convert_tiled(path: Path, opts: argparse.Namespace, role_map: Dict[str, str]) -> Dict[str, Any]:
    warnings: List[str] = []
    m = read_tiled(path, warnings)
    orient = m.get("orientation", "orthogonal")
    if orient != "orthogonal":
        raise ConvertError("map orientation %r is not supported; only orthogonal maps convert" % orient)
    tw, th = int(m.get("tilewidth", 0)), int(m.get("tileheight", 0))
    if tw <= 0 or th <= 0:
        raise ConvertError("map has no tile size")
    if getattr(opts, "level", None):
        warnings.append("--level is ignored for Tiled maps (one map per file)")
    infinite = bool(m.get("infinite"))
    flat = _flatten(m.get("layers", []))
    tile_layers = [lay for lay in flat if lay.get("type") == "tilelayer"]
    obj_layers = [lay for lay in flat if lay.get("type") == "objectgroup"]
    cells = {id(lay): _layer_cells(lay) for lay in tile_layers}
    for lay in flat:
        if lay.get("offsetx") or lay.get("offsety"):
            warnings.append("layer %r has a pixel offset; offsets are ignored" % lay["_path"])

    # object positions in tile units, needed for the bounding box of infinite maps
    objs_by_layer: Dict[int, List[Dict[str, Any]]] = {id(lay): lay.get("objects", []) or [] for lay in obj_layers}
    if infinite:
        xs: List[int] = []
        ys: List[int] = []
        for c in cells.values():
            for (x, y) in c:
                xs.append(x)
                ys.append(y)
        for objs in objs_by_layer.values():
            for o in objs:
                left, top, w, h = _object_box(o, tw, th)
                xs.append(int(math.floor((left + w / 2) / tw)))
                ys.append(int(math.floor((top + h / 2) / th)))
        if not xs:
            raise ConvertError("infinite map is empty")
        ox, oy = min(xs), min(ys)
        W, H = max(xs) - ox + 1, max(ys) - oy + 1
    else:
        ox = oy = 0
        W, H = int(m.get("width", 0)), int(m.get("height", 0))
        if W <= 0 or H <= 0:
            raise ConvertError("map has no size")

    firsts = [ts["firstgid"] for ts in sorted(m["tilesets"], key=lambda t: t["firstgid"])]
    sets = sorted(m["tilesets"], key=lambda t: t["firstgid"])

    def tile_props(gid: int) -> Dict[str, Any]:
        i = bisect.bisect_right(firsts, gid) - 1
        if i < 0:
            return {}
        return sets[i]["tiles"].get(gid - sets[i]["firstgid"], {})

    # ---- choose solid sources
    chosen: List[Dict[str, Any]] = []
    prop_key: Optional[str] = None
    notes: List[str] = []
    if opts.solid_layer:
        for want in opts.solid_layer:
            hits = [lay for lay in tile_layers + obj_layers if _name_matches(lay["_path"], want)]
            if not hits:
                raise ConvertError("no layer named %r; layers are: %s"
                                   % (want, ", ".join(l["_path"] for l in tile_layers + obj_layers) or "none"))
            chosen.extend(h for h in hits if not any(h is c for c in chosen))
            notes.append("layer %s" % want)
    if opts.solid_property:
        prop_key = opts.solid_property
        notes.append("tile property %s" % prop_key)
    if not chosen and not prop_key:
        for lay in tile_layers + obj_layers:
            low = lay["_path"].lower().rsplit("/", 1)[-1]
            props = {k.lower(): v for k, v in lay.get("properties", {}).items()}
            if low in AUTO_SOLID_LAYER_NAMES or any(truthy(props.get(k)) and k in props for k in ("solid", "collision")):
                chosen.append(lay)
                notes.append("layer %s (auto)" % lay["_path"])
        if not chosen:
            for key in AUTO_SOLID_PROPS:
                if any(key in p for ts in sets for p in ts["tiles"].values()):
                    prop_key = key
                    notes.append("tile property %s (auto)" % key)
                    break
    solid = [[False] * W for _ in range(H)]
    for lay in chosen:
        if lay.get("type") == "tilelayer":
            for (x, y) in cells[id(lay)]:
                if 0 <= x - ox < W and 0 <= y - oy < H:
                    solid[y - oy][x - ox] = True
        else:
            for o in lay.get("objects", []) or []:
                _solid_from_object(o, tw, th, ox, oy, solid, warnings)
    if prop_key:
        for lay in tile_layers:
            if any(lay is c for c in chosen):
                continue
            for (x, y), gid in cells[id(lay)].items():
                if 0 <= x - ox < W and 0 <= y - oy < H and prop_key in tile_props(gid) \
                        and truthy(tile_props(gid)[prop_key]):
                    solid[y - oy][x - ox] = True
    if not notes:
        warnings.append("no collision source found (no layer named collision/solid/walls, no tile property "
                        "solid/collision); every cell is walkable. Use --solid-layer or --solid-property")

    # ---- layers
    layers_out: List[Dict[str, Any]] = []
    for lay in tile_layers:
        c = cells[id(lay)]
        entry: Dict[str, Any] = {"name": lay["_path"], "kind": "tiles", "width": W, "height": H,
                                 "visible": lay.get("visible", True), "tile_count": len(c)}
        if not opts.omit_layer_data:
            flatdata = [0] * (W * H)
            for (x, y), g in c.items():
                if 0 <= x - ox < W and 0 <= y - oy < H:
                    flatdata[(y - oy) * W + (x - ox)] = g
            entry["data"] = flatdata
        layers_out.append(entry)
    for lay in obj_layers:
        layers_out.append({"name": lay["_path"], "kind": "objects",
                           "object_count": len(objs_by_layer[id(lay)]), "visible": lay.get("visible", True)})

    # ---- entities
    entities: List[Dict[str, Any]] = []
    for lay in obj_layers:
        if any(lay is c for c in chosen):
            continue
        for o in objs_by_layer[id(lay)]:
            if o.get("template"):
                warnings.append("object %s uses template %s that was not resolved; export the map with "
                                "--detach-templates to inline it" % (o.get("id"), o["template"]))
            left, top, w, h = _object_box(o, tw, th)
            props = norm_props(o.get("properties"))
            etype = o.get("type") or o.get("class") or ""
            name = o.get("name", "")
            role = classify(etype, name, props, [], role_map)
            is_point = bool(o.get("point"))
            cx = int(math.floor((left + (0 if is_point else w / 2)) / tw)) - ox
            cy = int(math.floor((top + (0 if is_point else h / 2)) / th)) - oy
            entities.append({
                "type": etype or name, "name": name, "role": role,
                "x": _r(left / tw - ox), "y": _r(top / th - oy), "w": _r(w / tw), "h": _r(h / th),
                "cell": [cx, cy], "layer": lay["_path"], "properties": props})

    return {
        "format": FORMAT, "name": path.stem,
        "source": {"file": path.name, "editor": "tiled", "editor_version": m.get("tiledversion"),
                   "level": None},
        "grid": {"width": W, "height": H}, "tile_size": [tw, th], "origin": [ox, oy],
        "layers": layers_out,
        "solid": {"source": "; ".join(notes) or "none", "legend": {"#": "solid", ".": "walkable"},
                  "rows": ["".join("#" if v else "." for v in row) for row in solid]},
        "entities": entities,
        "metadata": {"properties": m.get("properties", {}), "orientation": orient, "infinite": infinite,
                     "tilesets": [t.get("name", "") for t in sets]},
        "warnings": warnings,
    }


# --------------------------------------------------------------------------- LDtk

def _ldtk_levels(proj: Dict[str, Any]) -> List[Dict[str, Any]]:
    levels = list(proj.get("levels") or [])
    if not levels:
        for w in proj.get("worlds") or []:
            levels.extend(w.get("levels") or [])
    return levels


def convert_ldtk(path: Path, opts: argparse.Namespace, role_map: Dict[str, str]) -> Dict[str, Any]:
    warnings: List[str] = []
    try:
        proj = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ConvertError("cannot read %s: %s" % (path.name, exc))
    if not isinstance(proj, dict) or "defs" not in proj:
        raise ConvertError("%s does not look like an LDtk project (no 'defs')" % path.name)
    levels = _ldtk_levels(proj)
    if not levels:
        raise ConvertError("the project has no levels")
    want = getattr(opts, "level", None)
    if want:
        hits = [lv for lv in levels if want in (lv.get("identifier"), lv.get("iid"), str(lv.get("uid")))]
        if not hits:
            raise ConvertError("no level %r; levels are: %s" % (want, ", ".join(lv.get("identifier", "?") for lv in levels)))
        lv = hits[0]
    elif len(levels) == 1:
        lv = levels[0]
    else:
        raise ConvertError("the project has %d levels; pass --level NAME (one of: %s)"
                           % (len(levels), ", ".join(lv.get("identifier", "?") for lv in levels)))
    if lv.get("layerInstances") is None:
        rel = lv.get("externalRelPath")
        if not rel:
            raise ConvertError("level %s has no layer data" % lv.get("identifier"))
        ext = path.parent / rel
        try:
            full = json.loads(ext.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise ConvertError("cannot read external level file %s: %s" % (ext, exc))
        merged = dict(lv)
        merged.update(full)
        lv = merged
    layer_defs = {d.get("uid"): d for d in (proj.get("defs", {}).get("layers") or [])}
    tileset_defs = {d.get("uid"): d for d in (proj.get("defs", {}).get("tilesets") or [])}
    insts: List[Dict[str, Any]] = lv.get("layerInstances") or []

    # ---- pick the main grid size
    def is_solid_name(ident: str) -> bool:
        return ident.lower() in AUTO_SOLID_LAYER_NAMES

    named: List[Dict[str, Any]] = []
    if opts.solid_layer:
        for wnt in opts.solid_layer:
            hits = [li for li in insts if li.get("__identifier", "").lower() == wnt.lower()]
            if not hits:
                raise ConvertError("no layer named %r; layers are: %s"
                                   % (wnt, ", ".join(li.get("__identifier", "?") for li in insts)))
            named.extend(h for h in hits if h not in named)
    notes: List[str] = []
    if not named and not opts.solid_property:
        auto = [li for li in insts if li.get("__type") == "IntGrid" and is_solid_name(li.get("__identifier", ""))]
        if not auto:
            ints = [li for li in insts if li.get("__type") == "IntGrid"]
            if len(ints) == 1:
                auto = ints
        named = auto
        notes = ["layer %s (auto)" % li.get("__identifier") for li in auto]
    else:
        notes = ["layer %s" % li.get("__identifier") for li in named]
        if opts.solid_property:
            notes.append("tile tag %s" % opts.solid_property)
    primary = named[0] if named else next((li for li in insts if li.get("__type") in ("IntGrid", "Tiles", "AutoLayer")), None)
    gs = int((primary or {}).get("__gridSize") or proj.get("defaultGridSize") or 16)
    W = -(-int(lv.get("pxWid", 0)) // gs)
    H = -(-int(lv.get("pxHei", 0)) // gs)
    if W <= 0 or H <= 0:
        raise ConvertError("level has no size")

    def default_values(li: Dict[str, Any]) -> Set[int]:
        d = layer_defs.get(li.get("layerDefUid"), {})
        vals = {int(v.get("value")) for v in d.get("intGridValues") or []
                if set(_tokens(v.get("identifier") or "")) & AUTO_SOLID_VALUE_NAMES}
        return vals or {1}

    def values_from_opt(li: Dict[str, Any]) -> Set[int]:
        if not opts.solid_values:
            return default_values(li)
        d = layer_defs.get(li.get("layerDefUid"), {})
        by_name = {(v.get("identifier") or "").lower(): int(v.get("value")) for v in d.get("intGridValues") or []}
        out: Set[int] = set()
        for tok in opts.solid_values.split(","):
            tok = tok.strip()
            if not tok:
                continue
            if re.fullmatch(r"-?\d+", tok):
                out.add(int(tok))
            elif tok.lower() in by_name:
                out.add(by_name[tok.lower()])
            else:
                raise ConvertError("IntGrid value %r not found in layer %s (values: %s)"
                                   % (tok, li.get("__identifier"), ", ".join(sorted(by_name)) or "none"))
        return out

    def tags_for(li: Dict[str, Any]) -> Dict[int, Set[str]]:
        d = tileset_defs.get(li.get("__tilesetDefUid"), {})
        out: Dict[int, Set[str]] = {}
        for et in d.get("enumTags") or []:
            for tid in et.get("tileIds") or []:
                out.setdefault(int(tid), set()).add(str(et.get("enumValueId", "")).lower())
        return out

    def tiles_of(li: Dict[str, Any]) -> List[Dict[str, Any]]:
        return list(li.get("gridTiles") or []) + list(li.get("autoLayerTiles") or [])

    solid = [[False] * W for _ in range(H)]
    for li in named:
        lgs = int(li.get("__gridSize") or gs)
        if li.get("__type") == "IntGrid":
            vals = values_from_opt(li)
            cw, ch = int(li.get("__cWid", 0)), int(li.get("__cHei", 0))
            csv = li.get("intGridCsv") or []
            for y in range(H):
                for x in range(W):
                    lx = (x * gs + gs // 2) // lgs
                    ly = (y * gs + gs // 2) // lgs
                    if 0 <= lx < cw and 0 <= ly < ch and csv[ly * cw + lx] in vals:
                        solid[y][x] = True
        elif li.get("__type") in ("Tiles", "AutoLayer"):
            for t in tiles_of(li):
                px, py = t.get("px", [0, 0])
                cx, cy = (px + lgs // 2) // gs, (py + lgs // 2) // gs
                if 0 <= cx < W and 0 <= cy < H:
                    solid[cy][cx] = True
        else:
            warnings.append("layer %s is an Entities layer; it cannot be a solid source" % li.get("__identifier"))
    if opts.solid_property:
        key = opts.solid_property.lower()
        for li in insts:
            if li.get("__type") not in ("Tiles", "AutoLayer", "IntGrid") or li in named:
                continue
            tg = tags_for(li)
            lgs = int(li.get("__gridSize") or gs)
            for t in tiles_of(li):
                if key in tg.get(int(t.get("t", -1)), set()):
                    px, py = t.get("px", [0, 0])
                    cx, cy = (px + lgs // 2) // gs, (py + lgs // 2) // gs
                    if 0 <= cx < W and 0 <= cy < H:
                        solid[cy][cx] = True
    if not notes:
        warnings.append("no collision layer found (no IntGrid layer named Collisions/Walls/Solid); every cell is "
                        "walkable. Use --solid-layer and --solid-values")

    # ---- layers
    layers_out: List[Dict[str, Any]] = []
    for li in insts:
        typ = li.get("__type")
        lgs = int(li.get("__gridSize") or gs)
        entry: Dict[str, Any] = {"name": li.get("__identifier"), "kind": {"IntGrid": "intgrid", "Entities": "entities",
                                  "Tiles": "tiles", "AutoLayer": "tiles"}.get(typ, "other"),
                                 "grid_size": lgs, "width": int(li.get("__cWid", 0)),
                                 "height": int(li.get("__cHei", 0)), "visible": li.get("visible", True)}
        if typ == "IntGrid":
            entry["tile_count"] = sum(1 for v in li.get("intGridCsv") or [] if v)
            if not opts.omit_layer_data:
                entry["data"] = list(li.get("intGridCsv") or [])
        elif typ in ("Tiles", "AutoLayer"):
            ts = tiles_of(li)
            entry["tile_count"] = len(ts)
            if not opts.omit_layer_data:
                cw, ch = entry["width"], entry["height"]
                data = [0] * (cw * ch)
                for t in ts:
                    px, py = t.get("px", [0, 0])
                    cx, cy = px // lgs, py // lgs
                    if 0 <= cx < cw and 0 <= cy < ch:
                        data[cy * cw + cx] = int(t.get("t", 0)) + 1
                entry["data"] = data
        elif typ == "Entities":
            entry["entity_count"] = len(li.get("entityInstances") or [])
        layers_out.append(entry)

    # ---- entities
    entities: List[Dict[str, Any]] = []
    for li in insts:
        if li.get("__type") != "Entities":
            continue
        offx = int(li.get("__pxTotalOffsetX", li.get("pxOffsetX", 0)) or 0)
        offy = int(li.get("__pxTotalOffsetY", li.get("pxOffsetY", 0)) or 0)
        for e in li.get("entityInstances") or []:
            fields: Dict[str, Any] = {}
            for f in e.get("fieldInstances") or []:
                fields[f.get("__identifier")] = f.get("__value")
            w, h = float(e.get("width", gs)), float(e.get("height", gs))
            pv = e.get("__pivot") or [0, 0]
            px, py = e.get("px", [0, 0])
            left = px + offx - pv[0] * w
            top = py + offy - pv[1] * h
            tags = list(e.get("__tags") or [])
            ident = e.get("__identifier", "")
            name = fields.get("name") if isinstance(fields.get("name"), str) else ""
            role = classify(ident, name, fields, tags, role_map)
            entities.append({
                "type": ident, "name": name, "role": role,
                "x": _r(left / gs), "y": _r(top / gs), "w": _r(w / gs), "h": _r(h / gs),
                "cell": [int(math.floor((left + w / 2) / gs)), int(math.floor((top + h / 2) / gs))],
                "layer": li.get("__identifier"), "properties": fields, "tags": tags})
    level_fields = {f.get("__identifier"): f.get("__value") for f in lv.get("fieldInstances") or []}
    return {
        "format": FORMAT, "name": lv.get("identifier", path.stem),
        "source": {"file": path.name, "editor": "ldtk", "editor_version": proj.get("jsonVersion"),
                   "level": lv.get("identifier")},
        "grid": {"width": W, "height": H}, "tile_size": [gs, gs], "origin": [0, 0],
        "layers": layers_out,
        "solid": {"source": "; ".join(notes) or "none", "legend": {"#": "solid", ".": "walkable"},
                  "rows": ["".join("#" if v else "." for v in row) for row in solid]},
        "entities": entities,
        "metadata": {"properties": level_fields, "worldLayout": proj.get("worldLayout"),
                     "worldX": lv.get("worldX"), "worldY": lv.get("worldY"),
                     "externalLevels": bool(proj.get("externalLevels"))},
        "warnings": warnings,
    }


# --------------------------------------------------------------------------- audit export

def _audit_id(text: str) -> str:
    s = re.sub(r"[^A-Za-z0-9_.:-]+", "_", text).strip("_.:-") or "level"
    if not s[0].isalnum():
        s = "l" + s
    return s[:128]


def to_audit(level: Dict[str, Any], level_id: Optional[str]) -> Tuple[Dict[str, Any], List[str], List[str]]:
    """Level-spec document (grid layout) plus (derived fields, fields that cannot be derived)."""
    W, H = level["grid"]["width"], level["grid"]["height"]
    rows = [list(r) for r in level["solid"]["rows"]]
    legend = {"#": "wall", ".": "floor"}
    marks = {"spawn": ("P", "spawn"), "exit": ("E", "exit"), "enemy": ("e", "enemy"),
             "hazard": ("^", "hazard"), "pickup": ("$", "pickup")}
    seen: Dict[Tuple[int, int], str] = {}
    shared = 0
    for role in ("spawn", "exit", "enemy", "hazard", "pickup"):  # first listed wins a shared cell
        for e in level["entities"]:
            if e.get("role") != role:
                continue
            x, y = e["cell"]
            if not (0 <= x < W and 0 <= y < H):
                continue
            if (x, y) in seen:
                shared += 1
                continue
            seen[(x, y)] = role
            rows[y][x] = marks[role][0]
            legend[marks[role][0]] = marks[role][1]
    props = level.get("metadata", {}).get("properties", {}) or {}
    doc: Dict[str, Any] = {
        "schema_version": "1.0", "$schema_name": "level-spec",
        "level_id": _audit_id(level_id or level.get("name") or "level"),
        "layout": {"type": "grid", "rows": ["".join(r) for r in rows], "legend": legend},
        "source": level.get("source", {}).get("file"),
    }
    derived = ["level_id", "layout"]
    exits = [e for e in level["entities"] if e.get("role") == "exit"]
    if exits:
        doc["goals"] = [{"type": "reach", "target": "exit", "count": 1}]
        derived.append("goals")
    hazards = [e["cell"] for e in level["entities"] if e.get("role") == "hazard"]
    if hazards:
        doc["obstacles"] = [{"type": "hazard", "cells": hazards}]
        derived.append("obstacles")
    mech = props.get("mechanics") or props.get("mechanic_refs")
    if isinstance(mech, str):
        ids = [m.strip() for m in mech.split(",") if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}", m.strip())]
        if ids:
            doc["mechanic_refs"] = list(dict.fromkeys(ids))
            derived.append("mechanic_refs")
    lim: Dict[str, Any] = {}
    if isinstance(props.get("moves"), int) and not isinstance(props.get("moves"), bool):
        lim["moves"] = props["moves"]
    for k in ("time_sec", "time_limit"):
        if isinstance(props.get(k), (int, float)) and not isinstance(props.get(k), bool) and props[k] > 0:
            lim["time_sec"] = props[k]
            break
    if lim:
        doc["moves_or_time_limit"] = lim
        derived.append("moves_or_time_limit")
    if props.get("teach") in ("teach", "test", "twist", "reward"):
        doc["teach"] = props["teach"]
        derived.append("teach")
    wr = props.get("target_win_rate", props.get("win_rate"))
    if isinstance(wr, (int, float)) and not isinstance(wr, bool) and 0 <= wr <= 1:
        doc["difficulty_target"] = {"win_rate": wr}
        derived.append("difficulty_target")
    notes = ["Imported by level_import.py from %s (%s). Layout keeps collision and the roles spawn/exit/enemy/"
             "hazard/pickup only; tile art, other layers and entity properties are not carried over."
             % (level.get("source", {}).get("file"), level.get("source", {}).get("editor"))]
    if shared:
        notes.append("%d entities shared a cell with a higher-priority entity and are not drawn." % shared)
    doc["notes"] = " ".join(notes)
    derived.append("notes")
    missing = [f for f in ("mechanic_refs", "goals", "moves_or_time_limit", "obstacles", "difficulty_target",
                           "solver", "teach") if f not in doc]
    return doc, derived, missing


# --------------------------------------------------------------------------- check

Cell = Tuple[int, int]


class Grid:
    def __init__(self, level: Dict[str, Any]) -> None:
        self.W = int(level["grid"]["width"])
        self.H = int(level["grid"]["height"])
        rows = level["solid"]["rows"]
        if len(rows) != self.H or any(len(r) != self.W for r in rows):
            raise ConvertError("solid.rows do not match grid size %dx%d" % (self.W, self.H))
        self.s = [[c == "#" for c in r] for r in rows]

    def inside(self, x: int, y: int) -> bool:
        return 0 <= x < self.W and 0 <= y < self.H

    def solid(self, x: int, y: int) -> bool:
        """Outside left, right = wall; above/below = open air."""
        if x < 0 or x >= self.W:
            return True
        if y < 0 or y >= self.H:
            return False
        return self.s[y][x]

    def walkable(self, x: int, y: int) -> bool:
        return self.inside(x, y) and not self.s[y][x]

    def standable(self, x: int, y: int) -> bool:
        return self.walkable(x, y) and y + 1 < self.H and self.s[y + 1][x]


Exploration = Tuple[Dict[Cell, float], Dict[Cell, Optional[Cell]], Dict[Cell, Tuple[float, Cell]],
                    Dict[Cell, Set[Cell]], bool]


def explore_topdown(g: Grid, start: Cell, diagonal: bool) -> Exploration:
    dist: Dict[Cell, float] = {start: 0.0}
    prev: Dict[Cell, Optional[Cell]] = {start: None}
    adj: Dict[Cell, Set[Cell]] = {}
    steps = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0)]
    if diagonal:
        steps += [(1, 1, 1.4142), (1, -1, 1.4142), (-1, 1, 1.4142), (-1, -1, 1.4142)]
    heap = [(0.0, start)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist.get(u, 1e18):
            continue
        for dx, dy, c in steps:
            v = (u[0] + dx, u[1] + dy)
            if not g.walkable(*v):
                continue
            if dx and dy and (not g.walkable(u[0] + dx, u[1]) or not g.walkable(u[0], u[1] + dy)):
                continue  # no corner cutting
            adj.setdefault(u, set()).add(v)
            nd = d + c
            if nd < dist.get(v, 1e18):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(heap, (nd, v))
    touched = {c: (dist[c], c) for c in dist}
    return dist, prev, touched, adj, False


class Jumper:
    """Approximate platformer movement: a body of one cell, parabolic jumps and falls.

    Units are cells and an arbitrary time unit in which a full jump lasts 1. Gravity is
    g = 8 * H, so a full jump rises H cells (plus a 1% margin) and travels D cells sideways. Variable jump
    height (v0 scaled) and partial stick (fraction of D) give shorter jumps. Holding
    the direction against a wall keeps pushing, so a body can slide up and over a ledge.
    """

    HEIGHT_FRACS = (1.0, 0.5, 0.25)
    SPEED_FRACS = (1.0, 0.5)

    def __init__(self, g: Grid, height: float, distance: float) -> None:
        self.g, self.H, self.D = g, height, distance
        self.grav = 8.0 * height
        hs = {float(h) for h in range(1, int(math.floor(height + 1e-9)) + 1)}
        hs.add(float(height))
        self.heights = sorted(hs)

    def _blocked(self, nx: float, cy: float) -> bool:
        col = int(math.floor(nx))
        r0 = int(math.floor(cy - 0.5 + 1e-9))
        r1 = int(math.floor(cy + 0.5 - 1e-9))
        return any(self.g.solid(col, r) for r in range(r0, r1 + 1))

    def simulate(self, px: float, cy: float, vx: float, vy: float) -> Tuple[Optional[Cell], Set[Cell]]:
        g, grav = self.g, self.grav
        touched: Set[Cell] = set()
        for _ in range(4000):
            speed = max(abs(vx), abs(vy), 1e-9)
            dt = min(0.3 / speed, 0.05)
            vy_new = vy + grav * dt
            nx = px + vx * dt
            if not self._blocked(nx, cy):
                px = nx
            col = int(math.floor(px))
            dy = 0.5 * (vy + vy_new) * dt
            ny = cy + dy
            if dy > 0:
                feet = ny + 0.5
                row = int(math.floor(feet))
                if 0 <= row < g.H and g.solid(col, row):
                    land = (col, row - 1)
                    touched.add(land)
                    if g.standable(*land):
                        return land, touched
                    return None, touched
                cy = ny
            elif dy < 0:
                head = ny - 0.5
                row = int(math.floor(head))
                if g.solid(col, row):
                    cy = row + 1.5
                    vy_new = 0.0
                else:
                    cy = ny
            vy = vy_new
            if cy - 0.5 >= g.H:
                return None, touched
            r0 = int(math.floor(cy - 0.5 + 1e-9))
            r1 = int(math.floor(cy + 0.5 - 1e-9))
            for r in range(r0, r1 + 1):
                if g.inside(col, r):
                    touched.add((col, r))
        return None, touched

    def edges(self, node: Cell) -> List[Tuple[Cell, Set[Cell]]]:
        g = self.g
        x, y = node
        out: List[Tuple[Cell, Set[Cell]]] = []
        for d in (-1, 1):
            nx = x + d
            if not g.walkable(nx, y):
                continue
            if g.standable(nx, y):
                out.append(((nx, y), {(nx, y)}))
                continue
            edge_x = (x + 1 - 1e-6) if d > 0 else (x + 1e-6)
            for sf in self.SPEED_FRACS:
                land, t = self.simulate(edge_x + d * 0.002, y + 0.5, d * self.D * sf, 0.0)
                t.add((nx, y))
                out.append((land, t) if land else ((x, y), t))
        for h in self.heights:
            v0 = 4.0 * math.sqrt(self.H * h) * 1.005  # apex 1% above h, so a jump of N clears an N-tile ledge
            out.append(self._jump(x, y, 0.0, v0))
            for d in (-1, 1):
                for sf in self.SPEED_FRACS:
                    out.append(self._jump(x, y, d * self.D * sf, v0))
        return out

    def _jump(self, x: int, y: int, vx: float, v0: float) -> Tuple[Cell, Set[Cell]]:
        land, t = self.simulate(x + 0.5, y + 0.5, vx, -v0)
        return (land if land else (x, y)), t


def explore_platformer(g: Grid, starts: Sequence[Cell], jumper: Jumper, max_nodes: int) -> Exploration:
    dist: Dict[Cell, float] = {}
    prev: Dict[Cell, Optional[Cell]] = {}
    adj: Dict[Cell, Set[Cell]] = {}
    touched: Dict[Cell, Tuple[float, Cell]] = {}
    heap: List[Tuple[float, Cell]] = []
    for s in starts:
        dist[s] = 0.0
        prev[s] = None
        heapq.heappush(heap, (0.0, s))
    done: Set[Cell] = set()
    truncated = False
    while heap:
        d, u = heapq.heappop(heap)
        if u in done or d > dist.get(u, 1e18):
            continue
        done.add(u)
        if len(done) > max_nodes:
            truncated = True
            break
        touched.setdefault(u, (d, u))
        for v, cells in jumper.edges(u):
            for c in cells:
                dd = d + abs(c[0] - u[0]) + abs(c[1] - u[1])
                if c not in touched or dd < touched[c][0]:
                    touched[c] = (dd, u)
            if v == u:
                continue
            adj.setdefault(u, set()).add(v)
            nd = d + max(1, abs(v[0] - u[0]) + abs(v[1] - u[1]))
            if nd < dist.get(v, 1e18):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(heap, (nd, v))
    return dist, prev, touched, adj, truncated


def entity_cells(e: Dict[str, Any]) -> List[Cell]:
    cx, cy = e["cell"]
    w, h = float(e.get("w", 0) or 0), float(e.get("h", 0) or 0)
    if w <= 0 and h <= 0:
        return [(cx, cy)]
    x0, y0 = int(math.floor(e["x"] + 1e-6)), int(math.floor(e["y"] + 1e-6))
    nw, nh = max(1, int(math.ceil(w - 1e-6))), max(1, int(math.ceil(h - 1e-6)))
    return [(x0 + i, y0 + j) for j in range(nh) for i in range(nw)]


PRESETS: Dict[str, Dict[str, Any]] = {
    # starting values, not measured limits; see references/level-checks.md
    "topdown": {"mode": "topdown", "screen_tiles": 20, "min_per_screen": 0.5, "max_per_screen": 6.0,
                "max_empty_screens": 1.5, "max_dead_end_ratio": 0.10, "min_path_tiles": 10, "pacing": True},
    "platformer": {"mode": "platformer", "screen_tiles": 20, "min_per_screen": 1.0, "max_per_screen": 8.0,
                   "max_empty_screens": 1.0, "max_dead_end_ratio": 0.05, "min_path_tiles": 10, "pacing": True},
    "puzzle": {"mode": "topdown", "screen_tiles": 20, "min_per_screen": 0.0, "max_per_screen": 1e9,
               "max_empty_screens": 1e9, "max_dead_end_ratio": 1.0, "min_path_tiles": 4, "pacing": False},
}


def _path_to(prev: Dict[Cell, Optional[Cell]], node: Cell) -> List[Cell]:
    out = [node]
    while prev.get(out[-1]) is not None:
        out.append(prev[out[-1]])  # type: ignore[arg-type]
    out.reverse()
    return out


def _samples(points: Sequence[Cell]) -> List[Tuple[float, float, float]]:
    """Walk the polyline one tile at a time: (x, y, distance along the path)."""
    out: List[Tuple[float, float, float]] = []
    s = 0.0
    for i, p in enumerate(points):
        if i == 0:
            out.append((p[0], p[1], 0.0))
            continue
        q = points[i - 1]
        seg = abs(p[0] - q[0]) + abs(p[1] - q[1])
        n = max(1, int(math.ceil(seg)))
        for k in range(1, n + 1):
            f = k / n
            out.append((q[0] + (p[0] - q[0]) * f, q[1] + (p[1] - q[1]) * f, s + seg * f))
        s += seg
    return out


def check_level(level: Dict[str, Any], opts: argparse.Namespace) -> Dict[str, Any]:
    preset_name = opts.preset or opts.mode or "topdown"
    preset = dict(PRESETS[preset_name])
    mode = opts.mode or preset["mode"]
    for key in ("screen_tiles", "min_per_screen", "max_per_screen", "max_empty_screens",
                "max_dead_end_ratio", "min_path_tiles"):
        val = getattr(opts, key, None)
        if val is not None:
            preset[key] = val
    g = Grid(level)
    findings: List[Dict[str, str]] = []

    def add(sev: str, code: str, msg: str) -> None:
        findings.append({"severity": sev, "code": code, "message": msg})

    ents = level.get("entities", [])
    spawns = [e for e in ents if e.get("role") == "spawn"]
    exits = [e for e in ents if e.get("role") == "exit"]
    report: Dict[str, Any] = {
        "tool": "level_import.py check", "level": level.get("name"), "mode": mode, "preset": preset_name,
        "grid": level["grid"], "thresholds": {k: preset[k] for k in (
            "screen_tiles", "min_per_screen", "max_per_screen", "max_empty_screens", "max_dead_end_ratio",
            "min_path_tiles")},
        "thresholds_note": "starting values (estimates); tune per game"}
    jump_h = opts.jump_height if opts.jump_height is not None else 3.0
    jump_d = opts.jump_distance if opts.jump_distance is not None else 5.0
    if mode == "platformer":
        report["jump"] = {"height_tiles": jump_h, "distance_tiles": jump_d,
                          "assumed": opts.jump_height is None or opts.jump_distance is None}
        if report["jump"]["assumed"]:
            add("info", "jump_assumed", "jump height/distance not given; using %.1f and %.1f tiles. Derive them "
                "from the controller (height = v^2/2g, distance = speed x air time), in tiles" % (jump_h, jump_d))
    if not spawns:
        add("error", "no_spawn", "no entity with role spawn; add one or map a type with --role at convert time")
        return _finish(report, findings, opts)
    if len(spawns) > 1:
        add("warning", "multiple_spawns", "%d spawns; checking from the first (%s)" % (len(spawns), spawns[0].get("type")))
    sx, sy = spawns[0]["cell"]
    report["spawn"] = [sx, sy]
    if not g.inside(sx, sy):
        add("error", "spawn_out_of_bounds", "spawn cell %s is outside the %dx%d grid" % ((sx, sy), g.W, g.H))
        return _finish(report, findings, opts)
    if g.s[sy][sx]:
        add("error", "spawn_in_solid", "spawn cell %s is a solid cell" % ((sx, sy),))
        return _finish(report, findings, opts)
    if not exits:
        add("warning", "no_exit", "no entity with role exit; reachability of an exit was not checked")

    truncated = False
    if mode == "platformer":
        jumper = Jumper(g, jump_h, jump_d)
        if g.standable(sx, sy):
            starts = [(sx, sy)]
            extra: Set[Cell] = {(sx, sy)}
        else:
            starts = []
            extra = set()
            for sf in (0.0,) + Jumper.SPEED_FRACS:
                for d in (-1, 1) if sf else (1,):
                    land, t = jumper.simulate(sx + 0.5, sy + 0.5, d * jump_d * sf, 0.0)
                    extra |= t
                    if land and land not in starts:
                        starts.append(land)
            if not starts:
                add("error", "spawn_falls", "the spawn at %s is in the air and the body falls out of the level" % ((sx, sy),))
                return _finish(report, findings, opts)
        dist, prev, touched, adj, truncated = explore_platformer(g, starts, jumper, opts.max_nodes)
        for c in extra:
            touched.setdefault(c, (0.0, starts[0]))
        if truncated:
            add("warning", "search_truncated", "stopped after %d standing cells (--max-nodes); results are partial"
                % opts.max_nodes)
    else:
        dist, prev, touched, adj, _ = explore_topdown(g, (sx, sy), opts.diagonal)
    nodes = set(dist)
    walkable_total = sum(1 for y in range(g.H) for x in range(g.W) if not g.s[y][x])
    if mode == "platformer":
        stand_total = sum(1 for y in range(g.H) for x in range(g.W) if g.standable(x, y))
        report["reachability"] = {"standable_cells": stand_total, "reachable_standable": len(nodes),
                                  "touchable_cells": len(touched)}
    else:
        report["reachability"] = {"walkable_cells": walkable_total, "reachable_cells": len(nodes),
                                  "reachable_fraction": _r(len(nodes) / walkable_total) if walkable_total else 0.0}

    def reach(e: Dict[str, Any]) -> Optional[Tuple[float, Cell, Cell]]:
        """(distance, takeoff node, touched cell) of the best touched cell, or None."""
        best: Optional[Tuple[float, Cell, Cell]] = None
        for c in entity_cells(e):
            cand: List[Cell] = [c]
            if g.inside(*c) and g.s[c[1]][c[0]]:  # solid cell (a door tile): count a touched neighbour
                cand = [(c[0] + dx, c[1] + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
            for k in cand:
                if k in touched:
                    d, src = touched[k]
                    d = d + (1 if k != c else 0)
                    if best is None or d < best[0]:
                        best = (d, src, k)
        return best

    for e in ents:
        for c in entity_cells(e):
            if not g.inside(*c):
                add("warning", "entity_out_of_bounds", "%s %s at %s is outside the grid" % (e.get("role"), e.get("type"), c))
                break
        if e.get("role") in ("pickup", "enemy") and all(g.inside(*c) and g.s[c[1]][c[0]] for c in entity_cells(e)):
            add("warning", "entity_in_solid", "%s %s at %s sits in a solid cell" % (e.get("role"), e.get("type"), e["cell"]))

    # exits
    exit_rows: List[Dict[str, Any]] = []
    best_exit: Optional[Tuple[float, Cell, Cell]] = None
    for e in exits:
        r = reach(e)
        exit_rows.append({"type": e.get("type"), "cell": e["cell"], "reachable": r is not None,
                          "distance_tiles": _r(r[0]) if r else None})
        if r is None:
            add("error", "exit_unreachable", "exit %s at %s cannot be reached from the spawn" % (e.get("type"), e["cell"]))
        elif best_exit is None or r[0] < best_exit[0]:
            best_exit = r
    report["exits"] = exit_rows

    # pickups and enemies
    for role, label in (("pickup", "pickups"), ("enemy", "enemies")):
        group = [e for e in ents if e.get("role") == role]
        bad = [e for e in group if reach(e) is None]
        report[label] = {"total": len(group), "unreachable": [{"type": e.get("type"), "cell": e["cell"]} for e in bad]}
        if bad:
            add("error" if (role == "pickup" and opts.strict) else "warning", "%s_unreachable" % role,
                "%d of %d %s cannot be reached (first at %s)" % (len(bad), len(group), label, bad[0]["cell"]))

    # path and pacing
    path_samples: List[Tuple[float, float, float]] = []
    if best_exit is not None:
        d, src, cell = best_exit
        chain = _path_to(prev, src) + ([cell] if cell != src else [])
        path_samples = _samples(chain)
        length = path_samples[-1][2] if path_samples else 0.0
        report["path"] = {"nearest_exit_tiles": _r(length), "nodes": len(chain)}
        if length < preset["min_path_tiles"]:
            add("warning", "path_short", "shortest route is %.1f tiles (below %.0f)" % (length, preset["min_path_tiles"]))
    occupied: Set[Cell] = set()
    for e in ents:
        occupied.update(entity_cells(e))
    # dead ends
    dead: List[Cell] = []
    if mode == "platformer":
        indeg: Dict[Cell, Set[Cell]] = {}
        for u, vs in adj.items():
            for v in vs:
                indeg.setdefault(v, set()).add(u)
        for n in nodes:
            deg = len(adj.get(n, set()) | indeg.get(n, set()))
            if deg <= 1 and n not in occupied and n != (sx, sy):
                dead.append(n)
    else:
        for n in nodes:
            deg = sum(1 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if g.walkable(n[0] + dx, n[1] + dy))
            if deg == 1 and n not in occupied and n != (sx, sy):
                dead.append(n)
    dead.sort()
    ratio = len(dead) / len(nodes) if nodes else 0.0
    report["dead_ends"] = {"count": len(dead), "ratio": _r(ratio), "cells": [list(c) for c in dead[:20]]}
    if len(dead) and ratio > preset["max_dead_end_ratio"]:
        add("warning", "dead_ends", "%d dead-end cells (%.0f%% of reachable; limit %.0f%%)"
            % (len(dead), ratio * 100, preset["max_dead_end_ratio"] * 100))
    # traps (platformer only)
    if mode == "platformer" and exit_rows and any(r["reachable"] for r in exit_rows) and not truncated:
        goal_nodes: Set[Cell] = set()
        for e in exits:
            r = reach(e)
            if r:
                goal_nodes.add(r[1])
        rev: Dict[Cell, Set[Cell]] = {}
        for u, vs in adj.items():
            for v in vs:
                rev.setdefault(v, set()).add(u)
        seen = set(goal_nodes)
        stack = list(goal_nodes)
        while stack:
            n = stack.pop()
            for p in rev.get(n, ()):
                if p not in seen:
                    seen.add(p)
                    stack.append(p)
        traps = sorted(n for n in nodes if n not in seen)
        report["traps"] = {"count": len(traps), "cells": [list(c) for c in traps[:20]]}
        if traps:
            add("warning", "softlock_traps", "%d standing cells can be reached but not left towards an exit "
                "(pits, one-way drops); fine only if the game respawns the player there" % len(traps))
    # pacing
    pacing: Dict[str, Any] = {"enabled": bool(preset["pacing"]) and not opts.no_pacing}
    if pacing["enabled"] and path_samples:
        screen = float(preset["screen_tiles"])
        length = path_samples[-1][2]
        radius = max(2.0, screen / 4.0)
        pos: List[float] = []
        off = 0
        for e in ents:
            if e.get("role") not in ("enemy", "pickup", "hazard"):
                continue
            ex, ey = e["cell"]
            bd, bs = 1e18, 0.0
            for (px, py, s) in path_samples:
                dd = max(abs(px - ex), abs(py - ey))
                if dd < bd - 1e-9:
                    bd, bs = dd, s
            if bd <= radius:
                pos.append(bs)
            else:
                off += 1
        pos.sort()
        gaps = [b - a for a, b in zip([0.0] + pos, pos + [length])]
        longest = max(gaps) if gaps else length
        screens = max(length / screen, 1.0)
        density = len(pos) / screens
        win = []
        s0 = 0.0
        while s0 <= max(length - screen, 0.0) + 1e-9:
            win.append(sum(1 for p in pos if s0 <= p < s0 + screen))
            s0 += screen / 4.0
        pacing.update({"route_tiles": _r(length), "screen_tiles": screen, "route_radius_tiles": radius,
                       "entities_on_route": len(pos), "entities_off_route": off,
                       "per_screen": _r(density), "emptiest_screen": min(win) if win else 0,
                       "fullest_screen": max(win) if win else 0, "longest_empty_stretch_tiles": _r(longest)})
        if length >= screen / 2.0:
            if density < preset["min_per_screen"]:
                add("warning", "pacing_sparse", "%.2f entities per screen on the route (min %.2f)" % (density, preset["min_per_screen"]))
            if density > preset["max_per_screen"]:
                add("warning", "pacing_dense", "%.2f entities per screen on the route (max %.2f)" % (density, preset["max_per_screen"]))
            if longest > preset["max_empty_screens"] * screen:
                add("warning", "empty_stretch", "%.0f tiles of route with nothing to do (limit %.0f)"
                    % (longest, preset["max_empty_screens"] * screen))
    report["pacing"] = pacing
    return _finish(report, findings, opts)


def _finish(report: Dict[str, Any], findings: List[Dict[str, str]], opts: argparse.Namespace) -> Dict[str, Any]:
    errors = [f for f in findings if f["severity"] == "error"]
    warns = [f for f in findings if f["severity"] == "warning"]
    report["findings"] = findings
    report["verdict"] = "fail" if errors else ("warn" if warns else "pass")
    report["fail"] = bool(errors) or (bool(warns) and bool(opts.strict))
    return report


# --------------------------------------------------------------------------- CLI

def dumps_level(level: Dict[str, Any]) -> str:
    """Readable JSON: one line per layer and per entity."""
    parts = []
    for key, val in level.items():
        if key in ("layers", "entities") and isinstance(val, list):
            body = ",\n".join("  " + json.dumps(v, separators=(",", ":")) for v in val)
            parts.append(' "%s": [\n%s\n ]' % (key, body) if val else ' "%s": []' % key)
        else:
            parts.append(" %s: %s" % (json.dumps(key), json.dumps(val, indent=1).replace("\n", "\n ")))
    return "{\n" + ",\n".join(parts) + "\n}\n"


def parse_roles(items: Optional[List[str]]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for it in items or []:
        k, sep, v = it.partition("=")
        if not sep or v.strip().lower() not in ROLES or not k.strip():
            raise ConvertError("--role expects TYPE=ROLE with ROLE one of %s, got %r" % (", ".join(ROLES), it))
        out[k.strip().lower()] = v.strip().lower()
    return out


def do_convert(path: Path, opts: argparse.Namespace) -> Dict[str, Any]:
    role_map = parse_roles(opts.role)
    suffix = path.suffix.lower()
    if suffix in (".tmj", ".tmx", ".json"):
        return convert_tiled(path, opts, role_map)
    if suffix == ".ldtk":
        return convert_ldtk(path, opts, role_map)
    if suffix == ".ldtkl":
        raise ConvertError("pass the project (.ldtk), not a single .ldtkl level file")
    raise ConvertError("unknown file type %r; expected .tmj, .tmx or .ldtk" % suffix)


PRESERVED_SPEC_FIELDS = ("solver", "difficulty_target", "teach", "moves_or_time_limit", "mechanic_refs", "notes")


def merge_existing_spec(doc: Dict[str, Any], path: Path) -> List[str]:
    """Keep hand-written or tool-written fields of an existing spec (the core adapter rule: merge, do not overwrite)."""
    if not path.is_file():
        return []
    try:
        old = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    if not isinstance(old, dict):
        return []
    kept: List[str] = []
    for key in PRESERVED_SPEC_FIELDS:
        if key not in old:
            continue
        if key == "notes" and isinstance(old[key], str) and old[key].startswith("Imported by level_import.py"):
            continue  # generated text, regenerate it
        if key not in doc or key == "notes":
            doc[key] = old[key]
            kept.append(key)
    return kept


def cmd_convert(args: argparse.Namespace) -> int:
    src = Path(args.map)
    if not src.is_file():
        print("error: %s not found" % src, file=sys.stderr)
        return 2
    try:
        level = do_convert(src, args)
    except ConvertError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(dumps_level(level), encoding="utf-8")
    summary: Dict[str, Any] = {
        "out": str(out), "name": level["name"], "grid": level["grid"], "tile_size": level["tile_size"],
        "solid_source": level["solid"]["source"],
        "entities": {r: sum(1 for e in level["entities"] if e["role"] == r) for r in ROLES
                     if any(e["role"] == r for e in level["entities"])},
        "warnings": level["warnings"]}
    if args.audit_out:
        doc, derived, missing = to_audit(level, args.level_id)
        ap = Path(args.audit_out)
        ap.parent.mkdir(parents=True, exist_ok=True)
        kept = merge_existing_spec(doc, ap) if not args.overwrite_audit else []
        if kept:
            summary["audit_preserved"] = kept
            missing = [m for m in missing if m not in kept]
        ap.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
        summary["audit_out"] = str(ap)
        summary["audit_derived"] = derived
        summary["audit_not_derivable"] = missing
    print(json.dumps(summary, indent=2))
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    src = Path(args.level)
    try:
        level = json.loads(src.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print("error: cannot read %s: %s" % (src, exc), file=sys.stderr)
        return 2
    if not isinstance(level, dict) or level.get("format") != FORMAT:
        print("error: %s is not an %s file (run convert first)" % (src, FORMAT), file=sys.stderr)
        return 2
    if args.jump_height is not None and args.jump_height <= 0 or args.jump_distance is not None and args.jump_distance <= 0:
        print("error: jump height and distance must be positive", file=sys.stderr)
        return 2
    try:
        report = check_level(level, args)
    except ConvertError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2
    text = json.dumps(report, indent=2)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 1 if report["fail"] else 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="level_import.py", description="Convert Tiled/LDtk levels and check them.")
    p.add_argument("--selftest", action="store_true", help="run offline self-tests and exit")
    sub = p.add_subparsers(dest="cmd")
    c = sub.add_parser("convert", help="normalise a Tiled or LDtk level into one JSON file")
    c.add_argument("map", help=".tmj, .tmx or .ldtk file")
    c.add_argument("--out", required=True, help="output level.json")
    c.add_argument("--level", help="LDtk level identifier (required when the project has several levels)")
    c.add_argument("--solid-layer", action="append", metavar="NAME",
                   help="layer that marks solid cells (repeatable). Tiled: any tile or collision shape; LDtk: IntGrid or tile layer")
    c.add_argument("--solid-values", metavar="LIST", help="LDtk IntGrid values that are solid, numbers or names (default: 1)")
    c.add_argument("--solid-property", metavar="KEY", help="Tiled tile property (or LDtk tile enum tag) that marks a tile solid")
    c.add_argument("--role", action="append", metavar="TYPE=ROLE", help="map an entity type to a role: spawn, exit, enemy, pickup, hazard, other")
    c.add_argument("--audit-out", metavar="FILE", help="also write a level-spec file the core level_audit.py can read")
    c.add_argument("--level-id", help="level_id for --audit-out (default: the level name)")
    c.add_argument("--overwrite-audit", action="store_true",
                   help="replace an existing --audit-out file instead of keeping its solver, difficulty_target, teach, limit, mechanic and notes fields")
    c.add_argument("--omit-layer-data", action="store_true", help="leave tile data out of layers (smaller file)")
    k = sub.add_parser("check", help="reachability, dead ends and pacing for a converted level")
    k.add_argument("level", help="level.json written by convert")
    k.add_argument("--mode", choices=("topdown", "platformer"), help="movement model (default: from --preset, else topdown)")
    k.add_argument("--preset", choices=sorted(PRESETS), help="threshold set (default: the mode)")
    k.add_argument("--jump-height", type=float, help="platformer: highest jump in tiles (default 3, assumed)")
    k.add_argument("--jump-distance", type=float, help="platformer: farthest level jump in tiles (default 5, assumed)")
    k.add_argument("--diagonal", action="store_true", help="top-down: allow diagonal steps (no corner cutting)")
    k.add_argument("--screen-tiles", dest="screen_tiles", type=float, help="screen width in tiles (preset default 20)")
    k.add_argument("--min-per-screen", dest="min_per_screen", type=float)
    k.add_argument("--max-per-screen", dest="max_per_screen", type=float)
    k.add_argument("--max-empty-screens", dest="max_empty_screens", type=float)
    k.add_argument("--max-dead-end-ratio", dest="max_dead_end_ratio", type=float)
    k.add_argument("--min-path-tiles", dest="min_path_tiles", type=float)
    k.add_argument("--no-pacing", action="store_true", help="skip pacing metrics")
    k.add_argument("--max-nodes", type=int, default=20000, help="platformer: stop after this many standing cells")
    k.add_argument("--strict", action="store_true", help="warnings also fail (exit 1)")
    k.add_argument("--out", help="also write the report to this file")
    return p


# --------------------------------------------------------------------------- self-test

def _fixture_objects(tw: int = 16) -> List[Dict[str, Any]]:
    # spawn (1,1), exit (5,2) inside a pocket, enemy (2,3), pickup (5,4)
    return [
        {"id": 1, "name": "start", "type": "PlayerStart", "x": 1 * tw + 8, "y": 1 * tw + 8, "point": True,
         "width": 0, "height": 0, "rotation": 0, "properties": {}},
        {"id": 2, "name": "", "type": "exit", "x": 5 * tw, "y": 2 * tw, "width": tw, "height": tw,
         "rotation": 0, "properties": {}},
        {"id": 3, "name": "grunt", "type": "Enemy", "x": 2 * tw + 8, "y": 3 * tw + 8, "point": True,
         "width": 0, "height": 0, "rotation": 0, "properties": {}},
        {"id": 4, "name": "", "type": "coin", "x": 5 * tw + 8, "y": 4 * tw + 8, "point": True,
         "width": 0, "height": 0, "rotation": 0, "properties": {}},
    ]


def _gids(rows: List[str]) -> List[int]:
    return [1 if ch == "#" else 0 for r in rows for ch in r]


def _pack(vals: List[int], comp: str) -> str:
    raw = struct.pack("<%dI" % len(vals), *vals)
    if comp == "zlib":
        raw = zlib.compress(raw)
    elif comp == "gzip":
        raw = gzip.compress(raw)
    return base64.b64encode(raw).decode("ascii")


def _tmj(rows: List[str], enc: str = "csv", comp: str = "") -> Dict[str, Any]:
    W, H = len(rows[0]), len(rows)
    layer: Dict[str, Any] = {"type": "tilelayer", "name": "Collision", "width": W, "height": H,
                             "x": 0, "y": 0}
    if enc == "csv":
        layer["data"] = _gids(rows)
    else:
        layer.update({"encoding": "base64", "data": _pack(_gids(rows), comp)})
        if comp:
            layer["compression"] = comp
    return {"type": "map", "version": "1.10", "tiledversion": "1.12.2", "orientation": "orthogonal",
            "width": W, "height": H, "tilewidth": 16, "tileheight": 16, "infinite": False,
            "tilesets": [{"firstgid": 1, "name": "t", "tilecount": 1, "tiles": []}],
            "properties": [{"name": "teach", "type": "string", "value": "teach"}],
            "layers": [layer, {"type": "objectgroup", "name": "Entities", "objects": [
                dict(o, properties=[{"name": "k", "type": "int", "value": 1}]) if o["id"] == 3 else o
                for o in _fixture_objects()]}]}


def _tmx(rows: List[str], enc: str = "csv", comp: str = "") -> str:
    W, H = len(rows[0]), len(rows)
    if enc == "csv":
        data = '<data encoding="csv">%s</data>' % ",".join(str(v) for v in _gids(rows))
    else:
        data = '<data encoding="base64"%s>%s</data>' % (' compression="%s"' % comp if comp else "", _pack(_gids(rows), comp))
    objs = []
    for o in _fixture_objects():
        shape = "<point/>" if o.get("point") else ""
        props = '<properties><property name="k" type="int" value="1"/></properties>' if o["id"] == 3 else ""
        objs.append('<object id="%d" name="%s" type="%s" x="%s" y="%s"%s>%s%s</object>' % (
            o["id"], o["name"], o["type"], o["x"], o["y"],
            "" if o.get("point") else ' width="%s" height="%s"' % (o["width"], o["height"]), props, shape))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<map version="1.10" tiledversion="1.12.2" orientation="orthogonal" '
            'width="%d" height="%d" tilewidth="16" tileheight="16" infinite="0">'
            '<properties><property name="teach" value="teach"/></properties>'
            '<tileset firstgid="1" name="t" tilewidth="16" tileheight="16" tilecount="1" columns="1"><tile id="0"/></tileset>'
            '<layer id="1" name="Collision" width="%d" height="%d">%s</layer>'
            '<objectgroup id="2" name="Entities">%s</objectgroup></map>' % (W, H, W, H, data, "".join(objs)))


def _ldtk_level(rows: List[str], with_layers: bool = True) -> Dict[str, Any]:
    W, H, gs = len(rows[0]), len(rows), 16
    csv = [1 if ch == "#" else 0 for r in rows for ch in r]

    def ent(ident: str, cx: int, cy: int, extra: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        return {"__identifier": ident, "__grid": [cx, cy], "px": [cx * gs, cy * gs], "width": gs, "height": gs,
                "__pivot": [0, 0], "__tags": [], "fieldInstances": extra or []}

    layers = [
        {"__identifier": "Entities", "__type": "Entities", "__cWid": W, "__cHei": H, "__gridSize": gs,
         "layerDefUid": 2, "entityInstances": [
             ent("PlayerStart", 1, 1), ent("Exit", 5, 2), ent("Enemy", 2, 3, [
                 {"__identifier": "k", "__type": "Int", "__value": 1}]), ent("Coin", 5, 4)],
         "intGridCsv": [], "gridTiles": [], "autoLayerTiles": []},
        {"__identifier": "Collisions", "__type": "IntGrid", "__cWid": W, "__cHei": H, "__gridSize": gs,
         "layerDefUid": 1, "intGridCsv": csv, "entityInstances": [], "gridTiles": [], "autoLayerTiles": []}]
    return {"identifier": "Level_0", "iid": "aaaa", "uid": 10, "pxWid": W * gs, "pxHei": H * gs, "worldX": 0,
            "worldY": 0, "fieldInstances": [{"__identifier": "teach", "__type": "String", "__value": "teach"}],
            "layerInstances": layers if with_layers else None}


def _ldtk(rows: List[str], external: bool = False) -> Dict[str, Any]:
    lv = _ldtk_level(rows, with_layers=not external)
    if external:
        lv["externalRelPath"] = "Level_0.ldtkl"
    return {"jsonVersion": "1.5.3", "worldLayout": "Free", "externalLevels": external, "defaultGridSize": 16,
            "defs": {"layers": [
                {"uid": 1, "identifier": "Collisions", "type": "IntGrid",
                 "intGridValues": [{"value": 1, "identifier": "wall"}]},
                {"uid": 2, "identifier": "Entities", "type": "Entities"}], "tilesets": []},
            "levels": [lv], "worlds": []}


def _ns(**kw: Any) -> argparse.Namespace:
    base = dict(level=None, solid_layer=None, solid_values=None, solid_property=None, role=None,
                omit_layer_data=False, audit_out=None, level_id=None, overwrite_audit=False)
    base.update(kw)
    return argparse.Namespace(**base)


def _chk(**kw: Any) -> argparse.Namespace:
    base = dict(mode=None, preset=None, jump_height=None, jump_distance=None, diagonal=False, screen_tiles=None,
                min_per_screen=None, max_per_screen=None, max_empty_screens=None, max_dead_end_ratio=None,
                min_path_tiles=None, no_pacing=False, max_nodes=20000, strict=False, out=None)
    base.update(kw)
    return argparse.Namespace(**base)


def _level_from_ascii(rows: List[str], marks: Dict[str, str]) -> Dict[str, Any]:
    ents = []
    solid = []
    for y, r in enumerate(rows):
        row = ""
        for x, ch in enumerate(r):
            if ch in marks:
                ents.append({"type": marks[ch], "name": "", "role": marks[ch], "x": x, "y": y, "w": 1, "h": 1,
                             "cell": [x, y], "layer": "t", "properties": {}})
                row += "."
            else:
                row += "#" if ch == "#" else "."
        solid.append(row)
    return {"format": FORMAT, "name": "t", "grid": {"width": len(rows[0]), "height": len(rows)},
            "tile_size": [16, 16], "entities": ents,
            "solid": {"source": "test", "rows": solid}}


def selftest() -> int:
    fails: List[str] = []

    def expect(cond: bool, what: str) -> None:
        if not cond:
            fails.append(what)

    rows = [
        "########",
        "#...#..#",
        "#...#..#",
        "#...####",
        "#.....##",
        "########",
    ]
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        files: List[Tuple[str, Path]] = []

        def put(name: str, text: str) -> Path:
            p = tmp / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text, encoding="utf-8")
            files.append((name, p))
            return p

        put("a_csv.tmj", json.dumps(_tmj(rows)))
        put("b_zlib.tmj", json.dumps(_tmj(rows, "base64", "zlib")))
        put("c_gzip.tmj", json.dumps(_tmj(rows, "base64", "gzip")))
        put("d_raw.tmj", json.dumps(_tmj(rows, "base64", "")))
        put("e_csv.tmx", _tmx(rows))
        put("f_zlib.tmx", _tmx(rows, "base64", "zlib"))
        put("g_gzip.tmx", _tmx(rows, "base64", "gzip"))
        put("h.ldtk", json.dumps(_ldtk(rows)))
        put("proj/i.ldtk", json.dumps(_ldtk(rows, external=True)))
        put("proj/Level_0.ldtkl", json.dumps(_ldtk_level(rows)))
        # fixture entities: spawn (1,1) exit (5,2) enemy (2,3) coin (5,4)
        for name, p in files:
            if p.suffix == ".ldtkl":
                continue
            try:
                lv = do_convert(p, _ns())
            except ConvertError as exc:
                fails.append("%s: convert failed: %s" % (name, exc))
                continue
            expect(lv["solid"]["rows"] == rows, "%s: solid rows differ: %r" % (name, lv["solid"]["rows"]))
            roles = sorted((e["role"], tuple(e["cell"])) for e in lv["entities"])
            expect(roles == [("enemy", (2, 3)), ("exit", (5, 2)), ("pickup", (5, 4)), ("spawn", (1, 1))],
                   "%s: entities %r" % (name, roles))
            expect(lv["grid"] == {"width": 8, "height": 6} and lv["tile_size"] == [16, 16], "%s: grid/tile size" % name)
            expect(lv["metadata"]["properties"].get("teach") == "teach", "%s: map property" % name)

        # zstd refused clearly
        z = _tmj(rows, "base64", "zlib")
        z["layers"][0]["compression"] = "zstd"
        zp = put("z.tmj", json.dumps(z))
        try:
            do_convert(zp, _ns())
            fails.append("zstd was not refused")
        except ConvertError as exc:
            expect("zstd" in str(exc), "zstd message unclear")

        # infinite map with chunks and a negative origin
        W, H = 8, 6
        chunks = []
        for cy in (0, 3):
            for cx in (0, 4):
                sub = [rows[cy + j][cx:cx + 4] for j in range(3)]
                chunks.append({"x": cx - 2, "y": cy + 5, "width": 4, "height": 3, "data": _gids(sub)})
        inf = _tmj(rows)
        inf["infinite"] = True
        inf["layers"][0] = {"type": "tilelayer", "name": "Collision", "width": 0, "height": 0, "chunks": chunks}
        for o in inf["layers"][1]["objects"]:
            o["x"] += -2 * 16
            o["y"] += 5 * 16
        lv = do_convert(put("inf.tmj", json.dumps(inf)), _ns())
        expect(lv["origin"] == [-2, 5] and lv["solid"]["rows"] == rows, "infinite map origin/rows: %r %r" % (lv["origin"], lv["solid"]["rows"]))
        expect(sorted(tuple(e["cell"]) for e in lv["entities"]) == [(1, 1), (2, 3), (5, 2), (5, 4)], "infinite entity cells")

        # audit export
        lv = do_convert(tmp / "a_csv.tmj", _ns())
        doc, derived, missing = to_audit(lv, "w1_l001")
        expect(doc["layout"]["rows"][1] == "#P..#..#", "audit rows")
        expect(doc["layout"]["rows"][2][5] == "E" and doc["goals"][0]["type"] == "reach", "audit exit/goals")
        expect(doc["teach"] == "teach" and "teach" in derived and "mechanic_refs" in missing, "audit derived/missing")
        expect(doc["schema_version"] == "1.0" and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]*", doc["level_id"]) is not None, "audit ids")

        # solid from a tile property (tile layer "Tiles", tile 2 has solid=true) and from a collision object layer
        prop = _tmj(rows)
        prop["layers"][0]["name"] = "Tiles"
        prop["layers"][0]["data"] = [2 if v else 0 for v in prop["layers"][0]["data"]]
        prop["tilesets"] = [{"firstgid": 1, "name": "t", "tiles": [{"id": 1, "properties": [
            {"name": "solid", "type": "bool", "value": True}]}]}]
        lv = do_convert(put("prop.tmj", json.dumps(prop)), _ns())
        expect(lv["solid"]["rows"] == rows and "tile property solid" in lv["solid"]["source"], "solid from tile property")
        shapes = _tmj(rows)
        shapes["layers"][0] = {"type": "objectgroup", "name": "Collision", "objects": [
            {"id": 9, "x": 0, "y": 0, "width": 128, "height": 16, "rotation": 0, "type": "", "name": ""},
            {"id": 10, "x": 0, "y": 80, "width": 128, "height": 16, "rotation": 0, "type": "", "name": ""},
            {"id": 11, "x": 0, "y": 16, "width": 16, "height": 64, "rotation": 0, "type": "", "name": ""},
            {"id": 12, "x": 112, "y": 16, "width": 16, "height": 64, "rotation": 0, "type": "", "name": ""}]}
        lv = do_convert(put("shapes.tmj", json.dumps(shapes)), _ns())
        expect(lv["solid"]["rows"][0] == "########" and lv["solid"]["rows"][2] == "#......#", "solid from collision rectangles")
        expect(len(lv["entities"]) == 4, "collision objects are not entities")

        # regenerating a spec keeps solver and notes written by other tools
        ap = tmp / "spec.level.json"
        ap.write_text(json.dumps({"schema_version": "1.0", "level_id": "x", "solver": {"solvable": True, "min_moves": 9},
                                  "notes": "hand written"}), encoding="utf-8")
        d2, _, _ = to_audit(do_convert(tmp / "a_csv.tmj", _ns()), "x")
        kept = merge_existing_spec(d2, ap)
        expect(sorted(kept) == ["notes", "solver"] and d2["solver"]["min_moves"] == 9 and d2["notes"] == "hand written",
               "merge keeps solver and hand-written notes: %r" % kept)

        # --level on a multi-level LDtk project
        multi = _ldtk(rows)
        second = _ldtk_level(rows)
        second["identifier"], second["iid"], second["uid"] = "Level_1", "bbbb", 11
        multi["levels"].append(second)
        mp = put("multi.ldtk", json.dumps(multi))
        try:
            do_convert(mp, _ns())
            fails.append("multi-level LDtk without --level should fail")
        except ConvertError as exc:
            expect("Level_1" in str(exc), "multi-level message lists levels")
        expect(do_convert(mp, _ns(level="Level_1"))["source"]["level"] == "Level_1", "--level selects")

    # ---- check: top-down
    lv = _level_from_ascii(rows, {})
    lv["entities"] = [
        {"type": "PlayerStart", "name": "", "role": "spawn", "x": 1, "y": 1, "w": 0, "h": 0, "cell": [1, 1], "layer": "t", "properties": {}},
        {"type": "exit", "name": "", "role": "exit", "x": 5, "y": 2, "w": 1, "h": 1, "cell": [5, 2], "layer": "t", "properties": {}},
        {"type": "coin", "name": "", "role": "pickup", "x": 5, "y": 4, "w": 0, "h": 0, "cell": [5, 4], "layer": "t", "properties": {}}]
    rep = check_level(lv, _chk())
    expect(rep["exits"][0]["reachable"] is False and rep["verdict"] == "fail" and rep["fail"], "top-down: pocket exit must be unreachable")
    expect(rep["pickups"]["unreachable"] == [] , "top-down: coin reachable")
    opened = json.loads(json.dumps(lv))
    opened["solid"]["rows"][2] = "#......#"[:4] + "." + "..#"
    rep = check_level(opened, _chk())
    expect(rep["exits"][0]["reachable"] and not rep["fail"] and rep["path"]["nearest_exit_tiles"] == 5.0,
           "top-down: opened wall should be reachable at 5 tiles, got %r" % rep.get("path"))
    # no spawn
    nosp = json.loads(json.dumps(lv))
    nosp["entities"] = nosp["entities"][1:]
    expect(check_level(nosp, _chk())["verdict"] == "fail", "no spawn fails")

    # ---- check: platformer
    gap = [
        "..........",
        "..........",
        "..........",
        ".P......E.",
        "###....###",
    ]
    marks = {"P": "spawn", "E": "exit"}
    lvp = _level_from_ascii(gap, marks)
    near = check_level(lvp, _chk(mode="platformer", jump_height=3, jump_distance=6))
    expect(near["exits"][0]["reachable"], "platformer: 4-wide gap with distance 6 should be crossable")
    far = check_level(lvp, _chk(mode="platformer", jump_height=3, jump_distance=2))
    expect(not far["exits"][0]["reachable"] and far["fail"], "platformer: 4-wide gap with distance 2 must fail")
    # ledge too high
    ledge = [
        "..........",
        "..........",
        ".....#####",
        ".....#####",
        ".....#####",
        ".....#####",
        "##########",
    ]
    ledge_l = _level_from_ascii(ledge, {})
    ledge_l["entities"] = [
        {"type": "s", "name": "", "role": "spawn", "x": 1, "y": 5, "w": 0, "h": 0, "cell": [1, 5], "layer": "t", "properties": {}},
        {"type": "e", "name": "", "role": "exit", "x": 8, "y": 1, "w": 1, "h": 1, "cell": [8, 1], "layer": "t", "properties": {}}]
    low = check_level(ledge_l, _chk(mode="platformer", jump_height=3, jump_distance=6))
    expect(not low["exits"][0]["reachable"], "platformer: 4-tile ledge needs more than height 3")
    high = check_level(ledge_l, _chk(mode="platformer", jump_height=4.6, jump_distance=6))
    expect(high["exits"][0]["reachable"], "platformer: 4-tile ledge with height 4.6 should be reachable")
    # pit that cannot be climbed out of: reachable by falling, flagged as a trap
    pit_rows = [".........."] * 4 + [".P.......E"] + ["###..#####"] * 6 + ["##########"]
    pit_l = _level_from_ascii(pit_rows, {"P": "spawn", "E": "exit"})
    pr = check_level(pit_l, _chk(mode="platformer", jump_height=3, jump_distance=6))
    expect(pr["exits"][0]["reachable"], "platformer: 2-wide pit is crossable")
    expect(pr.get("traps", {}).get("count", 0) > 0 and pr["verdict"] == "warn", "platformer: pit floor is a trap, got %r" % pr.get("traps"))

    if fails:
        for f in fails:
            print("FAIL: %s" % f, file=sys.stderr)
        return 1
    print("selftest ok")
    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return 0 if exc.code == 0 else 2
    if args.selftest:
        return selftest()
    if args.cmd == "convert":
        return cmd_convert(args)
    if args.cmd == "check":
        return cmd_check(args)
    parser.print_help()
    return 2


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows pipes default to the ANSI code page; Claude Code reads UTF-8
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
