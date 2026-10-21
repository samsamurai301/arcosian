# Playtest plan: [milestone / build]

Revision: [date] | Owner: `qa-lead` | Build: [version / commit] | Dates: [from - to]

<!-- A playtest answers specific questions. If you cannot name the decision it informs, do not run it. Combine automated passes (deterministic playthroughs, bots) with human sessions; each catches different failures. -->

## Questions and decisions
| # | Question | Decision it informs | Method |
|---|---|---|---|
| 1 | [Do new players understand the core loop in 60 seconds?] | [keep / rework FTUE] | [moderated sessions] |
| 2 | [Is level N a difficulty spike?] | [retune] | [bots + human] |

## Automated layer
| Check | Tool | Pass criteria |
|---|---|---|
| Static gate and unit tests | CI | zero errors |
| Scripted smoke playthrough | runner `--mode=script` | all expectations met |
| Bot runs (greedy, random) | runner `--mode=bot` | softlock rate [<= x%], win-rate band [a-b%] |
| Visual capture | screenshot mode | no clipped text, safe areas respected |
| Persona playtests | `player-simulator` | friction list triaged |

## Human sessions
| Item | Plan |
|---|---|
| Participants | [n] per segment; recruited from [source]; none from the dev team |
| Segments | [new / casual / genre veteran] |
| Devices | [low / mid / high tier, iOS and Android] |
| Session format | [moderated think-aloud / unmoderated remote], [minutes] |
| Consent and privacy | [consent captured; minors excluded or guardian consent; no personal data in notes] |

Small groups surface most usability problems but not rates; use human sessions for "why", telemetry and bots for "how often".

## Script (moderator)
1. Welcome and consent; clarify we test the game, not the player.
2. Pre-questions: [habits, genres played].
3. Free play without help for [minutes]; observe silently, note time-to-first-action.
4. Targeted tasks: [task 1], [task 2].
5. Post-questions: [what was the goal, what was frustrating, would you play again and why].

## Metrics to capture
- Time to first meaningful action; tutorial completion; deaths or fails per level; abandon points
- Self-reported: clarity (1-5), fun (1-5), intent to return; open comments
- Observations: confusion, misread UI, missed taps, rage taps

## Issue triage
| Severity | Definition | Action |
|---|---|---|
| S1 | Crash, data loss, blocks progress | Fix before next build |
| S2 | Major confusion or exploit | Fix this milestone |
| S3 | Friction | Backlog, ranked by frequency x impact |
| S4 | Polish | Batch |

## Reporting
- Report due [date] to [owner]; format: top 5 findings, evidence (clip or quote), recommendation, confidence
- Findings seen by one participant are hypotheses, not conclusions; label them.

## Exit criteria
Go to next milestone when: [no open S1, S2 count <= n, question 1 answered with >= x of y participants succeeding].
