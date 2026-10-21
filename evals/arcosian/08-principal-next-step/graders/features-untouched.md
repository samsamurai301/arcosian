---
type: regex
target: {source: file, path: .gamestudio/features.json}
pattern: '"passes"\s*:\s*true'
match: not_contains
---
