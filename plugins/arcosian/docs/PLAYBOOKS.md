# Playbooks

Five end-to-end procedures. Each lists the exact commands, skills, agents and workflows in order, the human checkpoints, and the exit test. `P` below means the plugin root; in a session use `${CLAUDE_PLUGIN_ROOT}`. Workflow arguments are shown in the form the workflow reads (`args.feature_id`, `args.topic`, and so on); the skills pass them for you, so you normally type the slash command and answer questions.

Rule for all five: humans sign off on style, fun and store submission. Everything between those checkpoints is automatic.

---

## Playbook 1: Idea to TestFlight

Goal: from a one-line idea to a signed build on TestFlight internal testing, with a core loop you have actually played. Plan for a prototype tier first; do not buy assets before the core loop is fun.

| Step | Do | Who and what runs | Exit test |
|---|---|---|---|
| 1 | `/arcosian:studio` | `studio` skill detects greenfield, hands off to `new-game` | State named correctly |
| 2 | `/arcosian:new-game "<brief>"` | `market-scan` workflow (args.topic), then `concept-tournament`; `principal` oversees | A recommended concept with a stated player motivation |
| 3 | Review the winning concept card | You | Checkpoint 1: you accept the concept or ask for another round |
| 4 | Contract | `game-designer` writes `.gamestudio/contract.json`: pillars, verbs, core loop, FTUE, must/should/won't, kill criteria | `gs.py validate --all` clean |
| 5 | `/arcosian:design-review` | `design-review` workflow (args.contract_path); edits proposed, not applied | You apply or reject each proposed edit |
| 6 | `python3 P/scripts/gs.py init --title "<title>" --engine godot --tier prototype --monetization iap --budget 25` | Creates `.gamestudio/` (the `new-game` skill does this for you) | `gs.py status` prints a summary |
| 7 | Copy `P/templates/godot-starter/` (or `unity-starter/`) into the project | `lead-engineer` confirms sim-core plus presentation split | Template tests run |
| 8 | Feature plan | `producer` fills `features.json` via `gs.py feature add`; first feature is the core loop in grey boxes | `gs.py feature next` returns the core loop |
| 9 | `/arcosian:build-feature F001` | `build-feature` workflow (args.feature_id): engineer builds sim-core with tests, then presentation; gates run; `critic` tries to refute; up to 3 fix rounds | `gs.py feature pass F001` succeeds |
| 10 | Play it | `/arcosian:playtest` runs `playtest-sweep`; then you play on a device for ten minutes | Checkpoint 2: is it fun? If not, iterate the loop, do not add content |
| 11 | Content and feel | Repeat step 9 for each feature in contract priority order; `ux-designer` and `gameplay-engineer` add feedback and juice to each feature | Slice tier reached: one complete level path plus FTUE |
| 12 | Style lock | `art-director` produces the style bible from `templates/docs/style-bible.md`; you approve a few reference images | Checkpoint 3: style approved |
| 13 | `/arcosian:asset-production` | `asset-batch` workflow via the gateway, within budget; then `/arcosian:audio-production` | Manifest entries have licence notes; `gs.py budget` under cap |
| 14 | `/arcosian:balance` | `balance-pass`; simulators `economy_sim.py`, `difficulty_curve.py` | Report with verified changes |
| 15 | `/arcosian:optimize` | `performance-engineer` against `perf_budget.py` | Perf gate passes on the low-end tier |
| 16 | Copy CI from `P/templates/ci/`, add secrets | `release-manager`; follow `templates/ci/README.md` setup order | Validate job green |
| 17 | `/arcosian:ship ios internal` | `ship` skill runs `release-candidate`: `compliance_preflight.py`, version bump, build, perf check, `store_metadata.py`, compliance review. Stops before submission | Release report plus human approval checklist |
| 18 | You upload to TestFlight (CI lane with `CONFIRM_RELEASE` set by you) | Hook asks you to confirm any store command | Build visible in TestFlight internal group |

Decision points:

| If | Then |
|---|---|
| The core loop is not fun after two iterations at step 10 | Re-run `concept-lab` with "mechanic transplant" or kill per the contract's kill criteria |
| Budget runs low at step 13 | Prefer recolour and reuse over new generation; log skipped items from `asset-batch` |
| Compliance pre-flight reports a blocker | Fix it before building again; do not bypass |

---

## Playbook 2: Onboarding an existing project

Goal: bring an unmanaged Godot or Unity project under the studio's state and gates without rewriting it.

1. `/arcosian:studio`. It finds `project.godot` or `ProjectSettings/` and routes to onboarding.
2. `python3 P/scripts/gs.py init --title "<existing title>" --engine godot --tier slice` (use the tier that matches reality; `--force` backs up before overwriting).
3. Deconstruct the project into a contract: `game-designer` reads code and scenes and writes `.gamestudio/contract.json` describing the game as it is (verbs, mechanics, loops, economy, FTUE). Unknowns go to `risks`, not guesses. `lead-engineer` fills the technical section.
4. `python3 P/scripts/gs.py validate --all`; fix schema errors.
5. Architecture audit by `lead-engineer`: is simulation separable from presentation? List the three biggest coupling problems as features, not a rewrite.
6. Baseline measurements before touching anything:
   - `python3 P/scripts/compliance_preflight.py --project . --platform all`
   - Frame times via the project's runner, then `python3 P/scripts/perf_budget.py --report <file>`
   - Run existing tests and record the log
7. Create the feature ledger: one feature per known gap. Mark existing working features done only with evidence: record each gate with `gs.py feature gate ... --evidence`, or `n/a` with an honest note.
8. `/arcosian:design-review` against the reconstructed contract to expose design and economy debt.
9. `/arcosian:playtest` for a baseline sweep.
10. Pick the first improvement with `gs.py feature next`; proceed with `/arcosian:build-feature`.

Exit test: `gs.py status` is truthful, `gs.py validate --all` is clean, and baseline reports are in `.gamestudio/evidence/`. Do not start new features until the baseline exists.

---

## Playbook 3: Content production at scale

Goal: ship dozens to hundreds of levels, items or assets with consistent quality and a controlled budget.

1. Define the unit. `level-designer` writes a level spec per `level-spec.schema.json` and the curve targets (difficulty, new-element introduction rhythm).
2. Build the generator and solver first:
   - Procedural layouts: `python3 P/scripts/pcg.py --help`
   - Solvability and move counts: `python3 P/scripts/puzzle_solver.py --help`, `python3 P/scripts/match3_sim.py --help`
   - Difficulty from solver output: `python3 P/scripts/difficulty_curve.py --help`
3. Generate a batch of 20, reject by solver rules (unsolvable, trivial, too long), then hand-tune the rest. Keep seeds in the spec for reproducibility.
4. Gate each batch: sim-core tests for the spec validator, a deterministic bot run per level in `playtest-sweep`, and visual critique on the five worst and five best.
5. Art: lock style with `art-director`, then `/arcosian:asset-production` (`asset-batch`). Rules:
   - Every asset prompt starts from the style lock text and reference images.
   - Run `image_postprocess` (and `image_post.py`) for size, palette and alpha.
   - Check the manifest for licence notes; free-tier vendor output may be restricted.
   - Watch `gs.py budget` after every batch; stop at 80 percent and review.
6. Audio: `/arcosian:audio-production`; loop and loudness QC through `audio_post.py` before import.
7. Telemetry: `event_taxonomy.py` defines level start, win, fail, booster use, quit; the `data-analyst` agent sets the funnel you will read.
8. Rebalance weekly: `/arcosian:balance` (`balance-pass`, args.focus) using real telemetry once available; compare predicted and observed difficulty.
9. Production control: `producer` tracks content throughput and risk in `progress.md`; `critic` samples 10 percent of new content each batch.

Throughput table to fill in for your project (measure; do not assume):

| Metric | Source | Action when off |
|---|---|---|
| Solver reject rate | `puzzle_solver.py` output | Fix generator constraints, not the filter |
| Cost per accepted asset | manifest and `gs.py budget` | Switch provider or reuse |
| Bot completion rate vs target | `playtest-sweep` report | Re-tune with `difficulty_curve.py` |
| Critic pass rate on samples | critic notes | Tighten the spec or style lock |

Exit test: a batch moves from generated to shipped with solver, bot, visual and licence checks all recorded.

---

## Playbook 4: Soft launch to live

Goal: validate retention and monetization in a small market, fix, then go global and run live-ops. This playbook assumes you already have a build on store testing tracks.

### Phase A: Prepare (before any real users)

1. `/arcosian:ship android internal` then beta tracks; run `compliance_preflight.py` and fix blockers.
2. `compliance-officer` reviews: privacy and consent, age rating, loot-box and odds disclosure (`gacha_calc.py` odds tables), AI-content disclosure, licences.
3. Instrument: confirm the event taxonomy is implemented; run an end-to-end test that events arrive in Firebase; set Crashlytics.
4. Fill `templates/docs/soft-launch-plan.md`: markets, duration, spend, success and kill thresholds written before launch. Choose thresholds from your genre benchmarks in `market-intel`; do not copy someone else's numbers blindly.
5. Define the Remote Config keys you may need to tune live (economy values, ad frequency, difficulty offsets).

### Phase B: Soft launch

1. Human step: create the store listing, finalize metadata (`store_metadata.py` generates fastlane metadata from the contract), submit to review yourself.
2. Watch daily, decide weekly. `/arcosian:operate` runs the review: `data-analyst` builds cohort retention, `python3 P/scripts/retention_ltv.py fit ...` fits curves, `ltv` projects value; `monetization-designer` reads conversion and ad metrics.
3. Experiments: one hypothesis at a time; size with `ab_test.py` before launching, and do not stop early on a good-looking number.
4. Crash triage: `liveops-manager` and `gameplay-engineer` fix top crash clusters first; ship hotfix builds via `/arcosian:ship`.
5. Fix the funnel in order: FTUE drop-off, then D1, then D7, then monetization. Tuning monetization before retention is a common waste.

### Phase C: Go or no-go

| Evidence | Go | Iterate | Kill |
|---|---|---|---|
| Retention vs your pre-written thresholds | Meets | Close and trending up | Far below after two fix cycles |
| Unit economics from `retention_ltv.py` against UA cost | LTV clears cost with margin | Near break-even with a tested lever | No credible lever |
| Stability | Crash-free target met | Known fixes pending | Unfixable device issues |
| Compliance | Clean | Minor open items | Policy conflict |

`critic` writes the recommendation; you decide.

### Phase D: Global and live

1. `/arcosian:ship all beta`, then staged production rollout by your own hand in the consoles.
2. `liveops-manager` builds the calendar from `templates/docs/liveops-calendar.md`: cadence, event types, segmentation, remote-config schedule.
3. Run the weekly `operate` loop: metrics review, experiment readout, crash triage, content pipeline status (Playbook 3).
4. Keep the budget discipline: ad and IAP changes go through A/B tests; maintain the ethics rules from the `monetization` and `legal-ethics` skills.
5. After each major milestone, `/arcosian:postmortem` records what worked, what did not and what to change in the studio's own process.

Exit test: a written go decision with evidence, a live-ops calendar for the next eight weeks, and a postmortem entry for the soft launch.

---

## Playbook 5: Change something safely

For a tuning change, a balance fix or a refactor in a project whose features already passed their gates.

1. **Refresh the map.** `python3 P/scripts/gs.py map`, then read `.gamestudio/map/MAP.md`.
2. **See what the change touches.** `python3 P/scripts/gs.py impact <file | class | tuning key>`: dependent scenes, scripts and tests, done features to re-check, and the gates to run again.
3. **Predict it (tuning, economy, levels).** `/arcosian:what-if KEY=VALUE`, or `python3 P/scripts/gs.py whatif --set KEY=VALUE`. Compare options with one run each. Apply only `improves`; take `mixed` to the human with the trade-off; never apply `reject`.
4. **Apply through the gates.** `/arcosian:build-feature F0xx` with the change; re-run every gate `impact` named for every listed feature.
5. **Show the result.** `python3 P/scripts/gs.py dashboard` and share `.gamestudio/reports/dashboard.html` at the checkpoint.

Exit test: the what-if result is saved, every gate `impact` named passes again with fresh evidence, and the progress log records the decision.

## Volatile facts (as of Oct 2026 — verify)

Store rules, SDK minimums and review timelines change; confirm on the store pages before committing dates.

| Topic | Source |
|---|---|
| Apple upcoming requirements | https://developer.apple.com/news/upcoming-requirements/ |
| Google Play target API requirement | https://developer.android.com/google/play/requirements/target-sdk |
| Google Play Console help | https://support.google.com/googleplay/android-developer/ |
