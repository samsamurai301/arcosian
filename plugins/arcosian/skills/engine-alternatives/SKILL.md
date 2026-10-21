---
name: engine-alternatives
description: Engine selection and quick-starts beyond Godot and Unity for mobile - Unreal, Defold, Cocos Creator, web stacks (Phaser, PixiJS, three.js, Babylon, PlayCanvas, Capacitor), Bevy, GameMaker, Construct, GDevelop, Solar2D, Flame, native. Use when asked which engine to use, whether to pick Unreal or Defold, how to ship a web game as an app, how to make a playable ad, or to compare engines.
---

# Engine Selection and Alternatives

## What this skill gives you
- A weighted decision procedure for picking an engine from the game's needs, the team, and agent-friendliness, with a default answer when nothing is decisive.
- A matrix of the main mobile options (strengths, constraints, licences, agent verification paths).
- Honest guidance on when Unreal makes sense on phones, and quick-starts for Defold and Cocos Creator.
- Web and hybrid routes (Phaser, PixiJS, three.js, Babylon.js, PlayCanvas, Capacitor), WebGPU status, and playable ad constraints.
- Pointers to the dedicated skills for the two default engines, `engine-godot` and `engine-unity`.

## Core models

**1. The engine is a production-risk decision, not a taste decision.**
Score engines on what can sink the project: platform SDK availability (ads, IAP), build and verification automation, performance ceiling for your content, team skills, licence terms at your expected revenue, and size budget. Visual preference comes last.

**2. Agent-friendliness is a real criterion in this plugin.**
Text-based assets, headless build commands, text languages with large training corpora, and a way to run and observe the game without a GUI make autonomous work reliable. Rank accordingly (details in `references/engine-selection-matrix.md`).

**3. Default routes.**
- 2D, casual, puzzle, idle, card, hyper-casual: Godot 4 (typed GDScript), see `engine-godot`.
- 3D-heavy or ad-and-SDK-heavy commercial mobile: Unity 6 LTS with URP, see `engine-unity`.
- Smallest builds, 2D, mature ad extensions: Defold.
- Web distribution, playables, portals, social: a web stack.
- Deviate only with a written reason in the design contract tech section.

**4. Sunk cost and team skill dominate technical differences.**
A team that ships in Unity should not switch to Godot for ideology; the plugin's agents can drive either. Switch only when a hard constraint (size, licence, platform) demands it.

**5. Prototype fidelity differs from ship fidelity.**
A web prototype can validate the core loop in hours; the ship engine may differ. State explicitly whether prototype code is throwaway. Keep the rules in a portable form (sim-core) so an engine change is a presentation rewrite, not a redesign (`game-architecture`).

## Decision procedures

### A. Pick an engine
1. Write constraints: genre, 2D or 3D, target devices (low-end Android?), session length, online needs, monetization (ads, IAP, subscriptions), team skills, schedule, budget.
2. Eliminate by hard constraints using the table below.
3. Score the survivors 1-5 on: SDK coverage, build automation, agent verification, performance fit, size fit, licence fit, team skill, risk of API churn. Weight by importance (default weights in the matrix reference).
4. If the top two are within 10 percent, choose the one with the lower integration risk for monetization SDKs.
5. Run a 1-day spike on the winner: boot on a real low-end device, show a touch-responsive screen, run the headless build, run one automated test. Fail fast.
6. Record the decision and the kill criteria in the design contract.

| Hard constraint | Eliminates |
|---|---|
| Install size under ~20 MB | Unreal; likely Unity and Godot with defaults (verify with a spike); favors Defold, native, small web wrappers |
| Heavy 3D with advanced lighting on high-end phones | Defold, Phaser, GameMaker |
| Needs first-party mediation SDKs with minimal glue | prefer Unity; Defold has official extensions; Godot needs plugin work |
| Web-only or playable ad | native engines (except exports to web: Godot, Defold, Cocos, Unity web) |
| Team knows only TypeScript | favors Cocos Creator, Phaser, PixiJS, Babylon.js, PlayCanvas, Capacitor |
| Zero licence cost and no seat fees | Unity Pro seats (above the free-tier threshold), Unreal royalties above their threshold |
| Console ports planned | Unity, Unreal, Godot via third parties, Defold (listed console targets) |

### B. Decide whether Unreal is justified on mobile
1. Is the core experience a high-fidelity 3D game that cannot be delivered in Unity or Godot? If no, stop; use another engine.
2. Does the team have C++ or Blueprint skill and desktop-class art pipelines (Nanite and Lumen do not run on mobile; the mobile renderer is a different path)?
3. Can the install size (reported 150-300 MB minimal) and device targets be tolerated?
4. Can you afford long builds and a binary-asset workflow that is poor for diffs and agents?
5. If all yes, see `references/unreal-defold-cocos.md` for constraints and the experimental official MCP plugin.

### C. Ship a web game as a mobile app
1. Build with a web stack (Phaser, PixiJS, three.js, Babylon.js, PlayCanvas) and Vite or similar; test in mobile browsers.
2. Wrap with Capacitor for store distribution; add native plugins for IAP, ads, haptics, push as needed.
3. Budget for WebView performance limits, memory pressure, audio unlock rules, and store review for web-wrapper apps (verify guidelines; apps must offer more than a repackaged website).
4. Verify with headless Chrome or Playwright for logic/visuals, then on devices for performance.
Details in `references/web-and-others.md`.

### D. Build a playable ad
1. Constraints: very small file size (network-specific caps; verify), no external requests, single HTML file or small bundle, call-to-action hooks per network.
2. Use a light stack (PixiJS, plain canvas, or an engine's playable export) and inline assets (compressed, base64).
3. Test on each ad network's previewer.
See `references/web-and-others.md`.

### E. Worked example: a one-thumb idle game, two engineers, TypeScript background
1. Constraints: 2D, tiny sessions, rewarded ads and IAP, low-end Android, store release in three months.
2. Hard-constraint pass: nothing eliminated; TypeScript skill favors Cocos Creator and web stacks; ad SDK need favors Unity, Defold or a Capacitor wrapper with plugins.
3. Scoring (illustrative): Godot scores high on agent verification and licence but needs ad plugin work; Defold scores high on size and ad extensions but Lua is new to the team; a web stack plus Capacitor scores high on skill, with WebView performance as the risk.
4. Spike: one day each on the top two, measuring cold start, memory and one rewarded ad test on a low-end phone.
5. Decision and kill criteria written to the contract: switch only if the spike misses the budget by more than the agreed margin.

## Mobile specifics
- Store SDK reality: ads, IAP, attribution and push are easiest in Unity, workable in Defold (official extensions), and plugin-dependent in Godot, Cocos and web wrappers. Check this before committing.
- Size: base runtime size varies widely between engines; measure an empty project export on your target before trusting any published number.
- Android fragmentation: GPU driver quirks hit Vulkan paths hardest; prefer an engine's GLES fallback for low-end coverage when relevant.
- iOS builds require macOS and Xcode for every engine.
- Web in a WebView is bounded by the WebView's memory and JIT behavior; keep assets small and avoid very large textures.
- Thermal behavior depends mostly on your content and frame cap, not the engine brand.

## Anti-patterns
| Anti-pattern | Detect | Fix |
|---|---|---|
| Choosing by benchmark blog post | decision lacks a device test | run your own spike on a low-end phone |
| Choosing Unreal for a casual game | art and size budgets mismatched | pick a lighter engine |
| Choosing a web stack without a store plan | no wrapper, no SDK plan | decide Capacitor or PWA distribution early |
| Rewriting the engine mid-project | schedule slips | keep sim-core portable, switch only at milestones with evidence |
| Trusting version numbers from memory | stale claims in docs | verify in the volatile-facts sections |
| Picking a niche engine with no ad SDK | monetization plan blocked | verify SDK coverage first |
| Ignoring licence thresholds | revenue plan exceeds free tier | read current terms in the matrix reference |

## Using the ontology
- The decision record maps to the project state's tech section (`gs.py`); the design contract lists the chosen engine, renderer, target devices and kill criteria.
- The rules stay engine-agnostic in the sim-core (`game-architecture`); only presentation and services change per engine.
- Perf budgets (`mobile-performance`) are checked per device tier with `${CLAUDE_PLUGIN_ROOT}/scripts/perf_budget.py`.

## Reference library
| File | What it contains | When to read |
|---|---|---|
| `references/engine-selection-matrix.md` | Criteria, weights, matrix for Godot, Unity, Unreal, Defold, Cocos, web, Bevy, GameMaker, Construct, GDevelop, Solar2D, Flame, native; decision procedure with worked examples | Choosing or defending an engine |
| `references/unreal-defold-cocos.md` | When Unreal on mobile makes sense and constraints, the UE 5.8 MCP plugin, Defold and Cocos Creator quick-starts | Evaluating or starting with those engines |
| `references/web-and-others.md` | Phaser 4, PixiJS 8, three.js, Babylon.js, PlayCanvas, Capacitor, WebGPU status, playable ads, Bevy and other options | Web, hybrid, playable and niche routes |

## Related skills
- `engine-godot`: default for 2D and casual.
- `engine-unity`: default for 3D-heavy and SDK-heavy.
- `game-architecture`: keeps rules portable across engines.
- `mobile-performance`: budgets and device tiers to test engines against.
- `technical-art`: import pipelines and shaders per engine.
- `store-release`: wrapper and review considerations.
- `legal-ethics`: licence terms and SDK compliance.
