# GDPR Core Concepts

These references summarize core GDPR concepts and foundational controls. Use them to guide design and documentation, not as legal advice.

## Personal Data Categories

| Category | Examples | Protection Level |
|----------|----------|------------------|
| **Basic** | Name, email, phone | Standard |
| **Special Categories (Art. 9)** | Health, biometrics, religion, ethnicity | Requires an Art. 9 condition (explicit consent is only one option) |
| **Criminal (Art. 10)** | Convictions, offenses | Official authority |
| **Children's** | Under 16 by default | Member states can set 13–16; verify for your target countries |

## Legal Bases for Processing (Article 6)

```
├── Consent: Freely given, specific, informed
├── Contract: Necessary for contract performance
├── Legal Obligation: Required by law
├── Vital Interests: Protecting someone's life
├── Public Interest: Official functions
└── Legitimate Interest: Balanced against rights

Notes:
- Choose consent only when it is truly “freely given” (no power imbalance / no bundling).
- Purpose limitation matters: document why the data is processed and don’t silently expand scope.
```

## Data Subject Rights (Common Timelines)

```
Right to Access (Art. 15)      ─┐
Right to Rectification (Art. 16) │
Right to Erasure (Art. 17)       │ Must respond
Right to Restrict (Art. 18)      │ within 1 month
Right to Portability (Art. 20)   │
Right to Object (Art. 21)       ─┘

Response timelines:
- Standard: 1 month
- Extension: up to 2 additional months for complex requests (with notice)
```

## Operational Building Blocks (Privacy by Design/Default)

- Data minimization: collect only what is needed, keep only as long as needed.
- Access control: least privilege; audit access to personal data.
- Security: encryption in transit/at rest where appropriate; secure secret handling.
- Logging: avoid leaking PII/secrets; use structured logs with redaction.
- Retention & deletion: implement retention as code/jobs, not as “policy only”.

## International Transfers (High-Level)

If personal data moves outside the EEA/UK:
- Track where processing occurs and what vendors are involved.
- Document the transfer mechanism (e.g., adequacy decision vs contractual clauses) and any supplementary measures.

This reference is not a substitute for legal review; it helps engineers implement the chosen mechanism.
