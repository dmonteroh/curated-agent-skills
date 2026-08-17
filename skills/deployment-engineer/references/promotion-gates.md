# Promotion Gates: Undecided Outcomes, Approver Sets, and Readiness Depth

Depth for the two gate-integrity decision points in `SKILL.md`. Use this when writing the actual pass/fail/undecided logic of a gate that promotes a release between environments — not when merely listing that a gate exists.

The failure this reference guards against is not a release that fails. It is a release that never resolves: a pipeline sitting on a gate that cannot decide, with no failure to alert on and no owner to notify.

## The third outcome

A gate has three possible states, and only two of them are usually designed:

| Outcome | Signal | Pipeline behavior |
| --- | --- | --- |
| Pass | Present, within criteria | Promote |
| Fail | Present, outside criteria | Stop, alert, roll back per the rollback plan |
| Undecided | Absent, unparseable, or unattributed | **Undefined unless designed** — the default is to wait forever |

Two concrete shapes of the same bug:

- **The metric gate with no data.** A gate that promotes when an error-rate query stays under a threshold cannot evaluate a query that returns an empty result. A renamed metric, a scrape target that stopped reporting, or an exporter that is down all produce "no data", which is neither above nor below the threshold. The rollout neither promotes nor aborts. Nothing has failed, so nothing pages.
- **The approval gate with no approver.** An approval gate whose reviewer set is empty, or points at a disbanded team or a departed account, waits for an approval that no human has been asked for. The pipeline reports "awaiting approval" indefinitely and the notification goes nowhere.

## Designing the undecided path

For each gate in the pipeline, write down four things:

1. **What "absent" looks like, distinct from "failing".** Name the concrete condition: empty query result, timed-out request, unparsed response body, missing artifact, no approver assigned. A gate that maps absent onto failing must say so deliberately — that is a design choice (fail-closed), not a default to fall into.
2. **The bound on staying undecided.** Either a count of consecutive inconclusive evaluations or a wall-clock ceiling. Both are chosen defaults, not measured thresholds: pick one per gate from the release cadence and the cost of a stalled pipeline, and record it as a chosen value rather than as a rule. Different gates deserve different bounds — a metric query that samples every minute and an approval that waits for a working day are not the same clock.
3. **What reaching the bound means.** Two defensible answers, and the choice must be explicit: *fail-closed* (treat expiry as a failure, abort and roll back — correct when an unobservable release is an unsafe release) or *escalate* (notify a named owner and hold — correct when aborting costs more than waiting and someone is genuinely on the hook). "Keep waiting" is not one of the answers.
4. **Who is told.** An undecided gate that stalls silently is the failure mode. Whichever branch is chosen, the expiry emits a message naming the gate, the missing signal, and the owner.

## Design-time gate audit

Run this before the pipeline ships, not during a release:

- Every approval gate resolves to a **non-empty** approver set, and every identity in that set still exists and is reachable. A gate referencing a group is only as valid as that group's current membership.
- Every metric-driven gate names the specific query it depends on, and that query returns data *now* — an empty result at design time is an unset gate, not a passing one.
- Every gate has a stated bound and a stated expiry branch from the section above.
- Confirm the failure is visible: force one gate into its undecided state (point it at a metric name that does not exist, or clear its reviewer set in a non-production copy) and check that the pipeline resolves within the bound and that the message reaches its named owner. A gate whose undecided path has never been exercised is an assumption, not a control.

## Readiness depth for a health gate

A gate that polls a health endpoint is only as good as what that endpoint checks.

- **Liveness** answers "is this process still running and worth keeping alive?" It must not fail because a downstream dependency is unavailable — a process restarted over a transient database blip turns a small outage into a crash loop.
- **Readiness** answers "can this instance serve traffic right now?" It verifies the dependencies the service actually needs — database, cache, queue, downstream services — and returns a non-2xx status when any of them is down.

A promotion gate uses readiness. A shallow endpoint that returns 200 as soon as the HTTP server binds proves only that the process started; a deploy where every dependency is misconfigured passes it. Keep the two endpoints separate and let each return the detail of which checks failed, so a failing gate names the broken dependency instead of just "unhealthy".

**Contrast:**

```text
# Wrong: the gate proves the process is up, nothing more.
poll /ping until 200  ->  promote

# Right: the gate proves the instance can serve, and cannot wait forever.
poll /health/ready (checks db, cache, queue; 503 if any down)
  pass on first 200            -> promote
  still not 200 at the ceiling -> fail the deploy and roll back
```

## Bounding the wait

The wait on a readiness gate is the undecided bound from the first section, wearing different clothes: "not yet healthy" is an absent verdict, not a failing one.

- Poll at a fixed interval and pass on the first healthy response, rather than sleeping for a fixed duration and checking once. A single check after a fixed sleep either wastes the difference or fails a service that was two seconds late.
- Cap the wait with a maximum attempt count or a wall-clock ceiling, and fail the deploy when it is reached. Without a cap, a service that never starts holds the pipeline open until a human notices.
- Derive the interval and the ceiling from this service's observed startup time — measure a cold start on the target environment and leave headroom for the slowest one seen. Poll counts and sleep durations copied from another pipeline are chosen constants with no relationship to this workload; if one is carried anyway, record it as a starting default to be replaced once startup time is measured.
- Report the elapsed time on both branches. A gate that passes on the last attempt every time is a ceiling about to become a false failure.
