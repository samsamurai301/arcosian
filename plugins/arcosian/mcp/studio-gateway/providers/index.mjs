// Provider registry. "lyria" is the Gemini-hosted music model and shares the Gemini key and endpoint.
import * as gemini from "./gemini.mjs";
import * as openai from "./openai.mjs";
import * as recraft from "./recraft.mjs";
import * as fal from "./fal.mjs";
import * as tripo from "./tripo.mjs";
import * as meshy from "./meshy.mjs";
import * as elevenlabs from "./elevenlabs.mjs";
import * as stability from "./stability.mjs";
import { baseUrl } from "../lib/util.mjs";

export const MODULES = { gemini, lyria: gemini, openai, recraft, fal, tripo, meshy, elevenlabs, stability };
export const ENV_KEY = { gemini: "GEMINI_API_KEY", lyria: "GEMINI_API_KEY", openai: "OPENAI_API_KEY", recraft: "RECRAFT_API_KEY", fal: "FAL_KEY",
  tripo: "TRIPO_API_KEY", meshy: "MESHY_API_KEY", elevenlabs: "ELEVENLABS_API_KEY", stability: "STABILITY_API_KEY" };
export const keyFor = (provider) => (process.env[ENV_KEY[provider]] || "").trim();
export const configured = () => Object.fromEntries(Object.keys(ENV_KEY).filter((p) => p !== "lyria").map((p) => [p, !!keyFor(p)]));
// Base URL a provider call goes to (GS_<PROVIDER>_BASE_URL override or the documented default).
export const baseFor = (provider) => baseUrl(provider === "lyria" ? "gemini" : provider, MODULES[provider].DEFAULT_BASE);
