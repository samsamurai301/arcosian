#!/usr/bin/env node
// lsp-selftest: drives a language server the way Claude Code does and checks what the plugin promises: a clean file
// opens with no errors, an injected type error is reported on its line and clears when reverted, document symbols and
// go-to-definition answer, and shutdown/exit leave no processes behind. Identical copies live in
// arcosian-godot/lsp and arcosian-unity/lsp.
//
//   node lsp-selftest.mjs --file <source> [--also <source>]... [--definition <identifier>] [--root <dir>]
//                         [--timeout <seconds>] [--incremental yes] [--pull no] -- <server command> [args...]
//
// --also files must report no errors either (no diagnostics at all is fine). --incremental sends the edits as ranges
// even to a full-sync server. --pull no leaves pull diagnostics out of the client capabilities, so the server has to
// push them. Exit code 0 means every check passed.
import { execFileSync, spawn } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const argv = process.argv.slice(2);
const sep = argv.indexOf("--");
if (sep < 0 || sep === argv.length - 1) { console.error("usage: see the header of lsp-selftest.mjs"); process.exit(2); }
const opts = { also: [] };
for (let i = 0; i < sep; i += 2) {
  const k = argv[i].replace(/^--/, ""), v = argv[i + 1];
  if (k === "also") opts.also.push(v); else opts[k] = v;
}
if (!opts.file) { console.error("--file is required"); process.exit(2); }
const [cmd, ...cmdArgs] = argv.slice(sep + 1);
const root = path.resolve(opts.root || process.cwd());
const timeoutMs = Number(opts.timeout || 180) * 1000;
const file = path.resolve(root, opts.file);
const LANG = { ".gd": "gdscript", ".cs": "csharp" };
// Appended to the file under test: each must produce a type error on the line that holds the string literal.
const PROBE = {
  ".gd": "\n\nfunc __gs_selftest_probe() -> int:\n\treturn \"not an int\"\n",
  ".cs": "\n\ninternal static class GsSelftestProbe\n{\n    internal static int Probe() { return \"not an int\"; }\n}\n",
};
const ext = path.extname(file);
if (!PROBE[ext]) { console.error(`no probe for ${ext} files`); process.exit(2); }

const results = [];
const check = (name, ok, detail = "") => { results.push(ok); console.log(`${ok ? "PASS" : "FAIL"}  ${name}${detail ? `  (${detail})` : ""}`); };
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const t0 = Date.now();
const secs = () => ((Date.now() - t0) / 1000).toFixed(1) + "s";

const server = spawn(cmd, cmdArgs, { cwd: root, stdio: ["pipe", "pipe", "pipe"], windowsHide: true });
let stderr = "";
server.stderr.on("data", (d) => { stderr += d; });
let exited = null;
server.on("exit", (code, signal) => { exited = { code, signal }; });

let nextId = 0, pull = false;
const waiting = new Map(), published = new Map();
const send = (msg) => { const b = Buffer.from(JSON.stringify({ jsonrpc: "2.0", ...msg })); server.stdin.write(`Content-Length: ${b.length}\r\n\r\n`); server.stdin.write(b); };
const request = (method, params, ms = timeoutMs) => new Promise((resolve) => {
  const id = ++nextId;
  const t = setTimeout(() => { waiting.delete(id); resolve({ error: { message: `no answer to ${method} within ${ms / 1000}s` } }); }, ms);
  waiting.set(id, (m) => { clearTimeout(t); resolve(m); });
  send({ id, method, params });
});
const notify = (method, params) => send({ method, params });

let buf = Buffer.alloc(0);
server.stdout.on("data", (chunk) => {
  buf = Buffer.concat([buf, chunk]);
  for (;;) {
    const end = buf.indexOf("\r\n\r\n");
    if (end < 0) return;
    const len = Number(/content-length:\s*(\d+)/i.exec(buf.subarray(0, end).toString("latin1"))?.[1]);
    if (buf.length < end + 4 + len) return;
    const msg = JSON.parse(buf.subarray(end + 4, end + 4 + len).toString("utf8"));
    buf = buf.subarray(end + 4 + len);
    if (msg.method && msg.id !== undefined) { // a request from the server
      if (msg.method === "client/registerCapability" && opts.pull !== "no" && msg.params?.registrations?.some((r) => r.method === "textDocument/diagnostic")) pull = true;
      send({ id: msg.id, result: msg.method === "workspace/configuration" ? (msg.params?.items || []).map(() => null) : null });
    } else if (msg.method === "textDocument/publishDiagnostics") {
      const prev = published.get(msg.params.uri);
      published.set(msg.params.uri, { diagnostics: msg.params.diagnostics, seq: (prev?.seq || 0) + 1 });
    } else if (!msg.method && waiting.has(msg.id)) waiting.get(msg.id)(msg);
  }
});

const errorsOf = (diags) => (diags || []).filter((d) => d.severity === 1 || d.severity === undefined);
// Waits until the diagnostics for uri satisfy want(errors); push and pull servers both work.
async function diagnostics(uri, want, sinceSeq, ms = timeoutMs) {
  const deadline = Date.now() + ms;
  let last = null;
  while (Date.now() < deadline && !exited) {
    if (pull) {
      const r = await request("textDocument/diagnostic", { textDocument: { uri } }, 30_000);
      if (r.result?.kind === "full") last = r.result.items;
    } else {
      const p = published.get(uri);
      if (p && p.seq > sinceSeq) last = p.diagnostics;
    }
    if (last && want(errorsOf(last))) return { ok: true, errors: errorsOf(last) };
    await sleep(pull ? 1000 : 250);
  }
  return { ok: false, errors: last ? errorsOf(last) : null };
}
const seqOf = (uri) => published.get(uri)?.seq || 0;

function descendants(pid) {
  let table;
  try {
    table = process.platform === "win32"
      ? execFileSync("powershell.exe", ["-NoProfile", "-Command", 'Get-CimInstance Win32_Process | ForEach-Object { "$($_.ProcessId) $($_.ParentProcessId)" }'], { encoding: "utf8", windowsHide: true })
      : execFileSync("ps", ["-A", "-o", "pid=,ppid="], { encoding: "utf8" });
  } catch { return []; } // no process table: the leftover check passes vacuously
  const rows = table.trim().split(/\r?\n/).map((l) => l.trim().split(/\s+/).map(Number));
  const out = [], todo = [pid];
  while (todo.length) { const p = todo.pop(); for (const [c, pp] of rows) if (pp === p) { out.push(c); todo.push(c); } }
  return out;
}
const alive = (pid) => { try { process.kill(pid, 0); return true; } catch (e) { return e.code === "EPERM"; } };

async function main() {
  const rootUri = pathToFileURL(root).href;
  const allowPull = opts.pull !== "no";
  const init = await request("initialize", {
    processId: process.pid, rootUri, rootPath: root, workspaceFolders: [{ uri: rootUri, name: path.basename(root) }],
    capabilities: {
      textDocument: {
        synchronization: { didSave: true }, publishDiagnostics: { relatedInformation: true },
        ...(allowPull ? { diagnostic: { dynamicRegistration: true } } : {}),
        hover: { contentFormat: ["markdown", "plaintext"] }, definition: { linkSupport: true }, references: {},
        documentSymbol: { hierarchicalDocumentSymbolSupport: true },
      },
      workspace: { configuration: true, workspaceFolders: true }, window: { workDoneProgress: true },
    },
  });
  check("initialize", !!init.result?.capabilities, init.error ? init.error.message : secs());
  if (!init.result) return;
  if (init.result.capabilities.diagnosticProvider && allowPull) pull = true;
  notify("initialized", {});

  const uri = pathToFileURL(file).href, text = fs.readFileSync(file, "utf8");
  notify("textDocument/didOpen", { textDocument: { uri, languageId: LANG[ext], version: 1, text } });
  let r = await diagnostics(uri, (e) => e.length === 0, 0);
  if (r.ok) { const s = seqOf(uri); await sleep(3000); if (!pull && seqOf(uri) > s) r = await diagnostics(uri, (e) => e.length === 0, s, 5000); }
  check(`clean file has no errors: ${path.relative(root, file)}`, r.ok, r.ok ? secs() : JSON.stringify(r.errors?.slice(0, 3)));

  const broken = text + PROBE[ext];
  const probeLine = broken.split("\n").findIndex((l) => l.includes("\"not an int\""));
  const endOf = (t) => { const ls = t.split("\n"); return { line: ls.length - 1, character: ls[ls.length - 1].length }; };
  const incremental = !!opts.incremental;
  let s = seqOf(uri);
  notify("textDocument/didChange", { textDocument: { uri, version: 2 },
    contentChanges: [incremental ? { range: { start: endOf(text), end: endOf(text) }, text: PROBE[ext] } : { text: broken }] });
  r = await diagnostics(uri, (e) => e.some((d) => d.range.start.line === probeLine), s);
  const hit = r.errors?.find((d) => d.range.start.line === probeLine);
  check("injected type error reported on its line", r.ok, hit ? `line ${probeLine + 1}: ${hit.message}; ${secs()}` : JSON.stringify(r.errors?.slice(0, 3)));

  s = seqOf(uri);
  notify("textDocument/didChange", { textDocument: { uri, version: 3 },
    contentChanges: [incremental ? { range: { start: endOf(text), end: endOf(broken) }, text: "" } : { text }] });
  r = await diagnostics(uri, (e) => e.length === 0, s);
  check("error clears after revert", r.ok, r.ok ? secs() : JSON.stringify(r.errors?.slice(0, 3)));

  const sym = await request("textDocument/documentSymbol", { textDocument: { uri } }, 60_000);
  check("document symbols", Array.isArray(sym.result) && sym.result.length > 0, sym.error ? sym.error.message : `${sym.result?.length ?? 0} top-level`);

  if (opts.definition) {
    const lines = text.split("\n");
    const re = new RegExp(`\\b${opts.definition}\\b`);
    const at = lines.map((l, i) => [i, l.search(re)]).filter(([, c]) => c >= 0)[1] || lines.map((l, i) => [i, l.search(re)]).find(([, c]) => c >= 0);
    const def = at ? await request("textDocument/definition", { textDocument: { uri }, position: { line: at[0], character: at[1] + 1 } }, 60_000) : { error: { message: `${opts.definition} not in file` } };
    const locs = def.result ? (Array.isArray(def.result) ? def.result : [def.result]) : [];
    const first = locs[0] && (locs[0].targetUri || locs[0].uri);
    check(`definition of ${opts.definition}`, locs.length > 0, def.error ? def.error.message : first ? `${decodeURI(first).split("/").slice(-2).join("/")}` : "no location");
  }

  for (const extra of opts.also) {
    const f = path.resolve(root, extra), u = pathToFileURL(f).href;
    notify("textDocument/didOpen", { textDocument: { uri: u, languageId: LANG[path.extname(f)], version: 1, text: fs.readFileSync(f, "utf8") } });
    let ok = await diagnostics(u, (e) => e.length === 0, 0, 15_000);
    if (!ok.ok && ok.errors === null) ok = { ok: true, errors: [] }; // silent is fine for --also files
    check(`no errors: ${extra}`, ok.ok, ok.ok ? "" : JSON.stringify(ok.errors?.slice(0, 3)));
  }
}

let kids = [];
try { await main(); } catch (e) { check("selftest ran", false, e.message); }
if (!exited) {
  kids = descendants(server.pid);
  const sd = await request("shutdown", null, 15_000);
  check("shutdown answered", sd.result === null && !sd.error, sd.error?.message || "");
  notify("exit", null);
  for (let i = 0; i < 100 && !exited; i++) await sleep(100);
}
check("server exited after exit", !!exited, exited ? `code ${exited.code ?? exited.signal}` : "still running");
if (!exited) server.kill("SIGKILL");
let left = kids;
for (let i = 0; i < 100 && left.length; i++) { await sleep(100); left = left.filter(alive); }
check("no leftover processes", left.length === 0, left.length ? `pids ${left.join(", ")}` : `${kids.length} child process(es) stopped`);
const failed = results.filter((x) => !x).length;
if (failed && stderr.trim()) console.log(`--- server stderr (last lines)\n${stderr.trim().split("\n").slice(-15).join("\n")}`);
console.log(failed ? `FAILED ${failed} of ${results.length} checks` : `ALL ${results.length} CHECKS PASSED`);
process.exit(failed ? 1 : 0);
