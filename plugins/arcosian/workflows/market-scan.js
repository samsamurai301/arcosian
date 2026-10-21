export const meta = {
  name: 'market-scan',
  description: 'Research fan-out on a genre or concept with a strict web budget per agent, cross-check of key claims, and a sourced report at .gamestudio/research/market-<slug>.md.',
  whenToUse: 'Before committing to a genre or concept, or to refresh market facts. Args: {topic}.',
  phases: [
    { title: 'Research', detail: 'Parallel researchers: top competitors, genre economics, trends, audience, UA/channels, risks' },
    { title: 'Cross-check', detail: 'Verify the claims that matter against independent sources' },
    { title: 'Report', detail: 'Write the market report with a labelled volatile-facts section' },
  ],
}

const topic = (args && args.topic) || ''
if (!topic) { log('args.topic is required'); return { error: 'args.topic is required' } }
const slug = topic.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '')
const out = `.gamestudio/research/market-${slug}.md`
const SKILL = 'Invoke the arcosian:market-scan skill (Skill tool) first for the method and source priorities.'
const BUDGET = 'WEB BUDGET: at most 6 searches and 6 page fetches. Prefer official or primary sources. Stop when the budget is spent and say what remains unknown. Never invent numbers; every number needs a source URL and an "as of" date.'
const AREAS = [
  'top 8-10 competitors: titles, developers, monetization model, positioning, recent changes',
  'genre economics: typical monetization mix, retention benchmarks, CPI/ARPDAU ranges as reported',
  'trends and recent launches: what is rising or falling, notable soft launches and failures',
  'audience: demographics, motivations, session patterns, platform split',
  'user acquisition and discovery: channels, store featuring patterns, creative hooks, costs as reported',
  'risks: saturation, platform policy, regulation (loot boxes, kids), IP and licence hazards',
]
const schema = {
  type: 'object',
  properties: {
    area: { type: 'string' },
    findings: { type: 'array', items: { type: 'object', properties: { claim: { type: 'string' }, source: { type: 'string' }, as_of: { type: 'string' }, volatile: { type: 'boolean' }, confidence: { type: 'string', enum: ['high', 'medium', 'low'] } }, required: ['claim', 'confidence'] } },
    unknowns: { type: 'array', items: { type: 'string' } },
  },
  required: ['area', 'findings'],
}

phase('Research')
const research = (await parallel(AREAS.map(area => () => agent(
  `${SKILL}\nTopic: ${topic}\nYour area: ${area}.\n${BUDGET}`,
  { label: `research: ${area.split(':')[0]}`, phase: 'Research', agentType: 'arcosian:market-analyst', schema, model: 'sonnet' },
)))).filter(Boolean)
if (!research.length) { log('All researchers failed'); return { error: 'no research output' } }

phase('Cross-check')
const key = []
for (const r of research) for (const f of r.findings) if (f.confidence !== 'high' || /\d/.test(f.claim)) key.push({ area: r.area, ...f })
const batch = key.slice(0, 18)
const checked = await pipeline([0, 1, 2].map(i => batch.filter((_, j) => j % 3 === i)).filter(b => b.length),
  (claims, group, i) => agent(
    `Cross-check these market claims with a different source than the original. ${BUDGET.replace('6 searches and 6 page fetches', '4 searches and 4 page fetches')}\nReturn each claim as confirmed, contradicted or unverified, with the corrected figure if any.\n${JSON.stringify(claims)}`,
    { label: `cross-check ${i + 1}`, phase: 'Cross-check', agentType: 'arcosian:critic', schema: { type: 'object', properties: { results: { type: 'array', items: { type: 'object', properties: { claim: { type: 'string' }, status: { type: 'string', enum: ['confirmed', 'contradicted', 'unverified'] }, correction: { type: 'string' }, source: { type: 'string' } }, required: ['claim', 'status'] } } }, required: ['results'] } },
  ),
)
const results = checked.filter(Boolean).flatMap(c => c.results)
log(`Cross-checked ${results.length} claims; contradicted: ${results.filter(r => r.status === 'contradicted').length}`)

phase('Report')
const report = await agent(
  `${SKILL}\nWrite ${out} for "${topic}": summary and recommendation first, then competitor table, genre economics, trends, audience, UA, risks, white-space opportunities, and positioning advice. Put every price, benchmark and market number in a section "## Volatile facts (as of Oct 2026 - verify before relying)" with a source link each. Drop contradicted claims, label unverified ones, and list open unknowns.\nResearch: ${JSON.stringify(research)}\nCross-check: ${JSON.stringify(results)}`,
  { label: 'report', phase: 'Report', schema: { type: 'object', properties: { path: { type: 'string' }, recommendation: { type: 'string' } }, required: ['path', 'recommendation'] } },
)
return { report, claimsChecked: results.length }
