# Audio bible: [game title]

Revision: [date] | Owner: `audio-director` | Lock status: [draft / locked on date]

<!-- Audio is half the game feel on mobile, and half your players have sound off. Design for both: every critical cue needs a visual or haptic partner. -->

## Audio identity
- Sonic pillars (three adjectives): [e.g. warm, tactile, bright]
- Reference tracks / games: [title - what we borrow]
- Instrument and sound palette: [acoustic, synth, foley, voice]

## Mix targets
| Bus | Role | Target loudness / level | Ducking rule |
|---|---|---|---|
| Music | Mood | [LUFS integrated, assumption until measured on device] | duck [dB] under voice |
| SFX | Feedback | [..] | |
| UI | Taps, menus | [..] | |
| Voice | Characters | [..] | priority over music |

Check on phone speaker, wired earbuds and Bluetooth; mobile speakers drop low frequencies, so avoid bass-dependent cues.

## Music plan
| Track | Use | Length | Loop? | Intensity layers |
|---|---|---|---|---|
| [menu] | [..] | [..] | yes | [..] |

- Loop QC: seamless at the loop point, no click, tail handled; checked by `audio_post.py`.
- Adaptive rules: [what raises or lowers intensity]

## SFX list
| ID | Trigger | Character | Variations | Max concurrent | Priority |
|---|---|---|---|---|---|
| [sfx_tap] | [tap] | [short, soft] | [3-5, pitch +-] | [n] | [1-5] |

<!-- Frequent sounds need variation or they become fatigue within a session. -->

## Voice (if any)
- Characters and tone: [..]; languages: [..]; line budget: [count]
- Direction notes per character: [..]
- AI voice licensing and consent: [source, rights, disclosure]

## Implementation rules
- Format: [OGG / WAV source / compressed], sample rate [Hz], mono for SFX
- Memory budget: [MB]; streaming for music, preloaded for SFX
- Interruptions: pause on phone call, respect silent switch, resume cleanly
- Haptic pairing: [events that also vibrate]

## Accessibility
- Captions or visual cues for every gameplay-critical sound
- Separate music / SFX / voice sliders; mute remembered across sessions

## Delivery checklist
- [ ] Peak below [dBFS], loudness within target
- [ ] No clipping, DC offset or clicks
- [ ] Loops verified; metadata and licences recorded in [file]
