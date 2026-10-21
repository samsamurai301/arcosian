# Progression Curves

A progression curve is a promise about time. Every XP table, upgrade cost list or pass track decides how many minutes, sessions and days a player spends before the next meaningful change. This file treats curves as pacing instruments. You design time-to-level first and derive costs from it. It covers the five curve families the plugin's tooling speaks (linear, polynomial, exponential, logistic, piecewise), the closed forms you need to reason about them, famous XP tables and what they teach, how income growth changes the felt curve, hard caps and soft caps, catch-up mechanisms, multi-track systems, idle and pass curves, `progression_calc.py` usage, and four fully worked examples with numbers. Currency flows and sinks live in `economy-design`. Level difficulty lives in `references/difficulty-design.md`.

## Contents

1. Vocabulary: requirement, reward, power and time curves
2. The pacing equation
3. Curve families: formulas, closed forms, behaviour
4. Side-by-side shape comparison
5. Famous XP tables and their lessons
6. Designing from time-to-level (the senior method)
7. Income growth and the felt curve
8. Play time, sessions and calendar time
9. Caps and soft caps
10. Catch-up mechanisms
11. Multi-track progression
12. Idle and incremental curves
13. Pass and season track curves
14. `progression_calc.py` usage
15. Worked examples
16. Progression curve checklist

---

## 1. Vocabulary: requirement, reward, power and time curves

| Curve | Question it answers | Typical unit | Owner |
|---|---|---|---|
| Requirement curve | How much does level n cost? | XP, coins, shards per level | This file |
| Cumulative requirement | How much in total to reach level n? | Total XP | This file |
| Income (reward) curve | How fast does the player earn the requirement unit at level n? | XP per minute, coins per run | `economy-design` + this file |
| Time-to-level (TTL) | How long does level n take? | Minutes of play per level | This file (the design target) |
| Power curve | How much stronger is the player at level n? | Stat totals, DPS, effective HP | `references/power-and-balance.md` |
| Content difficulty curve | How hard is the content met at level n? | Enemy power, target win rate | `references/difficulty-design.md` |

**Rule.** Players never feel the requirement curve directly. They feel TTL, and they feel the gap between their power curve and the content difficulty curve. A table of costs means nothing until it is divided by income.

Notation used below: `n` = level index starting at 1; `c(n)` = cost to go from level n to n+1; `C(N)` = cumulative cost to reach level N+1 = Σ c(1..N); `i(n)` = income per minute at level n; `t(n) = c(n) / i(n)` = TTL in minutes.

## 2. The pacing equation

```
t(n) = c(n) / i(n)            # minutes of play for level n
T(N) = Σ_{n=1..N} t(n)        # minutes of play to reach level N+1
days(N) = T(N) / (sessions_per_day × minutes_per_session)
```

Three consequences shape every decision:

1. **Only the ratio matters.** Doubling both cost and income changes nothing except number inflation. You choose number size for feel (big numbers feel generous, small numbers feel precious) and the ratio for pacing.
2. **The growth rate of t(n) is the growth rate of c(n) minus the growth rate of i(n)** (exactly, for exponentials: if c grows ×r per level and i grows ×q per level, t grows ×r/q per level). An exponential cost against an exponential income with the same rate gives a flat TTL.
3. **Players are a distribution.** A casual archetype at 12 minutes a day and an engaged archetype at 60 minutes a day reach level 30 at calendar times that differ by 5×. Design TTL in play minutes, then check calendar days per archetype (section 8, and `economy_sim.py` archetypes).

## 3. Curve families: formulas, closed forms, behaviour

### 3.1 Linear

```
c(n) = b + g·(n − 1)
C(N) = N·b + g·N·(N − 1)/2               # quadratic in N
ratio c(n+1)/c(n) = 1 + g/(b + g(n−1))   # tends to 1
```

- **Feels like:** fast acceleration early, then every level feels almost the same as the last. With constant income, TTL grows linearly.
- **Use for:** short tracks (≤ 20 levels), tutorial ramps, chapter or world counts, pass tiers (with g = 0, a flat cost), star-gated chapter unlocks.
- **Avoid for:** long tracks with growing income. Income that grows linearly turns a linear cost into a flat TTL; income that grows faster than that makes TTL shrink, so late levels come faster than early ones.

### 3.2 Polynomial (power law)

```
c(n) = b·n^e
C(N) ≈ b·N^(e+1)/(e+1)                   # good for N ≳ 10
ratio c(n+1)/c(n) = ((n+1)/n)^e          # tends to 1, slower than linear's
```

- **e = 1:** linear through the origin. **e = 1.5:** a gentle long-haul curve. **e = 2:** the classic quadratic RPG feel. **e = 3:** the cube law. Several Pokémon growth groups are cubic (section 5).
- **Feels like:** costs keep growing, but by a shrinking percentage, so a player whose income grows even slowly will feel progress speed up later. Good for tracks where power should keep coming.
- **Use for:** character levels where income also grows, upgrade tracks with many parallel instances (hero levels, card levels), mastery tracks.

### 3.3 Exponential (geometric)

```
c(n) = b·r^(n−1)
C(N) = b·(r^N − 1)/(r − 1)
doubling interval = ln 2 / ln r levels    # r = 1.07 → 10.2; 1.08 → 9.0; 1.15 → 5.0
ratio c(n+1)/c(n) = r                    # constant percentage growth
```

- **Feels like:** fine early, then a wall. With linear or polynomial income, TTL grows exponentially, so a cap arrives "naturally" at the level where TTL exceeds patience.
- **Use for:** idle and incremental games (where income also compounds), upgrade costs that must outrun a compounding income, prestige-driven loops, deliberate soft walls near the end of a track.
- **Danger:** the most common progression bug in mobile games is an exponential cost (often r = 1.1 to 1.2) paired with linear income. Compute the TTL at the last level before shipping (section 15.1).

### 3.4 Logistic (S-curve)

```
f(n) = L / (1 + e^(−k·(n − n0)))
```

`L` is the plateau, `k` the steepness, and `n0` the midpoint (f(n0) = L/2). Two uses:

- **As a per-level cost:** cheap early levels, a steep middle, then a plateau where every late level costs about L. With constant income the late game has a constant TTL. This suits endgame grinds you want to keep predictable, such as paragon-style infinite levels.
- **As a cumulative or power target:** power rises slowly, then quickly, then saturates. This suits mastery and collection completion. The last few percent are slow, but the curve stays bounded.

Behaviour: the logistic is symmetric around n0. For an asymmetric S (fast rise, long tail), use a piecewise curve or a Gompertz-style form, `L·exp(−β·e^(−k·n))`.

**`progression_calc.py --formula logistic` is a floored variant of this form.** It prices each level as `xp_to_next(L) = B·(1 + 9·σ(G·(L − N/2)))`, where `σ` is the sigmoid, `B` is `--base`, `G` is `--growth` (the steepness `k`, default 0.25) and `N` is `--levels`. The cost therefore starts near `B`, passes `5.5·B` at the fixed midpoint `N/2`, and plateaus at `10·B`. The plateau (`L` above) is always 10 × base, the midpoint cannot be moved, and the curve never starts near zero as the analytic form does. To approximate the form used in §4 (`L` = 10,000, `k` = 0.1, `n0` = 50) run `curve --formula logistic --levels 100 --base 1000 --growth 0.1`: it gives 1,067 at level 1, 5,500 at level 50 and 9,940 at level 100 (the analytic form gives 74, 5,000 and 9,933).

### 3.5 Piecewise

Define segments, each with its own family, and join them **continuously** (the cost at a seam is equal from both sides). Ideally also join them **smoothly**, with the percentage growth roughly continuous, so that no level suddenly costs 40% more than the previous one.

```
c(n) = linear(n)        for 1 ≤ n ≤ 10      # tutorial ramp: fast, readable
     = poly(n)·s1       for 10 < n ≤ 40     # main game: steady growth
     = exp(n)·s2        for 40 < n ≤ 60     # endgame: soft wall into cap
# s1, s2 chosen so values match at n = 10 and n = 40
```

- **Use for:** almost every shipped track longer than 30 levels. Real XP tables are usually piecewise, hand-edited or both (section 5).
- **Seam check:** print c(n−1), c(n), c(n+1) at every seam. A jump of more than about 1.5× the neighbouring growth reads as a wall. A drop reads as a bug.
- **`progression_calc.py --formula piecewise` is one fixed shape, not a segment builder.** It splits `--levels` into three equal thirds and grows the cost by `1 + (G − 1)·w` per level, with `G` = `--growth` (default 1.15) and `w` = 0.25, 0.6 and 1.0 for the first, second and last third. With `--base 100 --levels 60` and the default `G` the growth is ×1.0375 per level up to level 20, ×1.09 from level 21 to 40 and ×1.15 from level 41, giving 100 at level 1, 201 at level 20, 1,128 at level 40 and 18,461 at level 60. The seams are continuous (each level still builds on the previous one), but the growth steps up at levels 21 and 41. Segment designs like the one in §15.2 (linear, then geometric, then linear) are built by hand or with a short script and shipped as a table.

### 3.6 Hybrids worth knowing

| Form | Formula | Behaviour | Use |
|---|---|---|---|
| Poly × exp | `b·n^e·r^n` | Polynomial early, exponential late | Long RPG tracks that need a late wall |
| Offset exponential | `a + b·r^(n−1)` | Linear-feeling start, exponential tail | Upgrades whose first steps must feel affordable |
| Exponential with milestone discounts | `b·r^(n−1) × (0.5 at every 25th level)` | Sawtooth TTL | Idle milestones, "level 25 / 50 / 100" bonuses |
| Table-driven | Hand-edited list | Anything | Final shipping tables. Generate from a formula, then hand-tune 5–10% |

## 4. Side-by-side shape comparison

All curves start at c(1) ≈ 100. Linear: b = 100, g = 50. Poly 1.5 and poly 2: b = 100. Exp 1.08 and exp 1.15: b = 100. Logistic: L = 10,000, k = 0.1, n0 = 50 (the analytic form of §3.4, which starts near zero; `progression_calc.py --formula logistic` is floored at `--base` and plateaus at 10× it, see §3.4 and §14). The linear, poly and exp columns can be reproduced exactly with `progression_calc.py curve`.

**Per-level cost c(n):**

| n | Linear | Poly e=1.5 | Poly e=2 | Exp r=1.08 | Exp r=1.15 | Logistic |
|---|---|---|---|---|---|---|
| 1 | 100 | 100 | 100 | 100 | 100 | 74 |
| 2 | 150 | 283 | 400 | 108 | 115 | 82 |
| 5 | 300 | 1,118 | 2,500 | 136 | 175 | 110 |
| 10 | 550 | 3,162 | 10,000 | 200 | 352 | 180 |
| 25 | 1,300 | 12,500 | 62,500 | 634 | 2,863 | 759 |
| 50 | 2,550 | 35,355 | 250,000 | 4,343 | 94,231 | 5,000 |
| 75 | 3,800 | 64,952 | 562,500 | 29,741 | 3,101,989 | 9,241 |
| 100 | 5,050 | 100,000 | 1,000,000 | 203,682 | 102,114,213 | 9,933 |

**Cumulative cost C(N):**

| N | Linear | Poly 1.5 | Poly 2 | Exp 1.08 | Exp 1.15 | Logistic |
|---|---|---|---|---|---|---|
| 10 | 3,250 | 14,267 | 38,500 | 1,449 | 2,030 | 1,201 |
| 25 | 17,500 | 131,310 | 552,500 | 7,311 | 21,279 | 7,569 |
| 50 | 66,250 | 724,870 | 4,292,500 | 57,377 | 721,772 | 71,130 |
| 100 | 257,500 | 4,050,122 | 33,835,000 | 2,748,452 | 782,874,967 | 504,933 |

**Level-over-level growth c(n+1)/c(n):**

| n | Linear | Poly 1.5 | Poly 2 | Exp 1.08 |
|---|---|---|---|---|
| 1 | 1.50 | 2.83 | 4.00 | 1.08 |
| 5 | 1.17 | 1.32 | 1.44 | 1.08 |
| 10 | 1.09 | 1.15 | 1.21 | 1.08 |
| 25 | 1.04 | 1.06 | 1.08 | 1.08 |
| 50 | 1.02 | 1.03 | 1.04 | 1.08 |

Reading the tables:

- Polynomial curves front-load their growth. Poly 2 quadruples from level 1 to 2, but by level 50 it grows only 4% per level. Use a non-zero offset, or a linear first segment, if you do not want a brutal level 2.
- Exponential curves back-load. Exp 1.08 is cheaper than linear until about level 40, then dwarfs it. Exp 1.15 is cheaper than poly 1.5 until roughly level 40, then explodes.
- The growth table is the most useful view for tuning. Players notice growth rates, not absolute numbers. Keep level-over-level growth in a band (for example 3–12% in the main game) and treat anything outside it as a deliberate beat.

## 5. Famous XP tables and their lessons

These are public, long-lived tables, summarised for what they teach. Values were computed from the published formulas.

### 5.1 RuneScape skill XP (exponential with a linear term)

Per-level increment: `floor(n + 300·2^(n/7)) / 4`, summed and floored. The exponential term doubles every 7 levels.

| Level | Total XP |
|---|---|
| 10 | 1,154 |
| 30 | 13,363 |
| 50 | 101,333 |
| 70 | 737,627 |
| 80 | 1,986,068 |
| 90 | 5,346,332 |
| 92 | 6,517,253 |
| 99 | 13,034,431 |

**Lessons.** Level 92 is almost exactly half of level 99's XP, a fact the community celebrates. A doubling-every-7 curve makes the last 7 levels cost as much as all previous ones combined. This works on PC because the game has huge parallel content, very long horizons and players who treat 99 as a status symbol. On mobile, a curve like this needs (a) parallel tracks so a player is never stuck on one wall, and (b) the top levels framed as optional prestige, not as a gate.

### 5.2 Pokémon growth groups (cubic polynomials)

| Group | Total XP to level n | Level 50 | Level 100 |
|---|---|---|---|
| Fast | 4n³/5 | 100,000 | 800,000 |
| Medium fast | n³ | 125,000 | 1,000,000 |
| Medium slow | 1.2n³ − 15n² + 100n − 140 | ≈117,360 | ≈1,059,860 |
| Slow | 5n³/4 | 156,250 | 1,250,000 |

**Lessons.** (1) One family, different multipliers. Varying the multiplier per species creates rarity and investment differences without new maths. (2) The medium-slow polynomial is cheaper than medium fast in the early-mid levels (560 vs 1,000 at level 10) and dearer at 100. It is an S-shaped trade, so species that start fast finish slow. (3) Cubic cumulative curves mean per-level costs grow quadratically. They stay playable because XP rewards scale with the defeated creature's level, so income grows too (section 7).

### 5.3 Tabletop fifth-edition fantasy RPG (hand-tuned piecewise)

The current edition of the best-known tabletop fantasy RPG uses a hand-written table. Levels 2, 3 and 4 need 300, 900 and 2,700 total XP (×3 per level), 6,500 at level 5, and then the increments flatten to near-linear steps up to 355,000 at level 20.

**Lessons.** Fast early levels hook new players and teach the system. Mid and late increments flatten so a table group keeps levelling at a steady rhythm. The table reads as if it were designed in *sessions per level* rather than XP. That is the method in section 6.

### 5.4 Mobile account-level patterns (stable observations, no numbers claimed)

- Account levels in mobile F2P usually rise **fast in session 1** (several levels in the first 10–15 minutes), then slow sharply after day 1. Unlocks hang on early levels (section 11; `references/unlocks-pacing-ftue.md`).
- Many live games **raise the level cap** in content updates rather than shipping a deep table on day one. Ship a table with headroom, and keep the cap in remote config.

## 6. Designing from time-to-level (the senior method)

Never start from "XP = 100 × 1.1^n". Start from the experience timeline.

**Procedure.**

1. **Write the beat sheet.** For the track, write when (in play minutes) the player should hit key levels and what each delivers. Example: "Level 5 in the first session (≈10 min): the second hero slot. Level 10 by the end of day 1 (≈30 min): guilds teased. Level 20 by day 4–5: PvP arena. Level 30 by about week 3: the second world."
2. **Choose TTL at anchors.** Turn the beat sheet into TTL at 3–5 anchor levels: t(1), t(10), t(30), t(cap).
3. **Pick a family per segment** that interpolates the anchors. Linear TTL for the tutorial, geometric TTL for the main climb, linear or flat TTL for the endgame.
4. **Model income i(n).** Include every XP source: per action, per level win, quests, dailies, events and boosts. Use the expected average player, then check archetypes (section 8).
5. **Derive cost:** c(n) = t(n) × i(n). Round to readable numbers. Keep the growth table in band.
6. **Simulate days per archetype.** Compute calendar days to each anchor for a light, a mid and a heavy archetype, or run `economy_sim.py` with an XP resource.
7. **Check unlock collisions.** Do no more than one major unlock per level-up, and never put two new systems in one session (`references/unlocks-pacing-ftue.md` §2).
8. **Write it to the contract** (`progression.tracks[].curve`, `unlocks[]`), then generate the table with `progression_calc.py` (section 14). Hand-edit only within ±10% and record why.

**TTL design targets (starting hypotheses for mobile F2P, not industry facts).**

| Phase | Target TTL per level | Why |
|---|---|---|
| First session (levels 1–5) | 1–3 min | Frequent rewards while habits form; each level-up teaches or unlocks |
| Day 1–3 | 3–10 min | Still at least one level-up per session |
| Week 1–2 | 10–40 min | About one level-up per day for a mid archetype |
| Mid game | 40–120 min | Levels become milestones. Shorter loops (quests, chests) carry the minute-to-minute rewards |
| Endgame / cap approach | Flat or slow growth | Prestige framing. Cap raises arrive in updates |

**Rule of thumb.** At every point in the game, the player should be able to see **some** progress bar move within one session. If the account level stops doing that, a faster track (missions, mastery, pass) must take over. The fastest moving bar sets the felt pace.

## 7. Income growth and the felt curve

Income almost always grows with level: higher-level enemies give more XP, bigger levels pay more coins, multipliers stack. Ignoring this is the root of "the curve looked fine in the spreadsheet".

| Cost family | Income family | Felt TTL | Typical outcome |
|---|---|---|---|
| Linear | Constant | Linear rise | Fine for short tracks |
| Linear | Linear | Flat, tends to constant | Levels feel samey; fine for pass tiers |
| Poly e | Linear | Grows like n^(e−1) | e = 2 gives linear TTL growth, a classic RPG feel |
| Poly e | Exponential | Shrinks eventually | Late game accelerates; can feel great if intended (power fantasy) |
| Exp r | Linear | Exponential wall | Hard cap by patience; deliberate or a bug |
| Exp r | Exp q | Grows ×(r/q) per level | Idle games: tune r slightly above q (section 12) |

**Procedure for income-aware tuning.**

1. Write i(n) as a formula or a table. Include **all** sources, and take the 50th-percentile player, not the best player.
2. Compute t(n) = c(n)/i(n) for every level, and plot t(n) and the growth of t(n).
3. Look for **TTL inversions**, where a later level is faster than an earlier one by more than 20% for no designed reason. They usually come from an income jump such as a new zone or a multiplier unlock. Either smooth the cost or celebrate the jump as an intentional "power spike" beat.
4. Look for **runaway walls**: growth of t(n) above about 15% per level for more than 5 levels, outside a planned wall.

## 8. Play time, sessions and calendar time

```
calendar_days(N) = T(N) / (sessions_per_day × session_minutes × active_share)
```

`active_share` is the fraction of session time that actually produces progression income (menus, ads and social screens produce none). Typical modelling values sit between 0.6 and 0.9. Measure it in your own telemetry.

**Archetype check (example: reaching level 30 takes about 370 min of productive play, from §15.2):**

| Archetype | Sessions/day | Min/session | Active share | Productive min/day | Days to level 30 |
|---|---|---|---|---|---|
| Light | 2 | 4 | 0.75 | 6 | 62 |
| Mid | 4 | 6 | 0.8 | 19.2 | 19 |
| Heavy | 8 | 8 | 0.85 | 54.4 | 7 |

A 9× spread between light and heavy is normal. Decide which archetype the beat sheet is written for (usually mid) and make sure the light archetype still sees a weekly milestone. Energy systems, daily caps and offline timers compress this spread. That is often their real job (`economy-design`, `mechanics-codex` file 08).

## 9. Caps and soft caps

### 9.1 Hard caps

A hard cap is a maximum level or stat value. Reasons to cap: it bounds balance (`references/power-and-balance.md`), lets live ops sell "cap raise" updates, and protects PvP fairness. Rules:

- **Show the cap** once players are within about 20% of it. Hidden caps feel like bugs.
- **Convert overflow.** XP earned at the cap should flow somewhere: a prestige currency, a paragon track, mastery points or cosmetics. Wasted income at the cap is a churn trigger.
- **Raise caps in steps of 5–10 levels**, and give returning-player catch-up when you do (section 10).

### 9.2 Soft caps (diminishing returns)

A soft cap lets a stat keep growing while each point is worth less. The standard forms (all available in `scripts/balance_math.py softcap`):

| Form | Output for stat x | Property | Example use |
|---|---|---|---|
| Hyperbolic | `cap·x/(x + k)` | Half of cap at x = k. Each point adds the same effective HP when used for mitigation | Armour, cooldown, dodge |
| Exponential | `cap·(1 − e^(−x/k))` | 63% of cap at x = k; saturates faster | Crit chance, resistances |
| Piecewise | Full value to k, then `rate` per point | Simple and explainable | Stat thresholds in UI ("beyond 50, each point gives half") |
| Logarithmic | `a·ln(1 + x/k)` | Unbounded but slow | Prestige multipliers, idle bonuses |
| Rating conversion | `percent = rating / (rating + K(level))` | K grows with level, so the same rating is worth less at higher levels | Level-scaled secondary stats |

**Worked contrast (hyperbolic, k = 100, cap = 100%):**

| Stat x | Output | Marginal per point |
|---|---|---|
| 0 | 0% | 0.99 |
| 25 | 20% | 0.63 |
| 50 | 33.3% | 0.44 |
| 100 | 50% | 0.25 |
| 200 | 66.7% | 0.11 |
| 300 | 75% | 0.06 |

**A notable public example.** In late 2020 *League of Legends* replaced its percentage cooldown reduction, which had a hard cap, with "ability haste", which converts as `CDR = haste / (haste + 100)`. Each point of haste gives the same increase in casts per minute, so stacking no longer has a cliff and no longer needs a hard cap. The general lesson: **express the stat in the unit whose value is linear to the player** (casts per minute, effective HP), and let a hyperbolic conversion produce the displayed percentage.

**Hard cap vs soft cap decision:**

| Situation | Use |
|---|---|
| A stat reaching 100% would break the game (dodge, damage reduction, CDR) | Hyperbolic or exponential soft cap, plus a hard cap at a safe value |
| PvP fairness matters more than expression | Hard cap and normalisation in ranked modes |
| Players love big numbers (idle, ARPG) | Logarithmic or rating conversion; no hard cap |
| Players must understand it at a glance | Piecewise with a UI explanation |

## 10. Catch-up mechanisms

Catch-up compresses the distance between behind and ahead players. Use it for late joiners, lapsed returners, alts and new seasons, and to keep social groups together.

| Mechanism | How it works | Formula / parameter | Notes |
|---|---|---|---|
| Rested XP | Offline time banks a bonus multiplier on future XP | e.g. 2× XP until the bank is spent; bank fills at x% of a level per hour offline, capped | WoW popularised it. It rewards breaks instead of punishing them |
| Behind-the-curve multiplier | XP boost when below the median (or cohort, or friends') level | `m = clamp(1 + α·(L_median − L)/L_median, 1, m_max)` | Typical m_max is 2–3×. Show it ("Catch-up bonus ×1.8") |
| Server-age acceleration | Later players on an old server or season earn faster | Rate ∝ days since server start | Common in 4X and MMO-lite |
| Level sync / scaling | Content or players scale to a shared level | Scale stats to the zone band | See the Oblivion caution below |
| Content compression | Old content made cheaper when new content ships | Old chapter costs × 0.5 | Keeps new content reachable for new installs |
| Bad-luck protection | Guaranteed progress after repeated failure | Pity counters (`gacha_calc.py`) | Progress-side pity; see `economy-design` |
| Comeback packs | Returning-player bundles of boosts and currency | Triggered after N days lapsed | Must not be pay-gated to be catch-up |

**Cautions.**

- **Scaling everything erases progress.** *The Elder Scrolls IV: Oblivion* (2006) is the standard cautionary tale. Enemies scaled with player level, so levelling the "wrong" skills could make the game harder. Players learned to avoid levelling, which inverts the reward. Scale within bands, and let the player outgrow old content.
- **Catch-up must not punish the ahead player.** Boost the behind player; never slow the leader in PvE. In PvP, matchmaking and brackets handle it (`references/dynamic-difficulty.md` §7).
- **Disclose catch-up.** Visible bonuses read as generosity. Hidden ones discovered later read as unfairness.

## 11. Multi-track progression

Mobile games run several tracks at once: account level, chapter or world progress, character levels, mastery, collections and a season pass. Design the set, not each track alone.

**Track roles.**

| Role | Speed | Example tracks | Job |
|---|---|---|---|
| Fast | Moves every session or every few minutes | Missions, pass tier, per-level stars | Constant feedback |
| Medium | Moves every 1–3 days | Account level, chapter progress | Unlock cadence, milestones |
| Slow | Moves every week or more | Mastery, collections, prestige | Long-term goals and identity |
| Seasonal | Resets every 4–10 weeks | Pass, ranked ladder | Renewal, live-ops anchor |

**Rules.**

1. **Pick one spine.** One track drives unlocks (usually account level or chapter progress). Other tracks reward, but do not gate core features.
2. **Never cross-gate in a cycle.** If track A requires a B level and B requires an A level, someone will deadlock. Draw the gate graph and check it is acyclic.
3. **Stagger level-ups.** Fast, medium and slow tracks should not all level up in the same minute, then all stall. Offset their periods so at least one bar is about to move at any time.
4. **One shared income can feed several tracks** (for example, level wins give account XP, pass XP and character XP). That multiplies the reward feeling without multiplying sources.
5. **Store each track** in `contract.progression.tracks[]` with `type` (`player_level`, `chapter`, `character_level`, `mastery`, `battle_pass`, `prestige`, `collection`, `story`).

## 12. Idle and incremental curves

Idle games are where exponential costs belong, because income compounds too.

- **Generator cost:** `cost_k = b·r^k` for the k-th copy owned. Long-running idle games commonly use r between about 1.07 and 1.15. *Cookie Clicker* buildings rise 15% per purchase. Anthony Pecorella's "The Math of Idle Games" series (Kongregate blog, 2016) works through this family and analyses *AdVenture Capitalist*-style coefficients.
- **Income:** linear in generator count, times multipliers (milestones at 25/50/100 owned, upgrades, prestige).
- **Felt pacing:** track **time-to-next-meaningful-purchase (TTNP)**. A healthy idle game shows a sawtooth TTNP. It grows until a multiplier lands, drops, and grows again. When TTNP passes a threshold (minutes early, hours late), the player should want to prestige.
- **Prestige currency:** usually a root (square or cube) of lifetime earnings, so each reset needs a growing run to give a meaningful boost. The economics of resets are covered in `economy-design` and the `prestige` card in `mechanics-codex`.

**Idle tuning rule.** Set the cost growth r slightly above the effective income growth between multiplier milestones, so TTNP rises gently. Then let milestones knock TTNP back down. If TTNP rises monotonically for more than about 30 minutes of active play without a milestone or prestige option, players stall.

## 13. Pass and season track curves

Pass tracks are almost always **flat** (constant XP per tier) or **lightly stepped**, because players compare progress with the calendar.

```
required_xp = tiers × xp_per_tier
xp_available(d) = d × daily_xp + floor(d/7) × weekly_xp + match_xp(d)
completion_day = smallest d with xp_available(d) ≥ required_xp
```

**Design targets (studio starting hypotheses; verify with your own telemetry):**

- A player who plays about 70–80% of days and does most weekly missions should finish the paid track with about one to two weeks to spare.
- A daily player should finish early enough to reach overflow tiers (bonus rewards), so the last weeks of the season still pay.
- Paid tier skips should shorten the timeline, never be required to finish within the season for the target archetype.
- Never make the free track unfinishable as a pressure tactic. Disclose tier count and expected effort.

See §15.3 for a worked pass, and `monetization` and `liveops` for pass design and pricing.

## 14. `progression_calc.py` usage

The plugin's progression calculator lives at `${CLAUDE_PLUGIN_ROOT}/scripts/progression_calc.py` (stdlib only, `--json` for machine output, `--selftest`). Its command lines are fixed by the blueprint:

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/progression_calc.py curve \
    --formula linear|poly|exp|logistic|piecewise --levels N \
    [--base B] [--growth G] [--exponent E] [--xp-per-min X] [--json]

python3 ${CLAUDE_PLUGIN_ROOT}/scripts/progression_calc.py time-to-level \
    --table PATH --xp-per-min X [--json]
```

**How to use it in the procedure of section 6.**

| Step | Command | Read |
|---|---|---|
| Explore a family | `curve --formula exp --levels 50 --base 100 --growth 1.08 --xp-per-min 40` | Per-level and cumulative cost, and time per level at constant income |
| Compare families | Run `curve` for linear, poly, exp at matched level-1 cost; diff the outputs | Where each crosses the others (compare with §4) |
| Check an edited table | `time-to-level --table .gamestudio/economy/xp_table.json --xp-per-min 40` | Minutes per level and cumulative hours for a hand-tuned table |
| Archetype days | Divide cumulative minutes by productive minutes per day (§8) | Days to anchors per archetype |

**What the flags mean for each formula.** `xp_to_next(L)` is the XP to go from level L to L+1, for L = 1..N (`--levels`); `--base` B is the cost of level 1 → 2 (default 100). `--help` only says "formula-specific growth", so the mapping is:

| `--formula` | `xp_to_next(L)` | `--growth` G | `--exponent` E |
|---|---|---|---|
| `linear` | `B + G·(L − 1)` | XP added per level (default 50) | unused |
| `poly` | `B·L^E` | unused | the exponent (default 1.5) |
| `exp` | `B·G^(L − 1)` | per-level multiplier (default 1.15) | unused |
| `logistic` | `B·(1 + 9·σ(G·(L − N/2)))` | steepness (default 0.25); floor ≈ B, plateau 10·B, midpoint fixed at N/2 | unused |
| `piecewise` | exponential in three equal thirds, per-level multiplier `1 + (G − 1)·w` with w = 0.25, 0.6, 1.0 | late-game multiplier (default 1.15) | unused |

Real runs: `curve --formula logistic --levels 100` prints 100 at level 1, 550 at level 50 and 1,000 at level 100; `curve --formula piecewise --levels 60` prints 100, 201 (level 20), 1,128 (level 40) and 18,461 (level 60). The linear, poly and exp families reproduce the closed forms of §3 exactly.

Notes:

- Check the level-1, middle and level-N values of any logistic or piecewise table against the intent before you commit it, because these two families are the script's own fixed shapes (§3.4 and §3.5), not the general forms of section 3.
- `--xp-per-min` assumes **constant income**. For growing income, either compute t(n) = c(n)/i(n) yourself or feed the table and run `time-to-level` per income band. The worked example in §15.2 shows the income-aware path.
- Store the chosen curve in the contract as `{"formula": "exp", "params": {"base": 100, "growth": 1.08}}`. That is the same vocabulary the script uses, so another agent can regenerate the table. It holds for all five families as long as `growth` carries the meaning in the table above (for `logistic` the steepness, for `piecewise` the late-game multiplier); the `segments` form in §15.2 is design documentation that the script does not read.

`scripts/balance_math.py softcap` covers diminishing-returns curves, and `funnel` gives level funnel checks once telemetry exists.

## 15. Worked examples

### 15.1 Hybrid-casual upgrade cost: diagnosing an exponential wall

**Setup.** A runner pays coins per run. Income per run grows with level progress: `i(n) = 30 + 4n` coins. The upgrade cost draft is `c(n) = 50·1.12^(n−1)`. Measure pacing in **runs per upgrade** (runs are about 45 s each).

| Upgrade n | Cost | Coins/run | Runs per upgrade |
|---|---|---|---|
| 1 | 50 | 34 | 1.5 |
| 5 | 79 | 50 | 1.6 |
| 10 | 139 | 70 | 2.0 |
| 15 | 244 | 90 | 2.7 |
| 20 | 431 | 110 | 3.9 |
| 25 | 759 | 130 | 5.8 |
| 30 | 1,337 | 150 | 8.9 |

**Diagnosis.** Exponential cost against linear income: runs per upgrade grow almost 6× from upgrade 1 to 30. If the design wants a satisfying upgrade every 2–3 runs through upgrade 30 (≈ the first week), this is a wall from about upgrade 15.

**Two fixes, compared:**

| Upgrade n | Fix A: r = 1.08, same income — runs/upgrade | Fix B: keep r = 1.12, income ×1.06 per level (coin multiplier track) — runs/upgrade |
|---|---|---|
| 1 | 1.5 | 1.7 |
| 10 | 1.4 | 2.7 |
| 20 | 2.0 | 4.7 |
| 30 | 3.1 | 8.2 |

Fix A delivers the target pacing. Fix B shows that a compounding income multiplier at 6% cannot rescue a 12% cost growth, because the TTL still grows ×(1.12/1.06) ≈ 1.057 per level. Choose A, or raise the income compounding to about 10–11% if the multiplier track is itself a desired system. Then confirm with `economy_sim.py`, since players spread coins across several upgrade tracks.

### 15.2 RPG hero level 1–60 designed from time-to-level

**Beat sheet (mid archetype):** level 10 inside the first 30 minutes; level 20 at about 2 hours of play; level 30 at about 6 hours; level 60 at about 45 hours.

**Attempt 1: a single geometric TTL.** t(n) = 1 min × r^(n−1), with r solved so that 59 level-ups take 60 h. That gives r ≈ 1.106. Result: level 30 at only 2.8 h, and the last level alone takes 5.8 h. It is back-loaded, so the mid game is rushed and the end is a slog. **Rejected.**

**Attempt 2: piecewise TTL.**

| Segment | TTL rule | Rationale |
|---|---|---|
| Levels 1–10 | Linear 1 → 5 min | Tutorial cadence: a level-up every few minutes |
| Levels 10–30 | Geometric 5 → 45 min (×9 over 20 levels, ≈11.6% per level) | Main climb; one level per session, then one per day |
| Levels 30–59 | Linear 45 → 110 min | Predictable endgame; levels become milestones |

**Income model:** XP per productive minute, `i(n) = 30·1.04^(n−1)` (higher-level stages give more XP).

**Derived table (selected rows):**

| Level n → n+1 | TTL (min) | Cumulative play to reach n+1 | XP/min | Cost c(n) = t × i |
|---|---|---|---|---|
| 1 | 1.0 | 1 min | 30 | 30 |
| 2 | 1.4 | 2.4 min | 31 | 45 |
| 5 | 2.8 | 9.4 min | 35 | 97 |
| 10 | 5.0 | 30 min | 43 | 213 |
| 15 | 8.7 | 1.1 h | 52 | 450 |
| 20 | 15.0 | 2.1 h | 63 | 948 |
| 25 | 26.0 | 3.9 h | 77 | 1,998 |
| 30 | 45.0 | 6.9 h | 94 | 4,210 |
| 40 | 67.4 | 16.5 h | 139 | 9,336 |
| 50 | 89.8 | 29.8 h | 205 | 18,415 |
| 59 | 110.0 | 44.9 h | 292 | 32,096 |

All four anchors are met: level 10 is reached at 25 min, level 20 at 1.9 h, level 30 at 6.2 h and level 60 at 44.9 h. Calendar check: at 25 productive minutes a day, level 60 takes about 108 days; at 45 minutes, about 60 days. If the live-ops plan raises the cap at day 90, the heavy archetype will wait at the cap for about a month. Give the cap an overflow track (§9.1).

**Contract entry:**
```json
{"id": "hero_level", "type": "character_level",
 "curve": {"formula": "piecewise", "params": {
   "segments": [
     {"to": 10, "ttl_min": [1, 5], "shape": "linear"},
     {"to": 30, "ttl_min": [5, 45], "shape": "geometric"},
     {"to": 59, "ttl_min": [45, 110], "shape": "linear"}],
   "income_xp_per_min": "30*1.04^(n-1)"}},
 "unlocks": [{"at": 5, "unlock": "second skill slot"}, {"at": 10, "unlock": "gear crafting"},
             {"at": 20, "unlock": "arena (PvP)"}, {"at": 30, "unlock": "world 2"}]}
```

`progression_calc.py` cannot generate this table: its `piecewise` is the fixed three-phase exponential of §3.5 and it reads no `segments`. Compute c(n) = t(n) × i(n) per segment in a few lines of Python (or a spreadsheet), save the result as a JSON list or CSV with an `xp_to_next` column, and check it with `progression_calc.py time-to-level --table PATH --xp-per-min X`.

### 15.3 Season pass: 50 tiers in 8 weeks

**Setup.** 50 tiers × 1,000 XP = 50,000 XP. The season is 56 days. Weekly missions pay 2,500 XP per week. Target: a player who plays 42 of 56 days (75%) and completes 6 of 8 weekly sets finishes the track.

```
42·d + 6·2,500 ≥ 50,000  →  d ≥ 834  →  daily XP d = 850
```

**Check:**

| Player | XP over season | Finishes |
|---|---|---|
| 75% days, 6 weeklies | 42×850 + 15,000 = 50,700 | Just at the end (tight but fair) |
| Every day, all weeklies | 56×850 + 20,000 = 67,600 | Week 6 (≈ day 41–42); about 2 weeks of overflow tiers |
| 50% days, 4 weeklies | 28×850 + 10,000 = 33,800 | Tier ≈ 33; consider an end-of-season XP boost week |

Decisions: add 10 overflow tiers (repeatable cosmetic currency) so daily players keep earning, and run a "double XP weekend" in week 7 to rescue the 50% player without devaluing the pass.

### 15.4 Soft-capped crit chance

**Setup.** Crit rating from gear runs 0–600 in the late game. Design wants about 25% crit at mid gear (rating 150), never above 50%, and every point to matter.

Choose exponential: `crit = 50% × (1 − e^(−x/k))`. Solve 25% at x = 150: `1 − e^(−150/k) = 0.5` → k = 150/ln 2 ≈ 216.

| Rating | Crit |
|---|---|
| 0 | 0% |
| 150 | 25.0% |
| 300 | 37.5% |
| 450 | 43.8% |
| 600 | 46.9% |

Each successive 150 rating gives half the previous gain, so players see diminishing returns but never a dead stat. Show the conversion in the stat tooltip. Check it with `balance_math.py softcap --formula exponential --k 216 --cap 50 --values 0,150,300,450,600`.

## 16. Progression curve checklist

- [ ] The beat sheet exists in play minutes for the target archetype, with 3–5 anchors.
- [ ] Each track has a role (fast, medium, slow, seasonal); one spine track drives unlocks.
- [ ] TTL is computed with **income growth included**; no unintended TTL inversions or runaway walls.
- [ ] Level-over-level growth stays inside a stated band; every outlier is a named beat.
- [ ] Seams in piecewise curves are continuous, and growth does not jump more than about 1.5× at a seam.
- [ ] Calendar days were checked for light, mid and heavy archetypes; the light archetype sees a weekly milestone.
- [ ] Caps are visible near the top, and overflow income is converted, not wasted.
- [ ] Soft caps use hyperbolic, exponential or piecewise forms with a tooltip explanation.
- [ ] Catch-up exists for late joiners and returners, and it is disclosed.
- [ ] The gate graph across tracks is acyclic.
- [ ] Curves are stored in `contract.progression.tracks[].curve` with `formula` and `params`, and tables are regenerated with `progression_calc.py` (hand-built segment curves are stored as tables and checked with `time-to-level`).
- [ ] Pass track completion was checked for the 50%, 75% and 100% player.
