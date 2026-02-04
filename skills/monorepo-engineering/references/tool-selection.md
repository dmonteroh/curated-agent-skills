# Tool Selection (Pragmatic)

Choose the minimal tool that solves your actual pain.

## Package manager / workspaces

- Prefer pnpm workspaces when you want:
  - fast installs
  - strict dependency graph
  - good monorepo ergonomics

Yarn/npm workspaces can also work; choose what the repo already uses unless there's a strong reason to migrate.

## Task runner / build graph

- Turborepo: great default for JS/TS monorepos focusing on task caching and pipeline speed.
- Nx: broader feature set (generators, graph constraints, plugins), but more surface area.
- Bazel: strongest for polyglot + hermetic builds, but highest complexity.

## Decision heuristic

1) If you are already on Nx/Turbo/Bazel: improve the existing system first.
2) If you are JS/TS only and want speed: Turbo is often the simplest.
3) If you are polyglot and correctness/hermetic builds matter: consider Bazel.

