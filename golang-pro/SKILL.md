---
name: golang-pro
description: Build and review production Go (1.21+) services/CLIs with Go-idiomatic design, correctness, and concurrency. Includes a concurrency playbook and best-practices references (Effective Go, Code Review Comments, context/cancellation).
---

# golang-pro

Write Go that is simple, correct, and production-ready. Default to the standard library and Go idioms.

This skill also covers concurrency patterns (worker pools, pipelines, cancellation, graceful shutdown) and how to avoid common footguns (goroutine leaks, racy access, channel misuse).

## Use this skill when

- Implementing or reviewing Go services/CLIs/libraries.
- Designing or debugging concurrency (goroutines/channels/sync/context).
- Fixing performance, reliability, correctness, or production readiness issues in Go.

## Do not use this skill when

- The task is primarily another language/framework.
- You only need a quick explanation of a small snippet (use a general code explanation skill).

## Workflow (fast + high-signal)

1) Confirm constraints
- Go version, module layout (single module vs workspace), target runtime (container/k8s/serverless), and SLOs.

2) Choose the simplest design that works
- Prefer sequential code until concurrency is required.
- Prefer clear ownership:
  - channels for ownership transfer / pipelines
  - mutexes for shared state

3) Build in cancellation and bounds
- Every goroutine must have an exit path.
- Use `context.Context` for cancellation/timeouts and to stop work promptly.
- Add bounded concurrency for fan-out (semaphore / `errgroup.SetLimit`).

4) Validate with the right tools
- `go test ./...`
- `go test -race ./...` (when concurrency is involved)
- Bench/profile only after establishing a baseline (`go test -bench`, `pprof`).

## Concurrency defaults (opinionated)

- Prefer `errgroup.WithContext` for “N goroutines, return first error, cancel the rest”.
- Use channels to connect pipeline stages; close channels from the sender side only.
- Avoid unbounded goroutine creation; enforce limits and backpressure.
- Avoid `time.Sleep` for synchronization; use `context`, channels, and `sync`.

## References (load as needed)

- Concurrency patterns + corrected templates: `references/concurrency-patterns.md`
- Go best practices + authoritative sources: `references/best-practices.md`

