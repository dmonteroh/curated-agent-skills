# Scanning and evidence collection

Use this reference to run best-effort local scans and capture evidence.

## Principles

- Use only locally available tools; do not install new tooling.
- Capture raw outputs under `docs/_docgen/deps-audit/raw/`.
- Record missing tools with suggested commands.

## Local scan commands (best-effort)

- Node
  - `npm audit --json`
  - `pnpm audit --json`
  - `yarn audit --json` (classic) or `yarn npm audit --all --json` (berry)
- Python
  - `pip-audit -f json`
- Go
  - `govulncheck ./...`
- Rust
  - `cargo audit --json`

## Evidence capture

- Save stdout to a named file (for example, `npm-audit.json`).
- Save stderr to a sibling `*.stderr` file for troubleshooting.
- Do not modify dependencies during scans.

## Decision points

- If a tool is missing, skip the scan and document the suggested command.
- If multiple tools are available, prefer lockfile-aware scans.

## Pitfalls to avoid

- Treating scan errors as zero findings.
- Overwriting previous evidence without noting timestamps or context.
