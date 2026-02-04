# Blameless Postmortem Template

```markdown
# Postmortem: [Incident Title]

**Date:** [YYYY-MM-DD]

## Summary

One-paragraph summary of what happened, impact, and resolution.

## Impact

- **Duration:** [total duration]
- **Users affected:** [estimate]
- **Revenue impact:** [estimate]
- **SLO impact:** [error budget consumed]

## Timeline (relative)

| Time  | Event |
|-------|-------|
| T+0m  | Issue begins |
| T+5m  | Alert fires |
| T+6m  | On-call acknowledges |
| T+10m | Incident declared |
| T+20m | Root cause identified |
| T+25m | Fix or rollback initiated |
| T+30m | Service recovers |
| T+40m | Incident resolved |

## Root Cause

Explain the technical root cause and contributing factors.

## Resolution

Describe the mitigation or fix and how it was verified.

## Detection

**What went well:**
- [bullet]

**What could be improved:**
- [bullet]

## Action Items

| Action | Owner | Priority | Due Date |
|--------|-------|----------|----------|
| [Action item] | [Owner] | P0/P1/P2 | [YYYY-MM-DD] |

## Lessons Learned

**What went well:**
- [bullet]

**What didn't go well:**
- [bullet]

**Where we got lucky:**
- [bullet]
```
