# Packet Templates

## Task Board Template

```text
T1:
- Outcome:
- Allowed:
- Forbidden:
- Claim set (may modify):
- Inputs/evidence:
- Acceptance criteria:
- Verification (controller-run after barrier):
- Status:

T2:
- Outcome:
- Allowed:
- Forbidden:
- Claim set (may modify):
- Inputs/evidence:
- Acceptance criteria:
- Verification (controller-run after barrier):
- Status:
```

## Worker Packet Template

```text
Task: <one sentence target outcome>

Read-first:
- <paths>

Scope:
- Allowed: <paths>
- Forbidden: <paths>

Claim set (MUST NOT VIOLATE):
- You may only modify: <paths>

Constraints:
- If blocked/ambiguous: STOP and output QUESTIONS.
- Do not expand scope.
- Do not refactor unrelated code.
- Preserve public APIs unless instructed otherwise.
- Do not run verification commands; recommend them only.

Inputs/evidence:
- <errors/tests/logs/repro>

Acceptance criteria:
- [ ] <criterion>
- [ ] <criterion>

Deliverable:
- Root cause
- Files changed (exact list)
- Patch summary
- Recommended verification commands
- Risks/follow-ups
- QUESTIONS if blocked
```

## Reviewer Packet Template (Read-Only)

```text
Review type: <spec-compliance | code-quality>

Scope:
- Review only: <paths>

Inputs:
- Requirements/spec:
- Files changed:
- Diff summary (optional):

Rules:
- Read-only. Do not modify files.
- Cite file paths/lines for findings.
- State verification gaps explicitly.

Deliverable:
- Verdict: pass | fail | needs-info
- Findings by severity
- Concrete fixes (file paths)
- Verification gaps (commands to run)
```

## Final Report Template

```text
Task Board:
- T1 <title> | claim: <...> | status: <...>
- T2 <title> | claim: <...> | status: <...>

Task Reports:
- T1 Root cause: <...>
  Files changed: <...>
  Verification: <commands + results>
  Risks/follow-ups: <...>
- T2 ...

Integration:
- Conflicts: <none or details>
- Final verification: <commands + results>

dot-agent Maintenance:
- memory.md: <updated | not present>
- session-log.md: <updated | not present>
- docs/: <updated | unchanged | not present>

Automation:
- scripts added/updated: <none | paths>
- user confirmation: <yes/no>
```
