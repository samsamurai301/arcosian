export const meta = {
  name: 'deconstruct-game',
  description: 'Deconstruct a shipped game through 7 parallel lenses, merge into a deconstruction.schema.json document plus markdown, then fact-check and strip unsupported claims.',
  whenToUse: 'To learn from a comparable or reference game before designing. Args: {game}.',
  phases: [
    { title: 'Lenses', detail: 'Seven parallel analyses: loop, economy, progression, UX, art/audio, psychology, market' },
    { title: 'Merge', detail: 'Merge into deconstruction JSON + markdown under .gamestudio/research/deconstructions/' },
    { title: 'Fact-check', detail: 'Remove or flag claims that are not supported' },
  ],
}

const game = (args && args.game) || ''
if (!game) { log('args.game is required'); return { error: 'args.game is required' } }
const slug = game.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '')
const jsonPath = `.gamestudio/research/deconstructions/${slug}.json`
const mdPath = `.gamestudio/research/deconstructions/${slug}.md`
const SKILL = 'Invoke the arcosian:deconstruct skill (Skill tool) first for the method, the deconstruction schema path and validator command.'

const LENSES = [
  ['core loop and mechanics', 'core_loop, meta_loops, mechanics (mechanic-card-like), innovations'],
  ['economy and monetization', 'economy {currencies, sources, sinks}, monetization {model, top_offers, ads}'],
  ['progression and live-ops', 'progression, liveops, retention_hooks, social'],
  ['UX and onboarding', 'ux_notable, FTUE flow, friction points'],
  ['art and audio', 'art_audio_notable'],
  ['psychology and ethics', 'psychology (principles used), ethical concerns, dark patterns'],
  ['market', 'game {title, developer, year, genre, platforms}, positioning, audience, weaknesses, lessons, borrow_for_us'],
]
const claimSchema = {
  type: 'object',
  properties: {
    lens: { type: 'string' },
    fields: { type: 'string' },
    claims: { type: 'array', items: { type: 'object', properties: { claim: { type: 'string' }, confidence: { type: 'string', enum: ['high', 'medium', 'low'] }, source: { type: 'string' } }, required: ['claim', 'confidence'] } },
  },
  required: ['lens', 'claims'],
}

phase('Lenses')
const lensOut = (await parallel(LENSES.map(([lens, fields]) => () => agent(
  `${SKILL}\nGame: ${game}\nLens: ${lens}. Produce the deconstruction fields for: ${fields}. Use only what you actually know about the game; mark confidence honestly and give a source URL when you have one. Do not invent numbers (prices, revenue, retention). Return the findings as claims plus a "fields" string holding a JSON object with the schema fields above.`,
  { label: `lens: ${lens}`, phase: 'Lenses', schema: claimSchema, model: 'sonnet' },
)))).filter(Boolean)
if (!lensOut.length) { log('All lenses failed'); return { error: 'no lens output' } }

phase('Merge')
const merged = await agent(
  `${SKILL}\nMerge these lens outputs into ONE deconstruction document for "${game}", schema_version "1.0". Write ${jsonPath} and a readable ${mdPath}. Fill borrow_for_us and lessons concretely. Run the validator from the skill and fix errors. Keep a claims list with confidence in the markdown appendix. Return paths.\n${JSON.stringify(lensOut)}`,
  { label: 'merge', phase: 'Merge', schema: { type: 'object', properties: { json_path: { type: 'string' }, md_path: { type: 'string' }, valid: { type: 'boolean' } }, required: ['json_path', 'md_path', 'valid'] } },
)
if (!merged) { log('Merge failed'); return { error: 'merge failed', lensOut } }

phase('Fact-check')
const checked = await agent(
  `Fact-check ${merged.json_path} and ${merged.md_path}. For each factual claim (dates, developers, features, monetization, numbers) decide supported / unsupported. Edit both files in place: delete unsupported claims or rewrite them hedged ("reported", "unverified"), keep the JSON valid against the schema (use the validator from the arcosian:deconstruct skill), and list what you removed.`,
  { label: 'fact-check', phase: 'Fact-check', agentType: 'arcosian:critic', schema: { type: 'object', properties: { removed: { type: 'array', items: { type: 'string' } }, hedged: { type: 'array', items: { type: 'string' } }, valid: { type: 'boolean' } }, required: ['removed', 'valid'] } },
)
return { game, json: merged.json_path, markdown: merged.md_path, factCheck: checked }
