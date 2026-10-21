export const meta = {
  name: 'asset-batch',
  description: 'Produce a batch of visual assets through a per-asset pipeline: style-locked prompt, studio-gateway generation, post-process, engine import, comparative critique, manifest update. Respects the budget and logs skipped items.',
  whenToUse: 'To generate sprites, icons, backgrounds or UI art in bulk after the style bible exists. Args: {kind?, ids?, count?}; ids are asset ids or names from the asset list, kind filters by manifest kind.',
  phases: [
    { title: 'Plan', detail: 'Resolve the asset list, budget and style lock' },
    { title: 'Produce', detail: 'Per asset: prompt, generate, post-process, import, critique' },
    { title: 'Summary', detail: 'Approved, rejected and skipped assets with spend' },
  ],
}

const a = args || {}
const CANDIDATES = 3 // image_generate n per asset: every candidate is a billed image, so an asset costs its unit price x CANDIDATES
const SKILL = 'Invoke the arcosian:asset-production skill (Skill tool) first: it gives the style-lock procedure, studio-gateway tool usage, image_post.py command lines and import steps. Use the studio-gateway MCP tools (image_generate, image_postprocess, manifest_update, budget_status, licence_check).'
const skipped = []

phase('Plan')
const plan = await agent(
  `${SKILL}\nResolve the assets to produce: kind=${a.kind || 'any'}, ids=${JSON.stringify(a.ids || [])}, count=${a.count || 'all pending'}. Take them from the design contract, feature list and existing manifest (skip already approved ones). Call budget_status. For each asset estimate the cost of ONE image as unit_cost_usd (the estimated_usd_if_real of an image_generate dry_run at the asset's size, or the pricing.json list price). The batch requests ${CANDIDATES} candidates per asset, so an asset costs unit_cost_usd x ${CANDIDATES}; est_cost_usd is the total for all assets including that factor. Read the style bible (art-director) and return the style-lock text and reference image paths.`,
  { label: 'plan', phase: 'Plan', agentType: 'arcosian:art-director', schema: { type: 'object', properties: { style_lock: { type: 'string' }, references: { type: 'array', items: { type: 'string' } }, remaining_usd: { type: 'number' }, est_cost_usd: { type: 'number' }, assets: { type: 'array', items: { type: 'object', properties: { id: { type: 'string' }, kind: { type: 'string' }, brief: { type: 'string' }, size: { type: 'string' }, transparent: { type: 'boolean' }, target_path: { type: 'string' }, unit_cost_usd: { type: 'number' } }, required: ['id', 'kind', 'brief'] } } }, required: ['style_lock', 'assets', 'remaining_usd'] } },
)
if (!plan || !plan.assets.length) { log('Nothing to produce or planning failed'); return { error: 'no assets', plan } }
const wanted = a.count ? plan.assets.slice(0, a.count) : plan.assets
const remaining = plan.remaining_usd
// Commit budget in order: parallel agents each see the same remaining balance, so ration it here, counting every candidate.
const items = []
let committed = 0
for (const it of wanted) {
  const cost = (it.unit_cost_usd || 0) * CANDIDATES
  if (cost > 0 && committed + cost > remaining + 1e-9) {
    skipped.push({ id: it.id, reason: `budget: ${CANDIDATES} candidates cost about ${cost.toFixed(2)} USD, ${Math.max(remaining - committed, 0).toFixed(2)} USD left after the assets before it` })
    continue
  }
  committed += cost
  items.push(it)
}
if (!items.length) { skipped.forEach(s => log(`SKIPPED ${s.id}: ${s.reason}`)); return { error: 'no asset fits the remaining budget', skipped, plan } }
log(`${items.length} of ${wanted.length} assets x ${CANDIDATES} candidates: estimated ${committed.toFixed(2)} USD of ${remaining} USD remaining (planner total ${plan.est_cost_usd})`)

phase('Produce')
const results = await pipeline(items,
  (asset) => agent(
    `${SKILL}\nCall budget_status first. This asset needs ${CANDIDATES} candidates, so it costs ${CANDIDATES} x the price of one image${asset.unit_cost_usd ? ` (planned at ${(asset.unit_cost_usd * CANDIDATES).toFixed(2)} USD)` : ''}. If the remaining budget cannot cover all ${CANDIDATES} candidates (estimate before generating) return skipped=true with the reason and generate nothing.\nAsset ${asset.id} (${asset.kind}): ${asset.brief}\nStyle lock (prepend verbatim): ${plan.style_lock}\nReferences: ${JSON.stringify(plan.references)}\nWrite the final prompt and negative prompt, then call image_generate with n=${CANDIDATES} candidates (size ${asset.size || 'per skill'}, transparent=${!!asset.transparent}, style_ref set). Return candidate asset ids and paths.`,
    { label: `generate ${asset.id}`, phase: 'Produce', agentType: 'arcosian:art-director', schema: { type: 'object', properties: { skipped: { type: 'boolean' }, reason: { type: 'string' }, prompt: { type: 'string' }, candidates: { type: 'array', items: { type: 'object', properties: { asset_id: { type: 'string' }, path: { type: 'string' } }, required: ['asset_id', 'path'] } }, cost_usd: { type: 'number' } }, required: ['skipped'] } },
  ),
  (gen, asset) => {
    if (!gen || gen.skipped || !gen.candidates || !gen.candidates.length) { skipped.push({ id: asset.id, reason: gen ? gen.reason || 'no candidates' : 'generation failed' }); return null }
    return agent(
      `${SKILL}\nPost-process and import candidates for ${asset.id}: ${JSON.stringify(gen.candidates)}. Run image_post.py check on each, background removal/resize/pixelate as the skill and style lock require, then import the keepers into the engine project at ${asset.target_path || 'the path from config assets_dir'} (placeholders stay marked placeholder). Return the processed paths.`,
      { label: `post+import ${asset.id}`, phase: 'Produce', agentType: 'arcosian:technical-artist', schema: { type: 'object', properties: { processed: { type: 'array', items: { type: 'object', properties: { asset_id: { type: 'string' }, path: { type: 'string' }, check_ok: { type: 'boolean' } }, required: ['asset_id', 'path'] } } }, required: ['processed'] } },
    )
  },
  (post, asset) => !post ? null : agent(
    `Comparatively critique the candidates for ${asset.id} against the style lock and brief: ${JSON.stringify(post.processed)}. Open the images side by side with the reference images (${JSON.stringify(plan.references)}). Pick at most one winner or reject all. Then call manifest_update for the winner (status "approved", approved_by "art-director") and for the others (status "rejected", with a note), and licence_check the winner. Brief: ${asset.brief}\nStyle lock: ${plan.style_lock}`,
    { label: `critique ${asset.id}`, phase: 'Produce', agentType: 'arcosian:art-director', schema: { type: 'object', properties: { winner: { type: 'string' }, rejected_all: { type: 'boolean' }, reasons: { type: 'string' }, licence_ok: { type: 'boolean' } }, required: ['rejected_all', 'reasons'] } },
  ),
)

phase('Summary')
const done = items.map((it, i) => ({ id: it.id, result: results[i] }))
const approved = done.filter(d => d.result && d.result.winner && !d.result.rejected_all).map(d => d.id)
const rejected = done.filter(d => d.result && (d.result.rejected_all || !d.result.winner)).map(d => d.id)
const failed = done.filter(d => !d.result && !skipped.some(s => s.id === d.id)).map(d => d.id)
skipped.forEach(s => log(`SKIPPED ${s.id}: ${s.reason}`))
const spend = await agent(
  `Call budget_status and return remaining and spent USD. Report only numbers.`,
  { label: 'budget', phase: 'Summary', model: 'sonnet', schema: { type: 'object', properties: { spent_usd: { type: 'number' }, remaining_usd: { type: 'number' } }, required: ['remaining_usd'] } },
)
return { approved, rejected, skipped, failed, budget: spend }
