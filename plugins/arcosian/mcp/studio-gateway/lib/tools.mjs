// Tool registry: names, descriptions, JSON Schemas, handlers, argument validation.
import * as gen from "./gen.mjs";
import * as adm from "./admin.mjs";
import { openProject } from "./project.mjs";

const str = (description, extra = {}) => ({ type: "string", description, ...extra });
const obj = (properties, required = []) => ({ type: "object", properties, required, additionalProperties: false });
const common = { project_dir: str("Project directory; default CLAUDE_PROJECT_DIR or the working directory. The nearest .gamestudio/ at or above it is used.") };
const PROV = ["auto", "gemini", "openai", "recraft", "fal", "stability"];
const STATUS = ["placeholder", "candidate", "approved", "rejected", "final"];
const GEN = "Writes files under the project's generated_dir, appends a manifest entry (status candidate) and a budget ledger entry, and refuses calls that would exceed the remaining cap. Without a provider key, with GS_MOCK=1 or dry_run it returns valid placeholder files at cost 0.";
const dry = { dry_run: { type: "boolean", description: "Force a free placeholder result without calling any provider." } };
const outs = { out_dir: str("Output directory inside the project (default config paths.generated_dir)."), id_prefix: str("Prefix for the asset ids, e.g. hero-idle.") };

export const TOOLS = [
  { name: "gs_status", description: "Show the resolved project root, budget, which providers have API keys configured, and whether mock mode is forced. Call first to see what is available.",
    inputSchema: obj({ ...common }), handler: adm.gsStatus },
  { name: "image_generate", description: `Generate 1-4 images (2D art, sprites, UI, icons, backgrounds, textures). ${GEN}`,
    inputSchema: obj({ ...common, prompt: str("Image prompt."), kind: str("Asset kind recorded in the manifest.", { enum: ["sprite", "spritesheet", "ui", "icon", "background", "tileset", "texture", "other"] }),
      provider: str("Provider; auto picks config.providers.image or the first configured one.", { enum: PROV }), model: str("Model id override (default from pricing.json or GS_MODEL_<PROVIDER>_IMAGE). A recraft model containing 'vector' returns SVG."),
      size: str("'1024' or 'WxH' (placeholders up to 2048)."), n: { type: "integer", minimum: 1, maximum: 4, description: "Number of candidates (default 1)." },
      references: { type: "array", items: { type: "string" }, description: "Reference image paths (gemini: up to 14 png/jpeg/webp; openai: via the edits endpoint). Other providers ignore them." }, quality: { type: "string", enum: ["low", "medium", "high"], description: "OpenAI only: image quality tier (default medium); drives cost." }, transparent: { type: "boolean", description: "Request a transparent background (native on openai; otherwise run image_postprocess remove_background)." },
      seed: { type: "integer", description: "Seed where the provider supports it (recraft, fal, stability; recorded only for gemini and openai)." }, style_ref: str("Path of a style reference image, also stored in the manifest."), ...outs, ...dry }, ["prompt", "kind"]), handler: gen.imageGenerate },
  { name: "image_edit", description: `Edit an existing image with a text instruction (gemini or openai). ${GEN}`,
    inputSchema: obj({ ...common, source: str("Path of the image to edit."), prompt: str("Edit instruction."), references: { type: "array", items: { type: "string" }, description: "Extra reference image paths." },
      provider: str("Provider.", { enum: ["auto", "gemini", "openai"] }), model: str("Model id override."), n: { type: "integer", minimum: 1, maximum: 4 }, quality: { type: "string", enum: ["low", "medium", "high"], description: "OpenAI only: image quality tier (default medium); drives cost." }, ...outs, ...dry }, ["source", "prompt"]), handler: gen.imageEdit },
  { name: "image_postprocess", description: `Post-process an image with Recraft: remove_background, vectorize (SVG) or upscale (crisp). The result is a new manifest entry derived from the source. ${GEN}`,
    inputSchema: obj({ ...common, path: str("Path of the source image."), op: str("Operation.", { enum: ["remove_background", "vectorize", "upscale"] }), provider: str("Provider.", { enum: ["auto", "recraft"] }), ...outs, ...dry }, ["path", "op"]), handler: gen.imagePostprocess },
  { name: "model3d_generate", description: `Generate a 3D model (GLB) from a prompt or an image with Tripo or Meshy. Multi-stage jobs (Tripo rig = rig-check then rig; Meshy text with texture = preview then refine) run as a pipeline: the call waits up to wait_sec and, if a task is still running, returns a task_id that model3d_status continues through the remaining stages until the final GLB is downloaded. Each stage is billed when its task is created. face_limit maps to the provider polygon target. ${GEN}`,
    inputSchema: obj({ ...common, prompt: str("Text prompt (or use image)."), image: str("Path of an input image (or use prompt)."), provider: str("3D provider.", { enum: ["tripo", "meshy"] }),
      face_limit: { type: "integer", minimum: 48, maximum: 300000, description: "Target face / polycount; keep mobile characters low (about 2k-10k). Tripo P1 accepts 48-20000, Meshy 100-300000." }, texture: { type: "boolean", description: "Textured model (tripo: standard texture; meshy text: a refine stage after the preview)." }, pbr: { type: "boolean", description: "PBR maps (implies texture)." }, rig: { type: "boolean", description: "Auto-rig (tripo only): rig-check, then rig with the Mixamo skeleton spec. A model that is not riggable is returned unrigged." },
      wait_sec: { type: "number", minimum: 0, maximum: 3600, description: "Seconds to wait for completion (default 240)." }, ...outs, ...dry }, ["provider"]), handler: gen.model3dGenerate },
  { name: "model3d_status", description: "Continue and collect a 3D job started by model3d_generate: polls the running stage, starts the next one (rig, refine; billed at creation, recorded in .gamestudio/jobs.json) and, when the last stage is done, downloads the GLB and records it in the manifest. Safe to call repeatedly; a finished job returns its files again at no cost. Use the same project_dir as the generate call.",
    inputSchema: obj({ ...common, provider: str("3D provider.", { enum: ["tripo", "meshy"] }), task_id: str("task_id returned by model3d_generate (a later stage id also works)."), wait_sec: { type: "number", minimum: 0, maximum: 3600, description: "Seconds to keep polling and chaining stages before returning (default 0: one check)." }, out_dir: outs.out_dir, id_prefix: outs.id_prefix }, ["provider", "task_id"]), handler: gen.model3dStatus },
  { name: "audio_music", description: `Generate a music track (ElevenLabs Music, Google Lyria or Stability Stable Audio). ElevenLabs Music has revenue-limited indie licence terms: see licence_check. ${GEN}`,
    inputSchema: obj({ ...common, prompt: str("Style, mood, instruments, tempo."), duration_sec: { type: "number", minimum: 3, maximum: 600 }, instrumental: { type: "boolean", description: "Default true." },
      provider: str("Provider.", { enum: ["auto", "elevenlabs", "lyria", "stability"] }), model: str("Model id override (lyria-3-clip-preview makes fixed 30 s clips)."), composition_plan: { type: "object", description: "ElevenLabs section plan (intro/loop body/outro); replaces prompt and duration." }, id_prefix: outs.id_prefix, out_dir: outs.out_dir, ...dry }, ["prompt", "duration_sec"]), handler: gen.audioMusic },
  { name: "audio_sfx", description: `Generate a sound effect or ambience (ElevenLabs 0.5-30 s with optional seamless loop, or Stability Stable Audio for textured beds). ${GEN}`,
    inputSchema: obj({ ...common, prompt: str("What the sound is."), duration_sec: { type: "number", minimum: 0.5, maximum: 30 }, loop: { type: "boolean", description: "Seamless loop (ambiences, engine hums)." },
      provider: str("Provider.", { enum: ["auto", "elevenlabs", "stability"] }), model: str("Model id override."), id_prefix: outs.id_prefix, out_dir: outs.out_dir, ...dry }, ["prompt"]), handler: gen.audioSfx },
  { name: "audio_voice", description: `Synthesize speech or dialogue (ElevenLabs or Gemini TTS). Give text, or lines [{text, voice_id}] for multi-speaker dialogue. voice_description designs a new ElevenLabs voice. ${GEN}`,
    inputSchema: obj({ ...common, text: str("Text to speak."), voice_id: str("Voice id (ElevenLabs voice_id or Gemini voice name such as Kore)."), voice_description: str("ElevenLabs only: describe a voice to design (20-1000 chars)."),
      provider: str("Provider.", { enum: ["auto", "elevenlabs", "gemini"] }), model: str("Model id override."), lines: { type: "array", items: obj({ text: str("Line text."), voice_id: str("Voice for this line.") }, ["text"]), description: "Dialogue lines." }, id_prefix: outs.id_prefix, out_dir: outs.out_dir, ...dry }), handler: gen.audioVoice },
  { name: "manifest_query", description: "Search .gamestudio/assets/manifest.json by kind, status, provider or free text (id, path, prompt, notes). Returns the most recent matches.",
    inputSchema: obj({ ...common, kind: str("Asset kind."), status: str("Status.", { enum: STATUS }), provider: str("Provider id."), text: str("Substring to match."), limit: { type: "integer", minimum: 1, maximum: 200 } }), handler: adm.manifestQuery },
  { name: "manifest_update", description: "Update a manifest entry: status (candidate/approved/rejected/final), approved_by, notes, or merge licence fields (terms, plan_tier, commercial_ok, attribution, restrictions).",
    inputSchema: obj({ ...common, asset_id: str("Asset id."), status: str("New status.", { enum: STATUS }), approved_by: str("Who approved."), notes: str("Notes."), licence: { type: "object", description: "Licence fields to merge." } }, ["asset_id"]), handler: adm.manifestUpdate },
  { name: "licence_check", description: "Audit one asset or the whole manifest for non-commercial terms, free-tier ownership problems, revenue-threshold licences (e.g. ElevenLabs Music indie limits against config.revenue), placeholders and missing provenance.",
    inputSchema: obj({ ...common, asset_id: str("Asset id; omit to check every asset.") }), handler: adm.licenceCheck },
  { name: "budget_status", description: "Show the asset budget cap, spend, remaining amount and recent ledger entries.", inputSchema: obj({ ...common }), handler: adm.budgetStatus },
  { name: "kb_search", description: "Search the arcosian skill library (PLUGIN/skills/**/*.md) and return ranked snippets with plugin-relative file paths.",
    inputSchema: obj({ query: str("Search terms."), skill: str("Restrict to one skill directory name."), limit: { type: "integer", minimum: 1, maximum: 20 } }, ["query"]), handler: adm.kbSearch },
];

// Minimal JSON Schema check: required, type, enum, min/max, nested array items/objects. Returns an error string or null.
export function validate(schema, v, at = "arguments") {
  const t = schema.type;
  const ok = { string: typeof v === "string", number: typeof v === "number" && Number.isFinite(v), integer: Number.isInteger(v), boolean: typeof v === "boolean",
    array: Array.isArray(v), object: v !== null && typeof v === "object" && !Array.isArray(v) }[t];
  if (t && !ok) return `${at} must be ${t}`;
  if (schema.enum && !schema.enum.includes(v)) return `${at} must be one of ${schema.enum.join(", ")}`;
  if (typeof v === "number" && ((schema.minimum !== undefined && v < schema.minimum) || (schema.maximum !== undefined && v > schema.maximum))) return `${at} out of range ${schema.minimum ?? ""}..${schema.maximum ?? ""}`;
  if (t === "array" && schema.items) for (let i = 0; i < v.length; i++) { const e = validate(schema.items, v[i], `${at}[${i}]`); if (e) return e; }
  if (t === "object" && schema.properties) {
    for (const r of schema.required || []) if (v[r] === undefined) return `missing required ${at === "arguments" ? "" : at + "."}${r}`;
    for (const [k, x] of Object.entries(v)) {
      if (!schema.properties[k]) { if (schema.additionalProperties === false) return `unknown ${at === "arguments" ? "" : at + "."}argument ${k}`; continue; }
      const e = validate(schema.properties[k], x, at === "arguments" ? k : `${at}.${k}`); if (e) return e;
    }
  }
  return null;
}

export function makeCtx(args, env) {
  const p = openProject(args, env);
  return { a: args, env, p, cfg: p.config(), forceMock: env.GS_MOCK === "1" || args.dry_run === true };
}
