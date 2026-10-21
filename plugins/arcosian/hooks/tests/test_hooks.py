#!/usr/bin/env python3
"""End-to-end tests for the arcosian hooks: each script is run as a subprocess with a JSON payload."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[2]
SCRIPTS = PLUGIN / "hooks" / "scripts"
TEMPLATE = PLUGIN / "templates" / "godot-starter"
sys.path.insert(0, str(PLUGIN / "scripts"))
sys.path.insert(0, str(SCRIPTS))
import gslib  # noqa: E402
import post_tool_check  # noqa: E402

GODOT = post_tool_check.godot_binary()   # the hook's own lookup
needs_godot = unittest.skipUnless(GODOT, "no Godot binary (set GODOT_BIN)")
NODE = shutil.which("node")


def run_hook(script: str, payload: dict, env_extra: dict = None):
    env = dict(os.environ)
    env.pop("GS_PYTHON", None)  # set by run-python.mjs in real sessions; tests choose it explicitly
    env.update(env_extra or {})
    r = subprocess.run([sys.executable, str(SCRIPTS / script)], input=json.dumps(payload), capture_output=True,
                       text=True, env=env, timeout=60)
    out = json.loads(r.stdout) if r.stdout.strip() else None
    return r.returncode, out, r.stderr


def passing_feature(fid="F001", root: Path = None, **over) -> dict:
    f = gslib.new_feature(fid, "Test feature", "tech")
    f.update(status="done", passes=True)
    for g in gslib.GATES:
        f["gates"][g] = "pass"
        rel = ".gamestudio/evidence/%s/%s.log" % (fid, g)
        f["evidence"][g] = rel
        if root is not None:
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("ok\n", encoding="utf-8")
    f.update(over)
    return f


class HookTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="gshooks-")).resolve()
        self.root = self.tmp / "game"
        self.root.mkdir()
        gslib.init_project(self.root, "Hook Test", None, "puzzle", platforms=["ios", "android"])
        self.features = self.root / ".gamestudio" / "features.json"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def payload(self, event, **kw):
        d = {"session_id": "s", "cwd": str(self.root), "hook_event_name": event}
        d.update(kw)
        return d

    def write_features(self, feats):
        gslib.save_json(self.features, {"schema_version": "1.0", "features": feats})

    def bash(self, cmd):
        return run_hook("pre_tool_guard.py", self.payload("PreToolUse", tool_name="Bash", tool_input={"command": cmd}))

    def ps(self, cmd):
        return run_hook("pre_tool_guard.py", self.payload("PreToolUse", tool_name="PowerShell", tool_input={"command": cmd}))

    def decision(self, out):
        return out["hookSpecificOutput"]["permissionDecision"] if out else None

    # ---- SessionStart
    def test_session_start_summary(self):
        rc, out, _ = run_hook("session_start.py", self.payload("SessionStart"))
        self.assertEqual(rc, 0)
        ctx = out["hookSpecificOutput"]["additionalContext"]
        self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "SessionStart")
        self.assertIn("Hook Test", ctx)

    def test_session_start_engine_hint_and_noop(self):
        bare = self.tmp / "bare"
        bare.mkdir()
        rc, out, _ = run_hook("session_start.py", {"cwd": str(bare), "hook_event_name": "SessionStart"})
        self.assertEqual((rc, out), (0, None))
        (bare / "project.godot").write_text("config_version=5\n", encoding="utf-8")
        rc, out, _ = run_hook("session_start.py", {"cwd": str(bare), "hook_event_name": "SessionStart"})
        self.assertIn("/arcosian:studio", out["hookSpecificOutput"]["additionalContext"])

    def test_session_start_python_note(self):
        bare = self.tmp / "bare"
        bare.mkdir()
        _, out, _ = run_hook("session_start.py", {"cwd": str(bare), "hook_event_name": "SessionStart"}, {"GS_PYTHON": "py -3"})
        self.assertIn("`py -3`", out["hookSpecificOutput"]["additionalContext"])
        _, out, _ = run_hook("session_start.py", {"cwd": str(bare), "hook_event_name": "SessionStart"}, {"GS_PYTHON": "python3"})
        self.assertIsNone(out)
        _, out, _ = run_hook("session_start.py", self.payload("SessionStart"), {"GS_PYTHON": "python"})
        ctx = out["hookSpecificOutput"]["additionalContext"]
        self.assertIn("Hook Test", ctx)
        self.assertIn("`python`", ctx)

    # ---- PreToolUse PowerShell (Claude Code's shell on Windows)
    def test_powershell_secret_reads_denied(self):
        for cmd in ("Get-Content release.keystore", "gc .\\keys\\upload.jks", "type C:\\proj\\.env",
                    "Microsoft.PowerShell.Management\\Get-Content -Path keys/upload.p12 -Raw",
                    "cmd /c type secrets\\.env.production", "[System.IO.File]::ReadAllBytes('C:\\keys\\release.keystore')",
                    "certutil -encode release.jks out.txt", "Get-StoredCredential -Target play"):
            _, out, _ = self.ps(cmd)
            self.assertEqual(self.decision(out), "deny", cmd)
        for cmd in ("Get-Content .env.example", "Get-Content README.md", "Copy-Item release.keystore build\\"):
            _, out, _ = self.ps(cmd)
            self.assertIsNone(out, cmd)

    def test_powershell_store_submission_asks(self):
        _, out, _ = self.ps("bundle exec fastlane ios deliver --submit_for_review")
        self.assertEqual(self.decision(out), "ask")
        _, out, _ = self.ps("fastlane ios beta")
        self.assertIsNone(out)

    def test_powershell_recursive_delete_asks(self):
        for cmd in ("Remove-Item -Recurse -Force .gamestudio", "rm -r assets", "ri .gamestudio -Recurse",
                    "cmd /c rd /s /q .gamestudio", "Remove-Item -Path assets -Recurse", "Remove-Item -Recurse %s" % self.root,
                    "Remove-Item -Recurse -Force .gamestudio\\*"):
            _, out, _ = self.ps(cmd)
            self.assertEqual(self.decision(out), "ask", cmd)
        for cmd in ("Remove-Item -Recurse build\\tmp", "Remove-Item .gamestudio\\cache.json",
                    "Remove-Item notes.txt -ErrorAction SilentlyContinue"):
            _, out, _ = self.ps(cmd)
            self.assertIsNone(out, cmd)

    # ---- PreToolUse Bash
    def test_fastlane_deliver_asks(self):
        _, out, _ = self.bash("bundle exec fastlane ios deliver --submit_for_review")
        self.assertEqual(self.decision(out), "ask")
        _, out, _ = self.bash("fastlane ios beta")
        self.assertIsNone(out)

    def test_pc_store_uploads_ask(self):
        for cmd in ("steamcmd +login builder +run_app_build ../scripts/app_build_1000.vdf +quit",
                    "./steamcmd.sh +login builder +run_app_build_http app.vdf +quit",
                    "steamcmd +login builder +run_workshop_build item.vdf +quit",
                    "butler push build/web studio/game:html5 --userversion 1.0.0",
                    "BuildPatchTool.exe -mode=UploadBinary -OrganizationId=o -ProductId=p",
                    "msstore publish ./build/msix"):
            _, out, _ = self.bash(cmd)
            self.assertEqual(self.decision(out), "ask", cmd)
        _, out, _ = self.ps("steamcmd.exe +login builder +run_app_build C:\\build\\app.vdf +quit")
        self.assertEqual(self.decision(out), "ask")
        for cmd in ("steamcmd +login anonymous +app_update 1007 +quit", "butler status studio/game",
                    "butler validate build/web", "msstore apps list"):
            _, out, _ = self.bash(cmd)
            self.assertIsNone(out, cmd)

    def test_keystore_read_denied(self):
        _, out, _ = self.bash("cat release.keystore")
        self.assertEqual(self.decision(out), "deny")
        _, out, _ = self.bash("security find-generic-password -s foo -w")
        self.assertEqual(self.decision(out), "deny")
        _, out, _ = self.bash("grep KEY .env")
        self.assertEqual(self.decision(out), "deny")
        _, out, _ = self.bash("cat .env.example && ls release/")
        self.assertIsNone(out)

    def test_rm_rf_protected_asks(self):
        _, out, _ = self.bash("rm -rf .gamestudio")
        self.assertEqual(self.decision(out), "ask")
        _, out, _ = self.bash("rm -rf assets")
        self.assertEqual(self.decision(out), "ask")
        _, out, _ = self.bash("rm -rf build/tmp")
        self.assertIsNone(out)

    # ---- PreToolUse features.json
    def feature_write(self, feats):
        content = json.dumps({"schema_version": "1.0", "features": feats})
        return run_hook("pre_tool_guard.py", self.payload(
            "PreToolUse", tool_name="Write", tool_input={"file_path": str(self.features), "content": content}))

    def test_features_pass_without_evidence_denied(self):
        _, out, _ = self.feature_write([passing_feature(root=None)])
        self.assertEqual(self.decision(out), "deny")

    def test_features_pass_with_evidence_allowed(self):
        _, out, _ = self.feature_write([passing_feature(root=self.root)])
        self.assertNotEqual(self.decision(out), "deny")

    def test_features_edit_reconstruction(self):
        feat = gslib.new_feature("F001", "Test feature", "tech")
        self.write_features([feat])
        edit = {"file_path": str(self.features), "old_string": '"passes": false', "new_string": '"passes": true'}
        _, out, _ = run_hook("pre_tool_guard.py", self.payload("PreToolUse", tool_name="Edit", tool_input=edit))
        self.assertEqual(self.decision(out), "deny")
        edit = {"file_path": str(self.features), "old_string": '"priority": "P1"', "new_string": '"priority": "P0"'}
        _, out, _ = run_hook("pre_tool_guard.py", self.payload("PreToolUse", tool_name="Edit", tool_input=edit))
        self.assertIsNone(out)

    def test_deleting_passing_feature_denied(self):
        self.write_features([passing_feature(root=self.root)])
        _, out, _ = self.feature_write([])
        self.assertEqual(self.decision(out), "deny")

    # ---- PostToolUse
    def post(self, path: Path, tool="Write"):
        return run_hook("post_tool_check.py", self.payload(
            "PostToolUse", tool_name=tool, tool_input={"file_path": str(path)}))

    def test_invalid_contract_blocks(self):
        p = self.root / ".gamestudio" / "contract.json"
        p.write_text(json.dumps({"schema_version": "1.0", "meta": "not an object"}), encoding="utf-8")
        _, out, _ = self.post(p)
        self.assertEqual(out["decision"], "block")
        p.write_text("{not json", encoding="utf-8")
        _, out, _ = self.post(p)
        self.assertEqual(out["decision"], "block")

    def test_duplicate_uid_blocks(self):
        (self.root / "project.godot").write_text("config_version=5\n", encoding="utf-8")
        a, b = self.root / "a.tscn", self.root / "b.tscn"
        a.write_text('[gd_scene load_steps=1 format=3 uid="uid://abc123"]\n[node name="A" type="Node"]\n', encoding="utf-8")
        b.write_text('[gd_scene format=3 uid="uid://abc123"]\n[node name="B" type="Node"]\n', encoding="utf-8")
        _, out, _ = self.post(b)
        self.assertEqual(out["decision"], "block")
        self.assertIn("uid://abc123", out["reason"])
        b.write_text('[gd_scene format=3 uid="uid://other1"]\n[node name="B" type="Node"]\n', encoding="utf-8")
        _, out, _ = self.post(b)
        self.assertIsNone(out)

    @unittest.skipUnless(shutil.which("godot") or shutil.which("godot4") or os.environ.get("GODOT_BIN"),
                         "no Godot binary (set GODOT_BIN)")
    def test_godot_parse_error_blocks(self):
        (self.root / "project.godot").write_text('config_version=5\n[application]\nconfig/name="t"\n', encoding="utf-8")
        bad, good = self.root / "bad.gd", self.root / "good.gd"
        bad.write_text("extends Node\nfunc _ready(:\n\tvar x = \n", encoding="utf-8")
        good.write_text("extends Node\nfunc _ready():\n\tprint(1)\n", encoding="utf-8")
        _, out, _ = self.post(bad)
        self.assertEqual(out["decision"], "block")
        self.assertIn("Parse Error", out["reason"])
        _, out, _ = self.post(good)
        self.assertIsNone(out)

    # ---- PostToolUse on a real Godot project (the template): autoloads, class_name types, imported assets
    def copy_template(self):
        """The game template inside the test project, never imported (no .godot, no .uid, no .import files)."""
        shutil.copytree(str(TEMPLATE), str(self.root), dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns(".godot", "*.uid", "*.import"))

    def assert_not_blocked(self, rel: str):
        rc, out, err = self.post(self.root / rel)
        self.assertEqual((rc, out), (0, None), "%s was blocked: %s %s" % (rel, out, err))

    @needs_godot
    def test_godot_valid_template_scripts_with_autoloads_not_blocked(self):
        self.copy_template()
        # These reference the autoload singletons (Analytics, SaveService, EventBus, SafeArea, Haptics...), which do
        # not exist in --script mode; the analyzer knows their names, so only a compile error (not reported) arises.
        for rel in ("presentation/game.gd", "presentation/boot.gd", "presentation/results.gd",
                    "services/app_lifecycle.gd", "tools/playtest/runner.gd", "tools/perf/perf_probe.gd",
                    "core/sim.gd"):
            self.assert_not_blocked(rel)

    @needs_godot
    def test_godot_class_name_types_not_blocked_while_cache_is_stale(self):
        self.copy_template()
        (self.root / "core" / "widget.gd").write_text(
            "class_name Widget\nextends RefCounted\n\nvar value: int = 3\n\nfunc double() -> int:\n\treturn value * 2\n", encoding="utf-8")
        user = self.root / "presentation" / "uses_widget.gd"
        user.write_text(
            "extends Node\n\nvar w: Widget = Widget.new()\n\nfunc _ready() -> void:\n"
            "\tvar d := w.double()\n\tAnalytics.log_event(\"widget\", {\"d\": d})\n", encoding="utf-8")
        self.assert_not_blocked("core/widget.gd")
        # No .godot cache yet, so the analyzer cannot see Widget: the hook refreshes the cache and re-checks.
        self.assert_not_blocked("presentation/uses_widget.gd")
        cache = (self.root / ".godot" / "global_script_class_cache.cfg").read_text(encoding="utf-8")
        self.assertIn("Widget", cache)

    @needs_godot
    def test_godot_preload_of_unimported_asset_not_blocked(self):
        self.copy_template()
        (self.root / "presentation" / "uses_icon.gd").write_text(
            "extends Node\n\nconst ICON = preload(\"res://icon.svg\")\n\nfunc _ready() -> void:\n\tprint(ICON)\n", encoding="utf-8")
        self.assert_not_blocked("presentation/uses_icon.gd")

    @needs_godot
    def test_godot_syntax_error_in_template_script_blocks(self):
        self.copy_template()
        game = self.root / "presentation" / "game.gd"
        game.write_text(game.read_text(encoding="utf-8") + "\nfunc broken(:\n\tAnalytics.log_event(\"x\", {}\n", encoding="utf-8")
        _, out, _ = self.post(game)
        self.assertEqual(out["decision"], "block")
        self.assertIn("game.gd", out["reason"])
        self.assertIn("Parse Error", out["reason"])

    @needs_godot
    def test_godot_real_errors_still_block_next_to_class_names(self):
        self.copy_template()
        (self.root / "core" / "widget.gd").write_text("class_name Widget\nextends RefCounted\n", encoding="utf-8")
        typo = self.root / "presentation" / "typos.gd"
        # Widgit is not a class in this project (a typo), so it must not be mistaken for a stale cache entry.
        typo.write_text("extends Node\n\nfunc _ready() -> void:\n\tvar w = Widgit.new()\n\tprint(w)\n", encoding="utf-8")
        _, out, _ = self.post(typo)
        self.assertEqual(out["decision"], "block")
        self.assertIn('Identifier "Widgit"', out["reason"])
        unknown = self.root / "presentation" / "unknown_ident.gd"
        unknown.write_text("extends Node\n\nfunc _ready() -> void:\n\tvar count: int = 3\n\tprint(cuont)\n", encoding="utf-8")
        _, out, _ = self.post(unknown)
        self.assertEqual(out["decision"], "block")
        self.assertIn('Identifier "cuont"', out["reason"])

    @needs_godot
    @unittest.skipIf(os.name == "nt", "the wrapper is a POSIX shell script")
    def test_godot_stale_cache_errors_dropped_when_refresh_fails(self):
        self.copy_template()
        (self.root / "core" / "widget.gd").write_text("class_name Widget\nextends RefCounted\n", encoding="utf-8")
        user = self.root / "presentation" / "uses_widget.gd"
        user.write_text("extends Node\n\nfunc _ready() -> void:\n\tvar w := Widget.new()\n\tprint(w)\n", encoding="utf-8")
        wrapper = self.tmp / "godot_no_import.sh"   # delegates to the real binary but cannot import
        wrapper.write_text('#!/bin/sh\nfor a in "$@"; do [ "$a" = "--import" ] && exit 1; done\nexec "%s" "$@"\n' % GODOT, encoding="utf-8")
        wrapper.chmod(0o755)
        _, out, _ = run_hook("post_tool_check.py", self.payload(
            "PostToolUse", tool_name="Write", tool_input={"file_path": str(user)}), {"GODOT_BIN": str(wrapper)})
        self.assertIsNone(out)

    def test_unlisted_asset_reminder(self):
        png = self.root / "assets" / "hero.png"
        png.parent.mkdir(exist_ok=True)
        png.write_bytes(b"\x89PNG")
        _, out, _ = self.post(png)
        self.assertIn("manifest", out["hookSpecificOutput"]["additionalContext"])

    # ---- Stop / TaskCompleted
    def test_stop_blocks_done_but_failing(self):
        self.write_features([passing_feature(root=None)])
        _, out, _ = run_hook("stop_gate.py", self.payload("Stop", stop_hook_active=False))
        self.assertEqual(out["decision"], "block")
        self.assertIn("F001", out["reason"])
        for ev in ("Stop", "SubagentStop"):
            rc, out, _ = run_hook("stop_gate.py", self.payload(ev, stop_hook_active=True))
            self.assertEqual((rc, out), (0, None))

    def test_stop_passes_when_consistent(self):
        self.write_features([passing_feature(root=self.root)])
        rc, out, _ = run_hook("stop_gate.py", self.payload("Stop"))
        self.assertEqual((rc, out), (0, None))

    def test_task_completed_failing_feature_exit_2(self):
        self.write_features([gslib.new_feature("F001", "Test feature", "tech")])
        rc, _, err = run_hook("task_gate.py", self.payload(
            "TaskCompleted", task_subject="Implement F001 spawn bag", task_description=""))
        self.assertEqual(rc, 2)
        self.assertIn("F001", err)
        rc, _, _ = run_hook("task_gate.py", self.payload("TaskCompleted", task_subject="Write docs"))
        self.assertEqual(rc, 0)

    # ---- PreCompact and no-op
    def test_pre_compact_writes_snapshot(self):
        rc, _, _ = run_hook("pre_compact.py", self.payload("PreCompact", trigger="auto"))
        self.assertEqual(rc, 0)
        self.assertEqual(len(list((self.root / ".gamestudio" / "snapshots").glob("precompact-*.md"))), 1)

    def test_no_gamestudio_is_noop(self):
        bare = self.tmp / "plain"
        bare.mkdir()
        cases = [("pre_tool_guard.py", dict(tool_name="Bash", tool_input={"command": "cat release.keystore"})),
                 ("pre_tool_guard.py", dict(tool_name="Write", tool_input={
                     "file_path": str(bare / ".gamestudio" / "features.json"), "content": "{}"})),
                 ("post_tool_check.py", dict(tool_name="Write", tool_input={"file_path": str(bare / "x.gd")})),
                 ("stop_gate.py", {}), ("task_gate.py", dict(task_subject="F001")), ("pre_compact.py", {})]
        for script, extra in cases:
            rc, out, _ = run_hook(script, dict(cwd=str(bare), hook_event_name="X", **extra))
            self.assertEqual((rc, out), (0, None), script)
        self.assertFalse((bare / ".gamestudio").exists())

    def test_garbage_stdin_fails_open(self):
        r = subprocess.run([sys.executable, str(SCRIPTS / "pre_tool_guard.py")], input="not json",
                           capture_output=True, text=True)
        self.assertEqual((r.returncode, r.stdout), (0, ""))


@unittest.skipUnless(NODE and os.name == "posix", "needs node and a POSIX shell for the fake interpreters")
class RunPythonTest(unittest.TestCase):
    """hooks.json starts every hook as `node run-python.mjs <script>`. The PATHs below mimic Windows machines:
    no python3, a Microsoft Store stub, only the py launcher, or no Python at all."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="gsrunpy-")).resolve()
        self.data = self.tmp / "data"
        self.bare = self.tmp / "bare"
        self.bare.mkdir()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def tool(self, folder: str, name: str, body: str) -> Path:
        d = self.tmp / folder
        d.mkdir(exist_ok=True)
        p = d / name
        p.write_text("#!/bin/sh\n%s\n" % body, encoding="utf-8")
        p.chmod(0o755)
        return d

    def launch(self, path_dirs, script=SCRIPTS / "session_start.py", stdin=None):
        env = {"PATH": os.pathsep.join(str(d) for d in path_dirs), "CLAUDE_PLUGIN_DATA": str(self.data)}
        payload = stdin if stdin is not None else json.dumps({"cwd": str(self.bare), "hook_event_name": "SessionStart"})
        return subprocess.run([NODE, str(SCRIPTS / "run-python.mjs"), str(script)], input=payload,
                              capture_output=True, text=True, env=env, timeout=60)

    def note(self, r):
        return json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"] if r.stdout.strip() else ""

    def test_python_without_python3(self):
        d = self.tool("py", "python", 'exec "%s" "$@"' % sys.executable)
        r = self.launch([d])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("`python`", self.note(r))
        self.assertEqual(json.loads((self.data / "python.json").read_text(encoding="utf-8"))["cmd"], "python")

    def test_store_stub_skipped_for_py_launcher(self):
        stub = self.tool("WindowsApps", "python", 'echo "Python was not found; run without arguments to install from the Microsoft Store" >&2\nexit 9009')
        py = self.tool("launcher", "py", '[ "$1" = "-3" ] && shift\nexec "%s" "$@"' % sys.executable)
        r = self.launch([stub, py])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("`py -3`", self.note(r))

    def test_no_python_is_a_visible_non_blocking_error(self):
        r = self.launch([self.tmp / "empty"])
        self.assertEqual(r.returncode, 1)
        self.assertIn("no Python 3 found", r.stderr)

    def test_python3_on_path_needs_no_note(self):
        d = self.tool("py3", "python3", 'exec "%s" "$@"' % sys.executable)
        r = self.launch([d])
        self.assertEqual((r.returncode, r.stdout), (0, ""), r.stderr)

    def test_stale_cache_is_replaced(self):
        self.data.mkdir()
        (self.data / "python.json").write_text(json.dumps({"cmd": "python-removed-long-ago", "pre": []}), encoding="utf-8")
        d = self.tool("py", "python", 'exec "%s" "$@"' % sys.executable)
        r = self.launch([d])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads((self.data / "python.json").read_text(encoding="utf-8"))["cmd"], "python")

    def test_stdin_and_exit_code_pass_through(self):
        probe = self.tmp / "probe.py"
        probe.write_text("import sys\ndata = sys.stdin.read()\nprint(len(data))\nsys.exit(2)\n", encoding="utf-8")
        d = self.tool("py3", "python3", 'exec "%s" "$@"' % sys.executable)
        r = self.launch([d], script=probe, stdin="x" * 4321)
        self.assertEqual((r.returncode, r.stdout.strip()), (2, "4321"), r.stderr)


class GodotLookupTest(unittest.TestCase):
    """post_tool_check.godot_binary() on layouts users have: Windows downloads, folders, the adapter's option."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="gsgodot-")).resolve()
        self.saved = {k: os.environ.get(k) for k in ("GODOT_BIN", "PATH", "CLAUDE_PLUGIN_DATA")}
        for k in self.saved:
            os.environ.pop(k, None)
        os.environ["PATH"] = ""

    def tearDown(self):
        for k, v in self.saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        shutil.rmtree(self.tmp, ignore_errors=True)

    def exe(self, folder: str, name: str) -> Path:
        d = self.tmp / folder
        d.mkdir(parents=True, exist_ok=True)
        p = d / name
        p.write_text("", encoding="utf-8")
        p.chmod(0o755)
        return p

    def test_windows_gui_build_swapped_for_console_twin(self):
        gui = self.exe("godot", "Godot_v4.7.2-stable_win64.exe")
        console = self.exe("godot", "Godot_v4.7.2-stable_win64_console.exe")
        os.environ["GODOT_BIN"] = str(gui)
        self.assertEqual(post_tool_check.godot_binary(), str(console))
        os.environ["GODOT_BIN"] = str(gui.parent)  # the folder works too
        self.assertEqual(post_tool_check.godot_binary(), str(console))

    def test_folder_with_plain_binary(self):
        binary = self.exe("linux-godot", "godot")
        os.environ["GODOT_BIN"] = str(binary.parent)
        self.assertEqual(post_tool_check.godot_binary(), str(binary))

    def test_versioned_download_on_path(self):
        console = self.exe("bin", "Godot_v4.7.2-stable_win64_console.exe")
        os.environ["PATH"] = str(console.parent)
        self.assertEqual(post_tool_check.godot_binary(), str(console))

    def test_godot_adapter_option(self):
        custom = self.exe("custom", "godot-4.7.2")
        data = self.tmp / "plugin-data" / "arcosian-arcosian"
        data.mkdir(parents=True)
        adapter = data.parent / "arcosian-godot-arcosian"
        adapter.mkdir()
        (adapter / "options.json").write_text(json.dumps({"godot_bin": str(custom)}), encoding="utf-8")
        os.environ["CLAUDE_PLUGIN_DATA"] = str(data)
        self.assertEqual(post_tool_check.godot_binary(), str(custom))


if __name__ == "__main__":
    unittest.main(verbosity=1)
