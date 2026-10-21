# Style bible: [game title]

Revision: [date] | Owner: `art-director` | Lock status: [draft / locked on date]

<!-- The style bible is what makes 200 assets look like one game. It must be specific enough that a new artist, or an image model with reference images, produces matching work without asking. Show, do not describe: attach reference images and approved samples. -->

## Style statement
[Two sentences: the look and the feeling. Example form: "Chunky, hand-cut paper shapes with warm light; playful, never cute-for-its-own-sake."]

## References
| Reference | Take | Avoid |
|---|---|---|
| [game / artist / image link] | [shape language, palette, etc.] | [what not to copy] |

<!-- Reference for inspiration only; never trace or reproduce protected work. -->

## Visual rules
| Aspect | Rule |
|---|---|
| Shape language | [round / angular / mixed; ratio] |
| Outline | [none / width in px at 1x / color rule] |
| Perspective and camera | [top-down, side, isometric angle] |
| Lighting | [direction, rim, shadow style] |
| Detail density | [low / medium; max elements per icon] |
| Texture and noise | [flat / painterly / grain level] |

## Palette
| Role | Hex | Usage | Contrast note |
|---|---|---|---|
| Background | [#......] | [..] | |
| Primary | [#......] | [..] | |
| Accent / reward | [#......] | [..] | |
| Danger | [#......] | [..] | |
| UI text | [#......] | [..] | Check at least 4.5:1 on its background |

Do not rely on color alone for meaning; pair it with shape or icon.

## Typography and UI
- Display font: [name, licence]; body font: [name, licence]
- Minimum text size: [pt at reference resolution]
- Button, panel and icon style: [rules]; corner radius: [px]
- Safe areas and notches: [handling]

## Characters and objects
- Proportions: [head-to-body, silhouette test: readable at 48 px]
- Expression and animation principles: [squash and stretch amounts, timing]

## Technical constraints
| Item | Value |
|---|---|
| Reference resolution | [e.g. 1080 x 1920] |
| Sprite sheet / atlas size | [max px], padding [px] |
| Texture compression | [per platform] |
| Texture memory budget | [MB] |

## AI generation lock (if used)
- Model and version: [..]; seed policy: [..]; reference images: [file list]
- Prompt prefix (style lock): [fixed text]; negative prompt: [fixed text]
- Acceptance: three approved samples must match before a batch starts; drift check every [n] assets.
- Licensing and disclosure: [tool terms; store AI disclosure noted]

## Do and don't
| Do | Don't |
|---|---|
| [..] | [..] |
