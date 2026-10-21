# Worldbuilding, Characters, Tone and IP

A game world exists to make the player's verbs meaningful, and its characters exist to give the player someone to care about, follow, help or beat. This file turns that into documents and procedures: mechanics-first worldbuilding, the world bible (with a template and canon tiers), naming, character design (function, motivation, contradiction, archetypes used as functions, visual identity, voice identity, arcs that work in live games), cast design, the tone bible (axes, calibration lines, content boundaries), and building a durable IP (premise engines, mascot ladders, consistency, legal ownership and AI-content caveats). A running example — *Lantern Harbour*, a merge-2 restoration game with a mystery spine — shows each document filled in. Visual execution belongs to `art-direction`; voice production belongs to `audio-direction` and `ai-audio-pipeline`; this file defines *what* the world and cast are so those disciplines can execute consistently.

## Contents

1. Mechanics-first worldbuilding
2. The world bible — structure, template, canon tiers
3. Naming
4. Character design — function, core, contradiction
5. Archetypes as functions
6. Visual identity
7. Voice identity
8. Character arcs in finite and live games
9. Cast design
10. The tone bible
11. Building an IP
12. Worldbuilding for live games — canon at scale
13. Worked example: *Lantern Harbour* bible on a page
14. Checklists
15. Volatile facts

---

## 1. Mechanics-first worldbuilding

The commonest worldbuilding failure in game teams is building a world *then* bolting a game onto it. Seniors work the other way round: start from the verbs and the loop, then ask what world makes those verbs natural, desirable and repeatable.

**The five world questions (answer in order):**

1. **Why can the player do the core verb here?** (Why are there merge-able objects washing up on the beach? Because the storm scattered the town's belongings across the coast.)
2. **Why must they keep doing it?** (The town is still broken; every restored building reveals more.)
3. **What does progress change in the world?** (Visible restoration; returning townsfolk; the lighthouse beam reaching further each chapter.)
4. **Who wants something from the player, and who opposes it?** (Townsfolk want their homes back; a developer wants the harbour empty.)
5. **What is the one big lie?** The single fantastical or exaggerated premise the audience is asked to accept — everything else should follow believable rules. (A storm scattered a whole town's belongings in mergeable pieces. Nothing else is magical.)

**Rules of thumb:**

| Rule | Meaning | Test |
|---|---|---|
| Iceberg | Write 10× more than you show; show the 10% that serves play | Can a player understand everything shown without the 90%? |
| Specificity over scope | One vivid harbour beats a vague continent | Can you name three smells, sounds and objects of the place? |
| Conflict in the world | Factions with competing wants generate stories for free | Does every faction want something another faction blocks? |
| Rules have costs | Powers and technologies are defined by limits | Brandon Sanderson's essays on magic systems (2007 onward) argue limitations are more interesting than powers and that a problem solved by an ability is satisfying only if the audience understands the ability |
| Expand before adding | Deepen existing elements before introducing new ones | Is this new faction/creature needed, or can an existing one grow? |
| Serve the art pipeline | Every world element implies art cost | Does the world need 40 unique building types, or 8 types × 5 variations? |

## 2. The world bible

### 2.1 What it is for

A world bible is the **single source of truth** for canon, so that writers, artists, audio, UA, community and AI-assisted pipelines produce consistent output. It is not a novel. Its success measure is: *a new team member (or an agent) can produce on-canon content after reading it for 30 minutes.*

### 2.2 Size targets

| Project | Bible size | Notes |
|---|---|---|
| Hypercasual / hybrid-casual | 1 page | Premise, character, tone, taboo list |
| Casual meta-story | 5–15 pages + character sheets | Plus a story outline mapped to levels |
| Story app series | 15–40 pages per series | Plus route maps and relationship charts |
| RPG / gacha / live IP | 40–200+ pages, as a wiki | Plus a lore database and canon tiers |

Start with the **bible on a page** (§13) and grow only where production needs answers.

### 2.3 Template

```markdown
# <Game> World Bible  (version, date, owner)

## 0. Bible on a page   (logline, premise, one big lie, tone in 3 words, cast list, macro question)
## 1. Premise and player fantasy   (mirror contract.json: meta.logline, player_fantasy, pillars)
## 2. The one big lie and the rules   (what is fantastical; what is NOT; costs and limits)
## 3. Setting   (places as playable spaces: each with mood, function in the loop, art notes, audio notes)
## 4. History   (only what the story uses; a dated timeline; what characters believe vs what is true)
## 5. Factions and forces   (want, method, resources, relationship to player, visual motif)
## 6. Cast   (one line each; link to character sheets)
## 7. Tone   (link to tone bible; three adjectives; the darkest permissible moment)
## 8. Language   (naming palettes, glossary, invented terms with pronunciation, words we never use)
## 9. Visual and audio hooks   (motifs, colour meanings, signature sounds — hand-off to art/audio bibles)
## 10. Taboos and boundaries   (content limits by age rating; cultural sensitivities; real-world references to avoid)
## 11. Canon tiers and open questions   (see 2.4)
## 12. Change log   (date, change, reason, impacted assets)
```

### 2.4 Canon tiers

Live games accumulate contradictions. Label every fact:

| Tier | Meaning | Who can change it | Example |
|---|---|---|---|
| **Core canon** | Load-bearing facts; changing them breaks the game or marketing | Narrative lead + game director | Grandma Eda kept the lighthouse for 40 years |
| **Soft canon** | True unless a later story needs otherwise | Narrative lead | Mr. Hale has a sister inland |
| **Flavour** | Item descriptions, barks, event jokes; may contradict mildly | Any writer, with review | Pip the cat dislikes Tuesdays |
| **Open question** | Deliberately undecided — keep a list so writers do not decide by accident | Narrative lead decides when needed | Who sent the message in the bottle? |
| **Retired** | No longer canon; keep for reference to avoid reuse | Narrative lead | The original "sea witch" concept |

### 2.5 Keeping it alive

- Store it next to the game (`docs/narrative/world-bible.md` in the project, referenced from the contract — see SKILL.md "Using the ontology").
- Every merged story change updates the bible in the same change; reviews reject content that introduces facts without a bible entry.
- Quarterly "bible bloat" pass: move unused detail to an appendix; keep the first page current.
- For AI-assisted drafting, the bible's first page plus the relevant character sheets are the context pack; keep them short enough to fit (a few thousand words).

## 3. Naming

| Criterion | Rule | Check |
|---|---|---|
| Phonetic palette | Each culture/faction gets a sound palette (syllables, endings, consonant clusters) | Ten names from the palette feel related |
| Pronounceability | Players can say it after one reading | Read aloud by three people; all agree on pronunciation |
| Distinctiveness | Main cast names start with different letters and have different lengths/shapes | No two main names share first letter + syllable count |
| UI length | Main cast names ≤ 10–12 characters (name tags, notifications, chat) | Fits name tag at minimum font size, plus 30% |
| Localisation | No unfortunate meanings in target languages; avoid letters that need diacritics if the font cannot render them | Native-speaker check for each storefront locale |
| Gender and number | In gendered languages, names and titles affect grammar | Translator notes per character (gender, pronouns, formality level) |
| Searchability | Game and hero names are googlable and ASO-friendly | Search engine and store search show no dominant conflicting product |
| Legal | No conflict with trademarks in the category | Trademark clearance before marketing spend (see §11.6) |
| Real people | Never name characters after real public figures; avoid real living private persons | Reviewer check |

**Running example palette (Lantern Harbour):** coastal, warm, slightly old-fashioned English: short names with soft consonants (Maya, Eda, Pip, Hale, Rosalind, Ned). Antagonist faction (the developers): clipped corporate names and acronyms (Vantis Holdings, Mr. Kessler).

---

## 4. Character design — function, core, contradiction

### 4.1 Function first

Every character must earn its art, writing, localisation and VO cost by doing a job in the game.

| Function | Job in the loop | Typical mobile form |
|---|---|---|
| **Guide / mentor** | Teaches mechanics, explains goals, delivers FTUE | Butler, grandparent, ship's captain, robot assistant |
| **Protagonist (directed)** | The character the player steers; carries the arc | Renovation heroine, detective |
| **Client / requester** | Generates goals (orders, makeovers, requests) | Townsfolk with requests; makeover clients |
| **Rival** | Personalises competition; comic tension | Neighbouring farmer, rival chef |
| **Antagonist** | Gives progress direction and stakes | Developer who wants the land, comic villain king |
| **Companion / mascot** | Emotional anchor, reacts to performance, brand face | Pet, sidekick, mascot creature |
| **Vendor / service** | Fronts a shop or system | Shopkeeper, gacha "summoner" |
| **Comic relief** | Releases tension, carries barks | Clumsy assistant, chatty bird |
| **Mystery figure** | Embodies the macro question | Missing grandmother, masked stranger |

**Rule:** if a character's function can be removed without changing any goal, reward or feeling, merge or cut them. Casual metas typically need **3–7 core characters**; more dilutes attachment and multiplies art cost.

### 4.2 The character core

| Field | Question | Lantern Harbour — Maya |
|---|---|---|
| Want (external goal) | What do they actively pursue? | Relight the lighthouse and find Grandma Eda |
| Need (internal) | What must they learn or accept? | That she cannot fix everything alone — she must let the town help |
| Flaw | What gets in the way, from inside? | Stubborn self-reliance; hides worry behind jokes |
| Wound / backstory pressure | What past event explains the flaw? (screenwriting convention; use lightly) | Left the harbour at 16 after a fight with Eda; never apologised |
| Contradiction | Which two traits pull against each other? | Practical engineer who keeps every sentimental scrap |
| Values | What will they not do? | Will not sell the town's heritage, even to save it |
| Fear | What do they avoid? | That Eda left because of her |
| Secret | What do they hide? (fuel for later reveals) | She has Eda's last unopened letter |
| Signature behaviour | What do they *do* that only they do? | Fixes things with hair clips; talks to tools |
| Relationship web | How do they relate to each core character? | Teases Mr. Hale; protective of Pip; wary of Kessler |

**Contradiction is the engine of interest.** A character with only consistent traits (kind, brave, loyal) is a mascot, which is fine for a mascot but flat for a protagonist. One well-chosen contradiction generates dozens of scenes.

### 4.3 Character sheet template

```markdown
# <Name>   (id: <snake_case>, tier: core|support|guest)
Function: <from table 4.1>          Appears: <chapters/areas/events>
One line: <who they are in ≤ 15 words>
Want / Need / Flaw / Contradiction / Values / Fear / Secret: <one line each>
Arc: <positive|flat|negative> — start belief → end belief (or: what they change in others)
Signature behaviour: <2–3 concrete actions>
Voice: <see voice chart>; sample lines: 3 "golden" lines, 1 "never says"
Visual: silhouette notes, dominant colour, signature prop, shape language, expression set needed
Relationships: <name — attitude — tension>
Localisation notes: gender/pronouns, formality register, name pronunciation, wordplay to transcreate
Do / Don't: <behaviour rules for writers, artists, UA>
Assets: portrait set ids, VO voice id (if any), manifest refs
```

---

## 5. Archetypes as functions

Archetypes are useful as **roles in the structure**, not as personalities. Vogler's adaptation of Jungian archetypes (*The Writer's Journey*, 1992) names several functions — mentor, herald, threshold guardian, shapeshifter, shadow, trickster, ally — that any character, place, object or system can hold at a given moment.

| Function | Narrative job | Can be held by | Mobile casual example |
|---|---|---|---|
| Herald | Announces change; issues the call | Letter, phone message, storm | The letter in Grandma's handwriting |
| Mentor | Gives tools and knowledge | Guide character, tutorial system | Mr. Hale teaching the merge board's rules in character |
| Threshold guardian | Tests commitment before a new area | Hard level, gatekeeper NPC | The harbourmaster demands the dock be fixed first |
| Shapeshifter | Loyalty or truth is uncertain | Charming stranger, rival | Kessler, who may know where Eda is |
| Shadow | Embodies what the hero fears becoming | Antagonist, dark mirror | A former keeper who abandoned another town |
| Trickster | Disrupts, mocks, reveals | Comic sidekick, pet | Pip, who keeps knocking clues off shelves |
| Ally | Helps and humanises | Townsfolk, team members | Rosalind the baker |

**Archetype vs stereotype.** An archetype is a function; a stereotype is a lazy bundle of traits attached to a group. Test: if the character's traits are predictable from their gender, ethnicity, age, body or disability, rewrite. Subvert by keeping the function and changing the expected texture (the mentor is a nervous 12-year-old radio enthusiast; the shadow is kind and believes he is helping).

**Mobile casual archetype patterns that recur** (use knowingly, then give each a contradiction):

| Pattern | Why it works on mobile | Freshening move |
|---|---|---|
| Competent, unflappable helper (butler, assistant) | Explains goals without friction | Give them a secret life or a comic weakness |
| Grumpy-but-loving elder | Instant warmth via reveals of softness | Let the softness be earned slowly, not every scene |
| Plucky protagonist returning home | Universal "restoration" fantasy | Give them a real reason they left |
| Comic villain | Stakes without darkness | Give a sympathetic motive the player discovers |
| Expressive pet/mascot | Reads without text; brand face; ad-friendly | Give it a consistent "rule" of behaviour (e.g. always steals one thing) |

---

## 6. Visual identity

Execution belongs to `art-direction`; narrative supplies the *brief*. A character's look must communicate function and personality at **phone scale** — name tags, portraits of 64–256 px, map icons, notification thumbnails and 3-second ads.

| Tool | Rule | Test |
|---|---|---|
| **Silhouette** | Recognisable as a solid black shape; distinct from every other cast member | Fill black, shrink to ~64 px, line the cast up: each identifiable |
| **Shape language** | Round = friendly/safe, square = stable/stubborn/strong, triangle/spikes = dynamic/dangerous (animation convention) | Does the dominant shape match the character's function? |
| **Dominant colour** | One dominant hue per main character, distinct in value as well as hue (colour-blind safety) | Greyscale test: values still separate the cast |
| **Signature prop** | One object that is "theirs" | Prop alone evokes the character (Maya's hair-clip toolkit) |
| **Proportions** | Head-to-body ratio sets register: ~1:2–1:3 cute/chibi; ~1:5–1:6 stylised; ~1:7–1:8 heroic/realistic | Matches tone bible and audience |
| **Face readability** | Large eyes/brows/mouth for expression at small sizes | Expression readable at portrait size on a 6" phone |
| **Expression set** | Budget by need: casual meta 6–8; VN 8–15 per main character | List each expression's use before ordering art |
| **Costume variants** | Seasonal/event outfits keep the silhouette and dominant colour | Variant still passes the silhouette test |

Valve's paper on *Team Fortress 2*'s illustrative rendering (Mitchell, Francke and Eng, 2007) is a well-known articulation of silhouette- and value-led character readability; the principles transfer directly to small screens.

**Narrative → art brief (per character):** function, three personality adjectives, one contradiction to show visually, dominant colour and its meaning, signature prop, shape language, age/body/register, expression list with use cases, poses needed, do/don't (e.g. "never shown angry at the player").

---

## 7. Voice identity

| Dimension | Options | Maya | Mr. Hale | Pip (barks only) |
|---|---|---|---|---|
| Sentence length | Short / medium / long | Short, quick | Long, rambling | — |
| Register | Formal / neutral / casual / slang | Casual | Formal, old-fashioned | — |
| Vocabulary | Technical, poetic, plain, invented | Technical (tools) | Nautical | — |
| Humour | Wordplay, deadpan, self-deprecating, none | Self-deprecating | Deadpan | Physical |
| Emotional expression | Open / guarded / deflecting | Deflects with jokes | Guarded | — |
| Verbal signature (use rarely) | A phrase, tic or construction | "Okay. Okay okay okay." when stressed | Calls everyone "lad" or "lass" — retire if it localises badly | Meows encoded as text sound-effects |
| Never says | Words/phrases off-limits | Never swears; never says "magic" | Never says "sorry" directly | — |

**Cover-the-name test:** remove name tags from a page of dialogue. A reviewer should identify each speaker correctly from voice alone. If not, sharpen sentence length, register and vocabulary first — they survive translation better than catchphrases.

**Localisation-safe voice:** dialects, puns and catchphrases do not translate; voice built from *sentence length, formality and attitude* does. Give translators a voice chart per character and permission to transcreate signature lines.

---

## 8. Character arcs in finite and live games

K. M. Weiland (*Creating Character Arcs*, 2016) distinguishes **positive change**, **flat** and **negative change** arcs. The flat arc — a character whose core belief is already right and who changes the world around them — is the secret weapon of live games.

| Arc | Shape | Fits | Example use |
|---|---|---|---|
| Positive change | Believes a lie → confronts it → embraces a truth | Protagonist of a finite story or season | Maya learns to accept help (season 1) |
| Flat | Holds a truth → the world tests it → the world changes | Mascots, guides and protagonists of forever-running games | Pip never changes; Mr. Hale's steadiness changes Maya |
| Negative change | Rejects a truth → worsens | Antagonists, tragedies, mature stories | A former keeper who chose profit |

**Live-game rule:** core cast members who must persist for years should run **flat arcs or slow, reversible arcs**; transformative arcs belong to **guest characters per season/event** and to the protagonist **per season** (with a new flaw surfaced next season). Completing a core character's arc too early leaves nothing to write.

---

## 9. Cast design

**Contrast matrix.** Place core cast on two axes that matter to the tone (e.g. *warm ↔ cool* and *orderly ↔ chaotic*). Each quadrant should hold at most one core character; empty quadrants are opportunities.

```
             orderly
    Mr. Hale    |   Kessler
   (warm-gruff) | (cool-polished)
 warm ----------+---------- cool
    Maya, Pip   |   (empty: a cool chaotic
   (warm-messy) |    character? the bottle sender?)
             chaotic
```

**Cast checks:**

- [ ] Every core character has a distinct function, silhouette, dominant colour and voice.
- [ ] At least one relationship has ongoing tension (rivalry, secret, unresolved past).
- [ ] The cast reflects the audience thoughtfully; representation is specific, researched and reviewed by people with lived experience where it matters (sensitivity review), not tokenistic.
- [ ] Content suits the age rating; romance, violence and substance references follow the tone bible's boundaries.
- [ ] Antagonists have a comprehensible motive; comic villains still want something specific.
- [ ] The cast size fits art and VO budgets (each core character × expressions × outfits × localisation).

---

## 10. The tone bible

### 10.1 What it is for

Tone is a contract with the audience about what kind of experience this is — how funny, how dark, how sincere. Tone mistakes (a grim beat in a cozy game, sarcasm in a children's game, a joke at a tragic moment) break trust faster than plot holes. A tone bible makes tone **testable** for writers, artists, audio, UA, community managers and AI-assisted drafting.

### 10.2 Tone axes

Score each axis 1–5 and write one sentence of interpretation.

| Axis | 1 | 5 | Lantern Harbour |
|---|---|---|---|
| Comic ↔ serious | Slapstick | Grave | 2 — warm humour, sincere at key moments |
| Cozy ↔ tense | Safe, slow | Threatening | 2 — mystery without danger |
| Grounded ↔ fantastical | Realistic | High fantasy | 2 — one big lie, otherwise real |
| Sincere ↔ ironic | Earnest | Knowing, sarcastic | 2 — earnest, gently self-aware |
| Family ↔ mature | All ages | Adult | 2 — family-friendly, adult nostalgia |
| Sparse ↔ verbose | Minimal text | Prose-rich | 2 — short lines, few words |

### 10.3 Tone bible template

```markdown
# <Game> Tone Bible
Three words: <e.g. warm, curious, bittersweet>
Axes: <table 10.2 with one-sentence interpretation each>
Humour: <kinds allowed: wordplay | situational | physical | deadpan; who we never joke about; punch up, not down>
Emotional range: <emotions allowed; the darkest permissible moment, described concretely>
Content boundaries: <violence, romance, substances, fear, real-world issues — mapped to the target age rating>
Language: <reading level, sentence length targets, banned words, profanity policy, emoji policy in UI>
Golden lines: <5–10 lines that are exactly on tone, across characters>
Rejected lines: <5–10 near-misses with why they are off-tone>
UI & system voice: <how buttons, errors, offers, push notifications sound — consistent with the world>
Monetization voice: <how offers speak; no guilt, no false urgency; no character pleading for money>
Cross-discipline hooks: <colour mood, music mood words, SFX character> → art bible / audio bible
```

### 10.4 Calibration with golden and rejected lines

Golden/rejected pairs are the fastest way to align a team (and an AI drafting model). Example for Lantern Harbour:

| Golden | Rejected | Why rejected |
|---|---|---|
| MAYA: "The roof's fixed. Mostly. Don't lean on the left side." | MAYA: "Wow!!! The roof looks AMAZING now!!!" | Over-excited, generic, shouty caps |
| HALE: "Your grandmother never asked for help either. Runs in the family." | HALE: "You're a stubborn little brat, just like that old hag." | Cruel; breaks family tone |
| PIP: *knocks the map off the table — onto the exact cove we needed* | PIP: "Meow! I'm such a silly kitty!" | Pip does not talk; breaks the established rule |
| Offer: "Rosalind baked extra today — the Harbour Bundle is in the shop." | Offer: "Rosalind is STARVING. Only YOU can save her. 2 hours left!" | Guilt and false urgency (doctrine forbids) |

### 10.5 Tone across the product

| Surface | Tone rule |
|---|---|
| Push notifications | In-world but never guilt-based ("Pip found something on the beach" not "Pip misses you and is sad") |
| Offers and shop | Warm, honest, no pressure; prices and contents stated plainly |
| Error and system messages | Plain language first; light flavour optional and never at the cost of clarity |
| Store page and ads | Same tone as the game; misrepresentation of tone is a form of misleading advertising |
| Community and support | Tone-consistent but human; never role-play a character when handling refunds or complaints |
| Age-rating fit | Tone bible boundaries align with the rating questionnaire answers kept in `legal-ethics` |

---

## 11. Building an IP

### 11.1 What "IP" means for a game team

In practice a game IP is the bundle of **characters, world, name, visual signature and premise** that audiences recognise and that can travel beyond one game — into sequels, spin-offs, ads, merchandise, animation and collaborations. Mechanics alone rarely constitute protectable or recognisable IP; characters and look do.

### 11.2 The premise engine

Durable IPs have a **situation that generates endless episodes** without explanation. Test your premise against these questions:

| Question | Weak premise | Strong premise |
|---|---|---|
| Can it be shown in one image? | "An epic saga of five kingdoms" | Birds versus pigs who stole their eggs |
| Does it imply a repeatable conflict or task? | "A girl's emotional journey" | A creature who must be fed candy; a town that needs restoring |
| Does it work without words? | Requires lore to understand | Readable in a 3-second ad, muted |
| Can new episodes be made without breaking it? | The story ends when the plot resolves | Every week there is a new room, client, mystery or rival |
| Does it have an emotional core? | Pure spectacle | Protecting family, restoring home, friendship |

Examples of premise-driven mobile IPs that extended beyond their original game: *Angry Birds* (Rovio, 2009; feature film 2016), *Cut the Rope*'s Om Nom (ZeptoLab, 2010; animated shorts and spin-off games), *Talking Tom* (Outfit7, 2010; an animated series and a family of apps), and *Clash of Clans* (Supercell, 2012), whose characters carried into *Clash Royale* (2016) and animated shorts. Each pairs a simple, wordless premise with a strongly designed character.

### 11.3 The IP ladder

| Rung | What exists | Investment | Unlocks |
|---|---|---|---|
| 1. Premise | A situation and a look | Concept art, logline | UA tests of the premise (creative tests before the game exists are common in mobile) |
| 2. Mascot | One recognisable character with rules | Model sheet, expression set, behaviour rules | Ads, icon, store presence, social content |
| 3. Cast | 3–7 characters with relationships | Character sheets, voice chart | Story beats, events, character-led offers |
| 4. World | Places, factions, history | World bible, canon tiers | Seasons, spin-off modes, collaborations |
| 5. Franchise | Multiple products sharing canon | IP bible, brand guidelines, licensing process | Sequels, merch, animation, partnerships |

Do not build rung 5 documents before rung 2 has proven appeal. Most mobile IPs that travel were mascot-first.

### 11.4 Consistency at scale

- **Model sheets and turnarounds** for every core character (front, side, back, 3/4) plus expression and pose libraries — the visual canon.
- **Behaviour rules** — a short list of what each character always/never does (Pip never talks; Maya never gives up on someone). These keep ads, events and community art on-model.
- **Brand guidelines** — logo usage, colours, typography, character usage in marketing.
- **Approval flow** — anything showing core characters (ads, collaborations, merch) passes a narrative + art review.
- **AI-assisted pipelines** — character consistency across hundreds of images needs reference sheets, style references and often fine-tuned adapters; see `ai-asset-pipeline`. Record provenance for every asset in `.gamestudio/assets/manifest.json`.

### 11.5 IP and marketing

Characters are the cheapest marketing asset a game owns: they make creatives recognisable, give UA a face, carry social content and make store screenshots tell a story. Brief UA with the character rules and tone bible; ads that misrepresent characters or gameplay erode trust and invite regulatory action (see `references/mobile-narrative.md` §7 and `marketing-ua`).

### 11.6 Owning the IP — legal basics (not legal advice; see `legal-ethics`)

| Asset | Typical protection | Action |
|---|---|---|
| Game title, logo, main character names | Trademark (registered per country/class) | Clearance search before spending on marketing; file in key markets |
| Art, text, music, code | Copyright (arises on creation, with human authorship) | Keep source files, dated drafts and contributor agreements |
| Contributor work | Contracts (work-for-hire / assignment) | Every freelancer and contractor signs an assignment |
| AI-generated material | Weak or no copyright where there is no meaningful human authorship (US position; see §15) | Make human authorship real: human-written dialogue, human-edited art, human selection and arrangement; record provenance |
| Real people and brands | Rights of publicity, trademark, defamation | No real persons or brands without licences |
| Cultural material | Not "IP" in the legal sense, but a reputational risk | Consult and credit; avoid sacred or culturally specific elements used as decoration |

---

## 12. Worldbuilding for live games — canon at scale

| Problem | Symptom | Practice |
|---|---|---|
| Contradictions accumulate | Players post side-by-side screenshots of conflicting lore | Canon tiers (§2.4); lore database with ids; review gate on core-canon changes |
| Writers decide open questions by accident | A throwaway event line "answers" the macro mystery | Maintain the open-questions list; flag in review |
| Seasonal lore bloat | New factions every season, none developed | "Expand before adding": each season deepens one existing element and adds at most one new one |
| Community theorises faster than you write | Fans guess the twist | Plant red herrings fairly; keep at least two viable explanations alive; never retcon to dodge a correct guess unless the story improves |
| Retcons | A change invalidates earlier content still in the game | Retcon policy: only for quality or sensitivity reasons; update or remove affected content; changelog |
| Staff turnover | New writers break voice | Voice charts, golden/rejected lines, and the bible on a page as onboarding |
| Event stories disappear | Players who missed an event lose story context | Story archive or "memories" album; recap the event in the next chapter's opening |

**Lore database (lightweight).** A JSON or spreadsheet table of entities is enough for most mobile games:

```json
{"id": "char_eda", "type": "character", "name_key": "char.eda.name", "tier": "core",
 "facts": [
   {"id": "eda_keeper_years", "text": "Kept the lighthouse for 40 years", "tier": "core", "source": "ch1_s03"},
   {"id": "eda_sold_light", "text": "Sold the lighthouse to Vantis before vanishing", "tier": "core", "source": "ch3_s12"}],
 "open_questions": ["Why did Eda sell?", "Who sent the bottle?"],
 "first_appearance": "cold_open", "assets": ["portrait_eda_neutral"]}
```

Facts carry their **source scene id**, so a script search finds every place a fact is stated when it changes.

---

## 13. Worked example: *Lantern Harbour* bible on a page

```markdown
# Lantern Harbour — Bible on a page (v0.3)
Logline: Return to your storm-wrecked childhood harbour, merge the town's scattered
         belongings back into shape, and relight your grandmother's lighthouse.
Player fantasy: You restore a place you love and bring its people home.
Pillars: Restoration you can see · A town that remembers you · A mystery worth returning for
One big lie: The storm scattered a whole town's belongings in mergeable pieces along the coast.
Rules: No magic. No deaths shown. Danger is weather and money, never violence.
Macro question: Where is Grandma Eda, and why did she sell the lighthouse?
Tone: warm · curious · bittersweet (axes: comic 2, tense 2, fantastical 2, ironic 2, mature 2)
Darkest permissible moment: the storm memory — loss implied, never shown; no one is hurt on screen.
Cast (core 5):
  Maya   — protagonist (directed); engineer; jokes to deflect; arc: accept help (positive)
  Eda    — mystery figure; absent keeper; seen in letters and memories
  Hale   — mentor/threshold guardian; gruff harbourmaster; flat arc (steadiness)
  Pip    — mascot/trickster; dock cat; never talks; always steals one thing per chapter
  Kessler— antagonist/shapeshifter; Vantis Holdings rep; wants the harbour; secretly knew Eda
Places: cottage → docks → market → cliffs → lighthouse (one area per sequence; 8–15 tasks each)
Factions: Townsfolk (want homes back) · Vantis Holdings (want the harbour empty for a resort)
Visual hooks: lighthouse beam = progress motif; warm lamp-orange vs storm-blue palette
Audio hooks: gulls, rigging creak, a music-box motif for Eda's memories
Taboos: no guilt notifications; no character pleads for money; no real-world brands; no romance in season 1
Open questions: who sent the bottle? does Kessler know where Eda is?
```

Contract mapping (see SKILL.md "Using the ontology"): `meta.logline`, `player_fantasy`, `meta.pillars`, `content.characters` (objects with ids and `bible_ref`), `content.worlds` (the five areas), `art_direction.bible_ref`, `audio_direction.voice`.

---

## 14. Checklists

**World bible ready for production**
- [ ] Bible on a page exists and matches `contract.json` (logline, fantasy, pillars).
- [ ] The five world questions are answered, with the one big lie stated and its limits written.
- [ ] Each place is described as a playable space with its loop function and art/audio notes.
- [ ] Each faction has a want, a method and a relationship to the player.
- [ ] Canon tiers and the open-questions list exist.
- [ ] Taboos and content boundaries map to the target age rating.
- [ ] Naming palette, glossary and pronunciation guide exist; names pass the localisation and trademark checks.

**Character ready for art and writing**
- [ ] Function is clear and non-redundant.
- [ ] Want, need, flaw, contradiction, values, fear, secret written.
- [ ] Arc type chosen deliberately (flat for long-lived live-game cast).
- [ ] Silhouette, dominant colour, shape language, signature prop and expression list briefed.
- [ ] Voice chart row, golden lines and "never says" written; cover-the-name test passed.
- [ ] Localisation notes (gender, pronouns, formality, transcreation permission) written.
- [ ] Do/don't behaviour rules written for writers, artists and UA.

**Tone bible ready**
- [ ] Axes scored with interpretations; three words chosen.
- [ ] Darkest permissible moment described concretely.
- [ ] ≥ 5 golden and ≥ 5 rejected lines with reasons.
- [ ] UI, push, offer and store voice rules written; monetization voice forbids guilt and false urgency.

**IP readiness**
- [ ] Premise passes the one-image, wordless, repeatable-situation tests.
- [ ] Mascot or lead character has model sheets and behaviour rules.
- [ ] Trademark clearance done for title and lead names before marketing spend.
- [ ] Human authorship is real for key creative assets; provenance recorded.

---

## 15. Volatile facts (as of Oct 2026 — verify before relying)

- **US copyright and AI-generated material.** The US Copyright Office's position is that purely AI-generated material is not copyrightable and that human authorship is required (affirmed in *Thaler v. Perlmutter*, D.C. Cir.); its Part 2 report on copyrightability (29 January 2025) states that prompts alone do not provide sufficient control; in the *Zarya of the Dawn* registration, AI-generated images lost protection while human-written text and arrangement remained protected — [Promise Legal summary](https://blog.promise.legal/ai-game-assets-copyright-steam-disclosure-2026/). Other jurisdictions differ; consult `legal-ethics` and counsel.
- **Steam AI disclosure.** Valve revised its AI disclosure rules in mid-January 2026: player-facing AI-generated content (including in-game text), store assets and marketing materials must be disclosed, while internal development tools no longer require disclosure — [Gigazine](https://gigazine.net/gsc_news/en/20260120-steam-updates-ai-disclosure-guidelines); [Notebookcheck](https://www.notebookcheck.net/Steam-updates-AI-disclosure-form-requiring-developers-to-report-visible-and-in-game-AI-but-not-background-tools.1206103.0.html). Mobile store rules on AI disclosure are less explicit; see `legal-ethics` and `store-release`.
