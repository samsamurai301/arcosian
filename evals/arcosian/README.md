# Arcosian evals

Eight end-to-end cases for `claude plugin eval`. Each case is a directory with `prompt.md` (the task, plus run settings), `graders/*.md` (one grader per file), and `case.yaml` plus `scaffold.sh` when the run needs a project to start from. Scaffolds call `python3 <plugin-root>/scripts/gs.py init`, then add only the state the case needs. They locate the plugin from their own path (`../../../plugins/arcosian`), so run them from a checkout of this repository, and they write the plugin root to `plugin_root.txt` for the agent.

| Case | Checks |
|---|---|
| `01-concept-cards` | Brief to three concept cards, schema-valid, recommendation |
| `02-design-contract` | Contract filled, `gs.py validate` output saved and clean |
| `03-five-gates` | Refuses to pass F001 without gate evidence |
| `04-deconstruct-royal-match` | Deconstruction JSON, valid, specific |
| `05-economy-sim` | Economy model, `economy_sim.py` run, grounded findings |
| `06-compliance-preflight` | Godot project with target SDK 34 flagged as a blocker |
| `07-gateway-mock-image` | `image_generate` in mock mode creates a manifest entry at zero cost |
| `08-principal-next-step` | Principal picks the right next step in a half-built project |

## Run

Scaffolds run author-supplied bash and the cases need Bash and Write, so both are opt-in flags. Pin the model and cap the spend:

```
claude plugin eval plugins/arcosian \
  --eval-dir evals/arcosian \
  --scaffold \
  --allow-tools Bash Write Edit "mcp__plugin_arcosian_studio-gateway__*" \
  --model claude-sonnet-5-5 \
  --judge-model haiku \
  --runs 2 \
  --max-cost-usd 15 \
  --no-publish
```

- `--max-cost-usd` aborts with exit 2 and reports partial results when hit. Start low and raise it.
- `--case '0[1-3]*'` runs a subset; `--tag gates` filters by tag.
- `--ablation none` skips the no-plugin baseline arm and roughly halves the cost. With the default `with-without`, the report shows WITH, W/OUT and the delta.
- `--threshold 0.8` sets the pass bar (default 1.0, exit 1 below it). The `llm` graders make 1.0 unrealistic.
- Add `--mocks off` only if the gateway case should spawn the real server; keys are empty in an eval, so it still writes placeholders.
- Results land in `evals/results/<timestamp>/` (`aggregate-result.json`, `report.html`). Add `--json out.json` for CI.

## Writing and grading notes

- Deterministic checks sit in the run itself: the prompt asks for a command to be run and its output written to a file, a `regex` or `file_exists` grader checks that file, and `tool_used` asserts the command ran.
- `llm` graders are reserved for quality (concept distinctness, findings grounded in numbers, refusal reasoning).
- Case 07 names the MCP tool as `mcp__plugin_arcosian_studio-gateway__image_generate`. If your Claude Code version names plugin MCP tools differently, update that grader.
- Hooks and real MCP servers run outside the agent sandbox, so treat scores as advisory unless the run is in an isolated container or CI runner.
- Cost scales with cases x runs x arms; the prompts set `runs: 2` and tight `max_turns`.
- Validate structure without running anything: `claude plugin validate plugins/arcosian`.

## Reading a result

- A case fails when any weighted grader fails; per-grader verdicts are in `report.html`. Fix the prompt or plugin before loosening a grader.
- Case 03 is the most important: if it passes with the plugin and fails without, the five-gate hooks and `gs.py feature pass` are doing their job.
- Case 06 should fail the pre-flight on purpose; the grader checks that the assistant reports the failure, not that the project is clean.
- Case 08's scaffold leaves F001 with only the static gate, so the correct answer is to finish F001, not to start F003.
- After editing a case, re-run just that case with `--case` and `--runs 1` to keep the loop cheap.

