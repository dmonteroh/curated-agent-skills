---
name: secrets-management
description: "Secure secrets handling for CI/CD and runtime: secret inventory, access boundaries, short-lived identity (OIDC/workload identity), rotation, auditing, and leak response. Works across Vault and cloud-native secret managers."
category: security
---
# Secrets Management

Provides guidance to prevent secret leakage and make access auditable and maintainable.

## Use this skill when

- Handling credentials, signing keys, API keys, TLS material, or connection strings
- Designing secret retrieval for CI/CD or runtime workloads
- Implementing rotation, auditing, and leak response

## Do not use this skill when

- You only need local dev values that will never be shared (use `.env` locally, never commit)
- You cannot secure access to any secrets backend

## Required inputs

- Target environments and workloads (CI/CD, runtime, or both)
- Current secret locations and owners (source control, env vars, secret managers)
- Access constraints (identity provider, IAM policies, compliance requirements)
- Rotation expectations and incident response requirements

## Constraints

- Never request or output real secret values; use placeholders when needed
- Avoid guidance that depends on external network access or time-sensitive data

## Workflow (Deterministic)

0) Confirm required inputs
- If any required input is missing, request it before proceeding.
- Output: list of missing inputs or a confirmation to proceed.

1) Inventory secrets
- List secret types, owners, environments, and rotation requirements.
- Identify where secrets are currently stored and where they can leak (logs, artifacts, env dumps).
- Output: inventory table with owner, location, and rotation target.

2) Choose access model (prefer short-lived)
- Prefer OIDC/workload identity over long-lived static credentials.
- Enforce least privilege and environment separation.
- If OIDC/workload identity is available, use short-lived tokens scoped to each workload.
- If only static credentials are possible, require scoped secrets, explicit expiration, and rapid rotation.
- Output: access model decision and required identity claims/scopes.

3) Choose backend (don’t overfit)
- Vault when you need centralized policy + dynamic secrets.
- Cloud secret managers when you want managed storage + IAM integration.
- If you need database credentials or just-in-time secrets, favor Vault.
- If you need simple storage with cloud IAM and KMS, favor cloud secret managers.
- Output: backend selection with rationale and constraints.

4) Integrate safely
- Fetch secrets at runtime or job runtime (not baked into images).
- Mask secrets in logs; avoid printing env.
- Add auditing and usage visibility.
- For CI/CD: use ephemeral tokens, short-lived runners, and masked variables.
- For runtime: use sidecars/agents or direct SDK calls with minimal scopes.
- Output: integration plan with retrieval flow, masking, and audit signals.

5) Rotation + incident response
- Rotation plan: cadence, automation, blast radius.
- Leak response: revoke/rotate, search logs/artifacts, postmortem follow-ups.
- If a leak is confirmed, revoke immediately, rotate dependent services, and document exposure window.
- Output: rotation runbook and leak-response checklist.

## Common mistakes to avoid

- Storing secrets in source control, container images, or build artifacts
- Reusing the same secret across environments or teams
- Printing secrets via verbose logging or debugging dumps
- Long-lived CI/CD tokens without rotation or scope limits
- No audit trail for reads, updates, or rotations

## Examples

**Example request**
"We need to move GitHub Actions secrets to OIDC and choose a backend."

**Example response (condensed)**
- Secret inventory: GitHub deploy key (prod), DB password (staging/prod)
- Access model: OIDC with repository + environment claims
- Backend: cloud secret manager (managed storage + IAM)
- Integration: job-level token exchange, masked outputs, audit logs enabled
- Rotation: policy-based cadence, automated rotation + alerting

## Reporting format

1. Secret inventory (what/where/owner/rotation)
2. Access model + backend decision (with rationale)
3. Integration plan (CI/CD and/or runtime) with least-privilege boundaries
4. Rotation + incident response plan
5. Verification steps (masking, access policy, rotation checks)

## Output Contract (Always)

- Secret inventory (what/where/owner/rotation)
- Recommended backend + access model with rationale
- Integration plan (CI/CD and/or runtime) with least-privilege boundaries
- Rotation + incident response plan
- Verification steps (how to prove masking, rotation, and access policies work)

## Resources (Optional)

- References index: `references/README.md`
- Implementation playbook (patterns + examples): `resources/implementation-playbook.md`
- Vault setup notes: `references/vault-setup.md`
- GitHub secrets hygiene: `references/github-secrets.md`
