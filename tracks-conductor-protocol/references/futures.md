# Futures (Unified Handling)

Futures capture deferred requirements that are architecture-sensitive (compliance, scale bottlenecks, identity evolution).

This protocol supports two modes:

## Mode A (default): File-per-entry + index

Recommended for multi-agent work to reduce merge conflicts.

Default directory: `docs/project/futures/`

Filename: `FUT-XXX-<short-slug>.md`

Template (recommended fields):
- ID
- Topic
- Status: Open | Triggered | Promoted
- Strategy (high-level pivot)
- Trigger (promotion condition)
- Links (tracks/tasks/ADRs)

The Work Index (`docs/project/work_index.md`) is the discoverability layer.

## Mode B (compat): Ledger file

If a repo already uses a ledger (e.g. `docs/architecture/futures_ledger.md`), this protocol can coexist:
- Continue using the ledger as source of truth
- Add a link to it in the Work Index
- When a trigger fires, promote to an ADR via `adr-madr-system`

## Promotion rule

When a Future becomes current:
- mark it Triggered
- create an ADR (new decision)
- link ADR <-> track spec/plan
