---
name: audio-middleware
description: Procedures for FMOD Studio and Wwise on any game, plus when engine-native audio (Godot buses and interactive streams, Unity AudioMixer, Web Audio) is enough. Covers events and banks, WAAPI and WwiseConsole build automation, Godot and Unity hookup, licences, bank size, loudness and platform formats. Use when asked "should we use FMOD or Wwise", "build banks in CI", "WAAPI script", "adaptive music setup".
---

# Audio middleware

## When to use

Use this skill when the game needs more audio than the engine's own mixer gives, or when someone is deciding whether it does. Typical triggers: a sound designer wants to iterate without code changes; music must react to gameplay; a console port needs platform codecs; banks must be built in CI; a licence question comes up.

Do not use it for creative direction (what the audio should feel like) or for producing the sound files. Those belong to `/arcosian:audio-direction` and `/arcosian:audio-production`. This skill starts when the design says "events, parameters, banks" and ends when banks are built, hooked up and measured.

Default stance: start native. Add middleware only when a trigger in the decision table fires, and add it behind a thin wrapper so game code never names the middleware.

## Decision table

| Question | Answer | Then |
|---|---|---|
| Is a dedicated sound designer or composer iterating weekly? | Yes | Middleware likely pays off |
| More than about 50 to 100 events with shared behaviour? | Yes | Middleware |
| Interactive music with many states and transition rules? | Yes | Middleware, or Godot 4.3 interactive streams if 2 to 4 states |
| Web build? | Yes | Native Web Audio first; see `engine-native-audio.md` |
| Console target? | Yes | Middleware platform packages usually needed; check console programme access via `/arcosian:console-pathway` |
| Team under 3 and no audio specialist? | Yes | Native |
| Godot project, want middleware? | FMOD (community extension) or Wwise (community-originated integration) | Check version support first; no official FMOD integration found |
| Unity or Unreal project, want middleware? | FMOD or Wwise, both official | Pick by team skill, then licence |
| Budget | FMOD Indie under $600k (free or $2,000, verify); Wwise Indie under $250k (free) | See licence checklist |

Full table with tie-breakers: `references/engine-native-audio.md`.

## Recipes

### Recipe 1: Create an event and build banks (FMOD)

1. Confirm the Studio version and record it in the repo (`AUDIO_TOOLCHAIN.md`).
2. Create the project next to the game repo or inside `audio/`. Commit the `.fspro` and `Metadata/` and `Assets/`; ignore `Build/` and caches. Track audio with Git LFS.
3. Import the WAV files. Create an event `event:/SFX/Pickup`. Add a multi-instrument for variation, randomise pitch plus or minus 2 semitones and volume plus or minus 1 dB (defaults).
4. Assign the event to a bank (events are not added automatically).
5. Route the event to the `SFX` bus. Add a VCA `SFX` for the player slider.
6. Set per-platform encoding and sample rate in the Platform settings.
7. Build. Confirm `Master.bank`, `Master.strings.bank` and the content banks exist per platform.
8. Copy banks to the engine's streaming folder (script it).
9. In game: load the master bank, then the strings bank, then content banks; play by path.
10. Check in the profiler: voice count, memory, and the event stops cleanly.

### Recipe 2: Create an event and build banks (Wwise)

1. Record the Wwise version. Create the project with several Work Units per hierarchy.
2. Import audio. Build an Actor-Mixer or Random Container under the Actor-Mixer Hierarchy, route to a bus.
3. Create the event `Play_SFX_Pickup` with a Play action targeting the container.
4. Create or edit a SoundBank (or use auto-defined banks in newer versions; verify) and add the event.
5. Set conversion settings per platform.
6. Generate SoundBanks in the GUI once, then reproduce from the command line with WwiseConsole (see recipe 5).
7. In game: load `Init.bnk` first, then the content bank; register the game object; post the event by name.
8. Check in the Profiler (voices, memory, streaming, bus meters).

Optional WAAPI check before scripting changes:

    python3 ${CLAUDE_PLUGIN_ROOT}/scripts/waapi.py info
    python3 ${CLAUDE_PLUGIN_ROOT}/scripts/waapi.py call ak.wwise.core.object.get --args '{"from":{"ofType":["Event"]}}' --options '{"return":["name","path"]}'

The script is not verified against a running Wwise; if it errors, read `references/wwise.md` section 3 and check the WAAPI preferences.

### Recipe 3: Hook into Godot

1. Decide native or middleware using the decision table. For up to about 4 music states and simple SFX, stay native (`AudioStreamInteractive`, `AudioStreamSynchronized`, `AudioStreamRandomizer`, buses).
2. Native: create the bus layout `Master > Music, SFX, UI, Voice`; add an autoload `Audio` singleton with `play_sfx(id)`, `set_music_state(name)`, and `set_volume(bus, linear)` (use `linear_to_db`).
3. FMOD: install `utopia-rise/fmod-gdextension` matching your Godot and FMOD versions (read its releases and docs first). Put banks under a folder the extension loads. Use its emitter and listener nodes, or call through the singleton from the wrapper.
4. Wwise: install the Wwise Godot integration for your Wwise version; confirm Godot 4.x support in its releases. Generate banks to the folder the integration expects.
5. Run an export test on every target platform. GDExtension libraries must exist for each export platform; web is likely unsupported by community extensions (verify).
6. Keep the wrapper API the same in all three cases so a swap changes one file.

### Recipe 4: Hook into Unity

1. Native: `AudioMixer` with groups Music, SFX, UI, Voice; expose volume parameters; snapshots for Normal, Paused, Dialogue. Use `PlayScheduled` for beat-aligned music.
2. FMOD: import FMOD for Unity (official). Set the project path or bank folder in FMOD settings. Use `StudioEventEmitter` for scene sounds and `RuntimeManager.PlayOneShot` for fire-and-forget. Set parameters with `setParameterByName`.
3. Wwise: install through the Wwise Launcher (official integration). Generate banks to the project's `StreamingAssets` path as configured by the integration. Post events with `AkSoundEngine.PostEvent` or AkEvent components.
4. Add build steps that copy banks into the player build. Console builds need platform packages from the vendor portals after licence access.
5. Test an IL2CPP player build early; native plug-ins sometimes fail only there.

### Recipe 5: Bank builds in CI

1. Pin tool versions: the same FMOD Studio or Wwise authoring version as the team uses. Record it.
2. Cache the installer on the runner. Check the licence terms for build machines first.
3. FMOD: run `fmodstudiocl -build <project>.fspro`. The flags beyond `-build` are unverified here; run `fmodstudiocl -help` once and put the real flags in the script. Fail on non-zero exit and on missing `Master.bank` or `Master.strings.bank`.
4. Wwise: run `WwiseConsole generate-soundbank <project>.wproj --platform <name> --continue-on-error --verbose --no-source-control`, once per platform. Check the output for error lines and for the SoundBanksInfo file. Confirm `--output` and `--root-output-path` behaviour on your version.
5. Compare bank sizes with the previous build. Fail on growth above 10% (default) unless a note explains it.
6. Upload banks as artefacts. The engine packaging step consumes them.
7. Never let CI upload a build to a store; store uploads are human-approved (see `/arcosian:ship`).

## Worked example

Game: a Godot 4.3 top-down shooter for PC and Switch, 6 people, one part-time sound designer, 150 events, layered combat music with 3 intensity levels, budget $300k.

1. Decision. Layered music with 3 levels and 150 events fits native Godot 4.3: `AudioStreamSynchronized` with three stems, volumes tied to an `intensity` variable. A Switch port may need a platform codec and the studio wants the designer to iterate without code. Wwise Indie is free under $250k but the budget is $300k, so Wwise Pro applies; FMOD Indie applies under $600k. The only FMOD Godot route is the community extension.
2. Choice. Stay native for the first milestone (zero cost). Define the wrapper `Audio.play("sfx.pickup")` and the intensity API now. Re-decide at milestone 3 if the designer is blocked, with a one-day spike on the FMOD GDExtension on Switch (the extension's console support is unverified).
3. Mix. Buses Music, SFX, UI, Voice; sidechain Voice to Music: 4 dB, attack 30 ms, release 500 ms.
4. Music at 100 BPM: beat 0.6 s, bar 2.4 s. Combat start on the next beat, combat end after a 5 s hold, fade 1 bar.
5. Memory: stems Vorbis 128 kbps, 3 x 2 min = 5.8 MB on disk, streamed.
6. Loudness: 30 minute captures, console profile target -24 LUFS plus or minus 2 and handheld -18 LUFS plus or minus 2 (see `references/adaptive-music-and-mix.md`).
7. Record the decision and the review date in the design contract notes via `/arcosian:audio-direction`.

## Checklists

### Licence checklist

- [ ] Development budget and revenue for the game are known, with funding included, and compared with the tier thresholds today.
- [ ] FMOD: tier chosen (Indie, Basic, Premium); the $2,000 Indie fee condition read on the page; logo credit and profile registration done for Indie.
- [ ] Wwise: tier chosen (Indie, Pro, Premium); a licence for each shipped platform.
- [ ] Console platform terms and platform packages confirmed with the vendor.
- [ ] CI machines allowed to run the authoring tool.
- [ ] Community integrations (Godot) have an open-source licence compatible with the game and the middleware EULA.
- [ ] Decision recorded with date and source URL.

### Bank size checklist

- [ ] Banks split by level or feature, plus one small always-loaded bank.
- [ ] No bank holds both streamed music and in-memory SFX.
- [ ] Per-platform audio RAM budget written down (see `references/adaptive-music-and-mix.md`).
- [ ] Total bank size per platform compared with the previous build.
- [ ] Unused assets and events stripped (FMOD: unassigned events; Wwise: unused media report).
- [ ] Localised voice in separate language banks.

### Platform formats checklist

- [ ] Per-platform conversion set: music Vorbis or Opus, short SFX ADPCM or PCM, voice mono.
- [ ] Sample rates chosen per sound class (22.05 kHz low SFX, 44.1 or 48 kHz music).
- [ ] Web: codec fallback tested on Safari, Chrome, Firefox; first-input audio unlock works.
- [ ] Console: platform codec and hardware decoder choices confirmed in the console SDK docs.
- [ ] Loudness measured per platform profile.

## Failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| Event does not play in game | Strings bank or Init bank not loaded first, or event not in a bank | Load master/Init first; assign events to banks; rebuild |
| Banks empty (FMOD) | Events not assigned to banks | Assign and rebuild |
| Banks built in GUI but not in CI (Wwise) | User SoundBank settings ignored on command line | Set options in project SoundBank settings |
| Version mismatch crash or silent audio | Banks from a different version than runtime | Rebuild with the matching version |
| WAAPI call fails | WAAPI disabled, wrong port, second Wwise instance, allowed origins | Check preferences; read `references/wwise.md` |
| Music restarts on every state change | State change retriggers the event | Use parameters or transition rules, not new events |
| Clicks at transitions | Cut on non-zero crossing or off-beat | Fade 10 to 50 ms or transition on a beat |
| Memory spike on level load | Long clips decompressed in RAM | Stream music; compress in memory |
| Web has no sound | Context suspended until input | Resume in first gesture handler |
| Community extension breaks after an engine upgrade | Version pinning missing | Pin engine, extension and middleware versions together |

## Security

- WAAPI and the FMOD scripting terminal accept commands over a local socket with no authentication. Keep them on localhost, turn the FMOD script server off when idle, never forward the ports.
- `waapi.py` refuses non-localhost URLs unless `--allow-remote` is given. Do not use that flag unless you control the network.
- Do not run scripts or WAAPI payloads copied from issues, forums or downloads without reading them.
- Install middleware only from the vendor's own download pages. Community integrations are third-party code: read the licence and pin a release.
- No licence keys, vendor account tokens or project passwords in the repo or in this skill's output.
- Store uploads and community posts are human-approved.

## Reference library

| File | Contents | Read when |
|---|---|---|
| `references/fmod.md` | FMOD concepts, project layout, bank builds, scripting, integrations, licence | Using or evaluating FMOD |
| `references/wwise.md` | Wwise concepts, WAAPI, WwiseConsole, integrations, licence | Using or evaluating Wwise, or writing build automation |
| `references/engine-native-audio.md` | Godot, Unity, web native audio and the decision table | Deciding whether middleware is needed |
| `references/adaptive-music-and-mix.md` | Interactive music, snapshots, ducking, voices, loudness, memory, formats | Designing music and mix, or setting budgets |
| `${CLAUDE_PLUGIN_ROOT}/scripts/waapi.py` | Minimal WAAPI HTTP client with `--selftest` | Checking a Wwise connection or scripting one call |

## Volatile facts (as of Oct 2026 - verify)

- FMOD licence tiers and thresholds (Indie under $600k, Basic to $1.8M, Premium above). Source: https://www.fmod.com/licensing
- Wwise tiers (Indie under $250k, Pro to $2M, Premium above) and per-platform licence. Source: https://www.audiokinetic.com/en/wwise/pricing/ and https://www.audiokinetic.com/en/blog/wwise-licensing-and-pricing-philosophy/
- WAAPI defaults (HTTP 8090, WAMP 8080, path `/waapi`). Source: https://www.audiokinetic.com/en/blog/stepbystep-waapi-example/
- WwiseConsole `generate-soundbank` flags. Source: https://www.audiokinetic.com/en/public-library/ (search "generate-soundbank")
- `fmodstudiocl` flags and Studio scripting. Source: https://www.fmod.com/docs/2.03/studio/ (unverified)
- Godot FMOD community extension status. Source: https://github.com/utopia-rise/fmod-gdextension
- Wwise Godot integration status. Source: https://github.com/alessandrofama/wwise-godot-integration
- Godot 4.3 interactive audio streams. Source: https://docs.godotengine.org/en/4.3/classes/class_audiostreaminteractive.html
- PlayStation loudness target. Source: https://designingsound.org/2015/06/04/sulpha-the-new-ps4-mastering-suit
- No official FMOD or Wwise MCP server was found (community servers exist only), so this plugin ships no `.mcp.json`.

## Related skills

- `/arcosian:audio-direction`: what the audio should be, music model choice, loudness philosophy.
- `/arcosian:audio-production`: producing and reviewing the sound files and naming.
- `/arcosian:ai-audio-pipeline`: generated audio and its provenance.
- `/arcosian:engine-godot` and `/arcosian:engine-unity`: engine specifics.
- `/arcosian:platform-targets`: input, performance tiers and platform UX.
- `/arcosian:console-pathway`: console programmes and certification.
- `/arcosian:optimize`: performance work when audio CPU or memory is the bottleneck.
