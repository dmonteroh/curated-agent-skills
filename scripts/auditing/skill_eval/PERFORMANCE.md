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

## Eval cards: suite version 2

A version 2 suite is an eval card. It states what the skill promises as claims and ties every check and assertion to one claim, so the result is a verdict per claim instead of a delta per task. `examples/text-card.json` is a worked card that `validate` passes.

```json
{
  "version": 2,
  "claims": [{"id": "keeps-certainty", "statement": "A rewrite keeps every hedge at the source's strength.", "rests_on": ["SKILL.md"]}],
  "invalidation": {"SKILL.md": "all", "references/*.md": ["keeps-certainty"]},
  "tasks": [{
    "id": "release-note", "kind": "deliverable", "claims": ["keeps-certainty"],
    "prompt": "Rewrite this status note for a customer.",
    "checks": [{"id": "hedge", "kind": "regex", "value": "(?i)\\bmay\\b", "claim": "keeps-certainty"}],
    "assertions": [{"id": "approximate", "text": "The duration stays approximate.", "claim": "keeps-certainty"}],
    "planted": [{"path": "planted/good", "expect": "good"}, {"path": "planted/bad", "expect": "bad"}]
  }]
}
```

| Field | Meaning |
| --- | --- |
| `claims` | Nonempty. Each has an `id`, a one-line `statement` of a reader-visible outcome, and optional `rests_on`, the skill paths or sections it depends on. Every claim needs at least one tagged check or assertion |
| `invalidation` | Optional. Glob patterns relative to the skill directory, each mapped to a list of claim ids or `"all"`. `plan` reads it. A changed path no pattern matches invalidates every claim |
| task `kind` | `deliverable` (default), `harm` (input the skill must leave alone or not over-apply to), or `stand-down` (a near-miss request where the right move is to decline the skill's procedure). A card needs at least one `harm` or `stand-down` task (chosen default) |
| task `claims` | The claims the task probes. Every check and assertion in the task names one of them in `claim` |
| task `planted` | Planted outputs for `validate`. Each `path` is a directory, relative to the card, holding `output.txt` and an optional `artifacts/` directory laid out like a run's evidence. `expect` is `good` or `bad` |

A claim counts once per pair. An arm meets a claim when every check and assertion the task tags with it passes. One missing or unsupported piece of evidence leaves that pair out of the claim, so a judge that never ran cannot turn a claim into a pass.

| Verdict | Rule |
| --- | --- |
| `STRONG` | The 95% Wilson intervals of the with rate and the without rate do not overlap, and the with rate is higher |
| `HARM` | The same separation in the other direction |
| `BASELINE` | No separation, and the without arm meets the claim at 0.8 or above (chosen default): the skill earns nothing for it |
| `WEAK` | No separation at this n. More pairs may still separate it |
| `UNMEASURED` | No pair with complete evidence |

Disjoint intervals are a conservative chosen test. At 20 pooled pairs, 18 against 6 separates, and 14 against 10 does not. The summary gives each claim's verdict per vendor and pooled, and whether the two vendors moved in the same direction.

Check a card before spending anything:

```bash
python3 scripts/auditing/skill-eval.py performance validate --suite CARD.json
```

Every check must pass every planted good output and fail at least one planted bad output. A check that passes every bad output cannot fail, so it certifies nothing, and `validate` reports it as an error. A claim with only judged assertions is reported as info, because no free check backs it.

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
| `--grading batched` | Default. One judge call per presentation order grades every assertion for both outputs and gives the overall preference: two judge calls per pair |
| `--grading separate` | One judge call per assertion per output, plus two pairwise calls. Runs recorded before batched grading used this mode, and `rejudge` keeps it for them |
| `--claims a,b` | Version 2 cards only. Runs only the tasks that probe the listed claims |
| `--adaptive` | Version 2 cards only. Runs one round per repeat. From the second round on, a task is skipped for a vendor once every claim it probes is `STRONG` or `HARM` for that vendor. Skipped pairs are recorded in `plan.json` and never count as incomplete |
| `--install-as NAME` | Installs the skill under `NAME`, with its frontmatter name rewritten, and uses `NAME` in the explicit prompt and the activation checks. Use it when the skill's name collides with a vendor built-in: Claude ships a built-in `code-review`, and without an alias that vendor's arms are refused. |

Each call gets a fresh home and workspace. Claude task arms expose `Read,Glob,Grep,Bash,Skill,Edit,Write,NotebookEdit`. Both arms receive the same tools. Baseline probes retain the activation tool set. Control and treatment order varies using the recorded seed. Baselines detect built-in collisions, and contamination excludes the entire pair.

Judges receive the original task and outputs, with skill and vendor references redacted. They receive neither the skill nor the arm labels. Assertion quotes must pass the existing mechanical evidence check.

Pairwise judgments use both presentation orders. An order-dependent flip counts as a tie. Failed judges produce unsupported grades or void comparisons. Explicit Claude tool errors cannot count as skill activation.

Batched grades follow the same rule. A grade counts only when both presentation orders agree on it after the quote check. Disagreement is position bias, and the grade becomes `unsupported` with the reason `order-dependent`.

## Spend, records, and interpretation

The default is four repeats, following the recovered writing-style campaign's floor for close variants. That campaign also required five probes. Neither choice makes a one-task suite conclusive.

The plan includes baseline, arm, and judge calls. With batched grading a pair costs four calls: two arms and two judges. With separate grading it costs two arms, two calls per assertion, and two pairwise calls. `--max-calls` refuses an oversized plan before execution. `--max-cost-usd` and `--max-codex-tokens` stop subsequent calls after their respective guards are reached.

Dollar and token guards can be exceeded by the last in-flight call. Costs come from vendor traces. Claude dollars and Codex tokens remain separate, including judge calls.

Records use the existing `SKILL_EVAL_RUNS_DIR` destination. Run records must remain outside the repository and the arm scratch root. Each run writes these files:

- `plan.json`: normalized suite, hashes, frozen fixture paths, models, CLI versions, seed, evaluator version, effort, timeout, and limits.
- `baselines.jsonl`: vendor controls and isolation findings.
- `pairs.jsonl`: outputs, artifacts, validity, objective checks, grades, and comparisons.
- `budget.json`: attempted calls and reported usage.
- `summary.json` and `summary.md`: per-task, per-vendor paired results. For a card, also a verdict per claim, per vendor and pooled. Every run also reports the mean cost per arm in each vendor's own unit, and how many with-skill arms executed a file under the skill's `scripts/` directory (`script_runs` in the trace). Runs recorded before traces carried `script_runs` show "not recorded".

When judges failed (an outage, an expired login), re-run only the judging of the affected valid pairs. Arm outputs are reused, the previous `pairs.jsonl` is kept beside the new one, and `--all` re-judges every valid pair:

```bash
python3 scripts/auditing/skill-eval.py performance rejudge RUN_DIR --max-calls 60
```

Rebuild the report without making calls:

```bash
python3 scripts/auditing/skill-eval.py performance report RUN_DIR --json
```

Rerun the objective checks and scorers over a finished run's stored outputs, with no agent or judge calls, after a scorer or check changes. `--suite` takes checks and claim tags from an edited suite for tasks with the same id. Changed assertions are reported, because their grades need `rejudge --all`. The previous `pairs.jsonl` is kept beside the new one:

```bash
python3 scripts/auditing/skill-eval.py performance rescore RUN_DIR --suite CARD.json
```

List what a change to a skill invalidates, from `git diff` against a ref plus untracked files. A frontmatter change invalidates activation. A body change and every other changed path map through the card's `invalidation` globs to claims. The command prints the claims, the tasks that probe them, a call estimate, and the commands to run. It runs nothing:

```bash
python3 scripts/auditing/skill-eval.py performance plan --skill S --suite CARD.json --since HEAD
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
