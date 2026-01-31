# Vault Setup (Practical Guide)

This is a pragmatic, non-exhaustive guide for setting up Vault for CI/CD and runtime secrets retrieval.

## Core Concepts

- Auth method: how a caller proves identity (OIDC, Kubernetes, AppRole, etc.).
- Policy: what that identity is allowed to read/write.
- Secret engine: KV, database, PKI, transit, etc.

## Recommended Defaults

- Run Vault in HA mode (not dev mode) for any shared environment.
- Enable audit devices (file or syslog).
- Prefer TLS everywhere.
- Prefer identity-based auth (OIDC/Kubernetes) over static tokens.

## Secret Engines

- `kv-v2`: general secrets with versioning.
- `database`: dynamic DB credentials (high leverage).
- `pki`: issue short-lived certs.
- `transit`: encryption/signing as a service.

## Auth Methods (When To Use)

- OIDC: humans + some CI/CD systems (good for SSO alignment).
- Kubernetes auth: workloads running in Kubernetes.
- AppRole: machine-to-machine when nothing better exists (treat as sensitive).

## Policy Design

- Write policies per service and environment.
- Deny by default; allow only required paths.
- Separate read vs write; separate rotation roles.

## CI/CD Integration Patterns

### Pattern A: CI uses OIDC -> Vault

- CI job exchanges OIDC token for a Vault token.
- Vault token has short TTL.

### Pattern B: CI uses wrapped token (fallback)

- Use response-wrapping and very short-lived wrapped tokens.
- Avoid long-lived root/management tokens in CI.

## Operational Checklist

- Backup/restore procedure tested.
- Unseal key management defined (auto-unseal preferred in cloud environments).
- Break-glass process defined.
- Monitoring for:
  - seal/unseal events
  - auth failures spikes
  - audit log delivery failures

## Migration Notes

If moving from GitHub/GitLab secrets to Vault:

- Start with one service.
- Keep both sources temporarily.
- Migrate secrets one-by-one and rotate during cutover.
