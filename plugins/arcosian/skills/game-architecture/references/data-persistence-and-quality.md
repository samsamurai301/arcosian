# Data, persistence and code quality

How to store, version, sync and configure game data without corrupting players' progress, and how to keep a mobile codebase testable and fast: versioned saves with migration chains, cloud save conflict policy, remote config layering, localisation tables, module boundaries, a testing strategy that matches the sim-core split, allocation-aware coding, and a review checklist. It assumes the `sim-core + presentation` structure from `references/sim-core-presentation.md` and reuses the save approach of `templates/godot-starter` (`core/save_data.gd`, `services/save_service.gd`).

## Contents

1. Save data principles
2. Save format and atomic writes
3. Versioning and migrations
4. Save corruption, backup and recovery
5. Cloud saves and conflict resolution
6. Remote config layering
7. Localisation tables
8. Module boundaries and project layout
9. Testing strategy
10. Allocation-aware code
11. Logging, errors and crash hygiene
12. Review checklist

## 1. Save data principles

1. A save is a contract with the player's time. Treat losing it as a severity-1 defect.
2. Persist the minimum that rebuilds state: `to_dict()` of the core, profile, settings, purchases receipt state, timestamps. Never persist derived values or node paths.
3. Separate files or top-level keys by lifetime and sync policy:

| Bucket | Content | Sync | Reset on logout |
|---|---|---|---|
| `profile` | Progress, currencies, unlocks, stats | Cloud | No |
| `run` | In-progress session (board, level state) | Local, maybe cloud | Optional |
| `settings` | Audio, language, accessibility | Local (cloud optional) | No |
| `cache` | Remote config copy, last-seen server time | Local only | Yes |
| `entitlements` | Purchase state snapshot | Server is source of truth | Re-verify |

4. Everything has a `version` integer at the root (the template uses `version` and `default_save()`).
5. Never trust a save: validate types, clamp ranges, ignore unknown keys. Players edit local files; do not treat the save as authoritative for anything with real money or competitive value (see `multiplayer-backend`).
6. Do not store int64 values in JSON numbers if they may exceed 2^53 (RNG state, big IDs); store as strings. Big idle numbers: store mantissa/exponent, not floats beyond range.

## 2. Save format and atomic writes

| Format | Use | Notes |
|---|---|---|
| JSON | Default for mobile games | Human-debuggable, easy to migrate, diff-friendly; slightly large |
| Binary (MessagePack, protobuf, custom) | Large state, many saves, tight cloud quotas | Needs tooling and explicit schema discipline |
| Engine resource formats (`.tres`, ScriptableObject serialisation) | Avoid for saves | Tied to class layout and can execute or break across versions; prefer plain data |
| SQLite | Large relational data (collections, logs) | Good for thousands of records; adds dependency |

Atomic write recipe (as in the template's `save_service.gd`): write to `save.json.tmp`, flush and close, rotate current to `.bak`, rename tmp to current. On load try current, then `.bak`, then defaults. Never write directly over the only copy.

```gdscript
func save() -> bool:
	var tmp: String = path + ".tmp"
	var f: FileAccess = FileAccess.open(tmp, FileAccess.WRITE)
	if f == null: return false
	f.store_string(JSON.stringify(data))
	f.close()
	if FileAccess.file_exists(path):
		DirAccess.rename_absolute(path, path + ".bak")
	return DirAccess.rename_absolute(tmp, path) == OK
```

```csharp
public static void WriteAtomic(string path, string json) {
    var tmp = path + ".tmp";
    File.WriteAllText(tmp, json);
    if (File.Exists(path)) File.Copy(path, path + ".bak", true);
    File.Move(tmp, path, true);   // .NET Standard 2.1 / Unity 6 supports overwrite overload
}
```

When to save: on app pause/background (the only reliable hook on mobile), on milestones (level complete, purchase, reward claim), and on a debounce timer after changes (a few seconds), never every frame. Use a dirty flag and flush only when changed. Large saves: serialise off the main thread if the profiler shows hitches.

Encryption and obfuscation: obfuscation deters casual editing only. If the economy is client-authoritative the player can still cheat; the fix is server authority for what matters, not a better cipher. Never ship secrets in the save.

## 3. Versioning and migrations

Rules:

- Every shipped save version is permanent. Keep a migration for every historical version; players update after long gaps.
- Migrations are pure functions `vN -> vN+1`, chained (the template's `migrate` loops until `CURRENT`). Never skip-write a multi-version jump by hand.
- Unknown future versions (save from a newer app after a downgrade): refuse to load and keep the file untouched; do not downgrade-overwrite.
- Add fields with defaults; rename by migration; delete by ignoring first, removing later.
- Each migration has a test fixture: a real or captured save of that version (store fixtures in `tests/fixtures/saves/`).

```gdscript
static func migrate(data: Dictionary) -> Dictionary:
	var v: int = int(data.get("version", 1))
	if v < 1 or v > CURRENT:
		return {}                               # caller keeps file, falls back
	var d: Dictionary = data.duplicate(true)
	while v < CURRENT:
		match v:
			1: d = _v1_to_v2(d)
			2: d = _v2_to_v3(d)
			_: return {}
		v = int(d.get("version", v + 1))
	return d
```

Checklist per release that touches data shape: bump `CURRENT`; write migration; add fixture and test (old fixture migrates to valid current; migrating twice is a no-op; result passes validation); verify round trip of the newest version; verify an empty and a corrupt file produce defaults without crashing.

Content ids and renames: if a level, item or currency id is renamed, add an alias map applied during migration rather than editing historical saves. Removing content: migrate owned items to a compensation (currency or equivalent) and record it.

## 4. Save corruption, backup and recovery

Causes: process killed mid-write, disk full, storage permission glitches, bad migration, serialisation bug, cloud merge bug.

Defences, in order of value:
1. Atomic write plus `.bak`.
2. Validate after load (schema, ranges); if invalid, try `.bak`, then cloud copy, then defaults.
3. Keep a rolling set of N dated local snapshots for support (small, e.g. last 3 daily) if saves are tiny.
4. Never auto-overwrite a save that failed to load: rename it to `save.corrupt.<n>` so support can inspect it.
5. Telemetry event on any recovery path (`save_recovered{source}`) so you can see rates; spike after a release means a migration bug.
6. A hidden support screen: export save as text, import save, reset profile with confirmation.

Do not claim "cloud backed up" in UI unless the sync is confirmed; show last sync time.

## 5. Cloud saves and conflict resolution

Options: platform cloud (iCloud key-value or document sync; Google Play Games Services saved games), a backend (Firebase, Nakama, PlayFab, Supabase; see `multiplayer-backend`), or none for offline games. Platform sync is free and good enough for single-player; a backend is needed for cross-platform, anti-cheat or social.

Conflict policy must be explicit. A save carries a `meta` block: `{device_id, updated_at, play_time, version, progress_score, revision}`.

| Strategy | When | Risk |
|---|---|---|
| Last-write-wins | Settings; tiny low-value state | Overwrites progress after clock skew |
| Highest progress wins | Linear progression games (level, playtime) | Loses side changes (purchases made on the other device) |
| Field-wise merge | Currencies as ledgers, unlocks as sets | More code; needs commutative data design |
| Ask the player | Rare, genuinely divergent saves | Friction; show a clear comparison (level, playtime, last played) |

Design for merge: represent unlocks as sets (union), currencies as earned and spent totals (derive balance), purchases as receipts (verified server side), and counters as monotonic maxima. Then most conflicts merge automatically. Use a monotonic `revision` or server time rather than device clocks, which are wrong or tampered.

Procedure on launch: load local; fetch cloud metadata; if only one exists use it; if both, compare `revision` lineage (if cloud revision equals the local base it is a fast-forward); on divergence apply the merge or prompt. Upload after milestones and on pause, with retry and backoff; never block gameplay on network. Account linking (anonymous to Apple/Google sign-in) must preserve the save and handle "this account already has a save" using the same policy.

Privacy: cloud saves are personal data; follow account deletion rules (both stores require in-app account deletion paths where accounts exist; see `legal-ethics` and `store-release`).

## 6. Remote config layering

Remote config lets live ops change numbers without a release. Use it safely.

Layer order (later wins), each layer small and typed:

```
1. Code defaults          (compiled in; game works with no network)
2. Bundled data           (tuning.json shipped in the build)
3. Cached remote config   (last successfully fetched, validated)
4. Fresh remote config    (fetched this session, applied at a safe point)
5. Segment / experiment overrides (server decides per player; carries experiment id)
6. Debug overrides        (dev builds only)
```

Rules:
- Keys are namespaced (`economy.shop.starter_price_tier`), typed, and validated against a schema with min/max. An out-of-range value is rejected and logged, falling back one layer.
- Apply at safe points (session start, between levels), not mid-run; record the applied config version in the run so replays and analytics know which numbers were in effect.
- Never put code or unbounded expressions in remote config. Feature flags are booleans or small enums.
- Kill switches: every risky feature (new ad format, event, offer) has a flag that disables it without a build, and the default when config is missing is the safe state.
- Experiments: assignment must be sticky per player and logged on every relevant event; keep the experiment id in the save so reinstalls do not reshuffle (or accept that they do and say so).
- Fetch throttling: platform SDKs impose minimum fetch intervals; design for stale values and show no UI that depends on a fresh fetch.
- Test matrix: no network, cached only, fresh, corrupt payload, partial payload.
- Authority: remote config values that affect balances must also be validated server side if the server pays out.

## 7. Localisation tables

Principles: no user-visible string in code; keys are stable semantic ids (`ui.shop.buy`), not English sentences; one table per locale; English (or your source locale) is the fallback chain end.

| Concern | Practice |
|---|---|
| Format | CSV or JSON, or engine-native (Godot translation CSV/PO, Unity Localization package) |
| Plurals | Use ICU-style plural categories; languages have more than singular and plural; never concatenate "{n} " + "coins" |
| Variables | Named placeholders (`{name}`, `{count}`), never positional-only; translators may reorder |
| Numbers and dates | Locale-aware formatting for digits, separators, currency, dates |
| Text expansion | Plan for large growth in some languages; design buttons and labels to flex; test with a pseudo-locale that pads and adds accents |
| Scripts | CJK, Arabic and Hebrew (right-to-left), Thai, Devanagari need fonts, shaping and layout mirroring; choose fonts early and subset to control size |
| Context | Give translators a context column and screenshots; same English word may need different translations |
| Art text | Avoid text baked into textures |
| Pipeline | Extract keys in CI; fail the build on missing keys in the source locale; report missing keys for others; ship fallbacks, not blanks |

Content strings (item names, quest text) live with content data and reference keys; do not duplicate English in data files. Details of accessibility and locale launch strategy live in `accessibility-localization`.

## 8. Module boundaries and project layout

Prefer few, clear modules over many packages:

```
core/            rules, state, rng, tuning, save schema        no engine
content/         data files and schemas                        data only
presentation/    scenes, views, input, ui
services/        platform wrappers behind interfaces
tools/           headless runners, editor tooling, CI scripts
tests/           unit, playthroughs, fixtures
```

Rules: dependency direction is one way (see sim-core file); features are vertical slices where practical (a feature's core logic, content, view and tests are discoverable together); shared utilities live in one small `common/` with no game knowledge; third-party SDKs are wrapped by a service so you can remove or replace them; Unity asmdefs mirror these boundaries and also cut compile times; enforce with grep or asmdef references in CI.

Code standards worth fixing early: static typing everywhere (typed GDScript; nullable-aware C#); naming conventions per engine; one class per file; signals/events named in past tense; no logic in `_ready`/`Awake` beyond wiring; no `Find` or `get_node` by string paths in hot code (cache references or use exported fields).

## 9. Testing strategy

Pyramid for a mobile game with a sim core:

| Layer | Scope | Count | Speed | Tooling |
|---|---|---|---|---|
| Unit | Pure rules, migrations, RNG, tuning loaders | many | ms | built-in runner (`run_tests.gd`), GdUnit4, Unity EditMode |
| Property / invariant | Random actions via seeded RNG: no crashes, invariants hold, round trip equals | some | seconds | same, loops of seeded runs |
| Scripted playthrough | Deterministic action scripts with `expect` state paths | a few per feature | ms | `runner.gd --mode=script`, `PlaytestRunner.Run` |
| Bot sweeps | Thousands of runs, win rates, softlocks | per balance pass | seconds to minutes | `--mode=bot` |
| Integration | Services with mocks, scene load, save/load through disk | some | seconds | headless engine |
| Visual | Screenshots reviewed by a human or critic | per release | manual | screenshot capture tool |
| Device | Perf, thermals, interruptions, store builds | per milestone | slow | real devices; see `mobile-performance` and `qa-testing` |

Rules: test behaviour through `apply`, not private helpers; every bug fix gets a failing test first (a seed and action list from the replay file makes a perfect regression test); keep tests deterministic (seed everything; no sleeps; no wall clock); flaky tests are deleted or fixed the same day; tests run in CI on every change (static, unit, playthrough are fast gates); record a `rules_version` so golden-file tests update deliberately.

Golden tests: store the final state hash for a few canonical seeds. A change in the hash means gameplay changed; review it intentionally rather than rubber-stamping.

Mocking: services provide null implementations; clock and network are injected in services (core has none); time-based features test with a fake clock passed as an action argument.

What not to test: engine behaviour, pixel positions of tweens, third-party SDK internals.

## 10. Allocation-aware code

Mobile frame budget: about 16.6 ms at 60 fps and 33.3 ms at 30 fps, shared with rendering. Garbage creates spikes (C# GC collections; GDScript allocations from Arrays, Dictionaries and strings in hot loops add CPU cost too).

Hot path rules (anything per frame, per entity or per touch event):

| Avoid | Prefer |
|---|---|
| String concatenation, `ToString()`, `str()` per frame | Cache strings; update labels only when values change |
| New collections in `Update`/`_process` | Reuse a member list and `Clear()` or `clear()` |
| LINQ and closures/lambdas in C# hot code | Plain loops; static lambdas or cached delegates |
| `foreach` over non-array collections in older runtimes where it allocates | `for` loops over lists/arrays; check with the profiler |
| Boxing value types (passing structs as `object`, enums in dictionaries) | Generic collections, typed arrays, ints as keys |
| `GetComponent`, `FindObjectOfType`, `get_node` per frame | Cache in `Awake`/`_ready` |
| Instantiate/destroy per spawn | Pools (see patterns file) |
| Dictionary events per frame in GDScript | Aggregate events per action; tick-based sims emit only meaningful events |
| `Array` of Variants for numeric data | `PackedFloat32Array`, `PackedInt32Array`, typed arrays |
| `Camera.main` property in old Unity versions | Cached camera reference |

Procedure: profile on the lowest target device first (see `mobile-performance`); find allocations per frame with the engine profiler (Unity Profiler GC Alloc column, Godot monitors and profiler); fix the top three; re-measure. Do not micro-optimise cold code. Prefer algorithmic fixes (grid instead of N^2) over constant-factor tricks. Incremental GC settings and scene unloading strategy belong to the engine skills (`engine-unity`, `engine-godot`).

Memory budgets also matter: texture memory and audio streams dominate; see `technical-art`.

## 11. Logging, errors and crash hygiene

- One logging wrapper with levels; strip or gate verbose logs in release builds (log spam costs frame time).
- Errors in core return `rejected` events or error results; presentation shows a friendly fallback; never swallow errors silently.
- Crash reporting (Crashlytics or equivalent) with breadcrumbs: last N events and the current screen; attach `rules_version`, build number, seed; avoid personal data.
- Assertions in debug builds for invariants (state sums, bounds); remove or downgrade in release as appropriate.
- ANR and watchdog: no synchronous disk or network on the main thread at startup; defer heavy loads behind a loading screen with progress.

## 12. Review checklist

Architecture
- [ ] Core has no engine access; boundaries enforced by grep or asmdef.
- [ ] Every mutation goes through `apply`; events sufficient for the view.

Persistence
- [ ] Root `version`; migration chain complete with fixtures; future-version saves refuse safely.
- [ ] Atomic write plus backup; corrupt files preserved, not overwritten.
- [ ] Saves flushed on pause and milestones, debounced otherwise.
- [ ] Cloud conflict policy documented; merge-friendly data shapes; no reliance on device clock.

Config and content
- [ ] All tunables in validated data; ids not indices; defaults safe.
- [ ] Remote config schema-validated, applied at safe points, kill switch for each risky feature.
- [ ] No user-visible hard-coded strings; plurals and placeholders handled.

Quality
- [ ] Unit tests for rules and migrations; at least one playthrough and a bot run in CI.
- [ ] Seeds, replays and golden hashes available for regressions.
- [ ] No per-frame allocations in profiled hot paths on the lowest device tier.
- [ ] Services behind interfaces with null implementations; no SDK calls in core.
- [ ] Crash reports carry build, rules version and breadcrumbs; no secrets or personal data in logs.
