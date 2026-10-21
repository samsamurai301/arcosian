# Lifecycle and Planning

This file defines the phases of a mobile game project, the gate and kill criteria for each, and the planning tools a producer needs: scoping, MoSCoW, estimation, milestones, and how to plan when most implementation is done by AI agents. Thresholds given are starting points; calibrate them to genre and budget and freeze them in the design contract before each phase begins. Numbers marked "heuristic" are practitioner rules of thumb, not published standards.

## Contents
1. Phase model overview
2. Phase detail: goal, deliverables, gate, kill criteria
3. Scoping and the design contract
4. MoSCoW with a budget
5. Estimation methods
6. Milestones and schedules
7. Planning for an AI-agent team
8. Worked examples
9. Checklists

## 1. Phase model overview

| Phase | Question it answers | Typical length (small team, heuristic) | Output |
|---|---|---|---|
| 0. Concept | Is there a worthwhile idea and a gap? | days | Concept card, market scan, one-pager |
| 1. Prototype | Is the core loop fun? | days to 2 weeks | Playable grey-box |
| 2. Vertical slice | Can we hit final quality and cost at one minute of play? | 2-6 weeks | Slice build, measured cost per minute |
| 3. Production | Can we build all of it on time? | the bulk | Feature-complete, content-complete builds |
| 4. Soft launch | Do real players stay and pay? | 4-8 weeks | Retention and monetisation data |
| 5. Launch | Is the release safe and marketed? | 2-4 weeks | Store release |
| 6. Live | Does the game keep growing profitably? | open-ended | Live-ops calendar, patches |

Rules that apply to all phases:
- Every phase starts with a written goal, a gate threshold and a kill or pivot action.
- A phase may end early if the gate is passed; it may not be extended more than once without a kill review.
- A failed gate triggers a decision, never silent continuation.
- Gate evidence is a build or data. A document alone is never evidence for phases 1 and later.

## 2. Phase detail

### Phase 0: Concept
Goal: choose one concept worth prototyping.
Deliverables: concept card (verb, fantasy, loop sketch, audience, differentiator), market scan (see `market-intel`), one-page design contract draft, top-5 risks.
Gate (all must hold):
- The core verb and the 30-second loop can be described in two sentences a stranger repeats back correctly.
- At least three comparable live games exist (proves demand) and you can state what you do differently in one sentence (proves a gap).
- The Must list is plausibly buildable by the team inside the budget.
Kill criteria: no comparable titles and no theory of why that is good news; the differentiator is only graphics or only theme; the team cannot name the target player.
Human checkpoint: the owner picks the concept; agents do not.

### Phase 1: Prototype
Goal: find the fun fast. Build the loop with placeholder art in hours to days, then iterate.
Deliverables: playable build on a real device, a 10-minute scripted test plan, notes from at least 5 outside players.
Gate (starting thresholds, heuristic):
- Most testers want another go without being asked; look for unprompted "one more" behaviour rather than polite praise.
- The first moment of fun happens inside about 90 seconds (see the time-to-fun note in `player-analytics`).
- Input feels good on a phone: one-handed where the genre allows, no mis-taps on core controls.
- The loop has depth signal: testers form strategies or want to improve, not only repeat.
Kill or pivot criteria:
- Three iterations (each addressing the top tester complaint) fail to move the gate metric: pivot the verb or kill.
- Fun depends on content volume that does not exist yet: the loop is not self-sufficient; pivot.
- The loop only works with complex input that mobile cannot support: change the control scheme or kill.
Iteration rule: change one thing per test, write the hypothesis first ("if the first level teaches the booster, second-session rate rises").

### Phase 2: Vertical slice
Goal: one representative minute (or one level, one battle, one run) at final quality across art, audio, UI, feel, performance, telemetry and monetisation touchpoints.
Deliverables: slice build on a low-end and a high-end device; measured person-days per minute of final content; the performance report; the first draft of the content pipeline; updated estimates for the whole game.
Gate:
- Art and audio direction signed off by the human (style checkpoint).
- Frame rate, memory, load time and thermal behaviour inside budget on the target low-end device (see `mobile-performance`).
- Cost per minute of content multiplied by planned content minutes fits the budget with a buffer. If the product exceeds the budget, scope drops; quality does not.
- Outside players rate the slice's clarity and appeal at or above the bar in the contract.
Kill criteria: cost per content minute is more than the budget allows even after cutting content in half; the slice needs a technique that blows the performance budget on the target tier; the human owner dislikes the style and no cheaper path exists.

### Phase 3: Production
Goal: build all Musts, then Shoulds, behind feature-complete and content-complete milestones.
Sub-milestones:
- Feature complete: all Must features exist and are playable; no new features are accepted after this point.
- Content complete: all planned levels, items, events for launch exist, unpolished allowed.
- Beta candidate: bug-fix only; telemetry, consent, crash reporting and store assets in place.
Gate per milestone: five-gate definition of done for every feature (static, unit, playthrough, visual, perf; see `qa-testing`), burn-down of the Must list on schedule, risk register reviewed.
Kill criteria: Must list burn-down shows a finish date later than the planned date by more than 30% twice in a row (heuristic) with no scope to cut; a critical dependency (SDK, platform policy, licence) fails and has no substitute.
Production rhythm: weekly playable build, weekly playtest, bi-weekly scope review.

### Phase 4: Soft launch
Goal: replace assumptions with measured retention, session length and early monetisation before spending on scale.
Deliverables: soft-launch plan (`templates/docs/soft-launch-plan.md`), instrumented build, test-market list, dashboards, A/B test plan.
Gate: thresholds written in the contract before launch, expressed as retention at D1/D7/D30, crash-free sessions, early revenue per active user, and acquisition cost against the payback you can afford. Public benchmark medians are reported in `market-intel` and `player-analytics`; they differ by source and genre, so use your own genre cohort or the practitioner "viability screen" noted there as a starting hypothesis, not a truth.
Diagnostics: if D1 is weak, fix the first session and tutorial; if D7/D1 ratio is weak, fix days 2-5 engagement; if D30 is weak, fix meta and live-ops; if monetisation is weak but retention strong, fix offers and economy (`economy-design`).
Kill criteria: after two improvement cycles (each a build, a cohort, a read-out) the core metrics stay below the kill line; or the payback maths never closes at any plausible acquisition cost. Killing here is cheap compared with scaling a losing game.

### Phase 5: Launch
Goal: ship safely; no submission without explicit human approval.
Deliverables: signed builds, store listing and assets, compliance pre-flight pass, privacy and age answers, a rollback plan, staged rollout settings, support and moderation plan.
Gate: compliance pre-flight clean; crash-free rate at the planned bar for two weeks of beta; store-review buffer scheduled (see `store-release`).
Kill/hold criteria: unresolved policy or licence blocker; severe crash or data-loss bug; analytics or consent not working.

### Phase 6: Live
Goal: grow lifetime value profitably. Plan a 90-day content calendar before launch; see `liveops`.
Gate (quarterly review): cohort curves flat or improving, event ROI positive, support load manageable, content pipeline sustaining cadence.
Sunset criteria: define in advance (revenue below running cost for N months, player trend, platform policy). A planned sunset with notice beats an abandoned game.

## 3. Scoping and the design contract

The design contract is a one-page document, schema-validated (`design-contract.schema.json`), containing:
- Player promise (one sentence), target player, platforms and device floor.
- Pillars (3 maximum) each with an observable test.
- Core loop (verb, challenge, reward) and session length.
- Must / Should / Could / Won't lists (see section 4).
- Monetisation model and ethical limits.
- Performance and size budgets.
- Gate thresholds and kill criteria per phase.
- Budget (people-time and cash including asset and API spend) and target dates.
Change control: any addition requires removing equal-sized scope or an explicit budget increase signed by the owner; log it with `gs.py progress`.

Scoping heuristics:
1. Count content in player-minutes, not features. Players consume minutes.
2. For each feature ask: which pillar does it serve, and what happens if we ship without it? If the answer is "nothing much", it is not a Must.
3. Prefer one deep system over three shallow ones.
4. Cut multiplayer, user-generated content, chat and cross-platform saves unless they are the pillar; each carries operations cost that outlives development.
5. Cut anything that needs a server unless a hard requirement exists; the cheapest backend is none.
6. Write a Won't list; a visible Won't list defuses most feature requests.

## 4. MoSCoW with a budget

| Class | Definition | Budget share of capacity (heuristic) | Rule |
|---|---|---|---|
| Must | Game is not shippable or not the game promised without it | up to about 60% | Finite list, frozen at feature-complete |
| Should | Important, workaround exists | about 20% | First to slip |
| Could | Nice to have | remainder as buffer | Pulled in only when Musts are done |
| Won't (this release) | Explicitly out | 0% | Written down, revisited at the next release |

Procedure:
1. List candidate features with a one-line value statement and a range estimate.
2. Sum Must estimates using the likely value; compare with 60% of capacity. If over, demote or shrink Musts.
3. Rank Shoulds by value per unit cost.
4. Review at each gate; scope moves down the list, never up, without a budget change.
Capacity is people-time after meetings, review, device testing and sickness; use the actual throughput from the last 4 weeks, not the theoretical headcount.

## 5. Estimation methods

| Method | Use when | How |
|---|---|---|
| Reference class | Always first | Use actuals of a comparable finished item including review and test |
| Three-point | Moderate uncertainty | Best, likely, worst; plan on (best + 4 x likely + worst) / 6, communicate the range |
| Spike then estimate | Unknown technology | Time-boxed experiment (1-2 days), then estimate |
| Per-minute content cost | Content-heavy games | Slice cost per minute x planned minutes x ramp factor |
| T-shirt sizing | Early backlog | S, M, L mapped to ranges you calibrate from history |
| Throughput forecasting | Kanban in production | Use cycle-time distribution of the last 20 items to forecast |

Rules:
- Never estimate without listing assumptions and the biggest unknown.
- Estimates cover done (five gates), not code written.
- Tag first-of-kind work; apply a bigger contingency (often 1.5x to 2x of the likely; heuristic) than repeat work (about 1.1x to 1.3x).
- Re-estimate at every gate with measured data; publish the delta.
- Do not convert agent-generated speed into promises: measure agent throughput per lane on the slice, include review time.

Worked formula, content: planned minutes M, slice cost per minute C (person-days at final quality), pipeline improvement factor f (0.6 to 1.0, only after you have measured a second batch), contingency k. Content cost = M x C x f x k.
Example: 90 minutes of planned puzzle content (count real play minutes, not level counts), slice cost 0.4 person-days per minute, f = 0.8, k = 1.3 gives 90 x 0.4 x 0.8 x 1.3 = about 37 person-days. Show the range by varying f and k.

## 6. Milestones and schedules

Milestone list for a typical mobile project (adapt):
| Milestone | Definition | Evidence |
|---|---|---|
| M0 Greenlight | Concept gate passed | Contract v1 signed |
| M1 Fun proven | Prototype gate passed | Tester notes, build |
| M2 Slice | Slice gate passed | Slice build, cost per minute |
| M3 Feature complete | All Musts playable | Feature list all green except polish |
| M4 Content complete | All launch content in | Content checklist |
| M5 Beta | Fix-only; compliance pre-flight started | Crash-free data |
| M6 Soft launch | Real cohorts | Dashboards |
| M7 Launch | Store release | Approved listing |

Scheduling rules:
- Work backwards from fixed external dates (events, seasons, platform deadlines) and place gates inside them.
- Put a schedule buffer of 15-25% in front of each external deadline (heuristic).
- Schedule store review, signing, certificate and policy tasks explicitly; they have long lead times and no parallel substitute.
- Do not schedule two high-risk items in the same sprint.
- Track the critical path: usually human decisions (style, fun, approval), then integration, then device testing.

## 7. Planning for an AI-agent team

What changes:
- Code, first-draft assets, docs and tests become cheap; review, integration, taste and device verification do not.
- Failure modes: confident wrong code, inconsistent style across batches, hidden licence and provenance issues, over-generation, budget burn on API calls.

Lane design:
1. Define lanes by disjoint file ownership (gameplay, UI, art, audio, data/economy, build/CI). Two agents never edit the same file concurrently.
2. Each lane has an owner agent, an inputs list, a definition of done and a review gate.
3. Shared contracts (schemas, interfaces, event taxonomy) are written first by one agent and frozen; lanes consume them.
4. Integration is a scheduled task with an owner, not a side effect.

Human checkpoints (never delegated):
- Concept choice and style lock.
- Fun verdict after each playtest.
- Spend increases, store submission, legal and ethics calls.

Throughput plan:
- Measure on the slice: tasks completed per lane per day to the five-gate standard, rework rate, review minutes per task.
- Cap generation by review capacity: if the human reviews 20 asset candidates per day, do not generate 200.
- Track API and asset spend with `gs.py budget`; set a cap per phase and a stop rule at 80% of cap.
- Use a critic pass (`arcosian:critic`) on claims in gate evidence.

Cadence:
- Daily: agents work the board; the human unblocks decisions.
- Twice weekly: playable build and human playtest.
- Weekly: gate-style review of the Must list and risk register.

## 8. Worked examples

### Example A: scope cut at the slice gate
Slice measured at 0.9 person-days per minute against a planned 0.5. Planned content: 120 minutes. Budget allows 60 person-days of content. At 0.9, 120 minutes costs 108 days. Options: (1) halve content to 60 minutes (54 days); (2) invest 10 days in a better pipeline hoping to reach 0.5 (risky: unmeasured); (3) reduce fidelity (style change; needs a human checkpoint). Recommendation: option 1 now, option 2 as a parallel bounded experiment with a measurable target; revisit at the next gate. Do not do both by assuming the pipeline win.

### Example B: kill review at soft launch
Cohorts after two cycles: D1 below line both times, D7/D1 ratio low, session length acceptable. Diagnosis: first-session drop. Cycle 1 changed the tutorial; cycle 2 changed the first five levels; both moved D1 slightly, neither crossed the line. The payback maths needs acquisition cost below an amount that the channel has never delivered. Decision: kill, write the postmortem, extract the pipeline and tools for reuse. This is a success of the process: bounded spend, clear data.

### Example C: AI-built game timeline sketch (illustrative, not a promise)
Week 1: concept and prototype. Week 2: prototype iterations and tests. Weeks 3-5: vertical slice with style lock and perf run. Weeks 6-12: production with weekly builds. Weeks 13-14: beta and compliance. Weeks 15-18: soft launch. Treat these as illustrative ranges; re-plan with measured throughput after the slice.

## 9. Checklists

Gate-readiness checklist:
- [ ] Threshold and kill action written in the contract
- [ ] Build on a physical device, not an editor only
- [ ] Evidence folder populated (`gs.py evidence-dir`)
- [ ] Risk register updated
- [ ] Human checkpoint scheduled
- [ ] Estimates refreshed with measured data

Scope-cut checklist:
- [ ] Is it a Must? Prove it by the pillar test
- [ ] Is there a cheaper variant (smaller content, scripted instead of simulated)?
- [ ] Does the cut break an economy or progression dependency? Check `economy-design` and `progression-difficulty`
- [ ] Updated the contract and feature list

Pre-production kickoff checklist:
- [ ] Contract signed
- [ ] Device matrix chosen
- [ ] Analytics plan drafted
- [ ] Budget and caps set
- [ ] Style and audio direction process defined
- [ ] Licence and provenance policy set (`legal-ethics`)
