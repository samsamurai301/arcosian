# Offers, Regulation and Ethics

This file covers how to design and measure offers (starter packs, bundles, passes, price ladders), and the legal and ethical frame around them: loot-box laws, odds disclosure, refunds, virtual-currency consumer protection, minors and a list of red lines the studio never crosses. Read it before designing a store, before a design review's monetization pass, and before any regional launch. It is not legal advice; confirm with counsel for each market.

## Table of contents
1. Offer anatomy
2. Offer catalogue and when each works
3. Price ladders and pack design
4. Offer triggers and segmentation
5. Measuring offers
6. Worked example: starter pack test
7. Loot boxes and randomized paid items
8. Odds disclosure and pity systems
9. Refunds, chargebacks and revocation
10. Virtual-currency consumer protection
11. Minors and vulnerable players
12. Red lines
13. Compliance workflow
14. Volatile facts (as of Oct 2026 - verify)

## 1. Offer anatomy
An offer is a product plus a context. Specify all of these:
| Field | Question |
|---|---|
| Need | Which loop tension does it relieve? |
| Audience | Which segment, state and lifecycle stage? |
| Contents | What exactly is delivered; what is the real-value comparison? |
| Price | Which store tier; which currency? |
| Trigger | When does it appear; what suppresses it? |
| Duration | Real expiry or evergreen? |
| Frequency | Max impressions per player, cool-down |
| Success metric | Conversion, revenue per exposed, guardrails |
| Ethics check | Would a reasonable player feel tricked? |

## 2. Offer catalogue and when each works
| Offer | Purpose | Use when | Caution |
|---|---|---|---|
| Starter pack | First purchase; converts non-payers | After player has felt value (not session one minute one) | Make it a good deal at a low tier, one time only |
| Remove-ads bundle | Convert ad-averse | Ad load is noticeable | Include a perk beyond ad removal |
| Currency packs | Core store ladder | Always available | Keep pack sizes aligned to item prices |
| Time-skip / energy refill | Convenience | Loop has waiting | Do not make waiting artificially painful |
| Progress boost | Speed | Mid-game | Avoid in competitive modes |
| Cosmetic bundles | Expression | Social or visible avatars | Best ethical sink; rotate honestly |
| Season pass | Engagement plus revenue | Live game with cadence | Completability and honest value |
| Subscription | Recurring convenience | Daily habit | Clear renewal and cancel path |
| Piggy bank / savings | Accumulating discount | Players accrue currency | Clearly show how it fills and the price |
| Event bundle | Time-boxed power | Event with rewards | Real deadline only |
| Welcome-back offer | Win-back | Lapsed payers or non-payers | Segment, limit, no guilt tone |

## 3. Price ladders and pack design
- Ladder rungs: from the lowest store tier to a high tier. Having many rungs is a convenience; having too many dilutes decision speed. Typical store shows about five to seven packs.
- Value per currency unit should increase with price, but not so steeply that buying small packs feels like a trap. Compute `currency_per_price` for each rung and chart it.
- Align pack sizes to item costs so the player does not end with a useless leftover remainder (a common currency-obfuscation complaint). Test: for each common item price, check the leftover for each pack; flag packs with awkward remainders.
- Best-value tags must be factual relative to other packs.
- Regional pricing: use store price tiers; do not convert by hand. Review emerging-market prices for affordability.
- First-purchase bonuses ("double the first time") are common; keep them transparent and once per account, not per device reinstall.
- Price changes: change contents by config rather than price per product id where possible; communicate changes in patch notes when material.
Formula for pack value index: `VI_i = (currency_i / price_i) / (currency_1 / price_1)`. Keep VI monotone non-decreasing with a gentle slope; inspect jumps above the previous rung's slope.

## 4. Offer triggers and segmentation
Segments by payer state: non-payer, first-time buyer (within N days), repeat payer, lapsed payer, subscriber. Add lifecycle (day 0-3, 4-14, mature) and engagement (casual, core).
Allowed triggers (examples): milestone reached, resource nearly spent, new content unlocked, event start, return after absence, level completion with sustained progress.
Disallowed or high-risk triggers: right after a loss streak designed to induce frustration, when the player is detected as a heavy spender in a short time (risk of harm), when the account is flagged as a minor, repeated pop-ups in a single session.
Rules of thumb:
- At most one monetization interruption per session in the first week; none in the tutorial.
- Offers must be dismissible with one tap and accessible again from the store.
- Every pop-up gets a suppression rule; write it in the offer spec.
- Personalization must not use sensitive inferences (financial distress, mental state).

## 5. Measuring offers
Metrics: impressions, click-through, purchase conversion (per impression and per exposed user), revenue per exposed user, incremental revenue vs holdout, cannibalization of other SKUs, refund rate, effect on D1/D7/D30 retention, support tickets.
Procedure:
1. Define hypothesis and primary metric (revenue per exposed user, or conversion for a first-purchase offer).
2. Randomize by player id; hold out a no-offer group when the offer is new, to detect cannibalization.
3. Pre-compute sample size (`${CLAUDE_PLUGIN_ROOT}/scripts/ab_test.py`); payer conversion is a rare event, so required samples are large; plan duration accordingly.
4. Guardrails: retention, session, refund, review sentiment.
5. Do not peek and stop on the first positive; use a fixed horizon or sequential method.
6. Read heterogeneity (country, platform, acquisition source) but treat subgroup findings as hypotheses.
7. Record decision and learnings in the project state.
Common traps: novelty effect (offers always convert at first), seasonality, mixing price tests with content changes, whale outliers dominating mean revenue (report medians and trimmed means as well, plus capped revenue).

## 6. Worked example: starter pack test
Hypothesis: offering a starter pack at level 8 instead of day 2 raises first-purchase conversion without reducing D7.
- Variants: A (level 8 trigger), B (day 2 trigger, same content and price).
- Primary: share of users who make a first purchase within 7 days of install. Guardrails: D7 retention, refund rate.
- Sample: compute with `ab_test.py` using the baseline conversion from soft launch; if baseline is low, the test may need more traffic than soft launch provides; then pool countries or test a bigger lever.
- Read: if A wins on conversion and D7 is flat, ship A; if tied, choose the less intrusive timing; if B wins but refund rate is higher, investigate whether buyers understood the contents.

## 7. Loot boxes and randomized paid items
Definition used here: any paid item whose contents are determined by chance and where the player cannot know what they will receive in advance (crates, gacha pulls, card packs, mystery boxes). Premium-currency-purchased randomized items count if the currency is bought for money.
Regulatory picture (summary; verify):
| Jurisdiction | Status (as researched) | Design consequence |
|---|---|---|
| Belgium | Paid loot boxes treated as gambling; ban since 2018 | Disable paid random items there |
| Brazil | Law restricts sale of loot boxes to under-18s, in force 2026; a court case against a major publisher reported | Age-verify or disable for minors; show probabilities |
| Netherlands | Enforcement approach reversed by courts; no effective ban reported | Still follow odds disclosure |
| Australia | Classification rules: paid chance-based items rated at least M; simulated gambling R18+ | Plan the age rating |
| EU | A consumer-law initiative (Digital Fairness Act) is discussed; timing uncertain | Design for transparency now |
| Platforms | Apple and Google require odds disclosure before purchase | Mandatory for store approval |
| China | Disclosure of draw probabilities required since May 1, 2017 (Ministry of Culture notice); the NPPA's December 2023 draft with further limits was pulled in January 2024, status unclear | Publish odds; local licensed publisher |
| South Korea | Mandatory probability disclosure from March 2024; Nexon Korea fined 11.6 billion won in January 2024 for undisclosed odds changes | Accurate odds; change log |
| Japan | "Complete gacha" (set-completion prizes) held unlawful by the Consumer Affairs Agency in 2012 | No set-completion prizes; display rates |
| United Kingdom | Industry principles on paid loot boxes (July 2023) instead of legislation | Follow the principles; parental controls |
| United States | FTC v. HoYoverse (January 2025): $20M penalty, parental consent for loot-box purchases under 16, disclosure of odds and exchange rates | Show odds and real-money cost; age gating |
| Others | Own disclosure or restriction regimes | Check per market before launch |
Design alternatives that lower regulatory risk without killing the genre: deterministic purchases (buy the item), "choose one of N" packs, pity timers with visible counters, duplicate protection, free-to-earn alternative paths for each randomized item, spending caps.

## 8. Odds disclosure and pity systems
- Publish exact probabilities per rarity (and per item where reasonable) before the purchase decision, in a place reachable in one or two taps from the purchase screen, in the player's language.
- Probabilities must match code. Generate the disclosure from the same config the server uses; add a test that compares them. Version the table; store which version each pull used.
- If pity or soft-pity exists, disclose the rule (for example "guaranteed after N pulls without a top-rarity item") and show the counter to the player.
- Do not apply hidden dynamic odds (odds that change per player by spending or by "luck balancing") unless disclosed; many jurisdictions and platforms treat hidden manipulation as deceptive.
- Use `${CLAUDE_PLUGIN_ROOT}/scripts/gacha_calc.py` to compute expected pulls, cost to complete, pity effect and the distribution tail. Show the 90th-percentile cost honestly to the design team, even if you do not show it to players.
- Audit: log every randomized grant with seed id, table version, outcome.
Worked example: a pull has a base rate p for top rarity and a hard pity at N. Expected pulls to first top item is less than 1/p because of pity; compute exactly with the calculator rather than by hand, and add a worst-case cost (N pulls) to the store copy where the law requires clarity on cost.

## 9. Refunds, chargebacks and revocation
- Platform refunds are decided by the stores; developers receive notifications. Handle them: mark ledger refunded, apply policy.
- Policy options for consumed currency: allow negative balance until recovered; deduct remaining balance; restrict purchases; for repeat abusers suspend features. Document the policy in terms of service.
- Do not punish a player for a legitimate refund beyond reversing the grant.
- Provide an in-app way to find the stores' refund process and your support contact.
- Track refund rate by SKU and by country; a high refund SKU signals a misleading offer or accidental purchases (especially for minors).
- Accidental purchase prevention: confirmation steps for high-priced SKUs, device-level purchase protection guidance, parental gates in kid-facing contexts.
- Subscriptions: show renewal terms before the store sheet; link to platform subscription management.

## 10. Virtual-currency consumer protection
- Show the real-money price at the point of purchase and, where practical, the real-money equivalent of items priced in virtual currency, especially for high-value items. Consumer authorities in several jurisdictions have taken positions against obscuring real prices behind layered currencies; verify per market.
- Avoid multiple stacked currencies whose conversion rates are intentionally opaque.
- Currency expiry: avoid expiring paid currency without clear, prominent notice, and check local rules; many places restrict expiry of prepaid balances.
- Terms: state that virtual currency has no cash value if true, but do not use that to justify deceptive practices.
- Gifting and trading: if players can transfer value, assess money-laundering and fraud risks and platform rules.
- Account termination: define what happens to purchased items; deletion requests should be honored under privacy law.
- Spending visibility: provide a purchase history and an optional spending limit or reminder.

## 11. Minors and vulnerable players
- Determine audience in the design contract. If minors are a possible audience, apply the stricter standard to everyone or implement reliable age gating.
- Neutral age screens (do not hint at the "right" answer); do not store age beyond need; use platform age signals where available.
- For minors: no randomized paid items in regions that forbid them; spending caps; parental gate before purchase and external links; no personalized ads; no manipulative timers or pressure messaging; no social-pressure offers.
- Detection of at-risk patterns: very high spend within a short time, spend at odd hours repeatedly, rapid repeated purchases after losses. Response: friction (confirmation, cool-off), suppress offers, surface limits, and review by a human. Do not exploit these signals for targeting.
- Chat and social features add child-safety obligations beyond monetization; see `legal-ethics`.
- Platform parental controls are the first line; do not rely on them exclusively.

## 12. Red lines
The studio never ships these, regardless of metrics:
1. Hidden or false odds; odds that differ from disclosure.
2. Paid randomized items sold to players in jurisdictions or age groups where this is prohibited.
3. Countdown timers that restart or are fake scarcity.
4. Pay-to-win in competitive modes without a clearly labelled, fair separation.
5. Manufacturing frustration to sell relief (artificially rigged difficulty to drive offers).
6. Targeting identified minors or problem spenders with escalated offers.
7. Obscuring real-money cost through currency layering.
8. Making cancel flows harder than sign-up flows.
9. Unclear subscription renewal or free-trial conversion terms.
10. Dark patterns in consent (pre-checked boxes, confirm-shaming, rewards for tracking consent).
11. Selling or sharing children's data.
12. Deceptive ads for the game (see `marketing-ua`).
Detection: add these as review checklist items in the `design-review` skill and the compliance pre-flight.

## 13. Compliance workflow
1. Declare audience and target markets in the contract.
2. List every SKU and mark randomized ones.
3. Generate odds disclosure from config; verify parity.
4. Region matrix: feature flags per country for loot boxes, age rules, ads personalization.
5. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/compliance_preflight.py` and fix failures.
6. Human sign-off by the producer or counsel before store submission.
7. After launch, monitor regulation news for the markets you operate; maintain a changelog of policy changes.

## 14. Volatile facts (as of Oct 2026 - verify)
- Brazil's ECA Digital (signed Sep 2025) bans selling loot boxes to under-18s, effective March 2026; a June 2026 Brazilian court order against a major publisher reportedly required damages, age verification and probability disclosure (reported amounts conflict). Source: https://www.sheepesports.com/articles/brazil-court-orders-riot-games-to-pay-eur2-5m-over-league-of-legends-loot-boxes/en
- Belgium banned paid loot boxes under gambling law in 2018. Source: https://programminginsider.com/loot-boxes-regulation-and-where-the-line-sits-in-2026/
- Netherlands: reports conflict; a 2022 court ruling overturned a regulator fine, so no effective ban. Source: same as above.
- Australia: games classified from Sep 22, 2024 with paid chance-based items rated at least M; simulated gambling R18+. Source: https://www.pcworld.com/article/2464538/all-games-with-loot-boxes-will-be-rated-m-or-higher-in-australia.html
- EU: a Digital Fairness Act could bring EU-wide rules, reportedly not before 2028. Source: https://programminginsider.com/loot-boxes-regulation-and-where-the-line-sits-in-2026/
- Apple and Google require odds disclosure for randomized paid items. Source: https://developer.apple.com/app-store/review/guidelines/
- FTC v. HoYoverse (checked 2026-10-20): press release of January 17, 2025: $20 million civil penalty; no loot-box purchases by under-16s without a parent's affirmative express consent; disclosure of odds and of multi-tier virtual-currency exchange rates; COPPA terms; a stipulated order that needed court approval. Source: https://www.ftc.gov/news-events/news/press-releases/2025/01/genshin-impact-game-developer-will-be-banned-selling-lootboxes-teens-under-16-without-parental
- China, South Korea, Japan and UK (checked 2026-10-20, through press and law-firm sources; confirm texts with counsel): https://www.chinalawtranslate.com/en/ministry-of-culture-notice-regarding-strengthening-regulation-online-gaming-operations/ ; https://www.dtnext.in/lifestyle/technology/china-regulator-removes-draft-video-game-rules-from-website-shares-jump-763035 ; https://www.animenewsnetwork.com/news/2024-01-05/korean-ftc-fines-nexon-usd8.8-million-for-allegedly-manipulating-draw-odds-in-maplestory-game/.206181 ; https://www.invenglobal.com/articles/20319/nexons-maplestory-appeals-fine-as-seoul-high-court-resumes-hearing-in-april ; https://www.gamedeveloper.com/business/why-quot-kompu-gacha-quot-was-banned ; https://www.lewissilkin.com/insights/2023/07/24/new-uk-principles-and-guidance-on-loot-boxes-published-102ik8a
- COPPA amended rule: compliance deadline Apr 22, 2026. Source: https://toyassociation.org/PressRoom2/News/2026-News/updated-coppa-rule-requirements-take-effect-april-22.aspx
- US state app-store age-verification laws (Texas Jan 1, 2026; Utah May 7, 2026; Louisiana Jul 1, 2026). Source: https://9to5mac.com/2025/11/04/app-store-texas-sb2420-new-apis/
- GDPR Article 8: digital consent age 16 by default, states may lower to 13. Source: https://gdpr-info.eu/art-8-gdpr/

## 15. Offer spec template
Copy into the design contract or a feature spec for each offer.
```yaml
offer_id: starter_pack_v1
need: "bridge from first upgrade wall to second"
segment: { payer_state: non_payer, min_level: 8, max_account_age_days: 14 }
contents: [ {item: soft_currency, qty: 1500}, {item: booster_a, qty: 5}, {item: cosmetic_frame_basic, qty: 1} ]
price_tier: store_tier_low
real_value_note: "contents priced at normal store rates would cost more; compute and store the ratio"
trigger: "level_complete AND resource_low"
suppress_if: [ in_tutorial, shown_this_session, minor_flag, purchased_before ]
duration: { type: evergreen_once_per_account }
frequency: { max_impressions: 6, cooldown_hours: 24 }
metrics: { primary: first_purchase_7d, guardrails: [d7_retention, refund_rate] }
ethics_check: { odds: none, timer: none, minor_safe: true }
owner: monetization-designer
```
Review checklist for the spec: contents reproducible from config; no randomized element without odds; suppression covers tutorial, minors and recent purchase; the metric and sample size are written before launch.

## 16. Store layout rules
- Order: personalized offer, pass, currency ladder, convenience items, cosmetics. Put free rewards (daily claim) at the top so the store is a place players visit even when not buying.
- Show item contents and quantities explicitly; avoid cropped labels.
- Display each real price from the store API; show the "was" price only if it was truly the selling price in the recent past (many consumer authorities treat fake reference prices as deceptive; verify local rules).
- Keep the store reachable in two taps from the main screen; do not hide the way back.
- Provide a restore purchases button on iOS and a link to manage subscriptions.
- Accessibility: price and contents readable at large text settings; no information conveyed by color alone (see `accessibility-localization`).
- Localization: currency formatting from the store; legal copy translated.

## 17. Ethical review questions for every monetization feature
Ask in `design-review`; any "yes" in the first four needs redesign.
1. Does it rely on a player misunderstanding what they are buying, or what it costs?
2. Does it create pressure through false urgency, social shame or loss framing that is not real?
3. Would we be comfortable if the player saw the exact odds, the cost to complete and the offer logic?
4. Could a child or a person in a vulnerable state be harmed by it?
5. Can a player enjoy the whole game at a reasonable pace without paying, or is the free path an advertisement for paying?
6. Is there a spending visibility tool (history, limit)?
7. Does the monetization conflict with the fairness of competitive play?
8. Would the feature survive a regulator or journalist asking for explanations?

## 18. Region matrix example
Maintain as config, not code; flags are read by the client and server.
| Region | Paid random items | Odds screen | Age gate strictness | Link-outs | Notes |
|---|---|---|---|---|---|
| Belgium | off | n/a | standard | per platform | Treat as gambling regime |
| Brazil | off for minors; on for verified adults | on | strict | per platform | Verify age assurance method |
| EU (other) | on with odds | on | standard; parental gate for minors | per platform terms | Watch consumer-law developments |
| US | on with odds | on | COPPA-aware; state age laws | per platform and court status | Re-check quarterly |
| Australia | on; plan rating | on | rating-driven | per platform | Avoid simulated gambling features |
| Default | on with odds | on | standard | off until reviewed | Conservative fallback |
Fill the table from legal counsel, not from this file; this is a structure example, not a statement of law.
