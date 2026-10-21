---
name: console-pathway
description: Guidance for getting a game onto Nintendo, PlayStation and Xbox consoles using public information only - self-publish, publisher or porting partner; when to start; budget and time ranges; what design and code must already do (controller UI, safe area, suspend, user switching, saves); programmes, ratings and a porting plan. Use for "should we port to Switch", "how do I get a dev kit", "console age ratings".
---

# Console Pathway

## What this skill gives you
- A decision procedure: self-publish through the platform programme, sign with a publisher, or hire a porting partner, with budget and time as ranges.
- A readiness list: what the game's design and code must already do before any port starts, so the port is a translation and not a rewrite.
- Public information about the three programmes (Nintendo Developer Portal, ID@Xbox, PlayStation Partners), engine support, public themes of certification, and age rating routes.
- A porting plan template with phases, staffing, performance targets, a risk register and a worked 2D example.

## The NDA boundary
Console SDKs, development kit specifications, technical requirements documents and certification checklists are covered by non-disclosure agreements that you sign after approval. This skill uses only public pages and public themes. It does not contain, and must never be asked to produce, SDK APIs, memory budgets from NDA documents, certification requirement numbers or test cases. Where the plan needs those, it says "from the platform's documents after you are approved". If a human pastes NDA material into a conversation, do not store it in the repository or a public file, and flag it. Public repositories must never contain console SDK code, headers or documents.

## Core models
**1. Access is a gate, not a purchase.** You cannot buy your way to console builds. Each platform holder approves the developer (registration), the game (concept or pitch) and the release (certification). Plan for three approvals per platform, each taking weeks.

**2. A port is mostly design debt.** The hardest parts are not rendering. They are behaviours: suspending and resuming, switching users, handling controller disconnects, safe saves, no keyboard, no web views, memory pressure, and text rules. A game built with these in mind ports in weeks; a game that is not takes months.

**3. Three ways to ship, one trade-off.** Self-publishing keeps revenue and control but needs staff, approvals and cash for kits. A publisher funds and handles the process but takes a share and rights. A porting partner does the engineering work and sometimes the publishing, for a fee or a revenue share. Choose by the scarce resource: staff time, cash, or relationships.

**4. Consoles reward finished, polished, well-reviewed games.** A game with strong reviews and a clean PC release is an easier pitch than a concept. Release on PC first (see `pc-web-release`), then port.

**5. Console releases are slow clocks.** Registration, kit shipping, certification rounds, rating certificates and store scheduling stack. Start the process 6 to 9 months before the target date for a first title (estimate).

**6. Every submission is human-approved.** An agent prepares checklists, builds, store text and test logs. A human signs agreements, enters identity and tax data, submits concepts, and presses submit for certification. Never put credentials or NDA content in files.

## Decision procedures

### A. Should this game go to console at all?
Go if at least three are true:
1. The game plays well with a controller (design contract `meta.input` includes gamepad) and has no mouse-only mechanics.
2. A PC release exists or is near, with solid reviews or a visible audience.
3. The audience plays on console (genres: platformers, action, roguelikes, puzzle, narrative, co-op party).
4. The team can support patches and bug reports for a further platform for at least 6 months.
5. Budget exists for kits, ports, ratings and certification (section C).
Do not port if the game depends on mods, a keyboard, precision pointer input, heavy text entry or an online service you cannot extend to consoles.

### B. Which route
| Situation | Route | Why |
|---|---|---|
| Small team, engine and design already console-friendly; some budget | Self-publish through the platform programme | Keep revenue and control |
| No engine access, or team has no time for ports | Porting partner (fee or rev share; some also publish) | Their staff and their kit access |
| No money and strong pitch; wants marketing and funding | Publisher | Advance and platform relationships |
| Wants Game Pass or platform feature funding | Pitch the platform holder after approval (ID@Xbox lists funding as a path after joining) | Business decision by the holder |
| Unreal or Unity with a larger budget | Self-publish through the programme, use the engine's console modules | Engine vendors support consoles through platform holders |
| Godot | Porting partner or middleware vendor | Godot does not ship console export templates itself |
Order of platforms: for most indie games Switch first (large indie audience; Switch 2 now relevant), then Xbox and PlayStation. Evidence beats this default; ask your partner or publisher which platform buys your genre.

### C. Budget and time (planning ranges; estimates, verify with quotes)
| Item | Typical range | Note |
|---|---|---|
| Developer registration | Free (Nintendo portal registration is free; ID@Xbox reported free) | Public |
| Dev kits | Hundreds to a few thousand USD per kit, or loaned (varies); public figures are unreliable | Details inside the programme |
| Porting partner for a small 2D game | Tens of thousands USD per platform, or a revenue share | Get at least two quotes |
| Self-port by your team | 2 to 6 person-months per platform for a well-prepared 2D game | Estimate |
| Ratings | Digital IARC: no fee at Nintendo; physical or Japan 18+ may need CERO | See `references/certification-and-ratings.md` |
| Localisation, QA, certification rounds | 10 to 30 percent of port cost | Estimate |
| Calendar | 4 to 9 months from approval to release for a first title | Estimate |
These are priors, not quotes. Replace them with real quotes and record the source.

### D. When to start
1. Concept stage: design controller-first and write the readiness list (section E) into the design contract.
2. Production: avoid engine or middleware choices that block consoles (web views, unsupported plug-ins).
3. Six to nine months before the target date: register with the platform programmes; apply for access with the game's public page, trailer and build.
4. After approval: sign agreements (NDA), receive documents, order or borrow kits, replan the port with the real requirements.
5. Pre-certification: internal checklist from the platform's documents; ratings; store assets.
6. Certification: submit (human), fix, resubmit; allow at least two rounds.
7. Release: coordinate with PC patches so the console build has parity.

### E. Readiness: what the game must already do
| Area | Requirement before porting |
|---|---|
| Input | Full controller-only play, including menus and all UI; alternatives to keyboard text entry; button glyphs for the active controller; no hover-only controls |
| Display | TV safe area margins on all HUD elements; legible text at 2 to 3 metres; supports docked and handheld resolutions where relevant |
| Suspend and resume | Survives suspension and resume at any moment, including mid-save, without losing progress; audio and timers recover |
| User switching | Handles a different user signing in or the active user signing out; progress tied to a user where the platform requires it |
| Controller changes | Disconnect pauses the game with a message; a different controller can take over |
| Saves | Atomic, versioned, corruption-safe; handles full storage; cloud conflicts; never write every frame |
| Network | Clear messages and recovery for offline, lost connection and account restrictions; no hard dependence on a connection for single-player |
| Web views and links | No embedded web views, external browser links or QR purchases |
| Text | Localised UI that fits; content suited to the age rating; correct platform terms and button names |
| Achievements | Map to the platform's trophies or achievements; a table per platform |
| Performance | Stable target (30 or 60 fps) on the weakest mode; no long load hitches; memory within the platform budget (from the platform's documents) |
| Accessibility | Subtitles, simple or remappable controls, colour not the only signal (see `accessibility-localization`) |
| Privacy and legal | Privacy policy, children's data handling, loot box rules (see `legal-ethics`) |
Use the `platform-targets` skill for input and platform UX detail.

### F. The submission rule (human gate)
1. Registration, concept or pitch submissions, agreements, tax and bank forms, dev kit orders, certification submissions and store page publication are human actions.
2. The agent prepares: the pitch document, a build or video, the readiness audit, test logs, ratings questionnaire answers and store text.
3. Record approvals in `.gamestudio/reports/console-<platform>-<date>.md`; never commit NDA material.

### G. Worked example: a 2D platformer going to Switch
Game: Godot 4, 2D, controller-first, 5 hours, on Steam with 1,500 reviews at 92 percent positive (illustrative).
1. Route: Godot has no console templates; ask two porting partners from Godot's console page for quotes, sending the PC build and the readiness audit.
2. Audit: the game fails three checks (suspend mid-save, controller disconnect, text size at handheld resolution). Fix them on PC first (4 weeks).
3. Registration: a human registers on the Nintendo Developer Portal and submits the Switch access request with the Steam page and trailer.
4. Plan: use `references/porting-plan.md` to schedule 16 weeks: 4 for the engine port by the partner, 6 for platform features and performance, 4 for QA and ratings, 2 for submission rounds (estimate).
5. Ratings: digital-only titles can obtain IARC ratings at no fee at Nintendo; confirm the exact path with the platform documents.
6. Release: ship a PC update with the console fixes first, then the console release; announce after certification passes.

## Platform specifics
- **Nintendo**: Switch and Switch 2; registration open to individuals and companies; Switch access requested by form after registering. Handheld and TV modes mean two resolutions and two input situations.
- **Xbox**: ID@Xbox needs concept approval and agreements; covers Xbox consoles and Xbox on PC; some Xbox publishing documents are public at devdocs.xbox.com.
- **PlayStation**: registration via PlayStation Partners with a project plan; approval and agreements gate tools and backend.
- **All**: dev kits and certification documents are behind NDAs; digital storefront ratings mostly go through IARC, with exceptions.

## Anti-patterns
- Starting a port before the PC release is stable.
- Planning the schedule from public blog numbers instead of platform documents and partner quotes.
- Treating the port as a recompile: no budget for platform features, QA, ratings and certification rounds.
- Putting NDA material, SDK headers or keys into a repository, issue or chat.
- Leaving suspend, user switching and save safety to the last month.
- Signing with a porting partner or publisher without reading exclusivity, rights, revenue and exit clauses (a human or lawyer decides).
- Releasing on three consoles at once for a first title; stagger by platform.
- Assuming one age rating covers all regions and physical editions.
- Announcing a console release date before the platform confirms certification and store scheduling.

## Using the ontology
- `.gamestudio/contract.json`: `meta.platforms` (add `switch`, `playstation`, `xbox`), `meta.input` (`gamepad`), age rating targets and audience (`age_min`). Readiness items map to features in `.gamestudio/features.json` (for example "suspend and resume safe", "controller-only UI", "TV safe area").
- Add the readiness list as acceptance criteria on the relevant features; the five gates apply as usual.
- Process skill: `ship` (human gates); agents: `arcosian:release-manager`, `arcosian:compliance-officer`, `arcosian:producer` for the porting plan. Workflow: `/arcosian:release-candidate`.

## Reference library
| File | What it contains | When to read |
|---|---|---|
| `references/programmes-and-access.md` | Nintendo Developer Portal, ID@Xbox, PlayStation Partners: eligibility, process, kits; engine support and porting companies | Choosing a route and applying |
| `references/certification-and-ratings.md` | Public certification themes, common failures, age ratings by region and store | Preparing for certification |
| `references/porting-plan.md` | Plan template, staffing, performance targets, controller and TV UX conversion, risk register, worked 2D example | Planning the port |

## Volatile facts (as of Oct 2026 - verify)
- Nintendo Developer Portal registration, legal age, Switch access request form, Switch 2 page: https://developer.nintendo.com/register and https://developer.nintendo.com/faq
- ID@Xbox application steps and review time (typically 10 to 15 business days, up to 3 weeks): https://learn.microsoft.com/en-us/gaming/game-publishing/onboarding/onboarding-join-id-at-xbox
- PlayStation Partners registration (page content not retrievable; steps from Sony's public indie guidance via secondary reports): https://partners.playstation.net
- Godot console support, porting companies and W4 Games middleware: https://docs.godotengine.org/en/4.5/tutorials/platform/consoles.html
- Unity console build access and licence rules (platform-holder approval, Pro or platform key; secondary sources): https://unity.com/solutions/console
- IARC participants and milestones: https://www.globalratings.com/milestones
- Xbox rating requirement documentation: https://devdocs.xbox.com/publishing/certification/xr/xr-017

## Related skills
- `store-release`: the mobile pipeline; shares the human-gate model.
- `pc-web-release`: PC release first; signing and store pipeline.
- `platform-targets`: input, UX and performance per platform.
- `engine-godot`, `engine-unity`: engine-specific porting concerns.
- `legal-ethics`: ratings, privacy and children's rules.
- `accessibility-localization`: accessibility and text requirements.
- `production`: schedule and risk management for the port.
- `qa-testing`: test plans and certification-style soak tests.
