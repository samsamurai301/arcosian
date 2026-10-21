# Risk, Team and Process

This file covers how to keep a game project alive: a risk register that drives decisions, the risks that recur on mobile and AI-built games, team roles and RACI (including a human plus agent crew), kanban adapted to game work, and rules that avoid crunch. The risk percentages and thresholds are judgement aids, not measured industry constants. Use them to start the conversation, then replace with your own project history.

## Contents
1. Risk register format
2. Scoring and review cadence
3. Top risks: mobile games
4. Top risks: AI-built games
5. Response strategies
6. Roles
7. RACI
8. Kanban for games
9. Crunch avoidance
10. Meetings and communication
11. Checklists

## 1. Risk register format

One row per risk, kept in `templates/docs/risk-register.md` or the project state:

| Field | Meaning |
|---|---|
| ID | R-001 etc. |
| Risk statement | "If X happens, then Y, causing Z" |
| Category | Design, tech, content, market, platform, legal, team, budget, AI |
| Likelihood | 1 to 5 |
| Impact | 1 to 5 (cost to schedule, budget or the player promise) |
| Score | Likelihood x Impact |
| Trigger | The observable sign that it is happening |
| Response | Avoid, reduce, transfer, accept, with a concrete action |
| Owner | One named role |
| Due / next review | Date |
| Status | Open, mitigating, realised, closed |

Rules:
- A risk without a trigger and an owner is a worry, not a risk. Delete it or complete it.
- Write the statement with a consequence, not a topic ("performance" is a topic).
- Keep the register to the top 10 to 15 live risks; archive the rest.
- Record realised risks; they are the data for the next project's likelihood scores.

## 2. Scoring and review cadence

| Score | Class | Action |
|---|---|---|
| 15-25 | Critical | Response funded this sprint; reviewed weekly; may trigger a gate review |
| 8-14 | High | Response scheduled; reviewed at every gate and bi-weekly |
| 4-7 | Medium | Monitor |
| 1-3 | Low | Accept; review at gates |

Cadence:
- Weekly: top five, whether triggers fired, whether responses are on track.
- At every gate: full register review; re-score using evidence.
- After every incident: add or update; was it on the register?

Risk burn-down: plot the sum of scores of open risks per week. A flat line late in production means mitigation is not being funded.

## 3. Top risks: mobile games

| Risk | Typical trigger | Responses |
|---|---|---|
| Core loop is not fun | Testers do not restart; praise is polite | Fun gate before content; cut loop complexity; pivot verb |
| Retention below viability | D1 or D7/D1 under the contract line in soft launch | FTUE rework, meta-systems, live-ops; kill criteria |
| Acquisition cost exceeds payback | CPI rises vs plan; payback never closes | Cheaper channels, organic and creative testing first; kill if the maths does not close |
| Low-end device failure | Frame drops, crashes, thermal throttling on the floor device | Perf budgets from prototype; test floor device weekly (`mobile-performance`) |
| Store rejection or policy change | Review feedback, new SDK or privacy requirement | Pre-flight early (`compliance_preflight.py`); buffer for one rejection cycle; track policy news |
| Platform SDK deadline | Required SDK or API level moves | Calendar the dates from `store-release`; keep toolchain current |
| Ad or analytics SDK problem | Crash, privacy flag, bloat | Isolate behind an interface; test on a clean device |
| Monetisation backlash | Reviews cite pay-to-win or dark patterns | Ethical limits in contract; transparent odds (`monetization`, `legal-ethics`) |
| Content treadmill | Players consume faster than you produce | Live-ops plan funded in advance; systemic content, procedural support |
| Key-person dependency | One person holds unique knowledge | Docs, pairing, agent-readable runbooks |
| Scope creep | Must list grows | Contract change control |
| Cash or time runout | Burn above plan | Gate-linked budget release; kill criteria |
| Single-point server dependency | Backend outage or cost spike | Prefer offline-first; managed services; cost alarms |
| Clone or market saturation | A near-identical title rises | Differentiation statement; speed; community |

## 4. Top risks: AI-built games

| Risk | Typical trigger | Responses |
|---|---|---|
| Plausible but wrong code | Tests absent or trivial; features "work" only on the happy path | Five-gate definition of done; deterministic playthroughs; reviewer agent separate from author |
| Integration decay | Agent lanes drift; interfaces change silently | Frozen contracts and schemas; a named integration owner; CI on every merge |
| Style inconsistency | Asset batches do not match | Style bible and style lock; reference images; batch critique before import (`art-direction`) |
| Licence and provenance | Asset origin unclear; model terms forbid commercial use | Provenance manifest per asset; licence check before ship (`legal-ethics`, `ai-asset-pipeline`) |
| Generated content exceeds review capacity | Backlog of unreviewed assets | Review quota caps generation |
| Cost overrun on API/assets | Spend rising without outputs accepted | Per-phase caps, `gs.py budget`, stop rule at a preset share of cap |
| Over-trust in agent self-reports | "Done" without evidence | Evidence folders; critic agent refutes before approval |
| Model or tool churn | Vendor changes model, API or terms mid-project | Pin versions where possible; abstract behind the gateway; keep exports in open formats |
| Hallucinated facts in docs | Invented stats in pitch or store copy | Source or delete; critic pass |
| Taste drift | The game becomes average because the agents agree with each other | Human taste checkpoints; deliberate references; "what makes this distinct" in each review |
| Security and secrets | Keys in code or prompts | Keys only from environment; hooks guard secrets |
| Store AI disclosure | Policy requires disclosure of generated content or AI features | Track in compliance checklist; disclose where required |
| Platform skepticism about low-effort content | Reviewers or players treat generated content as low quality | Invest in feel, polish and original design; the differentiator is craft |

## 5. Response strategies

| Strategy | Meaning | Example |
|---|---|---|
| Avoid | Remove the cause | Drop real-time multiplayer |
| Reduce | Lower likelihood or impact | Spike a risky shader in week 1 |
| Transfer | Shift to someone else | Use a managed backend or a licensed middleware |
| Accept | Plan for it | Keep a contingency buffer |
| Contingency | Pre-agreed action on trigger | If D1 under the line twice, run kill review |

Decision rule: respond to anything scoring High or Critical; the response must be a dated, owned task on the board.

## 6. Roles

For a small human team with agents, map roles to people and agents explicitly. A person may hold several roles; an agent holds one lane.

| Role | Responsibility | Studio agent |
|---|---|---|
| Owner / product owner | Vision, spend, kill decisions, store submission | Human |
| Game director | Pillars, contract, final design calls | `arcosian:principal` |
| Producer | Plan, gates, risks, budget, reports | `arcosian:producer` |
| Game / systems designer | Loop, rules, economy, progression | `arcosian:game-designer`, `arcosian:systems-designer` |
| Level / content designer | Levels, content pipelines | `arcosian:level-designer` |
| Narrative designer | World, tone | `arcosian:narrative-designer` |
| UX designer | Flows, HUD, onboarding, accessibility | `arcosian:ux-designer` |
| Art director, technical artist | Style, assets, import perf | `arcosian:art-director`, `arcosian:technical-artist` |
| Audio director | Music, SFX, voice | `arcosian:audio-director` |
| Lead engineer | Architecture, standards | `arcosian:lead-engineer` |
| Engineers | Features, engine specifics | `arcosian:gameplay-engineer`, `arcosian:godot-engineer`, `arcosian:unity-engineer` |
| Performance engineer | Budgets, profiling | `arcosian:performance-engineer` |
| QA lead | Test strategy, gates | `arcosian:qa-lead` |
| Player simulator | Persona playtests | `arcosian:player-simulator` |
| Data analyst | Telemetry, cohorts, A/B | `arcosian:data-analyst` |
| Monetisation designer | IAP, ads, offers | `arcosian:monetization-designer` |
| Live-ops manager | Events, calendar | `arcosian:liveops-manager` |
| Market analyst | Market and competitors | `arcosian:market-analyst` |
| Release manager | Builds, signing, store | `arcosian:release-manager` |
| Compliance officer | Policy, privacy, licences | `arcosian:compliance-officer` |
| Critic | Adversarial review | `arcosian:critic` |

Single-human case: the human is owner and taste authority; assign the producer role to an agent to prevent plan drift, but keep spend and submission with the human.

## 7. RACI

R = does the work, A = accountable (one only), C = consulted, I = informed.

| Decision / deliverable | Owner | Director | Producer | Design | Eng | Art/Audio | QA | Data | Compliance |
|---|---|---|---|---|---|---|---|---|---|
| Concept choice | A | R | C | C | C | C | I | C | I |
| Design contract | A | R | C | R | C | C | C | C | C |
| Gate pass/fail | A | R | R | C | C | C | R | C | C |
| Scope cut | A | R | R | C | C | C | I | I | I |
| Style lock | A | C | I | C | I | R | I | I | I |
| Architecture | I | A | I | C | R | I | C | I | I |
| Feature done (five gates) | I | I | C | C | R | I | A | I | I |
| Economy tuning | I | A | I | R | C | I | C | R | C |
| Monetisation design | A | C | I | R | C | I | I | C | R |
| Soft-launch go / no-go | A | R | R | C | C | I | C | R | C |
| Store submission | A | C | C | I | R | I | C | I | R |
| Spend increase | A | C | R | I | I | I | I | I | I |
| Postmortem | I | A | R | C | C | C | C | C | C |

Rule: exactly one A per row. An agent can be R but never A for spend, submission, taste, or kill.

## 8. Kanban for games

Columns: Backlog, Ready, Doing (WIP limited), Review, Playtest, Done (five gates met), plus a blocked marker.

Rules:
- WIP limit per person or lane, typically two items; a blocked item does not count toward freeing capacity.
- Pull from Ready only; Ready items have acceptance criteria, an estimate range, and an owner.
- Done means five gates (static, unit, playthrough, visual, perf) or n/a with a note.
- Classes of service: expedite (crash, store blocker; one at a time), fixed-date (event or deadline), standard, intangible (tooling, refactors; reserve capacity of about 10-20%).
- Track cycle time and throughput; forecast with the distribution, not the average.
- Limit "Review" and "Playtest" columns; they are where agent output queues up.
- Swimlanes: Features, Content, Bugs, Tech debt, Live-ops. Protect the Bugs lane from starvation by a fixed capacity share.

Cadence:
- Daily 10-minute board walk right to left (finish before start).
- Weekly replenishment and risk review.
- Bi-weekly retrospective with one change experiment.

Compare with sprints: sprints suit stable teams and predictable content; kanban suits prototype, live-ops and agent crews where arrivals are irregular. Use sprints with a sprint goal if the human prefers timeboxes; keep the same Done definition.

## 9. Crunch avoidance

Principles:
- Crunch is a planning failure: the schedule assumed capacity that did not exist.
- Overtime has diminishing and often negative returns for creative and debugging work; quality drops, bugs rise, people leave. Treat sustained overtime as a defect in the plan.

Rules:
1. Plan on measured throughput, with buffer, never on heroics.
2. Cut scope at the gate, not at the deadline: scope decisions are cheap early and brutal late.
3. Hard feature freeze at feature complete; hard content freeze at content complete.
4. Define a "last responsible moment" for each decision; hold decisions until then, but not past it.
5. Maintain a visible "if we are late we cut X, Y, Z" list, ordered, agreed in advance.
6. Release windows with buffers: do not schedule submission on the last safe day.
7. One-off crisis (a critical bug) is allowed; two consecutive weeks of overtime triggers a scope or schedule change, not more overtime.
8. For a solo founder, treat energy as capacity: plan three focused blocks a day, not ten hours.
9. Agents do not need rest, but reviewers do: do not use agent availability to justify human overtime.
10. Run a retrospective after every crunch-like period and fix the cause.

Early-warning signs: bug count rising while velocity rises; rework share growing; decisions deferred to "later"; scope unchanged while the burn-down slips.

## 10. Meetings and communication

- Write decisions down in the contract or the progress log; chat is not a record.
- One status format: Goal this week, Done, Blocked, Next, Top risks, Decision needed.
- Playtests are the best meeting: watch players, do not explain the game.
- Demos are on device, with real data.
- Escalate by changing a gate, not by sending a longer message.

## 11. Checklists

Weekly producer checklist:
- [ ] Board reviewed against WIP limits
- [ ] Top five risks checked for triggers
- [ ] Burn-down vs plan updated
- [ ] Playtest done on latest build
- [ ] Spend vs cap checked (`gs.py budget`)
- [ ] Decisions needed from the owner listed

Pre-gate risk checklist:
- [ ] Every Critical and High risk has an owner and a dated action
- [ ] New risks from the last phase added
- [ ] Realised risks recorded with cause
- [ ] Contingency triggers re-checked

Team health checklist:
- [ ] No role without a named holder
- [ ] No person over capacity for two consecutive weeks
- [ ] Rework rate trending down
- [ ] At least one retro action completed
