# Architecture

How the suite fits together and why. Read this before extending it. File names below are relative to `plugins/arcosian/`.

## 1. Five layers

| Layer | Lives in | Job | Rule of thumb |
|---|---|---|---|
| Codex | `skills/*/SKILL.md` and `skills/*/references/*.md` | Knowledge as procedures, formulas, decision tables | SKILL.md is a short router; depth sits in references loaded on demand |
| Ontology | `skills/game-ontology`, `scripts/schemas/*.schema.json` | One vocabulary: verbs, mechanics, dynamics, aesthetics; loops as graphs; resources and flows; progression tracks; content units; project state | If two parts of the system exchange data, it is a schema, not prose |
| Studio | `agents/*.md`, `workflows/*.js` | Specialists plus multi-agent procedures | Judgement work on opus, execution on sonnet |
| Tools | `scripts/`, `mcp/studio-gateway/`, `templates/` | Deterministic computation and side effects | Anything that can be computed is computed by a script, not estimated by a model |
| Enforcement | `hooks/`, plus the repository's `evals/arcosian/` | Machine-checkable definition of done | Hooks check files on disk; they do not trust claims |

The layers depend downward only. Skills call scripts; agents load skills; workflows spawn agents; hooks read the state that scripts write.

## 2. Project state: `.gamestudio/`

Created by `python3 scripts/gs.py init --title "..." [--engine godot|unity|...] [--tier prototype|slice|soft_launch|global|live] [--monetization ...] [--budget N]`. It lives in the user's game project, not in the plugin.

The layout below mirrors section 5 of the marketplace repository's `docs/BLUEPRINT.md` (two levels above the plugin root: `../../docs/BLUEPRINT.md`). `gs.py init` creates every directory in it (`assets/`, `design/`, `art/`, `audio/`, `concepts/`, `research/`, `economy/`, `levels/`, `analytics/`, `evidence/`, `playtests/`, `reports/`, `snapshots/`, each with a `.gitkeep`) plus the six files at the top; re-running it on an older project adds any missing directory and touches nothing else.

| Path | Meaning | Schema |
|---|---|---|
| `config.json` | Engine, platforms, paths, budgets, revenue thresholds, storefronts, licence allowlist, preferred providers, tier | `config.schema.json` |
| `contract.json` | The design contract (one-page truth of the game): pillars, verbs, loops, economy, FTUE, scope lists, risks, kill criteria | `design-contract.schema.json` |
| `features.json` | Feature ledger with per-feature five-gate results and evidence paths | `features.schema.json` |
| `progress.md` | Dated, append-only session log | n/a |
| `budget.json` | Asset and audio spend ledger and cap | `budget.schema.json` |
| `assets/manifest.json` | Provenance for every generated or imported asset: provider, model, prompt, seed, cost, licence terms, status | `asset-manifest.schema.json` |
| `design/` | Living design docs: `core-loop.md`, `ftue.md`, `world.md`, `tone-bible.md`, `decisions.md`, `liveops-calendar.md`, `ux/`, `mechanics/<id>.mechanic.json`, `features/<F###>.md` | `mechanic-card.schema.json` for the cards (`gs.py validate --cross` checks their ids are unique) |
| `art/` | `style-bible.md`, `style-cards.md`, `asset-list.md`, `import-presets.md`, `vfx-budget.md`, `reviews/` | n/a |
| `audio/` | `audio-bible.md`, `cue-list.md`, `music-plan.md`, `sfx-list.md`, `qc/` | n/a |
| `concepts/` | Concept cards from ideation, and `ranking.md` | `concept.schema.json` |
| `research/` | `market-<slug>.md`, `positioning.md`, `comparables.json`, `market-risks.md`, `deconstructions/<slug>.json` | `deconstruction.schema.json` |
| `economy/` | Economy models and simulator outputs | `economy-model.schema.json` |
| `levels/` | Level specs | `level-spec.schema.json` |
| `analytics/` | Event taxonomy | `event-taxonomy.schema.json` |
| `evidence/<FEATURE-ID>/` | Gate evidence per feature: logs, playthrough reports, screenshots, perf reports | n/a |
| `playtests/` | Playtest and sweep reports | `playtest-report.schema.json` |
| `reports/` | Reviews, perf reports (`<feature-or-build>.<device>.perf.json`), release reports | `perf-report.schema.json` for the perf reports |
| `snapshots/` | PreCompact snapshots (`precompact-<timestamp>.md`) and `gs.py init` backups (`init-backup-<timestamp>/`) | n/a |

The gateway also keeps `jobs.json` in this directory when it runs a multi-stage 3D job (see section 5); it is not part of the layout above and holds no design state.

Other schemas: `common` (shared definitions) and `mechanic-card`. Schema selection from file names is automatic (for example `*.mechanic.json`, `*.level.json`, `*.taxonomy.json`, `*.perf.json`; `validate_json.py --list` prints the rules). Validate everything with `python3 scripts/gs.py validate --all`, add `--cross` for cross-document checks (unique mechanic, currency and event ids, references, evidence and manifest paths), and check single files with `scripts/validate_json.py`.

Design choice: state is plain JSON and markdown in the repo, so it diffs in git, survives context compaction and can be edited by hand. The PreCompact hook snapshots it; SessionStart reads it back.

## 3. The five gates

A feature is `done` only if each gate is `pass` with evidence on disk, or `n/a` with a written note.

| Gate | Question | Typical evidence |
|---|---|---|
| static | Does it lint, type-check, import and validate against schemas? | Linter output, `gs.py validate` output |
| unit | Do sim-core tests pass? | Test runner log |
| playthrough | Does a deterministic scripted playthrough or bot complete the feature path? | Run log with seed and result |
| visual | Does a screenshot critique pass at target resolution and safe areas? | Screenshots plus critic notes |
| perf | Is the frame-time and memory budget met on the target device tier? | `perf_budget.py` verdict, perf report |

Commands:

```
python3 scripts/gs.py feature add --help
python3 scripts/gs.py feature next
python3 scripts/gs.py feature start F001
python3 scripts/gs.py evidence-dir F001
python3 scripts/gs.py feature gate F001 unit pass --evidence .gamestudio/evidence/F001/unit.log
python3 scripts/gs.py feature gate F001 perf n/a --note "no render change"
python3 scripts/gs.py feature pass F001      # refuses unless the five-gate rule holds
```

`feature pass` exits 1 on failure (exit codes: 0 ok, 1 check failed, 2 usage). Use `n/a` honestly: a note that says "n/a" proves nothing, and the critic is told to challenge it.

## 4. Hooks

Declared in `hooks/hooks.json`; handlers in `hooks/scripts/`; tests in `hooks/tests/test_hooks.py`. Every hook starts in exec form as `node hooks/scripts/run-python.mjs <handler>.py`: no shell is involved, and the launcher uses `python3`, `python` or `py -3` (whichever is a working Python 3; Windows Store placeholders are skipped) and caches the choice in the plugin data folder.

| Event | Handler | Behaviour |
|---|---|---|
| SessionStart | `session_start.py` | Injects the project summary, or hints at `/arcosian:studio` for a bare engine project; where Python 3 is not `python3` (Windows), tells Claude which command to use |
| PreToolUse (Bash, PowerShell) | `pre_tool_guard.py` | Asks before store submission or promotion (fastlane deliver/supply, altool upload, gradle publish and similar); denies reading signing secrets and keychain or Windows credential store; asks before a recursive delete (`rm -rf`, `Remove-Item -Recurse`, `rd /s`) of project state or source assets |
| PreToolUse (Write, Edit, MultiEdit) | `pre_tool_guard.py` | Denies a write to `.gamestudio/features.json` that marks a feature done while it fails the gates |
| PostToolUse (Write, Edit, MultiEdit) | `post_tool_check.py` | GDScript parse check (Godot from `GODOT_BIN`, the Godot adapter's `godot_bin`, PATH including versioned Windows downloads, or `/Applications`; a Windows GUI build is swapped for its `_console.exe` twin), duplicate scene uids, schema check of `.gamestudio` JSON, reminder to add new binary assets to the manifest |
| Stop, SubagentStop | `stop_gate.py` | Blocks stopping while any feature is `done` but fails the five-gate rule |
| TaskCompleted | `task_gate.py` | Same check at task level |
| PreCompact | `pre_compact.py` | Snapshots project state before context compaction |

All hooks are Python stdlib, share `_common.py`, and fail open on internal errors so a bug never bricks a session. They are a safety net, not the primary control: the primary control is the doctrine in the agents and skills.

## 5. Studio-gateway MCP server

`mcp/studio-gateway/server.mjs`, registered in `.mcp.json`, zero npm dependencies. It is the only path by which the core plugin spends money.

- Tools (all 14 that `tools/list` returns; details in `mcp/studio-gateway/README.md`):

  | Group | Tools |
  |---|---|
  | Status and budget | `gs_status` (resolved project root, budget, configured providers, mock flag; call it first), `budget_status` (cap, spend, recent ledger) |
  | Images | `image_generate`, `image_edit`, `image_postprocess` (Recraft remove_background, vectorize, upscale) |
  | 3D | `model3d_generate` (Tripo or Meshy GLB from text or an image), `model3d_status` (continues and collects a handed-back multi-stage job; jobs are recorded in `.gamestudio/jobs.json`) |
  | Audio | `audio_music`, `audio_sfx`, `audio_voice` |
  | Provenance | `manifest_query`, `manifest_update` (both on `.gamestudio/assets/manifest.json`), `licence_check` (licence terms, provenance and placeholder audit) |
  | Knowledge | `kb_search` (ranked snippets from `skills/**/*.md`) |

- Providers in `providers/`: Gemini (Google Lyria music shares its key and endpoint), OpenAI, Recraft, fal, Tripo, Meshy, ElevenLabs, Stability. A provider without a key is simply unavailable.
- Budget: per-project cap from `.gamestudio/config.json`, defaulting to the `asset_budget_usd` user setting; per-call caps; `pricing.json` holds estimates used for pre-flight and must be refreshed against vendor pricing.
- Provenance: every output gets a manifest entry (provider, model, prompt, seed if any, cost, licence note). `licences.mjs` holds per-provider licence defaults and checks rules against the revenue in `.gamestudio/config.json`; treat them as reminders and verify vendor terms yourself.
- Mock mode: no key, `GS_MOCK=1` or `dry_run` yields valid placeholder PNG, WAV, GLB and SVG files at cost 0, so the pipeline can be tested end to end for free.
- Tests: `node mcp/studio-gateway/test/run-tests.mjs`.

## 6. Workflows

`workflows/*.js` are dynamic multi-agent scripts, each with a `meta` block (`name`, `description`). They are invoked as `/arcosian:<name>` and use agents as `arcosian:<agent>`.

Shared patterns:

- Fan out, then reduce: independent lenses or generators run in parallel, a synthesizer merges.
- Judge independence: scorers never see each other's scores.
- Adversarial pass: a skeptic or `critic` tries to refute before approval (`concept-tournament`, `design-review`, `build-feature`, `deconstruct-game`).
- Bounded retries: `build-feature` fixes and re-gates at most 3 rounds, then reports blocked.
- Budget awareness: `market-scan` caps web use per agent; `asset-batch` logs skipped items when the budget is hit.
- Read-only by default: `design-review` proposes contract edits and does not apply them; `release-candidate` stops at internal-track preparation.

Selection guide:

| Situation | Workflow |
|---|---|
| Need ideas | `concept-tournament` |
| Learning from a shipped game | `deconstruct-game` |
| Contract exists, before building | `design-review` |
| Genre or competitor unknown | `market-scan` |
| One feature to implement | `build-feature` |
| Many assets to make | `asset-batch` |
| A build to test | `playtest-sweep` |
| Numbers feel off | `balance-pass` |
| Going to a store | `release-candidate` |

## 7. Model routing

Agent frontmatter pins the model. The rule: opus where an error is expensive to discover later, sonnet where the work is bounded and checkable.

| Opus | Sonnet |
|---|---|
| `principal`, `game-designer`, `systems-designer`, `art-director`, `lead-engineer`, `monetization-designer`, `critic` | all other 17 agents |

Rationale: vision, core loop, economy, style, architecture, monetization ethics and adversarial review set the ceiling of the project. Implementation, QA, research and logistics are verified by gates and scripts, so a cheaper model is safe. Workflows that fan out wide (judges, lenses, personas) use sonnet agents for volume and reserve opus for synthesis and refutation. Override per run if your budget or quality bar differs; keep `critic` on the strongest model you have.

## 8. Security model

| Concern | Control |
|---|---|
| Spending | Gateway-only, capped per project and per call, mock mode by default without keys |
| Secrets | API keys are `sensitive` user-config values passed as env vars to the gateway; never written to project files; hooks deny reading keystores, `.p8`, `.p12`, provisioning profiles and keychain |
| Store actions | Hooks ask before submit/promote; `ship` and `release-candidate` stop at internal tracks; env var `CONFIRM_RELEASE` is set by a human per CI run |
| Untrusted content | Research output (web pages, vendor docs) is data; agents cite sources and the market workflows cross-check key claims |
| Third-party MCP adapters | Separate opt-in plugins, pinned in their own `.mcp.json`; review each server before enabling |
| Language servers (Godot and Unity adapters) | Local processes only: Godot's server on a free localhost port behind a stdio bridge, csharp-ls over stdio; generated C# projects live in the plugin data folder, never in the user's project; no network calls except `dotnet restore` of the generated engine-free projects |
| Licences | Provenance per asset; vendor terms checked; AI-content disclosure handled by `compliance-officer` |
| Plugin hygiene | No `CLAUDE.md` or top-level `bin/` in the plugin; scripts use the standard library only |

Limits to be honest about: hooks operate on patterns and can be evaded by an agent determined to; they catch accidents. Keep real signing keys out of the dev machine and in CI secrets.

## 9. Evals and audit

- `scripts/audit_plugin.py --root .`: frontmatter validity (allowed keys, name equals directory), references and scripts listed and present, preloaded skills existing, counts. `--map FILE` regenerates `docs/KNOWLEDGE-MAP.md`.
- `evals/arcosian/` (repository root; not shipped with the plugin): eight cases for `claude plugin eval` (concepts, contract, five gates, deconstruction, economy sim, compliance preflight, gateway mock, principal next step). See `evals/arcosian/README.md` for flags and cost caps.
- Self-tests: `gs.py --selftest`, each script's `--selftest`, hook tests, gateway tests.

## 10. Extending

1. New codex skill: directory name equals `name`; short SKILL.md; every file in `references/` listed in it; run the audit.
2. New agent: pick the model by the rule in section 7; list preloaded skills that exist.
3. New workflow: `meta.name` equals the file name; read-only unless it must write; add a bounded retry.
4. New schema: add to `scripts/schemas/` with a valid example; wire into `validate_json.py`.
5. New provider: add `providers/<name>.mjs`, a `pricing.json` entry, a userConfig key, and a mock path.
