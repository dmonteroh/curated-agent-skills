# Review Packet Template (Subagent)

Use this when dispatching a reviewer subagent (spec compliance or code quality).

```text
Review type: <spec-compliance|code-quality>

Scope:
- Review only these paths: <paths>

Inputs:
- Requirements/spec:
  - <spec file path(s) or pasted requirements>
- Code changes:
  - <git diff summary or file list>
  - <commit SHA(s)> (optional)

Rules:
- Be strict and explicit.
- If you cannot verify, say so.

Output:
- Verdict: pass | fail | needs-info
- Findings (ordered by severity)
- Concrete fixes (file paths)
- Verification gap (if any)
```
