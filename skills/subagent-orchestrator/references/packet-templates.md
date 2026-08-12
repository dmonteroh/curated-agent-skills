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

The two review types are independent axes and are not merged: code that is well built can implement the wrong thing (passes code-quality, fails spec-compliance), and code that meets the spec can be badly built. Run spec-compliance first; run code-quality after it passes, or when quality review is requested regardless.

```text
Review type: <spec-compliance | code-quality>

Scope:
- Review only: <paths>

Inputs:
- Requirements/spec:
- Files changed:
- Diff summary (optional):
- Optional: diff range <base sha>..<head sha>

Rules:
- Read-only. Do not modify files.
- Do not trust the implementer's report. Verify by reading the code and diffs.
- Cite file paths/lines for findings.
- State verification gaps explicitly.

Checks (code-quality):
- Correctness: edge cases, error handling, concurrency, idempotency.
- Maintainability: naming, structure, duplication, complexity.
- Safety: secrets and logging, unsafe defaults, dangerous operations.
- Tests: present, and actually validating behavior rather than restating it.
- Verification gap: were the right commands run, by anyone?

Checks (spec-compliance):
- Missing requirements, with file references.
- Extra or unrequested scope, with file references.
- Ambiguities in the spec, raised as questions for the controller.

Deliverable:
- Verdict: pass | fail | needs-info
- Findings ordered by severity: Critical | Important | Minor
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
