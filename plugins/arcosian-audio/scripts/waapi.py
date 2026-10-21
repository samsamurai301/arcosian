#!/usr/bin/env python3
"""waapi.py - minimal WAAPI client over HTTP (arcosian-audio, audio-middleware skill).

Sends one JSON request to the Wwise Authoring API HTTP endpoint and prints the
JSON reply. Not verified against a running Wwise: the endpoint and request
shape follow Audiokinetic's published WAAPI examples (HTTP POST to
http://localhost:8090/waapi with a JSON body holding "uri", "args", "options").
Check Project > User Preferences in your Wwise version for the port.

    waapi.py info [--url URL] [--timeout S] [--allow-remote]
    waapi.py call URI [--args JSON] [--options JSON] [--url URL] [--timeout S]
                      [--allow-remote]
    waapi.py --selftest

Non-localhost URLs are refused unless --allow-remote is given. WAAPI has no
authentication; never expose it to a network. HTTP cannot subscribe to topics
(use the WebSocket/WAMP endpoint for that).

Exit codes: 0 ok, 1 request failed or server returned an error, 2 usage error.
Stdlib only, Python 3.9+.
"""
from __future__ import annotations

import argparse
import json
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, Optional, Tuple

DEFAULT_URL = "http://127.0.0.1:8090/waapi"
LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}


class UsageError(Exception):
    pass


def check_url(url: str, allow_remote: bool) -> str:
    parts = urllib.parse.urlsplit(url)
    if parts.scheme not in ("http", "https"):
        raise UsageError("URL must start with http:// or https://")
    host = (parts.hostname or "").lower()
    if not host:
        raise UsageError("URL has no host")
    if host not in LOCAL_HOSTS and not allow_remote:
        raise UsageError(
            "refusing non-localhost URL %r (WAAPI has no authentication); "
            "pass --allow-remote only if you understand the risk" % host
        )
    return url


def parse_json_arg(text: Optional[str], name: str) -> Dict[str, Any]:
    if text is None:
        return {}
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise UsageError("%s is not valid JSON: %s" % (name, exc))
    if not isinstance(value, dict):
        raise UsageError("%s must be a JSON object" % name)
    return value


def post(url: str, uri: str, args: Dict[str, Any], options: Dict[str, Any],
         timeout: float) -> Tuple[int, Any]:
    body = json.dumps({"uri": uri, "args": args, "options": options}).encode("utf-8")
    req = urllib.request.Request(
        url, data=body, method="POST",
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(req, timeout=timeout) as resp:
            status, raw = resp.status, resp.read()
    except urllib.error.HTTPError as exc:
        status, raw = exc.code, exc.read()
    text = raw.decode("utf-8", errors="replace")
    try:
        return status, json.loads(text)
    except json.JSONDecodeError:
        return status, {"raw": text}


def run(url: str, uri: str, args: Dict[str, Any], options: Dict[str, Any],
        timeout: float) -> int:
    try:
        status, reply = post(url, uri, args, options, timeout)
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        print("request failed: %s" % exc, file=sys.stderr)
        return 1
    print(json.dumps(reply, indent=2, ensure_ascii=False))
    if status >= 400:
        print("server returned HTTP %d" % status, file=sys.stderr)
        return 1
    return 0


# --------------------------------------------------------------------------- selftest

def _selftest() -> int:
    seen: Dict[str, Any] = {}

    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:  # noqa: N802
            length = int(self.headers.get("Content-Length", "0"))
            req = json.loads(self.rfile.read(length).decode("utf-8"))
            seen["path"] = self.path
            seen["req"] = req
            if req.get("uri") == "ak.wwise.core.getInfo":
                payload, code = {"version": {"displayName": "mock"}}, 200
            else:
                payload, code = {"uri": "ak.wwise.error.invalid_uri", "message": "no"}, 500
            data = json.dumps(payload).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def log_message(self, *a: Any) -> None:
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = "http://127.0.0.1:%d/waapi" % server.server_address[1]
    failures = []

    def check(cond: bool, label: str) -> None:
        if not cond:
            failures.append(label)

    try:
        status, reply = post(url, "ak.wwise.core.getInfo", {}, {}, 5)
        check(status == 200 and reply["version"]["displayName"] == "mock", "getInfo reply")
        check(seen["path"] == "/waapi", "path")
        check(seen["req"] == {"uri": "ak.wwise.core.getInfo", "args": {}, "options": {}}, "body shape")
        status, reply = post(url, "ak.bad", {"a": 1}, {"b": 2}, 5)
        check(status == 500 and "message" in reply, "error reply")
        check(seen["req"]["args"] == {"a": 1} and seen["req"]["options"] == {"b": 2}, "args/options sent")
    finally:
        server.shutdown()
        server.server_close()

    for bad in ("http://example.com/waapi", "http://10.0.0.5:8090/waapi"):
        try:
            check_url(bad, False)
            failures.append("remote not refused: " + bad)
        except UsageError:
            pass
    try:
        check_url("http://example.com/waapi", True)
    except UsageError:
        failures.append("allow-remote ignored")
    for ok in (DEFAULT_URL, "http://localhost:8090/waapi", "http://[::1]:8090/waapi"):
        try:
            check_url(ok, False)
        except UsageError:
            failures.append("local refused: " + ok)
    try:
        check_url("file:///etc/passwd", True)
        failures.append("file scheme accepted")
    except UsageError:
        pass
    try:
        parse_json_arg("[1]", "--args")
        failures.append("non-object JSON accepted")
    except UsageError:
        pass

    if failures:
        print("selftest FAILED: " + "; ".join(failures), file=sys.stderr)
        return 1
    print("selftest ok")
    return 0


# --------------------------------------------------------------------------- CLI

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Minimal WAAPI HTTP client (unverified against a running Wwise).")
    p.add_argument("--selftest", action="store_true", help="run offline self-test against a mock server")
    sub = p.add_subparsers(dest="cmd")
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--url", default=DEFAULT_URL, help="WAAPI HTTP endpoint (default %(default)s)")
    common.add_argument("--timeout", type=float, default=10.0, help="seconds (default 10)")
    common.add_argument("--allow-remote", action="store_true", help="allow a non-localhost URL")
    sub.add_parser("info", parents=[common], help="call ak.wwise.core.getInfo")
    c = sub.add_parser("call", parents=[common], help="call any WAAPI URI")
    c.add_argument("uri", help="e.g. ak.wwise.core.object.get")
    c.add_argument("--args", help="JSON object")
    c.add_argument("--options", help="JSON object")
    return p


def main(argv: Optional[list] = None) -> int:
    parser = build_parser()
    ns = parser.parse_args(argv)
    if ns.selftest:
        return _selftest()
    if not ns.cmd:
        parser.print_usage(sys.stderr)
        return 2
    try:
        url = check_url(ns.url, ns.allow_remote)
        if ns.cmd == "info":
            return run(url, "ak.wwise.core.getInfo", {}, {}, ns.timeout)
        args = parse_json_arg(ns.args, "--args")
        options = parse_json_arg(ns.options, "--options")
        return run(url, ns.uri, args, options, ns.timeout)
    except UsageError as exc:
        print("error: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):  # Windows pipes default to the ANSI code page; Claude Code reads UTF-8
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
