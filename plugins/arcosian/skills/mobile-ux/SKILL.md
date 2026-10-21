---
name: mobile-ux
description: 'Mobile game UX codex: thumb zones, touch targets, gestures, safe areas, interruptions, HUD, hubs, shops, inventories, reward screens, pop-up hierarchy, tutorials, first-session flow, permission timing, typography, contrast and Godot/Unity UI scaling. Use when asked "design this screen", "UX review", "onboarding flow", "safe area" or "audit this layout".'
when_to_use: 'Screen and flow design, HUD and menu layout, onboarding UX, pop-up and permission timing, UI scaling, UX acceptance criteria.'
---

# Mobile UX

A phone game UI is used one-handed, in short sessions, under interruption, on screens from small phones to tablets, by players who will not read. Senior UX work here is mostly constraint management: physical reach, glanceable information, a hard budget on interruptions, and layouts that survive every aspect ratio and language. This skill gives rules you can check and a script that checks the structural ones.

## What this skill gives you

- Physical and interaction rules: units, thumb zones, target sizes, gestures, safe areas, orientation, interruptions.
- Screen-pattern guidance for HUD, meta hubs, shops, inventories, progression maps, reward screens and pop-ups.
- Onboarding, first-session flow and permission-prompt timing.
- Typography, iconography, contrast and responsive layout rules, with Godot and Unity scaling recipes.
- A heuristic review checklist, UX acceptance criteria and an audit script for contrast, units, text expansion and layout specs.

## Core models

1. **The thumb sets the layout.** Primary actions go in the natural thumb arc at the bottom of the screen; destructive or rare actions go out of the arc. Decide dominant hand and posture first (`references/mobile-interaction.md` section 2).
2. **Targets have a floor and a context.** Platform minimums are floors, not goals. Dense boards, danger neighbours (a destructive control beside a common one) and gloved or moving use push sizes up (section 3).
3. **One primary action per screen.** The eye should know within a second what to press. Everything else is visually subordinate. If two buttons compete, the screen has two jobs; split it.
4. **Glanceable, not readable.** In-play information must be understood in a glance: icon plus number, colour plus shape, never colour alone, and never a sentence.
5. **Every screen is interruptible.** Calls, locks, notifications and process death will happen. Resume to where the player was, with state intact (section 7).
6. **Interruptions cost trust.** Pop-ups, prompts and offers draw from a shared budget per session. Rank them, cap them, and never stack them over a player's achievement moment (`references/game-ui-patterns-and-onboarding.md` section 6).
7. **Teach by doing.** A tutorial step has one instruction, one highlighted target, and ends when the player performs the action. Text that can be replaced by an affordance should be.
8. **Layout is a function of the screen, not a picture of it.** Anchors, safe areas and flexible containers beat pixel positions; test the extremes of aspect ratio and language (`references/layout-typography-and-review.md`).
9. **Feedback at the finger.** Acknowledge touch within about one frame at the point of contact: pressed state, haptic or sound where appropriate (`references/mobile-interaction.md` section 8).

## Decision procedures

### A. Designing a new screen

1. Write the screen's single job and its entry and exit points in one sentence each.
2. List information by priority: must see, should see, may see. Cut or demote the third group.
3. Pick the posture and hand (`ui_audit.py template --hand either`); place primary actions in the reach zone.
4. Choose the pattern from `references/game-ui-patterns-and-onboarding.md` (HUD, hub, shop, inventory, map, reward).
5. Set type sizes, contrast and icon style from `references/layout-typography-and-review.md`.
6. Spec the layout as JSON and run `layout` (below); fix findings.
7. Define every state: empty, loading, error, offline, insufficient funds, max level, long text, many items.
8. Run the heuristic review checklist before handing to engineering.

### B. Placing controls (decision table)

| Control type | Place | Reason |
|---|---|---|
| Primary action (play, confirm, collect) | Bottom centre or bottom third, full-width or large | Thumb arc, easiest to hit |
| Frequent secondary (boosters, skills) | Bottom corners or bottom row | Reachable without regrip |
| Currency and status | Top edge, glance only | Read, not pressed |
| Settings, pause | Top corner away from the dominant thumb, 44 pt or larger target, extra padding | Rare use; avoid accidental taps |
| Destructive (delete, reset, spend premium currency) | Out of the arc, behind confirmation or hold | Prevent accidents |
| Close on a pop-up | Top corner plus tap-outside or back gesture where safe | Familiar, but never the only way out on one-hand layouts |

### C. Deciding whether an interruption is allowed

1. Is the player mid-input (drag, swipe, board in motion)? Defer.
2. Did they just fail, or just earn something? Do not sell on failure; let the reward land first.
3. Is it required (legal consent, permission with a feature reason)? Show at the moment of need.
4. Otherwise, rank it in the pop-up hierarchy and check the per-session cap.
5. Always give a way to dismiss with one tap, and remember the dismissal.

### D. Auditing a layout with the script

1. Print a starter spec: `python3 scripts/ui_audit.py template --platform ios --hand either --out screen.json`.
2. Fill in the elements (id, role, rect, text, `translatable`, `font_pt`).
3. Run `python3 scripts/ui_audit.py layout --spec screen.json`. Exit 1 means a check failed; add `--json` for tooling.
4. Convert units with `units`, check colours with `contrast`, check translated length with `expansion`.

### E. Handling a notch, island or gesture bar

1. Treat the safe area as the container for anything interactive; let backgrounds bleed beyond it.
2. Keep gesture-edge zones (bottom home indicator, side back gestures) free of critical taps.
3. Test the matrix in `references/mobile-interaction.md` section 5.4.

## Mobile specifics

This skill is mobile-first throughout. The differences that bite most often:

- **Posture varies by session:** commute is one-handed portrait, couch is two-handed, tablet is cradled. Support the weakest posture for your genre (section 2).
- **Orientation is a product decision:** pick it per genre, handle rotation if you allow it, and treat tablets and foldables as resolution changes (section 6).
- **System UI is hostile:** notifications, control centre swipes and back gestures steal edge touches. Keep edge drags out of core play.
- **Battery, heat and data matter to UI:** avoid constantly animating idle screens; offer a low-power mode when the game is long-session.
- **Store policy shapes UX:** permission prompts, tracking consent and purchase flows follow platform rules (see `store-release` and `legal-ethics`).

## Anti-patterns

| Anti-pattern | Detect | Fix |
|---|---|---|
| Tiny close button on pop-ups | `layout` target warnings | Enlarge the hit area beyond the glyph; add tap-outside |
| Top-corner primary action | Placement review | Move to bottom third |
| Wall-of-pop-ups at launch | Count modal screens before the first play | Cap, rank, defer to after the first win |
| Permission prompt on first frame | Prompt fires before any value shown | Ask in context, after a priming screen |
| Colour-only state (red vs green) | Greyscale screenshot test | Add icon, shape or label |
| Fixed pixel layouts | Run at a 20:9 phone and a 4:3 tablet | Anchors, containers, safe areas |
| Text baked into images | Search assets for text | Live text from string tables |
| Tutorial as a text wall | Steps with more than one instruction | One action per step, highlight the target |
| Shop with unclear prices or currency | Review price and currency labelling | Show real currency and amounts plainly; see `monetization` and `legal-ethics` |
| Unrecoverable interruption | Kill app mid-level, reopen | Implement the resume contract |
| Dark pattern timers and fake urgency | Review offer copy | Honest timers; see `legal-ethics` |

## Using the ontology

- Screens and flows belong in the design contract's UX section (`game-ontology`): screen list, flows, orientation, supported aspect ratios, accessibility targets, and the FTUE definition.
- The FTUE steps map to the onboarding funnel events in `player-analytics`; name each step id consistently so drop-off is attributable.
- Layout specs (`screen.json`) can be kept next to the design contract and re-audited when the UI changes.
- Agent: `arcosian:ux-designer` owns this domain; `arcosian:critic` and the `design-review` workflow apply the review checklist.

### Script: `scripts/ui_audit.py`

Stdlib Python 3.9. Exit 0 ok, 1 check failed, 2 usage error; `--selftest` runs built-in fixtures.

| Command | Use | Example |
|---|---|---|
| `contrast` | WCAG contrast ratio of two colours; `--large` and `--nontext` judge at 3:1 | `python3 scripts/ui_audit.py contrast --fg "#FFFFFF" --bg "#2A6FDB"` |
| `units` | Convert between pt, dp, px and mm given a scale and ppi | `python3 scripts/ui_audit.py units --pt 44 --scale 3` |
| `expansion` | Translation length budget for a source string | `python3 scripts/ui_audit.py expansion --text "Collect reward" --max-chars 20` |
| `layout` | Audit one screen layout spec (targets, safe area, overlap, text) | `python3 scripts/ui_audit.py layout --spec screen.json` |
| `template` | Print an example spec for a platform and hand | `python3 scripts/ui_audit.py template --platform android --hand right` |

## Reference library

| File | Contains | Read when |
|---|---|---|
| `references/mobile-interaction.md` | Units and densities, the finger, thumb zones, target sizes, gestures, safe areas, orientation, tablets and foldables, interruptions, touch feedback, one-hand audit, volatile platform facts | Placing controls, sizing targets, handling safe areas or lifecycle |
| `references/game-ui-patterns-and-onboarding.md` | HUD, meta hubs, shops, inventories, progression maps, reward screens, pop-up hierarchy and fatigue, tutorials, first-session flow, permission timing | Designing a screen or flow, or planning onboarding |
| `references/layout-typography-and-review.md` | Typography, iconography, contrast, responsive layouts and aspect ratios, tablets, Godot and Unity UI scaling, heuristic UX review checklist, UX acceptance criteria | Spec'ing visual layout, scaling UI, or reviewing and signing off |
| `scripts/ui_audit.py` | Contrast, units, expansion, layout audit and template (above) | Before handoff and after any layout change |

## Volatile facts (as of Oct 2026 — verify)

Platform minimums and OS behaviour change; the full table with sources is in `references/mobile-interaction.md` section 10. Key sources to recheck:

- Apple Human Interface Guidelines (target size, accessibility): https://developer.apple.com/design/human-interface-guidelines/accessibility
- Material Design touch targets: https://m3.material.io/foundations/designing/structure
- WCAG 2.2 target size and contrast criteria: https://www.w3.org/TR/WCAG22/
- Android 16 behaviour changes (edge-to-edge, large-screen orientation rules, game exemption): https://developer.android.com/about/versions/16/behavior-changes-16
- Google Play target API requirements: https://developer.android.com/google/play/requirements/target-sdk

## Related skills

- `mechanics-codex`: control schemes (virtual sticks, skill clusters) that sit on top of this interaction layer.
- `game-feel`: juice and feedback timing for taps, rewards and transitions.
- `accessibility-localization`: full accessibility options, text expansion and localisation workflow.
- `player-psychology`: attention, habit and reward timing behind pop-up and reward design.
- `player-analytics`: funnel events for onboarding and screen flows.
- `monetization`: shop and offer design that this skill places and sequences.
- `art-direction`: visual style that icons and typography must express.
- `engine-godot`, `engine-unity`: engine specifics for UI implementation.
- `mobile-performance`: UI rendering cost, overdraw and canvas rebuilds.
- `narrative-design`: text length and reading speed for story screens.
