# Doc templates

Fill-in templates for the documents a mobile game studio actually keeps alive. Copy into `.gamestudio/design/` (art and audio bibles into `.gamestudio/art/` and `.gamestudio/audio/`) or the game project's `docs/`. Text in `<!-- comments -->` is guidance: delete it once the section is filled. Anything in `[brackets]` is a blank to fill. Leave no blank empty: write "unknown, test by [date]" rather than guessing.

## Index

| Template | Owner (agent) | When | Feeds |
|---|---|---|---|
| `gdd-one-pager.md` | `game-designer` | Concept stage | design contract, pitch |
| `design-contract-guide.md` | `principal` | Before any build | `.gamestudio/` design contract |
| `feature-spec.md` | `game-designer` | Per feature | `build-feature` |
| `style-bible.md` | `art-director` | Before asset batches | `asset-production` |
| `audio-bible.md` | `audio-director` | Before audio batches | `audio-production` |
| `art-asset-brief.md` | `art-director` | Per asset batch | asset pipeline |
| `playtest-plan.md` | `qa-lead` | Per milestone | `playtest` |
| `soft-launch-plan.md` | `producer` + `data-analyst` | Before soft launch | go / iterate / kill decision |
| `liveops-calendar.md` | `liveops-manager` | Pre-launch onward | `operate` |
| `risk-register.md` | `producer` | Weekly | milestone reviews |
| `store-listing.md` | `release-manager` | Before submission | `ship`, `store_metadata.py` |
| `postmortem.md` | `producer` | After milestone or launch | `postmortem` |
| `pitch-deck-outline.md` | `principal` | Funding or publisher talks | pitch |

## Conventions

- One owner per document. Edits by others go through the owner.
- Date every revision at the top; keep a one-line change log.
- Numbers need a source or a label: `measured`, `benchmark`, or `assumption`. Assumptions get a test date.
- Claims about the market or store rules go in a "Volatile facts" block with a source URL and a re-check date.
- Documents are inputs to gates, not decoration: if nothing reads a section, cut it.

## Suggested order for a new game

1. `gdd-one-pager` and `risk-register` (day one).
2. `design-contract-guide` (turn the one-pager into a locked contract).
3. `style-bible`, `audio-bible` (before spending on assets).
4. `feature-spec` per feature, `art-asset-brief` per batch.
5. `playtest-plan` each milestone; `soft-launch-plan` before the first external install.
6. `store-listing`, `liveops-calendar` before submission.
7. `postmortem` after every milestone that mattered; `pitch-deck-outline` when you need money.

## Maintenance

Review these documents at every milestone. Stale documents are worse than none: archive what no longer matches the game, and note the date.
