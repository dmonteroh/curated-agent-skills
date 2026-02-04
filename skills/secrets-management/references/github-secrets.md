# GitHub Secrets Best Practices

Use GitHub Secrets for CI/CD needs. Treat them as a delivery mechanism, not your only long-term secrets system.

## Prefer OIDC Over Long-Lived Cloud Keys

- Use GitHub Actions OIDC + cloud provider federation where possible.
- Avoid storing cloud access keys as GitHub secrets.

## Secret Scoping

- Prefer Environment secrets for production deployments.
- Use required reviewers for production environments.
- Use minimal permissions per workflow.

## Masking & Logging

- Always add masks for any value written to logs.
- Do not echo secrets.
- Avoid passing secrets via command-line args (they can show up in process lists).

## Rotation

- Record owner and rotation expectations for each secret.
- When rotating, update the secret and redeploy affected workflows.

## Governance

- Keep a secret inventory outside GitHub (at least: name, owner, usage, rotation cadence).
- Restrict who can create/update secrets.
- Use branch protections to limit the ability to exfiltrate secrets via workflow changes.

## Common Pitfalls

- Secrets printed via debug output.
- Secrets embedded in generated artifacts.
- Overly permissive workflow permissions (`contents: write`, `id-token: write` everywhere).
