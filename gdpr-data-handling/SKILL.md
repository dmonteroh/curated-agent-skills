---
name: gdpr-data-handling
description: Implement practical GDPR-compliant data handling (privacy by design, lawful basis, DSARs, retention, vendor/transfer controls, breach readiness). Use when building or reviewing systems that process EU personal data.
category: security
---

# GDPR Data Handling

Practical implementation guide for GDPR-compliant data processing, privacy controls, and operational workflows.

This skill is intentionally **implementation-oriented** (engineers/operators). It does not replace legal counsel; it helps turn requirements into concrete artifacts and verifiable behaviors.

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

- The task is unrelated to gdpr data handling
- You need a different domain or tool outside this scope

## Outputs (what you should produce)

Minimum artifacts (paths are suggestions; use existing repo conventions):
- Data inventory: systems, datasets, fields, owners, purpose, lawful basis
- DSAR runbook: identity verification, timelines, export format, deletion rules
- Retention schedule: what is retained, for how long, and why; deletion mechanism
- Vendor/transfer notes: processors/subprocessors, DPAs, transfer mechanism notes
- Breach readiness runbook: detection, triage, notification workflow, evidence capture

Templates and checklists are in `resources/` (load as needed).

## Workflow (fast, high-signal)

1) Map the processing
- What personal data is processed, where it flows, who can access it, where it is stored.

2) Establish purpose + lawful basis
- Be explicit per processing purpose (don’t default to consent).

3) Implement privacy by design/default
- Data minimization, least privilege, access logging, encryption, redaction, safe defaults.

4) Build DSAR capability
- Access/export/rectify/erase/restrict/object flows with auditability and safeguards.

5) Retention and deletion
- Enforce retention in code/DB/jobs; document exceptions (legal holds).

6) Vendors and transfers (if applicable)
- Track processors, access scope, and transfer mechanism notes; avoid surprises.

7) Operationalize
- Add monitoring/alerts for DSAR/breach workflows and runbook gates.

## Instructions

- Clarify goals, constraints, and required inputs.
- Apply relevant best practices and validate outcomes.
- Provide actionable steps and verification.
- If detailed patterns/templates are required, open:
  - `resources/implementation-playbook.md`
  - `resources/templates.md`

## Resources

- `resources/implementation-playbook.md` for detailed patterns and examples.
- `resources/templates.md` for copy/paste templates (data inventory, DSAR runbook, retention, vendor/transfers, breach readiness).
