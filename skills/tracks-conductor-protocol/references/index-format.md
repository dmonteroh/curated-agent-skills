# Index Format (Managed Blocks)

This protocol uses a single index file with managed blocks so multiple agents can update work deterministically.

Default: `docs/project/work_index.md`

## Managed block markers

Each table lives inside markers:

```markdown
<!-- TCD:INTAKE:START -->
| ID | Title | Status | Date | Owner | Links | Track | Tags |
| --- | --- | --- | --- | --- | --- | --- | --- |
<!-- TCD:INTAKE:END -->

<!-- TCD:TASKS:START -->
| ID | Title | Status | Seq | Date | Links | Track | ADRs | Futures |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
<!-- TCD:TASKS:END -->

<!-- TCD:TRACKS:START -->
| Track | Title | Status | Owner | Links | ADRs | Futures |
| --- | --- | --- | --- | --- | --- | --- |
<!-- TCD:TRACKS:END -->

<!-- TCD:FUTURES:START -->
| ID | Topic | Status | Strategy | Trigger | Links |
| --- | --- | --- | --- | --- | --- |
<!-- TCD:FUTURES:END -->
```

## Update rules

- Scripts should only rewrite content between START/END markers.
- Sort deterministically to reduce churn:
  - Intake: by id (TD ids embed the date, so this is chronological)
  - Tasks: by numeric sequence, then alpha suffix (S2 < S10 < S10a < S100)
  - Tracks: by track slug
  - Futures: by id
- The index is a *view*; sources of truth remain the individual files (`to-do/`, `tasks/`, `tracks/`, `futures/`).
