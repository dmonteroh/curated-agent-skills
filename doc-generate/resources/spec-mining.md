# Spec Mining (Reverse-Spec from Code)

This resource describes a fast, repeatable approach to reverse-engineer a **baseline spec** from an existing repo when requirements are missing or stale.

Goal: produce a single “reverse-spec” doc that is **grounded in reality** (code, config, tests, observed behavior) and is easy to refine with stakeholders.

## Outputs (minimum)

One file: `docs/specs/reverse-spec.md` containing:
- **Scope & actors**: who uses the system, what they do.
- **Functional requirements** in EARS format.
- **Non-functional requirements** discovered or implied (security, reliability, performance, auditability).
- **Constraints / invariants** (things the system must never violate).
- **Assumptions** (explicitly marked).
- **Open questions** + follow-up work items.

## Workflow

1) Inventory truth sources:
- Routes/endpoints, CLI commands, cron/jobs/workers
- DB schema/migrations
- Authn/authz and tenancy/partitioning rules
- Config/env vars and feature flags
- Tests (especially integration/e2e)
- Operational docs/runbooks (if any)

2) Two-pass reading (fast + thorough):
- **Arch pass**: entry points, service boundaries, major data flows, persistence, integrations.
- **QA pass**: observable behaviors, validation, error handling, edge cases, retries/timeouts.

3) Write “what it does” before “how it does it”:
- Prefer externally observable behavior, invariants, and contracts.
- Avoid internal implementation details unless they imply constraints.

4) Express behavior as EARS requirements:

Use these patterns (pick the simplest that fits):
- **Ubiquitous**: `The system SHALL <capability>.`
- **Event-driven**: `WHEN <trigger> THEN the system SHALL <response>.`
- **Unwanted behavior**: `IF <unwanted condition> THEN the system SHALL <mitigation>.`
- **State-driven**: `WHILE <state> the system SHALL <response>.`
- **Optional feature**: `WHERE <feature enabled> the system SHALL <response>.`

5) Keep a strict separation:
- **Observed** (confirmed in code/tests) vs **Assumed** (not confirmed).
- If unsure, add an open question instead of inventing behavior.

## Evidence Rules (multi-agent friendly)

- Every non-trivial requirement should include an **Evidence** line pointing to code/config/tests (file path + optional symbol/line).
- Prefer “Observed” statements; label inferences explicitly.
- If evidence is unclear, record an open question instead of guessing.

Suggested tagging:
- `OBS-<AREA>-###` for observed requirements (e.g., `OBS-AUTH-001`).
- `INF-<AREA>-###` for inferences.

## Fast Search Patterns (optional)

Use ripgrep/`find` to locate likely truth quickly:

- Entry points: `**/main.*`, `**/app.*`, `**/index.*`, `cmd/**/main.go`
- HTTP routing: `router.`, `app.get`, `app.post`, `MapGet`, `MapPost`, `chi.Router`, `HandleFunc`
- Auth: `jwt`, `oauth`, `bearer`, `middleware`, `guard`, `policy`, `Authorize`, `RBAC`, `claims`
- Migrations/schema: `migrations/`, `schema.sql`, `*.sql`, `prisma/schema.prisma`, `db/migrate`
- Config/env: `.env`, `appsettings`, `config.*`, `values.yaml`, `helm`, `terraform`
- Tests: `*.spec.*`, `*.test.*`, `e2e`, `integration`, `playwright`, `dockertest`

## Reverse-Spec Template (copy/paste)

## Reverse-Spec Template (copy/paste)

```md
# Reverse Spec (Derived from Code)

Generated: YYYY-MM-DD (UTC)
Source: repo scan + code/config/tests

## Scope

- In scope:
- Out of scope:

## Actors & Primary Flows

- Actor: ...
  - Flow: ...

## Functional Requirements (EARS)

### Authentication / Authorization
- OBS-AUTH-001: WHEN ... THEN the system SHALL ...
  - Evidence: `path/to/file.ext:123` (or symbol name)

### Core Behaviors
- OBS-CORE-001: The system SHALL ...
  - Evidence: `path/to/file.ext:123`

### Error Handling
- OBS-ERR-001: IF ... THEN the system SHALL ...
  - Evidence: `path/to/file.ext:123`

## Non-Functional Requirements (Discovered / Implied)

- Security:
- Reliability:
- Performance:
- Observability:
- Privacy/Compliance:

## Constraints & Invariants

- Invariant:

## Data & State (External Contracts)

- Entities:
- Identifiers:
- Versioning / concurrency:

## Assumptions

- Assumption (needs confirmation):

## Open Questions / Follow-Ups

- Question:
```
