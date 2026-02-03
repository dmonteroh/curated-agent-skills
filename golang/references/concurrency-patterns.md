# Go Concurrency Patterns (Production Templates)

This reference is a practical playbook for writing safe, bounded, cancellation-aware concurrency in Go.

Defaults:
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

## Pattern: Worker pool (bounded, cancellable)

Use when you have a stream of jobs and want fixed concurrency.

```go
package workerpool

import (
	"context"
	"sync"
)

type Job struct {
	ID   int
	Data string
}

type Result struct {
	JobID  int
	Output string
	Err    error
}

func Run(ctx context.Context, workers int, jobs <-chan Job, process func(context.Context, Job) (string, error)) <-chan Result {
	results := make(chan Result)

	var wg sync.WaitGroup
	wg.Add(workers)
	for i := 0; i < workers; i++ {
		go func() {
			defer wg.Done()
			for {
				select {
				case <-ctx.Done():
					return
				case job, ok := <-jobs:
					if !ok {
						return
					}
					out, err := process(ctx, job)
					select {
					case <-ctx.Done():
						return
					case results <- Result{JobID: job.ID, Output: out, Err: err}:
					}
				}
			}
		}()
	}

	go func() {
		wg.Wait()
		close(results)
	}()

	return results
}
```

## Pattern: Fan-out / fan-in pipeline (with cancellation)

Use when you have staged transformations and want parallelism per-stage.

Key idea: each stage:
- reads from `in`,
- writes to `out`,
- stops on `ctx.Done()`,
- closes `out` when it returns.

```go
package pipeline

import (
	"context"
	"sync"
)

func generate(ctx context.Context, nums ...int) <-chan int {
	out := make(chan int)
	go func() {
		defer close(out)
		for _, n := range nums {
			select {
			case <-ctx.Done():
				return
			case out <- n:
			}
		}
	}()
	return out
}

func square(ctx context.Context, in <-chan int) <-chan int {
	out := make(chan int)
	go func() {
		defer close(out)
		for {
			select {
			case <-ctx.Done():
				return
			case n, ok := <-in:
				if !ok {
					return
				}
				select {
				case <-ctx.Done():
					return
				case out <- n * n:
				}
			}
		}
	}()
	return out
}

func merge(ctx context.Context, cs ...<-chan int) <-chan int {
	out := make(chan int)
	var wg sync.WaitGroup
	wg.Add(len(cs))

	for _, c := range cs {
		c := c
		go func() {
			defer wg.Done()
			for {
				select {
				case <-ctx.Done():
					return
				case n, ok := <-c:
					if !ok {
						return
					}
					select {
					case <-ctx.Done():
						return
					case out <- n:
					}
				}
			}
		}()
	}

	go func() {
		wg.Wait()
		close(out)
	}()
	return out
}
```

## Pattern: “N goroutines, fail fast” with `errgroup`

Use when you want:
- return the first error,
- cancel the rest,
- optionally cap concurrency.

```go
package fanout

import (
	"context"
	"fmt"
	"io"
	"net/http"

	"golang.org/x/sync/errgroup"
)

func fetchAll(ctx context.Context, urls []string, maxConcurrent int) ([]string, error) {
	g, ctx := errgroup.WithContext(ctx)
	if maxConcurrent > 0 {
		g.SetLimit(maxConcurrent)
	}

	results := make([]string, len(urls))
	for i, url := range urls {
		i, url := i, url
		g.Go(func() error {
			req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
			if err != nil {
				return fmt.Errorf("new request %s: %w", url, err)
			}
			resp, err := http.DefaultClient.Do(req)
			if err != nil {
				return fmt.Errorf("do request %s: %w", url, err)
			}
			defer resp.Body.Close()

			// If the body matters, read it here; keeping it minimal as an example.
			io.Copy(io.Discard, resp.Body)

			results[i] = resp.Status
			return nil
		})
	}

	if err := g.Wait(); err != nil {
		return nil, err
	}
	return results, nil
}
```

## Pattern: Graceful shutdown (context + waitgroup)

Use in `main` to stop background goroutines and servers cleanly.

```go
package shutdown

import (
	"context"
	"os"
	"os/signal"
	"syscall"
)

func SignalContext(parent context.Context) (context.Context, func()) {
	ctx, cancel := context.WithCancel(parent)
	ch := make(chan os.Signal, 1)
	signal.Notify(ch, syscall.SIGINT, syscall.SIGTERM)
	go func() {
		select {
		case <-ctx.Done():
		case <-ch:
			cancel()
		}
	}()
	return ctx, func() {
		signal.Stop(ch)
		cancel()
	}
}
```

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

