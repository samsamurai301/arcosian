# Live-Ops Fundamentals and Events

This file defines what live-ops is, lists the main event types with when to use each, explains cadence and layering, and gives a complete procedure for designing one event: goal, rewards, difficulty, duration, economy impact and measurement. It includes worked examples and templates. Read it when you plan an event, audit an existing one, or decide how heavy the live program should be for a team of a given size.

## Table of contents
1. What live-ops covers
2. Team and capacity models
3. Event taxonomy
4. Event templates in detail
5. Cadence and layering
6. Designing an event step by step
7. Reward design
8. Difficulty and effort tuning
9. Duration and timing
10. Economy impact modelling
11. Measurement plan
12. Worked example: collection event
13. Worked example: tournament
14. Event spec template
15. Post-event review
16. Failure patterns

## 1. What live-ops covers
- Content: events, seasons, new levels, modes, characters or items.
- Economy: tuning rewards, prices, offers, odds (with disclosure), sinks.
- Engagement: notifications, mail, in-game messaging, social features.
- Operations: remote config, releases, incident response, support.
- Analytics: dashboards, tests, cohort tracking.
- Community: communication, feedback loops, moderation.
The loop of live-ops: plan -> build -> release -> observe -> learn -> adjust. Cycle times should shrink with maturity; configuration-driven content shortens the cycle from weeks to days.

## 2. Team and capacity models
| Team size | Realistic live program | Notes |
|---|---|---|
| Solo or tiny | Daily login, one weekly challenge, one seasonal theme every few weeks | Automate with templates and remote config; avoid bespoke art |
| Small (under about ten) | Layered calendar with one special event per few weeks | Reuse mechanics; outsource localization |
| Mid | Seasons, collaborations, segmentation, A/B tests | Dedicated live-ops manager and analyst |
| Large | Multiple concurrent seasons, regional calendars, CRM | Tools for self-serve event creation |
Capacity rule: plan events against the slowest discipline (usually art or QA); include an explicit buffer and a fallback "evergreen" event if a drop slips.

## 3. Event taxonomy
| Type | Mechanic | Primary goal | Typical risk |
|---|---|---|---|
| Login streak | Rewards for consecutive days | Re-engage, habit | Streak anxiety; allow a recovery |
| Daily/weekly quests | Task list with rewards | Habit, direct play toward features | Chore feeling; keep tasks varied |
| Milestone ladder | Cumulative progress track | Deepen | Grind if thresholds too high |
| Collection | Collect items through play | Deepen, monetize cosmetically | Random duplicates, odds disclosure |
| Tournament / leaderboard | Rank by score within brackets | Core engagement, competition | Cheating, fairness, demotivating low ranks |
| Co-op / guild goal | Shared target | Community, retention | Free-rider problem |
| Limited-time mode | New rules for a short time | Variety, press moments | Balance, QA load |
| Seasonal pass | Free and premium reward tracks | Engagement and revenue | Completability, fatigue |
| Challenge / boss event | Hard content with big reward | Core engagement | Excludes casuals; offer tiers |
| Offer events | Bundles, sales, piggy bank | Monetize | Ethics, cannibalization |
| Welcome-back | Re-entry rewards | Win-back | Do not punish loyal players |
| Community event | Global shared goal | Community | Needs scale |
| Collaboration / IP | Crossover content | Acquisition and PR | Licensing and approvals |
| Beginner event | New players only track | Onboarding retention | Must not clash with the tutorial |

## 4. Event templates in detail
### 4.1 Milestone ladder
- Structure: N tiers, each requires cumulative points from specified actions; rewards at each tier, a grand reward at the end.
- Tuning: first tier within the first session of the event; final tier reachable by a target share of engaged players.
- Variation: point sources rotate daily to avoid routine.
### 4.2 Collection
- Players earn tokens and exchange for items; completion of a set yields an exclusive.
- Avoid pure random drops for the last item (the dreaded last-card problem); add a targeted exchange or guaranteed progress.
- If any element is randomized for money, disclose odds (see `monetization`).
### 4.3 Tournament
- Bracket by skill or progression to protect new players; promote and demote between divisions.
- Rewards by rank band, plus a participation reward.
- Anti-cheat: server-authoritative scoring, anomaly detection, replay checks.
- End time in UTC with local display; avoid last-second sniping advantages via a grace rule.
### 4.4 Co-op goal
- Team target with individual contribution floors; rewards scale with team success and individual participation, so free riders cannot take everything and low contributors are not punished harshly.
### 4.5 Limited-time mode
- Reuse core systems with a twist; QA must test it as a mini-game; ensure it does not break progression or economy.
### 4.6 Season
- Spine of the calendar: theme, pass, weekly missions, new content, a narrative arc.
- Season length matches content cadence; announce the end date from day one.

## 5. Cadence and layering
Weekly rhythm example (illustrative):
| Day | Layer |
|---|---|
| Daily | Login reward and quests |
| Start of week | Weekly challenge opens, leaderboard resets |
| Midweek | Limited-time mode or bonus |
| Weekend | Higher activity: social or co-op event |
| Every few weeks | Special event or content drop |
| Season boundary | Pass reset, narrative beat, store refresh |
Guidelines:
- A predictable rhythm helps habit; surprises add spice but not chaos.
- Leave quiet days; players need time to feel progress.
- Never cancel the evergreen layer (daily, weekly) to run specials; stack by priority instead.
- Count concurrent "must-do" tasks per day per player; keep it low and optional.

## 6. Designing an event step by step
1. State the goal and primary metric (see SKILL.md table).
2. Pick the segment: who sees it, who does not (new players protected from overload, payers not spammed with discount offers).
3. Choose the template and the twist (what is new to the player).
4. Define the player journey across the duration: first session, midpoint, last 24 hours, post-event.
5. Set reward budget and structure (section 7).
6. Set difficulty and effort tiers (section 8).
7. Set duration and timing (section 9).
8. Model economy impact (section 10).
9. Define telemetry and success criteria (section 11).
10. Write the config and the spec (section 14).
11. QA: functional, economy sim, localization, edge cases (timezone changes, offline play, app update mid-event).
12. Launch with monitoring and a rollback plan.
13. Review (section 15).

## 7. Reward design
- Budget rewards in "economy units" (for example, soft-currency equivalents) per tier; track the total injected per player.
- Reward types and their risk:
| Reward | Value | Risk |
|---|---|---|
| Soft currency | Flexible | Inflation if unbounded |
| Premium currency (small) | Highly motivating | Devalues the store; keep small and finite |
| Consumables | Short-lived | Hoarding, but safe |
| Permanent power | Strong | Power creep, unfairness to late joiners |
| Cosmetics | Expression, scarcity | Best exclusive anchor; never pay-to-win |
| Time-skips | Convenience | Cannibalize IAP if too generous |
| Titles, badges | Status | Cheap, durable |
- Anchor reward: one visible exclusive (cosmetic, ideally returning later in the shop with an indicator, so FOMO is not absolute).
- Front-load a small reward so players feel progress immediately; place the biggest reward at the end but ensure mid-track rewards exist every few steps.
- Catch-up mechanics for late joiners.
- Do not make rewards depend on spending unless it is a clearly labelled paid lane.
- Premium lane rewards should include some value that is not a competitive advantage.

## 8. Difficulty and effort tuning
- Define effort in minutes of play: casual, core, hardcore players have different weekly playtime; derive from analytics (`player-analytics`).
- Target completion curve (example intention, to be tuned): hardcore players complete early with slack, core players complete near the end, casual players reach a satisfying midpoint reward.
- Check with a model: `time_to_complete = total_points / (points_per_session x sessions_per_day)`; compare against duration.
- If challenge content: provide difficulty tiers or assist options so players of different skill can progress; reward scales with tier.
- Avoid forced daily attendance for the main reward; allow batching (a limited banked-quest system) to respect real lives.

## 9. Duration and timing
- Short (a few days): high urgency, low fatigue, good for simple mechanics.
- Medium (one to two weeks): standard events; allows slower players to finish.
- Long (several weeks): seasons; need internal milestones so players do not feel nothing happens.
- Start times: align with player timezones; avoid starting in the middle of the night for the main market; consider rolling local starts for fairness in non-competitive events, and fixed UTC for competitive ones.
- End: announce a countdown; honor a grace window for in-progress activity; no silent early end.
- Spacing: a rest day or two between big events; do not overlap two big reward events that compete for the same behavior.

## 10. Economy impact modelling
Procedure:
1. List all reward sources in the event with quantities by tier.
2. Estimate participation and completion rates by segment (from past events or assumptions flagged as such).
3. Compute expected injection: `sum over tiers of reward x P(reach tier)`.
4. Compare with the weekly baseline source and sink totals per segment.
5. Simulate in `${CLAUDE_PLUGIN_ROOT}/scripts/economy_sim.py` with event rewards added; check balances after several weeks of repeated events.
6. Decide sink actions: new shop items, upgrade costs, limited cosmetic store.
7. Add a monitoring metric: average soft-currency balance by cohort; alert on drift.
Rule: if an event injects more than a small share of the weekly baseline of a critical currency, treat it as an economy change and review it with `economy-design`.

## 11. Measurement plan
Metrics by funnel stage: eligible -> exposed -> started -> mid-progress -> completed -> claimed -> purchased (if any).
Core comparisons:
- Participation rate among DAU during the event.
- Completion rate by segment.
- Incremental DAU, sessions per DAU, retention and revenue vs holdout or prior comparable period.
- Post-event hangover: do metrics fall below baseline afterward?
- Reward cost per participant.
- Support tickets and sentiment.
Attribution cautions: events overlap with updates, UA bursts and seasonality; holdout or staggered rollout is the clean method. For tests use `ab_test.py` for sample size.
Event names for telemetry should follow the project taxonomy (`event_taxonomy.py` validates names and parameters).

## 12. Worked example: collection event
Goal: deepen engagement of core players for ten days; secondary: cosmetic monetization.
- Mechanic: complete levels to earn stamps; trade stamps for set pieces; completing the set gives an exclusive frame.
- Effort: a core player plays about N levels per day (from analytics); set cost designed so a core player completes by day eight, casual by day ten only with consistent play, hardcore day five.
- Rewards: soft currency at each piece, a booster at midpoint, the exclusive at the end; a paid lane adds extra cosmetic pieces (no power).
- Economy: injection modeled at a moderate share of weekly baseline; sink: cosmetic shop opens.
- Measurement: holdout of a modest share of players with no event; primary metric sessions per DAU; guardrails: soft-currency balance, D7 retention, refund rate.
- Exit criteria: if participation among core below target after day three, adjust difficulty by config and notify.

## 13. Worked example: tournament
Goal: competitive engagement for a weekend.
- Brackets of players by trophy range, each bracket a modest number of players; ranks pay out by band.
- Points per match; server validates scores; ties by earlier achievement time.
- Rewards: participation chest, bracket rewards, exclusive trophy.
- Safeguards: bots fill brackets when needed, disclosed if required; reports and suspicious-score flags.
- Measurement: participation, matches per participant, retention among participants vs non-participants (with selection-bias caution), negative feedback in the lowest ranks; adjust bracket sizing and reward floors.

## 14. Event spec template
```yaml
event_id: collection_spring_01
goal: deepen
primary_metric: sessions_per_dau
segment: { min_level: 10, exclude: [new_players_d0_3] }
template: collection
start_utc: "set at schedule time"
end_utc: "set at schedule time"
display_timezone: local
tiers: [ {id: 1, points: 50, reward: soft_currency_200}, ... ]
paid_lane: { price_tier: low, rewards: cosmetic_only }
economy: { injected_per_completer: "from simulation", sinks_added: [cosmetic_shop_set_01] }
telemetry: [event_start, task_progress, reward_claimed, event_complete, purchase_event_lane]
holdout_pct: 10
rollback: "disable via remote config key events.collection_spring_01.enabled"
client_min_version: "set to the build that supports template v2"
owner: liveops-manager
```

## 15. Post-event review
Within a few days after the event:
1. Results vs goal and success criteria.
2. Economy: injected vs planned; balance drift.
3. Segment breakdown: who benefited, who bounced.
4. Qualitative: community sentiment, support themes.
5. Operational: incidents, config changes during event, slippage.
6. Decision: repeat as is, repeat with changes, retire, convert to evergreen.
7. Update templates and the calendar.

## 16. Failure patterns
- All events are discounts: players learn to wait. Balance with content events.
- Rewards power creep: late joiners cannot catch up. Provide catch-up or convert to cosmetics.
- Overly tight timers: casual players feel excluded; introduce flexible tiers.
- Event fatigue: team and players burn out; schedule rest and reuse content.
- No telemetry planned: results arrive with no interpretation. Plan telemetry before building.
- Too much hidden complexity: events with many sub-systems that confuse; keep one clear goal and a one-line explanation.
