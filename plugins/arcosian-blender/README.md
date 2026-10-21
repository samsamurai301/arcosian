# arcosian-blender

Adapter plugin for the `arcosian` core plugin. It lets Claude drive a running Blender through the community `blender-mcp` bridge (ahujasid, MIT) for asset cleanup, previews and export.

Requires the core plugin `arcosian` (declared as a dependency).

## What you get

- Skill `blender-bridge`: cleanup recipes for mobile (decimate, UV, bake, glTF export), the gltfpack and KTX2 stage, preview renders for the critic agent, and a security checklist.
- `.mcp.json` registers one server, `blender`, launched with `uvx blender-mcp==2.0.0` (pinned) and with telemetry disabled by default.

## Setup

1. Install Blender (the bridge needs 3.0+) and `uv`.
2. Install the Blender add-on from the project's repository (link below) and, in Blender, start its server from the side panel.
3. Restart Claude Code, run `/mcp`, and confirm `blender` is connected while Blender is open.
4. Launch command confirmed (Oct 2026): `uvx blender-mcp==2.0.0` runs PyPI package `blender-mcp` (2.0.0), whose repository is now `ahujasid/mcp-for-blender`; its README names `uvx mcp-for-blender` as the new command and says `uvx blender-mcp` keeps working. The server talks to the add-on over `BLENDER_HOST`/`BLENDER_PORT` (default `localhost:9876`).

## Tools the bridge exposes (per the research notes)

`get_scene_info`, `look` (viewport, camera, multi-angle sheets, animation frames, wireframe), `execute_blender_code`, `search_assets` / `import_asset` (Poly Haven, Sketchfab, Poly Pizza), `generate_3d` (Tripo, Hunyuan3D, Hyper3D Rodin, Meshy). Tool names can change between releases; list them with `/mcp` first.

## When not to use the bridge

The socket server is single-session, GUI-bound and unauthenticated. For batch production (hundreds of assets, CI) write plain headless Blender scripts and gltfpack calls instead; use the bridge for exploration, one-off fixes and preview renders.

## What this plugin runs, sends and fetches

- **Runs:** `uvx blender-mcp==2.0.0` (exact version) with its telemetry switched off (`DISABLE_TELEMETRY=true`); it drives a Blender on your machine through the add-on's localhost socket.
- **Fetches:** the `blender-mcp` package from PyPI on first start.
- **Sends:** nothing by itself. The asset and generation tools contact the services they name (Poly Haven, Sketchfab, Poly Pizza, Tripo, Hunyuan3D, Hyper3D Rodin, Meshy) only when you enable and use them in the add-on.

## Security (read before enabling)

- **Arbitrary Python.** `execute_blender_code` runs any Python in Blender with your user's rights: files, network, subprocesses. Treat every call as code execution.
- **No authentication or encryption** on the socket. Keep it bound to localhost, never forward the port, never run on a shared machine.
- **Safe mode.** The add-on has an optional safe mode that blocks file, network and process access; turn it on unless a task needs those.
- **Telemetry.** Anonymous telemetry is on by default upstream; this plugin sets `DISABLE_TELEMETRY=true` in `.mcp.json`, which the upstream README documents as turning telemetry off entirely, including the minimal anonymous usage record.
- **Third-party assets.** Imported models carry their own licences; register them with provenance in the studio manifest.
- Do not open untrusted .blend files in the bridged session: they can carry scripts.

## Typical session

1. Open the asset in Blender and start the add-on server.
2. Ask the studio to run the `blender-bridge` skill on it with a stated budget (role, triangle target, texture size).
3. Claude inspects, cleans, bakes and exports, then renders previews to `.gamestudio/evidence/`.
4. The critic agent reviews the previews; the asset is registered through the core gateway with `manifest_update`.
5. Close the add-on server when finished so the socket is not left open.

## Volatile facts (as of Oct 2026 - verify)

- Repository, star count, version numbers and tool list move; directory mirrors disagree. Source: https://github.com/ahujasid/blender-mcp
- Meshy remesh options (quad or triangle, 100-300k target) and credit costs. Source: https://docs.meshy.ai/en/api/remesh
- gltfpack features (quantize, merge, simplify, KTX2 via BasisU). Source: https://dyn.manpages.debian.org/trixie/gltfpack/gltfpack.1.en.html

## License

MIT.
