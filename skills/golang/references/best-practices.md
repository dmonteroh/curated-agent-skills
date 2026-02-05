# Go Best Practices (High Signal)

Provides rules of thumb that tend to produce the best Go code in collaborative environments.

## Core principles

- Prefer clarity over cleverness.
- Keep APIs small; make the zero value useful where reasonable.
- Prefer composition; keep interfaces narrow and consumer-defined.
- Return errors, don’t panic (except truly unrecoverable programmer errors in `main`/tests).

## Error handling

- Wrap errors with context using `%w` so callers can `errors.Is/As`.
- Don’t hide errors; propagate them with enough information to debug.
- Keep sentinel errors rare; prefer typed errors only when callers need branching behavior.

## Concurrency & cancellation

- Every goroutine must have:
  - a clear owner,
  - a way to stop (context / close / done signal),
  - a bounded input (avoid unbounded fan-out).
- Prefer `errgroup.WithContext` for concurrent fan-out where any error should cancel the rest.
- Use channels for ownership transfer and pipelines; use mutexes for shared mutable state.
- Close channels from the sender side only; never close a channel you didn’t create.
- Avoid `select { default: }` busy loops; add blocking ops or timers/tickers.

## Context usage

- Pass `context.Context` explicitly (first param) down the call stack.
- Never store contexts in structs for later use.
- Don’t use `context.Background()` inside request handlers (use the request context).

## Testing & maintainability

- Prefer table-driven tests for edge cases and consistency.
- Run `go test -race ./...` for concurrency-sensitive code.
- Keep packages small; avoid cyclic dependencies; don’t over-export.

## Tooling & hygiene

- Format with `gofmt` (always) and keep `go vet` and static analysis clean.
- Prefer standard layouts (but don’t bikeshed); make module boundaries explicit.

## Authoritative references (worth following)

```text
Effective Go:
  https://go.dev/doc/effective_go

Go Code Review Comments (style/idioms and common pitfalls):
  https://go.dev/wiki/CodeReviewComments

Go blog: Pipelines and cancellation patterns:
  https://go.dev/blog/pipelines

Go blog: Context usage (cancellation/deadlines):
  https://go.dev/blog/context
```
