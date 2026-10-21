# Claude Code Plugin Architecture and Agent-Orchestration Best Practices (state as of 2026-10-18)

Scope note for the report writer: nearly all findings below come from official Anthropic docs (code.claude.com/docs, platform.claude.com/docs) and Anthropic engineering posts, fetched on 2026-10-18. The docs cite Claude Code versions up to roughly v2.1.296, so many fields carry "requires v2.1.2xx+" notes. Items marked `experimental`, "research preview", or "early access" may still change. Game-dev ecosystem findings come from third-party directories and are much weaker evidence.

---

## 1. Plugin structure and packaging (manifest, layout, marketplaces, install, versioning, distribution, component types)

### Takeaway
A Claude Code plugin is a directory with an optional `.claude-plugin/plugin.json` manifest. It can bundle skills, commands, agents, hooks, MCP servers, LSP servers, output styles, workflows (JS orchestration scripts), `bin/` executables, default settings, and the experimental themes, monitors and evals. Plugins are distributed through git, npm, archive or command-backed `marketplace.json` catalogs. You get versions pinned by `version` or by commit SHA, dependency resolution, userConfig with keychain-stored secrets, and `claude plugin validate` and `claude plugin eval` for CI.

### Cited Findings

**Manifest basics**
- The manifest is optional. It lives at `.claude-plugin/plugin.json`. Every other file (`skills/`, `commands/`, `hooks/`, and so on) goes at the plugin root, not inside `.claude-plugin/`. Without a manifest, Claude Code loads the components it finds in the standard layout. — [Plugin manifest reference](https://code.claude.com/docs/en/plugins-reference)
- `name` is the only required field. Use kebab-case. Every component is namespaced under it, so agent `reviewer` in plugin `deploy-tools` becomes `deploy-tools:reviewer`. — [Plugin manifest reference](https://code.claude.com/docs/en/plugins-reference)
- Top-level fields: `$schema`, `name`, `displayName`, `version`, `description`, `author` {name, email, url}, `homepage`, `repository`, `license`, `keywords`, `metadata` (free-form, not read), `icon`, `documentationUrl`, `supportUrl`, `privacyPolicyUrl`, `termsOfServiceUrl` (the last five are directory-listing fields), `defaultEnabled`, `dependencies`, `settings`, `userConfig`, `types` (a `.d.ts` file for mods), `channels`, `skills`, `commands`, `agents`, `hooks`, `mcpServers`, `lspServers`, `outputStyles`, `workflows`, and `experimental` {`themes`, `monitors`, `evals`}. — [Plugin manifest reference](https://code.claude.com/docs/en/plugins-reference)
- Unknown top-level keys are stripped with a validator warning. Unknown keys inside `userConfig`, `channels`, `lspServers` or `monitors` entries are errors, and the plugin fails to load. — [Plugin manifest reference](https://code.claude.com/docs/en/plugins-reference)
- Reserved names: names starting with `claude-`, `anthropic-` or `cc-plugin-`, or putting "official" next to claude/anthropic, are errors. Using `claude` as a whole word elsewhere is a warning. — [Plugin manifest reference](https://code.claude.com/docs/en/plugins-reference)
- `version` is a free-form string, not checked against semver. "Setting it keeps users on that version until you change it." — [Plugin manifest reference](https://code.claude.com/docs/en/plugins-reference)
- `dependencies` entries can be `"name"`, `"name@marketplace"`, or `{name, marketplace, version}`. A separate dependencies page covers version ranges such as `^1.2`. — [Plugin manifest reference](https://code.claude.com/docs/en/plugins-reference); [docs index](https://code.claude.com/docs/llms.txt)
- Plugin `settings` (or a root `settings.json`) applies only `agent` and `subagentStatusLine`. Other keys are dropped. — [Plugin manifest reference](https://code.claude.com/docs/en/plugins-reference)

**Standard layout (defaults)**
- `.claude-plugin/plugin.json`; `skills/<name>/SKILL.md`; `commands/*.md` ("Prefer `skills/` for new plugins"); `agents/*.md` (subfolders become part of the agent name); `hooks/hooks.json`; `.mcp.json`; `.lsp.json`; `output-styles/`; `workflows/*.js`; `themes/`; `monitors/monitors.json`; `bin/` (on the Bash tool's PATH while enabled); `settings.json`. A `CLAUDE.md` at the plugin root is NOT loaded, and the validator warns about it. Put instructions in a skill instead. — [Plugin manifest reference](https://code.claude.com/docs/en/plugins-reference)
- claude.ai and Cowork won't install a plugin that has a top-level `bin/` directory. — [Plugin manifest reference](https://code.claude.com/docs/en/plugins-reference)
- Path rules: every component path must start with `./` and resolve inside the plugin root (`..` is rejected). `commands`, `agents`, `outputStyles`, `workflows`, themes and monitors REPLACE the default folder. `skills` ADDS to it. `hooks`, `mcpServers` and `lspServers` MERGE with the default file. — [Plugin manifest reference](https://code.claude.com/docs/en/plugins-reference)

**Environment variables**
- `${CLAUDE_PLUGIN_ROOT}` is the plugin's installed-version directory. It changes on update, so don't write state there. `${CLAUDE_PLUGIN_DATA}` is `~/.claude/plugins/data/<id>/`, persists across updates, and is deleted on final uninstall unless you pass `--keep-data`. `${CLAUDE_PROJECT_DIR}` is the project root. — [Plugin manifest reference](https://code.claude.com/docs/en/plugins-reference)
- These variables are NOT in the environment of the Bash tool, in the main session or in subagents. In skill and agent Markdown, write the `${...}` reference and Claude Code substitutes it inline. — [Plugin manifest reference](https://code.claude.com/docs/en/plugins-reference)

**userConfig and secrets**
- `userConfig` options take `type` (string/number/boolean/directory/file), `title`, `description`, `required`, `default`, `options` (v2.1.271+), `multiple`, `sensitive`, `min`/`max`. Sensitive values go to the platform's secure credential store. Non-sensitive values go to `pluginConfigs` in settings.json. — [Plugin manifest reference](https://code.claude.com/docs/en/plugins-reference)
- How saved values reach components:
  - `${user_config.KEY}` is substituted in MCP and LSP server config, exec-form hook `args`, and skill and agent content. Sensitive values become a placeholder in skill and agent content.
  - Hooks also receive every option as `CLAUDE_PLUGIN_OPTION_<KEY>` in their environment.
  - Shell-form hooks, monitor commands and MCP `headersHelper` reject `${user_config.*}`. Monitors don't get option env vars at all.

  — [Plugin manifest reference](https://code.claude.com/docs/en/plugins-reference)

**Component specifics**
- MCP servers:
  - `mcpServers` accepts a `.json` path, a `.mcpb`/`.dxt` bundle path or https URL (extracted into `.mcpb-cache/`), or an inline map.
  - stdio servers resolve `${...}` in `command`, `args` and `env`.
  - http/sse/ws servers resolve `${...}` in `url`, `headers` and `headersHelper`.
  - `claude plugin validate` (v2.1.281+) flags `http://` URLs to non-loopback hosts and header values that look like literal credentials.

  — [Plugin manifest reference](https://code.claude.com/docs/en/plugins-reference)
- LSP servers: strict config with `command` and `extensionToLanguage` (required), plus `args`, `transport`, `env`, `initializationOptions`, `settings`, `workspaceFolder`, timeouts, `restartOnCrash`, `maxRestarts`, and `diagnostics` (default true, which pushes diagnostics into context after edits). — [Plugin manifest reference](https://code.claude.com/docs/en/plugins-reference)
- Monitors (experimental): `{name, command, description, when}`, where `when` is `"always"` or `"on-skill-invoke:<skill>"`. Each one is a persistent background shell process whose output reaches the session. Monitors run only in interactive sessions, and not on Bedrock, Google Cloud's Agent Platform or Foundry. — [Plugin manifest reference](https://code.claude.com/docs/en/plugins-reference)
- Commands can also be declared as an object map with `source` or `content`, plus `description`, `argumentHint`, `model` and `allowedTools`. — [Plugin manifest reference](https://code.claude.com/docs/en/plugins-reference)
- Channels: a channel binds to one of the plugin's MCP servers. It lets the server push events (CI results, chat messages, monitoring events) into a running session. — [Plugin manifest reference](https://code.claude.com/docs/en/plugins-reference); [docs index (channels)](https://code.claude.com/docs/llms.txt)
- Mods: a newer extension type with its own docs section (overview, create, reference, interface, events, API, test). The `types` manifest field points to a `.d.ts` for mod state. — [Plugin manifest reference](https://code.claude.com/docs/en/plugins-reference); [docs index](https://code.claude.com/docs/llms.txt)
- Workflows in plugins: put the script in `workflows/`. It runs namespaced, e.g. `/acme-tools:release-audit` for `meta.name: 'release-audit'`. — [Workflows](https://code.claude.com/docs/en/workflows)

**Marketplaces**
- The catalog file is `.claude-plugin/marketplace.json`. Required fields: `name`, `owner`, `plugins`. Optional: `description`, `version`, `metadata.pluginRoot`, `forceRemoveDeletedPlugins`, `allowCrossMarketplaceDependenciesOn`, `renames`. — [Marketplace reference](https://code.claude.com/docs/en/plugins/marketplace-reference)
- Plugin entry fields: `name`, `source` (required), `description`, `version`, `category`, `tags`, `strict` (default true), `relevance`, `dependencies`, `defaultEnabled`, `displayName`, `metadata`, `headers`, `headersHelper`. An entry also accepts any plugin.json field. — [Marketplace reference](https://code.claude.com/docs/en/plugins/marketplace-reference)
- Plugin source types:
  - relative path (`./plugins/x`)
  - `github` {repo, ref, sha}
  - `url` (any git repo) {url, ref, sha}
  - `git-subdir` {url, path, ref, sha}, a sparse partial clone that suits monorepos
  - `npm` {package, version, registry}, with install scripts never run
  - `archive` {url, sha256}, v2.1.224+
  - `command` {command, timeout, mode: copy|link}, v2.1.229+

  — [Marketplace reference](https://code.claude.com/docs/en/plugins/marketplace-reference)
- Pinning: `sha` takes a full 40-character commit and wins over `ref`. `version` in plugin.json overrides the entry's `version`. — [Marketplace reference](https://code.claude.com/docs/en/plugins/marketplace-reference)
- Team distribution: declare `extraKnownMarketplaces` in settings. Admins can lock sources down with `strictKnownMarketplaces` (allowlist; supports `owner/*`, `hostPattern`, `pathPattern`) and `blockedMarketplaces`. — [Marketplace reference](https://code.claude.com/docs/en/plugins/marketplace-reference)
- Install flow: `/plugin marketplace add <owner>/<repo>`, then `/plugin install <plugin>@<marketplace-name>`. The marketplace name is the `name` field in marketplace.json. — [Anthropic's marketplaces](https://code.claude.com/docs/en/plugins/anthropic-marketplaces.md)
- Anthropic's three general marketplaces:

  | Marketplace name | Repository | How you get it |
  |---|---|---|
  | `claude-plugins-official` | anthropics/claude-plugins-official | Auto-added on first interactive start |
  | `claude-community` | anthropics/claude-plugins-community | Third-party plugins that authors submitted to Anthropic; add manually |
  | `claude-code-plugins` | anthropics/claude-code | Demo plugins; add manually |

  There are also topic marketplaces such as `anthropics/skills` and `anthropics/knowledge-work-plugins`. Anthropic's claude.ai directory is separate and reaches Claude Code through account sync. — [Anthropic's marketplaces](https://code.claude.com/docs/en/plugins/anthropic-marketplaces.md)
- Anthropic doesn't review third-party marketplaces. — [Anthropic's marketplaces](https://code.claude.com/docs/en/plugins/anthropic-marketplaces.md)

**Skills (the main way to carry knowledge)**
- A skill is a directory with `SKILL.md` (YAML frontmatter plus body) and optional supporting files: reference docs that load when needed, and scripts that are executed rather than loaded. Skills follow the open Agent Skills standard (agentskills.io) with Claude Code extensions. — [Skills](https://code.claude.com/docs/en/skills)
- Frontmatter fields: `name`, `description`, `when_to_use`, `argument-hint`, `arguments`, `disable-model-invocation`, `user-invocable`, `allowed-tools`, `disallowed-tools`, `model`, `effort`, `context: fork`, `agent`, `background`, `hooks`, `paths` (globs), `shell`, `metadata`, `license`, `compatibility`. Outside Claude Code (claude.ai, Skills API), only name, description, license, compatibility, metadata and allowed-tools are allowed. — [Skills](https://code.claude.com/docs/en/skills)
- Progressive disclosure:
  - Descriptions are always in context. `description` plus `when_to_use` is truncated at 1,536 characters in the listing.
  - The body loads on invocation. Keep `SKILL.md` under 500 lines.
  - After compaction, each skill's most recent invocation is re-attached, up to 5,000 tokens per skill and 25,000 tokens combined.

  — [Skills](https://code.claude.com/docs/en/skills)
- Substitutions: `$ARGUMENTS`, `$N`, `$name`, `${CLAUDE_SKILL_DIR}`, `${CLAUDE_PROJECT_DIR}`, `${CLAUDE_SESSION_ID}`, `${CLAUDE_EFFORT}`. `` !`cmd` `` injects dynamic shell output before Claude sees the skill, and a failing command aborts the invocation. — [Skills](https://code.claude.com/docs/en/skills)
- Custom commands have merged into skills. A legacy `.claude/commands/x.md` still creates `/x`. — [Skills](https://code.claude.com/docs/en/skills)

**Subagents (agent definition files)**
- Frontmatter fields:
  - Required: `name`, `description`
  - Optional: `tools`, `disallowedTools`, `model` (sonnet/opus/haiku/fable/full ID/inherit), `permissionMode`, `maxTurns`, `autoCompactWindow` (100k–1M, v2.1.296+), `skills` (preloaded), `mcpServers`, `hooks`, `memory` (user/project/local), `background`, `omitClaudeMd`, `effort` (low/medium/high/xhigh/max), `isolation: worktree`, `color`, `initialPrompt`, `experimental.cacheTtl` (5m/1h)

  — [Subagents](https://code.claude.com/docs/en/sub-agents)
- **Plugin subagents ignore `hooks`, `mcpServers` and `permissionMode` (and `initialPrompt`)** for security. Ship hooks in `hooks/hooks.json` and MCP servers in `.mcp.json` instead. Plugin agents have the lowest precedence: managed > `--agents` flag > project > user > plugin. — [Subagents](https://code.claude.com/docs/en/sub-agents)

**Hooks (event list as of 2026-10)**
- Events:
  - Session lifecycle: `SessionStart`, `Setup`, `SessionEnd`
  - Prompts and tools: `UserPromptSubmit`, `UserPromptExpansion`, `PreToolUse`, `PermissionRequest`, `PermissionDenied`, `PostToolUse`, `PostToolUseFailure`, `PostToolBatch`
  - Display and notifications: `Notification`, `MessageDisplay`
  - Subagents and tasks: `SubagentStart`, `SubagentStop`, `TaskCreated`, `TaskCompleted`, `TeammateIdle`
  - Turn end: `Stop`, `StopFailure`
  - Config and filesystem: `InstructionsLoaded`, `ConfigChange`, `CwdChanged`, `DirectoryAdded`, `FileChanged`, `WorktreeCreate`, `WorktreeRemove`
  - Compaction and models: `PreCompact`, `PostCompact`, `PreModelSwitch`, `PostModelSwitch`
  - MCP input: `Elicitation`, `ElicitationResult`

  — [Hooks reference](https://code.claude.com/docs/en/hooks)
- Hook handler types: `command`, `http` (POST JSON), `mcp_tool` (calls a tool on a configured MCP server), `prompt` (single-turn model judgment), `agent` (subagent with tools; experimental). — [Hooks reference](https://code.claude.com/docs/en/hooks)
- Handler fields: `type`, `if` (a permission-rule expression such as `Bash(git *)`), `timeout`, `statusMessage`, `once`. Command hooks also take `command`, `args` (exec form), `async`, `asyncRewake`, `shell`, and `onFailure` (`"block"`, v2.1.295+). — [Hooks reference](https://code.claude.com/docs/en/hooks)

### Inferences
- For a game-dev plugin, skills hold domain knowledge (engine APIs, store submission rules, art-direction guides) because they cost almost nothing until invoked. MCP servers hold engine and tool control. Hooks hold enforcement. Agents hold roles. Workflows hold repeatable multi-agent pipelines.
- Because plugin agents ignore `mcpServers`, `hooks` and `permissionMode`, tool scoping per role must come from `tools`/`disallowedTools` in the agent file, with plugin-level hooks keyed on agent context (e.g., `SubagentStop` matchers) and MCP servers at plugin level.
- Long-lived engine bridges (Unity/Godot editor log tail, device logcat, build server) map naturally onto **monitors** (experimental, interactive only) or **channels** (MCP server pushes events). Heavy native helpers (asset converters, `xcrun`/`gradle` wrappers) fit in `bin/`, but `bin/` blocks claude.ai/Cowork installation, so a CLI-only product would accept that trade-off.
- Third-party API keys (image, 3D, audio generation; store credentials) should be `userConfig` options with `sensitive: true`. They reach MCP servers via `${user_config.KEY}` in `env`, and hooks via `CLAUDE_PLUGIN_OPTION_<KEY>`. Never put them in skill text.
- Put caches (generated assets, downloaded SDKs, `node_modules`) in `${CLAUDE_PLUGIN_DATA}`, never in `${CLAUDE_PLUGIN_ROOT}`.
- A multi-plugin suite (core orchestrator, engine adapters per Unity/Godot, asset-gen, store-deploy) can use `dependencies` plus one marketplace with `git-subdir` or relative-path sources, pinned by `sha`.
- Illustrative (not from docs) layout for the game plugin:
  ```
  mobile-game-forge/
  ├── .claude-plugin/plugin.json      # name, version, userConfig (sensitive API keys), dependencies, experimental.evals
  ├── skills/{game-design-doc, godot-engine, unity-engine, asset-pipeline, audio-pipeline, store-submission, playtest-qa}/SKILL.md (+ references/, scripts/)
  ├── agents/{producer, gameplay-engineer, technical-artist, audio-designer, qa-tester, build-release, critic}.md
  ├── workflows/{build-feature.js, asset-batch.js, release-candidate.js}
  ├── hooks/hooks.json                # PostToolUse compile check, Stop/TaskCompleted/SubagentStop gates, SessionStart progress injection
  ├── .mcp.json                       # engine bridge (stdio), asset-gen gateway, device/emulator controller
  ├── monitors/monitors.json          # engine log tail / emulator logcat (experimental)
  ├── bin/                            # optional CLI helpers (blocks claude.ai/Cowork install)
  ├── scripts/                        # hook scripts
  └── evals/<case>/{prompt.md, graders/*.md, case.yaml}, evals/mocks/<server>/<tool>.md
  ```

### Gaps
- I didn't fetch the full `plugins/loading` page (version computation for git sources without `version`, update cadence and auto-update toggles) or the `plugins/publish` page (directory submission review process).
- The main session's status line can't be set through plugin `settings`; only `subagentStatusLine` can. The plugin-authoring skill description suggests mods can draw a status line, but I didn't verify the mods reference.
- I couldn't confirm whether "output styles" remain a first-class plugin component beyond the `outputStyles` manifest field (they are listed, but I didn't read the runtime semantics).

---

## 2. Claude Agent SDK, headless mode, GitHub Actions, cloud sessions, routines: plugin vs standalone agent

### Takeaway
The Agent SDK (Python and TypeScript) is "Claude Code as a library". It runs the same binary, agent loop, tools, hooks, subagents, skills and plugins. `claude -p` is the CLI face of the same SDK. Build a plugin when the user drives Claude Code interactively, or when automation can run Claude Code headless, in CI or as cloud routines. Build a standalone SDK app (or use Managed Agents) when you need your own product UI, server hosting, or third-party end users. Third-party SDK products must use API keys, not claude.ai login.

### Cited Findings
- Comparison from the docs:
  - Agent SDK: "Embed Claude Code's agent in your own Python or TypeScript application, in a process you operate. A library that runs the Claude Code binary."
  - CLI: interactive use.
  - Client SDK: raw API, you write the loop.
  - Managed Agents: Anthropic-hosted harness with a cloud or self-hosted sandbox.

  — [Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview)
- SDK capabilities include built-in tools, hooks, subagents, MCP, permissions, sessions (resume/fork), skills, commands and memory loaded from `.claude/` and `~/.claude/`, and "Plugins: package skills, agents, hooks, and MCP servers, and load them by local path." — [Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview)
- "Unless previously approved, Anthropic does not allow third party developers to offer claude.ai login or rate limits for their products, including agents built on the Claude Agent SDK." Branding: "Claude Agent" or "X Powered by Claude" are allowed. "Claude Code" branding is not. — [Agent SDK overview](https://code.claude.com/docs/en/agent-sdk/overview)
- Headless flags:
  - `claude -p` with `--output-format text|json|stream-json`, `--json-schema` (result in `structured_output`), `--allowedTools`, `--permission-mode` (auto, dontAsk, acceptEdits), `--permission-prompts none` (v2.1.259+), `--continue` and `--resume <session_id>`, `--append-system-prompt`.
  - `--bare` skips auto-discovery of hooks, skills, plugins, MCP and CLAUDE.md. It is "recommended mode for scripted and SDK calls, and will become the default for `-p`". Plugins then load explicitly with `--plugin-dir <path>` / `--plugin-url <url>`, agents with `--agents`, and MCP with `--mcp-config`.

  — [Headless](https://code.claude.com/docs/en/headless.md)
- JSON output includes `total_cost_usd` and a per-model breakdown. `--max-budget-usd` caps spend and stops background work when reached. The `system/init` event lists `plugins` and `plugin_errors`, and `mcp_servers` and `mcp_server_errors`, "so a CI gate can fail on a non-empty array". — [Headless](https://code.claude.com/docs/en/headless.md)
- Without `--bare`, a `-p` session runs project hooks and connects `.mcp.json` servers with no trust dialog. That is a security consideration for CI on untrusted repos. — [Headless](https://code.claude.com/docs/en/headless.md)
- GitHub Actions: `anthropics/claude-code-action@v1`.
  - Modes: interactive (`@claude` mentions) or automation (a `prompt` input).
  - Plugins install via the `plugin_marketplaces` and `plugins` inputs (e.g., `code-review@claude-code-plugins`), and the prompt can be `/plugin-name:skill-name`.
  - Other inputs: `claude_args` passes CLI flags such as `--max-turns`, `--model` and `--allowedTools`.
  - Auth: `ANTHROPIC_API_KEY`, `CLAUDE_CODE_OAUTH_TOKEN`, or OIDC workload identity federation. Bedrock, Vertex and Foundry are supported.

  — [GitHub Actions](https://code.claude.com/docs/en/github-actions.md)
- Routines (research preview) are saved cloud configurations: prompt, repos, environment, connectors and model.
  - Triggers: schedule (minimum interval 1 hour, plus one-off runs), API (`POST .../routines/<id>/fire` with a bearer token and beta header `experimental-cc-routine-2026-04-01`), and GitHub events (PR, release).
  - They run autonomously "as full Claude Code cloud sessions: there is no permission-mode picker". They use skills committed to the cloned repo, and push to `claude/`-prefixed branches.
  - Limits: 100 scheduled runs/hour per account, 30 run-now or API fires per routine per hour.
  - Fire `text` arrives wrapped as untrusted data in a `<routine-fire-payload>` block.

  — [Routines](https://code.claude.com/docs/en/routines.md)
- Routines need a claude.ai subscription login (Pro/Max/Team/Enterprise); `/schedule` is unavailable with Console API keys or cloud providers. Network access is set per cloud environment: Trusted is the default allowlist, with Custom and Full options. Keys for APIs that Claude calls should be stored as "network secrets" rather than env vars, which are visible to anyone using the environment. — [Routines](https://code.claude.com/docs/en/routines.md)
- Cloud sessions (Claude Code on the web) have `--cloud`/`--teleport`, and workflow results survive VM reclamation when you resume. Cloud environments configure network, env vars, setup scripts and caching. — [docs index](https://code.claude.com/docs/llms.txt); [Workflows](https://code.claude.com/docs/en/workflows)
- Agent teams cannot spawn teammates in `-p` or SDK sessions. Named subagents run as ordinary subagents there. — [Agent teams](https://code.claude.com/docs/en/agent-teams.md)
- Workflows run in `-p` and the SDK, but don't prompt for approval there. Allow them with a `Workflow` / `Workflow(<name>)` permission rule, auto mode, a PreToolUse hook, or `canUseTool`. — [Workflows](https://code.claude.com/docs/en/workflows)

### Inferences
- A hybrid architecture seems best:
  - The **plugin** is the source of truth for skills, agents, hooks, MCP and workflows.
  - **Interactive** use for creative direction and sign-off.
  - **Headless or SDK runners** (`claude --bare -p --plugin-dir ... --output-format stream-json --max-budget-usd N`) for overnight build-and-test loops.
  - **GitHub Actions** for CI quality gates, and **routines** for scheduled tasks (nightly builds, store-review checks).
- A commercial "build a game for me" SaaS for end users would have to be an Agent SDK or Managed Agents product with API-key billing. It can load the same plugin by path, but cannot use users' claude.ai subscriptions.
- Agent teams are interactive-only, so headless long-running builds should orchestrate with subagents and workflows, not teams.

### Gaps
- I didn't fetch the Agent SDK `plugins` page or the TypeScript/Python option lists (exact option names such as `plugins`, `settingSources`, `maxBudgetUsd`, `canUseTool`). Only `canUseTool` and `interrupt()` are confirmed by the fetched pages.
- I didn't verify Managed Agents details (pricing, sandbox specs).

---

## 3. Multi-agent orchestration patterns and long-horizon context management

### Takeaway
Anthropic's guidance agrees on three things. Use orchestrator-worker with isolated subagent contexts that return condensed results. Externalize state to files (a feature list in JSON, a progress log, git history) so fresh sessions can resume. Spend tokens deliberately, since multi-agent work costs about 15x chat but wins on breadth. Claude Code now offers four orchestration primitives: subagents, skills with `context: fork`, agent teams (experimental), and dynamic workflows (JS scripts with `agent()`, `parallel()`, `pipeline()` and schemas), with worktree isolation and resumability.

### Cited Findings
- Multi-agent research system (Jun 13, 2025):
  - An Opus 4 lead with Sonnet 4 subagents beat single-agent Opus 4 by 90.2% on an internal research eval.
  - Token usage explained about 80% of BrowseComp variance.
  - Agents use about 4x the tokens of chat; multi-agent systems about 15x.
  - Parallel tool calls cut research time by up to 90%.
  - Practices: give subagents an objective, output format, tool guidance and boundaries; scale effort to complexity; write subagent outputs to the filesystem and pass references; resume from checkpoints rather than restarting.
  - Poor fit: "Tasks with few parallelizable steps, such as most coding work" and tightly interdependent tasks.

  — [Anthropic: multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
- Effective harnesses for long-running agents (Nov 26, 2025):
  - The initializer agent writes `init.sh`, `claude-progress.txt`, an initial git commit, and a JSON feature list (200+ features, all with `passes: false`).
  - Coding agents work one feature per session, may change only `passes`, commit, and update progress.
  - "It is unacceptable to remove or edit tests." JSON was chosen because models are less likely to overwrite it than Markdown.
  - Session startup routine: read git log and progress, pick the top unfinished feature, run `init.sh`, run a basic E2E check.

  — [Anthropic: effective harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- That harness post leaves "single vs multi-agent" open. The authors suggest specialized testing, QA or cleanup agents could help. — [Anthropic: effective harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- Context engineering (Sep 29, 2025):
  - Context is "a critical but finite resource", and context rot sets in as it grows.
  - Write system prompts at the "right altitude".
  - Use just-in-time retrieval through lightweight references.
  - Long-horizon techniques: compaction, structured note-taking (agentic memory), and sub-agents that return condensed results "often 1,000-2,000 tokens".

  — [Anthropic: context engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- Writing tools for agents (Sep 11, 2025):
  - Don't wrap every endpoint; consolidate.
  - Namespace tools.
  - Return high-signal, human-readable fields, with a `response_format` concise/detailed option.
  - Paginate and truncate: "For Claude Code, we restrict tool responses to 25,000 tokens by default."
  - Develop tools against evals, and let Claude optimize tool descriptions.

  — [Anthropic: writing tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- Dynamic workflows (blog Jun 2, 2026):
  - `agent(prompt, opts)` with `schema`, `model`, `isolation` (worktree or remote) and `agentType`, plus `parallel()` and `pipeline()`.
  - Rationale: long single-context runs suffer from "agentic laziness, self-preferential bias, and goal drift."
  - Patterns: adversarial verification (one verifier per output, then a skeptic filter), generate-and-filter, tournament ("comparative judgment is more reliable than absolute scoring"), fan-out-and-synthesize, loop-until-done, classify-and-act (route to Sonnet or Opus by complexity), and quarantine (unprivileged readers of untrusted content, a privileged actor that acts only on their summaries).

  — [Claude blog: A harness for every task](https://claude.dev/blog/a-harness-for-every-task-dynamic-workflows-in-claude-code/)
- Workflow runtime:
  - Scripts are plain JS with top-level await. `agent()`, `pipeline()`, `parallel()`, `phase()`, `log()` and the `args` global are available. `meta` {name, description, phases} must be the first statement.
  - No `import()`. No direct filesystem or shell access; agents do the work.
  - `Date.now()` and `Math.random()` throw, to keep replay deterministic.
  - Up to 16 concurrent agents by default (`CLAUDE_CODE_WORKFLOW_MAX_CONCURRENT_AGENTS`, 1–256), 4,096 items per `parallel()`/`pipeline()`, 1,000 agents per run.
  - Resumable in the same session: completed agents return cached results, and later agents rerun after the first changed or failed one.
  - Stalled agents auto-restart up to 5 times (`stallMs`).
  - Schema-validated output gets 5 retries.

  — [Workflows](https://code.claude.com/docs/en/workflows)
- When to use what:

  | | Decides what runs next | Scale |
  |---|---|---|
  | Subagents | Claude, turn by turn | A few per turn |
  | Agent teams | Lead agent | A handful of long-running peers, shared task list, interruption-tolerant |
  | Workflows | The script | Dozens to hundreds of agents, resumable, results in script variables |

  — [Workflows](https://code.claude.com/docs/en/workflows)
- Subagent mechanics:
  - Nesting goes up to 3 levels below the main conversation by default (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`), with a cap of 20 concurrent subagents (`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`).
  - `isolation: worktree` branches from the default branch, confines Bash to the worktree, and auto-removes the worktree if nothing changed.
  - `memory: project` stores agent memory at `.claude/agent-memory/<name>/`; the first 200 lines or 25KB of `MEMORY.md` auto-load.
  - Background subagents run with a reduced built-in toolset but keep MCP tools.

  — [Subagents](https://code.claude.com/docs/en/sub-agents)
- Agent teams (experimental, `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`):
  - Structure: a lead plus teammates, a shared task list with dependencies and file-locked claiming, and mailboxes at `~/.claude/teams/{team}/inboxes/`.
  - Advice: start with 3–5 teammates and 5–6 tasks per teammate, and avoid two teammates editing one file.
  - Limitations: no resume of in-process teammates, no nested teams, interactive only.
  - In plan mode, teams use about 7x the tokens of a standard session.

  — [Agent teams](https://code.claude.com/docs/en/agent-teams.md); [Costs](https://code.claude.com/docs/en/costs.md)
- Memory and context features:
  - CLAUDE.md (or AGENTS.md) and auto memory.
  - Custom compaction instructions in CLAUDE.md ("# Compact instructions").
  - Keep CLAUDE.md under 200 lines and move workflow-specific instructions into skills.

  — [Costs](https://code.claude.com/docs/en/costs.md); [docs index (memory)](https://code.claude.com/docs/llms.txt)

### Inferences
- Recommended topology for an autonomous mobile-game builder:
  1. **Initializer/producer** phase: turn the brief into a GDD, then into a JSON feature/asset list with `passes` flags, `init.sh` (opens the engine headless, runs tests), `progress.md`, and a git repo.
  2. **Per-feature loop**: one gameplay feature per session or agent. Code agents run in worktrees, then merge.
  3. **Asset pipeline** as a `pipeline()` fan-out per asset (generate, post-process, import, verify), with schema-validated manifests.
  4. **Verification** as adversarial critic agents per feature, with a tournament for creative choices such as art style candidates.
  5. **Release** phase: build, device test, store metadata, submit.
- Engine projects contain shared, conflict-prone files (Unity `.unity` scenes and `.meta` files, Godot `.tscn`/`project.godot`). Parallelize assets and isolated scripts freely. Serialize scene and project-settings edits through one owner agent, or merge with worktrees plus engine-aware merge tooling.
- Keep state in files the harness controls, not in context:
  - `features.json` holds pass/fail.
  - An `assets/manifest.json` holds provenance, license, cost and status.
  - `progress.md` holds session notes.
  - A `SessionStart` hook injects a compact summary via `additionalContext` (capped at 10,000 characters).

### Gaps
- I did not re-fetch "Building effective agents" (Dec 2024; patterns: prompt chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer) or the Agent Skills announcement (Oct 2025) this session. These are known from prior knowledge and should be cited as [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) and [Equipping agents with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills), but I did not verify their contents here.
- No Anthropic source specifically addresses game development or binary-asset-heavy repos.

---

## 4. Verification loops: hooks, visual verification, critics, eval suites, quality gates

### Takeaway
Claude Code offers deterministic enforcement through hooks: exit code 2 blocks, and `decision: "block"` on Stop, SubagentStop, TaskCompleted and TeammateIdle keeps the agent working. Model-judged gates are available too, through `prompt` and `agent` hook types and critic subagents. `claude plugin eval` (early access) runs plugin eval suites with a no-plugin baseline, mockable MCP servers, cost ceilings and CI exit codes. Anthropic's harness research shows that end-to-end testing "as a human user would" via browser automation was essential. Agents otherwise declare features done after unit tests.

### Cited Findings
- Exit code semantics:
  - 0: success, with stdout parsed as JSON if it is a JSON object.
  - 2: blocking error, with stderr as the reason. It "blocks even if the hook also prints JSON".
  - Other codes: non-blocking.
  - On PreToolUse, exit 2 blocks the tool. On PostToolUse, it only shows stderr to Claude because the tool already ran.

  — [Hooks reference](https://code.claude.com/docs/en/hooks)
- Decision control:
  - `"decision": "block"` plus `reason` on `UserPromptSubmit`, `PostToolUse`, `Stop`, `SubagentStop`, `ConfigChange` and `PreCompact`.
  - PreToolUse returns `permissionDecision` (allow/deny/ask/defer) and `updatedInput`.
  - PostToolUse can return `updatedToolOutput`.
  - `additionalContext` (10,000-character cap) is available on SessionStart, PreToolUse, PostToolUse and Stop. The docs advise "factual statements, not imperative system instructions".

  — [Hooks reference](https://code.claude.com/docs/en/hooks)
- Async and failure behavior:
  - `async: true` runs in the background.
  - `asyncRewake` runs in the background and wakes Claude on exit 2 with stderr. That suits long builds.
  - `onFailure: "block"` makes a crashed or timed-out hook block the action.
  - Default timeouts: 600s for command, 30s for prompt, 60s for agent.

  — [Hooks reference](https://code.claude.com/docs/en/hooks)
- Team and task gates: `TeammateIdle` (exit 2 keeps the teammate working), `TaskCreated` and `TaskCompleted` (exit 2 prevents completion and sends feedback). — [Agent teams](https://code.claude.com/docs/en/agent-teams.md)
- Long-running harness evidence:
  - Agents marked features complete after unit tests or curl. Prompting them to use Puppeteer MCP and test as a human would "markedly improved results".
  - Limitation: Claude could not see browser-native alert modals through Puppeteer.

  — [Anthropic: effective harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- Multi-agent research evals:
  - Start with about 20 representative queries.
  - A single LLM-judge call with a rubric (0.0–1.0 plus pass/fail) matched human judgment best.
  - Human testers still caught issues that automation missed.

  — [Anthropic: multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
- `claude plugin eval` (requires v2.1.269+; the troubleshooting section mentions "currently in early access"):
  - Cases live in `evals/<case>/` with `prompt.md` (frontmatter `max_turns`, `allowed_tools`, `model`, `timeout_seconds` default 300 and max 3600, `tags`, `env`), `graders/*.md`, and an optional `case.yaml` (`schema_version: "1.1"`, `context.scaffold_script`, `context.history_file`, `context.add_dirs`).
  - `claude plugin eval init` interviews you and writes the suite.

  — [Plugin evals](https://code.claude.com/docs/en/plugin-evals)
- Grading:
  - Grader types: `regex`, `tool_used`, `tool_order` and `file_exists` (free), plus `llm` and `baseline` (judge model, 3 judge calls per grader per run). "There are no custom-code graders."
  - Each case runs 3 times with the plugin and 3 times without, reporting WITH, W/OUT and Δ.
  - Skill-trigger graders are excluded from scoring in two-arm runs.

  — [Plugin evals](https://code.claude.com/docs/en/plugin-evals)
- Mocks and isolation:
  - MCP mocks live at `evals/mocks/<server>/<tool>.md`. They support `{{input.x}}` templating, `expect:` input guards, `error: true`, and `type: agent` (judge-model-simulated server), with recorded replays under `mocks/.replay/`.
  - Runs never start real MCP servers unless you pass `--allow-real-servers` or `--mocks off`.
  - Granted Bash runs under the OS sandbox.

  — [Plugin evals](https://code.claude.com/docs/en/plugin-evals)
- CI flags:
  - `--runs`, `--model` (pin it in CI), `--judge-model`, `--ablation none|with-without`, `--threshold` (default 1.0; exit 1 below it), `--max-cost-usd` (exit 2 on partial runs), `--allow-tools`, `--scaffold`, `--trust-plugin`, `--json`, `--no-publish`, `--keep-temp`.
  - Results are written to `aggregate-result.json` (`schemaVersion: 1`) and `report.html`.

  — [Plugin evals](https://code.claude.com/docs/en/plugin-evals)
- Tip from the docs: "To check that a build or test passed inside the run, have the prompt ask Claude to run it and write the outcome to a file, grade that file, and assert the command ran with a `tool_used` grader." — [Plugin evals](https://code.claude.com/docs/en/plugin-evals)
- Skill-level evals: the `skill-creator` plugin (`/plugin install skill-creator@claude-plugins-official`) uses `evals/evals.json`, `grading.json` and `benchmark.json`, blind A/B comparison, and description trigger-rate tuning. Its file format differs from `claude plugin eval`. — [Skills](https://code.claude.com/docs/en/skills)
- `claude plugin validate [--strict]` is the schema and path check for CI. — [Plugin manifest reference](https://code.claude.com/docs/en/plugins-reference)
- Bundled skills include `/verify`, `/run`, `/code-review` and `/skill-doctor`. — [Skills](https://code.claude.com/docs/en/skills)
- LSP plugins push diagnostics into context after edits, which catches type errors without a compile. — [Plugin manifest reference](https://code.claude.com/docs/en/plugins-reference); [Costs](https://code.claude.com/docs/en/costs.md)

### Inferences
- A layered gate design for the game plugin:
  1. **PostToolUse** (`Write|Edit` on `*.cs`/`*.gd`): a fast compile or lint via an engine CLI (e.g., Godot `--headless --check-only`, Unity batchmode compile). Return errors as `additionalContext`, or exit 2 so Claude fixes them immediately.
  2. **TaskCompleted / SubagentStop / Stop**: block until the feature's tests pass in headless mode and `features.json` shows `passes: true` with evidence (test log path, screenshot path).
  3. **Visual verification**: a capture tool from the engine MCP or device MCP (simulator or emulator screenshot) feeds a critic subagent with vision and a rubric. Anthropic models accept image input ([Models overview](https://platform.claude.com/docs/en/about-claude/models/overview)). Comparative or tournament judging beats absolute scores for art.
  4. **Adversarial verifier** agents per feature, as in the workflow quality patterns.
  5. **Plugin evals in CI**:
     - mock the asset-gen and store MCP servers with `type: agent` mocks or fixtures;
     - grade produced files (`file_exists`, `regex` over manifests or build logs);
     - run `tool_order` checks (e.g., test before commit);
     - pin models and set `--max-cost-usd`.
- Since plugin eval has no custom-code graders, push deterministic checks (FPS budget, APK size, build success) into the run itself: Claude writes the result to a file, and a `regex` or `file_exists` grader checks it.

### Gaps
- I found no Anthropic-published guidance specific to screenshot-based game QA, simulator automation, or mobile device farms.
- I didn't verify the exact Stop hook input fields (e.g., a `stop_hook_active` loop guard) on the fetched page portion. The page was truncated at 100k characters.

---

## 5. Cost and model selection

### Takeaway
As of October 2026 the lineup is:

| Model | Input $/MTok | Output $/MTok | Default effort | Role |
|---|---|---|---|---|
| Claude Fable 5.1 | 10 | 50 | high | Hardest long-horizon work |
| Claude Opus 5.5 | 4 | 20 | medium | Recommended default |
| Claude Sonnet 5.5 | 2 | 10 | high | Speed/intelligence balance |
| Claude Haiku 5.5 | from 0.10 | from 0.50 | medium | High volume, latency-sensitive |

All have 1M context, 128K output and adaptive thinking. Cost control in Claude Code rests on per-agent `model`/`effort`, prompt caching (with sibling cache sharing in workflow fan-outs), small CLAUDE.md files, skills over always-on context, deferred MCP tools, hooks that pre-filter output, and hard caps: `--max-budget-usd`, `--max-turns`, `maxTurns`, workflow size guidelines, and `--max-cost-usd` for evals.

### Cited Findings
- Model IDs: `claude-fable-5-1`, `claude-opus-5-5`, `claude-sonnet-5-5`, `claude-haiku-5-5`. "If you're unsure which model to use, start with Claude Opus 5.5". Use Fable 5.1 "for demanding reasoning and long-horizon agentic work, or when your evals on Claude Opus 5.5 at higher effort still fall short." — [Models overview](https://platform.claude.com/docs/en/about-claude/models/overview)
- Pricing modifiers: the Batch API is 50% off. Cache reads cost 10% of base input by default, 5% on Opus 5.5 and Sonnet 5.5, and 2.5% on Fable 5.1. Legacy models still available: Fable 5, Opus 5, Opus 4.8/4.7/4.6/4.5, Sonnet 5, Sonnet 4.6, Haiku 4.5. — [Models overview](https://platform.claude.com/docs/en/about-claude/models/overview)
- You can't turn off thinking on Opus 5.5, Sonnet 5.5, Haiku 5.5 or the Fable models. Use effort levels to reduce cost. — [Costs](https://code.claude.com/docs/en/costs.md)
- Effort levels in Claude Code agents: `low`, `medium`, `high`, `xhigh`, `max`. "Ultracode" (`/effort ultracode`) makes Claude plan a workflow for every substantive task and sets effort to `xhigh`. — [Subagents](https://code.claude.com/docs/en/sub-agents); [Workflows](https://code.claude.com/docs/en/workflows)
- Subagent model resolution: per-invocation model, then frontmatter `model`, then `CLAUDE_CODE_SUBAGENT_MODEL`, then the main model. `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` overrides everything. Defining a project-level `Explore` agent with `model: haiku` makes exploration cheaper. — [Subagents](https://code.claude.com/docs/en/sub-agents)
- Enterprise averages: about $13 per developer per active day and $150–250 per month, with 90% under $30 per active day. Guidance: "Sonnet handles most coding tasks well and costs less than Opus." "For simple subagent tasks, specify `model: haiku`." "Use Sonnet for teammates." — [Costs](https://code.claude.com/docs/en/costs.md)
- Context levers:
  - MCP tool definitions are deferred by default (tool search). CLI tools like `gh` are still more context-efficient.
  - Hooks can pre-filter test output.
  - Move instructions from CLAUDE.md into skills, and keep CLAUDE.md under 200 lines.
  - Delegate verbose operations to subagents.

  — [Costs](https://code.claude.com/docs/en/costs.md)
- Caching:
  - Workflow agents with the same model, effort, agent type, tools, schema and cwd share a prompt-cache prefix. Claude Code staggers sibling starts by up to 5s (`CLAUDE_CODE_WORKFLOW_PREFIX_STAGGER_MS`) so the siblings read the first agent's cache.
  - The subagent cache TTL is 5 minutes by default. `subagentPromptCacheTtl: "1h"` extends it, and 1h cache writes cost more.

  — [Workflows](https://code.claude.com/docs/en/workflows)
- The main-session cache TTL is 1 hour on a subscription and 5 minutes on an API key or usage credits by default. — [Costs](https://code.claude.com/docs/en/costs.md)
- Workflow cost controls:
  - A "Large workflow" warning appears above 25 agents or 1.5M projected tokens.
  - `workflowSizeGuideline` takes small (<5), medium (<10, default), large (<50) or unrestricted.
  - Hard caps: 1,000 agents per run, 16 concurrent.
  - The blog's example runs: 14 agents at 482k tokens, 22 agents at 1.1M tokens.

  — [Workflows](https://code.claude.com/docs/en/workflows); [Claude blog](https://claude.dev/blog/a-harness-for-every-task-dynamic-workflows-in-claude-code/)
- Budget caps:
  - Headless: `--max-budget-usd`, with `total_cost_usd` reported in JSON.
  - GitHub Action: `--max-turns`, workflow timeouts, concurrency controls.
  - Plugin eval: `--max-cost-usd`.
  - Org level: workspace spend limits (Console), seat allowances and usage-credit spend limits (Team/Enterprise), and a `modelPricing` managed setting for reporting at contracted rates.

  — [Headless](https://code.claude.com/docs/en/headless.md); [GitHub Actions](https://code.claude.com/docs/en/github-actions.md); [Plugin evals](https://code.claude.com/docs/en/plugin-evals); [Costs](https://code.claude.com/docs/en/costs.md)
- Background work: with `autoContinueAtUsageLimit`, workflows pause at subscription usage limits and resume after the reset. This applies to interactive sessions only. — [Workflows](https://code.claude.com/docs/en/workflows)
- Multi-agent token multipliers: about 4x tokens for agents and about 15x for multi-agent versus chat (2025 data). Teams use about 7x in plan mode. — [Anthropic: multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system); [Costs](https://code.claude.com/docs/en/costs.md)

### Inferences
- Suggested role-to-model mapping (my inference, to be validated with plugin evals):

  | Role | Model and effort |
  |---|---|
  | Producer/architect and final critic | Opus 5.5 at high/xhigh; escalate to Fable 5.1 only for stuck debugging or overall design |
  | Gameplay engineers | Sonnet 5.5 at medium/high, or Opus 5.5 at medium |
  | Asset prompt-writers, manifest bookkeeping, log triage, file search | Haiku 5.5 at low/medium |
  | Visual QA critic | Sonnet 5.5 or Opus 5.5 (vision), using comparative judgments |

- Keep agent definitions byte-stable (same tools, model, effort) within a fan-out so prompt-cache sharing works. Consider `subagentPromptCacheTtl: 1h` for long builds with gaps over 5 minutes.
- External generation APIs (image, 3D, audio, music) likely dominate dollar cost relative to tokens for asset-heavy games. The plugin should track per-asset spend in a manifest and enforce its own budget in the MCP gateway; Claude Code's budget flags cover only model tokens.

### Gaps
- I didn't fetch the full pricing page (cache write multipliers for 5m and 1h, long-context surcharges, Haiku 5.5 tiered "from" pricing details).
- I didn't fetch the `model-config` page (effort semantics per model, `availableModels`, the advisor tool, fast mode pricing).

---

## 6. Security: API keys, sandboxing, permission modes

### Takeaway
Store third-party keys as plugin `userConfig` with `sensitive: true` (OS keychain), or as cloud-environment "network secrets" for routines. In CI, use GitHub Secrets or OIDC federation. Turn on the OS-level Bash sandbox (Seatbelt on macOS, bubblewrap on Linux and WSL2) with domain allowlists and `sandbox.credentials` deny/mask rules. Pick a permission mode for unattended runs (auto with a classifier, dontAsk, or acceptEdits) plus explicit allow rules. Plugin agents can't escalate their own permission mode, and `-p` without `--bare` will run repository hooks and MCP servers with no trust prompt.

### Cited Findings
- Sensitive `userConfig` values are stored in the platform's secure credential store, not settings.json. — [Plugin manifest reference](https://code.claude.com/docs/en/plugins-reference)
- What the Bash sandbox restricts, and what it doesn't:
  - Writes are limited to the cwd, a temp dir and added dirs.
  - Reads cover most of the machine, including `~/.ssh` and `~/.aws/credentials`, unless you add deny rules.
  - Network has no direct route out. A local proxy checks hosts against `network.allowedDomains`, which starts empty.
  - Environment variables, "including any secrets", are inherited.
  - Built on the open-source `@anthropic-ai/sandbox-runtime`.
  - Read, Edit, WebFetch, MCP servers and hooks run OUTSIDE the sandbox.

  — [Sandboxing](https://code.claude.com/docs/en/sandboxing.md)
- Sandbox settings:
  - `sandbox.enabled`, `filesystem.allowWrite`/`denyWrite`/`denyRead`/`allowRead`, `network.allowedDomains`/`deniedDomains`, `excludedCommands`.
  - `allowUnsandboxedCommands: false` disables the unsandboxed-retry escape hatch.
  - `failIfUnavailable: true` makes Claude Code exit if the sandbox can't start.
  - `autoAllowBashIfSandboxed` defaults to true.

  — [Sandboxing](https://code.claude.com/docs/en/sandboxing.md)
- Credential rules:
  - `sandbox.credentials` takes `files` and `envVars` entries with `mode: "deny"` (block or unset) or `mode: "mask"`. Masking shows a per-session sentinel, and the proxy substitutes the real value only on outbound requests to allowed hosts.
  - "There is no built-in credential deny list."
  - `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` strips credentials from all subprocesses.

  — [Sandboxing](https://code.claude.com/docs/en/sandboxing.md)
- Permission modes: `default`/`manual`, `acceptEdits`, `auto` (classifier-reviewed), `dontAsk`, `bypassPermissions`, `plan`. Plugin subagents ignore the `permissionMode` frontmatter. — [Subagents](https://code.claude.com/docs/en/sub-agents)
- `--permission-prompts none` (v2.1.259+) makes unattended runs deny anything that would prompt instead of waiting. In `--permission-mode auto`, a bare `Bash` allow entry is dropped and the classifier evaluates each command. — [Headless](https://code.claude.com/docs/en/headless.md)
- Workflow agents' prompts don't count as user requests for the auto-mode classifier, because the script computed them. Messages between agents (SendMessage) are flagged as coming from another Claude session, not the user, so they can't grant consent or approvals. — [Workflows](https://code.claude.com/docs/en/workflows); [Agent teams](https://code.claude.com/docs/en/agent-teams.md)
- Routines:
  - They run without permission prompts.
  - Connectors included in a routine can do writes without asking.
  - Env vars are visible to anyone using the environment, so store keys as network secrets.
  - Fire payloads are wrapped as untrusted data.

  — [Routines](https://code.claude.com/docs/en/routines.md)
- GitHub Actions: "Never commit API keys", use GitHub Secrets. OIDC federation via `anthropic_federation_rule_id` avoids long-lived secrets. Write access and human-actor checks guard triggers. — [GitHub Actions](https://code.claude.com/docs/en/github-actions.md)
- Eval runs: plugin hooks and real MCP servers run outside the agent sandbox, so "treat its scores as advisory unless you ran it in an isolated environment such as a container or CI runner." — [Plugin evals](https://code.claude.com/docs/en/plugin-evals)
- MCP spec security principles: explicit user consent for tool invocation, and treat tool descriptions and annotations as untrusted unless the server is trusted. — [MCP specification](https://modelcontextprotocol.io/specification/latest)
- Quarantine pattern from the workflow blog: unprivileged readers process untrusted content, and a privileged actor acts on their summaries. — [Claude blog](https://claude.dev/blog/a-harness-for-every-task-dynamic-workflows-in-claude-code/)

### Inferences
- For the game plugin, run asset-generation API calls inside the plugin's MCP gateway server, which receives keys through `${user_config.*}` in `env`. That way keys never enter the model's context or the Bash environment.
- Mobile signing material (iOS certificates, Android keystores, App Store Connect or Play Console API keys) is the highest-risk secret. Keep it out of the sandbox entirely: use `credentials.files` deny rules, and run signing only through a dedicated `bin/` tool or MCP tool, gated by a PreToolUse hook that requires user confirmation (`permissionDecision: "ask"`). Never allow it in unattended routines.
- An unattended overnight build should use:
  - `--permission-mode auto` or `dontAsk` with explicit allow rules for engine CLIs;
  - the sandbox with `allowedDomains` limited to package registries and the asset-API hosts;
  - `allowUnsandboxedCommands: false`;
  - `--permission-prompts none`;
  - `--bare` with an explicit `--plugin-dir`.

### Gaps
- I didn't fetch the `permission-modes`, `auto-mode-config` or `plugins/security` pages (plugin trust model, what a plugin can do on install).
- I didn't verify whether Claude Code's MCP config supports OAuth for remote HTTP servers bundled in plugins. The MCP spec's latest auth details weren't captured.

---

## 7. Examples: notable plugins and marketplaces, game-dev plugins, engine MCP servers; MCP spec status

### Takeaway
Anthropic maintains the official (`claude-plugins-official`), community (`claude-community`) and demo (`claude-code-plugins`) marketplaces, plus topic marketplaces (`anthropics/skills`, `anthropics/knowledge-work-plugins`). Notable first-party plugins include commit-commands, code-review, feature-dev, security-guidance, skill-creator, and LSP plugins. The game-dev ecosystem is community-built and immature: one Godot plugin (cc-godot) bundles commands, an agent, a skill and a Godot MCP server, and several Unity, Godot and Blender MCP servers exist. I found no official Anthropic game-dev plugin. The current MCP spec revision is 2026-07-28, with Tasks, Skills over MCP, and MCP Apps as extensions.

### Cited Findings
- Official marketplace contents: "Plugins Anthropic maintains, plus plugins from partners and other authors". Anthropic-maintained examples: `commit-commands`, `code-review`, `feature-dev`, and the language-server plugins. `security-guidance` is also in the demo marketplace. Browse via `/plugin` → Discover or claude.com/marketplace/plugins, which shows install counts and an "Anthropic verified" badge. — [Anthropic's marketplaces](https://code.claude.com/docs/en/plugins/anthropic-marketplaces.md)
- `skill-creator@claude-plugins-official` provides skill evals and benchmarking. — [Skills](https://code.claude.com/docs/en/skills)
- The bundled `/deep-research` workflow is the reference example of a fan-out, cross-check and vote pipeline. — [Workflows](https://code.claude.com/docs/en/workflows)
- The `code-review` plugin runs in GitHub Actions via `plugins: "code-review@claude-code-plugins"`. It shows CI use of a plugin skill with an MCP inline-comment tool. — [GitHub Actions](https://code.claude.com/docs/en/github-actions.md)
- Game dev:
  - **cc-godot** (community, by Zate) targets Godot 4.5+. It has namespaced commands (`/gd:setup`, `/gd:run`), a planning agent and a Godot expertise skill, and wires in a Godot MCP server that the user must clone and build. Install: `/plugin install gd@godot-gamedevp` after adding the marketplace.
  - Caveat: a directory listing showed a placeholder GitHub URL, so verify the repo before relying on it.

  — [cc-godot README (jsDelivr mirror)](https://cdn.jsdelivr.net/gh/zate/cc-godot@main/README.md); [vibeindex listing](https://vibeindex.ai/plugins/Zate/cc-godot/gd)
- Unity MCP servers listed on third-party directories: funplay-unity-mcp (STDIO) and unity-ai-bridge, with funplay-godot-mcp for Godot. There is also a Unity/Unreal/Godot pattern skill pack (guidance only, no bridge). Feature claims could not be confirmed. — [claudemarketplaces: funplay-unity-mcp](https://claudemarketplaces.com/mcp/funplayai/funplay-unity-mcp); [claudemarketplaces: game engines skill](https://claudemarketplaces.com/skills/pluginagentmarketplace/custom-plugin-game-developer/game-engines)
- A 2026 comparison article calls CoplayDev/unity-mcp "the most-active engine MCP today". It describes Godot MCP as fitting indie 2D/3D, and Blender MCP as a Python-driven 3D asset tool to pair with an engine (export GLTF/FBX). This is a third-party blog and weak evidence. — [mcp.directory blog](https://mcp.directory/blog/godot-vs-unity-vs-blender-mcp-skills-2026)
- GladeKit MCP (PyPI, versions 0.7.13–0.7.21) claims to connect Claude Code, Cursor and other clients to Unity or Godot editors. This is a third-party claim. — [PyPI gladekit-mcp](https://pypi.org/project/gladekit-mcp/0.7.21/)
- MCP spec status:
  - The latest spec page references schema `2026-07-28`.
  - Core: JSON-RPC 2.0, with "stateless, self-contained requests" and "per-request capability negotiation".
  - Server features: resources, prompts, tools. Client feature: elicitation.
  - Opt-in extensions: Tasks ("asynchronous execution of long-running operations, with polling, mid-flight input, and durable handles"), Skills over MCP, and MCP Apps (interactive UI inline).

  — [MCP specification](https://modelcontextprotocol.io/specification/latest)
- Claude Code supports MCP stdio and http/sse/ws server configs in plugins, `.mcpb`/`.dxt` bundles, and an `mcp_tool` hook type. MCP `Elicitation` and `ElicitationResult` hook events exist. — [Plugin manifest reference](https://code.claude.com/docs/en/plugins-reference); [Hooks reference](https://code.claude.com/docs/en/hooks)

### Inferences
- Existing engine MCP servers are community projects of uneven maturity. A "world-class" plugin should either vendor and pin one per engine (via `.mcpb` bundle or `npm`/`git-subdir` source with SHA) behind a thin, consolidated tool layer designed per "Writing tools for agents", or write its own engine bridge.
- Godot is the most automation-friendly target: MIT license, a headless CLI, text-based `.tscn` scenes that diff and merge well, and an existing Claude Code plugin precedent. Unity has the larger mobile market but binary or YAML scene merges, editor licensing, and batchmode constraints. This is my inference; it is not from a cited comparison.
- The MCP Tasks extension (async long-running operations with durable handles) fits long engine builds and slow asset generation (3D models, music) directly, if Claude Code supports it. I did not verify client support.
- Blender MCP fits as an asset-processing worker (retopology, LOD, export) inside the asset pipeline, rather than as the game runtime.

### Gaps
- I couldn't retrieve the GitHub repos for CoplayDev/unity-mcp, ahujasid/blender-mcp, or Godot MCP servers to confirm tools, transports, licenses, or plugin packaging.
- I found no evidence of an official Anthropic or partner game-dev plugin in the official marketplace. The catalog "changes often" and isn't listed in the docs, so a manual check of claude.com/marketplace/plugins is needed.
- I didn't verify whether Claude Code implements the MCP Tasks or MCP Apps extensions, or which MCP spec revision it negotiates.
- I didn't look at community "awesome-claude-code" lists or large community marketplaces (e.g., wshobson/agents) this session.
