# DevOps Engineer - Implementation Playbook

Use this when you need a deterministic sequence for operational changes.

## Inputs

- Service/workload name + environment.
- Runtime: Docker, Kubernetes, VM, managed service.
- SLOs and failure modes.
- Current deploy/rollback mechanism.

## Change Types

Pick the smallest relevant play:

- Containerization changes (Dockerfile/image/runtime)
- K8s changes (resources, probes, ingress, config/secret wiring)
- Platform/self-service (templates, golden paths, devcontainer/dev env)
- Incident response readiness (runbooks, paging, dashboards)

## Safety Gates

- Always have a rollback.
- Verify probes/health checks are meaningful.
- Verify resource limits are sane.
- Verify secrets are not logged and are sourced securely.

## Verification Checklist

- Startup and readiness are stable.
- Error rate/latency does not regress.
- CPU/memory/IO saturation is not worse.
- Logs include correlation IDs if applicable.
- Runbook steps exist for: deploy, rollback, known failure modes.
