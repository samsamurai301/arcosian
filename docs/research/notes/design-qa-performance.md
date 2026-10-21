# AI Agent Pipelines for Mobile Game Design, Content Generation, Automated QA/Playtesting, and Mobile Performance (state as of October 2026)

Research note scope: what an automated (AI-agent-driven) system can use to (a) produce game designs and balanced content, (b) verify the game works and is balanced/fun without human testers, and (c) hit mobile performance targets. Research date: 2026-10-18.

Method note for the report writer: about 40 tool calls were made. The session's shared web-search budget ran out partway through, so several sub-topics (GameDriver, Maestro, Xcode Instruments/xctrace CLI, Snapdragon Profiler, RenderDoc CLI, Android GPU Inspector CLI, Wave Function Collapse best practices, GameRefinery feature data) could not be verified. They are listed under Gaps. Where I add background knowledge that I could not verify this session, it is labeled "unverified" and placed under Inferences, not Cited Findings.

---

## 1. AI-assisted game design: GDDs, core loops, economy/progression balance, design agents

### Takeaway
LLMs can already write GDDs that experts score as clear and detailed, and commercial tools (Ludo.ai, Unity AI) now expose APIs or MCP hooks an agent can call. The strongest evidence for automated *balance* comes from simulation-based approaches: King's human-like bots for level difficulty (in production since about 2018) and, in research, multi-agent LLM self-play combined with Bayesian optimization (RuleSmith, Feb 2026). LLM "taste" for creativity is roughly human-level, not better, so a pipeline should generate options and then check them by simulation rather than trusting the LLM's judgment.

### Cited Findings
**GDD generation and GDD-to-prototype**
- A 2025 comparative study generated hyper-casual GDDs with an LLM. One academic and three industry experts scored them. The LLM GDD averaged 4.71/5 and the human-expert GDD 3.29/5. The LLM was stronger on understandability and detail, but performed similarly to the human on creativity and visual content. (Small sample, single genre.) — [Aydınalp, Doğan, Bal 2025, Bitlis Eren Univ. J. Sci.](https://openaccess.izu.edu.tr/entities/publication/b51838a1-dd18-4aa8-b6de-1d5450c8a0e2/full)
- arXiv:2509.08847 (Sept 2025) goes in the reverse direction. It parses GDDs into structured game specs and then synthesizes Unity C# templates, using a fine-tuned LLaMA-3 plus a custom Unity integration package. The authors report a 4.8/5 average on their own metrics (self-evaluated). — [arXiv:2509.08847](https://arxiv.org/abs/2509.08847v1)
- The 120-page survey "AI for Games in the Foundation Model Era" (arXiv:2609.16679, 15 Sept 2026) groups the field into six roles: playing/acting, modeling players and games, designing, building/maintaining, runtime generation/adaptation, and testing/evaluating. It notes that design specifications can drive executable implementations, and that play or testing feedback can guide revision. It also says evaluation is most standardized only for "bounded game playing", and that automated testing and repeated software revision are "less established". Rules, engine interfaces and state representations remain game-specific, so claims need validation in the target setting. — [arXiv:2609.16679](https://arxiv.org/abs/2609.16679)

**Commercial design tools an agent can drive**
- Ludo.ai expanded from a pre-production tool into a "complete game design hub" covering market intelligence through game validation. Features include a "Ludo Score" that rates creativity, mechanics and similar factors, a Game Ideation Hub, image generation for concepts, AI-assisted task management and documentation, and team collaboration. — [PocketGamer.biz](https://www.pocketgamer.biz/ludoai-evolves-into-complete-game-design-hub-with-major-update)
- In April 2026, Ludo.ai released a beta API and Model Context Protocol (MCP) integration for generating production-ready game assets inside existing workflows. This is directly callable by an agent. (Press coverage; I did not find the vendor's own announcement.) — [App Developer Magazine](https://appdevelopermagazine.com/search/ai-game-design)
- Ludo's existing capabilities include generating game concepts, elements and mechanics, plus game and image search, stats, top charts and image generation. (Third-party directory.) — [WebCatalog](https://webcatalog.io/es/apps/ludo)
- Unity AI entered open beta for all Unity 6 developers on May 4, 2026. It replaces the deprecated Unity Muse. Pricing: Personal gets a 14-day, 1,000-credit trial and then $10/month for 1,000 credits; Pro, Enterprise and Industry plans include it. Unity says project data will not be used to train models. (Secondary source.) — [BuildFastWithAI](https://buildfastwithai.com/blogs/unity-ai-open-beta-guide-2026); [Unity AI page](https://unity.com/features/ai)

**Automated balance and difficulty via simulated players**
- RuleSmith (arXiv:2602.06232, Feb 5, 2026) runs multi-agent LLM self-play combined with Bayesian optimization over a multi-dimensional rule space. It allocates more evaluation games to promising rule candidates and fewer to exploratory ones. On CivMini, a simplified civ-like game, it converged to well-balanced configurations with interpretable rule changes. — [arXiv:2602.06232](https://arxiv.org/abs/2602.06232)
- Xiao & Yang (arXiv:2410.02829, 2024, older) argue that LLMs are not human-level players but can serve as testers for measuring game difficulty. They tested this on Wordle and Slay the Spire. — [arXiv:2410.02829](https://arxiv.org/abs/2410.02829)
- King (Candy Crush), 2018: a CNN trained on player data predicts the most "human" move. Bot playthroughs then predict level difficulty. The paper says the agent had been in use for more than a year, across more than 1,000 new Candy Crush Saga levels. — [Gudmundsson et al. 2018 (King)](https://www.Gwern.net/doc/reinforcement-learning/imitation-learning/2018-gudmundsson.pdf)
- King follow-up work: difficulty estimates take under a minute, versus 7 days of human playtesting per 15-level episode previously. Simulating several player strategies beat a single-strategy baseline, with MAE improved about 13% and MSE about 23%. — [Politecnico di Milano thesis (King collaboration)](https://www.politesi.polimi.it/handle/10589/141799)
- In 2024, King AI Labs described a playtesting bot that automatically adjusts levels designers flag, against set criteria; designers then review the best solutions. — [WN Hub, June 2024](https://wnhub.io/news/Generative_AI/item-43934)
- King has also used bots built with MCTS, automatic heuristic construction and NEAT to predict success rates and run automated performance testing. — [StickyMinds talk](https://www.stickyminds.com/presentation/using-artificial-intelligence-test-candy-crush-saga-game)
- A 2026 King-affiliated paper reportedly compares BERT and graph-attention-network models against the CNN baseline for human-like playtesting, with stronger performance on hard configurations. (Seen only via a document mirror; I could not confirm the arXiv ID.) — [docshare mirror](https://docshare.wps.com/document/comparative-analysis-of-gat-and-bert-for-human-like-playtesting/86250/_payload.json)

### Inferences
- A sensible agent pattern: the LLM drafts the GDD, core loop and economy tables. These are encoded as a machine-readable spec (JSON/YAML) and handed to a simulator. Simulated players (heuristic, MCTS, RL or LLM agents) then estimate difficulty, pass rates and resource flows. An optimizer (Bayesian optimization, as in RuleSmith) tunes parameters. The LLM's creative judgment is used for ideation, not as the balance oracle.
- For puzzle and casual mobile games (match-3, block puzzles), King's work is the strongest production evidence that bot-predicted difficulty is good enough to replace most human difficulty playtests. It still relies on player data to make the bots human-like. A brand-new game with no player data would need heuristic or LLM agents first, then recalibration after soft launch.
- Ludo.ai's API/MCP and Unity AI make design and asset steps agent-callable. Neither, from what I found, offers automated balance verification.

### Gaps
- No independent evaluation of Ludo.ai's "Ludo Score" predictive validity was found.
- No 2025–2026 paper was found that end-to-end generates a *mobile F2P* GDD plus economy and validates it against real retention data.
- Specific "game design agent" multi-agent frameworks from 2026 (beyond RuleSmith) could not be searched; the search budget was exhausted.

---

## 2. Procedural content generation (PCG) and economy simulation

### Takeaway
Unreal's PCG Framework became production-ready in UE 5.7 (Nov 2025). For LLM-driven level generation, the consistent lesson is to generate and then verify playability with a solver or agent: LLM levels often fail, and hard levels fail much more often. For economy design, Machinations is still the dominant dedicated tool. I found no well-known open-source Python equivalent, so agents will likely write their own simulators (Monte Carlo in Python or spreadsheets) or drive Machinations.

### Cited Findings
**Engine PCG frameworks**
- Epic's release page states that the "Procedural Content Generation framework (PCG) is now Production-Ready" in UE 5.7. — [Unreal Engine What's New](https://www.unrealengine.com/whats-new)
- UE 5.7 PCG runs about 2x faster than UE 5.5 and adds a PCG editor mode for spline, volume and paint workflows. Epic recommends verifying runtime performance and scalability before production use. The Procedural Vegetation Editor remains experimental. — [Digital Production](https://digitalproduction.com/2025/11/12/unreal-engine-5-7-foliage-pcg-and-in-editor-ai/); [PCGH 5.7 preview](https://www.pcgameshardware.de/Unreal-Engine-Software-239301/News/57-Preview-Download-Changelog-Nanite-Foliage-Release-Beta-1482846/); [80.lv overview of 5.6/5.7 PCG](https://80.lv/articles/what-s-new-in-pcg-in-ue5-6-ue5-7)
- No mobile-specific guidance for UE PCG was found. — (see Gaps)

**LLM-based and classical PCG: evaluation evidence**
- A 2024 survey covers PCG methods with insights on emerging LLM integration. — [arXiv:2410.15644](https://arxiv.org/pdf/2410.15644)
- Withington, Cook & Tokarchuk (FDG 2024) find that consensus on how to evaluate PCG systems is limited, and propose a taxonomy of evaluation methods. — [arXiv:2404.18657](https://arxiv.org/pdf/2404.18657)
- An early LLM level generation paper (GPT-2 variants, 2023) reports novelty, playability and diversity, and frames prompt-based controllability as the main appeal. (Older.) — [arXiv:2302.05817](https://arxiv.org/pdf/2302.05817)
- An LLM plus GAN approach for Snake levels (FedCSIS 2025) validated LLM-generated, difficulty-labeled levels with A* pathfinding. Playability was 87% for easy levels and only 36% for hard levels. — [FedCSIS 2025, Annals CSIS vol. 43](https://annals-csis.org/Volume_43/drp/1909.html)
- Simulation-based metrics analyze a planning agent's behavior to measure the diversity and difficulty of generated levels. — [Beukman et al., arXiv:2201.10334](https://arxiv.org/abs/2201.10334v2)

**Economy and progression simulation**
- Machinations describes itself as a platform to "describe any economy, process or loop and simulate it in seconds". Its product areas are Design, Predict, Balance and Integrate (Machinations and spreadsheets), and it advertises a "Build systems using AI" feature. Named users include Amazon Games, Wooga, Zynga, Big Fish, LEGO and Behaviour Interactive. Use cases include F2P, LiveOps (it publishes a LiveOps handbook) and tokenomics. It has a free start; pricing tiers are not listed on the homepage. — [machinations.io](https://machinations.io)
- Listed alternatives: Flowtrix, a paid, Windows, node-based system and economy designer. Arcweave and articy:draft are narrative tools, not economy simulators. No open-source Python economy simulator surfaced. — [AlternativeTo](https://alternativeto.net/software/machinations)

### Inferences
- For an agent pipeline, writing a custom Monte Carlo economy simulator (for example in Python, driven by the same JSON economy spec the game reads) is likely more automatable than Machinations' GUI-centric workflow. I could not verify whether Machinations exposes a public API suitable for headless simulation.
- PCG best practice for an agent: always couple the generator with an automated verifier, such as an A*/BFS solver for puzzles or reachability, a bot playthrough for difficulty, or constraint checks. Reject or repair failing outputs. Hard-difficulty content needs the most verification, given the 36% playability for hard Snake levels.
- Unverified background knowledge: Wave Function Collapse is good at local tile coherence but does not guarantee global properties (connectivity, solvability) without extra constraints or backtracking. Grammar-based generators give stronger structural control, and noise suits terrain and resource distribution. Unity has no first-party PCG framework comparable to Unreal's; Unity developers rely on custom code or Asset Store tools. These points need verification.

### Gaps
- WFC, grammar and noise best-practice sources and Unity PCG tooling could not be searched (search budget exhausted).
- No primary data was found on whether Machinations has an API or SDK for headless simulation, Unity/Unreal plugins, or a Monte Carlo feature as of 2026.
- No 2025–2026 survey specifically benchmarking LLM level generators on playability was found.

---

## 3. What makes mobile games retain players (industry data)

### Takeaway
Retention benchmarks for 2026 are mostly repackaged GameAnalytics data. The median mobile game keeps about 22% of players at D1, under 4% at D7 and about 0.7–0.8% at D30; the top 1% reach about 64–68% D1. Practitioner consensus points at the FTUE and "time to fun" as the biggest D1 lever, and the D7/D1 ratio as the diagnostic. The market itself is flat (2025 mobile game IAP about $82B, +1%; H1 2026 IAP down 2% and downloads down 12%), which favors retention, LiveOps and hybrid-casual designs.

### Cited Findings
**Retention benchmarks**
- GameAnalytics benchmarks via secondary write-ups (16,000+ live mobile games): median D1 about 22%, D7 just under 4%, D30 about 0.7–0.8%. The top 1% of games hold 64–68% D1 and 13–15% D30. — [Segwise (citing GameAnalytics 2026)](https://segwise.ai/blog/mobile-gaming-app-user-retention-strategies); [Playio 2026 benchmarks](https://blog.playio.co/d1-d7-d30-retention-benchmarks-2026)
- A practitioner "viability screen" for marketed titles is 25–30% D1, 10–15% D7 and 3–6% D30; top-tier is 45%+ D1, 25%+ D7 and 12%+ D30. Some sources call the commonly cited 30–35/10–15/3–6 screen a working heuristic, not a published median. — [Playio](https://blog.playio.co/d1-d7-d30-retention-benchmarks-2026); [Galaxy4Games](https://galaxy4games.com/en/knowledgebase/blog/mobile-game-retention-benchmarks-2026-d1-d7-d30-data-for-publishers)
- Among top-quartile games, D1 runs 31–33% on iOS versus 25–27% on Android. Genre splits are inconsistent across sources (hyper-casual D1 cited at about 33% to 40%; mid-core D30 about 10–12%), and some trace back to AppsFlyer Q3 2022 data. — [Segwise](https://segwise.ai/blog/mobile-gaming-app-user-retention-strategies); [AppAgent](https://appagent.com/blog/mobile-game-retention-benchmarks/)

**FTUE, core loop, session diagnostics**
- D7/D1 ratio diagnostic: below 0.30 points to a first-session or FTUE problem; 0.30–0.44 points to weak engagement on days 2–5. The source attributes this to Lancaric's 2025 "Soft Launch Bible" and Traplight's 2022 analysis, and calls it practitioner consensus, not hard rules. — [GameDev.net](https://gamedev.net/blogs/entry/2298160-the-d7d1-retention-ratio-for-mobile-games-a-complete-guide)
- "Time to fun": if the aha moment takes more than about 90 seconds, a significant share of users never return for a second session. The same post repeats an unsourced claim that onboarding optimization can lift retention by up to 50%; treat it with caution. — [Playio (Aug 2026)](https://blog.playio.co/mobile-game-onboarding-retention)
- The core loop is the repeated chain of gameplay actions that forms the main experience; the FTUE is how players first experience that loop. AppFollow's 2026 guide says the FTUE shapes D1 and recommends fixing onboarding before late-game retention. — [AppFollow 2026](https://appfollow.io/blog/mobile-game-retention); [Metacore talk via PlaytestCloud](https://start.playtestcloud.com/blog/perfecting-the-first-time-user-experience-in-mobile-games)
- Deconstructor of Fun (Michail Katkoff, ex-Rovio and Zynga) offers consulting on retention design. I found no specific 2025–2026 FTUE article from them. — [Deconstructor of Fun consulting](https://www.deconstructoroffun.com/consulting)

**Market context**
- Sensor Tower State of Gaming 2026 (2025 data): mobile game IAP revenue rose 1% to about $82B with slowing downloads (52B). The growth came from retaining and monetizing existing players through LiveOps, events and IP collaborations. — [Sensor Tower press release](https://sensortower.com/press/press-release-sensor-tower-state-of-gaming-gaming-drove-52-billion-downloads-82b-iap-revenue-on-mobile-and-12b-premium-revenue-on-steam)
- Hybrid-casual had the largest spending jump in 2025 (+17.1%, $3.5B to $4.2B). In H1 2026, mobile game IAP totalled $40B (-2% YoY) and downloads 24B (-12%). Block Blast! topped downloads; Last War, Honor of Kings and Whiteout Survival led grossing in Q1 2026. — [Mobilegamer.biz data digest](https://mobilegamer.biz/data-digest-sensor-towers-h1-analysis-hay-days-comeback-julys-top-games-big-krafton-numbers-and-more/); [Bolsamania (Sensor Tower)](https://www.bolsamania.com/nota-de-prensa/mercados/sensor-tower-state-of-gaming-gaming-drove-94-billion-in-revenue-in-2025-downloads-reached-52-billion--21828650.html)
- Strategy (4X) was 2025's hot genre. Winners combined accessible hooks, heavy social loops and deep monetization. (A LinkedIn summary of Sensor Tower's State of Mobile 2026; secondary.) — [LinkedIn summary](https://fi.linkedin.com/in/teemu-tuulari-aa094028)

### Inferences
- An automated pipeline can turn these benchmarks into acceptance targets for soft-launch analytics (for example D1 ≥ 30%, D7/D1 ≥ 0.33). Pre-launch, it can only proxy them, for instance by measuring bot time-to-first-reward and first-session length. None of the AI QA tools found claim to predict retention.
- Given flat downloads and growing hybrid-casual, an agent-built game is most likely to compete in hybrid-casual or puzzle genres. These have short loops, data-driven level difficulty (King-style bots apply) and lower content-production cost.

### Gaps
- The GameAnalytics 2026 benchmark report itself and GameRefinery feature/genre data were not accessed directly; figures come from secondary blogs.
- No reliable source was found for recommended session length by genre in 2026.

---

## 4. Automated playtesting and functional QA: tools, RL/VLM agents, effectiveness in 2026

### Takeaway
There are three tiers. (1) Deterministic, scriptable frameworks are mature and fully agent-automatable: Unity Test Framework, AltTester for Unity/Unreal object-level control, Appium for menus, GdUnit4/GUT for Godot, and device farms. (2) Black-box, plain-English, vision-based agent services are commercially available: nunu.ai (Android/iOS real devices, Windows), modl.ai (Android/PC, iOS in development) and Razer QA Companion-AI (zero-integration, GDC 2026). They claim crash, softlock and visual-glitch detection, but publish no independent effectiveness numbers. (3) Research shows LLM/VLM agents are useful but far from autonomous: TITAN reached 95% task completion and is deployed in 8 QA pipelines, but the best model found only 48% of injected bugs on GBQA (Claude Opus 4.6, thinking mode). Raw-pixel VLMs still perform badly at real-time games.

### Cited Findings
**Black-box AI QA services**
- nunu.ai: tests are written in plain English (for example "complete the tutorial"). No scripts, engine integration or SDK are needed to start. The agent looks at the screen and acts like a human. Recent posts: "Meet William: the best AI agent for testing games & apps on real devices" (May 6, 2026); "PR Testing Agents" for end-to-end autonomous real-device testing (Dec 9, 2025); "nunu for Windows" (Jun 17, 2026); "APK Arena" phone-use benchmark (Jul 10, 2026). Listed case studies: Stormforge and Hogwarts Legacy. No pricing or effectiveness metrics are on the blog. — [nunu.ai blog](https://nunu.ai/blog)
- nunu.ai funding: founded 2022 in San Francisco, $8M total including a $6M seed in March 2025. — [Tracxn](https://tracxn.com/d/trending-business-models/startups-in-gameplay-testing/__PNvHMlYAxLu-StDwhbuTF8dMfY0ciZPUcOG330iy27Y/companies)
- APK Arena (nunu.ai) has 50+ real problems from building testing agents, in 7 categories: primitives/gestures, vision, memory, IQ, tempospatial, games and multi-step tasks. Agents see pixels only, with no accessibility IDs. GPT-5.5, Opus 4.8 and "Fable 5" are named as the first models to handle dice-counting well. A previously unsolvable sequence-memory level is now solved by the agent writing computer-vision code. In tower defense, weaker models misplace towers. No numeric scores are in the text. — [nunu.ai APK Arena](https://nunu.ai/blog/apk-arena)
- modl.ai: black-box, "no SDKs, plugins, or code changes required". You upload a build; agents read the screen and send simulated input. It supports Android and desktop PC today, with iOS in development and console being expanded. It suits match, narrative, card, turn-based and UI-heavy games; very fast or timing-critical gameplay is "not fully supported yet". It claims to detect visual glitches and missing assets, crashes, broken menus, softlocks, performance drops, logic bugs and log exceptions. Reports include screenshots, video, logs and an AI severity score. It can be triggered from CI. No pricing or case studies are listed. — [modl.ai](https://modl.ai)
- A secondary review cites a 50% reduction in manual QA cost for modl.ai; this is marketing-adjacent and unverified. — [AI Central Resources review](https://www.aicentralresources.com/tool/modlai)
- Razer QA Companion-AI was updated at GDC 2026 (announced Mar 9, 2026). It is zero-integration and vision-based (no SDK or plugin), reviews gameplay footage to flag rendering, physics, animation and collision issues, and generates functional and negative test cases from prompts or GDDs. Autonomous gameplay agents were shown only as an early preview. It builds on QA Copilot (GDC 2025). No independent results were found. — [Razer newsroom](https://www.razer.com/newsroom/company-news/razer-at-gdc-2026); [Razer blog](https://www.razer.com/blog/ai-that-plays-to-test-razer-qa-companion-ai-at-gdc-2026/); [PocketGamer.biz](https://www.pocketgamer.biz/razer-reveals-ai-tools-to-speed-up-game-development-pipelines); [KitGuru](https://www.kitguru.net/gaming/joao-silva/razer-goes-all-in-on-ai-at-gdc-2026/)
- Regression Games (founded 2022, $4.2M seed led by NEA) moved toward AI agent testing for Unity. CB Insights shows no funding since 2022. No 2025–2026 acquisition or pivot news was found. — [CB Insights](https://www.cbinsights.com/company/regression-games)

**Scriptable, deterministic automation frameworks**
- AltTester (formerly AltUnityTester) gives object-level access inside Unity and Unreal scenes. Unity SDK v2.3.1 and Unreal SDK v1.2.1 were released Apr 3, 2026. — [AltTester blog](https://alttester.com/blog/page/8)
- AltTester's Python setup was verified in June 2026 with alttester-driver 2.2.5, Appium-Python-Client 4.0.0 and pytest 8.0.0. — [TestMu AI docs](https://www.testmuai.com/support/docs/alttester-unity-game-automation/)
- Sauce Labs runs AltTester tests on real devices, connecting the C# driver through Sauce Connect or a public AltTester Desktop VM. iOS sessions use the official Appium WebDriverAgent starting with appium3-2026-01. — [Sauce Labs AltTester docs](https://docs.saucelabs.com/mobile-apps/automated-testing/alttester/unity/)
- Appium works for menus, settings and companion UI, but "does not see inside game engines' internal scene graphs". For in-scene gameplay, use AltTester. — [Sauce Labs Appium for Games](https://docs.saucelabs.com/mobile-apps/automated-testing/appium/appium-for-games/)
- A May 2026 comparison calls AltTester the best tool for Unity-specific automation, with trade-offs: it needs source access, adds SDK overhead and was described as Unity-only, although an Unreal SDK exists per AltTester. — [Drizz 2026 comparison](https://www.drizz.dev/post/best-mobile-game-testing-tools-in-2026-complete-comparison)
- GdUnit4 (Godot) has a scene runner that simulates mouse and keyboard input and waits for signals. It has a headless CLI with JUnit XML and HTML reports and GitHub Actions examples. GUT has a headless CLI (`gut_cmdln.gd`), but I could not confirm an input-simulation API. — [GdUnit4 repo](https://fr.github.com/MikeSchulze/gdUnit4); [Godot Asset Library](https://godotengine.org/asset-library/asset/1522)
- Firebase Test Lab supports Game Loop tests on iOS and Android, alongside instrumentation and Robo tests. Third-party pricing: Blaze plan about $1 per virtual-device-hour and $5 per physical-device-hour; Spark free tier 10 virtual and 5 physical tests per day. (Third-party; verify on Firebase's pricing page.) — [Back4App](https://blog.back4app.com/firebase-test-lab/); [Drizz FTL guide](https://www.drizz.dev/post/firebase-test-lab-guide); [issoh.co.jp (Aug 2026)](https://www.issoh.co.jp/tech/details/17046/)

**Reinforcement learning agents**
- Unity ML-Agents is maintained, not deprecated. Release 4.0.3 (2026-04-17) supports Fast Enter Play Mode and upgrades to Sentis 2.6.1. A Unity staff member said Unity is "not deprecating ML Agents" and plans consolidated packaging and Inference Engine integration. — [ML-Agents changelog](https://docs.unity3d.com/Packages/com.unity.ml-agents@4.0/changelog/CHANGELOG.html); [Unity Discussions](https://discussions.unity.com/t/is-ml-agents-being-deprecated/1643681/3)

**LLM/VLM game-playing and testing agents (research)**
- TITAN (arXiv:2509.22170, Sept 2025) is an LLM agent for MMORPG testing. It combines state abstraction, action prioritization, action-trace memory with reflection, and LLM bug oracles. It reached 95% task completion and found 4 previously unknown bugs on two commercial MMORPGs, one PC and one mobile. It is reportedly deployed in 8 real-world game QA pipelines. — [arXiv:2509.22170](https://arxiv.org/abs/2509.22170)
- GBQA (arXiv:2604.02648, ICLR 2026 workshop) has 30 games and 124 human-verified bugs. A ReAct-plus-memory baseline QA agent led by Claude Opus 4.6 (thinking) found 48.39% of bugs. The authors conclude that "autonomous bug discovery remains highly challenging". — [arXiv:2604.02648](https://arxiv.org/abs/2604.02648)
- VideoGameBench (2025, revised May 2026): VLMs playing 1990s games from raw frames in real time reached under 1% average progress in the original results. — [arXiv:2505.18134](https://arxiv.org/html/2505.18134v3)
- GameWorld (Apr 2026) is a standardized, verifiable evaluation of multimodal game agents across keyboard/mouse computer-use and semantic action spaces on browser games. — [arXiv:2604.07429](https://arxiv.org/pdf/2604.07429)
- The 2026 survey mentions PlaytestArena, in which a GUI agent plays browser games and judges observed behavior against task-specific rubrics. — [arXiv:2609.16679 (HTML)](https://arxiv.org/html/2609.16679)

### Inferences
- Effectiveness in 2026 by bug class (synthesizing the above):
  - **Crashes and exceptions:** reliably detectable by any automated driver plus log and crash capture (device farms, modl.ai log parsing). This is the most mature category.
  - **Softlocks and progression blockers:** detectable when the agent has a goal ("complete the tutorial") and a timeout or no-progress heuristic. modl.ai and nunu claim this, but publish no rates.
  - **Difficulty spikes:** best handled by many simulated playthroughs with statistics (King approach, RuleSmith, Xiao & Yang). Single VLM playthroughs are too noisy and expensive.
  - **Visual bugs:** VLMs catch obvious glitches but have high false-positive rates (see Section 5).
  - **Logic bugs from open exploration:** about 50% recall at best (GBQA).
- Recommended layering for an agent: (1) unit and integration tests in the engine test framework (headless, every commit); (2) scripted end-to-end flows with AltTester plus Appium on emulators and device farms; (3) large-scale headless simulation bots that call game logic directly (no rendering) for balance and difficulty; (4) VLM or plain-English agents (nunu, modl.ai, or a self-built Claude/GPT computer-use loop over adb screenshots) for exploratory and "does the FTUE work" checks; (5) human review of flagged items. Designing the game with a deterministic, headless-runnable logic layer and a semantic action API makes layers 1 and 3 dramatically cheaper than pixel-based play.
- Fast, timing-critical gameplay is explicitly a weak spot (modl.ai's own caveat; VideoGameBench <1%). Turn-based, puzzle and UI-heavy mobile genres are the best fit for current agents.

### Gaps
- GameDriver, Maestro and BrowserStack App Automate's game-specific features could not be researched (search budget exhausted).
- No independent head-to-head benchmark of modl.ai, nunu.ai or Razer was found. All effectiveness claims are vendor-sourced.
- nunu.ai and modl.ai pricing is not public.
- The APK Arena numeric scores are in an image and were not extractable.

---

## 5. Visual QA: screenshot diffing, golden images, VLM-based visual review

### Takeaway
Golden-image testing (Unity Graphics Test Framework's `ImageAssert.AreEqual` with tolerances) is mature but brittle across GPUs and drivers. VLM-based review catches many obvious glitches, but VideoGameQA-Bench (May 2025, older models) shows high false-positive rates and poor visual-regression and fine-UI accuracy. The authors estimate GPT-4o's precision would fall to about 20% at a realistic 5% glitch base rate. Use VLMs as triage, not as a gate.

### Cited Findings
- Unity Graphics Test Framework: `ImageAssert.AreEqual()` compares a rendered camera output against a reference image, with per-pixel and whole-image thresholds to absorb hardware and driver differences. Workflow: run tests, which write TestResults.xml and an ActualImages folder; approve them into ReferenceImages, organized by ColorSpace/Platform/GraphicsAPI (newer versions add a shared ReferenceImagesBase). It can auto-generate test cases from project scenes. — [Unity Graphics Test Framework docs](https://docs.unity3d.com/Packages/com.unity.testframework.graphics@8.9/manual/index.html)
- Unity itself renders scenes on all supported devices and compares them against approved per-device reference images. — [Unity blog: Graphics tests](https://blog.unity.com/technology/graphics-tests-the-last-line-of-automated-testing)
- Graphical tests are prone to false positives and flakiness from GPU, driver and configuration differences. A community guide recommends simplifying test scenes, for example a solid background with no skybox. — [Community guide](https://kissyagni-blog.statichost.eu/how-to-do-graphical-tests-in-unity.html)
- VideoGameQA-Bench (Univ. of Alberta and Sony Interactive Entertainment, May 2025; older models) has 2,236 image and 1,200 video samples across 9 tasks. Highlights:
  - **Image glitch detection:** GPT-4o 82.8%, GPT-4.1 81.3%, Gemini 2.5 Pro 75.4%, Claude Sonnet 3.7 65.1%.
  - **Visual regression:** best is o4-mini at 45.2%; GPT-4o 31.6%.
  - **UI unit tests:** best is Gemini 2.5 Pro at 40%.
  - **Video glitch detection:** Gemini 2.5 Pro 78.1%.
  - **Localizing glitch onset in video (needle in a haystack):** at most about 36%.
  - GPT-4o's image false-positive rate was 17.8%, implying about 19.8% precision at a 5% glitch prevalence. Models hallucinate clipping, miss unusual poses and common-sense errors, and miss small UI details.
  - The authors conclude that VLMs are not yet ready for many game QA tasks.
  — [arXiv:2505.15952](https://arxiv.org/html/2505.15952v1)
- A 2026 paper evaluates VLMs as autonomous agents for detecting geometry clipping in game QA (title only seen; findings not retrieved). — [arXiv:2607.25921](https://arxiv.org/pdf/2607.25921)
- Razer QA Companion-AI (GDC 2026) markets vision-based detection of rendering, physics, animation and collision issues from gameplay footage, with no published accuracy. — [KitGuru](https://www.kitguru.net/gaming/joao-silva/razer-goes-all-in-on-ai-at-gdc-2026/)

### Inferences
- A practical visual-QA stack for an agent:
  1. Deterministic golden-image tests for key screens (main menu, HUD, shop, results) rendered on a fixed emulator or GPU in CI, with tolerances.
  2. Structural UI checks through engine introspection (AltTester object tree: text overflow, off-screen elements, missing sprites, null textures). These are more reliable than pixels.
  3. VLM review of screenshots and short clips as a triage step, with a strict rubric (for example "list any text clipping, missing textures, overlapping UI, placeholder art") and multiple samples or majority voting to reduce false positives. Escalate only consistent flags.
  4. A subjective "does this look polished" VLM judgment is the least validated. No benchmark measuring aesthetic or polish judgment was found.
- VideoGameQA-Bench predates 2026 frontier models; current models likely score higher, but no updated numbers were found.

### Gaps
- No 2026 re-run of VideoGameQA-Bench with current models was found.
- No benchmark of VLMs judging aesthetic quality or "polish" of mobile game UI was found.
- Perceptual-diff tools (SSIM-based, for example) used in game CI were not researched (search budget exhausted).

---

## 6. Mobile performance: profiling tools, automated budgets in CI, best practices, headless scriptability

### Takeaway
Most of the mobile performance toolchain can be scripted. Unity Performance Testing package results go to JSON, Perfetto Trace Processor has a Python API, Arm Performance Studio's Performance Advisor generates reports in CI, and ADPF and Unity Adaptive Performance handle thermal headroom at runtime. Key targets: 16.6 ms per frame at 60 fps and 33.3 ms at 30 fps; ASTC with ETC2 fallback via Play's texture compression format targeting; Play Asset Delivery above 200 MB; Apple's Background Assets instead of the deprecated On-Demand Resources; and 16 KB page-size compliance for Google Play.

### Cited Findings
**Profiling and automation tools**
- Unity Performance Testing Extension (com.unity.test-framework.performance, v3.0.3 listed for 2020.3–2023.2) samples Profiler markers and custom metrics in the Editor and in players, and records build and player metadata for cross-hardware comparison. Unity Test Framework always builds a development player for these runs. — [Unity Performance Testing docs](https://docs.unity3d.com/Packages/com.unity.test-framework.performance@3.0/manual/index.html)
- Example CI usage: `[UnityTest, Performance]` with `Measure.Frames()` after warmup and `Measure.Custom` for peak memory, run in batch mode. Results are written to JSON for storage as CI artifacts and comparison against baselines. (Third-party blog; verify API names.) — [BugNet blog](https://bugnet.io/blog/performance-regression-tracking-builds)
- A third-party agent skill ("game-perf-profiling") combines Unity Profiler, Profile Analyzer and the Performance Testing package with pass/fail budgets of 16.6 ms (60 fps) and 33.3 ms (30 fps), CI regression tests and per-platform budget reports. This is an example of the pattern already packaged for agents. — [Tessl registry](https://tessl.io/registry/testland/game-perf-profiling)
- Unity Memory Profiler captures and compares snapshots, but works only with development builds and the Editor. Capturing can briefly freeze the app and allocate memory; programmatic capture is via `MemorySnapshot.RequestNewSnapshot`. — [Memory Profiler docs](https://docs.unity3d.com/Packages/com.unity.memoryprofiler@0.7/manual); [Unity blog: Memory Profiler 1.0](https://unity.com/blog/engine-platform/everything-you-need-to-know-about-memory-profiler)
- Arm Performance Studio (formerly Arm Mobile Studio) has five components: Streamline, Frame Advisor, RenderDoc (for Arm), Mali Offline Compiler and Performance Advisor. Performance Advisor is now part of Streamline and can generate reports alongside the regular build in a CI workflow; Arm publishes a learning path on CI integration. — [Arm blog: What is Arm Performance Studio](https://developer.arm.com/community/arm-community-blogs/b/mobile-graphics-and-gaming-blog/posts/what-is-arm-performance-studio); [Arm blog: Automated performance advice](https://developer.arm.com/community/arm-community-blogs/b/mobile-graphics-and-gaming-blog/posts/automated-performance-advice-for-android-games); [Arm Learning Path](https://learn.arm.com/learning-paths/mobile-graphics-and-gaming/ams/pa/)
- Perfetto Trace Processor Python API (`pip install perfetto`):
  - Loads traces from file, stream or URI and runs PerfettoSQL queries.
  - Returns pandas or Polars DataFrames.
  - `trace_summary()` produces structured metric summaries; the older `metric()` is deprecated.
  - Exports to sqlite or Arrow.
  - Pins and auto-downloads a trace_processor binary for reproducibility.
  - Has no GUI dependency, so it suits headless and CI use. CI is not explicitly documented.
  — [Perfetto docs](https://perfetto.dev/docs/analysis/trace-processor-python)
- Google's Android game optimization guide covers system tracing (under 1% overhead; about 10–15 MB buffer per core gives about 20 s of trace). It also recommends:
  - Separate game and render threads; enable Multithreaded Rendering and GPU Skinning in Unity.
  - A UI update budget of 2–3 ms.
  - Pinning short-duration work to little cores.
  - The Thermal API (status NONE through SHUTDOWN) to back off frame rate or tessellation.
  - The Frame Pacing library, since a late frame at 30 fps costs an extra 33 ms.
  - IL2CPP over Mono for load speed.
  It warns that framerates often degrade after 45–50 minutes of play as devices heat up. It links separate docs for Android Performance Tuner, ADPF (Game Mode/State, Fixed Performance Mode), Android GPU Inspector and Play Asset Delivery. — [Android Developers: Optimize games](https://developer.android.com/games/optimize)

**Thermal and adaptive performance**
- ADPF `getThermalHeadroom()` estimates headroom before severe throttling so games can scale workload pre-emptively. The Thermal API is broadly available from Android 11 (API 30) and the Performance Hint API from Android 12 (API 31). — [Android Developers: MediaTek ADPF story](https://developer.android.com/stories/games/mediatek-adpf)
- Unity's Adaptive Performance Android provider (v5.x) wraps ADPF's thermal headroom and status APIs. — [Unity Adaptive Performance Android docs](https://docs.unity3d.com/Packages/com.unity.adaptiveperformance.google.android@5.1/manual/index.html)
- Kakao Games (Ares) used Android Adaptability with Unity Adaptive Performance and raised FPS stability from 75% to 96% (2023, older). Netmarble (Game of Thrones: Kingsroad) used ADPF for resolution scaling and dynamic frame rate. UNISOC fully supports core ADPF APIs from Android 14. — [Android Developers Blog (Kakao)](https://android-developers.googleblog.com/2023/09/kakao-games-increased-fps-stability-through-android-adapatability.html); [Netmarble story](https://developer.android.com/stories/games/netmarble-got-adpf); [UNISOC story](https://developer.android.com/stories/games/unisoc-adpf)

**Textures, asset delivery, size**
- Google recommends ASTC as the primary format and ETC2 as the fallback. ASTC is on over 75% of active Android devices and ETC2 on over 90% (needs GLES 3.0). Mipmaps add about 33% memory; skip them for fixed-distance textures. Use power-of-two sizes and smaller secondary maps (for example 512² roughness with a 1024² diffuse). Bilinear with 2x anisotropic filtering often beats trilinear with 1x, and texture filtering can be up to half of GPU energy. Texture Compression Format Targeting in Play Asset Delivery ships only the best format per device. — [Android Developers: Texture best practices](https://developer.android.com/games/optimize/textures)
- Play Asset Delivery replaces OBBs for games over 200 MB. Modes: install-time (counts toward app size), fast-follow and on-demand. It is free, with Play-hosted CDN. Install-time packs need 2x their size in free space, so keep them small. With texture targeting, download limits apply per texture format. A Unity integration guide exists. — [Android Developers: Play Asset Delivery](https://developer.android.com/guide/playcore/asset-delivery)
- iOS: at WWDC25, Apple called On-Demand Resources "a legacy technology" that "will be deprecated". The successor is Background Assets with Apple-hosted (or self-hosted) asset packs for games. An Apple DTS engineer advised against ODR for new products; there is no removal date. A third-party post says the managed Background Assets paths require an iOS 26 minimum deployment target (unverified). — [WWDC25 session 325](https://developer.apple.com/videos/play/wwdc2025/325); [Apple Developer Forums](https://developer.apple.com/forums/thread/807744); [Blake Crosley blog](https://blakecrosley.com/fr/blog/on-demand-resources-deprecated-background-assets)

**Store technical gates relevant to automated QA**
- Google Play 16 KB page size:
  - Google's notice (quoted on Unity forums) says that from Nov 1, 2025, new apps and updates targeting Android 15+ must support 16 KB pages. Users report a May 1, 2026 cutoff for updates.
  - Unity supports 16 KB from 6000.0.38f1 and 6000.1+, 2022.3.56f1 and 2021.3.48f1. Apps built with 4 KB alignment will not run on 16 KB devices.
  - Even on Unity 6000.3, Play may flag 4 KB-aligned `.so` files from outdated plugins (for example Firebase). Check with APK Analyzer.
  — [Unity Discussions: 16 KB support](https://discussions.unity.com/t/info-unity-engine-support-for-16-kb-memory-page-sizes-android-15/1589588); [Unity Discussions: Play requirement](https://discussions.unity.com/t/google-play-16kb-page-size-requirements/1681037); [Unity Discussions: 6000.3 rejection](https://discussions.unity.com/t/unity-6000-3-0f1-google-play-rejects-aab-due-to-16-kb-memory-page-size-agp-8-5-already-in-use/1707589); [Android Developers: Unity on Android](https://developer.android.com/games/engines/unity/unity-on-android)
- Android vitals bad-behavior thresholds: user-perceived crash rate 1.09% and ANR rate 0.47% overall; 8% per phone model. Exceeding them can reduce Play visibility or add store-listing warnings. — [Android Developers: Vitals for games](https://developer.android.com/games/optimize/vitals); [Android Developers Blog 2022](https://android-developers.googleblog.com/2022/10/raising-bar-on-technical-quality-on-google-play.html)

### Inferences
- Headless scriptability for an agent:
  - **Fully scriptable (cited):** Unity Performance Testing (JSON), Unity Test Framework in batch mode, Perfetto Trace Processor (Python/SQL), Arm Performance Advisor reports in CI, ADPF and Unity Adaptive Performance (runtime, in-game), APK Analyzer checks.
  - **Scriptable but unverified this session:** `adb shell perfetto` capture, `xcrun xctrace record/export` for Instruments, `adb shell dumpsys gfxinfo` and `dumpsys meminfo`, the Android GPU Inspector CLI (the docs URL returned 404), RenderDoc's Python API, and the Snapdragon Profiler command line.
  - **Mostly GUI-only:** the interactive Unity Profiler and Memory Profiler UI, Xcode Instruments GUI, and Snapdragon Profiler GUI. Agents should rely on their exportable data instead.
- Suggested CI perf budget gate for an agent pipeline. Thresholds marked * are pipeline suggestions; the rest are cited above.
  - Frame time p95 ≤ 33.3 ms on the low-end tier and ≤ 16.6 ms on mid/high.
  - UI ≤ 2–3 ms.
  - Draw calls and SetPass under a per-tier cap*.
  - Peak memory well under device RAM*, for example under about 1 GB on 3 GB devices.
  - Install-time size small, with the rest in PAD/Background Assets packs.
  - Cold start/load time cap*.
  - 30-minute soak with thermal-status logging to catch the 45–50 minute degradation.
  - 16 KB alignment check.
  - Crash and ANR rates projected under vitals thresholds.
- Performance must be measured on real low-end devices (device farm), because emulators and the Editor do not reflect GPU, thermal or memory behavior. The Memory Profiler and Unity Profiler need development builds, so CI should produce both a development build (for profiling) and a release build (for size and startup).

### Gaps
- No official 2026 docs were fetched for the Android GPU Inspector CLI, Xcode Instruments `xctrace`, Snapdragon Profiler or RenderDoc automation (search budget exhausted; the AGI CLI URL returned 404).
- Exact Google Play size limits (the base module limit, per-pack and total PAD caps) were not retrieved; the PAD page links to a Play support page.
- No primary data was found on the current Unity Performance Testing package version for Unity 6.x, or on its built-in baseline comparison features.
- Unity Addressables, shader-variant stripping and LOD/batching best practices were not specifically researched.

---

## 7. Device coverage: low-end Android targets, min specs, device farms and pricing

### Takeaway
There is no industry-standard 2026 Android minimum spec. Per-title floors cluster around 2–4 GB RAM, Android 7–8+, and Adreno 306–530-class GPUs at the low end (BGMI Lite targets 1.5 GB/Adreno 306; TFT moves from 2 GB to 4 GB; Fortnite needs 4 GB with Adreno 530/Mali-G72 MP12). Device-farm cost is modest for an automated pipeline: AWS Device Farm $0.17/device-minute or $250/slot/month unmetered; BrowserStack App Automate from about $199/month per parallel; Firebase Test Lab about $5 per physical-device-hour (third-party figure).

### Cited Findings
**Minimum spec data points**
- BGMI Lite (Krafton, pre-registration opened Aug 25, 2026) requires at least 1.5 GB RAM and an Adreno 306 or better GPU. (Single source, pre-release.) — [TalkEsport](https://www.talkesport.com/mobile-gaming/bgmi-lite-minimum-requirements-revealed-check-ram-gpu-and-other-details/)
- Teamfight Tactics Mobile currently requires 2 GB RAM and Android 7+. Its Unreal Engine migration (Patch 18.1, Aug 11, 2026) raises this to 4 GB RAM and Android 8+. — [Riot Support](https://support.riotgames.com/en-us/tft/gameplay/mobile-specs-android)
- Fortnite Android needs at least 4 GB RAM and an Adreno 530 or Mali-G72 MP12-class GPU; 8 GB+ is recommended. — [Epic Games Help](https://www.epicgames.com/help/c-34254770/c-38015632/a25800895?lang=en-US)
- Device-capability context: ASTC is on over 75% and ETC2 on over 90% of active Android devices. The Thermal API is broadly available from Android 11 and the Performance Hint API from Android 12. — [Android textures](https://developer.android.com/games/optimize/textures); [MediaTek ADPF story](https://developer.android.com/stories/games/mediatek-adpf)

**Device farms and pricing**
- AWS Device Farm (primary pricing page): $0.17 per device-minute (pay as you go). One-time free trial of 1,000 device-minutes, a limited-time offer (standard trial 250). Unmetered slots from $250 per device slot per month, bought per usage type and per Android/iOS family. Private devices from $200/month. — [AWS Device Farm pricing](https://aws.amazon.com/device-farm/pricing/)
- AWS Device Farm reportedly has a 150-minute hard limit per test run, with breakeven for unmetered at about 1,470 minutes per device per month. (Third-party.) — [DeviceLab](https://devicelab.dev/blog/aws-device-farm-pricing-2026)
- BrowserStack App Automate starts at about $199/month for 1 parallel; "Device Cloud Pro" is about $249/month per parallel; 10 parallels cost about $1,990/month. AWS metered is cheaper at low volume and a single parallel; BrowserStack is more competitive for many parallels across varied devices. (Third-party, citing BrowserStack's 2026 pricing page.) — [DeviceLab BrowserStack pricing](https://devicelab.dev/blog/browserstack-pricing-2026-hidden-costs); [DeviceLab AWS vs BrowserStack](https://www.devicelab.dev/blog/aws-device-farm-vs-browserstack); [TrustRadius](https://tr-web.dev.trustradius.com/compare-products/aws-device-farm-vs-browserstack)
- Firebase Test Lab is about $1 per virtual-device-hour and $5 per physical-device-hour on Blaze; the free tier is 10 virtual and 5 physical tests per day. It supports Game Loop tests. (Third-party.) — [Back4App](https://blog.back4app.com/firebase-test-lab/); [issoh.co.jp](https://www.issoh.co.jp/tech/details/17046/)
- Sauce Labs runs AltTester (Unity/Unreal) on real iOS and Android devices. — [Sauce Labs](https://docs.saucelabs.com/mobile-apps/automated-testing/alttester/unity/)
- nunu.ai runs its agents on real devices as a managed service. — [nunu.ai blog](https://nunu.ai/blog)

### Inferences
- A reasonable 2026 tiering for an automated pipeline. These tiers are my synthesis of the per-title data, not an industry standard:
  - **Low:** 3 GB RAM, Android 10–11, Adreno 610 / Mali-G52 class.
  - **Mid:** 4–6 GB, Snapdragon 7-series.
  - **High:** 8 GB+.
  - **iOS:** the oldest iPhone supported by the target iOS version.
  - Ultra-low 1.5–2 GB is only viable for "Lite"-style builds.
- Cost sketch: a nightly suite of 10 devices × 15 minutes = 150 device-minutes, about $25.50/night on AWS metered, or about $765/month. If running daily across many devices, 3–4 unmetered slots ($750–1,000/month) give more headroom. BrowserStack's per-parallel model favors fewer, longer-running parallels.
- Firebase Test Lab's Game Loop mode is a cheap way for a Unity build to run a scripted demo loop across many physical devices and collect crash and perf logs, without an external driver.

### Gaps
- No authoritative 2026 Android device-share data (RAM or GPU distribution) was found; Unity's or Google's device-distribution reports were not accessed.
- BrowserStack, Firebase Test Lab and Sauce Labs prices were not verified on primary pricing pages (only AWS was).
- Apple's recommended minimum device or iOS version for 2026 game launches was not researched.
- Search budget exhaustion prevented checking device-farm support for GPU and thermal profiling (for example whether AWS or BrowserStack expose `dumpsys`/Perfetto traces or GameBench-style metrics).
