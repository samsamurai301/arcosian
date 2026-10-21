---
name: legal-ethics
description: Legal and ethical risk knowledge for mobile games - clone and trade dress risk, trademarks, mechanic patents, AI content ownership and disclosure, voice and likeness, privacy (GDPR, COPPA, CCPA, age assurance), children, loot-box rules by region, open-source, font, music and asset licences, publishing contracts. Use when asked "can I copy this mechanic", "is this a clone", "disclose AI", "COPPA", "loot box legal" or "licence check".
---

# Legal and Ethics

Not legal advice. This skill is a risk-triage guide written by an engineer-minded practitioner. It helps you spot issues early, design around them, and know when to hire a lawyer. Laws differ by country and change often; where something is volatile it is marked and sourced. Final decisions on contracts, trademarks, children's data and gambling-adjacent features belong to qualified counsel and the human owner.

## What this skill gives you
- A way to separate idea from expression, so you can take inspiration without taking exposure.
- A clone-risk checklist and safe-inspiration procedure, with the two best-known mobile and puzzle cases explained.
- A privacy and children playbook: what data, what consent, what flags, which SDK settings.
- A region matrix for loot boxes and random-reward monetization, plus design patterns that avoid most of the exposure.
- A licence workflow for code, fonts, art, music and AI outputs, including provenance records.
- Triggers for when a human lawyer is required.

## Core models
**1. Idea versus expression.** Copyright protects the specific expression (art, code, text, music, specific arrangements) not ideas, rules or systems. Game rules and mechanics are generally ideas; the combination of look, feel, audio, UI layout, names and text can be expression. The more your game's expressive choices match another's, the higher the risk, even if you wrote every line yourself.

**2. Four independent exposure channels.** Copyright (expression), trademark (names, logos, sometimes trade dress, confusion), patent (specific claimed implementations of mechanics, rare but real), and contract/platform rules (store policies, licence terms, publisher agreements). A design can be safe in one channel and exposed in another.

**3. Risk is proportional to similarity, success and visibility.** A close clone that earns nothing may be ignored; a successful one draws takedowns and lawsuits. Store takedown processes are cheap for rights holders and fast.

**4. Compliance is a design constraint, not a late checklist.** Age, odds, data and consent requirements change the shape of the FTUE, the economy and the SDK list. Decide them in the design contract, not at submission.

**5. Provenance is the evidence.** For every asset (art, audio, code, text) record source, licence or generator, date, and human contribution. When a claim arrives, a clean provenance log turns a crisis into a ten-minute answer.

**6. Ethics goes beyond the law.** Minors, spending limits and transparency are ethical duties even where no law applies. The doctrine ("ethical monetization") sets a floor above legal minimums.

**7. Data minimisation.** Data you never collect cannot leak, be subpoenaed, or need a consent flow. Default to no personal data.

## Decision procedures

### A. "Can I take this mechanic or feature?"
1. State the mechanic as a rule in your own words, without names, art or numbers.
2. Ask: is it common in the genre (match, merge, idle, deckbuilder)? If yes, it is a genre convention: fine.
3. List what else you would copy: board dimensions, piece set, colours, UI layout, names, sounds, level designs, text, progression numbers. Each match adds risk.
4. If your design is the rule plus different expression, proceed. If more than a couple of expressive layers coincide, redesign those layers.
5. Search patents only for distinctive, named systems (a reported example class: loading-screen mini-games, procedurally generated enemy hierarchies); rare, but check when a feature is unusually specific.
6. Record the decision and the differentiators in the design contract.

### B. Clone-risk scorecard (0 = different, 2 = nearly identical)
Score each: name, icon, logo, colour palette, character designs, UI layout, board/field geometry, piece or unit set, audio, tutorial text, level layouts, monetization structure, store listing text and screenshots. Total over 8 on expressive items (name, icon, characters, UI, audio, text, listing) means redesign before shipping. The studio `critic` agent runs this scorecard on concept cards.

### C. Safe inspiration workflow
1. Deconstruct the reference into the ontology (`game-case-studies`, `deconstruct`) at the level of verbs, dynamics and aesthetics.
2. Choose a different fantasy, theme, art direction and naming scheme.
3. Change at least one core structural parameter and one player-facing system, so the game has its own reasons to exist.
4. Build your own assets; never trace, screenshot or "redraw" the reference.
5. Keep a clean-room note if the team has seen the reference closely: who designed what, what was changed and why.

### D. AI content decision
1. Choose tools whose terms permit commercial use of outputs; store the terms and date with the asset.
2. Record prompt, tool/model, version, date, human edits.
3. For core brand assets (logo, hero characters, key art), prefer human-authored or heavily human-modified work, because purely machine-generated output may not be protectable by copyright in some jurisdictions (see reference file) and you cannot stop copycats.
4. Disclose where platforms or laws require it (Steam asks; some regions require labelling of synthetic media). Do not disclose in misleading ways either direction.
5. Never imitate a real person's voice or likeness without a licence and consent.
6. Run the provenance check in CI (`licence_check`) before every release.

### E. Children and data decision tree
1. Is the game directed at children under 13 (COPPA) or under the local digital-consent age (GDPR Article 8, 13 to 16 depending on country)? Is the audience mixed? Decide and write it in the contract (`age_min`).
2. If child-directed: no behavioural ads, certified child-safe SDKs only, no persistent identifiers for advertising, no chat or UGC without strong moderation and consent, no link-outs without parental gate, no paid random items.
3. If mixed or general: neutral age screen, route minors to a restricted configuration (no personalised ads, no chat, no loot boxes in restricted regions).
4. Build the consent and deletion flows; log consent state.
5. Fill the store forms from the SDK register (`store-release`).

### F. Random-reward monetization decision
1. Is the item paid and chance-based? Then it is a loot box in most definitions.
2. Show odds before purchase. Always.
3. Apply region rules (matrix in `references/privacy-children-gambling.md`): disable or substitute in banned regions and for restricted ages.
4. Prefer direct-purchase, battle-pass, fixed-content bundles and earnable randomness when the design allows (inference, not a legal guarantee).
5. Add spending limits or cooling-off tools for adults if the game is gambling-adjacent; no pressure messaging towards minors.
6. Have counsel review before launch in any region with active enforcement.

### G. When to escalate to a human lawyer
| Trigger | Why |
|---|---|
| Receiving a takedown, cease-and-desist or store IP complaint | Deadlines and wording matter; do not reply alone |
| Child-directed or mixed-audience launch | Consent and data rules carry regulator attention |
| Paid random items in a region with active enforcement | Possible gambling classification |
| Any real-money prizes, sweepstakes, tokens or NFTs | Gambling and securities exposure |
| Publishing, work-for-hire or IP assignment contracts | Long-lived rights consequences |
| Using a recognisable brand, celebrity, sports league or film licence | Licence scope and approval rights |
| Using AI voice or likeness of a specific person | Publicity and union rules |
| Entering a market with new age-verification law | Obligations may sit on you, the store, or both |

Prepare for the call: a one-page summary, the provenance log, the SDK register, and the relevant contract or notice. The `compliance-officer` agent can assemble this pack.

## Mobile specifics
- Store review enforces many of these rules first (odds, deletion, privacy labels, kids). Pass the store forms honestly and the legal baseline mostly follows.
- SDKs are where mobile privacy violations hide: ad, attribution and analytics SDKs collect data unless configured otherwise. Read their child-directed and consent flags and test with a network proxy.
- Device identifiers (IDFA, GAID) require ATT on iOS and consent in many regions; design for denial.
- Age assurance is moving into the platform layer (Apple declared age range APIs, store-level laws in some US states); build to consume the platform signal where available.
- Push notifications, rewarded ads and daily-login streaks are manipulative in specific patterns; treat minors with stricter defaults.

## Anti-patterns
- "It is only a mechanic" used to justify copying art, names and UI as well.
- Trademark-adjacent names ("Candy-something") in titles or keywords.
- Shipping an SDK you did not read the data practices of.
- Treating "13+" as a legal shield when the art, theme and ads target children.
- Hiding odds behind several taps or in images that cannot be read by screen readers.
- Using AI voice cloned from a real actor, or "in the style of" prompts naming living artists for shipped assets.
- Copying GPL code into a closed binary, or using fonts and music with unclear licences.
- Signing a publishing contract without reading IP assignment, exclusivity, and termination clauses.

## Using the ontology
- `.gamestudio/contract.json` fields consumed by pre-flight: `age_min`, child-directed flags, monetization flags (ads, random rewards), odds disclosure, accounts, privacy policy URL.
- Resource and flow models from `economy-design` identify random converters (gacha, crates); each is a compliance surface: tag them `random: true` and `paid: true` where applicable.
- Content unit provenance fields: source, licence, generator, human edit level; enforced by the asset gateway and `licence_check`.
- Scripts: `${CLAUDE_PLUGIN_ROOT}/scripts/compliance_preflight.py` (store-facing checks), `${CLAUDE_PLUGIN_ROOT}/scripts/gacha_calc.py` (odds and pity maths to publish accurate probabilities).
- Agent: `arcosian:compliance-officer` runs these checks; `critic` runs the clone scorecard; humans sign off on children, gambling-adjacent features and contracts.

## Reference library
| File | What it contains | When to read |
|---|---|---|
| `references/ip-and-ai-content.md` | Idea vs expression, trade dress, Tetris Holding v. Xio, Spry Fox v. 6waves, trademarks, patents, safe inspiration, AI output copyrightability, disclosure, voice and likeness | Concept stage, asset sourcing, any clone worry |
| `references/privacy-children-gambling.md` | GDPR, GDPR-K, amended COPPA, CCPA/CPRA, age-assurance laws, ATT, loot boxes by jurisdiction, social casino | Before choosing SDKs, audience, or monetization |
| `references/licences-and-contracts.md` | OSS licences in games, fonts, asset-store and music licences, publishing and platform agreements | Adding any dependency or asset, signing anything |

## Related skills
- `store-release`: how these rules surface as store forms and rejections.
- `monetization`: designing revenue within the limits here.
- `economy-design`: random converters and odds maths.
- `player-psychology`: the ethical line on persuasion and compulsion loops.
- `ai-asset-pipeline`: provenance and licences for generated assets.
- `ai-audio-pipeline`: voice and music licensing for generated audio.
- `game-case-studies`: deconstructing references safely.
- `marketing-ua`: advertising claims and child-directed ad rules.
