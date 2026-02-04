# Multi-Cloud Reference

Use this when you intentionally run across multiple cloud providers.

## When Multi-Cloud Is Worth It

- Regulatory/data residency demands multiple sovereign regions/providers.
- M&A / org structure forces multiple providers.
- Extremely high availability requirements with true provider independence.

## Common Pitfalls

- Hidden complexity in identity, networking, observability, and incident response.
- Divergent managed services make portability expensive.
- Higher staffing requirements and slower iteration.

## Practical Strategies

- Prefer *one* primary provider; treat others as edge/specialty unless mandated.
- Standardize cross-cloud contracts:
  - Identity: SSO + short-lived workload identity.
  - Network: consistent CIDR plan; VPN/Interconnect; DNS strategy.
  - Observability: one metrics/logs backend or standardized exporters.
  - Secrets: centralized management or replicated, with clear rotation.
- Keep the app portable via containers and minimal provider-specific SDK usage.

## DR Across Providers

- Treat cross-provider DR as an explicit program: replicate data, test restores, validate RTO.
- Ensure runbooks and paging paths work even when an entire provider is degraded.
