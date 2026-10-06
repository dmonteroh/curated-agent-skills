# Task quality evaluation

`performance run` measures task quality with and without a skill on Claude and Codex. It reuses the package's isolation, trace parser, and blind judge. Each skill supplies task data to the same runner.

Activation and quality answer separate questions. `activation run` measures whether a skill loads. `performance run` measures what changes in the resulting work.

## Run a comparison

Preview a writing task without making vendor calls:

```bash
python3 scripts/auditing/skill-eval.py performance run \
  --skill writing-style \
  --suite scripts/auditing/skill_eval/examples/text-task.json \
  --dry-run
```

Run the planned comparison when vendor calls are authorized:

```bash
python3 scripts/auditing/skill-eval.py performance run \
  --skill writing-style \
  --suite scripts/auditing/skill_eval/examples/text-task.json \
  --models claude=haiku,codex=gpt-5.6-luna \
  --repeats 4 --max-calls 82
```

A second example uses the package's neutral git fixture:

```bash
python3 scripts/auditing/skill-eval.py performance run \
  --skill pr-description \
  --suite scripts/auditing/skill_eval/examples/git-task.json \
  --dry-run
```

These examples demonstrate the format. They are visible development tasks, and one task cannot establish a skill's general value. The library's real suites, their git fixtures, and their scorers are in `scripts/auditing/suites/` (see its README).

## Task suite

The suite is JSON with `version: 1` and a nonempty `tasks` list. Author the tasks and requirements before inspecting comparison outputs. Keep evaluation suites outside skill folders.

```json
{
  "version": 1,
  "tasks": [
    {
      "id": "status-note",
      "prompt": "Write report.txt from the provided notes.",
      "workspace": "fixtures/status-note",
      "artifacts": ["report.txt"],
      "checks": [
        {"id": "report-present", "kind": "file_exists", "target": "report.txt"},
        {"id": "version", "kind": "contains", "target": "report.txt", "value": "2.4"}
      ],
      "assertions": [
        {"id": "uncertainty", "text": "The report preserves uncertainty about the release."}
      ]
    }
  ]
}
```

| Field | Meaning |
| --- | --- |
| `id` | Unique task name containing letters, digits, underscores, or hyphens. |
| `prompt` | User task, identical across vendors and control arms. |
| `workspace` | `empty`, `git`, or a fixture directory relative to the suite file. Default: `empty`. |
| `artifacts` | Relative UTF-8 file paths to collect before workspace cleanup. Missing files remain visible in the record. |
| `checks` | Deterministic checks against the final answer or collected files. |
| `assertions` | Task requirements, as strings or objects containing `id` and `text`. Hidden from the tested agents. |
| `control_markers` | Optional regex fingerprints whose presence invalidates the control. Choose them before running the comparison. |

Each task requires checks or assertions. Unknown fields, invalid regexes, duplicate ids, unsafe paths, and contaminated fixtures fail validation before vendor calls.

Fixtures cannot carry agent instruction files, tool configuration, or symlinks. Custom fixtures and the full skill directory are frozen once per run. Both arms receive copies of the same fixture.

The runner collects declared artifacts only. Declare every file a scorer needs. Binary files and multi-turn sessions are outside this command's current scope.

## Objective checks and existing scorers

| Kind | Rule |
| --- | --- |
| `contains` | The target contains `value`, with case preserved. |
| `not_contains` | The target exists and excludes `value`. |
| `regex` | Python `re.search(value, target)` matches. Flags can be embedded in the regex. |
| `file_exists` | A declared artifact exists as a regular UTF-8 file. |
| `command` | An operator-supplied argv runs against the collected evidence. Exit 0 passes, 1 fails, and other exits are unsupported. |

Text checks default to `target: "output"`, meaning the final answer. Set `target` to a declared artifact path to check that file. A missing target fails, including for `not_contains`.

An existing scorer can join the comparison without a new harness:

```json
{
  "id": "writing-lint",
  "kind": "command",
  "argv": [
    "python3",
    "/absolute/path/to/writing_lint.py",
    "--format",
    "json",
    "{output}"
  ],
  "metrics": {
    "violations_per_1k": {"path": "summary.blocking_per_1k", "direction": "lower"}
  }
}
```

`{output}` expands to the saved final answer. `{workspace}` expands to the directory containing declared artifacts. Scorers receive random evidence-directory names without arm labels.

Commands execute trusted operator-supplied code without a shell. They inherit an environment allowlist and have a 60-second timeout. Timeout, missing executable, or scorer error produces an unsupported result.

Scorer stdout and stderr remain in the pair record. Optional `metrics` select finite numeric values from scorer JSON using dotted paths. Each metric declares `lower` or `higher` as its improvement direction.

The summary reports metric means, paired deltas, and direction-adjusted improvements. Missing or invalid metric values make that check unsupported. The scorer's full recorded output retains any additional domain measurements.

## Controls and judges

| Option | Behavior |
| --- | --- |
| `--mode explicit` | Default. The treatment requests the named skill. Trace activation is required for a valid treatment. |
| `--mode natural` | Both arms receive the identical task prompt. The treatment has the skill installed. Activation is reported separately. |
| `--judge-vendor cross` | Default. Codex judges Claude outputs, and Claude judges Codex outputs. |
| `--judge-vendor claude` or `codex` | One judge vendor for all outputs. The runner warns about judging the same vendor. |
| `--judge-vendor none` | Objective checks only. Every task must supply checks. |
| `--models` | Source models, using `claude=MODEL,codex=MODEL`. Existing package defaults apply when omitted. |
| `--judge-models` | Judge models in the same format. Defaults to the resolved source models. |
| `--vendors` | Defaults to `claude,codex`. Selecting one vendor produces a warning. |
| `--install-as NAME` | Installs the skill under `NAME`, with its frontmatter name rewritten, and uses `NAME` in the explicit prompt and the activation checks. Use it when the skill's name collides with a vendor built-in: Claude ships a built-in `code-review`, and without an alias that vendor's arms are refused. |

Each call gets a fresh home and workspace. Claude task arms expose `Read,Glob,Grep,Bash,Skill,Edit,Write,NotebookEdit`. Both arms receive the same tools. Baseline probes retain the activation tool set. Control and treatment order varies using the recorded seed. Baselines detect built-in collisions, and contamination excludes the entire pair.

Judges receive the original task and outputs, with skill and vendor references redacted. They receive neither the skill nor the arm labels. Assertion quotes must pass the existing mechanical evidence check.

Pairwise judgments use both presentation orders. An order-dependent flip counts as a tie. Failed judges produce unsupported grades or void comparisons. Explicit Claude tool errors cannot count as skill activation.

## Spend, records, and interpretation

The default is four repeats, following the recovered writing-style campaign's floor for close variants. That campaign also required five probes. Neither choice makes a one-task suite conclusive.

The plan includes baseline, arm, assertion, and pairwise calls. `--max-calls` refuses an oversized plan before execution. `--max-cost-usd` and `--max-codex-tokens` stop subsequent calls after their respective guards are reached.

Dollar and token guards can be exceeded by the last in-flight call. Costs come from vendor traces. Claude dollars and Codex tokens remain separate, including judge calls.

Records use the existing `SKILL_EVAL_RUNS_DIR` destination. Run records must remain outside the repository and the arm scratch root. Each run writes these files:

- `plan.json`: normalized suite, hashes, frozen fixture paths, models, CLI versions, seed, evaluator version, effort, timeout, and limits.
- `baselines.jsonl`: vendor controls and isolation findings.
- `pairs.jsonl`: outputs, artifacts, validity, objective checks, grades, and comparisons.
- `budget.json`: attempted calls and reported usage.
- `summary.json` and `summary.md`: per-task, per-vendor paired results.

When judges failed (an outage, an expired login), re-run only the judging of the affected valid pairs. Arm outputs are reused, the previous `pairs.jsonl` is kept beside the new one, and `--all` re-judges every valid pair:

```bash
python3 scripts/auditing/skill-eval.py performance rejudge RUN_DIR --max-calls 60
```

Rebuild the report without making calls:

```bash
python3 scripts/auditing/skill-eval.py performance report RUN_DIR --json
```

Check and assertion deltas use valid pairs with supported scores on both sides. Positive check and assertion deltas favour the skill. Numeric metric deltas use with minus without. Their `improvement` field accounts for the declared direction. Missing evidence and failed calls never become clean passes.

Preference counts name `with`, `without`, `tie`, or `void`. The JSON includes a 95% Wilson interval for skill wins among decisive comparisons. Small samples require cautious interpretation.

Exit 0 means the planned comparison completed with supported evidence. Exit 2 means invalid input or setup. Exit 3 means incomplete evidence, including budget exhaustion, failed calls, contamination, or unsupported scoring. Ctrl+C returns 130 and preserves the partial run records.

These exits describe evaluation validity. A valid comparison can show that the skill worsens task quality.

The existing limits still apply: trace contamination detection is heuristic, redaction is lexical, and visible suites are development evidence. This command provides no sealed performance holdout or automatic skill-editing loop.

## Verification

```bash
python3 -m unittest discover -s scripts/tests -p 'test_skill_eval*.py'
```

Tests include a command-level comparison through both vendor adapters using local synthetic clients. Those clients make no network calls and require no credentials. Live comparisons require vendor credentials and spend quota.
