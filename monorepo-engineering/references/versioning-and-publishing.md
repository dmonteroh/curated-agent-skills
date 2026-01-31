# Versioning and Publishing

## Default: private monorepo

Most repos should keep packages private:
- reduces release overhead
- avoids accidental public APIs

Use:
- `"private": true` at root
- workspace protocol for internal deps (e.g., `workspace:*`)

## When to publish packages

Publish only when you truly have external consumers (other repos/orgs) and you’re willing to support the API.

## Versioning modes

- Single version for the whole repo (simplest; good when everything releases together)
- Independent versions per package (more complex; better for shared libraries consumed externally)

## Release hygiene

- Make releases reproducible (tagged commits, changelog, build provenance if you care).
- Keep build artifacts out of the repo unless intentionally tracked.

