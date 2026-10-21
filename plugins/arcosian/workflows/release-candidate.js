export const meta = {
  name: 'release-candidate',
  description: 'Prepare a release candidate: compliance pre-flight, version bump, builds, perf check, store metadata and screenshots, compliance-officer review, and internal-track upload preparation only. Produces a release report and a human approval checklist. Never submits for store review.',
  whenToUse: 'When a build is feature-complete and you want a TestFlight or Play internal candidate. Args: {platforms?=["ios","android"], track?="internal"}.',
  phases: [
    { title: 'Preflight', detail: 'compliance_preflight.py and gate status of all features' },
    { title: 'Build', detail: 'Version bump and signed builds per platform' },
    { title: 'Verify', detail: 'Perf check, store metadata, screenshots' },
    { title: 'Review', detail: 'Compliance officer review of the whole package' },
    { title: 'Prepare', detail: 'Internal-track upload preparation only' },
    { title: 'Report', detail: 'Release report and human approval checklist' },
  ],
}

const a = args || {}
const platforms = (a.platforms && a.platforms.length) ? a.platforms : ['ios', 'android']
const track = a.track || 'internal'
const SKILL = 'Invoke the arcosian:ship skill (Skill tool) first: it gives the exact script paths, build commands, signing notes and upload steps. Never write credentials anywhere; signing material and store keys come from the environment or the human.'
const RULE = 'HARD RULE: never submit anything for store review or release to production/external testers. Stop at internal-track preparation.'

if (track !== 'internal') log(`Track "${track}" requested; this workflow only prepares internal uploads. Treating as internal.`)

phase('Preflight')
const pre = await agent(
  `${SKILL}\nRun compliance_preflight.py --project . --platform all --json, and check .gamestudio/features.json: every P0/P1 feature must have passes true. List blockers (compliance failures, unfinished features, missing licences via licence_check, missing privacy/age/AI-disclosure items).`,
  { label: 'preflight', phase: 'Preflight', agentType: 'arcosian:release-manager', schema: { type: 'object', properties: { ok: { type: 'boolean' }, blockers: { type: 'array', items: { type: 'string' } }, warnings: { type: 'array', items: { type: 'string' } } }, required: ['ok', 'blockers'] } },
)
if (!pre || !pre.ok) { log('Preflight failed: ' + JSON.stringify(pre && pre.blockers)); return { stopped: 'preflight', preflight: pre } }

phase('Build')
const bump = await agent(
  `${SKILL}\nBump the version and build number consistently across engine settings and store metadata (semver patch unless the skill says otherwise); record in progress.md. Return the new version and build number.`,
  { label: 'version bump', phase: 'Build', agentType: 'arcosian:release-manager', schema: { type: 'object', properties: { version: { type: 'string' }, build: { type: 'string' } }, required: ['version', 'build'] } },
)
if (!bump) return { stopped: 'version bump failed' }
const builds = await pipeline(platforms, (p) => agent(
  `${SKILL}\n${RULE}\nBuild the release artifact for ${p} (version ${bump.version}, build ${bump.build}) with the engine export command from the skill into .gamestudio/evidence/release/${p}/. Record log path and artifact path; if signing material is missing, say so and stop for this platform rather than improvising.`,
  { label: `build ${p}`, phase: 'Build', agentType: 'arcosian:release-manager', schema: { type: 'object', properties: { platform: { type: 'string' }, ok: { type: 'boolean' }, artifact: { type: 'string' }, log: { type: 'string' }, problem: { type: 'string' } }, required: ['platform', 'ok'] } },
))
const built = builds.filter(b => b && b.ok)
if (!built.length) { log('No platform built'); return { stopped: 'build', builds } }

phase('Verify')
const [perf, meta2, shots] = await parallel([
  () => agent(`${SKILL}\nRun the perf check on the release candidate for the reference device tiers with perf_budget.py against the contract's perf_budgets; write .gamestudio/reports/perf-release.json (perf-report schema). Report violations.`, { label: 'perf check', phase: 'Verify', agentType: 'arcosian:performance-engineer', schema: { type: 'object', properties: { verdict: { type: 'string', enum: ['pass', 'fail'] }, violations: { type: 'array', items: { type: 'string' } }, path: { type: 'string' } }, required: ['verdict'] } }),
  () => agent(`${SKILL}\nGenerate store metadata with store_metadata.py from the contract (en-US plus locales in config) into .gamestudio/evidence/release/metadata/. Check lengths, age rating answers and privacy/data-safety answers.`, { label: 'store metadata', phase: 'Verify', agentType: 'arcosian:release-manager', schema: { type: 'object', properties: { path: { type: 'string' }, issues: { type: 'array', items: { type: 'string' } } }, required: ['path'] }, model: 'sonnet' }),
  () => agent(`${SKILL}\nCapture store screenshots with the engine's screenshot mode for each platform orientation and save to .gamestudio/evidence/release/screenshots/. Check them against the style bible.`, { label: 'screenshots', phase: 'Verify', agentType: 'arcosian:technical-artist', schema: { type: 'object', properties: { dir: { type: 'string' }, count: { type: 'number' }, issues: { type: 'array', items: { type: 'string' } } }, required: ['dir'] }, model: 'sonnet' }),
])

phase('Review')
const review = await agent(
  `Review the whole release package for store policy, privacy, age rating, loot-box and monetization law in target storefronts, licence terms (licence_check) and AI-content disclosure. Inputs: preflight ${JSON.stringify(pre)}, builds ${JSON.stringify(builds)}, metadata ${JSON.stringify(meta2)}, screenshots ${JSON.stringify(shots)}. Return approve / approve-with-conditions / reject with reasons.`,
  { label: 'compliance review', phase: 'Review', agentType: 'arcosian:compliance-officer', schema: { type: 'object', properties: { decision: { type: 'string', enum: ['approve', 'approve-with-conditions', 'reject'] }, conditions: { type: 'array', items: { type: 'string' } }, reasons: { type: 'string' } }, required: ['decision'] } },
)
const blocked = !review || review.decision === 'reject' || (perf && perf.verdict === 'fail')

phase('Prepare')
const upload = blocked ? null : await agent(
  `${SKILL}\n${RULE}\nPrepare ${built.map(b => b.platform).join(' and ')} uploads to the internal track only (TestFlight internal testing / Play internal testing): produce the exact upload commands or fastlane lane and stage the package, but let the human run any step that needs their credentials. Do not click or call anything that submits for review.`,
  { label: 'prepare uploads', phase: 'Prepare', agentType: 'arcosian:release-manager', schema: { type: 'object', properties: { prepared: { type: 'array', items: { type: 'string' } }, commands: { type: 'array', items: { type: 'string' } }, needs_human: { type: 'array', items: { type: 'string' } } }, required: ['prepared'] } },
)

phase('Report')
const report = await agent(
  `Write .gamestudio/reports/release-candidate.md: version ${bump.version} (${bump.build}), platforms, evidence paths, perf and compliance outcomes, conditions, and what was prepared. End with a "Human approval checklist" (tick boxes) including: review perf/compliance conditions, test the internal build on real devices, confirm age rating and privacy answers, supply signing/store credentials, explicitly approve store submission. State that submission for review has NOT been done and requires explicit human approval.\nData: ${JSON.stringify({ pre, bump, builds, perf, meta2, shots, review, upload, blocked })}`,
  { label: 'release report', phase: 'Report', agentType: 'arcosian:producer', schema: { type: 'object', properties: { path: { type: 'string' }, ready_for_human: { type: 'boolean' } }, required: ['path', 'ready_for_human'] } },
)
return { version: bump.version, blocked: !!blocked, review, report, submittedForReview: false }
