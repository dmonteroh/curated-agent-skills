# Record shapes

The records a paired skill benchmark writes, field by field, plus the join and the arithmetic checks that make the rollup re-derivable. JSON is used for the shapes below; any format with the same fields works, provided every record is machine-readable rather than prose.

All values shown are illustrative fill for the shape. None is a target, a threshold, or a measured result.

## spec.json — frozen before the first run

```json
{
  "skill": {
    "name": "example-skill",
    "version": "0.3.0",
    "content_hash": "sha256:9c1e…"
  },
  "document_set": ["execution-plan.md", "code-changes.md", "verification-strategy.md"],
  "evals": [
    {
      "id": "eval-1",
      "name": "happy-path-feature-request",
      "prompt": "Add a config option to disable background indexing, behind a flag, and open a PR for it.",
      "expected_output": "A plan that isolates the work, stages it in more than one commit, and names every verification gate the project requires.",
      "fixtures": [],
      "assertions": [
        {
          "id": "worktree-isolation",
          "concept": "isolated-workspace",
          "text": "The execution plan uses a git worktree in a sibling directory, not the main working directory.",
          "grading": "automated"
        },
        {
          "id": "multi-commit",
          "concept": "atomic-commits",
          "text": "The plan uses 2 or more commits for the multi-file change.",
          "grading": "automated"
        }
      ]
    }
  ]
}
```

- `content_hash` pins the exact file loaded, not the version label. A version string that moves without the hash moving is how two iterations end up incomparable.
- `document_set` is fixed here, once, for both arms and all evals. It is the reason the grader looks in the same places both times.
- `expected_output` describes what is actually graded. When the graded artifact is a proposal, this sentence says so — an expected output claiming shipped, merged work over a plan document silently changes what the benchmark measures.
- `fixtures` carries per-eval input files where a prompt needs them. Its semantics are stated here rather than inherited: an entry is a path relative to the eval directory, copied into the run's working directory before the prompt is issued.
- `id` joins the two arms of one eval. `concept` groups assertions that test the same property across evals, and is what the discrimination rollup groups by; without it, one property tested in four evals under four ids is either four findings or a hand-merge.
- `grading` is `automated` or `manual`. A suite where every entry says `manual` has a declared axis nobody used.

## run-config.json — one per iteration, written before the first run

```json
{
  "iteration": 2,
  "previous_iteration": {"id": 1, "rollup": "iteration-1/rollup.json"},
  "arm_variable": "skill",
  "agent": {"model": "…", "model_version": "…", "temperature": null, "top_p": null, "seed": null, "sampling_note": "provider defaults, not pinned"},
  "runner": {"name": "…", "version": "…"},
  "skill_under_test": {"name": "example-skill", "version": "0.3.0", "content_hash": "sha256:9c1e…"},
  "control_arm_definition": "The skill file was removed from the agent's loadable set; every other input identical; each run started in a fresh session.",
  "target_state": {"repo": "…", "revision": "…", "checkout": "fresh per run from that revision, discarded after"},
  "grader": {"kind": "model", "model": "…", "model_version": "…", "blinded": true, "shuffle_seed": 41},
  "repeats_per_cell": 3,
  "repeats_provenance": "chosen budget, not a measured sufficiency",
  "started_at": "…",
  "finished_at": "…"
}
```

Every field is present or explicitly `null` with a note. A blank field and a default are indistinguishable after the fact, and a delta whose configuration was never recorded cannot be reproduced or compared with the next one.

`control_arm_definition` is prose on purpose, and it is the field most often skipped. "Without the skill" can mean the file was deleted, loading was suppressed, or a different session was used, and those are different experiments.

`arm_variable` names the one thing that differs between arms — `skill` or `agent` — and the rest of the record is read against it. Where it is `agent`, the skill (if any) is loaded identically in both arms and an `arms` block pins each candidate instead:

```json
{
  "arm_variable": "agent",
  "skill_under_test": null,
  "arms": {
    "control": {"binary": "…", "binary_version": "…", "model": "…", "model_version": "…"},
    "treatment": {"binary": "…", "binary_version": "…", "model": "…", "model_version": "…"}
  }
}
```

A binary name without its version is not a pin: an agent that updated between arms is a second variable nobody recorded. The task set, the fixtures, and `target_state` stay identical across arms, and one arm is designated the control so the delta has a stated direction. A record showing both the skill and the agent moving is not a matched pair, and the delta it produces belongs to neither. (authored — the source tool supplies the arm variable, not this record shape.)

`target_state` pins the material the agent works on, which the workspace layout otherwise says nothing about. A revision recorded here plus a fresh checkout per run is what makes two runs a matched pair rather than two passes over a tree that moved between them; a branch name in this field is not a pin. Keep the checkout itself outside the graded document set, so nothing inside it can be read as output. Where the task acts on no repository, say so in the field instead of leaving it out.

## arm-map.json — the file the grader does not open

```json
{
  "eval-1": {"r-8f21": "with_skill", "r-3ba9": "control", "r-c4d0": "with_skill"},
  "eval-2": {"r-77e2": "control", "r-1fa5": "with_skill"}
}
```

Run ids are opaque and carry no condition token. This file is the only place the mapping exists, and it is read after grading closes, never during. Keeping it out of the run directories is what makes blinding structural instead of a promise.

Condition labels follow the arm variable: `with_skill` and `control` where the skill varies, `treatment` and `control` where the agent does. Never the agent's own name — a label a reader can recognize is a condition token, and it defeats the file it is written in.

## eval-snapshot.json — one per eval, above the arm split

```json
{
  "eval_id": "eval-1",
  "eval_name": "happy-path-feature-request",
  "snapshot_of": "sha256:9c1e…",
  "prompt": "…verbatim copy from spec.json…",
  "assertions": [{"id": "worktree-isolation", "concept": "isolated-workspace", "text": "…", "grading": "automated"}]
}
```

A frozen copy of the spec entry as it stood when this iteration ran. Its position — above the run directories, not inside them — is what makes divergence between arms structurally impossible rather than merely discouraged. When the spec later moves, the snapshot is what keeps this iteration's numbers readable.

## grading.json — one per run

```json
{
  "run_id": "r-8f21",
  "eval_id": "eval-1",
  "snapshot_of": "sha256:9c1e…",
  "graded_at": "…",
  "results": [
    {
      "id": "worktree-isolation",
      "passed": true,
      "evidence": "\"git worktree add ../wt/feat-search origin/dev\"",
      "source": "outputs/execution-plan.md"
    },
    {
      "id": "multi-commit",
      "passed": false,
      "evidence": "\"Single commit: 'feat: add background-indexing flag'\"",
      "source": "outputs/execution-plan.md"
    }
  ]
}
```

- `id`, never assertion text. Text is paraphrased and truncated by whoever writes the record, and the clauses that go first — the parentheticals, the named values, the counts — are exactly the ones carrying the discrimination. A text join then fails silently on the rows that matter most.
- `evidence` quotes the output. A pass quotes the passage that satisfies the assertion; a failure quotes what the agent did instead. "Assertion not met" is a restatement, not evidence, and nothing can be re-derived from it.
- `source` names the document the quotation came from, so a reviewer can re-derive the pass bit without trusting the grader's summary.
- No field names the condition. Checking this is a search over the record, its filename, and its path for the condition tokens; any hit voids the grading pass.

## run-meta.json — one per run

```json
{"run_id": "r-8f21", "repeat_index": 1, "duration_seconds": 418, "tokens": null, "tokens_note": "not recorded by this runner"}
```

A field that is always null is a claim the artifact does not support. Either populate it or delete it, and where it stays null, say why — a cost comparison that was never possible should not look like one that came out even.

## rollup.json — recomputed, never transcribed

```json
{
  "weighting": "per-assertion",
  "cells": [
    {"eval_id": "eval-1", "condition": "with_skill", "repeats": 3, "passed": 8, "total": 10,
     "failed_ids": ["multi-commit", "gate-order"],
     "assertion_passes": {"worktree-isolation": 3, "multi-commit": 1, "gate-order": 0},
     "split_ids": ["multi-commit"]},
    {"eval_id": "eval-1", "condition": "control", "repeats": 3, "passed": 4, "total": 10, "failed_ids": ["worktree-isolation", "multi-commit", "gate-order", "gate-coverage", "cleanup-step", "pr-target"], "assertion_passes": {"worktree-isolation": 0, "multi-commit": 0, "…": 0}, "split_ids": []}
  ],
  "conditions": {"with_skill": {"passed": 21, "total": 26}, "control": {"passed": 13, "total": 26}},
  "delta_pp": 30.8,
  "buckets": {
    "discriminating": ["worktree-isolation", "gate-order"],
    "non_discriminating": ["branch-from-default", "tests-added"],
    "regression": ["minimal-change"],
    "unstable": ["multi-commit"]
  },
  "concentration": {"top_1_share": 0.31, "top_2_share": 0.55},
  "duration": {"with_skill": {"mean_s": 412.5, "sd_s": 88.4}, "control": {"mean_s": 371.0, "sd_s": 64.2}, "sd_estimator": "population"}
}
```

`sd_estimator` is stated because population and sample standard deviation give different numbers from the same data, and an unlabelled figure cannot be compared with anyone else's.

The cell list and the buckets are abridged above — one eval of several, five assertion ids of the suite's full set. In a real record both are exhaustive, because the arithmetic and partition checks below depend on it.

## Per-cell agreement across repeats

A repeat count says how many samples a cell has. It says nothing about whether they agreed, and a cell that disagrees with itself is indistinguishable from a stable one once both are rendered as a single pass bit.

`assertion_passes` closes that: for every assertion in the cell, how many of that cell's repeats passed it. `0` or `repeats` is unanimous; anything between is a split, and `split_ids` lists them. The cell's `passed` count is the per-assertion majority, and the split is carried beside it rather than folded into it — the majority is what the arithmetic check runs on, the split is what says how much the majority is worth.

An assertion split in either arm buckets as `unstable`, not as discriminating, non-discriminating, or a regression: the arms cannot be compared on a row where one of them has no settled outcome. The partition check is unchanged — every id still lands in exactly one bucket, of four.

An even repeat count can tie. A tied assertion is unstable by definition, so no tie-break rule is needed and none is offered; a tie broken silently is the failure this whole section exists to prevent.

No agreement level is established as sufficient. Unanimity is the only self-evident case, and any bar short of it is a chosen default, recorded with the run beside the repeat count — the same treatment the repeat count itself gets. (authored — the source names consistency across repeats as a metric; the shape, the bucket, and the tie rule are this skill's.)

## The join and the checks

Run all four against the records before any number leaves the workspace. Each names a failure that has actually occurred in practice.

1. **Id-set equality.** For each run, the set of `id` values in `grading.json` equals the set in its `eval-snapshot.json`. A missing or extra id voids the join. Failure mode it catches: rows quietly dropped from a positional alignment, so a rollup counts fewer assertions than were graded.
2. **Cell arithmetic.** For each cell, `passed + len(failed_ids) == total`. Failure mode it catches: a hand-written cell count that contradicts its own failed-assertion list — the record disagreeing with itself, in the one place a reader is least likely to check.
3. **Recomputation.** Every published figure is derived from the grading records in the same pass that renders the report. Failure mode it catches: several derived artifacts agreeing with each other and disagreeing with the evidence, because all were copied from one unverified intermediate.
4. **Bucket partition.** Every assertion id appears in exactly one bucket, and the bucket sizes sum to the assertion count. Failure mode it catches: a discrimination split written by eye, which lists a few memorable ids and silently omits the rest.

## Rendering

Whatever renders the result loads both arms' grading records and shows their per-assertion evidence side by side, keyed by id. A viewer built from one arm's records looks complete, shows a plausible per-assertion breakdown, and hides the control arm and every rollup error with it.
