# Status Model (Promotion Rules)

This protocol unifies lifecycle states across intake drafts, tasks, and tracks.

## Intake drafts (TD-YYYYMMDD-*.md)

Allowed statuses:
- Draft
- Ready for Review
- Accepted
- Rejected
- Parked

Promotion rule:
- Only **Accepted** intake drafts may be promoted to a Task Brief.

## Task briefs

Status is tracked centrally in `docs/project/task_status.md` (source of truth), and mirrored in the Work Index table.

Allowed statuses:
- Draft
- Approved
- In Progress
- Review
- Done
- Partially Done
- Blocked

Rules:
- Keep task briefs small and disposable; split scope rather than expanding.
- If partially done, create a follow-up task brief and link it.

## Tracks

Tracks organize work at a higher level via `tracks/<slug>/spec.md` and `tracks/<slug>/plan.md`.

Suggested statuses:
- Draft
- Active
- Blocked
- Done

Rules:
- A track must have a spec and plan to move to Active.
- Tracks should link to tasks; tasks should link back to their track.

## Futures

Futures capture deferred, architecture-sensitive requirements.

Suggested statuses:
- Open
- Triggered
- Promoted (to ADR)

Promotion rule:
- When a Future is Triggered, promote the topic to an ADR via `adr-madr-system` (do not rewrite history).
