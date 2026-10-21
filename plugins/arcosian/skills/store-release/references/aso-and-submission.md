# ASO and submission

Summary: App Store Optimization is conversion engineering for a store page: the right players find the page (search and browse visibility) and a high share of them install (page conversion). This file covers keyword and metadata craft within the character limits the plugin enforces, creative assets, store experiments (Apple product page optimization and custom product pages, Google store listing experiments), localization, and the submission pre-flight: a checklist mapped to what `compliance_preflight.py` checks automatically, what `store_metadata.py` drafts, and what only a human can verify. It ends with review notes and a launch-week routine.

## Contents
1. ASO model
2. Metadata limits and fields
3. Keyword research and placement
4. Creative assets
5. Store experiments
6. Localization of the listing
7. Ratings and reviews
8. Pre-flight checklist mapped to scripts
9. Using `store_metadata.py`
10. Review notes and submission
11. Launch week and post-launch routine
12. Anti-patterns
13. Volatile facts (as of Oct 2026 - verify)
14. Diagnostics, category and soft-launch listing

## 1. ASO model
Two multiplicative levers:
```
installs = impressions x tap-through rate x page conversion rate
impressions  <- keywords, category, featuring, ratings, velocity
tap-through  <- icon, title/subtitle, first screenshot, rating stars
conversion   <- screenshots, video, description first lines, reviews, price/IAP labels
```
Rules of thumb:
1. The icon and first two screenshots do most of the conversion work; text matters more for search ranking than for persuading.
2. A small lift in conversion compounds across paid and organic traffic; run experiments before scaling spend (`marketing-ua`).
3. Genre expectations are strong: players scan for the genre signal (match-3 board, idle numbers, card frames). Differentiate within the convention, not against it.
4. Retention and ratings feed ranking indirectly; ASO cannot rescue a game with weak day-1 retention.
5. Never keyword-stuff or use competitor trademarks; both stores reject or demote this.

## 2. Metadata limits and fields
The limits below are the ones enforced in `store_metadata.py` (verify against the stores before submission as limits can change).
| Field | Store | Limit | Notes |
|---|---|---|---|
| App name | Apple | 30 chars | Searchable and heavily weighted |
| Subtitle | Apple | 30 chars | Searchable; benefit or genre phrase |
| Keywords | Apple | 100 chars | Comma-separated, no spaces after commas, not visible to users |
| Promotional text | Apple | 170 chars | Editable without a new build; not searchable as keywords |
| Description | Apple | 4000 chars | Not used for search ranking on iOS; for people |
| What's new | Apple | 4000 chars | Release notes |
| Title | Google | 30 chars | Searchable; no emoji spam or price claims |
| Short description | Google | 80 chars | Shown on the listing; weighted for search |
| Full description | Google | 4000 chars | Indexed for search on Google Play |
Other fields: category (and secondary on Apple), content rating, support URL, marketing URL, privacy policy URL, copyright, contact details, icon (1024 square for Apple; Google icon spec in console), feature graphic and screenshots per device class, optional preview video.

## 3. Keyword research and placement
Procedure:
1. Seed list: genre, core verb, fantasy, platform, audience (for example "puzzle", "merge", "farm", "relax"). Pull 30 to 60 candidates from competitor titles, autocomplete, reviews, and your own concept card.
2. Score each candidate by relevance (does the game truly deliver), popularity (store tools give relative scores; treat as ordinal), and competition (strength of top results). Prioritise high relevance, medium popularity, beatable competition.
3. Place: highest-value phrase in title (Apple) or title (Google); secondary phrases in subtitle; remaining single words in the Apple keyword field, no repeats of words already in title or subtitle (Apple combines fields), no plurals if the singular is already covered, no category names that Apple adds automatically.
4. Google: weave phrases naturally into the short and full descriptions; repetition beyond natural use is penalised.
5. Track rank for 10 to 20 tracked keywords weekly; change at most one field per cycle so the effect is attributable.
6. Localize keyword research per market; translation is not research.

Worked example (fictional match-3 game "Orchard Pop"):
- Title: `Orchard Pop: Match 3` (20 chars).
- Subtitle: `Fruit puzzles, calm and quick` (29).
- Keyword field: `blast,swap,candy,farm,garden,relax,levels,offline,brain` (55, room left to test more).
- Short description (Google): `Swap fruit, clear the orchard, and relax in short, satisfying puzzle levels.` (under 80).
Check that none of these terms is another company's trademark.

## 4. Creative assets
- **Icon.** One focal shape, high contrast, readable at small sizes, no text unless the brand is the text. Test on light and dark home screens and as a notification-sized thumbnail. Apple icon must have no transparency.
- **Screenshots.** First two must show real gameplay and the core fantasy; caption with benefit, not feature (short verb phrases). Use real renderer captures (`screenshot_mode.gd` for Godot) and device frames sparingly. Show progression, social or collection hooks later in the sequence. Never depict UI that does not exist.
- **Video.** Apple app preview and Google promo video: first 3 seconds must show gameplay; muted autoplay is common, so captions carry meaning. Footage must come from the app (Apple requires that for previews).
- **Feature graphic (Google).** Legible when cropped; keep key content in the safe centre.
- **Localized creatives.** Localize captions for priority languages (`accessibility-localization`, market languages); keep layouts that survive text expansion.
- **Accessibility of art.** Sufficient contrast for captions; do not rely only on colour to convey meaning.
- **Creative briefs** go to `arcosian:art-director`; critique with the style bible.

## 5. Store experiments
Apple
- Product page optimization tests alternative icons (via the app binary alternates), screenshots and previews against the default using traffic splits; run until statistical confidence, usually weeks at small volumes.
- Custom product pages give different creative and promotional text per audience or ad campaign link; use them to align an ad creative with its landing page.
Google
- Store listing experiments test icon, feature graphic, screenshots, short and full descriptions; global or localized experiments; a minimum duration and traffic are needed.
Method:
1. One hypothesis per test ("gameplay-first screenshot beats character-first").
2. Pre-compute needed sample with `ab_test.py` (use the sample-size mode) from baseline conversion and the smallest lift worth shipping.
3. Run full weeks to cover weekday effects; do not peek and stop early.
4. Ship the winner only if the effect holds in your most valuable countries; check retention afterwards because misleading creatives raise installs and lower quality.
5. Log results in the knowledge base so future tests do not repeat losers.

## 6. Localization of the listing
- Translate title, subtitle, keywords (researched), descriptions and screenshots for priority markets; the store language list and the in-game language list should agree, or the page promises something the game does not deliver.
- Store localization is cheap relative to its effect on conversion in non-English markets; start with the top markets from `references/market-languages.md` in `accessibility-localization`.
- Use `store_metadata.py --locales en-US,de-DE,...` to scaffold; translations are reviewed by a native speaker (LQA).
- Respect character limits per locale; some languages need more characters, CJK needs fewer.

## 7. Ratings and reviews
- Ask for a rating after a positive moment (win, level-up), never after a failure, and never on first session; use the platform's in-app review API, which rate-limits prompts.
- Do not incentivise ratings or filter who is asked in a way the store disallows.
- Reply to reviews, especially low ones with concrete bugs; players see replies.
- Tag review themes weekly and feed them to `operate` and `player-analytics`.

## 8. Pre-flight checklist mapped to scripts
| Check | Automated by `compliance_preflight.py`? | Notes |
|---|---|---|
| Godot version supports 16 KB pages (>= 4.5) | Yes (`godot.16kb`) | Blocker |
| Export presets exist | Yes (`godot.presets`) | Blocker |
| Gradle build and AAB format | Yes (`android.gradle`, `android.aab`) | Blocker |
| arm64-v8a / ARM64 and IL2CPP | Yes (`android.arm64`, `android.il2cpp`) | Blocker |
| Target SDK at least 36 | Yes (`android.target_sdk`) | Warning if unset, blocker if below |
| Version code positive | Yes (`android.version_code`) | Blocker |
| Dangerous permissions | Yes (`android.permissions`) | Warning |
| Billing library 8+ | Info only for Unity; verify in plugin | Human check |
| iOS minimum version 13 or later | Yes (`ios.min_version`) | Blocker below floor |
| Package or bundle id valid and not placeholder | Yes | Blocker or warning |
| App icon present | Yes (`generic.icon`) | Blocker; alpha check is manual |
| Privacy policy URL declared | Yes (`generic.privacy_policy`) | Blocker; reachability is manual |
| Account deletion declared when accounts exist | Yes (`generic.account_deletion`) | Blocker; real flow is manual |
| ATT string when ads are present | Yes (`ios.att`) | Blocker |
| Privacy manifest present | Yes (`ios.privacy_manifest`) | Warning; completeness is manual |
| Odds disclosure when random rewards exist | Yes (`generic.odds`) | Blocker; correctness vs server tables is manual |
| COPPA flags when age_min below 13 | Yes (`generic.coppa`, `generic.coppa_ads`) | Blocker/warning |
| Data safety and App Privacy forms | No | Human with compliance-officer |
| Age rating answers | No | Human |
| Licences and AI provenance | Partly via `licence_check` tool | See `legal-ethics` |
| Screenshots match the build | No | Human or art-director |
| Review notes ready | No | Section 10 |

Run: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/compliance_preflight.py --project . --platform all --json`. Exit 1 means at least one blocker; exit 2 is a usage error. Warnings need a written decision in the release report.

## 9. Using `store_metadata.py`
```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/store_metadata.py --contract .gamestudio/contract.json --out store/ --locales en-US,de-DE --json
```
- It drafts a fastlane-style tree of title, subtitle, keywords, descriptions and what's-new text from the design contract, truncating at word boundaries to the limits in section 2.
- Exit 1 means a limit violation or a placeholder URL remains (default placeholder `https://example.com/`). Replace every placeholder URL before submission.
- Treat the output as a draft: check claims you cannot back, trademarks, tone, and that locale files are translated rather than copied.
- Upload with fastlane `metadata` lanes (`deliver` or `supply`); keep `submit_for_review` false.

## 10. Review notes and submission
1. Final pre-flight run attached to the release report.
2. Build processed and installed from the store channel (TestFlight or Play internal), not a local build.
3. Forms done: privacy, Data safety, age, ads, audience, export compliance, content declarations.
4. Review notes (template in `references/store-requirements-2026.md`, section 11).
5. Choose release option: manual release after approval, or phased/staged.
6. HUMAN approves submission in chat; only then is the version submitted (never by an automated script; the PreToolUse hook asks for confirmation).
7. After approval or rejection, update the release report and the postmortem log.

Expected timelines vary; do not promise launch dates to others until approval arrives. Schedule marketing for after approval with buffer days.

## 11. Launch week and post-launch routine
- Day 0: verify live listing, links, price, in-app products; install from the store on two devices; confirm analytics events and crash reporting arrive.
- Days 1 to 3: watch crash-free sessions, purchase success rate, retention day 1, store rating; ship a hotfix only for severe issues.
- Week 1: review feedback themes; update screenshots or text only through experiments.
- Ongoing: monthly keyword review, quarterly creative refresh, event-driven custom product pages for campaigns, update what's-new text with player-facing benefits.

## 12. Anti-patterns
- Keyword stuffing, competitor names, misleading claims, fake reviews.
- Screenshots with features not in the game; time-limited "free" claims that are untrue.
- Different language in store listing than in the game.
- Running three experiments on the same asset at once.
- Changing icon and title in the same week as a UA scale-up so effects cannot be separated.
- Submitting on Friday with no one available to answer a reviewer or fix a crash.

## 13. Volatile facts (as of Oct 2026 - verify)
- Character limits and experiment features change; confirm in App Store Connect and Play Console help before submission. Starting points: https://developer.apple.com/app-store/review/guidelines/ and https://support.google.com/googleplay/android-developer/
- Apple build SDK and deployment floors: https://developer.apple.com/news/upcoming-requirements/
- Google target API and billing floors: https://developer.android.com/google/play/requirements/target-sdk
- ATT opt-in rate reports conflict across sources: https://www.moburst.com/blog/idfa-att-update/

## 14. Diagnostics, category and soft-launch listing

### Funnel diagnostics
| Symptom | Likely cause | First action |
|---|---|---|
| Few impressions, healthy conversion | Weak keywords or category | Redo research, test title/subtitle, localize |
| Many impressions, low tap-through | Icon or title unclear, low rating | Test icon, clarify genre in title |
| Good tap-through, low page conversion | Screenshots/video misaligned with expectations | Test gameplay-first sequence, check first-lines of description |
| Good conversion, poor day-1 retention | Page over-promises or FTUE weak | Align creatives with the real first minute; fix FTUE (`player-psychology`, `mobile-ux`) |
| Conversion differs sharply by country | Missing localization or cultural mismatch | Localize creatives, review culturalization notes |
| Rating below genre norm | Crash, paywall friction, ads | Fix top review themes before more UA |

Compare against your own historical baselines and store-provided benchmarks; do not borrow conversion numbers from blog posts as targets.

### Category and positioning
- Pick the category where players of your genre browse and where you can rank, not the one with the lowest competition if the audience is elsewhere. Games categories are subdivided by genre on both stores; check where your two closest competitors sit.
- Positioning statement for the page, one line: "[verb phrase] in [setting], [differentiator]". Use it as the subtitle seed and the first caption.
- Price and IAP labels are part of the page: a free game with a visible high-priced pack can reduce conversion; a premium price needs stronger social proof. Test via experiments or regional pricing rather than guessing.

### Soft launch listing
- Launch in a small set of representative countries (see `market-intel`) with the final listing; use that traffic to test creatives early.
- Keep cohort-quality metrics next to creative metrics so a winning creative that attracts low-retention players is caught.
- Keep geo-specific features (loot-box restrictions, age gates) as a country matrix in the contract and verify it per country in the soft launch.
- Use the soft launch to rehearse review, rejection handling, and the staged rollout procedure.

### Metadata hygiene checklist
- [ ] No other company's trademark in title, subtitle, keywords or screenshots.
- [ ] Claims substantiated or removed (rankings, awards, "best", "free" if IAP exists is acceptable but do not imply no purchases).
- [ ] Support URL and privacy policy reachable over https.
- [ ] Copyright line matches the legal entity.
- [ ] Every locale file translated, reviewed and within limits.
- [ ] What's-new text lists player-visible changes truthfully.
- [ ] Age-rating-relevant features visible in screenshots match the questionnaire answers.
- [ ] Promotional text updated for current events (Apple allows changing it without a new build).
