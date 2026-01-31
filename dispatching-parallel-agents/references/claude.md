# Using This Skill In Claude Code (Example)

This is an optional reference for environments that support spawning parallel sub-agents.

## Pattern

1) Partition the work into independent domains.
2) Write one narrow prompt per domain.
3) Dispatch one sub-agent per domain.
4) Merge with an integration gate (check overlaps + run full verification).

## Example (Claude Code-style "Task" dispatch)

The exact API varies by host environment. The key is that each task is:

- scope-limited (files/modules)
- has explicit success criteria
- returns a summary + verification

```text
Task("Fix failing tests in packages/auth")
Task("Investigate deployment config drift in k8s manifests")
Task("Update docs for new CLI flags")
```

## Prompt Template (Copy)

```text
Task: <domain>

Scope:
- Allowed: <files/folders>
- Avoid: <files/folders>

Inputs:
- Failures/errors:
  - <copy/paste key errors or failing test names>

Constraints:
- <no refactors beyond scope>
- <keep public API stable>

Definition of done:
- <tests pass / command output matches>

Return:
- Root cause
- Exact changes made (files)
- How you verified
```
