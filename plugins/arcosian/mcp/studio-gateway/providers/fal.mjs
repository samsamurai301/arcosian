// fal.ai queue API: POST {queue}/{model} (Authorization: Key <FAL_KEY>) -> {request_id, status_url, response_url};
// poll status_url until status is COMPLETED; GET response_url for the result; download images[].url.
// Model schema (fal-ai/flux/schnell: prompt, image_size {width,height}, num_images, seed, output_format; images[{url, content_type}])
// confirmed on fal.ai/models/fal-ai/flux/schnell/api on 2026-10-20. The queue REST paths below are fal's documented queue
// protocol but were not re-fetched (that page shows the JS client only); the returned status_url/response_url are used as-is.
import { http, baseUrl, download, sleep, pollMs, sniffExt, ToolError } from "../lib/util.mjs";

export const DEFAULT_BASE = "https://queue.fal.run";

export async function image({ key, model, prompt, n = 1, width, height, seed, timeoutSec = 180 }) {
  const headers = { authorization: `Key ${key}`, "content-type": "application/json" };
  const input = { prompt, num_images: n, image_size: { width, height }, output_format: "png" };
  if (seed !== undefined && seed !== null) input.seed = seed;
  const base = baseUrl("fal", DEFAULT_BASE);
  const job = await http(`${base}/${model}`, { method: "POST", headers, body: JSON.stringify(input) });
  if (!job?.request_id && !job?.status_url) throw new ToolError("fal queue returned no request_id");
  const app = model.split("/").slice(0, 2).join("/"); // status and result paths drop the sub-path of the model id
  const statusUrl = job.status_url || `${base}/${app}/requests/${job.request_id}/status`;
  const resultUrl = job.response_url || `${base}/${app}/requests/${job.request_id}`;
  const deadline = Date.now() + timeoutSec * 1000;
  for (;;) {
    const st = await http(statusUrl, { headers });
    if (st.status === "COMPLETED") {
      if (st.error) throw new ToolError(`fal job failed: ${typeof st.error === "string" ? st.error : JSON.stringify(st.error).slice(0, 200)}`);
      break;
    }
    if (/FAIL|ERROR/i.test(st.status || "")) throw new ToolError(`fal job failed: ${st.status}`);
    if (Date.now() > deadline) throw new ToolError(`fal job ${job.request_id} still ${st.status} after ${timeoutSec}s`);
    await sleep(pollMs());
  }
  const res = await http(resultUrl, { headers });
  const urls = (res.images || []).map((i) => i && i.url).filter(Boolean);
  if (!urls.length) throw new ToolError("fal returned no images");
  return Promise.all(urls.map(async (u) => { const bytes = await download(u); return { bytes, ext: sniffExt(bytes, "png") }; }));
}
