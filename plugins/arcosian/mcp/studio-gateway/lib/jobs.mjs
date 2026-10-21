// Pipeline state for multi-stage 3D jobs (Tripo model -> rig-check -> rig; Meshy preview -> refine), kept in the small file
// <project>/.gamestudio/jobs.json so that model3d_status can continue the remaining stages after model3d_generate handed
// the task back. A job is addressed by its id (the first stage's provider task id) or by any later stage's task id.
//
// job = {id, provider, model, prompt, opts:{face_limit, texture, pbr, rig, image}, out_dir, id_prefix,
//        stages:[{name, usd, task_id, state: pending|running|done|failed|skipped, progress, error?}], stage (running index),
//        est_usd, billed_usd, last_model:{stage, task_id}|null, chain_done, notes[], status: running|done|failed, error?,
//        asset_ids[], files[], created_at, updated_at}
import path from "node:path";
import { readJson, writeJson } from "./util.mjs";
import { locked } from "./project.mjs";

const KEEP_FINISHED = 50;
export const jobsPath = (p) => path.join(p.gs, "jobs.json");
const load = (p) => { const j = readJson(jobsPath(p), null); return j && typeof j.jobs === "object" && j.jobs ? j : { schema_version: "1.0", jobs: {} }; };

export const listJobs = (p) => Object.values(load(p).jobs);
export const findJob = (p, taskId) => listJobs(p).find((j) => j.id === taskId || j.stages.some((s) => s.task_id === taskId)) || null;

// Write one job (read-modify-write under the project lock); prunes old finished jobs so the file stays small.
export function saveJob(p, job) {
  return locked(() => {
    const db = load(p);
    job.updated_at = new Date().toISOString();
    db.jobs[job.id] = job;
    const finished = Object.values(db.jobs).filter((j) => j.status !== "running").sort((a, b) => String(b.updated_at).localeCompare(String(a.updated_at)));
    for (const j of finished.slice(KEEP_FINISHED)) delete db.jobs[j.id];
    writeJson(jobsPath(p), db);
    return job;
  });
}

// Serialise work on one job inside this process: two concurrent model3d_status calls must not start the same next stage twice
// (that would bill it twice). fn runs after any earlier call for the same job id has settled.
const tails = new Map();
export function withJob(id, fn) {
  const run = (tails.get(id) || Promise.resolve()).catch(() => {}).then(fn);
  const tail = run.catch(() => {});
  tails.set(id, tail);
  tail.then(() => { if (tails.get(id) === tail) tails.delete(id); });
  return run;
}
