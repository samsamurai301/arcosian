# Discord and Devlogs

Discord is where most indie communities live; devlogs are where the team's progress is told in public. This file covers how to structure a server, roles and onboarding, moderation and safety, feedback and bug-report channels, playtest sign-ups, webhooks for devlogs and build notes, and what never to automate. Every post is human-approved. Discord's own help pages refused automated fetches while this was written, so Discord product details are marked "verify".

## Contents
1. Is there an official Discord MCP server?
2. Server structure
3. Roles
4. Onboarding
5. Moderation and safety
6. Feedback and bug-report channels
7. Playtest sign-ups
8. Webhooks for devlogs and build notes
9. Devlog writing
10. Cadence
11. What not to automate
12. Checklist

## 1. Is there an official Discord MCP server?

A web search in Oct 2026 found only third-party Discord MCP servers (community projects, some stating they are not affiliated with Discord, one that logs in as a user account and warns about Discord's terms). I found no server published by Discord itself. This plugin therefore registers none and does not add a community one. Reasons: a bot token can read and write a whole server; unofficial servers are unvetted; user-account automation can break Discord's terms.

If Discord publishes one later, add it after checking the publisher, URL and scopes against Discord's own developer docs.

What Claude can do instead: draft posts and replies to files, read exported feedback you paste in, and prepare webhook payloads for a person to review.

## 2. Server structure

Start small. Ten to fifteen channels is plenty before launch.

| Category | Channels | Notes |
|---|---|---|
| Start | `#welcome`, `#rules`, `#announcements` | Read-only for members. Announcements can be a followable announcement channel (verify feature name). |
| Game | `#devlogs`, `#general`, `#screenshots` | Devlogs read-only; discussion happens in `#general`. |
| Feedback | `#feedback` (forum), `#bug-reports` (forum), `#suggestions` | Forum channels give one thread per report. |
| Playtest | `#playtest-signup`, `#playtest-chat` | Private role-gated chat for active testers. |
| Support | `#help` | Players helping players, with a role that can mark answers. |
| Team | `#mod-log`, `#team` | Private. |

Rules of thumb:
1. One language per channel at first. Add language channels only when there is steady traffic.
2. Do not mirror every channel to every platform.
3. Archive dead channels instead of keeping empty ones.
4. Name channels for the job (`#bug-reports`), not the mood.

## 3. Roles

| Role | Who | Permissions in short |
|---|---|---|
| Owner/Admin | One or two team members | Everything. Few people, two-factor authentication on. |
| Moderator | Trusted volunteers and team | Timeout, delete messages, manage threads. No role management. |
| Developer | Team | Post in `#devlogs`. |
| Tester | Playtest participants | Access to `#playtest-chat`. |
| Supporter/Veteran | Long-time members | Cosmetic. |
| Bot | Integrations | Only the permissions it needs, in the channels it needs. |

Rules:
1. Never give a bot Administrator. Grant specific permissions per channel.
2. Review roles before every playtest.
3. Moderators are volunteers: write them a one-page guide and a list of who to escalate to.

## 4. Onboarding

Discord Community servers have onboarding and rules-screening features (verify current names and limits in Discord's help centre). Use them:
1. Rules screening: show rules, require acceptance.
2. Onboarding questions: pick interests (playtests, devlogs, bug reports) to assign roles or channels.
3. A pinned "start here" message: what the game is, where to report bugs, where to sign up to playtest, how often the team posts.
4. Keep the first screen under about 150 words.

## 5. Moderation and safety

1. Turn on AutoMod. It can block or flag keywords, spam and mention spam and can time users out (verify current rule types and limits). Start with: a slur and scam-link keyword list, mention-spam limit, and spam filter. Send alerts to `#mod-log`.
2. Verification level: require a verified email at minimum. Raise it temporarily during raids or after a launch spike.
3. Age rules: Discord's terms set a minimum age (13 in most places, higher in some; verify). Do not target children. If your game has a young audience, say what is allowed, avoid collecting personal data, and keep age-restricted content out. Follow platform rules for any 18+ channel.
4. Reporting: a visible way to report a person or message (a `#report` instruction or a modmail bot with a human reading it). Reports go to at least two moderators.
5. Written code of conduct: harassment, hate, doxxing, piracy links, cheating tools and leaks are bannable. Give a warn, timeout, ban ladder, and log each step.
6. Safety first: never post a player's name, face or message in a devlog or store page without permission.
7. Scams: players will get DMs pretending to be you. Pin a notice: "The team will never DM you first or ask for payment or passwords."
8. Leaks: set a rule about unreleased builds and keep tester builds under a non-disclosure line where you need one (a short written agreement for closed playtests).
9. Data: Discord messages are personal data. Do not export them into other tools without a reason, and delete exports when done.
10. Legal: see `legal-ethics` for privacy and children's data.

## 6. Feedback and bug-report channels

A forum channel with post guidelines and tags is the best fit (verify forum features: tags, required tags, post guidelines).

Bug-report template (pinned guideline text):
```
Game version:
Platform and device:
What happened:
What you expected:
Steps (numbered):
Frequency (always / sometimes / once):
Screenshot, video or log:
```

Tags: `new`, `confirmed`, `fixed in next build`, `cannot reproduce`, `duplicate`, `by design`.

Procedure (weekly, a human does the reading; Claude can help cluster text you paste):
1. Read new posts. Tag them.
2. For each confirmed bug, open a GitHub issue with `source:discord` and link both ways.
3. For feedback, group by theme and count unique players, not messages.
4. Reply to each report with one of: thanks and what happens next, a question, or "fixed in version X".
5. Close the loop when a fix ships: edit the thread tag and say so in the next devlog.

Forms: if you need structured sign-ups or surveys, use an external form (Google Forms, Typeform, itch.io) linked from the channel, with a privacy note. Do not collect emails in Discord messages.

## 7. Playtest sign-ups

1. Decide the size and goal first (see `playtest`): for example 30 testers to check the first 15 minutes.
2. Collect in a form: platform, device model, Discord handle, consent to being contacted, and age confirmation if you need it. Collect nothing you do not use.
3. Select testers to cover your device list, not first come first served.
4. Give testers the Tester role, a one-page guide (what to test, how to report, how to leave) and a deadline.
5. Distribute builds through the platform's tester system (TestFlight, Play internal testing, Steam keys, itch.io restricted access, or a private link). Never post a build link in a public channel.
6. After the test: thank testers, publish a "what we heard, what we changed" post, and remove the role.

## 8. Webhooks for devlogs and build notes

A webhook lets a script post into one channel without a bot. Facts from Discord's developer docs (Oct 2026): a message needs content, embeds, components, a file or a poll; `content` is at most 2000 characters; up to 10 embeds per message; the `allowed_mentions` field controls which mentions fire; `thread_id` posts into a thread, and forum channels need `thread_id` or `thread_name`. The webhook URL contains a secret token: anyone who has the URL can post. Treat it like a password.

Rules for this plugin's workflow:
1. Claude writes the post to a file, for example `.gamestudio/community/drafts/2026-10-21-devlog-0.9.2.md`, and a payload file next to it.
2. A person reads the draft, edits it and says "approved" in chat.
3. Only then does a person (or a script the person runs) send it. Claude does not send posts on its own.
4. The webhook URL lives in a secret store or CI secret, never in the repository, the draft or chat.
5. Always set `allowed_mentions` to an empty list so a draft cannot ping `@everyone`.
6. Strip user-generated text and links from anything that came from players or crash data.
7. Log what was posted, when and by whom, in `.gamestudio/community/posted.md`.

Build notes: a short post per build, written from the release notes: version, what changed for players (three to six bullets), known issues, where to report. Generated from the GitHub Release, reviewed by a person.

## 9. Devlog writing

Structure (300 to 600 words):
1. Headline that says what changed ("Combat now has a dodge").
2. One image or short clip.
3. What we did, in plain words.
4. What we learned or what went wrong (honest beats polished).
5. What is next, with a rough time frame marked as an estimate.
6. How to help (wishlist, playtest, feedback link).

Do not: promise dates you may miss, show unlicensed assets, include private tester names, or describe a bug as fixed before it is verified.

## 10. Cadence

| Stage | Devlog | Announcements | Moderation load |
|---|---|---|---|
| Prototype | Optional, one a month | None | Minimal |
| Playtest | One per test round | Test start and end | Daily glance |
| Early access | Every two to four weeks | Each patch | Daily |
| Launch | Daily for launch week | Launch, hotfixes | Several times a day |
| Live | Monthly or per update | Events and patches | Daily |

Regular and small beats rare and large. Missing a promised cadence costs more than choosing a slower one.

## 11. What not to automate

- Publishing any post, reply or announcement.
- Replying to individual players, especially complaints.
- Moderation decisions: bans and timeouts for anything beyond AutoMod rules a person set.
- DMs to players.
- Giving out keys or access.
- Anything using a player's own account or token.
- Reading private channels or DMs.
- Scraping the server.

What is fine to automate: drafting, summarising pasted feedback, clustering themes, filing issues with human approval, and posting to `#mod-log` internal notes.

## 12. Checklist

- [ ] Channel list and roles written down; no bot has Administrator
- [ ] AutoMod on, alerts to `#mod-log`, verification level set
- [ ] Rules, scam notice and report path pinned
- [ ] Bug-report forum with template and tags
- [ ] Playtest form collects only what is needed
- [ ] Webhook URL stored as a secret; `allowed_mentions` empty
- [ ] Every post approved by a person and logged
