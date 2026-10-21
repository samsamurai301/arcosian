#!/usr/bin/env node
// unity-csharp-lsp: runs csharp-ls for a Unity project so Claude Code gets C# diagnostics and navigation.
// Unity mode: when the Editor has written its project files (a .slnx or .sln next to Assets/, from the Visual Studio
// Editor package), csharp-ls loads them unchanged and every script is covered.
// Engine-free mode: without them (Editor never opened, no licence, CI) the launcher builds a solution in the plugin
// data folder from the asmdefs marked noEngineReferences (the game logic in this template) and silences every other
// .cs file, which without Unity's assemblies would only report false errors.
// GS_UNITY_CSHARP_MODE=auto|unity|engine-free overrides the choice. stdout carries protocol only; GS_LSP_LOG=<file>
// traces messages.
import { spawn, spawnSync } from "node:child_process";
import crypto from "node:crypto";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const env = process.env;
const setting = (v) => (v && !v.includes("${") ? v.trim() : ""); // an unset plugin option can arrive empty or unexpanded
const log = (m) => process.stderr.write(`unity-csharp-lsp: ${m}\n`);
const traceFile = setting(env.GS_LSP_LOG);
const trace = (dir, msg) => {
  if (!traceFile) return;
  const s = JSON.stringify(msg);
  fs.appendFileSync(traceFile, `${new Date().toISOString()} ${dir} ${s.length > 4000 ? s.slice(0, 4000) + "..." : s}\n`);
};
const GENERATOR = "unity-csharp-lsp 1"; // part of the fingerprint: bump when the generated projects change shape
const SKIP_DIRS = new Set(["Library", "Temp", "Logs", "obj", "Obj", "Build", "Builds", "UserSettings", "node_modules"]);
const isDir = (p) => { try { return fs.statSync(p).isDirectory(); } catch { return false; } };
const isUnityProject = (d) => isDir(path.join(d, "Assets")) && fs.existsSync(path.join(d, "ProjectSettings", "ProjectVersion.txt"));

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
  const forced = setting(env.GS_UNITY_PROJECT);
  if (forced) return isUnityProject(forced) ? path.resolve(forced) : null;
  for (let d = path.resolve(start); ; d = path.dirname(d)) {
    if (isUnityProject(d)) return d;
    if (path.dirname(d) === d) break;
  }
  let level = [path.resolve(start)], seen = 0;
  for (let depth = 0; depth < 3 && level.length && seen < 5000; depth++) {
    const next = [], found = [];
    for (const dir of level) {
      let entries = [];
      try { entries = fs.readdirSync(dir, { withFileTypes: true }); } catch { continue; }
      for (const e of entries.sort((a, b) => a.name.localeCompare(b.name))) {
        if (!e.isDirectory() || e.name.startsWith(".") || SKIP_DIRS.has(e.name) || e.name === "Assets") continue;
        const sub = path.join(dir, e.name);
        seen++;
        (isUnityProject(sub) ? found : next).push(sub);
      }
    }
    if (found.length) {
      if (found.length > 1) log(`found ${found.length} Unity projects, using ${found[0]} (set GS_UNITY_PROJECT to pick another)`);
      return found[0];
    }
    level = next;
  }
  return null;
}

function findExe(names, extra) {
  const exts = process.platform === "win32" ? [".exe", ""] : [""]; // Node cannot spawn .cmd shims without a shell
  const candidates = [...extra];
  for (const dir of (env.PATH || "").split(path.delimiter)) for (const n of names) if (dir) candidates.push(path.join(dir, n));
  for (const c of candidates) for (const x of exts) {
    if (!c) continue;
    try { fs.accessSync(c + x, fs.constants.X_OK); if (fs.statSync(c + x).isFile()) return c + x; } catch {}
  }
  return null;
}

// Unity skips folders that start with "." or end with "~" when it compiles.
function walk(dir, onFile) {
  let entries = [];
  try { entries = fs.readdirSync(dir, { withFileTypes: true }); } catch { return; }
  for (const e of entries) {
    if (e.name.startsWith(".") || e.name.endsWith("~")) continue;
    const p = path.join(dir, e.name);
    if (e.isDirectory()) walk(p, onFile); else onFile(p);
  }
}

function readAsmdefs(root) {
  const list = [];
  walk(path.join(root, "Assets"), (f) => {
    if (!f.endsWith(".asmdef")) return;
    try {
      const raw = fs.readFileSync(f, "utf8"), def = JSON.parse(raw);
      const guid = /^guid:\s*([0-9a-f]+)/m.exec(fs.existsSync(f + ".meta") ? fs.readFileSync(f + ".meta", "utf8") : "")?.[1];
      list.push({ file: f, dir: path.dirname(f), raw, def, name: def.name, guid });
    } catch (e) { log(`skipped ${f}: ${e.message}`); }
  });
  return list;
}

// Unity's own csc.rsp options that change how the scripts compile.
function rspOptions(root) {
  const rsp = path.join(root, "Assets", "csc.rsp");
  const text = fs.existsSync(rsp) ? fs.readFileSync(rsp, "utf8") : "";
  const nullable = [...text.matchAll(/^-nullable(?::(\S+)|([+-]))?\s*$/gim)].pop();
  return {
    text,
    langVersion: [...text.matchAll(/^-langversion:(\S+)/gim)].pop()?.[1] || "9.0",
    nullable: !nullable ? "disable" : nullable[1] || (nullable[2] === "-" ? "disable" : "enable"),
    defines: [...text.matchAll(/^-define:(\S+)/gim)].flatMap((m) => m[1].split(/[;,]/)).filter(Boolean),
  };
}

const xml = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
const msbuildPath = (p) => xml(p.split(path.sep).join("/").replace(/%/g, "%25").replace(/\$/g, "%24").replace(/@/g, "%40").replace(/;/g, "%3B").replace(/'/g, "%27"));

// Builds (or reuses) a solution of the engine-free asmdefs. Returns { solution, scopes } or { error }.
function engineFreeSolution(root, dotnet) {
  const all = readAsmdefs(root);
  const free = all.filter((a) => a.def.noEngineReferences === true && a.name);
  if (!free.length) return { error: "no Unity-generated solution (.slnx/.sln) and no asmdef with noEngineReferences to check without Unity" };
  const byRef = new Map();
  for (const a of free) { byRef.set(a.name, a); if (a.guid) byRef.set(`GUID:${a.guid}`, a); }
  const rsp = rspOptions(root);
  const base = path.join(setting(env.CLAUDE_PLUGIN_DATA) || path.join(os.tmpdir(), "arcosian-unity"), "unity-csharp",
    crypto.createHash("sha1").update(root).digest("hex").slice(0, 12));
  const fingerprint = crypto.createHash("sha1").update([GENERATOR, root, rsp.text, ...all.map((a) => a.file + "\n" + a.raw)].join("\0")).digest("hex");
  const scopes = free.map((a) => ({
    dir: a.dir,
    // Folders holding another asmdef belong to that assembly, not this one.
    exclude: all.filter((b) => b !== a && b.dir !== a.dir && b.dir.startsWith(a.dir + path.sep)).map((b) => b.dir),
  }));
  const solution = path.join(base, "EngineFree.slnx");
  const ready = fs.existsSync(path.join(base, "fingerprint")) && fs.readFileSync(path.join(base, "fingerprint"), "utf8") === fingerprint
    && free.every((a) => fs.existsSync(path.join(base, a.name, "obj", "project.assets.json")));
  if (ready) return { solution, scopes };

  fs.rmSync(base, { recursive: true, force: true });
  for (const [i, a] of free.entries()) {
    const refs = (a.def.references || []).map((r) => byRef.get(r)).filter(Boolean);
    const proj = [
      '<Project Sdk="Microsoft.NET.Sdk">',
      "  <PropertyGroup>",
      "    <TargetFramework>netstandard2.1</TargetFramework>",
      `    <LangVersion>${xml(rsp.langVersion)}</LangVersion>`,
      `    <Nullable>${xml(rsp.nullable)}</Nullable>`,
      `    <AssemblyName>${xml(a.name)}</AssemblyName>`,
      `    <AllowUnsafeBlocks>${a.def.allowUnsafeCode === true}</AllowUnsafeBlocks>`,
      `    <DefineConstants>$(DefineConstants);${xml(rsp.defines.join(";"))}</DefineConstants>`,
      "    <EnableDefaultCompileItems>false</EnableDefaultCompileItems>",
      "    <GenerateAssemblyInfo>false</GenerateAssemblyInfo>",
      "  </PropertyGroup>",
      "  <ItemGroup>",
      `    <Compile Include="${msbuildPath(a.dir)}/**/*.cs" />`,
      ...scopes[i].exclude.map((d) => `    <Compile Remove="${msbuildPath(d)}/**" />`),
      "  </ItemGroup>",
      ...(refs.length ? ["  <ItemGroup>", ...refs.map((r) => `    <ProjectReference Include="../${xml(r.name)}/${xml(r.name)}.csproj" />`), "  </ItemGroup>"] : []),
      "</Project>",
      "",
    ].join("\n");
    fs.mkdirSync(path.join(base, a.name), { recursive: true });
    fs.writeFileSync(path.join(base, a.name, `${a.name}.csproj`), proj);
  }
  fs.writeFileSync(solution, ["<Solution>", ...free.map((a) => `  <Project Path="${xml(a.name)}/${xml(a.name)}.csproj" />`), "</Solution>", ""].join("\n"));
  const r = spawnSync(dotnet, ["restore", solution, "--nologo", "-v", "q"], { cwd: base, encoding: "utf8", timeout: 150_000, env: { ...env, ...DOTNET_ENV }, windowsHide: true });
  if (r.status !== 0) return { error: `dotnet restore failed for the engine-free solution: ${(r.stdout + r.stderr).trim().split("\n").slice(-3).join(" ")}` };
  fs.writeFileSync(path.join(base, "fingerprint"), fingerprint);
  log(`engine-free solution with ${free.length} assemblies: ${free.map((a) => a.name).join(", ")}`);
  return { solution, scopes };
}

function unitySolution(root) {
  const names = fs.readdirSync(root).filter((n) => /\.slnx?$/i.test(n)).sort();
  const own = path.basename(root);
  const pick = names.find((n) => n === `${own}.slnx`) || names.find((n) => n === `${own}.sln`) || names.find((n) => n.endsWith(".slnx")) || names[0];
  return pick ? path.join(root, pick) : null;
}

const DOTNET_ENV = { DOTNET_CLI_TELEMETRY_OPTOUT: "1", DOTNET_NOLOGO: "1", DOTNET_SKIP_FIRST_TIME_EXPERIENCE: "1" };
const home = os.homedir();
const real = (p) => {
  try { return fs.realpathSync.native(p); } catch {}
  try { return path.join(fs.realpathSync.native(path.dirname(p)), path.basename(p)); } catch { return p; }
};
const startDir = setting(env.CLAUDE_PROJECT_DIR) || process.cwd();
const found = findProject(startDir);
const root = found && real(found); // generated projects and scopes use real paths (symlinks such as macOS /tmp resolved)
const mode = (setting(env.GS_UNITY_CSHARP_MODE) || "auto").toLowerCase();
let failure = null, scopes = null, solution = null;
const csharpLs = findExe(["csharp-ls"], [setting(env.GS_CSHARP_LS), path.join(home, ".dotnet", "tools", "csharp-ls")]);
const dotnet = findExe(["dotnet"], [env.DOTNET_ROOT && path.join(env.DOTNET_ROOT, "dotnet"), env.ProgramFiles && path.join(env.ProgramFiles, "dotnet", "dotnet"),
  "/usr/local/share/dotnet/dotnet", path.join(home, ".dotnet", "dotnet")]);
if (!root) failure = `no Unity project (Assets/ and ProjectSettings/ProjectVersion.txt) in ${startDir}, its parent folders or three levels below; start Claude Code in the project or set GS_UNITY_PROJECT`;
else if (!csharpLs) failure = "csharp-ls not found; install the .NET 10 SDK, then run: dotnet tool install --global csharp-ls";
else if (!["auto", "unity", "engine-free"].includes(mode)) failure = `GS_UNITY_CSHARP_MODE must be auto, unity or engine-free, not ${mode}`;
else {
  solution = mode === "engine-free" ? null : unitySolution(root);
  if (!solution && mode === "unity") failure = `no Unity-generated .slnx or .sln in ${root}; open the project in Unity with an external script editor set, or use engine-free mode`;
  else if (!solution) {
    if (!dotnet) failure = "dotnet not found; install the .NET 10 SDK (csharp-ls needs it too)";
    else {
      const r = engineFreeSolution(root, dotnet);
      if (r.error) failure = `${r.error}. For full coverage open the project in Unity once with the Visual Studio Editor package and an external script editor (Visual Studio Code, Visual Studio or Rider) so it writes the solution.`;
      else ({ solution, scopes } = r);
    }
  }
}

// Engine-free mode: files outside the generated assemblies are answered here and never reach csharp-ls. csharp-ls
// sees real paths, and the client gets back the exact URI strings it sent.
const uriPath = (uri) => { try { return uri.startsWith("file:") ? fileURLToPath(new URL(uri)) : null; } catch { return null; } };
const inScope = (uri) => {
  if (!scopes) return true;
  const p = uriPath(uri) && real(uriPath(uri));
  return !!p && p.endsWith(".cs") && scopes.some((s) => p.startsWith(s.dir + path.sep) && !s.exclude.some((x) => p.startsWith(x + path.sep)));
};
const emptyAnswer = (method) => (method === "textDocument/diagnostic" ? { kind: "full", items: [] } : method === "textDocument/documentSymbol" ? [] : null);
const URI_KEYS = new Set(["uri", "targetUri", "oldUri", "newUri"]);
const clientUris = new Map();
const pathKey = (p) => (process.platform === "linux" ? p : p.toLowerCase()); // macOS and Windows ignore case by default
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

let child = null, shutdownSeen = false, quitting = false;
const forwardedMethods = new Map();
function toClient(msg) { trace("<-", msg); process.stdout.write(encode(msg)); }

function quit(code) {
  if (quitting) return;
  quitting = true;
  if (!child || child.exitCode !== null) process.exit(code);
  const force = setTimeout(() => { try { child.kill("SIGKILL"); } catch {} process.exit(code); }, 5000);
  child.once("exit", () => { clearTimeout(force); process.exit(code); });
  try { child.stdin?.end(); } catch {}
  child.kill("SIGTERM");
}

if (failure) {
  log(failure);
  process.stdin.on("data", frames((msg) => {
    if (msg.method === "exit") return quit(shutdownSeen ? 0 : 1);
    if (msg.method === "shutdown") { shutdownSeen = true; return toClient({ jsonrpc: "2.0", id: msg.id, result: null }); }
    if (msg.method && msg.id !== undefined) {
      toClient(msg.method === "initialize"
        ? { jsonrpc: "2.0", id: msg.id, error: { code: -32603, message: `C# language server unavailable: ${failure}`, data: { retry: false } } }
        : { jsonrpc: "2.0", id: msg.id, error: { code: -32002, message: failure } });
    }
  }));
  process.stdin.on("end", () => quit(1));
} else {
  const args = ["--solution", solution, "--loglevel", "warning"];
  if (traceFile && !scopes) args.push("--rpclog", traceFile);
  const childEnv = { ...env, ...DOTNET_ENV, ...(dotnet && !env.DOTNET_ROOT ? { DOTNET_ROOT: path.dirname(fs.realpathSync(dotnet)) } : {}) };
  log(`${scopes ? "engine-free" : "unity"} mode: csharp-ls on ${solution}`);
  // Unity mode passes the streams straight through; engine-free mode filters them.
  child = spawn(csharpLs, args, { cwd: root, env: childEnv, stdio: scopes ? ["pipe", "pipe", "inherit"] : "inherit", windowsHide: true });
  child.on("error", (e) => { log(`could not start csharp-ls: ${e.message}`); process.exit(1); });
  child.on("exit", (code, signal) => { if (!quitting) process.exit(code ?? (signal ? 1 : 0)); });
  for (const sig of ["SIGTERM", "SIGINT", "SIGHUP"]) process.on(sig, () => quit(0));
  if (scopes) {
    const toServer = (msg) => { trace("->", msg); child.stdin.write(encode(msg)); };
    process.stdin.on("data", frames((msg) => {
      const uri = msg.params?.textDocument?.uri;
      if (msg.method === "shutdown") shutdownSeen = true;
      if (uri && msg.method && !inScope(uri)) {
        if (msg.id !== undefined) toClient({ jsonrpc: "2.0", id: msg.id, result: emptyAnswer(msg.method) });
        return;
      }
      if (uri) remember(uri);
      if (msg.method && msg.id !== undefined) forwardedMethods.set(msg.id, msg.method);
      toServer(mapUris(msg, serverUri));
    }));
    process.stdin.on("end", () => quit(shutdownSeen ? 0 : 1));
    child.stdout.on("data", frames((msg) => {
      if (msg.method === "textDocument/publishDiagnostics" && !inScope(msg.params.uri)) msg.params.diagnostics = [];
      if (!msg.method && msg.id !== undefined && forwardedMethods.has(msg.id)) {
        if (forwardedMethods.get(msg.id) === "workspace/diagnostic" && Array.isArray(msg.result?.items)) msg.result.items = msg.result.items.filter((i) => inScope(i.uri));
        forwardedMethods.delete(msg.id);
      }
      toClient(mapUris(msg, clientUri));
    }));
    process.stdout.on("error", () => quit(1));
  }
}
