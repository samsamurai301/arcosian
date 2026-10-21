// Model ids and cost estimates from pricing.json; GS_MODEL_<PROVIDER>_<KIND> overrides the model id.
import { fileURLToPath } from "node:url";
import { readJson, round6 } from "./util.mjs";

const DATA = readJson(fileURLToPath(new URL("../pricing.json", import.meta.url)), { models: {} });

export function entry(provider, kind) {
  const e = DATA.models[`${provider}.${kind}`];
  if (!e) return null;
  const ov = process.env[`GS_MODEL_${provider.toUpperCase()}_${kind.toUpperCase()}`];
  return { ...e, default_model: e.model, model: ov || e.model, model_overridden: !!ov };
}

// True when the price of this model id is listed (the default model or an entry in "models").
export function priceKnown(provider, kind, model) {
  const e = entry(provider, kind);
  return !!e && (!model || model === e.default_model || e.models?.[model] !== undefined);
}

// Price of one unit: a model listed in "models" wins (number, or tier map), else the default model's tiers / usd.
function unitUsd(e, q) {
  let table = e.tiers, base = e.usd;
  const alt = q.model ? e.models?.[q.model] : undefined;
  if (alt !== undefined) {
    if (typeof alt === "number") { table = undefined; base = alt; } else { table = alt; base = Object.values(alt)[0]; }
  }
  let p = table ? (table[q.tier] ?? table[e.default_tier] ?? base) : base;
  if (q.wide && e.wide_mult) p *= e.wide_mult;
  return p;
}

// q: {n, sec, chars, mp, image, texture, rig, model, tier, wide, refs}
//   n images/songs, sec audio seconds, chars text length, mp megapixels (1 MP = 1024x1024) per image, model effective model id,
//   tier size ("1K") or quality ("medium") tier, wide non-square size, refs number of input images (edits).
export function estimate(provider, kind, q = {}) {
  const e = entry(provider, kind);
  if (!e) return 0;
  const n = q.n ?? 1;
  const qty = { image: n, song: n, call: 1, task: 1, megapixel: n * Math.max(1, Math.ceil(q.mp || 1)), minute: (q.sec || 0) / 60, "1k_chars": (q.chars || 0) / 1000 }[e.unit] ?? 1;
  let usd = (q.image && e.image_usd ? e.image_usd : unitUsd(e, q)) * qty;
  if (q.texture) usd += e.texture_usd || 0;
  if (q.rig) usd += e.rig_usd || 0;
  if (q.refs && e.ref_usd) usd += q.refs * e.ref_usd;
  return round6(usd);
}

// {as_of, total, verified, unverified: ["openai.image", ...]} for gs_status.
export function pricingSummary() {
  const keys = Object.keys(DATA.models);
  return { as_of: DATA.as_of || null, total: keys.length, verified: keys.filter((k) => DATA.models[k].verified === true).length, unverified: keys.filter((k) => DATA.models[k].verified !== true) };
}
