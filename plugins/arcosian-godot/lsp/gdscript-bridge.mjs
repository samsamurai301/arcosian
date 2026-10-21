#!/usr/bin/env node
// gdscript-bridge: gives Claude Code Godot's own GDScript language server.
// Claude Code runs language servers over stdio; Godot serves LSP over TCP from inside the editor. The bridge finds the
// project, starts a headless editor on free ports (or attaches to an open editor when GS_GODOT_LSP_PORT is set) and
// relays messages, covering Godot's gaps: it answers shutdown/exit itself (Godot has no handlers), always sends full
// document text, drops Godot-only notifications and maps URIs back to the strings the client used.
// The plugin options godot_bin and godot_lsp_port arrive through options.json in the plugin data folder (written by
// the SessionStart hook in save-options.mjs); GS_GODOT_BIN, GS_GODOT_LSP_PORT and GS_GODOT_PROJECT override them.
// stdout carries protocol only; logs go to stderr. GS_LSP_LOG=<file> traces every message.
import { spawn } from "node:child_process";
import crypto from "node:crypto";
import fs from "node:fs";
import net from "node:net";
import os from "node:os";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const env = process.env;
const setting = (v) => (v && !v.includes("${") ? v.trim() : ""); // an unset plugin option can arrive empty or unexpanded
const log = (m) => process.stderr.write(`gdscript-bridge: ${m}\n`);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const traceFile = setting(env.GS_LSP_LOG);
const trace = (dir, msg) => {
  if (!traceFile) return;
  const s = JSON.stringify(msg);
  fs.appendFileSync(traceFile, `${new Date().toISOString()} ${dir} ${s.length > 4000 ? s.slice(0, 4000) + "..." : s}\n`);
};

const options = (() => {
  const dir = setting(env.CLAUDE_PLUGIN_DATA);
  try { return dir ? JSON.parse(fs.readFileSync(path.join(dir, "options.json"), "utf8")) : {}; } catch { return {}; }
})();
const SKIP_DIRS = new Set(["node_modules", "addons", "build", "builds", "export", "Library", "Temp"]);
const GODOT_ONLY = new Set(["gdscript_client/changeWorkspace", "gdscript/capabilities"]); // ~60 KB of class names at start
const URI_KEYS = new Set(["uri", "targetUri", "oldUri", "newUri"]);
const STARTUP_MS = 170_000; // .lsp.json gives the server 180 s to answer initialize (first import included)

// LSP base protocol: "Content-Length: N\r\n\r\n" then N bytes of UTF-8 JSON.
function frames(onMessage) {
  let buf = Buffer.alloc(0);
  return (chunk) => {
    buf = buf.length ? Buffer.concat([buf, chunk]) : chunk;
    for (;;) {
      const end = buf.indexOf("\r\n\r\n");
      if (end < 0) return;
      const len = /content-length:\s*(\d+)/i.exec(buf.subarray(0, end).toString("latin1"));
      if (!len) { buf = buf.subarray(end + 4); continue; }
      const start = end + 4, stop = start + Number(len[1]);
      if (buf.length < stop) return;
      const body = buf.subarray(start, stop).toString("utf8");
      buf = buf.subarray(stop);
      let msg;
      try { msg = JSON.parse(body); } catch { log("skipped a message that is not JSON"); continue; }
      onMessage(msg);
    }
  };
}
const encode = (msg) => {
  const body = Buffer.from(JSON.stringify(msg), "utf8");
  return Buffer.concat([Buffer.from(`Content-Length: ${body.length}\r\n\r\n`, "latin1"), body]);
};

function findProject(start) {
  const forced = setting(env.GS_GODOT_PROJECT);
  if (forced) return fs.existsSync(path.join(forced, "project.godot")) ? path.resolve(forced) : null;
  for (let d = path.resolve(start); ; d = path.dirname(d)) {
    if (fs.existsSync(path.join(d, "project.godot"))) return d;
    if (path.dirname(d) === d) break;
  }
  let level = [path.resolve(start)], seen = 0;
  for (let depth = 0; depth < 3 && level.length && seen < 5000; depth++) {
    const next = [], found = [];
    for (const dir of level) {
      let entries = [];
      try { entries = fs.readdirSync(dir, { withFileTypes: true }); } catch { continue; }
      for (const e of entries.sort((a, b) => a.name.localeCompare(b.name))) {
        if (!e.isDirectory() || e.name.startsWith(".") || SKIP_DIRS.has(e.name)) continue;
        const sub = path.join(dir, e.name);
        seen++;
        (fs.existsSync(path.join(sub, "project.godot")) ? found : next).push(sub);
      }
    }
    if (found.length) {
      if (found.length > 1) log(`found ${found.length} Godot projects, using ${found[0]} (set GS_GODOT_PROJECT to pick another)`);
      return found[0];
    }
    level = next;
  }
  return null;
}

const isFile = (p) => { try { return fs.statSync(p).isFile(); } catch { return false; } };
const isDir = (p) => { try { return fs.statSync(p).isDirectory(); } catch { return false; } };
const GODOT_EXE = /^godot.*\.exe$/i;

// A Godot path as users give it: the binary, a macOS .app, a folder holding Godot, or a Windows GUI .exe, which is
// swapped for its _console twin because only the console build reliably prints to a pipe.
function godotPath(p) {
  if (!p) return null;
  if (isFile(path.join(p, "Contents", "MacOS", "Godot"))) p = path.join(p, "Contents", "MacOS", "Godot");
  else if (isDir(p)) {
    let exes = [];
    try { exes = fs.readdirSync(p).filter((n) => GODOT_EXE.test(n)).sort(); } catch {}
    const plain = ["godot", "godot4", "Godot"].map((n) => path.join(p, n)).find(isFile);
    if (!exes.length && !plain) return null;
    p = exes.length ? path.join(p, exes.find((n) => /_console\.exe$/i.test(n)) || exes[0]) : plain;
  }
  if (/\.exe$/i.test(p) && !/_console\.exe$/i.test(p) && isFile(p.replace(/\.exe$/i, "_console.exe"))) p = p.replace(/\.exe$/i, "_console.exe");
  try { fs.accessSync(p, fs.constants.X_OK); return isFile(p) ? p : null; } catch { return null; }
}

function findGodot() {
  const names = process.platform === "win32" ? ["godot.exe", "godot4.exe"] : ["godot", "godot4"];
  const dirs = (env.PATH || "").split(path.delimiter).filter(Boolean);
  const candidates = [setting(env.GS_GODOT_BIN), setting(options.godot_bin), setting(env.GODOT_BIN), setting(env.GODOT)];
  for (const dir of dirs) for (const n of names) candidates.push(path.join(dir, n));
  // Windows downloads keep their versioned name (Godot_v4.7.2-stable_win64.exe); accept those on PATH too.
  for (const dir of dirs) { try { for (const n of fs.readdirSync(dir).filter((x) => GODOT_EXE.test(x)).sort()) candidates.push(path.join(dir, n)); } catch {} }
  if (process.platform === "darwin") candidates.push("/Applications/Godot.app");
  for (const c of candidates) { const p = godotPath(c); if (p) return p; }
  return null;
}

// Documents as the client sees them: Godot only accepts full-text sync, so incremental edits are applied here.
const docs = new Map();
function offsetAt(text, { line, character }) {
  let off = 0;
  for (let l = 0; l < line; l++) {
    const nl = text.indexOf("\n", off);
    if (nl < 0) return text.length;
    off = nl + 1;
  }
  const eol = text.indexOf("\n", off);
  const lineEnd = eol < 0 ? text.length : text[eol - 1] === "\r" ? eol - 1 : eol;
  return Math.min(off + character, lineEnd);
}
function applyChanges(text, changes) {
  for (const c of changes) {
    if (!c.range) { text = c.text; continue; }
    text = text.slice(0, offsetAt(text, c.range.start)) + c.text + text.slice(offsetAt(text, c.range.end));
  }
  return text;
}

// Godot sees every file under the project's real path (symlinks such as macOS /tmp resolved) and answers with URIs
// built from it; the client gets back the exact URI strings it sent for the same files.
const clientUris = new Map();
const real = (p) => {
  try { return fs.realpathSync.native(p); } catch {}
  try { return path.join(fs.realpathSync.native(path.dirname(p)), path.basename(p)); } catch { return p; }
};
const pathKey = (p) => (process.platform === "linux" ? p : p.toLowerCase()); // macOS and Windows ignore case by default
const uriPath = (uri) => { try { return uri.startsWith("file:") ? fileURLToPath(new URL(uri)) : null; } catch { return null; } };
const remember = (uri) => { const p = uriPath(uri); if (p) clientUris.set(pathKey(real(p)), uri); };
const serverUri = (uri) => { const p = uriPath(uri); return p ? pathToFileURL(real(p)).href : uri; };
const clientUri = (uri) => { const p = uriPath(uri); return p ? clientUris.get(pathKey(real(p))) || pathToFileURL(p).href : uri; };
function mapUris(v, fn) {
  if (Array.isArray(v)) return v.map((x) => mapUris(x, fn));
  if (!v || typeof v !== "object") return v;
  const out = {};
  for (const [k, x] of Object.entries(v)) {
    if (k === "changes" && x && typeof x === "object" && !Array.isArray(x)) {
      out[k] = Object.fromEntries(Object.entries(x).map(([u, edits]) => [fn(u), mapUris(edits, fn)]));
    } else out[k] = typeof x === "string" && URI_KEYS.has(k) ? fn(x) : mapUris(x, fn);
  }
  return out;
}

const startDir = setting(env.CLAUDE_PROJECT_DIR) || process.cwd();
const attachPort = Number(setting(env.GS_GODOT_LSP_PORT) || setting(String(options.godot_lsp_port ?? ""))) || 0;
const found = findProject(startDir);
const project = found && real(found);
let failure = null;
if (!project && !attachPort) failure = `no Godot project (project.godot) in ${startDir}, its parent folders or three levels below; start Claude Code in the project or set GS_GODOT_PROJECT`;
const bin = failure || attachPort ? null : findGodot();
if (!failure && !attachPort && !bin) failure = "no Godot 4 binary found; set the plugin option godot_bin (or GODOT_BIN), or put godot on PATH";

let godot = null, godotExited = false, sock = null, logFile = null, quitting = false, shutdownSeen = false, initId;
const queue = [], forwarded = new Set();

function toClient(msg) { trace("<-", msg); process.stdout.write(encode(msg)); }
function toServer(msg) { trace("->", msg); if (sock) sock.write(encode(msg)); else queue.push(msg); }
function reject(m) {
  toClient(m.method === "initialize"
    ? { jsonrpc: "2.0", id: m.id, error: { code: -32603, message: `GDScript language server unavailable: ${failure}`, data: { retry: false } } }
    : { jsonrpc: "2.0", id: m.id, error: { code: -32002, message: failure } });
}

function onClient(msg) {
  const { id, method } = msg;
  if (method === "exit") return quit(shutdownSeen ? 0 : 1);
  if (method === "shutdown") { shutdownSeen = true; return toClient({ jsonrpc: "2.0", id, result: null }); }
  if (failure) { if (method && id !== undefined) reject(msg); return; }
  const doc = msg.params?.textDocument;
  if (doc?.uri) remember(doc.uri);
  if (method === "initialize" && project) {
    initId = id;
    const rootUri = pathToFileURL(project).href;
    msg = { ...msg, params: { ...msg.params, rootPath: project, rootUri, workspaceFolders: [{ uri: rootUri, name: path.basename(project) }] } };
  } else if (method === "initialize") initId = id;
  else if (method === "textDocument/didOpen") docs.set(doc.uri, doc.text);
  else if (method === "textDocument/didClose") docs.delete(doc.uri);
  else if (method === "textDocument/didChange") {
    const changes = msg.params.contentChanges || [];
    if (docs.has(doc.uri) || changes.every((c) => !c.range)) {
      const text = applyChanges(docs.get(doc.uri) ?? "", changes);
      docs.set(doc.uri, text);
      msg = { ...msg, params: { ...msg.params, contentChanges: [{ text }] } };
    }
  }
  if (method && id !== undefined) forwarded.add(id);
  toServer(mapUris(msg, serverUri));
}

function onServer(msg) {
  if (msg.method && msg.id === undefined && GODOT_ONLY.has(msg.method)) return;
  if (!msg.method) {
    if (msg.id === null || msg.id === undefined || !forwarded.has(msg.id)) return; // Godot answers notifications it lacks
    forwarded.delete(msg.id);
    const caps = msg.id === initId ? msg.result?.capabilities : null;
    if (caps?.documentOnTypeFormattingProvider && !caps.documentOnTypeFormattingProvider.firstTriggerCharacter) delete caps.documentOnTypeFormattingProvider;
  }
  toClient(mapUris(msg, clientUri));
}

const freePort = () => new Promise((resolve, reject) => {
  const srv = net.createServer();
  srv.on("error", reject);
  srv.listen(0, "127.0.0.1", () => { const { port } = srv.address(); srv.close(() => resolve(port)); });
});

function run(cmd, args, out, ms) {
  return new Promise((resolve) => {
    const p = spawn(cmd, args, { stdio: ["ignore", out, out], windowsHide: true });
    const t = setTimeout(() => p.kill("SIGKILL"), Math.max(ms, 1000));
    p.on("error", () => { clearTimeout(t); resolve(-1); });
    p.on("exit", (code) => { clearTimeout(t); resolve(code ?? -1); });
  });
}

function capture(cmd, args, ms) {
  return new Promise((resolve) => {
    let text = "";
    const p = spawn(cmd, args, { stdio: ["ignore", "pipe", "pipe"], windowsHide: true });
    const t = setTimeout(() => p.kill("SIGKILL"), ms);
    p.stdout.on("data", (d) => { text += d; });
    p.stderr.on("data", (d) => { text += d; });
    p.on("error", () => { clearTimeout(t); resolve(""); });
    p.on("exit", () => { clearTimeout(t); resolve(text); });
  });
}

// A detached helper stops the editor if this bridge dies without cleaning up (for example on SIGKILL).
function watchdog(pid) {
  const code = 'const [b,g]=process.argv.slice(1).map(Number);const up=(p)=>{try{process.kill(p,0);return true}catch(e){return e.code==="EPERM"}};'
    + 'const t=setInterval(()=>{if(!up(g))process.exit(0);if(!up(b)){clearInterval(t);try{process.kill(g,"SIGTERM")}catch{}'
    + 'setTimeout(()=>{try{process.kill(g,"SIGKILL")}catch{}process.exit(0)},3000)}},2000);';
  spawn(process.execPath, ["-e", code, String(process.pid), String(pid)], { detached: true, stdio: "ignore", windowsHide: true }).unref();
}

async function connect(port, deadline) {
  for (;;) {
    try {
      return await new Promise((resolve, reject) => {
        const s = net.connect(port, "127.0.0.1");
        s.once("connect", () => { s.removeAllListeners("error"); resolve(s); });
        s.once("error", reject);
      });
    } catch {
      if (godotExited) throw new Error(`Godot exited before its language server started; see ${logFile}`);
      if (Date.now() > deadline) throw new Error(`no GDScript language server on port ${port}${logFile ? `; see ${logFile}` : ""}`);
      await sleep(250);
    }
  }
}

async function start() {
  const deadline = Date.now() + STARTUP_MS;
  let port = attachPort;
  if (!port) {
    const help = await capture(bin, ["--help"], 20_000);
    // Judge only output that lists options: a Windows GUI build may print nothing to a pipe.
    if (help.includes("--headless") && !help.includes("--lsp-port")) throw new Error(`${bin} has no --lsp-port option; use Godot 4 (tested with 4.7.2)`);
    if (!help.trim()) log(`${bin} printed nothing for --help; trying it anyway (on Windows, point godot_bin at the _console.exe build)`);
    const dir = path.join(setting(env.CLAUDE_PLUGIN_DATA) || os.tmpdir(), "gdscript-lsp");
    fs.mkdirSync(dir, { recursive: true });
    logFile = path.join(dir, `godot-${crypto.createHash("sha1").update(project).digest("hex").slice(0, 10)}.log`);
    const out = fs.openSync(logFile, "w");
    // Without the class-name cache the first diagnostics would flag every class_name type as unknown.
    if (!fs.existsSync(path.join(project, ".godot", "global_script_class_cache.cfg"))) {
      log(`first run on this project: importing (output in ${logFile})`);
      const code = await run(bin, ["--headless", "--path", project, "--import"], out, deadline - Date.now() - 30_000);
      if (code !== 0) log(`import exited with code ${code}; starting the editor anyway`);
    }
    port = await freePort();
    let dap = await freePort();
    while (dap === port) dap = await freePort();
    // Free ports keep this editor off 6005/6006, which an editor the user opens later expects to own.
    godot = spawn(bin, ["--headless", "--editor", "--path", project, "--lsp-port", String(port), "--dap-port", String(dap)], { stdio: ["ignore", out, out], windowsHide: true });
    godot.on("error", (e) => { godotExited = true; log(`could not start Godot: ${e.message}`); });
    godot.on("exit", (code, signal) => {
      godotExited = true;
      if (!quitting && sock) { log(`Godot exited (${signal || code}); see ${logFile}`); quit(1); }
    });
    watchdog(godot.pid);
    log(`headless Godot editor pid ${godot.pid} (${bin}) on ${project}, language server port ${port}; output in ${logFile}`);
  }
  const s = await connect(port, deadline);
  s.on("data", frames(onServer));
  s.on("close", () => { if (!quitting) { log("Godot closed the language server connection"); quit(1); } });
  s.on("error", (e) => log(`socket error: ${e.message}`));
  sock = s;
  for (const m of queue.splice(0)) sock.write(encode(m));
}

function fail(reason) {
  failure = reason;
  log(reason);
  if (godot && !godotExited) godot.kill("SIGKILL");
  for (const m of queue.splice(0)) if (m.method && m.id !== undefined) reject(m);
}

function quit(code) {
  if (quitting) return;
  quitting = true;
  try { sock?.end(); } catch {}
  if (!godot || godotExited) process.exit(code);
  const force = setTimeout(() => { try { godot.kill("SIGKILL"); } catch {} process.exit(code); }, 3000);
  godot.once("exit", () => { clearTimeout(force); process.exit(code); });
  godot.kill("SIGTERM");
}

process.on("uncaughtException", (e) => { log(`crashed: ${e.stack || e}`); quit(1); });
for (const sig of ["SIGTERM", "SIGINT", "SIGHUP"]) process.on(sig, () => quit(0));
process.stdout.on("error", () => quit(1));
process.stdin.on("data", frames(onClient));
process.stdin.on("end", () => quit(shutdownSeen ? 0 : 1));
if (failure) log(failure);
else start().catch((e) => fail(e.message));
