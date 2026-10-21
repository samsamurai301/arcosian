# Design Diagnostic Checklist

An original set of 130 diagnostic questions for reviewing a game design at any stage — concept, prototype, vertical slice, soft launch or live — grouped into eleven areas: player, loop, decisions, feedback, progression, economy, social, UX, art and audio, mobile fit, and ethics. Each question comes with what a bad answer usually signals and which skill or reference to consult next. It works as a review deck for the `design-review` workflow, a self-check for `arcosian:game-designer` before handing off a spec, and a refutation script for `arcosian:critic`. Start with the critical-20 fast pass; run the full list at stage gates. Answer with evidence (telemetry, playtest reports, simulation output), not opinion.

## Contents

1. How to use this checklist
2. Critical-20 fast pass
3. Player (P01–P12)
4. Loop (L01–L12)
5. Decisions (D01–D12)
6. Feedback (F01–F12)
7. Progression (R01–R12)
8. Economy (E01–E12)
9. Social (S01–S11)
10. UX (U01–U12)
11. Art and audio (A01–A11)
12. Mobile fit (M01–M12)
13. Ethics (X01–X12)
14. Recording findings
15. Stage-appropriate subsets

---

## 1. How to use this checklist

**Rating.** For each question record one of:
- **Green** — answered with evidence, no action needed.
- **Amber** — answer is plausible but unverified, or a minor problem exists; schedule a test or fix.
- **Red** — no answer, or the answer shows a real problem; must be resolved before the next stage gate.
- **N/A** — does not apply (state why, e.g., "no social features by design").

**Evidence rule.** A Green needs a pointer: a playtest report (`.gamestudio/playtests/`), a simulation output (`.gamestudio/economy/`), telemetry, a solver result, or a spec section. "We think so" is Amber at best.

**Blocking rule.** Any Red in **Ethics** blocks release-oriented stages regardless of other scores. Any Red in **Loop** blocks moving beyond `prototype`. Reds elsewhere must have an owner and a date.

**Consult column.** Skill names refer to sibling codex skills (e.g., `economy-design`); file names without a path refer to this skill's own references in `skills/design-theory/references/`.

---

## 2. Critical-20 fast pass

Use these when you have 15 minutes. A design that is Green on all 20 is probably worth deeper review; three or more Reds usually mean returning to prototyping.

| Order | ID | Short form |
|---|---|---|
| 1 | P01 | Target player named, not "everyone" |
| 2 | P03 | Player fantasy in one sentence |
| 3 | L01 | Core loop in one sentence (act → reward → invest) |
| 4 | L02 | Core verb is fun as a toy |
| 5 | L03 | Micro-loop survives 20 repetitions |
| 6 | L05 | Every meta loop feeds the core |
| 7 | L09 | Loops survive removing random rewards |
| 8 | D01 | Frequent decisions have trade-offs |
| 9 | D02 | No dominant option |
| 10 | F02 | Players can say why they failed |
| 11 | R02 | First difficulty spike placed after habit forms |
| 12 | R06 | A stuck player has a way forward |
| 13 | E03 | Non-spenders neither hoard nor starve |
| 14 | S01 | Solo players can progress fully |
| 15 | U01 | Core loop reachable in 1–2 taps |
| 16 | U02 | At most one popup at session start |
| 17 | M01 | Meaningful session under 90 seconds |
| 18 | M02 | Survives interruption at any moment |
| 19 | X01 | Odds disclosed and tails capped for paid randomness |
| 20 | X02 | No purchase prompts at frustration peaks |

---

## 3. Player

| ID | Question | A bad answer signals | Consult |
|---|---|---|---|
| P01 | Can you name the target player segment in one sentence without saying "everyone" or "casual and hardcore"? | No focus; features will serve incompatible audiences and none well | `market-intel`, `player-psychology` |
| P02 | What are that segment's top three motivations, and which loop serves each one every session? | A motivation with no loop is a retention gap; a loop with no motivation is a cost centre | `fun-and-motivation-design.md`, `player-psychology` |
| P03 | What is the player fantasy, phrased from the player's side ("I get to …")? | A feature list instead of a fantasy; weak marketing hook and weak tonal direction | `narrative-design`, `foundational-frameworks.md` |
| P04 | Where and when does this player play (commute, queue, sofa, bed), and does session design match that context? | Sessions or controls designed for a desk, not a phone in one hand | `mobile-ux`, `core-loops-and-structure.md` |
| P05 | What is the player thinking about an hour after closing the app? | Nothing: no unresolved goal, no anticipation, weak return pull | `core-loops-and-structure.md` (exit hooks) |
| P06 | Which games does this player already play, and what will they stop playing to make room for ours? | No displacement story; the game may be "fine" but unnecessary | `market-intel`, `game-case-studies` |
| P07 | What would make this player uninstall in the first ten minutes? | Unknown failure points; FTUE not observed with real target players | `player-analytics`, `prototyping-and-iteration.md` |
| P08 | After one session, can a player describe the game to a friend in one sentence? | Unclear identity; weak word-of-mouth and store conversion | `marketing-ua`, `analogy-engine` |
| P09 | Which basic need (competence, autonomy, relatedness) is weakest, and is that deliberate? | Unexamined need gaps that show up later as churn | `foundational-frameworks.md` (SDT) |
| P10 | What must a player learn in session 1, and does the total fit a small complexity budget? | Front-loaded learning; overwhelmed first sessions | `decisions-and-depth.md` (complexity budget), `mobile-ux` |
| P11 | What happens when a player returns after a week or a month away? | Returning players face a wall of popups, lost streaks or impossible catch-up | `liveops`, `progression-difficulty` |
| P12 | Has the design considered motor, visual, hearing and cognitive accessibility? | Excludes players and fails platform expectations; retrofitting costs more | `accessibility-localization` |

---

## 4. Loop

| ID | Question | A bad answer signals | Consult |
|---|---|---|---|
| L01 | Can the core loop be written in one sentence as act → reward → invest? | Tangled or missing loop; the team does not share a model of the game | `core-loops-and-structure.md` |
| L02 | Is the core verb enjoyable as a toy, with no goals attached? | All engagement depends on extrinsic structure; fragile retention | `prototyping-and-iteration.md` (toy-first), `game-feel` |
| L03 | Does the micro-loop stay engaging for 20 consecutive repetitions with no meta or rewards? | The core is not fun; meta will only delay churn | `core-loops-and-structure.md` (micro-loop test) |
| L04 | What makes cycle 30 different from cycle 3? | No variation source; mastery horizon of minutes | `procedural-generation`, `level-design` |
| L05 | Does every meta loop return power, variety, goals or meaning to the core, with a named anchor step? | Disconnected meta; currencies and screens with no reason to exist | `core-loops-and-structure.md` |
| L06 | Does each slower loop contain roughly 3–10 cycles of the faster loop beneath it? | Sessions too fragile (1 cycle) or too grindy (dozens of cycles per achievement) | `core-loops-and-structure.md` (time-scale ladder) |
| L07 | Where are the natural stopping points, and are they 2–5 minutes apart? | Players forced to quit mid-action, or never offered a clean exit | `core-loops-and-structure.md` (session design) |
| L08 | What is the exit hook at the end of a typical session? | No reason to return tomorrow beyond habit | `core-loops-and-structure.md` |
| L09 | If every random reward were removed, would each loop still be worth doing? | Loops are themed slot machines; ethical and retention risk | `fun-and-motivation-design.md`, `legal-ethics` |
| L10 | What share of playtime comes from repeatable loops vs consumed content, and can production sustain the content share? | Content burn will outrun the team; churn spikes after each update | `core-loops-and-structure.md` (content burn), `production` |
| L11 | Does every daily or weekly loop have enough content or systemic variety to feed it? | Empty dailies that become chores | `liveops` |
| L12 | Which loop would you cut first if forced, and why has it not been cut? | Scope carrying loops that do not earn their cost | `production`, `prototyping-and-iteration.md` (pillars) |

---

## 5. Decisions

| ID | Question | A bad answer signals | Consult |
|---|---|---|---|
| D01 | What are the three most frequent decisions, and does each involve a real trade-off? | Obvious choices; play degrades to execution or clicking through | `decisions-and-depth.md` |
| D02 | Is any option chosen by nearly everyone in nearly every situation? | Dominant strategy; dead options; stale meta | `decisions-and-depth.md` (detection), `balance` |
| D03 | Is any option worse than another in every situation? | Trap options that punish uninformed players | `decisions-and-depth.md` |
| D04 | At decision time, can players see enough to reason about outcomes? | Blind choices that feel random | `decisions-and-depth.md` (information structures), `mobile-ux` |
| D05 | Do important decisions have consequences that persist beyond the moment? | Irrelevant choices; low investment | `decisions-and-depth.md` |
| D06 | How many options appear per decision, and are more than four ever shown without grouping? | Overload on small screens; slow, anxious decisions | `mobile-ux` |
| D07 | Is randomness placed mostly before decisions (input) rather than after (output) where stakes are high? | Good play overridden by dice; perceived unfairness | `decisions-and-depth.md` (skill vs luck) |
| D08 | In a strong-bot vs random-bot test, how often does the strong bot win? | Near 50%: luck-dominated or shallow; near 100% in casual modes: possibly too punishing for novices | `decisions-and-depth.md`, `qa-testing` |
| D09 | For every strong threat, what are its hard and soft counters, and is it telegraphed in time to respond on a phone? | Races without counterplay; frustration from unreadable threats | `decisions-and-depth.md` (counterplay) |
| D10 | Do units or options differ in kind (roles, properties) or only in numbers? | Stat-sheet collapse; one best ratio wins | `decisions-and-depth.md` (orthogonal differentiation), `mechanics-codex` |
| D11 | How many distinct strategies remain viable at high skill? | One: solved game; players leave once they find it | `decisions-and-depth.md` (depth proxies) |
| D12 | Does each new rule interact with several existing rules? | Complexity without depth; feature bloat | `decisions-and-depth.md` (emergence), `foundational-frameworks.md` (Sylvester) |

---

## 6. Feedback

| ID | Question | A bad answer signals | Consult |
|---|---|---|---|
| F01 | Can a player tell within about a second what their last action did? | Undiscernable actions; play feels like pressing dead buttons | `game-feel`, `foundational-frameworks.md` (meaningful play) |
| F02 | After failing, can the player state why? | Failure reads as noise; competence need unmet; churn after losses | `fun-and-motivation-design.md` (failure design) |
| F03 | Is feedback intensity proportional to importance (small actions small, big moments big)? | Everything shouts, so nothing stands out; or key moments fall flat | `game-feel` |
| F04 | Is input-to-response latency imperceptible on the low-tier reference device? | Mushy controls; skill expression blocked | `game-feel`, `mobile-performance` |
| F05 | Does feedback ever mislead (inflated praise, manufactured near-misses)? | Trust erosion; possible manipulation | `fun-and-motivation-design.md` (ethics) |
| F06 | Are success and failure distinguishable with sound off and without relying on colour alone? | Muted and colour-blind players miss outcomes | `accessibility-localization`, `audio-direction` |
| F07 | Do haptics mark key moments without constant buzzing? | Haptic fatigue or missed tactile reinforcement | `game-feel` |
| F08 | Do effects appear near the action that caused them, at the time it happened? | Players cannot connect cause and effect | `game-feel`, `mobile-ux` |
| F09 | Is progress toward the current goal visible throughout play? | Players lose track of what they are doing | `mobile-ux` |
| F10 | Are numbers legible at a glance (size, contrast, abbreviation for large values)? | Misread rewards and states; incremental games especially suffer | `mobile-ux`, `art-direction` |
| F11 | Do rare achievements get a celebration distinct from routine ones? | Rare moments feel ordinary; flattened emotional peaks | `game-feel`, `core-loops-and-structure.md` (peak–end) |
| F12 | Is the loss/failure feedback designed with the same care as success? | Harsh or confusing failure screens drive quitting | `fun-and-motivation-design.md` |

---

## 7. Progression

| ID | Question | A bad answer signals | Consult |
|---|---|---|---|
| R01 | What does the difficulty curve look like over the first 30 levels or sessions, and where are the spikes? | Unplanned curve; spikes discovered by players, not designers | `progression-difficulty` |
| R02 | Is the first real difficulty spike placed after players have formed a habit? | Early walls cause first-week churn | `progression-difficulty`, `core-loops-and-structure.md` |
| R03 | Is each new element introduced via teach → test → twist → reward? | Mechanics dumped on players; confusion and unfair-feeling failures | `core-loops-and-structure.md` (kishōtenketsu), `level-design` |
| R04 | How often does something genuinely new appear in the first week? | Novelty drought; boredom before the meta pulls | `fun-and-motivation-design.md` (novelty schedule) |
| R05 | How much of clear rate depends on skill versus accumulated power? | All power: hollow; all skill: walls for weaker players | `fun-and-motivation-design.md` (growth types), `progression-difficulty` |
| R06 | What happens to a player stuck on one level for three sessions? | No way forward except paying or quitting | `progression-difficulty`, `monetization` |
| R07 | Does the progression pace match content production capacity? | Players hit the end of content; or content is gated artificially | `production`, `core-loops-and-structure.md` (content burn) |
| R08 | Does the first session reveal what the player is building toward? | No long-term motivation formed before players leave | `core-loops-and-structure.md` (interest curves) |
| R09 | Is a long-term goal visible from early on (map, collection, endgame tease)? | Short horizon; players see no future in the game | `progression-difficulty` |
| R10 | If dynamic difficulty exists, is it fair, limited to safety nets, and excluded from competitive modes? | Players feel the game is rigged; skill feels pointless | `progression-difficulty`, `foundational-frameworks.md` (flow) |
| R11 | Does power growth outpace content in ways that trivialise old content unintentionally? | Power creep; meaningless upgrades | `economy-design`, `progression-difficulty` |
| R12 | What do players do after finishing the content (endgame, prestige, mastery modes)? | Engaged players churn at content end | `liveops`, `core-loops-and-structure.md` |

---

## 8. Economy

| ID | Question | A bad answer signals | Consult |
|---|---|---|---|
| E01 | Can you list every currency with its sources and sinks? | Unmodelled economy; surprises at launch | `economy-design` |
| E02 | Does each currency do something no other currency can? | Currency bloat; confused players; UI clutter | `economy-design` |
| E03 | In simulation, do median non-spending players neither hoard nor starve? | Nothing worth buying (hoarding) or progress blocked (starvation) | `economy-design`, `${CLAUDE_PLUGIN_ROOT}/scripts/economy_sim.py` |
| E04 | What are the positive feedback loops, and what stops each? | Runaway inflation or snowballing advantage | `foundational-frameworks.md` (Adams & Dormans) |
| E05 | How long do non-spenders take to reach key milestones compared with spenders? | Pay-to-progress gaps that feel unfair, or no reason to pay at all | `economy-design`, `monetization` |
| E06 | Are there exploit loops (converter arbitrage, infinite generation, trade abuse)? | Economy collapse once players find them | `economy-design`, `qa-testing` |
| E07 | Is the real-money value of premium currency understandable? | Opaque pricing; distrust; regulatory risk | `monetization`, `legal-ethics` |
| E08 | Do sinks feel like meaningful choices rather than taxes? | Resentment; spending without satisfaction | `economy-design` |
| E09 | How do event rewards affect inflation in the main economy? | Events break long-term balance | `liveops`, `economy-design` |
| E10 | Are caps visible and justified to players? | Wasted earnings feel like theft | `economy-design`, `mobile-ux` |
| E11 | Can any purchase buy a competitive advantage in PvP? | Pay-to-win perception; competitive players leave | `monetization`, `decisions-and-depth.md` |
| E12 | Is the economy stored in the ontology format and re-simulated after every change? | Changes made on intuition; regressions go unnoticed | `game-ontology`, `economy-design` |

---

## 9. Social

| ID | Question | A bad answer signals | Consult |
|---|---|---|---|
| S01 | Can a player with no friends in the game progress fully? | Largest segment excluded; social features become a wall | `core-loops-and-structure.md` (social loops) |
| S02 | Do social interactions mostly help others rather than harm them? | Negative-sum interactions drive away non-competitive players | `fun-and-motivation-design.md` (relatedness) |
| S03 | Is there a free-rider problem in team goals, and how is individual contribution rewarded? | Team resentment; contributors burn out | `decisions-and-depth.md` (social dilemmas) |
| S04 | How are harassment and toxic behaviour prevented, reported and handled? | Community harm; store and legal exposure | `legal-ethics`, `multiplayer-backend` |
| S05 | Do social features protect minors and comply with regional rules? | Legal risk; platform rejection | `legal-ethics` |
| S06 | Is there a positive reason to engage with others at least weekly? | Social features exist but nobody uses them | `liveops` |
| S07 | Does losing a PvP match or being raided feel recoverable? | Victims churn; ecosystem collapse | `foundational-frameworks.md` (Bartle ecosystem), `economy-design` |
| S08 | Is matchmaking quality measured (rating spread, wait time, stomp rate)? | Unfair matches attributed to the game's design | `multiplayer-backend`, `player-analytics` |
| S09 | Are invite and referral mechanics non-spammy and within platform policy? | Store policy violations; damaged reputation | `store-release`, `marketing-ua` |
| S10 | Do team obligations or penalties create guilt loops? | Play driven by obligation; resentment and burnout | `fun-and-motivation-design.md` (autonomy) |
| S11 | Can players express themselves to others (profiles, visits, emotes)? | Expression motivation unserved; low social pull | `fun-and-motivation-design.md` |

---

## 10. UX

| ID | Question | A bad answer signals | Consult |
|---|---|---|---|
| U01 | Can a returning player reach the core loop within one or two taps of launch? | Friction before fun every session | `mobile-ux` |
| U02 | How many popups appear at session start? | Popup chains breaking the magic circle and autonomy | `mobile-ux`, `foundational-frameworks.md` (magic circle) |
| U03 | Is every primary action reachable by the thumb in the chosen orientation and grip? | Reach strain; one-handed play impossible | `mobile-ux` |
| U04 | Are touch targets at least platform-recommended sizes (Apple suggests about 44×44 pt; Material Design about 48×48 dp)? | Mis-taps; frustration; accessibility failures | `mobile-ux`, `accessibility-localization` |
| U05 | Does the play-screen HUD show only what the current decision needs? | Attention overload; the board competes with chrome | `mobile-ux`, `foundational-frameworks.md` (Hodent) |
| U06 | Is the tutorial taught by doing, one concept at a time, skippable for returning players? | Text walls; forced tutorials; churn in FTUE | `mobile-ux` |
| U07 | Are rewards and unlocks acknowledged without blocking play? | Interruptions that break flow | `mobile-ux`, `game-feel` |
| U08 | Can players find any feature within about three taps? | Hidden features never used | `mobile-ux` |
| U09 | Does the UI tolerate longer translated strings and right-to-left languages if targeted? | Broken layouts in localization; costly late fixes | `accessibility-localization` |
| U10 | Are errors (network, purchase, save) recoverable with clear, human messages? | Lost purchases and progress; support tickets; bad reviews | `mobile-ux`, `qa-testing` |
| U11 | Does each icon mean the same thing everywhere? | Learned meanings break; confusion | `mobile-ux`, `art-direction` |
| U12 | Do costly or irreversible actions require confirmation or allow undo? | Accidental spends; refund requests; anger | `mobile-ux`, `monetization` |

---

## 11. Art and audio

| ID | Question | A bad answer signals | Consult |
|---|---|---|---|
| A01 | Can the game state be read from a screenshot at thumbnail size? | Readability problems on small screens and in store listings | `art-direction` |
| A02 | Does a single screenshot or the icon communicate genre and fantasy? | Weak store conversion; mismatched audience expectations | `art-direction`, `store-release` |
| A03 | Are gameplay elements visually distinct from decoration (silhouette, value contrast)? | Players miss threats and interactables | `art-direction`, `level-design` |
| A04 | Is colour paired with shape or icon wherever it carries meaning? | Colour-blind players cannot play | `accessibility-localization`, `art-direction` |
| A05 | Is the game fully playable with sound off? | Many mobile sessions happen muted; information lost | `audio-direction`, `mobile-ux` |
| A06 | Does each important event have a distinct sound signature? | Audio mush; players cannot learn by ear | `audio-direction` |
| A07 | Does music intensity follow the gameplay intensity curve? | Emotional mismatch; flat pacing | `audio-direction`, `core-loops-and-structure.md` (pacing) |
| A08 | Is the art pipeline repeatable at production scale (style lock, references, approvals)? | Style drift; inconsistent assets; rework | `ai-asset-pipeline`, `art-direction` |
| A09 | Do visual effects ever obscure gameplay information on small screens? | Juice hurting readability | `technical-art`, `game-feel` |
| A10 | Are all assets licensed for commercial use with provenance recorded in the manifest? | Legal exposure; takedown risk | `ai-asset-pipeline`, `ai-audio-pipeline`, `legal-ethics` |
| A11 | Do art, audio, copy and mechanics express the same tone? | Identity confusion (e.g., cosy visuals on a punishing grind) | `foundational-frameworks.md` (tetrad), `narrative-design` |

---

## 12. Mobile fit

| ID | Question | A bad answer signals | Consult |
|---|---|---|---|
| M01 | Can a meaningful session (start, achieve, stop) be completed in under 90 seconds? | The game demands time phones rarely give | `core-loops-and-structure.md` (session design) |
| M02 | Does the game survive interruption at any moment (call, app switch, OS kill) without losing progress? | Lost progress; one-star reviews | `game-architecture`, `qa-testing` |
| M03 | Is it playable one-handed in the target orientation? | Excludes standing/commuting play | `mobile-ux` |
| M04 | Does it hold its frame budget on the low-tier device over a 30-minute session without thermal degradation? | Stutter and heat in long sessions | `mobile-performance` |
| M05 | Is the install size within budget, with later content delivered on demand? | Download abandonment; storage complaints | `mobile-performance`, `store-release` |
| M06 | Is cold start within the contract's `cold_start_sec` budget? | Players bounce before playing | `mobile-performance` |
| M07 | Does the game work offline or degrade gracefully on poor connections? | Unplayable on trains and in low-coverage regions | `game-architecture`, `multiplayer-backend` |
| M08 | Are notifications opt-in, useful and infrequent? | Notification fatigue; permission denial; uninstalls | `liveops`, `mobile-ux` |
| M09 | Is battery drain reasonable (frame caps in menus, no idle rendering)? | Players stop playing to save battery | `mobile-performance` |
| M10 | Does layout respect safe areas, notches, cut-outs and varied aspect ratios? | UI hidden under hardware features | `mobile-ux` |
| M11 | Do thumbs hide critical information during play? | Players fail because they cannot see | `mobile-ux`, `level-design` |
| M12 | Does the game respect system settings (silent mode, reduced motion, text size)? | Accessibility and comfort failures | `accessibility-localization` |

---

## 13. Ethics

| ID | Question | A bad answer signals | Consult |
|---|---|---|---|
| X01 | Are odds disclosed for every paid random reward, with pity or guarantees capping the tail? | Regulatory and store risk; exploitation of the unlucky tail | `legal-ethics`, `monetization` |
| X02 | Is any purchase prompt triggered by near-misses, loss streaks or frustration peaks? | Manipulative monetization | `fun-and-motivation-design.md` (ethics), `monetization` |
| X03 | Can players identified as minors buy random rewards? | Legal exposure in multiple regions; harm to minors | `legal-ethics` |
| X04 | Does any timer, streak or absence mechanic remove progress the player earned? | Loss-aversion pressure; coercive retention | `fun-and-motivation-design.md` |
| X05 | Are there fake scarcity signals (resetting countdowns, invented stock limits)? | Deceptive design; consumer-protection risk | `legal-ethics` |
| X06 | Can the full core game be progressed without paying? | Paywall disguised as free-to-play | `monetization` |
| X07 | Do ads ever interrupt active play, or are all ads opt-in or placed at natural breaks? | Broken magic circle; retention loss | `monetization` |
| X08 | Can players see their spending history and set limits? | Unaware overspending | `monetization`, `legal-ethics` |
| X09 | Would the design survive being explained to a regulator, a journalist and a parent? | Hidden intent the team would not defend publicly | `legal-ethics` |
| X10 | Is personal data limited to what the game needs, with consent and clear disclosures? | Privacy violations; store rejection | `legal-ethics`, `store-release` |
| X11 | Are AI-generated assets disclosed where required and correctly licensed? | Store or legal issues; provenance gaps | `ai-asset-pipeline`, `legal-ethics` |
| X12 | Would players, thinking calmly afterwards, be glad each retention mechanic exists? | Compulsion over engagement; long-term trust erosion | `core-loops-and-structure.md` (engagement vs compulsion) |

---

## 14. Recording findings

Write findings so they can be routed and tracked. Suggested record (fits `.gamestudio/reports/` review files and the `design-review` workflow):

```json
{
  "id": "D02",
  "area": "decisions",
  "rating": "red",
  "answer": "Multishot picked 78% when offered; +13 pt run win-rate delta",
  "evidence": [".gamestudio/reports/softlaunch-week2-cards.csv"],
  "action": "Add diminishing returns to Multishot stacking; re-run pick/win analysis",
  "owner": "systems-designer",
  "consult": ["decisions-and-depth.md", "balance"],
  "due": "2026-11-02"
}
```

**Summary table for a review.**

| Area | Green | Amber | Red | N/A | Top issue |
|---|---|---|---|---|---|
| Player | | | | | |
| Loop | | | | | |
| Decisions | | | | | |
| Feedback | | | | | |
| Progression | | | | | |
| Economy | | | | | |
| Social | | | | | |
| UX | | | | | |
| Art and audio | | | | | |
| Mobile fit | | | | | |
| Ethics | | | | | |

Route findings: design/loop/decisions → `arcosian:game-designer`; economy/progression → `arcosian:systems-designer`; UX → `arcosian:ux-designer`; art/audio → `arcosian:art-director` / `arcosian:audio-director`; mobile fit → `arcosian:performance-engineer` / `arcosian:lead-engineer`; ethics → `arcosian:compliance-officer` and `arcosian:monetization-designer`; overall verdict → `arcosian:principal`.

---

## 15. Stage-appropriate subsets

| Stage (config `tier`) | Run | Why |
|---|---|---|
| Concept | P01–P08, L01, L02, D01, X09 | Validate audience, fantasy and core idea before building |
| `prototype` | Critical-20 + all Loop + D01–D08 + F01–F02 | The core loop and decisions are the only things that matter yet |
| `slice` | Full checklist except live-only items (E09, S08, R12) | Quality bar across disciplines |
| `soft_launch` | Full checklist with telemetry evidence | Replace estimates with data |
| `live` | Economy, Progression, Social, Ethics each update; full list each season | Drift detection as content and offers accumulate |
