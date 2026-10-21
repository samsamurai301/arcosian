# Game UI Patterns and Onboarding

This file covers the screens a mobile game is made of and the order in which a new player meets them: the in-play HUD, the meta hub, shops, inventories, progression maps, reward screens, the pop-up hierarchy that governs interruptions, tutorials, the first-session flow and the timing of permission prompts. Each section gives the job of the pattern, a layout recipe, rules, failure modes and a checklist. Numbers given are studio starting points, not laws: validate them in playtests on your smallest supported device. Interaction physics (thumb zones, target sizes, safe areas) live in `references/mobile-interaction.md`; type, colour and scaling live in `references/layout-typography-and-review.md`.

## Contents

1. The HUD
2. Meta hubs and home screens
3. Shops and offer surfaces
4. Inventories and collections
5. Progression maps and level select
6. Reward and result screens
7. Pop-up hierarchy and fatigue
8. Tutorials
9. First-session flow
10. Permission prompt timing
11. Pattern checklists

---

## 1. The HUD

**Job:** keep the information needed for the next decision visible without covering the thing being played.

### 1.1 Information tiers

| Tier | Meaning | Treatment | Examples |
|---|---|---|---|
| T1 | Needed every second to play | Always visible, high contrast, near the play focus | Health, moves left, timer, ammo, goal counter |
| T2 | Needed every few seconds | Always visible but small, or visible on change | Score, combo, secondary resource |
| T3 | Needed occasionally | Behind a tap, or appears on trigger | Inventory, full stats, quest log |
| T4 | Meta or background | Not in the play HUD | Currencies for the shop, social, settings detail |

Rule: if a T1 item is not glanceable within a fraction of a second, it is a T2. If the HUD has more than five or six persistent items, audit which tier each really is.

### 1.2 Layout recipe (portrait)

- **Top band** (inside the safe area): goal, moves or timer, pause. Information only, except pause.
- **Play field** in the middle: nothing overlaps the area where the player must see the board.
- **Bottom band** within thumb reach: boosters, skill buttons or controls. Sized for the thumb; the home indicator zone stays free.
- Keep the player's finger from occluding T1 information: for a bottom-hand drag, put the readout above the finger path.

### 1.3 Landscape

Controls sit at both lower corners (left stick or move, right actions); information at top corners; keep the centre clear. Add an option to swap sides for left-handed play where the control scheme is asymmetric.

### 1.4 Rules

- **Change draws the eye.** Animate a number only when it changes and only briefly; a permanently pulsing element trains players to ignore it.
- **Redundant encoding.** Pair colour with icon or shape (see accessibility notes in the layout reference).
- **Feedback proximity.** Show damage, points and gains near where they happened, then roll them into the HUD counter.
- **Scale with the screen, not with the content.** Targets and type follow the minimums even when the board shrinks on small phones.
- **Pause is a safe state.** Pausing hides nothing the player needs to resume, and resuming gives a short ramp (a beat or a countdown) in action games.
- **Do not put purchase prompts in the HUD during play.**

## 2. Meta hubs and home screens

**Job:** answer "what should I do now?" within a second and get the player into play with one tap.

### 2.1 Structure

- **One dominant call to action** (Play, Continue). It is the largest element, bottom third.
- **A navigation bar** of three to five destinations at the bottom (shop, collection, social, events and so on). More than five means an overflow or a second tier; do not squeeze to hit the minimum target size.
- **A status strip** at the top: currencies, energy or lives, profile. Informational; tap targets still meet the minimum.
- **A feature rail or event row** for time-limited content, ranked and capped.
- **Return-state reminders** (collect, claim, ready timers) shown as badges, not pop-ups.

### 2.2 Rules

| Rule | Why |
|---|---|
| Nav destinations unlock progressively, with locked tabs hidden or clearly marked with the unlock condition | Reduces overload for new players; avoids dead taps |
| Badge counts mean "something is ready"; clear them when seen, not only when acted on | Otherwise players stop trusting badges |
| Keep the nav bar in the same place on every hub screen | Motor memory |
| The back path is consistent: system back gesture, on-screen back, and tab behaviour agree | Prevents accidental app exit |
| Animated or idle hubs respect battery: limit continuous animation | Heat and drain |
| The hub never shows more than one promotional surface above the fold in the first sessions | Keeps the call to action dominant |

## 3. Shops and offer surfaces

**Job:** let a player who wants something find it, understand it and buy it, with no confusion about what they pay.

### 3.1 Layout

- Group by intent: featured or starter offers, currency packs, items, subscriptions or passes. Titles are plain.
- Each product card shows: what you get (icon, quantity), the price in the real currency or the premium currency (with the currency icon), and a clear buy affordance.
- If an offer is limited by time or quantity, show the real limit. Do not fabricate countdowns.
- Show the player's balance on the shop screen and update it live.

### 3.2 Rules

| Rule | Detail |
|---|---|
| Price clarity | Show the amount and currency unambiguously; for premium currency purchases show the cost, not just the icon |
| Insufficient funds | Offer a direct path to get more, with the shortfall stated, but never auto-open a purchase flow |
| Confirmation | Confirm purchases that spend premium currency on non-trivial items; use a hold or a second tap, not a modal wall for small items |
| Receipt feedback | Show what was granted, animate it into the inventory or balance, and confirm in text once |
| Restore purchases | Provide a visible restore control where the platform requires one |
| Odds or probabilities | Disclose where required; place the disclosure within reach of the buy action (`legal-ethics`) |
| Child audiences | Extra care: no pressure tactics, parental gate where required (`legal-ethics`, `monetization`) |
| Offline | A clear "can't reach store" state with retry, never a spinner that never ends |

## 4. Inventories and collections

**Job:** let the player find, compare, equip and manage items quickly.

### 4.1 Layout

- A grid for visual items, a list for text-heavy items. Offer sort and filter once the item count passes what fits on roughly two screens.
- Item cell shows icon, rarity cue (shape or frame, not colour alone), quantity or level, and new or equipped markers.
- Selecting an item shows a detail panel or sheet. On phones use a bottom sheet in the thumb arc; on tablets, a side panel.
- The primary action (equip, use, upgrade) is in the detail view's bottom area.

### 4.2 Rules

- Show comparisons ("+12 attack") not raw tables when equipping.
- Provide "best for this slot" or auto-equip for casual audiences.
- Mark new items until viewed; clear the marker on view.
- Support drag-and-drop only as a shortcut; every drag action has a tap alternative. Drag anatomy is in `references/mobile-interaction.md` section 4.2.
- Capacity limits: show current and max, and explain what happens at max before the player hits it.
- Selling or destroying: confirm, show the result, and support undo for a short window where feasible.
- Empty states say what the screen is for and how to get items.

### 4.3 Scale

| Item count | Pattern |
|---|---|
| Under about 20 | Single grid or list, no filters |
| About 20 to 100 | Tabs by category, sort |
| Over 100 | Search or filters, saved loadouts, auto-sort, virtualised list (performance) |

## 5. Progression maps and level select

**Job:** show where the player is, what is next and what is far away, and make "continue" the easiest tap.

### 5.1 Patterns

| Pattern | Use | Notes |
|---|---|---|
| Vertical scrolling path | Level-based casual | Start scrolled to the current level; show the next few and a hint of the next milestone |
| Chapter or world map | Episodic or world themes | Locked areas show unlock condition |
| Grid of levels | Packs of levels, arcade | Show stars or best score; keep cells big enough to tap |
| Tree or web | Skill or tech trees | Pan and zoom with a recenter button; avoid tiny nodes |
| Linear list | Quests and missions | Sort by what is ready |

### 5.2 Rules

- Auto-scroll to the current node on open, with the camera easing, not snapping, after progress.
- The current node is visually dominant and tappable with one tap from anywhere (also reachable via the Play button).
- Locked nodes are visibly locked, with the reason on tap.
- Milestones (chests, bosses, chapter ends) are shown ahead so players see a reason to continue.
- A long map needs a quick-jump (to current, to start) and keeps its scroll position through interruptions.
- Do not rely on pinch-zoom as the only way to read a dense map; offer large tap targets at default zoom.
- Progress after a win animates from the old node to the new one; this is a reward moment, so let it complete before any pop-up.

## 6. Reward and result screens

**Job:** convert an outcome into a feeling and a next step.

### 6.1 Anatomy

1. **Outcome headline** (win, fail, new best), short.
2. **Primary result** (stars, score, goal state) with a short animated reveal.
3. **Rewards earned**, flying into the visible balance.
4. **Next action** — one dominant button (Next, Continue). A secondary (Retry, Home) smaller.
5. **Optional offers** (double the reward, watch an ad, upgrade), strictly secondary and never blocking the primary.

### 6.2 Pacing

- Reveal in a sequence that totals a couple of seconds for ordinary wins; allow tap to skip to the end state. Longer sequences are reserved for rare moments.
- Never lock the Next button behind the animation if the player taps repeatedly; the first tap completes the animation, the second proceeds.
- Fail screens: say what happened and offer the most useful recovery (retry, a hint, an easier path). Offer help before offering a purchase.
- Rare or large rewards earn a bigger moment, because contrast between ordinary and special is what makes special feel special.

### 6.3 Rules

| Rule | Why |
|---|---|
| Reward screens do not host unrelated pop-ups | Protects the emotional peak |
| Show reward quantities exactly and keep them consistent with the economy | Trust; see `economy-design` |
| Randomised rewards reveal what the player got, not a menu of what they missed | Avoids pressure |
| Rewarded ads are opt-in and labelled with what the player receives | Honesty; see `monetization` |
| Keep sound and haptics optional and short | Accessibility and public use |

## 7. Pop-up hierarchy and fatigue

Pop-ups (modals, interstitial overlays, full-screen offers, prompts) draw on one shared attention budget. Left ungoverned, each team ships its own, and the player meets six at launch.

### 7.1 Hierarchy

| Rank | Class | Examples | Rule |
|---|---|---|---|
| P0 | System and legal | Age gate, consent, required update, connectivity errors | Always allowed, shown at the right moment, never stacked |
| P1 | Player-initiated | Confirmations the player asked for, reward claims | Shown immediately, no cap |
| P2 | Progress | Level-up, unlock notice, milestone | Short, deferred to a calm moment, merge where possible |
| P3 | Re-engagement | Daily bonus, event start | At most one per session start, capped |
| P4 | Commercial | Offers, store promotions | Lowest priority; never over P2 moments; hard caps |
| P5 | Social and rating | Review prompt, share, invite | At positive moments only, rare |

A single **pop-up queue** (a service) sorts by rank, de-duplicates, and decides what shows now, later or never. No feature opens a modal directly.

### 7.2 Queue rules

- At most one modal at a time. A queued item waits for the player to be idle, not mid-input.
- Cap per session and per day for P3 to P5; record dismissals and back off after repeated dismissal.
- Block P4 and P5 during the first sessions, during failure states, and immediately after a P2 moment.
- Provide one-tap dismissal with a visible, adequately sized close control, plus back gesture support.
- Persist the queue across interruptions where the event is still valid; drop it if it is stale (an expired offer).
- Log every show, dismiss and accept with the pop-up id for review (`player-analytics`).

### 7.3 Fatigue detection

| Signal | Reading |
|---|---|
| Rising dismiss rate on the same pop-up | Players have learned to ignore it |
| Session length drops when pop-up count rises | Interruptions are costing play time |
| Review prompts followed by negative reviews or reports | Timing is wrong |
| Support tickets about "can't find X" after modals multiply | Navigation is being buried |

Treat pop-up count per session as a tracked KPI, with a budget agreed in `design-review`.

### 7.4 Writing pop-ups

- Title says what it is, body says what to do or what you get, buttons are verbs.
- A negative option is as visible as the positive; do not disguise it as a link.
- No fake urgency. If a timer exists it reflects a real deadline.

## 8. Tutorials

**Job:** get the player to competence with the least reading and the fewest forced steps.

### 8.1 Method choice

| Method | Use when | Cost |
|---|---|---|
| Learn by playing (level design teaches) | Mechanic can be taught by a safe first encounter | Level design time |
| Contextual hint | A new element appears | Low; must trigger on need |
| Guided step (highlight and mask) | UI-heavy action the player must find | Medium; brittle against layout changes |
| Demonstration (ghost hand, animation) | Gestures | Medium |
| Text screen | Rules that cannot be shown | Last resort; skippable and re-readable |

### 8.2 Step anatomy

- **One instruction, one target, one action.** The step ends when the action is done, not when a Next button is pressed.
- Mask everything except the target; keep the target tappable and the rest not, so the player cannot wander.
- Show the instruction near the target, in the thumb arc where possible.
- Short copy: a few words; use pictograms or a hand animation to replace text.
- Allow a safe mistake: wrong taps are ignored or gently corrected, never punished in the first minutes.

### 8.3 Rules

- Teach a thing at the moment it is first needed, not up front.
- Space new concepts: one new idea at a time, then use it before the next appears.
- Provide a way to re-read: a help page or a "tips" log.
- Skipping: offer skip for returning players (reinstall, second device), not for the very first run, unless the genre demands.
- Resume mid-tutorial after interruption at the last completed step.
- Don't gate the tutorial behind sign-in or consent walls beyond what is legally required.
- Tutorial steps use stable ids, logged in order, so funnels show where players stall.

## 9. First-session flow

**Job:** deliver the core fun, a first reward and a reason to return, in the shortest path.

### 9.1 Principles

- **Time to first fun** is the headline metric: the number of taps and seconds from app open to the first satisfying action. Remove everything that does not serve it.
- **Defer everything deferrable:** account creation, notifications, ratings, social, offers, language selection beyond auto-detect.
- **First win is guaranteed or near-guaranteed.** Difficulty on the first levels is designed, not tuned for later.
- **Show the loop, then the meta.** The first meta unlock appears after the player understands what earns it.
- **End the first session with a hook:** a next goal in view, a timed reward to return for, or an open story question.

### 9.2 Example flow (skeleton, adapt per genre)

| Step | Content | Notes |
|---|---|---|
| 0 | Splash then straight into play | No menus; minimal loading |
| 1 | Zero-text or minimal tutorial level | One action, immediate success |
| 2 | Second level, new variation | Reinforce, small reward |
| 3 | First reward moment | Animated, rewards flying to the balance |
| 4 | First meta unlock or first story beat | Pointer to what it is for |
| 5 | A few more levels | Difficulty ramps gently |
| 6 | Light soft ask (account link or notification priming) at a natural pause | Only if value is clear |
| 7 | Session end hook | Preview of tomorrow's reward or next chapter |

### 9.3 Returning and second session

- Greet with state: "continue where you left off", with progress preserved.
- Introduce one new system per session, not per minute.
- Re-tutorial only what the player has not used.
- Daily reward screens are P3 pop-ups under the queue rules above.

### 9.4 Measurement

Define funnel steps with stable ids: app open, first input, tutorial complete, first win, first meta action, session end, return next day. Compare cohorts when you change the flow. Event design lives in `player-analytics`; thresholds come from your own baseline, not from published averages.

## 10. Permission prompt timing

System permissions (notifications, tracking, camera, microphone, location, photos, contacts) are one-shot or hard to re-enable after denial on many platforms, so a premature prompt burns the opportunity.

### 10.1 Rules

1. **Ask in context, at the moment of value.** The player has just done something the permission would improve.
2. **Prime first, with your own screen.** A short, honest explanation with "Allow" and "Not now" buttons; only the "Allow" leads to the system dialog. "Not now" does not consume the system prompt.
3. **Never ask on the first frame** or before the player has experienced any value.
4. **One permission at a time**, never chained back to back.
5. **Explain the benefit in the player's terms**, not the platform's.
6. **Offer a path to enable later** (settings with a deep link to system settings if the system prompt is spent).
7. **The game works without it.** A denial degrades gracefully, with no nagging.
8. **Respect platform policy** on consent and tracking; coordinate with `legal-ethics` and `store-release`.

### 10.2 Timing table

| Permission | Good moment | Bad moment |
|---|---|---|
| Notifications | After a completed timer, energy refill, or a second session where a reminder helps | Launch, or before the first win |
| Tracking or ad personalisation (where applicable) | After the first session, after a short explanation, in line with platform and legal requirements | Before the first screen of play |
| Camera, photos | At the feature that needs it (profile photo, AR) | At install or first run |
| Microphone | When the player taps a voice feature | Anywhere unrelated |
| Location | Only when a location feature is used | Never "for later" |
| Contacts or friends | When the player taps "invite friends" | At onboarding |
| App rating | After a high point (a milestone win) in a calm moment, rarely | After a failure or at launch |

### 10.3 Denial handling

- Remember the denial; do not re-prime within the same session.
- A re-ask is allowed only after a meaningful change of context and a capped number of times.
- If the permission is permanently denied, show a one-line explanation with a button to open system settings when the player re-enters the feature.

## 11. Pattern checklists

### 11.1 Screen readiness

- [ ] The screen's single job is stated; one dominant action
- [ ] Information tiered; T3 and T4 off the main view
- [ ] Targets meet platform minimums; neighbours of destructive controls have spacing
- [ ] Back path and interruption resume defined
- [ ] Empty, loading, error, offline, insufficient funds and max states designed
- [ ] Text from string tables, tested at expansion and at largest system font
- [ ] Pop-ups on this screen route through the queue

### 11.2 Flow readiness

- [ ] Funnel steps have stable ids
- [ ] Time to first fun measured and budgeted
- [ ] No permission or consent before value, except what law requires
- [ ] Tutorial steps: one action each, resumable, skippable for returners
- [ ] Reward screens protected from stacked pop-ups
- [ ] First session ends with a hook
