# Business Models and Implementation

This file explains each mobile business model (premium, free-to-play, ads, hybrid, subscription, pass), then the implementation path for purchases (StoreKit 2, Google Play Billing, RevenueCat, server validation) and for ads (mediation with MAX, LevelPlay and AdMob, placements, frequency, consent with UMP and ATT, and families policy). Read it when you must choose a model, wire up purchases or ads, or review an existing integration. Volatile figures are collected at the end.

## Table of contents
1. Model deep dives
2. Model-fit worked example
3. Purchase architecture
4. StoreKit 2 notes
5. Google Play Billing notes
6. RevenueCat as the layer in between
7. Server validation and entitlements
8. Battle pass and subscription mechanics
9. Ad mediation
10. Placements and frequency
11. Consent: UMP and ATT
12. Families and kids policy
13. Integration test matrix
14. Volatile facts (as of Oct 2026 - verify)

## 1. Model deep dives

### 1.1 Premium
- Player pays once. Revenue = units x price x (1 - commission). No LTV tail except expansions.
- Works when the product is complete, distinctive and discoverable without paid UA. Reviews and featuring matter more than funnels.
- Decision: choose premium if session design is "finish it" rather than "return daily", and if the team can live with a spike-and-tail revenue curve.
- Pricing: anchor on comparable titles in the store, regionalize with store tiers, and avoid permanent heavy discounting that trains buyers to wait.
- Trials: a free demo or a free first chapter with a single unlock IAP ("freemium unlock") often beats a paywall on the store page; measure conversion of unlock per install.

### 1.2 Free-to-play with IAP
- Revenue from a minority of players buying currency, items, convenience or access.
- Requires: a core loop worth repeating, a meta economy with sinks, a content and event cadence, and a UA engine that tolerates a payback window.
- The design contract must state: what is free forever, what is purchasable, what is never purchasable (competitive fairness line).
- Typical components: starter pack, currency packs, time skips, battle/season pass, cosmetics, subscription "VIP", rotating offers.
- Sustainability: revenue concentrated in a few payers is fragile. Track the share of revenue from top 1 percent and top 10 percent of payers; if concentration climbs, widen the mid-tier (cosmetics, passes) instead of escalating whale offers.

### 1.3 Ad-supported
- Revenue = impressions x eCPM. Retention and session count dominate. Rewarded video is the most player-friendly unit; interstitials and banners are the volume units.
- Fits very short sessions and huge reach; hyper-casual economics depend on low CPI and rapid testing (see `marketing-ua`).
- The failure mode is ad load: every added interstitial buys short-term revenue and costs D1 and D7. Always test ad load against retention.

### 1.4 Hybrid (ads + IAP)
- Ads monetize the non-payer majority; IAP monetizes the minority. The cleanest design: IAP "Remove interstitials" bundle that includes a currency or boost, so the ad-averse become payers rather than churners.
- Segment ad load by payer state: payers see no interstitials (or only opt-in rewarded), non-payers see the normal load.
- Hybrid-casual means a hyper-casual core with a meta layer (collection, upgrades, events) that supports IAP. Reported hybrid IAP growth numbers conflict by source; do not quote them.

### 1.5 Subscription
- Auto-renewing product that grants recurring value: daily gems, ad-free, pass-like track, exclusive content.
- Works when the game has a daily habit and the sub's value is felt every week. Churn is the core metric; publish the value cadence in the paywall.
- Rules: renewal price and period must be clear; offer easy cancellation guidance; honor grace periods and billing retry; handle billing issues without removing access instantly where the platform provides grace.
- Free trials and intro offers: use store-native mechanisms; track trial-to-paid conversion and refund rate separately.

### 1.6 Season / battle pass
- A time-boxed reward track with a free lane and a premium lane. Premium lane unlocked by a one-time purchase (non-consumable-like per season) or by subscription entitlement.
- Value logic: player must be able to complete the track with reasonable play; show total value up front; offer tier-skip as optional convenience, with honest prices.
- Do not stack multiple passes with overlapping obligations; fatigue and refund risk rise.
- Implementation: model as a per-season entitlement with an expiry; grant premium rewards by server rule keyed on entitlement and progress, never on client claims.

## 2. Model-fit worked example
Game: a 3-minute-per-session puzzle game with a collection meta layer, daily events, audience in several regions.
1. Session length and cadence suggest ad-friendly: rewarded video for hints/continues, interstitial between levels after level 10.
2. The collection meta gives IAP a surface: starter pack, cosmetic sets, pass.
3. Choose hybrid. Specify: payer state "payer" suppresses interstitials; "Remove ads + monthly pack" SKU.
4. Soft-launch gates: D1/D7 targets from `genre-playbooks`; ad revenue per DAU and payer conversion measured per country; compare to CPI.
5. Decision at soft launch: if payer conversion is low but ad ARPDAU is healthy, tighten the pass and offers; if retention is below gates, remove interstitial load before touching prices.

## 3. Purchase architecture
```
Client (store SDK / RevenueCat SDK)
   -> store purchase sheet
   -> transaction / purchase token
Your backend
   -> validate with store server API (or RevenueCat webhooks)
   -> record transaction id (unique)
   -> grant entitlement / currency (idempotent)
   -> return new state to client
Store server notifications (App Store Server Notifications v2, Play RTDN)
   -> refunds, renewals, revocations, billing retry
   -> update entitlement, claw back if policy says so
```
Rules:
- The client never decides what was purchased; the server maps product id to grants from remote config.
- Grants are idempotent on `transaction_id` (Apple) or `purchase token / order id` (Google).
- Finish/acknowledge only after the grant is durable (otherwise lost purchases or auto-refund on Android).
- Keep product ids stable forever; change grants via config, not new ids.
- Store price is shown from store APIs (localized), never hard-coded.

## 4. StoreKit 2 notes
- Apple moved developers to StoreKit 2 (Swift concurrency-based API); the original StoreKit APIs are deprecated. Use `Product`, `Transaction`, `Transaction.updates` listener started at app launch.
- Always start a `Transaction.updates` listener at launch to catch purchases completed outside the app (Ask to Buy approvals, interrupted flows, offer codes).
- Verify the JWS signed transaction (`VerificationResult`) on device and on your server; server-side use the App Store Server API and App Store Server Notifications v2.
- Call `transaction.finish()` only after granting.
- Restore: for consumables there is no restore; for non-consumables and subscriptions use `Transaction.currentEntitlements` and `AppStore.sync()` when the user taps Restore.
- Subscriptions: subscription groups, introductory offers, promotional offers; check renewal state via status APIs.
- Refund handling: server notifications for refund and revoke; decide policy for consumed currency (see offers file).
- Unity/Godot: use a plugin or a service layer; keep a thin `PurchaseService` interface with `purchase(product_id)`, `restore()`, `entitlements()`, so the store can change (see `game-architecture`).

## 5. Google Play Billing notes
- Use a supported Play Billing Library major version; the platform enforces minimum versions for new apps and updates (see volatile facts).
- Flow: `queryProductDetails` -> `launchBillingFlow` -> `onPurchasesUpdated` -> validate on server -> grant -> `consumeAsync` for consumables or `acknowledgePurchase` for non-consumables and subscriptions.
- Unacknowledged purchases are refunded after the platform's acknowledgement window; always acknowledge after durable grant.
- Pending purchases (cash payments, slow methods): treat state PENDING as not paid; grant only on PURCHASED.
- Use obfuscated account ids so the store can tie purchases to a player identity without exposing it.
- Server: Google Play Developer API for purchase verification; Real-time Developer Notifications (RTDN) over Pub/Sub for lifecycle events.
- Subscriptions use base plans and offers; model trials and intro prices there.
- Reconnect logic: the billing client can disconnect; retry with backoff and reconcile unfinished purchases at app start.

## 6. RevenueCat as the layer in between
- Gives one SDK across iOS and Android, entitlements, offerings (remotely configurable paywall groups), receipt validation, webhooks and charts.
- Good fit for subscriptions, passes and non-consumable unlocks; consumable currency still needs your own grant ledger keyed by transaction id (use webhooks or the transaction history).
- Offerings let you change which packages appear without an app release; experiments on offerings give price tests with proper exposure assignment.
- Cost: a percentage of tracked revenue beyond a free tier; see volatile facts, verify current pricing.
- RevenueCat offers a hosted MCP server that can manage products, entitlements, offerings and store product state; useful for scripted setup (see research notes link at the end).
- Alternative: Unity IAP if everything stays in Unity and you accept running your own validation and analytics.
- Decision table:
| Need | Choose |
|---|---|
| Solo/small team, subs or pass, fast to ship | RevenueCat |
| Pure consumable-currency game, own backend | Native SDKs or Unity IAP + own validation |
| Strict data residency or no third party in the purchase path | Native + own backend |
| Need cross-platform entitlement across web shop | RevenueCat or own entitlement service |

## 7. Server validation and entitlements
Entitlement model (minimal):
```
Player { id, entitlements: [ {key, source, product_id, starts, expires|null, status} ] }
Ledger  { txn_id (unique), player_id, product_id, grants[], created, state }
```
Procedure for a consumable:
1. Client sends `{product_id, signed_txn}` to `/purchase/verify`.
2. Server verifies signature with store key chain or the store server API.
3. Check `txn_id` not in ledger; insert with state `granted` and apply grants in one transaction.
4. Return updated balances. Client finishes/consumes the transaction.
5. On refund notification: mark ledger `refunded`; apply policy (negative balance allowed, or deduct what remains, or flag account for review). Document the policy.
Fraud basics: replayed receipts (ledger uniqueness handles), jailbroken-client spoofing (server validation handles), chargeback abusers (flag repeat refunders), device/app attestation (Play Integrity, App Attest) for high-value flows.

## 8. Battle pass and subscription mechanics
Pass design parameters:
| Parameter | Typical decision |
|---|---|
| Length | Match the content cadence (weeks), not marketing preference |
| Tiers | Enough to feel progress every session; no dead stretches |
| Free lane | Real value, to keep non-payers engaged |
| Premium lane | Cosmetics, convenience, some currency that offsets the price (clearly stated) |
| Catch-up | Allow late buyers to claim back rewards or buy-in with accrued progress |
| Completion target | Reasonable for a typical engaged player; state hours estimate honestly |
| Tier skips | Optional, priced fairly, not required to finish |
Measure: pass attach rate among active players, completion rate, refund rate, retention lift of attached vs matched non-attached (beware selection bias: attached players were more engaged already; use holdouts or staggered rollouts where possible).

## 9. Ad mediation
- Mediation SDK sells your inventory across networks in real-time auctions (bidding) and sometimes waterfalls. Main options: AppLovin MAX, Unity LevelPlay, Google AdMob mediation.
- Decision table:
| Factor | MAX | LevelPlay | AdMob |
|---|---|---|---|
| Game-industry adoption | Very high in games | Strong, esp. Unity users | Strong, common in casual and apps |
| Unity integration | Good | Native fit | Good |
| Bidding | Yes | Yes (waterfall-only for Unity Ads ended; see volatile) | Yes |
| Reporting/API | Dashboard and APIs | Dashboard and APIs | Dashboard and APIs |
| Pick when | Maximum networks and tools, game-centric | You already use Unity services | You want Google ecosystem, simple setup |
- Do not run two mediation layers on top of each other without a reason; one mediator, many networks.
- Always include a fallback; test with the mediator's test mode; verify network adapters are current and have privacy manifests (iOS).
- Revenue reporting: reconcile mediator reports with MMP ad revenue events for ROAS (impression-level revenue where available).

## 10. Placements and frequency
Placement catalogue:
| Format | Placement | Rules |
|---|---|---|
| Rewarded video | Hint, continue, 2x reward, free daily chest, offer wall | Player-initiated; reward is clearly previewed; never gate core progression exclusively |
| Interstitial | After level complete, before next | Not in session 1; not mid-action; cap; cooldown after IAP |
| Banner | Menu screens only | Avoid in gameplay; accidental clicks hurt trust and may violate network policy |
| App open | Resume from background | Cool-off; avoid on first launch |
| Native / offerwall | Meta screens | Clear labelling |
Frequency design:
- Per-session cap, minimum seconds between interstitials, daily cap by cohort.
- Start conservative (for example, after a minimum level count and a minimum session count), then loosen by test against D1/D7 and ARPDAU.
- Suppress after purchases and for payers; suppress during tutorials and onboarding, and after a fail streak.
- Rewarded video availability should be visible (icon only when an ad is ready) so players do not tap dead buttons.
- Track: ads_shown per DAU by format, rewarded opt-in rate, ad ARPDAU, retention by ad-load tercile.
Worked example of an ad-load test: control caps interstitial to 1 per 120 seconds; variant to 1 per 180 seconds. Primary: D7 retention and total ARPDAU (ads + IAP). Use `scripts/ab_test.py` for sample size; stop only when guardrails and sample size are met.

## 11. Consent: UMP and ATT
- Google's User Messaging Platform (UMP) SDK handles GDPR/UK and US state consent messaging for ad personalization. Request consent info on every launch, show the form when required, and only then initialize ad SDKs that require consent. Mediators (MAX, LevelPlay) provide hooks to pass the consent state.
- Apple App Tracking Transparency: required before accessing the IDFA or tracking across apps. Add the usage description string; request after a value-first moment with a short custom explainer screen (no coercion, no rewards for accepting). Reported opt-in rates conflict by source, so plan economics without assuming a rate.
- Order of operations at launch: (1) age/audience determination, (2) UMP consent flow, (3) ATT prompt (iOS) at an appropriate moment, (4) initialize mediation and MMP, (5) first ad request.
- Persist consent and respect revocation (a settings entry to reopen the consent form is a requirement under many regimes).
- Privacy manifests (iOS): each SDK must declare data use; keep SDK versions updated.
- Without consent, serve non-personalized ads where allowed; revenue falls, but legality takes priority.

## 12. Families and kids policy
- If the app targets children, or children are a mixed audience, ad networks must be certified for it and flags set (child-directed treatment, under-age-of-consent). Both major stores publish families program rules; verify the current text before each release.
- Kids-directed apps generally cannot use behavioral advertising or collect identifiers for ads; use contextual ads only through families-certified networks, or no ads.
- Purchases in kids content: parental gate before any purchase flow or external link, no pressure messaging, no randomized paid items targeted at children.
- COPPA, GDPR-K and similar laws apply to data collection by ad SDKs; the app owner is responsible for SDK behavior.
- Practical approach: decide the audience first (design contract); if teen/adult only, use an age screen and never route minors into personalized ads.
- See `skills/legal-ethics/` and `scripts/compliance_preflight.py` for checklists.

## 13. Integration test matrix
| Case | Expected |
|---|---|
| Purchase success | Grant once, UI updates, ledger row |
| Purchase cancel | No grant, no error toast spam |
| Network drop mid-purchase | Recovered on next launch via update listener |
| Duplicate delivery of same transaction | Single grant |
| App killed after pay, before grant | Grant on restart |
| Refund notification | Ledger updated, policy applied |
| Subscription renew / lapse / billing retry | Entitlement matches store state |
| Ask to Buy / pending | No grant until approved |
| Restore on new device | Non-consumables and subs restored |
| Consent denied | No personalized ads, no crash |
| Ad no-fill | Graceful fallback, no stuck UI |

## 14. Volatile facts (as of Oct 2026 - verify)
- Mediation share: MAX, LevelPlay and AdMob together reported above 90 percent of mediation in 2025, with MAX above half; Unity LevelPlay ended waterfall-only support for Unity Ads in Jan 2026. Source: https://www.pocketgamer.biz/nine-facts-about-the-mediation-space-in-2025 and https://segwise.ai/blog/applovin-publisher-monetization-guide
- Ads vs IAP revenue share varies by region (reported ads majority in India, IAP majority in US/Japan/Korea/Canada, Jan-May 2026). Source: https://sensortower.com/blog/gaming-deep-dive-ad-monetization-report
- Google Play Billing Library: new apps and updates must use PBL 8 or higher from Aug 31, 2026 (extension requests to Nov 1, 2026 were reported); newer major versions recommended. Source: https://www.revenuecat.com/blog/engineering/play-billing-8-migration and https://developer.android.com/google/play/billing
- Apple: original StoreKit APIs deprecated in favor of StoreKit 2; server validation via App Store Server API and Notifications v2. Source: https://developer.apple.com/documentation/storekit
- RevenueCat: free tier then percentage of tracked revenue (commonly cited; verify). Hosted MCP exists. Source: https://www.revenuecat.com/pricing and https://www.revenuecat.com/docs/tools/mcp
- ATT opt-in rates reported with conflicting values (roughly 35 to 50 percent by source). Source: https://www.moburst.com/blog/idfa-att-update/
