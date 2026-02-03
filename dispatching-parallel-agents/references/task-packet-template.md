# Task Packet Template (Subagent)

Use this template to provide a subagent enough context to work non-interactively.

```text
Task: <one sentence, explicit outcome>.

Context:
- Why: <why this change exists>
- Where it fits: <module/service>
- Constraints: <compat/security/perf/etc>

Scope:
- Allowed: <paths>
- Avoid: <paths>

Inputs:
- Pointers:
  - <file paths to read>
- Evidence:
  - <failing test names / stack traces / logs>

Rules:
- If ambiguous or conflicting: STOP and output QUESTIONS.
- Do not expand scope.
- Do not refactor unrelated code.

Steps:
1) Inspect current state (read the listed files).
2) Implement minimal changes to satisfy the acceptance criteria.
3) Update/add tests if appropriate.
4) Run verification (or explain why you cannot).

Acceptance Criteria:
- [ ] <criterion>
- [ ] <criterion>

Output:
- Root cause.
- Files changed/moved.
- Verification commands + results.
- Any follow-ups or risks.
```
