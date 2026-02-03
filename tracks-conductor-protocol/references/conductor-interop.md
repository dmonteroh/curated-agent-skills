# Conductor Interop (Condensed)

Conductor is a plugin-driven workflow that maps closely to Tracks Conductor Protocol. Use this mapping if a repo already uses Conductor artifacts.

## Command Mapping

- `/conductor:setup` -> `scripts/tcd.sh init`
- `/conductor:new-track` -> `scripts/tcd.sh track "<Track title>"`
- `/conductor:implement` -> `references/execution-playbook.md`
- `/conductor:status` -> `docs/project/work_index.md` + `docs/project/task_status.md`
- `/conductor:revert` -> use VCS tools + track/task registry
- `/conductor:manage` -> archive/restore tracks under `docs/project/tracks/`

## Artifact Mapping

Conductor:
- `conductor/product.md`
- `conductor/tech-stack.md`
- `conductor/workflow.md`
- `conductor/tracks/<id>/{spec.md,plan.md}`

Tracks Conductor Protocol:
- `docs/context/product.md`
- `docs/context/tech-stack.md`
- `docs/context/workflow.md`
- `docs/project/tracks/<slug>/{spec.md,plan.md}`

If a repo already uses Conductor, prefer its existing paths and link them from the index.
