export const meta = {
  name: 'balance-pass',
  description: 'Systems designer builds or updates the economy model, runs the balance simulators via the balance skill, proposes changes, re-runs to verify them, and writes a balance report.',
  whenToUse: 'After economy, progression or difficulty changes, or when playtest/analytics data shows hoarding, stalls or churn spikes. Args: {focus?} such as "soft currency", "difficulty", "gacha".',
  phases: [
    { title: 'Model', detail: 'Build or update the economy model in .gamestudio/economy/' },
    { title: 'Simulate', detail: 'Run economy_sim and related calculators, diagnose against targets' },
    { title: 'Tune', detail: 'Propose parameter changes and apply them to a candidate model copy' },
    { title: 'Verify', detail: 'Re-run the simulators on the candidate and compare with baseline' },
    { title: 'Report', detail: '.gamestudio/reports/balance-pass.md' },
  ],
}

const focus = (args && args.focus) || 'whole economy and difficulty curve'
const SKILL = 'Invoke the arcosian:balance skill (Skill tool) first: it gives the exact script paths, command lines and the economy-model schema. Run the scripts for real, never estimate results by hand.'
const AGENT = 'arcosian:systems-designer'
const simSchema = {
  type: 'object',
  properties: {
    model_path: { type: 'string' },
    metrics: { type: 'string' },
    violations: { type: 'array', items: { type: 'string' } },
    output_paths: { type: 'array', items: { type: 'string' } },
  },
  required: ['model_path', 'metrics', 'violations'],
}

phase('Model')
const model = await agent(
  `${SKILL}\nFocus: ${focus}. Read .gamestudio/contract.json (economy, progression, monetization, analytics targets). Build or update the economy model at .gamestudio/economy/model.json (economy-model.schema.json, schema_version "1.0"), validate it with validate_json.py, and list assumptions you had to make.`,
  { label: 'economy model', phase: 'Model', agentType: AGENT, schema: { type: 'object', properties: { model_path: { type: 'string' }, assumptions: { type: 'array', items: { type: 'string' } } }, required: ['model_path'] } },
)
if (!model) { log('Could not build an economy model'); return { error: 'no model' } }

phase('Simulate')
const base = await agent(
  `${SKILL}\nBaseline run on ${model.model_path}: economy_sim.py (--runs 200 --seed 1 --json --out .gamestudio/economy/baseline.json) plus, where relevant to the focus (${focus}), progression_calc.py, difficulty_curve.py and gacha_calc.py. Compare against the model's targets (days_to_complete_content, max_soft_currency_hoard_days, payer_conversion). List every violated target with the number.`,
  { label: 'baseline sim', phase: 'Simulate', agentType: AGENT, schema: simSchema },
)
if (!base) { log('Baseline simulation failed'); return { error: 'baseline failed', model } }

phase('Tune')
const tune = await agent(
  `${SKILL}\nBaseline results: ${JSON.stringify(base)}\nPropose the minimum set of parameter changes that fix the violations without breaking other targets. For each: path, old value, new value, expected effect, and the player-experience reason. Write the changed copy to .gamestudio/economy/candidate.json (do not overwrite model.json) and validate it. If nothing needs changing, say so and copy nothing.`,
  { label: 'propose changes', phase: 'Tune', agentType: AGENT, schema: { type: 'object', properties: { changes: { type: 'array', items: { type: 'object', properties: { path: { type: 'string' }, old: { type: 'string' }, new: { type: 'string' }, effect: { type: 'string' } }, required: ['path', 'new'] } }, candidate_path: { type: 'string' } }, required: ['changes'] } },
)

phase('Verify')
let verify = null
if (tune && tune.changes.length && tune.candidate_path) {
  verify = await agent(
    `${SKILL}\nRe-run the same simulators on ${tune.candidate_path} (same seeds and runs as the baseline, output to .gamestudio/economy/candidate-run.json). Report whether each previously violated target is now met, and whether any new violation appeared. Also run with a second seed (--seed 2) to check stability.\nBaseline: ${JSON.stringify(base)}\nChanges: ${JSON.stringify(tune.changes)}`,
    { label: 'verify candidate', phase: 'Verify', agentType: AGENT, schema: { type: 'object', properties: { fixed: { type: 'array', items: { type: 'string' } }, remaining: { type: 'array', items: { type: 'string' } }, regressions: { type: 'array', items: { type: 'string' } }, stable_across_seeds: { type: 'boolean' } }, required: ['fixed', 'remaining', 'regressions'] } },
  )
} else log('No changes proposed; skipping verification')

phase('Report')
const report = await agent(
  `${SKILL}\nWrite .gamestudio/reports/balance-pass.md: focus, baseline metrics, violations, proposed changes with before/after numbers, verification outcome, residual risks, and what to playtest next. State clearly that candidate.json is NOT yet adopted: adopting it is a human/principal decision.\nData: ${JSON.stringify({ model, base, tune, verify })}`,
  { label: 'report', phase: 'Report', agentType: AGENT, schema: { type: 'object', properties: { path: { type: 'string' }, summary: { type: 'string' } }, required: ['path', 'summary'] } },
)
return { report, tune, verify }
