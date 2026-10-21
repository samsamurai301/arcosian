---
name: game-glossary
description: Defines about 500 game development, design, engineering, art, audio, live-ops, monetization, store and production terms, with a top-50 summary and a file index per domain. Use when someone asks what a game term means, uses jargon such as FTUE, ARPDAU, rollback netcode, LUFS or gacha, or needs shared vocabulary before a design doc, review or KPI definition.
---

# Game Glossary

## What this skill gives you

- One-line definitions for about 500 game-industry terms, each pointed at the codex skill that goes deeper.
- A top-50 list for terms that come up on almost every project.
- A domain index, so you open one reference file instead of scanning all three.
- Shared vocabulary for design docs, code reviews, KPI definitions and sprint tickets.
- Practitioner shorthand, not legal advice, platform-policy rulings or current market benchmarks.

## How to use this glossary

1. Check the top-50 list below first. If the term is there, the definition is enough for most conversations.
2. If it is not, identify the domain in the index and open that file. Entries are alphabetical. Search with `grep -n "^\*\*Term" references/<file>.md`.
3. Follow each `see:` pointer to the named codex skill when you need procedures, not definitions.
4. When two terms overlap (ARPU, ARPPU, ARPDAU), pick the one whose population and time window match your question, and state the denominator in writing.
5. Treat numbers inside entries as formulas or illustrations. Verify platform rules, fees, policy text and market figures against current official documentation before relying on them.

Checklist for pinning a term in a document:

- [ ] Write the term, then its formula or unit in brackets.
- [ ] Name the source system (analytics tool, store console, engine profiler).
- [ ] State the population (all users, payers, a cohort) and the time window.
- [ ] Note which team owns the definition, so the number is reproducible.

## Top 50 terms

**Core loop** — The smallest repeated cycle (act, reward, decide) that produces the game's main feel. — see: `game-ontology`
**Game feel (juice)** — Feedback layer (shake, hit stop, easing, sound) that makes actions read as impactful. — see: `game-feel`
**FTUE (first-time user experience)** — Scripted first session that teaches the core loop with minimal friction. — see: `mobile-ux`
**Difficulty curve** — Planned challenge over time; every spike needs a recovery point. — see: `progression-difficulty`
**Flow** — Mental state where challenge matches skill; a design target that is hard to measure directly. — see: `player-psychology`
**Feedback loop** — Output feeding back into input; positive loops amplify, negative loops stabilize. — see: `economy-design`
**Economy faucet** — Mechanism that adds currency or items to the economy, such as quest rewards. — see: `economy-design`
**Economy sink** — Mechanism that removes currency or items, such as repairs or crafting costs. — see: `economy-design`
**Expected value (EV)** — Probability-weighted average outcome of a random reward. — see: `economy-design`
**Loot table** — Weighted list of drops with probabilities; document expected value and rarity. — see: `economy-design`
**Gacha** — Paid, chance-based reward draw; many jurisdictions require disclosed odds. — see: `legal-ethics`
**Pity timer** — Guaranteed reward after a streak without one; disclose it where regulated. — see: `monetization`
**Dark pattern** — Interface that tricks users into unintended choices; regulators and stores treat many as violations. — see: `legal-ethics`
**Retention (D1, D7, D30)** — Share of a cohort still active on day N after install. — see: `player-analytics`
**Cohort** — Group of users sharing a start date or trait, tracked over time. — see: `player-analytics`
**ARPDAU** — Daily revenue divided by daily active users. — see: `monetization`
**ARPU** — Total revenue divided by all active users in a period. — see: `monetization`
**LTV (lifetime value)** — Expected revenue or margin per user over their whole life. — see: `monetization`
**CAC (customer acquisition cost)** — Acquisition spend divided by new paying users in the same window. — see: `marketing-ua`
**LTV:CAC ratio** — Lifetime value divided by acquisition cost, stated with its payback window. — see: `marketing-ua`
**ROAS (return on ad spend)** — Revenue from ad-acquired users divided by ad spend. — see: `marketing-ua`
**Attribution** — Assigning an install or purchase to the campaign or channel that caused it. — see: `marketing-ua`
**Churn** — Share of users who stop playing or paying in a period. — see: `player-analytics`
**Live event** — Time-limited mode or challenge that changes the experience for a window. — see: `liveops`
**LiveOps calendar** — Scheduled plan of events, offers, content drops and maintenance windows. — see: `liveops`
**Remote config** — Server-controlled parameters that change without a store update. — see: `liveops`
**Feature flag** — Runtime switch that enables or disables a code path without a new build. — see: `liveops`
**Kill switch** — Remote control that disables a feature quickly after an incident. — see: `liveops`
**Soft launch** — Release in a few markets to test retention and cost before a global launch. — see: `store-release`
**Vertical slice** — Polished sample of the core loop and one level that proves quality and direction. — see: `production`
**Milestone** — Dated checkpoint with defined exit criteria. — see: `production`
**Scope creep** — Unplanned growth of features without matching time or budget. — see: `production`
**Quality gate** — Explicit pass or fail criteria a build or milestone must meet before moving on. — see: `production`
**Playtest** — Observed play by target players against a stated question. — see: `qa-testing`
**Authoritative server** — Server simulation is the truth; clients predict locally and reconcile. — see: `multiplayer-backend`
**Client-side prediction** — Client applies its own input immediately, then reconciles to server state. — see: `multiplayer-backend`
**Rollback netcode** — Predicts ahead, then rewinds and resimulates when late inputs arrive. — see: `multiplayer-backend`
**Lockstep** — Every client runs the same deterministic simulation from shared inputs. — see: `multiplayer-backend`
**Determinism** — Same inputs and seed always produce the same state; enables replays and lockstep. — see: `game-architecture`
**Fixed timestep** — Simulation advances in constant steps, independent of render rate. — see: `game-architecture`
**Frame budget** — Target frame time (about 16.7 ms at 60 fps) divided across systems. — see: `mobile-performance`
**Draw call** — One GPU submission; a common mobile bottleneck when counts are high. — see: `mobile-performance`
**Overdraw** — Pixels shaded more than once per frame; a fill-rate cost on mobile GPUs. — see: `mobile-performance`
**Object pooling** — Reusing pre-allocated objects instead of creating and destroying them. — see: `mobile-performance`
**Garbage collection (GC) spike** — Frame stall when a managed runtime collects memory; avoid per-frame allocation. — see: `mobile-performance`
**ECS (entity-component-system)** — Architecture separating entities, data components and behaviour systems. — see: `game-architecture`
**Behavior tree** — Tree of selectors, sequences and decorators that picks AI actions each tick. — see: `gameplay-programming`
**Procedural generation (PCG)** — Algorithmic content built from rules and seeds; design the rules, then curate the output. — see: `procedural-generation`
**Safe area** — Screen region clear of notches, rounded corners and system bars; keep critical UI inside it. — see: `mobile-ux`
**Code signing** — Cryptographic proof of a build's origin and integrity; required to install or submit. — see: `store-release`

## Index of reference files

| File | Domain | Covers | Read when |
|---|---|---|---|
| `references/design-and-tech-terms.md` | Design and engineering | Core loop, game feel, progression and difficulty, AI, networking, rendering and mobile performance, testing, architecture | A design or code discussion uses unfamiliar technical or design vocabulary |
| `references/business-liveops-terms.md` | Business | Monetization and economy, user acquisition and attribution, retention analytics, live ops, store economics, production and planning, market research | A pricing, KPI, forecast, live-ops or planning term is unclear |
| `references/art-audio-platform-terms.md` | Art, audio and platform | Art direction and rendering art, audio production and implementation, mobile, PC and console platform and store terms | An art brief, audio spec, build or store submission uses unfamiliar terms |

Each reference file holds one entry per line, in the form **Term** — definition — see: skill, grouped alphabetically with a contents list at the top.

## Related skills

- `game-ontology`: shared schema for the parts of a game, which many glossary terms map onto.
- `design-theory`: the vocabulary of rules, decisions and player agency in depth.
- `economy-design`: faucets, sinks, currencies and reward math behind the economy terms.
- `monetization`: pricing, offers, paywalls and the ethics boundary for monetization terms.
- `liveops`: calendars, segments, remote config and event operations.
- `mobile-performance`: budgets, profiling and frame-time vocabulary in practice.
- `legal-ethics`: loot-box, age, consent and store-policy terms with their legal context.
