# AI-Assisted Review Workflow (Condensed)

## Scope

- Security, performance, architecture, maintainability, tests.
- Prefer static analysis first, then AI for context-sensitive issues.

## Local Tooling (optional)

- Run local static analysis tools already available in the repo.
- Record when tooling is unavailable rather than assuming results.

## Workflow

1) Collect diff context and run optional scans.
2) Summarize the change intent and constraints.
3) Apply the mode checklists to identify risks and gaps.
4) Draft findings with severity and concrete fixes.
5) Deliver the final report in the output format.

## Output Expectations

- File + line references.
- Severity levels.
- Concrete fixes and tests.
