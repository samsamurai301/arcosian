// Generation tool handlers. Each handler gets ctx = {a: args, env, p: project, cfg, forceMock}.
// Flow: choose provider -> mock or (budget guard -> provider call) -> write files + manifest + ledger.
// 3D generation is a staged pipeline kept in .gamestudio/jobs.json (see lib/jobs.mjs): model3d_generate and model3d_status
// both drive it, so a task handed back with a task_id continues through rig or refine until the final file is downloaded.
import fs from "node:fs";
import path from "node:path";
import { ToolError, b64, extMime, download, sleep, pollMs, num, round6, redact } from "./util.mjs";
import { makePng, makeWav, makeGlb, makeSvg, parseSize, pngSize, seedOf } from "./media.mjs";
import { entry, estimate, priceKnown } from "./pricing.mjs";
import { licenceFor } from "./licences.mjs";
import { commitAssets, budgetSummary, guardBudget, recordLedger, loadManifest } from "./project.mjs";
import { MODULES, ENV_KEY, keyFor } from "../providers/index.mjs";
import { findJob, saveJob, withJob } from "./jobs.mjs";

const pkey = (provider) => (provider === "lyria" ? "gemini" : provider); // pricing / model-env namespace

function choose(ctx, requested, slot, candidates) {
  let provider = requested && requested !== "auto" ? requested : null;
  if (!provider) {
    const pref = ctx.cfg.providers?.[slot];
    provider = (candidates.includes(pref) && keyFor(pref) && pref) || candidates.find((c) => keyFor(c)) || (candidates.includes(pref) ? pref : candidates[0]);
  }
  if (!candidates.includes(provider)) throw new ToolError(`provider "${provider}" is not supported here; use one of: ${candidates.join(", ")}`);
  const why = ctx.forceMock ? (ctx.a.dry_run ? "dry_run" : "GS_MOCK=1") : !keyFor(provider) ? `${ENV_KEY[provider]} not configured` : null;
  return { provider, mock: !!why, mockWhy: why };
}
function readInput(ctx, f) {
  const abs = ctx.p.resolve(f);
  if (!fs.existsSync(abs) || !fs.statSync(abs).isFile()) throw new ToolError(`file not found: ${f}`);
  return { abs, rel: ctx.p.rel(abs), buf: fs.readFileSync(abs), mime: extMime(abs), filename: path.basename(abs) };
}
const IMAGE_MIME = /^image\/(png|jpeg|webp)$/;
function needImages(provider, files) {
  for (const f of files) if (!IMAGE_MIME.test(f.mime)) throw new ToolError(`${provider} accepts png, jpeg or webp input images; got ${f.rel}`);
}

// Nearest aspect ratio (log distance) from a provider's list.
function closest(w, h, options) {
  let best = options[0], bd = Infinity;
  for (const o of options) { const [x, y] = o.split(":").map(Number), d = Math.abs(Math.log(x / y / (w / h))); if (d < bd) { bd = d; best = o; } }
  return best;
}
const GEMINI_RATIOS = ["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"];
const RECRAFT_RATIOS = ["1:1", "2:1", "1:2", "3:2", "2:3", "4:3", "3:4", "5:4", "4:5", "6:10", "14:10", "10:14", "16:9", "9:16"];
// Recraft raster models take exact sizes from a per-family list (docs, 2026-10-20); vector models take w:h ratios.
const RECRAFT_SIZES = {
  v4: ["1024x1024", "1536x768", "768x1536", "1280x832", "832x1280", "1216x896", "896x1216", "1152x896", "896x1152", "832x1344", "1280x896", "896x1280", "1344x768", "768x1344"],
  pro: ["2048x2048", "3072x1536", "1536x3072", "2560x1664", "1664x2560", "2432x1792", "1792x2432", "2304x1792", "1792x2304", "1664x2688", "2560x1792", "1792x2560", "2688x1536", "1536x2688"],
  v3: ["1024x1024", "2048x1024", "1024x2048", "1536x1024", "1024x1536", "1365x1024", "1024x1365", "1280x1024", "1024x1280", "1024x1707", "1434x1024", "1024x1434", "1820x1024", "1024x1820"],
};
function recraftSize(model, w, h) {
  const list = /recraftv[23](_|$)/.test(model) ? RECRAFT_SIZES.v3 : /pro/.test(model) ? RECRAFT_SIZES.pro : RECRAFT_SIZES.v4;
  let best = list[0], bd = Infinity;
  for (const s of list) { const [x, y] = s.split("x").map(Number), d = Math.abs(Math.log(x / y / (w / h))); if (d < bd - 1e-9) { bd = d; best = s; } }
  return best;
}
const STABILITY_RATIOS = ["1:1", "2:3", "3:2", "4:5", "5:4", "9:16", "16:9", "9:21", "21:9"];
const geminiTier = (w, h) => (Math.max(w, h) <= 1024 ? "1K" : "2K"); // sizes are clamped to 2048 by parseSize
const oaSize = (w, h) => (w / h > 1.2 ? "1536x1024" : w / h < 0.83 ? "1024x1536" : "1024x1024");
const priceNote = (provider, kind, model) => (priceKnown(pkey(provider), kind, model) ? [] : [`pricing.json has no price for model ${model}: the estimate uses the default model's price`]);

async function done(ctx, s) {
  const files = await commitAssets(ctx.p, ctx.env, { ...s, notes: s.notes.join(" "), licence: licenceFor(s.placeholder ? "mock" : s.provider, s.kind, s.model, ctx.env) });
  const r = { ok: true, tool: s.tool, provider: s.provider, model: s.model, placeholder: !!s.placeholder, cost_usd: s.cost, files, budget: budgetSummary(ctx.p, ctx.env) };
  if (s.placeholder) r.estimated_usd_if_real = s.est;
  if (s.notes.length) r.notes = s.notes;
  return r;
}
const mockNote = (c) => `mock output (${c.mockWhy}): placeholder files, cost 0`;
const modelOf = (ctx, provider, kind) => ctx.a.model || entry(pkey(provider), kind).model;

// ---------- images ----------
export async function imageGenerate(ctx) {
  const a = ctx.a, n = a.n || 1, [w, h] = parseSize(a.size);
  const c = choose(ctx, a.provider, "image", ["gemini", "openai", "recraft", "fal", "stability"]);
  const vector = c.provider === "recraft" && /vector/i.test(a.model || "");
  const refs = [a.style_ref, ...(a.references || [])].filter(Boolean).map((f) => readInput(ctx, f));
  const oaEdit = c.provider === "openai" && refs.length > 0; // references go through the edits endpoint
  const pk = vector ? "image_vector" : oaEdit ? "image_edit" : "image", model = modelOf(ctx, c.provider, pk);
  const quality = a.quality || "medium";
  const est = estimate(c.provider, pk, { n, model, tier: c.provider === "gemini" ? geminiTier(w, h) : quality, wide: c.provider === "openai" && oaSize(w, h) !== "1024x1024", mp: Math.ceil((w * h) / 1048576), refs: oaEdit ? refs.length : 0 });
  const notes = [];
  let outputs, cost = 0;
  if (c.mock) {
    outputs = Array.from({ length: n }, (_, i) => ({ bytes: vector ? makeSvg(seedOf(a.prompt) + i) : makePng(w, h, { seed: seedOf(a.prompt) + i, alpha: !!a.transparent }), ext: vector ? "svg" : "png" }));
    notes.push(mockNote(c));
  } else {
    if (c.provider === "gemini" && refs.length > 14) throw new ToolError("gemini accepts at most 14 reference images");
    if (c.provider === "gemini" || c.provider === "openai") needImages(c.provider, refs);
    guardBudget(ctx.p, ctx.env, est);
    const key = keyFor(c.provider), M = MODULES[c.provider], base = { key, model, prompt: a.prompt, n };
    if (c.provider === "gemini") outputs = await M.image({ ...base, aspect: closest(w, h, GEMINI_RATIOS), tier: geminiTier(w, h), images: refs.map((r) => ({ mime: r.mime, data: b64(r.buf) })) });
    else if (c.provider === "openai") outputs = refs.length ? await M.edit({ ...base, size: oaSize(w, h), quality, images: refs }) : await M.image({ ...base, size: oaSize(w, h), quality, transparent: a.transparent });
    else if (c.provider === "recraft") outputs = await M.image({ ...base, size: vector ? closest(w, h, RECRAFT_RATIOS) : recraftSize(model, w, h), vector, seed: a.seed });
    else if (c.provider === "fal") outputs = await M.image({ ...base, width: w, height: h, seed: a.seed });
    else outputs = await M.image({ ...base, aspect: closest(w, h, STABILITY_RATIOS), seed: a.seed });
    cost = est;
    if (refs.length && !["gemini", "openai"].includes(c.provider)) notes.push(`${c.provider} ignores reference images`);
    if (a.transparent && c.provider !== "openai") notes.push("provider has no native transparency: run image_postprocess op=remove_background");
    if (a.seed != null && ["gemini", "openai"].includes(c.provider)) notes.push(`${c.provider} has no seed parameter: the seed is only recorded`);
    notes.push(...priceNote(c.provider, pk, model));
  }
  return done(ctx, { tool: "image_generate", kind: a.kind, provider: c.provider, model, prompt: a.prompt, outputs, placeholder: c.mock, cost, est, notes,
    outDir: a.out_dir, idPrefix: a.id_prefix, seed: a.seed, references: refs.map((r) => r.rel), style_ref: a.style_ref, params: { size: a.size, n, transparent: !!a.transparent, ...(c.provider === "openai" ? { quality } : {}) } });
}

export async function imageEdit(ctx) {
  const a = ctx.a, n = a.n || 1, src = readInput(ctx, a.source);
  const c = choose(ctx, a.provider, "image", ["gemini", "openai"]);
  const refs = (a.references || []).map((f) => readInput(ctx, f)), dims = pngSize(src.buf), [w, h] = dims || [1024, 1024];
  const model = modelOf(ctx, c.provider, "image_edit"), quality = a.quality || "medium";
  const est = estimate(c.provider, "image_edit", { n, model, tier: c.provider === "gemini" ? geminiTier(w, h) : quality, wide: !!dims && oaSize(w, h) !== "1024x1024", refs: 1 + refs.length });
  const notes = [];
  let outputs, cost = 0;
  if (c.mock) {
    outputs = Array.from({ length: n }, (_, i) => ({ bytes: makePng(Math.min(w, 2048), Math.min(h, 2048), { seed: seedOf(a.prompt) + i }), ext: "png" }));
    notes.push(mockNote(c));
  } else {
    const all = [src, ...refs];
    if (c.provider === "gemini" && all.length > 14) throw new ToolError("gemini accepts at most 14 input images");
    needImages(c.provider, all);
    guardBudget(ctx.p, ctx.env, est);
    const key = keyFor(c.provider);
    outputs = c.provider === "gemini"
      ? await MODULES.gemini.image({ key, model, prompt: a.prompt, n, aspect: dims ? closest(w, h, GEMINI_RATIOS) : undefined, tier: geminiTier(w, h), images: all.map((r) => ({ mime: r.mime, data: b64(r.buf) })) })
      : await MODULES.openai.edit({ key, model, prompt: a.prompt, n, size: dims ? oaSize(w, h) : undefined, quality, images: all });
    cost = est;
    notes.push(...priceNote(c.provider, "image_edit", model));
  }
  const prev = loadManifest(ctx.p).assets.find((x) => x.path === src.rel);
  return done(ctx, { tool: "image_edit", kind: prev?.kind || "other", provider: c.provider, model, prompt: a.prompt, outputs, placeholder: c.mock, cost, est, notes,
    outDir: a.out_dir, idPrefix: a.id_prefix, derived_from: prev ? [prev.id] : [], references: [src.rel, ...refs.map((r) => r.rel)], params: { source: src.rel, n, ...(c.provider === "openai" ? { quality } : {}) } });
}

const OPS = { remove_background: ["removeBackground", "remove_background", "png"], vectorize: ["vectorize", "vectorize", "svg"], upscale: ["crispUpscale", "upscale", "png"] };
const RECRAFT_MIN_SIDE = { remove_background: 256, vectorize: 256, upscale: 32 }; // Recraft input limits: < 20 MB, longest side <= 4096 px
export async function imagePostprocess(ctx) {
  const a = ctx.a, src = readInput(ctx, a.path), [api, pk, ext] = OPS[a.op];
  const c = choose(ctx, a.provider, "image", ["recraft"]);
  const model = entry("recraft", pk).model, est = estimate("recraft", pk), notes = [];
  let outputs, cost = 0;
  if (c.mock) {
    const [w, h] = pngSize(src.buf) || [256, 256], k = a.op === "upscale" ? 2 : 1;
    outputs = [{ bytes: ext === "svg" ? makeSvg(seedOf(src.rel)) : makePng(Math.min(w * k, 2048), Math.min(h * k, 2048), { seed: seedOf(src.rel), alpha: a.op === "remove_background" }), ext }];
    notes.push(mockNote(c));
  } else {
    needImages("recraft", [src]);
    const dims = pngSize(src.buf);
    if (src.buf.length > 20 * 1024 * 1024) throw new ToolError("recraft accepts input images under 20 MB");
    if (dims && (Math.min(...dims) < RECRAFT_MIN_SIDE[a.op] || Math.max(...dims) > 4096))
      throw new ToolError(`recraft ${a.op} needs the shortest side >= ${RECRAFT_MIN_SIDE[a.op]} px and the longest <= 4096 px (got ${dims.join("x")})`);
    guardBudget(ctx.p, ctx.env, est);
    outputs = await MODULES.recraft.postprocess({ key: keyFor("recraft"), op: api, src });
    cost = est;
  }
  const prev = loadManifest(ctx.p).assets.find((x) => x.path === src.rel);
  return done(ctx, { tool: "image_postprocess", kind: prev?.kind || "other", provider: "recraft", model, prompt: `${a.op} of ${src.rel}`, outputs, placeholder: c.mock, cost, est, notes,
    outDir: a.out_dir, derived_from: prev ? [prev.id] : [], references: [src.rel], params: { op: a.op }, idPrefix: a.id_prefix || (prev ? `${prev.id}-${a.op === "upscale" ? "up" : a.op === "vectorize" ? "vec" : "nobg"}` : undefined) });
}

// ---------- 3D: staged pipeline ----------
// Stages and prices (USD, billed when the stage's task is created). Tripo: model -> rig_check (free) -> rig (when rig=true).
// Meshy text: preview -> refine (when texture or pbr); Meshy image: one task (textured when texture or pbr).
function plan3d(provider, o) {
  const e = entry(provider, "model3d"), tex = o.texture || o.pbr, base = o.image && e.image_usd ? e.image_usd : e.usd;
  if (provider === "tripo") {
    const st = [{ name: "model", usd: round6(base + (tex ? e.texture_usd || 0 : 0)) }];
    if (o.rig) st.push({ name: "rig_check", usd: 0 }, { name: "rig", usd: e.rig_usd || 0 });
    return st;
  }
  if (o.image) return [{ name: "model", usd: round6(base + (tex ? e.texture_usd || 0 : 0)) }];
  return [{ name: "preview", usd: round6(base) }, ...(tex ? [{ name: "refine", usd: e.texture_usd || 0 }] : [])];
}
function checkFaceLimit(provider, model, n) {
  if (!n) return;
  if (provider === "tripo" && /^P1/i.test(model) && (n < 48 || n > 20000)) throw new ToolError(`face_limit must be 48-20000 for Tripo P1 (got ${n})`);
  if (provider === "meshy" && (n < 100 || n > 300000)) throw new ToolError(`face_limit must be 100-300000 for Meshy target_polycount (got ${n})`);
}

async function billStage(ctx, job, s, tool) {
  if (s.usd > 0) {
    await recordLedger(ctx.p, ctx.env, { tool, provider: job.provider, model: job.model, cost_usd: s.usd, asset_ids: [], note: `${s.name} task ${s.task_id} created (billed at creation)` });
    job.billed_usd = round6(job.billed_usd + s.usd);
  }
}
// Both vendors refund credits for failed tasks, so a failed stage is credited back in the ledger.
async function refundStage(ctx, job, s, tool) {
  if (s.usd > 0) {
    await recordLedger(ctx.p, ctx.env, { tool, provider: job.provider, model: job.model, cost_usd: -s.usd, asset_ids: [], note: `${s.name} task ${s.task_id} failed: credits refunded by the provider` });
    job.billed_usd = round6(job.billed_usd - s.usd);
  }
}
// Drop the stages after the running one and keep what has been produced so far.
function stopChain(job, note) {
  job.notes.push(redact(note));
  for (const x of job.stages.slice(job.stage + 1)) if (x.state === "pending") x.state = "skipped";
}

// Poll the running stage; when it is done start the next one (billing it) and carry on, until the deadline passes while a task
// is still running ("pending"), a stage fails with nothing to fall back on ("failed"), or the pipeline is complete ("done").
// A failing or unaffordable later stage ends the chain and returns the last model produced (the earlier stages were paid for).
async function advanceJob(ctx, job, deadline, tool) {
  const M = MODULES[job.provider], key = keyFor(job.provider);
  // The chain is over once it has finished, fallen back or stopped: remembered so a retry after a failed download neither
  // re-polls a failed stage (a second refund) nor re-evaluates a refused stage.
  const end = async () => { job.chain_done = true; await saveJob(ctx.p, job); return { state: "done" }; };
  if (job.chain_done) return { state: "done" };
  for (;;) {
    const s = job.stages[job.stage];
    const st = await M.poll(key, s.task_id, s.name);
    s.progress = st.progress ?? null;
    if (st.state === "pending") {
      if (Date.now() >= deadline) { await saveJob(ctx.p, job); return { state: "pending", progress: s.progress }; }
      await sleep(Math.min(pollMs(), Math.max(0, deadline - Date.now())));
      continue;
    }
    if (st.state === "failed") {
      s.state = "failed"; s.error = st.error;
      await refundStage(ctx, job, s, tool);
      if (job.last_model) { stopChain(job, `${s.name} stage failed (${st.error}): returning the ${job.last_model.stage} result`); return end(); }
      job.status = "failed"; job.error = st.error;
      await saveJob(ctx.p, job);
      return { state: "failed", error: st.error };
    }
    s.state = "done";
    if (st.url) job.last_model = { stage: s.name, task_id: s.task_id };
    const nxt = job.stages[job.stage + 1];
    if (!nxt) return end();
    let started;
    try {
      if (nxt.usd > 0) guardBudget(ctx.p, ctx.env, nxt.usd);
      started = await M.next(key, job, st, nxt.name);
    } catch (e) {
      if (e instanceof ToolError && e.data?.refused && job.last_model) { stopChain(job, `${nxt.name} stage not started: ${e.message}; returning the ${job.last_model.stage} result`); return end(); }
      await saveJob(ctx.p, job); // keep progress: the next model3d_status call retries starting the stage
      throw e;
    }
    if (started.skip) { stopChain(job, started.skip); return end(); }
    job.stage++; nxt.task_id = started.task_id; nxt.state = "running"; nxt.progress = null;
    await billStage(ctx, job, nxt, tool);
    await saveJob(ctx.p, job);
  }
}

function pendingResult(ctx, job, r) {
  const s = job.stages[job.stage];
  return { ok: true, pending: true, task_id: job.id, provider: job.provider, stage: s.name, stage_index: job.stage, stages: job.stages.map((x) => x.name), current_task_id: s.task_id,
    progress: r.progress ?? null, estimated_cost_usd: job.est_usd, billed_usd: job.billed_usd, notes: job.notes.length ? job.notes : undefined,
    hint: "call model3d_status with this task_id (same project_dir) to continue the remaining stages and collect the files; do not call model3d_generate again, it would bill again", budget: budgetSummary(ctx.p, ctx.env) };
}

// Download the newest model of the job (the url is re-read right before the download: signed urls expire quickly), record it.
async function collectJob(ctx, job, tool, billedThisCall) {
  const M = MODULES[job.provider], last = job.last_model;
  if (!last) throw new ToolError("3D job finished without a downloadable model", { task_id: job.id });
  const fresh = await M.poll(keyFor(job.provider), last.task_id, last.stage);
  if (fresh.state !== "done" || !fresh.url) throw new ToolError(`could not refresh the model url of ${last.stage} task ${last.task_id}`, { task_id: job.id });
  const bytes = await download(fresh.url).catch((e) => { throw e instanceof ToolError ? new ToolError(`${e.message} (the job is kept: call model3d_status again to retry the download)`, { ...e.data, task_id: job.id }) : e; });
  const r = await done(ctx, { tool, kind: "model", provider: job.provider, model: job.model, prompt: job.prompt, outputs: [{ bytes, ext: "glb" }], placeholder: false,
    cost: billedThisCall, assetCost: job.billed_usd, ledgerCost: 0, ledgerNote: `billed at task creation: $${job.billed_usd} for ${job.stages.filter((x) => x.state === "done").map((x) => x.name).join(" + ")}`,
    est: job.est_usd, notes: [...job.notes], outDir: job.out_dir || undefined, idPrefix: job.id_prefix || undefined,
    references: job.opts.image ? [job.opts.image] : [], params: { face_limit: job.opts.face_limit, texture: job.opts.texture, pbr: job.opts.pbr, rig: job.opts.rig, stages: job.stages.map((x) => ({ name: x.name, state: x.state, task_id: x.task_id })) } });
  job.status = "done"; job.asset_ids = r.files.map((f) => f.asset_id); job.files = r.files;
  await saveJob(ctx.p, job);
  return { ...r, task_id: job.id, job_cost_usd: job.billed_usd, stages: job.stages.map((x) => ({ name: x.name, state: x.state })) };
}
// billedBefore: what the job had billed before this tool call started (0 for model3d_generate, whose first stage is billed
// just before the job runs), so the result's cost_usd is what this call cost.
async function runJob(ctx, job, deadline, tool, billedBefore = job.billed_usd) {
  const r = await advanceJob(ctx, job, deadline, tool);
  if (r.state === "failed") throw new ToolError(r.error || "3D task failed", { task_id: job.id });
  if (r.state === "pending") return pendingResult(ctx, job, r);
  return collectJob(ctx, job, tool, round6(job.billed_usd - billedBefore));
}

export async function model3dGenerate(ctx) {
  const a = ctx.a, provider = a.provider;
  if (!a.prompt && !a.image) throw new ToolError("model3d_generate needs prompt or image");
  const mock = ctx.forceMock || !keyFor(provider), notes = [];
  const rig = !!a.rig && provider === "tripo";
  if (a.rig && !rig) notes.push("rig is only supported for tripo: ignored");
  const model = modelOf(ctx, provider, "model3d");
  checkFaceLimit(provider, model, a.face_limit);
  const opts = { face_limit: a.face_limit, texture: !!a.texture, pbr: !!a.pbr, rig };
  const stages = plan3d(provider, { ...opts, image: !!a.image }), est = round6(stages.reduce((sum, s) => sum + s.usd, 0));
  const prompt = a.prompt || `image: ${a.image}`;
  if (mock) {
    const c = { mockWhy: ctx.forceMock ? (a.dry_run ? "dry_run" : "GS_MOCK=1") : `${ENV_KEY[provider]} not configured` };
    notes.push(mockNote(c));
    return done(ctx, { tool: "model3d_generate", kind: "model", provider, model, prompt, outputs: [{ bytes: makeGlb(), ext: "glb" }], placeholder: true, cost: 0, est, notes, outDir: a.out_dir, idPrefix: a.id_prefix,
      params: { face_limit: a.face_limit, texture: !!a.texture, pbr: !!a.pbr, rig } });
  }
  const image = a.image ? readInput(ctx, a.image) : undefined;
  if (image) needImages(provider, [image]);
  guardBudget(ctx.p, ctx.env, est); // the whole pipeline must fit, so a rig stage is never left unaffordable
  const tid = await MODULES[provider].create(keyFor(provider), { model, prompt: a.prompt, image, ...opts });
  const job = { id: tid, provider, model, prompt, opts: { ...opts, image: image ? image.rel : null }, out_dir: a.out_dir || null, id_prefix: a.id_prefix || null,
    stages: stages.map((s, i) => ({ ...s, task_id: i === 0 ? tid : null, state: i === 0 ? "running" : "pending", progress: null })), stage: 0, chain_done: false,
    est_usd: est, billed_usd: 0, last_model: null, notes, status: "running", asset_ids: [], files: [], created_at: new Date().toISOString() };
  await billStage(ctx, job, job.stages[0], "model3d_generate");
  await saveJob(ctx.p, job);
  const wait = num(a.wait_sec) ?? 240;
  return withJob(job.id, () => runJob(ctx, job, Date.now() + wait * 1000, "model3d_generate", 0));
}

export async function model3dStatus(ctx) {
  const a = ctx.a, provider = a.provider;
  if (String(a.task_id).startsWith("mock-") || (ctx.forceMock && !keyFor(provider))) {
    return done(ctx, { tool: "model3d_status", kind: "model", provider, model: modelOf(ctx, provider, "model3d"), prompt: `task ${a.task_id}`, outputs: [{ bytes: makeGlb(), ext: "glb" }], placeholder: true, cost: 0, est: 0, notes: ["mock task"], outDir: a.out_dir, idPrefix: a.id_prefix });
  }
  if (!keyFor(provider)) throw new ToolError(`${ENV_KEY[provider]} not configured`);
  const known = findJob(ctx.p, a.task_id);
  if (known && known.provider !== provider) throw new ToolError(`task ${a.task_id} belongs to a ${known.provider} job in this project: call model3d_status with provider "${known.provider}"`);
  if (!known) return legacyStatus(ctx);
  return withJob(known.id, async () => {
    const job = findJob(ctx.p, known.id); // re-read inside the lock: a concurrent call may have advanced it
    if (job.status === "done") return { ok: true, tool: "model3d_status", provider, model: job.model, task_id: job.id, already_collected: true, cost_usd: 0, files: job.files, notes: job.notes.length ? job.notes : undefined, budget: budgetSummary(ctx.p, ctx.env) };
    if (job.status === "failed") throw new ToolError(job.error || "3D task failed", { task_id: job.id });
    if (a.out_dir) job.out_dir = a.out_dir;
    if (a.id_prefix) job.id_prefix = a.id_prefix;
    return runJob(ctx, job, Date.now() + (num(a.wait_sec) ?? 0) * 1000, "model3d_status");
  });
}
// A task this project has no pipeline state for (created elsewhere, or in another project directory): one poll, no chaining.
async function legacyStatus(ctx) {
  const a = ctx.a, provider = a.provider, r = await MODULES[provider].poll(keyFor(provider), a.task_id);
  if (r.state === "failed") throw new ToolError(r.error || "3D task failed");
  if (r.state === "pending") return { ok: true, pending: true, task_id: a.task_id, provider, progress: r.progress };
  if (!r.url) throw new ToolError(`task ${a.task_id} finished but has no downloadable model (not a model stage?)`);
  return done(ctx, { tool: "model3d_status", kind: "model", provider, model: modelOf(ctx, provider, "model3d"), prompt: `task ${a.task_id}`, outputs: [{ bytes: await download(r.url), ext: "glb" }], placeholder: false, cost: 0, est: 0,
    notes: ["no pipeline state for this task in this project: later stages (rig, refine) are not continued; already billed when the task was created"], outDir: a.out_dir, idPrefix: a.id_prefix, ledgerNote: "billed at task creation" });
}

// ---------- audio ----------
async function audio(ctx, { tool, kind, c, est, prompt, model, mockBytes, real, params, extraNotes = [] }) {
  const notes = [...extraNotes];
  let outputs, cost = 0;
  if (c.mock) { outputs = [{ bytes: mockBytes(), ext: "wav" }]; notes.push(mockNote(c)); }
  else { guardBudget(ctx.p, ctx.env, est); outputs = await real(); cost = est; }
  return done(ctx, { tool, kind, provider: c.provider, model, prompt, outputs, placeholder: c.mock, cost, est, notes, params, idPrefix: ctx.a.id_prefix, outDir: ctx.a.out_dir });
}
export async function audioMusic(ctx) {
  const a = ctx.a, instrumental = a.instrumental !== false;
  const c = choose(ctx, a.provider, "music", ["elevenlabs", "lyria", "stability"]);
  const pk = c.provider === "stability" ? "audio" : "music";
  const model = modelOf(ctx, c.provider, pk), est = estimate(pkey(c.provider), pk, { sec: a.duration_sec, model });
  const extra = [];
  if (a.duration_sec > 30 && c.mock) extra.push("mock WAV capped at 30 s");
  if (c.provider !== "elevenlabs" && a.composition_plan) extra.push(`composition_plan ignored by ${c.provider} (elevenlabs only)`);
  if (c.provider === "lyria" && /clip/i.test(model) && a.duration_sec !== 30) extra.push("lyria clip models always make 30 s: duration_sec is only a prompt hint");
  if (c.provider === "lyria" && !/clip/i.test(model) && a.duration_sec > 180) extra.push("lyria songs run about two minutes: duration_sec is only a prompt hint");
  if (c.provider === "stability" && a.duration_sec > 380) extra.push("stable audio makes at most 380 s: duration capped");
  if (!c.mock) extra.push(...priceNote(c.provider, pk, model));
  const key = keyFor(c.provider);
  return audio(ctx, { tool: "audio_music", kind: "music", c, est, prompt: a.prompt, model, extraNotes: extra, params: { duration_sec: a.duration_sec, instrumental, composition_plan: a.composition_plan },
    mockBytes: () => makeWav(a.duration_sec, { seed: seedOf(a.prompt) }),
    real: () => c.provider === "elevenlabs" ? MODULES.elevenlabs.music({ key, model, prompt: a.prompt, duration_sec: a.duration_sec, instrumental, composition_plan: a.composition_plan })
      : c.provider === "stability" ? MODULES.stability.audio({ key, model, prompt: a.prompt, duration_sec: Math.min(380, Math.max(1, a.duration_sec)) })
      : MODULES.gemini.music({ key, model, prompt: `${/[.!?]$/.test(a.prompt.trim()) ? a.prompt.trim() : `${a.prompt.trim()}.`}${instrumental ? " Instrumental only, no vocals." : ""} Approximately ${a.duration_sec} seconds.` }) });
}
export async function audioSfx(ctx) {
  const a = ctx.a, c = choose(ctx, a.provider, "sfx", ["elevenlabs", "stability"]);
  const pk = c.provider === "stability" ? "audio" : "sfx", dur = a.duration_sec || 5;
  const model = modelOf(ctx, c.provider, pk), est = estimate(c.provider, pk, { sec: dur, model });
  const extra = [];
  if (c.provider === "stability" && a.loop) extra.push("loop is not supported by stability: ignored");
  if (!c.mock) extra.push(...priceNote(c.provider, pk, model));
  return audio(ctx, { tool: "audio_sfx", kind: "sfx", c, est, prompt: a.prompt, model, extraNotes: extra, params: { duration_sec: a.duration_sec, loop: !!a.loop },
    mockBytes: () => makeWav(a.duration_sec || 1, { seed: seedOf(a.prompt) }),
    real: () => c.provider === "stability" ? MODULES.stability.audio({ key: keyFor("stability"), model, prompt: a.prompt, duration_sec: Math.max(1, dur) })
      : MODULES.elevenlabs.sfx({ key: keyFor("elevenlabs"), model, prompt: a.prompt, duration_sec: a.duration_sec, loop: a.loop }) });
}
export async function audioVoice(ctx) {
  const a = ctx.a, lines = a.lines || [];
  if (!a.text && !lines.length) throw new ToolError("audio_voice needs text or lines");
  const text = a.text || lines.map((l) => l.text).join("\n"), c = choose(ctx, a.provider, "voice", ["elevenlabs", "gemini"]);
  const dlg = c.provider === "elevenlabs" && lines.length > 0, pk = c.provider === "gemini" ? "tts" : dlg ? "dialogue" : "tts";
  const model = modelOf(ctx, c.provider, pk), est = estimate(c.provider, pk, { chars: text.length, model }), key = keyFor(c.provider);
  const dflt = "JBFqnCBsd6RMkjVDRZzb"; // default ElevenLabs premade voice id (George)
  if (!c.mock && c.provider === "elevenlabs" && a.voice_description && !a.voice_id && (a.voice_description.length < 20 || a.voice_description.length > 1000))
    throw new ToolError("voice_description must be 20-1000 characters (ElevenLabs voice design)");
  return audio(ctx, { tool: "audio_voice", kind: "voice", c, est, prompt: text, model, extraNotes: c.mock ? [] : priceNote(c.provider, pk, model), params: { voice_id: a.voice_id, voice_description: a.voice_description, lines: lines.length },
    mockBytes: () => makeWav(Math.min(30, Math.max(0.5, text.length / 15)), { kind: "silence" }),
    real: async () => {
      if (c.provider === "gemini") return MODULES.gemini.tts({ key, model, text, voice: a.voice_id || undefined, lines: lines.length ? lines : undefined });
      const E = MODULES.elevenlabs;
      const voice = a.voice_id || (a.voice_description ? await E.designVoice({ key, description: a.voice_description, name: `gs-${seedOf(a.voice_description).toString(16)}` }) : dflt);
      return dlg ? E.dialogue({ key, model, lines: lines.map((l) => ({ text: l.text, voice_id: l.voice_id || voice })) }) : E.tts({ key, model, text, voice_id: voice });
    } });
}
