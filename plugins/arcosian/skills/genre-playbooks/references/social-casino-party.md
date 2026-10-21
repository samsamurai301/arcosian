# Social, Casino and Party Playbooks

This file covers six genres that run on chance, social connection and live events:

1. Social casino and slots
2. Coin Master-likes (slot core + village + raids)
3. Board-game casual (*Monopoly Go!*-style dice boards)
4. Party and social deduction
5. Bingo
6. Casual sports (golf, pool)

Commercially they are some of the most durable genres on mobile. They are also where ethics, age ratings and gambling-adjacent law constrain design most. Section 0 holds the shared tools: the legal and store landscape for simulated gambling, chance math (RTP, volatility, dice distributions), energy-and-event economics, and social-graph mechanics. Technically, agents can build most of these well (3–4/5). Slot maths, dice boards, bingo rules and turn-based physics are deterministic and can be simulated. The barriers are commercial and regulatory: UA scale, IP licences, live-ops volume and classification. Party and social deduction is the exception (2/5), because real-time small-lobby play and human fun can't be verified automatically.

## Contents

| § | Playbook | Session profile (estimate) | Primary monetization | Agent-buildability | First project for an agent pipeline? |
|---|---|---|---|---|---|
| 0 | [Shared foundations](#0-shared-foundations) | — | — | — | Read first |
| 1 | [Social casino / slots](#1-social-casino--slots) | 5–20 min, several a day | Coin packs, VIP, piggy bank | 4/5 | Technically yes, commercially high-risk |
| 2 | [Coin Master-likes](#2-coin-master-likes) | 2–5 min bursts on spin regen | Spins, chests, event offers | 4/5 | Yes, with careful classification |
| 3 | [Board-game casual](#3-board-game-casual-monopoly-go-style) | 2–10 min bursts on dice regen | Dice, event and album offers | 4/5 | Yes (slice); live ops is the moat |
| 4 | [Party / social deduction](#4-party-and-social-deduction) | 10–20 min lobbies | Cosmetics, pass, ads | 2/5 | No |
| 5 | [Bingo](#5-bingo) | 2–5 min rounds | Credits/power-ups, VIP | 4/5 | Yes |
| 6 | [Casual sports](#6-casual-sports-golf-pool) | 1–5 min async/turn matches | Chests, equipment, coins | 3/5 (2D pool 4/5) | Yes |
| — | [Volatile facts](#volatile-facts-as-of-oct-2026--verify-before-relying) | — | — | — | Check before quoting numbers |

## How to use these playbooks

- Set `meta.genre` to `social-casino`, `casual` or `party` as appropriate (the slugs listed in `SKILL.md`), and set `meta.subgenre` to the playbook slug. **Before any design work, set `meta.target_audience.age_min` and the storefront list in `config.json`.** Classification and law depend on both.
- Copy loops into `contract.json → loops[]`. Turn the starter list into P0 features with `gs.py feature add`. "Sim validates" criteria become `unit` evidence, using `economy_sim.py` (spins and dice as `per_session` energy sources, events as `gate` and `converter` nodes) and `gacha_calc.py` (chests, sticker packs).
- Mechanic category labels used here (chance & randomness, economy & resources, time & energy, collection & randomness, social & competition, live events, progression & upgrade, UX automation, combat) map to `mechanics-codex` via `gs.py kb "<mechanic>" --skill mechanics-codex`.
- KPIs are qualitative unless sourced. Public genre benchmarks for these categories are scarce and often vendor-produced.

## 0. Shared foundations

### 0.1 Simulated gambling: law, stores, ethics
Stable rules of thumb. Have the `compliance-officer` agent and counsel confirm them per storefront.
- **Three legal categories:**
  1. **Social casino**: virtual coins, no cash-out, no prizes.
  2. **Real-money gambling**: licensed, geo-restricted, an entirely different business.
  3. **Prize-redeemable "sweepstakes" or skill-cash models**: their own legal category, high-risk and changing quickly state by state in the US. Do not drift from 1 into 2 or 3 by adding coin transfers, gifting marketplaces or prize redemption.
- **Store policies (background).** Apple's guideline 5.3 and Google Play's real-money gambling policy require licensing and geo-restriction for real-money play, and forbid buying real-money gambling credit through IAP. Social casino is allowed, with mature age ratings and no prizes.
- **Case law to know.** In *Kater v. Churchill Downs* (9th Cir. 2018), the court held that purchased virtual chips in *Big Fish Casino* could be "things of value" under Washington gambling law. Large class settlements followed across the industry. Purchasable chance-for-currency loops carry real litigation risk in some US states.
- **Classification.** Australia rates games with simulated gambling R18+ (since Sep 2024; volatile facts). A slot-machine *core* inside a non-casino theme (Coin Master-likes) can still count as simulated gambling. Classify early, before art and UA are locked.
- **Ethical guardrails (doctrine item 8):**
  - No marketing to minors, and a neutral age gate.
  - Optional spend and time limits plus spending summaries.
  - No hidden per-player odds manipulation (adaptive "win rate" tuning on a slot is a manipulation red flag).
  - No near-miss engineering beyond what the stated odds produce.
  - Odds disclosure for every paid random item.
  - Easy support routes for players who self-identify as vulnerable.

### 0.2 Chance math
```
RTP (return to player)    RTP = Σ_i P(outcome_i) · payout_i / bet
Hit frequency             HF = P(any payout > 0)
Volatility                σ² = Σ_i P_i · (payout_i/bet − RTP)²       (high σ = rare big wins)
Expected drain per spin   bet · (1 − RTP)
Mean spins to drain       ≈ bankroll / (bet · (1 − RTP))             (ignores variance, which ends sessions sooner)
Worked example            1,000,000 coins, bet 10,000, RTP 95% → ≈ 2,000 spins on average;
                          at bet 50,000 → ≈ 400 spins. Bet escalation, not RTP, is the main pacing lever.
Two dice (2d6)            P(sum = s) = (6 − |s − 7|) / 36 for s = 2..12; mean move 7; P(doubles) = 1/6
```
Social casino operators aren't bound by regulator RTP minimums, which makes RTP a *pacing* lever. That is exactly why transparency rules in §0.1 matter. Simulate every machine for at least 10M spins and check RTP, HF, the longest losing streak at p99 and the distribution of bonus-trigger intervals. On dice boards, compute landing frequencies per tile (Markov steady state, including "go to" tiles) before placing event tiles.

### 0.3 Energy and event economics (spins, dice, cards)
- **Return cadence** = cap ÷ regen rate. A 50-unit cap regenerating 5 per hour brings players back about every 10 hours. Notifications at full energy are the standard re-engagement hook.
- **Multipliers.** Spending k energy for a ×k outcome keeps *expected* value per energy constant. It becomes a real decision only when **event thresholds** make value non-linear (for example, a milestone that pays out when a specific tile is hit). Event stacking that rewards high multipliers is the genre's main spend driver. Make sure the decision is legible and that a low-multiplier player can still finish events.
- **Collections (cards, stickers).** Duplicates should convert into something useful (a vault, crafting, trading). Completion odds should be simulated per season. Late-set "missing card" walls are the most common complaint and a known dark pattern. Cap the expected packs needed for the final card.

### 0.4 Social graph mechanics
Invites, gifting with daily send/receive caps, friend raids and revenge, co-op partner events and clubs. Since ATT and the decline of social login, friend graphs are thinner. Design for "strangers who become friends" (clubs, partners) as well as imported contacts. Gifting must not create a transferable value channel (§0.1). Chat and voice with minors follow the defaults in `skills/genre-playbooks/references/competitive-pvp.md` §0.4.

## 1. Social casino / slots

### Definition and player fantasy
Free-to-play casino games played with virtual coins that cannot be cashed out. Slots dominate, alongside poker, blackjack and roulette, wrapped in progression and social layers. The fantasy is *Vegas excitement without the trip*: the anticipation of the spin, the big-win celebration, a growing collection of themed machines, VIP status.

### Core loop
```
pick machine → set bet → spin → win / lose → feature (free spins, bonus game, jackpot)
  → XP per coin wagered → level up → unlock machines and bet sizes
  → coins run low → hourly bonus / piggy bank / purchase → pick machine
```

### Meta loops
- **Level and machine unlocks.** Higher levels unlock higher max bets, the main escalation (§0.2).
- **VIP / loyalty tiers** earned through purchases, with perks such as better bonuses and dedicated support.
- **Missions and quests** (spin N times, trigger a bonus), **collections** (card albums, puzzle pieces) and **seasonal passes**.
- **Tournaments** on featured machines with short leaderboards. **Clubs** with team goals.
- **New-machine cadence.** Weekly releases are typical of large operators (observed). Novelty is the content.

### Session profile
Estimate: 5–20 minute sessions several times a day, timed around hourly and daily bonuses. Core payers play long sessions. Portrait has become common for slots; table games often use landscape.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Reels, paylines/ways, paytable, wilds, scatters | chance & randomness | Math model first, art second (§0.2) |
| Free spins / bonus games / pick'em / wheels | chance & randomness | Feature frequency drives excitement more than base RTP |
| Progressive or "mega" virtual jackpots | chance & randomness; social & competition | Show the jackpot ticker. Never imply cash value |
| Bet escalation with level | progression & upgrade; economy & resources | The real pacing lever. Guard against runaway bet creep |
| Hourly/daily bonuses + streaks | time & energy | The return-cadence engine (§0.3) |
| Piggy bank (coins accumulate, unlock by purchase) | economy & resources | Classic conversion offer. Show its contents honestly |
| Collections, missions, tournaments | collection & randomness; live events | Meta goals beyond the spin |

### Monetization model and typical mix
Coin packs dominate, followed by VIP and loyalty perks, piggy bank, time-limited sales, season pass, and sometimes rewarded ads for coins. Revenue concentration among high-spending payers is practitioner-reported to be extreme (qualitative, not sourced). That is the core ethical risk of this genre: build spend limits, cool-off options and vulnerability support (§0.1).

### KPI expectations
Qualitative, because no sourced ranges were found. Payer conversion tends to be low, with very high payer value and long lifetimes. UA depends on precise audience targeting and creative volume. Track coin-balance health by segment, bet-size drift, and time between purchases. Spend-velocity spikes are both a revenue signal and a welfare signal.

### Retention drivers
Hourly and daily bonuses. New machines. VIP status. Collections and seasons. Tournaments. Clubs. Familiar habit.

### Content pipeline and production scope (estimates)
A "slot factory": each machine needs a math model (paytable, reel strips, feature probabilities), symbol art, animations, a big-win sequence and audio. Weekly release cadence at top operators. Rough estimates: top social casinos run 30–150+ people. A small team can build a 5–10 machine slice in 6–12 months. UA and compliance costs make full launches hard for small studios.

### Reference titles
- *Slotomania* (Playtika)
- *House of Fun* (Playtika)
- *DoubleDown Casino* (DoubleDown Interactive)
- *Huuuge Casino* (Huuuge Games): clubs.
- *Cashman Casino* (Product Madness/Aristocrat)
- *Zynga Poker* (Zynga): table game.
- *Big Fish Casino* (Big Fish Games): central to *Kater v. Churchill Downs*.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Machines have distinctive features and great big-win moments | Reskinned machines with identical math |
| Pacing keeps balances healthy with steady feature hits | Rapid drains that force a purchase in session 1 |
| Strong VIP service and community | Generic UA with weak targeting means no payback |
| Responsible-play tools build trust | Predatory offers, regulatory and review backlash |
| Classification and legal review done before launch | A prize or transfer mechanic crosses into gambling law |

### Innovation vectors
- Narrative or meta-progression layers (travel, collections).
- Social clubs and co-op.
- Casual hybrids that borrow slot features without casino framing (see §2–3).
- Transparent odds UX.
- Responsible-play tooling as a differentiator.
- Web shops where store rules allow (see `monetization`).

### Agent-buildability: 4/5
**Why high:**
- Machine maths is pure data and simulation. Millions of headless spins verify RTP, hit frequency and volatility.
- Machines template well (one engine, data-driven reels).
- 2D symbol art and spine-free frame or tween animation fit the asset pipeline.

**Why not 5:**
- Big-win "juice" is a taste checkpoint.
- Legal and classification review is human.
- The commercial barrier (UA, compliance) is high even when the build is easy.

### Starter feature list (P0 vertical slice)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Data-driven slot engine (reels, paylines, paytable) (gameplay) | Machine loads from JSON. Payout evaluation unit-tested for every line pattern |
| 2 | Math-model simulator (tech) | 10M-spin sim reports RTP, HF, volatility and p99 losing streak within ±0.2 pp of design |
| 3 | 3 machines with different volatility profiles (content) | Each passes the simulator against its design sheet |
| 4 | Free spins + one bonus game (gameplay) | Trigger frequency matches the model within tolerance |
| 5 | Bet selector with level-gated maximum (economy) | Max bet per level from config. Sim shows no balance runaway for the casual archetype |
| 6 | XP and levels unlocking machines (meta) | Curve from `progression_calc.py`. Unlocks fire at the configured levels |
| 7 | Hourly and daily bonus with streak (meta) | Timers survive app kill and clock change. Streak grace rule unit-tested |
| 8 | Big-win celebration tiers (vfx) | Tiers at configured multiples. Skippable. Passes the visual gate |
| 9 | Coin store + piggy bank with honest content display (monetization) | Displayed content equals the granted amount. Ledger reconciles |
| 10 | Age gate + responsible-play settings (ux) | Neutral age gate. Spend and time limits enforced in tests |
| 11 | Missions (3 daily) (liveops) | Progress counts only the qualifying actions. Reset at server time |
| 12 | Compliance pre-flight for simulated gambling (release) | `compliance_preflight.py` passes. Age-rating answers recorded in the contract |

## 2. Coin Master-likes

### Definition and player fantasy
A slot-machine core serves as the resource generator for a village-building meta, asynchronous attacks and raids on other players, and card collections. Spins are the energy. The fantasy is *build and protect your village, raid your friends, complete the set*: light gambling-style thrills in a cartoon adventure frame.

### Core loop
```
spin (costs energy) → outcome: coins | attack | raid | shield | energy
  → attack or raid a target (friend, revenge, stranger) → spend coins on village items
  → village complete → next themed village → energy empty → wait / gifts / buy
```

### Meta loops
- **Villages**: themed sets of buildings with escalating costs. Completing one advances progression.
- **Card collections** from chests (random), organized in themed sets with set-completion rewards. Trading and gifting under limits.
- **Pets or helpers** that boost attack and raid outcomes.
- **Layered events**: time-boxed boosts to specific outcomes (attacks, raids, village builds), milestone reward tracks, and season-long collection events.
- **Social graph**: friends, gifting spins, revenge lists, invite rewards.

### Session profile
Estimate: 2–5 minute bursts to spend regenerated energy, several times a day. Notifications for full energy, attacks received and event starts. Portrait, one-handed.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Energy-gated slot with outcome symbols | chance & randomness; time & energy | The slot is a resource *router*. Tune outcome mix per event |
| Bet multiplier (spend k spins for ×k) | chance & randomness; economy & resources | A real decision only under event thresholds (§0.3) |
| Attack (damage a building) and raid (dig for coins) | social & competition; combat | Async. Choose targets to keep it light rather than spiteful |
| Shields | social & competition | Defence as a slot outcome. Cap stacking |
| Revenge list | social & competition | Strong re-engagement. Keep it from turning toxic |
| Village build with escalating costs | progression & upgrade | The coin sink. Pace with `economy_sim.py` |
| Card sets from chests | collection & randomness | Simulate set completion. Cap the cost of the final card (§0.3) |

### Monetization model and typical mix
Spin packs, coin packs, chests (random, so odds disclosure and loot-box rules apply), event passes and offers, and sometimes rewarded ads for spins. Viral invites and gifting cut acquisition costs. **Classification caution:** a slot core can trigger simulated-gambling ratings, for example in Australia (§0.1). Decide before UA creatives are made.

### KPI expectations
Qualitative, because no sourced ranges were found. The model relies on social virality (invites, gifting) and frequent short sessions. Track spins spent per DAU, the share of attacks that trigger revenge sessions, set completion rates, and invite conversion.

### Retention drivers
Energy regeneration. Being attacked (revenge). Village completion. Card sets. Layered events. Friends' activity.

### Content pipeline and production scope (estimates)
Village sets (5 or so buildings × several damage and upgrade states per theme), card sets (dozens of illustrations per season), pets, event templates and a large live-ops calendar. Rough estimate: 20–80 people. A small team can build a slice with 3 villages in 6–9 months.

### Reference titles
- *Coin Master* (Moon Active): the template.
- *Pirate Kings* (Jelly Button): an earlier spin-attack-raid design.
- *Dice Dreams* (SuperPlay): a dice-based variant.
- *Board Kings* (Jelly Button/Playtika): board-game cousin.
- *Monopoly Go!* (§3): the dice-board evolution.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| The spin loop routes into fun social moments (raids, revenge) | Pure slot with nothing to build. A casino without the casino appeal |
| Village themes have charm and humour | Generic art. No reason to see the next village |
| Card sets are completable with fair odds | Final-card walls and pay-gated sets |
| Events layer cleanly and stay readable | Event overload and confusing stacked rules |
| Classification and age policy handled up front | Store or regulator action over minors and simulated gambling |

### Innovation vectors
- Swapping the slot for dice, wheels or skill shots to soften gambling optics.
- Co-op team events.
- Narrative village journeys.
- Lighter social mechanics (helping instead of attacking).
- Transparent collection odds.
- Hybridization with merge or puzzle cores.

### Agent-buildability: 4/5
**Why high:**
- The slot router, energy economy and async raids are deterministic and fully simulatable (spin-economy sims, collection-completion sims).
- 2D village art suits a style-locked pipeline.

**Why not 5:**
- The social graph and event operations need a backend (Firebase or Nakama) and a staffed live-ops calendar.
- Charm and humour in themes are taste checkpoints.

### Starter feature list (P0 vertical slice)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Energy-gated slot with outcome router (gameplay) | Outcome frequencies match config within ±0.5 pp over 1M spins |
| 2 | Energy regen + cap + full-energy notification (meta) | Regen correct across background and kill. Notification honours consent |
| 3 | Bet multiplier (gameplay) | Spends k units, multiplies outcomes by k. Unlocks at the configured balance |
| 4 | Attack and raid vs async targets (social) | Target selection rules unit-tested. Results persisted server-side |
| 5 | Shields with cap (meta) | Shield blocks one attack. Stack cap enforced |
| 6 | Village with 5 buildings × 4 states, 3 villages (content) | Costs per table. Sim days-to-complete within ±15% of contract |
| 7 | Card chests + sets + duplicate conversion (meta) | Set-completion sim reports expected chests per set. Final-card cap honoured |
| 8 | Friends, gifting with daily caps, revenge list (social) | Caps enforced. Gifts not transferable as tradable value |
| 9 | One layered event with milestone track (liveops) | Points only for qualifying outcomes. Track pays out per tier |
| 10 | Store: spin packs + chests with odds disclosure (monetization) | Odds one tap away. Ledger reconciles |
| 11 | Age gate + classification record (release) | Age gate shown at first launch. Rating rationale stored in the contract |
| 12 | FTUE to first raid in 2 min or less (ux) | Scripted playthrough reaches the first raid and village build within 120 s |

## 3. Board-game casual (Monopoly Go-style)

### Definition and player fantasy
Roll dice to move around a board. Landing tiles grant currency, trigger raids, mini-games and event points. Spend currency on landmarks to complete boards. All of it sits under a dense, layered live-ops event system and a seasonal sticker-album collection. The fantasy is *board-game nostalgia with jackpot energy*: the big multiplier roll, building your board, beating friends, finishing the album.

### Core loop
```
choose roll multiplier → roll 2d6 → move → tile outcome (cash, raid, chance, tax, event points)
  → build landmarks → board complete → next board → dice empty → regen / rewards / buy
```

### Meta loops
- **Sticker albums.** Seasonal sets earned from event packs, with rarities, duplicate conversion and friend trading with limits. Special trading windows for rare stickers.
- **Concurrent events.** A main milestone event, short tournaments and side events at the same time. Each rewards landing on specific tiles, which drives multiplier decisions (§0.3).
- **Partner / co-op events** with friends building a shared goal.
- **Raids** (shutdowns, heists) on other players. Shields.
- **Mini-games** (plinko-style, wheels) as event rewards.

### Session profile
Estimate: 2–10 minute bursts several times a day, synchronized to dice regen and event start times. Portrait, one-handed. Big events produce longer "dice dump" sessions.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| 2d6 movement on a loop board | chance & randomness | Use tile-landing frequencies (§0.2) to price tiles and place event tiles |
| Roll multiplier | economy & resources; chance & randomness | The central decision. Value only becomes non-linear near event tiles |
| Landmark building with escalating costs | progression & upgrade | Board completion as the progression unit |
| Raids (shutdown, heist) + shields | social & competition | Light conflict. Mini-game framing softens it |
| Sticker albums with trading | collection & randomness; social & competition | Album completion is the season's long goal. Cap final-sticker cost |
| Layered event milestones and tournaments | live events | The revenue engine. Requires a disciplined calendar |
| Co-op partner events | social & competition | Turns friends into retention |

### Monetization model and typical mix
Dice packs, event-timed offers, album-related packs (random, so odds disclosure applies), flash sales, and passes. IP licensing (Hasbro for *Monopoly*) is a fixed cost and a UA advantage. Not sourced: no public breakdown of the revenue split was found.

### KPI expectations
Qualitative, because no sourced ranges were found. The genre is live-ops-intensive: revenue follows the event calendar. Track dice spent per event, multiplier distribution near event tiles (look for manipulation risk and confusion), album completion by spender segment, and partner-event participation.

### Retention drivers
Dice regeneration. Several daily event beats. Album season. Partner events with friends. Raids and revenge. Board novelty.

### Content pipeline and production scope (estimates)
Boards (themed landmark art sets), hundreds of stickers per album season, event templates, mini-games and a large live-ops and CRM team. Rough estimate: 50–200 people at top scale. A slice with 2 boards and one event is feasible in 6–9 months for a small team.

### Reference titles
- *Monopoly Go!* (Scopely, 2023): the template, IP-led.
- *Dice Dreams* (SuperPlay): dice-kingdom variant.
- *Board Kings* (Jelly Button/Playtika): an earlier board-raid design.
- *Coin Master* (§2): the slot-router cousin.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Recognisable board-game feel and big roll moments | A generic board with no theme or IP pull |
| Events layer into one readable daily rhythm | Opaque stacked rules that make players feel tricked |
| Album seasons are completable for engaged non-payers | Final-sticker walls |
| Social co-op and partners | Raid-heavy toxicity |
| A strong live-ops cadence and CRM | Thin event calendar. Dice with nothing to spend on |

### Innovation vectors
- Non-dice movement (cards, spinners) for pacing control.
- Co-op boards.
- Narrative boards.
- Skill elements in mini-games.
- Transparent multiplier helpers ("best multiplier now" hints).
- Smaller, IP-free cozy board games.
- Integration with real board-game brands.

### Agent-buildability: 4/5
**Why high:**
- The board, dice, events and albums are deterministic systems with exact probability models (Markov landing frequencies, `gacha_calc.py` for packs, `economy_sim.py` for dice flow).
- 2D or 2.5D board art.
- UI-heavy, so structural checks apply.

**Why not 5:**
- Success depends on IP, UA and an event-operations machine that agents can template but not staff.
- Event-rule clarity needs human playtests.

### Starter feature list (P0 vertical slice)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Board engine: 40 tiles, 2d6 movement, special tiles (gameplay) | Empirical landing frequencies match the Markov model within ±0.3 pp over 1M rolls |
| 2 | Dice energy + regen + cap (meta) | Regen correct across background and kill |
| 3 | Roll multiplier with unlock thresholds (gameplay) | Outcome scaling unit-tested. Unlocks per balance tier |
| 4 | Landmark building, 2 boards (content) | Costs per table. Sim days-per-board within ±15% of contract |
| 5 | Raid tile → raid mini-game vs async target (social) | Target rules unit-tested. Shield blocks per rule |
| 6 | Milestone event with tile-based points (liveops) | Points only from configured tiles. Milestones pay per tier |
| 7 | Short tournament with leaderboard (liveops) | Ranking ties resolved deterministically. Rewards per bracket |
| 8 | Sticker album with packs, duplicates and stars vault (meta) | Completion sim reports expected packs. Final-sticker cap honoured |
| 9 | Friends + gifting with caps (social) | Caps enforced. No transferable value channel |
| 10 | Offers: dice packs with odds disclosure for random packs (monetization) | Odds one tap away. Ledger reconciles |
| 11 | Event calendar from remote config (liveops) | Events switch without a client update. Time zones correct |
| 12 | Multiplier clarity UI (ux) | Shows the event value of the next landing. Playtest comprehension at or above the contract target |

## 4. Party and social deduction

### Definition and player fantasy
Short multiplayer sessions where the fun comes from the other people. There are three families:
- **Social deduction**: hidden roles, discussion, voting (*Among Us*, Werewolf/Mafia formats).
- **Party mini-game collections** and elimination party BRs (*Stumble Guys*, *Eggy Party*).
- **Phone-as-controller couch games and creative judging games**, where players or an AI judge submissions (*Death by AI*).

The fantasy is *laughing with friends*: bluffing, betrayal, absurd moments and stories worth retelling.

### Core loop
```
create / join lobby (code or matchmaking) → roles or round rules assigned → play round
  (tasks + sabotage, mini-game, prompt) → discuss / vote / judge → reveal → score → next round or rematch
```

### Meta loops
- **Cosmetics**: hats, skins, pets, emotes, as self-expression in a social space.
- **Account level and pass** with cosmetic rewards.
- **Friends, private lobbies, host controls.** Custom rule settings let groups make the game their own.
- **UGC maps or prompts** (creator ecosystems). AI-assisted creation has shown strong engagement in some titles (volatile facts).

### Session profile
Estimate: 10–20 minute lobbies made of 1–5 minute rounds. Evenings and weekends. Group play is often coordinated outside the game (Discord, calls). Portrait or landscape by title.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Hidden roles with asymmetric goals | social & competition | The core tension. Balance role ratios to lobby size |
| Meeting / discussion / vote | social & competition | Needs strong timers and an ejection reveal. Mobile typing is slow, so quick-chat helps |
| Tasks as cover and progress | combat; UX automation | Gives innocents something to do and a win condition |
| Sabotage and kill cooldowns | combat | Pacing levers for the impostor side |
| Lobby codes, host settings, rematch | UX automation; social & competition | Frictionless group formation is the product |
| Ghost/spectator play after elimination | social & competition | Keeps eliminated players engaged. *Among Us* lets ghosts finish tasks |
| Prompt-and-judge rounds (human or AI judge) | social & competition | AI judging needs moderation, report flows and consent disclosures |

### Monetization model and typical mix
Cosmetics (direct purchase and bundles), a pass, ad removal, and rewarded or interstitial ads between rounds (never during discussion). Premium price on some platforms. Paid power is essentially absent and would break the social contract.

### KPI expectations
Qualitative, because no sourced ranges were found. The genre is prone to viral spikes and steep decay (the 2020 *Among Us* surge is the archetype). Track lobby fill time, share of private vs public lobbies, rematch rate, report rate per 1,000 lobbies, and friend invites per DAU.

### Retention drivers
Friend groups (the dominant driver). New roles and maps. Creator content and streamers. Cosmetic expression. Seasonal events.

### Content pipeline and production scope (estimates)
Maps, roles and mini-games, plus cosmetics. Then networking (relay or P2P with host migration), moderation (text filters, report and review, voice safety), and anti-cheat. Rough estimates:
- Small team: 3–10 people over 9–18 months. *Among Us* came from a very small studio.
- Party mini-game collections with UGC: 30+ people.

### Reference titles
- *Among Us* (Innersloth, 2018; 2020 surge): mobile social deduction.
- Werewolf/Mafia-format apps: the classic voice- and text-led formula.
- *Heads Up!* (Warner Bros., 2013): phone-as-prop party game.
- *Stumble Guys* (Kitka Games, 2021): party elimination.
- *Eggy Party* (NetEase): party BR with AIGC UGC.
- *Death by AI* (Little Umbrella): AI-judged party game.
- *Mentiss Werewolf*: AI opponents built on frontier LLMs (volatile facts).

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Joining a friend takes seconds | Accounts, downloads and codes create friction |
| Rules are learnable in one round | Role complexity confuses first-timers |
| Moderation keeps lobbies fun and safe | Toxic or unsafe chat, especially with minors |
| Streamer-friendly moments | Nothing memorable or clip-worthy |
| Rules and roles keep arriving | One map and one mode. The fad fades |

### Innovation vectors
- LLM-driven players or judges that fill lobbies and enable solo play, with disclosure, moderation and the AI-consent rules in `legal-ethics`.
- Voice-first formats with safety tooling.
- Async social deduction.
- Cross-platform lobbies.
- UGC role and map creation with AI assistance.

### Agent-buildability: 2/5
**Why low:**
- Small-lobby real-time networking with host migration and reconnection.
- Moderation and child-safety systems.
- The fun lives in human interaction, which no automated gate can verify.

**What helps:**
- Deterministic round logic is testable.
- LLM agents can play social deduction for smoke tests, but they don't replace human playtests.

### Starter feature list (P0 vertical slice: 6-player social deduction)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Lobby create/join by code + host settings (ux) | Join in 3 taps or fewer. Settings sync to all clients |
| 2 | Relay networking with host migration + reconnect (tech) | Host drop migrates within 5 s. Reconnect restores role and state |
| 3 | Role assignment with configurable ratios (gameplay) | Assignment uniform over 100k draws (chi-square passes) |
| 4 | Movement + 6 tasks on one map (gameplay) | Scripted playthrough completes every task |
| 5 | Impostor kill + cooldown + sabotage (gameplay) | Cooldowns from config. Sabotage resolves per rules |
| 6 | Body report → meeting → vote → ejection reveal (gameplay) | All vote outcomes, including ties and skips, unit-tested |
| 7 | Quick-chat + optional text chat with filters (ux) | Filter blocks the test list. Text chat off by default for minors |
| 8 | Ghost mode for eliminated players (gameplay) | Ghosts can finish tasks and cannot affect votes |
| 9 | Win conditions both sides (gameplay) | All end states reachable in scripted multi-client playthroughs |
| 10 | Report / mute / block + moderation log (ux) | Reports logged with lobby replay context |
| 11 | Bot or LLM players for smoke tests (tech) | 6-bot lobby completes 50 rounds with no softlock |
| 12 | Cosmetic shop + equip (monetization) | Equipped cosmetics sync to every client. No gameplay effect |

## 5. Bingo

### Definition and player fantasy
Players daub called numbers on one or more cards, racing others to complete patterns. Mobile bingo wraps this in power-ups, collections and travel-themed rooms. Two standards:
- **75-ball** (US): 5×5 cards, free centre.
- **90-ball** (UK): 3×9 tickets, 15 numbers each, one line / two lines / full house.

The fantasy is *a sociable, low-stakes thrill*: the near-bingo tension, the shout of victory, a relaxing routine with a community.

### Core loop
```
choose room (theme, buy-in) → buy 1–4 cards (credits) → numbers called → daub (manual or auto)
  → power-ups charge and trigger → first to pattern = bingo → rewards (coins, collection items, XP) → next round
```

### Meta loops
- **Room progression**: travel-themed rooms unlocked by level, with collections per room (puzzle pieces, items).
- **Power-ups** charged by daubing (instant daubs, extra rewards, coin bonuses).
- **Events and tournaments.** Clubs and teams with shared goals. Season pass.
- **Mini-games** between rounds (scratchers, wheels). These are chance mechanics, so §0.1 applies.

### Session profile
Estimate: 2–5 minute rounds, several rounds per session, multiple sessions a day. Portrait. Strong habitual play.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Synchronized ball calls across a room | chance & randomness; social & competition | Server-generated calls. Every client sees the same sequence |
| Multi-card play (commonly up to 4) | chance & randomness; UX automation | More cards, more chances, higher cost. Readability limits the card count on phones |
| Manual daub vs auto-daub | UX automation | Manual daub is the engagement. Offer auto-daub as an accessibility option |
| Power-ups charged by daubs | progression & upgrade; chance & randomness | Adds agency to a pure-chance game |
| Patterns and bingo race with limited winners | social & competition | Limit bingos per round to create urgency |
| Collections per room | collection & randomness | The long-term goal. Simulate completion |
| Buy-in credits + payouts | economy & resources | Keep it social-casino only (§0.1). Real-money "skill bingo" is a separate legal category |

**Bingo math.** In 75-ball with one card, the call count needed to complete a line follows a distribution you can simulate cheaply. Run 1M simulated rounds per room configuration (card count, pattern, players) to set rewards, limits on winners per round and power-up charge rates. Use `economy_sim.py` for credit flows.

### Monetization model and typical mix
Credit and coin packs, power-up packs, VIP, season pass, collection boosters, and rewarded ads for credits in lighter titles. Players skew toward older, highly engaged audiences (practitioner-reported, not sourced). That makes respectful UX and responsible spend tools important.

### KPI expectations
Qualitative, because no sourced ranges were found. Habit-driven, with long lifetimes among core players. Track rounds per DAU, card count per round, credit balance health, and collection completion.

### Retention drivers
Habit and routine. Room travel and collections. Clubs and community. Events. Power-up progression.

### Content pipeline and production scope (estimates)
Rooms (theme art, collections), power-ups, events and mini-games, plus server ball-call infrastructure. Rough estimate: 10–40 people. A slice with 3 rooms is feasible in 4–8 months.

### Reference titles
- *Bingo Blitz* (Playtika): travel rooms, collections.
- *Bingo Bash*: power-ups and events.
- *Bingo Pop* (Jam City).
- *Blackout Bingo* (Big Run Studios): runs real-money skill tournaments through a third-party platform, a legally distinct category.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| Daubing feels satisfying and readable, even across 4 cards | Small numbers, missed daubs, eye strain |
| Power-ups add agency and excitement | Pure chance with no player input |
| Rooms and collections give long goals | Grindy collections with final-item walls |
| Clubs make it social | No community features |
| Accessibility for older players (text size, auto-daub, contrast) | Tiny UI, aggressive pop-ups |

### Innovation vectors
- Narrative and travel metas.
- Co-op team bingo.
- Live-hosted rooms with streamer formats.
- Accessibility-first design for older audiences.
- Bingo hybrids with puzzle or merge metas.
- Responsible-play tooling as a trust feature.

### Agent-buildability: 4/5
**Why high:**
- Rules are simple and deterministic, with server-side calls.
- Simulation sets rewards precisely.
- UI-heavy (structural checks for readability).
- 2D themed art.

**Why not 5:**
- Real-time rooms with synchronized calls need a backend.
- Theme charm and the community layer need humans.

### Starter feature list (P0 vertical slice: 75-ball)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Card generator (75-ball rules) (gameplay) | Every card valid (column ranges, free centre). 100k-card uniqueness test passes |
| 2 | Server-seeded synchronized ball calls (tech) | Two clients receive identical sequences and timing within 200 ms |
| 3 | Manual daub + auto-daub option (ux) | Auto-daub never misses. Manual daub has touch targets of 44 pt or more |
| 4 | Pattern detection (line, corners, blackout) (gameplay) | Unit tests for every pattern. Bingo claim validated on the server |
| 5 | Multi-card play (1–4) (gameplay) | 4-card layout passes structural readability checks on a 5.5" screen |
| 6 | Bingo race with winners limit (gameplay) | Round ends at N winners. Ties resolved by server timestamp |
| 7 | Power-ups charged by daubs (3 types) (gameplay) | Charge rates from config. Effects unit-tested |
| 8 | Rooms (3) with buy-ins and payouts (economy) | Sim: credit drain per round within the contract band per archetype |
| 9 | Collection items per room (meta) | Completion sim reports expected rounds. Final-item cap honoured |
| 10 | Bot players for room fill and tests (tech) | Room with 30 bots completes 100 rounds with no desync |
| 11 | Accessibility: text size, high contrast, call voice-over (ux) | Settings persist. Contrast meets WCAG AA (see `accessibility-localization`) |
| 12 | Store + responsible-play limits (monetization) | Limits enforced in tests. Ledger reconciles |

## 6. Casual sports (golf, pool)

### Definition and player fantasy
Turn-based or simultaneous 1v1 sports with physics-driven shots. Golf, pool, carrom, darts, archery and bowling, usually played against real opponents with coin buy-ins per table or tour. The fantasy is *the perfect shot*: a satisfying physics moment, beating a rival, climbing to higher-stakes tables.

### Core loop
```
choose tour / table (coin buy-in) → matchmake → 1v1 match (aim, power, spin; take turns or shoot simultaneously)
  → winner takes the pot (coins) + chest → open chest → upgrade club or cue → higher tour
```

### Meta loops
- **Equipment collection and upgrades.** Clubs, cues, balls with stats (aim guide length, power, spin), usually from chests. The pay-to-win flashpoint.
- **Tours and tables** with escalating buy-ins (the economy ladder).
- **Chest timers and slots**, a *Clash Royale*-style pacing system.
- **Leagues, clubs, events, pass.**

### Session profile
Estimate: 1–5 minute matches, 3–10 per session, several sessions a day. Portrait for pool, both orientations for golf. One finger.

### Signature mechanics
| Mechanic | `mechanics-codex` category | Design note |
|---|---|---|
| Aim + power + spin with a timing meter | combat | Skill expression in one gesture. A "perfect" window rewards precision |
| Deterministic ball physics | combat | Server replay validation and anti-cheat (§0.3 in `skills/genre-playbooks/references/competitive-pvp.md`) |
| Aim-guide length as an upgrade | progression & upgrade | Strong pay-to-win perception. Normalize it in ranked |
| Wind, lies, terrain (golf) | combat | Readable variables. Show them clearly |
| Coin buy-in tables and pots | economy & resources | Virtual-only (§0.1). Escalating tables are the sink ladder |
| Chests with timers and slots | collection & randomness; time & energy | Loot-box rules apply. Show odds |
| Simultaneous turns (both play the same hole) | social & competition | Cuts waiting time compared with alternating turns |

**Shot validation.** Clients send `(aim, power, spin, timing)`. The server re-simulates with fixed-point physics and confirms the result. This blocks trajectory hacks and enables replays. A shot-search bot (grid search over aim and power) estimates shot difficulty and powers both AI opponents and balance checks.

### Monetization model and typical mix
Chests and equipment (random items, so odds disclosure applies), direct equipment purchases, coin packs (buy-ins), pass, VIP, cosmetics. Equipment power is the main review risk. Offer level-normalized ranked play.

### KPI expectations
Qualitative, because no sourced ranges were found. Matches are short and social, and ladders are long. Track matches per DAU, coin balance by tour, the win rate of equipment-advantaged players (a fairness metric), and chest-slot idle time.

### Retention drivers
The next-tour ladder. Chest timers. Equipment chase. Rivals and friends. Leagues and events. Personal skill growth.

### Content pipeline and production scope (estimates)
- **Pool**: one table, physics and cue art. 3–10 people over 6–12 months.
- **Golf**: 3D courses with terrain, wind and many holes. 10–30 people over 12–24 months.
- **Both**: server physics validation and matchmaking.

All estimates.

### Reference titles
- *8 Ball Pool* (Miniclip): cue stats, coin tables.
- *Golf Clash* (Playdemic, 2017): simultaneous 1v1 golf, timing needle.
- *Golf Battle* (Miniclip): multiplayer mini-golf.
- *Carrom Pool* (Miniclip).
- *Archery King* and *Basketball Stars* (Miniclip): the one-gesture sports family.

### What makes it succeed / fail
| Succeeds when | Fails when |
|---|---|
| The shot gesture feels precise and satisfying | Physics feels random or floaty |
| Fair matchmaking by skill and equipment | Equipment buys wins and drives review backlash |
| Short matches with little waiting | Long alternating turns with idle time |
| Server-validated physics keeps cheaters out | Aim-hack tools dominate |
| Tours give a clear economic ladder | Coin drains with no path upward |

### Innovation vectors
- Simultaneous play modes.
- Creative variants: mini-golf course builders, trick shots.
- Party modes for 4–8 players.
- Async challenge links.
- Normalized ranked as standard.
- Physics puzzles as single-player campaigns.

### Agent-buildability: 3/5 (2D pool 4/5)
**Why mid:**
- Turn-based, deterministic physics with server re-simulation.
- Shot-search bots for AI and balance.
- Async-friendly.
- 2D pool art is light.

**Why not higher:**
- Shot *feel* (gesture mapping, timing windows, camera) needs on-device human tuning.
- Golf adds 3D terrain and course art.
- Matchmaking needs a backend.

### Starter feature list (P0 vertical slice: 8-ball pool)
| # | Feature (area) | Acceptance criterion |
|---|---|---|
| 1 | Fixed-point 2D ball physics (tech) | 1,000 recorded shots replay identically on 2 devices |
| 2 | Aim + power + spin gesture with guide line (gameplay) | Scripted gestures produce the expected cue vectors. Guide matches the first-contact prediction |
| 3 | 8-ball rules engine (fouls, ball-in-hand, win/loss) (gameplay) | Unit tests cover every rule case |
| 4 | Shot-search AI, 3 levels (gameplay) | Level win-rate ladder within contract bands over 500 matches |
| 5 | Async or turn-based PvP with server re-simulation (tech) | Server result equals client. Tampered shot rejected |
| 6 | Tables with coin buy-ins and pots (economy) | Pot math reconciles. Sim shows balance stability per archetype |
| 7 | Cue collection with stats + ranked normalization (meta) | Normalized mode ignores stats (unit test) |
| 8 | Chests with timers, slots and odds (monetization) | Odds one tap away. Timers correct across background and kill |
| 9 | Glicko-2 rating + leagues (meta) | Updates per formula. League thresholds unit-tested |
| 10 | Shot feedback: sound, ball spin, pocket VFX (vfx) | Passes `game-feel` checklist and visual gate |
| 11 | Turn timer + reconnect (ux) | Timeout ends the turn. Reconnect within 15 s resumes |
| 12 | FTUE: first pocketed ball in 30 s or less (ux) | Scripted new-player run pockets a ball in the tutorial within 30 s |

## Volatile facts (as of Oct 2026 — verify before relying)

- Since Sep 22, 2024, Australia classifies games with simulated gambling R18+ and games with paid chance-based items at least M — [PCWorld](https://www.pcworld.com/article/2464538/all-games-with-loot-boxes-will-be-rated-m-or-higher-in-australia.html); [PocketGamer.biz](https://www.pocketgamer.biz/australia-sets-new-rules-for-video-games-with-gambling-like-content)
- Belgium has banned paid loot boxes since 2018. Brazil's ECA Digital bans loot-box sales to under-18s from March 2026 — [Programming Insider](https://programminginsider.com/loot-boxes-regulation-and-where-the-line-sits-in-2026/)
- Apple's age-rating tiers are now 4+, 9+, 13+, 16+ and 18+, and updated questionnaire answers were due Jan 31, 2026 — [Apple Upcoming Requirements](https://developer.apple.com/news/upcoming-requirements/)
- US age-assurance laws (Texas from Jan 1, 2026, Utah May 7, 2026, Louisiana Jul 1, 2026) route through Apple's Declared Age Range API — [9to5Mac](https://9to5mac.com/2025/11/04/app-store-texas-sb2420-new-apis/)
- Casual and hyper-casual each took about 40% of game ad revenue (Feb–Apr 2026). Ads were 70.3% of game revenue in India vs 22.1% in the US (Jan–May 2026) — [Sensor Tower](https://sensortower.com/blog/gaming-deep-dive-ad-monetization-report); [GameDev Reports](https://gamedevreports.substack.com/p/sensor-tower-mobile-game-ad-monetization)
- AI-native party and social titles (aggregator data, unverified): *Death by AI* reported 20M players in 3 months. *Mentiss Werewolf* uses AI opponents built on Claude, GPT and Gemini. *Eggy Party*'s AIGC tools produced 1M+ player-made items — [NexWorld panorama](https://nexworld.wiki/en/ai-games/ai-games-panorama-2026/). One report says *Eggy Party* UGC-map revenue rose 40% month on month after AIGC — [36Kr](https://eu.36kr.com/en/p/3394131222956417)
- Apple guideline 5.1.2(i) (Nov 2025) requires disclosure and explicit consent before sharing personal data with third-party AI services. This is relevant to AI judges and AI players — [Radom](https://www.radom.com/insights/apple-updates-app-review-guidelines-to-strengthen-privacy-protections-against-third-party-ai-data-sharing)
- Retention anchors (all genres): median D1 about 22%, D7 under 4%, D30 0.7–0.8% — [Segwise (GameAnalytics)](https://segwise.ai/blog/mobile-gaming-app-user-retention-strategies)

## Related skills
- `legal-ethics`: simulated gambling, loot boxes, age ratings, sweepstakes risk.
- `economy-design`: energy economies, coin sinks, collection completion.
- `liveops`: layered event calendars, tournaments, seasons.
- `monetization`: offers, piggy banks, passes, responsible-spend tools.
- `multiplayer-backend`: synchronized rooms, lobbies, async PvP, shot validation.
- `player-psychology`: variable rewards, near-misses, vulnerable players.
- `mechanics-codex`: chance, social and collection mechanic cards.
- `accessibility-localization`: older-audience readability, auto-daub.
- `marketing-ua`: social virality, invite loops, creative testing.
