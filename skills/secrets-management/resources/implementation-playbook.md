# Secrets Management - Implementation Playbook

Use this playbook when you need a concrete secrets architecture, rollout plan, or incident-safe operating model.

## Default Deliverables

- Secret inventory: what secrets exist, who owns them, where they are used.
- Access model: humans vs workloads, and how each authenticates.
- Storage backend choice + rationale.
- Rotation plan: frequency, automation, and rollback.
- Leakage response: revoke/rotate steps + audit trail.

## Discovery (Ask First)

- Where are secrets used?
  - CI/CD (build/deploy), runtime (app), local dev, third-party integrations.
- What secret types?
  - API keys, DB creds, OAuth client secrets, signing keys, TLS certs.
- Rotation requirements?
  - Compliance-driven, risk-driven, or operational convenience.
- Deployment environment?
  - Kubernetes, VMs, serverless, PaaS.
- Identity options?
  - OIDC federation, workload identity, mTLS, Kubernetes auth.

## Architecture Decisions

### 1) Backend Selection

Prefer dedicated secrets backends for anything beyond trivial use.

- HashiCorp Vault: best when you need dynamic secrets, advanced auth methods, or multi-platform support.
- Cloud-native secrets managers: best when you are primarily in one cloud and want tight integrations.
- CI-only secret stores (e.g., GitHub/GitLab secrets): acceptable for small scopes but becomes hard to govern at scale.

### 2) Access Model

- Humans: SSO + MFA + break-glass procedure.
- Workloads: short-lived identity (OIDC / workload identity / Kubernetes auth). Avoid long-lived static keys.

### 3) Secret Delivery Pattern

Pick one dominant pattern; avoid mixing unless necessary.

- Inject at runtime (preferred): app fetches from backend via identity.
- Inject at deploy-time: deploy pipeline fetches and writes into platform secret store.
- Inject at build-time: avoid unless absolutely required (creates artifact contamination risk).

## Rotation Patterns

- Dual-secret / overlap rotation: publish new secret, deploy readers, then revoke old.
- Versioned secrets: rotate by version, keep N versions temporarily.
- Dynamic secrets (Vault): generate per-lease credentials; revoke automatically.

## Verification Checklist

- Secrets never appear in:
  - source control, build artifacts, container images, logs
- Pipelines mask secrets and use least privilege.
- Rotation is tested in a non-prod environment.
- Access is auditable.
- A leak response runbook exists.

## Incident Runbook (Leak Suspected)

- Contain: stop emitting logs/outputs that may leak.
- Identify: what secret, where it was exposed, blast radius.
- Revoke/rotate: prefer immediate revocation if safe.
- Audit: review access logs to confirm misuse.
- Prevent: add guardrails (scanner, policy, masking, permissions).
