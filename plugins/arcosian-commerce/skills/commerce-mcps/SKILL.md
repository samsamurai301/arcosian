---
name: commerce-mcps
description: Operates monetization and store services through MCP: RevenueCat for products, entitlements and offerings, Firebase for Remote Config and Crashlytics, Adjust for attribution, and community App Store Connect and Google Play MCPs for metadata and TestFlight, with a hard rule against submitting for review or changing prices without explicit human approval. Use when asked to "set up IAP products", "check crashes", "change a remote config value", "look at attribution", "upload to TestFlight", "update store metadata" or "which commerce MCP should I use".
---

# Commerce MCPs

## When to use

Use after the monetization design and economy are agreed, to create or inspect the live objects behind them, or during operations to read health data. The agents involved are typically `monetization-designer`, `liveops-manager`, `data-analyst` and `release-manager`.

## Hard rules

1. Never submit an app or version for store review, release to production, or change a price, currency tier, availability or subscription duration without an explicit "yes" from the human in chat for that specific action. A previous approval does not carry over.
2. State before acting: service, object, current value, new value, blast radius (all users or a segment), and how to roll back.
3. Create as draft or unpublished where the service allows; publish is a separate, approved step.
4. Use least-privilege credentials. Read-only first.
5. Never put store keys, .p8 files or service-account JSON in the repo or chat.

## Who owns what

| Job | Service | Notes |
|---|---|---|
| Products, entitlements, offerings, packages | RevenueCat hosted MCP | Can also touch store product state; treat price and availability edits as gated actions |
| Remote Config templates, rollback | Firebase MCP | Publish and roll back are gated; keep a copy of the previous template |
| Crashlytics issues, state | Firebase MCP | Read freely; changing issue state is low risk but logged |
| Attribution and campaign data | Adjust MCP (official, registered; aggregated data only) | Read-only |
| Store metadata, builds, TestFlight, tracks | Community ASC and Play MCPs (community, verify before enabling) or fastlane | Highest risk surface |
| Reliable CI uploads | fastlane with API key and service account | Preferred over MCP for writes |

## Procedure: products and entitlements

1. Take the product table from the design contract: ids, type (consumable, non-consumable, subscription), entitlement mapping, offering placement.
2. Keep one naming scheme; ids are permanent in the stores and cannot be reused after deletion in some cases, so confirm spelling with the human.
3. Create in RevenueCat; list the diff; verify that the store-side products exist and are approved or ready before any offering is shown to users.
4. Test in sandbox on a device with a test account. Record the receipt-validation result.
5. Server-authoritative grants: entitlements decide access, never client flags.
6. Prices: propose, show regional tiers as the stores define them, wait for approval, apply.

## Procedure: Remote Config

1. Fetch the current template and save it as the rollback copy.
2. Express the change as parameter, old value, new value, condition (segment, percentage).
3. Check the value against the economy simulators first (`economy_sim.py`); a config change to rewards is an economy change.
4. After approval, publish; watch Crashlytics and the key event for a defined window; roll back on the stated trigger.

## Procedure: attribution

Read installs, spend and cohort quality per channel. Remember iOS attribution runs through AdAttributionKit and consent (ATT) shapes what is measurable, so compare channels on cohort retention and revenue, not on install counts alone. Never share user-level data outside the MMP.

## Procedure: store metadata and TestFlight

1. Run `compliance_preflight.py` and `store_metadata.py` from the core plugin first (age rating, privacy answers, SDK manifests, AI disclosure).
2. Upload to TestFlight or the Play internal track only; internal testing does not require review on either store. The first Android bundle for a new app generally needs a manual Console upload.
3. Metadata edits: show a diff of every localized field; apply after approval.
4. Stop at "ready for review". The human presses submit, or says explicitly to do it; record the approval text in the release log.

## Community MCP risk checklist

- Read the source and pin the version before enabling.
- Count the tools; disable pricing, submission and delete tools if the server allows it.
- Use a dedicated API key with the narrowest role; revoke after the session if it was temporary.
- Prefer reads. If a write is needed and fastlane covers it, use fastlane.

## Worked example: "raise the starter pack price"

Claude does not change it. It reports the current price per region, the pack's share of revenue from the analytics, the effect modeled with `retention_ltv.py`, a proposed value, and the rollout plan, then asks the human for approval. Only after a clear yes, applies the change in the owning service and logs it.

## Approval log format

Every gated action is recorded in the project release or ops log as: date, action, service, object, before, after, approver text (quoted from chat), rollback step. If the approver text is missing, the action did not happen.

## Failure modes

- RevenueCat shows an offering but the store product is not ready: purchases fail silently in sandbox; check store product state first.
- Remote Config change published to all users by mistake: roll back to the saved template immediately, then report.
- Attribution numbers disagree with store consoles: expect differences from consent and attribution windows; reconcile on trends.

## Volatile facts (as of Oct 2026 - verify)

- RevenueCat hosted MCP at its documented URL; OAuth or API v2 key. Source: https://www.revenuecat.com/docs/tools/mcp
- Firebase MCP: `npx -y firebase-tools@15.34.0 mcp` (pinned); App Distribution not among its groups. Source: https://firebase.google.com/docs/ai-assistance/mcp-server
- Adjust official MCP exists; endpoint unconfirmed. Source: https://www.adjust.com/blog/adjust-mcp/
- Community store MCP list and maintenance status. Source: https://mcpservers.org/servers/forgeopslabs/appstore-mcp
- Store policy deadlines. Source: https://developer.apple.com/news/upcoming-requirements/
