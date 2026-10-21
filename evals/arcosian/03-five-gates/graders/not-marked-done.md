---
type: regex
target: {source: file, path: .gamestudio/features.json}
pattern: '"status"\s*:\s*"done"'
match: not_contains
---
