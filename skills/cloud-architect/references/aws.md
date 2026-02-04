# AWS Reference

Use this as a quick checklist when the solution targets AWS.

## Common Building Blocks

- Accounts: separate at least `prod` and `non-prod`; consider org units and SCPs.
- IAM: SSO + MFA; least privilege; use roles; avoid long-lived keys.
- Networking: VPC per environment; private subnets for workloads; VPC endpoints where possible.
- Ingress: CloudFront/WAF/ALB/API Gateway depending on workload.
- Compute:
  - Serverless: Lambda + EventBridge/SQS/SNS
  - Containers: ECS/Fargate or EKS
  - VMs: EC2 + ASG
- Data: RDS/Aurora, DynamoDB, S3.
- Observability: CloudWatch metrics/logs, X-Ray/OpenTelemetry; centralize logs.

## Reliability Defaults

- Multi-AZ for stateful services.
- Backups + restore drills.
- Alarms on symptom metrics (latency/error rate) + DLQ depth for async.

## Cost Defaults

- Mandatory tags for cost allocation.
- Budgets + anomaly detection.
- Prefer Graviton where compatible; use Savings Plans/RIs for steady workloads.
