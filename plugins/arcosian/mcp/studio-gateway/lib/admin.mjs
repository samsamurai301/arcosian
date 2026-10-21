// Non-generating tools: status, manifest, licence, budget, knowledge base.
import path from "node:path";
import { fileURLToPath } from "node:url";
import { ToolError } from "./util.mjs";
import { configured } from "../providers/index.mjs";
import { budgetState, budgetSummary, loadManifest, updateManifest } from "./project.mjs";
import { checkAsset } from "./licences.mjs";
import { kbRoot, search } from "./kb.mjs";
import { pricingSummary } from "./pricing.mjs";
import { listJobs } from "./jobs.mjs";

const SERVER_DIR = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

export async function gsStatus({ env, p, forceMock }) {
  return {
    ok: true, project_root: p.root, gamestudio_found: p.found, mock_forced: forceMock,
    providers: configured(), budget: budgetSummary(p, env), manifest_assets: loadManifest(p).assets.length,
    pricing: pricingSummary(),
    running_3d_jobs: listJobs(p).filter((j) => j.status === "running").map((j) => ({ task_id: j.id, provider: j.provider, stage: j.stages[j.stage]?.name })),
    plugin_root: env.GS_PLUGIN_ROOT || null, kb_root: kbRoot(env, SERVER_DIR),
    note: "providers without a key fall back to placeholder (mock) output",
  };
}
export async function manifestQuery({ a, p }) {
  const t = a.text ? a.text.toLowerCase() : null;
  const hits = loadManifest(p).assets.filter((x) =>
    (!a.kind || x.kind === a.kind) && (!a.status || x.status === a.status) && (!a.provider || x.provider === a.provider) &&
    (!t || [x.id, x.path, x.prompt, x.notes].some((s) => String(s || "").toLowerCase().includes(t))));
  const limit = a.limit || 20;
  return { ok: true, total: hits.length, returned: Math.min(limit, hits.length), assets: hits.slice(-limit) };
}
export async function manifestUpdate({ a, p }) {
  const asset = await updateManifest(p, (man) => {
    const x = man.assets.find((s) => s.id === a.asset_id);
    if (!x) throw new ToolError(`asset not found: ${a.asset_id}`);
    for (const k of ["status", "approved_by", "notes"]) if (a[k] !== undefined) x[k] = a[k];
    if (a.licence) x.licence = { ...x.licence, ...a.licence };
    return x;
  });
  return { ok: true, asset };
}
export async function licenceCheck({ a, env, p }) {
  const cfg = p.config(), all = loadManifest(p).assets;
  const assets = a.asset_id ? all.filter((x) => x.id === a.asset_id) : all;
  if (a.asset_id && !assets.length) throw new ToolError(`asset not found: ${a.asset_id}`);
  const flags = assets.flatMap((x) => checkAsset(x, cfg));
  const count = (s) => flags.filter((f) => f.severity === s).length;
  return { ok: true, checked: assets.length, passed: count("error") === 0, errors: count("error"), warnings: count("warn"), revenue: cfg.revenue || null, flags };
}
export async function budgetStatus({ env, p }) {
  const s = budgetState(p, env);
  return { ok: true, ...budgetSummary(p, env), entries: (s.b.ledger || []).length, recent: (s.b.ledger || []).slice(-5) };
}
export async function kbSearch({ a, env }) {
  const root = kbRoot(env, SERVER_DIR);
  if (!root) throw new ToolError("no skills directory found (set GS_PLUGIN_ROOT)");
  const results = search(root, a.query, { skill: a.skill, limit: a.limit || 5 });
  return { ok: true, query: a.query, count: results.length, results };
}
