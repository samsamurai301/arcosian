// Shared helpers: errors, JSON files, hashing, HTTP with retry. Never logs secrets.
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";

export class ToolError extends Error {
  constructor(message, data) { super(message); this.data = data || {}; }
}
export const sha256 = (buf) => crypto.createHash("sha256").update(buf).digest("hex");
export const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
export const num = (v) => (v === undefined || v === null || v === "" || !Number.isFinite(Number(v)) ? null : Number(v));
export const round6 = (n) => Math.round(n * 1e6) / 1e6;
export const log = (...a) => process.stderr.write(`[studio-gateway] ${redact(a.join(" "))}\n`);
export const pollMs = () => num(process.env.GS_POLL_MS) ?? 3000;
export const baseUrl = (provider, dflt) => (process.env[`GS_${provider.toUpperCase()}_BASE_URL`] || dflt).replace(/\/$/, "");
export const b64 = (buf) => Buffer.from(buf).toString("base64");
export const mimeExt = (m) => ({ "image/png": "png", "image/jpeg": "jpg", "image/webp": "webp", "audio/mpeg": "mp3", "audio/mp3": "mp3", "audio/wav": "wav", "audio/x-wav": "wav" }[String(m || "").split(";")[0]] || "bin");
// File extension from magic bytes (provider responses do not always state a media type); dflt when unknown.
export function sniffExt(buf, dflt = "bin") {
  const b = Buffer.from(buf), at = (o, n) => b.toString("latin1", o, o + n);
  if (b.length >= 8 && b[0] === 0x89 && at(1, 3) === "PNG") return "png";
  if (b.length >= 3 && b[0] === 0xff && b[1] === 0xd8 && b[2] === 0xff) return "jpg";
  if (b.length >= 12 && at(0, 4) === "RIFF" && at(8, 4) === "WEBP") return "webp";
  if (b.length >= 12 && at(0, 4) === "RIFF" && at(8, 4) === "WAVE") return "wav";
  if (b.length >= 3 && at(0, 3) === "ID3") return "mp3";
  if (b.length >= 2 && b[0] === 0xff && (b[1] & 0xe0) === 0xe0) return "mp3";
  if (at(0, 4) === "OggS") return "ogg";
  if (at(0, 4) === "fLaC") return "flac";
  if (at(0, 4) === "glTF") return "glb";
  if (/^\s*(<\?xml|<svg)/i.test(b.toString("utf8", 0, 120))) return "svg";
  return dflt;
}
export const extMime = (p) => ({ ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp" }[path.extname(p).toLowerCase()] || "application/octet-stream");

export function redact(s) {
  let out = String(s);
  for (const [k, v] of Object.entries(process.env)) {
    if (/KEY|TOKEN|SECRET/.test(k) && v && v.length > 6) out = out.split(v).join("[redacted]");
  }
  return out;
}
export function readJson(p, fallback) {
  try { return JSON.parse(fs.readFileSync(p, "utf8")); } catch { return fallback; }
}
export function writeJson(p, obj) {
  fs.mkdirSync(path.dirname(p), { recursive: true });
  const tmp = `${p}.${process.pid}.tmp`;
  fs.writeFileSync(tmp, JSON.stringify(obj, null, 2) + "\n");
  fs.renameSync(tmp, p);
}

// fetch with timeout, retry with exponential backoff on 429/5xx and network errors.
// expect: "json" | "buffer" | "text" | "response" (-> {status, headers, body: Buffer}, for 200 vs 202 polling).
export async function http(url, { method = "GET", headers = {}, body, timeoutMs = 60000, retries = 3, expect = "json" } = {}) {
  const baseDelay = num(process.env.GS_RETRY_BASE_MS) ?? 800;
  for (let attempt = 0; ; attempt++) {
    const ac = new AbortController();
    const timer = setTimeout(() => ac.abort(), timeoutMs);
    try {
      const res = await fetch(url, { method, headers, body, signal: ac.signal });
      if ((res.status === 429 || res.status >= 500) && attempt < retries) {
        const ra = num(res.headers.get("retry-after"));
        await res.arrayBuffer().catch(() => {});
        await sleep(Math.min(ra !== null ? ra * 1000 : baseDelay * 2 ** attempt, 30000));
        continue;
      }
      if (!res.ok) {
        const txt = (await res.text().catch(() => "")).slice(0, 300);
        throw new ToolError(redact(`HTTP ${res.status} from ${new URL(url).host}: ${txt}`));
      }
      if (expect === "buffer") return Buffer.from(await res.arrayBuffer());
      if (expect === "response") return { status: res.status, headers: res.headers, body: Buffer.from(await res.arrayBuffer()) };
      return expect === "text" ? await res.text() : await res.json();
    } catch (e) {
      if (e instanceof ToolError) throw e;
      if (attempt < retries) { await sleep(baseDelay * 2 ** attempt); continue; }
      throw new ToolError(redact(`network error calling ${new URL(url).host}: ${e.name === "AbortError" ? "timeout" : e.message}`));
    } finally {
      clearTimeout(timer);
    }
  }
}
export const download = (url) => http(url, { expect: "buffer", timeoutMs: 120000 });

// multipart helper: fields {k: string}, files [{name, buf, filename, mime}]
export function form(fields, files = []) {
  const f = new FormData();
  for (const [k, v] of Object.entries(fields)) if (v !== undefined && v !== null) f.append(k, String(v));
  for (const x of files) f.append(x.name, new Blob([x.buf], { type: x.mime }), x.filename);
  return f;
}
