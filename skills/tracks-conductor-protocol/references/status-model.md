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
- After promotion, the intake status is stamped `Accepted (promoted to <task-ids> on <date>)` and the file moves to the archive directory (default `docs/project/archive/to-do/`). `tcd.sh archive-promoted` performs this sweep.

## Task briefs

Status is tracked in task frontmatter (`status:`) and mirrored in the Work Index table.

Allowed statuses:
- Draft
- Approved
- In Progress
- Review
- Done
- Partially Done
- Blocked
- split-required
- superseded-by-children

Rules:
- Keep task briefs small and disposable; split scope rather than expanding.
- If partially done, create a follow-up task brief and link it.
- `split-required` and `superseded-by-children` are terminal umbrella-parent statuses: a parent task marked for splitting is never dispatched, and once its child tasks exist it is superseded (and can be archived). Child tasks reuse the parent sequence with an alpha suffix (e.g. `S12a`, `S12b`).
- Statuses are a closed enum; `tcd.sh validate` rejects ad-hoc values.

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
- When a Future is Triggered, promote the topic to an ADR using the repo's ADR format (do not rewrite history).
