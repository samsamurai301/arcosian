// Recraft API (docs: recraft.ai/docs/api-reference, verified 2026-10-20). Bearer auth.
// Generations: raster or vector is chosen by the model id (*_vector returns SVG). size is an exact WxH from the documented
// list for raster models and a w:h ratio for vector models (the caller maps it). The default raster output is WebP, so png
// is requested. removeBackground, vectorize and crispUpscale take a multipart "file" and answer {image: {url}}.
// Result URLs are valid for about 24 hours: they are downloaded right away.
import { http, baseUrl, form, download, sniffExt, ToolError } from "../lib/util.mjs";

export const DEFAULT_BASE = "https://external.api.recraft.ai/v1";
const B = () => baseUrl("recraft", DEFAULT_BASE);
const auth = (key) => ({ authorization: `Bearer ${key}` });

export async function image({ key, model, prompt, n = 1, size = "1024x1024", vector, seed }) {
  const body = { prompt, model, n, size, response_format: "url" };
  if (!vector) body.image_format = "png";
  if (seed !== undefined && seed !== null) body.random_seed = seed;
  const r = await http(`${B()}/images/generations`, { method: "POST", headers: { ...auth(key), "content-type": "application/json" }, body: JSON.stringify(body), timeoutMs: 180000 });
  const urls = (r?.data || []).map((d) => d && d.url).filter(Boolean);
  if (!urls.length) throw new ToolError("recraft returned no image url");
  return Promise.all(urls.map(async (u) => { const bytes = await download(u); return { bytes, ext: vector ? "svg" : sniffExt(bytes, "png") }; }));
}
// op: removeBackground | vectorize | crispUpscale; src: {buf, mime, filename}
export async function postprocess({ key, op, src }) {
  const fields = op === "vectorize" ? {} : { image_format: "png" };
  const r = await http(`${B()}/images/${op}`, { method: "POST", headers: auth(key), body: form(fields, [{ name: "file", ...src }]), timeoutMs: 180000 });
  const url = r?.image?.url || r?.data?.[0]?.url;
  if (!url) throw new ToolError(`recraft ${op} returned no image url`);
  const bytes = await download(url);
  return [{ bytes, ext: op === "vectorize" ? "svg" : sniffExt(bytes, "png") }];
}
