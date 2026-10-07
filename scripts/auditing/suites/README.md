# Task-quality suites

Task suites for `skill-eval.py performance run`, one JSON file per skill. Each measures whether the skill improves the work, comparing the same task with and without it on Claude and Codex, with objective checks and blind cross-vendor grading. Format and interpretation: [`../skill_eval/PERFORMANCE.md`](../skill_eval/PERFORMANCE.md).

| Suite | Tasks | Fixtures |
| --- | --- | --- |
| `code-review.json` | review a branch with an injection, an off-by-one page, and a None crash; review a retry helper that repeats POSTs, swallows the final error, and never backs off | `review-search`, `review-retry` |
| `pr-description.json` | describe a rate-limit branch that has a brief; describe a fix-plus-rename branch with no brief | `pr-ratelimit`, `pr-renamefix` |
| `smart-conventional-commits.json` | commit two unrelated changes; commit one feature beside a stray scratch file | `commit-mixed`, `commit-feature` |
| `root-cause-debugging.json` | a test that fails only in the full suite (shared mutable default); a misleading error message hiding float rounding | `debug-shared-default`, `debug-float-total` |

## Running

The fixtures are git repositories, generated rather than tracked (a nested `.git` cannot live in this repository). Build them, then run a suite:

```bash
python3 scripts/auditing/suites/build_fixtures.py
python3 scripts/auditing/skill-eval.py performance run --skill code-review \
  --suite scripts/auditing/suites/code-review.json --repeats 3 --dry-run
```

`scorers/commit_log.py` scores the commits an agent made from the collected reflog; `scorers/run_tests.py` reruns a fixture's tests against the agent's edited files.

## Authoring rules

- Write tasks and requirements as the user would state them, without reading the skill body. A requirement copied from the skill grades compliance with the skill's own rules, not the quality of the work (`../skill_eval/DESIGN.md` §2 T-B).
- Every check must be able to fail: confirm it fails on the untouched fixture and passes on a correct result before trusting it.
- New suites are eval cards (version 2): claims, a `harm` or `stand-down` task, planted good and bad outputs, and an invalidation map (`../skill_eval/PERFORMANCE.md`, "Eval cards"). Run `performance validate` on a card before any live run. The five suites above are version 1.
- These suites are visible, so they are development evidence. An author tuning a skill against them can overfit; there is no sealed performance holdout yet.
