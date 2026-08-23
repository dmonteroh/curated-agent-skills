# Architecture Patterns (Practical, Backend-Focused)

This is a fast reference for choosing and applying architecture patterns without over-engineering.

## Default guidance (avoid confusion)

- Prefer **one codebase, clear modules** before microservices.
- Prefer **layering and boundaries** over “framework choice wars”.
- Keep decisions reversible: isolate infrastructure behind interfaces where it matters.

## Pattern selection (when to use what)

### Clean Architecture (Layers)

Use when:
- you want strict dependency direction (domain/application independent of frameworks)
- testability and portability matter
- multiple adapters (DB + queue + HTTP) are expected

Avoid when:
- the service is tiny and the layering becomes ceremony

Rule:
- dependencies point inward; outer layers depend on inner layers, never the reverse.

Suggested layers:
- `domain`: core concepts, invariants, domain services (no DB/http)
- `app`: use cases / orchestration (calls domain + ports)
- `ports`: interfaces for persistence/IO
- `adapters`: DB, HTTP, queues implementing ports
- `infra`: wiring, config, server bootstrap

### Hexagonal Architecture (Ports & Adapters)

Use when:
- you want to make IO boundaries explicit (DB, HTTP, queues, third parties)
- you expect multiple adapters (e.g., Postgres + in-memory for tests)

Avoid when:
- the “port” layer is only used to satisfy a pattern and adds no leverage

Rule:
- the core defines ports (interfaces); the outside world supplies adapters.

Contract test:
- write one shared test suite against the port itself and run it against **every** implementation of that port — the real adapter and the in-memory fake the tests use. A fake exercised only through the use cases that consume it drifts into fiction: it passes because it agrees with the expectations written next to it, not because it behaves like the thing it stands in for, and the substitution the port exists to allow stops being safe. *(Authored: the sourced rule says "each adapter implementation"; including the fake in that set is the point of the rule, so it is stated here rather than left implied.)*

### Domain-Driven Design (DDD)

Use when:
- the domain is complex, terminology matters, and boundaries are unclear
- you need explicit consistency boundaries and clear ownership

Avoid when:
- the domain is CRUD-simple; forcing DDD terms adds noise

Rules of thumb:
- Model **invariants** first; choose aggregates around consistency needs.
- Keep interfaces narrow; let callers define interfaces where possible.
- Use domain events when they represent meaningful business facts (not every change).

## Minimal package layout (language-agnostic)

```text
<service>/
  cmd/<service>/        # main / bootstrap
  internal/
    domain/             # entities/value-objects/invariants (no IO)
    app/                # use-cases, orchestration, transactions
    ports/              # interfaces (repositories, clock, idgen, external clients)
    adapters/           # implementations (db, http, queue)
    transport/          # http handlers, grpc handlers (thin)
    infra/              # wiring, config, logging, metrics
  testdata/             # fixtures (if needed)
```

Notes:
- Keep handlers thin: parse/validate -> call app/use-case -> map result.
- Keep DB queries in adapters; keep business rules in domain/app.

## Refactor/migration checklist (use when introducing boundaries)

1) Identify the stable domain concepts and invariants.
2) Draw boundaries:
- what is pure business logic?
- what is IO?
3) Introduce ports only where it buys you:
- external integrations
- persistence that needs to be swap-able/testable
4) Move code incrementally:
- keep behavior the same; add tests around seams
- do not rewrite everything at once
- keep the old entry point and make it delegate to the new use case, so callers stay put while the internals move; delete it only once nothing calls it
- hold a reversible per-slice switch — a route toggle or a flag — until that slice is verified in production, and migrate the next slice only after the previous one has run there
5) Verify dependency direction (no domain importing adapters/infra).

## Compensating workflows across services

Use when a workflow spans several services or steps, no single transaction can cover them, and partial completion therefore has to be undone by explicit compensating actions instead of a rollback. The design output is the ordered step list, one compensation per step, and the rules below — not a framework choice.

### Compensation rules

| Situation | Handling |
| --- | --- |
| Step never started | No compensation; skip it |
| Step completed successfully | Run its compensation |
| Step failed before completing | No compensation for that step; mark the workflow failed |
| Compensation itself fails | Retry with backoff, then dead-letter, then alert a human — never drop it |
| The result the compensation targets no longer exists | Treat the compensation as successful; it is idempotent by contract |

### Rules that decide whether it works

- **A compensation records its completion on every path, including when there was nothing to undo.** A handler that returns silently because the resource was already released leaves the workflow waiting for a signal that never arrives, and it sits in the compensating state indefinitely. Emit the completion event even when the underlying operation was a no-op or raised "already gone".
- **Compensate in reverse order of completion, one step at a time.** Publishing every compensation in one reverse-ordered pass orders only the *dispatch*: independent consumers then run them concurrently, in whatever order they happen to pick the messages up, which is exactly the failure the reverse-order rule exists to prevent. Await each compensation's completion signal before dispatching the next. *(Authored: the sourced material states the reverse-order rule but verifies it by inspecting a dispatch loop's index order, which the concurrent case defeats.)*
- **A deadline per step, never one deadline for the workflow.** A card authorization, a shipping-label creation, and a human approval do not live on the same timescale, so a single global timeout either compensates a slow-but-valid step or waits far too long on a fast one. Size each deadline from that step's own service level; there is no portable default.
- **Every step and every compensation is idempotent.** Commands are redelivered on broker reconnect and replayed when a coordinator restarts mid-workflow. Guard each with an idempotency key and return the recorded result on a repeat rather than acting twice.
- **One correlation id flows through every command, event, and log line** of a workflow instance, and every state transition is logged with it. Without it, a stuck instance cannot be reconstructed from logs after the fact.

### The test that proves the design

Fail the workflow deliberately at each step index in turn and assert the exact set of compensations that ran, and their order. A workflow tested only on the happy path and a first-step failure has never exercised the ordering rule at all. The assertion fails when a compensation is missing, extra, or out of order, which makes it a gate rather than an intention.

### Operability

Expose the workflow's states as first-class signals: instances entering compensation, instances finishing it, and the age of the oldest instance in a non-terminal state. "Stuck" is a duration in a state, so it must be measured as one — a difference between two counters over a window reads identically for a compensation that completed in seconds and one that has been wedged since yesterday. *(Authored: the sourced alert is that counter difference and cannot express duration.)*

