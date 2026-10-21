// Meshy (https://api.meshy.ai/openapi; Bearer auth). Task ids are "text:<id>" or "image:<id>" (they pick the endpoint).
// Text flow: POST /v2/text-to-3d {mode: preview, prompt, ai_model, should_remesh, target_polycount} (untextured mesh), then, for a
// textured model, POST /v2/text-to-3d {mode: refine, preview_task_id, enable_pbr}. Image flow: POST /v1/image-to-3d {image_url,
// should_texture, enable_pbr, ...} in one task. Both answer {result: <task id>}; GET .../{id} gives status PENDING | IN_PROGRESS |
// SUCCEEDED | FAILED | CANCELED, progress, model_urls.glb, task_error.message.
// Text-to-3d fields verified against docs.meshy.ai/en/api/text-to-3d on 2026-10-20 (ai_model: meshy-7.1, latest, meshy-6;
// target_polycount 100-300000 only applies when should_remesh is true). The image-to-3d request was not re-fetched; it uses the
// same field names and accepts a public URL or base64 data URI in image_url.
import { http, baseUrl, b64, ToolError } from "../lib/util.mjs";

export const DEFAULT_BASE = "https://api.meshy.ai/openapi";
const B = () => baseUrl("meshy", DEFAULT_BASE);
const H = (key) => ({ authorization: `Bearer ${key}`, "content-type": "application/json" });
const post = async (key, path, body) => {
  const r = await http(`${B()}${path}`, { method: "POST", headers: H(key), body: JSON.stringify(body) });
  if (!r?.result) throw new ToolError(`meshy ${path} returned no task id`);
  return r.result;
};

// o: {model, prompt, image:{buf,mime,filename}, face_limit, texture, pbr}. pbr implies texture.
export async function create(key, o) {
  const texture = !!(o.texture || o.pbr);
  const remesh = o.face_limit ? { should_remesh: true, target_polycount: o.face_limit } : {};
  if (o.image) {
    const id = await post(key, "/v1/image-to-3d", { image_url: `data:${o.image.mime};base64,${b64(o.image.buf)}`, ai_model: o.model, should_texture: texture, enable_pbr: !!o.pbr, ...remesh });
    return `image:${id}`;
  }
  return `text:${await post(key, "/v2/text-to-3d", { mode: "preview", prompt: o.prompt, ai_model: o.model, ...remesh })}`;
}
// Starts the refine (texture) stage once the preview has SUCCEEDED. Returns {task_id}.
export async function next(key, job, st, nextName) {
  if (nextName !== "refine") throw new ToolError(`unknown meshy stage ${nextName}`);
  const preview = job.stages[0].task_id;
  if (!preview.startsWith("text:")) throw new ToolError("meshy refine needs a text-to-3d preview task");
  return { task_id: `text:${await post(key, "/v2/text-to-3d", { mode: "refine", preview_task_id: preview.slice(5), enable_pbr: !!job.opts?.pbr })}` };
}
export async function poll(key, taskId) {
  const [kind, id] = String(taskId).split(":");
  if (!id) throw new ToolError(`meshy task_id must look like "text:<id>" or "image:<id>"`);
  const d = await http(`${B()}/${kind === "image" ? "v1/image-to-3d" : "v2/text-to-3d"}/${encodeURIComponent(id)}`, { headers: H(key) });
  if (d.status === "SUCCEEDED") {
    if (!d.model_urls?.glb) throw new ToolError("meshy task succeeded but returned no model_urls.glb");
    return { state: "done", url: d.model_urls.glb, progress: 100 };
  }
  if (d.status === "FAILED" || d.status === "CANCELED") return { state: "failed", error: `meshy task ${d.status}: ${d.task_error?.message || ""}` };
  return { state: "pending", progress: d.progress ?? null };
}
