export const meta = {
  name: 'design-review',
  description: 'Multi-discipline review of the design contract: lens reviewers report severity-rated findings, each finding is checked by 2 skeptics, and a report with proposed contract edits is written (edits are not applied).',
  whenToUse: 'Before committing to production, after a major contract change, or at tier gates. Args: {contract_path?} defaults to .gamestudio/contract.json.',
  phases: [
    { title: 'Review', detail: 'Seven lens reviewers: design, economy, UX, monetization ethics, tech feasibility, market, scope' },
    { title: 'Challenge', detail: 'Two skeptics try to refute each major finding' },
    { title: 'Report', detail: 'Synthesis report .gamestudio/reports/design-review.md with proposed edits' },
  ],
}

const contract = (args && args.contract_path) || '.gamestudio/contract.json'
const SKILL = 'Invoke the arcosian:design-review skill (Skill tool) first for the checklist and paths.'
const LENSES = [
  ['game design', 'arcosian:game-designer'],
  ['economy and progression', 'arcosian:systems-designer'],
  ['mobile UX and onboarding', 'arcosian:ux-designer'],
  ['monetization ethics', 'arcosian:monetization-designer'],
  ['technical feasibility', 'arcosian:lead-engineer'],
  ['market fit', 'arcosian:market-analyst'],
  ['scope and schedule', 'arcosian:producer'],
]
const findingsSchema = {
  type: 'object',
  properties: {
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          title: { type: 'string' },
          severity: { type: 'string', enum: ['blocker', 'major', 'minor', 'polish'] },
          detail: { type: 'string' },
          contract_path: { type: 'string' },
          proposed_edit: { type: 'string' },
        },
        required: ['title', 'severity', 'detail'],
      },
    },
  },
  required: ['findings'],
}
const verdictSchema = {
  type: 'object',
  properties: { holds: { type: 'boolean' }, reason: { type: 'string' } },
  required: ['holds', 'reason'],
}

phase('Review')
const reviews = await parallel(LENSES.map(([lens, agentType]) => () => agent(
  `${SKILL}\nReview the design contract at ${contract} through the "${lens}" lens only. Report concrete findings with severity (blocker, major, minor, polish), the contract JSON path affected, and a proposed edit. Read-only: do not modify the contract. No filler; at most 8 findings, strongest first.`,
  { label: `review: ${lens}`, phase: 'Review', agentType, schema: findingsSchema },
)))
const all = []
reviews.forEach((r, i) => { if (r) for (const f of r.findings) all.push({ ...f, lens: LENSES[i][0] }) })
log(`${all.length} findings from ${reviews.filter(Boolean).length}/${LENSES.length} lenses`)

phase('Challenge')
const major = all.filter(f => f.severity === 'blocker' || f.severity === 'major')
const checks = await pipeline(major,
  (f) => parallel([1, 2].map(k => () => agent(
    `Skeptic ${k}: try to refute this design-review finding about ${contract}. Read the contract and check whether the finding is real, correctly rated and the proposed edit sensible.\nLens: ${f.lens}\nFinding: ${f.title}\n${f.detail}\nProposed edit: ${f.proposed_edit || 'none'}`,
    { label: `skeptic ${k}: ${f.title.slice(0, 40)}`, phase: 'Challenge', agentType: 'arcosian:critic', schema: verdictSchema },
  ))),
)
major.forEach((f, i) => {
  const v = (checks[i] || []).filter(Boolean)
  f.skeptics = v
  f.confirmed = v.length > 0 && v.filter(x => x.holds).length >= Math.ceil(v.length / 2)
})
const dropped = major.filter(f => !f.confirmed).map(f => f.title)
if (dropped.length) log('Not confirmed by skeptics: ' + dropped.join('; '))

phase('Report')
const keep = all.filter(f => !major.includes(f) || f.confirmed)
const report = await agent(
  `${SKILL}\nWrite .gamestudio/reports/design-review.md for ${contract}: verdict (go / go with changes / no-go), findings grouped by severity then lens, skeptic outcomes for major ones, unconfirmed findings listed separately as "disputed", and a "Proposed contract edits" section with exact JSON paths and new values. Do NOT edit the contract itself.\nConfirmed/minor findings: ${JSON.stringify(keep)}\nDisputed: ${JSON.stringify(major.filter(f => !f.confirmed))}`,
  { label: 'report', phase: 'Report', agentType: 'arcosian:principal', schema: { type: 'object', properties: { path: { type: 'string' }, verdict: { type: 'string' }, blockers: { type: 'number' } }, required: ['path', 'verdict'] } },
)
return { report, findings: keep.length, disputed: dropped.length }
