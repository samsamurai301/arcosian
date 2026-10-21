# Art Critique Rubric and the Comparative Tournament

This file defines how the studio judges art: a weighted rubric with scoring anchors for screens and assets, a protocol for running visual critique with models or humans without trusting any single pass, and the comparative tournament method for picking one winner out of many AI-generated candidates. The core insight is measurement, not taste: absolute scores from a model or a tired human drift and cluster around the middle, while a pairwise question ("which of these two fits the style bible better?") is far more reliable. Scripts in `scripts/` implement the aggregation and the ranking (`critique_aggregate.py`, `tournament_rank.py`), and `palette_audit.py` supplies objective colour numbers to the rubric.

## Contents

1. [What critique is for](#1-what-critique-is-for)
2. [The rubric](#2-the-rubric)
3. [Scoring anchors](#3-scoring-anchors)
4. [Severity and flags](#4-severity-and-flags)
5. [Pass thresholds by milestone tier](#5-pass-thresholds-by-milestone-tier)
6. [Running a critique pass](#6-running-a-critique-pass)
7. [Aggregating with critique_aggregate.py](#7-aggregating-with-critique_aggregatepy)
8. [Comparative tournament method](#8-comparative-tournament-method)
9. [Running a tournament with tournament_rank.py](#9-running-a-tournament-with-tournament_rankpy)
10. [Objective checks that precede judgement](#10-objective-checks-that-precede-judgement)
11. [Giving feedback that production can use](#11-giving-feedback-that-production-can-use)
12. [Worked example](#12-worked-example)
13. [Failure modes of critics](#13-failure-modes-of-critics)

---

## 1. What critique is for

Critique serves three decisions: **accept or reject** an asset or screen, **choose** among candidates, and **direct** the next iteration. Use different tools for each. Accept/reject needs a rubric with thresholds. Choosing needs the tournament. Directing needs specific, actionable notes tied to a rule in the style bible.

Principles:
- Critique against the bible, not against personal taste. If a rule is missing from the bible and a critic keeps raising it, add the rule.
- Critique the screen on a real device capture at real size (a screenshot from the playtest runner), not on a zoomed desktop view.
- Separate "is it on-style" from "is it good". A beautiful asset in the wrong style is a reject.
- Humans sign off on style and on store-facing art. Critique by models is an advisory screen.

## 2. The rubric

Five criteria, scored 1-5 per criterion, matching the names `critique_aggregate.py` expects. Weights are the tool's defaults and can be overridden in the input file; they sum to 1.

| Criterion | Weight | What it asks |
|---|---|---|
| readability | 0.30 | Can the player parse gameplay-critical elements instantly at phone size? Hierarchy, contrast, silhouette, clutter |
| consistency | 0.25 | Does it follow the style bible (shape language, line, shading, palette, detail density) and match neighbouring approved assets (proportions, lighting, finish)? |
| technical | 0.20 | Size, format, transparency, pivot, padding, memory and naming per the spec; text legibility and safe areas |
| appeal | 0.15 | Does it deliver the intended emotional target and feel distinctive? |
| polish | 0.10 | Craft: edges, anatomy and perspective, artifacts, banding, alignment, text rendering, no obvious generation errors |

Note that "on-style" lives inside consistency; if a project wants style adherence separated, run the aggregator twice with a different input file rather than renaming criteria (the tool rejects unknown names).

## 3. Scoring anchors

Anchors prevent drift: a score of 3 must mean the same thing every time. Use these descriptions verbatim in the reviewer prompt.

| Score | Meaning | Readability example | Consistency example |
|---|---|---|---|
| 5 | Exemplary; could be used as a bible example | Every critical element is identifiable in 200 ms at phone size; clear single focal point | Every checkable rule is met; indistinguishable from approved work |
| 4 | Good; ship with at most trivial polish | One minor ambiguity that does not affect play | One minor deviation (e.g. line weight off by a small amount) |
| 3 | Acceptable for a prototype; needs work for release | Critical elements readable but the player must look; some clutter | Several small deviations or one clear deviation in a secondary rule |
| 2 | Weak; fix before it goes further | A critical element is easily missed or confused with another | Violates a primary rule (palette or shape language) |
| 1 | Fails | The screen cannot be played without guessing | Clearly belongs to a different style |

Anchors for polish: 5 = no artifacts at 200% zoom; 4 = artifacts only at high zoom; 3 = visible at normal view but minor; 2 = distracting (broken hands, warped text, stray marks); 1 = unusable.

Scoring guidance for reviewers:
- Start at 3 and justify moving up or down with a concrete observation.
- A 5 needs a stated reason; a 1 needs a flag.
- Give a score for each criterion even if the answer is "unclear"; mark unclear items as a flag with low confidence.

## 4. Severity and flags

A flag is a specific defect with a location and a fix. Flags are what actually get fixed.

| Severity | Definition | Effect |
|---|---|---|
| blocker | Breaks gameplay or violates legal or store rules (illegible critical element, trademarked content, wrong content for the age rating) | Fails any tier; routes to a human |
| major | Visible quality or consistency problem the player will notice | Fails slice tier and above |
| minor | Polish item | Logged, fixed in the polish pass |
| nit | Taste-level suggestion | Optional |

The aggregator's flag format is `{id, severity, where, evidence, note}`. Use a stable snake_case `id` per defect type (`text_clipping`, `hand_artifact`, `edge_halo`) so the same defect reported by several reviewers at the same `where` is confirmed by quorum. Put the suggested fix in `note`. Severities in the tool are blocker, major, minor and polish (the nit level of this table maps to polish). Reviews that flag without a location or a fix are rejected by the lead.

## 5. Pass thresholds by milestone tier

Quality bars rise as the game matures. Tiers match `critique_aggregate.py --tier`. Presets as implemented at the time of writing (the script is the source of truth; override with `--floor` and `--pass-score`):

| Tier | Intent | Per-criterion floor | Weighted pass score | Confirmed flags that fail |
|---|---|---|---|---|
| prototype | Find the fun; art only needs to be readable | 2 | 2.5 | blocker |
| slice | One representative slice at release quality | 3 | 3.5 | blocker, major |
| soft_launch | Players outside the team see it | 3 (readability and technical 4) | 4.0 | blocker, major |
| global | Store launch | same as soft_launch | 4.0 | blocker, major |
| live | Ongoing content | same as soft_launch | 4.0 | blocker, major |

For `live`, add a drift check outside the tool: compare a sample of new assets side by side with launch assets. Re-read the thresholds with `python3 ${CLAUDE_PLUGIN_ROOT}/skills/art-direction/scripts/critique_aggregate.py --help` before quoting them.

## 6. Running a critique pass

Use at least three independent passes. Independence comes from varying one of: reviewer model, image crop or zoom, screen sample, or prompt framing (for example one pass focused on readability, one on style adherence, one on craft).

Procedure:
1. Collect captures: the screen at native size, plus 2x crops of the HUD, the focal area and any new asset. For animation, capture three frames (start, peak, end).
2. Run objective checks first (section 10) and give the numbers to the reviewers.
3. Give each reviewer: the style bible excerpt, the anchors table, the objective numbers, the captures, and the output schema.
4. Ask for scores for each criterion with a one-sentence justification, then flags with severity, location and fix.
5. Collect the JSON from every pass into one reviews file (`{subject, tier, reviews: [{reviewer, scores, flags}]}`).
6. Aggregate (section 7). Treat unconfirmed blockers as items for a human to look at, not as automatic failures or automatic dismissals.
7. Route: pass -> accepted; fail with confirmed flags -> fix list to the producer; split decision -> human.

Reviewer prompt skeleton:

```
You are critiquing <asset|screen> for <game>. Use only the style bible below and the anchors.
Score each criterion 1-5 using the anchors; start at 3 and justify any move.
List flags: {id, severity, where, evidence, note}.
Do not praise generally. Do not invent rules not in the bible. If something cannot be judged from the capture, say so.
Return JSON only, in this schema: <schema>
```

## 7. Aggregating with critique_aggregate.py

The tool computes the median per criterion across reviewers, the weighted score, flag confirmation by quorum (a flag counts as confirmed when enough reviewers (default two thirds, minimum two) report the same flag id at the same location), and a verdict by tier. Why median: one drifting reviewer cannot move it. Why quorum: single-pass hallucinated flags are common.

```
python3 ${CLAUDE_PLUGIN_ROOT}/skills/art-direction/scripts/critique_aggregate.py --in reviews.json --tier slice --md evidence/F012/visual_review.md --json
```

Exit codes: 0 pass, 1 fail, 2 input error. Outputs a markdown report suited for the evidence folder of a feature. Use `--quorum` to tune sensitivity: a higher quorum reduces false positives and increases missed defects; keep the default for gates and lower it when you want a thorough defect hunt.

Interpreting results:
- Pass with confirmed minors: accept and queue polish.
- Fail with a confirmed major: fix list is the deliverable; re-run only the failing criterion after the fix.
- Unconfirmed blocker: escalate to the human; a blocker is severe enough that one credible report deserves a look.
- Scores clustering at 3-4 with no flags: suspect an under-critical reviewer; add a pass with an adversarial prompt ("find the three weakest things").

## 8. Comparative tournament method

When AI generates a batch of candidates for an icon, a hero, a key art or a style frame, picking by absolute score wastes the signal. Pairwise comparison forces a relative judgement and works for both humans and models.

Method:
1. **Pre-filter objectively.** Drop candidates that fail hard checks: wrong size or aspect, background not removable, text garbled, obvious anatomy errors, palette audit failure, forbidden content. Do this before judging so judges only compare viable candidates.
2. **Define the question once.** The pairwise question must be concrete and tied to the bible: "Which image better matches the style bible and reads more clearly at 64 px?" Use one question per tournament; run a second tournament for a second dimension rather than mixing them.
3. **Present both orders.** Every pair is shown as (A,B) and (B,A) because judges, especially models, prefer the first or the second position. Position bias is a measured, not hypothetical, issue; the tool schedules both orders by default.
4. **Few rounds, many judges.** Use 3 or more judge calls per pair if budget allows, with different framing or models.
5. **Rank with Bradley-Terry.** The model estimates a strength per candidate from the votes; strengths give a ranking and a confidence picture (close races are visible).
6. **Check bias.** The tool reports how often the first-shown item won. A rate far from one half means judge position bias; the both-orders scheme neutralizes most of it.
7. **Top-k to a human.** Send the top 2-3 to the human checkpoint with the ranking and the reasons; the human picks. Never auto-ship store-facing art from a model tournament alone.
8. **Record.** Store the votes, the ranking and the chosen id in the manifest (`status: approved`, `approved_by`), so the decision is auditable.

Sizing: with N candidates, round-robin has N(N-1)/2 pairs (times two orders). Use round-robin up to about 8-10 candidates. Beyond that use the sampling mode (each candidate meets about K random opponents) or Swiss-style rounds that pair candidates of similar current strength, which concentrates comparisons near the top.

Cost sketch: 12 candidates, sampling with K = 4 and both orders is roughly 12 x 4 / 2 x 2 = 48 judgements. Multiply by the per-call cost of the judge model to get the budget, and compare with the cost of generating more candidates. Judges that see images cost more than text-only calls, so downscale the images shown to the judge to the size the player will see (this also aligns the judgement with readability).

## 9. Running a tournament with tournament_rank.py

```
# 1. Schedule comparisons (both orders by default)
python3 ${CLAUDE_PLUGIN_ROOT}/skills/art-direction/scripts/tournament_rank.py schedule --items c01,c02,c03,c04 --mode roundrobin
python3 ${CLAUDE_PLUGIN_ROOT}/skills/art-direction/scripts/tournament_rank.py schedule --items c01,...,c16 --mode sample --per-item 4 --seed 7
# 2. Collect votes from judges, then rank (optionally fail when the winner is not clear)
python3 ${CLAUDE_PLUGIN_ROOT}/skills/art-direction/scripts/tournament_rank.py rank --votes votes.json --bootstrap 200 --min-margin 0.65 --json
# 3. Optional Swiss-style follow-up round using the votes so far
python3 ${CLAUDE_PLUGIN_ROOT}/skills/art-direction/scripts/tournament_rank.py next --help
```

The votes file is CSV (header `left,right,winner[,judge][,criterion]`) or a JSON list of objects with those keys; `winner` is the left id, the right id, or `tie`. Run each subcommand with `--help` for details. Keep the schedule in the workflow's scratch files and the votes next to the manifest.

Judge prompt skeleton:

```
Two images, A and B, for <asset type> in <game>. Question: <the single concrete question>.
Reference: <bible excerpt or reference image>.
Answer with exactly one letter, A or B, then one sentence of reason. If they are truly equal answer the letter of the one that reads better at 64 px.
```

Do not allow "tie" as an answer in the first pass; forced choice produces cleaner rankings. If a pair is close the rank output will show similar strengths.

## 10. Objective checks that precede judgement

Give reviewers numbers so they judge what machines cannot measure.

| Check | Tool | Notes |
|---|---|---|
| Palette contrast, colour-blind separation | `palette_audit.py` | Gameplay-critical pairs, text pairs and UI pairs |
| Size, alpha, dimensions, file size | `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/image_post.py check --in <path>` | Compare with the spec table |
| Silhouette distinctness | Fill with black and compare (see visual fundamentals) | Quantify overlap if you have many units |
| Value structure | Greyscale conversion | Squint test numerically: foreground vs background luminance difference |
| Text legibility | Minimum text size and contrast per the UI spec | Fail small text before a critic sees it |
| Perf | `perf_budget.py` on the capture session | Visual passes do not replace the performance gate |

## 11. Giving feedback that production can use

- Tie every note to a rule: "Outline is 2 px, bible says 4 px at reference resolution" beats "outline looks thin".
- Say what to change and what to keep: "Keep pose and palette; increase hat size by about a third for silhouette separation from unit B."
- Prioritize: at most five must-fix items per round.
- For AI regeneration, convert feedback into prompt or reference changes (add a negative, change a reference, change the seed policy) rather than re-rolling blindly.
- Track recurring defects (hands, text, perspective) in the bible's negative prompt and in the checklist so the next batch avoids them.

## 12. Worked example

Situation: the pipeline produced 16 app icon candidates for a merge game.

1. Pre-filter: remove 4 with garbled letters and 2 whose background cannot be separated. 10 remain.
2. Palette check: 2 fail the thumbnail contrast target against both light and dark wallpapers. 8 remain.
3. Tournament: question "Which icon is more recognizable and more distinct from a generic merge-game icon at 64 px?" Round-robin on 8 candidates is 28 pairs, 56 judgements with both orders. Rank by Bradley-Terry; the first-shown win rate is checked and found near one half.
4. Top 3 go to the human with the ranking. The human picks one and asks for a lower-saturation background.
5. Craft pass: hand fix of the star highlight edge; export all platform sizes from the master.
6. Critique pass (3 reviewers, tier global) on the final icon in context screens; aggregate; pass.
7. Manifest updated: provider, prompt, seed, bible version, approver, licence status.

## 13. Failure modes of critics

| Failure | Symptom | Countermeasure |
|---|---|---|
| Score clustering | Everything gets 3-4 | Anchors, adversarial pass, comparative method |
| Position bias | First or second image wins disproportionately | Both orders, report the first-shown win rate |
| Verbosity or polish bias | Busier or shinier images win | Downscale judge input, ask the readability question explicitly |
| Style drift in the judge | The judge prefers its own idea of beauty | Always include the bible and a reference image in the prompt |
| Hallucinated defects | Flags about things not visible | Quorum confirmation, location required, crop check by a second pass |
| Missed defects | Hands, text, seams slip through | Objective checks and targeted crops (hands, text, edges) |
| Anchoring on the first reviewer | Later reviewers copy | Run passes independently and in parallel |
| Taste laundering | Personal preference presented as rule | Require a bible rule for every note; add the rule if it is real |
