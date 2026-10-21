# Engine Selection Matrix

Summary: a criteria-driven way to choose a mobile game engine. It defines the criteria and default weights, gives a comparison of Godot, Unity, Unreal, Defold, Cocos Creator, web stacks, Bevy, GameMaker, Construct, GDevelop, Solar2D, Flame and fully native development, then a step-by-step decision procedure with worked examples and a spike protocol. Qualitative ratings are judgments from the research notes plus general practice; cells marked "verify" need a spike or current documentation.

## Contents
1. Criteria and default weights
2. Agent-friendliness criteria
3. Engine profiles
4. Comparison matrix
5. Scoring procedure
6. Worked examples
7. The one-day spike
8. Switching costs and portability
9. Red flags by engine
10. Volatile facts (as of Oct 2026 - verify)

## 1. Criteria and default weights

| # | Criterion | What to ask | Default weight |
|---|---|---|---|
| 1 | SDK coverage | Are ads, IAP, attribution, push and analytics available and maintained? | 5 |
| 2 | Performance fit | Does it hit 30 or 60 FPS on your lowest target device with your content? | 5 |
| 3 | Build automation | Can CI produce signed Android and iOS builds headlessly? | 4 |
| 4 | Agent verification | Can an agent run the game and observe state without a GUI? | 4 |
| 5 | Team skill | Language and tool familiarity | 4 |
| 6 | Size fit | Install size and download size against budget | 3 |
| 7 | Licence fit | Fees at expected revenue; source access | 3 |
| 8 | Ecosystem | Assets, docs, community, hiring | 2 |
| 9 | API churn risk | How fast APIs move relative to model knowledge | 2 |
| 10 | Platform breadth | Web, console, desktop later | 1-3 (depends on plan) |

Adjust weights per project and record them. Weights must be set before scoring to avoid reverse-engineering the answer.

## 2. Agent-friendliness criteria

| Factor | Good | Weak |
|---|---|---|
| Asset format | text, diffable (Godot scenes, Defold collections, code-only) | binary assets (Unreal), dense YAML with GUIDs (Unity) |
| Language | large training corpus (C#, TypeScript, JavaScript) | smaller corpus or fast-changing API (GDScript less so, Rust/Bevy API churn) |
| Headless build | one command (Godot export, Defold bob.jar, Unity batchmode, Vite + Capacitor) | heavy toolchain (Unreal UAT) |
| Run without GUI | headless scripts, movie capture, MCP stepping, headless browser | requires editor |
| Static checks | compile or parse step that fails fast (C#, TypeScript) | runtime-only errors |
| MCP/automation | maintained bridges | thin or none |

Practitioner reports in the notes (anecdotal, mostly 2026 blog and forum posts) say Godot's text scenes make it the easiest for agents, with the known hazards of invented UIDs and Python idioms; Unity works but needs more care because scenes are ID-heavy YAML, so scenes should be built by editor scripts. Treat these as informative, not definitive.

## 3. Engine profiles

**Godot 4** (MIT). 2D strong, 3D mid-tier on mobile, text scenes, headless export, GDScript or C# (C# on mobile marked experimental in docs). Monetization via Foundation-maintained billing/StoreKit 2 plugins plus community and AppLovin plugins. See `engine-godot`.

**Unity 6** (proprietary; seat fees above a revenue threshold; no runtime fee). Highest ceiling for 3D and richest SDK ecosystem; C#; URP; large editor tooling; automation through batchmode, CLI, MCP. See `engine-unity`.

**Unreal 5.x** (royalty above a lifetime-revenue threshold). Top visual fidelity on high-end devices; large installs; C++ and Blueprints; binary assets; experimental official MCP plugin. See `references/unreal-defold-cocos.md`.

**Defold** (free, source-available licence). Very small runtime, Lua, strong 2D, component model, official ad extensions, headless builds via bob.jar. Thin MCP ecosystem. Console targets listed.

**Cocos Creator** (free, custom licence). TypeScript, strong in the Asian mobile and mini-game market, 2D and basic 3D, web and native exports. Fewer English docs; verify licence terms for your case.

**Web stacks.** Phaser 4 (2D, WebGL2), PixiJS 8 (renderer, WebGL/WebGPU), three.js and Babylon.js (3D), PlayCanvas (engine plus cloud editor), wrapped with Capacitor for stores or served as PWA. TypeScript, instant iteration, headless-browser verification, bounded by WebView performance.

**Bevy** (Rust, Apache-2.0 or MIT). Code-only ECS; API changes quickly between releases; mobile examples exist but production maturity on mobile unverified in the notes. Good for programmers who want Rust; risky for agents because the API outpaces training data (agents should read the installed source).

**GameMaker** (proprietary, commercial licence tiers). 2D, GML language, fast prototyping, mobile export; closed ecosystem; text project files are partly XML/JSON; verify agent workflow.

**Construct** (browser-based, subscription). No-code event sheets, HTML5 export, wrapper for mobile; agent automation weak because logic lives in visual event sheets (project files are JSON but not designed for hand editing).

**GDevelop** (open-source core, free tier with cloud services). No-code events, JSON project, mobile export via its build service; good for non-programmers; limited custom control.

**Solar2D** (Lua, MIT, formerly Corona). Lightweight 2D, fast iteration; small community; SDK coverage via plugins; verify maintenance.

**Flame** (Flutter-based 2D engine, MIT). Dart; good if the app is a Flutter app with game elements; performance fine for casual 2D; SDK coverage via Flutter plugins (large ecosystem for IAP, ads, notifications).

**Native** (Swift/SpriteKit/Metal on iOS, Kotlin/Jetpack/Vulkan on Android). Maximum control and smallest size, double the work, no shared code unless using a shared core (Kotlin Multiplatform or C++). Rare for games outside of very specific needs.

## 4. Comparison matrix

Legend: strong / ok / weak / verify.

| Engine | 2D | 3D | Size | Ad/IAP SDKs | Headless build | Agent verification | Language | Licence cost |
|---|---|---|---|---|---|---|---|---|
| Godot | strong | ok (mid-tier) | ok (tens of MB) | ok (plugins) | strong | strong (CLI, movie, MCPs) | GDScript, C# (mobile experimental) | none |
| Unity | strong | strong | ok (tens of MB) | strong | strong | strong (tests, CLI, MCP) | C# | free tier then seats |
| Unreal | ok | strong (high-end) | weak (large) | ok | ok (heavy UAT) | ok (experimental MCP, PIE) | C++, Blueprints | royalty above threshold |
| Defold | strong | weak | strong (smallest) | strong (official extensions) | strong (bob.jar) | ok (thin MCP, headless run) | Lua | none |
| Cocos Creator | strong | ok | ok | ok (verify) | ok (verify) | ok (one popular MCP) | TypeScript | free, custom licence |
| Web + Capacitor | ok | ok | strong (small assets) | ok (plugins) | strong | strong (headless browser) | TypeScript | none |
| Bevy | ok | ok | verify | weak | ok (cargo) | ok (offscreen capture) | Rust | none |
| GameMaker | strong | weak | ok | ok | ok (verify) | weak | GML | paid tiers |
| Construct | ok | weak | ok | ok (plugins/wrapper) | weak | weak | no-code | subscription |
| GDevelop | ok | weak | ok | ok | ok (cloud build) | weak | no-code events | free and paid |
| Solar2D | ok | weak | strong | ok (plugins) | ok | weak | Lua | none |
| Flame | ok | weak | ok | strong (Flutter plugins) | strong (flutter build) | ok | Dart | none |
| Native | ok | strong (Metal/Vulkan work) | strong | strong | strong | weak | Swift, Kotlin | none |

Size note: the notes cite one 2026 blog for minimal builds (Unity 30-50 MB, Godot 30-60 MB, Unreal 150-300 MB) and older forum posts (dated) suggesting Defold is several times smaller. Methodology was weak; measure your own empty export per target.

## 5. Scoring procedure

1. List candidate engines (maximum four).
2. Apply hard constraints (see `SKILL.md` table). Remove failures with a one-line reason.
3. Score each remaining candidate 1-5 per criterion with a one-line evidence note (doc link, spike result, team experience).
4. Compute weighted score: sum(weight x score) / sum(weight x 5).
5. Identify the criterion where each candidate is weakest; ask whether that weakness is a project killer. A candidate with any score of 1 on weight 4-5 criteria needs a mitigation plan or is out.
6. If the top two are within ten percent, pick the lower monetization-SDK risk, then the stronger team skill.
7. Spike (section 7) and revise.

Formula example:

```
score = sum_i(w_i * s_i) / (5 * sum_i(w_i))
```

## 6. Worked examples

**A. Match-3 with live events, ads and IAP, mid-tier Android and iPhone, three engineers with C# experience.**
Hard constraints: none eliminate. SDK coverage weight 5 favors Unity (first-party mediation, IAP). Godot would need plugin work. Performance fit is fine for either. Choice: Unity 6 LTS with URP 2D renderer; Godot is the runner-up if licence costs matter. Spike: rewarded ad plus IAP sandbox purchase on both platforms within two days.

**B. Minimal puzzle game targeting under 15 MB install on low-end Android.**
Size weight rises to 5. Defold scores highest on size with official ad extensions; Godot's baseline is larger; Unity's baseline is larger still. Choice: Defold, risk Lua familiarity and thinner tooling for agents; mitigation: strict module structure and headless tests via a Lua test runner on the sim-core.

**C. Narrative 3D adventure with cinematic lighting for high-end phones.**
Performance and visuals dominate. Unity URP scores high; Unreal scores highest on visual ceiling but fails size and schedule risk for a small team; Godot Mobile renderer is a possibility for stylized art. Choice: Unity unless art direction is stylized and the team prefers Godot; run a stress scene on target hardware.

**D. Playable-ad-first studio shipping short interactive experiences and one casual app.**
Web stack (PixiJS or Phaser) for playables and prototypes, plus Capacitor for the app, with a shared TypeScript sim-core. Risk: WebView performance and store acceptance of wrapped apps; mitigation: perf spike and store-policy check.

**E. Hobbyist, no code, wants a simple tap game.**
GDevelop or Construct; accept limited agent automation; keep scope tiny.

## 7. The one-day spike

Goal: eliminate surprises before committing.

Checklist (all on the lowest target device unless noted):
1. Create the project and a scene with a touch-responsive button and a counter.
2. Export a signed debug build for Android and run it; for iOS, a debug build on a device or simulator.
3. Cold start time to first interactive frame (stopwatch or log); record the install size.
4. Draw the representative stress scene (for example 300 sprites with alpha, or a 3D scene with the intended lighting) and record p95 frame time for 60 seconds.
5. Integrate one rewarded ad test unit and one sandbox purchase (or confirm the SDK installs and initializes).
6. Run one automated test headlessly (unit test and a scripted playthrough).
7. Run the CI build on a clean clone.
8. Write down surprises, time spent, and a go or no-go.

A spike that cannot complete steps 2, 3 and 5 on its first day is itself a signal of integration risk.

## 8. Switching costs and portability

What ports across engines if designed well (see `game-architecture`):
- Rules, state and simulation (sim-core) if kept pure and data-driven; port is a language translation.
- Tuning data and level data as JSON.
- Economy and progression design, analytics taxonomy, content, art source files, audio.

What does not port: scenes, prefabs, shaders (rewrite), UI layout, plugin integrations, build and CI config, engine-specific editor tooling.

Rule: keep a language-neutral spec of the sim-core (schemas, golden playthrough JSON files) so a second implementation can be verified by replaying the same playthroughs. This is also the cheapest regression test.

## 9. Red flags by engine

| Engine | Red flags to check early |
|---|---|
| Godot | Android GPU driver issues on the Mobile renderer; plugin maturity for your ad network; C# on mobile experimental |
| Unity | Licence tier and seat cost at expected revenue; in-editor AI/MCP pricing and deprecations (do not depend); package churn between LTS versions |
| Unreal | Install size, build times, minimum device spec, Blueprint-heavy projects hard for agents |
| Defold | Lua-only tooling, small plugin ecosystem outside ads, 3D limits |
| Cocos | Licence text, English documentation, release cadence |
| Web | WebView memory limits, audio unlock, store review for wrappers, no true background execution |
| Bevy | API churn, mobile maturity, no mature mobile SDK ecosystem |
| GameMaker/Construct/GDevelop | Limits at scale; export and plugin costs; agent automation |
| Native | Double the workload; shared core needed |

## 9b. Genre defaults (starting points, not rules)

| Genre | First choice | Second choice | Why |
|---|---|---|---|
| Hyper-casual, tiny size | Defold | Godot | size and startup |
| Puzzle, match-3, merge | Godot or Unity | Defold | deterministic sim-core, event-heavy live-ops favors Unity SDKs |
| Idle, incremental, card | Godot | web + Capacitor | UI heavy, simple rendering |
| Endless runner, arcade 2D | Godot | Unity, Defold | 2D strength, fast iteration |
| Stylized 3D action | Unity | Godot Mobile renderer | tooling and SDKs vs licence and agent friendliness |
| Realistic 3D, high-end only | Unity | Unreal | see the Unreal decision in `SKILL.md` |
| Casual multiplayer, async | Unity or Godot with a managed backend | web | backend choice matters more (`multiplayer-backend`) |
| Playable ads, portals | PixiJS or Phaser | PlayCanvas | size and web delivery |
| Word, trivia, board | web + Capacitor or Flutter/Flame | Godot | UI-centric, plugin ecosystem |

Re-check the default against the criteria table for any project with unusual constraints.

## 10. Volatile facts (as of Oct 2026 - verify)

| Fact | Source |
|---|---|
| Godot 4.7.2 stable; Unity 6.3 LTS (supported to Dec 2027) with 6.7 LTS expected; UE 5.8; Defold 1.14.0; Cocos Creator 3.8.8 latest tag; Bevy 0.20.0 | https://github.com/godotengine/godot/releases ; https://www.cgchannel.com/2025/12/unity-6-3-lts-is-out-see-5-key-features-for-cg-artists/ ; https://github.com/defold/defold/releases ; https://github.com/cocos/cocos-engine/releases ; https://github.com/bevyengine/bevy/releases |
| Unity: no runtime fee; free Personal tier under a revenue and funding threshold; Pro priced per seat (increase Jan 2026) | https://unity.com/products/pricing-updates |
| Unreal: royalty above a lifetime gross threshold; reduced rate under a store program (secondary source) | https://www.unrealengine.com/en-US/news/unreal-engines-improved-royalty-reporting-system |
| Godot MIT; Defold free with its own licence; Cocos Creator free with custom licence (terms not found); Bevy Apache-2.0 | https://github.com/godotengine/godot ; https://defold.com/faq/faq/ ; https://www.cocos.com/en/creator ; https://github.com/bevyengine/bevy |
| Minimal build size comparison (weak methodology) | https://oceanviewgames.co.uk/blog/posts/unity-vs-godot-vs-unreal-mobile-games |
| Agent-friendliness reports for Godot vs Unity (anecdotal) | https://dev.to/mistyhx/why-ai-writes-better-game-code-in-godot-than-in-unity-10hf and https://news.ycombinator.com/item?id=47146712 |
| Godogen supports Godot, Bevy, Babylon.js and three.js, not Unity or Unreal | https://github.com/htdt/godogen |
| Pricing and terms for GameMaker, Construct, GDevelop, Solar2D, Flame | not in the notes; check each vendor's site |

Note: ratings in this file are judgments; replace any rating that matters to your decision with spike evidence and record it in the design contract.
