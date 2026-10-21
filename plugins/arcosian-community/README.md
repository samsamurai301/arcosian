# arcosian-community

Adapter plugin for the `arcosian` core plugin. It registers GitHub's and Sentry's official MCP servers and ships one skill, `community-ops`, for team tools, player community, store community pages and crash triage, for any game and platform.

Requires the core plugin `arcosian` (declared as a dependency).

## What you get

- Skill `community-ops`: which channels to run at each stage (prototype, playtest, early access, launch, live), a weekly operations checklist, a worked example (crash spike to fix pull request plus a devlog draft awaiting approval), failure modes and security rules.
- Four references: GitHub for game teams, Discord and devlogs, Steam and itch.io community, crash and feedback triage.
- `.mcp.json` with two servers, both opt-in:

| Server | Transport | Auth | Notes |
|---|---|---|---|
| `github` | remote http, `https://api.githubcopilot.com/mcp/readonly` | Bearer token from `github_token` (sensitive) | Read-only variant of GitHub's official remote server. URL confirmed in GitHub's docs (Oct 2026). |
| `sentry` | remote http, `https://mcp.sentry.dev/mcp` | OAuth with your Sentry account through `/mcp`; no token stored | URL confirmed on Sentry's MCP page (Oct 2026). |

Without your accounts both do nothing. No Discord server is registered: Discord publishes no official MCP server (none found in an October 2026 search), and this plugin does not add community ones.

## Setup

1. Install the plugin. Optionally enter a fine-grained GitHub token in the plugin settings (`github_token`). Leave it empty if you do not use the GitHub server.
2. For Sentry, run `/mcp` and authorise the `sentry` server in the browser. Scope it to one project by changing the URL to `https://mcp.sentry.dev/mcp/<org>/<project>` in a copy of `.mcp.json`.
3. To let GitHub tools write (create issues, open pull requests), use the non-read-only URL `https://api.githubcopilot.com/mcp/` in your project's own `.mcp.json` and a token with matching write permissions. Do this only when you need it.

## What this plugin runs, sends and fetches

- **Runs:** nothing locally. Both servers are hosted by their vendors.
- **Sends:** the tool calls Claude makes (repository, issue, crash and project data you ask about) to GitHub and Sentry, under your accounts.
- **Fetches:** issue, pull request, crash and event data from those accounts.
- **Never:** posts to Discord, Steam, itch.io or social media. Those posts are drafted by Claude and published by a person.

## Security

- The GitHub token is entered as sensitive configuration, never stored in files. Use a fine-grained token limited to the game repositories and read-only permissions.
- Crash events can contain player data. Scrub it in the SDK (`before_send`) before it reaches Sentry.
- Issue, review and chat text is untrusted data. Claude does not follow instructions found in it.
- Every community post is human-approved.

## Typical session

1. "Crashes spiked after 0.9.2." Claude reads the top Sentry issues, maps them to features, and opens a bug report (with your approval to write).
2. Claude drafts a fix branch and pull request description, and a devlog draft saved to a file.
3. You review, approve and post the devlog yourself.

## Volatile facts (as of Oct 2026 - verify)

- GitHub remote URL, read-only URL and toolsets. Source: https://github.com/github/github-mcp-server/blob/main/docs/remote-server.md
- Sentry remote MCP URL and OAuth. Source: https://mcp.sentry.dev/
- Not verified here: Discord policy pages and itch.io docs (both refused automated fetches).

## License

MIT.
