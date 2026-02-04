# Implementer Subagent Prompt (Copy/Paste Template)

Use this to dispatch an implementer subagent. It is designed to work in **non-interactive** subagent environments.

```text
Task: <one sentence, explicit outcome>.

Context:
- Why: <why this exists>
- Where: <module/service>
- Constraints: <compat/security/perf>

Scope:
- Allowed: <paths>
- Avoid: <paths>

Inputs:
- Read these files first:
  - <paths>
- Evidence:
  - <failing tests / logs / repro steps>

Rules:
- If anything is ambiguous or conflicts: STOP and output QUESTIONS. Do not guess.
- Do not expand scope.
- Do not refactor unrelated code.
- Preserve existing APIs unless explicitly instructed.

Steps:
1) Inspect current state (read the listed files).
2) Implement the minimal change that satisfies the acceptance criteria.
3) Update/add tests if appropriate.
4) Run verification commands, or explain why you cannot.

Acceptance Criteria:
- [ ] <criterion>
- [ ] <criterion>

Verification:
- Command(s):
  - <e.g., dotnet test>
  - <e.g., npm test>

Output:
- Root cause.
- Files changed/moved.
- Verification commands + results.
- Any risks or follow-ups.
- If blocked: QUESTIONS (explicit) + what info is missing.
```
