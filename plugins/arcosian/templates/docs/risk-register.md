# Risk register: [game title]

Revision: [date] | Owner: `producer` | Review cadence: [weekly]

<!-- Keep it short and alive. A register of 60 stale risks is worse than 10 honest ones. Review the top 5 in every milestone meeting, retire resolved risks, and add the new ones that scare you. -->

## Scoring
- Likelihood (L): 1 rare, 2 possible, 3 likely, 4 almost certain
- Impact (I): 1 minor, 2 noticeable slip, 3 milestone at risk, 4 project at risk
- Score = L x I. Act on 8 and above; watch 4-7; log below 4.

## Register
| ID | Category | Risk (cause -> event -> consequence) | L | I | Score | Owner | Mitigation (reduce) | Contingency (if it happens) | Trigger / early warning | Status | Review date |
|---|---|---|---|---|---|---|---|---|---|---|---|
| R1 | Design | [Core loop not fun after 3 sessions -> low retention -> no launch] | 3 | 4 | 12 | [name] | [prototype test by date] | [pivot to alt concept] | [playtest fun < x] | open | [date] |
| R2 | Tech | [..] | | | | | | | | | |
| R3 | Market | [..] | | | | | | | | | |
| R4 | Store / compliance | [policy change or rejection] | | | | | | | | | |
| R5 | Team | [key person unavailable] | | | | | | | | | |
| R6 | Budget | [..] | | | | | | | | | |
| R7 | Legal / IP | [asset licence, AI tool terms] | | | | | | | | | |
| R8 | Dependency | [SDK, engine upgrade, vendor outage] | | | | | | | | | |

## Categories to scan each time
Design fun and clarity; economy balance and inflation; technical performance on low-tier devices; platform policy (privacy labels, age rating, ads, payments); third-party SDKs and licences; AI asset provenance and disclosure; scope creep; schedule dependencies; team capacity; funding runway; market timing and competitor launches.

## Response options
| Response | Use when |
|---|---|
| Avoid | Cut the feature or change the plan |
| Reduce | Prototype early, add tests, simplify |
| Transfer | Vendor, contract, insurance |
| Accept | Cost of action exceeds expected loss; record a trigger |

## Closed risks
| ID | Closed on | Outcome | Lesson |
|---|---|---|---|
| [..] | [date] | [happened / avoided] | [..] |

## Review log
| Date | Attendees | Changes made |
|---|---|---|
| [date] | [..] | [new / escalated / closed] |
