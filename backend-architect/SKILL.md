---
name: backend-architect
description: "Expert backend architect for designing operable services and APIs: service boundaries, contracts, reliability, integration patterns, and rollout safety. Produces crisp architecture decisions and verification steps. Use PROACTIVELY when creating or changing backend services/APIs."
metadata:
  model: inherit
---

# Backend Architect

This skill is about backend design quality and operability, not framework-specific implementation.

## Use this skill when

- Designing a new service/API or changing service boundaries
- Defining contracts (request/response, events, schemas) and compatibility rules
- Planning reliability/observability/rollout (SLIs/SLOs, dashboards, runbooks)
- Choosing integration mechanisms (sync vs async, queues, webhooks) with failure modes

## Do not use this skill when

- You only need a local code fix with no architectural impact
- You need deep database design (use database-architect / postgresql-engineering)
- You need stack-specific implementation guidance (use language/framework skills)

## Workflow (Deterministic)

1) Capture constraints
- Domain: primary use-cases, actors, data ownership.
- NFRs: latency, throughput, availability, consistency, privacy/compliance.
- “Done” means: what must be observable and supportable in production.

2) Define boundaries
- What is inside the service vs outside.
- Owned data vs referenced data.
- Public API surface: what is stable and versioned.

3) Design contracts
- Error shape and status semantics.
- Pagination, filtering, sorting, idempotency (if applicable).
- Backwards compatibility rules (deprecations, migrations, rollout ordering).

4) Plan failure modes + operability
- Timeouts, retries, backoff, circuit breaking where appropriate.
- Telemetry hygiene: logs/metrics/traces with correlation IDs.
- Runbooks and alerting targets (what pages a human, what is noisy).

5) Rollout plan
- Migration steps (if any), canary/feature flags, rollback strategy.
- Verification steps (what to check in staging and prod).

## Output Contract (Always)

- Architecture sketch (boundaries + contracts) with 2-3 alternatives and tradeoffs
- The chosen approach + rationale
- Risks and mitigations
- Verification plan (tests + observability + rollout gates)

## References (Optional)

- Pattern selection + boundary rules: `references/architecture-patterns.md`
- Operability-first checklist (SLIs/SLOs, golden signals, telemetry): `references/operability-sre.md`
- API contract hygiene (error shape, pagination, versioning): `references/api-contract-hygiene.md`
- Backend security coding checklist: `references/backend-security-coding.md`

