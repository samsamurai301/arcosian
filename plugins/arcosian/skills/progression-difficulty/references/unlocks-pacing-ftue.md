# Unlocks, Pacing and FTUE

The first minutes decide whether a player ever sees your progression system. The first week decides whether they understand it. This file covers how new things enter the game: the complexity budget, novelty schedules and unlock density, what to gate and how, first-time user experience (FTUE) design (time to aha, teaching in context, progressive disclosure, tutorial beats, permission prompts), first-session, first-day and first-week design, onboarding funnel targets and diagnosis, re-onboarding for returners and new features, and worked examples with numbers. Curves that schedule unlocks are in `references/progression-curves.md`. Screen-level onboarding UX (layouts, copy, thumb zones) is in `mobile-ux`. Retention analytics are in `player-analytics`.

## Contents

1. Principles of pacing new things
2. The complexity budget
3. Novelty schedule and unlock density
4. What to unlock: a gating catalogue
5. Feature gating methods
6. FTUE design
7. First session, first day, first week
8. Onboarding funnel: targets and diagnosis
9. Re-onboarding: returners and new features
10. Worked examples
11. Unlocks and FTUE checklist
12. Volatile facts (as of Oct 2026 — verify before relying)

---

## 1. Principles of pacing new things

1. **Core loop first, everything else later.** The first session teaches the core verb and lets the player enjoy it. Every meta system waits until the core is fun on its own (doctrine principle 2).
2. **One new concept at a time.** Teach, let the player use it, then add the next. Two simultaneous new concepts halve retention of both. This is a practical reading of cognitive-load research as summarised for games by Celia Hodent (*The Gamer's Brain*, 2017).
3. **Just in time, not just in case.** Unlock a system when the player has a reason to want it. The shop arrives when coins have piled up; upgrades arrive when the first wall is felt; the guild arrives when the player has invested enough to care about a team.
4. **Dangle, then deliver.** Show locked features with their unlock condition ("Arena: level 12"). Visible goals create pull. Invisible features create surprise, but no anticipation.
5. **Every unlock is a beat.** Celebrate it (animation, sound, a short mini-FTUE) and give the player something to do with it immediately.
6. **Pacing is measured in minutes, not levels.** Convert unlock levels to play minutes with the TTL table (`references/progression-curves.md` §6) and check the gaps.

## 2. The complexity budget

Treat the player's working memory as a budget. Count **concepts** introduced: a verb, a goal type, a currency, a resource, a screen, a system or a rule exception.

**Budget (studio starting targets):**

| Window | Max new concepts | Typical contents |
|---|---|---|
| First 60 s | 1–2 | The core verb; one goal |
| First session (≈ 5–10 min) | 4–6 | Verb, 1–2 goal types, first obstacle, first reward, the meta hook |
| Day 1 (sessions 1–3) | 6–10 | Soft currency, first upgrade or meta step, first booster, daily reward |
| Days 2–7 | About 1–2 per day | Second currency, social, events, pass, new mechanics |
| Weeks 2–4 | About 1 per 2–4 days | Advanced systems (crafting, guild wars, PvP) |

**Rules.**

- **Currencies:** at most one currency in session 1 (soft). Add the premium currency when the shop opens. Add event and material currencies only after day 3. Every currency needs a reason the player can state.
- **Screens:** the first session should touch at most two or three screens (play, result, map or home).
- **Rule exceptions** ("this blocker ignores bombs") count double. Introduce them late, one per teach-test-twist sequence.

Record the budget per beat in `contract.ftue.steps[].teaches` and per unlock in `contract.progression.tracks[].unlocks`. A reviewer can then count concepts directly.

## 3. Novelty schedule and unlock density

Novelty (something new to see, do or own) keeps curiosity alive between mastery beats. Density should be high early and taper as the player's own goals take over.

**Novelty interval targets (studio starting hypotheses):**

| Phase | Something new every… | Examples of "new" |
|---|---|---|
| First 10 minutes | 1–2 min | New level element, first reward, first upgrade, map reveal |
| First hour of play | 5–15 min | New world element, booster, system tease, cosmetic |
| Days 2–7 | About 1 notable unlock per day | New system, world, event entry, social feature |
| Weeks 2–4 | Every 2–4 days | New mode, chapter, collection set |
| Month 2+ | The live-ops cadence | Events, seasons, content drops (`liveops`) |

**Computing an unlock schedule from TTL.**

1. List candidate unlocks with their minimum prerequisite (what must be learned first) and their *pull moment* (when the player starts wanting them).
2. Place each unlock at the play minute of its pull moment. Respect the novelty intervals and the complexity budget.
3. Convert minutes to track values using the cumulative TTL table T(N): the unlock level is the smallest N with T(N) ≥ the target minute.
4. Check collisions: no two systems in the same session through day 3; at most one major unlock per level-up.
5. Write to `progression.tracks[].unlocks[]` as `{"at": N, "unlock": "..."}`.

## 4. What to unlock: a gating catalogue

| Feature | Typical gate | Why gate it | When to show it locked |
|---|---|---|---|
| Core verb variants (special pieces, combos) | Levels, teach-test-twist cadence | Complexity budget | Not needed; introduce in levels |
| Boosters (pre-level, in-level) | First wall or first fail; gift 2–3 on unlock | Teach their value before selling them | From the first booster tease |
| Upgrades / meta progression | After the core loop is fun (session 1–2) | Gives wins meaning | From session 1 (meta hook) |
| Shop | When coins pile up; or the first wall | Avoid early pressure | When the first coins arrive |
| Daily rewards / login calendar | End of session 1 or start of session 2 | Return reason | At the session 1 exit |
| Missions / quests | Day 1–2 | Directs attention once basics are known | Day 1 |
| Events | Day 2–5 (after the core plus one meta) | Events need understood systems | When an event is live |
| Season / battle pass | Day 3–7 | Needs a daily habit to be worth it | When the pass track is visible |
| Social (friends, gifting) | Day 1–3 | Value rises with investment | Early, as "help from friends" |
| Teams / guilds | Day 3–7 (investment, chat moderation) | Teams need committed members | From day 2 |
| PvP / ranked | After mastery basics and enough power (often day 3–10) | Losing early to experts drives churn | From day 2 with a level condition |
| Advanced systems (crafting, research) | Week 2+ | Depth for retained players | When the prerequisite exists |
| Ads (rewarded) | After the first win; never in the first minute | Value exchange must be understood | At the first natural offer moment |
| Interstitial ads | Not in the first session (studio rule); then rate-limited | Early interruption is a top FTUE killer | Never "shown locked" |
| Purchases (starter offer) | After the first meaningful wall or day 2–3 | Avoid buying before liking | When the shop opens |

Public examples of gating philosophy (stable observations): *Clash of Clans* ties building caps to Town Hall level, so every upgrade sits inside a predictable gate. *Clash Royale* unlocks cards through arenas, so new decisions arrive with new opponents. *Genshin Impact* gates co-op and some modes behind Adventure Rank. *Hay Day* opens new production buildings at farm levels. Most mobile farming and building games follow this pattern.

## 5. Feature gating methods

| Gate | Mechanism | Pros | Cons | Use for |
|---|---|---|---|---|
| Level gate | Account or player level ≥ N | Predictable; pairs with TTL | Ties pacing to grind speed | Most system unlocks |
| Content gate | Clear chapter or level N | Ties unlock to demonstrated skill | Blocks stuck players | Mechanics, worlds, PvP |
| Time gate | Day N since install, or a timer | Controls calendar pacing; compresses archetype spread | Feels artificial; needs disclosure | Events, pass, social |
| Achievement gate | Do X (win 3 matches, collect 10) | Ensures prerequisite skills | Can confuse | Advanced modes |
| Social gate | Have friends or a team | Encourages invites | Excludes solo players; always have a solo path | Co-op, team events |
| Purchase gate | Pay to unlock | Revenue | Violates "earn the core" | Cosmetics and premium extras only; never core systems |

**Hard vs soft gates.** A hard gate makes the feature unavailable. A soft gate makes it available but discouraged (a "recommended level 15" warning). Use soft gates for optional content, so skilled players can skip ahead, and hard gates when the feature would break without its prerequisite.

**Locked-feature UI.** Show the icon greyed out with the condition ("Unlocks at level 12"), a progress bar if it is close, and a celebration when it opens. Do not send notifications for locked features. Do not show more than about 3–4 locked features on the home screen at once (clutter becomes noise).

**Gate graph sanity.** Draw all gates as a directed graph (feature → prerequisite). It must be acyclic. Every feature must be reachable without payment and without other players (solo path).

## 6. FTUE design

### 6.1 What the FTUE must achieve, in order

1. **Get to fun fast:** the core verb with juice, within seconds.
2. **Establish the fantasy:** who I am, what I am doing, why it matters (one line, one image).
3. **First win:** a guaranteed success that feels earned.
4. **First meaningful choice:** something that makes the player feel smart.
5. **Reveal the long goal (the meta hook):** a glimpse of what progress builds toward.
6. **Set up session 2:** an exit hook (timer, daily reward, cliffhanger, unopened chest).

### 6.2 Time to aha

**Definition.** Seconds from first launch (app open) to the first moment the player experiences the core fun. Examples: the first satisfying chain or cascade, the first merge that clearly beats a wave, the first big crowd smash. Store the target in `contract.ftue.aha_seconds_target` and log a proxy event (for example, `ftue_aha` fired on the first combo of size ≥ N).

**Budgeting the seconds:**

| Segment | Budget (studio targets) | Notes |
|---|---|---|
| Cold start to first frame | Per `contract.technical.perf_budgets.cold_start_sec` | Engineering budget (`mobile-performance`) |
| Splash, logos, intro | ≤ 5 s total; skippable | Logos cost players. Cut them in the FTUE where licences allow |
| First interactive input | ≤ 10–15 s after the first frame | The player should touch the game almost immediately |
| Aha moment | ≤ 30–60 s for casual; ≤ 90 s ceiling | Practitioner guidance treats > ~90 s as a retention risk (§12) |
| First win | ≤ 60–120 s | Celebrate it |

**Measure it.** Run deterministic FTUE playthroughs that time every beat (`playtest` skill; `playtest-report.metrics.time_to_first_reward_sec`). Use human or persona playtests for perceived clarity (`arcosian:player-simulator`).

### 6.3 Teach in context

**Principles.**

- **Show, then let them do it within 2–3 seconds.** One instruction, one action. The hand pointer appears on the exact target.
- **Constrain the first boards** so the only possible action is the right one, then loosen the constraints over 3–5 levels.
- **Use the world as the teacher.** Level 1-1 of *Super Mario Bros.* (1985) is the classic example, widely analysed. The first enemy approaches in a safe open space, and early blocks and power-ups are placed so players almost inevitably discover them, without a word of text. *Portal* (2007) taught through test chambers that each isolate one idea before combining them.
- **Feedback carries the lesson.** Juice the correct action (sound, particles, haptics). Make wrong actions harmless and explained ("Match 3 of the same colour").
- **No walls of text.** One line per screen at most, under about 10 words. Icons over words.
- **Teach right before need.** Introduce the booster on the level where it is useful, not in a menu tour.

**Tutorial forms, ranked (best first for mobile):**

| Form | Use |
|---|---|
| Embedded in level design (affordances, constrained boards) | Core verb, early mechanics |
| Contextual one-liner plus hand pointer | New element on its teach level |
| Interactive mini-sequence (2–3 forced steps) | A new system (upgrade screen, shop) |
| Optional help screen or codex | Reference for rules exceptions |
| Video or slideshow tutorial | Almost never in casual mobile |

### 6.4 Progressive disclosure

Hide what the player does not need yet, and reveal it with ceremony.

**HUD and menu reveal order (typical casual game):**

| Stage | Visible |
|---|---|
| First 60 s | Board or play area, goal counter, move or time limit |
| First win | Result screen with stars and coins |
| Session 1, after 2–4 wins | Map or home screen; meta progress bar |
| End of session 1 | Daily reward, one menu button (settings) |
| Day 1–2 | Shop, boosters bar, missions |
| Day 2–7 | Social, events, pass, inbox |

Settings, account linking, language and privacy controls must be reachable at all times from the start (`legal-ethics`, `accessibility-localization`). Disclosure applies to game systems, not to player rights.

### 6.5 Tutorial beat structure

Each beat maps to `contract.ftue.steps[]` {`id`, `goal`, `teaches`, `max_seconds`}, and its id becomes the `step` parameter of the tutorial analytics event.

| Field | Rule |
|---|---|
| `id` | Stable, snake_case (`ftue_merge_1`); never renumber after launch (analytics continuity) |
| `goal` | A player-visible achievement ("merge two golems") |
| `teaches` | Exactly one new concept (verb or mechanic id), sometimes zero (a reward beat) |
| `max_seconds` | The time budget; deterministic playtests flag beats that exceed it |

**Beat checklist.** Can the beat be failed? (It should not be in the first 3 beats.) Does it end in a reward? Does the next beat start within about 2 seconds? Can an experienced player skip it?

### 6.6 Forced vs free, and skipping

- Force only the **core verb** and the **first meta step**. Release control as soon as the player has done each once.
- Offer **skip** for players with a cloud save or a reinstall (detect the account), and a "replay tutorial" option in settings.
- If a player idles for about 8–10 s on a step, re-show the pointer with a slightly different cue. Do not repeat the same text.

### 6.7 Failure inside the FTUE

- The first levels are **unlosable** in practice (FAWR 0.95–1.0; `references/difficulty-design.md` §5).
- If failure is part of the lesson (a game about risk), make it instant, free and explained, with an immediate retry and a hint.
- Never charge lives or show a purchase on an FTUE failure.

### 6.8 First-launch technical and consent steps

| Step | Rule |
|---|---|
| First-launch download | Ship enough content in the install to play the FTUE offline; download the rest in the background (`mobile-performance`, `store-release`) |
| Age gate / consent | Where legally required, ask before collecting data, with as little friction as compliant (`legal-ethics`) |
| Tracking permission prompt (iOS) | Show after the player has seen value; follow current platform rules on pre-prompts (`store-release`) |
| Notification permission | Ask when the player has a reason (a timer they will want to know about). Android 13 and later require a runtime notification permission, so placement matters on both platforms (verify current platform rules) |
| Account creation / sign-in | Never required before play; offer linking after investment (day 1–3), framed as save protection |
| Ads | No interstitials in the first session (studio rule); a rewarded ad only after its value is clear |

### 6.9 FTUE anti-patterns

| Anti-pattern | Detect | Fix |
|---|---|---|
| Long intro cutscene or lore dump | Time to first input > 15 s | Cut to a one-line premise plus in-play storytelling |
| Menu tour before play | First screen is the home screen with pointer tours | Start in the core loop; reveal menus later |
| Wall of text | Text boxes > 1 line; players tap through | Teach by doing; icons |
| Everything at once | > 6 concepts in session 1 | Apply the complexity budget |
| Permission and account prompts first | Prompts before the first win | Move them after value moments |
| Early monetization pressure | Offers or interstitials in session 1 | Gate monetization surfaces (§4) |
| Fake choice in tutorial | Options shown but only one allowed, repeatedly | Constrain silently, or give a real choice |
| Unskippable for returners | Reinstalls replay a 5-minute tutorial | Account detection; skip |
| Tutorial teaches what the game does not use | Concepts taught early, unused for days | Teach just in time |
| FTUE tuned on developers | Team members find it slow, so it gets shortened past clarity | Test with target players (`playtest`) |

## 7. First session, first day, first week

### 7.1 First session (0–10 minutes): timeline template

| Time | Beat | Purpose |
|---|---|---|
| 0:00–0:15 | First input in the core loop | Hands on immediately |
| 0:15–0:45 | Aha moment (combo, merge, smash) | The fun is proven |
| 0:45–2:00 | First win and celebration; first currency | Competence and reward |
| 2:00–4:00 | 2–3 quick levels, one new element | Fluency |
| 4:00–6:00 | Meta hook: spend currency on the first meta step | Investment and fantasy |
| 6:00–8:00 | A slightly harder level (still about 0.9 FAWR); first booster tease | Light tension |
| 8:00–10:00 | Long-goal reveal (map, collection, world) plus exit hook | A reason to return |

Design so that a 3-minute first session still reaches the aha moment, the first win and the meta hook. Many first sessions end early because of real-world interruptions.

### 7.2 Exit hooks

| Hook | Mechanism | Ethical note |
|---|---|---|
| Timer ready later | A chest or building finishes in 1–4 h | Fine; notify only with permission |
| Daily reward preview | "Tomorrow: 2 boosters" | Fine; avoid punishing streak loss harshly |
| Cliffhanger | Story or map reveal partially shown | Fine |
| Unfinished collection | 4/5 items collected | Fine; avoid paid-only completion |
| Energy refill | Lives full again in X min | Use carefully; it doubles as a session limiter |

### 7.3 First day (sessions 1–3)

- **Session 2 must start with a win** (warm-up level, claim the timer reward, daily reward). Never open with a hard level or a sales screen.
- Introduce **one system per session**: for example missions in session 2, the shop in session 3.
- By the end of day 1, the player should know: the core verb, the meta goal, how to get stronger, and why to come back tomorrow.

### 7.4 First week (D1–D7): schedule template

| Day | New this day (one or two) | Return reason created |
|---|---|---|
| D0 (install) | Core loop, meta hook, daily reward | Timer, tomorrow's reward |
| D1 | Missions; first booster gift; first hard level (around levels 15–25) | Mission refresh |
| D2 | Social (friends, gifting); shop opens fully | Gifts from friends |
| D3 | Event entry (if live), or a second world tease | Event progress |
| D4 | Pass track visible (free track); collection set | Pass tier progress |
| D5 | Team or guild join prompt (if the game has teams) | Team requests |
| D6 | New mechanic family or world | Curiosity |
| D7 | Weekly reward or first week-end recap; streak milestone | Weekly loop starts |

Adapt to the genre. The rule is roughly **one notable new thing per day**, each building on the previous day's knowledge.

### 7.5 First month sketch

Weeks 2–4 shift from unlocks to **mastery and identity**: harder chapters, PvP or leaderboards for those who want them, collections, team play and the first full season or event cycle. By about day 30 the live-ops calendar is carrying novelty (`liveops`). Track day-14 and day-30 unlock completion. Systems most players never unlock are wasted production.

## 8. Onboarding funnel: targets and diagnosis

### 8.1 Funnel definition (events)

```
app_first_open → ftue_start (first input) → ftue_step{id} … → ftue_complete → first_win
→ level_5 → level_10 → session_2_start → d1_return
```

Use the step ids from `contract.ftue.steps[]` as the `step` parameter. Taxonomy generation: `event_taxonomy.py generate --contract .gamestudio/contract.json --out .gamestudio/analytics/taxonomy.json`.

### 8.2 Funnel targets (studio starting heuristics, not benchmarks)

| Transition | Target | Losses usually come from |
|---|---|---|
| first_open → ftue_start | ≥ 95% | Load time, crashes, consent friction, long intros |
| Each mandatory tutorial step | ≥ 97–98% | Confusing instruction, unresponsive input, a step that is too long |
| ftue_start → ftue_complete | ≥ 85–90% | Too many steps, forced menus, failure in FTUE |
| ftue_complete → first meta step | ≥ 90% | Meta not visible or not attractive |
| Session 1 → session 2 | Game-specific; benchmark against the D1 data in §12 | Weak exit hook; no aha |

Calibrate these against your own soft-launch cohorts. Published retention benchmarks (§12) describe D1/D7/D30, not step conversions, so step targets are internal standards.

### 8.3 Computing and reading a funnel

```
python3 ${CLAUDE_PLUGIN_ROOT}/skills/progression-difficulty/scripts/balance_math.py funnel \
  --steps "first_open:10000,tutorial_start:9400,ftue_step_3:8900,first_win:8500,level_5:7600,level_10:6300,d1_return:2900" \
  --min-step 0.9
```

| Step | Step conversion | Cumulative | Share of total loss |
|---|---|---|---|
| first_open | 1.000 | 1.000 | 0% |
| tutorial_start | 0.940 | 0.940 | 8.5% |
| ftue_step_3 | 0.947 | 0.890 | 7.0% |
| first_win | 0.955 | 0.850 | 5.6% |
| level_5 | 0.894 | 0.760 | 12.7% |
| level_10 | 0.829 | 0.630 | 18.3% |
| d1_return | 0.460 | 0.290 | 47.9% |

**Reading it.**

1. **first_open → tutorial_start at 94%** misses the 95% target. Check cold start time, crash-free sessions on low-end devices, and any prompt before play.
2. **Tutorial steps at about 95%** are below the 97–98% step target. Find the slowest step in deterministic and persona playtests and cut or split it.
3. **level_5 → level_10 at 83%** is the largest in-session leak (18% of all loss). Is a difficulty spike or an unclear mechanic in levels 6–10? Check per-level FAWR and churn (`references/difficulty-design.md` §12).
4. **D1 return of 29% of first opens:** compare with the benchmark ranges in §12, then work on the session 1 exit hook and the D1 schedule. Fix in-session leaks first. They are cheaper and compound into D1.

The command exits 1 when any step is below `--min-step`, so it can be a CI-style check on exported funnel data.

### 8.4 Diagnosis table

| Pattern | Likely cause | Action |
|---|---|---|
| Drop at the first screen | Load or crash, or a consent wall | Perf and crash triage; streamline consent |
| One tutorial step is much worse than its neighbours | Unclear instruction or input problem on that step | Rewrite; enlarge touch targets; shorten |
| Steady decay across all steps | Tutorial too long overall | Cut beats; teach later |
| Good FTUE, poor session 2 | No aha, or weak exit hook | Strengthen the hook; check time to aha |
| Good D1, poor D7 (D7/D1 low) | Days 2–7 lack novelty or goals | Apply the first-week schedule (§7.4) |

## 9. Re-onboarding: returners and new features

**Returning players (lapsed 7+ days).**

- **Welcome back** with a gift, a one-screen recap ("You were building the Keep; 2 stars to the next room") and a warm-up level.
- **Catch-up** for systems that moved on without them (`references/progression-curves.md` §10).
- **Re-teach** only what changed, and keep the old tutorial skippable.
- Do not greet a returner with expired offers, a full inbox or a forced event tutorial.

**New features for existing players (mid-life FTUE).**

- Every new system ships with a **mini-FTUE** of at most 3 beats, using the same `ftue` step structure. Track it with its own funnel.
- Unlock it for existing players through a visible "New!" entry point, not by a forced interruption mid-level.
- Gate it the same way as for new players (by level or content). Do not dump every new feature on high-level veterans at once.

## 10. Worked examples

### 10.1 Merge-defence game: FTUE plan (aha target 45 s)

| Step id | Goal | Teaches | max_seconds | Check |
|---|---|---|---|---|
| `ftue_spawn` | Wake the first golem | `tap_spawn` | 8 | Pointer on the spawn button; any tap succeeds |
| `ftue_merge` | Merge two tier-1 golems | `drag_merge` | 12 | Only one valid merge on the board |
| `ftue_power` | See the merged golem pop the first wave | "merging is the source of power" | 20 | Wave tuned to lose against tier-1 and win against tier-2 |
| `ftue_star` | Win level 1, place the first star in the keep | `meta_restore` | 90 | Win guaranteed; meta screen opens |

Budget: 8 + 12 + 20 = 40 s to aha (the merged golem beating the wave), inside the 45 s target. A deterministic playthrough asserts each beat's time. The first booster appears on level 4. The shop opens when coins exceed the first upgrade's cost. The daily reward appears at the exit of session 1.

### 10.2 Seven-day unlock schedule for a hybrid-casual runner from TTL

Player-level TTL (from the progression design): level 2 at 2 min, level 5 at 12 min, level 8 at 45 min, level 10 at day 1 end (≈ 70 min), level 15 at day 3 (≈ 3 h), level 20 at day 6–7 (≈ 6 h). Mid archetype, about 60 productive min per day.

| Unlock | Pull moment | Target minute | Level (from T(N)) | Day (mid archetype) |
|---|---|---|---|---|
| Upgrade: starting crowd | Feels the first loss to a bigger crowd | 3 | 2 | D0 |
| Upgrade: income | Coins pile up after a few runs | 10 | 4 | D0 |
| Daily reward | Session 1 exit | 12 | 5 | D0 |
| Skins (cosmetic) | First big coin balance | 40 | 8 | D0–D1 |
| Missions | Habit forming | 70 | 10 | D1 |
| Rewarded ad doubler | Understands coin value | 75 | 10 (after the first offer moment) | D1 |
| Second world | Mastery of world 1 | 180 | 15 | D3 |
| Event entry | Daily habit established | 240 | 16 | D4 |
| Pass (free track) | Daily habit plus events understood | 300 | 18 | D5 |
| Leaderboard | Skill plateau reached | 360 | 20 | D6–D7 |

Collision check: day 0 has four unlocks across about 40 minutes (within the "new every 1–2 min early, every 5–15 min later" targets). Days 1–7 have about one each.

### 10.3 Funnel triage

See §8.3. Priority order: (1) the level 6–10 spike (largest in-session loss, cheap to fix with level tuning); (2) the tutorial step exceeding its `max_seconds`; (3) cold start on low-end Android; (4) the session 1 exit hook. Re-measure with the same funnel and an A/B holdout (`ab_test.py`).

## 11. Unlocks and FTUE checklist

- [ ] The complexity budget is counted per beat and per unlock; session 1 introduces at most 4–6 concepts and one currency.
- [ ] The novelty schedule meets interval targets for the first 10 minutes, the first hour and days 2–7.
- [ ] Every unlock has a pull moment, a celebration and a mini-FTUE of at most 3 beats.
- [ ] The gate graph is acyclic; every feature is reachable solo and without payment.
- [ ] Locked features show their condition; there are no notifications for locked features.
- [ ] `contract.ftue` has an `aha_seconds_target` (≤ 60 s casual) and steps with `teaches` and `max_seconds`.
- [ ] Deterministic FTUE playthrough evidence records every beat's time; persona playtests confirm clarity.
- [ ] FTUE levels are unlosable; no lives, offers or interstitials in session 1.
- [ ] Permission, account and consent prompts are placed after value, within current platform and legal rules.
- [ ] The first-session timeline survives a 3-minute session (aha, first win and meta hook all reached).
- [ ] The first-week schedule exists, with one notable new thing per day.
- [ ] Funnel events and step ids match the contract; funnel targets are defined and checked with `balance_math.py funnel`.
- [ ] Returner and mid-life feature onboarding are designed.

## 12. Volatile facts (as of Oct 2026 — verify before relying)

| Fact | Source |
|---|---|
| GameAnalytics benchmarks (16,000+ live mobile games, via secondary write-ups): median D1 about 22%, D7 just under 4%, D30 about 0.7–0.8%; the top 1% hold about 64–68% D1. | Segwise (citing GameAnalytics 2026) — https://segwise.ai/blog/mobile-gaming-app-user-retention-strategies |
| Among top-quartile games, D1 is reported at about 31–33% on iOS vs 25–27% on Android. | Segwise — https://segwise.ai/blog/mobile-gaming-app-user-retention-strategies |
| A practitioner "viability screen" for marketed titles: about 25–30% D1, 10–15% D7, 3–6% D30. Some sources call these working heuristics, not published medians. | Playio — https://blog.playio.co/d1-d7-d30-retention-benchmarks-2026 |
| D7/D1 ratio diagnostic (practitioner consensus, not a hard rule): below 0.30 points to a first-session or FTUE problem; 0.30–0.44 to weak engagement on days 2–5. | GameDev.net — https://gamedev.net/blogs/entry/2298160-the-d7d1-retention-ratio-for-mobile-games-a-complete-guide |
| If the aha moment takes more than about 90 seconds, a significant share of users reportedly never return for a second session (practitioner guidance; the same post repeats an unsourced uplift claim, so treat it with caution). | Playio (Aug 2026) — https://blog.playio.co/mobile-game-onboarding-retention |
| Practitioner guides say the FTUE shapes D1 and recommend fixing onboarding before late-game retention. | AppFollow 2026 — https://appfollow.io/blog/mobile-game-retention |
