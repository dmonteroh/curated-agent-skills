# Go Concurrency Checklist

Provides a checklist to validate concurrency designs and spot common failure modes.

## Defaults

- Prefer `context.Context` for cancellation and deadlines.
- Prefer bounded fan-out (`errgroup.SetLimit` or a semaphore).
- Avoid goroutine leaks: every goroutine needs an exit path.

## Quick checklist

- Do we actually need concurrency? (Prefer sequential until proven otherwise.)
- Who owns each goroutine and who cancels it?
- Is concurrency bounded?
- Who closes each channel? (Sender closes; receiver never closes.)
- Are error paths and `ctx.Done()` handled?
- Can this deadlock or leak if the consumer stops reading?

## Race detection (must-use for concurrency work)

```sh
go test -race ./...
```

## Common footguns (avoid)

- Using `len(jobs)` on a channel (does not do what you want).
- Spawning goroutines in loops without bounds or cancellation.
- Closing a channel from the receiver side.
- Using `time.Sleep` for synchronization.
- Using `select { default: }` in a tight loop (burns CPU).
