#!/usr/bin/env node
// SessionStart hook: hands this plugin's options to the GDScript bridge. Claude Code exports plugin options to hooks
// (CLAUDE_PLUGIN_OPTION_*) but not to language servers, and in Claude Code 2.1.267 a ${user_config.*} reference in
// .lsp.json keeps the server from loading at all. The bridge reads the file written here. Prints nothing.
import fs from "node:fs";
import path from "node:path";

const dir = process.env.CLAUDE_PLUGIN_DATA;
if (dir) {
  const options = {};
  for (const key of ["godot_bin", "godot_lsp_port"]) {
    const v = (process.env[`CLAUDE_PLUGIN_OPTION_${key.toUpperCase()}`] || "").trim();
    if (v && !v.includes("${")) options[key] = v;
  }
  try {
    fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(path.join(dir, "options.json"), JSON.stringify(options) + "\n");
  } catch {} // never block a session over this
}
