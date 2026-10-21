# The House Doctrine, Operationalized

The `arcosian` plugin follows a ten-point doctrine, in priority order, as stated in the plugin's mission. A doctrine is only real if it changes decisions, so this file expands each principle into: **what it means** (and what it does not), **how the plugin enforces it** (contract fields, gates, hooks, scripts, agents, workflows and skills), **decisions it settles** (worked cases that should never be re-argued), and **failure signs** (observable symptoms that the principle is being ignored). It ends with the conflict-resolution rules for when principles collide, a milestone audit checklist, and doctrine-health metrics. Where a mechanism belongs to another part of the plugin, it is named exactly as the plugin's architecture names it; details of how those parts work live in their own skills.

## Contents

1. The doctrine at a glance
2. Principle 1 — Player first
3. Principle 2 — Find the fun fast
4. Principle 3 — Verify by playing
5. Principle 4 — Data-informed, not data-driven
6. Principle 5 — Scope ruthlessly
7. Principle 6 — Mobile-native
8. Principle 7 — Readability over detail; juice everything the player touches
9. Principle 8 — Ethical monetization
10. Principle 9 — Own the output
11. Principle 10 — Automatic between taste checkpoints
12. When principles collide: priority rules and worked cases
13. Milestone doctrine audit
14. Doctrine-health metrics

---

## 1. The doctrine at a glance

| # | Principle | One-line test | Primary enforcers |
|---|---|---|---|
| 1 | Player first | Can you name the player, the moment and the feeling this decision creates? | `player_fantasy`, pillars, `critic`, `player-simulator` |
| 2 | Find the fun fast | Is the core loop playable and judged before content and polish? | `concept-tournament`, fun checkpoint, `features.json` priorities and dependencies |
| 3 | Verify by playing | Does evidence on disk prove each gate? | Five gates, `gs.py feature pass`, `pre_tool_guard.py`, `stop_gate.py`, `task_gate.py` |
| 4 | Data-informed, not data-driven | Was the hypothesis written before the data was read? | Event taxonomy, `ab_test.py`, `retention_ltv.py`, `data-analyst` |
| 5 | Scope ruthlessly | Does every item trace to a pillar, and is the won't list real? | `scope.must/should/wont`, `kill_criteria`, `producer` |
| 6 | Mobile-native | Does it work one-handed, in two minutes, on a low-end phone, after an interruption? | `perf_budgets`, `min_spec`, `perf` gate, `perf_budget.py`, `performance-engineer` |
| 7 | Readability over detail; juice the touched | Can a player read the screen at a glance, and does every touch answer back? | `visual` gate, style bible, `art-director`, `game-feel` |
| 8 | Ethical monetization | Would you show this offer to a 13-year-old's parent? | `monetization.ethics`, `compliance-officer`, `compliance_preflight.py` |
| 9 | Own the output | Could the user rebuild and ship this without us or any single vendor? | Templates, asset manifest, `licence_check`, `licence_allowlist` |
| 10 | Automatic between taste checkpoints | Is a human being asked only about style, fun or store submission? | Human checkpoints, `pre_tool_guard.py` ask rules, `ship` process |

Priority order matters: when two principles conflict, the lower number wins unless section 12 lists an explicit exception.

---

## 2. Principle 1 — Player first

**What it means.** Every decision is justified by the experience it creates for a specific player. "Player first" is not "do what players say" (players are good at spotting problems and poor at prescribing fixes, as Mark Rosewater puts it) and not "maximize engagement". It means the player experience is the unit of value, and other goals (revenue, technical elegance, schedule) are means to it or constraints on it.

**Player-experience statement (use in features, mechanics and reviews).**

```
When <segment from meta.target_audience.segments> <does action> in <situation>,
they should feel <aesthetic / emotion>, evidenced by <observable behaviour or metric>.
```

*Example:* "When a lapsed casual player opens the game on a bus, they should feel competent within 30 seconds, evidenced by clearing level 1 without a hint in at least 90% of persona runs."

**How the plugin enforces it.**

| Mechanism | Where | What it enforces |
|---|---|---|
| `player_fantasy`, `meta.pillars` (3–5), `meta.target_audience` | `contract.json` | A written player promise every review checks against |
| `player_fantasy`, `aesthetics` (MDA targets) | `mechanic-card.schema.json` | Mechanics are justified by the experience they create |
| Player-observable acceptance criteria | `features.json` `acceptance` | Done means a player-visible outcome, not "code merged" |
| Persona playtests | `player-simulator` agent, `/arcosian:playtest-sweep` | Fresh eyes without designer knowledge |
| Adversarial review | `critic` agent | Claims about fun and quality must survive refutation |
| Multi-discipline review | `/arcosian:design-review` workflow | Pillars checked from design, UX, economy, ethics, tech, market and scope angles |

**Decisions it settles.**
- *Unskippable 8-second logo sequence on every launch?* No. It serves the brand, not the player; show it once at most.
- *Refactor the rendering layer to a newer pattern?* Only if it changes something the player can perceive (frame pacing, load time, battery), or unblocks a player-facing feature.
- *Copy a competitor feature because "they all have it"?* Only after writing the player-experience statement it serves in *our* game; if none can be written, it goes to `scope.wont`.

**Failure signs.** Features justified by "competitors have it", "it's cool tech" or "it will lift ARPDAU" alone; acceptance criteria with no player-observable outcome; pillars that never appear in review reports; playtest findings closed without a fix or a reason.

---

## 3. Principle 2 — Find the fun fast

**What it means.** Prototype the core loop in hours, not weeks. Order of work: core loop, then content, then polish. A loop that is not fun with grey boxes will not become fun with final art.

**House time boxes (defaults; the `principal` may change them per project).**

| Stage | Time box | Exit question |
|---|---|---|
| Feel prototype (one verb) | One working session | Is the verb pleasant with no goal? |
| Loop prototype | One to two days | Do players start another loop unprompted? |
| Iteration budget | Three loop iterations | Still no fun signal after three? Pivot the hook or kill |
| Vertical slice | Only after the fun checkpoint | Can we reach target quality? |

**How the plugin enforces it.**

| Mechanism | Where | What it enforces |
|---|---|---|
| Concept generation and elimination | `concept-lab` skill, `/arcosian:concept-tournament` workflow, `concept.schema.json` scores | Many concepts, few survivors, scored on `fun_potential`, `feasibility` and `agent_buildability` among others |
| Fun checkpoint | Human sign-off (principle 10) | No content or final art before a human says the loop is fun |
| Priorities and dependencies | `features.json` (`priority`, `depends_on`); `gs.py feature next` picks the highest-priority `todo` whose dependencies pass | Content features depend on core-loop features, so they cannot be scheduled first |
| Placeholders | Asset manifest `placeholder: true`; gateway mock mode (`GS_MOCK=1`, `dry_run`) | Art never blocks the loop; placeholder files are valid |
| Tier | `config.tier` / `scope.tier` = `prototype` | Signals what quality bar applies |
| Kill criteria | `contract.kill_criteria` | The stop condition is written before the work starts |

**Decisions it settles.**
- *Generate final art for the prototype?* No: placeholders until the fun checkpoint, then the style is locked (principle 10) before production assets.
- *Build 50 levels so the prototype "feels like a real game"?* No: three to five levels that exercise the loop; the rest is content.
- *Write a 30-page design document first?* No: a one-page contract (principle 5) and a playable build.

**Failure signs.** Budget ledger entries for paid asset generation before any core-loop feature passes its `playthrough` gate; content features `in_progress` while a P0 core-loop feature is `todo`; a prototype older than its time box with no fun decision recorded in `progress.md`.

---

## 4. Principle 3 — Verify by playing

**What it means.** Nothing is "done" until it has been played deterministically, measured against the perf budget and visually critiqued. "It compiles" and "the agent says it works" are not evidence.

**How the plugin enforces it.**

| Mechanism | Where | What it enforces |
|---|---|---|
| Five gates (`static`, `unit`, `playthrough`, `visual`, `perf`) | `features.json` `gates`, `evidence`, `gate_notes` | `passes: true` only when every gate is `pass` or `n/a`, every `pass` has evidence on disk, every `n/a` has a note |
| Gate recording | `gs.py feature gate F001 <gate> <result> --evidence PATH --note TEXT` (result `pass`, `fail` or `n/a`), `gs.py feature pass F001`, `gs.py evidence-dir F001` | Evidence lives under `.gamestudio/evidence/<FEATURE-ID>/` |
| Write guard | `pre_tool_guard.py` on `.gamestudio/features.json` | Denies marking a feature done or passing without `check_feature_pass` |
| Stop and task guards | `stop_gate.py`, `task_gate.py` | Blocks finishing while a done feature fails its gates, or completing a task for a non-passing feature |
| Deterministic playthroughs and bots | Engine-template playtest runners (Godot and Unity; see `qa-testing`), `playtest-report.schema.json` | Scripted input with state assertions; bot runs for difficulty and softlocks |
| Perf check | `perf_budget.py --report PATH --contract PATH` against `technical.perf_budgets` | Budgets checked on the reference device tier |
| Visual critique | `visual` gate: structural UI checks first, then model-based review; `art-director`, `critic` | Screenshots cleared against a rubric |
| QA ownership | `qa-lead` agent, `qa-testing` skill, `/arcosian:playtest` | Test strategy, regression and gate discipline |

**Decisions it settles.**
- *The feature compiles and unit tests pass; mark it done?* No: `playthrough`, `visual` and `perf` still need evidence or a justified `n/a`.
- *A pure data feature (an event table) has nothing to look at?* `visual: n/a` with a `gate_notes` entry is correct.
- *The bot found a softlock in 1 of 200 runs?* That is a `blocker` finding, not noise, until the seed reproduces cleanly without it.

**Failure signs.** Evidence paths that point to missing or stale files; `n/a` used to dodge hard gates; playthroughs that only script the happy path; perf measured in the editor or on a high-end phone only; visual reviews with no screenshots attached.

---

## 5. Principle 4 — Data-informed, not data-driven

**What it means.** Form a hypothesis from player understanding and design theory, predict the effect, then use telemetry to confirm or refute. Data refines decisions; it does not replace judgement, and it never overrides principles 1 and 8.

**Hypothesis template (store with the feature or test plan).**

```
We believe <change> will <increase|decrease> <primary metric> by <expected size>
for <segment>, because <player-experience reason>.
Guardrails: <metrics that must not get worse, e.g. D7, crash rate, review score>.
Test: <A/B | before-after | simulation>; minimum sample <n per arm> (from ab_test.py size).
If refuted: <what we will do>.
```

**How the plugin enforces it.**

| Mechanism | Where | What it enforces |
|---|---|---|
| KPI targets | `contract.analytics.kpi_targets` (`d1`, `d7`, `d30`, `session_len_sec`, `sessions_per_day`, `arpdau_usd`, `payer_conversion`) | Targets set before launch, not after |
| Event taxonomy | `event_taxonomy.py generate --contract PATH --out PATH`; `event-taxonomy.schema.json` | Instrumentation designed from the contract, with KPIs per event |
| Test sizing and analysis | `ab_test.py size`, `ab_test.py analyze`, `ab_test.py sequential` | No underpowered tests; planned interim looks instead of peeking |
| Retention and LTV | `retention_ltv.py fit`, `retention_ltv.py ltv` | Curves and value from data, not anecdote |
| Pre-launch simulation | `economy_sim.py`, `difficulty_curve.py`, `match3_sim.py`, `puzzle_solver.py` | Hypotheses tested by simulation before players exist |
| Ownership | `data-analyst` agent, `player-analytics` skill, `/arcosian:operate` | Cohorts, funnels and A/B reads |

**Decisions it settles.**
- *Test seven button colours in soft launch with 3,000 installs a week?* No: the sample cannot detect realistic effects; decide by design principles and test something with a large expected effect.
- *Data shows more interstitials raise ARPDAU?* Not sufficient. Check guardrails (D7, session length, reviews) and principle 8 caps first; revenue gains that hurt retention or trust are rejected.
- *A metric moved but no hypothesis predicted it?* Treat it as a new hypothesis to test, not as a conclusion.

**Failure signs.** Tests launched without a written hypothesis or guardrails; results read daily and stopped at the first significant-looking value; metric definitions changed after results arrive; decisions justified by a single dashboard number; analytics events added ad hoc outside the taxonomy.

---

## 6. Principle 5 — Scope ruthlessly

**What it means.** A one-page design contract, explicit must/should/won't lists, and pre-committed kill criteria. Scope is the variable that moves when time or quality is threatened; gates are not.

**Scope heuristics (house defaults).**
- Every `must` item traces to a pillar; an item that traces to none moves to `should` or `wont`.
- A healthy `wont` list is at least as long as the `must` list: if nothing has been refused, nothing has been decided.
- A prototype has a handful of must items (roughly one screen); a soft-launch build may have more, but each still traces to a pillar.
- Kill criteria are measurable and dated ("D1 below 25% after 2,000 organic installs in soft launch", "no fun sign-off after three loop iterations").

**How the plugin enforces it.**

| Mechanism | Where | What it enforces |
|---|---|---|
| Design contract | `contract.json` (`scope.tier`, `scope.must`, `scope.should`, `scope.wont`, `kill_criteria`, `risks`); one-page GDD in `templates/docs/` | Scope written down and versioned |
| Priorities | `features.json` `priority` (`P0`, `P1`, `P2`) | P0 first; P2 cannot block a milestone |
| Scope owner | `producer` agent, `production` skill | Milestones, risks, cuts |
| Reviews | `/arcosian:design-review` (scope pass), `critic` | Challenges scope creep and unfounded musts |
| Kill review | `concept-tournament`, soft-launch reviews in `operate`, `postmortem` | Kill criteria actually evaluated, and kills documented |

**Decisions it settles.**
- *Add real-time multiplayer to a single-player puzzle game "for retention"?* `wont` unless a pillar requires it; async social (leaderboards, ghost replays) is the scoped alternative.
- *Milestone at risk?* Move items from `should` to `wont` (and P1 to P2). Never relax a gate.
- *Kill criterion hit?* Kill or pivot as pre-committed; reopening requires a new contract version with new criteria, recorded in `progress.md`.

**Failure signs.** An empty or token `wont` list; features with no pillar trace; P2 work in progress while P0 features fail gates; a contract that has grown into a multi-page design bible; kill criteria nobody has evaluated at the date they name.

---

## 7. Principle 6 — Mobile-native

**What it means.** Design for the phone first, not as a port: thumb reach, one-handed play where possible, 1–5 minute sessions, constant interruptions, low-end devices, battery and heat, download size, intermittent connectivity.

**Mobile-native checklist.**

| Constraint | Requirement | Where checked |
|---|---|---|
| Reach | Primary actions in the lower thumb zone; no critical control in top corners for portrait | `ux-designer`, `mobile-ux`, `visual` gate |
| Input | One thumb for core actions in casual genres; no precise multi-touch unless the genre demands it | Mechanic-card `mobile_fit.one_hand` |
| Session | Core loop completes in the `session_length_target_sec`; progress saved on every meaningful step | Contract; playthrough timing |
| Interruption | App backgrounding pauses safely; state survives OS kill and restore | Playthrough scripts with pause/resume steps; engine templates |
| Low-end | Budgets hold on the low tier in `technical.min_spec` | `perf` gate on the reference low-tier device |
| Thermal and battery | No throttling over a sustained scenario | `thermal` start/end and `duration_sec` in a `perf-report.schema.json` report |
| Size and start | Within `download_mb` and `cold_start_sec` budgets | `perf_budget.py` |
| Connectivity | Core play works offline unless the design is inherently online | Contract `technical.backend`, `multiplayer` |

**How the plugin enforces it.** Contract fields (`orientation`, `session_length_target_sec`, `technical.min_spec`, `technical.perf_budgets` with `fps_target`, `frame_ms_p95`, `memory_mb`, `download_mb`, `cold_start_sec`), mechanics' `mobile_notes`, mechanic-card `mobile_fit`, the `perf` gate with `perf-report.schema.json` evidence, `perf_budget.py`, the `performance-engineer` agent, the `/arcosian:optimize` process and the `mobile-performance` and `mobile-ux` skills.

**Decisions it settles.**
- *A twin-stick scheme plus four action buttons for a casual audience?* No: redesign to one-thumb input with auto-actions, as Habby and Tencent's mobile translations do.
- *Puzzle game at 30 fps on low-end devices?* Acceptable if frame pacing is stable and the budget says so; battery and heat matter more than a frame-rate number for turn-based play.
- *A 600 MB first download for a casual game?* No: ship a small core and stream or download additional content on demand within the `download_mb` budget.

**Failure signs.** Perf reports only from the editor or a flagship phone; playthrough scripts with no pause/resume steps; text or touch targets that need zooming; sessions that cannot end cleanly before two minutes; thermal throttling in sustained scenarios.

---

## 8. Principle 7 — Readability over detail; juice everything the player touches

**What it means.** The player must read the game state at a glance on a small screen: who they are, what to do, what threatens them, what they just earned. Detail that competes with that is removed. Every element the player touches answers back with feedback proportional to its importance.

**Readability tests.**
1. *Thumbnail test:* scale a gameplay screenshot to 25%. The player character, the goal and the threats must still be distinguishable.
2. *Silhouette test:* fill each actor black; key actors remain identifiable.
3. *Colour-independence test:* run a colour-blindness simulation; no information is carried by hue alone.
4. *Value-contrast test:* foreground interactive elements have clearly higher contrast than backgrounds.
5. *Feedback inventory:* list every touchable element and its feedback tier (see the juice budget in `schools-of-thought.md` section 8); none is silent.

**How the plugin enforces it.** The style bible (`art_direction.bible_ref`) sets palette, value structure and silhouette rules; `image_post.py check` and `image_post.py palette` support automated checks on assets; the `visual` gate runs structural UI checks and then a model-based critique against the rubric; the `art-director`, `technical-artist` and `critic` agents review; `game-feel`, `art-direction` and `technical-art` hold the craft knowledge. Juice cost is bounded by principle 6 budgets.

**Decisions it settles.**
- *A richer, more detailed background?* Only if foreground contrast and readability tests still pass; otherwise simplify it.
- *Screen shake on every tap?* No: shake is a tier 3 effect for big moments, with a reduce-motion toggle.
- *Particle-heavy effects drop the low tier below budget?* Scale effects by device tier; readability and budget win over spectacle.

**Failure signs.** Busy backgrounds with the same value range as actors; friend and foe in similar hues; buttons with no pressed state; celebration effects that hide the next decision; juice added late as a "polish pass" instead of per feature.

---

## 9. Principle 8 — Ethical monetization

**What it means.** Monetize only in ways the player would consider fair if they fully understood them. No dark patterns, transparent odds, and specific protection for minors. Revenue is a constraint to satisfy, not the goal that overrides players.

**House red lines (default `monetization.ethics` entries).**
1. Odds and pity published for every randomized paid item, before purchase.
2. No paid randomness for minors in jurisdictions that restrict it; age-appropriate behaviour driven by `meta.target_audience.age_min` and `config.storefronts`.
3. No fake urgency: timers do not silently reset; scarcity is real.
4. No pay-to-win against other humans in competitive modes.
5. Real-money prices visible alongside premium-currency prices.
6. Ads never interrupt active play; rewarded ads are opt-in; interstitials respect `min_interval_sec` and `first_after_sec`.
7. No post-loss offer targeting for minors, and post-loss offers capped for everyone.
8. No confirmshaming, nagging or hidden auto-renewals; restore purchases is easy to find.
9. Streak and daily systems include recovery; missing a day never wipes large progress.

**How the plugin enforces it.** `contract.monetization` (`iap`, `ads`, `pass`, `ethics`); the `monetization-designer` (designs within the red lines) and `compliance-officer` (checks store policy, privacy, age, loot-box law, licences, AI disclosure) agents; `compliance_preflight.py --project DIR --platform ios|android|all`; `gacha_calc.py` for odds and pity; the `monetization` and `legal-ethics` skills; and the design-review ethics pass.

**Decisions it settles.**
- *A starter-pack countdown that restarts each login?* No: fake urgency. A one-time 48-hour offer that truly expires is acceptable.
- *A character gacha with pity?* Allowed with published odds and pity, age gating where required, and a model of expected cost to the guarantee from `gacha_calc.py` reviewed by the `compliance-officer`.
- *Revive with a rewarded ad?* Allowed: opt-in, value-aligned, does not interrupt play.
- *Raising interstitial frequency because A/B shows higher ARPDAU?* Only within the contract caps and only if retention guardrails hold (principle 4 does not override principle 8).

**Failure signs.** Monetization KPIs used as the only success measure for features; offers triggered by loss events for young segments; odds missing or hidden behind several taps; premium currency bundles priced so that leftovers force another purchase; reviews mentioning "pay to win" or "scam".

---

## 10. Principle 9 — Own the output

**What it means.** The user owns native builds and source they can rebuild without the plugin or any single vendor. No runtime lock-in, licences checked for every asset, secrets never in files.

**How the plugin enforces it.**

| Mechanism | Where | What it enforces |
|---|---|---|
| Engine templates and CI | `templates/godot-starter/`, `templates/unity-starter/`, `templates/ci/` (GitHub Actions, fastlane, Codemagic) | Standard engine projects and reproducible native builds |
| Provenance | `assets/manifest.json` (`provider`, `model`, `prompt`, `seed`, `licence` {`terms`, `plan_tier`, `commercial_ok`, `attribution`, `restrictions`}, `sha256`, `approved_by`) | Every generated or imported asset is traceable |
| Licence checks | Gateway `licence_check`; `config.licence_allowlist`; `config.revenue` thresholds | Flags non-commercial terms, free-tier ownership problems and revenue-threshold licences |
| Untracked assets | `post_tool_check.py` reminder for new binary assets not in the manifest | Nothing slips in unrecorded |
| Spend control | `budget.json` cap and ledger; gateway refuses calls over the remaining cap | Costs are bounded and visible |
| Secrets | Keys only through environment variables from plugin user config; `pre_tool_guard.py` denies reading or printing signing secrets | No keys in repositories or logs |

**Decisions it settles.**
- *Build on a hosted, proprietary web runtime because it is faster?* Not for anything that ships. Acceptable for a throwaway feel prototype only if nothing from it is carried into the product (section 12, case D).
- *Use an asset generated on a free tier whose terms forbid commercial use?* Reject or regenerate on a plan with commercial rights; `licence_check` flags it.
- *Depend on one vendor's proprietary engine feature with unclear future terms?* Record it in `risks` with a mitigation; Mega Crit's 2023 engine switch is the cautionary reference (`studio-doctrines.md`).

**Failure signs.** Assets on disk with no manifest entry; `commercial_ok` unknown; builds that only work on a vendor's cloud; API keys in config files; provider lock-in not listed in `risks`.

---

## 11. Principle 10 — Automatic between taste checkpoints

**What it means.** Agents run everything automatically except three human sign-offs: **style** (the visual and audio direction is locked), **fun** (the core loop is fun enough to build on) and **store submission** (anything that publishes to players). Everything between those checkpoints is the agents' responsibility, including quality, so humans are not asked trivial questions and are never bypassed on the three that matter.

**How the plugin enforces it.**

| Checkpoint | Trigger | What the human sees | Record |
|---|---|---|---|
| Style | Before production asset batches (`asset-production`, `audio-production`) | A small comparison set of style candidates against the art or audio bible | Manifest `approved_by`, `style_ref`; `gs.py progress` entry |
| Fun | End of loop prototype (`concept-lab`, `build-feature` on the core loop) | A playable build plus playthrough evidence and the persona report | `gs.py progress` entry; contract version |
| Store submission | `ship` process, `/arcosian:release-candidate` | Compliance pre-flight results, store metadata, build evidence | `pre_tool_guard.py` asks before submission and promotion commands; the human approves |

Other guard rails that ask a human: destructive deletes of `.gamestudio`, `assets` or the project root (`pre_tool_guard.py`).

**How to ask well.** Batch decisions; present two to four options with a recommendation and evidence; state the default that will apply if the human does not care; record the answer so it is never asked twice.

**Decisions it settles.**
- *Ask the user which shade of blue for a button?* No: decide within the locked style bible.
- *All gates pass; submit to App Review?* No: prepare everything, then ask.
- *Regenerate 40 icons in the approved style?* Yes, automatically, within budget; the style was already approved.

**Failure signs.** Approval fatigue (many small questions per session); checkpoints skipped "because the user was busy"; approvals not recorded in the manifest or progress log; humans asked to judge things the gates should have caught.

---

## 12. When principles collide: priority rules and worked cases

**Rule 1.** The lower-numbered principle wins.
**Rule 2.** No principle ever licenses skipping a gate (3) or crossing an ethics red line (8) in shipped work; those are floors, not trade-offs.
**Rule 3.** Prototype-tier work may defer *quality* obligations (polish, full accessibility, perf tuning) with written notes, but not *integrity* obligations (evidence for whatever is claimed, ethics, licences of anything kept).

| Case | Collision | Resolution |
|---|---|---|
| A | 2 (fun fast) vs 3 (verify): a feel prototype has no perf evidence | Allowed in `prototype` tier: mark `perf: n/a` with `gate_notes` "prototype tier, perf deferred to slice"; `playthrough` still needs a scripted run if the feature claims to pass. The deferral is revisited at the slice milestone |
| B | 4 (data) vs 8 (ethics): an aggressive offer lifts revenue in A/B | Ethics is a floor (rule 2): reject, record the result as a learning, look for an ethical variant |
| C | 5 (scope) vs 1 (player): a cut removes a feature playtesters love | Player first wins only if the feature is central to `player_fantasy` or a pillar; otherwise cut it and log it for a later update |
| D | 2 (fun fast) vs 9 (own output): a hosted tool would speed a throwaway prototype | Allowed for the throwaway prototype (2 outranks 9), but nothing from it, including assets, carries into the product unless it clears principle 9 |
| E | 6 (mobile) vs 7 (juice): effects push the low tier over budget | Mobile-native wins: scale effects by device tier; readability first |
| F | 1 (player) vs 2 (fun fast): accessibility in a prototype | Basic readability and touch-target size are cheap and stay; full accessibility options are deferred to the slice with a note |
| G | 10 (automation) vs 3 (verify): an agent is confident a feature works | Confidence is not evidence; gates still run automatically, and humans are not asked to replace them |
| H | 4 (data) vs 1 (player): metrics favour a mechanic players dislike in reviews | Investigate with segment data and qualitative playtests; player experience decides, with data used to size the problem |

---

## 13. Milestone doctrine audit

Run at each tier change (`prototype` → `slice` → `soft_launch` → `global` → `live`). Every "no" needs an owner and a date in `progress.md`.

1. Does each `must` item have a player-experience statement and a pillar trace? (1, 5)
2. Was the core loop judged fun at a recorded checkpoint before content production? (2, 10)
3. Do all `done` features pass `gs.py feature pass`, with evidence files present? (3)
4. Does every running or planned test have a written hypothesis, guardrails and a computed sample size? (4)
5. Is the `wont` list at least as long as the `must` list, and were kill criteria evaluated on their dates? (5)
6. Are perf reports from the low reference tier, including a sustained thermal scenario? (6)
7. Do key screens pass the thumbnail, silhouette and colour-independence tests? (7)
8. Does `compliance_preflight.py` pass, and does every monetization item comply with `monetization.ethics`? (8)
9. Is every asset in the manifest with known commercial rights, and does `licence_check` pass? (9)
10. Were humans asked only at the three checkpoints, and are their decisions recorded? (10)

---

## 14. Doctrine-health metrics

| Metric | Healthy direction | Source |
|---|---|---|
| Hours from concept selection to a playable loop | Down; within the time box | `progress.md` timestamps |
| Concept kill rate in `concept-tournament` | High (most concepts die early) | Concept files under `.gamestudio/concepts/` |
| Share of `done` features with complete gate evidence | 100% | `gs.py status --json` |
| Gates marked `n/a` without notes | Zero (hooks enforce) | `features.json` |
| Tests with pre-written hypotheses | 100% | Test plans and `data-analyst` reports |
| `wont` count vs `must` count | Ratio at or above 1 | `contract.json` |
| Perf violations on the low tier | Zero at soft launch | Perf reports under `.gamestudio/reports/` and evidence |
| Ethics findings from `compliance_preflight.py` | Zero open at release | Pre-flight output |
| Manifest coverage of binary assets | 100% | `manifest_query`, `post_tool_check.py` reminders |
| Human prompts per milestone outside the three checkpoints | Near zero | Session log |
