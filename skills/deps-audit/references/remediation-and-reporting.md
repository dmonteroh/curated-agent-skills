# Remediation and reporting

Use this reference to prioritize findings and produce a consistent report.

## Prioritization rubric

- Severity: critical/high/medium/low.
- Exposure: reachable vs unreachable, runtime vs dev-only.
- Fixability: patch/minor vs major upgrade or replacement.

## Remediation planning

- Prefer minimal compatible upgrades first.
- Propose alternative packages when fixes are unavailable.
- Flag changes that require architectural review.

## Report template

- Detected ecosystems + evidence files.
- Tools executed and missing tools (suggested commands).
- Top vulnerabilities with severity, package, version, and fix.
- License or SBOM findings (if available).
- Ordered remediation actions with effort notes.
- Limitations and gaps.

## Pitfalls to avoid

- Mixing findings from different ecosystems without labeling.
- Listing fixes without confirming the current version in lockfiles.
