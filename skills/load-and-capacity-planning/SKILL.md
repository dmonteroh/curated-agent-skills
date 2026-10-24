---
name: load-and-capacity-planning
description: "Plans load tests with pass criteria fixed beforehand and turns measured saturation points into capacity limits, headroom and scale triggers. Use to validate expected traffic before a launch, find a service's breaking point, or forecast when resources run out."
metadata:
  category: observability
---
# Load and Capacity Planning

Provides a process for testing a service against a stated traffic target, locating where it saturates, and converting that measurement into headroom, scaling triggers and a forecast with a date on it.

## Use this skill when

- A launch, campaign or migration must be validated against expected traffic before it happens.
- The breaking point or safe operating limit of a service is unknown.
- Someone asks when CPU, memory, disk or connections will run out, or how many instances a target load needs.
- Autoscaling thresholds or capacity alerts need a measured basis instead of a guess.

## Do not use this skill when

- The task is finding why one code path is slow; profile that path instead of testing at scale.
- The service needs logs, traces or alerts designed; that is instrumentation work, not load work.
- A single latency regression needs a before-and-after benchmark of one function.
- The question is cloud pricing or cost optimisation with no traffic or resource model.

## Required inputs

- Traffic target: peak requests per second or concurrent users, and where the number comes from.
- Latency and error limits the service must hold at that target.
- A test environment and how closely it matches production (size, data volume, dependencies).
- Existing utilisation history, if a forecast is wanted.

## Workflow

1. **Fix the pass criteria before running.** Write the target load, p95 and p99 latency limit, error-rate limit and the saturation signal to watch (CPU, pool wait, queue depth). A test with no written criteria cannot fail, so do not run it.
   - Output: test charter with numeric pass and fail lines.
2. **Pick the test type from the question.**
   - Load: does the target traffic pass the criteria.
   - Stress: where does it break and how.
   - Spike: does it survive and recover from a sudden jump.
   - Soak: does anything leak over hours.
3. **Build a representative workload.** Use journey mixes taken from production traffic, realistic data volume and think time, and a request distribution that does not hit one cached row. Drive arrival rate (open model) when real users arrive independently of response time; a fixed-user loop slows its own load when the server slows and hides the failure.
4. **Run and watch the service, not only the client.** Record saturation per resource while load ramps. Stop and discard the run if the load generator itself is saturated or errors originate in the test harness.
   - Output: latency and error curves against load, with the first resource to saturate named.
5. **Convert to capacity.** Take the load at which the first criterion fails; set the safe operating limit below it with stated headroom for failure of one instance and for traffic growth. Compute instance count from that limit, not from average utilisation.
   - Output: per-instance limit, headroom, instances needed at target.
6. **Set triggers and forecast.** Scale or alert at a utilisation that leaves more lead time than provisioning takes. Forecast from at least one full seasonal cycle of history and backtest it: run the model on past data, compare with what happened, and report the error.
   - Output: scaling thresholds, forecast with date and error band.
7. **State what the test did not prove.** Name each difference between the test environment and production (data size, dependencies stubbed, network) as a limit on the result.

## Examples

Input: "We expect 2x traffic at launch. Validate it."

Weak: ramp to 200 virtual users, report "p95 was fine".

Better:
- Charter: 1,200 rps mixed 60% search, 30% browse, 10% checkout; p95 under 500 ms, error rate under 0.5%, DB pool wait under 50 ms.
- Run: open-model ramp 300 to 1,500 rps over 15 minutes, 15 minutes steady at 1,200.
- Finding: passes at 1,200 rps; p95 crosses 500 ms at 1,380 rps when the DB pool saturates.
- Capacity: safe limit 1,100 rps per this deployment (one instance loss plus 20% headroom); scale out trigger at 70% pool use.
- Unproven: test database held 10% of production rows.

## Output contract

- **Charter**: target, criteria, test type and why.
- **Results**: load against latency, errors and saturation, with the first limit named.
- **Capacity**: limit, headroom, instance count, scaling triggers.
- **Forecast**: date and error band, with the backtest result.
- **Unproven**: environment differences and untested paths.

## Resources

| Topic | Reference | Load when |
|-------|-----------|-----------|
| k6 | `references/performance-testing-k6.md` | Load, stress, spike and soak scripts |
| Other tools | `references/performance-testing-tools.md` | Artillery, Locust, JMeter |
| Scenarios | `references/performance-testing-scenarios-metrics.md` | Journeys and custom metrics |
| Forecasting | `references/capacity-planning-forecasting.md` | Trends and exhaustion queries |
| Resource models | `references/capacity-planning-resource-models.md` | CPU, memory, connection estimates |
| Scaling | `references/capacity-planning-scaling.md` | Instance counts and autoscaling |
| Budgets and cost | `references/capacity-planning-budgets-costs.md` | Performance budgets and sizing |
| Capacity alerts | `references/capacity-planning-alerts-reference.md` | Alert rules and heuristics |

See `references/README.md` for the index.
