# Casual, social and simulation case studies

Sixteen deconstructions of games whose engine is other people, the clock, or both. The set spans the slot-adjacent social loop (Coin Master and its board-game descendant Monopoly Go!), production and farming sims (Hay Day, Township), merge-2 boards (Merge Mansion, Travel Town), cosy and life sims (Animal Crossing: Pocket Camp, The Sims FreePlay), platforms and sandboxes (Roblox, Minecraft), social deduction (Among Us), interactive fiction (Episode and Choices), asynchronous and short-session PvP (Words With Friends, 8 Ball Pool, Golf Clash), and the most-studied gamified non-game (Duolingo). Read the file as a study of three engines: **timers** that turn absence into anticipation, **social obligation** that turns other players into reasons to return, and **collection** that turns randomness into goals. Each case uses the 16-lens format from `SKILL.md` and ends with an ontology encoding in the contract field names (`loops[].steps[]`, `economy.currencies[]`). Currency `kind` follows the `SKILL.md` conventions (`premium` = purchasable, even if also earnable). Revenue figures are left out. Mechanics are described as publicly observable in shipped builds; event names, timer values and caps change often in live games and are marked "verify". Market and regulatory facts that move are collected in section 18 with sources.

**Contents.** Sections 1–16 are case studies (index below). Section 17 is a cross-case synthesis with decision tables and checklists. Section 18 lists volatile facts with sources.

| # | Game | Genre | Year | Key lesson |
|---|---|---|---|---|
| 1 | Monopoly Go! | board-dice social casual | 2023 | A proven social loop transplants to a new IP when the IP adds a native mechanic (board position), not just a skin |
| 2 | Coin Master | slot-adjacent social casual | 2016 (breakout 2018–19) | Real friends as attack targets make a viral loop; a slot core is also the sharpest ethical and regulatory edge in casual |
| 3 | Hay Day | farming production sim | 2012 | Forgiving timers + interlocking production chains + player trade sustain a decade of retention |
| 4 | Township | farm + town builder | 2011 web, mobile later | Breadth by stacking many light loops (orders, transport, zoo, co-ops) on one production core |
| 5 | Merge Mansion | merge-2 + mystery story | c. 2020 | A merge board needs a narrative "why"; the mystery doubles as the marketing hook |
| 6 | Travel Town | merge-2 + orders | c. 2021 | Order boards make merge goal-directed; energy is the single pacing and monetization knob |
| 7 | Animal Crossing: Pocket Camp | cosy life sim | 2017 (service ended 2024) | Cosy IP loops survive on mobile; ending a service with an offline edition is a model sunset |
| 8 | Among Us | social deduction | 2018 (breakout 2020) | When players generate the content, streamers become the distribution |
| 9 | Roblox | UGC platform | 2006 (mobile 2012) | Platform economics: creator payouts, one currency, discovery; safety is a core feature, not a policy page |
| 10 | Minecraft | sandbox survival / creative | 2009 (mobile 2011) | A systemic sandbox with self-set goals; premium plus a creator marketplace |
| 11 | The Sims FreePlay | life sim | 2011 | Real-time action timers as session design, and where they stop being fun |
| 12 | Episode / Choices | interactive story | 2014 / 2016 | Monetizing choices instead of power; chapter energy; UGC writing at scale |
| 13 | Words With Friends | async word PvP | 2009 | Async turns + push notifications = an always-on social obligation |
| 14 | 8 Ball Pool | real-time sports PvP | c. 2010 web, mobile later | Stakes-based matchmaking is progression, sink and drama in one rule |
| 15 | Golf Clash | 1v1 sports PvP | 2017 | Simultaneous short 1v1 timing duels; chest timers transplanted from Clash Royale |
| 16 | Duolingo (gamification) | gamified learning | 2012 | Streaks, leagues and notification science as a retention engine, with honest limits |

---

## 1. Monopoly Go!

**Snapshot**
- Developer: Scopely (Los Angeles), under licence from Hasbro. Savvy Games Group agreed to acquire Scopely for $4.9B in April 2023 (reported; [PocketGamer.biz](https://www.pocketgamer.biz/how-savvy-aims-to-grow-its-games-empire-after-3-5bn-niantic-deal)).
- Release: worldwide April 2023, after an extended soft launch.
- Genre: board-dice social casual, often grouped with "social casino" because it shares the slot-style loop, although there is no real-money wagering or payout. Business model: free-to-play, IAP-led.
- Scale: widely reported as one of the fastest-grossing mobile launches of 2023, supported by very large marketing spend. Revenue figures are omitted (see `market-intel` for current data).

**Core loop**
1. Choose a roll multiplier (×1 by default). Higher multipliers unlock as the dice balance grows; each multiplies both dice cost and payout.
2. Roll two dice; the token moves around a Monopoly-style board.
3. Resolve the tile: cash from properties and passing Go, Chance and Community Chest draws, tax, jail, and railroads that trigger a **Shutdown** (damage another player's landmark) or a **Bank Heist** (pick vaults to steal cash) against another player.
4. During events, marked tiles pay event points that fill a milestone track (dice, cash, sticker packs, event tokens).
5. Spend cash to build and upgrade the current board's landmarks. Completing every landmark finishes the board, raises net worth and opens the next themed board.
6. When dice run out: wait for regeneration, claim gifts and quick-win tasks, buy dice, or return when an event refills them.

**Meta and progression**
- Themed boards with escalating landmark costs; net worth as the long-term score.
- **Sticker albums** run in seasons. Packs come from events, landmarks and the shop. Stickers carry a 1–5 star rarity; sets pay dice and cash; a full album pays a large prize. Duplicates feed a secondary reward vault (verify the current mechanic).
- **Golden stickers** can be traded only during short "Golden Blitz" windows, so scarcity is time-boxed rather than permanent.

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Dice rolls | energy | timed regeneration (capped), gifts, invites, quick wins, events, IAP | each roll × multiplier |
| Cash | soft | tiles, passing Go, heists, shutdowns, events | landmarks |
| Sticker packs / stickers | material | events, landmarks, shop bundles | set and album completion |
| Shields | material | shield tile results | absorb incoming shutdowns (small cap) |
| Event tokens (e.g., prize-drop tokens) | event | milestones, shop | event mini-games (expire with the event) |

There is no separate premium currency in the shop as commonly observed: offers sell dice, cash and packs directly for real money (verify the current build). This removes the gem-conversion step from every purchase decision.

**Monetization**: dice bundles with cash and sticker packs, time-limited offers keyed to the running event, event-token packs, and pass-style products (verify the current names). Spending clusters at two moments: when an event milestone is in reach, and late in an album season when few stickers are missing.

**Live-ops**: one of the densest calendars in mobile. A multi-day main event runs alongside short leaderboard tournaments, flash boosts (higher multipliers, boosted heists, cash and rent boosts, sticker booms), cooperative partner events and album seasons with Golden Blitz windows. Event names rotate; verify before citing.

**Retention hooks**: the dice regeneration appointment; overlapping event timers so something is always about to pay out; near-complete sticker sets; partner obligations; revenge after being shut down or robbed.

**Social layer**: friends via Facebook, contacts or invite links; shutdowns and heists against friends and strangers, with revenge options; **partner events** in which a small fixed group (up to four partners; verify) builds a shared project; sticker trading and gifting. Off-platform Facebook groups and Discord servers organise trades, and grey markets for stickers and accounts have appeared around them.

**UX and onboarding notables**
- Board-game literacy means almost nothing needs teaching: a single large Go button, hold-to-auto-roll, and fast token animations.
- The multiplier selector sits next to the Go button, so stake size is a one-tap decision every roll.
- Community strategy shows the design's hidden depth: players raise the multiplier when the token is a few tiles from a high-value event tile, turning a random roll into a timing decision.

**Art and audio identity**: glossy, toy-like 3D boards, the Mr. Monopoly mascot and classic tokens, city-themed landmarks, and slot-style celebration audio with cash showers.

**Psychology principles used**: variable-ratio reinforcement from dice outcomes (Skinner); illusion of control from the multiplier choice (Langer, 1975); goal-gradient and Zeigarnik pull from nearly complete sticker sets; time-boxed scarcity in Golden Blitz windows (Cialdini); reciprocity through gifts and partner contributions; loss aversion when shields fail; social comparison through net worth.

**Innovations (at the time)**
- Moved the Coin Master loop (spin → attack/raid → build) onto a board, where **position** matters. The board gives a random roll a spatial context that players can reason about.
- Brought cooperative partner events into the slot-adjacent loop, adding a positive-sum social layer to an otherwise adversarial one.
- Ran sticker albums with time-boxed trading of the rarest tier at very large scale.
- Combined a universally known board-game IP with this loop, widening the audience to players who would not install a slot-style game.

**Weaknesses and criticism**
- The multiplier is a stake bet in all but name. Critics call the loop slot-like, and press coverage in 2024 described very large spending by a minor. This is the key ethical issue for anyone copying the loop (`legal-ethics`).
- Completing an album depends on rare stickers, which concentrates spending at the end of the season and feeds grey markets for stickers and accounts.
- Event overload: overlapping timers create urgency fatigue.
- The core offers little agency, and success depended on very large user-acquisition and brand spend.

**Lessons for designers**
1. A mature social loop transfers to a new theme only if the theme adds a mechanic native to it (board position), not just a skin.
2. If you offer a stake choice, make it a decision (timing it before a reward tile), and put guardrails around it: spend limits, age gating, no stake multipliers for minors.
3. Layer events so one timer is always near its payout, but cap simultaneous events (three or four is plenty) to avoid fatigue.
4. Collections need a trading valve. Build in-game trading windows rather than leaving players to grey markets, and disclose rarity odds.
5. Pair adversarial social actions (heists) with cooperative ones (partners) so the social graph does not turn sour.

**Analogy hooks**
- Multiplier timing before reward tiles → any roll- or spin-based resolver (dice RPGs, racing boosts, idle "multiplier" buttons).
- Partner events (a fixed group of four co-building) → farming, merge and puzzle metas.
- Time-boxed trading of the rarest tier → any collection game that wants scarcity without permanent exclusivity.
- Board movement as a reward resolver → match-3 meta maps, roguelite map nodes.

**Ontology encoding**
```json
{"loops": [
  {"id": "mgo_core", "type": "core", "period": "seconds", "steps": [
    {"id": "c1", "action": "choose_multiplier_and_roll", "reward": "token_moves", "next": "c2"},
    {"id": "c2", "action": "resolve_tile", "reward": "cash_cards_or_minigame", "next": "c3"},
    {"id": "c3", "action": "shutdown_or_heist_target", "reward": "stolen_cash", "next": "c4"},
    {"id": "c4", "action": "collect_event_points", "reward": "milestone_dice_packs", "next": "c1"}]},
  {"id": "mgo_meta", "type": "meta", "period": "session", "steps": [
    {"id": "m1", "action": "spend_cash_on_landmarks", "reward": "net_worth", "next": "m2"},
    {"id": "m2", "action": "complete_board", "reward": "new_board_and_prizes", "next": "m3"},
    {"id": "m3", "action": "open_packs_complete_sticker_sets", "reward": "set_prizes", "next": "m1"}]},
  {"id": "mgo_social", "type": "social", "period": "weekly", "steps": [
    {"id": "s1", "action": "join_partner_event", "reward": "shared_project_slot", "next": "s2"},
    {"id": "s2", "action": "contribute_event_tokens", "reward": "partner_milestones", "next": "s3"},
    {"id": "s3", "action": "trade_stickers_in_golden_window", "reward": "set_completion", "next": "s1"}]}],
 "economy": {"currencies": [
  {"id": "dice", "kind": "energy", "sources": ["regen", "gifts", "quick_wins", "events", "iap"], "sinks": ["roll_times_multiplier"], "cap": null},
  {"id": "cash", "kind": "soft", "sources": ["tiles", "pass_go", "heists", "shutdowns", "events"], "sinks": ["landmarks"], "cap": null},
  {"id": "stickers", "kind": "material", "sources": ["packs_from_events", "landmarks", "iap_bundles"], "sinks": ["set_completion"], "cap": null},
  {"id": "shields", "kind": "material", "sources": ["shield_tiles"], "sinks": ["blocked_shutdown"], "cap": null},
  {"id": "event_tokens", "kind": "event", "sources": ["milestones", "iap"], "sinks": ["event_minigame"], "cap": null}]}}
```
Caps are `null` because they are not published; measure them in the current build.

## 2. Coin Master

**Snapshot**
- Developer: Moon Active (Tel Aviv, founded in 2011 according to [Wikipedia](https://en.wikipedia.org/wiki/Moon_Active), which cites an investor-club source; other sources may say 2012).
- Release: 2016 on iOS and Android (Wikipedia's Moon Active article says January 2016 without a citation; the Coin Master article gives only the year, so the exact day is unconfirmed: [Coin Master](https://en.wikipedia.org/wiki/Coin_Master)). Global breakout around 2018–2019, driven by TV, celebrity and influencer campaigns. German media regulators (NRW and the KJM) concluded proceedings against Moon Active on 3 April 2020, with age-verification changes.
- Genre: slot-adjacent social casual (no real-money payouts). Business model: free-to-play, IAP-led.
- Scale: widely reported among the top-grossing casual games of 2019–2021. Revenue figures are omitted.

**Core loop**
1. Spin a three-reel slot machine. Each spin costs spins (energy) multiplied by the chosen bet.
2. Resolve the result: coins or coin bags; three hammers → **Attack** (damage a building in a target's village unless a shield blocks it); three pigs → **Raid** (dig spots in the current "Coin Master's" village to steal coins); shields; extra spins.
3. Spend coins to build and upgrade the five or so buildings of the current village.
4. Complete the village → move to the next themed village, where costs and rewards are higher.
5. Buy chests with coins for cards; complete card sets for spins and pet rewards.
6. Out of spins: wait for regeneration, collect friends' gifts and promotional free-spin links, or buy spins.

**Meta and progression**
- A long ladder of villages (hundreds by the mid-2020s; verify) with escalating costs, and a star count as the long-term score.
- Card collection: sets tied to village tiers; rarer gold cards are tradeable only during special trading events.
- Pets modify the core: Foxy adds a dig to raids, Tiger raises attack rewards, Rhino blocks attacks. Pets need food to stay active and XP potions to level (verify the current rules).

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Spins | energy | hourly regeneration to a cap (commonly cited as 5 per hour up to 50; verify), friend gifts, set rewards, events, IAP | each spin × bet |
| Coins | soft | slot results, attacks, raids, events | buildings, chests (raids also take coins away) |
| Cards | material | chests, events, trades | set completion |
| Pet food / XP potions | material | chests, events, set rewards | activating and levelling pets |
| Shields | material | slot results | block an attack (small cap) |

Like Monopoly Go!, the shop sells spins, coins and chests directly, with no intermediate gem currency (verify).

**Monetization**: spin packs, coin packs, chest bundles, and time-limited offers tied to events. Spending peaks during attack or raid events (when spins are worth more) and near village or set completion.

**Live-ops**: rotating events such as Attack Madness, Raid Madness, Village Master, card booms and secondary slot machines (e.g., a Viking-themed quest slot with its own bet). Card seasons and gold-card trading events act as the long calendar. Names rotate; verify before citing.

**Retention hooks**: spin regeneration; "you were attacked" notifications that invite revenge (loss aversion); free-spin links posted daily on official social channels; nearly complete card sets.

**Social layer**: connecting Facebook was central from the start: friends are gift sources, attack targets and revenge targets, and inviting friends pays spins. Card trading and gifting. Fan pages and sites aggregating daily spin links became a distribution channel in their own right.

**UX and onboarding notables**
- One large Spin button, autospin, a three-reel slot that anyone reads instantly, and mini-games (attack, raid) that last a few seconds.
- The first session reaches an attack and a raid within minutes, so the social premise is taught by doing.

**Art and audio identity**: bright cartoon Vikings, pigs and villages; slot-machine audio grammar (reel ticks, coin cascades, jackpot stingers).

**Psychology principles used**: variable-ratio reinforcement (Skinner); loss aversion from being attacked and raided (Kahneman and Tversky, 1979); social comparison and provocation via revenge (Festinger, 1954); reciprocity in gifting (Cialdini); illusion of control in the bet multiplier (Langer, 1975); Zeigarnik pull from incomplete sets.

**Innovations (at the time)**
- Combined a slot-machine core with a village-building meta and asynchronous attacks and raids on real friends, so the player's social graph became the content.
- Ran celebrity and influencer marketing at a scale unusual for a casual game.
- Established the template ("spin → attack/raid → build → collect") that Monopoly Go! later moved onto a board.

**Weaknesses and criticism**
- Simulated gambling accessible to minors. Regulators and consumer groups in several European countries scrutinised the game and its influencer marketing around 2019–2021 (verify specifics by jurisdiction). Australia's classification rules from September 2024 rate games with simulated gambling R18+ (section 18), so a slot core is a regulatory design decision, not just a theme.
- Low agency: outcomes are almost entirely random.
- Facebook dependence and aggressive notifications.
- Revenge loops can turn friendships sour.

**Lessons for designers**
1. Real people as targets create emotion that AI opponents cannot, but give defenders tools (shields, pets) so being attacked feels recoverable.
2. If you use a chance core, set the ethics line before tuning: no cash-out or real-money-like payouts, age gating, spend limits, odds disclosure, and no stake multipliers for minors.
3. A meta (villages) gives each spin result somewhere to go. Without it, a slot is only a slot.
4. Promotional free-spin links are a cheap re-engagement channel; plan them as part of the economy, not as an afterthought.

**Analogy hooks**
- Asynchronous attack and raid on friends' persistent bases → farming, kingdom and merge metas (as Clash of Clans does in `references/midcore-strategy.md`).
- Pets that modify core outcomes → idle games and RPGs (companions that alter drop rules).
- Event-weighted symbol value (attack events make hammers worth more) → any slot-like resolver, including roguelite reward tables.

**Ontology encoding**
```json
{"loops": [
  {"id": "cm_core", "type": "core", "period": "seconds", "steps": [
    {"id": "c1", "action": "spin_slot_with_bet", "reward": "symbol_result", "next": "c2"},
    {"id": "c2", "action": "attack_or_raid_target_village", "reward": "coins", "next": "c3"},
    {"id": "c3", "action": "build_or_upgrade_village_building", "reward": "village_progress_stars", "next": "c1"}]},
  {"id": "cm_meta", "type": "meta", "period": "daily", "steps": [
    {"id": "m1", "action": "complete_village", "reward": "next_village", "next": "m2"},
    {"id": "m2", "action": "open_chests_trade_cards", "reward": "set_progress", "next": "m3"},
    {"id": "m3", "action": "complete_card_set", "reward": "spins_pet_rewards", "next": "m1"}]},
  {"id": "cm_social", "type": "social", "period": "daily", "steps": [
    {"id": "s1", "action": "send_and_receive_spin_gifts", "reward": "spins", "next": "s2"},
    {"id": "s2", "action": "revenge_attack", "reward": "coins_and_satisfaction", "next": "s1"}]}],
 "economy": {"currencies": [
  {"id": "spins", "kind": "energy", "sources": ["regen_hourly", "friend_gifts", "set_rewards", "events", "iap"], "sinks": ["spin_times_bet"], "cap": null},
  {"id": "coins", "kind": "soft", "sources": ["slot", "attacks", "raids", "events"], "sinks": ["buildings", "chests"], "cap": null},
  {"id": "cards", "kind": "material", "sources": ["chests", "events", "trades"], "sinks": ["set_completion"], "cap": null},
  {"id": "pet_food", "kind": "material", "sources": ["chests", "events"], "sinks": ["pet_activation"], "cap": null},
  {"id": "shields", "kind": "material", "sources": ["slot"], "sinks": ["blocked_attack"], "cap": null}]}}
```

## 3. Hay Day

**Snapshot**
- Developer: Supercell (Helsinki).
- Release: iOS 2012, Android 2013.
- Genre: farming production sim. Business model: free-to-play, IAP-led (diamonds). Supercell has historically kept third-party ads out of its games; verify the current build.
- Scale: one of the longest-running top-grossing farming games. A Sensor Tower H1 2026 digest headlined a "Hay Day comeback" (section 18). Revenue figures are omitted.

**Core loop**
1. Plant crops (wheat grows in about two minutes; later crops take hours) and harvest by dragging the sickle across many fields in one gesture.
2. Feed animals with feed made at the feed mill to collect eggs, milk, wool and so on.
3. Process raw goods in production buildings (bakery, dairy, sugar mill and many more), each with a queue.
4. Fill orders: the truck order board (coins + XP), boat orders made of crates (neighbours can help fill them), and visitors.
5. Spend coins on buildings, animals and decorations; XP levels unlock new crops, buildings and products.
6. Manage storage: the barn (goods) and silo (crops) fill up and are upgraded with rare materials.

**Meta and progression**
- Player level gates the product tree. Land expansion needs rare tools (land deeds, mallets, marker stakes); barn and silo upgrades need another set (bolts, planks and duct tape for the barn; nails, screws and wood panels for the silo).
- Side systems unlock over time: fishing, a mine, a town with visitors and its own buildings, and a cooperative seasonal mode with neighbours (the Valley; verify current status).

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Coins | soft | truck orders, boat orders, roadside shop sales, visitors | buildings, animals, decorations, buying from other players |
| Diamonds | hard | IAP, achievements, mystery boxes, occasional rewards | speed-ups, missing items, extra slots, helpers |
| XP | xp | orders, harvesting, production | level unlocks |
| Expansion and storage tools | material | random drops from harvesting and orders, roadside shop, diamonds | land expansion, barn and silo upgrades |
| Crops and products | material | fields, animals, buildings | orders, production inputs, roadside shop |

**Monetization**: diamonds for speed-ups, missing ingredients, extra production and shop slots, and helpers who fetch items; a season pass ("Farm Pass"; verify). The game monetizes impatience and convenience rather than access.

**Live-ops**: the weekly neighbourhood **Derby** (task-based competition between neighbourhoods, with variants), seasonal events and decorations, and periodic boosts such as faster production or bonus yields (verify the names).

**Retention hooks**: production timers that players set before leaving ("set and return"), roadside shop sales that happen while away, boat departure deadlines, Derby tasks, and the never-finished order board.

**Social layer**: neighbourhoods (guilds with chat, help requests and the Derby); the **roadside shop**, a player-to-player market where sellers set prices within limits; a newspaper for browsing other players' shops; help on boat crates; farm visits.

**UX and onboarding notables**
- **Crops never wither.** FarmVille-era farming games punished absence by killing crops; Hay Day removed that, so absence costs opportunity, never assets.
- The drag-to-harvest and drag-to-plant gestures turn chores into pleasure on a touchscreen.
- Long-press shows remaining time; ready items show bubbles; early levels unlock quickly to teach one production chain at a time.

**Art and audio identity**: warm, hand-painted cartoon farm, expressive animals, crisp harvest pops and satisfying collection sounds; icons readable at small sizes.

**Psychology principles used**: IKEA effect and endowment from a farm the player arranged and decorated (Norton, Mochon and Ariely, 2012); Zeigarnik pull from unfinished orders; goal-gradient on the level bar; reciprocity in neighbourhood help; autonomy, competence and relatedness (Deci and Ryan) from choosing what to produce, running efficient chains, and belonging to a neighbourhood; commitment (planting is a promise to return).

**Innovations (at the time)**
- A mobile-native, touch-first farming game that removed punishment for absence (no withering).
- A player market with price limits that made other players sources and sinks without breaking the economy.
- No energy system: production timers and storage caps are the gate.

**Weaknesses and criticism**
- The mid-game slows as timers lengthen; storage pressure frustrates players who lack rare upgrade tools (which drop randomly).
- Diamond speed-ups monetize impatience; late-game production chains become long and repetitive.
- The pace can feel slow to players raised on faster merge and puzzle metas.

**Lessons for designers**
1. Make timers forgiving: absence should cost opportunity, never assets.
2. Interlocking production chains create self-generated goals ("I need cheese, so I need milk, so I need feed, so I need corn").
3. A player market with price caps turns other players into an economy while protecting it from abuse.
4. Storage caps are the main sink and upgrade gate. Model them explicitly (`economy_sim.py` pool and gate nodes).
5. A weekly cooperative competition (the Derby) gives guilds a heartbeat.

**Analogy hooks**
- Production chains with queues → merge games, idle tycoons, city builders, crafting RPGs.
- A player market with price limits → crafting economies in RPGs, trading in collection games.
- The Derby → any guild system that lacks a weekly rhythm.
- Batch gestures (drag-harvest) → any sim with repetitive collection.

**Ontology encoding**
```json
{"loops": [
  {"id": "hd_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "plant_and_drag_harvest_crops", "reward": "crops_xp", "next": "c2"},
    {"id": "c2", "action": "feed_animals_queue_production", "reward": "products", "next": "c3"},
    {"id": "c3", "action": "fill_truck_or_boat_order", "reward": "coins_xp", "next": "c4"},
    {"id": "c4", "action": "buy_building_or_expand", "reward": "new_production_options", "next": "c1"}]},
  {"id": "hd_social", "type": "social", "period": "weekly", "steps": [
    {"id": "s1", "action": "pick_derby_task", "reward": "task_slot", "next": "s2"},
    {"id": "s2", "action": "complete_task_for_neighbourhood", "reward": "derby_points", "next": "s3"},
    {"id": "s3", "action": "claim_derby_rewards", "reward": "tools_diamonds_boosts", "next": "s1"}]}],
 "economy": {"currencies": [
  {"id": "coins", "kind": "soft", "sources": ["truck_orders", "boat_orders", "roadside_sales", "visitors"], "sinks": ["buildings", "animals", "decor", "player_market_purchases"], "cap": null},
  {"id": "diamonds", "kind": "hard", "sources": ["iap", "achievements", "mystery_boxes"], "sinks": ["speed_ups", "missing_items", "slots"], "cap": null},
  {"id": "xp", "kind": "xp", "sources": ["orders", "harvest", "production"], "sinks": [], "cap": null},
  {"id": "storage_tools", "kind": "material", "sources": ["random_drops", "roadside_market", "diamonds"], "sinks": ["barn_silo_upgrades", "land_expansion"], "cap": null},
  {"id": "goods", "kind": "material", "sources": ["fields", "animals", "buildings"], "sinks": ["orders", "production_inputs", "roadside_shop"], "cap": null}]}}
```

## 4. Township

**Snapshot**
- Developer: Playrix.
- Release: on social networks around 2011, with mobile versions following (verify exact dates by platform).
- Genre: farming plus town building. Business model: free-to-play, IAP-led (T-cash), with optional rewarded placements in some builds (verify).
- Scale: a long-running top-grossing casual sim in Playrix's portfolio. Revenue figures are omitted.

**Core loop**
1. Grow crops and raise animals.
2. Process them in factories (bakery, dairy, sugar factory and many more) with queues.
3. Fill transport orders: the helicopter (small orders), the train (crates to fill and send between stations), and later planes and ships to islands.
4. Earn coins, XP and materials; build houses to raise population.
5. Build community buildings to raise the population cap, and factories and decorations to expand capability.
6. Expand land and upgrade the barn with tool items that drop from orders and production.

**Meta and progression**
- Player level and population both gate content. Population is capped by community buildings, so the town must grow in balance.
- Side areas unlock over time: a mine, a zoo (with its own collection and building), islands and expeditions, and seasonal mini-games. Later updates added a match-3 mode alongside the sim (verify the current name and gating).
- Co-ops (guilds) with chat and help, and **Regattas** (timed co-op competitions with tasks).

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Coins | soft | orders, market sales, events | buildings, factories, decor |
| T-cash | hard | IAP, level-ups, achievements, some events | speed-ups, missing items, premium buildings |
| XP | xp | orders, production | level unlocks |
| Population | xp | houses | gates new buildings and factories |
| Barn and expansion tools | material | random drops from orders and production, trade with co-op members | barn capacity, land expansion |
| Event tokens | event | seasonal events | event rewards (expire) |

**Monetization**: T-cash for speed-ups and missing items, bundles with exclusive buildings, a season pass (verify), and offers keyed to events.

**Live-ops**: seasonal events with themed decorations, Regattas on a regular cycle, zoo and island content drops, and mini-game events. Playrix runs a dense calendar across its portfolio.

**Retention hooks**: transport deadlines (the train returns, the plane leaves), production timers, Regatta tasks, population goals and the next building unlock.

**Social layer**: co-ops with help requests and Regattas; friend visits; requests for missing items.

**UX and onboarding notables**
- Every transport system is a visible, animated order board, so the player always sees what is needed next.
- Systems unlock gradually, one per few levels, which keeps the early game readable despite great final breadth.
- Playrix's user-acquisition creatives across the portfolio have often shown mini-games in the foreground. Homescapes' advertising ruling (`references/puzzle-casual.md` §3) is the cautionary precedent: any game shown in an ad must exist in the product.

**Art and audio identity**: bright, clean cartoon town, many small animated vehicles, and colourful UI with strong icons; light, cheerful audio.

**Psychology principles used**: goal-gradient on population and level bars; IKEA effect from town layout; Zeigarnik pull from transport orders; relatedness through co-ops; variety-seeking satisfied by many side systems.

**Innovations (at the time)**
- Merged farming and city building into one economy with several transport-order systems, each a distinct mini-loop with its own timer.
- Grew breadth over a decade by adding side systems (zoo, islands, mini-games) without changing the production core.

**Weaknesses and criticism**
- Feature sprawl: late-game players juggle many timers and screens; new players can feel lost.
- Storage pressure and random tool drops create slowdowns that push toward premium currency.
- Advertising across the genre has been criticised for showing mini-game content more than the core sim.

**Lessons for designers**
1. Several light order loops with different cadences (minutes, hours, days) keep a production sim fresh without new mechanics.
2. Gate expansion on balance (population needs community buildings) to create meaningful build-order choices.
3. Add side systems only when each has its own collection or goal (the zoo), and unlock them gradually.
4. If ads show a mini-game, make sure the mini-game is real and reachable early.

**Analogy hooks**
- Multiple transport-order systems with different cadences → idle tycoon and logistics games.
- Population capped by community buildings → any builder needing balanced growth (colony sims, kingdom metas).
- A side collection area (the zoo) → any sim that needs a long-term collection goal.

**Ontology encoding**
```json
{"loops": [
  {"id": "ts_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "grow_crops_raise_animals", "reward": "raw_goods", "next": "c2"},
    {"id": "c2", "action": "process_in_factories", "reward": "products", "next": "c3"},
    {"id": "c3", "action": "fill_helicopter_train_plane_orders", "reward": "coins_xp_tools", "next": "c4"},
    {"id": "c4", "action": "build_houses_and_community_buildings", "reward": "population_unlocks", "next": "c1"}]},
  {"id": "ts_social", "type": "social", "period": "weekly", "steps": [
    {"id": "s1", "action": "take_regatta_task", "reward": "task_slot", "next": "s2"},
    {"id": "s2", "action": "complete_task_for_coop", "reward": "regatta_points", "next": "s3"},
    {"id": "s3", "action": "claim_league_rewards", "reward": "tcash_tools_decor", "next": "s1"}]}],
 "economy": {"currencies": [
  {"id": "coins", "kind": "soft", "sources": ["orders", "market", "events"], "sinks": ["buildings", "factories", "decor"], "cap": null},
  {"id": "tcash", "kind": "hard", "sources": ["iap", "level_ups", "achievements"], "sinks": ["speed_ups", "missing_items", "premium_buildings"], "cap": null},
  {"id": "xp", "kind": "xp", "sources": ["orders", "production"], "sinks": [], "cap": null},
  {"id": "population", "kind": "xp", "sources": ["houses"], "sinks": [], "cap": null},
  {"id": "tools", "kind": "material", "sources": ["random_drops", "coop_trade"], "sinks": ["barn_upgrades", "expansion"], "cap": null},
  {"id": "event_tokens", "kind": "event", "sources": ["seasonal_events"], "sinks": ["event_rewards"], "cap": null}]}}
```
Population is gated by community buildings; the gate is a progression rule, not a currency sink, so it appears in `progression.tracks` in a full deconstruction.

## 5. Merge Mansion

**Snapshot**
- Developer: Metacore (Helsinki, founded 2018).
- Release: global around 2020 after soft launch (verify the exact date).
- Genre: merge-2 puzzle with a renovation meta and an episodic mystery story. Business model: free-to-play, IAP-led (gems, energy, bundles).
- Scale: widely reported as one of the leading merge games of the early 2020s, with unusually high-profile brand campaigns for a mobile game. Revenue figures are omitted.

**Core loop**
1. Tap a generator on the board (for example a toolbox or a garden item). Each tap costs energy and drops a low-tier item into a free cell.
2. Drag two identical items together to make one item of the next tier. Some high-tier items become generators themselves.
3. Deliver the specific items that characters and tasks request (shown beside the board).
4. Completed requests pay coins, XP and story progress. Renovation tasks restore areas of the mansion and its grounds (verify which currency each task costs in the current build).
5. A restored area plays a story beat and opens the next area and new generators.
6. When energy runs out: wait for regeneration, use level-up refills, or buy energy.

**Meta and progression**
- The mansion map, area by area, with an episodic mystery about Grandma Ursula's past, told through the protagonist Maddie.
- Player level (XP) gates generators and areas. Board space and storage slots are permanent upgrades.

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Energy | energy | timed regeneration (capped), level-ups, rewards, IAP | generator taps |
| Coins | soft | requests, selling items, events | renovation tasks, shop items (verify) |
| Gems | hard | IAP, rewards, some high-tier merges | energy, speed-ups, board and storage slots, missing items |
| XP | xp | requests, merges | level-ups (energy refills, unlocks) |
| Items on the board | material | generators | merges, requests |

**Monetization**: energy refills, gem packs, bundles with energy and items, extra storage, and event passes or event-specific offers (verify). The highest-intent moment is "one item missing for a task" with no energy left.

**Live-ops**: limited-time events with their own boards, generators and mini-stories; seasonal themes; new mansion areas and story episodes on a cadence.

**Retention hooks**: energy regeneration (the main appointment), the next story beat (a cliffhanger mystery), nearly finished tasks, and event deadlines.

**Social layer**: minimal in the core. Merge games of this generation are largely single-player; social pressure comes from marketing and community discussion of the mystery rather than in-game teams.

**UX and onboarding notables**
- The merge verb is learned in seconds: drag identical items together. Highlighting of mergeable pairs reduces search effort.
- **Board space is the real puzzle**: generators, half-merged chains and requested items compete for cells, so planning which chains to keep is the skill.
- The story is delivered in short dialogue beats between tasks, so narrative never blocks play for long.

**Art and audio identity**: warm, detailed 2D item art with clear tier progressions (each tier visibly "more" than the last), a slightly eccentric cast, and cosy-mystery music. Brand campaigns built around the question of what Grandma is hiding became a recognisable identity (verify specific campaigns and cast).

**Psychology principles used**: curiosity and the information gap (Loewenstein, 1994) from the mystery; Zeigarnik pull from unfinished tasks and episodes; goal-gradient on area restoration; the completion pleasure of tier chains; endowed progress from the restored mansion.

**Innovations (at the time)**
- Paired a merge-2 board (merge boards had been popularised by merge-3 games such as Merge Dragons!, 2017) with a renovation meta and a continuing mystery narrative, applying the Homescapes recipe (puzzle core + renovation + story) to merge.
- Treated narrative as a marketing asset: the mystery became the hook of the brand campaigns, not just the in-game reason for tasks.

**Weaknesses and criticism**
- Energy gating stops binge play; late-game item chains need many taps, so energy spending rises sharply.
- Board clutter frustrates; storage upgrades feel mandatory.
- Merge boards are hard to differentiate: theme and story carry most of the identity.

**Lessons for designers**
1. A merge board needs a "why": requests and a story arc make merges goal-directed.
2. Board space is your difficulty and monetization knob. Tune the cell count and storage before you tune energy.
3. Know the merge arithmetic. Merge-2 needs 2^(n−1) tier-1 items for one tier-n item (32 for tier 6). Price energy against that curve, not against tap counts alone.
4. Deliver story in short beats between tasks; never block play with long cutscenes.
5. Let the narrative hook carry the marketing, but keep ad content true to the game.

**Analogy hooks**
- Mystery narrative over a puzzle board → match-3, sort and solitaire metas.
- Generators that are themselves merge products → crafting RPGs, idle games (machines that make machines).
- Board space as the core constraint → inventory-management puzzles and backpack roguelites.

**Ontology encoding**
```json
{"loops": [
  {"id": "mm_core", "type": "core", "period": "seconds", "steps": [
    {"id": "c1", "action": "tap_generator", "reward": "low_tier_item", "next": "c2"},
    {"id": "c2", "action": "merge_identical_items", "reward": "higher_tier_item", "next": "c3"},
    {"id": "c3", "action": "deliver_requested_item", "reward": "coins_xp_story_progress", "next": "c1"}]},
  {"id": "mm_meta", "type": "meta", "period": "session", "steps": [
    {"id": "m1", "action": "complete_renovation_task", "reward": "area_restored", "next": "m2"},
    {"id": "m2", "action": "watch_story_beat", "reward": "mystery_reveal", "next": "m3"},
    {"id": "m3", "action": "unlock_next_area", "reward": "new_generators_requests", "next": "m1"}]}],
 "economy": {"currencies": [
  {"id": "energy", "kind": "energy", "sources": ["regen", "level_up", "rewards", "iap"], "sinks": ["generator_tap"], "cap": null},
  {"id": "coins", "kind": "soft", "sources": ["requests", "sell_items", "events"], "sinks": ["renovation_tasks", "shop"], "cap": null},
  {"id": "gems", "kind": "hard", "sources": ["iap", "rewards"], "sinks": ["energy", "storage_slots", "speed_ups"], "cap": null},
  {"id": "xp", "kind": "xp", "sources": ["requests", "merges"], "sinks": [], "cap": null}]}}
```

## 6. Travel Town

**Snapshot**
- Developer: Magmatic Games (London). Moon Active acquired the studio in 2021 according to PitchBook (11 August 2021) and the investor Creandum; one analyst article says 2022, and no press release was found, so treat the year as 2021 and unconfirmed ([PitchBook](https://pitchbook.com/profiles/company/56284-48); [Creandum](https://www.creandum.com/commitments/magmatic-games)).
- Release: around 2021 (not verified).
- Genre: merge-2 puzzle with an order board and a town-building meta. Business model: free-to-play, IAP-led (energy, gems, bundles), with rewarded placements in some builds (verify).
- Scale: widely reported as a leading merge title in the mid-2020s. Revenue figures are omitted.

**Core loop**
1. Tap generators (each tap costs energy) to drop items onto the board.
2. Merge identical items into higher tiers.
3. Fulfil **orders** from townspeople shown at the top of the board; each names one or more specific items.
4. Orders pay coins and XP (and sometimes other rewards).
5. Spend coins on town buildings and decorations; XP levels unlock new generators and refill energy.
6. Out of energy: wait, claim rewards, or buy energy.

**Meta and progression**
- Themed town areas built up piece by piece; a travel framing with new locations over time (verify the current structure).
- Generator tiers and level-gated item chains: new chains add new order types.

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Energy | energy | timed regeneration (capped), level-ups, rewards, IAP | generator taps |
| Coins | soft | orders, events | town buildings, decor |
| Gems | hard | IAP, rewards | energy, board space, speed-ups, bubbles (verify) |
| XP | xp | orders | level-ups |
| Items | material | generators, chests | merges, orders |

**Monetization**: energy is the product. Energy packs, gem packs and bundles; event passes or offers (verify). The design question for every merge game is the **energy price of one order**:

```
items_needed(tier n, merge-2) = 2^(n-1) tier-1 items
taps_per_order ≈ Σ over requested items of 2^(n_i - 1) / items_per_tap
energy_per_order = taps_per_order × energy_per_tap
minutes_of_regen_per_order = energy_per_order × regen_minutes_per_energy
```
Illustrative (not measured): an order for one tier-5 and one tier-4 item from generators that drop one tier-1 item per tap costs 16 + 8 = 24 taps. At one energy per tap and two minutes of regeneration per energy, that is 48 minutes of waiting, about one appointment. Generators that sometimes drop tier-2 items cut the cost, which is the main tuning knob.

**Live-ops**: limited-time events with separate boards or collection tracks, seasonal themes, and regular content (new areas, chains).

**Retention hooks**: energy regeneration, the always-visible order queue, area completion, and event deadlines.

**Social layer**: light; some friend features and events (verify). Like most merge-2 titles, it is primarily single-player.

**UX and onboarding notables**
- Orders sit at the top of the board, so the goal is always on screen; hints point to the next mergeable pair.
- Item chains are visually themed, so tier order can be guessed without memorising.

**Art and audio identity**: bright, clean 2D items and characters, holiday-postcard warmth, and light, upbeat audio with satisfying merge pops.

**Psychology principles used**: goal-gradient (orders nearly done), Zeigarnik (open orders), completion satisfaction of tier chains, and variable reward from occasional higher-tier drops.

**Innovations (at the time)**
- Not a new mechanic. It refined the merge-2 plus orders formula with tight pacing, a readable order queue and generous early energy, the "speed and polish" strategy that Royal Match applied to match-3.

**Weaknesses and criticism**
- Energy is the only throttle, so late-game orders become energy-expensive and push spending.
- Low differentiation from other merge-2 titles; board clutter.

**Lessons for designers**
1. Show the goal on the board at all times (order cards), and let hints find merges.
2. Tune energy cost per order with the merge arithmetic above, and set a target of one to two orders per regeneration cycle for non-payers.
3. Generator drop tables (chance of tier-2 or tier-3 drops) are a better difficulty knob than raw energy prices.
4. In a crowded subgenre, compete on pacing and polish, not features.

**Analogy hooks**
- Order queues → idle tycoon, cooking and farming games (Hay Day's truck board is the ancestor).
- Generator drop tables → loot tables in RPGs, spawn weights in match-3.
- Energy-per-goal arithmetic → any energy-gated game.

**Ontology encoding**
```json
{"loops": [
  {"id": "tt_core", "type": "core", "period": "seconds", "steps": [
    {"id": "c1", "action": "tap_generator", "reward": "item", "next": "c2"},
    {"id": "c2", "action": "merge_items", "reward": "higher_tier_item", "next": "c3"},
    {"id": "c3", "action": "fulfil_townsperson_order", "reward": "coins_xp", "next": "c1"}]},
  {"id": "tt_meta", "type": "meta", "period": "daily", "steps": [
    {"id": "m1", "action": "spend_coins_on_town_buildings", "reward": "area_progress", "next": "m2"},
    {"id": "m2", "action": "level_up", "reward": "new_generators_energy_refill", "next": "m3"},
    {"id": "m3", "action": "wait_for_energy_regen", "reward": "energy", "next": "m1"}]}],
 "economy": {"currencies": [
  {"id": "energy", "kind": "energy", "sources": ["regen", "level_up", "rewards", "iap"], "sinks": ["generator_tap"], "cap": null},
  {"id": "coins", "kind": "soft", "sources": ["orders", "events"], "sinks": ["town_buildings", "decor"], "cap": null},
  {"id": "gems", "kind": "hard", "sources": ["iap", "rewards"], "sinks": ["energy", "board_space", "speed_ups"], "cap": null},
  {"id": "xp", "kind": "xp", "sources": ["orders"], "sinks": [], "cap": null}]}}
```

## 7. Animal Crossing: Pocket Camp

**Snapshot**
- Developer and publisher: Nintendo.
- Release: Australia on 25 October 2017, worldwide on 21 November 2017 ([Wikipedia](https://en.wikipedia.org/wiki/Animal_Crossing:_Pocket_Camp)). The online service ended on 28 November 2024. Nintendo then released a paid, offline edition, *Animal Crossing: Pocket Camp Complete*, on 2 December 2024. Players could transfer save data from the original app until 1 June 2025 ([Nintendo](https://www.nintendo.com/us/whatsnew/mobilenews-animal-crossing-pocket-camp-complete-is-now-available/)). Nintendo's page states an introductory price until 30 January 2025 but not the amount; Wikipedia gives a US list price of $19.99 with a $9.99 introductory price, a claim it flags as uncited, so confirm the price on the store.
- Genre: cosy life sim with collection and decoration. Business model: free-to-play with IAP (Leaf Tickets), later a subscription ("Pocket Camp Club"), then premium for the Complete edition.
- Scale: a large global launch on the strength of the IP. Revenue figures are omitted.

**Core loop**
1. Visit recreation areas and gather: shake trees for fruit, catch fish and bugs, collect shells.
2. Give animal visitors the items they request; earn friendship, crafting materials and Bells.
3. Craft furniture at the workshop, which takes materials, Bells and real time.
4. Decorate the campsite; animals whose requested furniture is placed can be invited to stay.
5. Raise friendship levels to unlock new animals, furniture and clothing.

**Meta and progression**
- Player level and per-animal friendship levels; furniture and clothing collections; campsite and camper (cabin) customisation.
- Recurring gardening and fishing or bug events with their own items and timed goals.

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Bells | soft | selling items, requests, events | crafting, clothing, upgrades |
| Leaf Tickets | hard | IAP, level-ups, goals, events | crafting speed-ups, missing materials, fortune cookies, event shortcuts |
| Crafting materials (cotton, wood, steel, paper, preserves, essences) | material | animal requests, events | crafting |
| Friendship | xp | gifts, requests | animal level unlocks |
| Event items (flowers, gyroid parts and the like) | event | event activities | event rewards (expire) |

**Monetization**: Leaf Tickets for speed and materials; **fortune cookies** (randomised bundles of exclusive items, bought with Leaf Tickets) from 2018; a monthly subscription from 2020 that added helpers and storage (verify tiers); after the sunset, a one-time purchase for the offline edition.

**Live-ops**: frequent garden events, fishing and bug tourneys, seasonal and holiday events, and new animals and furniture series, run throughout the live service.

**Retention hooks**: crafting timers, real-world day cycles and daily goals, animal requests that refresh, and event deadlines, all inherited from the series' real-time clock.

**Social layer**: friend lists, visiting campsites and giving kudos, watering friends' flowers during garden events, and a market box for selling items to friends.

**UX and onboarding notables**
- The franchise's cosy tone and characters carry onboarding: requests are small, failure does not exist, and goals are framed as favours.
- Portrait one-hand play; tap-to-move; animated requests make each goal concrete.

**Art and audio identity**: faithful Animal Crossing art and audio (animalese speech, soft acoustic music), simplified for phones.

**Psychology principles used**: relatedness with characters (SDT); IKEA effect from the campsite; collection completion; low-stakes competence; reciprocity framed as friendship. Fortune cookies introduced variable-ratio rewards into a non-competitive game.

**Innovations (at the time)**
- An early major Nintendo IP adaptation as a free-to-play mobile service: the series' real-time cosiness mapped onto mobile timers and daily goals.
- **The sunset**: rather than just shutting down, Nintendo released a paid offline edition with the content preserved and an option to transfer data (verify the window). It is one of the clearest examples of a service ending with respect for player investment.

**Weaknesses and criticism**
- Fortune cookies were criticised as loot boxes in a game marketed to all ages; cosmetics behind random paid draws clash with the series' spirit.
- The core became repetitive; the depth of the console series (town ownership, museum, community) was missing.
- A live service with evergreen IP still ended, a reminder that F2P services have finite lives.

**Lessons for designers**
1. A cosy IP can carry a gentle timer economy, but the core needs depth beyond requests and crafting.
2. Random paid cosmetics in an all-ages cosy game cause backlash out of proportion to their revenue; prefer direct purchase.
3. Plan the sunset at launch: a paid or free offline edition with save transfer protects players and the brand.
4. Subscriptions for convenience (helpers, storage) are a gentler fit for cosy audiences than random draws.

**Analogy hooks**
- Requests as friendship → any sim with NPCs (farming, merge, cooking).
- Furniture-based NPC invites (place what they like) → decoration metas in puzzle games.
- An offline "complete" edition at end of service → any live game with a loyal audience.

**Ontology encoding**
```json
{"loops": [
  {"id": "acpc_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "gather_fruit_fish_bugs", "reward": "items", "next": "c2"},
    {"id": "c2", "action": "fulfil_animal_requests", "reward": "materials_bells_friendship", "next": "c3"},
    {"id": "c3", "action": "craft_furniture_with_timer", "reward": "furniture", "next": "c4"},
    {"id": "c4", "action": "decorate_and_invite_animals", "reward": "friendship_unlocks", "next": "c1"}]},
  {"id": "acpc_liveops", "type": "liveops", "period": "weekly", "steps": [
    {"id": "l1", "action": "join_garden_or_fishing_event", "reward": "event_items", "next": "l2"},
    {"id": "l2", "action": "complete_event_goals", "reward": "exclusive_furniture", "next": "l1"}]}],
 "economy": {"currencies": [
  {"id": "bells", "kind": "soft", "sources": ["sell_items", "requests", "events"], "sinks": ["crafting", "clothing"], "cap": null},
  {"id": "leaf_tickets", "kind": "hard", "sources": ["iap", "level_ups", "goals"], "sinks": ["speed_ups", "materials", "fortune_cookies"], "cap": null},
  {"id": "materials", "kind": "material", "sources": ["animal_requests", "events"], "sinks": ["crafting"], "cap": null},
  {"id": "friendship", "kind": "xp", "sources": ["requests", "gifts"], "sinks": [], "cap": null},
  {"id": "event_items", "kind": "event", "sources": ["event_activities"], "sinks": ["event_rewards"], "cap": null}]}}
```

## 8. Among Us

**Snapshot**
- Developer: Innersloth (Redmond, Washington; a small team).
- Release: mobile June 2018, PC (Steam) November 2018; consoles from late 2020.
- Genre: social deduction (party). Business model: mobile free with ads and cosmetic IAP (ad removal available); PC and consoles paid.
- Scale: a breakout in mid-2020, two years after release, when Twitch and YouTube streamers adopted it. Download and player figures are widely reported but omitted here.

**Core loop**
1. Join a lobby (4–15 players since a 2021 update; originally up to 10) by code or public matchmaking. The host sets rules (impostor count, kill cooldown, vision, task count).
2. Roles are assigned secretly: most players are crewmates; one to three are impostors.
3. Crewmates move around the map completing short task mini-games, which fill a shared task bar. Impostors fake tasks, kill on a cooldown, use vents and trigger sabotages (lights, communications, and timed critical sabotages such as reactor and oxygen).
4. A reported body or the emergency button calls a meeting: discussion on a timer, then a vote, then ejection (or skip).
5. Crewmates win by finishing all tasks or ejecting every impostor; impostors win by reaching parity or with a critical sabotage.
6. Dead players continue as ghosts: they finish tasks (crewmates) or sabotage (impostors) and watch, so they remain engaged until the round ends.

**Meta and progression**
- Cosmetics (hats, skins, pets, visors, nameplates) and account-level progression with cosmetic unlocks earned by playing (verify current currency names).
- Roles added from late 2021 (Scientist, Engineer, Guardian Angel, Shapeshifter, with more in later updates) and maps (The Skeld, MIRA HQ, Polus, The Airship in 2021, The Fungle in 2023).

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Play-earned cosmetic currency | soft | matches, rewarded ads on mobile | cosmetic unlock tracks |
| Purchasable cosmetic currency | premium | IAP | cosmetic bundles and tracks |

There are no gameplay-affecting purchases; all spending is cosmetic.

**Monetization**: cosmetic bundles, ad removal on mobile, cosmetic currency, and the paid PC and console versions.

**Live-ops**: content updates rather than events: new maps, roles, game modes (Hide and Seek, 2022), cosmetic collaborations, and account and safety systems.

**Retention hooks**: friends' game nights (an obligation to the group, not the game), new roles and maps changing the meta, and memorable stories from each round.

**Social layer**: fully synchronous. Groups usually add external voice chat (Discord); public lobbies use text chat with a filter and a **Quick Chat** option of preset phrases for safety (verify current availability by age). Cross-platform play between phones, PCs and consoles.

**UX and onboarding notables**
- Crewmates are identified by colour; task mini-games take 3–10 seconds and work on touch; the whole rule set fits on one screen.
- Typing on a phone during meetings is slow, which disadvantages mobile players in public lobbies; Quick Chat partly addresses it.
- The game is a perfect spectator format: discussion and accusation are entertainment in their own right.

**Art and audio identity**: simple, flat 2D "bean" crewmates, readable maps, comedic kill animations, and iconic meeting and ejection sounds. Low production cost, high meme value.

**Psychology principles used**: theory-of-mind play (reasoning about others' beliefs); social bonding through shared deception and humour; competence through deduction; curiosity from hidden information; relatedness (SDT). It descends from the Mafia party game (Dimitry Davidoff, 1986) and Werewolf.

**Innovations (at the time)**
- Brought Mafia and Werewolf into a real-time spatial game where tasks create alibis and evidence (who was seen where).
- Ghost play keeps eliminated players engaged, a recurring problem in elimination games.
- Cross-platform play between phones and PCs in a social game, at a low price or free.

**Weaknesses and criticism**
- It needs a group. Public lobbies suffer from toxicity, quitters and cheaters, and the 2020 boom brought a widely reported spam-bot attack and hacking waves.
- Retention fell after the 2020 peak; social games ride fads.
- Monetization is light relative to reach; text chat on phones is weak.
- Innersloth cancelled a planned sequel in 2020 to support the original, a sound decision but a reminder of how fragile a small team is under sudden scale.

**Lessons for designers**
1. When players generate the content (accusations, lies, stories), streamers and clips become the distribution channel. Design for watchability.
2. Keep eliminated players engaged (ghost roles, spectating with agency).
3. Make the mechanics produce evidence (visual tasks, location logs) so conversation has something to argue about.
4. Plan safety and moderation (quick chat, reporting, accounts) before a viral spike, not after.
5. If a hit arrives late, invest in the original rather than rushing a sequel.

**Analogy hooks**
- Hidden roles with task-based alibis → co-op puzzle, party and survival games.
- Ghost play → any battle royale or elimination format.
- Meetings as a phase change (action → discussion → vote) → board-game-like strategy and party games.

**Ontology encoding**
```json
{"loops": [
  {"id": "au_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "receive_secret_role", "reward": "objective", "next": "c2"},
    {"id": "c2", "action": "do_tasks_or_kill_and_sabotage", "reward": "task_bar_or_eliminations", "next": "c3"},
    {"id": "c3", "action": "report_body_or_call_meeting", "reward": "discussion_phase", "next": "c4"},
    {"id": "c4", "action": "discuss_and_vote", "reward": "ejection_or_skip", "next": "c5"},
    {"id": "c5", "action": "check_win_condition", "reward": "round_result_and_cosmetic_xp", "next": "c1"}]},
  {"id": "au_social", "type": "social", "period": "session", "steps": [
    {"id": "s1", "action": "gather_friends_in_private_lobby", "reward": "game_night", "next": "s2"},
    {"id": "s2", "action": "play_rounds_and_share_clips", "reward": "stories_and_status", "next": "s1"}]}],
 "economy": {"currencies": [
  {"id": "cosmetic_soft", "kind": "soft", "sources": ["matches", "rewarded_ads"], "sinks": ["cosmetic_tracks"], "cap": null},
  {"id": "cosmetic_premium", "kind": "premium", "sources": ["iap"], "sinks": ["cosmetic_bundles"], "cap": null}]}}
```

## 9. Roblox

**Snapshot**
- Developer: Roblox Corporation (San Mateo, California), founded by David Baszucki and Erik Cassel.
- Release: 2006 on PC; iOS 2012, Android 2014; later Xbox, PlayStation and VR.
- Genre: user-generated-content (UGC) platform: millions of creator-made "experiences" sharing one account, avatar and currency. Business model: free to play; Robux (IAP), a Premium subscription, creator monetization inside experiences, and the Developer Exchange (DevEx) cash-out for eligible creators.
- Scale: a public company (NYSE listing in 2021) that reports daily active users and bookings quarterly; use its investor-relations reports for current figures (`market-intel`).

**Core loop (player)**
1. Browse discovery (charts, recommendations, search, friends' activity) and join an experience in seconds.
2. Play that experience's own loop: obby (obstacle course), tycoon, role-play, simulator, survival, social hangout.
3. Earn experience-specific progress; optionally spend Robux on game passes or developer products inside it.
4. Customise the avatar with marketplace items and carry that identity into every experience.
5. Follow friends into whatever they are playing; repeat.

**Core loop (creator)**
1. Build in Roblox Studio (free), scripting in Luau, a typed derivative of Lua.
2. Publish; the discovery system tests the experience on players and promotes what retains.
3. Monetize: game passes, developer products, avatar items, and engagement-based payouts from Premium subscribers' play time.
4. Earn Robux; exchange eligible earnings for cash through DevEx (eligibility rules and rate in section 18), or reinvest in on-platform ads.

**Meta and progression**
- For players, the avatar and its inventory are the cross-experience progression; everything else lives inside each experience.
- For creators, the meta is the studio: teams, groups, revenue, and climbing the charts.

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Robux | hard | IAP, Premium stipend, creator earnings, gift cards | avatar items, game passes, developer products, on-platform ads |
| Experience currencies | soft | gameplay inside each experience | upgrades defined by each creator |
| DevEx (cash-out) | n/a | eligible creator Robux | real-money payout (standard rate $0.0038 per Earned Robux, minimum 30,000; see section 18 [V9]) |

The platform takes a share of in-experience sales (a 70/30 creator/platform split on many sales is commonly cited; verify), and DevEx converts Robux to cash at a rate well below the price players pay for Robux. Creators' effective share of player spend is therefore a recurring point of criticism.

**Monetization**: Robux packs and gift cards, the Premium subscription (monthly Robux, trading, other perks), and a cut of creator sales and avatar marketplace transactions. Each experience designs its own monetization within platform rules, including randomised "egg" or crate mechanics in some experiences, which creates loot-box exposure for a young audience.

**Live-ops**: platform-wide events (cross-experience hunts and brand activations) plus each experience's own cadence. Top experiences often update weekly, and a hit can emerge and peak within weeks, as several did in 2025 (for example the farming experience Grow a Garden, widely reported for record concurrent players; verify figures).

**Retention hooks**: friends are already there; endless new experiences; the avatar as identity; experience-level hooks (daily rewards, gardens that grow offline, limited items).

**Social layer**: friends, parties, groups, text chat (with age-based restrictions) and voice chat for age-verified older users; experiences double as social spaces (role-play towns are among the most played genres). Age-assurance checks for chat were being rolled out in 2025–26 (verify current requirements).

**UX and onboarding notables**
- One tap from discovery to play, on almost any device, with progress following the account.
- Discovery is both the strength and the bottleneck: thumbnails, icons and early retention decide which experiences surface, so creators A/B test them.

**Art and audio identity**: the original blocky avatar and low-poly worlds, now joined by layered clothing and more realistic options; each experience owns its style. Low-poly assets keep low-end phones viable.

**Psychology principles used**: autonomy (thousands of experiences), relatedness (friends and role-play), identity expression (avatar), competence (obbies, simulators); for creators, status and income. The social proof of chart rankings and friend activity drives discovery.

**Innovations (at the time)**
- Large-scale UGC where the players are the creators, with free tools and a path to income for teenage developers.
- One cross-experience currency and avatar, which makes the platform the progression system.
- Trends that emerge from creators rather than a studio: obbies, tycoons, simulators, role-play towns and short-lived meme genres.

**Weaknesses and criticism**
- **Child safety**: grooming and exploitation risks; lawsuits by several US state attorneys general and families in 2025 (verify specifics); a 2024 short-seller report (Hindenburg Research) alleging inflated metrics and safety failures, which Roblox disputed. Safety is the platform's main business risk.
- **Creator economics**: critics, including a widely viewed 2021 People Make Games investigation, argue that young creators receive a small share of the value they create.
- Copycat experiences, scams around Robux, and gacha-like mechanics in experiences aimed at children.

**Lessons for designers**
1. If players create, give them free tools, a path to status and income, and clear rules on what they may sell.
2. A shared avatar and currency turn a portfolio of games into one progression system.
3. With a young audience, safety (age assurance, chat gating, parental controls, moderation) is a core product feature.
4. On a UGC platform, discovery decides success; first-session retention is what the algorithm rewards.
5. For a studio choosing Roblox as a channel: compare DevEx economics, ownership and audience age against a native app before committing.

**Analogy hooks**
- A cross-game avatar → any studio portfolio (shared cosmetics, shared identity).
- Engagement-based creator payouts → level-editor games that reward popular community levels.
- Short-lived trend genres → rapid prototyping strategies (as in hyper-casual testing).
- Offline growth in a UGC experience → idle mechanics in social spaces.

**Ontology encoding**
```json
{"loops": [
  {"id": "rbx_player", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "discover_and_join_experience", "reward": "new_play_loop", "next": "c2"},
    {"id": "c2", "action": "play_experience_loop", "reward": "experience_progress", "next": "c3"},
    {"id": "c3", "action": "customise_avatar", "reward": "identity_status", "next": "c4"},
    {"id": "c4", "action": "follow_friends_to_next_experience", "reward": "shared_play", "next": "c1"}]},
  {"id": "rbx_creator", "type": "meta", "period": "weekly", "steps": [
    {"id": "m1", "action": "build_and_update_in_studio", "reward": "new_version", "next": "m2"},
    {"id": "m2", "action": "publish_and_get_discovered", "reward": "players", "next": "m3"},
    {"id": "m3", "action": "monetize_passes_products_items", "reward": "robux", "next": "m4"},
    {"id": "m4", "action": "devex_or_reinvest_in_ads", "reward": "cash_or_growth", "next": "m1"}]}],
 "economy": {"currencies": [
  {"id": "robux", "kind": "hard", "sources": ["iap", "premium_stipend", "creator_earnings", "gift_cards"], "sinks": ["avatar_items", "game_passes", "developer_products", "ads"], "cap": null},
  {"id": "experience_currency", "kind": "soft", "sources": ["experience_gameplay"], "sinks": ["experience_upgrades"], "cap": null}]}}
```

## 10. Minecraft

**Snapshot**
- Developer: Mojang Studios (Stockholm), founded by Markus Persson; Microsoft acquired Mojang in 2014.
- Release: 2009 (early PC versions), full release 2011; Pocket Edition on mobile from 2011. The mobile, console and Windows versions were unified as Bedrock Edition from 2017; Java Edition remains separate on PC.
- Genre: sandbox survival and creative building. Business model: premium (one-time purchase on mobile) plus the Marketplace (Minecoins) for creator content and the Realms subscription for hosted worlds.
- Scale: widely reported as the best-selling video game of all time (verify the current figure).

**Core loop (survival)**
1. Punch a tree, get wood, make a crafting table, make tools.
2. Gather and mine: stone, coal, iron, and deeper ores such as diamonds.
3. Craft better tools, armour and shelter before night. A full day-night cycle lasts 20 real minutes, and hostile mobs spawn in darkness.
4. Explore biomes, caves and structures; farm; trade with villagers; enchant and brew.
5. Optionally pursue the Nether, the End and the Ender Dragon, or set your own building goals.

Creative mode removes survival: unlimited blocks, flight, pure construction.

**Meta and progression**
- Player-defined goals: projects, bases, automation, exploration.
- An advancements tree gives soft guidance. Redstone (signal-carrying blocks) adds programmable logic and automation. Multiplayer servers create their own modes and economies.

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Resources (blocks, ores, crops) | material | mining, farming, mobs | crafting, building, trading |
| Experience levels | soft | mining, smelting, combat, breeding, trading | enchanting, anvil repairs (spent, so `soft` rather than `xp`) |
| Emeralds | soft | villager trades, mining | villager trades |
| Minecoins (Bedrock) | premium | IAP | Marketplace skins, worlds, texture packs |

**Monetization**: the up-front purchase; Marketplace content made by partner creators on revenue share; Realms subscriptions; education licences. Gameplay power is never sold in vanilla survival.

**Live-ops**: free major updates for over a decade; an annual Minecraft Live showcase; a shift from 2024 toward smaller, more frequent "game drops" (verify the current cadence); Marketplace content drops weekly.

**Retention hooks**: self-set projects; friends' worlds and servers; updates; the creator culture on YouTube and Twitch; mods (Java).

**Social layer**: local, Realms and server multiplayer; cross-play across Bedrock platforms, including phones; the largest creator and video ecosystem of any game; classroom use through the Education edition.

**UX and onboarding notables**
- Historically almost no tutorial: players learned recipes from wikis and videos, which created a community but excluded newcomers. A recipe book (added in 2017) and in-game hints reduced the gap.
- Touch controls (virtual stick or D-pad, hold to break, tap to place) made a PC sandbox playable on phones.

**Art and audio identity**: voxel blocks with low-resolution (16×16) textures, cheap to render and instantly recognisable; sparse, calm ambient music by C418 (later joined by other composers such as Lena Raine) that leaves space for the player's own story.

**Psychology principles used**: autonomy and self-set goals (SDT); competence through survival mastery; expression and discovery (MDA aesthetics); the IKEA effect at its largest scale; night-time threat as a gentle structure.

**Innovations (at the time)**
- Popularised the survival-crafting sandbox (drawing on Infiniminer and Dwarf Fortress) with infinite procedural worlds.
- Sold an unfinished game in alpha and grew with its community, a model that later became Early Access.
- Unified mobile, console and PC versions with cross-play (Bedrock); creator content marketplace on consoles and phones.

**Weaknesses and criticism**
- Onboarding depends on outside knowledge; the Java/Bedrock split confuses players and causes feature-parity issues.
- Marketplace quality varies; some community votes on new features drew backlash.
- Multiplayer servers bring moderation and safety issues for young players.

**Lessons for designers**
1. Systems that combine (blocks + crafting + logic) produce goals the designer never wrote, which is the cheapest content there is.
2. A day-night cycle gives an open sandbox rhythm and stakes without forcing goals.
3. Offer separate modes for separate motivations: survival for challenge, creative for expression.
4. Low-fidelity art scales to low-end devices and invites players to create.
5. Let the community teach, but put a recipe book in the game for the player who will not search.

**Analogy hooks**
- A day-night threat cycle → base builders, colony sims, survival roguelites.
- Creative mode → level editors in puzzle and platform games.
- Logic blocks → automation layers in factory and idle games.
- A creator marketplace → any game with strong UGC potential.

**Ontology encoding**
```json
{"loops": [
  {"id": "mc_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "gather_and_mine", "reward": "resources", "next": "c2"},
    {"id": "c2", "action": "craft_tools_and_shelter", "reward": "capability", "next": "c3"},
    {"id": "c3", "action": "survive_night_and_explore", "reward": "new_biomes_ores_xp", "next": "c1"}]},
  {"id": "mc_meta", "type": "meta", "period": "session", "steps": [
    {"id": "m1", "action": "set_personal_project", "reward": "goal", "next": "m2"},
    {"id": "m2", "action": "build_or_automate", "reward": "creation_and_status", "next": "m3"},
    {"id": "m3", "action": "share_world_or_video", "reward": "social_recognition", "next": "m1"}]}],
 "economy": {"currencies": [
  {"id": "resources", "kind": "material", "sources": ["mining", "farming", "mobs"], "sinks": ["crafting", "building", "trading"], "cap": null},
  {"id": "experience_levels", "kind": "soft", "sources": ["mining", "combat", "smelting", "trading"], "sinks": ["enchanting", "anvil"], "cap": null},
  {"id": "emeralds", "kind": "soft", "sources": ["villager_trades", "mining"], "sinks": ["villager_trades"], "cap": null},
  {"id": "minecoins", "kind": "premium", "sources": ["iap"], "sinks": ["marketplace_content"], "cap": null}]}}
```

## 11. The Sims FreePlay

**Snapshot**
- Developer: EA (developed by EA's Melbourne mobile studio, later Firemonkeys).
- Release: December 2011 on iOS, with Android following.
- Genre: life sim. Business model: free-to-play, IAP-led (Lifestyle Points and Simoleons).
- Scale: one of EA's longest-running mobile titles. Revenue figures are omitted.

**Core loop**
1. Tap a Sim and choose an action from a menu: cook, work, sleep, a hobby, socialise.
2. Each action takes **real time**, from seconds to many hours, and pays Simoleons and XP on completion.
3. Spend Simoleons on furniture, houses and lots; spend Lifestyle Points on premium items and speed-ups.
4. Complete quest chains, which unlock life stages, careers, hobbies, pets and town areas.
5. Before leaving, queue long actions on every Sim; come back later to collect.

**Meta and progression**
- Player level unlocks; Sims' life stages (baby to elder), careers, relationships (friendship to romance to marriage), hobbies and pets; town expansion with new lots and areas.
- Quest chains carry most of the long-term direction.

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Simoleons | soft | actions, careers, quests | furniture, houses, lots |
| Lifestyle Points (LP) | hard | IAP, slow earning from quests and goals | premium items, speed-ups |
| Social Points | soft | visiting neighbours' towns, social actions | special items (verify) |
| XP | xp | actions | player level unlocks |

**Monetization**: LP and Simoleon packs, speed-ups on long timers, premium furniture and houses, and limited-time event bundles (verify any subscription or VIP tiers in the current build).

**Live-ops**: limited-time quests and seasonal events with exclusive rewards; content updates adding hobbies, careers and house types.

**Retention hooks**: real-time timers (an eight-hour shift creates an appointment), quest deadlines in events, Sims' life stages and relationships progressing over days.

**Social layer**: light: visiting neighbours' towns for Social Points; little direct interaction.

**UX and onboarding notables**
- Managing several Sims in parallel turns the life sim into a **scheduling puzzle**: matching action lengths to when you will next play.
- Timers are visible over every Sim; long-press and quick menus keep the overhead of many Sims manageable.

**Art and audio identity**: 3D Sims and houses with the series' Simlish voice and familiar UI sounds, scaled for 2011-era phones.

**Psychology principles used**: commitment and appointments (setting an action promises a return); endowment and IKEA effect from houses; Zeigarnik pull from quest chains; relatedness with Sims.

**Innovations (at the time)**
- Translated The Sims' action model into real-time F2P timers, turning autonomy into scheduling.
- Showed that a premium PC franchise could be rebuilt as a timer-based F2P service on early smartphones.

**Weaknesses and criticism**
- Very long timers and slow progression read as a paywall; the sandbox's emergent stories (needs, free will) were thinner than in the PC series.
- Some life events took real days, which frustrated players more than it delighted them.

**Lessons for designers**
1. Real-time timers turn a sandbox into a scheduling game, so design the scheduling decisions (short versus long actions, parallel agents).
2. Let players queue work before they leave; respect the session shape of 2–10 minute check-ins.
3. Price speed-ups against the value of waiting; when the wait has no decision in it, players see the price as a toll.
4. Keep the emergent-story layer: timers alone do not make a life sim.

**Analogy hooks**
- Parallel agents with real-time tasks → idle, farming and management games (workers, heroes on expeditions).
- Life stages as progression → pet and family sims.
- Action menus with duration trade-offs → expedition systems in RPG metas.

**Ontology encoding**
```json
{"loops": [
  {"id": "sfp_core", "type": "core", "period": "session", "steps": [
    {"id": "c1", "action": "assign_timed_actions_to_sims", "reward": "pending_rewards", "next": "c2"},
    {"id": "c2", "action": "return_and_collect", "reward": "simoleons_xp", "next": "c3"},
    {"id": "c3", "action": "buy_furniture_or_lots", "reward": "home_progress", "next": "c4"},
    {"id": "c4", "action": "advance_quest_step", "reward": "unlocks", "next": "c1"}]}],
 "economy": {"currencies": [
  {"id": "simoleons", "kind": "soft", "sources": ["actions", "careers", "quests"], "sinks": ["furniture", "houses", "lots"], "cap": null},
  {"id": "lifestyle_points", "kind": "hard", "sources": ["iap", "quests"], "sinks": ["premium_items", "speed_ups"], "cap": null},
  {"id": "social_points", "kind": "soft", "sources": ["neighbour_visits"], "sinks": ["special_items"], "cap": null},
  {"id": "xp", "kind": "xp", "sources": ["actions"], "sinks": [], "cap": null}]}}
```

## 12. Episode and Choices (interactive story)

**Snapshot**
- *Episode*: launched in 2014 by Pocket Gems; later operated as Episode Interactive. *Choices: Stories You Play*: Pixelberry Studios, 2016; Pixelberry was later acquired by Nexon (verify the year).
- Genre: interactive story (visual novel) libraries, romance-led. Business model: free-to-play with chapter energy and a premium currency for premium choices; ads in some builds (verify).
- Scale: both were among the top-grossing narrative games of the late 2010s. Revenue figures are omitted.

**Core loop**
1. Pick a story from a library (romance, drama, fantasy, mystery and others).
2. Read a chapter: an animated visual novel with dialogue and character art.
3. Make choices. Free choices change dialogue and branches; **premium choices** (outfits, romantic scenes, bonus paths) cost premium currency.
4. The chapter ends on a cliffhanger; the next chapter costs one unit of chapter energy (Episode's passes, Choices' keys).
5. Chapter energy regenerates over time, or the player pays (or watches an ad where offered).

**Meta and progression**
- Story completion across "books" and seasons; relationship tracks within stories; character customisation.
- Episode's writer platform let users script and publish their own stories with its scripting tools, turning readers into creators.

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Passes / keys | energy | timed regeneration (capped), IAP, ads (verify) | one per chapter |
| Gems / diamonds | hard | IAP, small grants per chapter or achievement | premium choices (outfits, scenes, branches) |
| Relationship and story stats | xp | choices | branch conditions |

**Monetization**: premium currency packs (the main revenue), chapter-energy packs, and subscriptions or ad removal in some builds (verify). Premium choices are priced per scene or item; reading a whole book on the fully premium path can cost far more than a premium game.

**Live-ops**: new chapters of running books on a weekly cadence; seasonal launches of new books and sequels; writing contests for UGC authors (Episode).

**Retention hooks**: cliffhanger chapter endings (Zeigarnik); weekly chapter drops; chapter-energy regeneration; investment in relationships and avatars.

**Social layer**: light in-game; strong fandom on social media; Episode's author community with followers.

**UX and onboarding notables**
- Tap to advance; premium choices are flagged with a currency icon and price before selection, so the player always knows when a choice costs money.
- Character creation in the first minutes builds identification with the protagonist.

**Art and audio identity**: stylised 2D character art (Episode's house style; Choices' painted backgrounds), expressive poses, romance-forward covers, and looping mood music.

**Psychology principles used**: narrative transportation (the reader is absorbed in the story); curiosity and Zeigarnik from cliffhangers; identification with a customised avatar; loss aversion around a premium scene the player will "miss"; sunk cost from earlier premium choices.

**Innovations (at the time)**
- Monetizing choices and content rather than power or speed.
- Applying the energy model to chapters, so episodic fiction gained a daily cadence.
- Large-scale UGC storytelling with scripting tools (Episode).

**Weaknesses and criticism**
- Premium choices can make the "good" path feel paywalled; the cost of a full premium read is high.
- Mature and suggestive content, and user-acquisition ads for the genre, drew criticism for sensationalism and for reaching younger audiences.
- Repetitive tropes; UGC moderation is a constant cost.

**Lessons for designers**
1. Sell expression and extra content (outfits, bonus scenes) rather than plot-critical information; keep the free path complete and satisfying.
2. Price premium choices transparently before selection.
3. Weekly episodic releases create appointments without energy; energy on top should be generous.
4. Writer tools grow content cheaply, but plan moderation, ratings and age-appropriate discovery from day one.

**Analogy hooks**
- Premium choices → narrative metas in merge, match-3 and renovation games (paid alternative designs or scenes).
- Cliffhanger chapter gating → episodic puzzle campaigns.
- Writer scripting tools → level editors and UGC quest builders.

**Ontology encoding**
```json
{"loops": [
  {"id": "ic_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "spend_pass_open_chapter", "reward": "story_scene", "next": "c2"},
    {"id": "c2", "action": "make_free_or_premium_choices", "reward": "branch_outfit_or_scene", "next": "c3"},
    {"id": "c3", "action": "reach_cliffhanger", "reward": "curiosity_for_next_chapter", "next": "c1"}]},
  {"id": "ic_liveops", "type": "liveops", "period": "weekly", "steps": [
    {"id": "l1", "action": "new_chapter_release", "reward": "fresh_content", "next": "l2"},
    {"id": "l2", "action": "read_and_discuss_in_fandom", "reward": "community_status", "next": "l1"}]}],
 "economy": {"currencies": [
  {"id": "passes", "kind": "energy", "sources": ["regen", "iap", "ads"], "sinks": ["chapter_open"], "cap": null},
  {"id": "gems", "kind": "hard", "sources": ["iap", "chapter_grants"], "sinks": ["premium_choices"], "cap": null},
  {"id": "story_stats", "kind": "xp", "sources": ["choices"], "sinks": [], "cap": null}]}}
```

## 13. Words With Friends

**Snapshot**
- Developer: Newtoy (brothers Paul and David Bettner), 2009 on iOS. Zynga acquired Newtoy in 2010; Take-Two acquired Zynga in 2022. A rebuilt *Words With Friends 2* followed in 2017.
- Genre: asynchronous turn-based word game (crossword tiles). Business model: free with ads plus IAP (ad removal, coins, power-ups).
- Scale: a defining social game of the early smartphone era. Revenue figures are omitted.

**Core loop**
1. Start a game with a friend, a random opponent or, in later versions, a computer opponent.
2. On your turn, place tiles from a seven-tile rack on a 15×15 board to form words connected to existing tiles. Double and triple letter and word squares multiply the score; their layout differs from Scrabble's.
3. Submit: the game previews the score before you commit, then notifies the opponent by push notification.
4. While waiting, take turns in other games; many games run in parallel.
5. When the tiles run out, the higher score wins; offer a rematch.

Using all seven tiles in one move earns a 35-point bonus (Scrabble awards 50).

**Meta and progression**
- Lifetime statistics (best word, average score), levels and challenges in the sequel, solo challenges and team or event modes (verify the current mode list).

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Coins | hard | IAP, rewards, events | power-ups (verify the current set: hints that show where words fit, a "best possible previous move" reveal, tile swaps) |
| XP / level | xp | games, challenges | cosmetic and mode unlocks |

**Monetization**: interstitial ads between turns (the main revenue on the free tier), ad removal, coin packs for power-ups, and cosmetic tile and board styles.

**Live-ops**: seasonal events and themed challenges in the sequel; word-of-the-day and daily puzzle features (verify).

**Retention hooks**: the push notification that says "it's your turn" (a friend is waiting); many open games, so one is always ready; ongoing rivalries with specific friends.

**Social layer**: per-game chat; friends from social networks and contacts; random matchmaking. Its cultural reach was widely illustrated in 2011, when actor Alec Baldwin was removed from a flight after refusing to stop playing it.

**UX and onboarding notables**
- The score preview before submitting removes fear of committing a move.
- Shuffle, tile-bag count and a dictionary check keep friction low; a turn takes seconds to minutes and fits any gap in the day.

**Art and audio identity**: clean, high-contrast tiles and board, gentle notification sounds, and a familiar board-game look that older players read instantly.

**Psychology principles used**: social obligation and reciprocity (a friend is waiting for your move); Zeigarnik pull from open games; competence through vocabulary and strategy; social comparison; variable reward from tile draws.

**Innovations (at the time)**
- Popularised asynchronous turn-based multiplayer on smartphones with push notifications, building on the studio's earlier *Chess With Friends*.
- Established the "With Friends" format: a known board game made asynchronous, social and free.

**Weaknesses and criticism**
- Obvious closeness to Scrabble (the premium-square layout and scoring were changed).
- Intrusive interstitial ads on the free tier; widespread use of anagram solvers.
- Abandoned games stall rivalries.
- A 2019 breach of a Zynga account database including Words With Friends players was widely reported.

**Lessons for designers**
1. Asynchronous turns need notification design: one push per turn, quiet hours, batching, and a forfeit timer for abandoned games.
2. Parallel games remove waiting; the player always has a move to make somewhere.
3. Preview the outcome before commit (score preview) to lower anxiety in a skill game.
4. Expect solvers in any word or puzzle duel; reward styles of play that solvers do not help with, or accept them.

**Analogy hooks**
- Async turns + push + parallel games → strategy duels, puzzle duels (asynchronous match-3 versus), card games.
- Reveal-the-best-move-afterwards → a learning tool in any puzzle or strategy game.
- "Known board game, made async" → chess, checkers, card games, dice games.

**Ontology encoding**
```json
{"loops": [
  {"id": "wwf_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "open_game_on_turn_notification", "reward": "board_and_rack", "next": "c2"},
    {"id": "c2", "action": "place_tiles_preview_score_submit", "reward": "points", "next": "c3"},
    {"id": "c3", "action": "switch_to_next_open_game", "reward": "another_move", "next": "c1"}]},
  {"id": "wwf_social", "type": "social", "period": "daily", "steps": [
    {"id": "s1", "action": "receive_your_turn_push", "reward": "social_obligation", "next": "s2"},
    {"id": "s2", "action": "play_turn_and_chat", "reward": "rivalry_progress", "next": "s3"},
    {"id": "s3", "action": "finish_and_rematch", "reward": "win_or_revenge_chance", "next": "s1"}]}],
 "economy": {"currencies": [
  {"id": "coins", "kind": "hard", "sources": ["iap", "rewards", "events"], "sinks": ["power_ups"], "cap": null},
  {"id": "xp", "kind": "xp", "sources": ["games", "challenges"], "sinks": [], "cap": null}]}}
```

## 14. 8 Ball Pool

**Snapshot**
- Developer: Miniclip (Tencent became the majority owner in 2015, widely reported).
- Release: as a web game around 2010, with mobile versions following (verify dates).
- Genre: real-time 1v1 sports (pool). Business model: free-to-play hybrid: IAP (cash, coins, cues, pass) plus ads.
- Scale: one of the most downloaded sports games on mobile over the 2010s (figures omitted).

**Core loop**
1. Pick a venue. Each venue has a coin entry fee; the winner takes the pot.
2. Match with a similar opponent in real time.
3. Play 8-ball: aim along the guideline, set power and spin, shoot within the shot timer; pot your group (solids or stripes), then the 8-ball.
4. Win: the pot plus XP. Lose: the entry fee is gone.
5. Upgrade cues and level up to unlock higher-stakes venues with bigger pots.

**Meta and progression**
- Levels unlock venues; the **venue ladder doubles as matchmaking, progression and stakes**.
- Cue collection and upgrades (force, aim, spin, time); leagues, tournaments (knockout brackets), a 9-ball mode, clubs, avatars and table cosmetics (verify the current modes).

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Coins | soft | match pots, spin wheel, scratch cards, events, IAP | venue entry fees, tournaments |
| Cash | hard | IAP, level-ups, events | cues, boxes, cosmetics |
| Cue pieces / boxes | material | boxes, pass, events | unlocking and upgrading cues |
| XP | xp | matches | levels (venue unlocks) |

**Monetization**: coin and cash packs, cues, a season pass (Pool Pass), randomised boxes (odds disclosure required by store rules), and ads for spins and bonus rewards.

**Live-ops**: pass seasons, limited-time cues and events, leagues, and tournaments.

**Retention hooks**: climbing to more prestigious venues; the daily spin wheel; pass progress; rivalry and revenge matches.

**Social layer**: challenging friends; preset chat messages; clubs. Matches are synchronous but short.

**UX and onboarding notables**
- Drag to aim, a vertical power slider and a spin control; the guideline shows the predicted path.
- The cue's aim stat lengthens the guideline, so equipment directly changes how much information the player sees.

**Art and audio identity**: a clean top-down table with realistic ball physics, satisfying clack and pocket sounds, and table themes per venue.

**Psychology principles used**: loss aversion (the entry fee is at stake every match); escalation of commitment as stakes rise; competence; variable reward from boxes and wheels.

**Innovations (at the time)**
- Stake-based matchmaking: venues are rank, entry fee is the sink and pot is the source, all in one rule.
- Low-latency real-time 1v1 sports on phones, reachable from a web audience.

**Weaknesses and criticism**
- Cue stats (especially a longer guideline) are felt as pay-to-win in a skill game.
- Coin stakes and spin wheels give the economy a gambling-like vocabulary.
- Third-party aim-assist tools are a persistent cheating problem; ads interrupt sessions.

**Lessons for designers**
1. A stakes ladder is elegant: entry fee as sink, pot as source, venue as rank. Tune pots so a 50% win rate is slightly negative at each venue, which keeps a sink active, and give daily free coins so nobody is locked out.
2. Equipment that changes skill expression (more information, more control) feels like pay-to-win. Sell cosmetics and sidegrades, or cap stat effects per venue.
3. Shot timers keep synchronous matches short enough for mobile.
4. Budget anti-cheat from the start in any skill PvP game.

**Analogy hooks**
- Venue stakes ladder → darts, bowling, golf, card duels, puzzle duels.
- Entry-fee knockout tournaments → any short skill game.
- Guideline length as a progression stat → aiming aids in archery or physics games (use with care).

**Ontology encoding**
```json
{"loops": [
  {"id": "ebp_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "pick_venue_pay_entry_fee", "reward": "match_with_pot", "next": "c2"},
    {"id": "c2", "action": "aim_set_power_spin_shoot", "reward": "potted_balls", "next": "c3"},
    {"id": "c3", "action": "pot_eight_ball_or_lose", "reward": "pot_xp_or_loss", "next": "c1"}]},
  {"id": "ebp_meta", "type": "meta", "period": "daily", "steps": [
    {"id": "m1", "action": "spin_wheel_and_claim_pass_rewards", "reward": "coins_cue_pieces", "next": "m2"},
    {"id": "m2", "action": "upgrade_cue", "reward": "stat_boost", "next": "m3"},
    {"id": "m3", "action": "unlock_higher_venue", "reward": "bigger_stakes", "next": "m1"}]}],
 "economy": {"currencies": [
  {"id": "coins", "kind": "soft", "sources": ["pots", "spin_wheel", "events", "iap"], "sinks": ["entry_fees", "tournaments"], "cap": null},
  {"id": "cash", "kind": "hard", "sources": ["iap", "level_ups", "events"], "sinks": ["cues", "boxes", "cosmetics"], "cap": null},
  {"id": "cue_pieces", "kind": "material", "sources": ["boxes", "pass", "events"], "sinks": ["cue_upgrades"], "cap": null},
  {"id": "xp", "kind": "xp", "sources": ["matches"], "sinks": [], "cap": null}]}}
```

## 15. Golf Clash

**Snapshot**
- Developer: Playdemic (Manchester). EA acquired Playdemic from Warner Bros. in 2021 (widely reported).
- Release: 2017.
- Genre: 1v1 sports PvP (golf). Business model: free-to-play, IAP-led (gems, chests, balls, pass; verify the current names).
- Scale: one of the most successful mobile sports games of the late 2010s (figures omitted).

**Core loop**
1. Enter a match on a tour by paying a coin entry fee; higher tours have harder courses and bigger pots.
2. Both players play the **same hole at the same time**: choose club and ball, aim, read the wind, add curl and spin, then stop a moving timing needle; stopping it in the "Perfect" zone gives the most accurate shot.
3. Watch both shots play out; the fewer strokes wins the hole; a match lasts a few holes (verify the format).
4. The winner takes the pot and earns a chest.
5. Chests occupy slots and unlock on real-time timers, a model borrowed from Clash Royale. They hold club cards, coins and gems.
6. Upgrade clubs with cards and coins, and climb to higher tours.

**Meta and progression**
- A tour ladder; club categories (drivers, woods, irons, wedges, rough and sand clubs) with levels that raise power, accuracy, spin and curl; balls as consumables with stats such as wind resistance.
- Weekly tournaments with skill divisions; clans (verify the current name).

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| Coins | soft | match pots, chests | tour entry fees, club upgrades |
| Gems | hard | IAP, chests, tournaments | chests, chest unlock speed-ups, balls, tournament entries |
| Club cards | material | chests | club levels |
| Balls | material | shop, chests, rewards | consumed when used |

**Monetization**: chests (randomised, with odds disclosure), gems, ball packs, a season pass, and limited offers.

**Live-ops**: weekly tournaments, themed events, season passes, and new courses and tours.

**Retention hooks**: chest timers (open a slot, start the next one); weekly tournament placement; the tour ladder.

**Social layer**: 1v1 matches with emoji-only chat, which limits toxicity; friend matches; clans. A community of guide writers and video creators publishes wind and ring charts, so much of the mastery is learned outside the game.

**UX and onboarding notables**
- **Simultaneous play** removes waiting: both players shoot at once, then watch both results. Turn-based dead time is gone.
- The timing needle gives a skill layer whose difficulty depends on club accuracy, so upgrades and skill interact.
- Wind compensation is learnable and deep, which keeps expert play interesting.

**Art and audio identity**: bright, stylised 3D courses with a readable aiming view, punchy hit and "Perfect" feedback, and crowd reactions.

**Psychology principles used**: competence (mastering wind and timing); loss aversion (entry fees); variable reward (chests); appointment mechanics (chest timers); social comparison (tournaments).

**Innovations (at the time)**
- Simultaneous 1v1 golf, which turns a turn-based sport into a fast duel.
- A cross-genre transplant of Clash Royale's chest-slot timers and card-upgrade economy into a sports game.

**Weaknesses and criticism**
- At higher tours, club levels and premium balls can outweigh skill, which players read as pay-to-win.
- Random chests; matchmaking against higher-level clubs.
- Expert play requires outside wind charts, which makes mastery opaque inside the game.

**Lessons for designers**
1. Simultaneous turns remove dead time in 1v1 duels; turn-based is not the only option for skill sports.
2. A proven economy (chests + cards + timers) can cross genres, but every stat must be checked against how much it overrides skill.
3. Cap stat advantage per tier (matchmake by club level as well as rank).
4. Put the knowledge the community writes down (wind charts) into the game, so mastery is earnable without a guide.

**Analogy hooks**
- Simultaneous turns → puzzle duels, card battles, racing ghosts.
- Chest slots with timers → any PvP game needing reward pacing.
- A timing needle shaped by an accuracy stat → archery, basketball, bowling, fishing.

**Ontology encoding**
```json
{"loops": [
  {"id": "gc_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "pay_tour_entry_fee", "reward": "match_with_pot", "next": "c2"},
    {"id": "c2", "action": "pick_club_ball_aim_curl_time_needle", "reward": "shot_result", "next": "c3"},
    {"id": "c3", "action": "win_holes_win_match", "reward": "pot_and_chest", "next": "c1"}]},
  {"id": "gc_meta", "type": "meta", "period": "daily", "steps": [
    {"id": "m1", "action": "start_chest_timer", "reward": "pending_chest", "next": "m2"},
    {"id": "m2", "action": "open_chest", "reward": "club_cards_coins_gems", "next": "m3"},
    {"id": "m3", "action": "upgrade_clubs_climb_tour", "reward": "new_courses_bigger_pots", "next": "m1"}]}],
 "economy": {"currencies": [
  {"id": "coins", "kind": "soft", "sources": ["pots", "chests"], "sinks": ["entry_fees", "club_upgrades"], "cap": null},
  {"id": "gems", "kind": "hard", "sources": ["iap", "chests", "tournaments"], "sinks": ["chests", "speed_ups", "balls"], "cap": null},
  {"id": "club_cards", "kind": "material", "sources": ["chests"], "sinks": ["club_levels"], "cap": null},
  {"id": "balls", "kind": "material", "sources": ["shop", "chests"], "sinks": ["use_in_match"], "cap": null}]}}
```
Chest slots are a gate (a `gate` node with a time condition in `economy-model.schema.json`), not a currency, so they are omitted from the currency list.

## 16. Duolingo (gamification lessons)

**Snapshot**
- Developer: Duolingo, Inc. (Pittsburgh), founded by Luis von Ahn and Severin Hacker. Public launch 2012; listed on Nasdaq in 2021.
- Genre: gamified learning app (not a game, but the most studied use of game retention systems outside games). Business model: freemium: free with ads; Super Duolingo subscription (renamed from Duolingo Plus in 2022); a higher Max tier with AI features from 2023.
- Scale: reports daily and monthly active users quarterly (use its shareholder letters for current figures).

**Core loop**
1. Open the app (often from a reminder) and tap the next lesson on the path.
2. Answer short exercises: translate, listen, speak, match. On the free tier, mistakes cost hearts (a lives system). In 2025 the company began testing an energy system that replaces hearts, with testing reported from 3 July 2025 for a small share of users and about 25 energy units a day; energy drains with each exercise, and subscribers get unlimited energy (grade C source: [Duolingo Wiki](https://duolingo.fandom.com/wiki/Energy)). Which platforms and countries have switched as of October 2026 was not confirmed here.
3. Finish the lesson: XP, gems, the day's streak extended, and progress along the path.
4. Daily quests and league XP add short-term goals; return tomorrow to keep the streak.

**Meta and progression**
- A linear course path (a 2022 redesign replaced the branching skill tree) with units and checkpoints.
- **Streak**: consecutive days with at least one lesson; streak freezes (bought with gems or granted) protect a missed day; streak repair offers.
- **Leagues** (first tested in 2018 according to [Duolingo's blog](https://blog.duolingo.com/duolingo-leagues-leaderboards/), where early versions had five leagues instead of today's ten): weekly leaderboards with cohorts of about 30 learners across ten tiers, with promotion and demotion zones.
- Achievements, friend quests (cooperative weekly goals) and friend streaks.

**Economy**

| Currency | Kind | Sources | Sinks |
|---|---|---|---|
| XP | xp | lessons, quests, boosts | league rank, daily goal |
| Gems | hard | lessons, quests, chests, IAP | streak freezes, hearts refills, boosts, cosmetics |
| Hearts / energy | energy | timed refill, practice, subscription (unlimited on paid tiers) | mistakes (hearts) or lessons (energy) |
| Streak freezes | material | gems, rewards | protect a missed day |

**Monetization**: subscriptions (no ads, unlimited hearts or energy, extra practice; Max adds AI-powered features), family plans, gem packs, and ads on the free tier (between lessons, plus rewarded placements).

**Live-ops**: monthly challenges and badges, seasonal events, XP ramp-up events, and brand marketing built on the mascot Duo. The company publicly describes heavy A/B testing of features and notifications.

**Retention hooks**: the streak (a daily stake), reminders, weekly league resets, daily quests, friend streaks and friend quests. Jorge Mazal, a former Duolingo product leader, described in a widely read 2022 essay (Lenny's Newsletter) how the team modelled users by state (new, current, at-risk, dormant, resurrected and so on), found that the retention rate of current users moved overall engagement most, and then prioritised leagues, streak improvements and notification work. Summarised here; read the original for detail.

**Social layer**: friends and following, friend quests (co-op), friend streaks, and leagues with strangers (competitive, low-stakes).

**UX and onboarding notables**
- A lesson takes a few minutes; feedback is immediate with sound; the path removes choice paralysis.
- A placement test and a first lesson before sign-up deliver value before asking for anything.
- Notifications and the mascot carry a distinct, often humorous voice; the "guilt-tripping owl" became an internet meme.

**Art and audio identity**: flat, bold illustration with a recognisable cast; Duo the owl; bright correct-answer chimes and celebration animations; streak-flame animation as a reward ritual.

**Psychology principles used**: loss aversion (the streak); goal-gradient (daily goal ring, path); social comparison (leagues; Festinger, 1954); the fresh-start effect at weekly league resets (Dai, Milkman and Riis, 2014); endowed progress (the streak count is an asset); variable reward (chests); implementation intentions through reminder timing.

**Innovations (at the time)**
- Imported game retention systems (streaks, leagues, lives, quests) into education at very large scale.
- Published research behind the systems: a half-life regression model for spaced repetition (Settles and Meeder, ACL 2016) and a "sleeping, recovering" bandit algorithm for choosing reminder notifications (Yancey and Settles, KDD 2020).

**Weaknesses and criticism**
- Engagement versus outcome: critics argue that streaks and leagues optimise for opening the app rather than for proficiency, and that easy lessons farmed for XP can replace real practice.
- Streak anxiety and guilt-toned notifications; hearts that punish mistakes conflict with learning.
- A 2025 "AI-first" strategy memo from the CEO drew public backlash over replacing contractors with AI and over content quality.

**Lessons for designers**
1. A streak retains because each day carries a stake. Add forgiveness (freezes, repair), or the first broken streak becomes the churn moment.
2. Weekly leagues with small cohorts (about 30) and promotion and demotion give most players a winnable race; the weekly reset is a fresh start.
3. Optimise reminder timing and copy with experiments, but cap frequency and do not default to guilt.
4. Measure the value you sell (learning, fun, mastery) alongside engagement. Gamification that drifts from the core value erodes trust.
5. Lives charged per mistake conflict with mastery goals; per-session energy, or no gate, fits learning better.

**Analogy hooks**
- Streak with freezes → puzzle-of-the-day games, login calendars, fitness features in games.
- Leagues of about 30 with promotion and demotion → puzzle event races (Royal Match's competitions in `references/puzzle-casual.md`), idle games, PvE leaderboards.
- Spaced repetition → skill-practice modes and tutorials that resurface forgotten mechanics.
- A notification bandit → live-ops CRM (`liveops`, `player-analytics`).

**Ontology encoding**
```json
{"loops": [
  {"id": "duo_core", "type": "core", "period": "minutes", "steps": [
    {"id": "c1", "action": "open_from_reminder_start_lesson", "reward": "exercise_set", "next": "c2"},
    {"id": "c2", "action": "answer_exercises", "reward": "immediate_feedback", "next": "c3"},
    {"id": "c3", "action": "finish_lesson", "reward": "xp_gems_path_progress", "next": "c1"}]},
  {"id": "duo_meta", "type": "meta", "period": "daily", "steps": [
    {"id": "m1", "action": "complete_daily_goal", "reward": "streak_plus_one", "next": "m2"},
    {"id": "m2", "action": "complete_daily_quests", "reward": "chests_gems", "next": "m3"},
    {"id": "m3", "action": "receive_tuned_reminder_next_day", "reward": "return_trigger", "next": "m1"}]},
  {"id": "duo_social", "type": "social", "period": "weekly", "steps": [
    {"id": "s1", "action": "join_league_cohort", "reward": "leaderboard_slot", "next": "s2"},
    {"id": "s2", "action": "earn_xp_against_cohort", "reward": "rank", "next": "s3"},
    {"id": "s3", "action": "promote_stay_or_demote_at_reset", "reward": "tier_change_fresh_start", "next": "s1"}]}],
 "economy": {"currencies": [
  {"id": "xp", "kind": "xp", "sources": ["lessons", "quests", "boosts"], "sinks": [], "cap": null},
  {"id": "gems", "kind": "hard", "sources": ["lessons", "quests", "chests", "iap"], "sinks": ["streak_freezes", "heart_refills", "boosts"], "cap": null},
  {"id": "hearts", "kind": "energy", "sources": ["timed_refill", "practice", "subscription"], "sinks": ["mistakes"], "cap": 5},
  {"id": "streak_freezes", "kind": "material", "sources": ["gems", "rewards"], "sinks": ["missed_day_protection"], "cap": null}]}}
```
The hearts `cap` of 5 reflects the long-standing free-tier design; verify against the current build, since the system is being changed.

## 17. Cross-case synthesis for casual, social and sim

### 17.1 Lineages (read as evolution)

```
Slot-adjacent social:  slot machine + village + friend raids (Coin Master, mid-2010s)
                       → board-dice + partner co-op + sticker albums + IP (Monopoly Go!, 2023)
Farming / production:  FarmVille (web, 2009; crops wither) → Hay Day (2012; no withering, player market, Derby)
                       → Township (farm + town, several transport-order loops, co-op Regattas)
Merge:                 Triple Town (2010, merge-3 puzzle) → Merge Dragons! (2017, merge-3 + camp)
                       → Merge Mansion (merge-2 + renovation + mystery) → Travel Town (merge-2 + orders, polish)
Life sim:              The Sims (PC) → The Sims FreePlay (real-time action timers, 2011)
                       Animal Crossing (console, real-time clock) → Pocket Camp (F2P, 2017) → Pocket Camp Complete (offline, 2024)
Async and short PvP:   Scrabble → Words With Friends (async + push, 2009)
                       web pool → 8 Ball Pool (stakes venues); Clash Royale chests → Golf Clash (simultaneous 1v1, 2017)
Social deduction:      Mafia (1986) / Werewolf → Among Us (spatial tasks + meetings, 2018)
Creation:              Minecraft (sandbox + marketplace) ; Roblox (UGC platform + creator payouts)
Interactive fiction:   visual novels → Episode / Choices (chapter energy + premium choices)
Gamified apps:         game retention systems → Duolingo (streaks, leagues, notification science)
```

### 17.2 The three engines

| Engine | Mechanism | Strongest cases | Typical failure | Guardrail |
|---|---|---|---|---|
| Timers (absence → anticipation) | Real-time production, regeneration, chests, chapter energy | Hay Day, Township, The Sims FreePlay, Golf Clash, Episode / Choices | Waits without decisions feel like tolls; binge players churn | No asset loss on absence; queue before leaving; generous early energy |
| Social obligation (other players → reasons to return) | Async turns, team help, co-op events, raids, leagues | Words With Friends, Hay Day Derby, Monopoly Go! partners, Duolingo leagues, Among Us game nights | Guilt, toxicity, dependence on friends who leave | Opt-out without penalty; forfeit timers; positive-sum actions alongside adversarial ones |
| Collection (randomness → goals) | Card sets, sticker albums, furniture, cosmetics | Monopoly Go!, Coin Master, Pocket Camp, Roblox avatars | Paid randomness at the last missing item; grey markets | Odds disclosure, duplicate protection, trading windows, direct purchase for minors |

### 17.3 Timer design comparison

| Game | Timer | What absence costs | Forgiveness | Monetized as |
|---|---|---|---|---|
| Hay Day | crop and production queues | opportunity only (no withering) | high | speed-ups, missing items |
| Township | production + transport departures | opportunity, occasional missed order | high | speed-ups, missing items |
| The Sims FreePlay | real-time Sim actions | idle Sims | medium (long actions can be queued) | speed-ups |
| Coin Master / Monopoly Go! | spin or dice regeneration to a cap | regeneration above the cap is lost | low above the cap | energy packs, event bundles |
| Merge Mansion / Travel Town | energy regeneration | regeneration above the cap is lost | medium (level-up refills) | energy, storage |
| Golf Clash | chest unlock timers | slots stay full, new chests are lost | medium | gems to open now |
| Episode / Choices | chapter energy | regeneration above the cap is lost | medium | passes, premium choices |
| Duolingo | daily streak | the streak itself | freezes, repair | gems, subscription |

Rule of thumb: the farther right a game sits on "absence costs assets", the more it relies on loss aversion and the more ethical scrutiny it needs. Hay Day's "no withering" decision is the benchmark for forgiving design.

### 17.4 Social structure taxonomy

| Structure | Sync | Valence | Cases | Design levers |
|---|---|---|---|---|
| Async raid / attack on persistent bases | async | adversarial | Coin Master, Monopoly Go! | shields, revenge, target selection, loss caps |
| Small-group co-op project | async | cooperative | Monopoly Go! partners, Hay Day Derby, Township Regattas | group size 4–30, task boards, shared milestones |
| Player market | async | positive-sum | Hay Day roadside shop, Roblox marketplace | price limits, fees, listing caps |
| Async turns | async | competitive | Words With Friends | push design, parallel games, forfeit timers |
| Short synchronous duels | sync | competitive | 8 Ball Pool, Golf Clash | entry fees, shot timers, emoji-only chat |
| Party session with hidden roles | sync | mixed | Among Us | lobby codes, host rules, quick chat, ghosts |
| Creator to audience | async | positive-sum | Roblox, Minecraft Marketplace, Episode writers | free tools, payouts, discovery, moderation |
| Comparison cohort | async | competitive, low stakes | Duolingo leagues | cohort size about 30, weekly reset, promotion and demotion |

### 17.5 Ethics risk register for these patterns

| Pattern | Cases | Risk | Required guardrail (see `legal-ethics`, `monetization`) |
|---|---|---|---|
| Slot core with paid energy | Coin Master, Monopoly Go! | simulated gambling, minors' spending | age gating, spend limits, no stake multipliers for minors, check Australia R18+ "simulated gambling" rules (section 18) |
| Stake multiplier | Coin Master, Monopoly Go! | escalating bets | cap multipliers, explain expected value, cool-down prompts |
| Paid random cosmetics | Pocket Camp fortune cookies, Roblox "eggs" in some experiences | loot-box law (Belgium, Brazil under-18), all-ages audiences | odds disclosure, direct-purchase alternative, disable for minors where required |
| Premium narrative choices | Episode / Choices | paywalled "good" path, mature content | complete free path, price shown before choice, age-appropriate discovery |
| UGC with a young audience | Roblox | grooming, exploitation, scams | age assurance, chat gating, parental controls, moderation SLAs |
| Guilt notifications and streaks | Duolingo, many casual games | anxiety, compulsive checking | frequency caps, quiet hours, streak forgiveness |
| Pay-to-win stats in skill PvP | 8 Ball Pool, Golf Clash | unfair matches | stat caps per tier, matchmaking on equipment level |

Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/compliance_preflight.py --project DIR --platform all --json` before soft launch for any design that uses these patterns.

### 17.6 Checklist before building a social, timer or collection game
- [ ] Name the engine (timer, social obligation, collection) that carries D7 and D30, and the case you are borrowing it from. Record it in `contract.meta.comparables`.
- [ ] Decide what absence costs. Default: opportunity only (Hay Day). If assets can be lost, justify it in `contract.monetization.ethics`.
- [ ] For each timer, write the decision the player makes while it runs. If there is none, shorten or remove it.
- [ ] Pair every adversarial social action with a defensive tool and a cooperative alternative.
- [ ] Model energy cost per goal (merge arithmetic in case 6) and storage caps in `economy-model.schema.json`, then run `economy_sim.py --model PATH --runs 200 --seed 1 --json`.
- [ ] For collections: odds disclosure, duplicate handling, trading windows, and a non-random purchase path.
- [ ] For notifications: one per meaningful event, quiet hours, a frequency cap, and a tone guide that avoids guilt.
- [ ] For young audiences: chat gating, moderation and no paid randomness, checked against `legal-ethics`.
- [ ] Plan the end of service (offline edition, save export) before launch.

## 18. Volatile facts (as of Oct 2026 — verify before relying)

- [V1] A Sensor Tower H1 2026 data digest headlined a "Hay Day comeback"; the same digest reports mobile game IAP of about $40B in H1 2026 (−2% YoY). Source: [Mobilegamer.biz data digest](https://mobilegamer.biz/data-digest-sensor-towers-h1-analysis-hay-days-comeback-julys-top-games-big-krafton-numbers-and-more/).
- [V2] Mobile game IAP in 2025 was about $82B (+1%); growth came from retaining and monetizing existing players through live-ops, events and IP collaborations, the Monopoly Go! playbook. Source: [Sensor Tower State of Gaming 2026](https://sensortower.com/press/press-release-sensor-tower-state-of-gaming-gaming-drove-52-billion-downloads-82b-iap-revenue-on-mobile-and-12b-premium-revenue-on-steam).
- [V3] Australia: games classified after 22 September 2024 with paid chance-based items are rated at least M; games with simulated gambling are rated R18+. Relevant to slot-core designs (cases 1–2). Sources: [PCWorld](https://www.pcworld.com/article/2464538/all-games-with-loot-boxes-will-be-rated-m-or-higher-in-australia.html), [PocketGamer.biz](https://www.pocketgamer.biz/australia-sets-new-rules-for-video-games-with-gambling-like-content).
- [V4] Brazil's ECA Digital law bans selling loot boxes to under-18s from March 2026; in June 2026 a Brazilian court ordered Riot Games to pay damages and add age verification and probability disclosure (reported amounts conflict). Relevant to random paid items in cases 1, 2, 7, 9, 14, 15. Source: [Sheep Esports](https://www.sheepesports.com/articles/brazil-court-orders-riot-games-to-pay-eur2-5m-over-league-of-legends-loot-boxes/en).
- [V5] Belgium has treated paid loot boxes as gambling since 2018. Source: [Programming Insider](https://programminginsider.com/loot-boxes-regulation-and-where-the-line-sits-in-2026/).
- [V6] Apple and Google require disclosure of odds for randomised paid items before purchase. Source: [App Review Guidelines](https://developer.apple.com/app-store/review/guidelines/).
- [V7] The amended US COPPA Rule had a compliance deadline of 22 April 2026, with biometric identifiers (relevant to voice chat) now counted as personal information. Relevant to Roblox-style UGC and any game with under-13 users. Source: [Toy Association](https://toyassociation.org/PressRoom2/News/2026-News/updated-coppa-rule-requirements-take-effect-april-22.aspx).
- [V8] Roblox launched "Cube 4D" generation in beta in February 2026; in one experience, players using it reportedly had 64% higher average playtime (self-reported). Source: [Roblox newsroom](https://about.roblox.com/newsroom/2026/02/accelerating-creation-powered-roblox-cube-foundation-model).
- [V9] Roblox Developer Exchange (checked 2026-10-20): the standard rate is $0.0038 per Earned Robux since 5 September 2025 at 10:00 PT, up from $0.0035 (so 30,000 Earned Robux pays $114 instead of $105); a higher rate of $0.0054 applies to certain earnings from eligible games (developer products, passes, subscriptions and private servers bought by US players verified as 18+); the minimum cash-out is 30,000 Earned Robux, once per calendar month; creators must be at least 13, with a verified email, a DevEx portal account and a tax form on file. Balances earned before the change cash out at the old rate first. Source: [Roblox Creator Docs](https://create.roblox.com/docs/production/monetization/developer-exchange).
- [V10] Pocket Camp Complete: launched 2 December 2024 as a paid, offline edition; the original app's service ended 28 November 2024; save data could be transferred until 1 June 2025 ([Nintendo](https://www.nintendo.com/us/whatsnew/mobilenews-animal-crossing-pocket-camp-complete-is-now-available/)). Duolingo leagues: [Duolingo blog](https://blog.duolingo.com/duolingo-leagues-leaderboards/). Coin Master, Moon Active and Travel Town: [Wikipedia: Moon Active](https://en.wikipedia.org/wiki/Moon_Active), [Wikipedia: Coin Master](https://en.wikipedia.org/wiki/Coin_Master).
- Not verified for this file, check before quoting: current Roblox age-assurance requirements for chat; the Pocket Camp Complete list price; Duolingo's hearts-to-energy change by platform; Monopoly Go! and Coin Master regeneration caps and event names; the Travel Town acquisition year (2021 vs 2022).
