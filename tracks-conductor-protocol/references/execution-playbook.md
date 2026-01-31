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
   - Update `docs/project/task_status.md`
   - Rebuild `docs/project/work_index.md` via `tcd.sh index`

## Verification checklist (minimum)

- Acceptance criteria satisfied (explicitly check each).
- Key risks mitigated or explicitly accepted.
- No untracked scope expansion:
  - If new work is discovered, create a new intake or task.
- If the change introduces/depends on an architectural decision, create/update an ADR via `adr-madr-system`.

## Commit hygiene (suggested)

- Small commits aligned to acceptance criteria or plan phases.
- Commit messages reference the task id (e.g. `S03-T-20260130-...`).

## When to stop and create more artifacts

- If you cannot proceed without a decision: create an ADR.
- If you can proceed but future requirements might be blocked: create a Future entry with a trigger.
- If the task is too large: split into multiple tasks and update the plan.
