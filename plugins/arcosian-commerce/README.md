# arcosian-commerce

Adapter plugin for the `arcosian` core plugin. It connects Claude to monetization and operations services: products and entitlements (RevenueCat), remote config and crash data (Firebase), attribution (Adjust), and store metadata and builds (community App Store Connect and Google Play MCPs).

Requires the core plugin `arcosian` (declared as a dependency).

## What you get

- Skill `commerce-mcps`: which service owns which job, procedures, and the approval rules.
- `.mcp.json` with three servers:

| Server | Transport | Auth | Status |
|---|---|---|---|
| `revenuecat` | remote http, `https://mcp.revenuecat.ai/mcp` | OAuth (an API v2 bearer key is also documented) | Official, hosted |
| `firebase` | stdio, `npx -y firebase-tools@15.34.0 mcp` (pinned) | Firebase CLI login or Application Default Credentials | Official, local |
| `adjust` | remote http (streamable), `https://mcp.adjust.com/mcpo` | Sign in to Adjust through `/mcp` | Official; URL confirmed in Adjust's help centre (Oct 2026): https://help.adjust.com/en/article/adjust-mcp. Aggregated data only (no user- or event-level data) |

Neither stores a secret in plugin config. For Firebase run `firebase login` first; for RevenueCat authorize through `/mcp`. Use `--only <groups>` on the Firebase command in a project-level config to limit exposed tool groups.

## Documented, not registered (community servers)

These stay out of `.mcp.json` on purpose: they are community-maintained and hold store credentials. A community `mcp-adjust` also exists; prefer the official `adjust` server above.

- **App Store Connect MCPs (community only, no Apple-official server found)**: examples named in the notes are forgeopslabs/appstore-mcp, zelentsov-dev/asc-mcp and TrialAndErrorAI/appstore-connect-mcp.
- **Google Play MCPs (community only)**: examples are appeeky/google-play-store-cli, petropentsak/play-store-mcp, AgiMaulana/GooglePlayConsoleMcp.

Risks of community store MCPs:

1. They hold an App Store Connect Team API key (.p8, issuer, key id) or a Play service account JSON. Anyone who controls the server controls your store listing.
2. Some expose hundreds of tools including pricing, submission and deletion.
3. Maintenance is thin (small star counts, one maintainer). Pin the version and read the source.
4. Prefer fastlane in CI for builds and uploads; use an MCP for read access first (analytics, build status), with a least-privilege key.

## What this plugin runs, sends and fetches

- **Sends:** requests to RevenueCat, Firebase (Google) and Adjust when Claude uses their tools, under your own sign-in.
- **Runs:** the Firebase MCP server locally; RevenueCat and Adjust are remote servers run by those companies.
- **Fetches:** `firebase-tools@15.34.0` from npm on first start (exact version).
- **Never automatic:** store submission, production releases, price changes and availability changes need your approval in chat, as below.

## Security and approval rules (enforced by the skill and the core hooks)

Claude never submits an app for review, releases to production, changes a price, or alters availability without explicit human approval in chat, stated per action. Read operations and TestFlight or internal-track uploads are the default scope.

## Typical flows

1. Monetization design hands a product table to this adapter; Claude creates products, entitlements and offerings in RevenueCat as drafts and lists what changed.
2. Live-ops proposes a remote-config change; Claude prepares the Firebase template diff and waits for approval before publishing.
3. The release manager checks build and TestFlight state read-only, then asks the human before any review submission.

## Volatile facts (as of Oct 2026 - verify)

- RevenueCat MCP URL and capabilities. Source: https://www.revenuecat.com/docs/tools/mcp
- Firebase MCP launch command and tool groups. Source: https://firebase.google.com/docs/ai-assistance/mcp-server
- Adjust MCP. Source: https://www.adjust.com/blog/adjust-mcp/
- Store requirements (target API, billing library, SDK manifests) change yearly. Source: https://developer.apple.com/news/upcoming-requirements/ and https://developer.android.com/google/play/requirements/target-sdk

## License

MIT.
