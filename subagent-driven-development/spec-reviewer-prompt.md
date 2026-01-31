# Spec Compliance Reviewer Prompt (Copy/Paste Template)

Purpose: verify the implementation matches requirements **line-by-line** (nothing missing, nothing extra).

```text
Review type: spec-compliance

Requirements:
<copy/paste or point to the exact spec text>

Scope:
- Review only these paths: <paths>

Inputs:
- Files changed (if known):
  - <paths>
- Optional: commit(s) or diff range:
  - <base sha>..<head sha>

Rules:
- Do not trust the implementer report.
- Verify by reading code and/or diffs.
- Call out missing requirements and extra scope explicitly.

Output:
- Verdict: pass | fail | needs-info
- Missing requirements (with file references)
- Extra/unrequested changes (with file references)
- Ambiguities in spec (if any) and questions for the controller
```
