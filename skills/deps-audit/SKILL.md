---
name: deps-audit
description: Produces a local, best-effort dependency audit summary and remediation plan for repos with dependency manifests.
category: security
---

# deps-audit

Provides a fast, low-noise dependency audit that relies on locally available tooling and produces an actionable remediation plan.

## Use this skill when

- A repo includes dependency manifests or lockfiles that need a security or license review.
- A release needs a quick dependency risk assessment with actionable next steps.
- A supply-chain or SBOM check is required using local tooling.

## Do not use this skill when

- No dependency manifests or lockfiles are available.
- Only high-level strategy discussion is needed without producing an audit report.
- The environment cannot write output files under the repo.

## Trigger phrases

- "audit dependencies"
- "dependency vulnerability scan"
- "license risk check"
- "supply-chain audit"

## Required inputs

- Target repo path (default: current working directory).
- Any policy constraints (severity threshold, license allow/deny list).
- Output location preference (default: `docs/_docgen/deps-audit/`).

## Constraints

- Uses local tooling only; no network access assumptions.
- Does not install or modify dependencies.
- Writes outputs only under the specified repo path.

## Workflow

1) Scope and detect manifests
- Identify dependency manifests and lockfiles by ecosystem.
- Output: list of detected ecosystems and evidence paths.

2) Collect local scan evidence
- Run best-effort local tools per ecosystem; do not install tools.
- If a tool is missing, record the recommended command and continue.
- Output: raw tool outputs under `docs/_docgen/deps-audit/raw/`.

3) Analyze findings
- Summarize vulnerabilities by severity, reachability, and exposure.
- Summarize license and SBOM signals when available.
- Output: prioritized findings table with affected packages and suggested fixes.

4) Produce remediation plan
- Propose minimal, compatible upgrades or mitigations.
- Flag items needing architectural decisions.
- Output: ordered remediation actions with effort notes.

## Decision points

- If no manifests are detected, stop and report "no dependency evidence found".
- If scan tooling is missing, document the missing tool and skip that scan.
- If license policy is provided, classify conflicts; otherwise list notable licenses only.
- If only transitive vulnerabilities exist with no direct fix, recommend pinning or replacement options.

## Common pitfalls

- Ignoring lockfiles and using manifests only (reduces accuracy).
- Treating dev-only dependencies as production impact without justification.
- Performing broad major upgrades without assessing compatibility.
- Assuming network access or installing tools without approval.

## Output contract

Report a concise summary with the following sections:

- Format: markdown with headings and bullet lists.
- Detected ecosystems + evidence files.
- Tools executed and missing tools (with suggested commands).
- Top vulnerabilities (severity, package, version, reachability, fix).
- License or SBOM findings and conflicts (if tooling available).
- Remediation plan (ordered actions + notes).
- Limitations or gaps (missing tools, missing manifests).

## Scripts

`scripts/deps.sh` provides `scan` and `report` commands.

- Usage:
  - `./skills/deps-audit/scripts/deps.sh scan`
  - `./skills/deps-audit/scripts/deps.sh report`
  - Optional: set `DEPS_REPO_ROOT=/path/to/repo` to target another repo.
- Required tools (best-effort only): `npm`, `pnpm`, `yarn`, `pip-audit`, `govulncheck`, `cargo-audit`.
- Verification:
  - Confirm docs/_docgen/deps-audit/REPORT.md exists.
  - Confirm raw outputs exist under `docs/_docgen/deps-audit/raw/`.

## Examples

Trigger test prompts:

- "Run a dependency audit and summarize the top risks."
- "Check this repo for vulnerable dependencies and license issues."

Example output snippet:

- Detected ecosystems: node, python
- Missing tools: `pip-audit` (suggested: `pip-audit -f json`)
- Top vulnerabilities: `package-x@1.2.3` (high, reachable)
- Remediation: upgrade `package-x` to `1.2.9`

## References

- `references/README.md`
