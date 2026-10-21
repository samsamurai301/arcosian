#!/usr/bin/env node
// studio-gateway: stdio MCP server (newline-delimited JSON-RPC 2.0). Logs go to stderr only; keys are never logged.
import readline from "node:readline";
import { TOOLS, validate, makeCtx } from "./lib/tools.mjs";
import { ToolError, log, redact } from "./lib/util.mjs";

const VERSIONS = ["2026-07-28", "2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05"];
const INFO = { name: "studio-gateway", version: "0.2.0" };
const text = (obj, isError) => ({ content: [{ type: "text", text: redact(typeof obj === "string" ? obj : JSON.stringify(obj)) }], ...(isError ? { isError: true } : {}) });

async function callTool(params) {
  const tool = TOOLS.find((t) => t.name === params?.name);
  if (!tool) return { rpcError: { code: -32602, message: `Unknown tool: ${params?.name}` } };
  const args = params.arguments ?? {};
  const bad = validate(tool.inputSchema, args);
  if (bad) return { result: text({ ok: false, error: `invalid arguments: ${bad}` }, true) };
  try {
    return { result: text(await tool.handler(makeCtx(args, process.env))) };
  } catch (e) {
    if (e instanceof ToolError) return { result: text({ ok: false, error: e.message, ...e.data }, true) };
    log(`tool ${tool.name} crashed: ${e.stack || e}`);
    return { result: text({ ok: false, error: `internal error: ${e.message}` }, true) };
  }
}

async function handle(msg) {
  if (!msg || typeof msg !== "object" || Array.isArray(msg) || typeof msg.method !== "string") {
    return msg && "id" in msg && !("method" in msg) ? null : { jsonrpc: "2.0", id: msg?.id ?? null, error: { code: -32600, message: "Invalid Request" } };
  }
  const { id, method, params } = msg;
  if (id === undefined) return null; // notification: never reply
  const ok = (result) => ({ jsonrpc: "2.0", id, result });
  const err = (code, message) => ({ jsonrpc: "2.0", id, error: { code, message } });
  switch (method) {
    case "initialize": {
      const want = params?.protocolVersion;
      return ok({ protocolVersion: VERSIONS.includes(want) ? want : "2025-06-18", capabilities: { tools: {} }, serverInfo: INFO,
        instructions: "Asset and audio gateway: call gs_status first. Generations are written into the project, tracked in the manifest and budget ledger; without provider keys they return placeholders." });
    }
    case "ping": return ok({});
    case "tools/list": return ok({ tools: TOOLS.map(({ name, description, inputSchema }) => ({ name, description, inputSchema })) });
    case "tools/call": {
      const r = await callTool(params);
      return r.rpcError ? err(r.rpcError.code, r.rpcError.message) : ok(r.result);
    }
    default: return err(-32601, `Method not found: ${method}`);
  }
}

const pending = new Set();
const rl = readline.createInterface({ input: process.stdin, crlfDelay: Infinity });
rl.on("line", (line) => {
  if (!line.trim()) return;
  let msg;
  try { msg = JSON.parse(line); } catch { process.stdout.write(JSON.stringify({ jsonrpc: "2.0", id: null, error: { code: -32700, message: "Parse error" } }) + "\n"); return; }
  const job = handle(msg)
    .then((res) => { if (res) process.stdout.write(JSON.stringify(res) + "\n"); })
    .catch((e) => {
      log(`handler crashed: ${e.stack || e}`);
      if (msg && msg.id !== undefined) process.stdout.write(JSON.stringify({ jsonrpc: "2.0", id: msg.id, error: { code: -32603, message: "Internal error" } }) + "\n");
    })
    .finally(() => pending.delete(job));
  pending.add(job);
});
rl.on("close", () => Promise.all([...pending]).then(() => process.exit(0)));
log(`ready (${TOOLS.length} tools, mock=${process.env.GS_MOCK === "1"})`);
