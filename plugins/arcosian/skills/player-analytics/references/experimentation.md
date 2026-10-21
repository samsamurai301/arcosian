# Experimentation for Games

How to run A/B tests and other controlled experiments in a live or soft-launched mobile game so that decisions are right more often than they are wrong: when to test at all, how to write the hypothesis, how to choose primary and guardrail metrics, how big and how long a test must be (power, sample size, minimum detectable effect), how to randomise and log exposure, how to avoid the classic traps (sample-ratio mismatch, novelty effects, peeking, multiple comparisons, interference through shared economies), how to reduce variance (CUPED, stratification, winsorising), when holdouts and bandits are the better tool, and how to build a remote-config layer that makes all of it cheap. Formulas are given with worked numbers; the plugin's `ab_test.py` does the arithmetic and `analytics_calc.py srm` checks assignment health. The core references are Kohavi, Tang and Xu, *Trustworthy Online Controlled Experiments* (2020), and the statistical papers cited in each section.

## Contents

1. When to experiment (and when not to)
2. The hypothesis
3. Metrics: primary, secondary, guardrails
4. Power, sample size and MDE
5. Randomisation unit, assignment and exposure
6. Health checks: A/A tests and sample-ratio mismatch
7. Novelty, primacy and long-term effects
8. Peeking and sequential testing
9. Variance reduction: CUPED, stratification, winsorising, ratio metrics
10. Multiple comparisons
11. Holdouts and holdbacks
12. Multi-armed bandits
13. Remote config: the experiment substrate
14. Game-specific pitfalls
15. Analysis procedure and readout template
16. Tool usage
17. Volatile facts (as of Oct 2026 — verify before relying)

---

## 1. When to experiment (and when not to)

| Situation | Approach |
|---|---|
| Parameter tuning with measurable short-term outcome (reward amounts, ad cooldowns, level move counts, offer price points, FTUE step order) | A/B test via remote config |
| Change whose effect shows on retention or LTV (FTUE redesign, new meta feature, economy change) | A/B test on **new installs**, sized for D7/D30 and run long enough to mature |
| Bug fixes, crash fixes, performance work, accessibility | Ship to everyone (staged rollout), monitor; testing a fix is unethical and wasteful |
| Large redesigns that cannot coexist in one build (new core loop) | Separate soft-launch builds or geo split; accept weaker inference |
| Very small traffic (soft launch with a few hundred installs/day) | Only test changes expected to move metrics a lot (≥ 15–20% relative); otherwise sequence changes and use before/after with care, or use bots and playtests |
| Short-lived choices with fast feedback (creative, store ordering in a 3-day event) | Bandit (section 12) |
| Ethically questionable variants (manipulative offers, dark patterns) | Do not test; the doctrine forbids shipping them, so testing them is moot |
| Measuring cumulative impact of a quarter's work | Global holdout (section 11) |

**Rule:** every experiment must have a decision attached: "if the primary metric improves by ≥ MDE without guardrail harm, we ship B; otherwise we keep A and try X."

---

## 2. The hypothesis

Template (fill every bracket before building):

> Because **[evidence: data, playtest, research]**, we believe that **[change]** for **[population]** will **[increase/decrease] [primary metric] by at least [MDE]** because **[mechanism]**. We will measure it at **[horizon]** with **[n per arm, duration]**, guarded by **[guardrails]**. If it wins we **[ship decision]**; if it loses or is flat we **[next step]**.

Examples:

| Area | Hypothesis (abridged) | Primary | Guardrails |
|---|---|---|---|
| FTUE | Level 6 churns 4.8× baseline with 39% win rate; adding two moves raises D7 for new installs by ≥ 1.0 pp because players stop hitting a wall before the first meta unlock | D7 classic retention (new installs) | D1, session length, levels/day, booster purchases |
| Ads | A rewarded "double coins" placement on the results screen raises ad ARPDAU by ≥ 10% without hurting D7, because coins are the binding constraint on meta progress | Ad ARPDAU (D0–D7 per install) | D7, soft-currency hoard days, IAP ARPDAU |
| Economy | Halving the cost of the first meta build raises D3 by ≥ 1.5 pp because players see the meta payoff in session 1 | D3 retention | Soft-currency balance p50 at D7, D7 IAP conversion |
| Offer | A starter pack at $1.99 vs $4.99 raises D7 payer conversion by ≥ 30% relative and D30 ARPU is not lower | D7 cohort payer conversion | D30 ARPU (secondary-confirmatory), refund rate |

---

## 3. Metrics: primary, secondary, guardrails

| Role | Definition | Rules |
|---|---|---|
| **Primary** | The one metric the decision rests on | Sensitive enough to move within the test, aligned with long-term value, decided before launch. One per experiment |
| Secondary | Metrics that explain the mechanism (did players actually use the feature?) | Exploratory; do not "win" on a secondary when the primary is flat |
| **Guardrails** | Metrics that must not get worse beyond a tolerance | Retention D1/D7, crash-free users, load time, session length, refunds, ratings, complaints, revenue (for non-monetization tests), fairness/ethics indicators |
| Data-quality checks | SRM, exposure balance, event volumes per user | A failing check invalidates the test |

**Overall evaluation criterion (OEC).** Kohavi and colleagues recommend a single metric (or weighted combination) that predicts long-term value and is measurable in the test window. For F2P games a practical OEC is **D7 or D14 cumulative net revenue per install plus a retention guardrail**, or **D7 retention** for non-monetization changes.

**Choosing a primary by experiment type:**

| Experiment type | Good primary | Why not something else |
|---|---|---|
| FTUE / onboarding | D1 or D3 retention of new installs; tutorial completion as secondary | Completion alone can rise while retention falls (e.g. skipping teaches nothing) |
| Early difficulty | D7 retention; levels completed by D3 as secondary | Win rate is the lever, not the outcome |
| Meta feature | D7/D14 retention; feature adoption secondary | |
| Economy tuning | D7 retention + soft-currency health guardrails; revenue per install secondary | Short-term revenue can rise while the economy inflates |
| Ad placement / frequency | Total (ads + IAP) revenue per install to D7 or D14, with D7 retention guardrail | Ad ARPDAU alone ignores retention and IAP cannibalisation |
| Pricing / offers | Revenue per install to D14/D30 (winsorised), payer conversion | ARPPU alone moves inversely with conversion |
| Live event design | Event participation and completion; DAU and revenue during the event vs holdout | |
| Notifications / CRM | Next-day return of targeted users vs holdout | Open rate is a vanity metric |

---

## 4. Power, sample size and MDE

### 4.1 Definitions

- **α (significance level)**: probability of a false positive if there is no effect; default 0.05 two-sided.
- **Power (1 − β)**: probability of detecting a true effect of size MDE; default 0.80.
- **MDE (minimum detectable effect)**: the smallest effect worth detecting; set by the business decision, not by what the traffic allows.
- **Baseline**: control's expected value of the primary metric.

### 4.2 Formulas

**Proportions** (retention, conversion), per arm:

```
n = (z_{1−α/2} + z_{1−β})² × [p₁(1 − p₁) + p₂(1 − p₂)] / (p₂ − p₁)²
z_{0.975} = 1.960, z_{0.80} = 0.842  →  (1.960 + 0.842)² ≈ 7.85
```

**Means** (revenue per install, minutes per day), per arm, equal variance σ²:

```
n = 2 × (z_{1−α/2} + z_{1−β})² × σ² / δ²    ≈ 16 σ² / δ²   (Lehr's rule of thumb, α = 0.05, power 0.8)
```

**MDE for a fixed n per arm** (proportions):

```
MDE ≈ (z_{1−α/2} + z_{1−β}) × sqrt(2 p (1 − p) / n)
```

### 4.3 Worked examples

| Primary | Baseline → target | Absolute MDE | n per arm |
|---|---|---|---|
| D1 retention | 40% → 42% | 2.0 pp (5% relative) | ≈ 9,500 |
| D1 retention | 40% → 41% | 1.0 pp | ≈ 37,800 |
| D7 retention | 15% → 16% | 1.0 pp (6.7% relative) | ≈ 20,600 |
| D7 payer conversion | 2.0% → 2.3% | 0.3 pp (15% relative) | ≈ 36,700 |
| Ad opt-in | 5.0% → 5.5% | 0.5 pp | ≈ 31,200 |

MDE available for D7 = 15% at a given traffic: n = 2,000 per arm → ±3.2 pp; 5,000 → 2.0 pp; 20,000 → 1.0 pp. Halving the MDE quadruples the sample.

To reproduce the table with the plugin script, pass the **absolute** difference to `--mde`: `ab_test.py size --baseline 0.40 --mde 0.02` prints 9,490 per arm and `--baseline 0.40 --mde 0.01` prints 37,824. A "5% relative" lift on a 40% baseline is therefore `--mde 0.02`, not `--mde 0.05` (which would size a 5-point, 12.5% relative lift: 1,531 per arm). The script's exact values differ from the rounded table figures by less than 1%.

**Revenue metrics are expensive.** Revenue per install is zero for most players and heavy-tailed for payers; its standard deviation is commonly an order of magnitude larger than its mean. Illustration: mean $0.50, σ $6.00, detect +5% ($0.025): n ≈ 16 × 36 / 0.000625 ≈ 920,000 per arm. Mitigations: test payer conversion (a proportion) as the primary and revenue as a guardrail; winsorise revenue at p99 or p99.9 of payers; use CUPED (section 9); lengthen the horizon only if traffic allows.

### 4.4 Duration

1. Sample-size days = n per arm × arms / eligible users per day (new installs for new-user tests).
2. Add the metric horizon: a D7 test needs the last enrolled cohort to age 7 days (+1 for data delay).
3. Round enrollment up to whole weeks (weekday/weekend players differ).
4. Minimum one full week even when the sample is reached sooner (day-of-week and novelty effects).

Example: D7 test, 20,600 per arm, 2 arms, 3,000 eligible new installs/day → 13.7 days → 14 days of enrollment + 8 days maturation ≈ 22 days to readout.

---

## 5. Randomisation unit, assignment and exposure

### 5.1 Unit

| Unit | Use when | Risk |
|---|---|---|
| Player (account or pseudonymous id) | Default for almost all game tests | Reinstalls and multiple devices may break stickiness if the id is per-install |
| Device / app instance | No accounts; only option pre-login | Same player on two devices may see both variants |
| Session | Only for pure presentation tests with no memory (rare in games) | Players see both variants; carry-over effects |
| Cluster (guild, server, shard, friend graph component) | Social features, PvP matchmaking, shared economies, guild events | Far fewer units → much lower power; analyse at cluster level |
| Geography / store | Pricing tests constrained by store rules, large redesigns | Weak inference (geos differ); use many geos and difference-in-differences |

### 5.2 Assignment

```python
# Deterministic, sticky, independent across experiments
import hashlib
def variant(player_id: str, experiment_id: str, salt: str, weights=(("A", 50), ("B", 50))) -> str:
    h = int(hashlib.sha256(f"{experiment_id}:{salt}:{player_id}".encode()).hexdigest()[:8], 16) % 100
    acc = 0
    for name, w in weights:
        acc += w
        if h < acc:
            return name
    return weights[-1][0]
```

- Assign at the moment of **eligibility** (first open for FTUE tests; reaching level 20 for a mid-game test), not at app start for everyone.
- Use a per-experiment salt so assignments across experiments are independent (no player is always in "B").
- Keep assignment server-side or in the remote-config tool; cache it locally so offline play is consistent.
- **Mutually exclusive layers**: experiments touching the same system (two economy tests) go in one layer with disjoint traffic; independent systems can overlap.

### 5.3 Exposure logging and triggered analysis

Log `experiment_exposure {experiment_id, variant}` once, at the moment the player first **experiences** the difference (opens the shop for a shop test, reaches level 6 for a level-6 test). Analyse only exposed players in both arms — control players must log the same "would have been exposed" moment (counterfactual logging). This removes unaffected players and increases power, often substantially for features deep in the game.

### 5.4 New vs existing players

- **New-install tests** measure the clean effect on fresh players; required for FTUE, early difficulty, and anything evaluated on D1–D30 retention.
- **Existing-player tests** are affected by habit (primacy) and novelty (section 7), and by players comparing notes in communities. Avoid visible-inequality variants (different prices for the same item seen side by side) in social games.

---

## 6. Health checks: A/A tests and sample-ratio mismatch

**A/A test.** Run the experiment system with two identical arms before trusting it. Over many A/A runs, about 5% should be "significant" at α = 0.05; more means broken randomisation, logging or analysis.

**Sample-ratio mismatch (SRM).** If the intended split is 50/50 and you observe 10,000 vs 10,600 exposed players, something is wrong (assignment bug, crash in one variant, logging lost, bots). Test with chi-square; a common alarm threshold is p < 0.001 (see Fabijan et al., *Diagnosing Sample Ratio Mismatch in Online Controlled Experiments*, KDD 2019).

```
python3 ${CLAUDE_PLUGIN_ROOT}/skills/player-analytics/scripts/analytics_calc.py srm --counts 10000,10600
→ chi2 = 17.48, df = 1, p = 2.9e-05 → SRM detected (exit code 1)
python3 .../analytics_calc.py srm --counts 10000,10400
→ chi2 = 7.84, p = 0.005 → no SRM at α = 0.001 (but investigate if it persists)
```

**An SRM invalidates the result.** Do not "correct" it by reweighting; find the cause. Typical game causes: variant B crashes on low-end devices before logging exposure; variant B's longer load causes more players to quit before exposure; assignment cached differently after reinstall; bots filtered unevenly.

---

## 7. Novelty, primacy and long-term effects

| Effect | Mechanism | Symptom | Mitigation |
|---|---|---|---|
| Novelty | Existing players engage with anything new | Treatment effect large in days 1–3, decays | Plot effect by days since exposure; read the stabilised tail; prefer new-install tests |
| Primacy (change aversion) | Existing players dislike change at first | Negative early, recovers | Same as above; run ≥ 2 weeks |
| Learning | Players learn to exploit a change (e.g. a farmable reward) | Effect grows, economy guardrails drift | Economy guardrails over the whole run; post-launch monitoring |
| Long-term vs short-term | More ads or harder walls lift revenue now, cut retention later | D1–D7 revenue up, D30 retention down | Revenue per install to a longer horizon; long-term holdback (section 11) |
| Content exhaustion | Faster progression looks great until content runs out | D7 up, D30 flat or down | Track content runway; read D30 before shipping progression speedups |

**Readout rule:** for existing-player tests, show the daily treatment effect curve; decide on the period after it stabilises.

---

## 8. Peeking and sequential testing

**The peeking problem.** Checking a fixed-horizon test repeatedly and stopping at the first p < 0.05 inflates the false-positive rate. With equally spaced looks at nominal α = 0.05 (two-sided), the real false-positive rate is approximately:

| Looks | 1 | 2 | 5 | 10 | 20 |
|---|---|---|---|---|---|
| False-positive rate | 5% | ~8% | ~14% | ~19–20% | ~25% |

(Classic result from Armitage, McPherson and Rowe, 1969; the figures above match a quick simulation of normally distributed increments.)

**Options:**

1. **Fixed horizon, no peeking.** Compute n, run to n, analyse once. Look only at health checks (SRM, crashes) during the run.
2. **Group sequential design.** Plan *K* interim looks with stricter boundaries:
   - O'Brien–Fleming (1979): very strict early, close to nominal at the end. For *K* = 5 (α = 0.05 two-sided) the z boundaries are approximately 4.56, 3.23, 2.63, 2.28, 2.04.
   - Pocock (1977): constant boundary; for *K* = 5 about 2.41 at every look (more early-stopping power, larger final threshold).
   - Lan–DeMets alpha-spending (1983) allows unplanned look timings.
   - Cost: a slightly larger maximum sample (a few percent for O'Brien–Fleming), but average sample size falls when effects are large.
   - `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ab_test.py sequential --baseline 0.15 --mde 0.01 --looks 5 --alpha 0.05 --json` (`--mde` is absolute; the default `--method obf` gives the O'Brien–Fleming boundaries above, `--method pocock` the constant 2.41; the output lists `z_boundary` and cumulative `n_per_arm` per look, plus `inflation` over the fixed-horizon sample: 1.03× for five O'Brien–Fleming looks, 1.23× for Pocock)
3. **Always-valid inference.** Mixture sequential probability ratio tests give p-values valid at any stopping time (Johari, Koomen, Pekelis and Walsh, *Peeking at A/B Tests*, KDD 2017). Useful for dashboards that people will look at anyway; less power than a fixed horizon at the same n.
4. **Bayesian monitoring.** Posterior "probability B beats A" is intuitive but not immune to optional stopping in terms of error rates; pre-specify a decision rule and a minimum sample, and check its frequentist error rates by simulation before relying on it.

**Stopping for harm** is always allowed: if a guardrail (crash rate, D1) is clearly breached, stop the variant.

---

## 9. Variance reduction: CUPED, stratification, winsorising, ratio metrics

### 9.1 CUPED

From Deng, Xu, Kohavi and Walker, *Improving the Sensitivity of Online Controlled Experiments by Utilizing Pre-Experiment Data* (WSDM 2013). Adjust each player's metric by a pre-experiment covariate *X* that is unaffected by the treatment:

```
Y_cuped = Y − θ (X − mean(X)),   θ = cov(X, Y) / var(X)    (θ pooled over both arms)
Var(Y_cuped) = Var(Y) × (1 − ρ²),  ρ = corr(X, Y)
```

| ρ | Variance reduction | Sample needed vs unadjusted |
|---|---|---|
| 0.3 | 9% | 91% |
| 0.5 | 25% | 75% |
| 0.6 | 36% | 64% |
| 0.8 | 64% | 36% |

Covariates: for existing-player tests, the same metric in the 2–4 weeks before exposure (minutes/day, spend). For new-install tests there is no pre-period; use only attributes fixed before assignment (country tier, platform, device tier, acquisition channel) — or behaviour before exposure if exposure happens well after install (e.g. day-0 activity for a test triggered at level 20).

### 9.2 Stratification and post-stratification

Balance or adjust by strong predictors (platform, country tier, payer status). Post-stratification: estimate the effect within strata and weight by stratum size; reduces variance when strata differ in the metric.

### 9.3 Winsorising and capping

Cap revenue per player at a high percentile (p99/p99.9 of payers, decided before the test) to stop one large purchase deciding the test. Report both capped (decision) and uncapped (sanity) results.

### 9.4 Ratio metrics

Metrics like ARPDAU, revenue per session or win rate per attempt are ratios of sums where the randomisation unit (player) is not the analysis unit (day, session, attempt). Naive standard errors are wrong (too small). Use the delta method or bootstrap over players (Deng et al., *Applying the Delta Method in Metric Analytics*, 2018). Simpler: convert to per-player metrics (revenue per exposed player, wins per player).

---

## 10. Multiple comparisons

Each extra metric, segment or variant is another chance of a false positive.

| Method | Controls | Use |
|---|---|---|
| Pre-registered single primary | — | Always; everything else is supporting evidence |
| Bonferroni (α/m) | Family-wise error | Few comparisons, e.g. 3 variants vs control → α = 0.0167 each |
| Holm (1979) step-down | Family-wise error, more power than Bonferroni | Multiple variants or several co-primary metrics |
| Benjamini–Hochberg (1995) | False discovery rate | Many exploratory metrics or segments; report as "candidates for follow-up" |

**Segment fishing rule:** a segment-level win found after the fact is a hypothesis for the next test, not a result.

**Many-variant tests.** Testing 5 reward amounts with equal splits divides traffic by 6 and needs corrections; prefer 2–3 well-separated variants, or a dose–response design analysed with a regression on the parameter value.

---

## 11. Holdouts and holdbacks

| Type | Design | Measures |
|---|---|---|
| Global holdout | A small random share of new players (commonly 1–5%) excluded from all new features and live-ops changes for a quarter | Cumulative impact of a roadmap; whether "every test won" actually added up |
| Feature holdback | After shipping a winner, keep 5–10% on the old experience for weeks or months | Long-term effect, novelty decay, cannibalisation |
| CRM / push holdout | Random 5–20% of each targeted segment receives no message | Incremental return and revenue from a campaign; without it, "opens" credit the push for players who would have returned anyway |
| Live-event holdout | A random share of players not shown an event (where fair and feasible) | Event uplift vs cannibalisation of normal play and revenue |

Ethics and fairness: holdouts must not deny players fixes, safety features or anything paid for; avoid holdouts that create visible unfairness in competitive or social contexts.

---

## 12. Multi-armed bandits

Bandits shift traffic toward better-performing arms during the run, trading inference quality for less regret.

| Use bandits for | Avoid bandits for |
|---|---|
| Short-lived decisions with fast feedback: which event banner, which store-tile order this weekend, which push copy | Long-horizon outcomes (D7 retention, LTV): the feedback arrives after the decision window |
| Many creative variants where you want the best quickly, not a precise effect size | Decisions where you need an unbiased effect estimate or must prove no harm |
| Ongoing optimisation that never "ends" (e.g. ordering of daily offers) | Anything with guardrail metrics that need a clean comparison |

Default algorithm: **Thompson sampling** (Thompson, 1933) with Beta priors for conversion-type rewards; keep a minimum exploration share (e.g. 5–10% per arm) to detect drift. Contextual bandits that personalise offers by player features belong under the ethics rules in `monetization` and `legal-ethics` (no targeting of vulnerable players, transparent pricing).

---

## 13. Remote config: the experiment substrate

Every tunable that might be tested should be a remote-config parameter with a safe in-build default.

### 13.1 What to parametrise

| System | Example keys |
|---|---|
| Difficulty | `level_moves_delta[level_id]`, `dda_enabled`, `dda_max_step`, `boss_hp_mult` |
| Economy | `reward_win_coins`, `daily_chest_coins`, `booster_price_hammer`, `meta_build_cost_mult` |
| Ads | `inter_first_after_sec`, `inter_min_interval_sec`, `rv_double_coins_enabled`, `rv_daily_cap` |
| Offers | `starter_pack_sku`, `starter_pack_show_after_level`, `store_tile_order` |
| FTUE | `ftue_variant`, `ftue_skip_allowed`, `notif_prompt_after_level` |
| Live-ops | `event_schedule`, `event_target_points`, `event_reward_table_id` |
| Safety | `kill_switch_<feature>`, `min_supported_build`, `maintenance_mode` |

### 13.2 Rules

1. **Defaults in the build** equal the current shipped values; the game must run correctly offline and when the fetch fails.
2. **Typed schema** for config (JSON with version and validation) — reject malformed values client-side and fall back to defaults.
3. **Fetch at startup, activate at a safe point** (next session or next menu), never mid-level; values must not change during a level or purchase flow.
4. **Log active values** that matter (or the config version) so analysis knows what each player actually had.
5. **Staged rollout**: 1% → 10% → 50% → 100% with guardrail checks between steps.
6. **Kill switches** for every new feature and every ad placement.
7. **Change log**: every config publish recorded with author, time, reason and linked experiment; roll back from the log. Firebase Remote Config templates can be listed, published and rolled back via the official Firebase MCP server, which makes agent-driven changes auditable (volatile section).
8. **Human checkpoint** for production config changes that affect monetization or difficulty for all players (doctrine: automatic between taste checkpoints).

### 13.3 Tooling options

Firebase Remote Config + A/B Testing (no-cost; integrates with Analytics audiences), Unity Remote Config / Game Overrides in Unity Gaming Services, Heroic Labs Satori (live-ops: audiences, experiments, feature flags; paid), or a custom config service. For high-stakes decisions, export assignments and outcomes (e.g. to BigQuery) and run your own readout with this file's methods rather than relying solely on a vendor dashboard.

---

## 14. Game-specific pitfalls

| Pitfall | Why it happens in games | Guard |
|---|---|---|
| **Shared-economy interference** | Trading, auction houses, gifting, guild resources leak treatment effects into control | Cluster randomisation by server/guild, or test only non-tradeable resources |
| **Competitive interference** | A variant that makes some players stronger changes opponents' experience in PvP/leaderboards | Exclude PvP-affecting changes from player-level tests; use matchmaking pools per variant or cluster tests |
| **Difficulty × monetization coupling** | Harder levels sell more boosters short term and lose players long term | Primary = retention; revenue to a long horizon; ethics review if difficulty is tuned for sales |
| **Ad frequency cannibalisation** | More interstitials raise ad revenue but cut sessions and IAP | Total revenue per install to D14+ with D7 guardrail |
| **Price testing** | Store price tiers, player comparison in communities, and consumer-protection rules on personalised pricing | Prefer testing bundle contents/value at the same price, or geo tests; route price personalisation through `legal-ethics` |
| **Soft-launch drift** | UA mix changes weekly in soft launch; a test spanning a UA change confounds nothing (randomised) but changes the population | Report by acquisition channel; avoid launching tests during big UA shifts |
| **Builds and platforms** | Variant behaviour differs by platform or build; store review delays iOS | Stratify by platform; require both platforms on the same build before enrolling |
| **Live events overlapping** | An event changes behaviour in both arms differently (e.g. variant changes reward economy) | Avoid tests that interact with the event's systems; annotate event periods |
| **Engagement vs well-being** | Metrics can reward compulsion | Guardrails on session counts at night for minors where known, spending velocity, complaint rates; reflective-endorsement check (see `design-theory`) |

---

## 15. Analysis procedure and readout template

**Procedure:**

1. Confirm the run matched the plan: dates, eligibility, split, exposure definition, metric horizon matured.
2. Health: SRM test on exposed players (and on assigned players); event volume per player by arm; crash and error rates by arm.
3. Primary metric: effect (absolute and relative), 95% confidence interval, p-value (fixed horizon) or boundary crossing (sequential). Use CUPED/post-stratification if pre-registered.
4. Guardrails: each with its tolerance; any breach → no ship regardless of primary.
5. Secondary metrics: mechanism checks (did players see and use the change?).
6. Pre-registered segments only (platform, new vs existing, country tier); others labelled exploratory.
7. Time profile: effect by day since exposure (novelty/primacy).
8. Decision per the pre-written rule; record it.

**Readout template** (store as `.gamestudio/reports/exp-<id>.md`):

```markdown
# Experiment <id>: <name>
- Hypothesis: <filled template>
- Population / unit / split: new installs, player id, 50/50; exposure = <event>
- Dates: enrollment <start>–<end>; metric horizon D7; readout <date>
- Sample: A n=… exposed; B n=… exposed; SRM p=… (pass/fail)
- Primary (D7 retention): A 15.1% vs B 16.3%; +1.2 pp (95% CI +0.5 to +1.9); p≈0.001
- Guardrails: D1 (±0.5 pp tolerance) +0.3 pp ✓; crash-free users −0.02 pp ✓; IAP rev/install D7 −1% (CI −6% to +4%) ✓
- Secondary: level-6 win rate 39% → 55%; levels/day +6%
- Segments (pre-registered): iOS +1.4 pp, Android +1.0 pp (no significant interaction)
- Time profile: stable from day 3 of enrollment
- Decision: SHIP B to 100% via remote config; keep 5% holdback for 4 weeks
- Follow-ups: test +1 move on levels 9–10; recalibrate bots with new data
```

---

## 16. Tool usage

The plugin's `ab_test.py` (owned by the core scripts) and this skill's `analytics_calc.py`:

```bash
# Sample size for a proportion (D7 15% → 16%). --mde is an ABSOLUTE difference (0.01 = +1 pp), not a relative lift.
# Prints n_per_arm = 20557 and n_total = 41114; --two-sided is the default and is accepted for explicitness.
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ab_test.py size --baseline 0.15 --mde 0.01 --alpha 0.05 --power 0.8 --two-sided

# Analyse a finished proportion test
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ab_test.py analyze --a-success 3020 --a-n 20000 --b-success 3260 --b-n 20000 --json

# Analyse a mean metric (e.g. winsorised revenue per install)
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ab_test.py mean --a-mean 0.48 --a-sd 3.1 --a-n 40000 --b-mean 0.52 --b-sd 3.3 --b-n 40000 --json

# Group-sequential boundaries for 5 planned looks
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ab_test.py sequential --baseline 0.15 --mde 0.01 --looks 5 --alpha 0.05 --json

# Sample-ratio mismatch check (exit 1 on mismatch)
python3 ${CLAUDE_PLUGIN_ROOT}/skills/player-analytics/scripts/analytics_calc.py srm --counts 20113,19887

# Confidence interval for one arm's rate
python3 ${CLAUDE_PLUGIN_ROOT}/skills/player-analytics/scripts/analytics_calc.py ci --success 3260 --n 20000
```

Worked check of the `analyze` example: A = 15.1%, B = 16.3%, difference 1.2 pp; pooled p = 15.7%, SE = sqrt(0.157 × 0.843 × (2/20,000)) ≈ 0.364 pp; z ≈ 3.3; p ≈ 0.001. A significant win at the planned sample — provided SRM and guardrails pass.

---

## 17. Volatile facts (as of Oct 2026 — verify before relying)

- Firebase Remote Config, A/B Testing, Analytics and Crashlytics are no-cost Firebase products (background). — [Firebase pricing](https://firebase.google.com/pricing)
- The official Firebase MCP server (run via `firebase-tools`) can get, publish and roll back Remote Config templates and read Crashlytics issues from Claude Code. — [Firebase MCP docs](https://firebase.google.com/docs/ai-assistance/mcp-server)
- Firebase Remote Config's default minimum fetch interval in production has been 12 hours, with real-time update listeners available in current SDKs; background knowledge, not re-verified this session. — [Remote Config docs](https://firebase.google.com/docs/remote-config)
- Heroic Labs Satori (live-ops audiences, experiments, feature flags) is listed from $1,800/month including 25M events, plus $0.018 per 1,000 events; a third-party aggregator shows a conflicting lower figure. — [Heroic Labs pricing](https://heroiclabs.com/pricing)
- RevenueCat's hosted MCP exposes experiment results and paywall/offering configuration for IAP tests. — [RevenueCat MCP docs](https://www.revenuecat.com/docs/tools/mcp)
- Unity LevelPlay ended waterfall-only support for Unity Ads in January 2026 (bidding is the standard path) — relevant when testing ad setups. — [Segwise AppLovin guide](https://segwise.ai/blog/applovin-publisher-monetization-guide)
