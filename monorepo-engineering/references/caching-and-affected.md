# Caching and Affected Detection (Speed)

Goal: make the common path (PR) fast.

## Caching checklist

- Ensure each task declares stable outputs (so caching works).
- Avoid caching "dev" or persistent tasks.
- Do not cache secrets or environment-specific outputs unintentionally.

Common outputs:
- `dist/`
- `.next/` (excluding `.next/cache` where appropriate)
- `coverage/` (optional)

## Affected detection

Affected detection means: only run tasks for projects touched by a change, plus their dependents/dependencies (depending on task direction).

Typical PR policy:
- lint/typecheck affected
- unit tests affected
- build affected

Typical main/nightly policy:
- broader suite, e.g. full integration/e2e

## Remote caching

Use remote caching when:
- CI is slow due to repeated builds
- teams are large or PR throughput is high

Avoid remote caching if:
- builds are not deterministic yet
- secrets accidentally leak into artifacts

