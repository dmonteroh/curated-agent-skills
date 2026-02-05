# Layout and Boundaries (Prevent Monorepo Entropy)

## Recommended layout

```text
.
├── apps/               # deployables (services, UIs)
├── packages/           # shared libraries (types, utils, ui, clients)
├── tools/              # repo tooling (optional)
├── docs/               # docs (optional)
└── <workspace config>  # pnpm-workspace.yaml / package.json workspaces / etc.
```

## Boundary rules (high signal)

- Apps can depend on shared packages.
- Shared packages should not depend on apps.
- “Shared” does not mean “global dumping ground”.

Patterns that work well:
- `@repo/shared-types`: contracts and DTOs only
- `@repo/shared-config`: lint/tsconfig/eslint presets
- `@repo/shared-utils`: small, stable helpers

Avoid:
- importing across sibling apps
- circular dependencies between packages
- “kitchen sink” shared packages with unrelated concerns

## Versioning approach (at the boundary level)

- Keep most packages private unless publishing is required.
- Use workspace protocol (e.g., `workspace:*`) for internal deps.
- Keep dependency updates centralized and automated where possible.
