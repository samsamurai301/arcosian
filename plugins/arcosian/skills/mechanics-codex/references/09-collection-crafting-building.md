# 09 — Collection, Crafting and Building Mechanics

Collection, crafting and building mechanics are the "ownership" layer of a game: the player gathers things, converts them into better things, and arranges them into a place that is theirs. On mobile they carry most mid- and long-term retention in farm, merge, city, base-builder, creature-collector and cozy games, and they are where economies leak (arbitrage, hoarding, storage walls) and where monetization pressure collects (timers, paid random eggs, last-item walls). This file catalogues 20 mechanics in the shared mechanic-card format: set bonuses, catalogues and albums, recipe and discovery crafting, storage pressure, defensive base layouts, HQ-gated building, city zoning, farming cycles, free-placement decoration, judged design challenges, creature capture, breeding, branching evolution, fusion tables, virtual pets, merge-2 boards, merge-3 worlds, order boards and production chains. Every entry gives precise rules, tuning ranges, the maths that matters, failure modes, a mobile verdict, the monetization hook with its ethical limit, and an implementation sketch. Seasonal albums, renovation metas and numeric hero ascension live in `05-progression-meta-mechanics.md`; the economy-side views of crafting chains, storage caps, build queues and production bottlenecks live in `04-economy-resource-mechanics.md`; the puzzle-side merge overview is `merge` (03); raids and trading are in file 06; timers and energy are in file 08. This file goes deeper on the player-facing structure, the maths and the build.

**Entry format.** Every entry maps 1:1 onto `${CLAUDE_PLUGIN_ROOT}/scripts/schemas/mechanic-card.schema.json` (`id`, `name`, `category`, `player_fantasy`, `rules`, `parameters`, `dynamics`, `aesthetics`, `feedback`, `failure_modes`, `mobile_fit`, `references`, `combos`). Ids are kebab-case; ids from sibling files carry their file number, e.g. `trading` (06). Aesthetic targets use the eight MDA aesthetics (Hunicke, LeBlanc and Zubek, 2004): Sensation, Fantasy, Narrative, Challenge, Fellowship, Discovery, Expression, Submission. Tuning ranges are practitioner starting points, not measured industry benchmarks: put them in data, then confirm with `economy_sim.py` and playtests.

## Contents

1. Index of mechanics · 2. Choosing a stack · 3. Collection (09.01–09.02) · 4. Crafting and inventory (09.03–09.05) · 5. Building and self-expression (09.06–09.11) · 6. Creatures (09.12–09.16) · 7. Merge, orders and production (09.17–09.20) · 8. Cross-cutting maths, audit checklist, related skills

## 1. Index of mechanics

| # | Id | Mechanic | Primary job | One-hand | Session fit |
|---|---|---|---|---|---|
| 09.01 | `set-bonuses` | Set bonuses | Build identity from assembling pieces | yes | menu, any |
| 09.02 | `collection-log` | Catalogues, dex and museums (incl. albums) | Completion drive with a visible end | yes | 10–60 s browse |
| 09.03 | `recipe-crafting` | Recipe crafting | Convert gathered inputs into needed outputs | yes | 1–5 min |
| 09.04 | `discovery-crafting` | Combinatorial discovery crafting | Reasoning-and-reveal loop | yes | 1–3 min |
| 09.05 | `storage-capacity` | Storage caps and inventory pressure | Force sinks and decisions | yes | check-in |
| 09.06 | `base-defense-layout` | Defensive base layout (async PvP) | Expression that others test | layout: two-hand; attack: yes | 3 min attacks |
| 09.07 | `hq-gated-building` | HQ-gated building upgrades | Paced growth with parallel planning | yes | appointment |
| 09.08 | `city-zoning` | City zoning, adjacency and coverage | Spatial optimisation | mostly | 3–10 min |
| 09.09 | `farming-cycle` | Plant–grow–harvest cycles | Ritual real-time production | yes | 1–3 min |
| 09.10 | `free-placement-decor` | Free-placement decoration and housing | Self-expression | mostly | open-ended |
| 09.11 | `design-challenge` | Themed design challenges with judging | Scored, social expression | yes | 2–5 min |
| 09.12 | `creature-collection` | Creature capture and collection | Hunt and catalogue | yes | 10–30 s encounters |
| 09.13 | `creature-breeding` | Breeding and genetics | Generative discovery | yes | async |
| 09.14 | `branching-evolution` | Branching evolution | Transformation with identity choice | yes | moments |
| 09.15 | `fusion-tables` | Fusion tables | Deterministic combine-and-sacrifice planning | yes | menu |
| 09.16 | `virtual-pet` | Pet care and visitor collection | Nurture and attachment | yes | 30–90 s |
| 09.17 | `merge-board` | Merge-2 board with generators | Tidy-and-upgrade core loop | yes | 3–8 min (energy) |
| 09.18 | `merge-world` | Merge-3 open world | Patience-rewarding merge sandbox | mostly | 5–15 min |
| 09.19 | `order-board` | Order and delivery boards | Directed short-term goals | yes | any |
| 09.20 | `production-chain` | Production chains | Flow optimisation | yes | check-in |

## 2. Choosing a stack

| Concept type | Spine (pick 1) | Layers (pick 2–4) | Avoid early |
|---|---|---|---|
| Merge casual (story merge) | `merge-board` | `order-board`, `storage-capacity`, `renovation-meta` (05), `energy-stamina` (08) | production chains deeper than 2 |
| Farm / town sim | `farming-cycle` | `production-chain`, `order-board`, `storage-capacity`, `free-placement-decor` | async PvP raiding |
| Base builder / 4X | `hq-gated-building` | `base-defense-layout`, `production-chain`, `storage-capacity`, `research-trees` (05) | multi-day timers in week 1 |
| Creature collector | `creature-collection` | `branching-evolution`, `creature-breeding`, `collection-log` | `fusion-tables` before D7 |
| Survival / sandbox crafting | `recipe-crafting` | `storage-capacity`, `set-bonuses`, `free-placement-decor` | order boards (they fight self-direction) |
| Cozy / expression | `free-placement-decor` | `design-challenge`, `collection-log`, `virtual-pet` | storage pressure, loss mechanics |
| City builder | `city-zoning` | `hq-gated-building`, `production-chain`, `order-board` | raiding |

Rule of thumb: one converter-type mechanic (crafting, chains, merge) is the engine; one placement-type mechanic (base, city, decor) is the showcase; one collection-type mechanic is the long tail. More than one of each before D7 overloads a phone-sized UI.

## 3. Collection

### 09.01 Set bonuses — `set-bonuses`

- **Category:** collection · power or identity layer
- **Player fantasy:** "Assembling the full set makes me more than the sum of my parts."
- **Core rules:**
  - *State:* items tagged with `set_id`; equipped or placed items; set definitions `{set_id, pieces[], thresholds: {2: bonusA, 4: bonusB}}`.
  - *Triggers:* equip/unequip, place/remove (decor sets), acquire (passive collection sets).
  - *Effects:* count distinct active pieces per set; apply every threshold reached; bonuses from different sets stack only within slot limits.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Pieces per set | 3–6 (gear), 5–12 (decor/collectibles) | Larger sets lengthen the farm and the build commitment |
| Threshold steps | 2/4 of 4–5 slots, or 3/5 | Partial thresholds allow "2+2" hybrids — the core build decision |
| Bonus magnitude | partial +5–15 %; full set +15–30 % or a rule change | Rule-changing full-set effects create identity; flat stats feel dull |
| Best off-set item value | 80–95 % of a set piece | If off-set always loses, sets become mandatory and builds converge |
| Piece sources | one set per dungeon, boss or event | Creates targeted farming loops and a reason to revisit content |

- **Dynamics:** hybrid builds; target farming of one source; theorycrafting; meta convergence when one set dominates.
- **Aesthetic targets (MDA):** Challenge (optimisation), Expression (build identity), Submission (farming).
- **Feedback and juice:** tooltip tracker ("Ember 3/4 — next: burning trail"); glow when a threshold activates; before-equip preview of gained/lost bonuses.
- **Failure modes and exploits:** one mandatory meta set; power pieces only in paid random sources (pay-to-win); tooltip overload in portrait; bonuses silently dropping when a piece is swapped.
- **Mobile fit:** menu play, one hand. Provide "equip recommended" with an explanation, and a compare view that fits portrait.
- **Monetization hooks and the ethical limit:** cosmetic theme sets are safe to sell directly. Power pieces must never be exclusive to paid random sources; if sold, disclose odds and keep a deterministic crafting path (`recipe-crafting`).
- **Implementation notes:** recompute on every loadout change; never persist computed bonuses (data patches change thresholds).

```text
active_bonuses(equipped):
  counts = Counter(i.set_id for i in equipped if i.set_id)
  for set_id, n in counts: for t in sorted(SETS[set_id].thresholds): if n >= t: yield SETS[set_id].thresholds[t]
```
- **Reference games:** Diablo III and IV (item sets), Genshin Impact (2- and 4-piece artifact sets), World of Warcraft (tier sets), Animal Crossing: New Horizons (furniture series scored by the Happy Home Academy).
- **Combines well with:** `recipe-crafting`, `free-placement-decor`, `loot-tables` (07), `gear-rarity` (05).

### 09.02 Catalogues, dex and museums — `collection-log`

- **Category:** collection · completion tracker (seasonal albums are a variant; see `collections-albums` (05))
- **Player fantasy:** "I'm documenting this whole world — every gap is a lead."
- **Core rules:**
  - *State:* entries `{id, group, rarity, source_hint, status: unknown|seen|owned|researched}`; per-group completion; optional research target (catch or donate N).
  - *Triggers:* encounter (→ seen), acquisition (→ owned), repeat acquisition or donation (→ researched).
  - *Effects:* each status step reveals information (habitat, lore, stats); group milestones at 25/50/75/100 % grant rewards; full completion grants a capstone (title, cosmetic, charm).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Catalogue size | 60–150 at launch; +10–20 % per content update | Bigger = longer tail; always show the total so players see the end |
| Unknown visibility | silhouette + hint / "???" / hidden count | Silhouettes create targeted goals; hidden entries add surprise but frustrate completionists |
| Milestone spacing | every 10–25 % of a group | Keeps the long tail rewarding |
| Rarest-entry chance | 0.1–2 % per encounter or draw | Expected wait is 1/q; cap with pity or an exchange path |
| Exclusive entries | none / rerun within 12 months | Permanently missable entries make 100 % impossible for late joiners |

  Worked example (the last-item wall): the expected wait for one specific item with per-draw chance q is 1/q draws, and the draws needed for a 90 % chance are ln(10)/q. A 0.5 % sticker needs 200 draws on average and 461 for the unlucky-10 % player; at 4 stickers per pack that is 50 and 116 packs. Equal-odds completion maths (n·Hₙ) is in `collections-albums` (05).
- **Dynamics:** targeted hunting; community spawn-sharing; stalls on the last 1–3 entries; the collection becomes a status display.
- **Aesthetic targets (MDA):** Discovery, Challenge, Submission, Expression (showcase).
- **Feedback and juice:** silhouette fills with a flourish; "NEW" badge until viewed; group progress bars; a museum or shelf that friends can visit.
- **Failure modes and exploits:** last-item wall; event-locked entries as FOMO; catalogue bloat devaluing entries; source hints that are wrong after a patch.
- **Mobile fit:** excellent — one-thumb browsing in 10–60 s; deep-link each entry to "where to find".
- **Monetization hooks and the ethical limit:** lures, bait and trackers that raise q for a while. Never sell random packs whose remaining entries are rarer than the displayed odds suggest; every catalogue entry must be obtainable through free play within a stated window. Japan's 2012 "complete gacha" prohibition applies to set-for-prize designs with paid random items (see `legal-ethics`).
- **Implementation notes:** store status as a compact byte array indexed by entry ordinal; version-stamp the catalogue so appended entries never shift ordinals.

```text
on_acquire(p, e):
  p.count[e.id] += 1; p.status[e.id] = max(p.status[e.id], OWNED)
  if p.count[e.id] >= e.research_target: p.status[e.id] = RESEARCHED
  pct = owned_in(p, e.group) / size(e.group)
  for m in MILESTONES[e.group]: if pct >= m.at and not claimed(p, m): grant(p, m.reward)
```
- **Reference games:** Pokémon series (Pokédex), Animal Crossing: New Horizons (museum), Old School RuneScape (collection log), Monopoly GO (sticker albums).
- **Combines well with:** `creature-collection`, `set-bonuses`, `collections-albums` (05), `duplicate-protection` (07), `lore-collectibles` (10).

## 4. Crafting and inventory

### 09.03 Recipe crafting — `recipe-crafting`

- **Category:** crafting · converter (chain economics: `crafting-chains` (04))
- **Player fantasy:** "I make what I need from what I find."
- **Core rules:**
  - *State:* inventory `{material: qty}`; recipes `{id, inputs {mat: qty}, outputs, station, craft_time, unlock}`; known-recipe set.
  - *Triggers:* player picks a known recipe at a valid station with all inputs present.
  - *Effects:* inputs consumed at start; output delivered after `craft_time` (0 = instant); optional quality roll; salvage reverses part of a craft.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Distinct inputs per recipe | 2–4 on mobile, up to 6 late | Each input is a gathering errand; more than 4 reads as chores |
| Value add (output ÷ input market value) | 1.1–1.5× | Below 1 nobody crafts; above 2 raw gathering becomes pointless |
| Salvage return | 30–70 % of input value | Must stay below 100 % around any craft→salvage cycle |
| Craft time | instant (action) to 1–8 h (meta) | Long crafts turn crafting into an appointment mechanic |
| Recipe unlock pace | 1–3 per session early | A wall of recipes overwhelms the inventory UI |

- **Dynamics:** shopping-list planning; gathering routes; intermediate bottlenecks; "cheapest path to X" problem solving.
- **Aesthetic targets (MDA):** Expression (self-reliance), Challenge (planning), Submission.
- **Feedback and juice:** "craftable" dots on the list; missing inputs highlighted with tap-through to sources; finished item pops and flies to the bag.
- **Failure modes and exploits:** recipe sprawl (40 materials in week one); arbitrage loops (craft→salvage or craft→sell above input cost) that print currency; one dominant recipe; unclear sources pushing players to wikis.
- **Mobile fit:** add "craft max", a craft queue and auto-pull from storage; keep visible material types to about 10–15 early.
- **Monetization hooks and the ethical limit:** material bundles and craft speed-ups. No core-progress recipe may require a purchase-only material; show the real-money value of premium speed-ups.
- **Implementation notes:** recipes form a DAG; propagate market values through it and run a CI check that no cycle is profitable.

```text
craftable_count(r, inv) = min(inv[m] // q for m, q in r.inputs.items())
assert_no_arbitrage(): for cycle C in graph(recipes + salvage + vendor_prices):
  assert product(value_ratio(edge) for edge in C) <= 1.0
```
- **Reference games:** Minecraft, Stardew Valley, Don't Starve, Terraria, Valheim.
- **Combines well with:** `storage-capacity`, `production-chain`, `order-board`, `set-bonuses`, `gear-rarity` (05).

### 09.04 Combinatorial discovery crafting — `discovery-crafting`

- **Category:** crafting · discovery puzzle
- **Player fantasy:** "I'm an alchemist — what happens if I combine these?"
- **Core rules:**
  - *State:* discovered elements; hidden recipe table `{sorted pair → product}`; tried-pairs set.
  - *Triggers:* player combines two (sometimes three) discovered elements.
  - *Effects:* valid → product joins the discovered set with a reveal; invalid → "nothing happens" with inputs kept (casual convention) or consumed (survival convention); a hint reveals one untried valid pair.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Element count | 50–700 | Length of game; pairs grow quadratically |
| Valid share of pairs | 2–10 % | Too low = brute-force grind; too high = no puzzle |
| Logic transparency | semantic (fire + water = steam) vs arbitrary | Semantic rewards reasoning; arbitrary forces wikis |
| Hint cadence | free hint every 3–10 min, or per rewarded ad | The anti-frustration valve |
| Cost of a failed attempt | none / consumes inputs | Consumption suits survival tension; free attempts suit kids and casual |

  Maths: with n discovered elements there are n(n+1)/2 unordered pairs (self-pairs included): 20 → 210, 100 → 5,050. At a 5 % valid share a blind player needs about 20 attempts per discovery — fine at n = 20, numbing at n = 100 unless reasoning prunes the space.
- **Dynamics:** reasoning early, brute force late; community spoilers; completion-count chase.
- **Aesthetic targets (MDA):** Discovery, Expression.
- **Feedback and juice:** discovery card with a flavour line; "first discovery" stamp; tried pairs greyed in the picker; x / total counter.
- **Failure modes and exploits:** brute-force tedium past ~100 elements; obscure logic; no goal beyond the count (add target quests); store screenshots that spoil reveals.
- **Mobile fit:** dragging one element onto another is native touch; ideal for 1–3 minute sessions.
- **Monetization hooks and the ethical limit:** hint packs and rewarded hints. The game must be completable without paid hints; no attempt timers in kids' titles.
- **Implementation notes:** grey out tried pairs automatically; pick hints from the shallowest undiscovered depth so they teach rather than skip.

```text
combine(p, a, b):
  key = tuple(sorted((a, b)))
  if key in p.tried: return show_already_tried()
  p.tried.add(key); prod = RECIPES.get(key)
  if prod and prod not in p.discovered: p.discovered.add(prod); reveal(prod)
hint(p) = min((k for k in RECIPES if set(k) <= p.discovered and k not in p.tried and RECIPES[k] not in p.discovered), key=depth)
```
- **Reference games:** Little Alchemy, Doodle God, Minecraft (recipe discovery before the recipe book).
- **Combines well with:** `collection-log`, `recipe-crafting`, `creature-breeding`, `deduction` (10).

### 09.05 Storage caps and inventory pressure — `storage-capacity`

- **Category:** inventory · constraint and sink driver (economy view: `storage-caps` (04))
- **Player fantasy:** "I run a tight, efficient storehouse."
- **Core rules:**
  - *State:* pools `{id, capacity, contents}`; category routing (e.g., crops → silo, goods → barn).
  - *Triggers:* harvests, production, drops, rewards.
  - *Effects:* add up to free capacity; overflow goes to an inbox (or blocks the producer); expansions raise capacity using expansion materials or currency.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Starting capacity | 1–2 sessions of output | Lower = constant sell decisions; higher = no pressure at all |
| Expansion step | +10–25 % per upgrade, rising material cost | Each upgrade should buy roughly 3–7 days of breathing room |
| Expansion material source | random drops 1 per 3–10 harvests, or quests | Random-only materials create gacha-like stalls |
| Overflow rule | inbox ≥ 7 days / block producer / auto-sell at a discount | Never destroy rewards silently |
| Shared vs per-category | per-category early, shared late | Per-category teaches routing; shared cuts micromanagement |

- **Dynamics:** forces selling and sinks; the "empty storage before logout" ritual; trade value for expansion items; hoard-versus-liquidity decisions.
- **Aesthetic targets (MDA):** Challenge (optimisation), Submission (tidying).
- **Feedback and juice:** capacity bar turns amber at 80 % and red at 95 %; a "storage full" toast with one-tap sell or expand; items flying to a full barn bounce off visibly.
- **Failure modes and exploits:** storage chores dominating the session; rewards lost to overflow; purchase-only expansions reading as a paywall; event rewards blocked by full storage.
- **Mobile fit:** bulk sell, filters, a "keep at most N" setting; one-hand lists.
- **Monetization hooks and the ethical limit:** expansion materials and currency. Purchased and event rewards must always be deliverable (inbox), never lost; expansions must be earnable at a stated pace.
- **Implementation notes:** model capacity as a `gate` node in the economy model and run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/economy_sim.py --model econ.json --json` to see how often each archetype hits the cap.

```text
add(p, pool, item, n):
  take = min(n, cap(p, pool) - used(p, pool)); p.pools[pool][item] += take
  if n > take: inbox_add(p, item, n - take, expires=now + 7*DAY); notify_full(pool)
```
- **Reference games:** Hay Day (barn and silo), Stardew Valley (chests), Resident Evil 4 (attaché case as a spatial puzzle), Diablo II (grid inventory).
- **Combines well with:** `production-chain`, `farming-cycle`, `recipe-crafting`, `order-board`, `merge-board`.

## 5. Building and self-expression

### 09.06 Defensive base layout (async PvP) — `base-defense-layout`

- **Category:** building · asynchronous PvP layout (raid loop and loot economy: `async-base-raid` (06))
- **Player fantasy:** "My fortress is a puzzle others can't crack."
- **Core rules:**
  - *State:* grid layout of walls, defences, traps, storages and HQ; building counts per HQ level; trophies; shield timer.
  - *Triggers:* another player attacks asynchronously; defence AI runs on the stored layout; the attack ends on time-out, wipe-out or full destruction.
  - *Effects:* attacker loots a share of unprotected storage and gains or loses trophies by result (stars for thresholds such as 50 %, HQ destroyed, 100 %); defender gets a shield after a heavy loss; a replay is saved.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Lootable share | 5–20 % of storage, minus a protected portion | Higher = raiding economy; too high = offline-loss rage |
| Shield after a loss | several hours, scaled by destruction | Stops repeated farming of one victim |
| Attack length | 2–3 min (Clash of Clans uses 3) | Fits one session |
| Defences added per HQ level | +1–3 | Drives HQ upgrades; rushing the HQ leaves bases weak |
| Matchmaking window | trophies ± range and HQ ± 1–2 | Wide windows create mismatches and churn |

- **Dynamics:** layout metas (funnelling, compartments, anti-3-star); layout sharing and copying; trophy pushing versus resource farming; revenge attacks.
- **Aesthetic targets (MDA):** Expression (fortress design), Challenge, Fellowship (clans, shared layouts).
- **Feedback and juice:** defence replays (watching an attack fail is the defender's payoff); defence log with a "revenge" button; opt-in "your base held" notifications.
- **Failure modes and exploits:** offline losses feel unfair (protect a storage share, shield); one dominant layout; bots farming inactive bases; HQ-rush mismatches; replays that desync from the real result.
- **Mobile fit:** attacks fit 3-minute sessions one-handed; the layout editor needs grid snap, multi-select move, undo/redo and saved layouts, and is usually a two-hand task.
- **Monetization hooks and the ethical limit:** time skips and resource packs. Match on strength, never on spend — never deliberately pair low spenders with whales to provoke purchases; loot caps protect lapsed players.
- **Implementation notes:** deterministic fixed-step simulation (fixed-point maths, seeded RNG) so a replay is layout + seed + deployment inputs; the server re-simulates to validate results (see `multiplayer-backend`).

```text
battle = Sim(layout_snapshot, seed)
for (t, unit, pos) in deployments: battle.schedule(t, deploy(unit, pos))
while not battle.done(): battle.step(FIXED_DT)
result = battle.score()   # stars, %, loot; server recomputes and compares with the client claim
```
- **Reference games:** Clash of Clans, Boom Beach.
- **Combines well with:** `hq-gated-building`, `storage-capacity`, `async-base-raid` (06), `matchmaking-rating` (06), `spectating-replays` (06).

### 09.07 HQ-gated building upgrades — `hq-gated-building`

- **Category:** building · upgrade graph with a concurrency limit (queue economics: `build-queues` (04))
- **Player fantasy:** "My settlement grows piece by piece into something mighty."
- **Core rules:**
  - *State:* buildings `{type, level}`; HQ level; builder slots (concurrent jobs); unlock table `{hq_level → new types, max level per type, max count per type}`.
  - *Triggers:* player starts an upgrade (cost paid up front) when a builder is free and `level < cap(type, hq)`.
  - *Effects:* building is unavailable or degraded during the job (design choice); on completion level + 1; an HQ upgrade raises every cap and unlocks new types.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Builder slots | 2–5 (one extra from an early quest) | More slots = more parallel planning and faster pace |
| Upgrade time growth | ×1.3–1.6 per level: minutes in hour 1, hours by day 3, days by week 3 | Sets the appointment cadence (timer maths in `build-timers-and-skips` (08)) |
| Cost growth | ×1.4–2.0 per level | Must track the income curve or it walls players |
| Cap rule | non-HQ max level = f(HQ level) | Creates the "max out before HQ" versus "rush" decision |
| New types per HQ level | 1–2 | Fresh toys are the HQ upgrade's main reward |
| Usable while upgrading | yes / degraded / no | "No" on producers or defences punishes upgrading |

- **Dynamics:** upgrade-order planning (economy first or defence first); HQ rushing; appointment play; idle-builder anxiety.
- **Aesthetic targets (MDA):** Submission (steady growth), Expression (the base visibly changes), Challenge (planning).
- **Feedback and juice:** scaffolding and builder animations; countdown over the building; silhouette change every few levels (visual tiers); idle-builder indicator on the HUD.
- **Failure modes and exploits:** idle builders with nothing affordable; timer walls in the first session (kills D1); upgrades that disable producers; visual change too rare to notice; nested caps players cannot explain.
- **Mobile fit:** the classic appointment loop — make sure the core loop gives players something to do while builders work; idle-builder pushes only when opted in.
- **Monetization hooks and the ethical limit:** extra builder slots and speed-ups. Keep the first sessions mostly timer-free; make the extra builder obtainable with premium currency that can be earned in play; show the real-money value of skips.
- **Implementation notes:** server-timestamped jobs `{building_id, start, end}`, completed lazily on load in end-time order; caps in data tables.

```text
can_upgrade(p, b) = free_builders(p) > 0 and b.level < CAP[b.type][p.hq] and can_pay(p, COST[b.type][b.level + 1])
on_load(p, now): for job in sorted(p.jobs, key=end): if job.end <= now: complete(p, job)
```
- **Reference games:** Clash of Clans, Township, Rise of Kingdoms, Whiteout Survival.
- **Combines well with:** `base-defense-layout`, `city-zoning`, `production-chain`, `build-timers-and-skips` (08), `research-trees` (05).

### 09.08 City zoning, adjacency and coverage — `city-zoning`

- **Category:** building · spatial optimisation
- **Player fantasy:** "I'm the mayor, and the city thrives because of how I planned it."
- **Core rules:**
  - *State:* tile grid; buildings with footprints; zones (residential, commercial, industrial); services with coverage radius; derived per-tile values (happiness, pollution, land value).
  - *Triggers:* place, move, demolish; economic tick (or lazy recompute on resume).
  - *Effects:* population = Σ residential capacity × satisfaction; income from taxes or goods; adjacency bonuses and penalties; coverage gaps cap growth or raise complaints.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Service radius | 3–8 tiles | Small radius = dense placement puzzles |
| Adjacency effects | ±5–25 % per neighbour type | Strong effects force grid-optimal "ugly" layouts |
| Footprints | 1×1 to 4×4 | Large footprints create packing puzzles |
| Land expansion cost | rising per plot | Paces map growth; a major soft-currency sink |
| Demand meters | R/C/I demand 0–100 | Tells the player what to build next; prevents paralysis |

- **Dynamics:** layout optimisation and periodic rebuilds; efficiency-versus-beauty tension; emergent problems (traffic, pollution) become goals.
- **Aesthetic targets (MDA):** Expression, Challenge, Submission.
- **Feedback and juice:** coverage heat-map while placing; ghost preview with +/− deltas; citizens and traffic animate; complaint bubbles point at causes.
- **Failure modes and exploits:** optimal layouts are ugly (add beauty bonuses such as parks); moving many buildings is tedious on touch; opaque formulas; frame rate collapses with many animated agents on low-end devices.
- **Mobile fit:** pinch/pan camera, placement ghost with an explicit confirm button (no accidental drops), a store-to-inventory mode for rearranging.
- **Monetization hooks and the ethical limit:** land expansions and premium buildings. Premium buildings should be cosmetic or modest bonuses; expansions must be earnable.
- **Implementation notes:** incremental influence maps per service — on placement update only cells within the radius; tile queries stay O(1).

```text
place(b, x, y): assert fits(b, x, y); grid.mark(b)
  for s in services_of(b): influence[s].add_disc(center(b), RADIUS[s], WEIGHT[s])
tile_value(t) = BASE[t.zone] * (1 + sum(adj_bonus(t))) * min(1, coverage(t) / REQUIRED[t.zone])
```
- **Reference games:** SimCity BuildIt, Pocket City, Cities: Skylines, Township, Islanders.
- **Combines well with:** `hq-gated-building`, `production-chain`, `free-placement-decor`, `order-board`.

### 09.09 Plant–grow–harvest cycles — `farming-cycle`

- **Category:** building · real-time production
- **Player fantasy:** "I nurture things and reap what I sow."
- **Core rules:**
  - *State:* plots `{state: empty|growing|ripe|withered, crop, planted_at}`; seeds and crops in storage.
  - *Triggers:* plant (consumes a seed or soft currency); time passes; harvest tap or swipe.
  - *Effects:* ripe when `now ≥ planted_at + grow_time`; harvest yields y crops (often 2 per seed, so replanting sustains itself); optional wither after a neglect window; optional seasons and quality tiers.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Grow-time ladder | 2 min → 5 min → 30 min → 2 h → 8 h | Short crops reward staying; long crops cover sleep and work |
| Yield per seed | 2:1 | Below 2 forces seed buying (a sink); above 2 floods storage |
| Value per real hour | falls as crops lengthen | Long crops must still win per check-in, or nobody plants them |
| Withering | off / lose bonus only | Withering punishes having a life; prefer "no bonus" over loss |
| Plot count | 6–12 early, +1–2 per level | Plots × crop ladder sets session length |

  Decision rule players actually use: for an absence of A minutes, the best crop is the one maximising `(yield × price − seed_cost)` among crops with `grow_time ≤ A` — "plant the crop that just fits the absence". Design the ladder so each common absence (5 min, 1 h, 8 h) has a clear best answer.
- **Dynamics:** appointment planning ("8-hour crop before bed"); sell-versus-process decisions; plot management.
- **Aesthetic targets (MDA):** Submission (ritual), Sensation (harvest swipe), Fantasy (pastoral).
- **Feedback and juice:** ripe sparkle; one swipe harvests many plots (Hay Day's sickle gesture); crops arc to the barn with a rising-pitch tick per item.
- **Failure modes and exploits:** neglect penalties; crops so short they tether players; one dominant crop; device clock changes used to skip time.
- **Mobile fit:** excellent — one gesture, 1–3 minute sessions.
- **Monetization hooks and the ethical limit:** instant grow, extra plots, fertiliser. Normal absence must never cause loss; cap and opt-in notifications.
- **Implementation notes:** never tick plots per frame; derive state from timestamps using server time.

```text
state(plot, now):
  if plot.crop is None: return EMPTY
  ripe_at = plot.planted_at + GROW[plot.crop]
  if now < ripe_at: return GROWING
  if WITHER_ON and now > ripe_at + WITHER_WINDOW: return WITHERED
  return RIPE
```
- **Reference games:** Hay Day, FarmVille, Stardew Valley, Story of Seasons (Harvest Moon), Animal Crossing.
- **Combines well with:** `storage-capacity`, `production-chain`, `order-board`, `virtual-pet`.

### 09.10 Free-placement decoration and housing — `free-placement-decor`

- **Category:** self-expression · spatial creativity
- **Player fantasy:** "This space is mine, and it shows who I am."
- **Core rules:**
  - *State:* owned decor `{id, footprint, rotations, tags (theme, series, colour)}`; layout `{item, x, y, rot}`; optional rating.
  - *Triggers:* lift, place, rotate, store; visitors (NPCs or players) view the space; rating on demand or weekly.
  - *Effects:* placement validated against occupancy; optional score from themes, series and variety; visitors leave reactions or likes.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Grid granularity | full tile / half tile / free with snap | Finer = more expression, harder on touch |
| Item cap per room | 50–300 | Perf and clutter limit; show a budget meter |
| Score weights | theme, series sets, variety, colour | A score gives non-creative players a goal |
| Audience | NPC visitors / friends / public gallery | Without an audience, decorating loses its point |
| Storage | generous | Decor collectors hoard; storage pain kills expression |

- **Dynamics:** self-expression; screenshot sharing; theme hunting drives collection; social status.
- **Aesthetic targets (MDA):** Expression, Fellowship, Fantasy.
- **Feedback and juice:** smooth lift and snap with a drop shadow; invalid cells tint red; theme-complete sparkle; photo mode.
- **Failure modes and exploits:** no audience or purpose; fiddly placement on small screens; draw-call explosion with hundreds of items on low-end devices; decor locked in paid random boxes.
- **Mobile fit:** long-press to lift, drag with the item offset above the finger, rotate button or two-finger twist, undo; batch static decor into atlases (see `mobile-performance`).
- **Monetization hooks and the ethical limit:** cosmetic sets — the cleanest monetization in this file. Decor never grants competitive power; prefer direct purchase over random boxes, and avoid random decor boxes entirely for minors.
- **Implementation notes:** occupancy bitset plus a compact layout list (a few bytes per item); rating by tag counting.

```text
can_place(item, x, y, rot) = in_bounds(item, x, y, rot) and not any(occ[c] for c in cells(item, x, y, rot))
place(item, x, y, rot): for c in cells(...): occ[c] = 1; layout.append((item.id, x, y, rot))
score(layout) = sum(series_bonus(layout)) + W_THEME * theme_match(layout) + W_VAR * variety(layout)
```
- **Reference games:** Animal Crossing: New Horizons, Animal Crossing: Pocket Camp, The Sims FreePlay, Minecraft, Hay Day (decorations).
- **Combines well with:** `set-bonuses`, `design-challenge`, `renovation-meta` (05), `cosmetic-shop` (12).

### 09.11 Themed design challenges with judging — `design-challenge`

- **Category:** self-expression · scored creativity
- **Player fantasy:** "My taste wins — people vote for my style."
- **Core rules:**
  - *State:* challenge `{theme, required items or tags, entry window, judging mode}`; the player's entry built from owned items.
  - *Triggers:* submit (optional soft-currency or ticket fee); voting phase; results.
  - *Effects:* score from pairwise player votes or tag-matching rules; rewards by percentile band; top entries showcased.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Judging mode | pairwise votes / tag scoring / hybrid | Votes reward real taste but are slow and gameable; tags are instant but formulaic |
| Required items | 0–3 | Requirements push collection and purchases |
| Entry window | 1–3 days | Shorter windows raise urgency |
| Reward bands | top 10 / 25 / 50 % | Percentile bands keep most entrants rewarded |
| Voting incentive | soft currency per N votes, daily cap | Feeds the voting pool; the cap limits bot voting |

- **Dynamics:** style metas and trends; buying items to meet themes; voting becomes its own micro-game.
- **Aesthetic targets (MDA):** Expression, Fellowship, Challenge.
- **Feedback and juice:** star reveal of the score; gallery of top looks; "your look beat 74 % of entries".
- **Failure modes and exploits:** required premium items (pay-to-enter); vote brigading and bots; tag scoring that rewards hoarding rather than taste; harsh results that discourage beginners.
- **Mobile fit:** styling is touch-native; pick-one-of-two voting is a perfect 30-second session.
- **Monetization hooks and the ethical limit:** themed items and entry tickets. Every challenge must be completable with free items; paid entries must be judged exactly like free ones.
- **Implementation notes:** rate entries with Elo or Bradley–Terry from pairwise votes rather than raw likes (corrects for unequal exposure).

```text
on_vote(w, l): ew = 1 / (1 + 10 ** ((r[l] - r[w]) / 400)); r[w] += K * (1 - ew); r[l] -= K * (1 - ew)
next_pair(voter): prefer fewest-votes entries with similar rating; exclude the voter's own and friends' entries
```
- **Reference games:** Design Home, Covet Fashion, Love Nikki: Dress Up Queen (tag-scored styling battles).
- **Combines well with:** `free-placement-decor`, `collection-log`, `cosmetic-shop` (12), `limited-time-events` (08).

## 6. Creatures

### 09.12 Creature capture and collection — `creature-collection`

- **Category:** collection · encounter and capture
- **Player fantasy:** "I find them, catch them, and build a team that's mine."
- **Core rules:**
  - *State:* species `{id, rarity, habitats, time windows, base_catch}`; owned creatures with individual variance (stats, size, cosmetic variant flag).
  - *Triggers:* encounter spawn (location, biome, time, weather, event); capture attempt.
  - *Effects:* success with probability p → owned plus catalogue update; failure → retry or flee chance; duplicates feed upgrades (candy, shards).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Species at launch | 50–150 | Months of hunting; room for drops |
| Encounter weights | common 60–70 %, uncommon 20–30 %, rare 5–10 %, very rare ≤ 1 % | Hunt duration and rare-spawn excitement |
| Base catch rate | 5–90 % | Low on rares so captures are memorable |
| Flee chance per failed attempt | 0–25 % | Stakes per throw; high values feel cruel |
| Individual variance | ±10–20 % stats; cosmetic variant 1 in 500–4,000 | Long-tail chase for a "perfect" or shiny specimen |

- **Dynamics:** rare-spawn hunting; community information sharing; team metas; duplicates as a currency.
- **Aesthetic targets (MDA):** Discovery, Fantasy, Expression, Challenge.
- **Feedback and juice:** rustle or shadow before the reveal; capture tension (shakes) under 3 s; "NEW" catalogue stamp; rarity-coded VFX.
- **Failure modes and exploits:** paid capture tools that dominate; region-exclusive species; power creep that strands old favourites; flee chances that feel random rather than readable.
- **Mobile fit:** flick-to-throw or tap timing, one hand, 10–30 s encounters.
- **Monetization hooks and the ethical limit:** capture tools, lures, incubators. Every core-catalogue species must be catchable for free; event species rerun; paid random eggs need odds disclosure.
- **Implementation notes:** seed spawns by world cell and time slot so co-located players see the same creature (essential for `gps-location` (10)).

```text
spawn(cell, slot) = weighted_pick(TABLE[biome(cell)][slot], rng=hash(WORLD_SEED, cell, slot))
attempt(c, tool): p = clamp(c.base * tool.mult * status(c) * (1.5 - c.hp / c.hp_max) * skill_bonus, 0.01, 0.95)
  return rng() < p
```
- **Reference games:** Pokémon series, Pokémon GO, Palworld.
- **Combines well with:** `creature-breeding`, `branching-evolution`, `collection-log`, `gps-location` (10), `gacha-banners` (07).

### 09.13 Breeding and genetics — `creature-breeding`

- **Category:** collection · generative combination
- **Player fantasy:** "I'm the breeder who discovers the rare hybrid."
- **Core rules:**
  - *State:* parents with species/element tags and heritable genes; nursery slots; breed and hatch timers.
  - *Triggers:* pair two compatible parents → breeding timer → egg → hatching timer.
  - *Effects:* offspring species from a combo table keyed by the parents' tags (with rare outcomes); each gene inherited 50/50 with a mutation chance; stats = parental mean ± variance.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Breed + hatch time | 30 s to 48 h (rarer = longer) | Long rare timers create appointments and skip demand |
| Rare outcome chance | 1–10 % per eligible pair | Chase intensity |
| Mutation rate | 1–5 % per gene | Novelty without chaos |
| Stat inheritance | mean ± 5–15 % | Dedicated breeders climb slowly toward "perfect" |
| Nursery slots | 1–4 | Concurrency, like builder slots |

- **Dynamics:** community breeding charts; long-term line optimisation; markets for bred stock; homogenised metas.
- **Aesthetic targets (MDA):** Discovery, Expression, Challenge (planning).
- **Feedback and juice:** egg pattern and colour hint at the outcome; hatch sequence; "new species" banner; family-tree view.
- **Failure modes and exploits:** opaque odds; paid speed-ups combined with random outcomes (effectively a paid random item); everyone converging on one genotype; timers stacking past patience.
- **Mobile fit:** async; drag two parents into the nursery; strong fit.
- **Monetization hooks and the ethical limit:** speed-ups, rare parents, nursery slots. If any paid input buys a random outcome, publish per-pair outcome odds before purchase (store rules on paid randomized items; see `12-monetization-linked-mechanics.md`).
- **Implementation notes:** combo tables keyed by sorted tag pairs; genes as small enums for compact saves.

```text
child.species = weighted_pick(COMBO[tuple(sorted((a.element, b.element)))])
for g in GENES:
  allele = a.genes[g] if rng() < 0.5 else b.genes[g]
  child.genes[g] = mutate(allele) if rng() < MUTATION else allele
child.stat = (a.stat + b.stat) / 2 * (1 + gauss(0, SIGMA))
```
- **Reference games:** DragonVale, Dragon City, Monster Legends, Pokémon (egg breeding), Viva Piñata.
- **Combines well with:** `creature-collection`, `branching-evolution`, `fusion-tables`, `discovery-crafting`.

### 09.14 Branching evolution — `branching-evolution`

- **Category:** collection · conditional form change (numeric star-up lives in `hero-ascension` (05))
- **Player fantasy:** "My little one grows into something mighty — and how I raised it decides what it becomes."
- **Core rules:**
  - *State:* creature `{species, stage, level, affection, held_item}`; rules `{from, to, conditions[]}`.
  - *Triggers:* level-up, item use, time of day, location, affection threshold, battle count, care quality.
  - *Effects:* one matching rule → evolve (player may cancel); several → player chooses; the new form changes stats, skills and appearance.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Stages | 2–3 | More stages dilute each moment and multiply art cost |
| Stat multiplier per stage | 1.3–1.8× | Big jumps make evolving mandatory |
| Condition types | level, item, time, place, affection, care | Varied conditions create discovery and lore |
| Branches per base form | 1–8 (Eevee has 8) | More branches = identity choice, more art |
| Cancel / revert | cancel allowed; cosmetic revert | Protects attachment to a favourite form |

- **Dynamics:** investment decisions; discovery of hidden conditions; attachment; community lore and guides.
- **Aesthetic targets (MDA):** Fantasy, Discovery, Expression.
- **Feedback and juice:** glow build-up and silhouette morph under 5 s, skippable after first view; known branches shown as silhouettes with condition hints.
- **Failure modes and exploits:** forced evolution to stay viable (offer a cosmetic form choice); hidden conditions with no hint; irreversible wrong branch (offer a reset item earnable in play).
- **Mobile fit:** short sequences; checks run on events and on resume.
- **Monetization hooks and the ethical limit:** evolution items. Show requirements before the player invests; no paid-only branches for core forms.
- **Implementation notes:** rules as data so live-ops can add branches without a client update.

```text
on_event(c, evt):
  m = [r for r in RULES[c.species] if all(cond(c, evt) for cond in r.conditions)]
  if len(m) == 1: prompt_evolve(c, m[0].to)
  elif m: prompt_choose(c, [r.to for r in m])
```
- **Reference games:** Pokémon series, Digimon World, Tamagotchi.
- **Combines well with:** `creature-collection`, `creature-breeding`, `virtual-pet`, `hero-ascension` (05).

### 09.15 Fusion tables — `fusion-tables`

- **Category:** collection · deterministic combine-and-sacrifice (rarity fusion of gear is `gear-rarity` (05))
- **Player fantasy:** "I forge something greater by giving things up — and I can plan it."
- **Core rules:**
  - *State:* units with family (race, arcana) and level; chart `{(familyA, familyB) → familyC}`; special recipes; skill-inheritance rules.
  - *Triggers:* player selects two (or more) units in the fusion screen.
  - *Effects:* preview shows the exact result and inheritable skills; confirm consumes inputs and creates the result; special recipes override the chart.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Determinism | full preview / partial / random | Full preview = planning puzzle; random = gambling |
| Result level | mean(parent levels) + k | Higher k makes fusion the main progression engine |
| Inherited skills | 1–4 chosen | Build-crafting depth |
| Fodder rank-up variant | N same-rank units → rank + 1 | Gives duplicates value |
| Compendium buy-back | re-buy registered units for currency | Removes fear of consuming favourites |

- **Dynamics:** route planning through the chart; community fusion calculators; duplicates gain value.
- **Aesthetic targets (MDA):** Challenge (planning), Discovery, Expression (custom builds).
- **Feedback and juice:** preview before every confirm; absorb animation; "registered in compendium" stamp.
- **Failure modes and exploits:** consuming a rare by mistake (favourite lock plus rarity confirm); random skill transfer bought with paid inputs; charts too opaque to plan.
- **Mobile fit:** filtered pickers; "auto-select fodder" (lowest value, unlocked only).
- **Monetization hooks and the ethical limit:** compendium currency and fodder packs. Always preview; confirm rare consumption; disclose odds on any random component.
- **Implementation notes:** `preview()` is a pure function shared by UI and server.

```text
preview(a, b):
  fam = SPECIAL.get(pair(a.id, b.id)) or CHART[pair(a.family, b.family)]
  return member_at_or_above(fam, (a.level + b.level) // 2 + K), inheritable(a, b)
fuse(a, b): r = preview(a, b); require confirm(r) and not (a.locked or b.locked); consume(a, b); grant(r)
```
- **Reference games:** Shin Megami Tensei series, Persona series, Raid: Shadow Legends (rank-up fodder), Summoners War.
- **Combines well with:** `creature-breeding`, `branching-evolution`, `merge-board`, `gear-rarity` (05).

### 09.16 Pet care and visitor collection — `virtual-pet`

- **Category:** collection · nurturing over real time
- **Player fantasy:** "Someone depends on me, and they're happy when I come back."
- **Core rules:**
  - *State:* needs meters (hunger, fun, cleanliness) with decay; derived mood; visitor variant: placed items and food, visitor table.
  - *Triggers:* real time passing; care actions; app resume (visitors simulated over the absence).
  - *Effects:* care restores meters; mood drives outputs (gifts, coins, tricks); visitors arrive by item preference and leave gifts or photos; rare visitors need specific items.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Decay full → empty | 8–24 h | Shorter tethers players; longer loses urgency |
| Neglect consequence | sad animation / fewer gifts (avoid sickness or death) | Harsh consequences hurt wellbeing and retention |
| Offline simulation cap | 12–48 h | Limits return dumps and protects the economy |
| Visitor weight per item | 1–20 | Item choice becomes a lure strategy |
| Care actions per session | 3–6 | 30–90 s sessions |

- **Dynamics:** daily ritual check-ins; attachment; photo-album collection; lure experiments.
- **Aesthetic targets (MDA):** Fantasy, Submission, Expression.
- **Feedback and juice:** expressive idles; reactions to touch (petting with a light haptic); visitor photo album.
- **Failure modes and exploits:** guilt design (death, crying notifications); meter chores; notification spam; device clock manipulation.
- **Mobile fit:** superb — one hand, 30-second sessions.
- **Monetization hooks and the ethical limit:** cosmetics and food variety. No permanent loss from neglect; no guilt-trip notifications ("your pet is crying"), especially for under-13 audiences; push opt-in and capped.
- **Implementation notes:** lazy meters `value = max(0, v0 − rate × (now − t0))`; visitors simulated on resume in coarse buckets with a seeded RNG.

```text
on_resume(p, now):
  steps = min((now - p.last) // BUCKET, CAP_STEPS)
  for i in range(steps):
    for slot in p.yard: if slot.food and rng(p.seed, i, slot.id) < visit_p(slot): add_visit(p, pick_visitor(slot.item))
```
- **Reference games:** Tamagotchi, Neko Atsume, Nintendogs, My Talking Tom.
- **Combines well with:** `branching-evolution`, `free-placement-decor`, `collection-log`, `farming-cycle`.

## 7. Merge, orders and production

### 09.17 Merge-2 board with generators — `merge-board`

- **Category:** merge · board-management core loop (puzzle-side overview: `merge` (03))
- **Player fantasy:** "I turn clutter into treasure — small things become wonderful things."
- **Core rules:**
  - *State:* grid of W×H cells; items `{chain, tier}` with tier 1…T per chain; generators (items themselves) with charges; energy; order list.
  - *Triggers:* drag an item onto an identical item (same chain and tier); tap a generator; fulfil an order.
  - *Effects:* merge → one item of tier + 1 at the target cell; generator tap spends 1 energy and spawns a tier-1 item (tier 2 with chance p) into the nearest empty cell; no empty cell → spawn refused; orders consume items for coins, XP and story progress.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Board size | 40–80 cells | Small boards make clutter the main puzzle; big boards remove tension |
| Chain length | 6–14 tiers | Long chains = long-term goals and big "max tier" moments |
| Generator tier-2 chance p | 5–20 % | Saves energy and adds surprise |
| Energy cap / regen | 50–150; 1 per 1–3 min | Sets session length (see `energy-stamina` (08)) |
| Generator charges / cooldown | 10–30 taps, then minutes to hours | Forces switching between generators |
| Order tier demand | mostly tiers 3–6, occasional 7+ | Order difficulty sets how much planning a session needs |

  Maths: a tier-t item needs 2^(t−1) tier-1 items, so expected energy ≈ 2^(t−1) / (1 + p). Tier 7 with p = 0.1 costs about 58 energy — roughly one full energy bar; tier 10 costs about 465. Building one chain upward behaves like a binary counter: holding at most one item per tier needs about t − 1 cells, so k active chains need roughly k(t − 1) cells plus generators. If that exceeds the free board, players hit clutter walls.
- **Dynamics:** board triage (what to keep, sell or store); hoarding high tiers for future orders; generator rotation; "one more merge" flow.
- **Aesthetic targets (MDA):** Submission (tidying), Discovery (next-tier reveal), Narrative (story via orders).
- **Feedback and juice:** merge pop with scale punch and a light haptic tick; chain viewer showing the next silhouette; crown or sparkle on max tier; generator shake when out of charges.
- **Failure modes and exploits:** clutter softlock (no merges, no empty cells); energy walls ending sessions in under 2 minutes; unknown chains; orders needing a rare chain the player cannot produce; "bubble" duplicates priced in premium currency with sub-minute countdowns.
- **Mobile fit:** one of the best one-thumb loops on mobile; sessions bounded by energy at 3–8 minutes.
- **Monetization hooks and the ethical limit:** energy refills, storage slots, extra generators, bubble duplicates. Show what energy costs in real terms; always offer a free way out of a clutter softlock (sell, store, delete); no countdown shorter than a minute on paid offers.
- **Implementation notes:** run a softlock check after every action and test boards with bots (generic `--mode=bot` runner, see `qa-testing`).

```text
on_drop(src, dst):
  if dst.empty: move(src, dst)
  elif same(src, dst) and src.tier < MAX_TIER[src.chain]: dst.tier += 1; clear(src); emit("merge", dst)
  else: swap(src, dst)
tap_generator(g):
  if energy < 1 or g.charges == 0: return deny()
  cell = nearest_empty(g.pos) or return deny("board_full")
  spawn(cell, g.chain, tier=2 if rng() < P_T2 else 1); energy -= 1; g.charges -= 1
softlocked() = no_empty_cells() and not any_mergeable_pair() and not any_sellable_or_storable()
```
- **Reference games:** Merge Mansion, Travel Town, Gossip Harbor, Love & Pies.
- **Combines well with:** `order-board`, `storage-capacity`, `renovation-meta` (05), `energy-stamina` (08).

### 09.18 Merge-3 open world — `merge-world`

- **Category:** merge · sandbox with group merges (see also `merge` (03))
- **Player fantasy:** "I heal a cursed land by combining magical things."
- **Core rules:**
  - *State:* open map with locked or cursed tiles; items `{chain, tier}`; helper creatures that harvest autonomously; camp and level separation.
  - *Triggers:* drop an item so it touches a connected group of identical items.
  - *Effects:* group of 3 → 1 item of tier + 1; group of 5 → 2 (efficiency bonus); leftovers stay; special items heal land; helpers harvest and collect.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Merge rule | 3 → 1, with 5 → 2 bonus | The 5-merge bonus rewards patience |
| Chain length | 6–12 tiers | Long-term goals |
| Helper speed | slow early, upgradeable | Automation as progression |
| Land-healing cost | rising per tile | Paces map expansion |
| Object budget per map | a few hundred | Low-end performance ceiling |

  Maths: with plain 3-merges a tier-t item costs 3^(t−1) base items; always merging in fives gives about 2.5^(t−1). At tier 6 that is 243 versus about 98 — a 2.5× saving that teaches players to wait and gather.
- **Dynamics:** patience-versus-immediacy trade-off; spatial clutter management; automation through helpers.
- **Aesthetic targets (MDA):** Submission, Discovery, Fantasy.
- **Feedback and juice:** the would-merge group highlights while dragging, with a "3 / 5" counter; burst VFX scales with group size.
- **Failure modes and exploits:** clutter and frame-rate collapse on low-end devices; confusing contact rules; late-game tedium of moving hundreds of items.
- **Mobile fit:** drag plus pinch/pan camera; works one-handed with an auto-collect option.
- **Monetization hooks and the ethical limit:** premium currency for chests and creature eggs. Paid random chests require odds disclosure.
- **Implementation notes:** flood-fill the connected group on drop; merge greedily — 6 items give 2 outputs and keep 1 leftover (5 → 2), better than 3 + 3 → 2 with none.

```text
on_drop(item): group = flood_fill(item.cell, same_as=item)        # 4-neighbour adjacency
  n = len(group); out = 2 * (n // 5); r = n % 5
  if r >= 3: out += 1; r -= 3
  if out: remove(n - r items from group, keeping the r farthest); spawn(out, item.chain, item.tier + 1, near=item.cell)
```
- **Reference games:** Merge Dragons!, Merge Magic!.
- **Combines well with:** `merge-board`, `creature-collection`, `storage-capacity`.

### 09.19 Order and delivery boards — `order-board`

- **Category:** goals · directed demand
- **Player fantasy:** "Customers need me — I fill orders and grow my business."
- **Core rules:**
  - *State:* K order slots; order `{items {id: qty}, reward, type: standard|long_haul, expiry?}`; discard cooldown per slot.
  - *Triggers:* inventory change (re-evaluate fillability); fulfil; discard; timer refills an empty slot.
  - *Effects:* fulfil consumes items and pays rewards; the slot refills after a delay with a generated order; long-haul orders (crate sets, longer deadlines, friend help) pay more.
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Slots K | 3–9 | More slots = more choice, less pressure per order |
| Order size | 1–4 item types, 1–6 each | Planning complexity |
| Reward vs market value | 1.2–2.0× | Must beat selling raw goods or orders get ignored |
| Discard cooldown | 5–30 min | Too short → reroll exploit; too long → stuck with bad orders |
| Generator look-ahead | 0–2 production steps beyond stock | Instant gratification versus planning |
| Rare-item orders | ≤ 1 in 5–10 | More often creates stalls |

- **Dynamics:** players plan production around orders; every session has a short-term goal; friends help with long-haul orders.
- **Aesthetic targets (MDA):** Challenge (planning), Submission, Fellowship (help requests).
- **Feedback and juice:** per-item checkmarks; truck or boat departure animation; coin shower; an always-visible order strip at the top of the board.
- **Failure modes and exploits:** orders for locked items; rare-item orders that stall progress; discard-reroll farming of rich orders (cooldown plus reward normalisation); order rewards below sale value.
- **Mobile fit:** excellent — the order strip keeps the goal visible in portrait.
- **Monetization hooks and the ethical limit:** buy missing items with premium currency. Show the price; never generate orders designed to be impossible without paying.
- **Implementation notes:** guarantee at least one order is fillable now and one requires planning.

```text
gen_order(p):
  pool = [i for i in ITEMS if unlocked(p, i)]
  w = {i: (1 / prod_minutes(i)) ** ALPHA * (1.5 if p.stock[i] > 0 else 1.0) for i in pool}
  items = weighted_sample(pool, w, k=randint(1, MAX_TYPES))
  qty = {i: clamp(round(TARGET_MIN / prod_minutes(i)), 1, cap_for(p, i)) for i in items}
  reward = round(sum(VALUE[i] * qty[i] for i in items) * MULT * (1 + 0.1 * len(items)))
  return Order(qty, reward)
refill(p): o = gen_order(p); if not any(fillable(x) for x in p.orders): o = make_fillable(o, p.stock)
```
- **Reference games:** Hay Day (truck and boat orders), Township, Travel Town, Merge Mansion, Stardew Valley (Community Center bundles).
- **Combines well with:** `production-chain`, `merge-board`, `farming-cycle`, `storage-capacity`.

### 09.20 Production chains — `production-chain`

- **Category:** building · converter network (bottleneck economics: `production-bottlenecks` (04))
- **Player fantasy:** "I run an elegant machine where everything flows."
- **Core rules:**
  - *State:* sources (fields, mines), converters (buildings) with recipes and queue slots, storage pools.
  - *Triggers:* player queues a recipe at a converter with inputs available; timers complete.
  - *Effects:* inputs leave storage at queue time; output arrives after T; chains run sources → intermediates → finished goods (Machinations-style sources, converters and pools; see `game-ontology`).
- **Tuning knobs:**

| Knob | Typical range | Effect on feel / difficulty |
|---|---|---|
| Chain depth | 2–4 on mobile (deeper on PC) | Each step adds planning and storage pressure |
| Queue slots per building | 2–9 | Longer queues = longer absences between sessions |
| Step time ladder | minutes early, hours late | Sets the check-in cadence |
| Value added per step | 1.2–1.6× | Below 1.2 nobody processes; above 2 nobody sells raw |
| Parallel copies of a building | 1–3 | Lets players fix bottlenecks |

  Throughput: for step i with m_i machines, output o_i per cycle of T_i minutes, and r_i units needed per final good, the maximum final rate is min_i (m_i × o_i / T_i) / r_i. Worked example: a field makes 2 wheat per 4 min (0.5/min); a mill turns 3 wheat into 1 flour in 5 min (needs 0.6 wheat/min); a bakery turns 2 flour into 1 bread in 10 min (needs 0.2 flour/min, which one mill supplies). One mill needs 1.2 fields; the chain yields 6 bread per hour; the field is the bottleneck until a second one is built.
- **Dynamics:** bottleneck hunting; queue planning before logging off; prioritising orders against stock.
- **Aesthetic targets (MDA):** Challenge (optimisation), Submission (flow), Expression (layout).
- **Feedback and juice:** conveyor or carrier visuals; queue icons; "starved" warning on idle buildings; a production stats panel.
- **Failure modes and exploits:** chains too deep to hold in working memory on a phone; idle buildings nobody notices; intermediate goods swamping storage; timers dominating play.
- **Mobile fit:** queue by drag; "collect all"; event-driven offline completion.
- **Monetization hooks and the ethical limit:** queue slots and speed-ups. Never place purchase-only items in chains that core orders require.
- **Implementation notes:** simulate offline time event by event (no per-frame ticking); model the chain in the economy schema and run `economy_sim.py` per archetype.

```text
resolve_offline(p, now):
  heap = [(job.end, job) for b in p.buildings for job in b.queue[:1]]
  while heap and heap[0][0] <= now:
    t, job = heappop(heap); deliver(p, job.output)          # may unblock storage or other buildings
    nxt = job.building.start_next(t, p.storage)            # inputs reserved at queue time
    if nxt: heappush(heap, (nxt.end, nxt))
```
- **Reference games:** Hay Day, Township, SimCity BuildIt, Factorio, Satisfactory, the Anno series.
- **Combines well with:** `order-board`, `storage-capacity`, `farming-cycle`, `city-zoning`.

## 8. Cross-cutting maths, audit checklist and related skills

| Question | Formula / rule | Use |
|---|---|---|
| Wait for one specific item | mean 1/q draws; 90th percentile ln(10)/q | Last-item walls (`collection-log`) |
| Merge-2 energy cost | 2^(t−1) / (1 + p) | Price orders and energy (`merge-board`) |
| Merge-2 board pressure | ≈ k(t − 1) cells for k active chains | Board sizing |
| Merge-3 cost with 5-merges | ≈ 2.5^(t−1) vs 3^(t−1) | Patience reward (`merge-world`) |
| Chain throughput | min_i (m_i·o_i/T_i) / r_i | Bottlenecks (`production-chain`) |
| Arbitrage check | product of value ratios around any cycle ≤ 1 | Crafting, salvage, vendors |

- [ ] Every collection has a visible total and a deterministic completion path.
- [ ] No craft→salvage→sell cycle prints currency (automated check in CI).
- [ ] Overflow never destroys rewards; storage expansions are earnable.
- [ ] Every paid random output (eggs, chests, breeding) has odds disclosed before purchase.
- [ ] Merge boards have a softlock check and a free escape; order generators never create unfillable orders.
- [ ] Offline progress is computed from server timestamps, event by event, with a cap.
- [ ] Telemetry: `item_crafted`, `merge`, `order_fulfilled`, `storage_full`, `collection_progress`, `building_upgraded` exist in the taxonomy (`player-analytics`).

**Related skills:** `economy-design` (sources, sinks, converters, simulation), `progression-difficulty` (timer and cost curves), `monetization` (offers and ethics), `liveops` (album seasons, events), `legal-ethics` (paid random items, minors), `mobile-performance` (object counts, atlasing), `game-ontology` (Machinations vocabulary).
