# Knowledge map

58 skills, 183 reference files, 86791 lines (SKILL.md + references), 24 agents, 9 workflows, 23 scripts.
Total skill description characters: 23443.

## accessibility-localization

Accessibility and localization knowledge for games on any platform - Game Accessibility Guidelines, colour-blind, motor, cognitive, hearing and photosensitivity design, Godot and Unity recipes, i18n architecture, ICU plurals, CJK and RTL fonts, text expansion, LQA, machine translation with review, market languages. Use when asked "make it accessible", "colour-blind mode", "add languages", "localize the game" or "RTL support".

| Reference | Lines | Starts with |
|---|---|---|
| `references/accessibility.md` | 220 | Accessibility for mobile games |
| `references/localization.md` | 274 | Localization |
| `references/market-languages.md` | 206 | Market languages |

## ai-asset-pipeline

AI visual asset pipeline for games - 2D and 3D model landscape and licences, style lock and prompt templates, tournament selection, background removal, upscaling, palette and sprite-sheet post chains, 3D cleanup, manifest provenance, disclosure, and studio-gateway usage with budgets. Use when generating sprites, icons, key art or 3D props with AI, keeping a style consistent, choosing a provider, or preparing provenance and AI disclosure.

| Reference | Lines | Starts with |
|---|---|---|
| `references/gateway-usage.md` | 242 | Using studio-gateway |
| `references/model-landscape-2026.md` | 212 | Model Landscape 2026 (2D and 3D Generation) |
| `references/post-processing-and-provenance.md` | 228 | Post-Processing and Provenance |
| `references/style-lock-and-prompts.md` | 259 | Style Lock and Prompts |

## ai-audio-pipeline

How to generate, post-process and QC game audio with AI: music, SFX and voice service landscape (licences, revenue-threshold traps, excluded vendors), composition plans, loop and stem engineering, SFX sets, voice design, and audio_post.py normalize/trim/loop/convert/qc. Use when asked "which AI music tool", "generate game music", "make this loop", "generate SFX", "AI voice lines", "check loudness" or "is this licence safe".

| Reference | Lines | Starts with |
|---|---|---|
| `references/generation-pipelines.md` | 270 | Generation Pipelines |
| `references/model-landscape-2026.md` | 208 | Model Landscape 2026 (Volatile) |
| `references/post-and-qc.md` | 206 | Post-Processing and QC |

## analogy-engine

Analogy and transformation codex for game concepts: structure mapping and conceptual blending, a scored design-by-analogy procedure, 39 transformation operators (SCAMPER, transplant, constraint inversion, fusion, idle-ification...), 50 game lineages, 100+ cross-domain sources and a concept generator scored with concept.schema.json. Use when asked "X meets Y", "give me game ideas", "twist this genre", "why did X work" or "borrow this mechanic".

| Reference | Lines | Starts with |
|---|---|---|
| `references/analogy-method.md` | 486 | Analogy Method: From Source Game to Target Design |
| `references/concept-generation-playbook.md` | 487 | Concept Generation Playbook: From Player to Scored Concept Card |
| `references/cross-domain-sources.md` | 327 | Cross-Domain Sources: Analogy Material Outside Video Games |
| `references/transformation-operators.md` | 544 | Transformation Operators: A Grammar for Generating Designs from Existing Ones |
| `references/worked-analogies.md` | 576 | Worked Analogies: 50 Documented Game Lineages |

## art-direction

Art direction for games - style selection and style bibles, readability, shape language, value and colour (accessible palettes), asset specs, atlases, 9-slice, icons, store screenshots, key art, and a scored critique rubric with tournament selection. Use when asked to choose an art style, write a style bible, review screens, audit a palette, brief assets, or pick the best AI-generated candidate.

| Reference | Lines | Starts with |
|---|---|---|
| `references/art-critique-rubric.md` | 218 | Art Critique Rubric and the Comparative Tournament |
| `references/asset-specs-and-marketing-art.md` | 226 | Asset Specs and Marketing Art |
| `references/style-selection-and-bible.md` | 222 | Style Selection and the Style Bible |
| `references/visual-fundamentals.md` | 205 | Visual Fundamentals for Mobile Games |

## asset-production

Runs the visual asset pipeline for a game - style bible, asset list from the contract, style lock, generation through the studio-gateway tools, post-processing, engine import, manifest status flow and licence checks. Use when the user says "make the art", "generate sprites", "asset batch", "lock the style", "build the asset list" or "import these assets".

## audio-direction

Audio direction for games - audio bible and sonic identity, adaptive music (re-sequencing, layering, stingers), SFX layering and reward escalation, bus mixing and ducking, loudness targets, formats, iOS/Android audio session rules, voice direction and AI-voice consent. Use when asked to "write the audio bible", "make the music adaptive", "design UI sounds", "set up the mix", "fix loudness", "direct voice lines" or "plan the audio".

| Reference | Lines | Starts with |
|---|---|---|
| `references/audio-bible-and-identity.md` | 259 | Audio Bible and Sonic Identity |
| `references/mixing-implementation-voice.md` | 207 | Mixing, Implementation and Voice |
| `references/music-and-sfx-systems.md` | 358 | Music and SFX Systems |

## audio-production

Runs the music, SFX and voice pipeline for a game - audio bible, cue list, generation via studio-gateway audio tools, audio_post.py normalize/loop/convert/qc, engine implementation with buses and adaptive music, QC and licence revenue thresholds. Use when the user says "make the music", "add sound effects", "generate voice lines", "loop this track", "check loudness" or "audio pass".

## balance

Tunes game economy and difficulty with simulators instead of guesses - authoring economy models, running economy_sim, difficulty curves, match-3 and puzzle solvers, gacha and progression calculators, then writing results back into the design contract. Use when the user says "balance the economy", "is this too grindy", "tune difficulty", "check drop rates", "simulate the economy", or "levels feel too hard".

## build-feature

Implements one feature from .gamestudio/features.json through the five gates (static, unit, playthrough, visual, perf) with evidence on disk, sim-core first. Use when the user says "build the next feature", "implement F012", "work the feature list", "make this feature pass", or when a feature needs gates run and recorded.

## concept-lab

Concept ideation lab - five ideation methods (analogy, constraint inversion, mechanic transplant, market gap, player-motivation-first), concept cards written to .gamestudio/concepts/ against concept.schema.json, and a weighted scoring rubric with 1/5/10 anchors, gates and evidence caps. Use when the user says "give me game ideas", "brainstorm concepts", "score these concepts", "X meets Y", or "which idea should we make".

| Reference | Lines | Starts with |
|---|---|---|
| `references/ideation-methods.md` | 128 | Ideation Methods |
| `references/scoring-rubric.md` | 140 | Concept Scoring Rubric |

## console-pathway

Guidance for getting a game onto Nintendo, PlayStation and Xbox consoles using public information only - self-publish, publisher or porting partner; when to start; budget and time ranges; what design and code must already do (controller UI, safe area, suspend, user switching, saves); programmes, ratings and a porting plan. Use for "should we port to Switch", "how do I get a dev kit", "console age ratings".

| Reference | Lines | Starts with |
|---|---|---|
| `references/certification-and-ratings.md` | 125 | Certification Themes and Age Ratings |
| `references/porting-plan.md` | 160 | Porting Plan Template |
| `references/programmes-and-access.md` | 134 | Programmes and Access: Nintendo, Xbox, PlayStation |

## deconstruct

Deconstructs an existing game into the shared ontology - core loop, mechanics, economy, progression, monetization, live-ops, retention hooks, psychology, weaknesses and lessons - from public sources, writing deconstruction.schema.json and a readable markdown analysis. Use when the user says "deconstruct <game>", "break down how X works", "analyse this game's economy" or "what can we borrow from X".

## design-philosophies

Codex of game-making ideologies. Doctrines of influential studios (Nintendo, Supercell, Valve, King, HoYoverse, indie craft houses), rules derived from notable designers, schools of thought and debates, and this plugin's 10-point house doctrine made operational. Use when asked "what would Nintendo do", "which philosophy fits this game", "settle this design debate", "is this ethical F2P", "should we kill it", or for a philosophy lens review.

| Reference | Lines | Starts with |
|---|---|---|
| `references/designer-philosophies.md` | 382 | Designer Philosophies |
| `references/schools-of-thought.md` | 505 | Schools of Thought |
| `references/studio-doctrine-operationalized.md` | 373 | The House Doctrine, Operationalized |
| `references/studio-doctrines.md` | 478 | Studio Doctrines |

## design-review

Multi-lens review of the design contract (design, economy, UX, monetization ethics, technical feasibility, market, scope, accessibility, compliance) with a four-level severity scale, a pass/fail verdict and a dated report. Use when the user says "review the design", "is this contract any good", "red-team my GDD", "check scope", or before building the vertical slice.

## design-theory

Game design theory codex: MDA/DDE, kinds of fun, flow, SDT and motivation models, core/meta/social loops, pacing, meaningful decisions, dominance and game theory, depth vs complexity, skill vs luck, failure design, prototyping, pillars, kill criteria and a 130-question design diagnostic. Use when asked "is this fun?", "design the core loop", "why is this boring", "review this design", "find dominant strategies" or "what do we prototype first".

| Reference | Lines | Starts with |
|---|---|---|
| `references/core-loops-and-structure.md` | 459 | Core Loops and Game Structure |
| `references/decisions-and-depth.md` | 448 | Decisions, Depth and Strategic Structure |
| `references/design-diagnostic-checklist.md` | 323 | Design Diagnostic Checklist |
| `references/foundational-frameworks.md` | 605 | Foundational Design Frameworks — A Working Practitioner's Digest |
| `references/fun-and-motivation-design.md` | 367 | Fun and Motivation Design |
| `references/prototyping-and-iteration.md` | 379 | Prototyping and Iteration |

## economy-design

Game economy codex: currency architecture (soft, hard, premium, energy, event, material), sources and sinks, inflation and hoarding, sim-based balancing with economy_sim.py, price ladders, offers, passes, gacha maths and pity, loot-box law, ad economics, and patterns from landmark games. Use when asked to "design the economy", "add a currency", "balance sinks", "price the shop", "design a banner" or "why are players hoarding".

| Reference | Lines | Starts with |
|---|---|---|
| `references/ad-economy.md` | 279 | Ad Economy |
| `references/currency-architecture.md` | 436 | Currency Architecture |
| `references/economy-case-patterns.md` | 350 | Economy Case Patterns |
| `references/gacha-and-loot.md` | 362 | Gacha and Loot |
| `references/pricing-and-offers.md` | 397 | Pricing and Offers |
| `references/sources-sinks-balancing.md` | 378 | Sources, Sinks and Balancing |

## engine-alternatives

Engine selection and quick-starts beyond Godot and Unity - Unreal, Defold, Cocos Creator, web stacks (Phaser, PixiJS, three.js, Babylon, PlayCanvas, Capacitor), Bevy, GameMaker, Construct, GDevelop, Solar2D, Flame, native. Use when asked which engine to use, whether to pick Unreal or Defold, how to ship a web game as an app, how to make a playable ad, or to compare engines.

| Reference | Lines | Starts with |
|---|---|---|
| `references/engine-selection-matrix.md` | 200 | Engine Selection Matrix |
| `references/unreal-defold-cocos.md` | 202 | Unreal, Defold and Cocos Creator |
| `references/web-and-others.md` | 204 | Web Stacks, Hybrid Wrappers and Other Engines |

## engine-godot

Senior Godot 4 practice - typed GDScript, project layout, autoloads, signals, Resources, renderers and export (Android gradle, iOS; desktop and web in pc-web-release), headless CLI gates, testing, perf and plugin options. Use when asked to build, fix, export, test or optimize a Godot project, write GDScript, set up Android/iOS builds, or choose Godot plugins.

| Reference | Lines | Starts with |
|---|---|---|
| `references/gdscript-and-project.md` | 261 | GDScript and Project Structure |
| `references/mobile-export-and-plugins.md` | 220 | Godot Mobile Export, Platform Settings and Plugins |
| `references/testing-perf-cheatsheet.md` | 330 | Godot Testing, Verification, Performance and API Recipes |

## engine-unity

Senior Unity 6 practice - C# project layout with asmdefs and a pure core assembly, URP and Player settings for phones, Addressables, Input System, editor automation (Unity CLI, batchmode, SceneBuilder/BuildScript), tests, CI and SDKs. Use when asked to build, fix, test, automate or ship a Unity game, write C# for Unity, configure URP, or set up IAP, ads or CI.

| Reference | Lines | Starts with |
|---|---|---|
| `references/csharp-project-and-urp.md` | 326 | Unity C# Project Structure, URP and Mobile Settings |
| `references/editor-automation-and-services.md` | 337 | Unity Editor Automation, CI and Services |
| `references/testing-and-cheatsheet.md` | 327 | Unity Testing, Verification and API Cheatsheet |

## extend

Scaffolds and checks an Arcosian add-on - a genre pack, an engine adapter or a tool connector - from the bundled template, then holds it to the house rules (skill format, pinned MCP servers, secrets only in sensitive options, disclosure README, self-tested scripts) before it is shared. Use when asked to "make an add-on", "add support for <engine or tool>", "write a genre pack", "publish my own Arcosian plugin" or "check my add-on".

## game-architecture

Game architecture codex: the studio sim-core + presentation split, deterministic cores, fixed timestep, state machines, command/undo/replay, event bus, pooling, ECS vs composition, DI, data-driven design, AI techniques, versioned saves, remote config, testing. Use when asked to structure a game project, choose a pattern, design saves or migrations, plan tests, or review code architecture.

| Reference | Lines | Starts with |
|---|---|---|
| `references/data-persistence-and-quality.md` | 271 | Data, persistence and code quality |
| `references/patterns-and-ai.md` | 337 | Programming patterns and game AI |
| `references/sim-core-presentation.md` | 322 | Sim-core + presentation: the studio core abstraction |

## game-case-studies

Deconstructions of about 113 landmark games (mobile genres, premium indie, PC and console, web and cross-play) in one 16-lens format, plus the method to deconstruct any game into deconstruction.schema.json and use precedents for decisions and analogies. Use when asked "how does X do it", "deconstruct X", "which games did this", "comparables" or "X meets Y", or before choosing a loop, economy or offer.

| Reference | Lines | Starts with |
|---|---|---|
| `references/casual-social-sim.md` | 1514 | Casual, social and simulation case studies |
| `references/cross-game-patterns.md` | 689 | Cross-game patterns |
| `references/hyper-hybrid-casual.md` | 1198 | Hyper-casual and hybrid-casual case studies |
| `references/midcore-strategy.md` | 1740 | Midcore, strategy and competitive case studies |
| `references/pc-console.md` | 794 | PC and console case studies |
| `references/premium-indie.md` | 1305 | Premium and indie case studies |
| `references/puzzle-casual.md` | 1177 | Puzzle and casual case studies |
| `references/rpg-gacha-cards.md` | 1568 | RPG, gacha, idle and card-game case studies |
| `references/web-and-crossplay.md` | 463 | Web-first and cross-platform case studies |

## game-feel

Game feel and juice codex: Swink-style response model, input latency budgets, coyote time and buffering, trauma-based screen shake, hit-stop, squash and stretch, easing, particles, number pop-ups, audio and haptic pairing, mobile battery cost, feel review rubric. Use when a game "feels floaty", "add juice", "make it satisfying", "screen shake", "hit-stop", "haptics", "tween" or "input lag".

| Reference | Lines | Starts with |
|---|---|---|
| `references/feel-review-rubric.md` | 241 | Feel review rubric |
| `references/input-animation-haptics.md` | 331 | Input, animation and haptics |
| `references/juice-catalog.md` | 345 | Juice catalog |

## game-glossary

Defines about 500 game development, design, engineering, art, audio, live-ops, monetization, store and production terms, with a top-50 summary and a file index per domain. Use when someone asks what a game term means, uses jargon such as FTUE, ARPDAU, rollback netcode, LUFS or gacha, or needs shared vocabulary before a design doc, review or KPI definition.

| Reference | Lines | Starts with |
|---|---|---|
| `references/art-audio-platform-terms.md` | 270 | Art, Audio, Platform and Store Terms |
| `references/business-liveops-terms.md` | 272 | Business, Monetization, Live Ops and Production Terms |
| `references/design-and-tech-terms.md` | 269 | Design and Technology Terms |

## game-ontology

The shared vocabulary and schemas of the studio: layered model (player, motivation, aesthetics, dynamics, mechanics, verbs and rules, entities and resources), loops, flows, content, sessions, live-ops, and how each maps to the JSON schemas. Use when asked to "describe this game in the ontology", "write a mechanic card", "model this loop", "which schema holds X", "validate a contract" or "what goes in the design contract".

| Reference | Lines | Starts with |
|---|---|---|
| `references/loops-flows-and-mda.md` | 342 | Loops, flows and MDA in practice |
| `references/ontology-overview.md` | 223 | Ontology overview: one vocabulary for every game |
| `references/schema-reference.md` | 301 | Schema reference: every ontology document, field by field |
| `references/worked-example.md` | 206 | Worked example: following one game through every document |

## gameplay-programming

Gameplay programming codex: vector math, easing, springs, kinematic controllers, jump arcs, cameras, grids and hexes, collision, pathfinding (BFS, A*, JPS, flow fields), PRNG, shuffle bags, pity, plus recipes for inventory, crafting, quests, timers, waves, match-3, merge, idle big numbers, block puzzles, runners. Use when implementing movement, feel, grids, search, randomness, or a game system.

| Reference | Lines | Starts with |
|---|---|---|
| `references/math-and-movement.md` | 268 | Math and movement for gameplay code |
| `references/pathfinding-and-rng.md` | 323 | Pathfinding and randomness |
| `references/systems-cookbook.md` | 350 | Gameplay systems cookbook |

## genre-playbooks

Genre playbooks for games on any platform: loops, session profile, signature mechanics, monetization, KPIs, production scope, agent-buildability and P0 features per subgenre - mobile genres plus shooters, action-adventure, platformers, survival, simulation, MMO and live service, racing, sports, fighting, horror, narrative, PC strategy and deckbuilders. Use when choosing or fusing a genre or scoping a slice.

| Reference | Lines | Starts with |
|---|---|---|
| `references/action-adventure.md` | 633 | Action-Adventure Playbooks |
| `references/action-arcade-roguelite.md` | 662 | Action, Arcade and Roguelite Playbooks |
| `references/competitive-pvp.md` | 792 | Competitive PvP Playbooks |
| `references/horror-narrative.md` | 741 | Horror and Narrative Playbooks |
| `references/hyper-hybrid-casual.md` | 785 | Hypercasual and Hybrid-Casual Playbooks |
| `references/idle-tycoon-sim.md` | 574 | Idle, Tycoon and Simulation Playbooks |
| `references/mmo-live-service.md` | 683 | MMO and Live-Service Playbooks |
| `references/narrative-rhythm-edu-kids.md` | 760 | Narrative, Rhythm, Educational, Kids, Fitness and Cozy Playbooks |
| `references/pc-strategy-cards.md` | 774 | PC Strategy and Card Playbooks |
| `references/platformer-metroidvania.md` | 617 | Platformer and Metroidvania Playbooks |
| `references/puzzle.md` | 966 | Puzzle Playbooks |
| `references/racing-sports-fighting.md` | 744 | Racing, Sports and Fighting Playbooks |
| `references/rpg-gacha.md` | 678 | RPG and Gacha Playbooks |
| `references/shooters.md` | 794 | Shooter Playbooks (PC and Console Depth) |
| `references/simulation-management.md` | 797 | Simulation and Management Playbooks |
| `references/social-casino-party.md` | 681 | Social, Casino and Party Playbooks |
| `references/strategy.md` | 727 | Strategy Playbooks |
| `references/survival-sandbox.md` | 741 | Survival and Sandbox Playbooks |

## legal-ethics

Legal and ethical risk knowledge for games - clone and trade dress risk, trademarks, mechanic patents, AI content ownership and disclosure, voice and likeness, privacy (GDPR, COPPA, CCPA, age assurance), children, loot-box rules by region, open-source, font, music and asset licences, publishing contracts. Use when asked "can I copy this mechanic", "is this a clone", "disclose AI", "COPPA", "loot box legal" or "licence check".

| Reference | Lines | Starts with |
|---|---|---|
| `references/ip-and-ai-content.md` | 205 | IP and AI content |
| `references/licences-and-contracts.md` | 215 | Licences and contracts |
| `references/privacy-children-gambling.md` | 229 | Privacy, children and gambling-adjacent rules |

## level-design

Level design codex: teach-test-twist-reward, kishōtenketsu, signposting, affordances, gating, pacing, flow, mobile readability, level metrics; puzzle aha and difficulty theory; match-3/blast production at scale; runner, survivor, platformer, arena and boss design; level-spec, solver gates, PCG and set audits. Use when asked to "design levels", "make 200 match-3 levels", "why does level 47 churn", "tune move limits" or "verify these levels".

| Reference | Lines | Starts with |
|---|---|---|
| `references/action-level-design.md` | 515 | Action Level Design |
| `references/casual-level-production.md` | 489 | Casual Level Production (Match-3, Blast and Friends) |
| `references/level-pipeline.md` | 412 | Level Pipeline: Specs, Editors, Solvers and Metrics |
| `references/principles.md` | 387 | Level Design Principles |
| `references/puzzle-level-design.md` | 464 | Puzzle Level Design |

## liveops

Live-operations craft for live games - event taxonomy and design, content calendar, seasons, segmentation, CRM and push, win-back, soft launch gates, remote config, incident handling, economy hotfixes and compensation. Use when asked to plan events, build a live-ops calendar, segment players, run soft launch, ship a hotfix via remote config, or handle a live incident.

| Reference | Lines | Starts with |
|---|---|---|
| `references/calendar-segmentation-crm.md` | 208 | Calendar, Segmentation and CRM |
| `references/liveops-fundamentals-and-events.md` | 221 | Live-Ops Fundamentals and Events |
| `references/soft-launch-and-ops.md` | 221 | Soft Launch and Ops |

## market-intel

Mobile games market intelligence codex: market size and trend reading, genre and regional trends, AI game-creation competitors, and research methods (Sensor Tower, AppMagic, charts, review mining, ad libraries). Use when sizing a market, choosing a genre or region, running a competitor scan, reading store charts, positioning against AI game tools, or checking how fresh a market claim is.

| Reference | Lines | Starts with |
|---|---|---|
| `references/ai-gamedev-landscape-and-methods.md` | 258 | AI Game-Creation Landscape and Research Methods |
| `references/genre-and-regional-trends.md` | 210 | Genre and Regional Trends |
| `references/market-overview-2026.md` | 207 | Market Overview 2026 |

## market-scan

Budget-aware competitive and market research for a genre or concept - sources, procedure, competitor matrix, positioning statement and a dated research file. Use when the user says "market research", "who are the competitors", "is this genre saturated", "scan the market for", or before a concept tournament or contract.

## marketing-ua

Mobile game marketing and user acquisition - CPI, ROAS and payback math, channels and bidding, attribution (SKAN, AdAttributionKit, GAID, MMPs), creative testing and playables, community, influencers, PR, pre-registration, launch timing, virality, and pre-production marketability tests. Use when asked about CPI targets, UA budgets, ad creatives, fake-door tests, launch plans or K-factor.

| Reference | Lines | Starts with |
|---|---|---|
| `references/community-launch-virality.md` | 210 | Community, Launch and Virality |
| `references/marketability-testing.md` | 202 | Marketability Testing |
| `references/ua-and-creatives.md` | 219 | UA and Creatives |

## mechanics-codex

Encyclopedia of 250+ game mechanics in twelve families (verbs/physics, combat, puzzle, economy, progression, social, randomness, time/session, collection/building, narrative/exploration, mobile controls, monetization) with rules, tuning ranges, dynamics, failure modes and implementation notes. Use when choosing, combining, specifying or tuning mechanics, writing mechanic cards, or asking which mechanic would make a game feel a certain way.

| Reference | Lines | Starts with |
|---|---|---|
| `references/01-verbs-movement-physics.md` | 749 | 01 — Input Verbs, Movement and Physics Mechanics |
| `references/02-combat-action.md` | 794 | 02 — Combat and Action Mechanics |
| `references/03-puzzle-mechanics.md` | 771 | 03 — Puzzle Mechanics |
| `references/04-economy-resource-mechanics.md` | 719 | 04 — Economy and Resource Mechanics |
| `references/05-progression-meta-mechanics.md` | 689 | Progression and Meta Mechanics |
| `references/06-social-competitive-mechanics.md` | 711 | Social and Competitive Mechanics |
| `references/07-randomness-chance-mechanics.md` | 735 | Randomness and Chance Mechanics |
| `references/08-time-energy-session-mechanics.md` | 719 | Time, Energy and Session Mechanics |
| `references/09-collection-crafting-building.md` | 795 | 09 — Collection, Crafting and Building Mechanics |
| `references/10-narrative-exploration-mechanics.md` | 769 | 10 — Narrative and Exploration Mechanics |
| `references/11-mobile-input-control-schemes.md` | 799 | 11 — Mobile Input and Control Schemes |
| `references/12-monetization-linked-mechanics.md` | 774 | 12 — Monetization-Linked Mechanics |

## mobile-performance

Mobile game performance codex - per-tier frame, memory, size and startup budgets, thermals, profiling (Unity, Godot, Instruments, Android Studio, Perfetto, AGI), optimisation playbooks, ADPF and soak tests, perf-report schema and perf_budget.py; PC, Steam Deck, web and console tiers are in platform-targets. Use when asked "why is it slow", "set perf budgets", "profile this", "it gets hot", "reduce APK size" or "perf gate".

| Reference | Lines | Starts with |
|---|---|---|
| `references/budgets-and-tiers.md` | 209 | Budgets and Device Tiers |
| `references/optimization-and-thermal.md` | 201 | Optimization and Thermal Playbooks |
| `references/perf-testing-automation.md` | 245 | Performance Testing and Automation |
| `references/profiling-toolkit.md` | 207 | Profiling Toolkit |

## mobile-ux

Mobile game UX codex: thumb zones, touch targets, gestures, safe areas, interruptions, HUD, hubs, shops, inventories, reward screens, pop-up hierarchy, tutorials, first-session flow, permission timing, typography, contrast and Godot/Unity UI scaling. PC, TV and web UI live in platform-targets. Use when asked "design this screen", "UX review", "onboarding flow", "safe area" or "audit this layout".

| Reference | Lines | Starts with |
|---|---|---|
| `references/game-ui-patterns-and-onboarding.md` | 348 | Game UI Patterns and Onboarding |
| `references/layout-typography-and-review.md` | 345 | Layout, Typography and UX Review |
| `references/mobile-interaction.md` | 526 | Mobile Interaction: Hands, Targets, Gestures, Safe Areas, Orientation and Interruptions |

## monetization

Senior monetization knowledge for games - business model choice, IAP and subscription implementation (StoreKit 2, Play Billing, RevenueCat), ad mediation and placements, offer design, battle passes, loot-box law, odds disclosure, minors, and payments rules. Use when asked to pick a business model, design IAP, add ads, price offers, build a battle pass, or check monetization ethics.

| Reference | Lines | Starts with |
|---|---|---|
| `references/business-models-and-implementation.md` | 218 | Business Models and Implementation |
| `references/offers-regulation-ethics.md` | 230 | Offers, Regulation and Ethics |
| `references/payments-landscape-2026.md` | 206 | Payments Landscape 2026 |

## multiplayer-backend

Multiplayer and backend codex: async vs real-time, authority, lockstep, rollback, snapshot interpolation, prediction, tick rates; backend selection (Firebase, Nakama, PlayFab, UGS, Photon, Colyseus, Supabase), remote config, CDN, push; leaderboards, Elo/Glicko-2, guilds, chat moderation, server authority, receipt validation, bot detection. Use when planning online features, picking a backend, or hardening against cheating.

| Reference | Lines | Starts with |
|---|---|---|
| `references/backend-and-liveops-infra.md` | 231 | Backend and live-ops infrastructure |
| `references/networking-models.md` | 215 | Networking models for mobile games |
| `references/social-and-security.md` | 260 | Social systems and security |

## narrative-design

Narrative design codex for games, weighted to mobile: story structures, ludonarrative fit, worldbuilding, characters, Ink/Yarn/Dialogic, branching cost maths, barks, UI-length writing, localisation and meta-stories. Use when asked "write the story", "branching cost", "bark pool", "tone bible" or "lint my Yarn/Ink".

| Reference | Lines | Starts with |
|---|---|---|
| `references/dialogue-and-branching.md` | 672 | Dialogue Systems, Branching and Writing for the Screen |
| `references/mobile-narrative.md` | 421 | Mobile Narrative: Meta-Stories, Episodes, Retention and Marketing |
| `references/story-structures.md` | 471 | Story Structures for Games |
| `references/worldbuilding-characters.md` | 496 | Worldbuilding, Characters, Tone and IP |

## new-game

Takes a one-line game brief to a validated, reviewed project - intake, market scan, concept tournament, human concept pick, design contract, design review, vertical-slice feature plan, engine choice, project template, bibles, placeholder assets, and the first build-feature run. Use when the user says "new game", "I have a game idea", "start a project", "make me a puzzle game", or "turn this brief into a plan".

## operate

Post-launch operations for a live game - KPI review with the data analyst, live-ops calendar, A/B tests with ab_test.py, remote config changes, crash triage, store review replies and a weekly cadence. Use when the user says "how is the game doing", "weekly review", "plan an event", "run an A/B test", "triage crashes", "reply to reviews" or "live-ops calendar".

## optimize

Runs a performance pass against the contract's budgets - frame time, memory, download size, cold start, thermals - with per-engine profiling, device tiers, perf_budget.py checks, a prioritized fix checklist and a perf report that sets the perf gate. Use when the user says "optimize performance", "it stutters", "too much memory", "build is too big", "check the perf budget", or "why is it hot".

## pc-web-release

Release knowledge for PC and web games - Steam (Steamworks, store page, wishlists, Next Fest, Playtest, SteamPipe, Deck review), itch.io and butler, web portals, self-hosted web builds, Epic, GOG, Microsoft Store, Mac App Store, and code signing for macOS, Windows and Linux. Use for "put my game on Steam", "butler push", "web export headers", "notarise my Mac build", "which store first".

| Reference | Lines | Starts with |
|---|---|---|
| `references/itch-and-web-portals.md` | 154 | itch.io, Web Portals and Web Hosting |
| `references/other-pc-stores.md` | 124 | Other PC Stores: Epic, GOG, Microsoft Store and Game Pass, Mac App Store |
| `references/signing-and-packaging.md` | 206 | Signing and Packaging: macOS, Windows, Linux |
| `references/steam.md` | 240 | Steam Release Guide |

## platform-targets

Platform-target codex for one game on many platforms: choosing platforms, input and controls (touch, mouse/keyboard, gamepad), platform UX, performance tiers, saves and platform rules for mobile, PC, Steam Deck, web and consoles (public info). Use when asked "which platforms", "add PC/web/console", "gamepad support", "Steam Deck", "port this game" or "set min spec".

| Reference | Lines | Starts with |
|---|---|---|
| `references/input-and-controls.md` | 449 | Input and controls |
| `references/performance-tiers.md` | 249 | Performance tiers |
| `references/platform-matrix.md` | 278 | Platform matrix |
| `references/platform-ux.md` | 319 | Platform UX |
| `references/saves-and-platform-rules.md` | 298 | Saves and platform rules |

## player-analytics

Player-analytics codex: KPI definitions (retention types, ARPDAU, LTV, ROAS, payback), event taxonomies for Firebase/GameAnalytics, funnels, level churn and difficulty spikes, cohorts, segmentation, RFM, churn models, A/B testing (power, SRM, peeking, CUPED), retention/LTV modelling, economy telemetry. Use when asked to "define KPIs", "design analytics events", "why did D7 drop", "size an A/B test", "project LTV" or "read soft-launch data".

| Reference | Lines | Starts with |
|---|---|---|
| `references/event-taxonomy-design.md` | 405 | Event Taxonomy Design |
| `references/experimentation.md` | 439 | Experimentation for Games |
| `references/funnels-cohorts-segmentation.md` | 429 | Funnels, Cohorts and Segmentation |
| `references/kpi-dictionary.md` | 389 | KPI Dictionary for Mobile Games |
| `references/ltv-retention-modeling.md` | 325 | Retention Curves, LTV and ROAS Modelling |
| `references/telemetry-for-design.md` | 395 | Telemetry for Design Decisions |

## player-psychology

Player psychology codex: motivation models (SDT/PENS, Quantic Foundry, Bartle, Lazzaro, Fogg, Hook, flow), behavioural economics with ethical boundaries, emotion and cognition for game UI, dark patterns and studio red lines, minors and wellbeing, and player research methods. Use when asked "why do players quit", "what motivates our audience", "is this offer manipulative", "plan a playtest", "write personas" or "check our ethics".

| Reference | Lines | Starts with |
|---|---|---|
| `references/behavioral-economics-in-games.md` | 564 | Behavioral Economics in Games |
| `references/emotion-and-cognition.md` | 418 | Emotion and Cognition |
| `references/ethics-and-dark-patterns.md` | 388 | Ethics and Dark Patterns |
| `references/motivation-models.md` | 449 | Motivation Models |
| `references/player-research-methods.md` | 529 | Player Research Methods |

## playtest

Runs and interprets playtests for a game build - deterministic scripted playthroughs, bot runs, persona playtests through the player-simulator agent, visual QA, and human TestFlight/internal rounds - and writes playtest reports. Use when the user says "playtest this", "does the FTUE work", "find softlocks", "run the bots", "simulate a casual player", or "QA this build".

| Reference | Lines | Starts with |
|---|---|---|
| `references/personas.md` | 109 | Playtest Personas |

## postmortem

Runs a structured, blameless postmortem for a game project, milestone, soft launch or release and captures lessons into the project record. Writes .gamestudio/reports/postmortem-<date>.md from the postmortem template using evidence from progress, features, playtests, budget and analytics. Use when the user says "postmortem", "retro", "what went wrong", "lessons learned" or "wrap up the project".

## procedural-generation

Procedural generation codex: noise, fBm, domain warping, CA caves, BSP and room-and-corridor, wave function collapse, Poisson disk, Voronoi, L-systems, graph grammars, constraint and search PCG, runner chunks, roguelite runs, loot affixes, solvable puzzles, seeded PRNGs, daily seeds, replays, expressive range. Use when asked to "generate levels", "make it procedural", "add endless mode", "daily challenge" or "why are generated levels broken".

| Reference | Lines | Starts with |
|---|---|---|
| `references/algorithms.md` | 736 | PCG Algorithms: Catalogue with Pseudo-code |
| `references/determinism-and-seeds.md` | 377 | Determinism and Seeds |
| `references/generate-and-test.md` | 347 | Generate and Test: Evaluation, Gates and Expressive Range |
| `references/pcg-for-mobile-games.md` | 441 | PCG for Mobile Games: Patterns that Ship |

## production

Game production codex: phase gates and kill criteria, scoping and MoSCoW, estimation for humans and AI agents, milestones, risk registers, roles and RACI, kanban for games, crunch avoidance, lean GDD, one-pagers, design contract, pitch decks, postmortems. Use when planning a game, cutting scope, estimating, setting milestones, writing a GDD or pitch, running a risk review or postmortem.

| Reference | Lines | Starts with |
|---|---|---|
| `references/docs-and-postmortems.md` | 221 | Documents and Postmortems |
| `references/lifecycle-and-planning.md` | 238 | Lifecycle and Planning |
| `references/risk-team-process.md` | 227 | Risk, Team and Process |

## progression-difficulty

Progression and difficulty codex: XP and cost curves (linear, poly, exp, logistic, piecewise), time-to-level, soft caps, catch-up; sawtooth difficulty, win-rate targets, hard-level cadence, failure costs, boosters; DDA methods and ethics; unlock pacing and FTUE; power curves, damage formulas, cost curves, PvP balance. Use when asked to "design the XP curve", "tune difficulty", "add DDA", "pace unlocks", "fix the tutorial" or "balance units".

| Reference | Lines | Starts with |
|---|---|---|
| `references/difficulty-design.md` | 404 | Difficulty Design |
| `references/dynamic-difficulty.md` | 347 | Dynamic Difficulty |
| `references/power-and-balance.md` | 425 | Power and Balance |
| `references/progression-curves.md` | 565 | Progression Curves |
| `references/unlocks-pacing-ftue.md` | 417 | Unlocks, Pacing and FTUE |

## qa-testing

Game QA codex - game test pyramid, risk-based testing, deterministic scripted playthroughs, bots (random, greedy, MCTS, RL), difficulty and softlock detection with match3_sim.py and puzzle_solver.py, structural UI and VLM visual QA, device matrices, crash and ANR handling, human playtests, bug and severity templates. Use when asked "test this build", "write a playthrough", "find softlocks", "visual QA", "device matrix" or "triage crashes".

| Reference | Lines | Starts with |
|---|---|---|
| `references/bots-and-visual-qa.md` | 205 | Bots, Difficulty and Visual QA |
| `references/devices-crashes-human-playtests.md` | 214 | Devices, Crashes and Human Playtests |
| `references/test-strategy-and-playthroughs.md` | 245 | Test Strategy and Scripted Playthroughs |

## ship

Release pipeline - compliance pre-flight, version bump, signed builds via CI templates and fastlane, store metadata and screenshots, uploads to TestFlight, Play internal testing or private Steam and itch.io channels, release report and the human-only steps. Never submits for review or goes live without explicit human approval. Use when the user says "ship it", "build a release", "upload to TestFlight", "store listing" or "release candidate".

## store-release

Mobile store release knowledge - headless builds, signing, fastlane, TestFlight and Play tracks, CI, versioning, App Store and Google Play requirements (SDK floors, privacy manifests, PBL, 16 KB pages, Data safety), ASO and the pre-flight checklist; PC and web stores are in pc-web-release, consoles in console-pathway. Use when asked "how do I ship to the App Store", "Play rejected my build", "set up fastlane" or "release checklist".

| Reference | Lines | Starts with |
|---|---|---|
| `references/aso-and-submission.md` | 202 | ASO and submission |
| `references/release-pipeline.md` | 217 | Release pipeline |
| `references/store-requirements-2026.md` | 207 | Store requirements (2026) |

## studio

Front door of the Arcosian suite. Boots the principal game developer persona and doctrine, detects project state (gs.py status, engine files, studio-gateway), maps the pipeline Concept to Live to the skill, workflow and agent for each stage, and routes to the next step. Use when the user says "/studio", "I want to make a game", "where are we", "what next", "continue the project" or "onboard this repo".

## technical-art

Technical art for games - toon, rim, matcap, dissolve, flipbook and wind shaders in Godot and Unity, VFX language and particle budgets, ASTC/ETC2/KTX2 textures, polycount and LOD budgets, gltfpack, skinning limits, tile-based GPU rendering, overdraw and post-processing cost. Use when writing shaders, building VFX, compressing textures, optimizing 3D assets, or fixing GPU-bound or hot-phone frames.

| Reference | Lines | Starts with |
|---|---|---|
| `references/mobile-shaders-and-vfx.md` | 354 | Mobile Shaders and VFX |
| `references/rendering-on-mobile.md` | 245 | Rendering on Mobile |
| `references/texture-and-3d-pipeline.md` | 273 | Texture and 3D Pipeline for Mobile |

## what-if

Predicts what a proposed change will do before anyone ships it - runs the current and the changed version through the project's bots or simulators on the same seeds, then reports the difference with ranges and a verdict against the design contract's targets. Also maps what the change touches. Use when the user asks "what if we change X", "will this make it too easy", "predict the effect", or before a tuning, economy or level change.

