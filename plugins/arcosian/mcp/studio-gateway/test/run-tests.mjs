#!/usr/bin/env node
// Offline tests for studio-gateway: spawns the real server over stdio. Part 1 runs in mock mode. Part 2 runs every real-provider
// request path against ONE local fake HTTP server that records each request, so the method, path, auth header shape and body
// fields are asserted against the documented provider APIs, and the responses are checked to end up as files, manifest entries
// and budget ledger entries. Part 3 covers 3D stage chaining (jobs file) and part 4 the opt-in live-smoke script (dry run and
// --yes against the fake server). Nothing here talks to a real provider.
import { spawn } from "node:child_process";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import http from "node:http";
import zlib from "node:zlib";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";
import { crc32, makeGlb, makePng, makeSvg, makeWav } from "../lib/media.mjs";
import { estimate } from "../lib/pricing.mjs";

const SERVER = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../server.mjs");
const SMOKE = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "live-smoke.mjs");
const TOOLS = ["gs_status", "image_generate", "image_edit", "image_postprocess", "model3d_generate", "model3d_status", "audio_music", "audio_sfx", "audio_voice", "manifest_query", "manifest_update", "licence_check", "budget_status", "kb_search"];
const SECRET = "sk-test-secret-123456";
const KEYS = ["GEMINI_API_KEY", "OPENAI_API_KEY", "RECRAFT_API_KEY", "FAL_KEY", "TRIPO_API_KEY", "MESHY_API_KEY", "ELEVENLABS_API_KEY", "STABILITY_API_KEY"];
const NO_KEYS = Object.fromEntries(KEYS.map((k) => [k, ""]));

class Client {
  constructor(env) {
    this.proc = spawn("node", [SERVER], { env: { ...process.env, ...NO_KEYS, GS_MOCK: "", GS_ASSET_BUDGET_USD: "", ...env }, stdio: ["pipe", "pipe", "pipe"] });
    this.waiting = new Map(); this.lines = []; this.err = ""; this.id = 0;
    let buf = "";
    this.proc.stdout.on("data", (d) => {
      buf += d;
      let i;
      while ((i = buf.indexOf("\n")) >= 0) {
        const msg = JSON.parse(buf.slice(0, i)); buf = buf.slice(i + 1);
        this.lines.push(msg);
        this.waiting.get(msg.id)?.(msg);
      }
    });
    this.proc.stderr.on("data", (d) => (this.err += d));
  }
  send(o) { this.proc.stdin.write(JSON.stringify(o) + "\n"); }
  request(method, params) {
    const id = ++this.id;
    return new Promise((resolve) => { this.waiting.set(id, resolve); this.send({ jsonrpc: "2.0", id, method, params }); });
  }
  async call(name, args = {}) {
    const r = await this.request("tools/call", { name, arguments: args });
    assert.ok(r.result, `tools/call ${name} returned an RPC error: ${JSON.stringify(r.error)}`);
    assert.equal(r.result.content[0].type, "text");
    return { isError: !!r.result.isError, ...JSON.parse(r.result.content[0].text) };
  }
  async close() { this.proc.stdin.end(); await new Promise((r) => this.proc.on("close", r)); }
}

// ---- helpers ----
const tmpDirs = []; // removed at the end of a passing run (kept for inspection when something fails)
function mkProject(config = {}) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), "gs-test-"));
  tmpDirs.push(root);
  const gs = path.join(root, ".gamestudio");
  fs.mkdirSync(path.join(gs, "assets"), { recursive: true });
  fs.writeFileSync(path.join(gs, "config.json"), JSON.stringify({ schema_version: "1.0", paths: { generated_dir: "assets/generated/" }, budgets: { asset_usd_cap: 5 }, revenue: { lifetime_gross_usd: 0, developer_annual_games_revenue_usd: 0 }, ...config }));
  return root;
}
const readJson = (root, rel) => JSON.parse(fs.readFileSync(path.join(root, ".gamestudio", rel), "utf8"));
const file = (root, rel) => fs.readFileSync(path.join(root, rel));
const sha = (buf) => crypto.createHash("sha256").update(buf).digest("hex");
const near = (a, b, msg = "value", tol = 1e-9) => assert.ok(Math.abs(a - b) < tol, `${msg}: ${a} != ${b}`);

function parsePng(buf) {
  assert.deepEqual([...buf.subarray(0, 8)], [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a], "PNG signature");
  let o = 8, ihdr, idat = [], sawEnd = false;
  while (o < buf.length) {
    const len = buf.readUInt32BE(o), type = buf.toString("ascii", o + 4, o + 8), data = buf.subarray(o + 8, o + 8 + len);
    assert.equal(buf.readUInt32BE(o + 8 + len), crc32(buf.subarray(o + 4, o + 8 + len)), `CRC of ${type}`);
    if (type === "IHDR") ihdr = { w: data.readUInt32BE(0), h: data.readUInt32BE(4), depth: data[8], color: data[9] };
    if (type === "IDAT") idat.push(data);
    if (type === "IEND") sawEnd = true;
    o += 12 + len;
  }
  assert.ok(sawEnd && o === buf.length, "IEND last");
  const raw = zlib.inflateSync(Buffer.concat(idat)), bpp = ihdr.color === 6 ? 4 : 3;
  assert.equal(raw.length, ihdr.h * (1 + ihdr.w * bpp), "inflated size");
  return { ...ihdr, raw };
}
function parseWav(buf) {
  assert.equal(buf.toString("ascii", 0, 4), "RIFF"); assert.equal(buf.toString("ascii", 8, 12), "WAVE");
  assert.equal(buf.readUInt16LE(20), 1, "PCM"); assert.equal(buf.readUInt16LE(22), 1, "mono");
  assert.equal(buf.readUInt32LE(24), 44100); assert.equal(buf.readUInt16LE(34), 16);
  assert.equal(buf.toString("ascii", 36, 40), "data");
  const n = buf.readUInt32LE(40);
  assert.equal(buf.length, 44 + n); assert.equal(buf.readUInt32LE(4), 36 + n);
  return { samples: n / 2, nonzero: buf.subarray(44).some((b) => b !== 0) };
}
function parseGlb(buf) {
  assert.equal(buf.readUInt32LE(0), 0x46546c67, "glTF magic"); assert.equal(buf.readUInt32LE(4), 2); assert.equal(buf.readUInt32LE(8), buf.length);
  const jl = buf.readUInt32LE(12); assert.equal(buf.readUInt32LE(16), 0x4e4f534a); assert.equal(jl % 4, 0);
  const json = JSON.parse(buf.toString("utf8", 20, 20 + jl));
  const bl = buf.readUInt32LE(20 + jl); assert.equal(buf.readUInt32LE(24 + jl), 0x004e4942); assert.equal(28 + jl + bl, buf.length);
  assert.equal(json.buffers[0].byteLength, bl);
  assert.equal(json.accessors[0].count, 24); assert.equal(json.accessors[2].count, 36);
  const bin = buf.subarray(28 + jl), idxOff = json.bufferViews[2].byteOffset;
  for (let i = 0; i < 36; i++) assert.ok(bin.readUInt16LE(idxOff + i * 2) < 24, "index in range");
  return json;
}
// multipart/form-data body of a recorded request -> {fields: {name: value}, files: [{name, filename, type, size}]}
function multipart(s) {
  const boundary = (String(s.h["content-type"] || "").match(/boundary=(.+)$/) || [])[1];
  assert.ok(boundary, `multipart content-type expected, got ${s.h["content-type"]}`);
  const fields = {}, files = [];
  for (const part of s.body.toString("latin1").split(`--${boundary}`).slice(1, -1)) {
    const [head, ...rest] = part.replace(/^\r\n/, "").split("\r\n\r\n"), data = rest.join("\r\n\r\n").replace(/\r\n$/, "");
    const name = (head.match(/name="([^"]+)"/) || [])[1], filename = (head.match(/filename="([^"]*)"/) || [])[1];
    if (filename !== undefined) files.push({ name, filename, type: (head.match(/content-type: ([^\r\n]+)/i) || [])[1], size: data.length });
    else fields[name] = data;
  }
  return { fields, files };
}

let failed = 0, total = 0;
async function section(name, fn) {
  total++;
  try { await fn(); console.log(`ok   ${name}`); } catch (e) { failed++; console.log(`FAIL ${name}\n${e.stack}`); }
}

// =====================================================================================================================
// Part 1: mock mode (no keys, no network)
// =====================================================================================================================
const root = mkProject({ revenue: { lifetime_gross_usd: 600000, developer_annual_games_revenue_usd: 0 } });
const plugin = fs.mkdtempSync(path.join(os.tmpdir(), "gs-plugin-"));
tmpDirs.push(plugin);
fs.mkdirSync(path.join(plugin, "skills", "economy-design"), { recursive: true });
fs.mkdirSync(path.join(plugin, "skills", "mobile-ux"), { recursive: true });
fs.writeFileSync(path.join(plugin, "skills", "economy-design", "SKILL.md"), "# Economy design\n\n## Soft currency sinks\n\nSoft currency hoarding is fixed with sinks: upgrades, gacha, and timed boosts keep the faucet-sink ratio near one.\n\n## Pacing\n\nUnrelated pacing text.\n");
fs.writeFileSync(path.join(plugin, "skills", "mobile-ux", "SKILL.md"), "# Mobile UX\n\n## Thumb zone\n\nPlace primary buttons in the bottom third of the screen for one-handed play.\n");

const c = new Client({ GS_MOCK: "1", CLAUDE_PROJECT_DIR: root, GS_PLUGIN_ROOT: plugin });
const made = {};

await section("protocol: initialize, ping, unknown method, notifications", async () => {
  let r = await c.request("initialize", { protocolVersion: "2025-11-25", capabilities: {}, clientInfo: { name: "t", version: "1" } });
  assert.equal(r.result.protocolVersion, "2025-11-25"); assert.deepEqual(r.result.capabilities, { tools: {} }); assert.equal(r.result.serverInfo.name, "studio-gateway");
  r = await c.request("initialize", { protocolVersion: "1999-01-01" });
  assert.equal(r.result.protocolVersion, "2025-06-18");
  const before = c.lines.length;
  c.send({ jsonrpc: "2.0", method: "notifications/initialized" });
  assert.deepEqual((await c.request("ping")).result, {});
  assert.equal(c.lines.length, before + 1, "no reply to notification");
  assert.equal((await c.request("nope/nothing")).error.code, -32601);
  assert.equal((await c.request("tools/call", { name: "nope", arguments: {} })).error.code, -32602);
  c.proc.stdin.write("not json\n");
  await new Promise((res) => setTimeout(res, 150));
  assert.equal(c.lines.at(-1).error.code, -32700);
});

await section("tools/list exposes all tools with schemas", async () => {
  const { tools } = (await c.request("tools/list")).result;
  assert.deepEqual(tools.map((t) => t.name).sort(), [...TOOLS].sort());
  for (const t of tools) { assert.equal(t.inputSchema.type, "object"); assert.ok(t.description.length > 30, t.name); }
  const by = (n) => tools.find((t) => t.name === n).inputSchema;
  assert.deepEqual(by("image_generate").required, ["prompt", "kind"]);
  assert.ok(by("image_generate").properties.quality && by("image_edit").properties.quality, "openai quality tier");
  assert.ok(by("model3d_status").properties.wait_sec, "status can wait and chain");
  assert.ok(by("audio_music").properties.provider.enum.includes("stability") && by("audio_sfx").properties.provider.enum.includes("stability"));
});

await section("argument validation", async () => {
  const r = await c.call("image_generate", { prompt: "x" });
  assert.ok(r.isError && /kind/.test(r.error));
  assert.ok((await c.call("image_generate", { prompt: "x", kind: "sprite", n: 9 })).isError);
  assert.ok((await c.call("image_generate", { prompt: "x", kind: "sprite", quality: "ultra" })).isError);
});

await section("gs_status", async () => {
  const r = await c.call("gs_status");
  assert.equal(fs.realpathSync(r.project_root), fs.realpathSync(root)); assert.equal(r.mock_forced, true); assert.equal(r.gamestudio_found, true);
  assert.equal(r.providers.gemini, false); assert.ok(r.kb_root);
  assert.ok(r.pricing.total >= 20 && r.pricing.verified > 0 && Array.isArray(r.pricing.unverified) && r.pricing.unverified.includes("openai.image"), JSON.stringify(r.pricing));
  assert.deepEqual(r.running_3d_jobs, []);
});

await section("image_generate: valid PNG, manifest, ledger", async () => {
  const r = await c.call("image_generate", { prompt: "red slime sprite", kind: "sprite", size: "64x48", n: 2, id_prefix: "slime" });
  assert.ok(r.ok && r.placeholder && r.cost_usd === 0 && r.files.length === 2);
  assert.match(r.files[0].asset_id, /^slime-\d{3}$/);
  const png = parsePng(file(root, r.files[0].path));
  assert.deepEqual([png.w, png.h, png.color], [64, 48, 2]);
  assert.equal(r.files[0].sha256, crypto.createHash("sha256").update(file(root, r.files[0].path)).digest("hex"));
  made.png = r.files[0];
  const t = await c.call("image_generate", { prompt: "gem icon", kind: "icon", size: "4000x16", transparent: true });
  const tp = parsePng(file(root, t.files[0].path));
  assert.deepEqual([tp.w, tp.h, tp.color], [2048, 16, 6], "clamped to 2048, RGBA");
  const man = readJson(root, "assets/manifest.json"), a = man.assets.find((x) => x.id === r.files[0].asset_id);
  assert.equal(man.schema_version, "1.0"); assert.equal(a.status, "candidate"); assert.equal(a.placeholder, true); assert.equal(a.kind, "sprite");
  assert.equal(a.sha256, r.files[0].sha256); assert.equal(a.licence.commercial_ok, true); assert.match(a.created_at, /^\d{4}-\d\d-\d\dT/);
  const b = readJson(root, "budget.json");
  assert.equal(b.cap_usd, 5); assert.equal(b.spent_usd, 0); assert.ok(b.ledger.length >= 2); assert.equal(b.ledger[0].tool, "image_generate");
});

await section("image_edit and image_postprocess derive from source", async () => {
  const e = await c.call("image_edit", { source: made.png.path, prompt: "add a crown" });
  assert.ok(e.ok); parsePng(file(root, e.files[0].path));
  const nb = await c.call("image_postprocess", { path: made.png.path, op: "remove_background" });
  assert.equal(parsePng(file(root, nb.files[0].path)).color, 6);
  const up = await c.call("image_postprocess", { path: made.png.path, op: "upscale" });
  assert.equal(parsePng(file(root, up.files[0].path)).w, 128);
  const v = await c.call("image_postprocess", { path: made.png.path, op: "vectorize" });
  assert.match(file(root, v.files[0].path).toString(), /<svg/);
  const a = readJson(root, "assets/manifest.json").assets.find((x) => x.id === nb.files[0].asset_id);
  assert.deepEqual(a.derived_from, [made.png.asset_id]);
  assert.ok((await c.call("image_edit", { source: "missing.png", prompt: "x" })).isError);
});

await section("model3d: valid GLB, mock status", async () => {
  const r = await c.call("model3d_generate", { prompt: "treasure chest", provider: "tripo", face_limit: 500, texture: true, rig: true });
  assert.ok(r.placeholder && r.cost_usd === 0);
  near(r.estimated_usd_if_real, 0.30 + 0.10 + 0.25, "estimate covers model, texture and rig");
  const json = parseGlb(file(root, r.files[0].path));
  assert.equal(json.meshes.length, 1);
  assert.ok(file(root, r.files[0].path).length < 2000);
  assert.equal(readJson(root, "assets/manifest.json").assets.find((x) => x.id === r.files[0].asset_id).kind, "model");
  parseGlb(file(root, (await c.call("model3d_status", { provider: "meshy", task_id: "mock-1" })).files[0].path));
  assert.ok((await c.call("model3d_generate", { provider: "tripo" })).isError, "needs prompt or image");
  assert.ok((await c.call("model3d_generate", { provider: "tripo", prompt: "x", face_limit: 50000 })).isError, "Tripo P1 face_limit is 48-20000");
  const m = await c.call("model3d_generate", { prompt: "barrel", provider: "meshy", texture: true });
  near(m.estimated_usd_if_real, 0.40 + 0.20, "meshy preview plus refine");
});

await section("audio: valid WAV for music, sfx and voice", async () => {
  const m = await c.call("audio_music", { prompt: "calm village loop", duration_sec: 3, provider: "elevenlabs" });
  const w = parseWav(file(root, m.files[0].path));
  assert.equal(w.samples, 132300); assert.ok(w.nonzero);
  const s = await c.call("audio_sfx", { prompt: "coin pickup", duration_sec: 0.5, loop: false });
  assert.equal(parseWav(file(root, s.files[0].path)).samples, 22050);
  const v = await c.call("audio_voice", { text: "Welcome back, hero.", provider: "gemini" });
  assert.equal(parseWav(file(root, v.files[0].path)).nonzero, false, "voice placeholder is silence");
  const d = await c.call("audio_voice", { lines: [{ text: "Hi", voice_id: "a" }, { text: "Hello there", voice_id: "b" }] });
  assert.ok(d.ok);
  const st = await c.call("audio_music", { prompt: "ambient drone", duration_sec: 3, provider: "stability" });
  assert.ok(st.placeholder && st.model === "stable-audio-3"); near(st.estimated_usd_if_real, 0.08);
  assert.ok((await c.call("audio_sfx", { prompt: "creak", duration_sec: 1, provider: "stability" })).placeholder);
  assert.ok((await c.call("audio_voice", {})).isError);
  const kinds = readJson(root, "assets/manifest.json").assets.map((x) => x.kind);
  for (const k of ["music", "sfx", "voice"]) assert.ok(kinds.includes(k), k);
});

await section("manifest_query and manifest_update", async () => {
  const q = await c.call("manifest_query", { kind: "sprite", text: "slime" });
  assert.equal(q.total, 5, "2 generated + 3 derived slime-* assets");
  assert.equal((await c.call("manifest_query", { kind: "music" })).assets[0].provider, "elevenlabs");
  const u = await c.call("manifest_update", { asset_id: made.png.asset_id, status: "approved", approved_by: "test", notes: "ok" });
  assert.equal(u.asset.status, "approved");
  assert.equal(readJson(root, "assets/manifest.json").assets.find((x) => x.id === made.png.asset_id).approved_by, "test");
  assert.ok((await c.call("manifest_update", { asset_id: "nope-001", status: "final" })).isError);
  assert.ok((await c.call("manifest_update", { asset_id: made.png.asset_id, status: "bogus" })).isError);
});

await section("licence_check flags non-commercial and placeholders", async () => {
  const before = await c.call("licence_check", {});
  assert.ok(before.passed && before.warnings > 0 && before.flags.every((f) => f.code !== "non_commercial"));
  await c.call("manifest_update", { asset_id: made.png.asset_id, licence: { commercial_ok: false, restrictions: ["CC BY-NC 4.0"], terms: "CC BY-NC 4.0" } });
  const r = await c.call("licence_check", { asset_id: made.png.asset_id });
  assert.equal(r.passed, false);
  assert.ok(r.flags.some((f) => f.code === "non_commercial" && f.severity === "error"));
  assert.ok((await c.call("licence_check", { asset_id: "zzz" })).isError);
});

await section("kb_search ranks relevant snippets with paths", async () => {
  const r = await c.call("kb_search", { query: "soft currency sinks hoarding" });
  assert.ok(r.count >= 1); assert.equal(r.results[0].file, "skills/economy-design/SKILL.md"); assert.match(r.results[0].snippet, /sinks/i);
  assert.equal((await c.call("kb_search", { query: "thumb one-handed", skill: "mobile-ux" })).results[0].skill, "mobile-ux");
  assert.equal((await c.call("kb_search", { query: "thumb", skill: "economy-design" })).count, 0);
});

await section("budget_status", async () => {
  const r = await c.call("budget_status");
  assert.equal(r.cap_usd, 5); assert.equal(r.spent_usd, 0); assert.ok(r.entries >= 8);
});
await c.close();

// ---- cap refusal: key present, no mock, no network needed because the call is refused first ----
await section("budget cap refuses a call that would exceed it; dry_run still works", async () => {
  const r2 = mkProject({ budgets: { asset_usd_cap: 0.01 } });
  const k = new Client({ CLAUDE_PROJECT_DIR: r2, GEMINI_API_KEY: SECRET });
  const refused = await k.call("image_generate", { prompt: "x", kind: "sprite", provider: "gemini" });
  assert.ok(refused.isError && refused.refused && refused.estimated_usd > refused.remaining_usd, JSON.stringify(refused));
  assert.ok(!fs.existsSync(path.join(r2, ".gamestudio/assets/manifest.json")) && !fs.existsSync(path.join(r2, ".gamestudio/budget.json")), "nothing written on refusal");
  const dry = await k.call("image_generate", { prompt: "x", kind: "sprite", provider: "gemini", dry_run: true, size: "8" });
  assert.ok(dry.ok && dry.placeholder && dry.cost_usd === 0 && dry.estimated_usd_if_real > 0.01);
  const noKey = await k.call("audio_sfx", { prompt: "boom" });
  assert.ok(noKey.placeholder, "missing key falls back to placeholder");
  await k.close();
  assert.ok(!k.err.includes(SECRET), "secret never logged");
});

// =====================================================================================================================
// Part 2: every real provider request path against one local fake HTTP server
// =====================================================================================================================
const K = { gemini: `${SECRET}-gem`, openai: `${SECRET}-oai`, recraft: `${SECRET}-rec`, fal: `${SECRET}-fal`, tripo: `${SECRET}-tri`, meshy: `${SECRET}-mes`, eleven: `${SECRET}-11l`, stability: `${SECRET}-sta` };
const MP3 = Buffer.from("ID3fake-mp3-bytes");
const PCM = Buffer.alloc(4800, 7); // raw 16-bit mono PCM, 0.1 s at 24 kHz
const b64 = (b) => Buffer.from(b).toString("base64");
const seed = (s) => crypto.createHash("sha1").update(s).digest().readUInt32BE(0) % 200;
const seen = []; // every request: {m, u, h, body}
const S = {
  openaiCalls: 0, interactions: 0, dl: 0, dlFail: 0,
  fal: { n: 0, polls: {}, images: {} }, stab: { n: 0, polls: {} },
  tripo: { n: { model: 0, rig_check: 0, rig: 0 }, tasks: {}, riggable: true, failRig: false, failModel: false, need: { model: 3, rig_check: 2, rig: 3 } },
  meshy: { n: { preview: 0, refine: 0, image: 0 }, tasks: {}, failRefine: false, need: 2 },
};
let base = "";
const json = (res, o, s = 200) => { res.writeHead(s, { "content-type": "application/json" }); res.end(JSON.stringify(o)); };
const bin = (res, buf, type) => { res.writeHead(200, { "content-type": type }); res.end(buf); };

function route(s, res) {
  const { m, u, h } = s, body = s.body.toString("utf8");
  // ---- downloads (no credentials may ever be sent here) ----
  if (m === "GET" && u.startsWith("/dl/")) {
    const ext = u.split(".").pop();
    if (ext === "png") return bin(res, u.includes("nobg") ? makePng(256, 256, { alpha: true }) : makePng(256, 256, { seed: seed(u) }), "image/png");
    if (ext === "svg") return bin(res, makeSvg(seed(u)), "image/svg+xml");
    if (ext === "glb") { if (S.dlFail > 0) { S.dlFail--; res.writeHead(500); return res.end("storage down"); } return bin(res, makeGlb(), "model/gltf-binary"); }
  }
  // ---- Gemini: Interactions API ----
  if (u === "/gemini/interactions" && m === "POST") {
    if (h["x-goog-api-key"] !== K.gemini) return json(res, { error: { code: 401, message: "API key not valid" } }, 401);
    const b = JSON.parse(body), k = ++S.interactions, kind = b.response_format?.type;
    if (kind === "image") {
      if (/NOIMAGE/.test(JSON.stringify(b.input))) return json(res, { id: `int_${k}`, status: "completed", steps: [{ type: "model_output", content: [{ type: "text", text: "I cannot draw that." }] }] });
      return json(res, { id: `int_${k}`, status: "completed", steps: [
        { type: "user_input", content: b.input },
        { type: "thought", summary: [{ type: "image", data: b64(makePng(8, 8, { seed: 199 })) }] }, // interim image: must be ignored
        { type: "model_output", content: [{ type: "text", text: "Here is the image." }, { type: "image", data: b64(makePng(16, 16, { seed: 100 + k })), mime_type: "image/png" }] }] });
    }
    if (kind === "audio" && /^lyria/.test(b.model)) return json(res, { id: `int_${k}`, status: "completed", steps: [{ type: "model_output", content: [{ type: "text", text: "[Verse] la la" }, { type: "audio", data: b64(MP3) }] }] });
    if (kind === "audio") {
      const raw = b.model === "gemini-3.1-flash-tts-preview";
      return json(res, { id: `int_${k}`, status: "completed", steps: [{ type: "model_output", content: [raw ? { type: "audio", mime_type: "audio/l16;rate=24000", data: b64(PCM) } : { type: "audio", mime_type: "audio/wav", data: b64(makeWav(0.2)) }] }] });
    }
  }
  // ---- OpenAI Images ----
  if (u === "/openai/images/generations" && m === "POST") {
    if (++S.openaiCalls === 1) { res.writeHead(429, { "retry-after": "0" }); return res.end("slow down"); }
    return json(res, { created: 1, data: Array.from({ length: JSON.parse(body).n || 1 }, (_, i) => ({ b64_json: b64(makePng(16, 16, { seed: 150 + S.openaiCalls + i })) })) });
  }
  if (u === "/openai/images/edits" && m === "POST") return json(res, { created: 1, data: Array.from({ length: Number(multipart(s).fields.n || 1) }, (_, i) => ({ b64_json: b64(makePng(16, 16, { seed: 170 + i })) })) });
  // ---- Recraft ----
  if (u === "/recraft/images/generations" && m === "POST") {
    const b = JSON.parse(body), vec = /vector/.test(b.model);
    return json(res, { created: 1, credits: 35, data: Array.from({ length: b.n || 1 }, (_, i) => ({ image_id: `img${i}`, url: `${base}/dl/rg-${++S.dl}.${vec ? "svg" : "png"}` })) });
  }
  if (m === "POST" && /^\/recraft\/images\/(removeBackground|vectorize|crispUpscale)$/.test(u)) {
    const op = u.split("/").pop();
    return json(res, { created: 1, credits: 10, image: { image_id: "x", url: `${base}/dl/${op === "removeBackground" ? "nobg" : op}-${++S.dl}.${op === "vectorize" ? "svg" : "png"}` } });
  }
  // ---- fal queue ----
  if (u === "/fal/fal-ai/flux/schnell" && m === "POST") {
    const id = `REQ${++S.fal.n}`; S.fal.polls[id] = 0; S.fal.images[id] = JSON.parse(body).num_images;
    return json(res, { status: "IN_QUEUE", request_id: id, status_url: `${base}/fal/fal-ai/flux/requests/${id}/status`, response_url: `${base}/fal/fal-ai/flux/requests/${id}`, cancel_url: `${base}/fal/fal-ai/flux/requests/${id}/cancel`, queue_position: 0 });
  }
  let mm = u.match(/^\/fal\/fal-ai\/flux\/requests\/(REQ\d+)\/status$/);
  if (mm && m === "GET") { const k = ++S.fal.polls[mm[1]]; return json(res, { status: k === 1 ? "IN_QUEUE" : k === 2 ? "IN_PROGRESS" : "COMPLETED" }); }
  mm = u.match(/^\/fal\/fal-ai\/flux\/requests\/(REQ\d+)$/);
  if (mm && m === "GET") return json(res, { images: Array.from({ length: S.fal.images[mm[1]] }, (_, i) => ({ url: `${base}/dl/fal-${mm[1]}-${i}.png`, width: 512, height: 256, content_type: "image/png" })), seed: 5, has_nsfw_concepts: [false], timings: {}, prompt: "x" });
  // ---- Stability ----
  if (u === "/stability/stable-image/generate/core" && m === "POST") return bin(res, makePng(16, 16, { seed: 140 }), "image/png");
  if (u === "/stability/audio/stable-audio/text-to-audio" && m === "POST") {
    const id = `${"A".repeat(63)}${++S.stab.n}`; S.stab.polls[id] = 0;
    res.writeHead(202, { "content-type": "application/json" }); return res.end(JSON.stringify({ id }));
  }
  mm = u.match(/^\/stability\/audio\/results\/(\w+)$/);
  if (mm && m === "GET") {
    if (++S.stab.polls[mm[1]] < 3) { res.writeHead(202, { "content-type": "application/json" }); return res.end(JSON.stringify({ id: mm[1], status: "in-progress" })); }
    return bin(res, MP3, "audio/mpeg");
  }
  // ---- ElevenLabs ----
  if (m === "POST" && /^\/eleven\/(music|sound-generation|text-to-speech\/[\w-]+|text-to-dialogue)\?/.test(u)) return bin(res, MP3, "audio/mpeg");
  if (u === "/eleven/text-to-voice/design" && m === "POST") return json(res, { previews: [{ generated_voice_id: "gen_prev_1", audio_base_64: "", media_type: "audio/mpeg", duration_secs: 3 }], text: "sample text" });
  if (u === "/eleven/text-to-voice" && m === "POST") return json(res, { voice_id: "voice_designed_1", name: "x" });
  // ---- Tripo v3 ----
  if (u.startsWith("/tripo/") && h.authorization !== `Bearer ${K.tripo}`) return json(res, { code: 2, status: "error", message: "unauthorized" }, 401);
  if (u === "/tripo/files" && m === "POST") return json(res, { code: 0, status: "success", data: { file_token: "file_tok_1" } });
  if (m === "POST" && ["/tripo/generation/text-to-model", "/tripo/generation/image-to-model", "/tripo/animations/rig-check", "/tripo/animations/rig"].includes(u)) {
    const kind = u.endsWith("rig-check") ? "rig_check" : u.endsWith("/rig") ? "rig" : "model", id = `${{ model: "TM", rig_check: "TC", rig: "TR" }[kind]}${++S.tripo.n[kind]}`;
    S.tripo.tasks[id] = { kind, polls: 0 };
    return json(res, { code: 0, status: "success", data: { task_id: id, type: kind, status: "queued" } });
  }
  mm = u.match(/^\/tripo\/tasks\/(\w+)$/);
  if (mm && m === "GET") {
    const t = S.tripo.tasks[mm[1]];
    if (!t) return json(res, { code: 2001, status: "error", message: "task not found" }, 404);
    t.polls++;
    if (t.polls < S.tripo.need[t.kind]) return json(res, { code: 0, status: "success", data: { task_id: mm[1], status: t.polls === 1 ? "queued" : "running", progress: t.polls * 30 } });
    if ((t.kind === "rig" && S.tripo.failRig) || (t.kind === "model" && S.tripo.failModel)) return json(res, { code: 0, status: "success", data: { task_id: mm[1], status: "failed", error_code: 2008, error_message: "moderation" } });
    const output = t.kind === "rig_check" ? { riggable: S.tripo.riggable, rig_type: "biped" } : { model_url: `${base}/dl/${mm[1]}.glb`, rendered_image_url: `${base}/dl/${mm[1]}.png` };
    return json(res, { code: 0, status: "success", data: { task_id: mm[1], status: "success", progress: 100, output, credits_consumed: 30 } });
  }
  // ---- Meshy ----
  if (u.startsWith("/meshy/") && h.authorization !== `Bearer ${K.meshy}`) return json(res, { message: "Unauthorized" }, 401);
  if (m === "POST" && (u === "/meshy/v2/text-to-3d" || u === "/meshy/v1/image-to-3d")) {
    const b = JSON.parse(body), kind = u.includes("image") ? "image" : b.mode === "refine" ? "refine" : "preview", id = `${{ image: "MI", refine: "MR", preview: "MP" }[kind]}${++S.meshy.n[kind]}`;
    S.meshy.tasks[id] = { kind, polls: 0 };
    return json(res, { result: id });
  }
  mm = u.match(/^\/meshy\/(?:v2\/text-to-3d|v1\/image-to-3d)\/(\w+)$/);
  if (mm && m === "GET") {
    const t = S.meshy.tasks[mm[1]];
    if (!t) return json(res, { message: "Not found" }, 404);
    t.polls++;
    if (t.polls < S.meshy.need) return json(res, { id: mm[1], status: t.polls === 1 ? "PENDING" : "IN_PROGRESS", progress: t.polls * 20 });
    if (t.kind === "refine" && S.meshy.failRefine) return json(res, { id: mm[1], status: "FAILED", progress: 100, task_error: { message: "texture generation failed" } });
    return json(res, { id: mm[1], status: "SUCCEEDED", progress: 100, model_urls: { glb: `${base}/dl/${mm[1]}.glb`, fbx: `${base}/dl/${mm[1]}.fbx` }, consumed_credits: 20 });
  }
  json(res, { error: "no route", method: m, url: u }, 404);
}
const fake = http.createServer((req, res) => {
  const chunks = [];
  req.on("data", (d) => chunks.push(d));
  req.on("end", () => {
    const s = { m: req.method, u: req.url, h: req.headers, body: Buffer.concat(chunks) };
    seen.push(s);
    try { route(s, res); } catch (e) { res.writeHead(500); res.end(String(e.stack)); }
  });
});
await new Promise((r) => fake.listen(0, "127.0.0.1", r));
base = `http://127.0.0.1:${fake.address().port}`;

const BASES = { GS_GEMINI_BASE_URL: `${base}/gemini`, GS_OPENAI_BASE_URL: `${base}/openai`, GS_RECRAFT_BASE_URL: `${base}/recraft`, GS_FAL_BASE_URL: `${base}/fal`, GS_TRIPO_BASE_URL: `${base}/tripo`, GS_MESHY_BASE_URL: `${base}/meshy`, GS_ELEVENLABS_BASE_URL: `${base}/eleven`, GS_STABILITY_BASE_URL: `${base}/stability`, GS_RETRY_BASE_MS: "5", GS_POLL_MS: "20" };
const rp = mkProject({ budgets: { asset_usd_cap: 100 }, revenue: { lifetime_gross_usd: 600000, developer_annual_games_revenue_usd: 0 } });
const real = new Client({ CLAUDE_PROJECT_DIR: rp, GEMINI_API_KEY: K.gemini, OPENAI_API_KEY: K.openai, RECRAFT_API_KEY: K.recraft, FAL_KEY: K.fal, TRIPO_API_KEY: K.tripo, MESHY_API_KEY: K.meshy, ELEVENLABS_API_KEY: K.eleven, STABILITY_API_KEY: K.stability, ...BASES });

const jbody = (s) => JSON.parse(s.body.toString("utf8"));
const orEmpty = (r, rel, dflt) => { try { return readJson(r, rel); } catch { return dflt; } }; // files appear with the first write
const ledgerOf = (r = rp) => orEmpty(r, "budget.json", { ledger: [] }).ledger;
const manifestOf = (r = rp) => orEmpty(r, "assets/manifest.json", { assets: [] }).assets;
const since = (mark, prefix) => seen.slice(mark).filter((s) => s.u.startsWith(prefix));
// One real call through the server, checking what every provider path must leave behind: a file per output, a manifest entry
// with provenance (provider, model, hash, licence, cost) and exactly one ledger entry with the same cost and asset ids.
async function realCall(tool, args, exp) {
  const nLedger = ledgerOf().length;
  const r = await real.call(tool, args);
  assert.ok(r.ok && !r.placeholder && !r.isError, JSON.stringify(r));
  assert.equal(r.provider, exp.provider, "provider");
  if (exp.model) assert.equal(r.model, exp.model, "model");
  assert.equal(r.files.length, exp.files ?? 1, "file count");
  near(r.cost_usd, exp.cost, `${tool} cost_usd`, 1e-6);
  for (const f of r.files) {
    assert.ok(f.path.endsWith(`.${exp.ext}`), `${f.path} should end with .${exp.ext}`);
    const bytes = file(rp, f.path);
    assert.ok(bytes.length > 0 && sha(bytes) === f.sha256 && f.bytes === bytes.length, "file content and hash");
    const a = manifestOf().find((x) => x.id === f.asset_id);
    assert.ok(a && a.provider === exp.provider && a.placeholder === false && a.status === "candidate" && a.sha256 === f.sha256 && a.licence?.terms && a.prompt !== undefined, `manifest entry for ${f.asset_id}`);
    if (exp.model) assert.equal(a.model, exp.model);
    near(a.cost_usd * r.files.length, exp.cost, "manifest cost_usd", 1e-5);
  }
  const led = ledgerOf(); assert.equal(led.length, nLedger + 1, "one ledger entry per call");
  const e = led.at(-1);
  assert.equal(e.provider, exp.provider); assert.equal(e.tool, tool); near(e.cost_usd, exp.cost, "ledger cost_usd", 1e-6); assert.deepEqual(e.asset_ids, r.files.map((f) => f.asset_id));
  return r;
}

await section("real path: gemini image generate (Interactions API); interim thought images are ignored", async () => {
  const mark = seen.length;
  const r = await realCall("image_generate", { prompt: "castle", kind: "background", provider: "gemini", size: "1536x1024", id_prefix: "castle" }, { provider: "gemini", model: "gemini-nano-banana-2.1", ext: "png", cost: 0.0504 });
  const q = since(mark, "/gemini/");
  assert.equal(q.length, 1);
  assert.equal(q[0].m, "POST"); assert.equal(q[0].u, "/gemini/interactions");
  assert.equal(q[0].h["x-goog-api-key"], K.gemini); assert.equal(q[0].h.authorization, undefined); assert.match(q[0].h["content-type"], /^application\/json/);
  const b = jbody(q[0]);
  assert.deepEqual(b, { model: "gemini-nano-banana-2.1", input: [{ type: "text", text: "castle" }], response_format: { type: "image", aspect_ratio: "3:2", image_size: "2K" } });
  assert.deepEqual(file(rp, r.files[0].path), makePng(16, 16, { seed: 100 + S.interactions }), "the model_output image is saved, not the interim thought image");
  assert.match(r.files[0].asset_id, /^castle-\d{3}$/);
  made.gemini = r.files[0];
});
await section("real path: gemini n=2 sends two requests and notes that seed has no effect", async () => {
  const mark = seen.length, before = S.interactions;
  const r = await realCall("image_generate", { prompt: "gem", kind: "icon", provider: "gemini", size: "1024", n: 2, seed: 7 }, { provider: "gemini", ext: "png", files: 2, cost: 0.0672 });
  const q = since(mark, "/gemini/"); assert.equal(q.length, 2);
  for (const s of q) assert.deepEqual(jbody(s).response_format, { type: "image", aspect_ratio: "1:1", image_size: "1K" });
  assert.ok(!("seed" in jbody(q[0])) && !("generation_config" in jbody(q[0])));
  assert.deepEqual(r.files.map((f) => file(rp, f.path).toString("hex")).sort(), [before + 1, before + 2].map((k) => makePng(16, 16, { seed: 100 + k }).toString("hex")).sort());
  assert.ok(r.notes.some((n) => /no seed parameter/.test(n)), JSON.stringify(r.notes));
});
await section("real path: gemini answers without an image: a clear error and nothing is written", async () => {
  const nMan = manifestOf().length, nLed = ledgerOf().length;
  const r = await real.call("image_generate", { prompt: "NOIMAGE please", kind: "icon", provider: "gemini" });
  assert.ok(r.isError && /gemini returned no image/.test(r.error) && /I cannot draw that/.test(r.error), JSON.stringify(r));
  assert.equal(manifestOf().length, nMan); assert.equal(ledgerOf().length, nLed);
});
await section("real path: gemini image edit sends the source and references as image blocks", async () => {
  fs.mkdirSync(path.join(rp, "refs"), { recursive: true });
  const ref = makePng(24, 24, { seed: 5 }); fs.writeFileSync(path.join(rp, "refs/ref.png"), ref);
  let mark = seen.length;
  const r = await realCall("image_edit", { source: made.gemini.path, prompt: "add a crown", provider: "gemini", references: ["refs/ref.png"] }, { provider: "gemini", ext: "png", cost: 0.0336 });
  const b = jbody(since(mark, "/gemini/")[0]);
  assert.equal(b.model, "gemini-nano-banana-2.1"); assert.equal(b.input.length, 3);
  assert.deepEqual(b.input[0], { type: "text", text: "add a crown" });
  assert.deepEqual(b.input[1], { type: "image", mime_type: "image/png", data: file(rp, made.gemini.path).toString("base64") });
  assert.deepEqual(b.input[2], { type: "image", mime_type: "image/png", data: ref.toString("base64") });
  assert.deepEqual(b.response_format, { type: "image", aspect_ratio: "1:1", image_size: "1K" });
  const a = manifestOf().find((x) => x.id === r.files[0].asset_id);
  assert.deepEqual(a.derived_from, [made.gemini.asset_id]); assert.deepEqual(a.references, [made.gemini.path, "refs/ref.png"]);
  // a JPEG source has no readable size: the aspect ratio is left to the model
  fs.writeFileSync(path.join(rp, "refs/photo.jpg"), Buffer.concat([Buffer.from([0xff, 0xd8, 0xff, 0xe0]), Buffer.alloc(32)]));
  mark = seen.length;
  await realCall("image_edit", { source: "refs/photo.jpg", prompt: "cartoon style", provider: "gemini" }, { provider: "gemini", ext: "png", cost: 0.0336 });
  const b2 = jbody(since(mark, "/gemini/")[0]);
  assert.deepEqual(b2.response_format, { type: "image", image_size: "1K" }); assert.equal(b2.input[1].mime_type, "image/jpeg");
  // unsupported reference types are refused before any request
  fs.writeFileSync(path.join(rp, "refs/notes.txt"), "hello");
  mark = seen.length;
  const bad = await real.call("image_edit", { source: made.gemini.path, prompt: "x", provider: "gemini", references: ["refs/notes.txt"] });
  assert.ok(bad.isError && /png, jpeg or webp/.test(bad.error)); assert.equal(seen.length, mark);
});
await section("real path: lyria music (duration and instrumental go in the prompt; MP3 block saved)", async () => {
  let mark = seen.length;
  const r = await realCall("audio_music", { prompt: "calm village loop", duration_sec: 45, provider: "lyria" }, { provider: "lyria", model: "lyria-3.5", ext: "mp3", cost: 0.08 });
  const q = since(mark, "/gemini/")[0], b = jbody(q);
  assert.equal(q.h["x-goog-api-key"], K.gemini);
  assert.deepEqual(Object.keys(b).sort(), ["input", "model", "response_format"]);
  assert.equal(b.model, "lyria-3.5"); assert.deepEqual(b.response_format, { type: "audio" });
  assert.equal(b.input, "calm village loop. Instrumental only, no vocals. Approximately 45 seconds.");
  assert.deepEqual(file(rp, r.files[0].path), MP3);
  const a = manifestOf().find((x) => x.id === r.files[0].asset_id); assert.match(a.licence.terms, /Gemini/);
  const clip = await realCall("audio_music", { prompt: "short sting", duration_sec: 10, provider: "lyria", model: "lyria-3-clip-preview" }, { provider: "lyria", model: "lyria-3-clip-preview", ext: "mp3", cost: 0.04 });
  assert.ok(clip.notes.some((n) => /always make 30 s/.test(n)), JSON.stringify(clip.notes));
});
await section("real path: gemini TTS single speaker, two speakers, and raw PCM wrapped as WAV", async () => {
  let mark = seen.length;
  const r = await realCall("audio_voice", { text: "Welcome back, hero.", provider: "gemini", voice_id: "Puck" }, { provider: "gemini", model: "gemini-3.8-flash-tts", ext: "wav", cost: estimate("gemini", "tts", { chars: 19 }) });
  let q = since(mark, "/gemini/")[0];
  assert.equal(q.h["x-goog-api-key"], K.gemini);
  assert.deepEqual(jbody(q), { model: "gemini-3.8-flash-tts", input: [{ type: "user_input", content: [{ type: "text", text: "Welcome back, hero." }] }], response_format: { type: "audio" }, generation_config: { speech_config: [{ voice: "Puck" }] } });
  assert.equal(file(rp, r.files[0].path).toString("ascii", 0, 4), "RIFF");
  mark = seen.length;
  await realCall("audio_voice", { lines: [{ text: "Hi", voice_id: "Kore" }, { text: "Hello there", voice_id: "Puck" }], provider: "gemini" }, { provider: "gemini", ext: "wav", cost: estimate("gemini", "tts", { chars: 14 }) });
  const b = jbody(since(mark, "/gemini/")[0]);
  assert.deepEqual(b.generation_config.speech_config, { speakers: [{ speaker: "Speaker1", voice: "Kore" }, { speaker: "Speaker2", voice: "Puck" }], mode: "conversational" });
  assert.deepEqual(b.input[0].content.map((x) => [x.text, x.annotations[0].type, x.annotations[0].speaker]), [["Hi", "speech_metadata", "Speaker1"], ["Hello there", "speech_metadata", "Speaker2"]]);
  const raw = await realCall("audio_voice", { text: "Raw please", provider: "gemini", model: "gemini-3.1-flash-tts-preview" }, { provider: "gemini", model: "gemini-3.1-flash-tts-preview", ext: "wav", cost: estimate("gemini", "tts", { chars: 10 }) });
  const wav = file(rp, raw.files[0].path);
  assert.equal(wav.readUInt32LE(24), 24000, "rate from the audio/l16 mime type"); assert.equal(wav.readUInt32LE(40), PCM.length); assert.ok(raw.notes.some((n) => /no price for model/.test(n)));
  mark = seen.length;
  const bad = await real.call("audio_voice", { lines: [{ text: "a", voice_id: "Kore" }, { text: "b", voice_id: "Puck" }, { text: "c", voice_id: "Zephyr" }], provider: "gemini" });
  assert.ok(bad.isError && /at most 2 speakers/.test(bad.error)); assert.equal(seen.length, mark, "refused before any request");
});

await section("real path: openai image retries on 429, sends the documented fields, records cost", async () => {
  const mark = seen.length;
  const r = await realCall("image_generate", { prompt: "castle", kind: "background", provider: "openai", size: "16" }, { provider: "openai", model: "gpt-image-2.5-flare", ext: "png", cost: 0.053 });
  assert.equal(S.openaiCalls, 2, "retried once after 429");
  const q = since(mark, "/openai/"); assert.equal(q.length, 2);
  assert.equal(q[1].m, "POST"); assert.equal(q[1].h.authorization, `Bearer ${K.openai}`); assert.match(q[1].h["content-type"], /^application\/json/);
  assert.deepEqual(jbody(q[1]), { model: "gpt-image-2.5-flare", prompt: "castle", n: 1, size: "1024x1024", quality: "medium", output_format: "png" });
  parsePng(file(rp, r.files[0].path));
  assert.equal(manifestOf().find((x) => x.id === r.files[0].asset_id).params.quality, "medium");
});
await section("real path: openai transparent high-quality wide images (background, size, quality, n)", async () => {
  const mark = seen.length;
  await realCall("image_generate", { prompt: "gem", kind: "icon", provider: "openai", size: "1536x1024", transparent: true, quality: "high", n: 2 }, { provider: "openai", ext: "png", files: 2, cost: 2 * 0.211 * 1.5 });
  assert.deepEqual(jbody(since(mark, "/openai/")[0]), { model: "gpt-image-2.5-flare", prompt: "gem", n: 2, size: "1536x1024", quality: "high", output_format: "png", background: "transparent" });
});
await section("real path: openai image edit posts multipart image[] files (also for image_generate with references)", async () => {
  let mark = seen.length;
  await realCall("image_edit", { source: made.gemini.path, prompt: "add a crown", provider: "openai", references: ["refs/ref.png"] }, { provider: "openai", model: "gpt-image-2.5-sunburst", ext: "png", cost: 0.053 + 2 * 0.01 });
  let q = since(mark, "/openai/")[0];
  assert.equal(q.m, "POST"); assert.equal(q.u, "/openai/images/edits"); assert.equal(q.h.authorization, `Bearer ${K.openai}`);
  const mp = multipart(q);
  assert.deepEqual(mp.fields, { model: "gpt-image-2.5-sunburst", prompt: "add a crown", n: "1", size: "1024x1024", quality: "medium", output_format: "png" });
  assert.deepEqual(mp.files.map((f) => [f.name, f.type, f.size]), [["image[]", "image/png", file(rp, made.gemini.path).length], ["image[]", "image/png", file(rp, "refs/ref.png").length]]);
  mark = seen.length;
  await realCall("image_generate", { prompt: "same style", kind: "sprite", provider: "openai", references: ["refs/ref.png"], quality: "low" }, { provider: "openai", model: "gpt-image-2.5-sunburst", ext: "png", cost: 0.006 + 0.01 });
  q = since(mark, "/openai/")[0]; assert.equal(q.u, "/openai/images/edits"); assert.equal(multipart(q).fields.quality, "low");
});

await section("real path: recraft raster and vector generation (model id picks vector; PNG requested; raster sizes exact, vector ratios)", async () => {
  let mark = seen.length;
  const g = await realCall("image_generate", { prompt: "gem icon", kind: "icon", provider: "recraft", size: "512", n: 2, seed: 42, id_prefix: "gem" }, { provider: "recraft", model: "recraftv4_1", ext: "png", files: 2, cost: 0.07 });
  let q = since(mark, "/recraft/").filter((s) => s.m === "POST"); assert.equal(q.length, 1);
  assert.equal(q[0].u, "/recraft/images/generations"); assert.equal(q[0].h.authorization, `Bearer ${K.recraft}`);
  assert.deepEqual(jbody(q[0]), { prompt: "gem icon", model: "recraftv4_1", n: 2, size: "1024x1024", response_format: "url", image_format: "png", random_seed: 42 });
  assert.equal(since(mark, "/dl/").length, 2, "both result urls downloaded");
  made.recraft = g.files[0];
  mark = seen.length;
  await realCall("image_generate", { prompt: "banner", kind: "background", provider: "recraft", size: "1200x800" }, { provider: "recraft", model: "recraftv4_1", ext: "png", cost: 0.035 });
  assert.equal(jbody(since(mark, "/recraft/")[0]).size, "1280x832", "nearest documented raster size (1.5:1)");
  mark = seen.length;
  await realCall("image_generate", { prompt: "banner", kind: "background", provider: "recraft", model: "recraftv4_1_pro", size: "1536x1024" }, { provider: "recraft", model: "recraftv4_1_pro", ext: "png", cost: 0.21 });
  assert.equal(jbody(since(mark, "/recraft/")[0]).size, "2560x1664", "pro models use the 2K size list");
  mark = seen.length;
  const v = await realCall("image_generate", { prompt: "gem icon", kind: "icon", provider: "recraft", model: "recraftv4_1_vector", size: "1024x768" }, { provider: "recraft", model: "recraftv4_1_vector", ext: "svg", cost: 0.08 });
  q = since(mark, "/recraft/");
  assert.deepEqual(jbody(q[0]), { prompt: "gem icon", model: "recraftv4_1_vector", n: 1, size: "4:3", response_format: "url" }, "no style, no image_format for vector");
  assert.match(file(rp, v.files[0].path).toString(), /<svg/);
});
await section("real path: recraft remove background, vectorize and crisp upscale (multipart file, image.url)", async () => {
  const src = made.recraft;
  for (const [op, api, ext, usd] of [["remove_background", "removeBackground", "png", 0.01], ["vectorize", "vectorize", "svg", 0.01], ["upscale", "crispUpscale", "png", 0.004]]) {
    const mark = seen.length;
    const r = await realCall("image_postprocess", { path: src.path, op }, { provider: "recraft", model: api, ext, cost: usd });
    const q = since(mark, "/recraft/")[0];
    assert.equal(q.m, "POST"); assert.equal(q.u, `/recraft/images/${api}`); assert.equal(q.h.authorization, `Bearer ${K.recraft}`);
    const mp = multipart(q);
    assert.deepEqual(mp.files.map((f) => [f.name, f.type, f.size]), [["file", "image/png", file(rp, src.path).length]]);
    assert.deepEqual(mp.fields, op === "vectorize" ? {} : { image_format: "png" });
    assert.deepEqual(manifestOf().find((x) => x.id === r.files[0].asset_id).derived_from, [src.asset_id]);
    if (op === "remove_background") assert.equal(parsePng(file(rp, r.files[0].path)).color, 6);
    if (op === "vectorize") assert.match(file(rp, r.files[0].path).toString(), /<svg/);
  }
  const mark = seen.length;
  const bad = await real.call("image_postprocess", { path: made.gemini.path, op: "remove_background" });
  assert.ok(bad.isError && /shortest side >= 256/.test(bad.error), JSON.stringify(bad)); assert.equal(seen.length, mark, "too-small input refused before any request");
});

await section("real path: fal queue submit, poll status_url, fetch response_url, download images", async () => {
  const mark = seen.length;
  const r = await realCall("image_generate", { prompt: "slime", kind: "sprite", provider: "fal", size: "512x256", n: 2, seed: 5 }, { provider: "fal", model: "fal-ai/flux/schnell", ext: "png", files: 2, cost: 0.006 });
  const q = since(mark, "/fal/");
  assert.equal(q[0].m, "POST"); assert.equal(q[0].u, "/fal/fal-ai/flux/schnell"); assert.equal(q[0].h.authorization, `Key ${K.fal}`);
  assert.deepEqual(jbody(q[0]), { prompt: "slime", num_images: 2, image_size: { width: 512, height: 256 }, output_format: "png", seed: 5 });
  const statuses = q.filter((s) => /\/status$/.test(s.u));
  assert.equal(statuses.length, 3, "IN_QUEUE, IN_PROGRESS, COMPLETED"); assert.ok(statuses.every((s) => s.m === "GET" && s.h.authorization === `Key ${K.fal}` && /^\/fal\/fal-ai\/flux\/requests\/REQ\d+\/status$/.test(s.u)));
  const result = q.filter((s) => /\/requests\/REQ\d+$/.test(s.u)); assert.equal(result.length, 1); assert.equal(result[0].h.authorization, `Key ${K.fal}`);
  assert.ok(q.indexOf(statuses.at(-1)) < q.indexOf(result[0]), "result is fetched after COMPLETED");
  assert.equal(since(mark, "/dl/").length, 2); parsePng(file(rp, r.files[0].path));
});

await section("real path: stability image core and Stable Audio 3 (202 {id}, then poll results until 200)", async () => {
  let mark = seen.length;
  await realCall("image_generate", { prompt: "mossy stone", kind: "texture", provider: "stability", size: "1024x1536", seed: 3 }, { provider: "stability", model: "stable-image-core", ext: "png", cost: 0.03 });
  let q = since(mark, "/stability/")[0];
  assert.equal(q.m, "POST"); assert.equal(q.u, "/stability/stable-image/generate/core"); assert.equal(q.h.authorization, `Bearer ${K.stability}`); assert.equal(q.h.accept, "image/*");
  assert.deepEqual(multipart(q).fields, { prompt: "mossy stone", aspect_ratio: "2:3", output_format: "png", seed: "3" });
  mark = seen.length;
  const m = await realCall("audio_music", { prompt: "ambient drone", duration_sec: 20, provider: "stability" }, { provider: "stability", model: "stable-audio-3", ext: "mp3", cost: 0.08 });
  const rq = since(mark, "/stability/audio/");
  assert.equal(rq[0].m, "POST"); assert.equal(rq[0].u, "/stability/audio/stable-audio/text-to-audio"); assert.equal(rq[0].h.authorization, `Bearer ${K.stability}`); assert.equal(rq[0].h.accept, "audio/*");
  assert.deepEqual(multipart(rq[0]).fields, { prompt: "ambient drone", model: "stable-audio-3", output_format: "mp3", duration: "20" });
  const polls = rq.slice(1); assert.equal(polls.length, 3, "202, 202, 200");
  assert.ok(polls.every((s) => s.m === "GET" && /^\/stability\/audio\/results\/A{63}\d$/.test(s.u) && s.h.accept === "audio/*" && s.h.authorization === `Bearer ${K.stability}`));
  assert.deepEqual(file(rp, m.files[0].path), MP3);
  mark = seen.length;
  const s = await realCall("audio_sfx", { prompt: "door creak", duration_sec: 0.5, loop: true, provider: "stability" }, { provider: "stability", model: "stable-audio-3", ext: "mp3", cost: 0.08 });
  assert.equal(multipart(since(mark, "/stability/audio/")[0]).fields.duration, "1", "below the 1 s minimum");
  assert.ok(s.notes.some((n) => /loop is not supported/.test(n)), JSON.stringify(s.notes));
});

await section("real path: elevenlabs music (prompt and composition plan), sfx with loop, tts, dialogue", async () => {
  let mark = seen.length;
  const m = await realCall("audio_music", { prompt: "theme", duration_sec: 30, provider: "elevenlabs" }, { provider: "elevenlabs", model: "music_v2", ext: "mp3", cost: 0.075 });
  let q = since(mark, "/eleven/")[0];
  assert.equal(q.m, "POST"); assert.equal(q.u, "/eleven/music?output_format=mp3_44100_128"); assert.equal(q.h["xi-api-key"], K.eleven); assert.equal(q.h.authorization, undefined);
  assert.deepEqual(jbody(q), { prompt: "theme", music_length_ms: 30000, model_id: "music_v2", force_instrumental: true });
  const lc = await real.call("licence_check", { asset_id: m.files[0].asset_id });
  assert.ok(lc.flags.some((f) => f.code === "revenue_threshold" && f.severity === "error"), JSON.stringify(lc));
  const plan = { positive_global_styles: ["folk"], negative_global_styles: [], sections: [{ section_name: "intro", positive_local_styles: ["calm"], negative_local_styles: [], duration_ms: 8000, lines: [] }] };
  mark = seen.length;
  await realCall("audio_music", { prompt: "ignored", duration_sec: 8, provider: "elevenlabs", composition_plan: plan }, { provider: "elevenlabs", model: "music_v2", ext: "mp3", cost: estimate("elevenlabs", "music", { sec: 8 }) });
  assert.deepEqual(jbody(since(mark, "/eleven/")[0]), { composition_plan: plan, model_id: "music_v2" });
  mark = seen.length;
  await realCall("audio_sfx", { prompt: "coin pickup", duration_sec: 2, loop: true, provider: "elevenlabs" }, { provider: "elevenlabs", model: "eleven_text_to_sound_v2", ext: "mp3", cost: 0.004 });
  q = since(mark, "/eleven/")[0];
  assert.equal(q.u, "/eleven/sound-generation?output_format=mp3_44100_128"); assert.equal(q.h["xi-api-key"], K.eleven);
  assert.deepEqual(jbody(q), { text: "coin pickup", model_id: "eleven_text_to_sound_v2", loop: true, duration_seconds: 2 });
  mark = seen.length;
  await realCall("audio_voice", { text: "Welcome", voice_id: "voice_abc", provider: "elevenlabs" }, { provider: "elevenlabs", model: "eleven_multilingual_v2", ext: "mp3", cost: 0.08 * 7 / 1000 });
  q = since(mark, "/eleven/")[0];
  assert.equal(q.m, "POST"); assert.equal(q.u, "/eleven/text-to-speech/voice_abc?output_format=mp3_44100_128"); assert.equal(q.h["xi-api-key"], K.eleven);
  assert.deepEqual(jbody(q), { text: "Welcome", model_id: "eleven_multilingual_v2" });
  mark = seen.length;
  await realCall("audio_voice", { lines: [{ text: "Hi", voice_id: "v1" }, { text: "Hello there", voice_id: "v2" }], provider: "elevenlabs" }, { provider: "elevenlabs", model: "eleven_v3", ext: "mp3", cost: estimate("elevenlabs", "dialogue", { chars: 14 }) });
  q = since(mark, "/eleven/")[0];
  assert.equal(q.u, "/eleven/text-to-dialogue?output_format=mp3_44100_128");
  assert.deepEqual(jbody(q), { inputs: [{ text: "Hi", voice_id: "v1" }, { text: "Hello there", voice_id: "v2" }], model_id: "eleven_v3" });
});
await section("real path: elevenlabs voice design, then speech with the designed voice", async () => {
  const mark = seen.length, desc = "A gruff old dwarf blacksmith with a warm laugh and slow cadence.";
  await realCall("audio_voice", { text: "Greetings, traveller", voice_description: desc, provider: "elevenlabs" }, { provider: "elevenlabs", model: "eleven_multilingual_v2", ext: "mp3", cost: estimate("elevenlabs", "tts", { chars: 20 }) });
  const q = since(mark, "/eleven/");
  assert.deepEqual(q.map((s) => `${s.m} ${s.u.split("?")[0]}`), ["POST /eleven/text-to-voice/design", "POST /eleven/text-to-voice", "POST /eleven/text-to-speech/voice_designed_1"]);
  assert.ok(q.every((s) => s.h["xi-api-key"] === K.eleven));
  assert.deepEqual(jbody(q[0]), { voice_description: desc, auto_generate_text: true });
  const create = jbody(q[1]); assert.deepEqual([create.voice_description, create.generated_voice_id], [desc, "gen_prev_1"]); assert.match(create.voice_name, /^gs-[0-9a-f]+$/);
  assert.deepEqual(jbody(q[2]), { text: "Greetings, traveller", model_id: "eleven_multilingual_v2" });
  const bad = await real.call("audio_voice", { text: "x", voice_description: "too short", provider: "elevenlabs" });
  assert.ok(bad.isError && /20-1000/.test(bad.error));
});

// =====================================================================================================================
// Part 3: 3D stage chaining (Tripo model -> rig-check -> rig, Meshy preview -> refine) with the jobs file
// =====================================================================================================================
const jobOf = (id, r = rp) => readJson(r, "jobs.json").jobs[id];
const ids = (rq, re) => rq.filter((s) => s.m === "GET").map((s) => s.u.split("/").pop()).find((x) => re.test(x));

await section("tripo: text to rigged model within wait_sec (create, poll, rig-check, rig, download) with stage ledger", async () => {
  const mark = seen.length, nLed = ledgerOf().length;
  const r = await real.call("model3d_generate", { prompt: "knight", provider: "tripo", texture: true, rig: true, face_limit: 3000, wait_sec: 10, id_prefix: "knight" });
  assert.ok(r.ok && !r.pending && !r.placeholder, JSON.stringify(r));
  assert.match(r.files[0].asset_id, /^knight-\d{3}$/); assert.ok(r.files[0].path.endsWith(".glb")); parseGlb(file(rp, r.files[0].path));
  near(r.cost_usd, 0.65); near(r.job_cost_usd, 0.65);
  assert.deepEqual(r.stages.map((s) => [s.name, s.state]), [["model", "done"], ["rig_check", "done"], ["rig", "done"]]);
  const rq = since(mark, "/tripo/"), creates = rq.filter((s) => s.m === "POST");
  assert.deepEqual(creates.map((s) => s.u), ["/tripo/generation/text-to-model", "/tripo/animations/rig-check", "/tripo/animations/rig"]);
  assert.ok(rq.every((s) => s.h.authorization === `Bearer ${K.tripo}`));
  const modelId = ids(rq, /^TM\d+$/), rigId = ids(rq, /^TR\d+$/);
  assert.deepEqual(jbody(creates[0]), { prompt: "knight", model: "P1-20260311", texture: true, pbr: false, face_limit: 3000 });
  assert.deepEqual(jbody(creates[1]), { input: modelId });
  assert.deepEqual(jbody(creates[2]), { input: modelId, out_format: "glb", spec: "mixamo", rig_type: "biped" }, "rig runs on the model task, rig_type comes from rig-check");
  assert.deepEqual(since(mark, "/dl/").map((s) => s.u), [`/dl/${rigId}.glb`], "the rigged model is downloaded");
  const L = ledgerOf().slice(nLed);
  assert.deepEqual(L.map((e) => [e.tool, e.cost_usd]), [["model3d_generate", 0.4], ["model3d_generate", 0.25], ["model3d_generate", 0]], "stage costs at creation, then the asset entry");
  assert.deepEqual(L[2].asset_ids, [r.files[0].asset_id]); assert.deepEqual(L[0].asset_ids, []);
  const a = manifestOf().find((x) => x.id === r.files[0].asset_id);
  near(a.cost_usd, 0.65); assert.equal(a.kind, "model"); assert.equal(a.provider, "tripo"); assert.equal(a.model, "P1-20260311");
  assert.deepEqual(a.params.stages.map((s) => s.name), ["model", "rig_check", "rig"]); assert.equal(a.params.face_limit, 3000);
  const job = jobOf(r.task_id); assert.equal(job.status, "done"); assert.deepEqual(job.asset_ids, [r.files[0].asset_id]); assert.equal(job.stage, 2);
});
await section("tripo: image-to-model uploads the image (multipart file) then creates the task from the file token", async () => {
  const mark = seen.length;
  const r = await real.call("model3d_generate", { image: made.gemini.path, provider: "tripo", wait_sec: 10 });
  assert.ok(r.ok && !r.pending, JSON.stringify(r)); near(r.cost_usd, 0.4); parseGlb(file(rp, r.files[0].path));
  const posts = since(mark, "/tripo/").filter((s) => s.m === "POST");
  assert.deepEqual(posts.map((s) => s.u), ["/tripo/files", "/tripo/generation/image-to-model"]);
  assert.deepEqual(multipart(posts[0]).files.map((f) => [f.name, f.type, f.size]), [["file", "image/png", file(rp, made.gemini.path).length]]);
  assert.deepEqual(jbody(posts[1]), { input: "file_tok_1", model: "P1-20260311", texture: false, pbr: false });
  assert.deepEqual(manifestOf().find((x) => x.id === r.files[0].asset_id).references, [made.gemini.path]);
});
await section("tripo: hand-back, then model3d_status chains rig-check and rig from the jobs file until the file is downloaded", async () => {
  const nLed = ledgerOf().length, nMan = manifestOf().length, mark = seen.length;
  const r = await real.call("model3d_generate", { prompt: "crate", provider: "tripo", rig: true, wait_sec: 0 });
  assert.ok(r.ok && r.pending && r.task_id, JSON.stringify(r));
  assert.equal(r.stage, "model"); assert.deepEqual(r.stages, ["model", "rig_check", "rig"]); near(r.billed_usd, 0.30); near(r.estimated_cost_usd, 0.55); assert.equal(r.current_task_id, r.task_id);
  assert.equal(manifestOf().length, nMan, "no file yet");
  assert.equal(jobOf(r.task_id).status, "running"); assert.deepEqual(jobOf(r.task_id).stages.map((s) => s.state), ["running", "pending", "pending"]);
  assert.ok((await real.call("gs_status")).running_3d_jobs.some((j) => j.task_id === r.task_id && j.stage === "model"));
  let s; const seq = [];
  for (let i = 0; i < 15; i++) { s = await real.call("model3d_status", { provider: "tripo", task_id: r.task_id }); seq.push(s.pending ? s.stage : "done"); if (!s.pending) break; }
  assert.ok(s.ok && !s.pending && s.files?.[0].path.endsWith(".glb"), JSON.stringify(s));
  assert.ok(seq.includes("rig_check") && seq.includes("rig") && seq.at(-1) === "done", `stages seen: ${seq}`);
  assert.equal(s.task_id, r.task_id); assert.deepEqual(s.stages.map((x) => x.state), ["done", "done", "done"]); near(s.job_cost_usd, 0.55);
  parseGlb(file(rp, s.files[0].path));
  const rq = since(mark, "/tripo/"), rigPosts = rq.filter((x) => x.m === "POST" && x.u === "/tripo/animations/rig");
  assert.equal(rigPosts.length, 1, "the rig stage is requested exactly once across repeated status calls");
  const modelId = ids(rq, /^TM\d+$/); assert.equal(jbody(rigPosts[0]).input, modelId);
  assert.deepEqual(ledgerOf().slice(nLed).map((e) => [e.tool, e.cost_usd]), [["model3d_generate", 0.3], ["model3d_status", 0.25], ["model3d_status", 0]]);
  near(manifestOf().find((x) => x.id === s.files[0].asset_id).cost_usd, 0.55);
  // asking again is free and idempotent; any stage id of the job resolves to it
  const m2 = seen.length, l2 = ledgerOf().length;
  const again = await real.call("model3d_status", { provider: "tripo", task_id: r.task_id });
  assert.ok(again.ok && again.already_collected && again.files[0].asset_id === s.files[0].asset_id); near(again.cost_usd, 0);
  const viaStage = await real.call("model3d_status", { provider: "tripo", task_id: jobOf(r.task_id).stages[2].task_id });
  assert.ok(viaStage.already_collected);
  assert.equal(seen.length, m2, "no requests"); assert.equal(ledgerOf().length, l2); assert.equal(manifestOf().length, nMan + 1);
  assert.ok(!(await real.call("gs_status")).running_3d_jobs.some((j) => j.task_id === r.task_id));
});
await section("tripo: a model that is not riggable is returned unrigged and the rig stage is not billed", async () => {
  S.tripo.riggable = false;
  const nLed = ledgerOf().length, mark = seen.length;
  const r = await real.call("model3d_generate", { prompt: "blob", provider: "tripo", rig: true, wait_sec: 10 });
  S.tripo.riggable = true;
  assert.ok(r.ok && !r.pending, JSON.stringify(r)); assert.ok(r.notes.some((n) => /not riggable/.test(n)), JSON.stringify(r.notes));
  assert.deepEqual(r.stages.map((x) => [x.name, x.state]), [["model", "done"], ["rig_check", "done"], ["rig", "skipped"]]); near(r.job_cost_usd, 0.30);
  const rq = since(mark, "/tripo/"); assert.ok(!rq.some((x) => x.u === "/tripo/animations/rig"), "no rig request");
  assert.deepEqual(since(mark, "/dl/").map((x) => x.u), [`/dl/${ids(rq, /^TM\d+$/)}.glb`]);
  assert.deepEqual(ledgerOf().slice(nLed).map((e) => e.cost_usd), [0.3, 0]);
});
await section("tripo: a failing rig stage returns the unrigged model and the rig credits are refunded in the ledger", async () => {
  S.tripo.failRig = true;
  const nLed = ledgerOf().length, mark = seen.length;
  const r = await real.call("model3d_generate", { prompt: "unlucky", provider: "tripo", rig: true, wait_sec: 10 });
  S.tripo.failRig = false;
  assert.ok(r.ok && !r.pending, JSON.stringify(r)); assert.ok(r.notes.some((n) => /rig stage failed.*returning the model result/.test(n)), JSON.stringify(r.notes));
  assert.deepEqual(r.stages.map((x) => [x.name, x.state]), [["model", "done"], ["rig_check", "done"], ["rig", "failed"]]); near(r.job_cost_usd, 0.30);
  const L = ledgerOf().slice(nLed); assert.deepEqual(L.map((e) => e.cost_usd), [0.3, 0.25, -0.25, 0]);
  assert.match(L[2].note, /refunded/);
  const rq = since(mark, "/tripo/"); assert.deepEqual(since(mark, "/dl/").map((x) => x.u), [`/dl/${ids(rq, /^TM\d+$/)}.glb`], "fresh url of the model task is used");
  near(manifestOf().find((x) => x.id === r.files[0].asset_id).cost_usd, 0.30);
});
await section("tripo: a failed download after a fallback is retried by model3d_status without refunding twice", async () => {
  S.tripo.failRig = true; S.dlFail = 4; // download() makes 4 attempts
  const nLed = ledgerOf().length, nMan = manifestOf().length;
  const r = await real.call("model3d_generate", { prompt: "flaky storage", provider: "tripo", rig: true, wait_sec: 10 });
  S.tripo.failRig = false;
  assert.ok(r.isError && /HTTP 500/.test(r.error) && /call model3d_status again/.test(r.error) && r.task_id, JSON.stringify(r));
  assert.equal(manifestOf().length, nMan, "nothing recorded yet"); assert.equal(jobOf(r.task_id).status, "running"); assert.equal(jobOf(r.task_id).chain_done, true);
  const mark = seen.length;
  const s = await real.call("model3d_status", { provider: "tripo", task_id: r.task_id });
  assert.ok(s.ok && !s.pending && s.files[0].path.endsWith(".glb"), JSON.stringify(s)); assert.ok(s.notes.some((n) => /rig stage failed/.test(n)));
  assert.equal(since(mark, "/tripo/").filter((x) => x.m === "POST").length, 0, "no new task is created");
  assert.deepEqual(ledgerOf().slice(nLed).map((e) => e.cost_usd), [0.3, 0.25, -0.25, 0], "exactly one refund"); near(s.job_cost_usd, 0.3);
  assert.equal(manifestOf().length, nMan + 1); assert.equal(jobOf(r.task_id).status, "done");
});
await section("tripo: a failing first stage is an error, credited back, and remembered", async () => {
  S.tripo.failModel = true;
  const nLed = ledgerOf().length, nMan = manifestOf().length;
  const r = await real.call("model3d_generate", { prompt: "doomed", provider: "tripo", wait_sec: 10 });
  S.tripo.failModel = false;
  assert.ok(r.isError && /tripo task failed \(error 2008: moderation\)/.test(r.error) && r.task_id, JSON.stringify(r));
  assert.deepEqual(ledgerOf().slice(nLed).map((e) => e.cost_usd), [0.3, -0.3]); assert.equal(manifestOf().length, nMan);
  assert.equal(jobOf(r.task_id).status, "failed");
  const again = await real.call("model3d_status", { provider: "tripo", task_id: r.task_id });
  assert.ok(again.isError && /failed/.test(again.error));
});
await section("tripo: an unaffordable later stage stops the chain and returns what was built (budget re-checked per stage)", async () => {
  const rp2 = mkProject({ budgets: { asset_usd_cap: 0.7 } });
  const r = await real.call("model3d_generate", { prompt: "tight budget", provider: "tripo", rig: true, wait_sec: 0, project_dir: rp2 });
  assert.ok(r.pending, JSON.stringify(r)); near(r.estimated_cost_usd, 0.55);
  const spend = await real.call("image_generate", { prompt: "x", kind: "icon", provider: "openai", quality: "high", size: "1024", project_dir: rp2 });
  assert.ok(spend.ok, JSON.stringify(spend));
  let s;
  for (let i = 0; i < 15; i++) { s = await real.call("model3d_status", { provider: "tripo", task_id: r.task_id, project_dir: rp2 }); if (!s.pending) break; }
  assert.ok(s.ok && !s.pending, JSON.stringify(s)); assert.ok(s.notes.some((n) => /rig stage not started: refused/.test(n)), JSON.stringify(s.notes));
  assert.deepEqual(s.stages.map((x) => [x.name, x.state]), [["model", "done"], ["rig_check", "done"], ["rig", "skipped"]]);
  near(readJson(rp2, "budget.json").spent_usd, 0.30 + 0.211, "rig was never billed", 1e-6);
});

await section("meshy: text preview then refine within wait_sec (preview body, refine body, textured model downloaded)", async () => {
  const mark = seen.length, nLed = ledgerOf().length;
  const r = await real.call("model3d_generate", { prompt: "wooden barrel", provider: "meshy", texture: true, pbr: true, face_limit: 2000, wait_sec: 10 });
  assert.ok(r.ok && !r.pending && !r.placeholder, JSON.stringify(r)); parseGlb(file(rp, r.files[0].path));
  near(r.cost_usd, 0.60); assert.deepEqual(r.stages.map((x) => [x.name, x.state]), [["preview", "done"], ["refine", "done"]]);
  const rq = since(mark, "/meshy/"), posts = rq.filter((s) => s.m === "POST");
  assert.ok(rq.every((s) => s.h.authorization === `Bearer ${K.meshy}`));
  assert.deepEqual(posts.map((s) => s.u), ["/meshy/v2/text-to-3d", "/meshy/v2/text-to-3d"]);
  const previewId = ids(rq, /^MP\d+$/), refineId = ids(rq, /^MR\d+$/);
  assert.deepEqual(jbody(posts[0]), { mode: "preview", prompt: "wooden barrel", ai_model: "meshy-7.1", should_remesh: true, target_polycount: 2000 });
  assert.deepEqual(jbody(posts[1]), { mode: "refine", preview_task_id: previewId, enable_pbr: true });
  assert.ok(rq.some((s) => s.m === "GET" && s.u === `/meshy/v2/text-to-3d/${previewId}`)); assert.deepEqual(since(mark, "/dl/").map((s) => s.u), [`/dl/${refineId}.glb`]);
  assert.deepEqual(ledgerOf().slice(nLed).map((e) => [e.cost_usd]), [[0.4], [0.2], [0]]);
  near(manifestOf().find((x) => x.id === r.files[0].asset_id).cost_usd, 0.60);
  assert.match(r.task_id, /^text:MP\d+$/);
});
await section("meshy: image-to-3d sends a data URI and textures in one task", async () => {
  const mark = seen.length;
  const r = await real.call("model3d_generate", { image: made.gemini.path, provider: "meshy", texture: true, wait_sec: 10 });
  assert.ok(r.ok && !r.pending, JSON.stringify(r)); near(r.cost_usd, 0.60); assert.deepEqual(r.stages.map((x) => x.name), ["model"]);
  const rq = since(mark, "/meshy/"), posts = rq.filter((s) => s.m === "POST");
  assert.deepEqual(posts.map((s) => s.u), ["/meshy/v1/image-to-3d"]);
  assert.deepEqual(jbody(posts[0]), { image_url: `data:image/png;base64,${file(rp, made.gemini.path).toString("base64")}`, ai_model: "meshy-7.1", should_texture: true, enable_pbr: false });
  assert.ok(rq.some((s) => s.m === "GET" && /^\/meshy\/v1\/image-to-3d\/MI\d+$/.test(s.u)));
  assert.match(r.task_id, /^image:MI\d+$/);
});
await section("meshy: hand-back, then model3d_status (wait_sec) starts the refine stage once and collects the file", async () => {
  const nLed = ledgerOf().length, nMan = manifestOf().length, mark = seen.length;
  const r = await real.call("model3d_generate", { prompt: "stone well", provider: "meshy", texture: true, wait_sec: 0 });
  assert.ok(r.pending && r.stage === "preview" && r.task_id.startsWith("text:"), JSON.stringify(r)); assert.deepEqual(r.stages, ["preview", "refine"]);
  const first = await real.call("model3d_status", { provider: "meshy", task_id: r.task_id });
  assert.ok(first.ok, JSON.stringify(first));
  const s = await real.call("model3d_status", { provider: "meshy", task_id: r.task_id, wait_sec: 10, out_dir: "assets/props", id_prefix: "well" });
  assert.ok(s.ok && !s.pending && s.files[0].path.startsWith("assets/props/") && /^well-\d{3}$/.test(s.files[0].asset_id), JSON.stringify(s));
  assert.equal(since(mark, "/meshy/").filter((x) => x.m === "POST" && jbody(x).mode === "refine").length, 1, "refine created once");
  assert.equal(manifestOf().length, nMan + 1); near(s.job_cost_usd, 0.60);
  assert.deepEqual(ledgerOf().slice(nLed).map((e) => e.cost_usd), [0.4, 0.2, 0]);
});
await section("meshy: a failing refine returns the preview mesh and credits the refine back", async () => {
  S.meshy.failRefine = true;
  const nLed = ledgerOf().length, mark = seen.length;
  const r = await real.call("model3d_generate", { prompt: "failing texture", provider: "meshy", texture: true, wait_sec: 10 });
  S.meshy.failRefine = false;
  assert.ok(r.ok && !r.pending, JSON.stringify(r)); assert.ok(r.notes.some((n) => /refine stage failed \(meshy task FAILED: texture generation failed\)/.test(n)), JSON.stringify(r.notes));
  assert.deepEqual(ledgerOf().slice(nLed).map((e) => e.cost_usd), [0.4, 0.2, -0.2, 0]); near(r.job_cost_usd, 0.4);
  assert.deepEqual(since(mark, "/dl/").map((x) => x.u), [`/dl/${ids(since(mark, "/meshy/"), /^MP\d+$/)}.glb`]);
});
await section("meshy: two concurrent model3d_status calls cannot start the same stage twice", async () => {
  const mark = seen.length, nMan = manifestOf().length;
  const r = await real.call("model3d_generate", { prompt: "race", provider: "meshy", texture: true, wait_sec: 0 });
  assert.ok(r.pending, JSON.stringify(r));
  const [a, b] = await Promise.all([1, 2].map(() => real.call("model3d_status", { provider: "meshy", task_id: r.task_id, wait_sec: 10 })));
  assert.equal(since(mark, "/meshy/").filter((x) => x.m === "POST" && jbody(x).mode === "refine").length, 1, "one refine request");
  assert.equal([a, b].filter((x) => x.ok && !x.already_collected && x.files).length, 1); assert.equal([a, b].filter((x) => x.already_collected).length, 1);
  assert.equal(manifestOf().length, nMan + 1, "one asset");
});
await section("3D status: a task without pipeline state in this project is collected without chaining", async () => {
  S.tripo.tasks.TMlegacy = { kind: "model", polls: 99 };
  const r = await real.call("model3d_status", { provider: "tripo", task_id: "TMlegacy" });
  assert.ok(r.ok && r.files[0].path.endsWith(".glb") && r.cost_usd === 0 && r.notes.some((n) => /no pipeline state/.test(n)), JSON.stringify(r));
  parseGlb(file(rp, r.files[0].path));
  const wrong = await real.call("model3d_status", { provider: "meshy", task_id: Object.keys(readJson(rp, "jobs.json").jobs).find((id) => /^TM\d+$/.test(id)) });
  assert.ok(wrong.isError && /belongs to a tripo job/.test(wrong.error), JSON.stringify(wrong));
  const unknown = await real.call("model3d_status", { provider: "meshy", task_id: "text:nope" });
  assert.ok(unknown.isError && /HTTP 404/.test(unknown.error), JSON.stringify(unknown));
});

await section("jobs file stays small and valid JSON; downloads never carry credentials", async () => {
  const db = readJson(rp, "jobs.json");
  assert.equal(db.schema_version, "1.0"); assert.ok(Object.keys(db.jobs).length >= 10);
  assert.ok(fs.statSync(path.join(rp, ".gamestudio/jobs.json")).size < 100000);
  for (const j of Object.values(db.jobs)) { assert.ok(["running", "done", "failed"].includes(j.status)); assert.equal(j.id, j.stages[0].task_id); assert.ok(!JSON.stringify(j).includes(SECRET), "no key in the jobs file"); }
  const dls = seen.filter((s) => s.u.startsWith("/dl/")); assert.ok(dls.length > 15);
  for (const s of dls) assert.ok(!s.h.authorization && !s.h["x-goog-api-key"] && !s.h["xi-api-key"], `credentials sent to a download url: ${s.u}`);
});

await section("coverage: every provider request path (create, poll, result, download) was hit on the fake server", async () => {
  const norm = (r) => `${r.m} ${r.u.split("?")[0]}`.replace(/\/requests\/REQ\d+/, "/requests/:id").replace(/\/tasks\/\w+$/, "/tasks/:id").replace(/\/results\/\w+$/, "/results/:id")
    .replace(/\/(text-to-3d|image-to-3d)\/\w+$/, "/$1/:id").replace(/\/text-to-speech\/[\w-]+$/, "/text-to-speech/:voice").replace(/\/dl\/.*/, "/dl/*");
  const hit = new Set(seen.map(norm));
  const expected = [
    "POST /gemini/interactions", "POST /openai/images/generations", "POST /openai/images/edits",
    "POST /recraft/images/generations", "POST /recraft/images/removeBackground", "POST /recraft/images/vectorize", "POST /recraft/images/crispUpscale",
    "POST /fal/fal-ai/flux/schnell", "GET /fal/fal-ai/flux/requests/:id/status", "GET /fal/fal-ai/flux/requests/:id",
    "POST /stability/stable-image/generate/core", "POST /stability/audio/stable-audio/text-to-audio", "GET /stability/audio/results/:id",
    "POST /eleven/music", "POST /eleven/sound-generation", "POST /eleven/text-to-speech/:voice", "POST /eleven/text-to-dialogue", "POST /eleven/text-to-voice/design", "POST /eleven/text-to-voice",
    "POST /tripo/files", "POST /tripo/generation/text-to-model", "POST /tripo/generation/image-to-model", "POST /tripo/animations/rig-check", "POST /tripo/animations/rig", "GET /tripo/tasks/:id",
    "POST /meshy/v2/text-to-3d", "POST /meshy/v1/image-to-3d", "GET /meshy/v2/text-to-3d/:id", "GET /meshy/v1/image-to-3d/:id", "GET /dl/*",
  ];
  assert.deepEqual(expected.filter((e) => !hit.has(e)), [], "request paths never exercised");
  assert.ok(![...hit].some((h) => /no route/.test(h)) && !seen.some((r) => r.u.startsWith("/openai/") && !/images\/(generations|edits)/.test(r.u)), "no request fell outside the documented routes");
});

await section("pricing.json: default ids, verified entries carry a source, price anchors", async () => {
  const data = JSON.parse(fs.readFileSync(path.join(path.dirname(SERVER), "pricing.json"), "utf8")), model = (k) => data.models[k].model;
  for (const [k, e] of Object.entries(data.models)) {
    assert.ok(e.model && e.unit && typeof e.usd === "number" && typeof e.verified === "boolean", k);
    if (e.verified) assert.ok(/^https:\/\//.test(e.source) && e.verified_via, `${k}: verified entries need source and verified_via`);
  }
  assert.deepEqual(["gemini.image", "gemini.image_edit", "gemini.music", "gemini.tts", "openai.image", "openai.image_edit", "recraft.image", "recraft.image_vector", "fal.image", "stability.audio", "tripo.model3d", "meshy.model3d", "elevenlabs.music", "elevenlabs.sfx", "elevenlabs.tts", "elevenlabs.dialogue"].map(model),
    ["gemini-nano-banana-2.1", "gemini-nano-banana-2.1", "lyria-3.5", "gemini-3.8-flash-tts", "gpt-image-2.5-flare", "gpt-image-2.5-sunburst", "recraftv4_1", "recraftv4_1_vector", "fal-ai/flux/schnell", "stable-audio-3", "P1-20260311", "meshy-7.1", "music_v2", "eleven_text_to_sound_v2", "eleven_multilingual_v2", "eleven_v3"]);
  assert.ok(!JSON.stringify(data).includes('"model": "gemini-2.5-flash-image"'), "the shut-down legacy model is not a default");
  near(estimate("gemini", "image", { tier: "1K" }), 0.0336); near(estimate("gemini", "image", { tier: "2K" }), 0.0504); near(estimate("gemini", "image", { model: "gemini-3-pro-image", tier: "4K" }), 0.24);
  near(estimate("recraft", "image"), 0.035); near(estimate("recraft", "image_vector"), 0.08); near(estimate("recraft", "image", { model: "recraftv4_1_pro", n: 2 }), 0.42);
  near(estimate("recraft", "remove_background"), 0.01); near(estimate("recraft", "upscale"), 0.004); near(estimate("stability", "audio"), 0.08);
  near(estimate("gemini", "music", { model: "lyria-3-clip-preview" }), 0.04); near(estimate("elevenlabs", "music", { sec: 60 }), 0.15); near(estimate("elevenlabs", "sfx", { sec: 60 }), 0.12);
  near(estimate("openai", "image", { tier: "low" }), 0.006); near(estimate("fal", "image", { n: 2, mp: 4 }), 0.024);
  assert.ok(data.models["tripo.model3d"].verified === false && data.models["openai.image"].verified === false, "unconfirmed prices stay unverified");
});

// =====================================================================================================================
// Part 4: the opt-in live smoke script (dry run prints the request; --yes makes ONE call), against local servers only
// =====================================================================================================================
function runSmoke(args, env = {}) {
  return new Promise((resolve) => {
    const p = spawn(process.execPath, [SMOKE, ...args], { env: { ...process.env, ...NO_KEYS, GS_MOCK: "", GS_POLL_MS: "20", GS_RETRY_BASE_MS: "5", ...env }, stdio: ["ignore", "pipe", "pipe"] });
    let out = "", err = "";
    p.stdout.on("data", (d) => (out += d)); p.stderr.on("data", (d) => (err += d));
    p.on("close", (code) => resolve({ code, out, err, project: (out.match(/\(project (\S+)\)/) || [])[1] }));
  });
}
const tidy = (r) => { if (r.project && r.project.includes("gs-live-")) fs.rmSync(r.project, { recursive: true, force: true }); return r; }; // --yes keeps its throwaway project for inspection
await section("live-smoke: usage errors exit 2 and need the provider key in the environment", async () => {
  let r = await runSmoke([]); assert.equal(r.code, 2); assert.match(r.err, /--provider is required/); assert.match(r.err, /usage: node test\/live-smoke\.mjs/);
  r = await runSmoke(["--provider", "nope"]); assert.equal(r.code, 2); assert.match(r.err, /unknown provider "nope"/);
  r = await runSmoke(["--provider", "openai", "--kind", "video"]); assert.equal(r.code, 2);
  r = await runSmoke(["--provider", "openai"]); assert.equal(r.code, 2); assert.match(r.err, /OPENAI_API_KEY is not set/);
  r = await runSmoke(["--help"]); assert.equal(r.code, 0); assert.match(r.out, /elevenlabs\s+ELEVENLABS_API_KEY\s+sfx, tts, music, dialogue/);
});
await section("live-smoke: the default is a dry run that prints the exact request and the estimated cost, sending nothing", async () => {
  const mark = seen.length;
  let r = await runSmoke(["--provider", "openai"], { OPENAI_API_KEY: K.openai });
  assert.equal(r.code, 0, r.err + r.out);
  assert.match(r.out, /mode: DRY RUN \(nothing was sent to the provider\)/); assert.match(r.out, /POST https:\/\/api\.openai\.com\/v1\/images\/generations/);
  assert.match(r.out, /authorization: Bearer <OPENAI_API_KEY>/); assert.match(r.out, /estimated cost: \$0\.0060/); assert.match(r.out, /"model": "gpt-image-2\.5-flare"/); assert.match(r.out, /"quality": "low"/); assert.match(r.out, /run again with --yes/);
  assert.ok(!r.out.includes(K.openai) && !r.err.includes(K.openai), "key is redacted");
  r = await runSmoke(["--provider", "tripo"], { TRIPO_API_KEY: K.tripo });
  assert.equal(r.code, 0, r.err); assert.match(r.out, /POST https:\/\/openapi\.tripo3d\.com\/v3\/generation\/text-to-model/); assert.match(r.out, /"model": "P1-20260311"/); assert.match(r.out, /"face_limit": 500/); assert.match(r.out, /estimated cost: \$0\.3000/);
  r = await runSmoke(["--provider", "stability", "--kind", "audio"], { STABILITY_API_KEY: K.stability });
  assert.equal(r.code, 0, r.err); assert.match(r.out, /POST https:\/\/api\.stability\.ai\/v2beta\/audio\/stable-audio\/text-to-audio/); assert.match(r.out, /accept: audio\/\*/); assert.match(r.out, /field model = stable-audio-3/);
  r = await runSmoke(["--provider", "gemini"], { GEMINI_API_KEY: K.gemini });
  assert.equal(r.code, 0, r.err); assert.match(r.out, /POST https:\/\/generativelanguage\.googleapis\.com\/v1beta\/interactions/); assert.match(r.out, /x-goog-api-key: <GEMINI_API_KEY>/); assert.match(r.out, /"image_size": "1K"/);
  r = await runSmoke(["--provider", "meshy"], { MESHY_API_KEY: K.meshy });
  assert.equal(r.code, 0, r.err); assert.match(r.out, /\/openapi\/v2\/text-to-3d/); assert.match(r.out, /"mode": "preview"/);
  assert.equal(seen.length, mark, "a dry run reaches no server");
});
await section("live-smoke --yes: ONE real request through the gateway into a throwaway project, with the cap enforced", async () => {
  let mark = seen.length;
  let r = tidy(await runSmoke(["--provider", "openai", "--yes"], { OPENAI_API_KEY: K.openai, GS_OPENAI_BASE_URL: `${base}/openai` }));
  assert.equal(r.code, 0, r.out + r.err);
  assert.match(r.out, /mode: LIVE: sending ONE real request/); assert.match(r.out, /OK: .*gs-live-.*\.png/); assert.match(r.out, /manifest: provider=openai model=gpt-image-2\.5-flare status=candidate cost_usd=0\.006 /); assert.match(r.out, /ledger: spent_usd=0\.006 of cap \$0\.25/);
  const gens = since(mark, "/openai/").filter((s) => s.u === "/openai/images/generations"); assert.equal(gens.length, 1, "exactly one billed request");
  assert.equal(jbody(gens[0]).quality, "low"); assert.equal(gens[0].h.authorization, `Bearer ${K.openai}`);
  assert.ok(!r.out.includes(K.openai) && !r.err.includes(K.openai));
  mark = seen.length;
  r = tidy(await runSmoke(["--provider", "openai", "--yes", "--max-usd", "0.001"], { OPENAI_API_KEY: K.openai, GS_OPENAI_BASE_URL: `${base}/openai` }));
  assert.equal(r.code, 1); assert.match(r.err, /FAILED: refused: estimated cost \$0\.006 exceeds/); assert.equal(seen.length, mark, "refused before sending");
  mark = seen.length;
  r = tidy(await runSmoke(["--provider", "tripo", "--yes"], { TRIPO_API_KEY: K.tripo, GS_TRIPO_BASE_URL: `${base}/tripo` }));
  assert.equal(r.code, 0, r.out + r.err); assert.match(r.out, /OK: .*\.glb/); assert.match(r.out, /manifest: provider=tripo model=P1-20260311 status=candidate cost_usd=0\.3 /);
  assert.equal(since(mark, "/tripo/").filter((s) => s.m === "POST").length, 1, "one billed task");
  assert.equal(jbody(since(mark, "/tripo/").find((s) => s.m === "POST")).face_limit, 500);
  mark = seen.length;
  r = tidy(await runSmoke(["--provider", "stability", "--kind", "audio", "--yes"], { STABILITY_API_KEY: K.stability, GS_STABILITY_BASE_URL: `${base}/stability` }));
  assert.equal(r.code, 0, r.out + r.err); assert.match(r.out, /OK: .*\.mp3/); assert.equal(since(mark, "/stability/audio/").filter((s) => s.m === "POST").length, 1);
});

await real.close(); fake.close();
await section("secrets never reach stderr", async () => { for (const k of Object.values(K)) assert.ok(!real.err.includes(k), "a provider key leaked to stderr"); assert.ok(!real.err.includes(SECRET)); });

if (!failed) for (const d of tmpDirs) fs.rmSync(d, { recursive: true, force: true });
console.log(failed ? `\n${failed} of ${total} test groups failed` : `\nall ${total} test groups passed`);
process.exit(failed ? 1 : 0);
