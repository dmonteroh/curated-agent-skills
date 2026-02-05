---
name: security-auditor
description: Provides a structured security audit workflow for DevSecOps,
  application security, and compliance readiness, used for scoped assessments,
  threat modeling, testing, and remediation planning.
category: security
---
Provides a structured security audit workflow for scoped assessments, threat
modeling, testing, and remediation planning across DevSecOps, application
security, and compliance readiness.

## Use this skill when

- Running security audits or risk assessments
- Reviewing SDLC security controls, CI/CD, or compliance readiness
- Investigating vulnerabilities or designing mitigation plans
- Validating authentication, authorization, and data protection controls

## Do not use this skill when

- You lack authorization or scope approval for security testing
- You need legal counsel or formal compliance certification
- You only need a quick automated scan without manual review

## Trigger phrases

- "security audit" or "risk assessment"
- "threat model" or "attack surface review"
- "DevSecOps controls" or "CI/CD security"
- "compliance readiness" or "security controls review"
- "vulnerability mitigation plan" or "security findings report"

## Required inputs

- In-scope assets, environments, and owners
- Security objectives (confidentiality, integrity, availability priorities)
- Compliance targets (if any) and deadlines
- Constraints (production testing limits, tooling restrictions)

## Instructions

1. Confirm scope, assets, and compliance requirements.
   - Output: scope summary, in/out-of-scope list, compliance targets.
   - Decision: if scope or authorization is missing, stop and request clarification.
2. Review architecture, threat model, and existing controls.
   - Output: threat model summary, control gaps, high-risk surfaces.
   - Decision: if critical assets lack documentation, request missing inputs.
3. Run targeted scans and manual verification for high-risk areas.
   - Output: evidence list, tool results, manual validation notes.
   - Decision: if production testing is disallowed, use staging or review-only methods.
4. Prioritize findings by severity and business impact with remediation steps.
   - Output: ranked findings list with impact, likelihood, and remediation owners.
   - Decision: if a finding lacks reproducibility, mark it as unverified and flag it.
5. Validate fixes and document residual risk.
   - Output: verification status, residual risk summary, next steps.

## Safety

- Do not run intrusive tests in production without written approval.
- Protect sensitive data and avoid exposing secrets in reports.

## Common pitfalls

- Skipping authorization checks or exceeding agreed scope
- Reporting findings without clear evidence or reproduction steps
- Treating compliance requirements as a substitute for threat modeling
- Missing business context when prioritizing remediation

## Output contract

When this skill runs, respond with a report that includes:

- Scope and constraints
- Threat model summary and attack surface highlights
- Findings table (id, severity, evidence, impact, remediation)
- Prioritized remediation plan with owners and timelines
- Verification status and residual risk

## Reporting format

Use this structure in final responses:

1. Summary
2. Scope & Constraints
3. Threat Model Highlights
4. Findings (table)
5. Remediation Plan
6. Verification & Residual Risk
7. Open Questions

## References
See `references/README.md` for detailed capabilities, behavioral traits, and knowledge areas.

## Examples
- "Conduct comprehensive security audit of microservices architecture with DevSecOps integration"
- "Implement zero-trust authentication system with multi-factor authentication and risk-based access"
- "Design security pipeline with SAST, DAST, and container scanning for CI/CD workflow"
- "Create GDPR-compliant data processing system with privacy by design principles"
- "Perform threat modeling for cloud-native application with Kubernetes deployment"
- "Implement secure API gateway with OAuth 2.0, rate limiting, and threat protection"
- "Design incident response plan with forensics capabilities and breach notification procedures"
- "Create security automation with Policy as Code and continuous compliance monitoring"

## Example Output

1. Summary: Identified 3 high-risk findings impacting API authentication.
2. Scope & Constraints: Production tests excluded; staging-only validation.
3. Threat Model Highlights: Token theft, privilege escalation, data exfiltration.
4. Findings (table):
   - SA-01 | High | Missing token rotation | Account takeover | Implement rotation
   - SA-02 | Medium | Excessive scopes | Data exposure | Scope minimization
5. Remediation Plan: Address SA-01 short-term, SA-02 medium-term.
6. Verification & Residual Risk: SA-01 pending validation; SA-02 not started.
7. Open Questions: Confirm token TTL requirements.

## Trigger test

- "Can you produce a security audit report for our API platform?"
- "We need a threat model and mitigation plan for our CI/CD pipeline."
