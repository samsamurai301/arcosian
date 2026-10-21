# Live-ops calendar: [game title]

Revision: [date] | Owner: `liveops-manager` | Planning horizon: [N weeks] | Cadence: [weekly / biweekly]

<!-- A calendar is a promise to the player and a load on the team. Plan content you can actually ship, keep a buffer, and never schedule two big events whose rewards compete for the same player attention. -->

## Principles
- Rhythm beats volume: a predictable weekly beat plus one monthly highlight.
- Every event has a goal metric, a cost (content + economy), and an end state.
- Events must not break the economy: run `economy_sim.py` on reward tables before scheduling.
- Fairness: no hidden odds; no manufactured scarcity that punishes players for life events.

## Event types
| Type | Purpose | Typical length | Team effort |
|---|---|---|---|
| Daily login / streak | Habit | continuous | low |
| Weekly challenge | Re-engagement | 7 days | low |
| Limited-time mode | Variety | [days] | medium |
| Seasonal event | Spikes, content | [weeks] | high |
| Collab / holiday | Reach | [..] | high |
| Sale / offer | Monetization | [days] | low |

## Calendar
| Week | Dates | Event | Goal metric | Rewards (cost in soft/hard currency) | Content needed | Status |
|---|---|---|---|---|---|---|
| 1 | [..] | [..] | [..] | [..] | [..] | [planned / built / live] |
| 2 | [..] | | | | | |

<!-- Fill the buffer weeks explicitly. A calendar with no empty weeks is already late. -->

## Segmentation
| Segment | Definition | Treatment |
|---|---|---|
| New (D0-D7) | [..] | protect from heavy offers; teach |
| Engaged | [..] | events, social |
| Lapsed | [..] | win-back message and offer, capped |
| Payers | [..] | content, no pressure |

## Release checklist per event
- [ ] Spec approved; economy simulated; remote config keys defined
- [ ] Assets and strings localized; QA on both platforms
- [ ] Telemetry events added; dashboard slice ready
- [ ] Kill switch tested; rollback plan
- [ ] Store/notification copy reviewed; push opt-in rules respected
- [ ] Post-event review scheduled

## Post-event review
| Event | Goal | Result | Economy impact | Keep / change / drop |
|---|---|---|---|---|
| [..] | [..] | [..] | [..] | [..] |

## Dependencies and constraints
- App update needed vs remote-config-only: [flag per event]
- Store review lead time: [assumption: x days; verify]
- Holidays and platform events to avoid or align with: [list, source]
