// Project root discovery, manifest, budget ledger. All writes are serialized through one in-process lock.
import fs from "node:fs";
import path from "node:path";
import { ToolError, readJson, writeJson, sha256, num, round6 } from "./util.mjs";

let chain = Promise.resolve();
export function locked(fn) {
  const run = chain.then(() => fn());
  chain = run.catch(() => {});
  return run;
}
const isDir = (p) => { try { return fs.statSync(p).isDirectory(); } catch { return false; } };

export function openProject(args, env, cwd = process.cwd()) {
  const start = path.resolve(args.project_dir || env.CLAUDE_PROJECT_DIR || cwd);
  if (!isDir(start)) throw new ToolError(`project_dir does not exist: ${start}`);
  let dir = start, root = null;
  for (;;) {
    if (isDir(path.join(dir, ".gamestudio"))) { root = dir; break; }
    const up = path.dirname(dir);
    if (up === dir) break;
    dir = up;
  }
  const found = !!root;
  root = root || start;
  const gs = path.join(root, ".gamestudio");
  return {
    root, gs, found,
    config: () => readJson(path.join(gs, "config.json"), {}),
    manifestPath: path.join(gs, "assets", "manifest.json"),
    budgetPath: path.join(gs, "budget.json"),
    rel: (abs) => path.relative(root, abs).split(path.sep).join("/"),
    resolve: (p) => path.resolve(root, p),
    generatedDir(outDir) {
      const cfg = this.config();
      const d = path.resolve(root, outDir || cfg.paths?.generated_dir || "assets/generated");
      if (d !== root && !d.startsWith(root + path.sep)) throw new ToolError(`out_dir must be inside the project (${root})`);
      return d;
    },
  };
}

export const loadManifest = (p) => readJson(p.manifestPath, null) || { schema_version: "1.0", assets: [] };

export function budgetState(p, env) {
  const cfg = p.config();
  const b = readJson(p.budgetPath, null) || { schema_version: "1.0", cap_usd: null, spent_usd: 0, ledger: [] };
  const cap = num(cfg.budgets?.asset_usd_cap) ?? num(env.GS_ASSET_BUDGET_USD) ?? num(b.cap_usd);
  const spent = round6(b.spent_usd || 0);
  return { b, cap, spent, remaining: cap === null ? null : round6(cap - spent), per_call_cap: num(cfg.budgets?.per_call_usd_cap) };
}
export function budgetSummary(p, env) {
  const s = budgetState(p, env);
  return { cap_usd: s.cap, spent_usd: s.spent, remaining_usd: s.remaining, per_call_cap_usd: s.per_call_cap };
}
// Refuse before spending: throws ToolError when the estimate exceeds the remaining cap or per-call cap.
export function guardBudget(p, env, estUsd) {
  const s = budgetState(p, env);
  if (s.per_call_cap !== null && estUsd > s.per_call_cap + 1e-9)
    throw new ToolError(`refused: estimated cost $${estUsd} exceeds per_call_usd_cap $${s.per_call_cap}`, { refused: true, estimated_usd: estUsd, per_call_cap_usd: s.per_call_cap });
  if (s.remaining !== null && estUsd > s.remaining + 1e-9)
    throw new ToolError(`refused: estimated cost $${estUsd} exceeds remaining budget $${s.remaining} (cap $${s.cap})`, { refused: true, estimated_usd: estUsd, remaining_usd: s.remaining, cap_usd: s.cap });
}

function nextId(prefix, taken) {
  for (let n = taken.size + 1; ; n++) {
    const id = `${prefix}-${String(n).padStart(3, "0")}`;
    if (!taken.has(id)) return id;
  }
}
// Writes output files, appends manifest entries and one ledger entry. spec fields:
// tool, kind, provider, model, prompt, outputs[{bytes, ext}], placeholder, cost, licence, outDir, idPrefix,
// seed, references, style_ref, params, derived_from, notes; assetCost (manifest cost_usd, default cost) and
// ledgerCost (ledger cost_usd, default cost) differ for 3D jobs, whose stages are ledgered when each task is created
export function commitAssets(p, env, spec) {
  return locked(() => {
    const dir = p.generatedDir(spec.outDir);
    fs.mkdirSync(dir, { recursive: true });
    const man = loadManifest(p);
    const taken = new Set(man.assets.map((a) => a.id));
    const files = [], per = spec.outputs.length ? round6((spec.assetCost ?? spec.cost) / spec.outputs.length) : 0;
    for (const o of spec.outputs) {
      const id = nextId(spec.idPrefix || spec.kind, taken);
      taken.add(id);
      const abs = path.join(dir, `${id}.${o.ext}`);
      fs.writeFileSync(abs, o.bytes);
      const hash = sha256(o.bytes);
      man.assets.push({
        id, path: p.rel(abs), kind: spec.kind, status: "candidate", placeholder: !!spec.placeholder,
        provider: spec.provider, model: spec.model, prompt: spec.prompt || "", negative_prompt: null,
        seed: spec.seed ?? null, references: spec.references || [], params: spec.params || {},
        licence: spec.licence, cost_usd: per, created_at: new Date().toISOString(), approved_by: null,
        style_ref: spec.style_ref || null, sha256: hash, derived_from: spec.derived_from || [], notes: spec.notes || "",
      });
      files.push({ asset_id: id, path: p.rel(abs), sha256: hash, bytes: o.bytes.length });
    }
    if (files.length) writeJson(p.manifestPath, man);
    ledger(p, env, { tool: spec.tool, provider: spec.provider, model: spec.model, cost_usd: spec.ledgerCost ?? spec.cost, asset_ids: files.map((f) => f.asset_id), note: spec.ledgerNote || (spec.placeholder ? "placeholder (mock)" : "") });
    return files;
  });
}
// Append a ledger entry (must run inside the lock or from commitAssets).
export function ledger(p, env, entry) {
  const s = budgetState(p, env);
  s.b.cap_usd = s.cap;
  s.b.spent_usd = round6(s.spent + (entry.cost_usd || 0));
  s.b.ledger = [...(s.b.ledger || []), { ts: new Date().toISOString(), ...entry }];
  writeJson(p.budgetPath, s.b);
}
export const recordLedger = (p, env, entry) => locked(() => ledger(p, env, entry));

export function updateManifest(p, fn) {
  return locked(() => { const man = loadManifest(p); const r = fn(man); writeJson(p.manifestPath, man); return r; });
}
