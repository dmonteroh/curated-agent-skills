# License and SBOM checks

Use this reference when license or SBOM evidence is required.

## License review (best-effort)

- Prefer lockfiles and package metadata already present in the repo.
- If local tooling exists, run it and capture outputs:
  - `cargo license` (Rust)
  - `go-licenses report ./...` (Go)
  - `pip-licenses --format=json` (Python)
- If no tooling is available, list detected license fields from manifests only.

## SBOM generation (optional, local only)

- Use local tools if already installed, such as `syft` or `cyclonedx-*`.
- Output: SBOM file under `docs/_docgen/deps-audit/raw/` with format noted.

## Decision points

- If policy constraints are provided, classify conflicts vs allowed licenses.
- If no license evidence is available, document the gap explicitly.

## Pitfalls to avoid

- Assuming license data is complete without lockfile verification.
- Downloading new tooling or contacting external services.
