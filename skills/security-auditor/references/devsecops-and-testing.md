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

## Security Testing & Validation

- Penetration testing and red team exercises for critical assets.
- Bug bounty or coordinated disclosure programs when appropriate.
- Security chaos engineering for resilience testing.
- Compliance testing to validate control effectiveness.

## Coordinated Disclosure and Bounty Submissions

The engagement mode for submitting to someone else's disclosure or bounty program, its confidence gate, and its three reportability filters are in `references/finding-triage.md`. This section covers what a submission contains once a candidate has cleared them.

### Classes that carry impact in this mode

Bias the search toward remotely reachable, user-controlled paths. These classes are the ones that consistently reach a meaningful sink:

| Class | CWE | Typical impact |
| --- | --- | --- |
| Server-side request forgery through a user-controlled URL | CWE-918 | Internal network access, cloud instance-metadata theft |
| Authentication bypass in middleware or an API guard | CWE-287 | Unauthorized account or data access |
| Remote deserialization, or an upload path that reaches execution | CWE-502 | Code execution |
| SQL injection in a reachable endpoint | CWE-89 | Data exfiltration, authentication bypass, data destruction |
| Command injection in a request handler | CWE-78 | Code execution |
| Path traversal in a file-serving path | CWE-22 | Arbitrary file read or write |
| Cross-site scripting that triggers without victim cooperation | CWE-79 | Session theft, administrator compromise |

The list is a search bias, not a scope definition: a class absent here is still reportable if the trace shows user control reaching a sink, and a class present here is not reportable if the program excludes it.

### Submission gate

Every item is a stop, and a submission that misses one is withdrawn rather than argued:

- The code path is reachable from a real network or cross-user boundary.
- The input is genuinely attacker-controlled, traced from entry point to sink.
- The sink is meaningful — it executes, reads, writes, or authenticates.
- The demonstration reproduces, in an environment the tester is authorized to touch.
- No advisory, CVE, published report, or open ticket already covers it.
- The target is in the program's published scope on the day of submission.

### Where the proof may be produced

A disclosure program expects a working demonstration, while an audit verifies by tracing code rather than by exercising live systems. Both hold, and the reconciliation is the environment, not the standard of proof: build and run the smallest proof of concept against a local or otherwise owned deployment of the same version, and quote the trace for the target. Run it against a third party's live system only where that program's rules explicitly authorize testing against it, and never beyond the minimum that establishes impact. *(Authored: neither the disclosure practice nor the audit's trace-only rule states how the two are reconciled.)*

### Report structure

```markdown
## Description
What the vulnerability is and why it matters

## Vulnerable code
File path, line range, and the smallest motivating snippet

## Proof of concept
The minimal request or script, and the environment it was run against

## Impact
What the attacker achieves, stated as a capability rather than a severity word

## Affected version
Version, commit, or deployment target tested
```
