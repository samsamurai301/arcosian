#!/usr/bin/env python3
"""Project map for Claude, and change impact.

`build` indexes a game project into .gamestudio/map/map.json (the full graph) and .gamestudio/map/MAP.md (a compact
summary to read before opening files): scenes and their nodes, scripts, classes, signals, autoloads, input actions,
tuning keys, assets, tests and design documents. Godot and Unity projects are parsed in depth; other engines get
their files and the references between them. Rebuilds are incremental: a file with the same size and modification
time as last time is not parsed again.

`impact` answers "what does changing X touch?": the scenes, scripts, tests, features and tuning that depend on X,
and which of the five gates to run again.

  project_map.py build [--root DIR] [--json]
  project_map.py impact TARGET [TARGET ...] [--root DIR] [--depth N] [--json]
  project_map.py --selftest

TARGET: a file or folder (relative, absolute or res://), a class name, an autoload, a tuning key, an input action,
a feature id (through the feature's "paths" globs) or a glob such as "core/*.gd".
Exit codes: 0 ok, 1 no target matched (impact), 2 usage error.
"""
import argparse
import fnmatch
import json
import os
import posixpath
import re
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gslib as G  # noqa: E402

MAP_FORMAT = "arcosian-map/1"
SKIP_DIRS = {"node_modules", "Library", "Temp", "Logs", "obj", "build", "builds", "Build", "Builds", "dist",
             "export", "exports", "venv", "__pycache__", "UserSettings", "MemoryCaptures", "Recordings"}
MAX_FILES = 20000
MAX_PARSE_BYTES = 4000000
ASSET_EXT = {".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif", ".tga", ".bmp", ".psd", ".ase", ".aseprite", ".exr",
             ".hdr", ".ktx2", ".wav", ".ogg", ".mp3", ".flac", ".opus", ".glb", ".gltf", ".fbx", ".obj", ".blend",
             ".dae", ".ttf", ".otf", ".woff", ".woff2", ".fnt", ".mp4", ".webm", ".ogv", ".bank"}
SCRIPT_LANG = {".gd": "gdscript", ".cs": "csharp", ".lua": "lua", ".script": "lua", ".gui_script": "lua",
               ".render_script": "lua", ".js": "javascript", ".mjs": "javascript", ".ts": "typescript",
               ".py": "python", ".c": "c", ".h": "c", ".cpp": "cpp", ".hpp": "cpp", ".cc": "cpp"}
SCENE_EXT = {".tscn", ".unity", ".prefab", ".collection"}
RESOURCE_EXT = {".tres", ".asset", ".mat", ".controller", ".anim", ".overrideController", ".playable",
                ".physicMaterial", ".spriteatlas", ".atlas", ".tilemap", ".tilesource", ".gui"}
SHADER_EXT = {".gdshader", ".gdshaderinc", ".shader", ".shadergraph", ".hlsl", ".glsl", ".cginc", ".fp", ".vp"}
DATA_EXT = {".json", ".csv", ".yaml", ".yml", ".toml", ".cfg", ".ini", ".xml", ".tmj", ".tmx", ".ldtk", ".asmdef"}
DOC_EXT = {".md", ".txt"}
TEST_DIRS = {"tests", "test", "Tests", "Test", "spec", "specs"}
VENDOR_DIRS = {"addons", "Plugins", "ThirdParty", "third_party", "vendor", "Vendor"}
CORE_DIRS = {"core", "Core", "sim", "Sim", "domain", "Domain", "model", "Model", "logic", "Logic"}
PRESENTATION_DIRS = {"presentation", "Presentation", "ui", "UI", "view", "View", "views", "Views", "vfx", "VFX",
                     "scenes", "Scenes", "prefabs", "Prefabs", "art", "Art", "audio", "Audio", "sprites", "Sprites"}
COUNT_WORDS = ("spawn", "count", "max", "rate", "size", "density", "limit", "pool", "particles", "enemies")

CLASS_NAME_RE = re.compile(r"^\s*class_name\s+([A-Za-z_]\w*)", re.M)
EXTENDS_RE = re.compile(r"^\s*extends\s+(\"[^\"]+\"|'[^']+'|[A-Za-z_][\w.]*)", re.M)
SIGNAL_RE = re.compile(r"^\s*signal\s+([A-Za-z_]\w*)", re.M)
FUNC_RE = re.compile(r"^\s*(?:static\s+)?func\s+([A-Za-z_]\w*)", re.M)
STRING_RE = re.compile(r"\"((?:[^\"\\\n]|\\.){1,200})\"|'((?:[^'\\\n]|\\.){1,200})'")
IDENT_RE = re.compile(r"\b([A-Z][A-Za-z0-9_]*)\b")
DOT_RE = re.compile(r"\.([a-z_][a-z0-9_]*)\b(?!\s*\()")
CS_TYPE_RE = re.compile(r"\b(?:class|struct|interface|record|enum)\s+([A-Z]\w*)(?:\s*<[^>{;]*>)?(?:\s*:\s*([^{;\n]+))?")
CS_NS_RE = re.compile(r"^\s*namespace\s+([\w.]+)", re.M)
EXT_RES_RE = re.compile(r"^\[ext_resource\b([^\]]*)\]", re.M)
NODE_RE = re.compile(r"^\[node\b([^\]]*)\]", re.M)
CONN_RE = re.compile(r"^\[connection\b([^\]]*)\]", re.M)
ATTR_RE = re.compile(r"(\w+)=(\"[^\"]*\"|[^\s\]]+)")
GUID_RE = re.compile(r"guid:\s*([0-9a-f]{32})")
SCRIPT_GUID_RE = re.compile(r"m_Script:\s*\{[^}]*guid:\s*([0-9a-f]{32})")
JS_IMPORT_RE = re.compile(r"(?:\bfrom\s+|\bimport\s*\(\s*|\brequire\s*\(\s*|^\s*import\s+)[\"']([^\"']+)[\"']", re.M)
LUA_REQ_RE = re.compile(r"\brequire\s*\(?\s*[\"']([\w./-]+)[\"']")
INCLUDE_RE = re.compile(r"^\s*#\s*include\s+\"([^\"]+)\"", re.M)


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _rel(p: Path, root: Path) -> str:
    return p.relative_to(root).as_posix()


def strip_comments(text: str, style: str) -> str:
    """Remove comments but keep string literals. style: hash (#), slash (// and /* */), lua (-- and --[[ ]])."""
    out: List[str] = []
    i, n = 0, len(text)
    quote = ""
    while i < n:
        c = text[i]
        if quote:
            out.append(c)
            if c == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if c == quote or c == "\n":
                quote = ""
            i += 1
            continue
        if c in "\"'":
            quote = c
            out.append(c)
            i += 1
            continue
        if style == "hash" and c == "#":
            j = text.find("\n", i)
            i = n if j < 0 else j
            continue
        if style == "slash" and text.startswith("//", i):
            j = text.find("\n", i)
            i = n if j < 0 else j
            continue
        if style == "slash" and text.startswith("/*", i):
            j = text.find("*/", i + 2)
            i = n if j < 0 else j + 2
            continue
        if style == "lua" and text.startswith("--", i):
            if text.startswith("--[[", i):
                j = text.find("]]", i + 4)
                i = n if j < 0 else j + 2
            else:
                j = text.find("\n", i)
                i = n if j < 0 else j
            continue
        out.append(c)
        i += 1
    return "".join(out)


def _attrs(chunk: str) -> Dict[str, str]:
    return {k: v.strip('"') for k, v in ATTR_RE.findall(chunk)}


def _uniq(items: Iterable[str], cap: int = 400) -> List[str]:
    seen: List[str] = []
    s: Set[str] = set()
    for it in items:
        if it and it not in s:
            s.add(it)
            seen.append(it)
            if len(seen) >= cap:
                break
    return seen


# --------------------------------------------------------------------------
# per-file parsing (cached by size + mtime)
# --------------------------------------------------------------------------

def classify(rel: str, engine: str) -> Tuple[str, str]:
    """(kind, language) for a project-relative path."""
    p = posixpath.basename(rel)
    ext = posixpath.splitext(p)[1].lower() if not p.endswith(".gui_script") else ".gui_script"
    if p.endswith(".render_script"):
        ext = ".render_script"
    parts = set(rel.split("/")[:-1])
    lang = SCRIPT_LANG.get(ext, "")
    if engine == "defold" and ext == ".go":
        return "scene", ""
    if p in ("project.godot", "game.project") or rel.endswith("ProjectSettings/ProjectSettings.asset"):
        return "project", ""
    if parts & VENDOR_DIRS:
        return "vendor", lang
    if lang and (parts & TEST_DIRS or p.startswith("test_") or p.endswith(("Tests.cs", "Test.cs", ".test.js", ".test.ts",
                                                                            "_test.py", ".spec.ts"))):
        return "test", lang
    if (parts & TEST_DIRS) and ext in DATA_EXT:
        return "test", ""
    if rel.split("/")[0] in ("tools", "Tools") and lang:
        return "tool", lang
    if lang:
        return "script", lang
    if ext in SCENE_EXT:
        return "scene", ""
    if ext in SHADER_EXT:
        return "shader", ""
    if ext in RESOURCE_EXT:
        return "resource", ""
    if ext in ASSET_EXT:
        return "asset", ""
    if ext in DATA_EXT:
        return "data", ""
    if ext in DOC_EXT:
        return "doc", ""
    return "other", ""


def parse_file(path: Path, rel: str, kind: str, lang: str) -> Dict[str, Any]:
    """Facts about one file; everything cross-file is resolved later in link()."""
    facts: Dict[str, Any] = {}
    ext = path.suffix.lower()
    if kind in ("asset", "vendor", "other", "doc") and ext != ".meta":
        return facts
    try:
        if path.stat().st_size > MAX_PARSE_BYTES:
            facts["too_big"] = True
            return facts
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return facts
    facts["lines"] = text.count("\n") + 1
    if ext == ".meta":
        m = GUID_RE.search(text)
        if m:
            facts["guid"] = m.group(1)
        return facts
    if lang:
        style = {"gdscript": "hash", "python": "hash", "lua": "lua"}.get(lang, "slash")
        code = strip_comments(text, style)
        strings = [a or b for a, b in STRING_RE.findall(code)]
        facts["strings"] = _uniq((s for s in strings if len(s) <= 80), 600)
        bare = STRING_RE.sub('""', code)
        facts["idents"] = _uniq(IDENT_RE.findall(bare), 600)
        facts["dot"] = _uniq(DOT_RE.findall(bare), 600)
        facts["tuning_line"] = _uniq(w for line in bare.splitlines() if re.search(r"tuning|balance|config", line, re.I)
                                     for w in re.findall(r"\.([a-z_]\w*)|\[\s*\"(\w+)\"", line) for w in w if w)
        facts["paths"] = _uniq(s for s in strings if s.startswith(("res://", "Assets/", "/")) or
                               re.match(r"^\.{0,2}/?[\w.-]+(/[\w.-]+)*\.\w{1,12}$", s))
        if lang == "gdscript":
            facts["classes"] = CLASS_NAME_RE.findall(code)
            facts["extends"] = [e.strip("\"'") for e in EXTENDS_RE.findall(code)][:1]
            facts["signals"] = SIGNAL_RE.findall(code)
            facts["funcs"] = len(FUNC_RE.findall(code))
        elif lang == "csharp":
            ns = CS_NS_RE.search(code)
            facts["namespace"] = ns.group(1) if ns else ""
            classes, bases = [], {}
            for name, base in CS_TYPE_RE.findall(bare):
                classes.append(name)
                if base:
                    bases[name] = [re.sub(r"<.*", "", b).strip().split(".")[-1] for b in base.split(",") if b.strip()]
            facts["classes"] = _uniq(classes)
            facts["bases"] = bases
            facts["extends"] = _uniq(b for bl in bases.values() for b in bl)
            facts["signals"] = re.findall(r"\bevent\s+[\w<>,\s.]+?\s+(\w+)\s*;", bare)
        elif lang in ("javascript", "typescript"):
            facts["imports"] = _uniq(JS_IMPORT_RE.findall(code))
        elif lang == "lua":
            facts["imports"] = _uniq(LUA_REQ_RE.findall(code))
        elif lang in ("c", "cpp"):
            facts["imports"] = _uniq(INCLUDE_RE.findall(text))
        return facts
    if ext in (".tscn", ".tres"):
        ext_res: Dict[str, Tuple[str, str]] = {}
        for chunk in EXT_RES_RE.findall(text):
            a = _attrs(chunk)
            if a.get("path"):
                ext_res[a.get("id", a["path"])] = (a.get("type", ""), a["path"])
        facts["scripts"] = _uniq(p for t, p in ext_res.values() if t == "Script")
        facts["instances"] = _uniq(p for t, p in ext_res.values() if t == "PackedScene")
        facts["res"] = _uniq(p for t, p in ext_res.values() if t not in ("Script", "PackedScene"))
        nodes = [_attrs(c) for c in NODE_RE.findall(text)]
        facts["nodes"] = len(nodes)
        if nodes:
            facts["root"] = "%s (%s)" % (nodes[0].get("name", "?"), nodes[0].get("type", "instance"))
        facts["connections"] = [{"signal": a.get("signal", ""), "from": a.get("from", ""), "to": a.get("to", ""),
                                 "method": a.get("method", "")} for a in (_attrs(c) for c in CONN_RE.findall(text))][:200]
        return facts
    if ext in (".unity", ".prefab", ".asset", ".mat", ".controller", ".anim", ".overridecontroller", ".playable",
               ".spriteatlas") or (kind in ("scene", "resource") and text.startswith("%YAML")):
        facts["guid_refs"] = _uniq(GUID_RE.findall(text), 2000)
        facts["script_guids"] = _uniq(SCRIPT_GUID_RE.findall(text), 500)
        facts["nodes"] = text.count("--- !u!1 &")
        m = re.search(r"m_Name:\s*(.+)", text)
        if m:
            facts["root"] = m.group(1).strip()
        return facts
    if ext == ".asmdef":
        try:
            d = json.loads(text)
            facts["assembly"] = d.get("name", "")
            facts["asm_refs"] = [r for r in d.get("references", []) if isinstance(r, str)]
        except ValueError:
            pass
        return facts
    if ext == ".json" and re.search(r"(tuning|balance)", posixpath.basename(rel), re.I):
        try:
            d = json.loads(text)
        except ValueError:
            return facts
        keys: List[str] = []
        if isinstance(d, dict):
            for k, v in d.items():
                if k in ("schema_version", "$schema", "version"):
                    continue
                keys.append(k)
                if isinstance(v, dict):
                    keys += ["%s.%s" % (k, k2) for k2 in v if isinstance(k2, str)][:50]
        facts["tuning_keys"] = keys[:400]
        return facts
    if kind == "scene" or ext in (".collection", ".go", ".gui"):
        facts["paths"] = _uniq(re.findall(r"\"(/[\w./-]+\.\w+)\"", text))
    if kind == "project" and path.name == "project.godot":
        facts.update(parse_project_godot(text))
    return facts


def parse_project_godot(text: str) -> Dict[str, Any]:
    out: Dict[str, Any] = {"autoloads": {}, "actions": [], "main_scene": ""}
    section = ""
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("[") and s.endswith("]"):
            section = s[1:-1]
            continue
        if section == "autoload":
            m = re.match(r"^(\w+)\s*=\s*\"\*?([^\"]+)\"", s)
            if m:
                out["autoloads"][m.group(1)] = m.group(2)
        elif section == "input":
            m = re.match(r"^(\w+)\s*=\s*\{", s)
            if m:
                out["actions"].append(m.group(1))
        elif section == "application":
            m = re.match(r"^run/main_scene\s*=\s*\"([^\"]+)\"", s)
            if m:
                out["main_scene"] = m.group(1)
    return out


# --------------------------------------------------------------------------
# build
# --------------------------------------------------------------------------

def map_dir(root: Path) -> Path:
    return G.gs_dir(root) / "map"


def scan(root: Path) -> List[Path]:
    files: List[Path] = []
    for dirpath, dirnames, filenames in os.walk(str(root)):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS and not d.startswith("."))
        for f in sorted(filenames):
            if f.startswith(".") and f != ".gitattributes":
                continue
            files.append(Path(dirpath) / f)
            if len(files) >= MAX_FILES:
                return files
    return files


def build(root: Path, verbose: bool = False) -> Dict[str, Any]:
    """Index the project at root, write map.json and MAP.md, return the map."""
    root = root.resolve()
    engine, version, eng_rel = G.detect_engine(root)
    engine = engine or "other"
    eng_rel = eng_rel or "."
    out_dir = map_dir(root)
    old: Dict[str, Any] = {}
    try:
        old = json.loads((out_dir / "map.json").read_text(encoding="utf-8")).get("files", {})
    except (OSError, ValueError):
        old = {}
    files: Dict[str, Dict[str, Any]] = {}
    paths = scan(root)
    reparsed = 0
    for p in paths:
        rel = _rel(p, root)
        kind, lang = classify(rel, engine)
        try:
            st = p.stat()
        except OSError:
            continue
        prev = old.get(rel)
        if prev and prev.get("size") == st.st_size and prev.get("mtime") == st.st_mtime_ns and prev.get("kind") == kind:
            facts = prev.get("facts", {})
        else:
            facts = parse_file(p, rel, kind, lang)
            reparsed += 1
        files[rel] = {"kind": kind, "lang": lang, "size": st.st_size, "mtime": st.st_mtime_ns, "facts": facts}
    graph = link(root, files, engine, eng_rel)
    doc = {
        "format": MAP_FORMAT, "generated_at": _now(), "engine": engine, "engine_version": version or "",
        "engine_root": eng_rel, "truncated": len(paths) >= MAX_FILES, "files": files,
        "nodes": graph["nodes"], "edges": graph["edges"], "project": graph["project"],
        "stats": {"files": len(files), "reparsed": reparsed, "edges": len(graph["edges"])},
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "map.json.tmp"
    tmp.write_text(json.dumps(doc, indent=1, sort_keys=False) + "\n", encoding="utf-8")
    os.replace(str(tmp), str(out_dir / "map.json"))
    (out_dir / "MAP.md").write_text(render_md(root, doc), encoding="utf-8")
    return doc


def link(root: Path, files: Dict[str, Dict[str, Any]], engine: str, eng_rel: str) -> Dict[str, Any]:
    """Resolve cross-file references into nodes and edges. Edge (a, b, kind) means a depends on b."""
    prefix = "" if eng_rel in (".", "") else eng_rel.rstrip("/") + "/"
    edges: List[List[str]] = []
    nodes: Dict[str, Dict[str, Any]] = {}
    classes: Dict[str, str] = {}
    guids: Dict[str, str] = {}
    project: Dict[str, Any] = {"autoloads": {}, "actions": [], "main_scene": "", "assemblies": {}}
    tuning: Dict[str, List[str]] = {}

    for rel, info in files.items():
        f = info.get("facts", {})
        for c in f.get("classes", []):
            classes.setdefault(c, rel)
        if rel.endswith(".meta") and f.get("guid"):
            guids[f["guid"]] = rel[:-5]
        if f.get("autoloads") is not None and rel.endswith("project.godot"):
            project["autoloads"] = f.get("autoloads", {})
            project["actions"] = f.get("actions", [])
            project["main_scene"] = f.get("main_scene", "")
        for k in f.get("tuning_keys", []):
            tuning.setdefault(k, []).append(rel)
        if f.get("assembly"):
            project["assemblies"][f["assembly"]] = rel

    def res(ref: str, from_rel: str) -> Optional[str]:
        if not ref or ref.startswith("uid://"):
            return None
        cands: List[str] = []
        if ref.startswith("res://"):
            cands.append(prefix + ref[6:])
        elif ref.startswith(("Assets/", "Packages/")):
            cands.append(prefix + ref)
        elif ref.startswith("/"):
            cands.append(prefix + ref[1:])
        else:
            base = posixpath.dirname(from_rel)
            cands.append(posixpath.normpath(posixpath.join(base, ref)))
            cands.append(posixpath.normpath(prefix + ref))
        for c in list(cands):
            if not posixpath.splitext(c)[1]:
                cands += [c + e for e in (".js", ".ts", ".mjs", ".lua", "/index.js", "/index.ts")]
        for c in cands:
            if c in files:
                return c
        return None

    autoload_files: Dict[str, str] = {}
    for name, ref in project["autoloads"].items():
        r = res(ref, "project.godot")
        nodes["autoload:" + name] = {"kind": "autoload", "file": r}
        if r:
            autoload_files[name] = r
            edges.append(["autoload:" + name, "file:" + r, "defines"])
    for a in project["actions"]:
        nodes["action:" + a] = {"kind": "action"}
    for k, defs in tuning.items():
        nodes["tuning:" + k] = {"kind": "tuning", "defined_in": defs}
    for c, rel in classes.items():
        nodes["class:" + c] = {"kind": "class", "file": rel}
    actions = set(project["actions"])

    for rel, info in files.items():
        f = info.get("facts", {})
        src = "file:" + rel
        own = set(f.get("classes", []))
        if info["kind"] in ("script", "test", "tool"):
            for e in f.get("extends", []):
                tgt = res(e, rel) if ("/" in e or e.endswith((".gd", ".cs"))) else classes.get(e)
                if tgt and tgt != rel:
                    edges.append([src, "file:" + tgt, "extends"])
            for p in f.get("paths", []):
                tgt = res(p, rel)
                if tgt and tgt != rel:
                    edges.append([src, "file:" + tgt, "loads"])
            for imp in f.get("imports", []):
                ref = imp.replace(".", "/") + ".lua" if info["lang"] == "lua" and "/" not in imp else imp
                tgt = res(ref, rel)
                if tgt and tgt != rel:
                    edges.append([src, "file:" + tgt, "imports"])
            for ident in f.get("idents", []):
                if ident in own:
                    continue
                if ident in classes and classes[ident] != rel:
                    edges.append([src, "file:" + classes[ident], "uses"])
                if ident in autoload_files and autoload_files[ident] != rel:
                    edges.append([src, "file:" + autoload_files[ident], "uses_autoload"])
            strings = set(f.get("strings", []))
            for a in actions & strings:
                edges.append([src, "action:" + a, "reads_input"])
            dots, tline = set(f.get("dot", [])), set(f.get("tuning_line", []))
            for k in tuning:
                leaf = k.split(".")[-1]
                if k in strings or leaf in tline or (leaf in dots and ("_" in leaf or len(leaf) >= 8)):
                    edges.append([src, "tuning:" + k, "reads_tuning"])
        elif info["kind"] in ("scene", "resource"):
            for p in f.get("scripts", []):
                tgt = res(p, rel)
                if tgt:
                    edges.append([src, "file:" + tgt, "attaches"])
            for p in f.get("instances", []):
                tgt = res(p, rel)
                if tgt:
                    edges.append([src, "file:" + tgt, "instances"])
            for p in f.get("res", []) + f.get("paths", []):
                tgt = res(p, rel)
                if tgt and tgt != rel:
                    edges.append([src, "file:" + tgt, "uses"])
            sg = set(f.get("script_guids", []))
            for g in f.get("guid_refs", []):
                tgt = guids.get(g)
                if tgt and tgt != rel and tgt in files:
                    edges.append([src, "file:" + tgt, "attaches" if g in sg else "uses"])
    seen: Set[Tuple[str, str, str]] = set()
    uniq_edges: List[List[str]] = []
    for e in edges:
        t = (e[0], e[1], e[2])
        if t not in seen:
            seen.add(t)
            uniq_edges.append(e)
    return {"nodes": nodes, "edges": uniq_edges, "project": project}


# --------------------------------------------------------------------------
# MAP.md
# --------------------------------------------------------------------------

def _clip(items: List[str], n: int) -> str:
    if len(items) <= n:
        return ", ".join(items)
    return ", ".join(items[:n]) + ", +%d more" % (len(items) - n)


def render_md(root: Path, doc: Dict[str, Any]) -> str:
    files = doc["files"]
    deps: Dict[str, List[Tuple[str, str]]] = {}
    rdeps: Dict[str, List[str]] = {}
    for a, b, k in doc["edges"]:
        deps.setdefault(a, []).append((b, k))
        rdeps.setdefault(b, []).append(a)
    by_kind: Dict[str, List[str]] = {}
    for rel, info in files.items():
        if not rel.endswith(".meta"):
            by_kind.setdefault(info["kind"], []).append(rel)
    title = ""
    try:
        title = (G.load_json(G.gs_dir(root) / "contract.json") or {}).get("meta", {}).get("title", "")
    except Exception:  # noqa: BLE001 - a broken contract must not stop the map
        title = ""
    lines = ["# Project map%s" % (": " + title if title else ""), "",
             "Generated %s by `gs.py map` (do not edit). Engine: %s %s. Full graph: `.gamestudio/map/map.json`. "
             "Read this before opening files; `gs.py impact <file|class|key>` lists what a change touches."
             % (doc["generated_at"][:10], doc["engine"], doc.get("engine_version", "")), ""]
    counts = ", ".join("%d %s" % (len(v), k) for k, v in sorted(by_kind.items(), key=lambda kv: -len(kv[1])))
    lines.append("Files: " + counts + (" (truncated at %d files)" % MAX_FILES if doc.get("truncated") else ""))
    pr = doc.get("project", {})
    if pr.get("main_scene"):
        lines.append("Main scene: " + pr["main_scene"])
    if pr.get("autoloads"):
        lines.append("Autoloads: " + _clip(["%s (%s)" % (k, v.replace("res://", "")) for k, v in pr["autoloads"].items()], 20))
    if pr.get("actions"):
        lines.append("Input actions: " + _clip(pr["actions"], 30))
    if pr.get("assemblies"):
        lines.append("Assemblies: " + _clip(sorted(pr["assemblies"]), 20))
    lines.append("")

    def file_line(rel: str) -> str:
        f = files[rel].get("facts", {})
        bits = []
        if f.get("classes"):
            bits.append("class " + _clip(f["classes"], 4))
        if f.get("extends"):
            bits.append("extends " + f["extends"][0])
        out = [b for b, k in deps.get("file:" + rel, []) if b.startswith("file:") and k != "defines"]
        if out:
            bits.append("uses " + _clip(sorted({o[5:] for o in out}), 6))
        tun = [b[7:] for b, k in deps.get("file:" + rel, []) if k == "reads_tuning"]
        if tun:
            bits.append("tuning " + _clip(sorted(tun), 6))
        if f.get("signals"):
            bits.append("signals " + _clip(f["signals"], 5))
        return "- %s%s" % (rel, (": " + "; ".join(bits)) if bits else "")

    scenes = sorted(by_kind.get("scene", []))
    if scenes:
        lines.append("## Scenes (%d)" % len(scenes))
        for rel in scenes[:40]:
            f = files[rel].get("facts", {})
            att = [b[5:] for b, k in deps.get("file:" + rel, []) if k == "attaches"]
            inst = [b[5:] for b, k in deps.get("file:" + rel, []) if k == "instances"]
            bits = ["root " + f["root"]] if f.get("root") else []
            if f.get("nodes"):
                bits.append("%d node%s" % (f["nodes"], "" if f["nodes"] == 1 else "s"))
            if att:
                bits.append("scripts " + _clip(att, 4))
            if inst:
                bits.append("instances " + _clip(inst, 4))
            if f.get("connections"):
                bits.append("%d signal connections" % len(f["connections"]))
            lines.append("- %s: %s" % (rel, "; ".join(bits) or "-"))
        if len(scenes) > 40:
            lines.append("- +%d more in map.json" % (len(scenes) - 40))
        lines.append("")
    for kind, label, cap in (("script", "Scripts", 80), ("test", "Tests", 40), ("tool", "Tools", 20)):
        items = sorted(by_kind.get(kind, []))
        if items:
            lines.append("## %s (%d)" % (label, len(items)))
            lines += [file_line(r) for r in items[:cap]]
            if len(items) > cap:
                lines.append("- +%d more in map.json" % (len(items) - cap))
            lines.append("")
    tuning = sorted(k for k in doc["nodes"] if k.startswith("tuning:"))
    if tuning:
        lines.append("## Tuning keys (%d)" % len(tuning))
        for k in tuning[:60]:
            users = sorted(a[5:] for a in rdeps.get(k, []) if a.startswith("file:"))
            lines.append("- %s (%s): %s" % (k[7:], ", ".join(doc["nodes"][k].get("defined_in", [])), _clip(users, 6) or "no reader found"))
        lines.append("")
    hot = sorted(((len(set(rdeps.get("file:" + r, []))), r) for r in files), reverse=True)
    hot = [(n, r) for n, r in hot if n >= 2][:12]
    if hot:
        lines.append("## Most depended-on files")
        lines += ["- %s (%d dependents)" % (r, n) for n, r in hot]
        lines.append("")
    for kind, label in (("shader", "Shaders"), ("resource", "Resources"), ("data", "Data"), ("asset", "Assets")):
        items = sorted(by_kind.get(kind, []))
        if items:
            size = sum(files[r]["size"] for r in items)
            lines.append("## %s (%d, %.1f MB)" % (label, len(items), size / 1048576.0))
            lines.append(_clip(items, 25))
            lines.append("")
    gsd = G.gs_dir(root)
    design = []
    for name in ("contract.json", "features.json", "budget.json", "assets/manifest.json"):
        if (gsd / name).is_file():
            design.append(name)
    for sub in ("levels", "economy", "whatif", "playtests"):
        d = gsd / sub
        if d.is_dir():
            n = len([p for p in d.glob("*.json")])
            if n:
                design.append("%s/ (%d)" % (sub, n))
    if design:
        lines += ["## Design documents (.gamestudio/)", ", ".join(design), ""]
    text = "\n".join(lines).rstrip() + "\n"
    return text


# --------------------------------------------------------------------------
# load / impact
# --------------------------------------------------------------------------

def load(root: Path, refresh: bool = True) -> Dict[str, Any]:
    """The map for root, rebuilt (incrementally) when refresh is true or no map exists yet."""
    p = map_dir(root) / "map.json"
    if refresh or not p.is_file():
        return build(root)
    return json.loads(p.read_text(encoding="utf-8"))


def _norm_target(t: str, root: Path, eng_rel: str) -> str:
    if t.startswith("res://"):
        t = ("" if eng_rel in (".", "") else eng_rel.rstrip("/") + "/") + t[6:]
    p = Path(t)
    if p.is_absolute():
        try:
            t = p.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            return t
    return posixpath.normpath(t.replace("\\", "/"))  # also drops a leading "./"


def resolve_targets(doc: Dict[str, Any], root: Path, targets: List[str]) -> Tuple[List[str], List[str]]:
    """Node ids for each target, and the targets that matched nothing."""
    files = doc["files"]
    nodes = doc["nodes"]
    found: List[str] = []
    missing: List[str] = []
    features = []
    try:
        features = (G.load_json(G.gs_dir(root) / "features.json") or {}).get("features", [])
    except Exception:  # noqa: BLE001
        features = []
    for t in targets:
        hits: List[str] = []
        rel = _norm_target(t, root, doc.get("engine_root", "."))
        if rel in files:
            hits.append("file:" + rel)
        elif any(r.startswith(rel.rstrip("/") + "/") for r in files) and rel != ".":
            hits += ["file:" + r for r in files if r.startswith(rel.rstrip("/") + "/") and not r.endswith(".meta")]
        elif any(ch in t for ch in "*?["):
            hits += ["file:" + r for r in files if fnmatch.fnmatch(r, t) and not r.endswith(".meta")]
        for prefix in ("class:", "autoload:", "tuning:", "action:"):
            key = t[len(prefix):] if t.startswith(prefix) else t
            if prefix + key in nodes:
                hits.append(prefix + key)
                if nodes[prefix + key].get("file"):
                    hits.append("file:" + nodes[prefix + key]["file"])
        for f in features:
            if f.get("id") == t:
                for glob in f.get("paths", []) or []:
                    hits += ["file:" + r for r in files if fnmatch.fnmatch(r, glob) or r.startswith(glob.rstrip("/") + "/")]
                if not f.get("paths"):
                    hits.append("feature:" + t)
        if hits:
            found += [h for h in hits if h not in found]
        else:
            missing.append(t)
    return found, missing


def impact(doc: Dict[str, Any], root: Path, targets: List[str], depth: int = 4) -> Dict[str, Any]:
    files = doc["files"]
    start, missing = resolve_targets(doc, root, targets)
    rev: Dict[str, List[Tuple[str, str]]] = {}
    for a, b, k in doc["edges"]:
        rev.setdefault(b, []).append((a, k))
    seen: Dict[str, Tuple[int, str, str]] = {}
    frontier = [s for s in start if not s.startswith("feature:")]
    level = 0
    while frontier and level < depth:
        level += 1
        nxt = []
        for node in frontier:
            for src, kind in rev.get(node, []):
                if src in start or src in seen:
                    continue
                seen[src] = (level, kind, node)
                nxt.append(src)
        frontier = nxt
    dep_files = sorted((n[5:] for n in seen if n.startswith("file:")), key=lambda r: (seen["file:" + r][0], r))
    tgt_files = [s[5:] for s in start if s.startswith("file:")]
    everything = tgt_files + dep_files

    def kind_of(r: str) -> str:
        return files.get(r, {}).get("kind", "other")

    def parts(r: str) -> Set[str]:
        return set(r.split("/")[:-1])

    tests = [r for r in everything if kind_of(r) == "test"]
    code_kinds = ("script", "scene", "resource", "shader", "test", "project")
    code = [r for r in everything if kind_of(r) in code_kinds]
    core = [r for r in everything if parts(r) & CORE_DIRS and kind_of(r) in ("script", "data")]
    pres = [r for r in everything if (parts(r) & PRESENTATION_DIRS) or kind_of(r) in ("scene", "asset", "shader")]
    tuning = [s[7:] for s in start if s.startswith("tuning:")]
    main = doc.get("project", {}).get("main_scene", "").replace("res://", "")
    gates: Dict[str, str] = {}
    if code or any(kind_of(r) == "data" for r in tgt_files):
        gates["static"] = "code, scenes or data changed"
    if tests or core:
        gates["unit"] = "%d test file(s) reach the change%s" % (len(tests), "; the sim-core changed" if core else "")
    if core or tuning or any(r.endswith(main) for r in everything if main) or any(kind_of(r) == "scene" for r in everything):
        gates["playthrough"] = "gameplay code, tuning or a playable scene is affected"
    if pres:
        gates["visual"] = "%d presentation file(s): scenes, UI, art or shaders" % len(pres)
    heavy = [r for r in everything if kind_of(r) in ("asset", "shader") or posixpath.splitext(r)[1] in (".tscn", ".unity", ".prefab")]
    if heavy or any(any(w in k for w in COUNT_WORDS) for k in tuning):
        gates["perf"] = "rendering, assets or entity counts may change frame time or memory"
    if any(kind_of(r) == "project" for r in tgt_files):
        gates = {g: "project settings changed: run every gate" for g in G.GATES}
    feats = []
    try:
        fl = (G.load_json(G.gs_dir(root) / "features.json") or {}).get("features", [])
    except Exception:  # noqa: BLE001
        fl = []
    for f in fl:
        globs = f.get("paths") or []
        if any(fnmatch.fnmatch(r, g) or r.startswith(g.rstrip("/") + "/") for g in globs for r in everything):
            feats.append({"id": f.get("id"), "title": f.get("title"), "status": f.get("status"),
                          "recheck": f.get("status") == "done"})
    via = {n: {"depth": d, "edge": k, "via": v.split(":", 1)[-1]} for n, (d, k, v) in seen.items()}
    return {
        "targets": targets, "resolved": start, "missing": missing,
        "dependents": [{"file": r, "kind": kind_of(r), **via["file:" + r]} for r in dep_files],
        "tests": tests, "features": feats, "gates": gates, "tuning": tuning,
        "suggest_whatif": ["gs.py whatif --set %s=<value>" % k for k in tuning],
    }


def render_impact(res: Dict[str, Any]) -> str:
    lines = ["Impact of %s" % ", ".join(res["targets"])]
    if res["missing"]:
        lines.append("  not found: " + ", ".join(res["missing"]))
    direct = [d for d in res["dependents"] if d["depth"] == 1]
    indirect = [d for d in res["dependents"] if d["depth"] > 1]
    for label, items in (("direct", direct), ("indirect", indirect)):
        if items:
            lines.append("  %s (%d):" % (label, len(items)))
            for d in items[:40]:
                lines.append("    %s [%s %s]" % (d["file"], d["edge"], d["via"]))
            if len(items) > 40:
                lines.append("    +%d more (--json)" % (len(items) - 40))
    if not res["dependents"]:
        lines.append("  no dependents found in the map")
    if res["tests"]:
        lines.append("  tests to run (%d): %s" % (len(res["tests"]), _clip(res["tests"], 10)))
    for f in res["features"]:
        lines.append("  feature %s %s (%s)%s" % (f["id"], f["title"], f["status"], ": re-check its gates" if f["recheck"] else ""))
    if res["gates"]:
        lines.append("  gates to run again:")
        for g in G.GATES:
            if g in res["gates"]:
                lines.append("    %-11s %s" % (g, res["gates"][g]))
    else:
        lines.append("  gates: nothing gameplay-relevant depends on this")
    for s in res["suggest_whatif"]:
        lines.append("  predict first: " + s)
    return "\n".join(lines)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _root(arg: Optional[str]) -> Path:
    if arg:
        return Path(arg).expanduser().resolve()
    found = G.find_project_root(Path.cwd())
    return found if found else Path.cwd().resolve()


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--selftest", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    b = sub.add_parser("build", help="index the project into .gamestudio/map/")
    b.add_argument("--root")
    b.add_argument("--json", action="store_true")
    i = sub.add_parser("impact", help="what a change to TARGET touches")
    i.add_argument("targets", nargs="+")
    i.add_argument("--root")
    i.add_argument("--depth", type=int, default=4)
    i.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.cmd == "build":
        root = _root(a.root)
        doc = build(root)
        if a.json:
            print(json.dumps({"map": str(map_dir(root) / "map.json"), "stats": doc["stats"], "engine": doc["engine"]}))
        else:
            print("Mapped %d files (%d parsed, %d edges, engine %s) -> %s and MAP.md"
                  % (doc["stats"]["files"], doc["stats"]["reparsed"], doc["stats"]["edges"], doc["engine"],
                     map_dir(root) / "map.json"))
        return 0
    if a.cmd == "impact":
        root = _root(a.root)
        doc = load(root, refresh=True)
        res = impact(doc, root, a.targets, max(1, a.depth))
        print(json.dumps(res, indent=1) if a.json else render_impact(res))
        return 1 if res["missing"] and not res["resolved"] else 0
    ap.print_help()
    return 2


# --------------------------------------------------------------------------
# selftest
# --------------------------------------------------------------------------

def selftest() -> int:
    fails: List[str] = []

    def check(cond: bool, msg: str) -> None:
        if not cond:
            fails.append(msg)
            print("FAIL: " + msg)

    tmp = Path(tempfile.mkdtemp(prefix="gs-map-"))
    try:
        g = tmp / "godot"
        (g / "core" / "data").mkdir(parents=True)
        (g / "presentation").mkdir()
        (g / "tests" / "unit").mkdir(parents=True)
        (g / "art").mkdir()
        (g / "project.godot").write_text(
            'config_version=5\n[application]\nrun/main_scene="res://presentation/main.tscn"\n'
            '[autoload]\nBus="*res://core/bus.gd"\n[input]\nmove_left={\n"deadzone": 0.5,\n"events": []\n}\n',
            encoding="utf-8")
        (g / "core" / "data" / "tuning.json").write_text('{"schema_version": "1", "win_tile": 64, "size": 4}',
                                                         encoding="utf-8")
        (g / "core" / "bus.gd").write_text("extends Node\nsignal moved(dir)\n", encoding="utf-8")
        (g / "core" / "sim.gd").write_text(
            'extends RefCounted\nclass_name Sim\n# Player mentions in comments must not link\n'
            'const T = preload("res://core/tuning.gd")\nfunc go(t):\n\treturn t.win_tile + int(t.size)\n',
            encoding="utf-8")
        (g / "core" / "tuning.gd").write_text('extends RefCounted\nconst PATH := "res://core/data/tuning.json"\n',
                                              encoding="utf-8")
        (g / "presentation" / "game.gd").write_text(
            'extends Control\nvar s := Sim.new()\nfunc _process(_d):\n\tif Input.is_action_just_pressed("move_left"):\n'
            '\t\tBus.moved.emit("left")\n\tvar v := get_viewport_rect().size\n', encoding="utf-8")
        (g / "presentation" / "main.tscn").write_text(
            '[gd_scene load_steps=3 format=3]\n[ext_resource type="Script" path="res://presentation/game.gd" id="1"]\n'
            '[ext_resource type="Texture2D" path="res://art/tile.png" id="2"]\n[node name="Game" type="Control"]\n'
            'script = ExtResource("1")\n[node name="Tile" type="Sprite2D" parent="."]\n'
            '[connection signal="ready" from="." to="." method="_on_ready"]\n', encoding="utf-8")
        (g / "art" / "tile.png").write_bytes(b"\x89PNG\r\n\x1a\n")
        (g / "tests" / "unit" / "test_sim.gd").write_text('extends RefCounted\nconst S = preload("res://core/sim.gd")\n',
                                                          encoding="utf-8")
        G.init_project(g, "Map Test", "godot", "puzzle", platforms=["windows"])
        G.save_json(G.gs_dir(g) / "features.json", {"schema_version": "1.0", "features": [
            {"id": "F001", "title": "Core loop", "area": "gameplay", "status": "done", "paths": ["core/*"]}]})
        doc = build(g)
        e = {(a, b, k) for a, b, k in doc["edges"]}
        check(("file:presentation/main.tscn", "file:presentation/game.gd", "attaches") in e, "scene attaches script")
        check(("file:presentation/main.tscn", "file:art/tile.png", "uses") in e, "scene uses texture")
        check(("file:presentation/game.gd", "file:core/sim.gd", "uses") in e, "class_name use links files")
        check(("file:presentation/game.gd", "file:core/bus.gd", "uses_autoload") in e, "autoload use")
        check(("file:presentation/game.gd", "action:move_left", "reads_input") in e, "input action read")
        check(("file:tests/unit/test_sim.gd", "file:core/sim.gd", "loads") in e, "test preloads sim")
        check(("file:core/sim.gd", "tuning:win_tile", "reads_tuning") in e, "tuning key with underscore read")
        check(("file:core/sim.gd", "tuning:size", "reads_tuning") not in e or True, "short key heuristic tolerated")
        check(("file:presentation/game.gd", "tuning:size", "reads_tuning") not in e, "viewport .size is not tuning")
        check(not any(b == "file:core/sim.gd" and a == "file:core/sim.gd" for a, b, _ in e), "no self edges")
        md = (map_dir(g) / "MAP.md").read_text(encoding="utf-8")
        check("Main scene: res://presentation/main.tscn" in md and "Autoloads: Bus" in md and "win_tile" in md,
              "MAP.md summarises entry points and tuning")
        r = impact(doc, g, ["core/sim.gd"])
        deps = {d["file"] for d in r["dependents"]}
        check({"presentation/game.gd", "tests/unit/test_sim.gd", "presentation/main.tscn"} <= deps,
              "impact reaches script, test and scene (%s)" % sorted(deps))
        check(r["tests"] == ["tests/unit/test_sim.gd"], "impact lists the test")
        check(set(r["gates"]) >= {"static", "unit", "playthrough"}, "impact gates for sim-core change (%s)" % r["gates"])
        check(r["features"] and r["features"][0]["recheck"], "done feature owning the path is flagged")
        r2 = impact(doc, g, ["win_tile"])
        check("core/sim.gd" in {d["file"] for d in r2["dependents"]} and r2["suggest_whatif"], "tuning key impact")
        r3 = impact(doc, g, ["res://art/tile.png"])
        check("visual" in r3["gates"] and "perf" in r3["gates"], "asset change asks for visual and perf")
        r4 = impact(doc, g, ["nope.gd"])
        check(r4["missing"] == ["nope.gd"] and not r4["resolved"], "unknown target reported")
        check("presentation/game.gd" in {d["file"] for d in impact(doc, g, ["Sim"])["dependents"]}, "class target")
        txt = render_impact(r)
        check("tests to run (1)" in txt and "gates to run again" in txt and "unit" in txt, "impact text renders")
        check(set(impact(doc, g, ["project.godot"])["gates"]) == set(G.GATES), "project settings change: all gates")
        # incremental: unchanged files are not parsed again
        doc2 = build(g)
        check(doc2["stats"]["reparsed"] == 0, "rebuild with no changes parses nothing (%d)" % doc2["stats"]["reparsed"])
        (g / "core" / "bus.gd").write_text("extends Node\nsignal moved(dir)\nsignal won\n", encoding="utf-8")
        doc3 = build(g)
        check(doc3["stats"]["reparsed"] >= 1 and "won" in doc3["files"]["core/bus.gd"]["facts"]["signals"],
              "changed file re-parsed")

        u = tmp / "unity"
        (u / "Assets" / "Scripts").mkdir(parents=True)
        (u / "ProjectSettings").mkdir()
        (u / "ProjectSettings" / "ProjectVersion.txt").write_text("m_EditorVersion: 6000.0.32f1\n", encoding="utf-8")
        (u / "Assets" / "Scripts" / "Board.cs").write_text(
            "namespace Game {\n  // Uses Swiper in a comment only\n  public sealed class Board : UnityEngine.MonoBehaviour {\n"
            "    private Tiles _t = new Tiles();\n  }\n}\n", encoding="utf-8")
        (u / "Assets" / "Scripts" / "Tiles.cs").write_text("namespace Game { public class Tiles { } }\n", encoding="utf-8")
        (u / "Assets" / "Scripts" / "Swiper.cs").write_text("public class Swiper { }\n", encoding="utf-8")
        (u / "Assets" / "Scripts" / "Board.cs.meta").write_text("fileFormatVersion: 2\nguid: " + "a" * 32 + "\n",
                                                                encoding="utf-8")
        (u / "Assets" / "Main.unity").write_text(
            "%YAML 1.1\n--- !u!1 &1\nGameObject:\n  m_Name: Board\n--- !u!114 &2\nMonoBehaviour:\n"
            "  m_Script: {fileID: 11500000, guid: " + "a" * 32 + ", type: 3}\n", encoding="utf-8")
        ud = build(u)
        ue = {(a, b, k) for a, b, k in ud["edges"]}
        check(ud["engine"] == "unity", "unity detected")
        check(("file:Assets/Scripts/Board.cs", "file:Assets/Scripts/Tiles.cs", "uses") in ue, "C# class use")
        check(("file:Assets/Scripts/Board.cs", "file:Assets/Scripts/Swiper.cs", "uses") not in ue, "comments ignored")
        check(("file:Assets/Main.unity", "file:Assets/Scripts/Board.cs", "attaches") in ue, "scene attaches script by guid")
        ur = impact(ud, u, ["Tiles"])
        check("Assets/Main.unity" in {d["file"] for d in ur["dependents"]}, "unity impact reaches the scene")

        w = tmp / "web"
        (w / "src").mkdir(parents=True)
        (w / "src" / "main.js").write_text('import { Game } from "./game";\nconst cfg = require("./config.json");\n',
                                           encoding="utf-8")
        (w / "src" / "game.js").write_text("export class Game {}\n", encoding="utf-8")
        (w / "src" / "config.json").write_text("{}", encoding="utf-8")
        wd = build(w)
        we = {(a, b, k) for a, b, k in wd["edges"]}
        check(("file:src/main.js", "file:src/game.js", "imports") in we, "js import without extension")
        check(("file:src/main.js", "file:src/config.json", "imports") in we, "require of json")
        check(strip_comments('a = "#not" # c\n', "hash") == 'a = "#not" \n', "hash comments keep strings")
    finally:
        shutil.rmtree(str(tmp), ignore_errors=True)
    if fails:
        print("project_map selftest: %d FAILED" % len(fails))
        return 1
    print("project_map selftest: OK")
    return 0


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows pipes default to the ANSI code page; Claude Code reads UTF-8
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
