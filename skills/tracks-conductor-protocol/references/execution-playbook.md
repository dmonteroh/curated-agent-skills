# Execution Playbook (TCD)

This is a concise execution protocol for implementing tasks created with Tracks Conductor Protocol.

## Default loop

1. Re-read the task brief (Intent, Scope, Acceptance Criteria).
2. Confirm links:
   - Track spec/plan (if present)
   - Relevant ADRs (architecture decisions)
   - Relevant Futures (deferred constraints)
3. Identify missing context:
   - If product/tech/workflow context is unclear, update `docs/context/*` (CDD).
   - If requirements are unclear, update the track spec before writing code (SDD).
4. Implement using a tight verify loop:
   - Write/update tests where possible (unit/integration/e2e as appropriate)
   - Make the minimal change to satisfy one acceptance criterion at a time
   - Run checks frequently
5. Record completion:
   - Set task status via `scripts/tcd.sh set-task-status <task-id> <status>` (updates frontmatter and rebuilds `docs/project/work_index.md` atomically)
   - Record the commit SHA beside the task in the track plan (see "Plan as revert map")

## Batch execution (recommended for large tasks)

If the task has multiple acceptance criteria or the plan has many steps, execute in small batches.

Default batch size: **2-5 atomic steps** or **1 acceptance criterion**.

After each batch:

- summarize what changed
- show verification evidence (tests/build output)
- ask for review/feedback before continuing

## Verification before completion (honesty gate)

Do not claim a task is complete without fresh verification evidence.

Checklist before claiming “done” or preparing integration:

1. Identify the command(s) that prove the claim (tests/build/lint).
2. Run them fresh.
3. Read output and confirm exit code.
4. Only then claim completion, with evidence.

If you cannot run verification in the current environment, say so explicitly and provide a concrete verification plan for the user.

## Verification checklist (minimum)

- Acceptance criteria satisfied (explicitly check each).
- Key risks mitigated or explicitly accepted.
- No untracked scope expansion:
  - If new work is discovered, create a new intake or task.
- If the change introduces/depends on an architectural decision, create/update an ADR using the repo's ADR format.

## Ordered dispatch (optional)

For queue-driven execution (e.g. autonomous runners), an optional `docs/project/order.csv` (override: `TCD_ORDER_FILE`) defines dispatch order:

- Columns: `order,task_id,enabled` plus optional per-task budget columns (`timeout_secs`, `no_progress_secs`, `hard_ceiling_secs`); a header row is recognized by name, otherwise v1 positional columns apply.
- `tcd.sh validate` checks the file when present: unique order values and task ids, integer budgets > 0, and every enabled task id resolving to a file in `tasks/`.

Two tasks may be dispatched concurrently only when they touch no common files **and** neither consumes the other's output; if either test fails, they stay serialized. `order.csv` cannot express concurrency — validate requires unique order values, so the file is a strictly serial queue — which means the criterion is applied when choosing what to dispatch, and any blocking relationship is written into the blocked task's `## Dependencies` section, where the task template already holds it.

## Commit hygiene (suggested)

- Small commits aligned to acceptance criteria or plan phases.
- Commit messages reference the task id (e.g. `S03-T-20260130-...`).

## Plan as revert map

The task id in the commit message links code back to the plan. Record the forward link too, so the plan file answers questions about the code without anyone reconstructing history from `git log`:

- When a task is marked complete, write its commit SHA beside it in the track plan.
- When a phase closes, add its checkpoint SHA to the plan's phase table (phase, SHA, date, status).
- Copy the SHA from `git rev-parse --short HEAD` rather than retyping it.

Task form (the phase-checkpoint table is in the Track Plan template in `references/templates.md`):

```markdown
- [x] Task: S03-T-20260130-parse-tokens `abc1234`
```

With both recorded, the plan answers "what changed in phase 2" (`git diff <phase-1-sha>..<phase-2-sha>`) and "return to the state at the end of phase 1" directly, and every satisfied acceptance criterion has a diff attached to it. Without them, a plan full of ticked boxes proves only that someone ticked them.

## Deviations from the plan

Execution departs from the plan routinely. Classify the departure and update the artifact that classification obliges — the routing is fixed, so the decision is not re-litigated per incident:

| Deviation | What happened | Artifacts it obliges |
| --- | --- | --- |
| Scope addition | A requirement was discovered mid-work | Add the requirement to the track spec; create a new task brief for it and add it to the plan; note the addition on the task in hand |
| Scope reduction | Planned work turned out to be unnecessary | Leave the plan item unchecked with a `SKIPPED:` note and its reason, and amend the spec's Scope section — so the removal is a recorded decision, not a silent omission |
| Technical deviation | A different implementation approach than planned | Record on the completed task why the planned approach was unsuitable; update `docs/context/tech-stack.md` if dependencies changed |
| Requirement change | The understanding of the requirement itself moved | Correct the spec, then re-verify the acceptance criteria against the new wording |

Record the deviation inline on the task it belongs to, so the plan stays a record of what happened rather than of what was intended:

```markdown
- [x] Task: S03-T-20260130-parse-tokens `abc1234`
  - DEVIATION (technical): used the platform tokenizer instead of a hand-rolled scanner
  - Reason: identical output across the fixture set, and no new dependency
  - Impact: scanner module deleted; no change to `tech-stack.md`
```

Two constraints on this routing:

- Scope addition does not license widening the task in hand. "No untracked scope expansion" stands: the discovered requirement becomes a new intake or task brief, and the deviation note records why it appeared.
- Scope reduction has no frontmatter status. `references/status-model.md` is a closed enum and `tcd.sh validate` rejects ad-hoc values, so a dropped task is recorded in the plan and the spec as above — never by inventing a `Skipped` status.

## Finishing / integration

When implementation is complete, finish the branch with verification-first workflows.

- Verify tests, then choose merge vs PR vs keep.

## When to stop and create more artifacts

- If you cannot proceed without a decision: create an ADR.
- If you can proceed but future requirements might be blocked: create a Future entry with a trigger.
- If the task is too large: split into multiple tasks and update the plan.
