# Ethics and Dark Patterns

The studio's operational ethics for player psychology: what a dark pattern is, the published taxonomies (Zagal, Björk & Lewis 2013; deceptive.design; academic UX and monetisation taxonomies), a game-specific catalogue of patterns in four categories (temporal, monetary, social, psychological), each with detection signals and an ethical alternative, the regulatory exposure they create, the studio's explicit red lines, rules for minors, problematic play and wellbeing design, and a review procedure with a scorecard. Doctrine item 8 ("Ethical monetization: no dark patterns, transparent odds, respect for minors") is enforced through this file: the red lines in §6 belong in every `contract.monetization.ethics` list, and `skills/player-psychology/scripts/psych_check.py redlines` checks a contract for the machine-checkable ones. Legal interpretation belongs to `legal-ethics` and `arcosian:compliance-officer`; this file is design policy, not legal advice.

## Contents

1. Why this is a design discipline
2. Definitions: persuasion, manipulation, coercion, dark pattern
3. Published taxonomies
4. Game dark-pattern catalogue (temporal, monetary, social, psychological)
5. Regulatory exposure (stable principles)
6. Studio red lines (binding)
7. Volatile regulatory facts (as of Oct 2026 — verify before relying)
8. Minors
9. Problematic play and wellbeing design
10. Ethical monetization patterns that work
11. Ethics review procedure and scorecard
12. Sources

---

## 1. Why this is a design discipline

- **Player first** is doctrine item 1. A pattern that wins a metric by undermining the player's informed choice is a design defect, the same as a crash.
- **Trust compounds.** Players who feel tricked churn, refund, review-bomb and warn others; trust lost in one feature taints every offer after it.
- **Regulatory and platform risk is real and growing**: consumer-protection enforcement, loot-box rules, children's privacy law and store policies (§5, §7). A pattern that is legal in one storefront can block a launch in another.
- **Measured short-term wins often hide long-term losses.** A/B tests that optimise next-week revenue rarely measure trust, refunds, regulatory risk or long-term retention. The studio decides on the longer horizon (`behavioral-economics-in-games.md` §24).

---

## 2. Definitions: persuasion, manipulation, coercion, dark pattern

| Term | Working definition | Game example |
|---|---|---|
| **Persuasion** | Influencing choice by giving reasons or making options attractive while the player can still evaluate them | Showing exactly what a bundle contains and why it is good value |
| **Manipulation** | Influencing choice by bypassing or exploiting the player's reasoning (hiding information, exploiting biases, timing to vulnerability) | A fake countdown on an offer shown right after a loss |
| **Coercion** | Removing reasonable alternatives or imposing penalties for not complying | "Pay or lose your base"; progress impossible without inviting friends |
| **Dark pattern** | An interface or system design that benefits the studio by undermining the player's informed, autonomous decision, or by exploiting a vulnerability | Disguised ads, pre-ticked purchases, near-miss loot reveals |

The term "dark patterns" was coined by UX designer Harry Brignull in 2010; his catalogue now lives at deceptive.design under the name "deceptive patterns". The studio uses "dark pattern" in internal documents because it is the established term in game research.

**Intent is not the test; effect is.** A pattern created innocently (for example a decline button that happens to be low-contrast) is still a dark pattern if it misleads. Review the build, not the intentions.

---

## 3. Published taxonomies

### 3.1 Zagal, Björk & Lewis (2013): dark patterns in game design
José Zagal, Staffan Björk and Chris Lewis ("Dark Patterns in the Design of Games", *Foundations of Digital Games* 2013) defined a game dark pattern as a pattern used intentionally by a game creator to cause negative experiences for players that are against their best interests and likely happen without their consent. They grouped examples into:

| Category | Examples they discuss (paraphrased) |
|---|---|
| **Temporal** | *Grinding* — padding with repetitive tasks to stretch play time; *Playing by appointment* — forcing play at times the game dictates |
| **Monetary** | *Pay to skip*; *Pre-delivered content* — content shipped in the game but locked behind payment; *Monetized rivalries* — exploiting competitiveness to drive spending |
| **Social capital-based** | *Social pyramid schemes* — progress requiring recruitment of friends; *Impersonation* — the game acting or posting as the player |

### 3.2 Four-category game catalogues
Community-maintained catalogues of game dark patterns (notably darkpattern.games) organise patterns into **temporal, monetary, social and psychological** categories and rate individual games against them. The studio adopts the same four categories for its own catalogue (§4). Entries in community catalogues change over time; consult the site directly rather than relying on a copied list.

### 3.3 deceptive.design (Brignull)
Brignull's catalogue describes general interface patterns that apply to game stores, onboarding and settings. Types it covers include (paraphrased): hidden costs, fake urgency, fake scarcity, fake social proof, confirmshaming, nagging, obstruction (hard to cancel or leave), preselection, sneaking items or costs in, trick wording, visual interference, disguised ads, forced action and comparison prevention. It also catalogues regulatory cases.

### 3.4 Academic taxonomies worth knowing
| Work | Contribution | Use |
|---|---|---|
| Gray, Kou, Battles, Hoggatt & Toombs (2018), CHI | Five strategies: nagging, obstruction, sneaking, interface interference, forced action | Reviewing UI flows (settings, cancellation, consent) |
| Mathur et al. (2019), CSCW | Large-scale crawl of shopping sites; categories incl. sneaking, urgency, misdirection, social proof, scarcity, obstruction, forced action | Store and offer reviews |
| Petrovskaya & Zendle (2022), *Journal of Business Ethics* ("Predatory Monetisation?") | Player-perspective categorisation of monetisation techniques perceived as unfair, misleading or aggressive | Monetisation reviews; player-language for surveys |
| King, Delfabbro et al. (2019) on "predatory monetization schemes" | Framing of schemes that disguise or withhold long-term cost and exploit information asymmetry | Policy discussions; high-spender protections |

---

## 4. Game dark-pattern catalogue

Each pattern has an id for use in reviews and `gate_notes`. **Grade**: R = red line (never), A = amber (only with listed safeguards and sign-off). "Detect" lists where a reviewer or agent finds it: design docs (D), build/UI (B), telemetry (T).

### 4.1 Temporal

| ID | Pattern | Detect | Harm | Ethical alternative | Grade |
|---|---|---|---|---|---|
| T1 | **Padding / grinding** — repetitive tasks added to stretch time, not to create play | D: content-hours targets with no new decisions; T: rising session time with falling enjoyment ratings | Wasted time; resentment | Variety, new decisions per hour; shorten, don't stretch | A |
| T2 | **Playing by appointment** — rewards lost unless the player returns at set times | D: windows < 12 h; B: "come back in 2 h or crops wither" | Life intrusion; anxiety | Rewards wait for the player (no wither); generous windows | A (R if loss of owned items) |
| T3 | **Punitive streaks** — long streaks reset to zero on one miss | D/B: streak counter with full reset | Obligation; anxiety; churn on break | Grace days, freezes earned by play, decay not reset | A |
| T4 | **Daily obligation stacks** — daily lists that take longer than a normal session | D: sum of daily tasks > target session length | Chore play | Cap dailies at one session; tasks bank for several days | A |
| T5 | **Energy walls tuned to sell** — energy caps whose main function is conversion | D: energy design notes cite conversion, not pacing; T: purchase spikes at energy zero | Frustration selling | Energy as pacing only, with generous refills; or no energy | A |
| T6 | **Can't-stop design** — no pause/save; sessions with no natural break | B: no save mid-level; levels > 10 min on mobile without checkpoints | Interruptions cause loss; binge structure | Autosave every action; natural stops every 2–5 min | R for no-save on mobile |
| T7 | **Power-exclusive FOMO** — gameplay power only available in short windows | D: event-exclusive power items | Pressure; competitive unfairness | Cosmetic exclusives; power returns in later rotations; catch-up | A |
| T8 | **Fake urgency** — timers that reset, or "last chance" offers that recur | B/server: timer restarts; offer recurrence logs | Deception | Truthful timers; stated recurrence policy | R |
| T9 | **Return penalties** — owned items decay or vanish while away | D/B: decay of owned items, base raids while offline without protection | Hostage-taking | Welcome-back gifts; offline protection | R |
| T10 | **Notification pressure** — frequent, guilt-laden or late-night pushes | B: > 1 non-transactional push/day default; copy like "Your team needs you!" at night | Intrusion; guilt | Opt-in, ≤ 1/day default, quiet hours, value-bearing copy | A (R for minors at night) |

### 4.2 Monetary

| ID | Pattern | Detect | Harm | Ethical alternative | Grade |
|---|---|---|---|---|---|
| M1 | **Pay-to-skip padding** — timers lengthened to sell skips | D: timer lengths set by skip-conversion targets | Impatience selling | Timers justified by pacing; transparent skip prices | A |
| M2 | **Pay-to-win in competitive modes** — purchased power decides PvP outcomes | D/T: win rate vs spend in PvP | Unfairness; competence frustration | Cosmetic or convenience monetisation; power-matched brackets | R in ranked PvP; A elsewhere |
| M3 | **Currency obfuscation** — premium currency hides real cost | B: no real-money equivalent near spend buttons | Spending without understanding | Real-money equivalent shown; confirmation threshold | R if no equivalent anywhere |
| M4 | **Multiple premium currencies** | D: > 1 purchasable currency | Mental-accounting confusion | One premium currency; earned-only tokens | R |
| M5 | **Engineered leftovers** — pack sizes mismatched to prices | D: leftover analysis (`behavioral-economics-in-games.md` §20) | Forced re-purchase | Pack sizes matched to common item prices | R |
| M6 | **Opaque paid randomness** — paid random items without odds, pity or caps | B: no odds before purchase | Gambling-like harm; legal risk | Direct purchase; or full disclosure + pity + caps (adults) | R without odds; A with safeguards; R for minors |
| M7 | **Escalating continues** — continue price rises within a run | B: second continue costs more | Sunk-cost exploitation | Fixed, pre-announced price; max one per attempt | R |
| M8 | **Frustration-triggered offers** — offers on loss, fail streak, out-of-resources | D/B: offer triggers; T: purchase share after failure | Exploiting vulnerability | Offers in neutral contexts (shop, level select); free help after fails | R |
| M9 | **Fake discounts / anchors** — reference prices never charged; unreproducible "value %" | B: compare claims with catalogue | Deception; legal risk | Real reference prices; published value formula | R |
| M10 | **Pre-delivered content** — content complete in the build but locked behind payment without disclosure | D: shipped-locked content plan | Feels like extortion when undisclosed | Disclose what is premium at purchase/download; premium unlock bundles | A |
| M11 | **Hidden or confusing subscriptions** — unclear price, period or auto-renewal | B: subscription screen review | Unwanted charges; regulatory exposure | Price, period, renewal and cancel path on the purchase screen | R if unclear |
| M12 | **Obstruction / hard to cancel** — cancellation or ad-free restoration buried | B: steps to cancel/restore > steps to buy | Trapped spending | Cancel and restore reachable from settings in ≤ 3 taps (deep link to store management) | R |
| M13 | **Accidental-purchase design** — purchase buttons where gameplay buttons usually are; no confirmation | B: offer buttons in gameplay positions; one-tap premium spend | Unwanted purchases (especially children) | Purchase UI visually distinct and in separate regions; confirmation | R |
| M14 | **Exploitative personalisation** — offers priced up by spend history or vulnerability signals | D: segmentation rules using spend velocity to raise prices | Price discrimination against impulsive players | Personalise by preference (content type), not by willingness to overspend; suppression rules | A (R for minors; R when targeting problem signals) |
| M15 | **Last-step paywall** — collection or event finale only purchasable | D/T: completion spike at "one short" | Goal-gradient exploitation | Every reward path completable through play | R |
| M16 | **High-spender pressure programmes** — account managers or VIP tiers pushing spend | D: VIP programmes with spend targets | Harm concentrated on most vulnerable spenders | VIP = service and recognition, never spend targets; spend checks | R for spend targets |
| M17 | **Disguised or forced ads** — ads styled as content; interstitials mid-play; fake close buttons | B: ad placement review | Deception; flow destruction | Rewarded opt-in ads with caps; interstitials only at natural breaks after FTUE | R for disguised/mid-play |
| M18 | **Monetised rivalries** — engineered grudges and spend-to-retaliate loops | D: revenge offers after PvP loss | Exploiting anger | Matchmaking fairness; no revenge offers | R |

### 4.3 Social

| ID | Pattern | Detect | Harm | Ethical alternative | Grade |
|---|---|---|---|---|---|
| S1 | **Social pyramid** — progress requires recruiting friends | D: gates requiring invites | Exploits relationships; excludes solo players | Solo path to all progress; invites optional with symmetric rewards | R if mandatory |
| S2 | **Friend spam / contact harvesting** | B: contact upload prompts; auto-invites | Privacy harm; social embarrassment | Explicit, per-invite consent; no contact upload by default | R for auto-posting/uploading |
| S3 | **Impersonation** — posting or messaging as the player without explicit action | B: auto-posts | Deception; reputational harm | Every share is explicit, previewed and user-initiated | R |
| S4 | **Obligation guilt** — team UI that blames inactive members; kick pressure | B: public "inactive" shaming; T: churn after kicks | Introjected regulation; anxiety | Contribution recognition, not blame; flexible team expectations | A |
| S5 | **Fake social proof** — fabricated purchase feeds, bots as friends | B/server: generated activity | Deception | True aggregated data only; disclose bots | R |
| S6 | **Humiliating comparison** — global leaderboards that bury most players; public failure | D/B | Performance-avoidance; shame | Brackets, neighbourhood views, private modes (`motivation-models.md` §10) | A |
| S7 | **Gifting as pressure** — gifts that create debts or nag | B: "X sent you a gift — send one back!" repeated | Obligation | Gifts without reciprocity prompts; batch claiming | A |
| S8 | **Unmitigated toxicity** — no tools against harassment | B: missing mute/report/block | Need frustration; harm | Default-safe chat, quick mute/report, moderation (see `multiplayer-backend`) | R for no tools in chat games |

### 4.4 Psychological

| ID | Pattern | Detect | Harm | Ethical alternative | Grade |
|---|---|---|---|---|---|
| P1 | **Engineered near-miss** on random outcomes | B: reveal animations; frame-frequency audit | Gambling-like urge | Honest reveals; near-miss info only for skill outcomes | R |
| P2 | **Confirmshaming** — guilt-laden decline copy | B: decline button copy | Manipulation | Neutral "Not now" / "No thanks" | R |
| P3 | **Nagging** — repeated popups after decline | B/T: same offer shown again in session | Attrition of resistance | Max one offer popup per session; respect decline for ≥ 24 h | A (R if after decline in-session) |
| P4 | **Hostage investment** — player creations or progress held for ransom | D/B | Coercion | Creations persist; no restore fees | R |
| P5 | **Endowed-progress trickery** — fake pre-fills, bars that slow near the end | B: bar rate audit | Deception | Accurate bars; honest head starts | R |
| P6 | **Complete-the-collection via paid randomness** | D: final items only in paid random pools | Goal-gradient + VR exploitation | Duplicate protection, crafting from duplicates, direct purchase or play paths | R |
| P7 | **Illusion of control** — skill-looking inputs on predetermined random outcomes ("tap to stop the wheel") | B: input doesn't affect outcome | Deception | If outcome is random, present it as random | R |
| P8 | **Visual interference** — decline/close hidden, tiny, low contrast, delayed | B: contrast and size of close buttons; close-button delays | Obstruction | Close button same prominence as accept, visible immediately | R |
| P9 | **Trick wording** — double negatives, misleading labels | B: copy review | Deception | Plain, literal copy; read-aloud test | R |
| P10 | **Sunk-cost copy** — "Don't waste your progress!" at decision points | B | Exploitation | Factual copy | R |
| P11 | **Mid-play attention hijack** — offers or popups during active play | B/T | Flow destruction; impulsive choices | Offers at natural breaks only | R |
| P12 | **Manufactured difficulty spikes** paired with offers | D/T: spikes coincide with offer triggers | Frustration selling | Fair curves; spikes decoupled from monetisation | R |
| P13 | **Spend-dependent difficulty** — difficulty or drop rates secretly adjusted by spend | D/server | Deception; unfairness | Difficulty independent of spending (declare it in ethics) | R |
| P14 | **Misleading marketing creatives** — ads showing gameplay that is not in the game | D/B: creative vs build comparison | Deception; regulatory action | Creatives show real gameplay or are clearly labelled concept (`marketing-ua`) | R |
| P15 | **Variable-reward compulsion core** — the core loop only works because of random reward | D: removal test fails (`design-theory`) | Wanting without liking | Rebuild around mastery, curiosity, expression | R |

---

## 5. Regulatory exposure (stable principles)

Dark patterns create legal exposure under several overlapping regimes. The principles below are stable; specific deadlines, cases and thresholds are volatile and live in §7. Always route concrete questions to `legal-ethics` and `arcosian:compliance-officer`.

| Regime | What it targets | Patterns most exposed | Notes |
|---|---|---|---|
| **General consumer protection** (e.g. US FTC Act §5 on unfair or deceptive practices; EU Unfair Commercial Practices Directive 2005/29/EC on misleading and aggressive practices) | Deception, omission of material information, aggressive pressure | M3, M9, M11, M12, M13, T8, P2, P8, P9, P14 | The UCPD's Annex I blacklist includes directly exhorting children to buy advertised products or to persuade adults to buy them for them |
| **Platform interface rules** (e.g. EU Digital Services Act Art. 25 on deceptive interface design for online platforms) | Interfaces that deceive or manipulate users | Store and social UI patterns | Whether a given game is an "online platform" under the DSA depends on its features (user-generated content, marketplaces); verify |
| **Children's privacy and design** (US COPPA; GDPR Art. 8; UK Age Appropriate Design Code) | Data collection from children, nudge techniques, default settings | S2, T10, M14, personalised ads | The UK code includes a standard against nudge techniques that lead children to weaken privacy |
| **Gambling law** | Staking value on chance for a prize of value | M6, P1, P6, social casino | Classification varies by jurisdiction and by whether items can be cashed out or traded |
| **Platform store policies** (Apple App Review Guidelines, Google Play policies) | Odds disclosure for paid random items, kids categories, ads in kids apps, subscription clarity | M6, M11, M17 | Enforced at review; violations block release (see `store-release`) |
| **Age ratings** (IARC, ESRB, PEGI, regional boards) | In-game purchase and random-item disclosures; gambling-like content | M6, social casino | Ratings affect store visibility and some legal obligations |
| **Advertising standards** (e.g. UK advertising codes) | Misleading ads, ads aimed at children | P14, M17 | Mobile game creatives have been subject to regulator rulings; see `marketing-ua` |

**Design principle that minimises exposure across regimes.** Fixed-content, direct-purchase monetisation (cosmetics, bundles with stated contents, passes with visible rewards, premium unlocks, remove-ads), transparent prices in real money, neutral UI, and protections that switch on for minors and unknown ages.

---

## 6. Studio red lines (binding)

These rules are non-negotiable for every game the studio builds. Copy the relevant ones into `contract.monetization.ethics` (verbatim ids help reviews: "RL-05: no offers triggered by failure ..."). `python3 ${CLAUDE_PLUGIN_ROOT}/skills/player-psychology/scripts/psych_check.py redlines --contract .gamestudio/contract.json` checks the machine-checkable subset.

**Randomness and odds**
- **RL-01** No paid random items (loot boxes, gacha pulls, paid spins) for players under 18 or of unknown age. Unknown age is treated as a minor for this purpose until a reliable age signal exists.
- **RL-02** No paid random item without, before purchase and on the same screen: odds per item or rarity tier in percentages, the pity rule in plain words, and the real-money price.
- **RL-03** No engineered near-misses and no illusion-of-control inputs on random outcomes.

**Pressure and timing**
- **RL-04** No fake urgency or scarcity: every timer is truthful and server-enforced, no stock counts on digital goods, no recurring "last chance" offers.
- **RL-05** No offers triggered by failure, loss, streak break or resource depletion, and no offers, ads or rating prompts during active play.
- **RL-06** No escalating continue or revive prices within a run or level; the price is shown before the decision, with at most one paid continue per attempt.

**Prices and currencies**
- **RL-07** At most one purchasable premium currency; real-money equivalent shown wherever it is spent; explicit confirmation for any spend equivalent to USD 5 or more.
- **RL-08** No engineered leftovers, no fictitious reference prices, and every "value", "best" or "popular" claim reproducible from the game's own data.

**Fairness**
- **RL-09** Difficulty, drop rates and matchmaking never secretly depend on spending.
- **RL-10** No purchasable power that decides outcomes in ranked PvP.
- **RL-11** Every reward path (collections, events, passes' free tracks) is completable through play; no last-step paywalls.
- **RL-12** No decay, deletion or ransom of player-owned items, progress or creations.

**Honest interface**
- **RL-13** No confirmshaming, trick wording, hidden, tiny, low-contrast or delayed close/decline buttons.
- **RL-14** No disguised ads; no interstitials during active play or before the FTUE is complete; rewarded ads are opt-in and capped.
- **RL-15** No fabricated social proof; bots are disclosed in help/FAQ and never used in purchase-related social proof or presented as specific real people.
- **RL-16** No mandatory friend recruitment, no contact upload by default, never post or message as the player without an explicit, previewed action.
- **RL-19** No marketing creative showing gameplay not in the game, unless clearly labelled.

**Vulnerable players**
- **RL-17** No personalised offers to minors; no offer targeting based on problematic-spending signals; no VIP or account-management programmes with spend targets.
- **RL-21** Push notifications are opt-in; none to minors during quiet hours (studio default 21:00–08:00 local time).
- **RL-24** No direct exhortation to children to buy, or to ask an adult to buy for them.

**Respect for time and agency**
- **RL-18** Subscriptions show price, period, renewal terms and cancellation path on the purchase screen; cancel/restore reachable from settings in ≤ 3 taps.
- **RL-20** Autosave and safe interruption: no progress lost to a phone call or app switch.
- **RL-22** No core loop that fails the removal test (a compulsion core; `design-theory` core model 10).
- **RL-23** Purchase history visible in-game (or deep-linked to the store's history), and support reachable from settings.

**Amber zone — allowed only with the safeguards in `behavioral-economics-in-games.md` and sign-off recorded in the contract:** paid randomness for verified adults (with RL-02 plus hard pity and spend caps), trial-to-purchase flows, streaks, energy systems, limited-time offers, personalised offers to adults, results-screen offers, PvP raiding of player structures, bots in matchmaking, invisible dynamic difficulty, notification reminders.

---

## 7. Volatile regulatory facts (as of Oct 2026 — verify before relying)

Each entry carries its source. Items marked **[verify]** were not confirmed against a primary source during this build.

**United States**
- The amended **COPPA Rule** (FTC final rule published April 22, 2025) had a compliance deadline of **April 22, 2026**; it expands personal information to include biometric identifiers, tightens mixed-audience, notice, consent, retention and security duties, and requires separate verifiable parental consent before disclosing children's data to third parties such as ad networks — [Toy Association](https://toyassociation.org/PressRoom2/News/2026-News/updated-coppa-rule-requirements-take-effect-april-22.aspx); [Loeb & Loeb](https://www.loeb.com/fr/insights/publications/2025/05/childrens-online-privacy-in-2025-the-amended-coppa-rule).
- **State app-store age-assurance laws**: Texas SB 2420 (effective Jan 1, 2026), Utah (May 7, 2026) and Louisiana (July 1, 2026). Apple provides a Declared Age Range API returning an age category plus consent-revocation notifications — [9to5Mac](https://9to5mac.com/2025/11/04/app-store-texas-sb2420-new-apis/); [Apple age-assurance page](https://developer.apple.com/support/age-assurance/). Litigation status of the Texas law was reported as changing during 2026 **[verify]**.
- **FTC v. Epic Games (Dec 2022)**: on December 19, 2022 the FTC announced two Epic settlements totalling $520 million: $245 million in refunds over allegations that dark patterns (for example button layouts that charged players who were waking the game or previewing an item) led to unwanted purchases, and a $275 million penalty for COPPA violations. The $245 million order was finalized in March 2023 — [FTC press release, Dec 2022](https://www.ftc.gov/news-events/news/press-releases/2022/12/fortnite-video-game-maker-epic-games-pay-more-half-billion-dollars-over-ftc-allegations); [FTC press release, Mar 2023](https://www.ftc.gov/news-events/news/press-releases/2023/03/ftc-finalizes-order-requiring-fortnite-maker-epic-games-pay-245-million-tricking-users-making). (ftc.gov rejects automated requests, so these URLs were confirmed through search results rather than a direct fetch.)
- **FTC and HoYoverse (Genshin Impact), Jan 2025**: on January 17, 2025 the FTC announced that Cognosphere (HoYoverse) would pay a $20 million civil penalty; be barred from letting children under 16 buy loot boxes without a parent's affirmative express consent; disclose loot-box odds and exchange rates for multi-tiered virtual currency; and comply with COPPA (verifiable parental consent before collecting data from under-13s, and deletion of previously collected under-13 data). It was a stipulated order filed in the Central District of California and needed court approval; Commissioner Ferguson concurred in part and dissented in part — [FTC press release](https://www.ftc.gov/news-events/news/press-releases/2025/01/genshin-impact-game-developer-will-be-banned-selling-lootboxes-teens-under-16-without-parental); [FTC consumer alert](https://consumer.ftc.gov/consumer-alerts/2025/01/ftc-settlement-order-bans-sales-genshin-impact-loot-boxes-kids-under-16-without-their-parents).
- FTC staff report "Bringing Dark Patterns to Light" (September 2022) catalogues dark patterns the agency considers problematic — ftc.gov **[verify URL]**.

**European Union**
- The proposed **Digital Fairness Act** may bring an EU-wide approach to loot boxes and dark patterns, reportedly not before 2028 — [Programming Insider](https://programminginsider.com/loot-boxes-regulation-and-where-the-line-sits-in-2026/).
- In March 2025 the **CPC network** and the European Commission published key principles on in-game virtual currencies (clear real-money pricing, no obscuring of cost, protection of children) **[verify text and status]** — European Commission consumer-protection pages.
- **Apple EU child-safety rules for payments (from Oct 1, 2026)**: no link-outs in Kids-category or under-13 apps; a parental gate for under-18 apps that use alternative payments or link-outs — [Apple Newsroom](https://www.apple.com/newsroom/2026/08/apple-announces-changes-for-apps-in-the-european-union/).
- **GDPR Art. 8** sets the digital-consent age at 16 by default; member states may lower it to 13 — [GDPR Art. 8](https://gdpr-info.eu/art-8-gdpr/).

**Loot boxes by country**
- **Belgium**: paid loot boxes treated as illegal gambling since 2018 — [Programming Insider](https://programminginsider.com/loot-boxes-regulation-and-where-the-line-sits-in-2026/).
- **Netherlands**: no effective ban; in 2022 the Council of State overturned the regulator's fine against EA's FIFA packs — [Programming Insider](https://programminginsider.com/loot-boxes-regulation-and-where-the-line-sits-in-2026/) (sources conflict on details).
- **Brazil**: the ECA Digital law (Law 15.211/2025) bans loot-box sales to under-18s, effective March 2026; a Brazilian court in June 2026 ordered Riot Games to pay damages and add age verification and probability disclosure — [Sheep Esports](https://www.sheepesports.com/articles/brazil-court-orders-riot-games-to-pay-eur2-5m-over-league-of-legends-loot-boxes/en).
- **Australia**: games classified after Sep 22, 2024 with paid chance-based items get at least an M rating; simulated gambling gets R18+ — [PCWorld](https://www.pcworld.com/article/2464538/all-games-with-loot-boxes-will-be-rated-m-or-higher-in-australia.html).
- **China**: a Ministry of Culture notice (issued December 2016) took effect May 1, 2017 and requires public disclosure of the content and draw probability of randomly drawn paid items and of draw results — [China Law Translate](https://www.chinalawtranslate.com/en/ministry-of-culture-notice-regarding-strengthening-regulation-online-gaming-operations/) (unofficial translation). The NPPA's draft online-game measures (December 22, 2023, comments to January 22, 2024) were pulled from its website around January 23, 2024 without a formal retraction notice, and their later status is unconfirmed — [DT Next news report](https://www.dtnext.in/lifestyle/technology/china-regulator-removes-draft-video-game-rules-from-website-shares-jump-763035).
- **Japan**: in May 2012 the Consumer Affairs Agency said "kompu gacha" (complete-the-set gacha) violated the premiums and representations law, with enforcement from July 2012, and operators withdrew it — [Bloomberg](https://www.bloomberg.com/news/articles/2012-05-18/japan-consumer-agency-says-complete-gacha-game-feature-illegal); [Game Developer](https://www.gamedeveloper.com/business/why-quot-kompu-gacha-quot-was-banned).
- **South Korea**: mandatory probability disclosure for chance-based items took effect in March 2024 under the Game Industry Promotion Act (date taken from reporting on Nexon's appeal; the statute text was not retrieved). In January 2024 the Korea Fair Trade Commission fined Nexon Korea 11.6 billion won over undisclosed changes to MapleStory Cube odds — [Anime News Network](https://www.animenewsnetwork.com/news/2024-01-05/korean-ftc-fines-nexon-usd8.8-million-for-allegedly-manipulating-draw-odds-in-maplestory-game/.206181); [Inven Global](https://www.invenglobal.com/articles/20319/nexons-maplestory-appeals-fine-as-seoul-high-court-resumes-hearing-in-april).
- **United Kingdom**: the government chose industry self-regulation in July 2022, and the industry published 11 principles on paid loot boxes in July 2023; independent research reported weak compliance — [CMS](https://cms.law/en/gbr/legal-updates/loot-boxes-11-new-principles-for-an-industry-led-approach); [5Rights Foundation](https://5rightsfoundation.com/research-reveals-non-existent-enforcement-of-industry-led-standards-on-loot-boxes).

**Platforms and ratings**
- Apple App Review Guideline 3.1.1 requires apps offering loot boxes or other randomized paid items to disclose the odds of each item type before purchase; Google Play has an equivalent requirement — [Apple App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/).
- Apple moved to a new age-rating system (4+, 9+, 13+, 16+, 18+) with questionnaire answers due Jan 31, 2026 — [Apple Upcoming Requirements](https://developer.apple.com/news/upcoming-requirements/). Google Play uses IARC questionnaires that yield regional ratings — [Play Console Help](https://support.google.com/googleplay/android-developer/answer/9898843).
- ESRB and PEGI introduced in-game purchase notices that flag random items (around 2020) **[verify current wording]**.

---

## 8. Minors

Children and teenagers are more susceptible to persuasive design (less developed impulse control, weaker understanding of virtual-currency value, stronger peer influence), and the law treats them differently almost everywhere. The studio designs for **the youngest permitted player**, not the average one.

### 8.1 Knowing who is a minor
- **Neutral age screen**: ask for birth year or age with no default and no hint about the "right" answer; do not use "Are you 18+? Yes/No" with Yes pre-selected.
- **Platform signals**: use platform age-range signals where available (e.g. Apple's Declared Age Range API; family accounts) — see `legal-ethics` and `store-release`.
- **Unknown age** is treated as a minor for risky features (paid randomness, personalised ads and offers, open chat) until a reliable signal says otherwise.
- **Contract field**: `contract.meta.target_audience.age_min`. If below 13 (or the local digital-consent age), children's-privacy, ad and loot-box constraints apply by default (schema description in `common.schema.json`).

### 8.2 Protections matrix (studio defaults)

| Feature | Under 13 | 13–15 | 16–17 | 18+ / verified adult |
|---|---|---|---|---|
| Paid random items | Off | Off | Off | Amber (RL-02 + pity + caps) |
| Personalised ads | Off (contextual only; child-directed flags) | Off by default | Consent-based where lawful | Consent-based |
| Interstitial ads | Off | Off before FTUE complete; low frequency | Low frequency | Per contract pacing |
| Rewarded ads | Allowed, capped, age-appropriate creatives | Allowed, capped | Allowed, capped | Allowed, capped |
| Personalised offers | Off | Off | Off | Amber |
| Limited-time offers | Off | Truthful, low frequency | Truthful | Truthful |
| Purchase confirmation | Platform parental controls + in-game confirmation every purchase | In-game confirmation every purchase | Confirmation ≥ USD 5 equivalent | Confirmation ≥ USD 5 equivalent |
| Open text chat | Off (preset phrases only) | Friends-only, filtered | Filtered, report/mute | Filtered, report/mute |
| Push notifications | Off by default; parent-controlled | Opt-in, quiet hours | Opt-in, quiet hours | Opt-in |
| Leaderboards with names | Nicknames only, no real names | Nicknames | Nicknames | Player choice |
| External links / link-outs | Off or parental gate | Parental gate where required | Per platform rules | Per platform rules |
| Data collection | Minimum necessary; no third-party sharing without verifiable parental consent | Minimised | Minimised | Per privacy policy |

### 8.3 Design rules for games that children may play
- No copy that tells children to buy or to ask parents to buy (RL-24).
- No characters that express sadness or disappointment when a child declines a purchase or leaves the game.
- Clear distinction between game rewards and purchasable items; price shown in real money.
- Session-end prompts that encourage stopping rather than continuing.
- Moderation and safety by default in any social feature (see `multiplayer-backend`).
- Store listing and age rating consistent with the actual content and monetisation (`store-release`).

---

## 9. Problematic play and wellbeing design

### 9.1 What is known (stable, hedged)
- The World Health Organization's ICD-11 includes **gaming disorder** (code 6C51), characterised by impaired control over gaming, increasing priority given to gaming over other activities, and continuation despite negative consequences, typically over at least 12 months; ICD-11 took effect in January 2022. The American Psychiatric Association's DSM-5 (2013) lists **internet gaming disorder** as a condition for further study rather than a formal diagnosis.
- Prevalence estimates vary widely with criteria, instruments and samples; most studies find that only a small minority of players meet clinical criteria. Do not quote a single number without a source.
- Research using publisher telemetry (for example Johannes, Vuorre & Przybylski 2021; Vuorre et al. 2022) found little evidence that play time alone drives wellbeing up or down, while the *quality of motivation* (playing because one wants to vs feeling compelled) related to wellbeing. This supports designing for need satisfaction rather than policing hours.
- Loot-box spending is consistently *associated* with problem-gambling severity across many studies (from Zendle & Cairns 2018 onward); causality and direction are unresolved, which is reason enough for the studio's restrictions.

### 9.2 Risk signals (telemetry) and responses
These signals are *indicators for supportive design*, not diagnoses. Use aggregates for design decisions; individual-level interventions must be supportive, privacy-respecting and never punitive.

| Signal | Example threshold (studio starting point; tune per game) | Response |
|---|---|---|
| Spend velocity spike | Spend in 7 days > 5× the player's prior 30-day weekly average and > USD 100 | Suppress personalised and limited-time offers for 14 days; show spending summary |
| Chasing after losses | ≥ 3 purchases within 30 min following failures or lost PvP matches | Suppress offers for the session; cool-down message without guilt |
| Very long sessions | Continuous session > 3 h | Gentle break reminder; natural stop offered; no penalties for leaving |
| Late-night play (minors) | Sessions 00:00–05:00 local on ≥ 3 nights in a week | Wellbeing reminder; quiet-hours notifications already off |
| Rapid repeat purchasing of random items | ≥ 10 paid random draws in one hour (adults) | Show cumulative spend and odds summary; offer to set a limit |
| Self-reported regret | "Not glad I spent" responses | Suppress offers; refund-help path visible |

### 9.3 Wellbeing features (menu)
- **Spending dashboard**: purchases by day/week/month, in real money.
- **Self-set limits**: optional spending or play-time limits stored server-side, with a cool-off period before raising a limit (e.g. 24–72 h).
- **Break reminders**: opt-in, default on for minors; never blocking unless a parent configured it.
- **Natural stopping points**: every 2–5 minutes in mobile designs; "done for today" states for daily content.
- **No penalties for absence**: rewards wait; welcome-back flows clear obligations instead of shaming.
- **Offline-progress caps** that reward returning without demanding constant checking.
- **Transparency page**: odds, pity rules, how matchmaking and difficulty work, how bots are used, data use.
- **Easy exit**: account deletion and data requests reachable from settings (required by stores and privacy law in many regions; see `store-release`).

### 9.4 Measuring wellbeing impact
- Add 2–3 wellbeing and endorsement items to periodic in-game surveys (`player-research-methods.md` §6): "I feel good about the time I spend in this game", "I feel good about the money I've spent", "I sometimes play when I'd rather be doing something else".
- Track them by segment and payer tier; a rising "rather be doing something else" score is a compulsion warning even if retention is rising.

---

## 10. Ethical monetization patterns that work

| Pattern | Why it is ethical | Design notes |
|---|---|---|
| **Direct purchase of stated content** (bundles, characters, levels) | Player knows exactly what they get | Show contents and real-money price; preview items |
| **Cosmetics** | Expression without power | Preview on the player's own character; avoid random-only cosmetics |
| **Season pass with free track** | Visible rewards; value scales with play | No power exclusives in premium; rewards earnable in the season by a reasonable player; clear end date |
| **Premium unlock / try-before-buy** | Fair exchange | Generous free portion; clear about what's premium (M10 safeguard) |
| **Remove-ads purchase** | Clear value | Keep rewarded ads optional afterwards; restore purchases easily |
| **Rewarded ads, opt-in and capped** | Player chooses the exchange | Never between fail and retry; daily caps; age-appropriate creatives |
| **Subscriptions with clear recurring value** | Predictable cost | Clear terms; easy cancel; no hostage of earned items on cancel where avoidable |
| **Supporter packs** | Voluntary support | Not adjacent to gifts; no guilt copy |
| **Fair starter pack** | Good value, single offer | No escalating ladder afterwards |
| **Transparent random rewards earned by play** | Fun of surprise without spend | Odds shown; duplicates convert to progress |

These patterns are the studio's default toolkit; `monetization` holds pricing and placement detail, and `arcosian:monetization-designer` owns the design.

---

## 11. Ethics review procedure and scorecard

### 11.1 When to review
- Concept stage (monetization model and target audience chosen).
- Design contract sign-off (`design-review` workflow includes a monetization-ethics reviewer).
- Before every feature that touches money, randomness, time pressure, social obligation or notifications is marked done.
- Before soft launch and before every major live-ops season.

### 11.2 Procedure
1. **Inventory**: list every offer, timer, random reward, notification, social prompt, ad placement and currency in the build (not just the docs).
2. **Classify** each against the catalogue (§4) and red lines (§6); record pattern ids.
3. **Walk the vulnerable paths**: play as (a) a new player in the first 30 minutes, (b) a player on a 5-level losing streak, (c) a minor according to the age gate, (d) a player who has just spent USD 50 today. Note every offer and pressure moment.
4. **Run the machine checks**: `python3 ${CLAUDE_PLUGIN_ROOT}/skills/player-psychology/scripts/psych_check.py redlines --contract .gamestudio/contract.json` and `compliance_preflight.py --project ...` (`${CLAUDE_PLUGIN_ROOT}/scripts/compliance_preflight.py`).
5. **Score** with the scorecard (§11.3).
6. **Fix or justify**: red items are fixed before the gate passes; amber items need documented safeguards and sign-off in `contract.monetization.ethics`.
7. **Record**: a review report under `.gamestudio/reports/ethics-review-<date>.md` and notes in the feature's `gate_notes`.
8. **Monitor after launch**: abuse metrics (`behavioral-economics-in-games.md` §24) reviewed monthly by `arcosian:data-analyst`.

### 11.3 Scorecard (0–3 per dimension)

| Dimension | 0 | 1 | 2 | 3 |
|---|---|---|---|---|
| **Transparency** | Prices/odds hidden | Disclosed but hard to find | Disclosed at decision point | Disclosed at decision point, real money, plain language, transparency page |
| **Fairness** | Pay-to-win or spend-dependent systems | Paid power significant | Paid convenience only | Skill/time decide outcomes; payments cosmetic or content |
| **Autonomy** | Pressure, fake urgency, nagging | Some pressure moments | Neutral prompts | Player-initiated purchases; easy decline; no obligation loops |
| **Vulnerability protection** | Targets frustration/minors | Some protections | Minors protected; no frustration triggers | Plus spend-signal suppression and self-limits |
| **Wellbeing** | No stopping points, punitive absence | Some stopping points | Natural stops, no absence penalty | Plus spending/play dashboards and endorsement tracking |

**Thresholds.** Any red-line violation fails regardless of score. Otherwise a total ≥ 12/15 with no dimension below 2 passes; 9–11 requires a remediation plan before soft launch; < 9 fails.

---

## 12. Sources

Paraphrased; consult originals. Volatile regulatory sources are listed inline in §7.

- Brignull, H. Deceptive Patterns (formerly darkpatterns.org) — https://www.deceptive.design/
- Dark Pattern Games (community catalogue) — https://www.darkpattern.games/
- Gray, C. M., Kou, Y., Battles, B., Hoggatt, J., & Toombs, A. L. (2018). "The Dark (Patterns) Side of UX Design." *CHI 2018*.
- Information Commissioner's Office (UK). *Age Appropriate Design Code* — https://ico.org.uk/
- Johannes, N., Vuorre, M., & Przybylski, A. K. (2021). "Video game play is positively correlated with well-being." *Royal Society Open Science*, 8(2).
- King, D. L., Delfabbro, P. H., Gainsbury, S. M., Dreier, M., Greer, N., & Billieux, J. (2019). "Unfair play? Video games as exploitative monetized services: An examination of game patents from a consumer protection perspective." *Computers in Human Behavior*, 101.
- Mathur, A., Acar, G., Friedman, M. J., Lucherini, E., Mayer, J., Chetty, M., & Narayanan, A. (2019). "Dark Patterns at Scale: Findings from a Crawl of 11K Shopping Websites." *Proceedings of the ACM on Human-Computer Interaction (CSCW)*.
- Petrovskaya, E., & Zendle, D. (2022). "Predatory Monetisation? A Categorisation of Unfair, Misleading and Aggressive Monetisation Techniques in Digital Games from the Player Perspective." *Journal of Business Ethics*.
- Vuorre, M., Johannes, N., Magnusson, K., & Przybylski, A. K. (2022). "Time spent playing video games is unlikely to impact well-being." *Royal Society Open Science*, 9(7).
- World Health Organization. ICD-11, 6C51 Gaming disorder — https://icd.who.int/
- Zagal, J. P., Björk, S., & Lewis, C. (2013). "Dark Patterns in the Design of Games." *Foundations of Digital Games 2013*.
- Zendle, D., & Cairns, P. (2018). "Video game loot boxes are linked to problem gambling: Results of a large-scale survey." *PLOS ONE*, 13(11).
- European Union. Directive 2005/29/EC (Unfair Commercial Practices Directive); Regulation (EU) 2022/2065 (Digital Services Act) — https://eur-lex.europa.eu/
