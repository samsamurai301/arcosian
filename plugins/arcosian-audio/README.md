# arcosian-audio

Adapter plugin for the `arcosian` core plugin. It adds one skill, `audio-middleware`, for FMOD Studio and Wwise on any game, for deciding when engine-native audio is enough, and for build automation. Requires the core plugin `arcosian` (declared as a dependency).

## What you get

- Skill `audio-middleware`: decision table, recipes (events and banks, Godot and Unity hookup, bank builds in CI), a worked example, licence / bank size / platform format checklists, failure modes, security notes.
- References: `fmod.md`, `wwise.md`, `engine-native-audio.md`, `adaptive-music-and-mix.md`.
- Script `scripts/waapi.py`: a minimal WAAPI client over HTTP (`info`, `call <uri> [--args JSON] [--options JSON]`, `--url`, `--allow-remote`, `--selftest`).
- No `.mcp.json`. I searched for an official MCP server from Audiokinetic (Wwise) or Firelight Technologies (FMOD) in October 2026 and found none; only community servers exist, and they are not shipped here.

## Setup

1. Install the plugin alongside `arcosian`.
2. Optional, for Wwise automation: open Wwise, enable WAAPI in the user preferences, restart, then run `python3 scripts/waapi.py info`.
3. Run `python3 scripts/waapi.py --selftest` to check the script offline.

## What this plugin runs, sends and fetches

- `waapi.py` sends one HTTP POST to the URL you give (default `http://127.0.0.1:8090/waapi`). It refuses any non-localhost URL unless you pass `--allow-remote`. It sends nothing else and reads no files.
- The skill describes commands (`fmodstudiocl`, `WwiseConsole`) for you or the agent to run on your machine; the plugin does not run them itself.
- No telemetry, no accounts, no downloads.

## Security

- WAAPI and the FMOD Studio scripting terminal have no authentication. Keep them on localhost.
- Read any script before running it. Do not run payloads copied from forums.
- Community integrations are third-party code; pin versions and read their licences.
- Store uploads and community posts are always human-approved.

## Typical session

1. Ask "do we need FMOD or Wwise?" The skill walks the decision table and records the answer.
2. Ask for a bank build recipe for your engine; the skill gives the steps and the CI commands.
3. Ask for a mix and music plan; the skill applies the numbers in `adaptive-music-and-mix.md` to your tempo and platforms.

## Verified and not verified

Not verified against a running Wwise: `waapi.py`. Its self-test passes against a local mock server only; the endpoint and request shape come from Audiokinetic's published WAAPI example. Audiokinetic and FMOD documentation pages could not be fetched directly in October 2026, so these are unverified or only confirmed through third-party summaries: `fmodstudiocl` flags, `WwiseConsole generate-soundbank` flags beyond the common ones, current Godot integration versions, and the exact licence conditions. Each is labelled in the references.

## Volatile facts (as of Oct 2026 - verify)

- FMOD licence tiers. Source: https://www.fmod.com/licensing
- Wwise licence tiers. Source: https://www.audiokinetic.com/en/blog/wwise-licensing-and-pricing-philosophy/
- WAAPI ports. Source: https://www.audiokinetic.com/en/blog/stepbystep-waapi-example/
- Godot community integrations. Sources: https://github.com/utopia-rise/fmod-gdextension and https://github.com/alessandrofama/wwise-godot-integration

## License

MIT.
