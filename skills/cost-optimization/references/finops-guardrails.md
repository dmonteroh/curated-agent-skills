# FinOps Guardrails (Cloud)

Use this as a compact set of guardrails and common high-ROI actions.

## Guardrails

- Define budget owners and escalation paths.
- Require cost allocation tags/labels from day 1.
- Make cost changes reversible (feature flags / staged rollout / rollback plan).

## High-ROI Actions

- Turn off idle/non-prod resources (scheduled shutdowns).
- Right-size always-on compute.
- Commit where stable (RIs / Savings Plans / CUDs) only after utilization evidence.
- Reduce data transfer (cache, colocate services, avoid cross-AZ/region chatter).
- Storage lifecycle policies (tiering + retention).

## Cost Review Cadence

- Weekly: anomaly review and top deltas.
- Monthly: rightsizing + reservation coverage review.
- Quarterly: architecture cost review (data flows, storage, egress, observability ingestion).
