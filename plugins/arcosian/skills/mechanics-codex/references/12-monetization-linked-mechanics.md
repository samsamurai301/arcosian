# 12 — Monetization-Linked Mechanics

Monetization-linked mechanics are the points where game rules and money touch: an ad that buys a second chance, a booster that buys a win, a timer that can be skipped, a pass that pays out over a season, a random pull. Designed well, they sell time, convenience, expression and generosity to players who want them while the free game stays complete. Designed badly, they become dark patterns, consumer-law exposure, store rejections and a reputation problem. This file catalogues 20 mechanics in the shared mechanic-card format — rewarded revives, reward doubling, ad-funded spins, rewarded unlocks, interstitial cadence with Remove Ads, paid boosters, continues, timer skips, refills, starter packs, triggered and chain offers, piggy banks, currency stores, cosmetic shops, web shops, VIP tiers, premium passes, subscriptions, offer walls and paid randomized rewards. Every entry carries its **ethical limit** and **regulatory notes** in addition to rules, tuning, dynamics, failure modes, mobile fit and an implementation sketch. Rules from stores and regulators change often: anything dated or numeric is collected in the volatile-facts section at the end with sources. Strategy, pricing and offer operations belong to `monetization`; legal analysis to `legal-ethics`; the underlying systems to files 04 (economy), 05 (progression), 07 (randomness) and 08 (time and energy).

**Entry format.** Every entry maps onto `${CLAUDE_PLUGIN_ROOT}/scripts/schemas/mechanic-card.schema.json`; the extra **Regulatory notes** field belongs in the card's `failure_modes` or in `contract.json → monetization.ethics`. Ids are kebab-case; sibling ids carry their file number, e.g. `pity-timers` (07). MDA aesthetics as in Hunicke, LeBlanc and Zubek (2004). Tuning ranges are practitioner starting points, not market benchmarks. Nothing here is legal advice; route launch decisions through `compliance-officer` and `compliance_preflight.py`.

## Contents

1. Index · 2. Ethics baseline · 3. Regulatory map · 4. Ad mechanics (12.01–12.05) · 5. Progress accelerators (12.06–12.09) · 6. Offers and stores (12.10–12.15) · 7. Recurring value (12.16–12.18) · 8. High-risk mechanics (12.19–12.20) · 9. Volatile facts with sources, related skills

## 1. Index

| # | Id | Mechanic | Revenue | Main ethical risk |
|---|---|---|---|---|
| 12.01 | `rewarded-revive` | Rewarded revive | rewarded ads | difficulty tuned to force revives |
| 12.02 | `rewarded-double` | Rewarded reward doubling | rewarded ads | base rewards nerfed so declining feels like a loss |
| 12.03 | `rewarded-free-spin` | Ad-funded free spin | rewarded ads | casino framing, rigged near-misses |
| 12.04 | `rewarded-unlock` | Rewarded unlocks and trials | rewarded ads | progress that resets if not finished |
| 12.05 | `interstitial-cadence` | Interstitial cadence and Remove Ads | forced ads, IAP | accidental taps, ads mid-play |
| 12.06 | `paid-boosters` | Paid boosters | IAP | levels that require boosters |
| 12.07 | `continues` | Continues (+moves, +time) | IAP | manufactured near-misses, escalation |
| 12.08 | `timer-skips` | Timer skips | IAP, ads | timers that exist only to sell skips |
| 12.09 | `refill-offers` | Lives and energy refills | IAP, ads | first-session walls, hidden free option |
| 12.10 | `starter-pack` | Starter packs | IAP | fake timers and fake reference prices |
| 12.11 | `triggered-offers` | Triggered and chain offers | IAP | targeting frustration or vulnerability |
| 12.12 | `piggy-bank` | Piggy bank | IAP | "you'll lose it" pressure |
| 12.13 | `currency-store` | Hard-currency store and first-purchase bonus | IAP | engineered leftover currency |
| 12.14 | `cosmetic-shop` | Cosmetic shop | IAP | rotation FOMO, child purchases |
| 12.15 | `web-shop` | Web shop (direct-to-consumer) | IAP (web) | jurisdiction and minor-protection gaps |
| 12.16 | `vip-tiers` | VIP tiers | IAP | status pressure, pay-to-win perks |
| 12.17 | `premium-pass` | Premium pass | IAP | grind-or-pay pacing |
| 12.18 | `subscription-perks` | Subscription perks | subscription | hard cancellation, unclear renewal |
| 12.19 | `offer-wall` | Offer walls | incentivized ads | hidden costs in third-party offers |
| 12.20 | `paid-random-rewards` | Paid randomized rewards (compliance layer) | IAP | gambling-like harm, minors, law |

## 2. Ethics baseline (applies to every entry)

These follow the plugin doctrine ("ethical monetization: no dark patterns, transparent odds, respect for minors") and should be copied into `contract.json → monetization.ethics`:

1. **The free game is complete.** Every level is beatable without paying at the contract's target win rates, verified by bots with all paid aids off.
2. **Decline is as easy as accept.** Equal-size "no thanks", no hidden close buttons, no countdowns shorter than about 5 s on a decision, no pre-selected paid options.
3. **Prices are honest.** Real-money equivalents near premium-currency prices; no invented "was" prices; no timers that reset.
4. **Randomness is disclosed and capped.** Per-item odds before purchase; hard pity or exchange ceilings; a deterministic path to every core item.
5. **Minors get a different game.** Age-band flags disable personalised ads, paid random items, urgency offers, chat-linked purchases and link-outs where rules require.
6. **No targeting of distress.** Offers never key on frustration streaks with escalating pressure, late-night bingeing or detected vulnerability; spending limits and reminders are available.
7. **Ads never ambush.** No ads mid-level or where the next game tap lands; rewarded ads are always the player's choice.
8. **Everything bought is kept.** Purchased currency never expires; non-consumables restore; event or overflow rewards are never silently lost.

## 3. Regulatory map

| Rule (summary) | Where it applies | Mechanics affected |
|---|---|---|
| Disclose odds of randomized paid items before purchase | Apple App Store, Google Play | 12.03 (if spins can be bought), 12.19, 12.20, paid eggs/chests in file 09 |
| Purchased in-game currency may not expire; restorable purchases need a restore mechanism | Apple App Store | 12.05, 12.12, 12.13, 12.17 |
| Pricing and terms must be clear and match the billing UI; promoting a false price is grounds for removal | Google Play; Apple App Store | 12.06–12.14 |
| Auto-renewing subscriptions: ongoing value, ≥ 7-day period, all of the user's devices, describe before subscribing | Apple App Store | 12.17, 12.18 |
| Full-screen ads must not appear unexpectedly or at the start of a level; must be closable after 15 s; opt-in rewarded ads are exempt | Google Play | 12.01–12.05 |
| No third-party ads or analytics in Kids Category apps (narrow exceptions) | Apple App Store | all ad mechanics |
| Verifiable parental consent before sharing children's data with third parties (e.g., targeted ads) | US (COPPA) | ad mechanics, 12.11, 12.19 |
| Paid loot boxes banned / banned for under-18s / classification M or R18+ | Belgium / Brazil / Australia | 12.03, 12.20 |
| Link-outs and alternative payments: allowed with conditions that differ by country and age | US, EU (Apple, Google) | 12.15 |

Dates, fees and case status are in section 9. The jurisdiction-by-jurisdiction matrix whose status is actively maintained (China, Japan, South Korea, the EU CPC principles and others) is `${CLAUDE_PLUGIN_ROOT}/skills/legal-ethics/references/privacy-children-gambling.md`, section 10.

## 4. Ad mechanics

### 12.01 Rewarded revive — `rewarded-revive`

- **Category:** ads · rewarded continue
- **Player fantasy:** "One more chance — I was so close."
- **Core rules:**
  - *State:* run frozen at the fail moment; revives used this run; ad availability.
  - *Triggers:* fail event (death, out of moves or time) while eligible (progress ≥ threshold, revives left).
  - *Effects:* offer with a plain decline; on the ad network's completed-reward callback, restore from the checkpoint with brief invulnerability or +N moves; decline or ad failure goes straight to results.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Eligibility | ≥ 30–50 % of goal, or near personal best | Offering on hopeless runs wastes the player's time |
| Ad revives per run | 1 (a second only for currency, or none) | More turns the run into an ad loop |
| Post-revive grace | 1–2 s invulnerability, or +3–5 moves | Too little and the revive feels fake |
| Decision time | no timer, or ≥ 5 s with an equal-size decline | Short countdowns are pressure tactics |

- **Dynamics:** rescues near-miss runs; lengthens sessions; often a high-engagement rewarded placement in arcade games.
- **Aesthetic targets (MDA):** Challenge (sustained tension), Submission.
- **Feedback and juice:** freeze-frame with desaturation; heartbeat sound; revive burst VFX.
- **Failure modes and exploits:** difficulty silently tuned assuming revives; reward granted before ad completion (client tampering — use server-side reward verification where the economy matters); dead "revive" button when no ad loads.
- **Mobile fit:** native to short arcade sessions.
- **Monetization hooks and the ethical limit:** ad revenue per run. Tune and verify difficulty with revives off; hide the offer when no ad is ready; never show to child audiences with personalised ads.
- **Regulatory notes:** Google Play exempts only explicitly opted-in rewarded ads from its full-screen ad restrictions, so the revive must be a choice. Child-directed apps face COPPA and store family-policy limits on ad SDKs and personalisation; Apple's Kids Category bars third-party ads.
- **Implementation notes:**

```text
on_fail(run): if run.ad_revives == 0 and progress(run) >= ELIGIBLE and ads.ready("revive"): show_offer()
on_reward(placement="revive", verified): restore(run.checkpoint); grant_iframes(1.5); run.ad_revives += 1
on_ad_unavailable(): hide_offer(); to_results()
```
- **Reference games:** Subway Surfers (continue with keys or an ad), Temple Run 2 ("save me").
- **Combines well with:** `continues`, `rewarded-double`, `lives` (08).

### 12.02 Rewarded reward doubling — `rewarded-double`

- **Category:** ads · reward multiplier
- **Player fantasy:** "I can make this win even sweeter."
- **Core rules:**
  - *State:* pending reward; daily cap counter; ad availability.
  - *Triggers:* results screen, chest claim, offline-earnings summary.
  - *Effects:* "claim ×1" always available; "claim ×2" (or a multiplier needle ×2–×5) after a completed ad.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Multiplier | fixed ×2, or needle ×2–×5 | Needles add excitement; they must be honest about skill vs chance |
| Daily cap | 5–15 per placement | Limits inflation and ad fatigue |
| Base reward share | base alone covers normal pacing | If base is starved, declining feels punitive |
| Placement count | 1–3 placements | More placements dilute value per view |

- **Dynamics:** high opt-in; ad-accepting players progress faster; inflation if sinks ignore doubled income.
- **Aesthetic targets (MDA):** Submission, Sensation.
- **Feedback and juice:** coins counting up twice; needle sweep with ticks.
- **Failure modes and exploits:** economy tuned on base income only (doubled players flood); base rewards cut to make doubling feel mandatory; a "timing" needle that is actually random.
- **Mobile fit:** excellent; seconds per decision.
- **Monetization hooks and the ethical limit:** ad revenue on every win. Equal-prominence ×1 claim; economy simulated with ad acceptance; label random needles as random.
- **Regulatory notes:** opt-in requirement as for 12.01. If a paid currency can boost the needle, it becomes a paid random item — disclose odds.
- **Implementation notes:** model as an `on_ad` source node with `probability = ad_accept_rate` per archetype and run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/economy_sim.py --model econ.json --json`.

```text
results(level): base = reward(level)
  show(claim=base, ad_claim=(base * MULT if ads.ready("double") and caps.ok("double") else None))
```
- **Reference games:** AdVenture Capitalist (ad-boosted profits), many hybrid-casual titles (end-of-level multiplier needles).
- **Combines well with:** `rewarded-free-spin`, `idle-input` (11), `offline-progress` (08).

### 12.03 Ad-funded free spin — `rewarded-free-spin`

- **Category:** ads · prize wheel (wheel design: `prize-wheel` (07))
- **Player fantasy:** "A daily gift — and maybe today's the jackpot."
- **Core rules:**
  - *State:* daily free spin flag; ad-spin counter; outcome table with weights.
  - *Triggers:* daily reset; player taps spin (free) or watches an ad (extra spin).
  - *Effects:* the server picks the outcome by weight; the wheel animation lands on that pre-chosen segment.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Spins | 1 free per day + 1–5 ad spins | Daily habit without fatigue |
| Jackpot weight | 1–2 % | Rare but real |
| Expected value | ≈ one small daily reward | Too high inflates; too low feels stingy |
| Pity | mid-tier guaranteed every k spins | Smooths streaks of duds |

- **Dynamics:** daily return habit; ad views; light excitement.
- **Aesthetic targets (MDA):** Sensation, Submission.
- **Feedback and juice:** ticking pointer, slowdown, celebratory burst.
- **Failure modes and exploits:** rigged near-misses (stopping just past the jackpot by design); slot-machine framing in games for children; adding paid re-spins.
- **Mobile fit:** five-second interaction.
- **Monetization hooks and the ethical limit:** ad views. Segment sizes or a visible odds list must match real probabilities; no engineered near-misses; no paid re-spins for minors; avoid casino aesthetics for young audiences.
- **Regulatory notes:** if spins can be bought with money or premium currency, the wheel is a paid randomized item (odds disclosure on both stores; Belgian and Brazilian rules). Australia classifies paid chance items at M and simulated gambling at R18+ — a casino-styled wheel risks the stricter category; check classification guidance.
- **Implementation notes:**

```text
spin(p, kind): require (kind == "free" and not p.spun_today) or (kind == "ad" and ad_verified() and p.ad_spins < CAP)
  out = weighted_pick(WHEEL, rng=server_rng); animate_to(segment_of(out)); grant(p, out); audit_log(p.id, out)
```
- **Reference games:** Candy Crush Saga (Daily Booster Wheel); Coin Master (spins as the core loop — a contrast case where spins are also sold).
- **Combines well with:** `prize-wheel` (07), `login-calendar` (05), `rewarded-double`.

### 12.04 Rewarded unlocks and trials — `rewarded-unlock`

- **Category:** ads · access for attention
- **Player fantasy:** "I can try the cool thing right now, without paying."
- **Core rules:**
  - *State:* per-item ad progress; trial entitlements with expiry.
  - *Triggers:* player chooses to watch an ad for a trial or for progress toward a permanent unlock.
  - *Effects:* trial (one run, or 24 h) or +1 toward N views for a permanent unlock; progress persists.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Views per permanent unlock | 2–5 | More = grind; fewer devalues IAP |
| Trial length | 1 run to 24 h | Long enough to feel the item |
| Daily cap | 5–10 views | Limits fatigue |
| Ad-unlockable share | cosmetics and side content, not core progression | Core gates by ads alone feel coercive |

- **Dynamics:** trials convert to purchases; ads act as a currency for non-payers.
- **Aesthetic targets (MDA):** Expression, Discovery.
- **Feedback and juice:** "2 / 3 watched" progress ring on the item; try-on preview.
- **Failure modes and exploits:** progress that resets if not finished in a window; ad failures consuming progress; core content gated only by ads.
- **Mobile fit:** excellent for hybrid-casual skin systems.
- **Monetization hooks and the ethical limit:** ad views and trial-to-purchase conversion. Progress never resets; always show views remaining; offer a play-based alternative for anything beyond cosmetics.
- **Regulatory notes:** Apple's 3.2.2(x) bars forcing store actions such as rating or downloading other apps (not ad viewing); Play's opt-in rewarded exemption applies; no personalised ads for children.
- **Implementation notes:**

```text
on_reward("unlock_progress", item, verified): p.ad_progress[item] += 1
  if p.ad_progress[item] >= VIEWS_NEEDED[item]: unlock(p, item); analytics("ad_unlock", item)
```
- **Reference games:** Crossy Road (coins from video ads feed character unlocks), hybrid-casual skin-unlock-by-ads patterns.
- **Combines well with:** `cosmetic-shop`, `rewarded-double`, `starter-pack`.

### 12.05 Interstitial cadence and Remove Ads — `interstitial-cadence`

- **Category:** ads · forced-ad pacing with a paid opt-out
- **Player fantasy:** none — interstitials are a cost; the purchasable fantasy is "Remove Ads: I bought peace and quiet."
- **Core rules:**
  - *State:* `contract.json → monetization.ads.interstitial {min_interval_sec, first_after_sec}`; last ad time; session counters; `remove_ads` entitlement.
  - *Triggers:* natural breaks only (level end → before next level, returning to the map).
  - *Effects:* show if all gates pass; after close, a short input guard; Remove Ads (a non-consumable) removes interstitials and banners but keeps opt-in rewarded ads available.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| `first_after_sec` / first level | 120–300 s, or after level 3–5; none in the first session is safer | Protects the first impression and D1 |
| `min_interval_sec` | 60–180 s | Lower = revenue now, churn later |
| Rewarded grace | skip interstitials for 2–5 min after a rewarded view | Rewards players who chose ads |
| Post-close input guard | 500–1,000 ms | Prevents accidental taps on the next screen |

- **Dynamics:** revenue from non-payers; churn and bad reviews when frequency is high; Remove Ads is commonly a top IAP in ad-led casual games.
- **Aesthetic targets (MDA):** none positive — minimise damage to the game's own aesthetics.
- **Feedback and juice:** "ad in 3…" pre-roll notice is optional; a thank-you after Remove Ads; banners never overlap controls.
- **Failure modes and exploits:** ads at app open or mid-level; ads appearing under the player's next tap (accidental clicks, also an ad-fraud signal); Remove Ads that also removes wanted rewarded ads; purchases that do not restore.
- **Mobile fit:** acceptable only at natural breaks in sessions of 1–5 minutes.
- **Monetization hooks and the ethical limit:** ad revenue and the Remove Ads IAP. Never place an interstitial where the next game tap lands; describe exactly what Remove Ads removes.
- **Regulatory notes:** Google Play prohibits unexpected full-screen ads, ads at the start of a level during gameplay, interstitials not closable after 15 s, and video interstitials before the loading screen. Apple requires a restore mechanism for restorable purchases such as Remove Ads; Kids Category apps cannot show third-party ads.
- **Implementation notes:**

```text
can_show(now) = (not p.remove_ads and at_natural_break() and now - session_start >= FIRST_AFTER
                 and now - p.last_ad >= MIN_INTERVAL and now - p.last_rewarded >= REWARDED_GRACE and p.ads_today < CAP)
on_close(): input_guard(GUARD_MS)
```
- **Reference games:** Helix Jump, Words With Friends (ad-free purchase), most hyper-casual titles.
- **Combines well with:** `rewarded-revive`, `subscription-perks` (ad-free tier), `tap-anywhere` (11).

## 5. Progress accelerators

### 12.06 Paid boosters — `paid-boosters`

- **Category:** IAP · consumable help (booster design and economy: `boosters` (04))
- **Player fantasy:** "A little help to beat this level my way."
- **Core rules:**
  - *State:* booster inventory by type (pre-level, in-level); free booster sources; price in premium currency.
  - *Triggers:* level start (pre-level picker), mid-level use, offer after repeated fails.
  - *Effects:* booster applied (start with special pieces, hammer, shuffle, extra time); purchase adds inventory.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Free booster drip | ≈ 1 per 3–5 levels from rewards, events, calendars | Players learn boosters' value before being asked to pay |
| Win-rate lift per booster | measure per level with bots | Know what you are selling; don't guess |
| Fail-offer threshold | after 2–3 fails on the same level | Earlier offers feel predatory |
| Bundle price | priced through premium currency packs | Show the real-money value |

- **Dynamics:** spending concentrates at difficulty spikes; hoarding by careful players.
- **Aesthetic targets (MDA):** Challenge (made achievable), Sensation (big booster effects).
- **Feedback and juice:** spectacular booster activations; post-level "booster helped" recap.
- **Failure modes and exploits:** levels tuned so boosters are effectively required; unclear booster effects; pre-level picker defaulting to paid boosters.
- **Mobile fit:** native to casual puzzle loops.
- **Monetization hooks and the ethical limit:** consumable sales at friction points. Every level beatable at target win rates without boosters (bot-verified with `match3_sim.py --level PATH --bot greedy --json` or the template's bot runner); free sources always exist; never pre-select paid boosters.
- **Regulatory notes:** prices and contents must be stated clearly and match the store billing UI (Google Play Payments policy); EU consumer authorities have pushed for real-money price visibility for virtual-currency purchases (see section 9).
- **Implementation notes:** booster effects as data; measure the lift so offers can state it honestly.

```text
lift(level, booster) = winrate(bot_runs(level, boosters=[booster])) - winrate(bot_runs(level, boosters=[]))
offer_after_fail(p, level): if p.fails[level] >= FAIL_OFFER_AT and offers.ok(p): show(booster_bundle(level))
```
- **Reference games:** Candy Crush Saga, Royal Match, Toon Blast, Homescapes.
- **Combines well with:** `continues`, `triggered-offers`, `boosters` (04), `level-limits` (08).

### 12.07 Continues (+moves, +time) — `continues`

- **Category:** IAP · pay to extend an attempt
- **Player fantasy:** "So close — let me finish it."
- **Core rules:**
  - *State:* attempt state at fail; continues used; price ladder.
  - *Triggers:* out of moves or time with the goal unmet.
  - *Effects:* offer +N moves or seconds for premium currency; price escalates per consecutive continue in the same attempt; "give up" ends the attempt (and usually costs a life).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Extension | +5 moves or +15–30 s | Must make success plausible, not certain |
| Price escalation | ×1.5–2 per repeat | Escalation exploits sunk cost if uncapped |
| Max continues per attempt | 3–5 | Caps loss-chasing |
| Offer condition | goal not met; remaining goal shown honestly | Players must judge the real odds |

- **Dynamics:** sunk-cost escalation; a major revenue line in casual puzzle games.
- **Aesthetic targets (MDA):** Challenge.
- **Feedback and juice:** remaining-goal display ("2 jellies left"); calm, non-flashing offer panel.
- **Failure modes and exploits:** board RNG conditioned to manufacture near-misses before the offer; uncapped escalation; the "continue" button placed where "retry" was.
- **Mobile fit:** native.
- **Monetization hooks and the ethical limit:** high-intent purchases. Cap continues; never let monetization state influence board RNG (audit test); equal-prominence "give up"; consider disabling continue offers for declared minors.
- **Regulatory notes:** the FTC's 2022 settlement with Epic Games included refunds over purchase flows the FTC alleged caused unintended charges — button placement, confirmation and easy undo matter (see section 9).
- **Implementation notes:**

```text
on_fail(a): if a.continues < MAX_CONT: offer(price=BASE * ESC ** a.continues, moves=EXTRA, show_remaining=remaining_goal(a))
test_rng_independence(): assert board_seed(level, attempt) does not read p.spend_tier, p.continues or offer state
```
- **Reference games:** Candy Crush Saga (+5 moves), Royal Match, Gardenscapes.
- **Combines well with:** `paid-boosters`, `rewarded-revive`, `lives` (08).

### 12.08 Timer skips — `timer-skips`

- **Category:** IAP and ads · time-to-money conversion (timer design: `build-timers-and-skips` (08))
- **Player fantasy:** "I want it now."
- **Core rules:**
  - *State:* remaining time on a job; skip price function; ad-skip counter; guild help count.
  - *Triggers:* player taps "finish now" (premium currency), "watch ad" (fixed time off) or receives help.
  - *Effects:* timer completes or shortens; a free finish applies below a threshold.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Price curve | gems = ceil(a · minutes^b), b 0.6–0.9 | b < 1 makes long skips cheaper per minute |
| Ad skip | −15 to −30 min per view, capped per day | Lets non-payers trade attention for time |
| Free-finish threshold | last 3–5 min free | Removes trivial waits |
| Large-spend confirm | above ~10 % of a typical balance | Prevents accidental big spends |

  Worked example (a = 1, b = 0.8): 10 min → 7 gems; 1 h → 27 gems; 24 h → 336 gems. Cost per minute falls from 0.7 to 0.23, so whales skip long timers and casual payers skip short ones.
- **Dynamics:** impatience monetization; appointment play for non-payers.
- **Aesthetic targets (MDA):** Submission.
- **Feedback and juice:** timer bar drain animation on skip; builder cheer.
- **Failure modes and exploits:** timers in the first session placed only to sell skips; skip costs with no real-money reference; device clock manipulation.
- **Mobile fit:** native to base builders and farms.
- **Monetization hooks and the ethical limit:** steady spend. Keep early timers short; show real-money value near skip buttons; confirm large spends.
- **Regulatory notes:** clear pricing obligations (Google Play Payments policy); EU consumer guidance on virtual currencies (section 9).
- **Implementation notes:** server-authoritative timers; price computed server-side from remaining time at the moment of purchase.

```text
skip_cost(rem_min) = 0 if rem_min <= FREE_MIN else ceil(A * rem_min ** B)
finish_now(p, job): c = skip_cost(remaining(job)); if c > CONFIRM_AT: require confirm(c, real_money_equiv(c)); spend(p, c); complete(job)
```
- **Reference games:** Clash of Clans, Hay Day, Township, Rise of Kingdoms.
- **Combines well with:** `hq-gated-building` (09), `refill-offers`, `subscription-perks`.

### 12.09 Lives and energy refills — `refill-offers`

- **Category:** IAP and ads · session extension (systems: `lives`, `energy-stamina` (08))
- **Player fantasy:** "Let me keep playing right now."
- **Core rules:**
  - *State:* lives or energy pool with regeneration; refill options; unlimited-lives timers.
  - *Triggers:* pool empty when the player tries to play.
  - *Effects:* option list, free option first — wait (timer shown), ask friends, watch an ad for a chunk (capped), refill with premium currency, or time-boxed unlimited lives.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| First empty pool | never in the first session | Energy walls on day 0 crush D1 |
| Ad refill | 1 life or 10–30 % of energy, 2–5 per day | Non-payer path |
| Unlimited lives | 30–120 min in bundles, real-time | Strong bundle sweetener; say it runs in real time |
| Refill prompts | ≤ 1 per session | More reads as nagging |

- **Dynamics:** session caps create return cadence; purchase at peak engagement.
- **Aesthetic targets (MDA):** Submission.
- **Feedback and juice:** heart refill animation; friend gift arrivals.
- **Failure modes and exploits:** refill popup that hides the free wait timer; repeated prompts; unlimited-lives timers expiring while the app is closed without warning.
- **Mobile fit:** native.
- **Monetization hooks and the ethical limit:** refills and bundles. Show the free option first and clearly; cap prompts; no first-session wall.
- **Regulatory notes:** pricing clarity; for child-directed apps, ad refills follow COPPA and family-policy ad rules.
- **Implementation notes:** regeneration computed from timestamps (file 08); offer list ordered free → ad → paid.

```text
on_empty(p): options = [Wait(time_to_next(p)), AskFriends(), (AdRefill() if ads.ready() and p.ad_refills < CAP else None), BuyRefill(price)]
  show([o for o in options if o])        # order fixed: free first
```
- **Reference games:** Candy Crush Saga (lives, unlimited-lives boosters), Royal Match, Merge Mansion (energy).
- **Combines well with:** `continues`, `triggered-offers`, `lives` (08), `energy-stamina` (08).

## 6. Offers and stores

### 12.10 Starter packs — `starter-pack`

- **Category:** IAP · first-purchase conversion
- **Player fantasy:** "A great deal to get me going."
- **Core rules:**
  - *State:* one-time entitlement; trigger conditions; availability window (if any).
  - *Triggers:* after the player has felt the core value (e.g., level 5–15 or day 1–3) and met the first real friction.
  - *Effects:* one-time high-value bundle (currency, boosters, a hero or cosmetic); disappears after purchase or at a real deadline.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Trigger timing | after the aha moment and first friction | On first launch it reads as a cash grab |
| Value vs store baseline | 3–10× | The first purchase is the biggest barrier; make it obviously good |
| Price tier | lowest to low tiers of the storefront | Low commitment |
| Window | real 24–72 h, or permanent until bought | Fake resetting timers are a dark pattern |

- **Dynamics:** converts payers early; later offers ladder up from it.
- **Aesthetic targets (MDA):** Fantasy (a head start), Submission.
- **Feedback and juice:** clear contents grid; satisfying unpacking after purchase.
- **Failure modes and exploits:** shown before value is felt; countdowns that reset; "was" prices that never existed.
- **Mobile fit:** one screen, one decision.
- **Monetization hooks and the ethical limit:** first conversion. Real windows only; no fabricated reference prices; no urgency messaging to declared minors.
- **Regulatory notes:** Apple treats promoting a false price as grounds for removal; EU price-reduction disclosure rules may apply to "discount" claims — check applicability to digital items with `legal-ethics`.
- **Implementation notes:** server-side offer state; one-time entitlement survives reinstall.

```text
eligible(p) = not p.bought("starter") and p.max_level >= START_LEVEL and p.first_friction_seen
urgency_copy(p) = p.age_band == "adult"       # no countdown framing for minors or unknown age
expires_at = p.starter_shown_at + WINDOW     # set once, never reset
```
- **Reference games:** Hearthstone (Welcome Bundle), most free-to-play mobile titles.
- **Combines well with:** `triggered-offers`, `currency-store`, `piggy-bank`.

### 12.11 Triggered and chain offers — `triggered-offers`

- **Category:** IAP · contextual and segmented offers
- **Player fantasy:** "The shop offers what I actually need, right now."
- **Core rules:**
  - *State:* offer catalogue with triggers and segments; per-player caps, cooldowns and decline history.
  - *Triggers:* context (level-up, event start, resource empty, new feature) or segment (payer tier, lapsed).
  - *Effects:* show one eligible offer; chain ("endless") offers alternate free and paid steps where claiming or buying unlocks the next step.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Offers per session / day | 1 / 2–3 | More = fatigue and resentment |
| Decline cooldown | 24–72 h per offer group | Respects a "no" |
| Chain free:paid ratio | 1:1 to 2:1 | Free steps build goodwill and momentum |
| Segment price points | 2–4 tiers | Too fine-grained looks like price discrimination |

- **Dynamics:** higher conversion; feels personal when relevant, manipulative when keyed to frustration.
- **Aesthetic targets (MDA):** Submission.
- **Feedback and juice:** chain steps unlock with a satisfying chain-link animation; free steps clearly labelled.
- **Failure modes and exploits:** offers fired at frustration peaks with countdowns; perceived unfair pricing across players; offer spam.
- **Mobile fit:** good when capped.
- **Monetization hooks and the ethical limit:** relevance-driven conversion. Never key offers to distress, losing streaks with escalating pressure, or late-night binge patterns; offer spending limits; do not personalise prices for minors.
- **Regulatory notes:** EU consumer law requires telling consumers when a price is personalised by automated decision-making, and GDPR governs profiling — confirm with `legal-ethics`; child audiences fall under COPPA and age-appropriate design codes.
- **Implementation notes:**

```text
eligible(o, p) = (o.trigger(p.recent_events) and p.offers_today < DAILY_CAP and now - p.last_decline.get(o.group, 0) >= COOLDOWN
                  and not (p.age_band == "child") and not o.blocked_by(p.spend_limit))
```
- **Reference games:** chain ("endless") offers are widely reported in deconstructions of top-grossing casual titles such as Royal Match — check current live offers before citing specifics.
- **Combines well with:** `starter-pack`, `paid-boosters`, `piggy-bank`.

### 12.12 Piggy bank — `piggy-bank`

- **Category:** IAP · accumulated-value purchase
- **Player fantasy:** "Look how much I've saved — now I can crack it open."
- **Core rules:**
  - *State:* locked bank balance in premium currency; cap; price to open.
  - *Triggers:* level wins or currency spend add to the bank; purchase opens it.
  - *Effects:* contents granted on purchase; the bank resets (often to a higher tier).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Fill per win | small, visible | Visible growth is the pull |
| Cap value vs price | 3–8× | Below 3× is unattractive; above 8× undercuts the store |
| Minimum to open | e.g., 30–50 % full | Prevents buying a near-empty bank |
| Decay | none | Decay is a pressure tactic |

- **Dynamics:** engagement to fill; a purchase pull that grows with play.
- **Aesthetic targets (MDA):** Submission.
- **Feedback and juice:** coins dropping into the jar after wins; "full" shimmer.
- **Failure modes and exploits:** contents that expire or shrink; wording implying the currency is already the player's; uncapped banks.
- **Mobile fit:** passive, glanceable.
- **Monetization hooks and the ethical limit:** a recurring mid-price purchase. Show the price on the bank itself; contents never decay; no "you'll lose it" messaging.
- **Regulatory notes:** price transparency rules as for other offers; virtual currency only usable within the app it was bought for (Google Play).
- **Implementation notes:**

```text
on_win(p): p.bank = min(p.bank + FILL, CAP[p.bank_tier])
open_bank(p): require purchase_verified("piggy_" + p.bank_tier); grant(p, "gems", p.bank); p.bank = 0; p.bank_tier = next_tier(p.bank_tier)
```
- **Reference games:** common in casual puzzle and social-casino titles, for example Toon Blast.
- **Combines well with:** `starter-pack`, `triggered-offers`, `currency-store`.

### 12.13 Hard-currency store and first-purchase bonus — `currency-store`

- **Category:** IAP · currency packs (currency design: `currency-architecture` (04))
- **Player fantasy:** "I can top up once and choose what to spend it on."
- **Core rules:**
  - *State:* pack ladder `{product_id, amount, bonus_pct, first_purchase_double}`; localised prices from the store.
  - *Triggers:* store visit; insufficient-funds prompts.
  - *Effects:* purchase grants currency (doubled on the first purchase of each tier where offered); currency buys items in the game.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Ladder size | 5–8 packs | More choice, more anchoring |
| Bonus by size | rises with pack size | Rewards larger packs without hiding unit prices |
| First-purchase-per-tier double | on / off | Strong conversion lever at every tier |
| Pack-to-item fit | common items purchasable without awkward leftovers | Engineered leftovers ("breakage") push repeat purchases unfairly |

- **Dynamics:** anchoring on the best-value badge; one premium currency simplifies every price decision.
- **Aesthetic targets (MDA):** Submission.
- **Feedback and juice:** currency shower; balance ticks up; receipt-style confirmation.
- **Failure modes and exploits:** pack sizes mismatched to item prices on purpose; several premium currencies that blur value; hard-coded prices that are wrong in other storefronts.
- **Mobile fit:** standard store screen.
- **Monetization hooks and the ethical limit:** the core IAP surface. One premium currency; real-money equivalents near premium prices; packs that fit common purchases.
- **Regulatory notes:** Apple: purchased currency may not expire. Google Play: virtual currency usable only in the title it was bought for; prices must match the billing UI. EU consumer authorities' principles on in-game virtual currencies push for real-money price clarity (section 9). Some jurisdictions cap minors' spending — check `legal-ethics` per storefront.
- **Implementation notes:** read localised prices from the store at runtime (StoreKit 2 products, Play Billing product details, or RevenueCat offerings); grant currency only after server-side receipt validation.

```text
on_purchase(tx): require validate_server_side(tx); pack = PACKS[tx.product_id]
  amt = pack.amount * (2 if pack.first_double and not p.bought_tier[pack.id] else 1) * (1 + pack.bonus_pct)
  grant(p, "gems", round(amt)); p.bought_tier[pack.id] = True; ledger(tx, amt)
```
- **Reference games:** Genshin Impact (first top-up bonus per tier), Clash of Clans (gems), Brawl Stars (gems).
- **Combines well with:** `starter-pack`, `piggy-bank`, `web-shop`, `currency-architecture` (04).

### 12.14 Cosmetic shop — `cosmetic-shop`

- **Category:** IAP · direct-purchase self-expression
- **Player fantasy:** "I look the way I want — and others notice."
- **Core rules:**
  - *State:* catalogue of cosmetics (no gameplay stats); rotation schedule; owned items; wishlist.
  - *Triggers:* daily or weekly rotation; player browses, previews, buys or gifts.
  - *Effects:* direct purchase (no randomness); items equip immediately; wishlisted items notify on return.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Rotation cadence | daily featured, weekly full | Faster rotation = more urgency, more FOMO |
| Return frequency | stated "returns occasionally" | Reduces panic buying |
| Bundle discount | 20–40 % vs items separately | Raises basket size honestly |
| Preview | full try-on with animation | Fewer regret purchases and refunds |

- **Dynamics:** expression and status; collection; social display in matches and visits.
- **Aesthetic targets (MDA):** Expression, Fellowship, Fantasy.
- **Feedback and juice:** try-on with emotes; purchase confirmation with a "show it off" moment.
- **Failure modes and exploits:** extreme scarcity messaging; cosmetics with hidden stats; poor previews; unauthorised purchases by children on a shared device.
- **Mobile fit:** browse in seconds; strong fit for portrait shops.
- **Monetization hooks and the ethical limit:** the cleanest monetization: value is visible, nothing is random, nothing affects winning. Offer preview, purchase confirmation and an undo or refund window; no stats on cosmetics.
- **Regulatory notes:** the FTC's 2022 Epic Games settlement covered purchase flows and children's purchases on shared accounts — confirmation steps and parental controls matter (section 9).
- **Implementation notes:** rotation seeded by date on the server; client shows server time to avoid clock tricks.

```text
rotation(day) = seeded_sample(CATALOGUE.eligible(day), k=FEATURED, seed=hash(SHOP_SEED, day))
buy(p, item): require confirm(item.price); charge(p, item); own(p, item); allow_undo(p, item, window=UNDO_WINDOW)
```
- **Reference games:** Fortnite (Item Shop), Brawl Stars (skins), League of Legends: Wild Rift (skins), Pokémon GO (avatar shop).
- **Combines well with:** `free-placement-decor` (09), `design-challenge` (09), `premium-pass`.

### 12.15 Web shop (direct-to-consumer) — `web-shop`

- **Category:** payments · off-app storefront
- **Player fantasy:** "Better deals for buying direct."
- **Core rules:**
  - *State:* web store linked to the game account; entitlement service; per-storefront feature flags (`config.json → storefronts`).
  - *Triggers:* player visits the web store directly, or follows an in-app link-out where the storefront country's rules allow it.
  - *Effects:* purchase on the web; entitlement granted server-side and delivered on next sync; parental gates where required.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Web bonus vs in-app | +5–20 % value | Must justify the extra steps |
| Link-out placement | only where permitted per country and age band | Wrong placement = store rejection |
| Login friction | one-tap account link | Each extra step loses buyers |
| Payment methods | local methods per region | Major conversion driver outside the US |

- **Dynamics:** margin improvement; player confusion about where to buy; account-security exposure.
- **Aesthetic targets (MDA):** none — commerce infrastructure.
- **Feedback and juice:** in-game mail confirming the delivery; same item art as in-app.
- **Failure modes and exploits:** link-outs shown where they are not allowed; entitlement sync failures; account takeovers; minors buying without gates.
- **Mobile fit:** off-app by design; keep the round trip short.
- **Monetization hooks and the ethical limit:** better margins. Same refund and price-clarity standards as in-app; disclose that the purchase happens outside the store's protections.
- **Regulatory notes (highly volatile):** US Apple link-outs are allowed but the permissible fee is before the Supreme Court; US Google alternative billing is allowed under the Epic injunction with fees unsettled; in the EU, Apple's new terms from 1 October 2026 bar link-outs in Kids Category and under-13 apps and require a parental gate for under-18 apps using alternative payments or link-outs. Details and sources in section 9.
- **Implementation notes:** treat storefront country and age band as feature-flag dimensions; server-to-server entitlement with idempotent grants.

```text
show_linkout(p) = LINKOUT_RULES[p.storefront].allowed and not p.is_kids_category and (p.age_band != "under_18" or parental_gate_passed(p))
deliver(order): if order.id not in p.granted: grant(p, order.items); p.granted.add(order.id)    # idempotent
```
- **Reference games:** Supercell Store (web store for Supercell titles).
- **Combines well with:** `currency-store`, `starter-pack`, `subscription-perks`.

## 7. Recurring value

### 12.16 VIP tiers — `vip-tiers`

- **Category:** IAP · cumulative-spend status
- **Player fantasy:** "My loyalty is recognised."
- **Core rules:**
  - *State:* VIP points (from verified purchases, sometimes daily logins or items); VIP level thresholds; perk table; optional activation timer.
  - *Triggers:* verified purchase; daily login points; perk activation.
  - *Effects:* level-ups unlock permanent or active perks (extra queue slot, speed-up %, daily chest, auto-play speed).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Thresholds | rising steeply | Top tiers concentrate on high spenders |
| Perk type | convenience vs power | Power perks in PvP are pay-to-win |
| Visibility | private by default | Public badges create status pressure |
| Free VIP points | small daily drip | Lets non-payers taste perks |

- **Dynamics:** high-spender retention; sunk cost; status signalling.
- **Aesthetic targets (MDA):** Fellowship (status), Submission.
- **Feedback and juice:** VIP card with perks listed; level-up ceremony kept modest.
- **Failure modes and exploits:** PvP power perks; public VIP shaming; perks that lapse unless the player keeps spending.
- **Mobile fit:** menu feature; low interaction cost.
- **Monetization hooks and the ethical limit:** retention of payers. Convenience perks only; private by default; earned levels never decay; spending-limit tools available.
- **Regulatory notes:** minors' spending caps exist in some jurisdictions (verify per storefront); avoid aggressive-practice risks under EU unfair-commercial-practices law.
- **Implementation notes:** points only from server-validated receipts; level is a pure function of lifetime points.

```text
on_verified_purchase(tx): p.vip_points += POINTS_PER_USD * tx.usd_value; p.vip = level_for(p.vip_points)
perks(p) = union(PERKS[l] for l in range(1, p.vip + 1))
```
- **Reference games:** Rise of Kingdoms, Whiteout Survival, Lords Mobile.
- **Combines well with:** `subscription-perks`, `auto-play` (11), `hq-gated-building` (09).

### 12.17 Premium pass — `premium-pass`

- **Category:** IAP · seasonal premium track (track design: `pass-tracks` (05))
- **Player fantasy:** "Paying once makes my whole season richer."
- **Core rules:**
  - *State:* season id; premium entitlement; tier progress; claimed flags; optional premium-plus and tier purchases.
  - *Triggers:* purchase; tier advances.
  - *Effects:* premium rewards unlock retroactively for all reached tiers; premium-plus adds tier skips; unclaimed rewards auto-grant at season end.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Perceived value vs price | 5–10× | Below this conversion drops |
| Premium-plus skips | 10–25 % of tiers | Sells time without breaking pacing |
| Tier purchase price | high enough not to undercut the pass | Last-week tier buying is sunk-cost driven |
| Completion pacing | engaged median finishes by 75–90 % of the season | Requiring daily max play breeds burnout |

- **Dynamics:** day-one and final-week purchase spikes; season-long engagement.
- **Aesthetic targets (MDA):** Submission, Expression.
- **Feedback and juice:** "you'd already unlock N rewards" counter; one-tap claim-all.
- **Failure modes and exploits:** pacing that forces daily play or tier purchases; power on the premium track in PvP; lost unclaimed rewards.
- **Mobile fit:** excellent.
- **Monetization hooks and the ethical limit:** the best-value recurring purchase for most players. Completable by the median engaged player without tier buys; auto-grant unclaimed rewards; end date always visible.
- **Regulatory notes:** a pass sold as an auto-renewing subscription must meet Apple's 3.1.2 rules (ongoing value, period ≥ 7 days, all devices, clear description before subscribing); otherwise it is a non-consumable or consumable per season.
- **Implementation notes:** entitlement per season id, server-side (store server notifications or RevenueCat entitlements).

```text
on_purchase_pass(p, season): require validate(tx); p.premium[season] = True
  for t in range(1, p.tier[season] + 1): queue_reward(p, PREMIUM_TRACK[season][t])     # retroactive
on_season_end(p, season): auto_grant_unclaimed(p, season)
```
- **Reference games:** Fortnite (Battle Pass), Clash Royale (Pass Royale), Brawl Stars (Brawl Pass), Clash of Clans (Gold Pass).
- **Combines well with:** `subscription-perks`, `cosmetic-shop`, `pass-tracks` (05).

### 12.18 Subscription perks — `subscription-perks`

- **Category:** subscription · recurring value
- **Player fantasy:** "A small regular fee makes every day better."
- **Core rules:**
  - *State:* entitlement states (active, grace period, billing retry, expired); perk list; daily-claim state.
  - *Triggers:* purchase or renewal (store server notifications); daily claim; cancellation or expiry.
  - *Effects:* perks while active — daily currency drip, ad removal, convenience slots, an exclusive cosmetic; a non-renewing 30-day card is the lighter variant.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Total monthly value vs price | clearly above one-off packs | The sub must beat buying currency |
| Daily-claim rule | accumulate vs lose missed days | Losing missed days is engagement pressure; say so clearly or let claims accumulate |
| Perks | convenience and cosmetics | Removing them must not break the game |
| Trial | short, with clear conversion notice | Silent trial conversion is a dark pattern |

- **Dynamics:** predictable revenue; habit; churn concentrated at renewal.
- **Aesthetic targets (MDA):** Submission.
- **Feedback and juice:** daily claim card; "your subscription saved you N" summary.
- **Failure modes and exploits:** hard-to-find cancellation; unclear renewal price; perks whose loss makes the game unplayable; trial conversion surprises.
- **Mobile fit:** one daily tap.
- **Monetization hooks and the ethical limit:** recurring revenue. In-app link to the store's subscription management; renewal price and period stated before purchase; the game stays fully playable without the subscription.
- **Regulatory notes:** Apple 3.1.2: ongoing value, period ≥ 7 days, available on all the user's devices, and a clear description of what the user gets before subscribing. In the US, state automatic-renewal laws apply; the FTC's federal "click-to-cancel" rule was reported vacated in 2025 (section 9).
- **Implementation notes:** drive state from App Store Server Notifications and Google Play real-time developer notifications (or RevenueCat); never trust client state for entitlements.

```text
on_store_notification(n): p.sub = transition(p.sub, n.type)      # ACTIVE / GRACE / RETRY / EXPIRED
daily_claim(p): require p.sub in (ACTIVE, GRACE) and not p.claimed_today; grant(p, "gems", DAILY_DRIP)
```
- **Reference games:** Genshin Impact (Blessing of the Welkin Moon, a 30-day card), Roblox (Roblox Premium).
- **Combines well with:** `premium-pass`, `vip-tiers`, `interstitial-cadence` (ad-free perk).

## 8. High-risk mechanics

### 12.19 Offer walls — `offer-wall`

- **Category:** incentivized ads · third-party tasks for currency
- **Player fantasy:** "I can earn premium currency by trying other things."
- **Core rules:**
  - *State:* offer-wall SDK placement; postback ledger; category filters.
  - *Triggers:* player opens the wall and completes a third-party task (install-and-reach-level, survey, sign-up).
  - *Effects:* the network's server-to-server postback credits currency, often hours or days later.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Placement | store page "free gems" only | Prominent placement cannibalises IAP |
| Category filters | exclude finance, gambling, dating, subscriptions-with-trials | Protects players and reputation |
| Payout display | currency plus expected credit time | Most support tickets are about delayed credit |
| Eligibility | adults only (age-gated) | Third-party offers are unsuitable for minors |

- **Dynamics:** monetises non-payers at high value per completion; low participation share.
- **Aesthetic targets (MDA):** none — commerce infrastructure.
- **Feedback and juice:** "pending credit" status per offer; credit toast with source.
- **Failure modes and exploits:** offers with hidden costs; missing or delayed credits; fraud; inappropriate offers to minors; data sharing without consent.
- **Mobile fit:** menu feature.
- **Monetization hooks and the ethical limit:** non-payer revenue. Off for under-18 and unknown-age players; strict category filters; never require an offer to progress.
- **Regulatory notes:** Apple 3.2.2(x) bars forcing users to download other apps to access functionality, and offer networks commonly restrict install-incentive offers on iOS — verify current store and network rules. Google Play treats ads and associated offers as part of your app, so every offer must comply with Play policy. Child audiences: COPPA consent rules; tracking requires Apple's ATT prompt.
- **Implementation notes:** verify postback signatures; idempotent crediting; log offer id and network for support.

```text
on_postback(req): require verify_signature(req, NETWORK_SECRET) and req.txn_id not in ledger
  grant(user(req.user_id), "gems", req.amount); ledger.add(req.txn_id, req.offer_id, req.network)
```
- **Reference games:** no specific titles recommended — offer walls come from ad networks (for example Tapjoy) and appear mostly in social-casino and idle games.
- **Combines well with:** `currency-store`, `rewarded-unlock`.

### 12.20 Paid randomized rewards (compliance layer) — `paid-random-rewards`

- **Category:** IAP · randomized purchase (mechanics: `gacha-banners`, `mystery-boxes`, `pity-timers` (07))
- **Player fantasy:** "Maybe this pull is the one."
- **Core rules:**
  - *State:* odds table (single source of truth); pity counters; spark or exchange balance; region and age flags.
  - *Triggers:* any purchase — direct or via premium currency — whose contents are random (pulls, packs, paid eggs or chests, paid spins).
  - *Effects:* blocked where law or age forbids; otherwise odds shown before purchase, server-side draw, pity and exchange ceilings applied, every draw audit-logged.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Top-rarity base rate | 0.5–3 % per pull | Lower rates concentrate spend and variance |
| Hard pity | 50–100 pulls | Defines the worst case — publish it |
| Exchange (spark) | target item after N pulls | Deterministic ceiling for featured items |
| Odds display | per item and per rarity, before purchase | Required by both stores |

  Model the cost distribution before launch: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gacha_calc.py --rate 0.006 --soft-pity-start 74 --soft-pity-step 0.06 --hard-pity 90 --pulls 180 --json`.
- **Dynamics:** revenue concentration in a small share of players; variance-driven community rituals; loss-chasing risk.
- **Aesthetic targets (MDA):** Sensation, Discovery, Fantasy.
- **Feedback and juice:** rarity-coded reveal; pity counter always visible; exchange balance next to the pull button.
- **Failure modes and exploits:** displayed odds differing from real odds; no ceiling; sales to minors where banned; "complete gacha" set prizes; draw results influenced by spend history.
- **Mobile fit:** short interactions; the risk is in frequency, not length.
- **Monetization hooks and the ethical limit:** the highest-yield and highest-risk mechanic in this file. Prefer transparent alternatives (passes, direct bundles); if used: per-item odds, published ceilings, deterministic paths to core items, region and age gating, spending reminders. Large-scale survey research has associated loot-box spending with problem-gambling measures (Zendle and Cairns, *PLOS ONE*, 2018; correlational).
- **Regulatory notes:** odds disclosure on Apple (3.1.1) and Google Play (Payments section 7); paid loot boxes banned in Belgium; banned for under-18s in Brazil since March 2026; Australian classification M (paid chance items) or R18+ (simulated gambling) for games classified since 22 September 2024; Japan's consumer authority reportedly found "kompu gacha" (complete-the-set prizes) problematic from about 2012 and the industry self-regulates; China and South Korea reportedly require probability disclosure (verify current rules); no effective Dutch ban since 2022. Details in section 9 and, for current status, `${CLAUDE_PLUGIN_ROOT}/skills/legal-ethics/references/privacy-children-gambling.md` (section 10); run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/compliance_preflight.py --project DIR --json` before every submission.
- **Implementation notes:** one odds file drives both draws and the odds screen, so they cannot drift.

```text
pull(p): if blocked(p.storefront, p.age_band): return deny("unavailable in your region or age group")
  p.pity += 1; item = guaranteed_top() if p.pity >= HARD_PITY else weighted_pick(ODDS, rng=server_rng)
  if item.rarity == TOP: p.pity = 0
  audit_log(p.id, item.id, server_rng.state); return item
```
- **Reference games:** Genshin Impact, Fate/Grand Order, FIFA / EA Sports FC Ultimate Team packs (subject of the Belgian and Dutch cases).
- **Combines well with:** `gacha-banners` (07), `pity-timers` (07), `currency-store`.

## 9. Volatile facts (as of Oct 2026 — verify before relying)

**Store rules** (pages fetched 19 Oct 2026; wording paraphrased):
- Apple App Review Guidelines: 3.1.1 — randomized paid items must disclose the odds of each item type before purchase; purchased credits or in-game currencies may not expire; provide a restore mechanism for restorable purchases. 3.1.2(a) — auto-renewing subscriptions must provide ongoing value, last at least seven days and be available on all the user's devices; 3.1.2(c) — describe what the user gets before asking them to subscribe. 3.2.2(x) — apps must not force users to rate, review or download other apps to access functionality. 1.3 / 5.1.4 — Kids Category apps should not include third-party advertising or analytics (narrow exceptions with human review of ad creatives). Promoting a false price is grounds for removal (2.3.1(a)). — [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/)
- Google Play Ads policy: full-screen restrictions exempt rewarded ads that users explicitly opt into; prohibited: interstitials that appear unexpectedly, ads at the beginning of a level during gameplay, full-screen interstitials not closable after 15 s, full-screen video interstitials before the app's loading screen; ads and associated offers are treated as part of the app. — [Play Ads policy](https://support.google.com/googleplay/android-developer/answer/9857753)
- Google Play Payments policy: randomized virtual items must clearly disclose odds before purchase (section 7); in-app virtual currencies may only be used in the title they were bought for; developers must clearly and accurately state terms and pricing, and in-app prices must match the Play billing UI; Play billing is required unless specific alternative-billing sections apply. — [Play Payments policy](https://support.google.com/googleplay/android-developer/answer/9858738)

**Children, privacy and age:**
- Amended US COPPA Rule: compliance deadline 22 April 2026; broader personal-information definition (including biometrics), mixed-audience standards, operator responsibility for third-party integrations; separate verifiable parental consent before disclosing children's data to third parties such as ad networks. — [Toy Association](https://toyassociation.org/PressRoom2/News/2026-News/updated-coppa-rule-requirements-take-effect-april-22.aspx); [Loeb & Loeb](https://www.loeb.com/fr/insights/publications/2025/05/childrens-online-privacy-in-2025-the-amended-coppa-rule)
- US state app-store age-assurance laws (Texas from 1 January 2026, Utah 7 May 2026, Louisiana 1 July 2026) route through Apple's Declared Age Range API. — [9to5Mac](https://9to5mac.com/2025/11/04/app-store-texas-sb2420-new-apis/)
- Apple's ATT prompt is required before tracking via IDFA; reported opt-in rates range from about 35 % to 50 % depending on source. — [Moburst](https://www.moburst.com/blog/idfa-att-update/)

**Paid randomized items:**
- Belgium: paid loot boxes banned under gambling law since 2018. Netherlands: no effective ban after the 2022 Council of State ruling on FIFA packs (sources conflict on current enforcement). EU: a Digital Fairness Act may address loot boxes, reportedly not before 2028. — [Programming Insider](https://programminginsider.com/loot-boxes-regulation-and-where-the-line-sits-in-2026/)
- Brazil: ECA Digital bans selling loot boxes to under-18s from March 2026; in June 2026 a court ordered Riot Games to pay damages and add age verification and odds disclosure (reported amounts conflict). — [Sheep Esports](https://www.sheepesports.com/articles/brazil-court-orders-riot-games-to-pay-eur2-5m-over-league-of-legends-loot-boxes/en)
- Australia: games classified from 22 September 2024 with paid chance-based items are rated at least M; simulated gambling is rated R18+. — [PCWorld](https://www.pcworld.com/article/2464538/all-games-with-loot-boxes-will-be-rated-m-or-higher-in-australia.html)
- Background, reported positions, not re-verified this session: Japan's consumer authority reportedly found "kompu gacha" (complete-the-set prizes) problematic from about 2012 and the industry self-regulates, with platform and industry guidelines asking for odds disclosure; China reportedly requires public odds disclosure (a 2017 ministry notice, with later draft online-game measures); South Korea reportedly began requiring probability disclosure for chance-based items in 2024. Confirm current texts with counsel or official sources before relying on them.
- Where current status is maintained: `${CLAUDE_PLUGIN_ROOT}/skills/legal-ethics/references/privacy-children-gambling.md` (section 10, loot boxes by jurisdiction; section 15, volatile facts). This section is a dated snapshot; if the two differ, the `legal-ethics` file wins.

**Payments and link-outs:**
- EU (Apple, from 1 October 2026): App Store with Apple IAP 26 % (15 % for small-business and qualifying cases); alternative processor 20 % (10 %); link-out 15 % (10 %); 5 % Core Technology Commission for apps distributed outside the App Store; the payment choice is locked for 12 months; no link-outs in Kids Category or under-13 apps; parental gate for under-18 apps using alternative payments or link-outs. — [Apple Newsroom](https://www.apple.com/newsroom/2026/08/apple-announces-changes-for-apps-in-the-european-union/); [Apple: apps in the EU](https://developer.apple.com/support/apps-in-the-eu/)
- US (Apple): link-outs are permitted; the Ninth Circuit (11 December 2025) allowed only a cost-based fee on remand; the Supreme Court granted review (No. 25-1311) and Apple filed its merits brief on 14 September 2026. — [Justia](https://law.justia.com/cases/federal/appellate-courts/ca9/25-2935/25-2935-2025-12-11.html); [SCOTUS docket filing](https://www.supremecourt.gov/DocketPDF/25/25-1311/424150/20260914154510009_2026-09-14%20No.%2025-1311%20Apple-Epic%20Merits%20Opening%20Brief.pdf)
- US (Google Play): alternative billing and external links allowed under the Epic injunction; the fee schedule and settlement approval were unsettled as of mid-2026. — [Stash](https://www.stash.gg/blog/blog-epic-v-google-settlement-update-april-2026)

**Consumer protection (background, not re-verified this session):**
- FTC v. Epic Games (December 2022): settlements totalling $520 million — a $275 million COPPA penalty and $245 million in refunds over purchase flows the FTC alleged were dark patterns. — [FTC press release](https://www.ftc.gov/news-events/news/press-releases/2022/12/fortnite-video-game-maker-epic-games-pay-more-half-billion-dollars-over-ftc-allegations)
- EU Consumer Protection Cooperation (CPC) Network: reportedly published key principles on in-game virtual currencies (real-money price clarity, no pressure selling, protection of children). `legal-ethics` records the year as 2025; the date and primary URL were not re-verified here, so find the text on the European Commission site before citing it.
- US subscriptions: the FTC's "click-to-cancel" negative-option rule was reported vacated by the Eighth Circuit in 2025; state automatic-renewal laws continue to apply. Verify on FTC.gov and with counsel.
- Research: Zendle and Cairns (2018) found loot-box spending associated with problem-gambling severity in a large survey (correlational). — [PLOS ONE](https://doi.org/10.1371/journal.pone.0206767)

**Related skills:** `monetization` (pricing, offers, live operations of the store), `economy-design` (sources, sinks, ad-income modelling), `legal-ethics` (loot boxes, minors, consumer law), `liveops` (offer calendars, passes), `player-psychology` (motivation versus manipulation), `store-release` (store review and compliance pre-flight).
