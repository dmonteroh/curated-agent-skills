---
name: monorepo-engineering
description: "Design and operate monorepos with clear boundaries, fast builds, and low-conflict collaboration. Covers workspace layout, dependency constraints, build caching, affected detection, versioning/publishing, and CI integration. Works standalone; choose tooling pragmatically (pnpm/yarn/npm, Nx/Turbo/Bazel)."
metadata:
  category: architecture
---
# monorepo-engineering

Provides guidance to build monorepos that scale across teams without becoming a ball of mud.

## Use this skill when

- Setting up a monorepo or migrating from polyrepo.
- Making build/test/dev workflows faster (caching, affected detection).
- Defining boundaries for shared packages (dependency constraints, layering).
- Debugging monorepo pain: slow CI, dependency hell, inconsistent tooling, "why did this rebuild?"

## Do not use this skill when

- The repo is not a monorepo and there’s no plan to make it one.
- You only need a single-package refactor unrelated to workspace tooling.

## Required inputs

- Current repo structure (folders, package manager, build tools).
- CI environment and typical workflows (PR vs main vs nightly).
- Pain points (slow builds, flaky cache, dependency chaos).
- Publishing needs (private only vs public packages).

## Outputs

- Proposed repo layout (`apps/`, `packages/`, optional `tools/`).
- Boundary rules (allowed dependency directions, shared package criteria).
- Task graph + caching strategy (local + optional remote).
- Affected detection strategy (what runs on PRs, what runs on main).
- Versioning/publishing plan (private vs publishable packages).
- CI plan (PR vs main vs nightly).

## Workflow (fast, deterministic)

1) Inventory reality
- Capture package manager(s), languages, build tools, CI runner, and pain points.
- Identify the "hot paths" (slowest jobs; most frequent tasks).
- Output: inventory summary + top 3 bottlenecks.

2) Choose minimal tooling
- Prefer the smallest tool that solves the immediate pain.
- Decision: If the repo already uses Nx/Turbo/Bazel, extend it instead of swapping.
- Decision: If the repo is small and pain is limited to workspace wiring, recommend package-manager workspaces only.
- Output: tooling recommendation + rationale.

3) Define the workspace shape
- Prefer:
  - `apps/` for deployables
  - `packages/` for libraries/shared code
  - `tools/` for scripts/CLIs (optional)
- Decision: If non-JS language mono-root exists, allow `services/` or `libs/` to match conventions.
- Output: proposed folder layout + migration notes.

4) Define dependency constraints
- Prevent "everything imports everything" with explicit layering rules.
- Keep shared libraries narrow and explicit.
- Decision: If shared utilities grow >2 teams, split into domain-specific packages.
- Output: dependency matrix + enforcement approach.

5) Build speed: caching + affected detection
- Ensure build outputs are cached and stable.
- Only run tasks for affected projects on PRs.
- Decision: If CI times are >15–20 minutes, recommend remote caching.
- Output: caching/affected strategy + required config changes.

6) CI integration
- PR: cheap checks + affected build/test
- main: full build/test + deploy gates (if applicable)
- nightly: heavy suites (full e2e, dependency checks)
- Output: CI job matrix + trigger rules.

## Common pitfalls to avoid

- Mixing multiple package managers in the same workspace.
- Defining "shared" packages so broadly that every app depends on them.
- Cache keys that include timestamps or non-deterministic inputs.
- CI running full builds on every PR when affected detection exists.

## Output contract (report format)

Report in this format:

- Summary: 2–3 sentences on the recommended direction.
- Layout: bullet list of top-level folders and rules.
- Boundaries: dependency rules and enforcement mechanisms.
- Build/Caching: affected strategy + cache approach.
- Versioning: publishability + versioning model.
- CI Plan: PR vs main vs nightly matrix.
- Open Questions: missing inputs blocking decisions.

## Examples

**Example input**
"We have a Node + Go monorepo with slow PR builds and unclear package boundaries. We use GitHub Actions and pnpm. Should we add Nx or Turbo?"

**Example output (excerpt)**
- Summary: Keep pnpm workspaces, add Turbo for caching and affected pipelines.
- Layout: `apps/` for deployables, `packages/` for shared libs, `tools/` for CI scripts.
- Boundaries: enforce with lint rules and explicit dependency graph.

## References (load as needed)

- `references/README.md`
