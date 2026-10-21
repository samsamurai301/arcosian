export const meta = {
  name: 'concept-tournament',
  description: 'Generate n concept cards from distinct angles, score them with 3 independent judges, run a pairwise tournament on the top 4, try to refute the winner, then synthesize a final concept.',
  whenToUse: 'At the start of a new game, or when the current concept is weak and you need competing alternatives. Args: {brief, constraints?, n?=6}.',
  phases: [
    { title: 'Generate', detail: 'One concept card per angle, saved under .gamestudio/concepts/' },
    { title: 'Judge', detail: '3 independent judges score every card with the concept-lab rubric' },
    { title: 'Tournament', detail: 'Pairwise bracket of the top 4' },
    { title: 'Refute', detail: 'Critic tries to kill the winner' },
    { title: 'Synthesize', detail: 'Winner plus the best grafted ideas, saved as final concept card' },
  ],
}

const a = args || {}
const n = Math.max(2, Math.min(a.n || 6, 6))
const ANGLES = ['market gap', 'mechanic-first', 'analogy transplant', 'motivation-first', 'constraint inversion', 'art hook'].slice(0, n)
const SKILL = 'First invoke the arcosian:concept-lab skill (Skill tool) for the method, concept-card fields and exact paths. Concept cards follow concept.schema.json (schema_version "1.0").'
const ctx = `Brief: ${a.brief}\nConstraints: ${a.constraints || 'none'}`

const cardSchema = {
  type: 'object',
  properties: { id: { type: 'string' }, title: { type: 'string' }, logline: { type: 'string' }, path: { type: 'string' }, hook: { type: 'string' }, angle: { type: 'string' } },
  required: ['id', 'title', 'logline', 'path'],
}
const scoreSchema = {
  type: 'object',
  properties: { scores: { type: 'array', items: { type: 'object', properties: { id: { type: 'string' }, total: { type: 'number' }, note: { type: 'string' } }, required: ['id', 'total'] } } },
  required: ['scores'],
}
const pairSchema = {
  type: 'object',
  properties: { winner: { type: 'string' }, reason: { type: 'string' } },
  required: ['winner', 'reason'],
}

phase('Generate')
const cards = (await parallel(ANGLES.map((angle, i) => () => agent(
  `${SKILL}\n${ctx}\nAngle: ${angle}. Write ONE concept card from this angle only, make it distinct from the other angles. Save it to .gamestudio/concepts/ as ${String(i + 1).padStart(2, '0')}-<slug>.json and validate it with the validate_json.py script from the skill. Return its id, title, logline, hook and project-relative path.`,
  { label: `concept: ${angle}`, phase: 'Generate', schema: cardSchema, model: 'sonnet' },
)))).filter(Boolean)
if (cards.length < 2) { log('Fewer than 2 concept cards were produced; aborting.'); return { error: 'not enough concepts', cards } }
const list = cards.map(c => `- ${c.id}: ${c.title} (${c.path}) ${c.logline}`).join('\n')

phase('Judge')
const judged = (await parallel([1, 2, 3].map(j => () => agent(
  `${SKILL}\nYou are independent judge ${j}. Read every concept card file and score each with skills/concept-lab/references/scoring-rubric.md (the skill gives its path). Judge alone; do not soften scores. Return a total per id.\n${ctx}\nCards:\n${list}`,
  { label: `judge ${j}`, phase: 'Judge', schema: scoreSchema },
)))).filter(Boolean)
const totals = {}
for (const r of judged) for (const s of r.scores) totals[s.id] = (totals[s.id] || 0) + s.total
const ranked = cards.slice().sort((x, y) => (totals[y.id] || 0) - (totals[x.id] || 0))
log('Ranking: ' + ranked.map(c => `${c.id}=${totals[c.id] || 0}`).join(', '))

phase('Tournament')
const top = ranked.slice(0, 4)
const duel = async (x, y, label) => {
  const r = await agent(
    `${SKILL}\nPairwise match. Read both cards and pick the concept more likely to become a successful, buildable mobile game. ${ctx}\nA: ${x.id} ${x.title} (${x.path})\nB: ${y.id} ${y.title} (${y.path})\nReturn winner as exactly "${x.id}" or "${y.id}".`,
    { label, phase: 'Tournament', schema: pairSchema },
  )
  return r && r.winner === y.id ? y : x
}
let champion = top[0]
if (top.length >= 4) {
  const [s1, s2] = await parallel([() => duel(top[0], top[3], 'semi 1 v 4'), () => duel(top[1], top[2], 'semi 2 v 3')])
  champion = await duel(s1 || top[0], s2 || top[1], 'final')
} else if (top.length >= 2) {
  champion = await duel(top[0], top[1], 'final')
}
log(`Champion: ${champion.id} ${champion.title}`)

phase('Refute')
const refutation = await agent(
  `${SKILL}\nTry to refute this winning concept: find the strongest reasons it fails (market saturation, weak hook, retention, scope, agent-buildability). Read ${champion.path}. List fatal vs fixable flaws. ${ctx}`,
  { label: 'refute winner', phase: 'Refute', agentType: 'arcosian:critic', schema: { type: 'object', properties: { fatal: { type: 'array', items: { type: 'string' } }, fixable: { type: 'array', items: { type: 'string' } }, verdict: { type: 'string' } }, required: ['fatal', 'fixable', 'verdict'] } },
)

phase('Synthesize')
const others = ranked.filter(c => c.id !== champion.id).map(c => `${c.id} ${c.path}`).join('\n')
const final = await agent(
  `${SKILL}\nSynthesize the final concept: start from the winner ${champion.path}, fix the critic's fixable flaws (${JSON.stringify(refutation && refutation.fixable)}), address fatal ones (${JSON.stringify(refutation && refutation.fatal)}) or say plainly if the concept must be dropped, and graft the best ideas from the runners-up:\n${others}\nSave as .gamestudio/concepts/final.json (validate it). Summarize what was grafted from where. ${ctx}`,
  { label: 'synthesis', phase: 'Synthesize', schema: { type: 'object', properties: { path: { type: 'string' }, title: { type: 'string' }, grafts: { type: 'array', items: { type: 'string' } }, summary: { type: 'string' } }, required: ['path', 'title', 'summary'] } },
)
return { ranking: ranked.map(c => ({ id: c.id, title: c.title, total: totals[c.id] || 0 })), champion: champion.id, refutation, final }
