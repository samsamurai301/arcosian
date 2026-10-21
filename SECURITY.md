# Security policy

## Report a vulnerability

Report it privately on GitHub: open the repository's **Security** tab and choose **Report a vulnerability**. Please do not open a public issue for a security problem. Include the plugin and version, what an attacker can do, and the steps to reproduce.

## Scope

- **Hooks**: the release guard (store submission asks first), the secret guard (reading keystores, `.p12`, `.p8`, `.mobileprovision` and `.env` files is denied in Bash and PowerShell), the recursive-delete guard and the five-gate checks.
- **`studio-gateway`**: spending caps, API-key handling, provider calls and the files it writes into a project.
- **Language-server bridges**: `gdscript-bridge.mjs` and `unity-csharp-lsp.mjs`, including the processes they start and stop.
- **MCP configurations**: the pinned packages and remote endpoints the adapters register.
- **CI templates**: how they handle signing secrets and store credentials.

The third-party MCP servers, engines and vendor APIs the adapters connect to are out of scope; report problems in them to their maintainers.

## Built-in protections

- API keys are sensitive plugin options, never files; the gateway redacts keys from its logs.
- Generation calls are capped per project and per call; without keys the gateway runs in mock mode.
- Every package an adapter runs through `npx` or `uvx` is pinned to an exact version.
- Hooks fail open on their own internal errors but never on an explicit deny rule.
- Store submission and promotion always need a human.

## Supported versions

Fixes go into the latest release.
