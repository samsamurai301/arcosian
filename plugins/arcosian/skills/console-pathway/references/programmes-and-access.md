# Programmes and Access: Nintendo, Xbox, PlayStation

This file describes, from public pages only, how a developer gets access to the three console platforms: who can apply, what they ask for, what happens after approval, and how dev kits are obtained. It also covers engine support (Unity, Unreal, Godot) and porting companies. Everything behind the agreements (SDK, kit specifications, requirements documents) is under NDA and is not covered. Confidence labels: "verified" means read on an official page in Oct 2026; "reported" means secondary source; "unverified" means not confirmed.

## Contents
1. Common pattern across platforms
2. Nintendo Developer Portal
3. ID@Xbox
4. PlayStation Partners
5. Dev kit access
6. Pitch pack: what to prepare for any programme
7. Engine support
8. Porting companies and middleware
9. Publishers
10. Application checklist and human gates
11. Typical timeline for a first title
12. Questions to ask each platform after approval

## 1. Common pattern across platforms
1. Register an account (legal age, identity, company or individual).
2. Apply for platform access with a plan or concept (what the game is, the engine, the team, the release plan).
3. Sign agreements (NDA, then licensing and publishing agreements).
4. Receive documentation, SDK and tools, and obtain dev kits (purchase or loan).
5. Develop, rate, submit for certification, schedule the release.
Each step is a human action; each can take weeks.

## 2. Nintendo Developer Portal
Sources: https://developer.nintendo.com/register and https://developer.nintendo.com/faq (verified).
- Who: individuals and companies; you must be of legal age in your country (minors cannot register). No prior development experience is required. Home offices are accepted; you do not need a business address.
- Cost: registration and downloading tools are free; development hardware is the main cost (details inside the portal). Digital-only titles can get an IARC age rating at no fee (FAQ).
- Accounts: Company (the registrant becomes administrator and can add users) or Individual (cannot add users). Do not register the same organisation twice; if your company already has an account, ask your administrator to add you.
- Information asked: organisation details and the administrator's personal information. For Switch, a Switch Access Request form asks about your development experience and the planned project.
- Process after registering: for Nintendo Switch, apply for access through the Switch Access Request form (Getting Started section). Switch 2 development information is on a separate page linked from the registration page. New titles and patches can no longer be released for Nintendo 3DS and Wii U (portal notice).
- Publishing model (FAQ): you set the price, release date and content for your eShop title; digital and physical releases are supported.
- Technical: the portal is tested on current Chrome and Firefox on Windows.
- Not public: SDK, hardware specifications, certification, revenue share terms.

## 3. ID@Xbox
Source: https://learn.microsoft.com/en-us/gaming/game-publishing/onboarding/onboarding-join-id-at-xbox (verified, page dated 2026).
1. Register as an Xbox partner and sign the NDA; accept the App Developer Agreement; enrol in Partner Center (see `pc-web-release/references/other-pc-stores.md` for Partner Center accounts).
2. Requirements reported by Microsoft's FAQ: at least 18 (or a parent or guardian starts the relationship), a signed NDA, a country where Microsoft can do business. No cost to join (reported).
3. In the Xbox Partner Dashboard choose Apply to ID@Xbox: contact details, a shipping address for kit hardware, a registered business number, developer and/or publisher role, studio presence (website, public game trailers).
4. Submit a game concept (up to 10 reviewed at once): developer and publisher, key features and description, target release date, platforms, markets and pricing, Xbox network functionality and user-generated content, supplementary videos. Decision typically in 10 to 15 business days, up to 3 weeks. Outcomes: approved, more information needed, or rejected (you can submit another concept).
5. If approved, sign the Title Licensing Agreement and the GDK License Agreement. You then join the programme: full Xbox development and publishing features, onboarding for kit hardware and royalty payouts.
6. After joining you can pitch for strategic funding, including Game Pass and the Developer Acceleration Programme (a separate track for underrepresented creators; 2023 article, verify current status).
7. Scope: Xbox consoles and Xbox on PC. Microsoft's program selection page describes ID@Xbox for developers with a registered business; there are other programme routes (check https://developer.microsoft.com/en-US/games/publish/program-selection).
8. Public Xbox certification and rating requirement pages exist at https://devdocs.xbox.com (some pages are public; some are gated).

## 4. PlayStation Partners
Source: https://partners.playstation.net (page content not retrievable in this session). The following is from Sony's public indie guidance as reported by secondary articles (reported; verify):
1. Register at the PlayStation Partners site.
2. Submit a project plan, described by Sony as an elevator pitch: art style, target timing, platform plans, perhaps one or two key features.
3. Sony recommends a working build or prototype as the strongest pitch; earlier projects can send footage or concept art; answer business questions (other platforms, marketing timeline, business model, post-launch plans).
4. Approved partners sign the Global Developer and Publisher Agreement before getting backend tools. Approval does not guarantee Sony will publish or support the game.
5. Time: one executive was reported to say one to two weeks to onboard; another source says four to eight weeks (unreliable). Plan for a month.
6. Dev kits: reported that kits can be loaned to those who qualify; official eligibility is not public.
7. Engines: Unity requires PlayStation approval for its PlayStation build modules (Unity's console page, via search).

## 5. Dev kit access
1. Kits are provided after approval and agreements. Sources and prices are under NDA or vary; public figures are unreliable.
2. Ways to get kit time without owning one: a porting partner uses its own kits; a publisher may lend; some programmes have loan or lease options (reported, verify).
3. Plan shipping, customs and power adapters; kits are sometimes restricted by country.
4. Test kits are for development only; retail devices run only certified builds unless a dev-mode feature exists (for example Xbox has a retail dev mode feature reported in its docs; verify).
5. Security: kits and builds are confidential; store builds on access-controlled storage, not in public repositories or public CI logs.

## 6. Pitch pack: what to prepare for any programme
| Item | Content |
|---|---|
| One-page pitch | Hook, genre, platforms, team, release plan (2 to 3 sentences each) |
| Trailer | 60 to 90 seconds of real gameplay |
| Playable build | Windows build and a short video walkthrough; a controller-tested build is a strong signal |
| Store proof | Steam page link, wishlist count, reviews, press (if any) |
| Team | Names, roles, shipped titles |
| Technical | Engine and version, middleware, online features, controller support, performance profile |
| Business | Target price, release window, platforms, localisation, marketing plan |
| Readiness audit | The table in `SKILL.md` section E filled in |
Keep the pack accurate; overclaiming gets caught at certification.

## 7. Engine support
| Engine | Console support | Notes |
|---|---|---|
| Unity | Console build modules via the platform holders; apply for developer status and get approval from each platform holder; Unity Pro or a platform-holder licence key reported as required for closed platforms | Sony and Nintendo reportedly provide keys; Xbox reportedly does not: verify on Unity's console page |
| Unreal | Console support is built in; you obtain platform SDKs and source access from each platform holder after registration | Unverified here: check Epic's documentation for the current process |
| Godot | No official console export templates: docs cite legal liability, cost and open source licensing; third-party porting companies and middleware | https://docs.godotengine.org/en/4.5/tutorials/platform/consoles.html |
| GameMaker, Construct, others | Vendor programmes exist for some | Check the vendor |
| Custom engine or C++ | Direct SDK use after approval | Highest effort |

## 8. Porting companies and middleware
Godot's console page lists these (verified Oct 2026; list changes, recheck):
- Porting services (third parties port your game, some also publish): Lone Wolf Technology (Switch and PlayStation 4), Pineapple Works (Switch 1 and 2, Xbox One, Xbox Series, PlayStation 5; GDScript and C#), RAWRLAB games (Switch), mazette! games (Switch, Xbox One, Xbox Series, publishing), Olde Skuull (Switch, Xbox One, PlayStation 4 and 5, publishing), Tuanisapps (Switch, publishing), Seaven Studio (Switch, Xbox, PlayStation porting), Sickhead Games (Switch, PlayStation, Xbox).
- Middleware: W4 Games supplies official middleware ports of Godot for Nintendo Switch, Xbox Series X/S and PlayStation 5; you still adapt the game yourself, which is less work than porting the engine. Older reports described a product called W4 Consoles; confirm current names and availability on w4games.com.
How to choose a partner:
1. Ask for shipped titles on the target platform, engine version, and references you can contact.
2. Compare quotes on: scope (engine port only, or full port plus certification), fixed fee or revenue share, who owns the console build, who publishes, who pays for kits and certification fees, patch support after launch.
3. Check exclusivity and exit terms; a human or lawyer reads the contract.
4. Start with a paid evaluation or milestone-based plan.

## 9. Publishers
1. A publisher can fund the port, handle access and certification, and market the game, in exchange for a revenue share and sometimes rights.
2. Pitch with the pitch pack in section 6; expect questions on audience, comparable titles and sales.
3. Read for: recoupment order, territory and platform rights, marketing commitments, exit and reversion clauses, who holds the developer account on each platform.
4. Do not accept an exclusive deal on all platforms without a milestone and reversion clause.

## 10. Application checklist and human gates
1. Decide the route and platforms (`SKILL.md` section B).
2. Prepare the pitch pack and readiness audit (agent).
3. Human registers each account, enters identity and tax data, and submits applications.
4. Human reads and signs every agreement.
5. Agent records dates, contacts and decisions in `.gamestudio/reports/console-<platform>-<date>.md` (no NDA content).
6. After approval, replan with the platform's real documents.

## 11. Typical timeline for a first title (estimates)
| Week | Step | Owner |
|---|---|---|
| 0 | Decide route; start pitch pack | Producer and agent |
| 1 to 2 | Register accounts; submit applications | Human |
| 2 to 8 | Approval and agreements (Xbox concept 10 to 15 business days; others vary) | Platform holders |
| 6 to 10 | Kit order and delivery, or partner kit access | Human and partner |
| 8 to 24 | Port and platform features | Team or partner |
| 20 to 28 | Ratings and internal certification checks | Human and QA |
| 24 to 34 | Certification rounds (allow at least two) | Platform holders |
| 30 to 36 | Store page, pricing, release date | Human |
These are planning estimates from public indie guidance; real schedules come from the platform documents and partner quotes.

## 12. Questions to ask each platform after approval
1. Which game engine versions and middleware are supported or approved?
2. What are the memory, storage and save-size limits for our target mode (docked, handheld, base and enhanced consoles)?
3. What does certification test, how many rounds are included, and what do re-submissions cost in time?
4. What are the ratings requirements for our regions and for physical editions?
5. What account, trophy or achievement, and online features are mandatory?
6. What is the revenue share, payout schedule and tax process?
7. How do patches, DLC and demos work, and how long does a patch take to approve?
8. What marketing tools (store features, wishlists, pre-order, demos) are available?
Write the answers into the porting plan (`porting-plan.md`), without copying NDA text into public files.
