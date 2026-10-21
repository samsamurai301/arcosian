# Business, Monetization, Live Ops and Production Terms

This file defines the vocabulary of game business: monetization and economy, user acquisition and attribution, retention analytics, live operations, store and launch economics, production management and game-market research. Use it when a forecast, a pricing proposal, a live-ops calendar or a milestone review uses a term you need to pin down. Entries are alphabetical; each entry is one line in the form **Term** — definition — see: related term or skill. Numbers in definitions are illustrative formulas, not benchmarks.

## Contents
- A: A/B test (business) through Attribution
- B: Bad debt (refunds and chargebacks) through Burn-up chart
- C: CAC (customer acquisition cost) through Crunch
- D: Daily login reward through Dynamic pricing
- E: Economy faucet through Expected value (EV) of a draw
- F: Feature flag rollout through Funnel (business)
- G: Gacha pool through Guardrail metric
- H: Hard currency through Hypothesis (product)
- I: IAP (in-app purchase) through Invalid traffic (IVT)
- K: Kanban through Kanban
- L: Live event through LTV (lifetime value)
- M: Magic number through MVP (minimum viable product)
- N: Net promoter score (NPS) through North star metric
- O: Offer fatigue through Organic install
- P: Patch notes through Push opt-in rate
- Q: Quarterly plan through Quarterly plan
- R: RACI through Royalty
- S: Scope creep through Sunk cost (player)
- T: Take rate through Tutorial completion rate
- U: UA (user acquisition) through UA (user acquisition)
- V: VAT (value-added tax) through VIP tier
- W: Whale through Wishlist (store)
- Y: Yield (ad) through Yield (ad)

## A

**A/B test (business)** — Controlled split of users to compare a monetization or live-ops change against a control; define the success metric and minimum effect before starting. — see: `player-analytics`
**Acquisition (user)** — Process of bringing new players to the game, paid or organic. — see: `marketing-ua`
**Ad frequency and recency** — Limits on how often and how recently a user sees the same ad or offer; protects experience and retention. — see: `monetization`
**Ad mediation** — Layer that chooses which ad network serves each request to maximize yield across networks. — see: `monetization`
**Ad waterfall** — Ordered list of networks called in sequence by floor price; many setups now mix it with bidding. — see: `monetization`
**ARPDAU (average revenue per daily active user)** — Daily revenue divided by daily active users; used to compare days and cohorts. — see: `monetization`
**ARPPU (average revenue per paying user)** — Revenue divided by paying users only; separates depth of spend from payer conversion. — see: `monetization`
**ARPU (average revenue per user)** — Total revenue divided by all active users in a period; the blended top-line monetization metric. — see: `monetization`
**ASO (app store optimization)** — Improving store listing text, icons, screenshots and video to raise conversion from impression to install. — see: `marketing-ua`
**ATT (App Tracking Transparency)** — Apple's permission prompt required before cross-app tracking; reduces attributable signal and shapes UA planning. — see: `legal-ethics`
**Attribution** — Assigning an install or purchase to the ad, campaign or channel that caused it; affected by platform privacy rules. — see: `marketing-ua`

## B

**Bad debt (refunds and chargebacks)** — Revenue later reversed by refund or chargeback; forecast it as a deduction from gross bookings. — see: `monetization`
**Ban (account action)** — Suspension of an account for rule breaks; define the evidence standard and the appeal path. — see: `legal-ethics`
**Banner ad** — Persistent small ad at the screen edge; low yield per impression and a layout cost in games. — see: `monetization`
**Battle pass** — Tiered reward track with a free and a paid lane, typically time-limited; design the paid lane's value per tier. — see: `monetization`
**Benchmark (genre)** — Reference figure from a credible source for a KPI in a genre; use it only with its source and definition attached. — see: `market-intel`
**Bidding (ad auction)** — Real-time auction where ad networks compete for an impression; the price signal behind eCPM. — see: `marketing-ua`
**Billing retry** — Re-attempting a failed subscription charge over days before cancellation; a major source of recovered revenue. — see: `monetization`
**Blended CPI** — Average cost per install across all channels, weighted by volume; hides channel differences. — see: `marketing-ua`
**Burn-down chart** — Chart of remaining work over a sprint or milestone; a rate-of-progress signal, not a forecast by itself. — see: `production`
**Burn rate** — Monthly spend exceeding revenue; determines how long a studio can run without new funds. — see: `production`
**Burn-up chart** — Completed work plotted against total scope over time, so scope changes show clearly. — see: `production`

## C

**CAC (customer acquisition cost)** — Total acquisition spend divided by new paying users acquired in the same window. — see: `marketing-ua`
**Capacity planning** — Estimating available person-days after holidays, meetings, support and leave. — see: `production`
**Cash runway** — Months a studio can operate at current burn before running out of money. — see: `production`
**Churn** — Share of users who stop playing or paying in a period; the mirror of retention. — see: `player-analytics`
**Churn prediction** — Model scoring users by probability of leaving; judge it by lift from interventions, not accuracy alone. — see: `liveops`
**Click-through rate (CTR)** — Clicks divided by impressions; a creative-quality signal for ad campaigns. — see: `marketing-ua`
**Code freeze** — Stop-merge point before release; only approved fixes land after it. — see: `production`
**Co-development** — Development shared between a studio and an outside partner with defined splits of work and rights. — see: `production`
**Cohort** — Group of users sharing a start date or trait, tracked over time to compare retention or revenue. — see: `player-analytics`
**Cohort LTV curve** — Cumulative revenue per install plotted by day since install; used to project lifetime value. — see: `monetization`
**Community manager** — Role that runs public channels, collects feedback and announces changes; works closely with live ops. — see: `liveops`
**Comparable titles (comps)** — Released games used to size an opportunity or set expectations; pick them by audience and monetization model. — see: `market-intel`
**Content complete** — Milestone where all planned content exists while bugs and polish remain. — see: `production`
**Content drop** — Scheduled release of new content into the live game, with its own test and rollback plan. — see: `liveops`
**Conversion rate (paying)** — Share of active users who make at least one purchase in a period. — see: `monetization`
**Conversion rate (store)** — Share of store page viewers who install; a function of icon, screenshots, rating and video. — see: `marketing-ua`
**Cost per action (CPA)** — Spend per defined action such as tutorial completion; choose the action that predicts revenue. — see: `marketing-ua`
**Cost per install (CPI)** — Spend divided by installs from a channel; cheap installs can still be low-value installs. — see: `marketing-ua`
**Cost per mille (CPM)** — Price per thousand ad impressions; a media buying unit. — see: `marketing-ua`
**Creative fatigue** — Decline in ad performance as the same creative repeats; plan refreshes before results drop. — see: `marketing-ua`
**Creative testing** — Comparing ad variants on cost and early retention signals before scaling spend. — see: `marketing-ua`
**Creator program (influencer)** — Paid or revenue-share partnerships with content creators to drive installs or awareness. — see: `marketing-ua`
**Critical path** — Longest chain of dependent tasks that sets the earliest finish date for a milestone. — see: `production`
**Crunch** — Sustained overtime to meet a deadline; a production failure signal with well-documented costs to quality and staff. — see: `production`

## D

**Daily login reward** — Calendar-style reward for returning on consecutive days; a retention lever that needs a clear end state. — see: `liveops`
**Dark pattern** — Interface that tricks users into unintended choices such as hidden costs or confusing cancel flows; regulators and stores treat many as violations. — see: `legal-ethics`
**DAU (daily active users)** — Unique users active on a given day; the denominator for daily metrics such as ARPDAU. — see: `player-analytics`
**DAU/MAU ratio** — Daily active users divided by monthly active users; a stickiness measure of habit. — see: `player-analytics`
**Definition of done** — Shared checklist that work must meet to count as complete, such as tests passing and performance checked. — see: `production`
**Dependency (task)** — Work that cannot start until other work finishes; map dependencies to see milestone risk. — see: `production`
**Dolphin (player segment)** — Informal name for a mid-level spender, between minnows and whales. — see: `monetization`
**Dormant user** — Player inactive beyond a defined window; a segment for win-back campaigns. — see: `liveops`
**Dynamic pricing** — Adjusting prices per user or region based on signals; check for fairness and local legal rules before using. — see: `monetization`

## E

**Economy faucet** — Mechanism that adds currency or items to the economy, such as quest rewards or daily grants. — see: `economy-design`
**Economy sink** — Mechanism that removes currency or items from the economy, such as crafting costs or repairs. — see: `economy-design`
**eCPM (effective cost per mille)** — Revenue per thousand impressions across an ad unit, including all networks; the way to compare ad inventory value. — see: `monetization`
**Event cadence** — Frequency and rhythm of live events on the calendar; too fast fatigues players, too slow loses habit. — see: `liveops`
**Expected value (EV) of a draw** — Probability-weighted average value of a random reward; the basis for checking fairness and disclosure. — see: `economy-design`

## F

**Feature flag rollout** — Enabling a feature for a percentage of users, then widening it with monitoring. — see: `liveops`
**Fill rate (ad)** — Share of ad requests that are filled by an ad; low fill limits ad revenue regardless of demand. — see: `monetization`
**Freemium (F2P)** — Free-to-play model where revenue comes from optional purchases and ads rather than the price of entry. — see: `monetization`
**Frequency cap** — Limit on how often a user sees an ad or offer in a period; protects retention and experience. — see: `monetization`
**Funnel (business)** — Ordered conversion steps (install, tutorial completion, first purchase) with drop-off measured at each. — see: `player-analytics`

## G

**Gacha pool** — Set of rewards and their weights inside a draw, which must be documented to check its odds. — see: `economy-design`
**Gacha (randomized paid draw)** — Paid chance-based reward; in many jurisdictions it requires disclosed odds and triggers loot-box rules. — see: `legal-ethics`
**Going live checklist** — Pre-launch list covering builds, store pages, analytics, server capacity and rollback steps. — see: `production`
**Go/no-go gate** — Decision point at a milestone with explicit criteria; a no-go stops or reshapes the project. — see: `production`
**Greenlight decision** — Approval to fund the next stage of development against stated criteria. — see: `production`
**Gross bookings** — Total purchase value before store fees, refunds or taxes; a top-line figure that overstates revenue. — see: `monetization`
**Gross margin** — Revenue minus direct cost of revenue, expressed as a share; platform fees and content costs sit in cost of revenue. — see: `production`
**Gross-to-net** — Process of converting gross bookings into net revenue after store fees, taxes and refunds. — see: `monetization`
**Guardrail metric** — Metric that must not degrade during an experiment, such as crash rate or refund rate. — see: `player-analytics`

## H

**Hard currency** — Premium currency bought with real money; monetization and balancing must account for its conversion rate. — see: `economy-design`
**Holdout group** — Users kept out of a campaign or change to measure its incremental effect. — see: `marketing-ua`
**Hotfix** — Urgent fix shipped outside the normal release cadence; relies on remote config or a small patch path. — see: `liveops`
**Hypothesis (product)** — Testable statement with an expected result and a measure, written before building. — see: `production`

## I

**IAP (in-app purchase)** — Purchase inside the app, including consumable, non-consumable and subscription products. — see: `monetization`
**Incrementality** — Share of conversions caused by a campaign beyond what would have happened anyway; measure with holdouts. — see: `marketing-ua`
**Inflation (economy)** — Rising prices or falling currency value caused by faucets exceeding sinks. — see: `economy-design`
**Install-day retention** — Share of installers who open the game on the install day; a leading indicator for onboarding quality. — see: `player-analytics`
**Install rate** — Installs divided by clicks or impressions; a funnel step between ad exposure and install. — see: `marketing-ua`
**Interstitial ad** — Full-screen ad shown between game states; high yield, high churn risk if frequent. — see: `monetization`
**Invalid traffic (IVT)** — Clicks or installs produced by bots or fraud; networks may refuse or deduct them, which distorts CAC. — see: `marketing-ua`

## K

**Kanban** — Flow-based board that limits work in progress; suits live-ops and support queues. — see: `production`

## L

**Live event** — Time-limited game mode or challenge that changes the experience for a window; test its economy before launch. — see: `liveops`
**LiveOps calendar** — Scheduled plan of events, offers, content drops and maintenance across weeks or months. — see: `liveops`
**Live tuning** — Adjusting parameters in production through remote config to fix balance without shipping a build. — see: `liveops`
**Lookalike audience** — Ad audience modelled on existing payers; quality depends on the seed list. — see: `marketing-ua`
**LTV:CAC ratio** — LTV divided by CAC; a common planning ratio, with the payback window stated alongside. — see: `marketing-ua`
**LTV (lifetime value)** — Expected revenue or margin per user over their life; compare against CAC to judge acquisition. — see: `monetization`

## M

**Magic number** — Unexplained literal value in code or design data; move it to named, documented config. — see: `game-architecture`
**Maintenance window** — Scheduled period with servers offline; announce it in advance and keep it short. — see: `liveops`
**Market fit** — Evidence that a product meets sustained demand at a sustainable price, judged by retention and payment rather than opinion. — see: `market-intel`
**Market gap** — Underserved combination of audience, mechanic and price; test it with a small scope before committing. — see: `market-intel`
**MAU (monthly active users)** — Unique users active in a month; a scale metric and denominator for stickiness. — see: `player-analytics`
**Milestone** — Dated checkpoint with defined exit criteria, such as vertical slice or content-complete. — see: `production`
**Minimum guarantee (MG)** — Advance paid against future royalties and recouped from revenue before the partner shares profit. — see: `production`
**Minimum viable game** — Smallest playable build that tests the core loop with real players; a research tool, not a product. — see: `production`
**Minnow (player segment)** — Low-spending payer; a large group whose total spend is small. — see: `monetization`
**MMP (mobile measurement partner)** — Third-party service that attributes installs and events to campaigns. — see: `marketing-ua`
**Moderation** — Review and action on player content and conduct such as chat and names; needs written policy and appeals. — see: `legal-ethics`
**MVP (minimum viable product)** — Smallest version that tests the core hypothesis with real users; not a shippable bad game. — see: `production`

## N

**Net promoter score (NPS)** — Survey metric from one question on likelihood to recommend; a sentiment signal, not a revenue one. — see: `player-analytics`
**Net revenue** — Gross bookings less refunds, chargebacks, store fees and taxes; the figure used for real economics. — see: `monetization`
**North star metric** — Single metric that reflects value delivered to players and predicts revenue, used to align teams. — see: `production`

## O

**Offer fatigue** — Falling response to repeated offers; reduce frequency and vary the value before discounting again. — see: `monetization`
**Offer (targeted)** — Discounted or bundled purchase shown to a segment at a moment of intent; check for fairness and disclosure. — see: `monetization`
**OKR (objectives and key results)** — Goal framework pairing an objective with measurable key results and a review cadence. — see: `production`
**Organic install** — Install not attributed to paid campaigns; its share is a measure of brand and store strength. — see: `marketing-ua`

## P

**Patch notes** — Public summary of an update; accuracy matters for trust and for store review sentiment. — see: `liveops`
**Payback period** — Months until cumulative user contribution covers acquisition cost; the cash-flow lens on UA. — see: `marketing-ua`
**Payer segmentation** — Grouping payers by spend or behaviour for offers and support; design offers that stay fair. — see: `monetization`
**Paying user rate** — Share of users who have ever or recently paid; the denominator for ARPPU analysis. — see: `monetization`
**Paywall** — Screen that gates content or features behind a purchase; design it with clear prices and a real free path. — see: `monetization`
**Phased release** — Store-side gradual rollout of an app update to a rising share of users. — see: `store-release`
**Pitch deck** — Short presentation that states the concept, audience, market, plan, budget and risks for funding or partners. — see: `market-intel`
**Playable ad** — Interactive, short gameplay demo used as an ad; conveys mechanics better than video in many tests. — see: `marketing-ua`
**Player support ticket** — Request for help from a player; ticket volume per release is an early quality signal. — see: `liveops`
**Playtest (business)** — Structured test of the game with target players; its findings feed the go/no-go decision. — see: `production`
**Post-mortem (project)** — Structured review of what happened on a project, with actions and owners; blameless in format. — see: `production`
**Pre-production** — Phase for prototype, vertical slice and plan before full production begins. — see: `production`
**Price anchoring** — Showing a reference price first so the real price feels lower; disclose any strike-through honestly. — see: `monetization`
**Price discrimination (regional)** — Charging different prices by region based on purchasing power; legal in most places, but check local rules. — see: `monetization`
**Producer** — Role owning schedule, scope, risk and budget; the person who turns a plan into shipped milestones. — see: `production`
**Publisher** — Company that funds, markets and distributes a game, often taking a revenue share. — see: `production`
**Push opt-in rate** — Share of users who accept push permission; it bounds how many users can be reached by push. — see: `liveops`

## Q

**Quarterly plan** — Set of goals and initiatives for a quarter, with owners and measurable outcomes. — see: `production`

## R

**RACI** — Matrix of who is Responsible, Accountable, Consulted and Informed for each task; use it to clear ownership. — see: `production`
**Rating prompt** — In-app request for a store review; show it after a positive moment and at a limited frequency. — see: `liveops`
**Recoupment** — Repayment of an advance from a partner's share of revenue before profit is paid out. — see: `production`
**Re-engagement campaign** — Notifications or ads to bring lapsed users back, gated by consent and frequency rules. — see: `liveops`
**Refund rate** — Share of purchases refunded; a quality and fraud signal and a guardrail for pricing changes. — see: `monetization`
**Remarketing (retargeting)** — Ads shown to users who already interacted with the game; efficient but limited in reach. — see: `marketing-ua`
**Retention curve** — Share of a cohort active by day since install, plotted for comparison across cohorts. — see: `player-analytics`
**Retention (paid vs organic)** — Retention compared by acquisition channel; judges channel quality better than install counts. — see: `player-analytics`
**Retro (retrospective)** — Team review after an iteration asking what to keep, stop and try; produces a small number of actions. — see: `production`
**Revenue share** — Contractual split of revenue with a partner; define the base (gross or net) and the timing. — see: `production`
**Rewarded video** — Ad the player chooses to watch for a reward; well-designed, it is one of the least resented formats. — see: `monetization`
**Risk register** — Table of risks with likelihood, impact, owner and mitigation, reviewed each milestone. — see: `production`
**ROAS (return on ad spend)** — Revenue from users acquired by ads divided by ad spend; a payback-oriented UA metric. — see: `marketing-ua`
**Royalty** — Percentage payment on revenue to a rights holder or partner; check the base and the deductions. — see: `production`

## S

**Scope creep** — Unplanned growth of features without matching time or budget; the most common cause of late projects. — see: `production`
**Scrum** — Iterative framework with fixed-length sprints, defined roles and ceremonies; studios often adapt it. — see: `production`
**Seasonal content** — Content tied to a calendar period or season pass, with a known end date. — see: `liveops`
**Segment (player)** — Group of players defined by behaviour or value, such as lapsed payers or new players in week one. — see: `liveops`
**Sentiment analysis** — Automated classification of feedback text; check it against human reads before acting on it. — see: `player-analytics`
**Session length** — Average time per session; the right target depends on genre and session design. — see: `player-analytics`
**Sessions per DAU** — Sessions per active user per day; reflects how often the habit recurs. — see: `player-analytics`
**Slip (schedule)** — Milestone moving later; track the slip rate as an early warning of trouble. — see: `production`
**Soft currency** — In-game currency earned by play and not bought with money; the main economy balancing lever. — see: `economy-design`
**Soft launch** — Release in a few markets to test retention, monetization and cost before a global launch. — see: `store-release`
**Spike (time-boxed investigation)** — Fixed-time study that answers one technical or design question before estimating the work. — see: `production`
**Store fee (platform fee)** — Percentage taken by a platform on digital sales; read the current published schedule rather than assuming a rate. — see: `store-release`
**Store rating** — Aggregate player score on a store page; sensitive to crashes and monetization complaints. — see: `marketing-ua`
**Story points** — Relative effort estimate for backlog items; they are not hours and should not be converted into them. — see: `production`
**Streak mechanic** — Reward for consecutive days of play; loss aversion can create pressure, so keep the cost of a missed day fair. — see: `liveops`
**Subscription** — Recurring paid product with a defined billing period; retention and churn are the core metrics. — see: `monetization`
**Sunk cost (player)** — Players continue because they have already spent; a retention effect that can become exploitative if pushed. — see: `legal-ethics`

## T

**Take rate** — Share of gross bookings kept by a platform or intermediary; the complement of net revenue after fees. — see: `store-release`
**Technical debt** — Shortcuts that slow future change; track it as a backlog with owners and cost estimates. — see: `production`
**Tiered pricing** — Several price points for similar products to guide choice; the middle option usually anchors the decision. — see: `monetization`
**Tournament (live)** — Competitive event with ranking and rewards over a window; plan matchmaking and anti-cheat early. — see: `liveops`
**Toxicity** — Abusive behaviour in player communication; mitigate with reporting, filters and penalties with appeal. — see: `legal-ethics`
**Tutorial completion rate** — Share of new users who finish onboarding; a leading indicator of retention. — see: `player-analytics`

## U

**UA (user acquisition)** — Spending on paid channels to acquire players; a cash-flow and LTV:CAC discipline. — see: `marketing-ua`

## V

**VAT (value-added tax)** — Consumption tax applied to digital goods in many regions; net revenue depends on it, so confirm with finance. — see: `monetization`
**Velocity** — Work completed per iteration, measured in a consistent unit; use it for planning, not for pressure. — see: `production`
**Vertical slice** — Finished, polished sample of the core loop and one level, used to prove quality and direction. — see: `production`
**VIP tier** — Loyalty system that rewards repeat spend with perks; design the perks so they do not punish free players. — see: `monetization`

## W

**Whale** — Very high-spending player; a small share of payers often generates a large share of revenue, which raises fairness questions. — see: `monetization`
**Win-back** — Targeted campaign that brings back lapsed or churned users with incentives within a defined window. — see: `liveops`
**Wishlist (store)** — Count of store followers who signal intent to buy at launch; a leading indicator, not a sales forecast. — see: `marketing-ua`

## Y

**Yield (ad)** — Revenue per ad request or impression; the output of demand quality, fill and mediation. — see: `monetization`
