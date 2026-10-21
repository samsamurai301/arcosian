# Store listing: [game title]

Revision: [date] | Owner: `release-manager` | Locales: [list] | Target stores: [App Store / Google Play]

<!-- Field limits change; confirm current limits in each store's documentation before finalizing (see Volatile facts). Write the first lines for a player scanning, not for search engines. Never claim features the build lacks. -->

## Core identity
| Field | iOS | Android | Notes |
|---|---|---|---|
| Title | [..] | [..] | brand + one keyword at most; limits in store docs |
| Subtitle / short description | [..] | [..] | benefit in plain words |
| Category | [..] | [..] | |
| Age rating answers | [..] | [..] | consistent with content and ads |
| Price / IAP | [..] | [..] | |

## Description
<!-- Structure: hook sentence; three benefit bullets; social proof only if real and sourced; call to action. -->
- Hook: [one sentence]
- Bullets: [benefit 1], [benefit 2], [benefit 3]
- What's new template: [short, specific, player-facing]

## Keywords and search
| Intent | Keyword | Rank target | Competition note |
|---|---|---|---|
| [genre] | [..] | [..] | [..] |

<!-- Do not stuff competitor names or trademarks. Validate with real store search suggestions and measure after launch. -->

## Visual assets
| Asset | Spec | Message | Status |
|---|---|---|---|
| Icon | [sizes] | Reads at 60 px, distinct from neighbors | [..] |
| Screenshots (n) | [device sizes] | Screen 1 = core fantasy; 2-3 = depth; 4+ = progression | [..] |
| Preview video | [length, specs] | First 3 seconds are gameplay | [..] |
| Feature graphic (Play) | [spec] | [..] | [..] |

Screenshots must show real gameplay from the shipped build; captions localized.

## Compliance and disclosures
- [ ] Privacy policy URL live and accurate; privacy nutrition label / data safety form matches SDKs
- [ ] Age rating questionnaire completed honestly (ads, IAP, random rewards)
- [ ] Odds disclosed for randomized purchases where required
- [ ] Ads and tracking consent flows match declarations
- [ ] AI-generated content disclosure per current store rules
- [ ] Support URL and contact working; account deletion path if accounts exist
- [ ] Third-party licences and attributions present

## Localization
| Locale | Title | Description | Screenshots | Reviewer |
|---|---|---|---|---|
| [..] | | | | native speaker |

## Experiments
Run store listing experiments (icon, first screenshot, short description) one variable at a time; record sample, duration and result.

## Release gates
- [ ] `store_metadata.py` and `compliance_preflight.py` pass
- [ ] Human approves copy and assets; submission done by a human

## Volatile facts (as of Oct 2026 — verify)
Field length limits, screenshot dimensions, and disclosure rules change. Source: https://developer.apple.com/help/app-store-connect/ and https://support.google.com/googleplay/android-developer/ (check the current pages; values here intentionally omitted).
