# Certification Themes and Age Ratings

This file lists the public themes of console certification (what every platform tests in broad terms), the usual reasons games fail, and a self-audit procedure you can run before you have the confidential documents. It then covers age ratings: IARC, ESRB, PEGI, USK, CERO, ACB, GRAC and ClassInd, which each console store needs and how to obtain them. The exact certification requirements, numbered rules and test cases are under NDA and are not reproduced; the themes below come from public developer talks and public pages, and every rule must be confirmed in the platform's own documents after approval.

## Contents
1. What certification is
2. Public themes
3. Common failure causes
4. Self-audit procedure before certification
5. Test matrix for soak and edge cases
6. Submission process (human gates)
7. Age ratings: the systems
8. Which console store needs what
9. How to obtain ratings
10. Rating content preparation

## 1. What certification is
1. After development, the platform holder tests your build against its technical and policy requirements before it can go on sale.
2. Test rounds are repeated until the build passes; plan for at least two rounds and a re-submission delay each.
3. Requirements differ by platform and change over time; each platform documents its own, under NDA. Public themes below are the overlap.
4. Pass is for a specific build; later patches go through a lighter version of the process (details in platform documents).

## 2. Public themes
| Theme | What platforms generally care about | What to build or test |
|---|---|---|
| Save data | Saves are safe, not corrupted by power loss or suspend; clear indicators when saving; storage full handled; save data tied to the right user | Atomic write (write temp, verify, swap); versioned format; test pulling power during save; test full storage |
| Network errors | Offline or lost connection does not crash or hang; clear messages; online features gated by account state and privileges | Simulate disconnect at each online call; timeouts; retry with backoff; offline single-player |
| User accounts | The game follows the signed-in user; handles sign-out, user switch, restricted accounts, child accounts | Handle user change events at any screen; do not cache the previous user's data |
| Suspend and resume | The game can be suspended (sleep, home button, system overlay) and resumed, including after hours or a network change | Pause logic, resume audio and network, rebuild timers; test at loading screens and mid-save |
| Trophies and achievements | Required or recommended sets; correct unlock; no spoilers; platform-specific naming and icons | Per-platform achievement table; test unlocks and offline queueing |
| Text and terminology | Official names for buttons, features and the platform; no references to other platforms or stores; correct legal text | A glossary per platform; strip "Press Esc", "Steam" and "click" strings |
| Accessibility | Subtitles, text size, controller remapping or alternatives, photosensitivity and flashing limits | See `accessibility-localization`; run a flashing test |
| Input | Controller disconnect and reconnect handling; correct glyphs; no keyboard dependence | Pull the controller at every screen |
| Performance and stability | Frame rate stable in the declared mode; no crash or hang in long sessions; memory within budget | Soak test 8 to 12 hours; stress test worst scenes |
| Content and policy | Age rating matches content; no prohibited content; no web views or external links in the game; no online ads or prohibited monetisation | Content review; remove external links and QR codes; check IAP rules per platform |
| Display | Safe area; resolution modes (for example docked and handheld); HDR where used | See `references/porting-plan.md` for TV and handheld UX |
| Legal and privacy | Privacy notice, data collection consent, children's protections | See `legal-ethics` |
Xbox's public developer documentation lists requirement pages under https://devdocs.xbox.com/publishing/certification/ (for example a page on age ratings, XR-017); read what is public there. Other platforms keep their lists behind the agreement.

## 3. Common failure causes
Reported by developers and partners in public talks (general; platform specifics are NDA):
1. Save corruption or loss after suspend, power cut or storage full.
2. Crash or hang on controller disconnect, user sign-out or network drop.
3. Missing or wrong trophies or achievements (unlock does not fire, wrong icon, duplicate).
4. Wrong terminology or a leftover PC string ("press Enter", "click", "Steam overlay").
5. Text that overflows or is unreadable at TV distance or handheld size.
6. Frame rate or load times outside the declared target; memory growth over a long session.
7. Missing localisation in a language the store page promises.
8. Age rating mismatch (content not declared in the questionnaire).
9. An external link, web view, QR code or reference to another store in the game or store text.
10. Online features that fail without a subscription or with parental restrictions.
11. Unhandled errors from platform services (store unavailable, account locked).
12. Patch day-one problems: build not matching the submitted one, stale content.

## 4. Self-audit procedure before certification
1. Build a release candidate for the console (or the PC build with console mode toggles if the platform build is not ready).
2. Run the readiness table (`SKILL.md` section E). Every row has a pass, fail or n/a with evidence (video or log).
3. Run the test matrix in section 5.
4. Fix failures; re-run only the affected rows.
5. When the platform documents arrive, map each requirement to a row; add missing rows. Keep the mapping in a private file that is not committed to public repositories.
6. A human signs off before submission. Record the build id, date and results in `.gamestudio/reports/console-<platform>-<date>.md` (summary only).

## 5. Test matrix for soak and edge cases
| Test | Steps | Pass |
|---|---|---|
| Suspend mid-play | Suspend for 10 seconds, 10 minutes, 8 hours; resume | State intact; audio and network recover |
| Suspend mid-save | Suspend or power off during a save | Previous save still loads |
| User switch | Sign out, sign in as a different user at menu and in game | No crash; correct save shown |
| Controller disconnect | Remove the controller in menus, play, cutscene, loading | Pause and message; resume on reconnect |
| Network loss | Remove the network at each online call | Message and graceful fallback |
| Storage full | Fill storage and save | Clear message; no corruption |
| Long session | Play 8 to 12 hours, repeating the worst scene | No memory growth, no crash |
| Fast boot and quit | Launch, quit at menu, relaunch 20 times | Stable |
| Language switch | Switch system language | UI updates; no clipped text |
| Display modes | Docked and handheld (where relevant); 720p to 4K | Safe area, legible text |
| Achievements | Unlock each one in order, offline and online | Correct unlock and no duplicates |
| Content audit | Search for external links, "PC" wording, store names | None |
Automate where possible: an input fuzzer script, a save-corruption injector and a soak runner belong in `qa-testing`.

## 6. Submission process (human gates)
1. Human confirms the release candidate and the store text.
2. Human completes the platform's submission form and uploads the build through the platform's portal.
3. Agent monitors the result email text pasted by the human; do not give the agent credentials.
4. Failure report: summarise and map to fixes; do not post confidential report text publicly; write only the summary in the repository.
5. Resubmit after fixes; human approves each resubmission.
6. Pass: human schedules the release date and store page.

## 7. Age ratings: the systems
| System | Region | Notes |
|---|---|---|
| IARC | Global umbrella | One questionnaire yields ratings for several authorities in participating storefronts |
| ESRB | North America | Member of IARC |
| PEGI | Europe | Member of IARC |
| USK | Germany | Member of IARC (founding group) |
| ACB (Australian Classification Board) | Australia | Member of IARC; some content can be refused classification |
| ClassInd | Brazil | Member of IARC |
| GRAC | South Korea | Joined IARC later; assigns ratings for participating storefronts |
| CERO | Japan | Separate; not an IARC participant in the sources checked in October 2026: unverified |
Founding IARC members listed by the coalition: ClassInd, the Australian Classification Board, ESRB, PEGI and USK; GRAC joined later; others (Taiwan, Indonesia and more) appear in the milestone timeline (https://www.globalratings.com/milestones).

## 8. Which console store needs what
Findings from public sources (verify for the current year):
| Store | Digital rating route | Notes |
|---|---|---|
| Nintendo eShop | IARC rating at no fee for digital-only titles (Nintendo FAQ) | Nintendo was the first console maker to adopt IARC (2015); in Japan, reported to accept IARC only below a certain age band |
| Xbox | IARC for digital distribution; physical discs often need certificates from each board | Xbox Series X/S counts as a new platform for most authorities, which may require a separate classification (Xbox docs, reported) |
| PlayStation Store | IARC displays ratings for digital games (milestone timeline); in Japan reported to accept IARC for download-only titles since March 2022 but to require CERO for 18+ games | Verify with PlayStation Partners documents |
| Physical releases | Authority certificates per region (PEGI, USK, ESRB, CERO and others) | Handled by the publisher or the manufacturing partner |
| Japan | CERO required for physical; costs reported to be higher and charged per platform | A 2022 industry article describes CERO costs for small creators: check current fees |
Default plan: digital-only first (IARC through the store questionnaire), physical later through a publisher.

## 9. How to obtain ratings
1. IARC (digital): complete the platform's rating questionnaire inside its developer portal (answers about violence, language, sex, drugs, gambling, user interaction, online purchases and similar). The system issues ratings per participating authority. Keep a copy of the certificate and the answers.
2. Platform specifics: the form is embedded in the Nintendo Developer Portal, Partner Center for Xbox and the PlayStation tools; availability is described in each platform's documents.
3. Physical or non-IARC regions: apply to each authority directly (ESRB, PEGI, USK, CERO, and others) with a build or video, sometimes a fee and a delay of weeks. Your publisher usually handles this.
4. Re-rating: content changes or a major update can require a new questionnaire; keep the answers in version control (summary only).
5. Mismatch risk: answering truthfully matters; a store can change a rating after review, and a mismatch is a certification failure.
6. Consistency: the Steam content survey, the Apple and Google forms, and the console forms should match; keep one questionnaire source of truth (`.gamestudio/contract.json` content flags) and fill each form from it. See `legal-ethics`.

## 10. Rating content preparation
1. List content: violence (intensity, blood, realism), sexual content, language, substances, gambling or simulated gambling, fear, discrimination, user-generated content, online chat, in-game purchases, loot boxes or random rewards.
2. Capture evidence: short videos of the strongest examples for each category.
3. Decide the target rating early (the `age_min` in the contract) and design to it; removing content late is expensive.
4. Check regional specifics: some content is prohibited in some territories (for example certain imagery in Germany, restrictions in Australia and Korea); ask the platform or a publisher.
5. Keep text and trailers in line with the rating; trailers on stores follow store rules.
