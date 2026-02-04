# Documentation Automation Playbook

## Goals

- Keep docs discoverable and consistent.
- Detect stale or missing docs early.
- Reduce manual maintenance.

## Automation checklist

- Maintain the managed docs index block in `docs/README.md`.
- Run link checks if tooling exists in the repo.
- Add a "docs freshness" checklist to release or PR templates.
- Scan for secrets before publishing docs.

## Managed index block

```md
<!-- DOC-INDEX:START -->
| Doc | Purpose |
| --- | --- |
<!-- DOC-INDEX:END -->
```

## Manual fallback

If CI tooling is unavailable, document the manual run steps and expected outputs in the doc plan.
