# IP and AI content

Summary: this file explains how intellectual property law touches game design and production, in practitioner terms. Not legal advice; it is a triage guide, and counsel decides. It covers the idea/expression line, trade dress and look-and-feel, the two cases most often cited in clone disputes (Tetris Holding v. Xio and Spry Fox v. 6waves/Lolapps), trademarks, patents on mechanics, a safe-inspiration procedure, then AI-generated content: who owns it, what must be disclosed, and the rules around voice and likeness. Jurisdictions differ, and the AI portion is moving fast, so volatile items are collected at the end with sources or explicit "verify" marks.

## Contents
1. Scope and disclaimer
2. Idea versus expression
3. Trade dress and look-and-feel
4. Case study: Tetris Holding v. Xio
5. Case study: Spry Fox v. 6waves/Lolapps
6. Trademarks
7. Patents on mechanics
8. Safe inspiration and clean-room practice
9. Clone-risk scorecard (detail)
10. Responding to a claim
11. AI-generated content: ownership
12. AI content: disclosure and platform rules
13. Voice, likeness and performers
14. Training data and tool terms
15. Provenance record format
16. Volatile facts (as of Oct 2026 - verify)
17. Worked examples

## 1. Scope and disclaimer
- Not legal advice. Facts decide cases; a one-line summary of a case here is a pointer, not a prediction.
- US law is used as the main example because the best-known game cases are American; other countries (UK, EU, Japan, China, Korea, Brazil) have different thresholds, remedies and moral-rights rules.
- Rule for builders: treat anything that might look like someone's work as risky, keep records, and escalate to a lawyer on any notice.

## 2. Idea versus expression
| Typically ideas (not protected as such) | Typically expression (protected) |
|---|---|
| Rules, objectives, win conditions | Source code, shaders, tools |
| Core loops, genre conventions | Art, animation, character designs |
| Standard mechanics: match three, merge two, tower defence | Music, sound effects, voice recordings |
| Scoring concepts, progression structures | Level layouts and puzzles as authored works (to a degree) |
| Common themes and tropes | Narrative text, dialogue, specific plots and character combinations |
| Functional or "scenes a faire" elements (a health bar in a shooter) | Distinctive selection and arrangement of many elements together |

The merger and scenes-a-faire ideas: when there are few ways to express an idea, or the expression is dictated by the idea or genre, the expression gets little or no protection. That is why genre conventions are safe.

The practical risk is in the layers where you might copy without noticing: the exact set of pieces, colours, board size, interface placement, animation timing, names, text and sound cues, written down in your own design doc as "like game X but...".

Design-doc hygiene: describe the target experience and rules; do not paste competitor screenshots into asset briefs given to artists or AI tools; do not prompt generators with another game's name.

## 3. Trade dress and look-and-feel
- **Trade dress** is the overall look and feel of a product (packaging, interface, presentation) that identifies its source. It is protected when distinctive and non-functional, and when imitation is likely to confuse consumers.
- In games, claims typically combine copyright (for the art and audiovisual elements) and trademark/trade dress (for confusion). Courts look at the total concept and feel, but also filter out unprotectable elements first.
- Risk factors: same icon composition and colour scheme, same character archetype rendered similarly, same title structure, same UI skeleton, same store screenshots composition, same sound identity.
- Reduce risk by: designing your own visual language early (`art-direction`, style bible), avoiding reference screenshots in the brief, and running the clone scorecard.
- Genres produce convergent looks (e.g. fruit match boards); pick a different theme and palette to add distance.

## 4. Case study: Tetris Holding v. Xio
Tetris Holding, LLC v. Xio Interactive, Inc., 863 F. Supp. 2d 394 (D.N.J. 2012). Facts as summarized in secondary sources: the Tetris rights holder sued the developer of "Mino", an iPhone game, alleging it copied Tetris; the developer acknowledged downloading Tetris and building what amounted to a clone. In 2012 a US federal court in New Jersey found infringement on summary judgement and rejected the argument that only unprotectable functional elements had been copied. The opinion was not read in full for this file (see section 16).
Takeaways in my words:
1. The court separated unprotectable ideas and rules (falling blocks, rotation, clearing lines on a rectangular field) from protected expression (the specific look: piece visual style, colours, dimensions and proportions of the playfield, the preview pane layout, the way pieces appear and animate).
2. Mino was not a pixel copy but was close enough in overall expression that the court found substantial similarity once genre-required elements were set aside.
3. Evidence mattered: the developer had played Tetris and aimed for a clone; intent and access are not required for copyright liability, but they colour the story.
Lesson: you may build a falling-block puzzle; you may not reproduce another one's visual and audio presentation. Change the theme, the board proportions, the preview and the feedback design.

## 5. Case study: Spry Fox v. 6waves/Lolapps
Spry Fox, LLC v. LOLApps, Inc., No. 2:12-cv-00147 (W.D. Wash. 2012), Judge Richard A. Jones. Facts as summarized in secondary sources: Spry Fox released the puzzle-strategy game Triple Town and had negotiated with a larger company about a possible licence for a version of it; negotiations ended and that company then released Yeti Town, which Spry Fox said copied its game. In 2012 the court declined to dismiss the copyright claim, finding that Spry Fox had plausibly identified enough copying to state a claim, and allowed the case to proceed (secondary sources disagree on the order's date, 18 September or 29 October 2012, so check the docket), indicating that a game's expression could be infringed through a close clone that changes the theme (bears to yetis). The matter settled afterwards, so there is no full trial ruling.
Takeaways:
1. Reskinning (changing theme only) does not cure copying if the other expressive choices (rules combined with the specific structure, character-like pieces, tiers, interface behaviour, progression) track the original.
2. Negotiation history can create risk: if you discussed licensing a game and then built something extremely similar, expect trouble. Keep clean-room discipline after any talks.
3. The ruling was early-stage; do not cite it as proof that mechanics are protected. It shows that plausible claims survive when similarity is wide.
Lesson: a "tile-merge with bears" and a "tile-merge with yetis" with the same board, tiers and interaction beats may be treated as the same expression.

## 6. Trademarks
- A trademark protects source identifiers: names, logos, sometimes sounds, colours and trade dress. Test: likelihood of confusion among consumers, plus dilution protection for famous marks in some countries.
- Clearance before naming (do this early; renaming after launch loses ASO equity):
  1. Search the stores for same and similar names and phonetic variants.
  2. Search the national trademark databases for your target markets (US, EU, UK, Japan, China, Korea at least) in classes covering software and games.
  3. Search domain names and social handles.
  4. If a close mark exists in games/software, pick another name. Where the budget allows, ask counsel for a clearance opinion.
  5. File your own mark after launch traction or before a large marketing spend; protection is territorial.
- Do not use competitor names or well-known marks in keywords, descriptions, or hidden metadata.
- "Candy", "Saga" or "Clash" style suffixes in names invite disputes when the party owning the family of marks is active; avoid even where technically descriptive.
- Licensed IP (movies, brands, sports): licence scope covers territory, platforms, time, approvals and merchandising; assets must be approved by the licensor. Keep the approval trail.
- Real brands appearing in-game (cars, drinks, logos) require clearance; generic invented brands avoid the issue.
- Real people, places and events: check right-of-publicity and defamation risk for characters resembling real persons.

## 7. Patents on mechanics
- Patents protect claimed inventions (methods and systems), not a general idea, and unlike copyright they bind independent creation. Game-mechanic patents exist and are enforced rarely but memorably.
- Examples reported in the industry include patents on loading-screen mini-games (since expired), on procedurally generated enemy hierarchies, and on specific matching or reward systems. Treat these as illustrations only; status changes, so verify any specific patent.
- Practical posture for an indie or small studio:
  1. You cannot search all patents. Search only when a feature is unusually specific and central (named, claimed systems in big-studio games are the usual suspects).
  2. Design around claims by changing a required element rather than hoping the patent is invalid.
  3. Prior art defences exist for old mechanics; a long-established genre convention is unlikely to be enforceable.
  4. Platform holders sometimes forward patent complaints; respond via counsel.
- If you invent something distinctive, decide whether to patent, keep as trade secret, or publish defensively; note that patent filings take years and money and may not match a mobile product's timescale.

## 8. Safe inspiration and clean-room practice
1. Work from the ontology: verbs, dynamics, aesthetics (`game-ontology`, `deconstruct`). Share that abstraction with designers, not the reference's assets.
2. Change at least three expressive layers: theme/fantasy, art style, naming/text, audio identity, UI layout, board or level structure.
3. Add a new structural element that gives the game a distinct reason to exist (a twist in the verbs or the progression).
4. Separate roles when copying risk is high: one person writes the abstract spec; another builds from the spec without looking at the reference.
5. Never trace, rotoscope, screenshot-and-redraw, rip audio, or use AI image-to-image from the reference.
6. Keep a design-decision log noting references consulted and differences chosen.
7. Test with people: show your screenshots next to the reference to five players; if more than a couple say "it is the same game", change more layers.
8. Review store listing text and screenshots with the same rigour; listing similarity is evidence of intent.

## 9. Clone-risk scorecard (detail)
| Layer | 0 | 1 | 2 |
|---|---|---|---|
| Name | Unrelated | Shares a common word | Same or near-same |
| Icon / logo | Different shape and palette | Similar palette or motif | Recognisable derivative |
| Characters / pieces | Original designs | Same archetype, own design | Same set and tiers |
| UI layout | Own layout | Common genre layout | Same positions, same chrome |
| Board / field geometry | Different | Genre standard | Same dimensions and layout |
| Audio | Original | Genre-typical | Imitates identifiable cues |
| Text / tutorial | Original | Similar structure | Paraphrased or copied |
| Listing | Original | Similar keywords | Mimics screenshots or copy |
Interpretation: 0 to 4 fine; 5 to 8 adjust the highest-scoring layers; over 8 redesign. This is a heuristic, not a legal test; the final judgement needs counsel for borderline high-revenue cases.

## 10. Responding to a claim
1. Do not delete evidence or edit history; preserve repositories, design docs, chats.
2. Do not reply to the claimant alone; collect the notice, deadlines and the platform's process (App Store or Play complaint workflow).
3. Pull the provenance log and clone scorecard; identify the exact allegations.
4. Counsel decides: contest, modify, settle, or withdraw. For a small studio the cheapest path is often to modify the contested layers and resubmit.
5. Communicate with the store through their dispute form once counsel agrees on content.
6. After resolution, run a retro and tighten the process (`postmortem`).

## 11. AI-generated content: ownership
- Copyright generally needs human authorship in many jurisdictions. In the US, the Copyright Office's published guidance (Part 2 report on copyrightability, published January 29, 2025) states that outputs are protectable only to the extent a human contributed expressive elements, and that prompts alone have generally not been enough to make a person the author of the output; selection, arrangement, modification, and human-made input integrated into the work can be protected. The D.C. Circuit affirmed refusal to register a work with no human author (Thaler v. Perlmutter, 130 F.4th 1039, decided March 18, 2025), and the Supreme Court denied review on March 2, 2026 (No. 25-449), which leaves that ruling in place without a Supreme Court opinion. Other countries differ; the UK has a provision for computer-generated works, and its future was under review; verify before relying.
- Consequences for studios:
  1. Pure raw outputs may be freely copyable by others; do not rely on them for brand-defining assets.
  2. Human modification, compositing, painting-over and authored selection raise protectability; keep layered source files as evidence.
  3. Code generated by AI and then reviewed, edited and integrated by humans is treated like other code in practice, but verify the tool's terms and licence-compatibility of any suggested snippets (see `references/licences-and-contracts.md`).
  4. Contracts: freelancers and vendors must state whether they use AI tools and warrant that deliverables do not infringe; allocate responsibility.
- Registration: when registering copyrights, disclose AI-generated material and claim only the human-authored parts, per the registration office's instructions.

Decision table for asset class:
| Asset | AI acceptable? | Condition |
|---|---|---|
| Prototype and placeholder art | Yes | Mark as placeholder in manifest |
| Backgrounds, props, UI icons | Usually | Style-locked, human review, provenance logged |
| Key art, logo, hero characters | Caution | Human-led, extensive modification, ownership counsel |
| Voice acting | Only with licensed voices | Consent and contract; see section 13 |
| Music | Tool with clear commercial licence | Check royalty-free terms and content ID behaviour |
| Narrative text | Yes with editing | Human editorial pass; check for echoing known text |
| Code | Yes with review | Licence scan, tests |

## 12. AI content: disclosure and platform rules
- Platforms: some storefronts ask developers to disclose AI-generated content in games. Steam introduced AI disclosure rules in 2024 and revised them in January 2026: developers no longer need to disclose AI tools used only to speed up development (such as code helpers), but must disclose AI-generated content that ships in the game or reaches players (marketing and concept assets, pre-generated in-game assets, and a checkbox for live-generated content). The Content Survey asks for a detailed description of pre-generated AI content and for the guardrails on live-generated content, and says Valve does not currently want to ship live-generated adult-only sexual content ([Steamworks Content Survey](https://partner.steamgames.com/doc/gettingstarted/contentsurvey); [Gigazine on the January 2026 revision](https://gigazine.net/gsc_news/en/20260120-steam-updates-ai-disclosure-guidelines)). Mobile store requirements on this topic are evolving; Google Play has policies on AI-generated content (notably around generative features and user-reported content, plus restrictions on deceptive or harmful output). Check the current policy text for each store at submission.
- If the game contains live generative features (chat NPCs, user-prompted images), you need: content filtering, reporting and blocking tools, age restrictions, and a statement of how outputs are produced. Minors raise the bar significantly.
- Regulation: some jurisdictions are introducing transparency duties for synthetic media and for AI systems that interact with people (the EU AI Act contains transparency obligations phased in over time; verify the application dates and whether they apply to your feature). Chinese rules on generative AI and deep synthesis require labelling and registrations for services offered in China.
- Marketing honesty: do not claim "handcrafted" when assets are AI-made, and do not hide AI use when a platform asks. Silence is risky; truthfulness is cheap.
- Credit: credit human contributors accurately; do not credit an AI tool as an author.
- Internal policy to write into the contract: which assets may be AI-assisted, tools approved, provenance logging, review by `art-director` and `compliance-officer`.

## 13. Voice, likeness and performers
- Right of publicity (US states) and personality rights (many countries) protect a person's name, image, voice and likeness; consent and a licence are needed for commercial use. Sound-alikes can infringe when the voice is distinctive and the use implies endorsement.
- Do not clone a real person's voice, even a "tribute", without a written licence specifying scope, term, AI use and compensation.
- Performers' unions have negotiated AI terms for video game voice work (reported 2024 to 2025); if you hire union talent, follow the agreement on consent, disclosure and compensation for digital replicas. Verify current terms with the union or counsel.
- Some US states passed laws on digital replicas and AI voice cloning (e.g. Tennessee's ELVIS Act); verify the state where you operate and where the person lives.
- Character likeness: avoid making characters recognisably resemble real people (celebrities, athletes, politicians) without a licence; parody defences are narrow in commercial contexts.
- Motion capture and scans of performers: contract for ownership of the data, reuse, and deletion; biometric laws can apply to face and voice templates (also relevant to the amended COPPA rule's treatment of biometrics).
- Synthetic voices from licensed providers: check whether the voice is licensed for commercial game use, whether the provider indemnifies, and whether the voice can be changed or revoked mid-product.

## 14. Training data and tool terms
- Generative tools differ in training data transparency, indemnification, output licensing and content filters. Risk-lower options include tools trained on licensed data with indemnities for enterprise customers; terms change, so store a copy of the terms with the date.
- Do not fine-tune a model on another artist's work without permission; style-lock using your own art instead (`ai-asset-pipeline`).
- Avoid prompts that name living artists or specific franchises; output resembling them is both ethically and legally risky.
- The asset gateway logs generator, prompt hash and settings for provenance.
- Lawsuits about training data are ongoing in several countries; outcomes are uncertain. The studio posture is: prefer tools with clear terms, keep humans in the loop, keep records.

## 15. Provenance record format
Per asset, in the manifest or sidecar file:
```json
{
  "asset": "art/ui/icon_gem.png",
  "origin": "ai-generated | human-made | stock | commissioned | open-licence",
  "tool": "tool name and version, or author name",
  "licence": "licence id or contract reference",
  "licence_url": "https://...",
  "date": "YYYY-MM-DD",
  "human_edits": "none | minor | substantial",
  "prompt_ref": "hash or note",
  "approved_by": "role"
}
```
The pre-release `licence_check` verifies every shipped asset has an entry and flags unknown or incompatible licences.

## 16. Volatile facts (as of Oct 2026 - verify)
- US Copyright Office AI reports and registration guidance (checked 2026-10-20: Part 1 on digital replicas published July 31, 2024; Part 2 on copyrightability published January 29, 2025; Part 3 on generative AI training released in pre-publication form on May 9, 2025): https://www.copyright.gov/ai/
- Thaler v. Perlmutter, 130 F.4th 1039 (D.C. Cir. Mar. 18, 2025), No. 23-5233, on human authorship; certiorari denied March 2, 2026 (No. 25-449). Sources: [Jones Day](https://www.jonesday.com/en/insights/2026/03/jones-day-talks-women-in-ip--supreme-court-denies-review-of-thaler-v-perlmutter-ai-authorship-questions-remain), [Baker Donelson](https://www.bakerdonelson.com/supreme-court-denies-certiorari-in-thaler-v-perlmutter-ai-cannot-be-an-author-under-the-copyright-act); court site: https://www.cadc.uscourts.gov/
- Steam AI disclosure rules for developers: [Steamworks Content Survey](https://partner.steamgames.com/doc/gettingstarted/contentsurvey) (AI section: pre-generated vs live-generated content, guardrails) and [Gigazine's report on the January 2026 revision](https://gigazine.net/gsc_news/en/20260120-steam-updates-ai-disclosure-guidelines) (development-tool use no longer needs disclosure). Valve's original 2024 announcement was not retrieved.
- Google Play policy on AI-generated content: https://support.google.com/googleplay/android-developer/ (search the AI-generated content policy)
- EU AI Act transparency obligations and timeline: https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai
- Union video game agreement AI terms: https://www.sagaftra.org/
- Tennessee ELVIS Act: https://www.tn.gov/ (search the ELVIS Act text)
- Tetris Holding v. Xio Interactive, 863 F. Supp. 2d 394 (D.N.J. 2012) and Spry Fox v. LOLApps, No. 2:12-cv-00147 (W.D. Wash. 2012): the citations, parties and outcomes were checked on 2026-10-20 against secondary sources ([Wikipedia: Spry Fox v. Lolapps](https://en.wikipedia.org/wiki/Spry_Fox,_LLC_v._Lolapps,_Inc.), [Eric Goldman's blog](https://blog.ericgoldman.org/?p=10653)). The court opinions themselves were not read, so the takeaways above are summaries; read the opinions before relying on any holding.

## 17. Worked examples
**Example A: "Like Merge Dragons but with robots."** Rule: merge two identical items to create the next tier on a board. Genre convention, safe. Risk layers: same tier ladder structure, same healing-orb and camp progression, same egg-hatching animation, same character names. Action: keep the merge rule, redesign the tier ladder around your own fantasy (parts to machines), change progression structure (workshop instead of camp), original UI, original names. Score the scorecard; should be under 5.

**Example B: Block puzzle for a hyper-casual studio.** Rule: place pieces on a grid, clear lines. Genre convention. Risk layers: the exact pieces and spawn behaviour of the classic falling-block game. Action: change piece set and grid proportions, make placement player-driven or cascading, change visuals and audio completely, avoid the word "Tetris" or derivatives in any text. The two cases above show why theming alone is not enough.

**Example C: AI-generated card art for a deckbuilder.** Action: style-lock on your own concept sheet, log prompts and tool terms, have an artist paint over key cards, disclose on stores that ask, keep layered files, avoid prompts naming artists. Hero card and logo done by a human illustrator under contract with a clause on AI use. Provenance sidecar for each card.

**Example D: Voice for a mascot.** Action: hire a voice actor with a contract covering game use, digital replica consent if you plan to extend lines synthetically later, and payment for each extension. Do not use a free voice-clone of a known actor "as a placeholder" in a build that ships to a store; placeholders leak into releases.

**Example E: Name clearance.** Candidate "Orchard Pop". Steps: store search finds several "Pop" titles in puzzle games; trademark search in key markets finds a registered "Orchard Pop" in an unrelated class. Decision: acceptable risk but add a distinctive second word or logo; record the search date and results; file your own application when revenue justifies it.

**Example F: Receiving a store IP complaint.** A rights holder complains about your icon. Steps: preserve evidence, compare icon to claimed work, fix the layer in question (new icon), submit a store response with counsel's agreement, update the scorecard with the new baseline, add "icon similarity check" to the pre-release checklist.
