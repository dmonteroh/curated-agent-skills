# Output Format

Default output order (optimize for actionability):

1) Findings (ordered by severity)
2) Open questions / assumptions
3) Suggested follow-ups (tests, monitoring, docs)
4) Change summary (only after findings)

## Severity scale

- **BLOCKER**: correctness/security issue that must be fixed before merge
- **HIGH**: likely bug, vuln, or major reliability issue
- **MEDIUM**: correctness edge case, maintainability risk, perf regression risk
- **LOW**: style/nit, minor clarity improvements

## Findings format

Each finding should include:
- file path + line reference (if available)
- severity
- problem statement (1-2 sentences)
- why it matters (risk / impact)
- concrete fix suggestion (short)

Example:

```
- src/auth/session.ts:42 (HIGH): Session cookie not set with SameSite/HttpOnly.
  Risk: cookie theft / CSRF amplification in browsers.
  Fix: set HttpOnly=true, SameSite=Lax/Strict, Secure=true in prod; add a test.
```

## Tone rules (fast + constructive)

- Prefer "I think" + evidence over absolutes.
- Ask questions when intent is unclear rather than guessing.
- Separate "must fix" from "nice to have".
