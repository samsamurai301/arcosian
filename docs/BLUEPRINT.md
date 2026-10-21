# Arcosian — Build Blueprint

This is the binding contract for everyone building the **Arcosian** plugin suite. If you are a builder, read it all before you write anything. Where this file and your task brief disagree, the task brief wins for your own paths only.

## 0. Mission

`arcosian` turns Claude Code into a **principal game developer** with a full studio behind them. It is not an engine wrapper. Its value is in five layers, all of which must be world-class:

1. **Codex (knowledge).** Design theory, studio philosophies ("ideologies"), a mechanics encyclopedia, genre playbooks, deconstructions of landmark games, an analogy method, player psychology, player-behaviour analytics, economy, progression, level design, procedural generation, narrative, game feel, mobile UX, art and audio direction, architecture, programming patterns, networking, performance, engines, AI asset and audio pipelines, QA, monetization, live-ops, store release, marketing, production, market intelligence, legal and ethics, accessibility and localization, and a full glossary.
2. **Ontology (logical abstractions).** One formal vocabulary and a set of JSON schemas every part of the system speaks: verbs → mechanics → dynamics → aesthetics; loops as graphs; resources and flows (Machinations-style sources, sinks, converters, pools, gates); progression tracks; content units; player models; and the project state files.
3. **Studio (agents and workflows).** A senior specialist for every discipline, led by the `principal` agent, plus multi-agent workflows for concept tournaments, deconstructions, design reviews, feature builds, asset batches, playtest sweeps, balance passes, market scans and release candidates.
4. **Tools (scripts, MCP, templates).** A project-state CLI, simulators and calculators (economy, progression, gacha, difficulty, A/B tests, retention and LTV), level solvers, procedural generators, an asset and audio gateway MCP server with budgets and provenance, compliance pre-flight, store metadata, perf budgets, audio and image post-processing, and production-grade Godot and Unity mobile templates with CI and fastlane.
5. **Enforcement (hooks and evals).** A machine-checkable definition of done (five gates), guards on irreversible actions, schema validation, provenance and licence checks, and an eval suite.

**Doctrine (the ideology the whole system follows, in priority order):**
1. Player first: every decision is justified by the player experience it creates.
2. Find the fun fast: prototype the core loop in hours, not weeks. Core loop before content, content before polish.
3. Verify by playing: nothing is "done" until a deterministic playthrough, the perf budget and a visual critique pass.
4. Data-informed, not data-driven: hypotheses first, then telemetry to confirm.
5. Scope ruthlessly: one-page design contract, explicit must/should/won't lists, kill criteria.
6. Platform-native: design for the devices and inputs you ship on (thumb reach and short sessions on phones; mouse, keyboard and gamepad on PC; controller-only TV play on consoles; download size on the web), and for interruptions, low-end hardware, battery and heat.
7. Readability over detail. Juice everything that the player touches.
8. Ethical monetization: no dark patterns, transparent odds, respect for minors.
9. Own the output: native builds the user owns, no runtime lock-in, licences checked.
10. Automatic between taste checkpoints: humans sign off on style, fun and store submission.

## 1. Repository layout

Root (referred to as `ROOT`): `arcosian/`

```
ROOT/
├── .claude-plugin/marketplace.json        # marketplace catalog (written by coordinator)
├── README.md                              # (integrator)
├── docs/BLUEPRINT.md                      # this file
└── plugins/
    ├── arcosian/                       # CORE plugin (referred to as PLUGIN)
    │   ├── .claude-plugin/plugin.json     # (coordinator) userConfig keys, metadata
    │   ├── README.md                      # (integrator)
    │   ├── .mcp.json                      # studio-gateway server (gateway builder)
    │   ├── skills/<skill-name>/SKILL.md   # + references/*.md, optional scripts/, assets/
    │   ├── agents/<agent-name>.md
    │   ├── hooks/hooks.json
    │   ├── hooks/scripts/*.py
    │   ├── mcp/studio-gateway/            # zero-dependency Node MCP server
    │   ├── scripts/*.py                   # Python CLI tools (stdlib only)
    │   ├── scripts/schemas/*.schema.json  # ontology schemas
    │   ├── templates/godot-starter/        # Godot 4.x template: phones, desktop, web
    │   ├── templates/unity-starter/        # Unity 6 LTS skeleton: phones, desktop, web
    │   ├── templates/ci/                  # GitHub Actions, fastlane, Codemagic
    │   ├── templates/docs/                # GDD one-pager, style bible, etc.
    │   ├── workflows/*.js                 # dynamic workflows
    │   ├── evals/<case>/                  # claude plugin eval cases
    │   └── docs/                          # ARCHITECTURE, KNOWLEDGE-MAP, SETUP (integrator)
    ├── arcosian-godot/                 # adapter: GDScript language server (lsp/) + Godot MCP bridges
    ├── arcosian-unity/                 # adapter: Unity-aware C# language server (lsp/) + Unity CLI + MCP bridges
    ├── arcosian-blender/               # adapter: Blender MCP
    ├── arcosian-vendors/               # adapter: asset/audio vendor MCPs (Scenario, PixelLab, Meshy, ElevenLabs, ComfyUI...)
    └── arcosian-commerce/              # adapter: RevenueCat, Firebase, Adjust, App Store/Play MCPs
```

Never write outside the paths your brief assigns you. Never create a `CLAUDE.md` or a top-level `bin/` inside a plugin (both are disallowed or break installation on some surfaces). Never rename another builder's files.

## 2. Global conventions

**Voice.** Senior practitioner. Concrete, specific, numerate. Every section must help someone make a decision or do the work. No filler, no marketing tone, no "In today's fast-paced world". Prefer checklists, decision tables, formulas, worked examples, and "do / don't" lists. Use Markdown headings, tables and fenced code.

**Accuracy.**
- Do not invent statistics, prices, dates, version numbers, quotes or sources. If you are not sure, say so ("approximately", "reported", "verify") or leave it out.
- Volatile facts (prices, model names, SDK versions, store rules, market numbers) go in a clearly labelled section such as `## Volatile facts (as of Oct 2026 — verify before relying)` with a source link per fact. Keep stable knowledge separate from volatile knowledge.
- The research notes from October 2026 are your best source of current facts: `RESEARCH_NOTES/` (path given in your brief) and the synthesized report `RESEARCH_REPORT`. Use them; cite their original source URLs, not the notes file.
- Web search is a scarce shared budget. Only use it if your brief allows it, and only for volatile facts. Prefer `WebFetch` on a known official URL.

**Copyright.** Summarize frameworks, books and talks in your own words with attribution (author, work, year). Never reproduce long passages, full card decks, full lists of someone else's questions, song lyrics, or code from non-permissive sources. Short quotes (< 15 words) only when essential, with attribution.

**Cross-references.**
- Refer to other skills by name in backticks: `economy-design`. Refer to a specific file by plugin-relative path: `skills/economy-design/references/currency-architecture.md`.
- Inside a SKILL.md, refer to your own files relatively: `references/foo.md`, `scripts/bar.py`.
- Refer to plugin scripts as `${CLAUDE_PLUGIN_ROOT}/scripts/<name>.py` (Claude Code substitutes `${CLAUDE_PLUGIN_ROOT}` inside skill and agent content). In docs and READMEs write `<plugin-root>/scripts/<name>.py`.
- Refer to schemas as `${CLAUDE_PLUGIN_ROOT}/scripts/schemas/<name>.schema.json`.

**Python.** Stdlib only, compatible with Python 3.9 (macOS system Python). `#!/usr/bin/env python3`, `argparse`, `--json` flag for machine output, exit code 0 = ok, 1 = check failed, 2 = usage/input error. Optional third-party packages (e.g. Pillow, numpy) only behind a guarded import that prints a one-line hint such as `pip install pillow` or `uv run --with pillow python3 ...`. Every script must support `--selftest` that exercises its core logic with built-in fixtures and exits 0 on success. **Builders must run every script's `--selftest` and fix failures before finishing.** Use `pathlib`, type hints are fine (3.9-compatible: `from __future__ import annotations`).

**Node.** Node ≥ 18, ESM (`.mjs`), zero npm dependencies (use built-in `fetch`, `zlib`, `crypto`, `fs`). Must run with `node file.mjs`.

**GDScript.** Godot 4.x (target 4.5+, written to be correct on 4.7), statically typed (`var x: int`, typed arrays, `-> void`), no Python idioms, signals and `@export` used correctly. Never hand-invent `uid://` values; omit `uid` attributes in `.tscn`/`.tres` (Godot regenerates them) — this avoids duplicate-UID corruption.

**C#.** Unity 6 LTS, C# 9, nullable-aware, no `UnityEngine` references in the pure core assembly.

**Secrets.** Never write API keys or credentials anywhere. Keys reach code only through environment variables populated from plugin `userConfig`.

## 3. Skill format

Path: `PLUGIN/skills/<skill-name>/SKILL.md`. `<skill-name>` is kebab-case and must equal the `name` field.

```markdown
---
name: <skill-name>
description: <≤ 450 characters. Third person. What it knows/does, then "Use when ..." with concrete trigger phrases a user or agent would say.>
argument-hint: "<only for process skills that take arguments>"
---

# <Title>
...
```

Allowed optional frontmatter: `when_to_use` (≤ 200 chars), `argument-hint`, `allowed-tools`, `disable-model-invocation`, `user-invocable`, `model`, `effort`, `context`, `agent`, `paths`, `license`, `metadata`. Do not add other keys.

**Codex (knowledge) skill body template** — SKILL.md 150–450 lines:
1. `## What this skill gives you` — 3–6 bullets.
2. `## Core models` — the essential mental models, frameworks and rules of thumb (the 20% that matters 80% of the time), each actionable.
3. `## Decision procedures` — step-by-step procedures, checklists, decision tables for the common tasks in this domain.
4. `## Platform specifics` — what changes on phones, PC, web and consoles (where relevant). Older skills use `## Mobile specifics`.
5. `## Anti-patterns` — common mistakes and how to detect them.
6. `## Using the ontology` — how this domain maps to the shared schemas (section 5) and which scripts/tools apply.
7. `## Reference library` — a table: file → what it contains → when to read it. Every file in `references/` must be listed.
8. `## Related skills` — names with one line each.

References: `references/*.md`, each 120–800 lines, dense and specific. Total references per codex skill: aim for 1,500–4,000 lines unless the brief says otherwise. Use worked examples, formulas, parameter tables, named reference games, and pseudo-code where useful. Each reference file starts with a one-paragraph summary and a table of contents.

**Process (command) skill body template** — SKILL.md 120–400 lines:
1. `## When to use` and `## Inputs` (what `$ARGUMENTS` means).
2. `## Procedure` — numbered steps with exact commands (`python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py ...`), which agents to delegate to (`arcosian:<agent>`), which workflow to run (`/arcosian:<workflow>`), which codex skills to load, and the human checkpoints.
3. `## Outputs` — files written (under `.gamestudio/` or the game project).
4. `## Quality gates` — what must be true before finishing.
5. `## Failure modes and recovery`.
Optional `references/` for long templates or checklists.

## 4. Agent format

Path: `PLUGIN/agents/<agent-name>.md`. Name is kebab-case, no colon.

```markdown
---
name: <agent-name>
description: <when to delegate to this agent; ≤ 400 chars; start with the role, then "Use for ...">
tools: <optional comma list; omit to inherit all>
model: <opus | sonnet | haiku | inherit>
effort: <low | medium | high | xhigh>
color: <red|blue|green|yellow|purple|orange|pink|cyan>
skills:
  - <skill-name>        # preloads; max 4; only codex skills central to the role
---
```

Do NOT use `hooks`, `mcpServers`, `permissionMode` or `initialPrompt` (ignored for plugin agents). Body (120–350 lines): identity and seniority (20+ years equivalent, shipped titles in the domain, described generically — never claim to be a real person), mandate and boundaries, operating procedure, the codex skills and scripts they use (by name/path), output formats (file paths and schemas), quality bar and self-review checklist, collaboration (who they hand off to), and red lines.

## 5. Project state convention and ontology schemas

Every game project the plugin manages has a `.gamestudio/` directory at its root:

```
.gamestudio/
├── config.json            # engine, platforms, paths, budgets, revenue thresholds, storefronts, licence allowlist
├── contract.json          # the design contract (one-page truth of the game)
├── features.json          # feature list with five-gate status and evidence
├── progress.md            # dated session log (append-only)
├── budget.json            # asset/audio spend ledger and cap
├── assets/manifest.json   # provenance for every generated or imported asset
├── design/                # living design docs: core-loop.md, ftue.md, world.md, tone-bible.md, decisions.md, liveops-calendar.md, ux/, mechanics/<id>.mechanic.json, features/<F###>.md
├── art/                   # style-bible.md, style-cards.md, asset-list.md, import-presets.md, vfx-budget.md, reviews/
├── audio/                 # audio-bible.md, cue-list.md, music-plan.md, sfx-list.md, qc/
├── concepts/              # concept cards from ideation (concept.schema.json) and ranking.md
├── research/              # market-<slug>.md, positioning.md, comparables.json, market-risks.md, deconstructions/<slug>.json (deconstruction.schema.json)
├── economy/               # economy models (economy-model.schema.json) and sim outputs
├── levels/                # level specs (level-spec.schema.json)
├── analytics/             # event taxonomy (event-taxonomy.schema.json)
├── evidence/<FEATURE-ID>/ # gate evidence: logs, playthrough reports, screenshots, perf reports
├── playtests/             # playtest reports (playtest-report.schema.json)
├── reports/               # reviews, perf reports (perf-report.schema.json), release reports
└── snapshots/             # pre-compaction state snapshots
```

Schemas live in `PLUGIN/scripts/schemas/`. JSON Schema draft 2020-12 subset (type, properties, required, items, enum, const, minimum, maximum, minLength, maxLength, pattern, additionalProperties, $ref to `#/$defs/...`, oneOf, anyOf). All top-level documents carry `"schema_version": "1.0"`.

Field-level essentials (the schema builder writes the full schemas; everyone else uses these names exactly):

**config.json** — `schema_version`, `project` {`title`, `slug`}, `engine` (`godot|unity|unreal|defold|web|other`), `engine_version`, `platforms` [`ios`,`android`], `orientation` (`portrait|landscape|both`), `paths` {`project_root`, `assets_dir` default `assets/`, `generated_dir` default `assets/generated/`}, `budgets` {`asset_usd_cap`, `per_call_usd_cap`}, `revenue` {`lifetime_gross_usd`, `developer_annual_games_revenue_usd`}, `storefronts` [ISO country codes], `licence_allowlist` [strings], `providers` {`image`, `model3d`, `music`, `sfx`, `voice`} preferred provider ids, `tier` (`prototype|slice|soft_launch|global|live`).

**contract.json (design contract)** — `schema_version`; `meta` {`title`, `logline`, `genre`, `subgenre`, `platforms`, `orientation`, `engine`, `target_audience` {`age_min`, `segments`, `motivations`}, `session_length_target_sec`, `monetization_model` (`premium|iap|ads|hybrid|subscription`), `analogy` ("X meets Y"), `comparables` [{`title`, `borrow`, `change`}], `pillars` [3–5 strings]}; `player_fantasy`; `verbs` [{`id`, `input`, `description`}]; `mechanics` [{`id`, `name`, `category`, `verbs`, `rules`, `parameters` [{`key`, `value`, `min`, `max`, `unit`, `note`}], `feedback`, `mobile_notes`}]; `loops` [{`id`, `type` (`core|meta|social|monetization|liveops`), `period` (`seconds|minutes|session|daily|weekly|season`), `steps` [{`id`, `action`, `reward`, `next`}]}]; `economy` {`currencies` [{`id`, `kind` (`soft|hard|premium|energy|event|xp|material`), `sources`, `sinks`, `cap`}], `model_ref` (path to economy model)}; `progression` {`tracks` [{`id`, `type`, `curve` {`formula`, `params`}, `unlocks` [{`at`, `unlock`}]}], `difficulty` {`model`, `target_win_rate`, `dda`}}; `content` {`levels` {`target_count`, `generation` (`handmade|procedural|hybrid`), `spec_ref`}, `worlds`, `characters`}; `ftue` {`aha_seconds_target`, `steps` [{`id`, `goal`, `teaches`, `max_seconds`}]}; `ux` {`hud`, `screens`, `accessibility`}; `art_direction` {`style`, `palette`, `references`, `bible_ref`}; `audio_direction` {`music`, `sfx`, `voice`, `bible_ref`}; `monetization` {`iap` [{`id`, `type`, `price_tier`, `contents`}], `ads` {`rewarded` [placements], `interstitial` {`min_interval_sec`, `first_after_sec`}}, `pass`, `ethics` [rules]}; `liveops` {`cadence`, `events`}; `analytics` {`kpi_targets` {`d1`, `d7`, `d30`, `session_len_sec`, `sessions_per_day`, `arpdau_usd`, `payer_conversion`}, `taxonomy_ref`}; `technical` {`architecture` (default `"sim-core+presentation"`), `deterministic` bool, `min_spec` {`ram_gb`, `gpu_class`, `os_min` {`ios`, `android_api`}}, `perf_budgets` {`fps_target`, `frame_ms_p95`, `memory_mb`, `download_mb`, `cold_start_sec`}, `backend` (`none|firebase|nakama|playfab|custom`), `multiplayer` (`none|async|realtime`)}; `scope` {`tier`, `must`, `should`, `wont`}; `risks` [{`id`, `risk`, `likelihood`, `impact`, `mitigation`}]; `kill_criteria` [strings].

**features.json** — `schema_version`, `features` [{`id` (pattern `^F\d{3,4}$`), `title`, `area` (`gameplay|meta|ui|ux|audio|art|vfx|monetization|analytics|liveops|tech|perf|release|content`), `description`, `acceptance` [strings], `depends_on` [ids], `priority` (`P0|P1|P2`), `status` (`todo|in_progress|blocked|done`), `passes` bool, `gates` {`static`, `unit`, `playthrough`, `visual`, `perf`: each `null|"pass"|"fail"|"n/a"`}, `evidence` {`static`, `unit`, `playthrough`, `visual`, `perf`: each a project-relative path string or list of paths, or null}, `gate_notes` {gate: string}, `owner`, `notes`}].

**assets/manifest.json** — `schema_version`, `assets` [{`id`, `path`, `kind` (`sprite|spritesheet|ui|icon|background|tileset|texture|model|animation|vfx|music|sfx|voice|font|video|other`), `status` (`placeholder|candidate|approved|rejected|final`), `placeholder` bool, `provider`, `model`, `prompt`, `negative_prompt`, `seed`, `references` [paths], `params` {}, `licence` {`terms`, `plan_tier`, `commercial_ok` bool, `attribution` (string|null), `restrictions` [strings]}, `cost_usd`, `created_at` (ISO 8601), `approved_by`, `style_ref`, `sha256`, `derived_from` [asset ids], `notes`}].

**budget.json** — `schema_version`, `cap_usd`, `spent_usd`, `ledger` [{`ts`, `tool`, `provider`, `model`, `cost_usd`, `asset_ids`, `note`}].

**economy-model.schema.json** — `schema_version`, `days`, `archetypes` [{`id`, `share`, `sessions_per_day`, `session_minutes`, `skill` 0–1, `spend_propensity` 0–1, `ad_accept_rate` 0–1}], `resources` [{`id`, `initial`, `cap`}], `nodes` [{`id`, `kind` (`source|sink|converter|gate|pool`), `trigger` (`per_session|per_minute|per_level_attempt|per_level_win|per_level_loss|daily|weekly|on_purchase|on_ad`), `inputs` {res: amount}, `outputs` {res: amount}, `probability`, `condition`}], `levels` {`count`, `base_win_rate`, `difficulty_curve` {`type` (`linear|sawtooth|stepped|custom`), `params`}}, `offers` [{`id`, `price_usd`, `contents` {res: amount}, `trigger`}], `targets` {`days_to_complete_content`, `max_soft_currency_hoard_days`, `payer_conversion`}.

**level-spec.schema.json** — `schema_version`, `level_id`, `mechanic_refs`, `layout` (grid array or generator ref), `goals`, `moves_or_time_limit`, `obstacles`, `difficulty_target` {`win_rate`, `attempts_p50`}, `solver` {`solvable`, `min_moves`, `bot_win_rate`, `runs`}, `teach` (`teach|test|twist|reward`), `notes`.

**event-taxonomy.schema.json** — `schema_version`, `naming` (`snake_case`), `common_params` [..], `events` [{`name`, `category` (`lifecycle|ftue|progression|economy|monetization|ads|social|liveops|tech|ux`), `trigger`, `params` [{`name`, `type`, `required`, `description`}], `kpis` [..]}].

**mechanic-card.schema.json** — `schema_version`, `id`, `name`, `category`, `player_fantasy`, `verbs`, `rules`, `parameters`, `dynamics` (emergent behaviours), `aesthetics` (MDA targets), `feedback`, `failure_modes`, `mobile_fit` {`one_hand`, `session_fit`, `notes`}, `references` [game titles], `combos` [mechanic ids].

**deconstruction.schema.json** — `schema_version`, `game` {`title`, `developer`, `year`, `genre`, `platforms`}, `core_loop` (loop object as in contract), `meta_loops`, `mechanics` [mechanic-card-like], `economy` {`currencies`, `sources`, `sinks`}, `progression`, `monetization` {`model`, `top_offers`, `ads`}, `liveops`, `retention_hooks`, `social`, `ux_notable`, `art_audio_notable`, `psychology` [principles used], `innovations`, `weaknesses`, `lessons` [strings], `borrow_for_us` [strings], `sources` [urls].

**concept.schema.json** — `schema_version`, `id`, `title`, `logline`, `analogy`, `genre`, `player_fantasy`, `core_loop`, `hook` (the novel twist), `pillars`, `target_audience`, `monetization_model`, `comparables`, `scores` {`market`, `novelty`, `fun_potential`, `feasibility`, `monetization`, `production_cost`, `agent_buildability`} each 1–10, `risks`, `kill_criteria`, `rationale`.

**playtest-report.schema.json** — `schema_version`, `feature_id` (optional), `build`, `mode` (`deterministic_script|bot|persona|human`), `runs`, `seed`, `steps` [{`t`, `action`, `expect`, `observed`, `ok`}], `metrics` {`win_rate`, `avg_session_sec`, `time_to_first_reward_sec`, `softlocks`, `crashes`, `errors`}, `screenshots` [paths], `findings` [{`severity` (`blocker|major|minor|polish`), `title`, `detail`, `repro`}], `verdict` (`pass|fail`).

**perf-report.schema.json** — `schema_version`, `build`, `device` {`name`, `tier` (`low|mid|high`), `os`}, `scenario`, `duration_sec`, `fps` {`avg`, `p1_low`}, `frame_ms` {`p50`, `p95`, `p99`}, `memory_mb` {`peak`, `avg`}, `draw_calls`, `cpu_ms`, `gpu_ms`, `thermal` {`start`, `end`}, `download_mb`, `cold_start_sec`, `budgets` {..}, `violations` [strings], `verdict` (`pass|fail`).

## 6. The five gates (definition of done)

A feature may only have `passes: true` (and `status: "done"`) when every gate is `"pass"` or `"n/a"`, and every `"pass"` gate has an evidence path that exists on disk:

| Gate | Meaning | Typical evidence |
|---|---|---|
| `static` | Code parses/compiles, lints clean (Godot `--check-only`, Roslyn/Unity compile), schemas validate | `.gamestudio/evidence/F012/static.log` |
| `unit` | Headless unit tests for the feature pass (GdUnit4, Unity Test Framework) | `.../unit.xml` or `unit.log` |
| `playthrough` | A deterministic scripted playthrough with input injection and state assertions passes; or bot runs meet targets | `.../playthrough.json` (playtest-report schema) |
| `visual` | Screenshot(s) or a recorded clip cleared the critic's rubric (structural UI checks first, then VLM review) | `.../shot_01.png`, `.../visual_review.md` |
| `perf` | Within the contract's `perf_budgets` on the reference scenario/device tier | `.../perf.json` from `tools/perf/perf_probe.gd` (perf-report schema), checked with `perf_budget.py` |

`"n/a"` requires a `gate_notes` entry explaining why (e.g. a pure data feature has no visual gate). Hooks and `gs.py feature pass` both enforce this rule using the shared library `scripts/gslib.py`.

## 7. Shared Python library: `scripts/gslib.py` (owned by the core-CLI builder)

Hooks and scripts import it by adding the plugin's `scripts/` dir to `sys.path` (compute it from `__file__`). API:
- `find_project_root(start: str | Path) -> Path | None` — nearest ancestor containing `.gamestudio/`.
- `gs_dir(root) -> Path`
- `load_json(path, default=None)`, `save_json(path, data)` (atomic write, indent 2, trailing newline)
- `load_state(root) -> dict` with keys `config`, `contract`, `features`, `manifest`, `budget` (missing → None)
- `GATES = ("static", "unit", "playthrough", "visual", "perf")`
- `check_feature_pass(feature: dict, root: Path) -> tuple[bool, list[str]]`
- `feature_counts(features_doc) -> dict` (total, done, passing, in_progress, blocked, todo)
- `next_feature(features_doc) -> dict | None` (highest priority `todo` whose deps all pass)
- `summarize(root, max_chars=2500) -> str` (for SessionStart)
- `schema_for(path) -> Path | None` and `validate_file(path) -> list[str]` (errors; uses `scripts/validate_json.py`)
- `append_progress(root, text)`
- `cross_check(root) -> list[tuple[str, str]]` — (severity, message) pairs, errors first, never raises: duplicate ids (features, assets, events, mechanics, currencies), unknown `depends_on`, level `mechanic_refs` not in the contract, missing evidence for passing gates (errors); offers without a contract IAP id, contract currencies without an economy resource, missing manifest files (warnings)

## 8. `gs.py` CLI (owned by the core-CLI builder)

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py init --title "Name" --engine godot|unity|other [--genre G] [--root DIR]
gs.py status [--json]
gs.py validate [--all | PATH ...] [--cross]     # --cross adds cross-document checks (gslib.cross_check); exit 1 on errors
gs.py feature list [--status S] [--json]
gs.py feature add --id F001 --title T --area A [--priority P0] [--accept "..."]... [--depends F001,F002] [--desc TEXT]
gs.py feature next [--json]
gs.py feature start F001
gs.py feature gate F001 <static|unit|playthrough|visual|perf> <pass|fail|n/a> [--evidence PATH]... [--note TEXT]
gs.py feature pass F001
gs.py feature block F001 --reason TEXT
gs.py evidence-dir F001            # creates and prints .gamestudio/evidence/F001/
gs.py progress "text"               # appends a dated entry to progress.md
gs.py budget [--json]
gs.py feature show F001 | gs.py summary         # also available: feature start --reopen, gate result 'reset'; every command takes --root and --json
gs.py kb "query" [--skill NAME] [--limit N] [--json]   # ranked search across PLUGIN/skills/**.md
gs.py map                         # project map: .gamestudio/map/MAP.md + map.json (incremental)
gs.py impact TARGET...            # dependents, tests, features and gates a change touches
gs.py whatif --set KEY=VALUE      # current vs proposed on the same seeds; verdict against contract targets
gs.py dashboard                   # offline .gamestudio/reports/dashboard.html
```

## 9. Asset & audio gateway MCP server: `studio-gateway`

Location `PLUGIN/mcp/studio-gateway/server.mjs` (+ `lib/*.mjs`, `providers/*.mjs`, `pricing.json`, `README.md`, `test/*.mjs`). Stdio JSON-RPC 2.0 MCP server, zero dependencies, implements `initialize` (echo a supported protocol version), `notifications/initialized`, `tools/list`, `tools/call`, `ping`. Tool results are `content: [{type: "text", text: <concise JSON or markdown>}]`, with `isError: true` on failure.

Environment (from `.mcp.json`, populated by plugin userConfig): `GEMINI_API_KEY`, `OPENAI_API_KEY`, `RECRAFT_API_KEY`, `FAL_KEY`, `TRIPO_API_KEY`, `MESHY_API_KEY`, `ELEVENLABS_API_KEY`, `STABILITY_API_KEY`, `GS_ASSET_BUDGET_USD`, `GS_PLUGIN_ROOT`, `GS_PLUGIN_DATA`, optional `GS_MOCK=1`, optional model overrides `GS_MODEL_<PROVIDER>_<KIND>`. Empty strings mean "not configured".

Tools (names are final):
- `gs_status` — project root, budget, which providers are configured, mock mode.
- `image_generate` {prompt, kind, provider? (`auto|gemini|openai|recraft|fal`), model?, size?, n? (1–4), references? [paths], transparent?, seed?, style_ref?, out_dir?, id_prefix?, dry_run?}
- `image_edit` {source, prompt, references?, provider?, n?}
- `image_postprocess` {path, op (`remove_background|vectorize|upscale`), provider?}
- `model3d_generate` {prompt? | image?, provider (`tripo|meshy`), face_limit?, texture? (bool), pbr?, rig?, out_dir?, wait_sec? (default 240)} → returns files or a `task_id`
- `model3d_status` {provider, task_id, out_dir?}
- `audio_music` {prompt, duration_sec, instrumental? (default true), provider? (`elevenlabs|lyria`), composition_plan?}
- `audio_sfx` {prompt, duration_sec?, loop?, provider? (`elevenlabs`)}
- `audio_voice` {text, voice_id? | voice_description?, provider? (`elevenlabs|gemini`), model?, lines? (dialogue array)}
- `manifest_query` {kind?, status?, provider?, text?, limit?}
- `manifest_update` {asset_id, status?, approved_by?, notes?, licence?}
- `licence_check` {asset_id?} — flags non-commercial terms, free-tier ownership problems, revenue-threshold licences (e.g. ElevenLabs Music indie limits) against `config.revenue`, missing provenance.
- `budget_status` {}
- `kb_search` {query, skill?, limit?} — searches `PLUGIN/skills/**/*.md`, returns ranked snippets with file paths.

Rules: every generation writes files under the project's `generated_dir`, appends manifest entries (`status: "candidate"`), appends a budget ledger entry, and refuses calls whose estimated cost would exceed the remaining cap. When a provider key is missing, `GS_MOCK=1`, or `dry_run` is set, it produces valid placeholder files (PNG, WAV, minimal GLB) with `placeholder: true` and `cost_usd: 0`. Model ids are configurable; defaults and list prices live in `pricing.json` with an "as of Oct 2026, verify" note.

## 10. Hooks contract (owned by the hooks builder)

`PLUGIN/hooks/hooks.json` + `PLUGIN/hooks/scripts/*.py` (Python 3.9 stdlib). Commands use exec form, `"command": "node", "args": ["${CLAUDE_PLUGIN_ROOT}/hooks/scripts/run-python.mjs", "${CLAUDE_PLUGIN_ROOT}/hooks/scripts/<x>.py"]`: no shell, and the launcher picks `python3`, `python` or `py -3`, so the same file works on macOS, Linux and Windows (with or without Git Bash). Shell guards match `Bash|PowerShell`. Every hook is a no-op (exit 0, no output) when the project has no `.gamestudio/` directory, except the SessionStart hint. Hooks fail open on internal errors (exit 0, note on stderr) except explicit deny rules.

| Event | Script | Behaviour |
|---|---|---|
| SessionStart | `session_start.py` | Inject `gslib.summarize()` as `additionalContext`; if an engine project without `.gamestudio/` is detected, inject a one-line hint to run `/arcosian:studio`. |
| PreToolUse (Bash) | `pre_tool_guard.py` | `ask` before store submission/promotion and PC store upload commands (steamcmd +run_app_build, butler push, BuildPatchTool, msstore publish, fastlane deliver/upload_to_app_store/submit_for_review/supply to production, altool/notarytool uploads, Play publishing); `deny` reading or printing signing secrets (keystores, .p12, .mobileprovision contents, .env with keys, `security find-generic-password`); `ask` before `rm -rf` of `.gamestudio`, `assets`, or the project root. |
| PreToolUse (Write/Edit on `.gamestudio/features.json`) | `pre_tool_guard.py` | Reconstruct the resulting JSON; `deny` if any feature becomes `passes: true` or `status: "done"` without passing `check_feature_pass`, or if a passing feature is deleted. |
| PostToolUse (Write/Edit/MultiEdit) | `post_tool_check.py` | `.gd`: if a Godot binary is available (`GODOT_BIN`, `godot`, `godot4`), run a headless parse check; block with errors. `.tscn/.tres`: duplicate `uid://` linter across the project; block on duplicates. `.gamestudio/**.json`: schema-validate; block on errors. New binary assets under `assets/` not in the manifest: add an `additionalContext` reminder. |
| Stop, SubagentStop | `stop_gate.py` | If `stop_hook_active` → exit 0. Block if any feature is `status: "done"` but fails `check_feature_pass`. |
| TaskCompleted | `task_gate.py` | If the task text references a feature id whose `passes` is false → exit 2 with the missing gates. |
| PreCompact | `pre_compact.py` | Write `.gamestudio/snapshots/precompact-<timestamp>.md` with the summary. |

## 11. Catalog

### 11.1 Process skills (user-facing commands, `/arcosian:<name>`)
| Skill | Purpose |
|---|---|
| `studio` | Entry point. Boots the principal persona, detects project state, explains the pipeline, routes to the right next step. |
| `new-game` | Brief → market scan → concept tournament → design contract → feature plan → project init (`gs.py init`). |
| `concept-lab` | Ideation methods (analogy, constraint inversion, mechanic transplant, market gap, player-motivation-first), concept cards, scoring rubric, runs `concept-tournament`. |
| `design-review` | Multi-discipline review of the design contract (design, economy, UX, monetization ethics, tech feasibility, market, scope), runs `design-review` workflow. |
| `market-scan` | Competitive and market research for a genre or concept; runs `market-scan` workflow. |
| `deconstruct` | Deconstructs any game into the ontology (deconstruction schema); runs `deconstruct-game`. |
| `build-feature` | Implements one feature through the five gates; runs `build-feature` workflow. |
| `playtest` | Deterministic playthroughs, bots, persona playtests, visual QA; runs `playtest-sweep`. |
| `balance` | Economy and difficulty tuning with simulators; runs `balance-pass`. |
| `optimize` | Performance pass against budgets on the target platforms. |
| `asset-production` | Visual asset pipeline through `studio-gateway` with style lock; runs `asset-batch`. |
| `audio-production` | Music/SFX/voice pipeline with loop and loudness QC. |
| `ship` | Release pipeline: compliance pre-flight, signed builds, store metadata, TestFlight/Play internal; runs `release-candidate`; never submits for review without explicit human approval. |
| `operate` | Post-launch: analytics review, live-ops calendar, A/B tests, remote config, crash triage. |
| `postmortem` | Structured postmortem and knowledge capture. |

### 11.2 Codex skills
`game-ontology`, `design-theory`, `design-philosophies`, `mechanics-codex`, `genre-playbooks`, `game-case-studies`, `analogy-engine`, `player-psychology`, `player-analytics`, `economy-design`, `progression-difficulty`, `level-design`, `procedural-generation`, `narrative-design`, `game-feel`, `mobile-ux`, `art-direction`, `technical-art`, `audio-direction`, `game-architecture`, `gameplay-programming`, `multiplayer-backend`, `mobile-performance`, `engine-godot`, `engine-unity`, `engine-alternatives`, `ai-asset-pipeline`, `ai-audio-pipeline`, `qa-testing`, `monetization`, `liveops`, `store-release`, `marketing-ua`, `production`, `market-intel`, `game-glossary`, `legal-ethics`, `accessibility-localization`.

### 11.3 Agents (`arcosian:<name>`)
| Agent | Model | Role |
|---|---|---|
| `principal` | opus | Principal game developer / game director. Owns vision, the contract, and orchestration; delegates; final sign-off below human checkpoints. |
| `game-designer` | opus | Core loop, mechanics, rules, FTUE, feature specs. |
| `systems-designer` | opus | Economy, progression, balance, simulation. |
| `level-designer` | sonnet | Level design, content pipelines, solvers, PCG. |
| `narrative-designer` | sonnet | World, characters, dialogue, meta-narrative, tone bible. |
| `ux-designer` | sonnet | UX/UI flows, HUD, onboarding, accessibility for every target platform. |
| `art-director` | opus | Style bible, art direction, asset briefs, visual critique. |
| `technical-artist` | sonnet | Shaders, VFX, atlases, import pipelines, art perf. |
| `audio-director` | sonnet | Audio bible, music/SFX/voice direction and implementation. |
| `lead-engineer` | opus | Architecture (sim-core + presentation), code standards, tech risks. |
| `gameplay-engineer` | sonnet | Implements features in the engine with tests. |
| `godot-engineer` | sonnet | Godot 4 specialist (GDScript, scenes, export, plugins). |
| `unity-engineer` | sonnet | Unity 6 specialist (C#, URP, editor scripting, packages). |
| `performance-engineer` | sonnet | Profiling, budgets, optimization, device tiers. |
| `qa-lead` | sonnet | Test strategy, deterministic playthroughs, bots, visual QA, gates. |
| `player-simulator` | sonnet | Plays builds as defined personas; reports experience and friction. |
| `data-analyst` | sonnet | Telemetry design, KPIs, cohorts, A/B analysis, retention/LTV models. |
| `monetization-designer` | opus | IAP, ads, offers, pricing, battle pass — ethically. |
| `liveops-manager` | sonnet | Events, calendar, segmentation, remote config, CRM. |
| `market-analyst` | sonnet | Market, competitors, trends, positioning. |
| `producer` | sonnet | Scope, milestones, risks, feature list, progress, budgets. |
| `release-manager` | sonnet | Builds, signing, CI, store metadata, compliance pre-flight. |
| `critic` | opus | Adversarial reviewer of fun, quality and claims; refutes before approving. |
| `compliance-officer` | sonnet | Store policy, privacy, age, loot-box law, licences, AI disclosure. |

### 11.4 Workflows (`/arcosian:<meta.name>`)
`concept-tournament`, `deconstruct-game`, `design-review`, `market-scan`, `build-feature`, `asset-batch`, `playtest-sweep`, `balance-pass`, `release-candidate`. Workflow agents may use `agentType: 'arcosian:<agent>'` and invoke skills via the Skill tool.

### 11.5 Scripts (`PLUGIN/scripts/`)
`gslib.py`, `gs.py`, `validate_json.py`, `economy_sim.py`, `progression_calc.py`, `gacha_calc.py`, `difficulty_curve.py`, `ab_test.py`, `retention_ltv.py`, `event_taxonomy.py`, `puzzle_solver.py`, `match3_sim.py`, `pcg.py`, `compliance_preflight.py`, `store_metadata.py`, `perf_budget.py`, `audio_post.py`, `image_post.py`.

### 11.6 Templates
`templates/godot-starter/` (sim-core + presentation architecture, services, playtest runner, tests, export presets), `templates/unity-starter/` (Core/Presentation/Editor assemblies, SceneBuilder, BuildScript, tests), `templates/ci/` (GitHub Actions for Godot and Unity, fastlane, Codemagic), `templates/docs/` (one-page GDD, style bible, audio bible, playtest plan, soft-launch plan, postmortem, pitch).

## 12. Builder self-check before finishing

- [ ] Every file is inside your assigned paths.
- [ ] Frontmatter is valid YAML, `name` matches the directory/file, description ≤ limit.
- [ ] Every reference file is listed in the SKILL.md reference table, and every listed file exists.
- [ ] No invented facts; volatile facts are labelled and sourced.
- [ ] Scripts pass `--selftest`; Node tests pass; JSON files parse.
- [ ] Cross-references use the exact names in section 11.
- [ ] Your final reply is a compact JSON-ish summary: files written (with line counts), self-test results, known gaps.

## 13. Runtime interfaces of the templates (binding for templates, process skills, agents, workflows)

**Godot template** (`templates/godot-starter/`, sample game: a deterministic 5×5 "merge numbers" puzzle that exercises the sim-core + presentation split):
```
# static gate (load/parse every .gd under res://, report errors; exit code 0/1)
godot --headless --path <project> -s res://tools/ci/check_all.gd -- --out=<abs>/static.log
# unit tests (built-in zero-dependency runner over res://tests/unit/test_*.gd; JUnit XML; exit 0/1). GdUnit4 optional.
godot --headless --path <project> -s res://tools/ci/run_tests.gd -- --out=<abs>/unit.xml
# deterministic scripted playthrough → playtest-report JSON
godot --headless --path <project> -s res://tools/playtest/runner.gd -- --mode=script --script=res://tests/playthroughs/smoke.json --out=<abs>/playthrough.json [--seed=1]
# bot runs (difficulty / softlock estimation)
godot --headless --path <project> -s res://tools/playtest/runner.gd -- --mode=bot --bot=greedy|random --runs=200 --seed=1 --out=<abs>/bots.json
# screenshots for the visual gate and store (needs a renderer; on CI use xvfb-run)
godot --path <project> -s res://tools/capture/screenshot_mode.gd -- --out=<abs dir> --screens=menu,game,results
# perf gate → perf-report JSON (windowed = real renderer; --headless = CPU-only, draw_calls/gpu_ms null); exit 0 pass, 1 over budget, 2 cannot run
godot [--headless] --path <project> -s res://tools/perf/perf_probe.gd -- --out=<abs>/perf.json [--seconds=20] [--budget-frame-ms=16.7] [--budget-memory-mb=512] [--budget-fps=60]
# exports
godot --headless --path <project> --export-release "Android" <out>.aab
godot --headless --path <project> --export-release "iOS" <out-dir>/game.xcodeproj
```
Playthrough script format (`tests/playthroughs/*.json`): `{"schema_version":"1.0","seed":1,"steps":[{"action":{"type":"<action>", ...},"expect":{"<state path>": <value or {"op": ">=", "value": n}>}}]}`. Runner output follows `playtest-report.schema.json`.

**Unity template** (`templates/unity-starter/`, same sample game):
```
Unity -batchmode -nographics -projectPath <p> -runTests -testPlatform EditMode -testResults <abs>/unit.xml -logFile <abs>/unity.log
Unity -batchmode -nographics -projectPath <p> -executeMethod Game.EditorTools.PlaytestRunner.Run -gsMode script -gsScript Assets/_Game/Tests/Playthroughs/smoke.json -gsOut <abs>/playthrough.json -quit
Unity -batchmode -nographics -projectPath <p> -executeMethod Game.EditorTools.SceneBuilder.BuildAll -quit
Unity -batchmode -nographics -projectPath <p> -executeMethod Game.EditorTools.BuildScript.BuildAndroid -gsOut Builds/Android/game.aab -quit
Unity -batchmode -nographics -projectPath <p> -executeMethod Game.EditorTools.BuildScript.BuildIOS -gsOut Builds/iOS -quit
```

## 14. Script command lines (binding; owners implement exactly these, everyone else calls exactly these)

```
economy_sim.py --model PATH [--runs N=200] [--seed S=1] [--days D] [--json] [--out PATH]
progression_calc.py curve --formula linear|poly|exp|logistic|piecewise --levels N [--base B] [--growth G] [--exponent E] [--xp-per-min X] [--json]
progression_calc.py time-to-level --table PATH --xp-per-min X [--json]
gacha_calc.py --rate R [--soft-pity-start N] [--soft-pity-step S] [--hard-pity N] [--rate-up P] [--guarantee] [--pulls N] [--json]
difficulty_curve.py generate --levels N --pattern linear|sawtooth|stepped --base WINRATE --floor WINRATE [--period P] [--hard-every K] [--json]
difficulty_curve.py analyze --data CSV(level,attempts,wins,churned) [--json]
ab_test.py size --baseline P --mde D [--alpha 0.05] [--power 0.8] [--two-sided]
ab_test.py analyze --a-success X --a-n N --b-success Y --b-n M [--json]
ab_test.py mean --a-mean --a-sd --a-n --b-mean --b-sd --b-n [--json]
ab_test.py sequential --baseline P --mde D --looks K [--alpha 0.05] [--json]
retention_ltv.py fit --points "1:0.42,7:0.18,30:0.07" [--model power|exp] [--json]
retention_ltv.py ltv --points "..." --arpdau A [--horizon 365] [--json]
event_taxonomy.py generate --contract PATH --out PATH
event_taxonomy.py stubs --taxonomy PATH --engine godot|unity --out DIR
puzzle_solver.py --level PATH [--algo bfs|astar] [--max-nodes N] [--json]     # level-spec with layout.type in {sliding, sokoban, sort, lights_out}
match3_sim.py --level PATH [--runs N=500] [--bot greedy|random|cascade] [--seed S] [--json]
pcg.py wfc|bsp|cave|noise|poisson|maze --w W --h H [--seed S] [--json] [--out PATH]
compliance_preflight.py --project DIR [--platform ios|android|all] [--json]
store_metadata.py --contract PATH --out DIR [--locales en-US,de-DE] [--json]
perf_budget.py --report PATH [--contract PATH] [--json]      # report: perf-report JSON or CSV of frame times (ms)
audio_post.py normalize|trim|loop|convert|qc --in PATH [--out PATH] [--lufs -16] [--tp -1] [--format ogg|m4a|wav] [--json]
image_post.py check|palette|resize|atlas|pixelate --in PATH(s) [--out PATH] [--json]
```
