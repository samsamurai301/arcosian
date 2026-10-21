# Behavioral Economics in Games

The biases and heuristics that shape player decisions — and the line between using them to make a game clearer and more satisfying versus using them to extract time and money players later regret. Every entry follows the same structure: mechanism, the classic evidence (with its caveats), legitimate game uses, the abuse pattern, an explicit ethical boundary graded green / amber / red, and how to measure it. Covers reinforcement schedules (with drop maths), loss aversion, endowment, sunk cost, goal gradient, Zeigarnik/Ovsiankina, IKEA effect, anchoring, decoy pricing, scarcity, social proof, reciprocity, commitment and consistency, peak-end, near-miss, hyperbolic discounting, defaults, framing, mental accounting and currency abstraction, plus choice overload and the fresh-start effect. It ends with a dissection of a stacked F2P offer, an audit checklist, and abuse-detection metrics. The studio's red lines themselves live in `ethics-and-dark-patterns.md` §6; this file explains the psychology behind them.

## Contents

1. How to read this file: the three tests and the grading
2. Reinforcement schedules
3. Loss aversion
4. Endowment effect
5. Sunk cost
6. Goal gradient
7. Zeigarnik and Ovsiankina effects (open loops)
8. IKEA effect (effort justification)
9. Anchoring
10. Decoy pricing (asymmetric dominance)
11. Scarcity and urgency
12. Social proof
13. Reciprocity
14. Commitment and consistency
15. Peak-end rule and duration neglect
16. Near-miss
17. Hyperbolic discounting (present bias)
18. Defaults
19. Framing
20. Mental accounting and currency abstraction
21. Two more: choice overload and the fresh-start effect
22. Anatomy of a stacked offer — and its ethical rewrite
23. Behavioural-economics audit checklist
24. Metrics that detect abuse
25. Sources

---

## 1. How to read this file: the three tests and the grading

Every bias here is a property of human cognition; using it is unavoidable (every price has a frame, every screen a default). The question is never "do we use psychology?" but "in whose interest?". Apply three tests to any design that leans on a bias:

| Test | Question | Fails when |
|---|---|---|
| **Sunlight** | Would it still work — and would we be comfortable — if the player fully understood what we are doing and why? | The technique depends on the player *not* noticing it |
| **Alignment** | Does it help the player get what *they* want from the game (fun, mastery, expression, connection), or only what we want? | The benefit flows only to the studio |
| **Vulnerability** | Does it target moments of weakness (frustration, loss, fatigue, late night), minors, or players showing problematic patterns? | It fires harder when the player is least able to decide well |

**Grading used in every entry**
- **Green** — passes all three tests. Use freely.
- **Amber** — legitimate with explicit safeguards (listed). Requires review by `arcosian:monetization-designer` and sign-off in `contract.monetization.ethics`.
- **Red** — studio red line. Do not build. Listed in `ethics-and-dark-patterns.md` §6.

**Evidence caveat.** Many classic behavioural-economics findings have been re-examined during psychology's replication debates. Where a finding is contested, this file says so. Contested does not mean "safe to exploit"; it means "do not assume a big effect without testing".

---

## 2. Reinforcement schedules

**Mechanism.** From operant conditioning research (B. F. Skinner and colleagues; Ferster & Skinner, *Schedules of Reinforcement*, 1957): how often and how predictably a behaviour is rewarded shapes how often and how persistently it is performed.

| Schedule | Rule | Typical behaviour pattern | Game example |
|---|---|---|---|
| Fixed ratio (FR) | Reward every *n* actions | Bursts of activity, pause after reward | XP bar fills every 10 wins; collect 5 stars for a chest |
| Variable ratio (VR) | Reward after an unpredictable number of actions (mean *n*) | High, steady rate; highly resistant to extinction | Random loot drops; card packs; slot-like spins |
| Fixed interval (FI) | First action after time *t* is rewarded | Activity clusters near the interval end | Daily chest; energy refill; crop timers |
| Variable interval (VI) | First action after an unpredictable time | Moderate, steady checking | Random world events; surprise boss spawns |

**Drop maths every designer must know.** For a drop chance *p* per attempt (independent):
- Expected attempts to first drop: `1 / p`.
- Probability of at least one drop in *n* attempts: `1 − (1 − p)^n`.
- Attempts needed for X% of players to have it: `n = ln(1 − X) / ln(1 − p)`.

| p | Mean attempts | 50% of players by | 90% by | 99% by |
|---|---|---|---|---|
| 0.10 | 10 | 7 | 22 | 44 |
| 0.05 | 20 | 14 | 45 | 90 |
| 0.02 | 50 | 35 | 114 | 228 |
| 0.01 | 100 | 69 | 230 | 459 |
| 0.006 | ~167 | 116 | 383 | 766 |

The tail is the ethical problem: with *p* = 1%, one player in a hundred needs 459+ attempts. **Pity** (a guaranteed drop by attempt *N*) caps the tail; a hard pity of 90 on *p* = 0.6% caps worst-case cost at 90 attempts. Model with `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gacha_calc.py --rate 0.006 --hard-pity 90 --pulls 200`.

**Legitimate uses.** Variable rewards are part of play: what card you draw, what the merge produces, which enemy spawns. Variety from *input randomness* (before the player's decision) keeps play fresh and rewards adaptation. Free variable bonus rewards (surprise chests for exploration) are a classic Easy Fun beat.

**Abuse pattern.** VR schedules attached to *payment* (paid loot boxes, gacha), with no pity, hidden odds and near-miss presentation, form the structural core of gambling-like design. Research has repeatedly found an association between loot-box spending and problem-gambling severity (for example Zendle & Cairns 2018, *PLOS ONE*; later studies broadly replicate the association, though causality is unresolved).

**Ethical boundary.**
- **Green:** free variable rewards from play; input randomness; random cosmetics earned through play with odds shown.
- **Amber (adults only):** paid random items with all of: odds displayed before purchase in percentages, hard pity, published per-item rates, real-money equivalent shown, spend caps and history, no near-miss animation, disabled for minors and in jurisdictions that restrict them (see `ethics-and-dark-patterns.md` §7). The studio's default recommendation is direct purchase instead.
- **Red:** paid randomness for players under 18; hidden or misleading odds; odds that change per player without disclosure; engineered near-misses on paid draws; random items that are the *only* route to competitive power.

**Measure.** Distribution of attempts-to-drop (not just mean); share of spenders hitting pity; spend concentration (share of revenue from top 1% of payers); refund requests on random items.

---

## 3. Loss aversion

**Mechanism.** Prospect theory (Kahneman & Tversky 1979; cumulative version Tversky & Kahneman 1992): people evaluate outcomes as gains or losses relative to a reference point, and losses weigh more than equal gains. Tversky and Kahneman's 1992 estimate of the loss-aversion coefficient was about 2.25. *Caveat:* later work (for example Gal & Rucker 2018) argues loss aversion is smaller and more context-dependent than commonly claimed, especially for small stakes. Assume "losses usually feel worse than gains" and test the size.

**Legitimate uses.**
- Make risk–reward decisions meaningful: "cash out now or push one more wave" works because losing banked progress stings.
- Stakes create tension and make wins feel earned (roguelite runs, ranked play).
- Framing failure as *progress kept* reduces frustration ("You keep 60% of your gold").

**Abuse pattern.** Manufacturing losses to sell protection: streaks that reset to zero with a paid "streak saver" offered at the moment of loss; "lose your rewards unless you continue for 900 gems"; time-limited items that vanish from inventory unless you buy an extension.

**Ethical boundary.**
- **Green:** player-chosen stakes in gameplay; clear rules about what is lost before the player commits.
- **Amber:** streak systems — require grace days or freezes earned through play, decay instead of reset, and no paid recovery offered at the moment of loss.
- **Red:** paid offers triggered by a loss event that frame payment as avoiding the loss (continue offers that escalate, "save your streak" purchase prompts, threats to delete progress).

**Measure.** Purchase rate in the 60 seconds after a loss event vs baseline (should not spike); churn after streak breaks; sentiment on "lost my streak".

---

## 4. Endowment effect

**Mechanism.** People value things more once they own them (Kahneman, Knetsch & Thaler 1990: mug owners demanded roughly twice what non-owners would pay). Ownership can be psychological — a trial item, a named character, a customised base.

**Legitimate uses.**
- Honest trials: "Play the Frost Golem in the next three runs" before deciding to unlock it. Players learn whether they actually want it.
- Ownership of creations (bases, decks, avatars) deepens attachment and expression.
- Starting players with a named companion they keep permanently.

**Abuse pattern.** Granting an item without clearly saying it is temporary, letting attachment build, then removing it with a purchase prompt ("Your Golden Golem is leaving! Keep it for $9.99"). Premium pass previews where earned premium rewards are shown as "yours" but locked.

**Ethical boundary.**
- **Green:** permanent grants; trials labelled as trials at the moment of grant, with duration shown.
- **Amber:** trial-to-purchase flows — trial status visible throughout, a neutral end-of-trial screen, no countdown pressure, purchase prompt dismissible in one tap and not repeated in the same session.
- **Red:** unlabelled "gifts" that expire into a sale; showing locked premium rewards as "already earned, pay to claim" when the player did not choose to pursue them (amber if the player opted into the pass track and the copy is factual).

**Measure.** Trial-to-purchase conversion alongside post-purchase retention of that item (do buyers keep using it?) and refund rate.

---

## 5. Sunk cost

**Mechanism.** People continue investing because of what they have already invested, rather than future value (Arkes & Blumer 1985: theatre-ticket buyers who paid full price attended more performances than those given discounts).

**Legitimate uses.**
- Players value long-term investment (a decorated keep, a levelled roster) and return to it — that is investment working *for* the player when the activity remains enjoyable.
- Roguelite runs: committing to a build creates engagement in the run's outcome.

**Abuse pattern.** Escalating continue prices within one attempt (100 → 200 → 400 gems), copy that cites prior investment ("Don't waste your 45 moves!"), multi-stage paid events where the final reward requires buying after many free stages.

**Ethical boundary.**
- **Green:** long-term investment the player enjoys and can take a break from without losing it.
- **Amber:** continue offers — fixed price shown *before* the run or at least before the decision, a per-run cap (e.g. one paid continue), no copy referencing prior investment.
- **Red:** escalating continue or revive prices within a run or level; events whose last stage is paywalled after free stages; deleting or decaying owned progress to force re-purchase.

**Measure.** Distribution of continues per run; spend per failed level; complaints mentioning "so close" or "wasted".

---

## 6. Goal gradient

**Mechanism.** Effort increases as a goal gets closer (Hull 1932, rats running faster near food; Kivetz, Urminsky & Zheng 2006: coffee-card customers given a 12-stamp card with 2 stamps pre-filled completed faster than those with a blank 10-stamp card — same remaining effort, more apparent progress).

**Legitimate uses.**
- Progress bars and "2 more to the next chest" make goals concrete and motivate the last stretch.
- Short early milestones (first reward after 1–2 levels) build momentum.
- Pre-filling a little progress at the start of a new track (honestly representing a head start the player earned or was given).

**Abuse pattern.** Fake progress (bar jumps to 90% then crawls); the final piece of a collection or event obtainable only by payment or very-low-probability drops ("99% complete").

**Ethical boundary.**
- **Green:** accurate progress bars, near-goal reminders on the results screen.
- **Amber:** head-start pre-fills — must be real progress toward a real reward and not reset if unused.
- **Red:** last-step paywalls; final collection items available only through paid randomness; bars whose rate secretly slows near completion to push purchases.

**Measure.** Completion distribution of tracks and collections (a large spike at "one short" is a red flag); time-to-complete by payer tier.

---

## 7. Zeigarnik and Ovsiankina effects (open loops)

**Mechanism.** Bluma Zeigarnik (1927) reported that interrupted tasks were remembered better than completed ones; Maria Ovsiankina (1928) reported people tend to *resume* interrupted tasks. *Caveat:* replications of the memory effect are mixed; the resumption tendency is better supported. Designers use "open loops" — unfinished goals that pull players back.

**Legitimate uses.**
- Session-end hooks: end on a visible next goal ("Next: restore the fountain — 2 stars").
- Cliffhangers between story chapters.
- Half-built structures that show what comes next.

**Abuse pattern.** Dozens of simultaneous open loops (quests, timers, events, badges) so that no session ever reaches closure; red dot badges on every tab; notifications nagging about unfinished tasks.

**Ethical boundary.**
- **Green:** one or two meaningful open goals visible at session end.
- **Amber:** notification reminders of open loops — opt-in, at most one per day by default, and only when the player can act.
- **Red:** badge spam designed to create anxiety; systems that never allow a "done for today" state.

**Design rule.** Every session should offer a **natural stopping point** with a sense of closure *and* one optional open goal. Closure supports wellbeing; one open goal supports return.

**Measure.** Count of simultaneous red badges on home screen (studio cap: 3); share of sessions ending at a natural stop vs force-close mid-level.

---

## 8. IKEA effect (effort justification)

**Mechanism.** People value things more when they helped make them (Norton, Mochon & Ariely 2012: participants valued self-assembled furniture and origami more than identical pre-made items, provided they completed them).

**Legitimate uses.**
- Building and customisation systems (bases, decks, gardens, avatars) make the result feel personal and worth returning to.
- Letting players name, arrange and share creations.
- Crafting chains where the player chooses inputs.

**Abuse pattern.** Holding creations hostage: bases that decay or get raided unless the player buys shields; creations deleted after inactivity; paid "restore" of something the player built.

**Ethical boundary.**
- **Green:** creations persist indefinitely and are always accessible; shareable.
- **Amber:** PvP raiding of built structures — opt-in or with protection earned by play (shield after being raided, offline protection), and loss limited to a capped share of resources, never the structure itself.
- **Red:** decay or deletion of player creations to sell restoration; paywalls on accessing one's own creations after lapsing.

**Measure.** Return rate of lapsed builders; complaints about lost bases.

---

## 9. Anchoring

**Mechanism.** An initial number biases later estimates (Tversky & Kahneman 1974: estimates of a quantity were pulled toward an arbitrary number from a rigged wheel). In pricing, the first or reference price shapes perceived value.

**Legitimate uses.**
- Showing the honest per-unit value of bundles versus the standard pack ("+40% more gems than the 4.99 pack") when the comparison is real and calculated transparently.
- Ordering a store from small to large so players understand the range.

**Abuse pattern.** Fictitious "was" prices that were never charged; "800% VALUE!" badges computed against an inflated baseline nobody buys; a very expensive top pack shown first purely to make others look cheap.

**Ethical boundary.**
- **Green:** reference prices that are real, current products; value percentages computed against the standard per-unit rate, with the formula consistent across the store.
- **Amber:** limited-time discounts — the reference price must have been the real price for a meaningful period before the discount. In the EU, the Price Indication Directive as amended by the Omnibus Directive (2019/2161) requires announced price reductions to reference the lowest price in the prior 30 days; how it applies to in-game virtual items varies — confirm with `legal-ethics`.
- **Red:** fake reference prices; value claims that cannot be reproduced from the store's own numbers.

**Formula the store must satisfy.** `value_pct = (units_in_offer / price) / (units_in_base_pack / base_price) − 1`, where the base pack is a standard, always-available product. Publish the base pack id in the economy model.

---

## 10. Decoy pricing (asymmetric dominance)

**Mechanism.** Adding an option that is clearly worse than one existing option (but not another) shifts choice toward the option that dominates it (Huber, Payne & Puto 1982). Dan Ariely's *Predictably Irrational* (2008) popularised a magazine-subscription example in which a print-only option at the same price as print-plus-web shifted choices to the bundle.

**Game example.** Gem packs at 4.99 (500), 9.99 (1,050), 19.99 (2,000): the 19.99 pack is a decoy that makes 9.99 look smart, because per-unit it is *worse* than 9.99. More commonly the decoy is a mid pack that pushes players to the largest.

**Legitimate uses.** Assortment design where every option is a genuine, fairly priced product and per-unit value improves (or stays flat) with size. Offering a clear "best for most players" option with honest reasoning.

**Abuse pattern.** Options that exist only to be unattractive; per-unit value that gets *worse* at some sizes without disclosure; hiding per-unit rates so decoys cannot be spotted.

**Ethical boundary.**
- **Green:** monotonic or flat per-unit value; every pack purchasable and useful; per-unit value visible.
- **Amber:** "most popular" or "best value" labels — must be true (computed from real sales or real per-unit value).
- **Red:** products intentionally designed to be worse value to steer choice, unless disclosed per-unit.

**Check.** Sort packs by price and compute units per dollar; flag any pack whose per-unit value is lower than a cheaper pack.

---

## 11. Scarcity and urgency

**Mechanism.** Things seem more valuable when scarce or disappearing (Worchel, Lee & Adewole 1975: cookies from a nearly empty jar were rated more desirable; Robert Cialdini's *Influence*, 1984, lists scarcity among six principles of persuasion). Time limits create urgency that shortens deliberation.

**Legitimate uses.**
- Real live-ops scarcity: seasonal events and limited cosmetics give the calendar rhythm and give lapsed players reasons to return.
- Time-limited challenges create shared moments for the community.

**Abuse pattern.** Countdown timers that reset when they expire; "Only 3 left!" on infinite digital goods; offers that appear "once only" but recur; urgency used on purchase screens to prevent comparison.

**Ethical boundary.**
- **Green:** event windows announced in advance, with clear end dates; cosmetics that return in later rotations (announced policy).
- **Amber:** limited-time offers — timers must be truthful (the offer genuinely ends and does not reappear identically within a stated window), no stock counters on digital goods, and power items should not be exclusive to a short window.
- **Red:** fake timers, fake stock counts, recurring "last chance" offers presented as unique; urgency targeted at minors.

**Measure.** Audit: list every timer in the build and verify server-side that it truly ends; track offer recurrence.

---

## 12. Social proof

**Mechanism.** People infer correct behaviour from what others do (Cialdini 1984; classic demonstrations include Asch's conformity studies of the 1950s). In product design: popularity indicators, reviews, friends' activity.

**Legitimate uses.**
- Showing what friends are doing ("Maya cleared level 40") supports relatedness and goal setting.
- True community stats ("68% of players chose the left path").
- Labelling the genuinely most-bought pack.

**Abuse pattern.** Fabricated purchase feeds ("Player123 just bought the Mega Pack!"), fake player counts, bots presented as real friends or rivals, inflated "most popular" labels.

**Ethical boundary.**
- **Green:** true, aggregated data; friend activity with the friend's permission.
- **Amber:** bots in matchmaking for new players — allowed for onboarding and queue health, but never used in purchase-related social proof, never presented as specific real people in social features, and disclosed in the game's help/FAQ.
- **Red:** any fabricated social activity used to drive purchases or engagement; fake reviews.

---

## 13. Reciprocity

**Mechanism.** People feel obliged to return favours (Regan 1971: participants given an unsolicited drink bought more raffle tickets from the giver; Cialdini 1984).

**Legitimate uses.**
- Gifting between players (lives, energy, help requests) builds relatedness — reciprocity between *players* is People Fun.
- Generous free rewards build goodwill and trust.

**Abuse pattern.** "Gift then ask": a free gift immediately followed by a purchase offer framed as a return favour ("We gave you 50 gems! Will you support us?"); guilt-laden copy when declining.

**Ethical boundary.**
- **Green:** player-to-player gifting with no obligation enforcement; free gifts with no attached ask.
- **Amber:** "support the developer" offers (common in indie games) — clearly optional, not adjacent to a gift, no guilt copy, shown at most once per milestone.
- **Red:** confirmshaming on decline ("No thanks, I don't like free stuff"); gifts timed to set up an immediate sale; punishing players who don't reciprocate in team systems.

---

## 14. Commitment and consistency

**Mechanism.** After a small commitment, people tend to act consistently with it (Freedman & Fraser 1966, the "foot-in-the-door" technique: people who agreed to a small request were more likely to agree to a larger one). Publicly stated commitments are stickier.

**Legitimate uses.**
- Players choosing a faction, team or long-term goal deepens identity and investment.
- Pledges in co-op ("I'll contribute 5 runs this week") support teamwork when opt-in.
- A low-price first purchase that is genuinely good value lets players try paying without much risk.

**Abuse pattern.** "Payer conversion ladders" designed to escalate spending step by step ($0.99 → $4.99 → $19.99 → $99.99 offers targeted on purchase history); daily streak traps; team obligations enforced by kicking.

**Ethical boundary.**
- **Green:** opt-in identity choices; one fair-value starter pack.
- **Amber:** personalised offers based on purchase history — adults only, price ceilings that do not escalate after each purchase, cool-down after any purchase, and suppression for players showing problematic-spending signals (`ethics-and-dark-patterns.md` §8).
- **Red:** offer sequences engineered to escalate price after each purchase; personalised offers to minors.

---

## 15. Peak-end rule and duration neglect

**Mechanism.** Retrospective evaluation of an experience is driven largely by its most intense moment and its end, with duration mattering little (Kahneman, Fredrickson, Schreiber & Redelmeier 1993: participants preferred a longer cold-water immersion that ended slightly less cold; Redelmeier & Kahneman 1996 on remembered pain of medical procedures).

**Legitimate uses.**
- End every level, session and season on a high: results-screen celebration, the last renovation reveal, season finale.
- Put the climax near the end of a level (boss, final wave) and resolve quickly.
- After a loss, end the failure screen on what was gained and how to improve, not on the loss.

**Abuse pattern.** Using a big end reward to paper over a frustrating, monetized experience so players remember it fondly; placing offers at emotional peaks when judgement is weakest.

**Ethical boundary.**
- **Green:** strong endings that reflect real progress; honest recap.
- **Amber:** offers on the results screen after a win — capped frequency, never on the first wins of the FTUE, dismissible in one tap.
- **Red:** offers at frustration peaks (directly after repeated losses); end rewards used to mask manipulative mid-session mechanics.

**Measure.** End-of-session sentiment micro-survey (1 tap) correlated with next-day return.

---

## 16. Near-miss

**Mechanism.** Outcomes that come close to a win are experienced as more motivating than clear losses and can increase the urge to continue, even in pure-chance games (Reid 1986 on near-misses in gambling; Clark et al. 2009, *Neuron*, found near-misses recruited reward-related brain circuitry and increased desire to play).

**Legitimate uses.** In **skill** games, honest proximity information helps learning and motivates retry: "2 blockers left", a heat map of how far you got, a ghost of your best run.

**Abuse pattern.** In **chance** outcomes, displaying near-wins that were never at stake: spinner wheels that slow down and stop one notch from the jackpot; loot-box reveals that flash a legendary before settling on a common; "so close!" copy on random outcomes.

**Ethical boundary.**
- **Green:** accurate proximity feedback in skill outcomes.
- **Amber:** "so close" framing on failure in skill games — only when objectively close (e.g. ≤ 10% of the goal remaining), and not adjacent to a paid continue.
- **Red:** engineered near-misses on any random outcome; near-miss animations on paid random draws; "almost" messages paired with paid continues.

**Check.** Every random reveal animation must be determined *after* the outcome and must not over-represent near-jackpot frames relative to their true probability.

---

## 17. Hyperbolic discounting (present bias)

**Mechanism.** People discount future rewards steeply in the short term and more gently further out, so immediate gratification beats a larger later reward when the immediate option is close (George Ainslie's work from the 1970s; David Laibson's 1997 "quasi-hyperbolic" β–δ model). A simple form: value = `A / (1 + k·D)` for amount *A* at delay *D*, with a person-specific *k*.

**Worked example.** With *k* = 0.1 per minute, a reward of 10 now is worth 10; the same reward after a 60-minute timer feels worth `10 / (1 + 6) ≈ 1.4`. That gap is the "impatience value" a skip sells.

**Legitimate uses.**
- Short wait timers as pacing and session-ending devices (a natural stop) in builders and idle games.
- Immediate feedback and rewards for actions (good feel and learning).
- Optional skips for players who value time over money, at transparent prices.

**Abuse pattern.** Timers tuned primarily to maximise skip purchases; skip prices shown only in premium currency; escalating timers that grow faster than content; "watch an ad to skip" stacked so often that the timer exists only to create ad inventory.

**Ethical boundary.**
- **Green:** short, predictable timers that serve pacing; rewarded-ad skips with daily caps.
- **Amber:** paid skips — real-money equivalent visible, price proportional to time saved, no timers longer than the content justifies, never on the FTUE path.
- **Red:** timers whose only purpose is to sell skips (no pacing function in design notes); pay-to-skip offers aimed at minors.

**Measure.** Skip purchase rate vs timer length (a steep curve suggests the timer is a sales tool); share of sessions that end at a timer and return later (healthy pacing) vs abandon.

---

## 18. Defaults

**Mechanism.** People tend to stick with pre-set options (Johnson & Goldstein 2003: organ-donor registration was far higher in opt-out than opt-in countries; Madrian & Shea 2001: automatic 401(k) enrolment greatly increased participation). Defaults carry implied endorsement and save effort.

**Legitimate uses.** Defaults are unavoidable, so make them serve the player:
- Accessibility and comfort options default to readable (adequate text size, subtitles on for story, reduced flashing honoured from the OS setting).
- Privacy-protective defaults (no personalised ads until consent; children's protections when age is unknown).
- Sensible difficulty defaults with easy access to change.
- Notifications off until the player opts in at a moment where the value is clear.

**Abuse pattern.** Pre-ticked auto-renew; premium currency auto-spent on continues; "accept all" pre-selected; marketing notifications on by default; auto-purchase of the next pass tier.

**Ethical boundary.**
- **Green:** defaults that favour privacy, comfort, accessibility and spending control.
- **Amber:** subscription auto-renewal (platform-standard) — price, period and cancellation path shown clearly before purchase; reminder before renewal where platform supports it.
- **Red:** premium currency or real money spent without an explicit confirmation step; pre-selected purchases; consent pre-ticked.

---

## 19. Framing

**Mechanism.** Logically equivalent descriptions lead to different choices (Tversky & Kahneman 1981, the "Asian disease" problem: the same outcome described as lives saved vs lives lost reversed preferences).

**Legitimate uses.**
- Encourage persistence: "Try again" instead of "You lost a life"; "You kept 3 golems" instead of "You lost 2".
- Mastery framing for feedback (see `motivation-models.md` §10).
- Accessibility of risk: show both framings for important risks ("70% success / 30% fail").

**Abuse pattern.** Framing costs as savings ("Save 500 gems!") when the player spends; describing odds as "up to" or "chance for legendary" without numbers; framing a purchase as avoiding a loss.

**Ethical boundary.**
- **Green:** encouraging framing of play outcomes.
- **Amber:** promotional copy — must be literally true and reproducible from in-game numbers.
- **Red:** odds disclosed in confusing formats (e.g. "1 in 2,000" for one item and "0.3%" for another on the same screen to frustrate comparison); cost framed as a saving.

**Odds disclosure format (studio standard).** Percentages with consistent decimal places, per item or per rarity tier, plus the pity rule in plain words, on the same screen as the purchase button, before purchase.

---

## 20. Mental accounting and currency abstraction

**Mechanism.** People sort money into mental accounts and treat it differently by source and label (Richard Thaler 1985, 1999). The "pain of paying" is reduced when payment is decoupled from consumption (Prelec & Loewenstein 1998). Unfamiliar currencies can distort spending (Raghubir & Srivastava 2002 found people spent differently with foreign currency depending on the face-value ratio).

**How games use it.** Premium currency (gems) decouples the moment of payment from consumption; odd exchange rates (e.g. 1 USD ≈ 105 gems) make mental conversion hard; pack sizes that never match item prices leave remainders that invite another purchase; multiple currencies per screen.

**Legitimate uses.**
- A single premium currency can simplify a store across many items and support earning premium currency through play.
- Separate "earned" and "bought" accounts can be clearer for players (e.g. earned-only event tokens).

**Abuse pattern.** Currency layers designed to obscure real cost; pack sizes deliberately mismatched to item prices; real-money prices never shown; premium currency spent in one tap.

**Ethical boundary.**
- **Green:** one premium currency at most, plus earned-only currencies; real-money equivalent shown wherever premium currency is spent; pack sizes that allow buying common items without forced leftovers.
- **Amber:** premium-currency-only pricing for items — acceptable only if the real-money equivalent is shown and confirmation is required above a threshold (studio default: any spend equivalent to ≥ USD 5 asks for confirmation).
- **Red:** more than one purchasable premium currency; deliberately mismatched pack sizes; no real-money equivalent anywhere.

**Regulatory note (verify before relying).** In March 2025 the EU Consumer Protection Cooperation (CPC) network, with the European Commission, published key principles on in-game virtual currencies that point in this direction (clear real-money pricing, no obscuring of cost, protection of minors). Confirm the current text and its status with `legal-ethics` and `arcosian:compliance-officer`; see `ethics-and-dark-patterns.md` §7.

**Leftover check.** For each premium item price *c* and pack size *s*, compute `s mod c` across common items; if the typical leftover after buying the most common item is more than ~20% of the pack, re-size packs or prices.

---

## 21. Two more: choice overload and the fresh-start effect

### 21.1 Choice overload
**Mechanism.** Too many options can reduce choice satisfaction or the likelihood of choosing at all (Iyengar & Lepper 2000, the jam-tasting study). *Caveat:* a meta-analysis (Scheibehenne, Greifeneder & Todd 2010) found the average effect close to zero with large variation — overload appears when options are hard to compare, the chooser lacks preferences, or time is short (all common on phones).
**Use:** keep decision sets to 2–4 on mobile; store front pages with 3–6 items; categorise long catalogues; recommend honestly.
**Boundary:** green when reducing confusion; red when complexity is deliberately added to prevent price comparison.

### 21.2 Fresh-start effect
**Mechanism.** Temporal landmarks (new week, month, birthday) increase motivation to pursue goals (Dai, Milkman & Riis 2014).
**Use:** season starts, weekly league resets, "new chapter" moments; welcome-back states for lapsed players that clear old obligations instead of showing a wall of expired events.
**Boundary:** green. Watch only for pairing fresh starts with aggressive offers.

---

## 22. Anatomy of a stacked offer — and its ethical rewrite

Many F2P offers stack several biases at once. A common pattern, triggered when a player fails a level for the third time:

> Full-screen popup. "SO CLOSE! You only needed 2 more moves!" Timer: 04:59. "Get +5 moves and 3 boosters — 900 gems (value 800%!)". The player has 600 gems. Second button: "Buy 1,000 gems $9.99". Decline text: "Give up and lose your progress".

| Element | Bias exploited | Test failed | Grade |
|---|---|---|---|
| Triggered on third failure | Vulnerability (frustration peak) | Vulnerability | Red |
| "SO CLOSE" | Near-miss framing | Sunlight if not objectively close | Amber → red when paired with a sale |
| 5-minute timer | Urgency / scarcity | Sunlight (fake urgency) | Red |
| "value 800%" | Anchoring against an unclear baseline | Sunlight | Red unless reproducible |
| 900 gems vs 600 owned, 1,000 pack | Mental accounting, leftover engineering | Alignment | Red |
| "lose your progress" | Loss aversion, sunk cost, confirmshaming | Alignment, vulnerability | Red |

**Ethical rewrite (same business goal: offer help to stuck players).**
- Trigger: not on the failure screen. After the third failure, offer a *free* hint or a booster earned through play; show a "Need help?" button on the level-select screen the next time the player arrives.
- Failure screen shows accurate progress ("2 blockers left") and a one-tap **Retry**.
- The move-pack is available in the shop at a fixed price with the real-money equivalent visible, no timer and a factual description ("+5 moves for this attempt").
- Paid continue (if any): fixed price shown *before* the level starts, max one per attempt, never escalating.
- Difficulty: if many players fail a level repeatedly, that is a level-design problem — fix the curve (`progression-difficulty`), do not monetise the spike.

---

## 23. Behavioural-economics audit checklist

Run this on any feature that touches rewards, time pressure, social systems or money. Record results in the feature's `gate_notes` or a review report.

- [ ] Every random reward lists its odds (if paid, before purchase), its pity rule, and passes the drop-tail check (99th percentile attempts computed).
- [ ] No offer is triggered by a loss, failure streak, streak break or out-of-resources event.
- [ ] No continue/revive price escalates within a run; prices visible before the decision.
- [ ] Every timer is truthful (server-verified end; no reset; recurrence policy written).
- [ ] No stock counters on digital goods; "limited" claims are true.
- [ ] Every "value", "best", "most popular" label is reproducible from store data.
- [ ] Per-unit value is flat or improving across pack sizes, or differences are disclosed.
- [ ] Real-money equivalent shown wherever premium currency is spent; confirmation at the threshold.
- [ ] Pack sizes leave reasonable leftovers for common items.
- [ ] Defaults favour privacy, comfort and spending control; nothing pre-selected that costs money.
- [ ] Trials are labelled as trials at grant time; no unlabelled expiring "gifts".
- [ ] No player creation or owned item can be lost to inactivity or held for ransom.
- [ ] Near-miss presentation only on skill outcomes, only when objectively close, never next to a paid continue.
- [ ] Social proof uses true data only; bots never appear in purchase-related social proof.
- [ ] Decline buttons are neutral ("Not now"); no confirmshaming.
- [ ] Session has a natural stop with closure; badge count on home ≤ 3.
- [ ] Minors (by age gate) receive none of the amber techniques and no paid randomness.
- [ ] Problematic-spending signals suppress personalised offers (see `ethics-and-dark-patterns.md` §8).

---

## 24. Metrics that detect abuse

Healthy monetization and engagement leave different fingerprints than exploitative ones. Add these to the KPI review (`player-analytics`, `arcosian:data-analyst`).

| Metric | Healthy signal | Warning signal | Notes |
|---|---|---|---|
| Purchases within 60 s of a failure event / all purchases | Close to the share of time spent on failure screens | Strongly over-represented | Indicates frustration-triggered selling |
| Revenue share of top 1% of payers | Stable, game-appropriate | Rising concentration with rising refund/complaint rate | Concentration alone is not proof; combine signals |
| Refund and chargeback rate by product | Low and flat | Spikes on specific offers | Investigate offer design and clarity |
| Post-purchase retention of the purchased item | Item used after purchase | Item unused, purchase followed by churn | Suggests regret or impulse |
| Late-night session share (local 00:00–05:00) for minors | Low | Rising | Wellbeing review trigger |
| Session length after loss streaks | Shorter (players stop and come back) | Much longer with spend | Chasing pattern |
| Regret micro-survey ("Glad I spent?" 1 tap, sampled) | Mostly yes | Rising no | Direct reflective-endorsement signal |
| Support tickets with keywords (scam, tricked, didn't mean to buy, my child) | Rare | Rising | Route to `arcosian:compliance-officer` |
| Streak-break churn | Small effect | Large spike at break | Streak design too punitive |

Use `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/ab_test.py analyze ...` when comparing an ethical rewrite against an existing design; expect short-term revenue to sometimes dip and long-term retention and trust metrics to be the decision criteria agreed *before* the test.

---

## 25. Sources

Paraphrased; consult originals. Contested findings are flagged in the text.

- Ainslie, G. (1975). "Specious reward: A behavioral theory of impulsiveness and impulse control." *Psychological Bulletin*, 82(4).
- Ariely, D. (2008). *Predictably Irrational*. HarperCollins.
- Arkes, H. R., & Blumer, C. (1985). "The psychology of sunk cost." *Organizational Behavior and Human Decision Processes*, 35(1).
- Cialdini, R. B. (1984). *Influence: The Psychology of Persuasion*. William Morrow.
- Clark, L., Lawrence, A. J., Astley-Jones, F., & Gray, N. (2009). "Gambling near-misses enhance motivation to gamble and recruit win-related brain circuitry." *Neuron*, 61(3).
- Dai, H., Milkman, K. L., & Riis, J. (2014). "The fresh start effect." *Management Science*, 60(10).
- Ferster, C. B., & Skinner, B. F. (1957). *Schedules of Reinforcement*. Appleton-Century-Crofts.
- Freedman, J. L., & Fraser, S. C. (1966). "Compliance without pressure: The foot-in-the-door technique." *Journal of Personality and Social Psychology*, 4(2).
- Gal, D., & Rucker, D. D. (2018). "The loss of loss aversion." *Journal of Consumer Psychology*, 28(3).
- Huber, J., Payne, J. W., & Puto, C. (1982). "Adding asymmetrically dominated alternatives." *Journal of Consumer Research*, 9(1).
- Hull, C. L. (1932). "The goal-gradient hypothesis and maze learning." *Psychological Review*, 39(1).
- Iyengar, S. S., & Lepper, M. R. (2000). "When choice is demotivating." *Journal of Personality and Social Psychology*, 79(6).
- Johnson, E. J., & Goldstein, D. (2003). "Do defaults save lives?" *Science*, 302(5649).
- Kahneman, D., Fredrickson, B. L., Schreiber, C. A., & Redelmeier, D. A. (1993). "When more pain is preferred to less." *Psychological Science*, 4(6).
- Kahneman, D., Knetsch, J. L., & Thaler, R. H. (1990). "Experimental tests of the endowment effect and the Coase theorem." *Journal of Political Economy*, 98(6).
- Kahneman, D., & Tversky, A. (1979). "Prospect theory." *Econometrica*, 47(2).
- Kivetz, R., Urminsky, O., & Zheng, Y. (2006). "The goal-gradient hypothesis resurrected." *Journal of Marketing Research*, 43(1).
- Laibson, D. (1997). "Golden eggs and hyperbolic discounting." *Quarterly Journal of Economics*, 112(2).
- Madrian, B. C., & Shea, D. F. (2001). "The power of suggestion: Inertia in 401(k) participation and savings behavior." *Quarterly Journal of Economics*, 116(4).
- Norton, M. I., Mochon, D., & Ariely, D. (2012). "The IKEA effect: When labor leads to love." *Journal of Consumer Psychology*, 22(3).
- Prelec, D., & Loewenstein, G. (1998). "The red and the black: Mental accounting of savings and debt." *Marketing Science*, 17(1).
- Raghubir, P., & Srivastava, J. (2002). "Effect of face value on product valuation in foreign currencies." *Journal of Consumer Research*, 29(3).
- Redelmeier, D. A., & Kahneman, D. (1996). "Patients' memories of painful medical treatments." *Pain*, 66(1).
- Regan, D. T. (1971). "Effects of a favor and liking on compliance." *Journal of Experimental Social Psychology*, 7(6).
- Reid, R. L. (1986). "The psychology of the near miss." *Journal of Gambling Behavior*, 2(1).
- Scheibehenne, B., Greifeneder, R., & Todd, P. M. (2010). "Can there ever be too many options?" *Journal of Consumer Research*, 37(3).
- Thaler, R. H. (1985). "Mental accounting and consumer choice." *Marketing Science*, 4(3). — and (1999) "Mental accounting matters." *Journal of Behavioral Decision Making*, 12(3).
- Tversky, A., & Kahneman, D. (1974). "Judgment under uncertainty: Heuristics and biases." *Science*, 185(4157).
- Tversky, A., & Kahneman, D. (1981). "The framing of decisions and the psychology of choice." *Science*, 211(4481).
- Tversky, A., & Kahneman, D. (1992). "Advances in prospect theory: Cumulative representation of uncertainty." *Journal of Risk and Uncertainty*, 5(4).
- Worchel, S., Lee, J., & Adewole, A. (1975). "Effects of supply and demand on ratings of object value." *Journal of Personality and Social Psychology*, 32(5).
- Zeigarnik, B. (1927). "Über das Behalten von erledigten und unerledigten Handlungen." *Psychologische Forschung*, 9.
- Zendle, D., & Cairns, P. (2018). "Video game loot boxes are linked to problem gambling: Results of a large-scale survey." *PLOS ONE*, 13(11).
