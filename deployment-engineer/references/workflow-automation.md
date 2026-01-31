# Workflow Automation (CI as a Product)

Use this reference when the goal is to eliminate manual steps and make CI predictable, fast, and secure.

## Outputs to produce

- A short inventory of current build/test/release steps
- Proposed workflow layout (jobs, caches, artifacts)
- Explicit quality gates (what fails the build)
- Required secrets and least-privilege permissions

## Fast path checklist

- Split workflows by intent:
  - PR checks (fast, deterministic)
  - main branch (build + deploy)
  - scheduled (nightly e2e, dependency checks)
- Cache what is safe:
  - dependency caches
  - build caches
  - test tooling caches
- Make artifacts explicit:
  - build outputs
  - test reports
  - coverage
- Fail early:
  - config validation
  - lint/typecheck
  - unit tests

## Security gates (minimal, high signal)

- Pin third-party actions by commit SHA (or approved versions).
- Use least-privilege `GITHUB_TOKEN` permissions.
- Avoid printing secrets; redact logs.
- Add dependency vulnerability scanning at least on main/nightly.

## Determinism and ergonomics

- Prefer reproducible builds (lockfiles, pinned tool versions).
- Avoid “works on my machine” scripts; encode steps in CI.
- Emit a single, readable summary for failures (link to logs, artifacts).

