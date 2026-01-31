---
name: secrets-management
description: Secure secrets handling for CI/CD and runtime: secret inventory, access boundaries, short-lived identity (OIDC/workload identity), rotation, auditing, and leak response. Works across Vault and cloud-native secret managers.
---

# Secrets Management

This skill is about preventing secret leakage and making secret access auditable and maintainable.

## Use this skill when

- Handling credentials, signing keys, API keys, TLS material, or connection strings
- Designing secret retrieval for CI/CD or runtime workloads
- Implementing rotation, auditing, and leak response

## Do not use this skill when

- You only need local dev values that will never be shared (use `.env` locally, never commit)
- You cannot secure access to any secrets backend

## Workflow (Deterministic)

1) Inventory secrets
- List secret types, owners, environments, and rotation requirements.
- Identify where secrets are currently stored and where they can leak (logs, artifacts, env dumps).

2) Choose access model (prefer short-lived)
- Prefer OIDC/workload identity over long-lived static credentials.
- Enforce least privilege and environment separation.

3) Choose backend (don’t overfit)
- Vault when you need centralized policy + dynamic secrets.
- Cloud secret managers when you want managed storage + IAM integration.

4) Integrate safely
- Fetch secrets at runtime or job runtime (not baked into images).
- Mask secrets in logs; avoid printing env.
- Add auditing and usage visibility.

5) Rotation + incident response
- Rotation plan: cadence, automation, blast radius.
- Leak response: revoke/rotate, search logs/artifacts, postmortem follow-ups.

## Output Contract (Always)

- Secret inventory (what/where/owner/rotation)
- Recommended backend + access model with rationale
- Integration plan (CI/CD and/or runtime) with least-privilege boundaries
- Verification steps (how to prove masking, rotation, and access policies work)

## Resources (Optional)

- Implementation playbook (patterns + examples): `resources/implementation-playbook.md`
- Vault setup notes: `references/vault-setup.md`
- GitHub secrets hygiene: `references/github-secrets.md`

