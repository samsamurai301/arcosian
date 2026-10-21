#!/usr/bin/env python3
"""validate_json.py - stdlib-only validator for the arcosian ontology.

Validates JSON documents against the JSON Schema (draft 2020-12) subset used by
the schemas in ``scripts/schemas/``. Every error carries a JSON pointer to the
offending value, e.g. ``/features/3/gates/static: "passed" is not one of ...``.

Supported keywords
    $ref (``#/$defs/...``, ``#``, and relative file refs such as
    ``common.schema.json#/$defs/loop``; refs inside a referenced file resolve
    against that file), $defs, type (incl. arrays of types; integer accepts
    1.0 but never booleans), enum, const, minimum, maximum, exclusiveMinimum,
    exclusiveMaximum, multipleOf, minLength, maxLength (code points), pattern,
    items, prefixItems, contains, minContains, maxContains, minItems, maxItems,
    uniqueItems, properties, patternProperties, additionalProperties (bool or
    schema), propertyNames, required, minProperties, maxProperties,
    dependentRequired, dependentSchemas, allOf, anyOf, oneOf, not,
    if / then / else.
    Annotations (title, description, default, examples, format, $comment,
    deprecated, readOnly, writeOnly, x-*) are accepted and ignored.
    Not supported: $id-based resolution, $anchor, $dynamicRef,
    unevaluatedProperties / unevaluatedItems, remote (http) refs.

CLI
    validate_json.py --schema S --instance I [--json]
    validate_json.py --auto PATH [PATH ...] [--json]   # PATH may be a directory
    validate_json.py --lint [SCHEMA ...] [--json]       # schema authoring lint
    validate_json.py --list                             # filename -> schema rules
    validate_json.py --bundle SCHEMA [--out PATH]       # self-contained schema (local refs only)
    validate_json.py --selftest

Exit codes: 0 = valid, 1 = validation failed, 2 = usage / input error.

Importable API
    validate(instance, schema, base_dir=None) -> list[str]
    validate_detailed(instance, schema, base_dir=None) -> list[tuple[str, str]]
    schema_path_for(filename) -> Path | None
    infer_schema(path, instance=None) -> Path | None
    validate_file(path, schema_path=None) -> list[str]
    lint_schema(schema_path) -> list[str]
    bundle_schema(schema_path) -> dict
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union
from urllib.parse import unquote

SCRIPT_DIR = Path(__file__).resolve().parent
SCHEMA_DIR = SCRIPT_DIR / "schemas"
EXAMPLES_DIR = SCHEMA_DIR / "examples"

# Canonical schema names: <name>.schema.json in SCHEMA_DIR. One per document type
# (BLUEPRINT section 5). common.schema.json holds shared $defs and is not a document.
SCHEMA_NAMES: Tuple[str, ...] = (
    "config",
    "design-contract",
    "features",
    "asset-manifest",
    "budget",
    "economy-model",
    "level-spec",
    "event-taxonomy",
    "mechanic-card",
    "deconstruction",
    "concept",
    "playtest-report",
    "perf-report",
)
SHARED_SCHEMAS: Tuple[str, ...] = ("common",)

# Exact file names (lower-case) -> schema name.
EXACT_FILENAMES: Dict[str, str] = {
    "config.json": "config",
    "contract.json": "design-contract",
    "design-contract.json": "design-contract",
    "features.json": "features",
    "manifest.json": "asset-manifest",
    "asset-manifest.json": "asset-manifest",
    "budget.json": "budget",
    # gate evidence written by playtest runners and perf tools (BLUEPRINT sections 6 and 13)
    "playthrough.json": "playtest-report",
    "bots.json": "playtest-report",
    "perf.json": "perf-report",
}

# "<anything>.<suffix>.json" (or exactly "<suffix>.json") -> schema name.
SUFFIXES: Dict[str, str] = {
    "economy": "economy-model",
    "economy-model": "economy-model",
    "level": "level-spec",
    "level-spec": "level-spec",
    "taxonomy": "event-taxonomy",
    "event-taxonomy": "event-taxonomy",
    "mechanic": "mechanic-card",
    "mechanic-card": "mechanic-card",
    "deconstruction": "deconstruction",
    "concept": "concept",
    "playtest": "playtest-report",
    "playtest-report": "playtest-report",
    "perf": "perf-report",
    "perf-report": "perf-report",
    "design-contract": "design-contract",
    "asset-manifest": "asset-manifest",
}

ErrorT = Tuple[str, str]  # (json pointer, message)

_MAX_DEPTH = 400
_MAX_REPR = 80


# --------------------------------------------------------------------------- helpers


def _jtype(value: Any) -> str:
    """JSON type name of a Python value produced by json.load."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _is_type(value: Any, name: str) -> bool:
    if name == "null":
        return value is None
    if name == "boolean":
        return isinstance(value, bool)
    if name == "integer":
        if isinstance(value, bool):
            return False
        if isinstance(value, int):
            return True
        return isinstance(value, float) and math.isfinite(value) and value.is_integer()
    if name == "number":
        return _is_number(value)
    if name == "string":
        return isinstance(value, str)
    if name == "array":
        return isinstance(value, list)
    if name == "object":
        return isinstance(value, dict)
    return False


def _json_equal(a: Any, b: Any) -> bool:
    """Equality with JSON semantics: 1 == 1.0, but true != 1, and deep for containers."""
    if isinstance(a, bool) or isinstance(b, bool):
        return isinstance(a, bool) and isinstance(b, bool) and a == b
    if _is_number(a) and _is_number(b):
        return a == b
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(_json_equal(a[k], b[k]) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(_json_equal(x, y) for x, y in zip(a, b))
    return type(a) is type(b) and a == b


def _canonical(value: Any) -> str:
    """Canonical string for uniqueness checks (1 and 1.0 collapse, key order ignored)."""

    def norm(v: Any) -> Any:
        if isinstance(v, float) and math.isfinite(v) and v.is_integer():
            return int(v)
        if isinstance(v, dict):
            return {k: norm(x) for k, x in v.items()}
        if isinstance(v, list):
            return [norm(x) for x in v]
        return v

    return json.dumps(norm(value), sort_keys=True, ensure_ascii=False)


def _short(value: Any) -> str:
    try:
        text = json.dumps(value, ensure_ascii=False)
    except (TypeError, ValueError):
        text = repr(value)
    if len(text) > _MAX_REPR:
        text = text[: _MAX_REPR - 3] + "..."
    return text


def _esc(token: Union[str, int]) -> str:
    return str(token).replace("~", "~0").replace("/", "~1")


def _child(path: str, token: Union[str, int]) -> str:
    return path + "/" + _esc(token)


def _fmt_path(path: str) -> str:
    return path if path else "/"


def format_errors(errors: Iterable[ErrorT]) -> List[str]:
    return ["%s: %s" % (_fmt_path(p), m) for p, m in errors]


class SchemaError(Exception):
    """Raised for unusable schemas (unparseable files, unresolvable refs at load time)."""


def _pointer_get(doc: Any, fragment: str) -> Any:
    """Resolve a JSON pointer fragment ('' or '/a/b') inside doc."""
    fragment = unquote(fragment)
    if fragment == "":
        return doc
    if not fragment.startswith("/"):
        raise SchemaError("unsupported fragment %r (only JSON pointers like '#/$defs/x' are supported)" % fragment)
    cur = doc
    for raw in fragment[1:].split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(cur, dict):
            if token not in cur:
                raise SchemaError("pointer token %r not found" % token)
            cur = cur[token]
        elif isinstance(cur, list):
            try:
                cur = cur[int(token)]
            except (ValueError, IndexError):
                raise SchemaError("pointer token %r is not a valid array index" % token)
        else:
            raise SchemaError("pointer token %r descends into a non-container" % token)
    return cur


def load_json_file(path: Union[str, Path]) -> Tuple[Any, List[str]]:
    """Load JSON strictly. Returns (data, problems). Problems include duplicate keys
    and non-standard constants (NaN, Infinity). On a parse error data is None."""
    problems: List[str] = []

    def pairs_hook(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        for k, v in pairs:
            if k in out:
                problems.append("duplicate key %r in one object (the last value silently wins)" % k)
            out[k] = v
        return out

    def bad_constant(name: str) -> Any:
        raise ValueError("non-standard JSON constant %s" % name)

    p = Path(path)
    try:
        text = p.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        return None, ["file is not UTF-8: %s" % exc]
    try:
        data = json.loads(text, object_pairs_hook=pairs_hook, parse_constant=bad_constant)
    except ValueError as exc:
        return None, ["invalid JSON: %s" % exc]
    return data, problems


# --------------------------------------------------------------------------- validator

_ANNOTATIONS = {
    "$schema", "$id", "$comment", "$defs", "definitions", "title", "description", "default",
    "examples", "deprecated", "readOnly", "writeOnly", "format", "contentMediaType",
    "contentEncoding", "contentSchema",
}
_APPLIED = {
    "$ref", "type", "enum", "const", "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum",
    "multipleOf", "minLength", "maxLength", "pattern", "items", "prefixItems", "contains",
    "minContains", "maxContains", "minItems", "maxItems", "uniqueItems", "properties",
    "patternProperties", "additionalProperties", "propertyNames", "required", "minProperties",
    "maxProperties", "dependentRequired", "dependentSchemas", "allOf", "anyOf", "oneOf", "not",
    "if", "then", "else",
}
_UNSUPPORTED = {
    "$anchor", "$dynamicRef", "$dynamicAnchor", "$recursiveRef", "$recursiveAnchor",
    "unevaluatedProperties", "unevaluatedItems", "additionalItems", "dependencies", "$vocabulary",
}
KNOWN_KEYWORDS = _ANNOTATIONS | _APPLIED | _UNSUPPORTED


class Validator:
    """Reusable validator; caches loaded schema files and compiled patterns."""

    def __init__(self) -> None:
        self._files: Dict[str, Any] = {}
        self._patterns: Dict[str, Any] = {}

    # ---- loading
    def load_schema(self, path: Union[str, Path]) -> Any:
        key = str(Path(path).resolve())
        if key not in self._files:
            data, problems = load_json_file(key) if Path(key).is_file() else (None, ["file not found"])
            if data is None:
                raise SchemaError("cannot load schema %s: %s" % (key, "; ".join(problems)))
            self._files[key] = data
        return self._files[key]

    def _resolve(self, ref: str, root: Any, base: Path) -> Tuple[Any, Any, Path]:
        if ref.startswith("#"):
            return _pointer_get(root, ref[1:]), root, base
        file_part, _, frag = ref.partition("#")
        if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", file_part):
            raise SchemaError("remote/absolute URI refs are not supported: %r" % ref)
        target_path = (base / unquote(file_part)).resolve()
        doc = self.load_schema(target_path)
        return _pointer_get(doc, frag), doc, target_path.parent

    def _regex(self, pattern: str) -> Any:
        rx = self._patterns.get(pattern)
        if rx is None:
            # re.ASCII keeps \d, \w, \b close to ECMA-262 semantics used by JSON Schema.
            rx = re.compile(pattern, re.ASCII)
            self._patterns[pattern] = rx
        return rx

    # ---- public
    def validate(self, instance: Any, schema: Any, base_dir: Union[str, Path, None] = None) -> List[ErrorT]:
        if isinstance(schema, (str, Path)):
            schema_path = Path(schema)
            root = self.load_schema(schema_path)
            base = schema_path.resolve().parent
        else:
            root = schema
            base = Path(base_dir).resolve() if base_dir is not None else SCHEMA_DIR
        return self._v(instance, root, "", root, base, 0)

    # ---- core
    def _v(self, inst: Any, schema: Any, path: str, root: Any, base: Path, depth: int) -> List[ErrorT]:
        if depth > _MAX_DEPTH:
            return [(path, "maximum schema depth exceeded (recursive $ref without progress?)")]
        if schema is True or schema == {}:
            return []
        if schema is False:
            return [(path, "no value is allowed here (schema is false)")]
        if not isinstance(schema, dict):
            return [(path, "invalid schema node of type %s" % _jtype(schema))]

        errors: List[ErrorT] = []

        ref = schema.get("$ref")
        if isinstance(ref, str):
            try:
                target, new_root, new_base = self._resolve(ref, root, base)
            except SchemaError as exc:
                errors.append((path, "cannot resolve $ref %r: %s" % (ref, exc)))
            else:
                errors.extend(self._v(inst, target, path, new_root, new_base, depth + 1))

        types = schema.get("type")
        if types is not None:
            tlist = types if isinstance(types, list) else [types]
            if not any(_is_type(inst, t) for t in tlist):
                shown = " or ".join(str(t) for t in tlist)
                errors.append((path, "expected %s, got %s %s" % (shown, _jtype(inst), _short(inst))))
                return errors  # every other keyword would only add noise

        if "enum" in schema and isinstance(schema["enum"], list):
            if not any(_json_equal(inst, e) for e in schema["enum"]):
                errors.append((path, "%s is not one of %s" % (_short(inst), _short(schema["enum"]))))
        if "const" in schema and not _json_equal(inst, schema["const"]):
            errors.append((path, "must equal %s, got %s" % (_short(schema["const"]), _short(inst))))

        if _is_number(inst):
            errors.extend(self._numeric(inst, schema, path))
        elif isinstance(inst, str):
            errors.extend(self._string(inst, schema, path))
        elif isinstance(inst, list):
            errors.extend(self._array(inst, schema, path, root, base, depth))
        elif isinstance(inst, dict):
            errors.extend(self._object(inst, schema, path, root, base, depth))

        errors.extend(self._combinators(inst, schema, path, root, base, depth))
        return errors

    def _numeric(self, x: Any, s: Dict[str, Any], path: str) -> List[ErrorT]:
        errs: List[ErrorT] = []
        mn, mx = s.get("minimum"), s.get("maximum")
        emn, emx = s.get("exclusiveMinimum"), s.get("exclusiveMaximum")
        if _is_number(mn) and x < mn:
            errs.append((path, "%s is less than the minimum %s" % (_short(x), _short(mn))))
        if _is_number(mx) and x > mx:
            errs.append((path, "%s is greater than the maximum %s" % (_short(x), _short(mx))))
        if _is_number(emn) and x <= emn:
            errs.append((path, "%s must be greater than %s (exclusiveMinimum)" % (_short(x), _short(emn))))
        if _is_number(emx) and x >= emx:
            errs.append((path, "%s must be less than %s (exclusiveMaximum)" % (_short(x), _short(emx))))
        mult = s.get("multipleOf")
        if _is_number(mult) and mult > 0:
            q = x / mult
            if not (math.isfinite(q) and abs(q - round(q)) < 1e-9):
                errs.append((path, "%s is not a multiple of %s" % (_short(x), _short(mult))))
        return errs

    def _string(self, text: str, s: Dict[str, Any], path: str) -> List[ErrorT]:
        errs: List[ErrorT] = []
        n = len(text)  # Python str length counts code points, as JSON Schema requires
        if isinstance(s.get("minLength"), int) and n < s["minLength"]:
            errs.append((path, "string of length %d is shorter than minLength %d" % (n, s["minLength"])))
        if isinstance(s.get("maxLength"), int) and n > s["maxLength"]:
            errs.append((path, "string of length %d is longer than maxLength %d" % (n, s["maxLength"])))
        pat = s.get("pattern")
        if isinstance(pat, str):
            try:
                if not self._regex(pat).search(text):
                    errs.append((path, "%s does not match pattern %s" % (_short(text), _short(pat))))
            except re.error as exc:
                errs.append((path, "schema has an invalid pattern %r: %s" % (pat, exc)))
        return errs

    def _array(self, arr: List[Any], s: Dict[str, Any], path: str, root: Any, base: Path, depth: int) -> List[ErrorT]:
        errs: List[ErrorT] = []
        n = len(arr)
        if isinstance(s.get("minItems"), int) and n < s["minItems"]:
            errs.append((path, "array has %d items; at least %d required (minItems)" % (n, s["minItems"])))
        if isinstance(s.get("maxItems"), int) and n > s["maxItems"]:
            errs.append((path, "array has %d items; at most %d allowed (maxItems)" % (n, s["maxItems"])))
        if s.get("uniqueItems") is True:
            seen: Dict[str, int] = {}
            for i, item in enumerate(arr):
                key = _canonical(item)
                if key in seen:
                    errs.append((_child(path, i), "duplicate of item %d (uniqueItems)" % seen[key]))
                else:
                    seen[key] = i
        prefix = s.get("prefixItems")
        items = s.get("items")
        if isinstance(items, list) and prefix is None:  # draft-07 tuple form, accepted leniently
            prefix, items = items, None
        start = 0
        if isinstance(prefix, list):
            for i, sub in enumerate(prefix[:n]):
                errs.extend(self._v(arr[i], sub, _child(path, i), root, base, depth + 1))
            start = len(prefix)
        if items is not None and not isinstance(items, list):
            for i in range(start, n):
                errs.extend(self._v(arr[i], items, _child(path, i), root, base, depth + 1))
        if "contains" in s:
            hits = sum(1 for item in arr if not self._v(item, s["contains"], path, root, base, depth + 1))
            lo = s.get("minContains", 1)
            hi = s.get("maxContains")
            if isinstance(lo, int) and hits < lo:
                errs.append((path, "array must contain at least %d matching item(s) (contains); found %d" % (lo, hits)))
            if isinstance(hi, int) and hits > hi:
                errs.append((path, "array must contain at most %d matching item(s) (maxContains); found %d" % (hi, hits)))
        return errs

    def _object(self, obj: Dict[str, Any], s: Dict[str, Any], path: str, root: Any, base: Path, depth: int) -> List[ErrorT]:
        errs: List[ErrorT] = []
        n = len(obj)
        if isinstance(s.get("minProperties"), int) and n < s["minProperties"]:
            errs.append((path, "object has %d properties; at least %d required" % (n, s["minProperties"])))
        if isinstance(s.get("maxProperties"), int) and n > s["maxProperties"]:
            errs.append((path, "object has %d properties; at most %d allowed" % (n, s["maxProperties"])))
        for key in s.get("required", []) or []:
            if isinstance(key, str) and key not in obj:
                errs.append((path, "missing required property %r" % key))
        dep_req = s.get("dependentRequired")
        if isinstance(dep_req, dict):
            for key, needed in dep_req.items():
                if key in obj:
                    for other in needed:
                        if other not in obj:
                            errs.append((path, "property %r requires property %r (dependentRequired)" % (key, other)))
        props = s.get("properties") if isinstance(s.get("properties"), dict) else {}
        pprops = s.get("patternProperties") if isinstance(s.get("patternProperties"), dict) else {}
        addl = s.get("additionalProperties", True)
        pnames = s.get("propertyNames")
        for key, value in obj.items():
            cpath = _child(path, key)
            if pnames is not None:
                for _p, msg in self._v(key, pnames, cpath, root, base, depth + 1):
                    errs.append((cpath, "property name %r is invalid: %s" % (key, msg)))
            matched = False
            if key in props:
                matched = True
                errs.extend(self._v(value, props[key], cpath, root, base, depth + 1))
            for pat, sub in pprops.items():
                try:
                    hit = self._regex(pat).search(key) is not None
                except re.error as exc:
                    errs.append((path, "schema has an invalid patternProperties regex %r: %s" % (pat, exc)))
                    continue
                if hit:
                    matched = True
                    errs.extend(self._v(value, sub, cpath, root, base, depth + 1))
            if not matched:
                if addl is False:
                    allowed = ", ".join(sorted(props)) or "(none)"
                    errs.append((cpath, "property %r is not allowed here (allowed: %s)" % (key, allowed)))
                elif isinstance(addl, dict):
                    errs.extend(self._v(value, addl, cpath, root, base, depth + 1))
        dep_s = s.get("dependentSchemas")
        if isinstance(dep_s, dict):
            for key, sub in dep_s.items():
                if key in obj:
                    errs.extend(self._v(obj, sub, path, root, base, depth + 1))
        return errs

    def _closest(self, branch_errors: List[List[ErrorT]], path: str) -> int:
        """Pick the failing branch most likely intended: avoid branches that rejected
        the value's type outright, then prefer the fewest errors."""

        def wrong_type(errs: List[ErrorT]) -> bool:
            return any(p == path and m.startswith("expected ") for p, m in errs)

        order = sorted(range(len(branch_errors)), key=lambda i: (wrong_type(branch_errors[i]), len(branch_errors[i])))
        return order[0]

    def _combinators(self, inst: Any, s: Dict[str, Any], path: str, root: Any, base: Path, depth: int) -> List[ErrorT]:
        errs: List[ErrorT] = []
        all_of = s.get("allOf")
        if isinstance(all_of, list):
            for sub in all_of:
                errs.extend(self._v(inst, sub, path, root, base, depth + 1))
        any_of = s.get("anyOf")
        if isinstance(any_of, list) and any_of:
            results = [self._v(inst, sub, path, root, base, depth + 1) for sub in any_of]
            if all(results):
                k = self._closest(results, path)
                errs.append((path, "does not match any of the %d allowed alternatives (anyOf); closest is #%d:" % (len(any_of), k)))
                errs.extend(results[k])
        one_of = s.get("oneOf")
        if isinstance(one_of, list) and one_of:
            results = [self._v(inst, sub, path, root, base, depth + 1) for sub in one_of]
            ok = [i for i, r in enumerate(results) if not r]
            if not ok:
                k = self._closest(results, path)
                errs.append((path, "does not match any of the %d alternatives (oneOf); closest is #%d:" % (len(one_of), k)))
                errs.extend(results[k])
            elif len(ok) > 1:
                errs.append((path, "matches %d alternatives %s; exactly one is required (oneOf)" % (len(ok), ok)))
        if "not" in s:
            if not self._v(inst, s["not"], path, root, base, depth + 1):
                errs.append((path, "must not match the schema under 'not'%s" % _rule_note(s["not"])))
        if "if" in s and ("then" in s or "else" in s):
            cond_ok = not self._v(inst, s["if"], path, root, base, depth + 1)
            branch = s.get("then") if cond_ok else s.get("else")
            if branch is not None:
                sub = self._v(inst, branch, path, root, base, depth + 1)
                note = _rule_note(s)
                errs.extend((p, m + note) for p, m in sub)
        return errs


_RULE_BLOCK_KEYS = {"if", "then", "else", "not", "description", "$comment", "title"}


def _rule_note(schema: Any) -> str:
    """Explanation appended to errors raised by a pure rule block (a schema made only of
    if/then/else or not plus a description), e.g. the five-gate rules in features."""
    if isinstance(schema, dict):
        text = schema.get("$comment")
        if not text and set(schema) <= _RULE_BLOCK_KEYS:
            text = schema.get("description")
        if isinstance(text, str) and text:
            return " [rule: %s]" % text
    return ""


# --------------------------------------------------------------------------- public API

_DEFAULT = Validator()


def validate_detailed(instance: Any, schema: Any, base_dir: Union[str, Path, None] = None) -> List[ErrorT]:
    """Validate and return (json_pointer, message) tuples. schema may be a dict or a path."""
    try:
        return _DEFAULT.validate(instance, schema, base_dir)
    except SchemaError as exc:
        return [("", "schema error: %s" % exc)]


def validate(instance: Any, schema: Any, base_dir: Union[str, Path, None] = None) -> List[str]:
    """Validate instance against schema (dict or path). Returns "pointer: message" strings;
    an empty list means valid. base_dir resolves relative file refs when schema is a dict
    (defaults to the shipped schemas directory)."""
    return format_errors(validate_detailed(instance, schema, base_dir))


def _schema_file(name: str) -> Optional[Path]:
    p = SCHEMA_DIR / ("%s.schema.json" % name)
    return p if p.is_file() else None


def schema_name_for(filename: Union[str, Path]) -> Optional[str]:
    """Infer the canonical schema name from a file name (no file access)."""
    name = Path(str(filename)).name.lower()
    if not name.endswith(".json"):
        return None
    if name in EXACT_FILENAMES:
        return EXACT_FILENAMES[name]
    stem = name[: -len(".json")]
    parts = stem.split(".")
    last = parts[-1]
    if len(parts) >= 2 and parts[0] == "example" and last in SCHEMA_NAMES:
        return last
    if last in SUFFIXES:
        return SUFFIXES[last]
    return None


def schema_path_for(filename: Union[str, Path]) -> Optional[Path]:
    """Map a document file name to its schema path, or None when the name is not conventional.

    config.json, contract.json, features.json, manifest.json, budget.json,
    playthrough.json / bots.json (playtest-report), perf.json (perf-report),
    *.economy.json, *.level.json, *.taxonomy.json, *.mechanic.json,
    *.deconstruction.json, *.concept.json, *.playtest.json, *.perf.json,
    and example.<schema-name>.json."""
    name = schema_name_for(filename)
    return _schema_file(name) if name else None


def _declared_name(instance: Any) -> Optional[str]:
    if isinstance(instance, dict):
        declared = instance.get("$schema_name")
        if isinstance(declared, str):
            declared = declared.strip()
            if declared.endswith(".schema.json"):
                declared = declared[: -len(".schema.json")]
            if declared in SCHEMA_NAMES:
                return declared
    return None


def infer_schema(path: Union[str, Path], instance: Any = None) -> Optional[Path]:
    """File-name rules first (same answer as schema_path_for), then a top-level
    "$schema_name" field in the instance (loaded from path when not given)."""
    by_name = schema_path_for(path)
    if by_name is not None:
        return by_name
    if instance is None and Path(path).is_file():
        instance, _ = load_json_file(path)
    declared = _declared_name(instance)
    return _schema_file(declared) if declared else None


def validate_file(path: Union[str, Path], schema_path: Union[str, Path, None] = None) -> List[str]:
    """Validate one file. Returns error strings; [] when valid. If no schema applies
    (and none is given), returns [] (nothing to check)."""
    p = Path(path)
    if not p.is_file():
        return ["/: file not found: %s" % p]
    data, problems = load_json_file(p)
    if data is None:
        return ["/: %s" % m for m in problems]
    schema = Path(schema_path) if schema_path else infer_schema(p, data)
    if schema is None:
        return []
    return ["/: %s" % m for m in problems] + validate(data, schema)


# --------------------------------------------------------------------------- schema lint

_SUBSCHEMA_MAPS = ("properties", "patternProperties", "$defs", "definitions", "dependentSchemas")
_SUBSCHEMA_SINGLE = ("items", "contains", "propertyNames", "additionalProperties", "not", "if", "then", "else")
_SUBSCHEMA_LISTS = ("allOf", "anyOf", "oneOf", "prefixItems")
_CONDITION_KEYS = {"if", "then", "else", "not", "contains"}


def lint_schema(schema_path: Union[str, Path], require_descriptions: bool = True) -> List[str]:
    """Authoring lint: unknown/unsupported keywords, unresolvable $refs, bad regexes,
    required names missing from properties, and (for document parts) properties
    without a description. Returns human-readable issues; [] means clean."""
    issues: List[str] = []
    path = Path(schema_path)
    v = Validator()
    try:
        root = v.load_schema(path)
    except SchemaError as exc:
        return [str(exc)]
    base = path.resolve().parent

    def walk(node: Any, where: str, in_condition: bool) -> None:
        if isinstance(node, bool):
            return
        if not isinstance(node, dict):
            issues.append("%s: schema node must be an object or boolean" % _fmt_path(where))
            return
        for key in node:
            if key.startswith("x-"):
                continue
            if key in _UNSUPPORTED:
                issues.append("%s: keyword %r is not supported by validate_json.py" % (_fmt_path(where), key))
            elif key not in KNOWN_KEYWORDS:
                issues.append("%s: unknown keyword %r (typo?)" % (_fmt_path(where), key))
        ref = node.get("$ref")
        if isinstance(ref, str):
            try:
                v._resolve(ref, root, base)
            except SchemaError as exc:
                issues.append("%s: unresolvable $ref %r (%s)" % (_fmt_path(where), ref, exc))
        for kw in ("pattern",):
            if isinstance(node.get(kw), str):
                try:
                    re.compile(node[kw], re.ASCII)
                except re.error as exc:
                    issues.append("%s: invalid pattern: %s" % (_fmt_path(where), exc))
        props = node.get("properties")
        if isinstance(node.get("required"), list) and isinstance(props, dict) and not in_condition:
            addl = node.get("additionalProperties", True)
            for req in node["required"]:
                if req not in props and addl is False:
                    issues.append("%s: required %r is impossible (not in properties, additionalProperties false)" % (_fmt_path(where), req))
        if isinstance(props, dict) and require_descriptions and not in_condition:
            for pname, psub in props.items():
                if isinstance(psub, dict) and not psub.get("description"):
                    issues.append("%s: property %r has no description" % (_fmt_path(_child(_child(where, "properties"), pname)), pname))
        for kw in _SUBSCHEMA_MAPS:
            sub = node.get(kw)
            if isinstance(sub, dict):
                for k, s in sub.items():
                    walk(s, _child(_child(where, kw), k), in_condition)
        for kw in _SUBSCHEMA_SINGLE:
            if kw in node and isinstance(node[kw], (dict, bool)):
                walk(node[kw], _child(where, kw), in_condition or kw in _CONDITION_KEYS)
        for kw in _SUBSCHEMA_LISTS:
            sub = node.get(kw)
            if isinstance(sub, list):
                for i, s in enumerate(sub):
                    walk(s, _child(_child(where, kw), i), in_condition)

    walk(root, "", False)
    return issues


# --------------------------------------------------------------------------- bundling

_FOREIGN_DROP = ("$defs", "definitions", "$schema", "$id", "title")


def bundle_schema(schema_path: Union[str, Path]) -> Dict[str, Any]:
    """Return a self-contained copy of a schema: every external ref
    ("common.schema.json#/$defs/loop") is copied into the root $defs under a
    namespaced key ("common__loop") and rewritten to a local "#/$defs/..." ref.
    Use it for validators that only follow local refs (ajv without a loader,
    minimal validators in other languages)."""
    path = Path(schema_path).resolve()
    v = Validator()
    original = v.load_schema(path)
    added: Dict[str, Any] = {}
    names: Dict[Tuple[str, str], str] = {}
    taken = set((original.get("$defs") or {}).keys()) if isinstance(original, dict) else set()

    def local_name(fpath: Path, frag: str) -> str:
        stem = fpath.name
        for suffix in (".schema.json", ".json"):
            if stem.endswith(suffix):
                stem = stem[: -len(suffix)]
                break
        tail = frag.strip("/")
        tail = tail[len("$defs/"):] if tail.startswith("$defs/") else tail
        tail = tail.replace("/$defs/", "__").replace("/", "__").replace("~1", "_").replace("~0", "_") or "root"
        base = "%s__%s" % (stem, tail)
        name, i = base, 2
        while name in taken:
            name, i = "%s_%d" % (base, i), i + 1
        taken.add(name)
        return name

    def resolve(ref: str, cur: Path) -> str:
        if ref.startswith("#"):
            if cur == path:
                return ref
            target, frag = cur, ref[1:]
        else:
            file_part, _, frag = ref.partition("#")
            target = (cur.parent / unquote(file_part)).resolve()
            if target == path:
                return "#" + frag
        key = (str(target), frag)
        if key not in names:
            names[key] = local_name(target, frag)
            node = _pointer_get(v.load_schema(target), frag)
            added[names[key]] = rewrite(node, target, foreign=True)
        return "#/$defs/" + names[key]

    def rewrite(node: Any, cur: Path, foreign: bool = False) -> Any:
        if isinstance(node, dict):
            out: Dict[str, Any] = {}
            for k, val in node.items():
                if foreign and k in _FOREIGN_DROP:
                    continue
                if k == "$ref" and isinstance(val, str):
                    out[k] = resolve(val, cur)
                elif k in ("properties", "patternProperties", "$defs", "definitions", "dependentSchemas") and isinstance(val, dict):
                    out[k] = {pk: rewrite(pv, cur) for pk, pv in val.items()}
                elif k in ("enum", "const", "default", "examples", "required", "dependentRequired", "type"):
                    out[k] = copy.deepcopy(val)
                else:
                    out[k] = rewrite(val, cur)
            return out
        if isinstance(node, list):
            return [rewrite(x, cur) for x in node]
        return copy.deepcopy(node)

    bundled = rewrite(original, path)
    if added:
        defs = bundled.setdefault("$defs", {})
        for k in sorted(added):
            defs[k] = added[k]
    return bundled


def _external_refs(node: Any) -> List[str]:
    found: List[str] = []
    if isinstance(node, dict):
        for k, val in node.items():
            if k == "$ref" and isinstance(val, str) and not val.startswith("#"):
                found.append(val)
            elif k not in ("enum", "const", "default", "examples"):
                found.extend(_external_refs(val))
    elif isinstance(node, list):
        for x in node:
            found.extend(_external_refs(x))
    return found


# --------------------------------------------------------------------------- self-test

_DELETE = object()


def _mutate(doc: Any, pointer: str, value: Any) -> Any:
    """Return a deep copy of doc with the value at pointer replaced (or deleted with _DELETE).
    Missing intermediate objects are created."""
    out = copy.deepcopy(doc)
    tokens = [t.replace("~1", "/").replace("~0", "~") for t in pointer.lstrip("/").split("/")]
    cur = out
    for tok in tokens[:-1]:
        if isinstance(cur, list):
            cur = cur[int(tok)]
        else:
            cur = cur.setdefault(tok, {})
    last = tokens[-1]
    if isinstance(cur, list):
        if value is _DELETE:
            del cur[int(last)]
        else:
            cur[int(last)] = value
    else:
        if value is _DELETE:
            cur.pop(last, None)
        else:
            cur[last] = value
    return out


def _keyword_cases() -> List[Tuple[str, Any, Any, Optional[str], Optional[str]]]:
    """(name, schema, instance, expected_error_path or None for valid, message substring).
    Relative file refs need files on disk and are tested separately in _selftest."""
    return [
        ("integer accepts int", {"type": "integer"}, 3, None, None),
        ("integer accepts 3.0", {"type": "integer"}, 3.0, None, None),
        ("integer rejects 3.5", {"type": "integer"}, 3.5, "", "expected integer"),
        ("integer rejects bool", {"type": "integer"}, True, "", "expected integer"),
        ("number rejects bool", {"type": "number"}, False, "", "expected number"),
        ("number accepts int", {"type": "number"}, 2, None, None),
        ("type array accepts null", {"type": ["string", "null"]}, None, None, None),
        ("type array rejects int", {"type": ["string", "null"]}, 1, "", "expected string or null"),
        ("enum numeric equality", {"enum": [1, "a", None]}, 1.0, None, None),
        ("enum bool is not 1", {"enum": [1, "a", None]}, True, "", "is not one of"),
        ("const deep equal", {"const": {"a": [1, 2]}}, {"a": [1, 2]}, None, None),
        ("const order matters in arrays", {"const": {"a": [1, 2]}}, {"a": [2, 1]}, "", "must equal"),
        ("exclusiveMinimum", {"exclusiveMinimum": 0, "maximum": 1}, 0, "", "exclusiveMinimum"),
        ("maximum inclusive", {"exclusiveMinimum": 0, "maximum": 1}, 1, None, None),
        ("maximum exceeded", {"exclusiveMinimum": 0, "maximum": 1}, 1.01, "", "greater than the maximum"),
        ("exclusiveMaximum", {"exclusiveMaximum": 10}, 10, "", "exclusiveMaximum"),
        ("minimum", {"minimum": 5}, 4.99, "", "less than the minimum"),
        ("multipleOf float", {"multipleOf": 0.01}, 4.99, None, None),
        ("multipleOf fail", {"multipleOf": 5}, 12, "", "multiple of"),
        ("minLength counts code points", {"minLength": 2}, "é", "", "shorter than minLength"),
        ("maxLength", {"maxLength": 3}, "abcd", "", "longer than maxLength"),
        ("pattern search", {"pattern": "^[a-z]+$"}, "ab1", "", "does not match pattern"),
        ("pattern ascii digits", {"pattern": "^\\d+$"}, "٣", "", "does not match pattern"),
        ("prefixItems+items ok", {"prefixItems": [{"type": "string"}, {"type": "integer"}], "items": {"type": "boolean"}}, ["a", 1, True], None, None),
        ("prefixItems position", {"prefixItems": [{"type": "string"}, {"type": "integer"}]}, ["a", "b"], "/1", "expected integer"),
        ("items after prefix", {"prefixItems": [{"type": "string"}], "items": {"type": "boolean"}}, ["a", "x"], "/1", "expected boolean"),
        ("minItems", {"minItems": 2}, [1], "", "at least 2"),
        ("maxItems", {"maxItems": 1}, [1, 2], "", "at most 1"),
        ("uniqueItems 1 == 1.0", {"uniqueItems": True}, [1, 1.0], "/1", "uniqueItems"),
        ("uniqueItems objects key order", {"uniqueItems": True}, [{"a": 1, "b": 2}, {"b": 2, "a": 1}], "/1", "uniqueItems"),
        ("contains", {"contains": {"const": 3}}, [1, 2], "", "contains"),
        ("required at parent path", {"required": ["a", "b"]}, {"a": 1}, "", "missing required property 'b'"),
        ("properties child path", {"properties": {"a": {"type": "integer"}}}, {"a": "1"}, "/a", "expected integer"),
        ("additionalProperties false child path", {"properties": {"x": {}}, "additionalProperties": False}, {"x": 1, "y": 2}, "/y", "not allowed"),
        ("additionalProperties schema", {"properties": {"x": {}}, "additionalProperties": {"type": "string"}}, {"x": 1, "y": 2}, "/y", "expected string"),
        ("patternProperties", {"patternProperties": {"^n_": {"type": "number"}}, "additionalProperties": False}, {"n_a": 1, "b": 2}, "/b", "not allowed"),
        ("propertyNames", {"propertyNames": {"pattern": "^[a-z]+$"}}, {"Bad": 1}, "/Bad", "property name"),
        ("dependentRequired", {"dependentRequired": {"a": ["b"]}}, {"a": 1}, "", "requires property 'b'"),
        ("minProperties", {"minProperties": 1}, {}, "", "at least 1"),
        ("pointer escape ~1 in $ref", {"$defs": {"a/b": {"type": "string"}}, "properties": {"p": {"$ref": "#/$defs/a~1b"}}}, {"p": 1}, "/p", "expected string"),
        ("pointer escape in instance path", {"properties": {"a/b": {"type": "string"}}}, {"a/b": 1}, "/a~1b", "expected string"),
        ("$ref to root", {"properties": {"child": {"$ref": "#"}}, "required": ["v"]}, {"v": 1, "child": {}}, "/child", "missing required property 'v'"),
        ("unresolvable $ref", {"$ref": "#/$defs/missing"}, 1, "", "cannot resolve $ref"),
        ("oneOf exactly one", {"oneOf": [{"type": "integer"}, {"type": "string"}]}, 5, None, None),
        ("oneOf two matches", {"oneOf": [{"type": "integer"}, {"minimum": 0}]}, 5, "", "exactly one"),
        ("oneOf none", {"oneOf": [{"type": "integer"}, {"type": "string"}]}, None, "", "does not match any"),
        ("anyOf closest branch", {"anyOf": [{"type": "string"}, {"type": "object", "required": ["k"]}]}, {}, "", "missing required property 'k'"),
        ("allOf", {"allOf": [{"minimum": 2}, {"maximum": 3}]}, 4, "", "greater than the maximum"),
        ("not", {"not": {"const": "x"}}, "x", "", "must not match"),
        ("if/then", {"if": {"properties": {"k": {"const": 1}}, "required": ["k"]}, "then": {"required": ["v"]}, "else": {"required": ["w"]}}, {"k": 1}, "", "missing required property 'v'"),
        ("if/else", {"if": {"properties": {"k": {"const": 1}}, "required": ["k"]}, "then": {"required": ["v"]}, "else": {"required": ["w"]}}, {"k": 2}, "", "missing required property 'w'"),
        ("if/then satisfied", {"if": {"properties": {"k": {"const": 1}}, "required": ["k"]}, "then": {"required": ["v"]}}, {"k": 1, "v": 0}, None, None),
        ("boolean schema false", {"properties": {"x": False}}, {"x": 1}, "/x", "schema is false"),
    ]


def _broken_cases() -> List[Tuple[str, str, str, Any, str, Optional[str]]]:
    """(name, schema name, pointer to mutate, new value, expected error path, message substring)."""
    D = _DELETE
    return [
        ("contract missing schema_version", "design-contract", "/schema_version", D, "", "missing required property 'schema_version'"),
        ("contract wrong schema_version", "design-contract", "/schema_version", "2.0", "/schema_version", "must equal"),
        ("contract schema_version as number", "design-contract", "/schema_version", 1.0, "/schema_version", "expected string"),
        ("contract bad loop type", "design-contract", "/loops/0/type", "core-loop", "/loops/0/type", "is not one of"),
        ("contract too many pillars", "design-contract", "/meta/pillars", ["a", "b", "c", "d", "e", "f"], "/meta/pillars", "at most 5"),
        ("contract negative interstitial interval", "design-contract", "/monetization/ads/interstitial/min_interval_sec", -5, "/monetization/ads/interstitial/min_interval_sec", "minimum"),
        ("contract retention as percent", "design-contract", "/analytics/kpi_targets/d1", 40, "/analytics/kpi_targets/d1", "maximum"),
        ("contract bad palette colour", "design-contract", "/art_direction/palette/2", "orange", "/art_direction/palette/2", "pattern"),
        ("contract loop step without action", "design-contract", "/loops/1/steps/0/action", D, "/loops/1/steps/0", "missing required property 'action'"),
        ("contract parameter value object", "design-contract", "/mechanics/1/parameters/0/value", {"x": 1}, "/mechanics/1/parameters/0/value", "expected number"),
        ("features short id", "features", "/features/0/id", "F12", "/features/0/id", "pattern"),
        ("features gate key typo", "features", "/features/3/gates/playthru", "pass", "/features/3/gates/playthru", "not allowed"),
        ("features evidence key typo", "features", "/features/1/evidence/visuals", ["x.png"], "/features/1/evidence/visuals", "not allowed"),
        ("features gate value typo", "features", "/features/3/gates/static", "passed", "/features/3/gates/static", "is not one of"),
        ("features passes with null gate", "features", "/features/1/gates/perf", None, "/features/1/gates/perf", "is not one of"),
        ("features done but not passing", "features", "/features/1/passes", False, "/features/1/passes", "must equal true"),
        ("features passes but in progress", "features", "/features/1/status", "in_progress", "/features/1/status", "must equal \"done\""),
        ("features n/a without note", "features", "/features/9/gate_notes", D, "/features/9", "missing required property 'gate_notes'"),
        ("features pass without evidence", "features", "/features/1/evidence/unit", None, "/features/1/evidence/unit", "expected string or array"),
        ("features absolute evidence path", "features", "/features/1/evidence/static", "/tmp/static.log", "/features/1/evidence/static", "pattern"),
        ("features parent-dir evidence path", "features", "/features/1/evidence/visual/0", "../shot.png", "/features/1/evidence/visual/0", "pattern"),
        ("features bad dependency id", "features", "/features/1/depends_on/0", "1", "/features/1/depends_on/0", "pattern"),
        ("manifest commercial_ok as string", "asset-manifest", "/assets/0/licence/commercial_ok", "yes", "/assets/0/licence/commercial_ok", "expected boolean"),
        ("manifest bad timestamp", "asset-manifest", "/assets/0/created_at", "yesterday", "/assets/0/created_at", "pattern"),
        ("manifest approved without approver", "asset-manifest", "/assets/0/approved_by", None, "/assets/0/approved_by", "expected string"),
        ("manifest final placeholder", "asset-manifest", "/assets/4/status", "final", "/assets/4/placeholder", "must equal false"),
        ("manifest bad sha256", "asset-manifest", "/assets/0/sha256", "ABC", "/assets/0/sha256", "pattern"),
        ("budget negative cap", "budget", "/cap_usd", -1, "/cap_usd", "minimum"),
        ("budget ledger missing ts", "budget", "/ledger/0/ts", D, "/ledger/0", "missing required property 'ts'"),
        ("economy skill above 1", "economy-model", "/archetypes/0/skill", 1.5, "/archetypes/0/skill", "maximum"),
        ("economy non-integer level count", "economy-model", "/levels/count", 10.5, "/levels/count", "expected integer"),
        ("economy bad trigger", "economy-model", "/nodes/0/trigger", "on_win", "/nodes/0/trigger", "is not one of"),
        ("economy non-numeric output", "economy-model", "/nodes/0/outputs/coins", "40", "/nodes/0/outputs/coins", "expected number"),
        ("level sort layout without tubes", "level-spec", "/layout/tubes", D, "/layout", "missing required property 'tubes'"),
        ("level bad layout type", "level-spec", "/layout/type", "hexsort", "/layout/type", "is not one of"),
        ("level bad teach", "level-spec", "/teach", "tutorial", "/teach", "is not one of"),
        ("level bot_win_rate above 1", "level-spec", "/solver/bot_win_rate", 97, "/solver/bot_win_rate", "does not match any"),
        ("taxonomy camelCase event", "event-taxonomy", "/events/0/name", "LevelStart", "/events/0/name", "pattern"),
        ("taxonomy reserved prefix", "event-taxonomy", "/events/0/name", "firebase_level", "/events/0/name", "pattern"),
        ("taxonomy bad param type", "event-taxonomy", "/events/1/params/0/type", "integer", "/events/1/params/0/type", "is not one of"),
        ("mechanic bad aesthetic", "mechanic-card", "/aesthetics/0", "fun", "/aesthetics/0", "is not one of"),
        ("mechanic missing name", "mechanic-card", "/name", D, "", "missing required property 'name'"),
        ("deconstruction bad source url", "deconstruction", "/sources/0", "dreamgames.com", "/sources/0", "pattern"),
        ("deconstruction mechanic without id", "deconstruction", "/mechanics/0/id", D, "/mechanics/0", "missing required property 'id'"),
        ("concept score 11", "concept", "/scores/novelty", 11, "/scores/novelty", "maximum"),
        ("concept score key typo", "concept", "/scores/novelity", 8, "/scores/novelity", "not allowed"),
        ("concept core_loop wrong type", "concept", "/core_loop", 5, "/core_loop", "does not match any"),
        ("playtest bad verdict", "playtest-report", "/verdict", "ok", "/verdict", "is not one of"),
        ("playtest pass with crash", "playtest-report", "/metrics/crashes", 1, "/metrics/crashes", "must equal 0"),
        ("playtest pass with blocker", "playtest-report", "/findings/0/severity", "blocker", "/findings/0/severity", "must not match"),
        ("perf fps as string", "perf-report", "/fps/avg", "60", "/fps/avg", "expected number"),
        ("perf pass with violations", "perf-report", "/verdict", "pass", "/violations", "at most 0"),
        ("perf bad tier", "perf-report", "/device/tier", "potato", "/device/tier", "is not one of"),
        ("config bad engine", "config", "/engine", "cryengine", "/engine", "is not one of"),
        ("config bad storefront", "config", "/storefronts/0", "USA", "/storefronts/0", "pattern"),
        ("config empty platforms", "config", "/platforms", [], "/platforms", "at least 1"),
        ("config missing project title", "config", "/project/title", D, "/project", "missing required property 'title'"),
    ]


def _inference_cases() -> List[Tuple[str, Optional[str]]]:
    return [
        (".gamestudio/config.json", "config"),
        (".gamestudio/contract.json", "design-contract"),
        (".gamestudio/features.json", "features"),
        (".gamestudio/assets/manifest.json", "asset-manifest"),
        (".gamestudio/budget.json", "budget"),
        (".gamestudio/economy/v1.economy.json", "economy-model"),
        (".gamestudio/levels/bonus_005.level.json", "level-spec"),
        (".gamestudio/analytics/events.taxonomy.json", "event-taxonomy"),
        ("cards/merge_two.mechanic.json", "mechanic-card"),
        (".gamestudio/research/royal-match.deconstruction.json", "deconstruction"),
        (".gamestudio/concepts/c03.concept.json", "concept"),
        (".gamestudio/playtests/2026-10-18-smoke.playtest.json", "playtest-report"),
        (".gamestudio/reports/a15-wave10.perf.json", "perf-report"),
        (".gamestudio/evidence/F002/playthrough.json", "playtest-report"),
        (".gamestudio/evidence/F009/perf.json", "perf-report"),
        ("schemas/examples/example.design-contract.json", "design-contract"),
        ("schemas/examples/example.config.json", "config"),
        ("Level.LEVEL.JSON", "level-spec"),
        ("jest.config.json", None),
        ("package.json", None),
        ("notes.json", None),
        ("level.txt", None),
    ]


def _selftest(verbose: bool = False) -> int:
    failures: List[str] = []
    passed = 0

    def check(name: str, ok: bool, detail: str = "") -> None:
        nonlocal passed
        if ok:
            passed += 1
            if verbose:
                print("  ok   %s" % name)
        else:
            failures.append("%s%s" % (name, (": " + detail) if detail else ""))

    def has_error(errors: List[ErrorT], path: Optional[str], substr: Optional[str]) -> bool:
        return any(p == path and (substr is None or substr in m) for p, m in errors)

    # 1. keyword semantics on inline schemas
    for name, schema, inst, epath, sub in _keyword_cases():
        errs = Validator().validate(inst, schema, SCHEMA_DIR)
        if epath is None:
            check("keyword: " + name, not errs, "; ".join(format_errors(errs)))
        else:
            check("keyword: " + name, has_error(errs, epath, sub), "got %s" % (format_errors(errs) or "no errors"))

    # 2. relative file refs, nested refs resolving inside the referenced file, subdirectories
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        (t / "sub").mkdir()
        (t / "a.schema.json").write_text(json.dumps({
            "$defs": {
                "x": {"type": "object", "properties": {"n": {"$ref": "#/$defs/n"}, "c": {"$ref": "sub/c.schema.json"}}},
                "n": {"type": "integer"},
            }
        }), encoding="utf-8")
        (t / "sub" / "c.schema.json").write_text(json.dumps({"$defs": {"s": {"type": "string"}}, "$ref": "#/$defs/s"}), encoding="utf-8")
        (t / "b.schema.json").write_text(json.dumps({"type": "object", "properties": {"q": {"$ref": "a.schema.json#/$defs/x"}}}), encoding="utf-8")
        v = Validator()
        errs = v.validate({"q": {"n": "s", "c": 5}}, t / "b.schema.json")
        check("file ref: nested local ref resolves in referenced file", has_error(errs, "/q/n", "expected integer"), str(format_errors(errs)))
        check("file ref: subdirectory ref", has_error(errs, "/q/c", "expected string"), str(format_errors(errs)))
        check("file ref: valid instance", not v.validate({"q": {"n": 1, "c": "ok"}}, t / "b.schema.json"))
        errs = v.validate({}, {"$ref": "missing.schema.json#/$defs/x"}, t)
        check("file ref: missing file reported", has_error(errs, "", "cannot resolve $ref"), str(format_errors(errs)))
        dup = t / "dup.json"
        dup.write_text('{"a": 1, "a": 2}', encoding="utf-8")
        _, problems = load_json_file(dup)
        check("loader: duplicate keys detected", any("duplicate key" in p for p in problems), str(problems))
        nan = t / "nan.json"
        nan.write_text('{"a": NaN}', encoding="utf-8")
        data, problems = load_json_file(nan)
        check("loader: NaN rejected", data is None and bool(problems), str(problems))

    # 3. shipped schemas: parse and lint
    schema_files = sorted(SCHEMA_DIR.glob("*.schema.json"))
    names_on_disk = {p.name[: -len(".schema.json")] for p in schema_files}
    for name in SCHEMA_NAMES + SHARED_SCHEMAS:
        check("schema exists: %s" % name, name in names_on_disk)
    for p in schema_files:
        issues = lint_schema(p)
        check("schema lint: %s" % p.name, not issues, "; ".join(issues[:8]))

    # 4. examples: one per document schema, all valid
    examples: Dict[str, Any] = {}
    for name in SCHEMA_NAMES:
        ex = EXAMPLES_DIR / ("example.%s.json" % name)
        if not ex.is_file():
            check("example exists: %s" % ex.name, False)
            continue
        data, problems = load_json_file(ex)
        check("example parses: %s" % ex.name, data is not None and not problems, "; ".join(problems))
        if data is None:
            continue
        examples[name] = data
        inferred = schema_path_for(ex)
        check("example schema inferred: %s" % ex.name, inferred is not None and inferred.name == "%s.schema.json" % name, str(inferred))
        errs = validate(data, SCHEMA_DIR / ("%s.schema.json" % name))
        check("example valid: %s" % ex.name, not errs, "; ".join(errs[:8]))
        check("validate_file agrees: %s" % ex.name, validate_file(ex) == [])

    # 5. broken documents must fail at the right JSON pointer
    for name, sname, pointer, value, epath, sub in _broken_cases():
        if sname not in examples:
            check("broken: " + name, False, "example %s missing" % sname)
            continue
        try:
            doc = _mutate(examples[sname], pointer, value)
        except (KeyError, IndexError, ValueError, TypeError) as exc:
            check("broken: " + name, False, "mutation failed: %s" % exc)
            continue
        errs = validate_detailed(doc, SCHEMA_DIR / ("%s.schema.json" % sname))
        check("broken: " + name, has_error(errs, epath, sub), "expected %s (%s); got %s" % (_fmt_path(epath), sub, format_errors(errs) or "no errors"))

    # 6. bundled schemas are self-contained and give identical results
    bundles: Dict[str, Any] = {}
    with tempfile.TemporaryDirectory() as empty:
        for name in SCHEMA_NAMES:
            try:
                bundles[name] = bundle_schema(SCHEMA_DIR / ("%s.schema.json" % name))
            except SchemaError as exc:
                check("bundle: %s" % name, False, str(exc))
                continue
            ext = _external_refs(bundles[name])
            check("bundle self-contained: %s" % name, not ext, str(ext[:3]))
            if name in examples:
                errs = Validator().validate(examples[name], bundles[name], empty)
                check("bundle validates example: %s" % name, not errs, "; ".join(format_errors(errs)[:5]))
        for name, sname, pointer, value, epath, sub in _broken_cases():
            if sname not in examples or sname not in bundles:
                continue
            doc = _mutate(examples[sname], pointer, value)
            a = sorted(validate_detailed(doc, SCHEMA_DIR / ("%s.schema.json" % sname)))
            b = sorted(Validator().validate(doc, bundles[sname], empty))
            check("bundle equivalent on broken: " + name, a == b, "unbundled %s vs bundled %s" % (a, b))

    # 7. filename inference and $schema_name fallback
    for fname, expected in _inference_cases():
        got = schema_name_for(fname)
        check("infer: %s" % fname, got == expected, "got %r" % got)
    p = infer_schema("misc/notes.json", {"$schema_name": "level-spec"})
    check("infer: $schema_name fallback", p is not None and p.name == "level-spec.schema.json", str(p))
    p = infer_schema("misc/notes.json", {"$schema_name": "level-spec.schema.json"})
    check("infer: $schema_name with suffix", p is not None and p.name == "level-spec.schema.json", str(p))
    check("infer: unknown $schema_name", infer_schema("misc/notes.json", {"$schema_name": "nope"}) is None)
    if "level-spec" in examples:
        tagged = dict(examples["level-spec"], **{"$schema_name": "level-spec"})
        check("$schema_name accepted by schema", not validate(tagged, SCHEMA_DIR / "level-spec.schema.json"))
        mis = dict(examples["level-spec"], **{"$schema_name": "concept"})
        check("$schema_name mismatch rejected", has_error(validate_detailed(mis, SCHEMA_DIR / "level-spec.schema.json"), "/$schema_name", "must equal"))

    # 8. error strings carry a JSON pointer prefix
    msgs = validate({"schema_version": "1.0", "features": [{"id": "F1", "title": "x"}]}, SCHEMA_DIR / "features.schema.json")
    check("error format: pointer prefix", any(m.startswith("/features/0/id: ") for m in msgs), str(msgs))
    root_msgs = validate({}, SCHEMA_DIR / "features.schema.json")
    check("error format: root shown as /", any(m.startswith("/: missing required property") for m in root_msgs), str(root_msgs))

    total = passed + len(failures)
    if failures:
        print("selftest: %d/%d checks passed; failures:" % (passed, total))
        for f in failures:
            print("  FAIL %s" % f)
        return 1
    print("selftest: all %d checks passed (%d keyword cases, %d schemas linted, %d examples valid, %d broken documents rejected at the expected pointer)"
          % (total, len(_keyword_cases()), len(schema_files), len(examples), len(_broken_cases())))
    return 0


# --------------------------------------------------------------------------- CLI


def _iter_auto_targets(paths: List[str]) -> Iterable[Tuple[Path, bool]]:
    """Yield (file, explicit). Directories are walked for *.json files, skipping VCS,
    dependency and engine-cache folders; explicitly named files are always yielded."""
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            for f in sorted(p.rglob("*.json")):
                if any(part in (".git", "node_modules", ".godot", "Library") for part in f.parts):
                    continue
                yield f, False
        else:
            yield p, True


def _result(instance: Path, schema: Optional[Path], errors: List[ErrorT], status: str) -> Dict[str, Any]:
    return {
        "instance": str(instance),
        "schema": str(schema) if schema else None,
        "status": status,
        "ok": status in ("valid", "skipped"),
        "errors": [{"path": _fmt_path(p), "message": m} for p, m in errors],
    }


def _check_one(instance: Path, schema: Optional[Path]) -> Dict[str, Any]:
    data, problems = load_json_file(instance)
    if data is None:
        return _result(instance, schema, [("", m) for m in problems], "invalid")
    if schema is None:
        schema = infer_schema(instance, data)
        if schema is None:
            return _result(instance, None, [], "unknown")
    errors = [("", m) for m in problems] + validate_detailed(data, schema)
    return _result(instance, schema, errors, "invalid" if errors else "valid")


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(
        prog="validate_json.py",
        description="Validate arcosian JSON documents against the ontology schemas (JSON Schema 2020-12 subset, stdlib only).",
    )
    ap.add_argument("--schema", help="schema file to validate against (with --instance)")
    ap.add_argument("--instance", help="JSON document to validate (with --schema)")
    ap.add_argument("--auto", nargs="+", metavar="PATH", help="validate files (or directories) inferring the schema from file names or a top-level $schema_name field")
    ap.add_argument("--lint", nargs="*", metavar="SCHEMA", help="lint schema files (default: every shipped schema)")
    ap.add_argument("--list", action="store_true", help="list schemas and the file-name rules")
    ap.add_argument("--bundle", metavar="SCHEMA", help="print a self-contained copy of SCHEMA with external refs inlined into $defs")
    ap.add_argument("--out", metavar="PATH", help="with --bundle: write to PATH instead of stdout")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--selftest", action="store_true", help="run built-in tests")
    ap.add_argument("-v", "--verbose", action="store_true", help="verbose self-test output")
    args = ap.parse_args(argv)

    if args.selftest:
        return _selftest(args.verbose)

    if args.bundle:
        bp = Path(args.bundle)
        if not bp.is_file() and _schema_file(args.bundle):
            bp = _schema_file(args.bundle)  # allow a bare schema name such as "design-contract"
        if not bp.is_file():
            print("error: schema not found: %s" % args.bundle, file=sys.stderr)
            return 2
        try:
            text = json.dumps(bundle_schema(bp), indent=2, ensure_ascii=False) + "\n"
        except SchemaError as exc:
            print("error: %s" % exc, file=sys.stderr)
            return 2
        if args.out:
            Path(args.out).write_text(text, encoding="utf-8")
            print("wrote %s" % args.out)
        else:
            sys.stdout.write(text)
        return 0

    if args.list:
        info = {
            "schema_dir": str(SCHEMA_DIR),
            "schemas": {n: str(_schema_file(n)) for n in SCHEMA_NAMES},
            "exact_filenames": EXACT_FILENAMES,
            "suffixes": {"*.%s.json" % k: v for k, v in SUFFIXES.items()},
            "also": "example.<schema-name>.json, or a top-level \"$schema_name\": \"<schema-name>\" field",
        }
        if args.json:
            print(json.dumps(info, indent=2))
        else:
            print("Schemas in %s:" % SCHEMA_DIR)
            for n in SCHEMA_NAMES:
                print("  %-16s %s" % (n, "ok" if _schema_file(n) else "MISSING"))
            print("File-name rules:")
            for k, v in EXACT_FILENAMES.items():
                print("  %-26s -> %s" % (k, v))
            for k, v in SUFFIXES.items():
                print("  %-26s -> %s" % ("*.%s.json" % k, v))
            print("  %-26s -> %s" % ("example.<name>.json", "<name>"))
            print("  fallback: top-level \"$schema_name\" field")
        return 0

    if args.lint is not None:
        targets = [Path(p) for p in args.lint] or sorted(SCHEMA_DIR.glob("*.schema.json"))
        report = {str(p): lint_schema(p) for p in targets}
        bad = any(report.values())
        if args.json:
            print(json.dumps({"ok": not bad, "issues": report}, indent=2))
        else:
            for p, issues in report.items():
                print("%s: %s" % (p, "clean" if not issues else "%d issue(s)" % len(issues)))
                for i in issues:
                    print("  - %s" % i)
        return 1 if bad else 0

    results: List[Dict[str, Any]] = []
    if args.schema or args.instance:
        if not (args.schema and args.instance):
            ap.error("--schema and --instance must be used together")
        sp, ip = Path(args.schema), Path(args.instance)
        for p in (sp, ip):
            if not p.is_file():
                print("error: file not found: %s" % p, file=sys.stderr)
                return 2
        try:
            results.append(_check_one(ip, sp))
        except SchemaError as exc:
            print("error: %s" % exc, file=sys.stderr)
            return 2
    elif args.auto:
        for f, explicit in _iter_auto_targets(args.auto):
            if not f.exists():
                print("error: file not found: %s" % f, file=sys.stderr)
                return 2
            res = _check_one(f, None)
            if res["status"] == "unknown":
                if explicit:
                    print("error: cannot infer a schema for %s; use a conventional name (validate_json.py --list) or add \"$schema_name\"" % f, file=sys.stderr)
                    return 2
                res["status"], res["ok"] = "skipped", True
            results.append(res)
    else:
        ap.print_help()
        return 2

    ok = all(r["ok"] for r in results)
    if args.json:
        print(json.dumps({"ok": ok, "results": results}, indent=2))
    else:
        for r in results:
            if r["status"] == "skipped":
                continue
            if r["ok"]:
                print("OK    %s  (%s)" % (r["instance"], Path(r["schema"]).name if r["schema"] else "-"))
            else:
                print("FAIL  %s  (%s)" % (r["instance"], Path(r["schema"]).name if r["schema"] else "-"))
                for e in r["errors"]:
                    print("      %s: %s" % (e["path"], e["message"]))
        checked = sum(1 for r in results if r["status"] != "skipped")
        failed = sum(1 for r in results if not r["ok"])
        print("%d file(s) checked, %d failed%s" % (checked, failed, ", %d skipped (no schema)" % (len(results) - checked) if len(results) > checked else ""))
    return 0 if ok else 1


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows pipes default to the ANSI code page; Claude Code reads UTF-8
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
