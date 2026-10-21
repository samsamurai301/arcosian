# Story Structures for Games

Structure is the pacing machinery of a story: it decides when the player learns what, when stakes rise, when tension releases and when the story pays off. Games break most film and novel assumptions — the player controls time, repeats content, fails, skips, and may stop for a week — so classic structures are useful only once they are translated into levels, sessions, chapters and seasons. This file covers the vocabulary, three-act and its relatives (Freytag, sequences, beat sheets), kishōtenketsu, the hero's journey with a serious critique, ludonarrative harmony and dissonance, environmental storytelling, emergent storytelling and drama management, and pacing tools such as scene–sequel and interest curves. Each structure comes with a mapping to game units, a worked example and a "use when / avoid when" verdict. Frameworks are summarised in our own words with attribution; read the original works for depth.

## Contents

1. Vocabulary that prevents arguments
2. What changes when the audience holds the controller
3. Three-act structure and its relatives
4. Kishōtenketsu
5. The hero's journey — and why to treat it as a diagnostic, not a template
6. Other structures worth knowing
7. Ludonarrative harmony and dissonance
8. Environmental storytelling
9. Emergent storytelling and drama management
10. Pacing tools: scene–sequel, value shifts, interest curves, open loops
11. Choosing a structure — decision table
12. Structure review checklist

---

## 1. Vocabulary that prevents arguments

| Term | Working definition | Why it matters in games |
|---|---|---|
| Story | The events that happen, in chronological order (the *fabula*, in Russian Formalist terms) | Lives in the world bible and timeline |
| Plot | The order and manner in which events are revealed (the *syuzhet*) | What the player actually experiences; you design this |
| Narrative | Everything that communicates story: text, VO, environment, mechanics, UI | Narrative design owns all channels, not just dialogue |
| Fiction | The imagined frame around the rules ("you are a butler restoring a mansion") | Can be thin (abstract puzzle) or thick (RPG) |
| Beat | The smallest unit of change — an action and a reaction | Mobile story beats are 10–40 s |
| Scene | A unit of continuous action in which a value changes (safe → in danger, stranger → ally) | One scene per chapter step, task or quest stage |
| Sequence | A run of scenes with one local goal (≈ 10–15 minutes of film) | Maps to a world, area, or 5–15 levels |
| Act | A run of sequences ending in a major reversal | Maps to a world, season or "book" |
| Arc | The change in a character or situation across the whole | Character arcs need many scenes; plan them across chapters |
| Dramatic question | The yes/no question the audience waits to see answered ("Will she save the lighthouse?") | Every chapter needs one; the macro question keeps players for weeks |
| Stakes | What is lost if the goal fails | Mobile stakes are usually emotional or communal, rarely lethal |
| Inciting incident | The event that disrupts the status quo and starts the story | Must happen in the first session — ideally before or during the first level |
| Reversal / turn | An event that flips expectation | One per chapter keeps episodic stories alive |
| Payoff / callback | The return of an earlier setup with new meaning | Cheapest way to make linear stories feel reactive |

**Rule:** in reviews, say "plot" when you mean reveal order and "story" when you mean events. Half of narrative disagreements are about the difference.

## 2. What changes when the audience holds the controller

| Film/novel assumption | Game reality | Structural consequence |
|---|---|---|
| The author controls time | The player controls pacing; may stall, grind or rush | Pace by **gates** (progress, stars, chapters), not by minutes |
| The audience experiences each scene once | Players repeat levels, retry, replay | Story must survive repetition: put narrative at boundaries, not inside the repeated unit |
| Watching is the activity | Playing is the activity; story competes with play | Story beats must be short, skippable and placed at natural breaks |
| One continuous sitting (or a few) | Sessions of 1–5 minutes, days apart | Recaps, short open loops, one dramatic question per session window |
| Protagonist is a character with fixed choices | Protagonist may be the player (avatar) or a character the player steers | Decide early: **player-as-character**, **player-as-director**, or **player-as-companion** |
| The ending is the point | Many games never end (live service) | Seasons become acts; the macro question must regenerate |
| Conflict drives scenes | Mechanics may already provide conflict (the level is the antagonist) | Story can supply *meaning* and *context* rather than more conflict |

**The player-position decision** (make it in the first week of narrative work):

| Position | Player relationship to protagonist | Fits | Watch out for |
|---|---|---|---|
| Player-as-character | Avatar, often silent or lightly voiced; choices express the player | RPGs, story apps, adventure | Protagonist blandness; dialogue must leave room for projection |
| Player-as-director | Player steers a defined character (Austin the butler, Maddie in Merge Mansion) | Casual meta-stories, narrative puzzle | Character must be likeable enough to follow for months |
| Player-as-companion/helper | Player helps a character who has their own arc ("help Grandpa rebuild the farm") | Cozy, renovation, merge, idle | Character's needs must feel real, not like a quest dispenser |
| Player-as-god/manager | Player oversees a population; stories emerge | Sim, strategy, colony, idle | Requires emergent tools (§9), not authored arcs |

---

## 3. Three-act structure and its relatives

### 3.1 The model

Aristotle's *Poetics* (c. 335 BCE) asked for a whole action with a beginning, middle and end, and named the reversal (*peripeteia*) and recognition (*anagnorisis*) as the strongest moments. Syd Field (*Screenplay*, 1979) codified the modern three-act "paradigm": setup, confrontation, resolution, in roughly 1 : 2 : 1 proportion, separated by plot points that spin the story in a new direction. Gustav Freytag (*Die Technik des Dramas*, 1863) described a five-part pyramid for classical drama: exposition, rising action, climax, falling action, and catastrophe or resolution.

| Act | Share | Job | Key beats |
|---|---|---|---|
| I — Setup | ~25% | Establish normal world, protagonist, want; disrupt it | Opening image, inciting incident (~10%), commitment / first plot point (~25%) |
| II — Confrontation | ~50% | Escalating obstacles; protagonist adapts, then fails | First pinch, **midpoint reversal** (~50%) that raises stakes or reframes the goal, second pinch, low point (~75%) |
| III — Resolution | ~25% | Final confrontation, the dramatic question answered, new normal | Climax (~90%), resolution, closing image echoing the opening |

The **midpoint** is the most underused tool in game stories. A midpoint that reframes the goal ("the mansion was never Austin's — someone wants it back") renews a mid-game that otherwise sags into repetition.

### 3.2 Mapping to game units

| Film unit | Premium game (10–20 h) | Casual meta-story (live, 300+ levels) | Story app (season of 15–20 chapters) | Hybrid-casual / idle |
|---|---|---|---|---|
| Act I | Tutorial + first region (first 1–2 h) | FTUE + first 1–3 areas (first ~1–3 days) | Chapters 1–4 | First zone / first prestige |
| Inciting incident | First 10 minutes | **Before or during level 1** | Chapter 1, first scene | Opening screen / premise card |
| Midpoint | Mid-game twist | End of the first "book" or area set (weeks in) | Chapter 8–10 | Mid-zone boss / reveal |
| Act III | Final region and boss | Season finale; never a true "end" | Chapters 16–20 + cliffhanger for next season | Final zone; prestige reframes |
| Closing image | Ending cinematic | Area completion screen echoes the first ruined room | Final scene mirrors first | Victory screen echoes opening |

### 3.3 The sequence approach (best fit for episodic play)

Paul Joseph Gulino (*Screenwriting: The Sequence Approach*, 2004), building on Frank Daniel's teaching, breaks a feature into **eight sequences** of roughly equal length, each with its own goal, tension and resolution, and each ending on a turn that launches the next. For games this is often more useful than the three acts, because each sequence maps neatly to a world, an area, a chapter or a week of live content — a self-contained unit with its own mini-arc that still advances the big one.

**Template for a sequence (one world/area/chapter):**

```
Sequence N
  Local goal:         <what the protagonist tries to achieve in this unit>
  Local obstacle:     <what makes it hard; often the mechanic's new twist>
  Mini-climax:        <the unit's peak — usually the area's final task or boss level>
  Turn / hook:        <reveal or complication that launches sequence N+1>
  Macro progress:     <how this moves the season's dramatic question>
  Character beat:     <who changes a little, and how>
```

### 3.4 Beat sheets

Blake Snyder (*Save the Cat!*, 2005) popularised a fifteen-beat sheet with page targets; its main contribution for game writers is the reminder to give the protagonist a likeable action early, to have a "fun and games" stretch that delivers the premise's promise, and to place an "all is lost" low before the finale. Use beat sheets as a **gap detector** — "where is our low point?" — not as a fill-in form. Rigid beat-sheet adherence is a leading cause of interchangeable stories.

### 3.5 Worked example — a 60-level casual arc

Premise: a lighthouse keeper's granddaughter returns to restore a storm-wrecked harbour town (merge or match-3 meta). Stars earned in levels buy restoration tasks; each task plays a 2–6 line micro-scene.

| Levels | Unit | Structural job | Beat |
|---|---|---|---|
| 0 (pre-level) | Cold open | Inciting incident | Storm footage: lighthouse dark, grandmother missing, letter in her handwriting: "Keep the light." |
| 1–8 | Seq 1 — the cottage | Setup; teach the meta | Clean the cottage; meet Pip (dock cat) and Mr. Hale (gruff harbourmaster). Dramatic question set: *where is Grandma, and can the light be relit?* |
| 9–20 | Seq 2 — the docks | Commitment | Restoring the docks earns the town's grudging trust; a mysterious buyer offers to purchase the harbour |
| 21–30 | Seq 3 — the market | Fun and games | Shops reopen, comic set pieces; clues to Grandma's journals |
| 31 | **Midpoint** | Reframe | The journal reveals Grandma *sold* the lighthouse before vanishing — the goal shifts from "repair" to "buy it back and find out why" |
| 32–45 | Seq 4–5 — the cliffs | Escalation | Buyer's crew sabotages repairs; Mr. Hale's secret history surfaces |
| 46–52 | Low point | All is lost | Storm destroys the docks again (story only — do **not** remove player progress) |
| 53–59 | Seq 6 — the lighthouse | Climax build | Town rallies; every earlier character returns (callback payoff) |
| 60 | Climax + closing image | Resolution + hook | Light relit; first shot echoes the cold open, but bright — then a message in a bottle opens the next season |

Mechanical note: the storm in the low point is a **story** reversal. Never take away renovated rooms or purchased items; loss aversion turns a dramatic beat into a betrayal.

### 3.6 Verdict

- **Use when:** there is a single protagonist, a clear goal and a finite arc (premium, story app seasons, campaign modes, season arcs in live games).
- **Avoid when:** the game is systemic, sandbox or player-as-god; or the content cadence cannot support a strong climax (then use kishōtenketsu or episodic structures).

---

## 4. Kishōtenketsu

### 4.1 The model

Kishōtenketsu (起承転結) is a four-part structure that came to Japanese and Korean writing from classical Chinese four-line poetry (*qǐ chéng zhuǎn hé*) and is the default shape of four-panel *yonkoma* comics:

| Part | Name | Job |
|---|---|---|
| 1 | **Ki** — introduction | Present the situation and characters |
| 2 | **Shō** — development | Deepen the same situation without changing direction |
| 3 | **Ten** — twist | Introduce something unexpected — often an apparently unrelated element |
| 4 | **Ketsu** — reconciliation | Show how the twist and the setup relate; the audience reconciles them |

A frequent misreading is "kishōtenketsu = story without conflict". More precisely, the turn comes from **juxtaposition and recontextualisation** rather than antagonism; conflict is permitted but not required. That makes it a natural fit for cozy, slice-of-life, wholesome and puzzle games, where a villain would feel wrong.

### 4.2 In level design and in narrative

Koichi Hayashida described using a four-step structure of this kind for Super Mario 3D Land levels — introduce a mechanic, develop it, twist it, then conclude (Gamasutra interview, 2012; verify the exact wording). The level-design use is covered in `design-theory` (`skills/design-theory/references/core-loops-and-structure.md`) and `level-design`; here the focus is narrative:

| Narrative scale | Ki | Shō | Ten | Ketsu |
|---|---|---|---|---|
| Micro-scene (4 lines) | Line 1 sets a situation | Line 2 deepens it | Line 3 turns it | Line 4 lands the joke or the warmth |
| Renovation room (4 tasks) | Clear the attic | Find old photos while cleaning | One photo shows Grandma with the rival buyer | Reframe: they were once partners — the room's final décor choice is "their" style |
| Chapter (4 sequences) | Arrive at the festival | Prepare stalls with townsfolk | The festival is the anniversary of the storm nobody mentions | The town lights lanterns for those lost — including Grandma's boat |
| Season (4 months) | New district | Deepen characters | Twist recontextualises the town's history | Reconciliation and the next mystery |

### 4.3 Worked micro-scene (original example)

```
KI    PIP (cat) knocks a jar off the shelf. Again.
SHŌ   MAYA: "Third jar today. Are you hunting ghosts?"
TEN   The jar breaks — inside, a brass key engraved with the lighthouse.
KETSU MAYA: "...Okay. Good cat. Very good cat."
```

Four lines, one laugh, one hook, under 140 characters per line, no conflict needed. This is the shape most casual meta-story scenes should take.

### 4.4 Verdict

- **Use when:** cozy, comedic, wholesome, puzzle or slice-of-life tone; micro-scenes; episodic content where each episode must stand alone; audiences that dislike high-stress drama.
- **Avoid when:** the core fantasy is struggle against an opponent (strategy, PvP, action); then three-act escalation fits better.

---

## 5. The hero's journey — and why to treat it as a diagnostic, not a template

### 5.1 The model in brief

Joseph Campbell (*The Hero with a Thousand Faces*, 1949) proposed a "monomyth": a hero departs the ordinary world, passes through trials and an ordeal in a special world, gains a boon, and returns transformed — seventeen stages grouped into departure, initiation and return. Christopher Vogler adapted it for Hollywood (*The Writer's Journey*, 1992, developed from a 1985 studio memo) into twelve stages and a set of archetypal *functions* (mentor, herald, threshold guardian, shapeshifter, shadow, trickster, ally). Games often cited as consciously monomyth-shaped include *Journey* (thatgamecompany, 2012).

Condensed to the parts that matter to a game writer:

| Phase | Function | Game translation |
|---|---|---|
| Ordinary world, call, refusal | Show a status quo worth leaving; resistance makes the choice meaningful | FTUE "home" space; one beat of reluctance at most — players are impatient |
| Mentor, threshold | Gain help; commit to the unknown | Tutorial guide; leaving the first zone |
| Tests, allies, enemies | Learn the special world's rules | Mid-game loops; party building |
| Approach, ordeal | The central crisis; symbolic death | Boss / low point |
| Reward, road back | Seize what was sought; consequences pursue | Power spike; escalation |
| Resurrection, return | Final test proves transformation; bring the boon home | Final boss uses everything learned; home space changed |

### 5.2 The critique (know it before using the model)

1. **Universality is overstated.** Folklorists (for example Alan Dundes) criticised Campbell's method as selective — collecting examples that fit and ignoring those that do not. The monomyth is one pattern among many, not the shape of all stories.
2. **It centres one kind of protagonist.** The model assumes an individual, usually male, outward-bound hero whose growth comes through conquest. Maureen Murdock (*The Heroine's Journey*, 1990) and Gail Carriger (*The Heroine's Journey*, 2020) describe alternatives built on community, connection and networks of help rather than solitary triumph — often a better fit for cozy, social and casual audiences.
3. **It produces sameness.** After decades of studio adoption, slavish monomyth stories are predictable: players recognise the mentor's death and the refusal of the call before they happen.
4. **It ignores agency and repetition.** The model describes one transformation through a linear series of trials. Games repeat, branch, fail and loop; a twelve-stage linear path fights the medium.
5. **It does not fit live service.** A hero who "returns transformed" ends the story; a live game needs a status quo that persists.

### 5.3 How seniors actually use it

- As a **transformation diagnostic**: "What does the protagonist believe at the start? What breaks that belief? What do they believe at the end?" If there is no answer, there is no arc — whatever structure you use.
- As a **function inventory**: does the story have someone who teaches (mentor), someone who tests (threshold guardian), someone whose loyalty is uncertain (shapeshifter)? Functions can be held by systems, places or items, not only characters.
- As a **season-arc skeleton** for RPG/gacha story chapters, where audiences expect the epic register.
- **Not** as a level-by-level template for a casual game.

### 5.4 Verdict

- **Use when:** epic fantasy/RPG register, single-protagonist campaigns, season arcs in gacha games, marketing trailers that need a recognisable shape.
- **Avoid when:** ensemble or communal stories, cozy tones, emergent games, live games whose cast must persist; or when it becomes the reason every story feels the same.

---

## 6. Other structures worth knowing

| Structure | Shape | Best game fit | Reference works (examples) |
|---|---|---|---|
| **Story circle** (Dan Harmon) | An eight-step loop: a character in comfort wants something, enters the unfamiliar, adapts, gets it, pays a price, returns, and is changed | Episodic content; one circle per episode or event | Common in TV writing rooms |
| **Episodic (story-of-the-week)** | Self-contained episodes, stable cast, light serial thread | Live events, client-based meta (one client per room), sitcom-tone casual | Sitcoms; makeover-style casual metas |
| **Serial (A/B plots)** | A-plot resolves per episode; B-plot runs across a season | Story apps, seasons, chapters | Prestige TV |
| **In medias res** | Open in the middle of action, then backfill | FTUE hooks; trailers | Many action games open on a crisis |
| **Mystery (reveal schedule)** | Crime/question → clues → false solutions → reveal | Merge/match metas with a mystery spine; hidden-object | Detective fiction; *June's Journey*-style metas |
| **Multi-perspective** | Same events from several viewpoints | Ensemble casts, unlockable character stories | *Rashomon* (film, 1950) |
| **Fragmented / database** | Player assembles story from shuffled fragments | Investigation games, lore collectibles | *Her Story* (Sam Barlow, 2015) |
| **Loop narrative** | Each run/death advances story; knowledge persists | Roguelites, time loops | *Hades* (Supergiant, 2020) |
| **Frame narrative** | A story told inside a story (narrator, journal, letters) | Cheap linking device for disconnected levels | Narrated journals, "grandma's diary" metas |
| **Vignette** | Short, emotionally complete slices with minimal plot | Premium mobile narrative | *Florence* (Mountains, 2018) |

### 6.1 Mystery reveal schedule (useful for casual metas)

Mystery spines are the most-used macro structure in story-led casual games because a question costs nothing to keep open and pays out for months. Rules:

1. **Answer one, raise one (or two).** Every reveal answers a question the player has been holding and opens a new, bigger one. Never close all loops at once except at a season finale.
2. **Fair play.** Plant at least two clues for every reveal before it happens; players who re-read should see the reveal coming.
3. **False solution before true solution.** A plausible wrong answer at ~60–75% of the arc makes the true reveal land.
4. **Reveal cadence.** Small revelation per sequence (world/area), major per act/season. Track it in an open-loops ledger (`references/mobile-narrative.md` §5.4).
5. **Never let monetization own the answer.** A reveal must be reachable through normal play at a reasonable pace.

---

## 7. Ludonarrative harmony and dissonance

### 7.1 The model

Clint Hocking coined *ludonarrative dissonance* in a 2007 blog essay on *BioShock*, arguing that the game's mechanics rewarded self-interest while its story argued against self-interest, so the two pulled the player in opposite directions. Generalised: **dissonance** occurs when what the rules reward contradicts what the fiction says; **harmony** (also "resonance" or "consonance") occurs when doing the mechanics *is* experiencing the story.

### 7.2 Types of dissonance

| Type | Example pattern | Typical fix |
|---|---|---|
| **Character contradiction** | A gentle, kind protagonist whose core verb is mass violence | Change the verb or the characterisation; or make the contradiction the point (*Spec Ops: The Line*, Yager, 2012) |
| **Urgency contradiction** | "The city burns tonight!" while the player is free to fish for days | Remove the false urgency, or make time real (timers on that arc only) |
| **Value contradiction** | The story praises mercy; the economy pays more for cruelty | Align rewards with stated values, or make the trade-off explicit and costly both ways |
| **Death/reload contradiction** | The narrative treats death as final; the game respawns | Diegetic respawn (cloning, dream, loop), or make failure non-death |
| **Ability contradiction** | A cutscene shows the hero helpless before an enemy they just beat easily | Keep cutscene power consistent with gameplay power |
| **Tone contradiction** | Grim story beats interrupted by goofy victory jingles and confetti | Tone-aware feedback; scene-specific juice levels |
| **Monetization contradiction** | A tragic loss scene followed immediately by a "50% OFF!" pop-up | Offer suppression windows after emotional beats (rule of thumb: no offers for the rest of that session break) |
| **Abstraction mismatch** | Matching candies fixes a staircase | Accepted by casual audiences **if** framing is light and causal claims are not made; see §7.4 |

### 7.3 Harmony techniques

1. **Verb–fiction alignment.** Choose verbs that mean something in the fiction. In *Papers, Please* (Lucas Pope, 2013) the core verb — checking documents — is the story about bureaucracy and complicity.
2. **Interaction as metaphor.** In *Florence* (Mountains, 2018), conversations are small jigsaw puzzles that become simpler as the relationship grows comfortable and harder during conflict — the difficulty curve *is* the relationship arc.
3. **Controls as characterisation.** In *Brothers: A Tale of Two Sons* (Starbreeze, 2013), each brother is mapped to one side of the controller, and the late game uses that mapping to deliver its emotional climax.
4. **Systems as moral argument.** In *This War of Mine* (11 bit studios, 2014), scarcity and survival systems force the moral compromises the story is about.
5. **Difficulty as drama.** Spikes placed where the story says things are hardest; release (an easy, generous level) after an emotional peak.
6. **Rewards that agree with the story.** If the theme is community, reward helping others (gifts, co-op chests), not hoarding.
7. **Diegetic UI and feedback where cheap.** A restoration progress bar shaped like the lighthouse beam; a character reacting on the results screen.

### 7.4 The casual-game abstraction contract

Casual meta-stories (match-3 + renovation) are, strictly speaking, dissonant: puzzle play does not cause the renovation. Players accept this because the game makes an implicit contract: *puzzles are the effort, the story is the meaning*. Keep the contract by:

- Never claiming literal causation in dialogue ("Your matching fixed the roof!" — avoid). Frame stars as effort or currency, not magic.
- Matching **emotional tone**: cheerful board feel for cheerful stories; if the story turns serious, soften the board's juice for that chapter's intro.
- Keeping story beats **outside** the puzzle unit (results screen, map, between tasks).
- Letting the renovation be the reward the player *sees*; the more visible the change, the stronger the contract.

### 7.5 Harmony audit procedure

For every core verb and every major reward:

| Column | Question |
|---|---|
| Verb / reward | What does the player do or receive? |
| Fiction claim | What does the story say this means? |
| Mechanical incentive | What does the economy actually reward? |
| Tone of feedback | What does the juice say emotionally? |
| Conflict? | Do any columns contradict? |
| Fix | Change verb, change fiction, change incentive, change feedback, or accept as abstraction contract |

Run it at concept (on the contract's `verbs[]` and `loops[]`), again at vertical slice, and before soft launch.

---

## 8. Environmental storytelling

### 8.1 The model

Henry Jenkins ("Game Design as Narrative Architecture", 2004) described four ways space carries story: **evocative** spaces that borrow associations the player already has (a haunted house, a pirate cove), **enacted** stories performed by the player moving through space, **embedded** narratives hidden in the environment for the player to reconstruct, and **emergent** stories that arise from systems in the space. Don Carson (Gamasutra, 2000) brought theme-park design lessons to games; Harvey Smith and Matthias Worch ("What Happened Here? Environmental Storytelling", GDC 2010) framed the player as a detective reading staged evidence. FromSoftware's *Dark Souls* (2011) item descriptions and *What Remains of Edith Finch* (Giant Sparrow, 2017) show the range: from terse fragments to fully staged rooms.

### 8.2 Techniques

| Technique | What it is | Mobile adaptation |
|---|---|---|
| **Staging / vignette** | A frozen tableau implying an event (two chairs, one knocked over, cold tea) | One vignette per room or screen; must read at phone size in under 3 seconds |
| **Before/after** | The same space shown in two states | The renovation meta *is* before/after storytelling — design the "before" as a story, not just "dirty" |
| **Traces** | Evidence of past behaviour: worn paths, scratch marks, repairs | Subtle texture detail is lost on small screens; exaggerate |
| **Juxtaposition** | Objects that do not belong together create a question | A child's drawing in a smuggler's den |
| **Props with history** | Items whose descriptions carry lore | Tap-to-inspect with 1–2 line descriptions (≤ 90 chars) |
| **Signage and writing** | Graffiti, notices, letters | Keep in-world text short; localise it (string IDs, not baked into textures) |
| **Light and colour coding** | Light guides attention; palette shifts encode mood and history | Strong value contrast survives small screens and glare |
| **Audio environment** | Ambient sound implies life or absence | Many players play muted — never put essential story only in audio |
| **Collectible fragments** | Letters, photos, logs | Album/scrapbook UI; each fragment readable alone |

### 8.3 Principles

1. **Glance → look → study.** Layer each space: a glance (≤ 3 s) gives mood and the main question; a look (≈ 10 s) gives the event; study (30 s+) rewards the curious with details and connections. Mobile players mostly glance — make the glance layer carry the story.
2. **Ask, don't tell.** A good vignette creates a question the player answers themselves; the inference is the pleasure.
3. **Consistency with the world bible.** Every staged detail must agree with canon; contradictions are noticed and screenshotted.
4. **One story per space.** Two competing vignettes in one phone screen read as clutter.
5. **Clutter is the enemy of readability.** Decorative density that serves "realism" hides the story beat; art direction must reserve contrast for the narrative focal point.
6. **Localise environmental text.** Baked-in text in textures blocks translation — use overlay labels or keep in-world text decorative and non-essential.

### 8.4 Checklist for a room or screen

- [ ] What happened here? (one sentence)
- [ ] What question should the player be left with?
- [ ] Which single element reads at a glance (focal point, value contrast)?
- [ ] Which 2–3 details reward a closer look?
- [ ] Is anything essential conveyed only by audio or only by small text? (fix)
- [ ] Does it contradict canon? (check the bible)
- [ ] Is in-world text localisable?

---

## 9. Emergent storytelling and drama management

### 9.1 The model

Emergent stories are stories players tell about what happened to them, generated by systems rather than authored scenes: the colonist who survived three raids in *RimWorld* (Ludeon Studios), the dynasty drama of *Crusader Kings* (Paradox), the nemesis who remembers your last fight in *Middle-earth: Shadow of Mordor* (Monolith, 2014; its Nemesis System was later patented by Warner Bros., granted 2021), the household chaos of *The Sims* (Maxis). Tynan Sylvester (*Designing Games*, 2013) argues that much of the effect comes from **apophenia** — players perceive meaningful patterns and motives in systemic events — so the designer's job is to supply the ingredients that make pattern-finding easy and rewarding.

### 9.2 Ingredients

| Ingredient | Why it matters | Design move |
|---|---|---|
| **Persistent identities** | Stories need someone to happen to | Names, faces, traits that persist across sessions |
| **Memory** | Callbacks are what make events feel like a story | Entities remember the player and each other ("you spared me at the bridge") |
| **Relationships** | Drama is relational | Opinion/affinity values between entities |
| **Legible causes** | Players must see *why* something happened | Event logs, thought bubbles, readable traits ("Greedy") |
| **Stakes and irreversibility** | Without loss there is no tension | Limited, recoverable losses on mobile; permanent only where the audience opts in |
| **Variety of events** | Repetition kills the illusion | Large event pools with cooldowns (see bark maths, `references/dialogue-and-branching.md` §10) |
| **A storyteller / pacer** | Raw randomness produces flat or unfair arcs | Drama manager that shapes tension over time (§9.3) |
| **Shareability** | Emergent stories become marketing when shared | Chronicles, recaps, shareable cards, replays |

### 9.3 Drama managers

*Left 4 Dead* (Valve, 2008) used an "AI Director" that tracked an estimate of player stress and alternated build-up, peak and relax phases by adjusting spawns (Michael Booth described the systems in talks around 2009). *RimWorld* ships selectable "storytellers" that pace events differently — a classic escalating one, a gentle one with long calm stretches, and a purely random one. The general pattern:

```text
# Tension-targeting drama manager (sketch)
state: tension in [0, 1], phase in {build, peak, relax}, phase_timer
each tick(dt):
  tension = decay(tension, dt) + recent_event_intensity()
  target  = curve(phase)                 # build: ramp up; peak: hold high; relax: low
  if phase == build and tension >= PEAK_T:   phase = peak;  phase_timer = PEAK_LEN
  if phase == peak  and phase_timer <= 0:    phase = relax; phase_timer = RELAX_LEN
  if phase == relax and phase_timer <= 0:    phase = build
  if tension < target - MARGIN: schedule(pick_event(intensity=target - tension, cooldowns, eligibility))
  if tension > target + MARGIN: suppress_new_threats()
```

Mobile adaptation: the drama manager's "tick" is often a **session** or a **day**, not a frame — e.g. an idle or colony game schedules one dramatic event per return session, with a calm session after any loss.

### 9.4 Storylets as authored emergence

Between fully authored and fully systemic sits **storylet / quality-based narrative**: many small authored story pieces, each with preconditions on state, selected by salience. It is associated with Failbetter Games (*Fallen London*) and discussed at length by Emily Short. Mechanic details, tuning ranges and selection pseudo-code are in `skills/mechanics-codex/references/10-narrative-exploration-mechanics.md` (`storylets`). Yarn Spinner 3's node groups with `when:` conditions and saliency strategies support this pattern directly (`references/dialogue-and-branching.md` §5).

### 9.5 Mobile examples and verdict

- Swipe-card reigns (*Reigns*, Nerial, 2016), life simulators driven by text events, idle-game expedition logs, and colony/survival games all produce emergent stories within short sessions.
- **Use when:** the core is systemic (sim, colony, strategy, idle), replay is central, or content production must scale beyond authored arcs.
- **Avoid when:** the audience expects a crafted plot with a defined protagonist, or when the systems cannot express causes legibly on a small screen.

---

## 10. Pacing tools

### 10.1 Scene and sequel (Dwight V. Swain)

Dwight V. Swain (*Techniques of the Selling Writer*, 1965) split narrative units into **scenes** (goal → conflict → disaster) and **sequels** (reaction → dilemma → decision). For games this maps cleanly onto play and story:

| Swain unit | Game equivalent | Example |
|---|---|---|
| Scene: goal | Quest/task objective | "Repair the dock crane" |
| Scene: conflict | Level or challenge | Hard level with crane-themed obstacle |
| Scene: disaster (or partial success) | Result + complication beat | Crane works, but lifts a crate marked with Grandma's initials |
| Sequel: reaction | Short character beat | Maya stunned; Pip sniffs the crate |
| Sequel: dilemma | Optional choice or decision | Open it now or wait for Mr. Hale? (flavour choice) |
| Sequel: decision | Next objective | "Find Mr. Hale" — new task appears |

Quest chains written as scene–sequel pairs never stall, because every resolution hands the player the next goal.

### 10.2 Value shifts (Robert McKee)

Robert McKee (*Story*, 1997) argues that every scene should turn at least one value from positive to negative or the reverse (trust → suspicion, hope → despair). **Test every scene:** name the value at the start and at the end. If they are equal, the scene is exposition — cut it, merge it, or add a turn. In a mobile meta-story where scenes are 2–6 lines, the turn can be tiny (bored → curious), but it must exist.

### 10.3 Interest curves

Jesse Schell (*The Art of Game Design*, 2008) describes the interest curve: a hook early, a sequence of rising peaks separated by valleys, a climax near the end and a short resolution. It applies at every scale — a scene, a session, a chapter, the FTUE, a season. Overlay the narrative interest curve on the difficulty curve (`progression-difficulty`): story peaks should land just **after** difficulty peaks (as reward) or just **before** them (as motivation — the cliffhanger before a hard level), never in the middle of a level.

### 10.4 Open loops ledger

Track every open narrative question with its opening point, its planned payoff and its scale. Rules of thumb (practitioner starting points, not published benchmarks):

| Scale | Open at any time | Typical lifespan |
|---|---|---|
| Micro (this scene/task) | 1 | Seconds to one session |
| Meso (this area/chapter) | 1–2 | Days |
| Macro (the season/series) | 1 (max 2) | Weeks to months |

More than ~4 open loops at once on mobile and returning players lose the thread; fewer than 1 macro loop and there is no reason to return for story. The ledger format is in `references/mobile-narrative.md` §5.4.

### 10.5 Beat density

| Context | Story beat frequency (starting point) | Note |
|---|---|---|
| Casual puzzle meta | One micro-scene per 1–3 level wins; one chapter beat per 10–20 levels | Players who only want puzzles can skip; the visible renovation carries the beat |
| Story app | Choices every 1–3 minutes of reading | Long stretches without choices read as passive |
| Action / roguelite | A narrative moment per run (hub conversation) | *Hades*-style reactive hub dialogue |
| Idle | A flavour beat per milestone; an event story per week | Text must survive skimming |
| RPG / gacha | Story chapter per progression gate; character stories per unlock | Players expect "skip" plus "story log" |

---

## 11. Choosing a structure — decision table

| Game type | Primary structure | Secondary | Avoid |
|---|---|---|---|
| Casual puzzle + renovation | Sequence approach (area = sequence) with a mystery spine | Kishōtenketsu micro-scenes | Full hero's journey; branching plot |
| Merge-2 with story | Mystery reveal schedule + episodic client/requests | Kishōtenketsu scenes | Long cutscenes |
| Cozy / life sim | Kishōtenketsu; episodic slice-of-life | Emergent (relationships), storylets | Villain-driven three-act |
| Story app / visual novel | Three-act per season + serial A/B plots | Branch-and-bottleneck (see dialogue reference) | Pure tree branching |
| Premium narrative mobile | Vignette or three-act | Ludonarrative metaphor (*Florence*-style) | Padding to hit play-time targets |
| RPG / gacha | Hero's journey season arcs + character side stories | Episodic events | One protagonist arc that "ends" the live game |
| Roguelite | Loop narrative (each run advances story) | Reactive hub dialogue | Story that requires winning runs to progress at all |
| Idle / tycoon | Episodic milestone story; frame narrative | Emergent event logs | Long linear dialogue |
| Strategy / 4X | Emergent + faction lore | Light three-act campaign | Long cutscenes between turns |
| Hypercasual / hybrid-casual | Premise + character (no structure beyond a hook) | Season framing | Text-heavy beats |
| Colony / survival sim | Emergent with drama manager | Storylets | Fixed plot |

---

## 12. Structure review checklist

- [ ] The player position is chosen (character / director / companion / manager).
- [ ] The macro dramatic question can be stated in one sentence, and it can regenerate (for live games).
- [ ] The inciting incident happens in the first session — ideally before or during level 1.
- [ ] Each sequence (world/area/chapter) has a local goal, a mini-climax and a turn.
- [ ] There is a midpoint that reframes the goal, not just raises numbers.
- [ ] Every scene turns a value (McKee test); exposition-only scenes are cut or merged.
- [ ] Story peaks are placed around, not inside, difficulty peaks; story losses never remove player progress.
- [ ] The harmony audit shows no unaddressed contradiction between verbs, rewards, feedback tone and fiction.
- [ ] Open loops ledger: ≤ 4 open at once, at least one macro loop, every loop has a planned payoff.
- [ ] Environmental beats read at a glance on a phone; nothing essential is audio-only.
- [ ] If the game is systemic, emergent ingredients (identity, memory, legible causes, pacing) are present.
- [ ] The structure was chosen from the decision table for a stated reason — not by default.
