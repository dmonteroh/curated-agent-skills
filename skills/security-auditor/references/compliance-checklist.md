# Compliance Checklist (Condensed)

- Identify applicable frameworks (GDPR, HIPAA, SOC2, PCI).
- Map data types to controls (PII, PHI, payment data).
- Ensure audit logging and retention.
- Verify access controls and least privilege.
- Document incident response procedures.

## Payment card data (PCI DSS)

Payment-card obligations do not travel with personal-data obligations: a system can be fully lawful under a privacy regime and still fail here, because the rules below are about the card number and the authentication data behind it, not about the person. Assess them separately.

PCI DSS is organized as 12 requirements. The two carrying the concrete, checkable rules about the data itself are **Requirement 3** (protect stored account data) and **Requirement 4** (protect cardholder data with strong cryptography in transit over open, public networks). Sub-requirement numbers below are the standard's own, given as v4.0 with the v3.2.1 equivalent in parentheses — confirm which version the assessment runs under before quoting a number, because the numbering moved between them.

### Never retained, in any form

Sensitive authentication data must not be stored after authorization completes, **even encrypted** (v4.0 §3.3.1; v3.2.1 §3.2):

- Full magnetic-stripe or equivalent chip track data.
- The card verification code or value — the three- or four-digit code printed on the card (CVV2/CVC2/CID).
- The PIN or PIN block.

Retainable when protected: the primary account number (PAN), cardholder name, expiration date, and service code. The PAN must be rendered unreadable **anywhere it is stored**, logs, backups, and portable media included (v4.0 §3.5.1; v3.2.1 §3.4).

Audit move: search logs, crash reports, request traces, analytics payloads, support tooling, and fixture data for card-shaped values and for the prohibited field names in every spelling the codebase uses. Incidental capture in an error path is the common way prohibited data comes to be stored, and it does not appear in the data model.

### Masking on display

The maximum that may be displayed is the issuer identification digits plus the last four. v3.2.1 §3.3 states this as the first six and last four; v4.0 §3.4.1 states it as the BIN and last four, which is not identical, since the BIN is not universally six digits. Anything wider than that cap requires a documented, role-scoped business need — so a full-PAN view in a support console is a finding unless the need and the role restriction are both written down.

### Scope reduction is the strongest control available

The cheapest way to satisfy Requirement 3 is for the PAN never to arrive: a hosted payment page, or a client-side tokenization script that posts the card details straight to the processor and returns a token, leaves the server holding only the token and a customer reference. Systems that never see the PAN fall outside the cardholder-data environment, and the assessment burden drops with them.

That burden is expressed as which self-assessment questionnaire applies:

| SAQ | Applies to |
| --- | --- |
| A | All card handling outsourced to a validated third party — a hosted page or a full redirect |
| A-EP | An e-commerce site that never receives the PAN but serves pages that can affect the payment transaction |
| D | Anything that stores, processes, or transmits card data |

*(Authored: the SAQ eligibility text moves between standard versions — read the eligibility criteria for the version being assessed rather than reciting them.)*

*(Authored: a self-hosted token vault does not reduce scope. An encrypted PAN is still a stored PAN, so Requirement 3's protection, key-management, and access obligations all still apply, and the system stays in the cardholder-data environment. Scope shrinks only where the card data is never present.)*
