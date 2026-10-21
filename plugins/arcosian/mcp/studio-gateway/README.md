# studio-gateway

Stdio MCP server that gives the Arcosian plugin one controlled door to asset, audio and 3D generation providers. Zero npm dependencies, Node 18 or newer, ESM.

What it adds on top of calling the providers directly:

- every generation lands under the project's `generated_dir`, with a manifest entry (`status: "candidate"`) and a budget ledger entry
- calls whose estimated cost exceeds the remaining cap are refused before any request is sent
- with no key, `GS_MOCK=1` or `dry_run`, it writes valid placeholder files (PNG, WAV, GLB, SVG) at cost 0
- multi-stage 3D jobs (Tripo rig, Meshy texture) run as a pipeline that `model3d_status` continues until the final GLB is downloaded
- licence rules against `config.revenue` (non-commercial terms, free tiers, ElevenLabs Music indie limits)
- `kb_search` over the plugin's skill library
- provider adapters checked against the official API docs (see [Verification](#verification-2026-10-20)) and an opt-in live smoke test for your own key

## Run

```
node server.mjs                                       # newline-delimited JSON-RPC 2.0 on stdin/stdout, logs on stderr
node test/run-tests.mjs                               # offline suite: no network, no keys
node test/live-smoke.mjs --provider openai            # DRY RUN: prints the exact request and the estimated cost
node test/live-smoke.mjs --provider openai --yes      # ONE real, billed request with your own key
```

The plugin's `.mcp.json` starts it with `${CLAUDE_PLUGIN_ROOT}/mcp/studio-gateway/server.mjs`. Protocol: `initialize` echoes the client's `protocolVersion` when it is one of 2026-07-28, 2025-11-25, 2025-06-18, 2025-03-26, 2024-11-05 (else 2025-06-18); also `notifications/initialized` (no reply), `tools/list`, `tools/call`, `ping`; unknown methods return -32601. Tool results are `content: [{type: "text", text: <JSON>}]` with `isError: true` on failure.

## Environment

| Variable | Purpose |
|---|---|
| `GEMINI_API_KEY`, `OPENAI_API_KEY`, `RECRAFT_API_KEY`, `FAL_KEY`, `TRIPO_API_KEY`, `MESHY_API_KEY`, `ELEVENLABS_API_KEY`, `STABILITY_API_KEY` | Provider keys. Empty means not configured. Never logged; redacted from errors. Lyria uses `GEMINI_API_KEY`. |
| `GS_ASSET_BUDGET_USD` | Default cap when `config.json` has no `budgets.asset_usd_cap`. |
| `GS_PLUGIN_ROOT`, `GS_PLUGIN_DATA` | Plugin paths. `kb_search` reads `GS_PLUGIN_ROOT/skills`, falling back to `../../skills` relative to `server.mjs`. |
| `GS_MOCK=1` | Force placeholder output for every generation. |
| `GS_MODEL_<PROVIDER>_<KIND>` | Override a model id, e.g. `GS_MODEL_GEMINI_IMAGE`, `GS_MODEL_ELEVENLABS_MUSIC`, `GS_MODEL_TRIPO_MODEL3D` (set it to `P2-20260801` to try Tripo P2). Kinds are the `pricing.json` key suffixes. |
| `GS_PLAN_<PROVIDER>` | Plan tier recorded in the licence (e.g. `free`, `paid`) so `licence_check` can flag free-tier output. Default `unknown`. |
| `GS_<PROVIDER>_BASE_URL` | Endpoint override for `GEMINI` (also Lyria), `OPENAI`, `RECRAFT`, `FAL`, `TRIPO`, `MESHY`, `ELEVENLABS`, `STABILITY`; the request path is appended to it. Used by the tests; also a regional or proxy host. |
| `GS_POLL_MS`, `GS_RETRY_BASE_MS` | Poll interval for queued providers (default 3000), retry backoff base (default 800). |

The project root comes from the `project_dir` argument, then `CLAUDE_PROJECT_DIR`, then the working directory; the nearest `.gamestudio/` at or above it is used. Budgets, revenue, `paths.generated_dir`, and `providers` preferences are read from `.gamestudio/config.json`.

## Tools

| Tool | Purpose |
|---|---|
| `gs_status` | Project root, budget, configured providers, mock flag, pricing verification summary, running 3D jobs |
| `image_generate` | 1-4 images via gemini, openai (`quality` low/medium/high), recraft (raster or vector), fal or stability |
| `image_edit` | Instruction edit via gemini or openai |
| `image_postprocess` | Recraft remove_background, vectorize (SVG), upscale; result is derived from the source asset |
| `model3d_generate` | Tripo or Meshy GLB from text or image; `face_limit`, `texture`, `pbr`, `rig` (tripo); runs the whole stage pipeline for `wait_sec` (default 240), then hands back a `task_id` |
| `model3d_status` | Continue and collect a handed-back 3D job (starts the next stage, downloads the final GLB); optional `wait_sec` |
| `audio_music` | ElevenLabs Music, Lyria or Stable Audio; optional `composition_plan` (ElevenLabs) |
| `audio_sfx` | ElevenLabs sound-generation with `loop`, or Stable Audio |
| `audio_voice` | ElevenLabs or Gemini TTS; `lines` for dialogue; `voice_description` designs an ElevenLabs voice |
| `manifest_query`, `manifest_update` | Search and edit `.gamestudio/assets/manifest.json` |
| `licence_check` | Audit licences, provenance and placeholders |
| `budget_status` | Cap, spend, recent ledger |
| `kb_search` | Ranked snippets from `skills/**/*.md` with plugin-relative paths |

## Providers and default models

| Provider | Used for | Request path (default host) | Auth | Default model | Status |
|---|---|---|---|---|---|
| `gemini` | `image_generate`, `image_edit`, `audio_voice` (TTS) | `POST /v1beta/interactions` (generativelanguage.googleapis.com) | `x-goog-api-key` | `gemini-nano-banana-2.1`; TTS `gemini-3.8-flash-tts` | verified |
| `lyria` | `audio_music` | same endpoint and key as gemini | `x-goog-api-key` | `lyria-3.5` (`lyria-3-clip-preview` = fixed 30 s) | verified |
| `openai` | `image_generate`, `image_edit` | `POST /v1/images/generations` (JSON), `/v1/images/edits` (multipart `image[]`) | `Bearer` | `gpt-image-2.5-flare`; edits `gpt-image-2.5-sunburst` | request shapes verified, per-image prices unverified |
| `recraft` | `image_generate`, `image_postprocess` | `POST /v1/images/generations`, `/images/removeBackground`, `/vectorize`, `/crispUpscale` (external.api.recraft.ai) | `Bearer` | `recraftv4_1`; vector `recraftv4_1_vector` | verified |
| `fal` | `image_generate` | queue: `POST /{model}`, poll `status_url`, `GET response_url` (queue.fal.run) | `Key <FAL_KEY>` | `fal-ai/flux/schnell` | model and schema verified; queue REST not re-fetched |
| `stability` | `image_generate`; `audio_music`, `audio_sfx` | image `POST /v2beta/stable-image/generate/core`; audio `POST /v2beta/audio/stable-audio/text-to-audio` then `GET /v2beta/audio/results/{id}` | `Bearer` | `stable-audio-3` | audio verified; image endpoint confirmed, its fields from memory |
| `tripo` | `model3d_generate` | v3: `POST /generation/text-to-model` or `/image-to-model` (after `POST /files`), `GET /tasks/{id}`, `POST /animations/rig-check`, `/animations/rig` (openapi.tripo3d.com/v3) | `Bearer` | `P1-20260311` | verified; USD per credit unverified |
| `meshy` | `model3d_generate` | `POST /openapi/v2/text-to-3d` (preview, refine), `POST /openapi/v1/image-to-3d`, `GET` the same paths + `/{id}` (api.meshy.ai) | `Bearer` | `meshy-7.1` | text flow verified; image flow and USD per credit unverified |
| `elevenlabs` | `audio_music`, `audio_sfx`, `audio_voice` | `POST /v1/music`, `/sound-generation`, `/text-to-speech/{voice_id}`, `/text-to-dialogue`, `/text-to-voice/design` + `/text-to-voice` (api.elevenlabs.io) | `xi-api-key` | `music_v2`, `eleven_text_to_sound_v2`, `eleven_multilingual_v2`, `eleven_v3` | not re-fetched; matches the research notes' quotes of the official pages |

## Behaviour notes

- **Budget.** Cap order: `config.budgets.asset_usd_cap`, `GS_ASSET_BUDGET_USD`, `budget.json cap_usd`. `budgets.per_call_usd_cap` is enforced too. A refusal returns `isError` with `refused: true`, the estimate and the remaining amount, and writes nothing. Estimates use the model's own price and the requested size tier (Gemini 1K/2K), quality (OpenAI) or megapixels (fal); a model id missing from `pricing.json` is estimated at the default model's price and the result says so.
- **Mock mode.** PNG up to 2048 px (valid CRCs, RGBA when `transparent`), 44.1 kHz 16-bit mono WAV (tone for music and sfx, silence for voice, capped at 30 s), a unit-cube GLB with JSON and BIN chunks. Results carry `placeholder: true`, `cost_usd: 0`, and `estimated_usd_if_real`.
- **3D pipelines and chaining.** `model3d_generate` creates the first task, records a job in `<project>/.gamestudio/jobs.json` and polls for up to `wait_sec`. Stages: Tripo `model` then `rig_check` (free) then `rig` when `rig: true`; Meshy text `preview` then `refine` when `texture` or `pbr` (Meshy image input textures in one task). If a task is still running when `wait_sec` ends, the call returns `pending: true` with a stable `task_id` (the first stage's provider id), the current `stage` and the `stages` list. `model3d_status` (same `project_dir`; `wait_sec` makes it keep polling) polls the running stage, starts the next one when it is done, and after the last stage downloads the final GLB and registers it. Repeating the call is safe: a stage is started once, a finished job returns its files again at no cost, and any stage's task id resolves to the job. A task this project has no job record for (made elsewhere) is collected with a single poll and no chaining.
- **3D billing.** Each stage is billed when its task is created, so each stage gets its own ledger entry then; the asset's manifest `cost_usd` is the job total and its own ledger entry has cost 0. The cap check at the start covers the whole pipeline and each later stage is checked again. A failed stage is credited back with a negative ledger entry (Tripo and Meshy refund failed tasks). If a later stage fails or is refused by the budget, or Tripo's rig-check says the model is not riggable, the chain stops and the last model built is returned with a note.
- **Gemini and Lyria.** One `interactions` request per image (`n` runs `n` requests). Images, audio and text come back as `steps[].content[]` blocks; only `model_output` steps are read, so interim "thought" images are ignored. The media type is detected from the bytes. There is no seed parameter (the seed is only recorded) and Lyria takes duration, instrumental and lyrics in the prompt text.
- **Recraft.** Vector comes from a `*_vector` model id (SVG); `size` is the nearest exact size from the model family's documented list for raster models and a `w:h` ratio for vector models; PNG is requested explicitly (the API default is WebP). Utility endpoints reject inputs under 256 px (32 px for upscale), over 4096 px or over 20 MB; the gateway refuses oversize files and out-of-range PNG dimensions before spending.
- **Reliability.** Per-request timeouts, retry with exponential backoff on 429 and 5xx (honours `Retry-After`), SHA-256 of every output in the manifest. Result URLs are downloaded without credentials.
- **Output formats.** ElevenLabs, Lyria and Stable Audio audio is saved as MP3; Gemini TTS as WAV (raw PCM is wrapped); images keep the type the provider returns, detected from the bytes (PNG is requested wherever the API allows, SVG for vector).
- **Licences.** `lib/licences.mjs` records terms per asset and flags: non-commercial terms, free-tier output (error for Recraft, warning elsewhere), ElevenLabs Music when `lifetime_gross_usd` exceeds $500k or `developer_annual_games_revenue_usd` exceeds $1M (warning above 80%), Stability Community licence over $1M, placeholders, missing provenance, and licences outside `config.licence_allowlist`.

## Pricing and verification

`pricing.json` holds the default model ids and list prices checked on 2026-10-20. Each entry has `verified` (true or false), `verified_via` (`docs` = official API documentation fetched that day, `research-notes` = a figure the Oct 2026 research notes cite from an official page that was not re-fetched), and `source` (the page confirming the price) plus `docs` (the page confirming the request shape). `verified: false` marks an estimate: OpenAI per-image prices (token-billed, third-party figures), Tripo and Meshy USD per credit (the credit counts are sourced, the USD per credit is not published or may be outdated), Gemini TTS (derived from token rates), fal and Stability Core prices (from memory) and ElevenLabs dialogue. `gs_status` lists the unverified entries. Override model ids with `GS_MODEL_*`.

## Verification (2026-10-20)

Request shapes, auth headers and response parsing in `providers/*.mjs` were checked against these pages; the findings below are what changed the code or what could not be confirmed.

| Provider | Source | Findings |
|---|---|---|
| Gemini image | https://ai.google.dev/gemini-api/docs/image-generation | Docs use the Interactions API, not `generateContent`: `input` blocks, `response_format {type, aspect_ratio, image_size}` (uppercase `1K`/`2K`/`4K`), results in `steps[].content[]`. `gemini-2.5-flash-image` is legacy (shut down 2026-10-02 per the notes); `gemini-nano-banana-2.1` is the default |
| Lyria | https://ai.google.dev/gemini-api/docs/music-generation | Same endpoint, `response_format {type: "audio"}`, audio block in `steps[]`; no duration, seed or instrumental field |
| Gemini TTS | https://ai.google.dev/gemini-api/docs/speech-generation | `input` as a `user_input` step, `generation_config.speech_config` (array for one voice, `{speakers, mode}` for two), speaker annotations, unary WAV at 24 kHz |
| OpenAI | https://developers.openai.com/api/docs/guides/image-generation | `gpt-image-2.5-flare` and `-sunburst`, `quality` low..max, `output_format`, `background: transparent` (2.5 models), edits as multipart `image[]`, always `b64_json`, no `response_format` |
| Recraft | https://www.recraft.ai/llms-full.txt (docs bundle for https://www.recraft.ai/docs/api-reference) | `recraftv4_1` default, vector by model id (the old `style: vector_illustration` is not documented), raster `size` as exact sizes per model family and ratios for vector, WebP default so `image_format: png`, utilities answer `image.url`, input limits, USD prices |
| fal | https://fal.ai/models/fal-ai/flux/schnell/api | Model live and commercial; input and output schema confirmed. Queue REST paths not re-fetched (page shows the JS client only) |
| Tripo | https://developers.tripo3d.com/assets/developer/tripo-v2-to-v3-migration/SKILL.md, https://developers.tripo3d.com/en/docs/quick-start | v2 `/v2/openapi/task` replaced by v3 per-capability endpoints on `openapi.tripo3d.com/v3`, `GET /tasks/{id}`, `output.model_url`, 5-value status enum, `POST /files` upload with `file_token`, rig-check then rig. P1 `face_limit` 48-20000 and forbidden params. P2-20260801 (native quad) is listed as preview |
| Meshy | https://docs.meshy.ai/en/api/text-to-3d | `ai_model` `meshy-7.1`/`latest`/`meshy-6`; `target_polycount` only applies with `should_remesh: true`; refine needs a SUCCEEDED preview; status values and `model_urls`. Image-to-3D and rigging pages not re-fetched (rigging is humanoid-only, 5 credits per the notes, and is not wired) |
| Stability | https://docs.stability.ai/api-reference/stable-audio/text-to-audio.md, https://docs.stability.ai/api-reference, https://docs.stability.ai/llms.txt | The old reference moved to docs.stability.ai. Stable Audio 3.0 is asynchronous (202 `{id}`, poll `/v2beta/audio/results/{id}`), 8 credits, 1 credit = $0.01, `duration` 1-380 s |
| ElevenLabs | not re-fetched (fetch budget went to the providers with changed APIs) | Shapes match the official reference pages as quoted in the research notes (music, sound-effects, text-to-dialogue, voice design) |

Open questions, none verified: the Gemini image page's REST tab shows requests only, so image results are read from `steps[].content[]` image blocks as its SDK section and the Lyria and TTS `jq` examples describe (the parser also accepts a top-level `outputs[]` list); whether Gemini's Interactions API stores requests server-side by default (the `store` option was not on the fetched pages and is not sent); the Tripo international host (the docs name `openapi.tripo3d.com` for both regions; override with `GS_TRIPO_BASE_URL`); the lifetime of Tripo model URLs (the quick start says 5 minutes, the migration guide 24 hours, so files are downloaded straight away); the Meshy image-to-3d fields and a USD price for Meshy API credits.

## Live smoke test

`test/live-smoke.mjs` checks one provider with your own key. It is not run by `run-tests.mjs` against real hosts.

```
node test/live-smoke.mjs --provider <name> [--kind <kind>] [--yes] [--max-usd <n>] [--timeout-sec <n>]
```

- `--provider` is required and the provider's key must be in the environment (`node test/live-smoke.mjs --help` lists names, key variables and kinds). Keys are read from the environment only.
- **Default is a dry run.** Nothing is sent to the provider. The gateway runs against a local capture port and the script prints the first request it would send (method, URL, headers with the key hidden, body, multipart fields) and the estimated cost from `pricing.json`.
- **`--yes` makes ONE minimal real generation** through the same gateway tool call, into a throwaway project under the OS temp dir whose cap is `--max-usd` (default 1.5 times the estimate, at least $0.25), so the gateway refuses anything bigger. Only that provider's key reaches the gateway, mock mode is off. For 3D providers the one billed task is followed by free polls until the GLB is downloaded or `--timeout-sec` (default 900) passes. It prints the written file, the manifest provenance and the ledger, and keeps the project for inspection.
- Exit codes: 0 success (and every dry run), 1 the call failed or a 3D task was still running at the timeout, 2 usage error or missing key.

| Provider | Kinds (first is default) | Minimal call |
|---|---|---|
| `gemini` | `image`, `tts` | 1K icon image (about $0.034); one short TTS line |
| `lyria` | `music` | `lyria-3-clip-preview`, 30 s ($0.04) |
| `openai` | `image` | 1024 px, `quality: low` (about $0.006) |
| `recraft` | `image`, `vector` | default `recraftv4_1` image ($0.035) or `recraftv4_1_vector` ($0.08) |
| `fal` | `image` | 512 px `fal-ai/flux/schnell` image ($0.003) |
| `stability` | `image`, `audio` | Core image ($0.03) or a 1 s Stable Audio effect ($0.08) |
| `tripo` | `model3d` | text to model, `face_limit` 500, no texture (30 credits) |
| `meshy` | `model3d` | text preview only (20 credits) |
| `elevenlabs` | `sfx`, `tts`, `music`, `dialogue` | 0.5 s effect (about $0.001); short TTS line; 3 s music; two-line dialogue |

Not covered by the smoke script: `image_edit`, `image_postprocess`, the Tripo rig and Meshy refine stages, ElevenLabs voice design. The offline suite covers those request paths against the fake server.

## Tests

`node test/run-tests.mjs` spawns the real server over stdio. Part 1 runs in mock mode. Part 2 starts one local fake HTTP server and runs every real provider request path against it: Gemini image generate and edit, Lyria, Gemini TTS (single, two speakers, raw PCM); OpenAI generate, edit, transparency; Recraft raster, vector, remove background, vectorize, crisp upscale; fal submit, poll, result; Stability Core and Stable Audio (202 then poll); ElevenLabs music (prompt and composition plan), sfx, TTS, dialogue, voice design. Each call asserts the HTTP method, path, auth header shape and body fields against the documented API, then that the response became files, a manifest entry with provenance, and one ledger entry with the right cost. Part 3 covers the 3D pipelines (Tripo create, poll, rig-check, rig, download; Meshy preview, refine, download, image-to-3d), hand-back and chaining through `model3d_status`, the jobs file, idempotency, concurrent status calls, failed and refused stages, refunds and unpriced models. Part 4 runs `live-smoke.mjs` (usage errors, dry run, `--yes` with the cap) against local servers only.

## Layout

```
server.mjs            JSON-RPC loop
lib/tools.mjs         tool schemas, validation, dispatch table
lib/gen.mjs           generation handlers (choose provider, budget guard, commit) and the 3D stage pipeline
lib/jobs.mjs          .gamestudio/jobs.json store and per-job lock
lib/admin.mjs         status, manifest, licence, budget, kb handlers
lib/project.mjs       project root, manifest, ledger, lock
lib/media.mjs         placeholder PNG, WAV, GLB, SVG
lib/licences.mjs      licence defaults and checks
lib/pricing.mjs       model ids and cost estimates
lib/kb.mjs            skill search
lib/util.mjs          errors, JSON IO, HTTP with retry, media sniffing
providers/*.mjs       gemini (also lyria), openai, recraft, fal, tripo, meshy, elevenlabs, stability
test/run-tests.mjs    offline tests (mock mode plus a fake local HTTP server)
test/live-smoke.mjs   opt-in live smoke test for one provider
```
