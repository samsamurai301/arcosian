---
name: accessibility-localization
description: Accessibility and localization knowledge for mobile games - Game Accessibility Guidelines, colour-blind, motor, cognitive, hearing and photosensitivity design, Godot and Unity recipes, i18n architecture, ICU plurals, CJK and RTL fonts, text expansion, LQA, machine translation with review, market languages. Use when asked "make it accessible", "colour-blind mode", "add languages", "localize the game" or "RTL support".
---

# Accessibility and Localization

## What this skill gives you
- A prioritised accessibility baseline for phones: what to build first, what it costs, and how to test it.
- Recipes for Godot 4 and Unity 6 covering text scaling, remapping, colour-blind safety, captions and reduced motion.
- A localization architecture that survives growth: string tables, ICU-style plurals, font fallback, layout that tolerates expansion, pseudo-localization and LQA.
- A procedure for machine translation with human review, plus culturalization checks.
- A market-language shortlist method for game and store localization.

## Core models
**1. Accessibility is a design input, not a mode.** Most barriers are removed by decisions made in design: do not rely on colour alone, do not demand precision timing for core progress, keep text readable, offer redundancy (visual plus audio plus haptic). Retrofits are expensive; the cheapest moment is the style bible and UI kit.

**2. Three tiers of effort.** Basic (nearly free, do on every game), intermediate (planned work), advanced (specialised, content-dependent). The Game Accessibility Guidelines organise advice this way; use it as the checklist skeleton and the studio's own summary in `references/accessibility.md`.

**3. Barriers by capability, not diagnosis.** Vision (low vision, colour vision deficiency, blindness), hearing, motor, cognitive (attention, memory, reading, processing speed), speech, and sensory sensitivity (photosensitivity, vestibular). Design for the situational cases too: one-handed on a bus, bright sun, muted phone, interrupted session. Mobile makes situational disability the norm.

**4. Let the OS do the work, and add game-level options for what it cannot.** Phones provide screen readers, system text scaling, switch control, reduced motion and captions. Game engines often bypass them. Respect system settings where feasible, and expose in-game options for the rest.

**5. Localization is architecture plus process.** Architecture: no strings in code or art, locale-aware formatting, font fallback, layouts that flex. Process: extract, translate with context, review in game, regression test every release. Cost explodes when either is skipped.

**6. Translate meaning, not words.** Humour, idioms, cultural references, colours, numbers, gestures and icons need culturalization; context (screenshots, character notes, glossary) decides quality more than translator price.

**7. Language count follows evidence.** Add languages in waves driven by market size, store competitiveness and your retention data; test the first wave before committing to many.

## Decision procedures

### A. Accessibility baseline (do for every game)
1. Text: minimum body size readable on a small phone, user scale option, contrast per `references/accessibility.md`.
2. Colour: never encode information by hue alone; add shape, icon, pattern or label; ship a tested colour-blind-safe palette.
3. Input: no required multi-finger or path gestures for core play without an alternative; adjustable touch target size; no hold requirement without a toggle option.
4. Timing: pause anywhere; adjustable or removable timers in non-competitive modes.
5. Audio: captions for speech and key sound cues; separate volume sliders; every critical audio cue has a visual or haptic twin.
6. Flashing: no content exceeding flash thresholds; reduce screen shake, flashes and parallax with a Reduce Motion toggle.
7. Cognitive: clear goals, tutorial replay, skippable cutscenes, saved progress, simple language.
8. Test with the checklist in `references/accessibility.md`, and with at least one real user per major barrier class when possible.

### B. Localization setup (before the first string is written)
1. Choose the string system (Godot: `tr()` with CSV or PO; Unity: Localization package with string tables).
2. Keys describe context, not English text: `shop.pack.title`, `battle.result.victory`.
3. Plurals and gender through message formats (ICU-style), never string concatenation.
4. Dates, numbers, currency via locale-aware formatting.
5. Font strategy per script (Latin, CJK, Arabic, Thai, Devanagari), with fallback chains and a size budget.
6. Layout rule: UI built with containers that grow; reserve expansion headroom (see `references/localization.md`).
7. Pseudo-localize in CI to catch hard-coded strings and clipping.
8. Add a glossary and style guide per language; send context with every batch.

### C. Choosing languages
1. Start from your market-intel data and the wave model in `references/market-languages.md`.
2. Wave 1: the languages with the biggest addressable mobile spend relevant to your genre, plus those where store localization alone lifts conversion.
3. Check retention and monetization by language after launch; extend to wave 2 only where data supports.
4. Always localize store listings for each language you list in-game and vice versa.

### D. Machine translation with review
1. Export strings with context; run MT as first draft only.
2. Human review by a native speaker who plays the game, for UI strings, tutorial, store copy and anything legal (age, odds, purchases).
3. Glossary enforcement and consistency checks automated.
4. LQA in build: truncation, wrong plural, wrong gender, tone.
5. Never machine-translate legal and purchase text without review.

### E. Accessibility testing loop
Automated (contrast, size, pseudo-loc, flash analyser) in CI, manual checklist per release, assistive-tech pass (screen reader, large text, switch control), user feedback channel, and a public accessibility statement in the store listing when features exist.

### F. Accessibility options menu: minimum content
| Group | Options |
|---|---|
| Display | Text size (at least three steps), high-contrast UI, colour-blind palette, reduce motion, reduce flashes, screen shake off |
| Controls | Touch target size, hold-to-toggle, swipe sensitivity, one-handed layout, left/right mirroring, button remap where applicable |
| Audio | Master, music, effects, voice sliders, captions on/off with size and background, mono audio, haptic intensity |
| Gameplay | Difficulty or assist options (more time, auto-aim, skip level after N fails), tutorial replay, pause anywhere |
| Language | Language picker with native names, persists across sessions |
Put the menu in the first-run flow as a short "Play your way" step, and make it reachable from the pause screen. Log which options are used (setting names only).

### G. Release checklist (both topics)
- [ ] Pseudo-localization run passes; no clipped or hard-coded text.
- [ ] Largest OS text size tested on the smallest supported phone.
- [ ] Colour-blind simulation screenshots reviewed for every key screen.
- [ ] Captions cover speech and critical sound cues.
- [ ] Flash and motion options verified.
- [ ] Store listing text and screenshots localized for each shipped language.
- [ ] Odds, age and purchase text reviewed by a native speaker.
- [ ] Language and accessibility settings persist and apply at boot.

## Mobile specifics
- System text scaling can break fixed layouts; test at the largest sizes the OS allows and design scrollable panels.
- Both iOS and Android expose screen readers; game engines render custom UI that the readers cannot see unless you supply accessibility nodes or a parallel menu layer. Menus and shops are the practical target; real-time play usually needs audio and haptic design instead.
- One-handed play, thumb reach and interruption handling are baseline accessibility on phones (`mobile-ux`).
- Haptics substitute for audio cues for deaf and hard-of-hearing players; check device support and provide an intensity setting.
- Language: respect the OS language list, allow in-game override, and persist the choice.
- Notch, safe areas and gesture bars: avoid placing critical controls where system gestures conflict.
- Store accessibility labels (Apple accessibility nutrition labels and Play accessibility info) are emerging; verify current store support before claiming features.

## Anti-patterns
- Red versus green as the only win/lose signal.
- Text baked into images and videos, which blocks translation and captions.
- Hard-coded string concatenation ("You have " + n + " gems").
- Fixed-width buttons sized to English.
- One font for all scripts, producing tofu boxes for CJK or Arabic.
- Quick-time events with no alternative; time-limited offers that punish slow players.
- Flashing effects on every reward for "juice".
- Translating from a previous translation instead of the source, or shipping MT without review.
- Adding twenty languages at launch without LQA capacity.
- Treating accessibility as "a settings page at the end".

## Using the ontology
- UI components in the content-unit model carry tags: `text_key`, `min_touch_target`, `colour_semantics` (what the colour means and its non-colour redundancy). The `ux-designer` agent checks these.
- Player-model personas include accessibility needs (low vision, one-handed, deaf); `player-simulator` plays builds under those constraints (`playtest`).
- Economy and shop screens with random rewards must expose odds as translatable text (`legal-ethics`).
- Telemetry: log language and accessibility settings (not diagnoses) to segment retention (`player-analytics`, `event_taxonomy.py`).
- Scripts: none dedicated; use `${CLAUDE_PLUGIN_ROOT}/scripts/store_metadata.py --locales` to scaffold store listings per locale.

## Reference library
| File | What it contains | When to read |
|---|---|---|
| `references/accessibility.md` | Guidelines summarised, mobile OS limits, vision, motor, cognitive, hearing, photosensitivity, Godot and Unity recipes, testing | Designing UI, options menus, QA |
| `references/localization.md` | i18n architecture, string tables, plurals, fonts for CJK and RTL, expansion, LQA, MT with review, culturalization | Starting or auditing localization |
| `references/market-languages.md` | Priority languages for mobile games, wave model, store localization, regional notes | Choosing languages and store locales |

## Related skills
- `mobile-ux`: thumb reach, onboarding and HUD patterns that carry accessibility.
- `game-feel`: juice that must respect reduced motion and flash limits.
- `audio-direction`: captions, mix and cue redundancy.
- `art-direction`: palettes and style that survive colour-blind filters.
- `narrative-design`: text volume and tone that localization must carry.
- `store-release`: store listing localization and accessibility declarations.
- `legal-ethics`: odds and consent text in every language.
- `qa-testing`: LQA and accessibility regression testing.
