# GCP Reference

Use this as a quick checklist when the solution targets Google Cloud.

## Common Building Blocks

- Projects: separate at least `prod` and `non-prod`; use folders/org policies.
- Identity: IAM; workload identity federation; service accounts with least privilege.
- Networking: VPCs, subnets, firewall rules; Private Service Connect for managed services.
- Ingress: Cloud Load Balancing + Cloud Armor.
- Compute:
  - Serverless: Cloud Run / Cloud Functions + Pub/Sub
  - Containers: GKE
  - VMs: Compute Engine + MIG
- Data: Cloud SQL, Spanner (when required), GCS.
- Observability: Cloud Monitoring/Logging; export to a central project as needed.

## Reliability Defaults

- Regional services for HA.
- Backups + PITR for stateful components.

## Cost Defaults

- Budgets + alerts.
- Committed use discounts for steady compute.
- Watch network egress and log ingestion.
