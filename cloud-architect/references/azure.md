# Azure Reference

Use this as a quick checklist when the solution targets Azure.

## Common Building Blocks

- Subscriptions: separate at least `prod` and `non-prod`; use management groups + policy.
- Identity: Entra ID; managed identities for workloads; conditional access.
- Networking: VNets, subnets, NSGs; private endpoints for PaaS services.
- Ingress: Front Door/WAF + Application Gateway as appropriate.
- Compute:
  - Serverless: Azure Functions + Service Bus/Event Grid
  - Containers: AKS
  - VMs: VMSS
- Data: Azure SQL, PostgreSQL Flexible Server, Storage accounts.
- Observability: Azure Monitor + Log Analytics; central workspaces.

## Reliability Defaults

- Zone-redundant where supported.
- Geo-redundant backups if required.

## Cost Defaults

- Azure Cost Management budgets.
- Reservations for steady state; autoscale for variable.
- Control egress; watch Log Analytics ingestion costs.
