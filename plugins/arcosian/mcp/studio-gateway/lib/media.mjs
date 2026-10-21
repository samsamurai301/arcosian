// Placeholder media generators (mock mode): valid PNG, WAV, GLB, SVG. Pure Node, no dependencies.
import zlib from "node:zlib";
import { sha256, ToolError } from "./util.mjs";

const CRC = new Uint32Array(256).map((_, n) => {
  let c = n;
  for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
  return c >>> 0;
});
export function crc32(buf) {
  let c = 0xffffffff;
  for (const b of buf) c = CRC[(c ^ b) & 255] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}
export const seedOf = (s) => parseInt(sha256(Buffer.from(String(s))).slice(0, 8), 16);

// "1024x768" | "1024" -> [w, h] clamped to 1..2048
export function parseSize(size, dflt = 1024) {
  if (size === undefined || size === null || size === "" || size === "auto") return [dflt, dflt];
  const m = String(size).trim().match(/^(\d{1,5})(?:\s*[x×]\s*(\d{1,5}))?$/i);
  if (!m) throw new ToolError(`size must look like "1024" or "1024x768", got "${size}"`);
  const c = (v) => Math.max(1, Math.min(2048, parseInt(v, 10)));
  return [c(m[1]), c(m[2] || m[1])];
}

function chunk(type, data) {
  const len = Buffer.alloc(4);
  len.writeUInt32BE(data.length);
  const body = Buffer.concat([Buffer.from(type, "ascii"), data]);
  const crc = Buffer.alloc(4);
  crc.writeUInt32BE(crc32(body));
  return Buffer.concat([len, body, crc]);
}
export function makePng(w, h, { seed = 0, alpha = false } = {}) {
  const bpp = alpha ? 4 : 3;
  const stride = 1 + w * bpp;
  const raw = Buffer.alloc(stride * h);
  const hue = seed % 200;
  for (let y = 0; y < h; y++) {
    let o = y * stride;
    raw[o++] = 0; // filter: none
    for (let x = 0; x < w; x++) {
      raw[o++] = (hue + (x * 55) / w) & 255;
      raw[o++] = (90 + (y * 120) / h) & 255;
      raw[o++] = (200 - hue / 2 + (x * y * 40) / (w * h)) & 255;
      if (alpha) {
        const dx = (x + 0.5) / w - 0.5, dy = (y + 0.5) / h - 0.5;
        raw[o++] = dx * dx + dy * dy <= 0.16 ? 255 : 0; // transparent corners
      }
    }
  }
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(w, 0);
  ihdr.writeUInt32BE(h, 4);
  ihdr[8] = 8; ihdr[9] = alpha ? 6 : 2;
  return Buffer.concat([
    Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]),
    chunk("IHDR", ihdr), chunk("IDAT", zlib.deflateSync(raw, { level: 3 })), chunk("IEND", Buffer.alloc(0)),
  ]);
}
export function pngSize(buf) {
  if (buf.length > 24 && buf.readUInt32BE(0) === 0x89504e47) return [buf.readUInt32BE(16), buf.readUInt32BE(20)];
  return null;
}

export function wavFromPcm(pcm, rate = 44100) {
  const h = Buffer.alloc(44);
  h.write("RIFF", 0); h.writeUInt32LE(36 + pcm.length, 4); h.write("WAVEfmt ", 8);
  h.writeUInt32LE(16, 16); h.writeUInt16LE(1, 20); h.writeUInt16LE(1, 22);
  h.writeUInt32LE(rate, 24); h.writeUInt32LE(rate * 2, 28); h.writeUInt16LE(2, 32); h.writeUInt16LE(16, 34);
  h.write("data", 36); h.writeUInt32LE(pcm.length, 40);
  return Buffer.concat([h, pcm]);
}
// 44.1 kHz 16-bit mono; kind "tone" (sine with fades) or "silence". Duration capped at 30 s for placeholders.
export function makeWav(sec, { kind = "tone", seed = 0 } = {}) {
  const rate = 44100;
  const n = Math.max(1, Math.round(Math.min(Math.max(sec, 0.05), 30) * rate));
  const pcm = Buffer.alloc(n * 2);
  if (kind === "tone") {
    const freq = 220 + (seed % 440), fade = Math.min(441, n >> 1);
    for (let i = 0; i < n; i++) {
      const env = Math.min(1, i / fade, (n - 1 - i) / fade);
      pcm.writeInt16LE(Math.round(Math.sin((2 * Math.PI * freq * i) / rate) * 0.3 * 32767 * env), i * 2);
    }
  }
  return wavFromPcm(pcm, rate);
}

// Unit cube (24 verts with normals, 36 u16 indices), one material, JSON + BIN chunks.
export function makeGlb() {
  const faces = [[[1, 0, 0], [[.5, -.5, -.5], [.5, .5, -.5], [.5, .5, .5], [.5, -.5, .5]]],
    [[-1, 0, 0], [[-.5, -.5, .5], [-.5, .5, .5], [-.5, .5, -.5], [-.5, -.5, -.5]]],
    [[0, 1, 0], [[-.5, .5, -.5], [-.5, .5, .5], [.5, .5, .5], [.5, .5, -.5]]],
    [[0, -1, 0], [[-.5, -.5, .5], [-.5, -.5, -.5], [.5, -.5, -.5], [.5, -.5, .5]]],
    [[0, 0, 1], [[-.5, -.5, .5], [.5, -.5, .5], [.5, .5, .5], [-.5, .5, .5]]],
    [[0, 0, -1], [[.5, -.5, -.5], [-.5, -.5, -.5], [-.5, .5, -.5], [.5, .5, -.5]]]];
  const pos = [], nor = [], idx = [];
  faces.forEach(([n, vs], f) => {
    vs.forEach((v) => { pos.push(...v); nor.push(...n); });
    const b = f * 4;
    idx.push(b, b + 1, b + 2, b, b + 2, b + 3);
  });
  const bin = Buffer.alloc(24 * 12 * 2 + 72);
  pos.forEach((v, i) => bin.writeFloatLE(v, i * 4));
  nor.forEach((v, i) => bin.writeFloatLE(v, 288 + i * 4));
  idx.forEach((v, i) => bin.writeUInt16LE(v, 576 + i * 2));
  const json = {
    asset: { version: "2.0", generator: "studio-gateway placeholder" },
    scene: 0, scenes: [{ nodes: [0] }], nodes: [{ mesh: 0, name: "placeholder_cube" }],
    meshes: [{ primitives: [{ attributes: { POSITION: 0, NORMAL: 1 }, indices: 2, material: 0 }] }],
    materials: [{ pbrMetallicRoughness: { baseColorFactor: [0.8, 0.5, 0.2, 1], metallicFactor: 0, roughnessFactor: 0.8 } }],
    buffers: [{ byteLength: bin.length }],
    bufferViews: [{ buffer: 0, byteOffset: 0, byteLength: 288, target: 34962 }, { buffer: 0, byteOffset: 288, byteLength: 288, target: 34962 },
      { buffer: 0, byteOffset: 576, byteLength: 72, target: 34963 }],
    accessors: [{ bufferView: 0, componentType: 5126, count: 24, type: "VEC3", min: [-0.5, -0.5, -0.5], max: [0.5, 0.5, 0.5] },
      { bufferView: 1, componentType: 5126, count: 24, type: "VEC3" }, { bufferView: 2, componentType: 5123, count: 36, type: "SCALAR" }],
  };
  let js = Buffer.from(JSON.stringify(json));
  js = Buffer.concat([js, Buffer.alloc((4 - (js.length % 4)) % 4, 0x20)]);
  const head = (len, type) => { const b = Buffer.alloc(8); b.writeUInt32LE(len, 0); b.writeUInt32LE(type, 4); return b; };
  const total = 12 + 8 + js.length + 8 + bin.length;
  const hdr = Buffer.alloc(12);
  hdr.writeUInt32LE(0x46546c67, 0); hdr.writeUInt32LE(2, 4); hdr.writeUInt32LE(total, 8);
  return Buffer.concat([hdr, head(js.length, 0x4e4f534a), js, head(bin.length, 0x004e4942), bin]);
}

export const makeSvg = (seed = 0) =>
  Buffer.from(`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><circle cx="32" cy="32" r="28" fill="hsl(${seed % 360},60%,55%)"/></svg>\n`);
