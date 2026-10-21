#!/usr/bin/env node
// Opt-in live smoke test for ONE provider: a dry run by default, ONE minimal real generation with --yes.
//
//   node test/live-smoke.mjs --provider <name> [--kind <kind>] [--yes] [--max-usd <n>] [--timeout-sec <n>]
//
// The provider's own key must be in the environment (never passed on the command line). Without --yes nothing is sent to the
// provider: the gateway is run against a local capture port and the exact request it would send (method, URL, header shapes,
// body) is printed with the estimated cost. With --yes the same gateway tool call is made for real, against the real host
// (or the GS_<PROVIDER>_BASE_URL you set), into a throwaway project under the OS temp dir, with a spending cap of max-usd.
// This script is not part of run-tests.mjs; the offline suite only exercises it against local fake servers.
import { spawn } from "node:child_process";
import http from "node:http";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { ENV_KEY, baseFor } from "../providers/index.mjs";

const SERVER = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../server.mjs");
const PROMPT_IMG = "a small red apple icon, flat colours, plain white background";

// provider -> kind -> one minimal tool call (the first kind is the default). Pick the cheapest call that still proves
// auth, endpoint and response parsing; the estimate printed comes from the gateway's own pricing.json.
const CASES = {
  gemini: { image: { tool: "image_generate", args: { prompt: PROMPT_IMG, kind: "icon", provider: "gemini", size: "1024" }, flow: "one POST /interactions; the image is decoded from steps[].content[]" },
    tts: { tool: "audio_voice", args: { text: "Welcome back, hero.", provider: "gemini", voice_id: "Kore" }, flow: "one POST /interactions; the WAV audio block is decoded from steps[].content[]" } },
  lyria: { music: { tool: "audio_music", args: { prompt: "short calm acoustic guitar loop", duration_sec: 30, provider: "lyria", model: "lyria-3-clip-preview" }, flow: "one POST /interactions (30 s clip model); the MP3 block is decoded" } },
  openai: { image: { tool: "image_generate", args: { prompt: PROMPT_IMG, kind: "icon", provider: "openai", size: "1024", quality: "low" }, flow: "one POST /images/generations; data[0].b64_json is decoded" } },
  recraft: { image: { tool: "image_generate", args: { prompt: PROMPT_IMG, kind: "icon", provider: "recraft", size: "1024" }, flow: "one POST /images/generations, then a download of data[0].url" },
    vector: { tool: "image_generate", args: { prompt: PROMPT_IMG, kind: "icon", provider: "recraft", model: "recraftv4_1_vector", size: "1024" }, flow: "one POST /images/generations (vector model), then a download of the SVG url" } },
  fal: { image: { tool: "image_generate", args: { prompt: PROMPT_IMG, kind: "icon", provider: "fal", size: "512" }, flow: "POST to the queue, poll status_url until COMPLETED, GET response_url, download images[0].url" } },
  stability: { image: { tool: "image_generate", args: { prompt: PROMPT_IMG, kind: "icon", provider: "stability", size: "1024" }, flow: "one POST /stable-image/generate/core (Accept image/*)" },
    audio: { tool: "audio_sfx", args: { prompt: "short wooden door creak", duration_sec: 1, provider: "stability" }, flow: "POST /audio/stable-audio/text-to-audio (202 {id}), then poll GET /audio/results/{id} until 200" } },
  tripo: { model3d: { tool: "model3d_generate", args: { prompt: "a small wooden crate", provider: "tripo", face_limit: 500, wait_sec: 0 }, async3d: true, flow: "one billed POST /generation/text-to-model, then free polls of GET /tasks/{id} and a download of output.model_url" } },
  meshy: { model3d: { tool: "model3d_generate", args: { prompt: "a small wooden crate", provider: "meshy", wait_sec: 0 }, async3d: true, flow: "one billed POST /v2/text-to-3d (preview), then free polls of GET /v2/text-to-3d/{id} and a download of model_urls.glb" } },
  elevenlabs: { sfx: { tool: "audio_sfx", args: { prompt: "short coin pickup chime", duration_sec: 0.5, provider: "elevenlabs" }, flow: "one POST /sound-generation; the MP3 bytes are saved" },
    tts: { tool: "audio_voice", args: { text: "Welcome back, hero.", provider: "elevenlabs" }, flow: "one POST /text-to-speech/{voice_id}; the MP3 bytes are saved" },
    music: { tool: "audio_music", args: { prompt: "short calm acoustic guitar loop", duration_sec: 3, provider: "elevenlabs" }, flow: "one POST /music (3 s, the minimum length); the MP3 bytes are saved" },
    dialogue: { tool: "audio_voice", args: { lines: [{ text: "Hello there." }, { text: "Hi, hero." }], provider: "elevenlabs" }, flow: "one POST /text-to-dialogue; the MP3 bytes are saved" } },
};

function usage() {
  const rows = Object.entries(CASES).map(([p, k]) => `  ${p.padEnd(11)} ${(ENV_KEY[p] || "").padEnd(19)} ${Object.keys(k).join(", ")} (default ${Object.keys(k)[0]})`).join("\n");
  return `usage: node test/live-smoke.mjs --provider <name> [--kind <kind>] [--yes] [--max-usd <n>] [--timeout-sec <n>]

  --provider   one of the providers below (required); its key must be set in the environment
  --kind       which minimal call to make (default: the first kind listed)
  --yes        really send ONE minimal request (billed by the provider); without it this is a dry run
  --max-usd    spending cap of the throwaway project (default: 1.5x the estimate, at least 0.25)
  --timeout-sec  how long to wait for 3D tasks (default 900)

  provider    key variable        kinds
${rows}
`;
}
function parseArgs(argv) {
  const o = {};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--yes") o.yes = true;
    else if (a === "--help" || a === "-h") o.help = true;
    else if (a.startsWith("--")) { const [k, v] = a.slice(2).split("="); o[k] = v ?? argv[++i]; }
    else { o.bad = a; }
  }
  return o;
}
const die = (msg, code = 2) => { process.stderr.write(`${msg}\n`); process.exit(code); };

// ---- a gateway child process spoken to over stdio (newline-delimited JSON-RPC) ----
function startGateway(env) {
  const proc = spawn(process.execPath, [SERVER], { env, stdio: ["pipe", "pipe", "pipe"] });
  const waiting = new Map();
  let buf = "", err = "", id = 0;
  proc.stdout.on("data", (d) => {
    buf += d;
    for (let i; (i = buf.indexOf("\n")) >= 0;) { const m = JSON.parse(buf.slice(0, i)); buf = buf.slice(i + 1); waiting.get(m.id)?.(m); }
  });
  proc.stderr.on("data", (d) => (err += d));
  const rpc = (method, params) => new Promise((resolve) => { const n = ++id; waiting.set(n, resolve); proc.stdin.write(JSON.stringify({ jsonrpc: "2.0", id: n, method, params }) + "\n"); });
  return {
    err: () => err,
    async init() { await rpc("initialize", { protocolVersion: "2025-06-18", capabilities: {}, clientInfo: { name: "live-smoke", version: "1" } }); },
    async call(name, args) { const r = await rpc("tools/call", { name, arguments: args }); if (!r.result) throw new Error(`RPC error: ${JSON.stringify(r.error)}`); return { isError: !!r.result.isError, ...JSON.parse(r.result.content[0].text) }; },
    close: () => new Promise((resolve) => { proc.on("close", resolve); proc.stdin.end(); }),
  };
}
function mkProject(capUsd) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "gs-live-"));
  fs.mkdirSync(path.join(root, ".gamestudio", "assets"), { recursive: true });
  fs.writeFileSync(path.join(root, ".gamestudio", "config.json"), JSON.stringify({ schema_version: "1.0", paths: { generated_dir: "assets/generated/" }, budgets: { asset_usd_cap: capUsd, per_call_usd_cap: capUsd } }));
  return root;
}
// Child environment: only the one provider key, mock mode off, no inherited caps.
function childEnv(provider, extra = {}) {
  const env = { ...process.env, GS_MOCK: "", GS_ASSET_BUDGET_USD: "", ...extra };
  for (const v of Object.values(ENV_KEY)) delete env[v];
  env[ENV_KEY[provider]] = process.env[ENV_KEY[provider]];
  return env;
}

// ---- printing the captured request ----
const shorten = (v) => (typeof v === "string" && v.length > 120 ? `<${v.length} chars: ${v.slice(0, 24)}...>` : Array.isArray(v) ? v.map(shorten) : v && typeof v === "object" ? Object.fromEntries(Object.entries(v).map(([k, x]) => [k, shorten(x)])) : v);
function describeBody(req) {
  const ct = req.headers["content-type"] || "";
  if (!req.body.length) return "(no body)";
  if (/multipart\/form-data/i.test(ct)) {
    const boundary = (ct.match(/boundary=(.+)$/) || [])[1], out = [];
    for (const part of req.body.toString("latin1").split(`--${boundary}`).slice(1, -1)) {
      const [head, ...rest] = part.replace(/^\r\n/, "").split("\r\n\r\n"), data = rest.join("\r\n\r\n").replace(/\r\n$/, "");
      const name = (head.match(/name="([^"]+)"/) || [])[1], file = (head.match(/filename="([^"]*)"/) || [])[1];
      out.push(file !== undefined ? `  file ${name}: ${file} (${(head.match(/content-type: ([^\r\n]+)/i) || [])[1] || "?"}, ${data.length} bytes)` : `  field ${name} = ${data.length > 200 ? `${data.slice(0, 200)}...` : data}`);
    }
    return `multipart/form-data\n${out.join("\n")}`;
  }
  try { return JSON.stringify(shorten(JSON.parse(req.body.toString("utf8"))), null, 2).replace(/^/gm, "  ").trimStart(); } catch { return `${req.body.length} bytes (${ct || "no content-type"})`; }
}
function printRequest(provider, req, key) {
  const hide = (s) => String(s).split(key).join(`<${ENV_KEY[provider]}>`);
  const lines = Object.entries(req.headers).filter(([k, v]) => !["host", "connection", "content-length", "accept-encoding", "accept-language", "sec-fetch-mode", "user-agent"].includes(k) && !(k === "accept" && v === "*/*")).map(([k, v]) => `  ${k}: ${hide(v)}`);
  console.log(`first request the gateway sends:\n  ${req.method} ${baseFor(provider)}${hide(req.url)}\n${lines.join("\n")}\n  body: ${describeBody(req)}`);
}

async function main() {
  const o = parseArgs(process.argv.slice(2));
  if (o.help) { process.stdout.write(usage()); return 0; }
  if (o.bad) die(`unexpected argument ${o.bad}\n${usage()}`);
  if (!o.provider) die(`--provider is required\n${usage()}`);
  const kinds = CASES[o.provider];
  if (!kinds) die(`unknown provider "${o.provider}"\n${usage()}`);
  const kind = o.kind || Object.keys(kinds)[0], c = kinds[kind];
  if (!c) die(`provider ${o.provider} has no kind "${kind}" (try: ${Object.keys(kinds).join(", ")})`);
  const keyVar = ENV_KEY[o.provider], key = (process.env[keyVar] || "").trim();
  if (!key) die(`${keyVar} is not set: export your own ${o.provider} key first (it is read from the environment only)`);

  console.log(`studio-gateway live smoke test: provider=${o.provider} kind=${kind} tool=${c.tool}`);
  // 1. the gateway's own estimate (a dry_run call in a throwaway project: no network)
  const probeRoot = mkProject(10), probe = startGateway(childEnv(o.provider, { CLAUDE_PROJECT_DIR: probeRoot }));
  await probe.init();
  const est = await probe.call(c.tool, { ...c.args, dry_run: true });
  await probe.close();
  fs.rmSync(probeRoot, { recursive: true, force: true });
  if (!est.ok) die(`could not prepare the call: ${est.error}`, 1);
  const estimate = est.estimated_usd_if_real ?? 0, cap = o["max-usd"] !== undefined ? Number(o["max-usd"]) : Math.max(0.25, Math.ceil(estimate * 150) / 100);
  if (!Number.isFinite(cap) || cap <= 0) die("--max-usd must be a positive number");
  console.log(`call: ${c.tool} ${JSON.stringify(c.args)}`);
  console.log(`estimated cost: $${Number(estimate).toFixed(4)} (gateway price list for model ${est.model}; the provider bills the real amount)`);
  console.log(`spending cap of the throwaway project: $${cap}`);

  if (!o.yes) {
    // 2a. dry run: capture the first request on a local port
    let captured = null;
    const srv = http.createServer((req, res) => {
      const chunks = [];
      req.on("data", (d) => chunks.push(d));
      req.on("end", () => { captured ||= { method: req.method, url: req.url, headers: req.headers, body: Buffer.concat(chunks) }; res.writeHead(418, { "content-type": "application/json" }); res.end('{"dry_run":true}'); });
    });
    await new Promise((r) => srv.listen(0, "127.0.0.1", r));
    const root = mkProject(cap);
    const gw = startGateway(childEnv(o.provider, { CLAUDE_PROJECT_DIR: root, [`GS_${(o.provider === "lyria" ? "gemini" : o.provider).toUpperCase()}_BASE_URL`]: `http://127.0.0.1:${srv.address().port}`, GS_RETRY_BASE_MS: "1" }));
    await gw.init();
    await gw.call(c.tool, c.args).catch(() => {});
    await gw.close();
    srv.close();
    fs.rmSync(root, { recursive: true, force: true });
    console.log("mode: DRY RUN (nothing was sent to the provider)");
    if (captured) printRequest(o.provider, captured, key); else console.log("the gateway refused before sending a request (budget cap or arguments)");
    console.log(`then: ${c.flow}`);
    console.log("run again with --yes to send this for real (one billed generation).");
    return 0;
  }

  // 2b. live: ONE minimal real call into a throwaway project
  const root = mkProject(cap), gw = startGateway(childEnv(o.provider, { CLAUDE_PROJECT_DIR: root }));
  await gw.init();
  console.log(`mode: LIVE: sending ONE real request to ${baseFor(o.provider)} (project ${root})`);
  let r = await gw.call(c.tool, c.args);
  if (c.async3d && r.ok && r.pending) {
    const deadline = Date.now() + (Number(o["timeout-sec"]) || 900) * 1000;
    console.log(`task ${r.task_id} started (stage ${r.stage}); polling is free`);
    while (r.ok && r.pending && Date.now() < deadline) {
      r = await gw.call("model3d_status", { provider: o.provider, task_id: r.task_id, wait_sec: 20 });
      if (r.pending) console.log(`  stage ${r.stage}: ${r.progress ?? "?"}%`);
    }
    if (r.pending) { console.log(`still running after the timeout: collect it later with model3d_status {provider: "${o.provider}", task_id: "${r.task_id}"} and project_dir ${root}`); await gw.close(); return 1; }
  }
  await gw.close();
  if (!r.ok) { console.error(`FAILED: ${r.error}`); return 1; }
  const readJson = (rel) => JSON.parse(fs.readFileSync(path.join(root, ".gamestudio", rel), "utf8"));
  const manifest = readJson("assets/manifest.json").assets.at(-1), budget = readJson("budget.json");
  console.log(`OK: ${r.files.map((f) => `${path.join(root, f.path)} (${f.bytes} bytes)`).join(", ")}`);
  console.log(`manifest: provider=${manifest.provider} model=${manifest.model} status=${manifest.status} cost_usd=${manifest.cost_usd} sha256=${manifest.sha256.slice(0, 12)}...`);
  console.log(`ledger: spent_usd=${budget.spent_usd} of cap $${budget.cap_usd} (${budget.ledger.length} entries)`);
  if (r.notes) console.log(`notes: ${r.notes.join(" | ")}`);
  return 0;
}
process.exit(await main().catch((e) => { console.error(`error: ${e.message}`); return 1; }));
