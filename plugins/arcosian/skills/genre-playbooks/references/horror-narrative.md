# Horror and Narrative Playbooks

Horror and narrative games are paced by the writer and the director, not by a score or a ladder. This file holds six playbooks in a shared 15-part template (the 14-part format used elsewhere, plus platform notes), with a focus on PC and console. Mobile visual novels and interactive stories are covered in `skills/genre-playbooks/references/narrative-rhythm-edu-kids.md`; read that file for mobile story monetisation and the branching-narrative checks, and do not repeat them here.

1. Survival horror
2. Psychological horror / walking sim
3. Co-op horror with proximity voice
4. Visual novel
5. Narrative adventure / point-and-click
6. Choice-based interactive fiction (Ink, Twine, Yarn Spinner)

Four foundations come first: tension and release pacing curves, sound for fear, branching structures with state tracking, and localising text-heavy games. Choice-based fiction and visual novels are the most agent-buildable games in this catalogue because the product is structured text plus state, and the graph can be verified. Horror is the opposite: its value is in felt dread, which only human playtests confirm. Market numbers live in the dated volatile-facts section.

## Contents

| § | Playbook | Session profile (estimate) | Primary monetisation | Agent-buildability | First project for an agent pipeline? |
|---|---|---|---|---|---|
| 0 | [Shared foundations](#0-shared-foundations) | — | — | — | Read first |
| 1 | [Survival horror](#1-survival-horror) | 30–90 min sittings, 6–15 h campaign | Premium | 2/5 | No, one floor and one stalker only |
| 2 | [Psychological horror / walking sim](#2-psychological-horror--walking-sim) | 1–3 h campaign, one or two sittings | Premium, low price | 3/5 | Yes, a short vignette |
| 3 | [Co-op horror, proximity voice](#3-co-op-horror-with-proximity-voice) | 20–45 min runs with friends | Premium, low price, cosmetics | 2/5 | Only a solo-with-bots slice |
| 4 | [Visual novel](#4-visual-novel) | 20–60 min sittings, 5–40 h reads | Premium, DLC | 5/5 | Yes |
| 5 | [Narrative adventure / point-and-click](#5-narrative-adventure--point-and-click) | 30–90 min sittings, 4–12 h | Premium, episodic | 3/5 | Yes, one room set |
| 6 | [Choice-based interactive fiction](#6-choice-based-interactive-fiction-ink-twine-yarn-spinner) | 10–40 min sittings, 1–8 h | Premium, pay-what-you-want, ads on web | 5/5 | Yes |
| — | [Volatile facts](#volatile-facts-as-of-oct-2026--verify-before-relying) | — | — | — | Check before quoting numbers |

## How to use these playbooks

- Copy the core loop into `contract.json → loops[]`. Set `meta.genre` to `horror` or `narrative` and `meta.subgenre` to the playbook slug. Set `meta.platforms`, `meta.input` and `meta.orientation`. Set `technical.multiplayer` (`none`, `coop` or `realtime`) for the co-op horror playbook.
- Turn the starter feature list into P0 `features.json` entries with `gs.py feature add`. Each acceptance criterion maps to `unit`, `playthrough` or `replay` gate evidence. Story playbooks can also use a graph-walk check (every ending reachable, no dead ends).
- Mechanic category labels used here: exploration & traversal, combat, puzzle & logic, narrative & dialogue, progression & upgrade, economy & resources, social & competition, UX automation. Resolve them with `gs.py kb "<mechanic>" --skill mechanics-codex`.
- For branching design and writing process use `narrative-design`. For fear audio use `audio-direction`. For text-heavy localisation use `accessibility-localization`. For input and platform differences use `platform-targets`. For storefront and age-rating steps use `pc-web-release` and `console-pathway`.
- KPI statements are qualitative unless sourced. Premium narrative games track completion rate, review score, refund rate and wishlist conversion more than D1 and D30.

## 0. Shared foundations

### 0.1 Tension and release: pacing curves
Fear is a rhythm. A constant high-threat level numbs the player within minutes (habituation). Build the curve on purpose.

```
Intensity
  ^        peak       peak
  |       /  \       /  \     rise: uncertainty, signs, sound
  |      /    \     /    \    peak: encounter or reveal (short)
  | ____/      \___/      \__ release: safe space, loot, story
  +---------------------------------> time
```

Procedure:
1. Write the **beat sheet**: a list of beats with a type (calm, unease, threat, encounter, release) and a target length. A typical default is 3–6 minutes of build per 30–60 seconds of peak, then 2–4 minutes of release (estimates; test with players).
2. **Escalate by kind, not volume.** Move through three steps: something is wrong (a sound, an object moved), something is near (a sighting, a trace), something is here (an encounter). Skipping steps wastes the dread.
3. **Withhold.** Show the threat for the shortest time that still registers. Anticipation is worth more than the reveal.
4. **Safe spaces and save points** teach the player where relief lives. Break the safety rule once or twice per game, not more.
5. **Resources set the stakes.** In survival horror, scarcity of ammo, health and light gives every encounter a price. Tune with an economy sim (`economy-design`): aim for the player to finish with about 20–30% of the resources they could have found (estimate).
6. **Threat director.** A system that raises threat when the player has been calm too long and lowers it after an encounter. Inputs: time since last threat, player health, resources, distance to objective. Output: spawn chance, patrol bias, sound-cue chance. Keep it bounded and logged so a test run can replay the curve.
7. **Fairness.** Every death needs a visible cause. Telegraph lethal threats with sound or animation at least once before they kill.
8. **Test with a tension trace.** Playtesters mark a 1–5 tension value every 30 seconds. Compare against the beat sheet. See `playtest`.

### 0.2 Sound for fear
Sound carries more fear than image. Use it as the primary threat channel. Full process, mixing and middleware choices are in `audio-direction` and `audio-production`; this is the minimum a horror game needs.
- **Silence is a tool.** Drop ambience for a few seconds before a peak. Do not fill every second.
- **Low-frequency and dissonance.** Sustained low tones and detuned clusters raise unease. Keep sub-bass below levels that distort laptop speakers, and offer a headphone-versus-speaker option.
- **Diegetic cues for AI state.** Let the enemy's sounds (breathing, steps, a hum) tell the player its state. The player learns the rules by listening.
- **Spatial audio.** Use 3D positional sound with occlusion so a monster behind a door is muffled. Test on stereo headphones first.
- **Proximity voice.** In co-op, voice attenuates with distance and is filtered by walls. Voice becomes both a tool and a risk (see §3).
- **Dynamic layers.** Fade stems by threat level. Never let the music announce that the safe moment has started unless that is the design.
- **Mix for accessibility.** Provide subtitles and visual sound indicators for key threats, volume sliders per bus and a "reduce jump scares" option. See `accessibility-localization`.
- **Jump scares.** Use rarely and earn them. A loud sting with no build is cheap and loses force after one use.

### 0.3 Branching structures and state tracking
Link: `narrative-design` for writing craft and `skills/genre-playbooks/references/narrative-rhythm-edu-kids.md` §0.1 for the verification checklist. This is the structural summary used by the three story-led playbooks.

| Structure | Shape | Cost per extra choice | Use when |
|---|---|---|---|
| Linear with flags | One path. Flags change lines and small scenes | Low | Walking sims, adventures, most visual novels |
| Branch and bottleneck | Branches that rejoin at fixed scenes | Medium | Most choice-based stories. The default |
| Parallel tracks (routes) | Separate routes after a split | High (content multiplies by routes) | Dating-style visual novels with character routes |
| Hub and spoke | Player picks order of spokes, returns to a hub | Medium | Adventures and investigations |
| Gauntlet | A series of scenes, failure ejects to a branch | Medium | Survival narratives |
| Storylets / qualities | Content cards gated by state | Low per card, hard to verify | Large, replayable narratives |
| Full tree | Every choice branches forever | Exponential | Avoid. Only for very short pieces |

**Combinatorial warning.** A tree with 2 choices per scene over 10 scenes has 2¹⁰ = 1,024 paths. With a bottleneck every third scene the writing load stays near 10 × 2 = 20 scene variants.

**State tracking rules:**
1. Name every variable in one data file: `trust_alice` (int, range −3…3), `knows_secret` (bool). No unnamed flags in prose.
2. Prefer a few **meaningful** variables over dozens of tiny ones. Players cannot track more than about five relationships or values (estimate).
3. Record each choice as `(scene_id, choice_id)` in the save. Re-derive state from it where possible, so a script change cannot corrupt old saves.
4. **Verify with a graph walk.** Export the story as a graph and check: every scene is reachable, every ending is reachable, no dead end without an ending, no variable read before it is set, no choice with a condition that is always false.
5. **Reflect choices.** Show a visible consequence within two scenes for each major choice, even a small one (a line, a gesture).
6. **Save and rewind.** Provide manual saves, autosave at chapter starts and a back or history log on PC and console. A seen-text skip option is expected in visual novels.

**Authoring tools.** Ink (inkle's scripting language), Yarn Spinner (dialogue language used in Unity and Godot), Twine (visual editor producing HTML) and Ren'Py (visual novel engine) are the common choices. Compare them in §6 and §4.

### 0.4 Localising text-heavy games
Text-heavy games ship large word counts, so a bad localisation setup costs the most here. Full guidance is in `accessibility-localization`.
1. **String IDs, not strings in code.** Every line has a stable ID. Keep source and translations in files (CSV, PO, JSON, or the authoring tool's own format).
2. **Word counts.** Estimate cost as words × rate × languages. A choice-based game of 150,000 words in 8 languages is 1.2 million words (arithmetic), so plan budgets and review time early.
3. **Expansion.** German and Russian text often runs 20–35% longer than English, and some Asian-language text is shorter but taller (estimates). Design boxes to flex, and test the longest language first.
4. **No concatenation.** Build sentences from whole strings with placeholders (`{name}`), not by joining fragments. Use plural and gender rules (ICU message format or the engine equivalent).
5. **Context for translators.** Give the speaker, the scene, the tone and a screenshot. Mark jokes, puns and references.
6. **Fonts.** Include glyph coverage for CJK, Cyrillic and accented Latin. Use a fallback font chain. Test right-to-left layout if shipping Arabic or Hebrew.
7. **Variables in prose.** If the player name appears in text, test gendered and inflected languages.
8. **Voice and subtitles.** Localising voice multiplies cost. Subtitles-first is the usual indie choice.
9. **Pseudo-localisation test.** Replace text with accented, lengthened dummy strings to find clipping and hard-coded text before real translations arrive.
10. **Linguistic QA pass in context.** Translators see the game running, not a spreadsheet.

### 0.5 Content notes and age ratings
Horror and mature narrative games should state content on the store page and at launch (violence, self-harm, abuse, sensitive themes) and offer a skip or "content warning" option. Age ratings follow regional systems and storefront questionnaires. See `legal-ethics` and `console-pathway`. Adult-content storefront rules differ by store and change often (volatile facts).

## 1. Survival horror

### Definition and player fantasy
The player explores a hostile place with limited ammo and health, solving environmental puzzles while avoiding or fighting monsters. The fantasy is *a vulnerable survivor who endures*: resourcefulness under pressure, the relief of reaching a safe room, and the dread of the next door.

### Core loop
```
explore a space → find keys, items, resources → meet a threat (flee / fight / avoid)
  → spend resources or lose health → reach safety (save, heal, manage inventory)
  → unlock next area → story beat → explore
```

### Meta loops
- **Map knowledge and backtracking.** Shortcuts open and the hub becomes familiar and safer.
- **Inventory management.** Limited slots force trade-offs.
- **Weapon and gear upgrades.**
- **Multiple endings and difficulty modes.**
- **New game plus, speed-run and challenge modes.**

### Session profile
Estimate: 30–90 minute sittings, 6–15 hour campaigns, played alone, often at night. Players stop at safe rooms. Save points define the rhythm.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Scarce ammo, health and light | economy & resources | Tune by sim (§0.1 step 5) |
| Inventory with limited slots | economy & resources | Every item is a decision |
| Enemy AI with senses (sight, sound) and states | combat | Patrol, investigate, chase, lose track. Telegraph states |
| Safe rooms and save points | progression & upgrade | Teach relief. Limit saves for tension, or offer an assist |
| Key-and-lock progression and map loops | exploration & traversal | See `level-design` for interlocking loops |
| Stealth and hiding | exploration & traversal | Gives a non-combat answer |
| Fixed-angle cameras (optional) | UX automation | A stylistic choice with accessibility cost |
| Threat director | combat | §0.1 step 6 |

### Monetisation model and typical mix
Premium purchase, sometimes with DLC story chapters or a modes pack. Free-to-play is rare. Avoid selling resources that remove the scarcity the design relies on. Remakes and re-releases are common revenue.

### KPI expectations
Qualitative. Premium: completion rate of the first chapter, completion of the whole campaign (long campaigns often finish low), review score, refund rate and wishlist conversion. Streaming and clip sharing drive discovery.

### Retention drivers
Atmosphere and unease. Mastery of the map. Multiple endings and harder modes. Speed-run and challenge communities. Word of mouth from streams.

### Content pipeline and production scope (estimates)
Environments, enemy models and animation, audio and level scripting dominate. A tight indie scope is 3–5 hours with one location and 3–4 enemy types. A full 10-hour campaign with several environments is a large-team, multi-year effort. Reusing a small set of modular rooms (`level-design`) controls cost.

### Reference titles
- *Resident Evil* series (Capcom): the template for survival horror.
- *Silent Hill* series (Konami): psychological survival horror.
- *Dead Space* (Visceral, EA): over-the-shoulder, dismemberment as resource play.
- *Alien: Isolation* (Creative Assembly): a single stalker with a director system.
- *The Evil Within* (Tango Gameworks).
- *Signalis* (rose-engine): retro-styled, puzzle-heavy.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Scarcity is felt but fair | The player is either swimming in ammo or soft-locked |
| The enemy has clear rules the player can learn | The enemy is random and cheap |
| The environment is memorable and interconnected | Corridors blur together |
| Sound and lighting do the scaring | Reliance on jump scares |
| A solid assist and difficulty menu | Controls fight the player (tank controls with no option) |

### Innovation vectors
- Adaptive threat directors with explainable behaviour.
- Procedural room layouts with solver-verified key chains.
- Roguelite structure with persistent knowledge.
- Short, dense survival horror (2–3 hours) at lower price.
- Accessibility modes (reduced fear intensity, aim assist, visible audio cues).
- Co-op survival variants.

### Agent-buildability: 2/5
**Why low:**
- Fear is a felt experience. Gates can verify resource counts and AI states, but not dread.
- Art, lighting and audio direction need human taste.

**What agents do well:**
- Inventory, save, key-and-door logic, AI state machines, resource economy sims, level graph checks, accessibility menus.

### Starter feature list (P0 vertical slice: one floor, one stalker, one safe room)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Controller with sprint and crouch (gameplay) | Speeds match the tuning table. Crouch lowers the noise value as defined |
| 2 | Enemy AI with sight and hearing, states patrol/investigate/chase/search (gameplay) | A scripted test shows each state transition. Detection ranges come from data |
| 3 | Inventory with 8 slots and 4 item types (gameplay) | Slot limits enforced. Items stack per rule |
| 4 | Resource economy for ammo and health (economy) | A sim of 100 runs ends with 20–30% of found resources left on average |
| 5 | Key, lock and shortcut graph for one floor (level) | Graph check: all areas reachable, no soft-lock, one shortcut opens a loop |
| 6 | Safe room with save and item box (meta) | Save restores the exact state. Item box persists |
| 7 | Threat director with a logged curve (gameplay) | Curve log shows peaks and releases within the beat sheet bounds |
| 8 | 3D audio with occlusion and enemy sound set (audio) | An enemy behind a closed door is attenuated. Sound states map to AI states |
| 9 | Difficulty and assist menu (ux) | At least resource scale, aim assist, damage taken and subtitle size |
| 10 | Content notes and "reduce jump scares" toggle (ux) | The toggle disables flagged stings and flashes |
| 11 | Death, retry and checkpoint flow (ux) | Retry returns to the last save in under 10 seconds |

### Platform notes
- **PC.** Mouse and keyboard plus pad. Support high frame rates, a field-of-view slider, and motion blur and head-bob toggles. VR is an option. Shader compilation stutter breaks dread, so pre-compile. Streamers are a main marketing channel (`pc-web-release`).
- **Console.** Pad-first. Haptics and adaptive triggers can carry tension. Aim assist is expected. Load times and a stable frame rate matter. Rating and certification steps apply (`console-pathway`).
- **Web.** Small-scale horror works in a browser (short, low-poly, itch.io style). Keep builds small and handle pointer lock and audio unlock.
- **Mobile.** Rare for full survival horror because of session length and controls. Business model on mobile is premium or short episodic; PC and console are premium.

## 2. Psychological horror / walking sim

### Definition and player fantasy
Atmospheric first-person exploration where dread comes from space, sound, ambiguity and the player's mind, with little or no combat. The fantasy is *investigating something wrong*: piecing together a story from rooms and objects while uncertainty grows.

### Core loop
```
walk through a space → notice anomaly, object or sound → interact or read / listen
  → learn a fragment of story → space changes (loop, shift, new area) → continue
```

### Meta loops
- **Anomaly spotting and loops.** Detect what changed and respond.
- **Collectible lore.** Notes, audio logs, photos.
- **Multiple endings** based on what the player noticed or did.
- **Short replay for missed details.**

### Session profile
Estimate: 1–3 hour campaign, often finished in one or two sittings. Short enough to complete in an evening, which suits streaming and low price points.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Environmental storytelling | narrative & dialogue | Place objects so players infer the story |
| Anomaly and change detection | puzzle & logic | State-based scene variants. Keep a small diff set |
| Audio logs, notes and photos | narrative & dialogue | Write short. Offer a journal |
| Looping and spatial impossibility | exploration & traversal | Tech: teleport and portal tricks |
| Limited interaction verbs | exploration & traversal | Few verbs, each meaningful |
| Sanity or unreliable perception | UX automation | Visual and audio distortion as feedback |
| Chase or stealth set piece (optional) | combat | Rare, scripted, fair |

### Monetisation model and typical mix
Premium at a low price. DLC is rare. A short free demo drives wishlists. No in-game purchases.

### KPI expectations
Qualitative. Wishlists and demo-to-purchase conversion, completion rate (high when short), review score, streamer pickup and refund rate. A short game can earn well if it spreads by streaming.

### Retention drivers
Mystery. Streaming and community theories. Alternate endings. Short length with strong ending impact. Atmosphere over mechanics.

### Content pipeline and production scope (estimates)
Small teams, short development (months to a year or two). Scope is controlled by reusing a small set of environments and varying them by lighting, layout and sound. Asset packs and AI-assisted assets need legal checks (`legal-ethics`, `ai-asset-pipeline`).

### Reference titles
- *P.T.* (Kojima Productions): a looping hallway demo that influenced the genre.
- *Layers of Fear* (Bloober Team).
- *Observation* (No Code): sci-fi view through a station AI.
- *Visage* (SadSquare Studio).
- *Control* (Remedy): unsettling architecture at a larger scale.
- *Dear Esther* (The Chinese Room): a walking-sim origin point.
- *Firewatch* (Campo Santo): narrative walking game with a calmer tone.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| A strong, consistent atmosphere and a clear hook | A grab bag of tropes without a point of view |
| Story fragments reward attention | Lore is hidden behind pixel-hunting |
| Movement and camera feel good | Slow walking with nothing to see |
| The ending lands | The ending is vague and unearned |
| Short and tight | Padding with backtracking |

### Innovation vectors
- Procedural anomaly loops with solver checks.
- Reactive environments that adapt to the player's gaze or path.
- Voice and microphone as input (with consent).
- Found-footage and analogue-horror presentation.
- Short episodic releases with community theories.
- Mixed with puzzle or detective mechanics.

### Agent-buildability: 3/5
**Why mid:**
- Scene variants, state flags, journal systems and interaction logic suit agents.
- Anomaly diff tests can be automated.

**Why not higher:**
- Atmosphere, lighting, art and sound design are the product, and they need human taste.

### Starter feature list (P0 vertical slice: a 15-minute vignette)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | First-person controller with walk, crouch, look and interact (gameplay) | Speeds and reach come from data. Interact prompt shows for valid targets only |
| 2 | Scene state machine with 5 states (tech) | Each state loads the named variant. Replay of a recorded path reaches the same state |
| 3 | Anomaly system with 8 anomalies (gameplay) | Each anomaly is detectable. A bot walkthrough finds all within the time limit |
| 4 | Journal with notes and audio logs (ui) | Collected items persist. Audio plays with subtitles |
| 5 | Two endings by player choice (narrative) | Graph walk reaches both. No dead ends |
| 6 | Lighting and audio mood presets (art/audio) | Presets switch on state change within 1 second. Audio follows `audio-direction` checks |
| 7 | One chase or scripted scare (gameplay) | Telegraphed. Death returns to a checkpoint in under 10 seconds |
| 8 | Accessibility: subtitles, reduce motion, reduce scares (ux) | Toggles persist. Flashing content stays under the photosensitivity limit |
| 9 | Save and resume (tech) | Resume restores the state and position |
| 10 | Demo build flag (release) | A flag cuts the build to the first 15 minutes with a wishlist prompt |

### Platform notes
- **PC.** Main platform for the genre. Mouse look, field-of-view and motion options. A free demo and demo events are common routes (`pc-web-release`). Check performance on integrated graphics.
- **Console.** Pad-first with a good look-sensitivity and dead-zone menu. Haptics help. Ratings required (`console-pathway`).
- **Web.** Short vignettes are common on itch.io. Mind pointer lock, audio unlock and file size.
- **Mobile.** Possible, but atmosphere suffers from small screens and noisy surroundings. Business model: low-priced premium on PC and console, premium or ads on mobile.

## 3. Co-op horror with proximity voice

### Definition and player fantasy
Two to eight friends enter a hostile place together, complete objectives, and try to escape, with voice chat that fades with distance and is picked up by monsters. The fantasy is *panic shared with friends*: laughing, shouting and betrayal while something hunts the group.

### Core loop
```
lobby → drop into a procedural or fixed map → search for objectives and loot
  → noise attracts a threat → flee, hide or distract → extract or wipe
  → payout → buy upgrades → next run
```

### Meta loops
- **Run payout and shop.** Currency buys gear and cosmetics.
- **Unlock tree.** New items, maps and monsters.
- **Daily or weekly challenges and seasonal updates.**
- **Cosmetics and lobby customisation.**
- **Community clips and memes.**

### Session profile
Estimate: 20–45 minute runs, sittings of 1–3 hours with the same group. Sessions are social and scheduled, often evenings and weekends.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Proximity voice chat | social & competition | Distance attenuation and wall filtering. Voice reaches monsters in some designs |
| Noise and detection | combat | Footsteps, voice and objects create noise. The AI hears it |
| Extraction loop with quota or timer | economy & resources | Risk and reward on each run |
| Procedural map per run | exploration & traversal | Layouts must pass solver checks |
| Shared and individual inventory | economy & resources | Weight limits drive teamwork |
| Revive and spectate | social & competition | Dead players keep a role (spectate, voice from beyond) |
| Emergent comedy from physics | movement & traversal | Physics objects create stories worth clipping |
| Cosmetics for status | collection & randomness | Avoid paid random boxes |

### Monetisation model and typical mix
Low-price premium with free updates, plus cosmetics. Games in this niche have grown from small teams on low prices, driven by streaming and word of mouth. Avoid pay-to-win items. Cosmetic stores should avoid loot boxes in markets with restrictions (`legal-ethics`).

### KPI expectations
Qualitative. Track concurrent players, group size, runs per session, return rate within 7 days, streamer and clip reach, refund rate and wishlist conversion. A sharp spike and decline is typical of a viral hit, so plan content updates.

### Retention drivers
Social play with friends. Emergent stories. Content updates (new maps, monsters, items). Cosmetic collection. Challenges. Community mods if supported.

### Content pipeline and production scope (estimates)
Small teams can ship a version with 2–4 maps, 5–8 monsters and 30–60 items. The cost sits in networking, voice, anti-cheat basics, balance for varied group sizes and lobby tooling. Mods extend life but add moderation load.

### Reference titles
- *Phasmophobia* (Kinetic Games): ghost hunting with voice recognition.
- *Lethal Company* (Zeekerss): scavenging with proximity voice and a quota.
- *Content Warning* (Landfall): filming scares for views.
- *Left 4 Dead* series (Valve): co-op horror with an AI director.
- *Dead by Daylight* (Behaviour Interactive): asymmetric horror, one killer against survivors.
- *Devour* (Straight Back Games): co-op against a cult.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Voice and noise create funny and scary moments | Voice is just a normal party chat |
| Easy lobby: invite a friend in under 30 seconds | Complex matchmaking or NAT failures |
| Content scales for group sizes | Balanced for four and broken for two |
| Frequent small updates | A single launch with no follow-up |
| Cheap and low barrier | Heavy hardware requirements |

### Innovation vectors
- Voice-aware AI (reacting to volume) with player consent.
- Asymmetric roles and spectator interaction.
- Streamer integration (audience votes affect the run).
- Dedicated server options for large groups.
- Mod workshop with curated maps.
- Solo mode with AI teammates.

### Agent-buildability: 2/5
**Why low:**
- Networking, voice, lobbies, anti-cheat and live balance for group dynamics are hard to verify by gates.
- Fun depends on groups and emergent play.

**What agents do well:**
- Procedural map generation with solver checks, AI sense models, item tables, economy sims, UI and settings, bot-driven soak tests for the single-player slice.

### Starter feature list (P0 vertical slice: solo plus bots, then 2 players)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Player controller with sprint, stamina and noise values (gameplay) | Noise per action comes from the table. Crouch halves it by default |
| 2 | Monster AI with hearing and states (gameplay) | Detection scales with noise and distance. State transitions logged |
| 3 | Procedural map of 12 rooms with objectives (level) | Solver proves all objectives reachable and extraction connected in 1,000 seeds |
| 4 | Loot, carry weight and quota (economy) | Weight slows movement per curve. Quota matches the contract target |
| 5 | Proximity voice with distance falloff (tech) | Volume follows the falloff curve. A wall attenuates by the set amount (test with a loopback bot) |
| 6 | Lobby, host and join by code (tech) | Two clients join in under 30 seconds in a test. Reconnect restores state |
| 7 | Death, spectate and revive (gameplay) | Dead players can spectate. A revive restores the stated health |
| 8 | Run payout and shop with 10 items (meta) | Payout follows the formula. Purchases persist |
| 9 | Voice privacy and consent controls (ux) | Mute, push-to-talk and block work. Voice is not recorded or stored by default |
| 10 | Bot teammates for solo play (gameplay) | Bots follow, carry and revive within rules |
| 11 | Network soak: 4 simulated clients at 100 ms and 2% loss (tech) | No desync or crash over 30 minutes |

### Platform notes
- **PC.** Home of the genre. Platform friends and invites, push-to-talk, microphone selection, input device handling and dedicated server or relay options. Check anti-cheat needs. Voice moderation and reporting tools matter (`multiplayer-backend`, `pc-web-release`).
- **Console.** Platform voice chat rules and parental controls apply, and cross-play needs a voice policy. Party and invite flows are certification items (`console-pathway`).
- **Web.** Browser multiplayer with WebRTC voice is possible for small lobbies. Microphone permission prompts add friction.
- **Mobile.** Uncommon. Voice in noisy places and small screens limit it. Business model: low-price premium on PC, cosmetics on any free-to-play version.

## 4. Visual novel

### Definition and player fantasy
A story told mostly through text, character art, backgrounds, music and choices. Sub-types: kinetic novels (no choices), dating-style route novels, mystery and detective novels, and adult-oriented titles with storefront restrictions. The fantasy is *being inside a story*: relationships, mystery and emotional payoff.

### Core loop
```
read scene (text, sprites, voice, music) → reach a choice or a flag check
  → branch → consequences in later scenes → ending → replay for other routes
```

### Meta loops
- **Routes and endings.** Character routes, with a true ending gated behind others.
- **Gallery and music room.** Unlock CGs and tracks.
- **Affection or stat tracking.**
- **Chapter releases and fan translations.**
- **Fandom and merchandise.**

### Session profile
Estimate: 20–60 minute sittings on PC and console, reads of 5–40 hours. Skip and auto modes are core UI. Played on handhelds, laptops and sofas. See `narrative-rhythm-edu-kids.md` for the mobile, episodic and ticket-gated version.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Choices and route flags | narrative & dialogue | §0.3 branch-and-bottleneck or routes |
| Text speed, auto, skip-seen | UX automation | Required UI on PC and console |
| Backlog and rollback | UX automation | Re-read and undo a choice |
| Sprite expressions and staging | narrative & dialogue | Data-driven scripts. Reuse sprites |
| Voice acting and music | narrative & dialogue | Partial voicing is common |
| CG gallery and replay scenes | collection & randomness | Gives replay value |
| Mini-games and puzzles (optional) | puzzle & logic | Keep short. Offer skip |
| Save slots and quick save | UX automation | Many slots. Save in the middle of a scene |

### Monetisation model and typical mix
Premium on PC and console, DLC for extra routes or epilogues, and fan-disc sequels. Mobile versions often use episodic tickets and passes (see `narrative-rhythm-edu-kids.md`). Adult-oriented titles face storefront and payment-processor rules (volatile facts). Check engine licence terms before shipping; Ren'Py is open source under its own licence.

### KPI expectations
Qualitative. Premium: completion rate, review score (often strong among fans), wishlist conversion and DLC attach. Genre fans read in bulk and share. Translation reach often drives sales beyond the source language.

### Retention drivers
Character attachment. Route completion and the true ending. Gallery unlocks. Community discussion. Sequels and fan discs.

### Content pipeline and production scope (estimates)
Writing and art dominate. Characters need 3–8 expressions each in several outfits, plus backgrounds and CGs. A small project of 80,000–150,000 words with 4 characters is a practical indie scope (estimate). Voice and music add cost. AI-assisted art needs disclosure and legal care on stores that require it (volatile facts; `ai-asset-pipeline`, `legal-ethics`).

### Reference titles
- *Doki Doki Literature Club!* (Team Salvato): genre-subverting horror visual novel.
- *Steins;Gate* (5pb. / Nitroplus): time-travel mystery novel.
- *Phoenix Wright: Ace Attorney* series (Capcom): courtroom investigation, a hybrid adventure.
- *Danganronpa* series (Spike Chunsoft): mystery with trial gameplay.
- *Fate/stay night* (Type-Moon): long-form route-based novel.
- *Hatoful Boyfriend* (Mediatonic): parody dating sim.
- *Coffee Talk* (Toge Productions): conversation-led cozy novel.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Strong writing and distinct characters | Flat characters and cliché beats |
| Choices matter or at least feel meaningful | Choices change nothing visible |
| Smooth UI (skip, backlog, rollback, saves) | Missing basics such as skip-seen |
| Consistent art style and good music | Mixed asset quality |
| Good localisation | Machine-translated or unchecked text |

### Innovation vectors
- Hybrids with investigation, deckbuilding or management.
- Reactive sprites and dynamic staging driven by state.
- Procedural side stories with authored endings.
- LLM-assisted dialogue with strict authored guardrails (see `narrative-design`).
- Accessible modes: dyslexia-friendly fonts, text-to-speech, high contrast.
- Episodic releases with community voting.

### Agent-buildability: 5/5
**Why high:**
- A structured script plus state is ideal for agents. Graph checks verify reachability and endings (§0.3).
- Engines such as Ren'Py take scripts as text. Localisation pipelines are mechanical.

**What stays human:**
- Writing taste and art direction. These decide whether the game is good, even when the code is complete.

### Starter feature list (P0 vertical slice: one chapter, two routes, three endings)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Script format with scenes, lines, speakers and commands (tech) | Parser loads the sample script. Unknown commands fail at build time |
| 2 | Text box with speed, auto, skip-seen and backlog (ui) | Skip stops at unseen text and at choices. Backlog shows the last 100 lines |
| 3 | Sprite and background staging with transitions (art) | Each command shows the named asset. Missing assets fail the build |
| 4 | Choices with variable effects (narrative) | Effects match the variable file. Conditions evaluate correctly |
| 5 | Two routes with a shared opening (narrative) | Graph walk: all scenes reachable, no dead ends |
| 6 | Three endings (narrative) | A scripted playthrough reaches each ending |
| 7 | Rollback to previous choice (ux) | Rollback restores exact variables and screen |
| 8 | Save slots, quick save and autosave (tech) | Save and load restore the same line. A corrupt save is rejected |
| 9 | Gallery and music room (meta) | Items unlock on the stated trigger and persist |
| 10 | String table export for localisation (tech) | Every line has a stable ID. Pseudo-localisation build passes (§0.4) |
| 11 | Accessibility: font size, font choice, contrast, text-to-speech hook (ux) | Settings persist. Text never overflows the box at the largest size |

### Platform notes
- **PC.** The main platform. Mouse click, keyboard shortcuts, windowed and full screen, high-resolution art, mod and fan-translation support. Ren'Py builds for Windows, macOS, Linux and web. Store pages need content descriptors (`pc-web-release`).
- **Console.** Pad navigation with fast skip, cloud saves and trophy or achievement lists. Handhelds suit long reads. Ratings and platform content policies apply, and adult content is often restricted (`console-pathway`).
- **Web.** Light visual novels run in the browser. Keep assets compressed. Autosave to local storage with care.
- **Mobile.** Portrait layouts, tap to advance, episodic tickets. See `narrative-rhythm-edu-kids.md`. PC and console are premium; mobile is more episodic and ad-led.

## 5. Narrative adventure / point-and-click

### Definition and player fantasy
The player explores scenes, collects items, talks to characters and solves puzzles to advance a story. Sub-types: classic inventory puzzle adventures, modern narrative adventures with dialogue choices, and detective games. The fantasy is *being the clever protagonist*: working out how things fit, and enjoying a well-told story.

### Core loop
```
enter scene → examine, talk, collect → combine items / use dialogue to solve a puzzle
  → progress the story → new scene or chapter → story beat
```

### Meta loops
- **Episodes or chapters.** Release in parts.
- **Hint systems and journals.**
- **Multiple endings or branching conversations.**
- **Collectibles and achievements.**
- **Director's commentary and art galleries.**

### Session profile
Estimate: 30–90 minute sittings, 4–12 hour campaigns. Players stop when stuck, so the hint system affects completion.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Inventory puzzles | puzzle & logic | Logic must be learnable. Avoid moon logic |
| Dialogue trees | narrative & dialogue | §0.3. Keep each node short |
| Verb set or context cursor | UX automation | Fewer verbs are friendlier |
| Hotspot highlight | UX automation | A key accessibility toggle against pixel-hunting |
| Hint system with tiers | UX automation | Nudge, then hint, then solution |
| Cutscenes and set pieces | narrative & dialogue | Budget heavy |
| Journal and objective log | UX automation | Cuts "what do I do now?" stalls |
| Chapter choices and consequences | narrative & dialogue | Use state tracking and recaps |

### Monetisation model and typical mix
Premium, often at a mid price point, with episodic releases sold as a season pass. Remasters and ports of older titles are common. No in-game purchases. Demos and a strong first chapter drive purchase.

### KPI expectations
Qualitative. Premium: completion rate, hint usage, review score, wishlist conversion and episode-to-episode retention for episodic games. Story-led titles depend heavily on critic and community praise.

### Retention drivers
Story and characters. Puzzle satisfaction. Choices and consequences. Episodic cliffhangers. Community discussion and streaming of branching outcomes.

### Content pipeline and production scope (estimates)
Scenes, characters, animation and voice acting are the cost. A small-team slice is 3–5 scenes and 10–15 puzzles. A full game is 40–100 scenes. Hand-drawn or 3D art both work. Puzzle design needs dependency-graph checks so the player is never stuck (`level-design`).

### Reference titles
- *Monkey Island* series (LucasArts): inventory puzzles with humour.
- *Day of the Tentacle* (LucasArts).
- *Grim Fandango* (LucasArts).
- *Broken Sword* series (Revolution Software).
- *The Walking Dead* (Telltale): choice-led episodic adventure.
- *Life is Strange* (Dontnod): choice-based adventure with rewind.
- *Disco Elysium* (ZA/UM): dialogue-led RPG adventure with a skill-voice system.
- *Return to Monkey Island* (Terrible Toybox).

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Puzzle logic is fair and the story pulls through | Obscure item-combining logic |
| Clear next-step cues (journal, hint) | Players stuck with no help |
| Characters and writing are distinctive | Generic dialogue |
| Good pacing: a puzzle, then story | Long dialogue or walk sections |
| Polished voice and audio | Weak voice acting |

### Innovation vectors
- Hybrids with investigation and deduction boards.
- Systemic puzzles with multiple solutions.
- Dialogue driven by state and memory.
- Adaptive hints from player progress data.
- Accessibility modes: hotspot highlight, auto-solve, text-to-speech.
- Short episodic releases.

### Agent-buildability: 3/5
**Why mid:**
- Puzzle dependency graphs, inventory logic and dialogue state are structured and testable. A solver can prove a game is completable.

**Why not higher:**
- Scene art, animation, voice and humour need human craft. Puzzle fairness needs playtests.

### Starter feature list (P0 vertical slice: three rooms, one chapter)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Scene loader with hotspots and walk areas (tech) | Click targets match hotspot data. Character paths avoid blocked areas |
| 2 | Inventory with use and combine (gameplay) | Combine table is data. Invalid combos give a hint line |
| 3 | Dialogue system with conditions (narrative) | Conditions read the state file. Graph walk shows no dead ends |
| 4 | Puzzle dependency graph with 8 puzzles (level) | Solver completes the chapter. No soft-lock state exists |
| 5 | Hotspot highlight key (ux) | Pressing the key shows all interactables in the scene |
| 6 | Hint system in three tiers (ux) | Each tier reveals more. Hint state persists per puzzle |
| 7 | Journal with objectives (ui) | Objectives update when puzzle flags change |
| 8 | Cutscene runner with skip (tech) | Skip lands on the same state as watching |
| 9 | Save, load and chapter select (tech) | Load restores inventory, flags and position |
| 10 | Subtitles, text size and voice-over hook (ux) | Settings persist. Subtitles track audio |

### Platform notes
- **PC.** Mouse is ideal for precise hotspots. Support keyboard and pad as options. Achievements and cloud saves are expected (`pc-web-release`).
- **Console.** A pad cursor needs snap-to-hotspot and radial menus. Cloud saves and trophies. Ratings and certification apply (`console-pathway`).
- **Web.** Fine for small adventures. Handle audio unlock and keep asset size small.
- **Mobile.** Touch suits adventures well, with tap-to-interact and hotspot highlight. Premium or episodic purchases on all platforms; mobile skews to lower prices.

## 6. Choice-based interactive fiction (Ink, Twine, Yarn Spinner)

### Definition and player fantasy
Mostly text, with choices as the main input. Sub-types: choose-your-own-adventure with branching text, hypertext pieces, dialogue-led RPG fragments and narrative layers embedded in larger games. The fantasy is *authorship through choice*: seeing how your decisions shape a character and a world.

### Core loop
```
read passage → choose an option (or pass a skill / state check)
  → state changes (stats, relationships, flags) → next passage → ending → replay
```

### Meta loops
- **Stats and qualities.** Hidden or visible numbers drive options.
- **Replay for other endings.**
- **Achievements and ending galleries.**
- **Serial or episodic release.**
- **Community jams and shared tools.**

### Session profile
Estimate: 10–40 minute sittings, stories of 1–8 hours. Frequent small choices. Players often replay for alternate paths.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Choices with conditions | narrative & dialogue | Show locked options with the reason, or hide them by design |
| Stat or skill checks | progression & upgrade | Show odds or make the check deterministic |
| Relationship and reputation tracking | narrative & dialogue | Keep to a few meaningful values (§0.3) |
| Storylets and quality-based narrative | narrative & dialogue | Content cards gated by state |
| Inventory or resource text mechanics | economy & resources | Light systems add tension |
| Save, back and history | UX automation | Rewind lowers regret |
| Dialogue runner embedded in a game | UX automation | Yarn Spinner and ink integrate with game engines |

### Tool choice
| Tool | Strength | Watch for |
|---|---|---|
| Ink (inkle) | Compact scripting with knots, weave, variables and lists. Runtime libraries for Unity and web. Good for large stories | Needs an integration layer in your engine |
| Yarn Spinner | Dialogue-first language with commands and functions. Plugins for Unity and Godot. Good for in-game dialogue | Less suited to freeform prose branches |
| Twine | Visual passage map. Exports HTML. Fast to prototype and publish on the web | Large stories get hard to manage. Weak built-in testing |
| Ren'Py | Full visual-novel engine with Python scripting | Heavier than text-only needs |
| Custom JSON format | Total control, verifiable | You build the tools |

Run the graph checks in §0.3 whatever the tool. For agent-built projects, prefer a text-based source format (ink, Yarn, Twee) over a binary editor file so diffs and tests work.

### Monetisation model and typical mix
Premium at a low price, pay-what-you-want on itch.io, ad-supported web versions, and free games as portfolio or jam entries. Longer commercial titles sell on Steam and mobile stores. Some sell as chapters. No loot boxes.

### KPI expectations
Qualitative. Premium: wishlist conversion, completion rate, review score and replay of alternate endings. Web: plays, completion and return visits. Word of mouth in interactive-fiction communities matters. Small niche, low costs.

### Retention drivers
Story quality and voice. Replay for endings. Consequences that show up later. Short, shareable pieces. Community events (jams).

### Content pipeline and production scope (estimates)
Writing dominates. A tight story of 30,000–60,000 words with 3–5 endings is a practical indie scope (estimate). A single writer can produce roughly 1,000–3,000 usable words a day, so 50,000 words is about 3–6 weeks of writing plus revision (estimate). Art is optional. Editing, proofreading and localisation are separate budgets.

### Reference titles
- *80 Days* (inkle): ink-powered travel story with a dynamic world.
- *Sorcery!* (inkle, Steve Jackson Games): interactive gamebook with a strategic map.
- *Heaven's Vault* (inkle): ink used inside an adventure.
- *Choice of Games* titles (ChoiceScript): text games with stats.
- *Fallen London* (Failbetter Games): quality-based storylets.
- *Disco Elysium* (ZA/UM): extreme dialogue and skill-check density.
- *Night in the Woods* (Infinite Fall): Yarn-based dialogue in a platform adventure.
- *Lifeline* (3 Minute Games): real-time text-message format (mobile).

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| A strong voice and clear stakes | Generic prose |
| Choices are distinct and consequences return | Illusory choices that all merge |
| The structure fits the scope | Tree explosion that the writer cannot finish |
| Easy-to-read UI and a history log | Walls of text with no formatting |
| Tested for dead ends | Broken variables and unreachable endings |

### Innovation vectors
- Visual graph tools plus a text source of truth.
- LLM-assisted drafting with human editing and strict guardrails (see `narrative-design`).
- Real-time or chat-style interaction.
- Generative storylets over a hand-authored core.
- Embedding in larger games (dialogue runners).
- Accessibility: screen-reader support, simple layouts.

### Agent-buildability: 5/5
**Why high:**
- The product is text plus state. Agents write, restructure, balance variables and verify graphs well.
- Tests can walk every path. Localisation pipelines are mechanical.

**What stays human:**
- Taste, voice and the decision of which themes to treat and how. Sensitive topics need human review.

### Starter feature list (P0 vertical slice: a 10,000-word story, three endings)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Story source in ink, Yarn or Twee under version control (tech) | Build compiles the source with no warnings. A CI step runs the compiler |
| 2 | State file with named variables and ranges (narrative) | Every variable declared. No undeclared reads |
| 3 | Branch-and-bottleneck structure with a map of scenes (narrative) | The graph shows no more than the planned branches. Every scene has an entry and an exit |
| 4 | Graph-walk test across all paths (qa) | All endings reachable. No dead ends. No always-false conditions |
| 5 | Seeded random-walk test of 10,000 playthroughs (qa) | Ending distribution report. No crash. Every ending hit at least once |
| 6 | Choice UI with locked-option reasons (ui) | Locked options show the reason when the design allows it |
| 7 | History log and back button (ux) | Back restores exact state. Log shows the last 50 passages |
| 8 | Save and autosave (tech) | Save restores story position and variables |
| 9 | Stats and relationships shown in a simple panel (ui) | Values update on change. Hidden values stay hidden |
| 10 | String export and pseudo-localisation (tech) | Stable IDs. Pseudo-localised build shows no clipping (§0.4) |
| 11 | Accessibility: font size, contrast, screen-reader labels (ux) | Settings persist. All choices have text labels |

### Platform notes
- **PC.** Windowed reading, keyboard shortcuts for choices, cloud saves, Steam or itch.io distribution. Easy to ship as an HTML build (`pc-web-release`).
- **Console.** Pad navigation for choices, large readable fonts at couch distance and rating forms. Smaller audience for pure text.
- **Web.** The natural home for Twine and ink web builds. Instant play, shareable links, local storage saves and ad or donation support.
- **Mobile.** Touch fits text well. See `narrative-rhythm-edu-kids.md` for mobile stories and monetisation. PC and web are low-price premium or free; mobile is episodic or ad-led.

## Volatile facts (as of Oct 2026 — verify before relying)

- Ren'Py's own download page listed version 8.5.3 as the current stable release, dated 15 May 2026 — [Ren'Py latest release](https://www.renpy.org/latest.html)
- The ink GitHub releases page marked version 1.2.1 as "Latest" (the page showed 05 May without a year, so the year is unverified) — [ink releases](https://github.com/inkle/ink/releases)
- The Yarn Spinner GitHub releases page marked v3.2.1 as the latest release (05 May shown, year unverified) — [Yarn Spinner releases](https://github.com/YarnSpinnerTool/YarnSpinner/releases)
- Steam charges a US$100 submission fee per product (Valve's onboarding page). The 30/25/20% revenue-share tiers at US$10 million and US$50 million are reported by secondary sources and should be checked in Steamworks — [Steamworks onboarding](https://partner.steamgames.com/doc/gettingstarted/onboarding), [Neowin](https://www.neowin.net/news/valve-introduces-new-revenue-share-tiers-for-steam-promising-bigger-cuts-for-studios/)
- Storefront rules on adult content, AI-generated assets and payment-processor limits change often and differ by store. Check each store's current content policy before committing a plan (`pc-web-release`, `console-pathway`).
- Pacing numbers, word counts, writing speeds and session lengths in this file are design estimates, not sourced figures.
- Loot-box regimes apply to any co-op horror cosmetic crates. Details: `skills/genre-playbooks/references/rpg-gacha.md` volatile facts.

## Related skills
- `mechanics-codex`: cards for every mechanic named above.
- `narrative-design`: branching craft, voice, structure and writing process.
- `audio-direction`: fear audio, mix and spatial sound.
- `audio-production`: recording, middleware and implementation.
- `accessibility-localization`: subtitles, text expansion, string pipelines and fonts.
- `level-design`: key-and-lock graphs, puzzle dependency and modular rooms.
- `game-feel`: camera, interaction feedback and response.
- `qa-testing`: graph walks, random walks and soak runs.
- `playtest`: tension traces and think-aloud sessions.
- `legal-ethics`: content ratings, loot boxes and asset licences.
- `platform-targets`: input, performance tiers and saves.
- `pc-web-release`: Steam, itch.io and web release steps.
- `console-pathway`: console programmes and ratings.
