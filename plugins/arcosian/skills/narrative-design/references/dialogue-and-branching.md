# Dialogue Systems, Branching and Writing for the Screen

This file is the implementation-side handbook for interactive dialogue: the anatomy of a dialogue system, how to choose between Ink, Yarn Spinner, Dialogic (Godot), Godot Dialogue Manager, articy:draft, Twine, Ren'Py or a plain JSON beat table, how each text-first format works with original examples, the catalogue of branching structures with cost formulas, choice design, state tracking and save/migration, barks with repetition mathematics and rule-based selection, UI-length writing with reading-speed formulas, localisation-ready writing (IDs, placeholders, plurals, gender, expansion, pseudo-localisation), voice-over decisions for mobile, and a QA procedure built on `scripts/narrative_lint.py`. Branching *mechanics* (dialogue choice, relationship meters, premium choices, storylets) have mechanic cards in `skills/mechanics-codex/references/10-narrative-exploration-mechanics.md`; this file is about building and writing them well. Tool versions and prices are volatile and collected in §15 with sources.

## Contents

1. Anatomy of a dialogue system
2. Choosing a tool — comparison and decision table
3. Ink
4. Yarn Spinner
5. Dialogic 2 and Godot Dialogue Manager (Godot)
6. When a plain JSON beat table is the right answer
7. Branching structures — catalogue and cost maths
8. Designing choices
9. State tracking, saves and migration
10. Barks — triggers, selection, repetition maths
11. UI-length writing and reading speed
12. Localisation-friendly writing
13. Voice-over for mobile narrative
14. Dialogue QA procedure and telemetry
15. Volatile facts

---

## 1. Anatomy of a dialogue system

| Layer | Responsibility | Must-haves on mobile |
|---|---|---|
| **Script data** | Lines, speakers, choices, conditions, effects, tags/metadata | Text-first, diffable files; stable line IDs |
| **Compiler / validator** | Parse, type-check variables, detect dead ends and missing targets | Runs in CI; failures block the `static` gate |
| **Runtime (runner)** | Steps through content, evaluates conditions, applies effects, exposes current line and choices | Deterministic; save/restore at any line boundary |
| **Variable storage** | Flags, counters, affinities, visit counts; bridge to game state | Single source of truth shared with the game's save system |
| **Presenter / view** | Text box, name tag, portraits, typewriter, choice buttons, backlog, auto/skip | Thumb-reachable choices; tap-to-complete then tap-to-advance; skip and log |
| **Command bridge** | Script tells the game to do things (play SFX, show item, change portrait, give reward) | Commands are data (tags/commands), never ad-hoc code in scripts |
| **Localisation** | String tables keyed by line ID; per-locale fonts; plural/gender handling | No concatenation; translator context; pseudo-locale in CI |
| **Voice-over** | Line ID → audio file; lip/portrait animation; subtitle sync | Captions always available; VO optional; per-line fallback to text |
| **Analytics** | Beat seen, choice made, skip, time on beat | Event names in the taxonomy (§14) |

**Data model for one line (tool-agnostic):**

```json
{"id": "ch1_dock_hale_001", "speaker": "hale", "text_key": "ch1_dock_hale_001",
 "tags": {"mood": "gruff", "portrait": "hale_neutral", "vo": "vo/en/ch1_dock_hale_001.ogg"},
 "conditions": null, "effects": null, "max_chars": 120, "context": "dialogue",
 "note_for_translators": "Hale is gruff but fond of Maya. 'Crane' = dock crane."}
```

---

## 2. Choosing a tool

### 2.1 Comparison

| Tool | Format | Engines | Strengths | Weaknesses | Localisation | Best for |
|---|---|---|---|---|---|---|
| **Ink** (inkle) | Text markup (`.ink`), compiled to JSON | Unity (official integration), web (inkjs), Godot and Unreal via community plugins | Prose-friendly writing flow; powerful weave, variables, lists, tunnels, threads; proven in shipped premium narrative games; MIT | No built-in line-ID localisation; complex logic can hide in text; Godot/Unreal ports vary in maintenance | Weak out of the box (see §3.5) | Prose-heavy branching, premium narrative, story apps |
| **Yarn Spinner** | Text markup (`.yarn`) in nodes | Unity (primary), Godot (.NET build) and others — verify current status | Screenplay-like; line IDs and string tables built in; Yarn 3 adds node groups, saliency, enums, smart variables, `once`; MIT | Less expressive weave than Ink; Godot support requires C# | Strong (line IDs, string tables) | Character dialogue, VO-heavy games, localised games, barks/storylets |
| **Dialogic 2** | Visual timeline editor; timelines stored as files | Godot 4 only | Fast visual-novel setup; designer-friendly GUI; characters/portraits/styles built in | Still alpha (API churn); GUI-first is harder to diff/lint; Godot-only | Built-in translation support (verify) | Godot VN-style games with non-programmer writers |
| **Godot Dialogue Manager** (Nathan Hoad) | Script-like `.dialogue` files | Godot 4 | Text-first, stateless, lightweight, popular in the Godot community | Single-engine; smaller feature set than Ink/Yarn | Supports translation via Godot (verify) | Godot games needing text-first dialogue without a VN framework |
| **articy:draft X** | Visual flow + entity database; export to JSON/engine plugins | Unity, Unreal (plugins), others via export | Large-team narrative design: flow views, entities, localisation, voice-over management | Commercial licence; heavy for small mobile titles | Strong | Large RPGs, multi-writer teams |
| **Arcweave** | Browser-based collaborative flow tool | Exports and engine plugins (verify) | Collaboration, visual boards, quick prototyping | Hosted service; export fidelity varies | Varies | Prototyping and small-team planning |
| **Twine** | Browser tool; HTML stories (Harlowe, SugarCube, Chapbook) | Web | Fastest prototyping of branching ideas; huge community | Not an in-engine runtime for commercial games | Weak | Paper prototypes of branching structure |
| **Ren'Py** | Python-based VN engine | Desktop, Android; mobile builds possible (verify iOS workflow) | Complete VN engine, mature, free | A separate engine, not a dialogue layer | Built-in translation framework | Standalone visual novels |
| **Plain JSON / spreadsheet beat table** | Your own schema | Any | Simplest possible; perfect for linear casual meta-stories | No branching language; you write the validator | As good as your string table | Casual renovation/merge metas (§6) |

### 2.2 Decision table

| Situation | Choose | Reason |
|---|---|---|
| Casual meta-story: linear micro-scenes between tasks | **JSON beat table** + string table | No branching needed; trivial runtime; easiest to localise and to edit in spreadsheets |
| Unity, character dialogue, VO, 5+ locales | **Yarn Spinner** | Line IDs and string tables built in; screenplay format suits VO scripts |
| Unity or web, prose-heavy branching, small number of locales | **Ink** | Best writing flow for branching prose |
| Godot, writers want a GUI, VN presentation | **Dialogic 2** (accept alpha risk) or Dialogue Manager | Built-in VN features vs text-first simplicity |
| Godot, agent-driven pipeline, text-first, CI linting | **Dialogue Manager** or **Yarn Spinner (C#)** or **Ink via a maintained plugin** | Diffable, lintable, LLM-writable files |
| Large team, many writers, entity-heavy RPG | **articy:draft X** with export | Database and flow tooling at scale |
| Barks and storylet-style selection | **Yarn Spinner 3** (node groups + saliency) or custom rule DB (§10.4) | Built-in salience selection, or full control |
| Exploring a branching idea in a day | **Twine** | Throwaway prototype; port later |

**Agent-buildability rule:** prefer text-first formats (JSON, Ink, Yarn, Dialogue Manager). They diff in version control, can be written and reviewed by agents, and can be validated by `scripts/narrative_lint.py` and by the tools' own compilers in CI. GUI-only formats need export steps before any automated check.

---

## 3. Ink

### 3.1 Concepts in one table

| Concept | Syntax (summary) | Use |
|---|---|---|
| Knot | `=== name ===` | A scene or section; divert target |
| Stitch | `= name` inside a knot | Sub-section of a scene |
| Divert | `-> target`, `-> END`, `-> DONE` | Jump; end the story or the current flow |
| Choice (once-only) | `* [Choice text] result` | Disappears after being chosen |
| Choice (sticky) | `+ [Choice text]` | Remains available (for menus, loops) |
| Conditional choice | `* {flag} [Text]` | Shown only if the condition holds |
| Gather | `-` | Rejoin point after a set of choices (weave) |
| Global variable | `VAR name = value` | Persistent state |
| Temporary variable | `~ temp x = 1` | Local scratch values |
| Assignment / logic | `~ x = x + 1` | Change state |
| Conditional text | `{flag: text if true \| text if false}` | Acknowledge state inline |
| Alternatives | `{a\|b\|c}` sequence, `{&a\|b}` cycle, `{~a\|b}` shuffle, `{!a\|b}` once | Variation without branching (great for barks and repeats) |
| Visit counts | `{knot_name}` evaluates to times visited | "Have we been here before?" without flags |
| Tags | `#key:value` at line end | Presentation metadata: speaker, mood, VO id |
| Tunnel | `-> scene ->` … `->->` | Reusable sub-scene that returns |
| Thread | `<- section` | Merge choices from several places |
| Lists | `LIST mood = calm, (tense), angry` | Enum-like state and sets |
| External function | `EXTERNAL give_reward(id)` | Call game code; keep logic in the game |
| Multiple flows | Runtime API (since 1.0) | Parallel conversations (e.g. barks while a scene runs) |

### 3.2 Original example — a mobile-friendly scene

```ink
VAR trust_hale = 0
VAR has_key = false
EXTERNAL give_item(item_id)

=== dock_crane ===
Crane's been rusted shut since the storm. #speaker:hale #mood:gruff
* [Offer to fix it]
    Give me ten minutes and a hair clip. #speaker:maya #mood:confident
    ~ trust_hale = trust_hale + 1
    -> crane_fixed
* [Ask about Grandma]
    Fix the crane first. Then we talk. #speaker:hale #mood:guarded
    -> dock_crane
+ {has_key} [Show him the brass key]
    Where did you find that? #speaker:hale #mood:surprised
    -> key_reveal

=== crane_fixed ===
{trust_hale > 1: Not bad, lass. Not bad at all.|Huh. It works.} #speaker:hale
~ give_item("crate_marked_E")
-> DONE

=== key_reveal ===
That key opened the lamp room. Eda never let it out of her sight. #speaker:hale #mood:quiet
-> DONE
```

Points demonstrated: tags carry presentation data (the presenter reads `speaker` and `mood`); `*` choices vanish after use so "Ask about Grandma" cannot loop forever; the sticky conditional choice appears only once the key is found; conditional text acknowledges earlier choices without branching; rewards go through an `EXTERNAL` function so the game owns the economy.

### 3.3 Runtime integration (shape, not exact API)

```text
story = load_compiled_json("story.json")
bind_external("give_item", game.give_item)
on_enter_scene(knot): story.choose_path(knot)
loop:
  while story.can_continue: line = story.continue(); present(line.text, line.tags)
  if story.choices: idx = await player_choice(story.choices); story.choose_choice_index(idx)
  else: break
save(): blob = story.state.to_json()        # store with script_version
load(blob): story.state.load_json(blob)
```

The Unity integration and inkjs expose this model; check the current API names for your integration.

### 3.4 Patterns and pitfalls

| Do | Don't |
|---|---|
| One knot per scene; one stitch per beat cluster | 2,000-line knots that mix scenes |
| Presentation in tags (`#speaker`, `#mood`, `#vo`, `#sfx`) | Presentation encoded in text ("HALE (gruff): ...") |
| Game logic via `EXTERNAL` or tags interpreted by the game | Economy rules inside ink arithmetic |
| Visit counts and conditional text for acknowledgement | A new boolean for every remembered detail |
| Alternatives (`{~a\|b\|c}`) for repeated visits | Copy-pasted near-identical knots |
| Run the compiler (inklecate) in CI and treat warnings (loose ends) as failures | Ship with "ran out of content" warnings |

### 3.5 Localising Ink

Ink has no built-in string-table localisation keyed by line ID. Common approaches (verify current community tooling): (a) compile a separate story file per language from translated `.ink` sources, which keeps logic in sync only if translators never touch logic; (b) attach a stable ID tag to every line (`#id:ch1_dock_hale_001`), export lines to a string table, and swap text at runtime by ID; (c) choose Yarn Spinner when localisation scale is a primary requirement. Inline alternatives and conditional text that build sentences from fragments are the main localisation hazard — keep each variant a complete sentence.

---

## 4. Yarn Spinner

### 4.1 Concepts

| Concept | Syntax (summary) | Use |
|---|---|---|
| Node | `title: Name` header, `---` body start, `===` end | Scene / conversation |
| Line | `Character: Text` | Dialogue in screenplay form |
| Option | `-> Option text` with indented consequences | Choices |
| Conditional option | `-> Text <<if $cond>>` | Show only if the condition holds |
| Jump / detour | `<<jump Node>>`, `<<detour Node>>` (returns; Yarn 3) | Navigation |
| Variables | `$name`; `<<declare $name = 0>>`; `<<set $name to 1>>` | State |
| Flow control | `<<if>> <<elseif>> <<else>> <<endif>>` | Conditional content |
| Commands | `<<command args>>` | Call game code: animations, SFX, rewards |
| Line tags | `#line:id`, other hashtags | Localisation IDs and metadata |
| Visit tracking | `visited("Node")`, `visited_count("Node")` | Acknowledgement without flags |
| Enums (3.0) | Named value sets | Typed states such as moods or quest stages |
| Smart variables (3.0) | Declared expressions evaluated at runtime | Derived state (`$is_friend = $trust >= 3`) |
| `once` (3.0) | Content that runs only once | First-time-only lines without flags |
| Node groups + `when:` (3.0) | Several nodes share a title, each with a condition; a saliency strategy picks one | Storylets, contextual barks, reactive hub dialogue |
| Line groups (3.0) | Alternative lines from which one is picked | Bark variation |

### 4.2 Original example

```yarn
title: DockCrane
tags: chapter1
---
<<declare $trust_hale = 0>>
<<declare $has_key = false>>
Hale: Crane's been rusted shut since the storm. #line:ch1_dock_hale_001
-> Offer to fix it #line:ch1_dock_opt_001
    Maya: Give me ten minutes and a hair clip. #line:ch1_dock_maya_001
    <<set $trust_hale to $trust_hale + 1>>
    <<jump CraneFixed>>
-> Ask about Grandma #line:ch1_dock_opt_002
    Hale: Fix the crane first. Then we talk. #line:ch1_dock_hale_002
    <<jump DockCrane>>
-> Show him the brass key <<if $has_key>> #line:ch1_dock_opt_003
    Hale: Where did you find that? #line:ch1_dock_hale_003
    <<jump KeyReveal>>
===
title: CraneFixed
---
<<give_item crate_marked_E>>
Hale: Huh. It works. #line:ch1_dock_hale_004
===
```

A contextual bark using a node group (Yarn 3; check the header syntax against current docs):

```yarn
title: HaleIdle
when: $trust_hale >= 3
---
Hale: You're all right, lass. Don't tell anyone I said so. #line:bark_hale_001
===
title: HaleIdle
when: $trust_hale < 3
---
Hale: Mind the nets. #line:bark_hale_002
===
```

The game jumps to `HaleIdle`; the runtime picks the eligible, most salient variant. The same mechanism implements storylets (`references/story-structures.md` §9.4).

### 4.3 Localisation and VO workflow

1. Writers draft without IDs; the Yarn compiler's tagging step adds `#line:` IDs to every line and option (Yarn's command-line tool can do this; keep IDs stable afterwards).
2. Export string tables (CSV) per locale; translators work on text plus character, context and length metadata.
3. VO files are named by line ID; the runtime resolves `line ID → localised text + audio`.
4. Changing a line's text after recording → mark the line "needs re-record" (diff on text per ID in CI).

### 4.4 Pitfalls

- Long nodes that mix several scenes — split at scene boundaries; jumps are cheap.
- Logic-heavy commands — keep game rules in the game; commands should be verbs (`<<give_item>>`, `<<play_sfx>>`), not scripts.
- Duplicate line IDs after copy-paste — lint for duplicates (`narrative_lint.py yarn` does).
- Options without IDs — untranslatable; lint for them.

---

## 5. Dialogic 2 and Godot Dialogue Manager

**Dialogic 2** is a Godot 4 plugin built around **timelines** (sequences of events: text, choice, condition, variable set, jump, signal, portrait changes, background, music) authored in a visual editor, plus **character** resources (names, colours, portraits per expression) and **styles/layouts** for the text box. It suits visual-novel presentation in Godot when writers prefer a GUI. As of the latest release listed on its GitHub releases page, Dialogic 2 is still labelled alpha (§15) — budget for API changes between alphas, pin the version in the project, and wrap Dialogic calls behind your own interface so a later swap is cheap.

**Godot Dialogue Manager** (Nathan Hoad) takes the opposite approach: plain-text `.dialogue` files with titled sections, lines, responses, conditions and mutations, compiled by the plugin and run by a stateless manager that talks to your game state. It is text-first and lightweight — a good fit for agent-driven Godot projects that need dialogue but not a VN framework. Check the current version and Godot compatibility before adopting.

**Godot integration rules (either tool):**

| Rule | Why |
|---|---|
| Wrap the plugin in a `DialogueService` autoload with your own signals (`line_shown`, `choice_made`, `dialogue_ended`) | Swap or upgrade plugins without touching gameplay code |
| Store dialogue state in your save system, not only in the plugin | Saves survive plugin upgrades |
| Run the static gate on dialogue files (plugin compile/validate + `narrative_lint.py`) | Dialogue errors fail CI like code errors |
| Keep text in translation CSVs keyed by ID | Godot's localisation pipeline handles fonts and locale switching |

---

## 6. When a plain JSON beat table is the right answer

Most casual meta-stories (renovation, merge requests, idle milestones) are **linear micro-scenes triggered by progress**. A branching language adds runtime, tooling and training cost for no benefit. Use a beat table:

```json
{"schema_version": "1.0",
 "beats": [
  {"id": "ch1_t03_dock_crane", "unlock": {"type": "task", "value": "fix_crane"},
   "area": "docks", "kind": "task_scene", "skippable": true,
   "lines": [
     {"id": "ch1_t03_l1", "speaker": "hale", "mood": "gruff", "max_chars": 90},
     {"id": "ch1_t03_l2", "speaker": "maya", "mood": "confident", "max_chars": 90},
     {"id": "ch1_t03_l3", "speaker": "pip",  "mood": "mischief", "max_chars": 60}],
   "on_complete": {"reveal": "crate_marked_E", "next_task": "open_crate"},
   "recap_key": "ch1_recap_docks"}]}
```

Text lives in the string table keyed by line ID. The presenter queues beats on progress events and plays them only at safe states (results screen, map), as in the `progress-gated-story` mechanic card. Validation: every `next_task` exists, every line ID has text in every locale, lengths fit budgets at 130–200% expansion (`narrative_lint.py lines`).

---

## 7. Branching structures — catalogue and cost maths

Pattern names below follow Sam Kabo Ashwell's survey *Standard Patterns in Choice-Based Games* (2015), summarised and extended in our own words.

### 7.1 Catalogue

```
Linear + acknowledgement   A ─ B ─ C ─ D        (choices change lines, not scenes)

Time cave (pure tree)          ┌ C ─ ...
                           ┌ B ┤
                         A ┤   └ D ─ ...
                           └ E ┬ F ─ ...
                               └ G ─ ...

Gauntlet                   A ─ B ─ C ─ D ─ END
                               └ x     └ x       (side branches end early / fail back)

Branch and bottleneck      A ┬ B1 ┬ C ┬ D1 ┬ E
                             └ B2 ┘   └ D2 ┘     (state carried through bottlenecks)

Sorting hat                A ─ B ┬ route 1 (long, mostly linear)
                                 └ route 2 (long, mostly linear)

Hub and spoke (quest hub)  H ⇄ S1, H ⇄ S2, H ⇄ S3 → exit when conditions met

Parallel routes            common trunk → character/romance routes → shared or per-route endings

Loop and grow              A → B → C → (fail/reset) → A' with new knowledge/options

Storylet / quality-based   pool of scenes, each gated by state; selection by salience
```

### 7.2 Cost and experience

| Structure | Unique scenes (formula) | Share of content seen per playthrough | Felt agency | Best for | Watch out for |
|---|---|---|---|---|---|
| Linear + acknowledgement | n | ~100% | Low–medium (memory, flavour) | Casual metas, mascot stories | Choices that change nothing visible feel fake |
| Time cave | (b^(d+1) − 1)/(b − 1) nodes; b^d endings | (d+1) nodes of the total — vanishingly small | High | Very short gamebooks, ad-style "choose" vignettes | Exponential cost; tiny share seen |
| Gauntlet | n + failures | High | Low–medium | Survival/peril stories, tutorials | Failures that feel arbitrary |
| Branch and bottleneck | k·b·L + (k+1) bottlenecks | ~(L·k + k + 1)/total | Medium–high when state pays off | Story apps, RPG dialogue, premium narrative | Bottlenecks that ignore carried state |
| Sorting hat | trunk + r·R | ~1/r of routes | High (identity choice) | Faction or class stories | Routes must each be complete — cost × r |
| Hub and spoke | hub + Σ spokes | ~100% (order varies) | Medium (order, approach) | Investigation, cozy towns, quest hubs | Order-dependence bugs; hub fatigue |
| Parallel routes | trunk + Σ routes | trunk + one route | High (relationship) | Romance and character routes | Uneven route quality; favourite-route pressure |
| Loop and grow | base + per-loop deltas | Grows each loop | High (knowledge as progression) | Roguelites, time loops | Repetition fatigue without fast-forward |
| Storylets | pool size N | Depends on state; each run a subset | High (emergent) | Long-running, systemic, card-driven | Incoherent sequences; state explosion |

Where b = options per choice, d = choice depth, k = branch points, L = scenes per branch before rejoining, r = routes, R = scenes per route.

### 7.3 Worked cost comparison

Ten choice points, three options each, scenes of ~150 words.

| Structure | Unique scenes | Words to write | Scenes seen per run | Share seen |
|---|---|---|---|---|
| Time cave, depth 10 | (3^11 − 1)/2 = 88,573 nodes | ~13.3 million | 11 | 0.01% |
| Branch and bottleneck, L = 2 | 10 × 3 × 2 + 11 = 71 | ~10,650 | 10 × 2 + 11 = 31 | 44% |
| Branch and bottleneck, L = 1 | 10 × 3 × 1 + 11 = 41 | ~6,150 | 21 | 51% |
| Linear + acknowledgement (3 variant lines per choice) | 11 scenes + 30 variant lines | ~1,650 + ~600 | 11 (+10 variant lines) | 100% of scenes, ~82% of words |

`python3 ${CLAUDE_PLUGIN_ROOT}/skills/narrative-design/scripts/narrative_lint.py cost --structure bnb --branch-points 10 --options 3 --branch-length 2 --words-per-node 150` reproduces this table for your parameters.

**Rule of thumb:** keep 60–80% of each playthrough's content shared (consistent with the `branching-narrative` mechanic card's tuning range); below ~60% shared, writing, art, VO, localisation and QA costs multiply quickly.

### 7.4 Making cheap structures feel reactive

1. **Acknowledge immediately.** The next line responds to the choice (one variant line per option).
2. **Call back later.** A flag set in chapter 1 changes one line in chapter 4 — memory feels like consequence.
3. **Vary the bottleneck, not the plot.** The same scene plays with different attitudes, a different item, a different character present.
4. **Show the state.** Relationship icons, journal entries, a chapter-end summary of choices.
5. **Delay some payoffs.** Delayed consequence is more memorable than immediate consequence and costs no more to write.
6. **Change the ending's texture.** Endings can share structure but differ in who stands beside the protagonist and what they say.

---

## 8. Designing choices

### 8.1 Choice types

| Type | Player question | Example | Cost |
|---|---|---|---|
| **Expressive / flavour** | "How do I feel about this?" | Joke, comfort, or stay silent | Low — one variant line each |
| **Informational** | "What do I want to know?" | Ask about the key / the storm / Grandma (hub of questions) | Low–medium |
| **Tactical** | "What is the best approach?" | Sneak in or ask permission | Medium — different short scenes |
| **Relationship** | "Whom do I side with?" | Support Hale or Rosalind in an argument | Medium — affinity effects, callbacks |
| **Moral dilemma** | "What do I value?" | Sell the heirloom to save the bakery | High — real consequences expected |
| **Identity / route** | "Who am I in this story?" | Choose a profession or a romance route | Very high — routes |
| **Timed** | "Decide now" | Answer before the timer runs out | Tension; requires an accessibility toggle |
| **Premium** | "Do I pay for the richer option?" | Paid outfit or bonus scene | See the `premium-choice` mechanic card — never paywall consequences |

### 8.2 Writing choice options

| Rule | Why | Example |
|---|---|---|
| ≤ 40 characters on mobile, one line preferred | Thumb buttons; localisation expansion | "Offer to fix it" not "Tell Hale that you can probably repair the crane yourself" |
| Start with the verb or the attitude | Scannable | "Joke about it" / "Ask about Grandma" |
| Distinct intents | Three options that mean the same thing waste a decision | Avoid "Yes" / "Sure" / "Okay" |
| No misleading paraphrase | If the option paraphrases, the result must match the player's reasonable expectation; paraphrase systems that surprise players with harsh lines are a well-known failure in dialogue-wheel games | Show a tone icon when paraphrasing; or show the actual line |
| 2–4 options | Mobile decision budget (see `design-theory`) | 3 is the default |
| Silence is an option when it is meaningful | Silence expresses character | "[Say nothing]" |
| Mark locked options honestly | Players should know why something is unavailable | Greyed "Show the key (you need a key)" — or hide entirely, but be consistent |

### 8.3 Choice payoff schedule

Plan payoffs per chapter so choices feel remembered without exponential cost:

| Payoff timing | Share of choices (starting point) | Form |
|---|---|---|
| Immediate (next 1–2 lines) | ~100% | Variant reaction line |
| Same scene | ~50% | Different beat or item |
| Later chapter (callback) | ~20–30% | Line change, character attitude, small scene |
| Ending / route | ≤ 10% | Major divergence |

---

## 9. State tracking, saves and migration

### 9.1 Variable taxonomy and naming

| Kind | Example | Convention |
|---|---|---|
| Event flag (bool) | Met Kessler | `ch2_met_kessler` (chapter prefix + past-tense fact) |
| Counter | Times visited the cliffs | Prefer the tool's visit counts over hand-made counters |
| Affinity | Trust with Hale | `aff_hale` (0–100) or tier enum (`low`, `mid`, `high`) |
| Enum state | Quest stage | `q_lighthouse_stage` ∈ {`locked`, `started`, `key_found`, `done`} |
| Derived | Is friend | Smart variable / function: `aff_hale >= 60` — never stored separately |
| Inventory / world | Has brass key | Owned by the game's inventory; dialogue reads it through a function |
| Scene-temporary | Asked about the storm in this conversation | Temp/local variable — not saved beyond the scene |

### 9.2 Budget and explosion

- n independent booleans → 2^n possible states. 10 flags = 1,024 states; 20 flags = ~1 million. Testing every combination becomes infeasible beyond roughly 20 tracked variables (matching the mechanic card's ≤ 20 core variables).
- Use **tiers instead of exact values** for conditions (`aff_hale_tier >= mid`), so content checks three states, not 101.
- **Scope ruthlessly:** chapter-scoped flags can be folded into a summary enum at chapter end (`ch1_outcome` ∈ {`helped_hale`, `helped_rosalind`, `neutral`}).
- Every flag must be **read** somewhere; a flag that is set but never read is dead weight (the linter warns).

### 9.3 Saves

| Rule | Detail |
|---|---|
| Save at line or choice boundaries | Never mid-effect; resume to the same line after an interruption or OS kill |
| Save the script version | `{script_version, position (node/knot id + line id), variables, visit_counts}` |
| One source of truth | Dialogue variables live in (or are mirrored to) the game save; avoid two diverging stores |
| Autosave on every choice | Mobile apps are killed in the background without warning |
| Cloud save conflict policy | Prefer the save with the furthest story progress; never silently merge two branches |

### 9.4 Migration when content changes (live games)

When a patch edits scripts, saved positions may point at removed or renamed content.

```text
on_load(save):
  if save.script_version == CURRENT: resume(save.position); return
  if position_exists(save.position) and not in(MIGRATION_RESET_LIST, save.position): resume(save.position)
  else: resume(scene_start(MIGRATION_MAP.get(save.scene, nearest_safe_scene(save))))
  apply(MIGRATION_VARS)            # renames, defaults for new variables
  log("dialogue_save_migrated", from=save.script_version, to=CURRENT)
```

Keep IDs stable (never reuse an ID for different content), maintain a `MIGRATION_MAP` of renamed scenes, and include migration cases in playthrough tests.

### 9.5 Narrative graph format for automated checks

`scripts/narrative_lint.py graph` validates a tool-agnostic JSON graph — export one from any tool, or author small structures directly:

```json
{"schema_version": "1.0", "start": "dock",
 "variables": {"trust_hale": 0, "has_key": false},
 "nodes": [
  {"id": "dock", "words": 40, "edges": [
     {"to": "fixed", "label": "Offer to fix it", "set": {"trust_hale": "+1"}},
     {"to": "dock",  "label": "Ask about Grandma", "once": true},
     {"to": "key",   "label": "Show the key", "if": "has_key"}]},
  {"id": "fixed", "words": 25, "ending": true},
  {"id": "key",   "words": 30, "ending": true}]}
```

Checks: missing targets, unreachable nodes (structurally and under conditions), dead ends and soft-locks (a reachable state where no edge is available and the node is not an ending), unreachable endings, variables read but never declared or written, variables written but never read, bottleneck nodes, path counts and the share of content seen per playthrough.

---

## 10. Barks

### 10.1 What barks are

Barks are short, context-triggered lines outside scripted conversations: reactions to events ("Nice combo!"), state ("Running low on energy"), idle nudges, greetings, and results-screen reactions. In mobile casual games they carry character personality more cheaply than scenes, and they are the most repeated text in the game — so repetition is the main design problem.

### 10.2 Trigger model

| Field | Meaning | Example |
|---|---|---|
| Event | What happened | `level_win`, `combo_5`, `idle_20s`, `booster_used`, `first_login_today` |
| Context facts | State at the time | `attempts`, `stars`, `time_of_day`, `streak`, `chapter` |
| Speaker | Who can say it | `pip`, `hale`, `maya` |
| Priority | Interrupt rules | Story > tutorial > reaction > idle |
| Cooldowns | Global, per speaker, per category, per line | Global 8 s; per line 1 session |
| Probability | Chance to fire when eligible | 30–60% for frequent events; 100% for rare ones |

### 10.3 Repetition mathematics

For a pool of N lines and T triggers in a session:

- **Pure random with replacement:** expected distinct lines heard = N · (1 − (1 − 1/N)^T); expected repeats = T − distinct.
- **Probability of hearing no repeat at all** (birthday problem): P = N! / ((N − T)! · N^T). With N = 10 and T = 5: P = 30,240 / 100,000 ≈ 0.30 — a **70% chance of a repeat within five barks** from a ten-line pool.
- **Shuffle bag** (no repeat until the pool is exhausted; guard the boundary so the last line of one bag is not the first of the next): repeats = max(0, T − N).
- **No-repeat-last-K:** picks uniformly from N − K lines; prevents immediate repeats but not session repeats.

Worked example: a combo bark fires ~12 times per 3-minute session. With N = 12 and pure random, expected distinct = 12 · (1 − (11/12)^12) ≈ 12 · (1 − 0.352) ≈ 7.8, so ≈ 4.2 repeats per session. With a 12-line shuffle bag: 0 repeats. Shuffle bags plus a probability gate (fire 50% of the time) halve the needed pool. `narrative_lint.py barks --pool 12 --triggers 12` computes all of this.

### 10.4 Rule-based contextual selection

Elan Ruskin's GDC 2012 talk on Valve's dynamic dialogue system ("AI-driven Dynamic Dialog through Fuzzy Pattern Matching") described a database of rules, each listing criteria over world facts; on an event, the system queries all rules and plays the line whose rule matches the **most criteria**, so specific lines automatically override generic ones. A mobile-sized version:

```text
RULES = [
  {id: "pip_win_generic",  speaker: "pip",  event: "level_win", criteria: [],                                  lines: POOL_A},
  {id: "pip_win_close",    speaker: "pip",  event: "level_win", criteria: ["moves_left <= 1"],                 lines: POOL_B},
  {id: "hale_win_streak",  speaker: "hale", event: "level_win", criteria: ["streak >= 5", "aff_hale_tier >= mid"], lines: POOL_C}]
on_event(evt, facts):
  if global_cooldown_active(): return
  candidates = [r for r in RULES if r.event == evt and all(eval(c, facts) for c in r.criteria) and not cooling(r)]
  best = max(candidates, key=lambda r: (len(r.criteria), r.priority), default=None)
  if best and random() < best.probability: say(best.speaker, best.lines.next_from_shuffle_bag()); start_cooldowns(best)
```

### 10.5 Bark matrix template

| Event \ speaker | Pip (mascot) | Hale | Maya | Pool size | Cooldown |
|---|---|---|---|---|---|
| `level_win` (generic) | 8 (sound-effect text) | 6 | 6 | 20 | 1 per win, global 8 s |
| `level_win` close call | 3 | 3 | 3 | 9 | once per session per line |
| `level_fail` | 4 (comforting gestures) | 4 (encouraging) | 4 | 12 | never mock failure |
| `idle_20s` hint | 3 | — | 3 | 6 | 60 s |
| `first_login_today` | 2 | 5 | 5 | 12 | daily |

**Failure barks are tone-critical:** never mock the player, never imply they should pay to succeed ("Need a booster? 😉" after a loss is a dark pattern), and keep failure lines encouraging and specific.

### 10.6 Bark writing rules

- ≤ 50–60 characters; speech-bubble sized; readable in under 2 seconds.
- Every bark must work out of order and on its 10th hearing — avoid jokes that only land once (put those behind `once`).
- Personality through attitude, not catchphrases repeated every time.
- Sound-off: barks display as bubbles or text, never audio-only.

---

## 11. UI-length writing and reading speed

### 11.1 Length budgets (starting points — validate at minimum font size with expansion)

| Context | Budget (English source) | Notes |
|---|---|---|
| Button | 12–18 chars | Verb-first; icons where possible |
| Choice option | ≤ 40 chars | One line in portrait; see §8.2 |
| Dialogue box page | 2–3 lines × 35–45 chars (≈ 120–140) | Split long lines into pages at sentence boundaries |
| Bark bubble | ≤ 50–60 chars | One idea |
| Task / quest name | ≤ 28 chars | Verb + object: "Fix the dock crane" |
| Item description | ≤ 90 chars | One fact + one flavour clause |
| Toast / reward pop-up | ≤ 50 chars | |
| Name tag | ≤ 12 chars | Applies to character naming (`references/worldbuilding-characters.md` §3) |
| Push notification | Front-load meaning in the first ~40 chars | Truncation varies by device, OS and settings |
| Recap card | ≤ 2 sentences, ≤ 160 chars | "Previously: …" |

**Write to ~70% of the budget** in the source language; the remaining 30%+ absorbs translation expansion (much more for very short strings — §12.3).

### 11.2 Reading speed and timing

- Average adult silent reading is roughly 238 words per minute for non-fiction and about 260 for fiction (Brysbaert, 2019, meta-analysis); game text read while holding a phone, with names and context switches, is slower. Children and second-language readers are slower still.
- Common subtitle guidelines cap presentation rates at roughly 15–20 characters per second for adults and lower for children — verify against the guideline you adopt.
- **Auto-advance timing:** `t_line = max(t_min, t_base + chars / cps)`, e.g. `t_min = 1.5 s`, `t_base = 0.6 s`, `cps = 15` → a 90-character line stays 6.6 s. Offer speed settings.
- **Typewriter reveal:** 30–60 chars/s; first tap completes the line, second tap advances; ignore taps for ~150–250 ms after the line completes to prevent accidental skips.
- **Always provide** skip (after first view), a backlog/log, and auto mode in story-heavy games.

### 11.3 Line-writing techniques

| Technique | Before | After |
|---|---|---|
| Front-load meaning | "Well, I suppose, if you really think about it, the crane might work." | "The crane might work. Maybe." |
| One idea per line | Two facts and a joke in one box | Split into two boxes |
| Cut stage directions from dialogue | "*sighs heavily and looks at the sea*" | Portrait mood `tired` + "Long day." |
| Prefer concrete nouns | "The thing over there" | "The brass key" |
| Avoid all caps for emphasis | "That's MY lighthouse!" | Use a bold/shake text effect sparingly; caps harm readability and some scripts have no case |

---

## 12. Localisation-friendly writing

### 12.1 The rules

| Rule | Why | Do | Don't |
|---|---|---|---|
| Every string has a stable ID | Translation memory, VO mapping, analytics | `ch1_dock_hale_001` | Key by English text |
| No concatenation | Word order differs by language | `"You found {count} shells"` as one string with a placeholder | `"You found " + n + " shells"` |
| Named placeholders with notes | Translators must know what fills them | `{player_name}`, `{item_name}` + note "item names are nouns, may need case" | `%s %s` |
| Plurals via CLDR categories | Languages have up to six plural forms (zero, one, two, few, many, other); English uses two, Russian four, Arabic six, Japanese one | ICU MessageFormat or your engine's plural support | `if n == 1 "shell" else "shells"` hard-coded |
| Gender and agreement | Many languages inflect adjectives/verbs by gender; player avatars may need variants | Neutral phrasing for the player; per-gender variants where unavoidable; translator notes for every character's gender and formality | Player-name in positions needing grammatical case |
| No text baked into images | Untranslatable | Overlay text labels; localised textures only if unavoidable | Signs, letters, titles painted into art |
| Puns, idioms, rhymes flagged | Need transcreation | Note: "pun on 'light'; replace with any light-themed pun" | Expect literal translation to work |
| Context for translators | Strings out of context are mistranslated | Screenshot or scene description, speaker, addressee, max length, tone | A bare spreadsheet of lines |
| Room for expansion | Translations are longer, especially short strings | Write to 70% of budget; test pseudo-locale | Fixed-width boxes sized to English |
| Formality register | Languages distinguish formal/informal "you" | Per-character register in the voice chart | Leave translators to guess |
| Dates, numbers, currency | Locale formats differ | Locale-aware formatters | Hard-coded "MM/DD" |
| Fonts and scripts | CJK, Arabic, Thai, Devanagari need coverage and shaping; RTL needs mirrored layouts | Choose fonts with glyph coverage; test RTL layouts | Assume Latin-only glyph sets |

### 12.2 String table template (CSV)

```
id,context,speaker,addressee,text_en,max_chars,placeholders,plural,gender_note,translator_note,screenshot,status
ch1_dock_hale_001,dialogue,hale,maya,"Crane's been rusted shut since the storm.",120,,,"Hale m; addresses Maya informally","'Crane' = dock crane",shots/ch1_dock.png,final
ui_shells_found,toast,,player,"You found {count} shells!",50,count:int,yes,,"count ≥ 0",,final
```

### 12.3 Expansion allowances

A widely cited IBM globalisation guideline gives additional space needed when translating from English by source length — roughly: up to 10 characters +100–200%; 11–20 +80–100%; 21–30 +60–80%; 31–50 +40–60%; 51–70 +31–40%; over 70 +30% (approximate; verify against your target languages — German, French, Portuguese and Russian commonly run long, CJK usually shorter in characters but needs larger font sizes). `narrative_lint.py lines` applies this length-dependent table by default, or a flat factor with `--expansion`.

### 12.4 Pseudo-localisation

Before any real translation, generate a pseudo-locale that (1) replaces characters with accented look-alikes ("Crâñé"), (2) pads each string by 30–40% (more for short strings), and (3) wraps strings in brackets ("[Crâñé's béén…]") so truncation and concatenation become visible on screen. Run it through screenshot capture for the visual gate. Fail the build on any clipped bracket.

---

## 13. Voice-over for mobile narrative

| Option | Cost profile | Localisation | Fits |
|---|---|---|---|
| No VO; text + SFX | Lowest | Text only | Most casual metas; sound-off audiences |
| Gibberish / synthesised babble voices | Low; one set of samples | Language-free | Cozy and mascot games; adds personality without translation |
| Grunts, reactions and key lines only | Low–medium | Few lines to localise | Casual with strong characters |
| Full human VO | High per language; recording logistics; union rules where applicable | Expensive per locale | Premium narrative, gacha story modes, hero characters |
| AI TTS / voice design | Low per character; requires consent, disclosure and QA | Many languages cheaply | Barks, prototypes, long-tail locales; hero lines with careful QA |

**Rules:**
1. **Captions always** — many mobile players play muted; VO is enhancement, never the sole channel.
2. **Line-ID-named audio files**; text edits after recording flag the line for re-record.
3. **Budget maths for TTS:** characters ≈ words × ~5.5 (English, including spaces). 20,000 words ≈ 110,000 characters; at a list rate of $0.08 per 1,000 characters (§15) that is ≈ $8.80 per language per full pass — retakes and variants typically multiply it several times. Costs are small next to human QA time.
4. **Consistency:** fixed voice IDs, seeds and settings per character; pronunciation dictionaries for invented names; store voice provenance in `.gamestudio/assets/manifest.json` (`kind: "voice"`, provider, model, prompt or voice description, seed, licence).
5. **Consent and disclosure:** never clone a real performer without written, use-specific consent; follow union agreements where they apply; disclose AI voices where provider policy or store rules require (§15). Production details in `ai-audio-pipeline` and `audio-direction`.

---

## 14. Dialogue QA procedure and telemetry

### 14.1 Procedure (per chapter or content drop)

1. **Compile/validate** with the tool's own compiler (inklecate warnings, Yarn compiler diagnostics, plugin validators). Warnings fail the build.
2. **Graph checks:** `narrative_lint.py ink|yarn --in <files>` for structure; `narrative_lint.py graph --story <export.json>` for state-aware reachability, soft-locks and ending reachability.
3. **Line checks:** `narrative_lint.py lines --in strings.csv` — duplicate IDs, missing text, length budgets with expansion, placeholder hazards, concatenation smells.
4. **Coverage playthrough:** a deterministic script that visits every choice at least once (branch coverage), saved as `playthrough` evidence (`playtest-report.schema.json`).
5. **Save/restore test:** save at each choice, kill, restore, verify the same line and variables; run migration cases if scripts changed.
6. **Pseudo-locale visual pass:** screenshots of every dialogue UI state with the pseudo-locale; no clipping.
7. **Tone and canon review** by the narrative lead (tone bible golden/rejected lines; canon tiers).
8. **Content rating and sensitivity scan** of all lines against the tone bible's boundaries.
9. **Record evidence** under `.gamestudio/evidence/<FEATURE-ID>/` and set gates with `gs.py feature gate`.

### 14.2 Telemetry events

| Event | Category | Key params | Answers |
|---|---|---|---|
| `story_beat_seen` | progression | `beat_id`, `chapter`, `skipped` (bool), `seconds_on_beat` | Which beats are read or skipped; where interest drops |
| `dialogue_choice` | progression | `scene_id`, `choice_id`, `option_index`, `paid` (bool) | Choice distributions; dead options; premium take-rate |
| `chapter_start` / `chapter_complete` | progression | `chapter`, `session_index` | Chapter funnel |
| `story_skip_all` | ux | `chapter`, `beats_skipped` | Players who opt out of story entirely |
| `dialogue_save_migrated` | tech | `from_version`, `to_version` | Migration health after content updates |

Names follow the `event-taxonomy.schema.json` rules (snake_case, ≤ 40 characters); register them through `event_taxonomy.py` and `player-analytics`.

---

## 15. Volatile facts (as of Oct 2026 — verify before relying)

- **Dialogic.** The GitHub releases page lists **Dialogic 2.0 Alpha 20** as the latest release, requiring Godot 4.5 or higher with 4.6+ recommended; Alpha 19 targeted Godot 4.4–4.6.x. Dialogic 2 remains labelled alpha — [Dialogic releases](https://github.com/dialogic-godot/dialogic/releases). Confirm the licence in the repository before shipping.
- **Yarn Spinner.** The compiler's releases page lists **v3.2.1** as the most recent release, after v3.0.0 (which introduced the Yarn Spinner 3 language: enums, smart variables, `once`, node groups with `when:` headers and saliency) and v3.1/v3.2 additions such as option-group fall-through and stable diagnostic codes. Engine integrations (Unity and others) ship as separate packages with their own release pages — [Yarn Spinner releases](https://github.com/YarnSpinnerTool/YarnSpinner/releases). Confirm the licence and Godot integration status in the repositories.
- **Ink.** The releases page lists **ink 1.2.1** as the latest release (universal macOS inklecate binary, documentation fixes), after 1.2.0 (Ink List API improvements, .NET Standard runtime) and 1.0.0 (multiple parallel flows, native booleans, error callback) — [ink releases](https://github.com/inkle/ink/releases). Confirm the licence and the maintenance status of any Godot or Unreal integration before adopting.
- **ElevenLabs.** API list rates per 1,000 characters: Flash/Turbo $0.04, Multilingual v2 $0.08, v3 $0.08 — [ElevenLabs API pricing](https://elevenlabs.io/pricing/api). Text-to-Dialogue (`POST /v1/text-to-dialogue`, default `eleven_v3`) accepts up to 10 unique voices and about 2,000 characters per request for reliable generation, with inline audio tags — [Text-to-Dialogue API](https://elevenlabs.io/docs/api-reference/text-to-dialogue/convert).
- **Gemini TTS.** `gemini-3.8-flash-tts` supports 130+ languages, up to 2 speakers per request, 24 kHz mono output — [Gemini speech generation](https://ai.google.dev/gemini-api/docs/speech-generation); priced at $9.00 per 1M audio output tokens through 31 Dec 2026, doubling from 1 Jan 2027 — [Gemini API pricing](https://ai.google.dev/gemini-api/docs/pricing).
- **OpenAI TTS policy** requires clear disclosure to end users that a TTS voice is AI-generated — [OpenAI TTS guide](https://developers.openai.com/api/docs/guides/text-to-speech).
- **SAG-AFTRA 2025 Interactive Media Agreement** (ratified July 2025) requires informed consent and a reasonably specific description of intended use before creating a performer's digital replica, plus usage reporting — [FKKS summary](https://ipandmedialaw.fkks.com/post/102ksuq/new-sag-aftra-2025-interactive-media-agreement-approved-by-members).
- **Vendor risk.** PlayHT shut down on 31 Dec 2025 and Replica Studios on 30 June 2025 — [TextToLab](https://texttolab.com/blog/play-ht-shutdown-alternatives); [MultiLingual](https://multilingual.com/replica-studios-shutdown-2025/). Cache generated audio and keep voice prompts/seeds so voices can be recreated elsewhere.
