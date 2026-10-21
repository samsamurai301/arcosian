# Payments Landscape 2026

This file describes how payments for mobile games are changing in 2026: Apple's EU terms under the Digital Markets Act, US link-outs on iOS and alternative billing on Google Play after the Epic cases, commission structures, and the rise of web shops. Almost everything here is volatile; the stable part is the decision method, which comes first. Read it before deciding whether to build a web shop, use alternative billing, or link out. Re-verify every number against the cited source before relying on it.

## Table of contents
1. Stable principles
2. Decision method for alternative payments
3. Web shop architecture
4. Margin model
5. Child-safety and consumer constraints
6. Operational checklist
7. Scenario table
8. Volatile facts (as of Oct 2026 - verify)
9. Open questions to re-check each quarter

## 1. Stable principles
- Rules about payments are regulatory and litigation driven; they shift every few months. Hard-code nothing: keep commissions, regions and feature flags in config.
- In-app purchase through the store is the baseline: simplest, trusted checkout, store handles tax, refunds and fraud. Anything else moves those duties to you or a payment provider.
- Savings from alternative payments are real only if the net margin after payment processing, tax handling, fraud, support and conversion loss is higher than store IAP. Conversion loss from leaving the app is often the largest term.
- Compliance is binary per platform: breaking steering or disclosure rules can lead to app rejection or removal. Follow the current guideline text for each platform and region.
- Players must not be misled: external payment pages need clear pricing, refund terms, and account linkage.
- Keep entitlement logic payment-source-agnostic: the same ledger records store purchases and web purchases (see `references/business-models-and-implementation.md`).

## 2. Decision method for alternative payments
1. List markets and platforms where alternatives are permitted and where you have meaningful revenue.
2. Compute potential gross savings: `revenue_in_region x (store_fee - alt_fee_total)`.
3. Subtract payment processor fees, tax compliance cost (merchant of record vs self), fraud and chargeback losses, support cost, build and maintenance cost.
4. Apply an estimated conversion factor (share of store buyers who would complete the web purchase). Run a pilot to measure; do not assume.
5. Add compliance cost: required disclosures, parental gates, regional restrictions.
6. Decide per region: stay IAP-only, add link-out for existing engaged players, or full alternative billing.
7. Re-evaluate quarterly or after a major ruling.
Break-even condition (simplified): `savings_rate x conversion_retained > added_costs_rate + lost_revenue_rate`, all as a fraction of regional gross.
Heuristic: web shops tend to pay off for games with established payers and high ARPPU, whose players already log in with an account, since checkout friction matters less to them. For small games, the engineering and support burden may outweigh savings.

## 3. Web shop architecture
```
Player account (cross-platform id)
   -> Web shop (hosted by you or a provider; merchant of record handles tax)
   -> Payment provider
   -> Webhook -> your entitlement/ledger service
   -> Game client syncs balances on launch/resume
```
Elements:
- Identity: players log in to the shop with the same account as the game; support deep links from the game to a prefilled shop session. Avoid putting personal data in URL query strings; use short-lived tokens.
- Catalog: shop products map to the same product ids and grants as in-app, with web-only bonuses where permitted.
- Tax and invoicing: use a merchant of record provider if you do not want to handle global sales tax and VAT.
- Fraud: card testing, stolen cards, chargebacks; add velocity limits and review.
- Refunds: web refunds are your responsibility; link to terms.
- Vendors: several providers specialize in games (for example Neonpay, Stash); evaluate fees, regions, and tax handling. Verify claims independently.
- Analytics: attribute web purchases to the player id and to the acquisition cohort so LTV and ROAS include them (see `marketing-ua`).
- Android distribution outside Play brings extra obligations such as developer verification in some regions; see volatile facts.

## 4. Margin model
For a single region, per 100 units of gross player spend:
| Line | Store IAP | Web shop |
|---|---|---|
| Platform commission | c_store | 0 or a reduced platform fee depending on rules |
| Payment processing | included in commission | p% + fixed per transaction |
| Tax handling | included (store remits) | merchant-of-record fee or in-house cost |
| Fraud/chargebacks | mostly store | you |
| Support | shared | you |
| Conversion retained | 100% | k% of IAP buyers (measured) |
Net per 100 of potential spend: `store = 100 x (1 - c_store)`; `web = 100 x k x (1 - fees - fraud - tax_cost - platform_fee)`. Fill with your own data. A pilot with 5 to 10 percent of eligible users gives an empirical k.
Incentive design: web-only bonuses (extra currency) are the lever that raises k; they cost margin but can stay positive. Keep the bonus ethical: no pressure, same item pool, honest comparison. Check that steering messages comply with the current platform rule text in each region.

## 5. Child-safety and consumer constraints
- External payment and link-outs have restrictions for children's apps on at least one major platform in the EU (see volatile facts). Treat kids and under-13 audiences as no-link-out by default, and add a parental gate for minors where alternative payments or link-outs are allowed.
- Age assurance: use platform age signals plus your own screen; do not show the web shop link to unverified minors.
- Consumer law applies to web sales: clear total price, taxes, withdrawal rights where required, receipts, contact info.
- Subscriptions sold on the web must provide a clear cancellation method.
- Privacy: a web shop is another data processor; update privacy notices and store questionnaires.

## 6. Operational checklist
- [ ] Region and platform eligibility table in config.
- [ ] Entitlement service accepts multiple payment sources and is idempotent.
- [ ] Shop terms and refund policy published and linked.
- [ ] Parental gate and age rules implemented.
- [ ] Tax and invoicing handled (provider or own).
- [ ] Webhook signature verification and retry handling.
- [ ] Fraud rules and chargeback workflow.
- [ ] Analytics join between web purchases and in-game player id.
- [ ] Legal review of steering/link text per platform and region.
- [ ] Rollback plan: ability to turn off link-outs by remote config within minutes.

## 7. Scenario table
| Scenario | Likely direction | Why |
|---|---|---|
| New indie, small payer base, global audience | IAP via RevenueCat or native | Savings small, engineering heavy |
| Mid-size F2P with strong US payer base, accounts, events | Pilot US link-out/web shop for lapsed or engaged payers | Rules permit link-outs; ARPPU high |
| Large game, EU audience on iOS | Evaluate EU terms; compare IAP, alt PSP, link-out fees | Terms offer multiple models; compute net |
| Kids or mixed-age audience | Stay IAP with parental gates | Restrictions on link-outs for minors |
| Android audience, US | Evaluate alternative billing and external links under the court-ordered changes | Rules in flux; verify current fee schedule |
| Subscription app-like game | Test web checkout for new subs; keep IAP | Subs benefit from lower fees, but churn handling on web is manual |

## 8. Volatile facts (as of Oct 2026 - verify)
US, Apple:
- Link-outs are allowed. The Ninth Circuit (opinion dated Dec 11, 2025) upheld a contempt finding about Apple's 27 percent commission on linked-out purchases but rejected a zero-commission bar; Apple may charge only a fee based on costs genuinely and reasonably necessary for coordinating external links, with the rate remanded to the district court. Sources: https://law.justia.com/cases/federal/appellate-courts/ca9/25-2935/25-2935-2025-12-11.html and https://www.courthousenews.com/ninth-circuit-confirms-contempt-finding-against-apple-in-epic-games-battle/
- The Supreme Court granted review (No. 25-1311); Apple filed its merits brief on Sep 14, 2026; no decision as of the research date; the remand on the fee rate was reported stalled. Whether Apple is currently charging any US link-out fee was not confirmed. Source: https://www.supremecourt.gov/DocketPDF/25/25-1311/424150/20260914154510009_2026-09-14%20No.%2025-1311%20Apple-Epic%20Merits%20Opening%20Brief.pdf and https://www.techtimes.com/articles/327527/20260915/app-store-commission-limbo-enters-new-phase-apples-epic-merits-brief-opens-scotus-fight.htm
EU, Apple (new terms effective Oct 1, 2026, per Apple; the rates and child-safety rules below were checked on 2026-10-20 against Apple's newsroom post dated Aug 18, 2026, which gives the date as "October 1" without the year):
- In-app purchase 26 percent standard / 15 percent reduced rate; alternative payment service provider 20 percent / 10 percent; link-out 15 percent / 10 percent; a 5 percent Core Technology Commission for apps distributed outside the App Store (replacing the per-install Core Technology Fee).
- Child-safety: no link-outs in Kids category or under-13 apps; parental gate for under-18 apps that use alternative payments or link-outs.
- Sources: https://www.apple.com/newsroom/2026/08/apple-announces-changes-for-apps-in-the-european-union/ and https://developer.apple.com/support/apps-in-the-eu/
- Which tier (standard or reduced) applies to a given developer depends on Apple's program criteria; read the source.
US, Google Play:
- Under the Oct 2024 Epic permanent injunction, Google no longer requires Play Billing in the US and permits alternative payments and external links; third-party stores get access to the Play catalog from July 22, 2026 (as reported).
- Proposed fees reported in Dec 2025: 10 percent on auto-renewing subscriptions and 25 percent on other IAP for alternative billing; 10 percent and 20 percent for external links. A March 2026 analysis says the Epic-Google settlement does not fix these rates. As of June 2026 the settlement was not yet approved; a roughly 700 million dollar states/consumer settlement received final approval in Aug 2026. The authoritative current fee schedule was not confirmed.
- Sources: https://www.neonpay.com/blog/google-plays-new-u.s.-billing-linking-policies-what-game-developers-need-to-know , https://www.stash.gg/blog/blog-epic-v-google-settlement-update-april-2026 , https://www.pymnts.com/cpi-posts/judge-approves-googles-700-million-play-store-settlement/
Android sideloading:
- Developer verification (app registration) is enforced on certified devices in Brazil, Indonesia, Singapore and Thailand from Sep 30, 2026, with global rollout in 2027; relevant to off-Play distribution. Source: https://www.androidauthority.com/p-3679204/ (blocks automated fetches; not re-checked on 2026-10-20).
Play Billing:
- Play Billing Library 8 or higher required for new apps and updates from Aug 31, 2026 (extension to Nov 1, 2026 reported). Source: https://www.revenuecat.com/blog/engineering/play-billing-8-migration
Web-shop vendors: Neonpay and Stash track these rules on their blogs: https://www.neonpay.com/blog/the-latest-on-alternative-payments-for-android-in-the-u-s and https://www.stash.gg/blog/epic-v-google-january-hearing-injunction-android-developers

## 9. Open questions to re-check each quarter
1. Has the Supreme Court decided No. 25-1311, and what fee, if any, applies to US iOS link-outs?
2. What is Google's current US fee schedule for alternative billing and external links after settlement approval?
3. Which Apple EU fee tier applies to us, and has the Commission acted further?
4. Have other regions (for example Japan, South Korea, UK, Brazil) imposed rules that open or restrict alternatives?
5. Do platform guideline texts on steering and link wording still match our in-game copy?
6. Is our measured web-shop conversion factor k still above break-even?
7. Are chargeback and fraud rates within budget?
Procedure: assign the check to `arcosian:monetization-designer` quarterly, record outcomes in `.gamestudio/` notes, and update the config flags rather than code.

## 10. Worked margin example (illustrative numbers only)
These numbers are invented to show the arithmetic; replace with your own and the current fees in section 8.
Assume per 100 units of potential regional gross spend:
- Store IAP path: commission 30 (use the fee that applies to you), net 70.
- Web shop path: platform fee 0 (if permitted), processor and merchant-of-record fees 8, fraud and chargebacks 1, support 1; conversion retained k = 0.80 (not all buyers follow the link). Net = 100 x 0.80 x (1 - 0.10) = 72.
Result: nearly break-even, so the web-only bonus must be small, and the saving disappears if k falls to 0.75 (net 67.5).
Now assume a lower store fee (15, small-business or reduced tier): store net 85; web net at k = 0.80 is still 72. Web loses. The conclusion flips with the applicable commission, which is why the decision needs a per-region calculation.
Sensitivity to run: vary k from 0.5 to 1.0 and fee from 10 to 30; plot net difference; find the minimum k that makes web profitable. Use `${CLAUDE_PLUGIN_ROOT}/scripts/retention_ltv.py` style spreadsheet thinking but keep this model in a simple table.
Takeaway: the answer depends mostly on k and on the fee that actually applies to you. Pilot to measure k.

## 11. Pilot design
1. Eligibility: engaged players with an account, in a permitted region, not minors, not in a kids audience.
2. Exposure: 5 to 10 percent holdout of eligible players sees the link; the rest do not. Randomize by player id.
3. Measure: share completing web purchase; total spend per exposed player vs control (total includes IAP, so cannibalization is visible); refund and chargeback; support contacts; retention.
4. Duration: long enough to cover a pay cycle and one event; payer conversion is rare, so size with `ab_test.py`.
5. Decision: ship wider only if spend per exposed player (net of fees) beats control with margin and guardrails are flat.
6. Document the result and the date: the answer will change when rules change.
Link wording: factual, not pressuring; no claims that the store route is unsafe; do not hide the in-app option. Check against the current platform rules for allowed wording and placement before every release.

## 12. Vendor evaluation criteria
| Criterion | Questions |
|---|---|
| Fees | Processing percentage and fixed fee; merchant-of-record fee; payout schedule |
| Tax | Do they remit sales tax and VAT in your markets? Invoicing? |
| Regions | Supported countries and payment methods (cards, wallets, local methods) |
| Games fit | SDK or hosted store; login with your account system; item catalog sync |
| Fraud | Tools, chargeback support, liability |
| Entitlement | Webhooks, idempotency, signature verification, retries |
| Compliance | Age gating hooks, parental consent support, data processing agreement |
| Exit | Can you export customers and transactions? Lock-in risk |
| Reliability | Status history, support responsiveness |
Pick two to pilot only if the first fails. Do not sign long contracts before measuring k.

## 13. Config schema sketch
Keep eligibility flags remote-controlled so a ruling or a policy rejection can be handled without a release.
```json
{
  "payments": {
    "regions": {
      "US": { "ios_linkout": true, "android_alt_billing": false, "android_external_link": true },
      "EU": { "ios_linkout": false, "ios_alt_psp": false },
      "default": { "ios_linkout": false, "android_alt_billing": false, "android_external_link": false }
    },
    "minors": { "linkouts": false, "parental_gate_required": true },
    "web_shop_url_template": "set at build time; no personal data in the query string",
    "kill_switch": false
  }
}
```
Rules: default is conservative (off); a kill switch exists; flags are logged on each purchase to explain which path was shown.

## 14. Risk register
| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Ruling reverses a permitted path | Medium | Feature must be disabled quickly | Remote flag, kill switch, IAP fallback |
| Fee imposed on link-outs after remand | Medium | Margin shrinks | Re-run margin model; keep IAP path healthy |
| App rejected over link wording | Medium | Release delay | Pre-review copy against current guidelines; staged rollout |
| Fraud on web shop | Medium | Chargebacks | Velocity limits, provider tools |
| Players confused by two paths | Medium | Support load | Clear comparison, same items, one account |
| Minor reaches web shop | Low if gated | Legal and reputational | Age signals, parental gate, block when unsure |
| Vendor outage or exit | Low | Revenue pause | Multi-vendor abstraction at the webhook layer |
| Tax miscalculation | Medium | Liability | Merchant of record |
Ownership: the `monetization-designer` agent maintains the register; `compliance-officer` reviews wording and age handling before each release.

## 15. Sequencing recommendation
1. Ship with store IAP and a clean ledger and entitlement service (no payment-source assumptions).
2. Instrument funnel and regional revenue so the margin model has real inputs.
3. When payers and revenue justify the effort, run the pilot in one region where rules are clear and stable enough.
4. Expand region by region, never globally in one release.
5. Keep reviewing legal status; treat any pending litigation as a reason to preserve the fallback path.

## 16. Glossary
| Term | Meaning |
|---|---|
| Link-out | A button or link in the app that sends the player to an external web page to buy |
| Alternative billing | Taking payment inside the app through a non-store payment provider where the platform allows it |
| Alternative PSP | A third-party payment service provider used in place of the store's payment system |
| Merchant of record | The entity legally selling to the customer and handling tax and invoicing |
| Steering | Telling players about cheaper or other purchase options; platform rules restrict or permit it by region |
| Core Technology Commission | Apple's EU fee on apps distributed outside the App Store (see volatile facts) |
| RTDN / Server Notifications | Store-to-server messages about renewals, refunds, revocations |
| Entitlement | A server-side record that a player owns something (pass, no-ads, subscription) |
| k (retained conversion) | Share of would-be store buyers who complete the external purchase |
