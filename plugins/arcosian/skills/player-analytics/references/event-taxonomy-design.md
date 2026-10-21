# Event Taxonomy Design

How to design the analytics contract for a mobile game: which events to send, how to name them, which parameters and user properties to attach, how to version the taxonomy without breaking dashboards, how to keep it free of personal data, and how it maps onto Firebase/GA4 and GameAnalytics. The taxonomy is a file, `.gamestudio/analytics/<game>.taxonomy.json`, validated by `event-taxonomy.schema.json`; `event_taxonomy.py` drafts it from the design contract and generates engine stubs from it. Treat it as code: reviewed, versioned, tested in playthroughs. The guiding rule: **every event exists to answer a named question or feed a named KPI** — if nobody can say which dashboard tile or decision it feeds, it does not ship.

## Contents

1. Principles
2. Naming conventions
3. The event envelope: common parameters
4. Core event catalogue for mobile games
5. Parameter design rules
6. User properties
7. Economy events: sources and sinks
8. Monetization and ad events
9. Versioning and change management
10. Privacy: no PII, consent, children
11. Client architecture: the analytics wrapper
12. Mapping to Firebase/GA4 and GameAnalytics
13. Using `event-taxonomy.schema.json` and `event_taxonomy.py`
14. Event QA checklist
15. Worked example: from contract to taxonomy
16. Volatile facts (as of Oct 2026 — verify before relying)

---

## 1. Principles

1. **Questions before events.** Start from the questions in the contract and kill criteria: "Where do new players drop in the FTUE?", "Which levels cause churn?", "Is soft currency inflating?", "Which rewarded placement earns most without hurting D7?". Each question → the minimum events and parameters that answer it.
2. **State changes, not clicks.** Log meaningful transitions (level started, ended, currency changed hands, offer shown, purchase validated). Button-tap logging creates volume without insight; log taps only on decision points you are actively studying (e.g. the store tab, an offer popup's close button).
3. **One event per concept, parameters for variants.** `level_end` with `success` and `reason` beats `level_win`, `level_lose_moves`, `level_lose_quit`. Fewer event names keep you inside per-app event-name limits and make funnels simple.
4. **Low cardinality.** Parameters are ids and closed enums, not free text. Unique values per parameter should stay in the hundreds or low thousands (level ids are fine; player names, timestamps-as-strings and error messages with numbers inside are not).
5. **Authority matters.** Economy and purchase events that drive money or balance decisions should be emitted by (or reconciled against) the server when one exists. Client events are for behaviour; server records are for truth.
6. **Same event, same meaning, forever.** Never repurpose an event name or change a parameter's unit. Add a new name and deprecate the old (section 9).
7. **Instrument with the feature, not after.** Analytics is part of a feature's acceptance criteria (`features.json` → `acceptance`), and its events are asserted in the deterministic playthrough (`playthrough` gate).
8. **Privacy by default.** No personal data in events, ever; consent gates collection (section 10).

---

## 2. Naming conventions

| Rule | Do | Don't |
|---|---|---|
| Case | `snake_case` (schema `naming` = `snake_case`) | `LevelStart`, `level-start`, `Level Start` |
| Order | `object_action`: `level_start`, `offer_shown`, `rv_completed` | `start_level`, mixing orders |
| Tense | Present or past participle consistently: `_start`, `_end`, `_shown`, `_completed` | `level_started` next to `level_start` |
| Length | ≤ 40 characters, starts with a letter | Long sentence-like names |
| Reserved prefixes | Avoid `firebase_`, `google_`, `ga_` (schema pattern rejects them) | `ga_level` |
| Reserved names | Avoid platform-reserved names such as `error`, `app_background`, `first_open`, `session_start`, `in_app_purchase` for custom events (see volatile section) | Logging your own `error` event (rejected by Firebase) — use `client_error` |
| Standard names | Prefer GA4 recommended game events where they fit: `level_start`, `level_end`, `level_up`, `tutorial_begin`, `tutorial_complete`, `earn_virtual_currency`, `spend_virtual_currency`, `post_score`, `unlock_achievement`, `ad_impression` | Inventing `currency_gain` when `earn_virtual_currency` exists |
| Parameter names | Same name everywhere for the same concept: `level_id`, `placement`, `product_id`, `source`, `item_name` | `levelId` in one event and `lvl` in another |
| Units in names | `duration_sec`, `price_usd_micros`, `load_ms`, `distance_m` | `duration` (seconds? ms?) |
| Booleans | `success`, `first_purchase`, `is_tutorial` | `"yes"`/`"no"` strings |
| Ids vs names | Stable ids (`w1_l012`, `starter_pack`) not display text ("Level 12", "Starter Pack!") | Localised strings as values |

**Prefix families** (readable, sort together in tools): `tutorial_*`, `level_*`, `offer_*`, `iap_*`, `rv_*`, `inter_*`, `liveops_event_*`, `social_*`, `push_*`, `perf_*`.

---

## 3. The event envelope: common parameters

`common_params` are attached by the analytics wrapper to every event. In Firebase they count toward the 25-parameter limit, so keep the envelope small (5–8) and put slow-changing attributes in user properties (section 6).

| Param | Type | Required | Purpose |
|---|---|---|---|
| `session_id` | string | yes | Joins events into sessions; random per session (regenerate after the SDK's inactivity timeout) |
| `build` | string | yes | `version-build`, e.g. `0.3.0-42`; every release comparison depends on it |
| `player_level` | int | yes | Highest level reached (or account level); the universal progression axis |
| `ab_cohort` | string | no | Active experiment variants, comma-separated, e.g. `spawn_cost_b,shop_v2_a` (keep under the value-length limit; see section 9 for exposure events) |
| `event_seq` | int | recommended | Per-install monotonically increasing counter; detects loss, duplicates and ordering problems |
| `client_ts` | timestamp | optional | Epoch ms on device; most SDKs stamp time already — add only if your pipeline needs it |
| `taxonomy_version` | string | recommended | Version of this taxonomy file in the build (section 9) |
| `debug_build` | bool | recommended | True for internal/QA builds so they can be excluded |

Do **not** add as common params: country, OS, device model, app version, install source — analytics SDKs collect device and geo context automatically, and attribution comes from the MMP.

---

## 4. Core event catalogue for mobile games

The catalogue below is the studio default. `event_taxonomy.py generate` drafts most of it from the contract; prune what the game does not have. Categories are the schema enum: `lifecycle`, `ftue`, `progression`, `economy`, `monetization`, `ads`, `social`, `liveops`, `tech`, `ux`.

### 4.1 Lifecycle

| Event | Trigger | Key params | Feeds |
|---|---|---|---|
| `first_open`, `session_start`, `user_engagement` | Automatic in Firebase/GA4 — do not re-log | — | DAU, retention, session length |
| `app_paused` | App goes to background mid-session | `screen`, `in_level` (bool) | Interruption analysis |
| `session_end_summary` | Best-effort on background after inactivity, or sent at next launch for the previous session | `duration_sec`, `levels_played`, `last_screen`, `end_context` (enum: `level_fail`, `out_of_lives`, `offer_declined`, `ad_shown`, `loading`, `menu_idle`, `goal_complete`) | Session-end reasons (`references/telemetry-for-design.md` §4) |
| `notification_permission_result` | Player answers the OS push prompt | `granted` (bool), `prompt_context` | Push reach, D1 |
| `att_prompt_result` (iOS) | Player answers the App Tracking Transparency prompt | `authorized` (bool) | Attribution coverage |

### 4.2 FTUE

| Event | Trigger | Key params | Feeds |
|---|---|---|---|
| `tutorial_begin` | First frame of the first guided step on a fresh install | — | `ftue_funnel` |
| `tutorial_step` | Each FTUE beat completed (ids from `contract.ftue.steps[].id`) | `step_id` (enum), `step_index` (int), `seconds_since_install` (float) | `ftue_funnel`, `aha_seconds` |
| `tutorial_complete` | Final FTUE beat complete | `seconds_since_install` | `ftue_funnel`, `d1` |
| `tutorial_skip` | Player skips (if allowed) | `step_id` | FTUE design |

Name steps by what they teach (`ftue_merge`, `ftue_booster`), not by number, so reordering steps does not corrupt history; carry the order in `step_index`.

### 4.3 Progression

| Event | Trigger | Key params | Feeds |
|---|---|---|---|
| `level_start` | Level begins (after the pre-level screen, not when the map is opened) | `level_id`, `attempt` (int, per level, from 1), `boosters_preselected` (int), `dda_step` (int, if DDA exists) | `level_funnel` |
| `level_end` | Results screen shown or the player quits the level | `level_id`, `attempt`, `success` (bool), `reason` (enum: `win`, `moves_out`, `time_out`, `hearts_out`, `quit`), `duration_sec`, `moves_left` or `targets_left` (int), `stars` (int), `boosters_used` (int), `continues_used` (int), `revived` (bool) | `level_win_rate`, `attempts_p50`, `churn_by_level` |
| `level_up` | Player/account level increases | `level` (int), `source` | Progression velocity |
| `milestone_reached` | Meta milestone (area restored, chapter finished, world unlocked) | `milestone_id`, `days_since_install` | `d7`, meta engagement |
| `unlock_achievement` | Achievement unlocked | `achievement_id` | Goal design |

**`level_end` vs `level_complete` / `level_fail`.** One `level_end` with `success` matches GA4's recommended event and makes win rate a single query; separate events map one-to-one onto GameAnalytics' progression statuses (Complete/Fail). The studio default is `level_end` and the wrapper translates to GameAnalytics progression events when both SDKs are used. Always log quits as `level_end` with `reason = "quit"` — otherwise rage-quits vanish from difficulty data.

**Near-miss parameters.** `moves_left` on wins and `targets_left` on fails are the two most useful difficulty parameters: they show how close the outcome was, which distinguishes "fair but tense" from "unwinnable" (`references/telemetry-for-design.md` §2).

### 4.4 Economy

| Event | Trigger | Key params | Feeds |
|---|---|---|---|
| `earn_virtual_currency` | Any grant of any currency | `virtual_currency_name` (enum), `value` (int), `source` (economy-model node id), `balance_after` (int) | `economy_balance` |
| `spend_virtual_currency` | Any spend | `virtual_currency_name`, `value`, `item_name` (sink id), `balance_after` | `economy_balance` |
| `item_acquired` | Non-currency inventory gain (boosters, cards, cosmetics) | `item_id`, `quantity`, `source` | Inventory health |
| `item_used` | Booster or consumable used | `item_id`, `context` (e.g. `level_id`) | Booster economy, difficulty |

Details in section 7.

### 4.5 Monetization and ads

| Event | Trigger | Key params | Feeds |
|---|---|---|---|
| `store_opened` | Shop screen shown | `entry_point` (enum) | Store funnel |
| `offer_shown` | An IAP offer is visible to the player | `offer_id`, `product_id`, `placement`, `trigger` (enum) | Offer funnel, ethics review |
| `iap_purchase_started` | Player taps buy (store sheet requested) | `product_id`, `offer_id` | Purchase funnel |
| `iap_purchase_completed` | Receipt validated (server-side where possible) and contents granted | `product_id`, `price_usd_micros` (int), `first_purchase` (bool), `offer_id`, `transaction_id_hash` (string, for dedup; not the raw receipt) | `payer_conversion`, `arpdau_usd` |
| `iap_purchase_failed` | Store returns an error or the player cancels | `product_id`, `reason` (enum: `cancelled`, `payment_declined`, `pending`, `network`, `validation_failed`) | Payment UX |
| `rv_offer_shown` | Rewarded-ad offer visible | `placement` (enum) | `rv_opt_in_rate` |
| `rv_started` | Player accepts and the ad begins | `placement` | Offer-to-watch rate |
| `rv_completed` | Ad SDK confirms the reward | `placement`, `network` | `rv_opt_in_rate`, ad ARPDAU |
| `inter_shown` | Interstitial displayed | `placement`, `seconds_since_last_inter` | Frequency-cap compliance |
| `ad_impression` | Impression-level revenue callback from mediation | `ad_platform`, `ad_source`, `ad_format`, `ad_unit_name`, `currency`, `value` | Ad revenue (ILRD) |

Details in section 8.

### 4.6 Social, live-ops, tech, UX

| Event | Category | Trigger | Key params |
|---|---|---|---|
| `social_invite_sent` | social | Invite or share link created | `channel` (enum), `context` |
| `social_invite_accepted` | social | Invited player opens via link (from attribution/deep link) | `channel` |
| `join_group` | social | Joins a team/guild | `group_size_bucket` (enum, not the group id if ids are user-named) |
| `liveops_event_join` | liveops | Player opts into or first participates in an event | `event_id`, `segment` |
| `liveops_event_progress` | liveops | Milestone reached | `event_id`, `milestone` |
| `liveops_event_reward` | liveops | Event reward claimed | `event_id`, `reward_id` |
| `push_opened` | liveops | App opened from a push | `campaign_id` |
| `client_error` | tech | Handled error worth counting | `error_code` (enum or short code), `severity` (enum), `context` |
| `load_time` | tech | Major load finished | `stage` (enum: `boot`, `first_playable`, `level`, `store`), `load_ms` (int) |
| `perf_sample` | tech | Every 60 s in gameplay, sampled (e.g. 5%) | `fps_avg`, `frame_ms_p95`, `memory_mb`, `thermal` |
| `settings_changed` | ux | Setting toggled | `setting` (enum), `value` |
| `screen_view` | ux | Major screen shown (automatic on some SDKs; manual in engines) | `screen_name` (enum) |

Crashes are captured by the crash reporter (Crashlytics or equivalent), not by analytics events.

---

## 5. Parameter design rules

| Rule | Detail |
|---|---|
| Types | Use the schema types: `string` (ids, enums), `int` (counts, money in minor units or micros), `float` (durations, ratios), `bool`, `timestamp` (epoch ms) |
| Money | Integers in micros (`price_usd_micros` = 4,990,000 for $4.99) or cents; never floats (rounding) and never localised price strings. Send the store's local price and currency only if you need regional analyses, and store the USD reference price from your price table |
| Enums | Declare `enum` lists in the taxonomy; the generated stubs assert them in debug builds |
| Cardinality budget | Rough guide: under ~1,000 distinct values per parameter. Level ids (hundreds) are fine; free text, user ids, raw timestamps or full error messages are not |
| Required vs optional | Required params are asserted by stubs; optional params must have a documented "absent means" rule |
| Nulls | Omit an absent optional parameter instead of sending `"null"` or `-1` |
| Durations | Exclude paused time; state it in the description |
| Counters | Per-level `attempt` resets per level; `event_seq` never resets; `session_index` counts sessions since install |
| Lists | Analytics parameters are scalars; encode short lists as comma-separated ids only when they are bounded (e.g. boosters used), otherwise emit one event per item |
| Value length | Keep string values under the platform limit (100 characters in GA4) |

**Parameter budget per event.** Event params + common params ≤ 25 in GA4. A practical budget: 6 common + up to 10 event-specific, leaving headroom for later additions.

---

## 6. User properties

User properties describe the player, not the moment. They are set when they change and attached by the SDK to subsequent events, so they segment every report without bloating events. GA4 allows 25 per property (names ≤ 24 characters, values ≤ 36 characters).

| Property | Values | Set when | Use |
|---|---|---|---|
| `payer_tier` | `non_payer`, `payer_low`, `payer_mid`, `payer_high` (thresholds from your own spend distribution, section 5 of the segmentation reference) | After each purchase | Monetization and live-ops segmentation |
| `first_purchase_day` | days since install at first purchase, bucketed (`d0`, `d1_3`, `d4_7`, `d8_30`, `d30p`) | First purchase | Conversion timing |
| `install_week` | ISO week string, e.g. `2026_w42` | First open | Cohort filters in tools without native cohorts |
| `acq_channel` | `organic`, `paid`, `crosspromo`, `referral` (coarse; detailed attribution stays in the MMP) | When attribution resolves | Channel quality comparisons |
| `device_tier` | `low`, `mid`, `high` (from a device-class table, see `mobile-performance`) | First open | Perf and churn by tier |
| `progress_bucket` | e.g. `l001_020`, `l021_050` | On bucket change | Coarse progression segmentation |
| `push_enabled` | `true`/`false` | Permission change | CRM reach |
| `ab_groups` | Short variant codes (if the experiment tool does not set its own property) | On assignment | Experiment analysis |
| `consent_state` | `analytics_only`, `ads_personalised`, `none` | On consent change | Excluding or weighting by consent |
| `social_status` | `solo`, `has_friends`, `in_group` | On change | Social retention analyses |

Never put PII in user properties (no names, emails, handles, phone numbers, exact birthdays or precise location).

---

## 7. Economy events: sources and sinks

Economy telemetry exists to check the live economy against the economy model (`economy-model.schema.json`). The link is the **node id**:

- `earn_virtual_currency.source` = the id of the `source` (or `converter` output) node that granted it, e.g. `win_reward`, `daily_chest`, `rv_double`, `iap_gems_m`.
- `spend_virtual_currency.item_name` = the id of the `sink` (or `converter` input) node, e.g. `booster_hammer`, `continue_gems`, `meta_build_area3`.
- `virtual_currency_name` = the resource id from `economy-model.resources[].id` and `contract.economy.currencies[].id`.

Rules:

1. **Log every flow**, including grants from IAP, ads, events, compensation, admin tools and refunds (`source = "refund_reversal"`). Missing faucets make sink/source ratios meaningless.
2. **Include `balance_after`** so balance distributions and hoarding can be computed without replaying history.
3. **Aggregate micro-flows.** For currencies that change many times per level (e.g. coins per tile), emit one `earn_virtual_currency` per level end with the total, and a `source` naming the aggregate (`level_coins`).
4. **Server reconciliation.** If an economy server exists, compare daily totals per node from events vs the server ledger; a gap above about 1–2% is a logging bug or an exploit.
5. **Hard currency from purchases**: emit the grant with `source = "iap_<product_id>"` in addition to `iap_purchase_completed`, so the economy view and the revenue view agree.

Analysis of these events — sink/source ratios, hoarding, broke rates, inflation — is in `references/telemetry-for-design.md` §3.

---

## 8. Monetization and ad events

**Purchase truth comes from validated receipts.** Fire `iap_purchase_completed` only after server-side validation (App Store Server API / Play Developer API, or a receipt-validation service such as RevenueCat) and content grant. Firebase also auto-collects store purchases on mobile (`in_app_purchase`), which is useful as a cross-check but does not know your offer ids, first-purchase flag or validation status.

**The offer funnel.** `offer_shown → iap_purchase_started → iap_purchase_completed | iap_purchase_failed`. Track `trigger` on `offer_shown` (e.g. `level_fail`, `store_visit`, `starter_timer`, `event_start`) so the ethics review can see whether offers are timed to frustration (`monetization`, `legal-ethics`).

**Rewarded ads funnel.** `rv_offer_shown → rv_started → rv_completed`. The design question is reward value per placement: `rv_started / rv_offer_shown` per placement shows which rewards players value; D7 retention of rewarded-ad users vs non-users must be read with selection bias in mind (engaged players watch more ads).

**Impression-level revenue.** Mediation SDKs (AppLovin MAX, Unity LevelPlay, AdMob) expose per-impression revenue callbacks. Forward them as `ad_impression` with `value` and `currency`; this is the ad side of ARPDAU and of cohort LTV. Reconcile to network payouts monthly.

**Interstitial compliance.** Log `seconds_since_last_inter` and session time at show; a dashboard check that no interstitial fires before `contract.monetization.ads.interstitial.first_after_sec` or more often than `min_interval_sec` catches config mistakes.

---

## 9. Versioning and change management

| Practice | How |
|---|---|
| Version the file | Keep a top-level `taxonomy_version` (semantic: `MAJOR.MINOR.PATCH`) and a `changelog` array in the taxonomy JSON (the schema allows extra top-level keys); send `taxonomy_version` as a common param |
| Additive by default | New events and new optional params = MINOR. Fixes to descriptions = PATCH |
| Breaking changes | Renaming an event, changing a param type/unit, or changing a trigger = MAJOR; implement as **new name + deprecation** of the old: emit both for at least one release, migrate dashboards, then stop the old |
| Never reuse names | A deprecated name stays reserved forever |
| Trigger changes are breaking | Moving `level_start` from "map tap" to "level actually begins" changes every funnel; treat as a new event (`level_start_v2`) or annotate the release on every dashboard |
| Experiment exposure | Log `experiment_exposure` {`experiment_id`, `variant`} once per experiment at the moment of first exposure — `ab_cohort` alone says who was assigned, not who saw the change (see `references/experimentation.md` §5) |
| Release annotations | Record each build's release date and rollout percentage; analysts join `build` to it |
| Review | Taxonomy changes go through the same review as code; the `data-analyst` agent owns approval |
| CI | `gs.py validate` on the taxonomy; stubs regenerated by `event_taxonomy.py stubs`; playthrough asserts key events fire |

---

## 10. Privacy: no PII, consent, children

**Never collect in analytics events or user properties:** names, emails, phone numbers, postal addresses, precise GPS location, free-text chat or player-entered names, photos, contacts, advertising ids inside custom params, IP addresses in custom params, account passwords or tokens, payment card data, raw receipts. Hashing does not make an email or phone number anonymous — a hash of a known value is still personal data in most regimes.

**Use pseudonymous ids.** A random player id generated at first open (and the SDK's own app-instance id) is enough for every analysis in this skill. Map it to an account id server-side only if needed for support or deletion.

**Consent gating.**
- Do not initialise analytics collection (or set it to disabled) until the consent decision where the law requires consent; record `consent_state` and respect it in every SDK (analytics, ads, MMP). Firebase supports disabling collection and consent signals for analytics and ad storage; configure them per storefront.
- iOS: ad tracking across apps requires the App Tracking Transparency prompt; analytics without cross-app tracking does not, but the privacy nutrition label must disclose what is collected.
- Google Play's Data safety form and Apple's privacy labels must match what the SDKs actually send. Run the `compliance-officer` review whenever the taxonomy adds a data type.

**Children and mixed audiences.** If the game targets or may attract under-13s (or the local age of digital consent), analytics and ads are constrained (no behavioural advertising, limits on persistent identifiers for such purposes, parental consent rules). Use an age gate, child-safe SDK configurations and a minimal taxonomy; route the design through `legal-ethics` before instrumenting.

**Retention and deletion.** Set the analytics data-retention period deliberately; implement user-deletion requests through the SDK's or backend's deletion API keyed by the pseudonymous id.

**Checklist for each new event:** Does any value identify a person by itself or combined with others? Is any field free text? Would the player be surprised to see it? If yes to any, redesign.

---

## 11. Client architecture: the analytics wrapper

```
Game code ──► Analytics.track("level_end", {...})        # one facade, typed stubs generated from the taxonomy
                 │  validate (debug builds): name known, required params present, enums valid, types right
                 │  enrich: common params (session_id, build, player_level, ab_cohort, event_seq, taxonomy_version)
                 │  consent gate: drop or queue until allowed
                 ▼
            Fan-out adapters ──► Firebase/GA4 SDK
                              ├─► GameAnalytics SDK (translated event types)
                              ├─► MMP SDK (only purchase/ad-revenue/key-milestone events for UA optimisation)
                              └─► own backend (economy/purchase truth, raw export)
```

| Concern | Rule |
|---|---|
| Single facade | No direct SDK calls from gameplay code; the wrapper is the only place that knows vendors |
| Typed stubs | Generated with `event_taxonomy.py stubs` (GDScript or C#); gameplay calls `Analytics.level_end(level_id, attempt, success, reason, ...)` so a missing param is a compile/parse error |
| Offline | SDKs queue offline; your own backend adapter needs a persistent queue with a cap and `event_seq` for dedup |
| Batching | Let SDKs batch; never flush on every event (battery, data) |
| Sampling | High-volume telemetry (`perf_sample`) uses the taxonomy `sampling` field; never sample economy or purchase events |
| Determinism | In the sim-core + presentation architecture, the sim emits domain events (level ended, currency granted); a presentation-side analytics listener translates them, so headless playthroughs can assert analytics without SDKs |
| Testability | A recording adapter captures events in tests; the playthrough report can include the event stream as evidence |
| Debug views | Use the vendor's live debug stream (e.g. Firebase DebugView) during QA; exclude debug builds from production data via `debug_build` |

---

## 12. Mapping to Firebase/GA4 and GameAnalytics

GA4 names below are recommended or automatically collected events; GameAnalytics columns describe its event types (business, resource, progression, design, error, ad). Verify current field names against each vendor's SDK docs before implementing (volatile section).

| Studio event | Firebase / GA4 | GameAnalytics | Notes |
|---|---|---|---|
| `first_open`, `session_start` | automatic | automatic session start/end | Do not re-log |
| `tutorial_begin` / `tutorial_complete` | recommended `tutorial_begin` / `tutorial_complete` | design event, e.g. `ftue:begin`, or progression `Start`/`Complete` on `ftue` | Keep `tutorial_step` custom |
| `tutorial_step` | custom | design event `ftue:<step_id>` | Design-event ids are hierarchical (colon-separated); keep the hierarchy shallow and bounded |
| `level_start` | recommended `level_start` (GA4 uses `level_name`; send `level_id` and optionally mirror to `level_name`) | progression event, status `Start`, progression tiers e.g. `world` / `level` | |
| `level_end` (success) | recommended `level_end` with `success = true` | progression `Complete` (optional score) | Wrapper translates by `success` |
| `level_end` (fail/quit) | `level_end` with `success = false` | progression `Fail` | Keep `reason` as a custom param in GA4; in GameAnalytics use a design event for the reason if needed |
| `level_up` | recommended `level_up` | design event or progression | |
| `earn_virtual_currency` | recommended `earn_virtual_currency` (`virtual_currency_name`, `value`) + custom `source` | resource event, flow `Source`, currency, amount, item type, item id | GameAnalytics expects currencies and item types declared at SDK init |
| `spend_virtual_currency` | recommended `spend_virtual_currency` (`virtual_currency_name`, `value`, `item_name`) | resource event, flow `Sink` | |
| `iap_purchase_completed` | custom (plus automatic `in_app_purchase`; optionally the e-commerce `purchase` event) | business event (currency, amount in minor units, item type, item id, cart type; receipt optional for validation) | Send once, after validation |
| `ad_impression` | recommended `ad_impression` (`ad_platform`, `ad_source`, `ad_format`, `ad_unit_name`, `currency`, `value`) | ad / impression events (ILRD integrations with mediation SDKs) | |
| `rv_offer_shown` / `rv_completed` | custom | ad event with action (e.g. show, reward received) and ad type (rewarded video) | |
| `client_error` | custom (`error` is reserved) | error event with severity | Crashes stay in the crash reporter |
| `unlock_achievement`, `post_score`, `join_group`, `share` | recommended names | design events | |
| everything else | custom | design events | |

**Firebase → BigQuery.** For anything beyond standard reports (cohort triangles, level churn, economy balances), enable the BigQuery export and query raw events; SQL patterns are in `references/funnels-cohorts-segmentation.md` §10.

---

## 13. Using `event-taxonomy.schema.json` and `event_taxonomy.py`

File: `.gamestudio/analytics/<slug>.taxonomy.json`; schema `${CLAUDE_PLUGIN_ROOT}/scripts/schemas/event-taxonomy.schema.json`; example `${CLAUDE_PLUGIN_ROOT}/scripts/schemas/examples/example.event-taxonomy.json`. Point `contract.analytics.taxonomy_ref` at the file.

Schema essentials: `schema_version` "1.0"; `naming` "snake_case"; `common_params[]` and `events[]` where each event has `name` (pattern `^(?!firebase_|google_|ga_)[a-z][a-z0-9_]{0,39}$`), `category` (enum), `trigger` (exact firing moment), `params[]` (≤ 25; each `name`, `type` ∈ {string, int, float, bool, timestamp}, `required`, `description`, optional `enum`), `kpis[]` (keys from `references/kpi-dictionary.md` §11), optional `sampling` (0–1).

Procedure:

```bash
# 1. Draft from the design contract (FTUE steps, levels, currencies, IAP ids, ad placements, live events)
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/event_taxonomy.py generate \
  --contract .gamestudio/contract.json --out .gamestudio/analytics/mygame.taxonomy.json

# 2. Edit: prune, add triggers and near-miss params, set enums from the contract ids, add kpis[] per event

# 3. Validate against the schema
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py validate .gamestudio/analytics/mygame.taxonomy.json

# 4. Generate typed engine stubs for the analytics wrapper
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/event_taxonomy.py stubs \
  --taxonomy .gamestudio/analytics/mygame.taxonomy.json --engine godot --out <project>/src/services/analytics/
#   (--engine unity for C#)

# 5. Record the analytics feature in features.json and assert events in the deterministic playthrough
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gs.py feature add --id F020 --title "Analytics wrapper + core taxonomy" \
  --area analytics --priority P0 --accept "All P0 events fire with required params in smoke playthrough"
```

Review checklist for the drafted file: every `contract.ftue.steps[].id` appears in the `tutorial_step.step_id` enum; every currency id appears in the economy event enums; every IAP id appears in `product_id` enums; every rewarded placement appears in `placement` enums; every KPI target in `contract.analytics.kpi_targets` is fed by at least one event's `kpis[]`.

---

## 14. Event QA checklist

Run before every release that touches analytics (and once per soft-launch week on live data):

- [ ] Taxonomy validates (`gs.py validate`); stubs regenerated and compiled.
- [ ] Smoke playthrough emits, in order: `tutorial_begin` → `tutorial_step` × N → `tutorial_complete` → `level_start` → `level_end` (win) → `earn_virtual_currency`; and a forced fail path emits `level_end` with `success=false`.
- [ ] Required params present on 100% of events (live query: count of events with null required param = 0).
- [ ] Enum values in live data ⊆ declared enums; unexpected values listed.
- [ ] `event_seq` gaps < 1% per install-day; duplicates < 0.5% (dedup on `session_id` + `event_seq`).
- [ ] Event counts per DAU stable vs the previous build (± 20% flags review): e.g. `level_start`/DAU, `earn_virtual_currency`/DAU.
- [ ] Revenue reconciliation: Σ `iap_purchase_completed.price_usd_micros` vs store reports within a few percent after refunds and FX.
- [ ] Economy reconciliation: Σ earn − Σ spend per currency ≈ change in Σ balances (from `balance_after` snapshots).
- [ ] No PII: scan string params for `@`, digits patterns resembling phone numbers, and values longer than expected.
- [ ] Debug/QA builds excluded (`debug_build = true` events absent from production dashboards).
- [ ] Consent: with consent declined, no events reach analytics endpoints (proxy capture in QA).

---

## 15. Worked example: from contract to taxonomy

Contract excerpt: FTUE steps `ftue_spawn`, `ftue_merge`, `ftue_power`, `ftue_star` (aha target 45 s); currencies `coins` (soft), `gems` (hard), `stars` (meta); IAP `starter_pack`, `gems_s`, `gems_m`, `remove_ads`; rewarded placements `results_double_coins`, `revive_continue`, `daily_chest`; KPI targets `d1` 0.40, `d7` 0.15, `arpdau_usd` 0.10.

Questions → events:

| Question | Events and params | KPI key |
|---|---|---|
| Do players reach the aha moment within 45 s? | `tutorial_step.seconds_since_install` for `ftue_merge` | `aha_seconds`, `ftue_funnel` |
| Where do new players drop? | `tutorial_begin`, `tutorial_step`, `tutorial_complete`, `level_start`/`level_end` for levels 1–10 | `ftue_funnel`, `d1` |
| Which levels cause churn? | `level_start`, `level_end` {`attempt`, `success`, `reason`, `moves_left`, `targets_left`} | `churn_by_level`, `level_win_rate` |
| Are coins inflating? | `earn_virtual_currency` / `spend_virtual_currency` {`source`/`item_name`, `balance_after`} | `economy_balance` |
| Which rewarded placement earns without hurting D7? | `rv_offer_shown`, `rv_started`, `rv_completed`, `ad_impression` | `rv_opt_in_rate`, `arpdau_usd` |
| Does the starter pack convert, and when? | `offer_shown{trigger}`, `iap_purchase_completed{first_purchase}` | `payer_conversion` |

Result: 16 custom events plus automatic lifecycle events, 6 common params, 8 user properties — comfortably within platform limits and every event linked to a decision. The plugin's example file (`examples/example.event-taxonomy.json`) shows the same structure for a merge-defence game.

---

## 16. Volatile facts (as of Oct 2026 — verify before relying)

- GA4 / Firebase app collection limits (standard properties): 500 distinctly named events per app user (automatically collected events excluded); event names ≤ 40 characters; 25 parameters per event; parameter names ≤ 40 characters; parameter values ≤ 100 characters; 25 user properties; user-property names ≤ 24 characters, values ≤ 36 characters; user-ID ≤ 256 characters. — [Google Analytics Help: collection limits](https://support.google.com/analytics/answer/9267744)
- Reserved event-name prefixes `firebase_`, `google_`, `ga_` and reserved event names (including `error`, `app_background`, `first_open`, `session_start`, `user_engagement`, `in_app_purchase`, `app_remove`, `notification_*`) cannot be logged as custom events. Background knowledge from the Firebase SDK reference, not re-verified this session — check the current reserved list before naming events. — [Firebase Analytics events reference](https://firebase.google.com/docs/reference/android/com/google/firebase/analytics/FirebaseAnalytics.Event)
- GA4 recommended game events (`level_start`, `level_end`, `level_up`, `post_score`, `tutorial_begin`, `tutorial_complete`, `earn_virtual_currency`, `spend_virtual_currency`, `unlock_achievement`) and the `ad_impression` event parameters — background knowledge, verify parameter names. — [GA4 recommended events](https://developers.google.com/analytics/devguides/collection/ga4/reference/events)
- GameAnalytics event types (business, resource, progression with Start/Complete/Fail statuses and up to three progression tiers, design events with colon-separated ids, error events with severities, ad and impression events) — background knowledge; the docs URL structure changed and could not be fetched this session. — [GameAnalytics docs](https://docs.gameanalytics.com/)
- Firebase's official MCP server (via `firebase-tools`) exposes Remote Config, Crashlytics, Auth, Firestore and Cloud Messaging tools usable from Claude Code; Analytics reporting was not among the tool groups found in Oct 2026 research, so plan on BigQuery export for analysis (verify the current tool list). — [Firebase MCP docs](https://firebase.google.com/docs/ai-assistance/mcp-server)
- Firebase Analytics, Remote Config, A/B Testing and Crashlytics are no-cost products (background). — [Firebase pricing](https://firebase.google.com/pricing)
- iOS attribution has moved from SKAdNetwork to AdAttributionKit, supported by the major MMPs; Google retired Privacy Sandbox on Android in Oct 2025, so GAID plus consent remains the Android basis for now. — [Moburst](https://www.moburst.com/mobile-attribution-in-2026-what-marketers-actually-need-to-know/); [BetaNews](https://betanews.com/2025/10/20/google-is-retiring-privacy-sandbox/)
