# Config Validation (Schema, Secrets, Env Drift)

Use this when configuration is a reliability risk (multi-env deployments, installers, many toggles, lots of secrets).

Goal: fail fast on misconfiguration *before* deploy.

## Outputs to produce

- Config inventory (files + env vars + runtime config sources)
- A schema (or typed struct) for config with validation rules
- Env-diff rules (what must be identical vs allowed to differ)
- CI gate that runs validation on every PR

## What to validate (minimum)

- Required keys present
- Types and formats (URLs, ports, durations)
- Bounds (timeouts, pool sizes, pagination limits)
- Cross-field constraints (if A enabled then B required)
- Production safety:
  - debug disabled
  - wildcard CORS not allowed (unless explicitly approved)
  - secure cookies/HSTS where applicable

## Secret hygiene

- Prevent committing real secrets (pre-commit + CI scanning).
- Prefer “secret references” in config (env var names, vault paths) instead of secret values.
- Ensure logs never print full config or secrets.

## Environment drift rules

Write down:
- what *must* be consistent across envs (schema, required vars, feature flags defaults)
- what is allowed to differ (URLs, credentials, scaling knobs)

## CI gate pattern

- Add a job early in the pipeline:
  - `validate-config` runs schema/type validation and fails the build with clear errors.
- Optionally validate multiple env profiles (dev/stage/prod) using example configs with placeholders.

