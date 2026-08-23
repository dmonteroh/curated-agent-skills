# Flaky-Test Triage

Read this when a failure does not reproduce on every run: "fails sometimes", "a different test each run", "passes in isolation", "only fails in CI". Intermittence is itself evidence, and reading it first usually collapses the search space before anyone forms a theory about the code.

## Step 1 — Capture the failure signature

Run these before forming any hypothesis, and record the result of each. The first three are always worth their cost; the fourth is conditional.

| Rerun | Command shape | Question it answers |
|---|---|---|
| Same scope, same command | exactly what just failed | Does the *same* test fail again, or a different one? |
| Failing test in isolation | single file or test filter | Does it pass alone? |
| Full scope on a quiet machine | stop concurrent builds, suites, and background agents first | Does the whole suite go green when nothing else is running? |
| Shuffled, when order is suspect | the runner's shuffle or random-seed flag | Does a specific order reproduce it? Record the seed. |

A rerun whose result was not written down is not a signature. The whole method rests on comparing runs, and a remembered run cannot be compared.

## Step 2 — Read the signature

| Signature | Dominant hypothesis | Next move |
|---|---|---|
| Same test fails intermittently, everywhere | A real race in the code under test, or an async test bug: a fixed sleep, an unawaited promise, polling on wall-clock time | Reproduce deterministically by subscribing to the completion event or injecting a clock, then treat it as the code defect it is |
| A different test or file each run; each passes in isolation; the quiet machine is green | Environment contention between concurrent runs — not the code, and not any one test | Step 3 checklist |
| Always the same test, but only in the full suite; isolation is green | Test-order dependence or a fixture leak: unreset module state, a leaked env var, a shared singleton | Bisect with the recorded shuffle seed, find the test that leaks, fix its teardown |
| Fails only in CI, never locally | Resource ceilings (slower disk or CPU pushing past timeouts), different parallelism defaults, container clock | Reproduce locally under the same constraint — pin CPUs, drop the worker count — and raise the *signal*, not the sleep |
| Green on a plain rerun of the same commit | Still a flake. Classify it with this table before ignoring it; an unclassified flake is a hidden bug report | Step 1 again, with the results written down |

## Step 3 — Concurrent-run contention checklist

The common modern cause: two checkouts or worktrees of the same repository — or one checkout plus a background agent — running suites at the same time while sharing a global mutable resource. Workstations that run several agents make this an ordinary failure mode rather than an exotic one. Check each:

- **Shared tmp roots.** A sandbox or cache directory derived from a fixed path (`$TMPDIR/<project>-fixed-name`) instead of a per-run temporary directory. Both runs read and write the same tree, and the loser sees half-deleted state.
- **Fixed ports.** Hardcoded listen ports in test servers. Two suites race to bind, and the loser gets connection refusals or 404s partway through whichever file happened to be running.
- **Global env or config mutation.** Tests writing process-external state — dotfiles, shared config, global environment — that the other run reads.
- **Shared containers or databases.** Same container name, same schema, same volume.
- **Caches and locks.** Package-manager caches, lockfiles, version-control index contention.

Capture the evidence while the failure is live, because it disappears with the run: what holds the contended port (`lsof -i :<port>`), a listing of the shared temporary path, and a process list showing the concurrent runners.

## Step 4 — Fix policy

Fix the class, not the instance.

- **Environment contention** → fix the test infrastructure, never the individual test. Namespace every suite-global resource per run: a fresh temporary directory per run, an ephemeral port (bind port `0` and read back what was assigned), a unique container name. The bar is stated as a condition that can fail: two checkouts of this repository running the suite concurrently must not interfere.
- **Order dependence** → find the leaking fixture using the recorded shuffle seed, reset it at teardown, and re-run shuffled until that seed class is clean.
- **A real race in the code under test** → this is a defect in the product, not in the tests. It ships with a test that fails first and reproduces the race deterministically.
- **Forbidden regardless of cause:** a retry wrapper around the test, an enlarged sleep, a per-test retry count, quarantining the test, or deleting it. Each one buries a bug report that has already been written.

*(Authored reconciliation. The automation-mode stability plan in this skill's entry point allows retries at the framework edge as a blunt backstop for an unclassified suite. This policy governs a flake that has been classified: once its signature is known it is a known bug, and retrying a known bug hides it.)*

A flake that was classified but not fixed is a finding to report, not to drop: record the signature, the evidence, and the classification, and state them as risks and gaps when reporting the result.
