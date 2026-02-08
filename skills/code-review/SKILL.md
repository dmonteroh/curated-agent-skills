---
name: code-review
description: "Provides high-signal, fast code review with selectable modes (quality, security, performance, tooling). Includes an optional safe-by-default review script to summarize diffs, scan for risky patterns, and produce a deterministic report."
category: workflow
---
# code-review

Provides a canonical code review workflow designed for speed, depth, and low noise.

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

## Required inputs

- Diff, PR link, or changed files list.
- Change intent and constraints (risk tolerance, compatibility needs).
- Runtime context (production vs internal, threat model, scale).

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
- If requirements are missing or ambiguous, ask clarifying questions before findings.

Output:
- changed files summary
- high-risk areas to prioritize
- open questions (if any)

### 3) Run automated signals (best-effort)

- Run `scripts/review.sh scan` to collect:
  - changed files list
  - suspicious patterns (best-effort heuristics)
  - TODO/FIXME hotspots
- If project tooling exists, run it (tests/linters). If not available, note it.
- If `git` is unavailable, document that the scan used a full-repo fallback.

Output:
- scan artifacts paths
- tooling results or missing-tool notes

### 4) Manual review by mode

Pick one or more modes and follow the corresponding checklist:
- `quality` (default)
- `security`
- `performance`
- `tooling`

Decision points:
- If changes touch auth, secrets, or input parsing, include `security`.
- If changes touch hot paths, queries, or batch jobs, include `performance`.
- If no tests exist for new behavior, record a test gap.

Output:
- mode-specific notes
- draft findings list with severity

### 5) Produce feedback in a deterministic format

Use `references/output-format.md`.

### 6) Finalize report

Output:
- ordered findings by severity
- open questions / assumptions
- suggested follow-ups
- short change summary

## Common mistakes to avoid

- Treating lint/style nits as blockers.
- Assuming intent instead of asking for clarification.
- Missing security boundaries at request or data layer edges.
- Skipping tests or observability impacts for behavior changes.

## Output contract

Provide the report sections and finding format in `references/output-format.md`.

## Script usage and verification (optional)

Commands:
- `./code-review/scripts/review.sh scan`
- `./code-review/scripts/review.sh report`

Requirements:
- `git` for diff context (falls back to full repo scan if missing).
- `rg` for faster pattern search (falls back to `find` + `grep`).

Verification:
- Confirm `docs/_docgen/code-review/REPORT.md` was created.
- Confirm the report lists changed files and pattern hits.

## Example output snippet

```
Findings:
- src/auth/session.ts:42 (HIGH): Session cookie lacks HttpOnly/SameSite.
  Risk: cookie theft / CSRF amplification.
  Fix: set HttpOnly=true, SameSite=Lax/Strict, Secure=true in prod; add a test.

Open questions:
- Is this endpoint reachable from public traffic?

Suggested follow-ups:
- Add a regression test for cookie attributes.

Change summary:
- Adds session refresh endpoint for mobile clients.
```

## Resources

- `references/README.md` (index of supporting references)
- `scripts/review.sh` (scan + report wrapper)
