# 10 — Narrative and Exploration Mechanics

Narrative and exploration mechanics turn story and space into things the player does rather than things the player watches: choosing what to say, deciding which branch to follow, pushing back fog, finding a secret, reading a room for what happened in it, walking to a real park to meet a creature. On mobile they must survive short sessions, sound-off play, small text, interruptions and a thumb that covers part of the screen, and they are the most expensive mechanics to test because state combinations explode. This file catalogues 20 mechanics in the shared mechanic-card format: dialogue choices, branching structures, storylets and swipe narratives, relationship meters, premium choices, progress-gated story, real-time messaging stories, narrative quest arcs, guidance and waypoints, fog of war, map reveal, ability gating, secrets, lore collectibles, environmental storytelling, deduction, time loops, expeditions, GPS location play and AR. Each entry gives precise rules, tuning ranges, dynamics, failure modes, a mobile verdict, the monetization hook with its ethical limit, and an implementation sketch. Writing craft (voice, character, tone bibles) belongs to `narrative-design`; spatial layout craft belongs to `level-design`; daily missions live in `missions-quests` (05).

**Entry format.** Every entry maps 1:1 onto `${CLAUDE_PLUGIN_ROOT}/scripts/schemas/mechanic-card.schema.json`. Ids are kebab-case; ids from sibling files carry their file number, e.g. `content-drip` (08). Aesthetic targets use the eight MDA aesthetics (Hunicke, LeBlanc and Zubek, 2004). Tuning ranges are practitioner starting points to be confirmed in playtests, not published benchmarks.

## Contents

1. Index of mechanics · 2. Choosing a narrative / exploration stack · 3. Choice and branching (10.01–10.07) · 4. Quests and guidance (10.08–10.09) · 5. Exploration and discovery (10.10–10.17) · 6. Away and real-world play (10.18–10.20) · 7. Narrative QA, platform notes and related skills

## 1. Index of mechanics

| # | Id | Mechanic | Primary job | One-hand | Session fit |
|---|---|---|---|---|---|
| 10.01 | `dialogue-choice` | Dialogue choices | Role-play through words | yes | 1–5 min scenes |
| 10.02 | `branching-narrative` | Branching structures | Consequence at story scale | yes | chapters |
| 10.03 | `storylets` | Storylets, quality-based narrative, swipe decisions | Emergent story from many small cards | yes | 2–5 min |
| 10.04 | `relationship-meters` | Relationship and affinity meters | Attachment to characters | yes | daily |
| 10.05 | `premium-choice` | Premium choices in episodic stories | Fantasy-fulfilment branches | yes | 10–20 min chapters |
| 10.06 | `progress-gated-story` | Story unlocked by progress | Story as reward schedule | yes | beats of 10–40 s |
| 10.07 | `realtime-narrative` | Real-time messaging stories | A character living alongside you | yes | 30 s bursts |
| 10.08 | `quest-arcs` | Narrative quest structures | Purpose with story consequence | mostly | 5–30 min |
| 10.09 | `waypoint-guidance` | Guidance and waypoints | Never lost, still discovering | yes | always on |
| 10.10 | `fog-of-war` | Fog of war | Play with imperfect information | yes | match |
| 10.11 | `map-reveal` | Map reveal and exploration progress | Cartographer's completion drive | yes | any |
| 10.12 | `ability-gating` | Ability-gated exploration | The world opens as you grow | needs controls | 10–30 min |
| 10.13 | `secrets` | Secrets and hidden areas | "I found what others missed" | yes | moments |
| 10.14 | `lore-collectibles` | Lore collectibles | Assemble the hidden history | yes | moments |
| 10.15 | `environmental-storytelling` | Environmental storytelling | The place tells what happened | yes | any |
| 10.16 | `deduction` | Deduction and investigation | Be the detective | mostly | 5–20 min |
| 10.17 | `time-loop` | Time loops and persistent knowledge | Knowledge as progression | depends | loop length |
| 10.18 | `expeditions` | Expeditions and idle exploration | Send explorers, read their stories | yes | async |
| 10.19 | `gps-location` | Location-based GPS play | The real world as the board | yes (walking) | 1–10 min |
| 10.20 | `ar-play` | AR placement and interaction | The game in your room | two-hand | 1–3 min |

## 2. Choosing a stack

| Concept type | Spine | Layers | Avoid |
|---|---|---|---|
| Casual puzzle with story | `progress-gated-story` | `dialogue-choice` (light), `lore-collectibles` | deep branching (content cost per level is too high) |
| Interactive fiction / visual novel | `branching-narrative` | `dialogue-choice`, `relationship-meters`, `premium-choice` (with limits) | fog, real-time action |
| Card / swipe narrative | `storylets` | `relationship-meters`, `time-loop` (meta across reigns) | long linear cutscenes |
| Action-adventure / metroidvania port | `ability-gating` | `map-reveal`, `secrets`, `lore-collectibles`, `environmental-storytelling` | `premium-choice` |
| Strategy / tactics | `fog-of-war` | `map-reveal`, `expeditions` | heavy dialogue |
| Mystery | `deduction` | `environmental-storytelling`, `lore-collectibles`, `dialogue-choice` | timers on reasoning |
| Location-based | `gps-location` | `map-reveal`, `ar-play` (optional), `expeditions` | content that requires dense cities only |

Mobile rule: every narrative beat must read with sound off, survive an interruption (resume to the same line), and fit a 1–5 minute session without losing the thread — keep a one-line recap for returns after 24 hours or more.

## 3. Choice and branching

### 10.01 Dialogue choices — `dialogue-choice`

- **Category:** narrative · player-voiced choice
- **Player fantasy:** "My words shape who I am and how others see me."
- **Core rules:**
  - *State:* dialogue graph of nodes `{id, speaker, text_key, conditions, effects}`; choice nodes list 2–4 options; variables (flags, affinity, tone counters).
  - *Triggers:* reaching a choice node; optional timer.
  - *Effects:* the chosen option sets variables, may trigger a skill check, and routes to the next node; options can be hidden, shown locked with a reason, or shown; a timer expiry picks a default (often silence).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Options per choice | 2–3 on phones (4 max) | More options = more expression, more reading on a small screen |
| Option length | ≤ ~40 characters, or a short tone label plus preview | Long options crowd the thumb zone |
| Timer | off, or 5–10 s | Timers add tension but hurt slow readers — make them optional |
| Flavour : consequential ratio | about 70 : 30 | All-consequential is unaffordable; all-flavour feels hollow |
| Acknowledgement delay | immediate nod plus a later payoff | Players need to see that a choice registered |

- **Dynamics:** role-play and self-expression; save-scumming for "best" answers; wiki-checking for romance or survival outcomes.
- **Aesthetic targets (MDA):** Narrative, Expression, Fantasy.
- **Feedback and juice:** portrait reaction on selection; affinity icons; Telltale-style "they'll remember this" notices for consequential picks.
- **Failure modes and exploits:** the illusion breaks when every option converges on the next line; option text that paraphrases badly (the spoken line is not what the player meant — a common criticism of Fallout 4's dialogue wheel); timers that exclude slow readers; walls of text.
- **Mobile fit:** options as large buttons in the bottom third; text size setting; auto-advance toggle; skip-seen-lines; resume mid-scene after interruption.
- **Monetization hooks and the ethical limit:** paid options belong in `premium-choice` and carry its limits.
- **Implementation notes:** author in an established narrative scripting tool (Ink by inkle and Yarn Spinner are widely used and open source); keep text as localisation keys; log every choice for analytics.

```text
show(node):
  render(node.speaker, loc(node.text_key)); apply(node.effects)
  if node.choices:
    opts = [c for c in node.choices if visible(c.cond)]          # hidden vs locked-with-reason is a per-option flag
    pick = await choose(opts, timeout=TIMER, default=node.default)
    apply(pick.effects); log("dialogue_choice", node.id, pick.id); goto(pick.next)
```
- **Reference games:** Mass Effect series, The Walking Dead (Telltale), Oxenfree, Disco Elysium, 80 Days.
- **Combines well with:** `branching-narrative`, `relationship-meters`, `premium-choice`, `deduction`.

### 10.02 Branching structures — `branching-narrative`

- **Category:** narrative · story graph architecture
- **Player fantasy:** "The story really went differently because of me."
- **Core rules:**
  - *State:* scene graph with conditions on variables; persistent variables carried across branches.
  - *Triggers:* choices and outcomes at branch points.
  - *Effects:* the story follows one edge; at bottlenecks paths rejoin but carried state alters later text, scenes and endings. Common patterns (summarised from Sam Kabo Ashwell's *Standard Patterns in Choice-Based Games*, 2015): the time cave (pure tree), the gauntlet (one path, side branches end early), branch-and-bottleneck (diverge, rejoin, track state), open map or quest hub, and sorting-hat (early choice selects a long route).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Pattern | branch-and-bottleneck for most commercial work | Linear content cost with felt consequence |
| Branch length before rejoin | 1–3 scenes | Longer = more distinct, more expensive |
| Endings | 2–6 | More endings = more replay, more QA |
| Unique content per playthrough | 60–80 % of a run is shared | Below ~60 % shared, cost explodes |
| Core tracked variables | ≤ 20 | Beyond this, testing every combination becomes infeasible |

  Cost maths: a pure tree with b options per choice and d choice depths has b^d leaves — 3 options × 5 depths = 243 endings. Branch-and-bottleneck grows roughly linearly with the number of branch points.
- **Dynamics:** replay to see other paths; community comparison; ending hunting.
- **Aesthetic targets (MDA):** Narrative, Discovery.
- **Feedback and juice:** chapter-end flowchart showing explored and locked paths, optionally with the share of players who chose each (Detroit: Become Human made this a signature).
- **Failure modes and exploits:** combinatorial explosion; untested paths with missing flags or softlocks; consequences too delayed or invisible to be felt; save-scumming that flattens tension.
- **Mobile fit:** episodic chapters of 10–20 minutes; autosave every scene; cloud save.
- **Monetization hooks and the ethical limit:** chapter passes or premium episodes. Paid content must not retroactively make free choices "wrong".
- **Implementation notes:** automated reachability tests over abstracted state; fail CI on unreachable scenes or dead ends.

```text
coverage(graph, start):
  frontier = [(start, initial_vars())]; seen = set()
  while frontier:
    node, vars = frontier.pop(); key = (node.id, abstract(vars)); if key in seen: continue; seen.add(key)
    if not node.edges and not node.is_ending: report("dead_end", node.id)
    for e in node.edges: if e.cond(vars): frontier.append((e.to, e.apply(vars)))
  report("unreachable", all_nodes - {k[0] for k in seen})
```
- **Reference games:** Detroit: Become Human, 80 Days, Life is Strange, The Witcher 3: Wild Hunt, Choices: Stories You Play.
- **Combines well with:** `dialogue-choice`, `storylets`, `time-loop`, `relationship-meters`.

### 10.03 Storylets, quality-based narrative and swipe decisions — `storylets`

- **Category:** narrative · emergent card-based structure
- **Player fantasy:** "My reign — my story — emerges from a thousand small decisions."
- **Core rules:**
  - *State:* qualities (numeric stats and flags); storylet pool `{id, requires(qualities), weight, effects, cooldown}`.
  - *Triggers:* draw the next storylet from the eligible pool; the player answers (in swipe form: left or right).
  - *Effects:* effects change qualities, unlock or lock storylets; in the swipe variant several meters must stay inside bounds — hitting 0 or max ends the run, and a meta layer carries over (Reigns uses four meters and a succession of rulers). The design approach is often called quality-based narrative (associated with Failbetter Games' *Fallen London*; Emily Short has written extensively on storylets).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Meters | 3–5 | More meters = harder balancing, more readable trade-offs per card |
| Effect size per answer | 5–20 % of the meter range | Larger swings shorten runs |
| Pool size | 150–1,000+ cards | Small pools repeat within hours |
| Repeat cooldown | 20–100 draws | Repetition is the main fatigue source |
| Unseen-card boost | 2–4× weight | Keeps discovery flowing |

- **Dynamics:** balancing act; emergent stories; dying as content; meta-progression across runs.
- **Aesthetic targets (MDA):** Narrative, Challenge, Discovery.
- **Feedback and juice:** during a partial swipe, preview which meters move (dot size for magnitude, not direction — Reigns' readable-but-uncertain cue); card flip and stamp on answer.
- **Failure modes and exploits:** repetition fatigue; incoherent sequences between cards; deaths that feel random when effects are fully hidden.
- **Mobile fit:** swipe is a perfect one-thumb verb; runs of 2–5 minutes.
- **Monetization hooks and the ethical limit:** extra lives or rewinds; cosmetic card backs. Never sell "insight" into hidden effects that makes the free game feel unfair.
- **Implementation notes:** salience-weighted selection; author storylets in a spreadsheet or Ink with requirement tags.

```text
next_card(q):
  eligible = [s for s in POOL if s.requires(q) and q.cooldown.get(s.id, 0) == 0]
  w = [s.weight * (BOOST if s.id not in q.seen else 1) * urgency(s, q) for s in eligible]
  return weighted_pick(eligible, w)
answer(s, side): apply(s.effects[side], q); q.cooldown[s.id] = COOLDOWN; if any(m <= 0 or m >= MAX for m in q.meters): end_run()
```
- **Reference games:** Reigns, Fallen London, King of Dragon Pass, Sunless Sea.
- **Combines well with:** `branching-narrative`, `relationship-meters`, `time-loop`.

### 10.04 Relationship and affinity meters — `relationship-meters`

- **Category:** narrative · character attachment track
- **Player fantasy:** "These people care about me, and I care about them."
- **Core rules:**
  - *State:* per-character affinity (0–100 or ranks 1–10); gift preferences; unlocked scenes.
  - *Triggers:* dialogue choices, gifts, shared activities, quests, time spent together.
  - *Effects:* affinity changes; thresholds unlock scenes, perks or abilities; optional exclusivity (one romance).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Gain per interaction | 1–10 % of a rank | Sets the weeks needed to max a character |
| Rank thresholds | 5–10 ranks | Each rank should unlock something visible |
| Gift multipliers | loved ×3, liked ×1, disliked −1× | Rewards learning a character |
| Daily cap | 1–2 gifts or talks per character | Prevents grinding one character in a day |
| Decay | none (preferred) / slow | Decay punishes absence |

- **Dynamics:** schedule planning (who to spend limited time with); favourite-character attachment; completionism across the cast.
- **Aesthetic targets (MDA):** Narrative, Fellowship (parasocial), Fantasy.
- **Feedback and juice:** heart burst; rank-up scene; characters referencing past choices.
- **Failure modes and exploits:** the "vending machine" feel (gift in, scene out); exploitative parasocial monetization (paid gifts to a virtual partner), especially toward minors; decay used as guilt.
- **Mobile fit:** daily check-in fits; one-tap gifting.
- **Monetization hooks and the ethical limit:** character-specific stories and cosmetic outfits. No romance-pressure monetization for minors; no guilt notifications ("she misses you"); affinity must be maxable without spending.
- **Implementation notes:** affinity as a progression track in `contract.json → progression.tracks`; unlock triggers data-driven.

```text
give_gift(p, npc, item):
  if p.gifts_today[npc] >= DAILY_CAP: return deny()
  m = PREFS[npc].get(item, 1); p.affinity[npc] = clamp(p.affinity[npc] + BASE_GIFT * m, 0, MAX)
  for t in THRESHOLDS[npc]: if p.affinity[npc] >= t.at and t.id not in p.unlocked: unlock_scene(p, t)
```
- **Reference games:** Persona 5 (Confidants), Stardew Valley (hearts), Fire Emblem: Three Houses (supports), Mystic Messenger, Genshin Impact (friendship level).
- **Combines well with:** `dialogue-choice`, `realtime-narrative`, `storylets`, `progress-gated-story`.

### 10.05 Premium choices in episodic stories — `premium-choice`

- **Category:** narrative · monetized branch
- **Player fantasy:** "I get to live the glamorous, romantic or daring version of the story."
- **Core rules:**
  - *State:* chapters gated by a regenerating key or ticket; premium options priced in premium currency; free currency drip per chapter.
  - *Triggers:* reaching a choice that includes a premium option; starting a chapter (spends a key).
  - *Effects:* premium option unlocks an outfit, a scene, an easier path or extra affinity; the free option always continues the story.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Premium options per chapter | 1–4 | More = more revenue moments, more resentment |
| What is paid | cosmetic / bonus scene / consequential | Consequential paid options are where ethics break |
| Free currency per chapter | enough for ~1 premium choice every 2–4 chapters | Lets free players taste premium content |
| Key regen | one per few hours, small cap | Paces binge reading; harsh caps break momentum |
| Price display | premium currency plus a real-money reference | Transparency builds trust |

- **Dynamics:** spending concentrates on favourite romance routes and outfits; players compare "what the paid scene showed".
- **Aesthetic targets (MDA):** Narrative, Fantasy, Expression.
- **Feedback and juice:** premium options styled distinctly (gem icon) but not pre-selected; payoff scene clearly richer.
- **Failure modes and exploits:** paywalled consequence (the free option gets a character killed or a route closed) — manipulative and widely resented; the key gate interrupting a cliffhanger; currency packs priced so one choice needs an awkward top-up.
- **Mobile fit:** native genre for phones — vertical framing, tap-to-advance, 10–20 minute chapters.
- **Monetization hooks and the ethical limit:** premium options and key refills. The free path must be narratively complete and never punished for not paying; no pre-selected paid option; no "last chance" countdowns on story choices; respect age ratings for romance content.
- **Implementation notes:** each option carries `cost` and a free `fallback_next`; track paid-choice take rate per chapter and churn after a declined paid choice (see `player-analytics`).

```text
on_choose(opt):
  if opt.cost and not try_spend(p, "gems", opt.cost): return offer_store(); # no auto-redirect to a purchase confirm
  log("premium_choice", chapter, opt.id, paid=bool(opt.cost)); goto(opt.next)
```
- **Reference games:** Choices: Stories You Play, Episode.
- **Combines well with:** `dialogue-choice`, `branching-narrative`, `relationship-meters`, `cosmetic-shop` (12).

### 10.06 Story unlocked by progress — `progress-gated-story`

- **Category:** narrative · reward schedule
- **Player fantasy:** "Every win moves my story forward."
- **Core rules:**
  - *State:* beat table `{beat_id, unlock {type: level|stars|chapter|collection, value}, media, length}`; seen flags.
  - *Triggers:* progress events (level cleared, stars spent, collection milestone).
  - *Effects:* the beat queues and plays at the next natural break (results screen, map), never mid-level; cliffhanger beats sit before known difficulty spikes to carry players through them.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Levels per beat | 5–15 (casual puzzle) | Sparser = players forget the plot |
| Beat length | 10–40 s | Longer beats need a skip and a recap |
| Cliffhanger placement | 1–3 levels before a hard level | Motivates pushing through a spike |
| Recap trigger | absence ≥ 24–72 h | Returning players regain the thread |
| Skip | always available after first view | Respects players who are here for the puzzle |

- **Dynamics:** story becomes a reason to clear hard levels; "what happens next" drives D7+ retention in story-meta casual games.
- **Aesthetic targets (MDA):** Narrative, Submission.
- **Feedback and juice:** "new story" badge on the map; character reactions on the results screen; chapter title cards.
- **Failure modes and exploits:** difficulty walls that block the story (offer a story recap or an alternative progress source); unskippable cutscenes; tone that does not match the core loop; story so thin players ignore it.
- **Mobile fit:** captions always on (sound-off play is common), portrait framing, beats under 40 s.
- **Monetization hooks and the ethical limit:** none directly — the story amplifies core-loop monetization. Never make a story beat purchasable "early" in a way that sells a skip over designed difficulty to minors.
- **Implementation notes:** beats are data; the presenter queues beats and drains them at safe states only.

```text
on_progress(evt): for b in BEATS if not seen(b) and b.unlock.type == evt.type and evt.value >= b.unlock.value: queue.append(b)
on_safe_state(): while queue: play(queue.pop(0)) ; mark_seen()
on_session_start(): if hours_since_last() >= RECAP_H: play(recap_for(current_chapter()))
```
- **Reference games:** Homescapes, Gardenscapes, Lily's Garden, Candy Crush Saga (map vignettes), Hades (story advancing across runs).
- **Combines well with:** `renovation-meta` (05), `chapters-worlds` (05), `quest-arcs`, `lore-collectibles`, `content-drip` (08).

### 10.07 Real-time messaging stories — `realtime-narrative`

- **Category:** narrative · real-time delivery
- **Player fantasy:** "A character is living alongside me, right now."
- **Core rules:**
  - *State:* script of message bursts with wait durations; scheduled timestamps; reply options.
  - *Triggers:* wall-clock time reaching the next burst; the player replying.
  - *Effects:* messages appear (with a notification if opted in); replies branch the script; the character goes "busy" for the next wait.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Wait durations | 1 min to several hours | Long waits = anticipation; too long = forgetting |
| Messages per burst | 3–12 | Burst length sets session length |
| Notifications | 0–4 per day, opt-in, quiet hours | More = intimacy, then fatigue |
| Catch-up / fast mode | available after first playthrough | Lets binge players move on |

- **Dynamics:** anticipation; appointment play; parasocial intimacy; players screenshot and share exchanges.
- **Aesthetic targets (MDA):** Narrative, Fantasy, Fellowship (parasocial).
- **Feedback and juice:** typing indicator, read receipts, timestamps, a notification styled like a real message.
- **Failure modes and exploits:** waits that feel artificial; notification fatigue; paid wait-skips becoming the main loop; device clock manipulation.
- **Mobile fit:** the phone is the diegetic device — the strongest form-factor match in this file.
- **Monetization hooks and the ethical limit:** wait skips and extra routes. Skips must be optional conveniences; no guilt framing ("I needed you and you weren't there"); honour quiet hours and OS notification settings.
- **Implementation notes:** schedule local notifications at burst times; on open, process all due bursts in order; handle time zones and daylight-saving shifts; validate time against the server.

```text
on_open(now): for burst in script.due(p.cursor, until=now): deliver(burst); p.cursor = burst.id
on_reply(opt): p.cursor = opt.next; nxt = script[opt.next]; schedule(nxt, at=now + nxt.wait, quiet_hours=p.quiet)
```
- **Reference games:** Lifeline, Mystic Messenger, Simulacra, Bury Me, My Love.
- **Combines well with:** `relationship-meters`, `dialogue-choice`, `timer-skips` (12).

## 4. Quests and guidance

### 10.08 Narrative quest structures — `quest-arcs`

- **Category:** narrative · goal structure with consequence (daily missions are `missions-quests` (05))
- **Player fantasy:** "I always have a purpose, and what I do changes the world."
- **Core rules:**
  - *State:* quest `{id, prereqs, stages[], objectives[], outcomes[], rewards}`; lifecycle locked → available → active → complete → claimed; active-quest cap.
  - *Triggers:* game events matching objective types (collect, defeat, reach, talk, craft, deliver, escort, survive); choices at outcome points.
  - *Effects:* objectives advance stages; outcome branches set world flags (NPC fate, area state) that later quests read; chains unlock follow-ups.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Active cap shown | 3–5 on phones | More = log bloat in portrait |
| Objectives per stage | 1–3 | More = errands |
| Stage length | 2–10 min | Fits sessions; long stages need mid-stage saves |
| Outcome branches | 1–3 per major quest | Each branch multiplies downstream QA |
| Archetype mix | ≤ 30 % pure fetch / kill | Variety is the antidote to fatigue |

- **Dynamics:** goal-directed play; "one more stage"; story told through doing; side quests as world-building.
- **Aesthetic targets (MDA):** Narrative, Challenge, Submission.
- **Feedback and juice:** tracker with stage progress; toasts on objective ticks; outcome callbacks later (an NPC you saved reappears).
- **Failure modes and exploits:** fetch fatigue; quests requiring a mode the player avoids (PvP); unclear destinations; outcomes nobody ever sees referenced; objective counters that miss events after an app kill.
- **Mobile fit:** many mobile RPGs add a one-tap "go" auto-navigation; useful for errands, harmful for exploration-led quests — make it optional.
- **Monetization hooks and the ethical limit:** quest skips and premium quest lines. Never put main-story quests behind purchase; premium side lines are fine when clearly labelled.
- **Implementation notes:** event-driven objective counters with idempotent event ids (no double counting on retries); persist progress per event.

```text
on_event(e):
  if e.id in p.processed: return; p.processed.add(e.id)
  for q in p.active: for o in q.stage.objectives:
    if o.matches(e): o.count = min(o.target, o.count + e.amount)
    if q.stage_done(): q.advance(); apply(q.stage.on_enter_effects)
```
- **Reference games:** The Witcher 3: Wild Hunt, The Elder Scrolls V: Skyrim (including procedurally generated "radiant" quests), World of Warcraft, Genshin Impact.
- **Combines well with:** `waypoint-guidance`, `progress-gated-story`, `branching-narrative`, `missions-quests` (05).

### 10.09 Guidance and waypoints — `waypoint-guidance`

- **Category:** exploration · navigation support
- **Player fantasy:** "I'm never lost — or I enjoy finding my way."
- **Core rules:**
  - *State:* current goal location(s); guidance layers enabled; idle timer.
  - *Triggers:* goal changes; player idle or circling; player opens the map.
  - *Effects:* escalate from diegetic cues (light, landmarks, painted ledges — the "yellow paint" convention) to HUD markers, compass pips, breadcrumb trails and finally explicit hints.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Soft-hint delay | 20–60 s idle or circling | Earlier = less frustration, less discovery |
| Explicit-hint delay | 90–180 s | Last resort before churn |
| Marker density | 1–3 visible goals | More = icon soup |
| Off-screen indicator | edge arrow with distance | Essential on small screens |
| Player control | guidance level setting (full / minimal / off) | Lets explorers opt out |

- **Dynamics:** balance between efficiency and discovery; players follow markers instead of looking at the world when markers are too strong.
- **Aesthetic targets (MDA):** Discovery (when restrained), Submission (smooth flow).
- **Feedback and juice:** soft pulse on the next interactable; camera nudge toward a landmark; brief arrival chime.
- **Failure modes and exploits:** markers that kill exploration; no guidance at all (silent churn); breadcrumbs through walls; hints that trigger during deliberate exploration.
- **Mobile fit:** short sessions mean returning players have forgotten the goal — show it on resume.
- **Monetization hooks and the ethical limit:** hint tokens in puzzle-adventure games. Free hints must exist on a timer; never hide basic navigation behind purchase.
- **Implementation notes:** escalation state machine; clamp off-screen markers to the screen edge.

```text
update(dt): idle = 0 if player_progressed() else idle + dt
  level = HINT_LEVELS.highest(lambda h: idle >= h.delay and h.enabled(settings))
  show(level, goal)
offscreen_marker(goal_screen_pos): d = normalize(goal_screen_pos - center); return clamp_to_rect(center + d * BIG, safe_rect)
```
- **Reference games:** The Legend of Zelda: Breath of the Wild (landmark-led), Dead Space (locator line), Fable II (breadcrumb trail), Uncharted series.
- **Combines well with:** `map-reveal`, `quest-arcs`, `secrets`.

## 5. Exploration and discovery

### 10.10 Fog of war — `fog-of-war`

- **Category:** exploration · information hiding
- **Player fantasy:** "I command with imperfect information."
- **Core rules:**
  - *State:* per-cell visibility: unexplored (black), explored (terrain remembered, no live units), visible (live); unit vision radii; blocking terrain.
  - *Triggers:* units move; vision changes (scouting, towers, abilities).
  - *Effects:* visible cells recomputed by line of sight; enemies show only in visible cells; last-known positions ghosted in explored cells.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Vision radius | 3–10 tiles | Small = ambush-heavy, tense; large = chess-like |
| Scout units / reveal abilities | 1–2 per side | Information becomes a resource to spend |
| Memory | terrain only / terrain + structures / ghosts | More memory reduces surprise |
| Elevation and blockers | on / off | Adds positional play |
| Partial information | sound pings, tracks | Lets players infer without seeing |

- **Dynamics:** scouting, ambushes, feints and bluffs; the information economy becomes part of strategy.
- **Aesthetic targets (MDA):** Challenge, Discovery.
- **Feedback and juice:** soft fog edges; reveal sweep animation; ghost icons for stale information.
- **Failure modes and exploits:** in multiplayer, clients that receive hidden data can map-hack (the server must not send it); per-frame line-of-sight on big maps kills frame time; single-player AI that "cheats" through fog feels unfair.
- **Mobile fit:** render fog as a low-resolution mask with bilinear upscale; update incrementally only when vision sources move.
- **Monetization hooks and the ethical limit:** none recommended in competitive modes — sold vision is pay-to-win.
- **Implementation notes:** recursive shadowcasting (a standard roguelike field-of-view algorithm) on a byte grid; server-side interest management decides which entities each client receives (see `multiplayer-backend`).

```text
recompute_vision(side):
  vis = zeros(W, H)
  for u in units[side]: shadowcast(u.pos, u.radius, blocks=opaque, mark=lambda c: vis.set(c, VISIBLE))
  explored |= vis; fog_mask.update_dirty(vis)
send_snapshot(client): entities = [e for e in world if vis[client.side][e.cell] == VISIBLE or e.side == client.side]
```
- **Reference games:** StarCraft, Civilization series, XCOM, The Battle of Polytopia.
- **Combines well with:** `map-reveal`, `secrets`, `expeditions`.

### 10.11 Map reveal and exploration progress — `map-reveal`

- **Category:** exploration · cartography and completion
- **Player fantasy:** "I'm the cartographer filling in the unknown."
- **Core rules:**
  - *State:* reveal mask; regions with completion %; points of interest (POIs) with discovered flags.
  - *Triggers:* visiting (reveal radius), climbing a viewpoint, buying or finding a map, clearing a level.
  - *Effects:* terrain revealed; POIs appear when discovered (or when revealed, by design choice); region completion rewards.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Reveal method | walk / viewpoint / purchase / level clear | Viewpoints are efficient; walking is personal |
| Reveal radius | 5–20 % of screen height | Larger = faster sweeping |
| POI density | one meaningful POI per 30–60 s of travel | Sparser = empty world; denser = checklist |
| POIs shown on reveal | terrain only vs all icons | Revealing icons converts exploration into chores |
| Completion rewards | at 50 / 100 % per region | Pulls completionists into corners |

- **Dynamics:** sweeping for completion; curiosity pulls toward unrevealed edges; checklist fatigue if icons dominate.
- **Aesthetic targets (MDA):** Discovery, Submission, Challenge.
- **Feedback and juice:** ink-spread reveal, region-complete stamp, compass rose animation.
- **Failure modes and exploits:** "icon soup"; viewpoints that remove all mystery (Breath of the Wild's towers reveal terrain but not shrines, a deliberate compromise); empty revealed spaces.
- **Mobile fit:** pinch-zoom map, large POI hit targets (≥ 44 pt), quick-travel to discovered points.
- **Monetization hooks and the ethical limit:** map packs or "treasure maps" revealing POIs. Fine as convenience; never hide required progression behind them.
- **Implementation notes:** reveal mask as a texture or bitset; completion = revealed cells ÷ region cells; POI discovery by proximity.

```text
on_move(pos): for c in disc(pos, REVEAL_R): if not revealed[c]: revealed[c] = 1; region_count[region_of(c)] += 1
  for poi in nearby(pos, DISCOVER_R): if not poi.found: poi.found = True; toast(poi)
completion(r) = region_count[r] / region_cells[r]
```
- **Reference games:** Assassin's Creed series (viewpoints), The Legend of Zelda: Breath of the Wild (towers), Hollow Knight (buying maps, updating them at benches), Civilization series.
- **Combines well with:** `fog-of-war`, `waypoint-guidance`, `lore-collectibles`, `gps-location`.

### 10.12 Ability-gated exploration — `ability-gating`

- **Category:** exploration · lock-and-key world structure
- **Player fantasy:** "The world opens up as I grow."
- **Core rules:**
  - *State:* world graph of areas connected by edges that require abilities or keys; acquired abilities; map markers for seen-but-locked edges.
  - *Triggers:* acquiring an ability (double jump, dash, swim, grapple) or key item.
  - *Effects:* previously blocked edges become traversable; backtracking opens shortcuts and optional areas.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Traversal abilities | 5–12 | Each must open several new paths to feel worth it |
| Backtrack distance to newly opened paths | 1–3 areas, with shortcuts | Long backtracks are padding |
| Locked-path signposting | visible obstacle + map marker | Players need to remember where to return |
| Sequence breaks | tolerated / designed / blocked | Tolerated breaks fuel speedrun communities |
| Optional-area share | 20–40 % of map | Rewards curiosity without bloating the critical path |

- **Dynamics:** mental-map building; the "aha" of remembering a locked door; sequence-break hunting.
- **Aesthetic targets (MDA):** Discovery, Challenge, Fantasy (growth).
- **Feedback and juice:** ability-get fanfare with a demo of what it opens; locked obstacles visually consistent per ability; map icons for known locks.
- **Failure modes and exploits:** softlocks (key placed behind its own lock, or a one-way drop into an area you cannot leave); aimless backtracking; obstacles whose required ability is unclear.
- **Mobile fit:** precise platforming on virtual controls is hard — simplify traversal verbs, add generous coyote time and controller support (see `11-mobile-input-control-schemes.md`).
- **Monetization hooks and the ethical limit:** premium ports sell the whole game. In F2P, never sell traversal abilities that gate the critical path.
- **Implementation notes:** verify the world graph with a progression solver in CI (reachability under acquired-ability sets).

```text
solve(world, start):
  have = set(); reach = flood(start, have)
  while True:
    new = {a for area in reach for a in area.pickups} - have
    if not new: break
    have |= new; reach = flood(start, have)
  assert all(a in reach for a in world.critical_areas), "softlock or unreachable critical area"
```
- **Reference games:** Super Metroid, Castlevania: Symphony of the Night, Hollow Knight, The Legend of Zelda series, Dead Cells.
- **Combines well with:** `map-reveal`, `secrets`, `lore-collectibles`.

### 10.13 Secrets and hidden areas — `secrets`

- **Category:** exploration · hidden reward
- **Player fantasy:** "I found something most people miss."
- **Core rules:**
  - *State:* secret registry `{id, area, trigger, reward, found}`; per-area counts.
  - *Triggers:* unusual actions — breaking a suspicious wall, going off-path, waiting, inputting a pattern, examining a detail.
  - *Effects:* hidden content opens (collectible, lore, shortcut, cosmetic, room); per-area "secrets found" increments.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Tell strength | subtle crack, sound cue, odd geometry | Strong tells feel fair; none feels like pixel hunting |
| Density | 1–3 per level or area | Too many = checklist |
| Reward type | lore, cosmetic, shortcut (not core power) | Power behind obscure secrets forces wikis |
| Count disclosure | show "2 / 3 found" after first clear | Turns secrets into an optional goal |
| Post-game hints | unlockable hint map | Lets completionists finish without wikis |

- **Dynamics:** community sharing; replay of levels; pride of discovery.
- **Aesthetic targets (MDA):** Discovery, Challenge.
- **Feedback and juice:** distinct discovery jingle; reveal camera beat; counter tick on the pause screen.
- **Failure modes and exploits:** essential content hidden; pixel hunting on small screens; tells that do not survive low-end graphics settings.
- **Mobile fit:** hidden interactables still need ≥ 44 pt hit areas; avoid secrets that depend on sound alone (many play muted).
- **Monetization hooks and the ethical limit:** none recommended; selling secret locations removes their value.
- **Implementation notes:** trigger volumes plus flags in the save; summarise found / total on the level-complete screen.

```text
on_trigger(s): if not p.secrets[s.id]: p.secrets[s.id] = True; grant(s.reward); play_jingle(); analytics("secret_found", s.id)
level_summary(level) = (sum(p.secrets[s] for s in SECRETS[level]), len(SECRETS[level]))
```
- **Reference games:** Super Mario Bros. (warp zones), Doom (secret areas), Fez, Hollow Knight.
- **Combines well with:** `lore-collectibles`, `ability-gating`, `collection-log` (09).

### 10.14 Lore collectibles — `lore-collectibles`

- **Category:** narrative · fragmentary storytelling
- **Player fantasy:** "I'm piecing together the true history."
- **Core rules:**
  - *State:* fragments `{id, set, order_hint, text_key, audio?}`; codex entries; collected flags.
  - *Triggers:* picking up a note, audio log, inscription or item description.
  - *Effects:* codex entry unlocks; completing a set reveals a meta-story, an epilogue or an alternate ending.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Fragment length | 60–120 words on phones | Longer becomes a wall of text |
| Fragments per area | 3–8 | Density versus clutter |
| Order | out of order, assembled in the codex | Assembly is part of the pleasure |
| Payoff | true ending, secret boss, epilogue | No payoff → collection fatigue |
| Audio version | optional voiced logs | Lets players listen while moving |

- **Dynamics:** theory-crafting communities (item-description lore is a famous example in Dark Souls); re-reading after new finds.
- **Aesthetic targets (MDA):** Narrative, Discovery, Submission.
- **Feedback and juice:** codex "new" badge; set progress; voiced logs keep playing while the player continues.
- **Failure modes and exploits:** critical plot locked in optional logs; collectible fatigue; unreadable text sizes.
- **Mobile fit:** short fragments, adjustable text, audio logs that continue during play.
- **Monetization hooks and the ethical limit:** lore books or artbooks as cosmetic DLC; never sell missing fragments of a free set.
- **Implementation notes:** codex entries keyed to localisation; track read state for "unread" badges.

```text
collect(f): p.lore.add(f.id); unlock_codex(f); s = f.set
  if all(x in p.lore for x in SETS[s]): grant(SET_PAYOFF[s]); analytics("lore_set_complete", s)
```
- **Reference games:** BioShock (audio diaries), Dark Souls series (item descriptions), Hollow Knight, Destiny (Grimoire cards).
- **Combines well with:** `secrets`, `environmental-storytelling`, `collection-log` (09).

### 10.15 Environmental storytelling — `environmental-storytelling`

- **Category:** narrative · spatial inference
- **Player fantasy:** "The place itself tells me what happened here."
- **Core rules:**
  - *State:* authored vignettes (arranged props, damage, bodies, notes, light); optional inspectable hotspots; seen flags.
  - *Triggers:* entering a space; inspecting a hotspot.
  - *Effects:* the player infers events; inspecting adds detail (text, voice-over, zoom); some vignettes feed deduction or quest outcomes.
- **Theory:** Henry Jenkins (*Game Design as Narrative Architecture*, 2004) distinguishes embedded narrative (story placed into the space for players to uncover) from emergent narrative; Harvey Smith and Matthias Worch's GDC 2010 talk on environmental storytelling framed it as "what happened here?" inference built from staged scenes.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Vignette density | 1 per room or screen in narrative spaces | Too sparse = generic; too dense = museum |
| Explicitness | implicit / one hotspot / labelled | Implicit is elegant but easy to miss on phones |
| Inspect zoom | 1.5–3× with rotation | Lets small screens show detail |
| Audio support | ambient cue or line on inspect | Helps comprehension; captions required |

- **Dynamics:** inference and re-reading spaces; community interpretation.
- **Aesthetic targets (MDA):** Narrative, Discovery, Fantasy.
- **Feedback and juice:** subtle highlight on hotspots after a delay; camera framing that leads the eye.
- **Failure modes and exploits:** details too small on phones; art cost per vignette; spaces that contradict what gameplay asks of the player.
- **Mobile fit:** tap-to-inspect hotspots with zoom; readable silhouettes over fine texture detail.
- **Monetization hooks and the ethical limit:** none direct.
- **Implementation notes:** vignettes as prefabs or scenes with inspect points; track which were seen to tune density.

```text
on_inspect(h): open_inspect(h.model, zoom=h.zoom); show(loc(h.text_key)); if h.vo: play(h.vo, captions=True)
  p.seen_vignettes.add(h.vignette); if h.clue: add_clue(p, h.clue)     # feeds `deduction`
```
- **Reference games:** Gone Home, What Remains of Edith Finch, BioShock, the Fallout series, Monument Valley.
- **Combines well with:** `lore-collectibles`, `deduction`, `secrets`.

### 10.16 Deduction and investigation — `deduction`

- **Category:** narrative · reasoning puzzle
- **Player fantasy:** "I'm the detective who figures it out."
- **Core rules:**
  - *State:* clues collected; facts to determine (who, how, why, by whom); player hypotheses; locked confirmations.
  - *Triggers:* collecting clues; filling a hypothesis (fill-in-the-blank, link-on-board, accuse, or search query).
  - *Effects:* correct hypotheses confirm only in batches (Return of the Obra Dinn confirms fates three at a time) to defeat brute force; wrong accusations cost something (lives, reputation) or simply do not confirm.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Batch confirmation size | 2–3 facts | Smaller = brute-forceable; larger = feedback too rare |
| Clue redundancy | ≥ 2 independent clue paths per fact | One obscure clue gating progress is the classic failure |
| Wrong-answer penalty | none / soft / lives | Penalties curb guessing but punish honest mistakes |
| Hint system | after N failed attempts | Prevents walkthrough churn |
| Interface | fill-in / board / query search | Search (Her Story) is powerful but typing-heavy on phones |

- **Dynamics:** note-taking; community theorising; the "aha" cascade when one fact unlocks others.
- **Aesthetic targets (MDA):** Challenge, Discovery, Narrative.
- **Feedback and juice:** confirmation stamp when a batch locks in; board threads snapping between clues.
- **Failure modes and exploits:** brute-force guessing; a single obscure clue blocking progress; text-heavy clue review on small screens.
- **Mobile fit:** drag-to-link boards and pick-lists suit touch; avoid free-text typing as the only input.
- **Monetization hooks and the ethical limit:** hint tokens or case packs. Free timed hints must exist.
- **Implementation notes:** validate that each fact has at least two clue paths; batch-lock logic.

```text
submit(answers):
  correct = [f for f, a in answers.items() if a == TRUTH[f] and f not in p.locked]
  if len(correct) >= BATCH: lock(correct[:BATCH * (len(correct) // BATCH)]); celebrate()
lint_case(): for f in FACTS: assert len(clue_paths(f)) >= 2, f"fact {f} has a single point of failure"
```
- **Reference games:** Return of the Obra Dinn, Her Story, Ace Attorney series, L.A. Noire, The Case of the Golden Idol.
- **Combines well with:** `environmental-storytelling`, `lore-collectibles`, `dialogue-choice`.

### 10.17 Time loops and persistent knowledge — `time-loop`

- **Category:** narrative · knowledge-as-progression
- **Player fantasy:** "I'm the only one who remembers — and knowledge is my power."
- **Core rules:**
  - *State:* loop clock; deterministic world schedule; persistent knowledge flags (and sometimes a few persistent unlocks); loop-local state.
  - *Triggers:* loop timer expires or the player dies.
  - *Effects:* loop-local state resets; knowledge persists; new knowledge opens new actions in the next loop; a log records discoveries.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Loop length | 5–25 min (Outer Wilds uses about 22) | On phones 5–10 min matches sessions |
| What persists | knowledge only / some items / shortcuts | More persistence = less replay tedium, less purity |
| Schedule determinism | fully fixed / fixed with variants | Fixed schedules make knowledge reliable |
| Discovery log | automatic rumour map | Prevents forgetting between sessions |
| Fast-forward | wait / sleep to a time | Removes dead time waiting for events |

- **Dynamics:** route planning; fearless experimentation; layered understanding of one place.
- **Aesthetic targets (MDA):** Discovery, Narrative, Challenge.
- **Feedback and juice:** loop-reset ritual (same sound, same opening shot); log entries lighting up connections.
- **Failure modes and exploits:** repetition fatigue; missing a timed event forces a long wait; players forgetting clues between sessions.
- **Mobile fit:** short loops; save mid-loop on interruption; strong discovery log.
- **Monetization hooks and the ethical limit:** premium purchase fits best; avoid selling loop extensions or knowledge.
- **Implementation notes:** separate persistent and loop saves; the world scheduler is a pure function of loop time.

```text
world_state(t) = SCHEDULE.events_until(t)          # deterministic: same t, same world
on_loop_end(): p.loop = fresh_loop_state(); p.loops += 1; save(p.persistent)   # knowledge flags survive
can_do(action) = action.requires_knowledge <= p.persistent.knowledge
```
- **Reference games:** Outer Wilds, The Legend of Zelda: Majora's Mask, Deathloop, Returnal, Hades.
- **Combines well with:** `storylets`, `deduction`, `lore-collectibles`.

## 6. Away and real-world play

### 10.18 Expeditions and idle exploration — `expeditions`

- **Category:** exploration · asynchronous dispatch (idle accumulation is `idle-accumulation` (08))
- **Player fantasy:** "I send my explorers out, and they come back with loot and stories."
- **Core rules:**
  - *State:* expedition slots; destinations `{duration, requirement, risk, reward_table, vignettes}`; assigned units become unavailable.
  - *Triggers:* dispatch; timer completion; player claims.
  - *Effects:* success probability from party power versus requirement; rewards and a short text vignette; optional injuries or rare finds; new destinations revealed.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Duration | 15 min to 24 h | Sets check-in cadence |
| Success curve | sigmoid of (power − requirement) | Steep = binary; gentle = risk management |
| Reward per hour | longer expeditions slightly lower per hour, higher per check-in | Mirrors crop maths in `farming-cycle` (09) |
| Concurrent slots | 1–5 | Roster depth matters more with more slots |
| Failure cost | none / injury timer / unit loss | Unit loss is harsh on mobile; prefer injuries |

- **Dynamics:** roster management; appointment play; vignettes give otherwise idle units personality.
- **Aesthetic targets (MDA):** Narrative, Submission, Discovery.
- **Feedback and juice:** return animation; vignette card ("Mira found a sealed door…"); loot reveal.
- **Failure modes and exploits:** zero agency (fix with route or risk choices); one best roster dominates; save-scumming results.
- **Mobile fit:** excellent — dispatch and claim in seconds.
- **Monetization hooks and the ethical limit:** extra slots and speed-ups. Expedition loot that is random and bought with premium speed-ups still needs disclosed odds if it can be purchased.
- **Implementation notes:** roll the outcome at dispatch with a seeded RNG (prevents save-scumming), reveal at claim.

```text
dispatch(team, dest): p_succ = 1 / (1 + exp(-K * (power(team) - dest.req)))
  outcome = roll(seed=hash(p.id, dest.id, p.dispatch_count), p_succ, dest.reward_table)
  p.expeditions.append(Expedition(team, dest, end=now + dest.duration, outcome=outcome))
```
- **Reference games:** Fallout Shelter (wasteland exploration), Genshin Impact (expeditions), World of Warcraft (garrison missions).
- **Combines well with:** `map-reveal`, `storylets`, `creature-collection` (09).

### 10.19 Location-based GPS play — `gps-location`

- **Category:** exploration · real-world map
- **Player fantasy:** "My real world is the game board."
- **Core rules:**
  - *State:* real-world map tiles; POIs (stops, gyms, portals) at real coordinates; spawns per spatial cell and time slot; player position, speed and accuracy.
  - *Triggers:* position updates; entering a POI's interaction radius; walking distance accrual.
  - *Effects:* encounters and POI interactions within range; distance credits (egg hatching, buddy rewards); co-located group content (raids).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Interaction radius | 20–80 m | Larger helps rural, accessibility and GPS jitter; smaller rewards walking |
| Spawn density by area type | boosted in low-density areas | Rural fairness is the genre's chronic problem |
| Distance-credit speed cap | 10–20 km/h | Discourages playing while driving |
| GPS jitter filter | ignore moves smaller than reported accuracy | Stops "drift walking" exploits and false credit |
| POI cooldown | 3–10 min | Paces POI farming |

- **Dynamics:** walking and exploring; social meet-ups; local communities; location spoofing.
- **Aesthetic targets (MDA):** Discovery, Fellowship, Fantasy.
- **Feedback and juice:** haptic buzz when something is nearby (lets players keep the phone pocketed); map pulse; POI photo cards.
- **Failure modes and exploits:** GPS spoofing; rural content deserts; safety (traffic, trespass — show warnings and lock interactions above the speed cap); POIs placed at private homes, memorials or other sensitive sites; battery drain.
- **Mobile fit:** walking one-hand play in 1–10 minute bursts; background step or distance tracking requires careful permission design.
- **Monetization hooks and the ethical limit:** lures, incubators, raid passes, remote-play passes. Remote options keep the game accessible to players who cannot walk far; never sell spoofing-like advantages.
- **Implementation notes:** seed spawns by (spatial cell, time slot) using a spatial index such as S2 cells or geohashes so co-located players see the same world; validate movement server-side.

```text
on_fix(fix):
  if fix.accuracy_m > MAX_ACC: return                       # discard poor fixes
  d = haversine(p.last, fix); v = d / (fix.t - p.last.t)
  if d >= fix.accuracy_m and v <= SPEED_CAP: p.distance += d
  p.last = fix; cell = cell_id(fix, LEVEL); spawns = spawn_table(cell, slot(fix.t))
```
- **Reference games:** Pokémon GO, Ingress, Pikmin Bloom, Monster Hunter Now.
- **Combines well with:** `map-reveal`, `creature-collection` (09), `ar-play`, `limited-time-events` (08).

### 10.20 AR placement and interaction — `ar-play`

- **Category:** exploration · camera-world overlay
- **Player fantasy:** "The game is happening right here — in my room, on my street."
- **Core rules:**
  - *State:* AR session state (initialising, scanning, placed, tracking-limited, lost); anchors; placed content.
  - *Triggers:* plane detected; player taps to place; tracking quality changes.
  - *Effects:* content anchored to the real world; interactions by tap, throw or walking around it; on tracking loss, pause and guide re-scan; non-AR fallback always available.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| AR segment length | 1–3 min | Arm fatigue, heat and battery limit longer segments |
| Placement scale | real-world scale vs tabletop | Real scale is impressive but needs space |
| Tracking-loss grace | 1–3 s before pausing | Avoids flicker-pauses |
| Occlusion and lighting estimation | on capable devices only | Realism versus device coverage |
| Fallback | 3D backdrop mode | Mandatory for unsupported devices and for comfort |

- **Dynamics:** spectacle and social sharing (AR photos); short special moments rather than a whole loop.
- **Aesthetic targets (MDA):** Sensation, Fantasy, Fellowship (shared photos).
- **Feedback and juice:** scanning guidance animation; placement reticle; photo mode with share.
- **Failure modes and exploits:** "gorilla arm" fatigue; heat and battery; walking while looking at the camera; unsupported devices; camera privacy concerns. Whole-game AR has a poor track record (Minecraft Earth shut down in 2021); AR works best as an optional layer.
- **Mobile fit:** two-handed and short; never require AR for progression.
- **Monetization hooks and the ethical limit:** AR photo frames and cosmetics. Never send camera frames off-device without explicit consent.
- **Implementation notes:** ARKit (iOS) and ARCore (Android) underpin mobile AR; Unity wraps both in its AR Foundation package; check current Godot support before committing (mobile AR there has relied on plugins). Treat AR as a presentation mode over the same sim state.

```text
ar_state machine: INIT -> SCANNING -(plane found)-> READY -(tap)-> PLACED -(tracking limited > GRACE)-> PAUSED_RESCAN
  any -(user toggle or unsupported)-> FALLBACK_3D        # identical sim, different camera and backdrop
```
- **Reference games:** Pokémon GO (AR and AR+ modes), Minecraft Earth (discontinued), Pikmin Bloom.
- **Combines well with:** `gps-location`, `virtual-pet` (09), `environmental-storytelling`.

## 7. Narrative QA, platform notes and related skills

- [ ] Reachability test over every story graph: no dead ends, no unreachable scenes, every ending reachable (`branching-narrative` sketch); world graphs pass the `ability-gating` solver.
- [ ] Every beat readable with sound off (captions), resumable after interruption, recap after 24 h+.
- [ ] Every deduction fact has ≥ 2 clue paths; every secret has a fair tell.
- [ ] No paid option makes the free path punitive; no guilt notifications; quiet hours honoured.
- [ ] GPS: speed cap, jitter filter, server-side validation, sensitive-POI removal flow, non-walking accessibility options.
- [ ] Telemetry: `dialogue_choice`, `story_beat_seen`, `quest_stage`, `secret_found`, `area_revealed`, `poi_interact` in the taxonomy (`player-analytics`).

**Platform notes (as of Oct 2026 — verify before relying):**
- Under the US COPPA Rule, geolocation precise enough to identify a street name and city counts as children's personal information, and the amended Rule's compliance deadline was 22 April 2026 — [16 CFR 312.2](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-C/part-312); [Toy Association](https://toyassociation.org/PressRoom2/News/2026-News/updated-coppa-rule-requirements-take-effect-april-22.aspx).
- Apple's App Review Guidelines (5.1.1 and 5.1.2) govern permission requests and data use; request location only for the features that need it, with a clear purpose string — [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/).
- Mobile AR platforms: [ARKit](https://developer.apple.com/augmented-reality/arkit/) and [ARCore](https://developers.google.com/ar).

**Related skills:** `narrative-design` (writing craft, tone bible), `level-design` (spaces, pacing, signposting), `player-psychology` (curiosity, attachment), `qa-testing` (graph reachability, playthroughs), `accessibility-localization` (text size, captions, string length), `legal-ethics` (location data, minors).
