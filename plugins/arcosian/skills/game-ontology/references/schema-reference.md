# Schema reference: every ontology document, field by field

This is the working guide to the thirteen JSON schemas in `${CLAUDE_PLUGIN_ROOT}/scripts/schemas/`. For each document it gives the file location and name pattern, required fields, the meaning and constraints of every field that matters, the enums, common mistakes, and the validation command. The schemas are the authority: when this file and a schema disagree, the schema wins, so re-check with `validate_json.py`. Read it when writing or reviewing any `.gamestudio/` document, or when a validation error needs interpreting.

## Contents
1. Validation commands and exit codes
2. Shared definitions (`common.schema.json`)
3. `config.json`
4. `contract.json` (design contract)
5. `features.json`
6. `assets/manifest.json`
7. `budget.json`
8. Economy model
9. Level spec
10. Event taxonomy
11. Mechanic card
12. Deconstruction
13. Concept card
14. Playtest report
15. Perf report
16. Common validation errors and fixes

## 1. Validation commands and exit codes

```bash
# Validate files or directories; the schema is inferred from the file name
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_json.py --auto PATH [PATH ...]

# Force a schema by file path
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_json.py --schema ${CLAUDE_PLUGIN_ROOT}/scripts/schemas/level-spec.schema.json --instance my.json

# Machine-readable output
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_json.py --auto PATH --json

# List the file-name rules, lint schemas, run the self-test
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_json.py --list
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_json.py --lint
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_json.py --selftest

# Whole project: every JSON file under .gamestudio/ plus the feature-list rules
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py validate --root PROJECT_DIR
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py validate --schema level-spec path/to/odd-name.json
```

Exit codes for both tools: 0 valid, 1 validation failed, 2 usage or input error (for example a missing file).

Inference rules (from `validate_json.py --list`): `config.json`, `contract.json` (or `design-contract.json`), `features.json`, `manifest.json`, `budget.json`, `playthrough.json` and `bots.json` (playtest report), `perf.json` (perf report), and the suffixes `*.economy.json`, `*.level.json`, `*.taxonomy.json`, `*.mechanic.json`, `*.deconstruction.json`, `*.concept.json`, `*.playtest.json`, `*.perf.json`. A file with another name falls back to its top-level `"$schema_name"` field (for example `"$schema_name": "level-spec"`). `gs.py validate --schema NAME` accepts a name or a path.

Every document starts with `"schema_version": "1.0"` (the value is a `const`). Tools refuse a future major version rather than guess.

## 2. Shared definitions (`common.schema.json`)

| Definition | Shape | Notes |
|---|---|---|
| `id` | string matching `^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$` | Stable identifiers |
| `id_list` | array of unique ids | References to other objects |
| `feature_id` | `^F\d{3,4}$` | `F001` to `F9999` |
| `slug` | kebab-case, at most 64 chars | Folder and URL safe |
| `iso_datetime`, `iso_date` | ISO 8601 | `2026-10-12T09:14:03Z`, `2026-10-18` |
| `path` | non-empty string | Prefer project-relative, forward slashes |
| `project_rel_path` | no leading `/`, no drive letter, no `..` | Used for evidence paths |
| `url` | `^https?://\S+$` | |
| `ratio` | number 0 to 1 | Never 0 to 100 |
| `usd` | number at least 0 | Decimal dollars |
| `string_list` | array of non-empty strings | |
| `text_or_list` | string or array of strings | |
| `platform` | `ios`, `android`, `web`, `windows`, `macos`, `linux`, `switch`, `playstation`, `xbox`, `other` | `platform_list` is unique |
| `orientation` | `portrait`, `landscape`, `both` | |
| `engine` | `godot`, `unity`, `unreal`, `defold`, `web`, `other` | |
| `monetization_model` | `premium`, `iap`, `ads`, `hybrid`, `subscription` | |
| `tier` | `prototype`, `slice`, `soft_launch`, `global`, `live` | Production stage |
| `likelihood_impact` | `low`, `medium`, `high`, or 1 to 5 | |
| `resource_amounts` | object: resource id to number | `{"coins": 40}` |

Structured shared objects:

| Object | Required | Fields |
|---|---|---|
| `verb` | `id` | `input` (string), `description` |
| `parameter` | `key` | `value` (number, string, boolean or null), `min`, `max` (number or null), `unit`, `note` |
| `comparable` | `title` | `borrow`, `change` (each `text_or_list`) |
| `target_audience` | none | `age_min` (integer at least 0), `segments`, `motivations` |
| `loop_step` | `id`, `action` | `reward` (string, object or null), `next` (string, array or null) |
| `loop` | `id`, `steps` | `name`, `type` (`core`, `meta`, `social`, `monetization`, `liveops`), `period` (`seconds`, `minutes`, `session`, `daily`, `weekly`, `season`), `description` |
| `mechanic` | `id` | `name`, `category`, `verbs` (id list), `rules` (string list), `parameters`, `feedback`, `mobile_notes` |
| `licence` | none | `terms`, `plan_tier` (string or null), `commercial_ok` (boolean), `attribution` (string or null), `restrictions` |

## 3. `config.json`

Path `.gamestudio/config.json`. Required: `schema_version`, `project` (with `title`).

| Field | Meaning | Constraints |
|---|---|---|
| `project` | `{title, slug}` | `title` min length 1; `slug` kebab-case |
| `engine`, `engine_version` | Engine and version | Version pattern `^\d+(\.\d+){0,3}...`, e.g. `4.5` |
| `platforms`, `orientation` | Targets | Shared enums |
| `paths` | `{project_root, assets_dir, generated_dir}` | Defaults `.`, `assets/`, `assets/generated/` |
| `budgets` | `{asset_usd_cap, per_call_usd_cap}` | USD |
| `revenue` | `{lifetime_gross_usd, developer_annual_games_revenue_usd}` | Feeds licence checks on asset terms |
| `storefronts` | Country codes | Array of strings |
| `licence_allowlist` | Licence terms accepted without review | String list |
| `providers` | `{image, model3d, music, sfx, voice}` | Provider id string or null |
| `tier` | Production stage | `tier` enum |

Mistake: putting secrets here. Keys come from environment variables, never from config.

## 4. `contract.json` (design contract)

Path `.gamestudio/contract.json`. Required: `schema_version`, `meta` (with `title`). Everything else is optional so a contract can grow with the tier, but a `slice` or later contract should have every section.

| Section | Fields | Notes |
|---|---|---|
| `meta` | `title`, `logline`, `genre`, `subgenre`, `platforms`, `orientation`, `engine`, `target_audience`, `session_length_target_sec` (10 to 7200), `monetization_model`, `analogy`, `comparables[]`, `pillars[]` | Pillars: 3 to 5 by convention |
| `player_fantasy` | string | One sentence |
| `verbs[]` | `{id, input, description}` | Core set of 1 to 3 on casual mobile |
| `mechanics[]` | `{id, name, category, verbs, rules, parameters, feedback, mobile_notes}` | `verbs` are verb ids |
| `loops[]` | loop objects | Expect a core and a meta loop |
| `economy` | `currencies[] {id, kind, sources, sinks, cap}`, `model_ref` | Currency `kind` values are `soft`, `hard`, `premium`, `energy`, `event`, `xp`, `material` by convention; `model_ref` points to `*.economy.json` |
| `progression` | `tracks[] {id, type, curve {formula, params}, unlocks[] {at, unlock}}`, `difficulty {model, target_win_rate, dda}` | `target_win_rate` is a ratio; `dda` may be boolean, string or object |
| `content` | `levels {target_count, generation, spec_ref}`, `worlds`, `characters` | `generation`: `handmade`, `procedural`, `hybrid` |
| `ftue` | `aha_seconds_target`, `steps[] {id, goal, teaches, max_seconds}` | `teaches` is a verb id list or a sentence |
| `ux` | `hud`, `screens`, `accessibility` | String, array or object |
| `art_direction` | `style`, `palette`, `references`, `bible_ref` | |
| `audio_direction` | `music`, `sfx`, `voice`, `bible_ref` | |
| `monetization` | `iap[]`, `ads {rewarded[], interstitial}`, `pass`, `ethics[]` | Interstitial uses `min_interval_sec` and `first_after_sec` |
| `liveops` | `cadence`, `events[]` | |
| `analytics` | `kpi_targets {d1, d7, d30, session_len_sec, sessions_per_day, arpdau_usd, payer_conversion}`, `taxonomy_ref` | Retention targets are ratios |
| `technical` | `architecture` (default `sim-core+presentation`), `deterministic`, `min_spec`, `perf_budgets {fps_target (15 to 240), frame_ms_p95, memory_mb, download_mb, cold_start_sec}`, `backend` (`none`, `firebase`, `nakama`, `playfab`, `custom`), `multiplayer` (`none`, `async`, `realtime`) | |
| `scope` | `tier`, `must[]`, `should[]`, `wont[]` | `wont` is as important as `must` |
| `risks[]` | `{id, risk, likelihood, impact, mitigation}` | `likelihood_impact` values |
| `kill_criteria[]` | strings | Each testable |

Validate: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_json.py --auto .gamestudio/contract.json`

Mistakes: retention targets written as `40` rather than `0.4`; `verbs` in a mechanic naming ids that are not in `verbs[]`; `model_ref` pointing to a file that does not exist; a currency in `economy.currencies` absent from the economy model's `resources`.

## 5. `features.json`

Path `.gamestudio/features.json`. Required: `schema_version`, `features[]`.

Feature: required `id`, `title`. Optional `area`, `description`, `acceptance[]`, `depends_on[]`, `priority`, `status`, `passes`, `gates`, `evidence`, `gate_notes`, `owner`, `notes`.

| Field | Constraint |
|---|---|
| `id` | `^F\d{3,4}$`, never reused |
| `title` | 1 to 120 characters, imperative |
| `area` | `gameplay`, `meta`, `ui`, `ux`, `audio`, `art`, `vfx`, `monetization`, `analytics`, `liveops`, `tech`, `perf`, `release`, `content` |
| `priority` | `P0`, `P1`, `P2` |
| `status` | `todo`, `in_progress`, `blocked`, `done` |
| `passes` | Boolean; set by `gs.py feature pass`, never by hand |
| `depends_on` | Unique feature ids; `gs.py feature next` offers only features whose dependencies pass |
| `gates` | Exactly the keys `static`, `unit`, `playthrough`, `visual`, `perf` (unknown keys rejected); each `null`, `"pass"`, `"fail"` or `"n/a"` |
| `evidence` | Same five keys; each a project-relative path, a list of paths, or null |
| `gate_notes` | Per-gate strings; required wherever a gate is `"n/a"` |

Rules enforced beyond the schema (`gs.py`, `gslib.py`, hooks): `status: "done"` requires `passes: true`; `passes: true` requires every gate to be `pass` or `n/a`, every `pass` gate to have an evidence path that exists on disk, and every `n/a` gate to have a note. The definition of the gates is in `docs/BLUEPRINT.md` section 6.

Validate the whole project with `gs.py validate`, which also applies the cross-field rules.

## 6. `assets/manifest.json`

Path `.gamestudio/assets/manifest.json`. Required: `schema_version`, `assets[]`; ids must be unique. Asset required: `id`, `path`.

| Field | Meaning |
|---|---|
| `kind` | `sprite`, `spritesheet`, `ui`, `icon`, `background`, `tileset`, `texture`, `model`, `animation`, `vfx`, `music`, `sfx`, `voice`, `font`, `video`, `other` |
| `status` | `placeholder`, `candidate`, `approved`, `rejected`, `final` |
| `placeholder` | Boolean; true for stand-ins that must be replaced before release |
| `provider`, `model`, `prompt`, `negative_prompt`, `seed`, `references`, `params` | Provenance of generation; keep enough to reproduce or explain |
| `licence` | `licence` object (terms, plan tier, `commercial_ok`, attribution, restrictions) |
| `cost_usd`, `created_at`, `approved_by`, `style_ref`, `sha256`, `derived_from`, `notes` | Ledger link, audit trail, lineage by asset ids |

Mistake: leaving `licence.commercial_ok` unset for generated assets; the pipeline compares it against `config.revenue` and `licence_allowlist`.

## 7. `budget.json`

Path `.gamestudio/budget.json`. Required: `schema_version`, `cap_usd`. Fields: `spent_usd`, `ledger[]`. Ledger entry required: `ts`, `tool`, `cost_usd`; optional `provider`, `model` (string or null), `asset_ids`, `note`. Convention to keep: `spent_usd` equals the sum of ledger costs; compare against `gs.py budget` output after every call.

## 8. Economy model

Path `.gamestudio/economy/NAME.economy.json`. Required: `schema_version`, `resources`, `nodes`.

| Field | Constraint and meaning |
|---|---|
| `name`, `days` | Label; horizon 1 to 3650 days |
| `archetypes[]` | Required `id`, `share` (ratio); `sessions_per_day`, `session_minutes`, `skill`, `spend_propensity`, `ad_accept_rate` (the last three are ratios). Shares should sum to 1 |
| `resources[]` | Required `id`; `initial` (at least 0), `cap` (number or null = uncapped) |
| `nodes[]` | Required `id`, `kind`, `trigger`; `inputs`, `outputs` (resource amounts), `probability` (ratio), `condition` (guard expression), `note` |
| `nodes[].kind` | `source`, `sink`, `converter`, `gate`, `pool` |
| `nodes[].trigger` | `per_session`, `per_minute`, `per_level_attempt`, `per_level_win`, `per_level_loss`, `daily`, `weekly`, `on_purchase`, `on_ad` |
| `levels` | `count`, `base_win_rate`, `difficulty_curve {type: linear|sawtooth|stepped|custom, params}` |
| `offers[]` | Required `id`, `price_usd`; `contents` (resource amounts), `trigger` (string) |
| `targets` | `days_to_complete_content`, `max_soft_currency_hoard_days`, `payer_conversion` (ratio) |

Mappings from Machinations-style primitives are in `references/loops-flows-and-mda.md` section 4. Simulate with `economy_sim.py` (see skill `economy-design`). Mistakes: shares summing to 1.2; a node referencing a resource id missing from `resources`; `probability` written as `20`; guard conditions using syntax beyond comparisons joined by `and` or `or`.

## 9. Level spec

Path `.gamestudio/levels/NAME.level.json`. Required: `schema_version`, `level_id`.

| Field | Meaning |
|---|---|
| `mechanic_refs` | Ids of mechanics used (unique) |
| `layout` | Array (grid) or object (generator reference or structured layout) |
| `goals` | Array of goal objects |
| `moves_or_time_limit` | Integer, object such as `{"moves": 30}`, or null |
| `obstacles` | Array |
| `difficulty_target` | `{win_rate (ratio), attempts_p50 (at least 1)}` |
| `solver` | `{solvable (boolean or null), min_moves, bot_win_rate, runs}`; extra keys (algorithm, notes) allowed |
| `teach` | `teach`, `test`, `twist`, `reward` |
| `notes` | Design intent in prose |

Mistakes: a move limit tighter than `min_moves` (unwinnable); `solvable: true` with `runs` null (nothing was run); several consecutive `twist` levels.

## 10. Event taxonomy

Path `.gamestudio/analytics/NAME.taxonomy.json`. Required: `schema_version`, `events[]`.

| Field | Constraint |
|---|---|
| `naming` | `snake_case` |
| `common_params[]` | Attached to every event; they count toward the per-event limit |
| `events[].name` | `^(?!firebase_|google_|ga_)[a-z][a-z0-9_]{0,39}$` (reserved prefixes rejected, max 40 chars) |
| `events[].category` | `lifecycle`, `ftue`, `progression`, `economy`, `monetization`, `ads`, `social`, `liveops`, `tech`, `ux` |
| `events[].trigger` | When it fires |
| `events[].params[]` | At most 25; each `{name, type, required, description, enum}`; `type` is `string`, `int`, `float`, `bool` or `timestamp` |
| `events[].kpis`, `sampling` | KPI names fed; sampling ratio |

Mistakes: free-text values in a param without an `enum` (cardinality explosion); a reserved prefix; money as float (use int minor units). See `player-analytics`.

## 11. Mechanic card

Path `*.mechanic.json`. Required: `schema_version`, `id`, `name`. Additional properties allowed.

Fields: `category`, `player_fantasy`, `verbs` (ids or verb objects), `rules`, `parameters`, `dynamics`, `aesthetics` (unique enum: `sensation`, `fantasy`, `narrative`, `challenge`, `fellowship`, `discovery`, `expression`, `submission`), `feedback`, `failure_modes`, `mobile_fit {one_hand, session_fit, notes}`, `references`, `combos`. The same card body is embedded in deconstructions. Procedure for writing one: `references/loops-flows-and-mda.md` section 11. Mistake: aesthetics outside the eight-word enum ("fun", "juicy").

## 12. Deconstruction

Path `.gamestudio/research/NAME.deconstruction.json`. Required: `schema_version`, `game` (with `title`).

| Field | Notes |
|---|---|
| `as_of` | ISO date of the observation; deconstructions date quickly |
| `game` | `{title, developer, year (1950 to 2100), genre, platforms}` |
| `core_loop` | A loop object (not a string) |
| `meta_loops[]` | Loop objects |
| `mechanics[]` | Mechanic-card-like entries |
| `economy` | `{currencies[], sources[], sinks[]}` |
| `progression`, `liveops`, `social` | String, array or object |
| `monetization` | `{model, top_offers[], ads}` |
| `retention_hooks`, `ux_notable`, `art_audio_notable`, `psychology`, `innovations`, `weaknesses`, `lessons`, `borrow_for_us` | String lists |
| `sources` | URLs |

Quality bar: `lessons` are claims about design, `borrow_for_us` are actions, and every non-obvious claim has a `sources` entry. Do not invent figures; omit or hedge.

## 13. Concept card

Path `.gamestudio/concepts/NAME.concept.json`. Required: `schema_version`, `id`, `title`.

Fields: `status` (`draft`, `shortlisted`, `winner`, `parked`, `killed`), `logline`, `analogy`, `genre`, `player_fantasy`, `core_loop` (a one-line string or a loop object), `hook`, `pillars`, `target_audience`, `monetization_model`, `comparables`, `scores {market, novelty, fun_potential, feasibility, monetization, production_cost, agent_buildability, weighted_total}`, `risks` (strings or risk objects), `kill_criteria`, `rationale`.

Score constraints: each of the seven scores is a number 1 to 10 (halves allowed when averaging judges); `weighted_total` is 0 to 10. State the weighting in `rationale` so the total can be recomputed.

## 14. Playtest report

Path `.gamestudio/playtests/NAME.playtest.json`, or evidence `playthrough.json` / `bots.json`. Required: `schema_version`, `mode`, `verdict`.

| Field | Constraint |
|---|---|
| `feature_id` | Optional, `^F\d{3,4}$` |
| `mode` | `deterministic_script`, `bot`, `persona`, `human` |
| `runs` | Integer at least 1 |
| `seed` | Integer or null |
| `steps[]` | `{t (seconds, at least 0), action, expect, observed, ok}` |
| `metrics` | `win_rate`, `avg_session_sec`, `time_to_first_reward_sec`, `softlocks`, `crashes`, `errors` (counts are non-negative integers) |
| `screenshots` | Project-relative paths |
| `findings[]` | Required `severity` (`blocker`, `major`, `minor`, `polish`), `title`; `detail`, `repro` |
| `verdict` | `pass` or `fail` |

Consistency rule worth enforcing: a `pass` verdict with any step `ok: false`, a blocker finding, a softlock or a crash is wrong. Evidence for the `playthrough` gate is a file of this shape.

## 15. Perf report

Path `.gamestudio/reports/NAME.perf.json`, or evidence `perf.json`. Required: `schema_version`, `verdict`.

Fields: `feature_id`, `build`, `device {name, tier (low|mid|high), os}`, `scenario`, `duration_sec`, `fps {avg, p1_low}`, `frame_ms {p50, p95, p99}`, `memory_mb {peak, avg}`, `draw_calls`, `cpu_ms`, `gpu_ms`, `thermal {start, end}`, `download_mb`, `cold_start_sec`, `budgets {...}` (copy of the contract's `technical.perf_budgets` used), `violations[]`, `verdict`, `notes`. Numbers are non-negative; several may be null when not measured.

Consistency rule: if any measured value exceeds its budget, `violations` is non-empty and `verdict` is `fail`. Report the device tier, because a pass on a high-tier device says little about the low tier. See `mobile-performance`.

## 16. Common validation errors and fixes

| Error text (shape) | Likely cause | Fix |
|---|---|---|
| `/schema_version: ... is not "1.0"` | Missing or misspelt version | Add `"schema_version": "1.0"` |
| `... is not one of [...]` | Enum typo or invented value | Use the listed enum value |
| `... is greater than the maximum 1` | Percentage given instead of ratio | Divide by 100 |
| `/features/3/gates/...: additional property` | Unknown gate key | Use only the five gate names |
| `... does not match pattern` | Id, event name or path rule | Check the pattern in sections above |
| `required property missing` | Missing `id`, `title`, `mode`, `verdict` and so on | Add the field |
| `error: file not found` (exit 2) | Wrong path, or `--schema` given a name instead of a path | Use `--auto` or a full schema path (or `gs.py validate --schema NAME`) |
| File not recognised by `--auto` | File name matches no rule | Rename to the pattern, or add `"$schema_name"` |
