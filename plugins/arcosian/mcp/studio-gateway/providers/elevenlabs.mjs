// ElevenLabs (xi-api-key header, https://api.elevenlabs.io/v1, MP3 output via ?output_format=mp3_44100_128):
//   POST /music                  {prompt | composition_plan, music_length_ms 3000-600000, model_id music_v2, force_instrumental}
//   POST /sound-generation       {text, duration_seconds 0.5-30, loop (eleven_text_to_sound_v2 only), model_id}
//   POST /text-to-speech/{voice} {text, model_id}
//   POST /text-to-dialogue       {inputs: [{text, voice_id}], model_id eleven_v3}
//   POST /text-to-voice/design   {voice_description 20-1000 chars, auto_generate_text} -> previews[].generated_voice_id
//   POST /text-to-voice          {voice_name, voice_description, generated_voice_id} -> voice_id
// Not re-fetched on 2026-10-20 (the fetch budget went to the providers with changed APIs): these shapes match the official
// ElevenLabs reference pages quoted in the Oct 2026 research notes (music, sound-effects, text-to-dialogue, voice design).
import { http, baseUrl, ToolError } from "../lib/util.mjs";

export const DEFAULT_BASE = "https://api.elevenlabs.io/v1";
const FMT = "output_format=mp3_44100_128";
const call = (key, path, body) =>
  http(`${baseUrl("elevenlabs", DEFAULT_BASE)}${path}`, {
    method: "POST", headers: { "xi-api-key": key, "content-type": "application/json" }, body: JSON.stringify(body), expect: path.startsWith("/text-to-voice") ? "json" : "buffer", timeoutMs: 300000,
  });
const mp3 = (bytes) => [{ bytes, ext: "mp3" }];

export async function music({ key, model, prompt, duration_sec, instrumental = true, composition_plan }) {
  const body = composition_plan ? { composition_plan, model_id: model } : { prompt, music_length_ms: Math.round(duration_sec * 1000), model_id: model, force_instrumental: instrumental };
  return mp3(await call(key, `/music?${FMT}`, body));
}
export async function sfx({ key, model, prompt, duration_sec, loop }) {
  const body = { text: prompt, model_id: model, loop: !!loop };
  if (duration_sec) body.duration_seconds = duration_sec;
  return mp3(await call(key, `/sound-generation?${FMT}`, body));
}
export async function tts({ key, model, text, voice_id }) {
  return mp3(await call(key, `/text-to-speech/${encodeURIComponent(voice_id)}?${FMT}`, { text, model_id: model }));
}
export async function dialogue({ key, model, lines }) {
  return mp3(await call(key, `/text-to-dialogue?${FMT}`, { inputs: lines.map((l) => ({ text: l.text, voice_id: l.voice_id })), model_id: model }));
}
// Design a voice from a description (20-1000 chars) and save it; returns a voice_id.
export async function designVoice({ key, description, name }) {
  const d = await call(key, "/text-to-voice/design", { voice_description: description, auto_generate_text: true });
  const id = d.previews?.[0]?.generated_voice_id;
  if (!id) throw new ToolError("elevenlabs voice design returned no preview");
  const v = await call(key, "/text-to-voice", { voice_name: name, voice_description: description, generated_voice_id: id });
  if (!v.voice_id) throw new ToolError("elevenlabs voice creation returned no voice_id");
  return v.voice_id;
}
