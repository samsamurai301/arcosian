# Soft Launch and Ops

This file covers soft launch (purpose, market selection, tests, KPI gates), the global launch checklist, and the operational craft of running a live game: remote-config workflows, live incidents, economy hotfixes and compensation. Soft-launch market lists and benchmark numbers are volatile and judgment-dependent, so they are hedged and flagged. Read it when planning a soft launch, deciding go or no-go, or building runbooks for live operations.

## Table of contents
1. Purpose of soft launch
2. Soft-launch plan structure
3. Choosing markets
4. What to test, in order
5. KPI gates
6. Reading soft-launch data
7. Go, iterate or kill
8. Global launch checklist
9. Remote config workflow
10. Live incident runbook
11. Economy hotfixes
12. Compensation policy
13. Support and community operations
14. Monitoring and alerts
15. Release train and rollbacks
16. Volatile facts (as of Oct 2026 - verify)

## 1. Purpose of soft launch
- Learn whether the game's retention, monetization and technical stability justify scaling UA, while the cost of being wrong is small.
- Soft launch is a measurement exercise, not a marketing event. Do not announce; do not spend large budgets.
- It also validates infrastructure: servers, analytics, payments, support, localization and store listings.
- Decide in advance which decisions the data will drive; otherwise data becomes a rationalization tool.

## 2. Soft-launch plan structure
Use the `soft-launch-plan` template in `templates/docs/`. Contents:
1. Hypotheses and decisions: for example "D1 retention at or above target allows scaling creative testing".
2. Markets and platforms, sample size targets, and duration.
3. Build and version plan; telemetry checklist; privacy and consent readiness.
4. UA plan: small, controlled spend; creative variants; channel mix.
5. KPI gates and thresholds (section 5).
6. Test calendar: onboarding tweaks, difficulty, monetization, ads.
7. Roles: owner for data, build, support, decision-making.
8. Exit criteria: what constitutes go, iterate, kill.
Sample sizes: retention is a proportion; estimate the needed installs with a confidence interval calculator (`ab_test.py` can size comparisons). Rare events like payer conversion need many more users than retention.

## 3. Choosing markets
Criteria (rank by what matters for your game):
| Criterion | Why |
|---|---|
| Behavioral similarity to the target market | Retention and monetization transfer imperfectly; pick markets with similar player habits |
| Language | English-speaking soft-launch markets simplify early localization |
| Cost per install | Lower cost lets you buy more data per budget |
| Platform mix | Match your platform priorities |
| Store features and policies | Ability to restrict availability; tax and payment readiness |
| Regulatory exposure | Avoid markets with unusually heavy compliance load for testing |
| Representativeness of spenders | Cheap markets under-represent high-spending behavior; use a second, more expensive market for monetization validation |
Strategy:
- Phase 1: cheap English-speaking or similar market for gameplay and retention.
- Phase 2: a market closer to the target spender profile for monetization tests, with a smaller budget.
- Phase 3: multi-region validation before global launch, including localization and payments.
- Avoid markets that are also your launch targets if you do not want pre-launch exposure, or deliberately include them if you want pre-launch learning; decide knowingly.
- Do not copy a market list from an article; build it from criteria and current data (see volatile facts).

## 4. What to test, in order
1. Technical health: crash-free rate, load time, ANR rate, battery and thermal on device tiers (`mobile-performance`).
2. Funnel and FTUE: tutorial completion, first-session length, first-session activity, D1.
3. Core loop retention: D1, D7, D14, D30 curves; session count and length; progression pacing.
4. Difficulty and content depth: where players churn (level-by-level churn).
5. Economy: currency balances, sink usage, time to first purchase opportunity.
6. Monetization: first-purchase conversion, ARPDAU, payer share, offer performance, ad ARPDAU and effect on retention.
7. Social and live events: participation, retention effects.
8. UA fit: CPI, creative to retention quality, cohort ROAS projection (see `marketing-ua`).
Rule: fix the earlier stages first; optimizing monetization on a leaky retention curve wastes time.

## 5. KPI gates
Gate design:
- A gate is a threshold on a metric with a confidence bound and a sample size requirement.
- Set thresholds from genre benchmarks in `genre-playbooks` and your own unit economics, not from folklore. State them as ranges and mark which are hard gates (technical) vs soft gates (retention, monetization).
| Stage | Metric | Gate logic |
|---|---|---|
| Technical | Crash-free sessions, startup time | Must meet store and internal budgets |
| Early retention | D1 | At or above the genre-typical level you set; below means FTUE or core loop problem |
| Mid retention | D7 | Same, plus slope of the decay curve |
| Long retention | D30 | Trajectory vs LTV model needs |
| Engagement | Sessions per DAU, minutes | Compatible with monetization surface |
| Monetization | Payer conversion, ARPDAU, ad ARPDAU | Combined with retention gives LTV |
| Unit economics | LTV (projected) vs CPI | LTV above CPI with margin at target payback window |
Projected LTV: use `${CLAUDE_PLUGIN_ROOT}/scripts/retention_ltv.py` to fit a retention curve (for example a power-law extrapolation) and multiply by ARPDAU; report intervals, not points.
Warning: early cohorts of cheap, incentivized or non-representative traffic can mislead; weight cohorts by their relevance to scaled UA.

## 6. Reading soft-launch data
- Cohort by install date, country, platform, channel, creative.
- Separate organic from paid; paid players behave differently.
- Compare to benchmarks cautiously; benchmark definitions vary by source.
- Watch for outliers: a single big spender can distort ARPDAU in small samples; look at median and trimmed means.
- Segment by device tier to catch performance problems hiding in averages.
- Check data integrity: duplicate events, missing events, time zones.
- Consider experiment structure: when testing changes in soft launch, ensure test and control run at the same time and same channels.

## 7. Go, iterate or kill
| Outcome | Condition | Action |
|---|---|---|
| Go | Gates met with margin; stable build; infrastructure ready | Prepare global launch; scale UA gradually |
| Iterate | Some gates close; clear hypotheses for improvement | Run another test cycle with specific changes and a time limit |
| Pivot | Retention good but monetization weak, or vice versa | Rework economy or loop element |
| Kill | Gates far away after several cycles; no credible hypotheses | Stop, write a postmortem (`postmortem`), reuse learnings |
Time-box each iteration cycle and each stage; budget burn is a decision input. The `critic` agent should challenge optimistic reading of the data.

## 8. Global launch checklist
Product and tech
- [ ] Crash-free and performance budgets met on target device tiers.
- [ ] Server capacity tested for expected peak plus margin; autoscaling and rate limits configured.
- [ ] Remote config validated; kill switches for events, offers, ads and payments.
- [ ] Analytics and attribution verified end to end; dashboards live.
- [ ] Backup and restore tested; data migrations dry-run.
Store and legal
- [ ] Store listings, localization, screenshots and age ratings complete (`store-release`).
- [ ] Privacy policy, terms, consent flows (UMP, ATT) tested.
- [ ] IAP products approved and tested; odds disclosures; region toggles (`monetization`).
- [ ] Compliance pre-flight passed (`compliance_preflight.py`).
Operations
- [ ] Support channels and macros; escalation paths; on-call rota.
- [ ] Community channels and moderation rules; launch comms drafted.
- [ ] Incident runbooks reviewed; status page ready.
- [ ] Launch-day monitoring dashboard and alert thresholds.
- [ ] Freeze rules for the first weeks except for hotfixes.
Marketing
- [ ] UA campaigns and creatives approved; budget pacing plan (`marketing-ua`).
- [ ] Pre-registration and press plans executed or consciously skipped.
Content
- [ ] First weeks of calendar built and QA'd; evergreen contingency prepared.
- [ ] Launch event (for example welcome track) ready.
Post-launch
- [ ] Day-1, day-3 and day-7 review meetings scheduled with decision owners.

## 9. Remote config workflow
Principles: all tunables live in config; config is validated, versioned, staged and reversible.
Workflow:
1. Define the key with type, range, default, owner, and which client versions read it.
2. Change in a draft; validate against a schema (for example with `${CLAUDE_PLUGIN_ROOT}/scripts/validate_json.py` and a JSON schema).
3. Review: second pair of eyes for economy or monetization changes.
4. Stage: apply to a small percentage or to a region; watch metrics for a defined interval.
5. Roll out in steps; keep a rollback version ready.
6. Log: who, why, expected effect, review date. Keep the change history.
7. Clean up: remove stale keys and experiments.
Rules:
- Config must be backward compatible with old clients; version-gate new keys.
- Defaults compiled into the client must be safe if config fetch fails.
- Never place secrets in config.
- Separate experiment assignment from config values so analysis is clean.
- Firebase Remote Config and its MCP can read, publish and roll back templates (verify: https://firebase.google.com/docs/ai-assistance/mcp-server). Other providers have equivalents.
- Cache and refresh policy: fetch at launch and on resume with a minimum interval; handle offline play.

## 10. Live incident runbook
Severity levels:
| Level | Examples | Response |
|---|---|---|
| Sev 1 | Data loss, purchase failure, login down, economy exploit in the wild | Immediate all-hands; contain within minutes; public notice |
| Sev 2 | Major feature broken, crash spike on a popular device | Same-day fix; notice if user-visible |
| Sev 3 | Minor bug, cosmetic | Normal queue |
Roles: incident commander, communications lead, engineering lead, support lead, scribe.
Steps:
1. Detect and confirm: alerts, support spikes, social posts; reproduce.
2. Declare severity and assign roles; open a channel and a timeline doc.
3. Contain: disable the offending feature via config; pause purchases if payments are broken; maintenance mode if needed; block exploit paths.
4. Communicate: status message with what is known, impact, next update time; avoid speculation.
5. Fix: patch, test in staging, stage rollout; for client bugs, consider server-side mitigation first.
6. Recover data: restore from backups, reconcile ledgers.
7. Compensate (section 12).
8. Close: confirm metrics normalized; announce resolution.
9. Postmortem: blameless; timeline, root cause, detection gaps, action items with owners and dates (`postmortem` skill).
Principles: contain before fixing; one source of truth; update at promised times even if no news.

## 11. Economy hotfixes
Scenarios: exploit duplicating currency, mispriced item, reward misconfigured, inflation from event.
Procedure:
1. Stop the bleeding: disable the source or item via config.
2. Quantify: how many players, how much currency or item volume, over what window (ledger queries).
3. Decide remediation: leave as is (if minor and removal would hurt more), partially claw back, or reset to a legitimate value. Weigh fairness, trust and cost.
4. Prefer removing the exploit going forward and handling excess via gentle sinks over hard clawbacks that anger honest players; clawback of clearly exploited amounts from flagged accounts is reasonable if terms allow.
5. Communicate transparently.
6. Add tests and monitoring: invariants such as total currency issued vs expected sources; alerts on abnormal balances.
7. Review config review process to prevent recurrence.
Never change odds or prices silently; update disclosures and notes where required (see `monetization`).
Server-authoritative economy limits exploit surface; keep the client from deciding grants.

## 12. Compensation policy
Write a policy before you need it.
| Situation | Typical compensation | Notes |
|---|---|---|
| Short downtime | Small reward gift in the inbox | Scale with duration and impact |
| Lost progress | Restore from backup, plus a gift | Priority for payers whose purchases were lost: restore the purchase |
| Failed purchase | Fix grant or refund guidance | Never leave money taken without goods |
| Event bug | Extend event or grant missing rewards | Keep fairness between affected and unaffected |
| Exploit fix | None, unless honest players were harmed | Communicate the rationale |
Rules:
- Compensation is a currency source; include it in economy tracking.
- Use the in-game mail with a claim window; log claims.
- Be consistent; do not create expectations that every issue yields gifts.
- Premium currency compensation should be modest and finite.
- Document each compensation decision: reason, size, eligibility query.

## 13. Support and community operations
- Support tooling: lookup by player id, purchase ledger visibility, safe tools to restore items, audit logs of support actions.
- Macros for common issues; escalation to engineering with reproducible data.
- Community: a consistent voice, a public known-issues list, patch notes with every change that affects players.
- Feedback loop: tag support themes weekly and feed them to design and live-ops reviews.
- Moderation: clear rules; escalation for harassment; protect minors.

## 14. Monitoring and alerts
Dashboards: DAU, new users, retention by cohort, session counts, revenue, purchase success rate, ad fill and ARPDAU, crash-free rate, ANR rate, server latency and error rate, queue depth, economy totals (currency issued and sunk), support ticket volume.
Alerts: purchase failure rate above threshold, crash rate spike, login failure spike, economy anomaly, config fetch failures, push delivery failures.
Thresholds start from baselines and are tuned to limit false alarms; every alert has an owner and a runbook link.

## 15. Release train and rollbacks
- Regular client releases on a cadence; live content flows through config and content bundles between releases.
- Staged rollouts on the stores (percentage rollouts) with crash monitoring gates; halt the rollout on regressions where the store allows.
- Rollback: server-side config rollback is instant; client rollback is slow, so prefer server-side kill switches.
- Maintain a minimum supported client version and force-update only for critical issues, with a friendly message.
- Coordinate with `store-release` for review lead times, and keep a hotfix lane.

## 16. Volatile facts (as of Oct 2026 - verify)
- Soft-launch market lists change with UA costs, store rules and your target regions; the research notes do not specify an authoritative list. Treat any list from articles as a starting hypothesis and re-derive from section 3 criteria with current data.
- Benchmark retention and monetization numbers differ by source and year and are not reproduced here; take them from `genre-playbooks` or a current benchmark source and record the source and date.
- Firebase Remote Config, A/B Testing, Cloud Messaging are available with free-tier terms; verify at https://firebase.google.com/pricing . Firebase MCP capabilities: https://firebase.google.com/docs/ai-assistance/mcp-server
- Store policies that affect launch (target API levels, Play Billing Library minimum, age-rating questionnaires, state age-verification laws) change; see `store-release` and https://developer.android.com/google/play/billing , https://developer.apple.com/news/upcoming-requirements/ , https://9to5mac.com/2025/11/04/app-store-texas-sb2420-new-apis/
