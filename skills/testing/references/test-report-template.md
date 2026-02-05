# Test Report Template (Compact)

Use this for a deterministic, decision-friendly report (PR comment, release gate, incident follow-up).

```md
# Test Report: <feature/change>

Date: YYYY-MM-DD
Scope: <unit / integration / e2e / perf / security>

## Summary

- Total: <n>
- Passed: <n>
- Failed: <n>
- Skipped/Quarantined: <n>
- Coverage (if tracked): <line/branch targets + actual>

## What changed (1-3 bullets)

- ...

## Findings (by severity)

### [CRITICAL] <title>
- Location: <file:line or endpoint>
- Repro: <steps>
- Expected vs Actual: <...>
- Impact: <...>
- Recommendation: <...>

### [HIGH] <...>

## Coverage gaps / follow-ups

- ...

## Verification artifacts (if available)

- Logs/traces/screenshots: <paths/links>
- Test command(s): <...>

## Sign-off gate

- [ ] No critical issues open
- [ ] Required suites green (or explicit exception)
- [ ] Known flakes quarantined with a ticket/plan
```

## Severity guide

- CRITICAL: security vulnerability, data loss, system crash, privilege escalation.
- HIGH: major functionality broken, serious perf regression.
- MED: partial feature break with workaround.
- LOW: minor edge/cosmetic.
