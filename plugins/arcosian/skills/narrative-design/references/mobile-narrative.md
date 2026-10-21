# Mobile Narrative: Meta-Stories, Episodes, Retention and Marketing

On phones, narrative rarely *is* the game; it is the reason the game matters — the "why" behind the levels, the reward the player sees between them, the characters they come back for, and the face of the game in ads and on the store. This file covers the four jobs of mobile narrative and the five ambition levels; the renovation/meta-story pattern popularised by Gardenscapes and Homescapes with its content mathematics; character-led casual design; short-form, episodic and serial storytelling for 1–5 minute sessions; narrative as a retention mechanism (with honest psychology and a measurement plan); narrative as marketing (UA creatives, store, community, push) and the misleading-ad line; narrative in the FTUE; a genre-by-genre table; the production pipeline including AI-assisted drafting; and two worked examples. Mechanic cards for progress-gated story, premium choices and real-time messaging stories live in `skills/mechanics-codex/references/10-narrative-exploration-mechanics.md`; deconstructions of Homescapes, Royal Match, Merge Mansion and Episode/Choices live in `game-case-studies`.

## Contents

1. The four jobs of mobile narrative
2. Choosing a narrative ambition level
3. The renovation / meta-story pattern
4. Character-led casual design
5. Short-form, episodic and serial storytelling
6. Narrative as retention — mechanisms and measurement
7. Narrative as marketing
8. Narrative in the FTUE
9. Narrative by mobile genre
10. Production pipeline (including AI-assisted drafting)
11. Worked example A — adding a meta-story to a sort puzzle
12. Worked example B — a season narrative for a hybrid-casual game
13. Checklists

---

## 1. The four jobs of mobile narrative

| Job | What it gives the player | Design lever | Evidence it works (measure) |
|---|---|---|---|
| **Context** — why am I doing this? | Purpose for repetitive play | Premise, goals framed in the fiction, task names | Fewer early "what do I do?" drop-offs; tutorial completion |
| **Reward** — something worth earning | Story beats and visible change as payoff for effort | Progress-gated beats, before/after renovation, character reactions | Beat view rates; progression after beat unlocks |
| **Retention** — a reason to come back | Curiosity, attachment, open loops, routine | Cliffhangers, mystery spine, character arcs, chapter cadence | Holdout tests (§6.4); chapter funnel |
| **Marketing** — a face and a hook | Recognisable characters and dramatic situations for ads, store and social | IP-ready cast, ad-friendly premises, shareable moments | Creative CTR/IPM by narrative concept; organic share (via `marketing-ua`) |

A narrative feature that does none of these four jobs is decoration — cut it or redesign it.

---

## 2. Choosing a narrative ambition level

| Level | Name | What exists | Writing volume (order of magnitude) | Typical genres | Main risk |
|---|---|---|---|---|---|
| **L0** | Premise only | A one-line situation and a look | < 100 words | Hypercasual, pure arcade | None — but no retention help from story |
| **L1** | Flavour | Mascot, item/level names, barks, results-screen reactions | Hundreds to a few thousand words | Hybrid-casual, puzzle, idle | Inconsistent tone across surfaces |
| **L2** | Meta-story | Linear micro-scenes gated by progress, a cast of 3–7, a mystery or goal spine | ~5,000–50,000 words per year of content | Match-3, merge, sort, word, renovation metas | Story pace outrun by fast players; art cost of renovation |
| **L3** | Story-led | Chapters with choices, relationships, routes, events with stories | 50,000–500,000+ words | Story apps, gacha/RPG story modes, narrative sims | Writing pipeline throughput; localisation cost; QA of branches |
| **L4** | Narrative game | Story is the core loop; interaction is storytelling | Varies widely; quality > volume | Premium narrative (*Florence*-style), interactive fiction | Small market per title; premium pricing on mobile |

Volumes are rough orders of magnitude for planning, not benchmarks. **Decide the level in the concept phase** and record it in the contract (see SKILL.md "Using the ontology"). Most F2P casual games should target L1–L2; moving from L2 to L3 multiplies writing, localisation, QA and art by an order of magnitude.

---

## 3. The renovation / meta-story pattern

### 3.1 Lineage

Playrix's *Gardenscapes: New Acres* (2016) and *Homescapes* (2017) established "match-3 + renovation + story" as a dominant casual meta: stars won in levels are spent on story tasks, each task advances a short scripted scene and changes the visible space, and finished areas open new chapters. *Lily's Garden* leaned into drama and romance; *Royal Match* (Dream Games, 2021) kept the renovation loop but made story light, with King Robert as a mascot rather than a narrator; *Merge Mansion* (Metacore, c. 2020) moved the formula onto a merge board with a mystery about the protagonist's grandmother; hidden-object metas such as *June's Journey* (Wooga) used a period mystery as the spine. Deconstructions with ontology encodings are in `skills/game-case-studies/references/puzzle-casual.md` and `skills/game-case-studies/references/casual-social-sim.md`.

### 3.2 Anatomy

```
win level → earn star(s) → pick story task (costs 1–3 stars) → micro-scene (2–6 lines)
         → visible change (repair/decorate; often a 3-option décor choice) → next task appears
         → area complete → chapter beat + reward → new area opens (new characters, new mystery thread)
```

| Element | Starting range | Design note |
|---|---|---|
| Task cost | 1–3 stars | Cheap first tasks in each area; costlier "big reveal" tasks at area end |
| Micro-scene length | 2–6 lines, ≤ 90 chars per line | Readable in ~10–30 s; skippable |
| Tasks per area | 8–20 | One sequence (`references/story-structures.md` §3.3) per area |
| Décor choice | 3 options, cosmetic | Expressive choice; persistent; changeable later |
| Area-end beat | 20–60 s | The area's mini-climax and turn |
| Recap | After 24–72 h absence | One card, ≤ 160 chars |

### 3.3 Writing the micro-scene

1. **Set up the change, let the art pay it off.** Dialogue introduces the problem ("The stairs are a death trap"); the renovation animation is the punchline. Never describe in text what the player is about to see.
2. **Kishōtenketsu in four lines** (`references/story-structures.md` §4) is the default shape: situation, development, twist, landing.
3. **End with an open micro-loop** every second or third scene: a found object, an overheard line, a character exit.
4. **Callbacks over exposition.** Reference earlier tasks and décor choices ("Still can't believe you picked the purple sofa").
5. **Comedy carries the cadence; sincerity carries the chapter.** Most scenes light, one sincere beat per area end.
6. **Task names are verbs + objects, ≤ 28 characters:** "Fix the dock crane", "Hang Eda's portrait".
7. **No literal causation claims** between puzzles and repairs (the abstraction contract, `references/story-structures.md` §7.4).

### 3.4 Content mathematics

The story is a reward schedule, so plan it like an economy (`economy-design`). Parameters for a target player segment:

```
W  = level wins per day (segment-specific; measure in playtests / soft launch)
S  = stars per win (often 1)
C  = average star cost per task
T  = tasks per day          = W × S / C
A  = tasks per area
D_area = days per area      = A / T
D_story = days of story runway = (total tasks) / T
words_per_day = T × lines_per_scene × words_per_line
```

**Worked example (hypothetical parameters):** a fast segment wins W = 12 levels/day, S = 1, C = 2 → T = 6 tasks/day. With A = 15, an area lasts 2.5 days. A 90-day runway for this fast segment needs 6 × 90 = 540 tasks ≈ 36 areas. Writing: 540 scenes × 4 lines × 11 words ≈ 24,000 words — modest. Art: 540 tasks, many with 3 décor options, is the real bottleneck. **Design the runway for the fastest decile of players**, because they hit the story wall first, and plan what happens at the wall (events, side content, "new chapter coming" with a date only if the date is certain).

### 3.5 Pacing against difficulty

- Place cliffhanger beats 1–3 levels **before** known hard levels (motivation to push through) and generous, warm beats **after** them (relief), consistent with the `progress-gated-story` mechanic card.
- Never block the story behind a level the player cannot pass without paying; offer an alternative progress source or a story recap path.
- Story losses (storms, sabotage) are narrative only — never remove renovated rooms or purchased items.

### 3.6 Variants

| Variant | Spine | Example games | Note |
|---|---|---|---|
| Renovation + drama | Personal/relationship drama | *Lily's Garden* | Higher writing ambition; romance must fit the rating |
| Renovation + mascot | Light comedy, mascot personality | *Royal Match* | Story minimal; progress feedback carries the meta |
| Construction + conflict | Antagonist to defeat | *Royal Kingdom* (per case study) | A villain gives progress direction |
| Merge + mystery | Mystery reveal schedule | *Merge Mansion* | Mystery doubles as the marketing hook |
| Client of the week | Episodic makeovers/requests | Makeover metas (e.g. *Project Makeover*) | Each client is a self-contained arc; easy to scale with events |
| Hidden object + period mystery | Serial detective story | *June's Journey* | Scenes double as environmental storytelling |

---

## 4. Character-led casual design

In casual games the character often carries more of the narrative load than the plot does.

| Role | Job | Rules |
|---|---|---|
| **Mascot** (Austin the butler, King Robert, Om Nom) | Brand face; reacts to play; appears in ads and icon | Simple silhouette; one behaviour rule; flat arc; expressive without words |
| **Guide** | FTUE teacher; explains new mechanics in character | Short lines; never condescending; fades after onboarding |
| **Client / requester** | Generates goals with personality | Each request reveals something about the requester |
| **Protagonist** | The person whose story the meta tells | Likeable within 30 seconds; has a want visible on screen |
| **Antagonist** | Gives progress direction | Comic menace for casual; sympathetic motive revealed later |

**Personality through reaction, not exposition.** The cheapest high-impact narrative feature in a casual game is the **results-screen reaction**: the mascot celebrates a close win differently from an easy one, consoles a loss, notices a streak. One animation set plus a bark pool (`references/dialogue-and-branching.md` §10) delivers character every session.

**Character-in-peril framing** ("save the character") is a widely used casual premise and ad format. Use it with care: if the game shows it, the game must contain it; keep peril cartoonish for broad audiences; and never connect the character's peril to a purchase prompt.

---

## 5. Short-form, episodic and serial storytelling

### 5.1 Session-native story units

| Unit | Length | Contains | Ends with |
|---|---|---|---|
| Beat | 10–40 s | One change (a reveal, a reaction, a joke) | A micro-hook or a landing |
| Scene / task | 30 s – 2 min | 2–6 beats around one value shift | A visible change or a question |
| Episode / chapter | 5–20 min of story spread over sessions | A local goal, a mini-climax, a turn | A cliffhanger or a satisfying close with a new question |
| Arc / season | Weeks | 4–8 episodes building to a finale | Macro reveal + the next macro question |

### 5.2 Micro-episode anatomy (for 1–5 minute sessions)

```
Cold open (≤ 5 s)   — a striking image or line that restates the open question
Beat 1              — situation develops
Beat 2              — turn (surprise, reveal, complication)
Play                — the levels / tasks (story pauses; it never interrupts a level)
Landing (≤ 20 s)    — consequence of the turn, a laugh or a sincere moment
Hook                — a new micro-question for the next session
```

### 5.3 Episodic vs serial

| Model | Strength | Weakness | Fits |
|---|---|---|---|
| Episodic (self-contained) | Any episode works as an entry point; easy to drop in events | Weak long-term pull | Client-of-the-week metas, mascot comedy, live events |
| Serial (continuing) | Strong "what happens next" pull | Returning players lose the thread; hard to join late | Mystery metas, story apps, gacha story chapters |
| Hybrid (A-plot per episode, B-plot across season) | Both pulls; entry-friendly | More planning | Most live narrative casual games |

**Always serve the returning player:** a "previously…" recap after 24–72 h of absence, a story log/album, and chapter titles that summarise.

### 5.4 Open-loops ledger

```markdown
| id  | question                              | scale | opened (beat)  | payoff (planned beat) | status |
|-----|---------------------------------------|-------|----------------|-----------------------|--------|
| L01 | Where is Grandma Eda?                 | macro | cold_open      | s1_finale             | open   |
| L07 | What is in the crate marked "E"?      | meso  | ch1_t03        | ch1_t09               | open   |
| L09 | Why does Hale avoid the cliffs?       | meso  | ch2_t02        | ch3_t11               | open   |
| L12 | Who keeps leaving shells on the step? | micro | ch2_t05        | ch2_t07               | closed |
```

Rules: answer one, raise one; ≤ 4 open at once; every loop has a planned payoff; never let a paid item hold the only answer.

### 5.5 Release cadence and production capacity

- **Cadence must match capacity.** Promise only the cadence the pipeline can sustain for a year; a broken promise ("new chapter every week") costs more trust than a slower honest cadence.
- **Buffer:** hold several weeks of finished content before launch of a serialised cadence (a common practice; size it to your pipeline's variance).
- **Event stories:** time-limited events with mini-stories are a staple of live casual games. Archive them (album, "memories", rerun) so players who missed an event are not locked out of story context; time-limited *rewards* are a monetization choice, time-limited *story* is a narrative cost.

### 5.6 Formats adjacent to games

- **Story apps** (chapter tickets, premium choices): see the `premium-choice` mechanic card and `skills/genre-playbooks/references/narrative-rhythm-edu-kids.md` §1.
- **Real-time messaging fiction** (*Lifeline*, 3 Minute Games, 2015): see the `realtime-narrative` mechanic card — the phone as diegetic device.
- **Vertical short-drama apps** and chat-fiction formats compete for the same snacking attention; their lessons (cold opens, cliffhanger every episode, vertical framing) transfer directly to mobile story beats.

---

## 6. Narrative as retention — mechanisms and measurement

### 6.1 Mechanisms (and how strong the evidence is)

| Mechanism | Source | Design use | Caveat |
|---|---|---|---|
| **Curiosity / information gap** | Loewenstein, "The psychology of curiosity" (1994): curiosity arises when attention is drawn to a gap in knowledge | Mystery spines, cliffhangers, locked rooms | Gaps that are too large or never closed produce frustration, not curiosity |
| **Unfinished business** | Zeigarnik (1927) reported better memory for interrupted tasks; replications are mixed, while the tendency to *resume* interrupted tasks (Ovsiankina effect) has stronger support | Open loops at session end | Treat as a heuristic, not a law; do not over-claim in reviews |
| **Narrative transportation** | Green and Brock (2000): absorption into a story changes attitudes and engagement | Strong characters and tone consistency | Requires quality writing; broken by dissonance and interruptions |
| **Parasocial attachment** | Horton and Wohl (1956): one-sided relationships with media figures | Mascots, companions, characters who remember the player | Ethically sensitive — no guilt or romance pressure, especially with minors |
| **Goal gradient** | Hull (1932); Kivetz, Urminsky and Zheng (2006): effort accelerates as a goal nears | Area completion bars, chapter progress | Works with or without story; story adds meaning |
| **IKEA effect / endowment** | Norton, Mochon and Ariely (2012) | Persistent décor choices in renovated spaces | Effect sizes vary; do not rely on it alone |
| **Routine** | Habit formation through cues and cadence | Daily story beat, weekly chapter | Pairs with cadence promises you can keep |

Deeper treatment in `player-psychology`.

### 6.2 What narrative does at each retention horizon

| Horizon | Narrative job | Instruments |
|---|---|---|
| D1 | Hook: a dramatic question and a likeable character within the first session | Cold open, FTUE beats, first open loop |
| D7 | Investment: players care about a character and a thread | First area-end reveals, callbacks to their choices, the midpoint of the first arc |
| D30+ | Belonging: world, cast, community lore, seasonal stories | Seasons, event stories, community theories, character anniversaries |

### 6.3 Design for skippers

A large share of casual players skip story (measure it — do not assume a number). Design so that skippers still get the story's benefits:
- The **visible change** (renovated room, new character in the scene) carries the beat without text.
- **One-line summaries** on task cards and a story log let skippers catch up later.
- **Never gate gameplay on reading.** Required information (new mechanic rules) belongs in the tutorial UI, not only in a character's dialogue.

### 6.4 Measuring narrative impact

Raw comparisons ("players who watch story retain better") are confounded — engaged players do everything more. Use:

1. **Holdout experiments.** Randomly assign new users to story-on vs reduced-story (e.g. beats replaced by summary cards). Primary metric D7 or D30 retention; guardrails: session length, progression, revenue per user. Size it first:
   `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ab_test.py size --baseline 0.15 --mde 0.01` (illustrative baseline — use your own), then analyse with `ab_test.py analyze`.
2. **Beat-level funnels.** `story_beat_seen` with `skipped` and `seconds_on_beat`; find beats with spikes in skip rate or session-end immediately after (a beat that ends sessions is failing as a hook).
3. **Choice telemetry.** `dialogue_choice` distributions reveal options no one picks (cut or rewrite) and paid-choice take rates (watch churn after declined paid choices — `premium-choice` card).
4. **Chapter funnels and story-wall analysis.** Retention of players who reach the end of available story versus matched players who have not; plan events for the wall.
5. **Qualitative.** Reviews and community mentions of characters and story; playtest observations of whether players read, smile or skip.

Event definitions: `references/dialogue-and-branching.md` §14.2; taxonomy and dashboards: `player-analytics`.

---

## 7. Narrative as marketing

### 7.1 Story-driven creative formats

| Format | Hook in the first 3 seconds | Narrative ingredient | Must be true in the game |
|---|---|---|---|
| Character in peril | "Help her!" | A character the viewer instantly wants to save | The game contains that situation or mode |
| Choose-your-response | "What would you do?" | Dilemma with 2–3 options | Choices of that kind exist |
| Before / after | Ruin → restored | Restoration fantasy | Renovation looks like that |
| Mystery tease | A question or a secret | Open loop | The mystery is in the story |
| Fail / rescue | Viewer sees a mistake, wants to do better | Competence fantasy | The mechanic shown is the real mechanic |
| Character comedy | A mascot reaction or gag | Personality | The character behaves this way in-game |

### 7.2 The misleading-ad line

Ads that show scenes, mechanics or story situations the game does not contain mislead players and carry regulatory risk. The UK Advertising Standards Authority, for example, ruled in 2020 that certain ads for Playrix's *Homescapes* and *Gardenscapes* were misleading because they showed gameplay not representative of the games (verify the details); the studio later added comparable mini-games. Rules for narrative teams:
- Brief UA with the character rules, tone bible and the list of real in-game situations.
- If a narrative concept tests well as an ad but is not in the game, **build it into the game before scaling spend** — or do not run it.
- Ads must not misrepresent tone (a horror-tinged ad for a cozy game misleads too).
Policies and enforcement details belong to `marketing-ua` and `legal-ethics`.

### 7.3 Store page and storefront storytelling

- **Screenshots tell a story in order:** premise → main character → the core loop → the meta change → the mystery or emotional hook. Captions ≤ 5–7 words each, localised.
- **App preview video:** open on the dramatic question, show real gameplay early.
- **Icon:** the mascot's face or the key object; recognisable at small sizes. Details in `store-release`.

### 7.4 Push notifications and CRM in character voice

| Do | Don't |
|---|---|
| "Pip found something shiny on the beach." | "Pip misses you and is sad you left 😢" (guilt) |
| "Chapter 4 is here: the lighthouse door is open." | "LAST CHANCE! Grandma's secret disappears in 1 hour!" (false urgency on story) |
| Respect quiet hours, OS settings and opt-in | Daily nags when the player has nothing new to do |
| Tie notifications to genuine new content or ready timers | Romance or companionship pressure, especially for minors |

Starting cap: at most one story-flavoured notification per day, only when there is new content.

### 7.5 Community and IP extension

- Fan theories are free engagement: plant fair clues, keep a couple of plausible explanations alive, acknowledge good theories without confirming.
- Character anniversaries, behind-the-scenes art and short social comics extend the cast's reach cheaply.
- IP extension (spin-offs, animation, merchandise) follows the IP ladder in `references/worldbuilding-characters.md` §11.3.

---

## 8. Narrative in the FTUE

| Principle | Rule |
|---|---|
| Situation before puzzle | Open on a story situation (the ruined harbour, the letter) so the first level has a reason — the pattern Homescapes used |
| Hook within ~30 seconds | Establish the dramatic question and one likeable character before or right after the first level |
| Text budget | ≤ 3 lines per beat, ≤ 90 characters per line during onboarding |
| Teach through the guide | The guide character introduces mechanics in voice; the UI carries the actual rules |
| Delay lore | No history lessons in the first session; one mystery, one character, one goal |
| Fast first reward | First visible change (repair, decoration) within the first few minutes; record the target in `contract.ftue.aha_seconds_target` (the schema notes > ~90 s to first real fun as a retention risk) |
| Skippable on reinstall | Returning players skip the opening |

**FTUE narrative beat template (maps to `contract.ftue.steps[]`):**

```json
[{"id": "ftue_cold_open", "goal": "Understand the premise and the missing grandmother", "teaches": ["premise"], "max_seconds": 20},
 {"id": "ftue_first_level", "goal": "Win the first board with guide encouragement", "teaches": ["merge"], "max_seconds": 45},
 {"id": "ftue_first_task", "goal": "Spend the first star; see the cottage door repaired", "teaches": ["stars_to_tasks"], "max_seconds": 30},
 {"id": "ftue_first_hook", "goal": "Find the brass key; open the first story loop", "teaches": ["story_tasks"], "max_seconds": 20}]
```

---

## 9. Narrative by mobile genre

| Genre | Typical level | What the story must do | Narrative budget priority | Reference examples |
|---|---|---|---|---|
| Hypercasual | L0 | Premise readable in one second | Icon and ad concept | Most hypercasual titles |
| Hybrid-casual | L1 | Character + light progression framing | Mascot, results reactions, season framing | Runner/arcade hybrids with a cast |
| Match-3 / sort / block | L1–L2 | Give levels a why; reward with visible change | Meta-story, renovation art | Homescapes, Royal Match, Lily's Garden |
| Merge-2 | L2 | Turn merges into requests from people; mystery spine | Requests with personality, reveal schedule | Merge Mansion, Travel Town (orders) |
| Idle / tycoon | L1–L2 | Milestone flavour, expedition logs, prestige reframing | Flavour text at scale; event stories | Idle titles with themed eras |
| Word / trivia | L1 | Travel or collection framing | Themed destinations, light characters | Word games with travel metas |
| Hidden object | L2–L3 | Serial mystery; environmental storytelling in scenes | Writing + scene art | June's Journey |
| Story apps / VN | L3 | The story is the product | Writing throughput, art consistency, localisation | Choices, Episode |
| RPG / gacha | L3 | Story mode, character stories, banner tie-ins | Writing, VO, localisation, events | Gacha RPG story modes |
| Strategy / 4X | L1–L2 | Faction identity, light campaign, emergent stories | Lore, faction art, event narratives | Mobile strategy campaigns |
| Narrative puzzle / premium | L4 | Interaction as storytelling | Craft over volume | Florence, Monument Valley (environmental, minimal text) |
| Cozy / life sim | L2–L3 | Relationships, community, slice-of-life | Character dialogue, barks, events | Cozy farm and town sims |

---

## 10. Production pipeline

### 10.1 Roles and documents

| Document | Owner | When | Size |
|---|---|---|---|
| Narrative pillars + ambition level | Narrative lead + game director | Concept | Half a page |
| Bible on a page (world, cast, tone) | Narrative lead | Concept → slice | 1 page |
| Story outline mapped to levels/areas | Narrative designer | Slice | Sequence table (`references/story-structures.md` §3.5) |
| Character sheets + voice chart | Narrative designer | Slice | 1 page per core character |
| Tone bible with golden/rejected lines | Narrative lead | Slice | 2–4 pages |
| Beat tables / scripts | Writers | Production | Data files (JSON, Ink, Yarn) |
| String tables + translator notes | Localisation manager | Production | CSV per locale |
| Open-loops ledger + canon tiers | Narrative lead | Ongoing | Living documents |
| Narrative live-ops calendar | Narrative lead + live-ops | Live | Season and event plan (`liveops`) |

### 10.2 Review stages per content drop

1. Outline review (structure, open loops, pacing against difficulty).
2. Draft review (tone, voice, canon, length budgets).
3. Lint and compile (`references/dialogue-and-branching.md` §14).
4. Rating and sensitivity review.
5. Localisation handoff with context; LQA on device.
6. Playthrough evidence and visual pass with pseudo-locale.

### 10.3 AI-assisted drafting — workflow and limits

Research on LLM storytelling in games finds that models write engaging prose but struggle to keep game mechanics consistent and verifiable over long or complex sessions (RPGBench, 2025 — see `skills/genre-playbooks/references/narrative-rhythm-edu-kids.md` §0.1 and its sources). Practical pipeline:

```
human: outline, beats, character sheets, tone bible (golden/rejected lines)
model: 3–5 draft variants per scene within length budgets, using the bible as context
human: select, edit, rewrite — the voice is human-owned
tools: narrative_lint.py (structure, lengths, placeholders), compiler checks, canon search
human: tone/canon/rating review; localisation handoff; record provenance
```

Rules: keep the deterministic structure (branches, flags, rewards) authored and validated, not generated at runtime; never let generated text introduce canon without review; record which text was AI-assisted (provenance notes in the project); check disclosure obligations for player-facing AI-generated content per storefront (`legal-ethics`; see the volatile facts in `references/worldbuilding-characters.md` §15). Runtime LLM dialogue (AI-as-mechanic NPCs) is a separate design with cost, latency, safety and moderation requirements — treat it as a feature with its own risk review.

---

## 11. Worked example A — adding a meta-story to a sort puzzle

**Situation:** a liquid-sort puzzle with solid D1 but weak D7; levels feel interchangeable. Budget: small (one writer part-time, existing 2D artist).

1. **Ambition level:** L2-light — client-of-the-week episodes plus a thin serial thread.
2. **Premise (five world questions):** *You run a tiny potion shop in a hillside village; each customer needs a remedy only correct sorting can brew.* One big lie: potions work. Serial thread: the shop's previous owner left a recipe book with pages missing.
3. **Structure:** each customer = one episode of 6–10 levels in kishōtenketsu shape (arrives with a problem → complication → twist about their real need → warm resolution). Every fourth customer reveals a recipe-book page (serial B-plot; open-loops ledger).
4. **Content maths:** fast segment wins ~15 levels/day → 2 customers/day; a 60-day runway needs ~120 customers if one per 7–8 levels — too many to write well. Fix: recurring customers (a cast of 12 regulars with returning arcs) plus event customers; each regular returns every ~10 days with a new problem. Writing ≈ 120 episodes × 6 lines × 11 words ≈ 8,000 words.
5. **Reward:** a shop that visibly fills with gifts from customers (persistent décor = IKEA effect) and a customer album (collection).
6. **Retention test:** holdout with story cards replaced by generic "order complete" cards; primary metric D7; guardrails: levels per day, session length.
7. **Marketing hook:** "A customer with a strange problem" creatives — real in-game customers only.
8. **Ontology:** `content.characters` gets the 12 regulars as objects with ids; a `story` progression track with unlocks for recipe pages; `analytics` events `story_beat_seen`, `chapter_complete` (customer = chapter).

## 12. Worked example B — a season narrative for a hybrid-casual game

**Situation:** a hybrid-casual runner with a 4-week season pass; the cast exists but seasons feel like reskins.

| Week | Kishōtenketsu part | Story card drops (free track) | Event | Hook |
|---|---|---|---|---|
| 1 | Ki — the circus comes to town | 3 cards: new rival introduced | Circus-themed run modifiers | Rival steals the mascot's hat |
| 2 | Shō — chasing the hat through the circus | 3 cards: rival's backstory hints | Chase event | The rival seems scared of the ringmaster |
| 3 | Ten — the rival was trying to escape the circus | 3 cards: reveal + choice of how to help (expressive, cosmetic outcome) | Team event "free the performers" | Ringmaster locks the gates |
| 4 | Ketsu — the gang helps the rival leave; the rival joins the cast | 3 cards + finale animation | Finale race | Postcard from the next destination (next season) |

Rules applied: story cards on the **free** track (story is not a paid privilege); premium track holds cosmetics; story archive in the album after the season; the rival becomes a permanent cast member with a flat arc from then on; a one-line recap card opens each week.

---

## 13. Checklists

**Meta-story launch readiness**
- [ ] Ambition level chosen and recorded; budget matches it.
- [ ] Premise answers the five world questions; bible on a page exists.
- [ ] Dramatic question set in the first session; first open loop opened in the FTUE.
- [ ] Content maths done for the fastest decile; story-wall plan exists.
- [ ] Micro-scenes ≤ 6 lines, ≤ 90 chars per line; skippable; recap after absence.
- [ ] Story never interrupts a level; story never blocked by a pay-only wall; story losses never remove progress.
- [ ] Visible change carries each beat for skippers.
- [ ] Telemetry events registered; holdout test planned.

**Episodic/serial content drop**
- [ ] Episode has a local goal, a turn and a hook; open-loops ledger updated (≤ 4 open).
- [ ] Cadence promise matches capacity with a buffer.
- [ ] Event story archived after the event.
- [ ] Localisation context and length checks passed.

**Marketing alignment**
- [ ] Every narrative ad concept maps to a real in-game situation and the real tone.
- [ ] Store screenshots tell the story in order with localised captions.
- [ ] Push notifications in character voice follow the do/don't table; quiet hours respected.
- [ ] No character pleads for money; no guilt or false urgency anywhere.
