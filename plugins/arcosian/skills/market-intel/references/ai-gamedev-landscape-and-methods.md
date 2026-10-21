# AI Game-Creation Landscape and Research Methods

This file does two jobs. First, it maps the competitors that generate or automate game development with AI as of October 2026 (from the research notes; many facts are vendor-reported and flagged) and states how this plugin differs. Second, it teaches the research methods a market analyst uses: third-party intelligence tools such as Sensor Tower and AppMagic, store charts, review mining and ad libraries, with procedures, templates and cautions. The competitive facts are volatile and sourced in a dedicated section; the methods are stable.

## Contents
1. Landscape categories and what they mean
2. Competitor profiles by category
3. What none of them do (gap analysis)
4. This plugin's differentiation and honest limits
5. Positioning guidance
6. Research methods: overview and ethics
7. Third-party intelligence tools
8. Store charts and page analysis
9. Review mining
10. Ad libraries and creative research
11. Search, keyword and community signals
12. Synthesis templates
13. Volatile facts (as of Oct 2026 — verify)
14. Checklists

## 1. Landscape categories and what they mean

| Category | What it sells | Output | Owner of output | Typical limit |
|---|---|---|---|---|
| Consumer prompt-to-game platforms | Make a game by chatting; publish to a feed | Hosted, mostly 2D web or in-app games | Platform (runtime and feed lock-in) | Not store-ready native titles; weak 3D |
| Prompt-to-web-game builders | Browser games from text | JavaScript (Phaser, Three.js) | Often exportable with paid plans | Web, mobile export limited |
| Engines and no-code tools with AI | AI inside an editor or engine | Editable projects | User | Quality depends on the user; credit pricing |
| General vibe-coding and app builders | Apps and sites from prompts, applied to games | Web or React Native apps | User | Not games-native; asset gap |
| Platform-holder tools | Generation inside Roblox, Fortnite, studio engines | Assets, scenes, NPCs inside the platform | Platform ecosystem | Locked to platform |
| Studio and publisher tooling | AI agents for UA, creatives, testing | Ads, test reports, mini-games | Studio | Services, not full game creation |
| World models | Playable generated worlds | Short interactive video-like sessions | Vendor | Research demos; short and unstable |
| Asset-generation tools | Sprites, 3D, audio, concept | Assets | Varies by licence | Single pipeline step |

## 2. Competitor profiles by category

All claims below are reported by the sources in section 13 and are marked as vendor or secondary where relevant. Use as a starting map and re-verify.

### 2.1 Consumer prompt-to-game platforms
- Astrocade: reported large funding round in 2026, tens of millions of monthly active users reported by company, website-based, hosted games, product skew toward 2D according to a competitor's guide.
- Aippy: UGC-style game-creation app with reported valuation and user metrics from a news interview; features include templates, voice input, AI assets, one-click error repair and remix.
- Upit (FRVR): AI game-making on phone and web with themes and remix; publishes to other platforms according to its 2026 updates.
- Jabali: text-to-playable game tool with several surfaces; leadership details conflict across sources.
- Others reported: Websim (sandbox, mostly small 2D, unclear export), Nilo (narrowed to 3D asset export for Roblox Studio per a vendor guide), Death by AI (AI party game, user numbers reported by an aggregator).
Reading: consumer platforms prove demand for "make a game by talking" and for remix communities, but their output stays inside their runtime.

### 2.2 Prompt-to-web-game builders
- Rosebud AI: browser games (Phaser and Three.js), hosted link, code export and commercial rights on higher tiers; credit-based pricing on its public page; mobile export not listed.
- SEELE, Cinevva and Gameer appeared in a vendor roundup; features vary and claims are vendor-reported.

### 2.3 Engines and no-code tools with AI
- GDevelop AI: open-source engine with an in-editor agent, exports to web, Android, iOS and desktop; credit-based plans.
- Buildbox 4: no-code, hyper-casual oriented, with AI generation and HTML5 export; engine lock-in noted by a guide.
- Summer Engine: Godot-compatible desktop AI studio; mobile export claims conflict between a vendor guide and the company page.
- Unity AI: open beta for Unity 6 reported to have started May 4, 2026, replacing Unity Muse; credit-based add-on for lower tiers.
- Unreal Engine: PCG framework reported production-ready in 5.7; AI assistant features inside the editor.

### 2.4 General vibe-coding and app builders
- Replit, Bolt.new, Cursor: general tools used for web games; Vibe Jam 2026 reportedly drew 945 submissions under a mostly-AI-code rule, mostly free web games.
- Rork and a0.dev: generate native mobile apps (React Native, SwiftUI); games are a side case; one reviewer says output needs substantial engineering to meet store standards.

### 2.5 Platform-holder tools
- Roblox: generative 4D object tools in beta (early 2026) with self-reported engagement lift; full scene generation promised.
- Fortnite UEFN: AI NPC features (voice and conversation devices) and a coding assistant, with policy limits.
- Tencent and NetEase: internal pipelines and in-game generation features for UGC; mostly Chinese-market and platform-bound.

### 2.6 Studio and publisher tooling
- Sett: AI agents for mobile studios focusing on ad creatives, playable ads and live features; reported funding in 2026; company-claimed speed and cost advantages.
- Testing vendors (nunu.ai, modl.ai, King's internal playtest bots): AI agents that play builds, black-box, screenshot-driven; no verified pricing or effectiveness metrics in the notes. King's published work shows bot-based difficulty prediction for puzzle levels.
- Machinations, Ludo.ai: economy simulation and ideation or market tools; Ludo added an API and an MCP integration in 2026 per press.

### 2.7 World models
- Genie 3 / Project Genie: limited release with short generations and acknowledged physics and latency limits.
- Decart and others: neural game demos; impressive, not shippable.

## 3. What none of them do (gap analysis)

| Gap | Evidence in the landscape | Opportunity |
|---|---|---|
| Native store-ready mobile builds the creator owns | Most output is hosted or web; native tools are not games-native | Native Godot or Unity projects with CI and store pipeline |
| Verified quality (does it play, run fast, look right) | Self-reported quality; surveys note automated testing is less established | Enforced definition of done: deterministic playthrough, perf budget, visual critique |
| Design depth (economy, progression, retention) | Tools generate content, rarely design systems | Codex-driven design, simulators, analytics planning |
| Release and compliance | Not offered | Compliance pre-flight, store metadata, signing, approval gates |
| Licence and provenance | Mixed or undisclosed | Provenance manifests and licence checks |
| Taste control | Platforms optimise for volume | Human checkpoints on style, fun, submission |
| Post-launch operations | Mostly absent | Live-ops, A/B, remote config guidance |

## 4. This plugin's differentiation and honest limits

Differentiators (stated in terms the user can verify):
1. Output is a normal native project in Godot or Unity that the user owns; no hosted runtime or credit lock-in.
2. A machine-checkable definition of done (five gates) rather than "it generated".
3. Studio structure: specialist agents, a critic, and workflows for tournaments, reviews, balance and release candidates.
4. Tools: simulators and calculators for economy, gacha, progression, retention and LTV; level solvers; compliance and perf budgets.
5. Ethics and compliance built in (transparent odds, minors, AI disclosure tracking).
6. Human checkpoints where taste and legal responsibility live.

Limits to state honestly:
- It does not replace distribution, acquisition or the human judgement of fun.
- Generated assets need review and licence checking; quality varies by model and batch.
- Complex 3D and multiplayer remain costly regardless of tooling.
- Market success depends on the loop and the acquisition economics, not on the tooling.
- Claims of speed are only valid when measured on the project's own slice.

## 5. Positioning guidance

Messages that hold up:
- "Ship a real mobile game you own, with the checks a studio would run."
- "Faster to a playable loop, with verification before polish."
- "Design depth and economy modelling included."
Messages to avoid:
- "Make any game in one prompt" (contradicted by the category's own limits).
- Comparisons with specific competitors' numbers without citing and dating.
- Claims about being better than human studios without evidence.

Competitive response table:
| If the competitor is | Emphasise |
|---|---|
| A hosted consumer platform | Ownership, native distribution, monetisation control |
| A web builder | Native mobile performance and store pipeline |
| An engine with AI | Studio-level process and verification beyond code generation |
| A testing vendor | Complements: use their agents as a gate; plugin provides the pipeline |
| A general app builder | Games-native design depth and asset pipeline |

## 6. Research methods: overview and ethics

Principles:
- Define the decision first; choose the cheapest method that informs it.
- Triangulate: one quantitative signal (estimates or charts) plus one qualitative (reviews, teardown).
- Record source, access date and period for every datum.
- Respect terms of service and law: do not scrape in violation of store or tool terms, do not bypass paywalls, do not collect personal data from reviews beyond what is needed (use reviews as aggregated text; avoid storing usernames).
- Summaries in your own words; short quotes only with attribution.
- Do not enter credentials for any tool unless the user provides access explicitly; prefer free public views and the user's own accounts.

## 7. Third-party intelligence tools

Tools such as Sensor Tower and AppMagic provide estimated downloads, revenue, rankings, retention and demographics, ad intelligence and market reports. Other tools (AppTweak, Appfigures, data.ai-style services) focus on ASO and competitor tracking. Plan and pricing details are not verified in the notes; treat features and costs as unknown until checked on the vendor's site.

Workflow:
1. Define the comparable set (5-10 titles) and the countries.
2. Pull estimated downloads and revenue by month for 12-24 months; plot against release and update dates.
3. Look for inflection points: update, event, ad push, featuring.
4. Pull ranking history by country for top free and top grossing.
5. If available, pull retention and engagement estimates and demographic splits; label them as modelled.
6. Export to a table in the project folder; note the extraction date and the tool.
7. Cross-check at least one figure against a primary public statement or another tool.

Uses:
| Question | Tool output |
|---|---|
| How big is the genre in country X? | Category revenue and download estimates |
| Who is gaining? | Ranking and growth deltas |
| How dependent is a title on ads vs IAP? | Ad revenue or network intelligence where available |
| What creatives are they running? | Ad intelligence |
| Which keywords drive installs? | ASO tools |

Cautions: estimates for small apps and long-tail markets are noisy; coverage of China Android is limited; revenue estimates are gross consumer spend, not developer net; some tools bundle estimates differently across modules.

Free and low-cost alternatives: public press releases and reports by data firms, store chart pages, trade-press data digests, platform developer blogs, and the developer's own console analytics once live.

## 8. Store charts and page analysis

Chart reading:
1. Use the same chart type, country, device and time window for all comparables.
2. Observe daily for two weeks to separate spikes from stable positions; note holiday effects.
3. Record rank in top free and top grossing; a title high in free but low in grossing is ad or low-ARPU; the reverse suggests high monetisation per user.
4. Note new entrants in the top 200 and how long they hold.

Store page analysis:
- Title and subtitle keywords, icon style, screenshot sequence and first three screenshots, preview video, description, rating distribution, "what's new" cadence, in-app purchase list (price points reveal monetisation), age rating, size, privacy labels.
- IAP list on the page gives price ladders and pack structure; compare to your plan (`economy-design`).
- Record version history for update cadence.

## 9. Review mining

Procedure:
1. Collect a sample of 200-500 recent reviews per competitor across rating bands and the last 90 days, using store-permitted means (store listings, official APIs for your own app, tools licensed for this). Do not exceed rate limits or terms.
2. Strip personal identifiers; keep text, rating, date, version, country.
3. Define a theme codebook before coding: difficulty, ads, monetisation fairness, bugs and crashes, performance, content, social, controls, progression, onboarding, nostalgia and IP.
4. Code each review with up to three themes; an agent can do first-pass coding, a human samples 10% to verify.
5. Compute theme counts by rating band and trend over versions.
6. Extract top three pains and top three delights; convert to design requirements and anti-requirements.
7. Check for incentivised or bot patterns (repetitive text, bursts); discount them.

Output table:
| Theme | Share of 1-2 star | Share of 4-5 star | Trend | Design implication |
|---|---|---|---|---|

Cautions: reviews overrepresent extremes; developers prompt for ratings at emotional peaks; translated reviews lose nuance; early-adopter reviews differ from later ones.

## 10. Ad libraries and creative research

Sources: platform ad transparency libraries (social platforms publish ads that are currently running), ad intelligence in third-party tools, and video platforms.

Procedure:
1. Search by advertiser or game name in the libraries; note how many distinct creatives and how long each has run. Long-running creatives usually perform.
2. Classify creative types: gameplay capture, fake gameplay (a misleading practice to avoid), playable, UGC-style reaction, meme, character story, challenge.
3. Record hooks in the first three seconds, call to action, pacing, and the player fantasy sold.
4. Map creative claims to actual first-session reality; large gaps imply high early churn or review backlash.
5. Derive test hypotheses for your own creatives (see `marketing-ua`).

Cautions: libraries show running ads, not performance; regional visibility varies; do not copy creative assets (copyright); do not replicate misleading ad practices.

## 11. Search, keyword and community signals
- Store search suggestions and ASO keyword tools indicate demand and competition for terms.
- Community sizes and growth (forums, video views, social followers) indicate fandom, not revenue.
- Trade press and developer talks reveal strategy; verify claims.
- Game jams and indie charts reveal emerging mechanics early.

## 12. Synthesis templates

Competitor card:
| Field | Entry |
|---|---|
| Title, publisher, release date | |
| Genre and loop | |
| Monetisation | |
| Performance signals (with source, period) | |
| Live-ops cadence | |
| Strengths | |
| Weaknesses (review themes) | |
| Creatives | |
| What we do differently | |

Opportunity statement: "Players of [reference game] who want [unmet need] are under-served; evidence: [theme count, chart signal, creative gap]; our approach: [differentiator]; risk: [top risk]; test: [soft-launch hypothesis]."

## 13. Volatile facts (as of Oct 2026 — verify)

| Fact | Source |
|---|---|
| Astrocade raised $56M (announced May 2026); reports about 5M monthly active users and about 140M plays per month; round label (Series A and B vs Series B) differs by outlet | https://pocketgamer.biz/astrocade-raises-56m-to-expand-ai-powered-games-creation-platform/ and https://www.fortune.com/2026/05/05/astrocade-raises-56-million-series-b-sequoia-video-games-platform-ali-amir-sadeghian/ |
| Aippy reported first round at a $250M post-money valuation, about 2M monthly active users, 3M+ downloads (company-reported via news interview) | https://apps.apple.com/us/app/aippy-game-maker/id6749073777 (store listing; funding figures from 36Kr Europe, June 2, 2026) |
| Rosebud AI pricing and rights per its public page; code download and Steam export on a higher tier; no mobile export listed | https://rosebud.ai/pricing |
| GDevelop AI exports to web, Android, iOS and desktop (vendor guide); credit-based plans | https://app.cinevva.com/guides/ai-game-generators-2026 |
| Unity AI open beta reported from May 4, 2026, replacing Unity Muse (secondary source) | https://unity.com/features/ai |
| Roblox 4D generation beta, early February 2026; company-reported engagement figures | https://about.roblox.com/newsroom/2026/02/accelerating-creation-powered-roblox-cube-foundation-m |
| Sett reported a $30M Series B on March 30, 2026 (company claims on speed and cost are unverified) | https://siliconangle.com/2026/03/30/sett-raises-30m-grow-agent-based-ai-platform-arcosians/ |
| Vibe Jam 2026: 945 submissions under a rule requiring mostly AI-written code, run April 1 to May 1, 2026 | https://vibejam.com/2026/press |
| Genie 3 / Project Genie opened Jan 29, 2026 to a limited subscriber tier; generations limited to 60 seconds | https://blog.google/innovation-and-ai/models-and-research/google-deepmind/project-genie/ |
| Epic UEFN conversational NPC feature reported in v40.20 (April 16, 2026) | https://respawn.outlookindia.com/gaming/gaming-news/epic-launch-ai-voice-npcs-via-gemini-elevenlabs-in-fortnite-uefn |
| Survey "AI for Games in the Foundation Model Era" (Sept 2026) notes automated testing and repeated revision are less established | https://arxiv.org/abs/2609.16679 |
| King bot-based difficulty prediction (2018 paper): used across 1,000+ levels | https://www.Gwern.net/doc/reinforcement-learning/imitation-learning/2018-gudmundsson.pdf |

Gaps in the research: several companies could not be checked for 2026 (Bitmagic, Exists.ai, Playgent, Spawn, Hiber, Ludeo, Lovable and v0 for games, SIMA 2); Sensor Tower, AppTweak and Appfigures API pricing was not researched. Many figures are vendor-reported.

## 14. Checklists

Competitor claim checklist:
- [ ] Claim traced to primary source or flagged vendor/secondary
- [ ] Date and metric definition recorded
- [ ] Conflicts between sources noted
- [ ] No unverified funding or user numbers in public materials

Research session checklist:
- [ ] Decision stated up front
- [ ] Comparable set and countries fixed
- [ ] At least one quantitative and one qualitative signal
- [ ] Terms of service respected, no personal data kept
- [ ] Output saved with dates and tool names
