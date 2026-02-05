# Versioning and Publishing

## Default: private monorepo

Most repos should keep packages private:
- reduces release overhead
- avoids accidental public APIs

Use:
- `"private": true` at root
- workspace protocol for internal deps (e.g., `workspace:*`)

## When to publish packages

Publish only when there are external consumers (other repos/orgs) and the team is willing to support the API.

## Versioning modes

- Single version for the whole repo (simplest; good when everything releases together)
- Independent versions per package (more complex; better for shared libraries consumed externally)

## Release hygiene

- Make releases reproducible (tagged commits, changelog, build provenance when required).
- Keep build artifacts out of the repo unless intentionally tracked.
