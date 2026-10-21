# Design and Technology Terms

This file defines game design, gameplay engineering, networking, rendering and mobile-performance terms. Use it when a design doc, code review, profiler trace or architecture discussion uses a term you need to pin down. Entries are alphabetical; each entry is one line in the form **Term** — definition — see: related term or skill.

## Contents
- A: AABB (axis-aligned bounding box) through Axis-aligned bounding box
- B: Backlog grooming through Bytes per second (bandwidth budget)
- C: Cache (LRU) through Cyclomatic complexity
- D: Dead reckoning through Dynamic resolution scaling
- E: Easing function through Exploit
- F: Feature flag through Funnel
- G: Game feel (juice) through Grind
- H: Hitbox and hurtbox through Hysteresis
- I: Idempotency through Interpolation (entity)
- J: Jank through Jitter (network)
- K: Kill switch through Kinematic body
- L: Latency compensation (lag compensation) through Loot table
- M: Memory budget through Mutation testing
- N: Navmesh through Null object
- O: Object pooling through Overdraw
- P: Parallax through Pseudo-random distribution
- Q: Quality gate through Quantization (network)
- R: Regression test through Rubber banding
- S: Save migration through System (ECS)
- T: Tick through Tween
- U: Undo/redo (command pattern) through UV mapping
- V: Vertex count through Vsync
- W: Weighted random through Working set
- Z: Zero-allocation path through Z-fighting

## A

**AABB (axis-aligned bounding box)** — Simplest box volume aligned to world axes; cheap overlap test used in the broad phase of collision. — see: `game-architecture`
**A/B test** — Randomized split of players into variants to measure a pre-declared metric; fix sample size and stopping rule before starting. — see: `player-analytics`
**Acceptance criteria** — Testable conditions a feature must meet to be called done; written before implementation starts. — see: `production`
**Actor model** — Concurrency model where isolated actors exchange messages instead of sharing state; common for match and player-session servers. — see: `multiplayer-backend`
**Adaptive quality** — Automatically lowering render cost (resolution, effects, distance) when frame time exceeds budget. — see: `mobile-performance`
**Affordance** — Visible property of an object that signals how it can be used, such as a ledge that looks climbable. — see: `design-theory`
**Aggro (threat table)** — Per-enemy record of which player has dealt the most threat, which decides its target. — see: `gameplay-programming`
**Alpha test** — Internal build test of feature completeness and stability before wide external testing. — see: `qa-testing`
**Animation blend tree** — Graph that blends several clips by a parameter such as speed or direction to avoid visible pops. — see: `technical-art`
**Animation state machine** — Graph of animation states and transitions driven by gameplay parameters; keep gameplay logic out of it. — see: `technical-art`
**Anti-cheat (server-authoritative)** — Design where the server owns outcomes and clients send only intents, so tampering cannot change results. — see: `multiplayer-backend`
**Asset bundle** — Packaged set of assets loaded on demand; the unit of downloads, DLC and patching. — see: `engine-unity`
**Asset pipeline** — Ordered set of import, convert, validate and package steps that turns source art and audio into shippable assets. — see: `technical-art`
**Asynchronous loading** — Loading resources on a background thread or across frames so the main thread does not stall. — see: `mobile-performance`
**Atlas (texture atlas)** — Many sprites or textures packed into one texture to cut draw calls and texture swaps. — see: `technical-art`
**Authoritative server** — Single simulation on the server is the truth; clients predict locally and reconcile to it. — see: `multiplayer-backend`
**Autotile** — Tile rules that choose the right edge or corner variant from neighbouring tiles so tile art joins cleanly. — see: `level-design`
**Axis-aligned bounding box** — See AABB. — see: `game-architecture`

## B

**Backlog grooming** — Ongoing trimming, estimating and ordering of work items so the next iteration can be pulled cleanly. — see: `production`
**Baking (lightmap baking)** — Precomputing lighting into textures offline; trades build time and memory for runtime cost. — see: `technical-art`
**Batching** — Combining draw calls that share material and state into fewer GPU submissions. — see: `mobile-performance`
**Behavior-driven development (BDD)** — Writing tests as given/when/then scenarios that non-engineers can read and review. — see: `qa-testing`
**Behavior tree** — Tree of selectors, sequences and decorators evaluated each tick to choose AI actions; modular and readable. — see: `gameplay-programming`
**Bin packing** — Algorithm for placing rectangles such as sprites into the smallest atlas. — see: `technical-art`
**Blackboard (AI)** — Shared key-value store that AI nodes read and write as context for decisions. — see: `gameplay-programming`
**Blend shape (morph target)** — Stored vertex offsets used to animate facial or body shape changes. — see: `technical-art`
**Bloom** — Post effect that spreads light from bright areas; cheap at small resolutions but costs fill rate. — see: `technical-art`
**Breakpoint (responsive)** — Screen width at which UI layout changes; on mobile also plan for safe areas and aspect ratios. — see: `mobile-ux`
**Budget (frame)** — Millisecond or memory allowance per system, derived from the target frame rate. — see: `mobile-performance`
**Build pipeline** — Scripted, repeatable process from source to signed binary; the foundation of continuous integration. — see: `store-release`
**Bundle identifier** — Reverse-DNS string that names an app on each store; changing it later creates a different app. — see: `store-release`
**Burst compiler** — Unity compiler that turns restricted jobs code into optimized native code. — see: `engine-unity`
**Bytes per second (bandwidth budget)** — Network budget per client that limits how much state can be replicated each second. — see: `multiplayer-backend`

## C

**Cache (LRU)** — Fixed-size store that evicts the least recently used entry; used for textures, asset data and server reads. — see: `mobile-performance`
**Camera rig** — Layered camera nodes (pivot, arm, camera) that separate follow, aim and shake behaviour. — see: `game-feel`
**Canary release** — Shipping to a small share of users first and watching health metrics before widening. — see: `store-release`
**Chunking (world)** — Dividing a world into streamable blocks loaded and unloaded by distance from the player. — see: `level-design`
**Client-side prediction** — Client applies its own input immediately and reconciles when authoritative state arrives. — see: `multiplayer-backend`
**Cognitive load** — Mental effort a screen or rule demands; reduce it by removing choices the player does not need yet. — see: `mobile-ux`
**Collider** — Shape used by physics or triggers to detect contact; simpler shapes are cheaper and more stable. — see: `game-architecture`
**Collision layer and mask** — Bitfields that decide which physics categories test against each other; removes wasted checks. — see: `game-architecture`
**Component (ECS)** — Plain data attached to an entity; behaviour lives in systems that process matching components. — see: `game-architecture`
**Config-driven design** — Keeping tuning values in data files rather than code so designers can change them without a build. — see: `economy-design`
**Continuous integration (CI)** — Automated build and test on every change; the gate that keeps the main branch shippable. — see: `production`
**Core loop** — The smallest repeated cycle that produces the game's main feel, such as act, reward, decide, act again. — see: `game-ontology`
**Coyote time** — Short grace window after leaving a ledge during which a jump still succeeds; a standard platformer feel tool. — see: `game-feel`
**Culling** — Skipping rendering or simulation of things that are not visible or not relevant. — see: `mobile-performance`
**Cutscene** — Authored non-interactive sequence; on mobile keep skip options and a sensible length. — see: `narrative-design`
**Cyclomatic complexity** — Count of independent paths through a function; high values predict bugs and hard-to-write tests. — see: `game-architecture`

## D

**Dead reckoning** — Extrapolating a remote entity's position from its last known velocity until the next update arrives. — see: `multiplayer-backend`
**Debug draw** — Drawing lines, boxes and text in the world during development to expose hidden state. — see: `gameplay-programming`
**Delta time** — Time since the last frame, used to make motion frame-rate independent. — see: `game-architecture`
**Dependency injection** — Passing collaborators in rather than creating them, so tests can substitute fakes. — see: `game-architecture`
**Determinism** — Same inputs and seed always produce the same state; enables replays, lockstep and reproducible bugs. — see: `game-architecture`
**Difficulty curve** — Planned change in challenge over time; plot it and check that every spike has a recovery point. — see: `progression-difficulty`
**Dirty flag** — Boolean marking cached data as stale so it is recomputed only when needed. — see: `game-architecture`
**Double buffering** — Drawing to a back buffer while the front buffer is shown, then swapping, to avoid tearing and half-drawn frames. — see: `mobile-performance`
**Draw call** — One GPU submission; a classic mobile bottleneck when counts are high. — see: `mobile-performance`
**Dynamic batching** — Engine merges small meshes at runtime; only works within vertex limits and shared materials. — see: `mobile-performance`
**Dynamic resolution scaling** — Lowering render resolution when frame time exceeds budget and restoring it when there is headroom. — see: `mobile-performance`

## E

**Easing function** — Curve that shapes interpolation (ease-in, ease-out, overshoot) so motion reads as natural. — see: `game-feel`
**ECS (entity-component-system)** — Architecture separating identity (entity), data (component) and behaviour (system) for cache-friendly updates. — see: `game-architecture`
**Edge-case matrix** — Table of boundary and error conditions per feature, used to design tests and review specs. — see: `qa-testing`
**Entity** — Identifier of a game object; holds data through components rather than logic of its own. — see: `game-architecture`
**Event bus** — Publish/subscribe channel that decouples senders from listeners; keep it typed and traceable. — see: `game-architecture`
**Event sourcing** — Storing state as an ordered log of events and deriving current state from it; useful for audits and replays. — see: `multiplayer-backend`
**Exploit** — Unintended mechanic that yields outsized gain; find it with simulation, bots and adversarial playtests. — see: `qa-testing`

## F

**Feature flag** — Runtime switch that enables or disables a code path without a new build. — see: `liveops`
**Feedback loop** — Output feeding back into input; positive loops amplify (snowball), negative loops stabilize. — see: `economy-design`
**Finite state machine (FSM)** — Object in one of a fixed set of states with explicit transitions; the simplest control structure. — see: `gameplay-programming`
**Fixed timestep** — Simulation advances in constant steps regardless of render rate; required for determinism. — see: `game-architecture`
**Flow** — Mental state where challenge matches skill; a design target that is hard to measure directly. — see: `player-psychology`
**Frame budget** — Target frame time (about 16.7 ms at 60 fps) divided across simulation, render and scripting. — see: `mobile-performance`
**Frustum culling** — Skipping objects outside the camera view volume. — see: `mobile-performance`
**FTUE (first-time user experience)** — Scripted first session that teaches the core loop with the least friction. — see: `mobile-ux`
**Funnel** — Ordered steps (install, tutorial complete, first purchase) with the drop-off measured at each step. — see: `player-analytics`

## G

**Game feel (juice)** — Feedback layer (camera shake, hit stop, easing, sound) that makes actions read as impactful. — see: `game-feel`
**Game loop** — Repeated cycle of input, update and render; fixed-step simulation with variable render is typical. — see: `game-architecture`
**Gameplay tag** — Hierarchical label such as State.Stunned used to query and grant states across systems. — see: `gameplay-programming`
**Garbage collection (GC) spike** — Frame stall when a managed runtime collects memory; avoid per-frame allocation on mobile. — see: `mobile-performance`
**GPU instancing** — Drawing many copies of one mesh in a single call with per-instance data. — see: `technical-art`
**Grind** — Repetitive, time- or effort-gated activity; design it as a choice rather than a toll. — see: `progression-difficulty`

## H

**Hitbox and hurtbox** — Hitbox deals damage, hurtbox receives it; keep them separate for readable combat. — see: `gameplay-programming`
**Hit stop (freeze frame)** — Brief pause on impact to sell force; a few frames at most. — see: `game-feel`
**Hot path** — Code run every frame or per event; the only place micro-optimization usually pays off. — see: `mobile-performance`
**Hot reload** — Applying code or asset changes to a running build; speeds iteration and is not a shipping feature. — see: `engine-godot`
**Hysteresis** — Different thresholds for entering and leaving a state, which prevents flicker at the boundary. — see: `game-architecture`

## I

**Idempotency** — Operation that can be repeated safely with the same result; essential for purchases and retries. — see: `multiplayer-backend`
**Input buffering** — Storing an input shortly before it becomes valid so it fires on time; improves responsiveness. — see: `game-feel`
**Input latency** — Delay from physical touch to on-screen response; measure end to end, not only in code. — see: `mobile-performance`
**Interpolation (entity)** — Rendering remote entities slightly behind the latest snapshot to keep motion smooth. — see: `multiplayer-backend`

## J

**Jank** — Visible stutter caused by missed frames or hitches. — see: `mobile-performance`
**Jitter (network)** — Variation in packet arrival time; jitter buffers trade variation for added delay. — see: `multiplayer-backend`

## K

**Kill switch** — Remote control that disables a feature or event quickly after a bug or incident. — see: `liveops`
**Kinematic body** — Physics body moved by code rather than forces; used for characters and moving platforms. — see: `game-architecture`

## L

**Latency compensation (lag compensation)** — Server rewinds the world to the shooter's view time to validate hits fairly. — see: `multiplayer-backend`
**Lerp** — Linear interpolation between two values; the base of smoothing and blending. — see: `game-feel`
**Level of detail (LOD)** — Swapping to simpler meshes or systems as objects move farther from the camera. — see: `technical-art`
**Lightmap** — Texture that stores baked lighting for static geometry. — see: `technical-art`
**Lobby** — Pre-match space where players gather and ready up before a session starts. — see: `multiplayer-backend`
**Localization (l10n)** — Adapting text, audio, art and layout to a locale. — see: `accessibility-localization`
**Lockstep** — Netcode where every client runs the same deterministic simulation from shared inputs; common in strategy games. — see: `multiplayer-backend`
**Logging (structured)** — Machine-readable event logs with stable IDs; the basis for crash and support triage. — see: `production`
**Loot table** — Weighted list of drops with probabilities; document expected value and rarity for players and regulators. — see: `economy-design`

## M

**Memory budget** — Allowed RAM per device tier; exceeding it leads to OS termination on mobile. — see: `mobile-performance`
**Metaprogression** — Progression that persists across runs or sessions, such as unlocks and permanent upgrades. — see: `progression-difficulty`
**Mipmap** — Pre-filtered smaller copies of a texture to reduce aliasing and bandwidth at distance. — see: `technical-art`
**Mock** — Test double that records calls; use sparingly and prefer fakes for logic-heavy code. — see: `qa-testing`
**Multiplayer tick rate** — Server simulation or send rate per second; higher is smoother and more expensive. — see: `multiplayer-backend`
**Mutation testing** — Injecting small bugs to see whether tests catch them; measures test quality rather than coverage. — see: `qa-testing`

## N

**Navmesh** — Walkable-area mesh used for pathfinding and agent steering. — see: `gameplay-programming`
**Netcode** — Overall system that keeps networked players' game state consistent and responsive. — see: `multiplayer-backend`
**Noise (Perlin or simplex)** — Smooth pseudo-random function used for terrain, textures and natural variation. — see: `procedural-generation`
**Null object** — Stand-in object with no-op behaviour that removes null checks from callers. — see: `game-architecture`

## O

**Object pooling** — Reusing pre-allocated objects instead of creating and destroying them each time. — see: `mobile-performance`
**Observer pattern** — Subject notifies registered listeners when it changes; the basis of events and UI binding. — see: `game-architecture`
**Occlusion culling** — Skipping objects hidden behind other geometry. — see: `mobile-performance`
**Offline progress** — Granting or simulating progress while the app is closed; check it for fairness and exploits. — see: `progression-difficulty`
**Overdraw** — Pixels shaded more than once in a frame; a fill-rate cost on mobile GPUs. — see: `mobile-performance`

## P

**Parallax** — Layers moving at different speeds to suggest depth; a cheap 2D depth cue. — see: `art-direction`
**Particle system** — Emitter-driven effects; cap particle counts and prefer sprite sheets on mobile. — see: `technical-art`
**Pathfinding (A*)** — Graph search with a heuristic that finds shortest paths on grids or navmeshes. — see: `gameplay-programming`
**Physics step** — Fixed-rate physics update, kept separate from render frame rate. — see: `game-architecture`
**Pity timer** — Guarantee that raises reward odds after a streak without the reward; disclose it where regulated. — see: `monetization`
**Playtest** — Observed play by target players against a stated question; among the most valuable tests in development. — see: `qa-testing`
**Presentation layer** — Code that displays simulation state (animation, UI, audio), kept separate from the rules. — see: `game-architecture`
**Procedural generation (PCG)** — Algorithmic content creation from rules and seeds; design the rules, then curate the output. — see: `procedural-generation`
**Profiler** — Tool that measures CPU, GPU and memory per frame; measure before optimizing. — see: `mobile-performance`
**Prototype** — Throwaway build that answers one question; scope it tightly. — see: `production`
**Pseudo-random distribution** — Random selection with bounded streaks, such as a shuffle bag, which often feels fairer than independent rolls. — see: `procedural-generation`

## Q

**Quality gate** — Explicit pass/fail criteria that a build or milestone must meet before moving on. — see: `production`
**Quantization (network)** — Reducing numeric precision of replicated values to save bandwidth. — see: `multiplayer-backend`

## R

**Regression test** — Test that reproduces a fixed bug so it cannot return unnoticed. — see: `qa-testing`
**Remote config** — Server-controlled parameters fetched at launch and changed without a store update. — see: `liveops`
**Render pipeline** — Sequence of GPU passes that produces a frame; choose the lightweight pipeline for mobile targets. — see: `engine-unity`
**Replay** — Recording of inputs or states to reproduce a session; cheap when simulation is deterministic. — see: `game-architecture`
**Retention (D1, D7, D30)** — Share of a cohort still active on day N after install; a core health metric for mobile games. — see: `player-analytics`
**RNG seeding** — Setting a random generator's seed so runs and tests reproduce exactly. — see: `game-architecture`
**Rollback netcode** — Predicts ahead, then rewinds and resimulates when late inputs arrive; common in fighting games. — see: `multiplayer-backend`
**Root motion** — Animation drives character movement so feet do not slide against the ground. — see: `technical-art`
**Rubber banding** — Adjusting AI or player speed to keep races close; a powerful tool that must be a deliberate design choice. — see: `progression-difficulty`

## S

**Save migration** — Upgrading saved data between versions; version every save from day one. — see: `game-architecture`
**Scene graph** — Tree of nodes and transforms in which child transforms are relative to their parent. — see: `engine-godot`
**ScriptableObject** — Unity asset type that holds data, used for configuration and tuning values. — see: `engine-unity`
**Shader** — Program that runs on the GPU per vertex or per pixel; the main source of visual cost. — see: `technical-art`
**Shader variant** — Compiled permutation of a shader from keyword combinations; uncontrolled counts inflate build size. — see: `technical-art`
**Signal (event)** — Godot's decoupled notification mechanism between nodes. — see: `engine-godot`
**Skinning** — Deforming a mesh by bone transforms each frame; cost grows with bone and vertex counts. — see: `technical-art`
**Soak test** — Long run under realistic load to find leaks, drift and slow degradation. — see: `qa-testing`
**Spatial hash** — Grid bucketing of objects so neighbour queries check only nearby cells. — see: `game-architecture`
**State machine** — See Finite state machine. — see: `gameplay-programming`
**Steering behaviour** — Local rules such as seek, avoid and flock that produce natural agent movement. — see: `gameplay-programming`
**Streaming (asset or level)** — Loading content in the background as the player approaches it. — see: `mobile-performance`
**System (ECS)** — Code that processes all entities holding a given set of components each frame. — see: `game-architecture`

## T

**Tick** — One fixed simulation step; networking and gameplay timing are often counted in ticks. — see: `game-architecture`
**Tile map** — Grid of tiles that reference art; an efficient way to author 2D worlds. — see: `level-design`
**Time slicing** — Spreading expensive work across several frames so no single frame spikes. — see: `mobile-performance`
**Trace (telemetry event)** — Structured event describing player actions; design the event schema before writing code. — see: `player-analytics`
**Tween** — Engine-driven interpolation of a value over time using an easing curve. — see: `game-feel`

## U

**Undo/redo (command pattern)** — Actions stored as reversible commands; needed for level editors and puzzle tools. — see: `game-architecture`
**Unit test** — Test of one function or class in isolation; fast and deterministic. — see: `qa-testing`
**UV mapping** — Mapping of a 3D surface onto 2D texture coordinates. — see: `technical-art`

## V

**Vertex count** — Number of vertices sent to the GPU; set a budget per object and per scene. — see: `technical-art`
**Vsync** — Synchronizing buffer swaps with display refresh; removes tearing at the cost of added latency. — see: `mobile-performance`

## W

**Weighted random** — Selection by probability weight; the building block of loot tables and spawns. — see: `economy-design`
**Working set** — Memory actively used at a given time; keep it under device limits. — see: `mobile-performance`

## Z

**Zero-allocation path** — Code path that allocates no memory per call, avoiding garbage collection spikes. — see: `mobile-performance`
**Z-fighting** — Flicker where two coplanar surfaces compete for depth; fix with offsets or depth precision. — see: `technical-art`
