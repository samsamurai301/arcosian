#!/usr/bin/env python3
"""narrative_lint.py - structural, text and cost checks for game narrative content.

Subcommands
  graph  --story PATH            state-aware checks of a JSON narrative graph (schema_version 1.0)
  yarn   --in FILE [FILE ...]    structural checks of Yarn Spinner scripts (subset parser)
  ink    --in FILE [FILE ...]    structural checks of ink scripts (knot/stitch-level subset parser)
  lines  --in PATH               string-table checks: IDs, length budgets with localisation expansion,
                                 placeholders, concatenation and plural/gender hazards (CSV or JSON)
  cost   --structure S ...       content-cost model for branching structures
  barks  --pool N --triggers T   repetition maths for bark pools (random vs shuffle bag)

The yarn and ink parsers are deliberately conservative subsets: they catch missing targets,
unreachable sections, loose ends, variable hygiene and mobile choice budgets. They do not replace
the official compilers (inklecate, the Yarn Spinner compiler), which must also run in CI.

Exit codes: 0 = no errors (warnings allowed unless --strict), 1 = check failed, 2 = usage/input error.
Stdlib only, Python 3.9+. Run `narrative_lint.py --selftest` to exercise the core logic.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
import re
import sys
import tempfile
from collections import deque
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

VERSION = "1.0.0"

# --------------------------------------------------------------------------------------------
# Findings
# --------------------------------------------------------------------------------------------


class Report:
    def __init__(self, tool: str) -> None:
        self.tool = tool
        self.findings: List[Dict[str, Any]] = []
        self.metrics: Dict[str, Any] = {}

    def add(self, level: str, code: str, where: str, message: str) -> None:
        self.findings.append({"level": level, "code": code, "where": where, "message": message})

    def err(self, code: str, where: str, message: str) -> None:
        self.add("error", code, where, message)

    def warn(self, code: str, where: str, message: str) -> None:
        self.add("warning", code, where, message)

    def info(self, code: str, where: str, message: str) -> None:
        self.add("info", code, where, message)

    def count(self, level: str) -> int:
        return sum(1 for f in self.findings if f["level"] == level)

    def codes(self) -> Set[str]:
        return {f["code"] for f in self.findings}

    def ok(self, strict: bool = False) -> bool:
        if self.count("error"):
            return False
        if strict and self.count("warning"):
            return False
        return True

    def to_dict(self, strict: bool = False) -> Dict[str, Any]:
        return {
            "tool": self.tool,
            "ok": self.ok(strict),
            "errors": self.count("error"),
            "warnings": self.count("warning"),
            "findings": self.findings,
            "metrics": self.metrics,
        }

    def render(self, strict: bool = False) -> str:
        out = [f"narrative_lint {self.tool}: {'OK' if self.ok(strict) else 'FAILED'} "
               f"({self.count('error')} errors, {self.count('warning')} warnings)"]
        if self.metrics:
            out.append("metrics:")
            for k, v in self.metrics.items():
                out.append(f"  {k}: {v}")
        for level in ("error", "warning", "info"):
            items = [f for f in self.findings if f["level"] == level]
            if items:
                out.append(f"{level}s:")
                for f in items:
                    out.append(f"  [{f['code']}] {f['where']}: {f['message']}")
        return "\n".join(out)


def emit(report: Report, as_json: bool, strict: bool) -> int:
    if as_json:
        print(json.dumps(report.to_dict(strict), indent=2, default=str))
    else:
        print(report.render(strict))
    return 0 if report.ok(strict) else 1


class InputError(Exception):
    pass


# --------------------------------------------------------------------------------------------
# Tiny safe expression language for graph conditions
#   literals: numbers, 'strings', "strings", true, false
#   identifiers: [A-Za-z_][A-Za-z0-9_.]* (a leading $ is ignored, for Yarn-style names)
#   operators: == != >= <= > < and or not && || ! ( )
# --------------------------------------------------------------------------------------------

_TOKEN_RE = re.compile(
    r"\s*(?:(?P<num>\d+(?:\.\d+)?)|(?P<str>'[^']*'|\"[^\"]*\")|(?P<op>==|!=|>=|<=|&&|\|\||[<>!()])|"
    r"(?P<id>\$?[A-Za-z_][A-Za-z0-9_.]*))"
)


def tokenize(expr: str) -> List[Tuple[str, str]]:
    pos = 0
    toks: List[Tuple[str, str]] = []
    expr = expr.strip()
    while pos < len(expr):
        m = _TOKEN_RE.match(expr, pos)
        if not m or m.end() == pos:
            raise InputError(f"cannot parse condition near: {expr[pos:pos + 20]!r}")
        pos = m.end()
        if m.group("num") is not None:
            toks.append(("num", m.group("num")))
        elif m.group("str") is not None:
            toks.append(("str", m.group("str")[1:-1]))
        elif m.group("op") is not None:
            toks.append(("op", m.group("op")))
        else:
            word = m.group("id")
            low = word.lower()
            if low in ("and", "or", "not"):
                toks.append(("op", low))
            elif low in ("true", "false"):
                toks.append(("bool", low))
            else:
                toks.append(("id", word.lstrip("$")))
        # skip trailing whitespace handled by regex
    return toks


class _Parser:
    def __init__(self, toks: List[Tuple[str, str]]) -> None:
        self.toks = toks
        self.i = 0

    def peek(self) -> Optional[Tuple[str, str]]:
        return self.toks[self.i] if self.i < len(self.toks) else None

    def take(self) -> Tuple[str, str]:
        t = self.peek()
        if t is None:
            raise InputError("unexpected end of condition")
        self.i += 1
        return t

    def parse(self) -> Any:
        node = self.or_expr()
        if self.peek() is not None:
            raise InputError(f"unexpected token {self.peek()[1]!r} in condition")
        return node

    def or_expr(self) -> Any:
        node = self.and_expr()
        while self.peek() in (("op", "or"), ("op", "||")):
            self.take()
            node = ("or", node, self.and_expr())
        return node

    def and_expr(self) -> Any:
        node = self.not_expr()
        while self.peek() in (("op", "and"), ("op", "&&")):
            self.take()
            node = ("and", node, self.not_expr())
        return node

    def not_expr(self) -> Any:
        if self.peek() in (("op", "not"), ("op", "!")):
            self.take()
            return ("not", self.not_expr())
        return self.cmp()

    def cmp(self) -> Any:
        left = self.atom()
        t = self.peek()
        if t and t[0] == "op" and t[1] in ("==", "!=", ">=", "<=", ">", "<"):
            self.take()
            return ("cmp", t[1], left, self.atom())
        return left

    def atom(self) -> Any:
        t = self.take()
        if t == ("op", "("):
            node = self.or_expr()
            if self.take() != ("op", ")"):
                raise InputError("missing ')' in condition")
            return node
        if t[0] == "num":
            return ("lit", float(t[1]) if "." in t[1] else int(t[1]))
        if t[0] == "str":
            return ("lit", t[1])
        if t[0] == "bool":
            return ("lit", t[1] == "true")
        if t[0] == "id":
            return ("var", t[1])
        raise InputError(f"unexpected token {t[1]!r} in condition")


def parse_condition(expr: str) -> Any:
    return _Parser(tokenize(expr)).parse()


def condition_vars(ast: Any) -> Set[str]:
    if ast is None:
        return set()
    kind = ast[0]
    if kind == "var":
        return {ast[1]}
    if kind == "lit":
        return set()
    if kind == "not":
        return condition_vars(ast[1])
    if kind in ("and", "or"):
        return condition_vars(ast[1]) | condition_vars(ast[2])
    if kind == "cmp":
        return condition_vars(ast[2]) | condition_vars(ast[3])
    return set()


def eval_condition(ast: Any, env: Dict[str, Any]) -> Any:
    kind = ast[0]
    if kind == "lit":
        return ast[1]
    if kind == "var":
        return env.get(ast[1])
    if kind == "not":
        return not truthy(eval_condition(ast[1], env))
    if kind == "and":
        return truthy(eval_condition(ast[1], env)) and truthy(eval_condition(ast[2], env))
    if kind == "or":
        return truthy(eval_condition(ast[1], env)) or truthy(eval_condition(ast[2], env))
    if kind == "cmp":
        op, a, b = ast[1], eval_condition(ast[2], env), eval_condition(ast[3], env)
        if op == "==":
            return a == b
        if op == "!=":
            return a != b
        try:
            if a is None or b is None or isinstance(a, str) != isinstance(b, str):
                return False
            return {">=": a >= b, "<=": a <= b, ">": a > b, "<": a < b}[op]
        except TypeError:
            return False
    return False


def truthy(v: Any) -> bool:
    return bool(v) if v is not None else False


# --------------------------------------------------------------------------------------------
# graph: JSON narrative graph checks
# --------------------------------------------------------------------------------------------

_INC_RE = re.compile(r"^[+-]\d+(?:\.\d+)?$")
DEFAULT_BOUND = 100


def apply_effects(env: Dict[str, Any], effects: Dict[str, Any], bounds: Dict[str, Tuple[float, float]]) -> Dict[str, Any]:
    new = dict(env)
    for var, val in effects.items():
        if isinstance(val, str) and _INC_RE.match(val):
            base = new.get(var) or 0
            if isinstance(base, bool):
                base = int(base)
            num = float(val) if "." in val else int(val)
            new[var] = base + num
        else:
            new[var] = val
        if isinstance(new[var], (int, float)) and not isinstance(new[var], bool):
            lo, hi = bounds.get(var, (-DEFAULT_BOUND, DEFAULT_BOUND))
            new[var] = max(lo, min(hi, new[var]))
    return new


def check_graph(doc: Dict[str, Any], max_states: int = 50000, max_options: int = 4,
                var_budget: int = 20) -> Report:
    rep = Report("graph")
    if not isinstance(doc, dict) or not isinstance(doc.get("nodes"), list):
        raise InputError("graph JSON must be an object with a 'nodes' array")
    if doc.get("schema_version") != "1.0":
        rep.warn("schema_version", "document", "expected \"schema_version\": \"1.0\"")
    variables: Dict[str, Any] = dict(doc.get("variables") or {})
    bounds_raw = doc.get("bounds") or {}
    bounds: Dict[str, Tuple[float, float]] = {}
    for k, v in bounds_raw.items():
        if isinstance(v, list) and len(v) == 2:
            bounds[k] = (v[0], v[1])

    nodes: Dict[str, Dict[str, Any]] = {}
    for n in doc["nodes"]:
        nid = n.get("id")
        if not isinstance(nid, str) or not nid:
            rep.err("node_id", "nodes", "every node needs a non-empty string id")
            continue
        if nid in nodes:
            rep.err("duplicate_node", nid, "node id used more than once")
        nodes[nid] = n
    start = doc.get("start") or (doc["nodes"][0].get("id") if doc["nodes"] else None)
    if start not in nodes:
        rep.err("missing_start", str(start), "start node does not exist")
        rep.metrics.update({"nodes": len(nodes)})
        return rep

    reads: Set[str] = set()
    writes: Set[str] = set()
    edges: Dict[str, List[Dict[str, Any]]] = {}
    for nid, n in nodes.items():
        compiled = []
        out = n.get("edges") or []
        labelled = [e for e in out if e.get("label")]
        if len(labelled) > max_options:
            rep.warn("too_many_options", nid, f"{len(labelled)} options; mobile budget is 2-{max_options}")
        for idx, e in enumerate(out):
            to = e.get("to")
            if to not in nodes:
                rep.err("missing_target", f"{nid} -> {to}", "edge points to a node that does not exist")
                continue
            ast = None
            if e.get("if"):
                try:
                    ast = parse_condition(str(e["if"]))
                except InputError as ex:
                    rep.err("bad_condition", f"{nid} -> {to}", str(ex))
                    continue
                reads |= condition_vars(ast)
            eff = e.get("set") or {}
            if not isinstance(eff, dict):
                rep.err("bad_effects", f"{nid} -> {to}", "'set' must be an object")
                eff = {}
            writes |= set(eff.keys())
            compiled.append({"to": to, "cond": ast, "set": eff, "once": bool(e.get("once")),
                             "label": e.get("label") or "", "key": (nid, idx)})
        edges[nid] = compiled

    # structural reachability
    struct_seen: Set[str] = set()
    dq = deque([start])
    while dq:
        cur = dq.popleft()
        if cur in struct_seen:
            continue
        struct_seen.add(cur)
        for e in edges.get(cur, []):
            if e["to"] not in struct_seen:
                dq.append(e["to"])
    for nid in nodes:
        if nid not in struct_seen:
            rep.err("unreachable", nid, "not reachable from start even ignoring conditions")
    for nid in struct_seen:
        if not nodes[nid].get("ending") and not edges.get(nid):
            rep.err("dead_end", nid, "reachable node with no outgoing edges and not marked as an ending")

    # state-space exploration
    init_env = dict(variables)
    var_order = sorted(set(variables) | writes | reads)

    def freeze(env: Dict[str, Any]) -> Tuple[Any, ...]:
        return tuple(env.get(v) for v in var_order)

    State = Tuple[str, Tuple[Any, ...], frozenset]
    start_state: State = (start, freeze(init_env), frozenset())
    parents: Dict[State, Optional[Tuple[State, str]]] = {start_state: None}
    envs: Dict[State, Dict[str, Any]] = {start_state: init_env}
    queue: deque = deque([start_state])
    state_seen_nodes: Set[str] = set()
    softlocks: Dict[str, State] = {}
    truncated = False
    while queue:
        st = queue.popleft()
        node_id, _, used = st
        state_seen_nodes.add(node_id)
        env = envs[st]
        avail = []
        for e in edges.get(node_id, []):
            if e["once"] and e["key"] in used:
                continue
            if e["cond"] is not None and not truthy(eval_condition(e["cond"], env)):
                continue
            avail.append(e)
        if not avail and edges.get(node_id) and not nodes[node_id].get("ending"):
            softlocks.setdefault(node_id, st)
        for e in avail:
            new_env = apply_effects(env, e["set"], bounds)
            new_used = used | {e["key"]} if e["once"] else used
            ns: State = (e["to"], freeze(new_env), new_used)
            if ns in parents:
                continue
            if len(parents) >= max_states:
                truncated = True
                break
            parents[ns] = (st, e["label"] or f"-> {e['to']}")
            envs[ns] = new_env
            queue.append(ns)
        if truncated:
            break

    def path_to(st: State) -> str:
        steps = []
        cur: Optional[State] = st
        while cur is not None and parents.get(cur) is not None:
            prev, label = parents[cur]  # type: ignore[misc]
            steps.append(f"{prev[0]} [{label}]")
            cur = prev
        steps.reverse()
        return " > ".join(steps + [st[0]]) if steps else st[0]

    for nid, st in softlocks.items():
        rep.err("softlock", nid, "a reachable state has no available edge and the node is not an ending; "
                f"example path: {path_to(st)}")
    for nid in struct_seen:
        if nid not in state_seen_nodes:
            if truncated:
                rep.warn("maybe_unreachable", nid, "not reached before the state limit; raise --max-states")
            else:
                rep.err("conditionally_unreachable", nid, "structurally linked but no reachable state satisfies the conditions")
    endings = [nid for nid, n in nodes.items() if n.get("ending")]
    if not endings:
        rep.warn("no_endings", "graph", "no node is marked as an ending (fine for hubs that exit to gameplay; otherwise mark endings)")
    for nid in endings:
        if nid not in state_seen_nodes and nid in struct_seen and not truncated:
            rep.err("ending_unreachable", nid, "ending can never be reached under the conditions")

    declared = set(variables)
    for v in sorted(reads - declared - writes):
        rep.err("undeclared_var", v, "read in a condition but never declared or set")
    for v in sorted((reads & declared) - writes):
        rep.info("never_written", v, "read but never changed; conditions depend only on its initial value")
    for v in sorted(writes - reads):
        rep.warn("unused_var", v, "set but never read; remove it or pay it off")
    for v in sorted(declared - reads - writes):
        rep.warn("unused_var", v, "declared but never read or set")
    if len(declared | writes) > var_budget:
        rep.warn("var_budget", "variables", f"{len(declared | writes)} tracked variables; budget is {var_budget} "
                 "(state combinations become untestable)")

    # dominators -> bottlenecks
    preds: Dict[str, Set[str]] = {n: set() for n in struct_seen}
    for nid in struct_seen:
        for e in edges.get(nid, []):
            if e["to"] in preds:
                preds[e["to"]].add(nid)
    dom: Dict[str, Set[str]] = {n: set(struct_seen) for n in struct_seen}
    dom[start] = {start}
    changed = True
    while changed:
        changed = False
        for n in struct_seen:
            if n == start:
                continue
            ps = [dom[p] for p in preds[n]]
            new = set.intersection(*ps) | {n} if ps else {n}
            if new != dom[n]:
                dom[n] = new
                changed = True
    reach_end = [e for e in endings if e in struct_seen]
    bottlenecks: List[str] = []
    if reach_end:
        common = set.intersection(*[dom[e] for e in reach_end])
        bottlenecks = sorted(common - {start} - set(reach_end))

    # path statistics on the structural graph (acyclic only)
    cyclic = _has_cycle(struct_seen, edges)
    words = {nid: float(nodes[nid].get("words") or 0) for nid in nodes}
    total_words = sum(words[n] for n in struct_seen)
    metrics: Dict[str, Any] = {
        "nodes": len(nodes),
        "edges": sum(len(v) for v in edges.values()),
        "choice_points": sum(1 for n in struct_seen if len(edges.get(n, [])) >= 2),
        "endings": len(endings),
        "reachable_states": len(parents),
        "state_search_truncated": truncated,
        "bottlenecks": bottlenecks,
        "cyclic": cyclic,
        "variables": len(declared | writes),
    }
    if not cyclic and reach_end:
        stats = _dag_paths(start, edges, set(reach_end), words)
        metrics.update(stats)
        if total_words > 0 and stats.get("paths"):
            metrics["total_words"] = int(total_words)
            metrics["share_seen_per_run"] = round(stats["mean_words_per_path"] / total_words, 3)
    rep.metrics = metrics
    return rep


def _has_cycle(nodes: Set[str], edges: Dict[str, List[Dict[str, Any]]]) -> bool:
    color: Dict[str, int] = {n: 0 for n in nodes}
    for root in nodes:
        if color[root]:
            continue
        stack: List[Tuple[str, int]] = [(root, 0)]
        color[root] = 1
        while stack:
            n, i = stack[-1]
            outs = [e["to"] for e in edges.get(n, []) if e["to"] in color]
            if i < len(outs):
                stack[-1] = (n, i + 1)
                m = outs[i]
                if color[m] == 1:
                    return True
                if color[m] == 0:
                    color[m] = 1
                    stack.append((m, 0))
            else:
                color[n] = 2
                stack.pop()
    return False


def _dag_paths(start: str, edges: Dict[str, List[Dict[str, Any]]], endings: Set[str],
               words: Dict[str, float]) -> Dict[str, Any]:
    memo: Dict[str, Tuple[int, float, int, int]] = {}  # count, sum_words, min_len, max_len

    def visit(n: str) -> Tuple[int, float, int, int]:
        if n in memo:
            return memo[n]
        count, sw, mn, mx = 0, 0.0, 10 ** 9, 0
        if n in endings:
            count, sw, mn, mx = 1, words.get(n, 0.0), 1, 1
        for e in edges.get(n, []):
            c, s, a, b = visit(e["to"])
            if c:
                count += c
                sw += s + words.get(n, 0.0) * c
                mn = min(mn, a + 1)
                mx = max(mx, b + 1)
        memo[n] = (count, sw, mn if count else 0, mx)
        return memo[n]

    sys.setrecursionlimit(max(1000, len(edges) * 4 + 100))
    c, s, mn, mx = visit(start)
    return {"paths": c, "shortest_path_nodes": mn, "longest_path_nodes": mx,
            "mean_words_per_path": round(s / c, 1) if c else 0.0}


# --------------------------------------------------------------------------------------------
# yarn: Yarn Spinner subset parser
# --------------------------------------------------------------------------------------------

_YARN_CMD = re.compile(r"<<\s*(\w+)\b(.*?)>>")
_YARN_VAR = re.compile(r"\$([A-Za-z_]\w*)")
_YARN_LINE_ID = re.compile(r"#line:([A-Za-z0-9_.\-]+)")


def _strip_comment(line: str) -> str:
    in_q = False
    for i, ch in enumerate(line):
        if ch == '"':
            in_q = not in_q
        elif ch == "/" and not in_q and line[i:i + 2] == "//" and (i == 0 or line[i - 1] != ":"):
            return line[:i]
    return line


def parse_yarn(files: List[Tuple[str, str]]) -> List[Dict[str, Any]]:
    nodes: List[Dict[str, Any]] = []
    for fname, text in files:
        lines = text.splitlines()
        i = 0
        while i < len(lines):
            headers: Dict[str, str] = {}
            # headers until ---
            while i < len(lines) and lines[i].strip() != "---":
                raw = lines[i].strip()
                if raw and ":" in raw and not raw.startswith("//"):
                    k, v = raw.split(":", 1)
                    headers.setdefault(k.strip(), v.strip())
                i += 1
            if i >= len(lines):
                break
            i += 1  # skip ---
            body_start = i
            body: List[Tuple[int, str]] = []
            while i < len(lines) and lines[i].strip() != "===":
                body.append((i + 1, lines[i]))
                i += 1
            i += 1  # skip ===
            if "title" not in headers:
                nodes.append({"title": None, "file": fname, "line": body_start, "headers": headers, "body": body})
            else:
                nodes.append({"title": headers["title"], "file": fname, "line": body_start, "headers": headers, "body": body})
    return nodes


def check_yarn(files: List[Tuple[str, str]], start: Optional[str] = None, max_options: int = 4,
               choice_budget: int = 40, line_budget: int = 140) -> Report:
    rep = Report("yarn")
    nodes = parse_yarn(files)
    if not nodes:
        raise InputError("no Yarn nodes found (expected 'title:' headers, '---' and '===')")
    by_title: Dict[str, List[Dict[str, Any]]] = {}
    for n in nodes:
        if n["title"] is None:
            rep.err("missing_title", f"{n['file']}:{n['line']}", "node without a 'title:' header")
            continue
        by_title.setdefault(n["title"], []).append(n)
    for title, group in by_title.items():
        if len(group) > 1 and not all("when" in g["headers"] for g in group):
            rep.err("duplicate_node", title, f"{len(group)} nodes share this title; node groups need a 'when:' header on every member")

    declared: Set[str] = set()
    reads: Set[str] = set()
    writes: Set[str] = set()
    line_ids: Dict[str, str] = {}
    missing_ids: List[str] = []
    edges: Dict[str, Set[str]] = {t: set() for t in by_title}
    commands: Dict[str, int] = {}
    lines_total = 0
    options_total = 0
    for n in nodes:
        title = n["title"]
        if title is None:
            continue
        if "when" in n["headers"]:
            reads |= set(_YARN_VAR.findall(n["headers"]["when"]))
        open_groups: Dict[int, int] = {}
        for lineno, raw in n["body"]:
            where = f"{n['file']}:{lineno}"
            line = _strip_comment(raw).rstrip()
            if not line.strip():
                continue
            indent = len(line) - len(line.lstrip(" \t"))
            s = line.strip()
            # close option groups at deeper or equal indent when a non-option line appears
            if not s.startswith("->"):
                for ind in [k for k in open_groups if k >= indent]:
                    del open_groups[ind]
            for m in _YARN_CMD.finditer(s):
                cmd, args = m.group(1), m.group(2).strip()
                if cmd in ("jump", "detour"):
                    target = args.split()[0] if args else ""
                    if target.startswith("{") or target.startswith("$"):
                        rep.info("dynamic_jump", where, f"dynamic {cmd} target not checked: {target}")
                    elif target:
                        edges[title].add(target)
                        if target not in by_title:
                            rep.err("missing_target", where, f"<<{cmd} {target}>> points to a node that does not exist")
                elif cmd == "set":
                    mm = re.match(r"\$([A-Za-z_]\w*)\s*(?:to|=)\s*(.*)$", args)
                    if mm:
                        writes.add(mm.group(1))
                        reads |= set(_YARN_VAR.findall(mm.group(2)))
                    else:
                        rep.warn("bad_set", where, f"could not parse <<set {args}>>")
                elif cmd == "declare":
                    mm = re.match(r"\$([A-Za-z_]\w*)", args)
                    if mm:
                        declared.add(mm.group(1))
                        reads |= set(v for v in _YARN_VAR.findall(args) if v != mm.group(1))
                elif cmd in ("if", "elseif", "once"):
                    reads |= set(_YARN_VAR.findall(args))
                elif cmd in ("else", "endif", "endonce", "stop", "wait"):
                    pass
                else:
                    commands[cmd] = commands.get(cmd, 0) + 1
                    reads |= set(_YARN_VAR.findall(args))
            # inline expressions
            for expr in re.findall(r"\{([^}]*)\}", s):
                reads |= set(_YARN_VAR.findall(expr))
            text_part = _YARN_CMD.sub("", s)
            text_part = re.sub(r"#\S+", "", text_part).strip()
            is_command_only = not text_part
            if s.startswith("->"):
                options_total += 1
                open_groups[indent] = open_groups.get(indent, 0) + 1
                if open_groups[indent] == max_options + 1:
                    rep.warn("too_many_options", where, f"more than {max_options} options in one choice group")
                opt_text = re.sub(r"\{[^}]*\}", "XXXXXXXX", text_part[2:].strip())
                if len(opt_text) > choice_budget:
                    rep.warn("choice_too_long", where, f"option is {len(opt_text)} chars (budget {choice_budget}): {opt_text[:50]!r}")
            if is_command_only:
                continue
            lines_total += 1
            ids = _YARN_LINE_ID.findall(s)
            if not ids:
                missing_ids.append(where)
            for lid in ids:
                if lid in line_ids:
                    rep.err("duplicate_line_id", where, f"#line:{lid} already used at {line_ids[lid]}")
                else:
                    line_ids[lid] = where
            if not s.startswith("->"):
                body_text = text_part[2:].strip() if text_part.startswith("=>") else text_part
                body_text = re.sub(r"^[A-Za-z][\w .'-]{0,30}:\s*", "", body_text)
                body_text = re.sub(r"\{[^}]*\}", "XXXXXXXX", body_text)
                if len(body_text) > line_budget:
                    rep.warn("line_too_long", where, f"line is {len(body_text)} chars (budget {line_budget}); split into pages")
    if missing_ids:
        rep.warn("missing_line_id", missing_ids[0], f"{len(missing_ids)} lines/options have no #line: ID "
                 f"(untranslatable; run the Yarn tagging tool). First few: {', '.join(missing_ids[:5])}")
    for v in sorted(reads - declared - writes):
        rep.warn("undeclared_var", f"${v}", "read but never declared or set in these files (the compiler may reject it, "
                 "or the game must define it)")
    for v in sorted(writes - reads):
        rep.warn("unused_var", f"${v}", "set but never read in these files")
    for v in sorted(declared - reads - writes):
        rep.warn("unused_var", f"${v}", "declared but never used")

    titles = list(by_title)
    start_title = start or ("Start" if "Start" in by_title else (titles[0] if titles else None))
    reachable: Set[str] = set()
    if start_title in by_title:
        dq = deque([start_title])
        while dq:
            cur = dq.popleft()
            if cur in reachable:
                continue
            reachable.add(cur)
            dq.extend(t for t in edges.get(cur, set()) if t in by_title and t not in reachable)
        for t in titles:
            if t not in reachable:
                rep.warn("unreachable", t, f"not reachable from '{start_title}' by jumps (fine if the game starts it directly)")
    else:
        rep.err("missing_start", str(start_title), "start node not found")
    terminal = [t for t in titles if not edges.get(t)]
    rep.metrics = {"nodes": len(nodes), "titles": len(titles), "lines": lines_total, "options": options_total,
                   "line_ids": len(line_ids), "variables": len(declared | writes), "start": start_title,
                   "reachable_from_start": len(reachable), "terminal_nodes": len(terminal),
                   "game_commands": dict(sorted(commands.items()))}
    return rep


# --------------------------------------------------------------------------------------------
# ink: knot/stitch-level subset parser
# --------------------------------------------------------------------------------------------

_INK_KNOT = re.compile(r"^\s*={2,}\s*(function\s+)?([A-Za-z_]\w*)\s*(\([^)]*\))?\s*=*\s*$")
_INK_STITCH = re.compile(r"^\s*=\s*([A-Za-z_]\w*)\s*(\([^)]*\))?\s*$")
_INK_VAR = re.compile(r"^\s*(VAR|CONST)\s+([A-Za-z_]\w*)\s*=\s*(.*)$")
_INK_LIST = re.compile(r"^\s*LIST\s+([A-Za-z_]\w*)\s*=\s*(.*)$")
_INK_DIVERT = re.compile(r"(?<![-<])->\s*(?!->)([A-Za-z_][\w.]*)")
_INK_THREAD = re.compile(r"<-\s*([A-Za-z_][\w.]*)")
_INK_LABEL = re.compile(r"^\(\s*([A-Za-z_]\w*)\s*\)")
_INK_IDENT = re.compile(r"(?<![\w.\"'])([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)?)(?![\w\"'])")
_INK_BUILTINS = {
    "true", "false", "not", "and", "or", "mod", "has", "hasnt", "TURNS", "TURNS_SINCE", "CHOICE_COUNT",
    "RANDOM", "SEED_RANDOM", "INT", "FLOOR", "CEILING", "FLOAT", "POW", "MIN", "MAX", "READ_COUNT",
    "LIST_COUNT", "LIST_MIN", "LIST_MAX", "LIST_RANDOM", "LIST_ALL", "LIST_RANGE", "LIST_INVERT",
    "LIST_VALUE", "LIST_VALUE", "END", "DONE", "temp", "return", "else", "ref", "EXTERNAL",
}


def _ink_strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)
    out = []
    for line in text.splitlines():
        line = re.sub(r"(?<!:)//.*$", "", line)
        if line.strip().startswith("TODO"):
            line = ""
        line = re.sub(r"(?<!\\)#.*$", "", line)  # tags
        out.append(line)
    return "\n".join(out)


def _ink_brace_reads(s: str) -> Set[str]:
    found: Set[str] = set()
    for inner in re.findall(r"\{([^{}]*)\}", s):
        inner = inner.strip()
        if not inner:
            continue
        if inner[0] in "&~!":
            continue  # alternatives: cycle, shuffle, once
        if ":" in inner:
            found |= set(_INK_IDENT.findall(inner.split(":", 1)[0]))
        elif "|" in inner:
            continue  # sequence of text
        else:
            found |= set(_INK_IDENT.findall(inner))
    return found


def check_ink(files: List[Tuple[str, str]], max_options: int = 4, choice_budget: int = 40) -> Report:
    rep = Report("ink")
    knots: Dict[str, Dict[str, Any]] = {}
    functions: Set[str] = set()
    labels: Dict[str, str] = {}  # qualified label -> node id
    order: List[str] = []
    declared: Set[str] = set()
    list_names: Set[str] = set()
    temps: Set[str] = set()
    reads: Dict[str, str] = {}
    assigns: Dict[str, str] = {}
    raw_edges: List[Tuple[str, str, str, Optional[str]]] = []  # node, target, where, knot
    externals: Set[str] = set()
    choices_total = 0

    def new_node(nid: str, where: str, knot: Optional[str]) -> None:
        if nid in knots:
            rep.err("duplicate_knot", where, f"'{nid}' defined more than once")
        knots[nid] = {"where": where, "knot": knot, "diverts": 0, "ends": False, "content": False,
                      "stitches": [], "choices": 0}
        order.append(nid)

    current = "__root__"
    current_knot: Optional[str] = None
    new_node(current, "start of file", None)
    choice_block: Dict[int, int] = {}
    for fname, text in files:
        clean = _ink_strip_comments(text)
        for lineno, line in enumerate(clean.splitlines(), start=1):
            where = f"{fname}:{lineno}"
            s = line.strip()
            if not s:
                continue
            if s.startswith("INCLUDE "):
                rep.info("include", where, f"INCLUDE {s[8:].strip()} - pass included files with --in to check them")
                continue
            if s.startswith("EXTERNAL "):
                mm = re.match(r"EXTERNAL\s+([A-Za-z_]\w*)", s)
                if mm:
                    externals.add(mm.group(1))
                continue
            km = _INK_KNOT.match(line)
            if km:
                name = km.group(2)
                if km.group(1):
                    functions.add(name)
                    current = f"__function__{name}"
                    current_knot = None
                    knots.setdefault(current, {"where": where, "knot": None, "diverts": 0, "ends": True,
                                               "content": True, "stitches": [], "choices": 0, "function": True})
                else:
                    current_knot = name
                    current = name
                    new_node(name, where, name)
                choice_block = {}
                continue
            sm = _INK_STITCH.match(line)
            if sm and current_knot:
                nid = f"{current_knot}.{sm.group(1)}"
                new_node(nid, where, current_knot)
                knots[current_knot]["stitches"].append(nid)
                current = nid
                choice_block = {}
                continue
            vm = _INK_VAR.match(line)
            if vm:
                declared.add(vm.group(2))
                if vm.group(3).strip().startswith("->"):
                    declared.add(vm.group(2))
                continue
            lm = _INK_LIST.match(line)
            if lm:
                list_names.add(lm.group(1))
                for item in re.findall(r"[A-Za-z_]\w*", lm.group(2)):
                    list_names.add(item)
                continue
            node = knots[current]
            # logic lines
            if s.startswith("~"):
                logic = s[1:].strip()
                tm = re.match(r"temp\s+([A-Za-z_]\w*)\s*=\s*(.*)$", logic)
                am = re.match(r"([A-Za-z_]\w*)\s*(=|\+=|-=|\+\+|--)\s*(.*)$", logic)
                rhs = logic
                if tm:
                    temps.add(tm.group(1))
                    rhs = tm.group(2)
                elif am and am.group(2) != "==":
                    assigns.setdefault(am.group(1), where)
                    if am.group(2) in ("+=", "-=", "++", "--"):
                        reads.setdefault(am.group(1), where)
                    rhs = am.group(3)
                rhs_clean = re.sub(r"\"[^\"]*\"", "", rhs)
                for ident in _INK_IDENT.findall(rhs_clean):
                    reads.setdefault(ident, where)
                node["content"] = True
                continue
            body = s
            depth = 0
            is_choice = False
            cm = re.match(r"^((?:[*+]\s*)+)", body)
            if cm:
                is_choice = True
                depth = cm.group(1).count("*") + cm.group(1).count("+")
                body = body[cm.end():].strip()
            else:
                gm = re.match(r"^((?:-(?!>)\s*)+)", body)
                if gm:
                    depth = gm.group(1).count("-")
                    for d in [k for k in choice_block if k >= depth]:
                        del choice_block[d]
                    body = body[gm.end():].strip()
            lab = _INK_LABEL.match(body)
            if lab:
                qual_base = current if current != "__root__" else ""
                labels[f"{qual_base}.{lab.group(1)}" if qual_base else lab.group(1)] = current
                if current_knot:
                    labels[f"{current_knot}.{lab.group(1)}"] = current
                labels.setdefault(lab.group(1), current)
                body = body[lab.end():].strip()
            for ident in _ink_brace_reads(body):
                reads.setdefault(ident, where)
            if is_choice:
                choices_total += 1
                node["choices"] += 1
                choice_block[depth] = choice_block.get(depth, 0) + 1
                for d in [k for k in choice_block if k > depth]:
                    del choice_block[d]
                if choice_block[depth] == max_options + 1:
                    rep.warn("too_many_options", where, f"more than {max_options} choices in one block")
                txt = re.sub(r"^\s*(\{[^}]*\}\s*)+", "", body)
                txt = txt.split("->")[0]
                shown = re.sub(r"\[([^\]]*)\].*$", r"\1", txt).strip() if "[" in txt else txt.strip()
                shown = re.sub(r"\{[^}]*\}", "XXXXXXXX", shown)
                if len(shown) > choice_budget:
                    rep.warn("choice_too_long", where, f"choice text is {len(shown)} chars (budget {choice_budget}): {shown[:50]!r}")
            for target in _INK_DIVERT.findall(body):
                if target in ("END", "DONE"):
                    node["ends"] = True
                else:
                    raw_edges.append((current, target, where, current_knot))
                node["diverts"] += 1
            if "->->" in body:
                node["ends"] = True  # tunnel return
            for target in _INK_THREAD.findall(body):
                raw_edges.append((current, target, where, current_knot))
                node["diverts"] += 1
            if re.sub(r"->.*$", "", body).strip():
                node["content"] = True

    flow_nodes = {k for k, v in knots.items() if not v.get("function")}
    edges: Dict[str, Set[str]] = {k: set() for k in flow_nodes}

    def resolve(target: str, knot: Optional[str]) -> Optional[str]:
        if knot and f"{knot}.{target}" in knots:
            return f"{knot}.{target}"
        if target in knots and target in flow_nodes:
            stitches = knots[target]["stitches"]
            if stitches and not knots[target]["content"]:
                return stitches[0]
            return target
        if target in labels:
            return labels[target]
        if knot and f"{knot}.{target}" in labels:
            return labels[f"{knot}.{target}"]
        if target in declared:
            return "__variable__"
        if target in functions:
            return "__variable__"
        return None

    for src, target, where, knot in raw_edges:
        if src not in edges:
            continue
        r = resolve(target, knot)
        if r is None:
            rep.err("missing_target", where, f"divert target '{target}' not found")
        elif r != "__variable__":
            edges[src].add(r)
    # implicit: knot with stitches and no diverts of its own flows into its first stitch
    for k in flow_nodes:
        info = knots[k]
        if info["stitches"] and info["diverts"] == 0 and not info["ends"]:
            edges[k].add(info["stitches"][0])

    for k in order:
        info = knots[k]
        if k == "__root__":
            if info["diverts"] == 0 and not info["ends"] and len(order) > 1:
                rep.warn("root_no_divert", "start of file", "the story starts at the top of the file; add '-> first_knot'")
            continue
        if info.get("function"):
            continue
        has_exit = info["diverts"] > 0 or info["ends"] or (info["stitches"] and info["diverts"] == 0)
        if not has_exit:
            rep.warn("loose_end", info["where"], f"'{k}' has no divert, END or DONE; flow will run out of content")

    reachable: Set[str] = set()
    dq = deque(["__root__"])
    while dq:
        cur = dq.popleft()
        if cur in reachable:
            continue
        reachable.add(cur)
        dq.extend(t for t in edges.get(cur, set()) if t not in reachable)
    for k in order:
        if k not in reachable and k in flow_nodes:
            rep.warn("unreachable", knots[k]["where"], f"'{k}' is not reachable by diverts from the start "
                     "(fine if the game jumps there with ChoosePathString)")

    known = (declared | temps | list_names | functions | externals | set(knots) | set(labels) |
             {k.split(".")[-1] for k in knots} | _INK_BUILTINS)
    for name, where in sorted(assigns.items()):
        if name not in declared and name not in temps:
            rep.err("undeclared_assignment", where, f"'{name}' assigned without VAR or temp (inklecate rejects this)")
    for name, where in sorted(reads.items()):
        base = name.split(".")[0]
        if name not in known and base not in known:
            rep.warn("unknown_identifier", where, f"'{name}' is not a declared variable, list, knot, label or function")
    read_names = {n.split(".")[0] for n in reads} | set(reads)
    for v in sorted(declared - read_names):
        rep.warn("unused_var", v, "declared but never read")
    rep.metrics = {"knots_and_stitches": len(flow_nodes) - 1, "functions": len(functions), "choices": choices_total,
                   "globals": len(declared), "reachable_from_start": len(reachable) - 1,
                   "endings_marked": sum(1 for k in flow_nodes if knots[k]["ends"])}
    return rep


# --------------------------------------------------------------------------------------------
# lines: string-table checks
# --------------------------------------------------------------------------------------------

DEFAULT_BUDGETS = {"button": 18, "choice": 40, "dialogue": 140, "bark": 60, "task": 28, "item": 90,
                   "toast": 50, "name": 12, "recap": 160, "push": 110, "achievement": 24}
# Widely cited IBM globalisation guideline (approximate lower bounds of each band; verify per language)
IBM_EXPANSION = [(10, 2.0), (20, 1.8), (30, 1.6), (50, 1.4), (70, 1.31), (10 ** 9, 1.3)]
_PH_NAMED = re.compile(r"\{([A-Za-z_]\w*)(?:[^}]*)\}")
_PH_POS = re.compile(r"\{\d+\}|%(?:\d+\$)?[sdif@]")


def expansion_factor(length: int, flat: Optional[float]) -> float:
    if flat:
        return flat
    for limit, factor in IBM_EXPANSION:
        if length <= limit:
            return factor
    return 1.3


def load_lines(path: Path) -> List[Dict[str, Any]]:
    text = path.read_text(encoding="utf-8-sig")
    if path.suffix.lower() == ".json":
        data = json.loads(text)
        if isinstance(data, dict) and isinstance(data.get("lines"), list):
            data = data["lines"]
        if isinstance(data, dict):
            return [{"id": k, "text": v} for k, v in data.items()]
        if isinstance(data, list):
            return [dict(r) for r in data]
        raise InputError("JSON must be a list of line objects, {'lines': [...]}, or an {id: text} map")
    return parse_lines_csv(text)


def parse_lines_csv(text: str) -> List[Dict[str, Any]]:
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames or "id" not in reader.fieldnames:
        raise InputError("CSV needs a header row with at least 'id' and 'text' (or 'text_en')")
    rows = []
    for r in reader:
        row = dict(r)
        if "text" not in row and "text_en" in row:
            row["text"] = row["text_en"]
        rows.append(row)
    return rows


def check_lines(rows: List[Dict[str, Any]], budgets: Dict[str, int], flat_expansion: Optional[float] = None) -> Report:
    rep = Report("lines")
    seen: Dict[str, int] = {}
    by_ctx: Dict[str, int] = {}
    no_budget = 0
    worst: List[Tuple[float, str]] = []
    for idx, r in enumerate(rows, start=1):
        lid = str(r.get("id") or "").strip()
        where = lid or f"row {idx}"
        if not lid:
            rep.err("missing_id", where, "line has no id")
        elif lid in seen:
            rep.err("duplicate_id", where, f"id also used on row {seen[lid]}")
        else:
            seen[lid] = idx
        text = r.get("text")
        if text is None or str(text).strip() == "":
            rep.err("missing_text", where, "empty text")
            continue
        text = str(text)
        ctx = str(r.get("context") or "").strip().lower()
        by_ctx[ctx or "(none)"] = by_ctx.get(ctx or "(none)", 0) + 1
        budget: Optional[int] = None
        mc = r.get("max_chars")
        if mc not in (None, ""):
            try:
                budget = int(mc)
            except (TypeError, ValueError):
                rep.warn("bad_max_chars", where, f"max_chars is not an integer: {mc!r}")
        if budget is None and ctx in budgets:
            budget = budgets[ctx]
        n = len(text)
        if budget is None:
            no_budget += 1
        else:
            factor = expansion_factor(n, flat_expansion)
            expanded = math.ceil(n * factor)
            worst.append((expanded / budget, where))
            if n > budget:
                rep.err("over_budget", where, f"{n} chars exceeds the {budget}-char budget before translation")
            elif expanded > budget:
                rep.warn("expansion_risk", where, f"{n} chars x{factor:.2f} = {expanded} > {budget}; shorten to <= "
                         f"{int(budget / factor)} chars")
        if text != text.strip():
            rep.warn("concat_smell", where, "leading/trailing whitespace suggests the line is concatenated with other strings")
        if re.search(r"\w\(s\)", text):
            rep.warn("plural_hack", where, "'(s)' plural hack; use plural forms (CLDR categories) instead")
        if re.search(r"\b(he/she|she/he|him/her|her/him|his/her|her/his)\b", text, re.I):
            rep.warn("gender_slash", where, "slash-gendered text; use neutral phrasing or gendered variants")
        if _PH_POS.search(text):
            rep.warn("positional_placeholder", where, "positional placeholder (%s, {0}); prefer named placeholders with translator notes")
        found = set(_PH_NAMED.findall(text))
        declared_ph = r.get("placeholders")
        if declared_ph not in (None, ""):
            names = {p.split(":")[0].strip() for p in str(declared_ph).replace(";", ",").split(",") if p.strip()}
            if names != found:
                rep.err("placeholder_mismatch", where, f"declared {sorted(names)} but text uses {sorted(found)}")
        caps = [w for w in re.findall(r"\b[A-Z]{4,}\b", text)]
        if caps:
            rep.info("all_caps", where, f"all-caps words {caps[:3]} hurt readability; use emphasis styling sparingly")
    worst.sort(reverse=True)
    rep.metrics = {"lines": len(rows), "by_context": dict(sorted(by_ctx.items())), "no_budget": no_budget,
                   "expansion": f"flat x{flat_expansion}" if flat_expansion else "IBM length-based table",
                   "tightest": [f"{w} ({ratio:.0%} of budget after expansion)" for ratio, w in worst[:5]]}
    if no_budget:
        rep.info("no_budget", "lines", f"{no_budget} lines have no max_chars and no known context; length not checked")
    return rep


# --------------------------------------------------------------------------------------------
# cost model
# --------------------------------------------------------------------------------------------


def cost_model(a: argparse.Namespace) -> Dict[str, Any]:
    s = a.structure
    W = float(a.words_per_node)
    res: Dict[str, Any] = {"structure": s, "words_per_node": W}
    if s == "linear":
        N, K, V, Wv = a.scenes, a.branch_points, a.options, float(a.words_per_variant)
        unique_words = N * W + K * V * Wv
        run_words = N * W + K * Wv
        res.update(unique_nodes=N, variant_lines=K * V, nodes_per_run=N, endings=1,
                   total_words=unique_words, words_per_run=run_words)
    elif s == "tree":
        B, D = a.options, a.depth
        unique = D + 1 if B == 1 else (B ** (D + 1) - 1) // (B - 1)
        res.update(unique_nodes=unique, nodes_per_run=D + 1, endings=B ** D,
                   total_words=unique * W, words_per_run=(D + 1) * W)
    elif s == "bnb":
        K, B, L = a.branch_points, a.options, a.branch_length
        unique = K * B * L + (K + 1)
        per = K * L + K + 1
        res.update(unique_nodes=unique, nodes_per_run=per, endings=1, total_words=unique * W, words_per_run=per * W)
    elif s == "gauntlet":
        N, F, L = a.scenes, a.failure_branches, a.branch_length
        res.update(unique_nodes=N + F * L, nodes_per_run=N, endings=1 + F,
                   total_words=(N + F * L) * W, words_per_run=N * W)
    elif s == "hub":
        S_, L = a.spokes, a.branch_length
        unique = 1 + S_ * L
        res.update(unique_nodes=unique, nodes_per_run=unique, endings=1, total_words=unique * W,
                   words_per_run=unique * W, visit_orders=math.factorial(S_) if S_ <= 20 else "huge")
    elif s == "routes":
        N, R, L = a.scenes, a.routes, a.branch_length
        res.update(unique_nodes=N + R * L, nodes_per_run=N + L, endings=R,
                   total_words=(N + R * L) * W, words_per_run=(N + L) * W)
    elif s == "storylets":
        N, R = a.pool, a.draws
        if R > N:
            raise InputError("--draws cannot exceed --pool")
        share = R / N
        runs90 = math.ceil(math.log(0.1) / math.log(1 - share)) if share < 1 else 1
        res.update(unique_nodes=N, nodes_per_run=R, endings="emergent", total_words=N * W, words_per_run=R * W,
                   runs_to_see_90pct_of_pool=runs90)
    else:
        raise InputError(f"unknown structure {s}")
    tw, rw = float(res["total_words"]), float(res["words_per_run"])
    res["total_words"] = int(round(tw))
    res["words_per_run"] = int(round(rw))
    res["share_seen_per_run"] = round(rw / tw, 4) if tw else 0.0
    if a.locales and a.locales > 1:
        res["translation_words"] = int(round(tw * (a.locales - 1)))
    if a.words_per_day:
        res["writer_days_first_draft"] = round(tw / a.words_per_day, 1)
        res["note"] = "writer_days uses your --words-per-day; revision, review and implementation are extra"
    if a.vo_usd_per_1k_chars:
        chars = tw * a.chars_per_word
        res["vo_usd_per_locale_one_pass"] = round(chars / 1000 * a.vo_usd_per_1k_chars, 2)
    return res


# --------------------------------------------------------------------------------------------
# bark repetition maths
# --------------------------------------------------------------------------------------------


def p_no_repeat(n: int, k: int) -> float:
    if k > n:
        return 0.0
    p = 1.0
    for i in range(k):
        p *= (n - i) / n
    return p


def bark_model(pool: int, triggers: float, prob: float = 1.0, sessions: int = 1) -> Dict[str, Any]:
    if pool < 1 or triggers < 0 or not (0 < prob <= 1) or sessions < 1:
        raise InputError("need --pool >= 1, --triggers >= 0, 0 < --prob <= 1, --sessions >= 1")
    te = triggers * prob
    distinct = pool * (1 - (1 - 1 / pool) ** te)
    k = int(round(te))
    min_pool_half = 1
    while p_no_repeat(min_pool_half, k) < 0.5 and min_pool_half < 100000:
        min_pool_half += 1
    return {
        "pool": pool, "triggers_per_session": triggers, "fire_probability": prob,
        "expected_barks_per_session": round(te, 2),
        "random": {"expected_distinct": round(distinct, 2), "expected_repeats": round(te - distinct, 2),
                   "p_no_repeat_in_session": round(p_no_repeat(pool, k), 4)},
        "shuffle_bag": {"expected_repeats": round(max(0.0, te - pool), 2)},
        "recommend": {"pool_for_zero_repeats_with_shuffle_bag": math.ceil(te),
                      "pool_for_50pct_no_repeat_with_random": min_pool_half},
        "hearings_per_line_over_sessions": round(te * sessions / pool, 2),
    }


# --------------------------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------------------------


def parse_budgets(spec: Optional[str]) -> Dict[str, int]:
    budgets = dict(DEFAULT_BUDGETS)
    if spec:
        for part in spec.split(","):
            if not part.strip():
                continue
            if "=" not in part:
                raise InputError(f"bad --budgets entry {part!r}; use context=chars")
            k, v = part.split("=", 1)
            budgets[k.strip().lower()] = int(v)
    return budgets


def read_files(paths: Iterable[str]) -> List[Tuple[str, str]]:
    out = []
    for p in paths:
        path = Path(p)
        if not path.is_file():
            raise InputError(f"file not found: {p}")
        out.append((path.name, path.read_text(encoding="utf-8-sig")))
    return out


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description="Narrative content checks: graphs, Yarn, ink, string tables, cost and bark maths.")
    ap.add_argument("--selftest", action="store_true", help="run built-in tests and exit")
    ap.add_argument("--version", action="version", version=VERSION)
    sub = ap.add_subparsers(dest="cmd")

    g = sub.add_parser("graph", help="state-aware checks of a JSON narrative graph")
    g.add_argument("--story", required=True)
    g.add_argument("--max-states", type=int, default=50000)
    g.add_argument("--max-options", type=int, default=4)
    g.add_argument("--var-budget", type=int, default=20)

    y = sub.add_parser("yarn", help="structural checks of .yarn files")
    y.add_argument("--in", dest="inputs", nargs="+", required=True)
    y.add_argument("--start")
    y.add_argument("--max-options", type=int, default=4)
    y.add_argument("--choice-budget", type=int, default=40)
    y.add_argument("--line-budget", type=int, default=140)

    i = sub.add_parser("ink", help="structural checks of .ink files")
    i.add_argument("--in", dest="inputs", nargs="+", required=True)
    i.add_argument("--max-options", type=int, default=4)
    i.add_argument("--choice-budget", type=int, default=40)

    l = sub.add_parser("lines", help="string-table checks (CSV or JSON)")
    l.add_argument("--in", dest="inputs", required=True)
    l.add_argument("--expansion", type=float, help="flat expansion factor (default: IBM length-based table)")
    l.add_argument("--budgets", help="override context budgets, e.g. bark=50,choice=36")

    c = sub.add_parser("cost", help="content-cost model for branching structures")
    c.add_argument("--structure", required=True, choices=["linear", "tree", "bnb", "gauntlet", "hub", "routes", "storylets"])
    c.add_argument("--scenes", type=int, default=10, help="linear/gauntlet scenes or routes trunk scenes")
    c.add_argument("--branch-points", type=int, default=10)
    c.add_argument("--options", type=int, default=3)
    c.add_argument("--depth", type=int, default=5)
    c.add_argument("--branch-length", type=int, default=2, help="scenes per branch/failure branch/spoke/route")
    c.add_argument("--failure-branches", type=int, default=3)
    c.add_argument("--spokes", type=int, default=4)
    c.add_argument("--routes", type=int, default=3)
    c.add_argument("--pool", type=int, default=200)
    c.add_argument("--draws", type=int, default=30)
    c.add_argument("--words-per-node", type=float, default=150)
    c.add_argument("--words-per-variant", type=float, default=20)
    c.add_argument("--words-per-day", type=float, help="your measured first-draft rate (no default by design)")
    c.add_argument("--locales", type=int, default=1)
    c.add_argument("--chars-per-word", type=float, default=5.5)
    c.add_argument("--vo-usd-per-1k-chars", type=float, help="TTS/VO list rate to estimate one pass per locale")

    b = sub.add_parser("barks", help="repetition maths for a bark pool")
    b.add_argument("--pool", type=int, required=True)
    b.add_argument("--triggers", type=float, required=True, help="eligible triggers per session")
    b.add_argument("--prob", type=float, default=1.0, help="chance a bark fires when eligible")
    b.add_argument("--sessions", type=int, default=1)

    for p in (g, y, i, l, c, b):
        p.add_argument("--json", action="store_true", help="machine-readable output")
        p.add_argument("--strict", action="store_true", help="treat warnings as failures")
    return ap


def main(argv: Optional[List[str]] = None) -> int:
    ap = build_parser()
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.cmd:
        ap.print_help()
        return 2
    try:
        if a.cmd == "graph":
            path = Path(a.story)
            if not path.is_file():
                raise InputError(f"file not found: {a.story}")
            try:
                doc = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as ex:
                raise InputError(f"invalid JSON: {ex}")
            return emit(check_graph(doc, a.max_states, a.max_options, a.var_budget), a.json, a.strict)
        if a.cmd == "yarn":
            return emit(check_yarn(read_files(a.inputs), a.start, a.max_options, a.choice_budget, a.line_budget), a.json, a.strict)
        if a.cmd == "ink":
            return emit(check_ink(read_files(a.inputs), a.max_options, a.choice_budget), a.json, a.strict)
        if a.cmd == "lines":
            path = Path(a.inputs)
            if not path.is_file():
                raise InputError(f"file not found: {a.inputs}")
            return emit(check_lines(load_lines(path), parse_budgets(a.budgets), a.expansion), a.json, a.strict)
        if a.cmd == "cost":
            res = cost_model(a)
            print(json.dumps(res, indent=2) if a.json else "\n".join(f"{k}: {v}" for k, v in res.items()))
            return 0
        if a.cmd == "barks":
            res = bark_model(a.pool, a.triggers, a.prob, a.sessions)
            print(json.dumps(res, indent=2) if a.json else _render_nested(res))
            return 0
    except InputError as ex:
        print(f"error: {ex}", file=sys.stderr)
        return 2
    except (ValueError, OSError) as ex:
        print(f"error: {ex}", file=sys.stderr)
        return 2
    return 2


def _render_nested(d: Dict[str, Any], indent: int = 0) -> str:
    out = []
    for k, v in d.items():
        if isinstance(v, dict):
            out.append(" " * indent + f"{k}:")
            out.append(_render_nested(v, indent + 2))
        else:
            out.append(" " * indent + f"{k}: {v}")
    return "\n".join(out)


# --------------------------------------------------------------------------------------------
# self-test
# --------------------------------------------------------------------------------------------

_GOOD_GRAPH = {
    "schema_version": "1.0", "start": "dock",
    "variables": {"trust_hale": 0, "has_key": False},
    "nodes": [
        {"id": "dock", "words": 40, "edges": [
            {"to": "fixed", "label": "Offer to fix it", "set": {"trust_hale": "+1"}},
            {"to": "dock", "label": "Ask about Grandma", "once": True},
            {"to": "beach", "label": "Search the beach", "set": {"has_key": True}}]},
        {"id": "beach", "words": 20, "edges": [{"to": "key", "label": "Show the key", "if": "has_key"}]},
        {"id": "fixed", "words": 25, "edges": [{"to": "end", "if": "trust_hale >= 1"}]},
        {"id": "key", "words": 30, "edges": [{"to": "end"}]},
        {"id": "end", "words": 10, "ending": True}]}

_BAD_GRAPH = {
    "schema_version": "1.0", "start": "a",
    "variables": {"gold": 0, "unused_flag": False},
    "nodes": [
        {"id": "a", "edges": [{"to": "b"}, {"to": "ghost"}, {"to": "locked", "if": "gold >= 5"}]},
        {"id": "b", "edges": [{"to": "c", "if": "met_ada", "set": {"orphan": 1}}]},
        {"id": "c", "edges": []},
        {"id": "locked", "ending": True},
        {"id": "island", "ending": True}]}

_BNB_GRAPH = {
    "schema_version": "1.0", "start": "s",
    "nodes": [
        {"id": "s", "words": 100, "edges": [{"to": "a1", "label": "A"}, {"to": "a2", "label": "B"}]},
        {"id": "a1", "words": 100, "edges": [{"to": "m"}]},
        {"id": "a2", "words": 100, "edges": [{"to": "m"}]},
        {"id": "m", "words": 100, "edges": [{"to": "b1", "label": "C"}, {"to": "b2", "label": "D"}]},
        {"id": "b1", "words": 100, "edges": [{"to": "e"}]},
        {"id": "b2", "words": 100, "edges": [{"to": "e"}]},
        {"id": "e", "words": 100, "ending": True}]}

_YARN = """title: Start
---
<<declare $trust = 0>>
Hale: Crane's been rusted shut since the storm. #line:a001
-> Offer to fix it #line:a002
    <<set $trust to $trust + 1>>
    <<jump Fixed>>
-> Ask about Grandma #line:a003
    Hale: Later. #line:a001
    <<jump Nowhere>>
-> Leave
    Maya: Fine.
===
title: Fixed
---
<<if $trust > 0>>
Hale: Not bad. #line:a004
<<endif>>
===
title: Orphan
---
Pip: Mrrp. #line:a005
===
title: Bark
when: $trust >= 3
---
Hale: You're all right. #line:a006
===
title: Bark
when: $trust < 3
---
Hale: Mind the nets. #line:a007
===
"""

_INK = """VAR trust = 0
VAR never_read = 1
-> dock

=== dock ===
Crane's rusted. #speaker:hale
* [Offer to fix it]
    ~ trust = trust + 1
    -> fixed
* [Ask about Grandma] -> dock
* [Leave] -> missing_knot
* [Wait]
* [Whistle] -> dock
~ mood = 3

=== fixed ===
{trust > 0: Not bad.|Huh.}
-> DONE

=== orphan ===
Never visited.
"""

_LINES_CSV = """id,context,text,max_chars,placeholders
a1,choice,Offer to fix it,,
a1,dialogue,Duplicate id here,,
a2,button,Collect all your rewards now,,
a3,toast,You found %s shells,,
a4,dialogue,"You found {count} shell(s) ",,count
a5,bark,Nice!,,
a6,dialogue,Tell him/her the truth,,
a7,dialogue,"Hello {player}",,name
"""


def selftest() -> int:
    failures: List[str] = []

    def check(cond: bool, msg: str) -> None:
        if not cond:
            failures.append(msg)

    # expression language
    ast = parse_condition("trust >= 2 and not has_key or $mood == 'calm'")
    check(eval_condition(ast, {"trust": 3, "has_key": False}) is True, "expr: and/not")
    check(eval_condition(ast, {"trust": 1, "has_key": False, "mood": "calm"}) is True, "expr: or/string")
    check(condition_vars(ast) == {"trust", "has_key", "mood"}, "expr: vars")
    try:
        parse_condition("trust >= ")
        failures.append("expr: incomplete condition should raise")
    except InputError:
        pass

    good = check_graph(_GOOD_GRAPH)
    check(good.ok(), f"good graph should pass: {good.findings}")
    check(good.metrics.get("bottlenecks") == [], f"good graph bottlenecks: {good.metrics.get('bottlenecks')}")
    check(good.metrics.get("cyclic") is True, "good graph has a self-loop (cyclic)")

    bad = check_graph(_BAD_GRAPH)
    for code in ("missing_target", "unreachable", "dead_end", "softlock", "undeclared_var", "unused_var",
                 "conditionally_unreachable"):
        check(code in bad.codes(), f"bad graph should report {code}: {sorted(bad.codes())}")
    check(not bad.ok(), "bad graph must fail")

    bnb = check_graph(_BNB_GRAPH)
    check(bnb.ok(), f"bnb graph should pass: {bnb.findings}")
    check(bnb.metrics.get("bottlenecks") == ["m"], f"bnb bottleneck should be m: {bnb.metrics.get('bottlenecks')}")
    check(bnb.metrics.get("paths") == 4, f"bnb paths should be 4: {bnb.metrics.get('paths')}")
    check(abs(bnb.metrics.get("share_seen_per_run", 0) - 5 / 7) < 0.01, f"bnb share: {bnb.metrics.get('share_seen_per_run')}")

    yr = check_yarn([("test.yarn", _YARN)])
    for code in ("missing_target", "duplicate_line_id", "missing_line_id", "unreachable"):
        check(code in yr.codes(), f"yarn should report {code}: {sorted(yr.codes())}")
    check("duplicate_node" not in yr.codes(), "yarn node group with when: must not be a duplicate")
    check(yr.metrics.get("titles") == 4, f"yarn titles: {yr.metrics.get('titles')}")

    ik = check_ink([("test.ink", _INK)], max_options=4)
    for code in ("missing_target", "undeclared_assignment", "unused_var", "too_many_options", "unreachable", "loose_end"):
        check(code in ik.codes(), f"ink should report {code}: {sorted(ik.codes())}")
    check("unknown_identifier" not in ik.codes() or all(f["where"] for f in ik.findings), "ink identifier check ran")

    ln = check_lines(parse_lines_csv(_LINES_CSV), dict(DEFAULT_BUDGETS))
    for code in ("duplicate_id", "over_budget", "positional_placeholder", "concat_smell", "plural_hack",
                 "gender_slash", "placeholder_mismatch"):
        check(code in ln.codes(), f"lines should report {code}: {sorted(ln.codes())}")
    check(expansion_factor(5, None) == 2.0 and expansion_factor(100, None) == 1.3, "IBM expansion bands")

    ns = argparse.Namespace(structure="tree", options=3, depth=10, words_per_node=150, locales=1,
                            words_per_day=None, vo_usd_per_1k_chars=None, chars_per_word=5.5)
    tree = cost_model(ns)
    check(tree["unique_nodes"] == 88573 and tree["endings"] == 59049, f"tree cost: {tree}")
    ns2 = argparse.Namespace(structure="bnb", branch_points=10, options=3, branch_length=2, words_per_node=150,
                             locales=3, words_per_day=1500, vo_usd_per_1k_chars=0.08, chars_per_word=5.5)
    bnbc = cost_model(ns2)
    check(bnbc["unique_nodes"] == 71 and bnbc["nodes_per_run"] == 31, f"bnb cost: {bnbc}")
    check(bnbc["translation_words"] == 21300 and bnbc["writer_days_first_draft"] == 7.1, f"bnb extras: {bnbc}")
    check(abs(bnbc["vo_usd_per_locale_one_pass"] - 4.69) < 0.01, f"bnb vo: {bnbc}")

    bk = bark_model(10, 5)
    check(abs(bk["random"]["p_no_repeat_in_session"] - 0.3024) < 1e-3, f"birthday maths: {bk}")
    bk2 = bark_model(12, 12)
    check(abs(bk2["random"]["expected_repeats"] - 4.22) < 0.02, f"repeat maths: {bk2}")
    check(bk2["shuffle_bag"]["expected_repeats"] == 0, "shuffle bag repeats")

    # CLI round trip through files
    with tempfile.TemporaryDirectory() as td:
        gp = Path(td) / "g.json"
        gp.write_text(json.dumps(_GOOD_GRAPH), encoding="utf-8")
        check(main(["graph", "--story", str(gp), "--json"]) == 0, "CLI graph good -> 0")
        bp = Path(td) / "b.json"
        bp.write_text(json.dumps(_BAD_GRAPH), encoding="utf-8")
        check(main(["graph", "--story", str(bp)]) == 1, "CLI graph bad -> 1")
        check(main(["graph", "--story", str(Path(td) / "missing.json")]) == 2, "CLI missing file -> 2")
        lp = Path(td) / "l.json"
        lp.write_text(json.dumps({"lines": [{"id": "x", "text": "Fix the dock crane", "context": "task"}]}), encoding="utf-8")
        check(main(["lines", "--in", str(lp)]) == 0, "CLI lines json -> 0")

    if failures:
        print("SELFTEST FAILED", file=sys.stderr)
        for f in failures:
            print("  - " + f, file=sys.stderr)
        return 1
    print("narrative_lint selftest: OK")
    return 0


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows pipes default to the ANSI code page; Claude Code reads UTF-8
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
