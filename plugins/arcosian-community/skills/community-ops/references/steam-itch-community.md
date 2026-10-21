# Steam and itch.io Community

Store community pages are where wishlists, reviews and long-term player relationships are built. This file covers the Steam community hub, events and announcements, store page updates, Steam Next Fest, replying to reviews and wishlists, then itch.io devlogs and community, and tone and cadence. All posts and uploads are human-approved: Claude drafts, a person publishes. Steam facts come from Steamworks documentation read in Oct 2026; itch.io's docs refused automated fetches, so itch.io details are marked "verify".

## Contents
1. Principles
2. Steam community hub
3. Events and announcements
4. Store page updates
5. Steam Next Fest
6. Wishlists
7. Replying to reviews
8. Review bombing
9. itch.io devlogs and community
10. Tone and cadence
11. Posting rules
12. Checklist

## 1. Principles

1. The store page is the main marketing asset. Keep it accurate, current and honest. See `store-release` for assets and metadata and `marketing-ua` for the funnel.
2. Players read the newest post and the latest reviews. Both age.
3. Respond to patterns, not to individuals.
4. Every public post goes through a person. Drafts live in `.gamestudio/community/drafts/`.
5. Platform differences: Steam serves PC (and Steam Deck); itch.io serves PC, web and jam games; mobile and console have their own store tools (see `store-release` and `console-pathway`).

## 2. Steam community hub

Each game has a community hub with discussions, announcements, screenshots, guides and reviews. In Steamworks you can set the hub's visibility and appoint moderators (verify current options in Steamworks).

Setup:
1. Seed the discussion forum with a few pinned topics: "Read first" (links to Discord, bug report path), "Known issues" (updated each patch), and "Bug reports".
2. Add team members as developers/moderators with the least access they need.
3. Decide whether to run the hub and Discord both. Two places halve the density. Choose one as the primary for bug reports and link from the other.
4. Check the hub weekly. Do not argue in threads.
5. Reports that matter go to GitHub as issues with `source:steam`.

## 3. Events and announcements

Steam's Events and Announcements tool (Steamworks doc) is the way to post news. From the Steamworks index, the event types are Major Update and Small Update or Patch Notes, there is an HTML import, event graphics, a review step, visibility settings and visibility statistics (verify details on the sub-pages: limits, lead times and what the review step checks).

Procedure for a patch announcement:
1. Draft from the GitHub Release notes: version, what changed for players, known issues, thanks.
2. Choose the type: Small Update/Patch Notes for fixes; Major Update for content.
3. Prepare graphics at the required sizes (read the Event Graphical Assets page; do not guess sizes).
4. Localise key posts if a language is above about 10 percent of your players.
5. Human reviews text and images, schedules or publishes, and records it in `posted.md`.
6. Watch the visibility statistics afterwards and note what worked.

Writing rules: lead with the benefit, put the patch notes below, avoid marketing language in patch notes, do not post unverified claims (such as performance numbers you have not measured).

## 4. Store page updates

Changes to the store page (description, capsules, screenshots, trailers, tags) are reviewed by Valve for major changes in some cases (verify).
1. Keep screenshots and trailers matching the current build.
2. Update the short description and tags when the game's focus changes.
3. Add the demo and its release notes.
4. A/B-type changes: change one thing, watch wishlists and visits for two weeks, record the result. Estimates only; traffic is noisy.
5. Check age ratings and content descriptions match the build (see `legal-ethics` and `compliance-officer`).
6. Uploads and releases to Steam are human-approved. The core hooks ask before `steamcmd ... +run_app_build`.

## 5. Steam Next Fest

From Steamworks (Oct 2026): a multi-day event held several times a year in which players try demos; a game must be unreleased and have a playable demo. Dates listed: October 19 to 26, 2026; February 22 to March 1, 2027; June 14 to 21, 2027. Each event has its own registration page and deadlines (read them; do not assume).

Plan (work back from the start date):
| When | Task |
|---|---|
| 12 weeks before | Decide whether the demo will be ready. If not, skip the event. |
| 8 weeks | Register. Demo submitted to Valve's review path early. |
| 6 weeks | Wishlist call to action in every post. Store page polished. |
| 4 weeks | Demo feature-complete; crash reporting in the demo build. |
| 2 weeks | Demo locked; devlog and Discord announcements drafted. |
| Event | Daily check of crashes and feedback; livestream or developer chat if staffed. |
| After | "What we learned" post; follow up with demo players. |

Demo rules: the first 15 to 30 minutes carry the whole demo; it must end with a wishlist prompt; test fresh installs on the Steam Deck if you claim support. A demo with a bad crash rate costs wishlists: put Sentry in it and watch it live.

## 6. Wishlists

1. Wishlists are the main pre-launch signal, but conversion depends on genre and quality; ratios differ widely. Do not quote a benchmark you cannot source.
2. Track weekly: new wishlists, deletions, visits, and where they came from (Steamworks wishlist reports).
3. Every post and trailer ends with one link to the store page.
4. Use wishlist counts as a go/no-go input in `market-intel`, not as a promise of sales.

## 7. Replying to reviews

Steamworks documents that developers can write an "Official Developer Response" from a review's detail view, and can comment on reviews; the response is marked as from the developer. Replies are not required, and Valve advises against arguing or disputing opinions.

Rules:
1. Reply to reviews that report a bug you fixed or a misunderstanding you can clear in one or two sentences.
2. Never reply to insults, never use sarcasm, never ask for a changed review as a condition of help.
3. Draft replies in `drafts/review-replies.md`: `review link | summary | draft reply | status`. A person approves each.
4. Use a studio account name that does not make one person a target.
5. When a fix ships, replying once to the oldest relevant reviews is fine. Do not bulk-reply.
6. Developers cannot delete reviews; abusive or off-topic reviews can be flagged for moderators.
7. Reviews are public statements by players. Do not copy a review text into marketing without the guidance of `legal-ethics`.

## 8. Review bombing

From Steamworks guidance: a review bomb is a surge of reviews meant to lower the score. Procedure:
1. Find the cause. If your update caused it, fix it first.
2. If the surge is off-topic or unrelated to the product, contact Valve through Partner Support so the abnormal period can be assessed (they may remove it from the score).
3. Do not argue publicly. Flag abuse using the moderator controls.
4. Say one calm sentence in an announcement if the cause is real and fixed.
5. Note: store pages show a 30-day score and an all-time score; a score below 40 percent ("Mostly Negative") makes featuring less likely (Steamworks docs).

## 9. itch.io devlogs and community

Verify details on itch.io's creator docs (they refused automated fetches).
1. Devlogs are posts on the game's page that notify followers. They suit jams, prototypes and small games.
2. Each game page has a comment section and, if enabled, a community tab (forum-style topics). Choose one place for bug reports and say so on the page.
3. Update the page description when versions change; the files section lists builds per platform (web, Windows, macOS, Linux, Android).
4. Restricted or password-protected builds can serve playtests; never post the password publicly.
5. Pushing builds with `butler` is a store upload: the core hooks ask before `butler push`; a person approves.
6. Follow itch.io's content rules and the platform's terms on payments, AI-generated content disclosure and age (verify current wording).
7. A devlog is a good place to explain a pivot, share a timelapse, or ask for specific feedback.
8. Jams: read the jam rules (scope, asset rules, voting period), tag the entry properly, and plan a post-jam update.

## 10. Tone and cadence

| Rule | Why |
|---|---|
| Plain words, short sentences | Players skim. |
| Say what you did, not how great it is | Trust. |
| Admit problems early, with a plan | Reviews follow honesty. |
| One call to action per post | Clarity. |
| Same voice everywhere | One person edits all posts. |
| No dates you cannot keep | Missed dates cost more than slow ones. |
| Credit people with their permission | Respect. |

Cadence by stage is in `discord-and-devlogs.md` section 10. Steam announcements: for each public build and for events; avoid more than one a week outside launch unless there is real news. itch.io devlogs: for each meaningful version.

## 11. Posting rules

1. Claude drafts. A person approves in chat with the word "approved" and the file name.
2. Claude does not log in to Steamworks, itch.io, Discord or social media, and does not use browser automation on them.
3. Drafts carry a header: `status: draft | approved | posted`, `approved by`, `date`.
4. Do not post text that includes private data, tester names, unreleased content under embargo or unlicensed material.
5. Do not edit a posted announcement silently; add a note if you correct it.
6. Check every link and every number before approval.

## 12. Checklist

- [ ] Hub seeded with pinned topics; primary bug-report place chosen
- [ ] Store page matches the current build
- [ ] Event dates checked on the Steamworks event page
- [ ] Review-reply drafts approved one by one
- [ ] Wishlist and visit numbers recorded weekly
- [ ] Every post has a draft file, an approval and an entry in `posted.md`
