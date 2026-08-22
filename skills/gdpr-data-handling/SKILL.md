---
name: gdpr-data-handling
description: "Implements practical GDPR-compliant data handling (privacy by design, lawful basis, DSARs, retention, vendor/transfer controls, breach readiness). Use when building or reviewing systems that process EU personal data."
metadata:
  category: security
---
# GDPR Data Handling

Produces concrete artifacts and verifiable behaviors from privacy requirements.

## Use this skill when

- Building systems that process EU personal data
- Establishing lawful basis + purpose limitation and mapping data flows
- Implementing consent/opt-in (when consent is the lawful basis)
- Handling data subject requests (DSARs)
- Setting retention/deletion and “right to be forgotten” behavior
- Managing processors/subprocessors and international transfers (high level)
- Conducting GDPR compliance reviews
- Designing privacy by design/default controls

## Do not use this skill when

- The task is unrelated to GDPR data handling
- Legal interpretation or formal legal advice is required
- A different domain or tool outside this scope is needed

## Required inputs

- Systems and datasets in scope (or a repo/architecture available for inspection)
- Processing purposes and audiences
- Current storage locations, access paths, and vendors
- Existing retention/deletion behaviors and policies
- Known DSAR/breach procedures (if any)

## Constraints

- Provides engineering/operational guidance, not legal advice.
- Avoids time-sensitive or jurisdiction-specific interpretations beyond GDPR basics.
- Requires local system context; do not assume external network access or third-party data.

## Outputs produced

Minimum artifacts (paths are suggestions; use existing repo conventions):
- Data inventory: systems, datasets, fields, owners, purpose, lawful basis
- DSAR runbook: identity verification, timelines, export format, deletion rules
- Retention schedule: what is retained, for how long, and why; deletion mechanism
- Vendor/transfer notes: processors/subprocessors, DPAs, transfer mechanism notes
- Breach readiness runbook: detection, triage, notification workflow, evidence capture

Templates and checklists are in `references/README.md` (load as needed).

## Workflow

1) Scope the processing
- Output: scope summary, data types, environments, and assumptions.

2) Build a data inventory + flow map
- Output: data inventory table with systems, fields, owners, purposes, lawful basis.

3) Choose lawful basis per purpose
- Decision: if consent is required, include consent collection + withdrawal plan.
- Output: lawful basis mapping and justification per purpose.

4) Design privacy by default controls
- Decision: if sensitive/special categories, add stricter access + logging.
- Output: control list (minimization, access, encryption, logging, redaction).

5) Define DSAR workflows
- Decision: if the task is DSAR-specific, prioritize runbook + tooling first.
- Output: DSAR runbook (verification, timelines, export format, deletion rules).

6) Set retention + deletion
- Decision: if legal holds apply, document exceptions and approval gate.
- Decision: if a downstream use survives losing the identifiers, irreversible anonymization is an alternative end-of-retention outcome to deletion — but only where no re-identification key is retained anywhere; otherwise the record stays personal data and the retention rule still applies. See `references/pattern-retention.md`.
- Output: retention schedule + deletion mechanism notes.

7) Capture processor/transfer requirements
- Decision: if vendors or cross-border transfers exist, include transfer mechanism notes.
- Output: processor/subprocessor register and transfer notes.

8) Prepare breach readiness
- Decision: fix the notification gate in the runbook before any incident — which severity band triggers supervisory-authority notification, which triggers data-subject notification, and which data categories escalate regardless of band. GDPR states a qualitative risk test rather than tiers, so any tiering is a chosen house rule to agree with counsel, not a legal requirement. Tier table and the record field that traces each decision to it: `references/pattern-breach-notification.md`.
- Output: breach readiness runbook with triage, the notification gate with its bands defined, evidence capture.

9) Validate gaps
- Output: compliance checklist with open gaps + owners.

## Common pitfalls

- Treating consent as the default lawful basis without justification.
- Relying on policy-only retention with no technical enforcement.
- Incomplete DSAR coverage (missing backups, archives, or linked systems).
- Missing audit trails for consent changes or DSAR actions.
- Ignoring processor/subprocessor access paths and transfer documentation.
- Treating authority notification and data-subject notification as one decision, when the second is a deliberately higher bar.

## Examples

**Example 1: System design review**
- Input: "Review our EU customer onboarding flow for GDPR compliance and produce required artifacts."
- Output: data inventory, lawful basis mapping, DSAR runbook, retention schedule, breach runbook.

**Example 2: DSAR readiness**
- Input: "Implement DSAR handling for our SaaS product, including export and deletion workflows."
- Output: DSAR runbook, data source list, deletion exceptions, verification checklist.

## Output contract

Report the following sections:
- Summary of scope and assumptions
- Artifacts produced (with paths)
- Gaps/risks and recommended next actions
- Decisions made (lawful basis, retention exceptions, transfers)

## References

- Start with `references/README.md` for the index.
- `references/templates.md` provides copy/paste templates (data inventory, DSAR runbook, retention, vendor/transfers, breach readiness).
