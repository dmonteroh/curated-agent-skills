# AI Review Workflow (Condensed)

## Scope

- Security, performance, architecture, maintainability, tests.
- Use static analysis first, then AI for context-sensitive issues.

## Suggested Toolchain

- CodeQL or Semgrep for security.
- SonarQube for code smells.
- Snyk for dependencies.

## Multi-Agent Review

- Dispatch domain reviewers (security, perf, architecture).
- Merge findings with severity ranking.
- Resolve conflicts before final report.

## Output Expectations

- File + line references.
- Severity levels.
- Concrete fixes and tests.
