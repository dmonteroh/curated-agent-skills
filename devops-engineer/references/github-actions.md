# GitHub Actions (Runtime Integration Notes)

This file is intentionally **not** a full CI/CD pipeline design guide.

Use it when DevOps work requires GitHub Actions as a *runtime integration surface* (building/publishing images, running smoke checks, triggering deploy tooling), but keep pipeline architecture/rollout strategy in `deployment-engineer`.

## Safe Defaults

- Treat `stdout` logs as public; never print secrets.
- Prefer OIDC federation for cloud access over long-lived cloud keys.
- Use least privilege permissions in workflows.
- Pin actions to major versions at minimum; pin to SHAs when security posture requires.

## Build/Publish (Container Image)

Minimal pattern for building and pushing an image to GHCR.

```yaml
permissions:
  contents: read
  packages: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v5
        with:
          context: .
          push: true
          tags: ghcr.io/${{ github.repository }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

## Secrets Handling

- Prefer identity-based auth (OIDC) to avoid storing cloud keys in GitHub Secrets.
- If you must use GitHub Secrets:
  - mask values (`::add-mask::`)
  - avoid passing secrets via CLI args
  - scope to environments for production deploys

## Environment Safety

- Use GitHub Environments for production:
  - required reviewers
  - environment-scoped secrets

## Artifact Conventions

- Name artifacts deterministically (`<app>-<sha>-<platform>`).
- Keep build output separate from deploy steps (deploy consumes an artifact).

## When You Actually Need Pipeline Design

If the question is about:

- stage layout (build/test/deploy), approvals
- progressive delivery / rollback policy
- release promotion (dev -> staging -> prod)
- config validation gates

…use `deployment-engineer`.
