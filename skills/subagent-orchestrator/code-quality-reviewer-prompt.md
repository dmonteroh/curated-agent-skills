# Code Quality Reviewer Prompt (Copy/Paste Template)

Purpose: verify the implementation is well-built: correct, maintainable, tested, and safe.

Only run this after spec compliance passes (or if explicitly asked to review quality regardless).

```text
Review type: code-quality

Scope:
- Review only these paths: <paths>

Inputs:
- Summary of change intent:
  - <1-3 bullets>
- Optional: diff range:
  - <base sha>..<head sha>

Checks:
- Correctness: edge cases, error handling, concurrency, idempotency (if relevant)
- Maintainability: naming, structure, duplication, complexity
- Safety: secrets/logging, unsafe defaults, dangerous operations
- Tests: presence, quality, and whether they actually validate behavior
- Verification gap: did anyone run the right commands?

Output:
- Verdict: pass | fail | needs-info
- Findings ordered by severity (Critical/Important/Minor)
- Concrete fixes (file paths)
- What to verify (commands)
```
