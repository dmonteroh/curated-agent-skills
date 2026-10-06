# skill-eval

`skill-eval` tests activation and task quality on Claude Code and Codex, without letting the test environment or the skill under test contaminate the result. It is standalone: the review pipeline (`run_parallel_skill_reviews.sh`, `audit-skills.sh`, `proposals.py`) neither calls it nor is called by it. `REPLACEMENT-BRIEF.md` lists which parts of that pipeline it could replace. `DESIGN.md` is the contract and threat model.

Entry point, from the repository root:

```bash
python3 scripts/auditing/skill-eval.py <command> <subcommand> [options]
```

Stdlib-only Python 3.10+. The `performance run` command makes calls unless `--dry-run` is set. The `activation`, `judge generate`, `judge pairwise`, `judge grade`, and `env builtins` commands call the `claude` and `codex` CLIs and spend money or quota. The rest are static and free.

Paired task-quality evaluation: [PERFORMANCE.md](PERFORMANCE.md). Tasks and requirements are data for the shared runner; the library's suites live in [`../suites/`](../suites/README.md).

## Commands

| Command | Cost | What it does |
| --- | --- | --- |
| `cases lint [--skill S \| --all] [--json]` | free | Lints `trigger-cases/`: the 5/5 floor, a near-miss negative, an off-register positive, generator residue, duplicates, echo of the description, cross-skill collisions. Exits 1 on any error. |
| `cases stats [--json]` | free | Per-skill case counts and quality signals. |
| `cases deficits [--skill S] [--json]` | free | Per skill, the template-residue cases that repair will drop and how many positives, negatives, near-misses, and off-register positives are still missing. Lists only files that need something unless `--include-clean`. |
| `cases apply --selection F.json --candidates F.md [--dry-run]` | free | Drops a file's template-residue cases and appends the selected cases. Every selected prompt must be an accepted row of the given candidates file with the same polarity, or nothing is written: a reviewer chooses generated prompts and never writes one. Edits are per case block, so notes and other cases survive. Exits 1 if the file still has lint errors afterwards. |
| `integrity scan --skill S` / `scan-all` | free | Looks for evaluation material inside a skill: canaries, sealed holdout and assertion text (error), and its own trigger prompts (warn). |
| `integrity diff-scan --skill S --base REF` | free | The same checks on lines added since `REF`. Run it before accepting a skill edit. |
| `integrity seal --skill S --kind holdout\|assertions --src F.json` | free | Encodes a holdout or assertion set into `scripts/auditing/sealed/` with a canary, so an authoring agent never reads it in plaintext. `list` shows headers; `show` decodes, with a warning. |
| `env check --vendor V --home H --cwd C --skills a,b` | free | Checks an arm home and cwd for pollution: instruction files, foreign skills, MCP servers, memory, settings, a cwd outside the scratch root. |
| `env builtins --vendor V [--model M]` | 1 call | Records which built-in skills a vendor shows with nothing installed. |
| `performance run --skill S --suite F.json [--dry-run]` | N calls | Paired task quality with and without the skill on both vendors. Cross-vendor judging is the default. |
| `performance report RUN_DIR [--json]` | free | Rebuilds task-quality metrics from saved pairs. |
| `activation run --skill S ...` | N calls | The activation test. See below. |
| `activation report RUN_DIR` / `compare A B` / `feedback RUN_DIR` | free | Re-renders a summary, diffs two runs per case, or gives train-only failure classes. |
| `activation selftest --skill S [--dry-run] [--max-calls N]` | calls | A positive control (the skill named explicitly) and, only if it activates, a negative control (renamed skill, unrelated description). `pass` (0), `fail` (1), or `inconclusive` (3: no valid comparison; `reasons` says whether the positive control did not activate, a cap stopped the run, or calls failed). `--max-calls` is split evenly per vendor and sizes the plan: fewer train positives are used so every vendor gets a complete paired comparison, and a cap below `3 × repeats` calls per vendor is refused (exit 2) before any call. Do not trust `run` results for a skill whose selftest is not `pass`. |
| `activation selftest-all [--skills a,b] [--parallel N] [--dry-run]` | calls | Runs `selftest` for every skill (or the listed ones) as parallel child processes, passing the other flags through per skill, and writes `sweep.json` and a `sweep.md` table of per-vendor verdicts, rates, valid calls, and reasons to a `selftest-sweep` run directory. Exit 0 when every skill passes, 1 on any `fail` or child error, 3 otherwise. |
| `judge pairwise --prompt F --a F --b F --judge-vendor V` | 2+ calls | A blind A/B judgement in both presentation orders. A flip counts as a tie. |
| `judge grade --prompt F --output F --assertions F\|--sealed F --judge-vendor V` | 1 call per assertion | Pass, fail, or unsupported. The quote is checked mechanically against the output. |
| `judge generate paraphrases\|cases --skill S --gen-vendor V` | calls | Candidate trigger cases from a generator that never sees the skill. Writes `candidates.md` for human review. `generate cases --jobs F.json` takes `{"<skill>": "<one-line job>"}` and writes one `<skill>.candidates.md` per skill; `--gen-vendor claude,codex` asks every listed vendor and tags each row `gen:<vendor>`; `--n-off-register N` adds terse lowercase positives. |

## Typical workflows

**Is the corpus good enough to measure?** Free, run first:

```bash
python3 scripts/auditing/skill-eval.py cases lint --skill pr-description
python3 scripts/auditing/skill-eval.py integrity scan --skill pr-description
```

**Repair a corpus that fails lint.** The generator sees only a one-line job you write per skill, never the skill. Review the candidates against the skill's scope, write a selection, then apply it:

```bash
python3 scripts/auditing/skill-eval.py cases deficits
python3 scripts/auditing/skill-eval.py judge generate cases --jobs jobs.json --gen-vendor claude,codex \
  --n-pos 5 --n-neg 4 --n-near-miss 3 --n-off-register 2
python3 scripts/auditing/skill-eval.py cases apply --selection sel/pr-description.json \
  --candidates RUN_DIR/pr-description.candidates.md
```

**Does a description load where it should?** Plan first, then run. `run` and `selftest` refuse a skill whose corpus has lint errors unless `--allow-corpus-errors` is passed, which the plan records:

```bash
python3 scripts/auditing/skill-eval.py activation run --skill pr-description --dry-run
python3 scripts/auditing/skill-eval.py activation selftest --skill pr-description
python3 scripts/auditing/skill-eval.py activation run --skill pr-description --repeats 4 --split train
```

The default vendors are `claude,codex`. Override models with `--models claude=haiku,codex=gpt-5.6-luna`. Cap spend with `--max-calls` and `--max-cost-usd`. Claude reports dollars and Codex reports tokens, and the two are never converted.

**Which skill wins when neighbours compete?**

```bash
python3 scripts/auditing/skill-eval.py activation run --skill monitoring-expert --shape competitive --neighbors sre-engineer,migration-observability
python3 scripts/auditing/skill-eval.py activation run --skill monitoring-expert --shape competitive --library
```

**A/B a description change.** Measure both variants on train, then measure the winner once on the sealed holdout:

```bash
python3 scripts/auditing/skill-eval.py activation run --skill S --repeats 4 --split train                              # current description
python3 scripts/auditing/skill-eval.py activation run --skill S --repeats 4 --split train --description-file new.txt   # candidate
python3 scripts/auditing/skill-eval.py activation compare RUN_A RUN_B
python3 scripts/auditing/skill-eval.py activation feedback RUN_B            # class-level, train only
python3 scripts/auditing/skill-eval.py activation run --skill S --split holdout --description-file new.txt
```

**Before accepting any edit to a skill:**

```bash
python3 scripts/auditing/skill-eval.py integrity diff-scan --skill S --base HEAD
```

## Case sets

| Set | Source | Who can read it | Use |
| --- | --- | --- | --- |
| train | `trigger-cases/<skill>.md`, hash-assigned | Anyone | Tuning and feedback |
| dev | `trigger-cases/<skill>.md`, the other side of the hash | Anyone | A check against tuning noise. It is not a real holdout, because it is plaintext |
| holdout | `scripts/auditing/sealed/<skill>.holdout.sealed` | Nobody during authoring | The final measurement. Each distinct description measured here is logged in `sealed/holdout-ledger.jsonl`. Past 3 (a chosen default), the run refuses without `--allow-holdout-reuse` |

To create a holdout, write `{"cases": [{"prompt": "...", "expect": true, "tags": ["near-miss"]}]}` somewhere outside the repository, run `integrity seal`, and delete the source. Whoever writes it should not have read the skill.

## Where things go

- Run records: `$SKILL_EVAL_RUNS_DIR`, default `~/.cache/skill-eval/runs`. They sit outside the repository, so an authoring agent cannot grep prompts, grades, or judge reasons, and outside the scratch root that arms browse. An arm that reads them by absolute path is marked contaminated. Point the variable at a durable path to keep runs across a container rebuild.
- Arm homes and working directories: `$SKILL_EVAL_SCRATCH`, default `/tmp/skill-eval`. Homes hold copied credentials, are created `0700`, and are deleted after each run unless `--keep-homes` is passed.
- Sealed sets and the holdout ledger: `scripts/auditing/sealed/`, tracked in git.

## Known limits

- Copilot is not covered, because no Copilot CLI is installed in this container.
- Claude accounts with organisation-provisioned skills (`anthropic-skills:*`) can see them appear in an otherwise bare arm. `activation` detects this, excludes the affected records, and lists the foreign skills in the summary. See `REPLACEMENT-BRIEF.md` §2 for the current state of this channel.
- `SCRATCH_ROOT` and its `homes/`, `cwd/`, and `selftest-negctrl/` directories are traverse-only (mode `0300`), so arms cannot list or glob their way to other arms' material. To inspect them by hand, `chmod u+r` first.
- Shell-capable arms (Claude Bash, Codex with `danger-full-access`, the only Codex mode that works in this container) can read any path the container user can. Nothing prevents it; `activation` detects it from the trace and marks the record contaminated when the path is in the repository, the real home, the scratch root, or the runs directory. Detection is a heuristic over tool inputs and shell commands.
- Codex reports no visible-skill list, so the post-run visible-skill check covers Claude only. Codex isolation rests on the generated home and on path detection.
- Arms run in a neutral git fixture by default (`--workspace git`). In an empty directory, task-shaped prompts often end with the agent exploring an empty cwd before any skill decision; `selftest` then reports `inconclusive` (exit 3).
- Redaction in `judge` is lexical. Style and vocabulary that are characteristic of a skill still reach the judge.
- Every threshold is a chosen default unless its comment names a measurement.

Tests: `python3 -m unittest scripts.tests.test_skill_eval_vendors scripts.tests.test_skill_eval_trace scripts.tests.test_skill_eval_cases scripts.tests.test_skill_eval_integrity scripts.tests.test_skill_eval_judge scripts.tests.test_skill_eval_activation scripts.tests.test_skill_eval_performance`. The tests make no live calls.
