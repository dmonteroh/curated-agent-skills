---
name: golang
description: Build and review production Go (1.21+) services/CLIs with idiomatic design, correctness, and safe concurrency/cancellation patterns.
category: language
---

# golang

Provides guidance for writing simple, correct, production-ready Go. Defaults to the standard library and Go idioms.

This skill covers concurrency patterns (worker pools, pipelines, cancellation, graceful shutdown) and common footguns (goroutine leaks, racy access, channel misuse).

## Use this skill when

- Implementing or reviewing Go services/CLIs/libraries.
- Designing or debugging concurrency (goroutines/channels/sync/context).
- Fixing performance, reliability, correctness, or production readiness issues in Go.

## Do not use this skill when

- The task is primarily another language/framework.
- You only need a quick explanation of a small snippet without broader Go changes.

## Trigger phrases

- "Go service", "Go CLI", "Go module", "Go handler"
- "goroutine leak", "channel deadlock", "errgroup"
- "context cancellation", "graceful shutdown"

## Required inputs

- Go version target and module layout (single module vs workspace).
- Execution environment (container/k8s/serverless/CLI) and lifecycle constraints.
- Performance expectations, SLOs, and concurrency requirements.
- Existing tests, benchmarks, or tooling expectations.

## Workflow (fast + high-signal)

1) Confirm constraints
- Requests missing required inputs.
- Output: confirmed Go version, runtime context, and constraints.

Decision: If constraints are unclear, stop and request clarification before coding.

2) Choose the simplest design that works
- Prefers sequential code until concurrency is required.
- Prefers clear ownership:
  - channels for ownership transfer / pipelines
  - mutexes for shared state
- Output: proposed design and whether concurrency is needed.

Decision: If concurrency is not required, keep the solution sequential.

3) Build cancellation, bounds, and ownership
- Ensures every goroutine has an exit path.
- Uses `context.Context` for cancellation/timeouts and to stop work promptly.
- Adds bounded concurrency for fan-out (semaphore / `errgroup.SetLimit`). Only use `errgroup` if the module already includes `golang.org/x/sync`; otherwise use `sync.WaitGroup` + error channel.
- Output: list of goroutines, their owners, and cancellation signals.

4) Implement changes and document behavior
- Keeps APIs small; returns errors with context.
- Output: change summary and key files touched.

5) Validate with the right tools
- Runs `go test ./...`.
- Runs `go test -race ./...` when concurrency is involved.
- Bench/profiles only after establishing a baseline (`go test -bench`, `pprof`).
- Output: verification commands run and results, or a reason if skipped.

## Concurrency defaults (opinionated)

- Prefer `errgroup.WithContext` for “N goroutines, return first error, cancel the rest”.
- Use channels to connect pipeline stages; close channels from the sender side only.
- Avoid unbounded goroutine creation; enforce limits and backpressure.
- Avoid `time.Sleep` for synchronization; use `context`, channels, and `sync`.

## Common mistakes to avoid

- Spawning goroutines without an exit path or owner.
- Closing channels from the receiver side.
- Using unbounded fan-out or buffered channels as a queue substitute.
- Ignoring `ctx.Done()` in long-running loops.
- Using `context.Background()` inside request handlers.

## Examples

### Example: implement bounded fan-out

Input:
"Add parallel fetches to this Go handler, but ensure cancellation and a 5-worker limit."

Expected behavior:
- Propose `errgroup.WithContext` plus `SetLimit(5)`.
- Ensure each request uses the provided `context.Context`.
- Report the concurrency limit and cancellation path.

### Trigger test

"We're seeing goroutine leaks in our Go worker pool; help fix it."

## Output contract

When executing this skill, report:

- Summary of approach and key decisions.
- Files changed (with paths).
- Verification commands run and results (or why skipped).
- Risks, edge cases, or follow-ups.

Reporting format:
- Summary
- Files changed
- Verification
- Risks/follow-ups

## References (load as needed)

- Index: `references/README.md`
- Concurrency checklist + footguns: `references/concurrency-checklist.md`
- Concurrency templates: `references/concurrency-templates.md`
- Go best practices + authoritative sources: `references/best-practices.md`
