# Narrative, Rhythm, Educational, Kids, Fitness and Cozy Playbooks

This file covers six genres where success depends on something other than combat or competition: story, music, learning, child safety, physical movement, and comfort. The playbooks are interactive stories and visual novels, rhythm, educational, kids (under COPPA constraints), fitness and location-based games, and cozy games. All six use the shared 14-part template. Section 0 collects the cross-cutting foundations:

- branching-narrative structure and how to verify it
- audio timing and latency for rhythm games
- the compliance stack for children and minors
- location and health data privacy

Agent-buildability is uneven. Branching narrative and cozy systems are deterministic and verifiable, and they suit a style-locked asset pipeline (4/5). Rhythm, educational and kids titles are buildable, but each has a human gate that can't be automated: device latency, pedagogical correctness and child usability (3/5). Location-based games need real-world testing, so they score 2/5. Volatile facts (COPPA, age assurance, music licensing) are dated and sourced at the end.

## Contents

| § | Playbook | Session profile (estimate) | Primary monetization | Agent-buildability | First project for an agent pipeline? |
|---|---|---|---|---|---|
| 0 | [Shared foundations](#0-shared-foundations) | — | — | — | Read first |
| 1 | [Interactive stories / visual novels](#1-interactive-stories--visual-novels) | 5–15 min chapters | Premium choices, tickets, VIP, premium | 4/5 | Yes, with human editorial |
| 2 | [Rhythm](#2-rhythm) | 1.5–3 min songs, 10–30 min sessions | Song packs, subscription, ads, idol gacha | 3/5 | Yes, with owned or licensed music |
| 3 | [Educational](#3-educational) | 5–15 min daily | Subscription, school licences, premium | 3/5 | Yes, with an SME reviewer |
| 4 | [Kids (COPPA)](#4-kids-coppa-constraints) | 5–20 min, parent-managed | Premium, subscription, unlock packs | 3/5 | Yes, with compliance review |
| 5 | [Fitness / location-based](#5-fitness-and-location-based) | Outdoor sessions + passive tracking | Items, event tickets, subscription, sponsored places | 2/5 | No, except a mock-GPS prototype |
| 6 | [Cozy](#6-cozy) | 5–20 min daily ritual | Premium, subscription platforms, cosmetics | 4/5 | Yes |
| — | [Volatile facts](#volatile-facts-as-of-oct-2026--verify-before-relying) | — | — | — | Check before quoting numbers |

## How to use these playbooks

- Set `meta.genre` and `meta.subgenre` to the playbook slug. **Set `meta.target_audience.age_min` first.** If it is below 13, or the audience is mixed, §0.3 applies to every feature, ad SDK and analytics call.
- Copy the loops into `contract.json → loops[]`. Turn the starter list into P0 features with `gs.py feature add`.
- Mechanic category labels used here (narrative & relationship, rhythm & timing, learning & mastery, collection & randomness, progression & upgrade, economy & resources, time & energy, exploration & traversal, social & competition, live events, UX automation) map to `mechanics-codex` via `gs.py kb "<mechanic>" --skill mechanics-codex`.
- KPI statements are qualitative unless sourced. For educational and kids titles, add *outcome* metrics (learning gains, parent trust) next to engagement metrics.

## 0. Shared foundations

### 0.1 Branching narrative: structure and verification
- **Structures.**
  - *Branch-and-bottleneck*: choices diverge, then reconverge at key beats.
  - *Delayed branching*: flags set early, payoff later.
  - *Parallel routes*: romance or character routes.
  - *Quality-based (storylet) narrative*: content unlocks when stat or flag conditions are met.
  Pure binary trees grow as 2^n and are unaffordable. Make choices *feel* consequential through acknowledgement (the story remembers them) and through flags, rather than full divergence.
- **Authoring formats.** ink (inkle, MIT) and Yarn Spinner (MIT) are text-first scripting languages. Agents can write them and linters can check them. Keep scripts as data, not code.
- **Verification an agent can run:**
  - Graph reachability: every node reachable, no dead ends, every ending reachable.
  - Flag consistency: no flag read before it is written on any path.
  - Variable bounds.
  - Localization keys: no missing strings, no text overflow at 130% length.
  - Content-rating scan of every line.
  Model the script as a graph and walk every path up to a depth limit. Use storylet satisfiability checks for quality-based content.
- **LLM-written text.** Research finds LLMs write engaging stories but struggle to keep game mechanics consistent and verifiable over long sessions (volatile facts). Keep mechanics deterministic, use the LLM for drafts and variants, and require human editorial sign-off. Player-facing AI text carries disclosure obligations and review stigma (volatile facts and `legal-ethics`).

### 0.2 Audio timing and latency (rhythm, music-driven games)
- **Judge on the audio clock, not the frame clock.** `error = t_input − (t_note + offset_audio)`. Use input event timestamps, not the frame in which the event was processed.
- **Calibration is mandatory.** Separate audio offset (when the sound is heard) from visual offset (when notes appear). Offer a tap-to-the-beat calibration in the FTUE and settings. Bluetooth headphones add large, variable latency, so detect the route change and prompt recalibration.
- **Android variability.** Output latency differs widely across devices. Use the platform's low-latency audio path (Google's Oboe library on Android) and test on real low-end devices. iOS is generally more consistent (background).
- **Timing windows.** Grade windows in tens of milliseconds (tight "perfect", wider "great/good") are a genre convention. Tune them per difficulty and widen them for accessibility modes.
- **Music assets.** Rhythm charts need a fixed BPM grid. Request steady tempo from generation, verify beats with onset and tempo detection, and keep tempo maps as data. Licensing is the genre's biggest legal trap (volatile facts and `ai-audio-pipeline`).

### 0.3 Children and minors: the compliance stack
Treat this as a design input, not a launch checklist. The `compliance-officer` agent signs off before any build goes to a store.

| Rule set | Applies when | Key design consequences |
|---|---|---|
| COPPA (US) and the amended rule (compliance by Apr 22, 2026) | Child-directed, or actual knowledge of users under 13 | Verifiable parental consent before collecting personal information, including persistent identifiers used for behavioural ads. Separate consent for third-party disclosure. Data retention and security programme. Biometric identifiers (voice) count as personal information |
| Apple Kids Category (guidelines 1.3 / 5.1.4; background) | Listed in Kids Category | No third-party behavioural ads or analytics except narrow exceptions. Parental gate before links, purchases and settings. In the EU, no link-outs in Kids-category or under-13 apps (from Oct 1, 2026) |
| Google Play Families policy (background) | Children in the target audience | Ads only through Families self-certified ad SDKs. No collection of device identifiers from children. Teacher Approved programme for quality |
| GDPR Art. 8 + UK Age-Appropriate Design Code (background) | EU/UK users below the consent age (13–16) | Parental consent below the age threshold. High privacy by default. No nudge techniques. Geolocation off by default |
| US state age-assurance laws | Texas, Utah, Louisiana (2026) | Use Apple's Declared Age Range API and parental-consent flows for downloads and purchases |
| Enforcement precedents | Mixed and teen audiences | FTC v. Epic (2022): chat off by default for kids and teens, no dark-pattern billing. FTC v. Cognosphere (2025): parental consent for under-16 purchases, odds disclosure |

Defaults for any game with minors:
- Neutral age gate.
- No behavioural ads.
- No paid random items.
- No open chat, only pre-set phrases.
- Parental gate on every purchase and outbound link.
- Minimal data collection.
- `compliance_preflight.py` scan of linked SDKs.

### 0.4 Location and health data
- Precise location is sensitive personal data. Ask in context, explain why, offer approximate location where it works, and never sell it or share it for advertising.
- Apple prohibits using HealthKit data for advertising or data mining (guideline 5.1.3; background). Treat Android Health Connect data the same way.
- Safety: speed lockouts (no play while driving), warnings about surroundings, processes for removing points of interest on private, dangerous or sensitive sites, and no spawns at schools or hospitals.
- Map data: OpenStreetMap data is ODbL-licensed, which requires attribution and share-alike for derived databases. Commercial map APIs have their own terms. Check before building a points-of-interest database.

## 1. Interactive stories / visual novels

### Definition and player fantasy
Choice-driven narrative presented as illustrated scenes with character sprites, backgrounds and text, released as episodic chapters. The forms are:
- F2P "story apps": premium choices plus chapter tickets.
- Premium narrative games: *80 Days*, *Florence*, *Reigns*.
- Messaging-format stories: *Lifeline*, *Mystic Messenger*.
- 3D romance gacha: *Love and Deepspace*.

The fantasy is *living a story as the protagonist*: romance, drama, mystery, agency over outcomes, and relationships with characters who remember what you did.

### Core loop
```
open chapter (ticket) → read scenes → choose (free or premium option) → flags, relationship stats
  → cliffhanger ending → wait for ticket regen / watch ad / pay → next chapter
```

### Meta loops
- A library of series ("books") across genres, each with weekly or seasonal chapter drops.
- Relationship meters and romance routes. Multiple endings and an endings gallery.
- Wardrobe and protagonist customization, often sold as premium choices.
- Achievements, choice statistics ("42% chose this").
- UGC story-creation platforms in some titles.

### Session profile
Estimate: 5–15 minute chapters, 1–3 chapters a day when ticket-gated, with binge sessions under subscriptions. Portrait, one-handed, tap to advance. Premium narrative games have longer sittings.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Branching choices with flags and stats | narrative & relationship | Branch-and-bottleneck (§0.1). Acknowledge choices even when paths reconverge |
| Premium choices | economy & resources; narrative & relationship | Sell *extra* (scenes, outfits), never the only good outcome |
| Chapter tickets / keys (energy) | time & energy | Paces content consumption to production speed |
| Relationship meters and routes | narrative & relationship | Visible feedback on choices. Romance routes drive spend |
| Timed choices | narrative & relationship | Tension. Offer an accessibility toggle |
| Swipe-binary decisions (*Reigns*) | narrative & relationship; UX automation | Mobile-native choice grammar with resource balancing |
| Real-time messaging format | narrative & relationship; time & energy | Story unfolds on a real clock with notifications. Intimate but interrupt-driven |

### Monetization model and typical mix
- **F2P story apps**: premium-choice currency, chapter tickets, VIP subscriptions (unlimited tickets or discounts), rewarded ads for tickets.
- **Premium**: one-time price.
- **3D romance gacha**: banner gacha (see `skills/genre-playbooks/references/rpg-gacha.md` §0).

Paywalling "the good ending" draws backlash. Sell flavour and convenience instead.

### KPI expectations
Qualitative, because no sourced ranges were found. Series completion and chapter-to-chapter continuation are the core funnel. Spending clusters around romance and customization moments. Track chapter drop-off by scene, premium-choice take rate, ticket wait abandonment and series cross-reads.

### Retention drivers
Cliffhangers. Character attachment and romance. Weekly chapter cadence. New series launches. Completing all endings. Community discussion of choices.

### Content pipeline and production scope (estimates)
Writing is the bottleneck. Chapters commonly run a few thousand words each, and a season needs 10–20 or more chapters. Each character needs sprites with expression sets, plus backgrounds, music and SFX, translation, and sensitivity and rating review. Rough estimates: a small studio with 5–30 people across writers, artists and producers runs several series. A premium narrative game takes 3–10 people 1–3 years.

### Reference titles
- *80 Days* (inkle, 2014): premium, ink-scripted.
- *Episode* (Pocket Gems, 2014): story app with UGC.
- *Lifeline* (3 Minute Games, 2015): real-time messaging.
- *Choices: Stories You Play* (Pixelberry, 2016).
- *Mystic Messenger* (Cheritz, 2016): messaging otome.
- *Reigns* (Nerial, 2016): swipe decisions.
- *Florence* (Mountains, 2018): interaction-led premium story.
- *Chapters* (Crazy Maple Studio).
- *Love and Deepspace* (Infold/Papergames, 2024): 3D romance gacha.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Characters and writing voice are distinctive | Generic tropes with a flat voice, or AI-sounding prose |
| Choices visibly matter (acknowledgement, flags) | Choices are cosmetic and players notice |
| Premium options add flavour without gating the story | Paywalled good endings and ticket walls mid-scene |
| A steady release cadence | Long gaps between chapters |
| Art is consistent across hundreds of sprites | Off-model characters break immersion |

### Innovation vectors
- LLM-assisted dynamic dialogue inside deterministic story structures.
- Voice-interactive AI-native narrative games (volatile facts).
- AI voice acting with consent and disclosure.
- Messaging and social-feed formats.
- 3D/Live2D-style presentation.
- UGC creation with AI tools.
- Interactive video hybrids.
- Short-form vertical episodes.

### Agent-buildability: 4/5
**Why high:**
- Scripts are text data (ink, Yarn).
- Graph verification proves reachability and flag consistency (§0.1).
- UI is simple and structurally testable.
- 2D sprite and background art fits a style-locked pipeline.

**Why not 5:**
- Writing quality needs human editorial (stigma and disclosure risks for AI prose).
- Multi-character art consistency needs LoRAs: reference-based generation is reliable for only one or two characters at a time (volatile facts).

### Starter feature list (P0 vertical slice: one 3-chapter story)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Script runtime for ink or Yarn (tech) | Loads the story. Save/restore mid-scene reproduces the exact state |
| 2 | Scene presentation: background, sprites, text box, name tag (ui) | Text never overflows at 130% length. Tap-to-advance. Auto/skip/log modes |
| 3 | Choices with flags and relationship stats (narrative) | Flags persist across chapters. Stat bounds enforced |
| 4 | Graph verifier in CI (tech) | Every node and ending reachable. No read-before-write flags. Report saved as `static` evidence |
| 5 | 3 chapters with 2 endings (content) | Branch coverage playthrough visits every choice at least once |
| 6 | Character expression sets, 2 characters × 6 expressions (art) | Style-locked. Passes visual gate for on-model consistency |
| 7 | Chapter tickets with regen (meta) | Regen correct across background and kill. Never interrupts mid-chapter |
| 8 | Premium choice with currency and honest preview (monetization) | Preview shows what is bought. Free path completes the story |
| 9 | Wardrobe customization (meta) | Outfit persists in all later scenes |
| 10 | Music and SFX cues from script tags (audio) | Cues fire on the tagged lines. Loudness within the audio bible target |
| 11 | Localization pipeline (tech) | Keys extracted. Pseudo-locale passes overflow checks |
| 12 | Content rating and AI-disclosure record (release) | Rating questionnaire answers and any AI-content disclosure stored in the contract |

## 2. Rhythm

### Definition and player fantasy
The player hits, holds, flicks and slides notes in time with music. Each song has charts at several difficulties, and timing accuracy decides the score. Variants:
- Tile tappers (*Piano Tiles*, *Magic Tiles*)
- Note highways and judgement lines (*Cytus II*, *Arcaea*, *Project Sekai*)
- Idol rhythm gacha (*BanG Dream!*)
- Rhythm-action hybrids (*Geometry Dash*, *Muse Dash*)
- Hyper-casual music runners (*Tiles Hop*)

The fantasy is *feeling the music through my fingers*: flow, performance mastery, music and idol fandom.

### Core loop
```
pick song (preview) → play chart (≈2–3 min) → judgements, combo, score, grade
  → rewards → unlock songs / difficulties → retry for full combo → pick song
```

### Meta loops
- Song library unlocks through currency, ads, subscription or packs.
- Difficulty ladders, full-combo and all-perfect badges, leaderboards.
- Idol variants: character cards (gacha) that boost scores, story episodes, live events with song-specific rankings.
- User charts and creator content in some titles (music rights permitting).

### Session profile
Estimate: songs of about 1.5–3 minutes, sessions of 10–30 minutes, headphones on. Orientation by variant: portrait for tile tappers, landscape for highways. Wired or low-latency audio is preferred.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Note types: tap, hold, flick, slide | rhythm & timing | Introduce one at a time. Each new type is a difficulty step |
| Timing windows and judgements | rhythm & timing | Judge on the audio clock (§0.2). Windows widen in accessibility modes |
| Latency calibration (audio and visual offsets) | rhythm & timing; UX automation | Mandatory in the FTUE and settings |
| Combo and score multiplier | rhythm & timing; progression & upgrade | Tension and reward for consistency |
| Chart difficulty rating (note density, patterns) | rhythm & timing | Compute notes per second and peak density. Validate against the label |
| Health bar / fail vs no-fail | rhythm & timing | No-fail keeps casual players. Grades reward mastery |
| Idol cards boosting score (gacha) | collection & randomness | Score boosts make leaderboards pay-sensitive. Separate skill and boosted ladders |

**Judgement maths.** For each note, `e = t_input − t_note − offset`. Grade k when `|e| ≤ w_k`. Score = Σ base × weight(grade) × combo multiplier. **Chart validation:** a perfect-input bot proves every chart is physically playable (max simultaneous touches, minimum gap between notes on the same lane, reachable slide paths), and a noisy-timing bot (Gaussian error with σ per persona) estimates clear rates by difficulty for the `playthrough` gate.

### Monetization model and typical mix
- **Premium plus song packs**, as with *Cytus II*.
- **Subscription** for unlimited songs.
- **Ad-supported**: rewarded unlocks, interstitials between songs, never mid-song. Typical of hyper-casual tile games.
- **Idol gacha**: character cards and event passes.

**Music licensing dominates cost and risk.** Commercial songs need both master and publishing rights. Original or commissioned music, or AI music under a licence whose revenue thresholds you track, avoids this (volatile facts).

### KPI expectations
Qualitative, because no sourced ranges were found. Song release cadence drives return visits. FTUE calibration quality strongly affects early churn (a practitioner observation). Track song-start to song-complete rate, retry rate per chart, calibration completion and offset distribution by device model.

### Retention drivers
New songs. Mastery goals (full combo, all perfect). Leaderboards. Idol fandom and events. Personal playlists. Daily song challenges.

### Content pipeline and production scope (estimates)
Per song: rights or creation, 3–5 charts (skilled charters spend hours per chart), background art or video, and preview clips. Rough estimates:
- Indie rhythm game: 2–8 people.
- Idol rhythm gacha: 50+ people with large music, voice and 3D/Live2D budgets.
- Licensed-hit libraries: spending on licences dwarfs development.

### Reference titles
- *Geometry Dash* (RobTop, 2013): rhythm platformer.
- *Deemo* (Rayark, 2013).
- *Piano Tiles 2* (Cheetah Mobile, 2015).
- *Arcaea* (lowiro, 2017).
- *Magic Tiles 3* (Amanotes, 2017).
- *BanG Dream! Girls Band Party!* (Craft Egg/Bushiroad, 2017): idol gacha.
- *Cytus II* (Rayark, 2018): premium plus packs.
- *Tiles Hop* (Amanotes, 2018): hyper-casual runner.
- *Muse Dash* (PeroPeroGames, 2018): rhythm action.
- *Project Sekai: Colorful Stage!* (Colorful Palette/Sega, 2020).

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Timing is tight and fair after calibration, even on budget Android | Latency drift makes perfect play impossible on some devices |
| Charts "feel like the music" (notes follow melody and drums) | Auto-generated charts that ignore musical phrasing |
| A strong music identity and steady releases | Generic library, or licensing gaps leave the catalogue thin |
| Clear difficulty ladder and no-fail options | Difficulty spikes, opaque grading |
| Readable note highway at speed | Visual clutter, poor contrast at high scroll speeds |

### Innovation vectors
- AI-assisted chart drafting from onset detection with human polish.
- Adaptive difficulty charts.
- Rhythm folded into other genres (combat, runners, puzzles).
- Generative or stem-reactive music (experimental real-time music APIs exist; volatile facts).
- Creator ecosystems with rights-cleared music.
- Accessibility rhythm modes (haptic beats, wider windows).

### Agent-buildability: 3/5
**Why mid:**
- The judgement engine is deterministic and unit-testable on timestamps.
- Perfect and noisy bots verify charts.
- Charts can be drafted from audio analysis.
- UI is simple.

**Why not higher:**
- Real-device latency and calibration testing.
- Chart *musicality* needs a human charter's ear.
- Music identity and licensing.
- Haptic and visual feel.

### Starter feature list (P0 vertical slice: 3 songs)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Audio-clock-driven conductor (tech) | Note times derive from audio position. Drift under 5 ms over a 3-minute song in tests |
| 2 | Input timestamping + judgement windows (gameplay) | Synthetic inputs at known offsets produce the expected grades (unit test per window edge) |
| 3 | Calibration screen (audio and visual offsets) (ux) | Offset saved per audio route. Route change prompts recalibration |
| 4 | Note types: tap, hold, flick (gameplay) | Each type passes scripted input tests |
| 5 | Chart format + loader with tempo map (tech) | Charts are data. BPM changes handled |
| 6 | 3 songs × 3 difficulties (content) | Music licence recorded in the manifest. Perfect bot gets a full combo on every chart |
| 7 | Chart validator (tech) | Rejects impossible patterns. Notes-per-second label within the band |
| 8 | Noisy-timing persona bots (tech) | Clear rate per difficulty within contract bands over 200 runs |
| 9 | Score, combo, grade, results (meta) | Score formula unit-tested. Results match the judgement log |
| 10 | Song select with preview and unlocks (ui) | Preview loops cleanly. Unlock rules enforced |
| 11 | No-fail and wide-window accessibility modes (ux) | Modes persist. Leaderboard tagged by mode |
| 12 | Perf: stable frame pacing during dense sections (perf) | p95 frame time ≤ 16.6 ms on mid tier in the densest chart section |

## 3. Educational

### Definition and player fantasy
Games whose primary goal is a learning outcome (literacy, maths, languages, coding, science) and where **learning is the core loop**, not a quiz bolted onto an unrelated game. The spectrum runs from gamified learning apps (*Duolingo*) through curriculum-aligned games (*Prodigy Math*, *DragonBox*) to open sandboxes. The fantasy is *competence*: "I'm getting better at this." For children it should be play first.

### Core loop
```
practice item in game form → immediate, specific feedback → adaptive difficulty update
  → reward + visible progress → spaced review of weak items → next skill node
```

### Meta loops
- A skill tree or curriculum map that shows mastery.
- Streaks with protective "freezes", daily goals, leagues and leaderboards.
- Avatars, customization and collections as extrinsic rewards (use sparingly).
- Parent and teacher dashboards. Classroom assignment modes.
- Spaced-repetition review queues.

### Session profile
Estimate: 5–15 minutes a day as a habit, or 20–40 minute classroom blocks. Notifications and streaks drive the daily return. Portrait for consumer apps, tablet landscape for schools.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Intrinsic integration (the mechanic *is* the concept) | learning & mastery | *DragonBox* teaches algebra as card manipulation, the gold standard |
| Adaptive difficulty with an item/learner model | learning & mastery; progression & upgrade | Elo or IRT style (formula below). Target about 70–85% success (heuristic) |
| Spaced repetition | learning & mastery; time & energy | Leitner boxes or SM-2-style intervals for retention |
| Mastery thresholds before advancing | learning & mastery | Rooted in mastery learning (Bloom, 1968). Avoid moving learners on too early |
| Error-specific feedback and hints | learning & mastery | Explain the misconception, not just "wrong" |
| Streaks with freezes | time & energy | Strong habit driver. Freezes cut anxiety-driven churn |
| Leagues and leaderboards | social & competition | Motivates some learners, alienates others. Make them optional |

**Adaptive model (Rasch/Elo hybrid).** `P(correct) = 1 / (1 + e^−(θ − β))` for learner ability θ and item difficulty β. After each response: `θ += K·(r − P)`, `β −= K_item·(r − P)`. Pick the next item so P falls in the target band. Elo-based adaptive practice is used in production learning systems (for example the Dutch *Math Garden* platform, described by Klinkenberg et al., 2011). Spaced repetition à la SM-2 (Wozniak): intervals of 1 day, 6 days, then the previous interval × ease factor (starting at 2.5, adjusted by recall quality). Simulate learners against both models before content production.

### Monetization model and typical mix
Freemium subscription (*Duolingo*-style tiers), school and district licences (B2B), premium one-time purchase (*DragonBox*), parent memberships (*Prodigy*), and ads only for adult learners and never for children (§0.3). **Efficacy claims must be substantiated.** The FTC's 2016 settlement with Lumos Labs over brain-training claims is the standard cautionary case. US schools look for evidence tiers under the Every Student Succeeds Act (ESSA).

### KPI expectations
Qualitative, because no sourced ranges were found. Track both engagement (DAU/WAU, streak length, session completion) **and outcomes**: pre/post assessment gains, mastery rate per skill, time to mastery, and retention of skills on delayed review. Engagement without learning gains is a failure in this genre.

### Retention drivers
Streaks and daily goals. Visible mastery progress. Leagues (for those who opt in). Notifications. Parent and teacher involvement. Real-world payoff (grades, travel, jobs).

### Content pipeline and production scope (estimates)
Curriculum design with subject-matter experts. Item banks of hundreds to thousands of items with difficulty calibration. Localization per curriculum and language. Accessibility. Learning-science review. Rough estimate: 3–15 people for a focused title over 9–18 months, plus an ongoing content team. Every item needs SME review for correctness.

### Reference titles
- *Duolingo* (2012): gamified language learning.
- *DragonBox Algebra 5+* (WeWantToKnow, 2012): intrinsic integration.
- *Endless Alphabet* (Originator): early literacy.
- *Swift Playgrounds* (Apple, 2016): coding.
- *Khan Academy Kids* (Khan Academy, 2018): free early learning.
- *Prodigy Math* (Prodigy Education): RPG-wrapped curriculum maths.
- *Elevate* (Elevate Labs): adult skills training.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| The mechanic embodies the concept | "Chocolate-covered broccoli": a quiz with a game skin |
| Adaptive difficulty keeps learners in the productive zone | One-size difficulty bores or overwhelms |
| Feedback explains errors | Wrong/right only, no learning |
| Efficacy is measured and claims are honest | Unsubstantiated "boosts IQ" claims, regulatory risk |
| Teachers and parents get useful dashboards | Black-box progress nobody trusts |

### Innovation vectors
- LLM tutors with guardrails: hints and explanations bounded by verified content, with consent rules for AI data sharing.
- Speech recognition for language and reading, which needs COPPA care for children's voice data.
- Simulation sandboxes for science.
- Adaptive item generation with SME validation.
- Classroom multiplayer.
- Learning layers inside mainstream games.

### Agent-buildability: 3/5
**Why mid:**
- Mechanics are simple and deterministic.
- Adaptive and spaced-repetition models can be simulated with synthetic learners.
- LLMs draft items quickly.
- UI testing is easy.

**Why not higher:**
- Content correctness needs SME review (hallucination risk).
- Learning efficacy can't be verified without real learners.
- Under-13 audiences trigger the full §0.3 stack.

### Starter feature list (P0 vertical slice: one skill strand, 40 items)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Item engine with 3 interaction types (gameplay) | Items load from data. Each type has scripted input tests |
| 2 | Intrinsically integrated core mechanic for the target concept (gameplay) | Design review signs off that the mechanic embodies the concept. Playthrough completes the strand |
| 3 | Learner model (Elo/IRT) (tech) | Synthetic learners of known ability converge within ±0.3 θ after 30 items |
| 4 | Item selection targeting the success band (tech) | Sim success rate within the target band (for example 70–85%) |
| 5 | Error-specific feedback + hints (content) | Every distractor maps to a feedback message. No empty hints |
| 6 | Spaced-repetition review queue (meta) | Intervals follow the configured algorithm (unit test) |
| 7 | Mastery map with skill states (ui) | States match model thresholds. Readable on a 5.5" screen |
| 8 | Streak + freeze + daily goal (meta) | Time-zone-correct day boundaries. Freeze consumption rules unit-tested |
| 9 | Pre/post assessment module (analytics) | Assessment items are separate from practice items. Results logged as events |
| 10 | Parent or teacher summary screen (ui) | Shows mastery and time. Behind a parental gate for child audiences |
| 11 | SME review workflow for items (content) | Every item carries reviewer id and date in data. CI fails on unreviewed items |
| 12 | Privacy mode for under-13 (release) | No third-party ad or analytics SDKs linked in the child build (`compliance_preflight.py` passes) |

## 4. Kids (COPPA constraints)

### Definition and player fantasy
Games designed for children: pre-school (about 2–5), early readers (about 6–8) and tweens (about 9–12). They are built under strict privacy, advertising, purchase and design constraints (§0.3). There are two audiences:
- **For the child**: open-ended play, creativity, role-play, characters, cause and effect, surprise.
- **For the parent** (who pays and decides): safe, ad-free, enriching, controllable, worth the money.

### Core loop
```
open-ended:  enter scene → interact with characters/objects → make up stories → discover surprises
             → unlock new places/characters (parent purchase or subscription)
structured:  pick mini-game → play (no harsh fail state) → stars/stickers → new mini-games/areas
```

### Meta loops
- Location, character and story packs (sandbox titles).
- Sticker books and collections.
- A parent area behind a parental gate: settings, progress, purchases, time limits.
- Seasonal content drops. Character collections.

### Session profile
Estimate: 5–20 minute sessions, often parent-managed (screen-time rules) and frequently offline (car, travel). Tablets are common, as is shared family devices. Landscape and portrait both appear. Design for pause and resume at any moment.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| No-reading UI (icons, voice-over, demonstration) | UX automation | Pre-readers can't read instructions. Show, don't tell |
| Large, forgiving touch targets | UX automation | Much larger than adult minimums. Tolerate imprecise and multi-touch input |
| No fail states (pre-school) / gentle failure (older) | progression & upgrade | Retry without punishment. Celebrate effort |
| Sandbox role-play with cause-and-effect objects | exploration & traversal; narrative & relationship | Replayability comes from imagination, not content volume |
| Parental gate | UX automation | Adult challenge before purchases, links, settings and data sharing |
| Pre-set phrases instead of open chat | social & competition | The safe default (FTC v. Epic precedent) |
| Offline-first content | UX automation | Works without network. Doubles as a privacy advantage |

### Monetization model and typical mix
Premium (one-time), family subscription (whole catalogue), unlock packs (locations, characters). **Not allowed or not acceptable**:
- Behavioural ads.
- Ads outside the store-approved frameworks: Families self-certified SDKs on Google Play, none in Apple Kids Category apart from narrow exceptions.
- Loot boxes or paid random items.
- Manipulative purchase prompts aimed at children.
- Purchases without a gate.

From Oct 1, 2026, EU Kids-category and under-13 apps cannot link out to external payments (volatile facts).

### KPI expectations
Qualitative, because no sourced ranges were found. Parent ratings and trust signals (store reviews, Teacher Approved badges, educator recommendations) drive organic growth. Subscription conversion and churn are the core financials. Analytics on children must be first-party, minimal and consented (§0.3). Many standard KPI tools are unavailable by design.

### Retention drivers
Open-ended replay value. New content drops. Character attachment. Parents' trust and recommendations. Routines (bedtime story apps, learning time).

### Content pipeline and production scope (estimates)
Illustration-heavy art, multi-language voice-over, child-tested UX (playtests with children require parental consent and an ethics protocol), compliance review, and accessibility. Rough estimate: 4–20 people per title over 9–18 months. Large catalogue studios run multiple teams.

### Reference titles
- *My Talking Tom* (Outfit7, 2013): mixed-audience, ad-supported. A contrast case for compliance.
- *Toca Life World* (Toca Boca, 2018): sandbox plus location packs.
- *Khan Academy Kids* (Khan Academy, 2018): free, no ads.
- *Sago Mini World* (Sago Mini): family subscription.
- *Pok Pok*: calm, open-ended play subscription.
- *PBS KIDS Games* (PBS KIDS): free, curriculum-informed.
- *Lingokids*: learning subscription.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Children can play without adult help or reading | Text instructions, tiny buttons, fail-heavy design |
| Parents trust it: no ads, clear pricing, gated purchases | Ad SDKs or dark patterns, store removal, enforcement |
| Open-ended play rewards imagination | Thin content that is exhausted in one session |
| Charming characters and voice | Generic art and robotic voice |
| Compliance built in from day one | Retrofitting COPPA after launch (data already collected) |

### Innovation vectors
- Open-ended "digital toys" with calm design.
- Co-play modes for parent and child.
- Speech-based play, with strict handling of children's voice data (COPPA biometrics).
- AI storytelling *for parents to curate*, never unsupervised generative chat with children.
- Offline-first privacy as a selling point.
- Accessibility for neurodiverse children.

### Agent-buildability: 3/5
**Why mid:**
- Mechanics are simple and deterministic.
- 2D art and voice pipelines apply.
- Compliance can be partly automated: scan linked SDKs, verify the parental gate, check that no network calls go to ad or analytics hosts in the child build.

**Why not higher:**
- Usability with real children is a human checkpoint, run with consent.
- Charm and voice are taste checkpoints.
- Legal review is mandatory.
- AI-generated voice and content for children raise ethical questions that need human sign-off.

### Starter feature list (P0 vertical slice: sandbox with 2 scenes)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Scene with 15 interactive objects (gameplay) | Every object responds to tap and drag. Scripted playthrough touches all |
| 2 | Characters with drag, pose and animation (gameplay) | Characters can be placed anywhere walkable. No softlocks after 1,000 random drags |
| 3 | No-reading UI with voice-over prompts (ux) | No screen requires reading to progress (structural check: no instructional text without icon or audio) |
| 4 | Oversized, forgiving touch targets (ux) | Target sizes meet the contract minimum. Multi-touch doesn't break state |
| 5 | Parental gate (ux) | Gate before purchases, links and settings. Not passable by tap-mashing (test) |
| 6 | Parent area: settings, time limit, purchases (ui) | Time limit enforced. Settings persist |
| 7 | Second scene unlocked by a gated purchase (monetization) | Purchase only behind the gate. Restore purchases works |
| 8 | Offline-first save (tech) | Full play with network disabled. State survives kill |
| 9 | Child-build privacy profile (release) | No third-party ad or analytics SDKs. No device identifiers sent (`compliance_preflight.py` + network log check) |
| 10 | Age gate / audience routing (ux) | Neutral age screen. Child path disables every non-essential data flow |
| 11 | Accessibility: reduced motion, audio-only cues mirrored visually (ux) | Settings respected in all scenes |
| 12 | Performance on older tablets (perf) | p95 frame time ≤ 33.3 ms on the low-tier reference device. Cold start ≤ the contract budget |

## 5. Fitness and location-based

### Definition and player fantasy
Games that turn physical movement or real places into gameplay. The forms are:
- Location-based collection and adventure on a real map (*Pokémon GO*, *Monster Hunter Now*).
- Step- and walk-driven games (*Pikmin Bloom*, *Dragon Quest Walk*).
- Audio-led running stories (*Zombies, Run!*).
- Workout gamification.

The fantasy is *adventure in my real world*: exploring the neighbourhood, exercise as play, meeting other players at real places.

### Core loop
```
location:  walk → spawns near you / at points of interest → encounter (catch, fight, AR optional)
           → collect → power up → co-op raids at points of interest → walk more (distance rewards)
fitness:   start run/walk → audio missions + distance-based pickups → finish → base or collection meta
```

### Meta loops
- Collection logs. Distance-based rewards (hatching, unlocks).
- Real-world community events: community days and city festivals, sometimes ticketed.
- Local co-op raids at points of interest. Friends and trading (often proximity-limited).
- Seasons and weather/time-of-day effects. Background step tracking (with permission).
- Sponsored locations (businesses as points of interest).

### Session profile
Estimate: outdoor sessions of 5–60 minutes plus passive all-day step tracking. Strong seasonality from weather and daylight, with event-driven peaks. Battery and data use are major constraints. Portrait, glanceable, one-handed while walking.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Real-map play with a points-of-interest database | exploration & traversal | Point density varies hugely between urban and rural areas, so design rural fallbacks |
| Spawn distribution by cell/biome/time | exploration & traversal; collection & randomness | Hierarchical cell systems (S2, H3) index the world. Control density per cell |
| Distance-based rewards with a speed cap | time & energy; progression & upgrade | The speed cap stops driving exploits and supports safety |
| Background step tracking (HealthKit, Health Connect) | time & energy | Explicit permission. Never used for ads (§0.4) |
| Local co-op raids | social & competition | Creates real-world meetups. Remote options broaden access but change the game's character |
| AR camera mode (optional) | exploration & traversal | Novelty and sharing. Battery-heavy, so always optional |
| GPS spoofing detection | social & competition | Fairness and anti-cheat. Server-side plausibility checks on movement |

### Monetization model and typical mix
Consumables (capture or attack items, incubators, raid passes), real-world and in-game event tickets, sponsored locations (B2B), cosmetics, and subscriptions in fitness titles (*Zombies, Run!*). Rolling back pandemic-era remote-play affordances drew player backlash (*Pokémon GO*, 2023). Remote vs local design choices become monetization and community decisions.

### KPI expectations
Qualitative, because no sourced ranges were found. Seasonality is strong, events drive large spikes, and urban/rural splits shape retention. Track distance per DAU, event attendance, rural vs urban retention, battery-related uninstall feedback and spoofing-detection rates.

### Retention drivers
Daily walks and step habit. Community days and events. Collections. Local social groups. Seasons. Health goals.

### Content pipeline and production scope (estimates)
Point-of-interest data (sourcing, licensing, moderation and removal requests), a geospatial backend, spawn tables, real-world event operations, safety and trust operations, AR assets, and a creature or content roster. Rough estimate: 20–100+ people, with backend and operations heavy from day one. Fitness audio-story games are smaller: writers, voice and audio, 5–15 people.

### Reference titles
- *Zombies, Run!* (Six to Start, 2012): audio running narrative.
- *Ingress* (Niantic, 2013): the original points-of-interest database.
- *Pokémon GO* (Niantic, 2016): IP plus location, the template.
- *Jurassic World Alive* (Ludia, 2018).
- *Harry Potter: Wizards Unite* (Niantic, 2019): closed in 2022, a cautionary tale that IP alone is not enough.
- *Dragon Quest Walk* (Square Enix/COLOPL, 2019 JP).
- *Pikmin Bloom* (Niantic, 2021): walk-and-plant.
- *Monster Hunter Now* (Niantic/Capcom, 2023): short real-time hunts.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Strong IP or fantasy that justifies going outside | Rural players see empty maps and churn |
| Safe, battery-friendly design | Battery drain, overheating, safety incidents |
| Community events that create memories | Removing access features without dialogue causes backlash |
| Anti-spoofing keeps competition fair | Spoofers dominate raids and leaderboards |
| Seasonal design for weather and daylight | Winter collapse with no indoor or low-movement options |

### Innovation vectors
- Low-movement and indoor modes for accessibility and winter.
- Walking-pace narrative and audio games.
- Wearables integration.
- Location-based social discovery (with strong safety).
- Sponsored and civic partnerships.
- Spatial and AR glasses as a future surface.
- Privacy-preserving approximate-location designs.

### Agent-buildability: 2/5
**Why low:**
- Correctness depends on the real world: GPS drift, background tracking limits, battery and heat, point-of-interest data quality, safety.
- AR can't be verified headlessly.

**What agents can do:**
- Build against **recorded GPS traces and mocked step fixtures** (deterministic replays of walks).
- Spawn-density sims per cell.
- The collection and backend systems.

Field testing remains a human gate.

### Starter feature list (P0 vertical slice: mock-GPS prototype)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Location provider abstraction with trace replay (tech) | Recorded GPS traces replay deterministically. Real provider swaps in without code changes |
| 2 | Map rendering with player marker (ui) | Marker follows the trace. Licensed map attribution shown |
| 3 | Cell-based spawn system (gameplay) | Spawn density per cell within config bands across urban and rural fixtures |
| 4 | Encounter and collect mini-game (gameplay) | Scripted input completes an encounter. Results persisted |
| 5 | Distance rewards with speed cap (meta) | Distance above the speed cap ignored (trace test at driving speeds) |
| 6 | Points of interest with removal and opt-out flags (content) | Flagged points never spawn content. Admin removal propagates |
| 7 | Background step import with permission (tech) | Permission prompt in context. Denial path fully playable |
| 8 | Spoofing plausibility checks (tech) | Teleport and impossible-speed traces flagged server-side |
| 9 | Safety: speed lockout and surroundings reminders (ux) | Lockout above the threshold speed. Reminder on first launch and periodically |
| 10 | Battery budget mode (perf) | Low-power mode cuts GPS polling. 30-minute session battery drain within the contract budget |
| 11 | Location privacy controls (ux) | Approximate-location mode works. No precise location sent to analytics |
| 12 | Event from remote config tied to a region and time window (liveops) | Event activates only inside the geofence and time window in trace tests |

## 6. Cozy

### Definition and player fantasy
Low-stakes games built around routine, creation, collection, relationships and comfort: farming and life-sim, decorating, pet care, café or shop keeping, gentle exploration. Fail states are absent or soft, and timers never punish. The fantasy is *a calm little world that is mine*: nurturing, self-expression, and a place that is happy to see me.

### Core loop
```
daily check-in → tend (water, feed, serve, craft) → harvest / collect → decorate / build
  → befriend characters (gifts, chats) → unlock items / areas / story → log off with something to look forward to
```

### Meta loops
- Catalogues and collections (furniture, fish, insects, recipes, outfits).
- Seasons on the real calendar and seasonal events.
- Relationship and friendship tracks with characters.
- Home and island decoration with sharing, visiting friends and photo mode.
- Gentle story chapters and area unlocks.
- Passive progress while away (visitors arrive while you're gone, as in *Neko Atsume*).

### Session profile
Estimate: a 5–20 minute daily ritual plus optional long creative sessions (decorating). Real-time clocks are common. Portrait or landscape. Relaxed one-handed play.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Gentle real-time growth timers | time & energy | Crops wait, they don't wilt. Absence is never punished |
| Free-placement decoration | progression & upgrade; UX automation | Self-expression is the endgame. Snap and grid options for touch |
| Catalogue collection | collection & randomness | Completion goals without pressure. Show silhouettes of missing items |
| Character friendship and gifting | narrative & relationship | Preferences to discover. Small daily moments |
| Seasonal calendar events | live events | Return reasons tied to real time. Recurring yearly |
| Visiting and sharing homes | social & competition | Social without conflict. Moderate any user text |
| Passive visitors and progress while away | time & energy | A surprise on return. Light FOMO without pressure |

### Monetization model and typical mix
- **Premium**: one-time price, as with *Stardew Valley* mobile.
- **Subscription platforms**: *Hello Kitty Island Adventure* launched on Apple Arcade.
- **F2P**: cosmetic and decoration purchases, passes, and light rewarded ads (*Cats & Soup*-style idle cozy).

Randomized furniture draws exist in some titles. Apply loot-box rules, and remember that cozy audiences are especially sensitive to pressure tactics. *Animal Crossing: Pocket Camp* (Nintendo, 2017) ended its live service in 2024 and was succeeded by a paid offline edition. Plan for players' long-term investment outliving the service.

### KPI expectations
Qualitative, because no sourced ranges were found. Daily-ritual retention can be strong and long-lived, with ARPPU typically lower than mid-core. Watch daily ritual completion, decoration activity, seasonal event participation and churn after seasons end.

### Retention drivers
Daily ritual. Seasonal events. Collections. Character relationships. Decoration expression. Friends' visits. Calm as an emotional need.

### Content pipeline and production scope (estimates)
Content volume is the main cost: hundreds of decorative items, seasonal sets, character dialogue and reactions, and a gentle soundtrack. Rough estimates: 3–20 people over 12–24 months. *Stardew Valley* was famously built by a solo developer, but mobile live cozy titles need steady seasonal content.

### Reference titles
- *Hay Day* (Supercell, 2012): farming with trade.
- *Neko Atsume* (Hit-Point, 2014): passive visitors.
- *Animal Crossing: Pocket Camp* (Nintendo, 2017).
- *Stardew Valley* (ConcernedApe; mobile 2018).
- *Sky: Children of the Light* (thatgamecompany, 2019): social, gentle exploration.
- *Hello Kitty Island Adventure* (Sunblink, 2023).
- *Cats & Soup* (Hidea): idle cozy.
- *Infinity Nikki* (see `skills/genre-playbooks/references/rpg-gacha.md` §2): a cozy open-world gacha.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Charm in art, audio and writing (the whole product) | Generic assets. "Cozy" in name only |
| No punishment for absence | Wilting crops and streak loss create anxiety |
| Deep decoration and self-expression | Shallow item pools that run out in a week |
| A respectful, gentle monetization tone | Aggressive offers that break the mood |
| Seasonal content keeps the world alive | Static world after the first month |

### Innovation vectors
- Cozy plus light narrative mysteries.
- Co-op cozy worlds.
- Cozy open worlds.
- Wellbeing and mindfulness framing.
- Cross-platform save with PC and console.
- UGC decoration sharing.
- LLM-flavoured character chatter inside authored personalities, under editorial and moderation control.

### Agent-buildability: 4/5
**Why high:**
- Systems are deterministic and simple: timers, crafting, catalogues, friendship tracks.
- Economy pacing can be simulated (`economy_sim.py`).
- High-volume decorative 2D art is exactly what a style-locked asset pipeline is good at.

**Why not 5:**
- "Charm" is the product and a taste checkpoint.
- Dialogue warmth needs human editing.
- Seasonal content cadence needs a live plan.

### Starter feature list (P0 vertical slice: one-week loop)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Real-time clock with gentle growth timers (tech) | Growth correct across background, kill and clock change. Nothing decays while away |
| 2 | Plot tending: plant, water, harvest (gameplay) | Scripted playthrough completes a full crop cycle |
| 3 | Crafting with 10 recipes (meta) | Recipes data-driven. Inventory ledger reconciles |
| 4 | Free-placement decoration with snap option (ui) | Placement, rotate and store work by touch. No overlapping colliders |
| 5 | Catalogue with silhouettes for missing items (meta) | Catalogue state matches inventory history |
| 6 | 3 characters with friendship and gift preferences (narrative) | Preferences data-driven. Friendship thresholds unlock dialogue |
| 7 | Passive visitor while away (meta) | Visit odds per config. A visit appears on return within the expected frequency in sim |
| 8 | Seasonal event from the calendar via remote config (liveops) | Event activates by date and time zone without a client update |
| 9 | Home sharing by code + visit (social) | Visitors see the exact layout. No editing rights. User text filtered |
| 10 | Photo mode (ux) | Hides the HUD. Saves to the device with permission |
| 11 | Calm audio and haptics pass (audio) | Loudness within the audio bible target. Haptics optional |
| 12 | Gentle monetization: cosmetic shop, no pop-ups on launch (monetization) | No offers before the first ritual completes. Ledger reconciles |

## Volatile facts (as of Oct 2026 — verify before relying)

**Children and minors**
- The amended COPPA Rule's compliance deadline was Apr 22, 2026. It expands personal information to include biometric identifiers and tightens third-party and mixed-audience duties — [Toy Association](https://toyassociation.org/PressRoom2/News/2026-News/updated-coppa-rule-requirements-take-effect-april-22.aspx); [Loeb & Loeb](https://www.loeb.com/fr/insights/publications/2025/05/childrens-online-privacy-in-2025-the-amended-coppa-rule)
- FTC v. Epic (Dec 19, 2022): $275M COPPA penalty and $245M refunds. Voice and text chat off by default for children and teens — [FTC](https://www.ftc.gov/news-events/news/press-releases/2022/12/fortnite-video-game-maker-epic-games-pay-more-half-billion-dollars-over-ftc-allegations)
- Genshin Impact's publisher settled with the FTC for $20M (Jan 2025). Terms include parental consent for under-16 purchases and odds disclosure — [PocketGamer.biz](https://www.pocketgamer.biz/hoyoverse-agrees-to-20-million-settlement-with-ftc-over-loot-boxes)
- From Oct 1, 2026, Apple in the EU: no link-outs in Kids-category or under-13 apps, and a parental gate for under-18 apps using alternative payments or link-outs — [Apple Newsroom](https://www.apple.com/newsroom/2026/08/apple-announces-changes-for-apps-in-the-european-union/)
- US age-assurance laws: Texas (Jan 1, 2026), Utah (May 7, 2026), Louisiana (Jul 1, 2026), via Apple's Declared Age Range API — [9to5Mac](https://9to5mac.com/2025/11/04/app-store-texas-sb2420-new-apis/). Apple's new age tiers are 4+, 9+, 13+, 16+ and 18+ — [Apple Upcoming Requirements](https://developer.apple.com/news/upcoming-requirements/)
- GDPR Art. 8 sets the digital-consent age at 16 by default (member states may lower it to 13) (background) — [GDPR Art. 8](https://gdpr-info.eu/art-8-gdpr/)

**AI content, narrative and music**
- On Steam, games disclosing AI use got about 53% fewer reviews (median score 84.6% vs 88.3%; correlation, not proven causation) — [Recognizing Patterns](https://recognizingpatterns.substack.com/p/use-ai-to-build-your-game-just-keep). LLMs write engaging stories but struggle with consistent, verifiable mechanics (RPGBench) — [arXiv 2502.00595](https://arxiv.org/html/2502.00595v1)
- Apple guideline 5.1.2(i) requires consent before sharing personal data with third-party AI. Google Play requires in-app reporting for generative-AI output — [Radom](https://www.radom.com/insights/apple-updates-app-review-guidelines-to-strengthen-privacy-protections-against-third-party-ai-data-sharing); [9to5Google](https://9to5google.com/2023/10/25/google-play-gen-ai-policy/)
- Nano Banana 2 accepts up to 14 references but stays reliable only for one or two consistent characters — [Zilliz](https://zilliz.com/ai-faq/how-many-consistent-characters-can-nano-banana-2-maintain-across-a-workflow)
- ElevenLabs Music self-serve plans exclude "Studio Games". A game qualifies as "Indie" only under $500K game revenue and under $1M annual developer games revenue — [Eleven Music Terms](https://elevenlabs.io/music-terms). Lyria output is SynthID-watermarked. Lyria RealTime (BPM, density, stem control) is experimental — [Gemini music docs](https://ai.google.dev/gemini-api/docs/music-generation); [Lyria RealTime](https://ai.google.dev/gemini-api/docs/realtime-music-generation)
- Exclude Suno (no API, download caps, label litigation) and MusicGen (CC-BY-NC weights) from commercial pipelines — [Suno pricing](https://suno.com/pricing); [audiocraft](https://github.com/facebookresearch/audiocraft)
- AI-native narrative titles (aggregator data, unverified): *Whispers from the Star* (Anuttacon, 2025), *AI Roguelite*, *Death by AI* — [NexWorld panorama](https://nexworld.wiki/en/ai-games/ai-games-panorama-2026/)

## Related skills
- `narrative-design`: branching structures, voice, ink/Yarn workflows.
- `audio-direction` and `ai-audio-pipeline`: music licensing, tempo maps, loudness, latency.
- `legal-ethics`: COPPA, Kids Category, age assurance, AI disclosure.
- `accessibility-localization`: timing accessibility, no-reading UI, older and younger audiences.
- `mobile-ux`: touch targets, parental gates, glanceable outdoor UI.
- `economy-design`: cozy pacing, ticket economies, gentle monetization.
- `player-psychology`: habit, streak anxiety, children's development.
- `multiplayer-backend`: geospatial services, home visits, events.
- `mechanics-codex`: narrative, rhythm, learning and cozy mechanic cards.
- `qa-testing`: graph verification, timing bots, GPS trace replays.
