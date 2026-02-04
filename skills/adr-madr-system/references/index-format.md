# ADR Index Format

Maintain a single ADR index file for discoverability.

Default path: `docs/adr/README.md`

## Managed block (recommended)

To make multi-agent updates deterministic and reduce merge conflicts, keep the table inside a managed block:

```markdown
<!-- ADR-INDEX:START -->
| ID | Title | Status | Date | Deciders | Links | Supersedes | Tags |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ADR-0001 | ... | Accepted | 2026-01-30 | @alice @bob | ./ADR-0001-something.md |  | ... |
<!-- ADR-INDEX:END -->
```

Scripts can safely rebuild only this block without touching other content in `docs/adr/README.md`.

## Table format

Recommended table columns:

- ID
- Title
- Status
- Date
- Deciders
- Links
- Supersedes / Superseded-by
- Tags (optional)

Example:

```markdown
| ID | Title | Status | Date | Deciders | Links | Supersedes | Tags |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ADR-0001 | Use PostgreSQL as primary database | Accepted | 2026-01-30 | @alice @bob | ./ADR-0001-use-postgresql.md |  | data, storage |
| ADR-0007 | Move from X to Y | Accepted | 2026-02-12 | @team | ./ADR-0007-move-x-to-y.md | ADR-0002 | migration |
```

## Update rules

- Add a row for every new ADR.
- When an ADR is superseded:
  - Create a new ADR with a `Supersedes` section.
  - Update the index row(s):
    - New ADR row lists `Supersedes = ADR-XXXX`.
    - Old ADR row changes `Status = Superseded` and can optionally link to the superseding ADR in a `Superseded-by` column if you choose to include it.
- Keep sorting stable:
  - Sort by ADR number (recommended) to avoid churn.
  - If sorting by date, expect more index merge conflicts.
