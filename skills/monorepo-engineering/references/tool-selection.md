# Tool Selection (Pragmatic)

Choose the minimal tool that solves the repo's actual pain.

## Package manager / workspaces

- Prefer pnpm workspaces when teams want:
  - fast installs
  - strict dependency graph
  - good monorepo ergonomics

Yarn/npm workspaces can also work; choose what the repo already uses unless there's a strong reason to migrate.

## Task runner / build graph

- Turborepo: great default for JS/TS monorepos focusing on task caching and pipeline speed.
- Nx: broader feature set (generators, graph constraints, plugins), but more surface area.
- Bazel: strongest for polyglot + hermetic builds, but highest complexity.

## Decision heuristic

1) If the repo already uses Nx/Turbo/Bazel: improve the existing system first.
2) If the repo is JS/TS only and speed is the main driver: Turbo is often the simplest.
3) If the repo is polyglot and correctness/hermetic builds matter: consider Bazel.
