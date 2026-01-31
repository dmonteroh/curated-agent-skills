---
name: deps-audit
description: Audit dependencies fast for vulnerabilities, licenses, and supply-chain risk across common ecosystems (Node/Python/Go/Rust/etc). Produces a short risk summary plus an executable remediation plan (compatible with tracks-conductor-protocol). Includes scripts to detect manifests and generate a deterministic audit report under docs/_docgen. Use PROACTIVELY for security posture checks, dependency upgrades, or pre-release hardening.
---

# deps-audit

Perform a dependency audit with a bias toward **speed**, **actionability**, and **low noise**.

This skill replaces overlapping dependency-audit skills and standardizes:
- manifest detection
- scan execution (best-effort using locally available tools)
- report output location
- conversion to remediation work items

## Use this skill when

- You need a quick dependency security posture check.
- You are preparing a release and want to de-risk known vulnerabilities.
- You need license/supply-chain risk visibility.
- You want an upgrade/remediation plan that can be executed by multiple agents.

## Do not use this skill when

- The repo has no dependency manifests (or you cannot access them).
- You cannot change dependencies and only want a casual discussion.

## Fast path

Run the wrapper in the target repo:

```sh
./deps-audit/scripts/deps.sh scan
./deps-audit/scripts/deps.sh report
```

Outputs go to `docs/_docgen/deps-audit/` (safe-by-default).

## Workflow (best performance, best results)

1) Detect manifests (don’t guess)
- Identify ecosystems present (Node/Python/Go/etc).
- Prefer lockfiles as the source of truth.

2) Run best-effort scans using available tooling
- If a tool is missing, record the recommended command and keep going.
- Avoid “fix everything” upgrades; prioritize by severity + reachability + exposure.

3) Produce a short, decision-ready summary
- Top vulnerabilities by severity + reachable impact.
- License conflicts / policy risks (if tooling available).
- Recommended upgrade path with compatibility notes.

4) Convert to executable work
- If this is real work (not just a report), create a track/tasks via `tracks-conductor-protocol`.
- If fixes require architecture/security decisions (e.g., replacing a core library), record an ADR via `adr-madr-system`.

## Output format

- `docs/_docgen/deps-audit/REPORT.md` (human summary)
- `docs/_docgen/deps-audit/raw/` (tool outputs, best-effort)
- Optional: list of remediation tasks (upgrade PRs, pin fixes, policy changes)

## Resources

- `resources/implementation-playbook.md` for tooling references and deeper patterns.
- `scripts/deps.sh` wrapper (scan + report).
