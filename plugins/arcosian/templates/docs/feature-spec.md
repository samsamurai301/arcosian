# Feature spec: [feature name]

Revision: [date] | Owner: [name] | Status: [draft / approved / built / shipped] | Contract pillar served: [pillar]

<!-- A spec is done when an engineer could build it and a tester could fail it without asking you anything. Prefer numbers to adjectives. -->

## Problem and goal
- Player problem: [what is missing or painful]
- Goal metric: [metric, baseline, target, by when] (label: measured / assumption)

## Non-goals
- [explicit exclusion]
- [explicit exclusion]

## Player flow
1. [Entry point and trigger]
2. [Step]
3. [Exit / return to loop]

<!-- Include the unhappy paths: first-time use, offline, interrupted by a call, backgrounded for an hour. -->

## Rules and numbers
| Parameter | Value | Range tested | Where tuned (file / remote config key) |
|---|---|---|---|
| [name] | [v] | [min-max] | [path] |

## States and edge cases
| Case | Expected behavior |
|---|---|
| First session | [..] |
| Offline / no store | [..] |
| App killed mid-action | [state restored or rolled back] |
| Clock changed by player | [..] |
| Max / min values | [..] |

## UI and feel
- Screens touched: [list]; touch targets at least [size]; one-hand reachable: [yes / no]
- Feedback: [animation, haptic, sound] on [events]
- Accessibility: [color-blind safe, text scaling, reduced motion]

## Telemetry
| Event | Parameters | Answers the question |
|---|---|---|
| [event_name] | [params] | [question] |

## Acceptance criteria
- [ ] Given [state], when [action], then [observable result].
- [ ] Deterministic playthrough covers the happy path (seed [n]).
- [ ] Unit tests cover the sim-core rules; no engine types in sim-core.
- [ ] Frame time and memory within budget on the low-tier device.
- [ ] Telemetry events fire exactly once per action.

## Risks and dependencies
- [dependency or risk] - mitigation: [..]

## Rollout
- Flag / remote config: [key], default [off], ramp [plan]
- Rollback: [how, how fast]
