// Licence defaults per provider and rule checks against .gamestudio/config.json revenue.
const ELEVEN_MUSIC_PER_GAME = 500000, ELEVEN_MUSIC_PER_YEAR = 1000000; // Indie Game self-serve limits (research notes, Oct 2026 - verify)
const STABILITY_COMMUNITY_LIMIT = 1000000;

const TERMS = {
  gemini: { terms: "Gemini API terms; output usable commercially (verify). Free-tier content may be used to improve Google products; SynthID watermark.", restrictions: ["free tier: input/output may be used to improve Google products"] },
  openai: { terms: "OpenAI terms: output assigned to the user (verify current terms)", restrictions: [] },
  recraft: { terms: "Recraft paid plan: user owns outputs with commercial rights", restrictions: ["free plan outputs are owned by Recraft, public and non-commercial"] },
  fal: { terms: "fal.ai hosted model; licence depends on the model", restrictions: ["check the licence of the specific model"] },
  stability: { terms: "Stability AI API terms (verify)", restrictions: [] },
  tripo: { terms: "Tripo API terms (verify)", restrictions: ["free plan assets may be public / attribution-required: verify"] },
  meshy: { terms: "Meshy API terms (verify)", restrictions: ["free plan assets may require CC BY attribution: verify"] },
  elevenlabs: { terms: "ElevenLabs terms; commercial use on paid plans (free tier conflicting in sources: verify)", restrictions: ["free tier: attribution and commercial rights unclear"] },
};
const NONCOMM = /non-?commercial|\bcc[- ]by-nc\b|\bflux\/dev\b|research only/i;

export function licenceFor(provider, kind, model, env = process.env) {
  if (provider === "mock") return { terms: "placeholder generated locally", plan_tier: "n/a", commercial_ok: true, attribution: null, restrictions: ["placeholder: replace before ship"] };
  const t = TERMS[provider === "lyria" ? "gemini" : provider] || { terms: "unknown provider", restrictions: [] };
  const restrictions = [...t.restrictions];
  if (provider === "elevenlabs" && kind === "music") restrictions.push(`Indie Game self-serve rights only below $${ELEVEN_MUSIC_PER_GAME} per game and $${ELEVEN_MUSIC_PER_YEAR} per year; above that Enterprise Music is required`);
  if (provider === "fal" && NONCOMM.test(model || "")) restrictions.push("model uses a non-commercial licence");
  return {
    terms: t.terms,
    plan_tier: env[`GS_PLAN_${provider.toUpperCase()}`] || "unknown",
    commercial_ok: !(provider === "fal" && NONCOMM.test(model || "")),
    attribution: null,
    restrictions,
  };
}

// -> [{severity: "error"|"warn"|"info", code, message}]
export function checkAsset(a, cfg = {}) {
  const f = [], add = (severity, code, message) => f.push({ asset_id: a.id, severity, code, message });
  const lic = a.licence, rev = cfg.revenue || {};
  if (a.placeholder) add("warn", "placeholder", "placeholder asset: replace with a real asset before shipping");
  if (!a.placeholder && (!a.provider || !a.model || !a.sha256 || !a.prompt)) add("warn", "missing_provenance", "provider, model, prompt or sha256 missing from the manifest entry");
  if (!lic || !lic.terms) { add("error", "missing_licence", "no licence terms recorded"); return f; }
  if (lic.commercial_ok === false || (lic.restrictions || []).some((r) => NONCOMM.test(r)) || NONCOMM.test(lic.terms))
    add("error", "non_commercial", `non-commercial terms (${lic.terms}); not shippable in a commercial game`);
  if (String(lic.plan_tier).toLowerCase() === "free" && !a.placeholder) {
    const sev = a.provider === "recraft" ? "error" : "warn";
    add(sev, "free_tier", `${a.provider} free-tier output: ownership or commercial rights may not transfer to you`);
  }
  if (a.provider === "elevenlabs" && a.kind === "music" && !a.placeholder) {
    const game = rev.lifetime_gross_usd ?? 0, year = rev.developer_annual_games_revenue_usd ?? 0;
    if (game > ELEVEN_MUSIC_PER_GAME || year > ELEVEN_MUSIC_PER_YEAR) add("error", "revenue_threshold", `ElevenLabs Music Indie Game rights exceeded (game $${game} of $${ELEVEN_MUSIC_PER_GAME}, annual $${year} of $${ELEVEN_MUSIC_PER_YEAR}); Enterprise Music licence required`);
    else if (game > 0.8 * ELEVEN_MUSIC_PER_GAME || year > 0.8 * ELEVEN_MUSIC_PER_YEAR) add("warn", "revenue_threshold_near", "within 20% of the ElevenLabs Music Indie Game revenue limits");
  }
  if (/stability.*community/i.test(lic.terms) && (rev.developer_annual_games_revenue_usd ?? 0) > STABILITY_COMMUNITY_LIMIT)
    add("error", "revenue_threshold", "Stability Community Licence is limited to under $1M annual revenue; Enterprise licence required");
  if (lic.attribution) add("info", "attribution_required", `attribution required: ${lic.attribution}`);
  const allow = (cfg.licence_allowlist || []).map((s) => String(s).toLowerCase());
  if (allow.length && !allow.some((s) => lic.terms.toLowerCase().includes(s) || String(a.provider).toLowerCase() === s))
    add("warn", "not_in_allowlist", "licence terms and provider are not on config.licence_allowlist");
  return f;
}
