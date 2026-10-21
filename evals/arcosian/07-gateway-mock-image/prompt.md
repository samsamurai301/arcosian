---
tags: [gateway,assets,mcp]
runs: 2
max_turns: 15
timeout_seconds: 600
allowed_tools: [Read, Write, Edit, Glob, Grep, Skill, Bash]
---
Use the studio-gateway MCP tool image_generate in dry-run/mock mode (no provider keys are configured; set dry_run true) to create one placeholder app icon: a flat-style blue pebble on a cream background, 1024x1024. Then use manifest_query to confirm the asset is in the manifest. Do not call any other generation tool. Reply with the asset id and path.
