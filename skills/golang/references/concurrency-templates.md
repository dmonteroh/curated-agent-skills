# Go Concurrency Templates

Provides templates for bounded, cancellation-aware concurrency. The examples are minimal and focus on safe shutdown and ownership.

## Pattern: Worker pool (bounded, cancellable)

Applies when there is a stream of jobs and fixed concurrency is required.

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

Applies when there are staged transformations and parallelism per-stage is required.

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

Applies when the workflow needs to:
- return the first error,
- cancel the rest,
- optionally cap concurrency.

Requires module import: `golang.org/x/sync/errgroup`.

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

Applies in `main` to stop background goroutines and servers cleanly.

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
