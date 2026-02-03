---
name: monorepo-engineering
description: Design and operate monorepos with clear boundaries, fast builds, and low-conflict collaboration. Covers workspace layout, dependency constraints, build caching, affected detection, versioning/publishing, and CI integration. Works standalone; choose tooling pragmatically (pnpm/yarn/npm, Nx/Turbo/Bazel).
category: architecture
---

# monorepo-engineering

Build monorepos that scale to multiple agents and teams without becoming a ball of mud.

## Use this skill when

- Setting up a monorepo or migrating from polyrepo.
- Making build/test/dev workflows faster (caching, affected detection).
- Defining boundaries for shared packages (dependency constraints, layering).
- Debugging monorepo pain: slow CI, dependency hell, inconsistent tooling, "why did this rebuild?"

## Do not use this skill when

- The repo is not a monorepo and there’s no plan to make it one.
- You only need a single-package refactor unrelated to workspace tooling.

## Outputs (what you should produce)

- Proposed repo layout (`apps/`, `packages/`, optional `tools/`)
- Boundary rules (what can depend on what; what is “shared”)
- Task graph + caching strategy (local + optional remote)
- Affected detection strategy (PR-only changes run minimal tasks)
- Versioning/publishing plan (private vs publishable packages)
- CI plan (what runs on PR vs main vs nightly)

## Workflow (fast, deterministic)

1) Inventory reality
- Package manager(s), languages, build tools, CI runner, current pain points.
- Identify the "hot paths" (slowest jobs; most frequent tasks).

2) Choose minimal tooling
- Prefer the smallest tool that solves the current problem.
- If your repo is already committed to Nx/Turbo/Bazel, don’t fight it—improve it.

3) Define the workspace shape
- Prefer:
  - `apps/` for deployables
  - `packages/` for libraries/shared code
  - `tools/` for scripts/CLIs (optional)

4) Define dependency constraints
- Prevent "everything imports everything".
- Keep shared libraries narrow and explicit.

5) Build speed: caching + affected detection
- Ensure build outputs are cached and stable.
- Only run tasks for affected projects on PRs.

6) CI integration
- PR: cheap checks + affected build/test
- main: full build/test + deploy gates (if applicable)
- nightly: heavy suites (full e2e, dependency checks)

## References (load as needed)

- `references/layout-and-boundaries.md`
- `references/caching-and-affected.md`
- `references/versioning-and-publishing.md`
- `references/tool-selection.md`

