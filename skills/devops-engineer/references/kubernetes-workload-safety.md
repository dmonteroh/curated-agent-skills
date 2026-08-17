# Kubernetes Workload Safety: Probes, API Access, and Disruption

Decision rules for the runtime safety properties of a workload, as distinct from the manifests that express them. Use this when choosing *which* probe, *whether* a workload gets an API credential, and *what* protects it from disruption events that no rollout setting covers.

## Probe selection

Choose the probe by what its failure does, not by which word matches the symptom:

| Probe | What failing it does | Use it for |
| --- | --- | --- |
| `startupProbe` | Kills the container if it has not come up within the budget | Slow-starting runtimes (JVM, large interpreted apps, warm-up caches) |
| `livenessProbe` | Restarts the container | Deadlock and hung-process detection only |
| `readinessProbe` | Removes the pod from Service endpoints; the container keeps running | Temporary inability to serve — a dependency reconnecting, a queue draining, warm-up after start |

Two rules follow from the table:

- **Do not use liveness where readiness is meant.** A liveness probe that checks a downstream dependency restarts a perfectly healthy process every time that dependency blips, turning a short degradation into a crash loop across every replica at once.
- **Readiness and liveness point at different endpoints.** Readiness may check the database, cache, and queue and report unready when they are down. Liveness answers only "is this process still functioning?" and must not consult a downstream — otherwise a downstream outage becomes a cluster-wide restart storm.

## Failure budgets are arithmetic, not vibes

Each probe's tolerance is `failureThreshold × periodSeconds` — how long the condition may persist before the probe's action fires. Configure probes by choosing the budget first and then the two factors that produce it, instead of nudging numbers until the alerts stop.

```yaml
# Illustrative only — the budgets below are invented for the example.
# Derive real ones from this workload's measured cold start and hang behavior.
startupProbe:
  periodSeconds: 5
  failureThreshold: 30   # budget = 30 x 5s = 150s to finish starting
livenessProbe:
  periodSeconds: 30
  failureThreshold: 3    # budget = 3 x 30s = 90s of hang before restart
```

- Measure the workload's cold start on the target environment, take the slowest observed value, add headroom, and make the startup budget at least that. A budget copied from another service is a chosen constant with no relationship to this one.
- The liveness budget trades detection speed against false restarts: shorter restarts a wedged process sooner and a busy one wrongly. State which way the trade was made and why.
- Note the period appears twice — it also sets how often the check costs the service a request. A one-second period on an expensive readiness endpoint is a self-inflicted load.

**Anti-pattern: a long `initialDelaySeconds` in place of a startup probe.** It is an arbitrary wait with a race on both sides — too short and the container is restarted mid-startup, too long and a genuinely wedged process runs unchecked for the whole delay. A startup probe expresses the same intent as a bounded budget that ends the moment the app is actually up.

## Least-privilege API access

Two patterns, and the safe one is the default. The decision is a single question: *does this workload call the control-plane API at all?*

**Pattern A — it does not (most workloads).** Give it a dedicated service account with token automounting disabled, and no Role or RoleBinding whatsoever. There is no credential in the pod to steal.

```yaml
# On the ServiceAccount
automountServiceAccountToken: false
# And again on the pod spec that references it — either setting alone can be
# overridden by the other, so set both.
```

Use a dedicated service account even here: pods that fall back to the namespace's `default` account inherit whatever anyone later binds to it.

**Pattern B — it does (operators, controllers, config watchers).** Enable the token, then grant the minimum:

- A namespace-scoped `Role`, not a `ClusterRole`, unless the workload demonstrably reads across namespaces.
- Only the verbs the code actually calls — `get`, `list`, `watch` for a config watcher; not `*`.
- `resourceNames` pinning access to the specific named objects wherever the API supports it, so read access to one secret is not read access to every secret in the namespace.

**Anti-pattern:** binding `cluster-admin` to an application service account. It is invisible until something is compromised, and then it is total. If a workload appears to need it, the finding is the missing enumeration of what it actually calls.

## Disruption and workload shape

Rollout settings govern deploys. They say nothing about *voluntary disruption* — node drains, cluster upgrades, autoscaler scale-down, maintenance — which can evict pods a deployment strategy never sees.

- Define a `PodDisruptionBudget` for every critical or stateful workload, expressing the floor of pods that must stay available (or the ceiling that may be unavailable) during those events.
- The floor must be greater than zero. `minAvailable: 0` is a budget that permits exactly the disruption it was created to prevent — it exists, it passes review, and it protects nothing.
- Running a single production replica means any drain is an outage; a floor above one replica is the default worth defending, with the exact number chosen per workload from its traffic and the cost of a brief absence rather than copied from a template.
- `maxUnavailable: 0` on a rolling update means the workload never dips below its current replica count during a deploy, at the cost of needing headroom for a surge pod. That is a chosen trade, not a universal setting: it is the right default when capacity is available and a dip is user-visible.
- **A Job with `restartPolicy: Always` is an infinite restart loop**, not a retry policy — the Job never completes because the pod is always restarted. Jobs take `OnFailure` or `Never`.

## Requests and limits: why both, always

Setting only limits is not a shortcut for setting both. When requests are omitted they default to the limits, so the scheduler reserves the ceiling rather than the expected usage and the cluster over-reserves capacity across every such workload. Setting neither leaves scheduling unpredictable and makes one workload able to starve a node.

Where predictable eviction behavior matters more than burst headroom, set the memory limit equal to the memory request: the workload is then scheduled for exactly what it may use, and cannot be evicted for exceeding a reservation it never had. Any specific CPU and memory figures are per-workload and must come from observed usage — a table of "typical" values for a workload class is someone else's measurement of someone else's service.

## Pod safety checklist

Verify each item against the live manifest, not against intent:

**Security**

- Runs as a non-root user with an explicit numeric UID.
- Root filesystem is read-only, with writable paths mounted explicitly where genuinely needed.
- Privilege escalation is disabled.
- All Linux capabilities dropped, with any needed capability added back by name.
- Dedicated service account, not the namespace `default`; token automounting off unless Pattern B applies.
- Permissions namespace-scoped, verb-limited, and name-pinned where possible.
- Secrets come from a secret store or an encrypted-at-rest mechanism, never from plaintext config objects committed to a repository — base64 in a manifest is encoding, not encryption.

**Reliability**

- Startup, liveness, and readiness probes each present and each sized as a stated budget.
- Requests *and* limits on every container.
- A production replica floor above one.
- A disruption budget with a floor above zero for critical or stateful workloads.
- Rollout strategy stated, with its availability trade recorded.

**Observability**

- Distinct endpoints for the liveness check and the dependency-checking readiness check.
- Structured logging with no personal data in log lines.
- Consistent labels for app, version, and environment, so a rollout can be attributed.
