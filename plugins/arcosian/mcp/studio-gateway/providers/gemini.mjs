// Gemini API, Interactions endpoint (POST {base}/interactions): Nano Banana image generate/edit, Lyria music, Gemini TTS.
// Request and response shapes follow the ai.google.dev docs for image-generation, music-generation and speech-generation
// (verified 2026-10-20). Auth is the x-goog-api-key header. Results come back as steps[type=model_output].content[] blocks:
// {type:"text", text} or {type:"image"|"audio", data: <base64>}.
import { http, baseUrl, ToolError, sniffExt } from "../lib/util.mjs";
import { wavFromPcm } from "../lib/media.mjs";

export const DEFAULT_BASE = "https://generativelanguage.googleapis.com/v1beta";

const call = (key, body) =>
  http(`${baseUrl("gemini", DEFAULT_BASE)}/interactions`, {
    method: "POST", headers: { "x-goog-api-key": key, "content-type": "application/json" }, body: JSON.stringify(body), timeoutMs: 240000,
  });

// Only model_output steps are results: "thought" steps may hold interim images (not charged, not the answer).
// Falls back to a top-level outputs[] list (earlier beta shape).
function blocks(res) {
  const out = (Array.isArray(res?.steps) ? res.steps : []).filter((s) => s && s.type === "model_output").flatMap((s) => (Array.isArray(s.content) ? s.content : []));
  return out.length ? out : (Array.isArray(res?.outputs) ? res.outputs : []);
}
// Last block of a media type (the docs' output_image / output_audio accessors return the last one).
function lastMedia(res, type) {
  const all = blocks(res), b = all.filter((x) => x && x.type === type && typeof x.data === "string" && x.data.length).at(-1);
  if (b) return { bytes: Buffer.from(b.data, "base64"), mime: b.mime_type || b.mimeType || "" };
  const said = all.filter((x) => x && x.type === "text" && x.text).map((x) => x.text).join(" ").slice(0, 200);
  throw new ToolError(`gemini returned no ${type} (status: ${res?.status || "unknown"}${res?.error?.message ? `, error: ${res.error.message}` : ""}${said ? `, text: "${said}"` : ""})`);
}

// aspect: "16:9" style ratio; tier: "1K" | "2K" | "4K" (uppercase K); images: [{mime, data(base64)}] references or the edit source.
// One image per request: n > 1 runs n requests.
export async function image({ key, model, prompt, n = 1, aspect, tier, images = [] }) {
  const one = async () => {
    const response_format = { type: "image" };
    if (aspect) response_format.aspect_ratio = aspect;
    if (tier) response_format.image_size = tier;
    const input = [{ type: "text", text: prompt }, ...images.map((i) => ({ type: "image", mime_type: i.mime, data: i.data }))];
    const { bytes } = lastMedia(await call(key, { model, input, response_format }), "image");
    return { bytes, ext: sniffExt(bytes, "png") };
  };
  return Promise.all(Array.from({ length: n }, one));
}

// Lyria: no duration, instrumental or lyrics fields; all of that goes in the prompt. MP3 unless response_format asks for WAV.
export async function music({ key, model, prompt }) {
  const { bytes } = lastMedia(await call(key, { model, input: prompt, response_format: { type: "audio" } }), "audio");
  return [{ bytes, ext: sniffExt(bytes, "mp3") }];
}

// lines: [{text, voice_id?}] (at most 2 distinct voices per request); otherwise one text with one voice (a prebuilt name such as Kore).
export async function tts({ key, model, text, voice = "Kore", lines }) {
  const named = lines && lines.length ? lines : null;
  const voices = named ? [...new Set(named.map((l) => l.voice_id || voice))] : [voice];
  if (voices.length > 2) throw new ToolError("gemini TTS supports at most 2 speakers in one call; use provider elevenlabs for more");
  let content, speech;
  if (!named || voices.length === 1) {
    content = [{ type: "text", text: named ? named.map((l) => l.text).join("\n") : text }];
    speech = [{ voice: voices[0] }];
  } else {
    content = named.map((l) => ({ type: "text", text: l.text, annotations: [{ type: "speech_metadata", speaker: `Speaker${voices.indexOf(l.voice_id || voice) + 1}` }] }));
    speech = { speakers: voices.map((v, i) => ({ speaker: `Speaker${i + 1}`, voice: v })), mode: "conversational" };
  }
  const res = await call(key, { model, input: [{ type: "user_input", content }], response_format: { type: "audio" }, generation_config: { speech_config: speech } });
  const { bytes, mime } = lastMedia(res, "audio");
  const ext = sniffExt(bytes);
  if (ext === "wav" || ext === "mp3") return [{ bytes, ext }]; // unary default is audio/wav with a RIFF header (24 kHz mono 16-bit)
  const rate = parseInt((mime.match(/rate=(\d+)/) || [])[1] || "24000", 10); // headerless audio/l16 PCM
  return [{ bytes: wavFromPcm(bytes, rate), ext: "wav" }];
}
