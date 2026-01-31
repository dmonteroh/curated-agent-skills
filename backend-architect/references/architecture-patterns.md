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
5) Verify dependency direction (no domain importing adapters/infra).

