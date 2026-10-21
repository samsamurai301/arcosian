#!/usr/bin/env python3
"""gslib - shared library for the arcosian plugin (stdlib only, Python 3.9+).

Everything that reads or writes a project's `.gamestudio/` state goes through
this module: the `gs.py` CLI, the hooks (SessionStart, PreToolUse guard,
PostToolUse schema check, Stop gate, TaskCompleted gate, PreCompact) and any
script that needs the project state.

Import it from a hook or script like this::

    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))  # from hooks/scripts/
    import gslib

Public API (BLUEPRINT section 7, plus helpers used by gs.py):

    find_project_root(start) -> Path | None
    gs_dir(root) -> Path
    load_json(path, default=None, strict=False)
    save_json(path, data)                    # atomic, indent 2, trailing newline
    load_state(root) -> dict                 # config, contract, features, manifest, budget
    GATES = ("static", "unit", "playthrough", "visual", "perf")
    check_feature_pass(feature, root) -> (bool, [problems])
    feature_counts(features_doc) -> dict
    next_feature(features_doc) -> dict | None
    summarize(root, max_chars=2500) -> str
    schema_for(path) -> Path | None
    validate_file(path) -> [errors]
    append_progress(root, text)

    init_project(...), new_feature(...), set_gate(...), mark_pass(...),
    ready_features(...), waiting_features(...), failing_gates(...),
    dod_violations(...), lint_features(...), normalize_evidence(...),
    evidence_contradiction(...), read_progress_entries(...),
    budget_summary(...), state_lock(root), validator_available(),
    kb_search(query, skills_root=None, skill=None, limit=8),
    cross_check(root) -> [(severity, message)]

The five-gate rule (BLUEPRINT section 6): a feature may only have
`passes: true` / `status: "done"` when every gate is "pass" or "n/a", every
"pass" gate has evidence that exists on disk, and every "n/a" gate has a
`gate_notes` entry.  This module adds one stricter, cheap check: evidence that
itself reports failure (a JSON report with `"verdict": "fail"`, or a JUnit XML
with failures/errors > 0) does not count as evidence of a pass.

Hooks: every function that reads state tolerates missing or corrupt files
(returns None / defaults and warns on stderr); validate_file() fails open
when scripts/validate_json.py is missing or crashes; summarize() never raises.

CLI: `python3 gslib.py --selftest | --summarize [ROOT] [--max-chars N] |
--validate PATH... [--json]`.
"""
from __future__ import annotations

import contextlib
import importlib.util
import json
import math
import os
import re
import shutil
import sys
import tempfile
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple

__version__ = "1.0.0"

# --------------------------------------------------------------------------
# Constants (names and enums are binding: BLUEPRINT section 5)
# --------------------------------------------------------------------------

SCHEMA_VERSION = "1.0"
SCRIPTS_DIR = Path(__file__).resolve().parent
PLUGIN_ROOT = SCRIPTS_DIR.parent
SCHEMAS_DIR = SCRIPTS_DIR / "schemas"
VALIDATOR_PATH = SCRIPTS_DIR / "validate_json.py"
GS_DIRNAME = ".gamestudio"

GATES = ("static", "unit", "playthrough", "visual", "perf")
GATE_RESULTS = ("pass", "fail", "n/a")
PRIORITIES = ("P0", "P1", "P2")
STATUSES = ("todo", "in_progress", "blocked", "done")
AREAS = (
    "gameplay", "meta", "ui", "ux", "audio", "art", "vfx", "monetization",
    "analytics", "liveops", "tech", "perf", "release", "content",
)
ENGINES = ("godot", "unity", "unreal", "defold", "web", "other")
PLATFORMS = ("ios", "android", "web", "windows", "macos", "linux", "switch", "playstation", "xbox", "other")
ORIENTATIONS = ("portrait", "landscape", "both")
TIERS = ("prototype", "slice", "soft_launch", "global", "live")
MONETIZATION_MODELS = ("premium", "iap", "ads", "hybrid", "subscription")
FEATURE_ID_RE = re.compile(r"^F\d{3,4}$")

STATE_FILES = {
    "config": "config.json",
    "contract": "contract.json",
    "features": "features.json",
    "manifest": "assets/manifest.json",
    "budget": "budget.json",
}
PROGRESS_FILE = "progress.md"
PROJECT_SUBDIRS = (
    "assets", "design", "art", "audio", "concepts", "research", "economy", "levels", "analytics",
    "evidence", "playtests", "reports", "snapshots",
)

DEFAULT_ASSET_USD_CAP = 50.0
DEFAULT_PER_CALL_USD_CAP = 5.0
DEFAULT_LICENCE_ALLOWLIST = ["commercial-paid", "cc0", "cc-by", "mit", "apache-2.0"]

# Engine version defaults for new projects.  Volatile (as of Oct 2026, verify):
#   Godot 4.7 is the current stable line  - https://godotengine.org/releases/4.7/
#   Unity 6.3 LTS (6000.3) is the current LTS - https://unity.com/unity-6-release
DEFAULT_ENGINE_VERSIONS = {"godot": "4.7", "unity": "6000.3"}

# Default perf budgets for a new contract.  These are starting *targets*
# (engineering decisions to tune per game), not market facts.
DEFAULT_PERF_BUDGETS = {
    "fps_target": 60,
    "frame_ms_p95": 16.7,      # 1000 ms / 60 fps
    "memory_mb": 512,
    "download_mb": 150,
    "cold_start_sec": 5,
}

PRIORITY_RANK = {"P0": 0, "P1": 1, "P2": 2}

_warned: set = set()


def _warn(msg: str, once_key: Optional[str] = None) -> None:
    """Print a one-line warning to stderr (optionally only once per process)."""
    if once_key is not None:
        if once_key in _warned:
            return
        _warned.add(once_key)
    try:
        sys.stderr.write("gslib: warning: %s\n" % msg)
    except Exception:  # pragma: no cover - stderr closed
        pass


# --------------------------------------------------------------------------
# Paths and JSON IO
# --------------------------------------------------------------------------

def _abspath(p: Any) -> Path:
    path = Path(str(p)).expanduser()
    if not path.is_absolute():
        path = Path.cwd() / path
    try:
        return path.resolve()
    except (OSError, RuntimeError):  # pragma: no cover - symlink loops
        return Path(os.path.abspath(str(path)))


def find_project_root(start: Any) -> Optional[Path]:
    """Return the nearest ancestor of `start` (inclusive) containing `.gamestudio/`.

    `start` may be a directory, a file, or a path that does not exist yet
    (e.g. a file about to be written by a tool call).
    """
    if start is None or str(start) == "":
        return None
    p = _abspath(start)
    for cand in [p] + list(p.parents):
        try:
            if (cand / GS_DIRNAME).is_dir():
                return cand
        except OSError:
            continue
    return None


def gs_dir(root: Any) -> Path:
    """Path of the `.gamestudio/` directory for a project root."""
    return Path(str(root)) / GS_DIRNAME


def state_path(root: Any, key: str) -> Path:
    """Path of a state document: key in config|contract|features|manifest|budget|progress."""
    if key == "progress":
        return gs_dir(root) / PROGRESS_FILE
    return gs_dir(root) / STATE_FILES[key]


def load_json(path: Any, default: Any = None, strict: bool = False) -> Any:
    """Load a JSON file.

    Missing file -> `default`.  Invalid JSON -> `default` (with a stderr
    warning), or raises ValueError when `strict=True` so callers that are
    about to rewrite the file never clobber a document they could not read.
    """
    p = Path(str(path))
    try:
        text = p.read_text(encoding="utf-8")
    except FileNotFoundError:
        return default
    except IsADirectoryError:
        if strict:
            raise ValueError("%s is a directory, not a JSON file" % p)
        return default
    except OSError as exc:
        if strict:
            raise ValueError("cannot read %s: %s" % (p, exc))
        _warn("cannot read %s: %s" % (p, exc))
        return default
    try:
        return json.loads(text)
    except ValueError as exc:
        if strict:
            raise ValueError("%s is not valid JSON: %s" % (p, exc))
        _warn("%s is not valid JSON (%s); using default" % (p, exc))
        return default


def save_json(path: Any, data: Any) -> Path:
    """Atomically write `data` as JSON (indent 2, UTF-8, trailing newline).

    Writes to a temp file in the same directory, fsyncs, then os.replace()s it
    over the target, so readers (hooks) never see a half-written file.
    Existing file permissions are preserved.
    """
    p = Path(str(path))
    p.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    fd, tmp = tempfile.mkstemp(prefix=".%s." % p.name, suffix=".tmp", dir=str(p.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
            fh.flush()
            os.fsync(fh.fileno())
        if p.exists():
            mode = p.stat().st_mode & 0o777
        else:
            umask = os.umask(0)
            os.umask(umask)
            mode = 0o666 & ~umask
        os.chmod(tmp, mode)
        os.replace(tmp, str(p))
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    return p


def load_state(root: Any) -> Dict[str, Any]:
    """Load the five state documents. Missing (or unreadable) documents are None."""
    return {key: load_json(state_path(root, key), None) for key in STATE_FILES}


@contextlib.contextmanager
def state_lock(root: Any, timeout: float = 15.0) -> Iterator[None]:
    """Exclusive advisory lock on `.gamestudio/.lock` for read-modify-write of state files.

    Parallel agents running gs.py against one project would otherwise lose
    updates to features.json.  POSIX only (fcntl); a no-op where unavailable.
    Raises TimeoutError if the lock cannot be taken within `timeout` seconds.
    """
    try:
        import fcntl  # type: ignore
    except ImportError:  # pragma: no cover - Windows
        yield
        return
    path = gs_dir(root) / ".lock"
    path.parent.mkdir(parents=True, exist_ok=True)
    fh = open(str(path), "a+", encoding="utf-8")
    try:
        deadline = time.monotonic() + timeout
        while True:
            try:
                fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError:
                if time.monotonic() >= deadline:
                    raise TimeoutError("could not lock %s within %.0f s (another gs.py running?)" % (path, timeout))
                time.sleep(0.05)
        yield
    finally:
        try:
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
        except OSError:
            pass
        fh.close()


def now_stamp() -> str:
    """Local time stamp used in progress.md entries: YYYY-MM-DD HH:MM."""
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def now_iso() -> str:
    """UTC ISO 8601 timestamp with seconds, e.g. 2026-10-19T08:15:00Z."""
    return datetime.now(timezone.utc).replace(microsecond=0, tzinfo=None).isoformat() + "Z"


def rel_to_root(path: Any, root: Any) -> str:
    """Project-relative POSIX path when `path` is inside `root`, else absolute POSIX."""
    ap = _abspath(path)
    try:
        return ap.relative_to(_abspath(root)).as_posix()
    except ValueError:
        return ap.as_posix()


# --------------------------------------------------------------------------
# Skeleton documents and project initialisation
# --------------------------------------------------------------------------

def slugify(text: str) -> str:
    """ASCII kebab-case slug: "Merge Ninja: Tiles!" -> "merge-ninja-tiles"."""
    s = re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")
    return s or "game"


def detect_engine(root: Any) -> Tuple[Optional[str], Optional[str], str]:
    """Detect an engine project at `root` or one level below.

    Returns (engine, engine_version, project_root_relative).  engine is None
    when nothing is detected.
    """
    root = Path(str(root))
    cands = [root]
    try:
        cands += sorted(d for d in root.iterdir() if d.is_dir() and not d.name.startswith("."))
    except OSError:
        pass
    for d in cands:
        rel = "." if d == root else d.name
        if (d / "project.godot").is_file():
            ver = None
            try:
                m = re.search(r'config/features=PackedStringArray\("(\d+\.\d+)',
                              (d / "project.godot").read_text(encoding="utf-8", errors="replace"))
                ver = m.group(1) if m else None
            except OSError:
                pass
            return "godot", ver, rel
        pv = d / "ProjectSettings" / "ProjectVersion.txt"
        if pv.is_file():
            ver = None
            try:
                m = re.search(r"m_EditorVersion:\s*(\S+)", pv.read_text(encoding="utf-8", errors="replace"))
                ver = m.group(1) if m else None
            except OSError:
                pass
            return "unity", ver, rel
        if list(d.glob("*.uproject")):
            return "unreal", None, rel
        if (d / "game.project").is_file():
            return "defold", None, rel
    return None, None, "."


def default_config(title: str, engine: str = "other", *, slug: Optional[str] = None,
                   engine_version: Optional[str] = None, platforms: Optional[List[str]] = None,
                   orientation: str = "portrait", tier: str = "prototype",
                   asset_usd_cap: float = DEFAULT_ASSET_USD_CAP,
                   per_call_usd_cap: float = DEFAULT_PER_CALL_USD_CAP,
                   project_root: str = ".") -> Dict[str, Any]:
    """Skeleton `.gamestudio/config.json` (BLUEPRINT section 5 field names)."""
    if engine_version is None:
        engine_version = DEFAULT_ENGINE_VERSIONS.get(engine)
    doc: Dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "project": {"title": title, "slug": slug or slugify(title)},
        "engine": engine,
        "engine_version": engine_version,
        "platforms": list(platforms or ["ios", "android"]),
        "orientation": orientation,
        "paths": {
            "project_root": project_root,
            "assets_dir": "assets/",
            "generated_dir": "assets/generated/",
        },
        "budgets": {"asset_usd_cap": asset_usd_cap, "per_call_usd_cap": per_call_usd_cap},
        "revenue": {"lifetime_gross_usd": 0, "developer_annual_games_revenue_usd": 0},
        "storefronts": ["US"],
        "licence_allowlist": list(DEFAULT_LICENCE_ALLOWLIST),
        "providers": {
            "image": "auto",
            "model3d": "tripo",
            "music": "elevenlabs",
            "sfx": "elevenlabs",
            "voice": "elevenlabs",
        },
        "tier": tier,
    }
    if not engine_version:          # schema requires a numeric-looking version when present
        del doc["engine_version"]
    return doc


def default_contract(title: str, engine: str = "other", *, genre: Optional[str] = None,
                     platforms: Optional[List[str]] = None, orientation: str = "portrait",
                     tier: str = "prototype", monetization_model: str = "hybrid") -> Dict[str, Any]:
    """Skeleton design contract with every section present and type-correct.

    Strings that must be decided by design start with "TBD" so reviews and
    the summary can tell an unfilled contract from a real one.  Numeric KPI
    targets start at 0 (= not set); perf budgets start at engineering defaults
    because the perf gate needs budgets from day one.  The *_ref fields hold
    the conventional locations of the economy model, level specs, style and
    audio bibles and event taxonomy; those files are created later.
    """
    return {
        "schema_version": SCHEMA_VERSION,
        "meta": {
            "title": title,
            "logline": "TBD: one sentence - who the player is, what they do, why it is fun.",
            "genre": genre or "TBD",
            "subgenre": "",
            "platforms": list(platforms or ["ios", "android"]),
            "orientation": orientation,
            "engine": engine,
            "target_audience": {"age_min": 13, "segments": [], "motivations": []},
            "session_length_target_sec": 180,
            "monetization_model": monetization_model,
            "analogy": "",
            "comparables": [],
            "pillars": [
                "TBD pillar 1: the feeling every feature must serve",
                "TBD pillar 2",
                "TBD pillar 3",
            ],
        },
        "player_fantasy": "TBD",
        "verbs": [],
        "mechanics": [],
        "loops": [],
        "economy": {"currencies": [], "model_ref": ".gamestudio/economy/model.economy.json"},
        "progression": {
            "tracks": [],
            "difficulty": {"model": "TBD", "target_win_rate": 0.7, "dda": False},
        },
        "content": {
            "levels": {"target_count": 0, "generation": "handmade", "spec_ref": ".gamestudio/levels/"},
            "worlds": [],
            "characters": [],
        },
        "ftue": {"aha_seconds_target": 60, "steps": []},
        "ux": {"hud": [], "screens": [], "accessibility": []},
        "art_direction": {"style": "", "palette": [], "references": [], "bible_ref": "docs/style-bible.md"},
        "audio_direction": {"music": "", "sfx": "", "voice": "", "bible_ref": "docs/audio-bible.md"},
        "monetization": {
            "iap": [],
            "ads": {
                "rewarded": [],
                "interstitial": {"min_interval_sec": 120, "first_after_sec": 600},
            },
            "pass": {},
            "ethics": [
                "No dark patterns: no fake scarcity timers, confirm-shaming or disguised ads.",
                "Disclose odds for every randomized paid item before purchase.",
                "Rewarded ads are always optional and always pay out what they promise.",
                "Respect minors: age-appropriate offers, no spend pressure, honour platform parental controls.",
            ],
        },
        "liveops": {"cadence": "", "events": []},
        "analytics": {
            "kpi_targets": {
                "d1": 0, "d7": 0, "d30": 0, "session_len_sec": 0,
                "sessions_per_day": 0, "arpdau_usd": 0, "payer_conversion": 0,
            },
            "taxonomy_ref": ".gamestudio/analytics/events.taxonomy.json",
        },
        "technical": {
            "architecture": "sim-core+presentation",
            "deterministic": True,
            "min_spec": {"ram_gb": 3, "gpu_class": "TBD", "os_min": {"ios": "15.0", "android_api": 24}},
            "perf_budgets": dict(DEFAULT_PERF_BUDGETS),
            "backend": "none",
            "multiplayer": "none",
        },
        "scope": {"tier": tier, "must": [], "should": [], "wont": []},
        "risks": [],
        "kill_criteria": [],
    }


def empty_features() -> Dict[str, Any]:
    return {"schema_version": SCHEMA_VERSION, "features": []}


def empty_budget(cap_usd: float = DEFAULT_ASSET_USD_CAP) -> Dict[str, Any]:
    return {"schema_version": SCHEMA_VERSION, "cap_usd": cap_usd, "spent_usd": 0, "ledger": []}


def empty_manifest() -> Dict[str, Any]:
    return {"schema_version": SCHEMA_VERSION, "assets": []}


def progress_header(title: str) -> str:
    return (
        "# Progress log - %s\n\n"
        "Append-only session log, newest entries at the bottom. One line per entry:\n"
        "`- [YYYY-MM-DD HH:MM] what changed, what was verified, what is next`.\n"
        "Add entries with `gs.py progress \"text\"`; never rewrite history.\n\n" % title
    )


def init_project(root: Any, title: str, engine: Optional[str] = None, genre: Optional[str] = None, *,
                 force: bool = False, slug: Optional[str] = None, engine_version: Optional[str] = None,
                 platforms: Optional[List[str]] = None, orientation: str = "portrait",
                 tier: str = "prototype", monetization_model: str = "hybrid",
                 asset_usd_cap: float = DEFAULT_ASSET_USD_CAP,
                 per_call_usd_cap: float = DEFAULT_PER_CALL_USD_CAP) -> Dict[str, Any]:
    """Create the full `.gamestudio/` tree (BLUEPRINT section 5) with skeleton documents.

    Never overwrites an existing file unless `force=True`; with force, the
    previous versions are copied to `.gamestudio/snapshots/init-backup-<ts>/`
    first, and progress.md is never truncated (an entry is appended instead).
    Returns {root, gs_dir, engine, created, skipped, overwritten, dirs_created, backup_dir}.
    """
    root_p = _abspath(root)
    g = gs_dir(root_p)
    det_engine, det_version, det_rel = detect_engine(root_p)
    if not engine:
        engine = det_engine or "other"
    if engine not in ENGINES:
        raise ValueError("engine must be one of %s" % ", ".join(ENGINES))
    if orientation not in ORIENTATIONS:
        raise ValueError("orientation must be one of %s" % ", ".join(ORIENTATIONS))
    if tier not in TIERS:
        raise ValueError("tier must be one of %s" % ", ".join(TIERS))
    if monetization_model not in MONETIZATION_MODELS:
        raise ValueError("monetization model must be one of %s" % ", ".join(MONETIZATION_MODELS))
    plats = [p.strip().lower() for p in (platforms or ["ios", "android"]) if p and p.strip()]
    bad = [p for p in plats if p not in PLATFORMS]
    if bad or not plats:
        raise ValueError("platforms must be a non-empty subset of %s" % ", ".join(PLATFORMS))
    if slug is not None and not re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", slug):
        raise ValueError("slug must be kebab-case ASCII (e.g. merge-ninja), got %r" % slug)
    if engine_version is not None and not re.match(r"^\d+(\.\d+){0,3}[A-Za-z0-9.+_-]*$", engine_version):
        raise ValueError("engine version must start with a number (e.g. 4.7 or 6000.3.2f1), got %r"
                         % engine_version)
    if engine_version is None and det_engine == engine and det_version:
        engine_version = det_version
    project_rel = det_rel if det_engine == engine else "."

    docs = {
        "config.json": default_config(
            title, engine, slug=slug, engine_version=engine_version, platforms=plats,
            orientation=orientation, tier=tier, asset_usd_cap=asset_usd_cap,
            per_call_usd_cap=per_call_usd_cap, project_root=project_rel),
        "contract.json": default_contract(
            title, engine, genre=genre, platforms=plats, orientation=orientation, tier=tier,
            monetization_model=monetization_model),
        "features.json": empty_features(),
        "budget.json": empty_budget(asset_usd_cap),
        "assets/manifest.json": empty_manifest(),
    }
    created: List[str] = []
    skipped: List[str] = []
    overwritten: List[str] = []
    dirs_created: List[str] = []
    backup_dir: Optional[Path] = None

    if not g.is_dir():
        g.mkdir(parents=True)
        dirs_created.append(GS_DIRNAME + "/")
    for sub in PROJECT_SUBDIRS:
        d = g / sub
        if not d.is_dir():
            d.mkdir(parents=True)
            dirs_created.append("%s/%s/" % (GS_DIRNAME, sub))

    for rel, data in docs.items():
        p = g / rel
        if p.exists():
            if not force:
                skipped.append(rel)
                continue
            if backup_dir is None:
                backup_dir = g / "snapshots" / ("init-backup-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
            dest = backup_dir / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(str(p), str(dest))
            overwritten.append(rel)
        save_json(p, data)
        created.append(rel)

    prog = g / PROGRESS_FILE
    if not prog.exists():
        prog.write_text(progress_header(title), encoding="utf-8")
        append_progress(root_p, "Project initialized: \"%s\" (engine %s, tier %s, platforms %s)."
                        % (title, engine, tier, ", ".join(plats)))
        created.append(PROGRESS_FILE)
    elif force:
        append_progress(root_p, "Re-initialized skeleton documents with --force (backup: %s)."
                        % (rel_to_root(backup_dir, root_p) if backup_dir else "none needed"))
        skipped.append(PROGRESS_FILE + " (kept; entry appended)")
    else:
        skipped.append(PROGRESS_FILE)

    gi = g / ".gitignore"
    if not gi.exists():
        gi.write_text("# gs.py lock file\n.lock\n", encoding="utf-8")

    # Keep empty directories in version control.
    for sub in PROJECT_SUBDIRS:
        d = g / sub
        try:
            if not any(d.iterdir()):
                (d / ".gitkeep").write_text("", encoding="utf-8")
        except OSError:
            pass

    return {
        "root": str(root_p),
        "gs_dir": str(g),
        "engine": engine,
        "created": created,
        "skipped": skipped,
        "overwritten": overwritten,
        "dirs_created": dirs_created,
        "backup_dir": str(backup_dir) if backup_dir else None,
    }


# --------------------------------------------------------------------------
# Features: the five-gate definition of done
# --------------------------------------------------------------------------

def get_features(features_doc: Any) -> List[Dict[str, Any]]:
    """The list of feature dicts in a features document (tolerant of bad input)."""
    if isinstance(features_doc, dict):
        feats = features_doc.get("features")
        if isinstance(feats, list):
            return [f for f in feats if isinstance(f, dict)]
    return []


def find_feature(features_doc: Any, feature_id: str) -> Optional[Dict[str, Any]]:
    fid = str(feature_id).strip().upper()
    for f in get_features(features_doc):
        if str(f.get("id", "")).upper() == fid:
            return f
    return None


def normalize_feature_id(feature_id: str) -> str:
    """'f12' -> 'F012'; 'F0012' stays.  Raises ValueError if not a feature id."""
    s = str(feature_id).strip().upper()
    m = re.match(r"^F(\d{1,4})$", s)
    if not m:
        raise ValueError("feature id must look like F001 (pattern ^F\\d{3,4}$), got %r" % feature_id)
    digits = m.group(1)
    if len(digits) < 3:
        digits = digits.zfill(3)
    return "F" + digits


def next_feature_id(features_doc: Any) -> str:
    """Next free id: one more than the highest numeric id, zero-padded to 3 (or 4) digits."""
    nums = []
    for f in get_features(features_doc):
        m = re.match(r"^F(\d{3,4})$", str(f.get("id", "")))
        if m:
            nums.append(int(m.group(1)))
    n = (max(nums) + 1) if nums else 1
    if n > 9999:
        raise ValueError("feature id space exhausted (F9999)")
    return "F%03d" % n if n < 1000 else "F%04d" % n


def new_feature(feature_id: str, title: str, area: str, *, priority: str = "P1",
                acceptance: Optional[List[str]] = None, depends_on: Optional[List[str]] = None,
                description: str = "", owner: str = "", notes: str = "") -> Dict[str, Any]:
    """A fresh feature record with every gate unset (null) and no evidence."""
    fid = normalize_feature_id(feature_id)
    if not str(title).strip():
        raise ValueError("feature title must not be empty")
    if area not in AREAS:
        raise ValueError("area must be one of %s" % ", ".join(AREAS))
    if priority not in PRIORITIES:
        raise ValueError("priority must be one of %s" % ", ".join(PRIORITIES))
    deps = [normalize_feature_id(d) for d in (depends_on or []) if str(d).strip()]
    if fid in deps:
        raise ValueError("%s cannot depend on itself" % fid)
    return {
        "id": fid,
        "title": str(title).strip(),
        "area": area,
        "description": description or "",
        "acceptance": [a for a in (acceptance or []) if str(a).strip()],
        "depends_on": deps,
        "priority": priority,
        "status": "todo",
        "passes": False,
        "gates": {g: None for g in GATES},
        "evidence": {g: None for g in GATES},
        "gate_notes": {},
        "owner": owner or "",
        "notes": notes or "",
    }


def _as_path_list(value: Any) -> List[Any]:
    """Evidence value (None | str | [str]) -> list (non-strings kept so they can be reported)."""
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return list(value)
    return [value]


def resolve_evidence(path: str, root: Any) -> Path:
    """Absolute path of an evidence entry (project-relative entries resolve against root)."""
    p = Path(str(path)).expanduser()
    if not p.is_absolute():
        p = Path(str(root)) / p
    return p


_JUNIT_ROOT_RE = re.compile(r"<testsuites\b([^>]*)>", re.S)
_JUNIT_SUITE_RE = re.compile(r"<testsuite\b([^>]*)>", re.S)
_ATTR_RE = re.compile(r'\b(failures|errors)\s*=\s*["\'](\d+)["\']')


def evidence_contradiction(path: Path) -> Optional[str]:
    """Return a reason string if the evidence file itself reports failure, else None.

    Checks only cheap, unambiguous signals: a JSON object whose top-level
    `verdict` is "fail" (playtest-report / perf-report schemas), and a JUnit
    XML whose root <testsuites> (or, without one, the sum of <testsuite>
    elements) reports failures or errors > 0.  An empty directory also counts.
    Unreadable or unknown formats return None (existence is what the rule requires).
    """
    try:
        if path.is_dir():
            return None if any(path.iterdir()) else "is an empty directory"
        size = path.stat().st_size
        if size > 32 * 1024 * 1024:
            return None
        suffix = path.suffix.lower()
        if suffix == ".json":
            data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
            if isinstance(data, dict) and str(data.get("verdict", "")).lower() == "fail":
                return "reports verdict \"fail\""
        elif suffix == ".xml":
            text = path.read_text(encoding="utf-8", errors="replace")
            m = _JUNIT_ROOT_RE.search(text)
            if m and _ATTR_RE.search(m.group(1)):
                bad = sum(int(v) for _, v in _ATTR_RE.findall(m.group(1)))
            else:
                bad = sum(int(v) for attrs in _JUNIT_SUITE_RE.findall(text)
                          for _, v in _ATTR_RE.findall(attrs))
            if bad > 0:
                return "reports %d failing/erroring test(s)" % bad
    except (OSError, ValueError):
        return None
    return None


def check_feature_pass(feature: Dict[str, Any], root: Any) -> Tuple[bool, List[str]]:
    """Apply the five-gate rule to one feature.

    Returns (ok, problems).  ok is True only when every gate in GATES is
    "pass" or "n/a"; each "pass" gate lists at least one evidence path, every
    path exists on disk (relative paths resolve against `root`) and none of
    them reports failure; each "n/a" gate has a non-empty gate_notes entry.
    """
    if not isinstance(feature, dict):
        return False, ["feature is not a JSON object"]
    fid = str(feature.get("id") or "?")
    gates = feature.get("gates")
    evidence = feature.get("evidence")
    notes = feature.get("gate_notes")
    problems: List[str] = []
    if not isinstance(gates, dict):
        return False, ["%s: 'gates' is missing or not an object" % fid]
    if evidence is not None and not isinstance(evidence, dict):
        problems.append("%s: 'evidence' is not an object" % fid)
        evidence = {}
    evidence = evidence or {}
    if notes is not None and not isinstance(notes, dict):
        problems.append("%s: 'gate_notes' is not an object" % fid)
        notes = {}
    notes = notes or {}
    for gate in GATES:
        val = gates.get(gate)
        if val == "pass":
            paths = _as_path_list(evidence.get(gate))
            if not paths:
                problems.append("%s: gate '%s' is pass but has no evidence path" % (fid, gate))
                continue
            for raw in paths:
                if not isinstance(raw, str) or not raw.strip():
                    problems.append("%s: gate '%s' has an invalid evidence entry %r" % (fid, gate, raw))
                    continue
                ap = resolve_evidence(raw, root)
                if not ap.exists():
                    problems.append("%s: gate '%s' evidence not found on disk: %s" % (fid, gate, raw))
                    continue
                why = evidence_contradiction(ap)
                if why:
                    problems.append("%s: gate '%s' evidence %s %s" % (fid, gate, raw, why))
        elif val == "n/a":
            note = notes.get(gate)
            if not isinstance(note, str) or not note.strip():
                problems.append("%s: gate '%s' is n/a but gate_notes.%s explaining why is missing"
                                % (fid, gate, gate))
        elif val == "fail":
            problems.append("%s: gate '%s' is fail" % (fid, gate))
        elif val is None:
            problems.append("%s: gate '%s' has not been run (null)" % (fid, gate))
        else:
            problems.append("%s: gate '%s' has invalid value %r (allowed: pass, fail, n/a, null)"
                            % (fid, gate, val))
    return (not problems), problems


def gate_line(feature: Dict[str, Any]) -> str:
    """Compact gate view: 'static=pass unit=fail playthrough=- visual=n/a perf=-'."""
    gates = feature.get("gates") if isinstance(feature.get("gates"), dict) else {}
    return " ".join("%s=%s" % (g, gates.get(g) or "-") for g in GATES)


def gate_code(feature: Dict[str, Any]) -> str:
    """Five-character gate code in GATES order: P=pass X=fail n=n/a .=unset ?=invalid."""
    gates = feature.get("gates") if isinstance(feature.get("gates"), dict) else {}
    out = []
    for g in GATES:
        v = gates.get(g)
        out.append({"pass": "P", "fail": "X", "n/a": "n", None: "."}.get(v, "?"))
    return "".join(out)


def open_gates(feature: Dict[str, Any]) -> List[str]:
    """Gates not yet 'pass' or 'n/a'."""
    gates = feature.get("gates") if isinstance(feature.get("gates"), dict) else {}
    return [g for g in GATES if gates.get(g) not in ("pass", "n/a")]


def feature_counts(features_doc: Any) -> Dict[str, int]:
    """Counts: total, done, passing, in_progress, blocked, todo (missing status counts as todo)."""
    counts = {"total": 0, "done": 0, "passing": 0, "in_progress": 0, "blocked": 0, "todo": 0}
    for f in get_features(features_doc):
        counts["total"] += 1
        if f.get("passes") is True:
            counts["passing"] += 1
        status = f.get("status") or "todo"
        if status in counts and status != "total":
            counts[status] += 1
    return counts


def _deps_status(feature: Dict[str, Any], by_id: Dict[str, Dict[str, Any]]) -> List[str]:
    """Dependency ids that do not (yet) pass, including unknown ids."""
    unmet = []
    for dep in feature.get("depends_on") or []:
        d = by_id.get(str(dep).upper())
        if d is None or d.get("passes") is not True:
            unmet.append(str(dep))
    return unmet


def _by_id(features_doc: Any) -> Dict[str, Dict[str, Any]]:
    return {str(f.get("id", "")).upper(): f for f in get_features(features_doc)}


def ready_features(features_doc: Any) -> List[Dict[str, Any]]:
    """`todo` features whose dependencies all pass, by priority (P0 first), then file order."""
    by_id = _by_id(features_doc)
    ready = []
    for idx, f in enumerate(get_features(features_doc)):
        if (f.get("status") or "todo") != "todo" or f.get("passes") is True:
            continue
        if _deps_status(f, by_id):
            continue
        prio = f.get("priority")
        rank = PRIORITY_RANK.get(prio, 1 if prio in (None, "") else 3)
        ready.append((rank, idx, f))
    ready.sort(key=lambda t: (t[0], t[1]))
    return [f for _, _, f in ready]


def next_feature(features_doc: Any) -> Optional[Dict[str, Any]]:
    """Highest-priority `todo` feature whose dependencies all pass (ties: file order)."""
    r = ready_features(features_doc)
    return r[0] if r else None


def waiting_features(features_doc: Any) -> List[Tuple[Dict[str, Any], List[str]]]:
    """`todo` features blocked by unmet dependencies, with the unmet ids."""
    by_id = _by_id(features_doc)
    out = []
    for f in get_features(features_doc):
        if (f.get("status") or "todo") != "todo" or f.get("passes") is True:
            continue
        unmet = _deps_status(f, by_id)
        if unmet:
            out.append((f, unmet))
    return out


def failing_gates(features_doc: Any) -> List[Tuple[str, List[str]]]:
    """[(feature id, [gates whose value is "fail"])] for features with any failing gate."""
    out = []
    for f in get_features(features_doc):
        gates = f.get("gates") if isinstance(f.get("gates"), dict) else {}
        bad = [g for g in GATES if gates.get(g) == "fail"]
        if bad:
            out.append((str(f.get("id", "?")), bad))
    return out


def dod_violations(features_doc: Any, root: Any) -> List[Tuple[str, List[str]]]:
    """Features marked done/passing that fail check_feature_pass: [(id, problems)]."""
    out = []
    for f in get_features(features_doc):
        if f.get("passes") is True or f.get("status") == "done":
            ok, problems = check_feature_pass(f, root)
            if not ok:
                out.append((str(f.get("id", "?")), problems))
    return out


def normalize_evidence(paths: Iterable[Any], root: Any, cwd: Any = None) -> List[Dict[str, Any]]:
    """Normalise user-supplied evidence paths.

    Relative paths are tried against `cwd` (shell semantics) first, then
    against the project root.  Paths inside the project are stored
    project-relative (POSIX); paths outside are stored absolute.
    Returns [{"stored": str, "abs": str, "exists": bool}].
    """
    root_p = _abspath(root)
    cwd_p = _abspath(cwd) if cwd else Path.cwd()
    out = []
    for raw in paths:
        s = str(raw).strip()
        if not s:
            continue
        p = Path(s).expanduser()
        if p.is_absolute():
            ap = _abspath(p)
        else:
            via_cwd = _abspath(cwd_p / p)
            via_root = _abspath(root_p / p)
            ap = via_cwd if via_cwd.exists() else via_root
        out.append({"stored": rel_to_root(ap, root_p), "abs": str(ap), "exists": ap.exists()})
    return out


def _normalize_result(result: Any) -> Optional[str]:
    if result is None:
        return None
    r = str(result).strip().lower()
    if r in ("pass", "passed", "ok"):
        return "pass"
    if r in ("fail", "failed"):
        return "fail"
    if r in ("n/a", "na", "n-a", "not_applicable", "not-applicable"):
        return "n/a"
    if r in ("reset", "null", "none", "-", ""):
        return None
    raise ValueError("gate result must be pass, fail, n/a (or reset), got %r" % result)


def set_gate(feature: Dict[str, Any], gate: str, result: Any, evidence: Optional[List[str]] = None,
             note: Optional[str] = None, root: Any = None) -> List[str]:
    """Record one gate result on a feature dict (in place). Returns warnings.

    - `evidence` (stored strings) replaces the gate's evidence when given;
      a single path is stored as a string, several as a list.
    - `note` sets gate_notes[gate] (empty string removes it).
    - "n/a" requires a note (given now or already present): ValueError otherwise.
    - "reset" (None) clears the gate and its evidence.
    - A todo feature moves to in_progress.  A passing feature whose gate turns
      fail/unset, or (with `root`) no longer satisfies the rule, is demoted to
      passes=false / status=in_progress (regression).
    """
    if gate not in GATES:
        raise ValueError("gate must be one of %s" % ", ".join(GATES))
    res = _normalize_result(result)
    # Validate before mutating anything.
    old_notes = feature.get("gate_notes") if isinstance(feature.get("gate_notes"), dict) else {}
    final_note = (str(note).strip() or None) if note is not None else old_notes.get(gate)
    if res == "n/a" and not str(final_note or "").strip():
        raise ValueError("gate '%s' = n/a needs a note explaining why (--note TEXT)" % gate)
    gates = feature.get("gates")
    if not isinstance(gates, dict):
        gates = {}
        feature["gates"] = gates
    for g in GATES:
        gates.setdefault(g, None)
    ev = feature.get("evidence")
    if not isinstance(ev, dict):
        ev = {}
        feature["evidence"] = ev
    for g in GATES:
        ev.setdefault(g, None)
    notes = feature.get("gate_notes")
    if not isinstance(notes, dict):
        notes = {}
        feature["gate_notes"] = notes

    if note is not None:
        if final_note:
            notes[gate] = final_note
        else:
            notes.pop(gate, None)

    warnings: List[str] = []
    if res is None:
        ev[gate] = None
    elif evidence:
        items = [str(e) for e in evidence if str(e).strip()]
        if items:
            ev[gate] = items[0] if len(items) == 1 else items
    gates[gate] = res

    fid = str(feature.get("id", "?"))
    if res == "pass" and not _as_path_list(ev.get(gate)):
        warnings.append("%s: gate '%s' recorded as pass without evidence; 'feature pass' will refuse "
                        "until evidence is attached (--evidence PATH)" % (fid, gate))
    if feature.get("status") in (None, "", "todo"):
        feature["status"] = "in_progress"
    if feature.get("passes") is True:
        still_ok = res in ("pass", "n/a")
        if still_ok and root is not None:
            still_ok, _ = check_feature_pass(feature, root)
        if not still_ok:
            feature["passes"] = False
            if feature.get("status") == "done":
                feature["status"] = "in_progress"
            warnings.append("%s: regression - was passing, now gate '%s' = %s; demoted to in_progress "
                            "(passes=false)" % (fid, gate, res if res else "unset"))
    return warnings


def mark_pass(feature: Dict[str, Any], root: Any) -> Tuple[bool, List[str]]:
    """Set passes=true / status=done if and only if check_feature_pass succeeds."""
    ok, problems = check_feature_pass(feature, root)
    if ok:
        feature["passes"] = True
        feature["status"] = "done"
    return ok, problems


def lint_features(features_doc: Any, root: Any) -> Tuple[List[str], List[str]]:
    """Semantic checks beyond the JSON schema. Returns (errors, warnings).

    Errors: malformed document, bad/duplicate ids, unknown or self
    dependencies, dependency cycles, invalid enums/gate values, features
    passing or done without satisfying the five-gate rule, done-but-not-passing.
    Warnings: passes=true with status != done, in-progress work on unmet
    dependencies, schema_version drift.
    """
    errors: List[str] = []
    warnings: List[str] = []
    if features_doc is None:
        return ["features.json is missing"], warnings
    if not isinstance(features_doc, dict):
        return ["features.json must be a JSON object"], warnings
    if features_doc.get("schema_version") != SCHEMA_VERSION:
        warnings.append("schema_version is %r (expected %r)"
                        % (features_doc.get("schema_version"), SCHEMA_VERSION))
    raw = features_doc.get("features")
    if not isinstance(raw, list):
        return errors + ["'features' must be an array"], warnings
    seen: Dict[str, int] = {}
    for i, f in enumerate(raw):
        if not isinstance(f, dict):
            errors.append("features[%d] is not an object" % i)
            continue
        fid = str(f.get("id", ""))
        label = fid or ("features[%d]" % i)
        if not FEATURE_ID_RE.match(fid):
            errors.append("%s: id must match ^F\\d{3,4}$" % label)
        if fid in seen:
            errors.append("%s: duplicate id (also features[%d])" % (fid, seen[fid]))
        seen.setdefault(fid, i)
        if not str(f.get("title", "")).strip():
            errors.append("%s: title is empty" % label)
        if f.get("area") not in AREAS:
            errors.append("%s: area %r is not one of %s" % (label, f.get("area"), "|".join(AREAS)))
        if f.get("priority") not in PRIORITIES:
            errors.append("%s: priority %r is not one of P0|P1|P2" % (label, f.get("priority")))
        if f.get("status") not in STATUSES:
            errors.append("%s: status %r is not one of %s" % (label, f.get("status"), "|".join(STATUSES)))
        gates = f.get("gates")
        if isinstance(gates, dict):
            for g, v in gates.items():
                if g not in GATES:
                    errors.append("%s: unknown gate %r" % (label, g))
                elif v not in (None,) + GATE_RESULTS:
                    errors.append("%s: gate %s has invalid value %r" % (label, g, v))
        else:
            errors.append("%s: gates must be an object" % label)
        if f.get("passes") is True or f.get("status") == "done":
            ok, problems = check_feature_pass(f, root)
            if not ok:
                state = "passes=true" if f.get("passes") is True else "status=done"
                pre = "%s: " % fid
                errors.extend("%s (%s) violates the five-gate rule: %s"
                              % (label, state, p[len(pre):] if p.startswith(pre) else p) for p in problems)
        if f.get("status") == "done" and f.get("passes") is not True:
            errors.append("%s: status is done but passes is not true" % label)
        if f.get("passes") is True and f.get("status") != "done":
            warnings.append("%s: passes is true but status is %r" % (label, f.get("status")))
    ids = set(seen)
    graph: Dict[str, List[str]] = {}
    for f in get_features(features_doc):
        fid = str(f.get("id", ""))
        deps = f.get("depends_on") or []
        if not isinstance(deps, list):
            errors.append("%s: depends_on must be an array" % fid)
            continue
        graph[fid] = [str(d) for d in deps]
        for d in deps:
            if str(d) == fid:
                errors.append("%s: depends on itself" % fid)
            elif str(d) not in ids:
                errors.append("%s: depends on unknown feature %s" % (fid, d))
        if f.get("status") == "in_progress":
            unmet = _deps_status(f, _by_id(features_doc))
            if unmet:
                warnings.append("%s: in progress while dependencies do not pass yet: %s"
                                % (fid, ", ".join(unmet)))
    # cycle detection (iterative DFS, white/grey/black)
    color: Dict[str, int] = {}
    reported = set()
    for start in graph:
        if color.get(start):
            continue
        stack = [(start, iter(graph.get(start, [])))]
        path = [start]
        color[start] = 1
        while stack:
            node, it = stack[-1]
            nxt = next(it, None)
            if nxt is None:
                color[node] = 2
                stack.pop()
                path.pop()
                continue
            if nxt not in graph:
                continue
            if color.get(nxt) == 1:
                cyc = path[path.index(nxt):] + [nxt]
                key = frozenset(cyc)
                if key not in reported:
                    reported.add(key)
                    errors.append("dependency cycle: %s" % " -> ".join(cyc))
            elif not color.get(nxt):
                color[nxt] = 1
                stack.append((nxt, iter(graph.get(nxt, []))))
                path.append(nxt)
    return errors, warnings


# --------------------------------------------------------------------------
# Cross-document checks (what per-file schema validation cannot see)
# --------------------------------------------------------------------------

def _rows(value: Any) -> List[Tuple[int, Dict[str, Any]]]:
    """(index, object) pairs of a list-of-objects value; anything else yields nothing."""
    return [(i, v) for i, v in enumerate(value) if isinstance(v, dict)] if isinstance(value, list) else []


def _duplicate_ids(rows: List[Tuple[int, Dict[str, Any]]], key: str) -> List[Tuple[str, int, int]]:
    """[(value, first index, repeat index)] for string `key` values that occur more than once."""
    seen: Dict[str, int] = {}
    dups: List[Tuple[str, int, int]] = []
    for i, row in rows:
        v = row.get(key)
        if isinstance(v, str) and v:
            if v in seen:
                dups.append((v, seen[v], i))
            else:
                seen[v] = i
    return dups


def _id_set(rows: List[Tuple[int, Dict[str, Any]]], key: str = "id") -> set:
    return {row[key] for _, row in rows if isinstance(row.get(key), str)}


def cross_check(root: Any) -> List[Tuple[str, str]]:
    """Consistency between the documents of a project, which per-file schema validation cannot see.

    Errors: duplicate ids (features; manifest assets; event names within a taxonomy; mechanics in the contract
    and among mechanic cards; currencies), features that depend on unknown features, level-spec `mechanic_refs`
    that are not contract mechanic ids, and evidence paths of gates marked "pass" that do not exist on disk.
    Warnings: economy-model offers with no matching contract `monetization.iap` id, contract currencies the
    economy model has no resource for, manifest asset files missing on disk (rejected assets are kept for
    lineage only, so they are not checked) and documents that could not be read.

    Returns [(severity, message)] with severity "error" or "warning", errors first. Documents that do not
    exist yet are skipped silently; so are reference checks that need the contract when it is missing.
    Feature messages end in the same wording `lint_features` uses after its "<id>: " prefix, so callers can
    drop the ones already reported. Never raises.
    """
    root_p = _abspath(root)
    issues: List[Tuple[str, str]] = []

    def add(severity: str, message: str) -> None:
        issues.append((severity, message))

    def read(path: Path, label: str) -> Any:
        if not path.is_file():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            add("warning", "%s is not readable JSON (%s); its cross-document checks were skipped" % (label, exc))
            return None

    g = gs_dir(root_p)

    def rel(path: Path) -> str:
        """Path relative to .gamestudio/ (every document shares that prefix), else relative to the project root."""
        try:
            return path.relative_to(g).as_posix()
        except ValueError:
            return rel_to_root(path, root_p)

    def under_root(ref: Any) -> Optional[Path]:
        if not isinstance(ref, str) or not ref.strip():
            return None
        p = Path(ref.strip()).expanduser()
        return p if p.is_absolute() else root_p / p

    def json_files(target: Optional[Path]) -> List[Path]:
        try:
            if target is None:
                return []
            if target.is_file():
                return [target]
            return sorted(p for p in target.rglob("*.json") if p.is_file()) if target.is_dir() else []
        except OSError:
            return []

    config = read(state_path(root_p, "config"), "config.json")
    contract = read(state_path(root_p, "contract"), "contract.json")
    features = read(state_path(root_p, "features"), "features.json")
    manifest = read(state_path(root_p, "manifest"), "assets/manifest.json")
    contract = contract if isinstance(contract, dict) else None

    def section(*keys: str) -> Any:
        cur: Any = contract
        for k in keys:
            cur = cur.get(k) if isinstance(cur, dict) else None
        return cur

    mechanics = _rows(section("mechanics"))
    currencies = _rows(section("economy", "currencies"))
    iap_ids = _id_set(_rows(section("monetization", "iap")))

    # -- features: unique ids, known dependencies, evidence of passing gates -----------------------------------
    try:
        rows = _rows(features.get("features") if isinstance(features, dict) else None)
        for fid, first, again in _duplicate_ids(rows, "id"):
            add("error", "features.json %s: duplicate id (also features[%d])" % (fid, first))
        known = _id_set(rows)
        for _, f in rows:
            fid = str(f.get("id", "?"))
            deps = f.get("depends_on")
            for dep in (deps if isinstance(deps, list) else []):
                if isinstance(dep, str) and dep not in known:
                    add("error", "features.json %s: depends on unknown feature %s" % (fid, dep))
            gates = f.get("gates") if isinstance(f.get("gates"), dict) else {}
            evidence = f.get("evidence") if isinstance(f.get("evidence"), dict) else {}
            for gate in GATES:
                if gates.get(gate) != "pass":
                    continue
                for raw in _as_path_list(evidence.get(gate)):
                    if isinstance(raw, str) and raw.strip() and not resolve_evidence(raw, root_p).exists():
                        add("error", "features.json %s: gate '%s' evidence not found on disk: %s" % (fid, gate, raw))
    except Exception as exc:  # a malformed shape must not hide the other checks
        add("warning", "features cross-check skipped: %s: %s" % (type(exc).__name__, exc))

    # -- asset manifest: unique ids, files on disk ---------------------------------------------------------------
    try:
        assets = _rows(manifest.get("assets") if isinstance(manifest, dict) else None)
        for aid, first, again in _duplicate_ids(assets, "id"):
            add("error", "assets/manifest.json assets[%d]: duplicate asset id '%s' (also assets[%d])" % (again, aid, first))
        cfg_paths = config.get("paths") if isinstance(config, dict) and isinstance(config.get("paths"), dict) else {}
        bases = [root_p]
        proj_dir = cfg_paths.get("project_root")
        if isinstance(proj_dir, str) and proj_dir.strip() not in ("", ".", "./"):
            bases.append(root_p / proj_dir.strip())
        for _, a in assets:
            ref = a.get("path")
            if a.get("status") == "rejected" or not isinstance(ref, str) or not ref.strip():
                continue
            p = Path(ref).expanduser()
            if not (p.exists() if p.is_absolute() else any((b / p).exists() for b in bases)):
                add("warning", "assets/manifest.json asset '%s': file not found: %s" % (a.get("id", "?"), ref))
    except Exception as exc:
        add("warning", "manifest cross-check skipped: %s: %s" % (type(exc).__name__, exc))

    # -- contract: unique mechanic and currency ids ---------------------------------------------------------------
    for mid, first, again in _duplicate_ids(mechanics, "id"):
        add("error", "contract.json mechanics[%d]: duplicate mechanic id '%s' (also mechanics[%d])" % (again, mid, first))
    for cid, first, again in _duplicate_ids(currencies, "id"):
        add("error", "contract.json economy.currencies[%d]: duplicate currency id '%s' (also economy.currencies[%d])"
            % (again, cid, first))

    # -- mechanic cards (design/mechanics): unique ids ------------------------------------------------------------
    try:
        owner: Dict[str, Path] = {}
        for card_path in json_files(g / "design" / "mechanics"):
            card = read(card_path, rel(card_path))
            cid = card.get("id") if isinstance(card, dict) else None
            if isinstance(cid, str) and cid:
                if cid in owner:
                    add("error", "%s: mechanic card id '%s' is also used by %s" % (rel(card_path), cid, rel(owner[cid])))
                else:
                    owner[cid] = card_path
    except Exception as exc:
        add("warning", "mechanic card cross-check skipped: %s: %s" % (type(exc).__name__, exc))

    # -- event taxonomy: unique event names -----------------------------------------------------------------------
    try:
        taxonomies = json_files(under_root(section("analytics", "taxonomy_ref")))
        if not taxonomies:
            for cand in json_files(g / "analytics"):
                if _gs_schema_key(("analytics", cand.name), cand) == "event-taxonomy":
                    taxonomies.append(cand)
        for tpath in taxonomies:
            tdoc = read(tpath, rel(tpath))
            events = _rows(tdoc.get("events") if isinstance(tdoc, dict) else None)
            for name, first, again in _duplicate_ids(events, "name"):
                add("error", "%s events[%d]: duplicate event name '%s' (also events[%d])" % (rel(tpath), again, name, first))
    except Exception as exc:
        add("warning", "event taxonomy cross-check skipped: %s: %s" % (type(exc).__name__, exc))

    # -- level specs: mechanic_refs must be contract mechanics ----------------------------------------------------
    try:
        level_files: List[Path] = []
        for target in (g / "levels", under_root(section("content", "levels", "spec_ref"))):
            for lp in json_files(target):
                if lp not in level_files:
                    level_files.append(lp)
        mech_ids = _id_set(mechanics)
        specs = []
        for lp in level_files:
            doc = read(lp, rel(lp))
            if isinstance(doc, dict) and ("level_id" in doc or "mechanic_refs" in doc):
                specs.append((lp, doc))
        if specs and contract is None:
            add("warning", "contract.json is missing or unreadable: level mechanic_refs were not checked")
        elif contract is not None:
            for lp, doc in specs:
                refs = doc.get("mechanic_refs")
                for ref in (refs if isinstance(refs, list) else []):
                    if isinstance(ref, str) and ref not in mech_ids:
                        add("error", "%s level '%s': mechanic_refs names '%s', which is not a contract mechanic id%s" % (
                            rel(lp), doc.get("level_id", "?"), ref,
                            " (contract mechanics: %s)" % ", ".join(sorted(mech_ids)) if mech_ids else " (the contract lists no mechanics)"))
    except Exception as exc:
        add("warning", "level cross-check skipped: %s: %s" % (type(exc).__name__, exc))

    # -- economy model vs contract --------------------------------------------------------------------------------
    try:
        models = json_files(under_root(section("economy", "model_ref")))
        if not models:
            for cand in json_files(g / "economy"):
                data = _sniff(cand)
                if _schema_key_from_content(data) == "economy-model":
                    models.append(cand)
        if contract is not None:
            for mpath in models:
                model = read(mpath, rel(mpath))
                if not isinstance(model, dict):
                    continue
                for _, offer in _rows(model.get("offers")):
                    oid = offer.get("id")
                    if isinstance(oid, str) and oid not in iap_ids:
                        add("warning", "%s offer '%s': no matching contract monetization.iap id" % (rel(mpath), oid))
                resources = _id_set(_rows(model.get("resources")))
                for _, cur in currencies:
                    cid = cur.get("id")
                    if isinstance(cid, str) and cid not in resources:
                        add("warning", "%s: contract currency '%s' is not a resource of the economy model" % (rel(mpath), cid))
    except Exception as exc:
        add("warning", "economy cross-check skipped: %s: %s" % (type(exc).__name__, exc))

    issues.sort(key=lambda it: 0 if it[0] == "error" else 1)   # stable: errors first, discovery order kept
    return issues


# --------------------------------------------------------------------------
# Progress log and budget
# --------------------------------------------------------------------------

def append_progress(root: Any, text: str) -> str:
    """Append a dated entry to `.gamestudio/progress.md` and return the entry.

    Format: `- [YYYY-MM-DD HH:MM] first line`, continuation lines indented by
    two spaces.  Creates the file (with header) if needed.  Never rewrites.
    """
    path = state_path(root, "progress")
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [ln.rstrip() for ln in str(text).strip().splitlines()] or [""]
    entry = "- [%s] %s\n" % (now_stamp(), lines[0])
    for ln in lines[1:]:
        entry += "  %s\n" % ln
    prefix = ""
    if not path.exists():
        cfg = load_json(state_path(root, "config"), {}) or {}
        title = ((cfg.get("project") or {}).get("title") if isinstance(cfg, dict) else None) \
            or Path(str(root)).name
        prefix = progress_header(str(title))
    else:
        try:
            with open(str(path), "rb") as fh:
                fh.seek(0, os.SEEK_END)
                if fh.tell() > 0:
                    fh.seek(-1, os.SEEK_END)
                    if fh.read(1) != b"\n":
                        prefix = "\n"
        except OSError:
            pass
    with open(str(path), "a", encoding="utf-8", newline="\n") as fh:
        fh.write(prefix + entry)
    return entry.rstrip("\n")


def read_progress_entries(root: Any, n: int = 5) -> List[str]:
    """Last `n` progress entries (first line of each bullet), oldest first."""
    path = state_path(root, "progress")
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    lines = text.splitlines()
    bullets = [ln.strip() for ln in lines if re.match(r"^[-*]\s+\S", ln)]
    if not bullets:
        bullets = [ln.strip() for ln in lines
                   if ln.strip() and not ln.lstrip().startswith("#") and not ln.startswith("`")]
    return bullets[-n:] if n > 0 else []


def _num(v: Any, default: float = 0.0) -> float:
    try:
        if isinstance(v, bool):
            return default
        f = float(v)
        return f if math.isfinite(f) else default
    except (TypeError, ValueError):
        return default


def budget_summary(budget_doc: Any, config: Any = None) -> Dict[str, Any]:
    """Spend summary from budget.json (cap falls back to config.budgets.asset_usd_cap)."""
    b = budget_doc if isinstance(budget_doc, dict) else {}
    c = config if isinstance(config, dict) else {}
    cfg_b = c.get("budgets") if isinstance(c.get("budgets"), dict) else {}
    ledger = [e for e in (b.get("ledger") or []) if isinstance(e, dict)]
    ledger_sum = round(sum(_num(e.get("cost_usd")) for e in ledger), 4)
    cap = b.get("cap_usd")
    cap = _num(cap) if cap is not None else _num(cfg_b.get("asset_usd_cap"), DEFAULT_ASSET_USD_CAP)
    spent = _num(b.get("spent_usd"), ledger_sum) if "spent_usd" in b else ledger_sum
    by_provider: Dict[str, float] = {}
    by_tool: Dict[str, float] = {}
    for e in ledger:
        cost = _num(e.get("cost_usd"))
        by_provider[str(e.get("provider") or "unknown")] = round(
            by_provider.get(str(e.get("provider") or "unknown"), 0.0) + cost, 4)
        by_tool[str(e.get("tool") or "unknown")] = round(by_tool.get(str(e.get("tool") or "unknown"), 0.0) + cost, 4)
    warnings = []
    if budget_doc is None:
        warnings.append("budget.json missing; cap taken from config")
    if abs(spent - ledger_sum) > 0.01:
        warnings.append("spent_usd (%.2f) differs from ledger total (%.2f)" % (spent, ledger_sum))
    if cfg_b.get("asset_usd_cap") is not None and b.get("cap_usd") is not None \
            and abs(_num(cfg_b.get("asset_usd_cap")) - _num(b.get("cap_usd"))) > 0.005:
        warnings.append("budget.json cap_usd (%.2f) differs from config budgets.asset_usd_cap (%.2f)"
                        % (_num(b.get("cap_usd")), _num(cfg_b.get("asset_usd_cap"))))
    if cap > 0 and spent > cap + 1e-9:
        warnings.append("spend exceeds cap by $%.2f" % (spent - cap))
    return {
        "cap_usd": round(cap, 4),
        "spent_usd": round(spent, 4),
        "remaining_usd": round(max(cap - spent, 0.0), 4),
        "pct_used": round(100.0 * spent / cap, 1) if cap > 0 else None,
        "per_call_usd_cap": _num(cfg_b.get("per_call_usd_cap"), DEFAULT_PER_CALL_USD_CAP)
        if cfg_b.get("per_call_usd_cap") is not None else None,
        "ledger_entries": len(ledger),
        "ledger_total_usd": ledger_sum,
        "by_provider": by_provider,
        "by_tool": by_tool,
        "recent": ledger[-5:],
        "warnings": warnings,
    }


# --------------------------------------------------------------------------
# Schemas and validation (delegates to scripts/validate_json.py)
# --------------------------------------------------------------------------

# Schema key -> candidate file stems in scripts/schemas/ (first existing wins).
SCHEMA_CANDIDATES: Dict[str, Tuple[str, ...]] = {
    "config": ("config", "project-config", "gamestudio-config"),
    "contract": ("contract", "design-contract"),
    "features": ("features", "feature-list"),
    "budget": ("budget",),
    "manifest": ("manifest", "asset-manifest", "assets-manifest"),
    "concept": ("concept",),
    "deconstruction": ("deconstruction",),
    "economy-model": ("economy-model",),
    "level-spec": ("level-spec",),
    "event-taxonomy": ("event-taxonomy",),
    "mechanic-card": ("mechanic-card",),
    "playtest-report": ("playtest-report",),
    "perf-report": ("perf-report",),
}
# Canonical file name per key, used to ask validate_json.schema_path_for().
_CANONICAL_NAMES = {
    "config": "config.json", "contract": "contract.json", "features": "features.json",
    "budget": "budget.json", "manifest": "manifest.json",
}
_SKIP = "__skip__"
# "<name>.<suffix>.json" convention (mirrors validate_json.SUFFIXES) -> schema key.
_SUFFIX_KEYS = {
    "economy": "economy-model", "economy-model": "economy-model", "level": "level-spec",
    "level-spec": "level-spec", "taxonomy": "event-taxonomy", "event-taxonomy": "event-taxonomy",
    "mechanic": "mechanic-card", "mechanic-card": "mechanic-card", "deconstruction": "deconstruction",
    "concept": "concept", "playtest": "playtest-report", "playtest-report": "playtest-report",
    "perf": "perf-report", "perf-report": "perf-report", "design-contract": "contract",
    "asset-manifest": "manifest",
}
# validate_json canonical schema names -> our keys (for "$schema_name" declarations).
_DECLARED_KEYS = {"design-contract": "contract", "asset-manifest": "manifest"}


def _explicit_key(path: Path) -> Optional[str]:
    """Schema key from an explicit convention: `example.<schema>.json`, `<name>.<suffix>.json`
    or a top-level `"$schema_name"` field in an existing file.  None when none applies."""
    name = path.name.lower()
    parts = name[:-5].split(".") if name.endswith(".json") else []
    if len(parts) >= 2 and parts[0] == "example":       # example.<schema-name>.json (schema examples)
        key = _DECLARED_KEYS.get(parts[-1], parts[-1])
        if key in SCHEMA_CANDIDATES:
            return key
    if len(parts) >= 2 and parts[-1] in _SUFFIX_KEYS:
        return _SUFFIX_KEYS[parts[-1]]
    data = _sniff(path)
    if isinstance(data, dict) and isinstance(data.get("$schema_name"), str):
        declared = data["$schema_name"].strip()
        if declared.endswith(".schema.json"):
            declared = declared[: -len(".schema.json")]
        declared = _DECLARED_KEYS.get(declared, declared)
        if declared in SCHEMA_CANDIDATES:
            return declared
    return None

_validator_state: Dict[str, Any] = {"module": None, "error": None, "path": None}


def _load_validator(path: Optional[Path] = None) -> Any:
    """Import scripts/validate_json.py once. Returns the module or None (error kept)."""
    target = Path(path) if path else VALIDATOR_PATH
    if _validator_state["path"] == str(target):
        return _validator_state["module"]
    _validator_state.update({"module": None, "error": None, "path": str(target)})
    try:
        existing = sys.modules.get("validate_json")
        if existing is not None and getattr(existing, "__file__", None) \
                and _abspath(existing.__file__) == _abspath(target):
            mod = existing
        else:
            if not target.is_file():
                raise ImportError("%s not found" % target)
            if str(target.parent) not in sys.path:
                sys.path.insert(0, str(target.parent))
            sys.dont_write_bytecode = True  # do not litter the plugin tree with __pycache__
            spec = importlib.util.spec_from_file_location("validate_json", str(target))
            if spec is None or spec.loader is None:
                raise ImportError("cannot load %s" % target)
            mod = importlib.util.module_from_spec(spec)
            sys.modules["validate_json"] = mod
            try:
                spec.loader.exec_module(mod)  # type: ignore[union-attr]
            except BaseException:
                sys.modules.pop("validate_json", None)
                raise
        if not callable(getattr(mod, "validate", None)):
            raise ImportError("validate_json has no validate(instance, schema, base_dir)")
        _validator_state["module"] = mod
    except (Exception, SystemExit) as exc:  # a broken module must never break a hook: fail open
        _validator_state["error"] = "%s: %s" % (type(exc).__name__, exc)
    return _validator_state["module"]


def validator_available() -> Tuple[bool, Optional[str]]:
    """(available, error message) for scripts/validate_json.py."""
    mod = _load_validator()
    return mod is not None, _validator_state["error"]


def _find_schema(key: str, schemas_dir: Optional[Path] = None) -> Optional[Path]:
    sdir = Path(schemas_dir) if schemas_dir else SCHEMAS_DIR
    for stem in SCHEMA_CANDIDATES.get(key, (key,)):
        p = sdir / ("%s.schema.json" % stem)
        if p.is_file():
            return p
    if schemas_dir is None and key in _CANONICAL_NAMES:
        mod = _load_validator()
        fn = getattr(mod, "schema_path_for", None) if mod else None
        if callable(fn):
            try:
                r = fn(_CANONICAL_NAMES[key])
                if r and Path(str(r)).is_file():
                    return Path(str(r))
            except Exception:
                pass
    return None


def _sniff(path: Path) -> Any:
    """Parsed JSON of an existing small file, else None."""
    try:
        if path.is_file() and path.stat().st_size <= 8 * 1024 * 1024:
            return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, ValueError):
        pass
    return None


def _schema_key_from_content(data: Any) -> Optional[str]:
    if not isinstance(data, dict):
        return None
    keys = set(data)
    if {"game", "core_loop"} <= keys or {"game", "lessons"} <= keys:
        return "deconstruction"
    if "archetypes" in keys or ("nodes" in keys and "resources" in keys):
        return "economy-model"
    if "level_id" in keys:
        return "level-spec"
    if "frame_ms" in keys or ("fps" in keys and "device" in keys):
        return "perf-report"
    if "steps" in keys and "verdict" in keys and "mode" in keys:
        return "playtest-report"
    if "events" in keys and "naming" in keys:
        return "event-taxonomy"
    if "mobile_fit" in keys or ("dynamics" in keys and "aesthetics" in keys):
        return "mechanic-card"
    if "scores" in keys and "logline" in keys and "hook" in keys:
        return "concept"
    return None


_AUX_STEM_RE = re.compile(r"(index|manifest|pack|list|summary|report|result|sim|solve|tournament|"
                          r"ranking|leaderboard|output|scores)")


def _gs_schema_key(rel_parts: Tuple[str, ...], path: Path) -> Optional[str]:
    """Schema key for a file at `.gamestudio/<rel_parts...>`; _SKIP = deliberately none."""
    if not rel_parts:
        return None
    name = rel_parts[-1]
    stem = name[:-5].lower() if name.lower().endswith(".json") else name.lower()
    top = rel_parts[0]
    if len(rel_parts) == 1:
        return {"config.json": "config", "contract.json": "contract",
                "features.json": "features", "budget.json": "budget"}.get(name)
    if top == "assets":
        return "manifest" if (len(rel_parts) == 2 and name == "manifest.json") else _SKIP
    if top == "snapshots":
        return _SKIP
    if top in ("concepts", "levels"):
        # one document per file; tournament rankings, packs, indices and solver/sim output are not
        if _AUX_STEM_RE.search(stem):
            return _SKIP
        return "concept" if top == "concepts" else "level-spec"
    if top == "playtests":
        return _SKIP if re.search(r"(index|summary|list)", stem) else "playtest-report"
    data = _sniff(path)
    if top == "analytics":
        if "taxonomy" in stem or stem.startswith("events"):
            return "event-taxonomy"
        if data is not None:
            return "event-taxonomy" if _schema_key_from_content(data) == "event-taxonomy" else _SKIP
        return _SKIP
    if top == "economy":
        if data is not None:
            return "economy-model" if _schema_key_from_content(data) == "economy-model" else _SKIP
        return _SKIP if re.search(r"(sim|result|output|out|report|run|summary)", stem) else "economy-model"
    if top == "research":
        if data is not None:
            k = _schema_key_from_content(data)
            return k if k in ("deconstruction", "mechanic-card", "concept") else _SKIP
        if "decon" in stem or "deconstructions" in rel_parts:
            return "deconstruction"
        if "mechanic" in stem or "mechanics" in rel_parts:
            return "mechanic-card"
        return _SKIP
    if top in ("reports", "evidence"):
        if stem.startswith(("playthrough", "bots", "bot_", "playtest")):
            return "playtest-report"
        if stem.startswith("perf") or stem.endswith("perf") or "perf_report" in stem or "perf-report" in stem:
            return "perf-report"
        if data is not None:
            k = _schema_key_from_content(data)
            return k if k in ("playtest-report", "perf-report") else _SKIP
        return _SKIP
    return None


def schema_for(path: Any) -> Optional[Path]:
    """Schema file for a JSON document, or None.

    Explicit conventions win everywhere: `<name>.<suffix>.json` (e.g.
    `level_01.level.json`, `royal-match.deconstruction.json`, same suffixes as
    validate_json) or a top-level `"$schema_name"` field.  Otherwise, inside
    `.gamestudio/` the mapping follows BLUEPRINT section 5 (top-level state
    files, assets/manifest.json, concepts/, levels/, analytics/, playtests/ by
    directory; economy/, research/, reports/, evidence/ by file name and
    content; snapshots/ never).  Outside `.gamestudio/` nothing else maps, so
    an engine's own config.json or manifest.json is never schema-checked.
    Files ending in `.schema.json` never map.  Unresolved cases inside
    `.gamestudio/` are delegated to validate_json.schema_path_for().
    """
    p = Path(str(path))
    name = p.name
    if not name.lower().endswith(".json") or name.lower().endswith(".schema.json"):
        return None
    explicit = _explicit_key(p)
    if explicit:
        return _find_schema(explicit)
    parts = p.parts
    if GS_DIRNAME in parts:
        idx = len(parts) - 1 - list(reversed(parts)).index(GS_DIRNAME)
        rel = tuple(parts[idx + 1:])
        key = _gs_schema_key(rel, p)
        if key == _SKIP:
            return None
        if key:
            found = _find_schema(key)
            if found:
                return found
        mod = _load_validator()
        fn = getattr(mod, "schema_path_for", None) if mod else None
        if callable(fn):
            for arg in (str(p), name):
                try:
                    r = fn(arg)
                except Exception:
                    continue
                if r and Path(str(r)).is_file():
                    return Path(str(r))
        return None
    return None


def validate_file(path: Any) -> List[str]:
    """Validate a JSON file against its schema; returns error strings ([] = valid).

    Returns [] when the file has no schema.  Fails open - returns [] with a
    warning on stderr - when scripts/validate_json.py cannot be imported or
    crashes, so hooks never block on tooling problems.  Invalid JSON in a
    file that has a schema is reported as an error.
    """
    p = Path(str(path))
    schema_path = schema_for(p)
    if schema_path is None:
        return []
    mod = _load_validator()
    if mod is None:
        _warn("schema validation skipped - cannot import %s (%s)"
              % (VALIDATOR_PATH.name, _validator_state["error"]), once_key="validator-import")
        return []
    try:
        instance = json.loads(p.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return ["%s: file not found" % p.name]
    except UnicodeDecodeError as exc:
        return ["%s: not UTF-8 text (%s)" % (p.name, exc)]
    except ValueError as exc:
        return ["%s: invalid JSON: %s" % (p.name, exc)]
    except OSError as exc:
        _warn("cannot read %s: %s" % (p, exc))
        return []
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        _warn("schema %s unreadable (%s); validation skipped" % (schema_path.name, exc))
        return []
    try:
        errs = mod.validate(instance, schema, schema_path.parent)
    except Exception as exc:
        _warn("validate_json crashed on %s (%s: %s); validation skipped"
              % (p.name, type(exc).__name__, exc))
        return []
    return [str(e) for e in (errs or [])]


# --------------------------------------------------------------------------
# SessionStart summary
# --------------------------------------------------------------------------

FIVE_GATE_RULE = (
    "Five-gate rule: a feature counts as done only when each gate (static, unit, playthrough, "
    "visual, perf) is \"pass\" with evidence on disk or \"n/a\" with a gate note; passes/status "
    "change only through gs.py feature gate / feature pass, and hooks block hand edits that skip it."
)
FIVE_GATE_RULE_SHORT = (
    "Five-gate rule: done = static, unit, playthrough, visual, perf each \"pass\"+evidence or "
    "\"n/a\"+note (gs.py feature gate/pass)."
)


def _clip(text: str, n: int) -> str:
    text = str(text)
    if n <= 0:
        return ""
    if len(text) <= n:
        return text
    if n <= 3:
        return text[:n]
    return text[: n - 3].rstrip() + "..."


def _is_tbd(s: Any) -> bool:
    return not isinstance(s, str) or not s.strip() or s.strip().upper().startswith("TBD")


def summarize(root: Any, max_chars: int = 2500) -> str:
    """Compact, factual project summary for the SessionStart hook.

    Contains: identity line, phase/tier, feature counts, in-progress work,
    the next 3 ready features with priorities, features with failing gates
    (and done features that break the rule), budget, the last 3 progress
    entries and the five-gate rule.  Lines are dropped in reverse priority
    order so the result never exceeds `max_chars`.  Never raises.
    """
    try:
        max_chars = int(max_chars)
    except (TypeError, ValueError):
        max_chars = 2500
    if max_chars <= 0:
        return ""
    try:
        return _clip(_summarize(root, max_chars), max_chars)
    except Exception as exc:  # the SessionStart hook must never break
        return _clip("arcosian: project state could not be summarized (%s: %s)."
                     % (type(exc).__name__, exc), max_chars)


def _summarize(root: Any, max_chars: int) -> str:
    root_p = _abspath(root)
    if not gs_dir(root_p).is_dir():
        found = find_project_root(root_p)
        if found is None:
            return ("arcosian: no %s/ project state at %s (initialise with gs.py init or "
                    "/arcosian:new-game)." % (GS_DIRNAME, root_p))
        root_p = found
    st = load_state(root_p)
    cfg = st["config"] if isinstance(st["config"], dict) else {}
    con = st["contract"] if isinstance(st["contract"], dict) else {}
    meta = con.get("meta") if isinstance(con.get("meta"), dict) else {}
    feats = st["features"]
    proj = cfg.get("project") if isinstance(cfg.get("project"), dict) else {}

    title = meta.get("title") or proj.get("title") or root_p.name
    genre = meta.get("genre") if not _is_tbd(meta.get("genre")) else None
    engine = cfg.get("engine") or meta.get("engine") or "engine?"
    ev = cfg.get("engine_version")
    plats = cfg.get("platforms") or meta.get("platforms") or []
    orient = cfg.get("orientation") or meta.get("orientation")
    tier = cfg.get("tier") or ((con.get("scope") or {}).get("tier") if isinstance(con.get("scope"), dict) else None) \
        or "prototype"

    items: List[Tuple[int, str]] = []   # (priority: lower = kept first, text) in display order

    ident = ['arcosian project "%s"' % title]
    if genre:
        ident.append(str(genre))
    ident.append(("%s %s" % (engine, ev)).strip() if ev and ev != "unspecified" else str(engine))
    if isinstance(plats, list) and plats:
        ident.append("/".join(str(x) for x in plats))
    if orient:
        ident.append(str(orient))
    items.append((0, " | ".join(ident)))

    phase = "Phase: tier %s" % tier
    scope = con.get("scope") if isinstance(con.get("scope"), dict) else {}
    if scope:
        phase += "; scope must %d / should %d / won't %d" % (
            len(scope.get("must") or []), len(scope.get("should") or []), len(scope.get("wont") or []))
    if not _is_tbd(meta.get("logline")):
        phase += "; logline: %s" % _clip(str(meta.get("logline")), 160)
    elif con:
        phase += "; contract still has TBD fields"
    else:
        phase += "; no contract.json"
    items.append((7, phase))

    if feats is None:
        items.append((2, "Features: features.json missing or unreadable."))
    else:
        c = feature_counts(feats)
        items.append((2, "Features: %d total, %d done, %d passing, %d in progress, %d blocked, %d todo."
                      % (c["total"], c["done"], c["passing"], c["in_progress"], c["blocked"], c["todo"])))
        prog = [f for f in get_features(feats) if f.get("status") == "in_progress"]
        if prog:
            parts = ["%s %s (%s; open gates: %s)" % (f.get("id"), _clip(str(f.get("title", "")), 60),
                                                     f.get("priority", "P?"), ", ".join(open_gates(f)) or "none")
                     for f in prog[:3]]
            more = " (+%d more)" % (len(prog) - 3) if len(prog) > 3 else ""
            items.append((5, "In progress: " + "; ".join(parts) + more + "."))
        ready = ready_features(feats)
        if ready:
            items.append((3, "Next ready: " + "; ".join(
                "%s [%s] %s" % (f.get("id"), f.get("priority", "P?"), _clip(str(f.get("title", "")), 60))
                for f in ready[:3]) + "."))
        elif c["total"] == 0:
            items.append((3, "Next ready: no features defined yet (gs.py feature add)."))
        else:
            waiting = waiting_features(feats)
            if waiting:
                items.append((3, "Next ready: none; todo features wait on dependencies: " + "; ".join(
                    "%s needs %s" % (f.get("id"), ",".join(u)) for f, u in waiting[:3]) + "."))
            else:
                items.append((3, "Next ready: none (no todo features left)."))
        fails = failing_gates(feats)
        viol = dod_violations(feats, root_p)
        if fails or viol:
            txt = []
            if fails:
                txt.append("Failing gates: " + "; ".join("%s (%s)" % (fid, ", ".join(g)) for fid, g in fails[:6])
                           + (" (+%d more)" % (len(fails) - 6) if len(fails) > 6 else "") + ".")
            if viol:
                txt.append("Marked done/passing but failing the five-gate check: "
                           + ", ".join(fid for fid, _ in viol[:8]) + ".")
            items.append((4, " ".join(txt)))
        else:
            items.append((6, "Failing gates: none."))

    if st["budget"] is not None or cfg:
        b = budget_summary(st["budget"], cfg)
        btxt = "Asset budget: $%.2f spent of $%.2f cap ($%.2f left" % (
            b["spent_usd"], b["cap_usd"], b["remaining_usd"])
        if b["pct_used"] is not None:
            btxt += ", %.0f%%" % b["pct_used"]
        btxt += ")"
        if b["per_call_usd_cap"] is not None:
            btxt += "; per-call cap $%.2f" % b["per_call_usd_cap"]
        if b["warnings"]:
            btxt += "; " + _clip(b["warnings"][0], 90)
        items.append((6, btxt + "."))

    entries = read_progress_entries(root_p, 3)
    if entries:
        items.append((8, "Recent progress:"))
        for i, e in enumerate(entries):
            # newest entry is the most important one to keep
            items.append((8 + (len(entries) - i), _clip(e, 220)))

    items.append((1, FIVE_GATE_RULE if max_chars >= 1200 else FIVE_GATE_RULE_SHORT))
    items.append((12, 'Project root: %s. State CLI: python3 "%s" status | feature next | feature gate | '
                      'kb "query".' % (root_p, SCRIPTS_DIR / "gs.py")))

    # Select by priority within the budget, then emit in display order.
    order = sorted(range(len(items)), key=lambda i: (items[i][0], i))
    chosen: Dict[int, str] = {}
    used = 0
    for i in order:
        prio, text = items[i]
        cost = len(text) + (1 if chosen else 0)
        if used + cost <= max_chars:
            chosen[i] = text
            used += cost
        elif prio <= 1:
            sep = 1 if chosen else 0
            room = max_chars - used - sep
            if room > 20:
                chosen[i] = _clip(text, room)
                used += sep + len(chosen[i])
    # Drop a dangling "Recent progress:" header if none of its lines survived.
    keys = sorted(chosen)
    out_lines = []
    for idx, i in enumerate(keys):
        if chosen[i] == "Recent progress:" and not any(
                items[j][0] >= 9 and items[j][0] <= 11 for j in keys[idx + 1:]):
            continue
        out_lines.append(chosen[i])
    return "\n".join(out_lines)


# --------------------------------------------------------------------------
# Knowledge-base search over PLUGIN/skills/**/*.md
# --------------------------------------------------------------------------

_TOKEN_RE = re.compile(r"[a-z0-9]+")
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")
_STOPWORDS = frozenset(
    "a an and are as at be been but by can do does for from has have how i if in into is it its "
    "of on or our should so than that the their them then there these they this to too use used "
    "using was we what when where which who why will with you your vs via per not no".split())
_stem_cache: Dict[str, str] = {}


def _stem(tok: str) -> str:
    """Tiny suffix stripper applied symmetrically to queries and documents.

    Plural/-ing/-ed endings are removed, then a final "e" on words longer than
    four letters, so balance/balanced/balancing -> "balanc" and
    price/pricing -> "pric"; "-ies" becomes "y" (currencies -> currency).
    """
    s = _stem_cache.get(tok)
    if s is not None:
        return s
    t = tok
    if len(t) > 4 and t.endswith("ies"):
        t = t[:-3] + "y"
    elif len(t) > 5 and t.endswith("ing"):
        t = t[:-3]
    elif len(t) > 4 and t.endswith("ed") and not t.endswith("eed"):
        t = t[:-2]
    elif len(t) > 4 and t.endswith("es") and t[-3] in "sxz":
        t = t[:-2]
    elif len(t) > 3 and t.endswith("s") and not t.endswith(("ss", "us", "is")):
        t = t[:-1]
    if len(t) > 4 and t.endswith("e") and not t.endswith("ee"):
        t = t[:-1]
    _stem_cache[tok] = t
    return t


def query_terms(query: str) -> List[str]:
    """Distinct stemmed query terms, stopwords removed (kept if nothing else remains)."""
    raw = [t for t in _TOKEN_RE.findall(str(query).lower()) if len(t) > 1 or t.isdigit()]
    kept = [t for t in raw if t not in _STOPWORDS] or raw
    out: List[str] = []
    for t in kept:
        s = _stem(t)
        if s not in out:
            out.append(s)
    return out


def _split_sections(text: str) -> List[Dict[str, Any]]:
    """Split Markdown into sections at headings (ignoring '#' lines inside code fences).

    Each section: heading (breadcrumb of the last two heading levels),
    heading_line (1-based), lines [(lineno, text)] of the body.
    """
    lines = text.splitlines()
    sections: List[Dict[str, Any]] = []
    start = 0
    if lines and lines[0].strip() == "---":
        for j in range(1, min(len(lines), 200)):
            if lines[j].strip() == "---":
                sections.append({"heading": "frontmatter", "heading_line": 1,
                                 "lines": [(k + 1, lines[k]) for k in range(1, j)]})
                start = j + 1
                break
    stack: List[Tuple[int, str]] = []
    cur: Dict[str, Any] = {"heading": "(top)", "heading_line": start + 1, "lines": []}
    in_fence = False
    fence = ""
    for idx in range(start, len(lines)):
        line = lines[idx]
        s = line.lstrip()
        if s.startswith("```") or s.startswith("~~~"):
            mark = s[:3]
            if not in_fence:
                in_fence, fence = True, mark
            elif mark == fence:
                in_fence = False
            cur["lines"].append((idx + 1, line))
            continue
        m = None if in_fence else _HEADING_RE.match(line)
        if m:
            if cur["lines"] or cur["heading"] != "(top)":
                sections.append(cur)
            level = len(m.group(1))
            title = m.group(2).strip()
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, title))
            crumb = " > ".join(t for _, t in stack[-2:])
            cur = {"heading": crumb, "heading_line": idx + 1, "lines": []}
        else:
            cur["lines"].append((idx + 1, line))
    if cur["lines"] or cur["heading"] != "(top)":
        sections.append(cur)
    return sections


def _excerpt(lines: List[Tuple[int, str]], terms: List[str], width: int = 220) -> Tuple[int, List[str]]:
    """Best 3-line excerpt (non-empty, non-fence lines) around the line with most term hits."""
    body = [(n, ln.strip()) for n, ln in lines
            if ln.strip() and not ln.lstrip().startswith(("```", "~~~")) and ln.strip() != "---"]
    if not body:
        return (lines[0][0] if lines else 0), []
    best_i, best_score = 0, -1
    for i, (_, ln) in enumerate(body):
        low = ln.lower()
        sc = sum(1 for t in terms if t in low)
        if sc > best_score:
            best_i, best_score = i, sc
    lo = max(0, best_i - 1) if best_i > 0 else 0
    window = body[lo: lo + 3]
    return body[best_i][0], [_clip(ln, width) for _, ln in window]


def kb_search(query: str, skills_root: Any = None, skill: Optional[str] = None, limit: int = 8,
              per_file: int = 2) -> Dict[str, Any]:
    """Ranked full-text search over `<plugin>/skills/**/*.md`.

    Query terms are lower-cased, stopword-filtered and stemmed.  Each
    Markdown section (split at headings outside code fences) is scored:

        score = sum_t idf(t) * (bm25_tf(t) + 2.5*[t in own heading]
                                + 1*[t only in parent heading] + 1*[t in file path])
        score *= 0.25 + 0.75 * coverage        # share of query terms matched
        score *= 1 + 0.5*share of query bigrams in the heading
                 (else 1 + 0.25*share in the body); x1.5 for the whole
                 phrase; x1.1 for SKILL.md

    bm25_tf uses k1=1.2, b=0.5 (long, complete sections are often the best
    answer); idf is file-level BM25 idf.  A word counts
    as a term hit when its stem equals the term; a stem that merely starts
    with a term of >= 4 letters counts half.  Only regex matches of the term
    roots are examined (no full tokenisation) and files/sections without a
    root substring are skipped, so a few hundred files search in well under
    a second.  At most `per_file` sections per file are returned.

    Returns {query, terms, results:[{file, skill, heading, heading_line, line,
    score, excerpt, matched}], files_searched, elapsed_ms[, note]}.
    `file` is relative to the plugin root (the parent of skills/).
    """
    t0 = time.perf_counter()
    sroot = Path(str(skills_root)) if skills_root else PLUGIN_ROOT / "skills"
    base = sroot.parent
    terms = query_terms(query)
    res: Dict[str, Any] = {"query": query, "terms": terms, "results": [], "files_searched": 0,
                           "elapsed_ms": 0}
    if not terms:
        res["note"] = "empty query"
        return res
    if not sroot.is_dir():
        res["note"] = "skills directory not found: %s" % sroot
        return res
    files = sorted(sroot.rglob("*.md"))
    if skill:
        files = [f for f in files if f.relative_to(sroot).parts[0] == skill]
        if not files:
            avail = sorted({p.relative_to(sroot).parts[0] for p in sroot.rglob("*.md")
                            if len(p.relative_to(sroot).parts) > 1})
            res["note"] = "no skill named %r; available: %s" % (skill, ", ".join(avail))
            return res
    res["files_searched"] = len(files)
    n_files = len(files)
    # Root = longest prefix shared by every surface form of the term ("currency" -> "currenc").
    roots = {t: (t[:-1] if t.endswith("y") and len(t) > 3 else t) for t in terms}
    pats = {t: re.compile(r"(?<![a-z0-9])%s[a-z0-9]*" % re.escape(roots[t])) for t in terms}

    def tf_of(t: str, text_low: str) -> float:
        if roots[t] not in text_low:
            return 0.0
        exact = pref = 0
        for w in pats[t].findall(text_low):
            st = _stem(w)
            if st == t:
                exact += 1
            elif len(t) >= 4 and st.startswith(t):
                pref += 1
        return exact + 0.5 * pref

    raw_tokens = _TOKEN_RE.findall(str(query).lower())
    phrase = " ".join(raw_tokens)
    content_tokens = [t for t in raw_tokens if t not in _STOPWORDS] or raw_tokens
    bigrams = [content_tokens[i] + " " + content_tokens[i + 1] for i in range(len(content_tokens) - 1)]
    sections: List[Dict[str, Any]] = []
    df: Counter = Counter()
    for f in files:
        rel = f.relative_to(base).as_posix()
        rel_low = rel.lower()
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        low = text.lower()
        if not any(roots[t] in low or roots[t] in rel_low for t in terms):
            continue
        parts = f.relative_to(sroot).parts
        skill_name = parts[0] if len(parts) > 1 else ""
        path_words = " ".join(_TOKEN_RE.findall(rel_low[:-3] if rel_low.endswith(".md") else rel_low))
        file_hits = {t for t in terms if tf_of(t, path_words) > 0}
        seen: set = set()
        for si, sec in enumerate(_split_sections(text)):
            head_low = sec["heading"].lower()
            own_low = head_low.rsplit(" > ", 1)[-1]
            sec_low = head_low + "\n" + "\n".join(ln for _, ln in sec["lines"]).lower()
            if not any(roots[t] in sec_low for t in terms) and not (si == 0 and file_hits):
                continue
            tfs = {t: tf_of(t, sec_low) for t in terms}
            heads = {t for t in terms if tf_of(t, head_low) > 0}
            own = {t for t in heads if tf_of(t, own_low) > 0}
            seen.update(t for t, v in tfs.items() if v > 0)
            sections.append({
                "file": rel, "skill": skill_name, "heading": sec["heading"],
                "heading_line": sec["heading_line"], "lines": sec["lines"], "tfs": tfs, "heads": heads,
                "own": own,
                "file_hits": file_hits, "length": max(len(sec_low.split()), 1),
                "is_skill_md": f.name == "SKILL.md", "low": sec_low,
            })
        for t in seen:
            df[t] += 1
    if not sections:
        res["elapsed_ms"] = round((time.perf_counter() - t0) * 1000, 1)
        return res
    avglen = sum(s["length"] for s in sections) / float(len(sections))
    idf = {t: math.log(1.0 + (n_files - df.get(t, 0) + 0.5) / (df.get(t, 0) + 0.5)) for t in terms}
    k1, b = 1.2, 0.5
    scored = []
    for s in sections:
        score = 0.0
        matched = []
        norm = k1 * (1 - b + b * s["length"] / avglen)
        for t in terms:
            tf = s["tfs"][t]
            h = 2.5 if t in s["own"] else (1.0 if t in s["heads"] else 0.0)
            fh = 1.0 if t in s["file_hits"] else 0.0
            if tf <= 0 and h == 0 and fh == 0:
                continue
            matched.append(t)
            bm = (tf * (k1 + 1)) / (tf + norm) if tf > 0 else 0.0
            score += idf[t] * (bm + h + 1.0 * fh)
        if not matched:
            continue
        coverage = len(matched) / float(len(terms))
        score *= 0.25 + 0.75 * coverage
        if bigrams and len(matched) >= 2:
            head_norm = " ".join(_TOKEN_RE.findall(s["heading"].lower()))
            in_head = sum(1 for bg in bigrams if bg in head_norm)
            body_norm = " ".join(_TOKEN_RE.findall(s["low"]))
            if in_head:
                score *= 1.0 + 0.5 * in_head / len(bigrams)
            else:
                score *= 1.0 + 0.25 * sum(1 for bg in bigrams if bg in body_norm) / len(bigrams)
            if len(content_tokens) > 2 and coverage == 1.0 and phrase in body_norm:
                score *= 1.5
        if s["is_skill_md"]:
            score *= 1.1
        scored.append((score, s, matched))
    scored.sort(key=lambda x: (-x[0], x[1]["file"], x[1]["heading_line"]))
    per: Counter = Counter()
    results = []
    for score, s, matched in scored:
        if per[s["file"]] >= max(1, per_file):
            continue
        per[s["file"]] += 1
        line, ex = _excerpt(s["lines"], [roots[t] for t in matched])
        results.append({
            "file": s["file"], "skill": s["skill"], "heading": s["heading"],
            "heading_line": s["heading_line"], "line": line or s["heading_line"],
            "score": round(score, 3), "excerpt": "\n".join(ex), "matched": matched,
        })
        if len(results) >= max(1, int(limit)):
            break
    res["results"] = results
    res["elapsed_ms"] = round((time.perf_counter() - t0) * 1000, 1)
    return res


# --------------------------------------------------------------------------
# Self-test
# --------------------------------------------------------------------------

def _write_fake_skills(skills: Path, filler: int = 200) -> None:
    """A small fake skills tree for kb_search tests (+ filler files for speed)."""
    def w(rel: str, text: str) -> None:
        p = skills / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

    w("economy-design/SKILL.md",
      "---\nname: economy-design\ndescription: Virtual economy design. Use when balancing currencies.\n---\n\n"
      "# Economy design\n\n## What this skill gives you\n\n- Faucets and drains for every currency.\n\n"
      "## Reference library\n\n| file | contents |\n|---|---|\n| references/currency-architecture.md | currencies |\n")
    w("economy-design/references/currency-architecture.md",
      "# Currency architecture\n\nSummary paragraph about soft and hard currency.\n\n"
      "## Sinks and sources\n\nEvery currency needs sinks that remove it and sources that add it.\n"
      "Track the sink-to-source ratio per day; hoarding means sinks are too weak.\n"
      "A currency sink should feel like a reward, not a tax.\n\n"
      "## Exchange rates\n\nHard currency converts to soft at a fixed rate.\n")
    w("game-feel/SKILL.md",
      "---\nname: game-feel\ndescription: Juice and feedback.\n---\n\n# Game feel\n\n"
      "## Screen shake\n\nUse screen shake sparingly: 2-6 px amplitude, 80-150 ms, with decay.\n"
      "Screen shake must respect the reduce-motion setting.\n\n"
      "```bash\n# comment inside fence that is not a heading\necho shake\n```\n\n"
      "## Hit stop\n\nFreeze 40-80 ms on impact.\n")
    filler_text = ("## Section {i}\n\nGeneric production planning text about milestones, risk registers, "
                   "scope and vertical slices. Nothing about the searched terms.\n\n") * 12
    for i in range(filler):
        w("filler-%03d/references/notes-%03d.md" % (i % 40, i), "# Filler %d\n\n" % i + filler_text.format(i=i))


def _selftest() -> int:
    import copy

    failures: List[str] = []
    passed = [0]

    def check(cond: Any, msg: str) -> None:
        if cond:
            passed[0] += 1
        else:
            failures.append(msg)
            print("FAIL: %s" % msg)

    tmp = Path(tempfile.mkdtemp(prefix="gslib-selftest-"))
    global VALIDATOR_PATH
    saved_validator_path = VALIDATOR_PATH
    saved_schema_for = globals()["schema_for"]
    try:
        root = (tmp / "proj")
        root.mkdir()
        (root / "project.godot").write_text('config/features=PackedStringArray("4.7", "Mobile")\n',
                                            encoding="utf-8")
        r = init_project(root, "Selftest Game", None, "puzzle")
        g = gs_dir(_abspath(root))
        check(r["engine"] == "godot", "engine auto-detected from project.godot")
        for rel in ("config.json", "contract.json", "features.json", "budget.json",
                    "assets/manifest.json", "progress.md"):
            check((g / rel).is_file(), "init created %s" % rel)
        for sub in PROJECT_SUBDIRS:
            check((g / sub).is_dir(), "init created %s/" % sub)
        check(find_project_root(root / "src" / "deep" / "file.gd") == _abspath(root),
              "find_project_root from a not-yet-existing nested file")
        check(find_project_root(g / "features.json") == _abspath(root), "find_project_root from inside .gamestudio")
        check(find_project_root(tmp) is None, "find_project_root returns None outside a project")
        r2 = init_project(root, "Other", "godot")
        check(r2["created"] == [] and "config.json" in r2["skipped"], "second init without force overwrites nothing")
        r3 = init_project(root, "Selftest Game", "godot", "puzzle", force=True)
        check("config.json" in r3["overwritten"] and r3["backup_dir"] and
              (Path(r3["backup_dir"]) / "config.json").is_file(), "init --force backs up before overwrite")
        prog_text = (g / "progress.md").read_text(encoding="utf-8")
        check("Project initialized" in prog_text and "Re-initialized" in prog_text,
              "progress.md kept and appended on force")

        st = load_state(root)
        check(set(st) == {"config", "contract", "features", "manifest", "budget"}, "load_state keys")
        cfg = st["config"]
        check(cfg["engine"] == "godot" and cfg["engine_version"] == "4.7", "config engine/version")
        check(cfg["platforms"] == ["ios", "android"] and cfg["orientation"] == "portrait", "config platforms")
        check(cfg["budgets"] == {"asset_usd_cap": 50.0, "per_call_usd_cap": 5.0}, "config budgets")
        check(cfg["storefronts"] == ["US"] and cfg["tier"] == "prototype", "config storefronts/tier")
        check(cfg["licence_allowlist"] == DEFAULT_LICENCE_ALLOWLIST, "config licence allowlist")
        check(st["contract"]["meta"]["title"] == "Selftest Game" and st["contract"]["meta"]["genre"] == "puzzle",
              "contract meta")
        check(st["budget"]["cap_usd"] == 50.0 and st["manifest"]["assets"] == [], "budget/manifest skeletons")

        # ---- features, ordering ----
        doc = st["features"]
        f1 = new_feature("F001", "Core merge rule", "gameplay", priority="P1")
        f2 = new_feature("f2", "Merge VFX", "vfx", priority="P0", depends_on=["F001"])
        f3 = new_feature("F003", "Board input", "gameplay", priority="P0")
        f4 = new_feature("F004", "Settings screen", "ui", priority="P2")
        check(f2["id"] == "F002", "feature id normalised (f2 -> F002)")
        doc["features"] = [f1, f2, f3, f4]
        check(next_feature_id(doc) == "F005", "next_feature_id")
        nf = next_feature(doc)
        check(nf is not None and nf["id"] == "F003", "next_feature: ready P0 beats P1; blocked P0 skipped")
        check([f["id"] for f in ready_features(doc)] == ["F003", "F001", "F004"], "ready order P0,P1,P2")
        check([(f["id"], u) for f, u in waiting_features(doc)] == [("F002", ["F001"])], "waiting_features")
        try:
            new_feature("F9", "x", "nope")
            check(False, "invalid area rejected")
        except ValueError:
            check(True, "invalid area rejected")

        # ---- gates ----
        evd = g / "evidence" / "F003"
        evd.mkdir(parents=True)
        (evd / "static.log").write_text("0 errors\n", encoding="utf-8")
        w = set_gate(f3, "static", "pass", [".gamestudio/evidence/F003/static.log"], root=root)
        check(w == [] and f3["status"] == "in_progress", "gate pass with evidence; todo -> in_progress")
        w = set_gate(f3, "unit", "pass")
        check(len(w) == 1 and "without evidence" in w[0], "gate pass without evidence warns")
        try:
            set_gate(f3, "visual", "n/a")
            check(False, "n/a without note rejected")
        except ValueError:
            check(True, "n/a without note rejected")
        set_gate(f3, "visual", "n/a", note="input layer only; covered by F002 visuals")
        set_gate(f3, "perf", "fail", note="p95 22 ms on low tier")
        set_gate(f3, "playthrough", "pass", [".gamestudio/evidence/F003/missing.json"])
        ok, probs = check_feature_pass(f3, root)
        joined = "\n".join(probs)
        check(not ok and "'unit' is pass but has no evidence" in joined and "'perf' is fail" in joined
              and "not found on disk" in joined and len(probs) == 3, "check_feature_pass refuses: %s" % probs)
        ok2, _ = mark_pass(f3, root)
        check(not ok2 and f3["passes"] is False and f3["status"] != "done", "mark_pass refused leaves feature")
        (evd / "unit.xml").write_text('<?xml version="1.0"?>\n<testsuites tests="3" failures="1" errors="0">'
                                      '<testsuite name="t" tests="3" failures="1" errors="0"/></testsuites>\n',
                                      encoding="utf-8")
        (evd / "playthrough.json").write_text(json.dumps({"schema_version": "1.0", "verdict": "pass"}),
                                              encoding="utf-8")
        (evd / "perf.json").write_text(json.dumps({"schema_version": "1.0", "verdict": "fail"}), encoding="utf-8")
        set_gate(f3, "unit", "pass", [".gamestudio/evidence/F003/unit.xml"])
        set_gate(f3, "playthrough", "pass", [".gamestudio/evidence/F003/playthrough.json"])
        set_gate(f3, "perf", "pass", [".gamestudio/evidence/F003/perf.json"])
        ok, probs = check_feature_pass(f3, root)
        check(not ok and len(probs) == 2 and any("failing/erroring" in p for p in probs)
              and any("verdict" in p for p in probs), "contradicting evidence refused: %s" % probs)
        (evd / "unit.xml").write_text('<testsuites tests="3" failures="0" errors="0">'
                                      '<testsuite name="t" tests="3" failures="0" errors="0"/></testsuites>',
                                      encoding="utf-8")
        (evd / "perf.json").write_text(json.dumps({"schema_version": "1.0", "verdict": "pass"}), encoding="utf-8")
        ok, probs = mark_pass(f3, root)
        check(ok and f3["passes"] is True and f3["status"] == "done", "mark_pass accepted: %s" % probs)
        w = set_gate(f3, "perf", "fail", root=root)
        check(f3["passes"] is False and f3["status"] == "in_progress" and any("regression" in x for x in w),
              "regression demotes a passing feature")
        set_gate(f3, "perf", "pass", root=root)
        check(f3["evidence"]["perf"] == ".gamestudio/evidence/F003/perf.json", "evidence kept when not re-given")
        check(mark_pass(f3, root)[0], "re-pass after fixing regression")
        for gate in GATES:
            set_gate(f1, gate, "n/a", note="rules spec only; verified via F003")
        check(mark_pass(f1, root)[0], "all-n/a feature with notes passes")
        nf = next_feature(doc)
        check(nf is not None and nf["id"] == "F002", "next_feature after deps pass: F002 (P0) before F004 (P2)")
        c = feature_counts(doc)
        check(c == {"total": 4, "done": 2, "passing": 2, "in_progress": 0, "blocked": 0, "todo": 2},
              "feature_counts %s" % c)
        check(gate_code(f3) == "PPPnP" and open_gates(f2) == list(GATES), "gate_code/open_gates")
        save_json(g / "features.json", doc)
        check(load_json(g / "features.json")["features"][2]["passes"] is True, "save_json round trip")
        check((g / "features.json").read_text(encoding="utf-8").endswith("}\n"), "save_json trailing newline")
        errs, warns = lint_features(doc, root)
        check(errs == [], "lint clean on valid doc: %s" % errs)
        bad = copy.deepcopy(doc)
        bad["features"][0]["depends_on"] = ["F002"]           # F001 <-> F002 cycle
        bad["features"][3]["depends_on"] = ["F077"]           # unknown
        bad["features"].append(copy.deepcopy(bad["features"][3]))  # duplicate F004
        bad["features"][3]["passes"] = True                   # passing without gates
        errs, _ = lint_features(bad, root)
        ej = "\n".join(errs)
        check("cycle" in ej and "unknown feature F077" in ej and "duplicate id" in ej and "five-gate" in ej,
              "lint catches cycle/unknown/duplicate/rule: %s" % errs)
        check(len(dod_violations(bad, root)) >= 1 and failing_gates(doc) == [], "dod_violations / failing_gates")

        # ---- lock ----
        with state_lock(root):
            try:
                with state_lock(root, timeout=0.2):
                    check(False, "nested lock from another handle must time out")
            except TimeoutError:
                check(True, "lock is exclusive")
        with state_lock(root, timeout=0.2):
            check(True, "lock released after use")

        # ---- evidence normalisation ----
        n = normalize_evidence([str(evd / "static.log")], root)
        check(n[0]["stored"] == ".gamestudio/evidence/F003/static.log" and n[0]["exists"], "absolute -> relative")
        n = normalize_evidence(["/nonexistent-gs/x.log"], root)
        check(n[0]["stored"] == "/nonexistent-gs/x.log" and not n[0]["exists"], "outside path kept absolute")
        n = normalize_evidence(["static.log"], root, cwd=evd)
        check(n[0]["stored"] == ".gamestudio/evidence/F003/static.log", "relative to cwd resolved")

        # ---- progress ----
        e = append_progress(root, "Merged F003 board input.\nVerified on low tier.")
        ents = read_progress_entries(root, 2)
        check(e.startswith("- [") and ents[-1].endswith("Merged F003 board input."), "append/read progress")
        check("  Verified on low tier." in (g / "progress.md").read_text(encoding="utf-8"), "continuation lines")

        # ---- budget ----
        b = load_json(g / "budget.json")
        b["ledger"] = [
            {"ts": now_iso(), "tool": "image_generate", "provider": "gemini", "model": "m", "cost_usd": 1.25,
             "asset_ids": ["a1"], "note": ""},
            {"ts": now_iso(), "tool": "audio_sfx", "provider": "elevenlabs", "model": "m", "cost_usd": 0.5,
             "asset_ids": ["a2"], "note": ""},
        ]
        b["spent_usd"] = 1.75
        save_json(g / "budget.json", b)
        bs = budget_summary(load_json(g / "budget.json"), load_json(g / "config.json"))
        check(bs["spent_usd"] == 1.75 and bs["remaining_usd"] == 48.25 and bs["pct_used"] == 3.5
              and bs["by_provider"] == {"gemini": 1.25, "elevenlabs": 0.5} and not bs["warnings"],
              "budget_summary %s" % bs)

        # ---- cross_check ----
        xr = tmp / "xproj"
        xr.mkdir()
        init_project(xr, "Cross Check", "godot")
        xg = gs_dir(_abspath(xr))
        check(cross_check(xr) == [], "cross_check: a fresh skeleton is clean: %s" % cross_check(xr))
        check(cross_check(tmp / "nowhere-at-all") == [], "cross_check: no project, nothing to report, no crash")
        con = load_json(xg / "contract.json")
        con["mechanics"] = [{"id": "merge_two"}, {"id": "spawn_bag"}, {"id": "merge_two"}]
        con["economy"]["currencies"] = [{"id": "coins"}, {"id": "gems"}, {"id": "coins"}]
        con["monetization"]["iap"] = [{"id": "gems_s"}]
        save_json(xg / "contract.json", con)
        xa = new_feature("F001", "Core", "gameplay")
        xb = new_feature("F002", "Juice", "vfx", depends_on=["F001"])
        xb["depends_on"].append("F099")                                  # unknown dependency
        xd = copy.deepcopy(xa)                                           # duplicate id F001
        set_gate(xa, "static", "pass", [".gamestudio/evidence/F001/static.log"])   # file does not exist
        set_gate(xa, "unit", "pass", [".gamestudio/evidence/F001/unit.xml"])        # this one will exist
        set_gate(xa, "perf", "fail", note="not measured yet")            # a failing gate needs no evidence
        (xg / "evidence" / "F001").mkdir(parents=True)
        (xg / "evidence" / "F001" / "unit.xml").write_text("<testsuites/>", encoding="utf-8")
        save_json(xg / "features.json", {"schema_version": "1.0", "features": [xa, xb, xd]})
        (xr / "assets").mkdir()
        (xr / "assets" / "real.png").write_bytes(b"\x89PNG")
        (xr / "game" / "assets").mkdir(parents=True)
        (xr / "game" / "assets" / "in_project.png").write_bytes(b"\x89PNG")
        cfg_x = load_json(xg / "config.json")
        cfg_x["paths"]["project_root"] = "game"
        save_json(xg / "config.json", cfg_x)
        save_json(xg / "assets" / "manifest.json", {"schema_version": "1.0", "assets": [
            {"id": "a1", "path": "assets/a1.png", "status": "candidate"},         # missing -> warning
            {"id": "a1", "path": "assets/a1_other.png", "status": "candidate"},   # duplicate id, also missing
            {"id": "a2", "path": "assets/gone.png", "status": "rejected"},        # rejected: not checked
            {"id": "a3", "path": "assets/real.png", "status": "approved"},        # at the repository root
            {"id": "a4", "path": "assets/in_project.png", "status": "approved"}]})  # under paths.project_root
        save_json(xg / "analytics" / "events.taxonomy.json", {"schema_version": "1.0", "naming": "snake_case", "events": [
            {"name": "level_start"}, {"name": "level_end"}, {"name": "level_start"}]})
        save_json(xg / "levels" / "l1.level.json", {"schema_version": "1.0", "level_id": "l1",
                                                    "mechanic_refs": ["merge_two", "ghost"]})
        save_json(xg / "levels" / "pack_index.json", {"levels": ["l1"]})        # not a level spec: ignored
        (xg / "levels" / "broken.level.json").write_text("{nope", encoding="utf-8")
        save_json(xg / "economy" / "model.economy.json", {"schema_version": "1.0",
                                                          "resources": [{"id": "coins"}],
                                                          "offers": [{"id": "gems_s", "price_usd": 1},
                                                                     {"id": "mystery", "price_usd": 2}]})
        (xg / "design" / "mechanics").mkdir(parents=True)
        save_json(xg / "design" / "mechanics" / "a.mechanic.json", {"id": "spawn_bag"})
        save_json(xg / "design" / "mechanics" / "b.mechanic.json", {"id": "spawn_bag"})
        res = cross_check(xr)
        errs = [m for sev, m in res if sev == "error"]
        warns = [m for sev, m in res if sev == "warning"]
        ej, wj = "\n".join(errs), "\n".join(warns)
        check(all(sev in ("error", "warning") for sev, _ in res)
              and [sev for sev, _ in res] == ["error"] * len(errs) + ["warning"] * len(warns),
              "cross_check returns errors first: %s" % [sev for sev, _ in res])
        check("features.json F001: duplicate id (also features[0])" in ej, "cross: duplicate feature id: %s" % ej)
        check("features.json F002: depends on unknown feature F099" in ej and "F001" not in
              "".join(m for m in errs if "depends on" in m), "cross: unknown dependency only for F099")
        check("features.json F001: gate 'static' evidence not found on disk: .gamestudio/evidence/F001/static.log" in ej
              and "unit.xml" not in ej and "perf" not in ej, "cross: only the missing evidence of a passing gate: %s" % ej)
        check("contract.json mechanics[2]: duplicate mechanic id 'merge_two' (also mechanics[0])" in ej, "cross: duplicate mechanic")
        check("contract.json economy.currencies[2]: duplicate currency id 'coins' (also economy.currencies[0])" in ej,
              "cross: duplicate currency")
        check("assets/manifest.json assets[1]: duplicate asset id 'a1' (also assets[0])" in ej, "cross: duplicate asset id")
        check("analytics/events.taxonomy.json events[2]: duplicate event name 'level_start' (also events[0])" in ej,
              "cross: duplicate event name: %s" % ej)
        check("levels/l1.level.json level 'l1': mechanic_refs names 'ghost'" in ej
              and "merge_two'," not in "".join(m for m in errs if "mechanic_refs" in m), "cross: level mechanic ref")
        check("mechanic card id 'spawn_bag' is also used by" in ej, "cross: duplicate mechanic card id")
        check("asset 'a1': file not found: assets/a1.png" in wj and "'a2'" not in wj and "'a3'" not in wj
              and "'a4'" not in wj, "cross: manifest paths: only a1 (+ a1 repeat), rejected skipped, project_root honoured: %s" % wj)
        check("offer 'mystery': no matching contract monetization.iap id" in wj and "'gems_s'" not in wj,
              "cross: offer without iap id: %s" % wj)
        check("contract currency 'gems' is not a resource of the economy model" in wj and "'coins'" not in wj,
              "cross: currency without resource: %s" % wj)
        check("broken.level.json is not readable JSON" in wj, "cross: unreadable document is a warning, not a crash")
        check(not any("pack_index" in m for _, m in res), "cross: aux level files are ignored")
        # no contract: reference checks that need it are skipped, with one warning about the levels
        (xg / "contract.json").unlink()
        res2 = cross_check(xr)
        check(("warning", "contract.json is missing or unreadable: level mechanic_refs were not checked") in res2
              and not any("ghost" in m for _, m in res2) and not any("offer" in m for _, m in res2),
              "cross: missing contract skips reference checks: %s" % res2)

        # ---- schema mapping ----
        dummy = tmp / "nofile.json"
        check(_gs_schema_key(("features.json",), dummy) == "features", "map features.json")
        check(_gs_schema_key(("assets", "manifest.json"), dummy) == "manifest", "map manifest")
        check(_gs_schema_key(("levels", "l001.json"), dummy) == "level-spec", "map levels/")
        check(_gs_schema_key(("concepts", "c1.json"), dummy) == "concept", "map concepts/")
        check(_gs_schema_key(("evidence", "F001", "playthrough.json"), dummy) == "playtest-report",
              "map evidence playthrough")
        check(_gs_schema_key(("evidence", "F001", "perf.json"), dummy) == "perf-report", "map evidence perf")
        check(_gs_schema_key(("snapshots", "x.json"), dummy) == _SKIP, "skip snapshots")
        check(_gs_schema_key(("economy", "sim_results.json"), dummy) == _SKIP, "skip economy sim output")
        check(_gs_schema_key(("economy", "model.json"), dummy) == "economy-model", "map economy model")
        check(_gs_schema_key(("concepts", "tournament-ranking.json"), dummy) == _SKIP, "skip concept rankings")
        check(_gs_schema_key(("levels", "pack_index.json"), dummy) == _SKIP, "skip level pack index")
        check(_gs_schema_key(("analytics", "events.taxonomy.json"), dummy) == "event-taxonomy", "map taxonomy")
        check(_gs_schema_key(("analytics", "ab_results.json"), dummy) == _SKIP, "skip analytics exports")
        check(schema_for(tmp / "x.schema.json") is None and schema_for(tmp / "package.json") is None,
              "no schema outside .gamestudio / for schema files")
        lvl = tmp / "research" / "royal.deconstruction.json"
        check(_explicit_key(lvl) == "deconstruction", "explicit suffix convention")
        check(_explicit_key(tmp / "example.config.json") == "config"
              and _explicit_key(tmp / "example.design-contract.json") == "contract", "example.<schema>.json")
        decl = tmp / "declared.json"
        decl.write_text('{"$schema_name": "design-contract"}', encoding="utf-8")
        check(_explicit_key(decl) == "contract", "$schema_name declaration")
        if (SCHEMAS_DIR / "design-contract.schema.json").is_file():
            check(schema_for(g / "contract.json") == SCHEMAS_DIR / "design-contract.schema.json",
                  "contract.json -> design-contract schema (real schemas)")
        if (SCHEMAS_DIR / "asset-manifest.schema.json").is_file():
            check(schema_for(g / "assets" / "manifest.json") == SCHEMAS_DIR / "asset-manifest.schema.json",
                  "manifest.json -> asset-manifest schema (real schemas)")
        check(schema_for(tmp / "web" / "manifest.json") is None and schema_for(tmp / "app.config.json") is None,
              "engine/web config files outside .gamestudio never map")
        sdir = tmp / "schemas"
        sdir.mkdir()
        (sdir / "level-spec.schema.json").write_text("{}", encoding="utf-8")
        check(_find_schema("level-spec", sdir) == sdir / "level-spec.schema.json", "_find_schema candidates")
        check(_find_schema("contract", sdir) is None, "_find_schema missing -> None")

        # ---- validate_file: fail open + delegation ----
        fake_schema = sdir / "features.schema.json"
        fake_schema.write_text('{"type": "object"}', encoding="utf-8")
        globals()["schema_for"] = lambda p: fake_schema
        VALIDATOR_PATH = tmp / "missing" / "validate_json.py"
        _validator_state["path"] = None
        saved_mod = sys.modules.pop("validate_json", None)
        check(validate_file(g / "features.json") == [], "validate_file fails open without validator")
        fake = tmp / "fakeval" / "validate_json.py"
        fake.parent.mkdir()
        fake.write_text(
            "def validate(instance, schema, base_dir):\n"
            "    return ['$.bad: not allowed'] if isinstance(instance, dict) and 'bad' in instance else []\n"
            "def schema_path_for(filename):\n    return None\n", encoding="utf-8")
        VALIDATOR_PATH = fake
        _validator_state["path"] = None
        good_f = g / "reports" / "good.json"
        good_f.write_text('{"ok": 1}', encoding="utf-8")
        bad_f = g / "reports" / "bad.json"
        bad_f.write_text('{"bad": 1}', encoding="utf-8")
        broken = g / "reports" / "broken.json"
        broken.write_text('{"x": ', encoding="utf-8")
        check(validate_file(good_f) == [], "validate_file valid -> []")
        check(validate_file(bad_f) == ["$.bad: not allowed"], "validate_file delegates errors")
        check(len(validate_file(broken)) == 1 and "invalid JSON" in validate_file(broken)[0],
              "validate_file reports invalid JSON")
        sys.modules.pop("validate_json", None)
        if saved_mod is not None:
            sys.modules["validate_json"] = saved_mod
        globals()["schema_for"] = saved_schema_for
        VALIDATOR_PATH = saved_validator_path
        _validator_state["path"] = None
        for p in (good_f, bad_f, broken):
            p.unlink()

        # Integration (soft): real validator + real schemas against fresh skeletons.
        avail, _err = validator_available()
        if avail:
            fresh = tmp / "fresh"
            fresh.mkdir()
            init_project(fresh, "Fresh", "unity")
            for rel in ("config.json", "contract.json", "features.json", "budget.json", "assets/manifest.json"):
                sp = schema_for(gs_dir(fresh) / rel)
                if sp is None:
                    print("NOTE: no schema yet for %s (skipped)" % rel)
                    continue
                errs = validate_file(gs_dir(fresh) / rel)
                check(not errs, "skeleton %s validates against %s: %s" % (rel, sp.name, errs[:5]))
        else:
            print("NOTE: validate_json.py not importable yet; skeleton/schema integration check skipped")

        # ---- kb search ----
        skills = tmp / "plugin" / "skills"
        _write_fake_skills(skills, filler=200)
        res = kb_search("currency sinks", skills_root=skills, limit=5)
        top = res["results"][0] if res["results"] else {}
        check(top.get("file") == "skills/economy-design/references/currency-architecture.md"
              and top.get("heading", "").endswith("Sinks and sources"), "kb top hit: %s" % top)
        check(top.get("excerpt") and len(top["excerpt"].splitlines()) <= 3 and top.get("skill") == "economy-design",
              "kb excerpt <= 3 lines + skill")
        check(res["files_searched"] == 203, "kb searched all files (%s)" % res["files_searched"])
        check(res["elapsed_ms"] < 3000, "kb fast on 200+ files (%.0f ms)" % res["elapsed_ms"])
        res = kb_search("screen shake", skills_root=skills, skill="game-feel")
        check(res["results"] and res["results"][0]["heading"].endswith("Screen shake"), "kb --skill filter")
        res = kb_search("comment inside fence", skills_root=skills)
        check(all("comment inside fence" not in r["heading"] for r in res["results"]),
              "kb ignores '#' lines in code fences as headings")
        res = kb_search("currency", skills_root=skills, skill="nope")
        check(res["results"] == [] and "available" in res.get("note", ""), "kb unknown skill note")
        check(kb_search("the and of", skills_root=skills)["terms"] == ["the", "and", "of"],
              "stopword-only query keeps terms")
        check(query_terms("Currencies sinks") == ["currency", "sink"], "query stemming")

        # ---- summarize ----
        s = summarize(root)
        check(len(s) <= 2500 and "Selftest Game" in s and "Five-gate rule" in s and "F002" in s
              and "Asset budget" in s and "Recent progress" in s, "summarize content:\n%s" % s)
        for n_chars in (1200, 400, 150, 60, 10, 1, 0):
            check(len(summarize(root, n_chars)) <= n_chars, "summarize <= %d chars" % n_chars)
        check("Five-gate" in summarize(root, 400), "rule survives tight budget")
        check("no .gamestudio" in summarize(tmp / "elsewhere"), "summarize outside project")
        (g / "features.json").write_text("{broken", encoding="utf-8")
        s2 = summarize(root)
        check("Selftest Game" in s2 and len(s2) <= 2500, "summarize survives corrupt features.json")
        try:
            load_json(g / "features.json", strict=True)
            check(False, "load_json strict raises on corrupt JSON")
        except ValueError:
            check(True, "load_json strict raises on corrupt JSON")
        check(load_json(g / "features.json", {"d": 1}) == {"d": 1}, "load_json default on corrupt JSON")
    except Exception as exc:  # pragma: no cover - report unexpected crashes as failures
        import traceback
        traceback.print_exc()
        failures.append("unexpected exception: %r" % exc)
    finally:
        globals()["schema_for"] = saved_schema_for
        VALIDATOR_PATH = saved_validator_path
        _validator_state["path"] = None
        shutil.rmtree(str(tmp), ignore_errors=True)
    if failures:
        print("gslib selftest: %d passed, %d FAILED" % (passed[0], len(failures)))
        return 1
    print("gslib selftest: OK (%d checks)" % passed[0])
    return 0


def main(argv: Optional[List[str]] = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(prog="gslib.py", description="arcosian shared library utilities.")
    ap.add_argument("--selftest", action="store_true", help="run the built-in self-test")
    ap.add_argument("--summarize", metavar="ROOT", nargs="?", const=".",
                    help="print the SessionStart summary for a project (default: cwd)")
    ap.add_argument("--max-chars", type=int, default=2500)
    ap.add_argument("--validate", metavar="PATH", nargs="+", help="validate JSON files against their schemas")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if args.summarize is not None:
        text = summarize(args.summarize, args.max_chars)
        print(json.dumps({"summary": text}) if args.json else text)
        return 0
    if args.validate:
        report = {p: validate_file(p) for p in args.validate}
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            for p, errs in report.items():
                print(("OK    %s" % p) if not errs else ("FAIL  %s\n" % p + "\n".join("      - " + e for e in errs)))
        return 1 if any(report.values()) else 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows pipes default to the ANSI code page; Claude Code reads UTF-8
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
