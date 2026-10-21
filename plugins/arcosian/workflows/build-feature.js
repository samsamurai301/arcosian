export const meta = {
  name: 'build-feature',
  description: 'Implement one feature end to end: engineer builds sim-core plus tests then presentation, a gate runner executes the five gates and records evidence with gs.py, a critic tries to refute completion, and failures are fixed and re-gated up to 3 rounds.',
  whenToUse: 'To take a single feature from features.json to done. Args: {feature_id} such as "F012".',
  phases: [
    { title: 'Plan', detail: 'Read the feature, contract and architecture; pick the engineer' },
    { title: 'Implement', detail: 'Sim-core + unit tests first, then presentation' },
    { title: 'Gate', detail: 'Run static, unit, playthrough, visual, perf gates and record evidence' },
    { title: 'Refute', detail: 'Critic tries to prove the feature is not really done' },
    { title: 'Fix', detail: 'Fix failures and re-gate, max 3 rounds' },
    { title: 'Close', detail: 'gs.py feature pass only if every gate passes' },
  ],
}

const id = args && args.feature_id
if (!id) { log('args.feature_id is required'); return { error: 'args.feature_id is required' } }
const SKILL = 'Invoke the arcosian:build-feature skill (Skill tool) first: it gives the exact gs.py, gslib and engine command lines, the five gates and evidence paths. Project state lives in .gamestudio/.'
const GATES = ['static', 'unit', 'playthrough', 'visual', 'perf']
const gateSchema = {
  type: 'object',
  properties: {
    results: { type: 'array', items: { type: 'object', properties: { gate: { type: 'string', enum: GATES }, status: { type: 'string', enum: ['pass', 'fail', 'n/a'] }, evidence: { type: 'string' }, note: { type: 'string' } }, required: ['gate', 'status'] } },
  },
  required: ['results'],
}

phase('Plan')
const plan = await agent(
  `${SKILL}\nFeature ${id}: read it in .gamestudio/features.json, plus contract.json and config.json. Check depends_on are done. Produce an implementation plan (sim-core units, tests, presentation pieces, which gates can be n/a and why) and name the engine from config.`,
  { label: 'plan', phase: 'Plan', agentType: 'arcosian:lead-engineer', schema: { type: 'object', properties: { engine: { type: 'string' }, plan: { type: 'string' }, blocked: { type: 'boolean' }, blocked_reason: { type: 'string' } }, required: ['engine', 'plan', 'blocked'] } },
)
if (!plan || plan.blocked) { log('Blocked: ' + (plan ? plan.blocked_reason : 'planning failed')); return { error: 'blocked', plan } }
const engineer = plan.engine === 'unity' ? 'arcosian:unity-engineer' : plan.engine === 'godot' ? 'arcosian:godot-engineer' : 'arcosian:gameplay-engineer'

phase('Implement')
const sim = await agent(
  `${SKILL}\nFeature ${id}. Plan: ${plan.plan}\nStep 1 only: implement the deterministic sim-core logic (no engine node/UnityEngine references) and its headless unit tests, and a playthrough script if the plan needs one. Run the unit tests and fix until green.`,
  { label: 'sim-core + tests', phase: 'Implement', agentType: engineer, schema: { type: 'object', properties: { files: { type: 'array', items: { type: 'string' } }, tests_green: { type: 'boolean' } }, required: ['files', 'tests_green'] } },
)
if (!sim) return { error: 'sim-core implementation failed' }
await agent(
  `${SKILL}\nFeature ${id}. Sim-core is done (${sim.files.join(', ')}). Step 2: implement the presentation layer (scenes/views/HUD/feedback) wired to sim-core only through its public interface. Keep logic out of the presentation.`,
  { label: 'presentation', phase: 'Implement', agentType: engineer, schema: { type: 'object', properties: { files: { type: 'array', items: { type: 'string' } } }, required: ['files'] } },
)

let gates = null, refuted = null, lastFailures = []
for (let round = 1; round <= 3; round++) {
  phase('Gate')
  gates = await agent(
    `${SKILL}\nRound ${round}: run all five gates for ${id} with the command lines from the skill, write evidence under .gamestudio/evidence/${id}/, and record each with gs.py (gate status plus evidence path). "n/a" needs a gate_notes entry. Do NOT run "gs.py feature pass".`,
    { label: `gates r${round}`, phase: 'Gate', agentType: 'arcosian:qa-lead', schema: gateSchema },
  )
  const failed = gates ? gates.results.filter(r => r.status === 'fail') : [{ gate: 'all', note: 'gate runner failed' }]
  if (!failed.length && gates) {
    phase('Refute')
    refuted = await agent(
      `Try to refute that ${id} is done. Read the feature acceptance criteria, the code, and the evidence in .gamestudio/evidence/${id}/ (open the files; check that evidence exists and actually proves the criteria, that n/a gates are justified, and that screenshots show a working feature). Gate results: ${JSON.stringify(gates.results)}`,
      { label: `critic r${round}`, phase: 'Refute', agentType: 'arcosian:critic', schema: { type: 'object', properties: { refuted: { type: 'boolean' }, problems: { type: 'array', items: { type: 'string' } } }, required: ['refuted', 'problems'] } },
    )
    if (refuted && !refuted.refuted) { lastFailures = []; break }
    lastFailures = refuted ? refuted.problems : ['critic failed to run']
  } else lastFailures = failed.map(f => `${f.gate}: ${f.note || 'failed'}`)
  if (round === 3) break
  phase('Fix')
  await agent(
    `${SKILL}\nFix these problems for ${id}, then stop (the gates will be re-run): ${JSON.stringify(lastFailures)}`,
    { label: `fix r${round}`, phase: 'Fix', agentType: engineer, schema: { type: 'object', properties: { fixed: { type: 'array', items: { type: 'string' } } }, required: ['fixed'] } },
  )
}

phase('Close')
const ok = gates && !lastFailures.length && refuted && !refuted.refuted
if (!ok) { log(`${id} NOT passed after 3 rounds: ${lastFailures.join('; ')}`); return { feature: id, passed: false, remaining: lastFailures, gates } }
const closed = await agent(
  `${SKILL}\nAll gates passed and the critic could not refute ${id}. Run gs.py feature pass for ${id}; it enforces the evidence rule itself. Add a progress.md entry. Report the exit code and output.`,
  { label: 'feature pass', phase: 'Close', agentType: 'arcosian:producer', schema: { type: 'object', properties: { exit_code: { type: 'number' }, output: { type: 'string' } }, required: ['exit_code'] } },
)
return { feature: id, passed: !!closed && closed.exit_code === 0, gates: gates.results, closed }
