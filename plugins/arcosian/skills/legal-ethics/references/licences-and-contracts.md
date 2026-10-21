# Licences and contracts

Summary: a shipped mobile game is a bundle of other people's work under dozens of licences: engine, libraries, SDKs, fonts, art, music, sound and tools, plus contracts with freelancers, publishers and platforms. This file explains which licence families are safe in a closed-source app-store binary, which are not, how to keep a register that proves compliance, and what to look for in asset-store, music, font, publishing and platform agreements. Not legal advice: licence texts and contracts are binding documents, so read the actual text and escalate anything unusual to counsel.

## Contents
1. Principles
2. Open-source licence families
3. Licences in app-store binaries: the GPL problem
4. Engine and SDK licences
5. Fonts
6. Art, asset-store and stock licences
7. Music, sound and voice
8. AI tool terms
9. Attribution and notices in the game
10. Licence register and CI check
11. Freelancer and work-for-hire contracts
12. Publishing agreements
13. Platform agreements
14. Red-flag clause table
15. Volatile facts (as of Oct 2026 - verify)
16. Worked examples and onboarding checklist

## 1. Principles
1. No licence, no use. Absence of a licence file means all rights reserved.
2. A licence applies to the thing as distributed: if you ship it inside the app, its terms apply to your users and to you.
3. Record every dependency and asset with licence, version, source URL and date.
4. Prefer permissive licences for code and clearly commercial-use licences for assets.
5. Licences are not transferable by assumption: a licence bought by a freelancer is not yours unless the contract says so.
6. Keep the proof: invoices, licence PDFs, store receipts, emails.

## 2. Open-source licence families
| Family | Examples | Closed-source mobile use | Obligations (summary) |
|---|---|---|---|
| Permissive | MIT, BSD-2/3, Apache-2.0, zlib, ISC | Yes | Keep copyright and licence text; Apache adds patent grant and NOTICE handling |
| Public domain dedications | CC0, Unlicense | Yes | None legally; still record |
| Weak copyleft | LGPL, MPL-2.0, EPL | Usually, with care | LGPL needs the user to be able to relink or replace the library (hard on iOS static linking); MPL requires sharing changes to MPL files |
| Strong copyleft | GPL-2.0, GPL-3.0 | Generally no for linked code | Whole combined work must be offered under the GPL; also conflicts with store terms in some readings |
| Network copyleft | AGPL | No for client code; caution server side | Source offer to network users |
| Non-commercial / no-derivatives | CC BY-NC, CC BY-ND, custom | No for commercial games | Forbidden use |
| Attribution licences | CC BY, CC BY-SA | CC BY yes with credit; BY-SA affects adaptations | Credit, link, indicate changes; SA requires same licence on adaptations |
Practical rules:
- Code under MIT, BSD, Apache, zlib: use freely with notices.
- Anything GPL or AGPL: do not link into the game. A separate server process under GPL communicating over a network is different from linking, but ask counsel.
- Creative Commons licences are for creative works, not software; CC BY-SA on art can force your derivative art to be share-alike.
- "Free for personal use", "free for indie" or revenue-capped licences: read the thresholds and what happens when you cross them.

## 3. Licences in app-store binaries: the GPL problem
- Store distribution adds terms (device limits, DRM, no redistribution) that can conflict with GPL's prohibition on additional restrictions. Treat GPL code in an iOS or Android app as a no-go.
- LGPL on iOS: dynamic replacement of the library is not practical because of code signing and static linking rules; avoid LGPL for iOS builds. On Android, dynamic linking of a shared library is feasible but needs a replaceable path and notices.
- Engines and middleware sometimes bundle GPL tools (build utilities); tools used only on the developer machine do not make the shipped game GPL, but tools that inject code into the build do.
- Check transitive dependencies; scan the resolved dependency tree, not only your direct list.

## 4. Engine and SDK licences
- **Godot**: MIT licensed engine; the exported game is yours; include the engine's licence notices (the engine provides a licence text accessible in-game via an API; use it in a credits screen).
- **Unity**: proprietary terms, with plan tiers and revenue thresholds; the terms and runtime fee policies have changed in the past, so read the current terms and keep a copy for the version you ship. Licence activation matters for CI (`store-release`).
- **Third-party engines and frameworks** (see `engine-alternatives`): check royalty, attribution and source-availability terms.
- **SDKs** (ads, analytics, attribution, IAP): licence agreements restrict redistribution, require the latest versions, impose data-handling rules and may forbid use in child-directed apps. Read the developer terms, not just the quickstart.
- Pin versions and store the licence of the version shipped.

## 5. Fonts
- Font licences are separate for desktop, web and app embedding. Embedding a font in a mobile app is "app embedding" and often needs a specific licence tier.
- Safe defaults: fonts under SIL Open Font License (OFL) or Apache-2.0 are generally free to embed in games, with the licence file included; OFL forbids selling the font by itself and has reserved-name rules for modified versions.
- Commercial foundry fonts: buy the app/game licence with the correct number of apps or monthly users; keep the invoice.
- Logos and stylised titles made from a font: check the licence for logo use; some forbid it.
- CJK and Arabic fonts are large and often under OFL; verify per family (see `accessibility-localization` references for coverage and size).
- Do not extract fonts from other games or apps.
- Icon fonts and emoji sets have their own licences; platform emoji cannot be redistributed.

## 6. Art, asset-store and stock licences
- Asset-store licences (engine stores, itch bundles, stock sites) usually permit use inside a game binary but forbid redistribution of the raw assets, resale as an asset pack, or use in an asset-creation tool. Read for: commercial use, number of seats, per-project vs unlimited, derivative edits, and whether the licence transfers if the studio is acquired.
- Seat licences: each team member using the asset needs a seat in many stores.
- Free assets: "free" does not mean public domain; check the licence on the specific listing, and screenshot it.
- Models and textures derived from real brands, cars, or people may need separate clearance even when the asset-store creator sells them.
- Do not use assets from game rips, fan sites or wikis.
- Your own contractors' art: contract for assignment (section 11).
- Keep a copy of the licence at purchase time; stores update terms.

## 7. Music, sound and voice
Music rights have layers: composition (the song), master recording (the particular recording), and performance; each can have a different owner.
| Source | Typical terms | Check |
|---|---|---|
| Commissioned composer | Work for hire or assignment, or licence | Written agreement, stems, credits, soundtrack release rights |
| Production-music library | Licence per project or subscription | Platform coverage (mobile games), cancellation effect on already-released games, content-ID registration prevention |
| Royalty-free packs | One-time fee; free to use in games | No resale of stems, attribution requirement |
| AI music tools | Terms differ; some limit commercial use by plan | Output licence at generation time, content-ID behaviour; see `ai-audio-pipeline` |
| Commercial songs | Sync and master licences from both rights holders | Expensive and slow; avoid for indie mobile |
| Sound effects libraries | Per-licence | Same as royalty-free; no standalone redistribution |
Voice: contract for scope (game, trailers, marketing), term, territory, AI and digital replica use, credits and buyouts. Record in the provenance log.
Streaming or user-generated content: if players can stream your game, decide whether music is safe for streaming; some libraries restrict it.

## 8. AI tool terms
- Store the terms of each generation tool at the date of use: commercial use rights, ownership statements, indemnity, restrictions on sensitive content, and whether the vendor trains on your inputs.
- Free or trial plans may forbid commercial use.
- If the tool changes its terms later, the licence for already generated content generally stays as at generation time, but verify and keep the evidence.
- See `references/ip-and-ai-content.md` for ownership and disclosure.

## 9. Attribution and notices in the game
- Add a Credits and Licences screen reachable from settings. Include: engine notice, library notices (MIT, BSD, Apache notices as required), CC BY attributions with names and links, font licences where required, music credits.
- Generate the text from the register; ship it as a bundled file (`licences.txt`) and display it in-game.
- Provide the licence text for each Apache component and the NOTICE file contents if present.
- Update with every release; the pre-flight should fail if the register changed and the file did not.

## 10. Licence register and CI check
Minimal register columns: id, name, type (code, font, art, audio, tool), version, source URL, licence id, licence file path, commercial OK (yes/no/needs review), attribution required, redistribution constraints, seats, purchase proof reference, date added, owner.
Procedure:
1. Add an entry when a dependency or asset enters the repo; the asset gateway does so for generated assets.
2. CI scans package manifests (Godot addons, Unity `Packages/manifest.json`, Gradle and CocoaPods lock files) and compares with the register; unknown entries fail the build.
3. Allowed-licence policy: allow permissive and public domain automatically; block GPL, AGPL, NC and ND; send LGPL, MPL, custom and unknown to review.
4. Generate the credits file from the register.
5. Before a release, run the `licence_check` tool and attach the result to the release report.

## 11. Freelancer and work-for-hire contracts
Clauses to require:
- **IP assignment** on payment (or work-made-for-hire where the law recognises it for the work type) so the studio owns deliverables; moral rights waiver or consent where applicable.
- **Originality warranty**: no copying, no unlicensed third-party material, disclosure of any AI tools used, with limits on which.
- **Deliverables**: source files, layered files, project files and exports, not just final images.
- **Credits**: how and where.
- **Confidentiality** and non-disclosure of unreleased work.
- **Portfolio rights**: when the freelancer may show the work.
- **Indemnity** for infringement caused by the freelancer; practical limit is the freelancer's means.
- **Payment, milestones, kill fee, revisions**: protect both sides.
- **Data protection**: when freelancers handle player data, require processor terms.
- **Governing law and dispute process.**
Employees: check employment IP assignment; contractors working under a studio they do not own need explicit assignment.
Collaborators and revenue shares: put the share, vesting, and what happens if someone leaves in writing early; verbal deals are the most common cause of indie disputes.

## 12. Publishing agreements
Publishers fund, market or operate games in exchange for a share. Read for:
| Clause | What to check |
|---|---|
| IP ownership | Does the studio keep the IP, or assign it? Does the publisher get sequels, ports or derivative rights? |
| Term and territory | Length, auto-renewal, regions, platforms |
| Exclusivity | Other platforms, engines, stores, your next game |
| Revenue split and recoupment | Is the advance recouped from developer share only? Are marketing costs recoupable and capped? Are taxes and store fees deducted before the split? |
| Reporting and audit | Frequency, detail, your audit right |
| Milestones | Acceptance criteria, deemed acceptance, payment dates, termination for missed milestones |
| Control | Approval over design, monetization, live-ops changes, sunset decisions |
| Data | Who owns player data and analytics access |
| Termination | Triggers, rights reversion, post-termination sell-off, transition help |
| Change of control | Assignment of the contract on acquisition |
| Warranties and indemnities | Scope and caps; who bears the cost of an IP claim |
| Sunset | Server shutdown obligations, offline mode |
| Non-compete | Narrow or broad |
Rules: negotiate rights reversion (if the publisher stops marketing or revenue falls below a threshold, rights return), cap the recoupable marketing, and never sign without counsel for money or IP of significance. Work-for-hire deals for platform-funded games are separate; read them for IP transfer.

## 13. Platform agreements
- Apple Developer Program License Agreement and Google Play Developer Distribution Agreement are non-negotiable; key points: payment terms and commission, tax responsibilities, content rules, termination rights for the platform, data use, and your responsibility for the content and SDKs.
- Accept updated agreements promptly; builds can be blocked until you accept.
- Individual vs organisation accounts: ownership of the account and the app listing; a studio should use an organisation account owned by the company, not a founder's personal account, to avoid account-transfer trouble.
- App transfer between accounts is possible but has conditions (IAP, subscriptions, entitlements); plan ownership early.
- Alternative distribution or payment options in some regions (EU, US litigation outcomes) bring separate terms and fees; see `store-release` volatile facts.
- Third-party SDK and ad network agreements: payment thresholds, invalid traffic clauses, data restrictions.
- Tax: platforms collect and remit sales taxes in many jurisdictions; income tax, withholding and treaty forms are your responsibility; consult an accountant.

## 14. Red-flag clause table
| Clause | Why it hurts | Counter |
|---|---|---|
| Assignment of all IP including pre-existing tools | You lose engine code and tools | Carve out background IP; licence not assign |
| Perpetual exclusive rights to sequels or "similar games" | Locks your future | Limit to named IP, time-limit |
| Unlimited recoupment of undefined costs | Never see revenue | Cap, approvals, itemisation |
| Termination for convenience by publisher only | One-sided | Mutual rights, notice, wind-down payment |
| No audit right | Cannot verify reports | Annual audit right at publisher cost on discrepancy |
| Indemnity without cap | Existential risk | Cap at fees received |
| "Moral rights" and credit waiver without credit clause | No credits | Keep credit obligations |
| Non-compete beyond the project | Blocks work | Limit by scope and time |
| Asset licence "for evaluation only" | Cannot ship | Buy full licence |
| Font licence capped on downloads | Costs balloon | Buy suitable tier or switch font |

## 15. Volatile facts (as of Oct 2026 - verify)
- Godot licence and notices: https://godotengine.org/license/
- Unity terms and plan thresholds change; read the current terms at https://unity.com/legal
- Open Font License text and FAQ: https://openfontlicense.org/
- Apache-2.0, MIT, BSD, GPL, LGPL texts: https://opensource.org/licenses
- Creative Commons licence deeds: https://creativecommons.org/licenses/
- Apple Developer Program License Agreement: https://developer.apple.com/support/terms/
- Google Play Developer Distribution Agreement: https://play.google.com/about/developer-distribution-agreement.html
- Alternative payments and link-out developments are in flux (Apple v. Epic proceedings, EU rules): https://law.justia.com/cases/federal/appellate-courts/ca9/25-2935/25-2935-2025-12-11.html ; https://www.apple.com/newsroom/2026/08/apple-announces-changes-for-apps-in-the-european-union/
- AI tool terms change often; store the terms at the date of use.

## 16. Worked examples and onboarding checklist

### Example A: adding a tween library from GitHub
1. Find the licence file in the repo root. MIT: allowed. Note version and commit hash.
2. Check its dependencies for copyleft; scan the lock file.
3. Add the register entry and the notice to `licences.txt`.
4. If the repo has no licence file, do not use it; ask the author to add one or pick another library.

### Example B: asset-store environment pack
1. Read the licence on the purchase page and the bundled licence file; confirm commercial game use and seat count for the team.
2. Check whether you can modify and re-export textures (usually yes) and whether source files may be shared with contractors (often needs seats for them).
3. Save the receipt and the licence text with the date; register the pack.
4. If the studio is sold later, check whether the licence survives change of control.

### Example C: free music track marked CC BY
1. Attribution is required: artist, title, link, licence, and a note if modified.
2. Add it to the credits screen and `licences.txt`.
3. Check whether the licence excludes use in games or in video; some tracks add extra conditions.
4. Confirm the track is not registered with a content-ID system that will claim your trailers.

### Example D: SDK with revenue-share terms
Read payment thresholds, invalid-traffic clauses and minimum SDK version rules; set a calendar reminder to update when the vendor deprecates versions, because stores and the vendor can both block outdated builds.

### New dependency or asset checklist
- [ ] Licence text read and saved.
- [ ] Commercial use in a closed-source mobile app allowed.
- [ ] Child-directed use allowed (if relevant).
- [ ] Attribution text drafted.
- [ ] Seat and revenue thresholds noted.
- [ ] Transitive dependencies scanned.
- [ ] Register entry added with owner.
- [ ] Credits file regenerated.
- [ ] Alternative identified if the licence changes.

### Quarterly licence review
Run the register scan; check each vendor for term changes; renew expiring subscriptions (music libraries, fonts, tools) and decide what happens to released games if a subscription lapses; archive the licence PDFs with the release tags.
