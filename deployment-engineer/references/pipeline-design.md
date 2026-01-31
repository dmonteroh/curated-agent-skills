# Pipeline Design (Stages, Gates, Rollout/Rollback)

Use this when designing or refactoring a CI/CD pipeline so it is fast, safe, and operable.

## Outputs to produce

- Pipeline stages + triggers (push/PR/tag/manual)
- Environments + promotion rules (dev/stage/prod)
- Quality gates (tests, security scans, policy checks)
- Approval gates (who/when/what signal)
- Rollout strategy + rollback triggers + runbook

## Canonical stage model

1) Validate (cheap checks)
- lint/format
- typecheck
- config validation
- secret scanning / policy checks

2) Build
- compile/package
- container build
- SBOM/signing (if used)
- artifact caching

3) Test
- unit
- integration (DB/service containers as needed)
- smoke
- (optional) e2e on PR or nightly

4) Security
- dependency vuln scan
- SAST (and DAST only when it’s real signal)
- container image scan

5) Deploy
- staging deploy + smoke
- production deploy with gates

6) Verify
- health checks
- error/latency gates vs baseline
- canary analysis (if applicable)

## Approval gates (when and how)

Use approvals for:
- production deploys
- irreversible migrations/cutovers
- privilege changes (IAM/secrets)

Keep approvals objective:
- “approve if p95 latency < X and error rate < Y for Z minutes in staging”

## Rollout strategies (choose one)

- Rolling: default; simplest.
- Blue/Green: instant rollback, but more infra.
- Canary: safest when you have good observability; requires traffic control.
- Feature flags: deploy code without releasing behavior; fastest rollback.

## Rollback triggers (make them explicit)

- health check failing
- error budget burn spike
- sustained 5xx > threshold
- p99 latency regression > threshold

