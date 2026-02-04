# DevSecOps Automation and Testing

## DevSecOps & Security Automation

- Security pipeline integration: gate SAST, DAST, dependency, and secrets checks in CI/CD.
- Shift-left security: capture security requirements early and review changes continuously.
- Security as Code: policy as code, baseline configurations, and automated enforcement.
- Container security: image scanning, runtime controls, Kubernetes policy enforcement.
- Supply chain security: provenance tracking, SBOM generation, dependency risk reviews.
- Secrets management: rotation policies and least-privilege access to secrets stores.

## Application Security Testing

- Static analysis (SAST) for code and IaC before merge.
- Dynamic analysis (DAST) for deployed environments with safe testing boundaries.
- Interactive testing (IAST) for runtime signal collection.
- Dependency and container scanning for transitive and image risks.
- Infrastructure scanning for misconfigurations and exposed services.
- See `references/security-scanning.md` for condensed tool examples and outputs.

## Security Testing & Validation

- Penetration testing and red team exercises for critical assets.
- Bug bounty or coordinated disclosure programs when appropriate.
- Security chaos engineering for resilience testing.
- Compliance testing to validate control effectiveness.
