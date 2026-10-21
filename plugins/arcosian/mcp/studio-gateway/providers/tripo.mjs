// Tripo 3D API v3 (https://openapi.tripo3d.com/v3; Bearer auth), per the Tripo quick start and the v2 -> v3 migration guide
// (verified 2026-10-20). Envelope {code: 0, status, data}. Stages used by the gateway:
//   model     POST /generation/text-to-model {prompt, model, texture, pbr, face_limit}
//             POST /generation/image-to-model {input: <file_token>, ...} after POST /files (multipart "file" -> data.file_token)
//   rig_check POST /animations/rig-check {input: <model task id>}  (free; output.riggable, output.rig_type)
//   rig       POST /animations/rig {input: <model task id>, out_format, spec, rig_type}
// Tasks are read with GET /tasks/{id}: data.status queued | running | success | failed | cancelled, data.progress,
// data.output.model_url. Signed model URLs are short lived (the quick start says 5 minutes): download straight away.
// P1 models take face_limit 48-20000 and must not receive quad, smart_low_poly, generate_parts or geometry_quality (never sent).
import { http, baseUrl, form, ToolError } from "../lib/util.mjs";

export const DEFAULT_BASE = "https://openapi.tripo3d.com/v3";
const B = () => baseUrl("tripo", DEFAULT_BASE);
const H = (key) => ({ authorization: `Bearer ${key}` });
const unwrap = (r) => {
  if (r && r.code !== undefined && r.code !== 0) throw new ToolError(`tripo error ${r.code}: ${r.message || ""}${r.suggestion ? ` (${r.suggestion})` : ""}`);
  return r?.data;
};
const post = async (key, path, body) => {
  const d = unwrap(await http(`${B()}${path}`, { method: "POST", headers: { ...H(key), "content-type": "application/json" }, body: JSON.stringify(body) }));
  if (!d?.task_id) throw new ToolError(`tripo ${path} returned no task_id`);
  return d.task_id;
};

// o: {model, prompt, image:{buf,mime,filename}, face_limit, texture, pbr}. pbr implies texture on Tripo.
export async function create(key, o) {
  const common = { model: o.model, texture: !!(o.texture || o.pbr), pbr: !!o.pbr };
  if (o.face_limit) common.face_limit = o.face_limit;
  if (!o.image) return post(key, "/generation/text-to-model", { prompt: o.prompt, ...common });
  const up = unwrap(await http(`${B()}/files`, { method: "POST", headers: H(key), body: form({}, [{ name: "file", ...o.image }]) }));
  if (!up?.file_token) throw new ToolError("tripo upload returned no file_token");
  return post(key, "/generation/image-to-model", { input: up.file_token, ...common });
}
// Starts the stage after the one that just finished (st = poll result of the finished stage). Returns {task_id} or {skip: reason}.
export async function next(key, job, st, nextName) {
  const modelTask = job.stages[0].task_id;
  if (nextName === "rig_check") return { task_id: await post(key, "/animations/rig-check", { input: modelTask }) };
  if (nextName === "rig") {
    if (st.riggable === false) return { skip: "tripo rig-check says the model is not riggable: rig skipped (not billed), returning the unrigged model" };
    const body = { input: modelTask, out_format: "glb", spec: "mixamo" };
    if (st.rig_type) body.rig_type = st.rig_type;
    return { task_id: await post(key, "/animations/rig", body) };
  }
  throw new ToolError(`unknown tripo stage ${nextName}`);
}
// stage: "model" | "rig_check" | "rig" (rig-check output has no model). Unknown statuses count as failed, as the guide advises.
export async function poll(key, taskId, stage) {
  const d = unwrap(await http(`${B()}/tasks/${encodeURIComponent(taskId)}`, { headers: H(key) }));
  if (d?.status === "success") {
    const url = stage === "rig_check" ? null : d.output?.model_url;
    if (stage !== "rig_check" && !url) throw new ToolError("tripo task succeeded but returned no output.model_url");
    return { state: "done", url, progress: 100, riggable: d.output?.riggable, rig_type: d.output?.rig_type };
  }
  if (d?.status === "queued" || d?.status === "running") return { state: "pending", progress: d.progress ?? null };
  return { state: "failed", error: `tripo task ${d?.status || "unknown"}${d?.error_code ? ` (error ${d.error_code}: ${d.error_message || ""})` : ""}` };
}
