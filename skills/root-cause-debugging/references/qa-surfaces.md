# Re-running the original scenario on the real surface

"Fix verified" means the exact scenario that originally failed, re-run, now produces correct output. Not a similar scenario, not a unit test of the fix. Where the original scenario is genuinely unreproducible — it depended on data state that is gone — construct the closest equivalent, record the difference in the journal, and escalate if the difference is material.

The failure mode this guards against is substitution: exercising a cheaper surface than the one the user touches, and reading its success as the product's.

## Surface table

Pick the row that matches the product. Do not substitute a row that is easier to drive.

| Product surface | Re-running it means |
| --- | --- |
| Command-line tool | Run the actual command end to end in a real terminal session. Capture exit code, stdout, stderr, and the side effects — files created or modified. |
| HTTP API | Start the real server and call the endpoint that reproduced the bug, with real authentication. Inspect status, body, **and** headers. |
| Browser-served application | Drive a real browser through the exact page and flow that failed, with the page's own scripts, cookies, storage, and viewport in play. A request-level HTTP client is not a substitute — it has none of that state. Capture what the browser rendered, not only what the network returned. |
| Model-backed pipeline | Re-send the same input that failed and capture the whole exchange: calls made, messages returned, and usage counters. Zero usage on a response that looks successful is a silent failure, not a pass. |
| Background worker or queued job | Trigger through the normal entry point — the API call, the schedule tick, the published message — and observe completion state in the queue or the store. Calling the worker function directly skips the path where the bug usually lives. |
| Tool server behind a client protocol | Invoke through a real client that performs the protocol handshake, not a bare health or probe endpoint. The handshake is itself a place bugs live. |
| Compiled binary | Re-run the exact command with the exact input. Capture exit code, any signal, and any crash artifact produced. |
| Long-running process | Start fresh and let it run for at least as long as the bug originally took to appear. Capture resource usage throughout — short runs miss leaks and cumulative-state bugs. |

Record each run in the journal: the scenario in one line, the exact invocation, the observed output verbatim and trimmed to the relevant part, the expected output, and a verdict of verified, not verified, or partial.

**Partial is not "mostly done."** A partial or regressed result sends the work back to cause confirmation.

## Silent-failure signals

Run this scan regardless of surface. If the original bug was a silent failure, the same shape often exists in adjacent code that has not been exercised.

- A success status with an empty or default body.
- A success envelope whose inner field carries a failure token — a status, stop reason, or state field that says the operation failed.
- Usage, count, or size counters at zero on a response that reports success.
- Exit code zero with an exception trace on the error stream.
- A panic or exception caught, logged, and then ignored.
- A rejected task, future, or promise with no handler above it.
- A catch or except block with an empty body.
- A falsy check on a field that can hold a meaningful non-null value, so the error branch never runs.
- A write that returned success while a read back shows stale data.
- A job marked complete whose side effect did not happen.
- A cache path returning stale data with no refresh triggered.

Anything found here that is not this bug is **not fixed now**. Record it as a follow-up with its location, the pattern matched, a one-line fix sketch, and what happens if it is left — then report it as a step deliberately not taken.
