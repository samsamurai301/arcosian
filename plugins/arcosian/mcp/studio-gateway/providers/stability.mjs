// Stability AI (optional; Bearer auth, https://api.stability.ai/v2beta):
//  - image: POST /stable-image/generate/core (multipart, Accept image/* returns the bytes). Endpoint confirmed on docs.stability.ai.
//  - audio: Stable Audio 3.0, verified 2026-10-20 against docs.stability.ai/api-reference/stable-audio/text-to-audio:
//    POST /audio/stable-audio/text-to-audio (multipart prompt, model, duration 1-380 s, seed, steps, cfg_scale, output_format
//    mp3|wav) answers 202 {id}; GET /audio/results/{id} answers 202 while running and 200 with the audio (Accept audio/*).
import { http, baseUrl, form, sleep, pollMs, ToolError, sniffExt } from "../lib/util.mjs";

export const DEFAULT_BASE = "https://api.stability.ai/v2beta";
const B = () => baseUrl("stability", DEFAULT_BASE);

export async function image({ key, prompt, n = 1, aspect = "1:1", seed }) {
  const one = async () => ({
    bytes: await http(`${B()}/stable-image/generate/core`, {
      method: "POST", headers: { authorization: `Bearer ${key}`, accept: "image/*" },
      body: form({ prompt, aspect_ratio: aspect, output_format: "png", seed }), expect: "buffer", timeoutMs: 120000,
    }),
    ext: "png",
  });
  return Promise.all(Array.from({ length: n }, one));
}

// duration_sec is sent as duration (clamped by the caller to 1-380). Also accepts a synchronous 200 audio answer.
export async function audio({ key, model, prompt, duration_sec, timeoutSec = 600 }) {
  const headers = { authorization: `Bearer ${key}`, accept: "audio/*" };
  const fields = { prompt, model, output_format: "mp3" };
  if (duration_sec) fields.duration = duration_sec;
  const made = await http(`${B()}/audio/stable-audio/text-to-audio`, { method: "POST", headers, body: form(fields), expect: "response", timeoutMs: 180000 });
  const media = (r) => [{ bytes: r.body, ext: sniffExt(r.body, "mp3") }];
  if (made.status === 200 && /^audio\//i.test(made.headers.get("content-type") || "")) return media(made);
  let id;
  try { id = JSON.parse(made.body.toString("utf8")).id; } catch { /* handled below */ }
  if (!id) throw new ToolError("stability audio returned neither audio nor a generation id");
  const deadline = Date.now() + timeoutSec * 1000;
  for (;;) {
    const r = await http(`${B()}/audio/results/${encodeURIComponent(id)}`, { headers, expect: "response", timeoutMs: 120000 });
    if (r.status === 200) return media(r);
    if (r.status !== 202) throw new ToolError(`stability audio result ${id}: unexpected HTTP ${r.status}`);
    if (Date.now() > deadline) throw new ToolError(`stability audio ${id} still running after ${timeoutSec}s`);
    await sleep(pollMs());
  }
}
