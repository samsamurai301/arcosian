# Privacy and data flows

Arcosian runs on your machine inside Claude Code. The plugins send nothing to their authors: there is no telemetry, analytics or crash reporting.

## What can leave your machine

Only the parts you set up send anything, and only to the destinations below.

| Part | What it sends | Where | When |
|---|---|---|---|
| `studio-gateway` (core) | The prompt, reference images and settings for the asset or audio you ask for | The providers whose API keys you add: Google (Gemini), OpenAI, Recraft, fal, Tripo, Meshy, ElevenLabs, Stability AI | Only for a generation call, only with a key you provided, and only within the budget cap. Without keys it writes local placeholders and sends nothing |
| Adapter MCP servers | What the tool Claude calls needs | That server's vendor: PixelLab, Meshy, ElevenLabs, Scenario, RevenueCat, Firebase (Google), Adjust, Figma (`arcosian-art`), GitHub and Sentry (`arcosian-community`). The Godot, Unity CLI and Blender servers stay on your machine. The full list with sources is in [docs/CONNECTORS.md](docs/CONNECTORS.md) | Only when that adapter is installed and the server is enabled |
| Package launchers | Download requests | npm (`npx`) and PyPI (`uvx`), for the exact-version packages the adapter MCP servers run | The first time Claude Code starts those servers |
| C# language server (`arcosian-unity`) | Package restore requests | NuGet, for a small generated project | In engine-free mode, when an asmdef changes |
| CI templates | Your project and the secrets you store in CI | Your CI provider and the stores you configure | Only after you copy a template into your repository and push |

Each provider's own privacy policy and terms cover what you send it, including the rights to generated assets. The gateway records provenance and licence notes for every asset so you can check them before shipping.

## What stays on your machine

- **API keys**: Claude Code stores them as sensitive plugin options in its secure storage. They are passed to the gateway as environment variables, never written to project files, and the hooks block reading signing keys and `.env` files.
- **Project state**: `.gamestudio/` in your project holds design documents, the feature list, the budget ledger and the asset manifest.
- **Project map, what-if results and the dashboard**: `gs.py map`, `gs.py whatif` and `gs.py dashboard` read and write only inside `.gamestudio/`; the dashboard is one offline HTML file that loads nothing from the network. The art, levels and audio adapters' scripts read and write only the files you name (`waapi.py` talks to Wwise on localhost unless you pass `--allow-remote`).
- **Plugin data**: `~/.claude/plugins/data/<plugin>/` holds the chosen Python command, a copy of the Godot plugin's options, language-server logs and the generated C# project.

## Questions

Open an issue on [GitHub](https://github.com/samsamurai301/arcosian/issues). For security problems, follow [SECURITY.md](SECURITY.md).
