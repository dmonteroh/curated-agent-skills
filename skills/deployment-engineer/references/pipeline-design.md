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

## Artifact promotion invariant

Build once; promote that same artifact through every environment.

Rebuilding per environment means staging validated bytes that never reach production: the tested artifact and the shipped artifact are different objects, and every difference between them is untested — a moved dependency version, a different base image layer, a build-time flag that only production sets. Environment differences belong in configuration injected at deploy time, not in a rebuild.

Concretely: the Build stage emits one immutable, addressable artifact (a digest, not a mutable tag), later stages reference it by that identity, and no deploy stage runs a build step. If a stage cannot deploy without rebuilding, that is the finding — fix the pipeline rather than accepting a second build.

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

## Schema changes and rollback

A rollback plan that only covers traffic and artifacts is incomplete. Reverting the service to its previous version while a migration stays applied leaves old code running against a new schema — the deploy is reported as rolled back and the service still errors. Plan the data side before the rollout, not during the incident.

### Expand / migrate / contract

Stage every schema change so that at no point does a deployed code version disagree with the schema it is running against:

| Release | Schema action | Code action | Why it is safe to stop here |
| --- | --- | --- | --- |
| Expand | Add the new structure, nullable/defaulted, alongside the old | Unchanged, or writes both | Old code never sees the new structure; rolling back changes nothing |
| Migrate | None | Backfill, then read and write the new structure | Both structures are present and populated; rolling back to the expand-era code still works |
| Contract | Remove the old structure | Unchanged | No deployed version references the old structure any more |

The three-step shape is what makes each release independently reversible; the release *count* is a consequence of the sequence, not a tuned constant. A change may need more steps (a large backfill run as its own release, a dual-write period held longer than one cadence) and must never need fewer.

Rules that follow from the sequence:

- **No destructive change until the old code is gone from every environment** — dropping a column, adding a NOT NULL constraint, narrowing a type, renaming in place. "Every environment" includes the long-lived staging deploy nobody upgraded and any pinned client, not just production.
- **A rename is an expand/contract, never an in-place edit.** Add the new column, dual-write, backfill, cut reads over, then drop the old one.
- **The undo script ships with its forward migration**, written and reviewed at the same time, versioned in the same commit. An undo written during an incident is untested code run under maximum pressure.
- **Verify reversibility, do not assert it.** Apply the forward migration to a copy of production-shaped data, run the *previous* release's code against the migrated schema, then apply the undo and run the previous release again. The check fails visibly if any of the three steps errors; "the migration is backward compatible" without that run is a claim, not a check.

### Rollback plan checklist

A rollback plan is complete when it answers all of these:

- Which artifact version traffic returns to, and how it is selected (digest, revision number, previous slot).
- What happens to schema state at that point: nothing to undo (the expand/contract sequence made the migration safe to leave applied) or a named undo script to run, in a stated order relative to the traffic switch.
- Whether in-flight data written by the new code is readable by the old code, and what happens to it if not.
- Who runs it, what signal triggers it, and what the verification is that it worked — the same readiness check the deploy gate used, not an eyeball on a dashboard.

