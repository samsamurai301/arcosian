#!/usr/bin/env python3
"""Analytics event taxonomy: generate from a design contract, emit engine stubs, validate names.

  event_taxonomy.py generate --contract PATH --out PATH
  event_taxonomy.py stubs --taxonomy PATH --engine godot|unity --out DIR

generate: standard lifecycle / FTUE / progression / economy / ads / monetization / liveops events,
          with enums taken from the contract (currencies, FTUE steps, IAP ids, ad placements).
stubs:    godot -> analytics_events.gd (typed static functions calling Analytics.log_event)
          unity -> AnalyticsEvents.cs (static class with a pluggable Sink delegate)
Rules checked on both: snake_case names, <= 40 chars, no reserved prefix, <= 25 params per event
(common params included), unique event names. Exit 0 ok, 1 rule violations, 2 usage/input error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

NAME_RE = re.compile(r"^(?!firebase_|google_|ga_)[a-z][a-z0-9_]{0,39}$")
MAX_PARAMS = 25
TYPES = ("string", "int", "float", "bool", "timestamp")
GD_TYPE = {"string": "String", "int": "int", "float": "float", "bool": "bool", "timestamp": "int"}
CS_TYPE = {"string": "string", "int": "int", "float": "float", "bool": "bool", "timestamp": "long"}
GD_RESERVED = {"as", "break", "class", "const", "continue", "elif", "else", "enum", "extends", "for", "func",
               "if", "in", "is", "match", "pass", "return", "self", "signal", "static", "super", "var", "void",
               "while", "await", "true", "false", "null", "and", "or", "not"}
CS_RESERVED = {"abstract", "as", "base", "bool", "break", "byte", "case", "catch", "char", "checked", "class",
               "const", "continue", "decimal", "default", "delegate", "do", "double", "else", "enum", "event",
               "explicit", "extern", "false", "finally", "fixed", "float", "for", "foreach", "goto", "if",
               "implicit", "in", "int", "interface", "internal", "is", "lock", "long", "namespace", "new",
               "null", "object", "operator", "out", "override", "params", "private", "protected", "public",
               "readonly", "ref", "return", "sbyte", "sealed", "short", "sizeof", "static", "string", "struct",
               "switch", "this", "throw", "true", "try", "typeof", "uint", "ulong", "unchecked", "unsafe",
               "ushort", "using", "virtual", "void", "volatile", "while"}


class InputError(Exception):
    pass


def P(name: str, typ: str, desc: str, required: bool = True, enum: Optional[List[Any]] = None) -> Dict[str, Any]:
    d: Dict[str, Any] = {"name": name, "type": typ, "required": required, "description": desc}
    if enum:
        d["enum"] = enum
    return d


def ids_of(items: Any) -> List[str]:
    out = []
    for it in items or []:
        v = it.get("id") if isinstance(it, dict) else it
        if isinstance(v, str) and v:
            out.append(v)
    return out


def generate(contract: Dict[str, Any]) -> Dict[str, Any]:
    meta = contract.get("meta", {})
    kp = (contract.get("analytics") or {}).get("kpi_targets") or {}
    ftue_steps = ids_of((contract.get("ftue") or {}).get("steps"))
    currencies = ids_of((contract.get("economy") or {}).get("currencies"))
    mon = contract.get("monetization") or {}
    iaps = ids_of(mon.get("iap"))
    placements = ids_of((mon.get("ads") or {}).get("rewarded"))
    liveops = ids_of((contract.get("liveops") or {}).get("events"))
    has_inter = (mon.get("ads") or {}).get("interstitial") is not None
    has_social = any(l.get("type") == "social" for l in contract.get("loops", []))
    target_aha = (contract.get("ftue") or {}).get("aha_seconds_target")
    core_kpis = [k for k in ("d1", "d7", "d30", "session_len_sec", "sessions_per_day") if k in kp]

    ev: List[Dict[str, Any]] = [
        {"name": "session_start", "category": "lifecycle", "trigger": "app becomes active after launch or after 30 min in background",
         "params": [P("is_first_session", "bool", "True on the first session after install.")], "kpis": core_kpis or ["d1"]},
        {"name": "session_end", "category": "lifecycle", "trigger": "app goes to background or is closed (send on next launch if killed)",
         "params": [P("duration_sec", "float", "Foreground seconds in this session.")], "kpis": ["session_len_sec", "sessions_per_day"]},
        {"name": "tutorial_begin", "category": "ftue", "trigger": "first frame of the first playable moment on a fresh install",
         "params": [], "kpis": ["ftue_funnel"]},
        {"name": "tutorial_step", "category": "ftue", "trigger": "each FTUE step completed (contract ftue.steps)",
         "params": [P("step_id", "string", "FTUE step id.", enum=ftue_steps or None),
                    P("seconds_since_install", "float", "Seconds since first launch%s." % (
                        "; feeds the aha-time target (%ss)" % target_aha if target_aha else ""))],
         "kpis": ["ftue_funnel", "aha_seconds"]},
        {"name": "tutorial_complete", "category": "ftue", "trigger": "last FTUE step completed",
         "params": [P("seconds_since_install", "float", "Seconds since first launch.")], "kpis": ["ftue_funnel", "d1"]},
        {"name": "level_start", "category": "progression", "trigger": "level begins (after any pre-level screen)",
         "params": [P("level_id", "string", "Level id from the level spec."),
                    P("attempt", "int", "Attempt number on this level, starting at 1.")], "kpis": ["level_funnel"]},
        {"name": "level_end", "category": "progression", "trigger": "results screen shown, or the player quits a level",
         "params": [P("level_id", "string", "Level id."), P("attempt", "int", "Attempt number."),
                    P("success", "bool", "True on win."),
                    P("reason", "string", "How it ended.", enum=["win", "fail", "quit"]),
                    P("duration_sec", "float", "Level time excluding pauses."),
                    P("moves_used", "int", "Moves or actions used.", required=False)],
         "kpis": ["level_win_rate", "attempts_p50", "churn_by_level"]},
    ]
    cur_enum = currencies or None
    ev.append({"name": "earn_virtual_currency", "category": "economy", "trigger": "any currency grant",
               "params": [P("virtual_currency_name", "string", "Currency id.", enum=cur_enum),
                          P("value", "int", "Amount granted."),
                          P("source", "string", "Economy node id that granted it.")], "kpis": ["economy_balance"]})
    ev.append({"name": "spend_virtual_currency", "category": "economy", "trigger": "any currency spend",
               "params": [P("virtual_currency_name", "string", "Currency id.", enum=cur_enum),
                          P("value", "int", "Amount spent."), P("item_name", "string", "Sink id.")],
               "kpis": ["economy_balance"]})
    if placements:
        ev.append({"name": "rv_offer_shown", "category": "ads", "trigger": "a rewarded-ad offer becomes visible",
                   "params": [P("placement", "string", "Placement id.", enum=placements)], "kpis": ["rv_opt_in_rate"]})
        ev.append({"name": "rv_completed", "category": "ads", "trigger": "the ad SDK confirms the reward",
                   "params": [P("placement", "string", "Placement id.", enum=placements),
                              P("network", "string", "Mediation network that served the ad.", required=False)],
                   "kpis": ["rv_opt_in_rate", "arpdau_usd"]})
    if has_inter:
        ev.append({"name": "interstitial_shown", "category": "ads", "trigger": "an interstitial ad is displayed",
                   "params": [P("placement", "string", "Where in the flow it appeared.")], "kpis": ["arpdau_usd"]})
    if iaps:
        ev.append({"name": "iap_offer_shown", "category": "monetization", "trigger": "an IAP offer or the shop becomes visible",
                   "params": [P("product_id", "string", "IAP product id.", enum=iaps),
                              P("surface", "string", "Screen or trigger that showed it.")], "kpis": ["payer_conversion"]})
        ev.append({"name": "iap_purchase", "category": "monetization", "trigger": "store confirms a successful purchase",
                   "params": [P("product_id", "string", "IAP product id.", enum=iaps),
                              P("price_usd_cents", "int", "Price in USD cents (minor units)."),
                              P("is_first_purchase", "bool", "True on the player's first purchase.")],
                   "kpis": ["payer_conversion", "arpdau_usd"]})
    if liveops:
        ev.append({"name": "liveops_event_join", "category": "liveops", "trigger": "player first engages with a live event",
                   "params": [P("event_id", "string", "Live event id.", enum=liveops)], "kpis": ["event_participation"]})
    if has_social:
        ev.append({"name": "social_action", "category": "social", "trigger": "player invites, gifts or joins a group",
                   "params": [P("action", "string", "What the player did.", enum=["invite", "gift", "join", "leave"])],
                   "kpis": ["social_engagement"]})
    ev.append({"name": "tech_error", "category": "tech", "trigger": "a handled error or soft-lock recovery occurs",
               "params": [P("code", "string", "Short error code."), P("screen", "string", "Screen or state.", required=False)],
               "kpis": ["crash_free"]})
    return {
        "schema_version": "1.0", "naming": "snake_case",
        "common_params": [P("session_id", "string", "Random id per app session."),
                          P("build", "string", "App version plus build number."),
                          P("player_level", "int", "Highest level reached."),
                          P("ab_cohort", "string", "Active experiment cohorts, comma-separated.", required=False)],
        "events": ev, "$comment": "Draft for %s: add game-specific events, then re-run validation." % (meta.get("title") or "game"),
    }


def check(tax: Dict[str, Any]) -> List[str]:
    errs: List[str] = []
    if tax.get("naming", "snake_case") != "snake_case":
        errs.append("naming must be snake_case")
    common = tax.get("common_params") or []
    for c in common:
        if not NAME_RE.match(str(c.get("name", ""))):
            errs.append("common param '%s': invalid name" % c.get("name"))
    seen = set()
    for e in tax.get("events") or []:
        n = str(e.get("name", ""))
        if not NAME_RE.match(n):
            errs.append("event '%s': name must be snake_case, start with a letter, <= 40 chars, no firebase_/google_/ga_ prefix" % n)
        if n in seen:
            errs.append("event '%s': duplicate" % n)
        seen.add(n)
        params = e.get("params") or []
        if len(params) + len(common) > MAX_PARAMS:
            errs.append("event '%s': %d params + %d common > %d" % (n, len(params), len(common), MAX_PARAMS))
        pn = set(c.get("name") for c in common)
        for p in params:
            if not NAME_RE.match(str(p.get("name", ""))):
                errs.append("event '%s' param '%s': invalid name" % (n, p.get("name")))
            if p.get("type") not in TYPES:
                errs.append("event '%s' param '%s': type must be one of %s" % (n, p.get("name"), "/".join(TYPES)))
            if p.get("name") in pn:
                errs.append("event '%s' param '%s': duplicate (or clashes with a common param)" % (n, p.get("name")))
            pn.add(p.get("name"))
    if not tax.get("events"):
        errs.append("no events")
    return errs


def _gd_literal(v: Any) -> str:
    return json.dumps(v) if isinstance(v, str) else str(v)


def _camel(s: str, upper: bool) -> str:
    parts = s.split("_")
    out = "".join(p[:1].upper() + p[1:] for p in parts)
    return out if upper else out[:1].lower() + out[1:]


def godot_stubs(tax: Dict[str, Any]) -> str:
    L = ["# Generated by event_taxonomy.py from the analytics taxonomy. Do not edit by hand; regenerate.",
         "# Requires an autoload named Analytics with: func log_event(name: String, params: Dictionary) -> void",
         "# (the wrapper adds common params: %s)." % ", ".join(c["name"] for c in tax.get("common_params", [])),
         "class_name AnalyticsEvents", "extends RefCounted", ""]
    for e in tax["events"]:
        req = [p for p in e.get("params", []) if p.get("required", True)]
        opt = [p for p in e.get("params", []) if not p.get("required", True)]
        arg = lambda p: p["name"] + "_" if p["name"] in GD_RESERVED else p["name"]
        sig = ["%s: %s" % (arg(p), GD_TYPE[p["type"]]) for p in req] + ["%s: Variant = null" % arg(p) for p in opt]
        L.append("## %s" % e.get("trigger", e["name"]))
        L.append("static func log_%s(%s) -> void:" % (e["name"], ", ".join(sig)))
        for p in e.get("params", []):
            if p.get("enum") and p.get("required", True):
                L.append("\tassert(%s in [%s], \"%s: unexpected value\")" % (
                    arg(p), ", ".join(_gd_literal(x) for x in p["enum"]), p["name"]))
        if req or opt:
            L.append("\tvar params: Dictionary = {%s}" % ", ".join('"%s": %s' % (p["name"], arg(p)) for p in req))
            for p in opt:
                L.append("\tif %s != null:" % arg(p))
                L.append("\t\tparams[\"%s\"] = %s" % (p["name"], arg(p)))
            L.append("\tAnalytics.log_event(\"%s\", params)" % e["name"])
        else:
            L.append("\tAnalytics.log_event(\"%s\", {})" % e["name"])
        L.append("")
    return "\n".join(L)


def unity_stubs(tax: Dict[str, Any]) -> str:
    L = ["// Generated by event_taxonomy.py from the analytics taxonomy. Do not edit by hand; regenerate.",
         "// Assign AnalyticsEvents.Sink once at startup (it should add common params: %s)." % ", ".join(
             c["name"] for c in tax.get("common_params", [])),
         "#nullable enable", "using System;", "using System.Collections.Generic;", "", "public static class AnalyticsEvents", "{",
         "    public static Action<string, Dictionary<string, object>> Sink = (name, parameters) => { };", ""]
    for e in tax["events"]:
        req = [p for p in e.get("params", []) if p.get("required", True)]
        opt = [p for p in e.get("params", []) if not p.get("required", True)]

        def arg(p: Dict[str, Any]) -> str:
            a = _camel(p["name"], False)
            return "@" + a if a in CS_RESERVED else a
        sig = ["%s %s" % (CS_TYPE[p["type"]], arg(p)) for p in req]
        sig += ["%s? %s = null" % (CS_TYPE[p["type"]], arg(p)) for p in opt]
        L.append("    /// <summary>%s</summary>" % e.get("trigger", e["name"]).replace("&", "&amp;").replace("<", "&lt;"))
        L.append("    public static void Log%s(%s)" % (_camel(e["name"], True), ", ".join(sig)))
        L.append("    {")
        L.append("        var p = new Dictionary<string, object>();")
        for p in req:
            L.append("        p[\"%s\"] = %s;" % (p["name"], arg(p)))
        for p in opt:
            L.append("        if (%s != null) p[\"%s\"] = %s;" % (arg(p), p["name"], arg(p)))
        L.append("        Sink(\"%s\", p);" % e["name"])
        L.append("    }")
        L.append("")
    L.append("}")
    return "\n".join(L) + "\n"


def read_json(path: str) -> Dict[str, Any]:
    try:
        d = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise InputError("cannot read %s: %s" % (path, e))
    if not isinstance(d, dict):
        raise InputError("%s: expected a JSON object" % path)
    return d


def selftest() -> int:
    fails: List[str] = []
    contract = {"meta": {"title": "T"}, "ftue": {"aha_seconds_target": 30, "steps": [{"id": "s1"}, {"id": "s2"}]},
                "economy": {"currencies": [{"id": "coins"}, {"id": "gems"}]},
                "monetization": {"iap": [{"id": "starter"}], "ads": {"rewarded": [{"id": "revive"}], "interstitial": {}}},
                "liveops": {"events": [{"id": "rally"}]}, "loops": [{"type": "core"}, {"type": "social"}]}
    tax = generate(contract)
    errs = check(tax)
    if errs:
        fails.append("generated taxonomy invalid: %s" % errs)
    names = [e["name"] for e in tax["events"]]
    for n in ("level_end", "iap_purchase", "rv_completed", "liveops_event_join", "social_action", "interstitial_shown"):
        if n not in names:
            fails.append("missing event %s" % n)
    step = next(e for e in tax["events"] if e["name"] == "tutorial_step")["params"][0]
    if step.get("enum") != ["s1", "s2"]:
        fails.append("ftue enum not taken from contract")
    bad = {"naming": "snake_case", "common_params": [], "events": [
        {"name": "BadName", "params": []}, {"name": "x" * 41, "params": []}, {"name": "ga_thing", "params": []},
        {"name": "ok_event", "params": [{"name": "p%d" % i, "type": "int"} for i in range(26)]},
        {"name": "ok_event", "params": []}]}
    if len(check(bad)) < 5:
        fails.append("check missed violations: %s" % check(bad))
    gd = godot_stubs(tax)
    if "static func log_level_end(level_id: String, attempt: int, success: bool, reason: String, duration_sec: float, moves_used: Variant = null) -> void:" not in gd:
        fails.append("godot level_end signature")
    if 'Analytics.log_event("tutorial_begin", {})' not in gd or "assert(step_id in [" not in gd:
        fails.append("godot body")
    cs = unity_stubs(tax)
    if "public static void LogLevelEnd(string levelId, int attempt, bool success, string reason, float durationSec, int? movesUsed = null)" not in cs:
        fails.append("unity level_end signature")
    for f in fails:
        print("FAIL", f)
    print("event_taxonomy selftest: %s" % ("FAILED" if fails else "ok"))
    return 1 if fails else 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--selftest" in argv:
        return selftest()
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--selftest", action="store_true")
    sub = p.add_subparsers(dest="cmd")
    g = sub.add_parser("generate", help="draft a taxonomy from a design contract")
    g.add_argument("--contract", required=True)
    g.add_argument("--out", required=True)
    s = sub.add_parser("stubs", help="engine code stubs from a taxonomy")
    s.add_argument("--taxonomy", required=True)
    s.add_argument("--engine", choices=("godot", "unity"), required=True)
    s.add_argument("--out", required=True, help="output directory")
    a = p.parse_args(argv)
    if not a.cmd:
        p.print_usage(sys.stderr)
        return 2
    try:
        if a.cmd == "generate":
            tax = generate(read_json(a.contract))
            errs = check(tax)
            out = Path(a.out)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(tax, indent=2) + "\n", encoding="utf-8")
            print("wrote %s (%d events)" % (out, len(tax["events"])))
        else:
            tax = read_json(a.taxonomy)
            errs = check(tax)
            if not errs:
                out = Path(a.out)
                out.mkdir(parents=True, exist_ok=True)
                fn, body = (("analytics_events.gd", godot_stubs(tax)) if a.engine == "godot"
                            else ("AnalyticsEvents.cs", unity_stubs(tax)))
                (out / fn).write_text(body, encoding="utf-8")
                print("wrote %s" % (out / fn))
    except InputError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    for e in errs:
        print("violation:", e, file=sys.stderr)
    return 1 if errs else 0


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows pipes default to the ANSI code page; Claude Code reads UTF-8
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
