# Wwise reference

Wwise (Audiokinetic) is an authoring application plus a runtime SDK. You author in Wwise, generate SoundBanks, and the game posts events to the runtime. This file covers the object model, WAAPI (the Authoring API that automation uses), the WwiseConsole command line, the engine integrations and licence tiers. Audiokinetic's documentation site blocked automated fetching in October 2026 (HTTP 403), so some details come from Audiokinetic blog and community pages and are marked unverified; confirm on your installed version.

## Contents
1. Concepts
2. Project layout and version control
3. WAAPI
4. WwiseConsole and SoundBank generation
5. Integrations
6. Runtime API shape
7. Licence tiers
8. Verification status

## 1. Concepts

| Concept | What it is | Use it for |
|---|---|---|
| Event | A list of actions (play, stop, set switch, set state, post another event) the game posts by name or ID | The only thing gameplay code should trigger |
| Actor-Mixer / Random / Sequence / Switch / Blend containers | Containers that pick or layer sounds | Variation, footsteps by surface, layered impacts |
| Game object | An emitter registered by code, with position | Each source of sound in the world |
| Game sync | Umbrella term: states, switches, RTPCs, triggers | Telling the audio engine about the game |
| State | A global condition with a set of values; changes properties of objects bound to it | Menu, pause, low health, music section |
| Switch | A per-game-object choice among values; selects which child plays in a Switch Container | Footstep surface, weapon type |
| RTPC | Real-Time Parameter Control: a continuous value mapped by curves to properties | Speed to pitch, health to filter, intensity to layers |
| Trigger | Fires a stinger in an interactive music segment | Music stingers |
| Bus / Auxiliary bus | Mix groups; aux buses carry reverb and effect sends | Master-mixer structure, room reverb |
| Interactive music hierarchy | Music Switch Container, Playlist Container, Segment, Track, with transition rules | Horizontal and vertical music |
| SoundBank | A runtime package of events, structures and (optionally) media | Memory and delivery unit |
| Work Unit | A project file holding a part of the hierarchy (XML) | Splitting the project so people do not collide |

Rules of thumb:
- Gameplay posts events. Do not call "play file" equivalents; everything goes through an event so sound design can change without a code change.
- Use switches for per-object categorical choices and states for global ones. The most common error is a footstep surface as a state.
- Map RTPCs with curves, and test the curve in the profiler. Linear is rarely right for volume.
- Keep an event-name convention (`Play_Weapon_Rifle_Fire`, `Stop_...`, `Set_...`) and enforce it with a WAAPI script.

## 2. Project layout and version control

A Wwise project has a `.wproj` file and folders (Originals, Actor-Mixer Hierarchy, Events, Interactive Music Hierarchy, Master-Mixer Hierarchy, Game Parameters, States, Switches, SoundBanks and others). Typical practice (verify with your team's source-control plug-in notes):

| Path | Commit? |
|---|---|
| `*.wproj`, `*.wwu` Work Units | Yes. Many small XML files; use several Work Units per hierarchy to avoid conflicts |
| `Originals/` | Yes, via Git LFS or Perforce |
| `.cache/`, `*.validationcache`, user files (`*.wsettings`) | No |
| Generated SoundBanks | No, unless the engine needs them checked in; build in CI instead |

Audiokinetic supports Perforce, Git and others through source-control plug-ins in the authoring tool. WwiseConsole generation has a `--no-source-control` option (seen in a community post), so CI does not need the plug-in.

Always record the Wwise version. Banks and the runtime SDK must come from the same version; the SoundBanksInfo output can differ across versions (a community question reports this).

## 3. WAAPI

WAAPI is the Wwise Authoring API. It runs inside the authoring application, so Wwise must be open (WwiseConsole can also host it for some operations; unverified).

Endpoints (from Audiokinetic's step-by-step WAAPI guide and community answers; defaults shown, confirm in Project > User Preferences):

| Transport | Default | Notes |
|---|---|---|
| WebSocket (WAMP) | `ws://localhost:8080/waapi` | Supports calls and subscriptions (topics). The WAMP port is a preference |
| HTTP | `http://localhost:8090/waapi` | POST with a JSON body. One call per request. Not usable for subscriptions (unverified) |

Setup: enable WAAPI in the user preferences, restart Wwise, and check the "Allowed Origins" preference (a staff answer lists `#unknown,#file` as the working value for scripts and local files). Only the first running Wwise instance gets the ports; others log a bind error.

HTTP request shape (as in the guide's cURL example):

    POST http://localhost:8090/waapi
    Content-Type: application/json
    {"uri": "ak.wwise.core.getInfo", "args": {}, "options": {}}

The reply is a JSON object. Errors carry a `uri` naming the error and a `message`. The `plugins/arcosian-audio/scripts/waapi.py` client sends exactly this.

Common calls (names from the WAAPI reference; verify argument shapes in the reference for your version):

| URI | Purpose |
|---|---|
| `ak.wwise.core.getInfo` | Version, platform, directories. First call to prove the connection |
| `ak.wwise.core.object.get` | Query objects with `from` (path, id, ofType), `transform`, and `options.return` |
| `ak.wwise.core.object.create` | Create an object under a parent (name, type, onNameConflict) |
| `ak.wwise.core.object.setProperty` / `setReference` | Change a property or a reference (for example output bus) |
| `ak.wwise.core.audio.import` | Import audio files into the project |
| `ak.wwise.core.project.save` | Save the project |
| `ak.wwise.core.soundbank.generate` | Generate SoundBanks (documented in the reference; check it exists in your version) |
| `ak.wwise.core.undo.beginGroup` / `endGroup` | Wrap a batch of edits as one undo step |

Guidelines:
1. Start with `getInfo`. If it fails, the cause is almost always the preferences, the port, or a second Wwise instance.
2. Wrap batch edits in an undo group so a bad run is one undo.
3. Read first (`object.get`), print what you are about to change, then write.
4. WAAPI has no authentication. Keep it on localhost. Never port-forward it.
5. Commit nothing that contains machine-specific paths from `getInfo`.

## 4. WwiseConsole and SoundBank generation

`WwiseConsole` is the command-line front end installed with the authoring tool (on Windows `WwiseConsole.exe`; the macOS name and location are unverified). Command: `generate-soundbank`.

Seen working in Audiokinetic community posts (verify against your version's reference):

    WwiseConsole generate-soundbank "E:/wwise-project/WwiseProject.wproj" --platform "Windows" --continue-on-error --verbose

| Flag | Meaning (from community use) |
|---|---|
| `--platform <name>` | Platform to generate (repeatable per platform) |
| `--language <name>` | Restrict to a language |
| `--root-output-path <dir>` | Root for generated output and the ProjectInfo files |
| `--output <dir>` | Output directory; one community report says it did not behave as expected, so test it |
| `--no-source-control` | Skip source-control integration |
| `--continue-on-error` | Keep going after errors |
| `--verbose` | List processed files |
| `--bank <name>` | Generate a named bank. Unverified (an older WwiseCLI used a similar flag) |

Other commands: `clear-audio-file-cache` (confirmed in a community answer). For the full list run `WwiseConsole --help` and `WwiseConsole generate-soundbank --help`.

Notes:
- User SoundBank settings (the dialog's choices) are normally ignored when generation is launched from the command line (community answer). Put the settings in the project's SoundBank settings so CI and the GUI agree.
- There is no known dry-run or "only changed banks" flag. Generate everything and diff by content hash.
- Use the same Wwise version in CI as the team's authoring version.
- In UE and other integrations, engine tools may call WwiseConsole for you.

CI procedure:
1. Install the matching Wwise authoring version on the runner (licence permitting; check the licence for build machines).
2. `WwiseConsole generate-soundbank <proj> --platform <each platform> --continue-on-error --verbose`.
3. Fail on non-zero exit, on any "error" line in output, and if `SoundbanksInfo` (JSON or XML) is missing.
4. Publish banks as build artefacts; the engine package step copies them.

## 5. Integrations

| Engine | Integration | Status (verify) |
|---|---|---|
| Unity | Wwise Unity integration, installed through the Wwise Launcher | Official from Audiokinetic |
| Unreal | Wwise Unreal integration | Official |
| Godot | `alessandrofama/wwise-godot-integration` (GDExtension wrapper; nodes AkEvent3D, AkEvent2D, AkBank, AkListener) | Community-originated. Audiokinetic has a blog post "What's New in Wwise 2024.1 for Godot". The newest release found in October 2026 was v2.0.4 for Wwise 2023.1 and Godot 4.2; the last push seen in an index was April 2024. Check releases for Godot 4.3 or later |
| Web | No first-party Wwise web runtime known | Unverified. Use FMOD or native Web Audio for web |
| Custom engine | Wwise SDK (C++), sample sound engine | Official |

Platform note: a Wwise licence is required for each platform a title ships on (from Audiokinetic's pricing statements).

## 6. Runtime API shape

1. Initialise memory manager, stream manager, sound engine, communication (optional, for profiling).
2. Load `Init.bnk`, then content banks (`AK::SoundEngine::LoadBank`).
3. Register game objects (`RegisterGameObj`), set positions (`SetPosition`), set the listener.
4. `PostEvent("Play_X", gameObjectId)`; set `SetSwitch`, `SetState`, `SetRTPCValue` as needed.
5. Call `RenderAudio()` each frame.
6. Unload banks, unregister objects on level exit.

Engine integrations wrap these calls; in Unity, `AkSoundEngine.PostEvent` and the AkEvent/AkBank components do it.

## 7. Licence tiers

From Audiokinetic's licensing blog and third-party listings (verify on audiokinetic.com/pricing):

| Tier | Total production budget | Notes |
|---|---|---|
| Indie | Under $250,000 | Free; full features; community support and pay-per-ticket support. The old 200-sound limit no longer applies, per a staff answer |
| Pro | $250,000 to $2M | Paid, per platform |
| Premium | Over $2M | Paid, per platform |
| Platinum | Bundle on top | Support bundle |

A licence is needed per platform shipped. Pricing and thresholds change; confirm the day you sign.

## 8. Verification status

| Item | Status |
|---|---|
| WAAPI ports 8080 and 8090, `/waapi`, JSON body with `uri` | Confirmed by Audiokinetic blog and community pages (2017 to 2019 era); not re-confirmed on a 2025 release |
| `generate-soundbank` flags beyond those in the table | Unverified |
| Godot integration status | Index data to April 2024; newer unknown |
| Licence thresholds | Blog and third-party listing |
