# Localization

Summary: localization (l10n) adapts a game to languages and cultures; internationalization (i18n) is the engineering that makes that cheap. This file covers the architecture (keys, string tables, message formats with ICU-style plurals, locale-aware formatting), fonts for Latin, CJK, Arabic, Hebrew, Thai and Indic scripts, right-to-left layout, text expansion budgets, the translation workflow including glossary, context and pseudo-localization, LQA, machine translation with human review, culturalization, and store listing localization. Engine specifics for Godot 4 and Unity 6 are included. Numbers like expansion percentages are rules of thumb, not measurements for your game.

## Contents
1. Vocabulary and scope
2. Architecture rules
3. Keys and string tables
4. Message formats: plurals, gender, variables
5. Locale-aware formatting
6. Fonts and scripts
7. Right-to-left and bidirectional text
8. Text expansion and layout
9. Text in art, audio and video
10. Workflow: extraction to release
11. Pseudo-localization
12. LQA
13. Machine translation with review
14. Culturalization
15. Godot 4 recipes
16. Unity 6 recipes
17. Store listing localization
18. Costs and scheduling
19. Anti-patterns
20. Volatile facts (as of Oct 2026 - verify)

## 1. Vocabulary and scope
- i18n: design so that no code change is needed to add a language.
- l10n: producing the content for one locale (language plus region, e.g. pt-BR vs pt-PT).
- Culturalization: adapting content beyond language (symbols, colours, humour, legal and sensitive content).
- LQA: linguistic quality assurance, testing translated text in the game build.
- Locale identifiers: BCP 47 tags (`en-US`, `zh-Hans`, `zh-Hant`, `pt-BR`, `es-419`); store identifiers differ slightly, so keep a mapping table.
- Scope for a mobile game: UI strings, tutorials, dialogue, item names, store listing, push notifications, customer support text, legal text, event text delivered by live-ops, server-sent messages.

## 2. Architecture rules
1. No user-visible text in code, scenes or prefabs; text comes from tables by key.
2. Server messages: send keys and parameters, not finished English strings.
3. Live-ops content (events, offers, news) is localized through the same pipeline; remote config carries keys.
4. Never concatenate translated fragments; use whole sentences with placeholders.
5. Do not reuse a string across contexts when meaning can differ ("Open" as a verb vs adjective); duplicates are cheaper than wrong translations.
6. Locale selection: default from OS language list, allow override in settings, persist, apply before the first screen draws.
7. Separate content locale (text) from formatting locale (numbers, dates) only if you have a reason; usually the same.
8. Fallback chain: `fr-CA` -> `fr` -> `en`; log missing keys in development builds and show the key in a visible debug style.
9. Text lives in a format your translators' tools understand (CSV, PO, XLIFF, JSON with metadata) and is round-trippable without manual editing.
10. Keep a stable key set; renaming a key loses translations.

## 3. Keys and string tables
Key naming: `area.screen.element.purpose`, lower-case, dots, no English text: `shop.pack.gems_small.title`, `battle.result.victory.header`.
Per-string metadata (stored beside the source text, sent to translators):
| Field | Purpose |
|---|---|
| `context` | Where it appears, who speaks, what the player just did |
| `max_chars` | Length budget from the layout |
| `placeholders` | Meaning and type of each variable |
| `screenshot` | Reference image path |
| `tone` | Formal, playful, terse |
| `do_not_translate` | Brand names, item codes |
| `owner` | Writer responsible for source changes |
| `status` | New, changed, translated, reviewed |
Table layout: one table per area or per feature for parallel work; a "common" table for shared strings; a separate table for store text.
Change management: when a source string changes meaning, mark translations as outdated; when only a typo changes, do not invalidate.
Glossary: term, translation per language, definition, notes (character names, currencies, game mechanics). Enforce through the translation tool and the LQA checklist.

## 4. Message formats: plurals, gender, variables
Languages differ in plural categories: English has two forms; some languages have one (no grammatical plural in common nouns), several have three or more, Arabic has six categories. Standard data (CLDR) defines categories: zero, one, two, few, many, other. ICU MessageFormat is the common syntax:
```
{count, plural,
  one {You earned # gem}
  other {You earned # gems}}
```
Rules:
1. Always use a plural construct for any number-dependent text, even if English "never needs it".
2. Give translators the full message so they add the categories their language needs.
3. Gender and selection: `{gender, select, female {...} male {...} other {...}}` for characters addressed or referred to; avoid needing gender by rewording where possible.
4. Variables are named or numbered with meaning (`{player_name}`, `{gems}`), never bare `%s` in multi-variable strings, because word order changes by language.
5. Ordinals: use ordinal selectors (`1st`, `2nd`) via format rules, not suffix concatenation.
6. Lists and "and": use list formatters from the locale library.
7. Inline markup (bold, colour) should be tag placeholders (`<b>...</b>`) that translators move but cannot break; validate tag balance automatically.
8. Capitalisation: do not force Title Case in code; capitalisation conventions vary.
9. Inflected languages (e.g. Slavic, Finnish, Turkish) change words by case; avoid inserting item names into sentences where grammar changes the item name; use fixed-structure sentences or provide case forms.
10. Engines without ICU support: implement plural rules via CLDR tables or a small library; Godot's gettext plural forms and Unity's smart strings provide mechanisms (section 15, 16).

## 5. Locale-aware formatting
- Numbers: grouping and decimal separators differ; use the platform or engine formatter. Large numbers in idle games: define your abbreviation system (K, M, B) per language, because some cultures group by ten-thousands (CJK languages commonly use units like man/wan, 10^4). Provide a localized abbreviation table and test it.
- Currency: show store-provided localized prices from the store API, never hard-coded; virtual currency amounts are numbers with your own names.
- Dates and times: locale formats, time zones for events (display in local time with clear rules), calendar differences (week start day).
- Sorting and search: locale-aware collation for leaderboards and name lists.
- Units: metric vs imperial only if your game shows them.
- Names: avoid assuming first/last order in social features.
- Text direction and digits: some locales use native digit shapes; decide whether to localize digits (usually keep Western digits unless the locale convention is strong and your font supports it).

## 6. Fonts and scripts
Strategy: choose a primary font for Latin and Cyrillic and Greek that matches art direction, then define fallback fonts per script, applied by the engine's fallback mechanism, so a missing glyph never renders as an empty box ("tofu").
| Script | Locales | Considerations |
|---|---|---|
| Latin extended | European languages, Vietnamese, Turkish | Diacritics need vertical room; Vietnamese stacks marks; Turkish dotted/dotless i casing |
| Cyrillic, Greek | Russian, Ukrainian, Greek | Primary font must include them or fallback |
| Chinese (Simplified, Traditional) | zh-Hans, zh-Hant | Thousands of glyphs; regional glyph forms differ (Han unification); choose region-specific fonts |
| Japanese | ja | Kana plus Kanji; line-breaking rules (kinsoku) forbid some characters at line starts and ends |
| Korean | ko | Hangul syllables; many glyphs; spaces separate words, wrapping easier |
| Arabic, Persian, Urdu | ar, fa, ur | Contextual shaping, right-to-left, ligatures; needs a shaping engine; Urdu prefers Nastaliq-style fonts but Naskh is common in UI |
| Hebrew | he | Right-to-left, no shaping complexity |
| Thai | th | No spaces between words; word-breaking needs a dictionary; stacked marks need line height |
| Indic scripts | hi, bn, ta, others | Complex conjuncts needing shaping; taller line heights |
Practical choices:
- Fonts: prefer open fonts with broad coverage under permissive licences (OFL families such as the Noto set cover most scripts) and verify the licence (`legal-ethics`).
- Size: CJK fonts can be large (several megabytes each). Options: ship a subset of glyphs actually used (requires a build step and a re-subset when text changes), download font packs on demand per language (an asset-delivery feature), or rely on system fonts for CJK in non-stylised UI. Decide by budget in `mobile-performance`.
- Dynamic atlases or SDF fonts: engines generate glyph atlases on demand; budget memory and watch hitches on first display of large character sets. Pre-warm common glyphs.
- Stylised display fonts rarely cover other scripts: define a separate "display font per script" or use the fallback font for non-Latin titles, and accept consistent but less stylised headings.
- Weight and italic: many scripts have no true italics; avoid italic as a meaning carrier.
- Emoji: system emoji differ by platform; do not rely on emoji in critical text.
- Line height: increase for Thai, Indic and Arabic diacritics; test with real strings.
- Test strings: keep a per-script pangram and worst-case string set in the test scene.

## 7. Right-to-left and bidirectional text
- Languages: Arabic, Hebrew, Persian, Urdu. Text flows right to left; numbers and embedded Latin words flow left to right inside it (bidirectional algorithm).
- Layout mirroring: horizontal lists, progress bars, back buttons, menu alignment, swipe directions and tutorial arrows mirror; things that do not mirror: media controls, clocks, game-world maps and directional gameplay (a character running right toward the goal remains right unless the design depends on reading order), logos and numerals.
- Engines: confirm text shaping and bidi support (Godot has built-in text server support for RTL and complex scripts; Unity needs the Arabic shaping solution or the current TextMeshPro and UI Toolkit RTL support in your version; verify and test on device).
- Alignment: set paragraph direction per string from the locale, not from the first character alone; mixed strings need explicit marks.
- Punctuation placement and parentheses mirroring are handled by the bidi algorithm; test strings with numbers, English names and punctuation.
- Input fields: RTL entry and caret behaviour.
- Art: avoid text in images; mirror icons that imply direction (arrows, undo) but not those depicting real-world objects.
- Ask native reviewers during LQA to check shaping, joins and alignment; screenshots are essential.

## 8. Text expansion and layout
Rule-of-thumb expansion relative to English (varies by string length and language): short strings (single words) can grow a lot, long sentences less; German and Finnish and many Romance languages often run longer than English; CJK is often shorter in characters but needs equal or larger font size for legibility. Use the budget table below only as a starting heuristic and replace with measured data from your own game's longest strings.
| Source length | Budget multiplier to plan for |
|---|---|
| 1 to 10 characters | Up to roughly double |
| 11 to 30 | Often about one and a half times |
| 31 to 70 | Often about one and a third times |
| over 70 | Often about one and a quarter times |
Layout rules:
1. Containers grow; avoid fixed-width buttons; use minimum width plus padding.
2. Allow two lines for button labels where design permits, or define shorter alternatives with `max_chars`.
3. Never shrink fonts below the readability floor to fit; instead rephrase or relayout.
4. Truncation with ellipsis is a last resort and never on purchase, legal, or odds text.
5. Test with the longest languages and with a pseudo-localized build.
6. Vertical text and ruby annotations (furigana) for Japanese are optional; plan if the genre needs them.
7. Dynamic text in 3D or world-space UI needs larger bounds.

## 9. Text in art, audio and video
- Baked text in sprites, logos, banners, tutorial images: replace with live text over art or maintain per-language art variants (cost grows with languages).
- Logos: decide whether to localize the logo (often kept) and the tagline.
- Audio: voice-over per language is costly; prefer subtitles with original voice for secondary languages; if you localize voice, plan casting, scripts with lengths, lip-sync needs and re-recording pipelines; AI voice raises licence issues (`ai-audio-pipeline`, `legal-ethics`).
- Video and cinematics: subtitle tracks, not burned-in captions.
- Number and unit icons that embed text (like "x2" badges) can stay if universal.
- Tutorial overlays: anchored to UI elements using text boxes that resize.

## 10. Workflow: extraction to release
1. Source text is final enough (freeze for a batch); writers update `context`.
2. Extract new and changed strings into the exchange format with metadata.
3. Send to translation vendor, platform, or in-house translators with glossary, style guide, screenshots.
4. Receive translations; automated checks: placeholders intact, tags balanced, length limits, glossary terms, forbidden terms.
5. Import into the game; build a localized test build.
6. LQA pass in build (section 12) with defect log; fixes round trip.
7. Release; live-ops strings follow the same pipeline with shorter lead times.
8. Maintain translation memory (TM) so repeated strings are reused and cost falls.
9. Track per-language: coverage percentage, open defects, review status; do not ship a language below the coverage rule (for example full UI coverage, no English leftovers in core flows).
Roles: localization manager (producer), translators and reviewers, writers, engineers for tooling, QA for LQA. A small studio often combines roles; keep the checklist.
Continuous localization: for live-ops games, automate extraction and import so updates ship weekly; set service levels with vendors.

## 11. Pseudo-localization
Transform source strings automatically to expose problems before translation:
- Accent replacement: "Settings" -> "[Šéttîñgš]" tests glyph coverage and vertical room.
- Expansion: pad by thirty to forty percent with filler (`~~~`) to test layout.
- Bracket markers at start and end reveal truncation.
- Mirror pseudo-locale for RTL: reverse and mark direction.
- Placeholders must survive untouched.
Run in CI by exporting screenshots of key screens in the pseudo locale; hard-coded text stays plain and shows up immediately. Fail the build when a string table has missing keys or when screenshots show clipped bracket markers.

## 12. LQA
Test plan per language:
1. Coverage: every screen, popup, error, push notification, store text and server message.
2. Defect classes: mistranslation, grammar, plural or gender errors, terminology inconsistency, tone, untranslated leftovers, truncation and overlap, font glyph missing, wrong direction, wrong formatting, cultural issues, legal text accuracy.
3. Severity: critical (blocks purchase or misleads about price/odds), major (confusing), minor (style).
4. Evidence: screenshot plus key and the proposed fix.
5. Reviewers: native speakers who play the game; give them a script (tutorial, shop, first event) plus free exploration.
6. Regression: re-test fixed items and changed strings each release; maintain a smoke list per language.
7. Pass criteria: no critical or major open; minor tracked.
Tooling: debug overlay that shows string keys on tap, a screenshot batch runner per locale, defect tracker with language labels.

## 13. Machine translation with review
Use MT (neural or large-model) as a drafting tool when volume is high or budgets are tight, with controls:
1. Give the model context: game description, tone, glossary, character notes, max lengths, placeholder rules.
2. Translate from the source language, not from another translation.
3. Automated checks on output (placeholders, tags, length, glossary).
4. Human review by a native speaker: mandatory for tutorials, store text, legal, purchases, odds, and anything player-facing and permanent; sample-based review may be acceptable for low-risk long-tail text (item descriptions) with measured defect rates.
5. Track edit distance: if reviewers rewrite most of the text, MT is costing more than it saves for that language.
6. Keep translation memory so reviewed translations are reused and not overwritten by MT.
7. Privacy: do not send unreleased secrets or player data to MT services without reviewing their terms.
8. Be careful with languages and domains where MT is weaker (rare languages, wordplay, honorific systems in Japanese and Korean, dialect choice in Arabic).
9. Marketing and store text deserve transcreation (creative adaptation) by a human.
10. Disclose internal policy: which text types allow MT and which do not.

## 14. Culturalization
Review content for each target market, prioritising by risk:
| Area | Examples | Action |
|---|---|---|
| Symbols and gestures | Hand gestures, animals, numbers with negative or positive meanings | Check with native reviewers; swap if needed |
| Colour meaning | Colours associated with mourning, luck, danger vary | Do not rely on one colour code globally |
| Religious and political content | Flags, maps, borders, sacred symbols, historical events | Avoid; use neutral or fictional geography; legal review |
| Violence, blood, gambling, alcohol, romance | Rules vary by region and by rating boards | Provide region toggles or content versions |
| Humour, idioms, pop-culture references | Often untranslatable | Rewrite for equivalent effect |
| Names and characters | Names with unfortunate meanings | Check names per market |
| Social conventions | Formal vs informal address, honorifics | Style guide per language |
| Holidays and events | Different calendars and holidays | Localize event calendars (`liveops`) |
| Representation | Diverse characters, stereotypes | Review with people from the group depicted |
| Legal | Loot boxes, age gates, data laws | See `legal-ethics` |
| Regional versions | China requires local licensing, content review and a local entity; some markets restrict content | Plan separately; consult counsel |
Process: a culturalization checklist per market, applied at concept stage and again at content lock; native consultants for top markets.

## 15. Godot 4 recipes
- Translation formats: CSV (one column per locale) or gettext PO files; register under Project Settings > Localization > Translations.
- `tr("shop.pack.gems_small.title")` for lookup; `tr_n("key_singular", "key_plural", count)` with PO plurals for count-based text; `TranslationServer.set_locale("de")` to switch; read OS locale with `OS.get_locale_language()`.
- Controls: `Label` and `Button` auto-translate their text when `auto_translate_mode` is enabled and the text is a key; for formatted strings use `tr(key) % [args]` with named placeholders via `String.format()` and dictionaries: `tr("battle.reward").format({"gems": n})`.
- Fonts: `FontVariation` and `Font` resource `fallbacks` array to chain CJK/Arabic fonts; enable MSDF for scalable text in Project Settings and font import where appropriate; Godot's text server handles shaping and bidi for complex scripts with the advanced text server enabled (check the export template includes it).
- RTL: `Control.layout_direction` (inherited, locale, LTR, RTL) mirrors containers; set to locale; test `HBoxContainer` order.
- Pseudo-localization: Project Settings includes a pseudolocalization option in recent 4.x versions; use it in test runs.
- Plural rules: PO headers `Plural-Forms` must be correct per language.
- Live-ops strings: store key-value tables in downloaded JSON and call `TranslationServer.add_translation()` at runtime.
- Missing keys: `tr()` returns the key, which makes missing strings visible.
```gdscript
func show_reward(gems: int) -> void:
    $RewardLabel.text = tr("battle.reward").format({"gems": gems})
```

## 16. Unity 6 recipes
- Package: Unity Localization. Concepts: Locales, String Tables (with shared table data and keys), Asset Tables (fonts, sprites, audio per locale), Smart Strings for plurals and gender with a format like `{count:plural:one{# gem}|other{# gems}}`, and a Localized String reference component.
- Locale selection: `LocalizationSettings.SelectedLocale`, with startup selectors (system language, saved preference); persist the player's choice.
- Fonts: TextMeshPro font assets with fallback lists; dynamic font assets for CJK with atlas population modes; per-locale font via Asset Tables; for RTL use a TextMeshPro-compatible shaping solution or UI Toolkit text features supported in your version, and test on device.
- Import/export: CSV, XLIFF, and Google Sheets integration in the package for translator workflows; use XLIFF for vendors.
- Pseudo-locale: the package provides a pseudo-locale feature to expand and accent strings; use in automated screenshot tests.
- Addressables: ship locale tables as Addressables groups so languages can be downloaded on demand and reduce install size.
- Editor scripting: a tool that finds hard-coded `TMP_Text` strings and flags scene text without a localized binding.
- Server messages: map keys to `LocalizedString` lookups at runtime, passing arguments as a dictionary for smart strings.

## 17. Store listing localization
- Localize title, subtitle or short description, keywords (researched per market), descriptions, what's-new text, screenshots, captions, previews, and promotional text.
- Match store languages to in-game languages (see `store-release/references/aso-and-submission.md`).
- Use `${CLAUDE_PLUGIN_ROOT}/scripts/store_metadata.py --contract .gamestudio/contract.json --out store/ --locales en-US,de-DE,ja-JP` to scaffold per-locale files; the script drafts text from the contract and enforces character limits; real translations and keyword research replace the drafts.
- Respect limits per store; CJK strings are shorter in characters, German longer.
- Regional store locales differ from in-game ones (es-ES vs es-419 vs es-MX, pt-BR vs pt-PT, zh-Hans vs zh-Hant); map explicitly.
- Review for legal wording: age rating descriptions, subscription terms, odds notes.

## 18. Costs and scheduling
- Cost drivers: word count, language count, specialist domain, rush, DTP/art variants, voice, LQA hours, tool licences. Typical vendor pricing is per word per language; quotes vary widely, so get several and run a paid pilot on 500 words before committing.
- Estimate effort in your own project: count source words (a script over the string table), multiply by the vendor rate and by the number of languages, add LQA as a percentage of translation cost and a contingency for rework.
- Schedule: freeze text, translate, import, LQA, fix, regression; allow time proportionate to volume and add buffer; first-time localization projects usually take longer than planned due to layout fixes.
- Budget rule: do not localize before the core loop is validated; do localize the store listing early for conversion testing.
- Live-ops: set a weekly cadence and a rush lane for urgent event text.
- Reuse: translation memory and glossaries reduce cost across updates and sequels.

## 19. Anti-patterns
- Source strings written without context or length awareness.
- Dropping spreadsheets into email with no tooling, leading to version chaos.
- Hard-coded "s" for plurals.
- Fixed-size buttons and baked-in text.
- Translating only the app and not the store, or the reverse.
- Machine-translating the purchase and odds text without review.
- One font for every script and no fallback.
- Shipping RTL without a native reviewer.
- Using country flags as language buttons (languages are not countries); use language names in their own language.
- Changing source text late and forgetting to invalidate translations.

## 20. Volatile facts (as of Oct 2026 - verify)
- CLDR plural rules and locale data: https://cldr.unicode.org/
- ICU MessageFormat syntax: https://unicode-org.github.io/icu/userguide/format_parse/messages/
- BCP 47 language tags: https://www.rfc-editor.org/info/bcp47
- Godot internationalization docs (plural forms, pseudolocalization, text server): https://docs.godotengine.org/en/stable/tutorials/i18n/index.html
- Unity Localization package documentation: https://docs.unity3d.com/Packages/com.unity.localization@latest
- Noto font families and licence: https://fonts.google.com/noto
- Store locale lists change; check App Store Connect localizations and Play Console store listing languages.
- Regional publishing rules for China (licensing, local entity, content review): consult counsel; not covered by the research notes.
