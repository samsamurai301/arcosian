export const meta = {
  name: 'playtest-sweep',
  description: 'Run deterministic playthroughs and bot runs plus parallel player-simulator personas, dedupe findings, verify blockers, and write .gamestudio/playtests/sweep-report.json and a markdown summary.',
  whenToUse: 'Before a milestone, after balance or feature changes, or to find softlocks and onboarding friction. Args: {personas?, runs?}.',
  phases: [
    { title: 'Automated', detail: 'Scripted playthroughs and bot runs via the engine runner' },
    { title: 'Personas', detail: 'Parallel player-simulator personas play the build' },
    { title: 'Dedupe', detail: 'Merge findings across sources' },
    { title: 'Verify', detail: 'Reproduce every blocker and major finding' },
    { title: 'Report', detail: 'sweep-report.json + markdown' },
  ],
}

const a = args || {}
const runs = a.runs || 200
const personas = (a.personas && a.personas.length) ? a.personas : ['casual commuter, one-handed, 3-minute sessions', 'completionist who reads everything', 'impatient skipper who ignores tutorials', 'lapsed player returning after 3 weeks', 'low-end device, accessibility needs (small text, colour blindness)']
const SKILL = 'Invoke the arcosian:playtest skill (Skill tool) first: it gives the exact runner command lines for the engine in .gamestudio/config.json and the playtest-report schema (schema_version "1.0").'
const findingItem = { type: 'object', properties: { severity: { type: 'string', enum: ['blocker', 'major', 'minor', 'polish'] }, title: { type: 'string' }, detail: { type: 'string' }, repro: { type: 'string' } }, required: ['severity', 'title', 'detail'] }
const reportSchema = { type: 'object', properties: { report_path: { type: 'string' }, runs: { type: 'number' }, metrics: { type: 'string' }, findings: { type: 'array', items: findingItem } }, required: ['report_path', 'findings'] }

phase('Automated')
const [scripted, bots] = await parallel([
  () => agent(`${SKILL}\nRun every deterministic playthrough script in the project's tests/playthroughs (seed 1). Write reports to .gamestudio/playtests/scripted-<name>.json and validate them against the schema. Report failures as findings with repro commands.`, { label: 'scripted playthroughs', phase: 'Automated', agentType: 'arcosian:qa-lead', schema: reportSchema, model: 'sonnet' }),
  () => agent(`${SKILL}\nRun bots (greedy and random, ${runs} runs, seed 1) and write .gamestudio/playtests/bots.json. Estimate win rate, softlock count, crashes and errors. Compare win rate with the contract's difficulty target. Report anomalies as findings.`, { label: 'bot runs', phase: 'Automated', agentType: 'arcosian:qa-lead', schema: reportSchema, model: 'sonnet' }),
])

phase('Personas')
const persona = (await parallel(personas.map((p, i) => () => agent(
  `${SKILL}\nYou are playing this build as: ${p}. Play through the first session and the first return visit using the runner/input injection described in the skill, take screenshots where useful, and report your experience honestly: confusion, boredom, frustration, delight, anything blocking. Save to .gamestudio/playtests/persona-${i + 1}.json (mode "persona").`,
  { label: `persona ${i + 1}`, phase: 'Personas', agentType: 'arcosian:player-simulator', schema: reportSchema, model: 'sonnet' },
)))).filter(Boolean)

phase('Dedupe')
const raw = []
for (const [src, r] of [['scripted', scripted], ['bots', bots], ...persona.map((r, i) => [`persona ${i + 1}`, r])]) {
  if (r) for (const f of r.findings) raw.push({ ...f, source: src })
}
log(`${raw.length} raw findings`)
const merged = raw.length ? await agent(
  `Deduplicate these playtest findings: merge duplicates (same root cause), keep the highest severity, list all sources, keep the best repro.\n${JSON.stringify(raw)}`,
  { label: 'dedupe', phase: 'Dedupe', model: 'sonnet', schema: { type: 'object', properties: { findings: { type: 'array', items: { type: 'object', properties: { ...findingItem.properties, sources: { type: 'array', items: { type: 'string' } } }, required: ['severity', 'title', 'detail'] } } }, required: ['findings'] } },
) : { findings: [] }
const findings = merged ? merged.findings : raw.map(f => ({ ...f, sources: [f.source] }))

phase('Verify')
const serious = findings.filter(f => f.severity === 'blocker' || f.severity === 'major')
const verdicts = await pipeline(serious, (f) => agent(
  `${SKILL}\nVerify by reproducing: ${f.title}\n${f.detail}\nRepro: ${f.repro || 'none given, find one'}\nTry to reproduce it twice with the runner. Say reproduced / not reproduced / cannot verify, and correct the severity if it is wrong.`,
  { label: `verify: ${f.title.slice(0, 40)}`, phase: 'Verify', agentType: 'arcosian:qa-lead', schema: { type: 'object', properties: { status: { type: 'string', enum: ['reproduced', 'not_reproduced', 'cannot_verify'] }, severity: { type: 'string' }, repro: { type: 'string' } }, required: ['status'] } },
))
serious.forEach((f, i) => { const v = verdicts[i]; f.verified = v ? v.status : 'cannot_verify'; if (v && v.severity) f.severity = v.severity; if (v && v.repro) f.repro = v.repro })

phase('Report')
const report = await agent(
  `Write .gamestudio/playtests/sweep-report.json (schema_version "1.0": findings with severity, title, detail, repro, sources, verified; metrics from the scripted and bot reports; verdict "fail" if any verified or unverified blocker remains, else "pass") and a readable .gamestudio/playtests/sweep-report.md. Do not include blockers that were "not_reproduced" except in a "could not reproduce" list.\nFindings: ${JSON.stringify(findings)}\nBot metrics: ${JSON.stringify(bots && bots.metrics)}\nScripted: ${JSON.stringify(scripted && scripted.metrics)}`,
  { label: 'report', phase: 'Report', agentType: 'arcosian:qa-lead', schema: { type: 'object', properties: { json_path: { type: 'string' }, md_path: { type: 'string' }, verdict: { type: 'string', enum: ['pass', 'fail'] } }, required: ['json_path', 'md_path', 'verdict'] } },
)
return { report, findings: findings.length, blockers: findings.filter(f => f.severity === 'blocker' && f.verified !== 'not_reproduced').length }
