# Migration Safety (Patterns)

## Default approach

- Expand/contract:
  1) add new columns/tables (expand)
  2) backfill/dual-write (if needed)
  3) switch reads
  4) remove old fields (contract)

## Safety gates

- Backups exist and restore is tested (at least in staging).
- Migration is rehearsed on production-like data size.
- Rollback plan is documented and executable.
- Observability exists for migration progress and impact (latency, errors, locks).

