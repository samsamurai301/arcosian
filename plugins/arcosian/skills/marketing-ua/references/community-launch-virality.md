# Community, Launch and Virality

This file covers the organic side of mobile game marketing: building a community before and after launch, working with influencers and creators, PR, pre-registration, choosing launch timing, and virality mechanics including K-factor, referrals and user-generated content. It gives procedures, timelines, formulas and checklists. Read it when you plan a launch, decide how to spend a small marketing budget, or design sharing and referral features.

## Table of contents
1. Principles
2. Community building
3. Community channels and cadence
4. Community health and moderation
5. Influencers and creators
6. PR and press
7. Pre-registration and wishlists
8. Launch timing
9. Launch timeline
10. Virality and K-factor
11. Referral design
12. User-generated content
13. Store featuring
14. Measurement
15. Worked example: small-team launch plan
16. Anti-patterns
17. Volatile facts (as of Oct 2026 - verify)

## 1. Principles
- Organic growth compounds only if the product retains players; community amplifies a good core loop and cannot rescue a leaky one.
- Build an audience before you need it: months before launch, not weeks.
- Be specific about who the game is for; niches are easier to reach than "everyone".
- Honesty builds long-term trust; overpromising kills it.
- Every marketing activity needs a tracked outcome (sign-ups, wishlists, installs, retained players).

## 2. Community building
Steps:
1. Define the audience and the promise in one sentence (genre, fantasy, differentiator).
2. Choose one or two primary channels where that audience already gathers; do not spread thin.
3. Share the development openly: short clips, devlogs, polls, behind-the-scenes. Show the hook early.
4. Create a home base: a Discord or similar community space, plus a landing page with a sign-up for updates.
5. Give early members roles: playtesters, feedback voices, ambassadors.
6. Close the loop: show what changed because of their feedback.
7. Convert: beta sign-ups, pre-registration, wishlists, newsletter.
Rules: be consistent in cadence over intensity; respond to people; keep a clear tone of voice.

## 3. Community channels and cadence
| Channel | Use | Cadence idea |
|---|---|---|
| Discord or similar chat | Core community, feedback, support | Daily presence, weekly event or Q and A |
| Short-video platforms | Discovery via clips | Several clips per week when possible |
| Video platform | Devlogs, trailers | Monthly or per milestone |
| Forums and subreddits | Genre enthusiasts | Participate genuinely; follow rules against self-promotion |
| Newsletter | Owned audience | Monthly or milestone |
| Social posts | Announcements | Regular, brief |
Post-launch: patch notes, roadmap posts, events announcements, community spotlight, seasonal recaps.
Keep a content calendar aligned with the live-ops calendar (`liveops`).

## 4. Community health and moderation
- Written rules and a code of conduct; consistent enforcement; trained moderators.
- Escalation for harassment, hate and threats; protect minors; do not collect children's data in community tools.
- Transparency about known issues and decisions; admit mistakes quickly.
- Feedback triage: tag, count, summarize weekly; feed design and live-ops reviews.
- Avoid dependence on a single platform; keep an owned list (email) where legal.
- Toxicity in the community drives away new players; moderation is a growth activity.

## 5. Influencers and creators
Selection:
- Fit over size: audience overlap with your target, content style that suits your game, authentic engagement.
- Check audience geography and age; for family or youth-adjacent content follow advertising rules for minors.
- Review past sponsored content for honesty.
Deal structures: flat fee, fee plus performance bonus, affiliate codes or links, product-for-content (for small creators), revenue share in some cases.
Process:
1. Brief: what the game is, key moments to show, mandatory disclosures, no scripts that misrepresent gameplay.
2. Give builds or access early with a support contact.
3. Unique tracking links or codes per creator for attribution.
4. Disclosure: creators must disclose sponsorship per local advertising rules; require it in contracts.
5. Measure: views, clicks, installs, cohort quality; compute cost per retained player.
6. Relationship: favor repeat collaborations with those who perform.
Small budget approach: many micro-creators in your niche can outperform a few large ones on cost per retained player, but measure it.
Do not buy fake engagement or fake reviews.

## 6. PR and press
- Know what is newsworthy: a distinctive hook, a milestone, data, a notable collaboration, a human story.
- Build a press kit: short description, logo and key art, screenshots, trailer, gameplay clips, fact sheet, contact, store links, embargo info.
- Target outlets by genre and region; personalize pitches; keep them short.
- Timing: pitch ahead of launch with embargoes; follow up once.
- Mobile-specific outlets and creators matter; do not rely only on general press.
- Use reviews responsibly: offer access to reviewers; never pay for positive coverage without disclosure.
- Monitor coverage and respond; reuse quotes on store pages (with permission).
- A small studio can run PR in-house with a clean list of relevant contacts.

## 7. Pre-registration and wishlists
- Both major stores offer pre-registration or pre-order style features for upcoming apps (verify current capabilities and rules in each store's developer documentation); users are notified at launch.
- Value: a day-one install burst helps ranking and gives early reviews; it also measures interest.
- Set up: store page assets must be ready; use the page as a marketing destination in ads and community posts.
- Measure: pre-registrations per source; conversion from pre-registration to install on launch day.
- Do not run pre-registration without a firm launch window; stale pages lose trust.
- Combine with a landing page and email list for platform independence.

## 8. Launch timing
Considerations:
- Product readiness and gates from soft launch come first; never launch on a date for its own sake.
- Competitive calendar: avoid launching against major titles in your genre when possible; check announcements.
- Seasonality: holidays and school breaks change attention and cost; weigh available time against competition for attention and higher ad prices.
- Day of week: store featuring and press have patterns; verify with your own region data.
- Team readiness: support, incident response, content pipeline, and stable servers.
- Store review lead times: submit early, with buffer (`store-release`).
- Staged geographic launch: start where performance is strongest, then expand; or launch globally if infrastructure is ready and marketing can support it.
- Avoid launching right before a holiday freeze unless the team will be on call.
Decision: choose the earliest window where the product, team and calendar are all ready; slip rather than ship a leaky launch.

## 9. Launch timeline
| When | Activities |
|---|---|
| Several months out | Community start, landing page, devlogs, closed beta, soft launch learning |
| Two to three months | Press kit, creator outreach, store page assets, localization |
| One month | Pre-registration live, trailer, influencer briefs, UA creatives tested |
| Launch week | UA ramp, creator content goes live, press embargo lifts, community events, store featuring request, launch event in game |
| First weeks | Daily monitoring, rapid fixes, patch notes, community engagement, first live event, ratings prompts |
| Month two onward | Content cadence, season one, retention focus, creative refresh |
Make a day-by-day plan for launch week with owners.

## 10. Virality and K-factor
Formulas:
- `K = i x c` where i is average invites sent per user and c is conversion rate of invites to new users.
- Cycle time matters: shorter viral cycles compound faster.
- Total users from a seed cohort N: `N x (1 + K + K^2 + ...)`; if K < 1, the sum is `N / (1 - K)`; if K >= 1 growth is self-sustaining (rare for games).
- Viral coefficient is usually below 1 for games; the practical value is lowering effective CPI: `blended CPI = paid spend / (paid installs x (1/(1-K)))` approximately, for K below 1.
Worked example: if K is 0.2, each paid install yields about 1.25 total installs; a CPI of 2.00 becomes about 1.60 effective. Measure K from data, not assumptions.
Levers: social features where multiplayer or co-op needs friends, shareable moments (wins, creations, replays), gifting, leaderboards among friends, team events, invitations with mutual benefit.
Negative virality: spammy invites, forced sharing, permissions abuse hurt retention and store standing; do not gate core progress on invites.

## 11. Referral design
- Give a reward to both sides, modest and non-power (cosmetic or convenience); cap per user.
- Make the invite link frictionless: deep link with attribution through the MMP and deferred deep links so the invitee lands on the right screen.
- Detect abuse: self-referrals, emulator farms; require the invitee to reach a milestone before rewards are paid.
- Track funnel: invites sent, link clicks, installs, milestone reached, rewards paid, retention of invitees.
- Ethics: no contact scraping without consent; follow privacy laws; no referral features for minors without parental considerations.
- Test: A/B reward sizes and prompts; watch for opt-outs and complaints.

## 12. User-generated content
- UGC includes screenshots, replays, creations (levels, skins), fan art, streams.
- Make sharing easy: native share sheet, watermark with store link, clip recording on key moments.
- Provide creators with tools: level editors, photo modes, creator codes.
- Moderation: automated filters plus reporting; legal review of IP and content policies; age-appropriate controls.
- Reward creators: showcases, in-game credits, featured content; avoid exploiting free labor without recognition.
- Rights: terms must grant the license needed to feature content; respect creators' rights.
- UGC fuels organic discovery and keeps content fresh at lower cost; it needs moderation capacity.

## 13. Store featuring
- Stores curate editorial features; criteria include quality, platform technology adoption, polish, accessibility and localization.
- Prepare: complete store assets, a story pitch, release notes of what is new, support for current platform features.
- Submit through the stores' official channels and contacts where available (verify current processes in the developer documentation).
- Do not count on featuring; it is a bonus.
- Prepare a launch event timed with potential features.

## 14. Measurement
- Funnel: community size, newsletter sign-ups, pre-registrations, wishlist counts, conversion at launch.
- Source tracking: unique links per creator or channel; promo codes; MMP attribution with campaign tags.
- Organic share of installs; branded search lift.
- Quality: D1/D7 by source.
- Sentiment: store ratings, review themes, community mood.
- Cost per retained player by source: including staff time where you can estimate.
- Review monthly and reallocate effort.

## 15. Worked example: small-team launch plan
Team of three, modest budget, puzzle game.
1. Month minus four: landing page with sign-up; weekly short clips of satisfying puzzle moments; small Discord for playtesters.
2. Month minus three: soft launch learnings; fix retention; refine hook clips into ad creatives.
3. Month minus two: outreach to a few dozen micro-creators in puzzle niche with free early access; press kit; localized store page.
4. Month minus one: pre-registration; creator content scheduled; creative tests in small paid campaigns to verify CPI and D1.
5. Launch week: coordinated creator posts, press embargo lift, launch event in game, community AMA, UA ramp in step increments.
6. Weeks 2 to 6: weekly patch notes, season one, ratings prompt after positive moments, review and respond to feedback.
Decision points: if pre-registration is far below plan, delay or boost the community effort; if D1 from creator traffic is poor, adjust briefs and creator selection.

## 16. Anti-patterns
| Anti-pattern | Detect | Fix |
|---|---|---|
| Launch to silence | No audience, flat page views | Start community early |
| Spamming communities | Bans, hostile replies | Participate genuinely, follow rules |
| Paying for fake reviews or followers | Spiky reviews, policy warnings | Never; earn them |
| Influencer scripts that misrepresent | Complaints, low retention | Honest briefs, real gameplay |
| No tracking of creator deals | Cannot attribute | Unique links and codes |
| Forced sharing for progress | Review complaints | Optional, rewarded sharing |
| Ignoring moderation | Toxic community | Rules, moderators, tools |
| Launching on a date regardless of readiness | Poor reviews, churn | Gate on readiness |

## 17. Volatile facts (as of Oct 2026 - verify)
- Store pre-registration features, editorial featuring processes and rules change; verify in current developer documentation: https://developer.apple.com/app-store/ and https://developer.android.com/distribute
- Android developer verification affects off-Play distribution and web/APK campaigns in some countries from Sep 30, 2026: https://www.androidauthority.com/p-3679204/
- Influencer disclosure rules differ by country and change; confirm with counsel (see `legal-ethics`).
- Platform privacy rules and consent regimes affect referral and contact features; see https://gdpr-info.eu/art-8-gdpr/ for the child-consent age baseline.

## 18. Launch-week checklist
- [ ] Store page final: icon, screenshots, video, localized text, age rating, privacy labels.
- [ ] Pre-registration notifications confirmed to fire at release.
- [ ] Tracking links and codes live for every creator and channel.
- [ ] MMP, analytics and consent flows verified in the release build.
- [ ] Support inbox, macros and on-call rota active; status channel ready.
- [ ] Press embargo time agreed; announcement posts scheduled with local-time variants.
- [ ] Launch event and welcome track enabled in remote config, with kill switch.
- [ ] Community moderators staffed across time zones.
- [ ] Daily review slots booked for the first week; owner for each metric.
- [ ] Rollback and hotfix lane confirmed with `release-manager`.

## 19. Community roles and workload
| Role | Responsibility | Time guide for a small team |
|---|---|---|
| Community lead | Voice, calendar, feedback triage | A fixed daily slot, more at launch |
| Moderators | Rules, reports, welcome new members | Volunteer plus a lead on escalation |
| Ambassadors | Early players who help others | Light touch, recognition rewards |
| Developers | Show work, answer questions | A short weekly session |
| Support | Account and purchase issues | Separate from community chat |
Keep support requests out of public channels where personal data could leak; route them to a ticket form.
