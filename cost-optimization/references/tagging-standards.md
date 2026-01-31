# Tagging Standards (Cloud Cost Allocation)

This is a cloud-agnostic tagging/labeling standard meant to support cost allocation, governance, and incident response.

## Goals

- Attribute spend to an accountable owner.
- Split shared costs by environment and service.
- Enable budgets/alerts by tag.
- Make cleanup possible (find orphaned resources).

## Required Tags

Use these keys (or your platform's equivalent label system) consistently.

- `owner` - primary accountable team or individual (e.g., `team-platform`, `team-auth`).
- `service` - workload/service name (e.g., `api`, `worker`, `identity-verifier`).
- `env` - `dev` | `staging` | `prod` (or your established environments).
- `cost_center` - finance mapping (string or numeric code).
- `managed_by` - `iac` | `console` | `script` (prefer `iac`).
- `data_classification` - `public` | `internal` | `confidential` | `restricted`.

## Optional (Recommended) Tags

- `project` - product or program grouping.
- `tenant` - when multi-tenant and cost attribution matters.
- `lifecycle` - `ephemeral` | `long-lived`.
- `expires_on` - ISO date for temporary resources (e.g., `2026-02-15`).
- `repo` - source repository identifier.
- `runbook` - link key or short ID for operational docs.

## Formatting Rules

- Lowercase keys.
- Values: lowercase, `kebab-case` preferred.
- Keep values stable; avoid free-form descriptions.

## Enforcement Patterns

- CI/IaC: fail plans when required tags are missing.
- Cloud policies (where supported): deny creation without required tags.
- Drift detection: alert when resources exist without required tags.

## Anti-Patterns

- Using `owner` values like `unknown` or `tbd`.
- Encoding secrets in tags.
- Overloading tags with long descriptions.
