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

**Derive the matrix from two tag axes, not one.** Tag every package twice, then write the matrix from the tags instead of drawing it by hand. A hand-drawn matrix records the graph as it happens to be, so every existing edge looks legal; tags state the rule the graph has to satisfy, so a violating edge is a failure rather than a row.

- **Layer** — what kind of thing the package is, drawn from a short list the repo defines once and then reuses. The names are per repo, not universal: `app` / `feature` / `ui` / `data-access` / `util` is one frontend workspace's cut and does not fit a backend or polyglot root, where `service` / `adapter` / `domain` / `util` may be the honest split. Fix the list once; adding a layer per package turns the axis back into a free-for-all.
- **Domain** — which product area or bounded context the package serves, plus exactly one `shared` value for packages that legitimately serve all of them.

Two rule families follow, and both are required, because each admits edges the other forbids:

- **Layer rule.** Each layer may depend only on layers at or below it in a stated order, and that order must be acyclic. The bottom layer — pure helpers carrying no domain knowledge — may depend only on itself. Writing out every layer's allowed targets is what makes the order explicit and checkable; an order that lives in reviewers' heads is not a constraint.
- **Domain rule.** Each domain may depend only on itself and on `shared`, and `shared` may depend only on `shared`. The asymmetry is deliberate: a shared package that reaches into a product domain inverts the dependency, and every consumer of that package then silently drags that domain in behind it. This is the rule most likely to be "relaxed just this once" by someone who cannot see what it buys, so record the reason beside it.

The axes catch different violations. Two packages can sit at legal layers and still form an illegal cross-domain edge — a `web` feature importing an `api` feature. Two packages in one domain can still form an illegal upward edge — a util importing a feature. Checking either axis alone passes both cases.

Enforce mechanically with whatever the repo already runs: a lint rule over import statements, a query over the build graph, a CI job that fails on a violating edge. The mechanism is open; what is not open is that the check runs unattended. A boundary enforced only by reviewers reading diffs is a convention, and conventions lose to deadlines. The `>2 teams` decision above is the symptom that a shared package needs splitting; the domain axis is what keeps the halves apart once it has been split.

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
- Boundaries: two tags per package — layer, ordered `app` > `feature` > `data-access` > `util`, and domain, one of `checkout`, `billing`, `shared`. Derived matrix: `packages/checkout-data-access` may import `data-access` and `util` packages tagged `checkout` or `shared`, and nothing else; `packages/shared-utils` may import `util` packages tagged `shared`. Enforced by an import lint rule run in CI, not by review.

## References (load as needed)

- `references/README.md`
