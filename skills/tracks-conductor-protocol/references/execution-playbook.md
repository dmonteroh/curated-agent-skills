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
   - Update task frontmatter (`status:`)
   - Rebuild `docs/project/work_index.md` via `tcd.sh index`

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
- If the change introduces/depends on an architectural decision, create/update an ADR via `adr-madr-system`.

## Commit hygiene (suggested)

- Small commits aligned to acceptance criteria or plan phases.
- Commit messages reference the task id (e.g. `S03-T-20260130-...`).

## Finishing / integration

When implementation is complete, finish the branch with verification-first workflows.

- If `git-workflow` exists, use `git-workflow/references/finish-branch.md`.
- Otherwise: verify tests, then choose merge vs PR vs keep.

## When to stop and create more artifacts

- If you cannot proceed without a decision: create an ADR.
- If you can proceed but future requirements might be blocked: create a Future entry with a trigger.
- If the task is too large: split into multiple tasks and update the plan.
