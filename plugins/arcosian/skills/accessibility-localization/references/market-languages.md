# Market languages

Summary: which languages to localize a mobile game into, and in what order, is an investment decision, not a politeness. This file gives a method (waves driven by addressable spend, competition, genre fit and your own data), qualitative profiles of the language groups that matter most for mobile games, how store-only localization differs from in-game localization, regional variants and traps (Chinese scripts, Portuguese and Spanish variants, Arabic), and a worked example. It deliberately contains no market-size numbers: revenue and download shares change every year and differ by genre, so the method tells you where to get current figures and how to use them. Treat all regional characterisations as hypotheses to confirm with your own telemetry.

## Contents
1. The decision model
2. Data sources for current numbers
3. Language groups and profiles
4. Wave plan template
5. Store-only localization
6. Variants and traps
7. Genre and monetization interactions
8. Regional operating constraints
9. Worked example
10. Measuring return
11. Anti-patterns
12. Volatile facts (as of Oct 2026 - verify)
13. Language readiness checklist and sample scorecard

## 1. The decision model
For each candidate language L, estimate:
```
value(L)   = addressable_players(L) x expected_conversion_uplift(L) x arpu_potential(L)
cost(L)    = translation + LQA + font/layout work + store assets + ongoing live-ops strings + support
competition(L) = how many strong games in your genre are already localized there
priority(L) = value(L) / cost(L), adjusted by strategic fit and risk
```
Guidance:
1. Addressable players: the number of active mobile gamers who prefer the language, plus those who prefer English but convert better in their own language. Use market-intel data (`market-intel`) for your genre.
2. Uplift: localization usually lifts store conversion and early retention most where English proficiency is lower and where competitors are localized; measure with store listing experiments before translating the whole game.
3. ARPU potential: some large-audience markets have lower spend per player; some smaller markets spend heavily; balance reach against monetization (`monetization`, `liveops`).
4. Cost: scripts with complex layout (RTL, Thai) and large font sets cost more engineering; Latin-script European languages are cheaper per language once the pipeline exists.
5. Strategic fit: your art style, theme and content may already suit certain markets; cultural fit matters as much as language.
6. Risk: regulatory and publishing constraints (section 8).
7. Decide in waves, and re-decide after each wave with evidence.

## 2. Data sources for current numbers
- Store consoles: App Store Connect analytics (impressions, product page views, conversion by country and by territory), Play Console statistics (installs by country and language, store listing performance).
- Your own telemetry: device language distribution of installs, retention and revenue by language and country (`player-analytics`, `event_taxonomy.py` should log the OS language).
- Market intelligence providers and public reports (mobile market trackers): use them for relative sizing by country and genre; compare two sources, because figures conflict.
- Competitor store pages: which languages the top ten in your genre list, and how deeply.
- Search keyword tools: popularity of your core keywords per language.
Record the source and retrieval date next to every number you use in a plan.

## 3. Language groups and profiles
Qualitative profiles to start hypotheses; confirm with data.

**English.** The default source and often the first test language. Covers several large markets with different expectations (US, UK, India, Southeast Asia, Australia). Do en-US first, add en-GB spellings only if store or brand demands. Indian English markets often prefer simple language and sometimes Hindi support.

**Spanish.** Two large regions: Spain and Latin America. A neutral Latin American Spanish (es-419) covers most of Latin America reasonably well; Spain differs in vocabulary and tone (vosotros, some terms). Start with es-419 for reach; add es-ES when data justify. Mexico and Argentina have distinct slang; avoid regionalisms in UI.

**Portuguese.** Brazil is the dominant mobile market for Portuguese by far; pt-BR and pt-PT differ in vocabulary, spelling and form of address. Localize pt-BR; treat pt-PT as an optional later variant. Brazil also has regulatory attention on children and loot boxes (`legal-ethics`).

**French.** France, Canada, parts of Africa and Belgium. fr-FR is the usual base; Canadian French differences matter mostly for store tone and legal terms. Check the length expansion.

**German.** A high-spend European market with high expectations of polish; longer words stress layouts; formal vs informal address needs a policy (casual games often use informal "du", but check genre norms).

**Italian, Dutch, Polish, Turkish, Nordic languages.** Medium-size markets with solid mobile spending in some cases. Turkish has dotted/dotless i casing; Polish and Czech have complex plurals and case. Group them into a later European wave and localize after the first European wave shows uplift.

**Russian and Ukrainian.** Large audiences; Cyrillic; complex plurals (one, few, many). Geopolitical and payment constraints can change availability; check the store availability and sanctions situation before investing, and treat Russian and Ukrainian as separate decisions with sensitivity.

**Japanese.** A very high-spend, high-expectation market with strong local competition and distinct design conventions (character art, gacha culture, polite register). Requires high-quality translation, often transcreation, careful voice and art, and compliance with Japanese practices on random-reward disclosure (`legal-ethics`). Line-breaking rules apply. Plan as a market-entry project, not a language add-on.

**Korean.** High-spend, competitive, with strong preferences for specific genres and polished UX. Hangul is easy to render; honorifics and tone need native adaptation. Local rules on probability disclosure apply. Local publishing partners are common.

**Chinese (Simplified and Traditional).** Simplified Chinese serves mainland China, where operating a game requires local licensing, a local entity or publishing partner, and content review; the store landscape differs (the major app stores are Android alternatives). Traditional Chinese serves Taiwan and Hong Kong with distinct vocabulary and a separate store ecosystem. Do not treat these as one language; translate from source separately or at least with separate review. Mainland entry is a business-structure decision, not just localization.

**Arabic.** A large, diverse audience across many countries; Modern Standard Arabic for text with careful tone; RTL layout and shaping needed; dialect choices matter for voice. Check regional content rules and payment methods. Games with strong cultural fit (sports, strategy, card games) often perform in this region; verify with data.

**Hindi and other Indian languages.** Very large audiences by number with lower average spend per player and strong preferences for lightweight, low-data apps; many players use English UI or Hinglish. Indic scripts need shaping and fonts. Consider Hindi first and others later, with attention to app size and performance on low-end devices (`mobile-performance`).

**Indonesian, Malay, Thai, Vietnamese, Filipino.** Large and growing Southeast Asian audiences; Latin script (except Thai) and simple plurals for Indonesian and Malay; Thai needs word-breaking; Vietnamese needs diacritic space. Low-end devices common; payments often through carrier billing and gift cards (`monetization`).

**Hebrew, Persian, Urdu, Bengali, Swahili and others.** Add by data and partnership; RTL for Hebrew, Persian and Urdu.

## 4. Wave plan template
| Wave | Languages (hypothesis) | Trigger to proceed |
|---|---|---|
| 0 | Source language only, plus store listing tests in 3 to 5 candidate languages | Core loop validated, soft launch metrics healthy |
| 1 | Languages with the largest addressable spend for your genre that you can serve at high quality, commonly including a mix of the biggest European languages, Brazilian Portuguese, Latin American Spanish, and one or two Asian languages where your genre competes | Store experiment uplift in listing languages; LQA capacity |
| 2 | The next tier by data: more European languages, Turkish, Russian where available, Indonesian, Thai, Vietnamese, Arabic | Wave 1 per-language retention and ARPU at or above English baseline (or acceptable) |
| 3 | High-effort or high-risk entries: Japanese and Korean with full cultural adaptation, mainland Chinese via a partner, voice localization | Business case with local partners and counsel |
Rules:
- Never launch a wave without a native reviewer per language.
- Keep each wave small enough that LQA completes before release.
- After every wave, compare retention, conversion and revenue per install for localized vs unlocalized cohorts in that country; stop or expand accordingly.
- Revisit when your game's audience mix shifts (UA campaigns in new regions).

## 5. Store-only localization
Localizing the store page without the game produces installs from players who then face a foreign UI; use only deliberately.
| Approach | When it makes sense | Risks |
|---|---|---|
| Store text in L, game in English | Language-light games (puzzles, hyper-casual with minimal text) in markets with reasonable English exposure | Mismatch complaints; lower retention |
| Store text and game both localized | Standard approach for target markets | Cost |
| Store screenshots localized, text minimal | Low-text games | None significant |
| Game localized, store in English | Rare; wastes conversion potential | Lower organic discovery |
Tips:
- Language-light design (icons, symbols, minimal text) cuts localization cost and broadens reach at no extra translation; plan it in UX design (`mobile-ux`).
- Test store localization with listing experiments before committing to full translation.
- Keyword fields differ by locale; research them in-language (`store-release/references/aso-and-submission.md`).
- Some stores let you show different creatives per country regardless of language; use that for culture-specific themes.

## 6. Variants and traps
- **Chinese**: zh-Hans (mainland, Singapore) vs zh-Hant (Taiwan, Hong Kong); the characters are different sets and the vocabulary differs; machine conversion between them is not enough. Choose region-appropriate fonts to avoid wrong glyph forms.
- **Portuguese**: pt-BR vs pt-PT.
- **Spanish**: es-ES vs es-419 vs country-specific; avoid regional slang.
- **French**: fr-FR vs fr-CA; mostly legal and tone differences.
- **English**: US vs UK spelling; "football" and similar terms by sport context.
- **Arabic**: MSA text, dialect voice, RTL, numeral choices.
- **Serbian, Bosnian, Croatian**: script and vocabulary differences; check the target.
- **Norwegian**: Bokmål vs Nynorsk; Bokmål is the common default.
- **Filipino and Tagalog**: many players mix English; keep UI terms clear.
- Locale naming: store consoles use their own identifiers; keep a mapping file.
- Currency and pricing: use store price tiers per country; do not convert by hand.
- Date and event timing: event times in local time zones; holiday calendars (Lunar New Year, Ramadan, Diwali, Golden Week) matter for live-ops (`liveops`).
- Naming conflicts: item or character names that are offensive or have awkward meanings in a language; screen with native speakers.

## 7. Genre and monetization interactions
| Genre trait | Localization effect |
|---|---|
| Text-heavy (RPG, narrative, strategy) | Translation volume and quality dominate; voice optional; high LQA need |
| Text-light (puzzle, arcade, hyper-casual) | Few strings; store localization carries most value; cheap to cover many languages |
| Gacha and collection | Character names and lore carry brand; Japanese and Korean quality bar is high; odds text must be exact (`legal-ethics`) |
| Social and competitive | Chat and moderation per language; names and profanity filters per language |
| Idle and incremental | Number formatting and abbreviations per language matter |
| Card and board games | Rules text precise; terminology consistent; glossary essential |
| Educational and kids | Language level and cultural content strict; parent-facing text legally reviewed |
| Live-ops heavy | Continuous localization pipeline needed; event text volume repeats |
Monetization: price points and payment methods differ by region; offer local payment methods through the stores' billing; subscription and offer texts are legal text and require review.

## 8. Regional operating constraints
Not language issues but they decide whether a language is worth doing:
- China mainland: licensing, local entity or partner, content review, local app stores for Android; plan with counsel.
- Japan and Korea: local expectations of polish and disclosure rules; local publishing partners common.
- Russia and some other markets: availability, payment and sanctions constraints may block publication or revenue; check current conditions.
- Brazil and EU: stricter rules on children and random rewards; the localized game must also apply the local configuration profile (`legal-ethics`).
- Middle East: content sensitivity; some countries restrict content categories and gambling-like mechanics.
- India: data and device constraints; regulatory attention on real-money games; check rules for any money-related feature.
- Age ratings per region; localized rating labels on store pages are generated from the questionnaires (`store-release`).
- Data residency requirements in some countries affect servers and analytics.

## 9. Worked example
Game: a match-3 puzzle with light text (about 600 words of UI) and a gem shop, soft launched in English.
1. Wave 0: listing experiments in German, Spanish (es-419), Portuguese (pt-BR), Japanese, and Turkish. Observe conversion uplift vs the English listing in each country using store experiments or localized listings with country targeting.
2. Costing: 600 words x 5 languages is a small project; Japanese needs extra review and a font check; layouts reflowed using pseudo-localization.
3. Wave 1: ship German, es-419, pt-BR. Japanese deferred until a partner or a high-quality review budget exists and the gacha-like "lucky chest" is reviewed for local disclosure norms.
4. After 4 weeks, compare per-country cohorts: day-1 and day-7 retention, installs per impression, revenue per install, against the English-only baseline in comparable countries; decide wave 2 (Turkish, Indonesian, French, Italian) accordingly.
5. Add Arabic only if data show demand and an RTL-capable UI pass has been completed and reviewed by native speakers.
6. Store: localize screenshots with short captions; keep a locale mapping file; review keywords per language.
This keeps cost proportional to evidence. A text-heavy RPG would flip the order: fewer languages, higher quality, translators briefed on lore, with voice left for later.

## 10. Measuring return
- Primary: change in store conversion, day-1 and day-7 retention, and revenue per install in countries where the language is primary, compared with a control (same country before localization, or similar countries without).
- Secondary: support tickets in that language, review sentiment, rating changes, share of players switching language manually in settings.
- Attribution caution: localization often coincides with UA changes; hold UA stable during the test or use country-level controls.
- Decision rule example: continue investing in a language if revenue per install or retention improves by more than the amortised cost per install; otherwise freeze the language at current coverage and spend elsewhere. Define the threshold before the test.
- Maintenance cost: every new feature adds strings in every language; include per-language maintenance in the feature cost estimate (`production`).

## 11. Anti-patterns
- Picking languages by national pride or by what the team speaks.
- Localizing into twenty languages at launch and abandoning half after the first update.
- Treating Chinese, Portuguese and Spanish as single languages.
- Launching a language without a native reviewer who plays the game.
- Ignoring regulatory and publishing constraints while celebrating translation completion.
- Copying market-size numbers from old blog posts into a plan.
- Localizing the store page into a language the game does not support without telling players.
- Using machine translation for the listing without review.

## 12. Volatile facts (as of Oct 2026 - verify)
No figures are asserted in this file. For current numbers, use:
- App Store Connect analytics: https://appstoreconnect.apple.com/ (your own data)
- Google Play Console statistics: https://play.google.com/console/ (your own data)
- Commercial market trackers and public market reports: compare at least two and record retrieval dates.
- Language and locale identifiers: https://www.rfc-editor.org/info/bcp47
- Store regional availability, ratings and regulatory notes for Brazil, China, Japan and Korea: see `legal-ethics/references/privacy-children-gambling.md`, section 10, and its sources; the research notes did not confirm China, Japan and Korea specifics, so verify with counsel.

## 13. Language readiness checklist and sample scorecard

### Readiness checklist (per language, before release)
- [ ] Business case recorded: expected uplift, cost, review date, owner.
- [ ] Native reviewer assigned and has played the build.
- [ ] Glossary and style guide approved (formality, tone, names).
- [ ] Fonts verified for all glyphs and weights; fallback chain tested; size budget checked.
- [ ] Plural, gender and number-format rules verified with test strings.
- [ ] Layout tested at pseudo-localized and real-language extremes.
- [ ] RTL mirroring and shaping verified if applicable.
- [ ] Legal text (age, odds, purchases, privacy) translated and reviewed.
- [ ] Store listing, keywords and screenshots localized and reviewed.
- [ ] Support macros and FAQ available in the language or a clear fallback.
- [ ] Live-ops string pipeline includes the language, with a rush lane.
- [ ] Telemetry segments by language set up before launch.
- [ ] Regional configuration profile (ads, chat, random rewards) applied and tested.

### Sample scorecard (illustrative, scores 1 to 5 from your own data)
| Language | Addressable demand | Uplift evidence | ARPU potential | Cost/effort (5 = cheap) | Competition gap | Risk (5 = low) | Total |
|---|---|---|---|---|---|---|---|
| Language A | 5 | 4 | 3 | 4 | 3 | 5 | 24 |
| Language B | 4 | 3 | 5 | 2 | 4 | 3 | 21 |
| Language C | 3 | 2 | 2 | 5 | 2 | 5 | 19 |
Weights: set them per game (a gacha game may weight ARPU and risk more; a casual puzzle may weight cost and demand more). The numbers above are placeholders to show the method, not data about any market.

### Review cadence
- After each wave: compare cohorts, update the scorecard, remove languages that fail the decision rule, decide whether to deepen quality (voice, transcreation) in winners.
- Yearly: re-run the data pulls; markets, store policies and competitors shift.
- When your genre or monetization model changes, re-score all languages, because uplift depends on how much text and how much price-sensitive monetization the game has.
- Keep the decision log with dates so the next producer understands why a language exists.
