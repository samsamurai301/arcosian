// kb_search: ranked snippets from PLUGIN/skills/**/*.md (TF-IDF over heading sections).
import fs from "node:fs";
import path from "node:path";

const STOP = new Set("a an and are as at be by for from how in is it of on or that the this to what when with do does can i we you".split(" "));
const tok = (s) => (String(s).toLowerCase().match(/[a-z0-9][a-z0-9_-]+/g) || []).filter((w) => !STOP.has(w));
let cache = { root: null, chunks: [] };

export function kbRoot(env, serverDir) {
  const cands = [env.GS_PLUGIN_ROOT && path.join(env.GS_PLUGIN_ROOT, "skills"), path.resolve(serverDir, "../../skills")].filter(Boolean);
  return cands.find((c) => { try { return fs.statSync(c).isDirectory(); } catch { return false; } }) || null;
}
function walk(dir, out = []) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    if (e.isDirectory()) walk(p, out);
    else if (e.name.endsWith(".md")) out.push(p);
  }
  return out;
}
function build(root) {
  const chunks = [];
  for (const file of walk(root)) {
    const rel = path.relative(path.dirname(root), file).split(path.sep).join("/");
    const skill = rel.split("/")[1];
    let heading = path.basename(file), buf = [];
    const flush = () => {
      const text = buf.join("\n").trim();
      if (text) for (let i = 0; i < text.length; i += 1500) {
        const part = text.slice(i, i + 1500);
        const tf = new Map();
        for (const w of tok(heading + " " + part)) tf.set(w, (tf.get(w) || 0) + 1);
        chunks.push({ file: rel, skill, heading, text: part, tf, head: new Set(tok(heading)) });
      }
      buf = [];
    };
    for (const line of fs.readFileSync(file, "utf8").split("\n")) {
      const m = line.match(/^#{1,4}\s+(.*)/);
      if (m) { flush(); heading = m[1].trim(); } else buf.push(line);
    }
    flush();
  }
  return chunks;
}
export function search(root, query, { skill, limit = 5 } = {}) {
  if (!root) return [];
  if (cache.root !== root) cache = { root, chunks: build(root) };
  const terms = [...new Set(tok(query))];
  if (!terms.length) return [];
  const pool = cache.chunks;
  const idf = (t) => Math.log(1 + pool.length / (1 + pool.filter((c) => c.tf.has(t)).length));
  const q = String(query).toLowerCase().trim();
  const scored = [];
  for (const c of pool) {
    if (skill && c.skill !== skill) continue;
    let s = 0;
    for (const t of terms) if (c.tf.has(t)) s += idf(t) * (1 + Math.log(c.tf.get(t))) * (c.head.has(t) ? 2 : 1);
    if (s > 0 && q.includes(" ") && c.text.toLowerCase().includes(q)) s *= 1.5;
    if (s > 0) scored.push({ c, s });
  }
  scored.sort((a, b) => b.s - a.s);
  return scored.slice(0, limit).map(({ c, s }) => {
    const low = c.text.toLowerCase();
    const at = Math.max(0, Math.min(...terms.map((t) => low.indexOf(t)).filter((i) => i >= 0)) - 60);
    return { file: c.file, skill: c.skill, heading: c.heading, score: Math.round(s * 100) / 100, snippet: c.text.slice(at, at + 360).replace(/\s+/g, " ").trim() };
  });
}
