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

Three answers that are not a root cause, and send the investigation back
instead of filling this in: human error (the open question is what let the
error reach production), a cause whose only available corrective action is
retraining or asking for more care, and the problem statement reworded.

## Resolution

Describe the mitigation or fix and how it was verified.

## Detection

**What went well:**
- [bullet]

**What could be improved:**
- [bullet]

## Action Items

| Action | Owner | Priority | Due Date | Monitoring window | Effectiveness evidence |
|--------|-------|----------|----------|-------------------|------------------------|
| [Action item] | [Owner] | P0/P1/P2 | [YYYY-MM-DD] | [window, declared now] | [filled at closure] |

The due date is when the action is implemented. The item closes only when the
last two columns are filled: evidence gathered across the declared window
showing the failure mode did not return.

## Lessons Learned

**What went well:**
- [bullet]

**What didn't go well:**
- [bullet]

**Where we got lucky:**
- [bullet]
```

## Closing an action item

An action item closes on evidence that the failure mode stopped, not on the arrival of its due date. Two distinct checks, and skipping the second is how an action-item tracker fills with closed items while the incident rate does not move:

- **Verification — was the action implemented as planned?** The change is in place: the alert exists, the timeout is set, the runbook step is written, the retry is bounded. This is what a due date can attest to, and it is where items are usually closed.
- **Validation — did the action actually prevent recurrence?** Evidence gathered after implementation, across a declared monitoring window, that the failure mode did not return. Attach it to the item; an item closed without it has recorded an intention, not an outcome.

Declare the monitoring window when the item is written, not when someone wants to close it *(authored: without that ordering the window is chosen by whoever wants the item closed, at the moment they want it closed)*, and set its length from the system's own cadence — long enough to contain the conditions that produced the incident, such as a full release cycle, a peak-traffic period, or a complete on-call rotation. A fix for a failure that only appears under end-of-month batch load is not validated by a quiet week. A window length carried over from another team or another system is a chosen default rather than a measured one; say which it is when stating it.

**A recurrence inside the monitoring window reopens the original item.** It does not open a new one. The recurrence is the evidence that the corrective action was ineffective, and the re-investigation starts from the assumption that the original analysis was incomplete — most often that it named a symptom instead of what the system permitted. Filing a fresh incident for a failure mode that already has an action item splits one unsolved problem into a series of separately closed tickets, and the tracker then shows steady progress against a failure that keeps happening.
