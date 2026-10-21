#!/usr/bin/env node
// Runs a arcosian hook script with the first working Python 3. hooks.json starts every hook in exec form
// ("node" plus this file), so no shell is involved: macOS, Linux, Windows with Git Bash and Windows without it all
// behave the same. Tries python3, python, then the Windows launcher "py -3"; Windows' App Execution Alias stubs
// (python/python3 that only open the Microsoft Store) fail the version check and are skipped. The working command is
// cached in the plugin data folder and passed to the script as GS_PYTHON. Stdio and exit code are the script's own.
import { spawn, spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";

const CANDIDATES = [["python3"], ["python"], ["py", "-3"]];
const CHECK = "import sys; sys.exit(sys.version_info[0] != 3)";
const [script, ...rest] = process.argv.slice(2);
const dataDir = process.env.CLAUDE_PLUGIN_DATA;
const cacheFile = dataDir ? path.join(dataDir, "python.json") : null;

const onPath = (name) => (process.env.PATH || "").split(path.delimiter).some((d) => {
  try { return d && fs.statSync(path.join(d, name)).isFile(); } catch { return false; }
});

function resolvePython() {
  for (const [cmd, ...pre] of CANDIDATES) {
    // Off Windows a python3 on PATH is the real thing; on Windows it may be a Store stub, so every candidate is run once.
    if (process.platform !== "win32" && cmd === "python3" && onPath(cmd)) return { cmd, pre };
    const r = spawnSync(cmd, [...pre, "-c", CHECK], { stdio: "ignore", windowsHide: true, timeout: 15_000 });
    if (r.status === 0) return { cmd, pre };
  }
  return null;
}

function cached() {
  try {
    const c = JSON.parse(fs.readFileSync(cacheFile, "utf8"));
    return typeof c.cmd === "string" && Array.isArray(c.pre) ? c : null;
  } catch { return null; }
}

function run(py, fromCache) {
  const child = spawn(py.cmd, [...py.pre, script, ...rest], {
    stdio: "inherit", windowsHide: true, env: { ...process.env, GS_PYTHON: [py.cmd, ...py.pre].join(" ") },
  });
  child.on("error", () => {
    if (fromCache) { try { fs.rmSync(cacheFile); } catch {} return start(false); } // Python moved or was removed
    fail();
  });
  child.on("exit", (code, signal) => process.exit(code ?? (signal ? 1 : 0)));
}

function fail() {
  process.stderr.write(`arcosian hooks: no Python 3 found (tried python3, python and py -3); ${path.basename(script || "hook")} skipped. Install Python 3 (python.org) and start a new session.\n`);
  process.exit(1); // a non-blocking hook error: the user sees it, the action goes ahead
}

function start(useCache) {
  const hit = useCache && cacheFile ? cached() : null;
  if (hit) return run(hit, true);
  const py = resolvePython();
  if (!py) return fail();
  if (cacheFile) { try { fs.mkdirSync(dataDir, { recursive: true }); fs.writeFileSync(cacheFile, JSON.stringify(py) + "\n"); } catch {} }
  run(py, false);
}

if (!script) { process.stderr.write("usage: node run-python.mjs <hook script> [args...]\n"); process.exit(1); }
start(true);
