// OpenAI Images API (GPT Image family, docs: developers.openai.com/api/docs/guides/image-generation, verified 2026-10-20):
// POST /images/generations (JSON) and POST /images/edits (multipart, image[] files). Bearer auth. GPT Image models always
// return base64 (data[].b64_json); response_format is not sent. quality is always sent so the cost estimate holds.
import { http, baseUrl, form, ToolError, sniffExt } from "../lib/util.mjs";

export const DEFAULT_BASE = "https://api.openai.com/v1";
const URL_BASE = () => baseUrl("openai", DEFAULT_BASE);
const outs = (r) => {
  const list = (r?.data || []).filter((d) => d && d.b64_json);
  if (!list.length) throw new ToolError("openai returned no image data (b64_json missing)");
  return list.map((d) => { const bytes = Buffer.from(d.b64_json, "base64"); return { bytes, ext: sniffExt(bytes, "png") }; });
};

// size: 1024x1024 | 1536x1024 | 1024x1536 | auto; quality: low | medium | high; transparent needs png/webp (2.5 models).
export async function image({ key, model, prompt, n = 1, size = "1024x1024", quality = "medium", transparent }) {
  const body = { model, prompt, n, size, quality, output_format: "png" };
  if (transparent) body.background = "transparent";
  return outs(await http(`${URL_BASE()}/images/generations`, {
    method: "POST", headers: { authorization: `Bearer ${key}`, "content-type": "application/json" }, body: JSON.stringify(body), timeoutMs: 240000,
  }));
}
// images: [{buf, mime, filename}] (the first is the source); the multipart field is image[] for every file.
export async function edit({ key, model, prompt, n = 1, size, quality = "medium", images }) {
  const fd = form({ model, prompt, n, size, quality, output_format: "png" }, images.map((i) => ({ name: "image[]", ...i })));
  return outs(await http(`${URL_BASE()}/images/edits`, { method: "POST", headers: { authorization: `Bearer ${key}` }, body: fd, timeoutMs: 240000 }));
}
