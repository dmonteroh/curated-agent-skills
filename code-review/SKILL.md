---
name: code-review
description: High-signal, fast code review with selectable modes (quality/tone, security/performance, tooling/automation). Includes a safe-by-default review script to summarize diffs, scan for risky patterns, and produce a deterministic report. Works standalone; if other skills are available, use them for domain/tech-specific checks.
category: workflow
---

# code-review

One canonical code review skill designed for speed, depth, and low noise.

It replaces overlapping code-review skills by providing explicit review modes:
- **quality**: correctness, clarity, maintainability, API ergonomics, review tone
- **security**: authz/authn, input validation, injection, secrets, supply chain
- **performance**: hot paths, I/O patterns, query behavior, allocations, scalability
- **tooling**: CI/CD checks, linters, static analysis, test signals, automation hooks

## Use this skill when

- Reviewing pull requests, diffs, or local changes.
- Establishing code review standards for a team.
- Auditing for correctness, security, performance, or maintainability before merge/release.

## Do not use this skill when

- There are no code changes to review.
- The request is to implement a feature (review can be a follow-up).

## Quick start (fast path)

1) Run the scan (optional but recommended):

```sh
./code-review/scripts/review.sh scan
./code-review/scripts/review.sh report
```

2) Review manually using the mode checklists:
- `references/checklists.md`

## Workflow (best performance, best results)

### 1) Establish review context

Output:
- change intent (what and why)
- constraints (deadlines, compatibility, risk tolerance)
- target environment (prod/internal, scale, threat model)

### 2) Triage scope

- Identify changed files and entrypoints.
- If the diff is huge, sample by risk: auth, money, data integrity, concurrency.

### 3) Run automated signals (best-effort)

- Run `scripts/review.sh scan` to collect:
  - changed files list
  - suspicious patterns (best-effort heuristics)
  - TODO/FIXME hotspots
- If project tooling exists, run it (tests/linters). If not available, note it.

### 4) Manual review by mode

Pick one or more modes and follow the corresponding checklist:
- `quality` (default)
- `security`
- `performance`
- `tooling`

### 5) Produce feedback in a deterministic format

Use `references/output-format.md`.

## Integration notes

- If review uncovers missing requirements/spec, create work items via `tracks-conductor-protocol`.
- If review requires an architectural decision, record it via `adr-madr-system`.
- If review is focused on refactoring tactics, use `refactor-clean` for execution guidance.

## Resources

- `references/checklists.md` (mode checklists)
- `references/output-format.md` (review output contract)
- `resources/implementation-playbook.md` (deeper patterns)
- `scripts/review.sh` (scan + report wrapper)
