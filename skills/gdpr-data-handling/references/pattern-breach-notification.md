# Pattern: Breach Notification

Use this reference to design incident workflows for personal data breaches.

## Triage Data Points

- What happened and when.
- Data categories affected (including special categories).
- Approximate number of data subjects.
- Ongoing risk of access or exfiltration.

## Notification Workflow

- Notify security and privacy owners immediately.
- Assess whether supervisory authority notification is required within 72 hours.
- If high risk to individuals, plan data subject notification with clear guidance.
- Make both of those assessments against the tier gate below rather than case by case, so the decision is checkable after the fact.

## Severity to Notification Tier (Chosen Default)

The regulation states a qualitative risk test, not a severity scale: the supervisory authority is notified unless the breach is unlikely to result in a risk to the rights and freedoms of individuals (Art. 33), and individuals are told separately when the breach is likely to result in a *high* risk to them (Art. 34). Every breach is recorded either way (Art. 33(5)).

**The bands and thresholds below are a chosen operational default for making that qualitative test checkable during an incident. GDPR defines no severity tiers and mandates none of these thresholds.** Agree the mapping with counsel, write it into the runbook before an incident, and record it as a house rule rather than a legal requirement. Only the 72-hour authority deadline in the workflow above is legally fixed.

Decide the two notifications separately — one gate does not imply the other:

| Condition | Authority (Art. 33) | Individuals (Art. 34) |
| --- | --- | --- |
| Special-category or credential-grade data involved (health, biometric, financial, authentication credentials) | Notify, regardless of assessed severity | Assess on severity, as below |
| Assessed severity medium or above | Notify | Not on this ground alone |
| Assessed severity high or above | Notify | Notify |
| Below both bars | Do not notify — record the decision and the reasoning | Do not notify |

Individual notification is deliberately the higher bar: it reaches people who cannot act on most of what they are told, and a low-value notification spends the attention needed for the one that matters.

Assigning the band is judgment, applied to the triage data points above plus how reversible the exposure is and how identifiable the subjects are. **Write the band definitions down before an incident, not during one** — a band chosen while an incident is live is chosen for the incident in hand, which is how the threshold moves.

Falsifiable check on the gate: the breach record names which row above was applied and why. A record whose notification decision cannot be traced to a row has not used the gate, and the decision *not* to notify is the one most likely to be questioned later.

## Evidence and Documentation

- Preserve relevant logs, alerts, and forensics snapshots.
- Record decisions, timelines, and mitigation steps.

## Minimum Breach Record Fields

| Field | Example |
| --- | --- |
| Incident ID | `BREACH-2024-004` |
| Detected at | ISO timestamp |
| Summary | `Unauthorized access to support tool` |
| Data categories | `contact info`, `account IDs` |
| Estimated subjects | Numeric estimate |
| Notification decision | `notify authority` / `no notification` |
| Decision basis | Which tier row applied: `special-category data`, `severity: high`, `below both bars` |
| Mitigations | `revoked tokens`, `patched system` |
